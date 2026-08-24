"""garak hitlog JSONL to canonical candidates. Pure translation (3.11).

Record structure verified against NVIDIA/garak `garak/evaluators/base.py`
(fetched 2026-08-24 from
https://raw.githubusercontent.com/NVIDIA/garak/main/garak/evaluators/base.py):
each hitlog line is one detector hit with keys goal, prompt, output,
triggers, score, run_id, attempt_id, attempt_seq, attempt_idx, generator,
probe, detector, generations_per_prompt. prompt/output are dataclass dicts of
garak Message objects (plain strings in older logs; the merged DefectDojo
parser handles the same fallbacks).

The adapter emits candidates WITHOUT id, provenance, or dedup (core stamps
those) and with transient _raw_probe/_raw_response keys that the pipeline
seals and removes. It never seals, hashes, or confirms. Missing source
fields become null, never invented: garak hitlogs carry no timestamp, so
discovered_at is null (schema 0.3.0, D-024).
"""

import json
import math
from pathlib import Path

REASON_INVALID_HITLOG = "invalid-hitlog"

# S2-1 boundary (D-038): the largest integer exactly representable in an
# IEEE 754 double; RFC 8785 refuses anything beyond it, so we refuse it at
# the boundary the untrusted data enters.
MAX_SAFE_INTEGER = 2**53 - 1

SCHEMA_VERSION = "0.3.0"


class GarakAdapterError(Exception):
    """Raised when the input is not a readable garak hitlog."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _extract_text(node) -> str | None:
    """Text of a garak Message-ish value: plain string, Message dict with
    'text', or a turns/messages container. Unknown shapes become null."""
    if node is None:
        return None
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if isinstance(node.get("text"), str):
            return node["text"]
        for key in ("turns", "messages", "parts"):
            if isinstance(node.get(key), list):
                texts = [t for t in (_extract_text(x) for x in node[key]) if t]
                return "\n".join(texts) if texts else None
        return None
    if isinstance(node, list):
        texts = [t for t in (_extract_text(x) for x in node) if t]
        return "\n".join(texts) if texts else None
    return None


def _reject_hostile_numbers(value, lineno: int, path: str) -> None:
    """S2-1 primary layer (D-038): refuse numbers RFC 8785 cannot represent
    (NaN, Infinity, integers beyond 2^53-1) at the ingest boundary. Per
    D-036 the detail names line and field path, NEVER the value: hostile
    values sit beside harmful model output, and an error message is an
    emission surface."""
    if isinstance(value, bool):
        return
    if isinstance(value, float) and not math.isfinite(value):
        raise GarakAdapterError(
            REASON_INVALID_HITLOG,
            f"line {lineno}, field {path}: non-finite number is not "
            "representable in canonical form (value withheld per D-036)",
        )
    if isinstance(value, int) and abs(value) > MAX_SAFE_INTEGER:
        raise GarakAdapterError(
            REASON_INVALID_HITLOG,
            f"line {lineno}, field {path}: integer exceeds IEEE-754 exact "
            "range (value withheld per D-036)",
        )
    if isinstance(value, dict):
        for key, sub in value.items():
            _reject_hostile_numbers(sub, lineno, f"{path}.{key}")
    elif isinstance(value, list):
        for i, sub in enumerate(value):
            _reject_hostile_numbers(sub, lineno, f"{path}[{i}]")


def _candidate_from_record(record: dict) -> dict:
    detector = record.get("detector")
    probe_name = record.get("probe")
    steps = []
    if probe_name is not None:
        target = record.get("generator") or "the target"
        step = f"Run garak probe {probe_name} against {target}"
        if detector is not None:
            step += f"; detector {detector} scored {record.get('score')}"
        steps.append(step + ".")
    # goal and triggers are TEXT-BEARING source fields: a goal often
    # describes the harm and triggers can be strings from the harmful
    # output. They never enter the candidate in the clear; the pipeline
    # seals them as a context blob (defect found by the sentinel control:
    # the fixture's goal carried the sentinel into an emitted packet).
    environment = {
        key: record[key]
        for key in (
            "run_id",
            "attempt_id",
            "attempt_seq",
            "attempt_idx",
            "generations_per_prompt",
            "score",
        )
        if key in record
    }
    context = {key: record[key] for key in ("goal", "triggers") if record.get(key) is not None}
    return {
        "schema_version": SCHEMA_VERSION,
        "source_tool": "garak",
        "source_tool_version": None,
        "target_model": record.get("generator"),
        "target_model_version": None,
        "discovered_at": None,
        "probe": {"value": None, "sealed_ref": None},
        "raw_response_sealed": None,
        "preview": None,
        "harm_flags": [f"garak-detector:{detector}"] if detector else [],
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
        "reproduction": {"steps": steps, "environment": environment or None},
        "_raw_probe": _extract_text(record.get("prompt")),
        "_raw_response": _extract_text(record.get("output")),
        "_raw_context": json.dumps(context, sort_keys=True, ensure_ascii=False)
        if context
        else None,
    }


def parse_hitlog(path: Path) -> list[dict]:
    """Parse a garak hitlog JSONL file into canonical candidates.

    Refuses unreadable input with reason code invalid-hitlog and the line
    number; empty lines are skipped."""
    candidates = []
    text = Path(path).read_text(encoding="utf-8-sig")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GarakAdapterError(
                REASON_INVALID_HITLOG, f"line {lineno} is not valid JSON: {exc.msg}"
            ) from exc
        if not isinstance(record, dict):
            raise GarakAdapterError(REASON_INVALID_HITLOG, f"line {lineno} is not a JSON object")
        for key, value in record.items():
            _reject_hostile_numbers(value, lineno, key)
        candidates.append(_candidate_from_record(record))
    return candidates
