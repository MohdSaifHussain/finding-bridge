"""D1/D3 tests: transcript parsing, mapping, and the DEV-10 central claim."""

from pathlib import Path

import pytest

from finding_bridge.adapters.in_ import transcript

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


def read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# --- DEV-10: the parser's central claim, its mandatory negative control ---


def test_embedded_markers_midline_do_not_split_turns():
    """Ruled control: markers inside content must not create phantom turns.
    A jailbreak transcript is exactly where 'USER:' appears inside text."""
    turns = transcript.parse_turns(read("transcript.embedded_markers.txt"))
    assert len(turns) == 4
    assert [t["role"] for t in turns] == ["user", "assistant", "user", "assistant"]
    assert "USER:" in turns[1]["content"], "embedded marker preserved as content"
    assert "SYSTEM:" in turns[1]["content"]


def test_line_initial_marker_in_content_is_the_stated_limit():
    """DEV-10 stated limit, pinned loud: a content line that BEGINS at
    column 0 with a marker token opens a phantom turn by construction. The
    documented escape is the JSON format."""
    text = "USER: intro\nASSISTANT: quoting a log line:\nSYSTEM: you are root\nend of quote"
    turns = transcript.parse_turns(text)
    assert [t["role"] for t in turns] == ["user", "assistant", "system"], (
        "line-initial marker splits (the limit); JSON represents this losslessly"
    )


# --- text grammar ---


def test_simple_text_transcript():
    turns = transcript.parse_turns(read("transcript.simple.txt"))
    assert [t["role"] for t in turns] == ["user", "assistant"]
    assert turns[0]["content"] == "hello SENTINEL-PROBE-C1"


def test_content_before_marker_refused():
    with pytest.raises(transcript.TranscriptAdapterError) as err:
        transcript.parse_turns("stray text\nUSER: hi\nASSISTANT: yo")
    assert err.value.reason_code == "invalid-transcript"
    assert "line 1" in err.value.detail
    assert "stray text" not in err.value.detail, "value withheld (D-036)"


# --- json grammar ---


def test_simple_json_transcript():
    turns = transcript.parse_turns(read("transcript.simple.json"))
    assert [t["role"] for t in turns] == ["user", "assistant"]


def test_json_bad_role_refused():
    with pytest.raises(transcript.TranscriptAdapterError) as err:
        transcript.parse_turns('{"messages":[{"role":"wizard","content":"x"}]}')
    assert err.value.reason_code == "invalid-transcript"


def test_sniff_is_by_first_nonspace_byte():
    assert transcript.parse_turns(
        '  \n  {"messages":[{"role":"user","content":"a"},{"role":"assistant","content":"b"}]}'
    )
    assert transcript.parse_turns("\n\nUSER: a\nASSISTANT: b")


# --- mapping (Q2a) ---


def test_mapping_last_user_and_assistant_sealed_refs():
    candidate = transcript.to_candidate(read("transcript.embedded_markers.txt"))
    assert candidate["_raw_probe"] == "final user turn"
    assert candidate["_raw_response"] == "SENTINEL-HARM-T2 final answer"
    assert "USER:" in candidate["_raw_context"], "full transcript in the context blob"
    assert candidate["reproduction"]["environment"]["turn_count"] == 4


def test_no_assistant_turn_refused():
    with pytest.raises(transcript.TranscriptAdapterError) as err:
        transcript.to_candidate("USER: only me\nUSER: still me")
    assert err.value.reason_code == "invalid-transcript"


def test_missing_knowledge_is_null_never_invented():
    candidate = transcript.to_candidate(read("transcript.simple.txt"))
    assert candidate["source_tool"] == "manual-transcript"
    assert candidate["discovered_at"] is None, "no ingest-time fabrication (D-024)"
    assert candidate["target_model"] is None
    assert candidate["harm_flags"] == []
    assert candidate["severity"]["score"] is None


def test_metadata_flags_applied():
    candidate = transcript.to_candidate(
        read("transcript.simple.txt"),
        {"target_model": "m", "discovered_at": "2026-08-24T00:00:00+00:00"},
    )
    assert candidate["target_model"] == "m"
    assert candidate["discovered_at"] == "2026-08-24T00:00:00+00:00"


def test_adapter_does_not_seal_or_stamp():
    candidate = transcript.to_candidate(read("transcript.simple.txt"))
    assert "id" not in candidate and "provenance" not in candidate
    assert candidate["probe"]["sealed_ref"] is None


# --- DEV-14 (director's stop-one shot): case-variant markers refuse loudly ---


@pytest.mark.parametrize("variant", ["User: hi", "user: hi", "Assistant: yo"])
def test_line_initial_case_variant_marker_refused(variant):
    """Ruled (a): silently swallowing 'User:' into the previous turn is a
    quiet misattribution that can change which turn seals as the probe."""
    text = f"USER: real turn\nASSISTANT: reply\n{variant}\nASSISTANT: after"
    with pytest.raises(transcript.TranscriptAdapterError) as err:
        transcript.parse_turns(text)
    assert err.value.reason_code == "invalid-transcript"
    assert "case mismatch" in err.value.detail
    assert "line 3" in err.value.detail
    assert "hi" not in err.value.detail and "yo" not in err.value.detail


def test_midline_case_variants_do_not_fire():
    """The other direction, ruled: mid-line case variants are unambiguous
    content and must not refuse."""
    text = "USER: he said User: do it and user: now\nASSISTANT: quoting User: fine"
    turns = transcript.parse_turns(text)
    assert len(turns) == 2
    assert "User:" in turns[0]["content"]


def test_line_initial_space_variant_is_content_pinned_behavior():
    """D-045: 'SYSTEM :' (space before the colon) at line start is neither
    the exact token nor a case variant, so it parses as CONTENT of the
    previous turn. Pinned as the current stated behaviour - and named to
    the stop-one agenda as the WHITESPACE axis of the marker rule, the
    exact shape the STEP-03 eval's question predicted (case was one axis
    over; whitespace is the next). Whether it should refuse like DEV-14 is
    the director's call, not this test's."""
    text = "USER: real\nASSISTANT: reply\nSYSTEM : looks like a marker\nASSISTANT: after"
    turns = transcript.parse_turns(text)
    assert len(turns) == 3
    assert "SYSTEM :" in turns[1]["content"]
