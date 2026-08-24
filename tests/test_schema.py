"""D1/D2 tests: canonical schema validity, fixtures, and the D-003 drift test.

Leaf rule for the mapping table (documented here because the drift test is the
enforcement): walk the schema's `properties`; a property that is an object with
its own declared `properties` recurses; everything else (scalars, nullable
scalars, arrays, objects without declared properties) is a leaf. `$ref`s into
`$defs` are resolved before the object test. The mapping table's keys must
equal the leaf set exactly, in both directions.
"""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

REPO = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO / "schemas" / "finding.schema.json"
FIELD_MAP_PATH = REPO / "schemas" / "field_map.json"
FIXTURES = REPO / "schemas" / "fixtures"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_ref(schema: dict, node: dict) -> dict:
    ref = node.get("$ref")
    if ref is None:
        return node
    assert ref.startswith("#/"), f"only local refs supported, got {ref}"
    target = schema
    for part in ref[2:].split("/"):
        target = target[part]
    return target


def leaf_paths(schema: dict, node: dict | None = None, prefix: str = "") -> set[str]:
    node = resolve_ref(schema, schema if node is None else node)
    leaves: set[str] = set()
    for name, sub in node.get("properties", {}).items():
        sub = resolve_ref(schema, sub)
        path = f"{prefix}{name}"
        if sub.get("type") == "object" and "properties" in sub:
            leaves |= leaf_paths(schema, sub, prefix=f"{path}.")
        else:
            leaves.add(path)
    return leaves


@pytest.fixture(scope="module")
def schema() -> dict:
    return load(SCHEMA_PATH)


@pytest.fixture(scope="module")
def field_map() -> dict:
    return load(FIELD_MAP_PATH)


# --- schema is itself valid 2020-12 ---


def test_schema_is_valid_draft_2020_12(schema):
    Draft202012Validator.check_schema(schema)


def test_schema_declares_2020_12_dialect(schema):
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"


# --- fixtures validate (positive controls) ---


def test_full_fixture_validates(schema):
    Draft202012Validator(schema).validate(load(FIXTURES / "candidate_full.json"))


def test_null_fields_fixture_validates(schema):
    """Missing source knowledge is null, never invented (contract 3.8)."""
    Draft202012Validator(schema).validate(load(FIXTURES / "candidate_null_fields.json"))


# --- validation can refuse (negative controls, skill rule 5) ---


def test_extra_property_refused(schema):
    finding = load(FIXTURES / "candidate_full.json")
    finding["invented_field"] = "x"
    with pytest.raises(ValidationError, match="invented_field"):
        Draft202012Validator(schema).validate(finding)


def test_missing_required_field_refused(schema):
    finding = load(FIXTURES / "candidate_full.json")
    del finding["provenance"]
    with pytest.raises(ValidationError, match="provenance"):
        Draft202012Validator(schema).validate(finding)


def test_inline_raw_harm_shape_refused(schema):
    """raw_response_sealed is a reference string or null; an inline object
    carrying content must refuse (charter: never inline raw harm)."""
    finding = load(FIXTURES / "candidate_full.json")
    finding["raw_response_sealed"] = {"content": "SENTINEL-HARM-0001"}
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(finding)


def test_bad_taxonomy_status_refused(schema):
    finding = load(FIXTURES / "candidate_full.json")
    finding["taxonomy"]["owasp_llm"][0]["status"] = "ai-decided"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(finding)


# --- D-003 drift test: schema and mapping table move together, loudly ---


def drift(schema: dict, field_map: dict) -> tuple[set[str], set[str]]:
    schema_leaves = leaf_paths(schema)
    mapped = set(field_map["map"].keys())
    return schema_leaves - mapped, mapped - schema_leaves


def test_mapping_table_covers_schema_exactly(schema, field_map):
    unmapped, stale = drift(schema, field_map)
    assert not unmapped, f"schema fields missing from field_map.json: {sorted(unmapped)}"
    assert not stale, f"field_map.json rows with no schema field: {sorted(stale)}"


def test_mapping_version_matches_schema_version(schema, field_map):
    assert field_map["canonical_schema_version"] == schema["properties"]["schema_version"]["const"]


def test_null_targets_all_carry_notes(field_map):
    """A null target is a stated decision; the note is the statement."""
    nulls = {
        f"{path}"
        for path, targets in field_map["map"].items()
        for target, value in targets.items()
        if value is None
    }
    assert nulls == set(field_map["null_target_notes"].keys())


# drift test negative controls: prove the detector can fire (skill rule 5)


def test_drift_fires_on_added_schema_field(schema, field_map):
    mutated = copy.deepcopy(schema)
    mutated["properties"]["new_unmapped_field"] = {"type": ["string", "null"]}
    unmapped, _ = drift(mutated, field_map)
    assert "new_unmapped_field" in unmapped


def test_drift_fires_on_removed_schema_field(schema, field_map):
    mutated = copy.deepcopy(schema)
    del mutated["properties"]["preview"]
    _, stale = drift(mutated, field_map)
    assert "preview" in stale


def test_drift_fires_on_stale_mapping_row(schema, field_map):
    mutated = copy.deepcopy(field_map)
    mutated["map"]["ghost.field"] = {"sarif": "x", "flare_ai": "y"}
    _, stale = drift(schema, mutated)
    assert "ghost.field" in stale


# --- D-020 (#6): format asserts, it does not annotate ---


def test_malformed_timestamp_refused():
    """Negative control: a garbage discovered_at must FAIL validation. Under
    annotation-only format (the pre-fix state) this validated silently."""
    from finding_bridge.core.schema import SchemaValidationError, validate_finding

    finding = load(FIXTURES / "candidate_full.json")
    finding["discovered_at"] = "not-a-timestamp"
    with pytest.raises(SchemaValidationError):
        validate_finding(finding)


def test_malformed_confirmed_at_refused():
    from finding_bridge.core.schema import SchemaValidationError, validate_finding

    finding = load(FIXTURES / "candidate_full.json")
    finding["provenance"]["confirmed_at"] = "yesterday-ish"
    with pytest.raises(SchemaValidationError):
        validate_finding(finding)


def test_valid_fixtures_pass_project_validator():
    """Positive control: both fixtures pass the asserting validator."""
    from finding_bridge.core.schema import validate_finding

    validate_finding(load(FIXTURES / "candidate_full.json"))
    validate_finding(load(FIXTURES / "candidate_null_fields.json"))
