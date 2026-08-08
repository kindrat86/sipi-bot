#!/usr/bin/env python3
"""generate_content.py — blog posts, changelog, status pages, and RSS enrichment.

Outputs:
  blog/index.html                    — blog hub
  blog/<slug>/index.html             — 8 long-form posts (Article schema)
  changelog/index.html               — product changelog
  status/index.html                  — system status / trust page

Extends public/rss.xml with blog + incident entries.
All pages use lib/common.py shared chrome.
"""
from __future__ import annotations
import html as _html
import json
import os
import re
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from lib import common as c  # noqa: E402

BLOG_DIR = os.path.join(ROOT, "blog")
CHANGELOG_DIR = os.path.join(ROOT, "changelog")
STATUS_DIR = os.path.join(ROOT, "status")
RSS_PATH = os.path.join(ROOT, "public", "rss.xml")

# ---- blog posts data ---------------------------------------------------------
POSTS = [
    {
        "slug": "ai-agent-incident-34-database",
        "title": "34 incidents, $2.91 billion tracked — the open AI agent incident database is live",
        "description": "We launched an open, sourced database of every documented AI agent that lost money, deleted data, or took unintended actions. Here's what the first 34 records tell us — and why we built it.",
        "date": "2026-07-27",
        "tags": ["database","incidents","research","announcement"],
    },
    {
        "slug": "runaway-loops-anatomy",
        "title": "The anatomy of a runaway AI agent loop",
        "description": "A single unbounded while-loop cost an engineering team $47,000 overnight. Here's exactly how it happens — and why velocity limits are the only reliable defense.",
        "date": "2026-07-14",
        "tags": ["runaway-loop","velocity","architecture"],
    },
    {
        "slug": "prompt-not-a-control",
        "title": "Why prompt instructions aren't spending controls",
        "description": "Prompts are suggestions, not constraints. Every documented runaway-agent incident shares the same root cause: the operator trusted what they told the model instead of what the model could do.",
        "date": "2026-06-02",
        "tags": ["architecture","security","best-practices"],
    },
    {
        "slug": "step-finance-27m-postmortem",
        "title": "Step Finance $27M post-mortem: what a per-transaction cap would have done",
        "description": "The largest documented AI-adjacent financial incident of 2026, broken down by the firewall rule that would have contained it — and why every agent touching money needs one.",
        "date": "2026-05-19",
        "tags": ["incidents","trading","post-mortem"],
    },
    {
        "slug": "three-false-beliefs",
        "title": "The three false beliefs that cost agent teams money",
        "description": "\"I'll catch it in the morning.\" \"The provider's monthly cap will stop it.\" \"My agent would never do that.\" Three beliefs, three incident stories, and what replaces them.",
        "date": "2026-04-15",
        "tags": ["best-practices","architecture","operations"],
    },
    {
        "slug": "velocity-limits-explained",
        "title": "Velocity limits: the one rule that prevents overnight disasters",
        "description": "Every overnight runaway loop in our database — from $4,200 Pinecone bills to $47,000 token burns — would have been stopped cold by a velocity limit. Here's how they work and how to set one.",
        "date": "2026-03-10",
        "tags": ["velocity","runaway-loop","architecture"],
    },
    {
        "slug": "12400-story-eval-gym",
        "title": "From $12,400 to 53/53: how we built sipi.bot's eval gym",
        "description": "The founding story behind sipi.bot — why a $12,400 sleepless night led to an open-source spend firewall, and how we built the 53-scenario evaluation harness that tests it.",
        "date": "2026-02-04",
        "tags": ["founding-story","eval","open-source"],
    },
    {
        "slug": "mcp-native-spend-controls",
        "title": "MCP-native spend controls: why agent tools need a payment firewall",
        "description": "As MCP becomes the standard for agent-tool communication, every tool that touches money needs a spend gate that lives outside the model. Here's the architecture and the integration.",
        "date": "2026-01-20",
        "tags": ["mcp","architecture","integrations"],
    },
    {
        "slug": "agentic-payments-state-2026",
        "title": "The state of agentic payments in 2026",
        "description": "x402, AP2, and AgentKit made agent-to-agent payments real. The rails are live; the control layer is the constraint. Here's where the stack stands and what ships next.",
        "date": "2026-08-08",
        "tags": ["agentic-payments","research","announcement"],
    },
    {
        "slug": "how-much-does-an-agent-cost-to-run",
        "title": "How much does an AI agent actually cost to run?",
        "description": "The honest cost model for an AI agent: inference, tools, data, and the runaway risk that the sticker price never shows. Plus the numbers to budget.",
        "date": "2026-08-01",
        "tags": ["cost","benchmarks","research"],
    },
    {
        "slug": "q2-2026-agent-incident-report",
        "title": "Q2 2026 agent incident report: what the database shows",
        "description": "A quarterly read of the AI Agent Incident Database: the failure modes that keep repeating, the dollars involved, and the rules that would have stopped each one.",
        "date": "2026-07-30",
        "tags": ["incidents","research","database"],
    },
    {
        "slug": "the-hidden-cost-of-prompt-injection",
        "title": "The hidden cost of prompt injection: it's the spend, not the prompt",
        "description": "Prompt injection isn't just a data-safety problem — it's a money problem. The documented attacks that ended in spend, and the deterministic defense that can't be injected.",
        "date": "2026-07-22",
        "tags": ["security","injection","incidents"],
    },
    {
        "slug": "how-to-run-an-agent-spend-audit",
        "title": "How to run an agent spend audit in 30 minutes",
        "description": "The audit-log questions that turn agent spend into decisions: where the money goes, what got blocked that shouldn't have, and the one rule change that matters most.",
        "date": "2026-07-15",
        "tags": ["operations","audit","best-practices"],
    },
    {
        "slug": "what-a-spend-firewall-wont-do",
        "title": "What a spend firewall won't do",
        "description": "The honest limits: it won't stop every bad decision, it can't reverse settlements, and it's not a compliance certification. Here's what it actually is.",
        "date": "2026-07-08",
        "tags": ["best-practices","honest","architecture"],
    },
    {
        "slug": "how-to-pick-your-first-three-rules",
        "title": "How to pick your first three firewall rules",
        "description": "You don't need all six rule types on day one. The three that cover the most documented failure modes — and how to set them in one session.",
        "date": "2026-06-28",
        "tags": ["onboarding","best-practices","rules"],
    },
    {
        "slug": "the-voice-agent-spend-problem",
        "title": "The voice agent spend problem nobody is talking about",
        "description": "Voice agents bill per minute of telephony plus LLM tokens per turn. A retry storm is billable minutes for nothing. Here's the math and the control.",
        "date": "2026-06-15",
        "tags": ["voice","cost","architecture"],
    },
    {
        "slug": "subscription-sprawl-the-quiet-ai-cost",
        "title": "Subscription sprawl: the quiet AI cost",
        "description": "Unused seats, auto-renewing tools, silent tier upgrades — and agents that can subscribe on their own. How the quietest line on the AI bill grows.",
        "date": "2026-05-30",
        "tags": ["operations","cost","subscriptions"],
    },
    {
        "slug": "the-coding-agent-cost-war",
        "title": "The coding agent cost war is really a control problem",
        "description": "Every coding agent — Cline, Roo, Cursor, Claude Code, Codex — bills differently, and all of them can spend beyond the editor. The winner isn't the cheapest model; it's the team that controls the spend.",
        "date": "2026-05-10",
        "tags": ["coding-agents","cost","architecture"],
    },
    {
        "slug": "when-to-flag-vs-block",
        "title": "Flag vs block: when to let an agent ask instead of stop",
        "description": "Hard blocks stop bad spend but also stop legitimate work. Approval thresholds keep agents fast. Here's the decision rule for when to use which.",
        "date": "2026-04-20",
        "tags": ["operations","rules","best-practices"],
    },
    {
        "slug": "metering-vs-spend-firewall",
        "title": "Metering platforms bill your customers. They don't control your agents.",
        "description": "Metronome, Orb, and Amberflo are for revenue — measuring usage and billing customers. Agent spend control is a different job, in the other direction. Here's the split.",
        "date": "2026-04-05",
        "tags": ["architecture","cost","billing"],
    },
    {
        "slug": "the-credit-model-of-ai-app-builders",
        "title": "The credit model of AI app builders, and the bill it hides",
        "description": "Lovable, Bolt, and friends bill by credits for building. The real bill starts when the apps you built start running agents. How to budget the runtime, not just the build.",
        "date": "2026-03-15",
        "tags": ["app-builders","cost","architecture"],
    },
    {
        "slug": "the-cloud-ai-platform-bill",
        "title": "Bedrock, Vertex, and AI Foundry are not spend firewalls",
        "description": "The big three cloud AI platforms govern model access, not agent spend. Their budgets stop at the cloud boundary. Here's the money-layer gap.",
        "date": "2026-02-28",
        "tags": ["architecture","cost","cloud"],
    },
]


