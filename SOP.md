# finding-bridge operations runbook (SOP)

## Document control

| Field | Value |
|---|---|
| Document | finding-bridge SOP, runbook form |
| Owner | Director: Mohd Saif Hussain |
| Escalation point of contact | None. This is a one-operator project. There is nobody to escalate to; the incident path below is what the one operator does. |
| Applies to | finding-bridge at the commit this file ships in; the `finding-bridge --help` command list is the authority for what exists |
| Standard followed | every procedure below was EXECUTED before it was written down (D-057). The captures are from real runs on 2026-08-25 with the store and key in a scratch folder outside the repository. Ids, refs and hashes are store-local; yours will differ. |
| Wording law | D-042: "sealed, with a safe metadata preview". The tamper-evidence bound (OB-4) is stated wherever the guarantee is stated. |
| Review | re-executed at every release; a procedure whose capture no longer matches the tool is a defect in this file |

Conventions: `$STORE` and `$KEY` stand for the two paths every command
takes (`--store $STORE --key $KEY`). Put both OUTSIDE the repository.
The tool refuses a key inside the repo tree (`key-inside-repo`). On
Windows CMD write `%STORE%` and `%KEY%`.

## 0. Install

Developer route: `pip install -e .`. Secure route (hash-verified, the
one CI and the container use): `pip install --require-hashes -r
constraints.txt`, then `pip install --no-deps <wheel>`. The lock file
`constraints.txt` is maintained by `python tools/lock.py`; `--check`
reports drift against PyPI. See README for the full block.

Container route (after the first CI run publishes the image): the store,
the key and your gitconfig are mounted from outside; nothing persists in
the image, and the image carries git because the gate needs it for
identity (F-8):

```
docker run --rm -v "%CD%\store:/work/store" -v "%CD%\key:/home/fb/key" -v "%USERPROFILE%\.gitconfig:/home/fb/.gitconfig:ro" ghcr.io/mohdsaifhussain/finding-bridge --store /work/store --key /home/fb/key/fb.key list
```

## 1. Initialise a workspace

There is no `init` command. The first command that touches a store
creates the store folder and, if the key file does not exist, a fresh
key. Executed:

```
$ finding-bridge list
[exit 0]

$ ls store; ls key dir
sop-key:
fb.key
sop-store:
sealed
```

The key file is JSON with three fields: `keyring_version` (1),
`encryption_keys` (a list, so rotation can hold more than one), and
`ref_key` (permanent, D-053). Values withheld here. Restrict the file:
on POSIX the tool sets mode 0600; on Windows the tool cannot, so run
`icacls %KEY% /inheritance:r /grant:r "%USERNAME%":F` yourself (D-023,
stated limit).

## 2. Ingest each source

Garak hitlog (JSON Lines from a garak run):

```
$ finding-bridge ingest-garak schemas/fixtures/garak.synthetic.hitlog.jsonl
{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
[exit 0]
```

Manual transcript, text format (exact uppercase `USER:`, `ASSISTANT:`,
`SYSTEM:` at line start) or JSON (`{"messages": [{"role", "content"}]}`),
from a file or `-` for stdin. Optional `--target-model`,
`--target-model-version`, `--discovered-at`; leave unknown values out,
the tool never guesses (D-024):

```
$ finding-bridge ingest-transcript input/attack.txt --target-model synthetic-model
{"ingested": 1, "total_candidates": 1, "duplicates_marked": 0}
[exit 0]

$ finding-bridge ingest-transcript input/attack.json
{"ingested": 1, "total_candidates": 2, "duplicates_marked": 0}
[exit 0]
```

What a refused ingest looks like (the location, never the value):

