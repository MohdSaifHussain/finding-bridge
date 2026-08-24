# STEP-01: v1 proof slice

**Project:** finding-bridge | **Phase:** 1 of the v1 arc | **Date:** 2026-08-24
**Status:** CLOSED, 2026-08-24, by the director's explicit word after their
independent phase-close ritual at commit `72a9cbb`. D1-D10 shipped; the exit
criterion met as written: the director ran the pipeline on the bundled
fixture with no real key set, read the packet by eye, found preview and
metadata and no raw harm, and every negative path refused with its stated
reason code. Ratified 2026-08-24 (D-008..D-013; readings R1-R4 confirmed);
extended only by numbered deviations DEV-1..DEV-3 per D-013.
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

- [x] `pytest` green with key-bearing env vars scrubbed (3.1); the scrub is
      shown in the run the director performs, not asserted.
      - Director's run: ANTHROPIC_API_KEY=dummy set, 105 passed 1 skipped,
        exit 0, 1.32 seconds.
- [x] `ruff check` clean AND `ruff format --check` clean, run as two named
      commands (3.9).
      - Director observed both, exit 0 each.
- [x] Happy path: pipeline on the bundled fixture emits a markdown packet;
      the director reads it by eye and finds preview + metadata, and finds
      the sealed sentinel string absent (3.4).
      - Director read packet.md by eye; sentinel absent, with their own
        positive control (the detector fires on the fixture itself).
- [x] Positive control: the sealed sentinel string IS present in the sealed
      store (proves the absence check can detect).
      - Director-run explicit unseal recovered it, two exposure rows.
- [x] Negative: chain verify on a tampered store exits nonzero with reason
      code `chain-broken` (3.6).
      *(restated: the director's hand tamper surfaced `attestation-tampered`
      and `head-mismatch`; the literal `chain-broken` mode is test-covered
      at test_provenance.py test_recomputed_tamper_breaks_chain; all are
      distinct modes of the 3.6 family)*
- [x] Negative: emit of an unconfirmed finding refuses with reason code
      `unconfirmed` (3.3). - Test-covered; CLI path observed.
- [x] Negative: unseal without the explicit flag refuses with reason code
      `unseal-not-explicit`; with the flag, the exposure log gains a
      who/when/finding row the director reads (3.5).
      - Director observed both, including attempt+outcome rows (D-022).
- [x] Negative: drift test fails on a schema change without a mapping-table
      change, demonstrated and reverted (3.7).
      *(exceeded spec: demonstrated on the real attestation_hash change and
      it additionally caught the unbumped schema version)*
- [x] Null-field fixture emits null/unknown, nothing invented (3.8).
      - Director read the packet: nulls render as "unknown".
- [x] Tier re-ask ruled at the stop and recorded (D9). - DEV-1.
- [x] Outcome section appended; obligations and limits carried forward by
      name, including: exact-hash dedup only (no clustering), and the
      Phase 0 verification limits, unchanged.
      - §7 below; the dedup limit carries its D-025 correction with the
        original quoted.

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
silently absorbed.

## 7. Outcome (assembled 2026-08-24 at commit `fa3eb53`; awaiting the director's phase-close ritual)

Shipped: D1-D10 all present. 98 tests green plus 1 deliberate skip (the
Windows key-permissions gap, which IS the recorded limit), `ruff check` and
`ruff format --check` both clean, full suite green with ANTHROPIC_API_KEY
deliberately set and scrubbed by the suite itself. Schema at 0.3.0 (two
bumps, both recorded against charter §7: 0.2.0 added attestation_hash per
R-1; 0.3.0 made discovered_at nullable per D-024 with a migration note).
Added beyond contract, named as added: `pipeline.py` (deterministic wiring
of §5.3, kept out of cli.py for testability), `gate.py`, the CLI `fb` entry
point, and `core/schema.py` as the single validating entry.

### Exit checklist, evidenced
- [x] pytest green with key vars scrubbed: enforced in-suite (conftest
      autouse + guard test), demonstrated red-first (assert
      ['ANTHROPIC_API_KEY'] == [] failed pre-fix); the director's run below
      sets a fake key on purpose.
- [x] ruff check AND ruff format --check, two named commands, both clean.
- [x] Happy path: CLI smoke observed this session: ingest 3, keyed
      previews, confirm under real git identity, "chain verifies clean",
      packet with zero sentinel content.
- [x] Positive control: explicit unseal recovers the sentinel and writes
      attempt+outcome rows (test_explicit_unseal_recovers_sentinel_and_logs).
- [x] Negative: tampered ledger fails verify (attestation-tampered;
      content-tampered and chain-broken each have their own control).
- [x] Negative: emit of unconfirmed refuses (`unconfirmed`).
- [x] Negative: unseal without the explicit flag refuses
      (`unseal-not-explicit`), exposure log unchanged; with it, the
      append-only two-row exposure record (D-022).
