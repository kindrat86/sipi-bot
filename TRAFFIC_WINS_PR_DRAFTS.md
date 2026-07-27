# PR & distribution drafts — win #6

These are **drafts for you to send**, not auto-published. Each is tuned to its channel's norms. Pick what fits your voice; the hooks (the 53/53 eval, the $12,400-while-you-slept framing, the open-source MIT core) are the strongest cards.

---

## A. Hacker News — "Show HN" post

**Title (≤80 chars):**
```
Show HN: sipi.bot – a spend firewall so an AI agent can't drain your card
```

**Body:**

```
Hi HN. I built sipi.bot because I almost shipped an agent that could have
spent $12,400 overnight on a bad retry loop, and the only thing standing
between me and that was "hope."

It's a single HTTP call an autonomous agent makes *before* it spends.
You send {amount, merchant, category}, it returns APPROVED, BLOCKED, or
FLAGGED against your rules — per-transaction caps, daily totals, velocity
limits (the runaway-loop killer), merchant allow/block, category limits,
time windows, and human-approval thresholds.

Three surfaces, same engine:
- MCP tool (Claude Code / Cursor / Hermes call it natively)
- HTTP API (any agent runtime: POST /v1/transactions/evaluate)
- CLI (pip install sipi-bot; sipi-guard)

The interesting design decision: it's deterministic, no model call. Every
decision is a priority-ordered rules check, so you can reason about why
a transaction was blocked and replay it. The eval gym is 53 hand-labeled
scenarios across 9 categories, all passing — served live at /eval, and
the guarantee is concrete: if the firewall green-lights a spend that
breaks your rule, that month is free.

It's also open-source (MIT) and free to self-host — the hosted version
($99/mo flat, unlimited evaluations) is just managed infra + a dashboard.

I'd genuinely like to hear where this is wrong. The threat model I'm most
unsure about: prompt-injected agents that misreport the amount to the
firewall. The current answer is "the amount must come from the tool call's
structured params, not agent free text" — but I'm curious what HN thinks
about agents that can forge their own tool inputs.

Try it free, no signup: https://sipi.bot/playground/
Source: https://github.com/kindrat86/sipi-bot
```

**When to post:** Tuesday–Thursday, 8–10am ET. Don't post Friday afternoon or weekend.

**First-comment seed (post immediately after):** a one-paragraph "what I learned building it" or the most interesting eval scenario — HN rewards a substantive first comment from the submitter.

---

## B. Newsletter pitches (3)

These are short, hook-first pitches. Send to the editor/contact address; don't mass-blast. Personalize line 1.

### B1. TLDR AI (admin@tlrdai.com) — broad AI audience

**Subject:** A pre-spend firewall for AI agents (open-source, 53/53 eval)

```
Hi [editor],

For TLDR AI readers building agent products: the scariest part of shipping
an autonomous agent isn't the model — it's giving it a payment method with
no real limit. Budget caps fire after the money's gone; observability tools
tell you about the loss in a dashboard.

sipi.bot is the layer that sits in front: one HTTP call before the agent
spends, returning APPROVED/BLOCKED/FLAGGED against per-tx caps, velocity
limits (kills runaway loops), and merchant allowlists. Deterministic — no
model call — with a 53-scenario eval gym live at /eval. Open-source (MIT),
free to self-host; hosted at $99/mo flat.

Worth a line in TLDR AI? Happy to write a 150-word "how it works" sidebar
or do a quick Q&A. The $12,400-while-you-slept framing tends to land.

— Maryan
https://sipi.bot
```

### B2. Latent Space (swyx@latent.space) — builder/infra audience

**Subject:** Spend firewall for the agent economy (deterministic, eval-gym'd)

```
Hi [editor],

Given Latent Space's coverage of agent infra and the x402 / AgentKit payment
rails — here's the missing layer: a deterministic pre-spend firewall.

sipi.bot evaluates every transaction an agent attempts *before* it fires,
against priority-ordered rules (per-tx, daily, velocity, merchant, category,
time-window, approval-threshold). No model call — fully replayable. Exposed
as an MCP tool, HTTP API, and CLI so it drops into any agent runtime.

The part your readers will care about: the engine is eval-gym'd against 53
hand-labeled scenarios (9 categories), all passing and served live. And
the canonical threat-model question — "what if the agent misreports the
amount?" — is handled by requiring structured tool params, not free text.

MIT core, self-hostable; hosted at $99/mo. Would love to do a deep-dive on
agent payment governance for Latent Space, or just share the eval report.

— Maryan
https://sipi.bot/eval-report/
```

### B3. Import AI / The Sequence / Ben's Bites — pick based on tone

**Subject:** The "hope is not a spending policy" tool for AI agents

```
Hi [editor],

Quick one for [newsletter] readers shipping agents with payment access.

The status quo for agent spend is a provider budget cap (fires after the
fact, only on that provider) or an observability dashboard (shows you the
loss nicely). sipi.bot is the pre-spend layer: one call before money moves,
returns APPROVED/BLOCKED/FLAGGED, with velocity limits that stop runaway
retry loops before they drain a card.

53/53 eval scenarios passing (live at /eval), open-source MIT core, $99/mo
hosted. The "your AI agent just spent $12,400 while you slept" framing is
the one that gets builders to click.

A short mention would mean a lot to a solo founder. Happy to do a quick
interview or write a guest piece on "the six rules a spend firewall
enforces."

— Maryan
https://sipi.bot
```

---

## C. Reddit — low-key, value-first (do NOT spam)

**Target subs:** r/LocalLLaMA, r/LangChain, r/OpenAI, r/MachineLearning, r/SaaS

**Approach:** Don't post a link-drop. Find threads where someone asks "how do I stop my agent overspending" or "agent ran up a huge bill" and reply with the *concept* (spend firewall, velocity limits) and mention you built an open-source one as a footnote. One genuine comment per thread, no copy-paste.

**Template reply (adapt to the thread):**

```
The thing that actually stops runaway agent spend isn't a budget cap — those
fire after the money's gone. It's a velocity limit: cap transactions per
time window at the workspace/card level (not per-agent, since serverless
spins up fresh identities). Combined with a per-tx cap and a default-BLOCK
on unknown merchants, a stuck retry loop physically can't drain the card.

I open-sourced a small firewall that does exactly this — one call before
the agent spends, returns approve/block/flag. MIT, self-hostable:
https://github.com/kindrat86/sipi-bot
```

---

## D. The badge as a distribution loop

Every "Protected by sipi.bot" badge embed is a free, dofollow backlink from a relevant site (devtools, agent products). This is the most scalable referral mechanism you already have.

1. Embed it in your own products first (sets the norm).
2. Offer it to early users / OSS friends who ship agents.
3. Each embed → a referring domain → DA rises → organic rises.

README section + embed guide already shipped at `/badge` in this deploy.
