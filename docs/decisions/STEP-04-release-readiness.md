# STEP-04: release-readiness arc (W1 docs, W2 packaging, W3 FLARE-AI, W4 identity paper)

**Project:** finding-bridge | **Phase:** 4 | **Date:** 2026-08-25
**Status:** CLOSED, 2026-08-25, by the director's explicit word after
their ritual (63 commits, 226+1; FLARE PROVISIONAL block and sentinel
absence observed; the whitespace-marker refusal observed naming the whole
variant family, which the director judged better than the single-variant
refusal ruled; and the README install line run by both of us in fresh
venvs - the one command that had never been run has now been run twice).
All six identity questions ruled (D-051..D-056); the process-claim rule
recorded (D-057). Previously: RATIFIED at drafting - the director pre-ruled scope and
decisions in the arc authorization (recorded as DEV-15 below), Sections
B-G of the standing authorization unchanged, two declared stops. v1
completion closed at STEP-03; this arc makes it usable, installable,
FLARE-connected (provisionally), and identity-decision-ready.
**Depends on:** STEP-01..03 (all closed); D-012, D-014/OB-1, D-036,
D-042 (wording law), D-043.1 (PROV at temptation), D-044 (governed
writing), D-029/D-040 (audit + timing reporting).
**Standing rule:** top applicable standard per requirement, fetched.

## 1. Objective

An analyst who has never seen this repo can install it, run the whole
pipeline from the docs alone, and read every limit in user language; the
package installs clean into a fresh venv; findings emit to FLARE-AI's
provisional format with the provisionality stamped in the output; and the
identity family (OB-2/OB-3-history/OB-6) reaches decision-ready analysis.
Exit criterion: the director's stop-two ritual passes including a
fresh-venv row and a FLARE-AI sentinel row, and the W4 paper ends in
numbered questions ready to rule.

## 2. Deliverables (four workstreams, in order)

| ID | Deliverable | Governing standard(s) |
|---|---|---|
| W1a | README.md + docs/USAGE.md for the never-seen-it analyst: install, full command walk-through on the synthetic fixtures, all 30 reason codes in a reference table with what-to-do, limits in user language | D-042 wording law; OB-4 bound wherever the guarantee is stated; D-012 (synthetic examples, labeled) |
| W1b | Never-overclaim check: banned-phrase list recorded in a decision row; a test greps user docs for them; demonstrated RED on a planted overclaim, then green | Skill rule 5; D-042 |
| W2a | Console script `finding-bridge` (replacing `fb`); pyproject metadata complete (license, description, classifiers, requires-python) | PyPA pyproject spec (fetched STEP-01); director's name ruling |
| W2b | Schema packaging limit RESOLVED (schemas as package data via importlib.resources) or explicitly re-carried with reasons | PyPA data-files guidance, to fetch |
| W2c | Fresh-venv proof: pip install (non-editable) into a new venv, suite run against the INSTALLED package with a control asserting the import resolves to site-packages | Contract's own control law |
| W3 | `adapters/out/flare_ai.py` from the field_map flare_ai column: PROVISIONAL stamped at run and result level (DEV-4 pattern), null-target fields omitted citing the mapping table's stated reasons, shared governed writer, sentinel controls both directions, boundary rows, CLI emit-flare | D-014/OB-1 (records that no canonical schema existed at this date); D-044; D-036 |
| W4 | The identity-family paper (ANALYSIS ONLY): rotation, canonical-form change, cross-store correlation; STEP-02 §4d's migration event developed to decision-ready; options, costs, recommendation, numbered questions | D-028, D-030 condition 4, OB-6; nothing built (Section C line 2 untouched) |
| W5 | Stops' bookkeeping: tier re-asks, outcome, eval once, close audit per D-029 (adapters stay mutation-unmeasured unless a first baseline is seated, then both denominators) | D-027/D-029/D-040 |

## 3. Requirements (beyond the standing ones, all of which hold)

- 3.1 W1 promises nothing that is not shipped; every command shown is run
  before it is written down (observed, not composed).
- 3.2 W3 never fabricates a FLARE field: null-target stays absent, the
  reason carried from field_map's null_target_notes verbatim as authority.
- 3.3 Anything touching core identity bytes, sealing, or the gate is NOT
  pre-ruled and stops everything (Section C line 2, no exceptions).
- 3.4 The whitespace axis of the marker rule (D-045) is on the stop-one
  ruling agenda; it is not fixed under delegation (refusal surface).

## 4. Out of scope

PyPI or any publish/remote (installability is the deliverable, not
distribution); building anything from W4; promptfoo/PyRIT; the semantic
summary (D-042); OB-2 implementation (unblocks only at the director's
ruling on W4).

## 4a. Stops

- **Stop one, after W1+W2:** docs read by the director; fresh-venv proof
  shown; never-overclaim check demonstrated red-then-green; whitespace
  axis ruled; tier re-ask.
- **Stop two, phase close after W3+W4:** full ritual incl. fresh-venv and
  FLARE-sentinel rows; close audit with ratchet (D-029 on any scope
  change); both timing numbers; eval once at the final commit;
  obligations by name; W4's numbered questions as the ruling agenda.

## 4b. Tier, with a binding re-ask

