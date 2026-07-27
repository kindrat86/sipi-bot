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

import hashlib
import hmac
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

_POSTHOG_KEY = os.environ.get("POSTHOG_API_KEY", "phc_lyZCgvTpicjLzAO3rY2GhxuX5WUc5jQjP8ZVwwJqauX")


def _capture(event: str, distinct_id: str, properties: Optional[dict] = None) -> None:
    """Server-side PostHog capture for webhook events. Best-effort: never
    raises, never blocks webhook processing. checkout.session.completed and
    subscription cancellations were previously silent here — the only place
    a real purchase/churn signal could be recorded server-side."""
    try:
        props = {"$host": "sipi.bot", "product": "sipi-bot"}
        props.update(properties or {})
        body = json.dumps({
            "api_key": _POSTHOG_KEY,
            "event": event,
            "distinct_id": distinct_id,
            "properties": props,
        }).encode()
        req = urllib.request.Request(
            "https://eu.i.posthog.com/capture/",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass

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


def _stripe_post(path: str, data: dict, api_version: Optional[str] = None) -> dict:
    key = os.environ["STRIPE_SECRET_KEY"]
    body = urllib.parse.urlencode(data, doseq=True).encode()
    req = urllib.request.Request(_STRIPE_API + path, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    if api_version:
        req.add_header("Stripe-Version", api_version)
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
        # Checkout previously inherited the shared Stripe account name
        # "MicroSaaS", breaking trust at the final conversion step. Session-
        # scoped branding keeps this product correctly identified without
        # changing the account-wide identity used by other products.
        "branding_settings[display_name]": "sipi.bot",
        "branding_settings[background_color]": "#0A0A0A",
        "branding_settings[button_color]": "#00D4AA",
        "branding_settings[border_style]": "rounded",
        "branding_settings[font_family]": "inter",
        "branding_settings[icon][type]": "url",
        "branding_settings[icon][url]": base + "/favicon.svg",
        "custom_text[submit][message]": (
            "Your API key is issued immediately after payment. "
            "If sipi.bot approves a spend that violates an active rule, that month is free."
        ),
    }
    # Per-session branding was added in Stripe's 2025-09-30.clover API.
    session = _stripe_post("/checkout/sessions", data, api_version="2025-09-30.clover")
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


_QUARANTINE_FILE = os.environ.get(
    "WEBHOOK_QUARANTINE_FILE",
    os.path.join(os.path.dirname(_DB) or os.getcwd(), "webhook_quarantine.log"),
)


def _quarantine(raw_body: bytes, sig_header: str, reason: str) -> None:
    """Append an unverifiable webhook to a local log. Zero state changes."""
    try:
        entry = {
            "ts": _now(),
            "reason": reason,
            "sig_header": (sig_header or "")[:256],
            "body": raw_body.decode("utf-8", "replace")[:10000],
        }
        with open(_QUARANTINE_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def verify_stripe_signature(raw_body: bytes, sig_header: str, secret: str,
                            tolerance: int = 300) -> bool:
    """Manual Stripe-Signature verification — no SDK required.

    Parses t= and v1= from the header, computes HMAC-SHA256 over
    b"{t}.{raw_payload}" with the webhook secret, compares in constant
    time, and rejects timestamps outside `tolerance` seconds (replay
    protection). Returns False on any parse/shape problem."""
    try:
        ts = None
        v1s = []
        for part in (sig_header or "").split(","):
            k, _, v = part.strip().partition("=")
            if k == "t":
                ts = int(v)
            elif k == "v1":
                v1s.append(v.strip())
        if ts is None or not v1s:
            return False
        if abs(time.time() - ts) > tolerance:
            return False
        expected = hmac.new(secret.encode(), f"{ts}.".encode() + raw_body,
                            hashlib.sha256).hexdigest()
        return any(hmac.compare_digest(expected, v1) for v1 in v1s)
    except Exception:
        return False


def handle_webhook(raw_body: bytes, sig_header: str) -> dict:
    """Process a Stripe webhook. The signature is ALWAYS verified manually
    (pure-Python HMAC-SHA256; the unsigned-body fallbacks are gone).

    Fail-closed behavior:
      * secret set, signature bad/missing -> raise (caller returns 400,
        zero state changes; Stripe retries genuine events)
      * STRIPE_WEBHOOK_SECRET not configured -> QUARANTINE the event to a
        local log, make zero state changes, return 200 so Stripe does not
        retry-storm. The operator must set the secret to resume processing.
    """
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        _quarantine(raw_body, sig_header, "webhook_secret_not_configured")
        return {"quarantined": True, "reason": "webhook_secret_not_configured"}
    if not verify_stripe_signature(raw_body, sig_header, secret):
        raise ValueError("signature_verification_failed")
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
        distinct_id = (obj.get("client_reference_id") or f"stripe:{obj.get('customer')}" or "anonymous")
        _capture("subscription_started", distinct_id, {
            "tier": plan,
            "stripe_customer_id": obj.get("customer"),
            "stripe_checkout_session": cs_id,
            "amount_total": obj.get("amount_total"),
            "currency": obj.get("currency"),
        })
        return {"issued": True, "tier": plan, "key_prefix": api_key[:16]}

    if etype == "customer.subscription.deleted":
        sub = obj.get("id")
        with _LOCK, _conn() as c:
            c.execute("UPDATE api_keys SET active=0 WHERE stripe_subscription_id=?", (sub,))
        _capture("subscription_canceled", f"stripe:{obj.get('customer')}", {
            "stripe_subscription_id": sub,
        })
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
