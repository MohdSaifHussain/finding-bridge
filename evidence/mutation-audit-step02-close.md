# Mutation audit, STEP-02 close (D-027 AUDIT cadence)

2026-08-24, cosmic-ray 8.7.0, audit Hypothesis profile, whole-tests
command (collection guard run first: 7 passed, incl. both Multitool
directions). Sequence: guard, then four per-module sessions, then a dedup
re-run verifying kills. Tree restored after every session.

## Scope change: BOTH denominators, side by side (D-029)

- **Old scope (STEP-01 close): provenance+sealing only, 329 mutants,
  287 killed = 87.2%** (the standing ratchet).
- **Same two modules at this close: 325 mutants** (surface changed by the
  S2-1 refactor), **286 killed = 88.0%.** The ratchet HELD and rose 0.8
  points on the comparable scope.
- **New scope (full core, first time dedup and schema are measured): 419
  mutants, 360 killed = 85.9%** after kill verification. This is the new
  ratchet baseline: **85.9 percent, 360 of 419 mutants, over the full
  core**, raised later, never lowered without a numbered ruling; any
  future scope change states both denominators again.

## Per module

| Module | Mutants | Killed | Survivors | Note |
|---|---|---|---|---|
| provenance | 195 | 161 (82.6%) | 34 | all previously-reasoned classes |
| sealing | 130 | 125 (96.2%) | 5 | identical to prior audit |
| dedup (first audit) | 63 | 49 (77.8%) | 14 | 3 killed at this close, verified by re-run (17 -> 14) |
| schema (first audit) | 31 | 25 (80.6%) | 6 | performance-only equivalents |

## What the first audit of dedup found (quadrant 2 earning its keep again)

Two real gaps, found by the tool, killed and verified:
1. **L50 `!=` -> `<` dropped reproduction.steps from the dedup key**:
   findings differing only in steps would silently merge - evidence loss.
   Killed by test_steps_difference_prevents_duplicate.
2. **Cluster-id truncation length (16) was pinned by nothing.** Killed by
   test_cluster_id_format_is_cl_plus_16_hex.

## Every survivor dispositioned (59 total)

- **44 annotation `|` mutants** (provenance 33: three `str | None`
  signatures x 11 operators; dedup 11: one annotated dict): equivalent
  class, PEP 649 lazy annotations never execute.
- **L291 provenance `i == 0` -> `<= 0`**: equivalent on non-negative
  indices.
- **dedup L50 `!=` -> `>`**: domain-equivalent - reproduction's keys are
  pinned to exactly {steps, environment} by the schema
  (additionalProperties false), and "steps" sorts after "environment";
  the drift test guards the key set.
- **dedup L79 `strict=True` -> `False`**: equivalent - marked and keys are
  built from the same list and cannot differ in length; strict is
  defensive only.
- **dedup L86 `> 1` -> `!= 1`**: equivalent - counts values are >= 1.
- **sealing L134/L139/L146**: as at STEP-01 close (domain-equivalent
  ambiguity comparison; index 0 = index -1 under the single-match guard;
  log-row key order not a stated guarantee).
- **sealing L80 chmod constants x2**: platform-conditional - the
  permission test skips on win32 (the D-023 limit made measurable).
- **schema lru_cache x6** (maxsize 1->0/2, decorator removed, both
  sites): performance-only; the cached functions are pure loads, so
  behaviour is identical without caching.

Zero survivors undispositioned; zero known-killable survivors left alive.

## Honest limits

Equivalence claims remain the builder's reasoning, not machine-verified.
The audit measures whether the suite notices a change, not correctness.
The Multitool route's measured limit (exits 0 on its own reported JSON
errors) is in evidence/sarif-validation-step02.md.
