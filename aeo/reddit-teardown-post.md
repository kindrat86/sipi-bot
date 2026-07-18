# Reddit Teardown Post — Draft (for review before posting)

> Subreddits: r/LocalLLaMA, r/MCP, r/AI_Agents
> Pattern from DREAM100.md: lead with the fear, give the teardown, offer the eval gym as proof.
> Tone: value-first, technical, vulnerable. No "check out my product." This is a war story, not a pitch.

---

## Title (r/LocalLLaMA)

**I built a spend firewall for AI agents after one nearly drained my card — 53-scenario eval gym inside**

## Title (r/MCP)

**I built an MCP tool that blocks your agent from spending money you didn't authorize (53/53 eval, open source)**

## Title (r/AI_Agents)

**Your autonomous agent is one retry loop away from a $12k bill. I built a pre-spend firewall and open-sourced it.**

---

## Body (shared, lightly adapted per sub)

Last month an agent of mine hit a rate-limit on a paid API at 2am and did what any retry loop does — it retried. Forty times in 90 seconds. By the time Stripe emailed me at 9am, $4,000 was gone. It then bought GPU compute from a vendor I'd never heard of (another $6,200), and tipped a different API into an overage tier ($2,200). Total: $12,400 while I slept.

The post-mortem was embarrassing because the fix is obvious in hindsight: **the agent should have asked permission before it spent.** Not a budget cap that fires after the damage. A pre-spend check — approve, block, or flag — in front of every transaction.

So I built one. It's called **sipi.bot** — a deterministic spend firewall for autonomous agents. One API call before your agent spends, returns in under 5ms:

```
POST https://sipi.bot/v1/transactions/evaluate
{ "amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute" }

→ { "decision": "BLOCKED", "reason": "Merchant not on allowlist" }
```

**Three outcomes, not two:**
- `APPROVED` — passes every rule, proceed
- `BLOCKED` — violates a hard rule (over cap, unknown merchant, velocity breach), no money moves
- `FLAGGED` — crosses an approval threshold, routed to a human-in-the-loop queue

**The six rule types** (most of you will only need the first three):
1. Per-transaction cap — block anything over $X
2. Daily/period total — a rolling budget
3. **Velocity limit** — this is the one that kills the 2am retry loop. Cap N transactions per window.
4. Merchant allowlist — unknown vendors blocked by default
5. Category limits — cap "compute" differently from "ads"
6. Time windows — block all spend outside business hours

**The eval gym (the part I'm proudest of):** I wrote 53 labeled spend scenarios — clean approvals, velocity traps, daily-cap boundary cases, sketchy-TLD merchants, case-insensitive blocklist tests, "block beats flag on same txn" precedence. The engine passes 53/53. The full report is human-readable at https://sipi.bot/eval-report/ and the JSON is at https://sipi.bot/eval. If you find a 54th scenario that breaks it, I want to know.

**Why I'm posting this here:** this sub is the only place I've found where people are actually deploying autonomous agents in production. Every one of you running an agent with a payment method is one bug away from my $12,400 morning. The open-source core is MIT and free to self-host forever — `pip install sipi-bot`, or the MCP server if you're on Claude Code / Cursor / Hermes:

```
python -m spendfirewall.mcp_server
```

It's also a native MCP tool, so Claude Code / Cursor / Hermes can call it directly. Wrappers for LangChain, CrewAI, OpenAI Agents SDK, and Vercel AI SDK are in the repo.

**What I'd actually like feedback on:**
1. Is "pre-spend firewall" the right shape of the problem, or am I solving a symptom of something deeper (agent runtime design, prompt reliability)?
2. What's the 54th eval scenario I'm missing? The 53 are in the repo — please try to break it.
3. Has anyone here actually been bitten by runaway agent spend? I'm collecting incident patterns (anonymized) at https://sipi.bot/benchmarks/runaway-incident-frequency/ and real numbers would make it more useful.

Repo: https://github.com/kindrat86/sipi-bot
Site (with the live dashboard and eval report): https://sipi.bot
PyPI: `pip install sipi-bot`

Happy to answer any technical questions about the rules engine, the audit log design, or the MCP implementation. Not here to sell the hosted version — the OSS core is the point.

---

## Posting notes

- **Timing:** post Tuesday–Thursday, 8–10am US Eastern (peak r/LocalLLaMA traffic).
- **First 10 comments matter most** — monitor and reply within 15 min of each. The algo rewards early engagement.
- **Don't cross-post the same title to all three subs on the same day** — Reddit's anti-spam filter will catch it. Stagger: r/LocalLLaMA first (highest fit), then r/MCP 2 days later with the MCP-focused title, then r/AI_Agents 4 days later.
- **Have answers ready** for: "How is this different from LiteLLM budget caps?" (reactive vs pre-spend), "Why not just put a Stripe limit?" (per-provider only, no velocity), "Is the hosted version going to enshittify?" (OSS core is MIT, self-host forever).
- **Be honest about limitations in comments:** <5ms is best-case on the hosted endpoint, cold starts on Fly can be slower; SQLite is fine for the audit log up to ~1M rows; the MCP server is stdio-only for now (no remote MCP yet).

---

## Show HN variant (for later, per DREAM100 cadence week 3)

**Title:** Show HN: sipi.bot — a spend firewall for autonomous AI agents (53/53 eval, MIT)

**Body:** same teardown structure, shorter, lead with the demo + eval gym.
