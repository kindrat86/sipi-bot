# Hermes Autonomous Execution Brief — sipi.bot AEO/SEO Remediation

**Target repo:** `~/projects/sipi-bot` (branch `main`, last commit at time of writing: `ee7c3d8`, 2026-07-20)
**Live domain:** https://sipi.bot, served by Fly.io app `sipi-bot-firewall` (region `iad`) — **not Vercel.** Prior portfolio tracking notes claiming a Vercel project `sipi-bot` and that the site was dead as of 2026-07-06 are stale/incorrect; the site is fully live today on Fly.
**Deploy command:** `flyctl deploy` from `~/projects/sipi-bot` (app name set in `fly.toml`)
**Source audit:** 10-site portfolio AEO/SEO audit, 2026-07-21, sipi.bot scored 85/100 — the highest score in the portfolio audit — with 0 critical + 2 medium + 3 low findings.
**Executor:** Hermes Agent (autonomous, DeepSeek v4 Pro). This document is your complete task spec — do not improvise scope beyond what's written here.

**Important methodology note:** this site scored highest in the portfolio for a reason — the technical AEO/schema work here is already unusually thorough. Verification found the audit's own top finding does not reproduce at all (the exact schema it says is missing already exists, live, in production) — see §3. What's left after removing that is a much smaller, more surgical set of real gaps than any other brief in this portfolio.

---

## 0. Read this whole section before touching anything

### 0.1 Collision check — mandatory first step, every run

```bash
ps aux | grep -i hermes | grep -v grep
cd ~/projects/sipi-bot && git status --short | wc -l && git log -1 --format='%H %ci'
```

**At brief-writing time this repo had 87 modified/untracked files**, including `spendfirewall/templates.py` itself (the single file every task below touches) with a large in-progress diff (+380/-12 lines across several separate hunks). This is a real, active concurrent edit, not as extreme as some sibling repos in this portfolio but still significant.

- If a Hermes process is running against `~/projects/sipi-bot`, or a deploy landed in the last ~30 minutes, wait and re-check every 10 minutes.
- **Before editing `templates.py`, run `git diff spendfirewall/templates.py | grep '^@@'` and check whether the hunk covering the shared `doc_page_html()` footer function (look for a hunk near the `def doc_page_html` docstring, roughly the 830-860 line range as of this writing) is still active.** At brief-writing time that exact region had a 35-line in-progress insertion — this is precisely the area TASK-02's second half would touch. If that hunk is still present/growing, **skip the `doc_page_html()` footer edit in TASK-02 and do only the homepage footer edit**, which sits in a separate, more stable region of the file (`landing_page_html()`, confirmed not part of any current diff hunk as of this writing). Re-attempt the `doc_page_html()` footer edit on a later run once that region has settled (been committed or gone quiet).
- Do not `git add -A` given how much else is in flight in this file and repo — stage only the exact lines/files your own edits touch.

### 0.2 Trusted-Types CSP — this one is currently FIXED, and unusually well-explained in-repo

This site's CSP carries `require-trusted-types-for 'script'`, the exact directive that blanked two sibling sites in this portfolio for ~40 hours each — but here it's correctly paired with an inline default-policy registration in `<head>`, before any other script runs, confirmed both in `spendfirewall/templates.py` and live in production. **No task below touches this — do not modify anything in the `<head>` script-ordering for any reason.**

### 0.3 Guardrails you must never bypass

- Never use `git commit --no-verify`. Always create new commits; never `git commit --amend` on a pushed/deployed commit. Never `git push --force` to `main`.
- `fly.toml` already has `auto_stop_machines = false` and `min_machines_running = 1` — correct, no cold-start risk on this app (unlike a sibling Fly-hosted site in this portfolio that has had this setting revert on deploy). Don't touch these values; just don't be surprised if you don't need to fix anything here, this is a "leave it alone, it's already right" note, not a task.

### 0.4 What you are NOT authorized to change autonomously

See §6 "Owner-gated — do not execute" at the bottom. Anything not explicitly listed as a task in §1–§2 is out of scope.

---

## 1. P3 — LOW (this portfolio's smallest, most surgical brief — most of the audit's findings are either already fixed or not code fixes)

### TASK-01: Add `/benchmarks` and `/best` hub links to the homepage footer

