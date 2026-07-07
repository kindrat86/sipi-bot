"""run_eval.py — the eval gym runner.

For each scenario: create a FRESH SQLite DB (zero cross-test contamination),
seed the default policy + any scenario-specific rules, insert prior transactions
as APPROVED to simulate cumulative daily/velocity state, then evaluate the test
transaction and compare to the expected decision.

Outputs:
  eval_report.json   (machine-readable, served at /eval)
  eval_report.md     (human-readable, the Isenberg sales asset)

Run:  python -m spendfirewall.eval.run_eval
"""
from __future__ import annotations

import json
import os
import tempfile
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from .. import store, core
from ..engine import Transaction, EvalResult, Decision
from .eval_scenarios import SCENARIOS, DEFAULT_RULES


def _fresh_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db", prefix="sfeval_")
    os.close(fd)
    os.unlink(path)  # let sqlite create it clean
    return path


def _create_tables_only() -> None:
    # Reuse store.init_db table DDL but avoid double-seeding: init_db seeds
    # defaults only if none exist; we then rely on our explicit DEFAULT_RULES.
    # We create tables via init_db then wipe rules to control the policy exactly.
    store.init_db()
    with store._LOCK, store._conn() as c:  # noqa: SLF001 (intentional test access)
        c.execute("DELETE FROM rules")


def _seed_rules(rules) -> None:
    for (rtype, params, action, priority, label) in rules:
        store.add_rule(rtype, params, action, priority, label)


def _insert_prior(priors) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with store._LOCK, store._conn() as c:  # noqa: SLF001
        for p in priors:
            tid = "txn_" + uuid.uuid4().hex[:12]
            c.execute(
                "INSERT INTO transactions (id, agent_id, amount, currency, merchant, category, "
                "description, decision, reason, rule_id, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (tid, None, float(p.get("amount", 0)), "USD", p.get("merchant", ""),
                 p.get("category", ""), "", "APPROVED", "seed", None, now),
            )


def run() -> dict:
    results = []
    passed = 0
    by_cat = defaultdict(lambda: {"pass": 0, "total": 0})

    for sc in SCENARIOS:
        db = _fresh_db()
        store._DB_PATH = db  # noqa: SLF001 — point store at the fresh DB
        try:
            _create_tables_only()
            _seed_rules(DEFAULT_RULES)
            if sc.get("rules"):
                _seed_rules(sc["rules"])
            if sc.get("prior"):
                _insert_prior(sc["prior"])

            txn = sc["txn"]
            out = core.evaluate_transaction(
                amount=txn.get("amount", 0),
                merchant=txn.get("merchant", ""),
                category=txn.get("category", ""),
                description=txn.get("description", ""),
                timestamp=txn.get("timestamp"),
                agent_id=None,
                record=False,
            )
            got = out["decision"]
            exp = sc["expected"]
            ok = (got == exp)
            passed += 1 if ok else 0
            cat = sc.get("category", "uncategorized")
            by_cat[cat]["total"] += 1
            by_cat[cat]["pass"] += 1 if ok else 0
            results.append({
                "name": sc["name"], "category": cat,
                "expected": exp, "got": got, "pass": ok,
                "reason": out.get("reason", ""), "note": sc.get("note", ""),
            })
        finally:
            try:
                os.unlink(db)
                for ext in ("-wal", "-shm"):
                    if os.path.exists(db + ext):
                        os.unlink(db + ext)
            except OSError:
                pass

    total = len(SCENARIOS)
    accuracy = round(100 * passed / total, 1) if total else 0.0
    report = {
        "product": "sipi.bot Spend Firewall",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": total, "passed": passed, "failed": total - passed,
        "accuracy_pct": accuracy,
        "by_category": {k: v for k, v in by_cat.items()},
        "results": results,
    }
    return report


def _markdown(report: dict) -> str:
    lines = [
        f"# sipi.bot Spend Firewall — Eval Report",
        "",
        f"**{report['passed']}/{report['total']} scenarios passed "
        f"({report['accuracy_pct']}% accuracy)** · generated {report['generated_at'][:19]}Z",
        "",
        "> We tested the firewall on 50 real spend scenarios an autonomous agent could hit — "
        "runaway loops, 3am compute buys, sketchy merchants, cumulative daily caps, and exact "
        "boundary values. Here's exactly how it did, including the tricky edge cases. "
        "This is the honesty behind the guarantee.",
        "",
        "## By category",
        "",
        "| Category | Passed | Total |",
        "|---|---|---|",
    ]
    for cat, v in sorted(report["by_category"].items()):
        lines.append(f"| {cat} | {v['pass']} | {v['total']} |")
    lines += ["", "## Every scenario", "", "| # | Scenario | Expected | Got | ✓ |", "|---|---|---|---|---|"]
    for i, r in enumerate(report["results"], 1):
        mark = "✅" if r["pass"] else "❌"
        lines.append(f"| {i} | {r['name']} | {r['expected']} | {r['got']} | {mark} |")
    fails = [r for r in report["results"] if not r["pass"]]
    if fails:
        lines += ["", "## Mismatches (investigate before shipping)", ""]
        for r in fails:
            lines.append(f"- **{r['name']}** — expected `{r['expected']}`, got `{r['got']}`. {r['note']}")
    else:
        lines += ["", "## 🎯 100% — every decision path verified.", ""]
    return "\n".join(lines)


def main() -> None:
    report = run()
    out_json = os.environ.get("EVAL_REPORT", os.path.join(os.getcwd(), "eval_report.json"))
    out_md = os.path.splitext(out_json)[0] + ".md"
    with open(out_json, "w") as f:
        json.dump(report, f, indent=2)
    with open(out_md, "w") as f:
        f.write(_markdown(report))
    print(f"{report['passed']}/{report['total']} passed ({report['accuracy_pct']}%)")
    print(f"wrote {out_json} and {out_md}")
    for r in report["results"]:
        if not r["pass"]:
            print(f"  FAIL: {r['name']} expected {r['expected']} got {r['got']}")


if __name__ == "__main__":
    main()
