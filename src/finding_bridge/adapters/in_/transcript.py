"""Manual attack transcript to canonical candidate. Pure translation (3.11).

Two strict formats, sniffed by the first non-space byte (D-041/Q1c): a
leading '{' or '[' selects JSON ({"messages": [{"role","content"}, ...]});
anything else selects the delimited text grammar. There is no guessing
between them and no third lenient path.

Delimited text grammar (DEV-10): a line opens a new turn ONLY when it
begins at column 0 with one of the exact uppercase tokens 'USER:',
'ASSISTANT:', 'SYSTEM:'. The same token anywhere else on a line is
content. Any text before the first marker refuses (no guessing a role).
Stated limit: a turn whose content contains a line starting at column 0
with a marker token cannot be represented in this format - it would open a
phantom turn - and the honest representation for such content is the JSON
format, which represents anything.

Missing knowledge is null, never invented (D-024): no detector runs here,
so harm_flags is empty, severity null, taxonomy empty; target model and
discovery time come only from explicit analyst flags.

Every refusal is location-not-value (D-036): details name the line or turn
index, never the content, which may be harmful.
"""

import json
import re

REASON_INVALID_TRANSCRIPT = "invalid-transcript"

SCHEMA_VERSION = "0.3.0"
SOURCE_TOOL = "manual-transcript"

ROLE_TOKENS = {"USER:": "user", "ASSISTANT:": "assistant", "SYSTEM:": "system"}
_MARKER_RE = re.compile(r"^(USER|ASSISTANT|SYSTEM):")
# The marker-variant family (D-049, ruled once so the next variant is a
# table lookup, not a fresh ruling). Family principle from the director:
# REFUSE when the string is more plausibly a marker than content, because
# silently swallowing a near-marker into the previous turn is a quiet
# misattribution that can change which turn seals as the probe.
#
# Covered variants, each one edit away from the exact token:
#   case      "User:" / "user:"        -> refuse (DEV-14)
#   space     "USER :"                 -> refuse
#   tab       "USER\t:"                -> refuse
#   full-width colon "USER:"          -> refuse
#   indented  "  USER:"                -> refuse
#   BOM       "﻿USER:"            -> TOLERATE: an encoding artifact,
#                                         never ambiguous, and the file
#                                         reader already strips it.
# Mid-line occurrences of any of these are plain content and never fire.
_NEAR_MARKER_RE = re.compile(
    r"^[ \t ]*(USER|ASSISTANT|SYSTEM)[ \t ]*[:：]",
    re.IGNORECASE,
)
_BOM = "﻿"
VALID_ROLES = {"user", "assistant", "system"}


class TranscriptAdapterError(Exception):
    """Raised when input is not a readable transcript; reason_code is
    machine-readable, detail is location-not-value (D-036)."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _parse_text(text: str) -> list[dict]:
    turns: list[dict] = []
    current: dict | None = None
    text = text.removeprefix(_BOM)  # encoding artifact, not content (D-049)
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = _MARKER_RE.match(line)
        if match:
            token = match.group(0)
            role = ROLE_TOKENS[token]
            current = {"role": role, "content": line[len(token) :].lstrip()}
            turns.append(current)
        elif _NEAR_MARKER_RE.match(line):
            raise TranscriptAdapterError(
                REASON_INVALID_TRANSCRIPT,
                f"line {lineno}: suspected marker that is not the exact token "
                "(check case, spaces or tabs before the colon, a full-width "
                "colon, or indentation; markers are exact uppercase "
                "USER:/ASSISTANT:/SYSTEM: at line start); value withheld "
                "per D-036",
            )
        elif current is None:
            if not line.strip():
                continue  # blank lines before the first marker carry nothing
            raise TranscriptAdapterError(
                REASON_INVALID_TRANSCRIPT,
                f"line {lineno}: content before the first role marker "
                "(USER:/ASSISTANT:/SYSTEM: at line start); value withheld per D-036",
            )
        else:
            current["content"] += "\n" + line
    if not turns:
        raise TranscriptAdapterError(
            REASON_INVALID_TRANSCRIPT, "no role markers found; empty or unstructured input"
        )
    return turns


def _parse_json(text: str) -> list[dict]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TranscriptAdapterError(
            REASON_INVALID_TRANSCRIPT,
            f"line {exc.lineno}: invalid JSON ({exc.msg}); value withheld per D-036",
        ) from exc
    messages = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(messages, list) or not messages:
        raise TranscriptAdapterError(
            REASON_INVALID_TRANSCRIPT,
            "JSON transcript must be a non-empty messages array",
        )
    turns = []
    for i, message in enumerate(messages):
        if not isinstance(message, dict) or "role" not in message or "content" not in message:
            raise TranscriptAdapterError(
                REASON_INVALID_TRANSCRIPT,
                f"message index {i}: each message needs 'role' and 'content'",
            )
        role = message["role"]
        if role not in VALID_ROLES:
            raise TranscriptAdapterError(
                REASON_INVALID_TRANSCRIPT,
                f"message index {i}: role must be one of {sorted(VALID_ROLES)}",
            )
        if not isinstance(message["content"], str):
            raise TranscriptAdapterError(
                REASON_INVALID_TRANSCRIPT,
                f"message index {i}: content must be a string",
            )
        turns.append({"role": role, "content": message["content"]})
    return turns


def parse_turns(text: str) -> list[dict]:
    """Parse a transcript into role/content turns, format chosen by sniff."""
    stripped = text.lstrip()
    if not stripped:
        raise TranscriptAdapterError(REASON_INVALID_TRANSCRIPT, "input is empty")
    if stripped[0] in "{[":
        return _parse_json(text)
    return _parse_text(text)


def to_candidate(text: str, metadata: dict | None = None) -> dict:
    """One transcript to one canonical candidate (Q2a mapping).

    Last user turn = probe, last assistant turn = response, whole transcript
    sealed as context. Refuses a transcript with no assistant turn. Emits
    transient _raw_* keys the pipeline seals and removes; never seals or
    hashes here (3.11)."""
    metadata = metadata or {}
    turns = parse_turns(text)
    assistant_turns = [t for t in turns if t["role"] == "assistant"]
    if not assistant_turns:
        raise TranscriptAdapterError(
            REASON_INVALID_TRANSCRIPT,
            "transcript has no assistant turn; there is no model response to seal",
        )
    user_turns = [t for t in turns if t["role"] == "user"]
    probe_text = user_turns[-1]["content"] if user_turns else None
    response_text = assistant_turns[-1]["content"]
    context_text = "\n".join(f"{t['role'].upper()}: {t['content']}" for t in turns)
    return {
        "schema_version": SCHEMA_VERSION,
        "source_tool": SOURCE_TOOL,
        "source_tool_version": None,
        "target_model": metadata.get("target_model"),
        "target_model_version": metadata.get("target_model_version"),
        "discovered_at": metadata.get("discovered_at"),
        "probe": {"value": None, "sealed_ref": None},
        "raw_response_sealed": None,
        "preview": None,
        "harm_flags": [],
        "taxonomy": {"owasp_llm": [], "saif": []},
        "severity": {
            "score": None,
            "rubric": {
                "exploitability": None,
                "impact_scope": None,
                "data_sensitivity": None,
                "effort": None,
            },
            "rationale": None,
            "status": None,
        },
        "reproduction": {
            "steps": [f"Replay the captured {len(turns)}-turn transcript against the target."],
            "environment": {"turn_count": len(turns)},
        },
        "_raw_probe": probe_text,
        "_raw_response": response_text,
        "_raw_context": context_text,
    }
