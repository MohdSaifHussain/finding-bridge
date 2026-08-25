# W6c real-data validation, evidence (2026-08-25)

Ordered at STEP-06 stop two (D-078, DEV-21). Everything below was run on
the development machine; the data lives at DATA_DIR outside the tree and
is never committed (D-012). Counts and metadata only, never content.

## Target, verified before the run

```
$ ollama list
llama3.2:1b    baf6a787fdff    1.3 GB
qwen3:4b       359d7dd4bcda    2.5 GB
$ curl http://localhost:11434/api/generate -d '{"model":"llama3.2:1b","prompt":"Reply with the single word OK.","stream":false}'
response: OK | model: llama3.2:1b | eval_count: 2
$ curl http://localhost:11434/api/version
{"version":"0.32.15"}
```

## garak 0.16.0 (own venv), sources fetched the same day

`garak/cli.py` and `garak/generators/ollama.py` at tag v0.16.0 from
raw.githubusercontent.com/NVIDIA/garak: `--probes` deprecated since
0.15.1 in favour of `--spec`; the Ollama generator defaults to host
127.0.0.1:11434 with a 30 s timeout. `garak/evaluators/base.py` at the
same tag is the hitlog writer (keys goal, prompt, output, triggers,
score, run_id, attempt_id, attempt_seq, attempt_idx, generator, probe,
detector, generations_per_prompt). The readthedocs pages are
script-rendered and returned no text; the sources are the citation.

Command (examples/04-real-data/run_garak.py), started 2026-08-25T08:05:51Z,
ended 08:14:24Z, box 2,700 s, garak's own clock 505.51 s, exit 0:

```
python -m garak --target_type ollama --target_name llama3.2:1b --spec probes.dan,probes.promptinject --generations 1 --report_prefix <DATA_DIR>/garak/fb-real
```

Probes queued by garak's defaults for the two families:
dan.Ablation_Dan_11_0, dan.AutoDANCached, dan.DanInTheWild,
promptinject.HijackHateHumans, promptinject.HijackKillHumans,
promptinject.HijackLongPrompt. Per-probe results are in
examples/04-real-data/README.md. Files left: fb-real.hitlog.jsonl
(1,941,223 bytes, 699 lines), fb-real.report.jsonl (11,030,511 bytes),
fb-real.report.html (1,783,050 bytes).

Real hitlog shape (every one of the 699 records): prompt =
`{"turns": [{"role": "user", "content": {"text", "lang", "data_path",
"data_type", "data_checksum", "notes"}}], "notes": {...}}`; output = a
Message with the same six keys; triggers null on all; generator
"ollama llama3.2:1b"; generations_per_prompt 1.

## The published dataset

Anthropic/hh-rlhf, `red-team-attempts/red_team_attempts.jsonl.gz`
(https://huggingface.co/datasets/Anthropic/hh-rlhf, license MIT per the
dataset card, fetched 2026-08-25): 15,483,307 bytes, sha256
4c7b0069991460f0064f279fd400b51f3f0095697d14d7793c49b0925f80814f, a
JSON array of 38,961 records with keys transcript,
min_harmlessness_score_transcript, num_params, model_type, rating,
task_description, task_descripton_harmlessness_score, red_team_member_id,
is_upworker, tags; transcript length 40 to 5,630 chars (median 839);
markers `\n\nHuman:` 127,217 and `\n\nAssistant:` 127,321 occurrences,
`USER:` 0.

Alternatives evaluated the same day (HF API): TrustAIRLab/in-the-wild-
jailbreak-prompts (MIT, four parquet configs, prompts only) and
JailbreakBench/JBB-Behaviors (MIT, behaviour CSVs, goals only). Chosen:
the Anthropic set, the only one carrying real model RESPONSES, which is
what the transcript adapter seals.

Sample: 40 transcripts, indices drawn with seed 20260825, markers
rewritten to the adapter's grammar (finding F-10), written under
DATA_DIR/prepared/.

## Ingest

Snapshot at 197 hits (mid-run), then the full 699 through the example:

First pass (before D-079, prompts silently null):

```
{"ingested": 699, "total_candidates": 699, "duplicates_marked": 253}
40 files: ingested 40, refused 0
candidates: 739 by source {'garak': 699, 'manual-transcript': 40}; marked duplicate: 253
```

Second pass, after D-079/D-080/D-081, the transcripts ingested unchanged
with `--grammar human-assistant` and their facts via `--environment`:

```
{"ingested": 699, "total_candidates": 699, "duplicates_marked": 62}
40 files: ingested 40, refused 0
candidates: 739 by source {'garak': 699, 'manual-transcript': 40}; marked duplicate: 62; probe sealed: 739/739; response sealed: 739/739; with source facts in environment: 739/739
```

Before/after: probe sealed 0/699 to 739/739. Duplicates 253 to 62: the
first figure was inflated by the bug (dedup keyed on responses alone);
recorded as C-011.

Refusal on real input: the 15 MB archive refuses `input-too-large` at
the 10 MiB cap. Verify clean. Four emitters emitted. The committed
transcript shows `<DATA_DIR>` in place of the local path (the pre-push
audit bans local paths).

## Controls

- fixture_scan: CONFORMING, 18 example outputs leak-checked.
- realdata_leak_scan: CLEAN, 5,000 sampled windows from 4,784 real
  texts (garak prompts, outputs, goals; prepared transcript turns),
  6 artifacts searched; selftest ok.
- showcase --check: SAME after normalising volatile fields, 6 files.
- Local-path grep over output/: none.

## Findings

F-10, F-11, F-12, F-13 in evidence/step06-findings.md. F-12 (prompt
silently lost on the real 0.16.0 hitlog) is the defect this workstream
existed to find.

## Limits

One target model, one machine, one garak version, one dataset sample of
40; the garak hitlog is one run's hits and a fresh run gives different
ones (the committed artifacts are compared modulo the volatile list, not
byte-for-byte). The leak scan proves absence of verbatim windows, not of
transformed content.
