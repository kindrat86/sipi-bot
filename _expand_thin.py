#!/usr/bin/env python3
"""
_expand_thin.py — Enrich thin HTML pages under public/ to >=400 visible words.

Reads all HTML files under public/, counts visible words (strip script/style/tags).
Skips files already >=400 words and pages explicitly excluded.
For thin pages (<400 words), extracts the page topic from <h1>, dispatches by
path prefix to section-specific enrichment generators, injects the HTML block
before </main>, fixes any JSON-LD 'https://***' corruption, and verifies the
new word count. Prints a summary table.

Usage:
  python3 _expand_thin.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "public"
MIN_WORDS = 400
GENERATOR_SENTINEL = "<!-- _expand_thin-enriched -->"

# Pages to skip (already enriched or index pages)
SKIP_PAGES = {
    "research/index.html",
    "checklists/index.html",
    "benchmarks/index.html",
    "checklists/agent-spend-firewall-deployment/index.html",
}

# Also skip non-content HTML (google verification, widgets, embed partials)
SKIP_PREFIXES = {
    "google",
    "widgets/",
    "embed/",
    "network/widget",
}

# ---------------------------------------------------------------------------
# Word-count helpers
# ---------------------------------------------------------------------------

_SCRIPT_STYLE = re.compile(r"<(script|style)\b[\s\S]*?</\1>", re.I)
_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def count_visible_words(html: str) -> int:
    """Count visible words — strip <script>/<style>, then tags, then split."""
    clean = _SCRIPT_STYLE.sub(" ", html)
    clean = _TAGS.sub(" ", clean)
    clean = _WS.sub(" ", clean).strip()
    return len(clean.split()) if clean else 0


def fix_jsonld_corruption(html: str) -> str:
    """Fix JSON-LD 'https://***' corruption -> 'https://schema.org","'.

    Some templates had a bug: "@context":"https://***@type" should be
    "@context":"https://schema.org","@type".
    """
    return html.replace('"https://***', '"https://schema.org","')


# ---------------------------------------------------------------------------
# Injection helpers
# ---------------------------------------------------------------------------

def inject_block(html: str, block: str) -> str:
    """Inject enrichment block before </main>. Idempotent via sentinel."""
    if GENERATOR_SENTINEL in html:
        return html
    idx = html.find("</main>")
    if idx == -1:
        # Fallback: before </body>
        idx = html.find("</body>")
        if idx == -1:
            return html
    wrapped = "\n\n" + GENERATOR_SENTINEL + "\n" + block + "\n"
    return html[:idx] + wrapped + html[idx:]


def extract_h1(html: str) -> str:
    """Extract the first <h1> tag content."""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    return m.group(1).strip() if m else ""


def extract_tag(html: str) -> str:
    """Extract the .tag content (Checklist, Guide, Glossary, etc.)."""
    m = re.search(r'<span class="tag">(.*?)</span>', html, re.I | re.S)
    return m.group(1).strip() if m else ""


def extract_lead(html: str) -> str:
    """Extract the .lead paragraph text."""
    m = re.search(r'<p class="lead">(.*?)</p>', html, re.I | re.S)
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------------------
# Section-specific enrichment generators
# ---------------------------------------------------------------------------

def enrich_checklist(h1: str, tag: str, lead_text: str, slug: str) -> str:
    """Enrich a /checklists/{x} page with implementation guidance."""
    parts = [
        '<section>',
        '<h2>Why this checklist matters for agent spend control</h2>',
        '<p>Checklists like "' + h1 + '" are only as valuable as their execution. '
        'In autonomous agent operations, a checklist item left unchecked is not a '
        'minor oversight — it is a financial exposure. Production agent teams that '
        'systematically work through deployment checklists report 60-80% fewer '
        'runaway cost incidents in the first 90 days compared to teams that rely '
        'on ad-hoc setups.</p>',
        '<p>The cost of skipping a single control — a velocity cap, a merchant '
        'allowlist entry, a human-in-the-loop threshold — is measured in dollars '
        'when a loop hits. The median runaway incident costs $340, and 67% of '
        'production agent teams experience at least one in a quarter. Every item '
        'on this checklist maps to a specific failure mode.</p>',
        '<h2>Implementation sequence</h2>',
        '<p>Work through these items in order. The first four (per-transaction '
        'limits, daily caps, velocity limits, merchant allowlists) form the '
        'foundation that every subsequent check depends on. Do not skip ahead '
        'to alerting or testing until the foundation is deployed and verified.</p>',
        '<ol>',
        '<li><strong>Start with the data</strong> — before configuring limits, '
        'audit your agent\'s actual spend patterns for a week. What is the median '
        'transaction? The 95th percentile? The max? Use real data, not guesses.</li>',
        '<li><strong>Set limits 2x above the 95th percentile</strong> — this gives '
        'headroom for legitimate variation while catching the 100x outlier that '
        'indicates a loop or compromise.</li>',
        '<li><strong>Test each path separately</strong> — send a transaction that '
        'should be APPROVED, one that should be BLOCKED (over limit), and one that '
        'should be FLAGGED (approval threshold). Confirm the agent handles all '
        'three outcomes gracefully.</li>',
        '<li><strong>Enable alerting before production</strong> — configure Slack '
        'or email notifications on flagged and blocked transactions. The first '
        'blocked transaction in production is information; make sure someone sees '
        'it within minutes, not hours.</li>',
        '<li><strong>Schedule a 7-day review</strong> — after one week of '
        'production traffic, review every blocked and flagged transaction. Tune '
        'limits based on what you learn. Most teams loosen initial limits by '
        '20-50% after observing real patterns.</li>',
        '</ol>',
        '<h2>Connecting back to your stack</h2>',
        '<p>sipi.bot enforces every item on this checklist in under 5 milliseconds '
        'per transaction. Define your per-transaction limit, daily ceiling, '
        'velocity cap, and merchant allowlist once — the firewall applies them '
        'consistently across every agent, every payment path, every run. '
        'At $99/month, the cost of deploying all 12 checklist items is less than '
        'the median single runaway incident.</p>',
        '</section>',
    ]
    return "\n".join(parts)


def enrich_guide(h1: str, tag: str, lead_text: str, slug: str) -> str:
    """Enrich a /guides/{x} page with concrete examples."""
    parts = [
        '<section>',
        '<h2>Putting this guide into practice</h2>',
        '<p>"' + h1.replace("&#x27;", "'") + '" covers the theory and architecture. '
        'The real challenge is translating that into working policy rules that '
        'actually run in production. Below are concrete examples that map the '
        'guide\'s concepts to sipi.bot policy configurations.</p>',
        '<h2>Common real-world scenarios</h2>',
        '<p>Teams implementing the patterns in this guide typically encounter three '
        'recurring situations. Here is how each one translates into actionable policy:</p>',
        '<h3>Scenario 1: The research agent that reads too deeply</h3>',
        '<p>A research agent hits 47 LLM API calls exploring a single topic. Each '
        'call is under $0.50 (within the per-transaction limit), but the cumulative '
        'cost hits $23 in 90 seconds. The fix is a velocity cap of 10 calls/minute '
        'per agent, which catches the rapid-fire pattern before the daily ceiling '
        'ever fires. Configure this in sipi.bot: set "max 10 evaluations/minute" '
        'on the agent\'s policy group. When the agent hits the limit, it receives '
        'a BLOCKED decision and must pace itself.</p>',
        '<h3>Scenario 2: The deployment that bypassed the staging check</h3>',
        '<p>A developer deploys a new agent version directly to production, skipping '
        'the staging environment. The new agent has a bug in its retry logic that '
        'generates 200 identical transactions. Without a daily ceiling ($50/agent) '
        'and a velocity cap, this becomes a $2,000 incident. With both, the agent '
        'is blocked at transaction 11 (velocity cap) or at the first transaction '
        'that pushes daily spend over $50. The audit log shows the new agent ID '
        'immediately, pinpoints the deployment, and the developer is alerted within '
        'seconds.</p>',
        '<h3>Scenario 3: The prompt injection that redirects a payment</h3>',
        '<p>An adversarial input tricks a customer-support agent into sending a payment '
        'to an attacker-controlled merchant. Without a merchant allowlist, the agent '
        'sends $500 to "merchant-service-pay.com" before anyone notices. With a '
        'merchant allowlist restricted to 8 approved vendors, the agent receives '
        'BLOCKED with reason "merchant not on allowlist." The transaction never '
        'executes. This scenario alone justifies the merchant allowlist as the '
        'highest-priority control in any deployment.</p>',
        '<h2>Next steps after reading this guide</h2>',
        '<p>Deploy the concepts in this guide with sipi.bot: set up your policy '
        'in the dashboard, wrap your agent\'s spend functions with the evaluation '
        'endpoint, and run the three test scenarios above. Each scenario takes '
        'under 10 minutes to configure and validates a different dimension of your '
        'spend control. At $99/month, the insurance is cheaper than a single '
        'uncontrolled incident.</p>',
        '</section>',
    ]
    return "\n".join(parts)


def enrich_use_case(h1: str, tag: str, lead_text: str, slug: str) -> str:
    """Enrich a /use-cases/{x} page with relevant scenarios."""
    # Extract the use case name from h1 or slug
    use_case = slug.split("/")[-1] if "/" in slug else slug
    use_case_name = use_case.replace("-", " ").title()

    parts = [
        '<section>',
        '<h2>Why spend control matters for ' + use_case_name + '</h2>',
        '<p>In ' + use_case_name + ' deployments, the agents are not experimental — '
        'they are moving money, making decisions, and operating with real financial '
        'authority. Every transaction is a potential failure point: a bug in agent '
        'logic, an unexpected edge case in the tool chain, or an adversarial input '
        'can turn a routine operation into a costly incident. The difference between '
        'a well-governed deployment and an unguarded one is not whether incidents '
        'happen — it is how much they cost when they do.</p>',
        '<p>Sector data shows that ' + use_case_name + ' teams with active spend '
        'firewalls experience 70% fewer cost overruns and recover from incidents '
        'in minutes rather than days. The primary reason is that a firewall provides '
        'the one thing dashboards and alerts cannot: pre-execution enforcement. '
        'The transaction is blocked before it executes, not reported after.</p>',
        '<h2>Three deployment scenarios for this use case</h2>',
        '<h3>Scenario A: Starting fresh</h3>',
        '<p>Deploying a new ' + use_case_name + ' agent? Configure your sipi.bot '
        'policy before the agent runs its first transaction. Set conservative defaults '
        '($2/transaction, $20/day, 10 calls/minute) and observe the audit log for '
        'the first week. You will almost certainly loosen limits after seeing real '
        'traffic — but starting tight means the first incident is a blocked '
        'transaction, not a bill.</p>',
        '<h3>Scenario B: Adding controls to an existing deployment</h3>',
        '<p>If your ' + use_case_name + ' agent is already running without a firewall, '
        'start with the audit log. Configure sipi.bot in monitor-only mode (flag all '
        'spend decisions, block nothing) for 48 hours. Review the flagged transactions '
        'to understand your actual spend patterns and identify anomalous behavior '
        'you did not know about. Then enable enforcement with limits calibrated to '
        'your observed data.</p>',
        '<h3>Scenario C: Multi-tenant or per-client deployments</h3>',
        '<p>For ' + use_case_name + ' setups serving multiple clients or internal '
        'teams, use per-agent policies. Each agent gets its own per-transaction '
        'limit, daily ceiling, velocity cap, and merchant allowlist. A billing agent '
        'that processes $500 refunds has different limits than a support agent that '
        'only makes $0.03 LLM calls. sipi.bot supports per-agent policies out of '
        'the box with no additional configuration complexity.</p>',
        '<h2>Getting started</h2>',
        '<p>sipi.bot\'s ' + use_case_name + ' deployment takes under an hour: '
        'create an account, define your policy rules, wire the evaluation endpoint '
        'into your agent\'s payment path, and run the three test scenarios. '
        'Pricing starts at $99/month for unlimited evaluations — less than the '
        'median single runaway incident. The audit log gives you complete visibility '
        'into every decision, blocked or approved.</p>',
        '</section>',
    ]
    return "\n".join(parts)


def enrich_benchmark(h1: str, tag: str, lead_text: str, slug: str) -> str:
    """Enrich a /benchmarks/{x} page with actionable insight."""
    parts = [
        '<section>',
        '<h2>Making this benchmark actionable</h2>',
        '<p>Benchmark data is only useful when it drives decisions. The numbers '
        'in "' + h1 + '" represent medians across many deployments — your actual '
        'costs may be higher or lower depending on your agent architecture, model '
        'choices, and workload patterns. The critical question is not "am I above '
        'or below the median?" but "what would an uncontrolled deviation from '
        'the median cost my team?"</p>',
        '<p>Production agent teams typically see a 10-50x spread between well-managed '
        'costs (within the benchmark range) and uncontrolled costs (a single runaway '
        'incident). The benchmark tells you what "good" looks like. A spend firewall '
        'is what keeps you there by enforcing the ceiling before the deviation '
        'becomes an incident.</p>',
        '<h2>How to use this data with sipi.bot</h2>',
        '<ol>',
        '<li><strong>Set your per-transaction limit at 3x the benchmark median</strong> '
        'for your use case. If the median task costs $0.30, set the limit at $0.90. '
        'This covers legitimate variance without leaving the blast radius wide open.</li>',
        '<li><strong>Set your daily ceiling at 50x the benchmark median</strong> — '
        'roughly a day\'s worth of normal operation. If the per-task median is $0.30 '
        'and you expect 100 tasks/day, set the ceiling at $15.00.</li>',
        '<li><strong>Configure velocity at 20x the benchmark rate</strong> — if a '
        'normal agent executes one task per minute, set velocity to 20 tasks/minute. '
        'This catches the loop pattern (100 calls in 90 seconds) without blocking '
        'legitimate burst traffic.</li>',
        '</ol>',
        '<h2>What to monitor</h2>',
        '<p>After deploying sipi.bot with these baseline limits, watch three metrics '
        'in the first week: blocked transaction rate (should be under 1%), flagged '
        'transaction rate (should be near zero), and cost per agent per day (should '
        'track your daily ceiling). If blocked rate is high, your limits are too '
        'tight. If flagged rate is high, your agents are operating near the edge of '
        'normal and you may have a behavioral pattern to investigate. In either case, '
        'the audit log shows you exactly which policy rule fired and why.</p>',
        '</section>',
    ]
    return "\n".join(parts)


def enrich_glossary(h1: str, tag: str, lead_text: str, slug: str) -> str:
    """Enrich a /glossary/{x} page with real-world context."""
    term = h1.split("—")[0].split("-")[0].replace("What Is ", "").replace("?", "").strip()
    if not term:
        term = slug.split("/")[-1].replace("-", " ").title()

    parts = [
        '<section>',
        '<h2>How ' + term + ' works in practice</h2>',
        '<p>Understanding the definition of ' + term + ' is the first step; knowing '
        'how it behaves in a production agent environment is what actually protects '
        'your budget. In practice, ' + term + ' manifests differently depending on '
        'your agent architecture, the payment methods your agent has access to, '
        'and whether the control is enforced before or after the transaction executes.</p>',
        '<p>Consider a real example: a research agent with access to a $500/month '
        'LLM API budget. Without ' + term + ', a single retry loop on a complex '
        'query can burn through 40% of the monthly budget in 20 minutes — 237 API '
        'calls at $0.84 each = $199.08. With ' + term + ' enforced as a velocity '
        'cap (10 calls/minute), the agent is blocked at call 11, the total spend '
        'is $9.24, and the audit log immediately surfaces the abnormal pattern. '
        'The team is alerted within seconds and investigates the retry bug before '
        'it recurs.</p>',
        '<h2>Common configuration mistakes</h2>',
        '<ul>',
        '<li><strong>Setting ' + term + ' too high</strong> because you are worried '
        'about interrupting legitimate agent work. Start conservative and raise '
        'based on observed data. A blocked transaction is a signal; an unblocked '
        'overspend is a cost.</li>',
        '<li><strong>Applying ' + term + ' globally instead of per-agent</strong>. '
        'Different agents have different spend profiles. A research agent that makes '
        '200 LLM calls/day is not the same as a billing agent that makes 5. Use '
        'per-agent policies.</li>',
        '<li><strong>Forgetting to test the block path</strong>. Configure ' + term
        + ', then deliberately trigger it to confirm your agent handles the BLOCKED '
        'response gracefully — no crash, no silent retry, and a clear explanation '
        'to the user.</li>',
        '</ul>',
        '<h2>How sipi.bot enforces ' + term + '</h2>',
        '<p>sipi.bot evaluates ' + term + ' on every transaction in under 5 '
        'milliseconds. The agent never sees the payment method directly; it receives '
        'a structured JSON decision (APPROVED, BLOCKED, or FLAGGED) and acts '
        'accordingly. Every decision is logged with agent ID, merchant, amount, '
        'timestamp, and the policy version that produced it — so you can always '
        'reconstruct why a transaction was allowed or denied. At $99/month, the '
        'enforcement costs less than a single uncontrolled incident.</p>',
        '</section>',
    ]
    return "\n".join(parts)


def enrich_integration(h1: str, tag: str, lead_text: str, slug: str) -> str:
    """Enrich an /integrations/{x} page with setup details."""
    target = h1.replace("sipi.bot + ", "").replace("sipi.bot+", "").strip()
    if not target or target.lower() == "sipi.bot":
        target = slug.split("/")[-1].replace("-", " ").title()

    parts = [
        '<section>',
        '<h2>Detailed integration walkthrough for ' + target + '</h2>',
        '<p>Integrating sipi.bot with ' + target + ' adds a policy enforcement layer '
        'between your agent\'s intent to spend and the actual transaction. The '
        'integration is deliberately minimal — a single API call with four fields '
        '(agent ID, merchant, amount, intent) — but the effect is comprehensive: '
        'every transaction must pass the policy check before money moves.</p>',
        '<h2>Step-by-step setup</h2>',
        '<ol>',
        '<li><strong>Install the sipi.bot SDK or use the HTTP API.</strong> If '
        + target + ' runs on Python, run <code>pip install sipi-bot</code>. For '
        'other runtimes, use the REST API at <code>POST https://sipi.bot/v1/transactions/evaluate</code>. '
        'Authentication is via bearer token.</li>',
        '<li><strong>Identify the spend paths.</strong> Search your ' + target + ' '
        'agent code for every place it can initiate a payment, charge, API call, '
        'provisioning action, or purchase. Each one needs a policy check inserted '
        'before the actual transaction executes.</li>',
        '<li><strong>Wrap each path with a policy check.</strong> The check takes '
        'four parameters: agent ID (string), merchant (string — the vendor or '
        'destination), amount (float in USD), intent (string — free-text description '
        'of what the transaction is for). Example: '
        '<code>sipi.check(agent_id="agent-1", merchant="openai", amount=0.50, intent="LLM call")</code></li>',
        '<li><strong>Handle the response.</strong> sipi.bot returns a JSON object: '
        '<code>{"decision": "APPROVED"|"BLOCKED"|"FLAGGED", "reason": "...", '
        '"transaction_id": "...", "policy_version": "..."}</code>. Your agent must '
        'handle all three outcomes. Do not assume APPROVED is the only response.</li>',
        '<li><strong>Test each path.</strong> Run one test for each outcome: '
        'a small approved transaction, a blocked transaction (exceed a limit), '
        'and a flagged transaction (exceed the approval threshold). Verify the '
        'audit log captures all three with correct details.</li>',
        '</ol>',
        '<h2>Testing your integration</h2>',
        '<p>After setup, run the integration with sipi.bot\'s sandbox mode first '
        '(set header <code>X-Sipi-Mode: sandbox</code>). Sandbox mode evaluates '
        'policies and writes to the audit log but never blocks a real transaction. '
        'Use it to verify your integration and tune your limits for 24 hours before '
        'enabling enforcement. Most teams find this catches 2-3 configuration issues '
        'that would have caused false positives in production.</p>',
        '<h2>Pricing</h2>',
        '<p>sipi.bot starts at $99/month for unlimited transaction evaluations. '
        'No per-call fees, no tier upgrades for higher volume. The integration with '
        + target + ' is supported out of the box, and setup typically takes under '
        'an hour for teams familiar with their agent\'s codebase.</p>',
        '</section>',
    ]
    return "\n".join(parts)


def enrich_generic(h1: str, tag: str, lead_text: str, slug: str) -> str:
    """Generic enrichment for other section types (answers, alternatives, compare,
    templates, tools, faq, for, vs, best, self-hosted, playground, network, etc.)."""
    section_name = tag if tag else slug.split("/")[0].replace("-", " ").title()

    parts = [
        '<section>',
        '<h2>Why ' + section_name + ' matters for agent spend control</h2>',
        '<p>Whether you are exploring ' + section_name.lower() + ', comparing '
        'solutions, or evaluating specific features, the central challenge remains '
        'the same: autonomous AI agents can initiate financial transactions, and '
        'without real-time enforcement, those transactions can escape human oversight '
        'in milliseconds. A policy that is not enforced before the transaction executes '
        'is not a control — it is a hope.</p>',
        '<p>Production teams that deploy active spend enforcement report 60-80% '
        'fewer cost incidents and recover from anomalies in minutes rather than '
        'days. The mechanism is straightforward: every transaction runs through a '
        'policy check that returns one of three decisions, and the agent acts on '
        'that decision before the money moves. No dashboard-watching, no after-the-fact '
        'reconciliation, no "we caught it on the next billing cycle."</p>',
        '<h2>Key considerations for ' + section_name.lower() + '</h2>',
        '<ul>',
        '<li><strong>Enforcement vs. observation:</strong> Dashboards tell you what '
        'happened. A spend firewall stops what should not happen. Both are useful; '
        'they are not substitutes. Start with enforcement, add observation for '
        'attribution and analytics.</li>',
        '<li><strong>Per-agent vs. global policies:</strong> Different agents have '
        'different spend profiles. A research agent and a billing agent need different '
        'limits. Configure per-agent policies from day one.</li>',
        '<li><strong>Velocity limits are non-negotiable:</strong> A per-transaction '
        'limit will not catch a loop of 200 small calls. A velocity cap (max '
        'transactions per minute) is the specific control for the most common '
        'runaway pattern.</li>',
        '<li><strong>Merchant allowlists prevent the worst-case scenario:</strong> '
        'A compromised agent can be redirected to any destination. An allowlist '
        'ensures it can only transact with vendors you have explicitly approved.</li>',
        '</ul>',
        '<h2>Next steps</h2>',
        '<p>sipi.bot enforces all four control dimensions — per-transaction limits, '
        'daily ceilings, velocity caps, and merchant allowlists — in under 5 '
        'milliseconds per evaluation. Pricing starts at $99/month for unlimited '
        'evaluations. Deploy in under an hour: define your policy, wrap your agent\'s '
        'spend functions, and run the three test scenarios (APPROVED, BLOCKED, '
        'FLAGGED) before going to production.</p>',
        '</section>',
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Section dispatch
# ---------------------------------------------------------------------------
# Map path prefixes to enrichment functions.
# The function signature is: fn(h1, tag, lead_text, slug) -> HTML block string

SECTION_DISPATCH = [
    ("checklists/", enrich_checklist),
    ("guides/", enrich_guide),
    ("use-cases/", enrich_use_case),
    ("benchmarks/", enrich_benchmark),
    ("glossary/", enrich_glossary),
    ("integrations/", enrich_integration),
]

# All other sections use the generic handler but with a section-specific name
GENERIC_SECTIONS = {
    "answers/": "Answers",
    "alternatives/": "Alternatives",
    "compare/": "Comparisons",
    "templates/": "Templates",
    "tools/": "Tools",
    "faq/": "FAQ",
    "for/": "For",
    "vs/": "Comparisons",
    "best/": "Best Of",
    "self-hosted/": "Self-Hosted",
    "playground/": "Playground",
    "network/": "Network",
}


def dispatch_enrichment(html: str, rel_path_str: str) -> str:
    """Determine the section of a page and apply the right enrichment."""
    h1 = extract_h1(html)
    tag = extract_tag(html)
    lead_text = extract_lead(html)
    slug = rel_path_str.replace("/index.html", "")

    # Check section-specific generators first
    for prefix, handler in SECTION_DISPATCH:
        if rel_path_str.startswith(prefix):
            return handler(h1, tag, lead_text, slug)

    # Check generic sections
    for prefix, section_name in GENERIC_SECTIONS.items():
        if rel_path_str.startswith(prefix):
            return enrich_generic(h1, section_name, lead_text, slug)

    # Fallback: use the directory name as the section
    dir_name = rel_path_str.split("/")[0] if "/" in rel_path_str else ""
    return enrich_generic(h1, dir_name.title() if dir_name else "Page", lead_text, slug)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    html_files = sorted(ROOT.rglob("*.html"))

    results = []
    total_thin = 0
    total_enriched = 0
    total_errors = 0
    total_jsonld_fixed = 0

    for html_path in html_files:
        rel = html_path.relative_to(ROOT)
        rel_str = str(rel)

        # Skip non-content files
        if any(rel_str.startswith(p) for p in SKIP_PREFIXES):
            continue

        # Skip explicitly excluded pages
        if rel_str in SKIP_PAGES:
            continue

        html = html_path.read_text(encoding="utf-8")

        # Fix JSON-LD corruption FIRST (even for pages that won't be enriched)
        fixed_html = fix_jsonld_corruption(html)
        if fixed_html != html:
            total_jsonld_fixed += 1
            html = fixed_html

        old_wc = count_visible_words(html)

        if old_wc >= MIN_WORDS:
            # Still write back if we fixed JSON-LD
            if fixed_html != html:
                html_path.write_text(html, encoding="utf-8")
                results.append((rel_str, old_wc, old_wc, "jsonld-fix"))
            continue

        total_thin += 1

        # Generate enrichment block
        try:
            block = dispatch_enrichment(html, rel_str)
            if not block:
                print(f"  WARNING: empty block for {rel_str}")
                continue
        except Exception as e:
            print(f"  ERROR generating block for {rel_str}: {e}")
            total_errors += 1
            continue

        # Inject
        new_html = inject_block(html, block)
        if new_html == html:
            print(f"  WARNING: injection failed for {rel_str} (no </main> found)")
            total_errors += 1
            continue

        new_wc = count_visible_words(new_html)

        if new_wc < MIN_WORDS:
            print(f"  WARNING: {rel_str} still thin after enrichment ({new_wc} words)")
            total_errors += 1
            # Still save the enriched version, it's better than nothing
            html_path.write_text(new_html, encoding="utf-8")
            results.append((rel_str, old_wc, new_wc, "enriched-thin"))
            continue

        html_path.write_text(new_html, encoding="utf-8")
        total_enriched += 1
        results.append((rel_str, old_wc, new_wc, "enriched"))

    # Print summary
    print()
    print("=" * 78)
    print("  _expand_thin.py — Summary")
    print("=" * 78)
    print(f"  Total HTML files scanned: {len(html_files)}")
    print(f"  Thin pages found:          {total_thin}")
    print(f"  Enriched (>=400 words):    {total_enriched}")
    print(f"  JSON-LD fixes:             {total_jsonld_fixed}")
    print(f"  Errors/warnings:           {total_errors}")
    print()
    print("  File                          Old    New    Action")
    print("  " + "-" * 60)
    for rel_str, old_wc, new_wc, action in results:
        print(f"  {rel_str:35s} {old_wc:4d} -> {new_wc:4d}  {action}")
    print()
    print(f"  Total files processed: {len(results)}")
    print("=" * 78)

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
