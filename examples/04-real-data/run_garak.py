"""Produce the real garak hitlog for example 04, OUTSIDE the repository.

    python examples/04-real-data/run_garak.py            # run garak against local Ollama
    python examples/04-real-data/run_garak.py --status   # show what a previous run left

The command this script runs, exactly as it ran on 2026-08-25 (garak
0.16.0 in its own venv; garak's CLI reference fetched from
https://raw.githubusercontent.com/NVIDIA/garak/v0.16.0/garak/cli.py and the
Ollama generator from .../garak/generators/ollama.py the same day: host
127.0.0.1:11434 by default, 30 s timeout; `--probes` is deprecated since
0.15.1 in favour of `--spec`):

    python -m garak --target_type ollama --target_name llama3.2:1b \\
        --spec probes.dan,probes.promptinject --generations 1 \\
        --report_prefix <DATA_DIR>/garak/fb-real

Target: llama3.2:1b on Ollama 0.32.15, verified first with `ollama list`
and a one-prompt smoke call (`/api/generate`, reply "OK"). Probe families:
dan and promptinject; garak's default-active members of each ran
(Ablation_Dan_11_0, AutoDANCached, DanInTheWild, HijackHateHumans,
HijackKillHumans, HijackLongPrompt). Time box: 45 minutes wall clock,
enforced with `timeout 2700`; a cut run still leaves a valid hitlog,
because garak appends one line per detector hit as it goes.

D-012: the hitlog is REAL model output produced by a jailbreak probe set
against a weak model. It lives at DATA_DIR/garak/ and is never committed.
example 04 commits only what the product emits about it.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = Path(
    os.environ.get("FB_REALDATA_DIR")
    or Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "finding-bridge-realdata"
)
GARAK_DIR = DATA_DIR / "garak"
GARAK_PY = os.environ.get("FB_GARAK_PYTHON") or shutil.which("python")
TIME_BOX_S = 2700
CMD = [
    "-m",
    "garak",
    "--target_type",
    "ollama",
    "--target_name",
    "llama3.2:1b",
    "--spec",
    "probes.dan,probes.promptinject",
    "--generations",
    "1",
    "--report_prefix",
    str(GARAK_DIR / "fb-real"),
]


def status() -> int:
    hitlog = GARAK_DIR / "fb-real.hitlog.jsonl"
    if not hitlog.exists():
        print(f"no hitlog at {hitlog}")
        return 2
    lines = hitlog.read_text(encoding="utf-8").count("\n")
    print(f"{hitlog}: {lines} hit lines, {hitlog.stat().st_size} bytes")
    for name in ("started.txt", "ended.txt"):
        p = GARAK_DIR / name
        if p.exists():
            print(f"{name}: {p.read_text(encoding='utf-8').strip()}")
    return 0


def main(argv: list[str]) -> int:
    if REPO in DATA_DIR.resolve().parents or DATA_DIR.resolve() == REPO:
        print("refusing: DATA_DIR inside the repository (D-012)", file=sys.stderr)
        return 2
    if argv[1:] == ["--status"]:
        return status()
    GARAK_DIR.mkdir(parents=True, exist_ok=True)
    print("running:", GARAK_PY, " ".join(CMD), f"(time box {TIME_BOX_S}s)")
    try:
        proc = subprocess.run([GARAK_PY, *CMD], cwd=GARAK_DIR, timeout=TIME_BOX_S)
        print("garak exit", proc.returncode)
    except subprocess.TimeoutExpired:
        print("time box reached; the hitlog written so far stands")
    return status()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
