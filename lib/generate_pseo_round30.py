"""Round 30 pSEO generator — sipi.bot (2026-08-08).

Eleventh round. 17 static pages (15 repo-root bare + 2 public) + 2 blog posts.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group, build_public  # noqa: E402
from generate_pseo_round30_data import (  # noqa: E402
    VS, INTEGRATIONS, SECTORS, ANSWERS, CHECKLISTS,
)


def main():
    total = 0
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "Metering & observability")
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "App builders & IDEs")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "More sectors")
    total += build_public("answers", ANSWERS, "Agent spend basics")
    total += build_public("checklists", CHECKLISTS, "Voice & MCP security")
    print(f"\n✓ Round 30 complete — {total} new pages")


if __name__ == "__main__":
    main()
