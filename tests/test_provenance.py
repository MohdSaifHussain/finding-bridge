"""D3 tests: hashing, stamping, confirmation, chain verification.

Every failure mode has a negative control and every check a positive control
(skill rule 5)."""

import copy
import json
from pathlib import Path

import pytest

from finding_bridge.core import provenance as prov

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture()
def finding() -> dict:
    return load_fixture("candidate_null_fields.json")


def make_chain(finding: dict, n: int = 3) -> list[dict]:
    chain: list[dict] = []
    prev = None
    for i in range(n):
        candidate = copy.deepcopy(finding)
        candidate["preview"] = f"synthetic preview {i}"
        stamped = prov.stamp(candidate, prev_hash=prev)
        chain.append(stamped)
        prev = stamped["provenance"]["content_hash"]
    return chain


# --- hashing and stamping ---


def test_hash_is_deterministic(finding):
    assert prov.content_hash(finding) == prov.content_hash(copy.deepcopy(finding))


def test_hash_exclusions_are_covered_by_other_guards(finding):
    """content_hash excludes id/provenance/dedup BY DESIGN (circularity and
    triage state), but per review R-1 that exclusion is only safe because a
    second guard covers each excluded field: id via id-mismatch, dedup by
    being non-evidence, and the gate record via the attestation hash. This
    test asserts the pair, not the exclusion alone."""
    before = prov.content_hash(finding)
    changed = copy.deepcopy(finding)
    changed["id"] = "fb-other"
    changed["provenance"]["confirmed_by"] = "someone"
    changed["dedup"]["cluster_id"] = "c1"
    assert prov.content_hash(changed) == before
    stamped = prov.stamp(finding)
    stamped["id"] = "fb-other"
    assert prov.REASON_ID_MISMATCH in {f["reason_code"] for f in prov.verify_chain([stamped])}
    confirmed = prov.confirm(prov.stamp(finding), "A <a@example.invalid>")
    confirmed["provenance"]["confirmed_by"] = "someone else"
    assert prov.REASON_ATTESTATION_TAMPERED in {
        f["reason_code"] for f in prov.verify_chain([confirmed])
    }


def test_hash_changes_on_content_change(finding):
    changed = copy.deepcopy(finding)
    changed["preview"] = "different"
    assert prov.content_hash(changed) != prov.content_hash(finding)


def test_stamp_sets_id_and_hash_without_mutating_input(finding):
    original = copy.deepcopy(finding)
    stamped = prov.stamp(finding)
    assert finding == original, "stamp must not mutate its input"
    digest = stamped["provenance"]["content_hash"]
    assert stamped["id"] == "fb-" + digest[:16]
    assert len(digest) == 64


def test_confirm_sets_identity(finding):
    confirmed = prov.confirm(prov.stamp(finding), "Fixture Human <fixture@example.invalid>")
    assert confirmed["provenance"]["confirmed_by"].startswith("Fixture Human")
    assert confirmed["provenance"]["confirmed_at"] is not None


def test_confirm_refuses_empty_identity(finding):
    with pytest.raises(prov.ProvenanceError) as err:
        prov.confirm(prov.stamp(finding), "  ")
    assert err.value.reason_code == prov.REASON_UNCONFIRMED


# --- chain verification: positive control ---


def test_valid_chain_verifies(finding):
    assert prov.verify_chain(make_chain(finding)) == []


# --- chain verification: negative controls, one per reason code ---


def test_content_tamper_detected(finding):
    chain = make_chain(finding)
    chain[1]["preview"] = "tampered after stamping"
    codes = {f["reason_code"] for f in prov.verify_chain(chain)}
    assert prov.REASON_CONTENT_TAMPERED in codes


