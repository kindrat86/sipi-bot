"""Round 21 pSEO generator — sipi.bot (2026-08-08).

Gap-fill after Round 20 (346 URLs). Adds:
  errors/      (NEW type, 10 pages + hub)  — real API error-code reference
  integrations/ (+6)                       — semantic-kernel, google-adk,
                                             aws-bedrock-agents, dify, flowise, agentops
  for/         (+5)                        — finance-teams, platform-engineers,
                                             ml-engineers, security-engineers, ctos
  use-cases/   (+4)                        — agentic-commerce, sales-development-agents,
                                             automated-qa-testing, backoffice-automation
  vs/          (+4)                        — agentops, arize-phoenix, stripe-billing, laminar-ai
  glossary/    (+6)                        — agentic-payment, x402, ap2, agent-wallet,
                                             spend-approval, overage-tier

Reuses Round 20 renderers (lib/generate_pseo_round20.py helpers).
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round20 import (  # noqa: E402
    esc, write_leaf, write_hub, build_leaf_body, cta, crumbs,
)
from generate_pseo_round21_data import (  # noqa: E402
    ERRORS, INTEGRATIONS, FOR, USE_CASES, VS, GLOSSARY, ERRORS_HUB,
)

# ------------------------------------------------------------------- builders
def build_errors():
    count = 0
    for e in ERRORS:
        meta = dict(e)
        meta["crumb"] = (("Home", "/"), ("Errors", "/errors/"), (e["h1"], None))
        meta["table_h2"] = "At a glance"
        body = build_leaf_body(meta)
        write_leaf("errors", e["slug"], e["title"], e["desc"], body, e["faqs"], e["related"])
        count += 1
    cards = [(f"{e['code_name']} — HTTP {e['status'].split()[0]}",
              f"/errors/{e['slug']}", e["lead"]) for e in ERRORS]
    write_hub("errors", ERRORS_HUB["title"], ERRORS_HUB["desc"],
              ERRORS_HUB["h1"], ERRORS_HUB["lead"], cards)
    print(f"errors/: hub + {count} pages")
    return count + 1


def build_integrations():
    count = 0
    for i in INTEGRATIONS:
        meta = dict(i)
        meta["crumb"] = (("Home", "/"), ("Integrations", "/integrations/"), (i["h1"], None))
        meta["table_h2"] = "Rules that fit this workload"
        body = build_leaf_body(meta)
        write_leaf("integrations", i["slug"], i["title"], i["desc"], body, i["faqs"], i["related"])
        count += 1
    # Rebuild hub with ALL integration slugs (18): known descs + one-liners.
    known = {i["slug"]: i for i in INTEGRATIONS}
    legacy = {
        "anthropic": ("Anthropic", "Claude API spend control."),
        "autogen": ("AutoGen", "Multi-agent conversation framework."),
        "crewai": ("CrewAI", "Role-based agent crews."),
        "google-gemini": ("Google Gemini", "Gemini API agents."),
        "langchain": ("LangChain", "The classic agent framework."),
        "openai": ("OpenAI", "OpenAI API spend control."),
        "stripe": ("Stripe", "Gate spend that settles through Stripe."),
        "vercel-ai-sdk": ("Vercel AI SDK", "AI streaming in Next.js apps."),
        "sipi-bot-plus-openai-agents-sdk": ("OpenAI Agents SDK recipe", "Plus-schema recipe."),
        "sipi-bot-plus-stripe": ("Stripe recipe", "Plus-schema recipe."),
    }
    slugs = []
    for d in sorted(os.listdir(os.path.join(ROOT, "integrations"))):
        if os.path.isdir(os.path.join(ROOT, "integrations", d)) and d != "index":
            slugs.append(d)
    cards = []
    for slug in slugs:
        if slug in known:
            cards.append((known[slug]["h1"], f"/integrations/{slug}", known[slug]["lead"]))
        elif slug in legacy:
            name, blurb = legacy[slug]
            cards.append((f"Spend Control for {name}", f"/integrations/{slug}", blurb))
        else:
            cards.append((slug.replace("-", " ").title(), f"/integrations/{slug}", "Integration guide."))
    write_hub(
        "integrations",
        "sipi.bot Integrations — MCP, Claude Code, Cursor & More",
        "Spend control integrations for the frameworks agents are built on: MCP, Claude Code, Cursor, LangGraph, LangChain, CrewAI, Semantic Kernel, Dify and more.",
        "sipi.bot Integrations",
        "sipi.bot plugs into whatever your agents run on — as an MCP tool, an HTTP API, or a CLI. Add the guard before the spend.",
        cards,
    )
    print(f"integrations/: hub rebuilt (all slugs) + {count} pages")
    return count + 1


def build_for():
    count = 0
    for f_ in FOR:
        meta = dict(f_)
        meta["crumb"] = (("Home", "/"), ("For teams", "/for/"), (f_["h1"], None))
        meta["table_h2"] = "What you get"
        body = build_leaf_body(meta)
        write_leaf("for", f_["slug"], f_["title"], f_["desc"], body, f_["faqs"], f_["related"])
        count += 1
    patch_hub("for", FOR, "h1", "lead", "More teams")
    print(f"for/: {count} pages + hub patched")
    return count


def build_use_cases():
    count = 0
    for u in USE_CASES:
        meta = dict(u)
        meta["crumb"] = (("Home", "/"), ("Use cases", "/use-cases/"), (u["h1"], None))
        meta["table_h2"] = "Spend map"
        body = build_leaf_body(meta)
        write_leaf("use-cases", u["slug"], u["title"], u["desc"], body, u["faqs"], u["related"])
        count += 1
    # Rebuild hub (small, absolute-href format differs from the patch marker).
    known = {u["slug"]: u for u in USE_CASES}
    legacy = {
        "ai-agency-operations": "AI agencies running client agents on budget.",
        "ai-startups": "Startups shipping agents without surprise bills.",
        "customer-support-bots": "Support bots at scale without overage.",
        "development-teams": "Dev teams controlling tool spend.",
        "devtools-startups": "Devtools companies with agent usage.",
        "enterprise": "Enterprise agent governance.",
        "enterprise-agent-deployments": "Large-scale agent rollouts.",
        "multi-agent-budgets": "Fleet-wide budgets for agent swarms.",
        "research-agents": "Research agents buying data and compute.",
        "solopreneur-agent-safety": "Solo builders protecting the card.",
        "trading-bots": "Trading agents with hard caps.",
    }
    slugs = []
    for d in sorted(os.listdir(os.path.join(ROOT, "use-cases"))):
        if os.path.isdir(os.path.join(ROOT, "use-cases", d)) and d != "index":
            slugs.append(d)
    cards = []
    for slug in slugs:
        if slug in known:
            cards.append((known[slug]["h1"], f"/use-cases/{slug}", known[slug]["lead"]))
        elif slug in legacy:
            cards.append((slug.replace("-", " ").title(), f"/use-cases/{slug}", legacy[slug]))
        else:
            cards.append((slug.replace("-", " ").title(), f"/use-cases/{slug}", "Use case."))
    write_hub(
        "use-cases",
        "AI Agent Spend Control Use Cases | sipi.bot",
        "Use cases for the pre-spend firewall: agentic commerce, sales development agents, QA fleets, backoffice automation, and more.",
        "Agent Spend Control Use Cases",
        "The shape of spend differs by job. These guides map where agents spend, the failure modes, and the first rules to turn on.",
        cards,
    )
    print(f"use-cases/: hub rebuilt (all slugs) + {count} pages")
    return count + 1


def build_vs():
    count = 0
    for v in VS:
        meta = dict(v)
        meta["crumb"] = (("Home", "/"), ("Comparisons", "/vs/"), (v["h1"], None))
        meta["table_h2"] = "Side by side"
        body = build_leaf_body(meta)
        write_leaf("vs", v["slug"], v["title"], v["desc"], body, v["faqs"], v["related"])
        count += 1
    patch_hub("vs", VS, "h1", "lead", "More comparisons")
    print(f"vs/: {count} pages + hub patched")
    return count


def build_glossary():
    count = 0
    for g in GLOSSARY:
        meta = dict(g)
        meta["crumb"] = (("Home", "/"), ("Glossary", "/glossary/"), (g["h1"], None))
        meta["table_h2"] = None  # no table
        body = build_leaf_body(meta)
        write_leaf("glossary", g["slug"], g["title"], g["desc"], body, g["faqs"], g["related"])
        count += 1
    patch_hub("glossary", GLOSSARY, "h1", "lead", "Agent payments & spend")
    print(f"glossary/: {count} pages + hub patched")
    return count


def patch_hub(prefix, items, title_key, lead_key, heading):
    """Insert new cards into an existing hub before the guide/home links marker."""
    hub_path = os.path.join(ROOT, prefix, "index.html")
    if not os.path.exists(hub_path):
        print(f"  !! {prefix}/index.html missing — skipped hub patch")
        return
    with open(hub_path, encoding="utf-8") as f:
        hub = f.read()
    first_slug = items[0]["slug"]
    if f"/{prefix}/{first_slug}" in hub:
        print(f"  !! {prefix} hub already contains new pages — skipped")
        return
    cards = "".join(
        f'<div class="card"><h3><a href="/{prefix}/{it["slug"]}">{esc(it[title_key])}</a></h3>'
        f"<p>{esc(it[lead_key])}</p></div>"
        for it in items
    )
    block = f'<h2>{heading}</h2>\n<div class="grid2">\n{cards}\n</div>\n'
    marker = '<div style="margin-top:2rem">'
    if marker in hub:
        hub = hub.replace(marker, block + marker)
    else:
        hub = hub.replace("</body>", block + "</body>")
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(hub)


def main():
    total = 0
    total += build_errors()
    total += build_integrations()
    total += build_for()
    total += build_use_cases()
    total += build_vs()
    total += build_glossary()
    print(f"\n✓ Round 21 complete — {total} new files (leaves + hubs)")


if __name__ == "__main__":
    main()
