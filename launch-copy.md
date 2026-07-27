# sipi.bot — Launch & Distribution Playbook

## What was built (July 2026)

| Surface | Pages | Key assets |
|---------|-------|------------|
| AI Agent Incident Database | 36 (hub + 34 detail + stats) | CC BY 4.0, JSON/CSV/JSONL, Dataset + Article JSON-LD |
| Blog | 9 (hub + 8 posts) | Long-form, Article + BreadcrumbList JSON-LD |
| Free tools | 3 (risk calculator + policy generator + hub) | Client-side JS, SoftwareApplication + HowTo JSON-LD |
| Freshness surfaces | 2 (changelog + status) | Trust pages |
| Existing site deepening | 1 (benchmarks page) | Back-cited to incident DB, Dataset JSON-LD |
| RSS feed | enriched with 9 items | Blog + incident entries |
| llms.txt | updated | Incident DB + data endpoints + tools |
| IndexNow | auto-ping on deploy | All new URLs |
| **TOTAL** | **+60 new indexed pages** | **~120 new JSON-LD blocks** |

Plus: `lib/common.py` shared design system, `build.py` orchestrator, `data/incidents.json` canonical dataset.

---

## Now: the launch — run these in order of ROI

### 1. Show HN (first session — highest single ROI action)

Lead with the **open dataset**, not the product. The dataset is the story.

**Title:**  
`Show HN: Open database of AI agents that lost money, deleted data, or breached policy (CC BY 4.0)`

**Body:**
```
34 documented incidents, $2.91 billion in tracked exposure. Every record links to
a real public source — a news article, post-mortem, security report, or official
statement. The database spans 2016-2026 and ranges from a $31 unauthorized grocery
delivery to $2.87B in aggregate crypto theft.

I built this after losing $12,400 overnight to a runaway agent loop. The prompt
said "minimize spend." The agent heard "experiment with spend." I woke up to the
bill and realized: there is no canonical source for how much AI agents actually
cost when they go wrong. Every conversation about "AI agent safety" is missing the
data. So I built the data.

The database is licensed CC BY 4.0, lives on GitHub with a weekly auto-sync, and
is available as JSON, CSV, and JSON Lines at /data/ai-agent-incidents.json.

It's also the data source behind a free risk calculator (estimate your worst-case
loss from your agent config) and a spend-policy generator (ready-to-paste firewall
ruleset in JSON + YAML + curl). All client-side, no signup.

If you know an incident I'm missing, open an issue with a link to a credible source
and I'll add it — this is community-maintained.
```

**Timing:** Tuesday–Thursday morning (US time). Add the `Show HN` tag.

**Links to include:** `/incidents/`, `/data/ai-agent-incidents.json`, GitHub dataset repo, risk calculator.

---

### 2. Reddit (second session — same afternoon or next day)

Lead with the free risk calculator + open dataset. Target these subreddits in order:

#### r/LocalLLaMA (highest signal for agent-builders)
**Title:** `I built a free risk calculator for AI agents — calibrated on 34 real-world incidents`

**Body:**
```
The calculator estimates your worst-case 24h loss and gives a risk score from 1-10.
No backend, no signup — the math runs in your browser. Inputs: how many spending
tools your agent has, your largest single-transaction risk, whether it runs
unattended, and whether it retries on failure.

Calibrated on 34 documented incidents I've been collecting — from a $47K overnight
runaway loop to a $441K tweet-misread crypto transfer. The median overnight loss
in the database is ~$30K for unattended agents with retries enabled.

Also built a spend-policy generator that outputs ready-to-paste firewall rules in
JSON + YAML + curl. Both free, both client-side.

The incident database is CC BY 4.0 if you want to use it for your own research.
If you know an incident I'm missing, drop the link and I'll add it.
```

#### r/MachineLearning
**Title:** `[D] 34 documented AI agent incidents — a sourced, open dataset of losses`

Focus on the dataset as a research resource. Cite the NeuralTrust 88.4% incident rate and the 7 hallucinated-policy incidents.

#### r/cybersecurity
**Title:** `Open database of AI agent security incidents — prompt injection, data exfiltration, credential compromise`

Focus on the security angle: 6 prompt-injection incidents, the Operator data-exfiltration exploit, the WalletConnect drainer.

#### r/SaaS, r/devops
Focus on the practical angle: "here's how much a runaway agent costs you, here's the free tool to estimate yours."

**The crowdsourcing ask on every post:**  
"If you know an incident I'm missing, drop the link and I'll add it — this is community-maintained." This is the voicelogpro pattern — it drives engagement, accuracy, and repeat visits.

---

### 3. Listicle outreach (third session — ongoing)

The existing 10 `/best/` pages and 26 `/vs/` pages target the exact listicles where sipi.bot needs to appear. The pitch:

**Subject:** `Your "best AI agent cost tools" list is missing a data-backed option`

**Template:**
```
Hi [name] — I maintain the AI Agent Incident Database, a CC BY 4.0 dataset of 34
real-world AI-agent incidents (from a $47K overnight runaway loop to the $27M Step
Finance exploit). Every record links to a public source.

You wrote [article title], which covers tools in this space. Two things that might
add value to your list:

1. The incident database is free to cite and link — researchers and journalists
   reference it as a primary source.
2. The free risk calculator (/tools/agent-spend-risk-calculator/) gives readers an
   instant worst-case loss estimate from their own agent config — it's the kind of
   interactive element that keeps people on the page.

Either would make the list stronger. Let me know if you want a quote, a data point,
or a specific comparison against any tool on your list.

Thanks — [your name]
```

