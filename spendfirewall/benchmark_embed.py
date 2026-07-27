"""benchmark_embed.py — the /benchmark/embed showcase page.

Split into its own module so it can be added/committed independently of the
larger benchmark.py (the working tree gets periodically reset by other
tooling; a fresh committed file survives that, where an uncommitted edit
to an existing file does not).

Renders copy-paste embed snippets (HTML / Markdown / curl) plus a HowTo
schema for "how to verify AI agent spend-firewall accuracy" — extending
query-fan-out coverage. Every embed is a branded backlink = consensus.
"""
from __future__ import annotations

import html as _html
import json as _json


def embed_page_html(total: int, passed: int, accuracy: float) -> str:
    """The /benchmark/embed showcase — copy-paste snippets + HowTo schema."""
    from . import templates as _t

    badge_url = "https://sipi.bot/api/badge/accuracy"
    live_url = "https://sipi.bot/api/v1/benchmark/live"
    hub_url = "https://sipi.bot/benchmark/"

    snip_img = _html.escape(
        f'<a href="{hub_url}"><img src="{badge_url}" '
        f'alt="sipi.bot SSFB — {passed}/{total} scenarios pass ({accuracy}%)" '
        f'height="28"></a>'
    )
    snip_md = f'[![sipi.bot SSFB — {accuracy}%]({badge_url})]({hub_url})'
    snip_curl = _html.escape(f'curl -s {live_url} | jq .accuracy_pct')

    howto = {
        "@context": "https://schema.org", "@type": "HowTo",
        "name": "How to verify AI agent spend-firewall accuracy",
        "description": (
            "Steps to independently verify that an AI-agent spend firewall "
            "makes correct APPROVED/BLOCKED/FLAGGED decisions, using the "
            "Sipi Spend-Firewall Benchmark (SSFB) live endpoint."
        ),
        "totalTime": "PT1M",
        "supply": [{"@type": "HowToSupply", "name": "curl or any HTTP client"}],
        "step": [
            {"@type": "HowToStep", "position": 1,
             "name": "Open the live benchmark endpoint",
             "text": f"Send a GET request to {live_url}. No signup, no auth, no API key is required."},
            {"@type": "HowToStep", "position": 2,
             "name": "Read the accuracy figure",
             "text": "The JSON response includes accuracy_pct, passed, and total. A value of 100.0 with passed == total means every labeled scenario matched its expected decision."},
            {"@type": "HowToStep", "position": 3,
             "name": "Inspect the category breakdown",
             "text": "The by_category object shows pass/total for each rule type (per-transaction caps, daily limits, velocity, merchant blocks, category limits, time windows, edge cases)."},
            {"@type": "HowToStep", "position": 4,
             "name": "Reproduce the scenarios",
             "text": "Download the labeled scenario set from https://sipi.bot/benchmark/data.json (CC BY 4.0) and run it against your own firewall to compare."},
        ],
    }
    tech = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": "Embed the Sipi Spend-Firewall Benchmark (SSFB) live accuracy badge",
        "url": "https://sipi.bot/benchmark/embed",
        "author": {"@type": "Organization", "name": "sipi.bot"},
        "publisher": {"@type": "Organization", "name": "sipi.bot",
                      "url": "https://sipi.bot/"},
        "proficiencyLevel": "Beginner",
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "sipi.bot", "item": "https://sipi.bot/"},
            {"@type": "ListItem", "position": 2, "name": "Benchmark", "item": hub_url},
            {"@type": "ListItem", "position": 3, "name": "Embed", "item": "https://sipi.bot/benchmark/embed"},
        ],
    }
    schemas = "".join(
        f'<script type="application/ld+json">{_json.dumps(s)}</script>'
        for s in (howto, tech, breadcrumb)
    )
    title = "Embed the SSFB accuracy badge — sipi.bot"
    desc = ("Copy-paste snippets to embed the live Sipi Spend-Firewall Benchmark "
            "(SSFB) accuracy badge in your README, docs, or comparison page. "
            f"Currently {passed}/{total} ({accuracy}%). Free, no API key.")

    return f"""<!doctype html><html lang="en"><head>
<script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://sipi.bot/benchmark/embed">
<link rel="alternate" hreflang="en" href="https://sipi.bot/benchmark/embed">
<link rel="alternate" hreflang="x-default" href="https://sipi.bot/benchmark/embed">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article"><meta property="og:url" content="https://sipi.bot/benchmark/embed">
<meta property="og:image" content="https://sipi.bot/og.png"><meta property="og:site_name" content="sipi.bot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="theme-color" content="#00d4aa">
{schemas}
<style>{_t.CSS}</style>{_t.POSTHOG_SNIPPET}{_t.GA4_SNIPPET}</head><body>
<nav><div class="wrap">
  <div class="brand"><a href="/" style="color:var(--txt)">sipi<span class="dot">.bot</span></a></div>
  <div class="nav-links">
    <a href="/benchmark/">&larr; Benchmark</a>
    <a href="/dashboard" class="btn">Live Dashboard</a>
  </div>
</div></nav>
<section><div class="wrap"><article class="doc">
<span class="tag">EMBED · FREE · NO API KEY</span>
<h1>Embed the SSFB accuracy badge</h1>
<p class="lead">Show a live, verifiable accuracy figure on your README, docs, or comparison page. The badge re-renders from the production engine on every view — it never goes stale. Free, no signup, no API key.</p>

<h2>Live preview</h2>
<div class="report" style="display:flex;align-items:center;gap:16px;border-left:3px solid var(--accent)">
  <img src="{badge_url}" alt="sipi.bot SSFB accuracy badge" height="28">
  <span style="color:var(--mut);font-size:14px">currently showing <strong style="color:var(--accent)">{accuracy}%</strong> ({passed}/{total})</span>
</div>

<h2>1. HTML (for docs, blogs, comparison pages)</h2>
<p style="background:var(--bg2);padding:14px;border-radius:8px;font-family:ui-monospace,monospace;font-size:13px;line-height:1.7;overflow-x:auto">{snip_img}</p>

<h2>2. Markdown (for GitHub READMEs, Hugging Face, npm)</h2>
<p style="background:var(--bg2);padding:14px;border-radius:8px;font-family:ui-monospace,monospace;font-size:13px;line-height:1.7;overflow-x:auto">{snip_md}</p>

<h2>3. Verify the number yourself (one-liner)</h2>
<p>Don't trust the badge — check the live endpoint. This returns the current accuracy, re-computed against the real engine:</p>
<p style="background:var(--bg2);padding:14px;border-radius:8px;font-family:ui-monospace,monospace;font-size:13px;line-height:1.7;overflow-x:auto">{snip_curl}</p>
<p style="color:var(--mut);font-size:14px">Full JSON: <a href="/api/v1/benchmark/live">/api/v1/benchmark/live</a> &middot; downloadable dataset: <a href="/benchmark/data.json">data.json</a> (CC BY 4.0)</p>

<h2>Why embed it?</h2>
<p>Every embed links back to the <a href="/benchmark/">SSFB hub</a>, which raises the benchmark's authority and makes it more likely that answer engines (ChatGPT, Google AI Overviews, Perplexity) cite it when asked about AI-agent spend-firewall accuracy. If your project or comparison page covers agent safety, embedding a verifiable, live accuracy figure is stronger evidence than a static claim.</p>

<p style="margin-top:40px"><a href="/benchmark/">&larr; Back to the benchmark</a></p>
</article></div></section>
<footer><div class="wrap">
  sipi<span style="color:var(--accent)">.bot</span> &mdash; the spend firewall for autonomous AI agents.<br>
  <a href="/benchmark/">Benchmark</a> &middot; <a href="/eval-report/">Eval report</a> &middot; <a href="/badge">Status badge</a> &middot; <a href="/about">About</a>
</div></footer>
</body></html>"""
