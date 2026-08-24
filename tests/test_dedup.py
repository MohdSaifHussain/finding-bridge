"""D5 tests: exact content-hash dedup with positive and negative controls."""

import copy
import json
from pathlib import Path

import pytest

from finding_bridge.core import dedup
from finding_bridge.core import provenance as prov

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


@pytest.fixture()
def base() -> dict:
    return json.loads((FIXTURES / "candidate_null_fields.json").read_text(encoding="utf-8"))


def variant(base: dict, *, preview: str | None = None, discovered_at: str | None = None) -> dict:
    v = copy.deepcopy(base)
    if preview is not None:
        v["preview"] = preview
    if discovered_at is not None:
        v["discovered_at"] = discovered_at
    return v


def test_same_content_different_time_is_duplicate(base):
    a = prov.stamp(variant(base, discovered_at="2026-08-24T10:00:00+00:00"))
    b = prov.stamp(variant(base, discovered_at="2026-08-24T11:00:00+00:00"))
    marked = dedup.mark_duplicates([a, b])
    assert marked[0]["dedup"]["duplicate_of"] is None
    assert marked[1]["dedup"]["duplicate_of"] == marked[0]["id"]
    assert marked[0]["dedup"]["cluster_id"] == marked[1]["dedup"]["cluster_id"]
    assert marked[0]["dedup"]["cluster_id"] is not None


def test_different_content_not_duplicate(base):
    a = prov.stamp(variant(base, preview="one"))
    b = prov.stamp(variant(base, preview="two"))
    marked = dedup.mark_duplicates([a, b])
    assert all(f["dedup"]["duplicate_of"] is None for f in marked)
    assert all(f["dedup"]["cluster_id"] is None for f in marked)


def test_inputs_not_mutated(base):
    a = prov.stamp(base)
    snapshot = copy.deepcopy(a)
    dedup.mark_duplicates([a, a])
    assert a == snapshot


def test_order_preserved_and_first_is_canonical(base):
    findings = [
        prov.stamp(variant(base, preview="x", discovered_at=f"2026-08-24T1{i}:00:00+00:00"))
        for i in range(3)
    ]
    marked = dedup.mark_duplicates(findings)
    assert marked[0]["dedup"]["duplicate_of"] is None
    assert marked[1]["dedup"]["duplicate_of"] == marked[0]["id"]
    assert marked[2]["dedup"]["duplicate_of"] == marked[0]["id"]


def test_unique_findings_drops_duplicates_only(base):
    dup1 = prov.stamp(variant(base, discovered_at="2026-08-24T10:00:00+00:00"))
    dup2 = prov.stamp(variant(base, discovered_at="2026-08-24T11:00:00+00:00"))
    other = prov.stamp(variant(base, preview="distinct"))
    uniques = dedup.unique_findings([dup1, dup2, other])
    assert [f["preview"] for f in uniques] == [dup1["preview"], "distinct"]


def test_marking_does_not_break_provenance_chain(base):
    a = prov.stamp(variant(base, discovered_at="2026-08-24T10:00:00+00:00"))
    b = prov.stamp(
        variant(base, discovered_at="2026-08-24T11:00:00+00:00"),
        prev_hash=a["provenance"]["content_hash"],
    )
    marked = dedup.mark_duplicates([a, b])
    assert prov.verify_chain(marked) == []


def test_unstamped_input_refused(base):
    """R-8: a finding without an id would make canonical_ids[key] None and
    every duplicate in the group silently canonical. (First version of this
    test passed the fixture unmodified, which carries an id, so it did not
    model unstamped input at all and failed to raise.)"""
    unstamped = copy.deepcopy(base)
    del unstamped["id"]
    with pytest.raises(dedup.DedupError) as err:
        dedup.mark_duplicates([unstamped, copy.deepcopy(unstamped)])
    assert err.value.reason_code == "unstamped-finding"


def test_none_id_input_refused(base):
    nulled = copy.deepcopy(base)
    nulled["id"] = None
    with pytest.raises(dedup.DedupError) as err:
        dedup.mark_duplicates([nulled])
    assert err.value.reason_code == "unstamped-finding"


def test_environment_difference_does_not_defeat_dedup(base):
    """Finding A principle (D-025): the dedup key asks 'have we seen this
    finding before' and excludes reproduction.environment; the content hash
    asks 'has this record changed' and keeps it."""
    a = copy.deepcopy(base)
    b = copy.deepcopy(base)
    a["reproduction"]["environment"] = {"attempt_id": "one"}
    b["reproduction"]["environment"] = {"attempt_id": "two"}
    sa, sb = prov.stamp(a), prov.stamp(b)
    marked = dedup.mark_duplicates([sa, sb])
    assert marked[1]["dedup"]["duplicate_of"] == marked[0]["id"]
    assert marked[0]["dedup"]["cluster_id"] is not None
    assert prov.content_hash(sa) != prov.content_hash(sb), "content hash still sees the change"


# --- close-audit kill tests (STEP-02; red demonstrated by the mutation run) ---


def test_cluster_id_format_is_cl_plus_16_hex(base):
    """Kills dedup L21 NumberReplacers: the documented cluster-id format is
    cl- plus exactly 16 hex chars; nothing previously pinned the length."""
    import re

    a = prov.stamp(variant(base, discovered_at="2026-08-24T10:00:00+00:00"))
    b = prov.stamp(variant(base, discovered_at="2026-08-24T11:00:00+00:00"))
    marked = dedup.mark_duplicates([a, b])
    assert re.fullmatch(r"cl-[0-9a-f]{16}", marked[0]["dedup"]["cluster_id"])


def test_steps_difference_prevents_duplicate(base):
    """Kills dedup L50 NotEq->Lt: under the mutant, 'steps' (which sorts
    after 'environment') is dropped from the dedup key, so findings
    differing ONLY in reproduction steps would silently merge - evidence
    the dedup key must keep. The NotEq->Gt variant is domain-equivalent:
    the schema pins reproduction's keys to exactly steps and environment
    (additionalProperties false), and the drift test guards that."""
    a = copy.deepcopy(base)
    b = copy.deepcopy(base)
    b["reproduction"]["steps"] = ["a genuinely different reproduction step"]
    marked = dedup.mark_duplicates([prov.stamp(a), prov.stamp(b)])
    assert marked[1]["dedup"]["duplicate_of"] is None
    assert marked[1]["dedup"]["cluster_id"] is None
