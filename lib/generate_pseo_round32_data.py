"""Round 32 pSEO data — sipi.bot (2026-08-08).

Thirteenth round. The two biggest missing API-cost queries (claude, gpt)
+ emerging observability + composio/autogpt + educational + personas.
13 static pages + 1 blog.

All existing dirs — no plumbing. Content honest; API pricing marked
verify-current (rate × volume framing).
"""

COST_OF = [
    dict(
        slug="claude-api-cost",
        title="Claude API Cost — Pricing and Agent Spend Control",
        desc="Claude API cost: token pricing for Anthropic models, what agentic usage really costs, and how to control it.",
        h1="How Much Does the Claude API Cost?",
        lead="The Claude API is priced per token, with different models for different jobs. For agents, the bill is rate × volume — and agentic volume is the multiplier nobody plans for.",
        sections=[
            ("How Claude pricing works",
             ["Per-token pricing, input and output, by model family (Haiku, Sonnet, Opus tiers).",
              "Output tokens cost more than input tokens — agents generate a lot of output.",
              "Verify current pricing on Anthropic's site."]),
            ("The agentic multiplier",
             ["Agents send large contexts and generate long outputs per turn.",
              "Retry loops and multi-turn sessions compound volume quickly.",
              "Tool-calling agents add output tokens with every tool result."]),
            ("What it really costs",
             ["Model rate × volume. Context trimming, model selection, and per-agent caps control the total."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Token rates", "Model selection (Haiku vs Sonnet vs Opus)"],
                ["Context size", "Trimming + caching"],
                ["Agentic volume", "Per-agent ceilings"],
                ["Retries", "Velocity limits"],
            ],
        ),
        faqs=[
            ("Is Claude expensive for agents?",
             "It depends on model tier and volume — verify current pricing. The rate is one factor; volume is the bigger one."),
            ("Can sipi.bot control Claude API spend?",
             "Yes — per-agent caps and category rules apply to Anthropic like any merchant."),
        ],
        related=[("GPT API cost", "/cost-of/gpt-api-cost"), ("Anthropic rate limits", "/vs/anthropic-rate-limits"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026")],
    ),
    dict(
        slug="gpt-api-cost",
        title="GPT API Cost — Pricing and Agent Spend Control",
        desc="GPT API cost: token pricing for OpenAI models, the agentic cost reality, and how to control it.",
        h1="How Much Does the GPT API Cost?",
        lead="GPT models are priced per token, with reasoning models costing more per output. Agents burn tokens fast — the bill is rate × volume, and volume is the story.",
        sections=[
            ("How GPT pricing works",
             ["Per-token pricing by model, input and output.",
              "Reasoning models charge premium output rates — and agents reason a lot.",
              "Verify current pricing on OpenAI's site."]),
            ("The agentic multiplier",
             ["Long contexts and long outputs per turn.",
              "Retry loops and multi-turn sessions compound volume.",
              "Reasoning models multiply output costs during planning."]),
            ("What it really costs",
             ["Model rate × volume. Model selection and per-agent caps control the total."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Token rates", "Model selection"],
                ["Reasoning output", "Limit planning depth"],
                ["Agentic volume", "Per-agent ceilings"],
                ["Retries", "Velocity limits"],
            ],
        ),
        faqs=[
            ("Is GPT expensive for agents?",
             "Rates vary by model — verify current pricing. Volume dominates the bill."),
            ("Can sipi.bot control OpenAI spend?",
             "Yes — per-agent caps and category rules apply to OpenAI like any merchant."),
        ],
        related=[("Claude API cost", "/cost-of/claude-api-cost"), ("OpenAI usage", "/vs/openai-usage"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026")],
    ),
]

VS = [
    dict(
        slug="langwatch",
        name="LangWatch",
        title="sipi.bot vs LangWatch — LLM Observability vs Spend Firewall",
        desc="LangWatch monitors LLM behavior; sipi.bot gates agent spend. Observability after, enforcement before.",
        h1="sipi.bot vs LangWatch",
        lead="LangWatch is LLM observability and evaluation. sipi.bot is a pre-spend firewall. One watches the pipeline; the other gates the money.",
        sections=[
            ("What LangWatch does well",
             ["LLM tracing, evaluation, and guardrail monitoring.",
              "Useful for catching behavioral issues post-hoc."]),
            ("Where it falls short for agent spend",
             ["Observability is after the fact — no pre-spend decision on transactions."]),
            ("Where sipi.bot wins",
             ["Deterministic decisions before settlement.",
              "Caps, allowlists, velocity limits, approvals."]),
            ("When to use which",
             ["LangWatch for monitoring; sipi.bot for enforcement. Complementary."]),
        ],
        table=dict(
            headers=["Dimension", "LangWatch", "sipi.bot"],
            rows=[
                ["Role", "LLM observability", "Pre-spend firewall"],
                ["When it acts", "After requests", "Before transactions"],
                ["Controls", "Traces, evals", "Caps, allowlists, approvals"],
                ["Decision", "Insights", "APPROVED / BLOCKED / FLAGGED"],
            ],
        ),
        faqs=[
            ("Do they overlap?",
             "Minimally — monitoring vs enforcement."),
            ("What's the compose pattern?",
             "Watch with LangWatch, gate with sipi.bot."),
        ],
        related=[("Best observability tools", "/best/best-ai-agent-observability-tools"), ("sipi.bot vs Langfuse", "/vs/langfuse"), ("sipi.bot vs HoneyHive", "/vs/honeyhive")],
    ),
    dict(
        slug="honeyhive",
        name="HoneyHive",
        title="sipi.bot vs HoneyHive — LLM Evaluation vs Spend Firewall",
        desc="HoneyHive evaluates LLM apps; sipi.bot gates agent spend. Evaluation informs, enforcement decides.",
        h1="sipi.bot vs HoneyHive",
        lead="HoneyHive is an LLM evaluation and observability platform. sipi.bot is a pre-spend firewall. One measures quality; the other gates money.",
        sections=[
            ("What HoneyHive does well",
             ["LLM evaluation, tracing, and prompt management.",
              "Strong for iterative quality work."]),
            ("Where it falls short for agent spend",
             ["Evaluation is post-hoc — no pre-spend decision on transactions."]),
            ("Where sipi.bot wins",
             ["Deterministic pre-spend decisions across every merchant."]),
            ("When to use which",
             ["HoneyHive for quality; sipi.bot for spend. Complementary."]),
        ],
        table=dict(
            headers=["Dimension", "HoneyHive", "sipi.bot"],
            rows=[
                ["Role", "LLM evaluation", "Pre-spend firewall"],
                ["When it acts", "After requests", "Before transactions"],
                ["Controls", "Evals, traces", "Caps, allowlists, approvals"],
                ["Decision", "Insights", "APPROVED / BLOCKED / FLAGGED"],
            ],
        ),
        faqs=[
            ("Are they competitors?",
             "No — evaluation and enforcement are different layers."),
            ("Can decisions feed HoneyHive?",
             "Yes — the audit log is API-queryable."),
        ],
        related=[("Best observability tools", "/best/best-ai-agent-observability-tools"), ("sipi.bot vs LangWatch", "/vs/langwatch"), ("sipi.bot vs PromptLayer", "/vs/promptlayer")],
    ),
]

INTEGRATIONS = [
    dict(
        slug="composio",
        title="Composio Agent Spend Control — sipi.bot Integration",
        desc="Composio connects agents to 300+ tools. sipi.bot gates the spend those tools can trigger.",
        h1="Spend Control for Composio",
        lead="Composio gives agents access to hundreds of tools and apps. More tools, more spend surfaces — the guard keeps the money path honest.",
        sections=[
            ("Why Composio agents overspend",
             ["300+ connected tools mean 300+ potential paid calls.",
              "Tool access is permissive by design.",
              "No dollar-level budget at the tool layer."]),
            ("How it works",
             ["Compose the sipi.bot guard into your tool set: before any spend-capable tool runs, the agent gets a deterministic decision."]),
            ("Rules that fit",
             ["Merchant allowlist for paid tools.",
              "Per-agent daily ceiling.",
              "Category rule: data vs compute vs payments."]),
        ],
        code=dict(
            title="Guard in the tool set",
            lang="typescript",
            body='const res = await fetch("https://sipi.bot/v1/transactions/evaluate", {\n  method: "POST", headers: { "Content-Type": "application/json" },\n  body: JSON.stringify({ amount: 15, merchant: "connected-app.com", category: "api" }),\n});\nconst { decision } = await res.json();',
            caption="Every connected tool, one gate.",
        ),
        faqs=[
            ("Does this slow tool calls?",
             "No — ~5 ms per check, spend-capable tools only."),
            ("Can I whitelist per integration?",
             "Yes — the merchant allowlist maps to connected apps."),
        ],
        related=[("MCP", "/integrations/mcp"), ("Tool calling", "/glossary/tool-calling"), ("How to implement spend controls", "/how-to/how-to-implement-spend-controls")],
    ),
    dict(
        slug="autogpt",
        title="AutoGPT Agent Spend Control — sipi.bot Integration",
        desc="AutoGPT autonomous agents iterate until done — and each iteration can spend. Cap it with the guard.",
        h1="Spend Control for AutoGPT",
        lead="AutoGPT agents run autonomous loops — plan, act, iterate — and every iteration can call a paid tool. The guard bounds the loop.",
        sections=[
            ("Why AutoGPT agents overspend",
             ["Autonomous loops iterate until the goal is met.",
              "Each iteration can trigger paid tool calls.",
              "Loops that miss the goal retry and compound."]),
            ("How it works",
             ["Add the guard as a tool: before any spend, the agent gets APPROVED, BLOCKED, or FLAGGED."]),
            ("Rules that fit",
             ["Per-task ceiling.",
              "Velocity limit on loop iterations.",
              "Merchant allowlist for paid tools."]),
        ],
        code=dict(
            title="Guard call",
            lang="python",
            body='from sipi_guard import sipi_guard\n\ndecision = sipi_guard(amount=25, merchant="api.vendor.com", category="api")\n# APPROVED | BLOCKED | FLAGGED',
            caption="Loops with a budget.",
        ),
        faqs=[
            ("Does this stop AutoGPT's loop?",
             "No — it gates spend actions; the loop continues within budget."),
            ("What about sub-agents?",
             "Fleet rules cover the whole run."),
        ],
        related=[("Subagent", "/glossary/subagent"), ("Retry loop", "/glossary/retry-loop"), ("How to stop runaway agents", "/how-to/how-to-stop-runaway-agents")],
    ),
]

LEARN = [
    dict(
        slug="what-is-an-ai-agent",
        title="What Is an AI Agent?",
        desc="AI agents defined: perception, decision, action — and why the action layer is where the money moves.",
        h1="What Is an AI Agent?",
        lead="An AI agent is a system that perceives context, decides on an action, and acts — often with tools. The definition is simple; the implications for spend are not.",
        sections=[
            ("The core loop",
             ["Perceive: take in context (prompts, tools, state).",
              "Decide: choose the next action.",
              "Act: call a tool, write output, or trigger a workflow."]),
            ("Why agents are different from chatbots",
             ["Chatbots respond; agents act. Acting means side effects — including spending money."]),
            ("The spend implication",
             ["Every action can be a purchase. Agents with tool access are spend-capable by design.",
              "That's why the money path needs a deterministic gate."]),
        ],
        faqs=[
            ("Do all agents spend money?",
             "Only those with access to paid tools — but tool access is the norm."),
            ("What's the difference from an LLM?",
             "An LLM generates text; an agent decides and acts with tools."),
        ],
        related=[("Agentic AI", "/glossary/agentic-ai"), ("Agentic workflow", "/glossary/agentic-workflow"), ("How agents spend money", "/learn/how-autonomous-agents-spend-money")],
    ),
]

FOR = [
    dict(
        slug="venture-capital",
        title="AI Agent Spend Control for Venture Capital | sipi.bot",
        desc="VCs and portfolio ops: agent spend is a diligence signal and a portfolio risk. The control framework to ask for.",
        h1="AI Agent Spend Control for Venture Capital",
        lead="For VCs, agent spend is two things: a diligence signal for AI startups and a governance risk across the portfolio. Here's the framework to ask for.",
        sections=[
            ("The diligence angle",
             ["Is spend controlled or ad-hoc? The answer predicts runaway risk.",
              "Ask for: ceilings, allowlists, approval thresholds, and an audit trail."]),
            ("The portfolio angle",
             ["Portfolio companies building agents face the same runaways documented in the incident database.",
              "A standard spend-control ask de-risks every AI bet."]),
            ("The signal",
             ["Deterministic controls on the money path = operational maturity. That's the pattern the best teams show."]),
        ],
        table=dict(
            headers=["VC question", "What to look for"],
            rows=[
                ["Spend controlled?", "Ceilings + allowlists"],
                ["Auditable?", "Decision log"],
                ["Runaway risk?", "Velocity limits"],
                ["Operational maturity", "Deterministic controls"],
            ],
        ),
        faqs=[
            ("Is agent spend a real diligence item?",
             "It's becoming one — runaways are documented financial events."),
            ("What's the minimum ask?",
             "A decision log and a ceiling policy for every spend-capable agent."),
        ],
        related=[("CFOs", "/for/chief-financial-officers"), ("Incident database", "/incidents/"), ("Best agent budgeting tools", "/best/best-agent-budgeting-tools")],
    ),
]

SECTORS = [
    dict(
        slug="travel",
        title="AI Spend Control for Travel | sipi.bot",
        desc="Travel AI agents: booking, itinerary, and support bots that spend on inventory, data, and inference per traveler.",
        h1="Spend Control for Travel AI Agents",
        lead="Travel agents book inventory, build itineraries, and answer support — each with paid APIs per traveler. Per-cohort budgets.",
        sections=[
            ("Where travel agents spend",
             ["Booking and inventory APIs per search.",
              "Itinerary generation inference per traveler.",
              "Support bots at volume.",
              "Market-data feeds for pricing."]),
            ("The failure modes",
             ["A booking-loop retry multiplies per-search charges.",
              "Unknown inventory vendors bypass procurement.",
              "Peak-season spikes hit overage tiers."]),
            ("Which rules to start with",
             ["Per-cohort daily ceiling.",
              "Merchant allowlist for inventory vendors.",
              "Velocity limit on search loops."]),
        ],
        table=dict(
            headers=["Travel spend", "Control"],
            rows=[
                ["Inventory APIs", "Per-cohort ceiling"],
                ["Itinerary inference", "Daily cap"],
                ["Support bots", "Category budget"],
                ["Market data", "Merchant allowlist"],
            ],
        ),
        faqs=[
            ("Can I budget per channel?",
             "Yes — per-agent rules per channel or cohort."),
            ("Does it slow booking?",
             "No — ~5 ms per check."),
        ],
        related=[("Hospitality sector", "/sectors/hospitality"), ("E-commerce sector", "/sectors/ecommerce"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
]

SCENARIOS = [
    dict(
        slug="api-key-compromise-scenario",
        title="API Key Compromise Scenario — What the Firewall Does",
        desc="The API-key-compromise eval scenario: a leaked key drives spend before the breach is found. The firewall's role.",
        h1="API Key Compromise Scenario",
        lead="A leaked API key is spend before it's a headline: an attacker (or an agent) with a valid key can drive transactions. The eval gym tests what the firewall does.",
        sections=[
            ("The scenario",
             ["A valid key leaks (repo, logs, prompt).",
              "Attacker-driven requests begin spending immediately.",
              "Traditional detection finds it after the fact."]),
            ("What the firewall does",
             ["Caps bound the damage per agent and per window.",
              "Velocity limits stop automated bursts.",
              "Merchant allowlists stop unknown destinations.",
              "The audit log shows exactly what moved."]),
            ("The honest limit",
             ["The firewall can't un-leak a key — it limits the blast radius and logs it."]),
        ],
        faqs=[
            ("Is this scenario in the eval gym?",
             "Yes — key-compromise is one of the 53 eval scenarios, 53/53 passing."),
            ("What else should I do?",
             "Rotate keys fast and put spend limits on every key — both."),
        ],
        related=[("Eval report", "/eval-report/"), ("Red flags in API keys", "/redflags/red-flags-in-api-keys"), ("Secret scanning", "/for/security-engineers")],
    ),
]

PRICING_QUESTIONS = [
    dict(
        slug="is-sipi-bot-open-source",
        title="Is sipi.bot Open Source?",
        desc="The honest answer: the decision engine core is MIT-licensed and self-hosts. The hosted layer isn't. What that means for you.",
        h1="Is sipi.bot Open Source?",
        lead="The core decision engine is MIT-licensed and self-hostable. The hosted dashboard and managed layer are not. Here's the exact split.",
        sections=[
            ("What's open",
             ["The deterministic rules engine — all six rule types, HTTP API, MCP tool, CLI.",
              "MIT license: use, modify, embed, self-host, no gating."]),
            ("What's not",
             ["The hosted dashboard, managed approval queue, and stored audit log are hosted-only."]),
            ("Why the split",
             ["The engine is the commodity; the managed experience is the product. Self-host for control, hosted for zero ops."]),
        ],
        table=dict(
            headers=["Layer", "Open?"],
            rows=[
                ["Rules engine", "Yes — MIT"],
                ["HTTP API / MCP / CLI", "Yes"],
                ["Hosted dashboard", "No — hosted"],
                ["Managed approval queue", "No — hosted"],
            ],
        ),
        faqs=[
            ("Can I fork it?",
             "Yes — MIT. The eval gym runs on the same core."),
            ("Is self-host the same engine?",
             "Yes — the exact deterministic engine, your infrastructure."),
        ],
        related=[("Can I self-host", "/pricing-questions/can-i-self-host-sipi-bot"), ("Self-host guide", "/guides/guide-to-self-hosting"), ("Self-host tutorial", "/tutorials/self-host-in-docker")],
    ),
]

ANSWERS = [
    dict(
        slug="how-much-do-ai-agents-cost",
        title="How Much Do AI Agents Cost?",
        desc="The honest agent cost answer: per-call pennies, per-month surprises. The drivers and the levers.",
        h1="How Much Do AI Agents Cost?",
        lead="A single agent call costs pennies. A fleet of agents costs real money — the bill is volume, retries, and ungoverned tools, not the token rate.",
        sections=[
            ("The honest shape",
             ["Per call: pennies — tokens plus tool calls.",
              "Per day: the multiplier — agents call tools hundreds of times.",
              "Per month: whatever isn't governed — the documented runaways range from hundreds to millions."]),
            ("The cost drivers",
             ["Volume (calls per task), retries (loops), context (long sessions), and tools (paid APIs)."]),
            ("The levers",
             ["Ceilings bound the total, velocity limits kill the loops, allowlists control the vendors, and model choice cuts the rate."]),
        ],
        table=dict(
            headers=["Timeframe", "Reality"],
            rows=[
                ["Per call", "Pennies"],
                ["Per day", "The multiplier"],
                ["Per month", "Whatever isn't governed"],
            ],
        ),
        faqs=[
            ("What's the biggest cost driver?",
             "Volume and retries — not the rate card."),
            ("What's the fastest fix?",
             "A velocity limit and a per-agent ceiling."),
        ],
        related=[("Why agents cost so much", "/answers/why-do-ai-agents-cost-so-much/"), ("Agent cost breakdown", "/blog/how-much-does-an-agent-cost-to-run"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs")],
    ),
]

# --- hub metadata -----------------------------------------------------------
