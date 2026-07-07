"""store.py — SQLite persistence + trust layer.

Tables:
  agents        (id, name, api_key, status, created_at)
  transactions  (id, agent_id, amount, currency, merchant, category,
                 description, decision, reason, rule_id, created_at)
  rules         (id, agent_id NULL=global, rule_type, params JSON,
                 action, priority, enabled, label, created_at)
  approvals     (id, txn_id, agent_id, status, created_at, resolved_at)

Thread-safe via a module-level lock (http.server is threaded). WAL mode.
"""
from __future__ import annotations

import json
import os
import secrets
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from .engine import Decision, Rule

_LOCK = threading.RLock()
_DB_PATH = os.environ.get("SPENDFIREWALL_DB", os.path.join(os.getcwd(), "spendfirewall.db"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(_DB_PATH, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


def init_db() -> None:
    with _LOCK, _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                merchant TEXT DEFAULT '',
                category TEXT DEFAULT '',
                description TEXT DEFAULT '',
                decision TEXT NOT NULL,
                reason TEXT DEFAULT '',
                rule_id TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS rules (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                rule_type TEXT NOT NULL,
                params TEXT NOT NULL DEFAULT '{}',
                action TEXT NOT NULL DEFAULT 'BLOCKED',
                priority INTEGER NOT NULL DEFAULT 100,
                enabled INTEGER NOT NULL DEFAULT 1,
                label TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                txn_id TEXT NOT NULL,
                agent_id TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                resolved_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_txn_agent ON transactions(agent_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_rules_agent ON rules(agent_id);
            CREATE INDEX IF NOT EXISTS idx_appr_status ON approvals(status);
            """
        )
    seed_default_rules()


# --- Agents ---

def create_agent(name: str) -> dict[str, Any]:
    aid = "agt_" + uuid.uuid4().hex[:12]
    key = "sk_live_" + secrets.token_urlsafe(24)
    with _LOCK, _conn() as c:
        c.execute(
            "INSERT INTO agents (id, name, api_key, status, created_at) VALUES (?,?,?,?,?)",
            (aid, name, key, "active", _now()),
        )
    return {"id": aid, "name": name, "api_key": key, "status": "active"}


def get_agent_by_key(api_key: str) -> Optional[dict[str, Any]]:
    with _LOCK, _conn() as c:
        row = c.execute("SELECT * FROM agents WHERE api_key=? AND status='active'", (api_key,)).fetchone()
        return dict(row) if row else None


def list_agents() -> list[dict[str, Any]]:
    with _LOCK, _conn() as c:
        rows = c.execute("SELECT id, name, status, created_at FROM agents ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


# --- Rules ---

def add_rule(rule_type: str, params: dict, action: str = "BLOCKED",
             priority: int = 100, label: str = "", agent_id: Optional[str] = None,
             enabled: bool = True) -> dict[str, Any]:
    rid = "rul_" + uuid.uuid4().hex[:10]
    with _LOCK, _conn() as c:
        c.execute(
            "INSERT INTO rules (id, agent_id, rule_type, params, action, priority, enabled, label, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (rid, agent_id, rule_type, json.dumps(params), action, priority,
             1 if enabled else 0, label, _now()),
        )
    return {"id": rid, "rule_type": rule_type, "params": params, "action": action,
            "priority": priority, "label": label, "agent_id": agent_id, "enabled": enabled}


def delete_rule(rule_id: str) -> bool:
    with _LOCK, _conn() as c:
        cur = c.execute("DELETE FROM rules WHERE id=?", (rule_id,))
        return cur.rowcount > 0


def get_rules_for_agent(agent_id: Optional[str]) -> list[Rule]:
    with _LOCK, _conn() as c:
        rows = c.execute(
            "SELECT * FROM rules WHERE enabled=1 AND (agent_id IS NULL OR agent_id=?)",
            (agent_id,),
        ).fetchall()
    out: list[Rule] = []
    for r in rows:
        out.append(Rule(
            id=r["id"],
            rule_type=r["rule_type"],
            params=json.loads(r["params"] or "{}"),
            action=Decision(r["action"]),
            priority=r["priority"],
            enabled=bool(r["enabled"]),
            agent_id=r["agent_id"],
            label=r["label"] or "",
        ))
    return out


def list_rules() -> list[dict[str, Any]]:
    with _LOCK, _conn() as c:
        rows = c.execute("SELECT * FROM rules ORDER BY priority DESC, created_at").fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["params"] = json.loads(d["params"] or "{}")
        d["enabled"] = bool(d["enabled"])
        out.append(d)
    return out


def seed_default_rules() -> None:
    """Give the product a working day-one policy without manual config."""
    with _LOCK, _conn() as c:
        n = c.execute("SELECT COUNT(*) AS n FROM rules WHERE agent_id IS NULL").fetchone()["n"]
    if n > 0:
        return
    add_rule("per_transaction", {"max_amount": 500}, "BLOCKED", 100,
             "Block any single transaction over $500")
    add_rule("daily_total", {"max_amount": 2000}, "BLOCKED", 90,
             "Block once daily spend would exceed $2,000")
    add_rule("velocity", {"max_count": 10, "window_seconds": 3600}, "BLOCKED", 80,
             "Block more than 10 transactions per hour (runaway protection)")
    add_rule("approval_threshold", {"amount": 200}, "FLAGGED", 50,
             "Flag transactions of $200+ for human approval")


# --- Transactions + context ---

def get_daily_spend(agent_id: Optional[str]) -> float:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    with _LOCK, _conn() as c:
        row = c.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM transactions "
            "WHERE decision='APPROVED' AND created_at>=? AND (agent_id=? OR (? IS NULL AND agent_id IS NULL))",
            (start, agent_id, agent_id),
        ).fetchone()
        return float(row["s"] or 0.0)


def count_recent_transactions(agent_id: Optional[str], window_seconds: int) -> int:
    since = (datetime.now(timezone.utc) - timedelta(seconds=window_seconds)).isoformat()
    with _LOCK, _conn() as c:
        row = c.execute(
            "SELECT COUNT(*) AS n FROM transactions "
            "WHERE created_at>=? AND decision IN ('APPROVED','FLAGGED') "
            "AND (agent_id=? OR (? IS NULL AND agent_id IS NULL))",
            (since, agent_id, agent_id),
        ).fetchone()
        return int(row["n"] or 0)


def record_transaction(txn, result) -> str:
    tid = "txn_" + uuid.uuid4().hex[:12]
    with _LOCK, _conn() as c:
        c.execute(
            "INSERT INTO transactions (id, agent_id, amount, currency, merchant, category, "
            "description, decision, reason, rule_id, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (tid, txn.agent_id, txn.amount, txn.currency, txn.merchant, txn.category,
             txn.description, result.decision.value, result.reason, result.rule_id, _now()),
        )
        if result.decision.value == "FLAGGED":
            aid = "apr_" + uuid.uuid4().hex[:10]
            c.execute(
                "INSERT INTO approvals (id, txn_id, agent_id, status, created_at) VALUES (?,?,?,?,?)",
                (aid, tid, txn.agent_id, "pending", _now()),
            )
    return tid


# --- Approvals ---

def list_approvals(status: str = "pending") -> list[dict[str, Any]]:
    with _LOCK, _conn() as c:
        rows = c.execute(
            "SELECT a.*, t.amount, t.merchant, t.category, t.description, t.reason "
            "FROM approvals a LEFT JOIN transactions t ON a.txn_id=t.id "
            "WHERE a.status=? ORDER BY a.created_at DESC",
            (status,),
        ).fetchall()
        return [dict(r) for r in rows]


def resolve_approval(approval_id: str, decision: str) -> bool:
    new_status = "approved" if decision.lower() in ("approve", "approved") else "denied"
    with _LOCK, _conn() as c:
        cur = c.execute(
            "UPDATE approvals SET status=?, resolved_at=? WHERE id=? AND status='pending'",
            (new_status, _now(), approval_id),
        )
        return cur.rowcount > 0


# --- Dashboard stats ---

def get_stats() -> dict[str, Any]:
    day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    with _LOCK, _conn() as c:
        approved_24h = c.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM transactions WHERE decision='APPROVED' AND created_at>=?",
            (day_start,)).fetchone()["s"]
        blocked_val = c.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM transactions WHERE decision='BLOCKED' AND created_at>=?",
            (day_start,)).fetchone()["s"]
        pending = c.execute("SELECT COUNT(*) AS n FROM approvals WHERE status='pending'").fetchone()["n"]
        agents = c.execute("SELECT COUNT(*) AS n FROM agents WHERE status='active'").fetchone()["n"]
        total_txns = c.execute("SELECT COUNT(*) AS n FROM transactions").fetchone()["n"]
        by_dec = {r["decision"]: r["n"] for r in c.execute(
            "SELECT decision, COUNT(*) AS n FROM transactions GROUP BY decision").fetchall()}
    return {
        "approved_24h": round(float(approved_24h or 0), 2),
        "blocked_value_24h": round(float(blocked_val or 0), 2),
        "pending_approvals": int(pending),
        "active_agents": int(agents),
        "total_transactions": int(total_txns),
        "by_decision": by_dec,
    }


def recent_transactions(limit: int = 50) -> list[dict[str, Any]]:
    with _LOCK, _conn() as c:
        rows = c.execute(
            "SELECT id, agent_id, amount, currency, merchant, category, decision, reason, created_at "
            "FROM transactions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def reset_demo_data() -> int:
    """Clear transaction + approval history (keeps rules and agents).
    Returns number of transactions cleared. For resetting the public demo."""
    with _LOCK, _conn() as c:
        n = c.execute("SELECT COUNT(*) AS n FROM transactions").fetchone()["n"]
        c.execute("DELETE FROM transactions")
        c.execute("DELETE FROM approvals")
    return int(n)
