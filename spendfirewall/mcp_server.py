"""mcp_server.py — MCP surface for agentic IDEs (Claude Code / Cursor / Hermes).

The docstring on each tool is the agent's ONLY spec — written so the agent
knows exactly when to call it. Install: pip install mcp. Run: python -m spendfirewall.mcp_server
"""
from __future__ import annotations

import json

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover
    raise SystemExit("MCP not installed. Run: pip install mcp")

from . import core

mcp = FastMCP("sipi-bot-spend-firewall")


@mcp.tool()
def evaluate_spend(amount: float, merchant: str = "", category: str = "",
                   description: str = "") -> str:
    """Check whether you (an autonomous agent) are allowed to make a purchase
    BEFORE you spend the money. Call this every time you are about to pay for
    anything: compute, API credits, ads, subscriptions, goods. Returns JSON with
    a `decision` of APPROVED (go ahead), BLOCKED (do NOT spend — explain why to
    the user), or FLAGGED (a human must approve first — do not proceed yet).
    Always respect a BLOCKED or FLAGGED decision."""
    return json.dumps(core.evaluate_transaction(
        amount=amount, merchant=merchant, category=category, description=description))


@mcp.tool()
def register_agent(name: str) -> str:
    """Register a new agent identity and get an API key to authenticate future
    spend evaluations. Call once per agent, then reuse the returned api_key."""
    return json.dumps(core.register_agent(name))


@mcp.tool()
def add_spend_rule(rule_type: str, params: str, action: str = "BLOCKED",
                   label: str = "") -> str:
    """Add a spend policy rule. rule_type is one of: per_transaction, daily_total,
    velocity, merchant_block, merchant_allow, category_limit, approval_threshold.
    params is a JSON string, e.g. '{"max_amount": 500}'. action is BLOCKED or
    FLAGGED. Use FLAGGED to require human approval instead of hard blocking."""
    try:
        p = json.loads(params) if isinstance(params, str) else params
    except Exception:
        return json.dumps({"error": "params must be valid JSON"})
    return json.dumps(core.add_rule(rule_type, p, action, label=label))


@mcp.tool()
def firewall_status() -> str:
    """Get current firewall stats: spend approved/blocked today, pending
    approvals, active agents. Use to report the spend posture to the user."""
    return json.dumps(core.status())


if __name__ == "__main__":
    mcp.run()
