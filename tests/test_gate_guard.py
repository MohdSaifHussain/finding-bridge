"""D7 conditions: identity rules, and the static guard that no code path
outside core/provenance.py writes the gate fields directly."""

import re
from pathlib import Path

import pytest

from finding_bridge import gate

SRC = Path(__file__).resolve().parent.parent / "src" / "finding_bridge"

GATE_FIELDS = "|".join(("confirmed_by", "confirmed_at", "attestation_hash"))
# Subscript assignment: provenance["confirmed_by"] = ...
ASSIGN_RE = re.compile(rf"\[(['\"])(?:{GATE_FIELDS})\1\]\s*=[^=]")
# Dict-literal construction: {"confirmed_by": ...}
LITERAL_RE = re.compile(rf"(['\"])(?:{GATE_FIELDS})\1\s*:")


def test_gate_fields_written_only_in_core_provenance():
    """Director's D7 condition: fails if any code path outside
    core/provenance.py writes confirmed_by, confirmed_at, or
    attestation_hash directly."""
    offenders = []
    for path in SRC.rglob("*.py"):
        if path.name == "provenance.py" and path.parent.name == "core":
            continue
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if ASSIGN_RE.search(line) or LITERAL_RE.search(line):
                offenders.append(f"{path.relative_to(SRC)}:{lineno}: {line.strip()}")
    assert not offenders, "gate fields written outside core/provenance.py:\n" + "\n".join(offenders)


def test_guard_detects_a_violation(tmp_path):
    """Negative control: the guard's patterns match the forbidden shapes."""
    assert ASSIGN_RE.search('provenance["confirmed_by"] = "someone"')
    assert LITERAL_RE.search('{"confirmed_at": now()}')
    assert not ASSIGN_RE.search('x = provenance["confirmed_by"]'), "reading is allowed"


# --- identity rules (D-011 + D7 condition: no fallback, ever) ---


def test_identity_formats_git_config(monkeypatch):
    monkeypatch.setattr(
        gate, "_git_config", lambda key: {"user.name": "A Person", "user.email": "a@x.invalid"}[key]
    )
    assert gate.get_git_identity() == "A Person <a@x.invalid>"


@pytest.mark.parametrize("missing", ["user.name", "user.email"])
def test_identity_missing_refuses_no_fallback(monkeypatch, missing):
    values = {"user.name": "A Person", "user.email": "a@x.invalid", missing: ""}
    monkeypatch.setattr(gate, "_git_config", lambda key: values[key])
    with pytest.raises(gate.GateError) as err:
        gate.get_git_identity()
    assert err.value.reason_code == "identity-missing"
