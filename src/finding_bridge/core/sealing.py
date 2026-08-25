"""Sealing: harmful content encrypted at rest, sealed by default, logged unseals.

Deterministic only (charter rule 1). Fernet authenticated symmetric encryption
per ruling D-010 (source, fetched 2026-08-24:
https://cryptography.io/en/latest/fernet/ - "Fernet guarantees that a message
encrypted using it cannot be manipulated or read without the key"; decrypt
raises InvalidToken on tamper or wrong key; key is a URL-safe base64-encoded
32-byte key from Fernet.generate_key()).

Binding conditions from D-010: the key lives OUTSIDE the repo tree and is
never committed; a key path inside the repo refuses loudly (key-inside-repo).
Unsealing is always explicit and logged (charter section 6): every unseal
appends who/when/ref to the exposure log, and an unseal without explicit=True
refuses (unseal-not-explicit).
"""

import base64
import hashlib
import hmac
import json
import os
import re
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from finding_bridge.core.provenance import utc_now_iso

REASON_KEY_INSIDE_REPO = "key-inside-repo"
REASON_UNSEAL_NOT_EXPLICIT = "unseal-not-explicit"
REASON_BLOB_MISSING = "blob-missing"
REASON_SEAL_INTEGRITY = "seal-integrity"
REASON_MALFORMED_REF = "malformed-ref"
REASON_AMBIGUOUS_REF = "ambiguous-ref"

# Review R-3: refs and preview digests are KEYED (HMAC-SHA256 under a key
# derived from the sealing key with domain separation), never plain
# sha256(plaintext). A plaintext-derived digest in an emitted packet is a
# confirmation oracle: anyone holding a guessable candidate string (e.g. a
# jailbreak from a public corpus) could hash it and test emitted packets for
# it, learning sealed content without unsealing and without an exposure-log
# row. Keying removes the oracle; refs stay stable within a store.
REF_KEY_DOMAIN = b"fb-refkey:"

SHORT_REF_RE = re.compile(r"[0-9a-f]{16}")

REF_PREFIX = "sealed/"
EXPOSURE_LOG_NAME = "exposure_log.jsonl"


