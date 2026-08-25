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
Since D-080 (finding F-10) the transcript adapter reads that grammar
directly when the operator names it (`--grammar human-assistant`), so this
script writes a SAMPLE of transcripts UNCHANGED, one file per transcript,
under DATA_DIR/prepared/, with a .meta.json sidecar of the record's facts
(rating, model_type, num_params, min_harmlessness_score_transcript) that
the example passes through `--environment` (D-081). Before D-080 this
script rewrote the markers; that rewrite is gone.

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
        rec = data[i]
        # D-080: the adapter now reads this grammar directly (--grammar
        # human-assistant); the text is written UNCHANGED except for leading
        # blank lines. The per-record facts go beside it as a sidecar the
        # example passes through --environment (D-081); task_description is
        # text-bearing and is not a fact, so it stays out.
        text = rec["transcript"].lstrip("\n")
        (out_dir / f"rt-{i:05d}.txt").write_text(text.rstrip("\n") + "\n", encoding="utf-8")
        facts = {
            k: rec[k]
            for k in ("rating", "model_type", "num_params", "min_harmlessness_score_transcript")
            if rec.get(k) is not None
        }
        (out_dir / f"rt-{i:05d}.meta.json").write_text(json.dumps(facts), encoding="utf-8")
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
