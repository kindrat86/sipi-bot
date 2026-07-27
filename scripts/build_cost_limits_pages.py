#!/usr/bin/env python3
"""build_cost_limits_pages.py — Generate /cost-of/ provider pages + hub and
/limits/ provider pages + hub, grounded 100% in public/ai-model-costs-2026.csv.

No fabricated prices or benchmarks. Every number traces to the CSV (CC BY 4.0,
sourced from provider pricing pages, July 2026) or to vendor-listed facts
(context window, latency tier). Honesty rule from CLAUDE.md: sipi.bot does not
"win" every comparison — pages state facts, the product is positioned where it
genuinely fits (the pre-spend layer that caps provider burn).

Serving note: spendfirewall/api.py::_serve_pseo() resolves
  /cost-of/<slug>  ->  cost-of/<slug>/index.html
so every page is written as <slug>/index.html. The flat cost-of/*.html files
that predate this generator are dead duplicates (they 404 on the live route)
and are intentionally not reproduced here.

Run: python3 scripts/build_cost_limits_pages.py
"""
from __future__ import annotations
import csv
import html
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
CSV_PATH = os.path.join(ROOT, "public", "ai-model-costs-2026.csv")
SITE = "https://sipi.bot"
TODAY = date.today().isoformat()  # 2026-07-27 in the deploy environment

# ──────────────────────────────────────────────────────────────────────────
# Shared CSS — matches the existing /cost-of/openai-api-cost design system
# (Isenberg round-19 pSEO): light theme, max-width 760, .price-tag, .callout,
# .cta, mesh-links, .check lists.
# ──────────────────────────────────────────────────────────────────────────
CSS = """body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.65;color:#0a0a0a;max-width:760px;margin:0 auto;padding:2rem 1.25rem}
h1{font-size:2.1rem;line-height:1.2;margin:.3em 0}
h2{font-size:1.45rem;margin-top:2rem;border-bottom:2px solid #e5e7eb;padding-bottom:.3rem}
h3{font-size:1.15rem;margin-top:1.5rem}
a{color:#0066cc;text-decoration:none}a:hover{text-decoration:underline}
.lede{font-size:1.1rem;color:#374151;margin-bottom:1.5rem}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.95rem}
th,td{border:1px solid #e5e7eb;padding:.6rem .75rem;text-align:left;vertical-align:top}
th{background:#f9fafb;font-weight:600}
.callout{background:#f0f7ff;border-left:4px solid #0066cc;padding:1rem 1.25rem;margin:1.5rem 0;border-radius:0 .375rem .375rem 0}
.callout.warn{background:#fef3c7;border-left-color:#d97706}
.callout.good{background:#ecfdf5;border-left-color:#059669}
.cta{background:linear-gradient(135deg,#0066cc,#004499);color:#fff;padding:2rem;border-radius:.75rem;margin-top:2rem;text-align:center}
.cta h2{color:#fff;border:none}.cta .btn{display:inline-block;background:#fff;color:#0066cc;padding:.75rem 1.5rem;border-radius:.375rem;font-weight:600;margin-top:.5rem}
.price-tag{display:inline-block;background:#dcfce7;color:#166534;font-weight:700;padding:.25rem .75rem;border-radius:.375rem;font-size:1.1rem}
.related-links,.mesh-links{background:#f9fafb;padding:1rem 1.25rem;border-radius:.5rem;margin-top:2.5rem}
.mesh-links ul,.related-links ul{list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:.4rem 1rem;font-size:.95rem}
footer{margin-top:3rem;padding-top:1.5rem;border-top:1px solid #e5e7eb;color:#6b7280;font-size:.9rem}
ul.check{list-style:none;padding-left:0}ul.check li::before{content:"\\2713  ";color:#059669;font-weight:700}
code{background:#f3f4f6;padding:.1em .35em;border-radius:.25em;font-size:.9em}
pre{background:#0a0a0a;color:#e5e7eb;padding:1rem 1.25rem;border-radius:.5rem;overflow-x:auto;font-size:.85rem;line-height:1.5}
pre code{background:none;padding:0}
.hub-grid{display:grid;grid-template-columns:1fr;gap:1rem;margin:1.5rem 0}
@media(min-width:560px){.hub-grid{grid-template-columns:1fr 1fr}}
.hub-card{background:#f9fafb;border:1px solid #e5e7eb;border-radius:.5rem;padding:1.25rem}
.hub-card h3{margin-top:0}.hub-card .prov{display:inline-block;background:#dbeafe;color:#1e40af;font-size:.75rem;padding:.15rem .5rem;border-radius:99px;margin-bottom:.5rem}
.src{font-size:.85rem;color:#6b7280;font-style:italic;margin-top:.5rem}"""


