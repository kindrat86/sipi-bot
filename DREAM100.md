# sipi.bot Dream 100 — outreach playbook

> Brunson's Dream 100: the ~100 people/orgs who already have your dream customers'
> attention. For an agent-economy spend firewall, your buyer is **the developer
> deploying an autonomous agent** who is one infinite loop away from a $12,400
> Stripe bill. Dig the well before you're thirsty.

## The 5 buckets (where agent devs congregate)

### 1. Agent frameworks & their maintainers (highest intent)
These are the people whose users hit the exact pain sipi.bot solves.
- LangChain / LangGraph
- CrewAI
- AutoGen (Microsoft)
- OpenAI Agents SDK / Swarm
- Anthropic Claude Agent SDK
- LlamaIndex
- Pydantic AI
- Vercel AI SDK
- Smolagents (HuggingFace)
- Mastra (TS agent framework)
- Composio (tool-calling infra)
- Letta / MemGPT

### 2. Agent-commerce & payment-rails builders (adjacent thesis)
The x402 / AP2 / ACP crowd — they're building the money movement; you build the guardrail.
- Coinbase x402 team
- Skyfire (agent payments)
- Payman (AI agent payouts)
- Google AP2 (Agent Payments Protocol) contributors
- Nevermined (agent payments)
- Catena Labs / agent commerce
- Crossmint (agent wallets)

### 3. YC / accelerator agent startups (deploying agents in prod NOW)
Filter YC W25/S25/W26 for "AI agent" companies. They have budget and a live pain.
- Any YC co with "autonomous agent" / "AI employee" / "AI SDR" in the one-liner
- a16z speedrun agent cos
- South Park Commons agent builders

### 4. Dev-influencer amplifiers (distribution, not buyers)
They can put sipi.bot in front of the whole bucket #1 at once.
- Greg Isenberg (Startup Ideas pod — "agents is the new SaaS")
- swyx (Latent Space / AI Engineer)
- Simon Willison (LLM tooling blog)
- Matt Berman (YouTube, agent demos)
- Riley Brown / AI Jason (agent tutorials)
- The MCP / awesome-mcp-servers maintainer (punkpeye)

### 5. Communities (fish where they swim)
- r/LocalLLaMA, r/AI_Agents, r/MCP
- MCP Discord, LangChain Discord, CrewAI community
- AI Engineer Slack / Latent Space Discord
- Hacker News (Show HN)

## The outreach principle (Brunson + Isenberg fused)
- **Lead with the fear, in their words.** Not "spend management API." Instead:
  "your agent is one retry loop away from a $12k bill — here's the firewall."
- **Give the teardown, not the pitch.** Send the workflow teardown ("$12,400 while
  you slept") as the opener. Painkiller, not vitamin.
- **Offer the eval gym as proof.** "We tested it on 53 spend scenarios, here's the
  100% report" — transparency builds trust with skeptical devs.
- **Sell the outcome.** Pilot = "we make sure your agent never spends a dollar you
  didn't authorize," $99/mo, guarantee attached.

---

## Message templates

### A. Framework maintainer / GitHub issue or DM (bucket 1)
> Subject: guardrail for {framework} agents that spend money
>
> Hey {name} — I build sipi.bot, a spend firewall for autonomous agents. Every
> {framework} user who lets an agent buy compute/API credits/ads is one retry
> loop away from a runaway bill.
>
> It's one call before the agent spends: returns APPROVED / BLOCKED / FLAGGED
> against their rules (per-tx, daily, velocity, merchant, time). MCP tool + HTTP,
> so it drops into {framework} in ~5 lines. Open-source core, self-host free.
>
> Would a short "spend guardrails for {framework}" recipe in your docs/examples
> be useful to your users? Happy to write it. Live: https://sipi.bot

### B. Agent-commerce / x402 builder (bucket 2)
> You're building the rails for agents to move money. I'm building the guardrail
> that keeps them from moving the WRONG money. sipi.bot sits in front of every
> agent transaction and approves/blocks/flags it against policy before it fires —
> the compliance twin to x402's payment. Complementary, not competitive. Worth a
> 15-min call on how they compose?

### C. YC / startup founder (bucket 3) — the pilot offer
> Saw {company} is shipping autonomous agents. Quick q: what stops one of your
> agents from an infinite-loop spend at 3am right now?
>
> sipi.bot is that stop. One API call before any agent spend → APPROVED / BLOCKED
> / FLAGGED against your rules. I'll set up a free pilot on your real spend
> patterns and show you the eval report. If it ever green-lights a spend that
> breaks your rule, you don't pay. Interested?

### D. Influencer / teardown pitch (bucket 4)
> I turned "your AI agent spent $12,400 while you slept" into a working product +
> a 53-scenario eval gym. Full teardown + open-source core here: https://sipi.bot
> — if it's interesting for {show/audience}, I'll give your audience a longer
> free tier. No ask beyond: is this the right shape of the problem?

## Cadence
- Week 1: buckets 1 + 2 (10 framework maintainers, 5 payment builders) — the
  highest-intent, lowest-volume, relationship plays.
- Week 2: bucket 3 (20 YC agent cos) with the pilot offer (template C).
- Week 3: bucket 4 (influencers) + Show HN once PyPI + registries are live.
- Throughout: 1 workflow-teardown post per platform per week (bucket 5).
