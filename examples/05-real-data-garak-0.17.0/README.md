# Example 05: real data on garak 0.17.0

This is example 04's real-data drill, run again on garak 0.17.0. The
inputs are real: a garak run against a real model, and real red-team
transcripts written by people attacking real models. Example 04 keeps the
first run (garak 0.16.0, 2026-08-25); this example holds the second
(garak 0.17.0, 2026-09-16), so each garak version has its own record.

## What is NOT here, and where it is

D-012 is absolute: no real harmful content is committed to this
repository, in any file, in any form. This example's inputs live OUTSIDE
the tree, in their own folder: `%LOCALAPPDATA%\finding-bridge-realdata-garak-0.17.0`
(or `%FB_REALDATA_DIR_05%`). They are made by example 04's committed
scripts, which carry the source, the checksum and the exact command
(`fetch.py` and `run_garak.py`), pointed at this folder.

What IS committed under `output/` is the product's own output: the run
transcript with ingestion counts, sealed previews, dedup results and
verify output, and the four emitted artifacts, which carry preview and
metadata and never raw harm.

## The run, 2026-09-16

garak 0.17.0, 451.86 seconds by garak's own clock (box 2,700 s), six
probes, 668 detector hits. garak's own per-probe summary, with the run
parameters it was measured under: target `llama3.2:1b` on Ollama 0.32.15,
`--generations 1`, `--spec probes.dan,probes.promptinject` (the same six
default-active probes as example 04), garak in its own venv on Python
3.13.5, 2026-09-16, one run:

| Probe | Detector | ok on | Attack success rate |
|---|---|---|---|
| dan.Ablation_Dan_11_0 | dan.DAN | 38/127 | 70.08% |
| dan.Ablation_Dan_11_0 | mitigation.MitigationBypass | 25/127 | 80.31% |
| dan.AutoDANCached | dan.DAN | 3/3 | pass |
| dan.AutoDANCached | mitigation.MitigationBypass | 1/3 | 66.67% |
| dan.DanInTheWild | mitigation.MitigationBypass | 60/256 | 76.56% |
| promptinject.HijackHateHumans | promptinject.AttackRogueString | 146/256 | 42.97% |
| promptinject.HijackKillHumans | promptinject.AttackRogueString | 227/256 | 11.33% |
| promptinject.HijackLongPrompt | promptinject.AttackRogueString | 116/256 | 54.69% |

These rates are not comparable one to one with example 04. The model
samples, so a fresh run gives different hits, and garak 0.17.0 passes
generation settings (such as a response length cap) to Ollama, which
0.16.0 did not.

Then the pipeline (`output/run-transcript.md`, complete and unedited):

```
$ finding-bridge ingest-garak <DATA_DIR>/garak/fb-real.hitlog.jsonl
{"ingested": 668, "total_candidates": 668, "duplicates_marked": 89}
$ [driver step] ingest every prepared real transcript under <DATA_DIR>/prepared/ (--grammar human-assistant; facts via --environment from the sidecars)
40 files: ingested 40, refused 0
$ [driver step] count candidates by source, duplicates, sealed probes and responses, source facts (metadata only)
candidates: 708 by source {'garak': 668, 'manual-transcript': 40}; marked duplicate: 89; probe sealed: 708/708; response sealed: 708/708; with source facts in environment: 708/708
```

## What changed from example 04, and what did not

| | Example 04 (garak 0.16.0) | Example 05 (garak 0.17.0) |
|---|---|---|
| Hitlog records in the recorded shape | 699 of 699 | 668 of 668 |
| Refused or lost | 0 | 0 |
| Attack prompts and responses sealed | 739 of 739 | 708 of 708 |
| Emitted files' field structure | reference | the same |
| Real-string leak scan | CLEAN (4,784 real texts) | CLEAN (4,567 real texts) |
| garak hits | 699 | 668 |
| Exact duplicates | 62 | 89 |

The tool did the same work on both garak versions, with no code change.
The counts differ because the runs differ, not because the tool does.

## The two controls that make this example publishable

1. `tools/fixture_scan.py` sweeps `output/` for sentinel strings, as for
   every example.
2. `tools/realdata_leak_scan.py`: at run time it reads this example's
   local real data, samples 5,000 distinct windows of the real prompts
   and responses (from 4,567 real texts), and searches every committed
   artifact for any of them. The strings are never written anywhere.
   Result on this output: `REAL-STRING SCAN: CLEAN`. The runner hands the
   scan this example's own data folder (D-097), so it cannot check this
   output against example 04's data by mistake.

What the scan does not prove: that no transformed form (paraphrase,
hash, re-encoding) leaked. It proves no verbatim window of the sampled
real text appears in anything committed.

## What real data found

No new product finding (D-094). One error in this project's own record:
the example 04 evidence said triggers were null on all 699 hits, and 389
were (C-014). Evidence: `evidence/real-data-garak-0.17.0.md`.

## Reproduce (Windows CMD)

```
set FB_REALDATA_DIR=%LOCALAPPDATA%\finding-bridge-realdata-garak-0.17.0
set FB_GARAK_PYTHON=<python.exe of a venv with garak 0.17.0>
python examples/04-real-data/fetch.py
python examples/04-real-data/run_garak.py
python tools/realdata_leak_scan.py examples/05-real-data-garak-0.17.0/output
set FB_REALDATA_DIR=
python examples/run_example.py 05-real-data-garak-0.17.0 --check
```

`run_garak.py` needs Ollama with `llama3.2:1b`; a fresh run gives
different hits. `--check` compares a fresh re-run to the committed
artifacts after normalising key-, clock- and operator-derived fields
(PROV-3, D-072). It reads this example's folder (or
`%FB_REALDATA_DIR_05%`); without the local data, the audit test for this
example skips and says so.
