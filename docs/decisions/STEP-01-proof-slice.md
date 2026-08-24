# STEP-01: v1 proof slice

**Project:** finding-bridge | **Phase:** 1 of the v1 arc | **Date:** 2026-08-24
**Status:** Ratified by the director 2026-08-24 (rulings D-008 through D-013;
readings R1-R4 all confirmed Y). In progress from D1. Per D-013 this ratified
contract is never amended in place; it is only extended by numbered deviation.
**Depends on:** Phase 0 (ratified charter at commit `8a48a7a`; rulings D-001
through D-007; specifically the D-002 slice definition, the D-003 drift-test
condition, and the charter's three non-negotiable rules).
**Standing rule:** every implementation follows the top applicable standard for
what is being built. Each requirement below names its governing standard.

## 1. Objective

Prove the thesis end to end with the thinnest complete slice: garak hitlog in,
then provenance + sealing + dedup + human gate, then a markdown finding packet
out, with the whole pipeline deterministic and key-free (charter rule 1).

Exit criterion, one line: the director runs the pipeline on a bundled fixture
with no API key set, reads the emitted packet by eye, and finds preview and
metadata but no raw-harm content; every negative path below refuses with its
stated reason code.

## 2. Deliverables

| ID | Deliverable | Governing standard(s) |
|---|---|---|
| D1 | Canonical finding schema (`schemas/finding.schema.json`) + fixtures, per charter §7 | JSON Schema draft 2020-12 (https://json-schema.org/specification, fetched before implementation) |
| D2 | Field-mapping table (canonical -> FLARE-AI schema, canonical -> SARIF 2.1.0) + drift test, in the SAME commit as D1's first schema file | Ruling D-003; SARIF v2.1.0 (OASIS spec, verified 2026-08-24); FLARE-AI schema (arXiv 2606.31567 + ai-reports.org, fetched at build time) |
| D3 | `core/provenance.py`: SHA-256 hashing, ISO 8601 timestamps, hash chain + verify, with tests | FIPS 180-4 via Python `hashlib`; RFC 3339/ISO 8601 via `datetime` (official Python docs, fetched) |
| D4 | `core/sealing.py`: seal-by-default, preview generation, explicit unseal + exposure logging, with tests | Charter §6; Fernet from pyca/cryptography per ruling D-010, official docs fetched and cited before implementation |
| D5 | `core/dedup.py`: content-hash dedup, with tests | Charter §5.2; same hash standard as D3 |
| D6 | In-adapter `adapters/in/garak.py` + fixture + round-trip test | garak hitlog JSONL structure per NVIDIA/garak source (`garak/evaluators/base.py`, fetched at build time; same source the merged DefectDojo parser cited) |
| D7 | Human-gate review flow in CLI (confirm/reject, severity confirm, identity into provenance) | Charter rule 3; identity from git config user.name + email per ruling D-011 |
| D8 | Out-adapter `adapters/out/markdown.py` + test: packet carries preview + metadata, never raw harm | CommonMark (https://spec.commonmark.org/, fetched); charter §6 |
| D9 | Tier re-ask at the review stop, ruled and recorded | Ruling D-001 binding condition; skill tier mechanism |
| D10 | Phase outcome appended here + DECISIONS entries for material choices | Template 1 outcome skeleton; Template 7 |

## 3. Requirements

- 3.1 The full pipeline runs with zero API keys set; the test suite scrubs
  key-bearing environment variables and asserts the pipeline still passes.
  (Charter rule 1.)
- 3.2 No AI touches any code path in this phase; the `ai/` package is not
  created. (Charter rule 2; D-002 scope.)
- 3.3 Nothing is emitted as a confirmed finding without the human gate;
  emitting an unconfirmed finding refuses with a distinct reason code.
  (Charter rule 3.)
- 3.4 Sealing defaults ON. The emitted packet never contains raw sealed
  content; the test proves it by sentinel search, with a positive control
  proving the sentinel exists in the sealed store. (Charter §6; skill rule 5.)
- 3.5 Every unseal writes an exposure log entry (who, when, which finding);
  unseal without the explicit flag refuses with its own reason code.
  (Charter §6.)
- 3.6 Chain verification fails on a tampered store with a distinct reason
  code; the negative control demonstrates it. (Charter provenance rule.)
- 3.7 The drift test fails when the canonical schema changes without the
  mapping table changing; demonstrated once in a throwaway change, then
  reverted. (Ruling D-003.)
- 3.8 Missing source fields emit null/unknown, never invented values; a
  fixture with absent fields proves it. (Charter: never fabricate.)
- 3.9 Style gate is BOTH `ruff check` AND `ruff format --check`, named
  separately in the exit checklist; one green is a null signal about the
  other. (Skill rule 5.)
- 3.10 Python 3.12+, `pip install -e .` layout per charter §Tech stack.
- 3.11 Adapters are pure translation; sealing/hashing live only in `core/`.
  (Charter §Adapters.)
- 3.12 Any framework or format decision fetches its current official source
  first and cites the URL in the commit or decision note. (Skill rule 3.)
- 3.13 The sealing key lives in a local file outside the repo tree and is
  never committed; sealing refuses with its own reason code if the key path
  resolves inside the repo tree. (Ruling D-010.)
- 3.14 Fixtures are synthetic with harmless sentinel strings; no real harmful
  model output is ever committed, in any phase, ever. (Ruling D-012,
  standing safety rule in CLAUDE.md.)

## 4. Out of scope

- Transcript in-adapter, SARIF out-adapter (v1 completion, own contracts).
- FLARE-AI export, promptfoo, PyRIT, tracker/xlsx outputs, `--ai` anything.
- Clustering beyond exact content-hash dedup (charter reserves clustering;
  the slice ships exact-hash dedup only, and says so as a limit).
- Session-exposure hints, retest replay.
- Any remote, any publish, any release act.

## 4a. Review stop

- Halt after D1-D5 (schema, mapping table, provenance, sealing, dedup),
  before D6-D8 (adapters, CLI, packet). The core carries every guarantee the
  charter makes; if it is wrong, the adapters would be built on the wrong
  thing and reviewed too late. At the stop: adversarial self-review per
  Template 4, quoting exact lines for (a) determinism/no-AI in the evidence
  path, (b) seal-by-default enforcement, (c) each negative path refusing with
  its reason code, (d) the D-003 drift test failing on an unmapped change.
  The director rules on findings before D6 begins.

## 4b. Tier, with a binding re-ask

- Tier for this phase: FULL, ruled by the director 2026-08-24 (D-008).
- Re-ask: at the review stop the tier is re-ruled explicitly (this is
  deliverable D9, not a habit). **Default:** drop to STANDARD for the back
  half (D6-D8: adapters, CLI, packet). **Discharge standard, ruled now and
  not after the evidence is in:** continuing at FULL requires naming, in a
  numbered ruling, a concrete finding attributable to a FULL-only practice.
  **Forecast, recorded in advance:** the builder expects the gate to fire
  (drop to STANDARD), because the back half is pure translation code under
  D-001's own mapping, unless the stop surfaces a safety coupling inside an
  adapter. If the tier changes, the change is a numbered deviation against
  this contract, never a quiet edit.
- What holds at every tier: skill rules 4, 5, 7, 8; sealing default-on;
  the charter's three non-negotiable rules.

## 4c. Readings

- R1: D-002's "markdown packet out". Read as: the packet renders preview and
  structured metadata only; raw sealed content never appears in any emitted
  artifact, even encrypted inline. **Confirmed Y, director, 2026-08-24.**
- R2: D-003's "in scope from the first schema commit". Read as: the mapping
  table and its drift test land in the same commit as the first schema file,
  not later in the phase. **Confirmed Y, director, 2026-08-24.**
- R3: "human gate" in this slice. Read as: a CLI review flow that confirms or
  rejects candidates and confirms severity, recording who and when into
  provenance; no AI assistance exists in this phase at all. **Confirmed Y,
  director, 2026-08-24.**
- R4: "STEP-01" numbering. Read as: phase contracts are named STEP-NN under
  `docs/decisions/`, starting at STEP-01 for this slice; Phase 0 keeps its
  record in DECISIONS.md and the charter amendment log, with no STEP-00 file
  written after the fact. **Confirmed Y, director, 2026-08-24.**

## 5. Exit checklist

- [ ] `pytest` green with key-bearing env vars scrubbed (3.1); the scrub is
      shown in the run the director performs, not asserted.
- [ ] `ruff check` clean AND `ruff format --check` clean, run as two named
      commands (3.9).
- [ ] Happy path: pipeline on the bundled fixture emits a markdown packet;
      the director reads it by eye and finds preview + metadata, and finds
      the sealed sentinel string absent (3.4).
- [ ] Positive control: the sealed sentinel string IS present in the sealed
      store (proves the absence check can detect).
- [ ] Negative: chain verify on a tampered store exits nonzero with reason
      code `chain-broken` (3.6).
- [ ] Negative: emit of an unconfirmed finding refuses with reason code
      `unconfirmed` (3.3).
- [ ] Negative: unseal without the explicit flag refuses with reason code
      `unseal-not-explicit`; with the flag, the exposure log gains a
      who/when/finding row the director reads (3.5).
- [ ] Negative: drift test fails on a schema change without a mapping-table
      change, demonstrated and reverted (3.7).
- [ ] Null-field fixture emits null/unknown, nothing invented (3.8).
- [ ] Tier re-ask ruled at the stop and recorded (D9).
- [ ] Outcome section appended; obligations and limits carried forward by
      name, including: exact-hash dedup only (no clustering), and the
      Phase 0 verification limits, unchanged.

## 6. Deviations

**DEV-1 (tier re-ask outcome, ruled by the director at the review stop,
2026-08-24).** Contract 4b's default was a full drop of D6-D8 to STANDARD;
the builder's recorded forecast agreed. The gate fired PARTLY: the director
ruled D6 (garak in-adapter) and D8 (markdown out-adapter) drop to STANDARD as
pure translation, while **D7 (human gate) stays FULL**, discharging 4b's
standard with a named FULL-only finding, quoted:

> "R-1 (safety, charter rule 3). The human gate record is not tamper-evident.
> src/finding_bridge/core/provenance.py:20 excludes the whole 'provenance'
> object from the hash; confirm() writes confirmed_by and confirmed_at into
> that same object [...] So editing who confirmed a finding, or when, leaves
> the chain verifying clean. [...] A field anyone can rewrite silently is not
> a record."

The director's ground: R-1 exists because a FULL adversarial review
re-derived the hash coverage instead of trusting the chain's own passing
tests, and D7 is the deliverable that writes the very field R-1 showed was
unprotected. The builder's forecast is scored: partly wrong (predicted a
full drop). Recorded here as a numbered deviation, not a quiet edit, per
D-013.

**DEV-2 (canonical JSON form diverges from RFC 8785 JCS; ruled at round-2
close, R-5).** The content-hash serialization (provenance.py
canonical_content_bytes, dedup.py dedup_key) uses Python
`json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)`, not
RFC 8785. Two named divergences and their reachability:
1. Key ordering: JCS sorts property names by UTF-16 code units; Python
   sorts by code point. They disagree only when a key mixes characters at
   or above U+E000 with supplementary-plane characters. Reachable in this
   schema ONLY through keys of `reproduction.environment`, the sole
   free-form object; every schema-fixed key is ASCII and pinned by the
   drift test.
2. Number serialization: JCS requires ECMA-262 7.1.12.1 shortest-round-trip
   serialization, which Python's json does not guarantee for every double.
   Reachable via non-integer `severity.score` floats.
JCS deliberately performs no Unicode normalization, so current "as is"
string handling already matches it. Discharge path: OB-3 (adopt JCS with
fetched official sources, or re-affirm this deviation with reasons) before
the SARIF adapter ships; cannot be discharged by silence (director
condition).

**DEV-3 (charter layout name `adapters/in/` is not importable Python).**
The charter's §5.2 layout names `adapters/in/`; `in` is a Python keyword and
cannot be a module path. Implemented as `adapters/in_/` with `adapters/out/`
unchanged. A naming deviation forced by the language, recorded rather than
silently absorbed; charter text left as is (the amendment log already
governs charter changes, and this is an implementation-layer rendering of
the same design).
