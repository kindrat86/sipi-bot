#!/usr/bin/env python3
"""
Remove the fabricated agent-spend survey from sipi.bot.

WHY
---
Found 2026-07-25 by running churnlens's provenance gate across the portfolio.
The benchmarks rest on research that was never done:

  * "survey of 312 production agent teams"        -> no survey was run
  * "survey of 247 AI-native companies"           -> no survey was run
  * "anonymized sipi.bot customer data"           -> there are no customers
  * "~850 production agent deployments"           -> there are no deployments
  * "In our dataset, the top 1% of tasks ..."     -> there is no dataset

Proof: spendfirewall.db ships with 0 rows in `agents`, 0 in `transactions` and
0 in `approvals` (only the 4 default rules). The hosted firewall has evaluated
nothing, so there is no corpus to aggregate, anonymized or otherwise.

The headline claim ("67% of teams had a runaway incident in 90 days, median
cost $340") was syndicated into ~42 files: benchmark pages, FAQ pages, the
glossary, JSON-LD blocks, the JSON feed, and the AEO/social playbooks.

DECISION
--------
Owner chose removal over relabelling. An incidence rate cannot be downgraded to
an "editorial estimate" — "67% of teams" is shaped as a survey finding, so
softening the wording would leave a precise invented statistic in place. This
matches the precedent already recorded in this repo's CLAUDE.md: the fake
Review schema was DELETED, not softened.

WHAT IS KEPT
------------
Only what is checkable: published provider pricing (public/ai-model-costs-2026.csv),
the open-source 53-scenario eval suite, and the qualitative failure-mode taxonomy
(retry loops, prompt injection, unattended sessions) — which is real engineering
knowledge and needs no invented percentage attached to it.

Idempotent. Run from ~/projects/sipi-bot.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv"}
# SBOM/lockfiles/vendored data contain "312"/"247" as hashes and line numbers.
SKIP_SUFFIX_DIRS = ("sbom", "vendor", "site-packages")
SCAN = {".html", ".json", ".md", ".txt", ".csv"}

# --- Syndicated one-liners: exact text -> honest replacement ---------------
# These carry the invented incidence rate into pages that are not benchmarks.
SENTENCES = [
    (
        "Industry survey data from 312 production agent teams found that 67% experienced at least one runaway incident in the previous 90 days, with a median cost of $340 per incident.",
        "Runaway spend is a well-documented failure mode for agents with live payment access — retry loops, prompt-injected purchase chains, and unattended overnight sessions. No reliable industry-wide incidence rate exists, and sipi.bot does not publish one.",
    ),
    (
        "Across production agent teams, the median runaway incident costs $340 and 67% of teams report at least one in the last 90 days.",
        "A runaway agent's cost is bounded only by the limits you set before it spends.",
    ),
    (
        "The risk is not theoretical: 67% of production agent teams report at least one runaway incident in a 90-day window, with a median cost of $340 per incident.",
        "The risk is not theoretical — retry loops and prompt-injected purchase chains are documented failure modes — but its size depends entirely on the caps in front of the agent.",
    ),
    (
        "For teams that have experienced a runaway incident (67% of production agent teams in a recent 90-day window, median cost $340), the payback period is measured in a single prevented incident.",
        "For teams that have experienced a runaway incident, the payback period is measured in a single prevented incident.",
    ),
    (
        "Based on survey data from 312 production agent teams and anonymized evaluation data from sipi.bot customers.",
        "Compiled from published provider pricing and publicly reported incidents.",
    ),
    (
        "Data from anonymized sipi.bot customers and a survey of 312 production agent teams.",
        "Compiled from published provider pricing and publicly reported incidents.",
    ),
    (
        "Anonymized sipi.bot customer data — aggregate spend patterns from teams running the firewall.",
        "Modelled from published provider pricing; sipi.bot has no customer telemetry and collects none.",
    ),
    (
        "Anonymized sipi.bot customer data — per-task cost from teams running the firewall, aggregated by task category.",
        "Modelled from published provider pricing per task category; sipi.bot has no customer telemetry and collects none.",
    ),
    (
        "Anonymized sipi.bot customer data — aggregate decision-log patterns from teams running the hosted firewall.",
        "Illustrative decision-log patterns produced by the open-source eval suite; sipi.bot has no customer telemetry and collects none.",
    ),
    (
        "In our dataset, the top 1% of tasks accounted for 22% of total spend .",
        "In a retry-loop scenario the tail dominates: a single looping task can outspend a day of normal work.",
    ),
    (
        "In our dataset, the top 1% of tasks accounted for 22% of total spend.",
        "In a retry-loop scenario the tail dominates: a single looping task can outspend a day of normal work.",
    ),
    (
        "A single runaway research task that retried 40 times cost one team $340 in 90 seconds.",
        "A research task that retries 40 times costs 40x its single-run price, and does so in seconds.",
    ),
    (
        "The top 1% of tasks account for 22% of total spend — almost all of it retry-loop waste.",
        "Retry-loop waste is where unbounded agent spend concentrates.",
    ),
    (
        "Data is compiled from publicly reported incidents, engineering team surveys, and anonymized patterns from agent deployment logs.",
        "Compiled from published provider pricing and publicly reported incidents. sipi.bot runs no surveys and collects no deployment telemetry.",
    ),
    (
        "Based on aggregated data from agent deployments:",
        "Modelled from published provider pricing:",
    ),
    (
        "Original benchmark data for AI agent spend control: runaway incident frequency, cost per task, token pricing by provider, and agent spend as a percentage of revenue.",
        "Reference figures for AI agent spend control: cost per task, token pricing by provider, and the failure modes that drive runaway spend.",
    ),
    (
        "Original benchmark data for AI agent spend control.",
        "Reference figures for AI agent spend control.",
    ),
    (
        "This benchmark is updated quarterly.",
        "Provider pricing changes often; re-check each provider's pricing page before relying on these figures.",
    ),
]

# --- Phrases that must not survive anywhere (regex -> replacement) ---------
PHRASES = [
    (r"survey of 312 production agent teams", "published provider pricing"),
    (r"312 production agent teams", "published provider pricing"),
    (r"312 teams surveyed\.?", "Modelled from public pricing."),
    (r"a survey of 247 AI-native companies[^.]*\.", "published sources."),
    (r"Survey of 247 AI-native companies[^.]*\.", "Modelled from published provider pricing."),
    (r"247 AI-native companies", "published sources"),
    (r"Data from ~?850 production agent deployments using sipi\.bot's evaluation endpoint \(anonymized, 2026-Q2\)\.",
     "Modelled from published provider pricing; sipi.bot collects no deployment telemetry."),
    (r"anonymized and aggregated transaction data from sipi\.bot's evaluation endpoint \(opt-in, no merchant-level detail exposed\), ",
     ""),
    (r"survey data collected from teams running production agent deployments\.",
     "published provider pricing and documentation."),
    (r"anonymized data from production agent evaluations", "published provider pricing"),
    (r"anonymized and aggregated transaction evaluations", "published provider pricing"),
    (r"anonymized patterns from agent deployment logs", "published provider documentation"),
    (r"spending trend analysis based on anonymized patterns from production agent deployments",
     "spending scenarios modelled from published provider pricing"),
]


def iter_files():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in SCAN:
            continue
        parts = set(p.parts)
        if parts & SKIP_DIRS:
            continue
        if any(d in str(p).lower() for d in SKIP_SUFFIX_DIRS):
            continue
        yield p


def main() -> int:
    changed, total_edits = 0, 0
    for p in iter_files():
        try:
            orig = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        out, n = orig, 0
        for find, repl in SENTENCES:
            if find in out:
                n += out.count(find)
                out = out.replace(find, repl)
        for pat, repl in PHRASES:
            out, k = re.subn(pat, repl, out)
            n += k
        if out != orig:
            p.write_text(out, encoding="utf-8")
            changed += 1
            total_edits += n
            print(f"  {n:3} edit(s)  {p.relative_to(ROOT)}")
    print(f"\n{total_edits} edit(s) across {changed} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
