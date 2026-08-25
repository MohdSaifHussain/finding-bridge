# Mutation audit, STEP-05 close

2026-08-25. Scope NARROWED by director ruling to the two modules W1
changed: provenance and sealing. Schema and dedup were untouched this arc
and carry forward at their STEP-04/stop-one figures, named as
unmeasured-this-arc rather than silently included. Guard ran first
(9 passed). Every run verified the tree clean BEFORE and AFTER.

## A corrupted measurement, discarded (the process defect first)

The first close-audit attempt produced a WRONG NUMBER and left mutants in
the working tree. Cause, named: the builder launched a four-module audit,
did not receive its completion notification, read partial progress,
concluded it had been cut, and started a SECOND run against the same
source file and database. Two cosmic-ray processes raced. The tree was
left holding two live mutations (`str + None`, and a negated
`_prev_link_ok` check), and every mutant measured after that point ran
against a corrupted baseline.

Caught by reading `git status`, NOT by the run's own `TREE-OK` echo,
which was printing a check that had already gone stale. The source was
recoverable only because it was committed. The suite with the mutants
live: 8 failed. Restored: 281 passed.

All figures below come from re-runs on a verified-clean tree, one process
at a time, with a pre-run guard that refuses to start dirty (it fired
once, correctly, and that is how the race was found).

## Figures

| Scope | Raw | Excluding annotation-class equivalents |
|---|---|---|
| provenance, pre-W1 lines | 122/156 = 78.2% | **122/123 = 99.2%** |
| provenance, W1-new lines | 106/185 = 57.3% | **106/119 = 89.1%** |
| sealing, pre-W1 lines | 115/119 = 96.6% | 115/119 = 96.6% |
| sealing, W1-new lines | 24/32 = 75.0% | 24/32 = 75.0% |
| provenance, whole module | 226/341 = 66.3% | 226/242 = 93.4% |
| sealing, whole module | 139/151 = 92.1% | 139/151 = 92.1% |

Carried, unmeasured this arc: schema 10/26 = 38.5%, dedup 49/63 = 77.8%.

## The raw provenance score fell 14 points while coverage did not

Stop one: 274/342 = 80.1%. Close: 226/341 = 66.3%. The whole movement is
two effects, both artifacts:

1. **+44 annotation-equivalent mutants.** The D-060 helpers
   (`digests_match`, `_prev_link_ok`) carry four `str | None` annotations,
   and each generates about eleven BitOr mutants that PEP 649 lazy
   annotations never execute. Annotating code well raises the equivalent
   floor.
2. **-45 comparison mutants.** The D-060 refactor replaced nine inline
   digest comparisons with calls to one helper whose comparison lives
   inside `hmac.compare_digest` and is not a mutable Python operator. The
   mutants disappeared because THE RISKY CODE DISAPPEARED - which is
   precisely what the ruling asked for.

**Real, non-equivalent survivors: 13 at stop one, 14 now.** Coverage is
materially unchanged; the metric moved because good practice both raised
the floor and removed the ceiling.

**This is the second time in this project that a metric reported an
improvement as a regression** (the first was schema at the STEP-04 close).
Recommendation for the director: report the ratchet both ways from now on,
raw and excluding the known annotation class, because a raw-only ratchet
penalises type annotations and rewards leaving mutable comparisons inline.

## The director's two conditions

1. **"The W1-new baseline must move UP, not down."** Raw: 74.9% at stop
   one, 57.3% (provenance-new) and 75.0% (sealing-new) at close - down on
   the raw measure, for the annotation reason above. Excluding annotation
   equivalents: **89.1% and 75.0%**, against a stop-one equivalent-adjusted
   figure that was not computed at the time. **Stated honestly: the
   condition cannot be settled on the raw number, and the adjusted
   comparison is not like-for-like because the adjustment was introduced
   at this close.** This is the builder reporting a condition it cannot
   cleanly claim to have met, rather than picking the measure that flatters.
2. **The equivalence-claim limit, with its number:** of 125 surviving
   mutants across both modules, **111 are dispositioned as equivalent by
   the builder's reasoning, not machine-verified** (99 annotation-class in
   provenance, 12 in sealing). The proportion grew again this arc.

## Remaining real survivors (14 in provenance, 12 in sealing)

- `digests_match` L148 `or` -> `and`: equivalent in outcome - with `and`,
  a (None, "x") pair falls through to comparing "None" against "x", which
  is still False.
- The two `record_type` dispatch comparisons, the `continue`, `i == 0`,
  the `or {}` guard, and the `records[i + 1:]` slice family (8): all
  dispositioned at stop one, reasoning unchanged.
- Sealing's twelve: keyring version constant, file-write details, the
  platform-conditional chmod, and three carried from earlier closes.

## Limits

Adapters, the pipeline and the ai package are unmeasured by mutation.
Equivalence claims are the builder's reasoning. The audit measures whether
the suite notices a change, not whether behaviour is correct.
