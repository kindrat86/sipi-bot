# OWNER ACTIONS — sipi.bot Traffic Maximization

Generated 2026-07-23 by Hermes automated runbook.

---

## 1. GSC Verify + Submit Sitemap

- Login to [Google Search Console](https://search.google.com/search-console)
- Verify ownership if not already: `sipi.bot` (likely via DNS TXT or HTML file)
- Submit sitemap: `https://sipi.bot/sitemap.xml`
- Submit sitemap index: `https://sipi.bot/sitemap-index.xml`

**Bing Webmaster Tools:**
- Import from GSC or verify at [Bing WMT](https://www.bing.com/webmasters)
- Submit sitemap same URLs

---

## 2. Ecosystem Listings — 10 Qualified Targets

Paste-ready one-liners with descriptions from live site copy.

### Agent Payment / x402 Ecosystem

1. **x402 Awesome List (GitHub)**
   > "sipi.bot — Pre-spend firewall for x402 payments: one call approves, blocks, or flags each agent transaction against per-tx caps, velocity limits, and merchant rules before the x402 payment is signed. MIT open-source, MCP-native."

2. **Awesome AI Agents (GitHub)**
   > "sipi.bot — Spend firewall for autonomous AI agents. Evaluates every transaction against your rules and returns approve/block/flag in <5ms. HTTP API, MCP tool, CLI. Flat $99/mo or free self-host (MIT)."

3. **Agentic Payments / AP2 Working Group lists**
   > "sipi.bot — The spend layer for agent-payment rails: sits in front of x402, AP2, and AgentKit transactions, approving or blocking each one before money moves. Deterministic <5ms firewall with tamper-evident audit log."

### MCP / Agent Tool Directories

4. **Model Context Protocol (MCP) Server Directory**
   > Repository: `kindrat86/sipi-bot` — MCP server exposing `evaluate_spend(amount, merchant, category)` returning APPROVED/BLOCKED/FLAGGED. Per-transaction caps, velocity limits, merchant allowlist. MIT license.

5. **PulseMCP / MCP.so / Smithery.ai — MCP tool registries**
   > "sipi-bot MCP Server — Spend firewall for autonomous AI agents. Tool: `evaluate_spend`. Before your agent spends a dollar, sipi.bot checks the transaction against your rules and returns a decision. Darwin-approved."

6. **Glama.ai MCP Directory**
   > "sipi-bot MCP Server — Pre-spend firewall: approve, block, or flag any agent transaction before money moves. 6 rule types, <5ms latency, tamper-evident audit log."

### Agent Infrastructure / DevOps Lists

7. **Awesome LangChain / Awesome CrewAI (GitHub)**
   > "sipi.bot — Spend guardrails for agent frameworks. Drop-in firewall for LangChain tools, CrewAI BaseTools, OpenAI function tools, and Vercel AI SDK tools. 5 lines to add a spend policy. Open-source (MIT)."

8. **AI Engineer Tools / Stack Lists**
   > "sipi.bot — Pre-spend firewall for autonomous AI agents. One curl call returns approve/block/flag against your rules. <5ms inline, no per-call fees, $99/mo hosted or free self-host."

### General Discovery

9. **Product Hunt (launch draft — see Section 3)**
   > Launch title: "sipi.bot — Pre-spend firewall for AI agents"
   > Tagline: "Approve, block, or flag every agent transaction before money moves"

10. **Hacker News (Show HN — see Section 3)**
    > Post title: "Show HN: Pre-spend firewall for AI agents — approve/block every transaction before it happens"

---

## 3. Show HN Draft

**Title:** Show HN: Pre-spend firewall for AI agents — approve/block every transaction before it happens

**Body:**

I deployed my first autonomous purchasing agent on a Tuesday. By Wednesday morning, it had spent $12,400 — retrying a failed purchase 40 times, buying from a vendor I'd never heard of, tipping an API into overage. I was asleep for all of it.

The problem wasn't the agent. It followed the prompt. It retried on failure — exactly what we train agents to do. The problem was that nobody was checking. Payment rails move money. They don't ask if the merchant is sketchy, if the amount is suspicious, or if 40 retries in 3 minutes is a bug.

So I built sipi.bot — a spend firewall that sits in front of every transaction and returns approve, block, or flag in under 5ms. One curl call. Before a dollar moves.

**How it works:**
- Your agent calls `POST /v1/transactions/evaluate` before it spends
- sipi.bot checks the transaction against 6 rule types: per-tx caps, daily totals, velocity limits, merchant allow/block, category rules, time-of-day rules
- Returns APPROVED, BLOCKED, or FLAGGED (needs human)
- <5ms latency, tamper-evident audit log

**Surfaces:** HTTP API, MCP tool (Claude Code/Cursor/Hermes), CLI, Python/TS SDKs

**Pricing:** $99/mo flat (unlimited evals), MIT open-source core free to self-host

**Honest comparison of all 5 approaches to controlling AI agent spending:** https://sipi.bot/learn/how-to-control-ai-agent-spending

There's no claim that sipi.bot is the right choice for everyone — prompt limits, framework caps, and virtual cards each have their place. But if an agent holds a real payment method and can spend while you sleep, a firewall in the payment path is the only enforced, cross-framework option.

Happy to answer questions. The open-source core is at github.com/kindrat86/sipi-bot.

---

## 4. Cross-Portfolio Note

sipi.bot already sends ~24 visits/30d to unlocksaas.com via existing crosslinks (portfolio network footer). No action needed — these are valuable and should remain. The network footer is present on the homepage.