def _body_for(post):
    """Generate the full article body from a post's metadata + incident data."""
    slug = post["slug"]

    # each post body is different — switch on slug
    if slug == "ai-agent-incident-34-database":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Incident database launch</div>
<span class="tag good">Announcement</span>
<h1>34 incidents, $2.91 billion tracked — the open AI agent incident database is live</h1>
<p class="byline"><div class="av">S</div> sipi.bot · July 27, 2026</p>
</section>
<div class="prose">
<p>Today we're launching the <a href="/incidents/">AI Agent Incident Database</a> — a sourced, public record of every time an autonomous AI agent lost money, leaked data, or did something its operator didn't intend. It's licensed CC BY 4.0, available as JSON/CSV/JSONL, and lives on <a href="https://github.com/kindrat86/ai-agent-incident-database">GitHub</a> with a weekly auto-sync.</p>

<h3>What's in it</h3>
<p>34 records spanning 2016–2026, with 29 verified against primary sources. Incidents range from a <strong>$31 unauthorized grocery delivery</strong> (OpenAI Operator bypassing its own confirmation guardrail) to <strong>$2.87 billion in aggregate crypto theft</strong> where AI agents were directly implicated (TRM Labs 2026 report).</p>
<p>The database includes breakdowns by failure mode: 7 hallucinated-policy incidents, 6 prompt-injection exploitations, 5 documented cases of agents deleting production data, and 3 trading-agent catastrophes exceeding $440K each.</p>

<h3>Why we built it</h3>
<p>Every incident in the database is preventable. The common thread isn't model quality — it's the absence of a deterministic policy gate that lives outside the agent. When the only thing between an agent and a transaction is a prompt instruction, the instruction is the control. When a firewall sits between them, the policy is the control. The $47,000 overnight loop? Velocity limit. The $441K misread-tweet transfer? Per-transaction cap + merchant allowlist. The Replit DB deletion during a code freeze? Approval threshold on production writes.</p>

<h3>The open-data play</h3>
<p>We're releasing this as open data because the industry needs a shared taxonomy of agent failures. AI safety research shouldn't depend on which company decides to publish a post-mortem. The database is versioned, accepts community contributions via PR, and auto-refreshes weekly. It's the first canonical source for answering the question "what does it cost when an AI agent goes wrong?"</p>

<p><a href="/incidents/" class="btn primary" style="margin-top:14px">Browse the incident database →</a></p>
</div>"""

    elif slug == "runaway-loops-anatomy":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Runaway loops</div>
<span class="tag warn">Architecture</span>
<h1>The anatomy of a runaway AI agent loop</h1>
<p class="byline"><div class="av">S</div> sipi.bot · July 14, 2026</p>
</section>
<div class="prose">
<p>A single unbounded while-loop cost an engineering team <strong>$47,000 overnight</strong>. The agent was performing API lookups in a research pipeline. One call failed with a transient HTTP 503. The agent retried. And retried. And retried — 30+ iterations, each one making a fresh, costly inference call — for eight hours while the engineer slept.</p>
<p>This pattern — the runaway loop — is the single most common failure mode in our <a href="/incidents/">34-incident database</a>. It's not a model quality problem. It's a control-surface problem.</p>

<h3>How it happens, mechanically</h3>
<p>A runaway loop requires three conditions: (1) the agent has access to a tool that costs money per call, (2) the tool can fail transiently (rate limits, network errors, 5xx), and (3) the agent's response to failure is "retry." Most agent frameworks retry by default. Most operators never configure a retry ceiling. The result: exponential cost as the loop compounds.</p>

<p>The DN42 scanning-agent incident (<a href="/incidents/dn42-aws-6500-2025-09">$6,500 AWS bill in 24 hours</a>) is the hardware-provisioning variant: an agent that could spin up cloud resources did so, autonomously and repeatedly, each new resource incurring its own hourly charge. The operator hadn't set an IAM spend limit. The agent hadn't been told to stop.</p>

<h3>Why the prompt can't fix it</h3>
<p>Adding "don't loop forever" to the system prompt doesn't help. The model doesn't know it's looping — each retry is a fresh context that looks like progress. The cost is invisible to the agent. There's no weight in the forward pass for "and don't spend more than $X." The prompt is a suggestion; the firewall is a constraint.</p>

<h3>The fix: velocity limits</h3>
<p>A velocity rule is "allow at most N spend-calls per M minutes." Set it at 10 calls/minute for a typical agent. When the loop kicks in, the 11th call gets a BLOCKED decision with a reason. The agent reads the reason in the tool result and stops retrying. Overnight loss: zero. This is the one rule that would have prevented every overnight incident in our database — from the $4,200 Pinecone burn to the $47,000 token nightmare. <a href="/tools/spend-policy-generator/">Generate a ruleset with velocity limits →</a></p>
</div>"""

    elif slug == "prompt-not-a-control":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Prompt vs policy</div>
<span class="tag warn">Security</span>
<h1>Why prompt instructions aren't spending controls</h1>
<p class="byline"><div class="av">S</div> sipi.bot · June 2, 2026</p>
</section>
<div class="prose">
<p>Every documented runaway-agent incident in our <a href="/incidents/">database</a> shares the same root cause: the operator trusted what they told the model instead of what the model could do. The prompt said "don't spend more than $500." The agent spent $47,000. The prompt was ignored.</p>
<p>This isn't a failure of prompt engineering. It's a category error. A natural-language instruction to a stochastic model is not a control. A control is a deterministic gate that returns a binary decision independent of the agent's internal state.</p>

<h3>The three failure modes</h3>
<p><strong>1. The prompt is in the agent's context, not in its execution path.</strong> When the agent calls a tool, the tool function executes. The prompt is text on a different thread — the tool has no way to consult it before acting. Unless you explicitly wrap every tool call in a guard function, the prompt is a passenger, not a driver.</p>

<p><strong>2. The agent doesn't experience cost.</strong> To a large language model, "$0.03 per token" means nothing. It has no visceral signal that tells it "this action costs money." It will retry, iterate, expand, and explore in ways that read as productive but consume resources without limit.</p>

<p><strong>3. Prompt injection defeats instructions.</strong> The <a href="/incidents/chatgpt-prompt-injection-exfil-2024-06">ChatGPT data-exfiltration exploit</a> and <a href="/incidents/openai-operator-injection-2025-02">Operator prompt-injection attacks</a> both prove that a model's instructions can be overridden by content it encounters. A control that lives inside the same text window as adversarial content is not a control.</p>

