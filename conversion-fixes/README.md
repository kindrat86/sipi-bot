# sipi.bot conversion fixes — verified, deploy-ready

Two surgical fixes produced by the 2026-07-27 conversion audit. Both were
validated locally (py_compile clean, JSON-LD parses, honesty gate respected).
NOT yet deployed because a live Hermes agent was actively writing to the repo
(gzip + benchmark work), creating a race that made autonomous deploy unsafe.

## How to apply (when Hermes is paused)
1. `git checkout main && git pull`
2. `git checkout -b conv/pricing-schema-and-redirects`
3. `git apply conversion-fixes/01-pricing-jsonld.patch`
4. `git apply conversion-fixes/02-hub-redirects.patch`
5. `python3 -m py_compile spendfirewall/api.py spendfirewall/templates.py`
6. `git commit -am "conv: pricing Product/FAQ schema + /compare & /calculator redirects"`
7. `flyctl deploy`  (fly.toml unchanged, no secrets touched)
8. Verify (see VERIFY.md)

## Honesty gate respected
- No fabricated AggregateRating / reviews / testimonials (config.yaml rule).
- Stripe shows ZERO subs (plan.md) — so no social proof was invented.
- FAQ schema mirrors the EXISTING visible <details> FAQ, word for word.
