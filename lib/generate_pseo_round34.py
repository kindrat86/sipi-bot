"""Round 34 pSEO generator — sipi.bot (2026-08-08).

Fifteenth round. Link-integrity fixes: 6 pages created from the internal-link
audit (all referenced-but-404). All repo-root bare canonical.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from generate_pseo_round27 import build_group  # noqa: E402
from generate_pseo_round34_data import (  # noqa: E402
    COST_OF, HOW_TO, REDFLAGS, INTEGRATIONS,
)


def main():
    total = 0
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "Local serving")
    total += build_group("how-to", HOW_TO, "How-to", "/how-to/",
                         None, "Cost & runaway guides")
    total += build_group("redflags", REDFLAGS, "Red flags", "/redflags/",
                         None, "Key management")
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "OpenClaw & friends")
    print(f"\n✓ Round 34 complete — {total} new pages")


if __name__ == "__main__":
    main()
