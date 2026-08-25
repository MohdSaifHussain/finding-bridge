"""D2 (D-036 as a tool, skill rule 14): the class check, not an instance.

For every dependency call the in-adapters make at the untrusted-input
boundary, this table names the exception classes it can raise and asserts
each surfaces as a governed reason code, never a traceback. A dependency
call absent from BOUNDARY_TABLE is a review-stop finding (3.4); the
coverage test below fails if the parser gains an unlisted raising call.

The tool proves it can fail (ruled): test_boundary_tool_detects_a_raw_leak
drives the missing-file boundary through the CLI path that shipped a raw
FileNotFoundError before D5, asserting the governed refusal now stands -
the same shape that ran red at ratification.
"""

import io
import json
from pathlib import Path

import pytest

from finding_bridge.adapters import reading
from finding_bridge.adapters.in_ import garak, transcript

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


def _oversize(tmp_path: Path) -> Path:
    p = tmp_path / "big.txt"
    p.write_bytes(b"USER: " + b"x" * (reading.MAX_INPUT_BYTES + 1))
    return p


# --- The boundary table: (name, trigger, expected reason code). Each row is
# --- one dependency call that can raise on untrusted input. ---


def _row_missing_file(tmp_path):
    reading.read_text_capped(str(tmp_path / "nope.txt"))


def _row_directory(tmp_path):
    reading.read_text_capped(str(tmp_path))


def _row_bad_utf8(tmp_path):
    p = tmp_path / "b.txt"
    p.write_bytes(b"USER: \xff\xfe not utf8")
    reading.read_text_capped(str(p))


def _row_oversize_file(tmp_path):
    reading.read_text_capped(str(_oversize(tmp_path)))


def _row_oversize_stdin(tmp_path):
    stream = io.BytesIO(b"USER: " + b"x" * (reading.MAX_INPUT_BYTES + 1))
    reading.read_text_capped("-", stdin_buffer=io.BufferedReader(stream))


def _row_text_bad_json_shape(tmp_path):
    transcript.parse_turns('{"not": "messages"}')


def _row_text_malformed_json(tmp_path):
    transcript.parse_turns("{ broken json")


def _row_text_no_marker(tmp_path):
    transcript.parse_turns("just some text with no role marker")


def _row_text_no_assistant(tmp_path):
    transcript.to_candidate("USER: hi\nUSER: still me")


def _row_garak_bad_json(tmp_path):
    p = tmp_path / "h.jsonl"
    p.write_text("{ not json\n", encoding="utf-8")
    garak.parse_hitlog(p)


BOUNDARY_TABLE = [
    ("reading: file not found", _row_missing_file, reading.REASON_INPUT_UNREADABLE),
    ("reading: path is a directory", _row_directory, reading.REASON_INPUT_UNREADABLE),
    ("reading: non-utf8 decode", _row_bad_utf8, reading.REASON_UNSUPPORTED_ENCODING),
    ("reading: oversize file", _row_oversize_file, reading.REASON_INPUT_TOO_LARGE),
    ("reading: oversize stdin", _row_oversize_stdin, reading.REASON_INPUT_TOO_LARGE),
    (
        "transcript: wrong JSON shape",
        _row_text_bad_json_shape,
        transcript.REASON_INVALID_TRANSCRIPT,
    ),
    ("transcript: malformed JSON", _row_text_malformed_json, transcript.REASON_INVALID_TRANSCRIPT),
    ("transcript: no role marker", _row_text_no_marker, transcript.REASON_INVALID_TRANSCRIPT),
    ("transcript: no assistant turn", _row_text_no_assistant, transcript.REASON_INVALID_TRANSCRIPT),
    ("garak: malformed JSONL", _row_garak_bad_json, garak.REASON_INVALID_HITLOG),
]

GOVERNED_ERRORS = (
    reading.InputError,
    transcript.TranscriptAdapterError,
    garak.GarakAdapterError,
)