```
$ finding-bridge ingest-garak input/garak.hostile.hitlog.jsonl
invalid-hitlog: line 1, field score: non-finite number is not representable in canonical form (value withheld per D-036)
[exit 1]

$ finding-bridge ingest-transcript input/malformed.txt
invalid-transcript: line 2: suspected marker that is not the exact token (check case, spaces or tabs before the colon, a full-width colon, or indentation; markers are exact uppercase USER:/ASSISTANT:/SYSTEM: at line start); value withheld per D-036
[exit 1]
```

Both files are under `examples/`; the full transcripts are in each
example's `output/run-transcript.md`.

## 3. The human gate, without and with `--ai`

Confirm needs `git config user.name` and `user.email`; it never falls
back to a default identity.

Without `--ai` (the normal path):

```
$ finding-bridge confirm fb-dd05014af88d50fb
confirmed fb-dd05014af88d50fb by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
[exit 0]
```

With `--ai` and NO `ANTHROPIC_API_KEY` set (executed with the variable
scrubbed from the environment):

```
$ finding-bridge confirm fb-169cb15fc1cb7ed7 --ai --ai-model claude-fable-5
[ai] ai-key-missing: ANTHROPIC_API_KEY is not set; --ai suggestions are unavailable and the deterministic pipeline is unaffected
[ai] ai-key-missing: ANTHROPIC_API_KEY is not set; --ai suggestions are unavailable and the deterministic pipeline is unaffected
[ai] accept or reject by hand; nothing above has been recorded
confirmed fb-169cb15fc1cb7ed7 by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
[exit 0]
```

Read that carefully: the AI was unavailable and the confirmation went
through unchanged. With a key set, the two `[ai]` lines become a
suggested severity rationale and suggested taxonomy mappings, printed for
you to weigh; nothing the AI prints is written to the finding. That run
was not captured here because it needs an API key, and this runbook only
shows what was executed without one.

Refusals at the gate:

```
$ finding-bridge reject fb-0000000000000000
unknown-id: no candidate with id 'fb-0000000000000000'
[exit 1]

$ finding-bridge confirm <id>   (with git user.name unset)
identity-missing: git config user.name and user.email must both be set; the gate never falls back to a default identity
[exit 1]
```

## 4. Verify, and the 2am reason-code table

```
$ finding-bridge verify
chain verifies clean
[exit 0]
```

Anything else is exit 1 with one line per failure. What each code means
and what to do first, at 2am, before thinking:

| Reason code | What it means | First action |
|---|---|---|
| `content-tampered` | a confirmed record's content no longer hashes to its stored `content_hash` | STOP. Do not edit anything. Go to section 8. |
| `id-mismatch` | the record's id is not derived from its content hash any more (usually arrives with `content-tampered`) | same |
| `attestation-tampered` | the gate fields (confirmed_by, confirmed_at) or the content were edited after confirmation | same |
| `attestation-missing` | a ledger record has no attestation hash | same; this should be impossible through the tool |
| `attestation-spurious` | a candidate carries an attestation before confirmation | same |
| `chain-broken` | a record's `prev_hash` does not point at the record before it | same |
| `head-mismatch` | `head.json` does not match the last ledger record | same; compare with the backup's head |
| `head-tampered` | `head.json` fails its own integrity check | same |
| `head-missing` | the ledger exists but `head.json` is gone | same; restore `head.json` from backup ONLY if the backup's ledger is byte-identical |
| `supersession-invalid` | a rotation record claims a remap it did not perform, or is malformed | same; this is the rotation join failing |
| `store-unreadable` | a store file is not valid JSON Lines (the detail names file and line) | check for an editor's stray edit or a BOM; go to section 8 if you did not touch it |
| `uncanonicalizable` | a record holds a value RFC 8785 cannot serialise | the store was written by something other than this tool; section 8 |

One hand-tamper produces three codes at once, because three checks fail
for three different reasons (captured in section 7).

## 5. Unseal, with the exposure log read back

Unsealing needs `--explicit`. Without it:

