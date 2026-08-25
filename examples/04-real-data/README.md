# Example 04: real data, the sealing feature demonstrating itself

Every other example uses synthetic input. This one does not. Its inputs
are real: a garak run this project did not script, against a real model,
and real red-team transcripts written by people attacking real models.
That is exactly the content class this tool was built for, and it is
why this is the one example only this tool can publish safely.

## What is NOT here, and where it is

D-012 is absolute: no real harmful content is committed to this
repository, in any file, in any form. The inputs live OUTSIDE the tree,
at `DATA_DIR` (default `%LOCALAPPDATA%\finding-bridge-realdata`, or
`$FB_REALDATA_DIR`), produced by two committed scripts that carry the
source, the checksum and the exact command:

- `fetch.py` downloads Anthropic's `red-team-attempts` file from the
  hh-rlhf dataset (MIT; sha256 pinned in the script, 15,483,307 bytes,
  38,961 transcripts), verifies it, and writes a fixed sample of 40
  transcripts unchanged under `DATA_DIR/prepared/`, each with a sidecar
  of its facts.
- `run_garak.py` runs garak 0.16.0 against `llama3.2:1b` on the local
  Ollama server (dan and promptinject families, 1 generation, 45-minute
  box) and leaves the hitlog under `DATA_DIR/garak/`.

What IS committed under `output/` is the product's own answer to the
tension: the run transcript with ingestion counts, sealed previews, dedup
results and verify output, and the four emitted artifacts, whose whole
design claim is that they carry preview and metadata and never raw harm.

## The run, 2026-08-25

garak 0.16.0, 505.51 seconds wall clock (box 2,700 s), six probes,
699 detector hits. garak's own per-probe summary, with the run
parameters it was measured under (someone will cite it): target
`llama3.2:1b` on Ollama 0.32.15, `--generations 1`, `--spec
probes.dan,probes.promptinject` (the six default-active probes listed
below), 2026-08-25, one run:

| Probe | Detector | ok on | Attack success rate |
|---|---|---|---|
| dan.Ablation_Dan_11_0 | dan.DAN | 37/127 | 70.87% |
| dan.Ablation_Dan_11_0 | mitigation.MitigationBypass | 21/127 | 83.46% |
| dan.AutoDANCached | dan.DAN | 3/3 | pass |
| dan.AutoDANCached | mitigation.MitigationBypass | 2/3 | 33.33% |
| dan.DanInTheWild | mitigation.MitigationBypass | 64/256 | 75.00% |
| promptinject.HijackHateHumans | promptinject.AttackRogueString | 141/256 | 44.92% |
| promptinject.HijackKillHumans | promptinject.AttackRogueString | 215/256 | 16.02% |
| promptinject.HijackLongPrompt | promptinject.AttackRogueString | 102/256 | 60.16% |

A weak 1B target was chosen on purpose: more hits, more real content
for the seal to hold against.

Then the pipeline (`output/run-transcript.md`, complete and unedited):

```
$ finding-bridge ingest-garak <DATA_DIR>/garak/fb-real.hitlog.jsonl
{"ingested": 699, "total_candidates": 699, "duplicates_marked": 62}
$ [driver step] ingest every prepared real transcript under <DATA_DIR>/prepared/ (--grammar human-assistant; facts via --environment from the sidecars)
40 files: ingested 40, refused 0
$ [driver step] count candidates by source, duplicates, sealed probes and responses, source facts (metadata only)
candidates: 739 by source {'garak': 699, 'manual-transcript': 40}; marked duplicate: 62; probe sealed: 739/739; response sealed: 739/739; with source facts in environment: 739/739
```

**Before and after the F-12 fix, the number that proves it:** on the
first pass the garak adapter sealed the response on 699 of 699 hits and
the attack prompt on **0 of 699**; after D-079 it seals both on
**739 of 739** candidates (699 garak, 40 transcripts). The duplicate
count moved with it, 253 to 62, and that is a correction, not a change
in the data: with every prompt null, dedup keyed on responses alone and
counted different attacks that drew the same reply as duplicates. 62 of
699 real hits are exact duplicates in prompt AND response, which is the
real Pain-4 figure (D-025), and the earlier 253 is recorded as C-011.

**The sealing claim has survived contact with real harmful content,
re-derived by the director:** both scans were re-run by the director's
own hands on the first pass (fixture scan conforming; real-string scan
clean, 5,000 sampled strings), and again by the builder on this one.

The refusal in this example is real too: the raw 15 MB dataset archive
fed to `ingest-garak` refuses with `input-too-large` at the 10 MiB cap,
location named, nothing read past the limit.

## The two controls that make this example publishable

1. `tools/fixture_scan.py` sweeps `output/` for sentinel strings, as for
   every example.
2. `tools/realdata_leak_scan.py`, the stronger one: at run time it reads
   the local real data, samples 5,000 distinct windows of the real
   prompts and responses (from 4,784 real texts), and searches every
   committed artifact for any of them. The strings are never written
   anywhere. Result on this output: `REAL-STRING SCAN: CLEAN`. Its
   selftest plants a string and must find it; a clean file must stay
   clean.

So the seal is shown holding against real content, not only against
sentinels. What that scan does not prove: that no transformed form
(paraphrase, hash, re-encoding) leaked. It proves no verbatim window of
the sampled real text appears in anything committed.

## What real data found (findings for the director, evidence/step06-findings.md)

- **F-12**, the one expected: the garak adapter silently lost the attack
  PROMPT on every one of the 699 hits. garak 0.16.0 writes the prompt as
  a Conversation whose turns carry a nested Message; the adapter never
  descended into it. The response sealed fine. FIXED (D-079): both
  shapes handled, each with its own fixture; an unrecognised shape now
  refuses instead of nulling; `docs/FIXTURE-VERSIONS.md` records which
  tool version each fixture mimics, with a test.
- **F-10**: the largest public red-team corpus writes `Human:` /
  `Assistant:`; the grammar accepted only `USER:` / `ASSISTANT:`. FIXED
  (D-080): `--grammar human-assistant`, exact, operator-named, never
  auto-detected; this example now ingests the transcripts unchanged.
- **F-11**: no field for per-record metadata (rating, task, model size).
  FIXED (D-081): `--environment KEY=VALUE` into
  `reproduction.environment` as `manual.KEY`; this example passes each
  record's rating, model type, parameter count and harmlessness score.
- **F-13**: `lang`, `data_*` on messages are now `garak.<side>.<key>` in
  the environment; `notes` joins `goal` and `triggers` in the sealed
  context (D-081).

## Reproduce

```
python examples/04-real-data/fetch.py
python examples/04-real-data/run_garak.py        (needs Ollama with llama3.2:1b, and garak; a fresh run gives different hits)
python examples/run_example.py 04-real-data
python examples/run_example.py 04-real-data --check
python tools/realdata_leak_scan.py
```

`--check` compares a fresh re-run to the committed artifacts after
normalising key-, clock- and operator-derived fields (PROV-3, D-072). It
needs the local data; without it, the audit test for this example skips
and says so.
