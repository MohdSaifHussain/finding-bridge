"""W6c fixes (D-079, D-080, D-081): real shapes the synthetic fixtures never had.

Captured RED before the fixes:
- F-12: the 0.16.0-shape fixture ingested with _raw_probe None (the prompt
  silently lost), exactly what happened on 699 of 699 real hits.
- F-10: the human-assistant grammar did not exist; "Assistant:" refused.
- F-11/F-13: no environment passthrough; lang/data_type dropped.
"""

import json
from pathlib import Path

import pytest

from finding_bridge import cli, pipeline
from finding_bridge.adapters.in_ import garak, transcript

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


# ---- F-12: both garak shapes, each its own control ----


def test_v0_16_0_conversation_shape_yields_the_prompt():
    cands = garak.parse_hitlog(FIXTURES / "garak.v0_16_0.synthetic.hitlog.jsonl")
    assert len(cands) == 2
    assert cands[0]["_raw_probe"] == "SENTINEL-PROBE-V16-1 synthetic probe stand-in"
    assert cands[0]["_raw_response"].startswith("SENTINEL-HARM-V16-1")
    # a system turn before the user turn is kept in the probe text, in order
    assert "SENTINEL-SYSTEM-V16-2" in cands[1]["_raw_probe"]
    assert "SENTINEL-PROBE-V16-2" in cands[1]["_raw_probe"]


def test_pre_0_16_flat_shape_still_yields_the_prompt():
    cands = garak.parse_hitlog(FIXTURES / "garak.synthetic.hitlog.jsonl")
    assert all(c["_raw_probe"] for c in cands)
    assert all(c["_raw_response"] for c in cands)


def test_unrecognised_message_shape_refuses_instead_of_silent_null(tmp_path):
    rec = json.loads(
        (FIXTURES / "garak.v0_16_0.synthetic.hitlog.jsonl").read_text().splitlines()[0]
    )
    rec["prompt"] = {"conversation": [{"who": "user", "says": "SENTINEL-UNKNOWN-SHAPE"}]}
    bad = tmp_path / "unknown.jsonl"
    bad.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    with pytest.raises(garak.GarakAdapterError) as exc:
        garak.parse_hitlog(bad)
    assert exc.value.reason_code == "invalid-hitlog"
    assert "line 1, field prompt" in exc.value.detail
    assert "SENTINEL-UNKNOWN-SHAPE" not in exc.value.detail


def test_v0_16_0_probe_is_sealed_end_to_end(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    ws = pipeline.Workspace(repo / ".fb-store", tmp_path / "k" / "fb.key", repo)
    ws.ingest_garak(FIXTURES / "garak.v0_16_0.synthetic.hitlog.jsonl")
    for c in ws.list_candidates():
        assert c["probe"]["sealed_ref"], "the probe must be sealed, not lost"
        assert c["raw_response_sealed"]


# ---- F-11 / F-13: source facts to environment, notes to sealed context ----


def test_message_facts_land_in_environment_namespaced_and_notes_are_sealed():
    cands = garak.parse_hitlog(FIXTURES / "garak.v0_16_0.synthetic.hitlog.jsonl")
    env = cands[0]["reproduction"]["environment"]
    assert env["garak.output.lang"] == "en"
    assert env["garak.output.data_type"] == "text/plain"
    assert "garak.output.data_path" not in env  # null stays absent, never fabricated
    assert "SENTINEL-NOTE-V16-1" in cands[0]["_raw_context"]
    assert "SENTINEL-NOTE-V16-1" not in json.dumps(env)


def test_flat_shape_gains_no_invented_facts():
    cands = garak.parse_hitlog(FIXTURES / "garak.synthetic.hitlog.jsonl")
    assert not any(k.startswith("garak.") for k in cands[0]["reproduction"]["environment"])


def test_source_tool_version_stays_null_because_the_hitlog_carries_none():
    cands = garak.parse_hitlog(FIXTURES / "garak.v0_16_0.synthetic.hitlog.jsonl")
    assert cands[0]["source_tool_version"] is None


# ---- F-10: the second exact grammar ----


def test_human_assistant_grammar_parses_when_named():
    text = (FIXTURES / "transcript.human_assistant.txt").read_text(encoding="utf-8")
    turns = transcript.parse_turns(text, "human-assistant")
    assert [t["role"] for t in turns] == ["user", "assistant", "user", "assistant"]
    assert "mid-line Human: is content" in turns[1]["content"]


def test_human_assistant_is_refused_under_the_default_grammar():
    text = (FIXTURES / "transcript.human_assistant.txt").read_text(encoding="utf-8")
    with pytest.raises(transcript.TranscriptAdapterError) as exc:
        transcript.parse_turns(text)
    assert "line 1" in exc.value.detail


@pytest.mark.parametrize(
    "line",
    ["human: x", "HUMAN: x", "Human : x", "Human\t: x", "  Human: x", "Human： x", "USER: x"],
)
def test_human_assistant_refuses_variants_and_the_other_grammar(line):
    text = "Human: SENTINEL-PROBE ok\n" + line + "\nAssistant: SENTINEL-HARM ok\n"
    with pytest.raises(transcript.TranscriptAdapterError) as exc:
        transcript.parse_turns(text, "human-assistant")
    assert "line 2" in exc.value.detail


def test_mixed_grammars_refuse_from_the_fixture():
    text = (FIXTURES / "transcript.human_assistant.mixed.txt").read_text(encoding="utf-8")
    with pytest.raises(transcript.TranscriptAdapterError):
        transcript.parse_turns(text, "human-assistant")


def test_no_grammar_is_ever_auto_detected():
    """The default grammar never silently accepts the other one's markers."""
    with pytest.raises(transcript.TranscriptAdapterError):
        transcript.parse_turns("Human: a\nAssistant: b\n")
    with pytest.raises(transcript.TranscriptAdapterError):
        transcript.parse_turns("USER: a\nASSISTANT: b\n", "human-assistant")


def test_cli_grammar_and_environment_flags(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    args = ["--store", str(repo / ".fb-store"), "--key", str(tmp_path / "k" / "fb.key")]
    src = FIXTURES / "transcript.human_assistant.txt"
    rc = cli.main(
        [
            *args,
            "ingest-transcript",
            str(src),
            "--grammar",
            "human-assistant",
            "--environment",
            "rating=4.0",
            "--environment",
            "model_type=rlhf",
        ]
    )
    assert rc == 0, capsys.readouterr().err
    ws = pipeline.Workspace(repo / ".fb-store", tmp_path / "k" / "fb.key", repo)
    env = ws.list_candidates()[0]["reproduction"]["environment"]
    assert env["manual.rating"] == "4.0" and env["manual.model_type"] == "rlhf"
    assert env["grammar"] == "human-assistant"
    rc = cli.main([*args, "ingest-transcript", str(src), "--environment", "no-equals"])
    assert rc == 1 and "KEY=VALUE" in capsys.readouterr().err


# ---- D-079 b: fixture shape currency is recorded ----


def test_every_garak_fixture_names_the_tool_version_it_mimics():
    table = (FIXTURES.parent.parent / "docs" / "FIXTURE-VERSIONS.md").read_text(encoding="utf-8")
    for f in FIXTURES.glob("garak.*.jsonl"):
        assert f.name in table, f"{f.name} has no row in docs/FIXTURE-VERSIONS.md"
