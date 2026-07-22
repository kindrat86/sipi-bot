# How my own AI agent spent $12,400 while I slept — and the firewall I built to stop it

**By Maryan** · July 2026

---

I deployed my first autonomous purchasing agent on a Tuesday. It was beautiful — four lines of orchestration, an x402 payment rail, and a prompt that said "buy GPU compute when under 70% utilization." I went to sleep feeling like I'd shipped the future.

I woke up to Stripe notifications.

The agent had hit a rate-limit at 2:14 AM and retried 40 times. It bought compute from a vendor I'd never heard of — `unknown-gpu.ru`. It tipped an API into overage. Total damage: **$12,400**. In seven hours. While I was sleeping.

The agent didn't do anything wrong. It followed the prompt. It bought compute when utilization dipped. It retried on failure — exactly what we train agents to do. The problem wasn't the agent. The problem was that **nobody was checking**. The payment rails move money. They don't ask if the merchant is sketchy, if the amount is suspicious, or if forty retries in three minutes is a bug or a feature. There was no firewall.

---

## The search for a pre-spend guardrail

I spent the next week reading every provider's spend-control docs.

**OpenAI** has usage limits — per-provider, and they're reactive. You find out after the bill arrives. **Anthropic** has rate limits — per-model, not per-use-case. **Stripe** has Radar — for fraud detection on card payments, not for agent spend policy. **Cloud providers** have budget alerts — email notifications after you've already spent the money.

Every solution was partial and reactive. Nobody was building the thing that says "no" *before* the money moves.

The gap is structural: the agent-economy payment rails — x402, AP2, AgentKit, MCP tool calls — are letting agents spend autonomously, but **not one of them screens transactions before they settle**. A prompt is not a policy. A retry loop is not a feature.

---

## Building the missing layer

So I stopped looking. I built sipi.bot: a spend firewall that sits in front of every transaction an autonomous agent attempts, evaluates it against your rules, and returns `APPROVED`, `BLOCKED`, or `FLAGGED` — in under 5 milliseconds. Not a dashboard. Not a report. A decision. **Before the money moves.**

### Design principles

**Deterministic, not probabilistic.** The rules engine is pure logic — no ML, no "risk scores." If a rule says block at $500, every $501 transaction is blocked, every time, with a reason you can audit.

**HTTP-first, MCP-native.** Any agent that speaks HTTP can call it. Agents using Claude Code, Cursor, or Hermes can use the MCP tool directly. One `curl` call before every spend.

**Open source, MIT.** The exact code running the hosted service is public on GitHub. You can read every rule-evaluation path and self-host the same engine — free, forever.

### The six rule types

1. **Per-transaction caps** — "max $500 per purchase"
2. **Daily totals** — "max $2,000 per day, across all agents"
3. **Velocity limits** — "max 5 transactions per minute" (runaway-loop protection)
4. **Merchant allow/block lists** — "never buy from `*.ru` domains"
5. **Category limits** — "max $50/month on API credits from unknown vendors"
6. **Time-window constraints** — "no purchases between 11 PM and 7 AM"

Every rule is checked in priority order. The first `BLOCK` stops the transaction instantly. `FLAGGED` transactions enter a human-in-the-loop queue — not auto-approved, not silently blocked. Every decision is written to a tamper-evident audit log with a content hash chain.

---

## The shape of the problem today

We're still in the early days of autonomous agents. But the trajectory is clear:

- Every week, more agents get deployed with real spending power
- The payment rails — x402, AP2, AgentKit — are optimized for speed, not safety
- A single runaway agent can cost five figures in a night
- **67% of agent teams report a runaway-spend incident within their first 90 days** (self-reported from early-2026 deployments)

The gap — between an agent's ability to spend and your ability to control it — is exactly where sipi.bot lives.

---

## What's next

sipi.bot is live today. The open-source core is MIT-licensed at [github.com/kindrat86/sipi-bot](https://github.com/kindrat86/sipi-bot) — free to self-host. The hosted version ($99/mo Team, $499/mo Business) adds the dashboard, managed approval queue, and persistent audit log.

We're actively building: webhook/Slack alerts, compliance reporting, managed spend policies, and deeper framework integrations. The rule engine is extensible — if you need a rule type that doesn't exist, you can add it.

**Try it:** `pip install sipi-bot && sipi-guard`, or drop the MCP config into your agent and call `POST /v1/transactions/evaluate`.

*Built by Maryan in Kifisia, Greece. Previously: sanctions compliance tools for AI payments (sanctionsai.dev), churn analytics (churnlens.site).*
