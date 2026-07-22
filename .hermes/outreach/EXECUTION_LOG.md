# sipi.bot — AEO/SEO Remediation Log

## 2026-07-21 — TASK-01 + TASK-03 deliverables

### Deployed code fixes
- **TASK-01**: ✅ Added `/benchmarks/` (spend benchmarks) and `/best/` (best-of comparisons) links to homepage footer — live after `flyctl deploy` (commit `eca46e6`)
- **TASK-02**: 🚫 Deferred — `doc_page_html()` footer region still has an active uncommitted diff hunk (35-line insertion). Re-attempt when region settles

### Third-party trust signals (TASK-03) — deliverables produced
- **Outreach kit**: `.hermes/outreach/sipi-bot-outreach-kit.md` — press targets, pitch templates, GH star seeding strategy, case study template, Product Hunt/Indie Hackers launch plan
- **Case study**: `.hermes/outreach/sipi-bot-case-study.md` — 500-word publish-ready origin story (the $12.4k incident), ready for `/blog` route creation and cross-posting to dev.to/Medium

### Already correct (no action needed)
- SoftwareApplication+Offer schema already exists on homepage — audit's top finding was a false positive
- CSP trusted-types correctly paired with inline default-policy registration

### Post-deploy verification (all passed)
| Check | Result |
|---|---|
| `/benchmarks/` on homepage | 1 match |
| `/best/` on homepage | 1 match |
| SoftwareApplication schema | 1 match |
| All routes (/, /pricing, /about, /dashboard, /benchmarks/, /best/) | All 200 |

### 2026-07-21 — TASK-03 synthetic testimonials removed

- **Action**: Removed entire "What Builders Say" section from `landing_page_html()` — 3 anonymous synthetic quotes (AG/MS/RK) that had no real user attribution.
- **Investigation**: Session history confirmed these were generated during a Brunson audit run on July 19 as part of Expert Secrets Ch.10 scoring. The subheader claimed "No invented quotes" but the origin was synthetic.
- **Fix**: Replaced 29 lines of fake testimonials + subheader with a single comment marker noting the removal and that the section should only be restored with verified named testimonials.
- **Deploy**: `flyctl deploy` (commit `75e43bb`) — initial attempt hit Fly nil-pointer on unreachable machine `825475b79ee518`; retried with `--strategy immediate` which force-replaced the broken machine. Machine 237 (version 237) now running with health check passing.
- **Verification**: `curl https://sipi.bot/ | grep -c 'What Builders Say'` → 0. Section gone live.
