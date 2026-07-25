# HERMES TASK — sipi.bot: "How to Control AI Agent Spending" Buyer's-Guide Decision Hub

> **Runbook for:** Hermes Agent running DeepSeek v4 Pro
> **Mode:** AUTONOMOUS — build, validate, commit, deploy without human intervention, subject to the fail-safes in §1.
> **Repo:** `~/projects/sipi-bot` (Python app `spendfirewall/`, serves sipi.bot on Fly.io app `sipi-bot-firewall`, region iad). Static pSEO served from disk by `spendfirewall/api.py` (`_serve_pseo`) under prefixes like `/learn/ /how-to/ /faq/ /integrations/`.
> **Deploy:** `flyctl deploy` (single command). NO edits to `spendfirewall/api.py`.
> **Author of runbook:** Claude (2026-07-21), grounded in a live audit.

---

## 0. What you are building and why

sipi.bot is **the spend firewall for autonomous AI agents** — before an agent pays, it calls `evaluate_spend` and gets APPROVED / BLOCKED / FLAGGED against your rules. The site is already mature (388 pages: `how-to/`, `faq/`, `learn/`, `alternatives-to/`, and a full `integrations/` cookbook for LangChain, OpenAI Agents SDK, CrewAI, AutoGen, Gemini, Vercel AI SDK, Anthropic, Stripe). Those levers are done.

The one distinct, high-value surface it's missing is the **top-of-funnel decision content**: the buyer at the start of the journey searches *"how do I limit AI agent spending,"* *"best way to stop an AI agent overspending,"* *"AI agent budget controls."* These are the **highest-commercial-intent** queries in an **emerging category sipi.bot is positioned to own** — and there's no definitive, honest, side-by-side guide answering them.

You will ship a **Buyer's-Guide Decision Hub**: a pillar page comparing every real approach to controlling agent spend (prompt limits, framework-native caps, virtual cards, a dedicated firewall), plus supporting spoke pages — each with comparison-table / HowTo / FAQ schema so it wins featured snippets and AI "best X" answers. This is the reliable 2026 lever for a category-defining product: **own the buyer's decision.**

**Why it's low-risk:** the comparison content is **provided, vetted, and approach-level** in §2 (you render it — you do not invent competitor claims), and the sipi.bot code is grounded in its **real** API.

---

## 1. 🚨 GUARDRAILS + FAIL-SAFES — READ FIRST

