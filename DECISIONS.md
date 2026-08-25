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

**Rationale addendum (director's note, 2026-08-24; changes nothing about
the policy, records where it came from so the reasoning is not lost):**

The problem being solved: our negative controls plant one defect, by hand,
once, at build time. That proves a check can fail for that single mutation
at that single moment. It does not prove the check catches a different
mutation, and nothing re-runs the planting, so it decays silently from the
day it is written. Humans plant once because a human chooses each defect by
hand and stops at one. The policy wants many defects, of many types,
generated and re-run automatically: one scripted probe is not a red team.

The four quadrants the three cadences were built around:

1. **Known knowns** - behaviour we specified. Unit tests + hand-planted
   negative controls. Already in place. GATE cadence.
2. **Unknown knowns** - code paths no test asserts anything about. The
   quadrant we had nothing for, and the one the complaint was really
   about. Mutation testing: one mutation at a time, run the suite, record
   whether it was caught; a surviving mutant is a line nothing cares
   about. AUDIT cadence.
3. **Known unknowns** - the invariant is known, the breaking input is not.
   Property-based testing: generated inputs across the described range,
   including edges the author did not think of, shrunk to smallest
   failure. GATE cadence, because it is cheap.
4. **Unknown unknowns** - the question itself is unknown. Coverage-guided
   fuzzing on untrusted input reaches part of it (TRIGGER cadence, OB-5);
   the rest is adversarial review by someone who did not build the thing
   (permanent practice, never automated away).

Candidate tools to evaluate, not adopted until their official sources are
read (3.12): mutmut (mutmut.readthedocs.io) or cosmic-ray for mutation
testing; Hypothesis (hypothesis.readthedocs.io) for properties; Atheris
(github.com/google/atheris) for fuzzing when OB-5 triggers. Unmaintained or
Windows/Python-unsuitable tools are reported plainly with an alternative.

Two limits recorded with the policy so nobody reads more into it than is
there: (1) mutation testing produces equivalent mutants, semantically
identical changes that can never be killed, so the score has a permanent
ceiling below 100 percent - we ratchet it, never chase perfection, and a
padded score is worse than an honest one; (2) the fourth quadrant does not
close - this phase's suite was green at 105 tests while outside review and
the director's ritual found what it missed, including the store-local id
finding no test would ever have asked about. That is the empirical case
for human adversarial review as a requirement, not a fallback.

The ceiling matters as much as the coverage: every check is code that must
be maintained, and checks rot like everything else. That is why the D-027
budgets are binding numbers, not aspirations.

Director's acknowledgement, recorded with the addendum: the builder's
distinction at close (the ritual's hand tamper surfaced attestation-tampered
and head-mismatch, while the literal chain-broken mode stayed test-covered
only) was correct and correctly handled - "the difference between a check
being covered and a check being demonstrated." Nothing reopened for it.

**Tool evaluation results (3.12 fetches, all 2026-08-24):**
- mutmut: UNSUITABLE here, reported plainly - official docs state "Mutmut
  must be run on a system with fork support... on windows, you must run
  inside WSL" (mutmut.readthedocs.io); the only WSL distro on this machine
  is docker-desktop, not a general Linux environment.
- cosmic-ray: ADOPTED for AUDIT - version 8.7.0, released 2026-08-09 (PyPI,
  actively maintained), installs and runs on this Windows / Python 3.14
  machine (cosmic-ray.readthedocs.io).
- Hypothesis: ADOPTED for GATE properties - version 6.165.10, "known to
  work and regularly tested on macOS, Windows, Linux", supports all live
  CPython versions (hypothesis.readthedocs.io/en/latest/compatibility.html).
- Atheris: not evaluated now; due when OB-5 triggers.

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

## D-029 — Audit rulings: scoped ratchet, collection guard, run-2 stands (director, 2026-08-24)

1. **The ratchet is scoped, and the scope is part of the number.** The
   baseline is recorded as "87.2 percent, 287 of 329 mutants, over
   provenance and sealing only", never as "the core". **Binding:** any
   future audit that widens or narrows scope restates BOTH the old and new
   denominators side by side; a moved figure with one number visible is how
   a ratchet quietly becomes a ceiling.
2. **Close the class, not the instance:** the audit must assert its
   collected test count equals the gate suite's collected count and refuse
   on difference. Built as tests/test_audit_guard.py (runs in GATE, so the
   mismatch is caught before any audit runs with stale commands).
3. **Run 2 stays in the record as written:** a gate run without its
   ammunition, caught by reading the numbers rather than by any check, is
   the strongest argument in this project's history for reading numbers by
   hand even when everything is green.

## D-030 — STEP-02 is SARIF-out (director, 2026-08-24)

