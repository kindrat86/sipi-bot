"""engine.py — THE AGENT (Minimum Useful Agent).

A bounded-action decision agent. Given a proposed transaction from an
autonomous AI agent, it evaluates the transaction against a set of rules and
returns a ternary Decision: APPROVED, BLOCKED, or FLAGGED (needs human review).

Design principles (Isenberg MUA + AgentShield architecture):
- Ternary, not binary. FLAGGED (human-in-the-loop) is the sweet spot that
  binary approve/deny misses.
- Rules evaluated in priority order (highest first).
- First BLOCK wins (definitive, stops evaluation).
- FLAG is non-blocking: keep checking for a BLOCK, but remember we flagged.
- The decision functions are pure w.r.t. their inputs. Historical lookups
  (daily spend, velocity counts) are passed IN as a context dict, so the
  engine itself does zero I/O and is trivially testable.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class Decision(str, Enum):
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    FLAGGED = "FLAGGED"


@dataclass
class Transaction:
    """A proposed spend an autonomous agent wants to make."""
    amount: float
    currency: str = "USD"
    merchant: str = ""
    category: str = ""          # e.g. "compute", "api", "ads", "travel"
    description: str = ""
    agent_id: Optional[str] = None
    timestamp: Optional[str] = None  # ISO8601; defaults to now (UTC)

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        try:
            self.amount = float(self.amount)
        except (TypeError, ValueError):
            self.amount = 0.0


@dataclass
class Rule:
    """A spend policy rule.

    rule_type is one of:
      per_transaction   params: {"max_amount": float}
      daily_total       params: {"max_amount": float}
      velocity          params: {"max_count": int, "window_seconds": int}
      merchant_block    params: {"patterns": ["*.ru", "sketchy*"]}
      merchant_allow    params: {"patterns": ["openai.com", "aws*"]}  (allowlist mode)
      category_limit    params: {"category": "compute", "max_amount": float}
      time_window       params: {"start_hour": 9, "end_hour": 18}  (UTC; outside => action)
      approval_threshold params: {"amount": float}  (>= amount => FLAG for human)

    action is the Decision to apply when the rule TRIPS: BLOCKED or FLAGGED.
    """
    id: str
    rule_type: str
    params: dict[str, Any] = field(default_factory=dict)
    action: Decision = Decision.BLOCKED
    priority: int = 100
    enabled: bool = True
    agent_id: Optional[str] = None  # None == global rule
    label: str = ""


@dataclass
class EvalResult:
    decision: Decision
    reason: str
    rule_id: Optional[str] = None
    triggered: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "rule_id": self.rule_id,
            "triggered": self.triggered,
        }


# --- Individual rule checks. Each returns Decision or None (rule did not trip). ---

def _check_per_transaction(txn: Transaction, rule: Rule, ctx: dict) -> Optional[Decision]:
    cap = float(rule.params.get("max_amount", 0))
    if cap > 0 and txn.amount > cap:
        return rule.action
    return None


def _check_daily_total(txn: Transaction, rule: Rule, ctx: dict) -> Optional[Decision]:
    cap = float(rule.params.get("max_amount", 0))
    spent = float(ctx.get("daily_spend", 0.0))
    if cap > 0 and (spent + txn.amount) > cap:
        return rule.action
    return None


def _check_velocity(txn: Transaction, rule: Rule, ctx: dict) -> Optional[Decision]:
    max_count = int(rule.params.get("max_count", 0))
    recent = int(ctx.get("recent_count", 0))
    # recent = number of txns already recorded inside the window.
    # This proposed txn would be #(recent + 1).
    if max_count > 0 and (recent + 1) > max_count:
        return rule.action
    return None


def _match_any(name: str, patterns: list[str]) -> bool:
    name = (name or "").lower().strip()
    for p in patterns:
        if fnmatch.fnmatch(name, str(p).lower().strip()):
            return True
    return False


def _check_merchant_block(txn: Transaction, rule: Rule, ctx: dict) -> Optional[Decision]:
    patterns = rule.params.get("patterns", [])
    if patterns and _match_any(txn.merchant, patterns):
        return rule.action
    return None


def _check_merchant_allow(txn: Transaction, rule: Rule, ctx: dict) -> Optional[Decision]:
    # Allowlist mode: if merchant is NOT in the allowlist, apply the action.
    patterns = rule.params.get("patterns", [])
    if patterns and not _match_any(txn.merchant, patterns):
        return rule.action
    return None


def _check_category_limit(txn: Transaction, rule: Rule, ctx: dict) -> Optional[Decision]:
    cat = str(rule.params.get("category", "")).lower().strip()
    cap = float(rule.params.get("max_amount", 0))
    if cat and cap > 0 and (txn.category or "").lower().strip() == cat and txn.amount > cap:
        return rule.action
    return None


def _check_time_window(txn: Transaction, rule: Rule, ctx: dict) -> Optional[Decision]:
    # Trips when the txn falls OUTSIDE the allowed [start_hour, end_hour) UTC window.
    start = int(rule.params.get("start_hour", 0))
    end = int(rule.params.get("end_hour", 24))
    try:
        hour = datetime.fromisoformat(txn.timestamp).astimezone(timezone.utc).hour
    except Exception:
        hour = datetime.now(timezone.utc).hour
    inside = start <= hour < end if start <= end else (hour >= start or hour < end)
    if not inside:
        return rule.action
    return None


def _check_approval_threshold(txn: Transaction, rule: Rule, ctx: dict) -> Optional[Decision]:
    amt = float(rule.params.get("amount", 0))
    if amt > 0 and txn.amount >= amt:
        return rule.action  # normally FLAGGED
    return None


_CHECKS = {
    "per_transaction": _check_per_transaction,
    "daily_total": _check_daily_total,
    "velocity": _check_velocity,
    "merchant_block": _check_merchant_block,
    "merchant_allow": _check_merchant_allow,
    "category_limit": _check_category_limit,
    "time_window": _check_time_window,
    "approval_threshold": _check_approval_threshold,
}


def evaluate(txn: Transaction, rules: list[Rule], ctx: Optional[dict] = None) -> EvalResult:
    """Evaluate a transaction against rules.

    ctx supplies historical context the pure engine can't compute itself:
      - daily_spend: float  (already-spent total today, excluding this txn)
      - recent_count: int   (txns already inside the velocity window)

    Priority order: rules sorted by priority DESC. First BLOCK wins.
    FLAG is remembered but non-blocking. If nothing blocks and something
    flagged, result is FLAGGED. Otherwise APPROVED.
    """
    ctx = ctx or {}
    triggered: list[dict[str, Any]] = []
    flagged: Optional[EvalResult] = None

    active = [r for r in rules if r.enabled]
    active.sort(key=lambda r: r.priority, reverse=True)

    for rule in active:
        check = _CHECKS.get(rule.rule_type)
        if not check:
            continue
        outcome = check(txn, rule, ctx)
        if outcome is None:
            continue
        entry = {
            "rule_id": rule.id,
            "rule_type": rule.rule_type,
            "action": outcome.value,
            "label": rule.label,
        }
        triggered.append(entry)
        reason = rule.label or _default_reason(rule, txn)
        if outcome == Decision.BLOCKED:
            return EvalResult(Decision.BLOCKED, reason, rule.id, triggered)
        if outcome == Decision.FLAGGED and flagged is None:
            flagged = EvalResult(Decision.FLAGGED, reason, rule.id, triggered)

    if flagged is not None:
        flagged.triggered = triggered
        return flagged
    return EvalResult(Decision.APPROVED, "Within all spend policies.", None, triggered)


def _default_reason(rule: Rule, txn: Transaction) -> str:
    rt = rule.rule_type
    if rt == "per_transaction":
        return f"Transaction ${txn.amount:,.2f} exceeds per-transaction limit ${float(rule.params.get('max_amount',0)):,.2f}."
    if rt == "daily_total":
        return f"Would exceed daily spend cap of ${float(rule.params.get('max_amount',0)):,.2f}."
    if rt == "velocity":
        return f"Too many transactions in {rule.params.get('window_seconds','?')}s window (max {rule.params.get('max_count','?')})."
    if rt == "merchant_block":
        return f"Merchant '{txn.merchant}' is on the blocklist."
    if rt == "merchant_allow":
        return f"Merchant '{txn.merchant}' is not on the allowlist."
    if rt == "category_limit":
        return f"Category '{txn.category}' spend ${txn.amount:,.2f} exceeds limit."
    if rt == "time_window":
        return f"Transaction outside allowed spend hours ({rule.params.get('start_hour')}:00-{rule.params.get('end_hour')}:00 UTC)."
    if rt == "approval_threshold":
        return f"Transaction ${txn.amount:,.2f} requires human approval (>= ${float(rule.params.get('amount',0)):,.2f})."
    return f"Rule {rule.id} tripped."
