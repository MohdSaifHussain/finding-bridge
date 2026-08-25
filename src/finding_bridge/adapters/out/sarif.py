"""Canonical findings to SARIF 2.1.0. Pure translation (3.11).

Target: OASIS SARIF v2.1.0 (spec fetched 2026-08-24; the official JSON
schema is vendored at schemas/sarif-schema-2.1.0.json from
docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/, fetched the
same day). Location design per ruling Q1(a) + DEV-4: the physical location
points at the findings artifact this emitter itself writes (a file that
genuinely exists and genuinely contains the finding), one finding per line,
plus a logicalLocation for the target model; an explicit disambiguation
property at run AND result level states that the location identifies the
FINDING RECORD, not a defective source artifact. Refuses unconfirmed
findings (charter rule 3). Never emits sealed content: every value is drawn
from the canonical record, whose harmful content exists only as sealed
references and keyed previews.
"""

import json

from finding_bridge import __version__

REASON_UNCONFIRMED = "unconfirmed"

SARIF_VERSION = "2.1.0"
SARIF_SCHEMA_URI = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)

LOCATION_SEMANTICS = (
    "The physical location identifies the finding RECORD emitted by "
    "finding-bridge, not a defective source artifact. AI red-team findings "
    "have no file or line of their own; the located artifact is the findings "
    "record file emitted alongside this log."
)

TAMPER_BOUND = (
    "Tamper-evidence bound: the hash chain and its head detect accident, "
    "drift and casual edit; they do not defend against an attacker with "
    "write access to both the ledger and its head."
)

TAXONOMY_NAMES = {
    "owasp_llm": "OWASP LLM Top 10",
    "saif": "Google SAIF risk map",
    "atlas": "MITRE ATLAS",
}


class SarifAdapterError(Exception):
    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _level_and_rank(score) -> tuple[str, float | None]:
    """Severity banding recorded in D-039: null -> none (unknown is not
    invented), 0-3 note, 4-6 warning, 7-10 error; rank = score * 10."""
    if score is None:
        return "none", None
    if score >= 7:
        return "error", score * 10.0
    if score >= 4:
        return "warning", score * 10.0
    return "note", score * 10.0


def render_findings_artifact(findings: list[dict]) -> str:
    """The findings record file the SARIF locations point at: one canonical
    finding per line (JSON Lines), so finding i lives at line i+1."""
    return "".join(json.dumps(f, sort_keys=True, ensure_ascii=False) + "\n" for f in findings)


def _taxonomies(findings: list[dict]) -> tuple[list[dict], dict[str, int]]:
    used: dict[str, list[str]] = {}
    for finding in findings:
        for family, entries in finding["taxonomy"].items():
            for entry in entries:
                used.setdefault(family, [])
                if entry["id"] not in used[family]:
                    used[family].append(entry["id"])
    components = []
    index_of = {}
    for family, ids in used.items():
        index_of[family] = len(components)
        components.append(
            {
                "name": TAXONOMY_NAMES[family],
                "taxa": [{"id": taxon_id} for taxon_id in ids],
            }
        )
    return components, index_of


def _result(finding: dict, artifact_uri: str, line: int, taxonomy_index: dict[str, int]) -> dict:
    provenance = finding.get("provenance") or {}
    if provenance.get("confirmed_by") is None:
        raise SarifAdapterError(
            REASON_UNCONFIRMED,
            f"finding {finding.get('id')!r} is not confirmed; nothing unconfirmed is emitted",
        )
    severity = finding["severity"]
    level, rank = _level_and_rank(severity["score"])
    result = {
        "message": {"text": finding["preview"] or "no preview recorded"},
        "level": level,
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": artifact_uri, "index": 0},
                    "region": {"startLine": line},
                },
                "logicalLocations": [
                    {"name": finding["target_model"] or "unknown", "kind": "aiModel"}
                ],
            }
        ],
        "partialFingerprints": {
            "findingBridge/id": finding["id"],
            "findingBridge/contentHash": provenance["content_hash"],
        },
        "properties": {
            "locationSemantics": LOCATION_SEMANTICS,
            "sourceTool": finding["source_tool"],
            "sourceToolVersion": finding["source_tool_version"],
            "targetModel": finding["target_model"],
            "targetModelVersion": finding["target_model_version"],
            "discoveredAt": finding["discovered_at"],
            "probeSealedRef": finding["probe"]["sealed_ref"],
            "rawResponseSealedRef": finding["raw_response_sealed"],
            "harmFlags": finding["harm_flags"],
            "rubric": finding["severity"]["rubric"],
            "severityRationale": severity["rationale"],
            "severityStatus": severity["status"],
            "reproductionSteps": finding["reproduction"]["steps"],
            "reproductionEnvironment": finding["reproduction"]["environment"],
            "provenanceConfirmedBy": provenance["confirmed_by"],
            "provenanceConfirmedAt": provenance["confirmed_at"],
            "provenanceAttestation": provenance["attestation_hash"],
            "provenancePrevHash": provenance["prev_hash"],
            "dedupClusterId": finding["dedup"]["cluster_id"],
            "duplicateOf": finding["dedup"]["duplicate_of"],
        },
    }
    if rank is not None:
        result["rank"] = rank
    if finding["harm_flags"]:
        result["ruleId"] = finding["harm_flags"][0]
    taxa = []
    for family, entries in finding["taxonomy"].items():
        for entry in entries:
            taxa.append(
                {
                    "id": entry["id"],
                    "toolComponent": {"index": taxonomy_index[family]},
                }
            )
    if taxa:
        result["taxa"] = taxa
    if finding.get("remediation") is not None:
        # schema 0.5.0 (D-071): a human-written remediation maps to a SARIF fix
        # object (spec 3.55); absent when null, never invented.
        result["fixes"] = [{"description": {"text": finding["remediation"]}}]
    return result


def render_sarif(findings: list[dict], artifact_uri: str) -> dict:
    """Render confirmed findings as a SARIF 2.1.0 log object."""
    taxonomies, taxonomy_index = _taxonomies(findings)
    rules = []
    seen_rules = []
    for finding in findings:
        for flag in finding["harm_flags"][:1]:
            if flag not in seen_rules:
                seen_rules.append(flag)
                rules.append(
                    {
                        "id": flag,
                        "shortDescription": {"text": f"finding-bridge harm flag: {flag}"},
                    }
                )
    run = {
        "tool": {
            "driver": {
                "name": "finding-bridge",
                "version": __version__,
                "rules": rules,
                "properties": {"canonicalSchemaVersion": "0.4.0"},
            }
        },
        "artifacts": [
            {
                "location": {"uri": artifact_uri},
                "description": {"text": "finding-bridge findings record file (JSON Lines)"},
            }
        ],
        "results": [
            _result(f, artifact_uri, i + 1, taxonomy_index) for i, f in enumerate(findings)
        ],
        "properties": {
            "locationSemantics": LOCATION_SEMANTICS,
            "tamperEvidenceBound": TAMPER_BOUND,
        },
    }
    if taxonomies:
        run["taxonomies"] = taxonomies
    return {"$schema": SARIF_SCHEMA_URI, "version": SARIF_VERSION, "runs": [run]}
