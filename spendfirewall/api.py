"""api.py — HTTP API + dashboard server + agent-card + eval report.

Stdlib only (http.server). Serves:
  GET  /                          landing page
  GET  /dashboard                 control room
  GET  /health                    {"ok": true}
  GET  /.well-known/agent-card.json   agent discoverability
  GET  /openapi.json                  OpenAPI 3.0 spec (AIO / AI-agent discoverability)
  GET  /eval                      last eval report (JSON) — the sales asset
  POST /v1/transactions/evaluate  THE core call (auth optional in free mode)
  GET  /v1/activity               retired (tenant-safe dashboard polls instead)
  GET  /api/stats                 dashboard aggregates
  GET  /api/transactions          recent txns
  GET  /api/approvals             pending approvals
  POST /api/approvals/<id>        resolve {decision}
  GET  /api/rules                 list rules
  POST /api/rules                 add rule
  DELETE /api/rules/<id>          delete rule
  GET  /api/agents                list agents
  POST /api/agents                register agent -> api key
  POST /subscribe                 email capture
"""
from __future__ import annotations

import gzip as _gzip
import hmac
import html as _html
import json
import math
import os
import queue
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlparse

from . import __version__, core, store, templates
from . import billing
from . import drip

# --- HTTP response compression (opt-in via env, safe default on) ---
# The server previously emitted every HTML/JSON/SVG body uncompressed — the
# 58 KB homepage shipped raw. gzip-encoding compressible text types above a
# small threshold cuts transfer size ~75% (and TTFB on slow/mobile links).
# Disabled under tests by setting HTTP_COMPRESSION=false.
_COMPRESSION_ENABLED = os.environ.get("HTTP_COMPRESSION", "true").lower() not in (
    "0",
    "false",
    "no",
    "off",
)
_COMPRESS_MIN_BYTES = 1024
_COMPRESSIBLE_PREFIXES = (
    "text/",
    "application/json",
    "application/javascript",
    "application/xml",
    "image/svg+xml",
)


def _gzip_acceptable(accept_encoding: str) -> bool:
    return "gzip" in (accept_encoding or "").lower()


def _compress_body(body: bytes, ctype: str, accept_encoding: str):
    """Return (body, content_encoding) — gzip when eligible, else unchanged.

    Compresses only compressible content-types above _COMPRESS_MIN_BYTES when
    the client advertised gzip and compression is enabled. Never compresses
    already-compressed types (images, fonts) or small bodies where the gzip
    header overhead exceeds the saving."""
    if not _COMPRESSION_ENABLED:
        return body, None
    if len(body) < _COMPRESS_MIN_BYTES:
        return body, None
    if not _gzip_acceptable(accept_encoding):
        return body, None
    if not ctype:
        return body, None
    semi = ctype.split(";", 1)[0].strip().lower()
    if not semi.startswith(_COMPRESSIBLE_PREFIXES):
        return body, None
    return _gzip.compress(body, compresslevel=6), "gzip"

_SUBSCRIBERS: list[queue.Queue] = []
_SUB_LOCK = threading.Lock()
_SUBSCRIBER_FILE_LOCK = threading.RLock()
_EVAL_REPORT_PATH = os.environ.get("EVAL_REPORT", os.path.join(os.getcwd(), "eval_report.json"))
_SUBSCRIBERS_FILE = os.environ.get("SUBS_FILE", os.path.join(os.getcwd(), "subscribers.txt"))
# Trusted origin echoed on state-changing control-plane routes instead of *.
_TRUSTED_ORIGIN = (os.environ.get("PUBLIC_URL") or "https://sipi.bot").rstrip("/")

# Bare app routes served by exact `path ==` match in do_GET. The site convention
# is bare URLs for app pages (/eval, /badge, /pricing, /dashboard) and directory
# URLs for pSEO spokes (/for/crewai/, /vs/litellm/). A user who types the slash
# form of a bare route (/eval/) used to hit a 404 — Google reads that as a
# soft-404 error and wastes crawl budget. do_GET uses this set to 301 /eval/
# -> /eval (and every other bare route) while leaving pSEO directory URLs
# untouched. Keep in sync with the `if path == "/..."` block in do_GET.
_BARE_ROUTES = frozenset({
    "/dashboard", "/health", "/eval", "/badge", "/pricing",
    "/masterclass", "/about", "/content-calendar", "/privacy", "/terms",
    "/data", "/blog", "/sitemap-html",
})

# --- In-memory rate limiting (per-instance, abuse prevention) ---
import time as _rl_time
from collections import defaultdict as _rl_defaultdict

_RATE_LIMITS = {
    "subscribe": {"window": 3600, "max": 5},     # 5 email captures/hour/IP
    "evaluate":  {"window": 60,   "max": 100},    # 100 evaluate calls/min/IP
    "default":   {"window": 60,   "max": 60},     # 60 req/min/IP fallback
}
_rate_windows: dict[str, list[float]] = _rl_defaultdict(list)
_last_rl_cleanup = _rl_time.time()


def _check_rate_limit(route_key: str, client_ip: str) -> bool:
    """Return True if within limit, False if exceeded. Thread-safe enough for ThreadingHTTPServer."""
    global _last_rl_cleanup
    cfg = _RATE_LIMITS.get(route_key, _RATE_LIMITS["default"])
    now = _rl_time.time()
    # Periodic cleanup (every 5 min) to prevent memory leak from abandoned IPs
    if now - _last_rl_cleanup > 300:
        _last_rl_cleanup = now
        max_w = max(c["window"] for c in _RATE_LIMITS.values())
        cutoff = now - max_w - 60
        stale = [k for k, v in _rate_windows.items() if not v or max(v) < cutoff]
        for k in stale:
            del _rate_windows[k]
    window_start = now - cfg["window"]
    key = f"{client_ip}:{route_key}"
    _rate_windows[key] = [t for t in _rate_windows[key] if t > window_start]
    if len(_rate_windows[key]) >= cfg["max"]:
        return False
    _rate_windows[key].append(now)
    return True


def _broadcast(event: dict) -> None:
    data = json.dumps(event)
    with _SUB_LOCK:
        dead = []
        for q in _SUBSCRIBERS:
            try:
                q.put_nowait(data)
            except Exception:
                dead.append(q)
        for q in dead:
            _SUBSCRIBERS.remove(q)


def _resolve_api_key(api_key: str) -> tuple[Optional[str], Optional[dict]]:
    """Resolve operator-created and paid checkout keys through one auth path."""
    agent = store.get_agent_by_key(api_key)
    if agent:
        return agent["id"], {"source": "agent", "agent": agent}
    paid = billing.validate_key(api_key)
    if paid:
        return paid["agent_id"], {"source": "billing", "billing": paid}
    return None, None


def _is_admin_token(given: str) -> bool:
    admin = os.environ.get("ADMIN_TOKEN", "")
    return bool(
        admin
        and given
        and hmac.compare_digest(given.encode(), admin.encode())
    )


def _validated_rule_input(body: dict) -> tuple[Optional[dict], Optional[str]]:
    """Bound rule input so one malformed rule cannot break a workspace."""
    rule_type = body.get("rule_type", "")
    allowed_types = {
        "per_transaction",
        "daily_total",
        "velocity",
        "merchant_block",
        "merchant_allow",
        "category_limit",
        "time_window",
        "approval_threshold",
    }
    if rule_type not in allowed_types:
        return None, "invalid_rule_type"
    action = body.get("action", "BLOCKED")
    if action not in {"BLOCKED", "FLAGGED"}:
        return None, "invalid_rule_action"
    params = body.get("params", {})
    if not isinstance(params, dict):
        return None, "invalid_rule_params"
    try:
        priority = int(body.get("priority", 100))
    except (TypeError, ValueError):
        return None, "invalid_rule_priority"
    if not -10_000 <= priority <= 10_000:
        return None, "invalid_rule_priority"
    label = body.get("label", "")
    if not isinstance(label, str) or len(label) > 200:
        return None, "invalid_rule_label"

    def positive_number(name: str, maximum: float = 1_000_000_000) -> bool:
        try:
            value = float(params.get(name))
        except (TypeError, ValueError):
            return False
        return math.isfinite(value) and 0 < value <= maximum

    if rule_type in {"per_transaction", "daily_total"}:
        if not positive_number("max_amount"):
            return None, "invalid_rule_params"
    elif rule_type == "approval_threshold":
        if not positive_number("amount"):
            return None, "invalid_rule_params"
    elif rule_type == "velocity":
        if not positive_number("max_count", 1_000_000) or not positive_number(
            "window_seconds", 31_536_000
        ):
            return None, "invalid_rule_params"
    elif rule_type in {"merchant_block", "merchant_allow"}:
        patterns = params.get("patterns")
        if (
            not isinstance(patterns, list)
            or not 1 <= len(patterns) <= 100
            or any(not isinstance(item, str) or not 1 <= len(item) <= 256 for item in patterns)
        ):
            return None, "invalid_rule_params"
    elif rule_type == "category_limit":
        category = params.get("category")
        if (
            not isinstance(category, str)
            or not 1 <= len(category) <= 64
            or not positive_number("max_amount")
        ):
            return None, "invalid_rule_params"
    elif rule_type == "time_window":
        try:
            start = int(params.get("start_hour"))
            end = int(params.get("end_hour"))
        except (TypeError, ValueError):
            return None, "invalid_rule_params"
        if not 0 <= start <= 23 or not 1 <= end <= 24:
            return None, "invalid_rule_params"
    return {
        "rule_type": rule_type,
        "params": params,
        "action": action,
        "priority": priority,
        "label": label.strip(),
    }, None


