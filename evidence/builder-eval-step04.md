# Builder eval, STEP-04

Compiled once at the stop-two commit (named in the commit adding this
file). Counts from commands (D-031). **Self-evaluation: the builder chose
the classes.**

## 1. Substantive defects

| # | Defect | Found by | Escape? |
|---|---|---|---|
| 1 | README's install command `pip install -e . -c constraints.txt` fails in a fresh venv - our own D-047 had predicted the shape | **D (docs read)** | **full escape** |
| 2 | Marker-variant family: space, tab, full-width colon and indentation all silently swallowed a turn | **D (ruled the sweep; builder found the specific variants by running them)** | **partial escape** - the axis was the director's, the variants the builder's |
| 3 | Attestation comparison tested in only one hash ordering | T (close mutation audit) | no |
| 4 | README missing the OB-4 bound sentence and D-042's ruled wording | T (the overclaim check, while being written) | no |
| 5 | Build artifacts (build/, dist/) committed | B (read the commit's file list) | no |
| 6 | BOM before the first marker refused with a confusing message | B (found while sweeping the family) | no |
| 7 | A heredoc mangled `\n` escapes while editing a test - the scripted-edit hazard, again | B (syntax error, immediate) | no |

## 2. Rates, with denominators

Substantive defects: **7**. Fully escaped: **1** (row 1). With row 2's
partial: **2**. So **1/7 = 14%** fully, **2/7 = 29%** counting the
partial. Previous phase: 2/3 product, 2/6 total. At these denominators
one defect moves the rate ~14 points; no trend is claimed.

What is worth saying without a rate: **both director findings this phase
were in things the builder had already built tooling for.** Row 1 was in
a doc whose examples the builder claimed were "run first, then written" -
and the install block was the one that was not. Row 2 was one axis beyond
the axis the builder had just fixed. That is the same shape as STEP-03's
escapes, now three phases running, and it is the strongest evidence in
this project that the fourth quadrant stays human.

## 3. Two-sided accounting

Builder escapes caught by the director: 1 full, 1 partial. Director
escapes caught by the builder: 0. Tool catches with no human: rows 3, 4.

## 4. Debits before credits

The builder wrote "every command was run before it was written down" and
then shipped an install command it had not run, in the same phase whose
own record predicted that command would fail. It committed build
artifacts. It hit the heredoc hazard the skill warns about, again.
Credits after: the overclaim check earned its existence on day one by
catching the builder's own doc gaps; the family sweep was done by running
every variant rather than reasoning about them; and the schema mutation
result was investigated rather than reported as a regression.

## 5. Repeat-class analysis

- **Claim-not-verified** (row 1): the builder asserted a practice
  ("ran first") that it had not applied uniformly. New class this phase,
  and the most serious, because it undermines the evidence rules the
  project runs on. The check now exists (broken-command test), but the
  general form - "a claim about my own process" - has no tool.
- **One-axis-over** (row 2): third phase running.
- **Comparison-weakening** (row 3): second occurrence, both caught by the
  audit, which is the audit doing its job.
- **Scripted-edit hazard** (row 7): recurring; still no tool, still a
  habit.

## 6. Honest limits of this document

Seven rows is a small denominator. The classes are the builder's. Row 2's
attribution is genuinely arguable either way. Anything after the compile
commit belongs to no eval.

## 7. The question for the next boundary

Row 1's class is "the builder claimed a process it did not follow". Is
there a checkable form of that, or does it stay a director-only catch? A
candidate: docs that carry executable examples get their examples
executed by a test. That would have caught row 1 mechanically. If the
next phase does not build it and the class recurs, the honest conclusion
is that process claims cannot be self-audited.
