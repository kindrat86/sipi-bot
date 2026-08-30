#!/usr/bin/env python3
"""Build incident replay proof pages under public/proof/<pa_id>/index.html.

Reads replay artifacts from the private campaign workspace and emits one static,
truthful, noindexed page per target. No contact emails or private targeting
state ever enter the page or the repository.
"""

from __future__ import annotations

import html
import json
import secrets
from pathlib import Path

PROOF_BASE_URL = "https://sipi.bot/proof"
GENERATED_NOTE = "from public data"
LIMITATION = ("This is a replay of a publicly reported amount, not a claim "
              "about avoided losses.")
FOOTER = "sipi.bot is a decision API. It does not hold or move money."


def generate_page_id() -> str:
    """Return a cryptographically random, non-reversible page id."""
    return "pa_" + secrets.token_hex(8)


def load_replay(artifact_dir: str | Path) -> dict:
    """Load request/response/metadata from one replay artifact directory."""
    d = Path(artifact_dir)
    return {
        "request": json.loads((d / "request.json").read_text(encoding="utf-8")),
        "response": json.loads((d / "response.json").read_text(encoding="utf-8")),
        "metadata": json.loads((d / "artifact-metadata.json").read_text(encoding="utf-8")),
        "snapshot": json.loads((d / "source-snapshot.json").read_text(encoding="utf-8")),
    }


def _esc(value) -> str:
    return html.escape(str(value), quote=True)


def generate_page_html(record: dict) -> tuple[str, str]:
    """Return (html_text, page_id) for one incident replay record.

    record keys: artifact_dir, metadata, incident{name_or_handle, incident_url,
    incident_date, incident_amount_native, reported_merchant, incident_summary}
    """
    replay = load_replay(record["artifact_dir"])
    meta = record["metadata"]
    inc = record["incident"]
    request = replay["request"]
    resp = replay["response"]["response"]
    pid = generate_page_id()
    canonical = f"{PROOF_BASE_URL}/{pid}/"
    checked = replay["snapshot"].get("fetched_at", meta["generated_at_utc"])

    request_json = json.dumps(request, indent=2, ensure_ascii=True)
    response_json = json.dumps(resp, indent=2, ensure_ascii=True)

    who = _esc(inc["name_or_handle"])
    parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Replay proof: {who} incident</title>
<meta name="robots" content="noindex,nofollow">
<link rel="canonical" href="{canonical}">
<style>
body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 760px;
       margin: 2rem auto; padding: 0 1rem; line-height: 1.55; color: #1a1a1a; }}
h1 {{ font-size: 1.35rem; }} h2 {{ font-size: 1.05rem; margin-top: 1.6rem; }}
code, pre {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
       font-size: 0.85rem; }} pre {{ background: #f5f5f5; padding: 0.8rem;
       border-radius: 6px; overflow-x: auto; }}
.meta {{ color: #555; }} .limit {{ background: #fff8e6; padding: 0.7rem 1rem;
       border-left: 3px solid #d9a400; border-radius: 4px; }}
footer {{ margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #ddd;
       font-size: 0.85rem; color: #555; }}
</style>
</head>
<body>
<h1>Replay proof: {who} &middot; {_esc(inc['incident_amount_native'])}</h1>
<p class="meta">Target: {who}{f" &middot; {_esc(inc['company_or_project'])}" if inc.get("company_or_project") else ""}</p>
<p class="meta">Original incident: <a href="{_esc(inc['incident_url'])}" rel="nofollow">{_esc(inc['incident_url'])}</a></p>
<p class="meta">Incident date: {_esc(inc['incident_date'])}</p>
<p class="meta">Reported amount: {_esc(inc['incident_amount_native'])} &middot; merchant/service: {_esc(inc['reported_merchant'])}</p>
<p>{_esc(inc['incident_summary'])}</p>
"""]

    parts.append(f"""<h2>Replayed through the live sipi.bot endpoint</h2>
<p>Request sent to <code>{_esc(meta['endpoint'])}</code> on {_esc(meta['generated_at_utc'])}:</p>
<pre>{_esc(request_json)}</pre>
<p>Exact response:</p>
<pre>{_esc(response_json)}</pre>
<p>For this replayed transaction proposal, the live sipi.bot endpoint returned {_esc(resp['decision'])} with the rule shown above.</p>
""")

    parts.append(f"""<h2>Limitations</h2>
<p class="limit">{LIMITATION} The decision shown is a timestamped observation of
the public demo decision API for this single replayed proposal, not a statement
about the historical incident or any party's account.</p>
<p>Source checked live at {_esc(checked)}.</p>
<footer>
<p>Generated {_esc(meta['generated_at_utc'])} {GENERATED_NOTE}.</p>
<p>{FOOTER} <a href="https://sipi.bot">sipi.bot</a> &middot;
<a href="https://github.com/kindrat86/sipi-bot">GitHub</a></p>
</footer>
</body>
</html>
""")
    return "".join(parts), pid


def write_page(record: dict, public_root: str | Path) -> tuple[str, str]:
    """Write one proof page; return (public_url, page_id)."""
    html_text, pid = generate_page_html(record)
    out = Path(public_root) / "proof" / pid / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")
    return f"{PROOF_BASE_URL}/{pid}/", pid


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Build incident proof pages")
    ap.add_argument("--artifacts", required=True,
                    help="campaign artifacts directory")
    ap.add_argument("--targets", required=True,
                    help="campaign targets directory")
    ap.add_argument("--public", default="public",
                    help="repository public/ root (default: ./public)")
    ap.add_argument("--manifest", default=None,
                    help="write a private manifest JSON of generated ids")
    args = ap.parse_args()

    adir = Path(args.artifacts)
    tdir = Path(args.targets)
    manifest = []
    for tfile in sorted(tdir.glob("IT-*.json")):
        target = json.loads(tfile.read_text(encoding="utf-8"))
        tid = target["target_id"]
        meta_file = adir / tid / "artifact-metadata.json"
        if not meta_file.exists():
            continue
        if target.get("route") not in ("public_comment",):
            continue
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        if not meta.get("causal_per_transaction_rule"):
            continue
        record = {"artifact_dir": str(adir / tid), "metadata": meta, "incident": target}
        url, pid = write_page(record, args.public)
        manifest.append({"target_id": tid, "page_id": pid, "url": url})
        print(f"{tid}: {url}")

    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        print(f"manifest: {args.manifest} ({len(manifest)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
