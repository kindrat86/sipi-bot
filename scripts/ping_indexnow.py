#!/usr/bin/env python3
"""Ping IndexNow (Bing, Yandex) to notify of new/changed URLs.

Usage:
    python3 scripts/ping_indexnow.py            # ping all sitemap URLs
    python3 scripts/ping_indexnow.py URL1 URL2  # ping specific URLs

Requires the key file at public/{INDEXNOW_KEY}.txt — already deployed.
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
import urllib.error
import re

BASE = "https://sipi.bot"
INDEXNOW_KEY = "9769ace59182381fe1af49982d9b58a9"
INDEXNOW_KEY_LOCATION = f"{BASE}/{INDEXNOW_KEY}.txt"


def urls_from_sitemap(sitemap_path: str = "public/sitemap.xml") -> list[str]:
    """Extract all <loc> URLs from the sitemap."""
    if not os.path.isabs(sitemap_path):
        sitemap_path = os.path.join(os.path.dirname(__file__), "..", sitemap_path)
    with open(sitemap_path) as f:
        xml = f.read()
    return re.findall(r"<loc>(.*?)</loc>", xml)


def ping(urls: list[str]) -> None:
    if not urls:
        print("No URLs to ping.")
        return
    payload = json.dumps({
        "host": "sipi.bot",
        "key": INDEXNOW_KEY,
        "keyLocation": INDEXNOW_KEY_LOCATION,
        "urlList": urls,
    }).encode()
    print(f"Pinging IndexNow with {len(urls)} URLs…")
    for endpoint in ("https://api.indexnow.org/indexnow",
                     "https://www.bing.com/indexnow"):
        try:
            req = urllib.request.Request(
                endpoint,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"  {endpoint}: {resp.status}")
        except urllib.error.HTTPError as e:
            print(f"  {endpoint}: HTTP {e.code} ({e.reason})")
        except Exception as e:
            print(f"  {endpoint}: {e}")


def main():
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        urls = urls_from_sitemap()
    ping(urls)


if __name__ == "__main__":
    main()
