# CLAUDE.md

<!--
  MAINTAINER NOTE (stripped from Claude's context; visible only when a human opens this file):
  This file follows Anthropic's official Claude Code memory guidance
  (https://code.claude.com/docs/en/memory): kept under ~200 lines, specific and
  concrete, structured with headers/bullets, no pasted code, deep material pushed
  to imports. If this file grows past ~200 lines, move detail into .claude/rules/
  or docs/ — do NOT let it bloat. Bloat measurably reduces adherence.
-->

Persistent project instructions for **finding-bridge** — a universal, local-first
adapter that turns AI red-team tool output into standardized, sealed,
provenance-stamped findings that flow into the systems teams already use.

## What this project is (and is not)

- **Is:** a small CLI that ingests findings from *any* AI red-team tool, normalizes
  them to one canonical schema, hashes + timestamps them for provenance, seals
  harmful content by default, deduplicates, and emits into *any* destination
  format (SARIF, Markdown packet, FLARE-AI export, tracker JSON). Think `pandoc`
  for AI red-team findings.
- **Is NOT:** an attack tool, a scanner, a dashboard, a database, a hosted
  service, or a disclosure hub. **It never replaces existing tools — it feeds
  them.** If a change starts to duplicate garak/PyRIT/promptfoo (attack) or
  DefectDojo/FLARE-AI (aggregation/disclosure), stop and reconsider.
- Full rationale, sourced requirements, and schema: see @docs/PROJECT_CHARTER.md

## The three non-negotiable rules (this project's spine)

YOU MUST preserve these in every change. They are the reason the tool is
trustworthy, and they are the differentiator:

1. **Deterministic core.** All evidence handling — hashing, sealing, dedup,
   normalization, schema validation, format emission — is plain deterministic
   code. No AI in this path, ever. The full pipeline MUST run with zero API keys.
2. **AI is caged and off by default.** Optional AI (behind an explicit `--ai`
   flag) may ONLY draft prose: severity rationale, taxonomy-mapping *suggestions*.
   It MUST NEVER create, edit, score, hash, or alter a finding's evidence. Every
   AI-touched field is labelled as suggested and requires human confirmation.
3. **Human gate on everything that enters a finding.** Nothing becomes a
   confirmed finding without an explicit human confirmation step. Provenance
   records who confirmed what, and when.

## Safety rules (this is a Trust & Safety tool — treat as such)

- **Harmful content is sealed by default.** Raw model outputs that constitute the
  "finding" are stored encrypted-at-rest and rendered redacted. Every emitted
  format carries a grey-scaled/summary preview + metadata, NOT the raw harm, so
  downstream triagers score severity WITHOUT re-reading harmful content.
  Unsealing is always explicit and logged. (Research basis: grey-scale preserves
  judgment while reducing exposure burden; heavy blur hinders assessment — see
  charter §Pain-3.)
- **Provenance is tamper-evident.** Findings are hash-chained. Never add a code
  path that can mutate a stored finding's evidence or break the chain silently.
- **Never fabricate.** If a source field is missing, emit null/unknown — never
  invent taxonomy tags, severities, reproduction steps, or citations.
- When in doubt on a safety trade-off, prefer *less* exposure and *more* logging.
- **No real harmful model output is ever committed to this repository, in any
  phase, ever.** Fixtures use synthetic content with harmless sentinel strings
  (ruling D-012, standing safety rule).

## Tech stack & conventions

- **Language:** Python 3.12+. **Install:** `pip install -e .`
- **Layout:**
  - `src/finding_bridge/` — package code
  - `src/finding_bridge/adapters/in/` — one module per input source (garak, transcript, ...)
  - `src/finding_bridge/adapters/out/` — one module per output format (sarif, markdown, ...)
  - `src/finding_bridge/core/` — schema, hashing, sealing, dedup (deterministic only)
  - `tests/` — mirrors `src/` structure
  - `docs/` — charter, schema spec, decisions
  - `schemas/` — canonical finding JSON Schema + fixtures
- **Adapters are pure translation.** In-adapters map a source format → canonical
  finding. Out-adapters map canonical finding → a target format. No adapter
  contains business logic, sealing, or hashing — those live in `core/` only.
- **Style:** run `ruff check` and `ruff format` before every commit. The linter
  is the source of truth for style — do not hand-argue formatting.
- **No em-dashes in generated output or docs.** Use commas or parentheses.
- **Windows-aware:** the author develops on Windows CMD. Do not assume a POSIX
  shell in scripts or docs; provide cross-platform commands.

## Testing (do this before claiming anything works)

- Run `pytest` — the full suite MUST pass with **no API key set** (proves rule 1).
- Every new adapter ships with: a fixture input, an expected canonical output,
  and a round-trip test. No adapter is "done" without tests.
- Every safety-relevant behavior (sealing default-on, chain verification, dedup)
  has an explicit regression test. Never remove one to make a build pass.
- YOU MUST NOT weaken or skip a safety test to get green. Fix the code instead.

## Workflow expectations (Anthropic-style)

- **Plan before large changes.** For anything beyond a small edit, propose a
  short plan (files touched, tests added) and get confirmation before writing.
- **Small, reviewable commits** with clear messages. One concern per commit.
- **No scope creep.** New feature ideas go to @docs/PROJECT_CHARTER.md roadmap,
  not into the current change.
- **Cite sources for requirements.** Any claim about "red teamers need X" must
  trace to a source in the charter, not to an assumption. If it isn't sourced,
  mark it as an assumption to verify.
- **Ask when uncertain** rather than guessing at a safety or scope boundary.

## Definition of done (a change is complete only when all hold)

- [ ] Tests pass with zero API keys set
- [ ] New behavior has tests (incl. any safety-relevant path)
- [ ] `ruff check` and `ruff format` clean
- [ ] The three core rules still hold; sealing still defaults on
- [ ] No new dependency on / duplication of an existing attack or aggregation tool
- [ ] Docs updated if behavior or interface changed

## Key references

- Project charter (requirements, sources, schema): @docs/PROJECT_CHARTER.md
- Canonical finding schema: `schemas/finding.schema.json`
- Anthropic CLAUDE.md guidance this file follows: https://code.claude.com/docs/en/memory

Builds run under the governed-orchestration skill; phase contracts in docs/decisions/ are binding under this charter.
