"""Round 28 pSEO generator — sipi.bot (2026-08-08).

Ninth round. Voice-agent cluster + meeting agents + filler gaps.
17 static pages (15 repo-root bare + 2 public slash) + 2 blog posts.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import (  # noqa: E402
    _body, build_group, build_public,
)
from generate_pseo_round28_data import (  # noqa: E402
    INTEGRATIONS, VS, USE_CASES, COST_OF, FOR, SECTORS, BENCHMARKS, BEST,
    FAQ, ANSWERS, CHECKLISTS,
)


def main():
    total = 0
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Voice & agents")
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "Voice & meetings")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "Voice & meetings")
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "Voice & meetings")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "More teams")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "More sectors")
    total += build_group("benchmarks", BENCHMARKS, "Benchmarks", "/benchmarks/",
                         "At a glance", "Token shapes")
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "Frameworks")
    total += build_group("faq", FAQ, "FAQ", "/faq/",
                         "At a glance", "The firewall, plainly")
    total += build_public("answers", ANSWERS, "Choosing a firewall")
    total += build_public("checklists", CHECKLISTS, "Self-hosting")
    print(f"\n✓ Round 28 complete — {total} new pages")


if __name__ == "__main__":
    main()