```
$ finding-bridge unseal sealed/653c2b4a5e87356c
unseal-not-explicit: unseal of 'sealed/653c2b4a5e87356c' requires explicit=True (charter: unsealing is always explicit and logged)
[exit 1]
```

With it, the content prints, and the exposure log at
`$STORE/sealed/exposure_log.jsonl` gains two rows, an attempt and its
outcome (D-022, append-only, never edited):

```
$ finding-bridge unseal sealed/653c2b4a5e87356c --explicit
SENTINEL-HARM-E2b second synthetic stand-in
[exit 0]

$ [driver step] read the exposure log
{"actor": "MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>", "at": "2026-08-25T06:35:48.576766+00:00", "ref": "sealed/653c2b4a5e87356c", "row": 1, "type": "attempt"}
{"at": "2026-08-25T06:35:48.591397+00:00", "attempt_row": 1, "outcome": "succeeded", "row": 2, "type": "outcome"}
```

The log is per store. If your organisation tracks analyst exposure,
this file is the record; nothing else in the tool reads harmful content.

## 6. Emit, every format

All four emitters write only confirmed findings, carry the safe metadata
preview and never sealed content, and create the output folder if it is
missing. A destination that cannot be written refuses with
`output-unwritable`.

```
$ finding-bridge emit-markdown output/packet.md
wrote output/packet.md
[exit 0]

$ finding-bridge emit-sarif output/findings.sarif
wrote output/findings.sarif and output/findings.fb.jsonl
[exit 0]

$ finding-bridge emit-tracker output/findings.tracker.json
wrote output/findings.tracker.json (1 issue(s))
[exit 0]

$ finding-bridge emit-flare output/findings.flare.json
wrote output/findings.flare.json (PROVISIONAL mapping; see the provisional block)
[exit 0]
```

SARIF writes the findings artifact (`findings.fb.jsonl`) beside it; the
SARIF locations point at lines in that file, and the SARIF says so in a
disambiguation property (D-033). The FLARE-AI set is marked PROVISIONAL
in the file because FLARE-AI has published no machine-readable schema.

**Known defect, for the director's ruling (finding F-2):** after a key
rotation, `emit-markdown`, `emit-sarif` and `emit-flare` crash on the
supersession record in the ledger; `emit-tracker` skips it. Until ruled
and fixed, emit BEFORE rotating, or use `emit-tracker`. Evidence in
`evidence/step06-findings.md`.

## 7. Backup and restore, and the full rotation walk

The tool has no backup command. A backup is a file copy of TWO things:
the store folder and the key file. The key is not inside the store, and
a store without its key cannot be unsealed. Keep them apart in storage
if your threat model asks for it; keep them together in your backup
procedure.

