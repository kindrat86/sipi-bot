# sipi.bot — Third-Party Trust Signal Outreach Kit

**Status:** 0 stars, 0 forks on GitHub (MIT, public). No press coverage. No named testimonials.  
**Goal:** Generate the first 3–5 real third-party endorsements (named testimonial, case study, press mention).  
**Founder:** Maryan — solo, Kifisia, Greece. AI infrastructure engineer since 2024. Ships fast.  
**Site:** https://sipi.bot | **Repo:** https://github.com/kindrat86/sipi-bot  
**Pricing:** Self-host (free/MIT) → Team $99/mo → Business $499/mo  

---

## 1. Quick wins (3 hours total)

### 1a. GitHub social proof — seed the stars

The repo has **0 stars**. The single biggest unlock for a 0-star repo is getting 5–10 stars from people who actually find it useful. Before any press outreach:

1. **Join communities where this repo is relevant** and post "built this, would love feedback":
   - r/MCP — post the MCP tool (`sipi-guard`)
   - r/AI_Agents — post the origin story (the $12.4k incident)
   - Hacker News "Show HN" — write a 2-paragraph submission
   - dev.to / Medium — cross-post the origin story as a blog
2. **Ask existing early users** (anyone who's tried it) to star the repo — single ask, no pressure.
3. **Add a GitHub Star badge** to the README once you hit ~5+ stars — visible social proof for anyone landing on the page.

### 1b. Product Hunt / Indie Hackers launch

Product Hunt launch is the highest-leverage single action for a 0-traction dev tool:
- Prep a PH listing with the origin story as the narrative hook
- Target "Developer Tools" category
- Ask your network (personal Twitter/X, LinkedIn) to upvote on launch day
- Cross-post to Indie Hackers the same day

### 1c. Turn existing anonymous quotes into attributed testimonials

The homepage already has 3 anonymous "What Builders Say" quotes. If these are from real users:
1. **DM each one** and ask: *"Would you be up for having your name and company attached to that quote? Happy to adjust the wording."*
2. If they agree, add `— Name, Company, Role` attribution on the site.
3. Even 1–2 attributed quotes transform the page from "looks like we wrote these ourselves" to "real people use this."

If these quotes are synthetic/mockups (placeholder for launch): **replace with nothing** until real ones come in. Empty is better than fake.

---

## 2. Press outreach — target list + templates

### Target publications (in priority order)

| Publication | Why | Pitch angle |
|---|---|---|
| **The Generalist** | Covers AI infrastructure, agent economy | "The $12.4k agent that bankrupt itself overnight" |
| **TechCrunch** | Startup/product launches | "AI spend guardrail exits stealth" |
| **TheNewStack** | Developer tooling, open-source | "MIT spend firewall for autonomous agents" |
| **MCP.so blog** | MCP ecosystem tooling | New MCP server for spend control |
| **Indie Hackers** | Solo founder audience | "Solo dev ships spend firewall after losing $12.4k to own agent" |

### Pitch template (cold email / DM)

```
Subject: sipi.bot — the $12.4k agent incident that became an open-source product

Hi [NAME],

I'm Maryan, a solo founder in Greece. Three months ago, my own autonomous 
agent spent $12,400 overnight — buying GPU compute, retrying into rate limits, 
hitting vendors I'd never heard of — while I slept. The money moved because 
no layer between the agent's decision and the payment API asked "should this 
happen?" before the charge went through.

I built that missing layer: sipi.bot (https://sipi.bot). It's an open-source 
(MIT) spend firewall for AI agents — one HTTP call returns approve/block/flag 
in under 5ms before any money moves, enforcing per-transaction caps, daily 
limits, velocity rules, merchant allow/block lists, and human-in-the-loop 
approval. The same core is free to self-host; the hosted version starts at $99/mo.

It integrates via MCP tool (Claude Code, Cursor, Copilot), HTTP API, or CLI.
53/53 tests passing. MIT. Built with stdlib only — no framework, no ML.

Would you be interested in:

[CHOOSE ONE]
— A 5-minute demo / screenshare
— A writeup of the origin story + technical architecture
— An interview about building in the agent-economy infrastructure layer

Happy to tailor the angle however works for your audience.

Best,
Maryan
sipi.bot — https://sipi.bot
```

---

## 3. Case study — write the first one yourself (30 min)

Before you can ask others for a case study, **you need something to show what one looks like**. Write a short internal case study based on the origin story — it's real, it's vivid, and it's the strongest sales tool you have.

Suggested structure for a 500-word case study:

```
# How my own AI agent spent $12,400 while I slept — and the firewall I built to stop it

[200 words: The incident — deployment, the 2:14 AM log entry, the 40 retries, 
the unknown-gpu.ru merchant, the Stripe notifications at 7 AM]

[150 words: What I looked for and why nothing fit — OpenAI caps (per-provider, 
reactive), Stripe Radar (fraud, not policy), human babysitters ($4,500/mo). 
Identified the gap: no pre-spend control layer existed for agent transactions.]

[150 words: What I built — sipi.bot's architecture (deterministic rules engine, 
5ms evaluation, tamper-evident audit log). Key design decisions: HTTP-first 
so any agent can call it, MCP-native so agent frameworks use it natively, 
MIT open-source so anyone can self-host the exact same engine.]
```

**Publish this case study:**
1. On **sipi.bot/blog/** — the site needs a blog; create a minimal `/blog` route pointing to this post
2. Cross-post to **dev.to** and **Medium** (free, high discoverability for dev audience)
3. Link to it from the homepage ("Read the full story →")

---

## 4. Longer-term plays

### Open-source community building
- Add a `CONTRIBUTING.md` with "good first issue" tags
- Promote in the MCP Discord, LangChain community, CrewAI community
- Write a "how to add a custom rule type" tutorial

### MCP directory presence
- List on https://github.com/modelcontextprotocol/servers
- List on https://mcp.so (glama.ai)

### Speaking / podcast
- Apply to talk at AI Engineer Summit, Agent Conf, or local meetups
- Pitch to "Latent Space" or "Last Week in AI" podcasts with the origin story

---

## 5. One-pager summary (for quick reference)

| Action | Time | Impact | Difficulty |
|---|---|---|---|
| Ask early users to star GitHub repo | 15 min | High | Trivial |
| DM anonymous quote authors for attribution | 30 min | High | Trivial |
| Post origin story as blog on dev.to + Medium | 1 hr | Medium | Low |
| Product Hunt launch | 3 hrs prep + 1 day | High | Medium |
| Cold-pitch top-3 press targets | 1 hr | Medium | Medium |
| Write + publish case study on sipi.bot/blog | 30 min | High | Low |
| MCP directory listings | 30 min | Medium | Trivial |
| HN Show HN post | 30 min | Medium | Low |
| Contribute to MCP ecosystem discussions | Ongoing | Medium | Low |