def _validated_transaction_input(
    body: dict,
) -> tuple[Optional[dict], Optional[str]]:
    if "amount" not in body:
        return None, "amount_required"
    try:
        amount = float(body["amount"])
    except (TypeError, ValueError):
        return None, "invalid_amount"
    if not math.isfinite(amount) or abs(amount) > 1_000_000_000_000:
        return None, "invalid_amount"
    limits = {
        "merchant": 512,
        "category": 128,
        "description": 2_000,
        "currency": 8,
        "timestamp": 64,
    }
    values: dict[str, Optional[str]] = {}
    for name, maximum in limits.items():
        value = body.get(name)
        if value is None and name == "timestamp":
            values[name] = None
            continue
        if value is None:
            value = "USD" if name == "currency" else ""
        if not isinstance(value, str) or len(value) > maximum:
            return None, f"invalid_{name}"
        values[name] = value
    return {"amount": amount, **values}, None


# --- pSEO internal-link-graph enrichment -------------------------------------
# Cached parse of sitemap.xml -> {silo: [urls]}. Built once per process; the
# sitemap changes rarely and a stale cache only means a new page isn't linked
# until restart, never a broken link (every URL came from the sitemap itself).
_SITEMAP_INDEX = None
_SITEMAP_INDEX_MTIME = 0.0


def _sitemap_index():
    """Return {silo: [/path/, ...]} parsed from sitemap.xml, cached by mtime."""
    global _SITEMAP_INDEX, _SITEMAP_INDEX_MTIME
    import os as _os
    base = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
    sm = _os.path.join(base, "sitemap.xml")
    try:
        mt = _os.path.getmtime(sm)
    except OSError:
        return {}
    if _SITEMAP_INDEX is not None and mt == _SITEMAP_INDEX_MTIME:
        return _SITEMAP_INDEX
    import re as _re
    sections = {}
    try:
        with open(sm, encoding="utf-8") as fh:
            for m in _re.finditer(r"<loc>([^<]+)</loc>", fh.read()):
                url = m.group(1).strip().replace("https://sipi.bot", "")
                parts = [p for p in url.split("/") if p]
                if len(parts) >= 2:
                    sections.setdefault(parts[0], []).append(url)
    except OSError:
        return {}
    _SITEMAP_INDEX = sections
    _SITEMAP_INDEX_MTIME = mt
    return sections


def _inject_related_links(html, current_path):
    """Inject a 'Related' cross-link block before </body> on pSEO pages.

    Picks up to 5 same-silo siblings (excluding the current page) plus up to 3
    stable hub links (homepage, integrations index, comparison index).
    Strengthens the internal-link graph so pSEO spokes aren't orphaned and
    crawl discovery + link equity flow beyond the homepage's dozen links.
    Idempotent via a sentinel comment so re-injection never duplicates the block."""
    import html as _html
    # Idempotent at the helper level too (not just at the _serve_pseo call
    # site): never double-inject if the block is already present.
    if "data-related-injected" in html:
        return html
    sections = _sitemap_index()
    parts = [p for p in current_path.strip("/").split("/") if p]
    if not parts:
        return html
    silo = parts[0]
    siblings = [u for u in sections.get(silo, []) if u.rstrip("/") != current_path.rstrip("/")][:5]
    if not siblings:
        return html
    # Hub links — only ones that exist as silos in the sitemap.
    hubs = []
    for hub_path, label in [
        ("/", "Home"),
        ("/for/", "All integrations"),
        ("/vs/", "All comparisons"),
        ("/glossary/", "Glossary"),
    ]:
        if hub_path == "/":
            hubs.append((hub_path, label))
        elif hub_path.strip("/") in sections and sections[hub_path.strip("/")]:
            hubs.append((hub_path, label))
    links = "".join(
        '<li><a href="%s">%s</a></li>' % (
            _html.escape(u),
            _html.escape(u.strip("/").split("/")[-1].replace("-", " ").title()),
        )
        for u in siblings
    )
    hub_links = "".join(
        '<li><a href="%s">%s</a></li>' % (_html.escape(p), _html.escape(lbl))
        for p, lbl in hubs[:3]
    )
    block = (
        '\n<!-- data-related-injected: internal-link-graph enrichment -->\n'
        '<nav aria-label="Related" style="max-width:760px;margin:48px auto 0;padding:24px 20px;'
        'border-top:1px solid #23242a;font:14px/1.7 -apple-system,BlinkMacSystemFont,sans-serif">'
        '<strong style="color:#e8e8ea;font-size:13px;text-transform:uppercase;letter-spacing:.05em">Related</strong>'
        '<ul style="list-style:none;padding:0;margin:12px 0 0;display:grid;grid-template-columns:1fr 1fr;gap:6px 18px">'
        + links + hub_links +
        '</ul></nav>\n'
    )
    return html.replace("</body>", block + "</body>", 1)


def _inject_mobile_nav(html: str) -> str:
    """Inject a working mobile hamburger nav into a baked pSEO page.

    0 of the 176 baked content pages had a mobile menu, so on phones their nav
    links wrapped/overflowed with no path back to Home / FAQ / How-it-works.
    This adds the same nav the landing page ships (button + #mainnav + toggle
    JS), scoped under .sipi-nav so the injected NAV_CSS never restyles the
    page body. Idempotent.
    """
    if 'data-sipi-nav-injected' in html or 'class="nav-toggle"' in html:
        return html
    nav_links = (
        '    <a href="/">Home</a>\n'
        '    <a href="/#how">How it works</a>\n'
        '    <a href="/#faq">FAQ</a>\n'
        '    <a href="/pricing">Pricing</a>\n'
        '    <a href="/dashboard" class="btn">Dashboard</a>'
    )
    brand = (
        '<div class="brand"><a href="/" style="color:var(--txt)">'
        'sipi<span class="dot">.bot</span></a></div>'
    )
    nav = (
        '<div class="sipi-nav" data-sipi-nav-injected>'
        + templates.NAV_CSS +
        '<nav><div class="wrap">\n  ' + brand + '\n  ' + templates.NAV_TOGGLE +
        '\n  <div class="nav-links" id="mainnav">\n' + nav_links +
        '\n  </div>\n</div></nav>\n' + templates.NAV_JS +
        '</div>\n'
    )
    m = re.search(r"<body\b[^>]*>", html, re.I)
    if not m:
        return html
    return html[:m.end()] + "\n" + nav + html[m.end():]