Executed as the rotation drill (`examples/03-rotation-drill`, driver
steps say what the operator's hands do):

```
$ [driver step] BACKUP: copy the store folder and the key file to backup/
copied store/ and fb.key into backup/ (the key is NOT inside the store; back up both)

$ finding-bridge rotate-key --reason "drill: first rotation"
rotated: supersession recorded, event=key-rotation, remap=0 id(s), confirmed by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
the ref key is permanent and was NOT rotated; ids are unchanged
[exit 0]

$ finding-bridge verify
chain verifies clean
[exit 0]

$ finding-bridge unseal sealed/8bfcd6ac9e9d2316 --explicit
SENTINEL-HARM-7001 synthetic harmful response stand-in, not real model output
[exit 0]

$ finding-bridge rotate-key --reason "drill: second rotation"
rotated: supersession recorded, event=key-rotation, remap=0 id(s), confirmed by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
the ref key is permanent and was NOT rotated; ids are unchanged
[exit 0]

$ finding-bridge verify
chain verifies clean
[exit 0]
```

Rotation re-encrypts every sealed blob under a new encryption key and
records the event in the ledger as a supersession record (D-051,
D-052). `verify` walks through it. Finding ids do not change, because
the reference key is separate and permanent (D-053). **Stated limit: the
reference key is never rotated.** Losing it means losing the link
between findings and their sealed content; that is why the key file is
in the backup.

Restore is the copy in reverse. A restore takes the store back to the
key it had at backup time; if you rotated after the backup, the restored
store uses the OLDER key, and that is correct, because the blobs in the
backup were encrypted under it:

```
$ [driver step] RESTORE: copy backup/ back over the store folder and the key file
store/ and fb.key replaced from backup/ (the backup predates both rotations, so the older key is restored with it)

$ finding-bridge verify
chain verifies clean
[exit 0]
```

Manual equivalents (POSIX; Windows CMD in the drill's README):

```
cp -r $STORE /path/to/backup/store
cp $KEY /path/to/backup/fb.key
rm -r $STORE && cp -r /path/to/backup/store $STORE && cp /path/to/backup/fb.key $KEY
```

Back up before every rotation and before every restore.

## 8. Incident path: `verify` fails and you did not expect it

Executed in the drill by changing one byte inside a confirmed record:

```
$ [driver step] INCIDENT: flip one byte inside the ledger by hand
ledger.jsonl: one byte changed inside a confirmed record (source_tool)

$ finding-bridge verify
attestation-tampered: attestation_hash '982e1776f9aef18aef538107629fa994a9a70071a8c9d28f4b536bd0686999f8' does not match (content_hash, confirmed_by, confirmed_at); the gate record was edited after confirmation
content-tampered: stored content_hash 'f5651adfd090d04c8327f8450ecb221d83160c0757685f6f05143c7ac4ae9c04' != recomputed '5ea3c2e0dab8a1ae36e1aaeda86787b25c83264ce0eaa4feb7e1a8b76e780541'
id-mismatch: id 'fb-f5651adfd090d04c' != derived 'fb-5ea3c2e0dab8a1ae'
[exit 1]
```

The path, in order. Do not skip a step to get to the restore faster.

1. **Stop writing.** No ingest, confirm, rotate or emit against this
   store until the path completes. Every one of those appends to the
   ledger or rewrites blobs.
2. **Preserve the evidence.** Copy the whole store folder AND the key
   file, as they are now, to a folder named for the date and the word
   `incident`. Record the `verify` output verbatim beside it. The
   failure output names hashes and ids, never content, so the record is
   safe to keep in a ticket.
3. **Read the codes against the table in section 4.** Three codes on one
   record means one edit; codes on many records means many edits or a
   rewritten file; `store-unreadable` means a tool other than
   finding-bridge wrote the file.
4. **Compare with the last backup.** `verify` the backup copy (point
   `--store` and `--key` at it). If the backup verifies clean, the
   damage happened after it. Diff the two ledgers line by line: the
   first differing line is where the edit is.
5. **Decide, and write the decision down.** Restore from the backup
   (section 7) if the edit is not something you meant to keep. If the
   backup also fails, or there is no backup, the store's history from
   that record onward is unverifiable and stays that way: do not repair
   a ledger by hand and do not re-confirm to "fix" hashes. A repaired
   chain is a forged chain.
6. **What the guarantee is, said plainly (OB-4):** the hash chain and
   its head detect accident, drift and casual edit. They do not defend
   against an attacker with write access to both the ledger and its head
   at once. If that is your incident, the chain cannot tell you, and
   the backup held elsewhere is your only witness.
7. **Escalation:** none exists (document control table). Record the
   incident in the project's decision log.

## 9. Gate before any change ships

```
python tools/gate.py
```

Runs the test suite (no API key set; the suite scrubs key variables and
proves it), `ruff check` and `ruff format --check`, each exit code read
directly, one word at the end. Exit 0 pass, 1 a constituent failed, 2 a
constituent could not run. There is no override flag. Do not pipe its
output through `tail` and read the pipeline's status; that mask is the
reason the tool exists (D-062, C-008, C-009).
