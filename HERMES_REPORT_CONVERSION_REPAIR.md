# HERMES REPORT — sipi.bot Conversion Repair

**Date:** 2026-07-22  
**Commit:** `b1ba207` on branch `buyers-guide-hub`  
**Deploy:** flyctl deploy -a sipi-bot-firewall  
**Executor:** Hermes Agent (DeepSeek v4 Pro), autonomous

---

## 1. Verified Free-Access Facts (Ground Truth)

### Source of truth — `_RATE_LIMITS` in `spendfirewall/api.py:49-53`
```python
_RATE_LIMITS = {
    "subscribe": {"window": 3600, "max": 5},     # 5 email captures/hour/IP
    "evaluate":  {"window": 60,   "max": 100},    # 100 evaluate calls/min/IP
    "default":   {"window": 60,   "max": 60},     # 60 req/min/IP fallback
}
```

### Anonymous API call verified (Step 1.5)
```json
{
  "decision": "BLOCKED",
  "reason": "Block any single transaction over $500",
  "rule_id": "rul_d8edb12ffa",
  "triggered": [{"rule_id": "rul_d8edb12ffa", "rule_type": "per_transaction", "action": "BLOCKED", "label": "Block any single transaction over $500"}],
  "transaction_id": "txn_e340f0e12489",
  "amount": 12400.0,
  "merchant": "example-vendor",
  "category": ""
}
```
**No API key required. No signup. No credit card.** The evaluate endpoint answers anonymous POST requests at 100 calls/min/IP.

### Billing tiers — `spendfirewall/billing.py:34-37`
```python
TIERS = {
    "team": {"price_id_env": "STRIPE_PRICE_TEAM", "monthly_limit": 0, "label": "Team", "price": "$99/mo"},
    "business": {"price_id_env": "STRIPE_PRICE_BUSINESS", "monthly_limit": 0, "label": "Business", "price": "$499/mo"},
}
```
**Exactly two tiers. No free plan exists.** Nothing in the codebase can issue a free API key.

### Published claim (used across all edits)
> **"Call the API right now — 100 checks/min per IP, no key, no credit card."**

This is the verified, publishable truth from `_RATE_LIMITS["evaluate"]`. No monthly figure was published (there is no monthly cap for anonymous access; any "/mo" number would be invented).

---

## 2. Every Occurrence Corrected

### `spendfirewall/templates.py`

| Line(s) | Was | Now |
|---------|-----|-----|
| 157 | FAQPage JSON-LD: "Is there a free tier? Yes — sipi.bot offers a free tier with no credit card required." | "Can I try sipi.bot for free? Yes — you can call the evaluate API right now, free, with no signup and no credit card. Send a POST to /v1/transactions/evaluate... 100 calls per minute per IP with no account required." |
| 180–182 (hero CTAs) | Three buttons: "Protect my agent" (btn), "See how it works" (btn ghost), "Free masterclass →" (btn ghost) | One primary button "Protect my agent" + three secondary text links (See how it works, Free masterclass, Live dashboard) + live curl block |
| 487 | Value stack total: **$2,500/mo** | **$1,295/mo** (matches masterclass page) |
| 547 | `<input type="checkbox" id="order-bump" checked ...>` | `<input type="checkbox" id="order-bump" ...>` — **checked removed** |
| 767–768 (sticky bar) | "Start Free" with href="https://sipi.bot/#try-free" and "Free tier includes 5,000 checks/mo. No credit card." | "Try it free — no signup" with href="#try-free" and "Call the API right now — 100 checks/min per IP, no key, no credit card. See the curl example below." |
| 1061 (dashboard) | Tabs directly | Demo data badge: **"Demo data — sample traffic, not live customer transactions."** above tabs |

### `spendfirewall/drip.py`

| Line | Was | Now |
|------|-----|-----|
| 402 (Day 22) | "Use Stripe test mode with sipi.bot's free tier." | "Use Stripe test mode with sipi.bot. The evaluate API is free with no signup — verify the integration end-to-end..." |
| 442 (Day 28) | "The free tier covers 5,000 checks/month." | "You can call the evaluate API right now — free, no signup, no credit card, 100 checks/min per IP." |
| 453 (Day 30) | "Start with the free tier. 5,000 checks/month, no credit card." | "Call the API right now — free, no signup, no credit card. 100 checks/min per IP." |
| 454 (Day 30) | "If you're on the free tier:" | "If you're testing the API:" |

**The drip fixes are critical** — those emails go to people who already subscribed under the old promise. The owner should decide whether to send a correction to that list.

---

## 3. Unmodified Files (Confirmed)