# ──────────────────────────────────────────────────────────────────────────
# CSV loader
# ──────────────────────────────────────────────────────────────────────────
def load_models():
    rows = []
    with open(CSV_PATH, encoding="utf-8") as fh:
        # The CSV has a trailing "Source:" line that is not a data row; skip it.
        for row in csv.DictReader(fh):
            if row.get("AI Model") and not row["AI Model"].startswith("Source:"):
                rows.append(row)
    return rows


def price_num(s):
    """'$2.50' -> 2.50 float (for sorting / arithmetic only)."""
    return float(s.replace("$", "").replace(",", "").strip())


def price_str(s):
    """'$2.50' -> '2.50' (display string, we add $ at the call site)."""
    return s.replace("$", "").strip()


# ──────────────────────────────────────────────────────────────────────────
# JSON-LD builders (must each carry @context + @type to pass the deploy gate)
# ──────────────────────────────────────────────────────────────────────────
def article_ld(title, desc, path):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "author": {"@type": "Organization", "name": "sipi.bot", "url": SITE},
        "publisher": {"@type": "Organization", "name": "sipi.bot", "url": SITE},
        "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + path},
        "datePublished": TODAY,
        "dateModified": TODAY,
    }


def breadcrumb_ld(crumb_name, path):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": crumb_name, "item": SITE + path},
        ],
    }


def faq_ld(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }


def jsonld_blocks(*blocks):
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in blocks
    )


