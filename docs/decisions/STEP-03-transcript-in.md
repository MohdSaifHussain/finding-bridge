# STEP-03: transcript in-adapter (raw paste to canonical)

**Project:** finding-bridge | **Phase:** 3 | **Date:** 2026-08-24
**Status:** RATIFIED by the director 2026-08-24, subject to the amendments
recorded as deviations DEV-10 through DEV-13 below (never in-place edits).
Rulings: Q1 (c) amended, Q2 (a), Q3 as drafted, Q4 (a) with two
conditions; readings R1-R4 all Y (R3 amended: mojibake sentence into the
docstring); tier FULL ratified with the inverted re-ask default, builder's
forecast (default holds) recorded for scoring. D-034 Sections B-G in
force; halting only at the declared stops.

## 6. Deviations (ratification amendments; global DEV numbering continues)

**DEV-10 (Q1 addition - the embedded-marker hazard, the parser's central
claim).** In delimited text, marker strings can appear inside content, and
a jailbreak transcript is precisely where they live. Disambiguation rule
DECIDED here, not discovered by the first draft: a marker opens a new turn
ONLY as the exact uppercase token (`USER:`, `ASSISTANT:`, `SYSTEM:`) at
column 0 of a line; anywhere else on a line it is content. **Stated limit
(what the text grammar cannot represent):** a turn whose CONTENT contains
a line that itself begins at column 0 with a marker token - such a line
opens a phantom turn by construction; the exact representation for such
content is the JSON format, which represents anything. Two controls, not
optional: (1) embedded marker strings mid-line inside a turn leave the
turn count unchanged (the ruled negative control for the central claim);
(2) the line-initial collision is pinned by a test asserting the
DOCUMENTED split behaviour, so the limit is loud, not hidden.

**DEV-14 (stop-one ruling, the case-mismatch shot; D-043.3).** A
line-initial case-variant of a marker token refuses (invalid-transcript,
detail: suspected marker with case mismatch, location only), rather than
being silently swallowed into the preceding turn where it could change
which turn seals as the probe. Mid-line case variants remain unambiguous
content. Both directions controlled; the refusal control captured red
against the pre-fix parser. S3-1 ratified with the standing PROV-at-
temptation rule; forecast on the tier default scored correct.

**DEV-11 (Q2).** Option (c), analyst-marked turns via flags, is recorded
as the NAMED future extension - addable later without unmaking (a) - so
nobody invents it fresh.

**DEV-12 (Q3).** The decision row carries the D-024 cross-reference:
null-over-invented is settled law; discovered_at null is what "unknown"
honestly looks like.

**DEV-13 (Q4 conditions).** (1) The cap is enforced WHILE reading - the
shared helper consumes chunked input and stops at the limit, because
stdin cannot be sized in advance; the over-limit stdin control asserts the
refusal reason code (memory instrumentation judged disproportionate, and
that judgement is stated per the ruling). (2) The cap is a stated limit
where users meet it (CLI help and the refusal detail), with the sentence
that a configurable cap remains addable later without unmaking the fixed
default. Additional ruled requirement on D2: the boundary tool must prove
it can fail. Discharged by a REAL red rather than a planted copy: the
table's missing-file row runs red against the pre-existing code (a raw
FileNotFoundError traceback through the CLI, probed and observed at
ratification - the unguarded-boundary class live in the tree), then green
after the helper lands.
**Depends on:** STEP-01 (core spine), STEP-02 (closed; canonical form is
RFC 8785; D-036 unguarded-boundary class and location-not-value rule;
D-018 untrusted-input constraints; D-034 standing delegation).
**Standing rule:** every implementation follows the top applicable
standard; each requirement names its governing standard.

