"""Round 33 pSEO generator — sipi.bot (2026-08-08).

Fourteenth round. 13 static pages (12 repo-root bare + 1 public) + 1 blog.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round33_data import (  # noqa: E402
    COST_OF, INTEGRATIONS, LEARN, FAQ, BEST, BENCHMARKS, TEMPLATES, ANSWERS,
)


def main():
    total = 0
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "Provider costs")
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Autonomous agents")
    total += build_group("learn", LEARN, "Learn", "/learn/",
                         None, "Agent fundamentals")
    total += build_group("faq", FAQ, "FAQ", "/faq/",
                         "At a glance", "Budgets vs firewall")
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "Cost tracking")
    total += build_group("benchmarks", BENCHMARKS, "Benchmarks", "/benchmarks/",
                         "At a glance", "Local vs hosted")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "Reporting")
    total += build_public("answers", ANSWERS, "Budgeting")
    print(f"\n✓ Round 33 complete — {total} new pages")


if __name__ == "__main__":
    main()
