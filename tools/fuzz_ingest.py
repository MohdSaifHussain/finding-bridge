"""OB-5: structured malformed-input fuzzing of the two ingest parsers.

    python tools/fuzz_ingest.py --minutes 30 [--seed-dir DIR]   # the OB-5 pass
    python tools/fuzz_ingest.py --selftest                       # prove it can see a crash

WHY THIS AND NOT ATHERIS. OB-5's recorded trigger fired on 2026-08-25
(D-078). Atheris was checked before promising: PyPI serves only
manylinux2014_x86_64 wheels for atheris 3.1.0, and `pip install atheris`
on this Windows / CPython machine answers "No matching distribution found".
This is the honest structured alternative the ruling named: a randomised
malformed-input generator over the boundary table's refusal families
(D-036, D-044), seeded from REAL-DATA SHAPES read at run time from a local
directory that is never committed, driving both parsers through the CLI
entry (`cli.main`), where every outcome must be a governed refusal or a
success.

WHAT COUNTS AS A FINDING: any exception that escapes `cli.main` (a raw
traceback the operator would see), any exit code other than 0 or 1, and
any run that exceeds the per-input time cap. Governed refusals (exit 1
with a reason code) and successes are the expected outcomes and are
counted, not reported.

WHAT A PASS DOES NOT PROVE: coverage. This generator mutates along the
families someone thought to name (structure, numbers, encoding, markers,
size, JSON shape); it is not coverage-guided and it cannot find a class it
does not mutate toward. It proves the named families do not escape, for
the minutes it ran, on the seeds it had. The count of inputs and the
wall-clock budget are printed so the claim carries its own width.

EXIT CODES: 0 no findings; 1 findings (listed, values withheld per D-036);
2 could not run.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import random
import sys
import tempfile
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from finding_bridge import cli  # noqa: E402

EXIT_OK, EXIT_FINDINGS, EXIT_COULD_NOT_RUN = 0, 1, 2
PER_INPUT_CAP_S = 20.0

GARAK_SEED = {
    "goal": "SENTINEL-GOAL synthetic seed",
    "prompt": {"turns": [{"role": "user", "content": {"text": "SENTINEL-PROBE seed"}}]},
    "output": {"role": "assistant", "content": {"text": "SENTINEL-HARM-SEED seed"}},
    "triggers": None,
    "score": 1.0,
    "run_id": "00000000-0000-0000-0000-000000000000",
    "attempt_id": "00000000-0000-0000-0000-000000000001",
    "attempt_seq": 0,
    "attempt_idx": 0,
    "generator": "ollama llama3.2:1b",
    "probe": "dan.Dan_11_0",
    "detector": "mitigation.MitigationBypass",
    "generations_per_prompt": 1,
}
TRANSCRIPT_SEED = "USER: SENTINEL-PROBE seed\nASSISTANT: SENTINEL-HARM-SEED seed\n"

# Mutation families, each named for the boundary-table refusal family it
# aims at. Each takes (rng, text) and returns text.
JUNK = ["﻿", "\x00", "\r", " ", "\ud800", "\U0001f600", "：", "\t", " " * 8]


def m_truncate(rng, s):
    return s[: rng.randrange(len(s) + 1)] if s else s


def m_insert_junk(rng, s):
    i = rng.randrange(len(s) + 1)
    return s[:i] + rng.choice(JUNK) * rng.randrange(1, 4) + s[i:]


def m_numbers(rng, s):
    bad = rng.choice(["NaN", "Infinity", "-Infinity", "1e400", str(2**53 + 1), "-0.0", "1E-400"])
    return s.replace("1.0", bad, 1).replace('"score": 1.0', f'"score": {bad}')


def m_duplicate_lines(rng, s):
    lines = s.splitlines(keepends=True)
    if not lines:
        return s
    i = rng.randrange(len(lines))
    return "".join(lines[:i] + [lines[i]] * rng.randrange(2, 5) + lines[i:])


def m_marker_variants(rng, s):
    v = rng.choice(
        ["User:", "USER :", "USER\t:", "USER：", "  USER:", "Human:", "ASSISTANT:\n", "SYSTEM:"]
    )
    return s.replace("USER:", v, 1) if "USER:" in s else v + "\n" + s


def m_json_shape(rng, s):
    tricks = [
        lambda t: t.replace('"prompt"', '"prompt_x"'),
        lambda t: t.replace('{"turns"', '["turns"'),
        lambda t: t.replace('"output"', '"output": null, "output_'),
        lambda t: t + "\n" + t,
        lambda t: t.replace("}", "", 1),
        lambda t: "[" + t + "]",
        lambda t: t.replace('"content": {"text"', '"content": {"text": null, "t"'),
        lambda t: t.replace('"text": "', '"text": "' + "x" * rng.randrange(0, 3000)),
    ]
    return rng.choice(tricks)(s)


def m_grow(rng, s):
    return s * rng.randrange(2, 40)


def m_encoding_bytes(rng, s):
    return s  # handled at write time: raw non-UTF-8 bytes appended


FAMILIES = [
    ("truncate", m_truncate),
    ("junk", m_insert_junk),
    ("numbers", m_numbers),
    ("duplicate-lines", m_duplicate_lines),
    ("marker-variants", m_marker_variants),
    ("json-shape", m_json_shape),
    ("grow", m_grow),
    ("encoding", m_encoding_bytes),
]


def load_seeds(seed_dir: Path | None) -> tuple[list[str], list[str]]:
    """Real-data shapes: hitlog lines and transcript texts, from a local
    directory that is never committed. Falls back to the synthetic seeds."""
    garak = [json.dumps(GARAK_SEED)]
    transcripts = [TRANSCRIPT_SEED]
    if seed_dir and seed_dir.is_dir():
        for p in seed_dir.rglob("*.hitlog.jsonl"):
            garak += [
                ln
                for ln in p.read_text(encoding="utf-8", errors="replace").splitlines()
                if ln.strip()
            ][:200]
        for p in seed_dir.rglob("*.txt"):
            transcripts.append(p.read_text(encoding="utf-8", errors="replace"))
    return garak, transcripts


def run_one(argv: list[str]) -> tuple[str, str]:
    """Drive cli.main; classify the outcome."""
    out, err = io.StringIO(), io.StringIO()
    t0 = time.monotonic()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(argv)
    except SystemExit as exc:  # argparse
        rc = exc.code if isinstance(exc.code, int) else 2
    except BaseException:  # noqa: BLE001 - this IS the finding
        return "CRASH", traceback.format_exc().splitlines()[-1][:160]
    dt = time.monotonic() - t0
    if dt > PER_INPUT_CAP_S:
        return "SLOW", f"{dt:.1f}s"
    if rc == 0:
        return "ok", ""
    if rc == 1:
        return "refused", err.getvalue().split(":", 1)[0].strip()[:40]
    return "EXIT", f"exit {rc}"


def fuzz(minutes: float, seed_dir: Path | None, rng_seed: int) -> tuple[dict, list[str], int]:
    garak_seeds, transcript_seeds = load_seeds(seed_dir)
    rng = random.Random(rng_seed)
    counts: dict[str, int] = {}
    findings: list[str] = []
    n = 0
    deadline = time.monotonic() + minutes * 60
    with tempfile.TemporaryDirectory(prefix="fb-fuzz-") as tmp:
        tmp = Path(tmp)
        store, key = tmp / "store", tmp / "k" / "fb.key"
        while time.monotonic() < deadline:
            n += 1
            kind = rng.choice(["garak", "transcript"])
            base = rng.choice(garak_seeds if kind == "garak" else transcript_seeds)
            text = base
            for _ in range(rng.randrange(1, 4)):
                fam, fn = rng.choice(FAMILIES)
                text = fn(rng, text)
            path = tmp / f"in-{n}.{'jsonl' if kind == 'garak' else 'txt'}"
            data = text.encode("utf-8", errors="surrogatepass")
            if fam == "encoding" or rng.random() < 0.1:
                data += bytes(rng.randrange(128, 256) for _ in range(rng.randrange(1, 40)))
            path.write_bytes(data)
            cmd = "ingest-garak" if kind == "garak" else "ingest-transcript"
            outcome, detail = run_one(["--store", str(store), "--key", str(key), cmd, str(path)])
            key_name = f"{kind}:{outcome}:{detail}" if outcome == "refused" else f"{kind}:{outcome}"
            counts[key_name] = counts.get(key_name, 0) + 1
            if outcome in ("CRASH", "SLOW", "EXIT"):
                findings.append(f"input {n} ({kind}, last family {fam}): {outcome} {detail}")
            try:
                path.unlink()
            except OSError:
                pass
    return counts, findings, n


def selftest() -> int:
    """The harness must SEE a crash: drive a function that raises."""

    def boom(argv):
        raise ValueError("planted")

    real = cli.main
    try:
        cli.main = boom
        outcome, _ = run_one(["x"])
    finally:
        cli.main = real
    if outcome != "CRASH":
        print(f"FUZZ SELFTEST: BLIND (got {outcome})")
        return EXIT_COULD_NOT_RUN
    print("FUZZ SELFTEST: ok (a planted crash is classified CRASH)")
    return EXIT_OK


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--minutes", type=float, default=None)
    ap.add_argument("--seed-dir", type=Path, default=None)
    ap.add_argument("--rng-seed", type=int, default=20260825)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if a.minutes is None:
        ap.print_help()
        return EXIT_COULD_NOT_RUN
    os.environ.pop("ANTHROPIC_API_KEY", None)
    t0 = time.monotonic()
    counts, findings, n = fuzz(a.minutes, a.seed_dir, a.rng_seed)
    wall = time.monotonic() - t0
    print(
        f"FUZZ: {n} inputs in {wall / 60:.1f} min (budget {a.minutes} min), rng seed {a.rng_seed}"
    )
    for k in sorted(counts):
        print(f"  {counts[k]:6d}  {k}")
    if findings:
        print(f"FUZZ: {len(findings)} FINDING(S)")
        for f in findings:
            print(f"  {f}")
        return EXIT_FINDINGS
    print("FUZZ: no escaped exception, no slow input, no unexpected exit code")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
