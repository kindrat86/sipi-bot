#!/usr/bin/env python3
"""pSEO expansion for sipi.bot - fills thin page types."""
import os, json
from datetime import date

BASE = os.path.expanduser("~/projects/sipi-bot")
TODAY = date.today().isoformat()
DOMAIN = "sipi.bot"
CANONICAL = f"https://{DOMAIN}"

CANOPY = "Sipi Bot"

PAGES = {
    "scenarios": [
        ("agent-budget-breach", "AI Agent Budget Breach Scenario", [
            "What happens when an AI agent exceeds its budget ceiling? This scenario walks through the escalation flow: the agent receives a budget exceeded error, triggers an alert to the human operator, and defaults to read-only mode pending approval.",
            "This is one of the most common failure modes in agent spending. Sipi Bot's circuit breaker automatically detects the breach, logs the incident, and prevents further spending until the ceiling is reset.",
        ], [("How does the circuit breaker trigger?", "When total spend in a period hits the configured ceiling, Sipi Bot immediately blocks all further agent payments and sends a notification via email, Slack, or webhook.")]),

        ("unauthorized-api-call", "Unauthorized API Call Blocking Scenario", [
            "An agent attempts to call an API endpoint that isn't on its allowlist. Sipi Bot intercepts the call, logs the attempt, and returns an unauthorized error to the agent.",
            "This scenario tests the merchant allowlist enforcement and helps agents learn which endpoints are permitted without exposing billing systems to unauthorized charges.",
        ], [("Can agents request additional endpoints?", "Yes. The blocked event is logged with the endpoint details. An admin can review and approve new endpoints via the dashboard, automatically updating the allowlist.")]),

        ("runaway-agent-loop", "Runaway Agent Loop Detection Scenario", [
            "An agent enters a loop, repeatedly calling the same API endpoint and racking up costs. Sipi Bot detects the pattern (same endpoint + same parameters + excessive calls) and auto-throttles the agent.",
            "The velocity cap kicks in: if an agent makes more than N calls per minute, subsequent calls are queued with exponential backoff. The human operator is alerted to investigate the loop.",
        ], [("How many calls trigger the velocity cap?", "Default is 10 calls per minute per agent. Configurable per agent profile. The cap prevents silent runaway costs from loop bugs.")]),

        ("agent-key-compromise", "Agent API Key Compromise Scenario", [
            "An agent's API key is leaked or compromised. Sipi Bot detects anomalous usage (unusual endpoints, changed geo-location, different agent behavior patterns) and forces a key rotation.",
            "The compromised key is immediately revoked, a new key is issued, the incident is logged, and the human operator is notified. All spending under the compromised key is flagged for audit.",
        ], [("How does Sipi Bot detect anomalous usage?", "It builds a baseline of normal agent behavior patterns (endpoints called, time of day, request volume). When usage deviates significantly, it flags the incident for human review.")]),

        ("multi-tenant-billing-breach", "Multi-Tenant Billing Isolation Breach Scenario", [
            "One tenant's agent attempts to spend against another tenant's budget. Sipi Bot enforces strict tenant isolation: each agent's spending is tied to its tenant's wallet, and cross-tenant charges are blocked at the routing layer.",
            "The isolation is enforced at every payment attempt — not just at settlement. This prevents both accidental misrouting and intentional attempts to use another tenant's budget.",
        ], [("Can one tenant share budget with another?", "Only if explicitly configured via the shared budget feature. By default each tenant's budget is isolated. Shared budgets require admin approval and create a separate audit trail.")]),
    ],

    "redflags": [
        ("sudden-spike-in-small-payments", "Sudden Spike in Micro-Payments", [
            "A sudden increase in many small payments from a single agent is a classic sign of a run-away loop or exploitation. Red flag when: daily payment count exceeds 10x the 7-day average.",
            "This pattern often precedes budget breaches. Sipi Bot flags it immediately and throttles the agent if the spike continues for more than 5 consecutive minutes.",
        ], [("What's considered a micro-payment?", "Payments under $0.50 per transaction. An agent calling an LLM repeatedly with small prompts can rack up $100+ in minutes without triggering a single-payment limit.")]),

        ("off-hours-billing-activity", "Off-Hours Billing Activity Spike", [
            "Agents billing outside their normal operating hours is suspicious. A 3x increase in off-hours activity compared to baseline may indicate compromise or misconfiguration.",
            "Sipi Bot flags off-hours spikes for human review. If compounded with other anomalies (new endpoint, different response size), the agent may be automatically paused.",
        ], [("What counts as off-hours?", "Configurable per agent or tenant. Default is 10 PM — 6 AM in the agent's configured timezone. Different rules apply to global agents that operate 24/7.")]),

        ("new-endpoint-high-volume", "New Endpoint with High-Volume Spend", [
            "An agent suddenly starts calling a new API endpoint at high volume — significant because it's outside the agent's normal behavior pattern.",
            "Sipi Bot's velocity cap applies per-new-endpoint. The agent is limited to 5 calls/minute on new endpoints for the first 24 hours, preventing runaway costs on newly configured API integrations.",
        ], [("How does Sipi Bot distinguish new from existing endpoints?", "It tracks all endpoints an agent has called in the past 30 days. Any endpoint not in that history is treated as 'new' and subject to stricter thresholds.")]),

        ("payment-to-previously-failed-vendor", "Payment to Unknown or Previously Failed Vendor", [
            "An agent attempting payment to a vendor it has never used before, or to one where prior attempts failed, warrants scrutiny. Could indicate a hallucinated API endpoint or compromised routing.",
            "Sipi Bot blocks payments to unknown vendors by default. Admins must explicitly approve new vendor relationships. This prevents both accidental spending and malicious exploitation.",
        ], [("Can agents discover new vendors dynamically?", "Not by default. New vendors must be pre-approved by an admin. For approved discovery scenarios, agents can request vendor approval through the policy API.")]),
    ],

    "calculators": [
        ("agent-cost-calculator", "AI Agent Cost Calculator", [
            "Estimate the monthly cost of running AI agents. Enter your expected API calls per day, average tokens per request, and which models you're using.",
            "This calculator helps you budget for agent deployment before you start building. Includes estimates for GPT-4o, Claude Sonnet, and DeepSeek models.",
        ], [("Is usage-based or fixed pricing better for agents?", "Usage-based pricing aligns costs with value — you pay only for successful agent actions. Fixed pricing works better for predictable workloads with consistent call volumes.")]),

        ("runaway-cost-calculator", "Runaway Agent Cost Calculator", [
            "What would a runaway agent cost you? Enter your model, API pricing, and a conservative runaway scenario (e.g., 1000 calls/hour for 8 hours).",
            "See the potential damage from a loop bug, compromised key, or misconfigured retry logic. Then see how Sipi Bot's circuit breakers and velocity caps would have stopped it.",
        ], [("What's the most common runaway cost scenario?", "LLM API calls in a retry loop. An agent that gets rate-limited retries immediately, compounding the problem. Sipi Bot's exponential backoff prevents this.")]),

        ("budget-sizing-calculator", "Agent Budget Sizing Calculator", [
            "How much budget does your agent need? Enter expected usage, growth rate, and risk tolerance. Get recommended daily, weekly, and monthly ceilings.",
            "The calculator considers both normal usage patterns and burst scenarios (e.g., product launches, traffic spikes). It recommends buffering 30% above projected peak usage.",
        ], [("Should budgets be per-agent or per-team?", "Both. Set a per-agent daily ceiling to prevent individual runaways, and a per-team monthly budget to control overall spend. Sipi Bot supports both with hierarchical enforcement.")]),
    ],

    "guides": [
        ("agent-spend-governance", "AI Agent Spend Governance Guide", [
            "Spend governance for AI agents is fundamentally different from human employee expense management. Agents operate at machine speed, can make thousands of decisions per minute, and don't have the judgment to distinguish normal from anomalous spending.",
            "Key principles of agent spend governance: (1) Default-deny — agents should have zero spending capacity until explicitly granted, (2) Least-privilege — agents should only be allowed to spend on the specific API endpoints they need, (3) Defense in depth — multiple independent safeguards (budgets, velocity caps, allowlists) rather than a single gate.",
            "Sipi Bot implements all three principles with an enterprise-grade policy engine. Every spend decision is evaluated against budget ceilings, merchant allowlists, velocity caps, and anomaly detection — all in under 100ms.",
        ], [("What's the minimum governance setup for production agents?", "At minimum: a daily budget ceiling, a merchant allowlist with exactly the endpoints the agent needs, and a notification webhook for any blocked transaction."), ("How does agent spend governance differ from API key management?", "API key management controls access; spend governance controls cost. An agent with a valid API key can still rack up unlimited costs. Sipi Bot separates authentication from authorization at the payment level.")]),

        ("circuit-breakers-for-ai-agents", "Circuit Breakers for AI Agents", [
            "A circuit breaker is an automatic switch that stops an agent from spending after it exceeds a threshold. Think of it as a fuse for your agent's budget — once blown, it stays off until manually reset.",
            "Why circuit breakers matter: LLM API calls cost money, and loops happen. A single bug in an agent's reasoning loop can burn $1,000+ in minutes. Circuit breakers stop this instantly.",
            "Sipi Bot circuit breakers are configurable per agent, per team, and per project. You can set daily, weekly, and monthly ceilings with optional auto-reset (reduced ceiling) or manual-reset (full stop) behavior.",
        ], [("Should all agents have circuit breakers?", "Every agent with spending capacity needs at least one circuit breaker. The safest minimum is a daily ceiling at 150% of expected daily spend."), ("What happens after a circuit breaker trips?", "The agent receives a block response on the next payment attempt. The human operator gets an alert with the spending breakdown. The ceiling can be reset via dashboard or API.")]),

        ("merchant-allowlists", "Merchant Allowlists for AI Agents", [
            "A merchant allowlist is a restrictively curated list of API endpoints an agent is allowed to pay. Any payment attempt to an endpoint not on the list is automatically blocked.",
            "The allowlist is the single most effective control against agent payment abuse. Even a compromised agent cannot spend on unapproved endpoints. Combined with circuit breakers, it creates a defense-in-depth payment security model.",
            "Sipi Bot's allowlist supports wildcards (e.g., api.openai.com/v1/chat/completions), rate limits per endpoint, and time-based access (only allow billing during business hours).",
        ], [("How restrictive should allowlists be?", "As restrictive as possible. Start with exactly the endpoints the agent needs. Add new endpoints as requirements emerge, not preemptively."), ("Can agents request new allowlist entries?", "Yes, through Sipi Bot's policy API. The request is logged, and an admin can approve it via the dashboard. This allows dynamic scaling without compromising security.")]),

        ("velocity-caps", "Velocity Caps for AI Agent Spending", [
            "A velocity cap limits how many payments an agent can make in a given time window. Unlike a budget ceiling (total spend), a velocity cap limits the rate of spending.",
            "Velocity caps prevent the 'death by a thousand cuts' scenario where an agent makes thousands of micro-payments below the single-transaction limit. Default: 10 payments per minute per agent.",
            "Sipi Bot applies velocity caps at the agent, endpoint, and tenant level. An agent hitting the velocity cap gets automatic exponential backoff — retry intervals double with each attempt.",
        ], [("What's the right velocity cap for my agent?", "Start at 10 calls/minute per endpoint. Monitor for 1-2 weeks. Adjust based on actual usage patterns. The goal is to allow normal operations while preventing runaway loops."), ("Do velocity caps affect user experience?", "For well-behaved agents, no. Velocity caps only trigger on anomalous patterns. Sipi Bot's backoff is transparent to the agent — it just gets slower responses.")]),
    ],
}

