"""Fixture harm scanner (proposal C1, ruled BUILD at the census stop).

Converts D-012 - "no real harmful model output is ever committed to this
repository, in any phase, ever" - from the project's most safety-critical
SENTENCE into a CHECK.

    python tools/fixture_scan.py

WHAT A PASS DOES NOT PROVE (stated plainly, as ruled). This tool cannot
certify content harmless. It checks CONFORMANCE TO SHAPES WE NAME:

  - every fixture's harm-bearing fields carry a SENTINEL-* marker, the
    project's convention for synthetic stand-ins;
  - no fixture matches a known-harmful-corpus string, if such a list is
    ever supplied (none exists today, and the tool says so rather than
    implying coverage it lacks).

A pass therefore means "these fixtures follow the synthetic convention",
NOT "these fixtures are safe". Real harmful text that happened to contain
the word SENTINEL would pass. Judging content is the fourth quadrant
(D-027): it stays human, and this tool exists to catch the careless case,
not the adversarial one.

EXIT CODES:
  0  every fixture conforms
  1  a fixture's harm-bearing field carries no sentinel marker
  2  the scan could not run (no fixtures found, unreadable file)
"""

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(os.environ.get("FB_FIXTURE_REPO", Path(__file__).resolve().parent.parent))
FIXTURES = REPO / "schemas" / "fixtures"

EXIT_PASS = 0
EXIT_NONCONFORMING = 1
EXIT_COULD_NOT_RUN = 2

SENTINEL = re.compile(r"SENTINEL[-_]", re.IGNORECASE)

# Fields that can carry model output or attack text. A fixture value here
# must be sentinel-marked. Everything else (ids, hashes, timestamps,
# tool names) is metadata and is not scanned.
HARM_BEARING_KEYS = {"content", "output", "prompt", "goal", "text", "_raw_probe", "_raw_response"}

# No known-harmful-corpus list exists. Recorded rather than silently absent.
KNOWN_CORPUS: list[str] = []


def harm_bearing_values(node, path: str = ""):
    """Yield (path, value) for every string under a harm-bearing key."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else key
            if key in HARM_BEARING_KEYS and isinstance(value, str) and value.strip():
                yield here, value
            else:
                yield from harm_bearing_values(value, here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from harm_bearing_values(item, f"{path}[{i}]")


def scan_file(path: Path) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix in (".json", ".jsonl"):
        lines = [text] if path.suffix == ".json" else text.splitlines()
        for lineno, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                problems.append(f"{path.name}:{lineno}: not valid JSON")
                continue
            for field, value in harm_bearing_values(record):
                if not SENTINEL.search(value):
                    problems.append(
                        f"{path.name}:{lineno}: field {field} carries text with no "
                        "SENTINEL marker (value withheld per D-036)"
                    )
    else:  # transcript-style text fixtures
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped and not SENTINEL.search(line) and len(stripped) > 60:
                problems.append(
                    f"{path.name}:{lineno}: long line with no SENTINEL marker "
                    "(value withheld per D-036)"
                )
    for needle in KNOWN_CORPUS:
        if needle in text:
            problems.append(f"{path.name}: matches a known-harmful-corpus entry")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print("fixture_scan takes no arguments; there is no override", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if not FIXTURES.is_dir():
        print(f"could-not-run: no fixtures directory at {FIXTURES}", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    files = sorted(p for p in FIXTURES.iterdir() if p.is_file())
    if not files:
        print("could-not-run: fixtures directory is empty", file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    problems: list[str] = []
    for path in files:
        try:
            problems.extend(scan_file(path))
        except OSError as exc:
            print(f"could-not-run: {path.name} ({type(exc).__name__})", file=sys.stderr)
            return EXIT_COULD_NOT_RUN

    if problems:
        print("FIXTURE SCAN: NONCONFORMING")
        for problem in problems:
            print(f"  {problem}")
        return EXIT_NONCONFORMING
    print(f"FIXTURE SCAN: CONFORMING ({len(files)} fixtures)")
    if not KNOWN_CORPUS:
        print("  note: no known-harmful-corpus list is configured; shape conformance only")
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