### 1a. NEVER fabricate.
- Use the comparison content in §2 **as written**. It compares **approaches/patterns** (not specific vendors' pricing or feature specs). Do NOT add invented statistics, benchmarks, competitor pricing, feature claims, testimonials, or "X% of agents overspend" numbers.
- The sipi.bot capabilities and code must match the **real API** (§3 — read `spendfirewall/mcp_server.py` + `spendfirewall/api.py` + the existing curl examples). Do not invent endpoints, parameters, or rule types.
- Keep the framing honest: sipi.bot is presented **fairly** (it wins on some dimensions, other approaches win on others). A one-sided "we win everything" table reads as marketing spam and won't earn citations. Honesty is the strategy.

### 1b. No api.py surgery.
- Do NOT edit `spendfirewall/api.py`. It already serves `/learn/<slug>/index.html` from disk (`_serve_pseo`). Put all new pages under `learn/` and they're served. Verify by reading `_serve_pseo` before relying on it.

### 1c. Fly deploy specifics.
- Deploy with `flyctl deploy` only. Do NOT run `flyctl secrets set`. Do NOT change `fly.toml`.
- `git config user.email` must be `sales@sipiteno.com` before deploy (Vercel/Fly team gating).

### 1d. Idempotency.
- Re-running regenerates cleanly (overwrite; no duplicate pages/sitemap entries).

---

## 2. Deliverable A — `agent-spend-approaches.json` (VETTED comparison — render as written)

Create this at repo root. **These characterizations are vetted and honest; render them, do not editorialize or add claims.**

```json
{
  "updated": "2026",
  "disclaimer": "This guide compares general approaches to controlling autonomous-agent spending as of 2026. Every team's needs differ; evaluate against your own stack and risk tolerance.",
  "dimensions": ["Enforced BEFORE the spend", "Controls real money (not just tokens/steps)", "Granular rules (merchant / category / velocity)", "Works across frameworks & agents", "Human-in-the-loop approvals", "Audit trail", "Setup effort"],
  "approaches": [
    {"name":"Prompt / instruction limits","slug":"prompt-limits","what":"Tell the agent its budget in the system prompt (\"don't spend over $100\").","pros":["Zero setup","Works with any model"],"cons":["Not enforced — the model can ignore, forget, or miscount","No hard stop before money moves","No audit trail"],"scores":{"before":"No","money":"No","rules":"No","cross":"Yes","human":"No","audit":"No","setup":"Trivial"}},
    {"name":"Framework-native caps","slug":"framework-native-caps","what":"Use a framework's built-in limits (max iterations, token/step caps, tool-call limits) in LangChain, the OpenAI Agents SDK, CrewAI, etc.","pros":["Built into the framework","Good for runaway loops"],"cons":["Caps tokens/steps, not real-money spend","Per-framework — no view across agents","No merchant/category/velocity rules"],"scores":{"before":"Partly","money":"No","rules":"No","cross":"No","human":"No","audit":"Partly","setup":"Low"}},
    {"name":"Virtual cards / provider caps","slug":"virtual-cards","what":"Issue a virtual card (or set a provider spend cap) with a hard limit per agent.","pros":["Hard money cap at the card","Provider-enforced"],"cons":["Coarse — usually one limit, no per-merchant/category/velocity logic","Blocks are after-the-fact at authorization, not policy-aware pre-checks","Issuance/reconciliation overhead"],"scores":{"before":"At auth","money":"Yes","rules":"Limited","cross":"Yes","human":"No","audit":"Partly","setup":"Medium"}},
    {"name":"Build your own policy service","slug":"build-your-own","what":"Write and host your own pre-spend policy engine.","pros":["Fully custom","No third-party dependency"],"cons":["You build & maintain rules, storage, audit, approvals","Slow to ship; easy to get edge cases wrong","Ongoing engineering cost"],"scores":{"before":"Yes","money":"Yes","rules":"Yes","cross":"Yes","human":"Depends","audit":"Depends","setup":"High"}},
    {"name":"Dedicated agent spend firewall (sipi.bot)","slug":"spend-firewall","what":"The agent calls a policy engine (evaluate_spend) BEFORE it pays; it returns APPROVED / BLOCKED / FLAGGED against your rules — velocity, merchant allow/block, category limits, approval thresholds — across every framework, with an audit trail and human approval for FLAGGED items.","pros":["Enforced before the spend, in real money","Granular rules (merchant/category/velocity/approval threshold)","One policy across all agents & frameworks (MCP / HTTP / CLI)","Human-in-the-loop for FLAGGED","Full audit trail"],"cons":["Adds a sub-second call in the payment path","You must define your rules"],"scores":{"before":"Yes","money":"Yes","rules":"Yes","cross":"Yes","human":"Yes","audit":"Yes","setup":"Low"}}
  ],
  "spokes": [
    {"slug":"how-to-stop-ai-agent-overspending","title":"How to stop an AI agent from overspending","angle":"The failure mode (an agent with a card and no hard limit) and the four things a real control needs: pre-spend enforcement, real-money limits, granular rules, and an audit trail."},
    {"slug":"do-you-need-a-spend-firewall-for-ai-agents","title":"Do you need a spend firewall for AI agents?","angle":"A decision checklist: if your agent can move money, calls external paid APIs/x402, or runs unattended, prompt limits and token caps are not enough."},
    {"slug":"ai-agent-budget-controls-best-practices","title":"AI agent budget controls: best practices","angle":"Set per-agent budgets, use velocity limits, allow/block by merchant, require human approval above a threshold, and keep an audit trail. Enforce before the spend, not after."}
  ]
}
```

---

## 3. Deliverable B — ground the sipi.bot code (read the real API)

Before generating, read the real surface so the pillar's "sipi.bot approach" shows correct, working code:
```bash
cd ~/projects/sipi-bot
grep -nA4 "def evaluate_spend" spendfirewall/mcp_server.py     # MCP tool signature
grep -rhoE "curl -X POST https://sipi.bot[^\`\"']*" . --include='*.md' --include='*.html' | head -1   # real HTTP example
sed -n '1,30p' spendfirewall/cli.py    # CLI example
```
Use the **verbatim** shapes you find. Known-good (verify against the above): MCP tool `evaluate_spend(amount, merchant, category, description)` → decision APPROVED/BLOCKED/FLAGGED; HTTP `POST https://sipi.bot/v1/transactions/evaluate`; CLI `python -m spendfirewall.cli eval --amount 750 --merchant unknown-gpu.ru --category compute`. If any differs from the code, use the code's version.

---

## 4. Deliverable C — `scripts/build_buyers_guide.py`

Renders the pillar + spoke pages under `learn/`, with comparison-table + HowTo + FAQ schema. Fill `SIPI_HTTP`, `SIPI_MCP`, `SIPI_CLI` from §3.

```python
#!/usr/bin/env python3
"""build_buyers_guide.py — render the AI-agent-spend buyer's-guide hub from
agent-spend-approaches.json into static pages under learn/. Renders vetted
content verbatim; no invented claims."""
import json, os, html
ROOT = os.getcwd(); BASE = "https://sipi.bot"
D = json.load(open(os.path.join(ROOT, "agent-spend-approaches.json"), encoding="utf-8"))
e = lambda s: html.escape(str(s))
DISC = D["disclaimer"]

# --- GROUNDED sipi.bot code (replace with the verified §3 values) ---
SIPI_HTTP = 'curl -X POST https://sipi.bot/v1/transactions/evaluate \\\n  -H "Authorization: Bearer $SIPI_KEY" -H "Content-Type: application/json" \\\n  -d \'{"amount": 750, "merchant": "unknown-gpu.ru", "category": "compute"}\'\n# -> {"decision": "BLOCKED", "reason": "..."}'
SIPI_MCP = '# In Claude Code / Cursor / Hermes: the agent calls the MCP tool\n# evaluate_spend(amount=750, merchant="unknown-gpu.ru", category="compute")\n# -> decision: APPROVED | BLOCKED | FLAGGED (respect BLOCKED/FLAGGED)'
SIPI_CLI = 'python -m spendfirewall.cli eval --amount 750 --merchant unknown-gpu.ru --category compute'

CSS = ("<style>body{font:16px/1.65 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:820px;"
       "margin:0 auto;padding:2rem 1rem;color:#0f172a;background:#fff}@media(prefers-color-scheme:dark)"
       "{body{background:#0b1120;color:#e2e8f0}}h1{font-size:2rem;line-height:1.12}a{color:#7c3aed;"
       "text-decoration:none}a:hover{text-decoration:underline}table{width:100%;border-collapse:collapse;"
       "margin:1.25rem 0;font-size:.9rem;display:block;overflow-x:auto}th,td{border:1px solid #e2e8f0;"
       "padding:.5rem .6rem;text-align:left;vertical-align:top}@media(prefers-color-scheme:dark){th,td"
       "{border-color:#1e293b}}th{background:#f8fafc}@media(prefers-color-scheme:dark){th{background:#111a2e}}"
       "pre{background:#0f172a;color:#e2e8f0;padding:1rem;border-radius:.5rem;overflow-x:auto;font-size:.85rem}"
       ".card{border:1px solid #e2e8f0;border-radius:.6rem;padding:1rem 1.25rem;margin:1rem 0}@media"
       "(prefers-color-scheme:dark){.card{border-color:#1e293b}}.disc{font-size:.85rem;color:#64748b;"
       "border-top:1px solid #e2e8f0;margin-top:2rem;padding-top:1rem}.cta{background:#7c3aed;color:#fff;"
       "border-radius:.7rem;padding:1.1rem 1.3rem;margin:1.5rem 0}.cta a{color:#fff;text-decoration:underline}</style>")

def shell(title, desc, canonical, jsonld, body):
    scripts = "".join(f'<script type="application/ld+json">{json.dumps(j,separators=(",",":"))}</script>' for j in jsonld)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
            f'<link rel="canonical" href="{canonical}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">'
            f'{CSS}{scripts}</head><body>{body}<p class="disc">{e(DISC)}</p></body></html>')

def write(slug, h):
    os.makedirs(os.path.join(ROOT,"learn",slug), exist_ok=True)
    open(os.path.join(ROOT,"learn",slug,"index.html"),"w",encoding="utf-8").write(h)

# ---- PILLAR ----
dims = D["dimensions"]; apps = D["approaches"]
# short dim keys align to scores dict order
keys = ["before","money","rules","cross","human","audit","setup"]
head = "<tr><th>Approach</th>" + "".join(f"<th>{e(d)}</th>" for d in dims) + "</tr>"
rows = ""
for a in apps:
    cells = "".join(f"<td>{e(a['scores'][k])}</td>" for k in keys)
    rows += f"<tr><td><strong>{e(a['name'])}</strong></td>{cells}</tr>"
cards = ""
for a in apps:
    cards += (f'<div class="card"><h3>{e(a["name"])}</h3><p>{e(a["what"])}</p>'
              f'<p><strong>Pros:</strong> {e("; ".join(a["pros"]))}</p>'
              f'<p><strong>Cons:</strong> {e("; ".join(a["cons"]))}</p></div>')
sipi_block = (f'<h2>The dedicated-firewall approach in code (sipi.bot)</h2>'
              f'<p>The agent asks before it pays. Three surfaces, one decision:</p>'
              f'<h3>HTTP</h3><pre>{e(SIPI_HTTP)}</pre>'
              f'<h3>MCP (Claude Code / Cursor / Hermes)</h3><pre>{e(SIPI_MCP)}</pre>'
              f'<h3>CLI</h3><pre>{e(SIPI_CLI)}</pre>')
faq_pillar = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
    {"@type":"Question","name":"What is the best way to control AI agent spending?","acceptedAnswer":{"@type":"Answer","text":"There are five main approaches — prompt limits, framework-native caps, virtual cards, building your own policy service, and a dedicated spend firewall. Prompt limits and token caps aren't enforced on real money; virtual cards give a hard but coarse cap; a dedicated firewall enforces granular rules before the spend across every framework, with human approval and an audit trail. "+DISC}},
    {"@type":"Question","name":"Do token/step limits stop an agent from overspending money?","acceptedAnswer":{"@type":"Answer","text":"No. Framework-native caps limit tokens or steps, not real-money spend, and don't apply merchant, category, or velocity rules. To control money you need a control in the payment path. "+DISC}}]}
howto = {"@context":"https://schema.org","@type":"HowTo","name":"How to control AI agent spending","step":[
    {"@type":"HowToStep","name":"Decide what to enforce","text":"Per-agent budget, per-merchant/category limits, velocity, and an approval threshold above which a human decides."},
    {"@type":"HowToStep","name":"Enforce before the spend","text":"Check each proposed transaction before money moves — not after — returning approve, block, or flag."},
    {"@type":"HowToStep","name":"Keep it cross-framework","text":"Apply one policy across all your agents and frameworks via HTTP, CLI, or MCP."},
    {"@type":"HowToStep","name":"Audit everything","text":"Log every decision so you can prove what was approved, blocked, or flagged."}]}
pillar_body = (f'<p style="font-size:.85rem"><a href="/">sipi.bot</a> › <a href="/learn">Learn</a> › How to control AI agent spending</p>'
    f'<h1>How to Control AI Agent Spending: 5 Approaches Compared ({e(D["updated"])})</h1>'
    f'<p>You gave an autonomous agent a way to pay — now how do you stop it spending on the wrong thing? '
    f'Here are the five real approaches, honestly compared on what actually matters.</p>'
    f'<table>{head}{rows}</table>'
    f'<p>No single approach is right for everyone: prompt limits are trivial but unenforced; framework caps stop runaway loops but not money; '
    f'virtual cards give a hard but blunt cap; a dedicated firewall gives enforced, granular, cross-framework control at the cost of one call in the path.</p>'
    f'{cards}{sipi_block}'
    f'<div class="cta"><strong>Put a firewall in front of every agent payment.</strong> sipi.bot approves, blocks, or flags each transaction against your rules — before a dollar moves. Free to start: <a href="/docs">read the docs →</a></div>')
write("how-to-control-ai-agent-spending", shell(
    f"How to Control AI Agent Spending: 5 Approaches Compared ({D['updated']}) | sipi.bot",
    "Prompt limits vs framework caps vs virtual cards vs build-your-own vs a dedicated spend firewall — an honest, side-by-side guide to controlling autonomous AI agent spending.",
    f"{BASE}/learn/how-to-control-ai-agent-spending", [faq_pillar, howto], pillar_body))

# ---- SPOKES ----
for s in D["spokes"]:
    canonical = f"{BASE}/learn/{s['slug']}"
    faq = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":s["title"]+"?","acceptedAnswer":{"@type":"Answer","text":s["angle"]+" "+DISC}}]}
    body = (f'<p style="font-size:.85rem"><a href="/">sipi.bot</a> › <a href="/learn">Learn</a> › {e(s["title"])}</p>'
        f'<h1>{e(s["title"])}</h1><p>{e(s["angle"])}</p>'
        f'<p>See the full comparison: <a href="/learn/how-to-control-ai-agent-spending">How to control AI agent spending — 5 approaches compared →</a></p>'
        f'<div class="cta"><strong>sipi.bot</strong> enforces your rules before every agent payment (APPROVED / BLOCKED / FLAGGED). <a href="/docs">Get started →</a></div>')
    write(s["slug"], shell(f"{s['title']} | sipi.bot", s["angle"][:150], canonical, [faq], body))

print("✓ buyer's-guide hub: pillar + %d spokes written under learn/" % len(D["spokes"]))
```

---

## 5. Deliverable D — sitemap + internal links
- Add the pillar + spoke URLs to the sitemap. Read how `spendfirewall/api.py` builds `/sitemap.xml` — if it auto-discovers `learn/*/index.html`, they appear automatically; if hardcoded, add a supplementary `sitemap-guide.xml` referenced by the sitemap index, or rely on internal links + IndexNow. **Do not edit api.py.**
- Add a link to the pillar from the most relevant existing pages (idempotent, skip if href present): `how-to/how-to-set-spend-limits/index.html`, `faq/how-to-set-ai-spend-limit/index.html`, `faq/how-to-prevent-runaway-ai-costs/index.html`, and the homepage. Anchor: `<a href="/learn/how-to-control-ai-agent-spending">How to control AI agent spending: 5 approaches compared →</a>`.

---

## 6. RUN + VALIDATE (before deploy)

```bash
cd ~/projects/sipi-bot
python3 scripts/build_buyers_guide.py

# a) pillar + spokes exist
ls learn/how-to-control-ai-agent-spending/index.html && ls learn/how-to-stop-ai-agent-overspending/index.html && echo "✓ pages"
# b) JSON-LD parses on the pillar
python3 -c "import re,json;h=open('learn/how-to-control-ai-agent-spending/index.html').read();[json.loads(m) for m in re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>',h,re.S)];print('✓ JSON-LD valid')"
# c) sipi.bot code in the pillar matches the real API (grounding check)
grep -q "v1/transactions/evaluate" learn/how-to-control-ai-agent-spending/index.html && echo "✓ real HTTP endpoint present"
grep -q "evaluate_spend" learn/how-to-control-ai-agent-spending/index.html && echo "✓ real MCP tool present"
# d) no fabricated stats/testimonials leaked
grep -inE "[0-9,]+% of (agents|teams|companies)|trusted by [0-9]|[0-9,]+ (developers|teams) (use|trust)" learn/how-to-control-ai-agent-spending/index.html && echo "FAIL: fabricated claim" || echo "✓ no fabricated claims"
# e) comparison is honest (sipi.bot is NOT 'Yes' on setup-effort etc. — table has trade-offs)
grep -c "Trivial\|Low\|Medium\|High\|No\|Partly" learn/how-to-control-ai-agent-spending/index.html   # expect several (real trade-offs shown)
```
If (c) fails, you didn't ground the code in §3 — fix `SIPI_HTTP/MCP/CLI` from the real files and re-run. If (d) fails, remove the claim.

---

## 7. DEPLOY (autonomous) — Fly.io

```bash
cd ~/projects/sipi-bot
git config user.email    # must be sales@sipiteno.com; if blank: git config user.email sales@sipiteno.com
git checkout -b buyers-guide-hub
git add agent-spend-approaches.json scripts/build_buyers_guide.py learn/ sitemap-guide.xml \
        how-to/how-to-set-spend-limits/index.html faq/how-to-set-ai-spend-limit/index.html \
        faq/how-to-prevent-runaway-ai-costs/index.html index.html 2>/dev/null
git commit -m "Add AI-agent-spend buyer's-guide decision hub (pillar + spokes)"

flyctl deploy    # no secrets; fly.toml unchanged

# --- Verify live ---
sleep 25
curl -s https://sipi.bot/learn/how-to-control-ai-agent-spending | grep -c "5 Approaches Compared"   # expect >=1
curl -sI https://sipi.bot/learn/how-to-stop-ai-agent-overspending | head -1                          # expect 200
curl -s https://sipi.bot/learn/how-to-control-ai-agent-spending | grep -c "v1/transactions/evaluate" # expect >=1
```
If `flyctl deploy` errors on auth/build, report and stop — do not force. Do NOT run `flyctl secrets set`.

---

## 8. POST-DEPLOY
1. **IndexNow:** the site has an IndexNow key (`89ce69c8...` .txt at root). Submit the new URLs to `https://api.indexnow.org/indexnow` (`host: sipi.bot`, that key + keyLocation, the pillar + spoke URLs). Bing → also ChatGPT Search/Copilot.
2. **Search Console + Bing:** request indexing on the pillar + spokes.
3. **Distribution (the multiplier):** the pillar is a genuinely useful, honest comparison — the content type that earns links. Share it where the question is asked (r/AI_Agents, r/LocalLLaMA, Hacker News, LangChain/CrewAI communities) and link it from the sipi.bot docs/README. Note for the owner.

---

## 9. Expected results (honest, mechanism-based — estimates, not guarantees)

| Effect | Mechanism | Realistic outcome | When |
|---|---|---|---|
| **Top-of-funnel commercial-intent traffic** | Pillar targets "how to / best way to control AI agent spending" — high-intent, low-competition, emerging category | New organic entries the how-to/integration pages don't capture; buyers arrive at the decision stage | 3–8 weeks |
| **Featured snippet / AI "best X" answers** | Comparison table + HowTo + FAQ schema; honest side-by-side | Wins the snippet / is quoted by AI assistants for "ways to control agent spend" | 1–3 months |
| **Backlinks** | Honest comparison guides are a top-linked content type; devs cite the table | Links that lift domain authority for an emerging-category site | 1–4 months (needs §8) |
| **Category ownership** | Being the definitive, fair guide as the category forms | sipi.bot becomes the default answer as search volume grows | compounding |

**Straight talk:**
- The guide's authority comes from being **honest** — the table shows sipi.bot losing on setup-simplicity to prompt limits and on blunt-hardness to virtual cards. That fairness is exactly what makes it citable (and what a marketing puff-piece never achieves). Do not "fix" the table to make sipi.bot win everything.
- This is decision-stage content; it converts better than generic traffic but its volume grows with the category. The compounding win is being early and definitive.
- Off-site sharing (§8) is the backlink multiplier. Measure: impressions on "control/limit AI agent spend" queries + referring domains to `/learn/how-to-control-ai-agent-spending`.

---

## 10. Rollback
Fully additive (json + generator + `learn/<slug>/` pages + optional sitemap + internal-link insertions). Roll back: `git revert`, `flyctl deploy`. No api.py changes to unwind.

### Definition of done
- [ ] `agent-spend-approaches.json` + `scripts/build_buyers_guide.py` created; pillar + 3 spokes rendered under `learn/`.
- [ ] sipi.bot code in the pillar grounded in the REAL API (§6c passes); comparison content rendered as vetted (honest trade-offs intact, §6e).
- [ ] JSON-LD valid; no fabricated stats/testimonials (§6d).
- [ ] Sitemap + internal links handled without editing api.py; committed to a branch; deployed via `flyctl deploy` (no secrets, fly.toml unchanged); live checks pass.
- [ ] IndexNow submitted (§8). Zero fabricated claims; sipi.bot presented fairly, not as winning every dimension.
```
