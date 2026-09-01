# Dependabot repair, 2026-09-01 (D-092)

Master went red at `1217516` after three Dependabot merges. This file is the
measured half: what was run, and what came back.

## What failed, and what did not

`gh run list`, read 2026-09-01:

| Run | Head | Workflow | Result |
|---|---|---|---|
| 33529392000 | `56a3316` (#3 anthropic) | gate | success |
| 33529392003 | `56a3316` | container | success |
| 33529415823 | `bb6a140` (#2 cryptography) | gate | success |
| 33529415858 | `bb6a140` | container | success |
| 33529459514 | `1217516` (#1 python 3.14) | gate | success |
| 33529459519 | `1217516` | container | **failure** |

Step outcomes on the failed run:

```
1 Set up job                                            success
2 actions/checkout                                      success
3 docker/setup-buildx-action                            success
4 Build (local load, not pushed yet)                    success
5 Read the base digest back ... compare to the pin      failure
6 Layer scan, selftest and positive control             skipped
7 Layer scan, candidate image                           skipped
8 Smoke (mounted key and gitconfig)                     skipped
9 Log in to GHCR                                        skipped
10 Compute the tag list                                 skipped
11 Push the computed tags                               skipped
```

Two readings follow from that, and only two. The 3.14 image BUILT (step 4).
Nothing was published (steps 9 to 11 skipped), so GHCR `:latest` is still the
`bb6a140` image. The 3.14 image was never smoked, so no claim is made here
about whether the tool runs correctly on a 3.14 base.

The three pull-request runs were `gate` only. `container` has no
`pull_request` trigger, so it first ran after each merge. That is the
structural half of D-092.

## The defect, replayed before the fix

The old step, run verbatim against the merged (3.14) Dockerfile:

```
$ pin=$(grep -o 'python:3.12-slim@sha256:[0-9a-f]\{64\}' Dockerfile | sort -u)
pinned:
empty? []
wc -l on empty pin -> 1
GUARD PASSED (this is the defect: it passed on an EMPTY pin)
```

`echo "" | wc -l` is 1, so `test "$(echo "$pin" | wc -l)" = "1"` passes on an
empty pin. Control flow then reached `docker pull -q ""`, which is the
`invalid reference format` in the run log.

## Controls on the replacement (rule 5, both directions)

Extraction and guards exercised against four synthetic Dockerfiles. The
`docker pull` and compare half needs a daemon and runs in CI; this covers the
half that broke.

| Case | Expected | Observed |
|---|---|---|
| 3.12 pinned, both stages agree | exit 0 | exit 0, pin extracted |
| 3.14 pinned, both stages agree | exit 0 | exit 0, pin extracted (version-agnostic) |
| tag present, no digest | exit 1 | `pin-not-found`, exit 1 |
| stages disagree on the pin | exit 1 | `pin-not-unique`, exit 1 |

Regression, against the reverted real Dockerfile:

```
pinned:   python:3.12-slim@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d
compare would be: python@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d
exit: 0
```

The positive cases matter as much as the negative ones: a guard that refused
everything would also have turned this run green-to-red for the wrong reason.

## The reverted digest, re-derived not remembered

`sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d`,
read back from three independent places in the record:

- `Dockerfile` at `41a33ed` (the commit before the merges)
- `evidence/w6-local-rehearsal.md`
- `evidence/ci-first-run-step06.md`

The reverted `Dockerfile` was then checked byte-identical to `41a33ed`'s:

```
VERIFIED: Dockerfile is byte-identical to 41a33ed (pre-merge state)
```

## Gate after the repair

`sed` touched the Dockerfile, so the whole gate re-ran, not the half that
looked affected:

```
  pytest        ok             356 passed, 1 skipped in 33.99s
  ruff-check    ok             All checks passed!
  ruff-format   ok             74 files already formatted
GATE: PASS
```

## Limits of this file

- The four controls cover pin extraction and the guards. They do not cover
  `docker pull` or the digest comparison, which need a daemon.
- `{{ index .RepoDigests 0 }}` still takes entry 0 on faith (D-092, F-3).
  Pre-existing, unchanged by this repair.
- ~~Whether the pull-request trigger behaves as intended is unproven until a
  pull request actually touches one of the four paths. Until then it is a
  configuration read back from YAML, not an observed run.~~ **NARROWED the
  same day: a real run now exists, see "After the push" below. What remains
  unproven is narrower: no pull request has yet exercised a Dockerfile change
  that SHOULD fail, so the PR lane has an observed positive and no observed
  negative.**

## After the push (runs on `bba0b0d`, read 2026-09-01)

| Run | Workflow | Event | Result |
|---|---|---|---|
| 33533815703 | gate | push | success, 4/4 jobs (ubuntu+windows x 3.12+3.14) |
| 33533815791 | container | push | success, all 11 steps |

The read-back, from the run log, both halves present again:

```
pinned:   python:3.12-slim@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d
pulled:   python@sha256:3ecf5ebe01fef4b6e81be34511fb40bf378ea7fd81ab215ba15b2775ef85413d
digest read-back matches the pin
```

## The new checks proved themselves within the hour, unplanned

Dependabot re-read the amended config and opened **PR #4, "Bump python from
`3ecf5eb` to `e5c9fa2`"**: a DIGEST-only refresh of the `3.12-slim` tag. That
is exactly the split the ignore rule was written for. It let a digest refresh
through and would have blocked a version bump.

`container` then ran on that PR (run 33533883964, `event=pull_request`), which
is the first observed proof of the new trigger:

```
  4 Build (local load, not pushed yet)          success
  5 Read the base digest back ... the pin       success
  6 Layer scan, selftest and positive control   success
  7 Layer scan, candidate image                 success
  8 Smoke (mounted key and gitconfig)           success
  9 Log in to GHCR                              skipped
 10 Compute the tag list                        skipped
 11 Push the computed tags                      skipped
```

Both directions, observed rather than argued: the image was built, scanned and
smoked BEFORE merge, and nothing was published from a pull request.

That run also proves the read-back is genuinely no longer bound to one value.
It passed against a digest that appears nowhere in the workflow, the old code,
or this file's earlier sections:

```
pinned:   python:3.12-slim@sha256:e5c9fa26ffb76e11e0f054f30dc2523a2f9693f0c36c0cf1e39b27e152d899fc
pulled:   python@sha256:e5c9fa26ffb76e11e0f054f30dc2523a2f9693f0c36c0cf1e39b27e152d899fc
digest read-back matches the pin
```

To be exact about what PR #4 does and does not show: under the OLD step it
would have passed too. The old grep was
`python:3.12-slim@sha256:[0-9a-f]{64}`, which matches any digest, so a
digest-only change kept the version literal true. Only a VERSION change broke
it, and that is what `1217516` was. So PR #4 does not re-demonstrate the
original bug. What it demonstrates is the new pull-request trigger, the
push-guard skipping, and the extraction working against a digest that appears
nowhere in the code or the record.

**PR #4 is open and is the director's call.** It is a digest refresh on the
declared floor, which is the update the rule was built to allow, and it is
green on both gate and container. Nothing here merges it.
