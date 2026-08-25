# finding-bridge usage guide

This guide is for someone who has never used finding-bridge. It covers
install, every command, the reason codes, and the limits.

All examples use the synthetic fixture files in the repo. The "harmful"
text in them is fake. Strings like `SENTINEL-HARM-7001` are labeled
stand-ins, not real model output.

## Install

Python 3.12 or newer.

```
pip install -e .
```

For a hash-verified install, build a wheel first:

```
pip install build
python -m build --wheel
pip install dist/finding_bridge-0.1.0-py3-none-any.whl -c constraints.txt
```

`constraints.txt` pins the exact hash of `rfc8785`, the library that does
canonical hashing. It sits inside the hash path, so its version is locked.
`pip` cannot hash-check an install from a source directory, which is why
the verified route uses a wheel. Either route installs the same pinned
version (0.1.4).

## How the pipeline works

A finding moves through five stages:

1. **Ingest.** Read a source file. Turn each item into a candidate.
2. **Seal.** Encrypt the harmful content. Store a safe metadata preview.
3. **Stamp.** Add hashes and chain the record.
4. **Confirm.** A human accepts or rejects each candidate. This is the
   gate. Nothing is confirmed without it.
5. **Emit.** Write confirmed findings to Markdown or SARIF.

Your work lives in a store directory (default `.fb-store`). The sealing
key lives outside the repo (default `~/.finding-bridge/fb.key`). The key
is never committed.

## Commands

### Ingest a garak hitlog

```
finding-bridge ingest-garak schemas/fixtures/garak.synthetic.hitlog.jsonl
```

Prints a summary, for example:
`{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}`.

### Ingest a transcript

A transcript is a saved copy of an attack conversation. Two formats work:

- **Text.** Each turn starts at the line start with `USER:`,
  `ASSISTANT:`, or `SYSTEM:`. The marker must be exact and uppercase.
- **JSON.** `{"messages": [{"role": "...", "content": "..."}]}`.

```
finding-bridge ingest-transcript schemas/fixtures/transcript.simple.txt
finding-bridge ingest-transcript - < my-transcript.txt   # from stdin
```

Optional flags: `--target-model`, `--target-model-version`,
`--discovered-at` (ISO 8601). If you do not know a value, leave it out.
The tool never guesses.

### List candidates

```
finding-bridge list
```

Shows each candidate's id, source, and safe preview. Duplicates are
marked.

### Confirm or reject (the human gate)

```
finding-bridge confirm <id>
finding-bridge reject <id>
```

Confirm records who you are, from `git config user.name` and
`user.email`. Set both first, or confirm will refuse.

### Verify the chain

```
finding-bridge verify
```

Prints `chain verifies clean`, or lists any tampering it finds.

### Emit

```
finding-bridge emit-markdown out/packet.md
finding-bridge emit-sarif out/findings.sarif
finding-bridge emit-flare out/findings.flare.json
finding-bridge emit-tracker out/findings.tracker.json
```

SARIF writes a second file next to it: `findings.fb.jsonl`. The SARIF
location points at a line in that file. Both emitters create the output
folder if it does not exist.

No output contains sealed content. They carry the preview, metadata, and
references only.

`emit-flare` writes a FLARE-AI style report set. It is marked
**PROVISIONAL** inside the file, at both the report-set and report level.
FLARE-AI has not published a machine-readable schema, so this mapping
comes from the field names in the FLARE-AI paper. Check the field names
before you submit anything based on it.

`emit-tracker` writes a flat JSON array of issues shaped for generic
tracker import (Jira, Linear, GitHub Issues). Common fields are at the top
level; anything tool-specific sits under `fields`. An unscored finding
gets priority `Unset` rather than a guess, and a suggested taxonomy label
carries a `?` so it cannot pass for a confirmed one.

### Ask the caged AI for suggestions (optional)

```
pip install -e ".[ai]"
set ANTHROPIC_API_KEY=...
finding-bridge confirm <id> --ai --ai-model <exact-model-id>
```

The AI can suggest two things: a severity rationale, and taxonomy
mappings. Both are **printed for you to weigh, never written**. You accept
or reject by hand; nothing the AI says enters a finding on its own.

