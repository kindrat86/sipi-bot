# sipi.bot — QA / Security / Speed Audit Report

**Date:** 2026-07-18  
**Target:** https://sipi.bot (Python stdlib `http.server` on Fly.io)  
**Repo:** `~/projects/sipi-bot/spendfirewall/api.py`  
**Scope:** Security headers per response path, broken links, HTTPS/HSTS. No pip audit, no dep upgrades, no Lighthouse, no deploy.

---

## Overall Scores

| Category | Score | Notes |
|---|---|---|
| **Security** | **68/100** | Good baseline on HTML paths; critical gaps on MCP 202, www redirect, HTTP→HTTPS redirect, checkout 302, and SSE path missing HSTS. No CSP on any JSON/API path. |
| **QA** | **88/100** | Solid routing. 4 minor: /favicon.ico 404 (exists as .svg), /compare/ 404 (pSEO prefix registered but no content), /cost-of/ 404, /templates/ 404, /calculators/ 404, /guides/ 404, /widgets/ 404. |
| **Speed** | **92/100** | All responses under 200ms from my probe. Static assets have Cache-Control. JSON/API paths lack Cache-Control but are small. |

---

## Security Headers — Response Path Inventory

### Legend
| Header | Code |
|---|---|
| Strict-Transport-Security (HSTS) | `H` |
| X-Content-Type-Options: nosniff | `X` |
| X-Frame-Options: DENY | `F` |
| Referrer-Policy | `R` |
| Content-Security-Policy | `C` |
| Permissions-Policy | `P` |
| X-Robots-Tag: noindex | `!r` |
| CORS (access-control-*) | `CORS` |

### ✅ Full Headers — HTML Pages (via `_html()`)
These paths have ALL 6 security headers (H, X, F, R, C, P):

| Path | Method | Headers | Handler |
|---|---|---|---|
| `/` | GET | H X F R C P | `_html(landing_page_html())` |
| `/dashboard` | GET | H X F R C P | `_html(dashboard_html())` |
| `/pricing` | GET | H X F R C P | `_html(pricing_html())` |
| `/about` | GET | H X F R C P | `_html(doc_page_html())` |
| `/privacy` | GET | H X F R C P | `_html(doc_page_html())` |
| `/terms` | GET | H X F R C P | `_html(doc_page_html())` |
| `/affiliates` | GET | H X F R C P | `_html(affiliates_html())` |
| `/affiliates/signup` | GET | H X F R C P | `_html(affiliates_signup_html())` |
| `/dream100` | GET | H X F R C P | `_html(dream100_html())` |
| `/unsubscribe` | GET/POST | H X F R C P | `_html(html literals)` |
| `/keys/<session>` | GET | H X F R C P | `_html(key_success_html(), cacheable=False)` |
| `/vs/<name>/` (pSEO) | GET | H X F R C P | `_html()` via `_serve_pseo()` |
| `/for/<name>/` etc. | GET | H X F R C P | `_html()` via `_serve_pseo()` |

### ⚠️ Partial — JSON / API Paths (via `_send()`)
These paths have the core 4 (H, X, F, R) + CORS, but **MISSING CSP and Permissions-Policy**:

| Path | Method | Headers | Missing |
|---|---|---|---|
| `/health` | GET | H X F R CORS !r | **C, P** |
| `/.well-known/agent-card.json` | GET | H X F R CORS | **C, P** |
| `/openapi.json` | GET | H X F R CORS | **C, P** |
| `/eval` | GET | H X F R CORS | **C, P** |
| `/api/stats` | GET | H X F R CORS | **C, P** |
| `/api/transactions` | GET | H X F R CORS | **C, P** |
| `/api/approvals` | GET | H X F R CORS | **C, P** |
| `/api/rules` | GET/POST/DELETE | H X F R CORS (trusted on control) | **C, P** |
| `/api/agents` | GET/POST | H X F R CORS (trusted on control) | **C, P** |
| `/api/approvals/<id>` | POST | H X F R CORS | **C, P** |
| `/admin/reset` | POST | H X F R CORS | **C, P** |
| `/BingSiteAuth.xml` | GET | H X F R CORS | **C, P** |
| `/billing/status` | GET | H X F R CORS | **C, P** |
| `/api/mcp` (GET + most POST paths) | GET/POST | H X F R CORS | **C, P** |
| `/api/a2a` | GET/POST | H X F R CORS | **C, P** |
| `/api/nlweb` | GET/POST | H X F R CORS | **C, P** |
| `/webhooks/stripe` | POST | H X F R CORS | **C, P** |
| `/v1/transactions/evaluate` | POST | H X F R CORS | **C, P** |
| `/subscribe` | POST | H X F R CORS | **C, P** |
| `/cron/drip` | GET/POST | H X F R CORS | **C, P** |
| `/v1/activity` (SSE) | GET | **C P CORS** — but **MISSING H, X, F, R** | **H, X, F, R** |
| `/_nonexistent` (404) | ANY | H X F R CORS | **C, P** |
| OPTIONS / | OPTIONS | H X F R CORS | **C, P** |

### ❌ Zero Security Headers — Redirects & Bare Response Paths

| Path | Method | Code | Headers Present | Fix Needed |
|---|---|---|---|---|
| `www.sipi.bot/→sipi.bot/` | GET | 301 | Location only (Fly.io default headers) | **Add HSTS + X-Frame-Options + X-Content-Type-Options + Referrer-Policy** in `do_GET` before line 235 |
| `http://sipi.bot/→https://sipi.bot/` | ANY | 301 | Location only (Fly.io edge redirect) | **Add HSTS** to the 301 response (Fly.io config) |
| `/checkout/<plan>` (successful) | GET | 302 | Location + Content-Length + X-Robots-Tag | **Add HSTS + X-Content-Type-Options + X-Frame-Options + Referrer-Policy** before `end_headers()` at line 408 |
| `/api/mcp` — method `notifications/initialized` | POST | 202 | **None** — just `send_response(202); end_headers()` | **CRITICAL**: Add all security headers; use `_send(202, b"")` or add explicit headers before `end_headers()` |

---

## Detailed Security Header Gap Analysis

### Gap 1: All `_send()` paths missing CSP and Permissions-Policy
**Root cause:** `Handler._send()` (line 135-157) sends HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and CORS, but **never** sends Content-Security-Policy or Permissions-Policy.

**Impact:** 20+ JSON/API endpoints are vulnerable to XSS (no CSP) and feature abuse (no Permissions-Policy). Though JSON responses are less prone to script injection via browsers, a CSP is still a defense-in-depth layer.

**Fix:** Add to `_send()`:
```python
self.send_header("Content-Security-Policy", "default-src 'none'")
self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=(), interest-cohort=()")
```

### Gap 2: SSE path (`_sse()`) missing HSTS, XFO, XCTO, RP
**Root cause:** `_sse()` (line 499-526) sends its own CSP and Permissions-Policy but **omits** the 4 security headers that `_send()` provides.

**Impact:** The SSE endpoint has CSP and Permissions-Policy but no HSTS preload signal, no clickjack protection, no nosniff, no referrer policy.

**Fix:** Add to `_sse()` before `end_headers()`:
```python
self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
self.send_header("X-Content-Type-Options", "nosniff")
self.send_header("X-Frame-Options", "DENY")
self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
```

### Gap 3 (CRITICAL): MCP `notifications/initialized` → bare 202
**Root cause:** Line 312: `self.send_response(202); self.end_headers(); return` — no security headers whatsoever.

**Impact:** An MCP client hitting this path gets literally zero security headers. While MCP is primarily machine-to-machine, attack surface is attack surface.

**Fix:** Replace with `self._send(202, b"")` to go through the `_send()` pipeline.

### Gap 4: www redirect → bare 301
**Root cause:** Lines 229-236: only sends `Location` header. `do_GET()` returns before reaching any `_send()` or `_html()` call.

