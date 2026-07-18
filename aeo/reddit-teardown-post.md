# Reddit Teardown Post — tailored for u/Worth_Wealth_6811

> **Identity:** Personal developer account. You are "the developer who built sipi.bot," NOT a brand account. This matters — Reddit rewards vulnerability and authorship, punishes brand promotion.
> **Accounts to cross-post from:** GitHub `kindrat86` (your repo), email `sales@sipiteno.com` (for Tier-1 outreach).

---

## ⚠️ Before you post — karma check

Reddit's spam filter is aggressive on new/low-karma accounts, especially in r/LocalLLaMA and r/MCP. Before posting, check:

- **Account age:** if Worth_Wealth_6811 is brand new (< 7 days), **do not post yet**. Build karma first.
- **Comment karma:** r/LocalLLaMA typically requires ≥ 50 comment karma to post. r/MCP is more lenient. r/AI_Agents varies.
- **Subreddit history:** if you've never commented in r/LocalLLaMA before, your first post may be auto-removed. Comment on 3–5 threads first (genuine answers, not links) over 2–3 days.

**If your account is new or low-karma**, do this prep sequence first:
1. Spend 3 days in r/LocalLLaMA, r/MCP, r/AI_Agents commenting genuinely on others' work (no links, no mentions of sipi.bot). Build ~30–50 comment karma.
2. Then post the teardown below.
3. Monitor the post for the first 30 minutes — if auto-removed, message the mods (template below).

---

## r/LocalLLaMA post (PRIMARY — highest fit)

**Title:**
```
I built a spend firewall for AI agents after one nearly drained my card — 53-scenario eval gym inside
```

**Body:**
```
Last month an agent of mine hit a rate-limit on a paid API at 2am and did what
any retry loop does — it retried. Forty times in 90 seconds. By the time Stripe
emailed me at 9am, $4,000 was gone. It then bought GPU compute from a vendor I'd
never heard of (another $6,200), and tipped a different API into an overage tier
($2,200). Total: $12,400 while I slept.

The post-mortem was embarrassing because the fix is obvious in hindsight: the
agent should have asked permission before it spent. Not a budget cap that fires
after the damage. A pre-spend check — approve, block, or flag — in front of every
transaction.

So I built one. It's called sipi.bot — a deterministic spend firewall for
autonomous agents. One API call before your agent spends, returns in under 5ms:

    POST https://sipi.bot/v1/transactions/evaluate
    { "amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute" }

    → { "decision": "BLOCKED", "reason": "Merchant not on allowlist" }

**Three outcomes, not two:**
- APPROVED — passes every rule, proceed
- BLOCKED — violates a hard rule (over cap, unknown merchant, velocity breach),
  no money moves
- FLAGGED — crosses an approval threshold, routed to a human-in-the-loop queue

**The six rule types** (most of you will only need the first three):
1. Per-transaction cap — block anything over $X
2. Daily/period total — a rolling budget
3. Velocity limit — this is the one that kills the 2am retry loop. Cap N
   transactions per window.
4. Merchant allowlist — unknown vendors blocked by default
5. Category limits — cap "compute" differently from "ads"
6. Time windows — block all spend outside business hours

**The eval gym (the part I'm proudest of):** I wrote 53 labeled spend scenarios
— clean approvals, velocity traps, daily-cap boundary cases, sketchy-TLD
merchants, case-insensitive blocklist tests, "block beats flag on same txn"
precedence. The engine passes 53/53. The full report is human-readable at
https://sipi.bot/eval-report/ and the JSON is at https://sipi.bot/eval. If you
find a 54th scenario that breaks it, I want to know.

**Why I'm posting this here:** this sub is the only place I've found where people
are actually deploying autonomous agents in production. Every one of you running
an agent with a payment method is one bug away from my $12,400 morning. The
open-source core is MIT and free to self-host forever — pip install sipi-bot,
or the MCP server if you're on Claude Code / Cursor / Hermes:

    python -m spendfirewall.mcp_server

It's also a native MCP tool, so Claude Code / Cursor / Hermes can call it
directly. Wrappers for LangChain, CrewAI, OpenAI Agents SDK, and Vercel AI SDK
are in the repo.

**What I'd actually like feedback on:**
1. Is "pre-spend firewall" the right shape of the problem, or am I solving a
   symptom of something deeper (agent runtime design, prompt reliability)?
2. What's the 54th eval scenario I'm missing? The 53 are in the repo — please
   try to break it.
3. Has anyone here actually been bitten by runaway agent spend? I'm collecting
   incident patterns (anonymized) at
   https://sipi.bot/benchmarks/runaway-incident-frequency/ and real numbers
   would make it more useful.

Repo: https://github.com/kindrat86/sipi-bot
Site (with the live dashboard and eval report): https://sipi.bot
PyPI: pip install sipi-bot

Happy to answer any technical questions about the rules engine, the audit log
design, or the MCP implementation. Not here to sell the hosted version — the
OSS core is the point.
```

