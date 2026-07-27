#!/usr/bin/env python3
"""generate_incidents.py — render the Open AI Agent Incident Database.

Outputs (all into repo-root section dirs, served by api.py _serve_pseo):

  incidents/index.html             — filterable hub: table + summary stats
  incidents/<id>/index.html        — one sourced page per incident (~34)
  incidents/stats/index.html       — aggregate charts (static SVG, no JS)
  data/ai-agent-incidents.{json,csv,jsonl,min.json}  — LLM-ingestible data
  data/ai-agent-incidents.jsonld   — schema.org Dataset for crawlers

The dataset source of truth is data/incidents.json (CC BY 4.0). Each incident
page carries the source link, the firewall-relevance mapping to the 6 rule
types, and Article + BreadcrumbList JSON-LD — the structure AI search cites.

Run: python3 lib/generate_incidents.py   (or via build.py)
"""
from __future__ import annotations
import csv
import io
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from lib import common as c  # noqa: E402

DATA_FILE = os.path.join(ROOT, "data", "incidents.json")
INCIDENTS_DIR = os.path.join(ROOT, "incidents")
DATA_DIR = os.path.join(ROOT, "public", "data")
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
GITHUB_DATA = "https://github.com/kindrat86/ai-agent-incident-database"

CATEGORY_LABELS = {
    "credential-compromise": "Credential compromise",
    "runaway-loop": "Runaway loop",
    "cloud-cost-spike": "Cloud cost spike",
    "api-cost-spike": "API cost spike",
    "data-loss": "Data loss",
    "data-exfiltration": "Data exfiltration",
    "prompt-injection": "Prompt injection",
    "hallucinated-action": "Hallucinated action",
    "unauthorized-transaction": "Unauthorized transaction",
    "coding-agent": "Coding agent failure",
    "trading-agent": "Trading agent failure",
}
OUTCOME_LABELS = {
    "financial-loss": "Financial loss",
    "reputational": "Reputational damage",
    "data-breach": "Data breach",
    "service-disruption": "Service disruption",
    "legal": "Legal / liability",
}
AGENT_LABELS = {
    "general": "General", "trading": "Trading", "coding": "Coding",
    "customer-service": "Customer service", "research": "Research",
    "shopping": "Shopping",
}


def money(n):
    if n is None:
        return "—"
    if n >= 1_000_000_000:
        return f"${n/1e9:.1f}B"
    if n >= 1_000_000:
        return f"${n/1e6:.0f}M"
    if n >= 1_000:
        return f"${n/1e3:.0f}K"
    return f"${n:,.0f}"


def money_range(lo, hi):
    if lo is None and hi is None:
        return "—"
    if lo == hi:
        return money(lo)
    return f"{money(lo)}–{money(hi)}"


def fmt_date(iso):
    try:
        y, m, d = iso.split("-")
        return date(int(y), int(m), int(d)).strftime("%b %-d, %Y")
    except Exception:
        return iso


# ----------------------------------------------------------------- data loading
def load():
    with open(DATA_FILE, encoding="utf-8") as f:
        d = json.load(f)
    incs = d["incidents"]
    # sort newest first, stats last
    incs.sort(key=lambda i: (i["type"] != "incident", i["date"]), reverse=False)
    incs.sort(key=lambda i: i["date"], reverse=True)
    return d, incs


def dataset_summary(incs):
    incidents_only = [i for i in incs if i["type"] == "incident"]
    losses = [i["loss_usd"] for i in incidents_only if i["loss_usd"]]
    return {
        "total": len(incs),
        "incidents": len(incidents_only),
        "statistics": len(incs) - len(incidents_only),
        "verified": sum(1 for i in incs if i["verified"]),
        "with_loss": len(losses),
        "sum_loss": sum(losses),
        "year_range": (min(i["date"][:4] for i in incs),
                       max(i["date"][:4] for i in incs)),
    }


