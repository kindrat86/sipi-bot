"""Focused tests for the /ai-cost-management answer-first authority guide.

Contract:
- public/ai-cost-management/index.html exists, slash-canonical, indexable
- answer-first: a direct-answer block appears before the first H2
- homepage (templates.landing_page_html) carries exactly one contextual link
- sitemap lists the page
- JSON-LD: Article + BreadcrumbList + FAQPage, valid JSON
- honesty: no em dashes, no invented pricing, no unverified outcome claims
- privacy: no private names, account IDs, secret paths, home-dir paths
"""
import json
import re
import unittest
from pathlib import Path

from spendfirewall import templates

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "ai-cost-management" / "index.html"
SITEMAP = ROOT / "public" / "sitemap.xml"
CANONICAL = "https://sipi.bot/ai-cost-management/"

REQUIRED_SECTION_IDS = [
    "answer",
    "measure",
    "attribute",
    "budgets",
    "routing",
    "retries",
    "caching",
    "token-controls",
    "observability",
    "anomaly-detection",
    "quality-gates",
    "sequence",
]

OFFICIAL_SOURCE_DOMAINS = [
    "developers.openai.com/api/docs/guides/prompt-caching",
    "developers.openai.com/api/docs/guides/batch",
    "platform.claude.com/docs/en/build-with-claude/prompt-caching",
    "platform.claude.com/docs/en/build-with-claude/batch-processing",
    "ai.google.dev/gemini-api/docs/pricing",
    "docs.cloud.google.com/billing/docs/how-to/budgets",
]

INTERNAL_LINKS_THAT_MUST_EXIST = [
    "/guides/guide-to-agent-spend-audits",
    "/how-to/how-to-monitor-ai-costs",
    "/best/ai-cost-management-tools",
    "/blog/why-your-ai-bill-keeps-growing",
    "/guides/guide-to-agent-budgeting-by-use-case",
]

# Routes rendered dynamically by spendfirewall/api.py (no file on disk)
DYNAMIC_ROUTES = {"/pricing", "/pilot", "/playground/", "/tools/"}


def _page() -> str:
    if not PAGE.is_file():
        raise AssertionError(
            f"missing guide page: {PAGE} (expected answer-first authority guide)"
        )
    return PAGE.read_text(encoding="utf-8")


class GuidePageTests(unittest.TestCase):
    def test_page_exists_with_slash_canonical_and_index_robots(self):
        html = _page()
        self.assertIn(f'<link rel="canonical" href="{CANONICAL}">', html)
        self.assertIn(f'<meta property="og:url" content="{CANONICAL}">', html)
        self.assertIn("index, follow", html)
        self.assertIn("AI cost management", html.split("<title>")[1].split("</title>")[0])
        self.assertIn('<meta name="description"', html)

    def test_answer_block_precedes_first_h2_and_names_the_levers(self):
        html = _page()
        body = html[html.index("<body") :]
        answer_pos = body.index('id="answer"')
        first_h2 = body.index("<h2")
        self.assertLess(answer_pos, first_h2)
        answer_text = re.sub(r"<[^>]+>", " ", body[answer_pos : answer_pos + 2500])
        lowered = answer_text.lower()
        for lever in ("measure", "attribut", "budget", "rout", "cach", "retr"):
            self.assertIn(lever, lowered, f"answer block must name lever: {lever}")

    def test_all_required_topic_sections_present(self):
        html = _page()
        for sid in REQUIRED_SECTION_IDS:
            self.assertIn(f'id="{sid}"', html, f"missing section id={sid}")


class GuideSchemaTests(unittest.TestCase):
    def test_article_breadcrumb_faq_jsonld_valid_and_consistent(self):
        html = _page()
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S
        )
        parsed = [json.loads(b) for b in blocks]
        types = {b.get("@type") for b in parsed}
        self.assertLessEqual(
            {"Article", "BreadcrumbList", "FAQPage"}, types, f"got types: {types}"
        )
        for b in parsed:
            if b.get("@type") == "Article":
                self.assertIn("AI cost management", b["headline"])
                self.assertEqual(b["url"], CANONICAL)
                self.assertRegex(b["datePublished"], r"^\d{4}-\d{2}-\d{2}$")
            if b.get("@type") == "BreadcrumbList":
                last = b["itemListElement"][-1]
                self.assertEqual(last["item"], CANONICAL)
            if b.get("@type") == "FAQPage":
                self.assertGreaterEqual(len(b["mainEntity"]), 3)


