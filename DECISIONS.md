# DECISIONS.md

Rulings by the project director. Each entry records the decision, its reasons,
the alternatives considered, and any binding conditions. Nothing here is
Claude's default; every entry required an explicit ruling. Charter changes
caused by a ruling are logged in `docs/PROJECT_CHARTER.md` §11 (Amendments)
with original wording quoted.

Phase 0 context: the charter was a draft produced by Claude chat, preserved
unmodified at commit `59c122c` before anything else touched the tree. All 17
sources in its index were fetched and verified on 2026-08-24 before these
rulings were asked for.

---

## D-001 — Ceremony tier: tiered (Q1, ruled 2026-08-24)

**Decision:** tiered ceremony, mapped to the director's method vocabulary:

- Core-rule, schema, and safety work runs **FULL**: a written contract in
  `docs/decisions/`, plan approval before writing, and a review stop.
- Adapters and plumbing run **STANDARD**: commit-and-test discipline, with
  judgment calls logged in this file as they arise.

**Binding condition:** the tier assignment is re-asked at every phase boundary
and recorded in that phase's contract. A tier chosen once is a tier nobody
examines.

**Reason:** the spine of the tool (sealing, provenance, human gate, schema) is
small and deserves full weight; taxing every adapter mapping with the same
ceremony would slow v1 without adding trust.

**Alternatives rejected:** full ceremony everywhere (too slow for pure
translation code); light ceremony (insufficient for a Trust & Safety tool's
safety spine).

## D-002 — v1 scope: the thin proof slice, and the positioning note (Q2, ruled 2026-08-24)

**Decision:** v1 proof slice is: garak in, then provenance + sealing + dedup +
human gate, then markdown packet out. One input, one output, the whole spine
exercised. Transcript-in and SARIF-out follow the slice, still pre-1.0, each
under its own phase contract.

**Positioning note (recorded as part of this decision):** the differentiator is
the spine (sealing, provenance, human gate), not garak parsing. SARIF-out is
the flagship second output, because the SARIF lane remains unserved by any AI
red-team tool while the garak-to-DefectDojo lane is now served natively (see
D-004).

**Reason:** build discipline; the smallest complete slice that proves the
thesis end to end.

**Alternatives rejected:** the charter's original v1 list as one phase (larger
surface before the thesis is proven); reordering v1 around SARIF first (kept as
positioning, not as build order).

## D-003 — Schema: internal canonical schema plus a loud-drift mapping table (Q3, ruled 2026-08-24)

**Decision:** the canonical finding schema stays internal plumbing (semver,
migration notes in `docs/decisions/`), with a maintained field-mapping table to
FLARE-AI's schema and SARIF 2.1.0 from day one.

**Binding condition:** the mapping table is a tracked file with a test that
fails when the canonical schema changes without the table changing. Drift must
be loud, not discovered at export time.

**Reason:** adopting FLARE-AI's schema as the base would couple the evidence
model to a two-month-old external schema; an internal schema with no mapping
would silently diverge from the formats the tool promises to emit.

**Alternatives rejected:** adopt/extend FLARE-AI's JSON-LD schema as the base;
internal schema with no maintained mapping.

## D-004 — Demand-signal amendment: validated and fulfilled (Q4, ruled 2026-08-24)

**Decision:** amend charter §3 to the true history: DefectDojo issue #14878
filed 2026-05-15, garak parser merged as PR #15013 on 2026-06-23, issue closed
as completed 2026-06-26. Reframe as validated-and-fulfilled demand with the
sharpened differentiation (sealing, provenance chain, human gate,
multi-destination emission are things the merged parser does not do). Drop the
v1.x contribute-the-parser roadmap item as moot.

**Binding condition:** the original wrong sentence ("filed May 2026 and still
open") stays visible, quoted, under Amendment A2, so a later reader sees what
was believed and what corrected it.

**Reason:** verification (GitHub API, 2026-08-24) showed the draft's "still
open" claim was false. The demand is stronger than claimed (built within six
weeks of being requested) but the garak-to-DefectDojo lane is now served, which
raises the differentiation burden and reshapes positioning.

