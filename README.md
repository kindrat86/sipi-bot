# sipi.bot — the spend firewall for autonomous AI agents

> You gave an autonomous agent your credit card and no spending limit.
> **sipi.bot** is the firewall that approves, blocks, or flags every
> transaction against *your* rules — before a single dollar moves.

One capability, three surfaces:

- **MCP tool** — Claude Code / Cursor / Hermes call `evaluate_spend` natively.
- **HTTP API** — any agent `POST /v1/transactions/evaluate`.
- **CLI** — verify without an agent.

## 10-second test

```bash
pip install sipi-bot
sipi-bot eval --amount 6200 --merchant unknown-gpu.ru --category compute
# -> {"decision": "BLOCKED", "reason": "Transaction $6,200.00 exceeds per-transaction limit $500.00."}

sipi-bot serve --port 8080   # landing + dashboard + API
```

Or from source:

```bash
python3.11 -m spendfirewall.cli eval --amount 6200 --merchant unknown-gpu.ru --category compute
```

Then open http://localhost:8080 (landing), http://localhost:8080/dashboard (control room), http://localhost:8080/pricing (Team $99 / Business $499).

**Hosted:** [sipi.bot](https://sipi.bot) · [dashboard](https://sipi.bot/dashboard) · [get an API key →](https://sipi.bot/pricing)

## The core call an agent makes before spending

```bash
curl -X POST https://sipi.bot/v1/transactions/evaluate \
  -H "Authorization: Bearer sk_live_..." \
  -d '{"amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute"}'
```

Returns one of: `APPROVED` (go), `BLOCKED` (do not spend), `FLAGGED` (human must approve).

## Rule types

`per_transaction`, `daily_total`, `velocity` (runaway protection), `merchant_block`,
`merchant_allow` (allowlist), `category_limit`, `time_window`, `approval_threshold`.

First `BLOCKED` wins. `FLAGGED` is non-blocking (queued for human approval).

## Eval gym (the guarantee + the sales asset)

```bash
python3.11 -m spendfirewall.eval.run_eval   # 53 scenarios -> eval_report.json + .md
```

53/53 passing. Served live at `/eval`. This is what backs the guarantee:
*if the firewall green-lights a spend that breaks your rule, that month is free.*

## MCP config

```json
{ "mcpServers": { "sipi-bot": { "command": "python", "args": ["-m", "spendfirewall.mcp_server"] } } }
```

## Deploy (Fly.io)

```bash
flyctl launch --no-deploy --copy-config --name sipi-bot-firewall
flyctl volumes create sf_data --size 1 --region iad --yes
flyctl deploy
flyctl certs add sipi.bot
```

Stdlib-only (http.server, sqlite3). No framework, trivial deploy. `pip install mcp` only for the MCP surface.
