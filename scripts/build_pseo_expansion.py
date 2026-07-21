#!/usr/bin/env python3
"""build_pseo_expansion.py — Generate /compare/, /alternatives/, /templates/ pSEO pages.

Creates 6 comparison pages (compare/), 5 additional alternatives pages
(adding to the existing x402), and 6 prompt/workflow templates pages.
Patches spendfirewall/api.py to add the /compare/ prefix to _serve_pseo.

Run: python3 scripts/build_pseo_expansion.py
"""
import html
import json
import os
import re
import sys

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
ol,ul{margin:0 0 16px 22px;color:#c9ccd3}
ol li,ul li{margin-bottom:8px;line-height:1.6}
@media(max-width:640px){.cmp{font-size:12.5px}.cmp th,.cmp td{padding:8px}}
"""

NAV = ('<nav><div class="wrap"><div class="brand">sipi<span class="d">.bot</span></div>'
       '<div class="nav-links"><a href="/for/">Integrations</a><a href="/pricing">Pricing</a>'
       '<a href="/dashboard">Dashboard</a></div></div></nav>')


def page(title, desc, canonical, body, faq):
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in faq]}
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
<p class="author" style="color:#8a8d96;font-size:14px;margin:0 0 18px"><span rel="author">By the sipi.bot engineering team</span> · Published 2026-07-17 · Last updated 2026-07-17</p>
{body}
<h2>Frequently asked</h2>
{''.join(f'<div class="card"><h3 style="color:#e8e8ea;font-size:17px;margin-bottom:8px">{html.escape(q)}</h3><p>{html.escape(a)}</p></div>' for q, a in faq)}
<p style="margin-top:30px"><a class="cta" href="/pricing">Get started — $99/mo</a>
<a class="cta" href="/for/" style="background:transparent;border:1px solid #23242a;color:#e8e8ea">Framework integrations</a></p>
</div></main>
<footer><div class="wrap">sipi<span style="color:#00d4aa">.bot</span> — the spend firewall for autonomous AI agents ·
<a href="/for/">Integrations</a> · <a href="/benchmarks/">Benchmarks</a> · <a href="/best/">Best-of</a> · <a href="/">Home</a></div></footer>
</body></html>"""


# ═══════════════════════════════════════════════════════════════
# 6 COMPARISON PAGES: sipi.bot vs other spend-control approaches
# ═══════════════════════════════════════════════════════════════

COMPARE_PAGES = {
    "human-approval-workflow": {
        "title": "sipi.bot vs human approval workflows for AI agent spend — sipi.bot",
        "desc": "Compare a programmatic spend firewall to Slack-approval, email-approval, and manual review workflows. sipi.bot gives you rules that fire in under 5ms; humans fire on their own schedule.",
        "body": """<span class="tag">Comparison</span>
<h1>sipi.bot vs human approval workflows</h1>
<p class="lead">Slack notifications, email threads, and manual approval queues work for five transactions a day. They break when your agent makes 50 decisions a minute. Here's the gap.</p>

<h2>When humans are the bottleneck</h2>
<p>A human approval workflow — DM the manager, wait for an emoji reaction, check a spreadsheet — adds minutes of latency to every purchase decision. That's fine when an agent buys one thing a day. It's catastrophic when a travel agent books three flights in a retry loop at 2am.</p>

<table class="cmp"><thead><tr><th>Dimension</th><th>Human approval workflow</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>Decision latency</td><td>Minutes to hours</td><td>Under 5ms</td></tr>
<tr><td>24/7 coverage</td><td>Only during business hours</td><td>Always on</td></tr>
<tr><td>Runaway-loop protection</td><td>None — 40 small buys fly through before a human notices</td><td>Velocity rules stop at the 11th request</td></tr>
<tr><td>Consistency</td><td>Depends on who's on call and how awake they are</td><td>Same rules fire every time, deterministically</td></tr>
<tr><td>Audit trail</td><td>Scattered across Slack DMs and email threads</td><td>Tamper-evident log of every decision and its reason</td></tr>
<tr><td>Cost</td><td>Human ops time — expensive, doesn't scale</td><td>$99/mo flat; one person reviews the exceptions only</td></tr>
</tbody></table>

<h2>The hybrid model: rules decide, humans handle the exceptions</h2>
<p>sipi.bot doesn't eliminate the human — it moves the human from gatekeeper to exception-handler. APPROVED transactions fire without anyone looking. BLOCKED transactions never reach a card. FLAGGED transactions go to a lean approval queue where a human reviews maybe three items a day instead of three hundred.</p>""",
        "faq": [
            ("Do I still need a human approval step?", "For most transactions, no. The firewall auto-approves everything within your rules. FLAGGED transactions — the borderline cases — go to a human. You review exceptions, not every purchase."),
            ("What if I want approval for every transaction?", "Set the approval_threshold rule to $0 — everything gets FLAGGED and goes to the human queue. But most teams find that setting per-transaction caps and daily totals catches 95% of risk with zero human latency."),
            ("How does the approval queue work in practice?", "When a transaction is FLAGGED, it appears in the dashboard. A human clicks Approve or Deny. The agent receives the result and acts on it. The queue is asynchronous — the agent waits for the decision."),
        ],
    },
    "aws-budgets": {
        "title": "sipi.bot vs AWS Budgets for AI agent spend control — sipi.bot",
        "desc": "AWS Budgets alerts you after you've already spent. sipi.bot blocks the agent before the spend. Compare a cloud billing monitor to a real-time agent spend firewall.",
        "body": """<span class="tag">Comparison</span>
<h1>sipi.bot vs AWS Budgets: real-time blocking vs after-the-fact alerting</h1>
<p class="lead">AWS Budgets sends you an email when you hit 80% of your monthly forecast. sipi.bot blocks the spend before it happens. They solve different problems on different timelines.</p>

<table class="cmp"><thead><tr><th>What it does</th><th>AWS Budgets</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>When it fires</td><td>After spend accrues — forecast or actual</td><td>Before the spend, in the agent's decision loop</td></tr>
<tr><td>Action</td><td>Sends an alert (email, SNS, Chatbot)</td><td>Returns APPROVED, BLOCKED, or FLAGGED to the agent</td></tr>
<tr><td>Granularity</td><td>Per AWS service, per linked account, per tag</td><td>Per transaction: amount, merchant, category</td></tr>
<tr><td>Prevents spend?</td><td>No — alerts only; you must act on the alert manually</td><td>Yes — BLOCKED means the agent physically cannot proceed</td></tr>
<tr><td>Works outside AWS?</td><td>AWS only (with some multi-cloud connectors)</td><td>Any platform — cloud, SaaS, ads, API credits</td></tr>
<tr><td>Velocity / retry-loop protection</td><td>No — 40 rapid small purchases look like normal usage</td><td>Yes — velocity caps stop runaway loops in real time</td></tr>
</tbody></table>

<h2>Different layers of the stack</h2>
<p>AWS Budgets is a billing-layer monitor: it tracks your cloud bill and alerts when you're trending over. sipi.bot is an application-layer firewall: it sits between the agent and the payment, making a decision on every transaction. Use AWS Budgets to watch your infrastructure costs; use sipi.bot to control what your agents are allowed to spend, anywhere, in real time.</p>""",
        "faq": [
            ("Can I use AWS Budgets instead of sipi.bot for my AI agents?", "Only if your agents spend exclusively on AWS services and you're comfortable with alerting after the fact. For agents that spend across multiple platforms — cloud, SaaS, APIs, ads — and need real-time blocking, sipi.bot fills the gap AWS Budgets doesn't cover."),
            ("Do AWS Budgets and sipi.bot complement each other?", "Yes. Use sipi.bot as the real-time guardrail on every agent transaction, and AWS Budgets as the billing-level safety net watching your overall cloud spend. They operate at different layers."),
            ("Does sipi.bot track cloud infrastructure costs?", "No. sipi.bot evaluates individual spend transactions — a $200 GPU purchase is one transaction. It doesn't monitor your EC2 bill. That's AWS Budgets' job."),
        ],
    },
    "openai-moderation": {
        "title": "sipi.bot vs OpenAI Moderation API for agent guardrails — sipi.bot",
        "desc": "The Moderation API catches harmful content. sipi.bot catches harmful spending. Compare content safety to spend safety — two guardrails, different threats.",
        "body": """<span class="tag">Comparison</span>
<h1>sipi.bot vs OpenAI Moderation API: spend safety vs content safety</h1>
<p class="lead">The OpenAI Moderation API flags harmful text. sipi.bot flags harmful transactions. If your agent can spend money, you need both — one protects your users, the other protects your wallet.</p>

<table class="cmp"><thead><tr><th>Dimension</th><th>OpenAI Moderation API</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>What it evaluates</td><td>Text — prompts and completions</td><td>Transactions — amount, merchant, category</td></tr>
<tr><td>What it blocks</td><td>Hate speech, violence, harassment, self-harm, sexual content</td><td>Over-budget spends, bad merchants, runaway loops, off-hours purchases</td></tr>
<tr><td>Decision model</td><td>ML classifier with category scores</td><td>Deterministic rules: caps, totals, velocity, allow/block lists</td></tr>
<tr><td>Output</td><td>Category flags with confidence scores (0-1)</td><td>APPROVED, BLOCKED, or FLAGGED with a human-readable reason</td></tr>
<tr><td>Configuration</td><td>Category thresholds per endpoint</td><td>Per-transaction limit, daily total, merchant allow/block, category limit, time window, velocity, approval threshold</td></tr>
<tr><td>Use case</td><td>Content safety — what the agent says</td><td>Spend safety — what the agent buys</td></tr>
</tbody></table>

<h2>Two guardrails, not one</h2>
<p>The Moderation API stops your agent from generating harmful text. It doesn't stop it from buying $2,000 of GPU time at 3am from an unknown vendor. sipi.bot stops the spend; the Moderation API stops the content. They're orthogonal safety layers and you need both when your agent talks to users and spends money.</p>
<p>The pattern: call the Moderation API on the agent's output to users, and call sipi.bot on the agent's spend actions. Two APIs, two threat surfaces, one safe agent.</p>""",
        "faq": [
            ("Does sipi.bot replace the OpenAI Moderation API?", "No. The Moderation API is for content safety — catching harmful text. sipi.bot is for spend safety — catching harmful transactions. Use both when your agent interacts with users and spends money."),
            ("Can I call both in the same agent pipeline?", "Yes. A typical flow: agent generates a response → Moderation API checks it for harmful content → agent proposes a spend → sipi.bot checks if it's allowed → agent executes the spend. Two guards, two checks, no overlap."),
            ("Is sipi.bot's rule engine as accurate as the Moderation API's ML?", "Different accuracy models. sipi.bot's rules are deterministic — they fire exactly when the condition matches, with no false positives or false negatives. The Moderation API uses probabilistic ML. Both are appropriate for their domain."),
        ],
    },
    "custom-middleware": {
        "title": "sipi.bot vs building custom spend middleware — sipi.bot",
        "desc": "Compare building your own spend guard in FastAPI/Express middleware to using sipi.bot. One is a weekend project; the other is a maintained firewall with an eval suite.",
        "body": """<span class="tag">Comparison</span>
<h1>sipi.bot vs building custom spend middleware</h1>
<p class="lead">Every team with an agent that spends money eventually writes a guard function. Here's what that guard function grows into, and why teams ship it to sipi.bot instead of maintaining it forever.</p>

<h2>The life cycle of a custom spend guard</h2>
<p>Week 1: <code>if amount > 500: raise ValueError</code>. Week 2: add a merchant list. Week 4: add daily totals in Redis. Week 8: add a human approval queue. Week 12: add an audit log. Week 16: realize you've built a worse version of sipi.bot, with no test suite, no eval gym, and your intern maintaining it.</p>

<table class="cmp"><thead><tr><th>What you need</th><th>DIY middleware effort</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>Per-transaction cap</td><td>2 lines of Python</td><td>Built-in</td></tr>
<tr><td>Merchant allow/block list</td><td>A dict and an if statement</td><td>Built-in, configurable in dashboard</td></tr>
<tr><td>Daily spending total across agents</td><td>Redis or Postgres, TTL keys, race conditions</td><td>Built-in, single writer, no races</td></tr>
<tr><td>Velocity / runaway-loop protection</td><td>Sliding window counter, careful edge cases</td><td>Built-in, 53-scenario eval gym verified</td></tr>
<tr><td>Human approval queue</td><td>Slack bot or custom dashboard</td><td>Built-in dashboard with Approve/Deny</td></tr>
<tr><td>Tamper-evident audit log</td><td>Append-only table, hash chaining</td><td>Built-in, every decision logged</td></tr>
<tr><td>Testing and maintenance</td><td>Your team's burden forever</td><td>Our team's burden; open-source core you can audit</td></tr>
</tbody></table>

<h2>The real cost is maintenance</h2>
<p>Building the first version takes a weekend. Maintaining it — handling edge cases, fixing race conditions, adding features as your agent fleet grows, writing tests for every new rule — is a permanent tax on your team. sipi.bot costs $99/mo and ships with a 53-scenario eval suite that proves every rule works. The alternative is paying your engineer $150/hour to maintain a custom guard forever.</p>""",
        "faq": [
            ("Is building a custom guard really that hard?", "The v1 is easy — one if statement. The v5 (daily totals, velocity, human-in-the-loop, audit trail) is a non-trivial distributed systems problem. sipi.bot has already solved it, tested it, and open-sourced the core."),
            ("Can I extend sipi.bot if my needs are unique?", "Yes. The core is MIT-licensed and runs on your hardware. Fork it, add custom rule types, wire in your own notification channels. The hosted version gives you uptime and support; the code is yours to modify."),
            ("What if I only need per-transaction caps?", "If that's truly all you need, a 2-line guard function is fine. The question is: will you still only need per-transaction caps in six months, when your agent fleet has grown and your CFO is asking about audit trails?"),
        ],
    },
    "cedar-opa-policy": {
        "title": "sipi.bot vs Cedar/OPA policy engines for agent spend — sipi.bot",
        "desc": "Compare general-purpose policy engines (Cedar, OPA/Rego) to sipi.bot's purpose-built spend firewall. Policy engines need you to write the spend logic; sipi.bot ships with it.",
        "body": """<span class="tag">Comparison</span>
<h1>sipi.bot vs Cedar and OPA: purpose-built spend firewall vs general policy engines</h1>
<p class="lead">Cedar and Open Policy Agent are powerful policy engines. But they're policy *frameworks* — you write the spend rules from scratch. sipi.bot is a spend *product* — the rules, the dashboard, and the audit trail ship pre-built.</p>

<table class="cmp"><thead><tr><th>Dimension</th><th>Cedar / OPA</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>What it is</td><td>A policy language and evaluation engine</td><td>A spend firewall product with a pre-built rule set</td></tr>
<tr><td>Rule authoring</td><td>You write Cedar policies or Rego rules from scratch</td><td>Pre-built rule types: per-tx cap, daily total, velocity, merchant, category, time window, approval threshold</td></tr>
<tr><td>Domain knowledge required</td><td>General policy logic; you define everything</td><td>None — the spend-control primitives are built in</td></tr>
<tr><td>Dashboard / UI</td><td>None — you build your own</td><td>Live dashboard with transaction feed, approval queue, rule editor</td></tr>
<tr><td>Audit trail</td><td>You implement logging yourself</td><td>Tamper-evident audit log built in</td></tr>
<tr><td>Agent framework integrations</td><td>You write the SDK wrappers</td><td>Pre-built wrappers for LangChain, CrewAI, OpenAI SDK, Vercel AI SDK</td></tr>
<tr><td>Best for</td><td>Arbitrary authorization policies across an entire platform</td><td>Controlling how much money AI agents can spend, where, and when</td></tr>
</tbody></table>

<h2>Policy engine vs policy product</h2>
<p>Cedar and OPA are excellent for what they do — arbitrary authorization policies — but they are not spend firewalls. To use them for agent spend control, you must design the spend model (amount, merchant, category, velocity), write the policy rules in their language, build the integration layer, add a dashboard, and maintain it all. sipi.bot gives you that entire stack in one product, pre-built and tested.</p>
<p>If you already run OPA for platform-wide authorization and want to add agent spend control as one more policy domain, sipi.bot composes cleanly — call sipi.bot from your agent code, and keep OPA for everything else. They're not competitors; they operate at different layers of the stack.</p>""",
        "faq": [
            ("Can sipi.bot replace OPA in my stack?", "No. OPA is a general authorization engine for your entire platform — APIs, Kubernetes, microservices. sipi.bot is specifically for AI agent spend control. They solve different problems and can coexist."),
            ("If I already use Cedar, do I still need sipi.bot?", "Probably yes. Cedar evaluates authorization policies; sipi.bot evaluates spend decisions with domain-specific primitives (velocity, merchant rules, daily caps) that you'd have to reimplement in Cedar from scratch."),
            ("Can sipi.bot's rules be expressed in Rego or Cedar?", "Yes, with enough effort. The question is: do you want to build, test, and maintain a complete spend-control system in a general policy language, or use a purpose-built product that ships with the primitives, dashboard, and eval suite already done?"),
        ],
    },
    "manual-audit": {
        "title": "sipi.bot vs manual spend auditing for AI agents — sipi.bot",
        "desc": "Compare manual end-of-month spend review to real-time automated guardrails. sipi.bot catches the overage during the transaction; manual audit catches it 30 days later.",
        "body": """<span class="tag">Comparison</span>
<h1>sipi.bot vs manual spend auditing: real-time guardrails beat the month-end surprise</h1>
<p class="lead">Reviewing agent spending at the end of the month means you discover a $3,000 overage 30 days after it happened. sipi.bot catches it during the transaction, when you can still do something about it.</p>

<h2>The month-end surprise</h2>
<p>Manual audit workflows — export the Stripe log, filter by agent key, review in a spreadsheet — catch problems after the money is gone. The agent already bought the GPU time, the ad spend, the API credits. You can ask for a refund; you can't undo the spend.</p>

<table class="cmp"><thead><tr><th>Dimension</th><th>Manual month-end audit</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>When you learn about a problem</td><td>Up to 30 days after the spend</td><td>During the transaction, before the money moves</td></tr>
<tr><td>What you can do about it</td><td>Request a refund, adjust next month's budget</td><td>Block the spend outright or flag it for human review</td></tr>
<tr><td>Runaway-loop detection</td><td>Impossible — 40 small buys look like normal usage in a monthly log</td><td>Velocity rules catch it in real time, on the 11th request</td></tr>
<tr><td>Human effort</td><td>Hours of spreadsheet work every month, per agent</td><td>Zero for APPROVED, a few clicks for FLAGGED</td></tr>
<tr><td>Accuracy</td><td>As good as the person doing the audit</td><td>Deterministic rules that never get tired</td></tr>
<tr><td>Scalability</td><td>Breaks at 3+ agents, 50+ transactions/month</td><td>Flat $99/mo, no limit on agents or transactions</td></tr>
</tbody></table>

<h2>Shift from auditor to policy-setter</h2>
<p>Manual auditing keeps you busy but doesn't keep you safe. sipi.bot lets you set the rules once — per-transaction cap, daily total, merchant allowlist, velocity limit — and then spend your time on the exceptions (FLAGGED transactions) instead of reviewing every line item. One person can manage a fleet of 50 agents instead of spending Friday afternoons in spreadsheets.</p>""",
        "faq": [
            ("Don't I still need to audit agent spending eventually?", "You need to review — but with sipi.bot, you're reviewing exceptions (FLAGGED items), not every transaction. The firewall auto-approves routine purchases and auto-blocks dangerous ones. Your audit time drops from hours per month to minutes."),
            ("What if I want to review everything manually?", "Set the approval_threshold rule to $0 — every transaction gets FLAGGED and requires your review. But most teams find that automated rules catch the routine cases and let humans focus on the borderline decisions."),
            ("Does sipi.bot provide an audit export?", "Yes — the tamper-evident audit log is exportable. Every decision (APPROVED, BLOCKED, FLAGGED) is recorded with a timestamp, the rule that fired, and the reason. Use it for compliance, accounting, or executive reporting."),
        ],
    },
}


# ══════════════════════════════════════════════════════════════
# 5 NEW ALTERNATIVES PAGES (adding to existing x402 in public/alternatives/)
# ══════════════════════════════════════════════════════════════

ALTERNATIVES_PAGES = {
    "guardrails-ai": {
        "title": "Guardrails AI alternative for agent spend control — sipi.bot",
        "desc": "Guardrails AI validates LLM output structure. sipi.bot validates agent spend decisions. If your agent spends money, Guardrails AI needs a spend firewall partner — here's why.",
        "body": """<span class="tag">Alternative</span>
<h1>Guardrails AI alternative: spend control for autonomous agents</h1>
<p class="lead">Guardrails AI is excellent at validating LLM output — structured JSON, regex patterns, toxicity checks. It doesn't validate whether your agent should spend $500 on GPU time. sipi.bot fills that gap.</p>

<h2>Output validation vs spend validation</h2>
<p>Guardrails AI sits in the LLM output pipeline, checking that the model returns valid JSON, stays within a word limit, or doesn't produce toxic text. When your agent generates a spend action — "buy $500 of GPU time from runpod.io" — Guardrails AI can validate the JSON format of that action. It cannot validate whether the spend itself should happen.</p>
<p>sipi.bot evaluates the decision: is this amount under the per-transaction cap? Is this merchant allowed? Have we hit the daily total? Is the spend happening at 3am against policy? The two tools validate different things and belong at different points in the agent pipeline.</p>

<h2>Use both together</h2>
<p>The recommended stack: Guardrails AI validates the agent's output format and content safety. sipi.bot validates the agent's spend decisions against your financial policy. One keeps your agent's behavior safe; the other keeps your bank account safe.</p>""",
        "faq": [
            ("Can Guardrails AI validate spend decisions?", "Guardrails AI can validate the structure of a spend action (is the amount a number? is the merchant a string?) but not the policy question (is this vendor allowed? is the amount over the daily cap?). sipi.bot handles the policy layer."),
            ("Do sipi.bot and Guardrails AI conflict?", "No. They operate at different stages. Guardrails AI checks the output format; sipi.bot checks the spend decision. A typical flow: agent generates output → Guardrails validates format → agent proposes spend → sipi.bot approves or blocks."),
            ("Which should I implement first?", "If your agent can spend money, implement sipi.bot first — the financial risk is immediate and irreversible. Add Guardrails AI for output quality once the spend guardrail is in place."),
        ],
    },
    "nvidia-nemo-guardrails": {
        "title": "NVIDIA NeMo Guardrails alternative for agent transaction control — sipi.bot",
        "desc": "NeMo Guardrails keeps conversations on rails. sipi.bot keeps spending on rails. Compare conversational guardrails to financial guardrails for AI agents.",
        "body": """<span class="tag">Alternative</span>
<h1>NeMo Guardrails alternative: spend firewalls for AI agents</h1>
<p class="lead">NVIDIA NeMo Guardrails defines what your agent can say. sipi.bot defines what your agent can spend. Two guardrail systems, two different threat surfaces, one safe agent deployment.</p>

<h2>Dialog rails vs spend rails</h2>
<p>NeMo Guardrails uses Colang — a modeling language for conversational boundaries — to keep agents from going off-topic, making promises they shouldn't, or revealing sensitive data. It operates in the dialog layer. sipi.bot operates in the transaction layer: when the agent reaches for a payment tool, the firewall evaluates the spend against your rules before a dollar moves.</p>

<table class="cmp"><thead><tr><th>What it guards</th><th>NeMo Guardrails</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>Conversation boundaries</td><td>Yes — topic rails, jailbreak prevention, fact-checking</td><td>No — this is the dialog layer</td></tr>
<tr><td>Tool-use safety</td><td>Limited — can define tool invocation rules</td><td>Yes — every spend action is evaluated before execution</td></tr>
<tr><td>Financial policy enforcement</td><td>No — not designed for transaction rules</td><td>Yes — per-tx caps, daily totals, velocity, merchant rules</td></tr>
<tr><td>Human-in-the-loop spend review</td><td>No</td><td>Yes — FLAGGED decisions go to a human approval queue</td></tr>
</tbody></table>

<h2>They compose, they don't compete</h2>
<p>NeMo Guardrails manages what your agent says and the guardrails around its conversational behavior. sipi.bot manages what your agent buys. An agent with both is safe in conversation and safe in spending. An agent with only NeMo Guardrails can say all the right things while draining your cloud budget.</p>""",
        "faq": [
            ("Can NeMo Guardrails control agent spending?", "NeMo Guardrails can define rules around tool invocation — e.g., 'don't call the buy tool more than 5 times per conversation' — but it does not have built-in financial primitives like daily caps, merchant allowlists, or human approval queues. sipi.bot provides those."),
            ("Do I need both NeMo Guardrails and sipi.bot?", "If your agent both talks to users and spends money, yes. NeMo Guardrails for the conversation, sipi.bot for the transactions. They protect different surfaces."),
            ("Is sipi.bot compatible with the NeMo ecosystem?", "Yes. sipi.bot is an HTTP API call your agent makes before spending. It works with any framework, including NeMo-based agents, through the same evaluate_spend endpoint."),
        ],
    },
    "openpolicyagent": {
        "title": "Open Policy Agent alternative for AI agent spend rules — sipi.bot",
        "desc": "OPA is a general-purpose policy engine. sipi.bot is a purpose-built spend firewall for AI agents. Compare building spend rules in Rego vs using a pre-built spend-control product.",
        "body": """<span class="tag">Alternative</span>
<h1>Open Policy Agent alternative: purpose-built spend firewalls for AI agents</h1>
<p class="lead">OPA can enforce any policy you can write in Rego — including spend rules. But you have to write them, test them, and maintain them. sipi.bot ships with the spend primitives already built, tested, and integrated.</p>

<h2>The Rego tax</h2>
<p>To control agent spending with OPA, you must: (1) learn Rego, (2) model spend concepts as Rego policies — per-transaction caps, daily totals with sliding windows, velocity detection, merchant allow/block lists, time-window rules, approval thresholds — (3) write tests for every rule, (4) build a dashboard for the approval queue, (5) integrate OPA into every agent framework you use, and (6) maintain all of this forever.</p>
<p>sipi.bot does all of that out of the box. The rule types are pre-built. The dashboard ships with the product. The framework integrations — LangChain, CrewAI, OpenAI SDK, Vercel AI SDK — are written and maintained. The 53-scenario eval gym proves every rule works. The core is MIT-licensed so you can audit it.</p>

<h2>When OPA makes sense for spend control</h2>
<p>OPA is the right choice if you already run OPA across your platform, you have Rego expertise on your team, and the spend-control rules you need are simple enough to express in a few Rego policies. For most teams deploying AI agents that spend money, a purpose-built spend firewall saves weeks of engineering time and months of maintenance.</p>""",
        "faq": [
            ("Can OPA do everything sipi.bot does?", "With enough engineering effort, yes — OPA with Rego can express arbitrary policies. The question is whether you want to build a spend firewall from scratch in Rego or use a product that ships with the primitives, dashboard, and integrations already done."),
            ("Can I use OPA alongside sipi.bot?", "Yes. Use OPA for platform-wide authorization — APIs, Kubernetes admission control, data access — and sipi.bot specifically for agent spend control. They address different policy domains."),
            ("Does sipi.bot support Rego policies?", "No. sipi.bot has its own rule engine with pre-built spend-control primitives. You configure rules through the dashboard or API, not by writing Rego. If you need arbitrary policy expression in Rego, OPA is the better fit."),
        ],
    },
    "aporia-guardrails": {
        "title": "Aporia Guardrails alternative for agent transaction safety — sipi.bot",
        "desc": "Aporia monitors LLM applications in production for hallucinations and policy violations. sipi.bot monitors agent spend decisions. Two monitoring systems, two different signals.",
        "body": """<span class="tag">Alternative</span>
<h1>Aporia alternative: spend monitoring for autonomous AI agents</h1>
<p class="lead">Aporia Guardrails monitors your LLM application in production — hallucinations, PII leaks, prompt injections. sipi.bot monitors your agent's spending — over-budget transactions, blocked merchants, runaway loops. Different signals, same principle: catch problems before they cause damage.</p>

<h2>Production monitoring, two layers</h2>
<p>Aporia sits as an observability layer between your application and the LLM, monitoring every request and response for quality and safety issues. sipi.bot sits as a decision layer between your agent and its spending tools, evaluating every transaction against your financial policy.</p>

<table class="cmp"><thead><tr><th>Monitoring focus</th><th>Aporia Guardrails</th><th>sipi.bot</th></tr></thead><tbody>
<tr><td>Hallucination detection</td><td>Yes — monitors response accuracy</td><td>No</td></tr>
<tr><td>PII / sensitive data leaks</td><td>Yes — detects and blocks</td><td>No</td></tr>
<tr><td>Prompt injection detection</td><td>Yes — real-time guardrails</td><td>No</td></tr>
<tr><td>Spend policy enforcement</td><td>No</td><td>Yes — APPROVED / BLOCKED / FLAGGED per transaction</td></tr>
<tr><td>Runaway-loop protection</td><td>No</td><td>Yes — velocity rules stop retry spirals</td></tr>
<tr><td>Merchant / vendor control</td><td>No</td><td>Yes — allowlist and blocklist rules</td></tr>
</tbody></table>

<h2>Two monitors, one safe agent</h2>
<p>The best deployment uses both: Aporia watches what the agent says and the quality of its outputs; sipi.bot watches what the agent buys and the safety of its transactions. Together they cover the two biggest risks of autonomous agents — bad outputs and bad spending.</p>""",
        "faq": [
            ("Can Aporia monitor agent spending?", "Aporia can monitor the text content of spend-related outputs (e.g., checking if a purchase amount is mentioned) but it does not have financial policy enforcement — per-transaction caps, daily totals, merchant rules. sipi.bot provides those."),
            ("Are sipi.bot and Aporia competitors?", "No. They monitor different signals. Aporia focuses on LLM output quality and safety; sipi.bot focuses on spend safety. They complement each other in a production agent deployment."),
            ("Which should I set up first?", "If your agent can spend money, sipi.bot first — the financial risk is immediate. Add Aporia for output quality monitoring once the spend guardrail is in place."),
        ],
    },
    "prompt-security": {
        "title": "Prompt Security alternative for AI agent spend firewalls — sipi.bot",
        "desc": "Prompt Security protects against prompt injection and data exfiltration. sipi.bot protects against unwanted spending. Two security layers for the agent economy.",
        "body": """<span class="tag">Alternative</span>
<h1>Prompt Security alternative: spend firewalls for the agent economy</h1>
<p class="lead">Prompt Security protects your LLM from injection attacks and data leaks. sipi.bot protects your wallet from runaway agent spending. Both are guardrails — one for security, one for finance — and both belong in a production agent stack.</p>

<h2>Input security vs output security vs spend security</h2>
<p>Prompt Security sits at the input layer — inspecting prompts for injection attempts, detecting attempts to exfiltrate data, and enforcing organizational security policies on LLM usage. sipi.bot sits at the action layer — when the agent decides to spend money, the firewall evaluates the transaction before it executes.</p>

<p>A complete agent security posture has three layers:</p>
<ol>
  <li><strong>Input guardrails</strong> (Prompt Security): what goes into the model is safe and policy-compliant.</li>
  <li><strong>Output guardrails</strong> (Moderation API, Guardrails AI): what comes out of the model is safe and valid.</li>
  <li><strong>Action guardrails</strong> (sipi.bot): what the agent does — specifically, what it spends — is within your financial policy.</li>
</ol>

<p>Skip any layer and you have a gap. Prompt Security catches the injection attack that tries to trick the agent into revealing secrets; sipi.bot catches the transaction the agent makes after a successful prompt injection convinces it to buy from a malicious vendor.</p>""",
        "faq": [
            ("Does Prompt Security prevent agent overspending?", "Prompt Security prevents prompt-level attacks but does not enforce financial policy — per-transaction caps, daily totals, or merchant rules. A legitimate agent with no injection can still overspend; sipi.bot catches that."),
            ("Can a prompt injection bypass sipi.bot?", "No, because sipi.bot evaluates the transaction itself — the amount, the merchant, the category — not the prompt that generated it. Even if an injection convinces the agent to spend, the firewall blocks the transaction if it violates your rules."),
            ("How do sipi.bot and Prompt Security work together?", "They're complementary security layers. Prompt Security = protect the LLM from attacks. sipi.bot = protect your money from overspend. Both are necessary for production agents that handle sensitive data and spend real money."),
        ],
    },
}


# ═══════════════════════════════════════════════════════
# 6 TEMPLATES PAGES: prompt and workflow templates
# ═══════════════════════════════════════════════════════

TEMPLATES_PAGES = {
    "spend-guard-prompt": {
        "title": "Spend guard prompt template for AI agents — sipi.bot",
        "desc": "A reusable system prompt template that instructs your AI agent to check spend limits before every purchase. Drop into any agent framework — LangChain, CrewAI, OpenAI, Vercel AI SDK.",
        "body": """<span class="tag">Template</span>
<h1>Spend guard system prompt template</h1>
<p class="lead">Give your agent this system prompt and it will check every purchase against your spend firewall before spending a dollar. Works with any agent framework.</p>

<h2>The template</h2>
<pre>You are an autonomous agent with the ability to spend money to accomplish tasks.
Before every purchase, you MUST follow this spend-control protocol:

1. IDENTIFY the purchase: amount, merchant name, and category (compute, api, ads,
   goods, services, other).
2. CALL the spend firewall: use the spend_guard tool with the amount, merchant, and
   category. The firewall returns APPROVED, BLOCKED, or FLAGGED.
3. ACT on the decision:
   - APPROVED: proceed with the purchase.
   - BLOCKED: do NOT retry. Explain to the user why the spend was blocked and stop.
   - FLAGGED: explain to the user that the purchase requires human approval and
     that you are waiting. Do NOT attempt to buy or find an alternative payment method.

NEVER attempt to bypass the firewall by:
- Splitting a large purchase into smaller transactions.
- Using a different payment method.
- Omitting or lying about the merchant name or category.
Violations will be detected by velocity and merchant rules.</pre>

<h2>Where to put it</h2>
<p><strong>LangChain:</strong> Add to the system message in <code>ChatPromptTemplate.from_messages([("system", TEMPLATE), ...])</code>. <strong>CrewAI:</strong> Put in the agent's <code>backstory</code> parameter. <strong>OpenAI Agents SDK:</strong> Add to the <code>instructions</code> string in <code>Agent(instructions=TEMPLATE)</code>. <strong>Vercel AI SDK:</strong> Add to the <code>system</code> prop in <code>generateText({ system: TEMPLATE })</code>.</p>""",
        "faq": [
            ("Can the agent ignore this prompt?", "Strong prompt engineering reduces the risk, but for hard enforcement, wrap the actual purchase tool with sipi_guard.py (Python) or sipiGuard.ts (TypeScript). The prompt sets the policy; the code wrapper enforces it even if the model ignores the prompt."),
            ("Should I customize this template?", "Yes. Add your specific daily budget, allowed merchants, and approval process details. The template is a starting point — adapt it to your organization's policies."),
            ("Does this work with any LLM?", "Yes. The template uses plain English instructions, no model-specific syntax. Works with GPT-4, Claude, Gemini, Llama, and any other capable LLM."),
        ],
    },
    "approval-workflow": {
        "title": "Human approval workflow template for AI agent spend — sipi.bot",
        "desc": "A ready-to-use workflow template for routing FLAGGED agent transactions to a human approver. Includes the notification message, the decision prompt, and the feedback loop back to the agent.",
        "body": """<span class="tag">Template</span>
<h1>Human-in-the-loop approval workflow template</h1>
<p class="lead">When sipi.bot returns FLAGGED, you need a human to decide. This template gives you the workflow: the notification, the decision interface, and the feedback loop back to the agent.</p>

<h2>Approval notification template</h2>
<pre>🚨 AGENT SPEND REQUIRES APPROVAL

Agent: {agent_name}
Amount: ${amount} USD
Merchant: {merchant}
Category: {category}
Reason flagged: {firewall_reason}
Transaction ID: {txn_id}

View and approve/deny: https://sipi.bot/dashboard/approvals/{txn_id}

This transaction will remain pending until approved or denied.
The agent is waiting for your decision.</pre>

<h2>The decision prompt</h2>
<pre>You are reviewing a FLAGGED agent transaction. Consider:
1. Is the amount reasonable for the stated purpose?
2. Is the merchant known and trusted?
3. Does this fit within the project's budget?
4. Is this the right time for this purchase?

If APPROVED, the agent proceeds immediately.
If DENIED, the agent is told not to retry.</pre>

<h2>Feedback loop to the agent</h2>
<p>When the human approves: the agent receives "APPROVED: human reviewer {name} authorized this transaction. You may proceed." When denied: "DENIED: human reviewer {name} rejected this transaction. Do not retry. Reason: {reviewer_note}."</p>
<p>The agent reads this message as the tool result and continues or stops accordingly. No special agent code needed — the approval resolution is just another tool return value.</p>""",
        "faq": [
            ("Where do these notifications go?", "sipi.bot's dashboard shows the pending approval queue. You can add Slack/email/Discord notification by subscribing to the approval webhook or polling /api/approvals. The template shows the message format; wire it to your notification channel of choice."),
            ("What if the human doesn't respond?", "The transaction stays in FLAGGED state. The agent's spend tool returns a 'waiting for approval' message. You can set a timeout in your agent code to handle cases where the approver doesn't respond within your SLA."),
            ("Can I customize the approval criteria?", "Yes. Edit the decision prompt to reflect your organization's specific approval criteria — dollar thresholds, vendor tiers, project codes. The template is a starting point."),
        ],
    },
    "merchant-blocklist": {
        "title": "Merchant blocklist template for AI agent spend control — sipi.bot",
        "desc": "A template for configuring merchant allowlists and blocklists in sipi.bot. Control which vendors your autonomous agents can and cannot spend money with.",
        "body": """<span class="tag">Template</span>
<h1>Merchant allowlist and blocklist template</h1>
<p class="lead">Control which vendors your agents can pay by configuring allowlists and blocklists. This template covers the three strategies: open-with-exceptions, closed-with-exceptions, and tiered access.</p>

<h2>Strategy 1: Open with exceptions (blocklist)</h2>
<p>Allow all merchants except specific ones. Best for internal tools where you trust the agent but want to block known-bad vendors.</p>
<pre># Block specific merchants
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"rule_type":"merchant_block","params":{"merchants":["unknown-gpu.ru","cheap-tokens.xyz","shadow-vps.io"]},"action":"BLOCKED","label":"blocklist"}'</pre>

<h2>Strategy 2: Closed with exceptions (allowlist)</h2>
<p>Block everything except approved merchants. Best for production agents where you want explicit control over every vendor.</p>
<pre># Allow only approved merchants
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"rule_type":"merchant_block","params":{"block_all":true,"allowed":["openai.com","anthropic.com","runpod.io","modal.com","stripe.com"]},"action":"BLOCKED","label":"allowlist"}'</pre>

<h2>Strategy 3: Tiered access</h2>
<p>Allow small spends anywhere, restrict large spends to approved vendors.</p>
<pre># Tier 1: any merchant up to $50
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"per_transaction","params":{"max_amount":50},"action":"BLOCKED","label":"tier1-cap"}'

# Tier 2: approved merchants up to $500
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"per_transaction","params":{"max_amount":500,"allowed_merchants":["openai.com","runpod.io"]},"action":"BLOCKED","label":"tier2-cap"}'

# Tier 3: requires approval for anything above
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"approval_threshold","params":{"min_amount":500.01},"action":"FLAGGED","label":"tier3-approval"}'</pre>""",
        "faq": [
            ("Should I use an allowlist or a blocklist?", "Allowlists (closed-by-default) are safer for production agents where you want complete control. Blocklists (open-with-exceptions) are practical for internal tools where you trust the agent and only need to block known-bad vendors."),
            ("How do I add a merchant to the allowlist later?", "Use the dashboard or PUT /api/rules/<id> to update the allowed_merchants list. The change takes effect immediately — no restart required."),
            ("Does the merchant name need to be exact?", "Yes — the merchant field in the evaluate call must match the configured name exactly. For fuzzy matching, add multiple entries or use a prefix convention (e.g., 'google-*' if you implement custom matching)."),
        ],
    },
    "daily-budget-alert": {
        "title": "Daily budget alert template for AI agent spend — sipi.bot",
        "desc": "A template for configuring daily spending limits with alerts at 50%, 80%, and 100% thresholds. Prevent surprise bills from autonomous agent spending.",
        "body": """<span class="tag">Template</span>
<h1>Daily budget monitoring template</h1>
<p class="lead">Set a daily spending cap and get alerts as your agents approach it. This template covers the rule configuration and the alert integration.</p>

<h2>Step 1: Set the daily cap</h2>
<pre># Daily total cap — blocks after $2,000 in a calendar day (UTC)
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"rule_type":"daily_total","params":{"max_amount":2000},"action":"BLOCKED","label":"daily-cap"}'</pre>

<h2>Step 2: Add threshold alerts</h2>
<pre># Warning at 50% of daily budget
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"daily_total","params":{"max_amount":1000},"action":"FLAGGED","label":"daily-50pct-warning"}'

# Warning at 80% of daily budget  
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"daily_total","params":{"max_amount":1600},"action":"FLAGGED","label":"daily-80pct-warning"}'</pre>

<h2>Step 3: Integrate alerts</h2>
<p>Poll the SSE stream at <code>/v1/activity</code> or call <code>/api/stats</code> periodically. When the daily total crosses your thresholds, trigger a notification:</p>
<pre># In your monitoring script (Python)
import requests, json

stats = requests.get("https://sipi.bot/api/stats").json()
spent_today = stats["spent_today"]
daily_cap = 2000

if spent_today >= daily_cap * 0.5:
    send_slack_alert(f"⚠️ Agent spending at {spent_today/daily_cap:.0%} of daily ${daily_cap} cap")
if spent_today >= daily_cap * 0.8:
    send_pagerduty_alert(f"🚨 Agent spending at {spent_today/daily_cap:.0%} — approaching daily cap")
if spent_today >= daily_cap:
    send_incident_alert(f"🔴 Daily cap reached. All further agent spending is BLOCKED.")</pre>""",
        "faq": [
            ("Is the daily cap per agent or across all agents?", "The daily_total rule applies to the entire sipi.bot instance — all agents share the cap. For per-agent limits, create separate API keys and instances, or use the per_transaction rule on a per-agent basis."),
            ("When does the daily cap reset?", "At midnight UTC. The daily total is tracked in the SQLite database and resets when the calendar day changes."),
            ("Can I set different caps for different categories?", "Yes. Use the category_limit rule type to set per-category daily caps (e.g., $500/day for compute, $200/day for ads). Combine with the global daily_total for an overall cap."),
        ],
    },
    "category-limits": {
        "title": "Category-based spend limits template for AI agents — sipi.bot",
        "desc": "A template for setting spend limits by category — compute, API, ads, goods, services. Control where your agents spend, not just how much.",
        "body": """<span class="tag">Template</span>
<h1>Per-category spend limit template</h1>
<p class="lead">Limit spending by category so your agents can't blow the compute budget even if the total is under the daily cap. Set independent limits for compute, APIs, ads, goods, and services.</p>

<h2>Category limit rules</h2>
<pre># Compute: up to $500/day (GPU rentals, cloud instances)
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"category_limit","params":{"category":"compute","max_amount":500},"action":"BLOCKED","label":"compute-daily-cap"}'

# APIs: up to $300/day (LLM tokens, search APIs, data feeds)
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"category_limit","params":{"category":"api","max_amount":300},"action":"BLOCKED","label":"api-daily-cap"}'

# Ads: up to $200/day (Google Ads, Meta Ads, LinkedIn Ads)
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"category_limit","params":{"category":"ads","max_amount":200},"action":"BLOCKED","label":"ads-daily-cap"}'

# Goods: up to $100/day (physical products, hardware)
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"category_limit","params":{"category":"goods","max_amount":100},"action":"BLOCKED","label":"goods-daily-cap"}'

# Services: up to $150/day (SaaS subscriptions, professional services)
curl -X POST https://sipi.bot/api/rules \\
  -H "Authorization: Bearer $ADMIN_TOKEN" \\
  -d '{"rule_type":"category_limit","params":{"category":"services","max_amount":150},"action":"BLOCKED","label":"services-daily-cap"}'</pre>

<h2>How agents use categories</h2>
<p>Your agent passes a category string when calling the spend firewall:</p>
<pre># Python
from sipi_guard import evaluate
result = evaluate(amount=75.00, merchant="runpod.io", category="compute")

# TypeScript
import { evaluateSpend } from "./sipiGuard";
const result = await evaluateSpend({amount: 75, merchant: "runpod.io", category: "compute"});

# HTTP
curl -X POST https://sipi.bot/v1/transactions/evaluate \\
  -d '{"amount":75,"merchant":"runpod.io","category":"compute"}'</pre>

<p>Pick a category taxonomy that matches your business and document it in the agent's system prompt so every agent categorizes consistently.</p>""",
        "faq": [
            ("What categories are supported?", "sipi.bot accepts any string as a category. Common choices: compute, api, ads, goods, services, software, travel, other. Pick a taxonomy that fits your agent's spending patterns and enforce it in your agent prompts."),
            ("Do category limits replace the daily total cap?", "No, they complement it. Set a global daily_total as your hard ceiling and category limits to prevent any single category from consuming the entire budget. Both rules fire on every transaction."),
            ("Can I add custom categories?", "Yes. The category field is a free-form string. Add categories like 'training', 'inference', 'data-labeling', or any label that makes sense for your use case. Create matching category_limit rules for each."),
        ],
    },
    "team-spend-policy": {
        "title": "Team spend policy template for AI agent deployments — sipi.bot",
        "desc": "A policy document template that defines spending rules for AI agents across your organization. Covers per-transaction limits, daily caps, merchant policies, and the approval chain.",
        "body": """<span class="tag">Template</span>
<h1>Team spend policy template for AI agents</h1>
<p class="lead">Every team deploying autonomous agents needs a written spend policy. This template covers the rules, the roles, and the escalation path — ready to adapt for your organization.</p>

<h2>Section 1: Scope</h2>
<p>This policy applies to all autonomous AI agents deployed by [Organization Name] that have the ability to spend money — whether via payment APIs, cloud billing, ad platforms, or cryptocurrency transactions. It covers agents in development, staging, and production environments.</p>

<h2>Section 2: Spend limits</h2>
<h3>2.1 Per-transaction limits</h3>
<ul>
  <li>Development agents: $10 per transaction</li>
  <li>Staging agents: $100 per transaction</li>
  <li>Production agents: As defined per agent in the deployment runbook; default $500 per transaction</li>
</ul>

<h3>2.2 Daily limits</h3>
<ul>
  <li>Development environment: $50/day total across all agents</li>
  <li>Staging environment: $500/day total across all agents</li>
  <li>Production: Per-agent budget defined in deployment runbook; default $2,000/day per agent</li>
</ul>

<h3>2.3 Category limits</h3>
<ul>
  <li>Compute (GPU/cloud): $500/day</li>
  <li>API credits (LLM tokens, search): $300/day</li>
  <li>Advertising: Requires separate budget approval</li>
  <li>Goods and services: $200/day</li>
</ul>

<h2>Section 3: Approved merchants</h2>
<p><strong>Always allowed:</strong> openai.com, anthropic.com, runpod.io, modal.com, replicate.com, stripe.com</p>
<p><strong>Requires approval:</strong> Any merchant not on the always-allowed list. New merchants must be reviewed by [Security/Engineering Lead].</p>
<p><strong>Blocked:</strong> Merchants flagged by the security team. The blocklist is maintained in the sipi.bot dashboard.</p>

<h2>Section 4: Approval chain</h2>
<p>Transactions FLAGGED by the spend firewall follow this escalation path:</p>
<ol>
  <li>Under $100: Auto-approve (set approval_threshold rule to $100)</li>
  <li>$100–$500: Team lead approval (respond within 4 business hours)</li>
  <li>$500–$2,000: Engineering manager approval (respond within 1 business day)</li>
  <li>Over $2,000: Director approval with written justification from the requesting agent's operator</li>
</ol>

<h2>Section 5: Monitoring and audit</h2>
<ul>
  <li>All transactions are logged in the sipi.bot tamper-evident audit trail.</li>
  <li>Monthly spend reports are generated from the audit log and reviewed by [Finance/Engineering].</li>
  <li>Anomalies (3x normal daily spend, new merchant first spend, off-hours spend) trigger a Slack alert to #agent-spend-alerts.</li>
</ul>

<h2>Section 6: Environment configuration</h2>
<pre># Apply this policy via sipi.bot rules (example for production)
# Per-transaction cap
POST /api/rules {"rule_type":"per_transaction","params":{"max_amount":500},"action":"BLOCKED","label":"prod-tx-cap"}
# Daily total
POST /api/rules {"rule_type":"daily_total","params":{"max_amount":2000},"action":"BLOCKED","label":"prod-daily-cap"}
# Merchant allowlist  
POST /api/rules {"rule_type":"merchant_block","params":{"block_all":true,"allowed":["openai.com","anthropic.com","runpod.io","modal.com","replicate.com","stripe.com"]},"action":"BLOCKED","label":"prod-merchants"}
# Approval threshold
POST /api/rules {"rule_type":"approval_threshold","params":{"min_amount":100},"action":"FLAGGED","label":"prod-approval"}
# Velocity (anti-runaway-loop)
POST /api/rules {"rule_type":"velocity","params":{"max_per_minute":10},"action":"BLOCKED","label":"prod-velocity"}</pre>""",
        "faq": [
            ("Is this policy template enforceable?", "Yes. Every rule in Section 6 maps directly to a sipi.bot rule type. Copy the curl commands, replace the values with your limits, and the firewall enforces the policy automatically."),
            ("How do I handle exceptions to this policy?", "Use the FLAGGED decision path with an approval threshold. Transactions that need exceptions get FLAGGED, a human reviews them, and the approval (or denial) is recorded in the audit trail."),
            ("Can different teams have different policies?", "Yes. Create separate sipi.bot instances (or API keys with different rule sets) for each team. The self-hosted core is free and MIT-licensed; spin up a dedicated instance per team if needed."),
        ],
    },
}


# ══════════════════════════════════════════
# WRITE ALL PAGES
# ══════════════════════════════════════════

def write_pages(pages, subdir, tag):
    """Write pSEO pages into public/<subdir>/<slug>/index.html"""
    base = os.path.join(PUB, subdir)
    count = 0
    for slug, d in pages.items():
        canonical = f"/{subdir}/{slug}/"
        out_dir = os.path.join(base, slug)
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "index.html")
        with open(path, "w") as f:
            f.write(page(d["title"], d["desc"], canonical, d["body"], d["faq"]))
        print(f"  wrote {canonical}  ({len(open(path).read())} bytes)")
        count += 1
    print(f"  → {count} pages in /{subdir}/")
    return count


