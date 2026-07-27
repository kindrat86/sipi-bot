#!/usr/bin/env python3
"""W2 — Generate real hub index pages for orphan sections.

Seven sections (/alternatives/, /compare/, /cost-of/, /limits/, /policies/,
/templates/, /tutorials/) had children in the sitemap but no parent index
page — so ~38 child pages were orphans with no internal-link path from the
homepage or any hub. Google treats a section root that 404s while its
children 200 as a weak cluster.

This writes a proper hub index.html for each: title + meta + intro + linked
child list + ItemList/BreadcrumbList JSON-LD + canonical. The hub itself is
then added to the sitemap by rebuild_sitemap.py and linked from the
site-wide Resources footer (already injected in api.py).

Re-runnable: overwrites existing hub index.html only when content changes.
"""
from __future__ import annotations
import os, re, json, html as _html

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SITE = "https://sipi.bot"

# Hub metadata: (title, meta description, intro paragraph, hub-h2 heading)
HUB_META = {
    "alternatives": (
        "sipi.bot alternatives & comparisons for AI agent guardrails",
        "Honest alternatives to sipi.bot across AI agent guardrail and policy engines — Aporia, Guardrails AI, NVIDIA NeMo, OPA, Prompt Security, x402. What each does, where sipi.bot wins.",
        "These pages compare sipi.bot to the other guardrail, policy, and payment-control tools teams consider before deploying autonomous agents. Each alternative page is honest about what the other tool does well and where a dedicated pre-spend firewall is the better fit.",
        "Alternatives & comparisons",
    ),
    "compare": (
        "sipi.bot vs build-vs-buy approaches for agent spend control",
        "Compare sipi.bot against AWS Budgets, Cedar/OPA, custom middleware, human-approval workflows, manual auditing, and OpenAI Moderation — for governing AI agent spend.",
        "Before adding a spend firewall, teams weigh it against the alternatives they could build or already use: cloud budgets, policy engines, custom middleware, manual review. These comparison pages lay out the trade-offs honestly so you can pick the right layer for your stack.",
        "Build-vs-buy comparisons",
    ),
    "cost-of": (
        "AI API & LLM tool pricing — what does it cost? [2026]",
        "Current 2026 pricing for the AI APIs and LLM tooling your agents call — Anthropic Claude, OpenAI, LangSmith — so you can size spend limits and budgets accurately.",
        "You can't set a sane spend limit without knowing what the underlying APIs cost. These pages pin down current per-token and per-seat pricing for the providers and tools agents most commonly spend against, with worked examples for sizing per-transaction caps and daily ceilings.",
        "What does it cost? (2026 pricing)",
    ),
    "limits": (
        "Recommended spend limits for AI agents — by provider & use case",
        "Reference spend limits for OpenAI and Anthropic agents, plus recommended caps by use case — per-transaction, daily, and velocity — to stop runaway spend.",
        "Setting agent spend limits is mostly about matching the cap to the provider's pricing and the use case's risk profile. These pages give concrete starting-point limits for OpenAI and Anthropic agents and a use-case matrix so you don't start from a blank page.",
        "Spend limit references",
    ),
    "policies": (
        "Agent spend policy patterns — daily ceiling, allowlist, per-tx, velocity",
        "Reusable spend-policy patterns for AI agents: daily ceiling, merchant allowlist, per-transaction limit, and velocity cap — each with the rule shape and when to use it.",
        "These policy pages describe the four rule patterns that cover almost every agent-spend scenario. Each one shows the rule shape, the failure mode it prevents, and how to combine it with the others into a complete spend firewall.",
        "Spend policy patterns",
    ),
    "templates": (
        "Free AI agent spend & governance templates [2026]",
        "Free, copy-paste templates for governing AI agent spend: spend policy, purchase authorization, runbook, cost allocation, incident response, approval workflow, and more.",
        "These are free, copy-paste templates for the documents every team deploying autonomous agents eventually needs — a spend policy, a purchase-authorization policy, a runbook, a cost-allocation sheet, an incident-response plan, and the operational templates around them. Adapt the fields; the structure is battle-tested.",
        "Free governance templates",
    ),
    "tutorials": (
        "sipi.bot tutorials — configure limits, allowlists, alerts, integrations",
        "Step-by-step tutorials for sipi.bot: configure a merchant allowlist, set per-agent limits, set up alerts, debug a blocked transaction, and integrate with Claude Code.",
        "Short, practical walkthroughs for the day-to-day work of running a spend firewall — configuring allowlists, setting per-agent limits, wiring up alerts, debugging a block, and integrating with the agent runtimes you already use.",
        "Step-by-step tutorials",
    ),
}