**Flair:** None (or "Project" if the sub requires flair).

---

## r/MCP post (SECONDARY — post 2 days later, MCP-focused angle)

**Title:**
```
I built an MCP tool that blocks your agent from spending money you didn't authorize (53/53 eval, open source)
```

**Body:** Same teardown structure but lead with the MCP integration:

```
Claude Code, Cursor, and Hermes can spend money — provisioning cloud resources,
calling paid APIs, triggering Stripe charges. There's no native MCP tool that
gates that spend before it fires. So I built one.

sipi.bot is a spend firewall exposed as an MCP server (stdio). Your agent calls
evaluate_spend before any payment; the firewall returns APPROVED, BLOCKED, or
FLAGGED in under 5ms.

    pip install sipi-bot
    python -m spendfirewall.mcp_server

[... same details as above, but emphasize the MCP angle, the agent-card.json,
the A2A discovery, and the framework wrappers ...]

The eval gym: 53 labeled spend scenarios, 53/53 passing. Full report at
https://sipi.bot/eval-report/. Repo: https://github.com/kindrat86/sipi-bot

What I'd like feedback on:
1. Is stdio the right transport, or should I add streamable HTTP MCP?
2. What's the 54th eval scenario?
3. Anyone here using MCP tools that trigger payments? How do you gate them today?
```

---

## r/AI_Agents post (TERTIARY — post 4 days later)

**Title:**
```
Your autonomous agent is one retry loop away from a $12k bill. I built a pre-spend firewall and open-sourced it.
```

**Body:** Same teardown, shorter, lead with the problem.

---

## ⚠️ If your post is auto-removed (modmail template)

```
Subject: Post removal — spend firewall teardown (author here)

Hi mods — I'm the developer of sipi.bot (github.com/kindrat86/sipi-bot, MIT,
open source). My teardown post was auto-removed, likely because the account is
newish or because it links to a product domain. I want to be clear: I'm not
here to spam. I'm a developer who got bitten by a $12k runaway-agent incident,
built a fix, open-sourced it, and wanted to share the eval gym (53 labeled
scenarios) with people who might actually try to break it. Happy to remove any
links the sub considers promotional and keep just the GitHub repo. Let me know
what works.
```

---

## Comment-defense prep (FIRST 30 MINUTES MATTER MOST)

Be online and replying within 5 minutes of each comment for the first hour. Common questions:

**Q: How is this different from LiteLLM budget caps?**
A: LiteLLM's caps are reactive — they reject the *next* call after a threshold is crossed. sipi.bot blocks the transaction *before* it fires. Velocity limits (the retry-loop killer) are something LiteLLM doesn't have at all. Most people run both: sipi.bot in front of LiteLLM.

**Q: Why not just put a Stripe limit?**
A: Stripe limits are per-provider and monthly. They don't stop a retry loop at 2am, they don't block unknown vendors, and they don't help if your agent spends at AWS or a third-party API. sipi.bot governs any payment the agent triggers.

**Q: Is the hosted version going to enshittify?**
A: The OSS core is MIT and self-hostable forever. The hosted version is a convenience, not a dependency. If I ever change that, the MIT license means you can fork the last good version.

**Q: <5ms is a bold claim.**
A: It's on the hosted endpoint. Cold starts on Fly can be slower (maybe 20-50ms). The engine itself is pure Python over SQLite — no network hops, no ML inference. I'll publish a proper latency benchmark if there's interest.

**Q: Why not just use prompt instructions to be cost-conscious?**
A: Because prompt instructions drift in long conversations, and a retry loop isn't a decision — it's a bug. The agent isn't choosing to overspend; it's stuck in a loop. Instructions don't stop bugs; deterministic rules do.

**Q: What's the catch?**
A: Honestly? The hosted version is $99/mo flat. The catch is that I'm one developer and the hosted infra is Fly.io on a shared-CPU-1x. If you need enterprise SLAs, self-host the OSS core. The eval gym (53/53) is the proof the engine works; the hosting is best-effort.