def agent_card() -> dict:
    return {
        "name": "sipi.bot Spend Firewall",
        "description": "Approves, blocks, or flags every transaction an autonomous AI agent "
                       "proposes, against configurable spend rules. The firewall for the agent economy.",
        "version": __version__,
        "url": "https://sipi.bot",
        "provider": {"organization": "sipi.bot", "url": "https://sipi.bot"},
        "capabilities": {"streaming": False},
        "skills": [{
            "id": "evaluate_transaction",
            "name": "Evaluate a spend",
            "description": "Given amount, merchant, category, returns APPROVED, BLOCKED, or FLAGGED.",
            "tags": ["spend-control", "policy", "guardrail", "agent-safety"],
            "examples": ["Can my agent spend $6200 at unknown-gpu.ru?"],
        }],
        "endpoints": {
            "evaluate": "https://sipi.bot/v1/transactions/evaluate",
            "openapi": "https://sipi.bot/openapi.json",
            "eval_report": "https://sipi.bot/eval",
        },
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):  # quieter logs
        pass

    def _client_ip(self) -> str:
        # Prefer Fly-Client-IP: it is set by the Fly proxy and is NOT
        # client-controllable, unlike X-Forwarded-For which an attacker can
        # forge to bypass per-IP rate limits (verified: rotating XFF values
        # all returned 200, defeating the 100/min/IP cap). XFF is only used as
        # a fallback for local/self-hosted deployments that run without the
        # Fly proxy in front.
        fly_ip = self.headers.get("Fly-Client-IP", "")
        if fly_ip:
            return fly_ip.strip()
        forwarded = self.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.client_address[0] if self.client_address else "0.0.0.0"

    def _check_rate(self, route_key: str) -> bool:
        return _check_rate_limit(route_key, self._client_ip())

    def _send(self, code: int, body: bytes, ctype="application/json", noindex=False,
              origin="*"):
        accept_encoding = self.headers.get("Accept-Encoding", "")
        body, encoding = _compress_body(body, ctype, accept_encoding)
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if noindex:
            # Machine endpoints (JSON) should not appear in search indexes.
            self.send_header("X-Robots-Tag", "noindex")
        # Vary tells any shared cache (Fly edge / CDN) that the response
        # representation depends on the Accept-Encoding request header, so a
        # gzip-encoded body is never served to a client that can't decode it.
        self.send_header("Vary", "Accept-Encoding")
        if encoding:
            self.send_header("Content-Encoding", encoding)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Headers", "Authorization,Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS,HEAD")
        # Security headers (Technical SEO + hardening) — matches _html() set.
        # CSP/PP are tighter than HTML: JSON/XML responses carry no scripts,
        # frames, or external assets, so default-src 'none' is safe here.
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
        self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=(), interest-cohort=()")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        self.close_connection = True
        self.end_headers()
        if getattr(self, "_head_only", False):
            return
        self.wfile.write(body)
        self.wfile.flush()

    def do_HEAD(self):
        """Mirror do_GET but suppress the body (fixes 501-on-HEAD; crawlers/audits use HEAD)."""
        self._head_only = True
        try:
            self.do_GET()
        finally:
            self._head_only = False

    def _json(self, code, obj, noindex=False, origin="*"):
        self._send(code, json.dumps(obj).encode(), "application/json", noindex=noindex,
                   origin=origin)

    def _require_admin(self) -> bool:
        """Bearer-token gate for state-changing control-plane routes
        (rules, agents/key-minting, approval resolution, admin reset).

        Reads ADMIN_TOKEN from the environment and compares in constant
        time. FAILS CLOSED: when ADMIN_TOKEN is unset every request is
        rejected with 403 until the operator sets the secret."""
        auth = self.headers.get("Authorization", "")
        given = auth[7:].strip() if auth.startswith("Bearer ") else ""
        if _is_admin_token(given):
            return True
        self._json(403, {"error": "forbidden"}, origin=_TRUSTED_ORIGIN)
        return False

    def _control_auth(self) -> Optional[dict]:
        """Authorize a dashboard/control-plane request.

        Operators receive an unscoped view with ADMIN_TOKEN. Checkout and
        operator-created API keys receive an isolated workspace keyed by the
        same agent identity used for transaction evaluation.
        """
        auth = self.headers.get("Authorization", "")
        given = auth[7:].strip() if auth.startswith("Bearer ") else ""
        if _is_admin_token(given):
            return {"admin": True, "agent_id": None}
        if given:
            agent_id, context = _resolve_api_key(given)
            if context:
                return {"admin": False, "agent_id": agent_id}
        self._json(
            401,
            {"error": "api_key_required"},
            noindex=True,
            origin=_TRUSTED_ORIGIN,
        )
        return None

    def _html(self, html: str, cacheable: bool = True):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if cacheable:
            self.send_header("Cache-Control", "public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800")
        else:
            # Secret-bearing pages (e.g. /keys/<session>) must never sit in
            # a shared/CDN cache or a search index.
            self.send_header("Cache-Control", "no-store, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Referrer-Policy",
            "strict-origin-when-cross-origin" if cacheable else "no-referrer",
        )
        if cacheable:
            csp = (
                "default-src 'self'; script-src 'self' 'unsafe-inline' "
                "https://js.stripe.com https://eu.i.posthog.com "
                "https://eu-assets.i.posthog.com https://eu.posthog.com "
                "https://checkout.stripe.com; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; connect-src 'self' "
                "https://eu.i.posthog.com https://eu-assets.i.posthog.com "
                "https://sipi.bot; frame-ancestors 'none'; "
                "object-src 'none'; base-uri 'self'; "
                "frame-src https://js.stripe.com https://checkout.stripe.com; "
                "require-trusted-types-for 'script'"
            )
        else:
            # Secret-bearing success pages must never load third-party scripts,
            # make cross-origin requests, or leak their capability URL.
            csp = (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                "connect-src 'self'; frame-ancestors 'none'; object-src 'none'; "
                "base-uri 'self'; form-action 'self'"
            )
        self.send_header("Content-Security-Policy", csp)
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=(), interest-cohort=()")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        if getattr(self, "_head_only", False):
            # HEAD must still emit a Content-Length and the Vary/Encoding
            # headers so a caching layer's HEAD/GET coherence is correct.
            body_bytes = html.encode()
            _, encoding = _compress_body(body_bytes, "text/html", self.headers.get("Accept-Encoding", ""))
            self.send_header("Content-Length", str(len(body_bytes)))
            if encoding:
                self.send_header("Content-Encoding", encoding)
            self.end_headers()
            return
        # Inject hreflang + OG image + twitter tags for any HTML page missing them
        if cacheable and "/analytics.js" not in html and "</head>" in html:
            html = html.replace(
                "</head>",
                '<script src="/analytics.js" defer></script></head>',
                1,
            )
        if 'hreflang' not in html.lower() and '<link rel="canonical"' in html:
            import re as _reh
            cm = _reh.search(r'<link rel="canonical" href="([^"]+)"', html)
            if cm:
                cu = cm.group(1)
                hb = ('<link rel="alternate" hreflang="en" href="' + cu + '">\n'
                      '<link rel="alternate" hreflang="en-US" href="' + cu + '">\n'
                      '<link rel="alternate" hreflang="x-default" href="' + cu + '">\n')
                html = html.replace('<link rel="canonical"', hb + '<link rel="canonical"', 1)
        if 'og:image' not in html and '<meta property="og:title"' in html:
            import re as _reo
            tm = _reo.search(r'<meta property="og:title" content="([^"]+)"', html)
            dm = _reo.search(r'<meta property="og:description" content="([^"]+)"', html)
            ot = tm.group(1) if tm else ''
            od = dm.group(1) if dm else ''
            ob = ('<meta property="og:image" content="https://sipi.bot/og.png">'
                  '<meta property="og:image:width" content="1200">'
                  '<meta property="og:image:height" content="630">'
                  '<meta property="og:image:alt" content="sipi.bot — The pre-spend firewall for autonomous AI agents">'
                  '<meta property="og:site_name" content="sipi.bot">\n'
                  '<meta name="twitter:card" content="summary_large_image">\n'
                  '<meta name="twitter:title" content="' + ot + '">\n'
                  '<meta name="twitter:description" content="' + od + '">\n'
                  '<meta name="twitter:image" content="https://sipi.bot/og.png">\n')
            html = html.replace('<meta property="og:title"', ob + '<meta property="og:title"', 1)
        body_bytes, encoding = _compress_body(html.encode(), "text/html", self.headers.get("Accept-Encoding", ""))
        self.send_header("Vary", "Accept-Encoding")
        if encoding:
            self.send_header("Content-Encoding", encoding)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def _body(self) -> dict:
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n <= 0:
                return {}
            if n > 65_536:
                self._body_error = "body_too_large"
                return {}
            parsed = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(parsed, dict):
                self._body_error = "invalid_json_object"
                return {}
            return parsed
        except Exception:
            self._body_error = "invalid_json"
            return {}

    def do_OPTIONS(self):
        path = urlparse(self.path).path
        # Control-plane routes only trust the site's own origin; everything
        # else keeps the permissive CORS needed for public read endpoints.
        if path.startswith("/api/") or path.startswith("/admin/"):
            return self._send(204, b"", origin=_TRUSTED_ORIGIN)
        self._send(204, b"")

    def do_GET(self):
        path = urlparse(self.path).path

        # SEO: redirect www to apex
        if 'host' in (h.lower() for h in self.headers.keys()):
            host = self.headers.get('Host', '') or self.headers.get('host', '')
            if host.startswith('www.'):
                target = 'https://' + host[4:] + self.path
                self.send_response(301)
                self.send_header('Location', target)
                # Redirects were bare (Location only) — add the baseline 4
                # security headers so HSTS/transport hardening survives the hop.
                self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("X-Frame-Options", "DENY")
                self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
                self.send_header("Cross-Origin-Opener-Policy", "same-origin")
                self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return


        # Trailing-slash normalization for bare app routes. The site convention
        # is directory URLs for pSEO spokes (/for/crewai/) but bare URLs for app
        # routes (/eval, /badge, /pricing, /dashboard). Both directions leaked:
        # /eval/ 404'd (soft-404 error in GSC) while /for/crewai 404'd. One rule
        # fixes all bare routes now and any added later: if the slashed form has
        # no on-disk directory AND a bare route handles it, 301 to the bare
        # form. pSEO spokes are left untouched because they resolve as dirs.
        if len(path) > 1 and path != "/" and path.endswith("/"):
            import os as _os_slash
            stripped = path.rstrip("/")
            base = _os_slash.path.abspath(_os_slash.path.join(_os_slash.path.dirname(__file__), ".."))
            spoke_dir = _os_slash.path.normpath(_os_slash.path.join(base, stripped.lstrip("/")))
            spoke_dir_exists = (
                spoke_dir.startswith(base + _os_slash.sep)
                and _os_slash.path.isfile(_os_slash.path.join(spoke_dir, "index.html"))
            )
            if stripped in _BARE_ROUTES and not spoke_dir_exists:
                qs = urlparse(self.path).query
                loc = stripped + ("?" + qs if qs else "")
                self.send_response(301)
                self.send_header("Location", loc)
                self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("X-Frame-Options", "DENY")
                self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
                self.send_header("Cross-Origin-Opener-Policy", "same-origin")
                self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
        # ── pSEO static pages ──────────────────────────
        try_pseo = self._serve_pseo(path)
        if try_pseo:
            return
        # Research Data hub (Dataset Search)
        if path == "/data":
            try:
                import os as _os
                base = _os.path.abspath(_os.path.dirname(__file__))
                fp = _os.path.join(base, "data/index.html")
                with open(fp, encoding="utf-8") as fh:
                    return self._html(fh.read())
            except Exception:
                pass
        if path == "/data/feed.json":
            try:
                import os as _os
                base = _os.path.abspath(_os.path.dirname(__file__))
                fp = _os.path.join(base, "data/feed.json")
                with open(fp, encoding="utf-8") as fh:
                    return self._send(200, fh.read().encode(), "application/json")
            except Exception:
                pass
        # /index.html served the homepage byte-for-byte, so the site had two URLs
        # for one page. Redirect it instead — same treatment /learn got when its
        # bare root 404'd. Mirrors the www->apex hop above, including the baseline
        # security headers so the hardening survives the redirect.
        if path == "/index.html":
            self.send_response(301)
            self.send_header("Location", "/")
            self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path == "/":
            return self._html(templates.landing_page_html())
        if path == "/dashboard":
            # The dashboard temporarily holds the customer's API key in
            # sessionStorage. Keep it non-cacheable and first-party-only so a
            # consented analytics SDK can never share its JavaScript context.
            return self._html(templates.dashboard_html(), cacheable=False)
        if path == "/health":
            return self._json(200, {"ok": True, "service": "sipi.bot", "version": __version__},
                              noindex=True)
        # IndexNow key file (instant re-crawling) — content must be just the key,
        # not the filename. IndexNow reads the body of the .txt file and expects
        # the raw key string (e.g. "9769ace59182381fe1af49982d9b58a9").
        if path in ("/9769ace59182381fe1af49982d9b58a9.txt", "/9769ace5.txt"):
            key = path.split("/")[-1].rsplit(".", 1)[0]
            return self._send(200, key.encode(), "text/plain")

        if path == "/BingSiteAuth.xml":
            xml = ('<?xml version="1.0"?>\n<users>\n\t<user>'
                   'FA4E122745948F0CAD16959F59DDCB85</user>\n</users>')
            return self._send(200, xml.encode(), "application/xml")
        if path == "/.well-known/agent-card.json":
            return self._json(200, agent_card())
        if path == "/.well-known/security.txt":
            sec = (
                "Contact: mailto:security@sipi.bot\n"
                "Expires: 2027-07-20T00:00:00Z\n"
                "Preferred-Languages: en\n"
                "Canonical: https://sipi.bot/.well-known/security.txt\n"
                "Policy: https://sipi.bot/privacy\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=86400")
            self.send_header("Content-Length", str(len(sec)))
            self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
            self.end_headers()
            if not getattr(self, "_head_only", False):
                self.wfile.write(sec.encode())
                self.wfile.flush()
            return
        if path == "/openapi.json":
            # AI-agent discoverability: OpenAPI 3.0 spec describing the public API.
            from . import openapi_spec
            return self._json(200, openapi_spec.SPEC, noindex=True)
        if path == "/eval":
            if os.path.exists(_EVAL_REPORT_PATH):
                with open(_EVAL_REPORT_PATH) as f:
                    return self._json(200, json.load(f), noindex=True)
            return self._json(200, {"status": "not_run_yet",
                                    "hint": "run: python -m spendfirewall.eval.run_eval"},
                              noindex=True)
        # ── Embeddable SVG badge endpoint ──
        if path == "/api/badge/firewall-status":
            return self._badge_svg()
        # ── Badge showcase page ──
        if path == "/badge":
            return self._html(templates.badge_page_html())
        # ── Sipi Spend-Firewall Benchmark (SSFB): branded, live-verifiable AEO hub ──
        if path == "/benchmark":
            return self._html(self._benchmark_hub(), cacheable=True)
        if path in ("/benchmark/embed", "/benchmark/embed/"):
            return self._html(self._benchmark_embed(), cacheable=True)
        if path == "/api/v1/benchmark/live":
            return self._benchmark_live()
        if path == "/api/badge/accuracy":
            return self._accuracy_badge_svg()
        if path == "/api/stats":
            access = self._control_auth()
            if not access:
                return
            return self._json(
                200,
                store.get_stats(access["agent_id"], scoped=not access["admin"]),
                noindex=True,
                origin=_TRUSTED_ORIGIN,
            )
        if path == "/api/transactions":
            access = self._control_auth()
            if not access:
                return
            return self._json(
                200,
                store.recent_transactions(
                    50, access["agent_id"], scoped=not access["admin"]
                ),
                noindex=True,
                origin=_TRUSTED_ORIGIN,
            )
        if path == "/api/approvals":
            access = self._control_auth()
            if not access:
                return
            return self._json(
                200,
                store.list_approvals(
                    "pending", access["agent_id"], scoped=not access["admin"]
                ),
                noindex=True,
                origin=_TRUSTED_ORIGIN,
            )
        if path == "/api/rules":
            access = self._control_auth()
            if not access:
                return
            return self._json(
                200,
                store.list_rules(
                    access["agent_id"], scoped=not access["admin"]
                ),
                noindex=True,
                origin=_TRUSTED_ORIGIN,
            )
        if path == "/api/agents":
            if not self._require_admin():
                return
            return self._json(
                200, store.list_agents(), noindex=True, origin=_TRUSTED_ORIGIN
            )

        # ── MCP (Model Context Protocol) JSON-RPC endpoint ──
        if path == "/api/mcp":
            _mcp_tools = [
                {"name": "evaluate_spend", "description": "Check whether an autonomous agent is allowed to make a purchase BEFORE spending. Returns APPROVED, BLOCKED, or FLAGGED.",
                 "inputSchema": {"type": "object", "properties": {"amount": {"type": "number"}, "merchant": {"type": "string"}, "category": {"type": "string"}, "description": {"type": "string"}}, "required": ["amount"]}},
                {"name": "add_spend_rule", "description": "Add a rule to the authenticated API key's isolated workspace.",
                 "inputSchema": {"type": "object", "properties": {"rule_type": {"type": "string"}, "params": {"type": "object"}, "action": {"type": "string"}, "priority": {"type": "integer"}, "label": {"type": "string"}}, "required": ["rule_type", "params"]}},
                {"name": "firewall_status", "description": "Get private firewall stats for the authenticated API key.",
                 "inputSchema": {"type": "object"}},
            ]
            _mcp_server_info = {"name": "sipibot-mcp", "version": "1.0.0"}
            _mcp_capabilities = {"tools": {"listChanged": False}, "resources": {}, "prompts": {}}
            if self.command == "GET":
                return self._json(200, {
                    "jsonrpc": "2.0",
                    "serverInfo": _mcp_server_info,
                    "capabilities": _mcp_capabilities,
                    "protocolVersion": "2024-11-05",
                    "tools": [{"name": t["name"], "description": t["description"]} for t in _mcp_tools],
                    "_meta": {"homepage": "https://sipi.bot", "contact": "support@sipi.bot",
                              "install": {"claude_desktop": "npx mcp-remote https://sipi.bot/api/mcp",
                                          "cursor": "https://sipi.bot/api/mcp"}}
                })
            # POST: JSON-RPC
            try:
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode() or '{}')
            except Exception:
                body = {}
            rpc_id = body.get("id")
            method = body.get("method", "")
            if method == "initialize":
                return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {
                    "protocolVersion": "2024-11-05", "capabilities": _mcp_capabilities, "serverInfo": _mcp_server_info}})
            if method == "notifications/initialized":
                # MCP handshake ack — was bare send_response(202) with ZERO headers.
                # Use _send so it inherits the full security header set (HSTS/XCTO/
                # XFO/RP/CSP/PP) consistent with every other response path.
                return self._send(202, b"")
            if method == "tools/list":
                return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": _mcp_tools}})
            if method == "tools/call":
                params = body.get("params", {})
                tool_name = params.get("name", "")
                args = params.get("arguments", {})
                tool = next((t for t in _mcp_tools if t["name"] == tool_name), None)
                if not tool:
                    return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {
                        "content": [{"type": "text", "text": f"Unknown tool: {tool_name}. Available: {', '.join(t['name'] for t in _mcp_tools)}"}], "isError": True}})
                # For evaluate_spend, actually run the evaluation
                if tool_name == "evaluate_spend":
                    agent_id = None
                    auth_context = None
                    paid_key = None
                    auth = self.headers.get("Authorization", "")
                    if auth:
                        if not auth.startswith("Bearer ") or not auth[7:].strip():
                            return self._json(401, {"error": "invalid_api_key"})
                        paid_key = auth[7:].strip()
                        if _is_admin_token(paid_key):
                            auth_context = {"source": "admin"}
                        else:
                            agent_id, auth_context = _resolve_api_key(paid_key)
                            if not auth_context:
                                return self._json(401, {"error": "invalid_api_key"})
                    transaction, transaction_error = _validated_transaction_input(args)
                    if transaction_error:
                        return self._json(200, {
                            "jsonrpc": "2.0",
                            "id": rpc_id,
                            "result": {
                                "content": [
                                    {"type": "text", "text": transaction_error}
                                ],
                                "isError": True,
                            },
                        })
                    result = core.evaluate_transaction(
                        **transaction, agent_id=agent_id
                    )
                    if auth_context and auth_context["source"] == "billing":
                        billing.record_key_use(paid_key, result.get("decision", "UNKNOWN"))
                    return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {
                        "content": [{"type": "text", "text": json.dumps(result)}]}})
                if tool_name == "firewall_status":
                    access = self._control_auth()
                    if not access:
                        return
                    stats = store.get_stats(
                        access["agent_id"], scoped=not access["admin"]
                    )
                    return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {
                        "content": [{"type": "text", "text": json.dumps(stats)}]}})
                if tool_name == "add_spend_rule":
                    access = self._control_auth()
                    if not access:
                        return
                    rule_input, rule_error = _validated_rule_input(args)
                    if rule_error:
                        return self._json(200, {
                            "jsonrpc": "2.0",
                            "id": rpc_id,
                            "result": {
                                "content": [{"type": "text", "text": rule_error}],
                                "isError": True,
                            },
                        })
                    created = store.add_rule(
                        **rule_input,
                        agent_id=None if access["admin"] else access["agent_id"],
                    )
                    return self._json(200, {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "result": {
                            "content": [
                                {"type": "text", "text": json.dumps(created)}
                            ]
                        },
                    })
            if method == "ping":
                return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {}})
            return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

        # ── A2A (Agent-to-Agent) JSON-RPC endpoint ──
        if path == "/api/a2a":
            _agent_card = {
                "name": "sipi.bot Spend Firewall",
                "description": "The spend firewall for autonomous AI agents. Evaluate every transaction against configurable rules before spending.",
                "url": "https://sipi.bot/api/a2a",
                "version": "1.0.0",
                "capabilities": {"streaming": False, "pushNotifications": False},
                "authentication": {"type": "none"},
                "skills": [{"id": t["name"], "name": t["name"], "description": t["description"]} for t in [
                    {"name": "evaluate_spend", "description": "Check if a purchase is allowed before spending."},
                    {"name": "firewall_status", "description": "Get current firewall stats."},
                ]]
            }
            if self.command == "GET":
                return self._json(200, _agent_card)
            try:
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode() or '{}')
            except Exception:
                body = {}
            rpc_id = body.get("id")
            method = body.get("method", "")
            if method in ("agent/info", "rpc.discover", "agent/card"):
                return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": _agent_card})
            return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {"agent": _agent_card["name"], "skills": _agent_card["skills"]}})

        # ── NLWeb endpoint ──
        if path == "/api/nlweb":
            query = parse_qs(urlparse(self.path).query).get("query", [""])[0]
            _nlweb_items = [
                {"@type": "Question", "name": "What is sipi.bot?", "acceptedAnswer": "The spend firewall for autonomous AI agents. Evaluate every transaction before spending.", "url": "https://sipi.bot/"},
                {"@type": "Question", "name": "How does the spend firewall work?", "acceptedAnswer": "Agents call evaluate_spend before any purchase. The firewall checks rules and returns APPROVED, BLOCKED, or FLAGGED.", "url": "https://sipi.bot/"},
            ]
            if query:
                q = query.lower()
                _nlweb_items = [i for i in _nlweb_items if q in i["name"].lower() or q in i["acceptedAnswer"].lower()]
            return self._json(200, {"@context": "https://schema.org", "@type": "ItemList", "name": "sipi.bot Knowledge Base", "numberOfItems": len(_nlweb_items), "itemListElement": _nlweb_items})
        if path == "/pricing":
            return self._html(templates.pricing_html())
        if path == "/sitemap-html":
            return self._html(templates.sitemap_html())
        if path == "/masterclass":
            return self._html(templates.masterclass_html())
        if path in ("/blog", "/blog/"):
            return self._html(templates.blog_page_html())
        if path == "/about":
            return self._html(templates.doc_page_html(
                "About", "/about",
                "sipi.bot is the spend firewall for autonomous AI agents — evaluate every transaction against your rules and get approve, block, or flag with a deterministic rules check.",
                templates.ABOUT_BODY))
        if path == "/dream100":
            return self._html(templates.doc_page_html(
                "Dream 100", "/dream100",
                "The communities, protocols, and platforms where agent-builders already gather — and how sipi.bot serves them first.",
                templates.DREAM100_BODY))
        if path == "/content-calendar":
            return self._html(templates.doc_page_html(
                "Content Calendar", "/content-calendar",
                "sipi.bot's publishing schedule: weekly eval reports, monthly integration guides, quarterly agent-spend benchmarks, and ongoing distribution across GitHub, PyPI, and MCP.",
                templates.CALENDAR_BODY))
        if path == "/privacy":
            return self._html(templates.doc_page_html(
                "Privacy Policy", "/privacy",
                "How sipi.bot handles transaction metadata, account data, and analytics. We are a decision layer — we never store card numbers.",
                templates.PRIVACY_BODY))
        if path == "/terms":
            return self._html(templates.doc_page_html(
                "Terms of Service", "/terms",
                "Terms for using sipi.bot, the spend firewall for autonomous AI agents, including the rule-integrity guarantee.",
                templates.TERMS_BODY))
        if path == "/billing/status":
            return self._json(200, billing.status())
        if path.startswith("/checkout/"):
            plan = path.rsplit("/", 1)[-1]
            query = parse_qs(urlparse(self.path).query)
            analytics_id = query.get("aid", [None])[0]
            source_cta = query.get("source", ["direct"])[0]
            try:
                url = billing.create_checkout_session(
                    plan,
                    analytics_id=analytics_id,
                    source_cta=source_cta,
                )
            except Exception as e:
                billing.capture_checkout_failure(
                    plan,
                    type(e).__name__,
                    analytics_id,
                )
                return self._json(400, {"error": str(e)})
            self.send_response(302)
            self.send_header("Location", url)
            self.send_header("Content-Length", "0")
            self.send_header("X-Robots-Tag", "noindex, nofollow")
            # Checkout redirect was missing the baseline 4 security headers.
            self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
            self.end_headers()
            return
        if path.startswith("/keys/"):
            sess = path.rsplit("/", 1)[-1]
            rec = billing.key_for_session(sess)
            billing.capture_key_delivery(rec)
            return self._html(templates.key_success_html(rec), cacheable=False)
        if path == "/v1/activity":
            return self._json(
                410,
                {"error": "activity_stream_retired", "use": "/api/transactions"},
                noindex=True,
                origin=_TRUSTED_ORIGIN,
            )
        # Static files from public/ (sitemap.xml, robots.txt, llms.txt, pSEO
        # pages written by the growth engine). Served last, before 404.
        if path == "/unsubscribe" or path == "/api/unsubscribe":
            email = parse_qs(urlparse(self.path).query).get("email", [""])[0]
            email = drip.normalize_email(email) or ""
            html = "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Unsubscribe - sipi.bot</title>"
            html += "<style>body{background:#0a0a0a;color:#ccc;font-family:-apple-system,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:20px}.card{background:#111;border:1px solid #1a1a1a;border-radius:16px;padding:40px;max-width:400px;text-align:center}h1{color:#fff;margin:0 0 8px;font-size:22px}p{color:#888;margin:0 0 24px;font-size:14px;line-height:1.6}.btn{background:#00d4aa;color:#0a0a0a;border:none;padding:12px 32px;border-radius:8px;font-weight:700;font-size:14px;cursor:pointer}.btn:hover{opacity:.9}</style></head><body>"
            html += "<div class='card'>"
            if email:
                # Email is HTML-escaped for display and read client-side from
                # location.search for the unsubscribe call (not server-
                # interpolated into inline JS) to avoid reflected XSS — a raw
                # query-param value can otherwise break out of the HTML
                # attribute/JS string and inject arbitrary script.
                html += "<h1>Unsubscribe</h1>"
                html += "<p>We'll stop sending emails to <strong style='color:#fff'>" + _html.escape(email) + "</strong>.</p>"
                html += "<button class='btn' id='ubtn'>Confirm unsubscribe</button>"
                html += "<p id='ustatus' style='display:none;color:#00d4aa;margin-top:16px'></p>"
                html += "<script>document.getElementById('ubtn').addEventListener('click',function(){var email=new URLSearchParams(location.search).get('email')||'';fetch('/unsubscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email})}).then(function(r){return r.json()}).then(function(d){if(d.ok){document.getElementById('ustatus').style.display='block';document.getElementById('ustatus').textContent='Unsubscribed.';document.getElementById('ubtn').style.display='none';}})});</script>"
            else:
                html += "<h1>Unsubscribe</h1>"
                html += "<p>Use the link from any email to unsubscribe.</p>"
            html += "</div></body></html>"
            return self._html(html)

        # Static files from public/ (served before cron/drip)
        if self._serve_static(path):
            return

        # Drip delivery is a state-changing operation and is POST-only so its
        # credential never leaks into URLs, access logs, or browser history.
        if path == "/cron/drip":
            return self._json(405, {"ok": False, "error": "method_not_allowed"})

        return self._json(404, {"error": "not_found"})

    def _send_embed(self, body: bytes, ctype: str = "text/html"):
        """Send a response with embed-safe framing headers.

        Mirrors _send() but allows cross-origin iframing. Used for
        /embed/* widget farm pages (portfolio-network, calculators)."""
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "ALLOWALL")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Strict-Transport-Security",
                         "max-age=63072000; includeSubDomains; preload")
        self.send_header("Content-Security-Policy",
                         "frame-ancestors *; default-src 'self'; "
                         "script-src 'self' 'unsafe-inline'; "
                         "style-src 'self' 'unsafe-inline'; "
                         "img-src 'self' data: https:; connect-src 'self'; "
                         "font-src 'self'")
        self.send_header("Permissions-Policy",
                         "camera=(), microphone=(), geolocation=(), "
                         "payment=(), usb=(), browsing-topics=(), "
                         "interest-cohort=()")
        self.close_connection = True
        self.end_headers()
        if getattr(self, "_head_only", False):
            return
        self.wfile.write(body)
        self.wfile.flush()

    def _badge_svg(self):
        """Return a dynamic SVG badge showing live firewall stats.
        
        Embeddable as <img src="https://sipi.bot/api/badge/firewall-status">
        on any site — READMEs, docs, landing pages. Each embed is a permanent
        backlink to sipi.bot. The Codecov/WakaTime distribution model.
        """
        try:
            stats = core.status()
        except Exception:
            stats = {}
        checked = stats.get("checked_today", 0)
        blocked = stats.get("blocked_today", 0)
        approved = stats.get("approved_today", 0)
        flagged = stats.get("flagged_today", 0)
        total_checked = stats.get("checked_total", checked)
        
        # Read query params for variant
        from urllib.parse import parse_qs
        qs = parse_qs(urlparse(self.path).query)
        variant = (qs.get("style", ["dark"])[0] or "dark").lower()
        width = min(int(qs.get("w", ["760"])[0] or 760), 1200)
        
        # Format numbers compactly
        def fmt(n):
            if n >= 1_000_000:
                return f"{n/1_000_000:.1f}M"
            if n >= 10_000:
                return f"{n/1000:.0f}k"
            if n >= 1_000:
                return f"{n/1000:.1f}k"
            return str(n)
        
        checked_str = fmt(checked)
        blocked_str = fmt(blocked)
        total_str = fmt(total_checked)
        
        if variant == "flat":
            # Minimal flat badge for README (single line)
            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="20" role="img" aria-label="Protected by sipi.bot — {checked_str} checks today">
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#0a0a0a"/>
    <stop offset="100%" stop-color="#121316"/>
  </linearGradient>
  <rect width="280" height="20" rx="10" fill="url(#bg)"/>
  <rect x="150" width="130" height="20" rx="10" fill="#00d4aa" fill-opacity="0.12"/>
  <text x="10" y="14" fill="#8a8d96" font-family="SF Mono,ui-monospace,monospace" font-size="11">Protected by sipi.bot</text>
  <text x="215" y="14" fill="#00d4aa" font-family="SF Mono,ui-monospace,monospace" font-size="10" text-anchor="middle">{checked_str} today</text>