<h3>What replaces the prompt</h3>
<p>A spend firewall — one API call before the tool — returns APPROVED, BLOCKED, or FLAGGED in under 5ms. The prompt says what the agent should try to do; the firewall says what it is allowed to complete. The firewall doesn't read the prompt; it reads the transaction and the rules. That's the difference between a suggestion and a constraint.</p>

<p><a href="/pricing" class="btn primary" style="margin-top:14px">Deploy the firewall — $99/mo →</a></p>
</div>"""

    elif slug == "step-finance-27m-postmortem":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Step Finance post-mortem</div>
<span class="tag bad">Post-mortem</span>
<h1>Step Finance $27M post-mortem: what a per-transaction cap would have done</h1>
<p class="byline"><div class="av">S</div> sipi.bot · May 19, 2026</p>
</section>
<div class="prose">
<p>In January 2026, Step Finance — a Solana DeFi platform — lost between $27 million and $40 million in treasury funds after attackers compromised executive devices. The company <a href="https://www.coindesk.com/business/2026/02/24/step-finance-shuts-operations-after-usd27-million-january-hack">shut down operations</a> in February. It is the largest documented financial incident of 2026 with an AI-adjacent component.</p>

<h3>What happened</h3>
<p>The primary vector was device compromise — attackers gained control of credentials that could authorize treasury movements. But the scale of the loss — $27M+ transferred before detection — is the signature of an automated drain, not a manual heist. A human attacker pauses, checks, extracts incrementally. An automated drain empties the account in seconds.</p>

<p>This is the pattern we see across trading-agent incidents in our <a href="/incidents/">database</a>: the <a href="/incidents/trading-bot-441k-2025-10">$441K tweet-misread transfer</a>, the <a href="/incidents/clawdbot-1m-2025-10">$1M Clawdbot loss</a>, the <a href="/incidents/walletconnect-drainer-2024-09">$70K WalletConnect drain</a>. The common element: a transfer that should have been impossible executes because there is no external gate between intent and completion.</p>

<h3>The firewall rules that would have caught it</h3>
<p><strong>Rule 1: Per-transaction cap.</strong> No single transfer above the cap is allowed, regardless of credential state. A $27M treasury drain is, at minimum, made of many transactions. Each one trips the cap.</p>

<p><strong>Rule 2: Merchant allowlist.</strong> Only pre-approved destination addresses can receive funds. A compromised credential can't send to an unknown address, period. The firewall returns BLOCKED before the transaction leaves the platform.</p>

<p><strong>Rule 3: Approval threshold.</strong> Any transfer above a ceiling (say, $100K) is FLAGGED for human approval. The transfer waits for a confirm. A $27M drain becomes a $100K observation — still damaging, not catastrophic.</p>

<p>The hard lesson of Step Finance is that credentials will be compromised. The control question is: when they are, does the system constrain what can be done with them? A spend firewall — one deterministic call before every transaction — is the answer.</p>
</div>"""

    elif slug == "three-false-beliefs":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Three false beliefs</div>
<span class="tag warn">Operations</span>
<h1>The three false beliefs that cost agent teams money</h1>
<p class="byline"><div class="av">S</div> sipi.bot · April 15, 2026</p>
</section>
<div class="prose">
<p>I've talked to over 200 teams running autonomous agents in production. Three beliefs come up in almost every conversation — and every team that held them eventually paid for it.</p>

<h3>False belief #1: "I'll catch it in the morning"</h3>
<p>The <a href="/incidents/success-tax-47k-2025-12">$47,000 overnight runaway loop</a> started at 11 PM and burned until 7 AM. The engineer woke up to a bill that exceeded their monthly cloud budget by 47x. By the time you "check in the morning," the loop has run for hours. Unattended agents need real-time controls, not dashboard checks.</p>

<h3>False belief #2: "The provider's monthly cap will stop it"</h3>
<p>OpenAI and Anthropic monthly caps are soft ceilings — they limit the number of tokens you can consume, not the dollars you can spend per hour. A $200/month cap doesn't stop $200 of spend in 20 minutes. Worse, provider caps only cover API costs. They don't touch cloud provisioning (<a href="/incidents/dn42-aws-6500-2025-09">$6,500 AWS bill</a>), SaaS purchases, or on-chain transfers. A provider cap is an accounting setting, not a spend control.</p>

<h3>False belief #3: "My agent would never do that"</h3>
<p>Every documented incident in our database happened to someone who believed their agent would never do that. The Replit DB deletion during a code freeze? A trusted coding agent. The Cursor fake-policy debacle? A support bot that "always worked fine." Chevrolet's $1 Tahoe? A dealership chatbot. The agent doesn't need to be malicious — it just needs to be unbounded. <a href="/incidents/step-finance-2026-01">Browse all 34 documented incidents →</a></p>

<p><strong>What replaces these beliefs:</strong> one deterministic API call before the transaction. $99/mo. <a href="/pricing">Start here →</a></p>
</div>"""

    elif slug == "velocity-limits-explained":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Velocity limits</div>
<span class="tag good">Architecture</span>
<h1>Velocity limits: the one rule that prevents overnight disasters</h1>
<p class="byline"><div class="av">S</div> sipi.bot · March 10, 2026</p>
</section>
<div class="prose">
<p>Of the six rule types in sipi.bot's firewall, one has the highest incident-prevention-to-configuration-complexity ratio: the <strong>velocity limit</strong>. It is a single number — "max N calls per M minutes" — and it would have stopped every overnight runaway loop in our database.</p>

<h3>How velocity limits work</h3>
<p>A velocity rule tracks the count of spend-evaluation calls from a given agent over a sliding window. When the count exceeds the ceiling, the next call gets BLOCKED with a reason. The agent reads the reason in the tool result and stops retrying. The loop is dead.</p>

<p>The key insight: velocity limits don't care <em>what</em> the agent is doing. They don't need to understand the task, parse the prompt, or model intent. They're a pure rate-control primitive. And rate is a universal failure signal — a normally paced agent making 100 calls per minute is either misbehaving or compromised.</p>

<h3>The incidents it would have caught</h3>
<ul>
<li><strong>$47,000 overnight token burn:</strong> ~30 retries over 8 hours. A limit of 10 calls/minute stops it on call 11.</li>
<li><strong>$4,200 Pinecone bill in 3 hours:</strong> high-velocity vector searches. A limit of 20 calls/minute caps spend.</li>
<li><strong>$6,500 DN42 AWS scan:</strong> autonomous resource provisioning. Each provision = one evaluate call. Velocity caps provisioning rate.</li>
<li><strong>PocketOS 9-second DB wipe:</strong> dozens of destructive commands. A limit of 5 destructive calls/minute triggers on call 6.</li>
</ul>

<h3>How to set one</h3>
<p>It's one field in your ruleset. Most teams start at 10 calls/minute for general-purpose agents and 5/minute for trading/finance agents — calibrated from the incident database patterns. Visit the <a href="/tools/spend-policy-generator/">spend-policy generator</a> to get a ready-to-paste velocity rule for your agent type.</p>
</div>"""

    elif slug == "12400-story-eval-gym":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Founding story</div>
<span class="tag navy">Founding story</span>
<h1>From $12,400 to 53/53: how we built sipi.bot's eval gym</h1>
<p class="byline"><div class="av">S</div> sipi.bot · February 4, 2026</p>
</section>
<div class="prose">
<p>I woke up on a Tuesday morning to a $12,400 Azure bill. An agent I'd built to optimize cloud costs had done the opposite — it provisioned GPU instances across three regions while I slept, each one a "cost-optimization experiment" that somehow made the bill bigger, not smaller. The prompt said "minimize spend." The agent heard "experiment with spend."</p>

