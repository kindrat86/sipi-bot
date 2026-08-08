"""Round 28 pSEO data — sipi.bot (2026-08-08).

Ninth round. Focus: the voice-AI-agent economy (per-minute telephony + LLM
spend nobody gates) + meeting agents + filler gaps. 17 static pages + 2 blog.

  integrations +1: vapi
  vs +4: vapi, retell, bland-ai, fireflies
  use-cases +2: voice-agents, meeting-agents
  cost-of +3: vapi-pricing, retell-pricing, fireflies-pricing
  for +1: data-engineers
  sectors +1: telecom
  benchmarks +1: agent-token-consumption-by-task
  best +1: best-ai-agent-frameworks
  faq +1: can-ai-agents-pay-subscriptions
  answers +1 (public/): how-to-choose-a-spend-firewall
  checklists +1 (public/): self-host-checklist
  blog +2 (via lib/generate_content.py)

All existing dirs — no plumbing. Content honest; voice-platform pricing is
public list info marked "verify current" (per-minute + LLM token components).
"""

INTEGRATIONS = [
    dict(
        slug="vapi",
        title="Vapi Voice Agent Spend Control — sipi.bot Integration",
        desc="Cap what Vapi voice agents spend: per-minute telephony plus LLM tokens per call. The guard sits in front of the call budget.",
        h1="Spend Control for Vapi",
        lead="Vapi builds AI voice agents that make and take calls — billed per minute of telephony plus LLM tokens per turn. At call volume, both lines compound fast.",
        sections=[
            ("Why Vapi agents overspend",
             ["Per-minute telephony charges scale directly with call volume — and with failed-call retries.",
              "LLM tokens per turn multiply across long or looping conversations.",
              "No built-in dollar budget for the agent's call spend."]),
            ("How it works",
             ["Call sipi.bot before a call or a high-cost turn: amount, merchant, category → APPROVED, BLOCKED, or FLAGGED in ~5 ms, fully logged."]),
            ("Rules that fit voice workloads",
             ["Per-call or per-day telephony ceiling.",
              "Category rule: telephony vs inference.",
              "Velocity limit so retry loops die before the minutes pile up."]),
        ],
        code=dict(
            title="Guard call",
            lang="python",
            body='import requests\n\nr = requests.post("https://sipi.bot/v1/transactions/evaluate",\n    json={"amount": 12.5, "merchant": "vapi", "category": "telephony"},\n    headers={"Authorization": "Bearer KEY"})\ndecision = r.json()["decision"]  # APPROVED | BLOCKED | FLAGGED',
            caption="One call before the minutes add up.",
        ),
        faqs=[
            ("Does this slow call setup?",
             "No — ~5 ms, and only spend actions trigger it."),
            ("Can I cap per campaign?",
             "Yes — per-agent rules per campaign or use case."),
        ],
        related=[("Voice agents", "/use-cases/voice-agents"), ("Vapi pricing", "/cost-of/vapi-pricing"), ("sipi.bot vs Vapi", "/vs/vapi")],
    ),
]

