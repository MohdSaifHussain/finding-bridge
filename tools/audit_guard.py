"""The audit tree guard (ruling D-067). Permanent tool.

Run this BEFORE any mutation-testing run and AFTER it:

    python tools/audit_guard.py acquire   # before: refuses a dirty or held tree
    python tools/audit_guard.py release   # after: verifies clean, drops the lock

WHY THIS EXISTS, and the lesson it carries (D-067, ruled into this
docstring): a mutation run was launched while another was still going.
Two cosmic-ray processes raced the same source file and the same
database. The tree was left holding live mutants, and every mutant
measured after that point ran against a corrupted baseline - a wrong
number that was nearly published.

The run's own `TREE-OK` echo said the tree was fine. It was a SINGLE
WITNESS restating a cached check. `git status`, re-derived at the moment
it mattered, is what beat it. That is the whole lesson, and it is why
every check below shells out to git rather than trusting a stored answer:
a status echo is not a status.

Two refusals, each with its own reason code:
  audit-tree-dirty  - the working tree has uncommitted source changes, so
                      a run would measure against an unknown baseline and
                      may leave mutants indistinguishable from real edits.
  audit-in-progress - another audit holds the tree. Racing instruments is
                      how the corrupted measurement happened; if it is
                      possible once it is possible twice.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# FB_AUDIT_REPO lets the guard be tested against a temp repo. Without it
# the guard governs this repo, which is the only production use.
REPO = Path(os.environ.get("FB_AUDIT_REPO", Path(__file__).resolve().parent.parent))
LOCK = REPO / ".audit-lock"

REASON_TREE_DIRTY = "audit-tree-dirty"
REASON_IN_PROGRESS = "audit-in-progress"

STALE_AFTER_SECONDS = 3 * 60 * 60  # a lock older than this is abandoned, not held


def source_is_dirty() -> str:
    """Re-derived, never cached: what git says right now."""
    result = subprocess.run(
        ["git", "status", "--porcelain", "src/", "tests/", "tests_audit/"],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    return result.stdout.strip()


def acquire() -> int:
    if LOCK.exists():
        age = time.time() - LOCK.stat().st_mtime
        holder = LOCK.read_text(encoding="utf-8").strip()
        if age < STALE_AFTER_SECONDS:
            print(
                f"{REASON_IN_PROGRESS}: another audit holds the tree "
                f"({holder}, {age:.0f}s ago). Racing instruments corrupt "
                "measurements; stop that run or wait for it.",
                file=sys.stderr,
            )
            return 1
        print(f"[guard] clearing a stale lock ({age:.0f}s old, {holder})")
        LOCK.unlink()

    dirty = source_is_dirty()
    if dirty:
        print(
            f"{REASON_TREE_DIRTY}: uncommitted source changes present, so an "
            "audit would measure an unknown baseline and could leave mutants "
            f"indistinguishable from real edits:\n{dirty}",
            file=sys.stderr,
        )
        return 1

    LOCK.write_text(
        f"pid {os.getpid()} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n", encoding="utf-8"
    )
    print("[guard] tree clean, lock acquired")
    return 0


def release() -> int:
    dirty = source_is_dirty()
    LOCK.unlink(missing_ok=True)
    if dirty:
        print(
            f"{REASON_TREE_DIRTY}: the audit left the tree dirty - a mutant is "
            "probably still applied. Restore with `git checkout -- src/` and "
            f"DISCARD the run's figures:\n{dirty}",
            file=sys.stderr,
        )
        return 1
    print("[guard] tree clean, lock released")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in ("acquire", "release"):
        print("usage: audit_guard.py [acquire|release]", file=sys.stderr)
        return 2
    return acquire() if argv[1] == "acquire" else release()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
