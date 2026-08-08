"""Round 36 pSEO data — sipi.bot (2026-08-08).

Seventeenth round. LLM gateway category, xAI API cost, indie-hackers persona,
insurance/retail sectors, provider selection, token caching, agent identity,
provider evaluation, security answers, one-api comparison.
12 static pages + 1 blog.

All existing dirs — no plumbing. Content honest.
"""

BEST = [
    dict(
        slug="best-llm-gateways-2026",
        title="Best LLM Gateways 2026 — Honest Comparison",
        desc="The best LLM gateways: LiteLLM Proxy, Kong AI Gateway, Cloudflare AI Gateway, Portkey, and how gateways differ from a spend firewall.",
        h1="Best LLM Gateways 2026",
        lead="An LLM gateway routes, observes, and sometimes rate-limits model traffic. The best one for you depends on scale, stack, and whether you need a money gate too.",
        sections=[
            ("The gateways teams actually run",
             ["LiteLLM Proxy — the open-source standard for model routing and key management.",
              "Kong AI Gateway — enterprise gateway with AI plugins.",
              "Cloudflare AI Gateway — edge routing with analytics.",
              "Portkey — gateway plus observability."]),
            ("What gateways do",
             ["Route to models, manage keys, add caching and fallbacks.",
              "Some rate-limit — but rate limits aren't dollar budgets."]),
            ("Gateway vs spend firewall",
             ["A gateway manages how requests reach models.",
              "A spend firewall decides whether money moves — for every merchant, not just model providers.",
              "They compose: gateway for routing, firewall for the money."]),
        ],
        table=dict(
            headers=["Tool", "Best at", "Spend layer"],
            rows=[
                ["LiteLLM Proxy", "Model routing", "External firewall"],
                ["Kong AI Gateway", "Enterprise gateway", "External firewall"],
                ["Cloudflare AI Gateway", "Edge routing", "External firewall"],
                ["Portkey", "Gateway + observability", "External firewall"],
            ],
        ),
        faqs=[
            ("Is a gateway a firewall?",
             "No — a gateway routes traffic. Rate limits stop requests, not purchases."),
            ("Do I need both?",
             "At agent scale, yes — gateway for the model layer, firewall for the money layer."),
        ],
        related=[("sipi.bot vs LiteLLM", "/vs/litellm"), ("sipi.bot vs Cloudflare AI Gateway", "/vs/cloudflare-ai-gateway"), ("sipi.bot vs Kong", "/vs/kong-ai-gateway")],
    ),
]

