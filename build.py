#!/usr/bin/env python3
"""build.py — single-command orchestrator for the sipi.bot content fleet.

Runs every content generator in order, rebuilds the sitemap, and (optionally)
pings IndexNow. Mirrors the proven voicelogpro-distribution/build.py pattern.

Usage:
    python3 build.py              # generate all + rebuild sitemap
    python3 build.py --ping       # ...and ping IndexNow (run after a deploy)
    python3 build.py --only incidents   # run one generator (dev/iterate)

Exit non-zero if any step fails, so CI / a deploy script can stop early.
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# Ordered steps. Each entry: (label, module path relative to repo root, importable).
# Existing pSEO generators live in scripts/ and are invoked as subprocesses
# (they predate lib/common.py and use their own inline chrome). New surfaces
# importable as modules go through lib/ and share the chrome.
STEPS = [
    # --- new shared-chrome surfaces (lib/) ---
    ("Incident database", "lib.generate_incidents", "module"),
    ("Interactive tools", "lib.generate_tools", "module"),
    ("Blog + changelog + status + RSS", "lib.generate_content", "module"),
]

# Existing generators run as scripts (they're written as standalone mains).
LEGACY_SCRIPTS = [
    # ("Legacy pSEO fleet", "scripts/build_pseo.py"),
    # Only re-enable if you want to regenerate the existing /for/ pages each run.
    # They're already committed and rarely change; leaving them off keeps the
    # build fast and avoids touching 200+ stable files on every run.
]

POST_STEPS = [
    ("Rebuild sitemap", "scripts/rebuild_sitemap.py", "script"),
]


def run_step(label, target, kind):
    t0 = time.time()
    print(f"\n=== {label} ===")
    if kind == "module":
        # import and call main() so relative imports resolve under one interpreter
        sys.path.insert(0, HERE)
        mod = __import__(target, fromlist=["main"])
        mod.main()
    else:  # script
        r = subprocess.run([sys.executable, os.path.join(HERE, target)],
                           cwd=HERE)
        if r.returncode != 0:
            raise SystemExit(f"Step '{label}' failed (exit {r.returncode})")
    print(f"  done in {time.time()-t0:.1f}s")


def validate_jsonld():
    """Run the same gate the Dockerfile enforces, before any deploy."""
    print("\n=== JSON-LD validation (Dockerfile gate) ===")
    r = subprocess.run([sys.executable, os.path.join(HERE, "scripts/validate_jsonld.py"),
                        os.path.join(HERE, "incidents"),
                        os.path.join(HERE, "public"),
                        os.path.join(HERE, "blog"),
                        os.path.join(HERE, "tools"),
                        os.path.join(HERE, "changelog"),
                        os.path.join(HERE, "status")],
                       cwd=HERE)
    if r.returncode != 0:
        raise SystemExit("JSON-LD validation FAILED — fix before deploy.")


def main():
    ap = argparse.ArgumentParser(description="Build the sipi.bot content fleet.")
    ap.add_argument("--ping", action="store_true",
                    help="Ping IndexNow after building (run post-deploy).")
    ap.add_argument("--only", metavar="MODULE",
                    help="Run a single generator module (e.g. lib.generate_incidents).")
    ap.add_argument("--no-validate", action="store_true",
                    help="Skip the JSON-LD gate (not recommended).")
    args = ap.parse_args()

    steps = STEPS
    if args.only:
        steps = [(args.only, args.only, "module")]
    if args.only and not args.no_validate:
        # single-module dev runs still validate their output
        pass

    for label, target, kind in steps:
        run_step(label, target, kind)
    for label, target, kind in LEGACY_SCRIPTS:
        run_step(label, target, "script")
    for label, target, kind in POST_STEPS:
        # sitemap rebuild only makes sense for a full build, not --only
        if not args.only:
            run_step(label, target, kind)

    if not args.no_validate:
        validate_jsonld()

    if args.ping:
        print("\n=== IndexNow ping ===")
        r = subprocess.run([sys.executable, os.path.join(HERE, "scripts/ping_indexnow.py")],
                           cwd=HERE)
        if r.returncode != 0:
            print("  IndexNow ping failed (non-fatal).")

    print("\n✓ build complete.")


if __name__ == "__main__":
    main()
