# Run transcript: 02-transcript-capture

Complete, unedited output of `python examples/run_example.py 02-transcript-capture`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-transcript input/attack.txt --target-model synthetic-model
{"ingested": 1, "total_candidates": 1, "duplicates_marked": 0}
[exit 0]

$ finding-bridge ingest-transcript input/attack.json
{"ingested": 1, "total_candidates": 2, "duplicates_marked": 0}
[exit 0]

$ finding-bridge ingest-transcript input/malformed.txt
invalid-transcript: line 2: suspected marker that is not an exact token of the user-assistant grammar (check case, spaces or tabs before the colon, a full-width colon, indentation, or a marker from the other grammar; the user-assistant markers are USER:/ASSISTANT:/SYSTEM: at line start); value withheld per D-036
[exit 1]

$ finding-bridge list
fb-2ca4ee930b9e9bb1  manual-transcript  [sealed content: 43 chars, 1 lines, keyed digest 4af2f6e4; harm flags: none recorded. Content is sealed; unseal is explicit and logged.]
fb-d3dbfa57b87b8ebd  manual-transcript  [sealed content: 53 chars, 1 lines, keyed digest 1fdd2060; harm flags: none recorded. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ finding-bridge confirm fb-2ca4ee930b9e9bb1
confirmed fb-2ca4ee930b9e9bb1 by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
[exit 0]

$ finding-bridge verify
chain verifies clean
[exit 0]

$ finding-bridge emit-markdown output/packet.md
wrote output/packet.md
[exit 0]

$ finding-bridge emit-sarif output/findings.sarif
wrote output\findings.sarif and output\findings.fb.jsonl
[exit 0]

$ finding-bridge unseal sealed/4af2f6e4cd8d1099
unseal-not-explicit: unseal of 'sealed/4af2f6e4cd8d1099' requires explicit=True (charter: unsealing is always explicit and logged)
[exit 1]

$ finding-bridge unseal sealed/4af2f6e4cd8d1099 --explicit
SENTINEL-HARM-E2b second synthetic stand-in
[exit 0]

$ [driver step] read the exposure log
{"actor": "MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>", "at": "2026-08-25T09:41:05.767898+00:00", "ref": "sealed/4af2f6e4cd8d1099", "row": 1, "type": "attempt"}
{"at": "2026-08-25T09:41:05.784434+00:00", "attempt_row": 1, "outcome": "succeeded", "row": 2, "type": "outcome"}
[driver step done]

```
