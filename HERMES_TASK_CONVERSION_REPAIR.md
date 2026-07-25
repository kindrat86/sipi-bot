# HERMES TASK — sipi.bot Conversion Repair

**Target site:** sipi.bot (spend firewall for AI agents — approve/block/flag in <5 ms)
**Repo:** `~/projects/sipi-bot` — Python stdlib HTTP server, package `spendfirewall/`, branch **`buyers-guide-hub`**
**Host:** Fly.io app **`sipi-bot-firewall`** — deploy with `flyctl deploy`
**Authored:** 2026-07-22
**Executor:** Hermes Agent (DeepSeek v4 Pro), autonomous
**Real data (90 days):** 196 pageviews · 165 visitors · 192 sessions · **98.4% bounce** · `mcp_tool_called` = **492** (the API genuinely gets exercised)

**Objective:** The site promises a **free tier that does not exist in the billing system**, pre-ticks a **paid $7 upsell inside a "free" signup**, and quotes two different values for the same offer. Meanwhile the product's single best developer feature — **you can call the API right now, free, with no signup** — is real, live, and completely hidden. Fix the untruths and surface the truth.

---

## 0. READ THIS FIRST — SIX HARD RULES

### RULE 1 — THE FREE-TIER CLAIM IS FALSE, BUT THE REALITY IS *BETTER*. DO NOT JUST DELETE IT.

The sticky bottom bar (`spendfirewall/templates.py:768`) and the email drip (`spendfirewall/drip.py:442,453`) promise:
> **"5,000 checks/mo. No credit card."**

Verified against the code:
- `spendfirewall/billing.py:36-37` defines **exactly two** tiers — `team` ($99/mo) and `business` ($499/mo). **There is no free plan.** Nothing can issue a free key, so "Start Free" has nothing to sign up for.
- But `spendfirewall/api.py:914` — *"Auth optional in free/self-host mode"* — and `_RATE_LIMITS["evaluate"] = {"window": 60, "max": 100}` means **anonymous callers get 100 evaluate calls per minute per IP, with no key and no monthly cap.**

So the advertised number is fiction, and the truth is **far more generous**: a developer can `curl` the endpoint this second, free, forever, without an account. Your job is to **replace the fictional metered tier with the real, verifiable, better offer** — not to delete the free positioning.

**You may not invent a new number.** Any figure you publish must come from `_RATE_LIMITS` in `spendfirewall/api.py`, read at the time you edit.

### RULE 2 — DO NOT CHANGE `billing.py`, `_RATE_LIMITS`, OR ANY TIER CONFIG
Changing `_RATE_LIMITS` alters live abuse protection and what real API consumers receive. Changing `TIERS` alters what paying customers get. **The code is the truth; the copy gets corrected to match it.** Never the reverse.

### RULE 3 — THE STRIPE "MicroSaaS" NAME IS OWNER-GATED. REPORT ONLY.
Stripe Checkout for `/checkout/team` correctly charges **$99.00/month for "sipi.bot Team"**, but the page's business name shows **"MicroSaaS"**. That is a **Stripe Dashboard → Business settings → Public details** field, not code. You have no credentials and must not attempt it. (The same defect affects gitdealflow.com — they share a Stripe account, so one fix likely resolves both.) **Record it; do not touch the checkout flow.**

### RULE 4 — NO `api.py` RESTRUCTURING
`spendfirewall/api.py` is the whole server and serves pages inline. **Single-line, targeted edits only.** No reformatting, no regeneration, no bulk substitution, no formatter runs. `api.py` failing to parse is a total outage on a live API that other systems call.

### RULE 5 — NEVER FABRICATE PROOF
This site has **no testimonials, logos, reviews, or case studies** anywhere — and it should stay that way until real ones exist. Do not invent customer counts, usage figures, or quotes.

### RULE 6 — SCOPE: NEVER `git add -A`
Untracked and not yours: `.hermes/`, `HERMES_TASK_BUYERS_GUIDE_HUB.md`. Stage only files you personally edit, by explicit path.

---

## 1. PRE-FLIGHT (abort conditions)

```bash
cd ~/projects/sipi-bot
```