def patch_api_py():
    """Add /compare/ prefix to _serve_pseo in spendfirewall/api.py"""
    api_path = os.path.normpath(os.path.join(HERE, "..", "spendfirewall", "api.py"))
    with open(api_path) as f:
        original = f.read()

    # The prefix list line in _serve_pseo
    old_line = 'for prefix in ("/vs/", "/for/", "/learn/", "/integrations/", "/glossary/", "/use-cases/", "/faq/", "/alternatives-to/", "/benchmarks/", "/tutorials/", "/policies/", "/limits/", "/best/", "/how-to/", "/templates/", "/cost-of/"):'

    # Add /compare/ as the first prefix (alphabetical, but it's a comparison cluster)
    new_line = 'for prefix in ("/compare/", "/vs/", "/for/", "/learn/", "/integrations/", "/glossary/", "/use-cases/", "/faq/", "/alternatives-to/", "/benchmarks/", "/tutorials/", "/policies/", "/limits/", "/best/", "/how-to/", "/templates/", "/cost-of/"):'

    if old_line not in original:
        print("WARNING: old prefix line not found in api.py. Searching for approximate match...")
        # Try to find the for prefix loop
        pattern = r'for prefix in \(".*?"\):'
        matches = list(re.finditer(pattern, original))
        if not matches:
            print("ERROR: Cannot find the prefix loop in api.py. Manual patch required.")
            return False
        # Find the one inside _serve_pseo
        pseo_start = original.find("def _serve_pseo")
        for m in matches:
            if m.start() > pseo_start:
                old_line = m.group(0)
                break

    if old_line in original:
        updated = original.replace(old_line, new_line, 1)
        with open(api_path, "w") as f:
            f.write(updated)
        print("  ✓ Patched api.py: added /compare/ to _serve_pseo prefixes")
        return True
    else:
        print("  ✗ Could not find prefix line to patch in api.py")
        return False


