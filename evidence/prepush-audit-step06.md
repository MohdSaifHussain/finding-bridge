# Delta pre-push audit, STEP-06 (2026-08-25), raw capture

Run before the first push of the launch arc (14 commits ahead of origin/master plus the staged W6 rehearsal tree). The first object-scan row read 0 blobs because the pipeline fed cat-file the wrong token; the CORRECTED section below re-ran it over every new blob.

```
== DELTA PRE-PUSH AUDIT: origin/master..HEAD plus the staged tree
commits ahead: 14
-- files touched:
70
-- new objects (blobs) scanned:
0
-- secret shapes in new blobs + staged tree (GitHub ghp_/gho_/github_pat_, AWS AKIA, OpenAI sk-, Slack xox, PEM, Fernet-keyring JSON):
0
-- key/store filenames ever in the delta:
0
-- local absolute paths in the staged tree (C:\Users):
0
-- authors/committers of the delta:
MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com> | MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
-- example outputs: sentinel leak scan
FIXTURE SCAN: CONFORMING (7 fixtures, 6 example inputs, 12 example outputs leak-checked)
== ADVERSARIAL RE-READ of workflows
-- .github/workflows/gate.yml
pull_request_target: 0
secrets referenced: 
unpinned uses (no 40-hex): 0
untrusted-input expressions inside run blocks (github.event.*|head_ref|inputs.): 0
permissions block: permissions:   contents: read  
-- .github/workflows/container.yml
pull_request_target: 0
secrets referenced: secrets.GITHUB_TOKEN 
unpinned uses (no 40-hex): 0
untrusted-input expressions inside run blocks (github.event.*|head_ref|inputs.): 0
permissions block: permissions:   contents: read   packages: write 
-- .github/dependabot.yml
pull_request_target: 0
secrets referenced: 
unpinned uses (no 40-hex): 0
untrusted-input expressions inside run blocks (github.event.*|head_ref|inputs.): 0
permissions block: 
== CORRECTED: every new blob in origin/master..HEAD
blobs: 98
bytes scanned: 1085627
secret shapes: 0
local absolute paths: 0
key/store filenames in any new tree: 0
```
