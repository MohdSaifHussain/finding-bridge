"""Kill tests for surviving mutants from the first AUDIT run (D-027).

Each test names the mutant class it kills (file:line, operator) from
evidence/mutation-audit-step02.md. Golden vectors pin the canonical form
(with non-ASCII content, so ensure_ascii mutations change the bytes); they
also make DEV-2 canonical-form drift loud, which is deliberate.
"""

import copy
import json
import re
from pathlib import Path

import pytest

from finding_bridge.core import provenance as prov
from finding_bridge.core import sealing

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
BASE = json.loads((FIXTURES / "candidate_null_fields.json").read_text(encoding="utf-8"))


# --- kills: ensure_ascii=False mutants (provenance L59, L77, L86, L162) ---


def test_canonical_form_golden_vectors():
    """Pinned vectors with non-ASCII content. If the canonical serialization
    ever changes, these fail and force a ruled decision, never silent drift.

    Re-pinned at RFC 8785 adoption (DEV-6 condition 3) and verified
    UNCHANGED: on this value space (ASCII keys, raw-UTF-8 values, ints,
    null) the old Python form and JCS are byte-identical; the DEV-2
    divergences lived only in exotic-key sorting and float round-trip,
    both now resolved to the standard (see test_jcs_vectors.py)."""
    f = {"preview": "café 中\U0001f600", "source_tool": "garak"}
    assert (
        prov.content_hash(f) == "8902f3924dbdfbca689d030ecf914910fb56a69da21a9b154ec2b83fb22485e3"
    )
    assert (
        prov.attestation_hash("a" * 64, "Anaé <a@x.invalid>", "2026-08-24T00:00:00+00:00")
        == "e539a536ca9174f5302b64bcb29b036ae7de69f02e3b8451a48ad28b5fea67ed"
    )
    chain = [prov.stamp({"preview": "café"})]
    head = prov.chain_head(chain)
    assert head["last_content_hash"] == (
        "7c07f826f564b77187b9ae4b86da74c341edd98c5444d0dd63767e1b49bcb36c"
    )
    # RE-PINNED at STEP-05 W1b (D-055): the head payload gained the
    # canonical form version, so head_hash moved and ONLY head_hash moved.
    # content_hash, the attestation and last_content_hash above are
    # byte-identical to their pre-change values, which is the evidence that
    # the change was scoped exactly to the head. The goldens made the move
    # loud, which is what they are for.
    assert head["head_hash"] == ("10cc0e928cc874e5d3e1e2560ac09f39fe5f7cbcf9acd37a8e84a93f76c36446")
    assert head["canonical_form"] == prov.CANONICAL_FORM_V1
    assert prov.chain_head_internal_ok(head)
    assert b"caf\xc3\xa9" in prov.canonical_content_bytes(f), "raw UTF-8, not \\u escapes"


# --- kills: comparison-weakening mutants need BOTH hash orderings ---
# (provenance L129/L250 != -> >, L278 != -> >, L80 == -> >=)


def tampers_in_both_orderings(stamped: dict) -> tuple[dict, dict]:
    """Two tampered copies: one where recomputed < stored hash, one where
    recomputed > stored, found deterministically, so a weakened comparison
    cannot pass by hash-ordering luck."""
    stored = stamped["provenance"]["content_hash"]
    below = above = None
    i = 0
    while below is None or above is None:
        candidate = copy.deepcopy(stamped)
        candidate["preview"] = f"tamper-{i}"
        recomputed = prov.content_hash(candidate)
        if recomputed < stored and below is None:
            below = candidate
        if recomputed > stored and above is None:
            above = candidate
        i += 1
    return below, above


def test_content_tamper_detected_in_both_hash_orderings():
    stamped = prov.stamp(copy.deepcopy(BASE))
    for tampered in tampers_in_both_orderings(stamped):
        codes = {f["reason_code"] for f in prov.verify_chain([tampered])}
        assert prov.REASON_CONTENT_TAMPERED in codes


def test_confirm_refuses_tamper_in_both_hash_orderings():
    stamped = prov.stamp(copy.deepcopy(BASE))
    for tampered in tampers_in_both_orderings(stamped):
        with pytest.raises(prov.ProvenanceError) as err:
            prov.confirm(tampered, "A <a@x.invalid>")
        assert err.value.reason_code == prov.REASON_CONTENT_TAMPERED


def test_prev_hash_mismatch_detected_in_both_orderings():
    first = prov.stamp(copy.deepcopy(BASE))
    second = copy.deepcopy(BASE)
    second["preview"] = "second"
    linked = prov.stamp(second, prev_hash=first["provenance"]["content_hash"])
    for forged in ("0" * 64, "f" * 64):
        broken = copy.deepcopy(linked)
        broken["provenance"]["prev_hash"] = forged
        codes = {f["reason_code"] for f in prov.verify_chain([first, broken])}
        assert prov.REASON_CHAIN_BROKEN in codes


def test_head_internal_check_rejects_both_orderings():
    chain = [prov.stamp(copy.deepcopy(BASE))]
    head = prov.chain_head(chain)
    for forged in ("0" * 64, "f" * 64):
        bad = dict(head, head_hash=forged)
        codes = [f["reason_code"] for f in prov.verify_chain(chain, expected_head=bad)]
        assert codes == [prov.REASON_HEAD_TAMPERED]


# --- kills: NumberReplacer on the reported index (provenance L271) ---


