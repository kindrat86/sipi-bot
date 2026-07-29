"""Shared template primitives for sipi.bot content surfaces.

One design system, one SEO head builder, one chrome (nav + footer + analytics).
Adapted from voicelogpro-distribution/lib/common.py, rebranded in sipi.bot's
signature dark palette (#00d4aa accent on #0a0a0a) that build_pseo.py and the
homepage already use. Replaces the per-script inline CSS in scripts/build_*.py.

All new surfaces (incidents/, blog/, tools/, changelog/, status/) render through
this module so the site reads as one product, not a fleet of unrelated pages.
"""
from __future__ import annotations
import html
import json
import os
from datetime import date

# ---------------------------------------------------------------------- identity
APP = "https://sipi.bot"
GITHUB = "https://github.com/kindrat86/sipi-bot"
BRAND = "sipi.bot"
BRAND_HTML = 'sipi<span class="dot-org">.bot</span>'
PUBLISHER = "sipi.bot"           # schema.org publisher / author
POSTHOG_KEY = "phc_lyZCgvTpicjLzAO3rY2GhxuX5WUc5jQjP8ZVwwJqauX"
POSTHOG_HOST = "https://eu.i.posthog.com"
OG_IMAGE = "/og-default.png"     # site-wide social card; override per page if needed

# BASE = where THIS site is hosted. Canonical + og:url MUST point here.
BASE = os.environ.get("SIPI_BASE_URL", "https://sipi.bot").rstrip("/")
SITE = BASE

NAV = [
    ("Incidents", "/incidents/"),
    ("Tools", "/tools/"),
    ("Blog", "/blog/"),
    ("Integrations", "/for/"),
    ("Pricing", APP + "/pricing"),
    ("Dashboard", APP + "/dashboard"),
]

FOOTER_SECTIONS = [
    ("Product", [
        ("Home", "/"),
        ("Pricing", "/pricing"),
        ("Dashboard", "/dashboard"),
        ("Playground", "/playground/"),
        ("Status", "/status/"),
        ("Changelog", "/changelog/"),
    ]),
    ("For builders", [
        ("Integrations", "/for/"),
        ("Comparisons", "/vs/"),
        ("Best-of lists", "/best/"),
        ("Open source", GITHUB),
        ("Self-host guide", "/self-hosted/"),
    ]),
    ("Data & research", [
        ("Incident database", "/incidents/"),
        ("Loss statistics", "/incidents/stats/"),
        ("Benchmarks", "/benchmarks/"),
        ("Glossary", "/glossary/"),
        ("FAQ", "/faq/"),
    ]),
    ("Free tools", [
        ("Risk calculator", "/tools/agent-spend-risk-calculator/"),
        ("Policy generator", "/tools/spend-policy-generator/"),
        ("Cost audit checklist", "/checklists/agent-cost-audit/"),
        ("Protected-by badge", "/badge"),
    ]),
    ("Network", [
        ("GitDealFlow", "https://gitdealflow.com"),
        ("VC Deal Flow Signal", "https://signals.gitdealflow.com"),
        ("ChurnLens", "https://churnlens.site"),
        ("SanctionsAI", "https://sanctionsai.dev"),
        ("UnlockSaaS", "https://unlocksaas.com"),
        ("InvisibleExit", "https://invisibleexit.com"),
    ]),
]

