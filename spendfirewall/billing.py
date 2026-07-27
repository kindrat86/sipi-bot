"""billing.py — API-key-as-product monetization (Stripe Checkout -> webhook -> key).

The API key IS the account. No signup or password; the same key opens an
isolated dashboard workspace.
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
import re
import secrets
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

_LOCK = threading.RLock()
_DB = os.environ.get("BILLING_DB", os.path.join(os.getcwd(), "billing.db"))
_STRIPE_API = "https://api.stripe.com/v1"

_POSTHOG_KEY = os.environ.get("POSTHOG_API_KEY", "phc_lyZCgvTpicjLzAO3rY2GhxuX5WUc5jQjP8ZVwwJqauX")
_ANALYTICS_ID_RE = re.compile(r"^[A-Za-z0-9._:@-]{1,128}$")


def _capture(
    event: str,
    distinct_id: Optional[str],
    properties: Optional[dict] = None,
) -> None:
    """Server-side PostHog capture for webhook events. Best-effort: never
    raises, never blocks webhook processing. checkout.session.completed and
    subscription cancellations were previously silent here — the only place
    a real purchase/churn signal could be recorded server-side."""
    if not distinct_id:
        return
    try:
        props = {
            "$host": "sipi.bot",
            "$process_person_profile": False,
            "product": "sipi-bot",
            "schema_version": 1,
        }
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


def _safe_analytics_id(value: Optional[str] = None) -> Optional[str]:
    """Return a consented bounded analytics id; never synthesize tracking."""
    candidate = (value or "").strip()
    if candidate and _ANALYTICS_ID_RE.fullmatch(candidate):
        return candidate
    return None


def _key_agent_id(api_key: str) -> str:
    """Stable pseudonymous agent id for a paid key without exposing the key."""
    return "billing_" + hashlib.sha256(api_key.encode()).hexdigest()[:24]


def _activation_bucket(created_at: Optional[str]) -> str:
    try:
        created = datetime.fromisoformat(created_at or "")
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        hours = max(0.0, (datetime.now(timezone.utc) - created).total_seconds() / 3600)
    except (TypeError, ValueError):
        return "unknown"
    if hours < 1:
        return "under_1h"
    if hours < 24:
        return "1h_to_24h"
    if hours < 72:
        return "1d_to_3d"
    if hours < 168:
        return "3d_to_7d"
    return "over_7d"

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
                last_used_at TEXT,
                analytics_id TEXT,
                activated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS pending_sessions (
                session_id TEXT PRIMARY KEY,
                plan TEXT NOT NULL,
                created_at TEXT NOT NULL,
                analytics_id TEXT,
                source_cta TEXT
            );
            CREATE TABLE IF NOT EXISTS processed_webhook_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT,
                processed_at TEXT NOT NULL
            );
            """
        )
        # Existing installs predate the attribution/activation columns. Keep the
        # migration additive so a running deployment can upgrade in place.
        api_columns = {row["name"] for row in c.execute("PRAGMA table_info(api_keys)")}
        if "analytics_id" not in api_columns:
            c.execute("ALTER TABLE api_keys ADD COLUMN analytics_id TEXT")
        if "activated_at" not in api_columns:
            c.execute("ALTER TABLE api_keys ADD COLUMN activated_at TEXT")
        pending_columns = {
            row["name"] for row in c.execute("PRAGMA table_info(pending_sessions)")
        }
        if "analytics_id" not in pending_columns:
            c.execute("ALTER TABLE pending_sessions ADD COLUMN analytics_id TEXT")
        if "source_cta" not in pending_columns:
            c.execute("ALTER TABLE pending_sessions ADD COLUMN source_cta TEXT")
        # New databases enforce one key per checkout. Older databases with
        # historical duplicates still retain the transactional lookup guard.
        try:
            c.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_api_keys_checkout_session "
                "ON api_keys(stripe_checkout_session) "
                "WHERE stripe_checkout_session IS NOT NULL"
            )
        except sqlite3.IntegrityError:
            pass
        # Abandoned Checkout sessions and old webhook replay markers otherwise
        # grow forever. These windows are well beyond Stripe's retry period.
        c.execute(
            "DELETE FROM pending_sessions WHERE created_at<?",
            ((datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),),
        )
        c.execute(
            "DELETE FROM processed_webhook_events WHERE processed_at<?",
            ((datetime.now(timezone.utc) - timedelta(days=365)).isoformat(),),
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


def create_checkout_session(
    plan: str,
    analytics_id: Optional[str] = None,
    source_cta: Optional[str] = None,
) -> str:
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
    analytics_id = _safe_analytics_id(analytics_id)
    source_cta = (source_cta or "direct").strip()[:64]
    data = {
        "mode": "subscription",
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1,
        "success_url": base + "/keys/{CHECKOUT_SESSION_ID}",
        "cancel_url": base + "/pricing?checkout=cancelled&plan=" + plan,
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
    if analytics_id:
        data["client_reference_id"] = analytics_id
    # Per-session branding was added in Stripe's 2025-09-30.clover API.
    session = _stripe_post("/checkout/sessions", data, api_version="2025-09-30.clover")
    init_db()
    with _LOCK, _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO pending_sessions "
            "(session_id, plan, created_at, analytics_id, source_cta) "
            "VALUES (?,?,?,?,?)",
            (session["id"], plan, _now(), analytics_id, source_cta),
        )
    _capture(
        "checkout_started",
        analytics_id,
        {"plan": plan, "source_cta": source_cta},
    )
    return session["url"]


def _issue_key(
    plan: str,
    email: Optional[str],
    customer: Optional[str],
    subscription: Optional[str],
    checkout_session: Optional[str],
    analytics_id: Optional[str],
) -> tuple[str, bool]:
    init_db()
    with _LOCK, _conn() as c:
        if checkout_session:
            existing = c.execute(
                "SELECT key FROM api_keys WHERE stripe_checkout_session=?",
                (checkout_session,),
            ).fetchone()
            if existing:
                return existing["key"], False
        api_key = "sk_live_" + secrets.token_hex(24)
        c.execute(
            "INSERT INTO api_keys (key, tier, email, stripe_customer_id, stripe_subscription_id, "
            "stripe_checkout_session, created_at, active, usage_count, usage_window_start, "
            "analytics_id) VALUES (?,?,?,?,?,?,?,1,0,?,?)",
            (
                api_key,
                plan,
                email,
                customer,
                subscription,
                checkout_session,
                _now(),
                _now(),
                _safe_analytics_id(analytics_id),
            ),
        )
        if checkout_session:
            c.execute("DELETE FROM pending_sessions WHERE session_id=?", (checkout_session,))
    return api_key, True


_QUARANTINE_FILE = os.environ.get(
    "WEBHOOK_QUARANTINE_FILE",
    os.path.join(os.path.dirname(_DB) or os.getcwd(), "webhook_quarantine.log"),
)


def _quarantine(raw_body: bytes, sig_header: str, reason: str) -> None:
    """Record a privacy-safe fingerprint for an unverifiable webhook."""
    try:
        entry = {
            "ts": _now(),
            "reason": reason,
            "signature_present": bool(sig_header),
            "body_bytes": len(raw_body),
            "body_sha256": hashlib.sha256(raw_body).hexdigest(),
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

    event_id = (event.get("id") or "").strip()
    etype = event.get("type")
    obj = event.get("data", {}).get("object", {})
    if event_id:
        init_db()
        with _LOCK, _conn() as c:
            seen = c.execute(
                "SELECT 1 FROM processed_webhook_events WHERE event_id=?",
                (event_id,),
            ).fetchone()
            if seen:
                return {"duplicate": True, "event": etype}

    if etype == "checkout.session.completed":
        cs_id = obj.get("id")
        plan = (obj.get("metadata") or {}).get("plan")
        analytics_id = _safe_analytics_id(obj.get("client_reference_id"))
        source_cta = "direct"
        if not plan:
            with _LOCK, _conn() as c:
                row = c.execute(
                    "SELECT plan, analytics_id, source_cta FROM pending_sessions "
                    "WHERE session_id=?",
                    (cs_id,),
                ).fetchone()
                plan = row["plan"] if row else "team"
                if row:
                    analytics_id = _safe_analytics_id(row["analytics_id"])
                    source_cta = row["source_cta"] or source_cta
        else:
            with _LOCK, _conn() as c:
                row = c.execute(
                    "SELECT analytics_id, source_cta FROM pending_sessions "
                    "WHERE session_id=?",
                    (cs_id,),
                ).fetchone()
                if row:
                    analytics_id = _safe_analytics_id(
                        obj.get("client_reference_id") or row["analytics_id"]
                    )
                    source_cta = row["source_cta"] or source_cta
        email = (obj.get("customer_details") or {}).get("email") or obj.get("customer_email")
        api_key, created = _issue_key(
            plan,
            email,
            obj.get("customer"),
            obj.get("subscription"),
            cs_id,
            analytics_id,
        )
        if created:
            safe_revenue = {
                "plan": plan,
                "amount_total": obj.get("amount_total"),
                "currency": obj.get("currency"),
                "source_cta": source_cta,
            }
            _capture("checkout_completed", analytics_id, safe_revenue)
            _capture(
                "api_key_issued",
                analytics_id,
                {"plan": plan, "source_cta": source_cta},
            )
        if event_id:
            with _LOCK, _conn() as c:
                c.execute(
                    "INSERT OR IGNORE INTO processed_webhook_events "
                    "(event_id, event_type, processed_at) VALUES (?,?,?)",
                    (event_id, etype, _now()),
                )
        return {"issued": created, "tier": plan}

    if etype == "customer.subscription.deleted":
        sub = obj.get("id")
        with _LOCK, _conn() as c:
            key_row = c.execute(
                "SELECT analytics_id, tier FROM api_keys "
                "WHERE stripe_subscription_id=? LIMIT 1",
                (sub,),
            ).fetchone()
            c.execute("UPDATE api_keys SET active=0 WHERE stripe_subscription_id=?", (sub,))
        _capture(
            "subscription_canceled",
            _safe_analytics_id(key_row["analytics_id"] if key_row else None),
            {
                "plan": (
                    key_row["tier"]
                    if key_row
                    else (obj.get("metadata") or {}).get("plan")
                ),
            },
        )
        if event_id:
            with _LOCK, _conn() as c:
                c.execute(
                    "INSERT OR IGNORE INTO processed_webhook_events "
                    "(event_id, event_type, processed_at) VALUES (?,?,?)",
                    (event_id, etype, _now()),
                )
        return {"deactivated": sub}

    if etype == "customer.subscription.updated":
        sub = obj.get("id")
        status = obj.get("status")
        if status in ("canceled", "unpaid", "incomplete_expired"):
            with _LOCK, _conn() as c:
                c.execute("UPDATE api_keys SET active=0 WHERE stripe_subscription_id=?", (sub,))
                if event_id:
                    c.execute(
                        "INSERT OR IGNORE INTO processed_webhook_events "
                        "(event_id, event_type, processed_at) VALUES (?,?,?)",
                        (event_id, etype, _now()),
                    )
            return {"deactivated": sub, "status": status}
        if event_id:
            with _LOCK, _conn() as c:
                c.execute(
                    "INSERT OR IGNORE INTO processed_webhook_events "
                    "(event_id, event_type, processed_at) VALUES (?,?,?)",
                    (event_id, etype, _now()),
                )
        return {"ok": True, "status": status}

    return {"ignored": etype}


def key_for_session(session_id: str) -> Optional[dict[str, Any]]:
    init_db()
    with _LOCK, _conn() as c:
        row = c.execute(
            "SELECT key, tier, active, analytics_id FROM api_keys "
            "WHERE stripe_checkout_session=?",
            (session_id,),
        ).fetchone()
        return dict(row) if row else None


def validate_key(api_key: str) -> Optional[dict[str, Any]]:
    """Validate a paid API key without recording usage.

    Recording is intentionally separate so malformed transactions cannot count
    as activation.
    """
    init_db()
    with _LOCK, _conn() as c:
        row = c.execute(
            "SELECT tier, analytics_id, created_at, activated_at "
            "FROM api_keys WHERE key=? AND active=1",
            (api_key,),
        ).fetchone()
        if not row:
            return None
        return {
            "tier": row["tier"],
            "analytics_id": row["analytics_id"],
            "agent_id": _key_agent_id(api_key),
            "created_at": row["created_at"],
            "activated": bool(row["activated_at"]),
        }


def record_key_use(api_key: str, decision: str) -> bool:
    """Record one successful paid-key evaluation and capture first activation."""
    init_db()
    now = _now()
    with _LOCK, _conn() as c:
        row = c.execute(
            "SELECT tier, analytics_id, created_at, activated_at "
            "FROM api_keys WHERE key=? AND active=1",
            (api_key,),
        ).fetchone()
        if not row:
            return False
        first_use = not bool(row["activated_at"])
        c.execute(
            "UPDATE api_keys SET usage_count=usage_count+1, last_used_at=?, "
            "activated_at=COALESCE(activated_at, ?) WHERE key=?",
            (now, now, api_key),
        )
    if first_use:
        _capture(
            "activation_completed",
            _safe_analytics_id(row["analytics_id"]),
            {
                "plan": row["tier"],
                "decision": decision,
                "hours_to_activation_bucket": _activation_bucket(row["created_at"]),
            },
        )
    return first_use


def capture_key_delivery(rec: Optional[dict[str, Any]]) -> None:
    """Track the success state server-side without exposing its capability URL."""
    if not rec:
        return
    _capture(
        "key_delivery_viewed",
        _safe_analytics_id(rec.get("analytics_id")),
        {"plan": rec.get("tier", "team")},
    )


def capture_checkout_failure(
    plan: str,
    failure_type: str,
    analytics_id: Optional[str] = None,
) -> None:
    _capture(
        "checkout_failed",
        _safe_analytics_id(analytics_id),
        {"plan": plan, "failure_type": failure_type[:64]},
    )


def status() -> dict[str, Any]:
    """Public capability status; never disclose customer/account counts."""
    return {"enabled": is_enabled(), "tiers": list(TIERS)}
