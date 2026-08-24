# STEP-02: SARIF out-adapter, with identity resolved first

**Project:** finding-bridge | **Phase:** 2 | **Date:** 2026-08-24
**Status:** DRAFT, awaiting director rulings on Q1-Q4 and readings R1-R4.
Nothing is built until those rulings land (opening-act work - property
tests, mutation audit, collection guard - is complete and committed).
**Depends on:** STEP-01 (closed; canonical schema 0.3.0, sealed store,
provenance chain with attestation + head, ledger workspace, ruling D-030),
D-027 opening act (ratchet 87.2 percent, 287 of 329, provenance and
sealing only).
**Standing rule:** every implementation follows the top applicable
standard; each requirement names its governing standard.

## 1. Objective

Emit confirmed findings as SARIF 2.1.0 that a strict consumer accepts,
having first settled finding identity's canonical serialization (OB-3)
while the change is still free. Per D-030 this phase is the first strict
test of the canonical schema's sufficiency.

Exit criterion, one line: the director generates a SARIF file from the
fixture pipeline, watches it pass BOTH validators (own schema check and
the Microsoft SARIF Multitool), watches a deliberately corrupted file fail
both, and finds no sealed content in the emitted SARIF.

## 2. Deliverables

| ID | Deliverable | Governing standard(s) |
|---|---|---|
| D1 | OB-3 resolution, FIRST: adopt RFC 8785 or re-affirm DEV-2, per Q3 ruling; if adopted: implementation, golden vectors re-pinned, migration note | RFC 8785 (https://www.rfc-editor.org/rfc/rfc8785, to fetch at build); ruling D-030 condition 3 |
| D2 | The identity-family paragraph (OB-2/OB-3/OB-6 in one view): does a store created today survive each change, and the one migration story - carried in §4d below and into docs | Ruling D-030 condition 4 |
| D3 | Canonical schema growth IF SARIF requires it: each field a numbered decision; drift test enforces mapping table updates | Charter §7; D-003 |
| D4 | `adapters/out/sarif.py` (canonical -> SARIF 2.1.0), location representation per Q1 ruling, taxa for owasp_llm/saif | OASIS SARIF v2.1.0 (fetched 2026-08-24: result.locations not mandated; logicalLocation §3.33; result.taxa §3.27.8) |
| D5 | Dual validation: own check against the official SARIF 2.1.0 JSON schema + Microsoft SARIF Multitool, with a negative control failing both | github.com/microsoft/sarif-sdk; npm package @microsoft/sarif-multitool (npx; dotnet SDK absent on this machine) |
| D6 | CLI `emit-sarif`, wiring only; refusals with reason codes | Charter §5.2 |
| D7 | Tier re-ask at the review stop, ruled and recorded | D-001; skill 4b mechanism |
| D8 | Outcome + builder eval + close-time mutation audit (scope widened to full core: BOTH denominators stated side by side per D-029) | D-027; D-029 |

## 3. Requirements

- 3.1 D1 completes and is RULED before a line of sarif.py exists; adopting
  JCS after mapping work means redoing it (D-030 condition 3).
- 3.2 SARIF emission consumes only confirmed ledger findings; unconfirmed
  refuses with reason code `unconfirmed` (charter rule 3).
- 3.3 No sealed content in emitted SARIF: sentinel-absence test with the
  positive control on the store (contract-3.4 pattern; reading R1 of
  STEP-01 applies unchanged).
- 3.4 The location decision (Q1) is implemented exactly as ruled, never as
  what the first draft happened to emit.
- 3.5 Both validators run in the suite; the negative control (corrupted
  SARIF) fails BOTH with distinct errors; one validator green is a null
  signal about the other (skill rule 5).
- 3.6 All STEP-01 standing rules hold: no AI, no keys, format assertion,
  gate-field guard, synthetic fixtures (D-012), official sources (3.12).
- 3.7 GATE stays under 60 seconds; wall-clock reported at close (D-027);
  currently 16.0s incl. the collection guard.
- 3.8 If a needed tool cannot run here (e.g. npx Multitool fails), that is
  reported with an alternative, not forced (D-027).

## 4. Out of scope

- Transcript-in (next contract). FLARE-AI export, promptfoo, PyRIT.
- OB-2 (rotation) and OB-6 (cross-store identity): NOT built here; D2 is
  one paragraph of analysis, not a design project (director's words).
- Actual GitHub ingestion: needs a remote, which does not exist and is its
  own future decision; see R3.
- Any remote, push, or release act.

## 4a. Review stop

- Halt after D1-D3 (identity resolution, family paragraph, any schema
  growth), before D4-D6 (adapter, validators, CLI). The FULL half is
  everything that changes bytes feeding content_hash / attestation / head
  or grows the canonical schema; reviewed before anything is built on it.
  Template 4 self-review quoting lines; the director rules before D4.

## 4b. Tier, with a binding re-ask

- Proposed (awaiting the explicit yes as part of ratification): SPLIT.
  **FULL for D1-D3** - canonical serialization and schema identity are the
  spine, and the director's prior says anything touching them is FULL.
  **STANDARD for D4-D6** - out-adapter mechanics are proven (markdown),
  pure translation downstream of a frozen canonical finding. **The line:**
  a change is FULL if it alters bytes that feed content_hash, attestation,
  or head, or adds/changes a canonical schema field; STANDARD if it only
  consumes the canonical finding.
- Re-ask at the review stop (deliverable D7). **Default:** the split
  stands (D4-D6 proceed STANDARD). **Discharge standard, ruled now:**
  raising D4-D6 to FULL requires naming, in a numbered ruling, a concrete
  finding showing the adapter half touches identity after all. **Forecast:**
  the default holds, unless Q1's ruled location design turns out to
  require a schema field (then that field's work is FULL under the line
  above, and only that work).
- Always-on at every tier: skill rules 4, 5, 7, 8; sealing default-on;
  the three charter rules.

## 4c. Readings

- R1: SARIF-out consumes only the confirmed ledger, refusing unconfirmed
  findings with `unconfirmed`, exactly as markdown does. **Confirm Y/N.**
- R2: "OB-3 comes due at the start" read as: D1 is completed AND ruled
  before any sarif.py code is written; the review stop then covers D1-D3
  together. **Confirm Y/N.**
- R3: "Name a real consumer" read as: GitHub Code Scanning is the design
  target (the charter's SARIF headline), but actual ingestion requires a
  remote, so this phase proves consumer acceptance via the Multitool's
  correctness rules plus a locally verifiable consumer at the close
  (VS Code SARIF Viewer, director-run); the GitHub ingestion test becomes
  a named obligation due when a remote exists. **Confirm Y/N.**
- R4: The npm-distributed Multitool (`npx @microsoft/sarif-multitool
  validate`) counts as the official Multitool route; the dotnet SDK is
  absent on this machine. If the npm route fails at build time, that is
  reported with an alternative per 3.8. **Confirm Y/N.**

## 4d. The identity-family paragraph (D2, carried per D-030 condition 4)

OB-2, OB-3 and OB-6 are one problem wearing three hats: a finding's
identity is derived from things that can change. A store created today
survives none of the three unchanged. Under OB-2 as scoped, rotating the
sealing key re-derives the ref key, so every sealed ref changes, so every
content_hash, id, attestation and the head break. Under OB-3, adopting
RFC 8785 changes canonical bytes, so every content_hash, id and
attestation changes and the head breaks - which is exactly why D1 happens
now, while no store outside test fixtures exists and the change is free.
Under OB-6, the store itself survives but identity does not cross store
boundaries, so correlation dies at any trust boundary. The one migration
story all three share, when any of them must be paid for a live store: a
chained SUPERSESSION EVENT - a ledger record, human-confirmed like any
finding, committing (old head, new head, the per-finding old-id to new-id
map), so history stays verifiable THROUGH the transition instead of being
broken by it. Rotation and re-canonicalization then become instances of
one mechanism instead of two inventions. Nothing of this mechanism is
built in STEP-02; this paragraph exists so that when one of the three
comes due, the answer was thought once, calmly, in advance.

## 5. Exit checklist

- [ ] D1 ruled and landed before sarif.py existed (git history is the
      evidence).
- [ ] `pytest` green, key vars scrubbed in-suite; GATE wall-clock
      reported, under 60s.
- [ ] `ruff check` AND `ruff format --check` clean, two named commands.
- [ ] Happy path: director generates SARIF from the fixture pipeline;
      both validators pass; the file opens in the local consumer (R3) and
      renders findings with the ruled location representation.
- [ ] Positive control: sealed sentinel present in the store, recoverable
      by explicit unseal only.
- [ ] Negative: sentinel absent from the emitted SARIF (grep exit 1).
- [ ] Negative: deliberately corrupted SARIF fails BOTH validators, with
      distinct error output from each (3.5).
- [ ] Negative: emit-sarif over an unconfirmed candidate refuses
      (`unconfirmed`).
- [ ] Negative: drift test fires if any D3 schema growth lands without
      its mapping row (demonstrated on the real change, as in STEP-01).
- [ ] Close-time mutation audit run with BOTH denominators stated
      (old scope and new scope side by side, D-029).
- [ ] Tier re-ask ruled at the stop (D7).
- [ ] Outcome appended; obligations and limits carried by name (OB-1,
      OB-2-blocked-on-OB-6, OB-4, OB-5, OB-6, the GitHub-ingestion
      obligation if R3 confirms, and all standing limits).
