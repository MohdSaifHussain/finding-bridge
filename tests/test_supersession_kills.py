"""Kill tests for W1's mutation survivors (STEP-05 stop one).

The headline: the NEW supersession verification code reproduced the exact
comparison-weakening class the STEP-03 and STEP-04 evals both flagged.
Writing fresh verify code re-created the gap rather than inheriting the
fix, because the fix lived in tests, not in a habit. Named as a repeat.
"""

import copy
import json
from pathlib import Path

import pytest

from finding_bridge import pipeline
from finding_bridge.core import provenance as prov
from finding_bridge.core import sealing
from finding_bridge.core.schema import SchemaValidationError, validate_record

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
HITLOG = FIXTURES / "garak.synthetic.hitlog.jsonl"
IDENTITY = "Kill Analyst <kill@example.invalid>"


@pytest.fixture()
def rotated(tmp_path: Path) -> pipeline.Workspace:
    repo = tmp_path / "repo"
    repo.mkdir()
    ws = pipeline.Workspace(repo / ".fb-store", tmp_path / "k" / "fb.key", repo)
    ws.ingest_garak(HITLOG)
    ws.confirm(ws.list_candidates()[0]["id"], IDENTITY)
    ws.rotate_key(IDENTITY, reason="kill-test rotation")
    return ws


def _both_orderings(real: str) -> list[str]:
    """A forged hash below and above the real one, so a weakened
    comparison cannot pass by ordering luck."""
    return ["0" * 64, "f" * 64] if real > "0" * 64 else ["f" * 64, "0" * 64]


# --- the repeat class: comparison weakening in the NEW verify paths ---


def test_supersession_content_tamper_detected_both_orderings(rotated):
    """Kills provenance L279 ('!=' weakened): the supersession record's own
    content hash, checked in both hash orderings."""
    ledger = rotated.confirmed_findings()
    for forged in ("0" * 64, "f" * 64):
        chain = copy.deepcopy(ledger)
        chain[-1]["provenance"]["content_hash"] = forged
        codes = {f["reason_code"] for f in prov.verify_chain(chain)}
        assert prov.REASON_CONTENT_TAMPERED in codes


def test_supersession_prev_hash_break_detected_both_orderings(rotated):
    """Kills provenance L291 ('!=' weakened): the join's own chain link."""
    ledger = rotated.confirmed_findings()
    for forged in ("0" * 64, "f" * 64):
        chain = copy.deepcopy(ledger)
        chain[-1]["provenance"]["prev_hash"] = forged
        codes = {f["reason_code"] for f in prov.verify_chain(chain)}
        assert prov.REASON_CHAIN_BROKEN in codes


def test_supersession_attestation_detected_both_orderings(rotated):
    """Kills provenance L452 ('!=' weakened): the attestation comparison,
    the third occurrence of this class in this project."""
    ledger = rotated.confirmed_findings()
    for forged in ("0" * 64, "f" * 64):
        chain = copy.deepcopy(ledger)
        chain[-1]["provenance"]["attestation_hash"] = forged
        codes = {f["reason_code"] for f in prov.verify_chain(chain)}
        assert prov.REASON_ATTESTATION_TAMPERED in codes


def test_old_head_describes_a_different_chain_and_is_caught(rotated):
    """Kills provenance L472 ('!=' weakened): old_head's comparison against
    the epoch it actually closes.

    THE FIRST VERSION OF THIS TEST PASSED FOR THE WRONG REASON. It forged
    old_head by editing `count` and leaving head_hash inconsistent, so the
    INTERNAL-consistency check rejected it and the comparison this test
    names was never reached. The mutation audit proved that by leaving the
    mutant alive under a green test. Fixed: build an old_head that is
    internally VALID but describes a different chain, so the comparison is
    the only thing that can catch it."""
    ledger = rotated.confirmed_findings()
    chain = copy.deepcopy(ledger)
    record = chain[-1]
    wrong_but_valid = prov.chain_head([])  # self-consistent, wrong chain
    assert prov.chain_head_internal_ok(wrong_but_valid), "the decoy must be self-consistent"
    record["old_head"] = wrong_but_valid
    record["provenance"]["attestation_hash"] = prov.supersession_attestation(record)
    record["provenance"]["content_hash"] = prov.content_hash(record)
    failures = prov.verify_chain(chain)
    assert prov.REASON_SUPERSESSION_INVALID in {f["reason_code"] for f in failures}
    detail = " ".join(f["detail"] for f in failures)
    assert "epoch it closes" in detail, "the comparison, not the internal check, must fire"