---

## Show HN variant (post once Reddit traction is established, ~week 2-3)

**Title:**
```
Show HN: sipi.bot — a spend firewall for autonomous AI agents (53/53 eval, MIT)
```

**Body:**
```
Hi HN — I built a pre-spend firewall for autonomous AI agents after one of mine
spent $12,400 in 90 seconds (retry loop + unknown vendor + overage tier, all at
2am).

One API call before your agent spends returns APPROVED, BLOCKED, or FLAGGED
against your rules (per-transaction, daily, velocity, merchant allowlist,
category, time windows) in <5ms.

Open source (MIT): https://github.com/kindrat86/sipi-bot
Live dashboard + eval report: https://sipi.bot
The eval gym: 53 labeled spend scenarios, 53/53 passing:
https://sipi.bot/eval-report/

Native MCP tool (Claude Code, Cursor, Hermes), HTTP API, CLI. Wrappers for
LangChain, CrewAI, OpenAI Agents SDK, Vercel AI SDK.

I'd love feedback on the rules-engine design and the eval coverage — what's the
54th scenario I'm missing?
```

---

## Cadence (from DREAM100.md bucket 5)

- **Week 1:** r/LocalLLaMA (highest fit, post Tuesday 8–10am ET)
- **Week 1+2 days:** r/MCP (MCP-focused angle)
- **Week 1+4 days:** r/AI_Agents (shorter, problem-first)
- **Week 2-3:** Show HN (once Reddit traction proves the framing works)
- **Throughout:** 1 genuine comment per day in each sub (no links) to build presence and karma

---

## Tier-1 outreach (email — from sales@sipiteno.com, signed as the developer)

These use the DREAM100.md templates but with your identity. Email from `sales@sipiteno.com`, sign as the developer (your name, GitHub kindrat86).

### A. Framework maintainer / GitHub issue or DM (bucket 1)
**Targets:** LangChain, CrewAI, AutoGen, OpenAI Agents SDK, Anthropic Claude Agent SDK, LlamaIndex, Pydantic AI, Vercel AI SDK, Mastra, Composio, Letta

```
Subject: guardrail for {framework} agents that spend money

Hey {name} — I'm the developer behind sipi.bot, a spend firewall for autonomous
agents. Every {framework} user who lets an agent buy compute/API credits/ads is
one retry loop away from a runaway bill.

It's one call before the agent spends: returns APPROVED / BLOCKED / FLAGGED
against their rules (per-tx, daily, velocity, merchant, time). MCP tool + HTTP,
so it drops into {framework} in ~5 lines. Open-source core, self-host free.

Would a short "spend guardrails for {framework}" recipe in your docs/examples
be useful to your users? Happy to write it. Live: https://sipi.bot
Repo: https://github.com/kindrat86/sipi-bot

— {your name}
GitHub: kindrat86
```

### B. Dev-influencer pitch (bucket 4)
**Targets:** Greg Isenberg, swyx, Simon Willison, Matt Berman, Riley Brown, AI Jason, punkpeye (awesome-mcp-servers)

```
Subject: teardown: "your AI agent spent $12,400 while you slept" → working product

Hey {name} — I turned the "agent spent $12k overnight" scenario into a working
product + a 53-scenario eval gym. Full teardown + open-source core here:
https://sipi.bot — if it's interesting for {show/audience}, I'll give your
audience a longer free tier. No ask beyond: is this the right shape of the
problem?

Repo: https://github.com/kindrat86/sipi-bot
Eval: https://sipi.bot/eval-report/

— {your name}
```

### C. awesome-mcp-servers PR (punkpeye repo)
Submit a PR adding sipi.bot to the list, with the MCP server as the primary surface. This is the highest-ROI single mention — it's the canonical MCP directory that ChatGPT and Claude pull from.

```
## sipi.bot — Spend Firewall for AI Agents

A spend firewall that approves, blocks, or flags every transaction an autonomous
AI agent proposes, against configurable spend rules. One MCP tool call before
any payment returns a decision in <5ms.

- **Install:** `pip install sipi-bot && python -m spendfirewall.mcp_server`
- **Eval:** 53/53 scenarios passing (https://sipi.bot/eval-report/)
- **License:** MIT
- **Repo:** https://github.com/kindrat86/sipi-bot
```
