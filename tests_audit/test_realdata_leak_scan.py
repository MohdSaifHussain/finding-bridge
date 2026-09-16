"""D-099: the real-string leak scan reads the data of the example it scans.

Found on 2026-09-16: a bare `python tools/realdata_leak_scan.py
examples/05-real-data-garak-0.17.0/output` read example 04's data (4,784
real texts, not 05's 4,567) and still printed CLEAN, a pass that meant
nothing. These controls pin the fix. AUDIT cadence (D-027): the one that
reads real data skips when the local data is absent (D-012).
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "realdata_leak_scan.py"
E04, E05 = "04-real-data", "05-real-data-garak-0.17.0"
LOCAL = Path(os.environ.get("LOCALAPPDATA") or Path.home())
D04 = Path(os.environ.get("FB_REALDATA_DIR") or LOCAL / "finding-bridge-realdata")
D05 = Path(os.environ.get("FB_REALDATA_DIR_05") or LOCAL / "finding-bridge-realdata-garak-0.17.0")


def _clean_env(**extra: str) -> dict:
    env = {
        k: v for k, v in os.environ.items() if k not in ("FB_REALDATA_DIR", "FB_REALDATA_DIR_05")
    }
    env.update(extra)
    return env


def _scan(output: Path, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), str(output)], capture_output=True, text=True, env=env
    )


def _texts(proc: subprocess.CompletedProcess):
    m = re.search(r"from (\d+) real texts", proc.stdout)
    return int(m.group(1)) if m else None


def _has_data(d: Path) -> bool:
    return (d / "garak" / "fb-real.hitlog.jsonl").exists()


def test_bare_scan_of_example_05_reads_example_05s_data():
    if not (_has_data(D04) and _has_data(D05)):
        pytest.skip("needs the local real data of examples 04 and 05 (never committed, D-012)")
    out = REPO / "examples" / E05 / "output"
    bare = _scan(out, _clean_env())
    explicit = _scan(out, _clean_env(FB_REALDATA_DIR=str(D05), FB_REALDATA_DIR_05=str(D05)))
    assert _texts(explicit) is not None, explicit.stdout + explicit.stderr
    assert _texts(bare) == _texts(explicit), (
        "a bare scan of example 05's output did not read example 05's data"
    )


def test_scan_refuses_an_output_folder_it_cannot_place(tmp_path: Path):
    out = tmp_path / "some-other-example" / "output"
    out.mkdir(parents=True)
    (out / "packet.md").write_text("nothing here", encoding="utf-8")
    proc = _scan(out, _clean_env())
    assert proc.returncode == 2, (
        "the scan checked an output it cannot place against some default data"
    )
    assert "which real data" in proc.stderr, proc.stdout + proc.stderr


def test_each_example_resolves_to_its_own_folder_even_in_a_check_copy(tmp_path: Path):
    sys.path.insert(0, str(TOOL.parent))
    import realdata_leak_scan as scan

    assert scan.REAL_DATA_DIRS[E04] != scan.REAL_DATA_DIRS[E05]
    for example in (E04, E05):
        committed = REPO / "examples" / example / "output"
        check_copy = tmp_path / "fb-check-x" / example / "output"
        assert scan.data_dir_for(committed) == scan.REAL_DATA_DIRS[example]
        assert scan.data_dir_for(check_copy) == scan.REAL_DATA_DIRS[example]
