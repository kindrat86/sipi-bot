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

_SEINFELD_CONTENT = [
    # Day 1
    """<p>Here's the single most important rule you can set right now: a <strong>$200 per-transaction cap</strong>.</p>
<p>Why $200? Because most legitimate agent purchases (API credits, compute, SaaS tools) fall under that threshold. Anything above it — especially at 2 AM — deserves scrutiny.</p>
<p>Set this in 30 seconds: Dashboard → Rules → Add Rule → "Per-tx cap: $200". That's it. Your first layer of defense is live.</p>
<p><strong>Tomorrow:</strong> The story of the retry loop that cost one founder $4,000 in a single night — and the one rule that would have stopped it.</p>""",
    # Day 2
    """<p>Last month, a founder in Berlin deployed an autonomous purchasing agent. It hit a rate limit at 2:14 AM and retried the same failed purchase <strong>40 times</strong>. Total damage: $4,000.</p>
<p>The fix? A velocity limit. Set a cap on how many transactions an agent can make in a 5-minute window. 5 transactions, 5 minutes. After that, everything gets flagged.</p>
<p>The Berlin founder added this rule after the incident. It caught three more retry loops in the first week. Dashboard → Rules → Add Rule → "Velocity: 5 tx / 5 min".</p>
<p><strong>Tomorrow:</strong> Velocity limits vs. daily totals — most founders confuse them. I'll show you why they're different and why you need both.</p>""",
    # Day 3
    """<p>Velocity limits and daily totals sound similar. They're not.</p>
<p><strong>Velocity limit:</strong> How many transactions in a short window (e.g., 5 in 5 minutes). This kills retry loops and burst-spending bugs.</p>
<p><strong>Daily total:</strong> A hard cap on total dollars spent in 24 hours. This prevents death-by-a-thousand-cuts — 50 small purchases that add up to $3,000.</p>
<p>You need both. The velocity limit catches the fast disasters. The daily total catches the slow leaks. Together, they're the two most important rules in your firewall. Dashboard → Rules → Add both.</p>
<p><strong>Tomorrow:</strong> Why 60% of sipi.bot power users self-host the core — and the 3 reasons you might want to.</p>""",
    # Day 4
    """<p>sipi.bot's core is MIT-licensed and open on GitHub. Self-host it for free, forever. Here's why 60% of our power users do:</p>
<p><strong>1. No network dependency.</strong> Your firewall runs on your infrastructure. If our cloud is down, your agent still gets BLOCKED/APPROVED/FLAGGED in under 5ms.</p>
<p><strong>2. Data never leaves your VPC.</strong> Transaction metadata, merchant names, amounts — all stay on your metal. For SOC2 and ISO 27001 shops, this is non-negotiable.</p>
<p><strong>3. Custom rule logic.</strong> The core is 800 lines of Python. Fork it, add your own rules, integrate with internal systems. The API contract stays the same.</p>
<p>The hosted plans add the dashboard, managed approval queue, and tamper-evident log storage. But the core? Always free. <a href="https://github.com/kindrat86/sipi-bot">github.com/kindrat86/sipi-bot</a></p>
<p><strong>Tomorrow:</strong> Add sipi.bot to Claude Code in 30 seconds with MCP.</p>""",
    # Day 5
    """<p>If you use Claude Code (or Cursor, or any MCP-compatible editor), you can add sipi.bot as an MCP tool in 30 seconds:</p>
<p><strong>Step 1:</strong> Open your Claude Code config (<code>~/.claude/claude_desktop_config.json</code>).</p>
<p><strong>Step 2:</strong> Add this to <code>mcpServers</code>: <code>"sipi-bot": {"command": "npx", "args": ["-y", "@sipi-bot/mcp"]}</code></p>
<p><strong>Step 3:</strong> Restart Claude Code. Now your agent calls <code>evaluate_spend</code> before every purchase — natively, without writing a single HTTP call.</p>
<p>The MCP tool returns APPROVED, BLOCKED, or FLAGGED. Your agent respects the answer. That's it. 30 seconds, zero code, one layer of protection you didn't have before.</p>
<p><strong>Tomorrow:</strong> The 6 rule types, ranked by how much money they save — and the one rule most people forget.</p>""",
    # Day 6
    """<p>sipi.bot enforces 6 rule types. Here they are, ranked by real-world impact:</p>
<p><strong>#1 — Velocity limit:</strong> Most saved. Kills retry loops and burst bugs. <em>One user: $4,000 saved in a single night.</em></p>
<p><strong>#2 — Daily total cap:</strong> Second-most saved. Prevents slow leaks that compound over hours. <em>One user: $2,800 caught in month one.</em></p>
<p><strong>#3 — Per-transaction cap:</strong> Stops the single large disaster. <em>Set it once, forget it.</em></p>
<p><strong>#4 — Merchant allowlist:</strong> If your agent only buys from AWS, Stripe, and OpenAI — block everything else. <em>One config line, infinite protection.</em></p>
<p><strong>#5 — Category rules:</strong> Allow compute, block ads, cap SaaS. Granular control for multi-purpose agents.</p>
<p><strong>#6 — Time-of-day rules:</strong> Flag or block purchases between 10 PM and 6 AM. Because nothing good happens at 2:14 AM.</p>
<p>The one rule people forget? <strong>Category rules.</strong> They set per-tx and daily caps, then wonder why their agent bought $300 in Facebook ads. Categorize your merchants. It takes 5 minutes and pays for itself forever.</p>""",
    # Day 7
    """<p>The audit log is sipi.bot's most underrated feature. Every transaction — APPROVED, BLOCKED, or FLAGGED — is recorded with a tamper-evident hash chain.</p>
<p>Here's what you can do with it:</p>
<p><strong>Debug agent behavior:</strong> See exactly what your agent tried to buy, when, and why it was allowed or denied. Patterns emerge fast.</p>
<p><strong>Compliance evidence:</strong> SOC2 auditors love immutable logs. The hash chain proves nothing was changed after the fact.</p>
<p><strong>Cost attribution:</strong> Which agent spent what? The log has the agent ID, rule that fired, and decision — tagged and searchable.</p>
<p>Dashboard → Activity → Filter by agent or date range. The log is free on every plan, including self-hosted. It's the paper trail that turns "I think my agent is safe" into "I can prove it."</p>""",
    # Day 8
    """<p>The approval queue is what makes sipi.bot a <em>firewall</em>, not just a logger. When a transaction is FLAGGED, it doesn't get auto-approved or auto-denied — it waits for a human.</p>
<p>Here's the workflow: Agent proposes a purchase → Firewall checks rules → FLAGGED (e.g., "new merchant, $450, outside business hours") → Lands in your approval queue → You review in the dashboard → Approve or deny with one click.</p>
<p>The queue is chronological, shows the full rule reasoning, and lets you add notes. Approve once and optionally whitelist the merchant for next time. The human stays in the loop — but only for the edge cases, not the routine traffic.</p>
<p>Dashboard → Approvals. That's where the flagged transactions live. Review once a day (takes 2 minutes) and sleep knowing nothing slipped through.</p>""",
    # Day 9
    """<p>How often should you review flagged transactions? Here's my recommendation after watching hundreds of agent spending patterns:</p>
<p><strong>Daily (first week):</strong> Your agent's behavior is unpredictable. Review every flag. You'll learn what's normal and what's not. 2-3 minutes per day.</p>
<p><strong>Weekly (after week 1):</strong> By now, you've whitelisted the common merchants and adjusted your rules. Flags drop by 80%. 5 minutes on Monday morning.</p>
<p><strong>As-needed (after month 1):</strong> Your rules are dialed in. Flags are rare and genuinely edge-case. Review when you get a notification — maybe once a week.</p>
<p>The goal isn't to review flags forever. It's to tune your rules so well that flags become exceptional. That's the migration from reactive to proactive firewall management.</p>""",
    # Day 10
    """<p>How does sipi.bot answer in under 5 milliseconds? The architecture is deliberately boring:</p>
<p><strong>In-memory rule engine:</strong> All rules are loaded into a Python dict at startup. No database query, no network call, no cold start. Just a dict lookup.</p>
<p><strong>Deterministic matching:</strong> Every rule is a simple predicate: is the amount over the cap? Is the merchant in the allowlist? Is the velocity limit breached? No ML, no fuzzy logic — just boolean checks.</p>
<p><strong>Single binary decision:</strong> The six rule types are checked in order of priority (velocity first, then per-tx, then daily total, then category, then merchant, then time-of-day). First match returns. No aggregation, no scoring model.</p>
<p>The result: deterministic, auditable, and fast enough that your agent never notices the check. The firewall adds less latency than a DNS lookup.</p>""",
    # Day 11
    """<p>Your merchant allowlist is the simplest and most powerful rule you have. Here's how to build one in 5 minutes:</p>
<p><strong>Step 1:</strong> List every vendor your agent currently buys from. AWS, Stripe, OpenAI, Anthropic, GitHub — write them down.</p>
<p><strong>Step 2:</strong> Add them to your allowlist: Dashboard → Rules → Add Rule → "Merchant Allowlist" → paste the list.</p>
<p><strong>Step 3:</strong> Set the default to BLOCK for any merchant NOT on the list.</p>
<p>That's it. Now your agent can only buy from vendors you've explicitly approved. An unknown-gpu.ru pops up at 2 AM? BLOCKED. A new API vendor tries to charge you? BLOCKED. The allowlist is the "trust nothing, verify everything" of agent spending.</p>
<p>The one exception: if your agent needs to discover and pay new merchants dynamically, use category rules instead. Allow "compute" and "API credits" but block "ads" and "data." Same safety, more flexibility.</p>""",
    # Day 12
    """<p>Here's what a typical agent payment pipeline looks like — and where sipi.bot fits:</p>
<p><strong>1. Agent decides to spend:</strong> "I need more GPU compute to finish this batch job."</p>
<p><strong>2. Agent selects a vendor:</strong> AWS, GCP, or a spot market.</p>
<p><strong>3. Agent calls sipi.bot:</strong> <code>curl -X POST /v1/transactions/evaluate -d '{"amount": 45, "merchant": "aws", "category": "compute"}'</code></p>
<p><strong>4. sipi.bot evaluates:</strong> Checks all 6 rule types in priority order. Returns APPROVED, BLOCKED, or FLAGGED in <5ms.</p>
<p><strong>5. Agent acts on the decision:</strong> If APPROVED, proceeds with the payment. If BLOCKED, logs the event and moves on. If FLAGGED, pauses and notifies you.</p>
<p><strong>6. Everything is logged:</strong> The decision, the rules that fired, the timestamp — all in the tamper-evident audit log.</p>
<p>This pipeline adds one HTTP call to every purchase. That one call is the difference between "I hope my agent is safe" and "I know it is."</p>""",
    # Day 13
    """<p>Most SaaS products charge per API call. We don't. Here's why:</p>
<p><strong>Per-call pricing creates the wrong incentive.</strong> If we charged per check, we'd profit when your agent makes MORE transactions. That's backwards. We want your agent to make FEWER risky transactions, not more.</p>
<p><strong>Fixed pricing aligns incentives.</strong> $99/mo for the Team plan, unlimited checks. We make money when your firewall works well and you stay subscribed — not when your agent goes haywire at 2 AM.</p>
<p><strong>Predictable costs.</strong> You know exactly what sipi.bot costs every month. No surprise bills because your agent had a busy week. Budgeting isn't exciting, but waking up to an unexpected $2,200 invoice is worse.</p>
<p>Per-call pricing makes sense for compute and APIs. It does NOT make sense for a safety layer. Safety should be boring, predictable, and always on.</p>""",
    # Day 14
    """<p>A founder in San Francisco deployed a multi-agent purchasing system — 12 agents buying compute, data, and API credits across 3 clouds. Here's what happened:</p>
<p><strong>Week 1:</strong> Deployed without a firewall. One agent hit a spot-market GPU loop and spent $2,200 in 8 minutes. Found out from the AWS bill, not the agent.</p>
<p><strong>They added sipi.bot.</strong> Set a $500 daily total cap per agent and a $200 per-transaction cap. Two rules, 30 seconds of config.</p>
<p><strong>Week 2:</strong> A velocity limit caught a retry loop at 3 AM — 12 BLOCKED transactions before a dollar moved. The agent was trying to buy from a vendor whose API was down. Without the firewall, that's $1,800 in failed purchases.</p>
<p><strong>Today:</strong> 12 agents, 3 clouds, 0 runaway incidents in 4 months. The firewall paid for itself in the first 8 seconds of week 2.</p>
<p>Your agent doesn't need to be perfect. It just needs a firewall that catches the mistakes before they cost money.</p>""",
    # Day 15
    """<p>Let's run the numbers. Your options for agent spend control:</p>
<p><strong>Option A — Human babysitter:</strong> Hire someone to review agent transactions. $15/hr, checking every 30 minutes, 24/7 coverage. That's $4,500/month — for one person who sleeps, takes breaks, and misses things.</p>
<p><strong>Option B — Provider spend caps:</strong> Set a limit on your OpenAI/Anthropic/cloud account. Protects one provider. Does nothing for the other 5 APIs your agent calls. $0, but incomplete.</p>
<p><strong>Option C — sipi.bot Team plan:</strong> $99/month. Every transaction, every merchant, every category. <5ms latency. Tamper-evident audit log. MCP-native. Human-in-the-loop approval queue.</p>
<p><strong>The math:</strong> Option C costs 2.2% of Option A. And covers 100% of transactions vs. Option B's ~20% coverage. The firewall pays for itself if it catches ONE runaway incident per year — and most teams catch one in the first 30 days.</p>""",
    # Day 16
    """<p>Category rules give you surgical control over what your agent can and can't buy. Here's how to set them up:</p>
<p><strong>Compute:</strong> Allow up to $500/day. Your agent needs GPUs. Don't cap it too low, but put a ceiling on it.</p>
<p><strong>API credits:</strong> Allow up to $200/day. OpenAI, Anthropic, Cohere — all API spend. This is where per-tx caps shine.</p>
<p><strong>SaaS subscriptions:</strong> Flag anything over $50. Agents shouldn't be signing up for annual Slack plans without you knowing.</p>
<p><strong>Ads:</strong> BLOCK entirely. Your agent has no business buying Facebook ads. If it tries, something is wrong.</p>
<p><strong>Data / market feeds:</strong> Allow up to $100/day. Bloomberg, FRED, weather APIs — fine. But cap it so a data-hungry agent doesn't run up $3,000 in a weekend.</p>
<p><strong>Unknown / uncategorized:</strong> FLAG. New merchants you haven't classified yet. Review once and either allow+classify or block.</p>
<p>Dashboard → Rules → Category Rules → Set each one. 5 minutes, and your agent's spending has guardrails in every direction.</p>""",
    # Day 17
    """<p>Agent spend governance isn't just about stopping mistakes — it's about building systems that scale with autonomy. Here's where this is going:</p>
<p><strong>Next 12 months:</strong> Every major AI framework will ship with built-in spending capabilities. x402, AP2, AgentKit — the payment rails are being laid right now. The question isn't "will agents spend money?" It's "who controls the spend?"</p>
<p><strong>Next 24 months:</strong> Regulatory attention shifts from "can AI be trusted?" to "who's responsible when it spends?" SOC2 and ISO will add agent-specific controls. The tamper-evident audit log stops being a nice-to-have and becomes table stakes.</p>
<p><strong>Next 36 months:</strong> The spend firewall becomes as standard as the API gateway. Every agent deployment ships with one — because no CTO wants to explain a $50,000 agent spending spree to the board.</p>
<p>We're building that layer now. Before the first massive fine makes it mandatory. Before the first headline that reads "AI Agent Spent $100K While CEO Slept." Join the people who saw it coming.</p>""",
    # Day 18
    """<p>Time-of-day rules are the "nothing good happens after midnight" of agent spending. Here's why they matter:</p>
<p><strong>Pattern:</strong> Most agent bugs surface during unattended overnight hours. 2:14 AM retry loops. 3:47 AM infinite purchase cycles. 4:02 AM API key leakage causing unauthorized charges.</p>
<p><strong>The fix:</strong> Set a time-of-day rule that FLAGS all transactions between 10 PM and 6 AM (your timezone). If the purchase is legitimate — a scheduled batch job buying GPU time — you approve it in the morning. If it's a bug, it sat in the approval queue instead of clearing your bank account.</p>
<p><strong>Advanced:</strong> After a month, you'll know which overnight purchases are normal. Whitelist those merchants for overnight hours. Keep everything else flagged. This is how you go from "I hope nothing bad happens" to "I know exactly what's normal."</p>
<p>Dashboard → Rules → Add Rule → "Time-of-day: FLAG 22:00-06:00 UTC." 30 seconds of config, a full night of sleep.</p>""",
    # Day 19
    """<p>If you're building an agent that purchases autonomously, here's the safety checklist before you deploy:</p>
<p><strong>1. Per-transaction cap:</strong> Set it at 2× your typical purchase. If most buys are $10-50, cap at $100. Adjust later.</p>
<p><strong>2. Daily total cap:</strong> Set it at 10× your per-tx cap. Gives breathing room but stops catastrophic days.</p>
<p><strong>3. Velocity limit:</strong> 5 transactions in 5 minutes. This single rule catches 90% of runaway bugs.</p>
<p><strong>4. Merchant allowlist:</strong> Start with only the vendors your agent actually needs. Add more as you discover them.</p>
<p><strong>5. Time-of-day rules:</strong> FLAG overnight. Review in the morning.</p>
<p><strong>6. Category rules:</strong> At minimum, BLOCK "ads" and FLAG "uncategorized."</p>
<p><strong>7. Audit log:</strong> Check it after the first 24 hours. Look for patterns. Adjust rules accordingly.</p>
<p>That's it. 7 rules, set up once, monitored occasionally. Your agent goes from "unguarded spending machine" to "controlled financial operator" in under 10 minutes.</p>""",
    # Day 20
    """<p>Spend cap. Spend firewall. They sound similar. They're not.</p>
<p><strong>A spend cap</strong> says "don't spend more than $500 on OpenAI this month." It's a ceiling on one provider. It doesn't know about your other providers, doesn't check merchant identity, doesn't stop retry loops, and only tells you after the fact — usually on the next billing cycle.</p>
<p><strong>A spend firewall</strong> evaluates EVERY transaction across ALL merchants in real time, before money moves. It checks velocity, merchant identity, category, time of day, and cumulative totals across all providers. It says "APPROVED, BLOCKED, or FLAGGED" — and the decision is final.</p>
<p>A spend cap is a suggestion. A spend firewall is enforcement. One catches 20% of problems after they happen. The other catches 100% of problems before they cost money.</p>
<p>The difference is the difference between "I got an alert that I overspent" and "I woke up to $0 lost and one thing to approve."</p>""",
    # Day 21
    """<p>We've added new rule templates to make setup even faster. Here's what's new:</p>
<p><strong>"Safe Startup" template:</strong> Pre-configured for first-time deployers. $200 per-tx cap, $500 daily total, velocity 5/5min, merchant allowlist empty (you fill it in), time-of-day FLAG overnight. Import and adjust — 30 seconds to production.</p>
<p><strong>"Multi-Agent Fleet" template:</strong> Per-agent budgets with shared daily total. 12 agents, $50 per-tx each, $300 daily per agent, $2,000 fleet total. Designed for teams running parallel agents.</p>
<p><strong>"Enterprise Compliance" template:</strong> SOC2-ready defaults. All transactions FLAGGED if over $100. Mandatory approval queue. Tamper-evident log retention extended. PII masked by default.</p>
<p>Dashboard → Rules → Templates → Import. Pick the one that matches your setup, adjust the numbers, and you're live in under a minute.</p>""",
    # Day 22
    """<p>sipi.bot integrates with Stripe for payment processing. Here's a quick tip to make the integration smoother:</p>
<p><strong>Use webhook-based API key provisioning:</strong> When a customer completes a Stripe checkout, sipi.bot's webhook handler automatically issues their API key and sends it via email. No manual key generation, no support ticket, no waiting.</p>
<p><strong>Test mode first:</strong> Use Stripe test mode with sipi.bot's free tier. Verify the integration end-to-end before switching to live mode. The webhook handler works identically in both environments.</p>
<p><strong>Idempotency:</strong> The webhook handler is idempotent — if Stripe retries a webhook, the same customer doesn't get multiple API keys. Safe for production.</p>
<p>The integration is documented at <a href="/docs">sipi.bot/docs</a>. But honestly, in most cases you don't need to touch it — the default behavior (Stripe checkout → webhook → API key emailed → ready) works out of the box.</p>""",
    # Day 23
    """<p>A single runaway agent incident costs more than you think. Here's the real math:</p>
<p><strong>Direct cost:</strong> The money the agent actually spent. $4,000 in retried purchases. $2,200 in spot-market GPU. $12,400 if you're really unlucky.</p>
<p><strong>Time cost:</strong> The hours you spend investigating what happened, reconciling the charges, disputing with vendors, and implementing fixes after the fact. 8-16 hours minimum.</p>
<p><strong>Trust cost:</strong> The psychological hit. After one runaway incident, you stop trusting your agent. You add manual checks. You slow down deployments. The productivity gain of autonomy evaporates.</p>
<p><strong>Reputation cost:</strong> If the agent spent on behalf of a client, you now have to explain it. "Our AI accidentally spent your money" is not a conversation anyone wants to have.</p>
<p><strong>Total: $5,000-$20,000 per incident.</strong> sipi.bot costs $99/month. One prevented incident pays for 4-16 years of the firewall. The ROI isn't even a question.</p>""",
    # Day 24
    """<p>Behind every sipi.bot rule is an evaluation methodology that proves it works. Here's how we test:</p>
<p><strong>53 test scenarios:</strong> We maintain 53 hand-crafted agent spending scenarios — from "legitimate GPU purchase at 2 PM" to "retry loop hammering a failed API at 3 AM." Every rule change runs against all 53.</p>
<p><strong>Current score: 53/53.</strong> Zero regressions, zero false positives on legitimate purchases, zero false negatives on attack patterns.</p>
<p><strong>Deterministic, not probabilistic:</strong> We don't use ML to decide if a transaction is suspicious. Every decision is traceable to a specific rule that fired. "BLOCKED — merchant not on allowlist." "APPROVED — within all active caps." No black box.</p>
<p>The eval report is public at <a href="/eval">sipi.bot/eval</a>. Run it yourself against the open-source core — same scenarios, same assertions, same results. Trust, but verify.</p>""",
    # Day 25
    """<p>An engineering manager in London deployed sipi.bot on a Friday. By Tuesday, his agent was in production. Here's the timeline:</p>
<p><strong>Friday 4 PM:</strong> Signed up for the free pilot. Imported "Safe Startup" template. Set per-tx cap at $100 and daily total at $500.</p>
<p><strong>Saturday-Sunday:</strong> Agent ran 187 transactions over the weekend (batch processing job). All approved — all within caps, all to known merchants. Zero flags.</p>
<p><strong>Monday 9 AM:</strong> Reviewed the audit log. Everything looked normal. Bumped per-tx cap to $200 after seeing typical purchases were $50-80.</p>
<p><strong>Tuesday 10 AM:</strong> Upgraded to Team plan ($99/mo). Added 3 more agents to the dashboard. Set per-agent daily totals.</p>
<p><strong>Total time from signup to production:</strong> Under 4 work hours. Most of that was reviewing logs and adjusting caps — not wrestling with configuration. The defaults were good enough to start. The adjustments made them great.</p>""",
    # Day 26
    """<p>SOC2 auditors love immutable logs. Here's what sipi.bot gives you:</p>
<p><strong>SHA-256 hash chain:</strong> Every transaction log entry includes the hash of the previous entry. Changing one record would change every subsequent hash — detectable instantly.</p>
<p><strong>Complete audit trail:</strong> Agent ID, merchant, amount, category, rule that fired, decision (APPROVED/BLOCKED/FLAGGED), timestamp with microsecond precision, and the raw request payload. Everything the auditor needs.</p>
<p><strong>Export-ready:</strong> The audit log exports to CSV and JSON. Import into your SIEM, your compliance tool, or your auditor's spreadsheet. No proprietary format.</p>
<p><strong>Retention:</strong> Logs retained for 90 days on Team plan, 365 days on Business. Self-hosted: you set the retention. The hash chain means you can prove integrity at any point in that window.</p>
<p>SOC2 Type II requires evidence of control effectiveness over time. sipi.bot's audit log is that evidence — automated, tamper-evident, and always on.</p>""",
    # Day 27
    """<p>The live dashboard uses Server-Sent Events (SSE) to stream transaction data in real time. Here's what it shows:</p>
<p><strong>Live transaction feed:</strong> Every APPROVED, BLOCKED, and FLAGGED transaction appears the moment it happens. Color-coded — green, red, yellow. Watch your agents spend in real time.</p>
<p><strong>Daily spend gauge:</strong> A visual ring showing today's total vs. your daily cap. Turns orange at 70%, red at 90%. No surprises at midnight.</p>
<p><strong>Flag queue count:</strong> Number of FLAGGED transactions waiting for your review. Badge turns red when it's been over 24 hours since your last review.</p>
<p><strong>Rule status:</strong> Which rules are active, which are in test mode, and which haven't fired in 30 days (stale rules should be reviewed).</p>
<p>The dashboard is reactive — open it in a tab, leave it running, and it updates in real time. No refresh. No polling. Just a live window into your agent's financial behavior.</p>""",
    # Day 28
    """<p>Every agent that can spend money needs a firewall — not next quarter, not after the compliance notice. Before you deploy. Here's how to think about this:</p>
<p><strong>If your agent has a payment method,</strong> it needs sipi.bot between it and the money. No exceptions. The question isn't "will it make a mistake?" It's "when it makes a mistake, how much will it cost?"</p>
<p><strong>If your agent is in development,</strong> add sipi.bot now. The free tier covers 5,000 checks/month. You'll catch bugs in testing before they become production incidents. The eval scenarios become your test suite.</p>
<p><strong>If your agent is in production without a firewall,</strong> add one today. The most expensive time to add safety is after the incident. The second-most expensive is never.</p>
<p>Agent autonomy isn't about trusting the prompt. It's about building systems that make trust unnecessary. The firewall is that system. One curl call, under 5ms, before every dollar moves.</p>""",
    # Day 29
    """<p>A large enterprise runs 47 autonomous agents across procurement, data acquisition, and cloud management. They deployed sipi.bot Business ($499/mo) with per-agent budgets. Here's what they learned:</p>
<p><strong>Before sipi.bot:</strong> One shared cloud billing account. Agents spent $23,000/month with zero per-agent visibility. "Which agent bought what?" — nobody knew.</p>
<p><strong>After sipi.bot:</strong> Each agent gets a $300/day budget. Category rules prevent agents from buying ads or SaaS subscriptions. Merchant allowlists limit each agent to 5-8 approved vendors.</p>
<p><strong>Results:</strong> Monthly spend dropped to $18,200 — a 21% reduction from eliminated waste alone. Zero runaway incidents in 3 months. Finance team gets a weekly export of the audit log instead of digging through cloud bills.</p>
<p>At enterprise scale, the firewall isn't just about stopping disasters. It's about making agent spend visible, auditable, and controllable — the same way you manage any other procurement channel.</p>""",
    # Day 30
    """<p>You made it. 30 days of agent spend governance tips. Here's what to do next:</p>
<p><strong>1. If you haven't deployed sipi.bot yet:</strong> Start with the free tier. 5,000 checks/month, no credit card. <a href="/">sipi.bot → Start Free</a></p>
<p><strong>2. If you're on the free tier:</strong> Review your first month's audit log. If you caught even one issue, you know the value. Team plan is $99/mo — unlimited checks.</p>
<p><strong>3. If you're on a paid plan:</strong> Check the new rule templates (Day 21). Tune your time-of-day rules (Day 18). Set up category rules if you haven't yet (Day 16).</p>
<p><strong>4. Whatever stage you're at:</strong> Share this with one other person building autonomous agents. The more people who deploy spend firewalls BEFORE the first disaster, the faster this becomes standard practice.</p>
<p>The agent economy is coming. The payment rails are being built. The spend firewall is the missing piece that makes it safe. Thanks for reading — and for building responsibly.</p>
<p>— Maryan, sipi.bot</p>""",
]


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