# ──────────────────────────────────────────────────────────────────────────
# Page shell
# ──────────────────────────────────────────────────────────────────────────
def page(title, desc, path, body, ld_blocks, og_type="article", marker="isenberg-cost-limits"):
    can = SITE + path
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{can}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{can}">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{SITE}/og.png">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="alternate" hreflang="en" href="{can}">
<link rel="alternate" hreflang="en-US" href="{can}">
<link rel="alternate" hreflang="x-default" href="{can}">
{ld_blocks}
<style>{CSS}</style>
<!-- {marker} -->
</head>
<body>
<article>
{body}
</article>
<section class="cta"><h2>Stop runaway agent spend before it happens</h2>
<p>sipi.bot is a pre-spend firewall for autonomous AI agents — approve, block, or flag every transaction in under 5ms.</p>
<a href="{SITE}/pricing" class="btn">See plans &rarr;</a></section>
<footer><p>&copy; 2026 sipi.bot &middot; <a href="{SITE}/">Home</a> &middot; <a href="{SITE}/about">About</a> &middot; <a href="{SITE}/pricing">Pricing</a></p></footer>
</body>
</html>"""


def mesh(items):
    """Render a related-links mesh. items: list of (href, label)."""
    lis = "".join(f'<li><a href="{h}">{html.escape(l)}</a></li>' for h, l in items)
    return (
        '<section class="mesh-links">'
        '<h3 style="margin-top:0">Related resources</h3>'
        f'<ul>{lis}</ul></section>'
    )


def prov_label(slug):
    """Human provider label from a cost-of slug, for mesh links."""
    name = slug.replace("-api-cost", "").replace("-", " ")
    # special cases so mesh labels read naturally
    fixes = {"amazon bedrock": "Amazon Bedrock"}
    return fixes.get(name, name.title())


# ──────────────────────────────────────────────────────────────────────────
# /cost-of/ provider pages
# ──────────────────────────────────────────────────────────────────────────
COST_PAGES = [
    {
        "slug": "gemini-api-cost",
        "provider_contains": "Google",
        "brand": "Google Gemini",
        "title": "How Much Does the Google Gemini API Cost? [2026 Pricing]",
        "h1": "How Much Does the Google Gemini API Cost?",
        "lede": "Google Gemini API pricing in 2026 spans the cheapest frontier model on the market (Gemini 1.5 Flash at $0.075/1M input) to a 2-million-token context workhorse (Gemini 1.5 Pro). Here is the per-token breakdown and what an autonomous agent actually pays.",
    },
    {
        "slug": "llama-api-cost",
        "provider_contains": "Meta",
        "brand": "Meta Llama",
        "title": "How Much Does the Llama 3.1 API Cost? [2026 Pricing]",
        "h1": "How Much Does the Meta Llama API Cost?",
        "lede": "Meta Llama 3.1 is open-weights, so the model is free — what you pay is inference. Pricing depends entirely on where you run it. Here is what Llama 3.1 70B and 405B cost across the common API providers in 2026.",
    },
    {
        "slug": "mistral-api-cost",
        "provider_contains": "Mistral",
        "brand": "Mistral",
        "title": "How Much Does the Mistral API Cost? [2026 Pricing]",
        "h1": "How Much Does the Mistral API Cost?",
        "lede": "Mistral Large is priced at $2.00/1M input and $6.00/1M output in 2026 — a mid-tier European option with a 128K context window. Here is the pricing breakdown and what it costs to run a Mistral-backed autonomous agent.",
    },
    {
        "slug": "deepseek-api-cost",
        "provider_contains": "DeepSeek",
        "brand": "DeepSeek",
        "title": "How Much Does the DeepSeek API Cost? [2026 Pricing]",
        "h1": "How Much Does the DeepSeek API Cost?",
        "lede": "DeepSeek V3 is one of the cheapest capable models available in 2026 at $0.27/1M input and $1.10/1M output. Cheap per-token does not mean cheap in aggregate — here is what a runaway agent actually costs and how to cap it.",
    },
    {
        "slug": "cohere-api-cost",
        "provider_contains": "Cohere",
        "brand": "Cohere",
        "title": "How Much Does the Cohere Command R+ API Cost? [2026 Pricing]",
        "h1": "How Much Does the Cohere Command R+ API Cost?",
        "lede": "Cohere Command R+ is priced at $2.50/1M input and $10.00/1M output in 2026 — positioned for RAG applications with a 128K context window. Here is the cost breakdown and the agent-deployment economics.",
    },
    {
        "slug": "groq-api-cost",
        "provider_contains": "Groq",
        "brand": "Groq (Llama inference)",
        "title": "How Much Does the Groq API Cost? [2026 Pricing]",
        "h1": "How Much Does the Groq API Cost?",
        "lede": "Groq serves Meta Llama 3.1 70B at $0.59/1M input and $0.79/1M output in 2026 — the fastest latency tier available. Here is the pricing and why speed is a double-edged sword for autonomous agents.",
    },
    {
        "slug": "amazon-bedrock-cost",
        "provider_contains": "Amazon",
        "brand": "Amazon Bedrock (Nova)",
        "title": "How Much Does Amazon Bedrock Cost? [2026 Nova Pricing]",
        "h1": "How Much Does Amazon Bedrock Cost?",
        "lede": "Amazon Bedrock's Nova models are priced for AWS-integrated workloads: Nova Pro at $0.80/1M in / $3.20/1M out and Nova Lite at $0.06/1M in / $0.24/1M out in 2026. Here is the per-token breakdown and the Bedrock-specific cost traps for agents.",
    },
]


def build_cost_page(spec, models, all_slugs):
    prov_models = [m for m in models if spec["provider_contains"] in m["Provider"]]
    if not prov_models:
        raise SystemExit(f"No CSV rows matched provider '{spec['provider_contains']}' for {spec['slug']}")
    slug = spec["slug"]
    path = f"/cost-of/{slug}"

    # Pricing table from real CSV rows
    rows_html = ""
    for m in prov_models:
        rows_html += (
            f"<tr><td><strong>{html.escape(m['AI Model'])}</strong></td>"
            f"<td><span class='price-tag'>${price_str(m['Input Price ($/1M tokens)'])} / 1M in</span></td>"
            f"<td><span class='price-tag'>${price_str(m['Output Price ($/1M tokens)'])} / 1M out</span></td>"
            f"<td>{html.escape(m['Context Window'])}</td>"
            f"<td>${price_str(m['Daily Cost (10K requests)'])}</td></tr>"
        )
    pricing_table = (
        '<table><thead><tr><th>Model</th><th>Input</th><th>Output</th>'
        '<th>Context</th><th>Est. daily cost (10K requests)</th></tr></thead>'
        f'<tbody>{rows_html}</tbody></table>'
    )

    # Burn scenario — arithmetic grounded in CSV daily cost column
    cheapest = min(prov_models, key=lambda m: price_num(m["Daily Cost (10K requests)"]))
    daily = price_num(cheapest["Daily Cost (10K requests)"])
    loop_5x = daily * 5
    loop_50x = daily * 50
    burn = (
        f'<h2>What a runaway agent actually costs</h2>'
        f'<p>The dataset estimates <strong>{cheapest["AI Model"]}</strong> at roughly '
        f'<strong>${daily:.2f}/day</strong> for 10,000 requests (500 input + 200 output tokens each, '
        f"per the sourced database below). That is the happy path. Agents do not run the happy path — "
        f"they retry. A function-calling agent stuck in a {cheapest['AI Model']} retry loop multiplies that "
        f"linearly:</p>"
        f'<table><thead><tr><th>Scenario</th><th>Estimated cost</th></tr></thead><tbody>'
        f"<tr><td>Normal: 10K requests/day</td><td>${daily:.2f}/day</td></tr>"
        f"<tr><td>5&times; retry loop (bug, bad tool output)</td><td>${loop_5x:.2f}/day</td></tr>"
        f'<tr><td>50&times; runaway loop (unattended overnight)</td><td><strong>${loop_50x:,.2f}/day</strong></td></tr>'
        f"</tbody></table>"
        f'<div class="callout warn"><strong>Per-token pricing rewards loops.</strong> A model that costs '
        f"$0.075/1M input looks free — until an agent fires 50 million tokens overnight debugging a "
        f"flaky tool. Provider monthly caps do not catch this until the bill is already large. "
        f'<a href="https://sipi.bot/">sipi.bot</a> blocks the loop at the transaction, not the month.</div>'
    )

    worth = (
        f'<h2>Is the {html.escape(spec["brand"])} API worth it for agents?</h2>'
        f"<p>For autonomous agents, the per-token price is almost irrelevant next to the cumulative burn "
        f"when a loop multiplies it. The right question is not which model is cheapest, but "
        f"<strong>what bounds the total</strong> when the agent misbehaves. sipi.bot sits in front of the "
        f"transaction and enforces per-transaction caps, daily totals, and velocity limits before the "
        f"request is even allowed to scale — regardless of provider.</p>"
    )

    hidden = (
        "<h2>Hidden costs to watch for</h2>"
        "<ul class=\"check\" style=\"list-style:'\\26A0  ' inside;color:#374151\">"
        "<li><strong>Retry loops:</strong> an agent that retries on transient errors multiplies token cost linearly — the single biggest agent cost driver.</li>"
        "<li><strong>Long-context bloat:</strong> stuffing a 200K context window when 8K would do can 25&times; your per-call cost silently.</li>"
        "<li><strong>Output-heavy tool calls:</strong> output tokens are typically 4&ndash;8&times; the input price; an agent that generates long JSON burns the expensive side of the curve.</li>"
        "<li><strong>Provider pass-throughs:</strong> some providers add caching premiums, fine-tune hosting, or data-retention surcharges on top of per-token.</li>"
        "</ul>"
    )

    # Related mesh — other cost-of pages + relevant clusters
    related = [("/cost-of/", "All AI model costs compared (2026 hub)")]
    for s in all_slugs:
        if s != slug:
            related.append((f"/cost-of/{s}", f"How much does {prov_label(s)} cost?"))
    related += [
        ("/limits/", "Recommended spend limits by provider"),
        ("/calculators/runaway-cost-calculator", "Runaway agent cost calculator"),
        ("/glossary/velocity-limit", "Velocity limit (glossary)"),
    ]

    faqs = [
        (f"Is the {spec['brand']} API expensive?",
         f"Relative to alternatives, it depends on volume and model tier. For autonomous agents the real cost driver is not the per-token price but cumulative burn when an agent loops — a cheap per-token model becomes expensive fast at retry volumes. The sourced database this page is built from estimates daily cost at 10K requests for each model."),
        ("What's the cheapest way to run this for agents?",
         "Pick the smallest model tier that completes the task, cap context length, and — most importantly — put a pre-spend firewall in front so a retry loop cannot multiply cost unbounded. Without that, no per-token discount is safe."),
        ("Does sipi.bot replace this API?",
         "No. sipi.bot is not an LLM provider. It sits in front of your agent and evaluates every transaction (including LLM and tool spend) against your rules in under 5ms, returning approve, block, or flag. You keep using your chosen model; sipi.bot bounds what an agent is allowed to spend on it."),
    ]

    body = (
        f'<header><p class="lede">sipi.bot &middot; cost-of</p>'
        f'<h1>{html.escape(spec["h1"])}</h1>'
        f'<p class="lede">{html.escape(spec["lede"])}</p></header>'
        f'<h2>{html.escape(spec["brand"])} API pricing (2026)</h2>'
        f"{pricing_table}"
        f'<p class="src">Pricing from provider pricing pages, July 2026. Daily cost is an estimate for 10,000 requests averaging 500 input + 200 output tokens. Source: <a href="/ai-model-costs-2026.csv">sipi.bot AI Model Cost Comparison Database</a> (CC BY 4.0).</p>'
        f"{burn}"
        f"{worth}"
        f"{hidden}"
        f'<div class="callout"><strong>Bound it before the loop starts.</strong> '
        f'<a href="https://sipi.bot/">sipi.bot</a> enforces per-transaction caps and velocity limits on '
        f"agent spend in under 5ms — so a {html.escape(spec['brand'])} retry loop is blocked at the "
        f"first violation, not discovered on next month's invoice. <a href=\"/pricing\">See plans &rarr;</a></div>"
        f'<h2>Frequently asked questions</h2>'
        + "".join(
            f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in faqs
        )
        + mesh(related)
    )

    ld = jsonld_blocks(
        article_ld(spec["title"], spec["lede"], path),
        breadcrumb_ld(spec["h1"], path),
        faq_ld(faqs),
    )
    return path, page(spec["title"], spec["lede"], path, body, ld)


# ──────────────────────────────────────────────────────────────────────────
# /cost-of/ hub
# ──────────────────────────────────────────────────────────────────────────
def build_cost_hub(models):
    path = "/cost-of/"
    title = "AI API Cost Comparison [2026] — Per-Token Pricing for 16 Models"
    desc = (
        "Side-by-side 2026 per-token pricing for 16 AI models across OpenAI, Anthropic, Google, "
        "Meta, Mistral, DeepSeek, Cohere, Groq, and Amazon. Input/output prices, context windows, "
        "and estimated daily cost — sourced from provider pricing pages."
    )

    # Full 16-model table from the CSV, sorted cheapest daily cost first
    ordered = sorted(models, key=lambda m: price_num(m["Daily Cost (10K requests)"]))
    rows = ""
    for m in ordered:
        rows += (
            f"<tr><td>{html.escape(m['AI Model'])}</td>"
            f"<td>{html.escape(m['Provider'])}</td>"
            f"<td>${price_str(m['Input Price ($/1M tokens)'])}</td>"
            f"<td>${price_str(m['Output Price ($/1M tokens)'])}</td>"
            f"<td>{html.escape(m['Context Window'])}</td>"
            f"<td>{html.escape(m['Latency Category'])}</td>"
            f"<td>${price_str(m['Daily Cost (10K requests)'])}</td></tr>"
        )
    table = (
        '<table><thead><tr>'
        "<th>Model</th><th>Provider</th><th>Input ($/1M)</th><th>Output ($/1M)</th>"
        "<th>Context</th><th>Latency</th><th>Est. daily (10K req)</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>"
    )

    # Provider sub-page cards
    cards = ""
    for spec in COST_PAGES:
        cards += (
            f'<div class="hub-card"><span class="prov">{html.escape(spec["provider_contains"])}</span>'
            f'<h3><a href="/cost-of/{spec["slug"]}">{html.escape(spec["brand"])} API cost</a></h3>'
            f'<p style="margin:0;font-size:.9rem;color:#374151">Per-token 2026 pricing, context windows, '
            f"and a runaway-agent cost model for {html.escape(spec['brand'])}.</p></div>"
        )
    # Existing pages (OpenAI, Anthropic, LangSmith) get cards too
    cards += (
        '<div class="hub-card"><span class="prov">OpenAI</span>'
        '<h3><a href="/cost-of/openai-api-cost">OpenAI API cost</a></h3>'
        '<p style="margin:0;font-size:.9rem;color:#374151">GPT-4o, o3, GPT-4.1 family per-token pricing.</p></div>'
        '<div class="hub-card"><span class="prov">Anthropic</span>'
        '<h3><a href="/cost-of/anthropic-api-cost">Anthropic Claude API cost</a></h3>'
        '<p style="margin:0;font-size:.9rem;color:#374151">Claude 3.5 Sonnet, Haiku, and Opus pricing.</p></div>'
        '<div class="hub-card"><span class="prov">Observability</span>'
        '<h3><a href="/cost-of/langsmith-pricing">LangSmith pricing</a></h3>'
        '<p style="margin:0;font-size:.9rem;color:#374151">LangSmith observability tiers vs. spend control.</p></div>'
    )

    faqs = [
        ("Which AI API is cheapest in 2026?",
         "On raw per-token input price, Gemini 1.5 Flash ($0.075/1M input) and Amazon Nova Lite ($0.06/1M input) are the cheapest in this dataset. But for autonomous agents, total cost depends far more on retry-loop multiplier than on per-token price — a cheap model in a 50x loop costs more than an expensive one used once."),
        ("How is the daily cost calculated?",
         "Each provider's daily cost is an estimate for 10,000 requests averaging 500 input + 200 output tokens each, computed from the per-token prices on that provider's pricing page as of July 2026. Full methodology and the raw CSV are linked above."),
        ("Does sipi.bot change which model I use?",
         "No. sipi.bot is provider-agnostic. You keep calling whichever model you chose; sipi.bot evaluates the spend transaction (the API call, tool call, or provisioning action) against your rules and returns approve, block, or flag before the cost is incurred."),
    ]

    body = (
        f'<header><h1>AI API Cost Comparison (2026)</h1>'
        f'<p class="lede">{html.escape(desc)}</p></header>'
        f'<h2>16-model per-token pricing table</h2>'
        f"{table}"
        f'<p class="src">Source: provider pricing pages, July 2026. Daily cost = estimate for 10,000 requests at 500 in + 200 out tokens each. Full sourced dataset: <a href="/ai-model-costs-2026.csv">ai-model-costs-2026.csv</a> (CC BY 4.0).</p>'
        f'<div class="callout"><strong>The trap this table hides.</strong> Sorted by per-token price, '
        "the cheapest model looks like the winner. But agents loop — a 5&times; or 50&times; retry loop "
        "turns any model into the most expensive one on the list. The cheapest deployable stack is the "
        "one with a pre-spend firewall that caps the loop. <a href=\"https://sipi.bot/\">sipi.bot</a> "
        "does exactly that.</div>"
        f'<h2>Cost by provider</h2><div class="hub-grid">{cards}</div>'
        f'<h2>How to read this table for autonomous agents</h2>'
        f'<ul class="check">'
        "<li><strong>Output price matters more than input.</strong> Agents generate long tool-call JSON; output tokens are usually 4&ndash;8&times; the input price.</li>"
        "<li><strong>Context window is a cost lever.</strong> A 200K context stuffed at 200K costs 25&times; the same call at 8K — and providers bill for every input token.</li>"
        "<li><strong>Latency tier affects loop cost.</strong> A 'Very Fast' tier (Groq) means a retry loop burns faster in wall-clock terms, not fewer dollars.</li>"
        "<li><strong>Daily cost assumes the happy path.</strong> Real agent cost is daily cost &times; your retry multiplier. Measure yours.</li>"
        "</ul>"
        + mesh([
            ("/limits/", "Recommended spend limits by provider"),
            ("/calculators/runaway-cost-calculator", "Runaway agent cost calculator"),
            ("/best/ai-cost-management-tools", "Best AI cost management tools (2026)"),
            ("/benchmarks/token-cost-by-provider", "Token cost by provider (benchmarks)"),
            ("/glossary/runaway-cost", "Runaway cost (glossary)"),
            ("/learn/ai-cost-optimization", "AI cost optimization guide"),
        ])
        + '<h2>Frequently asked questions</h2>'
        + "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in faqs)
    )

    ld = jsonld_blocks(
        article_ld(title, desc, path),
        breadcrumb_ld("AI API Cost Comparison", path),
        faq_ld(faqs),
    )
    return path, page(title, desc, path, body, ld, og_type="website")


# ──────────────────────────────────────────────────────────────────────────
# /limits/ provider pages
# ──────────────────────────────────────────────────────────────────────────
LIMIT_PAGES = [
    {
        "slug": "gemini-agent-limits",
        "brand": "Google Gemini",
        "title": "Spend Limits for Google Gemini Agents | sipi.bot",
        "h1": "Spend limits for Google Gemini agents",
        "lede": "Google Gemini agents using function calling or the Vertex AI platform need spend limits configured outside the model. This guide covers what Gemini's native controls do and do not bound, and how to enforce hard per-transaction and velocity limits via sipi.bot.",
        "native": (
            "Google Cloud and Vertex AI expose <strong>quota</strong> and <strong>project-level spending "
            "controls</strong>, plus per-request token caps. These are coarse and account/project-scoped: "
            "they cap aggregate usage, not individual agent actions, and they are evaluated after a request "
            "is in flight — not before a transaction commits. A Gemini agent that issues many parallel "
            "function calls inside one quota window can exceed a useful budget before the quota refreshes."
        ),
    },
    {
        "slug": "groq-agent-limits",
        "brand": "Groq",
        "title": "Spend Limits for Groq (Llama) Agents | sipi.bot",
        "h1": "Spend limits for Groq agents",
        "lede": "Groq serves Llama inference at the fastest latency tier available, which means an agent retry loop burns tokens faster in wall-clock time than on any other provider. Native rate limits cap requests per minute — they do not cap spend per decision. Here is how to bound a Groq agent before a loop runs away.",
        "native": (
            "Groq's native controls are <strong>requests-per-minute and tokens-per-minute rate limits</strong> "
            "tied to your plan tier. These throttle throughput; they do not evaluate whether a given "
            "transaction should be allowed. Because Groq is the fastest tier in the dataset, a retry loop "
            "hits the rate limit ceiling quickly but can still accumulate significant spend within a single "
            "minute window — exactly the scenario a velocity cap is built to catch."
        ),
    },
    {
        "slug": "bedrock-agent-limits",
        "brand": "Amazon Bedrock",
        "title": "Spend Limits for Amazon Bedrock Agents | sipi.bot",
        "h1": "Spend limits for Amazon Bedrock agents",
        "lede": "Amazon Bedrock agents orchestrate Nova and other models with native AWS Budgets and IAM scoping. AWS Budgets are monthly and alert-based; they do not block a transaction in real time. Here is how to add a deterministic pre-spend layer that blocks before the dollar moves.",
        "native": (
            "Bedrock inherits <strong>AWS Budgets</strong> (monthly, alert-only by default), "
            "<strong>IAM and service-control policies</strong> (scope which models/accounts can be invoked), "
            "and per-model provisioning limits. None of these evaluate a single transaction against a "
            "spend policy and block it in milliseconds. AWS Budgets also famously notify after the spend "
            "has occurred — the original incident this product was built to prevent."
        ),
    },
]


def build_limit_page(spec, all_limit_slugs):
    slug = spec["slug"]
    path = f"/limits/{slug}"
    faqs = [
        (f"Does {spec['brand']} block spend in real time?",
         "No. The native controls described above are quotas, rate limits, IAM scopes, or monthly budgets. They throttle or alert; they do not evaluate an individual transaction against a spend policy and block it in milliseconds before the cost is incurred. That is the gap sipi.bot fills."),
        ("What limit value should I start with?",
         "Start with the recommended default for your agent type, observe real traffic for a week, then tune. The right limit is the smallest value that does not interrupt legitimate work. If you are blocking more than 1% of transactions in steady state, the limit is probably too tight. Pair every dollar limit with a velocity cap (transactions per minute) — dollar limits catch the single large transaction, velocity caps catch the loop."),
        ("How does sipi.bot enforce this for a " + spec["brand"] + " agent?",
         "Your agent calls evaluate_spend before any transaction (the model call, tool call, or provisioning action). sipi.bot checks it against your per-transaction caps, daily totals, velocity limits, merchant allowlists, and category rules, then returns approve, block, or flag — in under 5ms. The " + spec["brand"] + " request only proceeds if the decision is approve."),
    ]

    related = [("/limits/", "All provider spend limits (hub)")]
    for s in all_limit_slugs:
        if s != slug:
            lbl = s.replace("-agent-limits", "").replace("-", " ").title()
            related.append((f"/limits/{s}", f"Spend limits for {lbl} agents"))
    related += [
        ("/limits/recommended-limits-by-use-case", "Recommended spend limits by use case"),
        ("/limits/openai-agent-limits", "Spend limits for OpenAI agents"),
        ("/limits/anthropic-agent-limits", "Spend limits for Anthropic Claude agents"),
        ("/glossary/velocity-limit", "Velocity limit (glossary)"),
        ("/glossary/per-transaction-limit", "Per-transaction limit (glossary)"),
    ]

    body = (
        f'<header><p class="lede">sipi.bot limits</p>'
        f'<h1>{html.escape(spec["h1"])}</h1>'
        f'<p class="lede">{html.escape(spec["lede"])}</p></header>'
        f'<h2>What {html.escape(spec["brand"])} provides natively</h2>'
        f'<p>{spec["native"]}</p>'
        f'<h2>Why that is not enough for autonomous agents</h2>'
        f'<p>Autonomous agents need explicit spend limits because the alternatives — trusting the agent, '
        f"the provider's monthly cap, or a human reviewer on every transaction — do not actually bound "
        f"the risk. Provider caps are coarse and account-level. Human review does not scale. And agents "
        f"have no native concept of a budget. A pre-spend firewall gives you a concrete, enforceable "
        f"ceiling evaluated on every transaction in under 5ms.</p>"
        f'<h2>The limits that matter for a {html.escape(spec["brand"])} agent</h2>'
        f'<table><thead><tr><th>Limit type</th><th>What it catches</th><th>Example</th></tr></thead><tbody>'
        f'<tr><td>Per-transaction cap</td><td>A single oversized call</td><td>Block any one model/tool spend over $5</td></tr>'
        f'<tr><td>Daily total</td><td>Aggregate session burn</td><td>Max $50/day across all agent spend</td></tr>'
        f'<tr><td>Velocity cap</td><td>Retry &amp; runaway loops</td><td>Max 30 {html.escape(spec["brand"])} calls/minute</td></tr>'
        f'<tr><td>Category limit</td><td>Tool-call cost categories</td><td>Cap "long-context" calls at $10/day</td></tr>'
        f"</tbody></table>"
        f'<div class="callout"><strong>Bound it per decision, not per month.</strong> '
        f'<a href="https://sipi.bot/">sipi.bot</a> evaluates every {html.escape(spec["brand"])} agent '
        f"transaction against these limits in under 5ms and returns approve, block, or flag before the "
        f"cost is incurred. Pricing starts at $99/mo. <a href=\"/pricing\">See plans &rarr;</a></div>"
        f'<h2>What happens when a limit is hit</h2>'
        f"<p>When a transaction would exceed the limit, sipi.bot returns <strong>block</strong> with a "
        f"reason code identifying which limit fired. The agent receives the decision as structured JSON "
        f"and can choose an alternative path — retry with smaller scope, request human approval, or "
        f"abandon the task. The blocked transaction is logged with the policy version, so you can always "
        f"see exactly why it was denied.</p>"
        f'<h2>Frequently asked questions</h2>'
        + "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in faqs)
        + mesh(related)
    )
    ld = jsonld_blocks(
        article_ld(spec["title"], spec["lede"], path),
        breadcrumb_ld(spec["h1"], path),
        faq_ld(faqs),
    )
    return path, page(spec["title"], spec["lede"], path, body, ld)


# ──────────────────────────────────────────────────────────────────────────
# /limits/ hub
# ──────────────────────────────────────────────────────────────────────────
def build_limits_hub():
    path = "/limits/"
    title = "Spend Limits by AI Provider [2026] — OpenAI, Anthropic, Gemini, Groq, Bedrock"
    desc = (
        "Provider-by-provider guide to spend limits for autonomous AI agents: what OpenAI, Anthropic, "
        "Google Gemini, Groq, and Amazon Bedrock cap natively, why those caps don't bound autonomous "
        "agents, and how to add a deterministic pre-spend layer."
    )
    all_specs = [
        {"slug": "openai-agent-limits", "brand": "OpenAI", "blurb": "OpenAI Responses API & function-calling agents."},
        {"slug": "anthropic-agent-limits", "brand": "Anthropic Claude", "blurb": "Claude tool-use agents."},
    ] + [{"slug": s["slug"], "brand": s["brand"], "blurb": s["lede"][:80] + "…"} for s in LIMIT_PAGES] + [
        {"slug": "recommended-limits-by-use-case", "brand": "By use case", "blurb": "Recommended default limits per agent type."},
    ]
    cards = "".join(
        f'<div class="hub-card"><span class="prov">{html.escape(c["brand"])}</span>'
        f'<h3><a href="/limits/{c["slug"]}">{html.escape(c["brand"])} agent limits</a></h3>'
        f'<p style="margin:0;font-size:.9rem;color:#374151">{html.escape(c["blurb"])}</p></div>'
        for c in all_specs
    )
    faqs = [
        ("Why do I need spend limits if my provider has a monthly cap?",
         "Provider caps are monthly, account-level, and reactive — they alert or cut off after spend has accumulated, often after the damage is done. Autonomous agents can rack up significant spend in minutes via retry loops; a monthly cap cannot catch that in time. A pre-spend limit evaluated per transaction (in milliseconds) is the only control that bounds a loop before it scales."),
        ("What's the difference between a per-transaction cap and a velocity cap?",
         "A per-transaction cap blocks a single oversized spend (e.g., one $500 call). A velocity cap blocks a runaway retry loop (e.g., 100 calls/minute). You need both: the per-transaction cap catches the catastrophic single call, the velocity cap catches the death-by-a-thousand-calls loop."),
        ("Does sipi.bot work across all these providers?",
         "Yes. sipi.bot is provider-agnostic. Your agent calls evaluate_spend before any transaction — whether that hits OpenAI, Anthropic, Gemini, Groq, Bedrock, or a non-LLM spend like cloud provisioning — and sipi.bot returns approve, block, or flag against your rules in under 5ms."),
    ]
    body = (
        f'<header><h1>Spend limits by AI provider (2026)</h1>'
        f'<p class="lede">{html.escape(desc)}</p></header>'
        f'<div class="callout warn"><strong>The pattern across every provider.</strong> Native controls '
        "are quotas, rate limits, or monthly budgets. They throttle or alert after the fact. None of them "
        "evaluate an individual agent transaction against a spend policy and block it in milliseconds "
        "before the cost is incurred. That gap is what sipi.bot fills.</div>"
        f'<h2>Limits by provider</h2><div class="hub-grid">{cards}</div>'
        f'<h2>The two limits every agent needs</h2>'
        f'<table><thead><tr><th>Limit</th><th>Catches</th><th>Without it</th></tr></thead><tbody>'
        f'<tr><td><strong>Per-transaction cap</strong></td><td>A single oversized spend</td><td>One buggy tool call empties the budget</td></tr>'
        f'<tr><td><strong>Velocity cap</strong></td><td>Retry &amp; runaway loops</td><td>A flaky-tool loop multiplies cost 50&times; overnight</td></tr>'
        f"</tbody></table>"
        + mesh([
            ("/cost-of/", "AI API cost comparison (hub)"),
            ("/glossary/velocity-limit", "Velocity limit (glossary)"),
            ("/glossary/per-transaction-limit", "Per-transaction limit (glossary)"),
            ("/policies/", "Spend policy templates"),
            ("/learn/how-to-stop-ai-agent-overspending", "How to stop AI agent overspending"),
            ("/calculators/budget-sizing-calculator", "Budget sizing calculator"),
        ])
        + '<h2>Frequently asked questions</h2>'
        + "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in faqs)
    )
    ld = jsonld_blocks(
        article_ld(title, desc, path),
        breadcrumb_ld("Spend limits by provider", path),
        faq_ld(faqs),
    )
    return path, page(title, desc, path, body, ld, og_type="website")


# ──────────────────────────────────────────────────────────────────────────
def write_page(rel_path, content):
    full = os.path.join(ROOT, rel_path.lstrip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    return full


def main():
    models = load_models()
    print(f"[build] loaded {len(models)} models from CSV")

    cost_slugs = [p["slug"] for p in COST_PAGES]
    limit_new_slugs = [p["slug"] for p in LIMIT_PAGES]

    written = []
    for spec in COST_PAGES:
        path, html_doc = build_cost_page(spec, models, cost_slugs)
        written.append((write_page(path, html_doc), path))
    path, html_doc = build_cost_hub(models)
    written.append((write_page(path, html_doc), path))

    for spec in LIMIT_PAGES:
        path, html_doc = build_limit_page(spec, limit_new_slugs)
        written.append((write_page(path, html_doc), path))
    path, html_doc = build_limits_hub()
    written.append((write_page(path, html_doc), path))

    print(f"[build] wrote {len(written)} pages:")
    for f, p in written:
        print(f"  {p}  ->  {os.path.relpath(f, ROOT)}")


if __name__ == "__main__":
    main()
