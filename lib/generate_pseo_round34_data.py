"""Round 34 pSEO data — sipi.bot (2026-08-08).

Fifteenth round. LINK-INTEGRITY round: created from the internal-link audit
(/tmp/audit_links.py) — every page below was referenced by existing pages
but returned 404. Plus the OpenClaw integration (2026's breakout agent,
zero coverage).

  cost-of +1: vllm-cost            (referenced by /cost-of/ollama-cost)
  how-to +3: how-to-reduce-ai-api-costs (8 referrers!)
             how-to-stop-runaway-agents (8 referrers!)
             how-to-track-ai-spend     (1 referrer)
  redflags +1: red-flags-in-api-keys   (1 referrer)
  integrations +1: openclaw

Link fixes (separate):
  - blog/what-a-spend-firewall-wont-do: /templates/firewall-rule-tuning-checklist
    -> /checklists/firewall-rule-tuning-checklist/
  - alternatives-to/index.html: 4 x /public/alternatives/<slug> -> /alternatives/<slug>/

All existing dirs — no plumbing. Content honest.
"""

COST_OF = [
    dict(
        slug="vllm-cost",
        title="vLLM Cost — Local Inference Pricing and Spend Control",
        desc="vLLM cost: open-source serving is hardware, power, and time — not tokens. The honest cost of self-served inference.",
        h1="How Much Does vLLM Cost?",
        lead="vLLM is free software — the cost is the GPU, the power, and the engineering. Self-served inference trades token bills for a different ledger.",
        sections=[
            ("How vLLM is priced",
             ["No per-token fee — you pay for hardware, power, and ops.",
              "Serving cost per million tokens depends on model size and your rig.",
              "Time is a real cost: slower serving means longer agent loops."]),
            ("The honest comparison",
             ["vLLM wins at high steady volume with a tuned rig.",
              "Hosted wins for spiky, varied, or multi-provider workloads.",
              "Model the TCO for your shape — don't trust averages."]),
            ("Why agents still need a budget",
             ["Self-served inference doesn't govern the tools and APIs beyond it.",
              "The firewall applies to any stack."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Hardware", "Model size vs rig"],
                ["Power", "Utilization"],
                ["Ops", "Tuning time"],
                ["Tools/APIs", "Firewall rules"],
            ],
        ),
        faqs=[
            ("Is vLLM cheaper than hosted APIs?",
             "At high steady utilization, often — model your TCO."),
            ("Does sipi.bot work with a vLLM stack?",
             "Yes — the firewall governs tool and API spend regardless of where inference runs."),
        ],
        related=[("Ollama cost", "/cost-of/ollama-cost"), ("Local vs hosted", "/benchmarks/local-llm-vs-hosted-api-cost"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs")],
    ),
]

HOW_TO = [
    dict(
        slug="how-to-reduce-ai-api-costs",
        title="How to Reduce AI API Costs",
        desc="Reduce AI API costs: the levers that actually move the bill — model selection, context, caching, volume, and retries.",
        h1="How to Reduce AI API Costs",
        lead="Cutting the AI API bill is rate shopping plus behavior change. The rate is one lever; volume, context, and retries are the bigger ones.",
        sections=[
            ("The rate levers",
             ["Model selection: match the model to the task — small models for simple work.",
              "Caching: cache stable prefixes and repeated outputs.",
              "Batching: batch where latency allows."]),
            ("The volume levers",
             ["Per-agent ceilings bound the total.",
              "Velocity limits kill retry loops — the most common multiplier.",
              "Merchant allowlists stop unvetted vendors."]),
            ("The context lever",
             ["Trim what you send: smaller contexts, targeted retrieval."]),
        ],
        table=dict(
            headers=["Lever", "Moves"],
            rows=[
                ["Model selection", "Rate"],
                ["Caching", "Rate"],
                ["Ceilings", "Volume"],
                ["Velocity limits", "Retries"],
                ["Context trimming", "Size"],
            ],
        ),
        faqs=[
            ("What's the fastest win?",
             "A velocity limit and a per-agent ceiling — both in one session."),
            ("Is cheaper the same as better?",
             "No — match the model to the task; the cheapest model that does the job is the right one."),
        ],
        related=[("Why AI bills grow", "/blog/why-your-ai-bill-keeps-growing"), ("GPT vs Claude cost", "/cost-of/gpt-api-cost"), ("How to track AI agent costs", "/answers/how-to-track-ai-agent-costs/")],
    ),
    dict(
        slug="how-to-stop-runaway-agents",
        title="How to Stop Runaway Agents",
        desc="Stop a runaway agent: the immediate kill switch, the containment rules, and the post-mortem that prevents the next one.",
        h1="How to Stop Runaway Agents",
        lead="A runaway agent is spend compounding at machine speed. Here's how to stop the bleeding now, contain it, and prevent the next one.",
        sections=[
            ("Step 1 — Stop the bleeding",
             ["Disable the agent's spending instantly (per-agent kill switch).",
              "Block the merchant or category the run is spending on.",
              "Pause the workflow, not just the agent."]),
            ("Step 2 — Contain",
             ["Set a hard ceiling on the agent and the fleet.",
              "Add a velocity limit if the pattern is a loop."]),
            ("Step 3 — Understand",
             ["Read the audit log: what fired, what didn't, which rule was missing."]),
            ("Step 4 — Prevent",
             ["Add the missing rule, review the fleet, and tune the thresholds."]),
        ],
        faqs=[
            ("How fast can I stop an agent?",
             "Instantly — disable spending, the next transaction is blocked."),
            ("What if I don't have a firewall?",
             "You're finding out now why the money path needs a gate."),
        ],
        related=[("Runaway loop anatomy", "/blog/runaway-loops-anatomy"), ("Retry loop", "/glossary/retry-loop"), ("How to handle a flagged transaction", "/how-to/how-to-handle-a-flagged-transaction")],
    ),
    dict(
        slug="how-to-track-ai-spend",
        title="How to Track AI Spend",
        desc="Track AI spend across providers and agents: per-agent attribution, per-merchant detail, and the weekly review cadence.",
        h1="How to Track AI Spend",
        lead="Tracking AI spend means attribution: which agent, which merchant, which category — and a cadence that turns the log into decisions.",
        sections=[
            ("The dimensions",
             ["Per-agent: every decision logged with the agent that made it.",
              "Per-merchant: who got paid, how much.",
              "Per-category: inference, data, tools, payments."]),
            ("The source of truth",
             ["Provider dashboards show their slice; the audit log shows the whole — including blocked attempts."]),
            ("The cadence",
             ["Weekly for spend, monthly for rules — one change at a time."]),
        ],
        faqs=[
            ("What's the ground truth?",
             "The audit log — every decision with the rule that fired."),
            ("How do I split provider vs firewall?",
             "Providers bill; the log attributes. Use both."),
        ],
        related=[("How to track AI agent costs", "/answers/how-to-track-ai-agent-costs/"), ("How to monitor AI costs", "/how-to/how-to-monitor-ai-costs"), ("Agent cost report template", "/templates/agent-cost-report-template")],
    ),
]

REDFLAGS = [
    dict(
        slug="red-flags-in-api-keys",
        title="Red Flags in API Key Management",
        desc="The warning signs that your API keys are a risk: keys in repos, over-scoped keys, no rotation, and no spend limits.",
        h1="Red Flags in API Key Management",
        lead="API keys are credentials — and leaked keys are spend before they're headlines. Here are the red flags that mean trouble.",
        sections=[
            ("The red flags",
             ["1. Keys in repos, logs, or prompts — the classic leak vector.",
              "2. Over-scoped keys: one key with access to everything.",
              "3. No rotation: keys that never change.",
              "4. No spend limits: a leaked key can spend freely.",
              "5. No audit: you can't see what a key did."]),
            ("The fix",
             ["Scoped keys per agent, rotation on a schedule, and spend limits per key."]),
        ],
        faqs=[
            ("What's the worst-case with a leaked key?",
             "A valid key can drive spend — the firewall's caps and velocity limits bound the damage."),
            ("How do I detect leaks?",
             "Secret scanning plus spend limits on every key — both."),
        ],
        related=[("API key compromise scenario", "/scenarios/api-key-compromise-scenario"), ("Secret scanning", "/for/security-engineers"), ("How to stop runaway agents", "/how-to/how-to-stop-runaway-agents")],
    ),
]

INTEGRATIONS = [
    dict(
        slug="openclaw",
        title="OpenClaw Agent Spend Control — sipi.bot Integration",
        desc="OpenClaw is the breakout autonomous agent of 2026. sipi.bot gates what its runs spend: tools, compute, and payments.",
        h1="Spend Control for OpenClaw",
        lead="OpenClaw is the open-source agent everyone runs in 2026 — autonomous, tool-hungry, and spend-capable by default. The guard makes the budget real.",
        sections=[
            ("Why OpenClaw runs overspend",
             ["Autonomous runs call tools hundreds of times.",
              "Every tool call can hit a paid API or trigger a payment.",
              "No dollar-level budget inside the agent."]),
            ("How it works",
             ["Call the guard before any spend-capable step: amount, merchant, category → APPROVED, BLOCKED, or FLAGGED."]),
            ("Rules that fit",
             ["Per-run ceiling.",
              "Velocity limit on retry loops.",
              "Merchant allowlist for paid tools."]),
        ],
        code=dict(
            title="Guard call",
            lang="typescript",
            body='const res = await fetch("https://sipi.bot/v1/transactions/evaluate", {\n  method: "POST", headers: { "Content-Type": "application/json" },\n  body: JSON.stringify({ amount: 30, merchant: "api.vendor.com", category: "api" }),\n});\nconst { decision } = await res.json();',
            caption="Autonomy with a budget.",
        ),
        faqs=[
            ("Does this stop OpenClaw's autonomy?",
             "No — it gates spend steps; the run continues within budget."),
            ("Is OpenClaw officially supported?",
             "sipi.bot is HTTP/MCP — any tool-calling agent works."),
        ],
        related=[("Manus", "/integrations/manus"), ("AutoGPT", "/integrations/autogpt"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
]

# --- hub metadata -----------------------------------------------------------
