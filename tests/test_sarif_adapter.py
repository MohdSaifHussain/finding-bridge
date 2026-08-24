"""D4/D5 tests: SARIF emission, own-schema validation route, refusals.

The own-check route validates against the OFFICIAL OASIS schema vendored at
schemas/sarif-schema-2.1.0.json (draft-04 meta-schema; jsonschema's
validator_for auto-selects). The Multitool route lives at AUDIT cadence
(tests_audit/) per the D-032 principle. Both routes prove they can fail.
"""

import json
from pathlib import Path

import jsonschema
import pytest

from finding_bridge import pipeline
from finding_bridge.adapters.out import sarif

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
HITLOG = FIXTURES / "garak.synthetic.hitlog.jsonl"
SARIF_SCHEMA = json.loads((FIXTURES.parent / "sarif-schema-2.1.0.json").read_text(encoding="utf-8"))
IDENTITY = "Test Analyst <analyst@example.invalid>"


def validate_official(log: dict) -> None:
    cls = jsonschema.validators.validator_for(SARIF_SCHEMA)
    cls(SARIF_SCHEMA).validate(log)


@pytest.fixture()
def confirmed(tmp_path: Path) -> list[dict]:
    repo = tmp_path / "repo"
    repo.mkdir()
    ws = pipeline.Workspace(repo / ".fb-store", tmp_path / "k" / "fb.key", repo)
    ws.ingest_garak(HITLOG)
    for candidate in list(ws.list_candidates())[:2]:
        ws.confirm(candidate["id"], IDENTITY)
    return ws.confirmed_findings()


def test_sarif_passes_official_schema(confirmed):
    log = sarif.render_sarif(confirmed, "findings.fb.jsonl")
    validate_official(log)


def test_own_validator_can_fail(confirmed):
    """Negative control for the own-check route (skill rule 5)."""
    log = sarif.render_sarif(confirmed, "findings.fb.jsonl")
    del log["version"]
    with pytest.raises(jsonschema.exceptions.ValidationError):
        validate_official(log)


def test_locations_point_at_findings_artifact_lines(confirmed):
    log = sarif.render_sarif(confirmed, "findings.fb.jsonl")
    artifact = sarif.render_findings_artifact(confirmed)
    lines = artifact.splitlines()
    for i, result in enumerate(log["runs"][0]["results"]):
        loc = result["locations"][0]["physicalLocation"]
        assert loc["artifactLocation"]["uri"] == "findings.fb.jsonl"
        assert loc["region"]["startLine"] == i + 1
        assert json.loads(lines[i])["id"] == confirmed[i]["id"], (
            "the located line genuinely contains the finding (Q1a honesty)"
        )


def test_disambiguation_at_run_and_result_level(confirmed):
    """DEV-4: locations mean 'where the record is', stated in the SARIF."""
    log = sarif.render_sarif(confirmed, "f.jsonl")
    assert "finding RECORD" in log["runs"][0]["properties"]["locationSemantics"]
    for result in log["runs"][0]["results"]:
        assert "finding RECORD" in result["properties"]["locationSemantics"]


def test_tamper_bound_accompanies_provenance(confirmed):
    """OB-4 rule: the bound travels wherever the guarantee is stated."""
    log = sarif.render_sarif(confirmed, "f.jsonl")
    assert (
        "do not defend against an attacker" in (log["runs"][0]["properties"]["tamperEvidenceBound"])
    )


def test_no_sealed_content_in_sarif_or_artifact(confirmed):
    log_text = json.dumps(sarif.render_sarif(confirmed, "f.jsonl"))
    artifact = sarif.render_findings_artifact(confirmed)
    for text in (log_text, artifact):
        assert "SENTINEL-HARM" not in text
        assert "SENTINEL-PROBE" not in text
    assert "sealed/" in log_text, "sealed references are the only content pointers"


def test_nulls_stay_null_never_invented(confirmed):
    log = sarif.render_sarif(confirmed, "f.jsonl")
    props = log["runs"][0]["results"][0]["properties"]
    assert props["discoveredAt"] is None, "garak hitlogs carry no timestamp (D-024)"
    assert props["sourceToolVersion"] is None


def test_unconfirmed_refused(confirmed, tmp_path):
    unconfirmed = json.loads((FIXTURES / "candidate_null_fields.json").read_text(encoding="utf-8"))
    with pytest.raises(sarif.SarifAdapterError) as err:
        sarif.render_sarif([unconfirmed], "f.jsonl")
    assert err.value.reason_code == "unconfirmed"


def test_level_banding():
    assert sarif._level_and_rank(None) == ("none", None)
    assert sarif._level_and_rank(2)[0] == "note"
    assert sarif._level_and_rank(5)[0] == "warning"
    assert sarif._level_and_rank(8) == ("error", 80.0)
