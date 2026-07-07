# sipi.bot Spend Firewall — Eval Report

**53/53 scenarios passed (100.0% accuracy)** · generated 2026-07-07T22:28:51Z

> We tested the firewall on 50 real spend scenarios an autonomous agent could hit — runaway loops, 3am compute buys, sketchy merchants, cumulative daily caps, and exact boundary values. Here's exactly how it did, including the tricky edge cases. This is the honesty behind the guarantee.

## By category

| Category | Passed | Total |
|---|---|---|
| approval_flag | 7 | 7 |
| category_limit | 4 | 4 |
| clean_approval | 7 | 7 |
| daily_limit | 4 | 4 |
| edge_case | 11 | 11 |
| merchant_block | 7 | 7 |
| per_tx_block | 5 | 5 |
| time_window | 3 | 3 |
| velocity | 5 | 5 |

## Every scenario

| # | Scenario | Expected | Got | ✓ |
|---|---|---|---|---|
| 1 | tiny coffee-money api call | APPROVED | APPROVED | ✅ |
| 2 | small compute spend | APPROVED | APPROVED | ✅ |
| 3 | just under approval flag | APPROVED | APPROVED | ✅ |
| 4 | modest ads spend | APPROVED | APPROVED | ✅ |
| 5 | cheap subscription | APPROVED | APPROVED | ✅ |
| 6 | zero-dollar auth check | APPROVED | APPROVED | ✅ |
| 7 | exactly at approval threshold | FLAGGED | FLAGGED | ✅ |
| 8 | mid-range flag | FLAGGED | FLAGGED | ✅ |
| 9 | just under per-tx block but flagged | FLAGGED | FLAGGED | ✅ |
| 10 | flag on ads | FLAGGED | FLAGGED | ✅ |
| 11 | exactly at per-tx limit (allowed) | FLAGGED | FLAGGED | ✅ |
| 12 | one cent over per-tx limit | BLOCKED | BLOCKED | ✅ |
| 13 | big single compute buy | BLOCKED | BLOCKED | ✅ |
| 14 | huge single spend | BLOCKED | BLOCKED | ✅ |
| 15 | block wins over flag | BLOCKED | BLOCKED | ✅ |
| 16 | pushes over daily cap | BLOCKED | BLOCKED | ✅ |
| 17 | exactly reaches daily cap (allowed edge) | FLAGGED | FLAGGED | ✅ |
| 18 | daily cap not yet reached | APPROVED | APPROVED | ✅ |
| 19 | daily cap with small txn still blocks | BLOCKED | BLOCKED | ✅ |
| 20 | 11th txn in an hour (runaway) | BLOCKED | BLOCKED | ✅ |
| 21 | 10th txn still allowed | APPROVED | APPROVED | ✅ |
| 22 | runaway loop of tiny charges | BLOCKED | BLOCKED | ✅ |
| 23 | blocklisted sketchy TLD | BLOCKED | BLOCKED | ✅ |
| 24 | blocklist pattern match | BLOCKED | BLOCKED | ✅ |
| 25 | clean merchant passes blocklist | APPROVED | APPROVED | ✅ |
| 26 | merchant not on allowlist | BLOCKED | BLOCKED | ✅ |
| 27 | merchant on allowlist | APPROVED | APPROVED | ✅ |
| 28 | allowlist flag instead of block | FLAGGED | FLAGGED | ✅ |
| 29 | ads over category cap | BLOCKED | BLOCKED | ✅ |
| 30 | ads under category cap | APPROVED | APPROVED | ✅ |
| 31 | category cap doesn't touch other categories | APPROVED | APPROVED | ✅ |
| 32 | category cap flag mode | FLAGGED | FLAGGED | ✅ |
| 33 | spend outside business hours | BLOCKED | BLOCKED | ✅ |
| 34 | spend inside business hours | APPROVED | APPROVED | ✅ |
| 35 | time window flag at night | FLAGGED | FLAGGED | ✅ |
| 36 | block beats flag on same txn | BLOCKED | BLOCKED | ✅ |
| 37 | merchant block beats approval flag | BLOCKED | BLOCKED | ✅ |
| 38 | negative amount treated as zero-ish | APPROVED | APPROVED | ✅ |
| 39 | flag when only approval rule trips | FLAGGED | FLAGGED | ✅ |
| 40 | daily block beats per-tx approval | BLOCKED | BLOCKED | ✅ |
| 41 | velocity block beats approval flag | BLOCKED | BLOCKED | ✅ |
| 42 | high priority merchant block over daily | BLOCKED | BLOCKED | ✅ |
| 43 | case-insensitive merchant match | BLOCKED | BLOCKED | ✅ |
| 44 | large travel booking flagged | FLAGGED | FLAGGED | ✅ |
| 45 | domain purchase small | APPROVED | APPROVED | ✅ |
| 46 | gpu rental blocked over per-tx | BLOCKED | BLOCKED | ✅ |
| 47 | api topup flagged mid | FLAGGED | FLAGGED | ✅ |
| 48 | many small under velocity ok | APPROVED | APPROVED | ✅ |
| 49 | category cap exact boundary allowed | APPROVED | APPROVED | ✅ |
| 50 | combined: daily near cap small ok | APPROVED | APPROVED | ✅ |
| 51 | flag then human territory | FLAGGED | FLAGGED | ✅ |
| 52 | blocklist plus under-limit amount | BLOCKED | BLOCKED | ✅ |
| 53 | clean high-freq legit ok | APPROVED | APPROVED | ✅ |

## 🎯 100% — every decision path verified.
