# Builder eval, STEP-02

Compiled once, at the final total, against the ledger and tree at the
close commit (named in the commit that adds this file; all figures from
commands, per D-031). **Self-evaluation: the builder assigned the classes
and chose what counts. Read the rates as "most were caught" figures.**

## Definitions

As in the STEP-01 eval: a defect is something wrong in an artifact; style
hits count separately; B = builder (build-time or self-review), D =
director, T = a tool this project runs. Escape = reached the director
unfound by the builder.

## 1. Substantive defects, one line each

| # | Defect | Found by | Escape? |
|---|---|---|---|
| 1 | Commit counts systematically overstated (+3, then +4): mental tally after a8977e2 (C-005, D-031) | D | **escape** |
| 2 | S2-1: rfc8785 domain errors unhandled on untrusted input | B (self-review, from the error surface); D proved it REACHABLE via hostile hitlog and promoted severity | partial escape (reachability was the director's) |
| 3 | S2-2: botched chain made an empty placeholder commit and folded ratification into records against D-013 | B (self-caught, same report) | no |
| 4 | Collection guard's -p arg filter left `no:cacheprovider` behind ("no tests collected") | B (ran the guard before committing it) - 4th gate-half-run instance, 1st caught pre-record | no |
| 5 | schema-invalid detail echoed instance values (found in the D-036 audit the director's rule ordered) | B under D's frame | no (the rule was D's) |
| 6 | Multitool exits 0 on its own reported JSON errors; original negative control was vacuous | T+B (running the control against the real tool) | no |
| 7 | Dedup key silently droppable of reproduction.steps under one mutant (evidence-merging gap) | T (first mutation audit of dedup) | no |
| 8 | Cluster-id truncation length pinned by nothing | T (same audit) | no |

Style hits: 1 (E501 in cli.py, caught by the gate that time - the gate
held and nothing was committed red).

## 2. Rates, with denominators

Substantive defects: **8**. Fully escaped to the director: **1** (row 1)
= **1/8 = 12.5%**; counting row 2's partial: **2/8 = 25%**. Band stated
both ways: **12.5-25%**, against STEP-01's 40-60%. One defect moves the
rate 12.5 points, so treat the improvement as directional, not precise;
the denominator is small.

## 3. Two-sided accounting

- Builder escapes caught by the director: 1 full (the count treadmill - in
  our own record's named class, which sharpens it), 1 partial (S2-1
  reachability).
- Director escapes caught by the builder: 1, C-006 by the director's OWN
  motion - the JCS ruling's unforeseen crash regression; recorded under
  their name at their instruction. The builder did not catch it either
  until self-review; it is listed here because the ruling's cost analysis
  was where it belonged.
- Tool catches with no human: rows 7, 8 (first dedup audit), plus the
  guard bug's detection depending on the builder actually running it.

## 4. Debits before credits

The builder ran a kill-verification audit whose test command could not see
the kill tests (run 2, STEP-02 opening) and only caught it by reading
identical numbers; reported two invented commit counts across two rounds;
chained a commit after a gate in a way that had already bitten once; and
wrote a Multitool control that could never fail until the real tool's
behaviour was measured. The credits (S2-1 found before any reviewer,
red-first discipline held throughout, the count correction held at the
next close) come after those debits.

## 5. Repeat-class analysis

Gate-half-run: 4 instances lifetime, this phase's caught pre-record - the
first evidence the practice works (director's note, recorded). Unguarded
boundary (D-036): 3 instances lifetime; the S2-1 fix added the backstop
that should end the class for the hash path; the next new boundary is the
test. Count treadmill: 1 instance, now under a command-only rule.
Silence-shaped failures: the Multitool exit-code discovery is this
phase's member.

## 6. What this phase changed about the builder's method

Tools: canonical_dumps backstop, the collection guard (AUDIT cadence),
permanent JCS vectors, no-echo controls. Rules that are checks: counts
from rev-list only. Habit with no tool: not chaining gates and commits -
bitten once this phase (row 3, different shape), so still a habit, still
a risk, named as such.

## 7. Honest limits of this document

Eight rows is a small denominator. The classes are the builder's. Row 5's
finder attribution (B under D's frame) could defensibly be D. Anything
after the close commit belongs to no eval.

## 8. The question for the next boundary

D-036's boundary check ("what can the component below raise, and does
each surface as a reason code?") is prose. Does the transcript-in phase
turn it into a tool - an audit that enumerates raisable exceptions per
boundary - or does the class recur there? If it recurs, the prose rule
failed and must become a check (skill rule 14).
