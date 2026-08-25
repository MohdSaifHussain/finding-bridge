# Example 02: capture a manual attack transcript

The by-hand case. An analyst attacked a model in a chat window and saved
the conversation. You want the last exchange sealed and stamped, the
probe and the response referenced but never inlined, and an explicit,
logged unseal when someone must read it.

Everything here is synthetic (D-012). `input/attack.txt` is a five-turn
transcript in the text format (exact uppercase `USER:`, `ASSISTANT:`,
`SYSTEM:` markers at line start). `input/attack.json` is the same idea in
the JSON format. `input/malformed.txt` has a mixed-case marker
(`Assistant:`) at line start, which the tool refuses rather than guessing
whether it is a turn boundary or content (D-049).

## What happens

1. Ingest the text transcript, naming the target model. One candidate.
2. Ingest the JSON transcript. A second candidate.
3. Refusal on purpose: ingest the malformed transcript. The reason names
   the line and the shape of the problem, never the text.
4. List, confirm one, verify, emit the packet and the SARIF.
5. Unseal the confirmed response WITHOUT `--explicit`: refused.
6. Unseal it WITH `--explicit`: the synthetic content comes back, and the
   exposure log gains two rows, an attempt and its outcome (D-022).
7. Read the exposure log back.

## Commands

Run from this folder, store and key outside the repository.

```
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key ingest-transcript input/attack.txt --target-model synthetic-model
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key ingest-transcript input/attack.json
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key ingest-transcript input/malformed.txt
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key list
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key confirm <id-from-list>
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key verify
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key emit-markdown output/packet.md
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key emit-sarif output/findings.sarif
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key unseal <response-ref-from-packet>
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key unseal <response-ref-from-packet> --explicit
```

Then read `/tmp/fb/store/sealed/exposure_log.jsonl`.

Or: `python examples/run_example.py 02-transcript-capture`.

## What is committed under output/

`run-transcript.md` (complete, unedited, including the explicit unseal
and the exposure log read back), `packet.md`, `findings.sarif`,
`findings.fb.jsonl`. The one place a `SENTINEL-HARM` string appears in
this folder's output is the line after the `--explicit` unseal in the
transcript, which is the point: `tools/fixture_scan.py` allows it there
and nowhere else.

## The refusals

```
$ finding-bridge ingest-transcript input/malformed.txt
invalid-transcript: line 2: suspected marker that is not the exact token (check case, spaces or tabs before the colon, a full-width colon, or indentation; markers are exact uppercase USER:/ASSISTANT:/SYSTEM: at line start); value withheld per D-036
[exit 1]

$ finding-bridge unseal sealed/<ref>
unseal-not-explicit: unseal of 'sealed/<ref>' requires explicit=True (charter: unsealing is always explicit and logged)
[exit 1]
```

The first refuses to guess where a turn begins, because a quiet
misattribution changes which turn is sealed as the probe. The second is
the charter's rule that reading harmful content is a deliberate act.
