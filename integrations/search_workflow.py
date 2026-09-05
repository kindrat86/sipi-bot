"""One fixed-price search-tool boundary with durable, conservative reservations.

The owner supplies a tool callable and a verified maximum per-call price. This
is not a provider billing cap and cannot govern calls outside this boundary.
"""
from __future__ import annotations

import sqlite3
from spendfirewall.engine import Transaction, Rule, evaluate


class SearchBlocked(RuntimeError):
    pass


class SearchWorkflow:
    def __init__(self, ledger, *, budget_cents, unit_cents):
        if any(type(n) is not int or n <= 0 for n in (budget_cents, unit_cents)):
            raise ValueError("Budget and maximum unit price must be positive integer cents")
        self.ledger = str(ledger)
        self.budget_cents = budget_cents
        self.unit_cents = unit_cents
        with sqlite3.connect(self.ledger) as db:
            db.execute("CREATE TABLE IF NOT EXISTS policy (id INTEGER PRIMARY KEY CHECK(id=1), budget INTEGER, unit INTEGER)")
            db.execute("INSERT OR IGNORE INTO policy VALUES (1, ?, ?)", (budget_cents, unit_cents))
            if db.execute("SELECT budget, unit FROM policy WHERE id=1").fetchone() != (budget_cents, unit_cents):
                raise SearchBlocked("Ledger policy differs; owner reconciliation required")
            db.execute("CREATE TABLE IF NOT EXISTS reservations (request_id TEXT PRIMARY KEY, cents INTEGER NOT NULL)")

    def search(self, request_id, query, tool):
        if not isinstance(request_id, str) or not request_id.strip():
            raise SearchBlocked("Stable request ID required")
        if not isinstance(query, str) or not query.strip():
            raise SearchBlocked("Nonempty search query required")
        # BEGIN IMMEDIATE serializes concurrent reservations across processes.
        # Commit BEFORE dispatch. Timeout/crash/error retains the reservation:
        # a failed response is not proof the provider did not charge.
        with sqlite3.connect(self.ledger, timeout=2) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM reservations WHERE request_id=?", (request_id,)).fetchone():
                raise SearchBlocked("Request already reserved; automatic replay denied")
            reserved = db.execute("SELECT COALESCE(SUM(cents),0) FROM reservations").fetchone()[0]
            result = evaluate(Transaction(amount=self.unit_cents / 100, merchant="search-tool", category="api"),
                              [Rule(id="workflow-budget", rule_type="daily_total", params={"max_amount": self.budget_cents / 100})],
                              {"daily_spend": reserved / 100})
            if reserved + self.unit_cents > self.budget_cents or result.to_dict().get("decision") != "APPROVED":
                raise SearchBlocked("Search budget exhausted or policy denied")
            db.execute("INSERT INTO reservations VALUES (?, ?)", (request_id, self.unit_cents))
        return tool(query)
