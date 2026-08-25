# Builder self-evaluation, STEP-06 (the launch arc), computed once at the close

Written by the builder about the builder: the limit this file states about
itself (the skill's Builder role note). Counts are from the record, each
naming where it lives.

## Defects this arc, by who caught them

Findings F-1 to F-15 plus corrections C-009 to C-012 (evidence/step06-
findings.md, DECISIONS.md corrections table). Attribution is by the row
that records the finder.

| # | What | Found by | Route |
|---|---|---|---|
| F-1 | workspace-setup tracebacks | builder | tour capture |
| F-2 | emitters crash after rotation | builder (the rotation drill) | documentation exercise |
| F-3, F-4, Q-1 | schema gaps against standards | builder | STANDARDS drafting |
| F-5 | OWASP pin stale | **director** | a question from outside the record |
| F-6 | install route never ran | builder | CI rehearsal |
| F-7 | lock incomplete on 3.12 | builder | local container build |
| F-8 | no git in the image | builder | local smoke |
| F-9 | (director's ghcr login, unconfirmed) | director | ritual |
| F-10..F-13 | real-data findings incl. the prompt loss | builder (real data) | W6c |
| F-14 | SARIF schema label stale | builder | W7 reading the driver block |
| F-15 | code-scanning alerts do not render (artifact URI) | builder | OB-7 verification at the flip |
| C-009 | gate masked by a pipe | builder (own re-read) | after the fact |
| C-010 | "the route we test" untested | builder | CI rehearsal |
| C-011 | duplicate count inflated by the bug | builder | post-fix re-run |
| C-012 | commit claimed unsettled figures | builder (own re-read) | after the fact |

Escapes to the director (defects the builder shipped that only the
director's reading found): **1 of 19 rows (F-5)**. Stated as
directional only: one arc, one director, a denominator the builder
assigned. The three instrument-first catches (F-7, F-8, the blind layer
scan whose positive control said SCAN BLIND) are the pattern worth
keeping: the rehearsal found what CI would have found later.

## The class that repeated

The gate-half-run family fired twice more this arc (C-009 through a pipe;
C-012 through a `;`-chained edit script), the sixth and seventh
instances. D-074's verdict file closed the pipe path for the gate; the
edit-script path is the census's next candidate check (a rule that the
commit in a chain must be gated on the script's exit, mechanically).

## What was measured, not felt

Real data: 39,660 records processed, 739/739 sealed, three clean
real-string scans (two the director's). Fuzz: 11,063 inputs, zero
escapes, 30 minutes. Tests at release: 349 (261/88). Rulings: 86 at this
file. Corrections: 12.

## Limits of this evaluation

Self-assigned classes and denominators; one arc; the director's reads
are the second position and this file is not one of them.