def child_pages(hub: str) -> list[dict]:
    """List {slug, url, title, desc} for every child page of a hub."""
    out = []
    for base in (os.path.join(ROOT, hub), os.path.join(ROOT, "public", hub)):
        if not os.path.isdir(base):
            continue
        for child in sorted(os.listdir(base)):
            idx = os.path.join(base, child, "index.html")
            if not os.path.isfile(idx):
                continue
            with open(idx, encoding="utf-8", errors="replace") as f:
                c = f.read()
            tm = re.search(r"<title>([^<]+)</title>", c)
            dm = re.search(r'<meta name="description" content="([^"]+)"', c)
            title = tm.group(1).strip() if tm else child.replace("-", " ").title()
            desc = dm.group(1).strip() if dm else ""
            url = f"{SITE}/{hub}/{child}/"
            # de-dupe by url (repo-root and public/ can both hold the same child)
            if not any(u["url"] == url for u in out):
                out.append({"slug": child, "url": url, "title": title, "desc": desc})
    return out


def build_hub_html(hub: str) -> str:
    title, desc, intro, h2 = HUB_META[hub]
    children = child_pages(hub)
    canonical = f"{SITE}/{hub}/"
    # ItemList JSON-LD
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": title,
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": ch["url"], "name": ch["title"]}
            for i, ch in enumerate(children)
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": hub.title(), "item": canonical},
        ],
    }
    web_page = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": desc,
        "url": canonical,
        "isPartOf": {"@id": f"{SITE}/#website"},
    }
    # Child list HTML
    items_html = "\n".join(
        f'      <li><a href="{ch["url"]}">{_html.escape(ch["title"])}</a>'
        + (f'<p>{_html.escape(ch["desc"])}</p>' if ch["desc"] else "")
        + "</li>"
        for ch in children
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_html.escape(title)}</title>
<meta name="description" content="{_html.escape(desc, quote=True)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{_html.escape(title, quote=True)}">
<meta property="og:description" content="{_html.escape(desc, quote=True)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<script type="application/ld+json">{json.dumps(item_list)}</script>
<script type="application/ld+json">{json.dumps(breadcrumb)}</script>
<script type="application/ld+json">{json.dumps(web_page)}</script>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.65;color:#0a0a0a;max-width:820px;margin:0 auto;padding:2rem 1.25rem}}
h1{{font-size:2.1rem;line-height:1.2;margin:.3em 0 0}}
.lede{{font-size:1.1rem;color:#374151;margin:1rem 0 1.5rem}}
h2{{font-size:1.3rem;margin-top:2rem;border-bottom:2px solid #e5e7eb;padding-bottom:.3rem}}
ul.hub{{list-style:none;padding:0;margin:1rem 0}}
ul.hub li{{padding:.8rem 0;border-bottom:1px solid #f3f4f6}}
ul.hub li a{{color:#0066cc;text-decoration:none;font-weight:600;font-size:1.05rem}}
ul.hub li a:hover{{text-decoration:underline}}
ul.hub li p{{margin:.25rem 0 0;color:#6b7280;font-size:.95rem}}
.back{{display:inline-block;margin-top:2rem;color:#0066cc;text-decoration:none}}
</style>
</head>
<body>
<h1>{_html.escape(title)}</h1>
<p class="lede">{_html.escape(intro)}</p>
<h2>{_html.escape(h2)}</h2>
<ul class="hub">
{items_html}
</ul>
<a class="back" href="{SITE}/">← Back to sipi.bot</a>
</body>
</html>
"""


def main():
    written = []
    for hub in HUB_META:
        # prefer repo-root (matches _serve_pseo prefix list); fall back to public/
        target_dir = os.path.join(ROOT, hub)
        if not os.path.isdir(target_dir):
            target_dir = os.path.join(ROOT, "public", hub)
            os.makedirs(target_dir, exist_ok=True)
        out = os.path.join(target_dir, "index.html")
        html_doc = build_hub_html(hub)
        existing = open(out, encoding="utf-8").read() if os.path.isfile(out) else ""
        if existing == html_doc:
            continue
        with open(out, "w", encoding="utf-8") as f:
            f.write(html_doc)
        n = len(child_pages(hub))
        written.append((hub, n, out))
    for hub, n, out in written:
        rel = os.path.relpath(out, ROOT)
        print(f"  wrote {rel} ({n} children)")
    if not written:
        print("  no changes — all hubs up to date")
    print(f"\n{len(written)} hub(s) written.")


if __name__ == "__main__":
    main()
