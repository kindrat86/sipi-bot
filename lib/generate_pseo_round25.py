"""Round 25 pSEO generator — sipi.bot (2026-08-08).

Sixth round. 26 static pages across 9 thin sections + 3 blog posts added via
lib/generate_content.py (POSTS + _body_for) + RSS idempotency fix.
All pages land in EXISTING repo-root dirs — no plumbing changes.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round20 import write_leaf, build_leaf_body  # noqa: E402
from generate_pseo_round21 import patch_hub  # noqa: E402
from generate_pseo_round25_data import (  # noqa: E402
    TUTORIALS, POLICIES, LIMITS, LEARN, GUIDES, SECTORS, USE_CASES,
    GLOSSARY, SCENARIOS,
)


def _body(meta, crumb_label, crumb_href, table_h2):
    m = dict(meta)
    m["crumb"] = (("Home", "/"), (crumb_label, crumb_href), (meta["h1"], None))
    m["table_h2"] = table_h2
    return build_leaf_body(m)


def build_group(prefix, items, crumb_label, crumb_href, table_h2, heading):
    for it in items:
        body = _body(it, crumb_label, crumb_href, table_h2)
        write_leaf(prefix, it["slug"], it["title"], it["desc"], body,
                   it["faqs"], it["related"])
    patch_hub(prefix, items, "h1", "lead", heading)
    print(f"{prefix}/: {len(items)} pages + hub patched")
    return len(items)


def main():
    total = 0
    total += build_group("tutorials", TUTORIALS, "Tutorials", "/tutorials/",
                         None, "Integrations & rules")
    total += build_group("policies", POLICIES, "Policies", "/policies/",
                         None, "Rule-type policies")
    total += build_group("limits", LIMITS, "Limits", "/limits/",
                         "At a glance", "Limit types")
    total += build_group("learn", LEARN, "Learn", "/learn/",
                         None, "Agent economy")
    total += build_group("guides", GUIDES, "Guides", "/guides/",
                         None, "New guides")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "More sectors")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "More use cases")
    total += build_group("glossary", GLOSSARY, "Glossary", "/glossary/",
                         None, "Agent economy terms")
    total += build_group("scenarios", SCENARIOS, "Scenarios", "/scenarios/",
                         "The rule set", "Policy in practice")
    print(f"\n✓ Round 25 static pages complete — {total} new pages")


if __name__ == "__main__":
    main()
