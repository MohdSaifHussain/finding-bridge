# finding-bridge

Turn AI red-team tool output into standard, sealed, provenance-stamped
findings. Feed them into the systems your team already uses.

Think of it as `pandoc` for AI red-team findings. Attack tools find
failures. finding-bridge is where a failure becomes a finding: normalized,
provable, sealed, and ready to share.

**It never replaces your tools. It feeds them.**

```
garak hitlogs  ──┐                              ┌──> Markdown packet
                 ├──> seal + hash + dedup + ────┤
transcripts    ──┘    human confirm             └──> SARIF 2.1.0
```

## What it does

- **Reads** garak hitlogs and manual attack transcripts.
- **Seals** harmful content. It is encrypted at rest and shown as a
  "safe metadata preview": length, line count, a keyed digest, and harm
  flags. Triagers can score findings without re-reading raw harm.
  Unsealing is always explicit and always logged.
- **Stamps** every finding with hashes and a tamper-evident chain, so a
  finding stays credible after the model changes.
- **Waits for a human.** Nothing becomes a confirmed finding until a
  person confirms it. The record shows who and when.
- **Emits** Markdown packets and SARIF 2.1.0 that real tools accept.

No AI runs anywhere in this pipeline. No API key is needed, ever. The
test suite proves it on every run.

## Install

Python 3.12 or newer.

```
git clone <this repo>
cd finding-bridge
pip install -e .
```

This gives you the `finding-bridge` command.

To verify dependency hashes as well, build and install a wheel. This is
the route we test:

```
pip install build
python -m build --wheel
pip install dist/finding_bridge-0.1.0-py3-none-any.whl -c constraints.txt
```

Hash verification needs a wheel. `pip` cannot hash-check an install from
a source directory, so `-c constraints.txt` does not work with
`pip install -e .`.

## Five-minute tour

The repo ships synthetic example files. The "harmful" text in them is
fake. Strings like `SENTINEL-HARM-7001` are labeled stand-ins, never real
model output.

```
finding-bridge ingest-garak schemas/fixtures/garak.synthetic.hitlog.jsonl
finding-bridge list
finding-bridge confirm <id-from-list>
finding-bridge verify
finding-bridge emit-markdown out/packet.md
finding-bridge emit-sarif out/findings.sarif
```

See [docs/USAGE.md](docs/USAGE.md) for the full walk-through, every
command, and the reason-code reference.

## Honest limits (short form)

- The preview is metadata: length, line count, a keyed digest, and harm
  flags. It is not a summary of the content. A meaning-level summary
  would need AI, and no AI is allowed in this pipeline.
- Tamper-evidence bound: the hash chain and its head detect accident,
  drift and casual edit. They do not defend against an attacker with
  write access to both the ledger and its head at once.
- Finding ids are local to one store. Two analysts ingesting the same
  file get different ids.
- Duplicate detection is exact-match only. Similar-but-not-identical
  findings are not clustered.
- Input files are capped at 10 MiB.

The full list, in user language, is in
[docs/USAGE.md](docs/USAGE.md#limits).

## Project record

Every decision, limit, and open obligation is written down:
`DECISIONS.md`, `docs/PROJECT_CHARTER.md`, and the phase contracts in
`docs/decisions/`.
