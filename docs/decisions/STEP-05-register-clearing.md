# STEP-05: the register-clearing arc (W1 supersession/rotation, W2 caged --ai, W3 tracker JSON)

**Project:** finding-bridge | **Phase:** 5 | **Date:** 2026-08-25
**Status:** RATIFIED at drafting - the director fired OB-2's trigger by
explicit call per D-052's own terms and pre-ruled the scope below
(recorded as DEV-16). Sections B-G of the standing authorization
unchanged. ONE mid-arc stop (after W1) plus the arc close.
**Depends on:** D-051..D-057 (the identity rulings), A13 (charter
roadmap), the ratified identity paper, D-058 (the private remote and its
push policy).
**Standing rule:** top applicable standard per requirement, fetched.

**The bound warning, quoted into this contract as D-052 requires:**

> The multi-epoch verification complexity in D is the part most likely to
> be underestimated here.

**Binding consequence:** if epoch-aware verification starts growing
beyond what one careful reader can audit by eye, that is a **Section C
stop**, not a heroic push-through.

## 1. Objective

Clear the register down to items whose triggers have genuinely not fired.
Rotation becomes an instance of the supersession mechanism; the caged AI
ships without touching evidence; the last unclaimed emitter lands.

Exit criterion: the director runs a key rotation, verifies the chain
across the join, runs the pipeline with `--ai` failing and sees it degrade
to exactly the no-ai behaviour, emits tracker JSON with no sealed content,
and the register contains only OB-5, OB-7, OB-6-via-E, the semantic
preview, and the D-018 adapter pack.

## 2. Deliverables

### W1 - supersession and key rotation (FULL, no re-ask inversion)

| ID | Deliverable |
|---|---|
| W1a | `supersession` record type: schema (major bump, migration note per charter §7), committing to event type, old head, new head, the old-id-to-new-id remap, canonical form from/to, reason, and a human attestation over all of it |
| W1b | Canonical form v1 written into the chain head (D-055) if not already there |
| W1c | Ref key split from the encryption key (D-053); the ref key's permanence stated where users meet it |
| W1d | Epoch-aware `verify_chain`: walk THROUGH supersession records - old epoch under old rules, new epoch under new, the join attested |
| W1e | Human-gated CLI rotation, implemented ONLY as a supersession event; never a standalone path |
| W1f | The three D-052 controls, red before green: rotation verifying clean across the join; a forged supersession failing; a supersession claiming a remap it did not perform, failing |

### W2 - the caged `--ai` feature (FULL: it implements charter rule 2)

| ID | Deliverable |
|---|---|
| W2a | `ai/` package importable ONLY behind `--ai`; an import-tracking control (not an assertion) proves the pipeline never imports it when the flag is absent; the zero-key suite passes untouched |
| W2b | Exactly two capabilities: severity-rationale prose suggestion, taxonomy-mapping suggestion. Both land as SUGGESTED and labeled; only a human's acceptance at the gate writes anything into a confirmed finding |
| W2c | The AI sees preview and metadata by default, never unsealed content unless the operator unsealed first through the existing logged path; the limit stated where users meet it |
| W2d | Anthropic API, official docs fetched and cited first; model pinned by exact ID in config, never hardcoded; every call's prompt and response hashed into an `ai_provenance` note on the suggestion |
| W2e | Governed refusals `ai-key-missing` and `ai-unavailable`, location-not-value, which NEVER block the deterministic pipeline; a control kills the network path mid-run and proves degradation to exactly the no-ai behaviour |

### W3 - tracker JSON out-adapter (STANDARD)

| ID | Deliverable |
|---|---|
| W3a | Flat JSON array shaped for generic tracker import (summary, description carrying preview and provenance hashes, labels from taxonomy and harm flags, severity), no vendor lock; the shape recorded as a decision with alternatives named |
| W3b | Same emitter law: shared governed writer, sentinel absence with positive control, boundary rows, location-not-value refusals |

### W4 - bookkeeping

Stops' reports, close audit with both denominators, both timing numbers
with deltas, eval once at the final total, register restated.