class GuideContentTests(unittest.TestCase):
    def test_official_provider_sources_linked(self):
        html = _page()
        for src in OFFICIAL_SOURCE_DOMAINS:
            self.assertIn(src, html, f"missing official source link: {src}")

    def test_date_sensitive_facts_labeled(self):
        html = _page()
        self.assertGreaterEqual(
            html.count("as of August 2026"), 2,
            "date-sensitive provider facts must carry an as-of label",
        )

    def test_internal_links_resolve_to_real_targets(self):
        html = _page()
        for href in INTERNAL_LINKS_THAT_MUST_EXIST:
            self.assertIn(f'href="{href}"', html)
        for href in INTERNAL_LINKS_THAT_MUST_EXIST:
            target = ROOT / href.lstrip("/") / "index.html"
            self.assertTrue(
                target.is_file() or href in DYNAMIC_ROUTES or (ROOT / href.lstrip("/")).is_dir(),
                f"internal link target missing on disk: {href}",
            )


class HomepageLinkTests(unittest.TestCase):
    def test_homepage_has_exactly_one_contextual_guide_link(self):
        html = templates.landing_page_html()
        self.assertEqual(html.count('href="/ai-cost-management/"'), 1)
        self.assertIn("AI cost management guide", html)


class SitemapTests(unittest.TestCase):
    def test_sitemap_lists_guide(self):
        xml = SITEMAP.read_text(encoding="utf-8")
        self.assertIn(f"<loc>{CANONICAL}</loc>", xml)


class HonestyTests(unittest.TestCase):
    def test_no_em_dashes_in_guide(self):
        self.assertNotIn("\u2014", _page())

    def test_no_invented_pricing_or_dollar_figures(self):
        self.assertIsNone(re.search(r"\$\s?\d", _page()))

    def test_no_unverified_outcome_or_universal_claims(self):
        banned = [
            "guaranteed savings",
            "average savings",
            "customers save",
            "cut your AI bill by",
            "typical reduction",
            "will always",
            "eliminates all",
        ]
        lowered = _page().lower()
        for phrase in banned:
            self.assertNotIn(phrase, lowered)

    def test_offer_positioning_preserved_no_agentshield(self):
        html = _page()
        self.assertIn("pre-spend firewall", html)
        self.assertIn('href="/pilot"', html)
        self.assertIn("paid implementation pilot", html)
        self.assertNotIn("AgentShield", html)


class PrivacyGuardTests(unittest.TestCase):
    """Regression guard: no private data may enter public source/output."""

    SECRET_PATTERNS = [
        r"\bsk-[A-Za-z0-9_-]{16,}",
        r"AKIA[0-9A-Z]{16}",
        r"ghp_[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{10,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    ]

    PATH_PATTERNS = [
        "/Users/",
        "~/.hermes",
        ".hermes/",
        "/Volumes/",
        # Escaped dot: an unescaped ".env" matched the space+"env" inside the
        # word "environment" in harmless public prose (attribution section).
        # We want the literal dotenv filename, not any occurrence of "env".
        r"\.env",
        "private/",
    ]

    def test_guide_has_no_secrets_or_private_paths(self):
        html = _page()
        for pat in self.SECRET_PATTERNS + self.PATH_PATTERNS:
            self.assertIsNone(
                re.search(pat, html), f"privacy guard tripped on pattern: {pat}"
            )

    def test_guide_has_no_non_public_emails(self):
        for mail in re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", _page()):
            self.assertRegex(
                mail, r"@(sipi\.bot|sipiteno\.com)$",
                f"non-public email in guide: {mail}",
            )

    def test_homepage_addition_has_no_secrets_or_private_paths(self):
        html = templates.landing_page_html()
        for pat in self.SECRET_PATTERNS:
            self.assertIsNone(re.search(pat, html))
