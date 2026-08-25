# Run transcript: 01-garak-triage

Complete, unedited output of `python examples/run_example.py 01-garak-triage`. The store and key were in a scratch folder outside the repo, passed as `--store` and `--key` on every command (omitted from the lines below only because the path is a temp folder). Refusals are shown as they happened: they are the product behaving well.

```
$ finding-bridge ingest-garak input/garak.synthetic.hitlog.jsonl
{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
[exit 0]

$ finding-bridge list
fb-7517ad07312806d2  garak  [sealed content: 77 chars, 1 lines, keyed digest 330cd48e; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
fb-b4a25d13c613ed7d  garak  [sealed content: 77 chars, 1 lines, keyed digest 330cd48e; harm flags: garak-detector:mitigation.SyntheticDetector. Content is sealed; unseal is explicit and logged.] duplicate-of fb-7517ad07312806d2
fb-d0c074b608144bfd  garak  [sealed content: 47 chars, 1 lines, keyed digest ef1d8268; harm flags: garak-detector:promptinject.SyntheticDetector. Content is sealed; unseal is explicit and logged.]
[exit 0]

$ finding-bridge confirm fb-7517ad07312806d2
confirmed fb-7517ad07312806d2 by MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
[exit 0]

$ finding-bridge confirm fb-0000000000000000
unknown-id: no candidate with id 'fb-0000000000000000'
[exit 1]

$ finding-bridge ingest-garak input/garak.hostile.hitlog.jsonl
invalid-hitlog: line 1, field score: non-finite number is not representable in canonical form (value withheld per D-036)
[exit 1]

$ finding-bridge verify
chain verifies clean
[exit 0]

$ finding-bridge emit-markdown output/packet.md
wrote output/packet.md
[exit 0]

$ finding-bridge emit-sarif output/findings.sarif
wrote output\findings.sarif and output\findings.fb.jsonl
[exit 0]

$ finding-bridge emit-tracker output/findings.tracker.json
wrote output/findings.tracker.json (1 issue(s))
[exit 0]

$ finding-bridge emit-flare output/findings.flare.json
wrote output/findings.flare.json (PROVISIONAL mapping; see the provisional block)
[exit 0]

```