def test_epoch_start_advances_across_two_rotations(rotated):
    """Kills provenance L269 (`epoch_start = i + 1`, 13 arithmetic mutants):
    with TWO supersessions, the second's old_head covers only ITS epoch, so
    a wrong epoch_start verifies the second join against the wrong range."""
    rotated.ingest_garak(HITLOG)
    rotated.confirm(rotated.list_candidates()[0]["id"], IDENTITY)
    rotated.rotate_key(IDENTITY, reason="second rotation")
    ledger = rotated.confirmed_findings()
    assert [r["record_type"] for r in ledger].count("supersession") == 2
    assert prov.verify_chain(ledger) == [], "two joins must both verify"
    assert ledger[-1]["old_head"]["count"] == len(ledger) - 1


def test_remap_pointing_backwards_is_not_accepted(rotated):
    """Kills provenance L495 (`records[i + 1:]`, 12 slice mutants): an id
    that exists BEFORE the join does not satisfy a remap claiming to have
    produced it after."""
    ledger = rotated.confirmed_findings()
    chain = copy.deepcopy(ledger)
    record = chain[-1]
    existing_before = [r["id"] for r in chain if r.get("record_type") == "finding"][0]
    record["remap"] = {"fb-0000000000000000": existing_before}
    record["provenance"]["attestation_hash"] = prov.supersession_attestation(record)
    record["provenance"]["content_hash"] = prov.content_hash(record)
    codes = {f["reason_code"] for f in prov.verify_chain(chain)}
    assert prov.REASON_SUPERSESSION_INVALID in codes


# --- the record_type dispatch (provenance L267/L276, schema L95) ---


def test_supersession_is_not_verified_as_a_finding(rotated):
    """Kills the dispatch comparisons: a supersession record must NOT be
    run through the finding checks (it has no id and no dedup, so treating
    it as a finding would produce id-mismatch noise) and a finding must
    never be run through the supersession checks."""
    ledger = rotated.confirmed_findings()
    assert prov.verify_chain(ledger) == []
    supersession = [r for r in ledger if r["record_type"] == "supersession"]
    assert len(supersession) == 1
    assert "id" not in supersession[0], "a supersession has no finding id"


def test_validate_record_routes_each_kind_to_its_own_schema(rotated):
    """Kills schema L95: both kinds validate, and a finding shaped like a
    supersession (or vice versa) refuses."""
    for record in rotated.confirmed_findings():
        validate_record(record)
    finding = [r for r in rotated.confirmed_findings() if r["record_type"] == "finding"][0]
    mislabeled = dict(finding, record_type="supersession")
    with pytest.raises(SchemaValidationError):
        validate_record(mislabeled)
    supersession = [r for r in rotated.confirmed_findings() if r["record_type"] == "supersession"][
        0
    ]
    with pytest.raises(SchemaValidationError):
        validate_record(dict(supersession, record_type="finding"))


def test_unknown_record_type_refuses(rotated):
    with pytest.raises(SchemaValidationError):
        validate_record({"record_type": "invented-kind"})


# --- sealing: the keyring and the re-encryption counter ---


def test_reencrypt_all_reports_how_many_blobs_it_touched(tmp_path: Path):
    """Kills sealing L259/L262 (the counter): the count is a reported fact,
    so it is asserted rather than assumed."""
    keyring = sealing.load_or_create_keyring(tmp_path / "k" / "fb.key", tmp_path / "repo")
    store = sealing.SealedStore(tmp_path / "s", keyring)
    store.seal("SENTINEL-A synthetic")
    store.seal("SENTINEL-B synthetic")
    assert store.reencrypt_all() == 2


def test_keyring_file_never_contains_the_derived_ref_key_bytes(tmp_path: Path):
    """Kills sealing L125: ref_key_bytes is a runtime convenience and must
    never be written to disk (it would duplicate key material in a second
    encoding)."""
    path = tmp_path / "k" / "fb.key"
    sealing.load_or_create_keyring(path, tmp_path / "repo")
    written = json.loads(path.read_text(encoding="utf-8"))
    assert "ref_key_bytes" not in written
    assert set(written) == {"keyring_version", "ref_key", "encryption_keys"}
    assert written["keyring_version"] == sealing.KEYRING_VERSION


def test_keyring_survives_a_reload_after_rotation(rotated):
    """The rotated keyring is what the next run loads: a rotation that did
    not persist would be silently undone on restart."""
    reloaded = sealing.load_or_create_keyring(rotated.key_path, rotated.repo_root)
    assert reloaded["encryption_keys"] == rotated.keyring["encryption_keys"]
    assert reloaded["ref_key"] == rotated.keyring["ref_key"]
