"""Round 20 pSEO generator — sipi.bot (2026-08-08).

New page types/pages (Greg Isenberg gap-fill for the 309-URL site):
  sectors/   (NEW type, 8 pages + hub)   — industry vertical intent
  integrations/ (+8 pages + hub)         — ecosystem SEO (MCP, Claude Code, Cursor, ...)
  vs/        (+8 pages)                  — comparison capture (Cursor, AgentKit, ...)
  cost-of/   (+6 pages + hub rebuild)    — "how much does X cost" commercial intent
  benchmarks/ (+3 pages)                 — link-bait / data pages
  best/      (+3 pages)                  — "best X" transactional lists

All leaves are repo-root pSEO dirs with BARE canonical (matches _serve_pseo's
slash→bare 301). Hubs are slash-canonical. Chrome via lib/common.py.
"""
from __future__ import annotations
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import common  # noqa: E402
from generate_pseo_round20_data import (  # noqa: E402
    SECTORS, INTEGRATIONS, VS, COST_OF, BENCHMARKS, BEST, SECTORS_HUB,
)

# ------------------------------------------------------------------- helpers
def esc(s):
    return common._esc(s)


def crumbs(*pairs):
    """pairs: (label, href). Last pair is current page (no link)."""
    items = ['<span class="crumbs"><a href="/">Home</a> <span class="sep">/</span>']
    for i, (label, href) in enumerate(pairs):
        if i == len(pairs) - 1:
            items.append(f" {esc(label)}")
        else:
            items.append(f' <a href="{href}">{esc(label)}</a> <span class="sep">/</span>')
    items.append("</span>")
    return "".join(items)


def hero(h1, lead, crumb_pairs):
    return f"{crumbs(*crumb_pairs)}\n<h1>{esc(h1)}</h1>\n<p class=\"lead\">{esc(lead)}</p>"


def section(h2, paras):
    ps = "".join(f"<p>{esc(p)}</p>" for p in paras)
    return f"<h2>{esc(h2)}</h2>\n{ps}"


def table_block(headers, rows, caption=None):
    thead = "".join(f"<th>{esc(h)}</th>" for h in headers)
    trs = "".join(
        "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in rows
    )
    cap = f"<p class=\"tbl-cap\">{esc(caption)}</p>" if caption else ""
    return (
        f"{cap}<div class=\"tbl-wrap\"><table class=\"cmp\"><thead><tr>{thead}</tr></thead>"
        f"<tbody>{trs}</tbody></table></div>"
    )


def code_block(title, lang, body, caption):
    return (
        f"<h3>{esc(title)}</h3>\n"
        f"<pre><code class=\"lang-{esc(lang)}\">{esc(body)}</code></pre>\n"
        f"<p class=\"code-cap\">{esc(caption)}</p>"
    )