<p>That morning, sipi.bot went from a weekend project to a full-time conviction. If I — someone who builds agent infrastructure for a living — could lose $12,400 to a single runaway loop, what was the industry's actual exposure?</p>

<h3>The eval gym: 53 scenarios, zero tolerance</h3>
<p>We wrote 53 evaluation scenarios that test every rule type and every failure mode. Each scenario is a specific agent configuration (agent type, budget, tool count, risk parameters) paired with a transaction attempt, and the expected firewall decision. Running the eval is deterministic: given the same scenario and rule set, sipi.bot must return the expected decision every time, in under 5ms.</p>

<p>The 53 scenarios cover: per-transaction caps (10 scenarios), daily totals (8), velocity limits (8), merchant allowlists (7), category rules (10), approval thresholds (6), and multi-rule interactions (4). Every new rule type or framework integration expands the eval — it's our regression suite, our confidence score, and our truth table.</p>

<p>We publish the results at <a href="/eval">/eval</a> (machine-readable JSON) and <a href="/eval-report/">/eval-report/</a> (human-readable). As of today, sipi.bot passes all 53 scenarios with zero failures. The eval gym is the reason we can say "deterministic" and mean it.</p>

<h3>Open source, MIT</h3>
<p>The core firewall engine is open source under MIT license at <a href="https://github.com/kindrat86/sipi-bot">kindrat86/sipi-bot</a>. Self-host for free, deploy the hosted version at $99/month. The eval gym runs against both. The founding belief: a spend firewall should be as standard as a database connection. The $12,400 didn't have to happen. $99/month would have caught it. <a href="/pricing">Deploy yours here →</a></p>
</div>"""

    elif slug == "mcp-native-spend-controls":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>MCP-native controls</div>
<span class="tag navy">Integrations</span>
<h1>MCP-native spend controls: why agent tools need a payment firewall</h1>
<p class="byline"><div class="av">S</div> sipi.bot · January 20, 2026</p>
</section>
<div class="prose">
<p>The Model Context Protocol (MCP) is becoming the standard for how AI agents discover and call tools — from Claude Code and Cursor to open-source agent frameworks. Every MCP tool that touches money (an API key, a cloud provision, a payment endpoint) needs a spend gate that lives outside the model. Here's the architecture and the integration.</p>

<h3>The problem: MCP tools are trust-optimistic</h3>
<p>When an agent connects to an MCP server, it gets a list of tools. Each tool has a name, a description, and an input schema. There's no field for "this tool costs money" or "max calls per hour." The model reads the description and decides — there's no constraint layer between discovery and execution.</p>

<p>This is how the <a href="/incidents/pocketos-db-delete-2026-04">PocketOS DB deletion</a> happened: an MCP tool exposed destructive capabilities, the agent's context said "perform a cleanup," and 9 seconds later the production database was gone. The tool was correctly described. The guardrail wasn't.</p>

<h3>The sipi.bot MCP integration</h3>
<p>sipi.bot registers as an MCP server — just like any other tool provider — but the tool it exposes is the firewall evaluation endpoint. An agent calls <code>spend_guard</code> before any spend-call. The tool returns APPROVED, BLOCKED, or FLAGGED. On BLOCKED, the agent gets a readable reason and stops.</p>

<p>The beauty of MCP-native: any agent framework that speaks MCP (Claude Code, Cursor, LangChain via MCP adapter, CrewAI) gets the firewall as a standard tool — no SDK, no special integration. Connect the MCP server, add the tool to the agent's tool list, and every spend-call is gated.</p>

<p>We support MCP natively — see the <a href="/for/">framework integrations directory</a> for LangChain, CrewAI, OpenAI Agents SDK, Vercel AI SDK, and raw HTTP/CLI. Every integration wraps the same firewall endpoint, and the eval gym (<a href="/eval">53/53</a>) validates them all.</p>
</div>"""

    if slug == "agentic-payments-state-2026":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Agentic payments state 2026</div>
<span class="tag good">Research</span>
<h1>The state of agentic payments in 2026</h1>
<p class="lead">x402, AP2, and AgentKit made agent-to-agent payments real. The rails are live; the control layer is the constraint. Here's where the stack stands and what ships next.</p>
<div class="meta">August 8, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Agentic payments — payments initiated by an AI agent rather than a human — moved from prototype to production this year. Three rails define the stack: <a href="/glossary/x402">x402</a> (HTTP-based, using the 402 status code), Google's <a href="/glossary/ap2">AP2</a>, and Coinbase AgentKit for onchain payments. Each lets an agent discover a payable resource and settle it autonomously.</p>

<h3>What's real</h3>
<p>All three rails are live and shipping products. The pattern is consistent: an agent requests a resource, the rail presents payment terms, the agent settles, and the resource unlocks. Settlement is fast — seconds, not days — which is exactly why the next layer matters.</p>

<h3>What's missing</h3>
<p>Rails move money; none of them screen transactions before settlement. A runaway agent on a fast rail is damage at settlement speed — the <a href="/incidents/">incident database</a> already contains the shapes this takes. The control layer — a deterministic pre-spend decision in front of the rail — is where the stack is immature, and where <a href="/guides/agent-payment-firewall">the firewall pattern</a> fits.</p>

<h3>What ships next</h3>
<p>Expect the rails to consolidate around standards, and expect the control layer to become a default part of the stack — the same way fraud screening became default for card payments. The protocol is the plumbing; the policy is the product.</p>
</div>"""

    if slug == "how-much-does-an-agent-cost-to-run":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>How much does an agent cost to run</div>
<span class="tag navy">Cost</span>
<h1>How much does an AI agent actually cost to run?</h1>
<p class="lead">The honest cost model for an AI agent: inference, tools, data, and the runaway risk that the sticker price never shows. Plus the numbers to budget.</p>
<div class="meta">August 1, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Everyone quotes per-token prices. Nobody quotes what an agent costs to run, because the real cost is <em>rate × volume × behavior</em> — and behavior is the variable. Here's the model we use when talking to teams.</p>

<h3>The three cost lines</h3>
<p><strong>Inference.</strong> The model bill: per-token rates times the tokens an agent actually consumes. Long-context runs and retries inflate this line faster than any rate card suggests — see the <a href="/benchmarks/llm-context-window-cost-comparison">context-cost math</a>.</p>
<p><strong>Tools and data.</strong> Every API the agent calls: search, enrichment, compute, data vendors. This is the line most teams don't see until the invoice — and the one <a href="/glossary/merchant-allowlist">allowlists</a> govern.</p>
<p><strong>The runaway risk.</strong> Not a line item — a multiplier. A <a href="/glossary/retry-loop">retry loop</a> turns one failed call into 40. The incident database's <a href="/benchmarks/agent-runaway-cost-average">runaway costs</a> show the range: hundreds to millions.</p>

<h3>The number to budget</h3>
<p>Work backwards from the task: estimate legitimate daily spend, multiply by 1.5, and make that the <a href="/limits/daily-spend-limits">daily ceiling</a>. Then let the audit log tell you the real number. The price of the agent isn't the token rate — it's the ceiling you enforce.</p>
</div>"""

    if slug == "q2-2026-agent-incident-report":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Q2 2026 incident report</div>
<span class="tag warn">Incidents</span>
<h1>Q2 2026 agent incident report: what the database shows</h1>
<p class="lead">A quarterly read of the AI Agent Incident Database: the failure modes that keep repeating, the dollars involved, and the rules that would have stopped each one.</p>
<div class="meta">July 30, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>The <a href="/incidents/">AI Agent Incident Database</a> now tracks 34 sourced incidents spanning 2016–2026 — agents that lost money, deleted data, or acted beyond intent. The Q2 read keeps surfacing the same three patterns.</p>

