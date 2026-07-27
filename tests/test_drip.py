import io
import json
import os
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from spendfirewall import drip


class _Response:
    def __init__(self, body=b'{"id":"email_123"}'):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


class DripPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.subscribers = self.root / "subscribers.txt"
        self.db = self.root / "drip.db"
        self.env = mock.patch.dict(
            os.environ,
            {
                "DRIP_ENABLED": "true",
                "RESEND_API_KEY": "re_test_only",
                "DRIP_DB": str(self.db),
                "SUBS_FILE": str(self.subscribers),
            },
            clear=False,
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    def _write_subscribers(self, *rows):
        self.subscribers.write_text("\n".join(rows) + "\n", encoding="utf-8")

    def _state(self, email):
        with sqlite3.connect(self.db) as conn:
            return conn.execute(
                "SELECT soap_day, last_sent, provider_id "
                "FROM drip_state WHERE email=?",
                (email,),
            ).fetchone()

    def test_disabled_by_default_and_does_not_touch_transport(self):
        os.environ.pop("DRIP_ENABLED")
        self._write_subscribers("person@example.com|homepage")
        with mock.patch.object(drip, "_send_resend") as send:
            result = drip.send_soap_operas()
        self.assertEqual(result, {"skipped": "disabled"})
        send.assert_not_called()
        self.assertFalse(self.db.exists())

    def test_normalizes_and_deduplicates_subscribers(self):
        self._write_subscribers(
            " Person@Example.COM |homepage",
            "person@example.com|duplicate",
            "not-an-email",
            "bad address@example.com|invalid",
        )
        with mock.patch.object(
            drip, "_send_resend", return_value={"ok": True, "id": "email_1"}
        ) as send, mock.patch.object(drip.time, "time", return_value=1000.0):
            result = drip.send_soap_operas()

        self.assertEqual(result["sent"], 1)
        send.assert_called_once()
        self.assertEqual(send.call_args.args[0], "person@example.com")
        self.assertEqual(self._state("person@example.com"), (1, 1000.0, "email_1"))

    def test_advances_only_after_full_24_hour_interval(self):
        self._write_subscribers("person@example.com|homepage")
        calls = []

        def accepted(email, subject, html, key):
            calls.append((subject, key))
            return {"ok": True, "id": f"email_{len(calls)}"}

        with mock.patch.object(drip, "_send_resend", side_effect=accepted):
            with mock.patch.object(drip.time, "time", return_value=10_000.0):
                first = drip.send_soap_operas()
            with mock.patch.object(
                drip.time, "time", return_value=10_000.0 + 86_399
            ):
                early = drip.send_soap_operas()
            with mock.patch.object(
                drip.time, "time", return_value=10_000.0 + 86_400
            ):
                due = drip.send_soap_operas()

        self.assertEqual(first["sent"], 1)
        self.assertEqual(early["sent"], 0)
        self.assertEqual(early["deferred"], 1)
        self.assertEqual(due["sent"], 1)
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0][1], calls[1][1])
        self.assertEqual(self._state("person@example.com")[0], 2)

    def test_stops_after_five_soap_messages_and_never_activates_seinfeld(self):
        self._write_subscribers("person@example.com|homepage")
        with mock.patch.object(
            drip, "_send_resend", return_value={"ok": True, "id": "accepted"}
        ) as send:
            for day in range(5):
                with mock.patch.object(
                    drip.time, "time", return_value=1000.0 + day * 86_400
                ):
                    self.assertEqual(drip.send_soap_operas()["sent"], 1)
            with mock.patch.object(
                drip.time, "time", return_value=1000.0 + 5 * 86_400
            ):
                finished = drip.send_soap_operas()

        self.assertEqual(send.call_count, 5)
        self.assertEqual(finished["sent"], 0)
        self.assertEqual(finished["complete"], 1)
        self.assertEqual(self._state("person@example.com")[0], 5)

    def test_idempotency_key_is_stable_across_transient_retry(self):
        self._write_subscribers("person@example.com|homepage")
        keys = []

        def fail_then_succeed(email, subject, html, key):
            keys.append(key)
            if len(keys) == 1:
                raise drip.ResendError("server", 503, stop_batch=True)
            return {"ok": True, "id": "email_retry"}

        output = io.StringIO()
        with mock.patch.object(
            drip, "_send_resend", side_effect=fail_then_succeed
        ), mock.patch.object(drip.time, "time", return_value=5000.0), \
                redirect_stdout(output):
            failed = drip.send_soap_operas()
            retried = drip.send_soap_operas()

        self.assertEqual(failed["stopped"], "server")
        self.assertEqual(retried["sent"], 1)
        self.assertEqual(keys[0], keys[1])
        self.assertNotIn("person@example.com", output.getvalue())
        self.assertEqual(self._state("person@example.com")[0], 1)

    def test_auth_and_rate_limit_errors_stop_batch_without_pii_logs(self):
        self._write_subscribers(
            "first@example.com|homepage",
            "second@example.com|homepage",
        )
        cases = (
            (401, "authentication", None),
            (403, "authentication", None),
            (429, "rate_limit", "17"),
        )
        for status, category, retry_after in cases:
            with self.subTest(status=status):
                error = drip.ResendError(
                    category,
                    status,
                    stop_batch=True,
                    retry_after=retry_after,
                )
                output = io.StringIO()
                with mock.patch.object(
                    drip, "_send_resend", side_effect=error
                ) as send, redirect_stdout(output):
                    result = drip.send_soap_operas()

                self.assertEqual(send.call_count, 1)
                self.assertEqual(result["failed"], 1)
                self.assertEqual(result["stopped"], category)
                if retry_after:
                    self.assertEqual(result["retry_after"], retry_after)
                self.assertNotIn("first@example.com", output.getvalue())
                self.assertNotIn("second@example.com", output.getvalue())

    def test_concurrent_run_is_serialized(self):
        self._write_subscribers("person@example.com|homepage")
        entered = threading.Event()
        release = threading.Event()
        first_result = {}

        def delayed_send(email, subject, html, key):
            entered.set()
            self.assertTrue(release.wait(timeout=5))
            return {"ok": True, "id": "email_concurrent"}

        def run_first():
            first_result.update(drip.send_soap_operas())

        with mock.patch.object(drip, "_send_resend", side_effect=delayed_send), \
                mock.patch.object(drip.time, "time", return_value=9000.0):
            thread = threading.Thread(target=run_first)
            thread.start()
            self.assertTrue(entered.wait(timeout=5))
            second = drip.send_soap_operas()
            release.set()
            thread.join(timeout=5)

        self.assertFalse(thread.is_alive())
        self.assertEqual(second, {"skipped": "already_running"})
        self.assertEqual(first_result["sent"], 1)

    def test_resend_request_has_idempotency_header_and_encoded_unsubscribe(self):
        with mock.patch.object(
            drip.urllib.request, "urlopen", return_value=_Response()
        ) as urlopen:
            result = drip._send_resend(
                "plus+tag@example.com",
                "Subject",
                "<p>Body</p>UNSUBSCRIBE_LINK",
                "stable-delivery-key",
            )

        self.assertEqual(result, {"ok": True, "id": "email_123"})
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.get_header("Idempotency-key"), "stable-delivery-key"
        )
        payload = json.loads(request.data)
        self.assertIn("plus%2Btag%40example.com", payload["html"])

    def test_transport_classifies_provider_errors_without_provider_body(self):
        for status, expected, stop in (
            (401, "authentication", True),
            (403, "authentication", True),
            (429, "rate_limit", True),
            (422, "recipient", False),
            (503, "server", True),
        ):
            with self.subTest(status=status):
                error = urllib.error.HTTPError(
                    "https://api.resend.com/emails",
                    status,
                    "provider included sensitive recipient@example.com",
                    {"Retry-After": "11"},
                    io.BytesIO(b'{"message":"recipient@example.com invalid"}'),
                )
                with mock.patch.object(
                    drip.urllib.request, "urlopen", side_effect=error
                ):
                    with self.assertRaises(drip.ResendError) as raised:
                        drip._send_resend(
                            "recipient@example.com",
                            "Subject",
                            "UNSUBSCRIBE_LINK",
                            "delivery-key",
                        )
                self.assertEqual(raised.exception.category, expected)
                self.assertEqual(raised.exception.stop_batch, stop)
                self.assertNotIn(
                    "recipient@example.com", str(raised.exception)
                )
                if status == 429:
                    self.assertEqual(raised.exception.retry_after, "11")

    def test_default_database_uses_data_mount_when_present(self):
        with mock.patch.dict(os.environ, {}, clear=False), \
                mock.patch.object(drip.os.path, "isdir", return_value=True):
            os.environ.pop("DRIP_DB", None)
            self.assertEqual(drip._db_path(), "/data/drip.db")

    def test_disabled_scheduler_does_not_start_thread(self):
        os.environ["DRIP_ENABLED"] = "false"
        with mock.patch.object(drip.threading, "Thread") as thread:
            drip.start_drip_scheduler()
        thread.assert_not_called()


if __name__ == "__main__":
    unittest.main()
