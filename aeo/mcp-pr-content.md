# awesome-mcp-servers PR content

> **Target repo:** https://github.com/punkpeye/awesome-mcp-servers
> **PR from:** kindrat86 (your GitHub identity — not the Reddit/YouTube identity)
> **Install command:** `pip install sipi-bot && python -m spendfirewall.mcp_server`

## PR title
```
Add sipi.bot — Spend Firewall for AI Agents (MIT, 53/53 eval)
```

## Entry to add

Insert in the list alphabetically under "S" or as a standalone entry:

```markdown
### sipi.bot - Spend Firewall for AI Agents

A spend firewall that approves, blocks, or flags every transaction an autonomous AI agent proposes, against configurable spend rules. One MCP tool call before any payment returns a decision in under 5ms. Includes a public 53-scenario eval gym.

- **Install:** `pip install sipi-bot && python -m spendfirewall.mcp_server`
- **Eval:** 53/53 scenarios passing ([report](https://sipi.bot/eval-report/))
- **License:** MIT
- **GitHub:** [github.com/kindrat86/sipi-bot](https://github.com/kindrat86/sipi-bot)
- **Website:** [sipi.bot](https://sipi.bot)
```

## PR body

```
Adds sipi.bot — a spend firewall for autonomous AI agents with a native MCP server.

- MIT-licensed, open source
- 53/53 passing eval scenarios (public gym)
- Ships as stdio MCP server + HTTP API + CLI
- Native MCP tool that Claude Code, Cursor, and Hermes load directly

One MCP tool call before your agent spends → APPROVED, BLOCKED, or FLAGGED in <5ms.

Let me know if the category placement needs adjusting.
```

## Alternative: also add to awesome-mcp (LangChain's MCP directory)

The repo at https://github.com/langchain-ai/awesome-mcp (pinned by LangChain, used by their ecosystem) is also worth a PR. Same entry text.
