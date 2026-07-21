#!/usr/bin/env python3
"""Rebuild sitemap.xml from public/ HTML files."""
import os, sys, re
from datetime import date
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

PUBLIC = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "public"))
SITEMAP = os.path.join(PUBLIC, "sitemap.xml")
SITE_BASE = "https://sipi.bot"
TODAY = date.today().isoformat()

# Pages to exclude (noindex or non-canonical)
EXCLUDE = {
    "embed",  # widget farm
    "index.html",
    "google57979683042f3b0e.html",
    "googlea30bb998b91eb6ac.html",
    "BingSiteAuth.xml",
    "robots.txt",
    "sitemap.xml",
    "sitemap-index.xml",
    "favicon.svg",
    "og.png",
    "ux.css", "ux.js",
    "image-sitemap.xml",
}

def build_sitemap():
    urls = set()

    # Walk public/ directory
    for root, dirs, files in os.walk(PUBLIC):
        rel = os.path.relpath(root, PUBLIC)
        if rel == ".":
            rel = ""
        # Skip excluded dirs
        if rel in EXCLUDE:
            continue
        for f in files:
            if not f.endswith(".html"):
                continue
            # Get the URL path
            if f == "index.html":
                url_path = "/" + rel.replace(os.sep, "/")
                if not url_path.endswith("/"):
                    url_path += "/"
            else:
                name = f[:-5]  # strip .html
                if rel:
                    url_path = "/" + rel.replace(os.sep, "/") + "/" + name
                else:
                    url_path = "/" + name
                url_path += "/"

            # Normalize: remove trailing // or duplicate slashes
            url_path = re.sub(r'/+', '/', url_path)

            full_url = SITE_BASE + url_path
            urls.add(full_url)

    # Sort and write
    # Add dynamic server-rendered pages not in public/
    urls.add(SITE_BASE + "/blog/")

    urls_sorted = sorted(urls)
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls_sorted:
        parts.append(f'  <url><loc>{escape(url)}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>')
    parts.append('</urlset>')

    xml = '\n'.join(parts) + '\n'
    with open(SITEMAP, "w") as f:
        f.write(xml)

    print(f"Built sitemap.xml with {len(urls_sorted)} URLs")

if __name__ == "__main__":
    build_sitemap()
