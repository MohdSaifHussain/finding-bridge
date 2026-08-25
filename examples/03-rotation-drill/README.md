# Example 03: the rotation drill, with a backup, an incident and a restore

The operations case. Rotate the encryption key twice, prove the chain
still verifies across both joins and that ids did not move, then break
the ledger by hand, watch `verify` refuse, and restore from the backup
you took first.

Everything here is synthetic (D-012). The input is the same hitlog as
example 01.

## What happens

1. Ingest, list, confirm one finding, verify. Emit a packet, so there is
   a reference to unseal later.
2. BACKUP: copy the store folder AND the key file. The key is not inside
   the store. A backup of the store alone cannot be unsealed.
3. Rotate the key. The tool records a supersession event in the ledger
   (event, both chain heads, who confirmed, an attestation) and
   re-encrypts every sealed blob. `verify` walks through the event.
4. Unseal the response with `--explicit`. The content survived the
   rotation; the reference did not change, because the reference key is
   separate and permanent (D-053; stated limit).
5. Rotate again, verify again, list: the ids are unchanged.
6. INCIDENT: change one byte inside a confirmed record in `ledger.jsonl`.
   `verify` refuses with three distinct reason codes, because three
   different checks failed for three different reasons.
7. RESTORE: copy the backup back over the store folder and the key file.
   `verify` is clean again. The backup predates both rotations, so the
   older key came back with it; that is what a restore means.

## Commands

Run from this folder, store and key outside the repository.

```
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key ingest-garak input/garak.synthetic.hitlog.jsonl
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key list
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key confirm <id-from-list>
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key verify
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key emit-markdown output/packet-before-rotation.md
```

Backup (the tool has no backup command; it is a file copy):

```
cp -r /tmp/fb/store /tmp/fb-backup/store          (Windows CMD: xcopy /e /i %TEMP%\fb\store %TEMP%\fb-backup\store)
cp /tmp/fb/fb.key /tmp/fb-backup/fb.key           (Windows CMD: copy %TEMP%\fb\fb.key %TEMP%\fb-backup\fb.key)
```

Rotate, verify, unseal, rotate, verify, list:

```
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key rotate-key --reason "drill: first rotation"
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key verify
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key unseal <response-ref-from-packet> --explicit
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key rotate-key --reason "drill: second rotation"
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key verify
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key list
```

Incident: open `/tmp/fb/store/ledger.jsonl` in an editor and change one
character inside the confirmed record, then:

```
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key verify
```

Restore, then verify:

```
rm -r /tmp/fb/store && cp -r /tmp/fb-backup/store /tmp/fb/store && cp /tmp/fb-backup/fb.key /tmp/fb/fb.key
finding-bridge --store /tmp/fb/store --key /tmp/fb/fb.key verify
```

Or: `python examples/run_example.py 03-rotation-drill`, where the backup,
the tamper and the restore are driver steps and say so in the transcript.

## What is committed under output/

`run-transcript.md` (complete, unedited) and `packet-before-rotation.md`.

## The refusal

```
$ finding-bridge verify
attestation-tampered: attestation_hash '<hash>' does not match (content_hash, confirmed_by, confirmed_at); the gate record was edited after confirmation
content-tampered: stored content_hash '<hash>' != recomputed '<hash>'
id-mismatch: id 'fb-<id>' != derived 'fb-<other>'
[exit 1]
```

One changed byte, three reason codes. Each names a different check, so an
operator at 2am knows which layer noticed. See SOP.md for what to do next.

## Known limit in this drill (finding F-2, for the director's ruling)

This drill does not emit a packet AFTER rotating. When it tried,
`emit-markdown`, `emit-sarif` and `emit-flare` crashed on the supersession
record the rotation put in the ledger (`emit-tracker` skips it). That is
a product defect found by this example, recorded as finding F-2 in
`evidence/step06-findings.md` with the measurement, and it is not fixed
here because this arc changes no product code without a ruling.