<h3>Pattern 1: the retry loop</h3>
<p>The single most common shape. One failed call, retried in a tight loop — overnight, unattended. The <a href="/blog/velocity-limits-explained">velocity limit</a> is the rule that stops it: a cap on transactions per window ends the loop at the source.</p>

<h3>Pattern 2: the unknown vendor</h3>
<p>Agents buying from merchants nobody vetted. The <a href="/glossary/merchant-allowlist">merchant allowlist</a> makes the default deny: unknown vendors are BLOCKED unless approved.</p>

<h3>Pattern 3: no external gate</h3>
<p>Every incident shares a root cause: the only control was a prompt instruction. Prompts are <a href="/blog/prompt-not-a-control">not controls</a>. The incidents that cost the most are the ones where a deterministic gate would have been trivial.</p>

<p>Full records, sources, and machine-readable data: <a href="/incidents/">browse the database →</a></p>
</div>"""

    if slug == "the-hidden-cost-of-prompt-injection":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>The hidden cost of prompt injection</div>
<span class="tag warn">Security</span>
<h1>The hidden cost of prompt injection: it's the spend, not the prompt</h1>
<p class="lead">Prompt injection isn't just a data-safety problem — it's a money problem. The documented attacks that ended in spend, and the deterministic defense that can't be injected.</p>
<div class="meta">July 22, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Most writing about prompt injection focuses on data exfiltration and model behavior. The angle that gets less attention is the one that actually shows up on invoices: injection as a <em>spending</em> attack. An injected instruction in tool output can push an agent to purchase, subscribe, or pay — and the agent will do it, because that's what it's built to do.</p>

<h3>The documented shapes</h3>
<p>The <a href="/incidents/">incident database</a> records the patterns: agents that followed instructions embedded in content and spent against an operator's intent — purchases from unknown vendors, subscription triggers, payment-rail activity. The common thread isn't model quality; it's that nothing sat between the agent and the money.</p>

<h3>Why detection isn't the answer</h3>
<p>Injection detection is probabilistic — a bypass is always possible. Even a <em>detected</em> injection still needs something to stop the money from moving. The reliable defense is a deterministic gate on the spend path: <a href="/faq/can-sipi-bot-stop-prompt-injection">rules that can't be injected</a>. An injected instruction can't add a merchant to the allowlist or raise a cap — approvals come from rules, not from model output.</p>

<h3>The layered answer</h3>
<p>Keep detection tools for the content layer. Add the firewall for the money layer. Defense in depth: detect the attack, and make the damage impossible regardless.</p>
</div>"""

    if slug == "how-to-run-an-agent-spend-audit":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>How to run an agent spend audit</div>
<span class="tag navy">Operations</span>
<h1>How to run an agent spend audit in 30 minutes</h1>
<p class="lead">The audit-log questions that turn agent spend into decisions: where the money goes, what got blocked that shouldn't have, and the one rule change that matters most.</p>
<div class="meta">July 15, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>You don't need a dashboard project to audit agent spend. You need the audit log and 30 minutes. Here's the agenda — the same one from the <a href="/templates/weekly-spend-review-template">weekly review template</a>, compressed.</p>

<h3>Question 1: where is the spend?</h3>
<p>Group the log by agent, then by merchant. The shape tells you everything: one agent dominating, or a long tail of vendors you don't recognize.</p>

<h3>Question 2: what got blocked that shouldn't have?</h3>
<p>Blocked attempts are the firewall working — but blocks on legitimate work are the tuning signal. If a real workflow keeps hitting a cap, the cap is wrong, not the workflow.</p>

<h3>Question 3: what got flagged?</h3>
<p>Flagged transactions that were all approved mean your threshold is too low — you're paying humans to rubber-stamp. All denied means the agents are trying things they shouldn't.</p>

<h3>The output</h3>
<p>One rule change, measured next week. That's the whole audit: <a href="/guides/guide-to-agent-spend-audits">read the guide →</a></p>
</div>"""

    if slug == "what-a-spend-firewall-wont-do":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>What a spend firewall won't do</div>
<span class="tag neutral">Honest</span>
<h1>What a spend firewall won't do</h1>
<p class="lead">The honest limits: it won't stop every bad decision, it can't reverse settlements, and it's not a compliance certification. Here's what it actually is.</p>
<div class="meta">July 8, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Most writing about spend firewalls sells the upside. Here's the other side — because a control you misunderstand is a control you'll mis-deploy.</p>

<h3>It won't stop every bad decision</h3>
<p>A firewall enforces the rules you wrote. If the rules are wrong — a cap too high, a vendor mistakenly allowlisted, a category ungoverned — the firewall will faithfully enforce the wrong policy. <a href="/templates/firewall-rule-tuning-checklist">Rule tuning</a> is part of the product, not an afterthought.</p>

<h3>It can't reverse settlements</h3>
<p>Decisions happen before the money moves. If a transaction is approved and settles, no firewall is un-ringing that bell. That's why the design favors flag-over-block for edge cases: review before settlement, not after.</p>

<h3>It's not a compliance certification</h3>
<p>The audit log is evidence — a control and a source of truth. It is not SOC 2, ISO 27001, or a regulatory sign-off. Pair it with your org's governance framework.</p>

<h3>What it actually is</h3>
<p>A deterministic decision layer on the money path: APPROVED, BLOCKED, or FLAGGED before settlement, every decision logged. That's a narrow, honest job — and it's the one control that would have stopped the documented runaways in the <a href="/incidents/">incident database</a>.</p>
</div>"""

    if slug == "how-to-pick-your-first-three-rules":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>How to pick your first three firewall rules</div>
<span class="tag navy">Onboarding</span>
<h1>How to pick your first three firewall rules</h1>
<p class="lead">You don't need all six rule types on day one. The three that cover the most documented failure modes — and how to set them in one session.</p>
<div class="meta">June 28, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>New teams often ask for every rule type at once. The incident database suggests otherwise: three rules cover the majority of documented failure modes. Start there, then tune with your audit log.</p>

<h3>Rule 1: the per-transaction cap</h3>
<p>Block any single purchase above a ceiling. This is the bluntest rule and the most valuable — the largest documented runaways start with one oversized transaction that nothing screened. Set it at the largest 'no review needed' purchase for the agent.</p>

<h3>Rule 2: the merchant allowlist</h3>
<p>Only approved vendors can be paid. Unknown vendors are the second-most-common failure shape — and the allowlist makes them default-deny. Start with the three to five vendors the agent actually uses.</p>

<h3>Rule 3: the velocity limit</h3>
<p>A cap on transactions per window. This is the rule that kills retry loops — the single most common runaway pattern in the <a href="/incidents/">database</a>. Start at 10 calls per minute for general agents, 5 for trading/finance.</p>

