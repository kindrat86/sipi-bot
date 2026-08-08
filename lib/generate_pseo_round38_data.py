"""Round 38 pSEO data — sipi.bot (2026-08-08).

Nineteenth round. Voice/audio API costs (ElevenLabs, Deepgram, OpenAI
Realtime — big queries, pairs with the voice cluster), best voice platforms,
budget-owner persona (the actual buyer), pharma/utilities sectors,
sales agents, risk assessment, voice red flags, agent-payment answers,
forecasting blog. 13 static pages + 1 blog.

All existing dirs — no plumbing. Content honest; pricing verify-current.
"""

COST_OF = [
    dict(
        slug="elevenlabs-cost",
        title="ElevenLabs Cost — Pricing and Agent Spend Control",
        desc="ElevenLabs cost: voice generation pricing, the credit model, and how to control agent spend on TTS.",
        h1="How Much Does ElevenLabs Cost?",
        lead="ElevenLabs bills per character of generated speech (plus credits for advanced models). For voice agents, the bill is characters × volume.",
        sections=[
            ("How ElevenLabs pricing works",
             ["Per-character pricing for TTS, with credit tiers.",
              "Higher-quality models cost more per character.",
              "Verify current pricing on ElevenLabs' site."]),
            ("The agentic multiplier",
             ["Voice agents generate speech per turn — characters compound fast.",
              "Retry loops regenerate audio."]),
            ("What it really costs",
             ["Per-character rate × volume. Per-agent caps and velocity limits control the volume."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["TTS characters", "Model tier selection"],
                ["Voice agent turns", "Per-agent ceilings"],
                ["Retries", "Velocity limits"],
            ],
        ),
        faqs=[
            ("Is ElevenLabs expensive for agents?",
             "Rates vary by tier — verify current pricing. Volume dominates."),
            ("Can sipi.bot govern ElevenLabs spend?",
             "Yes — per-agent caps and category rules apply to any merchant."),
        ],
        related=[("Voice agents", "/use-cases/voice-agents"), ("Vapi pricing", "/cost-of/vapi-pricing"), ("ElevenLabs integration", "/integrations/elevenlabs")],
    ),
    dict(
        slug="deepgram-cost",
        title="Deepgram Cost — Pricing and Agent Spend Control",
        desc="Deepgram cost: transcription and speech AI pricing, and how to control agent spend on STT.",
        h1="How Much Does Deepgram Cost?",
        lead="Deepgram bills per audio minute for transcription and per request for speech features. Voice agents transcribe every call — minutes add up.",
        sections=[
            ("How Deepgram pricing works",
             ["Per-minute pricing for transcription (STT).",
              "Per-request pricing for speech and language features.",
              "Verify current pricing on Deepgram's site."]),
            ("The agentic multiplier",
             ["Voice agents transcribe every call — billable minutes at volume.",
              "Retried calls re-bill minutes."]),
            ("What it really costs",
             ["Per-minute rate × call volume. Per-agent ceilings and velocity limits control the volume."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Transcription minutes", "Per-agent daily ceiling"],
                ["Speech features", "Category budget"],
                ["Retried calls", "Velocity limit"],
            ],
        ),
        faqs=[
            ("Is Deepgram priced per minute?",
             "Yes — verify current pricing."),
            ("Can sipi.bot govern Deepgram spend?",
             "Yes — per-agent caps and category rules."),
        ],
        related=[("Meeting agents", "/use-cases/meeting-agents"), ("Voice agents", "/use-cases/voice-agents"), ("Deepgram integration", "/integrations/deepgram")],
    ),
    dict(
        slug="openai-realtime-api-cost",
        title="OpenAI Realtime API Cost — Pricing and Agent Spend Control",
        desc="OpenAI Realtime API cost: audio-in/audio-out pricing and the agentic voice bill.",
        h1="How Much Does the OpenAI Realtime API Cost?",
        lead="The Realtime API bills audio tokens — more expensive per token than text. Voice agents on Realtime feel it fast.",
        sections=[
            ("How Realtime pricing works",
             ["Audio input/output tokens billed at a premium over text tokens.",
              "Model choice drives the rate.",
              "Verify current pricing on OpenAI's site."]),
            ("The agentic multiplier",
             ["Voice agents hold long realtime sessions.",
              "Every turn adds audio tokens; retries compound."]),
            ("What it really costs",
             ["Audio-token rate × session volume. Per-agent ceilings and session caps control it."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Audio tokens", "Model selection"],
                ["Session length", "Per-session caps"],
                ["Call volume", "Per-agent ceilings"],
            ],
        ),
        faqs=[
            ("Is Realtime pricier than text?",
             "Audio tokens cost more per token — verify current pricing."),
            ("Can sipi.bot govern Realtime spend?",
             "Yes — per-agent caps and category rules."),
        ],
        related=[("Voice agents", "/use-cases/voice-agents"), ("GPT API cost", "/cost-of/gpt-api-cost"), ("Best voice platforms", "/best/best-voice-agent-platforms-2026")],
    ),
]

BEST = [
    dict(
        slug="best-voice-agent-platforms-2026",
        title="Best Voice Agent Platforms 2026 — Honest Comparison",
        desc="The best voice agent platforms: Vapi, Retell, Bland, and the new wave. Honest criteria — and the spend layer every platform hides.",
        h1="Best Voice Agent Platforms 2026",
        lead="Voice agent platforms differ on latency, telephony, and pricing — but every one of them bills per minute and per token. The spend layer is yours to add.",
        sections=[
            ("The platforms teams run",
             ["Vapi — the developer standard for voice agents.",
              "Retell — low-latency voice with strong telephony.",
              "Bland AI — high-volume automated calling.",
              "LiveKit Agents — the open-source infrastructure play.",
              "OpenAI Realtime — direct audio-to-audio sessions."]),
            ("How to choose",
             ["Latency, telephony coverage, pricing model, and control.",
              "All of them bill per minute + tokens — budget for the spend, not just the rate."]),
            ("The spend angle",
             ["Every platform needs the same money gate: ceilings, allowlists, velocity limits."]),
        ],
        table=dict(
            headers=["Platform", "Best at", "Spend layer"],
            rows=[
                ["Vapi", "Developer velocity", "External firewall"],
                ["Retell", "Low latency", "External firewall"],
                ["Bland", "Call volume", "External firewall"],
                ["LiveKit", "Open source", "External firewall"],
                ["Realtime", "Audio-to-audio", "External firewall"],
            ],
        ),
        faqs=[
            ("Which platform is best?",
             "Stack-dependent — latency, telephony, and pricing. All need a spend gate."),
            ("Is one cheaper?",
             "Rates vary — verify current pricing. The bill is minutes × tokens × volume."),
        ],
        related=[("Voice agents", "/use-cases/voice-agents"), ("Vapi pricing", "/cost-of/vapi-pricing"), ("Voice agent launch checklist", "/checklists/voice-agent-launch-checklist/")],
    ),
]

INTEGRATIONS = [
    dict(
        slug="elevenlabs",
        title="ElevenLabs Voice Agent Spend Control — sipi.bot Integration",
        desc="Gate what ElevenLabs-powered agents spend on TTS: per-character ceilings and category budgets.",
        h1="Spend Control for ElevenLabs",
        lead="ElevenLabs is the TTS backbone for voice agents — billed per character. The guard caps the voice line.",
        sections=[
            ("Why ElevenLabs agents spend",
             ["Per-character billing at conversation volume.",
              "Premium voices cost more per character."]),
            ("How it works",
             ["Call the guard before TTS runs: amount, merchant, category → APPROVED, BLOCKED, or FLAGGED."]),
            ("Rules that fit",
             ["Per-agent daily ceiling on the voice category.",
              "Velocity limit on regeneration loops."]),
        ],
        code=dict(
            title="Guard call",
            lang="python",
            body='import requests\n\nr = requests.post("https://sipi.bot/v1/transactions/evaluate",\n    json={"amount": 4.2, "merchant": "elevenlabs", "category": "voice"},\n    headers={"Authorization": "Bearer KEY"})\ndecision = r.json()["decision"]',
            caption="Characters are a bill; the gate makes it a budget.",
        ),
        faqs=[
            ("Does this slow TTS?",
             "No — ~5 ms per check."),
            ("Can I cap per voice agent?",
             "Yes — per-agent rules per agent."),
        ],
        related=[("ElevenLabs cost", "/cost-of/elevenlabs-cost"), ("Voice agents", "/use-cases/voice-agents"), ("Best voice platforms", "/best/best-voice-agent-platforms-2026")],
    ),
    dict(
        slug="deepgram",
        title="Deepgram Transcription Agent Spend Control — sipi.bot Integration",
        desc="Gate what Deepgram-powered agents spend on transcription: per-minute ceilings and retry limits.",
        h1="Spend Control for Deepgram",
        lead="Deepgram transcribes at scale — per minute. Meeting and voice agents burn minutes fast. The guard caps the line.",
        sections=[
            ("Why Deepgram agents spend",
             ["Per-minute billing for transcription.",
              "Meeting agents transcribe every session."]),
            ("How it works",
             ["Guard call before transcription runs: APPROVED, BLOCKED, or FLAGGED."]),
            ("Rules that fit",
             ["Per-team daily ceiling on transcription.",
              "Velocity limit on retried sessions."]),
        ],
        code=dict(
            title="Guard call",
            lang="python",
            body='import requests\n\nr = requests.post("https://sipi.bot/v1/transactions/evaluate",\n    json={"amount": 6.0, "merchant": "deepgram", "category": "transcription"},\n    headers={"Authorization": "Bearer KEY"})\ndecision = r.json()["decision"]',
            caption="Minutes are a bill; the gate makes it a budget.",
        ),
        faqs=[
            ("Does this slow transcription?",
             "No — ~5 ms per check."),
            ("Can I cap per team?",
             "Yes — per-agent rules per team."),
        ],
        related=[("Deepgram cost", "/cost-of/deepgram-cost"), ("Meeting agents", "/use-cases/meeting-agents"), ("Voice agent launch checklist", "/checklists/voice-agent-launch-checklist/")],
    ),
]

SECTORS = [
    dict(
        slug="pharma",
        title="AI Spend Control for Pharma | sipi.bot",
        desc="Pharma AI agents: research, clinical, and regulatory bots that spend on data and compute per program.",
        h1="Spend Control for Pharma AI Agents",
        lead="Pharma runs agents for literature review, clinical operations, and regulatory documentation — each with paid data and inference per program.",
        sections=[
            ("Where pharma agents spend",
             ["Literature and patent data per query.",
              "Clinical-trial operations inference.",
              "Regulatory documentation at scale.",
              "Research pipelines on compute."]),
            ("The failure modes",
             ["A literature loop re-pulling data multiplies charges.",
              "Unknown data vendors bypass procurement.",
              "No per-program budget."]),
            ("Which rules to start with",
             ["Per-program daily ceiling.",
              "Merchant allowlist for data vendors.",
              "Category rule: data vs compute."]),
        ],
        table=dict(
            headers=["Pharma spend", "Control"],
            rows=[
                ["Literature data", "Per-program ceiling"],
                ["Clinical ops", "Category budget"],
                ["Regulatory docs", "Daily cap"],
                ["Research compute", "Merchant allowlist"],
            ],
        ),
        faqs=[
            ("Can I budget per program?",
             "Yes — per-agent rules per program."),
            ("Does it slow research?",
             "No — ~5 ms per check."),
        ],
        related=[("Healthcare sector", "/sectors/healthcare"), ("Research agents", "/use-cases/research-agents"), ("How to implement spend controls", "/how-to/how-to-implement-spend-controls")],
    ),
    dict(
        slug="utilities",
        title="AI Spend Control for Utilities | sipi.bot",
        desc="Utility AI agents: grid, customer care, and field-service bots that spend on data and inference at network scale.",
        h1="Spend Control for Utility AI Agents",
        lead="Utilities run agents for grid operations, customer care, and field service — each with paid data and inference at network scale.",
        sections=[
            ("Where utility agents spend",
             ["Grid-telemetry data feeds.",
              "Customer-care inference at volume.",
              "Field-service dispatch tools.",
              "Compliance reporting bots."]),
            ("The failure modes",
             ["A telemetry loop re-pulling data multiplies charges.",
              "Overnight grid runs without review.",
              "Unknown vendors bypass procurement."]),
            ("Which rules to start with",
             ["Per-region daily ceiling.",
              "Time-of-day rule for overnight runs.",
              "Merchant allowlist for data vendors."]),
        ],
        table=dict(
            headers=["Utility spend", "Control"],
            rows=[
                ["Telemetry data", "Per-region ceiling"],
                ["Customer care", "Daily cap"],
                ["Field service", "Category budget"],
                ["Overnight runs", "Time-of-day rule"],
            ],
        ),
        faqs=[
            ("Can I budget per region?",
             "Yes — per-agent rules per region."),
            ("Does it slow grid ops?",
             "No — ~5 ms per check."),
        ],
        related=[("Energy sector", "/sectors/energy"), ("Telecom sector", "/sectors/telecom"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
]

FOR = [
    dict(
        slug="budget-owners",
        title="Agent Spend Control for Budget Owners | sipi.bot",
        desc="Budget owners: you set the ceiling, the firewall enforces it, and the audit log proves it. The control that makes your budget real.",
        h1="Agent Spend Control for Budget Owners",
        lead="You own the budget; the firewall enforces it. Per-agent ceilings, approval thresholds, and an audit trail — the control layer that makes your numbers real.",
        sections=[
            ("Why budget owners need a firewall",
             ["Budgets in a spreadsheet don't stop spend.",
              "Agents spend autonomously — no PO, no approval, no ledger.",
              "The audit log is the ledger they were missing."]),
            ("What to set",
             ["Ceilings per agent and category.",
              "Approval thresholds for material spend.",
              "Allowlists for approved vendors."]),
            ("The reporting",
             ["The log answers: who spent, on what, against which rule — monthly, in minutes."]),
        ],
        table=dict(
            headers=["Budget owner lever", "sipi.bot answer"],
            rows=[
                ["Ceilings", "Enforced per agent"],
                ["Approvals", "Threshold + queue"],
                ["Vendors", "Allowlists"],
                ["Reporting", "Queryable audit log"],
            ],
        ),
        faqs=[
            ("Do budgets slow agents?",
             "No — ceilings only stop spend beyond the budget."),
            ("What's the first ceiling to set?",
             "Recent actuals × 1.5, tightened with the log."),
        ],
        related=[("CFOs", "/for/chief-financial-officers"), ("How to set a budget", "/answers/how-to-set-a-budget-for-ai-agents/"), ("Budget approval matrix", "/templates/budget-approval-matrix")],
    ),
]

TEMPLATES = [
    dict(
        slug="agent-risk-assessment-template",
        title="Agent Risk Assessment Template",
        desc="The risk assessment for any new agent: spend access, tool access, blast radius, and the controls required.",
        h1="Agent Risk Assessment Template",
        lead="Every new agent gets a risk score before it ships. This template makes the assessment fast and consistent.",
        sections=[
            ("The assessment",
             ["1. Spend access: can this agent spend? (score 0–5)",
              "2. Tool access: what can it call? (score 0–5)",
              "3. Autonomy: how long unattended? (score 0–5)",
              "4. Blast radius: worst-case cost if ungoverned? (score 0–5)",
              "5. Total: 0–8 low / 9–15 medium / 16–20 high.",
              "6. Required controls by level: low = ceiling; medium = + velocity + allowlist; high = + approvals + kill switch."]),
        ],
        faqs=[
            ("What's the minimum for any agent?",
             "A ceiling and a velocity limit — even for low risk."),
            ("Who reviews high-risk agents?",
             "The budget owner, before deployment."),
        ],
        related=[("Agent launch checklist", "/checklists/agent-launch-checklist/"), ("Agent onboarding brief", "/templates/agent-onboarding-spend-brief"), ("Vendor risk assessment", "/templates/vendor-risk-assessment-template")],
    ),
]

REDFLAGS = [
    dict(
        slug="red-flags-in-voice-agents",
        title="Red Flags in Voice Agent Spend",
        desc="The warning signs your voice agents are overspending: unbounded minutes, retry storms, and no per-call budgets.",
        h1="Red Flags in Voice Agent Spend",
        lead="Voice agents bill per minute and per token — the red flags are about unbounded volume, not rates.",
        sections=[
            ("The red flags",
             ["1. No per-call ceiling — one call can run long and bill big.",
              "2. Retry storms — failed calls re-bill minutes.",
              "3. 24/7 autonomy — no time-of-day review window.",
              "4. Mid-call tools ungoverned — purchases triggered inside calls.",
              "5. No per-campaign budget."]),
            ("The fix",
             ["Per-call ceilings, velocity limits on retries, and category rules separating minutes from tokens."]),
        ],
        faqs=[
            ("What's the most expensive red flag?",
             "Retry storms — billable minutes for nothing."),
            ("How do I bound a call?",
             "Per-call ceilings and velocity limits."),
        ],
        related=[("Voice agents", "/use-cases/voice-agents"), ("Voice agent launch checklist", "/checklists/voice-agent-launch-checklist/"), ("Vapi pricing", "/cost-of/vapi-pricing")],
    ),
]

USE_CASES = [
    dict(
        slug="sales-agents",
        title="Sales Agent Spend Control | sipi.bot",
        desc="Sales agents: prospecting, outreach, and demo bots that spend on data and comms per pipeline.",
        h1="Spend Control for Sales Agents",
        lead="Sales agents prospect, enrich, and reach out — each step hits paid data and comms APIs. Per-pipeline budgets.",
        sections=[
            ("Where sales agents spend",
             ["Prospecting data per record.",
              "Enrichment APIs per contact.",
              "Outreach and follow-up inference.",
              "Scheduling tools per meeting."]),
            ("The failure modes",
             ["An enrichment loop re-processing contacts multiplies charges.",
              "Unknown data vendors bypass procurement.",
              "Campaign spikes hit overage tiers."]),
            ("Which rules to start with",
             ["Per-campaign daily ceiling.",
              "Merchant allowlist for data vendors.",
              "Velocity limit on enrichment loops."]),
        ],
        table=dict(
            headers=["Sales spend", "Control"],
            rows=[
                ["Prospecting data", "Per-campaign ceiling"],
                ["Enrichment", "Velocity limit"],
                ["Outreach", "Category budget"],
                ["Scheduling", "Merchant allowlist"],
            ],
        ),
        faqs=[
            ("Can I budget per campaign?",
             "Yes — per-agent rules per campaign."),
            ("Does it slow outreach?",
             "No — ~5 ms per check."),
        ],
        related=[("Sales development agents", "/use-cases/sales-development-agents"), ("Cold email", "/use-cases/email-agents"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
]

ANSWERS = [
    dict(
        slug="how-do-agents-pay-for-services",
        title="How Do Agents Pay for Services?",
        desc="Agents pay through rails, not cards: x402, AP2, AgentKit, and API credits. And who gates it.",
        h1="How Do Agents Pay for Services?",
        lead="Agents pay through machine rails — x402, AP2, AgentKit, and plain API credits — not human checkout flows. The rails are settled; the gate is the open question.",
        sections=[
            ("The rails",
             ["x402: HTTP-based agent payments.",
              "AP2: the agent-pay protocol for agentic commerce.",
              "AgentKit: Coinbase's agent payment framework.",
              "API credits: the default — per-token or per-call billing."]),
            ("Who decides",
             ["The rail executes; the firewall decides.",
              "Deterministic rules in front of the rail: APPROVED, BLOCKED, FLAGGED."]),
        ],
        faqs=[
            ("Do agents have credit cards?",
             "Not typically — they use rails and API credits. Cards are the human layer."),
            ("What stops an agent from paying anything?",
             "The merchant allowlist — unapproved vendors are simply not payable."),
        ],
        related=[("x402", "/glossary/x402"), ("AP2", "/glossary/ap2"), ("Can agents pay with crypto", "/answers/can-ai-agents-pay-with-crypto/")],
    ),
]

# --- hub metadata -----------------------------------------------------------