def test_first_record_prev_violation_reports_index_zero():
    stamped = prov.stamp(copy.deepcopy(BASE))
    stamped["provenance"]["prev_hash"] = "0" * 64
    failures = prov.verify_chain([stamped])
    assert failures[0]["index"] == 0


# --- sealing kills ---


@pytest.fixture()
def store(tmp_path: Path) -> sealing.SealedStore:
    keyring = sealing.load_or_create_keyring(tmp_path / "keys" / "fb.key", tmp_path / "repo")
    return sealing.SealedStore(tmp_path / "store", keyring)


def test_key_creation_in_deep_fresh_path(tmp_path: Path):
    """Kills mkdir parents=True mutants (sealing L71): multi-level parent."""
    keyring = sealing.load_or_create_keyring(
        tmp_path / "a" / "b" / "c" / "fb.key", tmp_path / "repo"
    )
    assert len(keyring["encryption_keys"][0]) == 44


def test_second_key_in_existing_parent(tmp_path: Path):
    """Kills mkdir exist_ok=True mutants (sealing L71): parent already exists."""
    parent = tmp_path / "keys"
    sealing.load_or_create_keyring(parent / "one.key", tmp_path / "repo")
    keyring = sealing.load_or_create_keyring(parent / "two.key", tmp_path / "repo")
    assert len(keyring["encryption_keys"][0]) == 44


def test_store_in_deep_fresh_path(tmp_path: Path):
    """Kills store mkdir parents=True mutant (sealing L89)."""
    keyring = sealing.load_or_create_keyring(tmp_path / "k" / "fb.key", tmp_path / "repo")
    st = sealing.SealedStore(tmp_path / "x" / "y" / "store", keyring)
    assert st.seal("s").startswith("sealed/")


def test_exposure_rows_numbered_sequentially_from_one(store: sealing.SealedStore):
    """Kills the row-arithmetic family (sealing L144, 13 mutants): absolute
    numbering, not just relative references."""
    ref = store.seal("SENTINEL-ROWNUM synthetic")
    store.unseal(ref, "A <a@x.invalid>", explicit=True)
    store.unseal(ref, "B <b@x.invalid>", explicit=True)
    rows = store.exposures()
    assert [r["row"] for r in rows] == [1, 2, 3, 4]
    assert rows[1]["attempt_row"] == 1
    assert rows[3]["attempt_row"] == 3


def test_ambiguous_with_exactly_two_matches(store: sealing.SealedStore):
    """Kills the >1 -> >2 mutant (sealing L134): exactly two matches."""
    ref = store.seal("SENTINEL-AMBIG synthetic")
    short = ref.split("/", 1)[1]
    (store.store_dir / f"{short}{'0' * 48}.fernet").write_bytes(b"decoy")
    with pytest.raises(sealing.SealingError) as err:
        store.unseal(ref, "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == sealing.REASON_AMBIGUOUS_REF


def test_explicit_is_keyword_only(store: sealing.SealedStore):
    """Kills the keyword-only marker mutant (sealing L149): explicitness is
    the safety semantic and must not be passable positionally."""
    ref = store.seal("SENTINEL-KW synthetic")
    with pytest.raises(TypeError):
        store.unseal(ref, "A <a@x.invalid>", True)  # noqa: B026


def test_preview_line_count_and_digest_shape(store: sealing.SealedStore):
    """Kills the or->and mutant (L211) and digest[:8] NumberReplacers (L215)."""
    assert "3 lines" in store.structural_preview("a\nb\nc", [])
    assert "1 lines" in store.structural_preview("", [])
    assert re.search(r"keyed digest [0-9a-f]{8};", store.structural_preview("x", []))


def test_confirmed_at_alone_is_still_a_confirmation_claim():
    """Kills the or->and mutant (provenance L219): a record claiming only
    confirmed_at (confirmed_by null, no attestation) must still fail as
    attestation-missing; under the mutant it verified clean."""
    stamped = prov.stamp(copy.deepcopy(BASE))
    stamped["provenance"]["confirmed_at"] = "2026-08-24T13:00:00+00:00"
    codes = {f["reason_code"] for f in prov.verify_chain([stamped])}
    assert codes == {prov.REASON_ATTESTATION_MISSING}


def test_attestation_tamper_detected_in_both_hash_orderings():
    """Kills provenance L254 '!=' -> '<' (STEP-04 close audit). The
    attestation comparison had only ever been tested with one ordering of
    stored vs expected hash, so a weakened comparison passed by luck. Same
    class as the content-hash orderings killed at STEP-02: a repeat, and
    the eval says so."""
    stamped = prov.stamp(copy.deepcopy(BASE))
    below = above = None
    i = 0
    while below is None or above is None:
        confirmed = prov.confirm(stamped, f"Analyst-{i} <a@x.invalid>")
        real = confirmed["provenance"]["attestation_hash"]
        forged = prov.attestation_hash(
            confirmed["provenance"]["content_hash"],
            "Forged <f@x.invalid>",
            confirmed["provenance"]["confirmed_at"],
        )
        if forged < real and below is None:
            below = confirmed
        if forged > real and above is None:
            above = confirmed
        i += 1
    for confirmed in (below, above):
        tampered = copy.deepcopy(confirmed)
        tampered["provenance"]["confirmed_by"] = "Forged <f@x.invalid>"
        codes = {f["reason_code"] for f in prov.verify_chain([tampered])}
        assert prov.REASON_ATTESTATION_TAMPERED in codes