**1.1 — Branch, tree, rollback point.**
```bash
git branch --show-current    # expect: buyers-guide-hub
git status --short           # expect ONLY: ?? .hermes/  ?? HERMES_TASK_BUYERS_GUIDE_HUB.md
git rev-parse HEAD           # RECORD — rollback target
```
**ABORT** if `spendfirewall/` has uncommitted edits.

**1.2 — Another agent active?**
```bash
ps aux | grep -i hermes | grep -v grep
```
**ABORT** if anything references `sipi-bot`, `spendfirewall`, or a `flyctl` deploy in flight.

**1.3 — Author + Fly reachability.**
```bash
git config user.email                       # MUST be sales@sipiteno.com
flyctl status -a sipi-bot-firewall | head -12
```

**1.4 — Re-read the two ground-truth values yourself (RULE 1/2). Do not trust this document's numbers.**
```bash
sed -n '30,40p' spendfirewall/billing.py          # the ONLY tiers that exist
grep -n -A6 "_RATE_LIMITS = {" spendfirewall/api.py   # the REAL anonymous limits
```

**1.5 — Prove the free path actually works before you advertise it.**
```bash
curl -s -X POST https://sipi.bot/v1/transactions/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"amount": 12400, "currency": "USD", "merchant": "example-vendor"}' | head -20
```
**If this does NOT return a decision without an API key, STOP.** The entire premise of Step 3.1 is that anonymous calls work. Record the actual response and escalate instead.

**1.6 — Regression baseline.**
```bash
for u in / /pricing /dashboard /masterclass /docs; do
  printf "%-16s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' https://sipi.bot$u)"
done   # ALL should be 200
```

---

## 2. THE DIAGNOSIS

### 2.1 — P0: A promised free tier that cannot be signed up for
See RULE 1. The claim appears in at least four places:
```bash
grep -rn "5,000 checks\|no credit card\|No credit card" spendfirewall/ | grep -v __pycache__
```
- `templates.py:157`, `templates.py:768` — site copy / sticky bar
- `drip.py:442`, `drip.py:453` — **the email sequence repeats the promise to every subscriber**

The drip occurrences matter most: those go to people who already trusted you with an address.

### 2.2 — P0: A pre-checked paid upsell inside a "free" opt-in

`spendfirewall/templates.py:547`:
```html
<input type="checkbox" id="order-bump" checked ...>
```
A **$7 "First $10K Safe deployment checklist"** is **pre-ticked** on the free 5-day email playbook form. A visitor opting into something labelled *free* is defaulted into a paid purchase. This is a dark pattern, it inflates refunds and chargebacks, and it poisons trust for the $99 ask that follows.

### 2.3 — P1: The same offer is worth two different amounts

Same file, two totals for the same $99/mo offer:
- `spendfirewall/templates.py:487` → **$2,500/mo** value (homepage)
- `spendfirewall/templates.py:1371` → **$1,295/mo** value (masterclass)

A comparison-shopping developer who opens both pages sees the value stack is arbitrary.

### 2.4 — P1: Six competing CTAs, none of them the free path

The hero alone offers: *Protect my agent* → `/pricing`, *See how it works* → `#how`, *Free masterclass* → `/masterclass`, plus a nav *Live Dashboard* → `/dashboard`, plus a sticky *Start Free* bar, plus two separate email forms. **Every one of them leads to either a payment page or an email capture — none leads to the working, no-signup API call.**

### 2.5 — P1: `/dashboard` shows demo data without saying so

The public "Control Room" renders a live-looking feed of BLOCKED/APPROVED/FLAGGED transactions with counters, viewable without login and **not labelled as demo/sample data**. Presenting synthetic activity as if it were live customer traffic is the same category of problem as a fabricated testimonial.

### 2.6 — P2: A false "You are offline" banner

*"You are offline. Some features may be unavailable."* appears at the bottom of normally-loading pages — the same PWA symptom seen across sister sites.

### 2.7 — Things that are RIGHT — do not "fix" them

