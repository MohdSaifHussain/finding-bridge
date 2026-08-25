"""D6 tests: garak hitlog to canonical candidates. Pure translation."""

from pathlib import Path

import pytest

from finding_bridge.adapters.in_ import garak

FIXTURE = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
HITLOG = FIXTURE / "garak.synthetic.hitlog.jsonl"


def test_parses_all_lines():
    candidates = garak.parse_hitlog(HITLOG)
    assert len(candidates) == 3


def test_message_dict_and_plain_string_prompts_extracted():
    candidates = garak.parse_hitlog(HITLOG)
    assert candidates[0]["_raw_probe"].startswith("SENTINEL-PROBE-7001")
    assert candidates[0]["_raw_response"].startswith("SENTINEL-HARM-7001")
    assert candidates[2]["_raw_probe"].startswith("SENTINEL-PROBE-7002")
    assert candidates[2]["_raw_response"].startswith("SENTINEL-HARM-7002")


def test_source_facts_mapped_and_missing_fields_null():
    c = garak.parse_hitlog(HITLOG)[0]
    assert c["source_tool"] == "garak"
    assert c["source_tool_version"] is None, "hitlog has no version; never invent"
    assert c["target_model"] == "test synthetic-model"
    assert c["discovered_at"] is None, "hitlog has no timestamp; never invent (D-024)"
    assert c["harm_flags"] == ["garak-detector:mitigation.SyntheticDetector"]
    assert c["taxonomy"] == {"owasp_llm": [], "saif": [], "atlas": []}, "no invented taxonomy"
    assert c["severity"]["score"] is None, "severity is the human gate's call"
    assert c["reproduction"]["environment"]["run_id"] == "11111111-2222-3333-4444-555555555555"


def test_adapter_does_not_seal_or_stamp():
    """Contract 3.11: pure translation; core does sealing and hashing."""
    c = garak.parse_hitlog(HITLOG)[0]
    assert "id" not in c
    assert "provenance" not in c
    assert "dedup" not in c
    assert c["probe"]["sealed_ref"] is None
    assert c["raw_response_sealed"] is None


def test_non_jsonl_input_refused(tmp_path: Path):
    bad = tmp_path / "not-a-hitlog.jsonl"
    bad.write_text("this is not json\n", encoding="utf-8")
    with pytest.raises(garak.GarakAdapterError) as err:
        garak.parse_hitlog(bad)
    assert err.value.reason_code == "invalid-hitlog"
    assert "line 1" in err.value.detail


def test_non_object_line_refused(tmp_path: Path):
    bad = tmp_path / "list.jsonl"
    bad.write_text('["an", "array"]\n', encoding="utf-8")
    with pytest.raises(garak.GarakAdapterError) as err:
        garak.parse_hitlog(bad)
    assert err.value.reason_code == "invalid-hitlog"
