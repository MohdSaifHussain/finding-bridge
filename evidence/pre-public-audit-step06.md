# Pre-public audit (STEP-06 W7, 2026-08-25)

Stricter than the pre-push audit: every object in the whole history, not
the delta; every user document swept by the wording check in one run;
license and NOTICE re-verified in the built wheel; the known build blob
named. Run on the tree at the W7 commits (111 commits at the time of the
history scan; the W7 commits add documents only).

## Full-history scan, every object

```
commits: 111   blobs: 451   bytes scanned: 5,141,756
secret shapes (GitHub ghp_/gho_/github_pat_, AWS AKIA, OpenAI sk-, Slack xox, PEM blocks, Fernet-keyring JSON): 0
local absolute paths (C:\Users, C:/Users, /c/Users): 0
key / store / real-data filenames in any tree ever (fb.key, *.key, *.pem, *.fernet, exposure_log, ledger, candidates, head.json, fb-real*, red_team_attempts*, prepared/): 0
authors and committers: MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>, one identity throughout
build artifacts ever committed: 1 (dist/finding_bridge-0.1.0-py3-none-any.whl, blob 0e281d23..., 38,358 bytes; commits 56-57, D-058, kept in history on purpose and named in the release notes)
```

Method: `git rev-list --objects --all` piped through `git cat-file
--batch-check`, every blob concatenated and grepped; filenames from the
same listing.

## Every user document, one wording sweep

`tests/test_no_overclaim.py` scans README.md, docs/USAGE.md, SOP.md,
docs/STANDARDS.md, docs/showcase/README.md, CHANGELOG.md, SECURITY.md
and every examples/*/README.md for the D-046 banned list, with the D-073
quotation exemption (three conditions) and the known-broken-command
list; and asserts the required statements (the D-042 wording, the OB-4
bound, the no-AI statement) and the install route. Result: green at the
release commit (the gate's pytest constituent).

## License and NOTICE

`LICENSE` (Apache-2.0) and `NOTICE` present at the root; pyproject
declares `license = "Apache-2.0"` and `license-files = ["LICENSE"]`. The
wheel built at 1.0.0 carries `License-Expression: Apache-2.0` and
`License-File: LICENSE` in its METADATA (re-read from the wheel, below).
The act of publishing under Apache-2.0 is the director's separate ruling
at the flip (D-048's scope sentence).

## Documents reread

Every document under the repository root, docs/, examples/ and
evidence/ was regenerated or re-read during W1-W7 of this arc; the
director's STOP THREE read is the second reader. Figures restated in
prose were settled once at the release total (rule 14): 349 tests, 261
product / 88 governance, 84 rulings, 11 corrections.

## Limits of this audit

The secret-shape list is the named shapes only; a secret of an unlisted
shape would pass. The history scan is of this repository's objects; it
says nothing about the director's other repositories or the GHCR package
layers (those have their own scan, tools/layer_scan.py, run on every
container build).
