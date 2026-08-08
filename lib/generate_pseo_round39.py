"""Round 39 pSEO generator — sipi.bot (2026-08-08).

Twentieth round. 14 static pages (13 repo-root bare + 1 public) + 1 blog.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round39_data import (  # noqa: E402
    COST_OF, BEST, SECTORS, USE_CASES, VS, INTEGRATIONS, ANSWERS, FOR,
)


def main():
    total = 0
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "Image & memory")
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "Image APIs")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "Public sector")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "Moderation & legal review")
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "Model hosting")
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Model platforms")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "Platform teams")
    total += build_public("answers", ANSWERS, "Agentic AI cost")
    print(f"\n✓ Round 39 complete — {total} new pages")


if __name__ == "__main__":
    main()
