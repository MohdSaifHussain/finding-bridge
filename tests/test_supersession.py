"""W1 controls (STEP-05): the three D-052 controls plus the key split.

Every one of these is captured red before its implementation exists.
"""

import copy
import json
from pathlib import Path

import pytest

from finding_bridge import pipeline
from finding_bridge.core import provenance as prov
from finding_bridge.core import sealing

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
HITLOG = FIXTURES / "garak.synthetic.hitlog.jsonl"
IDENTITY = "Rotation Analyst <rot@example.invalid>"


@pytest.fixture()
def ws(tmp_path: Path) -> pipeline.Workspace:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = pipeline.Workspace(repo / ".fb-store", tmp_path / "k" / "fb.key", repo)
    workspace.ingest_garak(HITLOG)
    for candidate in list(workspace.list_candidates())[:2]:
        workspace.confirm(candidate["id"], IDENTITY)
    return workspace


# --- D-053: the key split ---


def test_keyring_holds_separate_ref_and_encryption_keys(tmp_path: Path):
    keyring = sealing.load_or_create_keyring(tmp_path / "k" / "fb.key", tmp_path / "repo")
    assert keyring["ref_key"] != keyring["encryption_keys"][0]
    assert len(keyring["encryption_keys"]) == 1


def test_legacy_raw_key_upgrades_preserving_refs(tmp_path: Path):
    """A pre-split raw Fernet key file upgrades in place, and the ref key
    it derives is the SAME one that produced existing refs, so no stored
    reference breaks."""
    import hashlib

    from cryptography.fernet import Fernet

    path = tmp_path / "k" / "fb.key"
    path.parent.mkdir(parents=True)
    legacy = Fernet.generate_key()
    path.write_bytes(legacy)
    keyring = sealing.load_or_create_keyring(path, tmp_path / "repo")
    expected_ref = hashlib.sha256(sealing.REF_KEY_DOMAIN + legacy).digest()
    assert keyring["ref_key_bytes"] == expected_ref
    assert keyring["encryption_keys"][0].encode() == legacy


# --- D-055: canonical form version in the head ---


def test_head_declares_canonical_form(ws: pipeline.Workspace):
    head = prov.chain_head(ws.confirmed_findings())
    assert head["canonical_form"] == prov.CANONICAL_FORM_V1
    assert prov.chain_head_internal_ok(head)


# --- D-052 control 1: a rotation verifies clean across the join ---


def test_rotation_verifies_clean_across_the_join(ws: pipeline.Workspace):
    assert ws.verify() == []
    result = ws.rotate_key(IDENTITY, reason="scheduled rotation")
    assert result["event_type"] == "key-rotation"
    assert result["remap"] == {}, "with the D-053 split, rotation remaps nothing"
    assert ws.verify() == [], "the chain must verify THROUGH the supersession record"
    # and the sealed content is still readable under the new key
    ref = ws.confirmed_findings()[0]["raw_response_sealed"]
    assert "SENTINEL-HARM" in ws.store.unseal(ref, IDENTITY, explicit=True)


def test_rotation_changes_the_encryption_key_but_not_identity(ws: pipeline.Workspace):
    before_ids = [f["id"] for f in ws.confirmed_findings()]
    before_key = ws.keyring["encryption_keys"][0]
    ws.rotate_key(IDENTITY, reason="scheduled rotation")
    after = [f for f in ws.confirmed_findings() if f.get("record_type") != "supersession"]
    assert [f["id"] for f in after] == before_ids, "ids must survive rotation (D-053)"
    assert ws.keyring["encryption_keys"][0] != before_key, "the encryption key must change"


# --- D-052 control 2: a forged supersession record fails ---


def test_forged_supersession_fails(ws: pipeline.Workspace):
    ws.rotate_key(IDENTITY, reason="scheduled rotation")
    ledger = ws.confirmed_findings()
    ledger[-1]["reason"] = "forged reason, attestation not recomputed"
    codes = {f["reason_code"] for f in prov.verify_chain(ledger)}
    assert prov.REASON_ATTESTATION_TAMPERED in codes