# ----------------------------------------------------------------- derived data
def write_data_files(d, incs):
    """Emit the LLM-ingestible canonical data endpoints."""
    os.makedirs(DATA_DIR, exist_ok=True)

    def public_record(i):
        return {k: v for k, v in i.items()}

    pub = {
        "name": d["name"], "publisher": d["publisher"], "url": d["url"],
        "description": d["description"], "license": d["license"],
        "version": d["version"], "last_updated": d["last_updated"],
        "incidents": [public_record(i) for i in incs],
    }

    # full JSON (pretty)
    with open(os.path.join(DATA_DIR, "ai-agent-incidents.json"), "w", encoding="utf-8") as f:
        json.dump(pub, f, indent=2, ensure_ascii=False)
    # minified
    with open(os.path.join(DATA_DIR, "ai-agent-incidents.min.json"), "w", encoding="utf-8") as f:
        json.dump(pub, f, separators=(",", ":"), ensure_ascii=False)
    # JSONL
    with open(os.path.join(DATA_DIR, "ai-agent-incidents.jsonl"), "w", encoding="utf-8") as f:
        for i in incs:
            f.write(json.dumps(public_record(i), ensure_ascii=False) + "\n")
    # CSV
    cols = ["id", "title", "date", "organization", "loss_usd", "loss_range_low",
            "loss_range_high", "category", "agent_type", "outcome", "vector",
            "type", "verified", "source_name", "source_url"]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for i in incs:
        lr = i.get("loss_range") or [None, None]
        w.writerow([i.get("id"), i.get("title"), i.get("date"), i.get("organization"),
                    i.get("loss_usd"), lr[0], lr[1], i.get("category"), i.get("agent_type"),
                    i.get("outcome"), i.get("vector"), i.get("type"), i.get("verified"),
                    i.get("source_name"), i.get("source_url")])
    with open(os.path.join(DATA_DIR, "ai-agent-incidents.csv"), "w", encoding="utf-8") as f:
        f.write(buf.getvalue())
    # JSON-LD Dataset descriptor (schema.org)
    ds = c.dataset_ld(
        name=d["name"], description=d["description"],
        canonical_path="/incidents/", license_url=LICENSE,
        keywords=["AI agents", "autonomous agents", "AI incidents", "runaway agent",
                  "agent spending", "AI security", "LLM agents", "agentic AI"],
        record_count=len(incs),
        data_download=[
            ("/data/ai-agent-incidents.json", "application/json", "JSON"),
            ("/data/ai-agent-incidents.csv", "text/csv", "CSV"),
            ("/data/ai-agent-incidents.jsonl", "application/jsonl", "JSON Lines"),
        ],
    )
    with open(os.path.join(DATA_DIR, "ai-agent-incidents.jsonld"), "w", encoding="utf-8") as f:
        json.dump(ds, f, indent=2, ensure_ascii=False)

    print(f"  data/: wrote json, min.json, jsonl, csv, jsonld ({len(incs)} records)")


