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

## D-015 — Tier re-ask outcome: split, discharged by R-1 (director, review stop, 2026-08-24)

**Decision:** D6 (garak in) and D8 (markdown out) drop to STANDARD as pure
translation; D7 (human gate) stays FULL. The 4b discharge standard is met by
naming R-1 (gate record not tamper-evident), a finding attributed to the FULL
practice of re-deriving hash coverage rather than trusting passing tests, and
D7 writes the exact field R-1 exposed. Recorded as deviation DEV-1 in
STEP-01 §6 with R-1 quoted. Builder's advance forecast (full drop) scored:
partly wrong.

## D-016 — Review round 2 blocking fixes ruled and applied (director, 2026-08-24)

**Decision:** independent review findings R-1, R-2, R-3, R-4, R-10 ruled
blocking; fixed with negative controls captured failing before each fix and
passing after. Commits: 044c31d (R-1 attestation hash; schema 0.2.0),
b7061c5 (R-2 chain head), cd6f322 (R-3+R-4 keyed refs, ref validation),
712b610 (R-10 env scrub). Schema minor-bumped 0.1.0 to 0.2.0
per charter §7 (field added); the drift test was demonstrated firing on that
real change before the mapping row was added (contract 3.7 demonstration).

## D-017 — Core language: Python, single-language, for v1 (director-initiated, 2026-08-24)

**Decision:** the core is Python, single-language, for v1. **Reasons:** the
source ecosystem this tool adapts (garak, PyRIT) is Python, so parsers can be
checked against real source rather than inferred; the users already have
Python; the project's guarantees are proven by one test suite, one linter
pair, one packaging story. **Alternatives rejected:** a Go or Rust core
(better single-binary distribution and faster on large hitlogs, but worse for
reading adjacent tool source and for outside contribution today); a mixed
core (doubles the surface where a safety rule can hold in one language and be
forgotten in the other). **Recorded triggers for revisiting, not
preferences:** (1) the tool must ship as a single binary to users who do not
have Python; (2) hitlog volume makes Python ingestion the bottleneck.
**Binding governance condition:** introducing a second language into the core
is a charter-level amendment requiring an explicit director ruling; no
session may treat it as an implementation detail inside a phase.

## D-018 — Plugin adapter pack: parked post-v1, trust boundary fixed now (director-initiated, 2026-08-24)

**Decision:** the polyglot seam is the canonical schema, not the codebase.
An external adapter pack (adapters in any language) is a post-v1 roadmap
feature, explicitly out of scope until v1 completes. **Design constraints
recorded now so they cannot be invented later under pressure:**
(a) an adapter is an executable that reads its source input and writes
candidate findings as canonical-schema JSON on stdout, exit 0 on success,
nonzero with a reason code on refusal; (b) core validates every adapter's
output against the canonical schema before accepting a single field and
treats it as untrusted input, with size limits and no execution of anything
the pack supplies beyond the declared adapter binary; (c) no external adapter
ever seals, hashes, confirms, or writes provenance — it returns candidates;
core performs sealing, hashing, and the human gate. Charter rule 1 and
contract 3.11 hold across the boundary; that is why the boundary is data,
not a library API. Nothing is built for this in v1. Charter roadmap carries
it with these constraints attached (amendment A12).

## D-019 — Build defaults ratified as decisions, each with its rejected alternative (ruled 2026-08-24)

1. **Hash exclusions** (`id`, `provenance`, `dedup` excluded from content
   hash). Alternative rejected: hashing all fields with provenance nulled
   (breaks the attestation design and makes the hash depend on triage
   state). The exclusion is safe only paired with the R-1 attestation guard;
   the test asserts the pair.
2. **Dedup key excludes `discovered_at`.** Alternative rejected: including
   the timestamp (every re-discovery of identical content would be unique,
   defeating the Pain-4 purpose).
3. **Structural preview only in v1.** Alternative rejected: semantic
   grey-scale summarization (requires either exposing content or AI in the
   evidence path, forbidden by charter rule 1).

## D-020 — Format assertion enabled everywhere (#6, ruled 2026-08-24)