def faq_block(faqs):
    qas = []
    for q, a in faqs:
        qas.append(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>")
    return f"<h2>FAQ</h2>\n" + "\n".join(qas)


def related_block(links):
    lis = "".join(f"<li><a href=\"{href}\">{esc(label)}</a></li>" for label, href in links)
    return f"<h2>Related</h2>\n<ul class=\"related\">{lis}</ul>"


def cta():
    return (
        '<div class="cta-card"><h3>Stop the next $12,400 night.</h3>'
        "<p>One API call (or MCP tool) in front of every agent transaction — "
        "APPROVED, BLOCKED, or FLAGGED, deterministic, ~5 ms, fully logged.</p>"
        '<a class="btn primary" href="/pricing">See plans — from $99/mo</a> '
        '<a class="btn ghost" href="/playground/">Try a live check</a></div>'
    )


def faq_ld_pairs(faqs):
    return [{"question": q, "answer": a} for q, a in faqs]


def write_leaf(prefix, slug, title, description, body, faqs, related):
    """Write dir/slug/index.html with BARE canonical (repo-root pSEO convention)."""
    path = os.path.join(ROOT, prefix, slug)
    os.makedirs(path, exist_ok=True)
    canonical = f"/{prefix}/{slug}"
    jsonld = [
        common.breadcrumb_ld([
            {"name": "Home", "url": common.SITE + "/"},
            {"name": prefix, "url": common.SITE + f"/{prefix}/"},
            {"name": slug, "url": common.SITE + canonical},
        ]),
        common.faq_ld(faq_ld_pairs(faqs)),
    ]
    html = common.page(
        title=title, description=description, canonical_path=canonical,
        active=None, body=body, jsonld=jsonld,
    )
    common.write(os.path.join(path, "index.html"), html)
    return canonical


def write_hub(prefix, title, description, h1, lead, cards, intro=None):
    """Write prefix/index.html with slash canonical (hub convention)."""
    cards_html = []
    for label, href, blurb in cards:
        cards_html.append(
            f'<div class="card"><h3><a href="{href}">{esc(label)}</a></h3>'
            f"<p>{esc(blurb)}</p></div>"
        )
    intro_html = f'<p class="lead">{esc(lead)}</p>'
    if intro:
        intro_html += f"<div class=\"hub-intro\">{intro}</div>"
    body = (
        f"{crumbs(('Home', '/'), (h1, None))}\n<h1>{esc(h1)}</h1>\n{intro_html}\n"
        f'<div class="grid two">{"".join(cards_html)}</div>\n{cta()}'
    )
    jsonld = [common.breadcrumb_ld([
        {"name": "Home", "url": common.SITE + "/"},
        {"name": h1, "url": common.SITE + f"/{prefix}/"},
    ])]
    html = common.page(
        title=title, description=description, canonical_path=f"/{prefix}/",
        active=None, body=body, jsonld=jsonld,
    )
    common.write(os.path.join(ROOT, prefix, "index.html"), html)
    return f"/{prefix}/"


def build_leaf_body(meta):
    """Generic leaf body from the data dict: hero + sections + table + code + faq + related + cta."""
    parts = [hero(meta["h1"], meta["lead"], meta["crumb"])]
    for h2, paras in meta["sections"]:
        parts.append(section(h2, paras))
    if meta.get("table"):
        parts.append(f"<h2>{esc(meta['table_h2'])}</h2>")
        parts.append(table_block(meta["table"]["headers"], meta["table"]["rows"]))
    if meta.get("code"):
        parts.append(code_block(meta["code"]["title"], meta["code"]["lang"],
                                meta["code"]["body"], meta["code"]["caption"]))
    parts.append(faq_block(meta["faqs"]))
    parts.append(related_block(meta["related"]))
    parts.append(cta())
    return "\n".join(parts)


# ------------------------------------------------------------------- builders
def build_sectors():
    count = 0
    for s in SECTORS:
        meta = dict(s)
        meta["crumb"] = (("Home", "/"), ("Sectors", "/sectors/"), (s["h1"], None))
        meta["table_h2"] = "The rules that matter most"
        body = build_leaf_body(meta)
        write_leaf("sectors", s["slug"], s["title"], s["desc"], body, s["faqs"], s["related"])
        count += 1
    cards = [(s["h1"], f"/sectors/{s['slug']}", s["lead"]) for s in SECTORS]
    write_hub("sectors", SECTORS_HUB["title"], SECTORS_HUB["desc"],
              SECTORS_HUB["h1"], SECTORS_HUB["lead"], cards)
    print(f"sectors/: hub + {count} pages")
    return count + 1


def build_integrations():
    count = 0
    for i in INTEGRATIONS:
        meta = dict(i)
        meta["crumb"] = (("Home", "/"), ("Integrations", "/integrations/"), (i["h1"], None))
        meta["table_h2"] = "Rules that fit this workload"
        # integrations pages are code-first: put code block after first section
        body = build_leaf_body(meta)
        write_leaf("integrations", i["slug"], i["title"], i["desc"], body, i["faqs"], i["related"])
        count += 1
    # Fresh hub (integrations/ had no index.html)
    cards = [(i["h1"], f"/integrations/{i['slug']}", i["lead"]) for i in INTEGRATIONS]
    write_hub(
        "integrations",
        "sipi.bot Integrations — MCP, Claude Code, Cursor & More",
        "Spend control integrations for the frameworks agents are built on: MCP, Claude Code, Cursor, LangGraph, n8n, Pydantic AI, SmolAgents, LlamaIndex.",
        "sipi.bot Integrations",
        "sipi.bot plugs into whatever your agents run on — as an MCP tool, an HTTP API, or a CLI. Add the guard before the spend.",
        cards,
    )
    print(f"integrations/: hub + {count} pages")
    return count + 1


def build_vs():
    count = 0
    for v in VS:
        meta = dict(v)
        meta["crumb"] = (("Home", "/"), ("Comparisons", "/vs/"), (v["h1"], None))
        meta["table_h2"] = "Side by side"
        body = build_leaf_body(meta)
        write_leaf("vs", v["slug"], v["title"], v["desc"], body, v["faqs"], v["related"])
        count += 1
    # Patch the existing hub with new cards (keep its custom chrome).
    hub_path = os.path.join(ROOT, "vs", "index.html")
    with open(hub_path, encoding="utf-8") as f:
        hub = f.read()
    if "vs/cursor" not in hub:
        cards = "".join(
            f'<div class="card"><h3><a href="/vs/{v["slug"]}">sipi.bot vs {esc(v["name"])}</a></h3>'
            f"<p>{esc(v['lead'])}</p></div>"
            for v in VS
        )
        block = f'<h2>More comparisons</h2>\n<div class="grid2">\n{cards}\n</div>\n'
        # insert before the guide/home links line
        marker = '<div style="margin-top:2rem">'
        if marker in hub:
            hub = hub.replace(marker, block + marker)
        else:
            hub = hub.replace("</body>", block + "</body>")
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(hub)
    print(f"vs/: {count} pages + hub patched")
    return count


def build_costof():
    count = 0
    for c in COST_OF:
        meta = dict(c)
        meta["crumb"] = (("Home", "/"), ("Cost of AI", "/cost-of/"), (c["h1"], None))
        meta["table_h2"] = "Where the money goes"
        body = build_leaf_body(meta)
        write_leaf("cost-of", c["slug"], c["title"], c["desc"], body, c["faqs"], c["related"])
        count += 1
    # Rebuild the hub (it existed but with no links — now lists everything).
    existing = []
    if os.path.isdir(os.path.join(ROOT, "cost-of")):
        for d in sorted(os.listdir(os.path.join(ROOT, "cost-of"))):
            if os.path.isdir(os.path.join(ROOT, "cost-of", d)) and d != "index":
                existing.append(d)
    all_slugs = [c["slug"] for c in COST_OF]
    for slug in existing:
        if slug not in all_slugs:
            all_slugs.append(slug)
    cards = []
    known = {c["slug"]: c for c in COST_OF}
    for slug in all_slugs:
        if slug in known:
            cards.append((known[slug]["h1"], f"/cost-of/{slug}", known[slug]["lead"]))
        else:
            cards.append((slug.replace("-", " ").title(), f"/cost-of/{slug}", "Pricing breakdown."))
    write_hub(
        "cost-of",
        "How Much Does AI Cost? — Pricing Breakdowns | sipi.bot",
        "Honest pricing breakdowns: Claude Code, GitHub Copilot, Cursor, AWS Bedrock, DeepSeek, Gemini, OpenAI, Anthropic — and how to control each.",
        "How Much Does AI Cost?",
        "Pricing pages show the rate. These guides show the whole cost — plans, hidden usage, and what autonomous agents add to the bill.",
        cards,
    )
    print(f"cost-of/: hub rebuilt + {count} pages")
    return count + 1


def build_benchmarks():
    count = 0
    for b in BENCHMARKS:
        meta = dict(b)
        meta["crumb"] = (("Home", "/"), ("Benchmarks", "/benchmarks/"), (b["h1"], None))
        meta["table_h2"] = "The data at a glance"
        body = build_leaf_body(meta)
        write_leaf("benchmarks", b["slug"], b["title"], b["desc"], body, b["faqs"], b["related"])
        count += 1
    # Patch hub
    hub_path = os.path.join(ROOT, "benchmarks", "index.html")
    if os.path.exists(hub_path):
        with open(hub_path, encoding="utf-8") as f:
            hub = f.read()
        cards = "".join(
            f'<div class="card"><h3><a href="/benchmarks/{b["slug"]}">{esc(b["h1"])}</a></h3>'
            f"<p>{esc(b['lead'])}</p></div>"
            for b in BENCHMARKS
        )
        block = f'<h2>2026 data</h2>\n<div class="grid2">\n{cards}\n</div>\n'
        marker = '<div style="margin-top:2rem">'
        if marker in hub:
            hub = hub.replace(marker, block + marker)
        else:
            hub = hub.replace("</body>", block + "</body>")
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(hub)
    print(f"benchmarks/: {count} pages + hub patched")
    return count


def build_best():
    count = 0
    for b in BEST:
        meta = dict(b)
        meta["crumb"] = (("Home", "/"), ("Best-of", "/best/"), (b["h1"], None))
        meta["table_h2"] = "At a glance"
        body = build_leaf_body(meta)
        write_leaf("best", b["slug"], b["title"], b["desc"], body, b["faqs"], b["related"])
        count += 1
    hub_path = os.path.join(ROOT, "best", "index.html")
    if os.path.exists(hub_path):
        with open(hub_path, encoding="utf-8") as f:
            hub = f.read()
        cards = "".join(
            f'<div class="card"><h3><a href="/best/{b["slug"]}">{esc(b["h1"])}</a></h3>'
            f"<p>{esc(b['lead'])}</p></div>"
            for b in BEST
        )
        block = f'<h2>New in 2026</h2>\n{cards}\n'
        marker = '<div style="margin-top:2rem">'
        if marker in hub:
            hub = hub.replace(marker, block + marker)
        else:
            hub = hub.replace("</body>", block + "</body>")
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(hub)
    print(f"best/: {count} pages + hub patched")
    return count


def main():
    total = 0
    total += build_sectors()
    total += build_integrations()
    total += build_vs()
    total += build_costof()
    total += build_benchmarks()
    total += build_best()
    print(f"\n✓ Round 20 complete — {total} new files (leaves + hubs)")


if __name__ == "__main__":
    main()
