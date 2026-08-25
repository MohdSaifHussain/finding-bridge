# Run transcript: 04-real-data

Complete, unedited output of `python examples/run_example.py 04-real-data`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-garak <DATA_DIR>/garak/fb-real.hitlog.jsonl
{"ingested": 699, "total_candidates": 699, "duplicates_marked": 253}
[exit 0]

$ [driver step] ingest every prepared real transcript under <DATA_DIR>/prepared/
40 files: ingested 40, refused 0
[driver step done]

$ [driver step] count candidates by source, and duplicates (metadata only)
candidates: 739 by source {'garak': 699, 'manual-transcript': 40}; marked duplicate: 253
[driver step done]

$ [driver step] list: the first 5 lines of N (safe metadata previews only)
fb-9256135319cfa04a  garak  [sealed content: 16 chars, 1 lines, keyed digest a3fdf1be; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-c5015d52b7abca93  garak  [sealed content: 1208 chars, 8 lines, keyed digest b469ac8e; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-7a8fea7665beb9b7  garak  [sealed content: 646 chars, 3 lines, keyed digest f8096391; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-34f6c91a1fe1b78a  garak  [sealed content: 840 chars, 3 lines, keyed digest de4707f1; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
fb-dd244dcc8d310fd7  garak  [sealed content: 234 chars, 1 lines, keyed digest fc3b8997; harm flags: garak-detector:dan.DAN. Content is sealed; unseal is explicit and logged.]
... 739 lines in total
[driver step done]

$ finding-bridge confirm fb-9256135319cfa04a
confirmed fb-9256135319cfa04a by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
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

$ finding-bridge emit-sarif output/findings.sarif
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