def test_supersession_with_wrong_old_head_fails(ws: pipeline.Workspace):
    """A record whose old_head does not match the chain it claims to
    supersede must fail, even with a correctly recomputed attestation."""
    ws.rotate_key(IDENTITY, reason="scheduled rotation")
    ledger = ws.confirmed_findings()
    record = ledger[-1]
    record["old_head"] = dict(record["old_head"], count=99)
    record["provenance"]["attestation_hash"] = prov.supersession_attestation(record)
    codes = {f["reason_code"] for f in prov.verify_chain(ledger)}
    assert prov.REASON_SUPERSESSION_INVALID in codes


# --- D-052 control 3: a claimed-but-unperformed remap fails ---


def test_claimed_but_unperformed_remap_fails(ws: pipeline.Workspace):
    ws.rotate_key(IDENTITY, reason="scheduled rotation")
    ledger = ws.confirmed_findings()
    record = ledger[-1]
    record["remap"] = {"fb-0000000000000000": "fb-1111111111111111"}
    record["provenance"]["attestation_hash"] = prov.supersession_attestation(record)
    failures = prov.verify_chain(ledger)
    codes = {f["reason_code"] for f in failures}
    assert prov.REASON_SUPERSESSION_INVALID in codes
    detail = " ".join(f["detail"] for f in failures)
    assert "remap" in detail


# --- the supersession record itself ---


def test_supersession_record_validates_against_its_schema(ws: pipeline.Workspace):
    from finding_bridge.core.schema import validate_record

    ws.rotate_key(IDENTITY, reason="scheduled rotation")
    for record in ws.confirmed_findings():
        validate_record(record)


def test_rotation_requires_an_identity(ws: pipeline.Workspace):
    with pytest.raises(prov.ProvenanceError) as err:
        ws.rotate_key("   ", reason="no identity")
    assert err.value.reason_code == prov.REASON_UNCONFIRMED


def test_supersession_is_the_only_rotation_path(ws: pipeline.Workspace):
    """W1e: rotation is reachable ONLY as a supersession event. The store
    exposes no key-swap that skips the ledger."""
    forbidden = [n for n in dir(ws.store) if "rotate" in n.lower()]
    assert forbidden == [], f"sealed store must expose no rotation path: {forbidden}"


def test_findings_carry_record_type(ws: pipeline.Workspace):
    for finding in ws.confirmed_findings():
        assert finding["record_type"] in ("finding", "supersession")


def test_ledger_after_rotation_keeps_one_unbroken_chain(ws: pipeline.Workspace):
    ws.rotate_key(IDENTITY, reason="scheduled rotation")
    ledger = ws.confirmed_findings()
    for i, record in enumerate(ledger):
        if i == 0:
            assert record["provenance"]["prev_hash"] is None
        else:
            assert (
                record["provenance"]["prev_hash"] == ledger[i - 1]["provenance"]["content_hash"]
            ), "the chain links through the supersession record, not around it"


def test_ingest_after_rotation_still_works(ws: pipeline.Workspace):
    ws.rotate_key(IDENTITY, reason="scheduled rotation")
    summary = ws.ingest_garak(HITLOG)
    assert summary["ingested"] == 3
    remaining = ws.list_candidates()
    ws.confirm(remaining[0]["id"], IDENTITY)
    assert ws.verify() == [], "new findings chain onto the post-rotation epoch"


def test_supersession_json_shape_is_stable(ws: pipeline.Workspace):
    ws.rotate_key(IDENTITY, reason="scheduled rotation")
    record = ws.confirmed_findings()[-1]
    assert set(record) >= {
        "record_type",
        "event_type",
        "old_head",
        "new_head",
        "remap",
        "canonical_form_from",
        "canonical_form_to",
        "reason",
        "provenance",
    }
    assert json.dumps(record)  # serializable
    assert copy.deepcopy(record) == record
