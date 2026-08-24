"""Shared untrusted-input reading for in-adapters (STEP-03 D5, D-018).

One helper both in-adapters use, so the size cap and the governed refusal
of unreadable input live in exactly one place. Every refusal here is
location-not-value (D-036): details name the source and the limit, never
the bytes read.
"""

import io
from pathlib import Path

REASON_INPUT_TOO_LARGE = "input-too-large"
REASON_UNSUPPORTED_ENCODING = "unsupported-encoding"
REASON_INPUT_UNREADABLE = "input-unreadable"

# D-041/Q4: 10 MiB per input, both adapters. A transcript or hitlog beyond
# this is a pipeline mistake, not a paste; refusing early beats an OOM deep
# in sealing. Stated limit; a configurable cap remains addable later
# without unmaking this default.
MAX_INPUT_BYTES = 10 * 1024 * 1024

_CHUNK = 65536
STDIN_SENTINEL = "-"


class InputError(Exception):
    """Raised on unreadable or oversized untrusted input; reason_code is
    machine-readable."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _read_capped(stream: io.BufferedReader, source: str) -> bytes:
    """Read at most MAX_INPUT_BYTES, STOPPING at the limit (DEV-13 cond 1).

    stdin cannot be sized in advance, so the cap is enforced while reading:
    we pull one chunk past the limit only to detect the overflow, never
    buffering the whole oversized stream."""
    buf = bytearray()
    while True:
        chunk = stream.read(_CHUNK)
        if not chunk:
            break
        buf.extend(chunk)
        if len(buf) > MAX_INPUT_BYTES:
            raise InputError(
                REASON_INPUT_TOO_LARGE,
                f"{source} exceeds the {MAX_INPUT_BYTES}-byte input cap "
                "(read stopped at the limit; a configurable cap is addable later)",
            )
    return bytes(buf)


def read_text_capped(path_or_dash: str, stdin_buffer: io.BufferedReader | None = None) -> str:
    """Read an untrusted input file, or stdin when path_or_dash is '-',
    capped and decoded as UTF-8 (BOM tolerated).

    Any non-UTF-8 input refuses with unsupported-encoding rather than
    guessing: mojibake in sealed evidence is silent corruption, and this
    tool never lets harmful content decay quietly into wrong bytes."""
    if path_or_dash == STDIN_SENTINEL:
        source = "stdin"
        import sys

        stream = stdin_buffer if stdin_buffer is not None else sys.stdin.buffer
        raw = _read_capped(stream, source)
    else:
        source = Path(path_or_dash).name
        try:
            with open(path_or_dash, "rb") as fh:
                raw = _read_capped(fh, source)
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
            raise InputError(
                REASON_INPUT_UNREADABLE,
                f"{source} could not be read ({type(exc).__name__})",
            ) from exc
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError(
            REASON_UNSUPPORTED_ENCODING,
            f"{source} is not valid UTF-8 at byte {exc.start}; only UTF-8 "
            "input is accepted (value withheld per D-036)",
        ) from exc
