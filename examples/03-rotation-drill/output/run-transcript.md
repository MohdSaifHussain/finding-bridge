# Run transcript: 03-rotation-drill

Complete, unedited output of `python examples/run_example.py 03-rotation-drill`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-garak input/garak.synthetic.hitlog.jsonl
{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
[exit 0]

$ finding-bridge list
fb-a8b4fcd352a4a76e  garak  [sealed content: 77 chars, 1 lines, keyed digest 73f400e4; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
fb-2745c107094ac10f  garak  [sealed content: 77 chars, 1 lines, keyed digest 73f400e4; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-a8b4fcd352a4a76e
fb-af23afdc6b79c6fa  garak  [sealed content: 47 chars, 1 lines, keyed digest f4c689e7; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ finding-bridge confirm fb-a8b4fcd352a4a76e
confirmed fb-a8b4fcd352a4a76e by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
[exit 0]

$ finding-bridge verify
chain verifies clean
[exit 0]

$ finding-bridge emit-markdown output/packet-before-rotation.md
wrote output/packet-before-rotation.md
[exit 0]

$ [driver step] BACKUP: copy the store folder and the key file to backup/
copied store/ and fb.key into backup/ (the key is NOT inside the store; back up both)
[driver step done]

$ finding-bridge rotate-key --reason "drill: first rotation"
rotated: supersession recorded, event=key-rotation, remap=0 id(s), confirmed by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
the ref key is permanent and was NOT rotated; ids are unchanged
[exit 0]

$ finding-bridge verify
chain verifies clean
[exit 0]

$ finding-bridge unseal sealed/73f400e4997c4d61 --explicit
SENTINEL-HARM-7001 synthetic harmful response stand-in, not real model output
[exit 0]

$ finding-bridge rotate-key --reason "drill: second rotation"
rotated: supersession recorded, event=key-rotation, remap=0 id(s), confirmed by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
the ref key is permanent and was NOT rotated; ids are unchanged
[exit 0]

$ finding-bridge verify
chain verifies clean
[exit 0]

$ finding-bridge list
fb-2745c107094ac10f  garak  [sealed content: 77 chars, 1 lines, keyed digest 73f400e4; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-a8b4fcd352a4a76e
fb-af23afdc6b79c6fa  garak  [sealed content: 47 chars, 1 lines, keyed digest f4c689e7; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ [driver step] INCIDENT: flip one byte inside the ledger by hand
ledger.jsonl: one byte changed inside a confirmed record (source_tool)
[driver step done]

$ finding-bridge verify
attestation-tampered: attestation_hash '656448abafff3b2aaf4c42bc5819735660d00cac96ca5360899bbae9d3cf8d5a' does not match (content_hash, confirmed_by, confirmed_at); the gate record was edited after confirmation
content-tampered: stored content_hash 'a8b4fcd352a4a76ed0efecbad1f89e094fc3d8c94e757eeb51f6c5bcb8f4689c' != recomputed '1d971418a6f88a6b8ac51fa22a59c10e1c1930ecedc7dbf979c9bc7acfdea30d'
id-mismatch: id 'fb-a8b4fcd352a4a76e' != derived 'fb-1d971418a6f88a6b'
[exit 1]

$ [driver step] RESTORE: copy backup/ back over the store folder and the key file
store/ and fb.key replaced from backup/ (the backup predates both rotations, so the older key is restored with it)
[driver step done]

$ finding-bridge verify
chain verifies clean
[exit 0]

```