# ----------------------------------------------------------------------- design
CSS = """
:root{
  --bg:#0a0a0a; --bg-1:#121316; --bg-2:#181a1f; --bg-3:#1e2128;
  --line:#23242a; --line-2:#303239;
  --fg:#e8e8ea; --fg-2:#c9ccd3; --fg-3:#8a8d96;
  --mint:#00d4aa; --mint-2:#34e8c0; --mint-ink:#04120e;
  --mint-soft:rgba(0,212,170,.10); --mint-line:rgba(0,212,170,.34);
  --red:#ff5c5c; --red-soft:rgba(255,92,92,.10); --red-line:rgba(255,92,92,.32);
  --amber:#f5a524; --amber-soft:rgba(245,165,36,.10); --amber-line:rgba(245,165,36,.36);
  --blue:#3b82f6; --blue-soft:rgba(59,130,246,.10);
  --r-s:8px; --r:12px; --r-l:16px;
  --nav-h:58px; --shell:1080px;
  --ease:cubic-bezier(.4,0,.2,1);
  color-scheme:dark;
}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:80px}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,system-ui,sans-serif;
  background:var(--bg);color:var(--fg);
  font-size:1.0625rem;line-height:1.65;
  overflow-x:hidden;min-height:100dvh;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
  padding-bottom:64px;
}
::selection{background:var(--mint);color:var(--mint-ink)}
a{color:var(--mint);text-decoration:none}
a:hover{text-decoration:underline}
strong{color:var(--fg);font-weight:650}
.wrap{max-width:var(--shell);margin:0 auto;padding:0 22px}
code{font-family:ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace;font-size:.9em;
  background:var(--bg-2);padding:.12em .4em;border-radius:6px;color:var(--mint-2)}
pre{background:#000;border:1px solid var(--line);border-radius:var(--r);padding:18px;
  overflow-x:auto;font-size:13.5px;line-height:1.55;color:#cfd2d8;margin:16px 0;
  font-family:ui-monospace,'SF Mono',SFMono-Regular,Menlo,monospace}
pre code{background:none;padding:0;color:inherit}
/* nav */
.nav{position:sticky;top:0;z-index:50;height:var(--nav-h);display:flex;align-items:center;
  background:rgba(10,10,10,.88);backdrop-filter:saturate(180%) blur(12px);
  border-bottom:1px solid var(--line)}
.nav .brand{display:flex;align-items:center;gap:7px;font-weight:800;letter-spacing:-.02em;
  color:var(--fg);font-size:1.08rem}
.nav .brand .dot-org{color:var(--mint)}
.nav .links{margin-left:auto;display:flex;gap:20px;font-size:.9rem;color:var(--fg-2);align-items:center}
.nav .links a{color:var(--fg-2)}
.nav .links a:hover{color:var(--fg);text-decoration:none}
.nav .links .cta{background:var(--mint);color:var(--mint-ink)!important;
  padding:8px 15px;border-radius:999px;font-weight:700}
.nav .links .cta:hover{background:var(--mint-2);text-decoration:none}
@media(max-width:880px){.nav .links a:not(.cta){display:none}.nav .links{gap:0}}
/* hero */
.hero{padding:54px 0 22px}
.crumbs{font-size:.83rem;color:var(--fg-3);margin-bottom:18px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.crumbs a{color:var(--fg-3)}.crumbs a:hover{color:var(--mint)}
.crumbs .sep{opacity:.45}
h1{font-size:clamp(1.75rem,4.3vw,2.85rem);line-height:1.08;letter-spacing:-.03em;font-weight:800;margin-bottom:14px}
.lead{color:var(--fg-2);font-size:1.16rem;max-width:64ch;line-height:1.6}
h2{font-size:clamp(1.3rem,2.6vw,1.7rem);letter-spacing:-.02em;font-weight:750;margin:44px 0 14px}
h3{font-size:1.14rem;font-weight:650;letter-spacing:-.01em;margin:28px 0 10px;color:var(--fg)}
h4{font-size:1rem;font-weight:650;margin:22px 0 8px;color:var(--fg)}
p{margin:0 0 14px;color:var(--fg-2)}
ul,ol{margin:0 0 16px;padding-left:1.35em}
li{margin:0 0 8px;color:var(--fg-2)}
li strong, p strong{color:var(--fg)}
/* grid */
.grid{display:grid;gap:14px;margin:18px 0 8px}
.grid.two{grid-template-columns:repeat(2,minmax(0,1fr))}
.grid.three{grid-template-columns:repeat(3,minmax(0,1fr))}
.grid.four{grid-template-columns:repeat(4,minmax(0,1fr))}
@media(max-width:980px){.grid.four{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:760px){.grid.two,.grid.three,.grid.four{grid-template-columns:1fr}}
.card{background:var(--bg-1);border:1px solid var(--line);border-radius:var(--r);
  padding:20px 20px 18px;transition:.18s var(--ease)}
.card:hover{border-color:var(--mint-line);transform:translateY(-1px)}
.card h3{margin-top:0}.card h3 a{color:var(--fg)}
.card h3 a:hover{color:var(--mint);text-decoration:none}
.card p{font-size:.96rem;color:var(--fg-3);margin:6px 0 0}
.card .meta{font-size:.82rem;color:var(--fg-3);margin-top:10px;display:flex;gap:10px;flex-wrap:wrap}
/* tags */
.tag{display:inline-flex;align-items:center;gap:6px;padding:4px 11px;border-radius:999px;
  font-size:.74rem;font-weight:700;letter-spacing:.03em;text-transform:uppercase}
.tag.good{background:var(--mint-soft);color:var(--mint);border:1px solid var(--mint-line)}
.tag.warn{background:var(--amber-soft);color:var(--amber);border:1px solid var(--amber-line)}
.tag.bad{background:var(--red-soft);color:var(--red);border:1px solid var(--red-line)}
.tag.navy{background:var(--blue-soft);color:#60a5fa;border:1px solid rgba(59,130,246,.32)}
.tag.neutral{background:var(--bg-2);color:var(--fg-3);border:1px solid var(--line)}
/* callout */
.callout{background:var(--mint-soft);border:1px solid var(--mint-line);border-left:3px solid var(--mint);
  border-radius:var(--r);padding:16px 18px;margin:24px 0}
.callout .k{font-size:.74rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;
  color:var(--mint-2);margin-bottom:6px}
.callout p{margin:0;color:var(--fg)}
.callout.warn{background:var(--amber-soft);border-color:var(--amber-line);border-left-color:var(--amber)}
.callout.warn .k{color:var(--amber)}
/* stat box */
.statbox{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0}
@media(max-width:760px){.statbox{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--bg-1);border:1px solid var(--line);border-radius:var(--r);padding:18px}
.stat .n{font-size:1.85rem;font-weight:800;letter-spacing:-.025em;color:var(--mint);line-height:1}
.stat .l{font-size:.82rem;color:var(--fg-3);margin-top:8px}
/* faq */
.faq{margin:8px 0}
.faq details{background:var(--bg-1);border:1px solid var(--line);border-radius:var(--r);margin:0 0 10px;overflow:hidden}
.faq summary{cursor:pointer;padding:16px 18px;font-weight:650;color:var(--fg);list-style:none;
  display:flex;justify-content:space-between;align-items:center;gap:12px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:'+';color:var(--mint);font-weight:800;font-size:1.2rem;transition:.2s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq .a{padding:0 18px 16px;color:var(--fg-2)}
/* tables */
table{width:100%;border-collapse:collapse;margin:14px 0;font-size:.95rem}
th,td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--fg-3);font-weight:600;font-size:.8rem;text-transform:uppercase;letter-spacing:.04em}
td a{color:var(--fg)}td a:hover{color:var(--mint)}
tr:hover td{background:rgba(255,255,255,.015)}
.num{font-variant-numeric:tabular-nums;text-align:right}
/* CTA band */
.band{margin:50px 0 10px;background:linear-gradient(135deg,var(--bg-1),var(--bg-2));
  border:1px solid var(--line);border-radius:var(--r-l);padding:34px;position:relative;overflow:hidden}
.band::after{content:'';position:absolute;right:-80px;top:-80px;width:280px;height:280px;border-radius:50%;
  background:radial-gradient(circle,var(--mint-soft),transparent 70%)}
.band h2{margin-top:0}.band p{color:var(--fg-2);max-width:60ch}
.band .btns{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px;position:relative}
.btn{display:inline-flex;align-items:center;gap:8px;padding:13px 22px;border-radius:999px;
  font-weight:700;font-size:1rem;transition:.18s var(--ease)}
.btn.primary{background:var(--mint);color:var(--mint-ink)}
.btn.primary:hover{background:var(--mint-2);text-decoration:none}
.btn.ghost{background:transparent;color:var(--fg);border:1px solid var(--line-2)}
.btn.ghost:hover{border-color:var(--mint-line);text-decoration:none}
/* article prose */
.prose{max-width:70ch}.prose p,.prose li{color:var(--fg-2)}.prose strong{color:var(--fg)}
.prose h2{margin-top:40px}
.byline{display:flex;align-items:center;gap:10px;color:var(--fg-3);font-size:.9rem;margin-bottom:8px}
.byline .av{width:30px;height:30px;border-radius:50%;background:var(--mint);color:var(--mint-ink);
  display:grid;place-items:center;font-weight:800;font-size:.85rem}
/* footer */
.foot{border-top:1px solid var(--line);margin-top:60px;padding:36px 0 0}
.foot .cols{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr;gap:26px}
@media(max-width:880px){.foot .cols{grid-template-columns:1fr 1fr}}
.foot h4{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;color:var(--fg-3);margin:0 0 12px}
.foot ul{list-style:none;padding:0;margin:0}.foot li{margin:0 0 8px}
.foot a{color:var(--fg-2);font-size:.9rem}.foot a:hover{color:var(--mint)}
.foot .blurb{color:var(--fg-3);font-size:.88rem;margin-top:14px;max-width:42ch}
.foot .legal{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);
  color:var(--fg-3);font-size:.82rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}
/* misc */
.kicker{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:var(--mint-2);margin-bottom:10px}
.muted{color:var(--fg-3)}
.spacer{height:18px}
.divider{height:1px;background:var(--line);margin:32px 0}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}
"""


