# awesome-mcp-servers PR entry

Target repo: https://github.com/punkpeye/awesome-mcp-servers (~90K★)

Section: **Finance & Fintech** (or **Security**) — alphabetical within.

PR title (agent fast-track per CONTRIBUTING.md):
```
Add sipi.bot spend firewall 🤖🤖🤖
```

Entry line (match neighbors' badge + emoji style):
```
- [kindrat86/sipi-bot](https://github.com/kindrat86/sipi-bot) 🐍 🏠 ☁️ - Spend firewall for autonomous AI agents: approve, block, or flag every transaction against your rules (per-tx, daily, velocity, merchant, time) before a dollar moves.
```

Emoji legend used: 🐍 Python · 🏠 self-host (local) · ☁️ cloud (hosted at sipi.bot)

PR body:
> ## What
> sipi.bot is a spend firewall for autonomous agents. One MCP tool call
> (`evaluate_spend`) before the agent spends → APPROVED / BLOCKED / FLAGGED.
>
> ## Why it belongs here
> Every agent that can spend money (compute, API credits, ads) needs a guardrail
> against runaway loops. This is the missing safety layer for the agent economy.
>
> ## Proof it works
> - Live: https://sipi.bot · eval report (53/53): https://sipi.bot/eval
> - `pip install sipi-bot` · MCP: `python -m spendfirewall.mcp_server`
> - Open-source core, stdlib-only, MIT.
