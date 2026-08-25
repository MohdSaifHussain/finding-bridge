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
fb-b1ed01896d82ccee  manual-transcript  [sealed content: 43 chars, 1 lines, keyed digest 22392ff0; harm flags: none recorded. Content is sealed; unseal is explicit and logged.]
fb-cae592ce29c678be  manual-transcript  [sealed content: 53 chars, 1 lines, keyed digest c8c01f8e; harm flags: none recorded. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ finding-bridge confirm fb-b1ed01896d82ccee
confirmed fb-b1ed01896d82ccee by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
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

$ finding-bridge unseal sealed/22392ff08267bf5c
unseal-not-explicit: unseal of 'sealed/22392ff08267bf5c' requires explicit=True (charter: unsealing is always explicit and logged)
[exit 1]

$ finding-bridge unseal sealed/22392ff08267bf5c --explicit
SENTINEL-HARM-E2b second synthetic stand-in
[exit 0]

$ [driver step] read the exposure log
{"actor": "MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>", "at": "2026-08-25T12:09:37.942277+00:00", "ref": "sealed/22392ff08267bf5c", "row": 1, "type": "attempt"}
{"at": "2026-08-25T12:09:37.959904+00:00", "attempt_row": 1, "outcome": "succeeded", "row": 2, "type": "outcome"}
[driver step done]

```
