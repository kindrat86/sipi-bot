#!/usr/bin/env python3
"""build_buyers_guide.py — render the AI-agent-spend buyer's-guide hub from
agent-spend-approaches.json into static pages under learn/. Renders vetted
content verbatim; no invented claims."""
import json, os, html
ROOT = os.getcwd(); BASE = "https://sipi.bot"
D = json.load(open(os.path.join(ROOT, "agent-spend-approaches.json"), encoding="utf-8"))
e = lambda s: html.escape(str(s))
DISC = D["disclaimer"]

# --- GROUNDED sipi.bot code (verified from real API in §3) ---
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
    f'<p style="padding:10px 16px;background:#f0f4ff;border-left:3px solid #7c3aed;border-radius:0 8px 8px 0;margin:0 0 1.5rem 0;font-size:.95rem;color:#374151"><strong>TL;DR:</strong> Five approaches to controlling autonomous AI agent spending — from prompt limits (free but unenforced) to dedicated spend firewalls (enforced, granular, cross-framework). The right choice depends on your risk: if an agent holds a real payment method, prompt limits and framework caps aren&apos;t enough.</p>'
    f'<p>You gave an autonomous agent a way to pay — now how do you stop it spending on the wrong thing? '
    f'Here are the five real approaches, honestly compared on what actually matters.</p>'
    f'<table>{head}{rows}</table>'
    f'<p>No single approach is right for everyone: prompt limits are trivial but unenforced; framework caps stop runaway loops but not money; '
    f'virtual cards give a hard but blunt cap; a dedicated firewall gives enforced, granular, cross-framework control at the cost of one call in the path.</p>'
    f'{cards}{sipi_block}'
    f'<div style="margin:1.5rem 0;padding:1rem 1.25rem;background:#f0f4ff;border-left:3px solid #7c3aed;border-radius:0 .5rem .5rem 0">'
    f'<strong>Definition:</strong> A <dfn>pre-spend firewall</dfn> is a control layer that approves, blocks, or flags each AI-agent transaction before money moves, using per-transaction caps, velocity limits, and merchant rules. It returns a deterministic decision in under 5ms.'
    f'</div>'
    f'<p>See also: <a href="/answers/">AI spending answers hub</a> &mdash; quick answers to common agent-spend questions.</p>'
    f'<div class="cta"><strong>Put a firewall in front of every agent payment.</strong> sipi.bot approves, blocks, or flags each transaction against your rules — before a dollar moves. Free to start: <a href="/docs">read the docs →</a></div>')
import json as _json
defined_term = _json.loads("""{"@context":"https://schema.org","@type":"DefinedTerm","@id":"https://sipi.bot/#pre-spend-firewall","name":"Pre-spend firewall","termCode":"pre-spend-firewall","description":"A control layer that approves, blocks, or flags each AI-agent transaction before money moves, using per-transaction caps, velocity limits, and merchant rules. It returns a deterministic decision in under 5ms.","inDefinedTermSet":{"@type":"DefinedTermSet","name":"AI Agent Spend Control Terminology","url":"https://sipi.bot/learn/how-to-control-ai-agent-spending"}}""")
write("how-to-control-ai-agent-spending", shell(
    f"How to Control AI Agent Spending: 5 Approaches Compared ({D['updated']}) | sipi.bot",
    "Prompt limits vs framework caps vs virtual cards vs build-your-own vs a dedicated spend firewall — an honest, side-by-side guide to controlling autonomous AI agent spending.",
    f"{BASE}/learn/how-to-control-ai-agent-spending", [faq_pillar, howto, defined_term], pillar_body))

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
