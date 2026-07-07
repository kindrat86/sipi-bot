"""sipi_guard.py — tiny stdlib client for the sipi.bot spend firewall.

Zero dependencies. Drop into any agent codebase. The one function every agent
should call before it spends money:

    from sipi_guard import guard, SpendBlocked

    guard(amount=42.00, merchant="openai.com", category="api")  # raises if not allowed
"""
from __future__ import annotations

import json
import os
import urllib.request

SIPI_URL = os.environ.get("SIPI_URL", "https://sipi.bot")
SIPI_API_KEY = os.environ.get("SIPI_API_KEY")  # optional: sk_live_... for hosted tiers


class SpendBlocked(Exception):
    """Raised when the firewall BLOCKS a transaction."""
    def __init__(self, reason: str, detail: dict):
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


class SpendNeedsApproval(Exception):
    """Raised when the firewall FLAGS a transaction for human approval."""
    def __init__(self, reason: str, detail: dict):
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


def evaluate(amount, merchant="", category="", description="", currency="USD") -> dict:
    """Call the firewall. Returns the raw decision dict (no exceptions)."""
    body = json.dumps({
        "amount": amount, "merchant": merchant, "category": category,
        "description": description, "currency": currency,
    }).encode()
    req = urllib.request.Request(
        f"{SIPI_URL}/v1/transactions/evaluate", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if SIPI_API_KEY:
        req.add_header("Authorization", f"Bearer {SIPI_API_KEY}")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def guard(amount, merchant="", category="", description="", currency="USD") -> dict:
    """Enforce the decision. Returns the decision dict if APPROVED; raises
    SpendBlocked on BLOCKED and SpendNeedsApproval on FLAGGED."""
    d = evaluate(amount, merchant, category, description, currency)
    decision = d.get("decision")
    if decision == "BLOCKED":
        raise SpendBlocked(d.get("reason", "blocked"), d)
    if decision == "FLAGGED":
        raise SpendNeedsApproval(d.get("reason", "needs approval"), d)
    return d


if __name__ == "__main__":
    # quick self-test against the live firewall
    for amt, mer, cat in [(5, "openai.com", "api"), (350, "aws", "compute"), (6200, "unknown-gpu.ru", "compute")]:
        print(amt, mer, "->", evaluate(amt, mer, cat)["decision"])
