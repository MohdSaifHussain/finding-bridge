# Run transcript: 03-rotation-drill

Complete, unedited output of `python examples/run_example.py 03-rotation-drill`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-garak input/garak.synthetic.hitlog.jsonl
{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
[exit 0]

$ finding-bridge list
fb-5c4c787c2b3698eb  garak  [sealed content: 77 chars, 1 lines, keyed digest c1a6901a; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
fb-ef39cc5556df3a16  garak  [sealed content: 77 chars, 1 lines, keyed digest c1a6901a; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-5c4c787c2b3698eb
fb-5ac634e95d31f354  garak  [sealed content: 47 chars, 1 lines, keyed digest 73274372; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ finding-bridge confirm fb-5c4c787c2b3698eb
confirmed fb-5c4c787c2b3698eb by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
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

$ finding-bridge unseal sealed/c1a6901a59db81d3 --explicit
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
fb-ef39cc5556df3a16  garak  [sealed content: 77 chars, 1 lines, keyed digest c1a6901a; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-5c4c787c2b3698eb
fb-5ac634e95d31f354  garak  [sealed content: 47 chars, 1 lines, keyed digest 73274372; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ [driver step] INCIDENT: flip one byte inside the ledger by hand
ledger.jsonl: one byte changed inside a confirmed record (source_tool)
[driver step done]

$ finding-bridge verify
attestation-tampered: attestation_hash 'faea176926faa5e7fa433b375a46f861837df3cc8db04e0ed479ce21975897b8' does not match (content_hash, confirmed_by, confirmed_at); the gate record was edited after confirmation
content-tampered: stored content_hash '5c4c787c2b3698eb1122c2bd159cc8c18b805b13433c25d1eb2475ea270db4aa' != recomputed '5a77cb92af203caa4e59c8d24bd9c352573827ca2e05f037f47050c20c46ca03'
id-mismatch: id 'fb-5c4c787c2b3698eb' != derived 'fb-5a77cb92af203caa'
[exit 1]

$ [driver step] RESTORE: copy backup/ back over the store folder and the key file
store/ and fb.key replaced from backup/ (the backup predates both rotations, so the older key is restored with it)
[driver step done]

$ finding-bridge verify
chain verifies clean
[exit 0]

```
