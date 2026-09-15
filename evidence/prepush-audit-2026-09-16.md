# Delta pre-push audit, 2026-09-16 push (D-093 to D-095), raw capture

Run before the push of `b95f485`, `630511a` and `a454253`
(`origin/master..HEAD` with origin/master at `bf49797`). The scripts lived
in the session's scratch folder and are not committed. The earlier
audits record the secret FAMILIES and the path and filename lists they
searched for, not their patterns; the patterns here are these scripts'
own, and each script proved its detectors fire on planted cases and stay
quiet on clean ones before its result was used.

## Version 1

```
DELTA AUDIT SELFTEST: ok (7 secret shapes, local path and filenames each fire when planted; clean inputs stay clean)
== DELTA PRE-PUSH AUDIT: origin/master..HEAD
commits ahead: 3
blobs: 26
bytes: 470060
secret shapes: 3
  DECISIONS.md: ['openai-or-anthropic-key']
  DECISIONS.md: ['openai-or-anthropic-key']
  DECISIONS.md: ['openai-or-anthropic-key']
local absolute paths: 4
  DECISIONS.md: 2
  evidence/real-data-garak-0.17.0.md: 5
  DECISIONS.md: 2
  DECISIONS.md: 1
key/store/real-data filenames: 0
authors: MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>|MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
workflows changed: (none)
```

Every hit, looked at directly (secret matches shown masked, never whole):

| Hit | Where | What it is | On master before this push? |
|---|---|---|---|
| secret shape, once in each of the 3 `DECISIONS.md` blobs | `DECISIONS.md` line 1676 | the NIST URL `.../itl/ai-risk-management-framework`: the `sk-` pattern had no word boundary and matched inside "risk-management-framework" | yes (D-090 addendum) |
| local path | `DECISIONS.md` line 1072 | the sentence "no `C:\Users\...` path in committed content", naming the pattern | yes |
| local path | `DECISIONS.md` line 1869 | D-094 naming the pattern (`C:\Users`) | no, pattern text only |
| local path (5) | `evidence/real-data-garak-0.17.0.md` lines 127 and 130 | the table and sentence listing the scan's patterns | no, pattern text only |

No secret and no real local path. The earlier audits reported 0 with the
NIST line and line 1072 already present, so this version was broader than
theirs.

## Version 2

Exactly two changes: the key pattern must start at a word boundary, and
a local path counts only when a folder name follows the users segment.
The selftest keeps every version-1 must-fire case and adds the three
version-1 false positives, verbatim, as must-stay-quiet cases.

```
DELTA AUDIT v2 SELFTEST: ok (7 secret shapes and 3 real path forms fire; the 3 version-1 false positives and a clean line stay quiet; filenames fire and stay quiet)
== DELTA PRE-PUSH AUDIT v2: origin/master..HEAD
commits ahead: 3
blobs: 26
bytes: 470060
secret shapes: 0
local absolute paths: 0
key/store/real-data filenames: 0
authors: MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>|MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com>
workflows changed: (none)
```

Direction: the figure moved from 3 and 4 to 0 and 0 because the instrument
was narrowed after its hits were looked at, not because the content
changed. Both runs are kept for that reason.

## The scans the real-data audits also recorded

```
REAL-STRING SCAN: CLEAN (5000 sampled strings from 4567 real texts, 6 artifacts searched)
FIXTURE SCAN: CONFORMING (10 fixtures, 6 example inputs, 18 example outputs leak-checked)
```
