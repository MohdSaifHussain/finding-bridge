"""Ordered-check test linter (proposal C3, ruled BUILD after C2).

Mechanizes D-061: a test of an ordered sequence of checks must assert the
failing check's OWN detail string, not merely the shared reason code, so a
test that dies at an earlier check fails loudly instead of passing hollow.

    python tools/ordered_check_lint.py

The rule bites only where it must. A reason code raised at ONE point in
the source is unambiguous: asserting it is enough. A code raised at TWO OR
MORE points is ambiguous, and a test asserting only that code cannot know
which check it reached - that is the exact shape of the STEP-05 stop-one
finding, where a kill test died at an internal-consistency check while
claiming to exercise a comparison, and the mutation audit exposed it by
leaving the mutant alive under a green test.

WHAT A PASS DOES NOT PROVE:
  - It does not prove the detail assertions are the RIGHT ones. A test may
    assert a detail substring from the wrong check and still pass here.
  - It only sees reason codes named as string literals; a code assembled
    at runtime is invisible to it.
  - It says nothing about tests that assert no reason code at all.

EXIT CODES:
  0  every ambiguous-code assertion is accompanied by a detail assertion
  1  a test asserts a multiply-raised code with no detail assertion
  2  the lint could not run
"""

import ast
import os
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(os.environ.get("FB_LINT_REPO", Path(__file__).resolve().parent.parent))

EXIT_PASS = 0
EXIT_VIOLATION = 1
EXIT_COULD_NOT_RUN = 2

CODE_RE = re.compile(r'"([a-z][a-z0-9]*(?:-[a-z0-9]+)+)"')


def multiply_raised_codes(src_root: Path) -> set[str]:
    """Reason codes that appear as a raise/append site more than once."""
    counts: Counter[str] = Counter()
    for path in sorted(src_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(text)):
            # a literal code inside a raise, or inside a dict with a
            # "reason_code" key (the verify-failure shape)
            if isinstance(node, ast.Raise | ast.Dict):
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        if CODE_RE.fullmatch(f'"{sub.value}"'):
                            counts[sub.value] += 1
            if isinstance(node, ast.Name) and node.id.startswith("REASON_"):
                counts[node.id] += 1
    return {code for code, n in counts.items() if n >= 2}


def violations(tests_root: Path, ambiguous: set[str]) -> list[str]:
    found: list[str] = []
    for path in sorted(tests_root.rglob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        lines = text.splitlines()
        for func in ast.walk(tree):
            if not isinstance(func, ast.FunctionDef) or not func.name.startswith("test_"):
                continue
            body = "\n".join(lines[func.lineno - 1 : (func.end_lineno or func.lineno)])
            codes = {c for c in CODE_RE.findall(body) if c in ambiguous}
            if not codes:
                continue
            asserts_detail = "detail" in body
            if not asserts_detail:
                found.append(
                    f"{path.name}:{func.lineno} {func.name}(): asserts "
                    f"{sorted(codes)} which is raised at 2+ sites, without "
                    "asserting a detail string (D-061)"
                )
    return found


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print("ordered_check_lint takes no arguments; there is no override", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    src = REPO / "src"
    tests = REPO / "tests"
    if not src.is_dir() or not tests.is_dir():
        print(f"could-not-run: missing src/ or tests/ under {REPO}", file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    ambiguous = multiply_raised_codes(src)
    problems = violations(tests, ambiguous)
    if problems:
        print("ORDERED-CHECK LINT: VIOLATIONS")
        for problem in problems:
            print(f"  {problem}")
        return EXIT_VIOLATION
    print(f"ORDERED-CHECK LINT: CLEAN ({len(ambiguous)} ambiguous codes tracked)")
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