What the AI sees: the safe metadata preview, the source tool, the target
model, and the harm flags. **It never sees sealed content.** If you want
it to see the actual text, you must unseal that text yourself first
through the explicit, logged `unseal` path and pass it in deliberately.

If the key is missing or the API is unreachable, the tool says so and
**carries on exactly as it would without `--ai`**. The deterministic
pipeline never depends on the AI.

### Rotate the encryption key

```
finding-bridge rotate-key --reason "quarterly rotation"
```

This re-encrypts every sealed blob under a fresh encryption key and
records the event in the ledger as a **supersession record**: what
happened, who confirmed it, both chain heads, and an attestation over all
of it. `verify` then walks through that record, so history stays checkable
across the change.

Your finding ids do not change. The reference key that produces sealed
references is separate from the encryption key and is **not** rotated.

**Limit, stated plainly: the reference key is permanent.** Rotating it
would change every sealed reference, content hash and finding id in the
store. That is possible in principle through the same supersession
mechanism, but it is not implemented and it is not free.

### Unseal (explicit and logged)

```
finding-bridge unseal <ref> --explicit
```

Unsealing needs the `--explicit` flag. Every unseal writes a log row:
who, when, which reference. This is by design. Reading harmful content is
a deliberate act.

## Reason codes

Every refusal prints a reason code and a short reason. The reason names
the location (file, line, field), never the content. Exit code is 1 on a
refusal.

| Reason code | What happened | What to do |
|---|---|---|
| `invalid-hitlog` | The garak file is not valid, or has a number that cannot be hashed (NaN, Infinity, huge integer) | Check the named line. Fix the source file. |
| `invalid-transcript` | The transcript is malformed: no marker, content before the first marker, bad JSON, or a lowercase/mixed-case marker at line start | Check the named line. Use exact uppercase markers, or the JSON format. |
| `input-too-large` | The input is over 10 MiB | Split the file. This is not a paste-sized input. |
| `unsupported-encoding` | The input is not UTF-8 | Re-save the file as UTF-8. |
| `input-unreadable` | The input file is missing, is a folder, or cannot be opened | Check the path. |
| `output-unwritable` | The output path cannot be written (for example, a parent is a file) | Pick a writable path. |
| `unknown-id` | No candidate has that id | Run `list` to see current ids. |
| `unconfirmed` | You tried to emit a finding that is not confirmed | Confirm it first. |
| `identity-missing` | `git config user.name` or `user.email` is not set | Set both, then confirm. |
| `unseal-not-explicit` | You ran `unseal` without `--explicit` | Add `--explicit`. Unsealing is deliberate. |
| `key-inside-repo` | The sealing key path is inside the repo | Move the key outside the repo. It must never be committed. |
| `store-unreadable` | A store file is corrupt | Check the named file. |
| `head-missing` | The ledger exists but its head record is gone | The store is damaged. Restore from a backup. |
| `schema-invalid` | A finding does not match the canonical schema | Usually a tool bug. Report it. |

Other codes exist for internal integrity checks (tamper detection,
sealing errors). You will only see them if a store is damaged or edited by
hand. They all mean: stop and check the store.

## Limits

Plain statements of what this tool does not do.

- **The preview is metadata, not a summary.** It shows length, line count,
  a keyed digest, and harm flags. It does not describe the content. A
  content summary would need AI, and no AI is allowed in this pipeline. A
  future opt-in `--ai` flag may add a suggested summary; it does not exist
  yet.
- **Tamper-evidence has a bound.** The hash chain and its head catch
  accidents, drift, and casual edits. They do not defend against an
  attacker with write access to both the ledger and its head at once.
- **Finding ids are local to one store.** The same input in two stores
  produces different ids. You cannot match findings across stores by id
  today.
- **Duplicate detection is exact-match only.** Two findings with identical
  evidence are merged. Similar-but-different findings are not clustered.
- **Input is capped at 10 MiB.** A configurable cap may come later.
- **The encryption key rotates; the reference key does not.**
  `rotate-key` rotates the key that encrypts content. The separate key
  that produces sealed references is permanent, because changing it would
  change every reference, hash and id. Losing the reference key means
  losing the link between findings and their sealed content.
- **On Windows, key file permissions are not locked by the tool.** Use
  `icacls` to restrict the key file yourself.
