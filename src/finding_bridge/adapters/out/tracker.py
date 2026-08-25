"""Canonical findings to generic tracker JSON. Pure translation (3.11).

Shape decision (recorded with alternatives in D-063): a FLAT JSON ARRAY of
issue objects using field names common to Jira, Linear and GitHub Issues -
summary, description, labels, severity - with everything tool-specific
under `fields` rather than at the top level. No vendor lock: an importer
for any of those trackers is a field rename, not a re-parse.

Same emitter law as the others: shared governed writer, refuses
unconfirmed findings, never emits sealed content. The description carries
the preview and the provenance hashes so a ticket is traceable back to the
store it came from, and carries the OB-4 tamper-evidence bound wherever it
states the guarantee.
"""

REASON_UNCONFIRMED = "unconfirmed"

TAMPER_BOUND = (
    "Tamper-evidence bound: the hash chain and its head detect accident, "
    "drift and casual edit; they do not defend against an attacker with "
    "write access to both the ledger and its head."
)

SEALED_NOTE = (
    "Content is sealed. This ticket carries a metadata preview and "
    "references only, never the raw model output. Unsealing is explicit "
    "and logged in the originating store."
)

PRIORITY_BANDS = (
    (7, "High"),
    (4, "Medium"),
    (0, "Low"),
)


class TrackerAdapterError(Exception):
    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _priority(score) -> str:
    """Null severity maps to 'Unset', never to a guessed band: an
    unscored finding is unscored, and inventing a priority would put a
    judgement in a ticket that no human made."""
    if score is None:
        return "Unset"
    for threshold, name in PRIORITY_BANDS:
        if score >= threshold:
            return name
    return "Unset"


def _labels(finding: dict) -> list[str]:
    """Labels from taxonomy and harm flags, prefixed by family so a
    tracker's flat label space stays unambiguous. Suggested taxonomy
    entries are labeled as suggested, so an unconfirmed mapping cannot
    masquerade as a confirmed one inside a ticket."""
    labels = []
    for flag in finding.get("harm_flags") or []:
        labels.append(f"harm:{flag}")
    for family, entries in (finding.get("taxonomy") or {}).items():
        for entry in entries:
            suffix = "" if entry.get("status") == "confirmed" else "?"
            labels.append(f"{family}:{entry['id']}{suffix}")
    labels.append(f"source:{finding.get('source_tool')}")
    return labels


def _description(finding: dict) -> str:
    provenance = finding.get("provenance") or {}
    reproduction = finding.get("reproduction") or {}
    lines = [
        finding.get("preview") or "no preview recorded",
        "",
        SEALED_NOTE,
        "",
        f"Target model: {finding.get('target_model') or 'unknown'}",
        f"Source tool: {finding.get('source_tool') or 'unknown'}",
        f"Discovered at: {finding.get('discovered_at') or 'unknown'}",
        "",
        "Reproduction:",
        *[f"  {i}. {step}" for i, step in enumerate(reproduction.get("steps") or [], 1)],
        "",
        "Provenance:",
        f"  finding id: {finding.get('id')}",
        f"  content hash: {provenance.get('content_hash')}",
        f"  attestation: {provenance.get('attestation_hash')}",
        f"  confirmed by: {provenance.get('confirmed_by')} at {provenance.get('confirmed_at')}",
        "",
        TAMPER_BOUND,
    ]
    return "\n".join(lines)


def _issue(finding: dict) -> dict:
    provenance = finding.get("provenance") or {}
    if provenance.get("confirmed_by") is None:
        raise TrackerAdapterError(
            REASON_UNCONFIRMED,
            f"finding {finding.get('id')!r} is not confirmed; nothing unconfirmed is emitted",
        )
    severity = finding.get("severity") or {}
    harm = (finding.get("harm_flags") or ["unclassified"])[0]
    return {
        "summary": f"AI red-team finding {finding['id']} ({harm})",
        "description": _description(finding),
        "labels": _labels(finding),
        "priority": _priority(severity.get("score")),
        "fields": {
            "remediation": finding.get("remediation"),
            "findingBridgeId": finding["id"],
            "contentHash": provenance.get("content_hash"),
            "severityScore": severity.get("score"),
            "severityStatus": severity.get("status"),
            "sourceTool": finding.get("source_tool"),
            "targetModel": finding.get("target_model"),
            "probeSealedRef": (finding.get("probe") or {}).get("sealed_ref"),
            "responseSealedRef": finding.get("raw_response_sealed"),
            "duplicateOf": (finding.get("dedup") or {}).get("duplicate_of"),
        },
    }


def render_issues(findings: list[dict]) -> list[dict]:
    """Render confirmed findings as a flat array of tracker issues.

    Supersession records are ledger bookkeeping, not findings, and are
    skipped rather than turned into tickets nobody can action."""
    return [_issue(f) for f in findings if f.get("record_type") != "supersession"]
