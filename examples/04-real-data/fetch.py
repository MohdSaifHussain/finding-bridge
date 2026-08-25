"""Fetch the real datasets for example 04 to a folder OUTSIDE the repository.

    python examples/04-real-data/fetch.py            # download + verify checksum + prepare
    python examples/04-real-data/fetch.py --verify   # checksum only, no network

D-012 IS ABSOLUTE: no real harmful content is ever committed to this
repository. This script is the FLARE-PDF pattern from Phase 0 (D-006):
the tree carries the source URL and the checksum; the bytes live at
DATA_DIR, which is outside the tree and is never read by anything that
commits. Nothing this script writes is under the repo root, and it
refuses to run if DATA_DIR resolves inside it.

SOURCE 1 (published adversarial dataset, transcript path):
  Anthropic/hh-rlhf, file red-team-attempts/red_team_attempts.jsonl.gz
  https://huggingface.co/datasets/Anthropic/hh-rlhf  (MIT license per the
  dataset card; fetched 2026-08-25). 38,961 human-vs-model red-team
  transcripts (JSON array; keys: transcript, min_harmlessness_score_transcript,
  num_params, model_type, rating, task_description, ...). Chosen because it
  is the only candidate that carries REAL MODEL RESPONSES beside the attack
  turns, which is what the transcript adapter seals. Alternatives evaluated
  the same day: TrustAIRLab/in-the-wild-jailbreak-prompts (MIT; jailbreak
  prompts only, no responses) and JailbreakBench/JBB-Behaviors (MIT;
  behaviour goals only, no responses). Both are prompt corpora; neither
  exercises the response seal.

PREPARE: the dataset writes turns as "\\n\\nHuman:" / "\\n\\nAssistant:". The
transcript adapter's grammar is exact uppercase USER:/ASSISTANT: at line
start (D-041, D-049). This script rewrites the markers of a SAMPLE of
transcripts into that grammar, one file per transcript, under DATA_DIR/
prepared/. The rewrite is the only transformation; the text between
markers is untouched. That the real-world marker form is refused by the
grammar as shipped is raised as finding F-10 (evidence/step06-findings.md),
not hidden in this script.

SOURCE 2 (the real garak run) is produced by examples/04-real-data/run_garak.py
into DATA_DIR/garak/, never fetched.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = Path(
    os.environ.get("FB_REALDATA_DIR")
    or Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "finding-bridge-realdata"
)
URL = (
    "https://huggingface.co/datasets/Anthropic/hh-rlhf/resolve/main/"
    "red-team-attempts/red_team_attempts.jsonl.gz"
)
FILENAME = "red_team_attempts.jsonl.gz"
SHA256 = "4c7b0069991460f0064f279fd400b51f3f0095697d14d7793c49b0925f80814f"
EXPECTED_BYTES = 15_483_307
SAMPLE = 40  # transcripts prepared for ingestion (time-box: a triage-sized batch)
SEED = 20260825  # fixed, so the sample is reproducible from the same file


def guard_outside_tree() -> None:
    if DATA_DIR.resolve() == REPO or REPO in DATA_DIR.resolve().parents:
        print(f"refusing: DATA_DIR {DATA_DIR} is inside the repository (D-012)", file=sys.stderr)
        raise SystemExit(2)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    target = DATA_DIR / FILENAME
    if not target.exists():
        print(f"downloading {URL}")
        req = urllib.request.Request(URL, headers={"User-Agent": "finding-bridge-example-04"})
        with urllib.request.urlopen(req, timeout=300) as r, target.open("wb") as out:
            for chunk in iter(lambda: r.read(1 << 20), b""):
                out.write(chunk)
    return target


def verify(target: Path) -> None:
    size = target.stat().st_size
    got = digest(target)
    if size != EXPECTED_BYTES or got != SHA256:
        print(
            f"CHECKSUM MISMATCH: size {size} (expected {EXPECTED_BYTES}), sha256 {got}"
            f" (expected {SHA256}); the file is not the one this example was built on",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"verified: {target} sha256={got} bytes={size}")


def prepare(target: Path) -> Path:
    """Rewrite a fixed sample of transcripts into the adapter's marker grammar."""
    out_dir = DATA_DIR / "prepared"
    out_dir.mkdir(exist_ok=True)
    with gzip.open(target, "rt", encoding="utf-8") as f:
        data = json.load(f)
    rng = random.Random(SEED)
    picks = sorted(rng.sample(range(len(data)), SAMPLE))
    written = 0
    for i in picks:
        text = data[i]["transcript"].strip()
        text = text.replace("\n\nHuman:", "\nUSER:").replace("\n\nAssistant:", "\nASSISTANT:")
        if text.startswith("Human:"):
            text = "USER:" + text[len("Human:") :]
        (out_dir / f"rt-{i:05d}.txt").write_text(text.lstrip("\n") + "\n", encoding="utf-8")
        written += 1
    print(f"prepared {written} transcripts under {out_dir} (indices seeded by {SEED})")
    return out_dir


def main(argv: list[str]) -> int:
    guard_outside_tree()
    if argv[1:] == ["--verify"]:
        target = DATA_DIR / FILENAME
        if not target.exists():
            print(f"not fetched yet: {target}", file=sys.stderr)
            return 2
        verify(target)
        return 0
    if argv[1:]:
        print("usage: fetch.py [--verify]", file=sys.stderr)
        return 2
    target = fetch()
    verify(target)
    prepare(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
