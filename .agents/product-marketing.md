# Product Marketing Context

**Document version:** v1
**Last updated:** 2026-08-24

## Product Overview
**One-liner:** sipi.bot is a deterministic pre-spend firewall and implementation service for autonomous AI agents.
**What it does:** Agents call sipi.bot before a paid action. The policy engine returns APPROVED, BLOCKED, or FLAGGED based on caps, velocity, merchant, category, time, and approval rules. The paid pilot maps and implements those controls in one real workflow.
**Product category:** AI agent spend control / agent payment governance
**Product type:** Open-source software, hosted SaaS, and fixed-scope implementation service
**Business model:** MIT-licensed self-hosted core; Team at $99/month; Business at $499/month; paid implementation pilot with scope and fee agreed in writing before kickoff.

## Target Audience
**Target companies:** AI product teams, automation agencies, agent infrastructure teams, and businesses running autonomous workflows that can trigger paid APIs, cloud jobs, purchases, credits, or payment rails.
**Decision-makers:** Technical founders, CTOs, heads of engineering, platform leads, security leads, and FinOps owners.
**Primary use case:** Put an enforceable decision point before one agent workflow can spend money or trigger metered work.
**Jobs to be done:**
- Stop retry loops and parallel agents from compounding spend.
- Enforce company-specific merchant, category, amount, and time rules.
- Preserve an auditable explanation for every approval, block, and human review.

## Personas
| Persona | Cares about | Challenge | Value we promise |
|---------|-------------|-----------|------------------|
| Technical owner | Reliable integration | Prompts and alerts are not enforcement | A deterministic decision wired into the paid path |
| Security / FinOps | Policy and evidence | Provider controls are fragmented and reactive | One cross-provider policy and audit trail |
| Founder / buyer | Avoiding costly failures | No proof that controls work in the real workflow | Fixed-scope implementation with acceptance tests |

## Problems & Pain Points
**Core problem:** Autonomous agents can repeat or parallelize legitimate paid actions faster than a human can notice.
**Why alternatives fall short:** Rate limits cap request volume; provider budgets are fragmented; observability reports events after they happen; prompt instructions can be bypassed or misapplied.
**What it costs them:** Unplanned API or cloud spend, operational interruption, manual review, and weak auditability.
**Emotional tension:** The team wants autonomy without giving an agent an effectively unlimited company card.

## Competitive Landscape
**Direct:** Spend-control gateways and agent policy engines.
**Secondary:** LLM observability, cloud cost tools, provider budgets, and API gateways.
**Indirect:** Hardcoded checks, prompts, spreadsheets, and manual review.

## Differentiation
**Key differentiators:**
- Deterministic logic with no model in the decision path.
- Three explicit outcomes: approve, block, or flag.
- HTTP API, MCP tool, and CLI.
- MIT-licensed, auditable core.
- A paid implementation path focused on one working workflow rather than another feature backlog.
**How we do it differently:** The control runs before the paid action and the calling workflow must honor the result.
**Why that's better:** The buyer gets enforcement and evidence, not only an alert or chart.

## Objections
| Objection | Response |
|-----------|----------|
| We already have provider budgets | They remain useful, but they are provider-specific and often reactive. sipi.bot applies one policy before the action. |
| We can hardcode a limit | That works for one threshold; sipi.bot adds velocity, merchant, category, time, approvals, and an audit trail. |
| We do not want another platform | The core is MIT licensed and self-hostable. The pilot can implement it in the buyer's chosen environment. |
| Will it stop money by itself? | No. sipi.bot returns a decision. The calling agent or payment integration must honor it. |

**Anti-persona:** Teams seeking a free architecture review, unlimited integrations, custody of funds, or reimbursement for actions that bypass the decision.

## Switching Dynamics
**Push:** Surprise spend, retry incidents, fragmented controls, weak audit logs.
**Pull:** Deterministic enforcement, one policy surface, open source, and hands-on implementation.
**Habit:** Relying on provider alerts and prompts because they are already present.
**Anxiety:** Added latency, integration work, false blocks, and sharing sensitive data.

## Customer Language
**Words to use:** spend firewall, pre-spend control, paid action, retry loop, velocity limit, merchant allowlist, approval threshold, audit trail, deterministic.
**Words to avoid:** revolutionary, secret, guaranteed savings, zero risk, autonomous prevention without integration.
**Glossary:**
| Term | Meaning |
|------|---------|
| Paid action | An API call, cloud job, purchase, credit top-up, or payment that creates cost |
| Spend firewall | A policy decision point before the paid action |
| FLAGGED | Held for human review before proceeding |

## Brand Voice
**Tone:** Technical, direct, conservative, and evidence-first.
**Style:** Clear claims, explicit limitations, short sentences, no fabricated incidents or testimonials.
**Personality:** Practical, auditable, calm, and slightly skeptical.

## Proof Points
**Metrics:** 53/53 public sipi.bot eval scenarios passing.
**Customers:** No public customer proof claimed for the pilot.
**Value themes:**
| Theme | Proof |
|-------|-------|
| Deterministic enforcement | Public engine and eval report |
| Auditable | MIT-licensed source and queryable decision records |
| Deployable | HTTP, MCP, CLI, and framework recipes |

## Goals
**Business goal:** Win one paid implementation pilot before building another feature or separate funnel.
**Conversion action:** Submit a qualified pilot application at `/pilot`.
**Current metrics:** AgentShield had zero verified customers and is now consolidated into sipi.bot. Stripe remains the revenue source of truth.

## Changelog
- v1 (2026-08-24) - Consolidated AgentShield into sipi.bot and established one paid implementation-pilot motion.
