"""D4 tests: seal-by-default, key placement, explicit+logged unseal, previews.

SENTINEL strings stand in for harmful content (ruling D-012). Each guard has
a negative control and a positive control (skill rule 5)."""

from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from finding_bridge.core import sealing

SENTINEL = "SENTINEL-HARM-9999 synthetic stand-in, not real model output"


def _fresh_keyring() -> dict:
    """A wholly different keyring: used to prove a wrong key refuses."""
    import base64

    return {
        "keyring_version": 1,
        "ref_key": base64.b64encode(Fernet.generate_key()).decode(),
        "ref_key_bytes": base64.b64decode(base64.b64encode(Fernet.generate_key())),
        "encryption_keys": [Fernet.generate_key().decode()],
    }


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    return root


@pytest.fixture()
def store(tmp_path: Path, repo_root: Path) -> sealing.SealedStore:
    keyring = sealing.load_or_create_keyring(tmp_path / "outside" / "fb.key", repo_root)
    return sealing.SealedStore(tmp_path / "outside" / "store", keyring)


# --- key placement (D-010) ---


def test_key_inside_repo_refused(repo_root: Path):
    with pytest.raises(sealing.SealingError) as err:
        sealing.load_or_create_keyring(repo_root / "sub" / "fb.key", repo_root)
    assert err.value.reason_code == sealing.REASON_KEY_INSIDE_REPO


def test_key_outside_repo_accepted(tmp_path: Path, repo_root: Path):
    keyring = sealing.load_or_create_keyring(tmp_path / "elsewhere" / "fb.key", repo_root)
    assert len(keyring["encryption_keys"][0]) == 44  # url-safe base64 of 32 bytes


def test_key_is_stable_across_loads(tmp_path: Path, repo_root: Path):
    path = tmp_path / "elsewhere" / "fb.key"
    first = sealing.load_or_create_keyring(path, repo_root)
    second = sealing.load_or_create_keyring(path, repo_root)
    assert first["ref_key"] == second["ref_key"]
    assert first["encryption_keys"] == second["encryption_keys"]


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
    assert log[0]["actor"] == "Analyst <a@example.invalid>"
    assert log[0]["ref"] == ref
    assert log[0]["at"]


