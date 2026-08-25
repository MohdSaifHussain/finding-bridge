"""Controls for the census tools C1, C3, C5 (standard anatomy).

Each tool gets: a positive control (passes on real data), a negative
control (a planted violation is caught), an exit-code distinctness check,
a no-override check, and a docstring check that it states what a pass
does not prove.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"

SCAN = TOOLS / "fixture_scan.py"
LINT = TOOLS / "ordered_check_lint.py"
REGISTER = TOOLS / "equivalence_register.py"
ALL_TOOLS = [SCAN, LINT, REGISTER, TOOLS / "gate.py", TOOLS / "audit_guard.py"]


def run(tool: Path, args: list[str] | None = None, env: dict | None = None, cwd: Path = REPO):
    return subprocess.run(
        [sys.executable, str(tool), *(args or [])],
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, **(env or {})},
        check=False,
    )


# --- standard anatomy, asserted for EVERY tool ---


@pytest.mark.parametrize("tool", ALL_TOOLS, ids=lambda p: p.name)
def test_tool_states_what_a_pass_does_not_prove(tool: Path):
    import re

    source = re.sub(r"\s+", " ", tool.read_text(encoding="utf-8")).upper()
    assert "DOES NOT PROVE" in source or "WHOLE LESSON" in source, (
        f"{tool.name} must bound its own claim"
    )


@pytest.mark.parametrize("tool", ALL_TOOLS, ids=lambda p: p.name)
def test_tool_has_no_override_flag(tool: Path):
    source = tool.read_text(encoding="utf-8")
    for flag in ("--skip", "--no-verify", "--ignore-errors", "--allow-fail"):
        assert flag not in source


# --- C1: fixture harm scanner ---


def test_fixture_scan_passes_on_real_fixtures():
    result = run(SCAN)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "CONFORMING" in result.stdout
    assert "shape conformance only" in result.stdout, "it must not imply it certifies safety"


def test_fixture_scan_catches_unmarked_content(tmp_path: Path):
    """Negative control: a fixture with harm-bearing text and no sentinel."""
    fixtures = tmp_path / "schemas" / "fixtures"
    fixtures.mkdir(parents=True)
    (fixtures / "planted.jsonl").write_text(
        json.dumps({"output": {"text": "this text has no marker at all"}}) + "\n",
        encoding="utf-8",
    )
    result = run(SCAN, env={"FB_FIXTURE_REPO": str(tmp_path)})
    assert result.returncode == 1
    assert "NONCONFORMING" in result.stdout
    assert "no marker at all" not in result.stdout, "the refusal withholds the value (D-036)"


def test_fixture_scan_could_not_run_is_distinct(tmp_path: Path):
    result = run(SCAN, env={"FB_FIXTURE_REPO": str(tmp_path)})
    assert result.returncode == 2, "no fixtures is could-not-run, never a pass"


# --- C3: ordered-check linter ---


def test_ordered_check_lint_passes_on_this_repo():
    result = run(LINT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "CLEAN" in result.stdout


def test_ordered_check_lint_catches_a_bare_code_assertion(tmp_path: Path):
    """Negative control: a test asserting a multiply-raised code with no
    detail assertion - the exact shape of the stop-one hollow test."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "thing.py").write_text(
        'def a():\n    raise ValueError({"reason_code": "shared-code"})\n'
        'def b():\n    raise ValueError({"reason_code": "shared-code"})\n',
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_planted.py").write_text(
        'def test_planted():\n    assert err.reason_code == "shared-code"\n', encoding="utf-8"
    )
    result = run(LINT, env={"FB_LINT_REPO": str(tmp_path)}, cwd=tmp_path)
    assert result.returncode == 1, result.stdout
    assert "VIOLATIONS" in result.stdout
    assert "D-061" in result.stdout


# --- C5: equivalence register ---


def test_register_reports_every_survivor_dispositioned():
    dbs = [p.name for p in REPO.glob("cr-*-s5.sqlite")]
    if not dbs:
        pytest.skip("no close-audit databases present in this checkout")
    result = run(REGISTER, ["check", *dbs])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "none of them VERIFIED" in result.stdout, (
        "the tool must state that dispositioned is not verified"
    )


def test_register_header_denies_verification():
    data = json.loads((REPO / "evidence" / "equivalence-register.json").read_text(encoding="utf-8"))
    assert "not verification" in data["note"]
    assert data["claims"], "the register must not be empty while survivors exist"


def test_register_records_its_own_first_catch():
    """The register flagged a stale claim of mine on its first run; the
    correction is part of the file, not a memory."""
    data = json.loads((REPO / "evidence" / "equivalence-register.json").read_text(encoding="utf-8"))
    assert data.get("corrections"), "the first catch must be recorded"
    assert "FIRST run" in data["corrections"][0]["correction"]