- **Anonymous API access at 100 calls/min/IP** — the best conversion asset on this property. Surface it; do not restrict it.
- **The rule-integrity guarantee** ("month is free if it wrongly approves a spend") — a real, specific risk reversal.
- **Stripe charges the correct $99.00/month for "sipi.bot Team"** — the *price* is right; only the displayed business name is wrong (RULE 3).
- **No fabricated testimonials anywhere.** Keep it that way.

---

## 3. EXECUTION

### STEP 3.1 — Replace the fictional free tier with the real one (the core fix)

**3.1a — Establish the true, publishable claim** from `_RATE_LIMITS` (read in 1.4) and the successful call in 1.5. The honest framing is roughly:

> **Free, no signup, no credit card — call the API right now.** Up to *N* checks per minute per IP, no account required.

where *N* is the verified `evaluate` `max` value. **Do not** publish a monthly figure — there is no monthly quota for anonymous use, so any "/mo" number would be invented.

**3.1b — Correct every occurrence** found in 2.1, in both `templates.py` **and** `drip.py`. The drip emails must not keep promising a metered tier that cannot be provisioned.

**3.1c — Give "Start Free" a real destination.** Today it implies a signup that does not exist. Point it at the working curl example / docs anchor — the thing a developer can actually do. **Do not point it at `/pricing`.**

**Gate 3.1:**
```bash
grep -rn "5,000 checks" spendfirewall/ | grep -v __pycache__ | wc -l     # MUST be 0
grep -rn "checks/mo\|checks/month" spendfirewall/templates.py spendfirewall/drip.py | wc -l   # MUST be 0 for the free tier
git diff --stat spendfirewall/billing.py spendfirewall/api.py            # billing.py MUST be empty; api.py only if you edited a page string
python3 -c "import ast;[ast.parse(open(f).read()) for f in ['spendfirewall/templates.py','spendfirewall/drip.py','spendfirewall/api.py']];print('parse OK')"
```

---

### STEP 3.2 — Un-tick the paid upsell

**File:** `spendfirewall/templates.py:547` — remove the `checked` attribute from `id="order-bump"`.

Keep the offer itself: the $7 checklist may remain as an **opt-in** checkbox the user actively ticks. Only the default changes. Ensure the price is stated adjacent to the checkbox so a ticked box is unambiguous.

**Gate 3.2:**
```bash
grep -n 'id="order-bump"' spendfirewall/templates.py    # MUST NOT contain `checked`
python3 -c "import ast;ast.parse(open('spendfirewall/templates.py').read());print('OK')"
```

---

### STEP 3.3 — One value-stack total

Pick **one** figure and use it in both places (`templates.py:487` and `templates.py:1371`). Prefer the **lower, more defensible** total ($1,295/mo) unless the itemised stack genuinely sums to the higher one — **add up the line items and use the real sum.** Do not average them and do not invent a third number.

**Gate 3.3:**
```bash
grep -c '\$2,500/mo' spendfirewall/templates.py
grep -c '\$1,295/mo' spendfirewall/templates.py    # exactly one of these MUST be 0
```

---

### STEP 3.4 — Label the dashboard as demo data

Add a clear, visible label to `/dashboard` — e.g. a badge reading **"Demo data — sample traffic, not live customer transactions."** It must be visible without scrolling and adjacent to the activity feed, not buried in a footer.

**Do not remove the dashboard** — it demonstrates the product well. It simply must not imply real customer volume.

**Gate 3.4:** the string appears in the dashboard template; `python3 -c "import ast;ast.parse(...)"` passes.

---

### STEP 3.5 — Put the working API call on the homepage

This is the highest-value *addition* in this task and it costs almost nothing: the product's best feature already works and is invisible.

Place the verified curl example from 1.5 directly in the hero area (or immediately below it), with a one-line frame: *"Try it right now — no signup, no key."* Show a real request and a real response shape.

Constraints:
- Use the **exact** endpoint and payload you verified in 1.5. Do not invent fields.
- Reduce the hero to **one** primary CTA (*Protect my agent*) plus this free-try block; demote *See how it works*, *Free masterclass*, and *Live Dashboard* to secondary text links (2.4).
- **Do not** add a JS-powered live sandbox widget in this task — a static, copy-pasteable curl is lower risk in an 836-line-per-route inline template and achieves the same thing.

