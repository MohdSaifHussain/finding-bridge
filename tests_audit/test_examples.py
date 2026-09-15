"""STEP-06 W3: the showcased-equals-current check, and its controls.

AUDIT cadence (D-027, D-032): each example re-runs the CLI end to end
through subprocesses, which is per-phase weight, not per-commit. The CI
gate runs it as its own named step.

What a pass proves is stated in examples/run_example.py's docstring: the
committed artifacts equal a fresh run in every field that does not derive
from the store key, the clock or the operator. Not byte identity.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
DRIVER = REPO / "examples" / "run_example.py"
SCAN = REPO / "tools" / "fixture_scan.py"

sys.path.insert(0, str(DRIVER.parent))
import run_example  # noqa: E402

# D-097: each real-data example reads its OWN local data folder. If two
# shared one, a leak scan could check one example's artifacts against the
# other's data and still print CLEAN, which would mean nothing.
REAL_DATA_EXAMPLES = ("04-real-data", "05-real-data-garak-0.17.0")


def _real_data_dir(example: str):
    return getattr(run_example, "REAL_DATA_DIRS", {}).get(example)


@pytest.mark.parametrize("example", sorted(run_example.EXAMPLES))
def test_committed_example_output_matches_a_fresh_run(example):
    data = _real_data_dir(example)
    if data is not None and not (data / "garak" / "fb-real.hitlog.jsonl").exists():
        # W6c: the real data is never committed (D-012). Without a local
        # copy the re-run cannot happen; this is a stated skip in the AUDIT
        # cadence, not in the gate, and the gate's single-skip deliverable
        # (W5) is unaffected.
        pytest.skip(f"no local real data under {data}; see examples/{example}/README.md")
    proc = subprocess.run(
        [sys.executable, str(DRIVER), example, "--check"], capture_output=True, text=True
    )
    assert proc.returncode == run_example.EXIT_OK, proc.stdout + proc.stderr
    assert "SHOWCASE CHECK: SAME" in proc.stdout


def test_each_real_data_example_has_its_own_data_folder():
    dirs = [_real_data_dir(e) for e in REAL_DATA_EXAMPLES]
    assert all(dirs), "a real-data example has no data folder of its own"
    assert len(set(dirs)) == len(dirs), "two real-data examples share a data folder"


@pytest.mark.parametrize("example", REAL_DATA_EXAMPLES)
def test_leak_scan_step_reads_the_examples_own_folder(example, monkeypatch, tmp_path: Path):
    """The runner's leak-scan step must hand the scan THIS example's data
    folder. Intercepted, so no real data is needed."""
    captured = {}

    def fake_run(argv, **kwargs):
        captured["env"] = kwargs.get("env")
        return subprocess.CompletedProcess(argv, 0, "REAL-STRING SCAN: CLEAN", "")

    monkeypatch.setattr(run_example.subprocess, "run", fake_run)
    run = run_example.Run(example, tmp_path, tmp_path / "out")
    try:
        run.leak_scan()
    finally:
        run.cleanup()
    env = captured.get("env") or {}
    assert env.get("FB_REALDATA_DIR") == str(_real_data_dir(example)), (
        "the leak scan was not told which data folder to read"
    )


def test_check_refuses_a_planted_difference(tmp_path: Path):
    """Negative control: one changed non-volatile byte must be reported."""
    committed = REPO / "examples" / "01-garak-triage" / "output"
    fresh = tmp_path / "fresh"
    shutil.copytree(committed, fresh)
    packet = fresh / "packet.md"
    packet.write_text(
        packet.read_text(encoding="utf-8").replace("Source tool: garak", "Source tool: gara_"),
        encoding="utf-8",
    )
    assert run_example.compare(committed, fresh, "01-garak-triage") == run_example.EXIT_DIFF


def test_check_ignores_only_the_named_volatile_fields(tmp_path: Path):
    """Positive control for the normaliser: a fresh id, hash and timestamp
    normalise to the same token; an unrelated change does not."""
    a = run_example.normalise("fb-0123456789abcdef at 2026-08-25T06:00:00+00:00")
    b = run_example.normalise("fb-fedcba9876543210 at 2026-08-26T07:11:22+00:00")
    assert a == b
    assert run_example.normalise("x") != run_example.normalise("y")


def test_fixture_scan_catches_a_leaked_sentinel_in_an_output_artifact(tmp_path: Path):
    """Negative control for the leak direction: a sealed-content sentinel in
    an emitted artifact must fail the scan, and one outside an explicit
    unseal in the transcript must fail too."""
    sys.path.insert(0, str(SCAN.parent))
    import fixture_scan

    art = tmp_path / "packet.md"
    art.write_text("preview ok\nSENTINEL-HARM-LEAK should not be here\n", encoding="utf-8")
    assert any("LEAK" in p for p in fixture_scan.scan_output_artifact(art))
    tr = tmp_path / "run-transcript.md"
    tr.write_text(
        "$ finding-bridge unseal sealed/x --explicit\nSENTINEL-HARM-OK\n"
        "$ finding-bridge list\nSENTINEL-HARM-LEAK\n",
        encoding="utf-8",
    )
    problems = fixture_scan.scan_output_artifact(tr)
    assert len(problems) == 1 and ":4:" in problems[0]
