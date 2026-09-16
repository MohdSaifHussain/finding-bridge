# Example 05: real data on garak 0.17.0, the sealing feature demonstrating itself

This is example 04's real-data drill, run again on garak 0.17.0. Its
inputs are real: a garak run this project did not script, against a real
model, and real red-team transcripts written by people attacking real
models. Example 04 keeps the first run (garak 0.16.0, 2026-08-25); this
example holds the second (garak 0.17.0, 2026-09-16), with its own data.

## What is NOT here, and where it is

D-012 is absolute: no real harmful content is committed to this
repository, in any file, in any form. The inputs live OUTSIDE the tree,
at `DATA_DIR` (for this example `%LOCALAPPDATA%\finding-bridge-realdata-garak-0.17.0`,
or `$FB_REALDATA_DIR_05`), produced by example 04's two committed scripts,
which carry the source, the checksum and the exact command, run with
`FB_REALDATA_DIR` set to this example's folder:

- `examples/04-real-data/fetch.py` downloads Anthropic's
  `red-team-attempts` file from the hh-rlhf dataset (MIT; sha256 pinned in
  the script, 15,483,307 bytes, 38,961 transcripts), verifies it, and
  writes the same fixed sample of 40 transcripts unchanged under
  `DATA_DIR/prepared/`, each with a sidecar of its facts.
- `examples/04-real-data/run_garak.py` runs garak 0.17.0 (its own venv,
  named by `FB_GARAK_PYTHON`) against `llama3.2:1b` on the local Ollama
  server (dan and promptinject families, 1 generation, 45-minute box) and
  leaves the hitlog under `DATA_DIR/garak/`.

What IS committed under `output/` is the product's own answer to the
tension: the run transcript with ingestion counts, sealed previews, dedup
results and verify output, and the four emitted artifacts, whose whole
design claim is that they carry preview and metadata and never raw harm.

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

A weak 1B target was chosen on purpose: more hits, more real content
for the seal to hold against. These rates are not comparable one to one
with example 04: the model samples, so a fresh run gives different hits,
and garak 0.17.0 passes generation settings (such as a response length
cap) to Ollama, which 0.16.0 did not.

Then the pipeline (`output/run-transcript.md`, complete and unedited):

```
$ finding-bridge ingest-garak <DATA_DIR>/garak/fb-real.hitlog.jsonl
{"ingested": 668, "total_candidates": 668, "duplicates_marked": 89}
$ [driver step] ingest every prepared real transcript under <DATA_DIR>/prepared/ (--grammar human-assistant; facts via --environment from the sidecars)
40 files: ingested 40, refused 0
$ [driver step] count candidates by source, duplicates, sealed probes and responses, source facts (metadata only)
candidates: 708 by source {'garak': 668, 'manual-transcript': 40}; marked duplicate: 89; probe sealed: 708/708; response sealed: 708/708; with source facts in environment: 708/708
```

**Same tool, new garak version, the numbers that prove it:** every one of
the 668 hits has the hitlog shape garak 0.16.0 wrote; nothing was refused
or lost; the attack prompt and the response are sealed on **708 of 708**
candidates (668 garak, 40 transcripts), as they were on 739 of 739 in
example 04; and the emitted files have the same field structure as
example 04's. No code changed between the two runs. The hit and duplicate
counts moved (699 to 668, 62 to 89) because the runs differ, not because
the tool does.

**The sealing claim held on new real content:** both scans were run by
the builder on this run (fixture scan conforming; real-string scan clean,
5,000 sampled strings from 4,567 real texts).

The refusal in this example is real too: the raw 15 MB dataset archive
fed to `ingest-garak` refuses with `input-too-large` at the 10 MiB cap,
location named, nothing read past the limit.

## The two controls that make this example publishable

1. `tools/fixture_scan.py` sweeps `output/` for sentinel strings, as for
   every example.
2. `tools/realdata_leak_scan.py`, the stronger one: at run time it reads
   the local real data, samples 5,000 distinct windows of the real
   prompts and responses (from 4,567 real texts), and searches every
   committed artifact for any of them. The strings are never written
   anywhere. Result on this output: `REAL-STRING SCAN: CLEAN`. The scan
   reads the data of the example whose output it scans, found by the
   example folder's name, so a plain scan of this output reads this
   example's data, not example 04's (D-099). Its selftest plants a string
   and must find it; a clean file must stay clean.

So the seal is shown holding against real content, not only against
sentinels. What that scan does not prove: that no transformed form
(paraphrase, hash, re-encoding) leaked. It proves no verbatim window of
the sampled real text appears in anything committed.

## What real data found (findings for the director, evidence/real-data-garak-0.17.0.md)

- **No new product finding** (D-094): 668 of 668 real hitlog records have
  the recorded shape, nothing was refused or lost, and everything that
  should be sealed is sealed.
- **C-014**, an error in this project's own record: the example 04
  evidence said triggers were null on all 699 hits; 389 were.

## Reproduce

```
set FB_REALDATA_DIR=%LOCALAPPDATA%\finding-bridge-realdata-garak-0.17.0
python examples/04-real-data/fetch.py
python examples/04-real-data/run_garak.py        (needs Ollama with llama3.2:1b, and garak 0.17.0 named by FB_GARAK_PYTHON; a fresh run gives different hits)
python examples/run_example.py 05-real-data-garak-0.17.0
python examples/run_example.py 05-real-data-garak-0.17.0 --check
python tools/realdata_leak_scan.py examples/05-real-data-garak-0.17.0/output
```

`--check` compares a fresh re-run to the committed artifacts after
normalising key-, clock- and operator-derived fields (PROV-3, D-072). It
needs the local data; without it, the audit test for this example skips
and says so.