- [x] Negative: drift test demonstrated on a REAL schema change
      (attestation_hash): failure output captured; it also caught the
      unbumped schema version, exceeding what 3.7 asked (noted per the
      director's round-2 close).
- [x] Null-field handling: garak adapter emits null for version/timestamp;
      fixture and tests prove nothing is invented.
- [x] Tier re-ask ruled and recorded (DEV-1: D6/D8 STANDARD, D7 FULL,
      discharged by R-1 quoted).
- [x] Outcome appended; obligations and limits carried below.

### Phase close, verified (director's ritual, 2026-08-24)

The director ran every row personally, plus controls of their own (including
a positive control the builder had not listed: searching the fixture itself
to prove the sentinel-absence search could detect). All happy-path and
refusal rows confirmed. The three rows previously marked prediction are now
OBSERVATIONS: hand-edited confirmed_by in ledger.jsonl gave exit 1
attestation-tampered; deleted head.json gave exit 1 head-missing; a
hand-built three-record ledger with the last row dropped gave exit 1
head-mismatch ("chain has count=2 ... head commits to count=3"), and an
accidentally duplicated record was ALSO caught by the head, so it detects
insertion as well as truncation. Two blocking findings came out of the
ritual (A and B below), fixed red-then-green and re-run before close.

Re-run of the two touched rows after the fixes (builder-observed, this
session, awaiting the director's own re-run): ingest-garak on the unchanged
fixture printed {"ingested": 3, "total_candidates": 3, "duplicates_marked": 1}
with `duplicate-of` shown on the second of the identical pair and record 3
unique; a BOM-prefixed ledger with forged confirmed_by (Notepad simulation)
gave exit 1 `attestation-tampered: ...`, a governed refusal, not a crash.

GATE suite wall-clock at this close (per D-027, reported every close):
**1.3 seconds** builder-observed, **1.32 seconds** in the director's own
close run, for 105 passed + 1 skipped.

**Director's close verification (2026-08-24, their run, their words the
authority):** Finding A verified by reading the stored dedup fields
directly, not the list output (pair shares cluster cl-6e5ebc43d3311315,
duplicate_of set on the second, record 3 null/null). Finding B verified as
the REAL case: the ledger's first three bytes read EF BB BF before
verifying; result attestation-tampered, exit 1, no traceback. Checks that
exceeded specification, noted per the director: (1) a genuinely malformed
line refused with "store-unreadable: ledger.jsonl line 2 is not valid
JSON: Expecting property name enclosed in double quotes" - file, line
number AND parse error, more than D-026 specified; (2) the drift test's
version-pin catch (noted at 3.7 above); (3) the chain head caught an
accidentally duplicated record - insertion detection nothing had claimed.

### Defects found by running it, not by inspection
1. The R-8 negative control tested nothing (fixture already carried an id);
   pytest caught it AFTER commit `a9251d4` landed red because the gate run
   and commit were chained in one command. Both recorded in the eval.
2. The sentinel control fired on the packet: garak `goal`/`triggers` carried
   harmful-capable text into candidates in the clear. Fixed by sealing them
   as a context blob (`context_sealed_ref`). No prior test or review row had
   named this class.
3. **Finding A (director's ritual):** dedup detected nothing in its own
   fixture; byte-identical evidence differed only in attempt bookkeeping
   riding inside the dedup key. Ruled a defect wearing a limit's clothes;
   fixed per D-025.
4. **Finding B (director's ritual):** a Notepad-edited (BOM) ledger crashed
   with a raw traceback instead of refusing; the only failure mode in the
   phase without a reason code, hit by following the ritual literally.
   Fixed per D-026.

**Practice finding (director's, recorded as ruled):** that is the third and
fourth time this phase that execution beat inspection, after the R-8 control
that tested nothing and the goal/triggers leak. A suite proves what it was
told to look for, and the ritual is where the things nobody thought to
assert show up.

### Obligations carried, by name
OB-1 (FLARE-AI canonical schema, v1.x), OB-2 (MultiFernet rotation,
v1-completion), OB-3 (JCS adopt-or-reaffirm before SARIF ships; no silent
discharge), OB-4 (external trust anchor; due at first trust-boundary
crossing; scoped OUT of v1 and named as such).

### Honest limits (carried forward unchanged unless marked new)
- Phase 0 verification limits, unchanged (charter §10).
- Exact-hash dedup only: identical evidence dedups within and across
  ingests (dedup key excludes reproduction.environment per D-025);
  near-duplicate clustering (similar but not identical evidence) remains
  out of v1 scope.
  **Correction (2026-08-24, direction: toward the less flattering answer
  for the builder).** This limit originally read: "Exact-hash dedup only;
  for garak that means re-ingestion dedup, since every hit carries a
  unique attempt_id (new, this phase)." The director's ritual showed that
  wording described a defect, not a limit: single-ingest dedup on
  byte-identical evidence, the case Pain-4 exists to serve, did not work
  on the only shipped adapter. Fixed per D-025; original kept here quoted.
- Preview is structural metadata, not semantic grey-scale.
- The chain head is unsigned: detects accident, drift and casual edit, not
  an attacker with write access to ledger AND head (OB-4 bound; the packet
  states this wherever it states the guarantee).
- Fernet tokens embed their creation time in plaintext: "the encrypted
  message contains the current time when it was generated in plaintext, the
  time a message was created will therefore be visible to a possible
  attacker" (official cryptography docs, quoted per the R-6 close).
- Windows ACL gap: chmod 0o600 does not restrict access on Windows; the
  operator step is icacls (docstring); the test skips there rather than
  asserting a guarantee chmod does not deliver.
- id is a 64-bit truncation: bounds display identity, not dedup correctness
  (schema description carries the full statement; duplicate_of links by id).
- Schema file resolved relative to the repo tree: holds for the editable
  install; wheel packaging would need schemas as package data (new).
- DEV-2: canonical JSON is not RFC 8785; two named divergences, discharge
  via OB-3.
- **Finding ids are store-local, not content-identity** (director's control
  at close, C-004): sealed refs are HMAC-keyed under the store's key (R-3)
  and sit inside the hashed content, so the same hitlog ingested into two
  stores yields different ids for identical findings. Consequences: no
  cross-store correlation by id (two analysts' stores, or two stores
  emitting into one tracker, will not match); and key rotation as scoped in
  OB-2 would change every ref, hash, id, attestation and the head - OB-2 is
  therefore BLOCKED on OB-6 (identity stability under rotation) and no
  rotation path is built before OB-6 resolves.

