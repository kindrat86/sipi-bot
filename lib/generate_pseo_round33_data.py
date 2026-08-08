"""Round 33 pSEO data — sipi.bot (2026-08-08).

Fourteenth round. Provider-cost sweep completion (Azure OpenAI, Bedrock,
Vertex, Ollama local) + Manus/gpt-engineer integrations + AI-bill learning
layer + tracking tools. 13 static pages + 1 blog.

All existing dirs — no plumbing. Content honest; provider pricing
verify-current; local-inference costs framed as hardware + power + time, not
invented numbers.
"""

COST_OF = [
    dict(
        slug="azure-openai-cost",
        title="Azure OpenAI Cost — Pricing and Agent Spend Control",
        desc="Azure OpenAI cost: token pricing on Azure, the enterprise premium, and how to control agent spend.",
        h1="How Much Does Azure OpenAI Cost?",
        lead="Azure OpenAI is OpenAI's models served through Azure — per-token pricing with enterprise features. For agents, the bill is rate × volume, with Azure's own usage costs layered on.",
        sections=[
            ("How Azure OpenAI pricing works",
             ["Per-token pricing by model, aligned with OpenAI's rates.",
              "Enterprise agreements, committed throughput, and Azure egress on top.",
              "Verify current pricing on Microsoft's site."]),
            ("The agentic multiplier",
             ["Agents on Azure OpenAI burn tokens at agentic volume.",
              "Egress and throughput commitments add a second cost line.",
              "Retry loops compound both."]),
            ("What it really costs",
             ["Token rate × volume + Azure usage. Per-agent caps and velocity limits control the volume."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Token rates", "Model selection"],
                ["Egress/throughput", "Right-size commitments"],
                ["Agentic volume", "Per-agent ceilings"],
                ["Retries", "Velocity limits"],
            ],
        ),
        faqs=[
            ("Is Azure OpenAI cheaper?",
             "Rates are close to OpenAI's — verify current pricing. The enterprise terms are the differentiator."),
            ("Can sipi.bot control Azure OpenAI spend?",
             "Yes — per-agent caps and category rules apply to any merchant."),
        ],
        related=[("GPT API cost", "/cost-of/gpt-api-cost"), ("Azure AI Foundry", "/vs/azure-ai-foundry"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026")],
    ),
    dict(
        slug="ollama-cost",
        title="Ollama Cost — Local LLM Pricing and Spend Control",
        desc="Ollama cost: local inference is hardware + power + time, not tokens. What local models really cost — and why agents still need a budget.",
        h1="How Much Does Ollama Cost?",
        lead="Ollama is free software — the cost is the hardware, the power, and the time. Local inference trades token bills for a different ledger.",
        sections=[
            ("How local inference is priced",
             ["No per-token fee — you pay for the GPU, the machine, and the electricity.",
              "Hardware cost per million tokens depends on the model size and your rig.",
              "Time is the hidden cost: slower models mean longer agent loops."]),
            ("The honest comparison",
             ["Local can win at high steady volume; hosted wins for spiky or varied workloads.",
              "The real cost is total cost of ownership, not the rate card."]),
            ("Why agents still need a budget",
             ["Local models still call paid tools and APIs.",
              "A local inference stack doesn't govern the spend beyond it."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Hardware", "Model size vs rig"],
                ["Power", "Utilization"],
                ["Time", "Agent loop design"],
                ["Tools/APIs", "Firewall rules"],
            ],
        ),
        faqs=[
            ("Is local always cheaper?",
             "No — it depends on volume and hardware. Model the TCO, don't guess."),
            ("Does sipi.bot work with local stacks?",
             "Yes — the firewall governs tool and API spend regardless of where inference runs."),
        ],
        related=[("Local vs hosted benchmark", "/benchmarks/local-llm-vs-hosted-api-cost"), ("vLLM cost", "/cost-of/vllm-cost"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs")],
    ),
    dict(
        slug="aws-bedrock-cost",
        title="AWS Bedrock Cost — Pricing and Agent Spend Control",
        desc="AWS Bedrock cost: model token pricing on AWS, plus usage and egress. How to control agent spend on Bedrock.",
        h1="How Much Does AWS Bedrock Cost?",
        lead="Bedrock bills per token by model, with AWS usage costs on top. The platform makes model access easy; the bill still follows volume.",
        sections=[
            ("How Bedrock pricing works",
             ["Per-token pricing by model from multiple providers.",
              "AWS usage (requests, egress, provisioned throughput) layered on.",
              "Verify current pricing on AWS's site."]),
            ("The agentic multiplier",
             ["Agent workloads burn tokens at volume.",
              "Provisioned throughput is an upfront commitment — size it right."]),
            ("What it really costs",
             ["Token rate × volume + AWS usage. Caps and velocity limits control the volume."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Token rates", "Model selection"],
                ["Provisioned throughput", "Right-size commitments"],
                ["Agentic volume", "Per-agent ceilings"],
                ["Retries", "Velocity limits"],
            ],
        ),
        faqs=[
            ("Is Bedrock cost-effective?",
             "Rates vary by model — verify current pricing. Enterprise terms matter."),
            ("Can sipi.bot govern Bedrock spend?",
             "Yes — per-agent caps and category rules."),
        ],
        related=[("sipi.bot vs AWS Bedrock", "/vs/aws-bedrock"), ("Bedrock Agents", "/integrations/aws-bedrock-agents"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026")],
    ),
    dict(
        slug="google-vertex-ai-cost",
        title="Google Vertex AI Cost — Pricing and Agent Spend Control",
        desc="Google Vertex AI cost: Gemini token pricing and GCP usage. How to control agent spend on Vertex.",
        h1="How Much Does Google Vertex AI Cost?",
        lead="Vertex AI bills per token for Gemini plus GCP usage. The platform is powerful; the bill is still rate × volume.",
        sections=[
            ("How Vertex pricing works",
             ["Per-token pricing by Gemini model.",
              "GCP usage (compute, egress) on top.",
              "Verify current pricing on Google's site."]),
            ("The agentic multiplier",
             ["Gemini agents burn tokens at volume.",
              "Context-heavy agent tasks amplify per-call cost."]),
            ("What it really costs",
             ["Token rate × volume + GCP usage. Caps and context trimming control the total."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Token rates", "Model selection"],
                ["Context size", "Trimming + caching"],
                ["Agentic volume", "Per-agent ceilings"],
                ["GCP usage", "Budgets"],
            ],
        ),
        faqs=[
            ("Is Vertex competitive?",
             "Rates vary by model — verify current pricing."),
            ("Can sipi.bot govern Vertex spend?",
             "Yes — per-agent caps and category rules."),
        ],
        related=[("Gemini API cost", "/cost-of/google-gemini-api-cost"), ("sipi.bot vs Google Vertex AI", "/vs/google-vertex-ai"), ("Vertex agents", "/integrations/vertex-ai")],
    ),
]

INTEGRATIONS = [
    dict(
        slug="manus",
        title="Manus Agent Spend Control — sipi.bot Integration",
        desc="Manus is the autonomous general agent. sipi.bot gates what its tasks spend: tools, compute, and payments per run.",
        h1="Spend Control for Manus",
        lead="Manus runs long-horizon autonomous tasks — browsing, executing, and spending across many steps. The guard bounds the run.",
        sections=[
            ("Why Manus runs overspend",
             ["Long-horizon autonomy means hundreds of tool calls per task.",
              "Each step can trigger paid APIs or purchases.",
              "No dollar-level budget inside the agent."]),
            ("How it works",
             ["Call the guard before any spend-capable step: amount, merchant, category → APPROVED, BLOCKED, or FLAGGED."]),
            ("Rules that fit",
             ["Per-task ceiling.",
              "Velocity limit on step loops.",
              "Merchant allowlist for paid tools."]),
        ],
        code=dict(
            title="Guard call",
            lang="typescript",
            body='const res = await fetch("https://sipi.bot/v1/transactions/evaluate", {\n  method: "POST", headers: { "Content-Type": "application/json" },\n  body: JSON.stringify({ amount: 40, merchant: "api.vendor.com", category: "api" }),\n});\nconst { decision } = await res.json();',
            caption="Long-horizon tasks, enforced budgets.",
        ),
        faqs=[
            ("Does this stop Manus autonomy?",
             "No — it gates spend steps; the task continues within budget."),
            ("Can I cap per task?",
             "Yes — per-agent rules per task."),
        ],
        related=[("AutoGPT", "/integrations/autogpt"), ("Agent orchestration", "/glossary/agent-orchestration"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
    dict(
        slug="gpt-engineer",
        title="gpt-engineer Agent Spend Control — sipi.bot Integration",
        desc="gpt-engineer generates codebases autonomously. sipi.bot gates the spend its build loops generate.",
        h1="Spend Control for gpt-engineer",
        lead="gpt-engineer generates entire codebases from prompts — a build loop that can call paid tools and compute. The guard keeps the build on budget.",
        sections=[
            ("Why gpt-engineer builds spend",
             ["Long build loops call models and tools repeatedly.",
              "Generated projects can trigger paid APIs.",
              "Iteration cycles multiply token spend."]),
            ("How it works",
             ["Attach the guard as a tool: before any spend during the build, the agent gets a deterministic decision."]),
            ("Rules that fit",
             ["Per-build ceiling.",
              "Velocity limit on iteration loops.",
              "Merchant allowlist for provisioned services."]),
        ],
        code=dict(
            title="Guard call",
            lang="python",
            body='from sipi_guard import sipi_guard\n\ndecision = sipi_guard(amount=55, merchant="provisioning-api.com", category="compute")\n# APPROVED | BLOCKED | FLAGGED',
            caption="Build loops with budgets.",
        ),
        faqs=[
            ("Does this slow codegen?",
             "No — ~5 ms per check, spend steps only."),
            ("What about the models it uses?",
             "Same rules — category caps apply to inference too."),
        ],
        related=[("OpenAI Codex", "/integrations/openai-codex"), ("Replit Agent", "/integrations/replit-agent"), ("How to stop runaway agents", "/how-to/how-to-stop-runaway-agents")],
    ),
]

LEARN = [
    dict(
        slug="how-do-ai-agents-make-decisions",
        title="How Do AI Agents Make Decisions?",
        desc="Agent decision-making explained: model choices, tool selection, and where the spending decisions happen.",
        h1="How Do AI Agents Make Decisions?",
        lead="Agents decide by combining model reasoning with tool access: what to do next, which tool to call — and whether to spend.",
        sections=[
            ("The decision loop",
             ["The model proposes the next action from context.",
              "The runtime executes tools and returns results.",
              "The loop repeats until the goal is met."]),
            ("Where spending decisions happen",
             ["The model decides to call a tool; the tool may spend.",
              "The model's proposal is a request — the gate is what enforces it."]),
            ("Why enforcement can't be in the prompt",
             ["Prompts can be injected or ignored; rules can't.",
              "A deterministic gate on the money path is the reliable control."]),
        ],
        faqs=[
            ("Do agents decide to spend?",
             "They decide to call tools — spending is a side effect the gate governs."),
            ("Can I trust the model's spending judgment?",
             "Not alone — documented runaways show why the money path needs rules."),
        ],
        related=[("What is an AI agent", "/learn/what-is-an-ai-agent"), ("Tool calling", "/glossary/tool-calling"), ("Spend policy", "/glossary/spend-policy")],
    ),
    dict(
        slug="agent-autonomy-levels",
        title="Agent Autonomy Levels — From Assistants to Autopilots",
        desc="The autonomy spectrum: from tool-assisted chatbots to long-horizon autonomous agents. More autonomy, more spend risk.",
        h1="Agent Autonomy Levels",
        lead="Autonomy is a spectrum — from a chatbot with tools to a long-horizon agent running unattended. Spend risk scales with autonomy.",
        sections=[
            ("The spectrum",
             ["Level 1 — Tool-assisted assistant: human in the loop for every action.",
              "Level 2 — Routed workflow: agent acts within a fixed process.",
              "Level 3 — Autonomous task: agent runs a task end-to-end.",
              "Level 4 — Long-horizon autopilot: agent works for hours or days unattended."]),
            ("The spend implication",
             ["Each level up multiplies tool calls and removes human review.",
              "Level 3–4 agents need deterministic gates — there's no human in the loop."]),
        ],
        faqs=[
            ("What autonomy level needs a firewall?",
             "Any agent that can spend — but gates matter most at levels 3–4."),
            ("Is autonomy the goal?",
             "It's a trade: more autonomy, more control required."),
        ],
        related=[("What is an AI agent", "/learn/what-is-an-ai-agent"), ("Subagent", "/glossary/subagent"), ("How agents spend money", "/learn/how-autonomous-agents-spend-money")],
    ),
]

FAQ = [
    dict(
        slug="do-i-need-a-spend-firewall-if-i-use-cloud-budgets",
        title="Do I Need a Spend Firewall If I Use Cloud Budgets?",
        desc="Cloud budgets alert you after spend; a firewall decides before. The honest answer: they're different jobs — you want both.",
        h1="Do I Need a Spend Firewall If I Use Cloud Budgets?",
        lead="Yes — and it's not either/or. Cloud budgets monitor the cloud bill; a spend firewall decides before the money moves. Different moments, different jobs.",
        sections=[
            ("What cloud budgets do",
             ["Alert when cloud usage crosses thresholds.",
              "Cover the cloud provider's own services."]),
            ("What they can't do",
             ["Stop a transaction before it happens.",
              "Gate spend outside the cloud — vendors, payment rails, tools."]),
            ("What the firewall adds",
             ["Pre-spend decisions across every merchant.",
              "Deterministic rules, approvals, and a decision log."]),
        ],
        table=dict(
            headers=["Job", "Cloud budgets", "Spend firewall"],
            rows=[
                ["Monitor after spend", "Yes", "No"],
                ["Decide before spend", "No", "Yes"],
                ["Cover all merchants", "No", "Yes"],
                ["Approval queue", "No", "Yes"],
            ],
        ),
        faqs=[
            ("Can I keep my cloud budgets?",
             "Absolutely — keep them. The firewall adds the pre-spend layer."),
            ("What's the overlap?",
             "Almost none — they operate at different moments."),
        ],
        related=[("sipi.bot vs AWS Budgets", "/vs/aws-budgets"), ("sipi.bot vs Google Cloud Budgets", "/vs/google-cloud-budgets"), ("Why do AI agents cost so much", "/answers/why-do-ai-agents-cost-so-much/")],
    ),
]

BEST = [
    dict(
        slug="best-ai-cost-tracking-tools",
        title="Best AI Cost Tracking Tools 2026 — Honest List",
        desc="The best AI cost tracking tools: provider dashboards, observability platforms, and the firewall that decides.",
        h1="Best AI Cost Tracking Tools 2026",
        lead="Tracking AI cost means provider dashboards for the bill, observability for the usage, and a decision layer for the control. Here's the honest split.",
        sections=[
            ("Provider dashboards",
             ["OpenAI, Anthropic, Google, AWS usage pages — the source of the bill.",
              "Best for billing, not for control."]),
            ("Observability platforms",
             ["LangSmith, Langfuse, Helicone — usage and cost attribution.",
              "Best for understanding what happened."]),
            ("The decision layer",
             ["A spend firewall — per-agent ceilings, allowlists, velocity limits.",
              "Best for controlling what happens next."]),
        ],
        table=dict(
            headers=["Layer", "Tools", "Job"],
            rows=[
                ["Billing", "Provider dashboards", "The bill"],
                ["Observability", "LangSmith, Langfuse", "What happened"],
                ["Control", "Spend firewall", "What happens next"],
            ],
        ),
        faqs=[
            ("What's the best single tool?",
             "There isn't one — billing, observability, and control are three jobs."),
            ("Where should I start?",
             "Provider dashboards for the bill, then a firewall for the control."),
        ],
        related=[("Best observability tools", "/best/best-ai-agent-observability-tools"), ("How to track AI agent costs", "/answers/how-to-track-ai-agent-costs/"), ("How to monitor AI costs", "/how-to/how-to-monitor-ai-costs")],
    ),
]

BENCHMARKS = [
    dict(
        slug="local-llm-vs-hosted-api-cost",
        title="Local LLM vs Hosted API Cost — The Honest Trade",
        desc="Local vs hosted LLM cost: the TCO comparison that depends on volume, hardware, and your workload. No invented numbers.",
        h1="Local LLM vs Hosted API Cost",
        lead="Local inference trades token bills for hardware, power, and time. Whether it wins depends on volume, hardware, and workload shape — here's the honest framework.",
        sections=[
            ("The local cost",
             ["Hardware (GPU amortization) + power + time.",
              "Cost per token falls at high steady utilization."]),
            ("The hosted cost",
             ["Per-token rates, zero upfront.",
              "Spiky or varied workloads avoid idle hardware."]),
            ("The honest framework",
             ["High steady volume → local can win.",
              "Spiky, varied, or multi-provider → hosted wins.",
              "Model the TCO for YOUR shape — don't trust averages."]),
            ("The control",
             ["Either way, agents need a spend gate — local inference doesn't govern the tools beyond it."]),
        ],
        table=dict(
            headers=["Workload", "Better fit"],
            rows=[
                ["High steady volume", "Local"],
                ["Spiky usage", "Hosted"],
                ["Multi-provider", "Hosted"],
                ["Low volume", "Hosted"],
            ],
        ),
        faqs=[
            ("Is local always cheaper at scale?",
             "Often — but only at high utilization. Model your TCO."),
            ("Does the firewall care where inference runs?",
             "No — it governs the spend surface around either stack."),
        ],
        related=[("Ollama cost", "/cost-of/ollama-cost"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026"), ("LLM API pricing", "/benchmarks/llm-api-pricing-comparison-2026")],
    ),
]

TEMPLATES = [
    dict(
        slug="agent-cost-report-template",
        title="Agent Cost Report Template",
        desc="The monthly agent cost report: spend by agent, category, and vendor, with blocked/flagged patterns and rule changes.",
        h1="Agent Cost Report Template",
        lead="A monthly agent cost report turns the audit log into decisions. Here's the structure that works.",
        sections=[
            ("The report",
             ["1. Total spend vs budget, by agent.",
              "2. Spend by category: inference, data, tools, payments.",
              "3. Top vendors and any new merchants.",
              "4. Blocked: what the firewall stopped.",
              "5. Flagged: approved vs denied — the tuning signal.",
              "6. Rule changes this month and their effect.",
              "7. Next month: one rule change to make."]),
        ],
        faqs=[
            ("How long does it take?",
             "30 minutes a month once the log is the source."),
            ("Who reads it?",
             "The budget owner and finance."),
        ],
        related=[("Weekly spend review", "/templates/weekly-spend-review-template"), ("Agent spend audit guide", "/guides/guide-to-agent-spend-audits"), ("How to track AI agent costs", "/answers/how-to-track-ai-agent-costs/")],
    ),
]

ANSWERS = [
    dict(
        slug="how-to-set-a-budget-for-ai-agents",
        title="How to Set a Budget for AI Agents",
        desc="Set an agent budget in four steps: inventory, ceilings, categories, and review. No spreadsheets required.",
        h1="How to Set a Budget for AI Agents",
        lead="Budgeting agents is like budgeting any team: know what they spend, cap it, and review it. Four steps, one afternoon.",
        sections=[
            ("Step 1 — Inventory",
             ["List spend-capable agents and what they buy."]),
            ("Step 2 — Set ceilings",
             ["Per-agent daily ceilings and per-transaction caps."]),
            ("Step 3 — Split categories",
             ["Separate budgets for inference, data, tools, and payments."]),
            ("Step 4 — Review weekly",
             ["Read the audit log, tune one rule at a time."]),
        ],
        faqs=[
            ("What's a good starting ceiling?",
             "Recent actuals × 1.5, then tighten with the log."),
            ("Do budgets slow agents?",
             "No — ceilings only stop spend beyond the budget."),
        ],
        related=[("Why agents cost so much", "/answers/why-do-ai-agents-cost-so-much/"), ("How to track costs", "/answers/how-to-track-ai-agent-costs/"), ("Budget approval matrix", "/templates/budget-approval-matrix")],
    ),
]

# --- hub metadata -----------------------------------------------------------