def test_recomputed_tamper_breaks_chain(finding):
    """Tamperer edits content AND recomputes the hash: linkage catches it."""
    chain = make_chain(finding)
    chain[1]["preview"] = "tampered and rehashed"
    digest = prov.content_hash(chain[1])
    chain[1]["provenance"]["content_hash"] = digest
    chain[1]["id"] = prov.derive_id(digest)
    failures = prov.verify_chain(chain)
    assert [f["reason_code"] for f in failures] == [prov.REASON_CHAIN_BROKEN]
    assert failures[0]["index"] == 2


def test_id_tamper_detected(finding):
    chain = make_chain(finding)
    chain[0]["id"] = "fb-0000000000000000"
    codes = {f["reason_code"] for f in prov.verify_chain(chain)}
    assert prov.REASON_ID_MISMATCH in codes


def test_nonnull_first_prev_hash_detected(finding):
    chain = make_chain(finding)
    chain[0]["provenance"]["prev_hash"] = "0" * 64
    codes = {f["reason_code"] for f in prov.verify_chain(chain)}
    assert prov.REASON_CHAIN_BROKEN in codes


def test_stamped_fixture_still_validates_against_schema(finding):
    from jsonschema import Draft202012Validator

    schema = json.loads((FIXTURES.parent / "finding.schema.json").read_text(encoding="utf-8"))
    stamped = prov.stamp(finding)
    Draft202012Validator(schema).validate(stamped)


# --- R-1: the human-gate record itself is tamper-evident ---


def test_confirmed_by_tamper_detected(finding):
    chain = make_chain(finding)
    chain[1] = prov.confirm(chain[1], "Real Analyst <real@example.invalid>")
    chain[1]["provenance"]["confirmed_by"] = "Forged Analyst <forged@example.invalid>"
    codes = {f["reason_code"] for f in prov.verify_chain(chain)}
    assert "attestation-tampered" in codes


def test_confirmed_at_tamper_detected(finding):
    chain = make_chain(finding)
    chain[1] = prov.confirm(chain[1], "Real Analyst <real@example.invalid>")
    chain[1]["provenance"]["confirmed_at"] = "1999-01-01T00:00:00+00:00"
    codes = {f["reason_code"] for f in prov.verify_chain(chain)}
    assert "attestation-tampered" in codes


def test_confirmation_without_attestation_detected(finding):
    chain = make_chain(finding)
    chain[1]["provenance"]["confirmed_by"] = "Injected <i@example.invalid>"
    chain[1]["provenance"]["confirmed_at"] = "2026-08-24T13:00:00+00:00"
    codes = {f["reason_code"] for f in prov.verify_chain(chain)}
    assert "attestation-missing" in codes


def test_spurious_attestation_on_unconfirmed_detected(finding):
    chain = make_chain(finding)
    chain[0]["provenance"]["attestation_hash"] = "a" * 64
    codes = {f["reason_code"] for f in prov.verify_chain(chain)}
    assert "attestation-spurious" in codes


def test_confirmed_chain_verifies_clean(finding):
    """Positive control: a properly confirmed chain still verifies."""
    chain = make_chain(finding)
    chain[1] = prov.confirm(chain[1], "Real Analyst <real@example.invalid>")
    assert prov.verify_chain(chain) == []


def test_confirm_refuses_tampered_content(finding):
    stamped = prov.stamp(finding)
    stamped["preview"] = "edited after stamping"
    with pytest.raises(prov.ProvenanceError) as err:
        prov.confirm(stamped, "Analyst <a@example.invalid>")
    assert err.value.reason_code == "content-tampered"


def test_confirm_refuses_double_confirm(finding):
    confirmed = prov.confirm(prov.stamp(finding), "A <a@example.invalid>")
    with pytest.raises(prov.ProvenanceError) as err:
        prov.confirm(confirmed, "B <b@example.invalid>")
    assert err.value.reason_code == "already-confirmed"


def test_stamp_refuses_confirmed_finding(finding):
    confirmed = prov.confirm(prov.stamp(finding), "A <a@example.invalid>")
    with pytest.raises(prov.ProvenanceError) as err:
        prov.stamp(confirmed)
    assert err.value.reason_code == "restamp-confirmed"
