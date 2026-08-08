"""Round 22 pSEO generator — sipi.bot (2026-08-08).

Third gap-fill (382 URLs → ~415). Adds:
  pricing-questions/ (NEW type, 8 pages + hub)  — commercial pricing intent
  vs/        (+4)  — kong-ai-gateway, vercel-ai-gateway, openllmetry, traceloop
  best/      (+4)  — agent payment gateways, guardrails, injection protection, MCP spend
  benchmarks/ (+3) — context cost, cache savings, retry-loop cost patterns
  templates/ (+3)  — approval policy, cost playbook, onboarding brief
  redflags/  (+3 + NEW hub — section previously had no hub → 404 at /redflags/)
  scenarios/ (+3 + NEW hub — section previously had no hub → 404 at /scenarios/)
  faq/       (+4)  — injection, LLM-free engine, framework-agnostic, blocked flow

Reuses Round 20 renderers (write_leaf/write_hub/build_leaf_body) and Round 21's
patch_hub (marker-aware hub patching with </body> fallback).
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round20 import write_leaf, write_hub, build_leaf_body  # noqa: E402
from generate_pseo_round21 import patch_hub  # noqa: E402
from generate_pseo_round22_data import (  # noqa: E402
    PRICING_QUESTIONS, VS, BEST, BENCHMARKS, TEMPLATES, REDFLAGS, SCENARIOS,
    FAQ, PRICING_HUB, REDFLAGS_HUB, SCENARIOS_HUB,
)


def _body(meta, crumb_prefix, crumb_label, crumb_href, table_h2):
    m = dict(meta)
    m["crumb"] = (("Home", "/"), (crumb_label, crumb_href), (meta["h1"], None))
    m["table_h2"] = table_h2
    return build_leaf_body(m)


def build_pricing():
    count = 0
    for p in PRICING_QUESTIONS:
        body = _body(p, None, "Pricing questions", "/pricing-questions/", "At a glance")
        write_leaf("pricing-questions", p["slug"], p["title"], p["desc"], body,
                   p["faqs"], p["related"])
        count += 1
    cards = [(p["h1"], f"/pricing-questions/{p['slug']}", p["lead"]) for p in PRICING_QUESTIONS]
    write_hub("pricing-questions", PRICING_HUB["title"], PRICING_HUB["desc"],
              PRICING_HUB["h1"], PRICING_HUB["lead"], cards)
    print(f"pricing-questions/: hub + {count} pages")
    return count + 1


def build_vs():
    for v in VS:
        body = _body(v, None, "Comparisons", "/vs/", "Side by side")
        write_leaf("vs", v["slug"], v["title"], v["desc"], body, v["faqs"], v["related"])
    patch_hub("vs", VS, "h1", "lead", "Gateways & observability")
    print(f"vs/: {len(VS)} pages + hub patched")
    return len(VS)


def build_best():
    for b in BEST:
        body = _body(b, None, "Best-of", "/best/", "At a glance")
        write_leaf("best", b["slug"], b["title"], b["desc"], body, b["faqs"], b["related"])
    patch_hub("best", BEST, "h1", "lead", "New in 2026")
    print(f"best/: {len(BEST)} pages + hub patched")
    return len(BEST)


def build_benchmarks():
    for b in BENCHMARKS:
        body = _body(b, None, "Benchmarks", "/benchmarks/", "At a glance")
        write_leaf("benchmarks", b["slug"], b["title"], b["desc"], body, b["faqs"], b["related"])
    patch_hub("benchmarks", BENCHMARKS, "h1", "lead", "Cost drivers")
    print(f"benchmarks/: {len(BENCHMARKS)} pages + hub patched")
    return len(BENCHMARKS)


def build_templates():
    for t in TEMPLATES:
        body = _body(t, None, "Templates", "/templates/", None)
        write_leaf("templates", t["slug"], t["title"], t["desc"], body, t["faqs"], t["related"])
    patch_hub("templates", TEMPLATES, "h1", "lead", "More templates")
    print(f"templates/: {len(TEMPLATES)} pages + hub patched")
    return len(TEMPLATES)


def build_redflags():
    for r in REDFLAGS:
        body = _body(r, None, "Red flags", "/redflags/", "At a glance")
        write_leaf("redflags", r["slug"], r["title"], r["desc"], body, r["faqs"], r["related"])
    # Section had NO hub (404 at /redflags/) — build one with all slugs.
    slugs = [r["slug"] for r in REDFLAGS]
    for d in sorted(os.listdir(os.path.join(ROOT, "redflags"))):
        if os.path.isdir(os.path.join(ROOT, "redflags", d)) and d not in slugs:
            slugs.append(d)
    known = {r["slug"]: r for r in REDFLAGS}
    cards = []
    for slug in slugs:
        if slug in known:
            cards.append((known[slug]["h1"], f"/redflags/{slug}", known[slug]["lead"]))
        else:
            cards.append((slug.replace("-", " ").title(), f"/redflags/{slug}", "Warning sign."))
    write_hub("redflags", REDFLAGS_HUB["title"], REDFLAGS_HUB["desc"],
              REDFLAGS_HUB["h1"], REDFLAGS_HUB["lead"], cards)
    print(f"redflags/: hub (new) + {len(REDFLAGS)} pages")
    return len(REDFLAGS) + 1


def build_scenarios():
    for s in SCENARIOS:
        body = _body(s, None, "Scenarios", "/scenarios/", "The rule set")
        write_leaf("scenarios", s["slug"], s["title"], s["desc"], body, s["faqs"], s["related"])
    slugs = [s["slug"] for s in SCENARIOS]
    for d in sorted(os.listdir(os.path.join(ROOT, "scenarios"))):
        if os.path.isdir(os.path.join(ROOT, "scenarios", d)) and d not in slugs:
            slugs.append(d)
    known = {s["slug"]: s for s in SCENARIOS}
    cards = []
    for slug in slugs:
        if slug in known:
            cards.append((known[slug]["h1"], f"/scenarios/{slug}", known[slug]["lead"]))
        else:
            cards.append((slug.replace("-", " ").title(), f"/scenarios/{slug}", "Scenario."))
    write_hub("scenarios", SCENARIOS_HUB["title"], SCENARIOS_HUB["desc"],
              SCENARIOS_HUB["h1"], SCENARIOS_HUB["lead"], cards)
    print(f"scenarios/: hub (new) + {len(SCENARIOS)} pages")
    return len(SCENARIOS) + 1


def build_faq():
    for f_ in FAQ:
        body = _body(f_, None, "FAQ", "/faq/", "At a glance")
        write_leaf("faq", f_["slug"], f_["title"], f_["desc"], body, f_["faqs"], f_["related"])
    patch_hub("faq", FAQ, "h1", "lead", "The firewall, plainly")
    print(f"faq/: {len(FAQ)} pages + hub patched")
    return len(FAQ)


def main():
    total = 0
    total += build_pricing()
    total += build_vs()
    total += build_best()
    total += build_benchmarks()
    total += build_templates()
    total += build_redflags()
    total += build_scenarios()
    total += build_faq()
    print(f"\n✓ Round 22 complete — {total} new files (leaves + hubs)")


if __name__ == "__main__":
    main()