**Decision:** every validator the project uses runs with
`Draft202012Validator.FORMAT_CHECKER` and the `rfc3339-validator` dependency,
so `date-time` asserts instead of annotating. **Source:** JSON Schema
Validation 2020-12 §7 ("MUST be disabled by default", §7.2.1
format-annotation vocabulary) and python-jsonschema validate docs ("The
date-time format requires the rfc3339-validator package... Without it,
validation succeeds silently"), both fetched 2026-08-24. A provenance
timestamp nothing checks is a silence-shaped failure; negative control: a
malformed timestamp must fail validation.

## D-021 — R-8 fix ruled; the finding is the sentence (ruled 2026-08-24)

**Decision:** `mark_duplicates` refuses unstamped input (reason code
`unstamped-finding`) with a negative control. Root cause of the miss,
recorded verbatim as the finding per the director: "my tests always stamped
first, which is exactly why my suite missed it" — the suite exercised only
the path the builder imagined, so the None-id collapse was invisible.

## D-022 — Exposure log: append-only two-row protocol (#4, ruled 2026-08-24)

**Decision:** keep the pre-write (no read can happen unlogged). Every unseal
appends an attempt row with an id; after the decrypt attempt, a second row
references it with the outcome (succeeded / failed with reason code). Rows
are never mutated. Controls both ways: successful unseal = attempt+success
rows; tampered blob = attempt+failure rows and no plaintext.

## D-023 — Key file permissions (R-7, ruled 2026-08-24)

**Decision:** chmod 0o600 on key creation where the OS honors it; the
Windows operator step (icacls) documented in the docstring; the Windows ACL
gap recorded as an honest limit. The chmod call must not imply a guarantee
it does not deliver on Windows, the platform this project is developed on.

## D-024 — Schema 0.3.0: discovered_at becomes nullable (this session, for D6)

**Decision:** the garak hitlog (fetched from NVIDIA/garak main, 2026-08-24)
carries NO timestamp field, and the charter forbids inventing one, so
`discovered_at` becomes `["string","null"]`. Changing a field is a major
bump per charter §7; within pre-1.0 development this maps to the 0.x minor
position per semver's initial-development convention, so 0.2.0 -> 0.3.0,
with the required migration note at docs/decisions/schema-0.3.0-migration.md.
**Alternatives rejected:** jumping to 1.0.0 (signals a stability that does
not exist; v1 completion is defined by the roadmap, not by this field);
stamping ingest time as discovery time (fabrication of the exact class the
charter forbids); using file mtime (an approximation presented as a fact).

## D-025 — Finding A: dedup key excludes reproduction.environment (director, phase-close ritual, 2026-08-24)

**Decision:** the content hash and the dedup key answer different questions
over different field sets. The content hash asks "has this record changed"
and keeps reproduction.environment; the dedup key asks "have we seen this
finding before" and excludes it, stated as a principle so the next adapter
(PyRIT will have its own bookkeeping) inherits it rather than a list of
garak field names. The prior state was ruled **a defect wearing a limit's
clothes**: "we do not do fuzzy clustering" is a limit; failing to mark two
byte-identical findings in a single ingest is the Pain-4 feature not
working on the only shipped adapter.

**Stated trade-off (director's condition, explicit not implicit):** findings
identical in evidence but produced under different environment settings now
mark as duplicates of each other. This costs nothing because dedup marks and
never deletes: the duplicate record stays in candidates with duplicate_of
set and its own environment preserved on its own record.

**Acceptance observed (builder re-run, then awaiting director's own):**
unchanged fixture reports duplicates_marked 1; pair shares cluster_id;
second carries duplicate_of; record 3 stays unique (negative control).

## D-026 — Finding B: unreadable stores refuse, never crash (director, phase-close ritual, 2026-08-24)

**Decision:** store files read with encoding="utf-8-sig" (accepts a Notepad
BOM, harmless without one) so a BOM-touched ledger reaches the attestation
check and fails as designed; genuinely malformed content refuses with a
reason code naming the file and line. Reading applied: the ruled code
"ledger-unreadable or similar" is implemented as `store-unreadable`, since
the same reader serves candidates, rejected, ledger, and head; the detail
names the actual file. This was the only failure mode in the phase without
a reason code, on the path a Windows-first project hits most often.

**Controls:** BOM-intact ledger verifies clean (positive); BOM+tamper yields
attestation-tampered; truncated line and corrupt head refuse with
store-unreadable (negative). All four captured red before the fix.

## D-027 — Testing cadence policy (director, ruled at phase close; runs from STEP-02)

**Decision, standing policy, recorded now and not started during this close:**

- **GATE (every commit, binding budget under 60 seconds):** unit tests,
  hand-planted negative controls, and Hypothesis property tests for the
  guarantee-carrying invariants: hash determinism and order independence;
  verify_chain accepting every well-formed chain and rejecting every
  single-record mutation; the sealed-ref validator accepting only
  ^[0-9a-f]{16}$; seal-then-unseal round-tripping over unicode, empty and
  very long inputs. **Wall-clock time reported at every phase close** so
  drift is seen before it hurts (at this close: 1.3 seconds).
- **AUDIT (once per phase close, never in CI):** one mutation-testing run
  scoped to src/finding_bridge/core/ only. Report the score with its
  denominator; list every surviving mutant; kill each with a test or record
  why it is equivalent. The score is a ratchet baseline: raised later,
  never lowered without a numbered ruling. Budget: over 20 minutes, narrow
  scope to provenance + sealing. Reproducible by the director with one
  command.
- **TRIGGER:** coverage-guided fuzzing as obligation OB-5, trigger: "the
  first time we parse data at volume that the project did not generate."
  Scoped out until then, named rather than unmentioned.

**Not automated, recorded as such:** adversarial review by someone who did
not build the thing stays a required practice; the evidence is this phase,
where outside review and the director's ritual found what the suite did
not. **Stated limits:** mutation testing measures whether the suite notices
a change, not whether behaviour is correct; property-based testing tests
only invariants someone thought to state.

**Timing:** first mutation audit and the property tests are the opening act
of STEP-02, before any new code, measuring the core as shipped. Official
sources fetched and cited before adopting any tool (3.12); an unmaintained
or Windows-unsuitable tool is reported with an alternative, not forced; any
layer that cannot name a specific failure in this codebase it would have
caught is reported for dropping.

## D-028 — Store-local finding ids: stated limit now, OB-2 blocked on OB-6 (director, at STEP-01 close, 2026-08-24)

**Finding (director's own control, no ritual row called for it):** the same
fixture ingested into two stores under two keys produced six different ids
for three identical findings. Finding ids are store-local, not
content-identity. Root cause is the director's own R-3 ruling working as
designed: HMAC-keyed sealed refs sit inside the hashed content, so the
store key propagates into every content_hash and id. The R-3 fix removed a
real confirmation oracle; this is its cost, recorded as C-004.

**Decision:** (1) for v1 this is a stated limit, not a defect: recorded in
the phase outcome and in the schema's id description, wherever finding
identity is described. (2) OB-6 opened: resolve identity stability under
key rotation BEFORE any rotation path is built; OB-2 is blocked on it.
Candidate direction to evaluate when due, explicitly not decided now:
separate the ref-derivation key from the encryption key, so encryption
rotates under MultiFernet while ref identity stays pinned. Discovering
this during a rotation would be the worst possible time; STEP-02 does not
quietly start either obligation.

## Obligations register (carried by name until discharged)

| ID | Obligation | Owner | Trigger / due |
|---|---|---|---|
| OB-1 | Resolve provisional FLARE-AI mapping against a canonical schema | v1.x FLARE-AI out-adapter phase | when FLARE-AI publishes one; phase cannot close silent (D-014) |
| OB-2 | Key rotation path via MultiFernet (docs: rotate() re-encrypts under primary key, preserving the token timestamp). **BLOCKED on OB-6 since the STEP-01 close (D-028):** as scoped, rotation would re-derive the ref key and break every id, hash, attestation and the head. | v1-completion phase, after OB-6 | phase close |
| OB-3 | Adopt RFC 8785 (JCS) with fetched sources, or re-affirm deviation DEV-2 with reasons | v1-completion phase, before the SARIF adapter ships | cannot be discharged by silence; explicit entry either way (director condition) |
| OB-4 | External trust anchor for the chain head (signed head, or anchor held outside the store) | unowned until triggered | comes due the first time a finding store or its head crosses a trust boundary (shared, synced, or handed to anyone who did not create it); out of v1 scope, named as scoped-out |
| OB-5 | Coverage-guided fuzzing of parsers (D-027) | unowned until triggered | comes due the first time the project parses data at volume it did not generate; scoped out until then |
| OB-6 | Resolve finding-identity stability under key rotation (D-028). Candidate direction to EVALUATE, not decided: separate the ref-derivation key from the encryption key so encryption rotates under MultiFernet while ref identity stays pinned. Options with trade-offs proposed when due. | must resolve before OB-2 | opened at STEP-01 close; **OB-2 is blocked on OB-6**; STEP-02 must not quietly start either |

## STEP-01 readings, confirmed

R1 (Y): raw sealed content never appears in any emitted artifact, encrypted
inline included. R2 (Y): mapping table + drift test in the same commit as the
first schema file. R3 (Y): zero AI anywhere in this phase. R4 (Y): STEP-NN
numbering starts here; no back-written STEP-00.

## Corrections

| # | Original claim (quoted) | Correction | What proved it | Direction |
|---|---|---|---|---|
| C-002 | Director's R-1 wording: "src/finding_bridge/core/provenance.py:20 excludes the whole 'provenance' object from the hash [...] A field anyone can rewrite silently is not a record" — framing the exclusion as the defect. | The exclusion is load-bearing, correct design (the hash cannot contain the object that stores it; dedup is mutable triage state). The defect was the ABSENT second guard over the excluded fields; the remedy (attestation hash) is unchanged. Ruled by the director on the builder's precision note 1. | The fix keeps the exclusion and adds the attestation; test_provenance.py:45-64 asserts the exclusion+guard pair. | Toward the more precise answer; remedy unchanged. |
| C-004 | Director's R-3 ruling (round 2): key the refs "so refs stay stable within a store and the cross-corpus oracle disappears" - stated the benefit; the identity cost went unstated. | The keyed refs sit inside hashed content, so finding ids became store-local, not content-identity: identical findings in two stores carry different ids, and rotation as scoped in OB-2 would break every id and attestation. Recorded as the director's own correction, at their instruction, in the same manner as the builder's. Consequences ruled in D-028 (stated limit + OB-6 gate). | The director's two-store control at the STEP-01 close: six different ids for three identical findings. | Toward the less flattering answer for the director's ruling: the fix was right and its cost was real and unstated. |
| C-003 | Director's R-10 wording: "The 'zero API keys' guarantee is currently claimed, not demonstrated." | Narrows to: demonstrated once ad hoc, never enforced in the suite. Evidence the ad hoc demonstration is recoverable from: (1) this session's transcript (URL in every commit trailer, Claude-Session line), where the run `env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY ... python -m pytest -q` returned "14 passed"; (2) commit 5ecdce4's message, which asserted "suite passes with API-key env scrubbed" contemporaneously. The contractual requirement (scrub as an enforced suite property, shown in the director's run) was genuinely unmet until commit 712b610. | Session transcript + commit 5ecdce4 message; enforcement landed in 712b610. | Toward the more flattering answer for the builder; accepted by the director only with this citation, per the higher burden rule. |
| C-001 | "The governed-orchestration skill is **not active** in this session and is not installed/listed here" and, in the closing limits, "not yet installed" (builder's Phase 0 closing report, this session, 2026-08-24) | The skill IS installed at `~/.claude/skills/governed-orchestration` and loaded when invoked with the Skill tool on the director's instruction. What was true: it was absent from the session's listed skills. The builder widened "not listed" into "not installed" without checking the filesystem or attempting invocation: an absence stated without a check, the defect class Phase 0 audited the charter for. | Successful `Skill(governed-orchestration)` invocation, this session, on the director's check-don't-assume instruction. | Toward the less flattering answer for the builder. |
