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
