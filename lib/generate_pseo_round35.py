"""Round 35 pSEO generator — sipi.bot (2026-08-08).

Sixteenth round. 11 static pages (9 repo-root bare + 2 public) + 1 blog.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round35_data import (  # noqa: E402
    INTEGRATIONS, VS, ANSWERS, GLOSSARY, TEMPLATES, SCENARIOS, BEST,
)


def main():
    total = 0
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Local AI stack")
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "Payment rails")
    total += build_group("glossary", GLOSSARY, "Glossary", "/glossary/",
                         None, "Control terms")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "Policy templates")
    total += build_group("scenarios", SCENARIOS, "Scenarios", "/scenarios/",
                         None, "Rogue agents")
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "Agent security")
    total += build_public("answers", ANSWERS, "Build cost & worth it")
    print(f"\n✓ Round 35 complete — {total} new pages")


if __name__ == "__main__":
    main()
