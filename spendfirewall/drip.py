"""drip.py — Soap Opera + Seinfeld email follow-up engine for sipi.bot.

Brunson Traffic Secrets Secret #6 (Follow-Up Funnels):
  - 5-day Soap Opera Sequence for new subscribers (emotion -> logic -> fear)
  - 30-day Seinfeld content retained for review (not activated)
  - Hourly daemon thread fires day-appropriate emails
  - Manual trigger via /cron/drip?secret=...

Mirrors the proven pattern in sanctionsai (~/workspace/agentmail/api.py).
Requires DRIP_ENABLED=true plus RESEND_API_KEY + EMAIL_FROM env vars.
If those are absent, the module is a no-op (subscribers still appended to
SUBS_FILE by api.py /subscribe handler) so the app never crashes.
"""
from __future__ import annotations

from contextlib import closing
import hashlib
import json
import os
import sqlite3
import time
import threading
import urllib.parse
import urllib.request
import urllib.error

_EMAIL_FROM = os.environ.get(
    "EMAIL_FROM", "sipi.bot <noreply@mail.sipi.bot>"
)
_PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://sipi.bot").rstrip("/")
_DAY_SECONDS = 24 * 60 * 60
_RUN_LOCK = threading.Lock()


class ResendError(RuntimeError):
    """A sanitized transport error with retry/batch-control metadata."""

    def __init__(
        self,
        category: str,
        status_code: int | None = None,
        *,
        stop_batch: bool = False,
        retry_after: str | None = None,
    ):
        super().__init__(f"Resend {category} error")
        self.category = category
        self.status_code = status_code
        self.stop_batch = stop_batch
        self.retry_after = retry_after