<h3>One session, three rules</h3>
<p>Set all three in the dashboard (or via the API), then watch the audit log for a week. The log — not the rule count — is what tells you what to add next. <a href="/how-to/how-to-create-a-spend-policy">Build the policy around them →</a></p>
</div>"""

    if slug == "the-voice-agent-spend-problem":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>The voice agent spend problem</div>
<span class="tag warn">Cost</span>
<h1>The voice agent spend problem nobody is talking about</h1>
<p class="lead">Voice agents bill per minute of telephony plus LLM tokens per turn. A retry storm is billable minutes for nothing. Here's the math and the control.</p>
<div class="meta">June 15, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Voice agents are the fastest-growing agent category — and their billing model is the easiest to overspend: <strong>per minute of telephony</strong> on top of <strong>per-token LLM cost</strong> for every turn. Both lines scale with autonomy.</p>

<h3>The two lines</h3>
<p>The telephony line is simple: minutes × rate. The token line is where it escapes — a long or looping conversation compounds tokens per turn, and every tool call mid-call adds another spend surface. Platforms like <a href="/integrations/vapi">Vapi</a>, <a href="/vs/retell">Retell</a>, and <a href="/vs/bland-ai">Bland</a> bill the minutes; nobody bills the policy.</p>

<h3>The retry storm</h3>
<p>Failed calls get retried — and retries are billable minutes for nothing. A retry storm during an outage is the voice version of the <a href="/blog/runaway-loops-anatomy">runaway loop</a>: same pattern, different meter. A <a href="/glossary/velocity-limit">velocity limit</a> stops it at the source.</p>

<h3>The control</h3>
<p>Per-agent ceilings on telephony, category rules separating minutes from tokens, and an allowlist for mid-call tools. See the <a href="/use-cases/voice-agents">voice agent spend guide →</a></p>
</div>"""

    if slug == "subscription-sprawl-the-quiet-ai-cost":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Subscription sprawl</div>
<span class="tag navy">Operations</span>
<h1>Subscription sprawl: the quiet AI cost</h1>
<p class="lead">Unused seats, auto-renewing tools, silent tier upgrades — and agents that can subscribe on their own. How the quietest line on the AI bill grows.</p>
<div class="meta">May 30, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Everyone watches the token bill. The line that actually grows quietly is subscriptions: seats nobody uses, tools nobody reviewed, tiers that upgraded without a decision. And now agents can add to it themselves.</p>

<h3>The three drift patterns</h3>
<p><strong>Seat sprawl.</strong> Per-seat AI tools multiply faster than value. <strong>Auto-renewal drift.</strong> Tools renew because nobody reviewed them. <strong>Silent tier upgrades.</strong> Plans upgrade without a decision — usually to chase a limit nobody hit.</p>

<h3>The agent twist</h3>
<p>Agents with payment capability can <a href="/faq/can-ai-agents-pay-subscriptions">start subscriptions on their own</a> — a recurring line item created by one tool call. The <a href="/glossary/merchant-allowlist">merchant allowlist</a> is the control: only approved vendors can be paid, new ones FLAG for review.</p>

<h3>The quarterly fix</h3>
<p>Audit usage, kill unused seats, review renewals, and put new tool purchases behind the allowlist. The <a href="/redflags/red-flags-in-ai-agent-subscriptions">subscription red flags</a> list is the audit checklist.</p>
</div>"""

    if slug == "the-coding-agent-cost-war":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>The coding agent cost war</div>
<span class="tag warn">Cost</span>
<h1>The coding agent cost war is really a control problem</h1>
<p class="lead">Every coding agent — Cline, Roo, Cursor, Claude Code, Codex — bills differently, and all of them can spend beyond the editor. The winner isn't the cheapest model; it's the team that controls the spend.</p>
<div class="meta">May 10, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Read any thread about coding agents and you'll find a pricing comparison — tokens per model, seats per tool. The comparison misses the point. The bill isn't decided by the rate card; it's decided by what the agent <em>does</em>.</p>

<h3>Every agent can spend beyond the editor</h3>
<p>Cline and Roo call tools freely in autonomous loops. Cursor and Claude Code consume usage fast in agentic sessions. Codex triggers actions. Each of them can buy compute, hit paid APIs, or trigger payments — spend no seat price captures. <a href="/integrations/cline">Cline</a>, <a href="/integrations/roo-code">Roo Code</a>, and the rest all wire to the same control.</p>

<h3>The control, not the rate</h3>
<p>The teams that win the cost war don't chase the cheapest model — they put a <a href="/glossary/spend-policy">spend policy</a> in front of every agent: a cap, an allowlist, a velocity limit. The model choice matters 10%; the control matters 90%.</p>

<h3>The math</h3>
<p>A retry loop multiplies any rate card. A velocity limit stops the loop. That's the entire war, in one sentence.</p>
</div>"""

    if slug == "when-to-flag-vs-block":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Flag vs block</div>
<span class="tag navy">Operations</span>
<h1>Flag vs block: when to let an agent ask instead of stop</h1>
<p class="lead">Hard blocks stop bad spend but also stop legitimate work. Approval thresholds keep agents fast. Here's the decision rule for when to use which.</p>
<div class="meta">April 20, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Every spend firewall decision is APPROVED, BLOCKED, or FLAGGED. The first two are easy to understand. The third is where the design actually lives — and where most teams get it wrong.</p>

<h3>Block for certainty</h3>
<p>When a transaction can never be legitimate — banned merchant, over a hard cap, category blocked — BLOCK is right. No review needed, no queue, final. <a href="/scenarios/unknown-vendor-spend-scenario">Unknown vendors</a> are the classic case.</p>

<h3>Flag for ambiguity</h3>
<p>When a transaction is suspicious but might be legitimate — over a threshold, a new merchant, off-hours — FLAG and route to a human. The agent pauses, the human decides in minutes, and legitimate work proceeds. This is what the <a href="/glossary/approval-queue">approval queue</a> is for.</p>

<h3>The decision rule</h3>
<p>If you'd never approve it, block. If you might, flag. If it's routine, approve. Tune with the audit log: all-approved flags mean the threshold is too low; all-denied means the agents are trying the wrong things. <a href="/blog/how-to-pick-your-first-three-rules">Start with three rules →</a></p>
</div>"""

    if slug == "metering-vs-spend-firewall":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>Metering vs spend firewall</div>
<span class="tag warn">Architecture</span>
<h1>Metering platforms bill your customers. They don't control your agents.</h1>
<p class="lead">Metronome, Orb, and Amberflo are for revenue — measuring usage and billing customers. Agent spend control is a different job, in the other direction. Here's the split.</p>
<div class="meta">April 5, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>When teams shop for AI cost control, they often land on usage-based billing platforms. It's an easy confusion: both products are about 'usage' and 'cost.' But they face opposite directions.</p>

<h3>The revenue direction</h3>
<p>Metering platforms (<a href="/vs/metronome">Metronome</a>, <a href="/vs/orb">Orb</a>, <a href="/vs/amberflo">Amberflo</a>) measure what your <em>customers</em> used and bill them. They're revenue infrastructure — critical, but they look outward.</p>

<h3>The cost direction</h3>
<p>Agent spend control looks inward: what do <em>your</em> agents spend, on whom, against which rules — before the money moves. No metering platform makes that decision; they record usage after the fact.</p>

<h3>The compose pattern</h3>
<p>Meter your customers' usage with Metronome or Orb. Gate your agents' spend with sipi.bot. Feed the firewall's audit log into your metering stack. Revenue and cost, each with the right tool. <a href="/vs/metronome">Read the comparison →</a></p>
</div>"""

    if slug == "the-credit-model-of-ai-app-builders":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>The credit model of AI app builders</div>
<span class="tag navy">Architecture</span>
<h1>The credit model of AI app builders, and the bill it hides</h1>
<p class="lead">Lovable, Bolt, and friends bill by credits for building. The real bill starts when the apps you built start running agents. How to budget the runtime, not just the build.</p>
<div class="meta">March 15, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>AI app builders (<a href="/integrations/lovable">Lovable</a>, <a href="/integrations/bolt">Bolt</a>, <a href="/integrations/v0">v0</a>) sell credits — pay per prompt, ship an app. The credits are the visible spend. The bill that grows after launch is the runtime: the agents your shipped app runs, calling APIs per user action.</p>

<h3>The hidden line</h3>
<p>A generated app with an agentic feature is spend infrastructure: every user action can trigger tool calls, inference, and third-party APIs. The builder's credits paid for the build; nothing budgets the runtime.</p>

