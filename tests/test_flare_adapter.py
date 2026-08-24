"""W3 tests: FLARE-AI provisional emission (D-014, OB-1)."""

import json
from pathlib import Path

import pytest

from finding_bridge import pipeline
from finding_bridge.adapters.out import flare_ai

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
HITLOG = FIXTURES / "garak.synthetic.hitlog.jsonl"
IDENTITY = "Test Analyst <analyst@example.invalid>"


@pytest.fixture()
def confirmed(tmp_path: Path) -> list[dict]:
    repo = tmp_path / "repo"
    repo.mkdir()
    ws = pipeline.Workspace(repo / ".fb-store", tmp_path / "k" / "fb.key", repo)
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], IDENTITY)
    return ws.confirmed_findings()


def test_provisional_stated_at_report_set_and_report_level(confirmed):
    """OB-1 condition: the output itself records that no canonical schema
    existed at this date (DEV-4 disambiguation pattern)."""
    out = flare_ai.render_reports(confirmed)
    assert out["provisional"]["status"] == "PROVISIONAL"
    assert "no canonical flare-ai schema was locatable" in out["provisional"]["notice"].lower()
    assert out["provisional"]["mappingCheckedOn"] == "2026-08-24"
    for report in out["reports"]:
        assert report["flare:provisionalMapping"] is True


def test_no_sealed_content_emitted(confirmed):
    text = json.dumps(flare_ai.render_reports(confirmed))
    assert "SENTINEL-HARM" not in text
    assert "SENTINEL-PROBE" not in text
    assert "sealed/" in text, "sealed references are the only content pointers"


def test_sentinel_search_can_detect(confirmed):
    """Positive control: the same search finds the sentinel in the fixture,
    so its absence above is a real absence."""
    assert "SENTINEL-HARM" in HITLOG.read_text(encoding="utf-8")


def test_null_target_fields_omitted_with_stated_reasons(confirmed):
    """Never invent a field. Omissions carry the field map's own reason."""
    out = flare_ai.render_reports(confirmed)
    omitted = out["provisional"]["omittedFields"]
    assert "dedup.cluster_id" in omitted
    assert "provenance.prev_hash" in omitted
    assert all(isinstance(reason, str) and reason for reason in omitted.values())
    report = out["reports"][0]
    assert not any(k.startswith("flare:dedup") for k in report)


def test_unconfirmed_refused():
    unconfirmed = json.loads((FIXTURES / "candidate_null_fields.json").read_text(encoding="utf-8"))
    with pytest.raises(flare_ai.FlareAdapterError) as err:
        flare_ai.render_reports([unconfirmed])
    assert err.value.reason_code == "unconfirmed"


def test_absent_source_values_are_absent_not_guessed(confirmed):
    """garak hitlogs carry no timestamp or tool version; the report must
    not invent either."""
    report = flare_ai.render_reports(confirmed)["reports"][0]
    assert "flare:detectionMethodVersion" not in report
    assert report["flare:evidence"]["flare:rawReport"] is None


def test_confirmed_identity_and_hash_travel(confirmed):
    report = flare_ai.render_reports(confirmed)["reports"][0]
    assert report["schema:author"]["schema:name"] == IDENTITY
    assert len(report["flare:evidence"]["contentHash"]) == 64
