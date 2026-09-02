import hashlib
import hmac
import json
import os
import sqlite3
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
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
        self.assertIsNotNone(agent_id)
        self.assertIsNotNone(context)
        assert agent_id is not None
        assert context is not None
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

    def test_checkout_webhook_ignores_foreign_shared_account_session_before_side_effects(self):
        event = {
            "id": "evt_gitdealflow_foreign",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_live_b1YT1hupteOe5cvg90saJZYucg9Zu9v2MJsJ2RZArs4NTxnpp27pUle8GT",
                    "payment_status": "paid",
                    "amount_total": 100,
                    "currency": "eur",
                    "payment_link": "plink_1TU4ZvCwGoUDklReEjuprkH0",
                    "metadata": {
                        "source": "landing-tripwire",
                        "tier": "teardown",
                    },
                    "line_items": {
                        "data": [
                            {
                                "price": {
                                    "id": "price_1TU4ZuCwGoUDklRev3fh8xib",
                                    "product": "prod_UT0aPLSENVCw5o",
                                }
                            }
                        ]
                    },
                    "customer": "cus_gitdealflow_foreign",
                    "customer_details": {"email": "foreign@example.com"},
                }
            },
        }
        raw = json.dumps(event).encode()

        with mock.patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}), \
                mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(raw, "test-signature")

        self.assertEqual(result, {"ignored": "foreign_checkout_session"})
        self.capture.assert_not_called()
        if os.path.exists(self.billing_db):
            with sqlite3.connect(self.billing_db) as conn:
                tables = {
                    row[0]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                if "api_keys" in tables:
                    self.assertEqual(
                        conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0],
                        0,
                    )
                if "processed_webhook_events" in tables:
                    self.assertEqual(
                        conn.execute(
                            "SELECT COUNT(*) FROM processed_webhook_events"
                        ).fetchone()[0],
                        0,
                    )

    def test_stale_pending_checkout_cannot_authorize_key_issuance(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_stale",
                    "team",
                    "2000-01-01T00:00:00+00:00",
                    "anon-stale",
                    "pricing",
                ),
            )
        event = {
            "id": "evt_owned_stale",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_stale",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "customer": "cus_owned_stale",
                    "subscription": "sub_owned_stale",
                    "customer_details": {"email": "buyer@example.com"},
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"ignored": "foreign_checkout_session"})
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0], 0)
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM processed_webhook_events").fetchone()[0],
                0,
            )
            self.assertEqual(
                conn.execute(
                    "SELECT COUNT(*) FROM pending_sessions WHERE session_id=?",
                    ("cs_owned_stale",),
                ).fetchone()[0],
                1,
            )

    def test_checkout_crossing_the_stale_cutoff_cannot_issue_or_claim(self):
        billing.init_db()
        cutoff = datetime(2030, 1, 1, tzinfo=timezone.utc)
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_cutoff",
                    "team",
                    (cutoff - timedelta(days=30)).isoformat(),
                    "anon-cutoff",
                    "pricing",
                ),
            )
        event = {
            "id": "evt_owned_cutoff",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_cutoff",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "customer": "cus_owned_cutoff",
                    "subscription": "sub_owned_cutoff",
                }
            },
        }

        class AdvancingClock:
            calls = 0

            @classmethod
            def now(cls, _tz=None):
                cls.calls += 1
                return cutoff if cls.calls == 1 else cutoff + timedelta(seconds=1)

            @classmethod
            def fromisoformat(cls, value):
                return datetime.fromisoformat(value)

        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(
            billing, "verify_stripe_signature", return_value=True
        ), mock.patch.object(billing, "datetime", AdvancingClock):
            result = billing.handle_webhook(json.dumps(event).encode(), "test-signature")

        self.assertEqual(result, {"ignored": "foreign_checkout_session"})
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0], 0)
            self.assertEqual(
                conn.execute(
                    "SELECT COUNT(*) FROM processed_webhook_events").fetchone()[0],
                0,
            )
            self.assertEqual(
                conn.execute(
                    "SELECT COUNT(*) FROM pending_sessions WHERE session_id=?",
                    ("cs_owned_cutoff",),
                ).fetchone()[0],
                1,
            )

    def test_duplicate_checkout_does_not_mutate_expired_maintenance_rows(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_duplicate",
                    "team",
                    billing._now(),
                    "anon-duplicate",
                    "pricing",
                ),
            )
            conn.execute(
                "INSERT INTO processed_webhook_events (event_id, event_type, processed_at) "
                "VALUES (?,?,?)",
                ("evt_expired_maintenance", "checkout.session.completed", "2000-01-01T00:00:00+00:00"),
            )
            conn.execute(
                "INSERT INTO processed_webhook_events (event_id, event_type, processed_at) "
                "VALUES (?,?,?)",
                ("evt_owned_duplicate", "checkout.session.completed", billing._now()),
            )
        event = {
            "id": "evt_owned_duplicate",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_duplicate",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "customer": "cus_owned_duplicate",
                    "subscription": "sub_owned_duplicate",
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(
            billing, "verify_stripe_signature", return_value=True
        ), mock.patch.object(
            billing, "_processed_event", return_value=False
        ), mock.patch.object(billing, "_claim_event", return_value=False):
            result = billing.handle_webhook(json.dumps(event).encode(), "test-signature")

        self.assertEqual(
            result, {"duplicate": True, "event": "checkout.session.completed"}
        )
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0], 0)
            self.assertEqual(
                conn.execute(
                    "SELECT COUNT(*) FROM processed_webhook_events WHERE event_id=?",
                    ("evt_expired_maintenance",),
                ).fetchone()[0],
                1,
            )

    def test_atomic_checkout_claim_rejects_a_stale_pending_row_without_a_marker(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_atomic_stale",
                    "team",
                    "2000-01-01T00:00:00+00:00",
                    "anon-atomic-stale",
                    "pricing",
                ),
            )
        with billing._LOCK, billing._conn() as conn:
            outcome, row = billing._claim_owned_checkout_event(
                conn,
                "evt_atomic_stale",
                "checkout.session.completed",
                "cs_atomic_stale",
            )
        self.assertEqual(outcome, "foreign")
        self.assertIsNone(row)
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM processed_webhook_events").fetchone()[0],
                0,
            )

    def test_checkout_ownership_database_error_is_retryable(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_db_error",
                    "team",
                    billing._now(),
                    "anon-db-error",
                    "pricing",
                ),
            )
        event = {
            "id": "evt_db_error",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_db_error",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "customer": "cus_db_error",
                    "subscription": "sub_db_error",
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(
            billing, "verify_stripe_signature", return_value=True
        ), mock.patch.object(
            billing, "_processed_event", return_value=False
        ), mock.patch.object(
            billing.sqlite3,
            "connect",
            side_effect=sqlite3.OperationalError("ownership read unavailable"),
        ):
            with self.assertRaises(sqlite3.OperationalError):
                billing.handle_webhook(json.dumps(event).encode(), "test-signature")

        self.capture.assert_not_called()

    def test_owned_checkout_requires_payment_before_key_issuance(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_unpaid",
                    "team",
                    billing._now(),
                    "anon-unpaid",
                    "pricing",
                ),
            )
        event = {
            "id": "evt_owned_unpaid",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_unpaid",
                    "mode": "subscription",
                    "payment_status": "unpaid",
                    "customer": "cus_owned_unpaid",
                    "subscription": "sub_owned_unpaid",
                    "customer_details": {"email": "buyer@example.com"},
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"ignored": "unpaid_checkout_session"})
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0], 0)
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM processed_webhook_events").fetchone()[0],
                0,
            )
            self.assertEqual(
                conn.execute(
                    "SELECT COUNT(*) FROM pending_sessions WHERE session_id=?",
                    ("cs_owned_unpaid",),
                ).fetchone()[0],
                1,
            )

    def test_owned_checkout_requires_the_locally_expected_mode(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_wrong_mode",
                    "team",
                    billing._now(),
                    "anon-wrong-mode",
                    "pricing",
                ),
            )
        event = {
            "id": "evt_owned_wrong_mode",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_wrong_mode",
                    "mode": "payment",
                    "payment_status": "paid",
                    "customer": "cus_owned_wrong_mode",
                    "subscription": None,
                    "customer_details": {"email": "buyer@example.com"},
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"ignored": "invalid_owned_checkout_session"})
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0], 0)
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM processed_webhook_events").fetchone()[0],
                0,
            )

    def test_owned_subscription_checkout_requires_a_subscription_id(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_missing_subscription",
                    "team",
                    billing._now(),
                    "anon-missing-subscription",
                    "pricing",
                ),
            )
        event = {
            "id": "evt_owned_missing_subscription",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_missing_subscription",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "customer": "cus_owned_missing_subscription",
                    "subscription": None,
                    "customer_details": {"email": "buyer@example.com"},
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"ignored": "invalid_owned_checkout_session"})
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0], 0)
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM processed_webhook_events").fetchone()[0],
                0,
            )

    def test_owned_subscription_checkout_requires_a_customer_id(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_missing_customer",
                    "team",
                    billing._now(),
                    "anon-missing-customer",
                    "pricing",
                ),
            )
        event = {
            "id": "evt_owned_missing_customer",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_missing_customer",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "customer": None,
                    "subscription": "sub_owned_missing_customer",
                    "customer_details": {"email": "buyer@example.com"},
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"ignored": "invalid_owned_checkout_session"})
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0], 0)
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM processed_webhook_events").fetchone()[0],
                0,
            )

    def test_owned_checkout_normalizes_expanded_stripe_ids(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_expanded",
                    "team",
                    billing._now(),
                    "anon-expanded",
                    "pricing",
                ),
            )
        event = {
            "id": "evt_owned_expanded",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_expanded",
                    "mode": "subscription",
                    "payment_status": "paid",
                    "customer": {"id": "cus_owned_expanded"},
                    "subscription": {"id": "sub_owned_expanded"},
                    "customer_details": {"email": "buyer@example.com"},
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"issued": True, "tier": "team"})
        with sqlite3.connect(self.billing_db) as conn:
            row = conn.execute(
                "SELECT stripe_customer_id, stripe_subscription_id FROM api_keys "
                "WHERE stripe_checkout_session=?",
                ("cs_owned_expanded",),
            ).fetchone()
        self.assertEqual(row, ("cus_owned_expanded", "sub_owned_expanded"))

    def test_owned_paid_one_time_checkout_still_issues_its_local_tier(self):
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_owned_agent_pilot",
                    "agent_pilot",
                    billing._now(),
                    "anon-agent-pilot",
                    "agent-reliability-sprint",
                ),
            )
        event = {
            "id": "evt_owned_agent_pilot",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_owned_agent_pilot",
                    "mode": "payment",
                    "payment_status": "paid",
                    "amount_total": 150000,
                    "currency": "eur",
                    "customer": None,
                    "subscription": None,
                    "customer_details": {"email": "buyer@example.com"},
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"issued": True, "tier": "agent_pilot"})
        with sqlite3.connect(self.billing_db) as conn:
            row = conn.execute(
                "SELECT tier, stripe_subscription_id FROM api_keys "
                "WHERE stripe_checkout_session=?",
                ("cs_owned_agent_pilot",),
            ).fetchone()
            pending_count = conn.execute(
                "SELECT COUNT(*) FROM pending_sessions WHERE session_id=?",
                ("cs_owned_agent_pilot",),
            ).fetchone()[0]
        self.assertEqual(row, ("agent_pilot", None))
        self.assertEqual(pending_count, 0)

    def test_foreign_subscription_events_are_ignored_before_side_effects(self):
        for event_type in (
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ):
            with self.subTest(event_type=event_type):
                event = {
                    "id": "evt_foreign_subscription_" + event_type.rsplit(".", 1)[-1],
                    "type": event_type,
                    "data": {
                        "object": {
                            "id": "sub_foreign",
                            "customer": "cus_foreign",
                            "status": "canceled",
                            "metadata": {"plan": "team"},
                        }
                    },
                }
                raw = json.dumps(event).encode()
                with mock.patch.dict(
                    os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
                ), mock.patch.object(
                    billing, "verify_stripe_signature", return_value=True
                ):
                    result = billing.handle_webhook(raw, "test-signature")

                self.assertEqual(result, {"ignored": "foreign_subscription"})
                self.capture.assert_not_called()
                self.assertFalse(os.path.exists(self.billing_db))

    def test_subscription_customer_mismatch_is_ignored_without_mutation(self):
        key, _ = billing._issue_key(
            "team",
            "buyer@example.com",
            "cus_owned",
            "sub_owned",
            "cs_owned",
            "anon-owned",
        )
        event = {
            "id": "evt_customer_collision",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_owned",
                    "customer": "cus_foreign",
                    "status": "canceled",
                }
            },
        }
        raw = json.dumps(event).encode()
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(raw, "test-signature")

        self.assertEqual(result, {"ignored": "foreign_subscription"})
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            active = conn.execute(
                "SELECT active FROM api_keys WHERE key=?", (key,)
            ).fetchone()[0]
            event_count = conn.execute(
                "SELECT COUNT(*) FROM processed_webhook_events"
            ).fetchone()[0]
        self.assertEqual(active, 1)
        self.assertEqual(event_count, 0)

    def test_subscription_ownership_database_error_is_retryable(self):
        billing._issue_key(
            "team",
            "buyer@example.com",
            "cus_subscription_db_error",
            "sub_subscription_db_error",
            "cs_subscription_db_error",
            "anon-subscription-db-error",
        )
        event = {
            "id": "evt_subscription_db_error",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_subscription_db_error",
                    "customer": "cus_subscription_db_error",
                    "status": "canceled",
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(
            billing, "verify_stripe_signature", return_value=True
        ), mock.patch.object(
            billing, "_processed_event", return_value=False
        ), mock.patch.object(
            billing.sqlite3,
            "connect",
            side_effect=sqlite3.OperationalError("ownership read unavailable"),
        ):
            with self.assertRaises(sqlite3.OperationalError):
                billing.handle_webhook(json.dumps(event).encode(), "test-signature")

        self.capture.assert_not_called()

    def test_subscription_lifecycle_mutates_only_the_validated_customer(self):
        key_a, _ = billing._issue_key(
            "team",
            "a@example.com",
            "cus_a",
            "sub_collision",
            "cs_a",
            "anon-a",
        )
        key_b, _ = billing._issue_key(
            "team",
            "b@example.com",
            "cus_b",
            "sub_collision",
            "cs_b",
            "anon-b",
        )
        event = {
            "id": "evt_subscription_collision",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_collision",
                    "customer": "cus_a",
                    "status": "canceled",
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"deactivated": "sub_collision"})
        with sqlite3.connect(self.billing_db) as conn:
            rows = dict(
                conn.execute(
                    "SELECT key, active FROM api_keys WHERE key IN (?, ?)",
                    (key_a, key_b),
                ).fetchall()
            )
        self.assertEqual(rows[key_a], 0)
        self.assertEqual(rows[key_b], 1)
        self.capture.assert_called_once_with(
            "subscription_canceled", "anon-a", {"plan": "team"}
        )

    def test_enabled_event_without_a_valid_id_is_rejected_before_side_effects(self):
        key, _ = billing._issue_key(
            "team",
            "buyer@example.com",
            "cus_missing_event_id",
            "sub_missing_event_id",
            "cs_missing_event_id",
            "anon-missing-event-id",
        )
        event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_missing_event_id",
                    "customer": "cus_missing_event_id",
                    "status": "canceled",
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            first = billing.handle_webhook(json.dumps(event).encode(), "test-signature")
            second = billing.handle_webhook(json.dumps(event).encode(), "test-signature")

        self.assertEqual(first, {"ignored": "invalid_event_id"})
        self.assertEqual(second, {"ignored": "invalid_event_id"})
        self.capture.assert_not_called()
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(
                conn.execute("SELECT active FROM api_keys WHERE key=?", (key,)).fetchone()[0],
                1,
            )
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM processed_webhook_events").fetchone()[0],
                0,
            )

    def test_subscription_event_is_claimed_before_mutation_analytics(self):
        billing._issue_key(
            "team",
            "buyer@example.com",
            "cus_atomic",
            "sub_atomic",
            "cs_atomic",
            "anon-atomic",
        )
        event = {
            "id": "evt_atomic_deleted",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_atomic",
                    "customer": "cus_atomic",
                    "status": "canceled",
                }
            },
        }
        marker_counts = []

        def capture_after_claim(name, _distinct_id, _properties):
            if name == "subscription_canceled":
                with sqlite3.connect(self.billing_db) as conn:
                    marker_counts.append(
                        conn.execute(
                            "SELECT COUNT(*) FROM processed_webhook_events "
                            "WHERE event_id=?",
                            ("evt_atomic_deleted",),
                        ).fetchone()[0]
                    )

        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(
            billing, "verify_stripe_signature", return_value=True
        ), mock.patch.object(billing, "_capture", side_effect=capture_after_claim):
            result = billing.handle_webhook(
                json.dumps(event).encode(), "test-signature"
            )

        self.assertEqual(result, {"deactivated": "sub_atomic"})
        self.assertEqual(marker_counts, [1])

    def test_concurrent_subscription_replays_have_one_claim_and_one_analytics_event(self):
        billing._issue_key(
            "team",
            "buyer@example.com",
            "cus_concurrent",
            "sub_concurrent",
            "cs_concurrent",
            "anon-concurrent",
        )
        event = {
            "id": "evt_concurrent_deleted",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_concurrent",
                    "customer": "cus_concurrent",
                    "status": "canceled",
                }
            },
        }
        raw = json.dumps(event).encode()
        barrier = threading.Barrier(2)
        results = []
        errors = []
        result_lock = threading.Lock()

        def force_both_past_fast_read(_event_id):
            barrier.wait(timeout=5)
            return False

        def deliver():
            try:
                result = billing.handle_webhook(raw, "test-signature")
                with result_lock:
                    results.append(result)
            except Exception as exc:  # pragma: no cover - assertion reports details
                with result_lock:
                    errors.append(exc)

        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(
            billing, "verify_stripe_signature", return_value=True
        ), mock.patch.object(
            billing, "_processed_event", side_effect=force_both_past_fast_read
        ):
            threads = [threading.Thread(target=deliver) for _ in range(2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=10)

        self.assertEqual(errors, [])
        self.assertEqual(
            sorted(results, key=lambda result: "duplicate" not in result),
            [
                {"duplicate": True, "event": "customer.subscription.deleted"},
                {"deactivated": "sub_concurrent"},
            ],
        )
        self.capture.assert_called_once_with(
            "subscription_canceled", "anon-concurrent", {"plan": "team"}
        )
        with sqlite3.connect(self.billing_db) as conn:
            self.assertEqual(
                conn.execute(
                    "SELECT COUNT(*) FROM processed_webhook_events "
                    "WHERE event_id=?",
                    ("evt_concurrent_deleted",),
                ).fetchone()[0],
                1,
            )

    def test_owned_subscription_lifecycle_uses_local_subscription_and_customer(self):
        key, _ = billing._issue_key(
            "team",
            "buyer@example.com",
            "cus_owned",
            "sub_owned",
            "cs_owned",
            "anon-owned",
        )
        updated = {
            "id": "evt_owned_updated",
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_owned",
                    "customer": "cus_owned",
                    "status": "active",
                }
            },
        }
        deleted = {
            "id": "evt_owned_deleted",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_owned",
                    "customer": "cus_owned",
                    "status": "canceled",
                }
            },
        }
        with mock.patch.dict(
            os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        ), mock.patch.object(billing, "verify_stripe_signature", return_value=True):
            updated_result = billing.handle_webhook(
                json.dumps(updated).encode(), "test-signature"
            )
            deleted_result = billing.handle_webhook(
                json.dumps(deleted).encode(), "test-signature"
            )

        self.assertEqual(updated_result, {"ok": True, "status": "active"})
        self.assertEqual(deleted_result, {"deactivated": "sub_owned"})
        with sqlite3.connect(self.billing_db) as conn:
            active = conn.execute(
                "SELECT active FROM api_keys WHERE key=?", (key,)
            ).fetchone()[0]
            event_count = conn.execute(
                "SELECT COUNT(*) FROM processed_webhook_events"
            ).fetchone()[0]
        self.assertEqual(active, 0)
        self.assertEqual(event_count, 2)
        self.capture.assert_called_once_with(
            "subscription_canceled",
            "anon-owned",
            {"plan": "team"},
        )

    def test_unsubscribed_invoice_and_refund_events_are_ignored_without_records(self):
        for event_type in (
            "invoice.paid",
            "invoice.payment_failed",
            "charge.refunded",
            "refund.created",
        ):
            with self.subTest(event_type=event_type):
                event = {
                    "id": "evt_unsubscribed_" + event_type.replace(".", "_"),
                    "type": event_type,
                    "data": {
                        "object": {
                            "id": "in_or_refund_foreign",
                            "customer": "cus_foreign",
                            "subscription": "sub_foreign",
                        }
                    },
                }
                with mock.patch.dict(
                    os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
                ), mock.patch.object(
                    billing, "verify_stripe_signature", return_value=True
                ):
                    result = billing.handle_webhook(
                        json.dumps(event).encode(), "test-signature"
                    )

                self.assertEqual(result, {"ignored": event_type})
                self.capture.assert_not_called()
                self.assertFalse(os.path.exists(self.billing_db))

    def test_checkout_webhook_is_idempotent_and_analytics_are_sanitized(self):
        event = {
            "id": "evt_repeat",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_sensitive",
                    "mode": "subscription",
                    "payment_status": "paid",
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
        billing.init_db()
        with sqlite3.connect(self.billing_db) as conn:
            conn.execute(
                "INSERT INTO pending_sessions "
                "(session_id, plan, created_at, analytics_id, source_cta) "
                "VALUES (?,?,?,?,?)",
                (
                    "cs_sensitive",
                    "team",
                    billing._now(),
                    "anon-browser-2",
                    "pricing",
                ),
            )
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

    def test_stripe_signature_verification_accepts_valid_and_rejects_bad_or_stale(self):
        raw = b'{"id":"evt_signature_fixture"}'
        secret = "whsec_fixture"
        now = int(time.time())
        digest = hmac.new(
            secret.encode(),
            f"{now}.".encode() + raw,
            hashlib.sha256,
        ).hexdigest()
        valid_header = f"t={now},v1={digest}"
        stale_time = now - 1000
        stale_digest = hmac.new(
            secret.encode(),
            f"{stale_time}.".encode() + raw,
            hashlib.sha256,
        ).hexdigest()

        self.assertTrue(
            billing.verify_stripe_signature(raw, valid_header, secret)
        )
        self.assertFalse(
            billing.verify_stripe_signature(raw + b" ", valid_header, secret)
        )
        self.assertFalse(
            billing.verify_stripe_signature(
                raw,
                f"t={stale_time},v1={stale_digest}",
                secret,
            )
        )

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
