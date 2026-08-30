"""Tests for incident proof pages (RED phase first).

A proof page is a static HTML file at public/proof/<pa_id>/index.html generated
from a replay artifact. It must be truthful, noindexed, email-free, and free of
unsupported claims.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from build_incident_proof_pages import generate_page_html, load_replay  # noqa: E402


def _make_fixture(tmp_path: Path) -> dict:
    """Create a minimal replay artifact directory and return the loadable record."""
    adir = tmp_path / "artifacts" / "IT-001"
    adir.mkdir(parents=True)
    (adir / "request.json").write_text(json.dumps({
        "transaction_id": "replay-it-001-1",
        "amount": 37901.73,
        "currency": "USD",
        "merchant": "aws-bedrock",
        "description": "Replay of publicly reported incident amount",
    }))
    (adir / "response.json").write_text(json.dumps({
        "http_status": 200,
        "response": {
            "decision": "BLOCKED",
            "reason": "Block any single transaction over $500",
            "rule_id": "rul_eff79f00f6",
        },
        "captured_at_utc": "2026-08-30T15:40:00+00:00",
    }))
    meta = {
        "target_id": "IT-001",
        "generated_at_utc": "2026-08-30T15:40:00+00:00",
        "endpoint": "https://sipi.bot/v1/transactions/evaluate",
        "http_status": 200,
        "decision": "BLOCKED",
        "reason": "Block any single transaction over $500",
        "rule_id": "rul_eff79f00f6",
        "schema_complete": True,
        "causal_per_transaction_rule": True,
        "amount_field": "currency units (verified by live 501 boundary probe this session)",
    }
    (adir / "artifact-metadata.json").write_text(json.dumps(meta))
    (adir / "source-snapshot.json").write_text(json.dumps({
        "fetched_at": "2026-08-30T15:40:00+00:00",
        "method": "hn_algolia_direct",
        "url": "https://news.ycombinator.com/item?id=47933355",
        "verbatim": {"author": "Zephyr0x", "created_at": "2026-04-28T12:07:40.000Z",
                      "title": "$38k AWS Bedrock bill caused by a simple prompt caching miss",
                      "text_excerpt": "I just learned a $37,901.73 lesson"},
    }))
    return {"artifact_dir": str(adir), "metadata": meta,
            "incident": {"name_or_handle": "Zephyr0x",
                          "incident_url": "https://news.ycombinator.com/item?id=47933355",
                          "incident_date": "2026-04-28",
                          "incident_amount_native": "$37,901.73",
                          "reported_merchant": "aws-bedrock",
                          "incident_summary": "Coding-agent workflow sent uncached input."}}


def test_page_id_format():
    """Generator must emit pa_<16 lowercase hex> ids."""
    from build_incident_proof_pages import generate_page_id
    pid = generate_page_id()
    assert re.fullmatch(r"pa_[0-9a-f]{16}", pid), pid


def test_generated_page_contains_required_elements(tmp_path):
    rec = _make_fixture(tmp_path)
    html_text, pid = generate_page_html(rec)
    # required content
    assert "Zephyr0x" in html_text
    assert "https://news.ycombinator.com/item?id=47933355" in html_text
    assert "2026-04-28" in html_text
    assert "$37,901.73" in html_text
    assert "aws-bedrock" in html_text
    assert "BLOCKED" in html_text
    assert "Block any single transaction over $500" in html_text
    assert "rul_eff79f00f6" in html_text
    # neutral explanation
    assert "the live sipi.bot endpoint returned BLOCKED" in html_text
    assert "Generated " in html_text and "from public data" in html_text
    assert "replay of a publicly reported amount" in html_text
    assert "decision API" in html_text and "does not hold or move money" in html_text
    assert "https://sipi.bot" in html_text
    assert "https://github.com/kindrat86/sipi-bot" in html_text


def test_generated_page_noindex_and_canonical(tmp_path):
    rec = _make_fixture(tmp_path)
    html_text, pid = generate_page_html(rec)
    assert '<meta name="robots" content="noindex,nofollow">' in html_text
    assert re.search(r'<link rel="canonical" href="https://sipi\.bot/proof/%s/?"' % pid, html_text)


def test_generated_page_no_email_no_pii(tmp_path):
    rec = _make_fixture(tmp_path)
    html_text, pid = generate_page_html(rec)
    assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html_text)
    assert "suppression" not in html_text.lower()
    assert "outreach" not in html_text.lower()


def test_generated_page_no_forbidden_claims(tmp_path):
    rec = _make_fixture(tmp_path)
    html_text, pid = generate_page_html(rec)
    low = html_text.lower()
    for bad in ["would have saved", "guaranteed to stop", "prevented this incident",
                "before money moved"]:
        assert bad not in low, bad
    # no custody/money-movement implication beyond the disclaimer footer
    assert "custody" not in low
    assert "wallet" not in low


def test_generated_page_valid_utf8_no_mojibake(tmp_path):
    rec = _make_fixture(tmp_path)
    html_text, pid = generate_page_html(rec)
    html_text.encode("utf-8").decode("utf-8")  # round trip
    for marker in ["\u201a\u00c4", "\u00c3", "\u00c2", "\u00e2\u20ac", "\ufffd"]:
        assert marker not in html_text, repr(marker)


def test_load_replay_reads_artifact(tmp_path):
    rec = _make_fixture(tmp_path)
    loaded = load_replay(rec["artifact_dir"])
    assert loaded["metadata"]["target_id"] == "IT-001"
    assert loaded["response"]["response"]["decision"] == "BLOCKED"


def test_write_page_creates_index(tmp_path):
    from build_incident_proof_pages import write_page
    rec = _make_fixture(tmp_path)
    public_root = tmp_path / "public"
    url, pid = write_page(rec, public_root)
    page = public_root / "proof" / pid / "index.html"
    assert page.exists()
    text = page.read_text(encoding="utf-8")
    assert "Zephyr0x" in text
    assert url == f"https://sipi.bot/proof/{pid}/"
