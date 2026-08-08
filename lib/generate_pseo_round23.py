"""Round 23 pSEO generator — sipi.bot (2026-08-08).

Fourth gap-fill (417 URLs → ~459). Depth round — 42 leaves across 12 EXISTING
page types, zero new plumbing (no api.py / Dockerfile / sitemap-prefix edits).
Hub patches only.

Reuses Round 20 renderers (write_leaf) and Round 21's patch_hub.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round20 import write_leaf, build_leaf_body  # noqa: E402
from generate_pseo_round21 import patch_hub  # noqa: E402
from generate_pseo_round23_data import (  # noqa: E402
    INTEGRATIONS, FOR, USE_CASES, GLOSSARY, BENCHMARKS, BEST, TEMPLATES,
    REDFLAGS, SCENARIOS, COST_OF, HOW_TO, ALTERNATIVES_TO,
)


def _body(meta, crumb_label, crumb_href, table_h2):
    m = dict(meta)
    m["crumb"] = (("Home", "/"), (crumb_label, crumb_href), (meta["h1"], None))
    m["table_h2"] = table_h2
    return build_leaf_body(m)


def _patch(prefix, items, heading):
    patch_hub(prefix, items, "h1", "lead", heading)
    print(f"  {prefix}/ hub patched")


def build_group(prefix, items, crumb_label, crumb_href, table_h2, heading):
    for it in items:
        body = _body(it, crumb_label, crumb_href, table_h2)
        write_leaf(prefix, it["slug"], it["title"], it["desc"], body,
                   it["faqs"], it["related"])
    _patch(prefix, items, heading)
    print(f"{prefix}/: {len(items)} pages")
    return len(items)


def main():
    total = 0
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Coding agents & routers")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "More teams")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "More use cases")
    total += build_group("glossary", GLOSSARY, "Glossary", "/glossary/",
                         None, "Agent economy terms")
    total += build_group("benchmarks", BENCHMARKS, "Benchmarks", "/benchmarks/",
                         "At a glance", "2026 cost data")
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "New in 2026")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "More templates")
    total += build_group("redflags", REDFLAGS, "Red flags", "/redflags/",
                         "At a glance", "Bills & logs")
    total += build_group("scenarios", SCENARIOS, "Scenarios", "/scenarios/",
                         "The rule set", "Policy in practice")
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "API pricing")
    total += build_group("how-to", HOW_TO, "How-to", "/how-to/",
                         None, "Guides")
    total += build_group("alternatives-to", ALTERNATIVES_TO, "Alternatives", "/alternatives-to/",
                         "At a glance", "Agent spend alternatives")
    print(f"\n✓ Round 23 complete — {total} new pages")


if __name__ == "__main__":
    main()