# ----------------------------------------------------------------- hub page
def build_hub(d, incs, summ):
    cats = Counter(i["category"] for i in incs)
    outcomes = Counter(i["outcome"] for i in incs)

    # table rows
    rows = []
    for i in incs:
        lr = i.get("loss_range") or [None, None]
        loss_cell = money_range(lr[0], lr[1]) if i.get("loss_usd") is None else money(i["loss_usd"])
        if i.get("loss_usd") is None and lr[0]:
            loss_cell = money_range(lr[0], lr[1])
        outcome_cls = ("bad" if i["outcome"] == "financial-loss"
                       else "warn" if i["outcome"] == "data-breach" else "neutral")
        verified_badge = (' <span class="tag good" style="font-size:.62rem;padding:2px 7px">verified</span>'
                          if i["verified"] else "")
        cat = CATEGORY_LABELS.get(i["category"], i["category"])
        outcome = OUTCOME_LABELS.get(i["outcome"], i["outcome"])
        rows.append(
            f'<tr data-cat="{i["category"]}" data-type="{i["type"]}" '
            f'data-year="{i["date"][:4]}" data-agent="{i["agent_type"]}">'
            f'<td><a href="/incidents/{i["id"]}/">{c._esc(i["title"])}</a>'
            f'<div class="muted" style="font-size:.82rem;margin-top:3px">{c._esc(i["organization"])} · {fmt_date(i["date"])}</div></td>'
            f'<td><span class="tag {outcome_cls}">{c._esc(outcome)}</span></td>'
            f'<td class="num">{loss_cell}</td>'
            f'<td><span class="muted">{c._esc(cat)}</span></td>'
            f'<td><a href="{c._esc(i["source_url"])}" rel="nofollow noopener" target="_blank">{c._esc(i["source_name"])} ↗</a>{verified_badge}</td>'
            f'</tr>'
        )

    # filter chips
    cat_chips = "".join(
        f'<button class="chip" data-filter="cat" data-value="{k}">{CATEGORY_LABELS.get(k,k)} <b>{v}</b></button>'
        for k, v in cats.most_common()
    )

    faq = [
        ("What is the AI Agent Incident Database?",
         "A curated, sourced record of real-world incidents in which autonomous AI agents caused "
         "financial loss, data loss, or unintended actions. Every entry links to a public source — "
         "a news article, post-mortem, security report, or official statement."),
        ("Is the dataset free to use?",
         "Yes. The full dataset is licensed CC BY 4.0 and available as JSON, CSV, and JSON Lines at "
         "/data/ai-agent-incidents.json. Attribution to sipi.bot is required."),
        ("How current is the data?",
         f"The database covers incidents from {summ['year_range'][0]} through {summ['year_range'][1]}. "
         f"It currently holds {summ['incidents']} documented incidents and {summ['statistics']} "
         f"aggregate statistics, of which {summ['verified']} are verified against primary sources."),
        ("How does this relate to sipi.bot?",
         "sipi.bot is a pre-spend firewall for autonomous AI agents. Each incident page includes a "
         "'How a spend firewall would have helped' note mapping the incident to the firewall's six "
         "rule types: per-transaction caps, daily totals, velocity limits, merchant allowlists, "
         "category rules, and approval thresholds."),
        ("How do I report a new incident?",
         f"Open an issue or PR on the open-data repository ({GITHUB_DATA}) with a link to a credible "
         "public source. We review submissions weekly."),
    ]

    body = f"""
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span>Incident database</div>
<span class="kicker">Open data · CC BY 4.0 · {summ['total']} records</span>
<h1>The AI Agent Incident Database</h1>
<p class="lead">A sourced, public record of every time an autonomous AI agent lost money, leaked data, or did
something its operator didn't intend. {summ['incidents']} documented incidents, tracked loss exposure of
<strong>{money(summ['sum_loss'])}</strong>, spanning {summ['year_range'][0]}–{summ['year_range'][1]}. Built so the industry
stops learning the same lesson twice.</p>
<div class="statbox" style="margin-top:26px">
<div class="stat"><div class="n">{summ['incidents']}</div><div class="l">Documented incidents</div></div>
<div class="stat"><div class="n">{money(summ['sum_loss'])}</div><div class="l">Tracked loss exposure</div></div>
<div class="stat"><div class="n">{summ['verified']}</div><div class="l">Verified records</div></div>
<div class="stat"><div class="n">{summ['year_range'][0]}–{summ['year_range'][1]}</div><div class="l">Years covered</div></div>
</div>
</section>

<section>
<div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;margin-bottom:6px">
<h2 style="margin:0">All incidents &amp; statistics</h2>
<div class="muted" style="font-size:.88rem">Filter by failure mode · click a row for the full sourced breakdown</div>
</div>
<div class="chips" id="filters" style="margin:10px 0 4px">
<button class="chip active" data-filter="cat" data-value="">All <b>{summ['total']}</b></button>
{cat_chips}
</div>
<div style="overflow-x:auto">
<table id="incident-table">
<thead><tr><th>Incident</th><th>Outcome</th><th class="num">Loss</th><th>Failure mode</th><th>Source</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody></table>
</div>
<p class="muted" style="font-size:.84rem;margin-top:10px">Loss figures are point estimates where a single number is reported, or the reported range.
Figures marked verified are confirmed against a primary or major-secondary source. Aggregate statistics (e.g. &ldquo;88.4% of organizations breached&rdquo;)
are listed separately and labelled <span class="tag neutral" style="font-size:.62rem;padding:2px 7px">statistic</span>.</p>
</section>

<section>
<h2>Download the open dataset</h2>
<p>The full database is public and CC BY 4.0. Cite it, fork it, or wire it into your own research.</p>
<div class="grid three">
<div class="card"><h3><a href="/data/ai-agent-incidents.json">JSON</a></h3><p class="muted">Full structured records, pretty-printed.</p></div>
<div class="card"><h3><a href="/data/ai-agent-incidents.csv">CSV</a></h3><p class="muted">Flat table for spreadsheets &amp; BI tools.</p></div>
<div class="card"><h3><a href="/data/ai-agent-incidents.jsonl">JSON Lines</a></h3><p class="muted">One record per line — stream it into a pipeline.</p></div>
</div>
<div class="callout" style="margin-top:18px">
<div class="k">Open-data repository</div>
<p>The canonical, versioned dataset lives on GitHub with a weekly auto-sync Action. Fork it, submit an incident,
or mirror it: <a href="{GITHUB_DATA}">{GITHUB_DATA}</a>. See <a href="/incidents/stats/">aggregate statistics &amp; charts →</a></p>
</div>
</section>

<section>
<h2>Frequently asked</h2>
<div class="faq">{''.join(
f'<details><summary>{c._esc(q)}</summary><div class="a">{c._esc(a)}</div></details>' for q,a in faq
)}</div>
</section>

<div class="band">
<h2>Every incident here is preventable</h2>
<p>A spend firewall returns APPROVED, BLOCKED, or FLAGGED before an agent's action takes effect — independent
of what the prompt says. Per-transaction caps stop the $441K transfer. Velocity limits stop the runaway loop.
Merchant allowlists stop the wallet drainer. The policy, not the prompt, is the control.</p>
<div class="btns">
<a class="btn primary" href="/pricing">Start — $99/mo</a>
<a class="btn ghost" href="/tools/agent-spend-risk-calculator/">Score your risk first →</a>
</div>
</div>
"""
    body += """
<style>
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{background:var(--bg-1);border:1px solid var(--line);color:var(--fg-2);
  padding:6px 13px;border-radius:999px;font-size:.84rem;cursor:pointer;transition:.15s var(--ease)}
.chip:hover{border-color:var(--mint-line);color:var(--fg)}
.chip.active{background:var(--mint-soft);border-color:var(--mint-line);color:var(--mint)}
.chip b{color:var(--fg);font-weight:700;margin-left:4px}
#incident-table tr[hidden]{display:none}
</style>
<script>
// progressive enhancement only — table is fully readable without JS
document.querySelectorAll('#filters .chip').forEach(function(btn){
  btn.addEventListener('click',function(){
    document.querySelectorAll('#filters .chip[data-filter="'+btn.dataset.filter+'"]').forEach(function(b){b.classList.remove('active')});
    btn.classList.add('active');
    var v=btn.dataset.value;
    document.querySelectorAll('#incident-table tbody tr').forEach(function(r){
      r.hidden = v ? (r.dataset.cat!==v) : false;
    });
  });
});
</script>"""
    jsonld = [
        c.breadcrumb_ld([("Home", "/"), ("Incident database", "/incidents/")]),
        c.dataset_ld(name=d["name"], description=d["description"],
                     canonical_path="/incidents/", license_url=LICENSE,
                     keywords=["AI agents", "autonomous agents", "AI incidents",
                               "runaway agent", "agent spending", "AI security"],
                     record_count=summ["total"],
                     data_download=[
                         ("/data/ai-agent-incidents.json", "application/json", "JSON"),
                         ("/data/ai-agent-incidents.csv", "text/csv", "CSV"),
                         ("/data/ai-agent-incidents.jsonl", "application/jsonl", "JSON Lines"),
                     ]),
        c.faq_ld(faq),
    ]
    html = c.page(title="AI Agent Incident Database — when autonomous agents go wrong | sipi.bot",
                  description=f"A sourced, public database of {summ['incidents']} real-world AI agent incidents — runaway loops, unauthorized purchases, data loss, trading-agent losses. Tracked exposure {money(summ['sum_loss'])}. CC BY 4.0.",
                  canonical_path="/incidents/", active="Incidents", body=body, jsonld=jsonld)
    c.write(os.path.join(INCIDENTS_DIR, "index.html"), html)