**Alternatives rejected:** keep the DefectDojo lane via "extend the merged
parser upstream"; declare the DefectDojo lane closed and remove it from
positioning.

## D-005 — Verification-driven amendments, applied with originals quoted (Q5, ruled 2026-08-24)

**Decision:** apply all three as amendments with original wording quoted:

1. FLARE-AI positioning rewritten (Amendment A4): the paper contradicts the
   draft's "public web form unsuitable for confidential findings" claim
   (stateless by default, local report generation, reporter-controlled
   dissemination); complementarity now rests on function (no sealed evidence
   storage, no provenance chain, no triage queue).
2. Attribution labels corrected (Amendment A5): "ICML 2026" relabelled "arXiv
   preprint, June 2026" (venue unverifiable); "MIT" relabelled "MIT-led,
   32-organization collaboration".
3. Pain-3 attribution shifted (Amendment A6): the stress/burnout/trauma claim
   now cites the FAccT 2025 paper (where it is verified); the CHI 2026 EA is
   kept for the field-demand claim its confirmed abstract supports.

**Binding condition (additional):** the grey-scaling caveat (arXiv 2602.19124
cites image-moderation research; it is not a red-teaming trial) is a standing
honest limit in charter §6 (Amendment A7), not only a note in this session's
report.

**Reason:** the official-sources rule; claims rest on what sources actually
say, and downgraded claims are recorded as such.

**Alternative rejected:** keeping the draft wording with footnoted caveats
(silently optimistic; the director requires quoted originals and corrected
operative text).

## D-006 — FLARE-AI PDF evidence handling: gitignore plus pointer (Q6, ruled 2026-08-24)