**Decision:** option (a). Two reasons recorded, the director's second
judged the stronger:
1. (Builder's) SARIF is the flagship second output (D-002) and OB-3 comes
   due against it; putting it first forces that reckoning at phase start.
2. (Director's, blast radius) SARIF is the change most likely to force the
   canonical schema to grow, and schema changes are cheapest when the
   fewest adapters depend on the schema (today: one in, one out). Building
   transcript-in first would double the re-mapping surface of a later
   SARIF-driven schema change. And markdown is a forgiving consumer that
   has proven almost nothing about schema sufficiency; SARIF is the first
   STRICT consumer, with a published schema and a real validator - the
   actual test of the project's central claim, better failed now than
   after more is built on the schema.

**Contract conditions ruled in advance:** the location problem is a
numbered decision, not a first-draft accident; validation runs two
independent routes (own schema check + Microsoft SARIF Multitool) against
a named real consumer; OB-3 resolves at PHASE START (adopting RFC 8785
changes canonical bytes, hence hashes, hence ids - doing it after mapping
work means redoing it); and OB-2/OB-3/OB-6 are one problem wearing three
hats (identity derived from things that can change), so OB-3's decision is
taken with the family in view and the contract carries one written
survival-and-migration paragraph for a store created today.

## D-031 — Commit counts: source of the systematic error named; command-only rule (director, 2026-08-24)

**The error, measured (git rev-list --count):** at 950742b actual 35,
reported 39 (+4); at 925c387 actual 33, reported 36 (+3); at a8977e2 and
72a9cbb reported figures were correct. **Source, named:** every count up to
a8977e2 came from a command; after it the builder switched to a mental
running tally incrementing once per remembered commit-EVENT, and the
opening-act turns had more events than commits (background chains
confirmed twice, intents folded into fewer commits). The three phantom
increments cannot be reconstructed exactly, which is the indictment of
tallies: they keep no receipts. This is the count-treadmill class in our
own record (D-027 addendum). **Standing rule:** commit counts are reported
only from `git rev-list --count HEAD`, command shown, never from a tally.
Correction C-005 in the table.

## D-032 — Gate budget: collection guard moves to AUDIT cadence; delta reporting (director, 2026-08-24)

**Decision:** the audit collection guard (tests_audit/test_audit_guard.py,
moved from tests/) runs at AUDIT cadence: `python -m pytest tests_audit`
is the first step of every mutation audit, before any cosmic-ray run. It
cost ~7s of every commit to protect an artifact that runs once per phase;
a check belongs at the cadence of the thing it guards (D-027 applied
consistently). Director's trend measurements: 1.3s -> 9.9s -> 17.7s; after
the move: 6.83s (126 passed, 1 skipped; `python -m pytest -q`). **From
this phase on, gate wall clock is reported as a delta from the previous
close as well as an absolute.**

## D-033 — STEP-02 Q1-Q4 rulings with amendments (director, 2026-08-24)

Q1 (a): physical location pointing at the emitted findings artifact, plus
logicalLocations. Binding addition: an explicit disambiguation property
inside the SARIF stating the physical location refers to the FINDING
RECORD, not a defective artifact (SARIF convention reads locations as
"where the defect is"; ours means "where the record is"). Named risk, not
a later discovery: GitHub Code Scanning associates alerts with repository
files, so this choice assumes the emitted artifact lives in the scanned
repository; acceptable given sealing, tested under OB-7.
Q2: approved; required addition: the Multitool must be fed a deliberately
invalid SARIF and its rejection captured (a validator only ever seen
saying yes is not yet a validator); resolved Multitool version recorded.
Q3 (a): adopt RFC 8785 now, five binding conditions: exact version pinned
WITH hash; the RFC's own test vectors committed as permanent suite;
goldens re-pinned in the SAME commit as adoption; behaviour verified over
our value space (nulls, nested objects, float severity.score, non-ASCII
environment text; the library raises on non-string keys and nothing may
rely on old leniency); and the recorded dependency is THE STANDARD, not
the library - RFC 8785 is frozen and reimplementable if the package
vanished. Migration note per charter §7. DEV-2 discharged by adoption.
Q4: the split stands as drafted, no amendment; the FULL/STANDARD line is
testable, which is why it is a good line.
Readings: R1 Y, R2 Y, R3 Y (GitHub ingestion becomes OB-7), R4 Y amended:
the npx Multitool invocation pins an explicit version, recorded, because
npx resolves floating versions and unpinned validation is not reproducible.
Practice note for the STEP-02 outcome, director's words: the guard bug
caught by running the guard before committing it is the fourth instance of
the gate-half-run family and the FIRST caught before it reached the
record; a defect class that starts getting caught earlier is the only real
evidence a practice is working.

## D-034 — Standing delegation for STEP-02 D1-D6 (director, 2026-08-24)

The director granted bounded autonomy through the phase: Section B items
decided alone with normal decision rows; Section C bright lines stop
everything regardless (sealed-content exposure, identity-path changes
beyond Section A, store compatibility breaks beyond the ruled adoption,
runtime dependencies beyond rfc8785, safety-test weakening, discovered
wrong premises, scope growth, anything remote, real harmful content,
hedge-worthy claims); Section D grey zone proceeds with the least
irreversible option recorded as PROV-n PENDING RATIFICATION, capped at
five open; two stops (after D3, and phase close); Section F quality bar
unchanged; Section G stall protocol. Nothing on the
questions-I-would-have-asked list closes by silence.

## D-035 — STEP-02 D3 result: no canonical schema growth required (builder, under D-034 Section B, 2026-08-24)

**Decision:** the SARIF mapping as ruled needs no new canonical schema
field. Checked element by element: the Q1(a) location design (emitted
findings artifact + region), the DEV-4 disambiguation property,
logicalLocations (target model, probe name), taxa (taxonomy.owasp_llm /
taxonomy.saif via run.taxonomies), and every result-level property draw
either from existing canonical fields (all 30 already have SARIF rows in
schemas/field_map.json since STEP-01) or from emission-time context (the
artifact path, tool name/version, the disambiguation text), which belongs
to the adapter, not the schema. **Alternative rejected:** adding a
"record_location" field to the canonical schema - rejected because the
location of the emitted record is a property of emission, unknowable at
finding creation and different per emission target; storing it would bake
one output's concern into the evidence model. If D4 implementation
falsifies this, that work is FULL under the ratified tier line and comes
back at the re-ask forecast's named condition.

## D-036 — The unguarded-boundary class, named; error messages are an emission surface (director, stop one, 2026-08-24)

**The class, named so it can be checked at every new boundary instead of
counted as coincidences:** UNGUARDED BOUNDARY - untrusted input reaches an
internal component and the component's own exception escapes as a raw
traceback instead of a governed refusal with a reason code. Instances to
date: (1) STEP-01 Finding B, BOM/corrupt store files crashing json.loads
(fix: store-unreadable); (2) the corrupt head.json variant of the same;
(3) S2-1, hostile hitlog values (NaN, Infinity, 2^53+1) crashing
rfc8785 in the hash path - CONFIRMED REACHABLE by the director through
the CLI, traceback quoted in the S2-1 evidence. The check at every new
boundary: what exceptions can the component below raise, and does each
surface as a reason code?

**Standing rule (error messages are an emission surface):** when a refusal
originates from untrusted source content, the detail names the LOCATION
(file, line, field path) and the reason, NEVER the value. The charter's
"sealed content never appears in any emitted artifact" includes error
output; today's refusals were safe by luck, and the S2-1 fix is exactly
where instinct would echo an offending value that sits beside harmful
model output. Control required: a malformed hitlog with a sentinel harm
string beside the invalid field; the sentinel must appear nowhere in the
refusal output, with the positive control finding it in the file itself.

**Audit of the existing 24 reason codes against the rule (builder,
2026-08-24):** one echoer found - `schema-invalid` used
jsonschema.ValidationError.message, which EMBEDS the offending instance
value (e.g. a rejected string is quoted verbatim); if a harmful string
failed schema validation its content would echo. Fixed: detail now built
from json_path + validator name, never the instance. All others clean:
invalid-hitlog and store-unreadable use JSONDecodeError.msg (generic text,
no content) plus line numbers; provenance details carry hashes and
indices; sealing details carry paths and refs (keyed digests);
unknown-id/malformed-ref echo OPERATOR-supplied arguments, which the rule
does not cover (they are not source content) - noted, not fixed.

## D-037 — Standing rule: when the builder may reset its own commits (director, 2026-08-24)

Reset without asking ONLY when all four hold: local and unpushed; nothing
references them; no ratified record is lost; the reset is reported in the
same report. Any one fails: stop and ask. Anything pushed: never in scope.
S2-2's cleanup is ratified under this rule.

## D-038 — S2-1 fix ruled: both layers, all of it FULL (director, stop one, 2026-08-24)

(b) primary: the ingest boundary refuses non-JCS-representable numbers
(NaN, Infinity, integers beyond 2^53-1) with `invalid-hitlog` and a
location-not-value detail. (a) backstop: canonical_content_bytes (and the
dedup key via the shared helper) translate rfc8785 domain errors to
ProvenanceError `uncanonicalizable`, so no future adapter can reach the
hash path unguarded. The whole fix is FULL under the ratified line,
adapter half included: it sits in the identity path, and over-ceremony
there beats discovering under-ceremony. Controls: the three values, red
before green, at both layers, plus the no-echo control (D-036).

## C-006 (correction, director's own, at their instruction)

| # | Original | Correction | What proved it | Direction |
|---|---|---|---|---|
| C-006 | The Q3(a) ruling adopted RFC 8785 with five conditions covering pinning, vectors, goldens, value space and standard-over-library - none of which foresaw the failure mode of unrepresentable values. | Before JCS, json.dumps serialized NaN as the non-standard token `NaN` and the hash silently succeeded (a silent wrong answer). Adoption turned that into a crash on untrusted input (S2-1). The direction of the change was right - silently hashing an unrepresentable value was worse - but the cost was the ruling's to foresee and was not. Adoption unimpeached; the regression was introduced by the ruling. | The director's own hostile hitlog through the CLI: FloatDomainError traceback, exit 1, no reason code. | Toward the less flattering answer for the ruling. |

## D-039 — D4-D6 build decisions under Section B (builder, 2026-08-24, alternatives named)

1. **Severity banding to SARIF level:** null -> "none", 0-3 "note", 4-6
   "warning", 7-10 "error"; rank = score x 10. Alternative rejected:
   mapping null to "warning" as a cautious default (invents a judgement
   the human gate has not made).
2. **ruleId = the finding's first harm flag**, declared in driver.rules;
   omitted when no flags exist. Alternative rejected: a synthetic generic
   rule id for flagless findings (an invented classification).
3. **Findings artifact is JSON Lines** (one canonical finding per line),
   so SARIF region.startLine = finding index + 1 points at a line that
   genuinely contains that finding. Alternative rejected: pretty-printed
   JSON array (line ranges become format-dependent and fragile).
4. **logicalLocation.kind = "aiModel"** (open enum; none of the spec's
   suggested kinds fits an AI model). Alternative rejected: overloading
   "module".
5. **Multitool route at AUDIT cadence** (tests_audit/), own-schema route
   in GATE - D-032's principle; npx startup and network per run.
   Alternative rejected: per-commit Multitool (budget theatre).
6. **Multitool negative control asserts on console error text** (`error
   JSON0001`), not exit code: measured 2026-08-24, the npm Multitool 5.6.0
   exits 0 even on input it itself reports as a JSON syntax error, and
   silently accepts version-less SARIF. Recorded as a measured ecosystem
   limit in evidence/sarif-validation-step02.md. Alternative rejected:
   trusting the exit code (vacuous control - it never fails).

## D-040 — STEP-02 close: three reconciliations answered; SARIF2005 ruling (2026-08-24)

1. **Suite timing spread (director 6.0s vs builder 11.58s wall, both
   honest medians-of-three):** machine-state spread now exceeds the
   number. Ruled: from the next close, report the pytest-reported time
   BESIDE the wall clock, track both.
2. **tests_audit 9 vs predicted 7, reconciled by collection
   (`pytest tests_audit --collect-only -q`):** the two extra are NOT the
   close-audit kill tests (those live in tests/, inside GATE). They are
   the collection guard's parametrized rows for cr-dedup.toml and
   cr-schema.toml: the guard grows one row per audit config
   automatically, and the "7" was an observed run predating those
   configs. Settled: 1 existence + 5 config rows + 1 negative control +
   2 Multitool = 9. A stale observation reported as a prediction is the
   lesson; the growth itself was the guard working.
3. **Warning SARIF2005** (tool provides no informationUri), which the
   builder's "no error lines" phrasing did not surface. Ruled: do NOT
   fabricate an informationUri - no public URL exists and inventing one
   to silence a linter is fabrication in a provenance tool. Absent it
   stays; stated limit; discharged with OB-7 (when a public repository
   exists, its URL becomes the informationUri in the same change).
   Builder hardening under Section B: the Multitool positive control now
   asserts the warning set is EXACTLY {SARIF2005}, so any new warning
   surfaces loudly instead of hiding under a passing test (rule 14: the
   stated limit became a check).

## D-041 — STEP-03 ratification rulings (director, 2026-08-24)

Q1 (c) both formats, sniffed, each strict; DEV-10's embedded-marker
disambiguation (column-0 exact token only), stated unrepresentable limit,
and the mandatory turn-count-unchanged control. Q2 (a); (c) named future
extension (DEV-11). Q3 as drafted with the D-024 cross-reference: null
over invented is settled law (DEV-12). Q4 (a) 10 MiB both adapters,
enforced while reading, stdin control asserting the reason code (memory
instrumentation judged disproportionate, stated), cap a stated limit with
the configurable-later sentence (DEV-13). Readings R1-R4 all Y; R3's
mojibake reason goes in the docstring. Tier FULL whole phase, inverted
re-ask default (remain FULL; the drop carries quoted-line burden);
builder forecast recorded for scoring: the default holds. D2 must prove
it can fail - discharged by the REAL missing-file red observed at
ratification (raw FileNotFoundError traceback through the CLI on a
nonexistent ingest path: unguarded-boundary instance live in the tree).

## D-042 — Pitch wording: never claim the semantic summary until it ships (director, 2026-08-24)

**Standing rule for all user-facing wording, recorded before any marketing
exists (never-overclaim applied to our own pitch):** v1's preview is
structural metadata only (length, lines, keyed digest, harm flags), so the
v1 wording is **"sealed, with a safe metadata preview"** - never "a safe
greyed-out summary". A meaning-level summary cannot be produced
deterministically without exposing content or invoking AI, which charter
rule 1 forbids in that path (already in structural_preview's docstring).
The grey-scale SEMANTIC summary is a future feature whose natural home is
the caged `--ai` flag (prose suggestion only, human-confirmed at the gate,
charter rule 2), carrying Amendment A7's research caveat alongside (the
grey-scale evidence is image-moderation research, not a red-teaming
trial). Wherever user-facing wording lands (README, packet headers, site),
this row is the wording authority until the feature ships.

## D-043 — Stop-one closes: sequencing rule, the lesson keeper, the case-mismatch ruling (director, 2026-08-24)

1. **S3-1 ratified; the class named:** early-D6 was exactly what the PROV
   register exists for - a grey-zone call, least-irreversible, recordable
   with options and reversal cost - and it happened silently and was
   confessed after. The confession is why it cost nothing this time.
   **Standing rule: a sequencing deviation goes into PROV at the moment of
   temptation, not into the findings table at the stop.**
2. **S3-3's lesson is a keeper**, recorded in docs/LESSONS.md: read a
   traceback's PATH before reading its stack.
3. **Case-mismatch (director's adversarial shot at stop one):** a
   line-initial case-variant of a marker token ("User:", "user:") was
   silently swallowed as content of the preceding turn - a quiet
   misattribution that can change which turn seals as the probe; worse
   than the loud phantom-split limit. **Ruled (a): refuse.** A
   case-variant marker at column 0 is far more likely a real turn
   boundary than real content; refusing loudly beats guessing either way.
   Reason code invalid-transcript, detail names
   suspected-marker-case-mismatch and the location, never the value.
   Controls both directions: fires on "User:" at column 0; does NOT fire
   on mid-line case variants, which are unambiguous content. Recorded on
   the contract as DEV-14. Escape accounting: this is a FULL director
   escape for the phase - the builder pointed the reviewer at the marker
   rule and still missed the case axis.

## D-044 — S3-CLOSE-1: the class covered on the exit side (director's ritual, ruled FULL, 2026-08-24)

**Finding (ritual, blocking under STEP-01 precedent):** emit-markdown to a
missing parent directory died with a raw FileNotFoundError while
emit-sarif created the directory and succeeded - the two emitters
disagreed about the same condition and the loser crashed ungoverned.
Fifth instance of the exception-escapes-as-traceback class, first on an
OUTPUT path; the boundary table had swept input dependencies only.
**Ruling executed:** both emitters agree via one shared governed writer
(adapters/writing.py) - parents created (an output path the user named is
intent, not accident), genuinely unwritable destinations refuse
`output-unwritable` (reason code 30), location-not-value. Three controls
captured red on the pre-fix CLI (markdown missing-parent, both
unwritable cases) with emit-sarif's create-parent green as the agreement
control; the boundary table gained its output-dependency section, closing
the class on the exit side as D2 closed it on entry.

## D-045 — The permanent skip: deleted as dead, and what deleting it exposed (director's item, 2026-08-25)

**Decision:** the "SYSTEM : x" parametrize row that permanently skipped was
DEAD - a non-case-variant planted in a case-variant test, then skipped
around instead of removed; deleted. Its substance now lives as an explicit
pinned-behaviour test: a line-initial space-variant ("SYSTEM :") parses as
content of the previous turn. **How the skip came to exist, said plainly:**
the builder noticed mid-edit that the fourth variant did not belong, and
skipped it in place rather than deciding - a decision made silently in the
same phase as its covering control, exactly what the director's item
suspected. **What deleting it exposed:** the WHITESPACE axis of the marker
rule is unswept - "USER :" at column 0 is plausibly a typo'd turn boundary
and currently swallows silently, the same quiet-misattribution shape
DEV-14 refused on the case axis. Named to the STEP-04 stop-one agenda for
ruling (a refusal-surface change, not pre-ruled, so not fixed under
Section B). The suite's skip count now means exactly one thing: the
named Windows key-permissions platform gap.

## D-046 — Banned-phrase list for user docs (builder under Section B, D-042's law made checkable)

The never-overclaim check (tests/test_no_overclaim.py) bans these claims
from README.md and docs/USAGE.md. Each is something the tool does not
ship. Alternative rejected: a review habit instead of a test (habits do
not fail builds; skill rule 14).

| Banned | Why |
|---|---|
| "grey/gray-scale summary", "safe greyed-out summary" | the semantic summary is not shipped (D-042) |
| "summarizes the content" | the preview is metadata, not a summary |
| "AI-powered" | no AI runs in this pipeline |
| "tamper-proof" | the chain is tamper-EVIDENT, and bounded (OB-4) |
| "unbreakable", "bulletproof", "military-grade" | unearned security claims |
| "guarantees safety/security" | no such guarantee is made |
| "fully automated", "no human review needed" | the gate is mandatory |
| "publishes to PyPI/GitHub" | no publishing exists |
| "cross-store correlation" | ids are store-local (D-028) |
| "detects all/every ..." | no completeness claim |

Required statements, checked in the same test: D-042's exact wording
"safe metadata preview"; the OB-4 bound sentence in BOTH docs; the no-AI
statement. Found while writing it: my own README was missing the bound
sentence and the ruled wording, and a line-wrapped sentence made the
check fail, so required-phrase matching normalizes whitespace (wrapping
is formatting, not meaning).

## D-047 — Wheel-first for the fresh-venv proof (builder under Section B)

`pip install . -c constraints.txt` fails in hash-checking mode: pip
cannot verify hashes for a local directory. Decision: build a wheel and
install that. Alternative rejected: dropping the constraints file for the
proof (it would test a different dependency set than the one ruled in
DEV-6). The wheel route is also the better proof: it tests the artifact a
user would receive. Observed: 203 passed, 1 skipped, imported from
site-packages. Build artifacts are gitignored (caught by reading the
commit's own file list).

## D-048 — License: Apache-2.0, ratified for the tree (director, STEP-04 stop one)

**Decision:** Apache-2.0. LICENSE file and pyproject metadata added in
one commit; NOTICE file added, since attribution suits a project whose
personality is provenance. **Reasons:** an explicit patent grant, which
matters for organizational security teams; it matches our one runtime
dependency (rfc8785 is Apache-2.0), so the wheel's license story is
uniform; the NOTICE mechanism fits. **Alternative rejected:** MIT -
simpler, but no patent language. **Scope, recorded as ruled:** this is
ratified FOR THE TREE and is reversible until the day the repo is first
pushed anywhere public; the act of publishing under it is a separate
future decision that re-confirms it. Verified in the built wheel:
`License-Expression: Apache-2.0`, `License-File: LICENSE`. PROV-2 closed.

## D-049 — The marker-variant family, swept and ruled once (director, STEP-04 stop one)

**Family principle:** refuse when the string is more plausibly a marker
than content, because a quiet misattribution that changes which turn
seals as the probe is the worst available failure. One table so the next
variant is a lookup, not a fresh ruling:

| Variant | Example | Ruling |
|---|---|---|
| exact token | `USER:` | parse (the grammar) |
| case | `User:` / `user:` | REFUSE (DEV-14) |
| space before colon | `USER :` | REFUSE (this ruling) |
| tab before colon | `USER\t:` | REFUSE |
| full-width colon | `USER：` | REFUSE |
| indented marker | `  USER:` | REFUSE |
| BOM before first marker | `﻿USER:` | TOLERATE and strip: an encoding artifact, never ambiguous, and the file reader already strips it |
| any of the above MID-LINE | `he said User: go` | content, never fires |

Swept by running each variant before deciding: space, tab, full-width
colon and indentation ALL silently swallowed into the previous turn
(3 turns where 4 were meant); BOM refused with a confusing message. One
reason code, `invalid-transcript`, with a detail naming the shape and the
line, never the value. Controls both directions for every row. D-045's
pinned test is superseded by the refusal test and says so - the pin did
its job by making the behaviour visible until it was decided.

## D-050 — The README install command was broken (director's docs read, W1 defect)

**Finding:** the README told users to run `pip install -e . -c
constraints.txt`. Run in a fresh venv it FAILS: "The editable requirement
... cannot be installed when requiring hashes, because there is no single
file to hash." D-047 had predicted the shape and the builder still shipped
it in the doc - the first command a new user runs, failing, predicted by
our own record. **Fix, observed not composed:** `pip install -e .` works
(verified in a fresh venv; still gets the pinned rfc8785 0.1.4, because
the pin lives in pyproject and the constraints file only adds hash
verification). Docs now show the plain editable install plus the wheel
route for hash verification, and say why. **Check added:**
tests/test_no_overclaim.py now fails if a known-broken command reappears
in the docs, and asserts both docs explain the wheel route.

## D-051 — Identity lifecycle: Option D, the supersession event, adopted (director, STEP-04 close)

**Decision:** the supersession event is the identity-lifecycle mechanism.
Every identity-changing event becomes a human-confirmed ledger record,
chained like any finding, committing to: event type, old head, new head,
the old-id-to-new-id map, the reason, the confirming human, and an
attestation over all of it. Verification walks THROUGH it: history before
verifies under the old rules, after under the new, and the join itself is
attested. **Deciding reason (the paper's own):** rotation and
canonical-form change become instances of ONE mechanism, so the third
instance of the class arrives with a home instead of a fresh invention.
**Alternatives rejected:** A (accept it) leaves OB-2 permanently blocked
and a key compromise fatal; C (content-derived identity) reopens the R-3
oracle, see D-056; E alone does not address lifecycle. **Adopted now;
nothing built.**

## D-052 — OB-2 unblocked as a decision, with binding conditions (director, STEP-04 close)

**Decision:** OB-2 (key rotation) is unblocked and moves into its own
future phase contract. **Binding conditions:** (1) rotation is implemented
AS a supersession event, never as a standalone path; (2) the phase's
controls include the three the paper names - a rotation that verifies
clean across the join, a forged supersession record that fails, and a
supersession claiming a remap it did not perform, failing. **Trigger, not
a date:** before the first production store exists, or on the director's
explicit call, whichever comes first. **Tier: FULL, with no re-ask
inversion**, because the paper's own honest limit stands and the phase
contract must quote it: *"The multi-epoch verification complexity in D is
the part most likely to be underestimated here."*

## D-053 — Option B adopted inside D: split the ref key from the encryption key (director, STEP-04 close)

**Decision:** sealed refs derive from a ref key separate from the
encryption key, so rotation re-encrypts blobs under a new encryption key
while refs, hashes and ids stay fixed. Adopted as part of D because it
shrinks the first supersession event's remap, possibly to zero, making it
cheaper to build and to verify. **Binding:** the ref key's permanence is a
STATED LIMIT recorded wherever the split is recorded - the frozen thing
moved, and we say so plainly rather than claiming it vanished.
**Alternative rejected:** one key for both, which is today's design and
the reason rotation breaks every id.

## D-054 — Option E parked as OB-6's named answer, gated on real demand (director, STEP-04 close)

**Decision:** the shared-key correlation digest (HMAC over the plaintext
digest under a correlation key exchanged out of band) is PARKED, not ruled
out. It is the register's named answer to OB-6. **Gate, per the charter's
own demand law:** built when a real user asks to correlate across stores,
and not before. Nobody proposes it fresh; nobody builds it speculatively.
**Alternative rejected:** building it now (inventing demand, which the
charter's evidence rules forbid).

## D-055 — The canonical form gets its own version number (director, STEP-04 close)

**Decision:** canonical form **v1 = RFC 8785**, as adopted at OB-3's
discharge. Carried as a constant, written into the chain head so every
store declares which form its hashes speak, and every future supersession
event states old and new form versions. **This closes the fourth hat:**
the canonical form and the schema can change independently, and until now
only the schema had a version axis. The axis now exists, cheaply, before
anything moves along it. **Alternative rejected:** overloading the schema
version (they change independently; one number cannot describe two axes).

## D-056 — Option C closed, with a stated reopening bar (director, STEP-04 close)

**Decision:** content-derived identity (unkeyed plaintext digest inside
the hashed content) is CLOSED. The R-3 oracle fix is settled law, and C
reopens it in exactly the currency this project refuses to spend.
**Reopening bar, adopted from the paper's own standard:** only a written
concrete attack analysis demonstrating the mitigation safe, brought as its
own numbered question, reopens it. Absent that, C is not proposed again.

## D-057 — Process claims must name their check or say "unchecked" (director, STEP-04 close)

**Standing rule, ruled by naming rather than solving:** any future
"I did X for all Y" claim in a report must either name the check that
enforces it, or carry the word **unchecked** beside it. Costs one word and
ends the class. **Origin:** the builder wrote "every command was run
before it was written down" and the install block was the one command it
had not run (D-050). A claim about one's own process failed exactly where
no tool checked it.

## D-058 — Private remote created as BACKUP, not publication (director, 2026-08-25)

**Decision:** a private GitHub repository was created and `master` pushed:
`github.com/MohdSaifHussain/finding-bridge`, visibility PRIVATE, default
branch master, 64 commits, remote head `3ad6576` identical to local HEAD.
No tags: tagging a release is a separate future decision.

**This is a backup decision, not a publication decision.** 64 commits of
closed, verified work existed on one machine with no copy; a disk failure
would have erased the code and the entire decision record. Publishing
under the Apache-2.0 license (D-048) remains a separate, future, explicit
ruling. D-048's own scope sentence stands: the license is ratified for the
tree, and the act of publishing under it re-confirms it.

**NOT discharged by this push, stated explicitly so nobody assumes
otherwise:** OB-7 (GitHub Code Scanning ingestion) and the SARIF2005
`informationUri` gap (D-040.3) both stay OPEN. A private repository URL is
not an `informationUri` the ecosystem can read, so nothing about a private
remote satisfies either obligation. They discharge when a PUBLIC URL
exists, which is the separate future decision above.

**History pushed as-is; no rewrite. Ruled, not merely answered:**
(1) a provenance project does not sanitize its own provenance;
(2) a rewrite would break every commit SHA cited in DECISIONS.md and the
evidence files, which are the project's load-bearing citations; and
(3) the briefly-tracked build artifacts (commits 56-57, incl. a 38,358-byte
wheel blob) plus their catch and fix are part of the honest record.
**Alternative rejected:** `filter-repo` to drop the artifacts - cosmetic
gain, paid for with a broken citation graph and an altered chain of work.

**Pre-push audit, run and reported before anything touched the network:**
109 files ever committed, all source/tests/schemas/docs/evidence/config;
no `.key`/`.pem`/`.fernet` file ever committed and no `fb.key`,
exposure log, `.fb-store`, ledger or candidates file in history; 533
history objects scanned for GitHub, AWS, OpenAI, Slack, PEM and Fernet
token shapes with zero hits; all 64 commits authored AND committed as the
noreply address; no `C:\Users\...` path in committed content.

## D-059 — The ratchet: per-module baselines, new surface seats its own (director, STEP-05 stop one)

**Ruling, applying D-029's own logic exactly as dedup and schema were
handled at their first measurement:** a NEW surface seats its own first
baseline; EXISTING baselines never drop. The composed figure is reported
alongside, never instead.

**Measured at stop one** (method: `git diff --unified=0` between the
pre-W1 commit `5d0ef0c` and HEAD gives the lines W1 added or changed;
every mutant is attributed to the pre-W1 or W1-new surface by its line):

| Scope | STEP-04 | STEP-05 W1 | Verdict |
|---|---|---|---|
| provenance, pre-W1 lines | 161/195 = 82.6% | 161/195 = 82.6% | HELD, identical |
| sealing, pre-W1 lines | 125/130 = 96.2% | 115/119 = 96.6% | HELD, up |
| schema, pre-W1 lines | 1/10 = 10% | 1/10 = 10% | HELD, identical |
| dedup (untouched) | 49/63 = 77.8% | 49/63 = 77.8% | HELD |
| **pre-W1 surface, composed** | | **277/324 = 85.5%** | |
| **W1-new surface, FIRST BASELINE** | | **146/195 = 74.9%** | seated |
| **full core, composed** | 360/419 = 85.9% | **472/582 = 81.1%** | composition effect |

**No pre-existing module dropped**, so no pre-W2 kill work is owed under
the ruling's second branch. The 81.1% headline is composition, confirmed
by measurement rather than asserted.

**Two binding conditions:** (1) the W1-new baseline (74.9%) must move UP
at the arc close, not down; (2) the growing proportion of
reasoned-not-verified equivalence claims is a NAMED LIMIT in the register
with its number beside it: **95 of 110 surviving mutants are dispositioned
as equivalent by the builder's reasoning, not machine-verified.**

## D-060 — The comparison-weakening class, closed in CODE (director, STEP-05 stop one)

**Diagnosis, the builder's own sentence adopted as the ruling's reason:**
the fix lived in tests, not in a habit, so fresh code re-created the gap.
Third occurrence.

**Ruling:** one shared verification-comparison helper in core, through
which every hash and head equality check in verify paths flows, with the
both-orderings property tested ONCE against the helper, plus a mechanical
check that no verify path compares digests inline. Code using the helper
cannot recreate the class; code bypassing it is findable by machine. Same
move the boundary table was for tracebacks: close the class, not the
instance.

## D-061 — Ordered-checks tests must prove they reached their check (director, STEP-05 stop one)

**Standing rule, from stop one's finding 2:** a test of an ordered
sequence of checks must assert the failing check's OWN detail string, not
merely the shared reason code, so a test that dies at an earlier check
fails loudly instead of passing hollow. Applied to the W1 controls now and
to everything after.

## D-062 — The D-057 self-application is the gate-half-run family's FOURTH instance (director, STEP-05 stop one)

The mechanism, recorded because it is the point: the edit script's anchor
assert FAILED, and the commit message claiming both docs were updated was
written anyway. A check fired and the claim ignored it. That is D-057
meeting the gate-half-run family, and it is the family's fourth instance.

## D-063 — Tracker JSON shape (builder under Section B, alternatives named)

**Decision:** a FLAT JSON ARRAY of issue objects with four common
top-level fields (summary, description, labels, priority) plus a `fields`
object for everything tool-specific. Field names are the intersection of
Jira, Linear and GitHub Issues, so an importer for any of them is a
rename, not a re-parse.

**Alternatives rejected:** (a) Jira's native issue JSON with its
`fields.customfield_NNNNN` shape - vendor lock, and the custom-field ids
differ per installation so it would not even import cleanly twice; (b) a
nested per-tracker structure with one branch per vendor - three shapes to
keep correct with no user asking for any of them yet.

**Two judgements inside the shape, recorded because they are choices:**
(1) an unscored finding gets priority "Unset", never a guessed band -
inventing a priority puts a judgement in a ticket that no human made;
(2) taxonomy labels carry a "?" suffix when the mapping is `suggested`,
so an unconfirmed mapping cannot masquerade as a confirmed one inside a
tracker's flat label space. **Supersession records are skipped**: ledger
bookkeeping is not an actionable ticket.

## D-064 — OB-2 DISCHARGED (director, STEP-05 close, explicit word)

**Discharged.** Key rotation is implemented, and implemented only as a
supersession event, per D-052's binding conditions.

**Evidence, as an EVIDENCE PAIR - the two-route standard this project uses
for absence claims, now ruled to apply to discharge claims too:**

*Route 1, the builder's tests* - the three D-052 controls, each captured
red before its implementation existed:
1. a rotation verifies clean across the join;
2. a forged supersession record fails (attestation-tampered);
3. a supersession claiming a remap it did not perform fails
   (supersession-invalid, detail naming the remap).

*Route 2, the director's hands* - two independent double-rotation runs on
live stores: fresh store, confirm, two rotations, verify clean after each
join, remap=0 both times, ids byte-identical before and after, explicit
unseal returning the sentinel after double re-encryption, ledger reading
finding / supersession / supersession as one unbroken chain.

Neither route alone would discharge it. Together they do.

## D-065 — The register is now FULLY EXTERNAL (director, STEP-05 close)

Register accepted as restated: OB-5, OB-7, OB-6-via-E, the semantic
preview, the D-018 adapter pack. Nothing else.

**With OB-2 discharged, every remaining item waits on an external
trigger** - a public repository, real user demand, or third-party data at
volume. **For the first time, nothing in the register waits on us.**

## D-066 — Ratchet reporting: both ways, permanently, on a FROZEN basis (director, STEP-05 close)

**Ruled:** every audit reports the raw figure AND the
annotation-adjusted figure, side by side.

**The adjustment method is FROZEN as recorded at this close**, so future
comparisons are like-for-like: a surviving mutant is excluded from the
adjusted denominator when its mutated line is a type annotation (a line
whose text contains `str |`, `dict |`, or `list[` in the annotation
position) or an `lru_cache` decorator - the classes PEP 649 lazy
annotations and pure-loader caching make unexecutable or behaviourally
inert. Any change to this method is a numbered ruling.

**Precedent set, in the director's words:** the builder's refusal to claim
the W1-new up-condition on an adjustment invented at the same close was
correct - *a measure invented at the moment of reporting cannot settle its
own claim*. **The up-condition transfers forward: it binds from the NEXT
audit, on the frozen basis.**

**Meta-finding, recorded with both instances side by side:** TWICE now the
raw metric has reported an improvement as a regression.
- *STEP-04 close, schema*: deleting risky path arithmetic removed ~21
  killable mutants, so the score fell 80.6% to 10% while the code got
  safer.
- *STEP-05 close, provenance*: annotating two new helpers added ~44
  equivalent mutants and de-inlining nine digest comparisons removed ~45
  killable ones, so the score fell 80.1% to 66.3% while non-equivalent
  survivors moved 13 to 14.

A metric that punishes the behaviours we want is a metric that needs its
denominator explained every time it is read - which is exactly what
both-ways reporting does.

## D-067 — The tree guard is a permanent tool, and also a concurrency lock (director, STEP-05 close)

**Ruled permanent.** It caught a real race on its first firing.

**Lesson in its docstring, as ruled:** the stale `TREE-OK` echo was a
single witness restating a cached check; `git status` was the
re-derivation that beat it.

**Binding condition:** the guard refuses a second audit start while a
first holds the tree, with its own reason code - not merely a dirty-start
refusal. If two instrument processes racing one tree is possible once, it
is possible twice.

## D-068 — The rule census is the next act, before any feature work (director, STEP-05 close)

**Ruled YES.** Walk every standing rule in DECISIONS.md and the
skill-derived practices and classify each as **CHECK** (a tool or test
fires when it is violated), **HABIT** (a human or the builder must
remember it), or **SENTENCE** (recorded, enforced by nothing). For every
HABIT and SENTENCE, state what a check would cost and whether it is worth
building - *some rules are correctly sentences, and saying so is a valid
disposition*.

**Evidence for urgency, from the builder's own eval:** D-062 was broken
within minutes of being ruled, by the mechanism it describes; the
comparison class was recreated by fresh code. Rules failed to prevent
their own class twice in one arc, while six of nine defects were caught by
machinery.

**Deliverable:** a table, plus a short list of proposed new checks with
costs, for the director's ruling. STANDARD tier, no code beyond trivial
check additions, one stop at the end.

**The framing, recorded because it is the point:** this is the project
maturing from rules-as-prose to rules-as-instruments.

## D-069 — Workspace-setup tracebacks fixed now, by the director's explicit word (STEP-06 W1, 2026-08-25)

**Finding (builder, capturing the five-minute tour):** an empty `$TMPDIR`
sent `--store` into `C:\Program Files\Git` and the CLI died with a raw
`PermissionError` from `Workspace.__init__`'s `mkdir`. Probing the same
shape found a second: a `--key` path whose parent is a file dies with a
raw `FileExistsError` from `_write_keyring`. Sixth and seventh instances
of the exception-escapes-as-traceback class (D-036), both on the
workspace-setup side, which the boundary table had not swept (inputs at
D-036, outputs at D-044, workspace never).

**Ruling (director, mid-turn, verbatim: "PLEASE MAKE SURE TO FIX IT"):**
fixed in this arc, as the contract's 3.1 exception by explicit ruling,
recorded on the contract as DEV-20. Two reason codes, distinct because
the operator's remedy differs: `store-unwritable` (pick a writable
`--store`) and `key-unwritable` (pick a writable `--key`). Detail names
the path and the exception class, never content (there is none at this
boundary). Three controls captured red before the fix (two refusals as
raw tracebacks, one positive control already green) and green after.
Full gate re-run after the scripted edit (whole gate, not the half).

**Alternative rejected:** a single `workspace-unwritable` code (the two
remedies differ, and the 2am reason-code table is the reason codes
exist). **Limit stated:** the mutation baselines for provenance and
sealing are unchanged by ruling until the next audit; sealing gained
nine lines here that are unmeasured until then.

## D-070 — F-2 fixed FULL: one shared filter in the ledger read path (director, STEP-06 stop one, 2026-08-25)

**Ruled:** `Workspace.confirmed_findings()` drops supersession records
once, so all four emitters inherit it; `emit-tracker`'s own skip stays
as a second layer, now the explicit shared behaviour rather than a lucky
accident. Controls captured red for markdown, sarif and flare
(KeyError tracebacks) against a rotated store, plus the shared-filter
test, before the fix; tests/test_emit_after_rotation.py.

**Two records, in the director's words:** (a) this is an ESCAPE against
the STEP-05 close, direction named: the close ritual rotated and
verified but never emitted after rotating, so every emitter was
certified against a store shape the rotation feature immediately
invalidates; the director's ritual missed it too, a joint escape.
(b) The finder was examples/03-rotation-drill: a documentation exercise
found a product defect the suite and two rituals missed, the
proof-artifacts addendum earning its place in one stroke. **Standing:
close rituals gain an emit-after-rotation row, all four formats.**

## D-071 — Schema 0.5.0 ratified under W4's narrow path: ATLAS, id patterns, remediation (director, STEP-06 stop one)

F-3: add `taxonomy.atlas`, pattern-pinned to ATLAS 5.6.0's id grammar
(`AML.T####`, sub-techniques `AML.T####.###`), null/empty legal,
mapping rows in the same commit. F-4: pattern pins on
`taxonomy.owasp_llm` (the fetched 2025 id form) and `taxonomy.saif`
(the fetched saif-data vocabulary), version pinned in the pattern's
description; empty and null stay legal everywhere: constrain the shape
of what IS claimed, never require a claim. Q-1: add `remediation`,
optional, null default, written only by the human at the gate like the
severity rationale; the `--ai` path gains NO remediation capability in
this arc (a suggested remediation is parked as a named future `--ai`
job beside the semantic preview); STANDARDS.md's row cites the Guide.
One minor bump, one migration note.

## D-072 — PROV-3 ratified: normalised showcase comparison (director, STEP-06 stop one)

Byte-match modulo a committed, named normalisation list, each entry
justified in the check's docstring; anything differing outside the list
fails. Byte identity requiring key material in the tree would violate
D-010 to satisfy a showcase. The list is part of the check's honesty: it
names exactly what the showcase does not prove.

## D-073 — Quoted standards may carry a banned phrase under three conditions (director, STEP-06 stop one)

(a) verbatim in quotation marks, (b) attributed to its source by name,
(c) immediately followed by our narrower claim. The check learns the
exemption under those three conditions so it stays mechanical; bare
unquoted use stays banned everywhere forever.

## D-074 — The gate gains a verdict file; never pipe the gate (director, STEP-06 stop one)

C-009 is C-008's mechanism biting the gate itself: gate.py piped to
tail masked gate.py's own exit code, the mask-killer masked. Ruled:
`tools/gate.py --verdict-file <path>` writes one line (`GATE: PASS` or
`GATE: FAIL ...` plus the exit code); the standing rule becomes NEVER
PIPE THE GATE: read the verdict file if you need the tail. The rule
converts from a sentence broken twice into a mechanism that makes
piping unnecessary.

## D-075 — DEV-20 accepted as applied; C-009 accepted as recorded (director, STEP-06 stop one)

The redone-from-scratch honesty of the resume report (naming what died
with the old session rather than patching around it) noted as done
right.

## D-076 — F-5: the OWASP pin was stale; re-pinned to the 2026 edition, standing rule for pins (director, STEP-06 stop-one addendum, 2026-08-25)

**Finding, the director's, found by asking a question outside the
record ("why 2025 and not 2026"):** the OWASP GenAI LLM Top 10 2026
edition was published 2026-08-03, three weeks before the builder's
fetch; STANDARDS.md pinned 2025 as current, which it was not on the day
it was written. **Second confirmed specimen of the outside-the-record
route working** (the first found the CI blank); the census's
fourth-quadrant note gains the tally.

**Rulings:** (1) re-fetched from the official OWASP source with a
browser UA: page and PDF (download 56857, 122 pages) both 200; the pin
rests on OWASP alone. (2) STANDARDS.md re-pins to 2026 with the delta
from 2025 stated in one paragraph; the 2025 row kept beside it, marked
superseded with its date, original kept and direction named. (3) The
F-4 pattern pins are built against the 2026 grammar from the start:
F-5 landed before the 0.5.0 commit existed, so it cost a re-fetch, not
a rework. (4) Finder and route recorded honestly. (5) **Standing rule:**
every pinned edition row carries its publication date AND the date we
last checked for a successor; the W7 release checklist gains a row to
re-check every pin within days of the flip.

**Verification limit, stated:** the 2026 PDF's own title page reads
"[Publication date to be set]"; the August 3, 2026 date comes from the
resource page. Both facts are recorded; neither is smoothed over.

## D-077 — C-010 and PROV-4 ratified; the wrong-object measurement class named (director, STEP-06 pre-push word, 2026-08-25)

C-010 ratified as recorded. F-6 survived one director read, one
D-049-class check, and a fresh-venv proof because **the STEP-04 proof
tested a similar command, not the documented command: the wrong-object
measurement class wearing an install script's clothes.** The first tamper
control proving nothing (one hash of two zeroed) and saying so is the
control-that-proves-it-can-fail discipline applied to the control itself.
The four listed rephrasings are within DEV-19 as written.

PROV-4 ratified: the widened lock is the correct cost of
--require-hashes; it converts the install from trust-the-index to
verify-every-byte. **Two conditions:** (1) the lock is maintained by the
W5b machinery: whether Dependabot's pip ecosystem reads a file named
constraints.txt could not be confirmed from the fetched docs (the
supported-ecosystems page is script-rendered), so tools/lock.py (with
--check as the drift detector and a selftest) is the maintenance path
until the first Dependabot run shows which manifests it found, recorded
as a verification limit; (2) README, USAGE and SOP state in one line
that the lock is the secure route and `pip install -e .` the developer
route.

Docker-daemon limit accepted as stated. Instruction: on CI's first build
the digest is read BACK from the pulled image on the runner and compared
to the Dockerfile's pin, recorded in evidence with the run URL; the local
rehearsal (daemon now running) is the first half of the pair.

## D-078 — STOP TWO closed; F-7, F-8, the layer-scan replacement ratified; W6c real-data validation ordered before W7 (director, 2026-08-25)

**Verified by the director:** remote at 2d97085, 101 commits, tree clean;
the STOP TWO run pair and the newest pair all success from the director's
own `gh run list`. The Ubuntu-executes-the-skip deliverable, the digest
read-back pair, the layer scan with positive control, and the private GHCR
package accepted on the evidence plus the green runs.

**Open item, for comparison:** the director's own `docker login ghcr.io`
from the reviewing session was refused on the v2 ping with a token
carrying write:packages. The builder's successful rehearsal used the OAuth
token from `gh auth login` (scopes as listed by `gh api -i user`, including
write:packages and delete:packages), piped as
`gh auth token | docker login ghcr.io -u MohdSaifHussain --password-stdin`
on this machine with Docker Desktop 29.7.2. If the CMD ritual fails the
same way, that is F-9 for investigation.

**Ratified:** F-7 (the 3.12 lock gap; the Python matrix earning its place
before it ran on CI); F-8 (no git, no human gate; the read-only gitconfig
mount is the right shape); the layer-scan replacement including its own
SCAN BLIND arc and the sealing.py false positive fixed against a planted
real keyring; the wrong-token audit row kept beside its correction.

**W6c ordered, before W7 (contract DEV-21):** real-data validation. Every
store so far came from synthetic fixtures; v1.0 does not launch on that.
Sources: (1) a REAL garak run against llama3.2:1b on the local Ollama
0.32.15, dan and promptinject families, time-boxed; (2) one published
2026-relevant adversarial dataset through the transcript path. D-012
absolute: the raw dataset and the real hitlog never enter the tree; a
committed script with source URL and checksum fetches them (the FLARE-PDF
pattern); example 04 commits only the transcript, sealed previews, dedup,
verify output and emitted artifacts, plus one stronger control: a scan of
the committed artifacts against real strings sampled at run time from the
local copy, never committed. **Findings law:** any crash, mis-parse,
silent field loss, or wrong refusal against real data is a FINDING for
ruling before W7; unmapped garak fields are the finding most expected.

## OB-5 FIRES (director, 2026-08-25)

The recorded trigger, "the first time we parse data at volume that the
project did not generate", is met by W6c by definition. A time-boxed
fuzzing pass (30 minutes, budget stated) runs against the two ingest
parsers with Atheris; if Atheris is unusable on Windows with this Python
(checked before promising), an honest structured alternative: a
randomised malformed-input generator over the boundary table's refusal
families, seeded from real-data shapes, every crash a finding. If nothing
runs, OB-5 is not quietly re-parked: a numbered ruling names the attempts.

## Open work after the STEP-04 close (the record, so no one needs memory)

Nothing here is proposed; each waits on the director's word.

| Item | State |
|---|---|
| `--ai` caged feature (taxonomy suggestions, severity rationale) | roadmap, unstarted |
| Tracker-JSON out-adapter | roadmap, unstarted |
| OB-2 supersession phase | UNBLOCKED (D-052), awaiting trigger |
| OB-5 coverage-guided fuzzing | trigger unfired |
| OB-7 GitHub ingestion | waits on a remote, which is the director's decision alone |
| OB-6 cross-store correlation | Option E parked (D-054), gated on real user demand |
| Semantic preview (grey-scale summary) | future `--ai` job; never claimed until it ships (D-042) |
| Suggested remediation | future `--ai` job, parked by D-071 beside the semantic preview; the human-written `remediation` field exists since schema 0.5.0 |

## PROV register (Section D provisional decisions, PENDING RATIFICATION)

| # | Decision taken | Options | Why least irreversible | Cost to reverse | Status |
|---|---|---|---|---|---|
| ~~PROV-2~~ **CLOSED: ratified as Apache-2.0 (D-048)** | pyproject ships WITHOUT a license field or license classifier | (a) omit, all-rights-reserved by legal default, director picks at stop one; (b) builder picks a permissive license | (a): adding a license later is one line; un-granting a wrongly-granted one is practically impossible. A rights decision belongs to the owner. | one pyproject edit once ruled | OPEN, pending ratification at STEP-04 stop one |
| PROV-3 | The W3 showcased-equals-current control compares committed example artifacts to a fresh re-run AFTER normalising the fields that derive from the store key, the clock and the operator (ids, cluster ids, sealed refs, keyed digests, 64-hex hashes, timestamps, identity, path separators), instead of the byte-match the director's word asked for | (a) normalised comparison, volatile list short and visible in examples/run_example.py, docstring states exactly what a pass proves; (b) commit a fixed example key and inject a clock so bytes match; (c) no control | (a): byte identity is impossible without key material in the tree, which key-inside-repo and the D-058 secret scan both exist to refuse, and the tool has no clock injection (a product change, Section C). (a) is reversible by editing one list. | one file if ruled the other way | **RATIFIED (a)** by the director at STEP-06 stop one (D-072) |
| PROV-4 | constraints.txt widened from the single rfc8785 pin to a full runtime lock (11 packages, PyPI hashes, all platforms), and the documented verified route becomes `--require-hashes -r constraints.txt` then `--no-deps <wheel>` | (a) full lock, pip's own secure-installs route; (b) keep the single pin and drop the hash-verified route from the docs; (c) keep the docs as they were | (a): additive, reversible by trimming the file; (b) narrows a promise the docs had made for two phases; (c) leaves a broken command in the first thing a user reads (D-050's class) | trim one file, reword two paragraphs | **RATIFIED (a)** by the director before the push (D-077), two conditions; condition 1 VERIFIED by observation on the first Dependabot run (its pip job checks names that exist only in constraints.txt; evidence/ci-first-run-step06.md) |
| PROV-1 | schema_version stays 0.3.0 at JCS adoption | (a) no bump: no schema FIELD changed, canonical serialization is provenance machinery not schema shape; (b) minor/major bump to signal the hash-behaviour change | (a) chosen: bumping is a one-line change that can be applied later without migration (no stores exist); un-bumping after consumers saw 0.4.0 could not be undone | one Edit + fixture updates if ratified the other way | **RATIFIED (a)** by the director at stop one; note added to OB-6 and §4d via DEV-9: canonical form and schema can change independently and only one has a version - the identity problem's fourth hat |

## Obligations register (carried by name until discharged)

| ID | Obligation | Owner | Trigger / due |
|---|---|---|---|
| OB-1 | Resolve provisional FLARE-AI mapping against a canonical schema | v1.x FLARE-AI out-adapter phase | when FLARE-AI publishes one; phase cannot close silent (D-014) |
| ~~OB-2~~ | ~~Key rotation path~~ **DISCHARGED 2026-08-25 (D-064)**: implemented as a supersession event per D-052, evidenced by the three controls (red-then-green) AND the director's two independent double-rotation runs. | closed | closed |
| ~~OB-3~~ | ~~Adopt RFC 8785 (JCS) with fetched sources, or re-affirm deviation DEV-2 with reasons~~ **DISCHARGED 2026-08-24 by adoption** (STEP-02 D1, ruling Q3(a), five DEV-6 conditions met; DEV-2 discharged with it; migration note docs/decisions/canonical-jcs-migration.md; measured impact on existing data: none, forms byte-identical on the current value space) | was: v1-completion phase | explicit entry, as the condition demanded |
| OB-4 | External trust anchor for the chain head (signed head, or anchor held outside the store) | unowned until triggered | comes due the first time a finding store or its head crosses a trust boundary (shared, synced, or handed to anyone who did not create it); out of v1 scope, named as scoped-out |
| OB-5 | Coverage-guided fuzzing of parsers (D-027). **FIRED 2026-08-25 (D-078): W6c parses real data.** Owner: STEP-06 W6c; 30-minute time-boxed pass, Atheris or the structured alternative, reported with what it does not prove. | STEP-06 W6c | fired |
| OB-6 | Resolve finding-identity stability under key rotation (D-028). Candidate direction to EVALUATE, not decided: separate the ref-derivation key from the encryption key so encryption rotates under MultiFernet while ref identity stays pinned. Options with trade-offs proposed when due. | must resolve before OB-2 | opened at STEP-01 close; **OB-2 is blocked on OB-6**; STEP-02 must not quietly start either |
| OB-7 | GitHub Code Scanning ingestion test (D-033/Q1): real ingestion of our SARIF, including the named assumption that the emitted findings artifact lives in the scanned repository and alerts render against it. **Explicitly NOT discharged by the private remote (D-058):** a private URL is not readable by the ecosystem. | due when a PUBLIC repository exists (publishing is a separate future ruling) | opened at STEP-02 ratification; trigger narrowed at D-058 |

## STEP-01 readings, confirmed

R1 (Y): raw sealed content never appears in any emitted artifact, encrypted
inline included. R2 (Y): mapping table + drift test in the same commit as the
first schema file. R3 (Y): zero AI anywhere in this phase. R4 (Y): STEP-NN
numbering starts here; no back-written STEP-00.

## Corrections

| # | Original claim (quoted) | Correction | What proved it | Direction |
|---|---|---|---|---|
| C-007 | Director's mid-verification belief at STEP-05 stop one: that a finding id had CHANGED across rotation. | It had not. The measurement compared the first row of `list` before and after, and the confirmed finding leaving the candidates listing shifted the row - a single witness measuring the wrong object. Re-derived from the store itself and killed. No product change. Recorded under the director's name at their instruction. | The director's own re-derivation from the ledger rather than the listing. | False alarm raised AND killed by the same reviewer; a live specimen of why rituals re-derive instead of restate. |
| C-010 | README at D-050: "To verify dependency hashes as well, build and install a wheel. This is the route we test:" followed by `pip install dist/...whl -c constraints.txt`. | The route was never tested. The STEP-04 proof installed the wheel without `-c`; the command fails in a fresh venv (pip requires hashes for all requirements once any has one). Corrected to pip's secure-installs route with a full lock, rehearsed with a negative control (F-6). | The W5 rehearsal of gate.yml's fresh-wheel step, run locally before the workflow was pushed. | Toward the less flattering answer for the builder: a D-057 claim ("the route we test") that named no check, for two phases. |
| C-009 | Builder's W3 commit at count 89 (message claiming the gate was green: "Controls in tests_audit/test_examples.py"), 2026-08-25. | The commit landed with `ruff-check` RED (two E501 lines in tools/fixture_scan.py). Mechanism: the edit script's anchor assert FAILED partway (the fixture_scan half never applied), the script was `;`-chained so the run continued, and the commit chain read `python tools/gate.py 2>&1 \| tail -2 && ... git commit`, which takes `tail`'s exit code, not the gate's. tools/gate.py printed `GATE: FAIL (ruff-check)` and the commit ran anyway. This is C-008's exact mechanism, the gate-half-run family's SIXTH instance, committed by the builder that had just re-read C-008 in this same session. Fix committed immediately after; no push had happened. | The builder re-reading the command output before writing the next report. | Toward the less flattering answer for the builder. The tool (gate.py, D-062's answer) did its job; the SHELL AROUND the tool masked it, which is the class gate.py's own docstring names. Recorded so the census can ask whether the mask needs a check of its own. |
| C-008 | Builder's commit message at count 72: "Record stop-one rulings D-059..D-062 and correction C-007". | C-007 was NOT recorded by that commit. The edit script's anchor assert for the corrections table FAILED, the script died, and the commit ran anyway with a message claiming the work was done. **This is D-062's exact mechanism - a check fired and the claim ignored it - repeating within minutes of D-062 being ruled, and it is the gate-half-run family's FIFTH instance.** The two rulings D-057 and D-062 were both already on the books; neither prevented it, because neither is a check that runs. The mechanical cause is specific and fixable: the heredoc script and the git command were separate statements, not `&&`-chained, so a failing script did not stop the commit. | The builder re-reading its own command output before writing the stop report. | Toward the less flattering answer for the builder; recorded rather than quietly patched. |
| C-002 | Director's R-1 wording: "src/finding_bridge/core/provenance.py:20 excludes the whole 'provenance' object from the hash [...] A field anyone can rewrite silently is not a record" — framing the exclusion as the defect. | The exclusion is load-bearing, correct design (the hash cannot contain the object that stores it; dedup is mutable triage state). The defect was the ABSENT second guard over the excluded fields; the remedy (attestation hash) is unchanged. Ruled by the director on the builder's precision note 1. | The fix keeps the exclusion and adds the attestation; test_provenance.py:45-64 asserts the exclusion+guard pair. | Toward the more precise answer; remedy unchanged. |
| C-005 | Builder's reported repo sizes: "Repo: 36 commits, clean tree, head 925c387" and "Repo: 39 commits, clean tree, head 950742b". | Actual counts by `git rev-list --count`: 33 and 35. Source of error named in D-031: a mental running tally after a8977e2, incrementing per remembered commit-event; phantom increments unreconstructable. Standing rule: command-only counts. | Director's independent `git rev-list --count HEAD` both rounds; builder's anchor-by-anchor measurement confirming drift began after a8977e2. | Upward both times, overstating activity: +3 then +4, a growing systematic overcount, not a slip. |
| C-004 | Director's R-3 ruling (round 2): key the refs "so refs stay stable within a store and the cross-corpus oracle disappears" - stated the benefit; the identity cost went unstated. | The keyed refs sit inside hashed content, so finding ids became store-local, not content-identity: identical findings in two stores carry different ids, and rotation as scoped in OB-2 would break every id and attestation. Recorded as the director's own correction, at their instruction, in the same manner as the builder's. Consequences ruled in D-028 (stated limit + OB-6 gate). | The director's two-store control at the STEP-01 close: six different ids for three identical findings. | Toward the less flattering answer for the director's ruling: the fix was right and its cost was real and unstated. |
| C-003 | Director's R-10 wording: "The 'zero API keys' guarantee is currently claimed, not demonstrated." | Narrows to: demonstrated once ad hoc, never enforced in the suite. Evidence the ad hoc demonstration is recoverable from: (1) this session's transcript (URL in every commit trailer, Claude-Session line), where the run `env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY ... python -m pytest -q` returned "14 passed"; (2) commit 5ecdce4's message, which asserted "suite passes with API-key env scrubbed" contemporaneously. The contractual requirement (scrub as an enforced suite property, shown in the director's run) was genuinely unmet until commit 712b610. | Session transcript + commit 5ecdce4 message; enforcement landed in 712b610. | Toward the more flattering answer for the builder; accepted by the director only with this citation, per the higher burden rule. |
| C-001 | "The governed-orchestration skill is **not active** in this session and is not installed/listed here" and, in the closing limits, "not yet installed" (builder's Phase 0 closing report, this session, 2026-08-24) | The skill IS installed at `~/.claude/skills/governed-orchestration` and loaded when invoked with the Skill tool on the director's instruction. What was true: it was absent from the session's listed skills. The builder widened "not listed" into "not installed" without checking the filesystem or attempting invocation: an absence stated without a check, the defect class Phase 0 audited the charter for. | Successful `Skill(governed-orchestration)` invocation, this session, on the director's check-don't-assume instruction. | Toward the less flattering answer for the builder. |
