# First CI runs (STEP-06 W5/W6), commit d857430, 2026-08-25

Observed to completion by the builder; every line below is quoted from
the run logs (`gh run view --log`) or the GitHub API, not restated.

## gate.yml, run 32822503809

https://github.com/MohdSaifHussain/finding-bridge/actions/runs/32822503809

| Job | Result |
|---|---|
| gate (ubuntu-latest, py3.12) | completed success |
| gate (ubuntu-latest, py3.14) | completed success |
| gate (windows-latest, py3.12) | completed success |
| gate (windows-latest, py3.14) | completed success |

Ubuntu py3.12 log lines:

```
GATE: PASS
FIXTURE SCAN: CONFORMING (7 fixtures, 6 example inputs, 12 example outputs leak-checked)
skips on ubuntu-latest: 0
No broken requirements found.
finding_bridge imported from: /home/runner/work/_temp/fb-venv/lib/python3.12/site-packages/finding_bridge/__init__.py
```

Windows py3.12 log line: `skips on windows-latest: 1`.

**The named deliverable, at the width of the evidence:** the suite's only
skip is `tests/test_sealing.py`'s key-file permission check (D-023),
which skips on Windows with the message "Windows ACLs are not set by
chmod; operator step is icacls (recorded limit)". The Ubuntu step counted
zero `SKIPPED` lines with `pytest -rs` and passed; the Windows step
counted exactly one. On this first run the workflow did not print the
SKIPPED line itself (it printed the count), so the test's name is not
quoted from the log; the step now prints it (next run), and the count
pair (0 on Linux, 1 on Windows) is the proof this run gives.

## container.yml, run 32822503853

https://github.com/MohdSaifHussain/finding-bridge/actions/runs/32822503853
Result: completed success.

Digest read-back on the runner (the measured half; the local pull was the
first half, evidence/w6-local-rehearsal.md):

```
pinned:   python:3.12-slim@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d
pulled:   python@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d
digest read-back matches the pin
```

Layer scan:

```
LAYER SCAN SELFTEST: ok (planted keyring found by name and by marker)
LAYER SCAN: KEY MATERIAL FOUND (1 layers)            <- the planted throwaway image
positive control: planted key found (scanner exit 1 as required)
LAYER SCAN: CLEAN (10 layers; no key-shaped file, no keyring marker)   <- the candidate
```

Smoke row (key and gitconfig mounted from outside the image):

```
{"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
confirmed fb-b214e8818a575501 by smoke-operator <smoke@example.invalid>
chain verifies clean
wrote store/packet.md
unseal-not-explicit: unseal of 'sealed/c8af568b1dfa7f93' requires explicit=True (charter: unsealing is always explicit and logged)
key was created OUTSIDE the image, in the mounted folder
explicit unseal returned the sealed sentinel
```

No `SENTINEL-HARM` reached stdout across ingest, list, confirm, verify,
emit and the refused unseal (the step greps for it and would have failed).

## GHCR package, API-verified (not clicked)

`gh api user/packages/container/finding-bridge`:

```
name=finding-bridge visibility=private versions=3
url=https://github.com/users/MohdSaifHussain/packages/container/package/finding-bridge
sha256:876d8ade2efb tags=["latest","d8574303c9ee463c7e90bc688de158e024f59069"]
sha256:dcb438409bee tags=[]        <- untagged manifests the buildx push produced
sha256:91f5aacb72f0 tags=[]           beside the index (attestation / platform)
```

PRIVATE, as contracted until the flip. `:latest` and `:<sha>` present; no
`v1.0.0` tag.

## Dependabot, first runs

Six update jobs (pip, github-actions, docker; two each) all `success`.
The pip job's log shows it checking `rpds-py 2026.6.3`, `cffi 2.1.1`,
`six 1.17.0`, `jsonschema-specifications 2025.9.1`: names that exist
only in `constraints.txt`. **PROV-4 condition 1 verified by observation:
Dependabot reads the lock.** No pull requests were opened on this run.

## Badges

The gate and container badges land in the commit that records this
file, per contract 3.2: their first observed green run is the one above.
