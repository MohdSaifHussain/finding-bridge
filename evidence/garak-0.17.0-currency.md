# garak 0.17.0 fixture currency, 2026-09-16 (issue #7, D-093)

Issue #7 was opened by `currency.yml` (D-090): garak 0.17.0 was released
and the pin was 0.16.0. This file is the measured half of the standing
procedure in `docs/FIXTURE-VERSIONS.md`. Reading taken 2026-09-15 18:32 UTC
(2026-09-16 local). Every source is GitHub's API for NVIDIA/garak, or PyPI.

## The release

- GitHub latest: v0.17.0, published 2026-09-09T18:56:03Z
  (https://github.com/NVIDIA/garak/releases/tag/v0.17.0).
- PyPI latest: 0.17.0 (https://pypi.org/pypi/garak/json).
- `compare/v0.16.0...v0.17.0`: 120 commits, 126 files changed.

## Step 1: the fixture-currency test

`python -m pytest tests/test_real_shapes.py -q`, Python 3.14.0, no API key:
20 passed.

## Step 2: did the hitlog shape move?

Three garak files mention the hitlog at v0.17.0 (`grep -rli hitlog garak/`
over the release tarball): `garak/_config.py`, `garak/command.py`,
`garak/evaluators/base.py`. `garak/attempt.py` is added because it defines
`Message` and `Conversation`, the objects the hitlog writes.

| File | v0.16.0 blob | v0.17.0 blob | Bytes (both tags) |
|---|---|---|---|
| `garak/evaluators/base.py` | `11e1c6fc053f` | `e0cff2dec1e1` | 18,583 |
| `garak/attempt.py` | `184ecf8620b0` | `184ecf8620b0` | 18,128 |
| `garak/_config.py` | `3433d699993a` | `3433d699993a` | 17,923 |
| `garak/command.py` | `f61c2fe00ba3` | `f61c2fe00ba3` | 13,945 |

The whole `base.py` diff is one comment:

```
259c259
<         #  total detections preformed (detection_counts: sum(None), sum(hit), sum(pass))
---
>         #  total detections performed (detection_counts: sum(None), sum(hit), sum(pass))
```

One more changed file touches a `Conversation`: `garak/probes/base.py`
(garak PR #2022, "unreachable Conversation branch in Probe.probe()
pre-translation notes"). Its diff is two lines: the `isinstance` check now
tests `Conversation` instead of `Message`, and it sets `turn.content.lang`
instead of `turn.context.lang`. Reading, not run: this changes a value
inside the attempt's pre-translation notes. It does not change the keys of
a hitlog record, and `attempt.py`, which serialises them, is identical.

**Verdict: the shape did not move.** Per the procedure, step 3 (a new
fixture and the real-data drill) is not needed. The pin line moves to
0.17.0 and the issue closes.

## Controls

| Check | Expected | Observed |
|---|---|---|
| `tests/test_readme_badges.py`, before any change | pass | 3 passed |
| Same test, pin changed to 0.17.0, badge left at 0.16.0 | fail on the mismatch | 1 failed: `garak badge says garak%20fixtures-0.16.0-informational, FIXTURE-VERSIONS pins 0.17.0` |
| Same test, badge fixed | pass | 3 passed |
| `tools/currency_check.py --selftest` | ok | `currency selftest: ok (pin parsed; duplicate detector discriminates by version)` |
| `tools/currency_check.py --dry-run` | garak current | `garak: pinned 0.17.0, latest 0.17.0 (github-releases): current` |
| `tools/currency_check.py --force-garak-pin 0.16.0 --dry-run` | builder predicted `WOULD-OPEN` | `already-open`. The prediction was wrong: issue #7 was still open, and the duplicate check runs before the dry-run branch (`currency_check.py:154-157`). To re-run after #7 closes, when `WOULD-OPEN` is the correct answer. |
| `python tools/gate.py --verdict-file <file>` | `GATE: PASS` | `GATE: PASS`, exit 0 (pytest 356 passed, 1 skipped; ruff check clean; ruff format: 74 files already formatted) |
| `python -m pytest -q`, API keys removed | all pass | 356 passed, 1 skipped, exit 0 |

## Found on the way

1. **garak 0.17.0 and the `ai` extra cannot share one environment.** garak
   0.17.0 requires `anthropic>=0.40.0,<1.0.0` (its `pyproject.toml` at
   v0.17.0, line 157; added by garak PR #2098, merged 2026-08-21). At
   v0.16.0 it required `anthropic>=0.40.0` with no upper bound (line 141).
   finding-bridge's `ai` extra pins a 1.x release. The core install is not
   affected, and example 04 already runs garak in its own venv.
   `docs/USAGE.md` now says so beside the `ai` install line.
2. **The `currency.yml` positive control can fail on a healthy tool.** It
   greps for `WOULD-OPEN`. While an issue for the same version is open,
   the tool correctly prints `already-open`, so the control would report
   FAILED. This is pre-existing (D-090) and is recorded, not fixed here.
3. **Working-copy line endings.** After the edits, the four changed `.md`
   files were CRLF on every line, against `.gitattributes` (`*.md` eol=lf).
   Git stores LF, so committed bytes were never affected. The cause was not
   determined: the edit tool, or a checkout made before the LF rule
   existed. Converted to LF before commit by a script that refuses on bare
   CR bytes; `git ls-files --eol` then read `w/lf` for all four and the
   diff was unchanged (52 insertions, 2 deletions).

## Limits

- This is a source comparison, not a real garak 0.17.0 run. The procedure
  allows closing the issue on it ("Closing it after step 2 with 'shape
  unchanged' is correct").
- Run on Python 3.14.0 only; no 3.12 is installed on this machine.
