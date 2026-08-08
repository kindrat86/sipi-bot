"""Round 26 pSEO data — sipi.bot (2026-08-08).

Seventh round. Modest, high-signal:
- answers/ +3 NEW pages AND rewrite of the 2 existing answers pages that
  contained fabricated market statistics (startups spend $500-5k/mo etc. —
  invented numbers, violates the honesty rule). All answers pages are
  public/-served → slash canonical, lib chrome, honest content.
- tutorials/ +2, scenarios/ +1, redflags/ +1, guides/ +1.
- blog +2 via lib/generate_content.py.

Content rules: honest, no fabricated stats. Where a number isn't verifiable,
the page says so and links to the real incident database / eval data.
"""

ANSWERS = [
    dict(
        slug="how-to-prevent-ai-agent-overspending",
        title="How to Prevent AI Agent Overspending",
        desc="AI agent overspending is a control problem, not a model problem. The rules that stop it: caps, velocity limits, allowlists, and approvals.",
        h1="How to Prevent AI Agent Overspending",
        lead="Overspending isn't the model's fault — it's the absence of a gate between the agent and the money. The prevention is a small set of rules, deterministically enforced.",
        sections=[
            ("Step 1 — Cap every transaction",
             ["A per-transaction cap blocks any single purchase above a ceiling. This alone stops the largest runaway shapes."]),
            ("Step 2 — Kill the loops",
             ["A velocity limit caps transactions per window. The documented runaway pattern — a retry loop — dies at the limit."]),
            ("Step 3 — Control the vendors",
             ["A merchant allowlist makes unknown vendors BLOCKED by default. Procurement regains control of who agents pay."]),
            ("Step 4 — Add a human gate",
             ["An approval threshold FLAGS material purchases for review — agents stay fast, big spends wait for a human."]),
            ("Step 5 — Watch the log",
             ["The audit log records every decision with the rule that fired. Review it weekly; tune rules with data."]),
        ],
        table=dict(
            headers=["Rule", "Stops"],
            rows=[
                ["Per-transaction cap", "Single oversized purchases"],
                ["Velocity limit", "Retry loops"],
                ["Merchant allowlist", "Unknown vendors"],
                ["Approval threshold", "Unreviewed material spend"],
            ],
        ),
        faqs=[
            ("Which rule is most important?",
             "The velocity limit — it stops the most common runaway shape (retry loops) in seconds."),
            ("Do I need all four?",
             "Three cover most risk: a cap, an allowlist, and a velocity limit. Approval adds the human gate."),
        ],
        related=[("How to stop runaway agents", "/how-to/how-to-stop-runaway-agents"), ("Velocity limit", "/glossary/velocity-limit"), ("Runaway loops", "/blog/runaway-loops-anatomy")],
    ),
    dict(
        slug="how-to-budget-for-ai-agents",
        title="How to Budget for AI Agents",
        desc="Budgeting for AI agents: estimate legitimate spend, set ceilings, and enforce them. A practical framework with real numbers to start from.",
        h1="How to Budget for AI Agents",
        lead="The honest way to budget an agent: estimate what the task legitimately costs, add headroom, and enforce the number. Here's the framework.",
        sections=[
            ("Estimate the legitimate cost",
             ["Work backwards from the task: tokens per run × runs per day, tool calls per task, data vendors in the path.",
              "The incident database and eval data give reference points for what agents actually consume."]),
            ("Set the ceilings",
             ["Daily ceiling ≈ legitimate daily spend × 1.5.",
              "Per-transaction cap at the largest 'no review needed' purchase.",
              "Approval threshold above that."]),
            ("Enforce and tune",
             ["The firewall enforces the numbers; the audit log shows the real spend. Tune monthly with data — one rule change at a time."]),
        ],
        table=dict(
            headers=["Budget element", "How to set it"],
            rows=[
                ["Daily ceiling", "Legit daily spend × 1.5"],
                ["Per-transaction cap", "Largest no-review purchase"],
                ["Approval threshold", "Above the cap, wait for human"],
                ["Merchant allowlist", "Approved vendors only"],
            ],
        ),
        faqs=[
            ("What if I don't know legitimate spend yet?",
             "Start conservative, watch the audit log for a week, and tune. The log is the ground truth."),
            ("Should every agent have the same budget?",
             "No — per-agent rules let each use case run its own number."),
        ],
        related=[("Agent budget template", "/templates/agent-budget-template"), ("Budget sizing calculator", "/calculators/budget-sizing-calculator"), ("How to set AI agent budget", "/faq/how-to-set-ai-agent-budget")],
    ),
    dict(
        slug="what-is-agentic-commerce",
        title="What Is Agentic Commerce?",
        desc="Agentic commerce: AI agents buying compute, data, and services autonomously on machine rails. The definition, the rails, and the control layer.",
        h1="What Is Agentic Commerce?",
        lead="Agentic commerce is the emerging market where autonomous agents — not humans — purchase goods and services on machine payment rails.",
        sections=[
            ("How it works",
             ["Agents discover payable resources and settle via protocols: x402 (HTTP-based), Google AP2, Coinbase AgentKit.",
              "Purchases are small, frequent, and autonomous — no human in the loop."]),
            ("What's real today",
             ["The rails are live and products ship on them. Compute, data, and API access are the first categories agents buy."]),
            ("The missing layer",
             ["Rails move money; they don't screen transactions. A pre-spend firewall is the control layer that makes the economy safe to scale."]),
        ],
        faqs=[
            ("Is agentic commerce speculative?",
             "The rails are live; what's immature is the control layer. That's the gap."),
            ("What should I do about it?",
             "If your agents can spend, put a decision layer in front of the rail before settlement."),
        ],
        related=[("Agentic commerce use case", "/use-cases/agentic-commerce"), ("Agentic payment", "/glossary/agentic-payment"), ("The agent economy", "/learn/the-agent-economy-explained")],
    ),
    # --- rewritten (honest) versions of the two fabricated-stat pages --------
    dict(
        slug="ai-spending-benchmarks-2026",
        title="AI Agent Spending Benchmarks 2026 — What the Data Shows",
        desc="What verifiable data says about AI agent spend in 2026: the incident database, documented runaways, and the shapes that repeat. No invented market numbers.",
        h1="AI Agent Spending Benchmarks 2026",
        lead="Most 'AI spending benchmarks' you'll find are invented ranges. Here's what's actually verifiable: documented incidents, eval data, and the patterns that repeat.",
        sections=[
            ("What the incident database shows",
             ["34 sourced incidents of agents that lost money or acted beyond intent, spanning 2016–2026.",
              "Documented runaways range from hundreds of dollars (small overages) to millions (the largest trading-agent losses).",
              "The $12,400 overnight retry loop is a documented founding case: 40 retries of one purchase at 2 AM."]),
            ("What the eval gym shows",
             ["53/53 scenarios pass — the six rule types tested against the documented failure shapes.",
              "Eval results are published machine-readably at /eval and /eval-report/."]),
            ("What we won't do",
             ["We won't publish 'startups spend $X/month' ranges — those numbers aren't verifiable, and fake precision helps nobody.",
              "If you want real numbers for your stack: measure with the audit log for a week. That's your benchmark."]),
        ],
        table=dict(
            headers=["Source", "What it verifies"],
            rows=[
                ["Incident database", "Documented runaway costs & patterns"],
                ["Eval gym", "Rule effectiveness (53/53)"],
                ["Your audit log", "Your actual spend"],
            ],
        ),
        faqs=[
            ("Why no industry averages?",
             "Because they're fabricated in most articles. Real spend varies by stack, workload, and controls — measure yours."),
            ("Where can I see the incidents?",
             "Browse the incident database — sourced, CC BY 4.0, JSON/CSV/JSONL."),
        ],
        related=[("Incident database", "/incidents/"), ("Runaway cost average", "/benchmarks/agent-runaway-cost-average"), ("Eval report", "/eval-report/")],
    ),
    dict(
        slug="how-to-control-ai-api-costs",
        title="How to Control AI API Costs",
        desc="Control AI API costs with levers that work: model selection, caching, context trimming, and enforcement. Honest, actionable.",
        h1="How to Control AI API Costs",
        lead="API cost = rate × volume × behavior. Control all three and the bill becomes predictable. Here are the levers, in order of impact.",
        sections=[
            ("Lever 1 — Right-size the model",
             ["Frontier models cost multiples of compact ones for the same task. Route hard tasks to frontier, everything else to compact."]),
            ("Lever 2 — Cache stable prefixes",
             ["Providers discount repeated input tokens. Stable system prompts and tool definitions hit cache discounts on every turn."]),
            ("Lever 3 — Trim context",
             ["Long-context calls are the most expensive shape. Summarize history, cap tool outputs, drop dead weight."]),
            ("Lever 4 — Stop the loops",
             ["A velocity limit kills retry loops — the single biggest multiplier on API spend."]),
            ("Lever 5 — Enforce the budget",
             ["Per-agent ceilings make the budget a decision, not a hope. The firewall enforces; the audit log measures."]),
        ],
        table=dict(
            headers=["Lever", "Controls"],
            rows=[
                ["Model selection", "Rate per token"],
                ["Caching", "Repeated input cost"],
                ["Context trimming", "Tokens per call"],
                ["Velocity limits", "Retry multiplier"],
                ["Ceilings", "Total budget"],
            ],
        ),
        faqs=[
            ("What's the biggest lever?",
             "Model selection changes per-token economics; velocity limits stop the volume multiplier. Both beat rate shopping."),
            ("Is there a free way to start?",
             "Yes — model right-sizing and caching are free. The firewall's MIT core self-hosts free."),
        ],
        related=[("How to reduce AI API costs", "/how-to/reduce-ai-api-costs"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026"), ("Token cache savings", "/benchmarks/token-cache-hit-savings")],
    ),
]

TUTORIALS = [
    dict(
        slug="integrate-with-vercel-ai-sdk",
        title="How to Integrate sipi.bot with the Vercel AI SDK",
        desc="Step-by-step: add sipi.bot's spend guard to a Vercel AI SDK app. One API call before the purchase, three rules to start.",
        h1="Integrate sipi.bot with the Vercel AI SDK",
        lead="The AI SDK makes streaming AI features easy — and easy features get agents that spend. The guard slots into the same flow.",
        sections=[
            ("Step 1 — Add the guard call",
             ["In the tool or action that spends, call the evaluate endpoint before the purchase."]),
            ("Step 2 — Branch on the decision",
             ["APPROVED → proceed. BLOCKED → return the reason to the model. FLAGGED → route to an approval step."]),
            ("Step 3 — Start with three rules",
             ["A per-transaction cap, a merchant allowlist, and a velocity limit."]),
        ],
        code=dict(
            title="Guard call",
            lang="typescript",
            body='const res = await fetch("https://sipi.bot/v1/transactions/evaluate", {\n  method: "POST",\n  headers: { "Content-Type": "application/json", "Authorization": `Bearer ${key}` },\n  body: JSON.stringify({ amount: 120, merchant: "api.vendor.com", category: "api" }),\n});\nconst { decision } = await res.json(); // APPROVED | BLOCKED | FLAGGED',
            caption="Deterministic, ~5 ms, no model call.",
        ),
        faqs=[
            ("Does this work in edge runtimes?",
             "Yes — it's a plain fetch to an HTTPS endpoint."),
            ("Is there a wrapper?",
             "A thin client wrapper exists for the AI SDK; the fetch above is the whole integration."),
        ],
        related=[("Vercel AI SDK", "/integrations/vercel-ai-sdk"), ("sipi.bot vs Vercel AI Gateway", "/vs/vercel-ai-gateway"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
    dict(
        slug="set-up-daily-spend-ceiling",
        title="How to Set Up a Daily Spend Ceiling",
        desc="Step-by-step: set a daily spend ceiling for an agent — the rolling 24-hour budget that resets every morning and is enforced all day.",
        h1="Set Up a Daily Spend Ceiling",
        lead="The daily ceiling is the single most useful budget number. Setup in three steps.",
        sections=[
            ("Step 1 — Pick the number",
             ["Legitimate daily spend × 1.5. Start conservative; loosen with audit-log data."]),
            ("Step 2 — Set the rule",
             ["Create a daily ceiling rule scoped to the agent."]),
            ("Step 3 — Watch and tune",
             ["Review the audit log weekly. If legitimate work gets blocked, raise it; if spend stays near the cap, you found your number."]),
        ],
        code=dict(
            title="Rule",
            lang="json",
            body='{\n  "daily_ceiling": {"max": 500, "currency": "USD", "action": "block"}\n}',
            caption="The day resets; the ceiling enforces.",
        ),
        faqs=[
            ("When does the window reset?",
             "Midnight in your configured timezone."),
            ("Should the ceiling be per agent or per fleet?",
             "Both — per-agent for attribution, a fleet ceiling to stop compounding."),
        ],
        related=[("Daily spend limits", "/limits/daily-spend-limits"), ("Daily spend ceiling", "/glossary/daily-spend-ceiling"), ("Daily ceiling policy", "/policies/daily-ceiling-policy")],
    ),
]

SCENARIOS = [
    dict(
        slug="unknown-vendor-spend-scenario",
        title="Scenario: An Agent Pays an Unknown Vendor",
        desc="Eval Gym scenario: an agent discovers a new vendor and pays it. What the merchant allowlist does — and the FLAG path for legitimately new vendors.",
        h1="Scenario: Unknown Vendor Payment",
        lead="An agent finds a service it needs, from a vendor nobody has vetted, and initiates payment. This is the second-most-common runaway shape in the incident database.",
        sections=[
            ("What happens without a firewall",
             ["The payment settles. The vendor is real — or a typo-squat. Either way, procurement finds out on the invoice."]),
            ("What happens with sipi.bot",
             ["Merchant not on the allowlist → BLOCKED. The agent can't pay an unvetted vendor, full stop."]),
            ("The legit-new-vendor path",
             ["Set the rule to FLAG new merchants instead: the purchase waits in the approval queue while procurement vets the vendor."]),
        ],
        code=dict(
            title="The decision",
            lang="json",
            body='{\n  "decision": "BLOCKED",\n  "reason": "Merchant not on allowlist",\n  "rule_id": "rul_allow_07",\n  "transaction_id": "txn_5f31e0"\n}',
            caption="Unknown vendors are the default-deny.",
        ),
        faqs=[
            ("Does this block legitimate new vendors?",
             "Only if the rule hard-blocks. FLAG instead: new vendors wait for a human, then proceed."),
            ("Is unknown-vendor spend common?",
             "It's one of the documented patterns in the incident database."),
        ],
        related=[("Merchant allowlist", "/glossary/merchant-allowlist"), ("Red flags in agent spend", "/redflags/red-flags-in-agent-spend"), ("Vendor onboarding policy", "/templates/vendor-onboarding-policy")],
    ),
]

REDFLAGS = [
    dict(
        slug="red-flags-in-ai-agent-subscriptions",
        title="Red Flags in AI Agent Subscriptions",
        desc="Six red flags in your AI subscription stack: unused seats, auto-renewing agents, silent tier upgrades, and more.",
        h1="Red Flags in AI Agent Subscriptions",
        lead="Subscription spend is the quiet part of the AI budget — monthly, automatic, and easy to ignore. These six flags say it's drifting.",
        sections=[
            ("The six flags",
             ["1. Unused seats — seats billed but no usage.",
              "2. Auto-renewal drift — tools renewing nobody reviewed.",
              "3. Silent tier upgrades — plans upgraded without a decision.",
              "4. Duplicate tools — three tools doing one job.",
              "5. Agent-scale seats — per-agent plans multiplying faster than value.",
              "6. No owner — subscriptions nobody owns."]),
            ("What to do",
             ["Audit quarterly: export usage, kill unused seats, and put agent tool purchases behind the allowlist so new subscriptions can't appear silently."]),
        ],
        table=dict(
            headers=["Red flag", "Fix"],
            rows=[
                ["Unused seats", "Quarterly usage audit"],
                ["Auto-renewal drift", "Review cadence + owner"],
                ["Silent tier upgrades", "Approval for plan changes"],
                ["Agent-scale seats", "Per-agent budgets"],
            ],
        ),
        faqs=[
            ("How do subscriptions relate to agent spend?",
             "Tool subscriptions are often the first thing agents buy — or the bill that grows when agents scale."),
            ("What's the fastest fix?",
             "Put new tool purchases behind the merchant allowlist; nothing new gets paid without review."),
        ],
        related=[("Merchant allowlist", "/glossary/merchant-allowlist"), ("Weekly spend review", "/templates/weekly-spend-review-template"), ("Red flags in LLM bills", "/redflags/red-flags-in-llm-api-bills")],
    ),
]

GUIDES = [
    dict(
        slug="guide-to-agent-spend-audits",
        title="Guide to Agent Spend Audits",
        desc="How to audit agent spend: what to review, the questions to ask, and how to turn findings into rules. A repeatable process.",
        h1="Agent Spend Audit Guide",
        lead="An agent spend audit turns the audit log into decisions. Here's the process — repeatable, data-driven, and short.",
        sections=[
            ("Step 1 — Pull the data",
             ["Export the audit log: every decision, amount, merchant, category, rule."]),
            ("Step 2 — Ask the questions",
             ["Where is spend going? Which agents, merchants, categories?",
              "What got BLOCKED that shouldn't have? (Rule-tuning signal.)",
              "What got FLAGGED — approved or denied? (Policy signal.)",
              "Any unknown merchants? (Vendor-control signal.)"]),
            ("Step 3 — Turn findings into rules",
             ["One change at a time: raise or lower ceilings, add allowlist entries, adjust thresholds. Measure next week."]),
        ],
        table=dict(
            headers=["Audit question", "Signal"],
            rows=[
                ["Where's the spend?", "Allocation & attribution"],
                ["Blocked-legit?", "Rule too tight"],
                ["Flagged outcomes?", "Threshold tuning"],
                ["Unknown merchants?", "Allowlist gaps"],
            ],
        ),
        faqs=[
            ("How long should an audit take?",
             "30 minutes with the queryable log — most of it reading the flagged and blocked lists."),
            ("How often?",
             "Monthly, plus an incident-triggered review after any runaway."),
        ],
        related=[("How to audit agent spending", "/how-to/how-to-audit-agent-spending"), ("Agent cost audit", "/checklists/agent-cost-audit"), ("Weekly spend review", "/templates/weekly-spend-review-template")],
    ),
]

# --- hub metadata -----------------------------------------------------------