def render_page(title, desc, paragraphs, faqs, path):
    schemas = ""
    bc_items = [("Home", CANONICAL), (title, "")]
    bc_elems = []
    for i, (n, u) in enumerate(bc_items, 1):
        bcu = u or (CANONICAL + "/")
        bc_elems.append(f'{{"@type":"ListItem","position":{i},"name":{json.dumps(n)},"item":{json.dumps(bcu)}}}')
    schemas += f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{",".join(bc_elems)}]}}</script>\n'
    schemas += f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":{json.dumps(title)},"description":{json.dumps(desc)},"author":{{"@type":"Organization","name":"{CANOPY}"}},"publisher":{{"@type":"Organization","name":"{CANOPY}","url":"{CANONICAL}"}},"datePublished":"{TODAY}"}}</script>\n'
    if faqs:
        faq_items = json.dumps([{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs])
        schemas += f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":{faq_items}}}</script>\n'
    
    p_html = "\n".join(f"<p>{p}</p>" for p in paragraphs)
    faq_html = "\n".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in (faqs or []))
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Sipi Bot</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{CANONICAL}{path}">
<meta property="og:title" content="{title} | Sipi Bot">
<meta property="og:description" content="{desc}">
<meta name="robots" content="index, follow">
{schemas}
</head>
<body>
<main>
<h1>{title}</h1>
{p_html}
<section class="faq">{faq_html}</section>
<section class="cta"><a href="/">Start monitoring agent spend</a></section>
</main>
<footer>&copy; {TODAY[:4]} Sipi Bot · <a href="https://x.com/sipiteno" style="color:inherit">X / Twitter</a></footer>
</body></html>'''

def build():
    total = 0
    for section, entries in PAGES.items():
        for slug, title, paragraphs, faqs in entries:
            desc = paragraphs[0][:155].replace('"', "'").replace("\n", " ")
            html = render_page(title, desc, paragraphs, faqs, f"/{section}/{slug}")
            d = os.path.join(BASE, section)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"{slug}.html"), "w") as f:
                f.write(html)
            total += 1
        print(f"  {section}: {len(entries)} pages")
    print(f"Total: {total}")

if __name__ == "__main__":
    build()
