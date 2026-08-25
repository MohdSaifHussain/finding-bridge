"""The gate (proposal C2, ruled BUILD FIRST at the census stop).

Run every gate constituent, capture each exit code UNMASKED, and print one
line:

    GATE: PASS
    GATE: FAIL (pytest)

WHY THIS EXISTS. The gate-half-run family reached six instances before its
mechanism was pinned, and all six share one cause: a failing command's
exit code was masked. Two shell constructs do it:

  pytest ... | tail -1 && git commit ...   <- the PIPELINE exits with
                                              tail's status, which is 0
  python script.py                          <- a newline, not `&&`, so a
  git commit ...                               failing script does not
                                               stop the commit

Both produced commits carrying claims that a check had already refuted.
This tool removes the possibility: it runs each constituent with
`subprocess.run` and reads `returncode` directly, where no pipe or
newline can intervene, then reduces everything to one word.

WHAT A PASS DOES NOT PROVE (standard anatomy):
  - It does not prove the tests are correct, only that they passed. A
    test asserting the wrong thing passes here (this project has shipped
    two such tests, both caught by mutation audit, not by the gate).
  - It does not prove coverage. The gate runs what exists.
  - It does not run the AUDIT cadence (mutation testing, the Multitool,
    the audit guard). Those are per-phase, by ruling D-027.
  - It says nothing about anything not in its constituent list below.

There is NO override flag, by ruling. A gate you can skip is a gate you
will skip on the day it matters.

EXIT CODES, distinct by ruling:
  0  every constituent passed
  1  GATE FAILED: a constituent ran and reported failure
  2  GATE COULD NOT RUN: a constituent was missing or could not start,
     which is NOT the same as passing and must never be read as such
"""

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(os.environ.get("FB_GATE_REPO", Path(__file__).resolve().parent.parent))

EXIT_PASS = 0
EXIT_FAILED = 1
EXIT_COULD_NOT_RUN = 2

# name -> argv. Each runs directly; nothing is piped, nothing is shelled.
CONSTITUENTS: list[tuple[str, list[str]]] = [
    ("pytest", [sys.executable, "-m", "pytest", "-q"]),
    ("ruff-check", [sys.executable, "-m", "ruff", "check", "."]),
    ("ruff-format", [sys.executable, "-m", "ruff", "format", "--check", "."]),
]


def run_constituent(name: str, argv: list[str]) -> tuple[str, int, str]:
    """Run one constituent and return its UNMASKED exit code."""
    try:
        result = subprocess.run(
            argv,
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "ANTHROPIC_API_KEY": "dummy-for-gate"},
        )
    except (FileNotFoundError, OSError) as exc:
        return name, -1, f"could not start ({type(exc).__name__})"
    tail = (result.stdout or result.stderr or "").strip().splitlines()
    return name, result.returncode, tail[-1] if tail else ""


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"gate takes no arguments (got {argv[1:]}); there is no override", file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    failed: list[str] = []
    could_not_run: list[str] = []
    for name, command in CONSTITUENTS:
        name, code, last_line = run_constituent(name, command)
        status = "ok" if code == 0 else ("could-not-run" if code == -1 else f"exit {code}")
        print(f"  {name:13} {status:14} {last_line}")
        if code == -1:
            could_not_run.append(name)
        elif code != 0:
            failed.append(name)

    if could_not_run:
        print(f"GATE: COULD-NOT-RUN ({', '.join(could_not_run)})")
        return EXIT_COULD_NOT_RUN
    if failed:
        print(f"GATE: FAIL ({', '.join(failed)})")
        return EXIT_FAILED
    print("GATE: PASS")
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
