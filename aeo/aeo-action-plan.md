# AEO Action Plan — sipi.bot

**Generated:** 2026-07-18 · **Method:** Ahrefs AEO methodology (AEO Architect skill)
**Brand:** sipi.bot — The Spend Firewall for AI Agents
**Domain:** https://sipi.bot · **Repo:** ~/projects/sipi-bot
**Priority platforms:** ChatGPT · Google AI Overviews · Perplexity (in that order — see §5)

---

## Executive summary — the one-paragraph version

sipi.bot's **technical AEO is best-in-class** (AI bots fully allowed at robots.txt AND edge, rich JSON-LD schema, llms.txt + agents.md + agent-card.json + knowledge-graph.json, FAQPage + SoftwareApplication + Organization markup, disambiguatingDescription for name collisions, fresh content updated 2026-07-17, sitemap with 108 URLs). You've nailed every technical lever the AEO course names. **But AI visibility is still ~zero** because the *single strongest signal* — **branded web mentions on third-party pages (r=0.664 with AI Overviews)** — is at zero. No listicle, Reddit thread, blog, review, or publication mentions sipi.bot. AI engines don't yet have a source to cite. The fix is not more on-site content — it's **earning mentions off-site** so AI has something to retrieve and consensus to form around. This plan sequences that work.

**The headline opportunity:** the "AI agent spend control" category is greenfield. No incumbent owns it. The brand that defines the category first — across enough independent sources that AI reaches consensus — wins durable visibility. sipi.bot is positioned to be that brand; the work below is how to make it so.

---

## Phase 0 — Scope (locked)

| Field | Value |
|---|---|
| **Brand** | sipi.bot (alternate: sipibot, sipi bot, "sipi.bot Spend Firewall") |
| **Sub-brands / surfaces** | MCP server · HTTP API · CLI (`pip install sipi-bot`) · Agent card (A2A) |
| **Proprietary vocabulary** | "spend firewall" · agent spend policy · daily spend ceiling · merchant allowlist · per-transaction limit · cost anomaly · agent audit trail · agent cost center |
| **Business type** | Product / SaaS (developer infrastructure, flat-rate $99/$499) |
| **Buyer** | Developer deploying an autonomous AI agent (one infinite loop from a $12k bill) |
| **Competitors (adjacent)** | LiteLLM, Helicone, Portkey, Langfuse, OpenRouter, OpenMeter, LangSmith, AWS Budgets, OpenAI spending limits — *none solve the actual pre-spend problem, all are observability/billing* |
| **Priority platforms** | ChatGPT → Google AIO → Perplexity |
| **Tooling available** | check_ai_bots.py ✅ · Ahrefs: ❌ · GA4: ❌ (no tracker detected) · GSC: not checked |

**Branded-entity note:** "spend firewall for AI agents" is a coined category term. Label every original framework with the brand name ("the sipi.bot 5ms Decision Pattern", "the sipi.bot Spend Firewall architecture") and distribute widely — LLMs flatten un-attributed originality into generic knowledge.

---

## Phase 2 — Brand gap analysis (summary)

Eight gaps logged in [`brand-gap-analysis.csv`](./brand-gap-analysis.csv). Ranked by impact:

