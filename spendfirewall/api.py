"""api.py — HTTP API + dashboard server + SSE + agent-card + eval report.

Stdlib only (http.server). Serves:
  GET  /                          landing page
  GET  /dashboard                 control room
  GET  /health                    {"ok": true}
  GET  /.well-known/agent-card.json   agent discoverability
  GET  /openapi.json                  OpenAPI 3.0 spec (AIO / AI-agent discoverability)
  GET  /eval                      last eval report (JSON) — the sales asset
  POST /v1/transactions/evaluate  THE core call (auth optional in free mode)
  GET  /v1/activity               SSE live stream
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

import hmac
import json
import os
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import __version__, core, store, templates
from . import billing

_SUBSCRIBERS: list[queue.Queue] = []
_SUB_LOCK = threading.Lock()
_EVAL_REPORT_PATH = os.environ.get("EVAL_REPORT", os.path.join(os.getcwd(), "eval_report.json"))
_SUBSCRIBERS_FILE = os.environ.get("SUBS_FILE", os.path.join(os.getcwd(), "subscribers.txt"))
# Trusted origin echoed on state-changing control-plane routes instead of *.
_TRUSTED_ORIGIN = (os.environ.get("PUBLIC_URL") or "https://sipi.bot").rstrip("/")


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


def agent_card() -> dict:
    return {
        "name": "sipi.bot Spend Firewall",
        "description": "Approves, blocks, or flags every transaction an autonomous AI agent "
                       "proposes, against configurable spend rules. The firewall for the agent economy.",
        "version": __version__,
        "url": "https://sipi.bot",
        "provider": {"organization": "sipi.bot", "url": "https://sipi.bot"},
        "capabilities": {"streaming": True},
        "skills": [{
            "id": "evaluate_transaction",
            "name": "Evaluate a spend",
            "description": "Given amount, merchant, category, returns APPROVED, BLOCKED, or FLAGGED.",
            "tags": ["spend-control", "policy", "guardrail", "agent-safety"],
            "examples": ["Can my agent spend $6200 at unknown-gpu.ru?"],
        }],
        "endpoints": {
            "evaluate": "https://sipi.bot/v1/transactions/evaluate",
            "activity": "https://sipi.bot/v1/activity",
            "openapi": "https://sipi.bot/openapi.json",
            "eval_report": "https://sipi.bot/eval",
        },
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):  # quieter logs
        pass

    def _send(self, code: int, body: bytes, ctype="application/json", noindex=False,
              origin="*"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if noindex:
            # Machine endpoints (JSON) should not appear in search indexes.
            self.send_header("X-Robots-Tag", "noindex")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Headers", "Authorization,Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS,HEAD")
        # Security headers (Technical SEO + hardening)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
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
        token = os.environ.get("ADMIN_TOKEN", "")
        auth = self.headers.get("Authorization", "")
        given = auth[7:].strip() if auth.startswith("Bearer ") else ""
        if token and given and hmac.compare_digest(given.encode(), token.encode()):
            return True
        self._json(403, {"error": "forbidden"}, origin=_TRUSTED_ORIGIN)
        return False

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
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://eu.i.posthog.com https://eu-assets.i.posthog.com https://eu.posthog.com https://checkout.stripe.com https://www.googletagmanager.com https://*.google-analytics.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://eu.i.posthog.com https://eu-assets.i.posthog.com https://sipi.bot https://*.google-analytics.com https://www.googletagmanager.com; frame-ancestors 'none'; object-src 'none'; base-uri 'self'; frame-src https://js.stripe.com https://checkout.stripe.com")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=(), interest-cohort=()")
        self.end_headers()
        if getattr(self, "_head_only", False):
            return
        self.wfile.write(html.encode())

    def _body(self) -> dict:
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n <= 0:
                return {}
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
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
                self.end_headers()
                return


        # ── pSEO static pages ──────────────────────────
        try_pseo = self._serve_pseo(path)
        if try_pseo:
            return
        if path == "/" or path == "/index.html":
            return self._html(templates.landing_page_html())
        if path == "/dashboard":
            return self._html(templates.dashboard_html())
        if path == "/health":
            return self._json(200, {"ok": True, "service": "sipi.bot", "version": __version__},
                              noindex=True)
        if path == "/BingSiteAuth.xml":
            xml = ('<?xml version="1.0"?>\n<users>\n\t<user>'
                   'FA4E122745948F0CAD16959F59DDCB85</user>\n</users>')
            return self._send(200, xml.encode(), "application/xml")
        if path == "/.well-known/agent-card.json":
            return self._json(200, agent_card())
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
        if path == "/api/stats":
            return self._json(200, core.status())
        if path == "/api/transactions":
            return self._json(200, store.recent_transactions(50))
        if path == "/api/approvals":
            return self._json(200, store.list_approvals("pending"))
        if path == "/api/rules":
            return self._json(200, store.list_rules())
        if path == "/api/agents":
            return self._json(200, store.list_agents())

        # ── MCP (Model Context Protocol) JSON-RPC endpoint ──
        if path == "/api/mcp":
            _mcp_tools = [
                {"name": "evaluate_spend", "description": "Check whether an autonomous agent is allowed to make a purchase BEFORE spending. Returns APPROVED, BLOCKED, or FLAGGED.",
                 "inputSchema": {"type": "object", "properties": {"amount": {"type": "number"}, "merchant": {"type": "string"}, "category": {"type": "string"}, "description": {"type": "string"}}, "required": ["amount"]}},
                {"name": "add_spend_rule", "description": "Add a spend policy rule. Types: per_transaction, daily_total, velocity, merchant_block, category_limit, approval_threshold.",
                 "inputSchema": {"type": "object", "properties": {"rule_type": {"type": "string"}, "params": {"type": "string"}, "action": {"type": "string"}}, "required": ["rule_type", "params"]}},
                {"name": "firewall_status", "description": "Get current firewall stats: spend approved/blocked today, pending approvals, active agents.",
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
                self.send_response(202); self.end_headers(); return
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
                    result = core.evaluate_transaction(
                        amount=args.get("amount", 0), merchant=args.get("merchant", ""),
                        category=args.get("category", ""), description=args.get("description", ""))
                    return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {
                        "content": [{"type": "text", "text": json.dumps(result)}]}})
                if tool_name == "firewall_status":
                    return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {
                        "content": [{"type": "text", "text": json.dumps(core.status())}]}})
                arg_summary = "; ".join(f"{k}={v}" for k, v in args.items())
                cta = f"https://sipi.bot/?utm_source=mcp&utm_campaign={tool_name}"
                return self._json(200, {"jsonrpc": "2.0", "id": rpc_id, "result": {
                    "content": [{"type": "text", "text": f"**{tool['description']}**\n\nParameters: {arg_summary or '(none)'}\n\nVisit: {cta}"}]}})
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
            from urllib.parse import parse_qs, urlparse as _up
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
        if path == "/about":
            return self._html(templates.doc_page_html(
                "About", "/about",
                "sipi.bot is the spend firewall for autonomous AI agents — evaluate every transaction against your rules and get approve, block, or flag in under 5ms.",
                templates.ABOUT_BODY))
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
            try:
                url = billing.create_checkout_session(plan)
            except Exception as e:
                return self._json(400, {"error": str(e)})
            self.send_response(302)
            self.send_header("Location", url)
            self.send_header("Content-Length", "0")
            self.send_header("X-Robots-Tag", "noindex, nofollow")
            self.end_headers()
            return
        if path.startswith("/keys/"):
            sess = path.rsplit("/", 1)[-1]
            rec = billing.key_for_session(sess)
            return self._html(templates.key_success_html(rec), cacheable=False)
        if path == "/v1/activity":
            return self._sse()
        # Static files from public/ (sitemap.xml, robots.txt, llms.txt, pSEO
        # pages written by the growth engine). Served last, before 404.
        if self._serve_static(path):
            return
        return self._json(404, {"error": "not_found"})

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
        self._send(200, data, ctype)
        return True

    def _sse(self):
        self.send_response(200)
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://eu.i.posthog.com https://eu-assets.i.posthog.com https://eu.posthog.com https://checkout.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://eu.i.posthog.com https://eu-assets.i.posthog.com https://sipi.bot; frame-ancestors 'none'; object-src 'none'; base-uri 'self'; frame-src https://js.stripe.com https://checkout.stripe.com")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=(), interest-cohort=()")
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
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
            if not self._require_admin():
                return
            rid = path.rsplit("/", 1)[-1]
            return self._json(200, {"deleted": store.delete_rule(rid)}, origin=_TRUSTED_ORIGIN)
        return self._json(404, {"error": "not_found"})

    
    def _serve_pseo(self, path):
        """Serve pSEO static HTML pages from vs/ for/ learn/ integrations/ subdirs.

        Returns True when a page was served (so do_GET stops routing),
        None/False on a miss. NB: _html() returns None — never return its
        result directly or do_GET falls through and appends a second 404
        response to the body (the 82-page corruption bug)."""
        import os
        for prefix in ("/vs/", "/for/", "/learn/", "/integrations/", "/glossary/", "/use-cases/", "/faq/", "/alternatives-to/", "/benchmarks/", "/tutorials/", "/policies/", "/limits/", "/best/", "/how-to/", "/templates/", "/cost-of/"):
            if path.startswith(prefix):
                base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                filepath = os.path.join(base, path.lstrip("/"), "index.html")
                filepath = os.path.abspath(os.path.normpath(filepath))
                # containment: never follow a traversal outside the app root
                if not filepath.startswith(base + os.sep):
                    return None
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, encoding="utf-8") as fh:
                            self._html(fh.read())
                            return True
                    except Exception:
                        pass
                return None
        return None

    def do_POST(self):
        path = urlparse(self.path).path

        # MCP, A2A, NLWeb POST routes — delegate to do_GET which handles JSON-RPC
        if path in ("/api/mcp", "/api/a2a", "/api/nlweb"):
            self.command = "POST"
            return self.do_GET()

        # Stripe webhook must read the RAW body once (before _body parses it)
        # for signature verification.
        if path == "/webhooks/stripe":
            try:
                n = int(self.headers.get("Content-Length", 0))
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

        if path == "/v1/transactions/evaluate":
            # Auth optional in free/self-host mode. If a key is provided, tie to agent.
            agent_id = None
            auth = self.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                agent = store.get_agent_by_key(auth[7:].strip())
                if agent:
                    agent_id = agent["id"]
            try:
                result = core.evaluate_transaction(
                    amount=body.get("amount", 0),
                    merchant=body.get("merchant", ""),
                    category=body.get("category", ""),
                    description=body.get("description", ""),
                    currency=body.get("currency", "USD"),
                    timestamp=body.get("timestamp"),
                    agent_id=agent_id,
                )
            except Exception as e:
                return self._json(400, {"error": str(e)})
            _broadcast({"type": "transaction", **result})
            return self._json(200, result)

        if path == "/api/rules":
            if not self._require_admin():
                return
            r = store.add_rule(
                rule_type=body.get("rule_type", "per_transaction"),
                params=body.get("params", {}),
                action=body.get("action", "BLOCKED"),
                priority=int(body.get("priority", 100)),
                label=body.get("label", ""),
            )
            return self._json(200, r, origin=_TRUSTED_ORIGIN)

        if path == "/api/agents":
            # Mints an sk_live_ agent key — operator-only. Paid keys from the
            # checkout flow are issued internally by the Stripe webhook
            # (billing._issue_key), never through this route.
            if not self._require_admin():
                return
            return self._json(200, store.create_agent(body.get("name", "agent")),
                              origin=_TRUSTED_ORIGIN)

        if path.startswith("/api/approvals/"):
            if not self._require_admin():
                return
            aid = path.rsplit("/", 1)[-1]
            ok = store.resolve_approval(aid, body.get("decision", "deny"))
            _broadcast({"type": "approval_resolved", "id": aid})
            return self._json(200, {"resolved": ok}, origin=_TRUSTED_ORIGIN)

        if path == "/admin/reset":
            # Admin-gated: clears transaction + approval history (keeps rules/agents).
            # Used to reset the public demo after testing. Set ADMIN_TOKEN on the server.
            if not self._require_admin():
                return
            n = store.reset_demo_data()
            return self._json(200, {"reset": True, "cleared": n}, origin=_TRUSTED_ORIGIN)

        if path == "/subscribe":
            email = (body.get("email") or "").strip()
            ref = (body.get("ref") or "").strip()
            if email and "@" in email:
                try:
                    with open(_SUBSCRIBERS_FILE, "a") as f:
                        f.write(f"{email}|{ref}\n")
                except Exception:
                    pass
                return self._json(200, {"ok": True, "message": "You're on the list. We'll email your pilot access."})
            return self._json(400, {"ok": False, "message": "Enter a valid email."})

        return self._json(404, {"error": "not_found"})


def serve(host="0.0.0.0", port=None):
    port = port or int(os.environ.get("PORT", 8080))
    store.init_db()
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"sipi.bot spend firewall on http://{host}:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    serve()
