"""F-2 (STEP-06 stop one, ruled FIX FULL, D-070): every emitter works on a
ledger that holds a supersession record.

Escape record, direction named: the STEP-05 close ritual rotated and
verified but never emitted after rotating, so all four emitters were
certified against a store shape the rotation feature immediately
invalidates. Found by examples/03-rotation-drill, a documentation
exercise, not by the suite or either ritual. Each control below was
captured RED (KeyError traceback for markdown, sarif and flare) before
the shared filter existed; tracker passed by its own skip, which now is
a second layer over the shared one, not the only one.
"""

from pathlib import Path

import pytest

from finding_bridge import cli, pipeline

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


def _rotated(tmp_path: Path) -> list[str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    store, key = repo / ".fb-store", tmp_path / "k" / "fb.key"
    ws = pipeline.Workspace(store, key, repo)
    ws.ingest_garak(FIXTURES / "garak.synthetic.hitlog.jsonl")
    ws.confirm(ws.list_candidates()[0]["id"], "T <t@x.invalid>")
    ws.rotate_key("T <t@x.invalid>", "test rotation")
    raw = pipeline._read_jsonl(ws.ledger_path)
    assert any(r.get("record_type") == "supersession" for r in raw), "control precondition"
    return ["--store", str(store), "--key", str(key)]


@pytest.mark.parametrize(
    "command, out_name",
    [
        ("emit-markdown", "packet.md"),
        ("emit-sarif", "findings.sarif"),
        ("emit-flare", "findings.flare.json"),
        ("emit-tracker", "findings.tracker.json"),
    ],
)
def test_emitter_after_rotation_emits_findings_only(tmp_path, command, out_name, capsys):
    args = _rotated(tmp_path)
    out = tmp_path / "out" / out_name
    rc = cli.main([*args, command, str(out)])
    err = capsys.readouterr().err
    assert rc == 0, err
    text = out.read_text(encoding="utf-8")
    assert "supersession" not in text.lower() or command == "emit-flare"
    assert out.exists()


def test_confirmed_findings_filters_supersession_records_once(tmp_path):
    """The shared filter is the mechanism (D-070): the ledger keeps the
    record, the emit-facing reader drops it, and verify still sees it."""
    args = _rotated(tmp_path)
    ws = pipeline.Workspace(Path(args[1]), Path(args[3]), tmp_path / "repo")
    findings = ws.confirmed_findings()
    assert findings and all(f.get("record_type") == "finding" for f in findings)
    assert len(pipeline._read_jsonl(ws.ledger_path)) == len(findings) + 1
    assert ws.verify() == []
