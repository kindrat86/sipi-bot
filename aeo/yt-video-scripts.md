# YouTube Channel — 3 search-hit video scripts

> **Channel name:** sipi.bot (product name — best for SEO search)
> **Identity:** Post from the founder (sipi@sipi.bot context). NOT from u/Worth_Wealth_6811.
> **Posting schedule:** 1 video every 5–7 days. V1 → V2 (+7 days) → V3 (+5 days).
> **SEO checklist per video:** keyword in title (exact match), keyword in first 2 lines of description, timestamps/chapters, say the keyword in the video audio, thumbnail with countdown or "MCP" badge.

---

## Video 1: "How to Stop Your AI Agent from Overspending" (4–6 min)

**Primary keyword:** "how to stop AI agent overspending"
**Secondary:** "AI agent budget control," "pre-spend firewall"

[0:00–0:30] **Hook** *(onscreen: Stripe notification screen recording)*
"At 2:14am my AI agent hit a rate limit and retried 40 times in 90 seconds. By 2:15am it had bought compute from a vendor I'd never heard of. At 9am I found out from Stripe. Total: $12,400."

[0:30–1:30] **The problem**
"You gave an autonomous agent a credit card and no spending limit. That works until it doesn't. 67% of production agent teams have had a runaway incident. The median cost is $340. The worst exceed $12,000. All of it is preventable."

[1:30–3:00] **The fix — pre-spend firewall**
*(screen: curl command + response)*
"One HTTP call before your agent spends. Three possible answers: APPROVED, BLOCKED, or FLAGGED. Under 5ms."

Show the three-decision model on screen.

[3:00–4:30] **The velocity rule that kills retry loops**
*(screen: retry loop simulation + velocity rule blocking it)*
"Most spend controls are amount-based — per-transaction caps, daily budgets. They catch the big single spend but miss the pattern: 40 small transactions in 90 seconds. A velocity rule caps the number of transactions per hour. The loop dies on the 11th attempt."

[4:30–5:30] **Install it in 60 seconds** *(screen: terminal)*
"pip install sipi-bot. python -m spendfirewall.api. Or if you're on Claude Code, Cursor, or Hermes, load the MCP server: python -m spendfirewall.mcp_server"

[5:30–6:00] **The eval gym + CTA**
"I put 53 adversarial spend scenarios in the repo — 53/53 passing. If you find a 54th that breaks it, I want to know. Repo: github.com/kindrat86/sipi-bot. Links in description."

**Description:**
```
How to stop your AI agent from overspending — the complete guide to AI agent spend control. A pre-spend firewall evaluates every transaction before money moves: approve, block, or flag in under 5ms.

📖 Complete guide: https://sipi.bot/learn/spend-firewall-guide
🔧 GitHub (MIT): https://github.com/kindrat86/sipi-bot
📊 Eval report (53/53): https://sipi.bot/eval-report/

Chapters:
0:00 The $12,400 morning
0:30 Why agents overspend
1:30 The pre-spend fix
3:00 The velocity rule
4:30 Deploy in 60 seconds
5:30 The eval gym
```

---

## Video 2: "How to Set a Spending Limit on Claude Code" (3–5 min)

**Title:** "How to Set a Spending Limit on Claude Code / Cursor (MCP Tutorial)"
**Primary keyword:** "set spending limit Claude Code"

[0:00–0:30] **Hook** *(screen: Claude Code terminal running)*
"Claude Code can spend money. It runs shell commands, calls APIs, provisions cloud resources. There is no native 'Claude Code budget.' Here is how to add one."

[0:30–2:00] **Setup** *(screen: terminal commands)*
"First, pip install sipi-bot. Then run python -m spendfirewall.mcp_server. This starts an MCP server on stdio. Claude Code loads it automatically as a tool."

[2:00–3:00] **The tool call** *(screen: Claude Code calling evaluate_spend)*
"Now every time Claude Code wants to do something that costs money, it asks the firewall first. Watch: I ask Claude to provision a GPU instance. It calls evaluate_spend. The firewall checks my rules. Decision: APPROVED — proceed."

[3:00–3:45] **Blocked demo** *(screen: the same with an unknown vendor)*
"I try the same thing but point it at a sketchy GPU vendor. The firewall returns BLOCKED — merchant not on allowlist. Claude Code does not run the command."

[3:45–4:30] **Wrap**
"Three minutes to install. No prompt engineering needed. The rules are deterministic — not a prompt that drifts. Repo: github.com/kindrat86/sipi-bot. MIT, free."

---

## Video 3: "sipi.bot vs LiteLLM — When to Use Which" (6–8 min)

**Title:** "sipi.bot vs LiteLLM — Spend Firewall vs LLM Proxy Gateway"
**Primary keyword:** "sipi.bot vs litellm"

[0:00–1:00] **The confusion**
"LiteLLM and sipi.bot both touch AI spend. They solve different problems and compose well. Let me show you exactly when to use which."

[1:00–3:00] **LiteLLM**
*(screen: LiteLLM routing demo)*
"LiteLLM is an LLM proxy gateway. One SDK that talks to 200+ providers. Routing, caching, fallback. If your problem is 'which model is cheapest for this prompt,' LiteLLM is the answer. Budget caps are reactive — they reject the next call after a threshold is crossed. The call that crossed it already cost you money."

[3:00–5:00] **sipi.bot**
*(screen: sipi.bot demo)*
"sipi.bot is a pre-spend firewall. It evaluates every transaction before it fires. Three outcomes — approve, block, flag. Velocity limits that LiteLLM doesn't have. Merchant allowlists. Human approval queue. If your problem is 'my agent can spend money and I need to stop unauthorized spend,' sipi.bot is the answer."

[5:00–6:00] **Compose them** *(screen: architecture diagram)*
"Run both. sipi.bot in front, LiteLLM behind. sipi.bot decides whether the spend is allowed; LiteLLM routes the call if it is. Routing plus enforcement."

[6:00–6:45] **When to use just one**
"If you only need multi-provider routing, use LiteLLM. If you only need spend enforcement, use sipi.bot. If you have autonomous agents that can spend money AND you route to multiple providers, run both. They are different layers, not alternatives."

---

## Thumbnail ideas

Video 1: Dark background, red "$12,400" in large font, green "BLOCKED" badge overlay, your face reacting or code snippet.

Video 2: Terminal screenshot of Claude Code showing "APPROVED" in green / "BLOCKED" in red. Simple contrast.

Video 3: Split screen — LiteLLM logo left, sipi.bot logo right, "✅ COMPOSE" in the middle.