</svg>'''
        elif variant == "shield":
            # Shields.io-style badge
            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="20">
  <linearGradient id="left" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#121316"/>
    <stop offset="100%" stop-color="#0a0a0a"/>
  </linearGradient>
  <rect width="180" height="20" rx="4" fill="url(#left)"/>
  <rect x="180" width="100" height="20" rx="4" fill="#00d4aa" fill-opacity="0.15"/>
  <text x="10" y="14" fill="#8a8d96" font-family="SF Mono,ui-monospace,monospace" font-size="10">Protected by sipi.bot</text>
  <text x="230" y="14" fill="#00d4aa" font-family="SF Mono,ui-monospace,monospace" font-size="10" text-anchor="middle">€0 lost</text>
</svg>'''
        else:
            # Full dark badge with live stats
            # Calculate dynamic heights based on width
            h = 140
            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" role="img" aria-label="Protected by sipi.bot — {checked_str} checks today, {blocked_str} blocked">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#121316"/>
      <stop offset="100%" stop-color="#0a0a0a"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00d4aa"/>
      <stop offset="100%" stop-color="#00b894"/>
    </linearGradient>
  </defs>
  <rect width="{width}" height="{h}" rx="12" fill="url(#bgGrad)" stroke="#1a1c20" stroke-width="1"/>
  <!-- Shield icon -->
  <path d="M24,24 L24,42 L60,58 L96,42 L96,24 L60,14 Z" fill="none" stroke="#00d4aa" stroke-width="2" opacity="0.7"/>
  <path d="M60,14 L96,24 L96,42 L60,58 L24,42 L24,24 Z" fill="#00d4aa" fill-opacity="0.08"/>
  <text x="72" y="40" fill="#00d4aa" font-family="SF Mono,ui-monospace,monospace" font-size="16" font-weight="700" text-anchor="middle">SPEND</text>
  <text x="72" y="54" fill="#00d4aa" font-family="SF Mono,ui-monospace,monospace" font-size="9" text-anchor="middle">FIREWALL</text>
  <!-- Main label -->
  <text x="120" y="28" fill="#e8e8ea" font-family="-apple-system,BlinkMacSystemFont,Inter,sans-serif" font-size="14" font-weight="700">sipi.bot</text>
  <text x="120" y="42" fill="#8a8d96" font-family="-apple-system,Inter,sans-serif" font-size="11">Agent spend firewall — active and enforcing</text>
  <!-- Stats row -->
  <rect x="120" y="56" width="{width-140}" height="1" fill="#23242a"/>
  <!-- Stat: Checks today -->
  <text x="120" y="76" fill="#8a8d96" font-family="SF Mono,ui-monospace,monospace" font-size="10">Checks today</text>
  <text x="120" y="92" fill="#e8e8ea" font-family="SF Mono,ui-monospace,monospace" font-size="18" font-weight="700">{checked_str}</text>
  <!-- Stat: Blocked -->
  <text x="260" y="76" fill="#8a8d96" font-family="SF Mono,ui-monospace,monospace" font-size="10">Blocked</text>
  <text x="260" y="92" fill="#ff5470" font-family="SF Mono,ui-monospace,monospace" font-size="18" font-weight="700">{blocked_str}</text>
  <!-- Stat: Approved -->
  <text x="400" y="76" fill="#8a8d96" font-family="SF Mono,ui-monospace,monospace" font-size="10">Approved</text>
  <text x="400" y="92" fill="#00d4aa" font-family="SF Mono,ui-monospace,monospace" font-size="18" font-weight="700">{fmt(approved)}</text>
  <!-- Stat: Flagged -->
  <text x="540" y="76" fill="#8a8d96" font-family="SF Mono,ui-monospace,monospace" font-size="10">Flagged</text>
  <text x="540" y="92" fill="#ffb020" font-family="SF Mono,ui-monospace,monospace" font-size="18" font-weight="700">{fmt(flagged)}</text>
  <!-- Total -->
  <text x="680" y="76" fill="#8a8d96" font-family="SF Mono,ui-monospace,monospace" font-size="10">Total all-time</text>
  <text x="680" y="92" fill="#e8e8ea" font-family="SF Mono,ui-monospace,monospace" font-size="18" font-weight="700">{total_str}</text>
  <!-- Verdict line -->
  <text x="120" y="118" fill="#00d4aa" font-family="SF Mono,ui-monospace,monospace" font-size="9">DECISION: APPROVED · BLOCKED · FLAGGED — deterministic decision path</text>
  <!-- CTA -->
  <text x="{width-16}" y="118" fill="#8a8d96" font-family="SF Mono,ui-monospace,monospace" font-size="8" text-anchor="end">sipi.bot/badge</text>
