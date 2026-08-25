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
  38,961 transcripts), verifies it, and rewrites a fixed sample of 40
  transcripts into the adapter's marker grammar under `DATA_DIR/prepared/`.
- `run_garak.py` runs garak 0.16.0 against `llama3.2:1b` on the local
  Ollama server (dan and promptinject families, 1 generation, 45-minute
  box) and leaves the hitlog under `DATA_DIR/garak/`.

What IS committed under `output/` is the product's own answer to the
tension: the run transcript with ingestion counts, sealed previews, dedup
results and verify output, and the four emitted artifacts, whose whole
design claim is that they carry preview and metadata and never raw harm.

## The run, 2026-08-25

garak 0.16.0, 505.51 seconds wall clock (box 2,700 s), six probes,
699 detector hits. garak's own per-probe summary:

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
{"ingested": 699, "total_candidates": 699, "duplicates_marked": 253}
$ [driver step] ingest every prepared real transcript under <DATA_DIR>/prepared/
40 files: ingested 40, refused 0
$ [driver step] count candidates by source, and duplicates (metadata only)
candidates: 739 by source {'garak': 699, 'manual-transcript': 40}; marked duplicate: 253
```

253 of 699 real hits were exact duplicates of another hit's content: a
1B model under jailbreak ablations repeats itself, and the Pain-4
feature (D-025) did what it exists for on real data, first time out.

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
  descends into it. The response sealed fine. Raised for ruling; not
  fixed in this arc.
- **F-10**: the largest public red-team corpus writes `Human:` /
  `Assistant:`; the grammar accepts only `USER:` / `ASSISTANT:` and
  refuses the case variant by design. Every real transcript needed a
  rewrite outside the tree.
- **F-11**: no field for per-record metadata (rating, task, model size).
- **F-13**: `lang`, `notes`, `data_*` on outputs are dropped; `goal` and
  `triggers` are sealed as context.

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
