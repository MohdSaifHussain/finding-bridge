# Example 01: triage a garak hitlog

The everyday case. A garak run produced a hitlog. You want the hits
sealed, deduplicated, confirmed by a person, and emitted into the formats
your team already reads.

Everything here is synthetic (D-012). The "harmful" text in
`input/garak.synthetic.hitlog.jsonl` is a labeled stand-in such as
`SENTINEL-HARM-7001`, never real model output. `input/garak.hostile.hitlog.jsonl`
carries values that cannot be hashed (NaN, Infinity, an integer beyond
2^53) so you can watch the tool refuse them.

## What happens

1. Ingest the hitlog. Three hits become three candidates; two are the
   same content, so one is marked as a duplicate of the other.
2. List the candidates. Each shows a safe metadata preview, not the
   content.
3. Confirm one. Your git identity is recorded as the confirmer.
4. Two refusals on purpose: confirm an id that does not exist, and
   ingest the hostile hitlog. Each refusal names its reason code and the
   location, never the value.
5. Verify the chain, then emit the packet, the SARIF, the tracker JSON
   and the provisional FLARE-AI report set.

## Commands

Run from this folder. Put the store and the key OUTSIDE the repository
(the tool refuses a key inside it). On Windows CMD use `%TEMP%` in place
of `/tmp`.

```
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key ingest-garak input/garak.synthetic.hitlog.jsonl
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key list
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key confirm <id-from-list>
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key confirm fb-0000000000000000
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key ingest-garak input/garak.hostile.hitlog.jsonl
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key verify
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key emit-markdown output/packet.md
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key emit-sarif output/findings.sarif --artifact-uri-base examples/01-garak-triage/output
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key emit-tracker output/findings.tracker.json
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key emit-flare output/findings.flare.json
```

Or run the whole thing exactly as the committed artifacts were produced:

```
python examples/run_example.py 01-garak-triage
```

## What is committed under output/

The real artifacts of a real run on 2026-08-25, unedited:

| File | What it is |
|---|---|
| `run-transcript.md` | every command, its output and its exit code, refusals included |
| `packet.md` | the Markdown finding packet |
| `findings.sarif` and `findings.fb.jsonl` | SARIF 2.1.0 and the findings artifact its locations point at; the locations are repository-rooted (`--artifact-uri-base`, `%SRCROOT%`) so GitHub code scanning renders them as alerts against this folder's committed record (F-15) |
| `findings.tracker.json` | generic tracker issues (Jira, Linear, GitHub Issues shaped) |
| `findings.flare.json` | the PROVISIONAL FLARE-AI report set |

None of these files contains sealed content. `tools/fixture_scan.py`
checks that: it fails if a `SENTINEL-HARM` string appears in any output
artifact.

`python examples/run_example.py 01-garak-triage --check` re-runs the
commands into a scratch folder and compares against these files after
normalising the fields that derive from the store key, the clock and the
operator (ids, refs, digests, hashes, timestamps, identity). It does not
prove byte identity; the driver's docstring says exactly what it proves.

## The two refusals, and why they are here

```
$ finding-bridge confirm fb-0000000000000000
unknown-id: no candidate with id 'fb-0000000000000000'
[exit 1]

$ finding-bridge ingest-garak input/garak.hostile.hitlog.jsonl
invalid-hitlog: line 1, field score: non-finite number is not representable in canonical form (value withheld per D-036)
[exit 1]
```

A tool that handles harmful content is judged by how it fails at least as
much as by how it succeeds. Both refusals name a reason code and a
location. Neither echoes the offending value, because an offending value
in a hitlog sits next to model output.