| # | Gap | Type | Priority |
|---|---|---|---|
| 1 | **Zero third-party mentions anywhere on the web** (r=0.664 signal = 0) | web-mentions | **P1** |
| 2 | **Category is undefined** — AI has no consensus answer for "stop my agent overspending" | narrative | **P1** |
| 3 | **All 16 /vs pages are 120–230 words** (below Bing's 300-word thin-content threshold, Rule 115) | topic | **P1** |
| 4 | **Brand invisible for category queries** (0 DDG results for "spend firewall AI agent" etc.) | visibility | **P1** |
| 5 | 23 /for/* pages are ~90 words each (wasted demand-capture surface) | demand | P2 |
| 6 | **Zero YouTube presence** (strongest single AI-citation channel, r=0.737 with ChatGPT) | format | P2 |
| 7 | Name-collision risk (SIP/VoIP, Sipi Capital, arkhann00/sipi_bot) | visibility | P2 |
| 8 | Glossary terms need external citations to cement category ownership | topic | P3 |

**Technical audit: PASS.** ✅ robots.txt + edge both clean (all AI bots HTTP 200). ✅ Rich schema (Organization, WebSite, WebPage, Breadcrumb, SiteNavigation, SoftwareApplication, FAQPage). ✅ AI-discovery files: llms.txt, llms-full.txt, agents.md, agents.txt, qa.jsonl, knowledge-graph.json, openapi.json, agent-card.json, mcp.json. ✅ Freshness: lastmod 2026-07-17. ✅ 108 URLs in sitemap across 16 buckets (for, vs, glossary, learn, integrations, faq, etc.).

---

## Phase 3 — Execution (the plan, prioritized)

### §1 · This week — quick wins (Fix)

| # | Action | Effort | Why |
|---|---|---|---|
| 1.1 | **Expand the top-6 /vs pages to 600–900 words each** — LiteLLM, Helicone, OpenRouter, Portkey, Langfuse, OpenMeter. Structure: BLUF verdict → feature comparison table → "when to pick X / when to pick sipi.bot" → pricing → code snippet. Target the exact "X vs Y" queries AI already answers. | M | Highest-ROI Fix. Pages exist, target high-intent queries, and 43.8% of ChatGPT citations are listicles/comparisons. Currently too thin to cite. **✅ DONE 2026-07-18** |
| 1.2 | **Install GA4 + add "How did you hear about us?" with AI options** (ChatGPT / Perplexity / Google AI Overview / Claude / Copilot / Reddit / HN / Other). You currently have NO analytics — can't measure what you can't see. | S | Measurement is Phase 4 but starts now. **✅ DONE 2026-07-18** (GA4=G-F5R5Y29J1F on all pages; attribution dropdown live) |
| 1.3 | **Refresh homepage with one original stat** (e.g., "53/53 eval scenarios" → make it a labeled framework: "the sipi.bot Eval Gym — 53 adversarial spend scenarios, 100% pass rate"). Original data is what AI loves to cite. | S | Freshness + brand-labeled originality. **✅ DONE 2026-07-18** |
| 1.4 | **Submit to Bing Webmaster Tools + IndexNow** (key already exists in memory: sipi.bot=9769ace5). Bing powers Copilot — direct AEO lever. | S | Copilot visibility. **⚠️ BLOCKED** — Bing IndexNow 403s until site is verified in Bing WMT (needs Microsoft OAuth, no API bypass). User must verify manually. Sitemap updated with cornerstone URL (priority 0.9). |

### §2 · Weeks 1–4 — own the category (Build)

| # | Action | Effort | Why |
|---|---|---|---|
| 2.1 | **Consolidate 23 thin /for/* pages into 4–5 hub pages** OR expand top 5 (openai-agents, anthropic-agents, trading-bots, ai-coding-agents, ai-developers) to 400+ words each with real use-case narrative + code. | M | Avoid thin-content cannibalization; capture demand that currently bounces. |
| 2.2 | **Publish 1 definitive cornerstone: "The Spend Firewall for AI Agents: A Complete Guide"** (2,500+ words). Define the category, the 6 rule types, the architecture, benchmarks. This is the page you want AI to cite when asked "how do I control my AI agent's spending." | L | Establishes category authority — the unit of work is the *topic*, not the keyword (query fan-out = 9–28 sub-queries). **✅ DONE 2026-07-18** (`/learn/spend-firewall-guide`, 2,486 words, Article+HowTo+FAQ+Breadcrumb schema) |
| 2.3 | **Publish original benchmark content** (you already have /benchmarks/* — promote it). "Agent spend as % of revenue", "AI agent cost per task", "Runaway incident frequency", "Token cost by provider". Original data = citation magnet. | M | AI loves citing specific numbers. This is your moat — competitors don't have it. |
| 2.4 | **Record 3 YouTube search-hit videos** (see §4 below). | M | YouTube = strongest single AI-citation channel. |

### §3 · Weeks 1–12 — earn mentions (Influence) — **THE #1 LEVER**

This is where AI visibility actually comes from. Branded web mentions had the **strongest correlation (r=0.664)** with AI Overviews in the 75,000-brand study. Currently at zero. Three tiers:

**Tier 1 — Third-party editorial / listicles (highest value, hardest)**
- Target every "best LLM cost management tools" / "AI observability tools" / "LLM gateway comparison" listicle. Use DREAM100.md buckets 1+2 as the outreach pool.
- Specific Tier-1 targets to pitch: dev.to, hackernoon, Latent Space blog, Simon Willison's blog, Greg Isenberg newsletter, awesome-mcp-servers (punkpeye), awesome-ai-agents lists.
- Pitch angle (from DREAM100.md): *"your agent is one retry loop away from a $12k bill — here's the firewall. 53-scenario eval gym, open-source core."*
- **Goal: 10 listicle mentions in 90 days.**

**Tier 2 — Community / Reddit / HN (fastest, high AI-citation weight)**
- Reddit is one of ChatGPT's most-cited sources. Post real value (not spam) to: **r/LocalLLaMA, r/AI_Agents, r/MCP, r/LangChain, r/CrewAI**.
- Find existing threads asking "how to limit my agent's spending" / "agent ran up a huge bill" — these exist. Answer with the teardown.
- **Show HN** once PyPI + registries are clean (DREAM100 bucket 5 cadence).
- **Goal: 1 substantive Reddit post/week for 8 weeks.**

**Tier 3 — Own additional surfaces**
- GitHub repo (exists ✅ — ensure README links to sipi.bot prominently).
- PyPI project page (exists ✅ — optimize long description with category keywords).
- LinkedIn page for sipi.bot (create).
- dev.to / Medium cross-posts of the cornerstone guide (2.2).
- A weekly "agent economy spend" post on X (builds training-data presence).

### §4 · YouTube (Build — highest single-channel ROI)

YouTube mentions correlate **0.737** with ChatGPT visibility — the strongest single factor. Currently: zero presence.

Three search-hit videos to record (not viral hits — *search hits*):
1. **"How to stop your AI agent from overspending"** — the core problem→solution. Title = exact search query.
2. **"sipi.bot vs LiteLLM"** — piggybacks on the /vs content. Comparison videos rank well.
3. **"Set a spending limit on Claude Code / Cursor (MCP tutorial)"** — tutorial format, MCP-native.

Checklist per video: keyword in title ✅ · real description with keyword in first 2 lines ✅ · timestamps/chapters ✅ · say the keyword in the video ✅ · match format to what ranks (tutorials dominate → make tutorials) ✅.

### §5 · Per-platform strategy (distinct, not a name-check)

Only ~14% of the top-50 cited domains appear on all of Google AIO + ChatGPT + Perplexity. Each has its own index and bias — give each a distinct tactic:

- **ChatGPT** → its most-cited sources are high-DR editorial/listicles + Reddit. Win here via §3 Tier-1 + Tier-2. ChatGPT's crawler does NOT render JS — your site is server-rendered HTML ✅, so you're fine. Push for mentions on Reddit and dev.to specifically.
- **Google AI Overviews / AI Mode** → crawls with regular Googlebot (not Google-Extended), so your clean robots.txt covers it. YouTube ≈5.6% of AIO citations → §4 videos are the lever here. Also: rank in Google's top 10 for "AI agent spend control" terms (~38–76% of AIO citations come from existing top-10 pages). Your /vs and /for pages are the ranking play.
- **Perplexity** → ~28.6% of its citations come from Google's top 10, so it's the **fastest win if you already rank**. Lean on the /vs comparison pages (once expanded, §1.1) and the cornerstone guide (§2.2). Perplexity also favors consensus — the more Tier-1 mentions you earn, the faster Perplexity picks you up.
- **Copilot (Bing)** → submit to Bing WMT + IndexNow (§1.4). Bing indexes more conservatively; get the site verified first.

---

## Phase 4 — Measure (setup now, review monthly)

| Signal | How | Cadence |
|---|---|---|
| **AI referral traffic** | GA4 "AI traffic" channel (sessions from chatgpt.com, perplexity.ai, gemini.google.com, copilot.microsoft.com, you.com, claude.ai) | weekly |
| **Self-reported attribution** | "How did you hear about us?" with AI options on signup (§1.2) | weekly |
| **AI bot crawl** | check_ai_bots.py sipi.bot --edge (already PASS) | monthly |
| **Mention tracking** | Google Alerts for "sipi.bot" + "spend firewall" + "sipi-bot"; DDG search for brand+modifiers | monthly |
| **AI visibility pulse** | Manually ask ChatGPT/Perplexity/Gemini "best way to control AI agent spending" / "sipi.bot" weekly; log whether mentioned | weekly (first 90 days) |
| **Brand Radar (if Ahrefs added)** | Mentions / Citations / AI Share of Voice vs competitors | monthly |
| **404 from hallucinated URLs** | GA4 → pages with AI-referrer traffic returning 404 → redirect to nearest real page | monthly |

**Re-run cadence:** >45% of AI Overview citations change on refresh (~every 2 days). Bake in a monthly Brand Radar check + quarterly competitive audit.

---

## What to do first (if you only do 3 things this week)

1. **§1.1** — Expand the top-6 /vs pages (LiteLLM, Helicone, OpenRouter, Portkey, Langfuse, OpenMeter) to 600–900 words each. Fastest content win, targets the exact queries AI answers.
2. **§1.2** — Install GA4 + add "How did you hear about us?" with AI options. You're flying blind without it.
3. **§3 Tier-2** — Post the "$12,400 while you slept" teardown to r/LocalLLaMA + r/MCP. First mention seed.

Then §2.2 (cornerstone guide) and §4 (YouTube) in weeks 2–4, §3 Tier-1 outreach ongoing through week 12.

---

## Artifacts

- `brand-gap-analysis.csv` — full 8-gap map with Fix/Build/Influence tags
- `check_ai_bots.py` output — robots.txt + edge audit (all PASS)
- This plan — `aeo-action-plan.md`
