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
| OWASP Top 10 for LLM Applications 2025 | "Version 2025", dated November 18, 2024 (title page of the PDF; build stamp `OWASP PDF v4.2.0a 20241114-202703`) | 2026-08-25 | https://genai.owasp.org/llm-top-10/ and the PDF behind https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/ (download id 43299) | HTML list page (912,998 bytes) and the PDF (8,768,341 bytes, 45 pages) |
| OWASP GenAI Red Teaming Guide | Version 1.0, January 23, 2025 (title page) | 2026-08-25 | https://genai.owasp.org/resource/genai-red-teaming-guide/ (download id 44859) | PDF, 2,738,142 bytes, 77 pages |
| Google Secure AI Framework (SAIF) risks | saif-data repository at commit `fe77c44481528b42d01516db9eb75d08054ca21f` (main, 2026-08-25); the risks page at saif.google | 2026-08-25 | https://github.com/google/saif-data (`yaml/risks.yaml`, 39,743 bytes) and https://saif.google/secure-ai-framework/risks | 15 risks with ids |
| MITRE ATLAS | 5.6.0 (`version:` line of the data file) | 2026-08-25 | https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml | 452,399 bytes; 170 techniques and sub-techniques under `matrices[0].techniques` |
| NIST AI 600-1, Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile | July 2024, DOI 10.6028/NIST.AI.600-1 | 2026-08-25 | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf | PDF, 1,174,643 bytes, 64 pages |

Fetch note: OWASP's site returned 403 to a plain fetcher in the prior
session. With a browser user-agent every OWASP page and both PDFs
returned 200. No source in this table is claimed from memory.

## Field-by-field alignment

The canonical record (schema 0.4.0) carries two taxonomy arrays,
`taxonomy.owasp_llm` and `taxonomy.saif`, each entry `{id, status}` with
`status` either `confirmed` or `suggested` (charter rule 2: a suggestion
is never a finding until a human confirms it).

### taxonomy.owasp_llm, pinned to the 2025 edition

The id vocabulary is the ten 2025 entries, written the way the standard
writes them, edition included, so the pin is in the value:

| id | Name (from the 2025 list) |
|---|---|
| LLM01:2025 | Prompt Injection |
| LLM02:2025 | Sensitive Information Disclosure |
| LLM03:2025 | Supply Chain |
| LLM04:2025 | Data and Model Poisoning |
| LLM05:2025 | Improper Output Handling |
| LLM06:2025 | Excessive Agency |
| LLM07:2025 | System Prompt Leakage |
| LLM08:2025 | Vector and Embedding Weaknesses |
| LLM09:2025 | Misinformation |
| LLM10:2025 | Unbounded Consumption |

Status today: no in-adapter populates this field (garak's hitlog names a
probe and a detector, not an OWASP category, and the tool never invents
a mapping). Entries enter at the human gate, or as `suggested` from the
caged `--ai` path. The schema constrains the entry shape, not the id
vocabulary: see finding F-4 below.

### taxonomy.saif, pinned to saif-data at commit fe77c44

The id vocabulary is the 15 risk ids in `yaml/risks.yaml`:

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

### MITRE ATLAS technique ids: no field exists (finding F-3)

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

The canonical schema has no `taxonomy.atlas` field. Recorded as
**finding F-3**, with this proposal and nothing applied: add
`taxonomy.atlas` as a third array of the existing `taxonomy_entry`
shape, ids in ATLAS form (`AML.T0051`, sub-techniques `AML.T0051.000`);
schema 0.4.0 to 0.5.0 (a field added is a minor bump per charter
section 7); two rows in `field_map.json` (SARIF: `result.taxa` plus a
third `run.taxonomies` entry; FLARE-AI: `flare:classification`,
provisional); the drift test fires on the change until the rows land;
the OWASP GenAI Red Teaming Guide names ATLAS beside OWASP and NIST as
the frameworks a programme aligns to (printed page 9, "frameworks such as
the NIST AI RMF, OWASP and MITRE ATLAS"). Product-code change: needs the
director's ruling at stop one.

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
| recommendations for remediation | none | **not aligned**: the record has no remediation field. Stated limit. Not proposed for the schema now, because remediation is an opinion downstream tools already hold a field for (tracker description, SARIF `fix` objects), and the charter's litmus test is moving a finding, not authoring advice. Raised for the director as a question, not a finding. |

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

## Findings raised by this document

| # | Finding | Proposal | Status |
|---|---|---|---|
| F-3 | no field for MITRE ATLAS technique ids | `taxonomy.atlas`, schema 0.5.0, two field-map rows, drift test fires until they land | for the director's ruling at stop one; nothing applied |
| F-4 | `taxonomy.owasp_llm` and `taxonomy.saif` accept any non-empty string; the version pin lives only in this document and in the id convention | add `pattern` constraints: `^LLM(0[1-9]\|10):2025$` and `^(DP\|UTD\|MST\|EDH\|MXF\|MDT\|DMS\|MRE\|IIC\|PIJ\|MEV\|SDD\|ISD\|IMO\|RA)$`, so a stale or misspelled id is refused with `schema-invalid`; a new edition then becomes a deliberate schema bump, which is what a pin should cost | for the director's ruling at stop one; nothing applied |
| Q-1 | no remediation field | none proposed; question for the director | open |
