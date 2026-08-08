"""Round 29 pSEO generator — sipi.bot (2026-08-08).

Tenth round. 19 static pages (18 repo-root bare + 1 public) + 2 blog posts.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round29_data import (  # noqa: E402
    INTEGRATIONS, COST_OF, FOR, TEMPLATES, GLOSSARY, HOW_TO, BEST,
    BENCHMARKS, PRICING_QUESTIONS,
)


def main():
    total = 0
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Coding agents & automation")
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "API pricing")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "More teams")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "More templates")
    total += build_group("glossary", GLOSSARY, "Glossary", "/glossary/",
                         None, "Agent economy terms")
    total += build_group("how-to", HOW_TO, "How-to", "/how-to/",
                         None, "Guides")
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "Incident response")
    total += build_group("benchmarks", BENCHMARKS, "Benchmarks", "/benchmarks/",
                         "At a glance", "Failure costs")
    total += build_group("pricing-questions", PRICING_QUESTIONS, "Pricing questions",
                         "/pricing-questions/", "At a glance", "Compliance")
    print(f"\n✓ Round 29 complete — {total} new pages")


if __name__ == "__main__":
    main()
