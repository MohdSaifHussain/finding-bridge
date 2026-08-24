# Mutation audit, STEP-02 opening act (D-027 AUDIT cadence)

Measured the core exactly as shipped at STEP-01 close (`72a9cbb`; kill tests
added at `8ada0ad`, no source code changed). Tool: cosmic-ray 8.7.0
(adopted after mutmut was found documented POSIX-only; evaluation in the
D-027 addendum). Per-mutant suite runs under the `audit` Hypothesis profile
(max_examples=15) so properties stay in the kill set inside the budget.

**Reproduce with one command sequence (from repo root):**
```
pip install cosmic-ray
set HYPOTHESIS_PROFILE=audit
cosmic-ray init cr-provenance.toml cr-p.sqlite && cosmic-ray exec cr-provenance.toml cr-p.sqlite && cr-report cr-p.sqlite
cosmic-ray init cr-sealing.toml cr-s.sqlite && cosmic-ray exec cr-sealing.toml cr-s.sqlite && cr-report cr-s.sqlite
```

## Scope and budget

Full-core init produced **425 mutants**; projected wall time exceeded the
20-minute budget, so scope narrowed to **provenance + sealing** per D-027's
binding rule (dedup and schema modules are unmeasured this audit and carry
to the next). Narrowed scope: **329 mutants** (199 provenance, 130 sealing).

## Runs, with the defective one kept in the record

| Run | Suite at | Result | Wall clock |
|---|---|---|---|
| 1 (baseline audit) | `c24159d` (pre-kill-tests) | 259/329 killed = **78.7%** (44 + 26 survivors) | 9m39s |
| 2 (defective, kept as record) | `8ada0ad` | identical 44+26: the enumerated test-command predated test_mutation_kills.py and never ran it - a gate run without its ammunition, caught by reading the numbers, fixed by whole-dir collection (commit in history) | 9m45s |
| 3 (verification) | post-fix configs | **287/329 killed = 87.2%** (37 + 5 survivors) | 9m28s |

Plus one targeted kill after run 3 (provenance L219, below), demonstrated
red/green by hand-applied mutant rather than a fourth full run. The ratchet
is set from the MEASURED run, not the projection.

## Ratchet baseline

**87.2 percent, 287 of 329 mutants, over provenance and sealing only**
(ruled wording, D-029: the scope is part of the number, and this figure is
never restated as "the core"). Set 2026-08-24. Raised later, never lowered
without a numbered ruling; any future audit that widens or narrows scope
restates both the old and new denominators side by side. Expected
next-audit value if nothing regresses: ~87.5% (288/329) once run 4
measures the L219 kill.

## Every surviving mutant, dispositioned

**Provenance (37 at run 3):**

| Mutants | Location | Disposition |
|---|---|---|
| 33 | L91/L115/L167: `\|` in type annotations (`str \| None`), 11 operator variants each | **Equivalent class:** Python 3.14 evaluates annotations lazily (PEP 649), so these never execute; killable only by introspecting annotations, which tests behaviour of nothing. |
| 2 | L77/L162: `ensure_ascii=False` in chain-head serialization | **Equivalent:** the head payload is `[count, last_content_hash]` - an int and a 64-hex string or null, always ASCII; the flag can never change the bytes. (The same mutants in content/attestation hashing were REAL and are killed by the golden vectors.) |
| 1 | L267: `i == 0` -> `i <= 0` | **Equivalent:** `i` ranges over non-negative list indices; `<= 0` is `== 0` on that domain. |
| 1 | L219: `or` -> `and` in the confirmation-claim check | **KILLED** post-run-3: `test_confirmed_at_alone_is_still_a_confirmation_claim`; red on hand-applied mutant, green on real code, observed this session. This was a real gap: a record claiming only `confirmed_at` verified clean under the mutant. |

**Sealing (5 at run 3):**

| Mutants | Location | Disposition |
|---|---|---|
| 2 | L80: `0o600` NumberReplacer | **Platform-conditional:** the permission test skips on win32 (the D-023 Windows ACL limit made measurable); killable on POSIX, unkillable on the machine the audit runs on. Carried, not padded. |
| 1 | L134: `> 1` -> `!= 1` | **Equivalent:** zero matches return earlier as blob-missing, so the live domain is len >= 1, where `!= 1` and `> 1` coincide. |
| 1 | L139: `matches[0]` -> `matches[-1]` | **Equivalent:** reached only when exactly one match exists (the ambiguity guard), where index 0 and -1 are the same element. |
| 1 | L146: `sort_keys=True` -> `False` in exposure-log rows | **Equivalent w.r.t. stated guarantees:** rows are consumed as parsed JSON; byte-level key order is not a guarantee anywhere, and asserting it would be a padded score. |

Totals at run 3: 42 survivors = 1 killed post-run + 39 equivalent (with
reasons above) + 2 platform-conditional. No survivor is undispositioned.

## What the audit actually found (quadrant 2 verdict)

Three real gaps no prior test or review named: the L219 confirmation-claim
gap (a verify path with an exploitable meaning), the comparison-weakening
survivals masked by id-mismatch redundancy (closed with both-ordering
tamper tests), and the exposure-row arithmetic family (closed with absolute
numbering). The layer named specific failures it caught; it is not a
decoration.

## Honest limits of this audit

- Mutation testing measures whether the suite notices a change, not whether
  behaviour is correct (D-027 limit, restated).
- dedup.py and schema.py are UNMEASURED this audit (budget narrowing);
  carried to the next audit by name.
- Equivalence claims are the builder's reasoning, quoted line by line above
  but not machine-verified; a wrong equivalence claim is a hidden gap.
- Run 2's defect (test-command omission) is the third instance this project
  of a gate half-run; the whole-dir fix removes the enumeration class but
  nothing yet checks that the audit config's command collects every test
  file.
- GATE wall-clock after the opening act: 9.2s of the 60s budget
  (126 passed, 1 skipped).