class SealingError(Exception):
    """Raised on sealing violations; reason_code is machine-readable."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


KEYRING_VERSION = 1


def _guard_key_path(key_path: Path, repo_root: Path) -> Path:
    key_path = key_path.resolve()
    repo_root = repo_root.resolve()
    if key_path.is_relative_to(repo_root):
        raise SealingError(
            REASON_KEY_INSIDE_REPO,
            f"sealing key path {key_path} resolves inside the repo tree {repo_root}",
        )
    return key_path


def load_or_create_keyring(key_path: Path, repo_root: Path) -> dict:
    """Load (or create) the keyring: a REF key and one or more encryption
    keys, split per ruling D-053.

    The split is what makes rotation cheap: rotating re-encrypts blobs
    under a new encryption key while the ref key stays fixed, so sealed
    references, content hashes and finding ids do not move, and a
    rotation's remap is empty.

    STATED LIMIT, recorded here because this is where the split lives:
    the REF KEY IS PERMANENT. It can never be rotated without changing
    every reference, hash and id in the store. D-053 moved the frozen
    thing; it did not remove it. Rotating the ref key would be a
    supersession event with a full remap, which is exactly the mechanism
    D-051 exists for, but it is not implemented and not free.

    A pre-split raw Fernet key file upgrades in place: the old key becomes
    the encryption key and the ref key it used to derive becomes the
    stored ref key, so no existing reference breaks.
    """
    key_path = _guard_key_path(key_path, repo_root)
    if key_path.exists():
        raw = key_path.read_bytes().strip()
        try:
            keyring = json.loads(raw)
            if isinstance(keyring, dict) and "encryption_keys" in keyring:
                keyring["ref_key_bytes"] = base64.b64decode(keyring["ref_key"])
                return keyring
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        # legacy raw Fernet key: upgrade in place, preserving refs
        keyring = {
            "keyring_version": KEYRING_VERSION,
            "ref_key": base64.b64encode(hashlib.sha256(REF_KEY_DOMAIN + raw).digest()).decode(),
            "encryption_keys": [raw.decode()],
        }
        _write_keyring(key_path, keyring)
        keyring["ref_key_bytes"] = base64.b64decode(keyring["ref_key"])
        return keyring
    keyring = {
        "keyring_version": KEYRING_VERSION,
        "ref_key": base64.b64encode(Fernet.generate_key()).decode(),
        "encryption_keys": [Fernet.generate_key().decode()],
    }
    _write_keyring(key_path, keyring)
    keyring["ref_key_bytes"] = base64.b64decode(keyring["ref_key"])
    return keyring


def _write_keyring(key_path: Path, keyring: dict) -> None:
    key_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in keyring.items() if k != "ref_key_bytes"}
    key_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    # R-7 / D-023: restrict permissions where the OS honors POSIX modes. On
    # Windows this call only toggles the read-only bit and does NOT restrict
    # access; the operator step there is:
    #   icacls <keyfile> /inheritance:r /grant:r "%USERNAME%":F
    # Recorded honest limit: no ACL guarantee on Windows from this code.
    os.chmod(key_path, 0o600)


class SealedStore:
    """Encrypted-at-rest store for harmful content, with an exposure log."""

    def __init__(self, store_dir: Path, keyring: dict):
        """Takes a KEYRING (D-053), not a bare key: refs derive from the
        permanent ref key, ciphertext from the encryption keys, newest
        first. MultiFernet decrypts under any listed key, which is what
        makes a rotation readable while it is in progress."""
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._keyring = keyring
        self._fernet = MultiFernet([Fernet(k) for k in keyring["encryption_keys"]])
        self._ref_key = keyring["ref_key_bytes"]

    def _keyed_digest(self, plaintext: str) -> str:
        """HMAC-SHA256 of the plaintext under the store's derived ref key
        (R-3): deterministic within this store, underivable without the key."""
        return hmac.new(self._ref_key, plaintext.encode("utf-8"), hashlib.sha256).hexdigest()

    def _blob_path(self, digest: str) -> Path:
        return self.store_dir / f"{digest}.fernet"

    @property
    def exposure_log_path(self) -> Path:
        return self.store_dir / EXPOSURE_LOG_NAME

    def seal(self, plaintext: str) -> str:
        """Encrypt plaintext into the store; return the sealed reference.

        The reference is a KEYED digest of the plaintext (R-3), so the same
        content seals to the same reference within this store, while nobody
        without the key can derive or confirm it from a candidate string."""
        digest = self._keyed_digest(plaintext)
        blob = self._blob_path(digest)
        if not blob.exists():
            blob.write_bytes(self._fernet.encrypt(plaintext.encode("utf-8")))
        return REF_PREFIX + digest[:16]

    def _resolve_ref(self, ref: str) -> Path:
        """Validate the ref BEFORE it touches the filesystem (R-4): only
        exactly 16 lowercase hex chars pass; path separators, dots and glob
        metacharacters refuse with malformed-ref. A prefix matching more
        than one blob refuses with ambiguous-ref instead of silently picking
        one."""
        if not ref.startswith(REF_PREFIX):
            raise SealingError(REASON_MALFORMED_REF, f"malformed sealed ref {ref!r}")
        short = ref[len(REF_PREFIX) :]
        if not SHORT_REF_RE.fullmatch(short):
            raise SealingError(
                REASON_MALFORMED_REF,
                f"ref payload {short!r} is not 16 lowercase hex characters",
            )
        matches = list(self.store_dir.glob(f"{short}*.fernet"))
        if not matches:
            raise SealingError(REASON_BLOB_MISSING, f"no blob for ref {ref!r}")
        if len(matches) > 1:
            raise SealingError(
                REASON_AMBIGUOUS_REF,
                f"ref {ref!r} matches {len(matches)} blobs; refusing to guess",
            )
        return matches[0]

    def _append_log_row(self, row: dict) -> int:
        """Append one row to the append-only exposure log; returns its row
        number (1-based). Rows are never mutated (D-022)."""
        n = len(self.exposures()) + 1
        with self.exposure_log_path.open("a", encoding="utf-8") as log:
            log.write(json.dumps({"row": n, **row}, sort_keys=True) + "\n")
        return n

    def unseal(self, ref: str, actor: str, *, explicit: bool = False) -> str:
        """Decrypt a sealed blob. Refuses unless explicit; always logs.

        Append-only two-row protocol (D-022, review residual #4): an attempt
        row is written BEFORE the decrypt (so no read can happen unlogged),
        and an outcome row referencing it is written after (succeeded, or
        failed with the reason code), so a refused decrypt is never
        indistinguishable from a real exposure. Malformed refs refuse before
        any row is written (R-4)."""
        if not explicit:
            raise SealingError(
                REASON_UNSEAL_NOT_EXPLICIT,
                f"unseal of {ref!r} requires explicit=True (charter: unsealing is "
                "always explicit and logged)",
            )
        blob = self._resolve_ref(ref)
        attempt_row = self._append_log_row(
            {"type": "attempt", "actor": actor, "at": utc_now_iso(), "ref": ref}
        )
        try:
            plaintext = self._fernet.decrypt(blob.read_bytes()).decode("utf-8")
        except InvalidToken as exc:
            self._append_log_row(
                {
                    "type": "outcome",
                    "attempt_row": attempt_row,
                    "outcome": "failed",
                    "reason_code": REASON_SEAL_INTEGRITY,
                    "at": utc_now_iso(),
                }
            )
            raise SealingError(
                REASON_SEAL_INTEGRITY,
                f"blob for {ref!r} failed authenticated decryption (tampered blob or wrong key)",
            ) from exc
        self._append_log_row(
            {
                "type": "outcome",
                "attempt_row": attempt_row,
                "outcome": "succeeded",
                "at": utc_now_iso(),
            }
        )
        return plaintext

    def reencrypt_all(self) -> int:
        """Re-encrypt every blob under the primary key (MultiFernet.rotate).

        Official docs: rotate() "re-encrypts a token under the MultiFernet
        instance's primary key" and "preserves the timestamp that was
        originally saved with the token"
        (https://cryptography.io/en/latest/fernet/, fetched 2026-08-24).
        Refs are NOT touched: they derive from the permanent ref key
        (D-053), which is what keeps identity stable across a rotation."""
        count = 0
        for blob in sorted(self.store_dir.glob("*.fernet")):
            blob.write_bytes(self._fernet.rotate(blob.read_bytes()))
            count += 1
        return count

    def exposures(self) -> list[dict]:
        if not self.exposure_log_path.exists():
            return []
        lines = self.exposure_log_path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines if line.strip()]

    def structural_preview(self, plaintext: str, harm_flags: list[str]) -> str:
        """Deterministic safe-to-read preview: structure and metadata, zero
        content. The digest shown is the store's KEYED digest (R-3), so the
        preview cannot be used to confirm a guessed plaintext.

        Honest limit (carried): v1's preview is structural metadata only. A
        semantic grey-scale summary of the kind arXiv 2602.19124 points at
        cannot be produced deterministically without exposing content or
        invoking AI, which charter rule 1 forbids in this path; richer
        previews are analyst-written at the human gate."""
        digest = self._keyed_digest(plaintext)
        lines = plaintext.splitlines() or [""]
        flags = ", ".join(harm_flags) if harm_flags else "none recorded"
        return (
            f"[sealed content: {len(plaintext)} chars, {len(lines)} lines, "
            f"keyed digest {digest[:8]}; harm flags: {flags}. "
            "Content is sealed; unseal is explicit and logged.]"
        )


def write_keyring(key_path: Path, repo_root: Path, keyring: dict) -> None:
    """Persist a keyring after rotation, with the same repo-path guard as
    creation: a rotated key may never land inside the repo either."""
    _write_keyring(_guard_key_path(key_path, repo_root), keyring)
