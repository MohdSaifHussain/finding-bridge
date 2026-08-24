"""Property-based tests (D-027 GATE, quadrant 3: known unknowns).

The invariants are the ones the director ruled; Hypothesis generates the
inputs (source fetched 2026-08-24: hypothesis.readthedocs.io, v6.165.10).
deadline=None because wall-clock flakiness is not a property of the code
under test; the GATE budget is enforced at the suite level (60s, D-027).
"""

import copy
import json
import re
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from finding_bridge.core import dedup, sealing
from finding_bridge.core import provenance as prov

FIXTURES = Path(__file__).resolve().parent.parent / "schemas" / "fixtures"
BASE = json.loads((FIXTURES / "candidate_null_fields.json").read_text(encoding="utf-8"))

COMMON = settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])


def fresh_base() -> dict:
    return copy.deepcopy(BASE)


@pytest.fixture(scope="module")
def store(tmp_path_factory) -> sealing.SealedStore:
    root = tmp_path_factory.mktemp("prop")
    key = sealing.load_or_create_key(root / "keys" / "fb.key", root / "repo")
    return sealing.SealedStore(root / "store", key)


# --- invariant 1: hash determinism and order independence ---


@COMMON
@given(seed=st.randoms(use_true_random=False))
def test_content_hash_is_order_independent(seed):
    finding = fresh_base()
    items = list(finding.items())
    seed.shuffle(items)
    shuffled = dict(items)
    assert prov.content_hash(shuffled) == prov.content_hash(finding)
    assert dedup.dedup_key(shuffled) == dedup.dedup_key(finding)


@COMMON
@given(preview=st.text(max_size=200))
def test_content_hash_is_deterministic_across_copies(preview):
    finding = fresh_base()
    finding["preview"] = preview
    assert prov.content_hash(finding) == prov.content_hash(copy.deepcopy(finding))


# --- invariant 2: verify_chain accepts every well-formed chain and rejects
# --- every single-record mutation of a guarded field ---


def build_chain(previews: list[str], confirm_mask: list[bool]) -> list[dict]:
    chain = []
    prev = None
    for preview, do_confirm in zip(previews, confirm_mask, strict=True):
        candidate = fresh_base()
        candidate["preview"] = preview
        stamped = prov.stamp(candidate, prev_hash=prev)
        if do_confirm:
            stamped = prov.confirm(stamped, "Prop Analyst <p@example.invalid>")
        chain.append(stamped)
        prev = stamped["provenance"]["content_hash"]
    return chain


@COMMON
@given(
    previews=st.lists(st.text(max_size=50), min_size=1, max_size=5),
    data=st.data(),
)
def test_every_well_formed_chain_verifies(previews, data):
    mask = data.draw(st.lists(st.booleans(), min_size=len(previews), max_size=len(previews)))
    chain = build_chain(previews, mask)
    assert prov.verify_chain(chain, expected_head=prov.chain_head(chain)) == []


GUARDED_MUTATIONS = [
    ("preview", lambda f: f.__setitem__("preview", (f["preview"] or "") + "X")),
    ("source_tool", lambda f: f.__setitem__("source_tool", f["source_tool"] + "X")),
    ("harm_flags", lambda f: f["harm_flags"].append("injected-flag")),
    ("probe.value", lambda f: f["probe"].__setitem__("value", "injected")),
    ("severity.score", lambda f: f["severity"].__setitem__("score", 9)),
    ("id", lambda f: f.__setitem__("id", "fb-0000000000000000")),
    (
        "provenance.confirmed_by",
        lambda f: f["provenance"].__setitem__("confirmed_by", "Forged <x@x.invalid>"),
    ),
    (
        "provenance.prev_hash",
        lambda f: f["provenance"].__setitem__("prev_hash", "f" * 64),
    ),
]


@COMMON
@given(
    previews=st.lists(st.text(max_size=30), min_size=1, max_size=4),
    index=st.data(),
    mutation=st.sampled_from(GUARDED_MUTATIONS),
)
def test_every_single_record_mutation_is_rejected(previews, index, mutation):
    chain = build_chain(previews, [False] * len(previews))
    i = index.draw(st.integers(min_value=0, max_value=len(chain) - 1))
    name, mutate = mutation
    mutate(chain[i])
    failures = prov.verify_chain(chain, expected_head=prov.chain_head(chain))
    assert failures, f"mutation of {name} at index {i} went undetected"


# --- invariant 3: the sealed-ref validator accepts only ^[0-9a-f]{16}$ ---


@COMMON
@given(payload=st.text(max_size=40))
def test_ref_validator_accepts_only_16_lowercase_hex(payload, store):
    ref = sealing.REF_PREFIX + payload
    if re.fullmatch(r"[0-9a-f]{16}", payload):
        with pytest.raises(sealing.SealingError) as err:
            store.unseal(ref, "P <p@x.invalid>", explicit=True)
        assert err.value.reason_code in (
            sealing.REASON_BLOB_MISSING,
            sealing.REASON_AMBIGUOUS_REF,
        ), "well-formed payloads must pass validation and fail only on lookup"
    else:
        with pytest.raises(sealing.SealingError) as err:
            store.unseal(ref, "P <p@x.invalid>", explicit=True)
        assert err.value.reason_code == sealing.REASON_MALFORMED_REF


# --- invariant 4: seal-then-unseal round-trips ---


@COMMON
@given(plaintext=st.text(min_size=0, max_size=2000))
def test_seal_unseal_round_trip(plaintext, store):
    ref = store.seal(plaintext)
    assert store.unseal(ref, "P <p@x.invalid>", explicit=True) == plaintext


def test_seal_unseal_round_trip_very_long(store):
    """Explicit large case, outside Hypothesis so the GATE stays fast."""
    plaintext = "SENTINEL-LONG " + ("x" * 200_000) + " é中\U0001f600"
    ref = store.seal(plaintext)
    assert store.unseal(ref, "P <p@x.invalid>", explicit=True) == plaintext
