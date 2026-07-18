# Framework-by-framework outreach checklist

> **Targets from DREAM100.md bucket 1 + bucket 2.**
> **Send from:** sipi@sipi.bot
> **Signed as:** your name, creator of sipi.bot (GitHub: kindrat86)
> **Cadence:** 2–3 emails per day, week 1 (not all at once — space them out)

---

## Phase 1 — Framework maintainers (bucket 1: highest intent)

These are the people whose users have the exact pain sipi.bot solves. Each one gets the tailored email template below.

| # | Target | Framework / Org | Why them | Priority |
|---|---|---|---|---|
| 1 | LangChain / LangGraph maintainers | `info@langchain.dev` or GitHub DM | 200K+ agents deployed; direct sipi.bot wrapper exists | P1 |
| 2 | CrewAI (João Moura) | `joao@crewai.com` or GitHub | Multi-agent swarms compound spend risk; wrapper exists | P1 |
| 3 | OpenAI Agents SDK team | GitHub issue or `api-feedback@openai.com` | SDK has no spend controls; wrapper exists | P1 |
| 4 | Anthropic Claude Agent SDK | GitHub or developer-relations | Native MCP integration; wrapper exists | P1 |
| 5 | Vercel AI SDK (Jared Palmer / Lee Robinson) | GitHub or Twitter DM | Edge-deployed agents spend fast | P1 |
| 6 | LlamaIndex (Jerry Liu) | GitHub | Tool-calling agents that call paid APIs | P2 |
| 7 | Pydantic AI (Samuel Colvin) | GitHub | Type-safe agent framework; growing quickly | P2 |
| 8 | Mastra (Stephane Amans) | GitHub | New TS agent framework | P2 |
| 9 | Composio (tool-calling infra) | GitHub | Their users already trigger external API calls | P2 |
| 10 | Letta / MemGPT (Charles Goddard) | GitHub | Long-running agents accumulate more spend | P2 |

## Phase 2 — Agent-commerce builders (bucket 2: adjacent thesis)

These are building the rails sipi.bot governs.

| # | Target | Rail | Why them | Priority |
|---|---|---|---|---|
| 1 | Coinbase x402 team | x402 | sipi.bot is the compliance layer in front of x402 wallets | P1 |
| 2 | Google AP2 team | AP2 | Agent Payment Protocol — sipi.bot composes | P1 |
| 3 | Skyfire (agent payments) | Skyfire | Complementary — they move money, we guard it | P1 |
| 4 | Payman (AI payouts) | Payman | Agent-to-agent payouts | P2 |
| 5 | Nevermined (agent payments) | Nevermined | Agent commerce infrastructure | P2 |
| 6 | Crossmint (agent wallets) | Crossmint | Wallet infra for agents | P2 |
| 7 | Catena Labs | Catena | Agent-commerce research | P2 |

## Phase 3 — Dev-influencers (bucket 4: distribution)

| # | Target | Platform | Why them | Priority |
|---|---|---|---|---|
| 1 | punkpeye | GitHub | awesome-mcp-servers maintainer. A PR here is the highest-ROI single mention. | P1 |
| 2 | swyx (Latent Space) | Twitter / podcast | AI Engineer audience; covers agent tooling | P1 |
| 3 | Simon Willison | Blog / Twitter | LLM tooling authority; has written about MCP | P1 |
| 4 | Greg Isenberg | Newsletter / podcast | "Agents is the new SaaS" — his audience is sipi.bot's buyer | P2 |
| 5 | Matt Berman | YouTube | Agent demo audience | P2 |
| 6 | Riley Brown | YouTube | Agent tutorials | P2 |
| 7 | AI Jason | YouTube | Agent tutorials | P2 |

## Suggested order of operations

```
Week 1 (Mon-Wed):  awesome-mcp-servers PR (30 sec once submitted)
Week 1 (Mon-Fri):  Framework maintainers #1-6 (2/day)
Week 2 (Mon-Wed):  Framework maintainers #7-10 + Agent-commerce #1-3
Week 2 (Thu-Fri):  Agent-commerce #4-7 + Influencers #2-3
Week 3:            Influencers #4-7
```

## Email template (same for all Phase 1)

```
To: {framework maintainer}
From: sipi@sipi.bot
Subject: spend guardrails for {framework} agents

Hey {name} — I build sipi.bot, a spend firewall for autonomous agents. Every
{framework} user who lets an agent buy compute/API credits/ads is one retry loop
away from a runaway bill.

It's one API call before the agent spends: returns APPROVED, BLOCKED, or FLAGGED
against their rules (per-tx, daily, velocity, merchant, time). MCP tool + HTTP,
drops into {framework} in ~5 lines. MIT-licensed OSS core, free to self-host.

There's already a wrapper in the repo for {framework}. Would a short recipe in
your docs/examples be useful to your users? Happy to write the PR.

53-scenario public eval: https://sipi.bot/eval-report/
Repo: https://github.com/kindrat86/sipi-bot

— {your name}
sipi@sipi.bot
```
