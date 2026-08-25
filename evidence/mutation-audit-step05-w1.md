# Mutation audit, STEP-05 W1 (stop one)

2026-08-25, cosmic-ray 8.7.0, audit Hypothesis profile. Collection guard
ran first (9 passed). Scope: the three modules W1 changed (provenance,
sealing, schema); dedup is unchanged this workstream and carried at its
STEP-04 figures.

## Both denominators, side by side (D-029)

| | STEP-04 close | STEP-05 W1 |
|---|---|---|
| provenance | 161/195 = 82.6% | **274/342 = 80.1%** |
| sealing | 125/130 = 96.2% | **139/151 = 92.1%** |
| schema | 1/10 = 10% | **10/26 = 38.5%** |
| dedup | 49/63 = 77.8% | 49/63 = 77.8% (carried) |
| **full core** | **360/419 = 85.9%** | **472/582 = 81.1%** |

**The ratchet is DOWN, 85.9 to 81.1, and that is reported as a fact, not
explained away.** W1 added a large amount of new identity machinery
(supersession records, their attestation, their verification, the keyring,
rotation), and new code arrived less well covered than the code it joined.
The direction is real. Three runs were needed to get here: 78.1% before
kill tests, 81.1% after them plus the design fix.

## What the audit found (its whole point)

1. **The comparison-weakening class REPEATED, for the third time.** The
   new supersession verify paths carried `!=` comparisons exercised in
   only one hash ordering - the exact class the STEP-03 and STEP-04 evals
   both flagged. Writing fresh verify code re-created the gap, because the
   previous fix lived in tests rather than in a habit. Killed with
   both-ordering tests on the content hash, the prev link, the attestation
   and old_head.
2. **A kill test of mine passed for the wrong reason.** The old_head test
   forged a head that failed the EARLIER internal-consistency check, so the
   comparison it claimed to kill was never reached; the mutant stayed
   alive under a green test and the audit exposed it. Rewritten to use a
   self-consistent decoy head and to assert on the comparison's own detail
   text.
3. **A real design bug, found by a new test written for this audit.** With
   TWO rotations, the second join failed to verify: `old_head` is the
   running ledger head (the value head.json holds), but verification
   compared it against only the slice since the previous rotation. Fixed
   by comparing against every record before the join - which REMOVED the
   epoch_start concept instead of adding to it.

## Remaining survivors, dispositioned

- **95 annotation / lru_cache mutants** (provenance `str | None`
  signatures, dedup's annotated dict, schema's five cached loaders):
  equivalent classes already dispositioned at earlier closes. PEP 649 lazy
  annotations never execute; the cached functions are pure loaders.
- **provenance L274/L282** (2): the record_type dispatch comparisons.
  Behaviourally reachable but currently equivalent-in-effect: both branches
  end in the same failures for a mislabeled record, because a supersession
  run through the finding checks fails on its missing id and a finding run
  through the supersession checks fails on its missing old_head. Named as
  reasoned-equivalent, not proven.
- **provenance L305** (`continue`): removing it re-runs the finding checks
  on a supersession, which produces additional failures on an already
  failing record - no observable difference on a valid chain.
- **provenance L354** (`i == 0`): equivalent on non-negative indices, as
  dispositioned since STEP-02.
- **provenance L398** (`or {}` guard): defensive against a record with no
  provenance key, which schema validation already refuses.
- **provenance L509** (8, the `records[i + 1:]` slice family): partially
  killed this round by the backwards-remap test; the residual mutants
  shift the slice by amounts that still exclude the pre-join ids, so they
  remain equivalent on the shapes a real ledger can hold.
- **sealing L60, L99, L125, L126, L132, L190, L195, L202** (12): the
  keyring-version constant and file-write details, the chmod (platform-
  conditional, D-023), and three carried from earlier closes.
- **schema L95** (1): the `kind == "supersession"` dispatch, with the same
  reasoning as provenance L274.

Zero undispositioned. The honest summary of the equivalence claims:
they are the builder's reasoning, not machine-verified, and the
proportion of them grew this workstream because the new code is
branch-heavy.

## Limits

Adapters and the pipeline remain unmeasured by mutation. The audit
measures whether the suite notices a change, not whether behaviour is
correct.
