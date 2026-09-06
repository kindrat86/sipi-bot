"""Local caller acceptance with synthetic transport, never a paid provider."""
import importlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class CallerAcceptance(unittest.TestCase):
    def test_registered_search_reserves_declared_maximum_before_transport(self):
        self.assertIsNotNone(importlib.util.find_spec('integrations.search_caller'),
                             'Missing runnable caller boundary')
        from integrations.search_caller import SearchCaller
        with tempfile.TemporaryDirectory() as directory:
            calls = []
            def transport(query, *, maximum_cents, retries):
                with sqlite3.connect(Path(directory) / 'search.sqlite') as db:
                    self.assertEqual(db.execute('SELECT SUM(cents) FROM reservations').fetchone()[0], 10)
                calls.append((query, maximum_cents, retries))
                return ['synthetic result']
            caller = SearchCaller(directory, budget_cents=10, maximum_cents=10, retries=0, transport=transport)
            self.assertEqual(caller.handle({'request_id': 'one', 'query': 'synthetic'}), ['synthetic result'])
            self.assertEqual(calls, [('synthetic', 10, 0)])
            with self.assertRaises(Exception):
                caller.handle({'request_id': 'two', 'query': 'synthetic'})
            self.assertEqual(len(calls), 1)


    def test_decisions_never_dispatch_unless_exact_approved(self):
        from integrations.search_caller import SearchCaller
        from integrations.search_workflow import SearchBlocked
        from types import SimpleNamespace
        for decision in ({}, {'decision': None}, {'decision': 'approved'},
                         {'decision': 'REVIEW'}, {'decision': 'UNKNOWN'}):
            with self.subTest(decision=decision), tempfile.TemporaryDirectory() as directory:
                caller = SearchCaller(directory, budget_cents=10, maximum_cents=10, retries=0,
                                      transport=lambda *a, **k: self.fail('must not dispatch'))
                with patch('integrations.search_workflow.evaluate', return_value=SimpleNamespace(to_dict=lambda: decision)):
                    with self.assertRaises(SearchBlocked):
                        caller.handle({'request_id': 'one', 'query': 'synthetic'})

    def test_timeout_no_retry_and_restart_retains_reservation(self):
        from integrations.search_caller import SearchCaller
        from integrations.search_workflow import SearchBlocked
        with tempfile.TemporaryDirectory() as directory:
            calls = []
            def timeout(*a, **k):
                calls.append(k)
                raise TimeoutError('synthetic timeout')
            caller = SearchCaller(directory, budget_cents=10, maximum_cents=10, retries=0, transport=timeout)
            with self.assertRaises(TimeoutError):
                caller.handle({'request_id': 'one', 'query': 'synthetic'})
            restarted = SearchCaller(directory, budget_cents=10, maximum_cents=10, retries=0, transport=timeout)
            for request_id in ('one', 'two'):
                with self.assertRaises(SearchBlocked):
                    restarted.handle({'request_id': request_id, 'query': 'synthetic'})
            self.assertEqual(len(calls), 1)

    def test_contract_override_and_unsafe_storage_rejected(self):
        from integrations.search_caller import SearchCaller
        from integrations.search_workflow import SearchBlocked
        with tempfile.TemporaryDirectory() as directory:
            options = dict(budget_cents=10, maximum_cents=10, retries=0,
                           transport=lambda *a, **k: self.fail('must not dispatch'))
            for retries in (1, -1, True, None):
                with self.assertRaises(ValueError):
                    SearchCaller(directory, **dict(options, retries=retries))
            caller = SearchCaller(directory, **options)
            for override in ('maximum_cents', 'ledger', 'retries', 'transport', 'budget_cents'):
                with self.assertRaises(SearchBlocked):
                    caller.handle({'request_id': 'one', 'query': 'synthetic', override: 0})
            ledger = Path(directory) / 'search.sqlite'
            ledger.chmod(0o644)
            with self.assertRaises(SearchBlocked):
                caller.handle({'request_id': 'one', 'query': 'synthetic'})
            ledger.chmod(0o600)
            ledger.unlink()
            with self.assertRaises(FileNotFoundError):
                caller.handle({'request_id': 'one', 'query': 'synthetic'})

    def test_concurrent_caller_reservations(self):
        from integrations.search_caller import SearchCaller
        from integrations.search_workflow import SearchBlocked
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as directory:
            caller = SearchCaller(directory, budget_cents=10, maximum_cents=10, retries=0,
                                  transport=lambda *a, **k: 'synthetic dispatch')
            def attempt(i):
                try:
                    return caller.handle({'request_id': str(i), 'query': 'synthetic'})
                except SearchBlocked:
                    return 'blocked'
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(attempt, range(8)))
            self.assertEqual(results.count('synthetic dispatch'), 1)
            self.assertEqual(results.count('blocked'), 7)


if __name__ == '__main__':
    unittest.main()
