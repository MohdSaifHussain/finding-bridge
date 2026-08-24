"""D-029 ruling 2: the audit's test command must collect exactly what the
gate suite collects. Closes the gate-half-run CLASS (run 2 of the first
audit ran without its ammunition because an enumerated command predated a
new test file), not just the instance."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
AUDIT_CONFIGS = sorted(REPO.glob("cr-*.toml"))


def collected_count(pytest_args: list[str]) -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *pytest_args],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    match = re.search(r"(\d+) tests? collected", result.stdout)
    assert match, f"could not parse collection output:\n{result.stdout[-500:]}"
    return int(match.group(1))


def audit_test_args(config: Path) -> list[str]:
    text = config.read_text(encoding="utf-8")
    match = re.search(r'test-command\s*=\s*"([^"]+)"', text)
    assert match, f"{config.name} has no test-command"
    command = match.group(1)
    args = command.split()
    assert args[:3] == ["python", "-m", "pytest"], f"unexpected test-command in {config.name}"
    kept: list[str] = []
    skip_next = False
    for token in args[3:]:
        if skip_next:
            skip_next = False
            continue
        if token == "-p":
            skip_next = True  # drop the flag AND its value (e.g. no:cacheprovider)
            continue
        if token in ("-x", "-q"):
            continue
        kept.append(token)
    return kept


def test_audit_configs_exist():
    assert AUDIT_CONFIGS, "no cr-*.toml audit configs found"


@pytest.mark.parametrize("config", AUDIT_CONFIGS, ids=lambda p: p.name)
def test_audit_command_collects_the_whole_gate_suite(config: Path):
    gate = collected_count(["tests"])
    audit = collected_count(audit_test_args(config))
    assert audit == gate, (
        f"{config.name} collects {audit} tests; the gate suite collects {gate}. "
        "An audit running fewer tests than the gate is a gate half-run."
    )


def test_guard_detects_a_shortfall():
    """Negative control: the comparison can fail; a subset collects fewer."""
    gate = collected_count(["tests"])
    subset = collected_count(["tests/test_schema.py"])
    assert subset < gate
