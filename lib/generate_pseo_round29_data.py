"""Round 29 pSEO data — sipi.bot (2026-08-08).

Tenth round. 19 static pages + 2 blog:
  integrations +4: cline, roo-code, zapier, make
  cost-of +2: groq-api-cost, cohere-api-cost
  for +2: customer-success-teams, legal-teams
  templates +3: vendor-offboarding-policy, agent-spend-policy-one-pager,
                mcp-server-vetting-template
  glossary +3: agent-orchestration, agentic-workflow, budget-alert
  how-to +2: how-to-vet-mcp-servers, how-to-handle-a-flagged-transaction
  best +1: best-agent-incident-response-tools
  benchmarks +1: agent-failure-cost-by-type
  pricing-questions +1: is-sipi-bot-soc-2-compliant (honest — no certification claims)
  blog +2 (via lib/generate_content.py)

All existing dirs — no plumbing. Content honest; cost figures approximate
with verify-current caveats; SOC 2 page explicitly declines certification
claims.
"""

INTEGRATIONS = [
    dict(
        slug="cline",
        title="Cline Agent Spend Control — sipi.bot Integration",
        desc="Give Cline coding agents a real spending policy. The guard tool returns APPROVED, BLOCKED, or FLAGGED before any purchase.",
        h1="Spend Control for Cline",
        lead="Cline is the open-source coding agent that runs in your editor — autonomous, tool-hungry, and free to spend. A guard makes the budget real.",
        sections=[
            ("Why Cline agents overspend",
             ["Autonomous plan-act loops call tools thousands of times.",
              "Paid tools and compute purchases happen mid-task.",
              "No built-in dollar-level budget."]),
            ("How it works",
             ["Add sipi.bot as a tool (or call the HTTP API from a custom tool). Before any spend, the agent gets a deterministic decision."]),
            ("Rules that fit Cline workflows",
             ["Per-transaction cap on compute and API credits.",
              "Merchant allowlist for known vendors.",
              "Velocity limit so retry loops die fast."]),
        ],
        code=dict(
            title="Guard tool",
            lang="typescript",
            body='const res = await fetch("https://sipi.bot/v1/transactions/evaluate", {\n  method: "POST", headers: { "Content-Type": "application/json" },\n  body: JSON.stringify({ amount: 90, merchant: "compute-vendor.com", category: "compute" }),\n});\nconst { decision } = await res.json();',
            caption="One call, deterministic policy.",
        ),
        faqs=[
            ("Does this slow Cline?",
             "No — ~5 ms per check, spend actions only."),
            ("Is Cline supported officially?",
             "sipi.bot is HTTP/MCP — any tool-calling agent works."),
        ],
        related=[("Roo Code", "/integrations/roo-code"), ("Claude Code", "/integrations/claude-code"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
    dict(
        slug="roo-code",
        title="Roo Code Agent Spend Control — sipi.bot Integration",
        desc="Cap what Roo Code agents spend: compute, APIs, and payments during autonomous coding sessions.",
        h1="Spend Control for Roo Code",
        lead="Roo Code (formerly Roo Cline) runs autonomous coding agents in the editor — capable of buying tools and compute mid-task. The guard keeps the budget.",
        sections=[
            ("Why Roo Code agents overspend",
             ["Long autonomous sessions call paid tools repeatedly.",
              "Task-planning loops can trigger purchases.",
              "No built-in dollar-level budget."]),
            ("How it works",
             ["Attach the guard as a tool. Before any spend, the agent asks sipi.bot and gets APPROVED, BLOCKED, or FLAGGED."]),
            ("Rules that fit Roo Code workflows",
             ["Per-session or per-agent daily ceiling.",
              "Merchant allowlist for paid tools.",
              "Velocity limit on retry loops."]),
        ],
        code=dict(
            title="Guard call",
            lang="typescript",
            body='const res = await fetch("https://sipi.bot/v1/transactions/evaluate", {\n  method: "POST", headers: { "Content-Type": "application/json" },\n  body: JSON.stringify({ amount: 30, merchant: "api.provider.com", category: "api" }),\n});\nconst { decision } = await res.json();',
            caption="One tool, enforced budget.",
        ),
        faqs=[
            ("Can I cap per project?",
             "Yes — per-agent rules per project or workspace."),
            ("Is the decision model-free?",
             "Yes — deterministic rules, ~5 ms."),
        ],
        related=[("Cline", "/integrations/cline"), ("Cursor", "/integrations/cursor"), ("How to stop runaway agents", "/how-to/how-to-stop-runaway-agents")],
    ),
    dict(
        slug="zapier",
        title="Zapier Agents Spend Control — sipi.bot Integration",
        desc="Cap what Zapier agents and automations spend: paid apps, AI steps, and API calls per run.",
        h1="Spend Control for Zapier",
        lead="Zapier automations run on schedules and triggers — and AI steps bill per run. A guard node before paid steps keeps the automation honest.",
        sections=[
            ("Why Zapier workflows overspend",
             ["AI steps bill per run — an hourly workflow is 720 runs a day.",
              "Paid app actions multiply across automations.",
              "Retry loops re-run paid steps."]),
            ("How it works",
             ["Add an HTTP Request step to sipi.bot before paid actions; branch on APPROVED, BLOCKED, or FLAGGED."]),
            ("Rules that fit Zapier workloads",
             ["Per-automation daily ceiling.",
              "Category rule: AI steps vs app actions.",
              "Merchant allowlist for paid apps."]),
        ],
        code=dict(
            title="Branch logic",
            lang="text",
            body="HTTP Request -> https://sipi.bot/v1/transactions/evaluate\nAPPROVED -> continue to paid action\nBLOCKED  -> stop + log\nFLAGGED  -> pause for human",
            caption="Three branches, one deterministic decision.",
        ),
        faqs=[
            ("Does this add latency to Zaps?",
             "~5 ms per check — negligible next to app-action latency."),
            ("Can I cap per workflow?",
             "Yes — per-agent rules per automation."),
        ],
        related=[("Make", "/integrations/make"), ("n8n", "/integrations/n8n"), ("How to implement spend controls", "/how-to/how-to-implement-spend-controls")],
    ),
    dict(
        slug="make",
        title="Make (Integromat) Agent Spend Control — sipi.bot Integration",
        desc="Cap what Make scenarios spend: operations, data, and AI modules per run.",
        h1="Spend Control for Make",
        lead="Make scenarios run operations and AI modules per execution — and executions are billable. A guard module before costly steps.",
        sections=[
            ("Why Make scenarios overspend",
             ["Operations and data modules bill per execution.",
              "AI modules add per-run LLM cost.",
              "Retries and loops re-run billable modules."]),
            ("How it works",
             ["Insert an HTTP module calling sipi.bot before costly steps; branch on the decision."]),
            ("Rules that fit Make workloads",
             ["Per-scenario daily ceiling.",
              "Velocity limit on retries.",
              "Category rule: operations vs AI modules."]),
        ],
        code=dict(
            title="Module",
            lang="text",
            body="HTTP module -> evaluate(amount, merchant, category)\nAPPROVED -> continue | BLOCKED -> stop | FLAGGED -> notify",
            caption="Gate the modules that spend.",
        ),
        faqs=[
            ("Does sipi.bot run inside Make?",
             "It's external — Make calls it over HTTP like any API."),
            ("Can I cap per scenario?",
             "Yes — per-agent rules per scenario."),
        ],
        related=[("Zapier", "/integrations/zapier"), ("n8n", "/integrations/n8n"), ("Workflow automation", "/for/devops-automation")],
    ),
]

COST_OF = [
    dict(
        slug="groq-api-cost",
        title="Groq API Cost — Pricing and Agent Spend Control",
        desc="Groq API cost: token pricing, the speed premium, and how to control agent spend on Groq models.",
        h1="How Much Does the Groq API Cost?",
        lead="Groq is known for speed — LPU inference with per-token pricing. For agents, speed at volume is still a bill.",
        sections=[
            ("How Groq pricing works",
             ["Per-token pricing by model, with input and output rates.",
              "Speed is the selling point; the bill is rate × volume like any API.",
              "Verify current pricing on Groq's site."]),
            ("The hidden cost",
             ["Fast inference invites more calls — agents loop faster.",
              "Retry loops at LPU speed multiply volume quickly."]),
            ("What it really costs",
             ["Model rate × volume. Velocity limits and per-agent caps control the volume."]),
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
            ("Is Groq cheaper than other APIs?",
             "Rates vary by model — verify current pricing. Total cost is rate × volume."),
            ("Can sipi.bot control Groq spend?",
             "Yes — category rules and per-agent caps apply to any API merchant."),
        ],
        related=[("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs"), ("LLM API pricing", "/benchmarks/llm-api-pricing-comparison-2026")],
    ),
    dict(
        slug="cohere-api-cost",
        title="Cohere API Cost — Pricing and Agent Spend Control",
        desc="Cohere API cost: token pricing, enterprise features, and how to control agent spend on Cohere models.",
        h1="How Much Does the Cohere API Cost?",
        lead="Cohere's API is per-token with an enterprise focus — RAG, classification, and generation models. The bill follows volume.",
        sections=[
            ("How Cohere pricing works",
             ["Per-token pricing by model family.",
              "Enterprise tiers add support and features.",
              "Verify current pricing on Cohere's site."]),
            ("The hidden cost",
             ["RAG-heavy agent workloads send large contexts per call.",
              "Retry loops and fan-out multiply volume."]),
            ("What it really costs",
             ["Model rate × volume × context. Caps and context trimming control all three."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Token rates", "Model selection"],
                ["RAG contexts", "Context caps + trimming"],
                ["Retry loops", "Velocity limit"],
            ],
        ),
        faqs=[
            ("Is Cohere competitive on price?",
             "Rates vary by model — verify current pricing."),
            ("Can sipi.bot govern Cohere spend?",
             "Yes — per-agent caps and category rules."),
        ],
        related=[("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026"), ("RAG pipelines", "/for/data-pipelines"), ("How to monitor AI costs", "/how-to/how-to-monitor-ai-costs")],
    ),
]

FOR = [
    dict(
        slug="customer-success-teams",
        title="AI Agent Spend Controls for Customer Success | sipi.bot",
        desc="Customer success teams: cap what support and health-score agents spend per customer and per cohort.",
        h1="Agent Spend Controls for Customer Success",
        lead="CS teams run agents for support triage, health scoring, and onboarding — each with paid API calls per customer. Per-cohort budgets keep the margin.",
        sections=[
            ("Where CS agents spend",
             ["Support triage inference per ticket.",
              "Health-scoring data pulls per account.",
              "Onboarding automation per customer.",
              "Email and comms APIs per touch."]),
            ("The failure modes",
             ["A triage loop re-running tickets multiplies inference.",
              "Health-score pulls looping against paid data APIs.",
              "Unknown vendors bypass procurement."]),
            ("Which rules to start with",
             ["Per-team daily ceiling.",
              "Category rule: triage vs data vs comms.",
              "Merchant allowlist for data vendors."]),
        ],
        table=dict(
            headers=["CS spend", "Control"],
            rows=[
                ["Triage inference", "Daily ceiling"],
                ["Health-score data", "Category budget"],
                ["Onboarding", "Per-customer cap"],
                ["Comms APIs", "Merchant allowlist"],
            ],
        ),
        faqs=[
            ("Can I budget per customer tier?",
             "Yes — per-agent rules per tier or cohort."),
            ("Does it slow support?",
             "No — ~5 ms per check."),
        ],
        related=[("Customer support bots", "/use-cases/customer-support-bots"), ("Customer onboarding agents", "/use-cases/customer-onboarding-agents"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
    dict(
        slug="legal-teams",
        title="AI Agent Spend Controls for Legal Teams | sipi.bot",
        desc="Legal teams: cap what research, review, and contract agents spend per matter — with a defensible audit trail.",
        h1="Agent Spend Controls for Legal Teams",
        lead="Legal agents review documents, research case law, and analyze contracts — each with paid data and inference per matter. Per-matter budgets.",
        sections=[
            ("Where legal agents spend",
             ["Document review inference per page.",
              "Case-law and paywalled data per query.",
              "Contract analysis APIs per document.",
              "E-discovery pipelines per GB."]),
            ("The failure modes",
             ["A review re-run after a prompt change multiplies inference.",
              "Unknown research vendors bypass procurement.",
              "No per-matter budget."]),
            ("Which rules to start with",
             ["Per-matter budget.",
              "Merchant allowlist for approved databases.",
              "Category rule: review vs research vs discovery."]),
        ],
        table=dict(
            headers=["Legal spend", "Control"],
            rows=[
                ["Review inference", "Per-matter ceiling"],
                ["Research data", "Merchant allowlist"],
                ["Contract APIs", "Category budget"],
                ["E-discovery", "Per-matter cap"],
            ],
        ),
        faqs=[
            ("Can I enforce client budgets?",
             "Yes — per-agent rules map to per-matter ceilings."),
            ("Is the audit trail defensible?",
             "Every decision is logged with the rule that fired — an evidence source, not a certification."),
        ],
        related=[("Legal sector", "/sectors/legal"), ("Compliance officers", "/for/compliance-officers"), ("Agent audit trail", "/glossary/agent-audit-trail")],
    ),
]

TEMPLATES = [
    dict(
        slug="vendor-offboarding-policy",
        title="AI Vendor Offboarding Policy Template",
        desc="A template for removing vendors from your agent allowlist: triggers, review, and revocation.",
        h1="AI Vendor Offboarding Policy",
        lead="Vendors leave the allowlist as deliberately as they enter it. This policy makes offboarding explicit.",
        sections=[
            ("The policy",
             ["1. Triggers — underuse, price change, risk finding, contract end.",
              "2. Review — procurement confirms removal and what replaces it.",
              "3. Revoke — vendor removed from the allowlist; new purchases BLOCKED.",
              "4. Migrate — agents pointed at approved alternatives.",
              "5. Verify — audit log confirms no further spend."]),
            ("Enforcement",
             ["Removal from the allowlist is the enforcement — unknown merchants are blocked by default."]),
        ],
        faqs=[
            ("How fast can I cut a vendor?",
             "Instantly — remove it from the allowlist and the next purchase is blocked."),
            ("What about existing subscriptions?",
             "Cancel the subscription separately; the allowlist stops new spend today."),
        ],
        related=[("Vendor onboarding policy", "/templates/vendor-onboarding-policy"), ("Merchant allowlist template", "/templates/merchant-allowlist-template"), ("Procurement teams", "/for/procurement-teams")],
    ),
    dict(
        slug="agent-spend-policy-one-pager",
        title="Agent Spend Policy One-Pager Template",
        desc="The one-page agent spend policy: budget, vendors, approvals, and review — short enough to actually be read.",
        h1="Agent Spend Policy One-Pager",
        lead="A policy nobody reads isn't a policy. This one-pager fits on a page and maps to real rules.",
        sections=[
            ("The one-pager",
             ["Budget: daily ceiling [$], per-transaction cap [$].",
              "Vendors: only allowlisted merchants may be paid.",
              "Approvals: purchases over [$] wait for [OWNER].",
              "Hours: overnight spend is flagged for review.",
              "Review: the audit log is reviewed monthly by [OWNER]."]),
            ("Why it works",
             ["Every line maps to a rule — the policy and the enforcement are the same document."]),
        ],
        faqs=[
            ("Is one page enough?",
             "For enforcement, yes — the rules carry the weight, the page carries the intent."),
            ("Who signs it?",
             "The budget owner, reviewed quarterly."),
        ],
        related=[("Agent spend policy template", "/templates/agent-spend-policy-template"), ("How to create a spend policy", "/how-to/how-to-create-a-spend-policy"), ("Spend policy", "/glossary/spend-policy")],
    ),
    dict(
        slug="mcp-server-vetting-template",
        title="MCP Server Vetting Template",
        desc="A checklist for vetting MCP servers before your agents trust them: source, permissions, paid calls, and credentials.",
        h1="MCP Server Vetting Template",
        lead="Every MCP server is third-party code with tool access. Vetting is the dependency review for the agent era.",
        sections=[
            ("The template",
             ["1. Source: repo, author, stars, maintenance?",
              "2. Permissions: does it ask for more than its job needs?",
              "3. Paid calls: does any tool hit a paid endpoint?",
              "4. Network: where does it send data?",
              "5. Credentials: does it store keys it shouldn't?",
              "6. Spend risk: worst-case monthly if it loops?",
              "7. Decision: APPROVE (allowlist) / CONDITIONAL (caps) / REJECT."]),
        ],
        faqs=[
            ("How deep should vetting go?",
             "Proportional to access — a filesystem server gets more scrutiny than a weather tool."),
            ("What happens to rejected servers?",
             "They're simply not allowed to spend — the allowlist is the enforcement."),
        ],
        related=[("Red flags in MCP servers", "/redflags/red-flags-in-mcp-servers"), ("How to vet MCP servers", "/how-to/how-to-vet-mcp-servers"), ("MCP integration", "/integrations/mcp")],
    ),
]

GLOSSARY = [
    dict(
        slug="agent-orchestration",
        term="Agent orchestration",
        title="What is Agent Orchestration? | sipi.bot Glossary",
        desc="Agent orchestration: coordinating multiple agents toward a goal — and the compounding spend risk it creates.",
        h1="What is Agent Orchestration?",
        lead="Agent orchestration is coordinating multiple agents — planning, delegating, and executing subtasks — toward a single goal.",
        sections=[
            ("How it works",
             ["A coordinator decomposes a goal and delegates to specialized agents.",
              "Agents run in parallel, share context, and report back."]),
            ("Why it changes spend",
             ["Orchestration multiplies spend: N agents × their tool calls and retries.",
              "No single agent looks expensive; the fleet does."]),
            ("The control",
             ["Shared ceilings and velocity limits across the orchestrated fleet stop compounding."]),
        ],
        faqs=[
            ("Is orchestration worth the complexity?",
             "For complex goals, yes — but budget the fleet, not the agents."),
            ("What's the biggest risk?",
             "Compounding — many agents retrying the same failure in parallel."),
        ],
        related=[("Subagent", "/glossary/subagent"), ("Multi-agent budgets", "/use-cases/multi-agent-budgets"), ("Multi-agent compounding", "/scenarios/multi-agent-compounding-scenario")],
    ),
    dict(
        slug="agentic-workflow",
        term="Agentic workflow",
        title="What is an Agentic Workflow? | sipi.bot Glossary",
        desc="An agentic workflow is a process where agents make decisions at each step — including spending decisions.",
        h1="What is an Agentic Workflow?",
        lead="An agentic workflow is a process in which an AI agent makes decisions at each step — choosing tools, routes, and actions without step-by-step human direction.",
        sections=[
            ("How it differs from automation",
             ["Automation follows a fixed path; an agentic workflow decides the path.",
              "That decision-making includes spending decisions."]),
            ("Why it matters for cost",
             ["The agent chooses which tools to call — and each choice can be a purchase.",
              "A workflow that 'decides' 100 times can spend 100 times."]),
            ("The control",
             ["Budget the decisions: caps, allowlists, and approvals apply at each step."]),
        ],
        faqs=[
            ("Is every agentic workflow a spend risk?",
             "Only if the agent can spend — but tool access makes that most workflows."),
            ("How do you govern one?",
             "The same way you govern any side-effecting system: external gates on the money path."),
        ],
        related=[("Agentic AI", "/glossary/agentic-ai"), ("How autonomous agents spend", "/learn/how-autonomous-agents-spend-money"), ("Spend policy", "/glossary/spend-policy")],
    ),
    dict(
        slug="budget-alert",
        term="Budget alert",
        title="What is a Budget Alert? | sipi.bot Glossary",
        desc="A budget alert fires when spend crosses a threshold — the monitoring companion to enforced ceilings.",
        h1="What is a Budget Alert?",
        lead="A budget alert notifies you when agent spend crosses a configured threshold — the monitoring layer on top of enforced ceilings.",
        sections=[
            ("How it works",
             ["Thresholds per agent, category, or fleet.",
              "Alerts fire on approach and breach."]),
            ("Alert vs ceiling",
             ["An alert tells you; a ceiling stops it.",
              "Run both: alerts for awareness, ceilings for enforcement."]),
        ],
        faqs=[
            ("What thresholds should I set?",
             "80% of the ceiling (approach) and 100% (breach)."),
            ("Do alerts replace ceilings?",
             "No — alerts inform, ceilings enforce. Both."),
        ],
        related=[("Daily budget alert template", "/templates/daily-budget-alert"), ("How to monitor AI costs", "/how-to/how-to-monitor-ai-costs"), ("Daily spend ceiling", "/glossary/daily-spend-ceiling")],
    ),
]

HOW_TO = [
    dict(
        slug="how-to-vet-mcp-servers",
        title="How to Vet MCP Servers",
        desc="Step-by-step MCP server vetting: source review, permissions, paid calls, and the spend gate.",
        h1="How to Vet MCP Servers",
        lead="MCP servers are dependencies with tool access. Vetting them is the security review your agents deserve.",
        sections=[
            ("Step 1 — Review the source",
             ["Check the repo, author, stars, and maintenance. Pin the version."]),
            ("Step 2 — Inspect permissions",
             ["Does it ask for more access than its job needs? Least privilege."]),
            ("Step 3 — Find the paid calls",
             ["Any tool hitting a paid endpoint? That's a spend surface."]),
            ("Step 4 — Gate the spend",
             ["Add approved servers to the allowlist with caps; everything else is blocked by default."]),
        ],
        code=dict(
            title="The decision",
            lang="text",
            body="APPROVE -> allowlist + caps\nCONDITIONAL -> allowlist + reduced caps\nREJECT -> not allowlisted (blocked)",
            caption="Vetting becomes enforcement.",
        ),
        faqs=[
            ("How long does vetting take?",
             "Minutes per server with the template — most of it is reading the paid calls."),
            ("What if a server needs review later?",
             "The approval threshold catches new merchants; the audit log records everything."),
        ],
        related=[("MCP server vetting template", "/templates/mcp-server-vetting-template"), ("Red flags in MCP servers", "/redflags/red-flags-in-mcp-servers"), ("MCP integration", "/integrations/mcp")],
    ),
    dict(
        slug="how-to-handle-a-flagged-transaction",
        title="How to Handle a Flagged Transaction",
        desc="The review workflow for FLAGGED agent transactions: triage, approve, deny, and tune.",
        h1="How to Handle a Flagged Transaction",
        lead="A flagged transaction is the firewall asking a question. Here's how to answer it well.",
        sections=[
            ("Step 1 — Read the context",
             ["Amount, merchant, category, and the rule that fired — all in the queue."]),
            ("Step 2 — Decide",
             ["Approve if legitimate; deny if not. Both are logged."]),
            ("Step 3 — Tune",
             ["Patterns of approval → raise the threshold. Patterns of denial → the agent is trying the wrong things."]),
        ],
        code=dict(
            title="The loop",
            lang="text",
            body="FLAG -> review -> approve/deny -> log -> tune threshold\nReview target: minutes, not days.",
            caption="The queue is designed to be fast.",
        ),
        faqs=[
            ("Who should review flags?",
             "The budget owner — the same person who sets the thresholds."),
            ("What if I'm unsure?",
             "Deny by default — the agent can retry with a different approach."),
        ],
        related=[("Approval queue", "/glossary/approval-queue"), ("False-positive scenario", "/scenarios/legit-workflow-false-positive-scenario"), ("Approval workflow template", "/templates/approval-workflow")],
    ),
]

BEST = [
    dict(
        slug="best-agent-incident-response-tools",
        title="Best Agent Incident Response Tools 2026 — Honest List",
        desc="The best tools for responding to agent incidents: the incident database, runbooks, and the firewall that prevents the next one.",
        h1="Best Agent Incident Response Tools 2026",
        lead="Agent incidents are new — the response tooling is young. Here's the honest shortlist, from documentation to prevention.",
        sections=[
            ("Documentation",
             ["The AI Agent Incident Database — sourced records, CC BY 4.0, machine-readable.",
              "Incident report and runbook templates for structured post-mortems."]),
            ("Monitoring",
             ["Observability platforms (LangSmith, Langfuse) and the audit log for what happened."]),
            ("Prevention",
             ["The firewall — because the best incident response is the one that never happens."]),
        ],
        table=dict(
            headers=["Tool", "Job", "Acts"],
            rows=[
                ["Incident database", "Reference patterns", "After the fact"],
                ["Runbook templates", "Structure response", "During"],
                ["Observability", "Show what happened", "After"],
                ["sipi.bot", "Prevent the next one", "Before"],
            ],
        ),
        faqs=[
            ("What's the most important response tool?",
             "The audit log — it's how you know what happened and what rule was missing."),
            ("Do I need a runbook?",
             "Yes — a structured template turns chaos into a fix."),
        ],
        related=[("Agent incident report", "/templates/agent-incident-report"), ("Incident database", "/incidents/"), ("Agent spend audits", "/guides/guide-to-agent-spend-audits")],
    ),
]

BENCHMARKS = [
    dict(
        slug="agent-failure-cost-by-type",
        title="Agent Failure Cost by Type — From the Incident Database",
        desc="What different agent failure types cost: retry loops, unknown vendors, injection, and deletion. Sourced from the incident database.",
        h1="Agent Failure Cost by Type",
        lead="Different failure modes carry different price tags. The incident database shows the shapes — and the rule that stops each one.",
        sections=[
            ("The failure types",
             ["Retry loops — the most common; cost = single op × retries.",
              "Unknown-vendor spend — procurement bypass, one unvetted merchant.",
              "Prompt-injection spend — instructed purchases the operator never wanted.",
              "Data deletion — the expensive non-monetary failure."]),
            ("What the database shows",
             ["Documented runaways range from hundreds to millions of dollars.",
              "The patterns repeat — which means the rules are known."]),
            ("The rule per type",
             ["Retry loop → velocity limit. Unknown vendor → allowlist. Injection spend → deterministic rules. Deletion → approval on destructive actions."]),
        ],
        table=dict(
            headers=["Failure type", "Cost shape", "Rule"],
            rows=[
                ["Retry loop", "Single op × retries", "Velocity limit"],
                ["Unknown vendor", "One unvetted merchant", "Merchant allowlist"],
                ["Injection spend", "Instructed purchases", "Deterministic rules"],
                ["Data deletion", "Non-monetary", "Approval on destructive ops"],
            ],
        ),
        faqs=[
            ("Which failure type is most expensive?",
             "The largest documented losses are trading-agent events; the most common is the retry loop."),
            ("Where's the data from?",
             "The public incident database — sourced records."),
        ],
        related=[("Runaway cost average", "/benchmarks/agent-runaway-cost-average"), ("Incident database", "/incidents/"), ("Retry-loop cost patterns", "/benchmarks/agent-retry-loop-cost-patterns")],
    ),
]

PRICING_QUESTIONS = [
    dict(
        slug="is-sipi-bot-soc-2-compliant",
        title="Is sipi.bot SOC 2 Compliant?",
        desc="The honest answer on sipi.bot's compliance posture: what we provide (deterministic controls, audit logs) and what we don't claim.",
        h1="Is sipi.bot SOC 2 Compliant?",
        lead="The honest answer: we don't make certification claims in this page. Here's exactly what sipi.bot provides, and how to verify current compliance posture.",
        sections=[
            ("What sipi.bot provides",
             ["Deterministic spend controls — rules that can't be argued with or injected.",
              "A queryable audit log of every decision, with the rule that fired.",
              "Merchant allowlists and approval workflows for vendor governance."]),
            ("What we don't claim here",
             ["Certification status (SOC 2, ISO 27001) is a moving target — verify the current posture with the team before relying on it in procurement."]),
            ("How to evaluate",
             ["Ask for the current compliance documentation, run the eval gym yourself (the core is MIT), and test the audit log against your requirements."]),
        ],
        table=dict(
            headers=["Question", "Answer"],
            rows=[
                ["Deterministic controls", "Yes — rules engine, no model in the path"],
                ["Audit log", "Yes — every decision logged"],
                ["Certification status", "Verify current posture with the team"],
                ["Self-host option", "Yes — MIT core"],
            ],
        ),
        faqs=[
            ("Can I self-host for compliance?",
             "Yes — the MIT core runs in your environment, which can simplify compliance in some regimes."),
            ("Where do I verify compliance?",
             "Contact the team for current documentation; don't rely on marketing pages."),
        ],
        related=[("Security page", "/security"), ("Compliance officers", "/for/compliance-officers"), ("Self-host guide", "/self-hosted/")],
    ),
]

# --- hub metadata -----------------------------------------------------------
