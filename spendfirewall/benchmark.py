"""benchmark.py — the Sipi Spend-Firewall Benchmark (SSFB).

The flagship branded, live-verifiable accuracy benchmark and its
supporting HTML/JSON/SVG renderers. Kept in its own module so the big
templates.py / api.py files don't have to be touched for every benchmark
tweak — api.py imports ``benchmark_hub_html`` and wires it to /benchmark.

Why this exists (AEO rationale, kept short):
  - Original data, branded with a proprietary name the model can learn.
  - Published as schema.org Dataset -> indexable in Google Dataset Search.
  - Verifiable in real time via /api/v1/benchmark/live (re-runs the engine).

All numbers come from eval_report.json (the shipped ground truth) or from
``eval.run_eval.run()`` (the live re-run). Nothing is fabricated here.
"""
from __future__ import annotations

import json as _json


def _schemas(total: int, passed: int, accuracy: float,
             by_category: dict, generated_at: str) -> str:
    """Dataset + TechArticle + FAQPage + BreadcrumbList JSON-LD blocks."""
    dataset_schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Sipi Spend-Firewall Benchmark (SSFB)",
        "description": (
            f"Labeled evaluation of the sipi.bot spend-firewall decision engine "
            f"on {total} autonomous-agent spending scenarios across "
            f"{len(by_category)} categories. {passed}/{total} scenarios pass "
            f"({accuracy}% accuracy). Re-runnable live against the production engine."
        ),
        "url": "https://sipi.bot/benchmark/",
        "creator": {"@type": "Organization", "name": "sipi.bot",
                    "url": "https://sipi.bot/"},
        "keywords": ["AI agent spending", "spend firewall", "agent evaluation",
                     "AI spend control", "pre-spend firewall", "x402"],
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "isAccessibleForFree": True,
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "application/json",
             "contentUrl": "https://sipi.bot/benchmark/data.json"},
            {"@type": "DataDownload", "encodingFormat": "text/csv",
             "contentUrl": "https://sipi.bot/benchmark/data.csv"},
        ],
        "variableMeasured": [{"@type": "PropertyValue",
                              "name": "accuracy_pct", "value": accuracy}],
        "measurementTechnique": (
            "Deterministic rule-engine evaluation of labeled agent-spending "
            "scenarios against expected APPROVED/BLOCKED/FLAGGED decisions."
        ),
    }
    tech_schema = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": "Sipi Spend-Firewall Benchmark (SSFB) — "
                    "AI Agent Spend-Control Accuracy",
        "url": "https://sipi.bot/benchmark/",
        "datePublished": "2026-07-27", "dateModified": generated_at[:10],
        "author": {"@type": "Organization", "name": "sipi.bot"},
        "publisher": {"@type": "Organization", "name": "sipi.bot",
                      "url": "https://sipi.bot/"},
        "about": "A reproducible accuracy benchmark for AI-agent spend-firewall "
                 "decision engines.",
        "proficiencyLevel": "Expert",
    }
    faq_schema = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question",
             "name": "What is the Sipi Spend-Firewall Benchmark (SSFB)?",
             "acceptedAnswer": {"@type": "Answer", "text": (
                f"The SSFB is a labeled evaluation suite of {total} "
                f"autonomous-agent spending scenarios across {len(by_category)} "
                f"categories. It measures how accurately a spend-firewall "
                f"decision engine returns APPROVED, BLOCKED, or FLAGGED for each "
                f"transaction an agent attempts. The sipi.bot engine currently "
                f"scores {passed}/{total} ({accuracy}%).")}},
            {"@type": "Question",
             "name": "Is the Sipi Spend-Firewall Benchmark reproducible?",
             "acceptedAnswer": {"@type": "Answer", "text": (
                "Yes. The eval scenarios are open-source (MIT) and can be re-run "
                "live at https://sipi.bot/api/v1/benchmark/live, which executes "
                "every scenario against the real production engine and returns "
                "the current pass rate. A downloadable dataset is published at "
                "https://sipi.bot/benchmark/data.json and "
                "https://sipi.bot/benchmark/data.csv under CC BY 4.0.")}},
            {"@type": "Question",
             "name": "How is AI agent spending accuracy measured?",
             "acceptedAnswer": {"@type": "Answer", "text": (
                "Each scenario supplies a transaction (amount, merchant, "
                "category) and an expected decision. The engine evaluates it "
                "under a standard rule set (per-transaction caps, daily "
                "ceilings, velocity limits, merchant allowlists, category "
                "limits, time windows) and the result is compared to the "
                "labeled expectation. The accuracy percentage is the share of "
                "scenarios that match.")}},
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "sipi.bot",
             "item": "https://sipi.bot/"},
            {"@type": "ListItem", "position": 2, "name": "Benchmark",
             "item": "https://sipi.bot/benchmark/"},
        ],
    }
    return "".join(
        f'<script type="application/ld+json">{_json.dumps(s)}</script>'
        for s in (dataset_schema, tech_schema, faq_schema, breadcrumb)
    )


