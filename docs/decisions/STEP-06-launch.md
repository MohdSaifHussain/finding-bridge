# STEP-06: the launch arc, ending in the v1.0.0 public release

**Project:** finding-bridge | **Phase:** 6 | **Date:** 2026-08-25
**Status:** RATIFIED at drafting from the director's word (pre-rulings
recorded as DEV-17). Sections B-G unchanged. THREE stops.
**Depends on:** every prior phase closed; D-042 (wording law), D-012
(fixture law), D-058 (backup-not-publication; history never rewritten),
D-064..D-068 (the census and its tools).

**The bar:** the lineage's finished form (badges that state checked facts,
a README with honest numbers and live captures, an operations manual with
a document-control table, worked examples, a digest-pinned container, a
record a stranger can audit) raised by one thing the lineage did not have:
**documentation aligned to the official AI red-teaming standards of 2026,
with fetched citations.**

**ZERO product-code changes**, except the single narrow path W4 may open
if the fetched sources justify it AND the director ratifies at stop one.
Any other product defect a doc or workflow exposes is a **finding for the
director's ruling, not a quiet fix** (contract requirement 3.1).

## Deliverables

### Part One - the documents (W1-W4), then STOP ONE
| ID | Deliverable |
|---|---|
| W1 | README rebuilt: true-fact badges only (no build/container badge until its workflow is observed green, landing in the same commit); mermaid architecture with the sealing boundary drawn as a boundary; five-minute tour as observed captures; a Notation section decoding D/OB/DEV/PROV/C; honest numbers (product/governance test split computed, mutation both ways per D-066 with denominators, the built-by-an-AI-under-a-human-director sentence); limits extended; D-046 passes on the final text |
| W2 | SOP.md: document-control table (escalation POC recorded as UNMET, never invented); numbered procedures each EXECUTED before being written (D-057); includes backup/restore, which does not exist anywhere yet, and the 2am reason-code table |
| W3 | examples/01-garak-triage, 02-transcript-capture, 03-rotation-drill: narrative README each, synthetic input, exact commands, real captures, **at least one refusal per example**; fixture_scan over examples/ as a control |
| W4 | docs/STANDARDS.md from FETCHED sources (OWASP GenAI Red Teaming Guide, OWASP LLM Top 10, SAIF, MITRE ATLAS, NIST AI 600-1), with per-field alignment, version pinning, honest non-alignment, and any missing-field issue raised as a FINDING with a proposal - never a silent schema change |

### Part Two - the machinery (W5-W6), then STOP TWO
| ID | Deliverable |
|---|---|
| W5 | .github/workflows/gate.yml running tools/gate.py + fresh-wheel proof; matrix ubuntu+windows x py3.12+current; **named deliverable: the Ubuntu runner EXECUTES the project's only skip**; no secrets (stated as documentation); tests_audit excluded per D-027 with a comment |
| W5b | .github/dependabot.yml for pip, github-actions, docker; weekly, limit 5, labeled; standing rule: green gate is necessary but NOT sufficient for a major bump of anything in the hash path (rfc8785, cryptography) - that stops for a ruling |
| W6 | Dockerfile (multi-stage, digest-pinned base READ BACK from the pull, non-root, entrypoint finding-bridge) + container.yml to ghcr, private while the repo is private; layer scan proving no key material; container smoke row asserting no sealed sentinel in stdout |

### Part Three - the release (W7-W8), then STOP THREE
| ID | Deliverable |
|---|---|
| W7 | CHANGELOG (Keep a Changelog), version 1.0.0, committed release checklist, the PRE-PUBLIC AUDIT (stricter than pre-push: full history re-scanned, every doc reread, one D-046 sweep over all artifacts), OB-7 discharge PREPARED (informationUri wired, meaningless until the flip, and the row says so), branch-protection ruleset created only AFTER gate.yml has run once on master, SECURITY.md, repo security settings split by who acts with API verification afterwards, draft release notes |
| W8 | **The flip, on the director's explicit final word only.** Visibility public (repo and package, one ruling one gate), tag v1.0.0, GitHub Release, OB-7 verified, secret scanning + push protection enabled and API-verified, record closed |

## Requirements

- 3.1 Zero product-code changes outside W4's ratified path. A defect a doc
  or workflow exposes is reported, not fixed.
- 3.2 Every badge is a checked fact. A badge whose check does not yet
  exist does not exist either.