**Decision:** `docs/FLARE AI Flaw Reporting for AI.pdf` (16,357,288 bytes,
placed by the director) is gitignored. The charter's source index carries a
pointer naming the file, its size, and the arXiv URL it corresponds to
(https://arxiv.org/pdf/2606.31567), so the evidence is re-fetchable if the
local copy is lost (Amendment A11).

**Reason:** keeps the repo lean while keeping the evidence locatable and
reproducible.

**Alternatives rejected:** committing the 16 MB binary; moving the file out of
the project.

## D-007 — Verification limits recorded in the charter (director's addition to step 4, ruled 2026-08-24)

**Decision:** the four honest limits from Phase 0 verification (CHI EA wording
unverifiable beyond the abstract; Google CART careers posting body
unverifiable; grey-scale evidence secondhand; FLARE-AI venue unproven) are
recorded in the charter as a "Verification limits" note under the source index
(Amendment A10), so they survive this session.

**Reason:** limits that live only in a session report die with the session.

## Phase 0 interpretations, ratified (2026-08-24)

Confirmed explicitly by the director (silence was not acceptance):

- I1: the pristine-draft obligation is satisfied by commit `59c122c`, made
  before any other tool ran.
- I2: "ratified-with-amendment-log" means original text stays physically
  present, quoted in a numbered Amendments section; no inline silent edits
  anywhere, ever.
- I3: the Phase 0 CLAUDE.md change is exactly one sentence, verbatim, and
  nothing else in CLAUDE.md changes.
- I4: "every load-bearing source" means all 17 entries in the charter's source
  index; practitioner blogs and the careers link are color per the charter's
  own sourcing note, but were fetched anyway.
- I5: DECISIONS.md lives at the repo root; `docs/decisions/` is the home of
  future phase contracts and schema migration notes.
- I6: ratification is dated 2026-08-24 and lands on the charter's status line.

---

## STEP-01 rulings (director, 2026-08-24)

## D-008 — STEP-01 tier: whole phase FULL, binding re-ask stands (Q1)

**Decision:** the whole phase runs FULL. The binding re-ask at the review stop
stands as written in contract §4b: default drops D6-D8 to STANDARD; continuing
FULL past the stop requires a named FULL-only finding in a numbered ruling.
The builder's advance forecast (the gate fires) is recorded as part of this
entry, so the outcome can be scored against it.

**Alternatives rejected:** split tiers within one contract; two separate
phases.

## D-009 — One review stop, after D1-D5 (Q2)

**Decision:** a single review stop after D1-D5 (schema, mapping table,
provenance, sealing, dedup), before any adapter or CLI code exists.

**Alternatives rejected:** an extra early stop before fixture freeze; a stop
after schema only.

## D-010 — Sealing mechanism: Fernet, key outside the repo, loud path check (Q3)

**Decision:** `pyca/cryptography` Fernet symmetric encryption.
**Binding conditions:** (1) the key lives in a local file outside the repo and
is never committed; (2) a check fails loudly, with its own reason code, if the
key path ever resolves inside the repo tree; (3) the official cryptography
docs are fetched and cited before a line of sealing code is written.

**Alternatives rejected:** OS keyring (platform-variant on Windows); deferring
the choice to kickoff.

## D-011 — confirmed_by identity: git config (Q4)

**Decision:** `git config user.name` + email is the identity recorded as
`confirmed_by` in provenance.

**Alternatives rejected:** OS username; per-session prompt.

## D-012 — Synthetic fixtures only, elevated to a standing safety rule (Q5)

**Decision:** fixtures are synthetic garak hitlogs with harmless sentinel
strings standing in for harmful content.
**Standing safety rule, ruled explicitly:** no real harmful model output is
ever committed to this repository, in any phase, ever. Recorded in CLAUDE.md's
Safety rules so it binds every future session, not just this fixture choice.

**Alternative rejected:** sanitized captures from real garak runs.

## D-013 — Standing convention: drafts committed, ratification separate, no in-place amendment

**Decision (adopting the builder's reported deviation as convention):** phase
contract drafts are committed as drafts before rulings (preserve-the-draft,
commit-evidence-first). Ratification lands as its own separate commit. A
ratified contract is never amended in place; it is only extended by numbered
deviation.

## D-014 — FLARE-AI mapping: provisional-from-paper ruled the best available approach

**Decision (director, this session, 2026-08-24):** no canonical
machine-readable FLARE-AI schema exists to map against. The builder checked
ai-reports.org and github.com/ai-flaw-reporting/ai-flaw-reporting; the
director searched independently and also found none: a two-route confirmed
absence, not a failed fetch. Ruled: the FLARE-AI column of the mapping table
is derived from the JSON-LD example vocabulary in arXiv 2606.31567 (the local
evidence PDF), stays marked PROVISIONAL, and is the project's approach until
a canonical schema is published.

**Obligation OB-1, narrowed:** from "locate the canonical schema" to "resolve
the provisional column against the canonical schema when FLARE-AI publishes
one". Owner: the v1.x FLARE-AI out-adapter phase, which must not close
without either discharging OB-1 or recording that no canonical schema exists
at that date.

## STEP-01 readings, confirmed

R1 (Y): raw sealed content never appears in any emitted artifact, encrypted
inline included. R2 (Y): mapping table + drift test in the same commit as the
first schema file. R3 (Y): zero AI anywhere in this phase. R4 (Y): STEP-NN
numbering starts here; no back-written STEP-00.

## Corrections

| # | Original claim (quoted) | Correction | What proved it | Direction |
|---|---|---|---|---|
| C-001 | "The governed-orchestration skill is **not active** in this session and is not installed/listed here" and, in the closing limits, "not yet installed" (builder's Phase 0 closing report, this session, 2026-08-24) | The skill IS installed at `~/.claude/skills/governed-orchestration` and loaded when invoked with the Skill tool on the director's instruction. What was true: it was absent from the session's listed skills. The builder widened "not listed" into "not installed" without checking the filesystem or attempting invocation: an absence stated without a check, the defect class Phase 0 audited the charter for. | Successful `Skill(governed-orchestration)` invocation, this session, on the director's check-don't-assume instruction. | Toward the less flattering answer for the builder. |
