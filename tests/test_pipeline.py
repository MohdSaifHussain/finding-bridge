"""D6-D8 round trip: ingest -> seal -> stamp -> dedup -> gate -> emit.

Runs the whole spine on the synthetic fixture with a tmp workspace and a key
outside the (simulated) repo root."""

import json
from pathlib import Path

import pytest

from finding_bridge import pipeline
from finding_bridge.adapters.out import markdown
from finding_bridge.core import provenance as prov

FIXTURE = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
HITLOG = FIXTURE / "garak.synthetic.hitlog.jsonl"
IDENTITY = "Test Analyst <analyst@example.invalid>"


@pytest.fixture()
def ws(tmp_path: Path) -> pipeline.Workspace:
    repo = tmp_path / "repo"
    repo.mkdir()
    return pipeline.Workspace(repo / ".fb-store", tmp_path / "keys" / "fb.key", repo)


def test_ingest_seals_stamps_and_validates(ws: pipeline.Workspace):
    summary = ws.ingest_garak(HITLOG)
    # duplicates_marked is 1 since D-025: the fixture's deliberate identical
    # pair differs only in attempt bookkeeping, which the dedup key excludes.
    assert summary == {"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
    candidates = ws.list_candidates()
    for c in candidates:
        assert c["id"].startswith("fb-")
        assert c["probe"]["value"] is None
        assert c["probe"]["sealed_ref"].startswith("sealed/")
        assert c["raw_response_sealed"].startswith("sealed/")
        assert "SENTINEL-HARM" not in json.dumps(c), "raw harm must never reach a candidate"
        assert "keyed digest" in c["preview"]


def test_reingest_marks_duplicates(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    summary = ws.ingest_garak(HITLOG)
    assert summary["total_candidates"] == 6
    # Two canonical findings across both ingests (the identical pair merges
    # within AND across ingests since D-025): 6 records, 2 canonical, 4 dupes.
    assert summary["duplicates_marked"] == 4


def test_confirm_builds_chained_ledger_and_head(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    ids = [c["id"] for c in ws.list_candidates()]
    first = ws.confirm(ids[0], IDENTITY)
    second = ws.confirm(ids[1], IDENTITY)
    assert first["provenance"]["confirmed_by"] == IDENTITY
    assert first["provenance"]["attestation_hash"] is not None
    assert second["provenance"]["prev_hash"] == first["provenance"]["content_hash"]
    assert ws.verify() == []
    assert len(ws.list_candidates()) == 1


def test_confirm_unknown_id_refused(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    with pytest.raises(pipeline.PipelineError) as err:
        ws.confirm("fb-0000000000000000", IDENTITY)
    assert err.value.reason_code == "unknown-id"


def test_tampered_ledger_fails_verify(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], IDENTITY)
    ledger = json.loads(ws.ledger_path.read_text(encoding="utf-8").splitlines()[0])
    ledger["provenance"]["confirmed_by"] = "Forged <f@example.invalid>"
    ws.ledger_path.write_text(json.dumps(ledger, sort_keys=True) + "\n", encoding="utf-8")
    codes = {f["reason_code"] for f in ws.verify()}
    assert prov.REASON_ATTESTATION_TAMPERED in codes


def test_truncated_ledger_fails_verify(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    ids = [c["id"] for c in ws.list_candidates()]
    ws.confirm(ids[0], IDENTITY)
    ws.confirm(ids[1], IDENTITY)
    lines = ws.ledger_path.read_text(encoding="utf-8").splitlines()
    ws.ledger_path.write_text(lines[0] + "\n", encoding="utf-8")
    codes = {f["reason_code"] for f in ws.verify()}
    assert prov.REASON_HEAD_MISMATCH in codes


def test_missing_head_fails_verify(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], IDENTITY)
    ws.head_path.unlink()
    codes = {f["reason_code"] for f in ws.verify()}
    assert "head-missing" in codes


def test_reject_moves_candidate(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    target = ws.list_candidates()[0]["id"]
    ws.reject(target)
    assert target not in [c["id"] for c in ws.list_candidates()]


# --- D8: markdown packet ---


def test_packet_carries_preview_metadata_and_bound_never_harm(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], IDENTITY)
    packet = markdown.render_packet(ws.confirmed_findings())
    assert "SENTINEL-HARM" not in packet, "raw sealed content must never be emitted (R1)"
    assert "SENTINEL-PROBE" not in packet
    assert "keyed digest" in packet
    assert "Confirmed by: Test Analyst" in packet
    assert markdown.TAMPER_BOUND in packet, "OB-4 bound sentence must accompany the guarantee"
    assert "sealed/" in packet, "sealed references (keyed) are the only content pointers"


def test_packet_refuses_unconfirmed(ws: pipeline.Workspace):
    ws.ingest_garak(HITLOG)
    with pytest.raises(markdown.MarkdownAdapterError) as err:
        markdown.render_packet(ws.list_candidates())
    assert err.value.reason_code == "unconfirmed"


def test_explicit_unseal_recovers_sentinel_and_logs(ws: pipeline.Workspace):
    """Positive control for the whole seal path: the sentinel IS recoverable,
    explicitly, with exposure rows."""
    ws.ingest_garak(HITLOG)
    ref = ws.list_candidates()[0]["raw_response_sealed"]
    out = ws.store.unseal(ref, IDENTITY, explicit=True)
    assert "SENTINEL-HARM" in out
    rows = ws.store.exposures()
    assert [r["type"] for r in rows] == ["attempt", "outcome"]
    assert rows[1]["outcome"] == "succeeded"


# --- Finding A (director's ritual, ruled): single-ingest dedup on identical evidence ---


def test_single_ingest_marks_byte_identical_pair(ws: pipeline.Workspace):
    """Director's acceptance criterion: the fixture's deliberate duplicate
    pair (identical goal/prompt/output/probe/detector/score, differing only
    in attempt bookkeeping) is marked in ONE ingest: duplicates_marked 1,
    shared cluster_id, second carries duplicate_of pointing at the first."""
    summary = ws.ingest_garak(HITLOG)
    assert summary["duplicates_marked"] == 1
    candidates = ws.list_candidates()
    pair = [
        c for c in candidates if c["raw_response_sealed"] == candidates[0]["raw_response_sealed"]
    ]
    assert len(pair) == 2
    assert pair[0]["dedup"]["duplicate_of"] is None
    assert pair[1]["dedup"]["duplicate_of"] == pair[0]["id"]
    assert pair[0]["dedup"]["cluster_id"] == pair[1]["dedup"]["cluster_id"] is not None


def test_genuinely_different_record_stays_unique(ws: pipeline.Workspace):
    """Negative control: marking can fail to appear; record 3's evidence
    genuinely differs and must stay unique."""
    ws.ingest_garak(HITLOG)
    others = [c for c in ws.list_candidates() if "promptinject" in (c["harm_flags"] or [""])[0]]
    assert len(others) == 1
    assert others[0]["dedup"]["duplicate_of"] is None
    assert others[0]["dedup"]["cluster_id"] is None
