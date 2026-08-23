# finding-bridge — Project Charter

> Deep reference for the project. `CLAUDE.md` (repo root) is the lean per-session
> file; this charter holds the full rationale, sourced requirements, schema, and
> roadmap. Read `CLAUDE.md` first; come here for the "why" and the evidence.

**Status:** pre-v1 (spec locked, implementation not started)
**Last reviewed:** 2026-08-24

---

## 1. One-line description

A universal, local-first CLI adapter that turns the output of any AI red-team
tool into standardized, sealed, provenance-stamped findings, and emits them into
the systems teams already use. **Attack tools find failures; finding-bridge is
where a failure becomes a finding — normalized, provable, sealed, and
disclosure-ready.**

The mental model is deliberately humble: `pandoc` / `ffmpeg` for AI red-team
findings. It converts between formats and does the boring lifecycle work in the
middle. It does not compete with the tools on either end of the pipe.

```
ANY SOURCE                 THE PIPE (deterministic core)        ANY DESTINATION
------------               -----------------------------        ---------------
garak JSONL      --,       normalize to one canonical      ,--> SARIF (GitHub Security tab)
PyRIT runs       --|       finding record                  |--> FLARE-AI export
promptfoo output --+-->     + hash + timestamp (provenance) +--> Markdown finding packet
raw transcript   --|        + seal harmful content         |--> tracker JSON (Jira/Linear)
CSV / JSONL      --'        + deduplicate + cluster         '--> xlsx / CSV tracker
                            (human confirms before emit)
```

---

## 2. Why this exists — the problem, with sources

AI red teaming professionalized fast, and the *evidence layer* under it did not
keep up. Five sourced problems define the gap this tool fills.

### Pain-1 — Findings are now legal-grade paperwork, produced by hand

The field converged on the demand that findings be reproducible, mapped to a
taxonomy, and audit-ready. Practitioner guidance is explicit that vague findings
are worthless: a finding must map each vulnerability to its OWASP LLM Top 10
category, the affected component, a reproduction case, and a remediation path,
because "the model can be jailbroken" is not actionable.
*Source: Repello AI, "AI Red Teaming: The Complete Guide for Security Teams (2026)"
— https://repello.ai/blog/the-essential-guide-to-ai-red-teaming-in-2024*

