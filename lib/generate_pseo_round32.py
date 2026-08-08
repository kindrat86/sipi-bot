"""Round 32 pSEO generator — sipi.bot (2026-08-08).

Thirteenth round. 13 static pages (12 repo-root bare + 1 public) + 1 blog.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round32_data import (  # noqa: E402
    COST_OF, VS, INTEGRATIONS, LEARN, FOR, SECTORS, SCENARIOS,
    PRICING_QUESTIONS, ANSWERS,
)


def main():
    total = 0
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "The big API costs")
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "Emerging observability")
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Tool platforms & autonomous")
    total += build_group("learn", LEARN, "Learn", "/learn/",
                         None, "Agent fundamentals")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "More teams")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "More sectors")
    total += build_group("scenarios", SCENARIOS, "Scenarios", "/scenarios/",
                         None, "Security scenarios")
    total += build_group("pricing-questions", PRICING_QUESTIONS, "Pricing questions",
                         "/pricing-questions/", "At a glance", "Open source")
    total += build_public("answers", ANSWERS, "Agent cost basics")
    print(f"\n✓ Round 32 complete — {total} new pages")


if __name__ == "__main__":
    main()