# ----------------------------------------------------------------- json-ld help
def _esc(s) -> str:
    return html.escape(str(s), quote=True)


def website_ld():
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": BRAND,
        "url": SITE + "/",
        "description": "The pre-spend firewall for autonomous AI agents — approve, block, or flag "
                       "every transaction before a dollar moves.",
        "publisher": {"@type": "Organization", "name": BRAND, "url": SITE + "/"},
    }


def breadcrumb_ld(crumbs):
    """crumbs = [(name, path), ...] ending at the current page."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "name": _esc(name), "item": SITE + path}
            for i, (name, path) in enumerate(crumbs)
        ],
    }


def faq_ld(qa):
    """qa = [(question, answer), ...]"""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": _esc(q),
             "acceptedAnswer": {"@type": "Answer", "text": _esc(a)}}
            for q, a in qa
        ],
    }


def article_ld(*, title, description, canonical_path, date_published,
               date_modified=None, author=PUBLISHER, image_path=None):
    dp = date_published if isinstance(date_published, str) else date_published.isoformat()
    dm = (date_modified or date_published)
    dm = dm if isinstance(dm, str) else dm.isoformat()
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": _esc(title),
        "description": _esc(description),
        "url": SITE + canonical_path,
        "image": SITE + (image_path or OG_IMAGE),
        "datePublished": dp,
        "dateModified": dm,
        "author": {"@type": "Organization", "name": author},
        "publisher": {"@type": "Organization", "name": PUBLISHER, "url": SITE + "/"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + canonical_path},
    }


def dataset_ld(*, name, description, canonical_path, license_url,
               keywords=None, record_count=None, data_download=None):
    d = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": _esc(name),
        "description": _esc(description),
        "url": SITE + canonical_path,
        "creator": {"@type": "Organization", "name": PUBLISHER, "url": SITE + "/"},
        "license": license_url,
        "isAccessibleForFree": True,
        "keywords": keywords or [],
    }
    if record_count is not None:
        d["variableMeasured"] = f"{record_count} documented incidents"
    if data_download:
        d["distribution"] = [
            {"@type": "DataDownload", "contentUrl": SITE + url, "encodingFormat": fmt, "name": name}
            for url, fmt, name in data_download
        ]
    return d


def software_app_ld(*, name, description, canonical_path, application_category,
                    operating_system="Web", offers_price="$99", offers_currency="USD"):
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": _esc(name),
        "description": _esc(description),
        "url": SITE + canonical_path,
        "applicationCategory": application_category,
        "operatingSystem": operating_system,
        "offers": {
            "@type": "Offer",
            "price": offers_price.replace("$", "").replace(",", ""),
            "priceCurrency": offers_currency,
        },
        "publisher": {"@type": "Organization", "name": PUBLISHER, "url": SITE + "/"},
    }


def howto_ld(*, name, description, steps):
    """steps = [str, ...] plain-text step descriptions."""
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": _esc(name),
        "description": _esc(description),
        "step": [
            {"@type": "HowToStep", "position": i + 1, "text": _esc(s)}
            for i, s in enumerate(steps)
        ],
    }


# ------------------------------------------------------------------- chrome fns
def _posthog_snippet() -> str:
    return (
        '<script>(function(){if(window.posthog&&window.posthog.__loaded)return;'
        'var s=document.createElement("script");s.type="text/javascript";'
        's.crossOrigin="anonymous";s.defer=true;'
        f's.src="{POSTHOG_HOST}/static/array.js";'
        's.onload=function(){window.posthog.init("' + POSTHOG_KEY + '",{api_host:"' +
        POSTHOG_HOST + '",person_profiles:"identified_only",defaults:"2025-05-24",'
        'capture_pageview:false});'
        'window.posthog.capture("$pageview",{$viewport_height:window.innerHeight,'
        '$viewport_width:window.innerWidth})};document.head.appendChild(s);})();</script>'
    )


def _block_to_str(b) -> str:
    """Serialize one JSON-LD block: accept a dict (from the *_ld helpers) or a
    pre-serialized string. Dicts must be json.dumps'd — str(dict) emits single
    quotes (Python repr), which is NOT valid JSON and trips validate_jsonld."""
    if isinstance(b, str):
        return b
    return json.dumps(b, ensure_ascii=False)


def head(*, title, description, canonical_path, og_image_path=None,
         jsonld=None, extra_robots=None) -> str:
    """Render <head> with full SEO/OG/Twitter tags + JSON-LD blocks + PostHog.

    Each item in jsonld may be a dict (preferred — pass helper output directly)
    or a pre-serialized JSON string.
    """
    canonical = SITE + canonical_path
    og_image = SITE + (og_image_path or OG_IMAGE)
    blocks = "".join(
        f'\n<script type="application/ld+json">{_block_to_str(b)}</script>'
        for b in (jsonld or [])
    )
    robots = extra_robots or "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
    gsc = os.environ.get("GSC_VERIFICATION", "").strip()
    gsc_tag = (f'\n<meta name="google-site-verification" content="{_esc(gsc)}">' if gsc else "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{_esc(title)}</title>
<meta name="description" content="{_esc(description)}">
<link rel="canonical" href="{canonical}">{gsc_tag}
<meta name="theme-color" content="#0a0a0a">
<meta name="robots" content="{robots}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{_esc(title)}">
<meta property="og:description" content="{_esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{_esc(title)}">
<meta name="twitter:description" content="{_esc(description)}">
<meta name="twitter:image" content="{og_image}">
<link rel="icon" type="image/svg+xml" href="{SITE}/favicon.svg">
<link rel="alternate" type="application/rss+xml" title="{BRAND} — incidents & research" href="/rss.xml">{blocks}
{_posthog_snippet()}
<style>{CSS}</style>
</head>
<body>"""


