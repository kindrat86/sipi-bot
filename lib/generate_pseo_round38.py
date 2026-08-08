"""Round 38 pSEO generator — sipi.bot (2026-08-08).

Nineteenth round. 13 static pages (12 repo-root bare + 1 public) + 1 blog.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round38_data import (  # noqa: E402
    COST_OF, BEST, INTEGRATIONS, SECTORS, FOR, TEMPLATES, REDFLAGS,
    USE_CASES, ANSWERS,
)


def main():
    total = 0
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "Voice & audio")
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "Voice platforms")
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Voice & audio")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "Pharma & utilities")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "Budget owners")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "Risk assessment")
    total += build_group("redflags", REDFLAGS, "Red flags", "/redflags/",
                         None, "Voice agents")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "Sales agents")
    total += build_public("answers", ANSWERS, "Agent payments")
    print(f"\n✓ Round 38 complete — {total} new pages")


if __name__ == "__main__":
    main()
