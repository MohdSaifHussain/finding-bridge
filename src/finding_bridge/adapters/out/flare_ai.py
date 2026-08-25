"""Canonical findings to FLARE-AI report format. Pure translation (3.11).

PROVISIONAL by ruling D-014. No canonical machine-readable FLARE-AI schema
existed when this was written: the builder checked ai-reports.org and
github.com/ai-flaw-reporting/ai-flaw-reporting on 2026-08-24, and the
director searched independently and also found none. The mapping is
derived from the JSON-LD vocabulary in the FLARE-AI paper (arXiv
2606.31567), carried in the field map's flare_ai column, which is the
authority for every row here.

Because it is provisional, the output SAYS SO: a provisional block at
report level and a flag on every report (the DEV-4 disambiguation
pattern). A downstream reader must never mistake this for a schema-
conformant submission.

Fields whose mapping target is null are OMITTED, never invented, and the
field map's stated reason travels with the output as documentation. The
adapter refuses unconfirmed findings and never emits sealed content.
"""

from finding_bridge import __version__
from finding_bridge.core.schema import load_field_map

REASON_UNCONFIRMED = "unconfirmed"

FLARE_PAPER = "https://arxiv.org/abs/2606.31567"

PROVISIONAL_NOTICE = (
    "PROVISIONAL. This report follows a mapping derived from the FLARE-AI "
    "paper's JSON-LD vocabulary, not a published machine-readable schema. "
    "No canonical FLARE-AI schema was locatable on 2026-08-24 (checked: "
    "ai-reports.org and github.com/ai-flaw-reporting/ai-flaw-reporting). "
    "Treat field names as provisional and re-verify before submission."
)

SEALED_CONTENT_NOTICE = (
    "Evidence is sealed. This report carries references and a metadata "
    "preview only, never the raw model output."
)


class FlareAdapterError(Exception):
    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _omitted_fields() -> dict[str, str]:
    """Canonical fields with no FLARE-AI target, and the field map's own
    stated reason for each. Omission is a recorded decision, not a gap."""
    field_map = load_field_map()
    notes = field_map["null_target_notes"]
    return {
        path: notes[path]
        for path, targets in field_map["map"].items()
        if targets.get("flare_ai") is None and path in notes
    }


def _report(finding: dict) -> dict:
    provenance = finding.get("provenance") or {}
    if provenance.get("confirmed_by") is None:
        raise FlareAdapterError(
            REASON_UNCONFIRMED,
            f"finding {finding.get('id')!r} is not confirmed; nothing unconfirmed is emitted",
        )
    severity = finding["severity"]
    report = {
        "@type": "flare:AIFlawReport",
        "flare:provisionalMapping": True,
        "schema:identifier": finding["id"],
        "schema:dateCreated": provenance["confirmed_at"],
        "schema:description": finding["preview"],
        "schema:author": {
            "@type": "schema:Person",
            "schema:name": provenance["confirmed_by"],
        },
        "flare:detectionMethod": finding["source_tool"],
        "flare:reportType": "flaw",
        "flare:evidence": {
            "@type": "flare:Evidence",
            "flare:rawReport": None,
            "sealedReferences": {
                "probe": finding["probe"]["sealed_ref"],
                "response": finding["raw_response_sealed"],
            },
            "note": SEALED_CONTENT_NOTICE,
            "contentHash": provenance["content_hash"],
        },
        "flare:stepsToReproduce": finding["reproduction"]["steps"],
    }
    if finding["target_model"]:
        report["flare:aiSystem"] = {
            "@type": "schema:SoftwareApplication",
            "schema:name": finding["target_model"],
        }
        if finding["target_model_version"]:
            report["flare:aiSystem"]["schema:softwareVersion"] = finding["target_model_version"]
    if finding["source_tool_version"]:
        report["flare:detectionMethodVersion"] = finding["source_tool_version"]
    if finding["harm_flags"]:
        report["flare:specificHarmTypes"] = finding["harm_flags"]
    if severity["score"] is not None:
        report["flare:severity"] = severity["score"]
    owasp = [e["id"] for e in finding["taxonomy"]["owasp_llm"]]
    owasp += [e["id"] for e in finding["taxonomy"].get("atlas", [])]  # 0.5.0: same slot
    saif = [e["id"] for e in finding["taxonomy"]["saif"]]
    if owasp:
        report["flare:classification"] = owasp
    if saif:
        report["flare:ThreatClassification"] = saif
    if finding.get("remediation") is not None:
        report["flare:proposedMitigation"] = finding["remediation"]  # 0.5.0, PROVISIONAL
    return report


def render_reports(findings: list[dict]) -> dict:
    """Render confirmed findings as a provisional FLARE-AI report set."""
    return {
        "@context": {
            "flare": "https://ai-reports.org/vocab#",
            "schema": "https://schema.org/",
        },
        "provisional": {
            "status": "PROVISIONAL",
            "notice": PROVISIONAL_NOTICE,
            "mappingSource": FLARE_PAPER,
            "mappingCheckedOn": "2026-08-24",
            "generator": f"finding-bridge {__version__}",
            "omittedFields": _omitted_fields(),
        },
        "reports": [_report(f) for f in findings],
    }