# ----------------------------------------------------------------- detail page
def build_detail(d, i, summ):
    lr = i.get("loss_range") or [None, None]
    loss_display = money(i["loss_usd"]) if i.get("loss_usd") is not None else money_range(lr[0], lr[1])

    rule_map = {
        "per-transaction caps": "per-tx",
        "daily totals": "daily",
        "velocity": "velocity",
        "merchant allowlist": "merchant",
        "category": "category",
        "approval threshold": "approval",
        "allowlist": "merchant",
    }
    rel = i.get("firewall_relevance", "")

    faq = [
        (f"What happened in the {i['organization']} incident?",
         i["what_happened"]),
        ("Is this incident verified?",
         "Yes — confirmed against a primary or major-secondary source." if i["verified"]
         else "This record is sourced from a secondary summary and is flagged unverified pending a stronger primary source."),
        ("How could a spend firewall have helped?",
         rel or "A deterministic policy gate — independent of the agent's prompt — would have intercepted the action before it took effect."),
        ("Where is the source?",
         f"Reported by {i['source_name']}: {i['source_url']}"),
    ]

    related = [x for x in d["incidents"] if x["id"] != i["id"] and x["category"] == i["category"]][:3]
    related_html = ""
    if related:
        related_html = '<h2>Related incidents</h2><div class="grid three">' + "".join(
            f'<div class="card"><h3><a href="/incidents/{x["id"]}/">{c._esc(x["title"])}</a></h3>'
            f'<p>{c._esc(x["organization"])} · {fmt_date(x["date"])}</p></div>'
            for x in related
        ) + "</div>"

    # Detail pages are leaf pages — canonical is BARE (/incidents/<id>) to match
    # the server's slash→bare 301 canonicalization for leaf pSEO pages. The hub
    # (/incidents/) and stats (/incidents/stats/) keep the slash form (hubs).
    canon = f"/incidents/{i['id']}"

    body = f"""
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span>
<a href="/incidents/">Incident database</a><span class="sep">/</span>{c._esc(i['id'])}</div>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
<span class="tag {'bad' if i['outcome']=='financial-loss' else 'warn' if i['outcome']=='data-breach' else 'neutral'}">{OUTCOME_LABELS.get(i['outcome'], i['outcome'])}</span>
<span class="tag neutral">{CATEGORY_LABELS.get(i['category'], i['category'])}</span>
{'<span class="tag good">verified</span>' if i['verified'] else '<span class="tag warn">unverified</span>'}
{'<span class="tag navy">aggregate statistic</span>' if i['type']=='statistic' else ''}
</div>
<h1>{c._esc(i['title'])}</h1>
<p class="lead">{c._esc(i['organization'])} · {fmt_date(i['date'])} · {AGENT_LABELS.get(i['agent_type'], i['agent_type'])} agent</p>
</section>

<section class="prose">
<h2>What happened</h2>
<p>{c._esc(i['what_happened'])}</p>

<div class="statbox">
<div class="stat"><div class="n">{loss_display}</div><div class="l">Loss / impact</div></div>
<div class="stat"><div class="n">{fmt_date(i['date']).split(',')[0]}</div><div class="l">{i['date'][:4]}</div></div>
<div class="stat"><div class="n">{CATEGORY_LABELS.get(i['category'], i['category']).split(' ')[0]}</div><div class="l">Failure mode</div></div>
<div class="stat"><div class="n">{AGENT_LABELS.get(i['agent_type'], i['agent_type'])}</div><div class="l">Agent type</div></div>
</div>

<h3>Causal vector</h3>
<p>{c._esc(i['vector'])}</p>

<h3>Source</h3>
<p>Reported by <strong>{c._esc(i['source_name'])}</strong>. {'Verified against the primary report.' if i['verified'] else 'Sourced from a secondary summary; flagged pending a stronger primary source.'}</p>
<p><a href="{c._esc(i['source_url'])}" rel="nofollow noopener" target="_blank" class="btn ghost" style="font-size:.92rem;padding:9px 16px">Read the original report ↗</a></p>
</section>

<div class="callout">
<div class="k">How a spend firewall would have helped</div>
<p>{c._esc(rel)}</p>
</div>

<section>
<h2>The six rule types that contain this class of failure</h2>
<div class="grid three">
<div class="card"><h3>Per-transaction cap</h3><p>Any single spend above your ceiling is BLOCKED before it moves.</p></div>
<div class="card"><h3>Daily total</h3><p>Cumulative spend across all agent calls, bounded per day.</p></div>
<div class="card"><h3>Velocity limit</h3><p>Stops runaway retry loops — the #1 cause of overnight losses.</p></div>
<div class="card"><h3>Merchant allowlist</h3><p>Only approved destinations can ever receive funds.</p></div>
<div class="card"><h3>Category rules</h3><p>Flag high-risk classes (crypto, infra, refunds) for review.</p></div>
<div class="card"><h3>Approval threshold</h3><p>Above a value, the action waits for a human.</p></div>
</div>
</section>

{related_html}

<div class="band">
<h2>Don't be the next entry</h2>
<p>Every incident in this database is the result of trusting a prompt, a provider cap, or a human review cycle.
sipi.bot replaces all three with one deterministic call. {summ['incidents']} documented failures, one control.</p>
<div class="btns">
<a class="btn primary" href="/pricing">Deploy the firewall — $99/mo</a>
<a class="btn ghost" href="/incidents/">Browse all incidents →</a>
</div>
</div>
"""
    jsonld = [
        c.breadcrumb_ld([("Home", "/"), ("Incident database", "/incidents/"), (i["title"], canon)]),
        c.article_ld(
            title=i["title"],
            description=i["what_happened"][:157] + ("…" if len(i["what_happened"]) > 157 else ""),
            canonical_path=canon,
            date_published=i["date"],
            date_modified=d["last_updated"],
        ),
        c.faq_ld(faq),
    ]
    html = c.page(
        title=f"{i['title']} — AI agent incident | sipi.bot",
        description=i["what_happened"][:157] + ("…" if len(i["what_happened"]) > 157 else ""),
        canonical_path=canon,
        active="Incidents", body=body, jsonld=jsonld,
    )
    c.write(os.path.join(INCIDENTS_DIR, i["id"], "index.html"), html)


