#!/usr/bin/env python3
"""SEO Regression Audit: sitemap correctness, canonicals, redirects.

CI gate for sitemap hygiene. Every URL from the sitemap is fetched and checked:
  1. Direct 200 (no redirect).
  2. Self-canonical — sitemap <loc> and HTML canonical match byte-for-byte
     after safe URL resolution. No slash equivalence tolerated.
  3. HTML canonical is present and well-formed.
  4. Canonical target is reachable (200), not a redirect, not noindex.
  5. No sitemap URL is noindex.

Usage:
  python3 scripts/audit_sitemap_canonicals.py                  # against prod
  python3 scripts/audit_sitemap_canonicals.py --local :8080    # against local
  python3 scripts/audit_sitemap_canonicals.py --googlebot       # dual-UA audit

Exit 0 when every URL passes for every tested user agent.
Exit 1 when any issue is found.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print("ERROR: pip install requests", file=sys.stderr)
    sys.exit(2)


# ── config ────────────────────────────────────────────────────────────────────
PRODUCTION_ORIGIN = "https://sipi.bot"
SITEMAP_PATH = "/sitemap.xml"
REQUEST_TIMEOUT = 20
POLITENESS_DELAY = 0.05
USER_AGENT = "sipi-bot-seo-audit/1.0 (+https://sipi.bot)"
GOOGLEBOT_UA = (
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/W.X.Y.Z Mobile Safari/537.36 "
    "(compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
)

CANONICAL_LINK_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)
META_ROBOTS_RE = re.compile(r'<meta\s+name="robots"\s+content="([^"]+)"', re.I)


# ── classifications ──────────────────────────────────────────────────────────
# Every URL gets exactly one classification.
CLASS_REDIRECT_IN_SITEMAP     = "redirect-in-sitemap"
CLASS_MISSING_CANONICAL       = "missing-canonical"
CLASS_NON_SELF_CANONICAL      = "non-self-canonical"
CLASS_CANONICAL_TARGET_REDIR  = "canonical-target-redirects"
CLASS_CANONICAL_TARGET_ERROR  = "canonical-target-error"
CLASS_CANONICAL_TARGET_NOINDEX = "canonical-target-noindex"
CLASS_NOINDEX_IN_SITEMAP      = "noindex-in-sitemap"
CLASS_ERROR_UNREACHABLE       = "error-unreachable"
CLASS_VALID                   = "valid"


@dataclass
class URLAudit:
    sitemap_url: str
    request_url: str = ""
    initial_status: int | str = ""
    final_url: str = ""
    final_status: int | str = ""
    redirect_chain: list[str] = field(default_factory=list)
    hop_count: int = 0
    canonical_html: str = ""
    canonical_absolute: str = ""
    meta_robots: str = ""
    x_robots: str = ""
    title: str = ""
    classification: str = "unchecked"

    @property
    def is_self_canonical(self) -> bool:
        """Exact byte-for-byte match after safe URL resolution."""
        return self.canonical_absolute == self.sitemap_url

    @property
    def has_noindex(self) -> bool:
        return "noindex" in (self.meta_robots + " " + self.x_robots).lower()

    @property
    def is_failure(self) -> bool:
        return self.classification != CLASS_VALID


# ── URL rewriting ─────────────────────────────────────────────────────────────

def _rewrite_url(sitemap_url: str, origin: str, local_base: str) -> str:
    """Rewrite a sitemap URL to point at the local server."""
    if sitemap_url.startswith(origin):
        return local_base + sitemap_url[len(origin):]
    if sitemap_url.startswith(local_base):
        return sitemap_url
    parsed = urlparse(sitemap_url)
    local_parsed = urlparse(local_base)
    return parsed._replace(scheme=local_parsed.scheme,
                           netloc=local_parsed.netloc).geturl()


# ── sitemap fetch ─────────────────────────────────────────────────────────────

def fetch_sitemap_urls(source: str) -> tuple[list[str], str | None]:
    if source.startswith("http"):
        try:
            r = requests.get(source, headers={"User-Agent": USER_AGENT},
                             timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            xml_text = r.text
        except Exception as e:
            return [], f"Failed to fetch sitemap: {e}"
    else:
        try:
            with open(source) as f:
                xml_text = f.read()
        except Exception as e:
            return [], f"Failed to read sitemap file: {e}"

    try:
        root = ET.fromstring(xml_text)
        ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
        urls = [
            loc.text
            for url_elem in root.findall(f".//{{{ns}}}url")
            if (loc := url_elem.find(f"{{{ns}}}loc")) is not None and loc.text
        ]
        return urls, None
    except ET.ParseError as e:
        return [], f"Sitemap XML parse error: {e}"


# ── single-URL audit ──────────────────────────────────────────────────────────

def audit_url(sitemap_url: str, *,
              request_url: str | None = None,
              user_agent: str = USER_AGENT) -> URLAudit:
    """Audit one sitemap URL. Comparison is always against sitemap_url."""

    result = URLAudit(sitemap_url=sitemap_url)
    current = request_url or sitemap_url
    result.request_url = current
    chain: list[str] = []
    max_hops = 10

    # ── Phase A: follow redirects (no parsing) ──
    for hop in range(max_hops):
        try:
            r = requests.get(
                current, allow_redirects=False,
                headers={"User-Agent": user_agent},
                timeout=REQUEST_TIMEOUT,
            )
        except Exception as e:
            if hop == 0:
                result.initial_status = "error"
            result.final_status = f"error: {e}"
            result.classification = CLASS_ERROR_UNREACHABLE
            return result

        if hop == 0:
            result.initial_status = r.status_code
            chain.append(current)

        if r.status_code in (301, 302, 303, 307, 308):
            loc = r.headers.get("Location", "")
            if not loc:
                result.classification = CLASS_ERROR_UNREACHABLE
                return result
            current = urljoin(current, loc)
            chain.append(current)
        elif r.status_code == 200:
            result.final_status = 200
            result.final_url = current
            result.redirect_chain = chain
            result.hop_count = hop
            break
        else:
            result.final_status = r.status_code
            result.final_url = current
            result.classification = CLASS_ERROR_UNREACHABLE
            return result
    else:
        result.classification = CLASS_REDIRECT_IN_SITEMAP  # too many hops
        return result

    # ── Short-circuit: if the sitemap URL itself redirected, it's a failure ──
    if result.hop_count > 0:
        result.classification = CLASS_REDIRECT_IN_SITEMAP
        return result

    # ── Phase B: parse the 200 response ──
    try:
        r = requests.get(
            current, allow_redirects=False,
            headers={"User-Agent": user_agent},
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as e:
        result.classification = CLASS_ERROR_UNREACHABLE
        return result

    html = r.text

    # Meta robots on the page itself
    mr = META_ROBOTS_RE.search(html)
    if mr:
        result.meta_robots = mr.group(1)
    result.x_robots = r.headers.get("X-Robots-Tag", "")

    # Title
    tm = re.search(r"<title>([^<]+)</title>", html)
    result.title = (tm.group(1) if tm else "")[:120]

    # Canonical — must be present and well-formed
    cm = CANONICAL_LINK_RE.search(html)
    if not cm:
        result.classification = CLASS_MISSING_CANONICAL
        return result

    result.canonical_html = cm.group(1)
    result.canonical_absolute = urljoin(sitemap_url, result.canonical_html)

    # Exact comparison — no slash normalization
    if not result.is_self_canonical:
        result.classification = CLASS_NON_SELF_CANONICAL
        return result

    # Check for noindex on the sitemap URL itself
    if result.has_noindex:
        result.classification = CLASS_NOINDEX_IN_SITEMAP
        return result

    # ── Phase C: verify the canonical target ──
    target = result.canonical_absolute
    if request_url and request_url != sitemap_url:
        # If auditing locally, rewrite the canonical target to local too
        local_parsed = urlparse(request_url)
        target = _rewrite_url(target, PRODUCTION_ORIGIN,
                              f"{local_parsed.scheme}://{local_parsed.netloc}")

    try:
        cr = requests.get(
            target, allow_redirects=False,
            headers={"User-Agent": user_agent},
            timeout=REQUEST_TIMEOUT,
        )
    except Exception:
        result.classification = CLASS_CANONICAL_TARGET_ERROR
        return result

    if cr.status_code in (301, 302, 303, 307, 308):
        result.classification = CLASS_CANONICAL_TARGET_REDIR
        return result
    if cr.status_code in (404, 410):
        result.classification = CLASS_CANONICAL_TARGET_ERROR
        return result
    if cr.status_code >= 500:
        result.classification = CLASS_CANONICAL_TARGET_ERROR
        return result
    if cr.status_code != 200:
        result.classification = CLASS_CANONICAL_TARGET_ERROR
        return result

    # Check canonical target for noindex
    t_mr = META_ROBOTS_RE.search(cr.text)
    t_xr = cr.headers.get("X-Robots-Tag", "")
    target_noindex = (
        (t_mr and "noindex" in t_mr.group(1).lower())
        or "noindex" in t_xr.lower()
    )
    if target_noindex:
        result.classification = CLASS_CANONICAL_TARGET_NOINDEX
        return result

    result.classification = CLASS_VALID
    return result


# ── aggregate stats ──────────────────────────────────────────────────────────

def compute_stats(results: list[URLAudit]) -> dict:
    stats: dict[str, int] = {}
    for r in results:
        cls = r.classification
        stats[cls] = stats.get(cls, 0) + 1
    stats.setdefault(CLASS_VALID, 0)
    return stats


def failure_count(stats: dict) -> int:
    return sum(v for k, v in stats.items() if k != CLASS_VALID)


def print_summary(label: str, stats: dict):
    f = failure_count(stats)
    total = sum(stats.values())
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Total URLs audited:      {total}")
    print(f"  Valid:                   {stats.get(CLASS_VALID, 0)}  ✅")
    for cls in sorted(stats):
        if cls == CLASS_VALID:
            continue
        print(f"  {cls}:{' '*(25-len(cls))}{stats[cls]}  ❌")
    print(f"{'='*60}")
    if f == 0:
        print(f"  PASS — zero failures. ✅")
    else:
        print(f"  FAIL — {f} failure(s). ❌")
    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="sipi.bot sitemap/canonical audit")
    parser.add_argument("--sitemap", help="sitemap URL or local file path")
    parser.add_argument("--local", metavar="PORT",
                        help="Audit against local server (e.g. :8080)")
    parser.add_argument("--origin", default=PRODUCTION_ORIGIN,
                        help=f"Production origin (default: {PRODUCTION_ORIGIN})")
    parser.add_argument("--max-urls", type=int, default=0,
                        help="Limit audit to first N URLs (0 = all)")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--googlebot", action="store_true",
                        help="Also audit with Googlebot UA (included in aggregate)")
    args = parser.parse_args()

    origin = args.origin.rstrip("/")
    local_base = f"http://localhost{args.local}" if args.local else ""
    is_local = bool(args.local)

    if args.sitemap:
        sitemap_src = args.sitemap
    elif is_local:
        sitemap_src = f"{local_base}{SITEMAP_PATH}"
    else:
        sitemap_src = f"{origin}{SITEMAP_PATH}"

    print(f"Origin:     {origin}")
    if is_local:
        print(f"Local base: {local_base}")
    print(f"Mode:       {'LOCAL' if is_local else 'PRODUCTION'}")
    print(f"Sitemap:    {sitemap_src}")
    print(f"Googlebot:  {'yes' if args.googlebot else 'no'}")
    print()

    urls, err = fetch_sitemap_urls(sitemap_src)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(2)

    print(f"URLs found: {len(urls)}")
    if args.max_urls and args.max_urls < len(urls):
        urls = urls[:args.max_urls]
        print(f"Auditing:   first {len(urls)} URLs")
    print()

    # ── Audit with primary UA ──
    results: list[URLAudit] = []
    for i, sitemap_url in enumerate(urls):
        request_url = (_rewrite_url(sitemap_url, origin, local_base)
                       if is_local else sitemap_url)

        if args.verbose or (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(urls)}] {request_url}")

        result = audit_url(sitemap_url, request_url=request_url)
        results.append(result)

        if result.is_failure:
            print(f"  ❌ [{result.classification}] {sitemap_url}")
            if result.canonical_absolute and not result.is_self_canonical:
                print(f"     Sitemap:    {sitemap_url}")
                print(f"     Canonical:  {result.canonical_absolute}")

        time.sleep(POLITENESS_DELAY)

    primary_stats = compute_stats(results)

    # ── Audit with Googlebot UA (results merged into aggregate) ──
    gb_results: list[URLAudit] = []
    gb_stats: dict = {}
    if args.googlebot:
        print(f"\n── Googlebot pass ──")
        gb_results: list[URLAudit] = []
        for i, sitemap_url in enumerate(urls):
            request_url = (_rewrite_url(sitemap_url, origin, local_base)
                           if is_local else sitemap_url)

            if args.verbose or (i + 1) % 50 == 0:
                print(f"  [GB {i+1}/{len(urls)}] {request_url}")

            result = audit_url(sitemap_url, request_url=request_url,
                               user_agent=GOOGLEBOT_UA)
            gb_results.append(result)

            if result.is_failure:
                print(f"  ❌ [GB] [{result.classification}] {sitemap_url}")

            time.sleep(POLITENESS_DELAY)

        gb_stats = compute_stats(gb_results)

    # ── Print summaries ──
    print_summary("PRIMARY USER AGENT", primary_stats)
    if args.googlebot:
        print_summary("GOOGLEBOT", gb_stats)

    # ── Print issue details ──
    all_issues = [r for r in results if r.is_failure]
    if args.googlebot:
        all_issues += [r for r in gb_results if r.is_failure]
    if all_issues:
        print(f"\n{'='*60}")
        print("ISSUE DETAILS")
        print(f"{'='*60}")
        seen = set()
        for r in all_issues:
            key = (r.sitemap_url, r.classification)
            if key in seen:
                continue
            seen.add(key)
            print(f"\n  URL: {r.sitemap_url}")
            if is_local:
                print(f"  Requested: {r.request_url}")
            print(f"  Classification: {r.classification}")
            if r.hop_count:
                chain = " → ".join(r.redirect_chain)
                print(f"  Redirect chain ({r.hop_count} hops): {chain}")
            if r.canonical_html and not r.is_self_canonical:
                print(f"  HTML canonical: {r.canonical_html}")
                print(f"  Resolved:       {r.canonical_absolute}")
                print(f"  Expected:       {r.sitemap_url}")
            if r.classification == CLASS_MISSING_CANONICAL:
                print(f"  No <link rel=\"canonical\"> found in page HTML")
            if r.meta_robots:
                print(f"  Meta robots: {r.meta_robots}")
            if r.x_robots:
                print(f"  X-Robots-Tag: {r.x_robots}")

    # ── Exit code ──
    total_failures = failure_count(primary_stats)
    if args.googlebot:
        total_failures += failure_count(gb_stats)

    if total_failures == 0:
        print("\n✅ ALL CHECKS PASSED — ready for production.\n")
        sys.exit(0)
    else:
        print(f"\n❌ {total_failures} TOTAL FAILURE(S) across all user agents.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
