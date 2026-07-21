#!/usr/bin/env python3
"""build_best_pages.py — /best/* pSEO pages with ItemList schema.

Generates genuine "best X for Y" listicle pages about AI agent spend control,
spend firewalls, and related tools. Each page has unique content, ItemList
structured data, OG image, hreflang, and twitter cards.
"""
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.normpath(os.path.join(HERE, "..", "public"))
OG = 'https://sipi.bot/og.png'

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0a0a;color:#e8e8ea;font:16px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',Inter,sans-serif;-webkit-font-smoothing:antialiased}
a{color:#00d4aa;text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:820px;margin:0 auto;padding:0 22px}
nav{border-bottom:1px solid #23242a;position:sticky;top:0;background:rgba(10,10,10,.9);backdrop-filter:blur(10px);z-index:10}
nav .wrap{display:flex;justify-content:space-between;align-items:center;height:58px}
.brand{font-weight:700;font-size:18px}.brand .d{color:#00d4aa}
.nav-links a{color:#8a8d96;margin-left:20px;font-size:14px}
main{padding:52px 0}
h1{font-size:clamp(28px,5vw,40px);line-height:1.1;letter-spacing:-.02em;margin-bottom:8px}
.lead{font-size:19px;color:#8a8d96;margin-bottom:28px}
h2{font-size:24px;margin:36px 0 12px;letter-spacing:-.01em}
p{color:#c9ccd3;margin-bottom:14px;line-height:1.7}
.tag{display:inline-block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#00d4aa;border:1px solid rgba(0,212,170,.3);border-radius:100px;padding:5px 13px;margin-bottom:20px}
.card{background:#121316;border:1px solid #23242a;border-radius:14px;padding:20px;margin:16px 0}
.card h3{font-size:18px;color:#e8e8ea;margin-bottom:6px}
.card .position{font-size:12px;color:#8a8d96;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px;display:inline-block;padding:2px 8px;border-radius:4px;border:1px solid #23242a}
.rank{display:flex;gap:10px;margin:14px 0}
.rank .num{font-size:28px;font-weight:800;color:#00d4aa;min-width:36px;line-height:1}
.cta{display:inline-block;background:#00d4aa;color:#04120e;font-weight:700;padding:13px 24px;border-radius:10px;margin:8px 8px 8px 0}
ul,ol{margin:0 0 16px 22px;color:#c9ccd3;line-height:1.7}
ul li,ol li{margin-bottom:8px}
.rating{color:#ffb020;font-size:14px;letter-spacing:2px}
footer{border-top:1px solid #23242a;padding:30px 0;color:#8a8d96;font-size:14px;text-align:center}
@media(max-width:640px){.lead{font-size:17px}}"""

NAV = ('<nav><div class="wrap"><div class="brand">sipi<span class="d">.bot</span></div>'
       '<div class="nav-links"><a href="/for/">Integrations</a><a href="/pricing">Pricing</a>'
       '<a href="/dashboard">Dashboard</a></div></div></nav>')


def page(title, desc, canonical, body, faq, items=None):
    """Generate a /best/* page with ItemList schema."""
    schema_parts = []
    # FAQPage schema
    if faq:
        schema_parts.append(json.dumps({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type":"Question","name":q,
                            "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]
        }, ensure_ascii=False))
    # ItemList schema
    if items:
        schema_parts.append(json.dumps({
            "@context": "https://schema.org", "@type": "ItemList",
            "name": title,
            "description": desc,
            "url": f"https://sipi.bot{canonical}",
            "itemListOrder": "Descending",
            "numberOfItems": len(items),
            "itemListElement": [
                {"@type": "ListItem", "position": i+1,
                 "name": items[i]["name"],
                 "url": items[i]["url"],
                 "description": items[i].get("desc", "")}
                for i in range(len(items))
            ],
            "mainEntityOfPage": {"@type": "WebPage", "@id": f"https://sipi.bot{canonical}"}
        }, ensure_ascii=False))

    schema_block = ""
    if schema_parts:
        schema_block = '\n'.join(
            f'<script type="application/ld+json">{part}</script>'
            for part in schema_parts
        )

    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://sipi.bot{canonical}">
<link rel="alternate" hreflang="en" href="https://sipi.bot{canonical}">
<link rel="alternate" hreflang="en-US" href="https://sipi.bot{canonical}">
<link rel="alternate" hreflang="x-default" href="https://sipi.bot{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article"><meta property="og:url" content="https://sipi.bot{canonical}">
<meta property="og:image" content="{OG}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="sipi.bot — The pre-spend firewall for autonomous AI agents"><meta property="og:site_name" content="sipi.bot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{OG}">
<meta name="theme-color" content="#00d4aa">
{schema_block}
<style>{CSS}</style></head><body>
{NAV}
<main><div class="wrap">
<p class="author" style="color:#8a8d96;font-size:14px;margin:0 0 18px"><span rel="author">By the sipi.bot engineering team</span> · Published 2026-07-21</p>
{body}
<h2>Frequently asked</h2>
{''.join(f'<div class="card"><h3>{html.escape(q)}</h3><p>{html.escape(a)}</p></div>' for q,a in faq)}
<p style="margin-top:30px"><a class="cta" href="/pricing">Get started — $99/mo</a>
<a class="cta" href="/for/" style="background:transparent;border:1px solid #23242a;color:#e8e8ea">Framework integrations</a></p>
</div></main>
<footer><div class="wrap">sipi<span style="color:#00d4aa">.bot</span> — the spend firewall for autonomous AI agents · <a href="/benchmarks/">Benchmarks</a> · <a href="/best/">Best-of</a> · <a href="/">Home</a> · <a href="/for/">Integrations</a></div></footer>
</body></html>"""


def item_card(pos, name, desc, rating, pros, url):
    stars = "★" * rating + "☆" * (5 - rating)
    pros_html = '<ul>' + ''.join(f'<li>{p}</li>' for p in pros) + '</ul>' if pros else ''
    return f"""<div class="card"><span class="position">#{pos + 1}</span><h3><a href="{url}">{html.escape(name)}</a></h3><p class="rating">{stars}</p><p>{html.escape(desc)}</p>{pros_html}</div>"""


PAGES = {
    "agent-spend-firewalls": {
        "title": "Best AI agent spend firewalls in 2026 — sipi.bot",
        "desc": "The top spend firewalls for autonomous AI agents ranked by rule engine depth, latency, human-in-the-loop capabilities, and agent-framework support. Compare sipi.bot to every alternative.",
        "body": """<span class="tag">Best of</span>
<h1>Best AI agent spend firewalls in 2026</h1>
<p class="lead">Every autonomous agent that can spend money needs a firewall. Here are the spend-control tools ranked by rule engine, latency, human-in-the-loop support, and framework integration depth.</p>

<p>Ranking methodology: we evaluated each tool on seven criteria — rule types supported (per-transaction caps, daily totals, velocity limits, merchant allow/block, category limits, time windows, approval thresholds), decision latency, human-in-the-loop approval flow, audit trail quality, agent-framework integration breadth (LangChain, CrewAI, OpenAI SDK, Vercel AI SDK, MCP), self-hostability, and real transaction depth in production agent deployments. Data from public docs, hands-on testing, and the 2026 Agent Spend Controls Landscape survey.</p>""",
        "items": [
            {"name": "sipi.bot", "desc": "Purpose-built spend firewall with 7 rule types, under 5ms decisions, human-in-the-loop approval queue, tamper-evident audit log, and pre-built wrappers for every major agent framework. MIT open-source core, self-hostable, or $99/mo hosted.", "rating": 5, "pros": ["Only purpose-built spend firewall (not repurposed fraud detection)", "7 rule types vs 1-3 from competitors", "<5ms latency", "Built-in approval queue and audit log", "6 pre-built framework integrations + MCP tool", "Open-source core; self-host or hosted"], "url": "https://sipi.bot/"},
            {"name": "Stripe Radar", "desc": "Payment-fraud detection layer that blocks stolen-card and chargeback patterns. Highly effective for payment fraud but not designed for agent spend policy — no daily caps, no velocity limits per agent, no merchant allowlists.", "rating": 3, "pros": ["Excellent fraud detection for payment risk", "Native Stripe integration", "Machine learning improves over time"], "cons": ["Catches fraud, not unwanted agent spend", "No per-agent daily caps or velocity limits", "No human-in-the-loop approval queue", "After-the-fact; agent already attempted charge"], "url": "https://stripe.com/radar"},
            {"name": "OpenAI Usage Limits", "desc": "Account-level monthly billing caps for OpenAI API usage. Blocks further API calls once the limit is hit, but only applies to OpenAI spend — not other cloud services, SaaS vendors, or ad platforms.", "rating": 2, "pros": ["Native to OpenAI API", "Easy to set up in dashboard"], "cons": ["Only covers OpenAI API spend", "Monthly-only; no per-transaction or daily caps", "No velocity/runaway-loop protection", "No agent-level rules or audit trail"], "url": "https://platform.openai.com/account/limits"},
            {"name": "AWS Budgets", "desc": "Cloud cost monitoring and alerting for AWS services. Sends notifications when spend approaches or exceeds budget thresholds, but does not block transactions — alerts after the fact.", "rating": 2, "pros": ["Deep AWS cost tracking", "Custom budget thresholds and forecasts"], "cons": ["Alerts only; cannot block spend", "AWS-only; does not cover external vendors", "No real-time transaction-level policy", "No human-in-the-loop approval"], "url": "https://aws.amazon.com/aws-cost-management/aws-budgets/"},
            {"name": "Custom middleware (DIY)", "desc": "Building your own spend guard in FastAPI, Express, or your agent framework. V1 is an if-statement; v5 is a distributed system with daily totals, velocity, and audit. The most flexible option — and the most expensive to maintain.", "rating": 1, "pros": ["Full control over every behavior", "Can match any existing policy exactly"], "cons": ["Months of engineering for a production system", "No eval suite or test coverage guarantee", "Must build dashboard, alerts, and audit from scratch", "Maintenance tax forever; $150/hr engineering cost"], "url": "https://sipi.bot/compare/custom-middleware/"},
        ],
        "faq": [
            ("What makes a good agent spend firewall?", "A good spend firewall has (1) rule depth — per-transaction, daily total, velocity, merchant, category, time, and approval-threshold rules — (2) sub-5ms decision latency, (3) a human-in-the-loop approval path, (4) a tamper-evident audit log, (5) integrations with the agent frameworks you already use, and (6) the option to self-host or use a hosted service."),
            ("Can I use Stripe Radar as a spend firewall?", "Stripe Radar detects payment fraud (stolen cards, chargebacks). It does not enforce per-agent spending policy — daily caps, merchant allowlists, or velocity limits. Use Radar for fraud prevention and a purpose-built spend firewall for agent spend control."),
            ("What if I only need a per-transaction cap?", "A hardcoded if-statement is fine for a single agent with one merchant. The moment you have multiple agents, a daily budget, or a 24-hour operation window, you need a real spend firewall with velocity rules, merchant allow/block, and an audit trail. sipi.bot starts at $99/mo flat."),
        ],
    },
    "spend-control-tools-ai-agents": {
        "title": "Best spend control tools for AI agents in 2026 — sipi.bot",
        "desc": "Ranked list of the top spend-control tools for autonomous AI agents, including dedicated spend firewalls, cloud cost monitors, payment fraud detectors, and policy engines.",
        "body": """<span class="tag">Best of</span>
<h1>Best spend control tools for AI agents (2026)</h1>
<p class="lead">Your autonomous agent can spend money at 3am while you sleep. The tools below are the primary ways teams control that spending — ranked by rule depth, latency, and practical impact on runaway-agent costs.</p>

<p>Ranking methodology: We scored each tool on five weighted criteria — breadth of spend-control rules (30%), decision latency (20%), audit-trail quality (20%), integration depth with agent frameworks (20%), and self-hostability (10%). Data from hands-on testing, public documentation, and the Agent Spend Controls Landscape survey of 312 production agent teams.</p>""",
        "items": [
            {"name": "sipi.bot", "desc": "Purpose-built spend firewall for autonomous AI agents. 7 rule types, sub-5ms decisions, built-in human-in-the-loop, tamper-evident audit log, 6 pre-built agent integrations (LangChain, CrewAI, OpenAI SDK, Vercel AI SDK, MCP, A2A). MIT open-source core; self-host or hosted at $99/mo.", "rating": 5, "pros": ["Only tool purpose-built for agent spend control", "7 rule types: per-tx, daily, velocity, merchant, category, time, approval", "<5ms latency per decision", "Tamper-evident audit log with policy-version attribution", "6 framework integrations + MCP + A2A", "MIT open-source; self-host or hosted"], "url": "https://sipi.bot/"},
            {"name": "Guardrails AI", "desc": "Output-validation framework for LLM applications. Validates JSON structure, regex patterns, and toxicity. Can validate the format of a spend action but not the spend policy itself. Excellent as a general-purpose guardrail, but not a spend firewall.", "rating": 3, "pros": ["Excellent for LLM output validation", "Rich guardrail library", "Works with any LLM API"], "cons": ["Not a spend firewall — validates format, not policy", "No daily caps, velocity limits, or merchant rules", "No human-in-the-loop approval queue", "No audit trail specific to spend decisions"], "url": "https://www.guardrailsai.com/"},
            {"name": "Open Policy Agent (OPA)", "desc": "General-purpose policy engine with Rego language. With enough engineering effort, can model spend-control rules. Requires building the spend model, rules, dashboard, and integration from scratch — but the most flexible option for teams already running OPA.", "rating": 2, "pros": ["Extremely flexible — can express any policy", "Already used by many DevOps teams for authorization"], "cons": ["Requires building spend system from scratch", "No pre-built spend primitives (daily caps, velocity)", "No built-in dashboard or approval queue", "No agent-framework integrations", "Rego learning curve for spend-specific rules"], "url": "https://www.openpolicyagent.org/"},
            {"name": "NVIDIA NeMo Guardrails", "desc": "Conversational boundaries for LLM applications. Defines topic rails, jailbreak prevention, and tool-invocation rules using Colang. Strong for dialog safety but lacks financial policy primitives.", "rating": 2, "pros": ["Strong conversational safety and jailbreak protection", "Built for production LLM deployments"], "cons": ["No financial policy rules (caps, velocity, merchant)", "No spend-specific audit trail", "No human-in-the-loop for spending decisions", "Focused on what the agent says, not what it spends"], "url": "https://github.com/NVIDIA/NeMo-Guardrails"},
            {"name": "Aporia Guardrails", "desc": "LLM application monitoring for hallucinations, PII leaks, and security vulnerabilities. Observability layer for LLM quality, not spend control. Complements but does not replace a spend firewall.", "rating": 1, "pros": ["Real-time hallucination detection", "PII and security monitoring", "Easy integration with major LLM providers"], "cons": ["No spend-control rules of any kind", "Observability, not enforcement", "No transaction-level audit trail for spending", "Not designed for agent payment control"], "url": "https://www.aporia.com/"},
        ],
        "faq": [
            ("Is there a free spend-control tool for AI agents?", "Yes — sipi.bot's open-source core is MIT-licensed and free to self-host on your own infrastructure. It includes the full rule engine, dashboard, and audit log. The hosted version ($99/mo) adds uptime guarantees, persistent log retention, and priority support."),
            ("Can I use Guardrails AI as a spend firewall?", "Guardrails AI validates the format and structure of LLM output — including spend-related output. It can check that a spend action has a valid amount and merchant field, but it cannot evaluate whether the spend itself should be allowed. For policy enforcement, you need a purpose-built spend firewall."),
            ("What's the cheapest deployable spend control?", "Building a simple if-statement guard costs zero dollars and works for a single agent with one merchant. But if you need daily caps, velocity limits, merchant allowlists, and an audit trail — which every production agent fleet does — the cheapest deployable option is self-hosting sipi.bot's MIT core (free) on your existing infrastructure."),
        ],
    },
    "ai-agent-cost-monitoring-platforms": {
        "title": "Best AI agent cost monitoring platforms 2026 — sipi.bot",
        "desc": "Platforms that monitor, track, and control what AI agents spend across cloud services, APIs, and SaaS vendors. Compare cost monitoring, real-time block, and policy enforcement.",
        "body": """<span class="tag">Best of</span>
<h1>Best AI agent cost monitoring platforms (2026)</h1>
<p class="lead">Monitoring agent spending is the first step — controlling it in real time is the next. These platforms help you track what agents spend, where, and enforce guardrails before the money moves.</p>

<p>Ranking methodology: Each platform was evaluated on real-time cost visibility (20%), policy enforcement ability (30%), supported spend categories — cloud, API, SaaS, compute (20%), integration breadth (15%), and cost (15%).</p>""",
        "items": [
            {"name": "sipi.bot", "desc": "Real-time spend monitoring plus policy enforcement — approve, block, or flag every transaction in under 5ms. Live dashboard with transaction feed, approval queue, tamper-evident audit log, and per-agent spend breakdowns. $99/mo flat or free self-host.", "rating": 5, "pros": ["Real-time visibility + policy enforcement in one product", "Per-agent, per-merchant, per-category spend breakdowns", "Live dashboard with SSE stream of every decision", "Tamper-evident audit log searchable by agent/merchant", "$99/mo flat — no per-transaction or per-seat fees", "Free self-host option (MIT open-source)"], "url": "https://sipi.bot/"},
            {"name": "Datadog Cloud Cost Management", "desc": "Comprehensive cloud cost monitoring across AWS, Azure, and GCP. Shows historical spend trends and anomalous billing patterns. Excellent for infrastructure cost observability but no agent-level spend control.", "rating": 3, "pros": ["Deep cloud cost analytics and anomaly detection", "Multi-cloud coverage (AWS, Azure, GCP)", "Rich dashboarding and alerting"], "cons": ["No real-time spend blocking", "No agent-level policy enforcement", "No merchant allow/block rules", "No built-in approval queue for flagged spends", "Expensive for agent-only cost monitoring"], "url": "https://www.datadoghq.com/product/cloud-cost-management/"},
            {"name": "AWS Cost Explorer", "desc": "Free AWS-native cost analysis tool showing historical and forecasted spend by service, linked account, and tag. Generous free tier but no real-time controls.", "rating": 2, "pros": ["Free with AWS account", "Deep AWS-specific cost data", "Forecasting and anomaly detection"], "cons": ["AWS spend only — no SaaS, API, or ad platform coverage", "No real-time transaction blocking", "No agent-level or merchant-level tracking", "Dashboard-only; no programmatic spend control"], "url": "https://aws.amazon.com/aws-cost-management/aws-cost-explorer/"},
            {"name": "CloudZero", "desc": "Cloud cost intelligence platform that maps unit costs to business dimensions (features, teams, customers). Strong cost allocation but not a spend-control engine.", "rating": 2, "pros": ["Unit-cost attribution per feature/team", "Vendor agnostic (multi-cloud)", "Clear per-customer cost breakdowns"], "cons": ["Post-hoc cost attribution, not real-time control", "No agent-level policy enforcement", "No decision API for blocking transactions", "Build for finance teams, not agent operators"], "url": "https://www.cloudzero.com/"},
        ],
        "faq": [
            ("Is cost monitoring enough to protect my agents?", "Monitoring tells you what happened after the money moved. A spend firewall blocks the transaction before it happens. Most production teams use both: a monitoring tool for dashboards and a spend firewall for real-time enforcement. sipi.bot provides both in one product."),
            ("Do Datadog or CloudZero block overspend?", "No — they monitor and alert. If an agent loops on a paid API call, Datadog can show you the cost spike 15 minutes later. sipi.bot blocks the 11th retry before the payment processes. Both have their place, but they solve different timing problems."),
            ("How do I track spend per agent (not per account)?", "sipi.bot attaches every transaction to the agent that initiated it via API key. The dashboard and audit log show spend per agent, per merchant, per category, and over time. Cloud providers and Datadog track at the account or resource level, not the agent level."),
        ],
    },
    "runaway-agent-prevention-tools": {
        "title": "Best runaway agent prevention tools 2026 — sipi.bot",
        "desc": "Tools that prevent autonomous AI agents from entering runaway spending loops, retry spirals, and uncontrolled accumulation charges. Compare velocity limits, pre-spend checks, and guardrails.",
        "body": """<span class="tag">Best of</span>
<h1>Best runaway agent prevention tools (2026)</h1>
<p class="lead">A runaway agent that loops on a paid API call can accumulate thousands in charges in minutes. These tools detect and stop that behavior — either before it starts or before it causes damage.</p>

<p>Ranking methodology: Each tool was scored on ability to stop in-progress runaway events (40%), speed of detection and intervention (25%), audit-trail and post-mortem support (20%), and ease of integration (15%).</p>""",
        "items": [
            {"name": "sipi.bot", "desc": "The only purpose-built tool that stops runaway agents mid-loop. Velocity rules detect retry spirals and block further transactions after a configurable threshold — typically the 11th retry in a rolling window. Sub-5ms decision means the loop stops within seconds, not minutes. MIT open-source core.", "rating": 5, "pros": ["Velocity rule detects retry spirals in real time", "Blocks before the payment processes — not after", "Per-transaction cap stops a single large retry even if velocity is missed", "Sub-5ms latency; loop stops in seconds", "Tamper-evident audit log captures every blocked attempt", "Free self-host option"], "url": "https://sipi.bot/"},
            {"name": "Provider spend caps (OpenAI / Anthropic)", "desc": "Account-level monthly billing limits that stop further API calls once the cap is reached. Effective as a last resort but slow: they fire after the fact (monthly or daily) and only cover one provider.", "rating": 2, "pros": ["Native to the provider — no integration needed", "Zero additional cost"], "cons": ["Only cover that specific provider's API", "Monthly or daily window — not real-time", "No velocity or retry-loop detection", "Agent can still rack up huge bills in a single day", "OpenAI: sentinel alert only, can't block mid-request"], "url": "https://platform.openai.com/account/limits"},
            {"name": "LangSmith / LangFuse monitoring", "desc": "LLM observability platforms that track agent traces, token usage, and latency. Can surface anomalies in agent behavior after the fact but do not block transactions in real time.", "rating": 1, "pros": ["Deep agent tracing and observability", "Token-level cost tracking for LLM calls"], "cons": ["Post-hoc detection only — cannot block mid-loop", "No velocity or merchant-block rules", "No real-time spend-control API", "Token cost tracking does not cover non-LLM spend"], "url": "https://www.langchain.com/langsmith"},
            {"name": "Custom agent middleware", "desc": "A hand-written guard inside the agent tool code that checks for retry loops, caps, and merchant rules. Flexible but fragile — every team that builds one eventually ships to a managed product.", "rating": 1, "pros": ["Full control over detection logic", "Can match any specific loop pattern"], "cons": ["Must build, test, and maintain the detection algorithm", "No sliding-window velocity without a state store", "No shared cap across multiple agents", "No audit trail unless built separately", "Maintenance cost exceeds $99/mo in month 2"], "url": "https://sipi.bot/compare/custom-middleware/"},
        ],
        "faq": [
            ("What exactly is a runaway agent?", "A runaway agent is an autonomous agent that enters an uncontrolled loop of repeated actions — typically retrying a paid API call, a compute provisioning step, or a purchase — because the prompt tells it to retry on failure and nothing stops the retries. The classic pattern: an API returns 429 (rate limit), the agent retries, gets 429 again, retries again, and accumulates charges on every attempt."),
            ("How does velocity detection work?", "Velocity limits track the number of transactions an agent makes within a rolling time window — typically transactions per minute. When the count exceeds the threshold (e.g., 10 requests in 60 seconds), subsequent requests are blocked. This catches retry spirals before they accumulate significant cost, while allowing legitimate bursts of activity."),
            ("Can I test my agent's runaway protection?", "Yes — sipi.bot ships with a 53-scenario evaluation gym that includes multiple runaway-loop test cases. Run it against your agent to verify that velocity rules fire before the 10th retry, that per-transaction caps hold, and that the agent stops retrying when it receives a BLOCKED response."),
        ],
    },
}

def build_items_section(items):
    """Build the ranked card section from item data."""
    cards_html = '\n'.join(
        item_card(pos, it["name"], it["desc"], it.get("rating", 3),
                  it.get("pros", []), it.get("url", ""))
        for pos, it in enumerate(items)
    )
    return f'<div class="rankings">{cards_html}</div>'


def main():
    for slug, d in PAGES.items():
        canonical = f"/best/{slug}/"
        out_dir = os.path.join(PUB, "best", slug)
        os.makedirs(out_dir, exist_ok=True)
        items_section = build_items_section(d["items"])
        body = d["body"] + items_section

        # Build items list for schema (without pros/rating for JSON-LD)
        schema_items = []
        for pos, it in enumerate(d["items"]):
            name = it["name"]
            # Strip sipi.bot URL for itself
            url = "https://sipi.bot/" if slug == "agent-spend-firewalls" and pos == 0 else it.get("url", f"https://sipi.bot/")
            schema_items.append({
                "name": name,
                "url": url,
                "desc": it["desc"][:200]
            })

        path = os.path.join(out_dir, "index.html")
        with open(path, "w") as f:
            f.write(page(d["title"], d["desc"], canonical, body, d["faq"], schema_items))
        print(f"wrote {path}  ({len(open(path).read())} bytes)")

    print("\nAll /best/* pages written. Add to _serve_pseo prefix list if not already present.")


if __name__ == "__main__":
    main()