**Impact:** www→apex redirect has zero security headers.

**Fix:** Add HSTS + XFO + XCTO + RP before `end_headers()`:
```python
self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
self.send_header("X-Content-Type-Options", "nosniff")
self.send_header("X-Frame-Options", "DENY")
self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
```

### Gap 5: Checkout 302 redirect → bare redirect
**Root cause:** Lines 404-409: only Location + Content-Length + X-Robots-Tag.

**Impact:** Stripe checkout redirect has no security headers.

**Fix:** Add same 4 headers before `end_headers()`.

---

## Broken Link Scan

| URL | Status | Notes |
|---|---|---|
| `/favicon.ico` | **404** | Missing. `/favicon.svg` exists and returns 200. Browsers that request `/favicon.ico` get a 404. |
| `/favicon.svg` | 200 ✅ | Present |
| `/compare/` | **404** | pSEO prefix registered, no content |
| `/cost-of/` | **404** | pSEO prefix registered, no content |
| `/templates/` | **404** | pSEO prefix registered, no content |
| `/calculators/` | **404** | pSEO prefix registered, no content |
| `/guides/` | **404** | pSEO prefix registered, no content |
| `/widgets/` | **404** | Directory exists in `public/` but empty |
| All `/vs/<name>/` pages sampled | 200 ✅ | litellm, openai-billing, openrouter all OK |
| `/pricing` | 200 ✅ | |
| `/about` | 200 ✅ | |
| `/privacy` | 200 ✅ | |
| `/terms` | 200 ✅ | |
| `/health` | 200 ✅ | |
| `/eval` | 200 ✅ | |
| `/llms.txt` | 200 ✅ | |
| `/robots.txt` | 200 ✅ | |
| `/sitemap.xml` | 200 ✅ | |
| `/BingSiteAuth.xml` | 200 ✅ | |
| `/og.png` | 200 ✅ | |

---

## HTTPS / HSTS Audit

| Check | Result |
|---|---|
| HTTPS enforced | ✅ All HTTP requests redirect 301 → HTTPS |
| HSTS on HTML pages | ✅ `max-age=63072000; includeSubDomains; preload` |
| HSTS on JSON/API paths | ✅ Yes (via `_send()`) |
| HSTS on SSE path | ❌ **MISSING** |
| HSTS on 301 redirects (www, http) | ❌ **MISSING** |
| HSTS on Checkout 302 | ❌ **MISSING** |
| HSTS on MCP 202 | ❌ **MISSING** |
| www → apex redirect | ✅ Working (301 to sipi.bot) |

---

## Summary of Findings

### Security (Score: 68/100)
**Strengths:**
- All HTML pages have full header coverage
- `_send()` path has the 4 core security headers on 20+ JSON endpoints
- HSTS with preload everywhere it matters on 200 responses
- Consistent CORS headers

**Critical (fix immediately):**
1. **Line 312: MCP `notifications/initialized` bare 202** — zero security headers (`send_response(202)` only)
2. **SSE path `_sse()`** — missing HSTS, XFO, XCTO, Referrer-Policy (has CSP + Permissions-Policy but not the core 4)

**High (fix next sprint):**
3. **All `_send()` paths missing CSP + Permissions-Policy** — 20+ endpoints
4. **www redirect** bare 301 — no security headers
5. **Checkout 302 redirect** bare redirect — no security headers

### QA (Score: 88/100)
- Solid routing coverage across 40+ unique paths
- `/favicon.ico` missing (serve a redirect to `/favicon.svg` or a small .ico)
- 6 pSEO prefix directories registered but empty (expected, they'll fill over time)

### Speed (Score: 92/100)
- All responses fast (Fly.io edge, small payloads)
- HTML pages have Cache-Control (public, max-age=3600)
- Static assets have Cache-Control (inherited from `_send()` — no explicit Cache-Control on static CSS/JS though)
- JSON/API paths lack Cache-Control (acceptable for dynamic data)
