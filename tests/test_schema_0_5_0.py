"""Schema 0.5.0 (D-071, D-076): taxonomy.atlas, id patterns, remediation.

Every pattern proves it can fail (negative control) and can pass
(positive control), and the "constrain the shape, never require a
claim" ruling has its own control: empty and absent are legal everywhere.
The OWASP pattern is the 2026 grammar (F-5): a 2025-tagged id is refused
on purpose, because re-tagging is a human act, not a renumbering.
"""

import copy
import json
from pathlib import Path

import pytest

from finding_bridge.core.schema import SchemaValidationError, validate_record

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


def _full() -> dict:
    return json.loads((FIXTURES / "candidate_full.json").read_text(encoding="utf-8"))


def _refused(record: dict, where: str) -> None:
    with pytest.raises(SchemaValidationError) as exc:
        validate_record(record)
    assert where in exc.value.detail, exc.value.detail
    assert "SENTINEL" not in exc.value.detail  # location, never value (D-036)


@pytest.mark.parametrize(
    "array, good, bad",
    [
        ("owasp_llm", "LLM03:2026", "LLM06:2025"),
        ("owasp_llm", "LLM10:2026", "LLM11:2026"),
        ("saif", "PIJ", "prompt-injection"),
        ("saif", "RA", "SENTINEL-NOT-A-RISK"),
        ("atlas", "AML.T0051", "T0051"),
        ("atlas", "AML.T0051.002", "AML.T51"),
    ],
)
def test_taxonomy_id_patterns_accept_the_pin_and_refuse_the_rest(array, good, bad):
    rec = _full()
    rec["taxonomy"][array] = [{"id": good, "status": "confirmed"}]
    validate_record(rec)
    rec["taxonomy"][array] = [{"id": bad, "status": "confirmed"}]
    _refused(rec, f"$.taxonomy.{array}[0].id")


def test_empty_and_absent_taxonomy_claims_are_legal():
    """D-071: constrain the shape of what IS claimed, never require a claim."""
    rec = _full()
    rec["taxonomy"] = {"owasp_llm": [], "saif": [], "atlas": []}
    validate_record(rec)
    del rec["taxonomy"]["atlas"]
    validate_record(rec)


def test_remediation_null_string_and_absent_are_legal_nothing_else():
    rec = _full()
    for value in (None, "SENTINEL-REMEDIATION synthetic advice"):
        rec["remediation"] = value
        validate_record(rec)
    del rec["remediation"]
    validate_record(rec)
    rec["remediation"] = ["not", "a", "string"]
    _refused(rec, "$.remediation")


def test_adapters_emit_null_remediation_and_empty_atlas_never_a_claim():
    from finding_bridge.adapters.in_ import garak

    cands = list(garak.parse_hitlog(FIXTURES / "garak.synthetic.hitlog.jsonl"))
    assert cands
    for c in cands:
        assert c["remediation"] is None
        assert c["taxonomy"]["atlas"] == []
        assert c["schema_version"] == "0.5.0"


def test_schema_version_and_ids_moved_together():
    schema = json.loads(
        (
            Path(__file__).resolve().parent.parent
            / "src/finding_bridge/schemas/finding.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert schema["$id"].endswith("/0.5.0")
    assert schema["properties"]["schema_version"]["const"] == "0.5.0"
    assert "remediation" not in schema["required"]
    assert "atlas" not in schema["properties"]["taxonomy"]["required"]
    assert copy.deepcopy(
        schema["$defs"]["owasp_llm_entry"]["properties"]["id"]["pattern"]
    ).endswith(":2026$")
