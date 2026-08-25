"""C2 controls: the gate catches what a masked exit code hid.

The headline control plants the EXACT live specimen - a failing command
behind a pipe to `tail` - and proves the shell would have reported success
while the gate reports failure.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "tools" / "gate.py"


def run_gate(repo: Path, extra_env: dict | None = None):
    env = {**os.environ, "FB_GATE_REPO": str(repo), **(extra_env or {})}
    return subprocess.run(
        [sys.executable, str(GATE)], capture_output=True, text=True, env=env, check=False
    )


# --- the live specimen: a pipe to tail masks a failure, the gate does not ---


def test_a_pipe_to_tail_masks_a_failure_the_gate_would_catch():
    """THE control this tool exists for. `false | tail -1` exits 0 because
    a pipeline exits with its LAST command's status. Six commits in this
    project's history carried claims a failed check had already refuted,
    all through this construct or its newline twin."""
    masked = subprocess.run(
        f'"{sys.executable}" -c "import sys; sys.exit(1)" | tail -1',
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    assert masked.returncode == 0, "the mask itself must be demonstrated, not assumed"

    unmasked = subprocess.run(
        [sys.executable, "-c", "import sys; sys.exit(1)"], capture_output=True, check=False
    )
    assert unmasked.returncode == 1, "read directly, the same failure is visible"


def test_gate_passes_on_this_repo():
    """Positive control: the real repo, real constituents."""
    result = run_gate(REPO)
    assert "GATE: PASS" in result.stdout, result.stdout + result.stderr
    assert result.returncode == 0


def test_gate_fails_when_a_constituent_fails(tmp_path: Path):
    """Negative control: a repo whose tests fail must produce FAIL and
    exit 1, naming the constituent."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_planted.py").write_text(
        "def test_planted_failure():\n    assert False, 'planted'\n", encoding="utf-8"
    )
    result = run_gate(tmp_path)
    assert result.returncode == 1, result.stdout
    assert "GATE: FAIL" in result.stdout
    assert "pytest" in result.stdout


def test_could_not_run_is_distinct_from_failed(tmp_path: Path):
    """A constituent that cannot start is NOT a pass and NOT a failure:
    it has its own exit code, because 'nothing ran' read as 'nothing was
    wrong' is how a gate becomes decorative."""
    result = subprocess.run(
        [sys.executable, str(GATE), "--force"],
        capture_output=True,
        text=True,
        env={**os.environ, "FB_GATE_REPO": str(tmp_path)},
        check=False,
    )
    assert result.returncode == 2, "an unknown argument is could-not-run, not pass"
    assert "no override" in result.stderr


def test_gate_has_no_override_flag():
    """Ruled: a gate you can skip is a gate you will skip on the day it
    matters."""
    source = GATE.read_text(encoding="utf-8")
    for flag in ("--skip", "--force", "--no-verify", "--ignore"):
        assert f'"{flag}"' not in source and f"'{flag}'" not in source


def test_gate_states_what_a_pass_does_not_prove():
    """Standard anatomy: the docstring must bound its own claim."""
    import re

    source = re.sub(r"\s+", " ", GATE.read_text(encoding="utf-8"))
    assert "WHAT A PASS DOES NOT PROVE" in source
    assert "does not prove the tests are correct" in source


@pytest.mark.parametrize("name", ["pytest", "ruff-check", "ruff-format"])
def test_every_constituent_is_named_in_output(name: str):
    result = run_gate(REPO)
    assert name in result.stdout