- Proposed: **STANDARD for W1/W2a/W2c** (documentation and packaging
  consume the frozen surface; the never-overclaim check and fresh-venv
  control carry the discipline), **FULL for W2b, W3, W4** - W2b moves the
  canonical schema's load path (identity-adjacent), W3 is a new emitter
  with refusal surfaces and the OB-1 record, W4 is the identity family
  itself. The line is the ratified STEP-02 line, applied.
- Re-ask at stop one. Default: the split stands. Discharge standard for
  raising W1/W2a to FULL: a named finding that documentation or packaging
  touched a guarantee. Forecast: the default holds.

## 4c. Readings

- R1: "installability, not distribution" read as: the fresh venv is
  created and destroyed locally; no index upload, no build artifacts
  committed. **Confirm Y/N at stop one (proceeding under the plain
  reading meanwhile, per the arc's own text).**
- R2: replacing `fb` with `finding-bridge` may break nothing (no user
  base exists); the old name is removed, not aliased. **Same.**
- R3: W3's "sidecar" is the same findings.fb.jsonl the SARIF emitter
  writes, shared, not duplicated per format. **Same.**

## 5. Exit checklist (assembled at the stops; the ritual tables are the
director's half)

- [ ] W1 docs complete; every example observed before written; overclaim
      check red-then-green demonstrated.
- [ ] W2 fresh-venv install + suite from installed package, control shown.
- [ ] Schema packaging resolved or re-carried with reasons.
- [ ] W3 sentinel rows both directions; PROVISIONAL stamp present at run
      and result level; OB-1 date-record in the output and the decision
      row.
- [ ] W4 paper ends in numbered questions; nothing built.
- [ ] Audits, timings, eval, obligations per W5.

## 7. Outcome (assembled 2026-08-25; awaiting the director's stop-two ritual)

Shipped: W1-W5. GATE: **226 passed, 1 skipped**; pytest-reported median
**8.17s**, wall median **8.9s** (medians of three, `ANTHROPIC_API_KEY=dummy
python -m pytest -q`). Previous close: pytest 7.58s. Delta +0.6s for 34
new tests. Both ruff halves clean. Reason codes: 30.

### What each workstream produced
- **W1:** README.md and docs/USAGE.md, plain English, every command run
  before it was written. The overclaim check (D-046) found two real gaps
  in the builder's own README while being written, and the fixes went
  into the doc, not the test.
- **W2:** `finding-bridge` console script; Apache-2.0 (D-048) verified in
  the wheel's metadata; schemas ship as package data, resolving the old
  repo-path limit; fresh-venv proof with the import-location control.
- **W3:** FLARE-AI provisional adapter. PROVISIONAL stamped at report-set
  and report level; OB-1's date-record inside the output; 7 null-target
  fields omitted with the field map's own reasons shipped alongside.
- **W4:** the identity-family paper, analysis only, ending in six
  numbered questions. Recommendation: the supersession event (Option D),
  with Option B considered inside it and Option E parked.
- **W5:** close audit, timings, eval, obligations.

### Defects found by running, not by reading
1. **The README's install command failed** (director's docs read, D-050):
   `pip install -e . -c constraints.txt` errors in a fresh venv, exactly
   as our own D-047 predicted. The first command a new user runs. Fixed
   with an observed command; a test now blocks known-broken commands.
2. **The marker-variant family** (D-049): sweeping by RUNNING each
   variant showed space, tab, full-width colon and indentation all
   silently swallowed a turn, and BOM refused with a confusing message.
   All ruled and fixed in one family rule.
3. **The attestation comparison** was only tested in one hash ordering
   (close audit). A repeat of the class the STEP-03 eval named.
4. **Build artifacts were committed** and caught by reading the commit's
   own file list.

### The metric finding
Deleting risky code LOWERED the mutation score (schema 80.6% -> 10% on a
denominator that fell from 31 to 10). Recorded in
evidence/mutation-audit-step04-close.md: a ratchet read without its
denominator would call an improvement a regression. First time D-029's
side-by-side rule has actually mattered.

### Obligations carried, by name
OB-1 (partially served: the provisional adapter records the date and the
absence; the obligation stands until a canonical schema exists), OB-2
(blocked on OB-6; the W4 paper proposes the unblock), OB-4, OB-5, OB-6
(the paper's subject), OB-7 (GitHub ingestion + DEV-4 assumption).

### Honest limits (carried, plus this phase's)
All prior limits stand. New: the FLARE-AI mapping is provisional and says
so in its own output; adapters remain unmeasured by mutation and the
unmeasured surface grew with flare_ai.py; the wheel route is required for
hash-verified installs; Apache-2.0 is ratified for the tree only, with
publishing a separate future decision (D-048).

## 6. Deviations

**DEV-15 (the director's pre-rulings, recorded as contract language):**
README examples use synthetic fixtures only, sentinels visible and
labeled synthetic (D-012 applied to documentation). Console script name
is `finding-bridge`; rejected: `fb` (collision-prone), `findingbridge`
(worse to read). W3 output naming follows the SARIF pattern
(findings.flare.json beside the shared sidecar) unless a better one is
recorded with its alternative. Core identity/sealing/gate changes are
never pre-ruled (Section C line 2).
