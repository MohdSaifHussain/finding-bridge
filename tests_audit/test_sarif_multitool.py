"""AUDIT-cadence: the Microsoft SARIF Multitool route (D5, DEV-5, DEV-7).

Runs at audit/close, not GATE: it shells out to npx (network fetch on first
use, multi-second startup), and the SARIF it validates changes only when
the adapter changes (D-032: a check belongs at the cadence of the thing it
guards). The npx invocation pins the package version per DEV-7; the pin is
recorded in the evidence. Both directions proven: the generated SARIF must
pass, and a corrupted file must be rejected.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from finding_bridge import pipeline
from finding_bridge.adapters.out import sarif

MULTITOOL_PIN = "@microsoft/sarif-multitool@5.6.0"  # resolved 2026-08-24, DEV-7

REPO = Path(__file__).resolve().parent.parent
HITLOG = REPO / "schemas" / "fixtures" / "garak.synthetic.hitlog.jsonl"
IDENTITY = "Audit Analyst <audit@example.invalid>"

npx = shutil.which("npx")
pytestmark = pytest.mark.skipif(
    npx is None, reason="npx unavailable; Multitool route must be reported, not skipped silently"
)


def run_multitool(sarif_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [npx, "--yes", MULTITOOL_PIN, "validate", str(sarif_path)],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )


@pytest.fixture(scope="module")
def emitted(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("mt")
    repo = root / "repo"
    repo.mkdir()
    ws = pipeline.Workspace(repo / ".fb-store", root / "k" / "fb.key", repo)
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], IDENTITY)
    findings = ws.confirmed_findings()
    out = root / "findings.sarif"
    (root / "findings.fb.jsonl").write_text(
        sarif.render_findings_artifact(findings), encoding="utf-8"
    )
    out.write_text(
        json.dumps(sarif.render_sarif(findings, "findings.fb.jsonl"), indent=2) + "\n",
        encoding="utf-8",
    )
    return out


def test_multitool_accepts_our_sarif(emitted: Path):
    result = run_multitool(emitted)
    combined = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Analysis completed successfully" in combined
    assert "error " not in combined, f"Multitool flagged errors:\n{combined[-1500:]}"


def test_multitool_flags_corrupted_input(tmp_path: Path):
    """DEV-5: a validator only ever seen saying yes is not yet a validator.

    Measured limit (recorded in the evidence): Multitool 5.6.0 via npm
    exits 0 even for input it itself reports as a JSON syntax error, and
    silently accepts a version-less SARIF. Its reliable failure signal on
    this machine is the console `error JSON0001` line, so this control
    asserts on that, not on the exit code."""
    bad = tmp_path / "garbage.sarif"
    bad.write_text("{not json", encoding="utf-8")
    result = run_multitool(bad)
    combined = result.stdout + result.stderr
    assert "error JSON0001" in combined, f"Multitool did not flag garbage input:\n{combined[-800:]}"
