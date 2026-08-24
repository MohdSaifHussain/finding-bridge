"""Canonical findings to a Markdown finding packet. Pure translation (3.11).

Target format: CommonMark 0.31.2 (https://spec.commonmark.org/, fetched
2026-08-24). The packet carries preview and metadata, NEVER raw sealed
content (contract 3.4, reading R1): only sealed references and the keyed
preview appear. Refuses any unconfirmed finding (contract 3.3). Wherever the
packet states the tamper-evidence guarantee it carries the OB-4 bound
sentence, per the director's round-2 ruling.
"""

REASON_UNCONFIRMED = "unconfirmed"

TAMPER_BOUND = (
    "Tamper-evidence bound: the hash chain and its head detect accident, "
    "drift and casual edit; they do not defend against an attacker with "
    "write access to both the ledger and its head."
)


class MarkdownAdapterError(Exception):
    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _val(value) -> str:
    return "unknown" if value is None else str(value)


def _taxonomy_lines(taxonomy: dict) -> list[str]:
    lines = []
    for family, entries in taxonomy.items():
        if entries:
            rendered = ", ".join(f"{e['id']} ({e['status']})" for e in entries)
            lines.append(f"- {family}: {rendered}")
    return lines or ["- none recorded"]


def render_finding(finding: dict) -> str:
    provenance = finding.get("provenance") or {}
    if provenance.get("confirmed_by") is None:
        raise MarkdownAdapterError(
            REASON_UNCONFIRMED,
            f"finding {finding.get('id')!r} is not confirmed; nothing unconfirmed is emitted",
        )
    severity = finding["severity"]
    rubric = severity["rubric"]
    lines = [
        f"## Finding {finding['id']}",
        "",
        f"- Source tool: {_val(finding['source_tool'])} "
        f"(version {_val(finding['source_tool_version'])})",
        f"- Target model: {_val(finding['target_model'])} "
        f"(version {_val(finding['target_model_version'])})",
        f"- Discovered at: {_val(finding['discovered_at'])}",
        f"- Harm flags: {', '.join(finding['harm_flags']) or 'none recorded'}",
        f"- Severity score: {_val(severity['score'])} ({_val(severity['status'])}); "
        f"rubric E/I/D/E: {_val(rubric['exploitability'])}/{_val(rubric['impact_scope'])}/"
        f"{_val(rubric['data_sensitivity'])}/{_val(rubric['effort'])}",
        "",
        "### Taxonomy",
        *_taxonomy_lines(finding["taxonomy"]),
        "",
        "### Preview (sealed content is never emitted)",
        "",
        f"> {finding['preview'] or 'no preview recorded'}",
        "",
        f"Sealed references: probe {_val(finding['probe']['sealed_ref'])}, "
        f"response {_val(finding['raw_response_sealed'])}. Unsealing is explicit "
        "and logged.",
        "",
        "### Reproduction",
        *[f"{i}. {step}" for i, step in enumerate(finding["reproduction"]["steps"], 1)],
    ]
    env = finding["reproduction"]["environment"]
    if env:
        lines.append("")
        lines.append("Environment: " + ", ".join(f"{k}={v}" for k, v in sorted(env.items())))
    lines += [
        "",
        "### Provenance",
        f"- Content hash: `{_val(provenance['content_hash'])}`",
        f"- Previous hash: `{_val(provenance['prev_hash'])}`",
        f"- Confirmed by: {provenance['confirmed_by']} at {_val(provenance['confirmed_at'])}",
        f"- Attestation hash: `{_val(provenance['attestation_hash'])}`",
    ]
    return "\n".join(lines)


def render_packet(findings: list[dict]) -> str:
    """Render confirmed findings into one CommonMark packet."""
    parts = [
        "# finding-bridge packet",
        "",
        f"{len(findings)} confirmed finding(s). Sealed content is stored "
        "encrypted and referenced, never inlined.",
        "",
        *[render_finding(f) + "\n" for f in findings],
        "---",
        "",
        TAMPER_BOUND,
        "",
    ]
    return "\n".join(parts)
