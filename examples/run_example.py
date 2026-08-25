"""Run one worked example end to end and record what happened.

    python examples/run_example.py 01-garak-triage           # run; write output/ + transcript
    python examples/run_example.py 01-garak-triage --check   # re-run to scratch and compare
    python examples/run_example.py --all [--check]

WHAT THIS IS. Each example folder holds synthetic input (D-012), a README
that narrates the commands, and the REAL artifacts a run produced under
output/, with the complete transcript of that run in run-transcript.md,
refusals included. This driver is how those artifacts were produced, so
the README's commands and the committed artifacts cannot drift from each
other: the command list lives here, once.

WHAT --check PROVES, AND WHAT IT DOES NOT (stated plainly, PROV-3). The
contract asked for a control asserting each committed artifact
byte-matches a fresh re-run. A fresh run cannot byte-match, because the
store key is generated per store (finding ids, sealed refs, keyed
digests and hashes all derive from it: D-028, a stated limit), the
confirmation timestamp is the wall clock, and confirmed_by is the local
git identity. Committing a fixed key would put key material in the tree,
which key-inside-repo exists to refuse. So --check compares after
normalising EXACTLY those volatile fields (the list is VOLATILE below,
visible and short) and fails on any other difference. A pass means: the
same commands produce the same artifacts in every field that does not
derive from the key, the clock, or the operator. It does not prove
byte identity, and does not claim to.

The store and key live in a scratch folder OUTSIDE the repo, created per
run and removed after, so no run can leave key material in the tree.

EXIT CODES: 0 ran (or check passed); 1 check found a difference;
2 could not run (unknown example, finding-bridge missing, git identity
unset).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = Path(
    os.environ.get("FB_REALDATA_DIR")
    or Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "finding-bridge-realdata"
)
EXIT_OK, EXIT_DIFF, EXIT_COULD_NOT_RUN = 0, 1, 2

# Volatile fields, normalised before comparison. Each derives from the key,
# the clock, the operator identity, or the OS path separator.
VOLATILE: list[tuple[str, str]] = [
    (r"fb-[0-9a-f]{16}", "fb-<id>"),
    (r"cl-[0-9a-f]{16}", "cl-<cluster>"),
    (r'"(confirmed_by|actor)": "[^"]*"', r'"": "<identity>"'),
    (r"\b[0-9a-f]{64}\b", "<hash64>"),
    (r"sealed/[0-9a-f]{16}", "sealed/<ref>"),
    (r"keyed digest [0-9a-f]{8}", "keyed digest <digest>"),
    (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(\+00:00|Z)", "<timestamp>"),
    (r"by [^<\n]+<[^>\n]+>", "by <identity>"),
    (r"(?<=\d{2}:\d{2}:\d{2})\.\d{6}", ""),
    (r"\\", "/"),
]

# Command lists. {id0} = first candidate id from the last `list`;
# {ref0} = first response ref from the last emitted packet. Steps that
# are not finding-bridge commands are tuples ("driver", label, fn).
EXAMPLES: dict[str, list] = {
    "01-garak-triage": [
        "ingest-garak input/garak.synthetic.hitlog.jsonl",
        "list",
        "confirm {id0}",
        "confirm fb-0000000000000000",
        "ingest-garak input/garak.hostile.hitlog.jsonl",
        "verify",
        "emit-markdown output/packet.md",
        "emit-sarif output/findings.sarif --artifact-uri-base examples/01-garak-triage/output",
        "emit-tracker output/findings.tracker.json",
        "emit-flare output/findings.flare.json",
    ],
    "02-transcript-capture": [
        "ingest-transcript input/attack.txt --target-model synthetic-model",
        "ingest-transcript input/attack.json",
        "ingest-transcript input/malformed.txt",
        "list",
        "confirm {id0}",
        "verify",
        "emit-markdown output/packet.md",
        "emit-sarif output/findings.sarif",
        "unseal {ref0}",
        "unseal {ref0} --explicit",
        ("driver", "read the exposure log", "show_exposure_log"),
    ],
    "03-rotation-drill": [
        "ingest-garak input/garak.synthetic.hitlog.jsonl",
        "list",
        "confirm {id0}",
        "verify",
        "emit-markdown output/packet-before-rotation.md",
        ("driver", "BACKUP: copy the store folder and the key file to backup/", "backup"),
        'rotate-key --reason "drill: first rotation"',
        "verify",
        "unseal {ref0} --explicit",
        'rotate-key --reason "drill: second rotation"',
        "verify",
        "list",
        ("driver", "INCIDENT: flip one byte inside the ledger by hand", "tamper_ledger"),
        "verify",
        ("driver", "RESTORE: copy backup/ back over the store folder and the key file", "restore"),
        "verify",
    ],
    # Real data (W6c). Inputs live OUTSIDE the tree at DATA_DIR (D-012); the
    # transcript shows them as <DATA_DIR>/... and never a local path.
    "04-real-data": [
        "ingest-garak {data}/garak/fb-real.hitlog.jsonl",
        (
            "driver",
            "ingest every prepared real transcript under <DATA_DIR>/prepared/ "
            "(--grammar human-assistant; facts via --environment from the sidecars)",
            "ingest_prepared",
        ),
        (
            "driver",
            "count candidates by source, duplicates, sealed probes and responses, "
            "source facts (metadata only)",
            "count_candidates",
        ),
        ("driver", "list: the first 5 lines of N (safe metadata previews only)", "list_head"),
        "confirm {id0}",
        "ingest-garak {data}/red_team_attempts.jsonl.gz",
        "verify",
        "emit-markdown output/packet.md",
        "emit-sarif output/findings.sarif --artifact-uri-base examples/04-real-data/output",
        "emit-tracker output/findings.tracker.json",
        "emit-flare output/findings.flare.json",
        (
            "driver",
            "real-string leak scan of every emitted artifact (tools/realdata_leak_scan.py)",
            "leak_scan",
        ),
    ],
}


class Run:
    def __init__(self, example: str, workdir: Path, out_dir: Path):
        self.example = example
        self.cwd = workdir
        self.scratch = Path(tempfile.mkdtemp(prefix="fb-example-"))
        self.store = self.scratch / "store"
        self.key = self.scratch / "key" / "fb.key"
        self.backup_dir = self.scratch / "backup"
        self.out_dir = out_dir
        self.workdir = workdir
        self.ids: list[str] = []
        self.refs: list[str] = []
        self.lines: list[str] = []

    def cleanup(self) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)

    # -- steps --

    def fb(self, command: str) -> None:
        shown = command
        command = command.replace("{id0}", self.ids[0] if self.ids else "{id0}")
        command = command.replace("{ref0}", self.refs[0] if self.refs else "{ref0}")
        shown = command.replace("{data}", "<DATA_DIR>")
        command = command.replace("{data}", DATA_DIR.as_posix())
        argv = ["finding-bridge", "--store", str(self.store), "--key", str(self.key)]
        argv += _split(command)
        proc = subprocess.run(argv, cwd=self.cwd, capture_output=True, text=True, encoding="utf-8")
        text = (proc.stdout + proc.stderr).rstrip("\n")
        self.lines.append(f"$ finding-bridge {shown}")
        if text:
            self.lines.append(text)
        self.lines.append(f"[exit {proc.returncode}]")
        self.lines.append("")
        if command.startswith("list"):
            self.ids = re.findall(r"fb-[0-9a-f]{16}", proc.stdout)
        if command.startswith("emit-markdown") and proc.returncode == 0:
            packet = (self.out_dir / _split(command)[1].split("/", 1)[1]).read_text(
                encoding="utf-8"
            )
            self.refs = re.findall(r"response (sealed/[0-9a-f]{16})", packet)

    def driver(self, label: str, fn: str) -> None:
        self.lines.append(f"$ [driver step] {label}")
        self.lines.append(getattr(self, fn)())
        self.lines.append("[driver step done]")
        self.lines.append("")

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        argv = ["finding-bridge", "--store", str(self.store), "--key", str(self.key), *args]
        return subprocess.run(argv, cwd=self.cwd, capture_output=True, text=True, encoding="utf-8")

    def ingest_prepared(self) -> str:
        files = sorted((DATA_DIR / "prepared").glob("*.txt"))
        ok, refused = 0, {}
        for f in files:
            args = ["ingest-transcript", str(f), "--grammar", "human-assistant"]
            args += ["--target-model", "hh-rlhf red-team model"]
            meta = f.with_suffix(".meta.json")
            if meta.exists():
                for k, v in json.loads(meta.read_text(encoding="utf-8")).items():
                    args += ["--environment", f"{k}={v}"]
            proc = self._cli(*args)
            if proc.returncode == 0:
                ok += 1
            else:
                code = proc.stderr.split(":", 1)[0].strip()
                refused[code] = refused.get(code, 0) + 1
        n_ref = sum(refused.values())
        return f"{len(files)} files: ingested {ok}, refused {n_ref} {refused or ''}".strip()

    def count_candidates(self) -> str:
        import json as _json

        rows = [
            _json.loads(ln)
            for ln in (self.store / "candidates.jsonl").read_text(encoding="utf-8").splitlines()
            if ln.strip()
        ]
        by_tool: dict[str, int] = {}
        for r in rows:
            by_tool[r["source_tool"]] = by_tool.get(r["source_tool"], 0) + 1
        dups = sum(1 for r in rows if r["dedup"]["duplicate_of"])
        self.ids = [r["id"] for r in rows if r["source_tool"] == "garak"] or [r["id"] for r in rows]
        sealed_probe = sum(1 for r in rows if r["probe"]["sealed_ref"])
        sealed_resp = sum(1 for r in rows if r["raw_response_sealed"])
        with_facts = sum(
            1
            for r in rows
            if any(
                k.startswith(("garak.", "manual."))
                for k in (r["reproduction"]["environment"] or {})
            )
        )
        return (
            f"candidates: {len(rows)} by source {by_tool}; marked duplicate: {dups}; "
            f"probe sealed: {sealed_probe}/{len(rows)}; "
            f"response sealed: {sealed_resp}/{len(rows)}; "
            f"with source facts in environment: {with_facts}/{len(rows)}"
        )

    def list_head(self) -> str:
        proc = self._cli("list")
        lines = proc.stdout.splitlines()
        return "\n".join(lines[:5] + [f"... {len(lines)} lines in total"])

    def leak_scan(self) -> str:
        proc = subprocess.run(
            [
                sys.executable,
                str(HERE.parent / "tools" / "realdata_leak_scan.py"),
                str(self.out_dir),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return (proc.stdout + proc.stderr).strip() + f"\n[exit {proc.returncode}]"

    def show_exposure_log(self) -> str:
        log = self.store / "sealed" / "exposure_log.jsonl"
        return log.read_text(encoding="utf-8").rstrip("\n")

    def backup(self) -> str:
        shutil.copytree(self.store, self.backup_dir / "store")
        shutil.copy2(self.key, self.backup_dir / "fb.key")
        return (
            "copied store/ and fb.key into backup/ (the key is NOT inside the store; back up both)"
        )

    def restore(self) -> str:
        shutil.rmtree(self.store)
        shutil.copytree(self.backup_dir / "store", self.store)
        shutil.copy2(self.backup_dir / "fb.key", self.key)
        return (
            "store/ and fb.key replaced from backup/ (the backup predates both "
            "rotations, so the older key is restored with it)"
        )

    def tamper_ledger(self) -> str:
        ledger = self.store / "ledger.jsonl"
        raw = ledger.read_bytes()
        i = raw.index(b'"source_tool": "garak"')
        raw = raw[:i] + b'"source_tool": "gara_"' + raw[i + len(b'"source_tool": "garak"') :]
        ledger.write_bytes(raw)
        return "ledger.jsonl: one byte changed inside a confirmed record (source_tool)"

    # -- run --

    def go(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.lines.append(f"# Run transcript: {self.example}")
        self.lines.append("")
        self.lines.append(
            "Complete, unedited output of `python examples/run_example.py "
            f"{self.example}`. The store and key were in a scratch folder outside "
            "the repo, passed as `--store` and `--key` on every command (omitted "
            "from the lines below only because the path is a temp folder). "
            "Refusals are shown as they happened: they are the product behaving well."
        )
        self.lines.append("")
        self.lines.append("```")
        for step in EXAMPLES[self.example]:
            if isinstance(step, tuple):
                self.driver(step[1], step[2])
            else:
                self.fb(step)
        self.lines.append("```")


def _split(command: str) -> list[str]:
    import shlex

    return shlex.split(command, posix=True)


def normalise(text: str) -> str:
    for pattern, repl in VOLATILE:
        text = re.sub(pattern, repl, text)
    return text


def run_one(example: str, check: bool) -> int:
    if example not in EXAMPLES:
        print(f"could-not-run: unknown example {example}", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if shutil.which("finding-bridge") is None:
        print("could-not-run: finding-bridge is not on PATH (pip install -e .)", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if example == "04-real-data" and not (DATA_DIR / "garak" / "fb-real.hitlog.jsonl").exists():
        print(
            f"could-not-run: no real data under {DATA_DIR}; run examples/04-real-data/fetch.py "
            "and run_garak.py first (the data is never committed, D-012)",
            file=sys.stderr,
        )
        return EXIT_COULD_NOT_RUN
    committed = HERE / example / "output"
    if check:
        # a scratch copy of the example folder, so every path in the
        # transcript is the same relative path a reader would type
        workdir = Path(tempfile.mkdtemp(prefix="fb-check-")) / example
        shutil.copytree(HERE / example, workdir, ignore=shutil.ignore_patterns("output"))
        target = workdir / "output"
    else:
        workdir = HERE / example
        target = committed
        if target.exists():
            shutil.rmtree(target)
    run = Run(example, workdir, target)
    try:
        run.go()
        (target / "run-transcript.md").write_text("\n".join(run.lines) + "\n", encoding="utf-8")
        if not check:
            print(f"{example}: wrote {len(list(target.iterdir()))} files under {committed}")
            return EXIT_OK
        return compare(committed, target, example)
    finally:
        run.cleanup()
        if check:
            shutil.rmtree(workdir.parent, ignore_errors=True)


def compare(committed: Path, fresh: Path, example: str) -> int:
    if not committed.is_dir():
        print(f"could-not-run: no committed output for {example}", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    names_c = sorted(p.name for p in committed.iterdir())
    names_f = sorted(p.name for p in fresh.iterdir())
    problems = []
    if names_c != names_f:
        problems.append(f"file set differs: committed {names_c} fresh {names_f}")
    for name in sorted(set(names_c) & set(names_f)):
        a = normalise((committed / name).read_text(encoding="utf-8"))
        b = normalise((fresh / name).read_text(encoding="utf-8"))
        if a != b:
            for i, (la, lb) in enumerate(
                zip(a.splitlines(), b.splitlines(), strict=False), start=1
            ):
                if la != lb:
                    problems.append(f"{name}:{i}: committed {la!r} / fresh {lb!r}")
                    break
            else:
                problems.append(f"{name}: line count differs")
    if problems:
        print(f"SHOWCASE CHECK: DIFFERENT ({example})")
        for p in problems:
            print(f"  {p}")
        return EXIT_DIFF
    print(
        f"SHOWCASE CHECK: SAME after normalising volatile fields ({example}, {len(names_c)} files)"
    )
    return EXIT_OK


def main(argv: list[str]) -> int:
    check = "--check" in argv
    args = [a for a in argv[1:] if a != "--check"]
    if args == ["--all"]:
        args = sorted(EXAMPLES)
    if not args:
        print(__doc__)
        return EXIT_COULD_NOT_RUN
    ident = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
    if ident.returncode != 0 or not ident.stdout.strip():
        print("could-not-run: git identity unset; confirm needs it (D-011)", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    worst = EXIT_OK
    for example in args:
        rc = run_one(example, check)
        worst = max(worst, rc)
    return worst


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