def test_every_unseal_appends_attempt_rows(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    store.unseal(ref, "A <a@x.invalid>", explicit=True)
    store.unseal(ref, "B <b@x.invalid>", explicit=True)
    attempts = [r["actor"] for r in store.exposures() if r["type"] == "attempt"]
    assert attempts == ["A <a@x.invalid>", "B <b@x.invalid>"]


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
    other = sealing.SealedStore(store.store_dir, _fresh_keyring())
    with pytest.raises(sealing.SealingError) as err:
        other.unseal(ref, "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == sealing.REASON_SEAL_INTEGRITY


# --- preview: structure only, zero content ---


def test_preview_contains_no_plaintext(store: sealing.SealedStore):
    preview = store.structural_preview(SENTINEL, ["synthetic-test-category"])
    assert "SENTINEL-HARM-9999" not in preview
    assert "synthetic-test-category" in preview
    assert str(len(SENTINEL)) in preview


def test_preview_is_deterministic(store: sealing.SealedStore):
    a = store.structural_preview(SENTINEL, [])
    b = store.structural_preview(SENTINEL, [])
    assert a == b


# --- R-3: no plaintext-derived digest leaves the store ---


def test_ref_is_not_plaintext_hash_derived(store: sealing.SealedStore):
    import hashlib

    ref = store.seal(SENTINEL)
    plain_digest = hashlib.sha256(SENTINEL.encode("utf-8")).hexdigest()
    assert plain_digest[:16] not in ref, "ref must not be derivable from plaintext alone"


def test_preview_digest_is_not_plaintext_hash(store: sealing.SealedStore):
    import hashlib

    preview = store.structural_preview(SENTINEL, ["synthetic-test-category"])
    plain_digest = hashlib.sha256(SENTINEL.encode("utf-8")).hexdigest()
    assert plain_digest[:8] not in preview, "preview digest must not confirm guessed plaintext"


def test_blob_filename_is_not_plaintext_hash(store: sealing.SealedStore):
    import hashlib

    store.seal(SENTINEL)
    plain_digest = hashlib.sha256(SENTINEL.encode("utf-8")).hexdigest()
    for blob in store.store_dir.glob("*.fernet"):
        assert plain_digest[:16] not in blob.name


def test_refs_differ_across_keys(tmp_path, store: sealing.SealedStore):
    other = sealing.SealedStore(tmp_path / "other-store", _fresh_keyring())
    assert store.seal(SENTINEL) != other.seal(SENTINEL)


# --- R-4: ref validation before the filesystem, ambiguity refused ---


def test_path_traversal_ref_refused(store: sealing.SealedStore):
    with pytest.raises(sealing.SealingError) as err:
        store.unseal("sealed/../../etc/key", "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == "malformed-ref"
    assert store.exposures() == [] or store.exposures()[-1]["ref"] != "sealed/../../etc/key"


def test_glob_metacharacter_ref_refused(store: sealing.SealedStore):
    with pytest.raises(sealing.SealingError) as err:
        store.unseal("sealed/*", "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == "malformed-ref"


def test_uppercase_hex_ref_refused(store: sealing.SealedStore):
    with pytest.raises(sealing.SealingError) as err:
        store.unseal("sealed/DEADBEEFDEADBEEF", "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == "malformed-ref"


def test_ambiguous_prefix_refused(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    short = ref.split("/", 1)[1]
    (store.store_dir / f"{short}{'0' * 48}.fernet").write_bytes(b"decoy-a")
    (store.store_dir / f"{short}{'1' * 48}.fernet").write_bytes(b"decoy-b")
    with pytest.raises(sealing.SealingError) as err:
        store.unseal(ref, "A <a@x.invalid>", explicit=True)
    assert err.value.reason_code == "ambiguous-ref"


# --- D-022 (#4): append-only two-row exposure protocol ---


def test_successful_unseal_writes_attempt_and_outcome_rows(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    out = store.unseal(ref, "Analyst <a@example.invalid>", explicit=True)
    assert out == SENTINEL
    rows = store.exposures()
    assert [r["type"] for r in rows] == ["attempt", "outcome"]
    assert rows[0]["actor"] == "Analyst <a@example.invalid>"
    assert rows[1]["attempt_row"] == rows[0]["row"]
    assert rows[1]["outcome"] == "succeeded"


def test_failed_unseal_writes_failure_row_and_no_plaintext(store: sealing.SealedStore):
    ref = store.seal(SENTINEL)
    blob = next(store.store_dir.glob("*.fernet"))
    blob.write_bytes(b"tampered" + blob.read_bytes()[8:])
    with pytest.raises(sealing.SealingError) as err:
        store.unseal(ref, "Analyst <a@example.invalid>", explicit=True)
    assert err.value.reason_code == sealing.REASON_SEAL_INTEGRITY
    rows = store.exposures()
    assert [r["type"] for r in rows] == ["attempt", "outcome"]
    assert rows[1]["outcome"] == "failed"
    assert rows[1]["reason_code"] == sealing.REASON_SEAL_INTEGRITY


def test_key_file_permissions_restricted_where_honored(tmp_path: Path, repo_root: Path):
    """R-7: 0o600 where the OS honors it; on Windows this documents the gap
    rather than asserting a guarantee chmod does not deliver there."""
    import stat
    import sys

    path = tmp_path / "perm" / "fb.key"
    sealing.load_or_create_keyring(path, repo_root)
    if sys.platform == "win32":
        pytest.skip("Windows ACLs are not set by chmod; operator step is icacls (recorded limit)")
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
