import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock

from spendfirewall import api, billing, store, templates


class DashboardSecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.billing_db_patch = mock.patch.object(
            billing, "_DB", os.path.join(self.tmp.name, "billing.db")
        )
        self.store_db_patch = mock.patch.object(
            store, "_DB_PATH", os.path.join(self.tmp.name, "firewall.db")
        )
        self.capture_patch = mock.patch.object(billing, "_capture")
        self.billing_db_patch.start()
        self.store_db_patch.start()
        self.capture_patch.start()
        store.init_db()
        self.key_one, _ = billing._issue_key(
            "team", "one@example.com", "cus_1", "sub_1", "cs_1", "browser-1"
        )
        self.key_two, _ = billing._issue_key(
            "team", "two@example.com", "cus_2", "sub_2", "cs_2", "browser-2"
        )
        self.server = api.ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
        self.thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.capture_patch.stop()
        self.store_db_patch.stop()
        self.billing_db_patch.stop()
        self.tmp.cleanup()

    def request(self, path, key=None, method="GET", body=None):
        headers = {}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        request = urllib.request.Request(
            self.base + path, headers=headers, data=data, method=method
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.load(response)

    def test_private_dashboard_routes_require_a_key(self):
        for path in (
            "/api/stats",
            "/api/transactions",
            "/api/approvals",
            "/api/rules",
        ):
            with self.subTest(path=path), self.assertRaises(
                urllib.error.HTTPError
            ) as error:
                self.request(path)
            self.assertEqual(error.exception.code, 401)

    def test_paid_workspaces_have_isolated_rules_and_transactions(self):
        _, created = self.request(
            "/api/rules",
            self.key_one,
            "POST",
            {
                "rule_type": "merchant_block",
                "params": {"patterns": ["private-one.example"]},
                "action": "BLOCKED",
                "label": "workspace one only",
            },
        )
        _, rules_one = self.request("/api/rules", self.key_one)
        _, rules_two = self.request("/api/rules", self.key_two)
        self.assertIn(created["id"], {rule["id"] for rule in rules_one})
        self.assertNotIn(created["id"], {rule["id"] for rule in rules_two})
        self.assertTrue(all(rule["agent_id"] for rule in rules_one))
        self.assertTrue(all(rule["agent_id"] for rule in rules_two))

        self.request(
            "/v1/transactions/evaluate",
            self.key_one,
            "POST",
            {"amount": 7, "merchant": "private-one.example", "category": "api"},
        )
        _, tx_one = self.request("/api/transactions", self.key_one)
        _, tx_two = self.request("/api/transactions", self.key_two)
        self.assertEqual(len(tx_one), 1)
        self.assertEqual(tx_one[0]["merchant"], "private-one.example")
        self.assertEqual(tx_two, [])

        _, deletion = self.request(
            f"/api/rules/{created['id']}", self.key_two, "DELETE"
        )
        self.assertFalse(deletion["deleted"])
        _, deletion = self.request(
            f"/api/rules/{created['id']}", self.key_one, "DELETE"
        )
        self.assertTrue(deletion["deleted"])

    def test_cross_workspace_approval_cannot_be_resolved(self):
        self.request(
            "/v1/transactions/evaluate",
            self.key_one,
            "POST",
            {"amount": 250, "merchant": "review.example", "category": "api"},
        )
        _, approvals = self.request("/api/approvals", self.key_one)
        self.assertEqual(len(approvals), 1)

        _, denied = self.request(
            f"/api/approvals/{approvals[0]['id']}",
            self.key_two,
            "POST",
            {"decision": "approve"},
        )
        self.assertFalse(denied["resolved"])
        _, allowed = self.request(
            f"/api/approvals/{approvals[0]['id']}",
            self.key_one,
            "POST",
            {"decision": "approve"},
        )
        self.assertTrue(allowed["resolved"])

    def test_malformed_rule_is_rejected_before_it_can_break_evaluation(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request(
                "/api/rules",
                self.key_one,
                "POST",
                {
                    "rule_type": "per_transaction",
                    "params": {"max_amount": "not-a-number"},
                    "action": "BLOCKED",
                },
            )
        self.assertEqual(error.exception.code, 400)
        _, result = self.request(
            "/v1/transactions/evaluate",
            self.key_one,
            "POST",
            {"amount": 5, "merchant": "safe.example", "category": "api"},
        )
        self.assertEqual(result["decision"], "APPROVED")

    def test_evaluation_rejects_missing_nonfinite_and_oversized_input(self):
        for body, expected in (
            ({}, "amount_required"),
            ({"amount": float("nan")}, "invalid_amount"),
            ({"amount": 1, "description": "x" * 70_000}, "body_too_large"),
        ):
            with self.subTest(expected=expected), self.assertRaises(
                urllib.error.HTTPError
            ) as error:
                self.request(
                    "/v1/transactions/evaluate",
                    self.key_one,
                    "POST",
                    body,
                )
            self.assertEqual(
                error.exception.code, 413 if expected == "body_too_large" else 400
            )
            payload = json.load(error.exception)
            self.assertEqual(payload["error"], expected)

    def test_activity_stream_is_retired_instead_of_leaking_all_tenants(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request("/v1/activity", self.key_one)
        self.assertEqual(error.exception.code, 410)

    def test_admin_token_can_use_dashboard_test_evaluation(self):
        with mock.patch.dict(os.environ, {"ADMIN_TOKEN": "operator-test-token"}):
            _, result = self.request(
                "/v1/transactions/evaluate",
                "operator-test-token",
                "POST",
                {"amount": 750, "merchant": "operator-test", "category": "api"},
            )
        self.assertEqual(result["decision"], "BLOCKED")

    def test_mcp_private_tools_require_auth_and_write_only_to_key_workspace(self):
        call = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "firewall_status",
                "arguments": {},
            },
        }
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request("/api/mcp", method="POST", body=call)
        self.assertEqual(error.exception.code, 401)

        call["params"] = {
            "name": "add_spend_rule",
            "arguments": {
                "rule_type": "merchant_block",
                "params": {"patterns": ["mcp-private.example"]},
                "action": "BLOCKED",
            },
        }
        _, response = self.request(
            "/api/mcp", self.key_one, "POST", call
        )
        created = json.loads(response["result"]["content"][0]["text"])
        _, rules_one = self.request("/api/rules", self.key_one)
        _, rules_two = self.request("/api/rules", self.key_two)
        self.assertIn(created["id"], {rule["id"] for rule in rules_one})
        self.assertNotIn(created["id"], {rule["id"] for rule in rules_two})

    def test_dashboard_starts_in_labelled_sample_mode(self):
        html = templates.dashboard_html()
        self.assertIn("Sample mode", html)
        self.assertIn("sessionStorage", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("EventSource", html)
        self.assertNotIn('id="p-agents"', html)

    def test_subscribe_normalizes_deduplicates_and_unsubscribes(self):
        subscribers = os.path.join(self.tmp.name, "subscribers.txt")
        with mock.patch.object(api, "_SUBSCRIBERS_FILE", subscribers), \
                mock.patch.object(api.drip, "delivery_enabled", return_value=False):
            _, first = self.request(
                "/subscribe",
                method="POST",
                body={
                    "email": "  Buyer@Example.COM ",
                    "ref": "pricing|forged\nsecond-line",
                },
            )
            _, second = self.request(
                "/subscribe",
                method="POST",
                body={"email": "buyer@example.com", "ref": "duplicate"},
            )
            self.assertTrue(first["ok"])
            self.assertTrue(second["ok"])
            with open(subscribers, encoding="utf-8") as handle:
                lines = handle.readlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0], "buyer@example.com|pricingforgedsecond-line\n")

            _, removed = self.request(
                "/unsubscribe",
                method="POST",
                body={"email": "BUYER@example.com"},
            )
            self.assertTrue(removed["ok"])
            self.assertTrue(removed["removed"])
            with open(subscribers, encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "")


if __name__ == "__main__":
    unittest.main()
