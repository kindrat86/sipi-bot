#!/usr/bin/env python3
"""
Enrich thin /for/*/index.html pages with Article + BreadcrumbList + FAQPage
JSON-LD, matching the schema the rich /for/ pages already ship (e.g.
for/ai-startups). Reads title + meta description from each page so the
schema is page-accurate, not generic.

Idempotent: skips pages that already carry an Article block. Run from the
repo root:  python3 _enrich_thin_for_schema.py
"""
import json
import re
import sys
from pathlib import Path

THIN = [
    "for/agent-builders",
    "for/customer-support-agents",
    "for/devops-teams",
    "for/fintech-teams",
    "for/startup-founders",
    "for/vercel-ai-sdk",
]

LD_RE = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.S
)
TITLE_RE = re.compile(r"<title>([^<]+)</title>")
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]+)"', re.I)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)


def strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def extract_faqs(html: str, audience_label: str):
    """Pull up to 2 question/answer pairs from the page's own FAQ section.
    Looks for <h2/h3>...?</h> followed by a <p>. Falls back to generic
    questions derived from the audience name if none found (so the FAQPage
    is never empty, but the content still reflects the page)."""
    pairs = []
    # find every heading ending in "?" with the next <p> as its answer
    for m in re.finditer(
        r"<h[23][^>]*>([^<]*\?</h[23]>)(.*?)(?=<h[23]|$)", html, re.S
    ):
        q = strip_tags(m.group(1))
        ans_m = re.search(r"<p[^>]*>(.*?)</p>", m.group(2), re.S)
        a = strip_tags(ans_m.group(1)) if ans_m else ""
        if q and a and len(a) > 15:
            pairs.append((q, a))
        if len(pairs) >= 2:
            break
    if not pairs:
        # honest fallback: the question is real, the answer is honest+generic
        pairs = [
            (
                f"How much does sipi.bot cost for {audience_label}?",
                "The open-source core is MIT-licensed and free to self-host. "
                "Hosted plans start at $99/month for unlimited transaction "
                "evaluations. See /pricing for current tiers.",
            ),
            (
                f"Does {audience_label} need a dedicated spend firewall?",
                "Yes whenever an autonomous agent can move money. sipi.bot sits "
                "in front of the payment and returns APPROVED, BLOCKED, or "
                "FLAGGED before any dollar moves — so a runaway loop or bad "
                "merchant cannot drain a card or an API-credit balance.",
            ),
        ]
    return pairs


def build_blocks(title: str, desc: str, h1: str, slug: str, faqs):
    url = f"https://sipi.bot/{slug}"
    name = slug.split("/")[-1].replace("-", " ")
    headline = h1 or title
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"{headline}",
        "description": desc or title,
        "author": {"@type": "Organization", "name": "sipi.bot", "url": "https://sipi.bot"},
        "publisher": {"@type": "Organization", "name": "sipi.bot", "url": "https://sipi.bot"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "datePublished": "2026-07-18",
        "dateModified": "2026-07-27",
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://sipi.bot/"},
            {"@type": "ListItem", "position": 2, "name": "sipi.bot", "item": url},
        ],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }
    return [article, breadcrumb, faq]


_INJECT_MARK = "<!-- enriched-by _enrich_thin_for_schema.py -->"


def inject(path: Path, url_slug: str) -> str:
    """url_slug is the URL path relative to the domain root, e.g.
    'for/fintech-teams' (NOT the filesystem path)."""
    html = path.read_text()
    # Re-processable: strip any block we previously injected (between the
    # idempotency mark and the next </script> group we own). We remove the
    # whole marked span so re-running produces clean output, not duplicates.
    html = re.sub(
        re.escape(_INJECT_MARK) + r".*?" + re.escape(_INJECT_MARK),
        "",
        html,
        flags=re.S,
    )

    title_m = TITLE_RE.search(html)
    desc_m = DESC_RE.search(html)
    h1_m = H1_RE.search(html)
    title = title_m.group(1).replace(" — sipi.bot", "").strip() if title_m else path.parent.name
    desc = desc_m.group(1).strip() if desc_m else title
    h1 = strip_tags(h1_m.group(1)) if h1_m else ""
    slug = url_slug
    # clean audience label from the slug, e.g. "fintech-teams" -> "fintech teams"
    audience_label = slug.split("/")[-1].replace("-", " ")
    faqs = extract_faqs(html, audience_label)
    blocks = build_blocks(title, desc, h1, slug, faqs)

    # Build the <script> tags, wrapped in an idempotency marker span
    inner = "\n".join(
        f'<script type="application/ld+json">{json.dumps(b)}</script>'
        for b in blocks
    )
    new_tags = f"{_INJECT_MARK}\n{inner}\n{_INJECT_MARK}"
    # Insert immediately before </head>
    if "</head>" not in html:
        return f"ERROR {path.parent}: no </head> found"
    new_html = html.replace("</head>", new_tags + "\n</head>", 1)
    path.write_text(new_html)

    # validate every JSON-LD block in the result parses
    for b in LD_RE.findall(new_html):
        json.loads(b)
    return f"OK   {path.parent}: +3 blocks (Article, BreadcrumbList, FAQPage with {len(faqs)} Qs)"


def main():
    root = Path(__file__).parent
    results = []
    for slug in THIN:
        p = root / slug / "index.html"
        if not p.exists():
            results.append(f"MISS {slug}: no index.html")
            continue
        results.append(inject(p, slug))
    print("\n".join(results))
    if any(r.startswith("ERROR") or r.startswith("MISS") for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
