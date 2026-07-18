# sipi.bot — Distribution Playbook (get cited by AI search)

**Why this file exists (AEO logic):** for MCP/agent tools, the pages AI assistants cite are
*directories and awesome-lists*, not your own site. Branded web mentions were the single strongest
correlate of AI visibility in Ahrefs' 75,000-brand study (0.664). GitDealFlow is the only portfolio brand
AI can "see" because it did exactly this. This is the sipi.bot version. Work top-down — Tier 1 first.

> Detailed per-registry steps already exist in [`REGISTRY_CHECKLIST.md`](./REGISTRY_CHECKLIST.md) and the
> awesome-mcp entry in [`AWESOME_MCP_ENTRY.md`](./AWESOME_MCP_ENTRY.md). This file is the master list +
> the channels those two don't cover (agent-economy + general directories). Status legend: ✅ done ·
> ⬜ todo · 🔒 needs browser GitHub OAuth or a publish action (you do it, or approve me to).

## Copy-paste submission fields

| Field | Value |
|---|---|
| Name | `sipi-bot` / **sipi.bot Spend Firewall** |
| One-liner | The spend firewall for autonomous AI agents — approve, block, or flag every transaction before a dollar moves. |
| Category | Security · Finance · AI Agents |
| Repo | https://github.com/kindrat86/sipi-bot |
| Homepage | https://sipi.bot |
| PyPI | `sipi-bot` (`pip install sipi-bot`) |
| MCP run | `python -m spendfirewall.mcp_server` |
| License | MIT |
| Tags | ai-agents, agent-economy, spend-control, guardrails, agent-safety, mcp, x402, security, fintech |
| Proof | eval 53/53 → https://sipi.bot/eval · agent-card → https://sipi.bot/.well-known/agent-card.json |

**Longer blurb:** sipi.bot is a spend firewall an autonomous agent calls before it spends money. One call
returns APPROVED, BLOCKED, or FLAGGED (human approval) against per-transaction caps, daily totals,
velocity (runaway-loop protection), merchant allow/block, category limits, time windows, and approval
thresholds. MCP tool + HTTP API + CLI. Open-source core (MIT), free to self-host. 53/53 eval scenarios.

## Tier 1 — MCP registries (highest ROI; these get cited)

| # | Registry | URL | Auth | Status |
|---|---|---|---|---|
| 1 | **Glama.ai** (do first — generates the awesome-mcp badge) | https://glama.ai/mcp/servers/submit | 🔒 GitHub OAuth | ⬜ |
| 2 | **mcp.so** | https://mcp.so/submit | 🔒 form/OAuth | ⬜ |
| 3 | **Smithery.ai** (GitHub-import path, *not* hosted-URL — see REGISTRY_CHECKLIST gotcha; needs PyPI live) | https://smithery.ai/new | 🔒 GitHub | ⬜ (needs PyPI) |
| 4 | **PulseMCP** | https://www.pulsemcp.com/submit | 🔒 form | ⬜ |
| 5 | **Cursor Directory** (GitDealFlow is listed here — proven channel) | https://cursor.directory/mcp | 🔒 form/PR | ⬜ |
| 6 | **Official MCP registry** | https://github.com/modelcontextprotocol/registry | 🔒 PR | ⬜ |
| 7 | **mcp-get / mcpservers.org** | https://mcpservers.org | 🔒 PR/form | ⬜ |

Prereqs (from REGISTRY_CHECKLIST): GitHub repo ✅, GitHub release ✅, `smithery.yaml` ✅, **PyPI publish ⬜**
(Trusted Publishing wired via `.github/workflows/publish.yml`; one 2-min pypi.org browser step then
`git tag v0.1.0 && git push origin v0.1.0`). Glama + mcp.so don't need PyPI; Smithery does.

## Tier 2 — Awesome-list PRs (highest long-term ROI; permanent citable pages)

Each is a GitHub PR. Entry lines below are ready to paste.

1. **punkpeye/awesome-mcp-servers** (~90K★) — full entry in [`AWESOME_MCP_ENTRY.md`](./AWESOME_MCP_ENTRY.md).
   Section: Finance & Fintech (or Security). Depends on Glama badge (Tier 1 #1).
2. **e2b-dev/awesome-ai-agents** — GitDealFlow used this exact channel (issue #890). Section: Tools/Infra.
   ```
   - [sipi.bot](https://github.com/kindrat86/sipi-bot) - Spend firewall for autonomous AI agents: one call returns APPROVED/BLOCKED/FLAGGED against per-transaction, daily, velocity, and merchant rules before money moves. MCP + HTTP + CLI, MIT.
   ```
3. **Awesome AI agent-economy / x402 lists** (e.g. `coinbase/x402` ecosystem, `awesome-agent-payments`).
   sipi.bot is the *guardrail* layer for x402/AP2 payments — a natural ecosystem fit.
   ```
   - [sipi.bot](https://sipi.bot) - Pre-spend guardrail for agent payments: evaluate any x402/AP2/card transaction against caps, velocity, and merchant rules; returns approve/block/flag. Open-source (MIT).
   ```
4. **awesome-agents / awesome-ai-tools** (various) — reuse the entry above.

**PR title convention** (agent fast-track, matches awesome-mcp CONTRIBUTING): `Add sipi.bot spend firewall 🤖🤖🤖`

## Tier 3 — Launches & general directories

| Channel | URL | Note | Status |
|---|---|---|---|
| **Show HN** | https://news.ycombinator.com/submit | Draft ready in [`SHOW_HN.md`](./SHOW_HN.md) | ⬜ 🔒 |
| **Product Hunt** | https://www.producthunt.com/posts/new | Schedule a launch; use the blurb above | ⬜ 🔒 |
| **Indie Hackers** | https://www.indiehackers.com/ | Product + a build post (GitDealFlow did this) | ⬜ 🔒 |
| **There's An AI For That** | https://theresanaiforthat.com/submit | AI-tool directory, heavily crawled | ⬜ 🔒 |
| **Futurepedia** | https://www.futurepedia.io/submit-tool | AI-tool directory | ⬜ 🔒 |
| **AlternativeTo** | https://alternativeto.net | List as an option in "agent spend control / guardrails" | ⬜ 🔒 |
| **Crunchbase** | https://www.crunchbase.com | Company profile (GitDealFlow has one — strong AI-citation signal) | ⬜ 🔒 |

## What I can vs. can't do
- ✅ Done for you: all on-site agent-discovery files (agents.txt, llms-full.txt, knowledge-graph.json,
  qa.jsonl) so every directory/agent that fetches sipi.bot gets clean, attributable, citable content.
- 🔒 The submissions themselves need browser GitHub OAuth or are publish actions — you run them, **or**
  approve me to open the awesome-list **PRs** (Tier 2) via `gh`, which is the highest-ROI channel and the
  one I can prepare end-to-end.

**Do first:** PyPI publish → Glama → mcp.so → awesome-mcp PR → awesome-ai-agents PR. That's the same order
that got GitDealFlow cited.