- 3.3 Every command in every document is gate-verified runnable and
  captured from a real run (D-050's class).
- 3.4 Alignment claimed is alignment cited; anything uncited is not
  claimed.
- 3.5 D-012 governs every example and fixture; D-042/D-046 govern every
  sentence.

## Stops

- **STOP ONE** after W4: the director reads README, SOP, examples,
  STANDARDS; rules on the standards mapping and any schema proposal;
  nothing proceeds to CI until then.
- **STOP TWO** after W6: CI green on both OSes and both Pythons shown, the
  converted skip shown EXECUTING on Ubuntu, container smoke and layer
  scan, a director-run `docker run`, badges true and landed, Dependabot
  live. The release act prepared, NOT performed.
- **STOP THREE**: the release ritual. Checklist fully green with evidence,
  pre-public audit clean, then HALT. **Bright line: no visibility change,
  no tag, no release act on the builder's initiative under any reading of
  this contract.**

## Deviations

**DEV-17 (the director's pre-rulings, as contract language):** file and
workflow naming, badge choice within the truth constraint, diagram
layout, example details within D-012, CHANGELOG phrasing within
D-042/D-046, and Dependabot cadence details are pre-ruled and need no
stop. NOT pre-ruled, Section C forever: any product-code change beyond
W4's ratified path, any new secret, any visibility change, any tag, any
PyPI act, and anything a document exposes as a product defect.

**DEV-18 (the director's resume word and annex, 2026-08-25, restored
after the prior session died at 100% context mid-W1):** the committed
draft above thinned the director's word. Each item below is contract
language, added by deviation, never in place. Where the draft already
says it, this row confirms it.

- W1 adds: true-fact badges (build/container badges land only with the
  first OBSERVED green run); five-minute tour from real captured output;
  D-046 passes on the final text; every command gate-verified (3.3).
- W2 adds: owner in the document-control table is Director Mohd Saif
  Hussain; escalation POC is honestly none / one operator; procedures
  are init, ingest each source, gate with and without --ai, the full
  rotation walk, verify with a 2am reason-code table, unseal with the
  exposure-log read back, every emit, BACKUP AND RESTORE (does not exist
  yet; must), and the unexpected-verify-failure incident path.
- W3 adds (proof-artifacts addendum): each example commits an output/
  folder holding the REAL emitted artifacts (packet, sarif,
  tracker/flare where relevant), a complete unedited run-transcript.md
  with at least one refusal, fixture_scan.py sweeping examples/ AND
  output/, and a control asserting each committed artifact byte-matches
  a fresh re-run (showcased-equals-current, as a CHECK). Refusals
  framing, in full: the refusals are the product behaving well and
  belong in the shop window, not hidden; an analyst evaluating a Trust
  and Safety tool judges it by how it fails at least as much as by how
  it succeeds.
- W4 adds: taxonomy.owasp_llm and taxonomy.saif pinned to a version;
  MITRE ATLAS technique ids; the NIST AI 600-1 red-team-finding mapping;
  honest non-alignments as stated limits; every source RE-FETCHED (the
  dead session's fetches are lost). OWASP's site returned 403 to the
  fetcher last time: try the official PDF endpoints and OWASP's GitHub
  mirrors; if an official source truly cannot be fetched, record a
  verification limit naming the attempts and claim nothing from it.
- Screenshots plan (new, Part One): docs/showcase/ PNGs, each under
  200KB, single-digit total, each named for the claim it proves, each
  caption pointing at the committed artifact or transcript that is the
  real proof; a screenshot proving nothing specific is not committed.
  Screenshots prove only what text cannot: SARIF Viewer render, CI
  green, the post-flip code-scanning tab. GUI captures are listed for
  the DIRECTOR with exact capture instructions; the builder verifies
  each file landed and is referenced.
- W6 adds: ghcr.io/mohdsaifhussain/finding-bridge tagged :sha and
  :latest; the v1.0.0 tag waits for W8; the digest is read back and
  recorded.
- W7 adds: license/NOTICE reread and the 38KB wheel blob (D-058)
  re-confirmed in the pre-public audit; branch protection blocks
  force-push and deletion and requires the gate check, single-operator
  bypass recorded honestly, and D-058's never-rewrite sentence becomes a
  CHECK; SECURITY.md carries private reporting, scope, and the honest
  one-operator response expectation; Dependabot alerts now, secret
  scanning and push protection at the flip, every toggle API-verified
  (clicked is not confirmed); release notes carry the two published
  numbers.
- W8 adds: optional code-scanning ingestion of our own SARIF; the final
  census, register, and builder-eval update. Bright line unchanged.
- Wording law (annex 1): D-042 governs EVERY artifact this arc produces
  (README, SOP, STANDARDS, examples, CHANGELOG, SECURITY.md, release
  notes): "sealed, with a safe metadata preview", never the
  semantic-summary claim; the OB-4 bound stated wherever the guarantee
  is stated; nothing promised that is not shipped. D-046 is the check;
  the law is broader than the check and both apply.
- Standing authorization: Sections B-G as recorded in DECISIONS.md
  (D-034, D-043.1 PROV-at-temptation, five-PROV cap, quality bar, stall
  protocol). Zero product-code changes except W4's narrow ratified path.
- Context rule: commit each document as it reaches a reviewable state;
  on approaching context exhaustion, stop at a clean commit and append a
  one-paragraph handoff note here (done / next / uncommitted).

**DEV-19 (the preservation rule for existing documents, director's
addendum, 2026-08-25, binding on all of W1-W4):** README.md and
docs/USAGE.md were read and ratified by the director at STEP-04. This arc
RESTRUCTURES them to the lineage and standards shape; it does not rewrite
them.
1. Work by edit, never by regeneration. New sections (badges, mermaid
   diagram, Notation, honest numbers, standards vocabulary, showcase
   references) are ADDED; existing sections may be REORDERED or have
   content MOVED between documents; ratified sentences travel verbatim.
2. Rephrasing an existing sentence is the exception and carries a burden:
   only where a fetched standard requires different vocabulary, a fact
   changed (counts, versions), or a defect exists (D-042/D-046 violation,
   broken command). Every rephrasing is listed in the stop-one report as
   old sentence, new sentence, reason. A rephrasing with no reason on
   that list is a finding against the arc. The director's follow-up word:
   no rephrasing; restructuring only, to the highest applicable 2026
   standards.
3. The diff is the proof: at stop one, the diffstat per document is shown
   beside the documents. A mostly-additive diff with a short listed set
   of rewordings is the arc done right.
4. The rule protects prose, not errors: anything factually wrong,
   overclaiming, or failing a check is fixed regardless, and listed.
