#!/usr/bin/env python3
"""Comprehensive sitemap audit for sipi.bot — compares all HTML files on disk
against the live sitemap and reports missing URLs."""
import re, urllib.request
from pathlib import Path

ROOT = Path("/Users/sipi/projects/sipi-bot")

# Collect all index.html files
pages = set()

# Main directories
for d in ["vs", "for", "how-to", "learn", "benchmarks", "faq", "glossary", "alternatives-to", "best"]:
    for f in (ROOT / d).glob("*/index.html"):
        rel = str(f.relative_to(ROOT)).rsplit("/index.html")[0]
        pages.add(f"https://sipi.bot/{rel}")
    # Also hub pages (direct index.html in the dir)
    hub = ROOT / d / "index.html"
    if hub.exists():
        pages.add(f"https://sipi.bot/{d}/")

# Public directory
for f in (ROOT / "public").glob("**/index.html"):
    rel = str(f.relative_to(ROOT / "public")).rsplit("/index.html")[0]
    pages.add(f"https://sipi.bot/{rel}/")

# Static pages
for name in ["llms.txt", "llms-full.txt", "sitemap.xml", "robots.txt"]:
    pages.discard(f"https://sipi.bot/{name}")

# Fetch live sitemap
try:
    resp = urllib.request.urlopen("https://sipi.bot/sitemap.xml", timeout=10)
    sitemap_xml = resp.read().decode()
    sitemap_urls = set(re.findall(r'<loc>([^<]+)</loc>', sitemap_xml))
except Exception as e:
    print(f"Error fetching sitemap: {e}")
    sitemap_urls = set()

# Compare
on_disk = pages
in_sitemap = sitemap_urls
missing = on_disk - in_sitemap
extra = in_sitemap - on_disk

print(f"Pages on disk: {len(on_disk)}")
print(f"URLs in sitemap: {len(in_sitemap)}")
print()
if missing:
    print(f"MISSING from sitemap ({len(missing)}):")
    for url in sorted(missing):
        print(f"  {url}")
else:
    print("✅ All pages on disk are in the sitemap")
print()
if extra:
    print(f"EXTRA in sitemap (not on disk) ({len(extra)}):")
    for url in sorted(extra)[:10]:
        print(f"  {url}")
else:
    print("✅ No extra URLs in sitemap")

print()
print("⚠️ The sitemap is managed by the growth engine (dynamic).")
print("   Hub pages and growth-engine pages may be auto-included on next rebuild.")
