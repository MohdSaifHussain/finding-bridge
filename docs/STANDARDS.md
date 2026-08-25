# Standards alignment

How the canonical finding record lines up with the official AI red-teaming
standards of 2026, field by field, from sources fetched on 2026-08-25.
Alignment claimed is alignment cited; anything uncited is not claimed
(STEP-06 contract 3.4). Where the record does not align, the gap is
stated as a limit, and where a gap needs a schema change, it is raised as
a finding with a proposal, never applied silently.

Wording law: D-042 applies to this file. The record is "sealed, with a
safe metadata preview"; the chain is tamper-evident with the OB-4 bound.

## Sources, as fetched

| Standard | Version pinned | Fetched | From | What was fetched |
|---|---|---|---|---|
| OWASP Top 10 for LLM Applications 2026 (current) | "Version 2026"; the resource page dates it August 3, 2026; the PDF's own title page reads "[Publication date to be set]" (both facts stated, neither invented) | 2026-08-25 | https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ (page 350,399 bytes; PDF download id 56857) | PDF, 2,402,520 bytes, 122 pages; successor last checked 2026-08-25 (none newer on the OWASP resources index that day) |
| OWASP Top 10 for LLM Applications 2025 (SUPERSEDED 2026-08-03; kept per the corrections law, F-5) | "Version 2025", November 18, 2024 (title page; build stamp `OWASP PDF v4.2.0a 20241114-202703`) | 2026-08-25 | https://genai.owasp.org/llm-top-10/ and the PDF behind https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/ (download id 43299) | HTML list page (912,998 bytes) and the PDF (8,768,341 bytes, 45 pages); successor: the 2026 edition above |
| OWASP GenAI Red Teaming Guide | Version 1.0, January 23, 2025 (title page) | 2026-08-25 | https://genai.owasp.org/resource/genai-red-teaming-guide/ (download id 44859) | PDF, 2,738,142 bytes, 77 pages; successor last checked 2026-08-25 (none) |
| Google Secure AI Framework (SAIF) risks | saif-data repository at commit `fe77c44481528b42d01516db9eb75d08054ca21f` (main, 2026-08-25); the risks page at saif.google | 2026-08-25 | https://github.com/google/saif-data (`yaml/risks.yaml`, 39,743 bytes) and https://saif.google/secure-ai-framework/risks | 15 risks with ids; successor last checked 2026-08-25 (main branch head is the pin) |
| MITRE ATLAS | 5.6.0 (`version:` line of the data file) | 2026-08-25 | https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml | 452,399 bytes; 170 techniques and sub-techniques under `matrices[0].techniques`; successor last checked 2026-08-25 (main branch head is the pin) |
| NIST AI 600-1, Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile | July 2024, DOI 10.6028/NIST.AI.600-1 | 2026-08-25 | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf | PDF, 1,174,643 bytes, 64 pages; successor last checked 2026-08-25 (none) |

Fetch note: OWASP's site returned 403 to a plain fetcher in the prior
session. With a browser user-agent every OWASP page and all three PDFs
returned 200. No source in this table is claimed from memory.

Standing rule (D-076): every pinned edition row carries its publication
date AND the date we last checked for a successor, and the release
checklist re-checks every pin within days of the flip.

## Field-by-field alignment

The canonical record (schema 0.5.0) carries three taxonomy arrays,
`taxonomy.owasp_llm` and `taxonomy.saif`, each entry `{id, status}` with
`status` either `confirmed` or `suggested` (charter rule 2: a suggestion
is never a finding until a human confirms it).

### taxonomy.owasp_llm, pinned to the 2026 edition

The id vocabulary is the ten 2026 entries, written the way the standard
writes them, edition included, so the pin is in the value, and the
schema's `pattern` (0.5.0, D-071) refuses anything else with
`schema-invalid`:

