#!/usr/bin/env python3
"""W3 (part 2) — normalize canonical tags + sitemap to the BARE form.

The site's canonical tags were split 156 bare / 70 slash. W3 in api.py now
301-redirects slash leaf URLs → bare, so the canonical tags and sitemap
must agree: leaf pages canonicalize to bare (no trailing slash); hub index
pages (section roots like /vs/, /templates/) keep the slash form.

This rewrites:
  1. <link rel="canonical"> on every leaf index.html → bare form
  2. og:url to match
  3. public/sitemap.xml leaf URLs → bare form

Hub index pages are left on slash. Re-runnable; only changes mismatched lines.
"""
from __future__ import annotations
import os, re

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SITE = "https://sipi.bot"

# Sections whose ROOT index is a real hub (slash-canonical).
HUB_SECTIONS = {
    "vs", "for", "learn", "integrations", "glossary", "use-cases", "faq",
    "alternatives-to", "benchmarks", "tutorials", "policies", "limits",
    "best", "how-to", "templates", "cost-of", "alternatives", "compare",
}

# pSEO prefixes served by _serve_pseo (must match api.py)
PSEO_PREFIXES = HUB_SECTIONS


def is_leaf(rel_path: str) -> bool:
    """True if rel_path like 'vs/litellm/index.html' is a leaf (not a hub).
    Handles both repo-root ('vs/litellm/index.html') and public/
    ('public/vs/litellm/index.html') layouts."""
    p = rel_path.replace(os.sep, "/")
    # strip a leading public/ if present
    if p.startswith("public/"):
        p = p[len("public/"):]
    parts = p.split("/")
    # ['vs','litellm','index.html'] → leaf; ['vs','index.html'] → hub
    return len(parts) >= 3 and parts[-1] == "index.html" and parts[0] in HUB_SECTIONS


def normalize_file(filepath: str) -> bool:
    """Strip trailing slash from canonical + og:url on a leaf page. Returns True if changed."""
    rel = os.path.relpath(filepath, ROOT)
    if not is_leaf(rel):
        return False
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    original = content

    # Rewrite canonical URLs that point at a leaf with trailing slash → bare
    # Match https://sipi.bot/<section>/<slug...>/  (ending in /, with path depth)
    def bareize(m):
        url = m.group(1)
        # only strip if it's a leaf URL (has a path under the section) and ends with /
        after_host = url.replace(SITE + "/", "")
        parts = after_host.strip("/").split("/")
        if len(parts) >= 2 and url.endswith("/"):
            return m.group(0).replace(url, url.rstrip("/"))
        return m.group(0)

    content = re.sub(r'rel="canonical" href="([^"]+)"', bareize, content)
    content = re.sub(r'<meta property="og:url" content="([^"]+)"', bareize, content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def normalize_sitemap() -> int:
    """Rewrite public/sitemap.xml leaf URLs to bare form."""
    sitemap = os.path.join(ROOT, "public", "sitemap.xml")
    with open(sitemap, encoding="utf-8") as f:
        content = f.read()
    original = content

    def bareize_loc(m):
        url = m.group(1)
        after_host = url.replace(SITE + "/", "")
        parts = after_host.strip("/").split("/")
        # leaf = section/slug... ; keep root "/" and pure section hubs "/vs/" slashed
        if len(parts) >= 2 and url.endswith("/"):
            return "<loc>" + url.rstrip("/") + "</loc>"
        return m.group(0)

    content = re.sub(r"<loc>([^<]+)</loc>", bareize_loc, content)
    changed = content != original
    if changed:
        with open(sitemap, "w", encoding="utf-8") as f:
            f.write(content)
    return 1 if changed else 0


def main():
    changed_files = []
    for prefix in PSEO_PREFIXES:
        for base in (os.path.join(ROOT, prefix), os.path.join(ROOT, "public", prefix)):
            if not os.path.isdir(base):
                continue
            for dirpath, _, files in os.walk(base):
                if "index.html" in files:
                    fp = os.path.join(dirpath, "index.html")
                    if normalize_file(fp):
                        changed_files.append(os.path.relpath(fp, ROOT))
    sm = normalize_sitemap()
    print(f"Normalized canonicals on {len(changed_files)} leaf page(s).")
    if changed_files:
        for f in changed_files[:20]:
            print(f"  {f}")
        if len(changed_files) > 20:
            print(f"  ... and {len(changed_files) - 20} more")
    print(f"Sitemap rewritten: {sm}")


if __name__ == "__main__":
    main()
