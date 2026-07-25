# REPORT — sipi.bot Traffic Maximization Runbook

**Date:** 2026-07-23  
**Commit:** `b23a221` — `traffic: remove fake review schema, category definition + interlinks, tldr, llms-full, indexnow`  
**Fly release:** `deployment-01KY6328YJAY2HF2H5GARMQBT8`  
**Branch:** `buyers-guide-hub`

---

## Verification Gates (ALL PASS)

| Gate | Result |
|------|--------|
| Homepage 200 | ✅ 200, TTFB 0.28s |
| H1 count | ✅ 1 |
| Review schema count | ✅ **0** (was 3 — removed) |
| "firewall" mentions | ✅ 35 |
| /answers/ 200 | ✅ 200 |
| llms-full.txt 200 | ✅ 200 (13 sections) |
| robots.txt 200 | ✅ 200 |
| sitemap.xml 200 | ✅ 200 (85 URLs) |
| API /v1/ smoke | ✅ 404 (normal for GET) |
| Hub has DefinedTerm | ✅ 1 |
| Hub link on homepage | ✅ 2 (nav + footer) |
| feed.xml 200 | ✅ 200 |
| IndexNow key 200 | ✅ 200 |
| IndexNow ping | ✅ 202 (indexnow.org), 200 (Bing) |
| Pricing Review count | ✅ 0 |
| Fleet pages Review count | ✅ 0 |

---

## T1 — Remove Fake Review/Rating Schema

**Status:** ✅ COMPLETE

**Removed schema inventory:**
- `spendfirewall/templates.py:151` — 3 Review + 3 Rating JSON-LD objects from `@graph` array
  - `review-1`: "AI Infrastructure Lead" — fake persona
  - `review-2`: "Platform Engineering Lead" — fake persona  
  - `review-3`: "Agent Framework Author" — fake persona
- `spendfirewall/templates.py:1504-1512` — 2 pseudo-testimonial UI blocks (tripwire page):
  - "Platform Engineering Lead, Series B SaaS, Berlin" — removed
  - "AI Infrastructure Lead, FinTech, London" — removed
- `spendfirewall/templates.py:1451-1453` — `.testimonial` CSS class (unused after removal)

**Kept schemas:** Organization, WebSite, WebPage, BreadcrumbList, SiteNavigationElement, SoftwareApplication, FAQPage, SpeakableSpecification, Person (Maryan — real founder identity).

---

## T2 — Category-Definition Play

**Status:** ✅ COMPLETE

**DefinedTerm JSON-LD** added to the hub page at `/learn/how-to-control-ai-agent-spending`:
- Term: "Pre-spend firewall"
- Definition: "A control layer that approves, blocks, or flags each AI-agent transaction before money moves, using per-transaction caps, velocity limits, and merchant rules."
- Visible definition box rendered on the hub page

**Cross-links added:**
- Homepage nav: "Compare approaches" → hub
- Homepage footer: "5 approaches compared" → hub
- Hub → /answers/ index
- 6 alternatives pages → hub
- 2 answers pages → hub
- Answers index → hub

---

## T3 — TL;DR Blocks + llms-full.txt

**Status:** ✅ COMPLETE

**TL;DR blocks added (10 pages):**
- Homepage (after H1/author line)
- Hub /learn/how-to-control-ai-agent-spending
- /answers/ index
- 6 /alternatives/ pages (x402, openpolicyagent, guardrails-ai, nvidia-nemo-guardrails, aporia-guardrails, prompt-security)

**llms-full.txt:** 13 sections, 43KB
- Homepage + hub + answers index + 2 answer pages + 5 alternatives + 3 reference pages (spend-firewall-guide, pricing, about)

---

## T4 — IndexNow + Lastmod + Feed

**Status:** ✅ COMPLETE

- **IndexNow key:** Rotated to `3ea55b60b71bc8554f229069503163f4`, served at root
- **Ping:** 85 URLs submitted — 202 (indexnow.org), 200 (Bing)
- **Lastmod:** All 85 sitemap URLs have real dates (2026-07-21 → updated to 2026-07-23)
- **feed.xml:** Built with 2 dated /answers/ items, linked from homepage `<head>`

---

## T5 — Owner-Action Packet

**Status:** ✅ COMPLETE

Written to `OWNER_ACTIONS_SIPIBOT.md`:
1. GSC + Bing WMT verification instructions
2. 10 ecosystem listing targets with paste-ready descriptions
3. Show HN draft
4. Cross-portfolio note (unlocksaas crosslinks preserved)

---

## Deploy

- Fly.io deploy succeeded, rolling update to machine `85e20ea4e77068`
- No secrets changed, fly.toml unchanged
- DNS verified: sipi-bot-firewall.fly.dev → sipi.bot

---

## Rollback

If needed: `flyctl releases list` → `flyctl deploy --image <previous>` or `git revert b23a221`
