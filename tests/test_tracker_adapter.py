"""W3 tests: tracker JSON emission (STANDARD tier, same emitter law)."""

import json
from pathlib import Path

import pytest

from finding_bridge import pipeline
from finding_bridge.adapters.out import tracker

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
HITLOG = FIXTURES / "garak.synthetic.hitlog.jsonl"
IDENTITY = "Tracker Analyst <t@example.invalid>"


@pytest.fixture()
def confirmed(tmp_path: Path) -> list[dict]:
    repo = tmp_path / "repo"
    repo.mkdir()
    ws = pipeline.Workspace(repo / ".fb-store", tmp_path / "k" / "fb.key", repo)
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], IDENTITY)
    return ws.confirmed_findings()


def test_no_sealed_content_in_tracker_output(confirmed):
    text = json.dumps(tracker.render_issues(confirmed))
    assert "SENTINEL-HARM" not in text
    assert "SENTINEL-PROBE" not in text
    assert "sealed/" in text, "sealed references are the only content pointers"


def test_sentinel_search_can_detect():
    """Positive control: the same search finds the sentinel in the source."""
    assert "SENTINEL-HARM" in HITLOG.read_text(encoding="utf-8")


def test_shape_is_a_flat_array_of_issues(confirmed):
    issues = tracker.render_issues(confirmed)
    assert isinstance(issues, list) and issues
    issue = issues[0]
    assert set(issue) == {"summary", "description", "labels", "priority", "fields"}
    assert isinstance(issue["labels"], list)


def test_description_carries_preview_provenance_and_the_bound(confirmed):
    issue = tracker.render_issues(confirmed)[0]
    description = issue["description"]
    assert "keyed digest" in description, "the preview travels"
    assert confirmed[0]["provenance"]["content_hash"] in description
    assert confirmed[0]["provenance"]["attestation_hash"] in description
    assert IDENTITY in description
    assert "do not defend against an attacker" in description, "OB-4 bound must travel"
    assert "Content is sealed" in description


def test_unscored_severity_is_unset_never_guessed(confirmed):
    issue = tracker.render_issues(confirmed)[0]
    assert confirmed[0]["severity"]["score"] is None
    assert issue["priority"] == "Unset", "an unscored finding must not gain a priority"


def test_priority_bands():
    assert tracker._priority(None) == "Unset"
    assert tracker._priority(2) == "Low"
    assert tracker._priority(5) == "Medium"
    assert tracker._priority(9) == "High"


def test_suggested_taxonomy_is_marked_in_labels():
    finding = json.loads((FIXTURES / "candidate_full.json").read_text(encoding="utf-8"))
    labels = tracker._labels(finding)
    assert "owasp_llm:LLM01:2026?" in labels, "a suggested mapping must not look confirmed"
    assert any(label.startswith("harm:") for label in labels)
    assert "source:garak" in labels


def test_unconfirmed_refused():
    finding = json.loads((FIXTURES / "candidate_null_fields.json").read_text(encoding="utf-8"))
    with pytest.raises(tracker.TrackerAdapterError) as err:
        tracker.render_issues([finding])
    assert err.value.reason_code == "unconfirmed"


def test_supersession_records_are_not_turned_into_tickets(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    ws = pipeline.Workspace(repo / ".fb-store", tmp_path / "k" / "fb.key", repo)
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], IDENTITY)
    ws.rotate_key(IDENTITY, reason="w3 test rotation")
    issues = tracker.render_issues(ws.confirmed_findings())
    assert len(issues) == 1, "ledger bookkeeping is not an actionable ticket"