</svg>'''
        
        body = svg.encode()
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # Short cache — badge shows live stats (30s CDN, 60s browser)
        self.send_header("Cache-Control", "public, max-age=30, s-maxage=60")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.close_connection = True
        self.end_headers()
        if getattr(self, "_head_only", False):
            return
        self.wfile.write(body)
        self.wfile.flush()

    # ── Sipi Spend-Firewall Benchmark (SSFB) handlers ─────────────
    def _load_eval_report(self):
        """Load the shipped eval_report.json; return None if absent."""
        try:
            if os.path.exists(_EVAL_REPORT_PATH):
                with open(_EVAL_REPORT_PATH) as f:
                    return json.load(f)
        except (OSError, ValueError):
            pass
        return None

    def _benchmark_hub(self) -> str:
        """Render the SSFB hub from eval_report.json (the shipped ground truth)."""
        from . import benchmark as _bm
        report = self._load_eval_report() or {}
        return _bm.benchmark_hub_html(
            total=report.get("total", 0),
            passed=report.get("passed", 0),
            accuracy=report.get("accuracy_pct", 0.0),
            by_category=report.get("by_category", {}),
            generated_at=report.get("generated_at", "2026-07-27T00:00:00+00:00"),
        )

    def _benchmark_embed(self) -> str:
        """Embed/showcase page with copy-paste badge snippets (Influence tier)."""
        from . import benchmark_embed as _be
        report = self._load_eval_report() or {}
        return _be.embed_page_html(
            total=report.get("total", 0),
            passed=report.get("passed", 0),
            accuracy=report.get("accuracy_pct", 0.0),
        )

    def _benchmark_live(self):
        """Re-run the real eval engine live and return JSON. The real-time-
        retrieval AEO asset — an answer engine hits this to verify the claim."""
        from . import benchmark as _bm
        try:
            from .eval.run_eval import run as _run_eval
            report = _run_eval()
            payload = _bm.live_payload(report)
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            # Real-time asset: keep fresh but cacheable so it survives a spike.
            self.send_header("Cache-Control", "public, max-age=30, s-maxage=60")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("X-Robots-Tag", "index, follow")
            self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if not getattr(self, "_head_only", False):
                self.wfile.write(body)
                self.wfile.flush()
        except Exception as e:  # never let the live endpoint take down a request
            return self._json(200, {
                "benchmark": "Sipi Spend-Firewall Benchmark (SSFB)",
                "verified_live": False,
                "error": "eval_unavailable",
                "detail": str(e)[:200],
                "fallback": "https://sipi.bot/benchmark/",
            }, noindex=False, origin="*")

    def _accuracy_badge_svg(self):
        """Embeddable live SSFB accuracy badge. Earns backlinks/consensus when
        embedded in READMEs, docs, and comparison pages."""
        from . import benchmark as _bm
        report = self._load_eval_report() or {}
        body = _bm.accuracy_badge_svg(report).encode()
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=60, s-maxage=120")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(body)
            self.wfile.flush()

    def _serve_static(self, path: str) -> bool:
        """Serve a file from the public/ dir if it exists. Path-traversal safe."""
        import mimetypes
        root = os.environ.get("PUBLIC_DIR", os.path.join(os.getcwd(), "public"))
        rel = path.lstrip("/") or "index.html"
        if rel.endswith("/"):
            rel += "index.html"
        target = os.path.normpath(os.path.join(root, rel))
        # containment check: must stay under root
        if not target.startswith(os.path.abspath(root) + os.sep) and target != os.path.abspath(root):
            return False
        if not os.path.isfile(target):
            # try /foo -> /foo/index.html (pSEO cluster pages)
            alt = os.path.normpath(os.path.join(root, rel, "index.html"))
            if os.path.isfile(alt):
                target = alt
            else:
                return False
        ctype = mimetypes.guess_type(target)[0] or "application/octet-stream"
        try:
            with open(target, "rb") as f:
                data = f.read()
        except OSError:
            return False
        # Embed widget farm — cross-origin iframing allowed
        if path.startswith("/embed/"):
            self._send_embed(data, ctype)
        elif ctype.startswith("text/html"):
            self._html(data.decode("utf-8"))
        else:
            self._send(200, data, ctype)
        return True

    def _sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        # Security headers — bring SSE up to the same baseline as _send/_html.
        self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' https://js.stripe.com https://eu.i.posthog.com https://eu-assets.i.posthog.com https://eu.posthog.com https://checkout.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://eu.i.posthog.com https://eu-assets.i.posthog.com https://sipi.bot; frame-ancestors 'none'; object-src 'none'; base-uri 'self'; frame-src https://js.stripe.com https://checkout.stripe.com")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=(), interest-cohort=()")
        self.end_headers()
        q: queue.Queue = queue.Queue()
        with _SUB_LOCK:
            _SUBSCRIBERS.append(q)
        try:
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            while True:
                try:
                    data = q.get(timeout=15)
                    self.wfile.write(f"data: {data}\n\n".encode())
                except queue.Empty:
                    self.wfile.write(b"data: ping\n\n")
                self.wfile.flush()
        except Exception:
            pass
        finally:
            with _SUB_LOCK:
                if q in _SUBSCRIBERS:
                    _SUBSCRIBERS.remove(q)

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/rules/"):
            access = self._control_auth()
            if not access:
                return
            rid = path.rsplit("/", 1)[-1]
            deleted = (
                store.delete_rule(rid)
                if access["admin"]
                else store.delete_rule_for_agent(rid, access["agent_id"])
            )
            return self._json(
                200, {"deleted": deleted}, noindex=True, origin=_TRUSTED_ORIGIN
            )
        return self._json(404, {"error": "not_found"})

    
    def _serve_pseo(self, path):
        """Serve pSEO static HTML pages from vs/ for/ learn/ integrations/ subdirs.

        Returns True when a page was served (so do_GET stops routing),
        None/False on a miss. NB: _html() returns None — never return its
        result directly or do_GET falls through and appends a second 404
        response to the body (the 82-page corruption bug)."""
        import os
        for prefix in ("/compare/", "/vs/", "/for/", "/learn/", "/integrations/", "/glossary/", "/use-cases/", "/faq/", "/alternatives-to/", "/benchmarks/", "/tutorials/", "/policies/", "/limits/", "/best/", "/how-to/", "/templates/", "/cost-of/"):
            # Match "/learn/foo" and also the bare section root "/learn". The bare
            # form used to fall through to a 404 because it does not start with
            # "/learn/", so /learn 404'd while /learn/ served learn/index.html —
            # and a breadcrumb on every /learn/* page pointed at the bare form.
            # Sections with no index.html (e.g. /compare) still 404, unchanged.
            if path.startswith(prefix) or path == prefix.rstrip("/"):
                if path == prefix.rstrip("/"):
                    path = prefix
                # /data/ files live inside the spendfirewall package; others at project root
                if prefix == "/data/":
                    base = os.path.abspath(os.path.dirname(__file__))
                else:
                    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                filepath = os.path.join(base, path.lstrip("/"), "index.html")
                filepath = os.path.abspath(os.path.normpath(filepath))
                # containment: never follow a traversal outside the app root
                if not filepath.startswith(base + os.sep):
                    return None
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, encoding="utf-8") as fh:
                            html = fh.read()
                            # Inject hreflang + OG image + twitter tags for pSEO pages missing them
                            if 'hreflang' not in html.lower() and '<link rel="canonical"' in html:
                                canonical_url = ''
                                import re as _re
                                cm = _re.search(r'<link rel="canonical" href="([^"]+)"', html)
                                if cm:
                                    canonical_url = cm.group(1)
                                hreflang_block = (
                                    '<link rel="alternate" hreflang="en" href="' + canonical_url + '">\n'
                                    '<link rel="alternate" hreflang="en-US" href="' + canonical_url + '">\n'
                                    '<link rel="alternate" hreflang="x-default" href="' + canonical_url + '">\n'
                                )
                                html = html.replace('<link rel="canonical"', hreflang_block + '<link rel="canonical"')
                            if 'og:image' not in html and '<meta property="og:title"' in html:
                                og_title = ''
                                og_desc = ''
                                import re as _re2
                                tm = _re2.search(r'<meta property="og:title" content="([^"]+)"', html)
                                dm = _re2.search(r'<meta property="og:description" content="([^"]+)"', html)
                                if tm: og_title = tm.group(1)
                                if dm: og_desc = dm.group(1)
                                og_image_block = (
                                    '<meta property="og:image" content="https://sipi.bot/og.png">'
                                    '<meta property="og:image:width" content="1200">'
                                    '<meta property="og:image:height" content="630">'
                                    '<meta property="og:image:alt" content="sipi.bot — The pre-spend firewall for autonomous AI agents">'
                                    '<meta property="og:site_name" content="sipi.bot">\n'
                                    '<meta name="twitter:card" content="summary_large_image">\n'
                                    '<meta name="twitter:title" content="' + og_title + '">\n'
                                    '<meta name="twitter:description" content="' + og_desc + '">\n'
                                    '<meta name="twitter:image" content="https://sipi.bot/og.png">\n'
                                )
                                html = html.replace('<meta property="og:title"', og_image_block + '<meta property="og:title"')
                            if 'twitter:image' not in html and 'twitter:card' not in html:
                                # Twitter card was already added above with og:image;
                                # if somehow missing entirely, inject before </head>
                                pass
                            # Internal-link graph boost: inject a "Related" block of
                            # cross-links into every pSEO page. pSEO spokes were
                            # near-orphaned from the homepage (1 in-link each), so
                            # link equity and crawl discovery were thin. This block
                            # adds same-silo siblings + the key hubs, computed from
                            # the live sitemap so it never drifts. Idempotent: only
                            # injected once (guarded by a sentinel comment).
                            if 'data-related-injected' not in html and '</body>' in html:
                                try:
                                    html = _inject_related_links(html, path)
                                except Exception:
                                    pass
                            # Mobile nav: 0 of the baked pSEO pages had a
                            # hamburger menu, so on phones their nav links
                            # wrapped/overflowed with no path back to Home /
                            # FAQ / How-it-works. Inject the same working
                            # menu the landing page ships. Idempotent.
                            if 'class="nav-toggle"' not in html and '<body' in html:
                                try:
                                    html = _inject_mobile_nav(html)
                                except Exception:
                                    pass
                            self._html(html)
                            return True
                    except Exception:
                        pass
                return None
        return None

    def do_POST(self):
        path = urlparse(self.path).path

        # MCP, A2A, NLWeb POST routes — delegate to do_GET which handles JSON-RPC
        if path in ("/api/mcp", "/api/a2a", "/api/nlweb"):
            try:
                if int(self.headers.get("Content-Length", 0)) > 65_536:
                    return self._json(413, {"error": "body_too_large"})
            except (TypeError, ValueError):
                return self._json(400, {"error": "invalid_content_length"})
            self.command = "POST"
            return self.do_GET()

        # Stripe webhook must read the RAW body once (before _body parses it)
        # for signature verification.
        if path == "/webhooks/stripe":
            try:
                n = int(self.headers.get("Content-Length", 0))
                if n < 0 or n > 1_048_576:
                    return self._json(413, {"error": "body_too_large"})
                raw = self.rfile.read(n) if n > 0 else b"{}"
            except Exception:
                raw = b"{}"
            sig = self.headers.get("Stripe-Signature", "")
            try:
                result = billing.handle_webhook(raw, sig)
            except Exception as e:
                return self._json(400, {"error": str(e)})
            return self._json(200, result)

        body = self._body()
        body_error = getattr(self, "_body_error", "")
        if body_error:
            code = 413 if body_error == "body_too_large" else 400
            return self._json(code, {"error": body_error})

        if path == "/v1/transactions/evaluate":
            if not self._check_rate("evaluate"):
                return self._json(429, {"error": "rate_limited", "retry_after": 60})
            # Auth is optional in free/self-host mode. If an Authorization
            # header is supplied, it must resolve; never silently downgrade an
            # invalid paid key to anonymous behavior.
            agent_id = None
            auth_context = None
            paid_key = None
            auth = self.headers.get("Authorization", "")
            if auth:
                if not auth.startswith("Bearer ") or not auth[7:].strip():
                    return self._json(401, {"error": "invalid_api_key"})
                paid_key = auth[7:].strip()
                if _is_admin_token(paid_key):
                    auth_context = {"source": "admin"}
                else:
                    agent_id, auth_context = _resolve_api_key(paid_key)
                    if not auth_context:
                        return self._json(401, {"error": "invalid_api_key"})
            transaction, transaction_error = _validated_transaction_input(body)
            if transaction_error:
                return self._json(400, {"error": transaction_error})
            try:
                result = core.evaluate_transaction(
                    **transaction,
                    agent_id=agent_id,
                )
            except Exception as e:
                return self._json(400, {"error": str(e)})
            if auth_context and auth_context["source"] == "billing":
                billing.record_key_use(paid_key, result.get("decision", "UNKNOWN"))
            _broadcast({"type": "transaction", **result})
            return self._json(200, result)

        if path == "/api/rules":
            access = self._control_auth()
            if not access:
                return
            rule_input, rule_error = _validated_rule_input(body)
            if rule_error:
                return self._json(
                    400,
                    {"error": rule_error},
                    noindex=True,
                    origin=_TRUSTED_ORIGIN,
                )
            r = store.add_rule(
                **rule_input,
                agent_id=None if access["admin"] else access["agent_id"],
            )
            return self._json(
                200, r, noindex=True, origin=_TRUSTED_ORIGIN
            )

        if path == "/api/agents":
            # Mints an sk_live_ agent key — operator-only. Paid keys from the
            # checkout flow are issued internally by the Stripe webhook
            # (billing._issue_key), never through this route.
            if not self._require_admin():
                return
            return self._json(200, store.create_agent(body.get("name", "agent")),
                              origin=_TRUSTED_ORIGIN)

        if path.startswith("/api/approvals/"):
            access = self._control_auth()
            if not access:
                return
            aid = path.rsplit("/", 1)[-1]
            ok = store.resolve_approval(
                aid,
                body.get("decision", "deny"),
                access["agent_id"],
                scoped=not access["admin"],
            )
            _broadcast({"type": "approval_resolved", "id": aid})
            return self._json(
                200, {"resolved": ok}, noindex=True, origin=_TRUSTED_ORIGIN
            )

        if path == "/admin/reset":
            # Admin-gated: clears transaction + approval history (keeps rules/agents).
            # Used to reset the public demo after testing. Set ADMIN_TOKEN on the server.
            if not self._require_admin():
                return
            n = store.reset_demo_data()
            return self._json(200, {"reset": True, "cleared": n}, origin=_TRUSTED_ORIGIN)

        if path == "/subscribe":
            if not self._check_rate("subscribe"):
                return self._json(429, {"error": "rate_limited", "retry_after": 3600})
            email = drip.normalize_email(body.get("email") or "")
            ref = (body.get("ref") or "").strip()[:128]
            ref = "".join(ch for ch in ref if ch not in "|\r\n" and ord(ch) >= 32)
            if email:
                try:
                    with _SUBSCRIBER_FILE_LOCK:
                        existing = set()
                        if os.path.exists(_SUBSCRIBERS_FILE):
                            with open(_SUBSCRIBERS_FILE, encoding="utf-8") as f:
                                for line in f:
                                    saved = drip.normalize_email(line.split("|", 1)[0])
                                    if saved:
                                        existing.add(saved)
                        if email not in existing:
                            parent = os.path.dirname(_SUBSCRIBERS_FILE)
                            if parent:
                                os.makedirs(parent, exist_ok=True)
                            with open(_SUBSCRIBERS_FILE, "a", encoding="utf-8") as f:
                                f.write(f"{email}|{ref}\n")
                except OSError:
                    return self._json(
                        503,
                        {"ok": False, "message": "We couldn't save your subscription. Please try again."},
                    )
                message = (
                    "You're on the list. Day 1 will arrive within 24 hours."
                    if drip.delivery_enabled()
                    else "You're on the list. We'll email the 5-day playbook when delivery is available."
                )
                return self._json(200, {"ok": True, "message": message})
            return self._json(400, {"ok": False, "message": "Enter a valid email."})

        # Unsubscribe POST handler
        if path == "/unsubscribe" or path == "/api/unsubscribe":
            email = drip.normalize_email(body.get("email") or "")
            removed = False
            if email:
                try:
                    with _SUBSCRIBER_FILE_LOCK:
                        subs_path = _SUBSCRIBERS_FILE
                        if os.path.exists(subs_path):
                            with open(subs_path, encoding="utf-8") as f:
                                lines = f.readlines()
                            kept = []
                            for line in lines:
                                saved = drip.normalize_email(line.split("|", 1)[0])
                                if saved == email:
                                    removed = True
                                else:
                                    kept.append(line)
                            parent = os.path.dirname(subs_path) or "."
                            with tempfile.NamedTemporaryFile(
                                "w",
                                encoding="utf-8",
                                dir=parent,
                                delete=False,
                            ) as tmp:
                                tmp.writelines(kept)
                                tmp_path = tmp.name
                            os.replace(tmp_path, subs_path)
                except OSError:
                    return self._json(503, {"ok": False, "error": "unsubscribe_failed"})
            return self._json(200, {"ok": True, "removed": removed})

        # Drip cron - protected endpoint to fire Soap Opera sequence
        # (Brunson Traffic Secrets Secret #6: Follow-Up Funnels)
        if path == "/cron/drip":
            secret = os.environ.get("DRIP_CRON_SECRET", "")
            auth = self.headers.get("Authorization", "")
            tok = auth[7:].strip() if auth.startswith("Bearer ") else ""
            if (
                secret
                and tok
                and hmac.compare_digest(secret.encode(), tok.encode())
            ):
                try:
                    result = drip.send_soap_operas()
                    return self._json(200, {"ok": True, "fired": True, "result": result})
                except Exception as e:
                    return self._json(500, {"ok": False, "error": str(e)})
            return self._json(403, {"ok": False, "error": "forbidden"})

        return self._json(404, {"error": "not_found"})


def serve(host="0.0.0.0", port=None):
    port = port or int(os.environ.get("PORT", 8080))
    store.init_db()
    # Start the drip email scheduler (Soap Opera sequence for new subscribers)
    # Brunson Traffic Secrets Secret #6: Follow-Up Funnels
    try:
        drip.start_drip_scheduler()
    except Exception as e:
        print(f"[drip] scheduler failed to start: {e}", flush=True)
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"sipi.bot spend firewall on http://{host}:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    serve()
