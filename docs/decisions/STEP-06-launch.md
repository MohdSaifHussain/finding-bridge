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

**DEV-20 (product-code change by explicit director ruling, D-069):** the
five-minute tour capture exposed two raw tracebacks on workspace setup
(store root unwritable; key parent unwritable). The director ruled them
fixed now rather than parked for stop one. This is the 3.1 exception
taken by ruling, not by builder initiative. Files: pipeline.py,
core/sealing.py, tests/test_boundary_table.py, docs/USAGE.md (two new
reason-code rows). No other product code changes in this arc.

## STOP ONE report (builder, 2026-08-25, after W1-W4)

**Commits:** `git rev-list --count HEAD` = 92 at this report (91 before
it). Nothing pushed since resume; origin/master is at 40e4df6 (83).

**Deliverable reconciliation against the contract and DEV-18:**

| Item | State | Where |
|---|---|---|
| W1 badges, true facts, checked | done | README top; tests/test_readme_badges.py (2 negative controls) |
| W1 mermaid with the sealing boundary | done | README "Architecture" |
| W1 five-minute tour, captured | done | README; scratch store+key outside the repo, 2026-08-25 |
| W1 Notation, honest numbers, built-by-AI sentence | done | README; figures settled once at this report (287 passed / 1 skipped; 259 v 29; mutation both ways from evidence/mutation-audit-step05-close.md) |
| W1 limits extended, D-046 on final text | done | 6 bullets added; test_no_overclaim green |
| W2 SOP runbook, every procedure executed first | done | SOP.md; captures from sop-capture and the example transcripts |
| W3 three examples, output/, transcripts with refusals | done | examples/; 12 artifacts; refusals: 01 x2, 02 x2, 03 x1 (verify after tamper) |
| W3 fixture_scan over examples/ and output/ | done | tools/fixture_scan.py; leak direction with control |
| W3 byte-match control | done as NORMALISED comparison | PROV-3, pending ratification |
| W4 STANDARDS with fetched sources | done | docs/STANDARDS.md; all five re-fetched (OWASP with a browser UA) |
| W4 field mapping, version pins, ATLAS, NIST, non-alignments | done; F-3, F-4, Q-1 raised | docs/STANDARDS.md |
| Screenshots plan | done (plan; captures are the director's) | docs/showcase/README.md |

**Findings for ruling (evidence/step06-findings.md):**
F-1 fixed by D-069 (director's word). **F-2** three of four emitters
crash after any rotation (product; proposal: filter supersession records
once in the ledger read path; FULL). **F-3** no ATLAS field (proposal:
taxonomy.atlas, 0.5.0). **F-4** taxonomy ids unconstrained (proposal:
patterns). **Q-1** no remediation field (question). **PROV-3** normalised
comparison. **C-009** the builder committed with the gate red through a
pipe mask; recorded.

**DEV-19 proof, the diff:** `git diff --stat 40e4df6 -- README.md docs/USAGE.md`
= README.md +178 / -0, docs/USAGE.md +2 / -0 (two reason-code rows for
D-069). **Rephrasings of ratified sentences: none.** Fact changes in NEW
sentences only (figures settled above).

**D-042/D-046 sweep over every artifact this arc wrote** (banned list
from tests/test_no_overclaim.py, run ad hoc over SOP, STANDARDS,
showcase, three example READMEs, README, USAGE, findings): clean, with
one flagged item for the director: docs/STANDARDS.md contains
"tamper-proof" twice, both as QUOTATIONS of NIST MS-2.8-003, immediately
followed by the sentence that this tool's claim is narrower
(tamper-evident, OB-4). The law bans the claim; the quotation is
reported, not hidden, for the ruling on whether a quoted standard may
carry the phrase.

**Deferred to W5-W6, not started:** gate.yml, dependabot, container.
Nothing has gone to CI.

**Handoff note (context rule):** everything above is committed; the tree
is clean at this commit. Next is the director's stop-one reading and
rulings on F-2, F-3, F-4, Q-1, PROV-3 and the quotation question, then
W5. Uncommitted: nothing.

## STOP TWO, pre-push report (builder, 2026-08-25, after W5-W6 built locally)

**Commits:** `git rev-list --count HEAD` = 96. Tree clean. NOTHING PUSHED:
origin/master is still 40e4df6 (83). The push is a Section C act
("anything remote", D-034); the workflows cannot run, badges cannot land,
and the container cannot be built on GHCR until the director says push.

**Since stop one, by ruling:** D-070 F-2 fixed (4 emitters green after
rotation, controls red first; ledger_records() is the raw reader);
D-071/D-076 schema 0.5.0 (atlas, patterns against OWASP 2026 / SAIF
fe77c44 / ATLAS 5.6.0, remediation; emit side extended after a hand-caught
SARIF KeyError on an ATLAS claim); D-073 quotation exemption, mechanical,
all user docs scanned; D-074 gate --verdict-file; W5 gate.yml; W5b
dependabot.yml; W6 Dockerfile, .dockerignore, container.yml.

**Findings since stop one:** F-5 (director; OWASP pin stale; corrected,
D-076). F-6 (builder, W5 rehearsal; the documented hash-verified install
route never ran; fixed with a full lock and pip's secure-installs route,
negative control captured; C-010; PROV-4 pending ratification).

**DEV-19 rephrasing list (rule 4, defects only):** README install block,
two paragraphs ("To verify dependency hashes as well ... the route we
test" and "Hash verification needs a wheel ..."), reason: the command
failed (F-6). USAGE install block, two paragraphs, same reason. Diffstat
against the last push now: README +186/-10, USAGE +12/-6; every deleted
line is in those four paragraphs.

**What the push will do:** gate.yml runs on both OSes and Pythons;
container.yml builds, scans, smokes, and pushes ghcr.io/mohdsaifhussain/
finding-bridge:<sha> and :latest as a PRIVATE package (the first run may
need the package's visibility confirmed private in GHCR settings; the
builder API-verifies after). Dependabot activates on the default branch.
No badge lands until a run is observed green.

**Rehearsed locally before the push:** the fresh-wheel route (fresh venv,
import from site-packages, pip check clean, negative control); the three
YAML files parse; the gate passes via the verdict file. NOT rehearsed
locally: the container build (Docker daemon not running on this machine;
the digest was read from the registry API and the CI pull is the
read-back) and the layer scan / smoke rows, which run first on CI.

**Handoff note:** everything committed; nothing uncommitted. Next: the
director's push go, then observe the runs, record run URLs and the
read-back digest in evidence/, land badges in the same commit as the first
observed green, then STOP TWO proper (director's docker run from ghcr).

## STOP TWO report and ritual (builder, 2026-08-25)

**State:** `git rev-list --count HEAD` = 99; origin/master = 3376970 =
local HEAD at the time of this report (the ritual text below is the one
commit after it). Pushed under the director's word after the delta
pre-push audit (evidence/prepush-audit-step06.md): 98 new blobs, zero
secret shapes, zero local paths, zero key/store files, uniform noreply
identity, workflows SHA-pinned, no pull_request_target, no untrusted
input in run blocks, only GITHUB_TOKEN in container.yml.

**W6 local rehearsal (D-077, evidence/w6-local-rehearsal.md)** found three
things before CI: F-7 (lock incomplete on 3.12), F-8 (no git in the image,
so no human gate), and a blind layer scan whose positive control said so.
All three fixed and re-run locally; CI's first run then confirmed rather
than discovered.

**CI, first runs (evidence/ci-first-run-step06.md):** gate 32822503809
green on all four jobs; skips 0 on Ubuntu, 1 on Windows; fresh-wheel proof
imported from site-packages with `pip check` clean. container 32822503853
green: digest read-back on the runner equals the pin
(`sha256:3ecf5ebe...`), layer scan CLEAN after its positive control, smoke
with mounted key and gitconfig, no sealed sentinel on stdout. GHCR package
API-verified PRIVATE with `:latest` and `:<sha>`. Dependabot's three
ecosystems ran; the pip job reads constraints.txt (PROV-4 condition 1
verified). Badges landed in commit 3376970, after the first observed
green. The ghcr image was pulled and run on the builder's machine with the
mounts below (D-049: the handed command was run first).

**Second run pair, on 3376970 (gate 32822828831, container 32822828852),
both green.** The skip step now quotes its line: Ubuntu `(no SKIPPED
line: the key-permission test executed)`; Windows `SKIPPED [1]
tests\test_sealing.py:248: Windows ACLs are not set by chmod; operator
step is icacls (recorded limit)`. That is the named deliverable quoted
from the log, as contracted.

**Findings this half:** F-7, F-8 (fixed, W6 scope), the blind scan
(replaced by a tool), and one instrument defect in the pre-push audit
(the first object-scan row read 0 blobs; corrected and both rows kept).

### The director's stop-two ritual (Windows CMD)

Docker Desktop must be running first (start it, wait for the whale to
settle). Each command was run by the builder on this machine on
2026-08-25 before being written here; expected results are stated.

1. Log in to GHCR with your gh token (it carries write:packages):

```
gh auth token | docker login ghcr.io -u MohdSaifHussain --password-stdin
```
Expected: `Login Succeeded`.

2. Pull the image and read its digest back:

```
docker pull ghcr.io/mohdsaifhussain/finding-bridge:latest
docker image inspect ghcr.io/mohdsaifhussain/finding-bridge:latest --format "{{index .RepoDigests 0}} user={{.Config.User}} entrypoint={{.Config.Entrypoint}}"
```
Expected: `ghcr.io/mohdsaifhussain/finding-bridge@sha256:01f7448cc226a0b164f8bd527cc5a4767acdb00313188fedbba3874fc3f147dc user=fb entrypoint=[finding-bridge]`
(`latest` was republished by the second run, on commit 3376970; the GHCR
API lists exactly this digest for `latest`. If a later push republishes,
re-read it from `gh api user/packages/container/finding-bridge/versions`
and compare.)

3. Make a scratch folder OUTSIDE the repo and run the pipeline in the
container with the store, the key and your gitconfig mounted:

```
mkdir %TEMP%\fb-ritual\store %TEMP%\fb-ritual\key %TEMP%\fb-ritual\in
copy schemas\fixtures\garak.synthetic.hitlog.jsonl %TEMP%\fb-ritual\in\
set FB=docker run --rm -v "%TEMP%\fb-ritual\store:/work/store" -v "%TEMP%\fb-ritual\key:/home/fb/key" -v "%TEMP%\fb-ritual\in:/work/in:ro" -v "%USERPROFILE%\.gitconfig:/home/fb/.gitconfig:ro" ghcr.io/mohdsaifhussain/finding-bridge:latest --store /work/store --key /home/fb/key/fb.key
%FB% ingest-garak in/garak.synthetic.hitlog.jsonl
%FB% list
%FB% confirm <an id from list>
%FB% verify
%FB% unseal sealed/0000000000000000 --explicit
dir %TEMP%\fb-ritual\key
```
Expected, in order: `{"ingested": 3, "total_candidates": 3,
"duplicates_marked": 1}`; three lines of safe metadata previews, one
marked duplicate-of; `confirmed fb-... by <your git identity>`; `chain
verifies clean`; the negative control `blob-missing: no blob for ref
'sealed/0000000000000000'` with exit code 1 (`echo %ERRORLEVEL%` shows 1);
and `fb.key` present in the mounted key folder, proving the key lives
outside the image. Nothing on stdout contains `SENTINEL-HARM`.

4. Read by eye: the Actions tab, both workflows green on master; the
package page (private); `evidence/ci-first-run-step06.md` against the run
logs; the README's badges rendering green. Take
`docs/showcase/02-ci-green-both-oses.png` per the showcase plan if you
choose to.

5. Rulings needed to open Part Three: none pending except the ritual's
own result. The release act (W7 preparation, then W8) remains behind the
bright line.

**Handoff note:** everything committed; nothing uncommitted after the
ritual commit. Next: the director's ritual result, then W7.

**DEV-21 (W6c, real-data validation, ordered by the director at stop two,
D-078):** before W7, examples/04-real-data proves the pipeline against
data this project did not write: a real garak run (llama3.2:1b on local
Ollama; dan and promptinject; time-boxed) and one published adversarial
dataset via the transcript path (alternatives recorded). D-012 absolute:
raw data fetched by a committed script (URL + checksum) to a documented
path outside the tree; committed: transcript, sealed previews, dedup,
verify, emitted artifacts, and a run-time control scanning the committed
artifacts against real strings sampled from the local copy. OB-5 fires
(30-minute fuzzing pass or the structured alternative, reported). Every
crash, mis-parse, silent field loss or wrong refusal is a finding for
ruling. Then STOP for the director's read of example 04.

## W6c report (builder, 2026-08-25), STOP for the director's read of example 04

**State:** `git rev-list --count HEAD` = 107 after this commit; tree
clean; origin/master at 2d97085 (six commits ahead, NOT pushed: the push
is the director's word).

**Done:** examples/04-real-data (README, fetch.py with pinned checksum,
run_garak.py, committed output/ with transcript and four artifacts);
real garak run (0.16.0, llama3.2:1b on Ollama 0.32.15, 505.51 s, 699
hits, 253 exact duplicates marked); 40 Anthropic red-team transcripts
ingested (alternatives recorded); tools/realdata_leak_scan.py (5,000
real windows, CLEAN, selftest); OB-5 pass (11,063 inputs, 30 min, zero
escapes; Atheris unavailable, attempt recorded); the provenance headline
as measurements (78 rulings, 324 tests 74.7/25.3, 10 corrections 5/5,
census by section; escape trend dropped as too small and said so).

**Findings for ruling (evidence/step06-findings.md):** F-12 the garak
adapter silently loses the prompt on a real 0.16.0 hitlog (product,
FULL); F-10 the transcript grammar refuses the real-world marker form;
F-11 no per-record metadata passthrough; F-13 dropped output fields.
OB-5 disposition. The "non-coder" wording (the director's own): held for
the director's yes. C-009-class note: none this half.

**Handoff:** everything committed; uncommitted: nothing. Next: the
director's read of example 04 and rulings on F-10..F-13, OB-5, the
provenance wording; then W7.