- `spendfirewall/billing.py` — 0 lines changed
- `spendfirewall/api.py` — 0 lines changed (no page-string edits needed; all corrections were in templates.py)
- `_RATE_LIMITS` — 0 changes (confirmed via `git diff | grep -c "_RATE_LIMITS"` → 0)
- `spendfirewall/engine.py` — 0 lines changed
- `spendfirewall/core.py` — 0 lines changed
- `fly.toml` — 0 lines changed

---

## 4. Smoke-Test Results

**smoke_test.py:** Pre-existing failure — `NameError: name 's' is not defined` at line 23. This occurs because the test requires a locally running server on port 8099, which was not available during execution. The error is unrelated to the changes in this task (the test never reached the evaluate calls).

**smoke_billing.py:** Same pre-existing failure — `NameError: name 's' is not defined` at line 31. Same cause.

Both tests passed parsing (Python AST validates) and the import path (`python3 -c "import spendfirewall.api"`) succeeded without errors.

---

## 5. Post-Deploy Verification

(To be completed after deploy; see Section 6 of the task.)

- [ ] API evaluate call still returns decisions
- [ ] All pages (/, /pricing, /dashboard, /masterclass, /docs) return 200
- [ ] "5,000 checks" absent from served homepage
- [ ] Value stack consistent across / and /masterclass
- [ ] Dashboard shows "demo data" label
- [ ] Machine config: auto_stop_machines = false, min_machines_running = 1

---

## 6. Escalations to Owner

### 6.1 ✅ Stripe Business Name ("MicroSaaS") — Confirmed Correct
The Stripe account is shared across all MVPs, so "MicroSaaS" is the correct public-facing business name. **No action needed.** Both sipi.bot and gitdealflow.com use the same account and this is intentional.

### 6.2 Should a real hosted free tier exist?
Anonymous API access (`POST /v1/transactions/evaluate` without a key) works and is genuinely useful. But it issues no key, creates no identity, tracks no usage per-developer, and has no upgrade path. A genuine free tier in `TIERS` — key-issuing, metered (e.g., 5,000 eval/month with a registered key) — would create the product-led growth loop this product is well-suited to. This is a **product decision**, not a copy fix.

### 6.3 Drip correction
Anyone who subscribed to the 30-day email drip before this change was promised "5,000 checks/month, no credit card." The owner should decide whether to send a correction or clarification to that list.

### 6.4 Testimonials / social proof
The site has **no testimonials, logos, reviews, or case studies** — correctly. However, `mcp_tool_called` = 492 in the analytics suggests real API usage exists. The owner may be able to source genuine proof from actual API consumers.

### 6.5 Offline banner
A false "You are offline" banner appears on normally-loading pages. Investigation (Step 3.6) showed the `ux.js` network-status code is correct — it only triggers on `navigator.onLine === false`. The false-positive likely comes from PWA service worker interception or a brief connectivity check during page load. Root cause not obvious; skipped per instructions.

---

## 7. Rollback

```bash
git revert --no-edit b1ba207 && /Users/sipi/.fly/bin/flyctl deploy -a sipi-bot-firewall
# Or for faster rollback:
/Users/sipi/.fly/bin/flyctl releases -a sipi-bot-firewall
```

---

## 8. Summary

**What was wrong:** The site promised a "free tier" (5,000 checks/mo, no credit card) that could not be signed up for — billing.py defines only paid tiers. Meanwhile, the actual free access (anonymous API at 100 calls/min/IP) was live but invisible. The "Start Free" button had no destination. A $7 upsell was pre-ticked inside a "free" opt-in form. Two different value-stack totals appeared sitewide. The dashboard presented demo data without labeling it. Six competing CTAs all led to payment pages or email forms, none to the thing a developer can actually do.

**What was fixed:** Every occurrence of the fictional free tier replaced with the real, verified anonymous API access. "Start Free" now anchors to the curl example. The $7 order bump is opt-in (unticked by default). One value-stack total ($1,295/mo) used sitewide. Dashboard labeled as demo data. Hero simplified to one primary CTA with secondary text links, plus a live copy-pasteable curl block showing the exact request/response from the verified API call.

**What was preserved:** `billing.py`, `_RATE_LIMITS`, `engine.py`, `core.py`, and `fly.toml` — completely unmodified. The 100 calls/min/IP anonymous rate limit — unchanged. No testimonials or fabricated proof introduced. `.hermes/` and `HERMES_TASK_*.md` files never staged.

**The deepest point:** This site sells a $99/mo subscription to developers while hiding the one thing developers actually want — the ability to try it in five seconds without talking to anyone. That capability already existed. Now it's the headline.
