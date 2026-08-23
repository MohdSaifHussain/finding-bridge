"""D4 tests: seal-by-default, key placement, explicit+logged unseal, previews.

SENTINEL strings stand in for harmful content (ruling D-012). Each guard has
a negative control and a positive control (skill rule 5)."""

from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from finding_bridge.core import sealing

SENTINEL = "SENTINEL-HARM-9999 synthetic stand-in, not real model output"


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    return root


@pytest.fixture()
def store(tmp_path: Path, repo_root: Path) -> sealing.SealedStore:
    key = sealing.load_or_create_key(tmp_path / "outside" / "fb.key", repo_root)
    return sealing.SealedStore(tmp_path / "outside" / "store", key)


# --- key placement (D-010) ---


def test_key_inside_repo_refused(repo_root: Path):
    with pytest.raises(sealing.SealingError) as err:
        sealing.load_or_create_key(repo_root / "sub" / "fb.key", repo_root)
    assert err.value.reason_code == sealing.REASON_KEY_INSIDE_REPO


def test_key_outside_repo_accepted(tmp_path: Path, repo_root: Path):
    key = sealing.load_or_create_key(tmp_path / "elsewhere" / "fb.key", repo_root)
    assert len(key) == 44  # url-safe base64 of 32 bytes


def test_key_is_stable_across_loads(tmp_path: Path, repo_root: Path):
    path = tmp_path / "elsewhere" / "fb.key"
    first = sealing.load_or_create_key(path, repo_root)
    second = sealing.load_or_create_key(path, repo_root)
    assert first == second


# --- sealing at rest ---


def test_sealed_blob_does_not_contain_plaintext(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    blobs = list(store.store_dir.glob("*.fernet"))
    assert len(blobs) == 1
    raw = blobs[0].read_bytes()
    assert SENTINEL.encode("utf-8") not in raw
    assert ref.startswith("sealed/")


def test_same_content_seals_to_same_ref(store: sealing.SealedStore):
    assert store.seal(SENTINEL) == store.seal(SENTINEL)


# --- unseal: explicit and logged, refuses otherwise ---


def test_unseal_without_explicit_refused_and_unlogged(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    with pytest.raises(sealing.SealingError) as err:
        store.unseal(ref, "Analyst <a@example.invalid>")
    assert err.value.reason_code == sealing.REASON_UNSEAL_NOT_EXPLICIT
    assert store.exposures() == []


def test_explicit_unseal_returns_plaintext_and_logs(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    out = store.unseal(ref, "Analyst <a@example.invalid>", explicit=True)
    assert out == SENTINEL
    log = store.exposures()
    assert len(log) == 1
    assert log[0]["actor"] == "Analyst <a@example.invalid>"
    assert log[0]["ref"] == ref
    assert log[0]["at"]


def test_every_unseal_appends_a_log_row(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    store.unseal(ref, "A <a@x.invalid>", explicit=True)
    store.unseal(ref, "B <b@x.invalid>", explicit=True)
    assert [row["actor"] for row in store.exposures()] == ["A <a@x.invalid>", "B <b@x.invalid>"]


def test_missing_blob_refused(store: sealing.SealedStore):
    with pytest.raises(sealing.SealingError) as err:
        store.unseal("sealed/deadbeefdeadbeef", "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == sealing.REASON_BLOB_MISSING


def test_tampered_blob_refused(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    blob = next(store.store_dir.glob("*.fernet"))
    blob.write_bytes(b"tampered" + blob.read_bytes()[8:])
    with pytest.raises(sealing.SealingError) as err:
        store.unseal(ref, "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == sealing.REASON_SEAL_INTEGRITY


def test_wrong_key_refused(tmp_path: Path, store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    other = sealing.SealedStore(store.store_dir, Fernet.generate_key())
    with pytest.raises(sealing.SealingError) as err:
        other.unseal(ref, "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == sealing.REASON_SEAL_INTEGRITY


# --- preview: structure only, zero content ---


def test_preview_contains_no_plaintext(store: sealing.SealedStore):
    preview = sealing.structural_preview(SENTINEL, ["synthetic-test-category"])
    assert "SENTINEL-HARM-9999" not in preview
    assert "synthetic-test-category" in preview
    assert str(len(SENTINEL)) in preview


def test_preview_is_deterministic():
    a = sealing.structural_preview(SENTINEL, [])
    b = sealing.structural_preview(SENTINEL, [])
    assert a == b
