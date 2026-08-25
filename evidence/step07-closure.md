# STEP-07 post-release closure, evidence (2026-08-25)

## P1 / F-15: the alert renders

GitHub's SARIF support doc (docs.github.com, fetched 2026-08-25): "Code
scanning interprets results that are reported with relative paths as
relative to the root of the repository analyzed"; producers declare
`%SRCROOT%` in `originalUriBaseIds` and use it as `uriBaseId`. The
emitter gained `--artifact-uri-base <repository-relative folder>`
(controls captured red first: `tests/test_sarif_srcroot.py`, 3 red / 1
green before, 4 green after; DEV-4's locationSemantics asserted to
survive). Example 01's committed SARIF now carries
`uri: examples/01-garak-triage/output/findings.fb.jsonl`,
`uriBaseId: %SRCROOT%`.

Proof, the only kind that counts: the rooted SARIF uploaded against
commit 0ce66f5 (upload 266a2858-a07e-11f1-9dbc-b98715f6cd26, processing
complete, no errors; analysis 1668624902, 1 result), and the alert
RENDERED:

```
{
  "created": "2026-08-25T12:11:50Z",
  "line": 1,
  "number": 2,
  "path": "examples/01-garak-triage/output/findings.fb.jsonl",
  "ref": "refs/heads/master",
  "rule": "garak-detector:mitigation.SyntheticDetector",
  "state": "open",
  "tool": "finding-bridge",
  "url": "https://github.com/MohdSaifHussain/finding-bridge/security/code-scanning/2"
}
```

Before (D-086 F6, the unrooted SARIF): 1 result, 0 alerts. After: 1
result, 1 alert at the committed record's line 1. F-15 closed; OB-7's
rendering half discharged. The director's capture of the alert page landed as
docs/showcase/03-code-scanning-alert.png (125,570 bytes): the alert's
message is the sealed metadata preview, which is the sealing claim and
the SARIF lane in one picture. The JSON above is the machine-readable
proof and stands on its own.

## P4 / F1: package visibility

`gh api user/packages/container/finding-bridge --jq .visibility` =
`public`, verified 2026-08-25 after the director's package-settings
click. D-086 F1 fully closed.
