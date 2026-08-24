# Mutation audit, STEP-04 close (D-027 AUDIT cadence)

2026-08-25, cosmic-ray 8.7.0, audit Hypothesis profile, whole-tests
command. Collection guard ran first: 9 passed. Tree restored after every
session.

## Headline

**86.6 percent, 349 of 403 mutants, full core.** Previous baseline:
85.9 percent, 360 of 419, full core (STEP-02 close). Both stated side by
side per D-029, because the denominator moved and a moved figure with one
number visible is how a ratchet becomes a ceiling.

## Per module, with both audits' numbers

| Module | Then (STEP-02 close) | Now | Note |
|---|---|---|---|
| provenance | 161/195 killed, 34 survived | 161/195 killed, 34 survived | one new survivor appeared and was killed, see below |
| sealing | 125/130, 5 survived | 125/130, 5 survived | unchanged |
| dedup | 49/63, 14 survived | 49/63, 14 survived | unchanged |
| schema | 25/31, 6 survived | 1/10, 9 survived | see "the schema result" |
| **total** | **360/419 = 85.9%** | **349/403 = 86.6%** | |

## Two real results

### 1. The attestation comparison was only ever tested one way

A new survivor appeared at `provenance.py:254`, `if attestation !=
expected` weakened to `<`. The attestation path had only been exercised
with one ordering of stored versus expected hash, so a weakened
comparison passed by luck. This is the SAME class killed at the STEP-02
close for content hashes, which the STEP-03 eval named as a repeat class
to watch. Killed by
`test_attestation_tamper_detected_in_both_hash_orderings`, which
constructs a forged attestation both below and above the real one.
Verified by re-run: provenance survivors 35 -> 34.

### 2. The schema result: removing risky code LOWERED the score

Schema went from 31 mutants (6 survivors, 80.6% killed) to 10 mutants
(9 survivors, 10% killed). That looks like a collapse and is the
opposite.

The W2b refactor replaced
`Path(__file__).resolve().parents[3] / "schemas" / ...` with
`importlib.resources`. The old path arithmetic generated roughly 21
killable mutants; the code that produced them is gone. What remains is
9 `lru_cache` decorator mutants (three cached loaders x maxsize-0,
maxsize-2, decorator-removed), all in the equivalent class dispositioned
at the STEP-02 close, plus one killed exception-replacer.

**The finding about the metric, not the module:** deleting risky code
lowers the mutation score, because the killable surface shrinks while the
equivalent-mutant floor stays put. A ratchet read without its denominator
would call this a regression and push toward keeping fragile code. This
is why D-029 exists, and it is the first time the rule has actually
mattered.

## Survivors, all dispositioned

- **44 annotation `|` mutants** (provenance 33, dedup 11): PEP 649 lazy
  annotations never execute. Equivalent.
- **9 schema `lru_cache` mutants**: performance-only; the cached
  functions are pure loaders. Equivalent.
- **provenance L291 `i == 0` -> `<= 0`**: equivalent on non-negative
  indices.
- **dedup L50, L79, L86**: domain-equivalent as dispositioned at the
  STEP-02 close (schema-pinned key set, same-length zip, counts >= 1).
- **sealing L134, L139, L146**: domain-equivalent as before.
- **sealing L80 chmod constants (2)**: platform-conditional; the
  permission test skips on win32 (the D-023 limit made measurable).

Zero undispositioned. Zero known-killable left alive.

## Scope note

Adapters remain unmeasured by mutation (R4 of the STEP-03 contract,
carried). W3 added `flare_ai.py`, so the unmeasured adapter surface grew
this phase; no baseline was seated for adapters, so no adapter
denominator is claimed.

## Honest limits

Equivalence claims are the builder's reasoning, not machine-verified.
The audit measures whether the suite notices a change, not whether
behaviour is correct.