A 2026 systematic review frames the whole field's direction as a shift toward
audit-ready artifacts and traceable links between findings, mitigations, and
governance outcomes ("from clever adversarial prompting toward disciplined,
lifecycle-integrated assurance engineering").
*Source: "A Systematic Review of Algorithmic Red Teaming Methodologies…", arXiv
2602.21267 — https://arxiv.org/pdf/2602.21267*

**Implication for the tool:** the packet-writing / format-translation labor is
the time sink, and it is deterministic work a machine should do.

### Pain-2 — Reproducibility is intrinsically hard with non-deterministic targets

Model outputs vary across identical prompts, which undermines traditional testing
baselines and makes a finding hard to re-demonstrate later.
*Source: Palo Alto Networks, "What Is AI Red Teaming?" —
https://www.paloaltonetworks.com/cyberpedia/what-is-ai-red-teaming*

**Implication for the tool:** a finding's value decays unless the exact probe,
target model + version, timestamp, and raw response are captured immutably at the
moment of discovery. Provenance is not a nice-to-have; it is what keeps a finding
credible after the model changes.

### Pain-3 — Analyst wellbeing is unmet, and research explicitly asks for tooling

Red teamers engage directly with harmful, biased, or manipulative outputs and
face psychological stress, burnout, or trauma; scaling the work without
deliberate design reproduces those harms at larger scale.
*Source: "Human Expertise for AI Red-Teaming and Scalable Evaluation", CHI 2026
Extended Abstracts — https://dl.acm.org/doi/10.1145/3772363.3778702*

Crucially, the research does not just name the problem — it asks for the
solution to be built into tools, and gives design guidance. A Feb 2026 paper
states that safeguards in red-team studies "remained at a fairly manual protocol
level" and that future work "should explore how to make such monitoring and
support scalable… by embedding safeguards into the systems used for red-team
activities," and notes that grey-scaling reduces burden while preserving judgment
whereas excessive blurring hinders risk assessment.
*Source: "Dark and Bright Side of Participatory Red-Teaming…", arXiv 2602.19124 —
https://arxiv.org/pdf/2602.19124*

A FAccT 2025 paper argues the unmet mental-health needs of AI red-teamers are a
critical workplace-safety concern and proposes adapting safeguards from content
moderation.
*Source: "When Testing AI Tests Us", FAccT 2025 —
https://dl.acm.org/doi/10.1145/3715275.3732120*

**Implication for the tool — and its most distinctive feature:** seal harmful
content by default; show grey-scaled/summary previews plus metadata so triage and
severity scoring happen without re-reading raw harm; log every unseal. No tool in
the current landscape does this. See §6.

### Pain-4 — Scanner output is a raw dump that a human must triage by hand

A garak run can produce hundreds of "failures"; the analyst must manually triage
each for real impact and relevance before any of it is usable.
*Source: Attila Rácz-Akácosi, "Automated Red Teaming: Using PyRIT, Garak, and
PromptFoo…" — https://aiq.hu/en/automated-red-teaming-using-pyrit-garak-and-promptfoo-to-uncover-vulnerabilities/*

**Implication for the tool:** ingesting a dump, deduplicating by content hash,
clustering, and queueing for human severity scoring turns the tools' biggest
annoyance into finding-bridge's onboarding funnel.

### Pain-5 — Taxonomy chaos: the same flaw has many names

Google built SAIF partly because the same technique gets called prompt injection,
instruction hijacking, prompt hacking, or jailbreaking, making flaws hard to
track and discuss consistently.
*Source: Google SAIF data repository — https://github.com/google/saif-data*

**Implication for the tool:** ship SAIF's machine-readable risk map and the OWASP
LLM Top 10 as bundled data; map findings to both (AI-suggested, human-confirmed,
deterministically stored).

---

## 3. Proof of demand (not assumption)

This tool was validated against the market before spec, specifically to avoid
re-deriving something that already exists.

- **A real, dated, unfulfilled request for exactly this bridge.** An open feature
  request on DefectDojo — the most widely used open-source vulnerability
  management platform — filed May 2026 and still open, asks for a parser to map
  garak's JSONL output to DefectDojo findings, noting the platform "lacks a
  dedicated parser for AI-specific vulnerability scanners, making it difficult to
  aggregate AI red-teaming results alongside traditional infrastructure/appsec
  scans."
  *Source: DefectDojo issue #14878 —
  https://github.com/DefectDojo/django-DefectDojo/issues/14878*

- **The public-disclosure hub exists but is explicitly not the analyst's desk.**
  FLARE-AI (MIT, open-source, ICML 2026) routes a single public flaw report to
  many recipients — but its own paper positions it as an ecosystem coordination
  tool, "not a compliance reporting tool," and it is a public web form unsuitable
  for confidential in-house or pre-disclosure findings. finding-bridge is
  complementary: it is where findings live *before* disclosure, and it can
  *export to* FLARE-AI's format.
  *Sources: FLARE-AI paper, arXiv 2606.31567 — https://arxiv.org/abs/2606.31567 ;
  MIT announcement — https://airisk.mit.edu/blog/announcing-flare-ai*

- **SARIF is the mature, natively-consumed interchange format for security
  findings — and no bridge exists from AI red-team tools onto it.** GitHub Code
  Scanning speaks SARIF natively; every finding becomes a triageable alert with
  PR annotations and branch-protection integration.
  *Sources: OASIS SARIF v2.1.0 spec —
  https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html ; SARIF Home —
  https://sarifweb.azurewebsites.net/*

**Audience reality check:** the global population of AI red teamers is thousands,
not millions. This is a concentrated, high-value audience (they cluster on the
garak/PyRIT GitHub, the OWASP GenAI community, and AI-village venues, and include
hiring managers at AI labs). The design optimizes for the right few hundred
users, not mass adoption.

---

## 4. Non-goals (scope guard)

finding-bridge is explicitly NOT, and v1 will not become:

- an attack / scanning / fuzzing tool (that space is saturated: garak, PyRIT,
  promptfoo, DeepTeam, and commercial platforms already own it);
- a findings *database* or *dashboard* (that is DefectDojo's job — finding-bridge
  feeds it);
- a public disclosure *hub* (that is FLARE-AI's job — finding-bridge exports to
  it);
- a hosted service, web app, or account-based product;
- a new *standard* the world must adopt — the canonical schema is internal
  plumbing, versioned humbly, existing to enable translation, not to compete with
  SARIF/OCSF/AVID.

Litmus test for any proposed change: *does it help a finding move from one tool to
another, more safely and with less human toil?* If yes, in scope. If it starts
replacing a tool on either end of the pipe, out of scope.

---

## 5. Architecture

### 5.1 The three non-negotiable rules (mirrored in CLAUDE.md, expanded here)

1. **Deterministic core.** Hashing, sealing, dedup, normalization, schema
   validation, and format emission are plain deterministic code with no AI in the
   path. The entire pipeline must run correctly with no API key present. This is
   both a correctness guarantee and a trust guarantee: evidence is never
   model-touched.

2. **AI is caged and off by default.** Optional AI (explicit `--ai` flag) may
   only draft prose — severity rationale text and taxonomy-mapping *suggestions*.
   It may never create, edit, score, hash, seal, or otherwise alter a finding's
   evidence or provenance. Every field an AI touched is labelled `suggested` and
   requires human confirmation before it is part of a finding.

3. **Human gate.** Nothing becomes a *confirmed* finding without an explicit human
   confirmation step. The provenance record captures who confirmed and when.

*(These three rules are the author's established method, applied here. They are
the differentiator, not boilerplate: a red-team evidence tool whose evidence
could be silently rewritten by a model would be worthless.)*

### 5.2 Component layout

- `core/` — deterministic only:
  - `schema.py` — the canonical finding model + validation
  - `provenance.py` — SHA-256 hashing, timestamps, hash-chaining, verification
  - `sealing.py` — encrypt-at-rest of harmful content, grey-scale/summary preview
    generation, unseal + exposure logging
  - `dedup.py` — content-hash dedup + clustering
- `adapters/in/` — one module per source (v1: `garak.py`, `transcript.py`).
  Pure translation: source format → canonical finding. No sealing/hashing here;
  they call `core/`.
- `adapters/out/` — one module per destination (v1: `sarif.py`, `markdown.py`).
  Pure translation: canonical finding → target format.
- `ai/` — optional, isolated. Taxonomy-suggestion + rationale-draft helpers.
  Import-guarded so the tool runs fully without it and without any API key.
- `cli.py` — wiring only.

### 5.3 Data flow (happy path)

1. `ingest` — an in-adapter reads a source file/stream, emits raw candidate
   findings.
2. `core.provenance` — hash + timestamp each candidate; capture target model +
   version if present in source.
3. `core.sealing` — detect/flag harmful content and seal it (default on);
   generate preview.
4. `core.dedup` — drop/merge duplicates by content hash; cluster near-duplicates.
5. **human gate** — analyst reviews the queue, confirms/rejects, sets or confirms
   severity (optionally aided by `--ai` suggestions).
6. `emit` — an out-adapter renders confirmed findings into the chosen destination
   format, carrying preview + metadata, never raw harm, unless explicitly
   unsealed.

---

## 6. The wellbeing feature (design detail)

This is the tool's soul and its clearest novelty; it is directly research-derived
(Pain-3). Requirements:

- Raw model outputs that constitute a finding are **sealed by default**: encrypted
  at rest, rendered redacted in any default view.
- Every emitted artifact (SARIF alert, Markdown packet, tracker ticket) carries a
  **grey-scaled/summary preview + structured metadata** (category, severity,
  reproduction recipe) so a reviewer or lead can triage and score **without
  re-reading raw harm**. Grey-scale/summary, not heavy blur — per arXiv 2602.19124,
  grey-scale preserves judgment while excessive blur hinders assessment.
- **Unsealing is always explicit and logged** (who, when, which finding) —
  producing an exposure record per analyst.
- Optional session-exposure hints (e.g., a rotation nudge after prolonged
  harmful-content review) — v2, but the schema reserves space now.

None of the tools surveyed (garak, PyRIT, promptfoo, DeepTeam, DefectDojo,
FLARE-AI, commercial platforms) ship any of this. It is the composition —
universality + provenance + wellbeing sealing — that makes finding-bridge
original rather than a re-derivation.

---

## 7. Canonical finding schema (v0 draft — see `schemas/finding.schema.json`)

Fields (each finding is a JSON object):

- `id` — stable content-derived id
- `source_tool` — e.g. `garak`, `manual-transcript`
- `source_tool_version` — string or null
- `target_model` — string or null
- `target_model_version` — string or null
- `discovered_at` — ISO 8601 timestamp
- `probe` — the attack/prompt used (may itself be sealed if harmful)
- `raw_response_sealed` — sealed blob reference (never inline raw harm)
- `preview` — grey-scale/summary safe-to-read rendering
- `harm_flags` — list of detected harmful-content categories
- `taxonomy` — object: `{ owasp_llm: [...], saif: [...] }`, each entry tagged
  `confirmed` or `suggested`
- `severity` — object: `{ score, rubric, rationale, tagged confirmed|suggested }`
  (rubric is an LLM-adapted rubric — exploitability / impact scope / data
  sensitivity / effort — because CVSS is not well-adapted to LLM flaws; see
  Repello source in Pain-1)
- `reproduction` — structured recipe (steps, environment)
- `provenance` — object: `{ content_hash, prev_hash, confirmed_by, confirmed_at }`
- `dedup` — object: `{ cluster_id, duplicate_of }`

The schema is versioned. Adding a field is a minor bump; changing/removing one is
a major bump and requires a migration note in `docs/decisions/`.

---

## 8. Roadmap (checkboxes so Claude Code can track progress)

### v1 — prove the thesis end to end (smallest complete slice)

- [ ] Canonical finding schema + JSON Schema file + fixtures
- [ ] `core/provenance` — hashing, timestamps, chain + verification, with tests
- [ ] `core/sealing` — seal-by-default + preview + unseal logging, with tests
- [ ] `core/dedup` — content-hash dedup, with tests
- [ ] In-adapter: `garak` (JSONL → canonical) + round-trip test
- [ ] In-adapter: `transcript` (raw paste → canonical) + round-trip test
- [ ] Out-adapter: `sarif` (canonical → SARIF 2.1.0) + validation test
- [ ] Out-adapter: `markdown` (canonical → finding packet) + test
- [ ] Human-gate review flow in CLI
- [ ] Full suite green with **no API key set**
- [ ] README with the time-math table (see §9) and the "feeds, not replaces" framing

### v1.x — reach the users where they already are

- [ ] Contribute a garak parser to DefectDojo (issue #14878) as a launch move and
      trailer for the standalone tool
- [ ] Out-adapter: FLARE-AI export format
- [ ] In-adapter: promptfoo
- [ ] Optional `--ai` taxonomy suggestions + severity rationale (caged, off by default)

### v2 — depth

- [ ] In-adapter: PyRIT
- [ ] Out-adapters: tracker JSON (Jira/Linear), xlsx/CSV
- [ ] Session-exposure hints / rotation nudges
- [ ] Retest recipe replay (re-run a stored reproduction, record breach-rate drift)

---

## 9. The time argument (the README's headline)

Per finding today, the non-creative labor: triage a raw dump line (~5-10 min),
write the packet (~30-60 min), translate to tracker/ticket format (~10 min),
check "did we already find this" (~10 min, often skipped, causing duplicate work
downstream). Roughly 60-90 minutes of toil per finding. finding-bridge collapses
that to a command plus a human review pass. An analyst producing ~10 findings a
week gets about a day back. That sentence is the reason a stranger installs it.

*(These figures are an internal estimate synthesized from the workflow described
in the Pain-1 and Pain-4 sources; label them as an estimate, not a measured
benchmark, until validated with real users.)*

---

## 10. Source index

Primary / official:
- Google SAIF (framework): https://saif.google/secure-ai-framework
- Google SAIF map: https://saif.google/secure-ai-framework/saif-map
- Google SAIF machine-readable data: https://github.com/google/saif-data
- Google CART role (careers): https://www.google.com/about/careers/applications/jobs/results/98948336718881478-senior-analyst-content-adversarial-red-team
- OASIS SARIF v2.1.0 spec: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- SARIF Home: https://sarifweb.azurewebsites.net/
- Anthropic Claude Code memory guidance (structure of CLAUDE.md): https://code.claude.com/docs/en/memory

Peer-reviewed / preprint (requirements evidence):
- Third-party flaw disclosure (Longpre et al., ICML 2025): https://arxiv.org/abs/2503.16861
- FLARE-AI (ICML 2026): https://arxiv.org/abs/2606.31567
- Red-teamer wellbeing / embedded safeguards (Feb 2026): https://arxiv.org/pdf/2602.19124
- Red-teamer mental health (FAccT 2025): https://dl.acm.org/doi/10.1145/3715275.3732120
- Human expertise + tooling/wellbeing needs (CHI 2026): https://dl.acm.org/doi/10.1145/3772363.3778702
- Systematic review of red-teaming methodologies (2026): https://arxiv.org/pdf/2602.21267

Practitioner (workflow evidence):
- Repello AI 2026 guide (findings must be actionable, adapted rubric): https://repello.ai/blog/the-essential-guide-to-ai-red-teaming-in-2024
- Palo Alto Networks (non-determinism / reproducibility): https://www.paloaltonetworks.com/cyberpedia/what-is-ai-red-teaming
- garak/PyRIT/promptfoo triage pain: https://aiq.hu/en/automated-red-teaming-using-pyrit-garak-and-promptfoo-to-uncover-vulnerabilities/

Demand signal:
- DefectDojo issue #14878 (asks for exactly this bridge): https://github.com/DefectDojo/django-DefectDojo/issues/14878

> Note on sourcing: official specs and peer-reviewed papers are load-bearing.
> Practitioner blogs are used only for workflow/time-cost color and are labelled
> as such. Any requirement in this charter that lacks a source above should be
> treated as an assumption to verify, not a fact.