VS = [
    dict(
        slug="vapi",
        name="Vapi",
        title="sipi.bot vs Vapi — Voice Pipeline vs Spend Firewall",
        desc="Vapi builds the voice pipeline; sipi.bot gates the spend. Why the platform that makes calls isn't the one that budgets them.",
        h1="sipi.bot vs Vapi",
        lead="Vapi is a voice-agent platform — telephony, LLM orchestration, and the tools to ship AI callers. sipi.bot is a spend firewall. One makes the calls; the other budgets them.",
        sections=[
            ("What Vapi does well",
             ["Purpose-built voice infrastructure: telephony, WebSockets, tool calling mid-call.",
              "Fast path from prototype to production voice agents.",
              "Per-minute pricing that's predictable per call."]),
            ("Where it falls short",
             ["It bills per minute and per token; it doesn't budget them.",
              "No per-agent spend ceiling, no merchant policy, no approval queue.",
              "A retry storm of failed calls is billable minutes."]),
            ("Where sipi.bot wins",
             ["Pre-spend decisions on every call and tool purchase.",
              "Per-agent ceilings on telephony and inference.",
              "Deterministic, ~5 ms, fully logged."]),
            ("When to use which",
             ["Vapi for the voice pipeline; sipi.bot for the budget. They compose: sipi.bot decides, Vapi makes the call."]),
        ],
        table=dict(
            headers=["Dimension", "Vapi", "sipi.bot"],
            rows=[
                ["Role", "Voice agent platform", "Pre-spend firewall"],
                ["Unit", "Per-minute calls", "Dollar decisions"],
                ["Controls", "Call tooling", "Caps, allowlists, velocity"],
                ["Budget", "Bills per minute", "Enforces per agent"],
            ],
        ),
        faqs=[
            ("Are they competitors?",
             "No — different layers. Vapi runs the calls; sipi.bot governs their cost."),
            ("Does sipi.bot integrate with Vapi?",
             "Yes — via the HTTP API or MCP tool, called before expensive steps."),
        ],
        related=[("Vapi integration", "/integrations/vapi"), ("Vapi pricing", "/cost-of/vapi-pricing"), ("Voice agents", "/use-cases/voice-agents")],
    ),
    dict(
        slug="retell",
        name="Retell AI",
        title="sipi.bot vs Retell — Voice Agents vs Spend Control",
        desc="Retell builds voice agents; sipi.bot controls what they spend. The per-minute bill needs a gate.",
        h1="sipi.bot vs Retell",
        lead="Retell is a voice-agent platform with per-minute pricing. sipi.bot is a spend firewall. One bills the minutes; the other caps them.",
        sections=[
            ("What Retell does well",
             ["Low-latency voice agents with strong telephony integrations.",
              "Predictable per-minute pricing for production voice."]),
            ("Where it falls short",
             ["Bills per minute and per token — no dollar-level budget enforcement.",
              "No per-agent ceilings, merchant policy, or approval queue."]),
            ("Where sipi.bot wins",
             ["Decides before the spend: caps, velocity limits, approvals.",
              "Covers telephony AND the LLM tokens and tools the call triggers."]),
            ("When to use which",
             ["Retell for the voice; sipi.bot for the budget. Complementary."]),
        ],
        table=dict(
            headers=["Dimension", "Retell", "sipi.bot"],
            rows=[
                ["Role", "Voice agent platform", "Pre-spend firewall"],
                ["Unit", "Per-minute calls", "Dollar decisions"],
                ["Controls", "Call tooling", "Caps, allowlists, velocity"],
                ["Budget", "Bills per minute", "Enforces per agent"],
            ],
        ),
        faqs=[
            ("Do Retell and sipi.bot overlap?",
             "No — pipeline vs policy."),
            ("What does a voice agent cost beyond Retell?",
             "LLM tokens per turn and any tools the call triggers — both firewall-governed."),
        ],
        related=[("Retell pricing", "/cost-of/retell-pricing"), ("Voice agents", "/use-cases/voice-agents"), ("sipi.bot vs Vapi", "/vs/vapi")],
    ),
    dict(
        slug="bland-ai",
        name="Bland AI",
        title="sipi.bot vs Bland AI — Automated Calls vs Spend Firewall",
        desc="Bland runs automated phone calls; sipi.bot controls what they cost. Per-minute autonomy needs a budget.",
        h1="sipi.bot vs Bland AI",
        lead="Bland AI automates phone conversations at scale. sipi.bot is a spend firewall. Scale is exactly why the spend needs a gate.",
        sections=[
            ("What Bland does well",
             ["High-volume automated calling with enterprise scale.",
              "Conversational AI over telephony with per-minute billing."]),
            ("Where it falls short",
             ["Per-minute billing scales with autonomy — no budget enforcement.",
              "No per-agent ceiling, merchant policy, or approval queue."]),
            ("Where sipi.bot wins",
             ["Pre-spend decisions at scale: caps, velocity, approvals.",
              "The audit log shows every call-dollar, per agent."]),
            ("When to use which",
             ["Bland for the calls; sipi.bot for the budget."]),
        ],
        table=dict(
            headers=["Dimension", "Bland AI", "sipi.bot"],
            rows=[
                ["Role", "Automated calling", "Pre-spend firewall"],
                ["Unit", "Per-minute calls", "Dollar decisions"],
                ["Controls", "Call tooling", "Caps, allowlists, velocity"],
                ["Budget", "Bills per minute", "Enforces per agent"],
            ],
        ),
        faqs=[
            ("Does Bland need a firewall?",
             "At volume, yes — per-minute bills compound fast with retries and scale."),
            ("Is sipi.bot a calling platform?",
             "No — it's the spend layer in front of one."),
        ],
        related=[("Voice agents", "/use-cases/voice-agents"), ("sipi.bot vs Vapi", "/vs/vapi"), ("Velocity limit", "/glossary/velocity-limit")],
    ),
    dict(
        slug="fireflies",
        name="Fireflies",
        title="sipi.bot vs Fireflies — Meeting Notes vs Spend Control",
        desc="Fireflies transcribes meetings; sipi.bot controls what transcription and summarization agents spend. Different jobs.",
        h1="sipi.bot vs Fireflies",
        lead="Fireflies records and transcribes meetings. sipi.bot is a spend firewall for agents — including the transcription and summarization agents that ride on platforms like Fireflies.",
        sections=[
            ("What Fireflies does well",
             ["Meeting recording, transcription, and search that teams love.",
              "Per-seat pricing with AI credits."]),
            ("Where it falls short",
             ["Per-seat + AI-credit billing — no dollar-level enforcement for heavy usage.",
              "No merchant policy or approval queue for AI spend."]),
            ("Where sipi.bot wins",
             ["Governs the agent side: transcription APIs, summarization inference, tool spend.",
              "Per-agent ceilings and velocity limits."]),
            ("When to use which",
             ["Fireflies for meeting capture; sipi.bot for the agent spend around it. Complementary."]),
        ],
        table=dict(
            headers=["Dimension", "Fireflies", "sipi.bot"],
            rows=[
                ["Role", "Meeting transcription", "Pre-spend firewall"],
                ["Unit", "Seats + AI credits", "Dollar decisions"],
                ["Controls", "Workspace tools", "Caps, allowlists, velocity"],
                ["Budget", "Per-seat billing", "Enforces per agent"],
            ],
        ),
        faqs=[
            ("Do they compete?",
             "No — one captures meetings, the other gates agent spend."),
            ("What's the agent angle?",
             "Meeting-agents that transcribe and summarize call paid APIs per minute of audio — that's firewall territory."),
        ],
        related=[("Meeting agents", "/use-cases/meeting-agents"), ("Fireflies pricing", "/cost-of/fireflies-pricing"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs")],
    ),
]

USE_CASES = [
    dict(
        slug="voice-agents",
        title="Voice Agent Spend Control | sipi.bot",
        desc="Voice agents spend per minute of telephony plus LLM tokens per turn. Cap the call budget before the bill multiplies.",
        h1="Spend Control for Voice Agents",
        lead="Voice agents are the fastest-growing agent category — and the easiest to overspend on: every call bills minutes, and every turn bills tokens.",
        sections=[
            ("Where voice agents spend",
             ["Telephony minutes per call — including failed and retried calls.",
              "LLM tokens per turn across long or looping conversations.",
              "Tool calls triggered mid-call (lookups, bookings, payments).",
              "Platform fees on top (Vapi, Retell, Bland)."]),
            ("The failure modes",
             ["A retry storm of failed calls bills minutes for nothing.",
              "Long conversations compound tokens per turn.",
              "Voice campaigns scaling without a budget ceiling."]),
            ("Which rules to start with",
             ["Per-call or per-day telephony ceiling.",
              "Category rule: telephony vs inference.",
              "Velocity limit on retries.",
              "Merchant allowlist for voice platforms and tools."]),
        ],
        table=dict(
            headers=["Voice spend", "Control"],
            rows=[
                ["Telephony minutes", "Per-call / daily ceiling"],
                ["LLM tokens", "Category budget"],
                ["Mid-call tools", "Merchant allowlist"],
                ["Retries", "Velocity limit"],
            ],
        ),
        faqs=[
            ("Can I cap per campaign?",
             "Yes — per-agent rules per campaign or use case."),
            ("Does the firewall slow call setup?",
             "No — ~5 ms per check, spend actions only."),
        ],
        related=[("Vapi integration", "/integrations/vapi"), ("sipi.bot vs Vapi", "/vs/vapi"), ("Vapi pricing", "/cost-of/vapi-pricing")],
    ),
    dict(
        slug="meeting-agents",
        title="Meeting Agent Spend Control | sipi.bot",
        desc="Meeting agents transcribe and summarize — paid per audio minute and per token. Cap the meeting stack's spend.",
        h1="Spend Control for Meeting Agents",
        lead="Meeting agents record, transcribe, and summarize — each step bills per minute of audio and per token. At team scale, that's real money.",
        sections=[
            ("Where meeting agents spend",
             ["Transcription APIs billed per audio minute.",
              "Summarization inference per meeting.",
              "Search and retrieval tools over the transcript corpus.",
              "Per-seat platforms (Fireflies, Otter) plus AI credits."]),
            ("The failure modes",
             ["A transcription retry loop re-bills audio minutes.",
              "Summarization running over every meeting, including ones nobody reads.",
              "Corpus-scale retrieval hitting expensive tiers."]),
            ("Which rules to start with",
             ["Per-team daily ceiling on transcription.",
              "Category rule: transcription vs summarization.",
              "Velocity limit on retries."]),
        ],
        table=dict(
            headers=["Meeting spend", "Control"],
            rows=[
                ["Transcription", "Daily ceiling"],
                ["Summarization", "Category budget"],
                ["Retrieval", "Per-agent cap"],
                ["Platform seats", "Merchant allowlist"],
            ],
        ),
        faqs=[
            ("Can I cap per team?",
             "Yes — per-agent rules per team."),
            ("What's the biggest lever?",
             "Summarization scope — only summarize meetings that matter."),
        ],
        related=[("sipi.bot vs Fireflies", "/vs/fireflies"), ("Fireflies pricing", "/cost-of/fireflies-pricing"), ("Backoffice automation", "/use-cases/backoffice-automation")],
    ),
]

COST_OF = [
    dict(
        slug="vapi-pricing",
        title="How Much Does Vapi Cost? — Voice Agent Pricing Explained",
        desc="Vapi pricing: per-minute telephony plus LLM tokens per call. What a production voice agent really costs and how to control it.",
        h1="How Much Does Vapi Cost?",
        lead="Vapi bills per minute of telephony plus the LLM tokens each call consumes. The per-minute rate is the visible price; the tokens are where the bill escapes.",
        sections=[
            ("The pricing model",
             ["Per-minute telephony pricing for voice agents (rates vary by region and carrier).",
              "LLM token costs per turn — the model choice drives this line.",
              "Platform features and tool calls on top.",
              "Verify current pricing on Vapi's site."]),
            ("What a production call really costs",
             ["A short support call: a few minutes of telephony + a modest token count.",
              "A long or looping conversation: minutes × turns — the expensive shape.",
              "Retried failed calls bill minutes for nothing."]),
            ("How to control it",
             ["Per-agent ceilings on telephony and inference.",
              "Category rules separating the two lines.",
              "Velocity limits on retries."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Telephony minutes", "Per-call / daily ceiling"],
                ["LLM tokens", "Model selection + category cap"],
                ["Retries", "Velocity limit"],
                ["Tool calls", "Merchant allowlist"],
            ],
        ),
        faqs=[
            ("Is Vapi priced per minute?",
             "Yes — per-minute telephony plus LLM tokens. Verify current rates."),
            ("What drives Vapi bills most?",
             "Call volume and conversation length — both firewall-controllable."),
        ],
        related=[("Vapi integration", "/integrations/vapi"), ("Voice agents", "/use-cases/voice-agents"), ("sipi.bot vs Vapi", "/vs/vapi")],
    ),
    dict(
        slug="retell-pricing",
        title="How Much Does Retell Cost? — Voice Agent Pricing",
        desc="Retell pricing: per-minute voice agents plus LLM tokens. What it costs to run production voice and how to cap it.",
        h1="How Much Does Retell Cost?",
        lead="Retell bills per minute for voice agents with LLM tokens on top. Predictable per call — unless calls loop.",
        sections=[
            ("The pricing model",
             ["Per-minute telephony pricing for voice agents.",
              "LLM token costs per turn.",
              "Verify current pricing on Retell's site."]),
            ("What drives the bill",
             ["Call volume — the per-minute line scales directly.",
              "Conversation length — tokens per turn compound.",
              "Failed-call retries — billable minutes for nothing."]),
            ("How to control it",
             ["Per-agent ceilings, category rules, velocity limits."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Telephony minutes", "Per-call / daily ceiling"],
                ["LLM tokens", "Category cap"],
                ["Retries", "Velocity limit"],
            ],
        ),
        faqs=[
            ("Is Retell priced per minute?",
             "Yes — verify current rates."),
            ("Can I cap a voice campaign?",
             "Yes — per-agent rules per campaign."),
        ],
        related=[("sipi.bot vs Retell", "/vs/retell"), ("Voice agents", "/use-cases/voice-agents"), ("How to set spend limits", "/how-to/how-to-set-spend-limits")],
    ),
    dict(
        slug="fireflies-pricing",
        title="How Much Does Fireflies Cost? — Plans and AI Credits",
        desc="Fireflies pricing: per-seat plans with AI credits. What meeting capture costs and what the AI usage really adds.",
        h1="How Much Does Fireflies Cost?",
        lead="Fireflies is per-seat with AI credits. The seat price is predictable; the AI-credit burn is the variable.",
        sections=[
            ("The pricing model",
             ["Per-seat monthly plans with included AI credits.",
              "Heavy transcription/summarization usage consumes credits fast.",
              "Verify current pricing on Fireflies' site."]),
            ("What drives the bill",
             ["Seat count — the predictable line.",
              "AI usage per meeting — transcription minutes and summarization tokens."]),
            ("How to control it",
             ["Seats: right-size to active users. AI usage: the agent-side firewall governs transcription and summarization APIs."]),
        ],
        table=dict(
            headers=["Cost bucket", "How to control it"],
            rows=[
                ["Seats", "Right-size to active users"],
                ["AI credits", "Per-team usage ceilings"],
                ["Transcription APIs", "Firewall category rules"],
            ],
        ),
        faqs=[
            ("Is Fireflies worth it per seat?",
             "Depends on meeting volume — verify current pricing and usage patterns."),
            ("What's the agent angle?",
             "Meeting agents riding on transcription APIs are firewall-governed."),
        ],
        related=[("sipi.bot vs Fireflies", "/vs/fireflies"), ("Meeting agents", "/use-cases/meeting-agents"), ("How to monitor AI costs", "/how-to/how-to-monitor-ai-costs")],
    ),
]

FOR = [
    dict(
        slug="data-engineers",
        title="Data Pipeline Agent Spend Control | sipi.bot",
        desc="Data engineers: cap what data-pipeline and ETL agents spend on compute, connectors, and inference.",
        h1="Agent Spend Control for Data Engineers",
        lead="Your pipelines call paid connectors, compute, and inference at scale. A runaway sync loop is a bill you'll see in the data warehouse first.",
        sections=[
            ("Where data agents spend",
             ["Connector APIs billed per sync or per row.",
              "Compute for transforms and feature pipelines.",
              "Inference for enrichment and classification at volume.",
              "Data vendors per lookup."]),
            ("The failure modes",
             ["A sync retry loop multiplies per-sync charges.",
              "An enrichment loop re-processing the same rows.",
              "Unknown data vendors bypass procurement."]),
            ("Which rules to start with",
             ["Per-pipeline daily ceiling.",
              "Velocity limit on sync retries.",
              "Merchant allowlist for data vendors."]),
        ],
        table=dict(
            headers=["Data spend", "Control"],
            rows=[
                ["Connector APIs", "Per-pipeline ceiling"],
                ["Compute", "Category budget"],
                ["Enrichment", "Velocity limit"],
                ["Data vendors", "Merchant allowlist"],
            ],
        ),
        faqs=[
            ("Can I budget per pipeline?",
             "Yes — per-agent rules per pipeline."),
            ("Does it add latency to syncs?",
             "No — ~5 ms per check."),
        ],
        related=[("Data pipelines", "/for/data-pipelines"), ("ML engineers", "/for/ml-engineers"), ("DevOps automation", "/for/devops-automation")],
    ),
]

SECTORS = [
    dict(
        slug="telecom",
        title="AI Spend Control for Telecom | sipi.bot",
        desc="Telecom AI agents: network ops, customer care, and fraud bots that spend on data and inference at carrier scale.",
        h1="Spend Control for Telecom AI Agents",
        lead="Carriers run agents for network ops, customer care, and fraud — at subscriber scale. The spend scales with the subscriber base.",
        sections=[
            ("Where telecom agents spend",
             ["Customer-care agents hitting inference at call volume.",
              "Network-ops agents pulling telemetry and running diagnostics.",
              "Fraud agents querying databases per event.",
              "Document and compliance bots at scale."]),
            ("The failure modes",
             ["A care-agent retry loop multiplies inference.",
              "Overnight network-diagnostics runs without review.",
              "Unknown vendors bypass procurement."]),
            ("Which rules to start with",
             ["Per-team daily ceiling.",
              "Time-of-day rule for overnight runs.",
              "Merchant allowlist for data vendors."]),
        ],
        table=dict(
            headers=["Rule", "Why it matters in telecom"],
            rows=[
                ["Per-team ceiling", "Fleet-wide budget in one number"],
                ["Time-of-day rule", "Overnight runs need review"],
                ["Merchant allowlist", "Unvetted vendors blocked"],
            ],
        ),
        faqs=[
            ("Can I budget per line of business?",
             "Yes — per-agent rules per LOB."),
            ("Does it slow customer care?",
             "No — ~5 ms per check."),
        ],
        related=[("Customer support bots", "/use-cases/customer-support-bots"), ("Voice agents", "/use-cases/voice-agents"), ("How to implement spend controls", "/how-to/how-to-implement-spend-controls")],
    ),
]

BENCHMARKS = [
    dict(
        slug="agent-token-consumption-by-task",
        title="Agent Token Consumption by Task — The Honest Shape",
        desc="Token consumption by agent task type: support, coding, research, voice. The shape, not invented precision — measure yours.",
        h1="Agent Token Consumption by Task",
        lead="Token consumption follows the task: short support turns, long coding sessions, huge research contexts. Here's the honest shape — and why you must measure your own.",
        sections=[
            ("The shapes",
             ["Support turns: short contexts, repeated per ticket — volume-driven.",
              "Coding sessions: long multi-turn contexts, tool outputs — length-driven.",
              "Research tasks: huge contexts (documents, search results) — context-driven.",
              "Voice calls: tokens per turn across the conversation — both."]),
            ("The honest caveat",
             ["Exact token counts vary wildly by model, prompt, and tool design.",
              "The useful benchmark is YOUR audit log, not industry averages."]),
            ("What to do",
             ["Cap per-call spend so one oversized context can't blow the budget.",
              "Trim context, cache stable prefixes, and watch the log."]),
        ],
        table=dict(
            headers=["Task type", "Spend shape", "Primary control"],
            rows=[
                ["Support", "Short × volume", "Daily ceiling"],
                ["Coding", "Long sessions", "Velocity limit"],
                ["Research", "Big contexts", "Per-call cap"],
                ["Voice", "Minutes × turns", "Category + ceiling"],
            ],
        ),
        faqs=[
            ("Are these exact numbers?",
             "No — they're shapes. Measure yours with the audit log."),
            ("What's the biggest token sink?",
             "Context size on long tasks — cap per-call spend to contain it."),
        ],
        related=[("LLM context cost", "/benchmarks/llm-context-window-cost-comparison"), ("Cost per 1M tokens", "/benchmarks/cost-per-1m-tokens-2026"), ("How to reduce AI API costs", "/how-to/how-to-reduce-ai-api-costs")],
    ),
]

BEST = [
    dict(
        slug="best-ai-agent-frameworks",
        title="Best AI Agent Frameworks 2026 — Honest Comparison",
        desc="The agent frameworks teams actually build on in 2026: LangChain, CrewAI, Mastra, Letta, Pydantic AI, AG2. Honest criteria-based list with the spend angle.",
        h1="Best AI Agent Frameworks 2026",
        lead="The framework you pick shapes your agent spend. Here's the honest shortlist — by what teams actually build, not hype — and the spend angle on each.",
        sections=[
            ("The shortlist",
             ["LangChain / LangGraph — the ecosystem standard for complex agent workflows.",
              "CrewAI — role-based crews, parallel agents.",
              "Mastra — TypeScript-native agent framework.",
              "Letta — persistent-memory agents.",
              "Pydantic AI — typed, production-minded Python agents.",
              "AG2 (AutoGen) — multi-agent conversations.",
              "OpenAI Agents SDK — the OpenAI-native path."]),
            ("How to choose",
             ["Language (TS vs Python), ecosystem fit, and how you'll control spend.",
              "All of them let agents call tools — which means all of them need a spend gate."]),
            ("The spend angle",
             ["Every framework wires to the same firewall: HTTP, MCP, or CLI. The integration directory covers each."]),
        ],
        table=dict(
            headers=["Framework", "Best at", "Spend control"],
            rows=[
                ["LangChain/LangGraph", "Complex workflows", "MCP / HTTP"],
                ["CrewAI", "Parallel crews", "Shared ceiling"],
                ["Mastra", "TypeScript agents", "Guard tool"],
                ["Letta", "Persistent memory", "Daily ceiling"],
                ["Pydantic AI", "Typed Python", "Guard tool"],
                ["AG2", "Multi-agent", "Fleet budget"],
            ],
        ),
        faqs=[
            ("Which framework is best?",
             "Stack-dependent — language and ecosystem fit first. All need spend control."),
            ("Do you rank them?",
             "No — that's not honest. Match the framework to your stack; the firewall is framework-agnostic."),
        ],
        related=[("Integrations hub", "/integrations/"), ("Mastra integration", "/integrations/mastra"), ("Pydantic AI integration", "/integrations/pydantic-ai")],
    ),
]

FAQ = [
    dict(
        slug="can-ai-agents-pay-subscriptions",
        title="Can AI Agents Pay for Subscriptions?",
        desc="Yes — agents can subscribe to services, and that's a spend vector nobody budgets. How it happens and how to control it.",
        h1="Can AI Agents Pay for Subscriptions?",
        lead="Yes. An agent with a payment method can sign up for services — and subscription spend is the quietest line on any AI bill.",
        sections=[
            ("How it happens",
             ["Agents on payment rails (x402, AP2) can initiate recurring payments.",
              "Tool-using agents can subscribe to APIs and services mid-task.",
              "The subscription renews automatically — nobody reviews it."]),
            ("Why it's risky",
             ["Recurring spend compounds silently.",
              "A single agent action can create a monthly line item forever."]),
            ("The control",
             ["Merchant allowlist: only approved vendors can be paid, subscriptions included.",
              "Approval threshold: new subscriptions FLAG for review.",
              "Audit log: every subscription start is a logged decision."]),
        ],
        faqs=[
            ("Is agent-created subscription real?",
             "It's a documented spend vector — agents with payment capability can commit recurring spend."),
            ("How do I stop it?",
             "Allowlist the merchants agents may pay; everything else is BLOCKED or FLAGGED."),
        ],
        related=[("Red flags in subscriptions", "/redflags/red-flags-in-ai-agent-subscriptions"), ("Merchant allowlist", "/glossary/merchant-allowlist"), ("Agentic payment", "/glossary/agentic-payment")],
    ),
]

ANSWERS = [
    dict(
        slug="how-to-choose-a-spend-firewall",
        title="How to Choose a Spend Firewall",
        desc="The honest criteria for choosing a spend firewall: deterministic decisions, rule types, audit, pricing, and deployment.",
        h1="How to Choose a Spend Firewall",
        lead="Choosing a spend firewall is like choosing any control: you're buying decisions, not dashboards. Here are the questions that separate them.",
        sections=[
            ("The criteria",
             ["1. Decision path: deterministic rules or model-based? (Deterministic can't be injected.)",
              "2. Latency: what's the p95 decision time?",
              "3. Rule types: caps, velocity, allowlists, categories, time-of-day, approvals?",
              "4. Audit: is every decision logged with the rule that fired?",
              "5. Pricing: flat or metered? Any overage tier?",
              "6. Deployment: hosted, self-host, or both?",
              "7. Integration: HTTP, MCP, CLI — and your stack?"]),
            ("How to score",
             ["Weight by your priorities. For most teams: deterministic path, flat pricing, audit log."]),
        ],
        faqs=[
            ("Why does deterministic matter?",
             "A model-based decision path can be argued with or injected; rules can't."),
            ("What's the most underrated criterion?",
             "The audit log — it answers questions six months later."),
        ],
        related=[("Spend firewall RFP checklist", "/checklists/spend-firewall-rfp-checklist/"), ("Pricing questions", "/pricing-questions/"), ("Eval report", "/eval-report/")],
    ),
]

CHECKLISTS = [
    dict(
        slug="self-host-checklist",
        title="Self-Host Checklist",
        desc="The deployment checklist for self-hosting the MIT core: storage, health, keys, rules, and backups.",
        h1="Self-Host Checklist",
        lead="Self-hosting is free and full-featured — if you cover the ops basics. This checklist is the basics.",
        sections=[
            ("The checklist",
             ["1. Storage: SQLite store on a persistent volume?",
              "2. Health: is /health wired to your orchestrator?",
              "3. Keys: admin token rotated, per-agent keys created?",
              "4. Rules: caps, allowlist, velocity limits set?",
              "5. Network: HTTPS in front, no public admin routes?",
              "6. Backups: store backed up?",
              "7. Upgrades: can you pull and rebuild the image?",
              "8. Ownership: one person on call for it?"]),
        ],
        faqs=[
            ("What's the minimum?",
             "Persistent storage, health check, and rotated keys."),
            ("Is self-host production-ready?",
             "It's the same engine as hosted — readiness is your ops."),
        ],
        related=[("Self-host guide", "/self-hosted/"), ("Guide to self-hosting", "/guides/guide-to-self-hosting"), ("Self-host tutorial", "/tutorials/self-host-in-docker")],
    ),
]

# --- hub metadata -----------------------------------------------------------