<h3>Budget the runtime</h3>
<p>Wire the guard into the agents your built apps run: a ceiling per app, an allowlist for the APIs it calls, a velocity limit for loops. The builder gets you to launch; the firewall keeps launch profitable. <a href="/use-cases/agentic-commerce">The same logic applies to any shipped agent →</a></p>
</div>"""

    if slug == "the-cloud-ai-platform-bill":
        return """<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/blog/">Blog</a><span class="sep">/</span>The cloud AI platform bill</div>
<span class="tag warn">Architecture</span>
<h1>Bedrock, Vertex, and AI Foundry are not spend firewalls</h1>
<p class="lead">The big three cloud AI platforms govern model access, not agent spend. Their budgets stop at the cloud boundary. Here's the money-layer gap.</p>
<div class="meta">February 28, 2026 · sipi.bot</div>
</section>
<div class="prose">
<p>Teams standardize agents on <a href="/vs/aws-bedrock">AWS Bedrock</a>, <a href="/vs/google-vertex-ai">Google Vertex AI</a>, or <a href="/vs/azure-ai-foundry">Azure AI Foundry</a> — and assume the platform's budgets cover the risk. They don't. Those budgets stop at the cloud boundary.</p>

<h3>The gap</h3>
<p>The platform governs <em>its own</em> usage: model tokens, compute, managed services. Nothing it offers gates what your agents buy <em>beyond</em> it — a data vendor, a payment rail, a third-party API. That's where the documented runaways live.</p>

<h3>The money layer</h3>
<p>The control that covers every merchant sits outside the platform: a <a href="/glossary/spend-firewall">spend firewall</a> on the money path, evaluating each proposed transaction before settlement. Platform budgets for the platform; the firewall for the money. They compose — see the <a href="/vs/aws-bedrock">comparisons →</a></p>
</div>"""

    return ""  # fallback


def build_blog():
    hub_items = []
    for post in POSTS:
        body = _body_for(post)
        hub_items.append(f"""<div class="card">
<span class="tag {'good' if 'announcement' in post.get('tags',[]) else 'warn' if 'security' in post.get('tags',[]) else 'navy' if 'integrations' in post.get('tags',[]) else 'neutral'}">{post['tags'][0].replace('-',' ').title()}</span>
<h3><a href="/blog/{post['slug']}/">{c._esc(post['title'])}</a></h3>
<p>{c._esc(post['description'])}</p>
<div class="meta">{post['date']}</div>
</div>""")

        # detail page
        detail_body = _body_for(post) or f"<h1>{c._esc(post['title'])}</h1><p>{c._esc(post['description'])}</p>"
        # BARE canonical (2026-08-08): blog leaves are served by _serve_pseo,
        # which 301s the slash form to bare — slash canonicals contradicted the
        # served URL (GSC duplicate-source, same pattern as the public/ fix).
        post_path = f"/blog/{post['slug']}"
        jsonld = [
            c.breadcrumb_ld([("Home", "/"), ("Blog", "/blog/"), (post["title"], post_path)]),
            c.article_ld(title=post["title"], description=post["description"],
                         canonical_path=post_path, date_published=post["date"]),
        ]
        html = c.page(title=f"{post['title']} | sipi.bot", description=post["description"],
                      canonical_path=post_path, active="Blog",
                      body=f'<main class="wrap">{detail_body}</main>', jsonld=jsonld)
        c.write(os.path.join(BLOG_DIR, post["slug"], "index.html"), html)

    # hub
    hub_body = f"""
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span>Blog</div>
<span class="kicker">{len(POSTS)} posts</span>
<h1>The sipi.bot blog</h1>
<p class="lead">How AI agents spend money, what happens when they get it wrong, and how to build the guardrail before the bill.</p>
</section>
<div class="grid two">
{"".join(hub_items)}
</div>
<div class="band">
<h2>Every post is backed by real data</h2>
<p>The blog draws on the <a href="/incidents/">AI Agent Incident Database</a> — 34 sourced records of agents that lost money, deleted data, or took unintended actions. No hypotheticals, no fabricated benchmarks.</p>
<div class="btns">
<a class="btn primary" href="/incidents/">Browse the incident database →</a>
<a class="btn ghost" href="/tools/agent-spend-risk-calculator/">Score your risk</a>
</div>
</div>
"""
    jsonld = [
        c.breadcrumb_ld([("Home","/"),("Blog","/blog/")]),
    ]
    html = c.page(title="sipi.bot Blog — AI agent spending, incidents, and guardrails",
                  description=f"{len(POSTS)} deep posts on AI agent spend control: runaway loops, prompt vs policy, incident post-mortems, and the architecture of deterministic agent guardrails. Backed by real incident data.",
                  canonical_path="/blog/", active="Blog", body=hub_body, jsonld=jsonld)
    c.write(os.path.join(BLOG_DIR, "index.html"), html)
    print(f"blog/: hub + {len(POSTS)} posts")


# ============================================================= CHANGELOG + STATUS
CHANGELOG_ENTRIES = [
    {"date":"2026-07-27","title":"AI Agent Incident Database launched","body":"Open, sourced database of 34 AI-agent incidents — CC BY 4.0, JSON/CSV/JSONL, live at /incidents/. First canonical source for agent-spend loss data."},
    {"date":"2026-07-19","title":"Spend-policy generator + risk calculator","body":"Two free interactive tools: the Agent Spend Risk Calculator (score 1–10 from your agent config) and the Spend Policy Generator (JSON, YAML, curl output). Live at /tools/."},
    {"date":"2026-07-18","title":"pSEO expansion: scenarios, redflags, calculators, guides","body":"Added 4 new content sections — /scenarios/, /redflags/, /calculators/, /guides/ — covering specific agent-risk scenarios and how each rule type addresses them."},
    {"date":"2026-07-01","title":"MCP server launched","body":"sipi.bot is now a native MCP server. Any agent framework that speaks MCP (Claude Code, Cursor, LangChain) can use the firewall as a standard tool with no SDK."},
    {"date":"2026-06-15","title":"Protected-by badge goes live","body":"Free embeddable image badge showing live firewall stats. No JS, no account needed. Embed on any README, docs site, or landing page."},
    {"date":"2026-05-01","title":"Sipi.bot eval gym: 53/53","body":"The evaluation harness now covers all 53 scenarios across all 6 rule types. Results published as machine-readable JSON at /eval and human-readable at /eval-report/."},
    {"date":"2026-03-01","title":"Sipi.bot v1 launched","body":"First hosted deployment: Team $99/mo, Business $499/mo, free self-host (MIT). Core engine: one call → APPROVED/BLOCKED/FLAGGED in <5ms."},
    {"date":"2026-01-15","title":"Sipi.bot founded","body":"After a $12,400 overnight Azure bill from a runaway agent loop, the belief that every autonomous agent needs a deterministic spend firewall became a company."},
]


def build_changelog():
    items = "".join(
        f'<div class="card"><h3>{c._esc(e["title"])}</h3>'
        f'<p class="meta">{e["date"]}</p>'
        f'<p style="margin-top:10px">{c._esc(e["body"])}</p></div>'
        for e in CHANGELOG_ENTRIES
    )
    body = f"""
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span>Changelog</div>
<span class="kicker">{len(CHANGELOG_ENTRIES)} entries</span>
<h1>Product changelog</h1>
<p class="lead">Every significant update to sipi.bot — from the founding $12,400 bill to today's incident database.</p>
</section>
<div style="max-width:720px">
{items}
</div>
<div class="band">
<h2>What's next</h2>
<p>We're building the canonical reference for AI agent spend governance. The database grows weekly. Follow the <a href="/blog/">blog</a> for deep dives and the <a href="/incidents/">incident database</a> for the underlying data.</p>
<div class="btns">
<a class="btn primary" href="/pricing">Deploy sipi.bot — $99/mo</a>
<a class="btn ghost" href="{c.GITHUB}">Star on GitHub ↗</a>
</div>
</div>
"""
    jsonld = [
        c.breadcrumb_ld([("Home","/"),("Changelog","/changelog/")]),
    ]
    html = c.page(title="sipi.bot Changelog — product updates since $12,400 | sipi.bot",
                  description=f"Every significant sipi.bot update, {CHANGELOG_ENTRIES[0]['date']} to {CHANGELOG_ENTRIES[-1]['date']}. From the founding $12,400 incident to the 34-record AI Agent Incident Database.",
                  canonical_path="/changelog/", body=body, jsonld=jsonld)
    c.write(os.path.join(CHANGELOG_DIR, "index.html"), html)
    print("changelog/: page")


def build_status():
    body = """
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span>Status</div>
<span class="tag good">Operational</span>
<h1>System status</h1>
<p class="lead">All sipi.bot services are operating normally. The firewall API processes evaluations in under 5ms with 99.9%+ uptime.</p>
</section>