**Gate 3.5:** homepage contains the curl block; exactly one primary-styled hero CTA remains; `api.py`/`templates.py` parse.

---

### STEP 3.6 — The false "You are offline" banner (investigate; skip if unclear)

```bash
grep -rn "You are offline\|navigator.onLine\|serviceWorker" spendfirewall/ public/ 2>/dev/null | grep -v __pycache__ | head
```
Safe minimal fix: show it only when `navigator.onLine === false`, never on a failed fetch. **Do not** rewrite caching or unregister a service worker. If the cause is not obvious, **skip and record**.

---

## 4. VALIDATION (before deploy)

```bash
cd ~/projects/sipi-bot

# 4.1 Everything still parses — api.py IS the live server
python3 -c "import ast;[ast.parse(open(f).read()) for f in ['spendfirewall/api.py','spendfirewall/templates.py','spendfirewall/drip.py','spendfirewall/billing.py']];print('ALL PARSE OK')"
python3 -c "import spendfirewall.api" 2>&1 | head -5

# 4.2 The fiction is gone
grep -rn "5,000 checks" spendfirewall/ | grep -v __pycache__ | wc -l    # 0

# 4.3 Engine/billing/limits untouched (RULE 2)
git diff --stat spendfirewall/billing.py spendfirewall/engine.py spendfirewall/core.py   # EMPTY
git diff spendfirewall/api.py | grep -c "_RATE_LIMITS"                                   # 0

# 4.4 No pre-checked upsell
grep -n 'id="order-bump"' spendfirewall/templates.py | grep -c "checked"                 # 0

# 4.5 No fabricated proof introduced
git diff | grep -ciE "testimonial|customers trust|[0-9,]+\+ (developers|teams|agents) (use|trust)"   # 0

# 4.6 Infra untouched
git diff --name-only | grep -cE "fly.toml|Dockerfile"    # 0

# 4.7 Smoke tests (this repo ships them — use them)
python3 smoke_test.py 2>&1 | tail -10
python3 smoke_billing.py 2>&1 | tail -10
```

**Do not deploy if anything fails to parse or if `smoke_test.py` regresses.**

---

## 5. COMMIT & DEPLOY

**5.1 — Stage explicitly (RULE 6).**
```bash
git add spendfirewall/templates.py spendfirewall/drip.py
# add spendfirewall/api.py ONLY if you edited a page string there
git status --short   # REVIEW: .hermes/ and HERMES_TASK_*.md must NOT be staged
```

**5.2 — Commit.**
```bash
git commit -m "fix(sipi.bot): advertise the free access that actually exists, un-tick the paid upsell

- The sticky bar and drip emails promised '5,000 checks/mo, no credit card',
  but billing.py defines only team (\$99) and business (\$499) — no free plan
  exists to sign up for. The real offer is better: api.py allows anonymous
  evaluate calls with no key. Copy now states the verified rate limit and
  'Start Free' points at the working curl instead of a signup that doesn't exist.
- Un-tick the pre-checked \$7 order bump inside the free email opt-in.
- Single value-stack total across homepage and masterclass.
- Label /dashboard as demo data.

billing.py, _RATE_LIMITS, engine and fly.toml unmodified."
```

**5.3 — Deploy.**
```bash
flyctl deploy -a sipi-bot-firewall
```
No secrets, no config change. If the deploy fails, read the error — **do not** retry with modified `fly.toml`, changed machine sizes, or new secrets.

---

## 6. POST-DEPLOY VERIFICATION

