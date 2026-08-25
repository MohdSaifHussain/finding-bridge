"""Real-string leak scan for example 04 (STEP-06 W6c, the stronger control).

    python tools/realdata_leak_scan.py            # scan example 04's output against real strings
    python tools/realdata_leak_scan.py --selftest # a planted real string MUST be found

fixture_scan.py proves committed artifacts carry no SENTINEL string. That
proves the seal held against sentinels. This tool proves it held against
REAL content: at run time it reads the local real datasets (the garak
hitlog and the prepared transcripts under DATA_DIR, never committed),
samples distinct substrings of the prompts and responses, and searches
every committed artifact of example 04 for any of them. The sampled
strings are never written anywhere; only counts are printed (D-036,
D-012).

Sampling: every prompt and response text is split into windows of
WINDOW characters at stride STRIDE; windows shorter than MIN_LEN or
consisting of whitespace are dropped; up to MAX_SAMPLES distinct windows
are kept, chosen with a fixed seed. Both the whole-text and the windows
are searched for, so a verbatim copy of any real text of MIN_LEN+ chars
in an artifact is caught.

WHAT A PASS DOES NOT PROVE: that no transformed form of the content
leaked (a paraphrase, a hash, a re-encoding). It proves no verbatim
window of the sampled real text appears in any committed artifact.

EXIT CODES: 0 clean; 1 a real string was found in a committed artifact;
2 could not run (no local data, no artifacts).
"""

from __future__ import annotations

import gzip
import json
import os
import random
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_DIR = Path(
    os.environ.get("FB_REALDATA_DIR")
    or Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "finding-bridge-realdata"
)
OUTPUT = REPO / "examples" / "04-real-data" / "output"
WINDOW, STRIDE, MIN_LEN, MAX_SAMPLES, SEED = 48, 24, 24, 5000, 20260825
EXIT_CLEAN, EXIT_LEAK, EXIT_COULD_NOT_RUN = 0, 1, 2


def _texts_from_hitlog(path: Path) -> list[str]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        for key in ("prompt", "output", "goal"):
            node = rec.get(key)
            stack = [node]
            while stack:
                n = stack.pop()
                if isinstance(n, str) and n.strip():
                    out.append(n)
                elif isinstance(n, dict):
                    stack.extend(n.values())
                elif isinstance(n, list):
                    stack.extend(n)
        trig = rec.get("triggers")
        if isinstance(trig, list):
            out.extend(t for t in trig if isinstance(t, str) and t.strip())
    return out


def real_texts() -> list[str]:
    texts: list[str] = []
    hitlog = DATA_DIR / "garak" / "fb-real.hitlog.jsonl"
    if hitlog.exists():
        texts += _texts_from_hitlog(hitlog)
    prepared = DATA_DIR / "prepared"
    if prepared.is_dir():
        for p in sorted(prepared.glob("*.txt")):
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                body = line.split(":", 1)[1] if line[:10].isupper() and ":" in line[:12] else line
                if body.strip():
                    texts.append(body.strip())
    raw = DATA_DIR / "red_team_attempts.jsonl.gz"
    if raw.exists() and not texts:
        with gzip.open(raw, "rt", encoding="utf-8") as f:
            data = json.load(f)
        texts += [r["transcript"] for r in data[:500]]
    return texts


def samples(texts: list[str]) -> set[str]:
    rng = random.Random(SEED)
    pool: set[str] = set()
    for t in texts:
        t = " ".join(t.split())
        if len(t) >= MIN_LEN:
            pool.add(t)
        for i in range(0, max(1, len(t) - WINDOW + 1), STRIDE):
            w = t[i : i + WINDOW]
            if len(w) >= MIN_LEN and w.strip():
                pool.add(w)
    if len(pool) > MAX_SAMPLES:
        pool = set(rng.sample(sorted(pool), MAX_SAMPLES))
    return pool


def scan(artifacts: list[Path], needles: set[str]) -> list[str]:
    hits = []
    for art in artifacts:
        text = " ".join(art.read_text(encoding="utf-8", errors="replace").split())
        n = sum(1 for s in needles if s in text)
        if n:
            hits.append(f"{art.name}: {n} real string(s) present (values withheld)")
    return hits


def main(argv: list[str]) -> int:
    if argv[1:] == ["--selftest"]:
        needles = {"a real sentence that must be found in the planted artifact"}
        with tempfile.TemporaryDirectory() as d:
            art = Path(d) / "packet.md"
            art.write_text("x " + next(iter(needles)) + " y", encoding="utf-8")
            clean = Path(d) / "clean.md"
            clean.write_text("nothing here", encoding="utf-8")
            found = scan([art], needles)
            not_found = scan([clean], needles)
        if not found or not_found:
            print("REAL-STRING SCAN SELFTEST: BLIND")
            return EXIT_COULD_NOT_RUN
        print("REAL-STRING SCAN SELFTEST: ok (planted string found; clean file clean)")
        return EXIT_CLEAN
    output = OUTPUT
    if len(argv) == 2:
        output = Path(argv[1])
    elif argv[1:]:
        print("usage: realdata_leak_scan.py [--selftest | <artifacts-dir>]", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    texts = real_texts()
    if not texts:
        print(f"could-not-run: no local real data under {DATA_DIR}", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    artifacts = sorted(p for p in output.glob("*") if p.is_file()) if output.is_dir() else []
    if not artifacts:
        print(f"could-not-run: no artifacts under {output}", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    needles = samples(texts)
    hits = scan(artifacts, needles)
    if hits:
        print(
            f"REAL-STRING SCAN: LEAK ({len(needles)} sampled strings from {len(texts)} real texts)"
        )
        for h in hits:
            print(f"  {h}")
        return EXIT_LEAK
    print(
        f"REAL-STRING SCAN: CLEAN ({len(needles)} sampled strings from {len(texts)} real texts, "
        f"{len(artifacts)} artifacts searched)"
    )
    return EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