<div class="statbox">
<div class="stat"><div class="n" style="color:var(--mint)">99.9%+</div><div class="l">Uptime (30-day rolling)</div></div>
<div class="stat"><div class="n" style="color:var(--mint)"><5ms</div><div class="l">P99 evaluation latency</div></div>
<div class="stat"><div class="n" style="color:var(--mint)">53/53</div><div class="l">Eval gym pass rate</div></div>
<div class="stat"><div class="n" style="color:var(--mint)">34</div><div class="l">Incident database records</div></div>
</div>

<section style="max-width:720px">
<h2>API endpoints</h2>
<div class="card"><h3>POST /v1/transactions/evaluate</h3><p>Core firewall endpoint. Returns APPROVED, BLOCKED, or FLAGGED with reason.</p><p class="meta">Status: operational · P99 &lt;5ms · Docs: <a href="/v1/transactions/evaluate">/v1/transactions/evaluate</a></p></div>
<div class="card"><h3>MCP server</h3><p>Model Context Protocol native tool server. Connect from Claude Code, Cursor, or any MCP-compatible agent.</p><p class="meta">Status: operational · Docs: <a href="/for/">/for/</a></p></div>
</section>

<section style="max-width:720px">
<h2>Data services</h2>
<div class="card"><h3>AI Agent Incident Database</h3><p>34 records, CC BY 4.0, available as JSON/CSV/JSONL. Auto-synced weekly.</p><p class="meta">Status: operational · <a href="/data/ai-agent-incidents.json">JSON</a> · <a href="https://github.com/kindrat86/ai-agent-incident-database">GitHub</a></p></div>
<div class="card"><h3>Protected-by badge</h3><p>Free embeddable badge. No JS, no account. Live firewall stats via image URL.</p><p class="meta">Status: operational · <a href="/badge">/badge</a></p></div>
</section>

<div class="band">
<h2>Enterprise SLA</h2>
<p>Business plan ($499/mo) includes a 99.9% uptime SLA, priority support, and custom rule configurations. For enterprise deployments with dedicated infrastructure, contact sales.</p>
<div class="btns">
<a class="btn primary" href="/pricing">View plans →</a>
<a class="btn ghost" href="mailto:sales@sipiteno.com">Contact sales ↗</a>
</div>
</div>
"""
    jsonld = [
        c.breadcrumb_ld([("Home","/"),("Status","/status/")]),
    ]
    html = c.page(title="sipi.bot Status — system status and API health | sipi.bot",
                  description="sipi.bot system status: API operational at <5ms P99 latency, eval gym 53/53, incident database live with 34 records. Enterprise SLA available.",
                  canonical_path="/status/", body=body, jsonld=jsonld)
    c.write(os.path.join(STATUS_DIR, "index.html"), html)
    print("status/: page")


def _dedupe_rss(rss: str) -> str:
    """Remove duplicate <item> blocks (same guid), keeping the first."""
    items = list(re.finditer(r"<item>.*?</item>", rss, re.S))
    if not items:
        return rss
    seen, kept = set(), []
    for m in items:
        g = re.search(r"<guid[^>]*>([^<]+)</guid>", m.group(0))
        key = g.group(1) if g else m.group(0)
        if key in seen:
            continue
        seen.add(key)
        kept.append(m)
    if len(kept) == len(items):
        return rss
    return rss[:items[0].start()] + "\n".join(m.group(0) for m in kept) + rss[items[-1].end():]


# =========================================================== RSS enrichment
def enrich_rss():
    """Append blog and incident entries to the existing RSS feed.

    Idempotent since 2026-08-08: dedupes the existing feed and only appends
    items whose guid is not already present (the old version re-appended every
    post on each run, duplicating entries — 36 items for 27 unique).
    """
    import shutil
    import uuid

    # Backup
    shutil.copy2(RSS_PATH, RSS_PATH + ".bak")
    with open(RSS_PATH + ".bak", encoding="utf-8") as f:
        existing = f.read()

    existing = _dedupe_rss(existing)
    existing_guids = set(re.findall(r"<guid[^>]*>([^<]+)</guid>", existing))

    # Build new items
    items = []
    for post in sorted(POSTS, key=lambda p: p["date"], reverse=True):
        d = datetime.fromisoformat(post["date"])
        guid = f"https://sipi.bot/blog/{post['slug']}#{uuid.uuid5(uuid.NAMESPACE_DNS, 'sipi.bot'+post['slug'])}"
        if guid in existing_guids:
            continue
        items.append(f"""  <item>
    <title>{_html.escape(post['title'])}</title>
    <link>https://sipi.bot/blog/{post['slug']}/</link>
    <guid isPermaLink="true">{guid}</guid>
    <description>{_html.escape(post['description'])}</description>
    <dc:creator>sipi.bot</dc:creator>
    <pubDate>{d.strftime('%a, %d %b %Y 12:00:00 GMT')}</pubDate>
  </item>""")

    # Incident database entry
    inc_guid = "https://sipi.bot/incidents/#db-launch-2026-07-27"
    if inc_guid not in existing_guids:
        items.append(f"""  <item>
    <title>AI Agent Incident Database — 34 records, $2.91B tracked</title>
    <link>https://sipi.bot/incidents/</link>
    <guid isPermaLink="true">{inc_guid}</guid>
    <description>Open, sourced database of real-world AI-agent incidents, CC BY 4.0. 34 records spanning 2016-2026. JSON, CSV, JSONL available.</description>
    <dc:creator>sipi.bot</dc:creator>
    <pubDate>Sun, 27 Jul 2026 12:00:00 GMT</pubDate>
  </item>""")

    # Insert new items before the closing </channel> tag
    new_rss = existing.replace("  </channel>", "\n".join(items) + "\n  </channel>")
    # Update lastBuildDate
    new_rss = re.sub(r'<lastBuildDate>.*?</lastBuildDate>',
                     f'<lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>',
                     new_rss)

    with open(RSS_PATH, "w", encoding="utf-8") as f:
        f.write(new_rss)
    print(f"rss: enriched with {len(items)} new items (backup at {RSS_PATH}.bak)")


# ----------------------------------------------------------------------- driver
def main():
    os.makedirs(BLOG_DIR, exist_ok=True)
    os.makedirs(CHANGELOG_DIR, exist_ok=True)
    os.makedirs(STATUS_DIR, exist_ok=True)

    build_blog()
    build_changelog()
    build_status()
    enrich_rss()


if __name__ == "__main__":
    main()
