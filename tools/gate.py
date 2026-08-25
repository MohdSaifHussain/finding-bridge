"""The gate (proposal C2, ruled BUILD FIRST at the census stop).

Run every gate constituent, capture each exit code UNMASKED, and print one
line:

    GATE: PASS
    GATE: FAIL (pytest)

WHY THIS EXISTS. The gate-half-run family reached six instances before its
mechanism was pinned, and all six share one cause: a failing command's
exit code was masked. Two shell constructs do it:

  python tools/gate.py | tail -2 && ...   <- C-009: the gate ITSELF, masked
                                           (use --verdict-file, never a pipe)
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


def _verdict(verdict_file: Path | None, line: str, code: int) -> int:
    """D-074: write the one-line verdict plus the exit code to a file, so
    nobody ever needs to pipe the gate to read its tail. NEVER PIPE THE
    GATE: a pipe reports the last command's status, not the gate's
    (C-008, C-009)."""
    print(line)
    if verdict_file is not None:
        verdict_file.write_text(f"{line}\nexit {code}\n", encoding="utf-8")
    return code


def main(argv: list[str]) -> int:
    verdict_file: Path | None = None
    args = list(argv[1:])
    if len(args) == 2 and args[0] == "--verdict-file":
        verdict_file = Path(args[1])
        args = []
    if args:
        print(
            f"gate takes no arguments except --verdict-file <path> (got {args}); "
            "there is no override",
            file=sys.stderr,
        )
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
        line = f"GATE: COULD-NOT-RUN ({', '.join(could_not_run)})"
        return _verdict(verdict_file, line, EXIT_COULD_NOT_RUN)
    if failed:
        return _verdict(verdict_file, f"GATE: FAIL ({', '.join(failed)})", EXIT_FAILED)
    return _verdict(verdict_file, "GATE: PASS", EXIT_PASS)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
