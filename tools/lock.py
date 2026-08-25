"""Maintain constraints.txt, the hash-pinned lock of every runtime dependency.

    python tools/lock.py            # rewrite constraints.txt from PINS, hashes from PyPI
    python tools/lock.py --check    # re-derive from PyPI and compare; exit 1 on any drift
    python tools/lock.py --selftest # prove --check can fail (a planted stale hash)

WHY THIS EXISTS (F-6, PROV-4 ratified at STEP-06 stop two): pip's
hash-checking mode needs a hash for every requirement, so the lock must
cover the whole runtime set, and a lock nobody regenerates rots. Whether
Dependabot's pip ecosystem maintains a file named constraints.txt could
not be confirmed from the fetched docs (the supported-ecosystems page is
script-rendered); until the first Dependabot run shows which manifests it
found, THIS tool is the maintenance path, and --check is the drift
detector. Hashes come from https://pypi.org/pypi/<name>/<version>/json,
every file of the release, all platforms, the same source the original
rfc8785 pin used.

WHAT A PASS DOES NOT PROVE: that the pinned versions are current or
secure, only that the file matches what PyPI serves for those exact
versions today. Bumping a version is a human edit of PINS, and a MAJOR
bump of rfc8785 or cryptography stops for the director's ruling.

EXIT CODES: 0 written / in sync; 1 drift found; 2 could not run (network,
unknown release).
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCK = REPO / "constraints.txt"
EXIT_OK, EXIT_DRIFT, EXIT_COULD_NOT_RUN = 0, 1, 2

# Versions a fresh Python 3.14 venv resolved for the built wheel on 2026-08-25,
# plus the Python 3.12 conditional dependency the 3.12 image exposed.
PINS: dict[str, str] = {
    "attrs": "26.1.0",
    "cffi": "2.1.1",
    "cryptography": "50.0.0",
    "jsonschema": "4.26.0",
    "jsonschema-specifications": "2025.9.1",
    "pycparser": "3.0",
    "referencing": "0.37.0",
    "rfc3339-validator": "0.1.4",
    "rfc8785": "0.1.4",
    "rpds-py": "2026.6.3",
    "six": "1.17.0",
    # referencing needs typing-extensions on Python < 3.13 (F-7: the 3.14 venv
    # that resolved these pins never saw it; the 3.12 image did). Pinned for
    # every Python so the lock is complete on the whole supported range.
    "typing-extensions": "4.16.0",
}
HASH_PATH = {"rfc8785", "cryptography"}


def pypi_hashes(name: str, version: str) -> list[str]:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=60) as r:
        files = json.load(r)["urls"]
    if not files:
        raise ValueError(f"{name}=={version}: no files on PyPI")
    return sorted({f["digests"]["sha256"] for f in files})


def render(hashes: dict[str, list[str]], date: str) -> str:
    lines = [
        "# Hash-pinned lock of EVERY runtime dependency (F-6, STEP-06; extends the",
        "# DEV-6 pin of rfc8785 to the whole runtime set). pip's hash-checking mode",
        "# requires hashes for all requirements once any has one, so a partial",
        "# file cannot be used as a constraint on a wheel install. The route that",
        "# works, per pip's secure-installs guide (pip.pypa.io, fetched 2026-08-25):",
        "#",
        "#   python -m build --wheel",
        "#   pip install --require-hashes -r constraints.txt",
        "#   pip install --no-deps dist/finding_bridge-<version>-py3-none-any.whl",
        "#",
        "# Maintained by tools/lock.py (--check detects drift). Hashes from",
        "# https://pypi.org/pypi/<name>/<version>/json (every file of the release,",
        f"# all platforms), fetched {date}. rfc8785 and cryptography sit in the",
        "# hash/sealing path: a MAJOR bump of either stops for the director's",
        "# ruling regardless of a green gate (STEP-06 W5b standing rule).",
    ]
    for name, version in PINS.items():
        if name in HASH_PATH:
            lines.append(f"# {name}: in the hash/sealing path (major bumps stop for a ruling)")
        lines.append(f"{name}=={version} \\")
        digests = hashes[name]
        for i, h in enumerate(digests):
            lines.append(f"    --hash=sha256:{h}" + (" \\" if i < len(digests) - 1 else ""))
    return "\n".join(lines) + "\n"


def fetch_all() -> dict[str, list[str]]:
    return {name: pypi_hashes(name, version) for name, version in PINS.items()}


def hash_lines(text: str) -> set[str]:
    return {ln.strip().rstrip(" \\") for ln in text.splitlines() if "--hash=" in ln}


def check(current: str, fresh: str) -> list[str]:
    problems = []
    cur, new = hash_lines(current), hash_lines(fresh)
    for name, version in PINS.items():
        if f"{name}=={version}" not in current:
            problems.append(f"{name}=={version} missing from constraints.txt")
    for h in sorted(new - cur):
        problems.append(f"PyPI serves a hash the lock lacks: {h[-20:]}")
    for h in sorted(cur - new):
        problems.append(f"lock carries a hash PyPI does not serve: {h[-20:]}")
    return problems


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "write"
    if mode not in ("write", "--check", "--selftest") or len(argv) > 2:
        print("usage: lock.py [--check | --selftest]; there is no override", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if mode == "--selftest":
        fresh = render({n: ["a" * 64] for n in PINS}, "selftest")
        stale = fresh.replace("a" * 64, "b" * 64, 1)
        assert check(stale, fresh), "selftest: a planted stale hash must be reported"
        assert not check(fresh, fresh), "selftest: identical lock must pass"
        print("lock selftest: ok (drift detected, identical passes)")
        return EXIT_OK
    try:
        hashes = fetch_all()
    except (urllib.error.URLError, ValueError, KeyError) as exc:
        print(f"could-not-run: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    date = datetime.now(UTC).date().isoformat()
    fresh = render(hashes, date)
    if mode == "write":
        LOCK.write_text(fresh, encoding="utf-8")
        print(f"constraints.txt written: {len(PINS)} packages, {len(hash_lines(fresh))} hashes")
        return EXIT_OK
    problems = check(LOCK.read_text(encoding="utf-8"), fresh)
    if problems:
        print("LOCK CHECK: DRIFT")
        for p in problems:
            print(f"  {p}")
        return EXIT_DRIFT
    print(f"LOCK CHECK: IN SYNC ({len(PINS)} packages, {len(hash_lines(fresh))} hashes)")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