def nav_html(active: str | None = None) -> str:
    items = []
    for label, href in NAV:
        if href.startswith("http"):
            items.append(f'<a class="cta" href="{href}">{_esc(label)}</a>')
            continue
        cls = ' style="color:var(--fg)"' if active and label.lower() == active.lower() else ""
        items.append(f'<a href="{href}"{cls}>{_esc(label)}</a>')
    return f"""<header class="nav"><div class="wrap" style="display:flex;align-items:center;width:100%">
<a class="brand" href="/">{BRAND_HTML}</a>
<nav class="links">{"".join(items)}</nav></div></header>"""


def footer_html() -> str:
    cols = ""
    for title, links in FOOTER_SECTIONS:
        lis = "".join(
            f'<li><a href="{href}">{_esc(name)}</a></li>' for name, href in links
        )
        cols += f'<div><h4>{title}</h4><ul>{lis}</ul></div>'
    return f"""<footer class="foot"><div class="wrap">
<div class="cols">
<div>
<h4>{BRAND}</h4>
<p class="blurb">The pre-spend firewall for autonomous AI agents. One call before an agent spends
returns APPROVED, BLOCKED, or FLAGGED against your rules. Open-source core, MIT self-host.</p>
<a class="btn primary" style="margin-top:14px" href="/pricing">Start — $99/mo</a>
</div>
{cols}
</div>
<div class="legal"><span>© {date.today().year} {BRAND}. Open-source core under MIT.</span>
<span>Incident data is documented from public sources and licensed CC BY 4.0.</span></div>
<div class="network" style="margin-top:1.5rem;padding-top:1rem;border-top:1px solid var(--line-2);font-size:.75rem;color:var(--fg-3);text-align:center"><span>Portfolio: </span><a href="https://gitdealflow.com" style="color:var(--fg-3);text-decoration:none">GitDealFlow</a> · <a href="https://signals.gitdealflow.com" style="color:var(--fg-3);text-decoration:none">Signals</a> · <a href="https://churnlens.site" style="color:var(--fg-3);text-decoration:none">ChurnLens</a> · <a href="https://carshake.online" style="color:var(--fg-3);text-decoration:none">CarShake</a> · <a href="https://unlocksaas.com" style="color:var(--fg-3);text-decoration:none">UnlockSaaS</a> · <a href="https://sanctionsai.dev" style="color:var(--fg-3);text-decoration:none">SanctionsAI</a> · <a href="https://voicelogpro.com" style="color:var(--fg-3);text-decoration:none">VoiceLogPro</a> · <a href="https://invisibleexit.com" style="color:var(--fg-3);text-decoration:none">InvisibleExit</a> · <a href="https://sipiteno.com" style="color:var(--fg-3);text-decoration:none">Sipiteno</a></div>
</div></footer>"""


def page(*, title, description, canonical_path, active=None, body="",
         jsonld=None, og_image_path=None) -> str:
    """Assemble a full HTML document from head + nav + body + footer."""
    # Always include the WebSite + org block unless caller passed their own.
    blocks = list(jsonld or [])
    has_website = any(
        isinstance(b, dict) and b.get("@type") in ("WebSite",) for b in blocks
    )
    if not has_website:
        blocks.insert(0, website_ld())
    return "\n".join([
        head(title=title, description=description, canonical_path=canonical_path,
             og_image_path=og_image_path, jsonld=blocks),
        nav_html(active),
        f'<main class="wrap">{body}</main>',
        footer_html(),
        "</body></html>",
    ])


def write(path: str, content: str):
    """Write a file, creating parent dirs. Idempotent across runs."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
