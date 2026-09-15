# Run transcript: 04-real-data

Complete, unedited output of `python examples/run_example.py 04-real-data`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-garak <DATA_DIR>/garak/fb-real.hitlog.jsonl
{"ingested": 699, "total_candidates": 699, "duplicates_marked": 62}
[exit 0]

$ [driver step] ingest every prepared real transcript under <DATA_DIR>/prepared/ (--grammar human-assistant; facts via --environment from the sidecars)
40 files: ingested 40, refused 0
[driver step done]

$ [driver step] count candidates by source, duplicates, sealed probes and responses, source facts (metadata only)
candidates: 739 by source {'garak': 699, 'manual-transcript': 40}; marked duplicate: 62; probe sealed: 739/739; response sealed: 739/739; with source facts in environment: 739/739
[driver step done]

$ [driver step] list: the first 5 lines of N (safe metadata previews only)
fb-08ffda1ca7b0f5b8  garak  [sealed content: 16 chars, 1 lines, keyed digest 5b55cb71; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-ee8c59033d619b20  garak  [sealed content: 1208 chars, 8 lines, keyed digest 3f3c5688; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-af04b8dfa948262d  garak  [sealed content: 646 chars, 3 lines, keyed digest a9dba8f1; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-9733f84b885863d1  garak  [sealed content: 840 chars, 3 lines, keyed digest 20c6e7da; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-bd6ca81034055d15  garak  [sealed content: 234 chars, 1 lines, keyed digest 072a2402; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
... 739 lines in total
[driver step done]

$ finding-bridge confirm fb-08ffda1ca7b0f5b8
confirmed fb-08ffda1ca7b0f5b8 by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
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

$ finding-bridge emit-sarif output/findings.sarif --artifact-uri-base examples/04-real-data/output
wrote output\findings.sarif and output\findings.fb.jsonl
[exit 0]

$ finding-bridge emit-tracker output/findings.tracker.json
wrote output/findings.tracker.json (1 issue(s))
[exit 0]

$ finding-bridge emit-flare output/findings.flare.json
wrote output/findings.flare.json (PROVISIONAL mapping; see the provisional block)
[exit 0]

$ [driver step] real-string leak scan of every emitted artifact (tools/realdata_leak_scan.py)
REAL-STRING SCAN: CLEAN (5000 sampled strings from 4784 real texts, 5 artifacts searched)
[exit 0]
[driver step done]

```
