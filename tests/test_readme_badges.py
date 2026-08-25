"""STEP-06 W1, contract 3.2: every badge is a checked fact.

Each README badge states one fact. This test re-derives each fact from
its source of truth (pyproject, the adapters' SCHEMA_VERSION, the SARIF
schema file, the environment scrub) and fails when the badge and the
source disagree. A workflow badge (build, container) may exist only when
its workflow file exists; observing it green is the director's ritual
and cannot be asserted statically, which this docstring states as the
limit.

The check proves it can fail: test_badge_check_detects_a_stale_badge
plants a wrong schema version and asserts refusal.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"
BADGE_RE = re.compile(r"!\[[^\]]*\]\((https://img\.shields\.io/badge/[^)]+)\)")


def _badges(text: str) -> list[str]:
    return BADGE_RE.findall(text)


def _facts() -> dict:
    py = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    from finding_bridge.adapters.in_ import garak, transcript

    assert garak.SCHEMA_VERSION == transcript.SCHEMA_VERSION
    return {
        "license": py["project"]["license"],
        "python": py["project"]["requires-python"],
        "schema": garak.SCHEMA_VERSION,
    }


def _check(text: str) -> list[str]:
    """Return a list of badge/fact disagreements (empty means all true)."""
    facts = _facts()
    problems = []
    badges = _badges(text)
    if not badges:
        return ["no badges found"]
    for url in badges:
        label = url.split("/badge/", 1)[1]
        if label.startswith("license-"):
            expected = facts["license"].replace("-", "--")
            if f"license-{expected}-" not in label:
                problems.append(f"license badge says {label}, pyproject says {facts['license']}")
        elif label.startswith("python-"):
            floor = facts["python"].lstrip(">=")
            if f"python-{floor}%2B-" not in label:
                problems.append(f"python badge says {label}, pyproject says {facts['python']}")
        elif label.startswith("canonical%20schema-"):
            if f"canonical%20schema-{facts['schema']}-" not in label:
                problems.append(f"schema badge says {label}, code says {facts['schema']}")
        elif label.startswith("emits-SARIF"):
            if not (REPO / "schemas" / "sarif-schema-2.1.0.json").exists():
                problems.append("SARIF badge without the 2.1.0 schema file")
        elif label.startswith("tests-"):
            # the number is the collected count, re-derived from pytest itself
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q", str(REPO / "tests")],
                capture_output=True,
                text=True,
                cwd=REPO,
            )
            m = re.search(r"(\d+) tests? collected", proc.stdout)
            assert m, proc.stdout[-300:]
            if f"tests-{m.group(1)}%20collected-" not in label:
                problems.append(f"tests badge says {label}, pytest collects {m.group(1)}")
        elif label.startswith("garak%20fixtures-"):
            pin = re.search(
                r"Pinned garak version:\s*(\d+\.\d+\.\d+)",
                (REPO / "docs" / "FIXTURE-VERSIONS.md").read_text(encoding="utf-8"),
            )
            assert pin, "docs/FIXTURE-VERSIONS.md has no pinned garak version line"
            if f"garak%20fixtures-{pin.group(1)}-" not in label:
                problems.append(f"garak badge says {label}, FIXTURE-VERSIONS pins {pin.group(1)}")
        elif label.startswith("AI%20in%20the%20evidence%20path-none"):
            if not (REPO / "tests" / "test_environment.py").exists():
                problems.append("no-AI badge without the environment scrub test")
        else:
            problems.append(f"unrecognised badge, no fact check written for it: {label}")
    for m in re.finditer(r"actions/workflows/([\w.-]+)", text):
        if not (REPO / ".github" / "workflows" / m.group(1)).exists():
            problems.append(f"workflow badge for a workflow that does not exist: {m.group(1)}")
    return problems


def test_every_readme_badge_is_a_checked_fact():
    assert _check(README.read_text(encoding="utf-8")) == []


def test_badge_check_detects_a_stale_badge():
    """Negative control: a wrong schema version must be refused."""
    text = README.read_text(encoding="utf-8").replace(
        "canonical%20schema-0.5.0", "canonical%20schema-9.9.9"
    )
    assert any("schema badge" in p for p in _check(text))


def test_badge_check_detects_a_workflow_badge_without_a_workflow():
    """Negative control for 3.2's build-badge rule."""
    text = (
        README.read_text(encoding="utf-8")
        + "\n![x](https://github.com/o/r/actions/workflows/nope.yml/badge.svg)\n"
    )
    assert any("nope.yml" in p for p in _check(text))
