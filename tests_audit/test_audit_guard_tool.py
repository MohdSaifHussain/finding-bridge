"""D-067 controls: the guard refuses dirty trees AND concurrent runs.

Tested against a TEMP git repo, not this one: an earlier version asserted
against the live repo and failed the moment the repo was dirty - which it
always is mid-change. A guard test that only passes on a clean repo tests
the repo, not the guard.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / "tools" / "audit_guard.py"


@pytest.fixture()
def sandbox(tmp_path: Path):
    """A tiny git repo with a committed src/ file, so the guard has
    something real to look at."""
    (tmp_path / "src").mkdir()
    victim = tmp_path / "src" / "thing.py"
    victim.write_text("VALUE = 1\n", encoding="utf-8")
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "t@example.invalid"],
        ["git", "config", "user.name", "T"],
        ["git", "add", "-A"],
        ["git", "commit", "-qm", "seed"],
    ):
        subprocess.run(cmd, cwd=tmp_path, check=True, capture_output=True)
    return tmp_path, victim


def run(action: str, repo: Path):
    env = {**os.environ, "FB_AUDIT_REPO": str(repo)}
    return subprocess.run(
        [sys.executable, str(GUARD), action],
        capture_output=True,
        text=True,
        cwd=repo,
        env=env,
        check=False,
    )


def test_acquire_then_release_on_a_clean_tree(sandbox):
    repo, _ = sandbox
    acquired = run("acquire", repo)
    assert acquired.returncode == 0, acquired.stderr
    assert (repo / ".audit-lock").exists()
    released = run("release", repo)
    assert released.returncode == 0, released.stderr
    assert not (repo / ".audit-lock").exists()


def test_second_acquire_is_refused_while_the_first_holds(sandbox):
    """The concurrency lock (D-067's binding condition): the exact failure
    that corrupted a measurement - two instruments on one tree."""
    repo, _ = sandbox
    assert run("acquire", repo).returncode == 0
    second = run("acquire", repo)
    assert second.returncode == 1
    assert "audit-in-progress" in second.stderr
    assert "Racing instruments corrupt measurements" in second.stderr


def test_acquire_refuses_a_dirty_tree(sandbox):
    repo, victim = sandbox
    victim.write_text("VALUE = 2  # uncommitted\n", encoding="utf-8")
    result = run("acquire", repo)
    assert result.returncode == 1
    assert "audit-tree-dirty" in result.stderr


def test_release_reports_a_leftover_mutant_and_says_discard(sandbox):
    """The exit side: a run that leaves a mutant applied must be told its
    figures are void."""
    repo, victim = sandbox
    assert run("acquire", repo).returncode == 0
    victim.write_text("VALUE = 999  # simulated leftover mutant\n", encoding="utf-8")
    result = run("release", repo)
    assert result.returncode == 1
    assert "audit-tree-dirty" in result.stderr
    assert "DISCARD" in result.stderr


def test_guard_re_derives_from_git_rather_than_a_cached_echo():
    """The lesson, asserted in the tool itself (D-067).

    Whitespace is normalized before matching: the sentence is line-wrapped
    in the docstring, and an unnormalized version of this test failed on
    the wrap - the same class as D-046's required-phrase check. Wrapping
    is formatting, not meaning."""
    import re

    source = re.sub(r"\s+", " ", GUARD.read_text(encoding="utf-8"))
    assert "git" in source and "porcelain" in source
    assert "SINGLE WITNESS restating a cached check" in source
