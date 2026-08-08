"""Round 31 pSEO generator — sipi.bot (2026-08-08).

Twelfth round. 15 static pages (13 repo-root bare + 2 public) + 1 blog post.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round31_data import (  # noqa: E402
    VS, INTEGRATIONS, COST_OF, FOR, USE_CASES, ANSWERS, GLOSSARY,
)


def main():
    total = 0
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "Cloud AI platforms")
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Cloud AI platforms")
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "Inference providers")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "More teams")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "More use cases")
    total += build_group("glossary", GLOSSARY, "Glossary", "/glossary/",
                         None, "Agent economy terms")
    total += build_public("answers", ANSWERS, "Crypto payments & firewall mechanics")
    print(f"\n✓ Round 31 complete — {total} new pages")


if __name__ == "__main__":
    main()
