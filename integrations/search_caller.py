"""Owner-wired local search caller. The CLI uses synthetic transport only.

Injected transports are trusted owner code: they must honor maximum_cents and
retries=0. This is not credential isolation or a provider-side billing cap.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import tempfile

from integrations.search_workflow import SearchBlocked, SearchWorkflow


class SearchCaller:
    def __init__(self, directory, *, budget_cents, maximum_cents, retries, transport):
        if type(retries) is not int or retries != 0:
            raise ValueError('Only zero retries is supported')
        if type(maximum_cents) is not int or maximum_cents <= 0:
            raise ValueError('Maximum must be positive integer cents')
        if not callable(transport):
            raise ValueError('Owner transport required')
        self._directory = Path(directory)
        self._ledger = self._directory / 'search.sqlite'
        self._check_private(self._directory, directory=True)
        try:
            fd = os.open(self._ledger, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(fd)
        self._check_private(self._ledger)
        self._workflow = SearchWorkflow(self._ledger, budget_cents=budget_cents, unit_cents=maximum_cents)
        self._maximum = maximum_cents
        self._transport = transport

    @staticmethod
    def _check_private(path, *, directory=False):
        info = path.lstat()
        kind_ok = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
        if not kind_ok or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise SearchBlocked('Owner-only directory and regular ledger required')

    def handle(self, request):
        # No caller-supplied price, path, provider, retry, or budget overrides.
        if type(request) is not dict or set(request) != {'request_id', 'query'}:
            raise SearchBlocked('Only request_id and query are accepted')
        self._check_private(self._directory, directory=True)
        self._check_private(self._ledger)
        return self._workflow.search(request['request_id'], request['query'], self._dispatch)

    def _dispatch(self, query):
        # Exactly one invocation. Exceptions propagate; reservation is retained.
        return self._transport(query, maximum_cents=self._maximum, retries=0)


def main():
    calls = []
    def synthetic_transport(query, *, maximum_cents, retries):
        calls.append({'maximum_cents': maximum_cents, 'retries': retries})
        return ['synthetic local result']
    with tempfile.TemporaryDirectory() as directory:
        caller = SearchCaller(directory, budget_cents=10, maximum_cents=10,
                              retries=0, transport=synthetic_transport)
        result = caller.handle({'request_id': 'synthetic-one', 'query': 'synthetic query'})
        try:
            caller.handle({'request_id': 'synthetic-two', 'query': 'synthetic query'})
        except SearchBlocked:
            blocked = True
        else:
            blocked = False
        assert blocked and len(calls) == 1
        print(json.dumps({'synthetic': True, 'result': result, 'dispatches': calls,
                          'second_request_blocked': blocked, 'network_calls': 0}))


if __name__ == '__main__':
    main()
