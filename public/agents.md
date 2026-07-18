# sipi.bot — Agent Reference

> sipi.bot is a spend firewall for autonomous AI agents — a real-time API that returns APPROVED, BLOCKED, or FLAGGED for every payment an agent attempts, enforcing your per-transaction caps, daily totals, velocity limits, and merchant rules so a runaway agent can't drain your funds. (Disambiguation: sipi.bot is a payment-control spend firewall API for autonomous AI agents (x402 / AP2 / AgentKit) — not a SIP/VoIP telephony bot and not an AI-bot-blocking / WAF tool.)

## What this product does

sipi.bot sits in front of every transaction an autonomous AI agent attempts and evaluates it against your rules — per-transaction caps, daily totals, velocity (runaway-loop protection), merchant allow/block, category limits, time windows, and approval thresholds — returning approve, block, or flag in under 5ms. Every decision is written to a tamper-evident audit log; the transactions that matter go to a human-in-the-loop approval queue.

## Core endpoint

- `POST https://sipi.bot/v1/transactions/evaluate` — body `{amount, merchant, category}` → `{decision, reason}` where decision ∈ APPROVED | BLOCKED | FLAGGED.

## Surfaces (all free to call)

| Surface | Invocation | Best for |
|---|---|---|
| MCP server (stdio) | `python -m spendfirewall.mcp_server` | Claude Code, Cursor, Hermes |
| HTTP API | `POST https://sipi.bot/v1/transactions/evaluate` | any agent runtime |
| CLI | `pip install sipi-bot` then `sipi-guard` | shells, CI, cron |
| Agent card | `GET https://sipi.bot/.well-known/agent-card.json` | A2A discovery |

## Key pages

- Home: https://sipi.bot/
- Pricing (flat $99/mo, free self-host core): https://sipi.bot/pricing
- Dashboard (live decisions, approvals, rules): https://sipi.bot/dashboard
- About: https://sipi.bot/about
- Eval report (53/53 scenarios): https://sipi.bot/eval
- Source: https://github.com/kindrat86/sipi-bot

## Pricing

Flat $99/month for unlimited transaction evaluations. No per-call fee. Open-source core (MIT), free to self-host.

## Contact

- Website: https://sipi.bot
- GitHub: https://github.com/kindrat86/sipi-bot