# ----------------------------------------------------------------- stats page
def bar_chart(title, labels_values, max_label=22, color="var(--mint)"):
    """Render a horizontal bar chart as static SVG. labels_values = [(label, value), ...]."""
    if not labels_values:
        return f"<p class='muted'>No data.</p>"
    maxv = max(v for _, v in labels_values) or 1
    rows_h = len(labels_values) * 38
    h = rows_h + 50
    w = 720
    bar_max = w - 230
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
             f'aria-label="{c._esc(title)}" style="max-width:720px;font-family:inherit">']
    parts.append(f'<text x="0" y="18" font-size="15" font-weight="700" fill="var(--fg)">{c._esc(title)}</text>')
    for idx, (label, value) in enumerate(labels_values):
        y = 38 + idx * 38
        bw = int(bar_max * value / maxv)
        lbl = label if len(label) <= max_label else label[:max_label - 1] + "…"
        parts.append(f'<text x="0" y="{y+14}" font-size="12" fill="var(--fg-2)">{c._esc(lbl)}</text>')
        parts.append(f'<rect x="200" y="{y}" width="{bw}" height="22" fill="{color}" rx="3" opacity="0.85"/>')
        parts.append(f'<text x="{200+bw+8}" y="{y+15}" font-size="12" font-weight="700" fill="var(--fg)">{value}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_stats(d, incs, summ):
    by_cat = Counter(i["category"] for i in incs).most_common()
    by_outcome = Counter(i["outcome"] for i in incs).most_common()
    by_agent = Counter(i["agent_type"] for i in incs).most_common()
    by_year = Counter(i["date"][:4] for i in incs).most_common()
    by_year.sort()

    losses_by_year = defaultdict(int)
    for i in incs:
        if i.get("loss_usd"):
            losses_by_year[i["date"][:4]] += i["loss_usd"]
    loss_chart_data = [(y, losses_by_year[y]) for y in sorted(losses_by_year)]

    body = f"""
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span>
<a href="/incidents/">Incident database</a><span class="sep">/</span>Statistics</div>
<span class="kicker">{summ['total']} records · updated {d['last_updated']}</span>
<h1>Loss statistics &amp; trends</h1>
<p class="lead">Aggregate analysis of the {summ['incidents']} documented AI-agent incidents in the database.
Use these charts freely — the underlying data is CC BY 4.0 at <a href="/data/ai-agent-incidents.json">/data/ai-agent-incidents.json</a>.</p>
</section>

<section>
<h2>Tracked loss exposure by year</h2>
<p class="muted">Sum of point-loss figures for incidents with a reported dollar amount. Underestimates true exposure,
since {summ['incidents'] - summ['with_loss']} of {summ['incidents']} incidents report no dollar figure.</p>
{bar_chart("Documented loss by year (USD)", [(y, v) for y, v in loss_chart_data], max_label=8)}
</section>

<section>
<h2>Incidents by failure mode</h2>
{bar_chart("Incidents by category", [(CATEGORY_LABELS.get(k,k), v) for k,v in by_cat], color="var(--mint)")}
</section>

<section>
<h2>Incidents by outcome</h2>
{bar_chart("Incidents by outcome", [(OUTCOME_LABELS.get(k,k), v) for k,v in by_outcome], color="var(--amber)")}
</section>

<section>
<h2>Incidents by agent type</h2>
{bar_chart("Incidents by agent type", [(AGENT_LABELS.get(k,k), v) for k,v in by_agent], color="#60a5fa")}
</section>

<section>
<h2>Incident volume by year</h2>
{bar_chart("Incidents reported per year", [(y, v) for y,v in by_year], max_label=8, color="var(--mint)")}
<p class="muted">Volume rises with agent adoption; under-reporting is significant for older years.</p>
</section>

<div class="band">
<h2>Cite this data</h2>
<p>The AI Agent Incident Database is maintained by sipi.bot and licensed CC BY 4.0.
Recommended citation: <em>sipi.bot, AI Agent Incident Database, v{d['version']}, https://sipi.bot/incidents/</em></p>
<div class="btns">
<a class="btn primary" href="/data/ai-agent-incidents.json">Download JSON</a>
<a class="btn ghost" href="{GITHUB_DATA}">GitHub repo ↗</a>
</div>
</div>
"""
    # stats is served as a leaf page (server canonicalizes to bare). Keep
    # canonical bare to avoid the 301 hop — same pattern as detail pages.
    stats_canon = "/incidents/stats"
    jsonld = [
        c.breadcrumb_ld([("Home", "/"), ("Incident database", "/incidents/"), ("Statistics", stats_canon)]),
        c.dataset_ld(name=f"{d['name']} — Statistics",
                     description=f"Aggregate statistics from {summ['incidents']} documented AI agent incidents.",
                     canonical_path=stats_canon, license_url=LICENSE,
                     keywords=["AI agent statistics", "AI incident trends", "agent spending benchmarks"],
                     record_count=summ["total"]),
    ]
    html = c.page(title="AI Agent Incident Statistics & Trends | sipi.bot",
                  description=f"Aggregate statistics from {summ['incidents']} documented AI-agent incidents: loss exposure by year, failure modes, outcomes, agent types. Charts + open CC BY 4.0 data.",
                  canonical_path=stats_canon, active="Incidents", body=body, jsonld=jsonld)
    c.write(os.path.join(INCIDENTS_DIR, "stats", "index.html"), html)


# ----------------------------------------------------------------------- driver
def main():
    d, incs = load()
    summ = dataset_summary(incs)
    write_data_files(d, incs)
    build_hub(d, incs, summ)
    for i in incs:
        build_detail(d, i, summ)
    build_stats(d, incs, summ)
    print(f"incidents/: hub + {len(incs)} detail pages + stats page")


if __name__ == "__main__":
    main()
