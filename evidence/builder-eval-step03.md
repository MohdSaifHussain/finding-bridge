# Builder eval, STEP-03

Compiled once at the stop-two commit (named in the commit adding this
file); counts from commands per D-031. **Self-evaluation; the builder
chose the classes.**

## 1. Substantive defects

| # | Defect | Found by | Escape? |
|---|---|---|---|
| 1 | Blank pre-marker lines refused instead of skipped | B (test red, pre-commit) | no |
| 2 | DEV-14: line-initial case-variant markers silently swallowed - quiet misattribution that could change which turn seals as the probe | **D (adversarial shot at stop one)** | **full escape** |
| 3 | S3-1: D6 built ahead of the declared stop, confessed at the stop instead of PROV-ed at the temptation (process) | B (self-report) | no |
| 4 | S3-3: S:\ traceback misread risk - measurement artifact, diagnosed before belief (measurement, not product) | B | no |
| 5 | Wall-clock formatter divided ns by 1e8 (measurement, caught before reporting) | B | no |

## 2. Rates, with denominators

Product defects: 2 (rows 1-2); escaped: **1/2**. All defects incl.
process/measurement: 5; escaped: **1/5 = 20%**. Stated both ways; at
these denominators one defect moves the rate 20-50 points, so no trend
claim is made against STEP-02's 12.5-25% band beyond: the director's
review keeps finding what the builder cannot, which row 2 proves again -
the builder pointed the reviewer AT the marker rule and still missed the
case axis. That is the empirical case for the fourth quadrant staying
human, restated with this phase's evidence.

## 3. Two-sided accounting

Builder escapes caught by the director: 1 (row 2). Director escapes
caught by the builder: 0 this phase. Tool catches: row 1 (sniff test).

## 4. Debits before credits

The builder built ahead of a stop it had itself drafted; missed a
one-character-class hazard while staring at the regex that carries it;
and botched a timing formatter in the same phase that made timing a
two-number rule. Credits after: the D2 boundary tool landed with a real
red, the DEV-14 fix carried both-direction controls, and every count in
this document came from a command.

## Recompilation after the director's close ritual (2026-08-24; restated ONCE, at the commit adding this section)

The first compilation's figures above stay as written. The ritual added:

| # | Defect | Found by | Escape? |
|---|---|---|---|
| 6 | S3-CLOSE-1: emit-markdown crashed raw on a missing output parent while emit-sarif silently succeeded - the class on the exit side, unswept by the input-only boundary table | **D (ritual)** | **full escape** |

**Corrected totals:** defects 5 -> **6** (product 2 -> **3**). Fully
escaped: 1 -> **2**: product **2/3**, all-defects **2/6 = 33%**
(previously 1/2 and 1/5 = 20%). Direction: toward the less flattering
answer for the builder, twice over - both phase escapes were found by the
director doing the thing the builder had already built tooling for
(adversarial review at the stop; the ritual at close), one axis or one
side beyond where the tooling swept.

## 5. The question for the next boundary

Row 2's shape is "the builder's attention was ON the surface and the
miss was one axis over" (case, after column-0 was handled). Does a
checklist of marker-axes (position, token, case, whitespace, encoding)
become part of D2-style tables for any future grammar, or does the class
recur? If it recurs, the axis list becomes a tool.
