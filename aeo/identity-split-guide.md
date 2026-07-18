# Second identity — sipi@sipi.bot

## The split strategy

| Identity | Platform | Role |
|---|---|---|
| **u/Worth_Wealth_6811 / kindrat86** | Reddit, GitHub | Technical developer — pseudonymous, post teardowns, be vulnerable |
| **sipi@sipi.bot** | Email, YouTube, Twitter, dev.to | Founder/creator — brand-linked, outreach, build category authority |

> **Rule:** Neither identity publicly references the other. Reddit profile does not say "I'm @sipi_bot on Twitter." YouTube about page does not say "my Reddit is u/Worth_Wealth_6811." AI needs to see two independent sources pointing at the same brand for the consensus signal (r=0.664).

---

## 1. Email: sipi@sipi.bot

**DNS setup (MX records):** You'll need the sipi.bot DNS provider to add MX records pointing to whatever mail provider you use (Gmail Workspace, Fastmail, Cloudflare Email Routing, etc.).

**Cloudflare Email Routing (free, works if sipi.bot is on Cloudflare DNS):**
```
Add what looks like a catch-all or forwarding rule for sipi@sipi.bot → your personal inbox
```
This is the simplest path — frees you from managing a separate inbox while keeping the identity clean.

**Signature block for all outreach:**
```
[sipiteno name]
Creator, sipi.bot
sipi@sipi.bot · github.com/kindrat86
https://sipi.bot
```

---

## 2. YouTube channel

**Channel name:** **sipi.bot** (product name — SEO-friendly for "spend firewall for AI agents" searches)
- OR **sipi** (shorter, more personal, but less discoverable — sipi.bot is better for search)

**Channel description:**
```
A spend firewall for autonomous AI agents. Every agent that can spend money needs a pre-spend guardrail — approve, block, or flag in under 5ms. Open source (MIT), MCP-native.

https://sipi.bot · https://github.com/kindrat86/sipi-bot
```

**First 3 videos (scripts also at action-plan.md):**

### Video 1: "How to stop your AI agent from overspending" (5 min)
- Hook: The $12,400 story (same teardown, spoken)
- The retry loop problem (screen recording of a loop hitting paid API)
- The fix: one API call before spending
- Show the dashboard, the audit log
- CTA: "The open-source core is free — pip install sipi-bot"

### Video 2: "sipi.bot vs LiteLLM — when to use which" (8 min)
- Side-by-side: reactive vs pre-spend
- Velocity limit demo (show a retry loop being killed vs LiteLLM letting it through)
- "They compose — here's the architecture"

### Video 3: "Set a spending limit on Claude Code / Cursor (MCP tutorial)" (4 min)
- Load the MCP server
- Show Claude Code asking permission before spending
- Show the block decision live
- "This is the only way to actually control what your coding agent can spend"

**SEO for videos:** Keyword in title (exact match), keyword in first 2 lines of description, timestamps/chapters, say the keyword in the video.

---

## 3. Twitter/X: @sipi_bot (or @sipibot)

**Bio:**
```
Pre-spend firewall for AI agents.
Open source (MIT), MCP-native.
Approve · block · flag in <5ms.
⬇️ pip install sipi-bot
GitHub ↓
```