| id | Name (from the 2026 PDF's table of contents) |
|---|---|
| LLM01:2026 | Prompt Injection |
| LLM02:2026 | Sensitive Information Disclosure |
| LLM03:2026 | Excessive Agency |
| LLM04:2026 | Supply Chain |
| LLM05:2026 | Data and Model Poisoning |
| LLM06:2026 | Unbounded Consumption |
| LLM07:2026 | Misinformation |
| LLM08:2026 | Hidden Context Exposure |
| LLM09:2026 | Vector and Embedding Weaknesses |
| LLM10:2026 | Improper Output Handling |

**The vocabulary moved between 2025 and 2026, and an analyst holding
2025-tagged findings needs to know how.** Prompt Injection and Sensitive
Information Disclosure keep LLM01 and LLM02. Excessive Agency rises from
LLM06 to LLM03. Supply Chain moves LLM03 to LLM04, Data and Model
Poisoning LLM04 to LLM05, Unbounded Consumption LLM10 to LLM06,
Misinformation LLM09 to LLM07, Vector and Embedding Weaknesses LLM08 to
LLM09, and Improper Output Handling falls from LLM05 to LLM10. System
Prompt Leakage (LLM07:2025) does not appear under that name; LLM08:2026
is Hidden Context Exposure. The 2026 PDF carries an "Appendix A: Related
Framework Mappings" (page 58 of the PDF) that this document does not yet
reproduce; a later pass may cite it for the ATLAS and NIST rows. A
2025-tagged id is refused by the 0.5.0 pattern on purpose: re-tagging is
a human act at the gate, not a silent renumbering.

**Superseded row, kept (F-5, corrections law: original kept, direction
named).** This document first pinned the 2025 edition on 2026-08-25 as
current. It was not: the 2026 edition had been published on 2026-08-03,
three weeks before the fetch. The finder was the director, by asking
"why 2025 and not 2026" from outside the record. The 2025 list, as it was
pinned: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure,
LLM03 Supply Chain, LLM04 Data and Model Poisoning, LLM05 Improper Output
Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08
Vector and Embedding Weaknesses, LLM09 Misinformation, LLM10 Unbounded
Consumption. Direction: the correction moved the pin to the newer,
official edition. The F-4 pattern pin was built against the 2026 grammar
from the start, because F-5 landed before the 0.5.0 commit existed: it
cost a re-fetch, not a rework.

Status today: no in-adapter populates this field (garak's hitlog names a
probe and a detector, not an OWASP category, and the tool never invents
a mapping). Entries enter at the human gate, or as `suggested` from the
caged `--ai` path.

### taxonomy.saif, pinned to saif-data at commit fe77c44

The id vocabulary is the 15 risk ids in `yaml/risks.yaml`, enforced by
the schema's `pattern` (0.5.0):

| id | Risk |
|---|---|
| DP | Data Poisoning |
| UTD | Unauthorized Training Data |
| MST | Model Source Tampering |
| EDH | Excessive Data Handling |
| MXF | Model Exfiltration |
| MDT | Model Deployment Tampering |
| DMS | Denial of ML Service |
| MRE | Model Reverse Engineering |
| IIC | Insecure Integrated Component |
| PIJ | Prompt Injection |
| MEV | Model Evasion |
| SDD | Sensitive Data Disclosure |
| ISD | Inferred Sensitive Data |
| IMO | Insecure Model Output |
| RA | Rogue Actions |

The charter (section 2, Pain-5) cites SAIF for the naming problem this
field exists to solve. Same status as above: populated at the gate or
suggested, never invented.

### taxonomy.atlas (0.5.0, finding F-3 ratified)

ATLAS 5.6.0 carries the techniques a red-team finding would most often
cite, for example:

| id | Name |
|---|---|
| AML.T0051 | LLM Prompt Injection |
| AML.T0054 | LLM Jailbreak |
| AML.T0056 | Extract LLM System Prompt |
| AML.T0057 | LLM Data Leakage |
| AML.T0065 | LLM Prompt Crafting |
| AML.T0068 | LLM Prompt Obfuscation |
| AML.T0069 | Discover LLM System Information |

`taxonomy.atlas` exists since schema 0.5.0 (D-071): a third array of
`{id, status}` entries, ids pattern-pinned to the 5.6.0 grammar
(`AML.T####`, sub-techniques `AML.T####.###`), optional, empty or absent
meaning no claim, mapped in `field_map.json` to SARIF `result.taxa` plus
a third `run.taxonomies` entry and to the provisional FLARE-AI
classification slot. The OWASP GenAI Red Teaming Guide names ATLAS
beside OWASP and NIST as the frameworks a programme aligns to (printed
page 9, "frameworks such as the NIST AI RMF, OWASP and MITRE ATLAS").
Raised as finding F-3 by the first draft of this document; ratified at
STEP-06 stop one.

### harm_flags

Free strings today (`garak-detector:<detector>` from garak; empty from
transcripts). Not a taxonomy; not claimed as one. A future mapping from
garak detector names to OWASP or ATLAS ids would be an in-adapter
suggestion, marked `suggested`.

### severity

The record's rubric (exploitability, impact scope, data sensitivity,
effort; score and rationale) is the charter's LLM-adapted rubric. The
OWASP GenAI Red Teaming Guide (section "Reporting and Continuous
Improvement", printed page 44) says severity levels "are likely defined by
the business or organization" and offers Critical / High / Medium / Low
as "a general guide". The record does not impose that four-band scale;
the tracker emitter bands a score into a priority and leaves an unscored
finding `Unset` rather than guessing (D-063). Stated: the four OWASP
bands are not a field; the score is, and it is human-set.

### reproduction, provenance, preview

The same Guide section: "Each finding should include detailed
documentation of the test case, evidence collected, impact assessment,
and specific recommendations for remediation." Alignment, at the width
of the evidence:

| Guide element | Canonical field | Aligned? |
|---|---|---|
| test case | `reproduction.steps`, `reproduction.environment`, `probe` (sealed) | yes |
| evidence collected | `raw_response_sealed`, `provenance.content_hash`, `provenance.attestation_hash` | yes, sealed, with a safe metadata preview |
| impact assessment | `severity` | yes, human-set |
| recommendations for remediation | `remediation` (0.5.0, D-071) | yes, with binding constraints: optional, null until a human writes it at the gate (never-fabricate), and the `--ai` path has no remediation capability in this arc. Raised as Q-1 by the first draft of this document, which had proposed leaving it out; the director ruled it in because the Guide asks each finding to carry "specific recommendations for remediation" (printed page 44). Limit: no CLI writes the field yet, the same limit `severity.rationale` has today. |

## NIST AI 600-1: where a red-team finding record sits

NIST AI 600-1 is a profile of the AI RMF for generative AI. It does not
define a finding record. The suggested actions below are the ones whose
text this tool's record supports, quoted from the fetched PDF, with the
claim narrowed to what the tool does.

| Action id | NIST text (quoted) | What the record does | Honest gap |
|---|---|---|---|
| MS-2.8-003 | "Use digital content transparency solutions to enable the documentation of each instance where content is generated, modified, or shared to provide a tamper-proof history of the content, promote transparency, and enable traceability." | every confirmed finding is hash-chained and attested; every modification event (key rotation) is a supersession record in the same chain; every unseal is an exposure-log row | NIST's phrase is "tamper-proof". This tool's claim is narrower and stays narrower: tamper-EVIDENT, bounded by OB-4 (no defence against write access to ledger and head together). The record does not sign the head (OB-4). |
| GV-1.5-003 | "Maintain a document retention policy to keep history for test, evaluation, validation, and verification (TEVV), and digital content transparency methods for GAI." | the ledger is append-only; supersession records keep old and new heads; nothing in the tool deletes a confirmed record | retention is the operator's policy (SOP section 7 backup); the tool provides the history, not the policy |
| MS-2.7-005 | "Measure reliability of content authentication methods, such as watermarking, cryptographic signatures, digital fingerprints, as well as access controls ... which can help support the effective implementation of content provenance techniques." | content hashes over RFC 8785 canonical bytes; HMAC-keyed sealed references; attestation hashes over the gate fields | no signatures, no external anchor (OB-4); no measurement of the methods' reliability beyond the project's own tests |
| MS-2.8-002 | "Document the instructions given to data annotators or AI red-teamers." | `reproduction.steps` and the sealed `probe` document what was sent to the model | the instructions given to the human red-teamer are not a field; out of scope for a finding record |
| MG-2.2-005 | "Engage in due diligence to analyze GAI output for harmful content, potential misinformation, and CBRN-related or NCII content." | `harm_flags` carries what the source tool detected; sealing keeps the output encrypted at rest so the analysis happens through a logged unseal | the tool detects nothing itself; it records what the source tool detected |
| MS-2.7-007, MS-2.10-001, MP-5.1-005 | red-teaming as a measurement activity (prompt injection, data extraction, unforeseen failure modes) | this tool is where such a red team's failures become findings; it does not perform the red-teaming | none claimed |

Not aligned, stated: NIST AI 600-1's twelve GAI risk categories
(Information Integrity, Information Security, and the others its actions
cite) are not a field in the record and are not proposed as one now.

## Wellbeing, the tool's distinctive claim, against the Guide

The Guide's reporting section does not address red-teamer exposure to
harmful content. The record's sealing default and exposure log rest on
the research cited in the charter (section 2, Pain-3; section 6, with
the standing limit that the grey-scale evidence is secondhand), not on
any of the five standards here. Stated so nobody reads a standards
alignment into it.

## Stated limits found by real data (W6c, D-079 and D-081)

- `source_tool_version` stays null for garak records: the hitlog carries
  no version field in any release seen; garak 0.16.0 writes
  `garak_version` into the sibling `report.jsonl`, a different file. A
  `--source-tool-version` flag is proposed, not built.
- garak per-message facts `lang`, `data_type`, `data_path`,
  `data_checksum` map to `reproduction.environment` as
  `garak.<side>.<key>`; `notes` on either side is text-bearing and is
  sealed into the context blob with `goal` and `triggers`. Nothing else
  the 0.16.0 hitlog carries is dropped.
- Transcript per-record facts are whatever the operator passes with
  `--environment`, stored as `manual.<key>`; a dataset's free-text fields
  (task descriptions) are not facts and have no home by design.

## Meta-alignment: the method that built this tool

Claimed only as far as the fetched text supports (D-042 applies to
claims about the method exactly as to claims about the sealing). NIST AI
600-1 GV-1.5-003 asks for a retained history of test, evaluation,
validation and verification; MS-2.8-002 asks that the instructions given
to AI red-teamers be documented; the OWASP GenAI Red Teaming Guide's
reporting section (printed page 44) asks for "detailed documentation of
all activities, findings, and recommendations" as the basis of
transparency and improvement. Those texts concern governing AI systems
under human oversight with a documented decision trail. This project is
itself an instance of that discipline applied to AI-assisted software
development: every line of code was written by an AI under a human
director who ruled on contracts, reviewed at declared stops and verified
each phase by hand, and the record (`DECISIONS.md`, `docs/decisions/`,
the corrections table with both parties' errors) is the evidence. Not
claimed: that either standard prescribes this development method, or
that the record has been assessed against either by anyone but its
authors.

## Findings raised by this document

| # | Finding | Disposition |
|---|---|---|
| F-3 | no field for MITRE ATLAS technique ids | RATIFIED, built in 0.5.0 (D-071) |
| F-4 | taxonomy ids were unconstrained strings | RATIFIED, pattern pins in 0.5.0 (D-071), built against the 2026 OWASP grammar |
| Q-1 | no remediation field | RATIFIED as a field in 0.5.0 (D-071), human-written, null default |
| F-5 | the OWASP pin was stale on the day it was written (2025 pinned; 2026 published 2026-08-03) | corrected above; finder the director; standing rule D-076 |
