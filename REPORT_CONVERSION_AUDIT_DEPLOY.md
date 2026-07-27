# Conversion Audit → Deploy Report — sipi.bot (2026-07-27)

## Outcome: DEPLOYED & VERIFIED LIVE (21/21 checks pass)

Two surgical conversion fixes from the full audit were shipped to production.
Build `deployment-01KYHSNTF0CNGYX66YMAZ1Q44W`, commit `13dd697`, branch
`conv/pricing-schema-and-redirects` (pushed to origin).

---

## What the audit actually found (after reading the source, not just scraping)

The initial external-scrape audit produced 10 "wins." Reading the real source
code corrected 4 of them — **those were NOT fixed, because they were either
already done or forbidden by the honesty gate:**

| Original "win" | Reality in the code | Action |
|---|---|---|
| "Fix checkout 502" | Transient Fly edge blip; 5/5 retests = 302→live Stripe. `auto_stop_machines=false`, `min_machines_running=1`. Not a code bug. | None needed |
| "Ship a thank-you page" | Already exists: `/keys/{session}` → `key_success_html()` with key display, copy button, onboarding, first-eval curl. | Already done |
| "Instrument conversion events" | Already fully instrumented: client `cta_clicked`/`playground_opened`/`$pageview`/aid-stitching + server `checkout_started/completed`, `api_key_issued`, `activation_completed`, `checkout_failed`, `subscription_canceled`. | Already done |
| "Add AggregateRating + testimonials" | **Forbidden** by `config.yaml` honesty gate ("never add ratings without real data") and `plan.md` ("Stripe shows ZERO subs"). Fabricating these would violate a non-negotiable rule. | Refused (honest) |

## The two genuine defects that WERE fixed

### Fix #1 — Pricing page had zero structured data (`templates.py`)
`/pricing` had `0` JSON-LD blocks while the homepage was schema-rich → invisible
to price rich results and AI price citations.
- Added `Product` + `AggregateOffer` (3 real tiers: $0 self-host / $99 Team / $499 Business)
- Added `FAQPage` (6 Q&As, mirrored verbatim from the existing visible `<details>` FAQ)
- **No `aggregateRating`** — honesty gate honored (no real ratings data exists; none fabricated)

### Fix #2 — Bare hub roots 404'd while children resolved (`api.py`)
`/compare/` and `/calculator/` returned 404 (no `index.html`) while their child
pages (`/compare/aws-budgets/`, `/tools/risk-calculator/`) resolved fine. Visitors
who guessed the URL or followed stale links hit a dead end.
- 301 `/compare` & `/compare/` → `/vs/` (populated comparison hub)
- 301 `/calculator` & `/calculator/` → `/tools/risk-calculator/` (the real calculator)
- All security headers (HSTS, XFO, COOP, COEP) survive the redirect

## How the Hermes race was avoided

A live Hermes agent (`hermes-agent` / `hermes_cli`, 4 processes) was actively
writing to the repo's working tree during this work (gzip compression + a
benchmark hub + a `Fly-Client-IP` rate-limit fix — none of which compile). To
deploy without racing that process or shipping unauthored work, the deploy ran
from a **fresh isolated clone of committed `origin/main`** at `/tmp/sipi-deploy`,
which the racing working tree cannot contaminate.

## Verification

### Pre-deploy (local, real server boot)
- `py_compile` clean on both files
- JSON-LD parses; honesty gate asserts no `aggregateRating`
- Booted `python -m spendfirewall.api`, ran 12 curl-based smoke tests → **12/12 pass**
- Dockerfile's built-in `validate_jsonld.py` build step passed (would fail on malformed schema)

### Post-deploy (LIVE on https://sipi.bot) — 21/21 pass
**Fix #1 (pricing schema):**
- `/pricing` serves JSON-LD ✓ | has Product ✓ | AggregateOffer ✓ | FAQPage ✓ | no fabricated rating ✓
- 3 offers $0/$99/$499, range 0–499 USD, valid JSON, Google Rich-Results eligible

**Fix #2 (redirects):**
- `/compare` → 301 `/vs/` ✓ | `/compare/` → 301 `/vs/` ✓
- `/calculator` → 301 `/tools/risk-calculator/` ✓ | `/calculator/` → 301 `/tools/risk-calculator/` ✓

**No regressions:**
- `/ /pricing /dashboard /playground/ /vs/ /tools/risk-calculator/ /self-hosted/ /for/langchain/` all 200 ✓
- `/checkout/team` still 302 → live Stripe ✓
- HSTS + CSP present ✓ | redirect keeps HSTS + X-Frame-Options ✓

## What was NOT touched
- `fly.toml` — 0 diff (verified)
- Secrets/env — none changed
- `api.py` business logic — only an additive redirect block mirroring the existing `/index.html → /` pattern
- No fabricated social proof, ratings, testimonials, or usage numbers

## Deploy command
```
flyctl deploy --remote-only --strategy rolling
```
Rolling strategy; machine `85e20ea4e77068` reached `started`, health check passing.
