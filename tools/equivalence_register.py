"""Equivalence-claim register (proposal C5, ruled BUILD at the census stop).

111 of 125 surviving mutants rest on the builder's reasoning that they are
equivalent. Nothing checked those claims, and their share grew every arc.
This tool does not verify them. It makes them COUNTABLE and AUDITABLE:

    python tools/equivalence_register.py check cr-provenance-s5.sqlite ...

WHAT A PASS DOES NOT PROVE, stated first because it is the whole point:
**this tool verifies nothing about whether a mutant is truly equivalent.**
A wrong equivalence claim passes here exactly as a right one does. What it
proves is narrower and still worth having:

  - every surviving mutant is covered by a dated, written disposition;
  - a survivor with NO disposition fails the audit, so an undispositioned
    claim cannot hide in an aggregate;
  - a disposition whose line no longer exists is flagged STALE, so the
    register cannot quietly describe code that has moved on.

That converts an invisible aggregate into a list someone can read and
disagree with, which is what D-029's spirit demands. Judging the claims
themselves is the fourth quadrant (D-027) and stays human.

EXIT CODES:
  0  every survivor is dispositioned and no disposition is stale
  1  undispositioned survivors, or stale dispositions
  2  the register could not run (missing database or register file)
"""

import json
import os
import sqlite3
import sys
from pathlib import Path

REPO = Path(os.environ.get("FB_REGISTER_REPO", Path(__file__).resolve().parent.parent))
REGISTER = REPO / "evidence" / "equivalence-register.json"

EXIT_PASS = 0
EXIT_PROBLEM = 1
EXIT_COULD_NOT_RUN = 2


def load_register() -> dict:
    if not REGISTER.exists():
        return {"claims": []}
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def survivors(db: Path) -> list[dict]:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute(
        """SELECT m.module_path, m.operator_name, m.start_pos_row
           FROM mutation_specs m JOIN work_results r ON m.job_id = r.job_id
           WHERE r.test_outcome = 'SURVIVED'"""
    ).fetchall()
    con.close()
    return [
        {"module": Path(p).name, "operator": op.replace("core/", ""), "line": line}
        for p, op, line in rows
    ]


def claim_key(claim: dict) -> tuple:
    return (claim["module"], claim["class"])


def classify(survivor: dict, source_line: str) -> str:
    """The FROZEN adjustment classes (D-066), reused here so one
    vocabulary serves both the ratchet and the register."""
    if "lru_cache" in source_line:
        return "lru-cache-equivalent"
    if "|" in source_line and ("str |" in source_line or "dict |" in source_line):
        return "annotation-equivalent"
    return f"{survivor['module']}:{survivor['line']}"


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] != "check":
        print("usage: equivalence_register.py check <db> [<db> ...]", file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    register = load_register()
    claims = {(c["module"], c["class"]): c for c in register["claims"]}

    undispositioned: list[str] = []
    seen: set[tuple] = set()
    total = 0

    for db_name in argv[2:]:
        db = REPO / db_name
        if not db.exists():
            print(f"could-not-run: no database at {db}", file=sys.stderr)
            return EXIT_COULD_NOT_RUN
        module_file = REPO / "src" / "finding_bridge" / "core" / db_name.split("-")[1].split(".")[0]
        source = (
            (module_file.with_suffix(".py")).read_text(encoding="utf-8").splitlines()
            if module_file.with_suffix(".py").exists()
            else []
        )
        for survivor in survivors(db):
            total += 1
            line_text = source[survivor["line"] - 1] if survivor["line"] <= len(source) else ""
            klass = classify(survivor, line_text)
            key = (survivor["module"], klass)
            seen.add(key)
            if key not in claims:
                undispositioned.append(
                    f"{survivor['module']} L{survivor['line']} "
                    f"{survivor['operator']} -> class {klass!r}: NO DISPOSITION"
                )

    stale = [f"{m}:{c}" for (m, c) in claims if (m, c) not in seen]

    print(f"EQUIVALENCE REGISTER: {total} survivors, {len(claims)} claims on file")
    if undispositioned:
        print(f"  UNDISPOSITIONED ({len(set(undispositioned))}):")
        for item in sorted(set(undispositioned))[:20]:
            print(f"    {item}")
    if stale:
        print(f"  STALE (claim no longer matches any survivor): {sorted(stale)}")
    if undispositioned or stale:
        print("REGISTER: PROBLEM")
        return EXIT_PROBLEM
    print("REGISTER: EVERY SURVIVOR DISPOSITIONED (none of them VERIFIED)")
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
