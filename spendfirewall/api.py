"""api.py — HTTP API + dashboard server + SSE + agent-card + eval report.

Stdlib only (http.server). Serves:
  GET  /                          landing page
  GET  /dashboard                 control room
  GET  /health                    {"ok": true}
  GET  /.well-known/agent-card.json   agent discoverability
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
            "eval_report": "https://sipi.bot/eval",
        },
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # quieter logs
        pass

    def _send(self, code: int, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization,Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS,HEAD")
        # Security headers (Technical SEO + hardening)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.end_headers()
        if getattr(self, "_head_only", False):
            return
        self.wfile.write(body)

    def do_HEAD(self):
        """Mirror do_GET but suppress the body (fixes 501-on-HEAD; crawlers/audits use HEAD)."""
        self._head_only = True
        try:
            self.do_GET()
        finally:
            self._head_only = False

    def _json(self, code, obj):
        self._send(code, json.dumps(obj).encode(), "application/json")

    def _html(self, html: str):
        self._send(200, html.encode(), "text/html; charset=utf-8")

    def _body(self) -> dict:
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n <= 0:
                return {}
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/index.html":
            return self._html(templates.landing_page_html())
        if path == "/dashboard":
            return self._html(templates.dashboard_html())
        if path == "/health":
            return self._json(200, {"ok": True, "service": "sipi.bot", "version": __version__})
        if path == "/BingSiteAuth.xml":
            xml = ('<?xml version="1.0"?>\n<users>\n\t<user>'
                   'FA4E122745948F0CAD16959F59DDCB85</user>\n</users>')
            return self._send(200, xml.encode(), "application/xml")
        if path == "/.well-known/agent-card.json":
            return self._json(200, agent_card())
        if path == "/eval":
            if os.path.exists(_EVAL_REPORT_PATH):
                with open(_EVAL_REPORT_PATH) as f:
                    return self._json(200, json.load(f))
            return self._json(200, {"status": "not_run_yet",
                                    "hint": "run: python -m spendfirewall.eval.run_eval"})
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
            self.end_headers()
            return
        if path.startswith("/keys/"):
            sess = path.rsplit("/", 1)[-1]
            rec = billing.key_for_session(sess)
            return self._html(templates.key_success_html(rec))
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
            rid = path.rsplit("/", 1)[-1]
            return self._json(200, {"deleted": store.delete_rule(rid)})
        return self._json(404, {"error": "not_found"})

    def do_POST(self):
        path = urlparse(self.path).path

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
            r = store.add_rule(
                rule_type=body.get("rule_type", "per_transaction"),
                params=body.get("params", {}),
                action=body.get("action", "BLOCKED"),
                priority=int(body.get("priority", 100)),
                label=body.get("label", ""),
            )
            return self._json(200, r)

        if path == "/api/agents":
            return self._json(200, store.create_agent(body.get("name", "agent")))

        if path.startswith("/api/approvals/"):
            aid = path.rsplit("/", 1)[-1]
            ok = store.resolve_approval(aid, body.get("decision", "deny"))
            _broadcast({"type": "approval_resolved", "id": aid})
            return self._json(200, {"resolved": ok})

        if path == "/admin/reset":
            # Admin-gated: clears transaction + approval history (keeps rules/agents).
            # Used to reset the public demo after testing. Set ADMIN_TOKEN on the server.
            token = os.environ.get("ADMIN_TOKEN", "")
            auth = self.headers.get("Authorization", "")
            given = auth[7:].strip() if auth.startswith("Bearer ") else ""
            if not token or given != token:
                return self._json(403, {"error": "forbidden"})
            n = store.reset_demo_data()
            return self._json(200, {"reset": True, "cleared": n})

        if path == "/subscribe":
            email = (body.get("email") or "").strip()
            if email and "@" in email:
                try:
                    with open(_SUBSCRIBERS_FILE, "a") as f:
                        f.write(email + "\n")
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
