"""Round 36 pSEO generator — sipi.bot (2026-08-08).

Seventeenth round. 12 static pages (10 repo-root bare + 2 public) + 1 blog.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round36_data import (  # noqa: E402
    BEST, COST_OF, FOR, SECTORS, HOW_TO, GLOSSARY, TEMPLATES, ANSWERS, VS,
)


def main():
    total = 0
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "LLM gateways")
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "xAI")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "Indie hackers")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "Insurance & retail")
    total += build_group("how-to", HOW_TO, "How-to", "/how-to/",
                         None, "Provider selection")
    total += build_group("glossary", GLOSSARY, "Glossary", "/glossary/",
                         None, "Cost & identity terms")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "Provider evaluation")
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "LLM gateways")
    total += build_public("answers", ANSWERS, "Security & fraud")
    print(f"\n✓ Round 36 complete — {total} new pages")


if __name__ == "__main__":
    main()
