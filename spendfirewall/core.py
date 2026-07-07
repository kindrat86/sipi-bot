"""core.py — the capability, wired to persistence.

This is the single entrypoint all three surfaces (HTTP API, MCP, CLI) call.
It pulls historical context from the store, runs the pure engine, records the
result, and returns a plain dict.
"""
from __future__ import annotations

from typing import Any, Optional

from . import engine, store


def evaluate_transaction(
    amount: float,
    merchant: str = "",
    category: str = "",
    description: str = "",
    currency: str = "USD",
    agent_id: Optional[str] = None,
    timestamp: Optional[str] = None,
    record: bool = True,
) -> dict[str, Any]:
    """Evaluate a proposed agent spend. Returns the decision dict.

    This is THE call an autonomous agent makes before spending money.
    """
    txn = engine.Transaction(
        amount=amount, currency=currency, merchant=merchant,
        category=category, description=description, agent_id=agent_id,
        timestamp=timestamp,
    )
    rules = store.get_rules_for_agent(agent_id)

    # Build historical context for the pure engine.
    max_window = 3600
    for r in rules:
        if r.rule_type == "velocity":
            max_window = max(max_window, int(r.params.get("window_seconds", 3600)))
    ctx = {
        "daily_spend": store.get_daily_spend(agent_id),
        "recent_count": store.count_recent_transactions(agent_id, max_window),
    }

    result = engine.evaluate(txn, rules, ctx)

    txn_id = None
    if record:
        txn_id = store.record_transaction(txn, result)

    out = result.to_dict()
    out["transaction_id"] = txn_id
    out["amount"] = txn.amount
    out["merchant"] = txn.merchant
    out["category"] = txn.category
    return out


def register_agent(name: str) -> dict[str, Any]:
    return store.create_agent(name)


def add_rule(rule_type: str, params: dict, action: str = "BLOCKED",
             priority: int = 100, label: str = "", agent_id: Optional[str] = None) -> dict[str, Any]:
    return store.add_rule(rule_type, params, action, priority, label, agent_id)


def status() -> dict[str, Any]:
    store.init_db()  # lazy-load: ensure DB + seed rules exist before reporting
    return store.get_stats()
