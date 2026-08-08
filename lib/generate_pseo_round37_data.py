"""Round 37 pSEO data — sipi.bot (2026-08-08).

Eighteenth round. Emerging costs (NVIDIA NIM, Meta Llama), adjacent
comparisons (Lakera guardrails, Skyfire agent payments), product FAQ
conversion pages, automotive/nonprofit sectors, content & procurement
use-cases, model routing, key rotation, LLM gateway answer.
13 static pages + 1 blog.

All existing dirs — no plumbing. Content honest.
"""

COST_OF = [
    dict(
        slug="nvidia-nim-cost",
        title="NVIDIA NIM Cost — Pricing and Agent Spend Control",
        desc="NVIDIA NIM cost: microservice inference pricing and how to control agent spend on NIM-hosted models.",
        h1="How Much Does NVIDIA NIM Cost?",
        lead="NVIDIA NIM serves optimized model microservices — priced per token (or self-hosted on your GPUs). For agents, the bill is rate × volume like any API.",
        sections=[
            ("How NIM pricing works",
             ["Per-token pricing for hosted NIM microservices.",
              "Self-host option: your GPUs, your power, your ops.",
              "Verify current pricing on NVIDIA's site."]),
            ("The agentic multiplier",
             ["Fast optimized inference invites more calls.",
              "Retry loops at speed multiply volume."]),
            ("What it really costs",
             ["Rate × volume (hosted) or hardware + power + time (self-hosted).",
              "Velocity limits and per-agent caps control the volume."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Hosted tokens", "Model selection"],
                ["Self-hosted", "Hardware utilization"],
                ["Agentic volume", "Per-agent ceilings"],
                ["Retries", "Velocity limits"],
            ],
        ),
        faqs=[
            ("Is NIM cheaper hosted or self-hosted?",
             "Depends on volume — verify current pricing; model your TCO."),
            ("Can sipi.bot govern NIM spend?",
             "Yes — per-agent caps and category rules apply to any merchant."),
        ],
        related=[("Ollama cost", "/cost-of/ollama-cost"), ("vLLM cost", "/cost-of/vllm-cost"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026")],
    ),
    dict(
        slug="llama-api-cost",
        title="Llama API Cost — Pricing and Agent Spend Control",
        desc="Llama API cost: Meta's open models across providers, per-token pricing, and the self-host alternative.",
        h1="How Much Does the Llama API Cost?",
        lead="Llama models are open weights — you pay whoever serves them: Together, Fireworks, Groq, Bedrock, or your own GPUs. The bill is rate × volume.",
        sections=[
            ("How Llama pricing works",
             ["Per-token pricing by serving provider.",
              "Self-host option: open weights, your hardware.",
              "Verify current pricing on each provider's site."]),
            ("The agentic multiplier",
             ["Llama models are popular for agent workloads — volume follows.",
              "Retry loops multiply per-token charges."]),
            ("What it really costs",
             ["Rate × volume (hosted) or hardware + power + time (self-hosted).",
              "Per-agent caps and velocity limits control the volume."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Provider tokens", "Provider + model selection"],
                ["Self-hosted", "Hardware utilization"],
                ["Agentic volume", "Per-agent ceilings"],
                ["Retries", "Velocity limits"],
            ],
        ),
        faqs=[
            ("Is Llama free?",
             "The weights are open; serving costs money — hosted or self-hosted."),
            ("Can sipi.bot govern Llama spend?",
             "Yes — per-agent caps and category rules apply to any serving merchant."),
        ],
        related=[("Together AI cost", "/cost-of/together-api-cost"), ("Groq API cost", "/cost-of/groq-api-cost"), ("Best LLM gateways", "/best/best-llm-gateways-2026")],
    ),
]

VS = [
    dict(
        slug="lakera",
        name="Lakera Guard",
        title="sipi.bot vs Lakera Guard — Prompt Security vs Spend Firewall",
        desc="Lakera Guard detects prompt injection; sipi.bot gates the spend. Detection vs enforcement — different layers.",
        h1="sipi.bot vs Lakera Guard",
        lead="Lakera Guard is a prompt-injection detection service. sipi.bot is a spend firewall. One detects the attack; the other makes the damage impossible.",
        sections=[
            ("What Lakera does well",
             ["Purpose-built prompt-injection detection at scale.",
              "Strong API-level security layer for LLM apps."]),
            ("Where it falls short",
             ["Detection is probabilistic — a bypass is always possible.",
              "It flags content; it doesn't gate the money path."]),
            ("Where sipi.bot wins",
             ["Deterministic rules on the spend path — they can't be injected.",
              "Caps, allowlists, velocity limits, approvals."]),
            ("When to use which",
             ["Lakera for content-layer detection; sipi.bot for the money layer. Defense in depth."]),
        ],
        table=dict(
            headers=["Dimension", "Lakera Guard", "sipi.bot"],
            rows=[
                ["Role", "Injection detection", "Pre-spend firewall"],
                ["Method", "Probabilistic", "Deterministic"],
                ["Layer", "Content", "Money path"],
                ["Decision", "Blocked/flagged content", "APPROVED / BLOCKED / FLAGGED"],
            ],
        ),
        faqs=[
            ("Are they competitors?",
             "No — detection and enforcement are different layers; use both."),
            ("Can a detected injection still spend?",
             "That's the gap the firewall closes — detection flags it, rules stop it."),
        ],
        related=[("Best AI guardrails", "/best/best-ai-guardrails-tools"), ("The hidden cost of injection", "/blog/the-hidden-cost-of-prompt-injection"), ("Can sipi.bot stop injection", "/faq/can-sipi-bot-stop-prompt-injection")],
    ),
    dict(
        slug="skyfire",
        name="Skyfire",
        title="sipi.bot vs Skyfire — Agent Payments vs Spend Firewall",
        desc="Skyfire gives agents payment rails; sipi.bot gates what they spend. One moves the money, the other decides.",
        h1="sipi.bot vs Skyfire",
        lead="Skyfire is agent-payments infrastructure — rails for machines to pay. sipi.bot is a spend firewall — the decision layer in front of the rails.",
        sections=[
            ("What Skyfire does well",
             ["Payment infrastructure built for agents.",
              "Fast settlement on machine rails."]),
            ("Where it falls short",
             ["It executes payments; it doesn't decide whether an agent may pay.",
              "No per-agent policy or approval queue."]),
            ("Where sipi.bot wins",
             ["Pre-spend decisions: APPROVED, BLOCKED, FLAGGED.",
              "Caps, allowlists, velocity limits, approvals."]),
            ("When to use which",
             ["Skyfire for the rail; sipi.bot for the gate. They compose."]),
        ],
        table=dict(
            headers=["Dimension", "Skyfire", "sipi.bot"],
            rows=[
                ["Role", "Agent payment rails", "Pre-spend firewall"],
                ["When it acts", "Executes payments", "Before payments"],
                ["Decision", "Settle or fail", "APPROVED / BLOCKED / FLAGGED"],
                ["Policy", "Payment features", "Agent spend rules"],
            ],
        ),
        faqs=[
            ("Are they competitors?",
             "No — rails vs gates. sipi.bot decides, Skyfire settles."),
            ("Can they integrate?",
             "Yes — the firewall's decision precedes the rail call."),
        ],
        related=[("x402", "/glossary/x402"), ("AP2", "/glossary/ap2"), ("sipi.bot vs Stripe Payments", "/vs/stripe-payments")],
    ),
]

FAQ = [
    dict(
        slug="does-sipi-bot-work-with-any-llm",
        title="Does sipi.bot Work with Any LLM?",
        desc="Yes — sipi.bot is model-agnostic. It sits on the money path, not the model path.",
        h1="Does sipi.bot Work with Any LLM?",
        lead="Yes. sipi.bot doesn't touch the model layer — it sits on the money path. Any LLM, any framework, any provider.",
        sections=[
            ("Why it's model-agnostic",
             ["The firewall evaluates transactions, not prompts.",
              "HTTP, MCP, and CLI interfaces — no SDK lock-in."]),
            ("What it covers",
             ["All model providers and self-hosted stacks.",
              "All the tools and merchants your agents call — not just inference."]),
        ],
        faqs=[
            ("Does it slow inference?",
             "No — it only evaluates spend actions, ~5 ms."),
            ("Does it care which framework I use?",
             "No — it composes with LangChain, CrewAI, Mastra, and the rest."),
        ],
        related=[("Framework-agnostic FAQ", "/faq/can-sipi-bot-work-with-any-framework"), ("Integrations hub", "/integrations/"), ("How to implement spend controls", "/how-to/how-to-implement-spend-controls")],
    ),
    dict(
        slug="how-fast-is-the-sipi-bot-decision",
        title="How Fast Is the sipi.bot Decision?",
        desc="~5 ms per evaluation: deterministic rules, no model in the path.",
        h1="How Fast Is the sipi.bot Decision?",
        lead="About 5 milliseconds per evaluation — deterministic rules, no model in the path, no network round-trip to an LLM.",
        sections=[
            ("Why it's fast",
             ["Rules are deterministic comparisons, not inference.",
              "The evaluate endpoint is a single lightweight call."]),
            ("What the number means",
             ["Spend actions add ~5 ms — invisible next to API latency.",
              "It's fast enough for payment rails and voice agents."]),
        ],
        faqs=[
            ("Is it faster than a model-based check?",
             "Yes — orders of magnitude. Rules don't reason, they decide."),
            ("Where does latency come from?",
             "Your network to the endpoint — the evaluation itself is microseconds."),
        ],
        related=[("How does the firewall work", "/answers/how-does-a-spend-firewall-work/"), ("Eval report", "/eval-report/"), ("The 5 ms design", "/answers/how-does-a-spend-firewall-work/")],
    ),
]

SECTORS = [
    dict(
        slug="automotive",
        title="AI Spend Control for Automotive | sipi.bot",
        desc="Automotive AI agents: production, supply-chain, and customer-experience bots that spend on data and compute per line.",
        h1="Spend Control for Automotive AI Agents",
        lead="Automakers run agents for production, supply chain, and customer experience — each with paid data and inference at scale.",
        sections=[
            ("Where automotive agents spend",
             ["Supply-chain forecasting APIs per SKU.",
              "Quality and inspection inference per line.",
              "Customer-experience bots at volume.",
              "Market and fleet data feeds."]),
            ("The failure modes",
             ["A forecast loop re-pulling data multiplies per-call charges.",
              "Unknown data vendors bypass procurement.",
              "Line-stop alerts triggering expensive runs."]),
            ("Which rules to start with",
             ["Per-facility daily ceiling.",
              "Merchant allowlist for data vendors.",
              "Velocity limit on forecast loops."]),
        ],
        table=dict(
            headers=["Rule", "Why it matters in automotive"],
            rows=[
                ["Per-facility ceiling", "Each plant has its own budget"],
                ["Merchant allowlist", "Unvetted vendors blocked"],
                ["Velocity limit", "Forecast loops die fast"],
            ],
        ),
        faqs=[
            ("Can I budget per plant?",
             "Yes — per-agent rules per facility."),
            ("Does it slow production systems?",
             "No — ~5 ms per check."),
        ],
        related=[("Manufacturing sector", "/sectors/manufacturing"), ("Supply chain", "/use-cases/procurement-agents"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
    dict(
        slug="nonprofits",
        title="AI Spend Control for Nonprofits | sipi.bot",
        desc="Nonprofit AI agents: donor comms, grant writing, and mission data — budgeted like the donations they depend on.",
        h1="Spend Control for Nonprofit AI Agents",
        lead="Nonprofits run agents for donor communication, grant writing, and mission analysis — every dollar matters, and agent spend is a new line to guard.",
        sections=[
            ("Where nonprofit agents spend",
             ["Donor-communication inference at volume.",
              "Grant-writing and research tools.",
              "Mission-data analysis APIs.",
              "Volunteer coordination bots."]),
            ("The failure modes",
             ["A comms retry loop multiplies inference.",
              "Unknown tool vendors bypass procurement.",
              "No budget visibility for the AI line."]),
            ("Which rules to start with",
             ["Per-campaign daily ceiling.",
              "Merchant allowlist for tools.",
              "Monthly spend report for the board."]),
        ],
        table=dict(
            headers=["Nonprofit spend", "Control"],
            rows=[
                ["Donor comms", "Per-campaign ceiling"],
                ["Grant tools", "Merchant allowlist"],
                ["Mission data", "Category budget"],
            ],
        ),
        faqs=[
            ("Is there a nonprofit discount?",
             "Check current pricing — the flat rate is deliberately small."),
            ("Does it slow donor outreach?",
             "No — ~5 ms per check."),
        ],
        related=[("Marketing sector", "/sectors/marketing"), ("Email agents", "/use-cases/email-agents"), ("How to set a budget", "/answers/how-to-set-a-budget-for-ai-agents/")],
    ),
]

USE_CASES = [
    dict(
        slug="content-creation-agents",
        title="Content Creation Agent Spend Control | sipi.bot",
        desc="Content agents: drafting, SEO, and localization at scale — cap the inference and tool spend per pipeline.",
        h1="Spend Control for Content Creation Agents",
        lead="Content agents draft, optimize, and localize at scale — inference per piece, tools per pipeline. Volume is the point; the budget is the guard.",
        sections=[
            ("Where content agents spend",
             ["Drafting and rewriting inference per piece.",
              "SEO and research tools per query.",
              "Localization APIs per language.",
              "Image and media generation APIs."]),
            ("The failure modes",
             ["A regeneration loop multiplies inference.",
              "Unknown tool vendors bypass procurement.",
              "Campaign spikes hit overage tiers."]),
            ("Which rules to start with",
             ["Per-pipeline daily ceiling.",
              "Category rule: text vs image generation.",
              "Merchant allowlist for tools."]),
        ],
        table=dict(
            headers=["Content spend", "Control"],
            rows=[
                ["Drafting", "Per-pipeline ceiling"],
                ["SEO tools", "Merchant allowlist"],
                ["Localization", "Category budget"],
                ["Image APIs", "Per-asset cap"],
            ],
        ),
        faqs=[
            ("Can I budget per campaign?",
             "Yes — per-agent rules per pipeline or campaign."),
            ("Does it slow content production?",
             "No — ~5 ms per check."),
        ],
        related=[("Marketing sector", "/sectors/marketing"), ("Media sector", "/sectors/media-publishing"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs")],
    ),
    dict(
        slug="procurement-agents",
        title="Procurement Agent Spend Control | sipi.bot",
        desc="Procurement agents: sourcing, vendor research, and purchasing — the agents that buy things need the strongest budgets.",
        h1="Spend Control for Procurement Agents",
        lead="Procurement agents source vendors, compare prices, and buy — they're the agents literally built to spend. The strongest budgets belong to them.",
        sections=[
            ("Where procurement agents spend",
             ["Vendor-research data per query.",
              "Price-comparison inference per SKU.",
              "Purchasing actions on payment rails.",
              "Contract-analysis tools."]),
            ("The failure modes",
             ["An unvetted vendor purchased by an agent.",
              "A comparison loop multiplying data charges.",
              "No per-requisition budget."]),
            ("Which rules to start with",
             ["Per-requisition ceiling.",
              "Merchant allowlist: ONLY approved vendors payable.",
              "Approval threshold for new vendors.",
              "Audit trail for every purchase."]),
        ],
        table=dict(
            headers=["Procurement spend", "Control"],
            rows=[
                ["Vendor research", "Category budget"],
                ["Purchases", "Per-requisition cap"],
                ["New vendors", "Approval threshold"],
                ["Payments", "Merchant allowlist"],
            ],
        ),
        faqs=[
            ("Can an agent really buy things?",
             "With payment capability, yes — that's exactly why the allowlist matters most here."),
            ("What's the strongest control?",
             "The allowlist — unapproved vendors are simply not payable."),
        ],
        related=[("Procurement teams", "/for/procurement-teams"), ("Merchant allowlist", "/glossary/merchant-allowlist"), ("Agentic payment", "/glossary/agentic-payment")],
    ),
]

GLOSSARY = [
    dict(
        slug="model-routing",
        term="Model routing",
        title="What is Model Routing? | sipi.bot Glossary",
        desc="Model routing sends each request to the best model — the cost lever that pairs with spend control.",
        h1="What is Model Routing?",
        lead="Model routing sends each request to the right model — cheap for simple work, powerful for hard work. The biggest lever on the rate side of the cost equation.",
        sections=[
            ("How it works",
             ["A gateway or router picks the model per request — by task, cost, or quality target."]),
            ("Why it matters for cost",
             ["Routing simple work to small models cuts the rate dramatically.",
              "Gateways (LiteLLM, One API) make it configurable."]),
            ("The honest pairing",
             ["Routing cuts the rate; the firewall governs the volume. Both."]),
        ],
        faqs=[
            ("Is routing the same as a gateway?",
             "Routing is a gateway's core job — plus key management and caching."),
            ("Does routing replace budgets?",
             "No — it cuts rate; caps bound volume."),
        ],
        related=[("Best LLM gateways", "/best/best-llm-gateways-2026"), ("How to choose an LLM provider", "/how-to/how-to-choose-an-llm-provider"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs")],
    ),
]

TEMPLATES = [
    dict(
        slug="agent-key-rotation-policy",
        title="Agent API Key Rotation Policy Template",
        desc="The rotation policy for agent keys: cadence, scoping, and the kill-switch path for compromised keys.",
        h1="Agent API Key Rotation Policy",
        lead="Keys age into risk. Rotation on a schedule — with scoping and a compromise path — keeps credentials fresh.",
        sections=[
            ("The policy",
             ["1. Cadence: keys rotate every 90 days (30 for high-risk agents).",
              "2. Scoping: one key per agent, minimum permissions.",
              "3. Rotation process: issue new key, migrate, revoke old, verify in the log.",
              "4. Compromise path: kill switch on the agent, revoke key, audit the window.",
              "5. Inventory: a quarterly list of every key and its agent."]),
        ],
        faqs=[
            ("How often is enough?",
             "90 days standard; 30 for anything touching payments."),
            ("What's the compromise first step?",
             "Kill the agent's spending, then revoke the key — in that order."),
        ],
        related=[("Red flags in API keys", "/redflags/red-flags-in-api-keys"), ("API key compromise scenario", "/scenarios/api-key-compromise-scenario"), ("Agent identity", "/glossary/agent-identity")],
    ),
]

ANSWERS = [
    dict(
        slug="what-is-an-llm-gateway",
        title="What Is an LLM Gateway?",
        desc="An LLM gateway routes, secures, and observes model traffic — and why it's not a spend firewall.",
        h1="What Is an LLM Gateway?",
        lead="An LLM gateway sits between your apps and model providers: routing, key management, caching, and observability. It manages traffic — not money.",
        sections=[
            ("What a gateway does",
             ["Routes requests to the best model or provider.",
              "Manages API keys centrally.",
              "Adds caching, fallbacks, and usage analytics."]),
            ("What it doesn't do",
             ["It doesn't decide whether an agent may pay a merchant.",
              "Rate limits stop requests — not purchases."]),
            ("Gateway + firewall",
             ["Gateway for the model layer, firewall for the money layer. They compose."]),
        ],
        faqs=[
            ("Is a gateway the same as a firewall?",
             "No — one manages model traffic, the other gates agent spend."),
            ("Which do I need first?",
             "The gateway if you're multi-provider; the firewall if your agents can spend. Usually both."),
        ],
        related=[("Best LLM gateways", "/best/best-llm-gateways-2026"), ("sipi.bot vs One API", "/vs/one-api"), ("How does a spend firewall work", "/answers/how-does-a-spend-firewall-work/")],
    ),
]

# --- hub metadata -----------------------------------------------------------