## 3. Requirements (beyond the standing ones)

- 3.1 W1's identity changes are authorized ONLY to the extent this
  contract specifies. Anything beyond it is Section C.
- 3.2 The `anthropic` client is pre-approved, pinned, and OPTIONAL: the
  package installs and the full suite runs without it.
- 3.3 The semantic grey-scale preview stays OUT of W2. D-042's wording
  law continues to ban claiming it.
- 3.4 W2's AI never creates, edits, scores, hashes, or seals evidence
  (charter rule 2), and every AI-touched field is labeled suggested.
- 3.5 Push policy (D-058, extended): at each director-closed stop, after
  the close word only, re-run the pre-push audit as a DELTA (new objects
  since the last push, same scans) and push master. Between closes,
  nothing is pushed. Tags remain a separate future ruling.

## 4. Out of scope

The semantic preview; OB-5 fuzzing; OB-7 (needs a public repo); Option E;
the D-018 external adapter pack; any tag or release; any publication.

## 4a. Stops

- **STOP ONE, hard halt after W1.** Contents: adversarial self-review
  with quoted lines; the three controls shown red-then-green; the
  epoch-aware verify walked line by line in the report; mutation audit on
  the changed core modules with both denominators; tier re-ask. Identity
  machinery is not built upon until the director has ruled.
- **STOP TWO, arc close after W3.** Full ritual including a
  rotation-across-the-join row the director runs, an
  --ai-degrades-to-deterministic row, a tracker sentinel row; close audit
  with ratchet and both denominators; both timing numbers with deltas;
  eval once at the final total; obligations and limits by name; the
  register restated.

## 4b. Tier

- **W1: FULL, no re-ask inversion** (D-052).
- **W2: FULL** - it implements charter rule 2, which makes it safety
  surface even though it writes no evidence (director's pre-ruling).
- **W3: STANDARD**, justified: pure consumption of the frozen canonical
  finding, same shared writer, same emitter law - the STEP-02 tier line
  applied unchanged.
- Re-ask at stop one for W2/W3 only; W1's tier is fixed by D-052.

## 4c. Readings

- R1: "walks THROUGH supersession records" read as: records before the
  join keep verifying under the rules in force when they were written;
  records after verify under the new rules; the supersession record's own
  attestation is what joins them. **Confirm Y/N at stop one; proceeding
  under the plain reading meanwhile.**
- R2: with the D-053 key split, an encryption-key rotation leaves refs,
  hashes and ids untouched, so its remap is EMPTY. The mechanism still
  applies (the event is recorded and attested); the remap is simply the
  empty case, which is the cheapest possible first exercise of it.
  **Same.**
- R3: "the AI never sees unsealed content unless the operator explicitly
  unsealed first" read as: the AI path consumes the canonical finding's
  preview and metadata only; it is never handed a sealed-store plaintext
  by the tool itself. **Same.**

## 5. Exit checklist (assembled at the stops)

- [ ] W1: three controls red-then-green; rotation is only reachable as a
      supersession event; epoch verify auditable by eye.
- [ ] W1: schema major bump with migration note; canonical form v1 in the
      head; ref key split with its permanence stated.
- [ ] W2: import-tracking control proves ai/ is unimported without the
      flag; zero-key suite untouched; degradation control kills the
      network path and matches no-ai behaviour exactly.
- [ ] W2: suggestions labeled, human-accepted only, ai_provenance hashes
      recorded.
- [ ] W3: tracker sentinel absence with positive control; boundary rows.
- [ ] Audits, timings, eval, register restated; delta pre-push audit at
      each close before any push.

## 6. Deviations

**DEV-16 (the director's pre-rulings, as contract language):** the schema
major bump number and its migration-note wording, suggestion-field
naming, the tracker filename convention (following the established
sidecar pattern), and any new reason codes under the existing law are all
pre-ruled and need no stop. NOT pre-ruled, Section C as always: anything
touching sealing, hashing, attestation, head, or gate semantics beyond
exactly what W1 specifies; any new runtime dependency beyond the
`anthropic` client, which is pre-approved, pinned, and must be optional.
