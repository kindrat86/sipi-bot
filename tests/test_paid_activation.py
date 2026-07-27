import json
import os
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock

from spendfirewall import api, billing, store, templates


class PaidActivationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.billing_db = os.path.join(self.tmp.name, "billing.db")
        self.firewall_db = os.path.join(self.tmp.name, "firewall.db")
        self.billing_db_patch = mock.patch.object(billing, "_DB", self.billing_db)
        self.store_db_patch = mock.patch.object(store, "_DB_PATH", self.firewall_db)
        self.capture_patch = mock.patch.object(billing, "_capture")
        self.billing_db_patch.start()
        self.store_db_patch.start()
        self.capture = self.capture_patch.start()
        store.init_db()

    def tearDown(self):
        self.capture_patch.stop()
        self.store_db_patch.stop()
        self.billing_db_patch.stop()
        self.tmp.cleanup()

    def _issue_paid_key(self):
        key, created = billing._issue_key(
            "team",
            "buyer@example.com",
            "cus_private",
            "sub_private",
            "cs_private",
            "anon-browser-1",
        )
        self.assertTrue(created)
        return key

    def test_paid_key_resolves_and_first_use_is_captured_once(self):
        key = self._issue_paid_key()

        agent_id, context = api._resolve_api_key(key)
        self.assertTrue(agent_id.startswith("billing_"))
        self.assertEqual(context["source"], "billing")

        self.assertTrue(billing.record_key_use(key, "BLOCKED"))
        self.assertFalse(billing.record_key_use(key, "APPROVED"))

        with sqlite3.connect(self.billing_db) as conn:
            usage_count, activated_at = conn.execute(
                "SELECT usage_count, activated_at FROM api_keys WHERE key=?",
                (key,),
            ).fetchone()
        self.assertEqual(usage_count, 2)
        self.assertTrue(activated_at)
        activation_calls = [
            call for call in self.capture.call_args_list
            if call.args and call.args[0] == "activation_completed"
        ]
        self.assertEqual(len(activation_calls), 1)
        props = activation_calls[0].args[2]
        self.assertEqual(props["plan"], "team")
        self.assertNotIn("api_key", props)
        self.assertNotIn("email", props)

    def test_paid_key_works_over_http_and_invalid_bearer_is_401(self):
        key = self._issue_paid_key()
        server = api.ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_address[1]}/v1/transactions/evaluate"
        try:
            body = json.dumps(
                {"amount": 5, "merchant": "openai.com", "category": "api"}
            ).encode()
            valid = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(valid, timeout=5) as response:
                result = json.load(response)
            self.assertIn(result["decision"], {"APPROVED", "BLOCKED", "FLAGGED"})

            invalid = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Authorization": "Bearer sk_live_invalid",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(invalid, timeout=5)
            self.assertEqual(error.exception.code, 401)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_checkout_webhook_is_idempotent_and_analytics_are_sanitized(self):
        event = {
            "id": "evt_repeat",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_sensitive",
                    "client_reference_id": "anon-browser-2",
                    "metadata": {"plan": "team"},
                    "customer": "cus_sensitive",
                    "subscription": "sub_sensitive",
                    "customer_details": {"email": "buyer@example.com"},
                    "amount_total": 9900,
                    "currency": "usd",
                }
            },
        }
        raw = json.dumps(event).encode()
        with mock.patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}), \
                mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            first = billing.handle_webhook(raw, "test-signature")
            second = billing.handle_webhook(raw, "test-signature")

        self.assertTrue(first["issued"])
        self.assertTrue(second["duplicate"])
        with sqlite3.connect(self.billing_db) as conn:
            count = conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0]
        self.assertEqual(count, 1)

        event_names = [call.args[0] for call in self.capture.call_args_list]
        self.assertEqual(event_names.count("checkout_completed"), 1)
        self.assertEqual(event_names.count("api_key_issued"), 1)
        for call in self.capture.call_args_list:
            properties = call.args[2]
            self.assertNotIn("stripe_customer_id", properties)
            self.assertNotIn("stripe_checkout_session", properties)
            self.assertNotIn("email", properties)

    def test_key_delivery_page_contains_no_third_party_analytics(self):
        html = templates.key_success_html(
            {
                "key": "sk_live_private",
                "tier": "team",
                "analytics_id": "anon-browser-3",
            }
        )
        self.assertNotIn("posthog", html.lower())
        self.assertNotIn("googletagmanager", html.lower())
        self.assertNotIn("google-analytics", html.lower())
        self.assertIn("history.replaceState", html)
        self.assertIn("sk_live_private", html)

    def test_unverifiable_webhook_quarantine_never_stores_raw_customer_data(self):
        quarantine = os.path.join(self.tmp.name, "webhook-quarantine.log")
        raw = b'{"customer_email":"private-buyer@example.com"}'
        with mock.patch.object(billing, "_QUARANTINE_FILE", quarantine), \
                mock.patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": ""}):
            result = billing.handle_webhook(raw, "t=1,v1=secret-signature")
        self.assertTrue(result["quarantined"])
        with open(quarantine, encoding="utf-8") as handle:
            entry = json.loads(handle.readline())
        self.assertNotIn("body", entry)
        self.assertNotIn("sig_header", entry)
        self.assertNotIn("private-buyer@example.com", json.dumps(entry))
        self.assertEqual(entry["body_bytes"], len(raw))


if __name__ == "__main__":
    unittest.main()
