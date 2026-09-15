# Run transcript: 05-real-data-garak-0.17.0

Complete, unedited output of `python examples/run_example.py 05-real-data-garak-0.17.0`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-garak <DATA_DIR>/garak/fb-real.hitlog.jsonl
{"ingested": 668, "total_candidates": 668, "duplicates_marked": 89}
[exit 0]

$ [driver step] ingest every prepared real transcript under <DATA_DIR>/prepared/ (--grammar human-assistant; facts via --environment from the sidecars)
40 files: ingested 40, refused 0
[driver step done]

$ [driver step] count candidates by source, duplicates, sealed probes and responses, source facts (metadata only)
candidates: 708 by source {'garak': 668, 'manual-transcript': 40}; marked duplicate: 89; probe sealed: 708/708; response sealed: 708/708; with source facts in environment: 708/708
[driver step done]

$ [driver step] list: the first 5 lines of N (safe metadata previews only)
fb-fbaea81d891a6f01  garak  [sealed content: 685 chars, 1 lines, keyed digest c1fe672a; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-67644e775c67758d  garak  [sealed content: 640 chars, 1 lines, keyed digest f26b8c6a; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-8b9e8b75f586186c  garak  [sealed content: 710 chars, 1 lines, keyed digest 122e94b0; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-8a60dc3ed571b389  garak  [sealed content: 700 chars, 1 lines, keyed digest 0f6fc040; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-740963c0aa3fa0d1  garak  [sealed content: 312 chars, 1 lines, keyed digest a2f1916f; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
... 708 lines in total
[driver step done]

$ finding-bridge confirm fb-fbaea81d891a6f01
confirmed fb-fbaea81d891a6f01 by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
[exit 0]

$ finding-bridge ingest-garak <DATA_DIR>/red_team_attempts.jsonl.gz
input-too-large: red_team_attempts.jsonl.gz exceeds the 10485760-byte input cap (read stopped at the limit; a configurable cap is addable later)
[exit 1]

$ finding-bridge verify
chain verifies clean
[exit 0]

$ finding-bridge emit-markdown output/packet.md
wrote output/packet.md
[exit 0]

$ finding-bridge emit-sarif output/findings.sarif --artifact-uri-base examples/05-real-data-garak-0.17.0/output
wrote output\findings.sarif and output\findings.fb.jsonl
[exit 0]

$ finding-bridge emit-tracker output/findings.tracker.json
wrote output/findings.tracker.json (1 issue(s))
[exit 0]

$ finding-bridge emit-flare output/findings.flare.json
wrote output/findings.flare.json (PROVISIONAL mapping; see the provisional block)
[exit 0]

$ [driver step] real-string leak scan of every emitted artifact (tools/realdata_leak_scan.py)
REAL-STRING SCAN: CLEAN (5000 sampled strings from 4567 real texts, 5 artifacts searched)
[exit 0]
[driver step done]

```
