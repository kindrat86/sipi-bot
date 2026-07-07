"""billing.py — API-key-as-product monetization (Stripe Checkout -> webhook -> key).

The API key IS the account. No signup, no password, no dashboard.
This is the Twilio/Stripe model applied to the sipi.bot spend firewall.

Billing is a LAYER flipped on with env vars. With no Stripe config the whole
firewall works normally; /pricing renders with dead buttons.

Env:
  STRIPE_SECRET_KEY      sk_live_... or sk_test_...
  STRIPE_WEBHOOK_SECRET  whsec_...
  STRIPE_PRICE_TEAM      price_...  ($99/mo Team)
  STRIPE_PRICE_BUSINESS  price_...  ($499/mo Business, optional)
  PUBLIC_URL             https://sipi.bot  (for success/cancel URLs)
"""
from __future__ import annotations

import json
import os
import secrets
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional

_LOCK = threading.RLock()
_DB = os.environ.get("BILLING_DB", os.path.join(os.getcwd(), "billing.db"))
_STRIPE_API = "https://api.stripe.com/v1"

TIERS = {
    "team": {"price_id_env": "STRIPE_PRICE_TEAM", "monthly_limit": 0, "label": "Team", "price": "$99/mo"},
    "business": {"price_id_env": "STRIPE_PRICE_BUSINESS", "monthly_limit": 0, "label": "Business", "price": "$499/mo"},
}
# monthly_limit 0 == unlimited evaluations (spend firewall is unlimited by design;
# the value is the outcome/guarantee, not metered call volume).


def is_enabled() -> bool:
    return bool(os.environ.get("STRIPE_SECRET_KEY"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(_DB, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init_db() -> None:
    with _LOCK, _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                key TEXT PRIMARY KEY,
                tier TEXT NOT NULL,
                email TEXT,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                stripe_checkout_session TEXT,
                created_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                usage_count INTEGER NOT NULL DEFAULT 0,
                usage_window_start TEXT,
                last_used_at TEXT
            );
            CREATE TABLE IF NOT EXISTS pending_sessions (
                session_id TEXT PRIMARY KEY,
                plan TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def _stripe_post(path: str, data: dict) -> dict:
    key = os.environ["STRIPE_SECRET_KEY"]
    body = urllib.parse.urlencode(data, doseq=True).encode()
    req = urllib.request.Request(_STRIPE_API + path, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def create_checkout_session(plan: str) -> str:
    """Create a Stripe Checkout Session, return the hosted checkout URL."""
    if not is_enabled():
        raise RuntimeError("billing_disabled: STRIPE_SECRET_KEY not set")
    tier = TIERS.get(plan)
    if not tier:
        raise ValueError(f"unknown plan: {plan}")
    price_id = os.environ.get(tier["price_id_env"])
    if not price_id:
        raise RuntimeError(f"billing_misconfigured: {tier['price_id_env']} not set")
    base = os.environ.get("PUBLIC_URL", "https://sipi.bot").rstrip("/")
    data = {
        "mode": "subscription",
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1,
        "success_url": base + "/keys/{CHECKOUT_SESSION_ID}",
        "cancel_url": base + "/pricing",
        "metadata[plan]": plan,
    }
    session = _stripe_post("/checkout/sessions", data)
    init_db()
    with _LOCK, _conn() as c:
        c.execute("INSERT OR REPLACE INTO pending_sessions (session_id, plan, created_at) VALUES (?,?,?)",
                  (session["id"], plan, _now()))
    return session["url"]


def _issue_key(plan: str, email: Optional[str], customer: Optional[str],
               subscription: Optional[str], checkout_session: Optional[str]) -> str:
    api_key = "sk_live_" + secrets.token_hex(24)
    init_db()
    with _LOCK, _conn() as c:
        c.execute(
            "INSERT INTO api_keys (key, tier, email, stripe_customer_id, stripe_subscription_id, "
            "stripe_checkout_session, created_at, active, usage_count, usage_window_start) "
            "VALUES (?,?,?,?,?,?,?,1,0,?)",
            (api_key, plan, email, customer, subscription, checkout_session, _now(), _now()),
        )
        if checkout_session:
            c.execute("DELETE FROM pending_sessions WHERE session_id=?", (checkout_session,))
    return api_key


def handle_webhook(raw_body: bytes, sig_header: str) -> dict:
    """Process a Stripe webhook. Verifies signature if the SDK is available;
    otherwise trusts the parsed body (set STRIPE_WEBHOOK_SECRET + install stripe
    for production-grade verification)."""
    event = None
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if secret:
        try:
            import stripe  # optional
            event = stripe.Webhook.construct_event(raw_body, sig_header, secret)
        except ImportError:
            event = json.loads(raw_body.decode())
        except Exception as e:
            return {"error": f"signature_verification_failed: {e}"}
    else:
        event = json.loads(raw_body.decode())

    etype = event.get("type")
    obj = event.get("data", {}).get("object", {})

    if etype == "checkout.session.completed":
        cs_id = obj.get("id")
        plan = (obj.get("metadata") or {}).get("plan")
        if not plan:
            with _LOCK, _conn() as c:
                row = c.execute("SELECT plan FROM pending_sessions WHERE session_id=?", (cs_id,)).fetchone()
                plan = row["plan"] if row else "team"
        email = (obj.get("customer_details") or {}).get("email") or obj.get("customer_email")
        api_key = _issue_key(plan, email, obj.get("customer"), obj.get("subscription"), cs_id)
        return {"issued": True, "tier": plan, "key_prefix": api_key[:16]}

    if etype == "customer.subscription.deleted":
        sub = obj.get("id")
        with _LOCK, _conn() as c:
            c.execute("UPDATE api_keys SET active=0 WHERE stripe_subscription_id=?", (sub,))
        return {"deactivated": sub}

    if etype == "customer.subscription.updated":
        sub = obj.get("id")
        status = obj.get("status")
        if status in ("canceled", "unpaid", "incomplete_expired"):
            with _LOCK, _conn() as c:
                c.execute("UPDATE api_keys SET active=0 WHERE stripe_subscription_id=?", (sub,))
            return {"deactivated": sub, "status": status}
        return {"ok": True, "status": status}

    return {"ignored": etype}


def key_for_session(session_id: str) -> Optional[dict[str, Any]]:
    init_db()
    with _LOCK, _conn() as c:
        row = c.execute("SELECT key, tier, email, active FROM api_keys WHERE stripe_checkout_session=?",
                        (session_id,)).fetchone()
        return dict(row) if row else None


def validate_key(api_key: str) -> Optional[dict[str, Any]]:
    init_db()
    with _LOCK, _conn() as c:
        row = c.execute("SELECT * FROM api_keys WHERE key=? AND active=1", (api_key,)).fetchone()
        if not row:
            return None
        c.execute("UPDATE api_keys SET usage_count=usage_count+1, last_used_at=? WHERE key=?",
                  (_now(), api_key))
        return {"tier": row["tier"], "email": row["email"]}


def status() -> dict[str, Any]:
    if not os.path.exists(_DB):
        return {"enabled": is_enabled(), "active_keys": 0, "tiers": list(TIERS)}
    with _LOCK, _conn() as c:
        active = c.execute("SELECT COUNT(*) AS n FROM api_keys WHERE active=1").fetchone()["n"]
    return {"enabled": is_enabled(), "active_keys": int(active), "tiers": list(TIERS)}