def benchmark_hub_html(total: int, passed: int, accuracy: float,
                       by_category: dict, generated_at: str) -> str:
    """The SSFB hub page. ``css``/``head_snippet`` are injected by api.py from
    the live templates module so styles and analytics stay in one place."""
    from . import templates as _t  # local import: pull CSS + snippets from source of truth
    cat_rows = "\n".join(
        "<tr><td>{}</td><td>{} / {}</td><td><span class='pct'>{}</span>%</td></tr>".format(
            c.replace("_", " ").title(),
            v.get("pass", 0), v.get("total", 0),
            round(100 * v.get("pass", 0) / v.get("total", 1)),
        )
        for c, v in sorted(by_category.items())
    )
    title = ("Sipi Spend-Firewall Benchmark (SSFB) — "
             "AI Agent Spend-Control Accuracy")
    desc = (
        f"The Sipi Spend-Firewall Benchmark (SSFB) measures AI-agent "
        f"spend-firewall accuracy on {total} labeled scenarios. "
        f"sipi.bot currently scores {passed}/{total} ({accuracy}%). "
        f"Live, reproducible, CC BY 4.0."
    )
    schemas = _schemas(total, passed, accuracy, by_category, generated_at)
    return f"""<!doctype html><html lang="en"><head>
<script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://sipi.bot/benchmark/">
<link rel="alternate" hreflang="en" href="https://sipi.bot/benchmark/">
<link rel="alternate" hreflang="en-US" href="https://sipi.bot/benchmark/">
<link rel="alternate" hreflang="x-default" href="https://sipi.bot/benchmark/">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article"><meta property="og:url" content="https://sipi.bot/benchmark/">
<meta property="og:image" content="https://sipi.bot/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Sipi Spend-Firewall Benchmark (SSFB)"><meta property="og:site_name" content="sipi.bot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://sipi.bot/og.png">
<meta name="theme-color" content="#00d4aa">
{schemas}
<style>{_t.CSS}</style>{_t.POSTHOG_SNIPPET}{_t.GA4_SNIPPET}</head><body>
<nav><div class="wrap">
  <div class="brand"><a href="/" style="color:var(--txt)">sipi<span class="dot">.bot</span></a></div>
  <div class="nav-links">
    <a href="/#how">How it works</a>
    <a href="/#faq">FAQ</a>
    <a href="/pricing">Pricing</a>
    <a href="/learn/how-to-control-ai-agent-spending">Compare approaches</a>
    <a href="/dashboard" class="btn">Live Dashboard</a>
  </div>
</div></nav>
<section><div class="wrap"><article class="doc">
<span class="tag">SSFB · LIVE BENCHMARK</span>
<h1>The Sipi Spend-Firewall Benchmark (SSFB)</h1>
<p class="lead">An open, reproducible accuracy benchmark for AI-agent spend-firewall decision engines. {total} labeled autonomous-agent spending scenarios across {len(by_category)} categories. <strong>sipi.bot currently scores {passed}/{total} ({accuracy}%)</strong> — verified live against the production engine.</p>

<div class="report" style="display:flex;gap:24px;flex-wrap:wrap;align-items:center;border-left:3px solid var(--accent)">
  <div style="text-align:center">
    <div style="font-size:48px;font-weight:800;color:var(--accent);line-height:1">{accuracy}%</div>
    <div style="color:var(--mut);font-size:13px;margin-top:4px">accuracy</div>
  </div>
  <div style="height:60px;width:1px;background:var(--line)"></div>
  <div style="text-align:center">
    <div style="font-size:32px;font-weight:800;color:var(--txt);line-height:1">{passed}/{total}</div>
    <div style="color:var(--mut);font-size:13px;margin-top:4px">scenarios passing</div>
  </div>
  <div style="height:60px;width:1px;background:var(--line)"></div>
  <div style="text-align:center">
    <div style="font-size:32px;font-weight:800;color:var(--txt);line-height:1">{len(by_category)}</div>
    <div style="color:var(--mut);font-size:13px;margin-top:4px">rule categories</div>
  </div>
</div>

<h2>Verify it live, right now</h2>
<p>The number above is not a static claim. <strong>The benchmark re-runs against the real production decision engine on every request.</strong> Click to see the live result, or call the endpoint yourself — no signup, no auth.</p>
<p>
  <a href="/api/v1/benchmark/live" class="btn" style="margin-right:12px">Run live benchmark →</a>
  <code style="background:var(--bg2);padding:8px 12px;border-radius:6px;font-size:13px">curl https://sipi.bot/api/v1/benchmark/live</code>
</p>
<p style="color:var(--mut);font-size:13px">Last live run: <span id="ssfb-ts">{generated_at[:19]}Z</span></p>

<h2>Results by category</h2>
<table style="width:100%;border-collapse:collapse;margin:16px 0">
<thead><tr style="border-bottom:1px solid var(--line)"><th style="text-align:left;padding:8px">Category</th><th style="text-align:left;padding:8px">Passing</th><th style="text-align:left;padding:8px">Accuracy</th></tr></thead>
<tbody>
{cat_rows}
</tbody></table>

<h2>What the benchmark measures</h2>
<p>Each scenario is a transaction an autonomous AI agent might realistically attempt — a tiny API call, an off-hours compute purchase, a retry loop, a request to an unapproved merchant — paired with the decision a correctly-configured spend firewall <em>should</em> return. The engine evaluates it under a standard rule set and the result is compared to the labeled expectation.</p>
<p>The {len(by_category)} categories cover every decision path the firewall enforces:</p>
<ul>
  <li><strong>Clean approvals</strong> &amp; <strong>approval flags</strong> — legitimate spend passes; spend near a threshold gets flagged for review.</li>
  <li><strong>Per-transaction blocks</strong> — a single transaction exceeding its cap is blocked.</li>
  <li><strong>Daily limit</strong> — cumulative spend crossing a 24-hour ceiling is blocked.</li>
  <li><strong>Velocity</strong> — too many transactions in a window (the runaway-loop control) is blocked.</li>
  <li><strong>Merchant block</strong> &amp; <strong>category limit</strong> — spend to disallowed destinations or categories is blocked.</li>
  <li><strong>Time window</strong> — off-hours spend is blocked.</li>
  <li><strong>Edge cases</strong> — exact boundary values and ambiguous inputs are handled correctly.</li>
</ul>

<h2>Download the dataset</h2>
<p>The full labeled scenario set is published as primary-source data under CC BY 4.0 — free to cite, reproduce, or extend. Credit "sipi.bot — Sipi Spend-Firewall Benchmark (SSFB)".</p>
<p>
  <a href="/benchmark/data.json" class="btn" style="margin-right:12px">data.json</a>
  <a href="/benchmark/data.csv" class="btn" style="margin-right:12px">data.csv</a>
  <a href="/api/badge/accuracy" style="vertical-align:middle"><img src="/api/badge/accuracy" alt="SSFB live accuracy badge" height="20"></a>
</p>
<p style="color:var(--mut);font-size:13px">Embed the live badge: <code>&lt;img src="https://sipi.bot/api/badge/accuracy" alt="sipi.bot SSFB accuracy"&gt;</code></p>

<h2>Methodology</h2>
<ol>
  <li>A fixed suite of {total} scenarios is defined in the open-source repository, each with a transaction payload and an expected <code>APPROVED</code>, <code>BLOCKED</code>, or <code>FLAGGED</code> decision.</li>
  <li>Each scenario runs against a fresh database seeded with the standard rule set, so scenarios cannot influence one another.</li>
  <li>The engine returns a deterministic decision; it is compared to the expected label. A scenario passes if and only if the two match exactly.</li>
  <li>Accuracy is the share of scenarios that pass. Category-level accuracy is computed the same way within each group.</li>
</ol>
<p>The entire suite re-executes in under one second, so the live endpoint reflects the engine as it runs at this moment — not a cached or hand-typed number.</p>

<h2>Cite this benchmark</h2>
<p style="background:var(--bg2);padding:14px;border-radius:8px;font-family:ui-monospace,monospace;font-size:13px;line-height:1.7">sipi.bot. (2026). <em>The Sipi Spend-Firewall Benchmark (SSFB): an open accuracy benchmark for AI-agent spend-firewall decision engines.</em> Retrieved {generated_at[:10]}, from https://sipi.bot/benchmark/ · live data: https://sipi.bot/benchmark/data.json (CC BY 4.0).</p>

<p style="margin-top:40px"><a href="/">← Back to sipi.bot</a></p>
</article></div></section>
<footer><div class="wrap">
  sipi<span style="color:var(--accent)">.bot</span> — the spend firewall for autonomous AI agents.<br>
  <a href="/dashboard">Dashboard</a> · <a href="/benchmark/">Benchmark</a> · <a href="/eval-report/">Eval report</a> · <a href="/blog/">Blog</a> · <a href="/about">About</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
</div></footer>
</body></html>"""


