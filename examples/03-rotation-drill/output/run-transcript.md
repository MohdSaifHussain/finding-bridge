# Run transcript: 03-rotation-drill

Complete, unedited output of `python examples/run_example.py 03-rotation-drill`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-garak input/garak.synthetic.hitlog.jsonl
{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
[exit 0]

$ finding-bridge list
fb-611ea38573724557  garak  [sealed content: 77 chars, 1 lines, keyed digest 0eda8780; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
fb-351d3ccd6928e403  garak  [sealed content: 77 chars, 1 lines, keyed digest 0eda8780; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-611ea38573724557
fb-99f072864d0eb97b  garak  [sealed content: 47 chars, 1 lines, keyed digest d56e638c; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ finding-bridge confirm fb-611ea38573724557
confirmed fb-611ea38573724557 by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
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

$ finding-bridge unseal sealed/0eda87805e1caac6 --explicit
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
fb-351d3ccd6928e403  garak  [sealed content: 77 chars, 1 lines, keyed digest 0eda8780; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-611ea38573724557
fb-99f072864d0eb97b  garak  [sealed content: 47 chars, 1 lines, keyed digest d56e638c; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ [driver step] INCIDENT: flip one byte inside the ledger by hand
ledger.jsonl: one byte changed inside a confirmed record (source_tool)
[driver step done]

$ finding-bridge verify
attestation-tampered: attestation_hash '16dda7fc88865f33623574f4dd0c53a08903299747a783bc7ab4179345fa115a' does not match (content_hash, confirmed_by, confirmed_at); the gate record was edited after confirmation
content-tampered: stored content_hash '611ea38573724557d0ab154d182fd6e8b9fed834dc4772d1635278ad2ec7b90a' != recomputed 'b98e0a0fa5786dbcc7ae824002f2b5b7d27a8934f7404392022619a74e41b5d8'
id-mismatch: id 'fb-611ea38573724557' != derived 'fb-b98e0a0fa5786dbc'
[exit 1]

$ [driver step] RESTORE: copy backup/ back over the store folder and the key file
store/ and fb.key replaced from backup/ (the backup predates both rotations, so the older key is restored with it)
[driver step done]

$ finding-bridge verify
chain verifies clean
[exit 0]

```