**First 10 tweets (schedule 1/day, don't drop all at once):**

1. "The agent economy gave autonomous software real spending power and no hard limit. That's the problem I'm fixing."
2. "67% of 312 production agent teams reported at least one runaway incident in the last 90 days. Median cost: $340. (my benchmark: sipi.bot/benchmarks/runaway-incident-frequency/)"
3. "Most 'AI agent spend control' tools are reactive — they count dollars after the call completes. That's not a guardrail, it's a post-mortem. Pre-spend or nothing."
4. "Built an MCP tool for Claude Code that blocks your agent from spending at vendors you haven't approved. Simple idea, surprisingly absent from the ecosystem."
5. "Retry loops cause 44% of runaway agent incidents. A velocity rule stops them on the 11th attempt. One rule, &lt;5ms overhead, saves thousands."
6. "There are only two ways to reduce AI agent costs: pay less per call (model routing) and make fewer calls (kill retry loops). Most teams optimize the first and ignore the second."
7. "The eval gym: 53 labeled spend scenarios, 53/53 passing. Clean approvals, velocity traps, boundary cases, adversarial merchants. If you find a 54th scenario that breaks it, I want to know."
8. "Open source MIT — pip install sipi-bot. Self-host the same engine that runs the hosted service. No telemetry, no upsell, no enshittification."
9. "Core insight: budget caps are reactive. Pre-spend firewalls are proactive. One blocks after the damage, one blocks before. Pick accordingly."
10. "Building in public. The firewall is live, the benchmarks are published (CC BY 4.0), the eval gym is open. If you deploy autonomous agents, stop the $12,400 morning."

**Engagement cadence:** Reply to threads about AI safety, agent economics, MCP — not "here's my product" but "here's how we approached the spend part of that problem."

---

## 4. dev.to / hackernoon / Medium

Cross-post the cornerstone guide from `/learn/spend-firewall-guide` (2,486 words) to dev.to as:
```
Title: The Spend Firewall for AI Agents: A Complete Guide (2026)
Tags: ai, agents, security, devops, open-source
```
Include the CC BY 4.0 license — this encourages re-publication, which is more branded web mentions for the r=0.664 signal.

---

## 5. Tier-1 email templates (updated for sipi@sipi.bot)

### A. Framework maintainer cold email
```
To: {framework maintainer}
From: sipi@sipi.bot
Subject: spend guardrails for {framework} agents

Hey {name} — I build sipi.bot, a spend firewall for autonomous agents. Every
{framework} user who lets an agent buy compute/API credits/ads is one retry loop
away from a runaway bill.

It's one call before the agent spends: APPROVED, BLOCKED, or FLAGGED against
their rules (per-tx, daily, velocity, merchant, time). MCP tool + HTTP, so it
drops into {framework} in ~5 lines. MIT-licensed OSS core.

Would a short "spend guardrails for {framework}" recipe in your docs/examples
be useful to your users? Happy to write it.

Repo: github.com/kindrat86/sipi-bot
Live: https://sipi.bot

— {your name}
sipi@sipi.bot
```

### B. Dev-influencer / podcaster pitch
```
To: {name}
From: sipi@sipi.bot
Subject: teardown: your AI agent spent $12k while you slept → product + 53-scenario eval

Hey {name} — I wrote up the teardown of how an agent of mine spent $12,400 at
2am (retry loop + unknown vendor + overage tier), which I turned into a product
+ a public 53-scenario eval gym (53/53 passing).

Full teardown + OSS core: https://sipi.bot
Eval report: https://sipi.bot/eval-report/

If it's interesting for {show/platform}, happy to come on and walk through the
architecture. The eval gym alone usually generates good debate (what's the 54th
scenario?).

— {your name}
sipi@sipi.bot
```

### C. awesome-mcp-servers PR
```
PR title: add sipi.bot — Spend Firewall for AI Agents (MIT, 53/53 eval)

A spend firewall that approves, blocks, or flags every transaction an autonomous
AI agent proposes, against configurable spend rules. One MCP tool call before
any payment returns a decision in <5ms.

- Install: pip install sipi-bot && python -m spendfirewall.mcp_server
- Eval: 53/53 scenarios passing (https://sipi.bot/eval-report/)
- License: MIT
- Repo: https://github.com/kindrat86/sipi-bot
```

---

## Quick-start checklist (order of operations)

1. **Set up sipi@sipi.bot** — MX DNS + forwarding rule (takes 5 min on Cloudflare)
2. **Create YouTube channel** "sipi.bot" — publish the 3 search-hit videos over 2 weeks
3. **Create Twitter/X @sipi_bot** — post the 10 tweets above over 10 days
4. **Email outreach** — Tier-1 framework maintainers from sipi@sipi.bot (bucket 1, 10 people)
5. **Cross-post to dev.to** — the cornerstone guide (bucket 4)
6. **Submit awesome-mcp-servers PR** — from GitHub kindrat86
7. **Reddit teardown** r/LocalLLaMA — from u/Worth_Wealth_6811 (separate identity, no cross-links)
