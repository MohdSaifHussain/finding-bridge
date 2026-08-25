"""W2a/W2e controls: the cage, proven by import tracking and degradation.

These are the tests that make charter rule 2 structural rather than
promised.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "schemas" / "fixtures"
HITLOG = FIXTURES / "garak.synthetic.hitlog.jsonl"


# --- W2a: the pipeline never IMPORTS the ai package without --ai ---


def run_pipeline_in_subprocess(tmp_path: Path, extra: str = "") -> dict:
    """Run a full pipeline in a FRESH interpreter and report which
    finding_bridge modules ended up imported. A subprocess is used
    deliberately: in-process assertions would be polluted by whatever the
    test session already imported."""
    script = f"""
import json, sys
sys.path.insert(0, {str(REPO / "src")!r})
from pathlib import Path
from finding_bridge import pipeline
ws = pipeline.Workspace(
    Path({str(tmp_path / "store")!r}),
    Path({str(tmp_path / "k" / "fb.key")!r}),
    Path({str(tmp_path / "repo")!r}),
)
ws.ingest_garak(Path({str(HITLOG)!r}))
ws.confirm(ws.list_candidates()[0]["id"], "Cage Analyst <c@example.invalid>")
ws.verify()
from finding_bridge.adapters.out import markdown, sarif, flare_ai
markdown.render_packet(ws.confirmed_findings())
sarif.render_sarif(ws.confirmed_findings(), "f.jsonl")
flare_ai.render_reports(ws.confirmed_findings())
{extra}
print(json.dumps(sorted(m for m in sys.modules if m.startswith("finding_bridge"))))
"""
    (tmp_path / "repo").mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr[-1500:]
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_full_pipeline_never_imports_ai(tmp_path: Path):
    """The cage, tracked not asserted: run ingest, gate, verify and all
    three emitters, then look at sys.modules."""
    modules = run_pipeline_in_subprocess(tmp_path)
    ai_modules = [m for m in modules if m.startswith("finding_bridge.ai")]
    assert ai_modules == [], f"the deterministic pipeline imported: {ai_modules}"
    assert "finding_bridge.core.provenance" in modules, "the tracker must see real imports"


def test_the_import_tracker_can_detect_an_import(tmp_path: Path):
    """The control proves it can fail: the same run, with the ai package
    deliberately imported, must show up."""
    modules = run_pipeline_in_subprocess(
        tmp_path, extra="import finding_bridge.ai.suggest  # deliberate\n"
    )
    assert any(m.startswith("finding_bridge.ai") for m in modules)


def test_cli_help_does_not_import_ai(tmp_path: Path):
    """Even the CLI's own module graph stays clean until --ai is used."""
    script = (
        f"import sys, json; sys.path.insert(0, {str(REPO / 'src')!r});"
        "from finding_bridge import cli;"
        'print(json.dumps([m for m in sys.modules if m.startswith("finding_bridge.ai")]))'
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr[-800:]
    assert json.loads(result.stdout.strip()) == []


# --- W2e: failure degrades to exactly the no-ai behaviour ---


def test_missing_key_refuses_governed(monkeypatch):
    from finding_bridge.ai import suggest

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(suggest.AiUnavailable) as err:
        suggest.suggest_severity_rationale({"preview": "x"}, model="pinned-model-id")
    assert err.value.reason_code == "ai-key-missing"
    assert "deterministic pipeline is unaffected" in err.value.detail


def test_dead_network_refuses_governed_and_never_raises_sdk_errors(monkeypatch):
    """The kill-the-network control: whatever the SDK raises, the caller
    sees ai-unavailable, never a transport exception."""
    from finding_bridge.ai import suggest

    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy-key-for-this-test")

    class DeadClient:
        class messages:  # noqa: N801
            @staticmethod
            def create(**kwargs):
                raise ConnectionError("network is down")

    monkeypatch.setattr(suggest, "_client", lambda model: DeadClient())
    with pytest.raises(suggest.AiUnavailable) as err:
        suggest.suggest_taxonomy({"preview": "x"}, model="pinned-model-id")
    assert err.value.reason_code == "ai-unavailable"
    assert "deterministic pipeline is unaffected" in err.value.detail


def test_emitted_packet_is_byte_identical_when_ai_fails(tmp_path: Path):
    """The degradation guarantee, measured on ONE store: emit the packet,
    then run every suggestion (all failing), then emit again. The bytes
    must be identical.

    An earlier version of this test compared TWO stores and failed on
    their differing ids - a test measuring the wrong object, the same
    shape as the director's own C-007. One store removes the confound."""
    from finding_bridge import pipeline
    from finding_bridge.adapters.out import markdown
    from finding_bridge.ai import suggest

    repo = tmp_path / "repo"
    repo.mkdir()
    ws = pipeline.Workspace(repo / ".fb-store", tmp_path / "keys" / "fb.key", repo)
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], "A <a@example.invalid>")

    before = markdown.render_packet(ws.confirmed_findings())

    finding = ws.confirmed_findings()[0]
    for call in (suggest.suggest_severity_rationale, suggest.suggest_taxonomy):
        with pytest.raises(suggest.AiUnavailable):
            call(finding, model="")  # no model configured -> governed refusal

    after = markdown.render_packet(ws.confirmed_findings())
    assert after == before, "a failed --ai run must leave the artifacts untouched"
    assert "suggested" not in after.lower()
    assert ws.verify() == [], "and the chain is untouched too"


# --- W2c: the AI sees preview and metadata only ---


def test_safe_context_excludes_sealed_material():
    from finding_bridge.ai import suggest

    finding = json.loads((FIXTURES / "candidate_full.json").read_text(encoding="utf-8"))
    context = suggest.safe_context(finding)
    blob = json.dumps(context)
    assert "SENTINEL-PROBE" not in blob and "SENTINEL-RESPONSE" not in blob
    assert "sealed/" not in blob, "not even sealed references are sent"
    assert "provenance" not in context and "confirmed_by" not in blob
    assert "reproduction" not in context, (
        "steps are adapter-authored prose and are excluded (found by this control)"
    )
    assert context["preview"] is not None, "the preview IS what it gets"


def test_safe_context_positive_control():
    """The search can find sealed refs when they ARE present."""
    finding = json.loads((FIXTURES / "candidate_full.json").read_text(encoding="utf-8"))
    assert "sealed/" in json.dumps(finding)