**File:** `~/projects/sipi-bot/spendfirewall/templates.py`, the `landing_page_html()` function's footer block (confirmed at ~line 587-599 as of this writing — re-locate by searching for `<footer><div class="wrap">` followed by `Framework integrations:` to confirm you're editing the homepage footer, not one of the other 4 `<footer>` occurrences in this file).

**Root cause (confirmed):** The homepage footer already links `/for/` (framework integrations) and `/vs/`, `/alternatives/` (compare & alternatives) — reasonably good hub coverage. But a repo-wide grep for `/benchmarks` or `/best` links across the entire `templates.py` file (which covers every page on the site, not just the homepage) returns only 2 total matches, both unrelated to these two hub families. The live sitemap has 84 URLs; `/benchmarks/*` and `/best/*` are real, populated hub families (confirmed via `curl https://sipi.bot/sitemap.xml`) that currently have **zero** in-content links pointing to them from anywhere on the site — they rely entirely on sitemap-only discovery, which is real but weaker than crawled internal links for PageRank/link-equity flow.

**Fix:** In the homepage footer's "Compare & alternatives" line, add two more links:
```html
<div style="margin-bottom:16px;font-size:13px;line-height:2">
    <strong style="color:var(--txt)">Compare & alternatives:</strong>
    <a href="/vs/hardcoded-check/">vs hardcoded budget check</a> ·
    <a href="/vs/stripe-radar/">vs Stripe Radar</a> ·
    <a href="/alternatives/x402/">x402 alternative</a> ·
    <a href="/self-hosted/">self-hosted / open source</a> ·
    <a href="/benchmarks/">spend benchmarks</a> ·
    <a href="/best/">best-of comparisons</a>
</div>
```
(Confirm `/benchmarks/` and `/best/` resolve to real hub index pages before adding — `curl -s -o /dev/null -w "%{http_code}" https://sipi.bot/benchmarks/` and same for `/best/`, both must be 200.)

**Verification (before commit):**
```bash
cd ~/projects/sipi-bot
grep -n 'href="/benchmarks/"' spendfirewall/templates.py   # must find your new addition
grep -n 'href="/best/"' spendfirewall/templates.py
python3 -c "import ast; ast.parse(open('spendfirewall/templates.py').read())"   # must not error — confirms the file is still valid Python
```

### TASK-02: Same fix for the shared pSEO-page footer (`doc_page_html()`) — conditional on §0.1's collision check

**File:** same file, the `doc_page_html()` function's footer (near where `Find us where builders are:` appears) — this is a shared template used to render the other ~80 pSEO pages, so a fix here has much broader reach than TASK-01 alone.

**Only attempt this if §0.1's collision check confirms this specific region of the file is no longer part of an active uncommitted diff hunk.** If it's still in flux, skip this task entirely for this run and note it as deferred in your execution log — do not force an edit into actively-changing code.

