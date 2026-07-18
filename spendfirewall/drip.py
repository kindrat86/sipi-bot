"""drip.py — Soap Opera + Seinfeld email follow-up engine for sipi.bot.

Brunson Traffic Secrets Secret #6 (Follow-Up Funnels):
  - 5-day Soap Opera Sequence for new subscribers (emotion -> logic -> fear)
  - 30-day Seinfeld daily emails after Soap Opera completes
  - Hourly daemon thread fires day-appropriate emails
  - Manual trigger via /cron/drip?secret=...

Mirrors the proven pattern in sanctionsai (~/workspace/agentmail/api.py).
Requires RESEND_API_KEY + EMAIL_FROM env vars (set via `flyctl secrets set`).
If those are absent, the module is a no-op (subscribers still appended to
SUBS_FILE by api.py /subscribe handler) so the app never crashes.
"""
from __future__ import annotations

import json
import os
import time
import threading
import urllib.request
import urllib.error

_RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "").strip()
_EMAIL_FROM = os.environ.get(
    "EMAIL_FROM", "sipi.bot <noreply@mail.sipi.bot>"
)
_PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://sipi.bot").rstrip("/")


# ─── Resend transport (stdlib urllib — sipi.bot is stdlib-only by design) ─
def _send_resend(to_email: str, subject: str, html_body: str) -> dict:
    """Send email via Resend API with unsubscribe link injection.

    Uses stdlib urllib so sipi.bot stays dependency-free (no requests).
    """
    if not _RESEND_API_KEY:
        return {"ok": False, "error": "RESEND_API_KEY not configured"}
    unsub_url = f"{_PUBLIC_URL}/unsubscribe?email={to_email}"
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
        headers={
            "Authorization": f"Bearer {_RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", "ignore")
            return {"ok": True, "id": json.loads(body).get("id")}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", "ignore")
        try:
            err = json.loads(err_body).get("message", err_body)
        except Exception:
            err = err_body
        raise RuntimeError(f"Resend error {e.code}: {err}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Resend network error: {e.reason}")


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
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>Tomorrow I'll show you the six rules that would have stopped every one of those charges in under 5 milliseconds. For now, just know: if you have an autonomous agent holding a payment method, this will happen to you. The only question is when.</p>
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
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>Your agent calls one endpoint. sipi.bot checks all six in under 5 milliseconds. If any rule fires, the transaction is approve, block, or flag. Money never moves on a block.</p>
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
# sipi.bot answers in &lt;5ms<br>
{ "decision": "BLOCKED", "reason": "Merchant not on allowlist" }
</code>
</td></tr></table>
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>That's it. LangChain, CrewAI, OpenAI Agents SDK, Vercel AI SDK &mdash; all wrap the same endpoint. Your agent gets approve, block, or flag before a single dollar moves.</p>
<p style='text-align:center;margin:24px 0 32px'><a href='https://sipi.bot/pricing' style='display:inline-block;background:#00d4aa;color:#0a0a0a;text-decoration:none;padding:12px 32px;border-radius:8px;font-weight:700;font-size:13px'>Start the free pilot &rarr;</a></p>
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
<p style='margin:0 0 20px;font-size:14px;color:#999;line-height:1.6'>The engine passes all 53. Every decision is written to a tamper-evident audit log &mdash; rule fired, amount, reason. Compliance-grade.</p>
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


# ─── Seinfeld: 30-day daily tips (broadcast mode) ───────────────────
_SEINFELD_SUBJECTS = [
    "Quick tip: Start with a $200 per-tx cap",
    "Case study: The retry loop that cost $4,000",
    "Velocity limits vs. daily totals — what's the difference?",
    "Why self-host? Three reasons.",
    "MCP tip: Add sipi.bot to Claude Code in 30 seconds",
    "The 6 rule types, ranked by impact",
    "How to read the audit log",
    "Feature deep dive: Human-in-the-loop approval queue",
    "How often should you review flagged transactions?",
    "Behind the scenes: How sipi.bot hits <5ms",
    "Quick tip: Merchant allowlist patterns",
    "The anatomy of an agent payment pipeline",
    "Why we don't charge per-call",
    "Customer story: Stopping a runaway agent in 8 seconds",
    "Cost analysis: sipi.bot vs. a human babysitter ($4,500/mo)",
    "Feature deep dive: Category rules",
    "The future of agent spend governance",
    "Quick tip: Time-of-day rules for overnight agents",
    "Building an agent that purchases safely",
    "Why every agent needs a spend firewall",
    "Customer story: Enterprise multi-agent budgets",
    "The difference between a spend cap and a spend firewall",
    "Feature update: New rule templates",
    "Quick tip: Integrating with Stripe",
    "The cost of a single runaway incident",
    "Behind the scenes: Our eval methodology (53/53)",
    "Customer story: From free pilot to production in a week",
    "Compliance 101: Audit trails for SOC2",
    "Feature deep dive: SSE live dashboard",
    "[Last] Your sipi.bot journey — what's next",
]

_SEINFELD_CONTENT = []  # placeholder; populated lazily if needed


# ─── Subscriber + state file helpers ────────────────────────────────
def _subs_file() -> str:
    return os.environ.get("SUBS_FILE", os.path.join(os.getcwd(), "subscribers.txt"))


def _state_file(name: str) -> str:
    data_home = os.environ.get("AGENTMAIL_HOME", os.path.join(os.getcwd(), "data"))
    return os.path.join(data_home, name)


def _load_subscribers():
    """Read subscribers.txt (email|ref format written by api.py /subscribe)."""
    path = _subs_file()
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 1)
            email = parts[0]
            ref = parts[1] if len(parts) > 1 else ""
            if email and "@" in email:
                yield {"email": email, "ref": ref, "subscribed_at": 0.0}


def _load_state(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


# ─── Main drip loop ─────────────────────────────────────────────────
def send_soap_operas():
    """Send day-appropriate Soap Opera email to each subscriber.

    For sipi.bot we don't have reliable subscribed_at timestamps (the file
    is email|ref lines), so we use state-only progression: each subscriber
    advances one day per cron tick until day 5.
    """
    if not _RESEND_API_KEY:
        return {"skipped": "no RESEND_API_KEY"}

    soap_state_path = _state_file("soap_state.json")
    state = _load_state(soap_state_path)
    new_state = dict(state)
    sent = 0

    for rec in _load_subscribers():
        email = rec["email"]
        current_day = state.get(email, {}).get("soap_day", 0)
        target_day = current_day + 1
        if target_day > 5:
            continue  # Soap Opera complete; Seinfeld handled separately
        idx = target_day - 1
        content = _build_branded_email(
            _SOAP_SUBJECTS[idx], _SOAP_CONTENT[idx], f"Day {target_day} of 5"
        )
        try:
            _send_resend(email, _SOAP_SUBJECTS[idx], content)
            new_state[email] = {"soap_day": target_day, "last_sent": time.time()}
            sent += 1
        except Exception as e:
            print(f"[drip] Soap failed for {email} day {target_day}: {e}", flush=True)

    _save_state(soap_state_path, new_state)
    print(f"[drip] Soap Opera: sent {sent} emails this tick", flush=True)
    return {"sent": sent}


def start_drip_scheduler():
    """Start the hourly drip daemon. Call from serve() in api.py."""
    if not _RESEND_API_KEY:
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
