#!/usr/bin/env python3
"""build_comparison_pages.py — Genuine comparison + alternative pSEO pages.

Populates public/vs/ and public/alternatives/ with real, non-doorway comparison
content: sipi.bot vs hardcoded checks, vs Stripe Radar, x402 alternatives, and
the self-hosted pitch. Each page is a landing fork for a money keyword.
"""
import os, html, json

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.normpath(os.path.join(HERE, "..", "public"))

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0a0a;color:#e8e8ea;font:16px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',Inter,sans-serif;-webkit-font-smoothing:antialiased}
a{color:#00d4aa;text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:820px;margin:0 auto;padding:0 22px}
nav{border-bottom:1px solid #23242a;position:sticky;top:0;background:rgba(10,10,10,.9);backdrop-filter:blur(10px);z-index:10}
nav .wrap{display:flex;justify-content:space-between;align-items:center;height:58px}
.brand{font-weight:700;font-size:18px}.brand .d{color:#00d4aa}
.nav-links a{color:#8a8d96;margin-left:20px;font-size:14px}
main{padding:52px 0}
h1{font-size:clamp(28px,5vw,40px);line-height:1.1;letter-spacing:-.02em;margin-bottom:8px}
.lead{font-size:19px;color:#8a8d96;margin-bottom:28px}
h2{font-size:24px;margin:36px 0 12px;letter-spacing:-.01em}
p{color:#c9ccd3;margin-bottom:14px}
.tag{display:inline-block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#00d4aa;border:1px solid rgba(0,212,170,.3);border-radius:100px;padding:5px 13px;margin-bottom:20px}
pre{background:#000;border:1px solid #23242a;border-radius:12px;padding:18px;overflow-x:auto;font-size:13.5px;line-height:1.5;color:#cfd2d8;margin:16px 0;font-family:'SF Mono',ui-monospace,Menlo,monospace}
code{font-family:'SF Mono',ui-monospace,Menlo,monospace}
.card{background:#121316;border:1px solid #23242a;border-radius:14px;padding:20px;margin:16px 0}
.cta{display:inline-block;background:#00d4aa;color:#04120e;font-weight:700;padding:13px 24px;border-radius:10px;margin:8px 8px 8px 0}
.cmp{width:100%;border-collapse:collapse;margin:20px 0;font-size:14.5px}
.cmp th,.cmp td{border:1px solid #23242a;padding:12px 14px;text-align:left}
.cmp thead th{background:#121316;color:#e8e8ea;font-weight:700}
.cmp tbody tr:nth-child(even){background:rgba(255,255,255,.02)}
.cmp tbody tr:last-child{background:rgba(0,212,170,.06)}
footer{border-top:1px solid #23242a;padding:30px 0;color:#8a8d96;font-size:14px}
@media(max-width:640px){.cmp{font-size:12.5px}.cmp th,.cmp td{padding:8px}}
"""

NAV = '<nav><div class="wrap"><div class="brand">sipi<span class="d">.bot</span></div><div class="nav-links"><a href="/for/">Integrations</a><a href="/pricing">Pricing</a><a href="/dashboard">Dashboard</a></div></div></nav>'

def page(title, desc, canonical, body, faq):
    faq_ld = {"@context":"https://schema.org","@type":"FAQPage",
              "mainEntity":[{"@type":"Question","name":q,
                             "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://sipi.bot{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article"><meta name="theme-color" content="#00d4aa">
<script type="application/ld+json">{json.dumps(faq_ld)}</script>
<style>{CSS}</style></head><body>
{NAV}
<main><div class="wrap">
<p class="author" style="color:#8a8d96;font-size:14px;margin:0 0 18px"><span rel="author">By the sipi.bot engineering team</span> · Published 2026-07-09 · Last updated 2026-07-09</p>
{body}
<h2>Frequently asked</h2>
{''.join(f'<div class="card"><h3 style="color:#e8e8ea;font-size:17px;margin-bottom:8px">{html.escape(q)}</h3><p>{html.escape(a)}</p></div>' for q,a in faq)}
<p style="margin-top:30px"><a class="cta" href="/pricing">Get started — $99/mo</a>
<a class="cta" href="/for/" style="background:transparent;border:1px solid #23242a;color:#e8e8ea">Framework integrations</a></p>
</div></main>
<footer><div class="wrap">sipi<span style="color:#00d4aa">.bot</span> — the spend firewall for autonomous AI agents ·
<a href="/for/">Integrations</a> · <a href="/vs/hardcoded-check/">vs hardcoded</a> · <a href="/vs/stripe-radar/">vs Stripe</a> · <a href="/">Home</a></div></footer>
</body></html>"""

PAGES = {
    "vs/hardcoded-check": {
        "title": "AI agent spend control vs hardcoded budget check — sipi.bot",
        "desc": "Why a hardcoded `if amount > X` check fails for autonomous agents. Compare hardcoded limits to a real spend firewall with velocity, daily caps, and human-approval paths.",
        "body": """<span class="tag">Comparison</span>
<h1>Hardcoded budget check vs a real spend firewall</h1>
<p class="lead">Every developer's first instinct: an `if amount > 500` guard. It works until the agent retries 40 times in one minute, splits a purchase across calls, or hits a vendor you didn't block. Here's what a single-line check actually misses.</p>

<h2>What the hardcoded check catches (and what it doesn't)</h2>
<p>A per-transaction limit — say, blocking anything over $500 — catches exactly ONE case: a single large purchase. It doesn't prevent any of the following:</p>

<table class="cmp"><thead><tr><th>Scenario</th><th>Hardcoded `if`</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>Single purchase over $500</td><td style="color:#00d4aa">Caught ✓</td><td style="color:#00d4aa">Caught ✓</td></tr>
<tr><td>40 small purchases ($40 each) in a retry loop</td><td style="color:#ff5470">Missed — $1,600 charged</td><td style="color:#00d4aa">Blocked — velocity rule stops at 11th</td></tr>
<tr><td>Multiple agents sharing a budget, cumulative $2,100 over a day</td><td style="color:#ff5470">Missed — per-tx limit sees only $250 each</td><td style="color:#00d4aa">Blocked — daily total rule fires at $2,000</td></tr>
<tr><td>Purchase from an unknown foreign vendor ($200)</td><td style="color:#ff5470">Missed — under per-tx limit</td><td style="color:#00d4aa">Blocked — merchant blocklist or allowlist</td></tr>
<tr><td>Large compute spend at 3am local time</td><td style="color:#ff5470">Missed — amount is fine, time is not</td><td style="color:#00d4aa">Blocked or flagged — time-window rule</td></tr>
<tr><td>Spend of $350 — legitimate but large enough to need a second pair of eyes</td><td style="color:#ff5470">Missed — goes through automatically</td><td style="color:#ffb020">Flagged for human review</td></tr>
</tbody></table>

<h2>The real cost: you're on call forever</h2>
<p>A hardcoded check puts the burden on you to monitor, tune, and enforce limits across every agent, every merchant, and every time zone. sipi.bot centralizes the rules once, enforces them on every call, and gives you a tamper-evident audit log of exactly what was allowed and why. You stop being a firewall operator and start being the person who reads one approval notification in the morning.</p>
<h2>When a hardcoded check is enough</h2>
<p>If you have one agent, one merchant, 9-to-5 hours, and no risk of retry loops, a hardcoded check works fine. The moment you have any of: multiple agents, a vendor allowlist, cumulative caps, or 24-hour operation, you've already rebuilt sipi.bot — just without the test suite, the audit trail, and the 53-scenario eval gym.</p>""",
        "faq": [
            ("Why not just set a spending limit on the credit card?", "Card limits fire after the charge and block ALL spending, including legitimate purchases. sipi.bot decides before the spend, applies rules per merchant and category, and flags (instead of blocking) transactions that only need a human look."),
            ("Can I combine a hardcoded check with sipi.bot?", "Yes. Many teams use a per-tx limit in their tool code for the obvious case and sipi.bot for the compound cases — daily totals, velocity, merchant rules, time windows. They complement each other; sipi.bot catches what the hardcoded guard misses."),
            ("How fast is the sipi.bot decision?", "Under 5 millseconds on the hosted endpoint. The check is a single HTTP call your agent makes before the spend; it doesn't slow down the purchase path."),
        ],
    },
    "vs/stripe-radar": {
        "title": "sipi.bot vs Stripe Radar — agent spend firewall vs card-level fraud detection",
        "desc": "Stripe Radar catches payment fraud. sipi.bot is a policy engine that blocks agent purchases before they happen. Complementary, not competitive — use both.",
        "body": """<span class="tag">Comparison</span>
<h1>sipi.bot vs Stripe Radar: agent policy engine meets card fraud detection</h1>
<p class="lead">Stripe Radar blocks suspicious payments. sipi.bot blocks purchases that violate YOUR rules. They operate at different layers and solve different problems.</p>

<table class="cmp"><thead><tr><th>What it does</th><th>Stripe Radar</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>When it fires</td><td>After the charge is attempted</td><td>Before the spend, in the agent's decision loop</td></tr>
<tr><td>What it blocks</td><td>Fraudulent payments (stolen cards, chargeback risk)</td><td>Unwanted purchases (runaway loops, bad merchants, over-budget)</td></tr>
<tr><td>Who configures it</td><td>The Stripe account owner; rules are about payment risk</td><td>The developer deploying the agent; rules are about spend policy</td></tr>
<tr><td>Rule types</td><td>Risk score thresholds, CVV/3DS checks, IP/location, velocity of card use</td><td>Per-tx limit, daily total, merchant allow/block, category limit, time window, velocity, approval threshold</td></tr>
<tr><td>Can it distinguish between vendors?</td><td>No — Radar blocks by risk signal, not by merchant name</td><td>Yes — merchant allowlist/blocklist per agent</td></tr>
<tr><td>What happens when blocked</td><td>Charge is declined; user may retry or use another card</td><td>Agent gets a reason string; stops and explains to the user</td></tr>
<tr><td>Human-in-the-loop</td><td>No — binary approve/decline</td><td>Yes — FLAGGED decision means a human reviews and approves or denies</td></tr>
</tbody></table>

<h2>They're built for different buyers</h2>
<p>Stripe Radar is built for businesses accepting payments from end-users and protecting against payment fraud — a security layer on the payment rail. sipi.bot is built for developers who deploy autonomous agents that spend money, and who need a policy layer on the *decision to spend at all* — before the payment even hits Stripe.</p>
<h2>Use both</h2>
<p>The best setup is sipi.bot as the agent-side guardrail (approve/block/flag before the agent calls the payment API) and Stripe Radar as the payment-side safety net (catch actual fraud if someone bypasses the agent layer). They operate at different points in the stack and neither replaces the other.</p>""",
        "faq": [
            ("Does sipi.bot replace Stripe Radar?", "No. Radar catches payment fraud (stolen cards, chargebacks); sipi.bot catches unwanted spending (runaway agents, bad merchants, over-budget). Use both."),
            ("If I use Stripe, do I still need sipi.bot?", "Yes. Radar doesn't know your agent's intent, doesn't enforce merchant allowlists, and doesn't have a human-approval path for borderline purchases. sipi.bot is the agent's spend firewall; Stripe is the payment rail's fraud guard."),
            ("Can sipi.bot work with a non-Stripe payment processor?", "Yes. sipi.bot is independent of the payment rail — it evaluates the spend decision before any payment API is called, whether that's Stripe, a cloud billing API, or an ad platform."),
        ],
    },
    "alternatives/x402": {
        "title": "x402 spend limit alternative: agent guardrails before the payment — sipi.bot",
        "desc": "x402 handles the crypto payment. sipi.bot handles the decision to pay. One approves the transaction before it reaches the x402 rail — complementary infrastructure for the agent economy.",
        "body": """<span class="tag">Alternative</span>
<h1>Spend limits before x402 payments: sipi.bot as an agent-first guardrail</h1>
<p class="lead">x402 is the protocol for autonomous agent-to-agent payments in USDC. But it doesn't decide whether the agent *should* spend at all — that's sipi.bot's job. One call before the x402 transaction approves, blocks, or flags the spend against your policy.</p>

<h2>The gap in agent-commerce infrastructure</h2>
<p>The agent economy is building payment rails fast: x402 (Coinbase), AP2 (Google), and agent wallets are all solving the *how* of agent spending. But nobody is solving the *whether* — should this specific agent, at this specific time, pay this specific merchant, this specific amount?</p>
<p>sipi.bot fills that gap. Your agent calls sipi.bot before it signs an x402 payment, and the firewall evaluates the transaction against your rules: per-tx caps, daily totals, velocity, merchant allow/block, category limits, time windows, and an approval threshold that flags big spends for a human.</p>

<h2>How they compose</h2>
<pre>Agent → sipi.bot (/v1/transactions/evaluate) → APPROVED
  → Agent signs x402 USDC payment on Base mainnet
  → Payment settles on-chain

Agent → sipi.bot → BLOCKED (merchant not on allowlist)
  → Agent stops, explains to user, no payment made</pre>

<p>The architecture is additive: sipi.bot is the guardrail upstream of the payment rail. x402 is the money movement; sipi.bot is the spending policy. Both are open-source infrastructure for the agent economy.</p>""",
        "faq": [
            ("Does sipi.bot replace x402?", "No. x402 is a payment protocol for USDC transfers between agents. sipi.bot is a spend firewall that decides whether a transaction should proceed — it sits upstream of x402 and approves the spend before the payment is signed."),
            ("Can sipi.bot and x402 be used together?", "Yes. The agent calls sipi.bot first, and if the decision is APPROVED, it then signs the x402 payment. If BLOCKED or FLAGGED, no payment occurs. The two are complementary infrastructure."),
            ("Does sipi.bot handle the x402 payment itself?", "No. sipi.bot is a policy engine, not a payment processor. It evaluates the transaction and returns a decision; your agent or payment stack executes the actual transfer."),
        ],
    },
    "self-hosted": {
        "title": "Open source agent spend firewall — self-host sipi.bot",
        "desc": "Self-host the sipi.bot spend firewall for free. Stdlib Python, zero framework dependencies, 37MB Docker image, MIT licensed. Full policy engine, dashboard, and audit trail on your own infrastructure.",
        "body": """<span class="tag">Self-hosted</span>
<h1>Open source, self-hosted agent spend firewall</h1>
<p class="lead">sipi.bot is MIT-licensed and runs on your hardware. Stdlib Python — zero framework dependencies. The hosted version at sipi.bot runs on the same code you self-host.</p>

<h2>What you get self-hosting</h2>
<p>The full spend firewall: per-transaction caps, daily totals, velocity limits (runaway-loop protection), merchant allow/block, category limits, time windows, and an approval threshold. A live dashboard with tamper-evident audit log. An MCP tool for Claude Code / Cursor / Hermes, an HTTP API for any agent runtime, and a CLI.</p>

<h2>Deploy in under 2 minutes</h2>
<pre>git clone https://github.com/kindrat86/sipi-bot.git
cd sipi-bot
pip install .
sipi-bot serve --port 8080</pre>
<p>Open http://localhost:8080 for the dashboard and http://localhost:8080/for/ for framework integration docs. That's the entire self-hosted surface — landing page, dashboard, pricing, docs.</p>

<h2>What the hosted version adds</h2>
<p>The hosted version at sipi.bot ($99/mo) adds uptime guarantees, persistent audit logging across restarts, and priority support. The self-hosted core is feature-complete — the hosted version is for teams that don't want to run their own infrastructure. There is no gated functionality; the entire policy engine ships in the open-source release.</p>
<h2>Architecture that ships with you</h2>
<p>37MB Docker image on Fly.io. Stdlib http.server + sqlite3. No framework, no ORM, no build step. You can audit the entire codebase in an afternoon — it's ~3000 lines of Python with a 53-scenario eval gym that proves every rule works.</p>""",
        "faq": [
            ("Is the self-hosted version limited compared to the hosted one?", "No. The open-source core is feature-complete: the full policy engine, dashboard, audit trail, MCP tool, HTTP API, and CLI. The hosted version adds uptime guarantees, persistent log retention, and support."),
            ("What are the infrastructure requirements?", "Any machine that runs Python 3.11+. The server uses Python's stdlib http.server and sqlite3 — no framework, no database server, no external dependencies. A Raspberry Pi can run it."),
            ("Can I get support while self-hosting?", "Yes. GitHub issues are the primary support channel. The hosted tier includes priority response and SLAs."),
        ],
    },
}


def main():
    for slug, d in PAGES.items():
        canonical = f"/{slug}/"
        out_dir = os.path.join(PUB, slug)
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "index.html")
        with open(path, "w") as f:
            f.write(page(d["title"], d["desc"], canonical, d["body"], d["faq"]))
        print(f"wrote {path}  ({len(open(path).read())} bytes)")

    print("\nAll 4 comparison/alternative pages written.")
    print("Next: add to sitemap, footer on /for/ hub, and set pSEO state prefix=for,vs,alternatives,self-hosted")


if __name__ == "__main__":
    main()