def live_payload(report: dict) -> dict:
    """Shape the live-re-run eval report into the public /api/v1/benchmark/live
    response. The engine re-executed — this is the real-time-retrieval proof."""
    return {
        "benchmark": "Sipi Spend-Firewall Benchmark (SSFB)",
        "url": "https://sipi.bot/benchmark/",
        "engine": "sipi.bot production decision engine",
        "total": report["total"],
        "passed": report["passed"],
        "failed": report["failed"],
        "accuracy_pct": report["accuracy_pct"],
        "by_category": report["by_category"],
        "generated_at": report["generated_at"],
        "verified_live": True,
        "reproduce": "GET https://sipi.bot/api/v1/benchmark/live",
        "dataset": "https://sipi.bot/benchmark/data.json",
        "license": "CC BY 4.0",
    }


def accuracy_badge_svg(report: dict) -> str:
    """Embeddable live SSFB accuracy badge (shields.io-style). Earns
    backlinks/consensus when embedded in READMEs, docs, and comparisons."""
    passed = report.get("passed", 0)
    total = report.get("total", 0)
    accuracy = report.get("accuracy_pct", 0.0)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="270" height="28" role="img" '
        f'aria-label="sipi.bot SSFB: {passed} of {total} scenarios pass ({accuracy}%)">'
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#121316"/>'
        '<stop offset="100%" stop-color="#0a0a0a"/>'
        '</linearGradient>'
        '<rect width="270" height="28" rx="6" fill="url(#bg)"/>'
        '<rect x="0" width="110" height="28" rx="6" fill="#00d4aa" fill-opacity="0.14"/>'
        f'<text x="9" y="19" fill="#00d4aa" '
        f'font-family="SF Mono,ui-monospace,monospace" font-size="11" '
        f'font-weight="700">SSFB · {passed}/{total}</text>'
        f'<text x="190" y="19" fill="#e8e8ea" font-family="-apple-system,sans-serif" '
        f'font-size="11" text-anchor="middle">{accuracy}% accuracy</text>'
        '</svg>'
    )