@pytest.mark.parametrize(
    "name,trigger,reason", BOUNDARY_TABLE, ids=lambda x: x if isinstance(x, str) else ""
)
def test_every_boundary_call_surfaces_a_reason_code(name, trigger, reason, tmp_path):
    if not isinstance(name, str):
        pytest.skip()
    with pytest.raises(GOVERNED_ERRORS) as err:
        trigger(tmp_path)
    assert err.value.reason_code == reason, (
        f"{name}: expected {reason}, got {err.value.reason_code}"
    )


def test_no_boundary_refusal_echoes_content(tmp_path):
    """Every row's detail is location-not-value (D-036)."""
    for _name, trigger, _ in BOUNDARY_TABLE:
        with pytest.raises(GOVERNED_ERRORS) as err:
            trigger(tmp_path)
        assert "SENTINEL" not in err.value.detail


def test_boundary_tool_detects_a_raw_leak():
    """The tool proves it can fail (ruled). Before D5, ingesting a missing
    file raised a raw FileNotFoundError (observed at ratification through
    the CLI). This asserts the governed refusal now stands; a regression
    that let the raw exception through would fail HERE, red."""
    with pytest.raises(reading.InputError) as err:
        reading.read_text_capped("this-path-does-not-exist.xyz")
    assert err.value.reason_code == reading.REASON_INPUT_UNREADABLE
    with pytest.raises(FileNotFoundError):
        # the UNGUARDED shape, shown explicitly: a bare read still raises raw
        Path("this-path-does-not-exist.xyz").read_text(encoding="utf-8")


def test_json_transcript_never_raises_bare_json_error():
    """Coverage guard (3.4): the transcript JSON path must translate every
    json.JSONDecodeError. Fuzz a batch of malformed inputs; none may escape
    as a bare exception."""
    for bad in ("{", "[", '{"messages":', "\x00", "{'single':1}", "[1,2,"):
        with pytest.raises(transcript.TranscriptAdapterError):
            transcript.parse_turns(bad)


# --- S3-CLOSE-1 (director's ritual, ruled FULL): the OUTPUT side of the
# --- class. The table swept input dependencies only; the fifth instance of
# --- exception-escapes-as-traceback arrived on an emit path. ---


from finding_bridge import cli, pipeline  # noqa: E402


