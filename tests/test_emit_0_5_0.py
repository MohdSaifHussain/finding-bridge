"""Schema 0.5.0 on the EMIT side: every emitter honours taxonomy.atlas and
remediation, and none crashes on a record that carries them.

Captured red before the fix: emit-sarif raised KeyError 'atlas' on a
record with an ATLAS claim, because TAXONOMY_NAMES named two families.
The suite had passed because nothing emitted such a record: the schema
grew and no emitter test grew with it. This file is that test.
"""

import json
from pathlib import Path

from finding_bridge.adapters.out import flare_ai, markdown, sarif, tracker
from finding_bridge.core import provenance as prov

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


def _confirmed_full() -> dict:
    f = json.loads((FIXTURES / "candidate_full.json").read_text(encoding="utf-8"))
    if f["provenance"]["confirmed_by"] is None:
        f = prov.confirm(prov.stamp(f), "T <t@x.invalid>")
    return f


def test_sarif_carries_atlas_taxonomy_and_a_fix_for_remediation():
    f = _confirmed_full()
    log = sarif.render_sarif([f], "f.jsonl")
    run = log["runs"][0]
    names = [t["name"] for t in run["taxonomies"]]
    assert "MITRE ATLAS" in names
    result = run["results"][0]
    assert any(t["id"] == "AML.T0051" for t in result["taxa"])
    assert result["fixes"][0]["description"]["text"] == f["remediation"]


def test_sarif_omits_fixes_when_remediation_is_null():
    f = _confirmed_full()
    f["remediation"] = None
    result = sarif.render_sarif([f], "f.jsonl")["runs"][0]["results"][0]
    assert "fixes" not in result


def test_flare_carries_atlas_in_classification_and_proposed_mitigation():
    f = _confirmed_full()
    text = json.dumps(flare_ai.render_reports([f]))
    assert "AML.T0051" in text
    assert "flare:proposedMitigation" in text


def test_markdown_and_tracker_carry_remediation_only_when_written():
    f = _confirmed_full()
    assert f["remediation"] in markdown.render_packet([f])
    assert tracker.render_issues([f])[0]["fields"]["remediation"] == f["remediation"]
    f["remediation"] = None
    assert "Remediation" not in markdown.render_packet([f])
    assert tracker.render_issues([f])[0]["fields"]["remediation"] is None
