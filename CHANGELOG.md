# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
(fetched 2026-08-25), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). The canonical
finding schema carries its own version (0.5.0) and its own migration
notes under `docs/decisions/`.

## [Unreleased]

## [1.0.0] - 2026-08-25

The first release. Everything below shipped between the first commit
(2026-08-24) and this tag, compressed to what a user of the tool cares
about. The full record, with every ruling and every correction, is
`DECISIONS.md` and `docs/decisions/`.

### Added

- Ingest from garak hitlogs (`ingest-garak`), both the flat Message shape
  of older garak releases and the 0.16.0 Conversation shape, with an
  explicit refusal for any other shape.
- Ingest from manual attack transcripts (`ingest-transcript`), text or
  JSON, with two exact marker grammars chosen by the operator
  (`--grammar user-assistant` or `human-assistant`) and per-record facts
  via `--environment KEY=VALUE`.
- Sealing by default: harmful content encrypted at rest (Fernet), shown
  everywhere as a safe metadata preview; `unseal` only with `--explicit`,
  every attempt and outcome logged.
- Provenance: RFC 8785 canonical hashing, a tamper-evident chain with an
  attested head, `verify` with a distinct reason code per failure mode.
- The human gate: `confirm` and `reject`, identity from git config, never
  a default.
- Exact-match dedup with clustering, marking never deleting.
- Key rotation as a recorded supersession event (`rotate-key`), verified
  across the join; the reference key is permanent, stated as a limit.
- Emitters: Markdown packet, SARIF 2.1.0 (validated by the Microsoft
  SARIF Multitool, no warnings), generic tracker JSON, and a PROVISIONAL
  FLARE-AI report set.
- Optional, caged `--ai` suggestions (severity rationale, taxonomy) that
  print for a human to weigh and never enter a finding on their own; the
  whole pipeline runs with no API key.
- Canonical schema 0.5.0 with taxonomy ids pinned to OWASP Top 10 for LLM
  Applications 2026, Google SAIF, and MITRE ATLAS 5.6.0, a human-written
  `remediation` field, and a field-mapping table to SARIF and FLARE-AI
  with a drift test.
- Every refusal names a location, never a value; every reason code is in
  the USAGE reference and the SOP's 2am table.
- Real-data validation (examples/04-real-data): a real garak 0.16.0 run
  against llama3.2:1b (699 hits) and 40 transcripts from Anthropic's
  red-team-attempts dataset (39,660 real records processed in all),
  739 of 739 attack prompts and responses sealed, three independent
  real-string leak scans over the committed artifacts clean, zero real
  bytes committed.
- Worked examples with committed artifacts and unedited transcripts;
  SOP runbook; standards alignment (OWASP, SAIF, ATLAS, NIST AI 600-1);
  a hash-locked install route; a digest-pinned container; CI on Ubuntu
  and Windows, Python 3.12 and 3.14.

### Changed

- Nothing: this is the first release.

### Fixed

- Before release, found by real data and fixed with controls: the garak
  adapter had silently dropped the attack prompt on garak 0.16.0 hitlogs;
  three emitters had crashed after a key rotation; the documented
  hash-verified install route had never run; the OWASP pin was a
  superseded edition. Each is a numbered finding in
  `evidence/step06-findings.md` and a correction in `DECISIONS.md`.

### Security

- No secret of any kind is in the repository history (full-history scan
  of every object before release, recorded in
  `evidence/pre-public-audit-step06.md`). See `SECURITY.md` for reporting.

### Known limits (stated, not hidden)

- The preview is metadata, not a summary. Tamper-evidence is bounded:
  no defence against write access to ledger and head together. Finding
  ids are store-local. Dedup is exact-match. Inputs are capped at 10 MiB.
  The reference key does not rotate. Key file permissions are not set by
  the tool on Windows. `source_tool_version` is null for garak records.
  The FLARE-AI export is provisional. Full list: `README.md`,
  `docs/USAGE.md`.

[Unreleased]: https://github.com/MohdSaifHussain/finding-bridge/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/MohdSaifHussain/finding-bridge/releases/tag/v1.0.0
