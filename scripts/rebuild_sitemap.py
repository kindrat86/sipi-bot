#!/usr/bin/env python3
"""Rebuild sitemap.xml from public/ HTML files and the pSEO fleet at repo root.

The pSEO clusters (vs/, for/, glossary/, etc.) are served directly from repo
root by api.py's _serve_pseo() — NOT from public/ — so a sitemap built by
walking public/ alone misses ~300 of the site's real, live pages. This walks
both: public/ (as before) and every prefix _serve_pseo() actually serves,
looking for exactly the index.html files that route resolves (matching its
lookup precisely, so nothing unreachable gets sitemapped).
"""
import os, re, subprocess
from xml.sax.saxutils import escape

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC = os.path.join(ROOT, "public")
SITEMAP = os.path.join(PUBLIC, "sitemap.xml")
SITE_BASE = "https://sipi.bot"

# Must match _serve_pseo()'s prefix list in spendfirewall/api.py exactly —
# these are the only repo-root directories any route actually serves.
PSEO_PREFIXES = [
    "compare", "vs", "for", "learn", "integrations", "glossary", "use-cases",
    "faq", "alternatives-to", "benchmarks", "tutorials", "policies", "limits",
    "best", "how-to", "templates", "cost-of",
    # 2026-07-27 traffic program: new shared-chrome surfaces (lib/generate_*.py)
    "incidents", "blog", "tools", "changelog", "status",
    # 2026-07-28: sync with _serve_pseo() prefix list in api.py — these prefixes
    # are served but were missing here, causing their pages to be absent from
    # the sitemap (and ghost URLs from removed pages to persist).
    "calculators", "compliance", "guides", "redflags", "scenarios", "data",
    # 2026-08-08 Round 20: industry vertical pages (sectors/)
    "sectors",
    # 2026-08-08 Round 21: API error-code reference (errors/)
    "errors",
    # 2026-08-08 Round 22: pricing questions (pricing-questions/)
    "pricing-questions",
]

# Directories to skip entirely (relative to public/). Checked as path prefix so
# subdirectories of excluded dirs (e.g. embed/tools/) are also skipped.
EXCLUDE_DIRS = {
    "embed",       # widget farm
    "widgets",     # embeddable widget HTML — not crawlable pages
}

# Individual filenames to skip anywhere in public/ — NOT index.html, that's
# the normal page marker and must stay includable. Widget .html files that
# produce trailing-slash URLs the server can't resolve (no index.html backing).
EXCLUDE_FILES = {
    "google57979683042f3b0e.html",
    "googlea30bb998b91eb6ac.html",
    "related-tools.html",   # widget artifact, not a page
    "widget.html",          # network/widget.html — embed widget, not a page
}



def git_lastmod(filepath):
    """Real last-content-change date from git history; falls back to mtime."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", filepath],
            capture_output=True, text=True, cwd=ROOT, timeout=5,
        )
        d = out.stdout.strip()
        if d:
            return d
    except Exception:
        pass
    from datetime import date, datetime
    try:
        return date.fromtimestamp(os.path.getmtime(filepath)).isoformat()
    except OSError:
        return date.today().isoformat()


def is_leaf(path_segments: tuple) -> bool:
    """True if path represents a leaf page (not a hub or the root).

    A page is a leaf when it has at least two path segments — a section
    prefix AND a slug (e.g. 'vs/litellm'). Hub index pages (e.g. just
    'vs') and the root '/' keep their trailing slashes.
    """
    return len(path_segments) >= 2


def build_sitemap():
    urls = {}  # full_url -> source filepath (for lastmod lookup)

    # Walk public/ directory (as before)
    for root, dirs, files in os.walk(PUBLIC):
        rel = os.path.relpath(root, PUBLIC)
        if rel == ".":
            rel = ""
        # Skip if this dir or any parent dir is excluded (prefix match catches
        # subdirectories like embed/tools/ too)
        if any(rel == d or rel.startswith(d + "/") for d in EXCLUDE_DIRS):
            continue
        # Skip mirrored leaves that are served from repo-root: if the exact
        # relative path exists at repo root, _serve_pseo() serves THAT file and
        # the fleet walk below emits its bare URL. Emitting the public slash
        # form here too would create a bare+slash duplicate pair.
        if rel:
            if os.path.isfile(os.path.join(ROOT, rel, "index.html")):
                continue
        for f in files:
            if not f.endswith(".html"):
                continue
            if f in EXCLUDE_FILES:
                continue
            if f == "index.html":
                url_path = "/" + rel.replace(os.sep, "/")
                if not url_path.endswith("/"):
                    url_path += "/"
                # Public/ pages are slash-canonical: _serve_static 301s the
                # bare form to the trailing-slash form, and since 2026-08-08
                # the pages' canonicals are slash too. Keep the trailing slash
                # for ALL index.html pages here (hubs and leaves alike).
                # Repo-root pSEO leaves stay BARE — that's the fleet walk
                # below, which is separate.
            else:
                name = f[:-5]
                url_path = ("/" + rel.replace(os.sep, "/") + "/" + name) if rel else ("/" + name)
                # Non-index flat files are leaf pages → bare
                url_path = url_path.rstrip("/")
            url_path = re.sub(r'/+', '/', url_path)
            full_url = SITE_BASE + url_path
            urls[full_url] = os.path.join(root, f)

    # Walk the pSEO fleet at repo root — only the exact index.html files
    # _serve_pseo() would actually resolve for a given URL.
    for prefix in PSEO_PREFIXES:
        base = os.path.join(ROOT, prefix)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            if "index.html" not in files:
                continue
            rel = os.path.relpath(root, ROOT)
            url_path = "/" + rel.replace(os.sep, "/")
            # Keep trailing slash for hub pages; leaf pages go bare
            segments = tuple(s for s in url_path.strip("/").split("/") if s)
            if is_leaf(segments):
                # Leaf page: no trailing slash, matches normalize_canonicals output
                pass
            else:
                # Hub page: keep trailing slash
                url_path += "/"
            url_path = re.sub(r'/+', '/', url_path)
            full_url = SITE_BASE + url_path
            urls[full_url] = os.path.join(root, "index.html")

    # Dynamic server-rendered pages not backed by a file
    urls.setdefault(SITE_BASE + "/", None)
    urls.setdefault(SITE_BASE + "/blog/", None)
    # Flat dynamic pages served by api.py (2026-08-08: were missing from sitemap)
    for flat in ["/about", "/pricing", "/security", "/terms", "/privacy"]:
        urls.setdefault(SITE_BASE + flat, None)

    urls_sorted = sorted(urls.keys())
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls_sorted:
        filepath = urls[url]
        lastmod = git_lastmod(filepath) if filepath else git_lastmod(__file__)
        parts.append(f'  <url><loc>{escape(url)}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>')
    parts.append('</urlset>')

    xml = '\n'.join(parts) + '\n'
    with open(SITEMAP, "w") as f:
        f.write(xml)

    print(f"Built sitemap.xml with {len(urls_sorted)} URLs")

if __name__ == "__main__":
    build_sitemap()