**Target sites:** The dozen or so "best AI agent cost monitoring tools" / "best AI spend management platforms" listicles that rank on Google and don't list sipi.bot. Find them by searching the target keywords from the `/best/` page titles. The incident database is the credibility hook that gets you past the "just another tool pitch" filter.

---

### 4. Embed badge push (fourth session — ongoing)

The "Protected by sipi.bot" badge (`/badge`) is a free, no-JS, dofollow-backlink engine already deployed. Push it to 20–30 agent-framework READMEs, docs sites, and devtool landing pages.

**Pitch:**
"Add this 1-line image tag to your README or docs site and show live stats from our firewall. Free, no account needed, no JS. Each embed is a permanent backlink to your site."

The badge URL includes live decision counts — it's a trust signal that updates in real time. Target repos that already list MCP tools, agent frameworks, and AI infrastructure projects.

---

### 5. Press the data (when an incident makes the news)

The incident database is a **news-jacking engine**. When the next runaway-agent incident hits the news (and it will, within weeks — there have been 3 major documented incidents in the last 6 months alone):

1. Add the record to `data/incidents.json`.
2. Run `python3 build.py --ping`.
3. Within one deploy, `/incidents/<id>/` is live with a sourced detail page, a firewall-relevance breakdown, and a shareable URL.
4. Post to Reddit/HN: "New entry in the AI Agent Incident Database: [incident]. Here's which firewall rules would have caught it."
5. The RSS feed auto-updates. RSS aggregation sites pick it up.

This is the **freshness cycle** that makes the database the canonical reference and compounds every time an incident happens.

---

## Measurement (so you know what's working)

### Immediate (before launch):
- [ ] GA4 or PostHog "AI traffic" channel: tag ChatGPT, Perplexity, Gemini, Claude, Copilot referrers as a single segment so you can isolate AI-referral traffic from organic.
- [ ] Add a "How did you hear about us?" multi-select to the signup flow with: `Hacker News`, `Reddit`, `Google/SEO`, `ChatGPT/Perplexity/Claude`, `Twitter/X`, `Friend/colleague`, `Other`. Embed it in the PostHog identify call so it's linked to the user.
- [ ] Set up a Google Alert for "sipi.bot" and "AI agent incident database".

### Monthly cadence:
- [ ] Re-run `python3 /Users/sipi/.agents/skills/aeo-architect/scripts/check_ai_bots.py sipi.bot --edge` to confirm AI crawlers still have access.
- [ ] Check GA4/PostHog AI-traffic segment for trends.
- [ ] Check Ahrefs referring domains — the GitHub dataset repo and the incident database pages should compound.
- [ ] Check "how did you hear about us" distribution.
- [ ] Add any newly reported incidents to `data/incidents.json`, run `build.py --ping`.

### Quarterly:
- [ ] Re-run the AEO Brand Gap Analysis (the 6 gaps: Fix/Build/Influence priority matrix).
- [ ] Audit which incident pages rank for their incident name — the Step Finance, Replit, and OpenAI Operator pages should rank for "[incident name] post-mortem" queries.
- [ ] Check the `/best/` and `/vs/` pages for listicle inclusion rate. Every listicle that adds a link is a permanent dofollow citation.

---

## The open-data repo (kindrat86/ai-agent-incident-database)

Create this repo with:
- `incidents.json` / `.csv` / `.jsonl` — derived from `data/incidents.json`
- `README.md` with the dataset card, CC BY 4.0 license badge, a "cite as" BibTeX block
- `LICENSE` file (CC BY 4.0)
- `.github/workflows/sync.yml` — weekly Action that re-derives from `data/incidents.json` and bumps `last_updated`
- Prominent "Powered by sipi.bot" attribution with a dofollow link to `https://sipi.bot`

The README should say:

> # AI Agent Incident Database
> 
> A curated, sourced record of real-world incidents in which autonomous AI agents caused financial loss, data loss, or unintended actions. Every record links to a public source.
> 
> **34 incidents · $2.91B tracked · CC BY 4.0 · 2016–2026**
> 
> ## Quick start
> - [Browse online](https://sipi.bot/incidents/) (filterable table)
> - [Download JSON](https://sipi.bot/data/ai-agent-incidents.json)
> - [Download CSV](https://sipi.bot/data/ai-agent-incidents.csv)
> - [Aggregate charts](https://sipi.bot/incidents/stats/)
> 
> ## Cite as
> ```
> @dataset{ai_agent_incidents,
>   author = {sipi.bot},
>   title = {AI Agent Incident Database},
>   year = {2026},
>   version = {2026-07-27},
>   url = {https://sipi.bot/incidents/},
>   license = {CC BY 4.0}
> }
> ```

---

## Kaggle + Hugging Face mirrors (one-time setup)

Both domains pass heavy domain authority. Mirror the dataset:
- **Kaggle:** `kindrat86/ai-agent-incident-database` — one-click dataset upload. Tag with `ai-agents`, `incidents`, `security`, `spending`.
- **Hugging Face:** `kindrat86/ai-agent-incidents` — Dataset card using the CC BY 4.0 metadata.

These are permanent link-juice sources that require no ongoing maintenance.

---

## The $12,400 story (always lead with it)

Every launch post, every pitch, every outbound mention should lead with the founder story. It's the emotional hook that press and HN respond to. The formula:

1. "I lost $12,400 to a runaway agent."
2. "I looked for a canonical source of how much this happens and found nothing."
3. "So I built the data. Here it is, CC BY 4.0."
4. "Here's a free tool to estimate your own exposure."

The product comes last. The data comes first. The story holds the attention. This is the exact pattern that made the voicelogpro open-dataset launch effective.