def _confirmed_workspace(tmp_path: Path) -> list[str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    store = str(repo / ".fb-store")
    key = str(tmp_path / "k" / "fb.key")
    ws = pipeline.Workspace(Path(store), Path(key), repo)
    ws.ingest_garak(FIXTURES / "garak.synthetic.hitlog.jsonl")
    ws.confirm(ws.list_candidates()[0]["id"], "T <t@x.invalid>")
    return ["--store", store, "--key", key]


def test_emit_markdown_creates_missing_parent(tmp_path, capsys):
    """Ruled: an output path the user named is intent, not accident - both
    emitters create the parent, agreeing with each other."""
    args = _confirmed_workspace(tmp_path)
    out = tmp_path / "deep" / "nested" / "packet.md"
    assert cli.main([*args, "emit-markdown", str(out)]) == 0
    assert out.exists()


def test_emit_sarif_creates_missing_parent(tmp_path):
    args = _confirmed_workspace(tmp_path)
    out = tmp_path / "also" / "missing" / "findings.sarif"
    assert cli.main([*args, "emit-sarif", str(out)]) == 0
    assert out.exists()


def test_emit_markdown_unwritable_refuses_governed(tmp_path, capsys):
    """A genuinely unwritable destination (parent is a FILE) refuses with
    output-unwritable, location-not-value, exit 1 - never a traceback."""
    args = _confirmed_workspace(tmp_path)
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file", encoding="utf-8")
    rc = cli.main([*args, "emit-markdown", str(blocker / "packet.md")])
    err = capsys.readouterr().err
    assert rc == 1
    assert "output-unwritable" in err
    assert "packet.md" in err


def test_emit_sarif_unwritable_refuses_governed(tmp_path, capsys):
    args = _confirmed_workspace(tmp_path)
    blocker = tmp_path / "blocker2"
    blocker.write_text("i am a file", encoding="utf-8")
    rc = cli.main([*args, "emit-sarif", str(blocker / "f.sarif")])
    err = capsys.readouterr().err
    assert rc == 1
    assert "output-unwritable" in err


def test_emit_flare_creates_missing_parent(tmp_path):
    """W3 emitter obeys the same output law as the other two (D-044)."""
    args = _confirmed_workspace(tmp_path)
    out = tmp_path / "flare" / "dir" / "findings.flare.json"
    assert cli.main([*args, "emit-flare", str(out)]) == 0
    assert out.exists()


def test_emit_flare_unwritable_refuses_governed(tmp_path, capsys):
    args = _confirmed_workspace(tmp_path)
    blocker = tmp_path / "blocker3"
    blocker.write_text("i am a file", encoding="utf-8")
    rc = cli.main([*args, "emit-flare", str(blocker / "f.json")])
    assert rc == 1
    assert "output-unwritable" in capsys.readouterr().err


def test_emit_flare_unconfirmed_refuses_governed(tmp_path, capsys):
    """No confirmed findings: the adapter refuses through the CLI."""
    from finding_bridge.adapters.out import flare_ai

    unconfirmed = json.loads((FIXTURES / "candidate_null_fields.json").read_text(encoding="utf-8"))
    with pytest.raises(flare_ai.FlareAdapterError) as err:
        flare_ai.render_reports([unconfirmed])
    assert err.value.reason_code == "unconfirmed"


def test_emit_tracker_creates_missing_parent(tmp_path):
    """W3 emitter obeys the same output law (D-044)."""
    args = _confirmed_workspace(tmp_path)
    out = tmp_path / "tr" / "dir" / "findings.tracker.json"
    assert cli.main([*args, "emit-tracker", str(out)]) == 0
    assert out.exists()


def test_emit_tracker_unwritable_refuses_governed(tmp_path, capsys):
    args = _confirmed_workspace(tmp_path)
    blocker = tmp_path / "blocker4"
    blocker.write_text("i am a file", encoding="utf-8")
    rc = cli.main([*args, "emit-tracker", str(blocker / "t.json")])
    assert rc == 1
    assert "output-unwritable" in capsys.readouterr().err


# --- STEP-06 W1 (director's ruling D-069, found by the five-minute tour
# --- capture): the WORKSPACE side of the class. An empty $TMPDIR sent the
# --- store root into C:\Program Files\Git and the CLI died with a raw
# --- PermissionError; the key parent has the same shape. Sixth and seventh
# --- instances of exception-escapes-as-traceback, both on workspace setup.


def test_store_root_unwritable_refuses_governed(tmp_path, capsys):
    """Store root whose parent is a FILE: store-unwritable, exit 1,
    location-not-value, never a traceback."""
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file", encoding="utf-8")
    key = tmp_path / "k" / "fb.key"
    rc = cli.main(["--store", str(blocker / "store"), "--key", str(key), "list"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "store-unwritable" in err
    assert "store" in err


def test_key_parent_unwritable_refuses_governed(tmp_path, capsys):
    """Key path whose parent is a FILE: key-unwritable, exit 1,
    location-not-value, never a traceback."""
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file", encoding="utf-8")
    store = tmp_path / "store"
    rc = cli.main(["--store", str(store), "--key", str(blocker / "k" / "fb.key"), "list"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "key-unwritable" in err
    assert "fb.key" in err


def test_store_root_writable_positive_control(tmp_path):
    """Positive control: a normal missing store root is created and works."""
    store = str(tmp_path / "new" / "store")
    key = str(tmp_path / "k" / "fb.key")
    rc = cli.main(["--store", store, "--key", key, "list"])
    assert rc == 0