```bash
sleep 30

# 6.1 The API still works — this is a live service other systems call. CHECK FIRST.
curl -s -X POST https://sipi.bot/v1/transactions/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"amount": 12400, "currency": "USD", "merchant": "example-vendor"}' | head -20
# MUST return a decision, exactly as in step 1.5

# 6.2 Pages up
for u in / /pricing /dashboard /masterclass /docs; do
  printf "%-16s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' https://sipi.bot$u)"
done   # ALL 200

# 6.3 The fiction is gone from the served site
curl -s https://sipi.bot/ | grep -c "5,000 checks"     # MUST be 0

# 6.4 Value stack consistent across both pages
curl -s https://sipi.bot/ | grep -oE '\$(2,500|1,295)/mo'
curl -s https://sipi.bot/masterclass | grep -oE '\$(2,500|1,295)/mo'   # MUST match

# 6.5 Dashboard labelled
curl -s https://sipi.bot/dashboard | grep -ci "demo data"   # MUST be >= 1

# 6.6 Machine config survived
flyctl config show -a sipi-bot-firewall | grep -E "auto_stop_machines|min_machines_running"
# expect: auto_stop_machines = false, min_machines_running = 1
```

**6.7 — Rendered check:** open the homepage in a fresh incognito window. Confirm the curl block is visible, the hero has one primary CTA, the order-bump checkbox is **unticked**, and no "You are offline" banner appears.

**Rollback:**
```bash
git revert --no-edit HEAD && flyctl deploy -a sipi-bot-firewall
# faster for an outage:
flyctl releases -a sipi-bot-firewall
```

---

## 7. REPORT (write this file, always — even on abort)

Write `~/projects/sipi-bot/HERMES_REPORT_CONVERSION_REPAIR.md` with:

1. **The verified free-access facts** — the exact `_RATE_LIMITS["evaluate"]` values you read, the raw response from step 1.5, and the exact wording you published. This is the evidence that the new claim is true.
2. **Every occurrence corrected**, in `templates.py` **and** `drip.py`, with line numbers. Call out the drip fixes separately — those emails go to people who already subscribed under the old promise.
3. **Confirmation** that `billing.py`, `_RATE_LIMITS`, `engine.py`, `core.py` and `fly.toml` are unmodified.
4. **Smoke-test output** (`smoke_test.py`, `smoke_billing.py`) before and after.
5. **Post-deploy API check (6.1)** — the live `evaluate` call must still return a decision.
6. **Escalate to owner:**
   - **Stripe Checkout shows "MicroSaaS" instead of "sipi.bot"** — Stripe Dashboard → Business settings → Public details. Owner-only. **The same defect affects gitdealflow.com; they appear to share a Stripe account, so one change likely fixes both.**
   - **Should a real hosted free tier exist?** Anonymous access works but issues no key, so there is no identity, no usage visibility, and no upgrade path. A genuine free tier in `TIERS` (key-issuing, metered) would create the PLG loop this product is otherwise well-suited to. That is a product decision, not a copy fix.
   - **Anyone who subscribed to the drip before this change was promised "5,000 checks/mo, no credit card."** The owner should decide whether to send a correction to that list.
   - The site has **no testimonials or case studies**, correctly. `mcp_tool_called` = 492 suggests real usage exists — the owner may be able to source genuine proof from actual API consumers.

---

## 8. WHAT SUCCESS LOOKS LIKE

- No page or email promises "5,000 checks/mo"; the published free claim matches `_RATE_LIMITS` exactly.
- "Start Free" leads to something a developer can actually do — not a signup that cannot be provisioned.
- The homepage shows a working, copy-pasteable, no-signup API call, and the hero has **one** primary CTA.
- The $7 order bump is **unticked** by default.
- One value-stack total sitewide.
- `/dashboard` says "demo data".
- `billing.py`, `_RATE_LIMITS`, `engine.py`, `core.py`, `fly.toml` **unmodified**; smoke tests pass; the live `evaluate` endpoint still returns decisions after deploy.
- `.hermes/` and `HERMES_TASK_BUYERS_GUIDE_HUB.md` were never staged.

**The deepest point:** this site is selling a $99/mo subscription to developers while hiding the one thing developers actually want — the ability to try it in five seconds without talking to anyone. That capability **already exists and already works**: `POST /v1/transactions/evaluate` answers anonymous calls at 100/minute with no key. Instead of showing it, the page advertises a free tier that was never built, pre-ticks a $7 charge inside a "free" signup, and offers six CTAs that all lead to a payment page or an email form. Stop selling the trial and just give it away — the product is good enough that the curl block *is* the pitch.
