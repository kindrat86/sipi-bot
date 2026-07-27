"""Tests for the 2026-07-27 SEO audit fixes.

Covers:
  - trailing-slash normalization for bare app routes (/eval/ -> 301 -> /eval)
  - pSEO directory URLs are NOT redirected (/for/crewai/ stays 200)
  - /sitemap-html renders with links + canonical + JSON-LD
  - footer carries a Sitemap link
  - Organization schema has the logo @id node + >=5 sameAs entries
  - _inject_related_links is idempotent and adds sibling + hub links
  - the homepage hero no longer links the dead /benchmark/ URL
"""
import json
import os
import re
import unittest
from io import BytesIO

# Stub gzip compression off so response bodies are plain bytes we can read.
os.environ.setdefault("HTTP_COMPRESSION", "false")

from spendfirewall import api, templates  # noqa: E402


def _get(path, host="sipi.bot", extra_headers=None):
    """Spin up a Handler against an in-memory socket and capture the response."""
    raw = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept-Encoding: identity\r\n"
    if extra_headers:
        for k, v in extra_headers.items():
            raw += f"{k}: {v}\r\n"
    raw += "Connection: close\r\n\r\n"

    class _Conn:
        def __init__(self, data):
            self.r = BytesIO(data)
            self.w = BytesIO()
        def makefile(self, *a, **k):
            return self.r if "rb" in (a[0] if a else k.get("mode", "rb")) else self.w
        def sendall(self, b):
            self.w.write(b)
        def close(self):
            pass

    conn = _Conn(raw.encode())
    # path_url must match what BaseHTTPRequestHandler parses from the request line
    handler = api.Handler(conn, ("127.0.0.1", 0), "test", )
    out = conn.w.getvalue().decode("utf-8", "replace")
    status = int(out.split(" ", 2)[1])
    headers, _, body = out.partition("\r\n\r\n")
    return status, headers, body


class TrailingSlashNormalizationTests(unittest.TestCase):
    def test_eval_with_slash_redirects_to_bare(self):
        status, headers, _ = _get("/eval/")
        self.assertEqual(status, 301)
        self.assertIn("Location: /eval", headers)

    def test_badge_with_slash_redirects_to_bare(self):
        status, headers, _ = _get("/badge/")
        self.assertEqual(status, 301)
        self.assertIn("Location: /badge", headers)

    def test_pricing_with_slash_redirects_to_bare(self):
        status, headers, _ = _get("/pricing/")
        self.assertEqual(status, 301)
        self.assertIn("Location: /pricing", headers)

    def test_pseo_directory_url_is_not_redirected(self):
        # pSEO spokes use directory URLs and must keep serving 200 with the slash.
        status, _, _ = _get("/vs/litellm/")
        self.assertEqual(status, 200)

    def test_redirect_preserves_query_string(self):
        status, headers, _ = _get("/eval/?foo=bar")
        self.assertEqual(status, 301)
        self.assertIn("Location: /eval?foo=bar", headers)

    def test_redirect_carries_security_headers(self):
        # HSTS and friends must survive the hop (the existing redirect-blocker bug).
        status, headers, _ = _get("/eval/")
        self.assertIn("Strict-Transport-Security", headers)
        self.assertIn("X-Frame-Options: DENY", headers)

    def test_bare_route_still_serves_200(self):
        status, _, _ = _get("/eval")
        self.assertEqual(status, 200)


class SitemapPageTests(unittest.TestCase):
    def test_sitemap_html_route_renders(self):
        status, _, body = _get("/sitemap-html")
        self.assertEqual(status, 200)
        self.assertIn('<a href="', body)

    def test_sitemap_html_has_canonical_and_jsonld(self):
        html = templates.sitemap_html()
        self.assertIn('rel="canonical" href="https://sipi.bot/sitemap-html"', html)
        self.assertIn("application/ld+json", html)

    def test_sitemap_html_lists_many_pages(self):
        html = templates.sitemap_html()
        # Should surface dozens of internal links (the whole URL set).
        self.assertGreater(html.count("<a href="), 100)

    def test_sitemap_html_slash_redirects(self):
        status, headers, _ = _get("/sitemap-html/")
        self.assertEqual(status, 301)
        self.assertIn("Location: /sitemap-html", headers)


class HomepageFooterAndSchemaTests(unittest.TestCase):
    def test_footer_has_sitemap_link(self):
        html = templates.landing_page_html()
        self.assertIn('href="/sitemap-html"', html)

    def test_organization_schema_has_logo_node(self):
        html = templates.landing_page_html()
        m = re.search(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S
        )
        data = json.loads(m.group(1))
        org = [n for n in data["@graph"] if n.get("@type") == "Organization"][0]
        self.assertIn("logo", org)
        self.assertEqual(org["logo"]["@id"], "https://sipi.bot/#logo")

    def test_organization_sameAs_has_at_least_five_real_entries(self):
        html = templates.landing_page_html()
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        data = json.loads(m.group(1))
        org = [n for n in data["@graph"] if n.get("@type") == "Organization"][0]
        self.assertGreaterEqual(len(org["sameAs"]), 5)
        # every sameAs must be a real https URL (no fabricated entities)
        for u in org["sameAs"]:
            self.assertTrue(u.startswith("https://"), u)

    def test_hero_does_not_link_dead_benchmark_url(self):
        # /benchmark/ (singular) 404s in production; must be /benchmarks/.
        html = templates.landing_page_html()
        self.assertNotIn('href="/benchmark/"', html)
        self.assertIn('href="/benchmarks/"', html)


class RelatedLinksInjectionTests(unittest.TestCase):
    def test_injection_adds_related_block(self):
        sample = open("vs/litellm/index.html").read()
        injected = api._inject_related_links(sample, "/vs/litellm/")
        self.assertIn("data-related-injected", injected)
        self.assertIn('aria-label="Related"', injected)

    def test_injection_is_idempotent(self):
        sample = open("vs/litellm/index.html").read()
        once = api._inject_related_links(sample, "/vs/litellm/")
        twice = api._inject_related_links(once, "/vs/litellm/")
        self.assertEqual(once.count("data-related-injected"),
                         twice.count("data-related-injected"))

    def test_injection_includes_sibling_links(self):
        sample = open("vs/litellm/index.html").read()
        injected = api._inject_related_links(sample, "/vs/litellm/")
        # at least one sibling /vs/<other> link besides the hub
        self.assertGreaterEqual(injected.count('href="/vs/'), 2)

    def test_injection_does_not_link_current_page(self):
        sample = open("vs/litellm/index.html").read()
        injected = api._inject_related_links(sample, "/vs/litellm/")
        # the Related block must not point back at itself
        block = injected.split('aria-label="Related"', 1)[1].split("</nav>", 1)[0]
        self.assertNotIn('href="/vs/litellm/"', block)


if __name__ == "__main__":
    unittest.main()
