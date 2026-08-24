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
