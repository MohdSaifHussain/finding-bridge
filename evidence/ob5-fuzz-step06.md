# OB-5: the fuzzing pass (2026-08-25, D-078)

**Trigger:** fired by W6c (real data at volume). **Budget:** 30 minutes
wall clock, stated in advance. **Route:** the structured alternative.
Atheris was checked before promising: PyPI serves only
`manylinux2014_x86_64` wheels for atheris 3.1.0 (no Windows files, no OS
classifiers), and `pip install atheris` on this Windows / CPython 3.14
machine answers `No matching distribution found for atheris`. The
attempt is recorded here as the ruling required.

**What ran:** `python tools/fuzz_ingest.py --minutes 30 --seed-dir <DATA_DIR>`,
rng seed 20260825. Seeds: the first 200 lines of the real garak 0.16.0
hitlog and the 40 prepared real transcripts (read at run time, never
committed), plus one synthetic seed of each kind. Mutation families:
truncate, junk insertion (BOM, NUL, CR, surrogates, full-width colon,
tabs), non-canonical numbers (NaN, Infinity, 1e400, 2^53+1), duplicated
lines, marker variants (case, spaces, tabs, full-width, indentation,
`Human:`), JSON shape (renamed keys, list-for-dict, nulls, missing braces,
array wrapping, 3,000-char text), growth (2x to 40x), and raw non-UTF-8
bytes. One to three families per input; both parsers driven through
`cli.main`. Selftest first: a planted crash is classified CRASH.

**Result, verbatim:**

```
FUZZ: 11063 inputs in 30.0 min (budget 30.0 min), rng seed 20260825
     363  garak:ok
    3932  garak:refused:invalid-hitlog
    1297  garak:refused:unsupported-encoding
    3046  transcript:ok
    1049  transcript:refused:invalid-transcript
    1376  transcript:refused:unsupported-encoding
FUZZ: no escaped exception, no slow input, no unexpected exit code
fuzz exit 0
```

11,063 inputs in 30.0 minutes. Every outcome was a success (3,409) or a
governed refusal with a reason code (7,654: invalid-hitlog 3,932,
unsupported-encoding 2,673, invalid-transcript 1,049). Zero escaped
exceptions, zero inputs over the 20 s cap, zero unexpected exit codes.

**What this does not prove:** coverage. The generator mutates toward the
families someone named; it is not coverage-guided and cannot reach a
class it does not mutate toward. It proves that, for 30 minutes on these
seeds, none of the named families produced a raw traceback, a hang, or
an ungoverned exit through either parser. The gate-guarded boundary
table (D-036, D-044) is the standing check; this pass is one measurement
against it. **Disposition for ruling:** OB-5's trigger is met and the
pass ran; whether OB-5 is DISCHARGED by a structured pass, or stays open
until a coverage-guided run is possible on a Linux runner (Atheris in
CI is feasible: the gate already runs Ubuntu), is the director's call.
The builder recommends the latter as a named follow-up, not a silent
close.