COST_OF = [
    dict(
        slug="xai-api-cost",
        title="xAI API Cost — Grok Pricing and Agent Spend Control",
        desc="xAI API cost: Grok model token pricing and how to control agent spend on Grok.",
        h1="How Much Does the xAI API Cost?",
        lead="xAI's API is per token by Grok model. Grok is fast — and fast models invite volume. The bill is rate × volume.",
        sections=[
            ("How xAI pricing works",
             ["Per-token pricing by Grok model.",
              "Verify current pricing on xAI's site."]),
            ("The agentic multiplier",
             ["Fast inference invites more calls.",
              "Retry loops at speed multiply volume."]),
            ("What it really costs",
             ["Rate × volume. Velocity limits and per-agent caps control the volume."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Token rates", "Model selection"],
                ["Fast loops", "Velocity limit"],
                ["Fleet volume", "Per-agent ceilings"],
            ],
        ),
        faqs=[
            ("Is Grok cheaper?",
             "Rates vary by model — verify current pricing."),
            ("Can sipi.bot govern xAI spend?",
             "Yes — per-agent caps and category rules."),
        ],
        related=[("GPT API cost", "/cost-of/gpt-api-cost"), ("Groq API cost", "/cost-of/groq-api-cost"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026")],
    ),
]

FOR = [
    dict(
        slug="indie-hackers",
        title="AI Agent Spend Control for Indie Hackers | sipi.bot",
        desc="Indie hackers: one runaway can wipe a month of margin. Cap agent spend before the first launch.",
        h1="AI Agent Spend Control for Indie Hackers",
        lead="For indie hackers, every dollar counts — and an ungoverned agent is one retry loop away from a bad month. The firewall is cheap; the runaway isn't.",
        sections=[
            ("Why indie hackers need it",
             ["Margins are thin — one runaway wipes real revenue.",
              "Solo teams have no one watching the agents.",
              "The free tier + MIT core makes it cost nothing to start."]),
            ("Where indie agents spend",
             ["Inference on side-project agents.",
              "Tools and APIs per task.",
              "Scraping and data vendors."]),
            ("Which rules to start with",
             ["Per-agent daily ceiling.",
              "Velocity limit on retries.",
              "Merchant allowlist for paid tools."]),
        ],
        table=dict(
            headers=["Indie spend", "Control"],
            rows=[
                ["Inference", "Daily ceiling"],
                ["Tools", "Merchant allowlist"],
                ["Retries", "Velocity limit"],
            ],
        ),
        faqs=[
            ("Is it free to start?",
             "The MIT core self-hosts free; hosted starts at a small flat rate."),
            ("What's the biggest risk?",
             "A runaway on an unattended side project — one loop, bad month."),
        ],
        related=[("AI startups", "/use-cases/ai-startups"), ("Solo developers", "/for/startup-founders"), ("How to set a budget", "/answers/how-to-set-a-budget-for-ai-agents/")],
    ),
]

SECTORS = [
    dict(
        slug="insurance",
        title="AI Spend Control for Insurance | sipi.bot",
        desc="Insurance AI agents: claims, underwriting, and compliance bots that spend on data and inference per policy.",
        h1="Spend Control for Insurance AI Agents",
        lead="Insurers run agents for claims, underwriting, and compliance — each with paid data and inference per policy. Per-line-of-business budgets.",
        sections=[
            ("Where insurance agents spend",
             ["Claims-review inference per claim.",
              "Underwriting data pulls per application.",
              "Fraud-check databases per event.",
              "Compliance documentation at scale."]),
            ("The failure modes",
             ["A claims re-review loop multiplies inference.",
              "Unknown data vendors bypass procurement.",
              "No per-LOB budget."]),
            ("Which rules to start with",
             ["Per-LOB daily ceiling.",
              "Merchant allowlist for data vendors.",
              "Approval threshold for payouts."]),
        ],
        table=dict(
            headers=["Insurance spend", "Control"],
            rows=[
                ["Claims review", "Per-claim ceiling"],
                ["Underwriting data", "Category budget"],
                ["Fraud checks", "Merchant allowlist"],
                ["Payouts", "Approval threshold"],
            ],
        ),
        faqs=[
            ("Can I budget per LOB?",
             "Yes — per-agent rules per line of business."),
            ("Does it slow claims?",
             "No — ~5 ms per check."),
        ],
        related=[("Claims processing", "/use-cases/claims-processing-agents"), ("Fintech sector", "/sectors/fintech"), ("How to implement spend controls", "/how-to/how-to-implement-spend-controls")],
    ),
    dict(
        slug="retail",
        title="AI Spend Control for Retail | sipi.bot",
        desc="Retail AI agents: pricing, inventory, and customer-service bots that spend on data and ads per store.",
        h1="Spend Control for Retail AI Agents",
        lead="Retailers run agents for pricing, inventory, and customer service — each with paid data and inference per store. Per-channel budgets.",
        sections=[
            ("Where retail agents spend",
             ["Pricing agents pulling competitor data.",
              "Inventory forecasting APIs per SKU.",
              "Customer-service bots at volume.",
              "Ad and promotion agents per channel."]),
            ("The failure modes",
             ["A pricing-loop retry multiplies data charges.",
              "Local ad agents overspend per store.",
              "Peak-season spikes hit overage tiers."]),
            ("Which rules to start with",
             ["Per-channel daily ceiling.",
              "Category rule: data vs ads vs support.",
              "Velocity limit on data loops."]),
        ],
        table=dict(
            headers=["Retail spend", "Control"],
            rows=[
                ["Pricing data", "Per-channel ceiling"],
                ["Inventory APIs", "Category budget"],
                ["Support bots", "Daily cap"],
                ["Ads", "Per-store ad cap"],
            ],
        ),
        faqs=[
            ("Can I cap per store?",
             "Yes — per-agent rules per store or channel."),
            ("Does it slow pricing?",
             "No — ~5 ms per check."),
        ],
        related=[("E-commerce sector", "/sectors/ecommerce"), ("Marketing sector", "/sectors/marketing"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
]

HOW_TO = [
    dict(
        slug="how-to-choose-an-llm-provider",
        title="How to Choose an LLM Provider",
        desc="Choose an LLM provider on the axes that matter: rate, latency, quality, and — for agents — governance.",
        h1="How to Choose an LLM Provider",
        lead="Rate cards are the start, not the decision. Providers matter on quality, latency, and how easy they make governance.",
        sections=[
            ("Step 1 — Match the model to the task",
             ["Small models for simple work, big models for complex reasoning.",
              "Benchmark against YOUR tasks, not leaderboards."]),
            ("Step 2 — Look past the rate card",
             ["Latency and reliability affect agent outcomes.",
              "Context windows and rate limits shape the workload."]),
            ("Step 3 — Check the governance story",
             ["What budgets and limits exist natively?",
              "Every provider needs the same money gate — the firewall is provider-agnostic."]),
            ("Step 4 — Measure with your log",
             ["Run the pilot, read the audit log, compare real cost per task."]),
        ],
        faqs=[
            ("Should I use one provider or many?",
             "Many teams route across providers — that's what gateways are for."),
            ("What's the cheapest provider?",
             "Cheapest per token isn't cheapest per task — measure your shape."),
        ],
        related=[("Best LLM gateways", "/best/best-llm-gateways-2026"), ("GPT vs Claude cost", "/cost-of/gpt-api-cost"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026")],
    ),
]

GLOSSARY = [
    dict(
        slug="token-caching",
        term="Token caching",
        title="What is Token Caching? | sipi.bot Glossary",
        desc="Token caching reuses billed context across calls — the single biggest lever on the rate side of the cost equation.",
        h1="What is Token Caching?",
        lead="Token caching lets providers reuse your context across calls and bill it at a discount — the biggest lever on the rate side of the cost equation.",
        sections=[
            ("How it works",
             ["Providers cache stable prefixes (system prompts, tool schemas).",
              "Cached input tokens bill at a lower rate."]),
            ("Why it matters for agents",
             ["Agents re-send large contexts every turn.",
              "Caching turns repeated context into a discount."]),
            ("The honest caveat",
             ["Cache hit rates vary by workload — measure yours.",
              "Caching cuts the rate; it doesn't govern the volume."]),
        ],
        faqs=[
            ("Is caching automatic?",
             "Often, for stable prefixes — check your provider's docs."),
            ("Does caching replace caps?",
             "No — it cuts rate; caps bound volume. Both."),
        ],
        related=[("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs"), ("Context window", "/glossary/context-window"), ("Cache-hit benchmark", "/benchmarks/token-cache-hit-savings")],
    ),
    dict(
        slug="agent-identity",
        term="Agent identity",
        title="What is Agent Identity? | sipi.bot Glossary",
        desc="Agent identity is how a system knows which agent is spending — the key to attribution and per-agent budgets.",
        h1="What is Agent Identity?",
        lead="Agent identity is how the system knows which agent is acting — the foundation of per-agent budgets and audit.",
        sections=[
            ("What it is",
             ["A stable identifier per agent (or per key).",
              "Scoped credentials tied to one agent."]),
            ("Why it matters",
             ["Attribution: the audit log answers 'which agent spent?'",
              "Budgeting: per-agent ceilings need per-agent identity.",
              "Security: scoped keys limit blast radius."]),
            ("The control",
             ["Per-agent keys with their own rules and limits."]),
        ],
        faqs=[
            ("Why not one key for everything?",
             "One key means no attribution and no per-agent limits — the opposite of governance."),
            ("What's the minimum?",
             "A scoped key per spend-capable agent."),
        ],
        related=[("Agent audit trail", "/glossary/agent-audit-trail"), ("Red flags in API keys", "/redflags/red-flags-in-api-keys"), ("How to track AI agent costs", "/answers/how-to-track-ai-agent-costs/")],
    ),
]

TEMPLATES = [
    dict(
        slug="llm-provider-evaluation-template",
        title="LLM Provider Evaluation Template",
        desc="The evaluation matrix for choosing an LLM provider: task fit, rate, latency, limits, and governance.",
        h1="LLM Provider Evaluation Template",
        lead="Choosing a provider is a decision with many axes. This template makes it a scored matrix instead of a vibe.",
        sections=[
            ("The matrix",
             ["1. Task fit: benchmark score on YOUR tasks.",
              "2. Rate: real cost per task, not per token.",
              "3. Latency: p95 for your workload shape.",
              "4. Limits: rate limits, context window, concurrency.",
              "5. Reliability: uptime and incident history.",
              "6. Governance: native budgets, key scoping, logs.",
              "7. Score each 1–5, weighted by your priorities."]),
        ],
        faqs=[
            ("What's the most common mistake?",
             "Picking on rate alone — per-task cost is the real number."),
            ("How often should I re-evaluate?",
             "Quarterly, or when pricing changes."),
        ],
        related=[("How to choose an LLM provider", "/how-to/how-to-choose-an-llm-provider"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026"), ("Vendor risk assessment", "/templates/vendor-risk-assessment-template")],
    ),
]

ANSWERS = [
    dict(
        slug="are-ai-agents-secure",
        title="Are AI Agents Secure?",
        desc="The honest security answer: agents are as secure as their credentials, tools, and money path. The three layers and the controls.",
        h1="Are AI Agents Secure?",
        lead="Agents are as secure as three layers: credentials, tools, and the money path. Secure the weakest one — it's usually the money path.",
        sections=[
            ("The credential layer",
             ["Scoped keys per agent, rotation, and secret scanning.",
              "A leaked key is spend before it's a headline."]),
            ("The tool layer",
             ["Vet MCP servers and tools — source, permissions, paid calls."]),
            ("The money layer",
             ["Deterministic gates on the money path: caps, allowlists, velocity limits.",
              "Prompts can be injected; rules can't."]),
        ],
        faqs=[
            ("What's the biggest agent security risk?",
             "Ungoverned spend — it's the least-guarded layer and the most expensive."),
            ("Where should I start?",
             "Secret scanning, MCP vetting, and a spend firewall — in that order."),
        ],
        related=[("Best agent security tools", "/best/best-agent-security-tools"), ("API key compromise scenario", "/scenarios/api-key-compromise-scenario"), ("MCP security checklist", "/checklists/mcp-security-checklist/")],
    ),
    dict(
        slug="how-to-prevent-ai-agent-fraud",
        title="How to Prevent AI Agent Fraud",
        desc="Prevent agent fraud: unauthorized spend, credential abuse, and injection-driven payments. The control stack.",
        h1="How to Prevent AI Agent Fraud",
        lead="Agent fraud is unauthorized spend — from stolen keys, injected instructions, or abused tools. The prevention stack is deterministic.",
        sections=[
            ("The fraud shapes",
             ["Credential abuse: a leaked key spending as your agent.",
              "Injection-driven payments: instructions in content trigger purchases.",
              "Tool abuse: a compromised tool spends beyond intent."]),
            ("The prevention stack",
             ["Scoped keys per agent — limit the blast radius.",
              "Merchant allowlists — unknown destinations default-deny.",
              "Caps and velocity limits — bound and slow the damage.",
              "Audit log — attribution for every decision."]),
        ],
        faqs=[
            ("What's the most common fraud?",
             "Credential abuse and injection-driven spend — both bounded by the same rules."),
            ("Can the firewall prevent all fraud?",
             "It prevents unauthorized SPEND. A stolen key still needs rotation — caps limit the window."),
        ],
        related=[("Are AI agents secure", "/answers/are-ai-agents-secure/"), ("API key compromise scenario", "/scenarios/api-key-compromise-scenario"), ("Red flags in API keys", "/redflags/red-flags-in-api-keys")],
    ),
]

VS = [
    dict(
        slug="one-api",
        name="One API",
        title="sipi.bot vs One API — LLM Gateway vs Spend Firewall",
        desc="One API routes LLM traffic; sipi.bot gates agent spend. Gateway for the model layer, firewall for the money.",
        h1="sipi.bot vs One API",
        lead="One API is an open-source LLM gateway for routing and key management. sipi.bot is a pre-spend firewall. One routes requests; the other gates money.",
        sections=[
            ("What One API does well",
             ["Open-source LLM gateway with multi-provider routing.",
              "Key management and usage tracking."]),
            ("Where it falls short for agent spend",
             ["It routes model traffic; it doesn't decide whether an agent may pay a merchant."]),
            ("Where sipi.bot wins",
             ["Pre-spend decisions across every merchant.",
              "Caps, allowlists, velocity limits, approvals."]),
            ("When to use which",
             ["One API for the model layer; sipi.bot for the money layer. They compose."]),
        ],
        table=dict(
            headers=["Dimension", "One API", "sipi.bot"],
            rows=[
                ["Role", "LLM gateway", "Pre-spend firewall"],
                ["Scope", "Model traffic", "All agent merchants"],
                ["When it acts", "Routes requests", "Before transactions"],
                ["Controls", "Keys, routing", "Caps, allowlists, approvals"],
            ],
        ),
        faqs=[
            ("Is One API a firewall?",
             "No — a gateway routes traffic. Rate limits stop requests, not purchases."),
            ("Can I use both?",
             "Yes — route with One API, gate with sipi.bot."),
        ],
        related=[("sipi.bot vs LiteLLM", "/vs/litellm"), ("Best LLM gateways", "/best/best-llm-gateways-2026"), ("How to choose an LLM provider", "/how-to/how-to-choose-an-llm-provider")],
    ),
]

# --- hub metadata -----------------------------------------------------------