**Fix (same pattern as TASK-01, adapted to this footer's existing structure):**
```html
<div style="margin-top:14px;color:var(--mut);font-size:13px">
    <a href="/benchmarks/">Benchmarks</a> ·
    <a href="/best/">Best-of comparisons</a> ·
    Find us where builders are:
    <a href="https://github.com/kindrat86/sipi-bot" rel="me noopener">GitHub</a> ·
    <a href="https://pypi.org/project/sipi-bot/" rel="me noopener">PyPI</a> ·
    <a href="https://x.com/sipiteno" rel="me noopener">X / Twitter</a> ·
    <a href="/.well-known/mcp.json">MCP manifest</a> ·
    <a href="/agents.md">Agent guide</a>
</div>
```
(Match this to whatever the actual current structure of that footer is once you re-check it — the exact wrapping HTML may have shifted given the in-progress edit noted in §0.1; the important part is adding the two new links, not reproducing this snippet verbatim if the surrounding markup has changed.)

**Verification (before commit):**
```bash
cd ~/projects/sipi-bot
python3 -c "import ast; ast.parse(open('spendfirewall/templates.py').read())"   # must not error
```

---

## 2. Verify-only, no code changes authorized

### TASK-03: E-E-A-T third-party trust signals — flag only

Single-founder attribution, no independent press/reviews/case studies found. This is real for a payments-adjacent product, but adding testimonials or pursuing external citations is content/business-development work, not a code fix. Not actioned in this brief.

### TASK-04: Core Web Vitals — verify with real data if possible, don't guess

No real Lighthouse/CrUX data has been pulled for sipi.bot specifically. If you have rendering capability, run a real check and report actual numbers in your execution log. If not, skip — the proxy signals (71.7KB HTML, ~14KB JS, server-rendered) already suggest this is a low-priority item regardless.

---

## 3. Findings from the source audit that did NOT reproduce — corrected here

- **"No SoftwareApplication/Product schema with offers/pricing despite a live /pricing page"** — **false, and this was the audit's only medium-severity finding for this site.** A full `SoftwareApplication` JSON-LD node already exists on the homepage (`"@id":"https://sipi.bot/#app"`), complete with `"offers":{"@type":"Offer","price":"99","priceCurrency":"USD"}`, `applicationCategory`, `featureList`, and a `disambiguatingDescription`. Confirmed present both in the last git commit (`ee7c3d8`, not part of any uncommitted change) and live in production via direct `curl`. No action needed — this appears to have already been fixed since whatever state the audit's source data reflected, or the audit simply missed it in the page's `@graph` array. Do not add a duplicate `SoftwareApplication` node.

---

## 4. Deploy protocol — follow exactly, in order

1. Re-run the §0.1 collision check, including the specific hunk-location check for `doc_page_html()`.
2. Make TASK-01 (always) and TASK-02 (only if safe per §0.1) edits.
3. Run every verification command. All must pass before committing.
4. Commit:
   ```bash
   cd ~/projects/sipi-bot
   git add spendfirewall/templates.py
   git commit -m "fix: add /benchmarks and /best hub links to site footer(s) for internal link equity"
   ```
   (If only TASK-01 was safe to do, the commit message and diff will just cover the homepage footer — that's fine, don't force TASK-02 in.)
5. Deploy:
   ```bash
   flyctl deploy
   ```

**If any step fails, do not proceed to the next step and do not force through it.** Report the exact error in your execution log (§7) and stop.

---

## 5a. Post-deploy verification — mandatory

```bash
# 1. Confirm new footer links are live on the homepage
curl -s https://sipi.bot/ | grep -c 'href="/benchmarks/"'
curl -s https://sipi.bot/ | grep -c 'href="/best/"'

# 2. If TASK-02 was done, confirm it's live on a sampled pSEO page too
curl -s https://sipi.bot/vs/stripe-radar/ | grep -c 'href="/benchmarks/"'

# 3. Confirm the SoftwareApplication+Offer schema is still intact (should be untouched, but confirm nothing broke)
curl -s https://sipi.bot/ | grep -c '"@type":"SoftwareApplication"'   # must be 1

# 4. Confirm the homepage and a few other routes are still fine
for path in / /pricing /about /dashboard /benchmarks/ /best/; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://sipi.bot$path")
  echo "$path: $code"
done   # all must be 200
```

## 5b. Rollback plan — use immediately if §5a verification fails

```bash
cd ~/projects/sipi-bot
flyctl releases -a sipi-bot-firewall   # find the previous good release
flyctl releases rollback <version> -a sipi-bot-firewall   # or: git revert --no-edit HEAD && flyctl deploy
```

---

## 7. Execution log — append your results here as you work

```
### 2026-07-21 run
- TASK-01: done — added /benchmarks and /best links to homepage footer, verified live
- TASK-02: [done — doc_page_html() region had settled, added same links / deferred — region still actively being edited per §0.1]
- TASK-03: flagged for owner, no action taken (not a code fix)
- TASK-04: [outcome — real Lighthouse data if available, or "skipped: no rendering capability"]
- Confirmed already-correct (no action taken): SoftwareApplication+Offer schema already exists, audit's top finding was false
- Deploy: flyctl deploy succeeded
- Post-deploy verification: all checks passed
- No rollback needed
```

---

## 6. Owner-gated — do not execute autonomously

- **Third-party trust signals** (TASK-03) — testimonials, press, case studies are content/BD work, not a technical fix.
- **Portfolio tracking-memory correction** (sipi.bot runs on Fly, not Vercel; not dead) — this is a note for whoever maintains this owner's own cross-session tracking/memory system, not a repo change; not something for Hermes to act on.
- Anything not listed as a numbered TASK above.

---

**End of brief.** This is the smallest brief in the portfolio because this site is already in the best shape — resist the urge to invent additional work. Verify after the deploy per §5a, and re-check §0.1's specific hunk-location caution before attempting TASK-02.
