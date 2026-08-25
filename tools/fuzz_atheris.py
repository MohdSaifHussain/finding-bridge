"""OB-5: coverage-guided fuzzing of both ingest parsers with Atheris (Linux).

    python tools/fuzz_atheris.py <corpus-dir> -max_total_time=1800 [libFuzzer flags]

Runs on ubuntu-latest via .github/workflows/fuzz.yml (workflow_dispatch
only, audit cadence, D-027). Atheris ships manylinux wheels only, which is
why the Windows development machine ran the structured alternative
(tools/fuzz_ingest.py) and this file exists for the runner.

HARNESS. One input at a time, the first byte selects the parser; the rest
is the parser's input. The garak parser reads a file, so the bytes are
written to a scratch path first (with a size cap below the 10 MiB
boundary so the run measures parsing, not the cap). The transcript
parser takes text: the bytes decode as UTF-8 with replacement, then a
second pass feeds the raw bytes through the CLI file path too, so the
encoding boundary is exercised.

WHAT COUNTS AS A FINDING: any exception that is not one of the parsers'
governed error classes (GarakAdapterError, TranscriptAdapterError,
InputError) escaping to Atheris, which reports it as a crash with the
reproducing input saved beside the run. Governed refusals are expected
outcomes.

WHAT A PASS DOES NOT PROVE: that no input outside the reached coverage
crashes the parsers; only that libFuzzer, starting from the corpus and
guided by coverage for the budgeted minutes, found none. The run prints
libFuzzer's own statistics (executions, coverage edges, corpus size),
which are the width of the claim.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import atheris  # noqa: E402

with atheris.instrument_imports():
    from finding_bridge.adapters import reading
    from finding_bridge.adapters.in_ import garak, transcript

GOVERNED = (garak.GarakAdapterError, transcript.TranscriptAdapterError, reading.InputError)
SCRATCH = Path(tempfile.mkdtemp(prefix="fb-atheris-"))
MAX_BYTES = 200_000


def one_input(data: bytes) -> None:
    if not data:
        return
    kind, payload = data[0] % 3, data[1:MAX_BYTES]
    try:
        if kind == 0:
            p = SCRATCH / "in.jsonl"
            p.write_bytes(payload)
            garak.parse_hitlog(p)
        elif kind == 1:
            text = payload.decode("utf-8", errors="replace")
            grammar = "human-assistant" if len(payload) % 2 else "user-assistant"
            transcript.to_candidate(text, {"grammar": grammar})
        else:
            p = SCRATCH / "in.txt"
            p.write_bytes(payload)
            transcript.to_candidate(reading.read_text_capped(str(p)), None)
    except GOVERNED:
        return


def main() -> None:
    atheris.Setup(sys.argv, one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