def _drip_enabled() -> bool:
    """Fail closed: delivery must be explicitly enabled."""
    return os.environ.get("DRIP_ENABLED", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def _resend_api_key() -> str:
    return os.environ.get("RESEND_API_KEY", "").strip()


# ─── Resend transport (stdlib urllib — sipi.bot is stdlib-only by design) ─
def _send_resend(
    to_email: str,
    subject: str,
    html_body: str,
    idempotency_key: str,
) -> dict:
    """Send email via Resend API with unsubscribe link injection.

    Uses stdlib urllib so sipi.bot stays dependency-free (no requests).
    """
    api_key = _resend_api_key()
    if not api_key:
        raise ResendError("configuration", stop_batch=True)
    unsub_url = (
        f"{_PUBLIC_URL}/unsubscribe?"
        + urllib.parse.urlencode({"email": to_email})
    )
    unsub_link = (
        f'<a href="{unsub_url}" style="color:#555;text-decoration:underline;font-size:11px">'
        "Unsubscribe</a>"
    )
    html_body = html_body.replace("UNSUBSCRIBE_LINK", unsub_link)
    payload = json.dumps(
        {"from": _EMAIL_FROM, "to": [to_email], "subject": subject, "html": html_body}
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        # Explicit User-Agent: Cloudflare (fronting Resend's API) 403s
        # urllib's default UA with a plaintext "error code: 1010" body,
        # before Resend itself ever sees the request. Same root cause
        # already found and fixed in sanctionsai's api.py (2026-07-24).
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "sipi-bot-drip/1.0 (+curl-compatible)",
            "Idempotency-Key": idempotency_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", "ignore")
            try:
                provider_id = json.loads(body).get("id")
            except (TypeError, ValueError):
                # A 2xx means Resend accepted the message. Treat a malformed
                # response body as success so it cannot cause a duplicate.
                provider_id = None
            return {"ok": True, "id": provider_id}
    except urllib.error.HTTPError as e:
        retry_after = e.headers.get("Retry-After") if e.headers else None
        if e.code in (401, 403):
            raise ResendError(
                "authentication", e.code, stop_batch=True
            ) from None
        if e.code == 429:
            raise ResendError(
                "rate_limit", e.code, stop_batch=True,
                retry_after=retry_after,
            ) from None
        if e.code >= 500:
            raise ResendError(
                "server", e.code, stop_batch=True
            ) from None
        raise ResendError("recipient", e.code) from None
    except urllib.error.URLError as e:
        raise ResendError("network", stop_batch=True) from None


# ─── Branded email wrapper ───────────────────────────────────────────
def _build_branded_email(subject: str, content_html: str, day_info: str = "") -> str:
    html = "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>sipi.bot</title></head>"
    html += "<body style='margin:0;padding:0;background-color:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif'>"
    html += "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='background-color:#0a0a0a'><tr><td align='center' style='padding:40px 16px'>"
    html += "<table role='presentation' width='100%' style='max-width:560px;background-color:#111;border-radius:16px;overflow:hidden;border:1px solid #1a1a1a'>"
    # header
    html += "<tr><td style='background:linear-gradient(135deg,#0a0a0a,#0d1f1a);border-bottom:1px solid #1a1a1a;text-align:center;padding:32px 32px 20px'>"
    html += "<h1 style='margin:0;font-size:22px;font-weight:800;color:#fff;letter-spacing:-0.5px'>sipi<span style='color:#00d4aa'>.bot</span></h1>"
    html += "<p style='margin:4px 0 0;font-size:10px;color:#555;letter-spacing:1px;text-transform:uppercase'>THE SPEND FIREWALL FOR AI AGENTS</p>"
    html += "</td></tr>"
    # body
    html += "<tr><td style='padding:32px 32px 0'>"
    html += content_html
    html += "</td></tr>"
    # footer
    html += "<tr><td style='padding:0'><table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='border-top:1px solid #1a1a1a;background:#0a0a0a'><tr><td style='padding:20px 32px;text-align:center'>"
    html += "<p style='margin:0 0 8px;font-size:10px;color:#555;line-height:1.6'>"
    html += "sipi.bot &mdash; the pre-spend firewall for autonomous AI agents<br>"
    html += f"<a href='{_PUBLIC_URL}' style='color:#00d4aa;text-decoration:none'>sipi.bot</a>"
    html += " &nbsp;&middot;&nbsp; <a href='https://github.com/kindrat86/sipi-bot' style='color:#555;text-decoration:none'>GitHub</a>"
    html += f" &nbsp;&middot;&nbsp; <a href='{_PUBLIC_URL}/pricing' style='color:#555;text-decoration:none'>Pricing</a>"
    html += "</p>"
    html += "UNSUBSCRIBE_LINK"
    if day_info:
        html += f"<p style='margin:6px 0 0;font-size:9px;color:#333'>{day_info}</p>"
    html += "</td></tr></table></td></tr></table>"
    html += "<p style='margin:12px 0 0;font-size:9px;color:#333;text-align:center'>sipi.bot &mdash; the spend firewall for autonomous AI agents</p>"
    html += "</td></tr></table></body></html>"
    return html


# ─── Soap Opera: 5-day sequence (emotion -> logic -> fear) ──────────
_SOAP_SUBJECTS = [
    "The night my agent spent $12,400 while I slept",
    "The 6 rules that would have stopped it",
    "Wire it into your agent before tonight",
    "The eval suite: 53 scenarios, 53/53 passed",
    "The deployment checklist (and why this matters now)",
]

_SOAP_CONTENT = []

# Day 1 — the wound (emotion)
_SOAP_CONTENT.append("""
<div style='text-align:center;margin-bottom:24px'>
<span style='display:inline-block;background:rgba(0,212,170,0.1);color:#00d4aa;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:0.5px'>DAY 1 OF 5</span>
</div>
<h2 style='margin:0 0 16px;font-size:18px;font-weight:700;color:#fff;line-height:1.3'>2:14 AM. My phone buzzed. Stripe receipt.</h2>
<p style='margin:0 0 16px;font-size:14px;color:#999;line-height:1.6'>My agent had hit a rate limit and retried the purchase <strong style='color:#fff'>40 times</strong>. By 2:31 AM it had tipped an API into an overage tier. I woke up at 9:03 AM to <strong style='color:#ff6b6b'>$12,400 gone</strong>.</p>
<div style='background:#120808;border:1px solid #2a1414;border-radius:10px;padding:16px;margin-bottom:20px'>
<p style='margin:0 0 4px;font-size:13px;font-weight:600;color:#ff6b6b'>The part that stung</p>
<p style='margin:0;font-size:12px;color:#888;line-height:1.5'>None of those transactions were malicious. The agent was doing exactly what I told it. It just had no ceiling. I gave it a credit card with no spending limit. That is on me.</p>
</div>
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>Tomorrow I'll show you the six rules that would have stopped every one of those charges with a deterministic rules check. For now, just know: if you have an autonomous agent holding a payment method, this will happen to you. The only question is when.</p>
<p style='margin:0;font-size:13px;color:#555;line-height:1.6'>— Maryan, founder, sipi.bot</p>
""")

# Day 2 — the rules (logic)
_SOAP_CONTENT.append("""
<div style='text-align:center;margin-bottom:24px'>
<span style='display:inline-block;background:rgba(0,212,170,0.1);color:#00d4aa;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:0.5px'>DAY 2 OF 5</span>
</div>
<h2 style='margin:0 0 16px;font-size:18px;font-weight:700;color:#fff;line-height:1.3'>Six rules. Every transaction. Before money moves.</h2>
<p style='margin:0 0 16px;font-size:14px;color:#999;line-height:1.6'>Here's what would have stopped the $12,400 night:</p>
<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='background:#0d1f1a;border:1px solid rgba(0,212,170,0.08);border-radius:10px;margin-bottom:20px'><tr><td style='padding:16px'>
<ul style='margin:0;padding-left:18px;font-size:13px;color:#ccc;line-height:1.9'>
<li><strong style='color:#fff'>Per-transaction cap</strong> &mdash; block anything over $200</li>
<li><strong style='color:#fff'>Daily total</strong> &mdash; rolling budget across all spend</li>
<li><strong style='color:#fff'>Velocity limit</strong> &mdash; kills the retry loop instantly</li>
<li><strong style='color:#fff'>Merchant allowlist</strong> &mdash; <code style='color:#34d399'>unknown-gpu.ru</code>? Blocked.</li>
<li><strong style='color:#fff'>Category rule</strong> &mdash; buy API credits, never wire money</li>
<li><strong style='color:#fff'>Time-of-day</strong> &mdash; flag spend outside 9-5</li>
</ul>
</td></tr></table>
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>Your agent calls one endpoint. sipi.bot checks all six with a deterministic rules check. If any rule fires, the transaction is approve, block, or flag. Money never moves on a block.</p>
<div style='background:linear-gradient(135deg,#0d1f1a,#0a0a0a);border:1px solid rgba(0,212,170,0.12);border-radius:10px;padding:16px;margin-bottom:20px'>
<p style='margin:0 0 4px;font-size:12px;font-weight:600;color:#00d4aa'>Tomorrow</p>
<p style='margin:0;font-size:12px;color:#666;line-height:1.5'>The three lines of code that wire sipi.bot into any agent runtime. MCP, HTTP, or CLI.</p>
</div>
""")

# Day 3 — integration (how-to)
_SOAP_CONTENT.append("""
<div style='text-align:center;margin-bottom:24px'>
<span style='display:inline-block;background:rgba(0,212,170,0.1);color:#00d4aa;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:0.5px'>DAY 3 OF 5</span>
</div>
<h2 style='margin:0 0 16px;font-size:18px;font-weight:700;color:#fff;line-height:1.3'>Three lines. Any agent runtime.</h2>
<p style='margin:0 0 16px;font-size:14px;color:#999;line-height:1.6'>sipi.bot is a native MCP tool, so Claude Code, Cursor, and Hermes call it directly. It's also a plain HTTP API and a CLI, so any agent can use it.</p>
<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='background:#0a0a0a;border-radius:8px;border:1px solid #1a1a1a;margin-bottom:20px'><tr><td style='padding:16px'>
<code style='display:block;font-family:SF Mono,Consolas,monospace;font-size:12px;color:#34d399;line-height:1.8'>
# Your agent asks before it spends<br>
curl -X POST https://sipi.bot/v1/transactions/evaluate \\<br>
&nbsp;&nbsp;-H "Authorization: Bearer ***" \\<br>
&nbsp;&nbsp;-d '{"amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute"}'<br><br>
# sipi.bot answers without a model call<br>
{ "decision": "BLOCKED", "reason": "Merchant not on allowlist" }
</code>
</td></tr></table>
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>That's it. LangChain, CrewAI, OpenAI Agents SDK, Vercel AI SDK &mdash; all wrap the same endpoint. Your agent gets approve, block, or flag before a single dollar moves.</p>
<p style='text-align:center;margin:24px 0 8px'><a href='https://sipi.bot/playground/' style='display:inline-block;background:#00d4aa;color:#0a0a0a;text-decoration:none;padding:12px 32px;border-radius:8px;font-weight:700;font-size:13px'>Try it free in the playground &rarr;</a></p>
<p style='text-align:center;margin:0 0 32px;font-size:12px;color:#666;line-height:1.6'>No signup, no card, no key &mdash; run a live transaction through the firewall now.<br>When you're ready to protect production: <a href='https://sipi.bot/checkout/team?source=drip_day3' style='color:#00d4aa;text-decoration:none'>Team is \$99/mo &rarr;</a></p>
""")

# Day 4 — proof (eval suite)
_SOAP_CONTENT.append("""
<div style='text-align:center;margin-bottom:24px'>
<span style='display:inline-block;background:rgba(0,212,170,0.1);color:#00d4aa;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:0.5px'>DAY 4 OF 5</span>
</div>
<h2 style='margin:0 0 16px;font-size:18px;font-weight:700;color:#fff;line-height:1.3'>53 labeled scenarios. 53/53 passed.</h2>
<p style='margin:0 0 16px;font-size:14px;color:#999;line-height:1.6'>A spend firewall is only as good as the rules behind it. So I built a public eval suite &mdash; the <strong style='color:#fff'>sipi.bot Eval Gym</strong> &mdash; with 53 real-world spend scenarios:</p>
<div style='background:#111;border:1px solid #1a1a1a;border-radius:10px;padding:16px;margin-bottom:16px'>
<ul style='margin:0;padding-left:18px;font-size:13px;color:#888;line-height:1.8'>
<li>Retry loops that drain budgets overnight</li>
<li>Unknown merchants and lookalike domains</li>
<li>Overage tier escalations</li>
<li>Off-hours autonomous purchases</li>
<li>Category violations (compute vs. wire transfer)</li>
<li>Multi-agent coordinated spend spirals</li>
</ul>
</div>
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>The engine passes all 53. Every decision is written to a queryable audit log &mdash; rule fired, amount, reason, and timestamp.</p>
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>You can <a href='https://sipi.bot/eval' style='color:#00d4aa;text-decoration:none'>read the full eval report</a> and run it yourself. The self-hosted core is MIT-licensed.</p>
""")

# Day 5 — urgency + close (fear)
_SOAP_CONTENT.append("""
<div style='text-align:center;margin-bottom:24px'>
<span style='display:inline-block;background:rgba(255,107,107,0.12);color:#ff6b6b;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:0.5px'>DAY 5 OF 5 &mdash; FINAL</span>
</div>
<h2 style='margin:0 0 16px;font-size:18px;font-weight:700;color:#fff;line-height:1.3'>The deployment checklist.</h2>
<p style='margin:0 0 16px;font-size:14px;color:#999;line-height:1.6'>If you deploy autonomous agents, here is the checklist to run before the next one goes to production:</p>
<table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='background:#0d1f1a;border:1px solid rgba(0,212,170,0.08);border-radius:10px;margin-bottom:20px'><tr><td style='padding:16px'>
<ol style='margin:0;padding-left:18px;font-size:13px;color:#ccc;line-height:2'>
<li>Set a per-transaction cap (start at $200)</li>
<li>Set a daily total (start at 10x your normal daily spend)</li>
<li>Set a velocity limit (10 transactions/hour)</li>
<li>Allowlist your known merchants</li>
<li>Block categories you never want spent (wire, crypto)</li>
<li>Flag off-hours spend for human approval</li>
</ol>
</td></tr></table>
<div style='background:linear-gradient(135deg,#0d1f1a,#0a0a0a);border:1px solid rgba(0,212,170,0.12);border-radius:14px;padding:24px;text-align:center;margin-bottom:20px'>
<p style='margin:0 0 8px;font-size:15px;font-weight:700;color:#fff'>The guarantee</p>
<p style='margin:0 0 16px;font-size:13px;color:#999;line-height:1.6'>If sipi.bot ever green-lights a spend that breaks one of your active rules, that month is free.</p>
<p style='margin:0 0 4px;font-size:24px;font-weight:800;color:#00d4aa'>$99<span style='font-size:11px;color:#555;font-weight:400'>/mo</span></p>
<p style='margin:0 0 16px;font-size:11px;color:#555'>unlimited evaluations &middot; no per-call fees &middot; cancel anytime</p>
<a href='https://sipi.bot/pricing' style='display:inline-block;background:#00d4aa;color:#0a0a0a;text-decoration:none;padding:12px 32px;border-radius:8px;font-weight:700;font-size:13px'>Protect my agent &rarr;</a>
</div>
<p style='margin:0;font-size:13px;color:#555;line-height:1.6'>Thanks for reading the playbook. If it was useful, the next step is wiring sipi.bot into your agent before it goes to production. If it wasn't useful, unsubscribe anytime.</p>
""")


# The retired 30-day broadcast sequence was removed; only the five-message
# opt-in playbook above is eligible for delivery.

# ─── Subscriber + state file helpers ────────────────────────────────
def _subs_file() -> str:
    return os.environ.get("SUBS_FILE", os.path.join(os.getcwd(), "subscribers.txt"))


def _db_path() -> str:
    configured = os.environ.get("DRIP_DB", "").strip()
    if configured:
        return configured
    if os.path.isdir("/data"):
        return "/data/drip.db"
    return os.path.join(os.getcwd(), "data", "drip.db")


def normalize_email(value: str) -> str | None:
    email = value.strip().casefold()
    if (
        not email
        or len(email) > 254
        or email.count("@") != 1
        or "|" in email
        or any(ch.isspace() or ord(ch) < 32 for ch in email)
    ):
        return None
    local, domain = email.rsplit("@", 1)
    if not local or not domain or local.startswith(".") or local.endswith("."):
        return None
    if domain.startswith(".") or domain.endswith(".") or ".." in email:
        return None
    return email


def _load_subscribers():
    """Read, normalize, and deduplicate legacy email|ref subscriber rows."""
    path = _subs_file()
    if not os.path.exists(path):
        return
    seen = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 1)
            email = normalize_email(parts[0])
            ref = parts[1] if len(parts) > 1 else ""
            if email and email not in seen:
                seen.add(email)
                yield {"email": email, "ref": ref, "subscribed_at": 0.0}


def _connect_state() -> sqlite3.Connection:
    path = _db_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS drip_state (
            email TEXT PRIMARY KEY,
            soap_day INTEGER NOT NULL DEFAULT 0,
            last_sent REAL,
            provider_id TEXT,
            updated_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def _idempotency_key(email: str, soap_day: int) -> str:
    digest = hashlib.sha256(email.encode("utf-8")).hexdigest()[:32]
    return f"sipi-soap-v1/day-{soap_day}/{digest}"


# ─── Main drip loop ─────────────────────────────────────────────────
def send_soap_operas():
    """Send day-appropriate Soap Opera email to each subscriber.

    The scheduler may poll hourly, but a subscriber advances at most once
    per 24 hours. State is committed after each accepted message.
    """
    if not _drip_enabled():
        return {"skipped": "disabled"}
    if not _resend_api_key():
        return {"skipped": "no RESEND_API_KEY"}
    if not _RUN_LOCK.acquire(blocking=False):
        return {"skipped": "already_running"}

    sent = 0
    failed = 0
    deferred = 0
    complete = 0
    stopped = None
    retry_after = None
    try:
        with closing(_connect_state()) as conn:
            for rec in _load_subscribers():
                email = rec["email"]
                now = time.time()
                row = conn.execute(
                    "SELECT soap_day, last_sent FROM drip_state WHERE email=?",
                    (email,),
                ).fetchone()
                current_day = int(row["soap_day"]) if row else 0
                last_sent = row["last_sent"] if row else None
                if current_day >= len(_SOAP_SUBJECTS):
                    complete += 1
                    continue
                if last_sent is not None and now - float(last_sent) < _DAY_SECONDS:
                    deferred += 1
                    continue

                target_day = current_day + 1
                idx = target_day - 1
                content = _build_branded_email(
                    _SOAP_SUBJECTS[idx],
                    _SOAP_CONTENT[idx],
                    f"Day {target_day} of 5",
                )
                delivery_key = _idempotency_key(email, target_day)
                try:
                    result = _send_resend(
                        email,
                        _SOAP_SUBJECTS[idx],
                        content,
                        delivery_key,
                    )
                except ResendError as exc:
                    failed += 1
                    if exc.stop_batch:
                        stopped = exc.category
                        retry_after = exc.retry_after
                        break
                    continue
                except Exception:
                    # Unknown transport failures are treated as global/transient,
                    # never echoed, and stop this batch to avoid a retry storm.
                    failed += 1
                    stopped = "unexpected"
                    break

                accepted_at = time.time()
                conn.execute(
                    """
                    INSERT INTO drip_state
                        (email, soap_day, last_sent, provider_id, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(email) DO UPDATE SET
                        soap_day=excluded.soap_day,
                        last_sent=excluded.last_sent,
                        provider_id=excluded.provider_id,
                        updated_at=excluded.updated_at
                    """,
                    (
                        email,
                        target_day,
                        accepted_at,
                        result.get("id"),
                        accepted_at,
                    ),
                )
                conn.commit()
                sent += 1
    finally:
        _RUN_LOCK.release()

    summary = {
        "sent": sent,
        "failed": failed,
        "deferred": deferred,
        "complete": complete,
    }
    if stopped:
        summary["stopped"] = stopped
    if retry_after:
        summary["retry_after"] = retry_after
    print(
        "[drip] Soap Opera tick: "
        f"sent={sent} failed={failed} deferred={deferred} "
        f"complete={complete} stopped={stopped or 'no'}",
        flush=True,
    )
    return summary


def start_drip_scheduler():
    """Start the hourly drip daemon. Call from serve() in api.py."""
    if not _drip_enabled():
        print("[drip] scheduler disabled (set DRIP_ENABLED=true to enable)", flush=True)
        return
    if not _resend_api_key():
        print("[drip] RESEND_API_KEY not set — drip scheduler disabled", flush=True)
        return

    def _loop():
        time.sleep(30)  # let server bind first
        while True:
            try:
                send_soap_operas()
            except Exception as e:
                print(f"[drip] error: {e}", flush=True)
            time.sleep(3600)

    t = threading.Thread(target=_loop, name="sipi-bot-drip", daemon=True)
    t.start()
    print("[drip] background scheduler started (hourly)", flush=True)


def delivery_enabled() -> bool:
    """Public status helper for subscription confirmation copy."""
    return _drip_enabled() and bool(_resend_api_key())
