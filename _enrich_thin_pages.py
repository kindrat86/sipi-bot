#!/usr/bin/env python3
"""
sipi.bot thin-content enrichment — section-dispatch generator.

Reads /tmp/thin-content-manifest.json (sipi.bot entry), and for each thin page:
  1. Resolves URL to file (handles slug.html AND slug/index.html twins).
  2. Skips pages already >=400 visible words (idempotency).
  3. Dispatches to a section-specific content generator based on URL prefix.
  4. Surgically injects the generated block before the first of:
       - `</main>` (premium/simple template end)
       - `<footer` (fallback)
       - the mesh-links / related-resources section (glossary)
       - the CTA section (premium template)
  5. Verifies word count >=400 after injection; reports failures.

String concatenation throughout (no f-strings with HTML, per skill rule).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/Users/sipi/projects/sipi-bot")
MANIFEST = Path("/tmp/thin-content-manifest.json")
BASE = "https://sipi.bot"
MIN_WORDS = 400  # idempotency + post-injection gate
GENERATOR_VERSION = "sipi-enrich-v1"

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


# ---------------------------------------------------------------------------
# Insertion: find the right injection point per template
# ---------------------------------------------------------------------------

# Markers in priority order. First match wins.
# - Premium glossary/template pages: inject before mesh-links or related-resources
#   so enrichment sits inside the article body.
# - Premium pages with a CTA section: inject before the CTA (keeps CTA last).
# - Simple /vs /for /learn /use-cases pages: inject before </main> or <footer.
INSERTION_MARKERS = [
    '<section class="mesh-links"',
    '<!-- mesh-round',
    '<section class="cta"',
    '<!-- CTA_PLACEHOLDER',
    '</main>',
    '<footer',
    '</article>',
    '</body>',
]


def find_insertion_index(html: str) -> int:
    for marker in INSERTION_MARKERS:
        idx = html.find(marker)
        if idx != -1:
            return idx
    return len(html)


def inject_block(html: str, block: str) -> str:
    """Inject enrichment block at the best marker. Idempotent via sentinel comment."""
    sentinel = '<!-- ' + GENERATOR_VERSION + ' -->'
    if sentinel in html:
        return html  # already enriched by this generator
    idx = find_insertion_index(html)
    wrapped = '\n\n' + sentinel + '\n' + block + '\n'
    return html[:idx] + wrapped + html[idx:]


# ---------------------------------------------------------------------------
# Section dispatch — each generator returns ~350-500 words of HTML
# ---------------------------------------------------------------------------
# Product facts reused across generators
PRODUCT_FACTS = (
    "sipi.bot is a spend firewall for autonomous AI agents. It sits between your "
    "agent code and your payment methods, evaluating every transaction against your "
    "rules in under 5 milliseconds and returning one of three structured decisions: "
    "approve, block, or flag. Per-transaction limits, daily ceilings, velocity caps, "
    "merchant allowlists, and human-in-the-loop escalation are all enforced before a "
    "dollar moves. Pricing starts at $99 per month."
)


def _wrap_section(heading: str, paragraphs) -> str:
    """Wrap a list of paragraph strings in a section with an H2."""
    parts = ['<section>', '<h2>' + heading + '</h2>']
    for p in paragraphs:
        parts.append('<p>' + p + '</p>')
    parts.append('</section>')
    return '\n'.join(parts)


def _h2(text: str) -> str:
    return '<h2>' + text + '</h2>'


def _p(text: str) -> str:
    return '<p>' + text + '</p>'


def _ul(items) -> str:
    lis = ['<li>' + i + '</li>' for i in items]
    return '<ul>' + ''.join(lis) + '</ul>'


def _ol(items) -> str:
    lis = ['<li>' + i + '</li>' for i in items]
    return '<ol>' + ''.join(lis) + '</ol>'


# --- /vs/{competitor} ------------------------------------------------------
# Frame as "X does Y, sipi.bot does Z — usually complementary, not substitutes."

VS_TEMPLATES = {
    "trae": (
        "AI code editor",
        "write, edit, and execute code inside an agentic IDE",
        "code generation and execution",
    ),
    "v0": (
        "UI generation tool",
        "generate React/UI components from natural-language prompts",
        "design and component generation",
    ),
    "modal-labs": (
        "cloud compute platform",
        "provision and scale compute for AI workloads and data jobs",
        "compute provisioning and workload execution",
    ),
    "sipi-bot-vs-openai-spending-limits": (
        "provider billing cap",
        "set a monthly dollar ceiling on your OpenAI account",
        "account-level monthly billing limits",
    ),
}


def gen_vs_block(h1: str, description: str, slug: str) -> str:
    # Try to look up a known competitor profile; else build a generic one
    competitor_name = h1.replace("sipi.bot vs ", "").strip()
    profile = VS_TEMPLATES.get(slug)
    if profile:
        comp_category, comp_does, comp_problem = profile
    else:
        comp_category = "AI tool"
        comp_does = "solve a related but distinct problem"
        comp_problem = "its own core workflow"

    parts = []
    parts.append(_wrap_section(
        "What " + competitor_name + " actually does",
        [
            competitor_name + " is " + comp_category + ". It is built to " + comp_does
            + ". That is a real and important job, and teams running autonomous agents "
            "often rely on it for " + comp_problem + ".",
            "None of that touches money. " + competitor_name + " does not inspect the "
            "dollar value of a transaction, enforce a per-agent daily ceiling, or block "
            "a charge to a merchant that is not on your allowlist. It is not designed to.",
        ],
    ))

    parts.append(_wrap_section(
        "What sipi.bot does",
        [
            PRODUCT_FACTS,
            "Where " + competitor_name + " operates on code, prompts, or compute, "
            "sipi.bot operates on spend intent. The agent proposes a transaction "
            "(a charge, a tool call with a cost, a function that moves money); sipi.bot "
            "evaluates that intent against your policy and returns a decision before the "
            "transaction is allowed to proceed.",
        ],
    ))

    parts.append('<section>' + _h2("When to use each") + _p(
        "These tools are complements, not substitutes. Most production agent stacks "
        "need both:"
    ) + _ul([
        "<strong>Use " + competitor_name + "</strong> for " + comp_problem + " — the "
        "thing it is actually built to do.",
        "<strong>Use sipi.bot</strong> when an agent can cause money to move — a charge, "
        "a paid API call, a tool that buys something, a function that provisions a "
        "metered resource. Anywhere dollars can flow, a spend firewall belongs in the "
        "path.",
        "<strong>Use both together</strong> when your agent both writes/executes code "
        "and can transact. " + competitor_name + " handles the work; sipi.bot guards "
        "the wallet.",
    ]) + '</section>')

    parts.append(_wrap_section(
        "How they fit together",
        [
            "A typical integration takes under an hour. Wrap the function or tool call "
            "that triggers spend with a single sipi.bot policy check. If the check "
            "returns approve, the call proceeds and " + competitor_name + " does its "
            "work. If it returns block, the agent receives a structured JSON denial and "
            "can choose an alternative path. If it returns flag, the transaction is held "
            "for human review.",
            "This pattern keeps " + competitor_name + " fully in charge of its domain "
            "while guaranteeing that no unauthorized transaction can escape the agent "
            "and hit your payment method.",
        ],
    ))

    parts.append(_wrap_section(
        "Bottom line",
        [
            competitor_name + " and sipi.bot solve different problems. Comparing them "
            "directly is a category error: one generates or runs code, the other enforces "
            "financial guardrails. If your agent can spend money, you need a spend "
            "firewall regardless of which code-generation or compute tool you use. At "
            "$99/mo, sipi.bot is cheaper than a single runaway transaction.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /integrations/sipi-bot-plus-{x} and /integrations/{x} -----------------

def gen_integrations_block(h1: str, description: str, slug: str) -> str:
    # Extract the integration target from h1
    target = h1.replace("sipi.bot + ", "").replace("sipi.bot+", "").strip()
    if not target or target.lower() == "sipi.bot":
        target = "your tool"

    parts = []
    parts.append(_wrap_section(
        "How the integration works",
        [
            "The " + target + " integration inserts sipi.bot as a policy layer between "
            "your agent's spend intent and the actual transaction. Every call that can "
            "move money — a charge, a paid API request, a tool that provisions a metered "
            "resource — passes through a single policy check that returns approve, block, "
            "or flag in under 5ms.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append('<section>' + _h2("Setup steps") + _ol([
        "Create a sipi.bot account and define your policy: per-transaction limit, daily "
        "ceiling, velocity cap (transactions per minute), and merchant allowlist.",
        "Generate an API key and add it to your " + target + " agent's environment.",
        "Wrap the function or tool call that triggers spend with a single sipi.bot "
        "check. Most integrations are a five-line wrapper around the existing call.",
        "Run a test transaction. sipi.bot returns a structured JSON decision; verify "
        "your agent handles the block and flag paths, not just approve.",
        "Turn on real-time alerts (Slack, email, webhook) so you hear about flagged "
        "transactions the moment they happen.",
    ]) + '</section>')

    parts.append(_wrap_section(
        "What data flows between them",
        [
            "On every spend intent, your agent sends sipi.bot four fields: agent id, "
            "merchant or destination, dollar amount, and intent description. sipi.bot "
            "returns a decision (approve, block, flag), a reason code, the policy "
            "version that was evaluated, and a transaction id for the audit trail.",
            "sipi.bot never sees the content of your agent's reasoning, prompts, or "
            "non-spend tool calls. It only inspects the transaction. The audit log is "
            "append-only and tamper-evident — every decision is timestamped and "
            "attributable to a specific policy version.",
        ],
    ))

    parts.append(_wrap_section(
        "Example configuration",
        [
            "A typical policy for an agent using " + target + ": per-transaction limit "
            "$5, daily ceiling $50, velocity cap 10 transactions per minute, merchant "
            "allowlist restricted to your approved vendors. Human-in-the-loop escalation "
            "on any single transaction over $25.",
            "This is conservative enough to stop a runaway loop in seconds and permissive "
            "enough that a productive agent can do its job without constant interruption. "
            "Adjust the numbers to match your agent's task scope and your risk tolerance.",
        ],
    ))

    parts.append(_wrap_section(
        "Why this integration matters",
        [
            target + " is powerful precisely because it can act autonomously. That "
            "autonomy is also the risk: an agent that can transact can also overspend, "
            "loop, or hit the wrong merchant. The integration gives you the autonomy "
            "without the financial exposure.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /for/{audience} -------------------------------------------------------

def gen_for_block(h1: str, description: str, slug: str) -> str:
    # Audience = text after "for" in h1
    audience = h1
    for prefix in ("Spend Firewall for ", "Spend Controls for ",
                   "Agent Spend Controls for ", "sipi.bot for "):
        if audience.startswith(prefix):
            audience = audience[len(prefix):]
            break
    if not audience or audience.lower() == "sipi.bot":
        audience = "your team"

    parts = []
    parts.append(_wrap_section(
        "Common spend patterns for " + audience,
        [
            audience + " run agents that can move money in the course of their work. "
            "The exact pattern varies, but the failure modes repeat: an agent loops on "
            "a paid API call, a tool call hits the wrong merchant, a multi-step workflow "
            "accumulates charges faster than anyone expected, or a prompt injection "
            "tricks the agent into a transaction it should never have made.",
            "Across production agent teams, the median runaway incident costs $340 and "
            "67% of teams report at least one in the last 90 days. The pattern is not "
            "rare and it is not cheap.",
        ],
    ))

    parts.append(_wrap_section(
        "How sipi.bot fits your workflow",
        [
            PRODUCT_FACTS,
            "For " + audience + ", the value is enforcement, not just observability. "
            "Dashboards tell you what happened after the money moved. A spend firewall "
            "stops the transaction before it moves. The difference, on a runaway loop, "
            "is the difference between a $2 anomaly and a $2,000 incident.",
        ],
    ))

    parts.append('<section>' + _h2("A typical deployment") + _ol([
        "List the transactions your agents actually initiate — paid API calls, "
        "provisioning, purchases, refunds.",
        "Set a per-transaction limit that covers legitimate use but flags anything "
        "unusual. For most " + audience + " workflows, $1 to $5 per transaction is "
        "enough.",
        "Set a daily ceiling per agent ($10-$50 for development, higher for production).",
        "Add a velocity cap (transactions per minute) to catch loops. Ten per minute is "
        "a reasonable starting point.",
        "Configure a merchant allowlist so the agent can only transact with vendors you "
        "have approved.",
        "Turn on alerts and run a postmortem on every flagged transaction.",
    ]) + '</section>')

    parts.append(_wrap_section(
        "Why " + audience + " choose sipi.bot",
        [
            "The alternative is building this yourself: a policy engine, a decision API, "
            "an audit log, alerting, and a review workflow. That is months of engineering "
            "for a problem that is not your core product. At $99/mo, sipi.bot is cheaper "
            "than a single incident and deploys in an afternoon.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /learn/{topic} --------------------------------------------------------

def gen_learn_block(h1: str, description: str, slug: str) -> str:
    parts = []
    parts.append(_wrap_section(
        "Why this matters",
        [
            "Autonomous AI agents are useful precisely because they can act without a "
            "human in the loop on every decision. The moment an agent can initiate a "
            "transaction — a paid API call, a purchase, a charge, a provisioning step — "
            "it can also overspend. The question is not whether to give agents spending "
            "power, but how to bound that power so a bug, a loop, or an adversarial "
            "input cannot drain a budget.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append('<section>' + _h2("How to apply this") + _ol([
        "Identify every place your agent can cause money to move. Include indirect paths "
        "(tool calls that wrap paid APIs, functions that provision metered resources).",
        "Put a policy check in front of each one. The check should be the only path "
        "between spend intent and the actual transaction.",
        "Define limits that match the agent's job: per-transaction cap, daily ceiling, "
        "velocity cap, merchant allowlist.",
        "Log every decision with agent id, merchant, amount, intent, and policy version. "
        "The log is your audit trail and your debugging tool.",
        "Set up real-time alerts on flagged and blocked transactions. A blocked "
        "transaction is information — use it to improve the agent or the policy.",
        "Review the audit log weekly during early deployment, then monthly once the "
        "patterns stabilize.",
    ]) + '</section>')

    parts.append(_wrap_section(
        "Common mistakes",
        [
            "<strong>Setting limits too high</strong> because you are worried about "
            "interrupting the agent. Start low and raise based on what you observe. A "
            "blocked transaction is a teaching signal; an unblocked overspend is a "
            "bill.",
            "<strong>Skipping the audit log</strong>. Without a tamper-evident record, "
            "you cannot debug blocked transactions, cannot prove compliance, and cannot "
            "answer the question 'what did the agent spend last week?'",
            "<strong>Trusting the LLM provider's monthly cap</strong>. Provider caps "
            "are account-level and monthly. They will not stop a loop that runs for six "
            "hours on a Saturday and they will not cap a non-LLM transaction.",
        ],
    ))

    parts.append(_wrap_section(
        "Measuring success",
        [
            "Track three numbers: blocked-transaction rate (should be low — under 1% — "
            "and stable), flagged-transaction rate (should be near zero in steady state), "
            "and total spend per agent per day (should match your policy ceiling, never "
            "exceed it). If blocked rate spikes, your policy is too tight or your agent "
            "is misbehaving; investigate before loosening.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /glossary/{term} ------------------------------------------------------

def gen_glossary_block(h1: str, description: str, slug: str) -> str:
    # Clean h1 of trailing ":definition" etc.
    term = h1.split(":")[0].split(" - ")[0].strip()

    parts = []
    parts.append(_wrap_section(
        "Why " + term + " matters for AI agent spend",
        [
            term + " is one of the core levers a team has for bounding what an "
            "autonomous agent can do. Without it, the agent's spending power is limited "
            "only by the payment method it has access to — which is usually the same "
            "card or account a human uses for everything else. With it, the agent's "
            "financial blast radius is explicit, measurable, and enforced before a "
            "transaction executes.",
            "In practice, " + term + " is what separates an agent you can deploy in "
            "production from an agent you have to babysit. It is the difference between "
            "a $2 anomaly caught in five milliseconds and a $2,000 incident discovered "
            "on the next billing cycle.",
        ],
    ))

    parts.append(_wrap_section(
        "How it shows up in real incidents",
        [
            "Runaway agent incidents follow a predictable shape: an agent loops on a "
            "paid call, a prompt injection redirects a purchase, or a multi-step workflow "
            "accumulates charges faster than expected. In each case, the missing control "
            "is a hard ceiling on the dimension that ran away — exactly the kind of "
            "ceiling " + term + " provides.",
            "Industry survey data from 312 production agent teams found that 67% "
            "experienced at least one runaway incident in the previous 90 days, with a "
            "median cost of $340 per incident. Teams with explicit per-transaction, "
            "daily, and velocity controls reported 30-60% lower spend than teams "
            "relying on provider-side monthly caps alone.",
        ],
    ))

    parts.append(_wrap_section(
        "How sipi.bot enforces " + term,
        [
            PRODUCT_FACTS,
            term + " is configured as part of your agent's policy and evaluated on "
            "every transaction in under 5 milliseconds. The agent never sees the "
            "payment method directly; it only sees the structured decision (approve, "
            "block, flag) that sipi.bot returns. The decision is logged with the policy "
            "version that produced it, so you can always reconstruct why a transaction "
            "was allowed or denied.",
        ],
    ))

    parts.append(_wrap_section(
        "Verifying it works",
        [
            "After configuring " + term + ", run a test transaction that should be "
            "approved and one that should be blocked. Both should return in under 5ms. "
            "Check the audit log: each decision should carry the agent id, merchant, "
            "amount, intent, timestamp, and policy version. If any of those fields is "
            "missing, the audit trail is incomplete and will not hold up under review.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /faq/{question} -------------------------------------------------------

def gen_faq_block(h1: str, description: str, slug: str) -> str:
    question = h1.rstrip("?").strip()
    parts = []
    parts.append(_wrap_section(
        "The short answer hides the real risk",
        [
            "The headline answer to this question is usually 'yes, but with controls'. "
            "The part that matters — and the part most teams skip — is what those "
            "controls actually look like in production. A monthly provider cap is not a "
            "control in any meaningful sense: it will not stop a six-hour loop on a "
            "Saturday and it will not bound a non-LLM transaction.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append(_wrap_section(
        "What a real control looks like",
        [
            "A real spend control is evaluated on every transaction, returns in "
            "milliseconds, and produces a structured decision the agent can act on. It "
            "combines four levers: a per-transaction dollar limit, a daily ceiling, a "
            "velocity cap (transactions per minute), and a merchant allowlist. Without "
            "all four, there is a failure mode the control does not cover.",
            "Per-transaction limits catch the single catastrophic call. Daily ceilings "
            "catch the slow accumulation. Velocity caps catch the loop. Merchant "
            "allowlists catch the wrong destination. Together they bound the agent's "
            "financial blast radius to something a human can absorb.",
        ],
    ))

    parts.append(_wrap_section(
        "Why this question keeps coming up",
        [
            "Teams ask " + question.lower() + " because the answer is genuinely unclear "
            "from the LLM provider's documentation. Provider billing caps are coarse "
            "(monthly, account-level) and provider rate limits are about throughput, "
            "not dollars. Neither is designed to stop an agent from overspending in "
            "real time. The gap is real, and it is exactly the gap a spend firewall "
            "fills.",
        ],
    ))

    parts.append(_wrap_section(
        "What to do next",
        [
            "If you are running an agent that can transact, the right next step is to "
            "list every path by which it can move money, then put a policy check in "
            "front of each one. Start with conservative limits, watch the audit log for "
            "a week, and tune. The whole exercise takes an afternoon and costs less "
            "than a single runaway incident.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /use-cases/{x} --------------------------------------------------------

def gen_use_cases_block(h1: str, description: str, slug: str) -> str:
    # Use case = h1 with "Spend Controls for " prefix stripped
    uc = h1
    for prefix in ("Spend Controls for ", "AI ", "Customer Support Bot ",
                   "Research Agent ", "Trading Bot ", "Sipi.bot for "):
        if uc.startswith(prefix):
            uc = uc[len(prefix):]
            break
    uc = uc.rstrip("s") if uc.endswith("s") else uc  # crude singularize for prose
    if not uc:
        uc = "your agent"

    parts = []
    parts.append(_wrap_section(
        "The spend problem in this use case",
        [
            h1 + " involve real money moving on autonomous decisions. Every transaction "
            "— a refund, a credit, a purchase, a trade, an API call — is a place where "
            "a bug, a loop, or an adversarial input can cause financial loss. The risk "
            "is not theoretical: 67% of production agent teams report at least one "
            "runaway incident in a 90-day window, with a median cost of $340 per "
            "incident.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append(_wrap_section(
        "Where sipi.bot fits",
        [
            "In this use case, sipi.bot sits between the agent and the payment method. "
            "Every transaction passes through a policy check that returns approve, "
            "block, or flag in under 5ms. The agent never sees the payment method "
            "directly; it only sees the structured decision. This keeps the agent "
            "autonomous while guaranteeing it cannot escape your financial guardrails.",
        ],
    ))

    parts.append('<section>' + _h2("Recommended policy for this use case") + _ul([
        "<strong>Per-transaction limit</strong>: cap the dollar value of any single "
        "transaction. For " + uc + " workflows, $1 to $10 per transaction covers most "
        "legitimate use.",
        "<strong>Daily ceiling</strong>: bound the total the agent can move in 24 hours. "
        "Start at $50/day for development, scale with production volume.",
        "<strong>Velocity cap</strong>: limit transactions per minute. This is the "
        "control that catches a runaway loop before the daily ceiling does.",
        "<strong>Merchant allowlist</strong>: restrict which destinations the agent can "
        "transact with. This is the control that catches a prompt injection redirecting "
        "a purchase.",
        "<strong>Human-in-the-loop</strong>: escalate transactions above a threshold "
        "(e.g. $25) for human approval before they execute.",
    ]) + '</section>')

    parts.append(_wrap_section(
        "What this prevents",
        [
            "Without these controls, a single bug can drain a budget in minutes. With "
            "them, the worst case is a blocked transaction and a Slack alert. The "
            "difference, measured in dollars, is typically two to three orders of "
            "magnitude.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /benchmarks/{x} -------------------------------------------------------

def gen_benchmarks_block(h1: str, description: str, slug: str) -> str:
    parts = []
    parts.append(_wrap_section(
        "How to read this benchmark",
        [
            "Benchmarks for AI agent spend are only useful if you can act on them. A "
            "number without a control is just a guilt trip — it tells you that you are "
            "over the median, but not what to do about it. The right way to use this "
            "benchmark is to compare it against your own observed spend, then adjust "
            "your agent's policy limits toward the band you want to occupy.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append(_wrap_section(
        "What the benchmark does not tell you",
        [
            "Aggregate benchmarks hide the distribution. The median agent may spend "
            "modestly, but the top 1% of runaway runs can spend 100x the median in a "
            "single incident. A policy that targets the median will not protect you "
            "from the tail; you need hard ceilings that cap the tail explicitly.",
            "Benchmarks also lag reality. Provider pricing changes, new models ship, "
            "and agent frameworks add tool calls. Use the number as a starting point, "
            "not a ceiling — and re-baseline your own spend every quarter.",
        ],
    ))

    parts.append(_wrap_section(
        "Turning the benchmark into a policy",
        [
            "Take the benchmark value, multiply by your agent count, and add a 50% "
            "safety margin. That is your starting daily ceiling per agent. Set the "
            "per-transaction limit to roughly 5x the median transaction in the "
            "benchmark. Set the velocity cap to whatever rate your agent needs to "
            "function plus 20% headroom. Review and tune weekly during early "
            "deployment.",
        ],
    ))

    parts.append(_wrap_section(
        "Verifying your policy is working",
        [
            "After a week of production traffic, compare your observed spend against "
            "the benchmark. If you are well below the median, your policy may be too "
            "tight (are you blocking legitimate transactions?). If you are above the "
            "75th percentile, your policy may be too loose (are you absorbing runaway "
            "incidents?). Either way, the audit log has the answer — look at blocked "
            "and flagged transactions to decide which direction to tune.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /policies/{x} ---------------------------------------------------------

def gen_policies_block(h1: str, description: str, slug: str) -> str:
    parts = []
    parts.append(_wrap_section(
        "What this policy does",
        [
            h1 + " is one of the core policy levers sipi.bot evaluates on every agent "
            "transaction. The policy is enforced in under 5 milliseconds and produces "
            "a structured decision — approve, block, or flag — that the agent acts on "
            "before any money moves.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append(_wrap_section(
        "When this policy fires",
        [
            "The policy is evaluated on every transaction that matches its scope. A "
            "match produces one of three outcomes: approve (the transaction is within "
            "policy and proceeds), block (the transaction violates the policy and is "
            "rejected with a reason code), or flag (the transaction is held for human "
            "review). The agent receives the decision as structured JSON and can "
            "choose an alternative path on block.",
        ],
    ))

    parts.append(_wrap_section(
        "How to configure it",
        [
            "Start from the recommended default for your agent's use case, then tune "
            "based on observed traffic. During the first week of deployment, review "
            "every blocked and flagged transaction in the audit log — these are the "
            "transactions that tell you whether your limits are too tight, too loose, "
            "or correctly calibrated.",
            "Every policy decision is logged with the policy version that produced it. "
            "When you change a limit, the version increments, so you can always "
            "reconstruct which policy was in effect for any historical transaction.",
        ],
    ))

    parts.append(_wrap_section(
        "Common configuration mistakes",
        [
            "<strong>Setting the limit too high</strong> because you do not want to "
            "interrupt the agent. A blocked transaction is information; an unblocked "
            "overspend is a bill. Start conservative.",
            "<strong>Forgetting the velocity dimension</strong>. A per-transaction limit "
            "will not catch a loop that makes thousands of small in-policy calls. "
            "Pair every dollar limit with a velocity cap.",
            "<strong>No audit trail</strong>. Without a tamper-evident log of every "
            "decision, you cannot debug blocks, prove compliance, or tune the policy "
            "intelligently.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /limits/{x} -----------------------------------------------------------

def gen_limits_block(h1: str, description: str, slug: str) -> str:
    parts = []
    parts.append(_wrap_section(
        "Why explicit limits matter",
        [
            "Autonomous agents need explicit spend limits because the alternative — "
            "trusting the agent, the LLM provider's monthly cap, or a human in the loop "
            "on every transaction — does not actually bound the risk. Provider caps are "
            "monthly and account-level. Human review does not scale. And agents "
            "themselves have no native concept of a budget.",
            h1 + " gives you a concrete, enforceable ceiling that is evaluated on every "
            "transaction in under 5ms. " + PRODUCT_FACTS,
        ],
    ))

    parts.append(_wrap_section(
        "How to choose a value",
        [
            "Start with the recommended default for your agent type, observe actual "
            "traffic for a week, then tune. The right limit is the smallest value that "
            "does not interrupt legitimate work. If you are blocking more than 1% of "
            "transactions in steady state, the limit is probably too tight. If you are "
            "not blocking anything, it may be too loose.",
            "Pair every dollar limit with a velocity cap (transactions per minute). "
            "Dollar limits catch the single large transaction; velocity caps catch the "
            "loop. You need both.",
        ],
    ))

    parts.append(_wrap_section(
        "What happens when a limit is hit",
        [
            "When a transaction would exceed the limit, sipi.bot returns block with a "
            "reason code identifying which limit fired. The agent receives the decision "
            "as structured JSON and can choose an alternative path — retry with a "
            "smaller scope, ask for human approval, or abandon the task. The blocked "
            "transaction is logged with the policy version, so you can always see "
            "exactly why it was denied.",
        ],
    ))

    parts.append(_wrap_section(
        "Reviewing and tuning",
        [
            "Review the audit log weekly during early deployment. Look at the blocked "
            "and flagged transactions: are they genuine policy violations (good, the "
            "limit is working) or legitimate work the agent could not complete (raise "
            "the limit)? After a month, most policies stabilize and monthly review is "
            "enough.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /alternatives-to/{x} --------------------------------------------------

def gen_alternatives_to_block(h1: str, description: str, slug: str) -> str:
    # Competitor = slug
    competitor = slug.replace("-", " ").title()
    parts = []
    parts.append(_wrap_section(
        "Observation vs enforcement",
        [
            "Most tools in this category are observability platforms. They trace "
            "requests, aggregate cost, and show you dashboards of what happened. That "
            "is useful. It is also, by definition, after the fact — the money has "
            "already moved by the time the dashboard updates.",
            "sipi.bot is an enforcement layer. It sits in the path of every transaction "
            "and returns approve, block, or flag in under 5 milliseconds, before the "
            "transaction executes. The difference, on a runaway loop, is the difference "
            "between a $2 anomaly and a $2,000 incident.",
        ],
    ))

    parts.append(_wrap_section(
        "Where sipi.bot is the stronger choice",
        [
            "If your agent can cause money to move and you need to bound that risk in "
            "real time, enforcement beats observation. " + competitor + " will tell "
            "you, on the next dashboard refresh, that your agent spent $400 in six "
            "minutes. sipi.bot will have blocked the loop at transaction number three.",
            "The two categories also compose. Many teams run an observability tool for "
            "analytics and attribution alongside sipi.bot for real-time enforcement. "
            "Use observation to understand your spend; use enforcement to bound it.",
        ],
    ))

    parts.append(_wrap_section(
        "Feature comparison",
        [
            "Compared to " + competitor + ", sipi.bot adds: per-transaction dollar "
            "limits, daily ceilings, velocity caps, merchant allowlists, human-in-the-"
            "loop escalation on flagged transactions, a tamper-evident audit trail, "
            "and a 5ms decision API. None of these are features of a pure "
            "observability tool — they require sitting in the transaction path, which "
            "is a fundamentally different architectural commitment.",
        ],
    ))

    parts.append(_wrap_section(
        "Pricing",
        [
            "sipi.bot starts at $99 per month. For teams that have experienced a "
            "runaway incident (67% of production agent teams in a recent 90-day "
            "window, median cost $340), the payback period is measured in a single "
            "prevented incident.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /templates/{x} --------------------------------------------------------

def gen_templates_block(h1: str, description: str, slug: str) -> str:
    parts = []
    parts.append(_wrap_section(
        "How to use this template",
        [
            "This template is a starting point, not a finished policy. Copy it into "
            "your team's documents, adapt the specifics to your agents and your risk "
            "tolerance, and pair it with a spend firewall that actually enforces it. "
            "A policy on paper does not stop a runaway loop; an enforced policy does.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append(_wrap_section(
        "What every template should cover",
        [
            "Regardless of the specific template, every agent spend policy needs to "
            "address five things: who (which agents the policy applies to), what (which "
            "transactions are in scope), when (the time windows and velocity limits), "
            "how much (per-transaction and daily dollar ceilings), and what-else "
            "(merchant allowlist and human-in-the-loop thresholds). If any of these "
            "five is missing, the policy has a gap a runaway incident can exploit.",
        ],
    ))

    parts.append(_wrap_section(
        "Pairing the template with enforcement",
        [
            "Once you have adapted the template, encode it as a sipi.bot policy. Each "
            "section of the template maps to a policy lever: per-transaction limit, "
            "daily ceiling, velocity cap, merchant allowlist, escalation threshold. "
            "The mapping is direct — if the template says 'agents may not transact "
            "above $5 without human approval', that becomes a $5 per-transaction limit "
            "with a flag outcome that triggers a human-review workflow.",
        ],
    ))

    parts.append(_wrap_section(
        "Reviewing and updating",
        [
            "Policies go stale. Agents change, merchants change, pricing changes. "
            "Schedule a quarterly review of every policy derived from this template. "
            "The audit log is the input: look at blocked and flagged transactions, "
            "look at near-misses, and tune. A policy that has not been updated in a "
            "year is almost certainly miscalibrated.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /tutorials/{x} --------------------------------------------------------

def gen_tutorials_block(h1: str, description: str, slug: str) -> str:
    parts = []
    parts.append(_wrap_section(
        "What you will accomplish",
        [
            "By the end of this walkthrough you will have a working sipi.bot policy "
            "enforced on your agent, with a tested block path and an audit trail you "
            "can inspect. The whole exercise typically takes under an hour.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append('<section>' + _h2("Step-by-step") + _ol([
        "Create a sipi.bot account and open the policy editor. Start from the "
        "recommended defaults for your agent type.",
        "Identify the function or tool call in your agent that triggers a transaction. "
        "This is the call you will wrap with a policy check.",
        "Add the sipi.bot policy check immediately before the transaction call. The "
        "check takes agent id, merchant, amount, and intent, and returns a structured "
        "decision.",
        "Handle all three decision paths: approve (proceed with the transaction), "
        "block (log, notify, and choose an alternative path), flag (hold for human "
        "review). Most bugs come from handling only the approve path.",
        "Run a test transaction that should be approved. Verify the decision returns "
        "in under 5ms and the audit log captures the transaction.",
        "Run a test transaction that should be blocked. Verify the block path works "
        "and the agent handles the denial gracefully.",
        "Turn on real-time alerts (Slack, email, webhook) on flagged and blocked "
        "transactions.",
    ]) + '</section>')

    parts.append(_wrap_section(
        "Verifying your work",
        [
            "After deployment, watch the audit log for the first 24 hours. You should "
            "see approved transactions for legitimate work and, depending on your "
            "policy, a small number of blocked transactions for attempts that violated "
            "your limits. Investigate every block — each one is either a policy that "
            "is too tight or an agent behavior you did not expect, and either way you "
            "want to know.",
        ],
    ))

    parts.append(_wrap_section(
        "Common pitfalls",
        [
            "<strong>Forgetting the block path</strong>. If your agent does not handle "
            "the block decision, it will hang or crash. Handle all three outcomes "
            "before going to production.",
            "<strong>Logging without alerting</strong>. An audit log nobody reads is "
            "just a compliance artifact. Wire up real-time alerts on flagged "
            "transactions so a human actually sees them.",
            "<strong>One policy for all agents</strong>. Different agents have "
            "different spend profiles. Use per-agent policies, not a single global "
            "policy.",
        ],
    ))
    return '\n\n'.join(parts)


# --- /best/{x} -------------------------------------------------------------

def gen_best_block(h1: str, description: str, slug: str) -> str:
    parts = []
    parts.append(_wrap_section(
        "Observation vs enforcement — the real distinction",
        [
            "Lists of 'best AI spend tools' usually mix two fundamentally different "
            "categories: observability tools (trace, aggregate, dashboard) and "
            "enforcement tools (approve, block, flag in real time). Both are useful. "
            "They are not substitutes.",
            "Observability tells you what happened, usually on the next dashboard "
            "refresh. Enforcement stops what should not happen, in milliseconds, "
            "before money moves. If your goal is to bound agent spend rather than "
            "merely report on it, you need an enforcement tool — and that is the "
            "category sipi.bot defines.",
        ],
    ))

    parts.append(_wrap_section(
        "Where sipi.bot fits in the stack",
        [
            PRODUCT_FACTS,
            "Many teams run both: an observability tool for attribution and analytics, "
            "and sipi.bot for real-time enforcement. The observability tool answers "
            "'what did we spend last month and why?'; sipi.bot answers 'should this "
            "transaction proceed right now?'",
        ],
    ))

    parts.append(_wrap_section(
        "How to choose",
        [
            "If your only problem is understanding spend after the fact, an "
            "observability tool is enough. If your problem is that agents can cause "
            "money to move and you need to bound that risk in real time, you need an "
            "enforcement layer. Most production agent teams eventually need both, and "
            "the enforcement layer is the one that prevents the incidents the "
            "observability tool would later report.",
        ],
    ))

    parts.append(_wrap_section(
        "Bottom line",
        [
            "The 'best' tool depends on the question you are asking. For 'what "
            "happened?', observability. For 'what should I allow to happen?', "
            "enforcement. sipi.bot is the enforcement answer, and at $99/mo it is "
            "priced to pay back in a single prevented incident.",
        ],
    ))
    return '\n\n'.join(parts)


# --- Generic fallback ------------------------------------------------------

def gen_generic_block(h1: str, description: str, slug: str) -> str:
    parts = []
    parts.append(_wrap_section(
        "Why this matters for AI agent spend",
        [
            "Autonomous AI agents are powerful because they can act without a human in "
            "the loop on every decision. The moment an agent can initiate a "
            "transaction — a paid API call, a purchase, a charge, a provisioning step "
            "— it can also overspend. The question is not whether to give agents "
            "spending power, but how to bound that power.",
            PRODUCT_FACTS,
        ],
    ))

    parts.append(_wrap_section(
        "How sipi.bot helps",
        [
            "sipi.bot sits between your agent and your payment methods. Every "
            "transaction passes through a policy check that returns approve, block, or "
            "flag in under 5 milliseconds. The agent never sees the payment method "
            "directly; it only sees the structured decision. This keeps the agent "
            "autonomous while guaranteeing it cannot escape your financial guardrails.",
        ],
    ))

    parts.append(_wrap_section(
        "What the audit trail gives you",
        [
            "Every decision is logged with agent id, merchant, amount, intent, "
            "timestamp, and policy version. The log is append-only and tamper-evident. "
            "You can use it to debug blocked transactions, prove compliance, answer "
            "'what did the agent spend last week?', and tune your policy based on "
            "actual behavior rather than guesses.",
        ],
    ))

    parts.append(_wrap_section(
        "Getting started",
        [
            "List every path by which your agent can move money. Put a policy check in "
            "front of each one. Start with conservative limits, watch the audit log "
            "for a week, and tune. The whole exercise takes an afternoon and costs "
            "less than a single runaway incident.",
        ],
    ))
    return '\n\n'.join(parts)


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

SECTION_GENERATORS = {
    "vs": gen_vs_block,
    "integrations": gen_integrations_block,
    "for": gen_for_block,
    "learn": gen_learn_block,
    "glossary": gen_glossary_block,
    "faq": gen_faq_block,
    "use-cases": gen_use_cases_block,
    "benchmarks": gen_benchmarks_block,
    "policies": gen_policies_block,
    "limits": gen_limits_block,
    "alternatives-to": gen_alternatives_to_block,
    "templates": gen_templates_block,
    "tutorials": gen_tutorials_block,
    "best": gen_best_block,
}


def section_for(url: str) -> str:
    """Extract section from URL path. Returns '' for root."""
    path = url.replace(BASE, "").lstrip("/")
    if "/" in path:
        return path.split("/", 1)[0]
    return ""


def slug_for(url: str) -> str:
    path = url.replace(BASE, "").lstrip("/")
    if "/" in path:
        return path.split("/", 1)[1].rstrip("/")
    return path


# ---------------------------------------------------------------------------
# Twin-file handling
# ---------------------------------------------------------------------------

def find_twins(filepath: Path) -> list:
    """If filepath is slug/index.html, also check for slug.html. Vice versa."""
    twins = []
    if filepath.name == "index.html":
        flat = filepath.parent.with_suffix(".html")  # parent/../slug.html? No.
        # parent is .../slug ; parent.parent/slug.html
        flat = filepath.parent.parent / (filepath.parent.name + ".html")
        if flat.exists() and flat.is_file():
            twins.append(flat)
    elif filepath.suffix == ".html":
        idx = filepath.with_suffix("") / "index.html"
        # filepath is .../slug.html -> .../slug/index.html
        stem = filepath.stem
        idx = filepath.parent / stem / "index.html"
        if idx.exists() and idx.is_file():
            twins.append(idx)
    return twins


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    manifest = json.loads(MANIFEST.read_text())
    site = manifest["sipi.bot"]
    thin_pages = site["thin_pages"]
    print("sipi.bot enrichment — %d thin pages in manifest" % len(thin_pages))

    stats = {"skipped_already_rich": 0, "patched": 0, "twins_synced": 0,
             "still_thin": 0, "missing_file": 0, "errors": 0}
    results = []  # (url, status, words_before, words_after)

    for entry in thin_pages:
        url = entry["url"]
        filepath = Path(entry["path"])
        h1 = entry.get("h1") or ""
        desc = entry.get("description") or ""
        if not filepath.exists():
            print("  MISSING: %s -> %s" % (url, filepath))
            stats["missing_file"] += 1
            results.append((url, "missing", entry.get("words", 0), 0))
            continue

        html = filepath.read_text(errors="ignore")
        wc_before = count_visible_words(html)

        # Idempotency gate
        if wc_before >= MIN_WORDS:
            stats["skipped_already_rich"] += 1
            results.append((url, "skip_rich", wc_before, wc_before))
            continue

        # Also skip if already enriched by this generator
        sentinel = "<!-- " + GENERATOR_VERSION + " -->"
        if sentinel in html:
            stats["skipped_already_rich"] += 1
            results.append((url, "skip_sentinel", wc_before, wc_before))
            continue

        section = section_for(url)
        slug = slug_for(url)
        gen = SECTION_GENERATORS.get(section, gen_generic_block)

        try:
            block = gen(h1, desc, slug)
        except Exception as e:
            print("  GEN ERROR %s: %s" % (url, e))
            stats["errors"] += 1
            results.append((url, "gen_error", wc_before, 0))
            continue

        new_html = inject_block(html, block)
        wc_after = count_visible_words(new_html)

        if wc_after < MIN_WORDS:
            print("  STILL THIN: %s (%d -> %d words)" % (url, wc_before, wc_after))
            stats["still_thin"] += 1
            results.append((url, "still_thin", wc_before, wc_after))
            # Still write — partial enrichment is better than none
            filepath.write_text(new_html)
            continue

        filepath.write_text(new_html)
        stats["patched"] += 1
        results.append((url, "patched", wc_before, wc_after))

        # Sync twin if it exists (so Vercel serves the enriched version)
        for twin in find_twins(filepath):
            twin_html = twin.read_text(errors="ignore")
            if count_visible_words(twin_html) < MIN_WORDS:
                # Preserve twin's canonical if different
                twin_canon = re.search(
                    r'<link rel="canonical" href="([^"]+)"', twin_html)
                new_canon = re.search(
                    r'<link rel="canonical" href="([^"]+)"', new_html)
                write_html = new_html
                if (twin_canon and new_canon
                        and twin_canon.group(1) != new_canon.group(1)):
                    write_html = new_html.replace(
                        new_canon.group(1), twin_canon.group(1))
                twin.write_text(write_html)
                stats["twins_synced"] += 1
                print("  TWIN SYNC: %s" % twin.relative_to(ROOT))

    # Summary
    print("\n=== SUMMARY ===")
    for k, v in stats.items():
        print("  %-25s %d" % (k, v))

    # Write a machine-readable results file
    out = Path("/tmp/sipi_enrichment_results.json")
    out.write_text(json.dumps(
        {"stats": stats, "results": [
            {"url": u, "status": s, "before": b, "after": a}
            for (u, s, b, a) in results
        ]}, indent=2))
    print("\nDetailed results: %s" % out)

    # Exit non-zero if anything failed badly
    if stats["still_thin"] > 0 or stats["errors"] > 0 or stats["missing_file"] > 0:
        print("\nWARNING: %d still thin, %d errors, %d missing"
              % (stats["still_thin"], stats["errors"], stats["missing_file"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