def main():
    total = 0
    issues = []

    print("build_pseo_expansion.py — sipi.bot pSEO expansion")
    print("=" * 60)

    # 1) Write /compare/ pages
    print("\n[1/4] /compare/ pages (6 comparison pages)")
    total += write_pages(COMPARE_PAGES, "compare", "Comparison")

    # 2) Write /alternatives/ pages (5 new, adding to existing x402)
    print("\n[2/4] /alternatives/ pages (5 new alternatives — x402 already exists)")
    total += write_pages(ALTERNATIVES_PAGES, "alternatives", "Alternative")

    # 3) Write /templates/ pages
    print("\n[3/4] /templates/ pages (6 prompt/workflow templates)")
    total += write_pages(TEMPLATES_PAGES, "templates", "Template")

    # 4) Patch api.py
    print("\n[4/4] Patching api.py")
    if not patch_api_py():
        issues.append("api.py patch failed — /compare/ prefix not added to _serve_pseo")

    print("\n" + "=" * 60)
    print(f"SUMMARY: {total} pages created across 3 new clusters")
    if issues:
        print(f"ISSUES ({len(issues)}):")
        for i in issues:
            print(f"  - {i}")
    else:
        print("No issues.")
    print("\nNext steps:")
    print("  - Regenerate sitemap (scripts/ping_indexnow.py or equivalent)")
    print("  - Rebuild sitemap-index.xml to include /compare/, /alternatives/, /templates/")
    print("  - Deploy to Fly.io")


if __name__ == "__main__":
    main()
