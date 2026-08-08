"""Round 37 pSEO generator — sipi.bot (2026-08-08).

Eighteenth round. 13 static pages (12 repo-root bare + 1 public) + 1 blog.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round37_data import (  # noqa: E402
    COST_OF, VS, FAQ, SECTORS, USE_CASES, GLOSSARY, TEMPLATES, ANSWERS,
)


def main():
    total = 0
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "NIM & Llama")
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "Guardrails & agent payments")
    total += build_group("faq", FAQ, "FAQ", "/faq/",
                         "At a glance", "The product, plainly")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "Automotive & nonprofits")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "Content & procurement")
    total += build_group("glossary", GLOSSARY, "Glossary", "/glossary/",
                         None, "Routing")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "Key rotation")
    total += build_public("answers", ANSWERS, "LLM gateways")
    print(f"\n✓ Round 37 complete — {total} new pages")


if __name__ == "__main__":
    main()
