"""S2-1 controls (D-038, FULL): hostile numeric values refuse at BOTH
layers, and refusal details never echo source values (D-036).

The hostile fixture carries NaN, Infinity, and 9007199254740993 (2^53+1),
each beside sentinel harm stand-ins (D-012), because the no-echo rule is
tested exactly where a fix would instinctively echo the offending value.
"""

import math
from pathlib import Path

import pytest

from finding_bridge.adapters.in_ import garak
from finding_bridge.core import dedup
from finding_bridge.core import provenance as prov
from finding_bridge.core.schema import SchemaValidationError, validate_finding

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
HOSTILE = FIXTURES / "garak.hostile.hitlog.jsonl"
CLEAN = FIXTURES / "garak.synthetic.hitlog.jsonl"

HOSTILE_VALUES = [
    ("NaN", float("nan")),
    ("Infinity", float("inf")),
    ("2^53+1", 9007199254740993),
]


# --- layer (b), primary: the ingest boundary refuses ---


def hostile_single_line(tmp_path: Path, index: int) -> Path:
    line = HOSTILE.read_text(encoding="utf-8").splitlines()[index]
    p = tmp_path / f"hostile-{index}.jsonl"
    p.write_text(line + "\n", encoding="utf-8")
    return p


@pytest.mark.parametrize("index,name", [(0, "NaN"), (1, "Infinity"), (2, "2^53+1")])
def test_boundary_refuses_each_hostile_value(tmp_path: Path, index: int, name: str):
    with pytest.raises(garak.GarakAdapterError) as err:
        garak.parse_hitlog(hostile_single_line(tmp_path, index))
    assert err.value.reason_code == "invalid-hitlog"
    assert "line 1" in err.value.detail, "detail names the location"


def test_boundary_refusal_names_field_path_not_value(tmp_path: Path):
    with pytest.raises(garak.GarakAdapterError) as err:
        garak.parse_hitlog(hostile_single_line(tmp_path, 2))
    assert "attempt_seq" in err.value.detail, "field path named"
    assert "9007199254740993" not in err.value.detail, "value never echoed (D-036)"


def test_no_echo_of_sentinels_in_refusal(tmp_path: Path):
    """D-036 control: the sentinel beside the invalid field appears nowhere
    in the refusal; positive control: the search CAN find it in the file."""
    assert "SENTINEL-HARM-HOSTILE-A" in HOSTILE.read_text(encoding="utf-8")
    with pytest.raises(garak.GarakAdapterError) as err:
        garak.parse_hitlog(HOSTILE)
    refusal_text = f"{err.value.reason_code}: {err.value.detail}"
    assert "SENTINEL" not in refusal_text
    assert "HOSTILE" not in refusal_text


def test_clean_fixture_still_parses():
    """Positive control: the boundary accepts representable numbers."""
    assert len(garak.parse_hitlog(CLEAN)) == 3


# --- layer (a), backstop: the hash path translates, never crashes raw ---


@pytest.mark.parametrize("name,value", HOSTILE_VALUES)
def test_backstop_content_hash_refuses(name, value):
    with pytest.raises(prov.ProvenanceError) as err:
        prov.content_hash({"preview": "x", "n": value})
    assert err.value.reason_code == "uncanonicalizable"


@pytest.mark.parametrize("name,value", HOSTILE_VALUES)
def test_backstop_dedup_key_refuses(name, value):
    with pytest.raises(prov.ProvenanceError) as err:
        dedup.dedup_key({"id": "fb-x", "n": value})
    assert err.value.reason_code == "uncanonicalizable"


def test_backstop_detail_never_echoes_value():
    with pytest.raises(prov.ProvenanceError) as err:
        prov.content_hash({"n": float("nan"), "beside": "SENTINEL-HARM-ECHO"})
    text = f"{err.value.reason_code}: {err.value.detail}"
    assert "nan" not in text.lower() or "not representable" in text
    assert "SENTINEL" not in text and "ECHO" not in text


def test_backstop_valid_content_unaffected():
    """Positive control: finite numbers hash as before."""
    assert math.isfinite(1.5)
    assert len(prov.content_hash({"n": 1.5, "m": 2**53 - 1})) == 64


# --- D-036 applied to the one audited echoer: schema-invalid ---


def test_schema_invalid_detail_names_path_not_value():
    import copy
    import json

    finding = json.loads((FIXTURES / "candidate_full.json").read_text(encoding="utf-8"))
    bad = copy.deepcopy(finding)
    bad["taxonomy"]["owasp_llm"][0]["status"] = "SENTINEL-HARM-ECHO-VALUE"
    with pytest.raises(SchemaValidationError) as err:
        validate_finding(bad)
    assert "SENTINEL-HARM-ECHO-VALUE" not in err.value.detail, "instance value never echoed"
    assert "status" in err.value.detail, "path to the failure named"
