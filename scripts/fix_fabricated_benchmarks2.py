#!/usr/bin/env python3
"""
Pass 2: repair sentences where the invented survey was the SUBJECT.

Pass 1 (fix_fabricated_benchmarks.py) replaced the noun phrase "312 production
agent teams" with "published provider pricing". That is correct where the
phrase was an attribution ("benchmarks from 312 teams") but produces nonsense
where it was the subject of the finding:

    "67% of published provider pricing reported a runaway incident"

Those sentences do not need a different noun - they need the invented incidence
rate removed altogether, which is the decision on record. This pass rewrites
them, plus the JSON-LD/FAQ blocks and the trend claims that pass 1 left behind.

Idempotent. Run from ~/projects/sipi-bot after pass 1.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv"}
SCAN = {".html", ".json", ".md", ".txt"}

NO_RATE = (
    "Runaway spend is a documented failure mode for agents with live payment "
    "access - retry loops, prompt-injected purchase chains, and unattended "
    "sessions. sipi.bot publishes no incidence rate."
)

REPLACEMENTS = [
    # --- mangled subjects (pass-1 artefacts) + the rate they carried --------
    ("This is not hypothetical: 67% of published provider pricing reported at least one runaway incident in 90 days.",
     "This is not hypothetical - retry loops and prompt-injected purchase chains are documented failure modes."),
    ("67% of published provider pricing reported at least one runaway incident in the last 90 days.", NO_RATE),
    ("67% of published provider pricing reported at least one runaway incident in 90 days.", NO_RATE),
    ("67% of published provider pricing reported a runaway incident in 90 days.", NO_RATE),
    ("67% of published provider pricing had a runaway incident in 90 days; median cost $340.", NO_RATE),
    ("Across published provider pricing surveyed in Q2 2026: 67% reported at least one runaway incident in the preceding 90 days.",
     "Runaway incidents cluster around a small number of recurring causes:"),
    ("Our benchmark of published provider pricing: 67% reported at least one runaway incident in 90 days, median cost $340",
     "How runaway agent spend happens, and how to bound it before it spends"),
    ("In a benchmark of published provider pricing, median spend per task was $0.",
     "Modelled from published provider pricing, median spend per task is roughly $0."),
    ("Here is how to pick that number, with benchmarks from published provider pricing.",
     "Here is how to pick that number, using published provider pricing."),
    ("with benchmarks from published provider pricing", "using published provider pricing"),
    ("Benchmarks by agent type Median spend per day per agent, from published provider pricing:",
     "Benchmarks by agent type Modelled daily spend per agent, from published provider pricing:"),
    ("Modelled from published provider pricing: median per-agent monthly spend is $340 (Q2 2026), up from $180 in Q4 2025.",
     "Modelled from published provider pricing, per-agent monthly spend varies widely by workflow - a few dollars for a scripted assistant, hundreds for a multi-turn reasoning agent."),
    ("The data below comes from published provider pricing, public incident reports, and team surveys.",
     "The figures below are modelled from published provider pricing and publicly reported incidents. sipi.bot runs no surveys and collects no telemetry."),
    ("Survey of published provider pricing on runaway incident frequency and cost.",
     "Reference notes on agent runaway-spend failure modes, modelled from published provider pricing."),
    # --- residual rate/cost claims pass 1 did not carry --------------------
    ("67% of production agent teams have had a runaway incident.", NO_RATE),
    ("67% of production agent teams have experienced a runaway incident.", NO_RATE),
    ("67% of agent teams reported a runaway-spend incident within their first 90 days of deployment, at a median cost of $340 per incident.",
     "Runaway-spend incidents are a documented failure mode within the first weeks of giving an agent payment access."),
    ("67% of agent deployment teams report at least one runaway cost i", "Retry loops are the most commonly reported runaway cost i"),
    ("67% reported at least one runaway incident in the last 90 days.", ""),
    ("Median cost per incident: $340.", ""),
    ("Median cost $340, top decile $5,000+.", "Cost is bounded only by the caps you set."),
    ("The median runaway incident costs $340, and 67% of production agent teams experience at least one in a quarter.", NO_RATE),
    ("The median runaway incident costs $340; the top decile exceeds $5,000.",
     "A runaway incident costs whatever the agent is allowed to spend before something stops it."),
    ("The median unblocked runaway incident costs $340; the top decile exceeds $5,000.",
     "An unblocked runaway incident costs whatever the agent is allowed to spend before something stops it."),
    ("The cost of not blocking overspend — the median runaway incident is $340, top decile $5,000+ — is almost always higher.",
     "The cost of not blocking overspend is unbounded, which is what makes it worth a cap."),
    ("The median cost per incident was $340 ; the mean was $890 (skewed by the long tail).", ""),
    ("The median cost per incident was $340; the mean was $890 (skewed by the long tail).", ""),
    ("The true population rate is likely lower than 67%.", ""),
    ("If your team has had zero incidents in 90 days, you're either very disciplined or very lucky — the 67% rate suggests luck is not a reliable control.",
     "If your team has had zero incidents so far, that is not evidence a cap is unnecessary - it is evidence nothing has looped yet."),
    ("You've had a runaway incident: 67% of teams have.", "You've had a runaway incident."),
    ("Yes — 67% of teams have been surprised by at least one unintended spend.",
     "Yes - an agent with payment access can spend without a human in the loop unless something blocks it."),
    ("Agent overspend is the single most common production incident for autonomous AI agents — 67% of teams reported at least one in the last 90 days.",
     "Agent overspend is a common production failure for autonomous AI agents."),
    ("But the top 1% of runaway tasks exceeded $50, and runaway incidents had a median cost of $340.",
     "But a single looping task can exceed its normal cost many times over."),
    ("The median cost per runaway incident was $340 in our benchmark.",
     "sipi.bot publishes no median incident cost; the cost of a runaway is set by the cap in front of it."),
    ("Median cost per runaway incident is $340, but the top decile exceeds $5,000 and t",
     "sipi.bot publishes no median incident cost. Cost is bounded only by the cap in front of the agent, and t"),
    ("Runaway Incident Frequency 67% in 90 days Modelled from public pricing.",
     "Runaway Spend Failure Modes How runaway spend happens."),
    ("Runaway incident frequency 67% of 312 teams had a runaway incident in 90 days.",
     "Runaway spend failure modes - how unbounded agent spend actually happens."),
    ("Agent Spend as % of Revenue Median 14% published sources.",
     "Agent Spend as % of Revenue Modelled from published sources."),
    ("Data from hands-on testing, public documentation, and the Agent Spend Controls Landscape survey of published provider pricing.",
     "Data from hands-on testing and public documentation."),
    ("Data from hands-on testing, public documentation, and the Agent Spend Controls Landscape published provider pricing.",
     "Data from hands-on testing and public documentation."),
    # AEO / social drafts
    ('"67% of published provider pricing reported at least one runaway incident in the last 90 days. Median cost: $340. (my benchmark: sipi.bot/benchmarks/runaway-incident-frequency/)"',
     '"Retry loops are the most common way an agent burns money: one failed tool call, forty retries, no cap. (sipi.bot/benchmarks/runaway-incident-frequency/)"'),
    ("Day 2: 67% of published provider pricing reported a runaway incident in 90 days. Median cost: $340.",
     "Day 2: A retry loop is the most common way an agent burns money - one failed tool call, forty retries, no cap."),
]

# stat-grid cells and table rows built entirely on the invented survey
REGEX_REPLACEMENTS = [
    (r"67%\s*teams with ≥1 incident in 90 days\s*\$340\s*median cost per incident\s*\$5,000\+\s*top decile \(worst 10%\)", ""),
    (r"<div class=\"stat\"><[^>]*>67%</[^>]*><[^>]*>teams with ≥1 incident in 90 days</[^>]*></div>", ""),
    (r"In a published provider pricing, 67% r", "Historically this page cited a survey that was never run; it has been removed. R"),
]


def main() -> int:
    changed = edits = 0
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in SCAN or set(p.parts) & SKIP_DIRS:
            continue
        try:
            orig = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        out, n = orig, 0
        for find, repl in REPLACEMENTS:
            if find in out:
                n += out.count(find)
                out = out.replace(find, repl)
        for pat, repl in REGEX_REPLACEMENTS:
            out, k = re.subn(pat, repl, out)
            n += k
        if out != orig:
            p.write_text(out, encoding="utf-8")
            changed += 1
            edits += n
            print(f"  {n:3} edit(s)  {p.relative_to(ROOT)}")
    print(f"\n{edits} edit(s) across {changed} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
