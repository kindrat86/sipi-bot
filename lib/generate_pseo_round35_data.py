"""Round 35 pSEO data — sipi.bot (2026-08-08).

Sixteenth round. Local-AI stack (Open WebUI, AnythingLLM), the build-cost
query, kill-switch/spend-cap glossary, security templates, rogue-agent
scenario, Stripe-payments compose comparison, worth-it answer, security
tools list. 11 static pages + 1 blog.

All existing dirs — no plumbing. Content honest (build-cost = honest ranges
with variables, never fabricated precision; worth-it = honest trade-offs).
"""

INTEGRATIONS = [
    dict(
        slug="open-webui",
        title="Open WebUI Agent Spend Control — sipi.bot Integration",
        desc="Open WebUI is the self-hosted AI frontend millions run. sipi.bot gates the agent spend behind it.",
        h1="Spend Control for Open WebUI",
        lead="Open WebUI is the open-source frontend for local and hosted LLMs — chat, agents, and tool pipelines. The frontend is free; the agents behind it spend.",
        sections=[
            ("Why Open WebUI agents spend",
             ["Agents and pipelines call paid APIs and tools.",
              "Multi-user deployments multiply usage.",
              "Local models still call paid tools beyond inference."]),
            ("How it works",
             ["Wire the guard into your agents and pipelines: before any spend, they ask sipi.bot and get a deterministic decision."]),
            ("Rules that fit",
             ["Per-user or per-pipeline daily ceiling.",
              "Merchant allowlist for paid tools.",
              "Velocity limit on retry loops."]),
        ],
        code=dict(
            title="Guard call",
            lang="python",
            body='import requests\n\nr = requests.post("https://sipi.bot/v1/transactions/evaluate",\n    json={"amount": 10, "merchant": "api.vendor.com", "category": "api"},\n    headers={"Authorization": "Bearer KEY"})\ndecision = r.json()["decision"]',
            caption="Your frontend, our gate.",
        ),
        faqs=[
            ("Does this work with local models?",
             "Yes — the firewall governs tool and API spend regardless of inference location."),
            ("Can I cap per user?",
             "Yes — per-agent rules per user or pipeline."),
        ],
        related=[("Ollama cost", "/cost-of/ollama-cost"), ("AnythingLLM", "/integrations/anythingllm"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
    dict(
        slug="anythingllm",
        title="AnythingLLM Agent Spend Control — sipi.bot Integration",
        desc="AnythingLLM is the local RAG + agent desktop app. sipi.bot gates what its agents spend on tools and APIs.",
        h1="Spend Control for AnythingLLM",
        lead="AnythingLLM brings RAG and agents to the desktop — free and local. Local inference is cheap; the paid tools and APIs its agents call are not.",
        sections=[
            ("Why AnythingLLM agents spend",
             ["Agents call paid tools and data APIs mid-task.",
              "RAG pipelines hit embedding and search APIs.",
              "Shared deployments multiply usage."]),
            ("How it works",
             ["Add the guard as a tool: before any spend, the agent gets APPROVED, BLOCKED, or FLAGGED."]),
            ("Rules that fit",
             ["Per-workspace daily ceiling.",
              "Merchant allowlist for data and tool APIs.",
              "Category rule: embeddings vs tools."]),
        ],
        code=dict(
            title="Guard call",
            lang="python",
            body='from sipi_guard import sipi_guard\n\ndecision = sipi_guard(amount=7, merchant="embedding-api.com", category="data")\n# APPROVED | BLOCKED | FLAGGED',
            caption="Local RAG, governed spend.",
        ),
        faqs=[
            ("Does this slow the desktop app?",
             "No — ~5 ms per check, spend actions only."),
            ("Can I cap per workspace?",
             "Yes — per-agent rules per workspace."),
        ],
        related=[("Open WebUI", "/integrations/open-webui"), ("vLLM cost", "/cost-of/vllm-cost"), ("How to implement spend controls", "/how-to/how-to-implement-spend-controls")],
    ),
]

VS = [
    dict(
        slug="stripe-payments",
        name="Stripe Payments",
        title="sipi.bot vs Stripe Payments — Payment Rails vs Spend Firewall",
        desc="Stripe moves money; sipi.bot decides whether agents may move it. Different layers of the same pipeline.",
        h1="sipi.bot vs Stripe Payments",
        lead="Stripe is payment infrastructure — it moves money. sipi.bot is a spend firewall — it decides whether an agent's money should move at all. One executes; the other governs.",
        sections=[
            ("What Stripe does well",
             ["Best-in-class payment rails: processing, billing, payouts.",
              "The standard way to move money programmatically."]),
            ("Where it falls short for agent spend",
             ["Stripe processes payments; it doesn't decide whether an agent may pay.",
              "No per-agent policy, no merchant intent review, no autonomy gate."]),
            ("Where sipi.bot wins",
             ["Evaluates every proposed transaction BEFORE it reaches the rail.",
              "Caps, allowlists, velocity limits, approvals — deterministic."]),
            ("When to use which",
             ["Stripe for the rail; sipi.bot for the gate. They compose: sipi.bot decides, Stripe executes."]),
        ],
        table=dict(
            headers=["Dimension", "Stripe", "sipi.bot"],
            rows=[
                ["Role", "Payment processing", "Pre-spend firewall"],
                ["When it acts", "Executes payments", "Before payments"],
                ["Decision", "Settle or fail", "APPROVED / BLOCKED / FLAGGED"],
                ["Policy", "Billing rules", "Agent spend rules"],
            ],
        ),
        faqs=[
            ("Are they competitors?",
             "No — Stripe is the rail; sipi.bot is the gate in front of it."),
            ("Can they integrate?",
             "Yes — sipi.bot approves, then Stripe settles."),
        ],
        related=[("sipi.bot vs Stripe Billing", "/vs/stripe-billing"), ("sipi.bot vs Stripe Spend Controls", "/vs/stripe-spend-controls"), ("Agentic payment", "/glossary/agentic-payment")],
    ),
]

ANSWERS = [
    dict(
        slug="how-much-does-it-cost-to-build-an-ai-agent",
        title="How Much Does It Cost to Build an AI Agent?",
        desc="The honest build-cost breakdown: models, tools, infrastructure, and the running cost nobody budgets.",
        h1="How Much Does It Cost to Build an AI Agent?",
        lead="Building an agent costs a few hundred dollars to start and a few thousand a month to run — the honest range depends on the model, the tools, and the volume.",
        sections=[
            ("The build cost",
             ["Development: a capable team can ship a first agent in days to weeks — the cost is engineering time.",
              "Models: API credits during development, usually modest.",
              "Tools and infra: whatever the agent calls and runs on."]),
            ("The running cost",
             ["Per-call pennies × volume — the number that matters.",
              "A pilot agent might cost hundreds a month; a production fleet, thousands and up.",
              "The documented runaways show the tail: hundreds to millions when ungoverned."]),
            ("The honest formula",
             ["Build = engineering time + dev credits. Run = rate × volume, governed by ceilings, velocity limits, and allowlists."]),
        ],
        table=dict(
            headers=["Bucket", "Cost driver"],
            rows=[
                ["Build", "Engineering time"],
                ["Models", "Rate × volume"],
                ["Tools", "Merchants the agent calls"],
                ["Runaway tail", "Ungoverned volume"],
            ],
        ),
        faqs=[
            ("Is it expensive to build?",
             "Not compared to the running cost — governance is the budget line that compounds."),
            ("What's the smartest first step?",
             "Cap the pilot before it runs — ceilings from day one."),
        ],
        related=[("Why agents cost so much", "/answers/why-do-ai-agents-cost-so-much/"), ("How to set a budget", "/answers/how-to-set-a-budget-for-ai-agents/"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs")],
    ),
    dict(
        slug="are-ai-agents-worth-it",
        title="Are AI Agents Worth It?",
        desc="The honest worth-it answer: agents pay for themselves where volume and autonomy meet — and cost real money when ungoverned.",
        h1="Are AI Agents Worth It?",
        lead="Agents are worth it where they do work at scale that humans shouldn't — and they're not worth it when the spend runs ungoverned. The ROI is in the governance.",
        sections=[
            ("When agents earn their keep",
             ["High-volume work: support triage, document review, research.",
              "24/7 coverage: things that can't wait for humans.",
              "Autonomy where it's safe: governed tools, bounded budgets."]),
            ("When they don't",
             ["Low-volume tasks a human does faster.",
              "Anything with a runaway tail — an ungoverned agent is a liability, not an asset."]),
            ("The honest ROI test",
             ["Value per task × volume − cost per task × volume, with the tail capped. If the ceiling makes the math work, they're worth it."]),
        ],
        faqs=[
            ("What's the biggest risk to ROI?",
             "The tail — one runaway wipes out months of value. Caps fix that."),
            ("What's the first thing to automate?",
             "The highest-volume, lowest-judgment task — with a budget."),
        ],
        related=[("Why agents cost so much", "/answers/why-do-ai-agents-cost-so-much/"), ("Agent ROI framework", "/benchmarks/ai-agent-spend-roi"), ("How to set a budget", "/answers/how-to-set-a-budget-for-ai-agents/")],
    ),
]

GLOSSARY = [
    dict(
        slug="kill-switch",
        term="Kill switch",
        title="What is a Kill Switch? | sipi.bot Glossary",
        desc="A kill switch is the instant off button for an agent's spending — the first control you should know.",
        h1="What is a Kill Switch?",
        lead="A kill switch is a control that instantly disables an agent's ability to spend — the emergency brake for a runaway.",
        sections=[
            ("How it works",
             ["One action disables spending for an agent, fleet, or merchant.",
              "The next transaction is blocked the moment it's evaluated."]),
            ("Why it matters",
             ["Runaways compound at machine speed — seconds count.",
              "A kill switch turns 'stop the bleeding' from a project into a click."]),
            ("The design principle",
             ["The kill switch should be faster than the agent. Deterministic rules make that possible."]),
        ],
        faqs=[
            ("Does a kill switch undo past spend?",
             "No — it stops new spend. Past transactions stay in the audit log."),
            ("Is a kill switch enough?",
             "No — pair it with ceilings and velocity limits so you rarely need it."),
        ],
        related=[("How to stop runaway agents", "/how-to/how-to-stop-runaway-agents"), ("Velocity limit", "/glossary/velocity-limit"), ("Daily spend ceiling", "/glossary/daily-spend-ceiling")],
    ),
    dict(
        slug="spend-cap",
        term="Spend cap",
        title="What is a Spend Cap? | sipi.bot Glossary",
        desc="A spend cap is the maximum an agent may spend in a period — the number that makes agent budgets real.",
        h1="What is a Spend Cap?",
        lead="A spend cap is a hard ceiling on what an agent may spend — per transaction, per day, or per month.",
        sections=[
            ("The kinds of caps",
             ["Per-transaction: the largest single purchase allowed.",
              "Per-period: daily, weekly, or monthly ceilings.",
              "Per-category: caps on inference, data, tools, payments."]),
            ("Why caps matter",
             ["They bound the worst case — the audit log can't stop a runaway, a cap can."]),
            ("The tuning loop",
             ["Set from actuals × 1.5, then tighten with audit-log data."]),
        ],
        faqs=[
            ("What's a good starting cap?",
             "Recent actuals × 1.5, then tighten."),
            ("Do caps slow agents?",
             "No — they only stop spend beyond the budget."),
        ],
        related=[("Daily spend ceiling", "/glossary/daily-spend-ceiling"), ("How to set spend limits", "/how-to/how-to-set-spend-limits"), ("Budget exhaustion", "/glossary/budget-exhaustion")],
    ),
]

TEMPLATES = [
    dict(
        slug="agent-time-of-day-policy",
        title="Agent Time-of-Day Policy Template",
        desc="The time-of-day policy: which agents may run when, what happens overnight, and the review rule.",
        h1="Agent Time-of-Day Policy",
        lead="Autonomous agents run 24/7 by default — which means spend happens at 3 a.m. with no one watching. This policy decides when.",
        sections=[
            ("The policy",
             ["1. Core hours (08:00–20:00 local): autonomous spend allowed within ceilings.",
              "2. Overnight: spend-capable runs FLAG for morning review, except approved services.",
              "3. Approved overnight services: allowlisted, with reduced caps.",
              "4. Exceptions: maintenance windows, approved by the budget owner.",
              "5. Review: overnight flags reviewed daily at 09:00."]),
        ],
        faqs=[
            ("Is overnight spend the risk?",
             "It's when no human is watching — the review rule closes that gap."),
            ("What about global teams?",
             "Set windows per region or use the audit log to find your risk hours."),
        ],
        related=[("Time-of-day rule", "/tutorials/set-up-time-of-day-rules"), ("Approval threshold policy", "/policies/approval-threshold-policy"), ("Agent runbook template", "/templates/agent-runbook-template")],
    ),
    dict(
        slug="prompt-injection-response-plan",
        title="Prompt Injection Response Plan Template",
        desc="The response plan for a prompt-injection incident: detect, contain, assess, and prevent — with the spend angle.",
        h1="Prompt Injection Response Plan",
        lead="When injection happens — and it will — the plan is: detect, contain, assess, prevent. The spend angle makes containment concrete.",
        sections=[
            ("The plan",
             ["1. Detect: anomaly in the audit log (unexpected merchant, velocity, amount).",
              "2. Contain: kill switch on the affected agents, block the injected destination.",
              "3. Assess: what did the injection attempt? What moved?",
              "4. Prevent: add the missing rule — deterministic gates can't be injected."]),
        ],
        faqs=[
            ("How do I detect an injection?",
             "The audit log — unexpected spend patterns are the first signal."),
            ("What's the best prevention?",
             "Rules on the money path — prompts can be injected, rules can't."),
        ],
        related=[("The hidden cost of prompt injection", "/blog/the-hidden-cost-of-prompt-injection"), ("Can sipi.bot stop injection", "/faq/can-sipi-bot-stop-prompt-injection"), ("Incident response plan", "/templates/incident-response-plan-template")],
    ),
]

SCENARIOS = [
    dict(
        slug="agent-goes-rogue-scenario",
        title="Agent Goes Rogue Scenario — What the Firewall Does",
        desc="The rogue-agent eval scenario: an agent begins spending beyond intent. The firewall's role, step by step.",
        h1="Agent Goes Rogue Scenario",
        lead="An agent 'going rogue' means spending beyond what anyone intended — the eval gym tests exactly how the firewall responds.",
        sections=[
            ("The scenario",
             ["An agent starts calling tools and merchants outside its task.",
              "Spend accelerates across a session.",
              "No human is watching."]),
            ("What the firewall does",
             ["The merchant allowlist blocks unknown destinations.",
              "Velocity limits stop the accelerating cadence.",
              "Caps bound the total damage.",
              "The audit log shows the full sequence."]),
            ("The honest limit",
             ["The firewall enforces rules — the missing rule it can't invent. Review what it blocked and add the gap."]),
        ],
        faqs=[
            ("Is this in the eval gym?",
             "Yes — it's one of the 53 scenarios, 53/53 passing."),
            ("What's the most common cause?",
             "A missing allowlist entry or a threshold set too high."),
        ],
        related=[("Eval report", "/eval-report/"), ("How to stop runaway agents", "/how-to/how-to-stop-runaway-agents"), ("Kill switch", "/glossary/kill-switch")],
    ),
]

BEST = [
    dict(
        slug="best-agent-security-tools",
        title="Best Agent Security Tools 2026 — Honest List",
        desc="The best agent security tools: secret scanning, MCP vetting, and the spend firewall that makes damage impossible.",
        h1="Best Agent Security Tools 2026",
        lead="Securing agents means three jobs: guarding credentials, vetting the tools they call, and gating the money. Here's the honest stack.",
        sections=[
            ("Credential security",
             ["Secret scanning (GitGuardian, TruffleHog) for leaked keys.",
              "Rotation and scoped keys per agent."]),
            ("Tool and MCP vetting",
             ["MCP server vetting — source, permissions, paid calls.",
              "Least-privilege tool access."]),
            ("Spend gating",
             ["A spend firewall: deterministic decisions on the money path.",
              "Caps, allowlists, velocity limits — the layer that makes damage impossible."]),
        ],
        table=dict(
            headers=["Layer", "Tools", "Job"],
            rows=[
                ["Credentials", "Secret scanning", "Find leaks"],
                ["Tools", "MCP vetting", "Trust review"],
                ["Money", "Spend firewall", "Gate damage"],
            ],
        ),
        faqs=[
            ("What's the most important layer?",
             "All three — but the money gate is the one that makes runaways impossible."),
            ("Where should I start?",
             "Secret scanning for today, spend rules for tomorrow."),
        ],
        related=[("Red flags in API keys", "/redflags/red-flags-in-api-keys"), ("MCP security checklist", "/checklists/mcp-security-checklist/"), ("API key compromise scenario", "/scenarios/api-key-compromise-scenario")],
    ),
]

# --- hub metadata -----------------------------------------------------------