Carried in from the start, per the director's close instruction: a
transcript parser is this project's largest untrusted-input surface, so
the D-036 class check ("what can the component below raise, and does each
surface as a reason code?") is a DELIVERABLE here, not a review item;
every refusal obeys location-not-value; and D-018's untrusted-input
constraints (size limits, validate before accepting a single field) apply
even though this is an internal adapter, because the boundary is the same
boundary.

## 1. Objective

Turn a manually captured attack transcript (the analyst's raw paste) into
a canonical candidate finding through the same seal/stamp/dedup/gate
spine, with the parser provably refusing everything it does not
understand. Exit criterion, one line: the director pastes a synthetic
transcript through the CLI, confirms it at the gate, emits it in both
formats, and every hostile variant (pre-marker garbage, missing turns,
oversize, wrong encoding) refuses with its stated reason code and no
echoed content.

## 2. Deliverables

| ID | Deliverable | Governing standard(s) |
|---|---|---|
| D1 | `adapters/in_/transcript.py`: parser for the Q1-ruled format(s), pure translation, no sealing/hashing (3.11) | Charter §5.2; D-036; grammar per Q1 ruling |
| D2 | **Boundary exception table + test** - the D-036 check as a TOOL (the STEP-02 eval's question answered): every dependency call the parser makes (file read, decode, json.loads) with every exception class it can raise, each triggered by a test and asserted to surface as a reason code, never a traceback | D-036; skill rule 14 (a lesson in prose becomes a check) |
| D3 | Mapping decisions implemented per Q2/Q3 rulings: turns to probe/response, full transcript sealed as context, analyst-supplied metadata flags, nothing invented | Charter never-fabricate; D-024 precedent |
| D4 | Hostile + happy fixtures (synthetic sentinels beside every malformed element) and no-echo controls | D-012; D-036 control pattern |
| D5 | Input size cap at the boundary, shared helper applied to BOTH in-adapters (garak retrofit in the same change: same class, one helper), distinct reason code `input-too-large` | D-018 constraint (size limits on untrusted input); cap value per Q4 |
| D6 | CLI `ingest-transcript` (file path or `-` for stdin), wiring only | Charter §5.2 |
| D7 | Tier re-ask at the review stop, ruled and recorded | D-001; skill 4b |
| D8 | Outcome + builder eval + close audit (both timing numbers per D-040; audit scope per R4) | D-027, D-029, D-040 |

## 3. Requirements

- 3.1 Every parser refusal carries a distinct reason code and a
  location-not-value detail (line number, turn index, byte offset; never
  content). New codes proposed: `invalid-transcript`, `input-too-large`,
  `unsupported-encoding` - each with negative AND positive controls.
- 3.2 The whole transcript is harmful-capable content: sealed in full;
  probe and response turns sealed individually; preview structural; no
  turn text ever reaches a candidate, packet, SARIF, log, or refusal in
  the clear (charter §6; STEP-01 R1 unchanged).
- 3.3 Missing knowledge is null, never invented: no detector exists here,
  so harm_flags start empty, severity null, taxonomy empty; target model
  and discovery time only from explicit analyst flags (Q3).
- 3.4 D2's table is exhaustive over the parser's actual dependency calls;
  a dependency call absent from the table is a review-stop finding.
- 3.5 All standing rules hold: no AI, no keys, format assertion, gate
  guard, D-036, D-012, official sources fetched (3.12) - the only
  anticipated fetch is Python codecs/json docs for D2's exception
  enumeration; no new runtime dependency (Section C line 4).
- 3.6 GATE under 60s; wall clock AND pytest-reported time at close
  (D-040).

## 4. Out of scope

- promptfoo, PyRIT, any out-adapter work, any OB item (OB-2/OB-6
  especially: nothing here touches identity derivation).
- Configurable role-marker grammars beyond the Q1-ruled markers (roadmap
  if ever asked for).
- Anything remote; the external adapter pack (D-018 stays parked - R1).

## 4a. Review stop

- Halt after D1-D5 (parser, boundary table, mapping, fixtures, caps),
  before D6 and D8. The parser IS the phase's risk; it is reviewed with
  its boundary table before any wiring builds on it. Template 4
  self-review with quoted lines; PROV and questions lists; escape
  accounting.

## 4b. Tier, with a binding re-ask

- Proposed: **FULL for the whole phase.** Justification for proposing
  nothing below FULL, per the director's stated prior: parsing untrusted
  input is where this project's defect classes live (D-036's three
  instances; STEP-01 Finding B; S2-1), and even D6's CLI wiring touches
  refusal surfaces. A split was considered and rejected: the STANDARD
  candidate (CLI wiring) is a dozen lines whose ceremony savings cannot
  pay for the risk of under-ceremonying a refusal path.
- Re-ask at the stop (D7). **Default: REMAIN FULL** for the back half -
  the inverse of STEP-02's default, deliberately. **Discharge standard
  for dropping, ruled now:** dropping D6/D8 to STANDARD requires showing,
  with quoted lines, that the remaining work introduces no new boundary
  and touches no refusal surface. **Forecast:** the default holds.
- Always-on: skill rules 4, 5, 7, 8; the three charter rules; D-036.

## 4c. Readings

- R1: transcript-in is an internal in_-adapter, NOT the D-018 external
  pack (which stays parked); D-018 appears here only as its
  untrusted-input principles (validation before acceptance, size limits).
  **Confirm Y/N.**
- R2: "raw paste" read as: the analyst saves their paste to a file (or
  pipes stdin via `-`); no interactive editor is built. **Confirm Y/N.**
- R3: input encoding is UTF-8 (BOM tolerated per Finding B's rule); any
  other encoding refuses with `unsupported-encoding` rather than
  guessing, because mojibake in sealed evidence is silent corruption.
  **Confirm Y/N.**
- R4: the close mutation audit's scope stays `src/finding_bridge/core`
  (unchanged denominators); adapters remain unmeasured by mutation, and
  that limit is named in the outcome rather than silently true.
  **Confirm Y/N.**

## 5. Exit checklist

- [ ] Happy path: director ingests the synthetic transcript fixture
      (both Q1 formats if both are ruled), confirms, verifies, emits
      markdown and SARIF; sentinels absent from every output (findstr
      exit 1), present in the fixture (positive control).
- [ ] Negative: pre-marker garbage, missing assistant turn, empty input,
      each refusing `invalid-transcript` with line/turn located, value
      withheld.
- [ ] Negative: oversize input refuses `input-too-large` on BOTH
      in-adapters (garak retrofit demonstrated).
- [ ] Negative: non-UTF-8 input refuses `unsupported-encoding`.
- [ ] No-echo control: sentinel beside every malformed element appears in
      no refusal output.
- [ ] D2's boundary table test green, and the table covers every
      dependency call (3.4).
- [ ] GATE green with keys scrubbed; both timing numbers reported with
      the commands.
- [ ] Close audit: ratchet compared at unchanged scope (85.9%, 360/419);
      any scope change states both denominators.
- [ ] Tier re-ask ruled at the stop; outcome, eval, obligations and
      limits carried by name.

## Questions for ruling (Q1-Q4)

- **Q1, input format(s).** (a) Strict JSON only (messages array of
  {role, content}): smallest parse surface, but not what a paste looks
  like. (b) Delimited plain text only, strict grammar: lines matching
  `^(USER|ASSISTANT|SYSTEM):` open a turn, other lines continue the
  current turn, ANY text before the first marker refuses (no guessing).
  (c) **Recommended: both**, one parser entry per format chosen by
  content sniff refusing ambiguity: `{`/`[` first non-space byte means
  JSON, else the text grammar. Cost of (c): two grammars to keep hostile
  fixtures for; benefit: the actual paste use case AND a machine-friendly
  path, each strict.
- **Q2, multi-turn mapping.** (a) **Recommended:** last user turn =
  probe (sealed), last assistant turn = response (sealed), FULL
  transcript sealed as a context blob (the garak context_sealed_ref
  pattern, consistent); refuse a transcript with no assistant turn.
  (b) Whole transcript as probe (loses the probe/response distinction the
  schema carries). (c) Analyst marks turns via flags (more control, more
  friction; can be added later without unmaking (a)).
- **Q3, metadata.** **Recommended:** optional flags `--target-model`,
  `--target-model-version`, `--discovered-at` (ISO 8601, format-asserted);
  defaults null; `source_tool` fixed to `manual-transcript`
  (charter §7's own example name); harm_flags empty for the human gate to
  own. Alternative rejected in draft: defaulting discovered_at to ingest
  time (fabrication of the exact class D-024 refused).
- **Q4, size cap value.** (a) **Recommended: 10 MiB** per input file,
  both in-adapters (a transcript or hitlog beyond that is not a paste, it
  is a pipeline mistake; refusing early beats an OOM deep in sealing).
  (b) 100 MiB. (c) Configurable flag with 10 MiB default (more surface,
  deferred unless you want it now).
