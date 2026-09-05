"""Synthetic fixed-price search tool. No credentials or external requests."""
import tempfile
import unittest
from pathlib import Path
from integrations import search_workflow


class SearchAcceptance(unittest.TestCase):
    def test_one_search_is_reserved_before_dispatch_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "budget.sqlite"
            calls = []
            workflow = search_workflow.SearchWorkflow(ledger, budget_cents=10, unit_cents=10)
            self.assertEqual(workflow.search("one", "synthetic query", lambda q: calls.append(q) or ["result"]), ["result"])
            restarted = search_workflow.SearchWorkflow(ledger, budget_cents=10, unit_cents=10)
            with self.assertRaises(search_workflow.SearchBlocked):
                restarted.search("two", "another query", lambda q: calls.append(q))
            self.assertEqual(calls, ["synthetic query"])


    def test_timeout_retains_budget_and_duplicate_is_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            workflow = search_workflow.SearchWorkflow(Path(directory) / "budget.sqlite", budget_cents=10, unit_cents=10)
            def timeout(query):
                raise TimeoutError("synthetic provider timeout")
            with self.assertRaises(TimeoutError):
                workflow.search("one", "query", timeout)
            for request_id in ("one", "two"):
                with self.assertRaises(search_workflow.SearchBlocked):
                    workflow.search(request_id, "query", lambda q: self.fail("must not dispatch"))

    def test_concurrent_calls_cannot_oversubscribe(self):
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as directory:
            workflow = search_workflow.SearchWorkflow(Path(directory) / "budget.sqlite", budget_cents=10, unit_cents=10)
            def attempt(i):
                try:
                    return workflow.search(str(i), "query", lambda q: "dispatched")
                except search_workflow.SearchBlocked:
                    return "blocked"
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(attempt, range(8)))
            self.assertEqual(results.count("dispatched"), 1)
            self.assertEqual(results.count("blocked"), 7)

    def test_policy_change_and_invalid_prices_are_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "budget.sqlite"
            search_workflow.SearchWorkflow(path, budget_cents=10, unit_cents=10)
            with self.assertRaises(search_workflow.SearchBlocked):
                search_workflow.SearchWorkflow(path, budget_cents=100, unit_cents=1)
            for value in (0, -1, True, float("nan"), 1.5):
                with self.assertRaises(ValueError):
                    search_workflow.SearchWorkflow(path, budget_cents=10, unit_cents=value)

    def test_storage_failure_never_dispatches(self):
        with tempfile.TemporaryDirectory() as directory:
            workflow = search_workflow.SearchWorkflow(Path(directory) / "budget.sqlite", budget_cents=10, unit_cents=10)
            workflow.ledger = directory
            import sqlite3
            with self.assertRaises(sqlite3.Error):
                workflow.search("one", "query", lambda q: self.fail("must not dispatch"))


if __name__ == "__main__":
    unittest.main()
