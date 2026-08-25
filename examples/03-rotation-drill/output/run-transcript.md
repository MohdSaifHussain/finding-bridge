# Run transcript: 03-rotation-drill

Complete, unedited output of `python examples/run_example.py 03-rotation-drill`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-garak input/garak.synthetic.hitlog.jsonl
{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
[exit 0]

$ finding-bridge list
fb-647068a43fe4798d  garak  [sealed content: 77 chars, 1 lines, keyed digest 58414854; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
fb-41d6ff09674f103b  garak  [sealed content: 77 chars, 1 lines, keyed digest 58414854; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-647068a43fe4798d
fb-f8b6591d984af803  garak  [sealed content: 47 chars, 1 lines, keyed digest c77b2458; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ finding-bridge confirm fb-647068a43fe4798d
confirmed fb-647068a43fe4798d by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
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

$ finding-bridge unseal sealed/58414854483fd5aa --explicit
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
fb-41d6ff09674f103b  garak  [sealed content: 77 chars, 1 lines, keyed digest 58414854; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-647068a43fe4798d
fb-f8b6591d984af803  garak  [sealed content: 47 chars, 1 lines, keyed digest c77b2458; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ [driver step] INCIDENT: flip one byte inside the ledger by hand
ledger.jsonl: one byte changed inside a confirmed record (source_tool)
[driver step done]

$ finding-bridge verify
attestation-tampered: attestation_hash '0059746caf8c5f94123a04c055f7bf2c27be636799678b76bb3c606201bacf2b' does not match (content_hash, confirmed_by, confirmed_at); the gate record was edited after confirmation
content-tampered: stored content_hash '647068a43fe4798d2301fee8f863f67305bf4270163308a710d0a49c1efa69e4' != recomputed '5e4a0303e60346ba86007eb79297cb13809bad082e712485084e9aebdc0ab802'
id-mismatch: id 'fb-647068a43fe4798d' != derived 'fb-5e4a0303e60346ba'
[exit 1]

$ [driver step] RESTORE: copy backup/ back over the store folder and the key file
store/ and fb.key replaced from backup/ (the backup predates both rotations, so the older key is restored with it)
[driver step done]

$ finding-bridge verify
chain verifies clean
[exit 0]

```
