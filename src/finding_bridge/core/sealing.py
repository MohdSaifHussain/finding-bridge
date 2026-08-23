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

import hashlib
import json
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from finding_bridge.core.provenance import utc_now_iso

REASON_KEY_INSIDE_REPO = "key-inside-repo"
REASON_UNSEAL_NOT_EXPLICIT = "unseal-not-explicit"
REASON_BLOB_MISSING = "blob-missing"
REASON_SEAL_INTEGRITY = "seal-integrity"

REF_PREFIX = "sealed/"
EXPOSURE_LOG_NAME = "exposure_log.jsonl"


class SealingError(Exception):
    """Raised on sealing violations; reason_code is machine-readable."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def load_or_create_key(key_path: Path, repo_root: Path) -> bytes:
    """Load the Fernet key, creating one on first use. Refuses a key inside
    the repo tree (D-010): the key must never be committable."""
    key_path = key_path.resolve()
    repo_root = repo_root.resolve()
    if key_path.is_relative_to(repo_root):
        raise SealingError(
            REASON_KEY_INSIDE_REPO,
            f"sealing key path {key_path} resolves inside the repo tree {repo_root}",
        )
    if key_path.exists():
        return key_path.read_bytes().strip()
    key = Fernet.generate_key()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_bytes(key)
    return key


class SealedStore:
    """Encrypted-at-rest store for harmful content, with an exposure log."""

    def __init__(self, store_dir: Path, key: bytes):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._fernet = Fernet(key)

    def _blob_path(self, digest: str) -> Path:
        return self.store_dir / f"{digest}.fernet"

    @property
    def exposure_log_path(self) -> Path:
        return self.store_dir / EXPOSURE_LOG_NAME

    def seal(self, plaintext: str) -> str:
        """Encrypt plaintext into the store; return the sealed reference.

        The reference is derived from the plaintext's SHA-256, so the same
        content seals to the same reference (stable across runs; the hash of
        harmful text exposes no harmful text)."""
        digest = hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
        blob = self._blob_path(digest)
        if not blob.exists():
            blob.write_bytes(self._fernet.encrypt(plaintext.encode("utf-8")))
        return REF_PREFIX + digest[:16]

    def _resolve_ref(self, ref: str) -> Path:
        if not ref.startswith(REF_PREFIX):
            raise SealingError(REASON_BLOB_MISSING, f"malformed sealed ref {ref!r}")
        short = ref[len(REF_PREFIX) :]
        matches = list(self.store_dir.glob(f"{short}*.fernet"))
        if not matches:
            raise SealingError(REASON_BLOB_MISSING, f"no blob for ref {ref!r}")
        return matches[0]

    def unseal(self, ref: str, actor: str, *, explicit: bool = False) -> str:
        """Decrypt a sealed blob. Refuses unless explicit; always logs.

        The exposure log row (who, when, which ref) is written BEFORE the
        plaintext is returned, so no read can happen unlogged."""
        if not explicit:
            raise SealingError(
                REASON_UNSEAL_NOT_EXPLICIT,
                f"unseal of {ref!r} requires explicit=True (charter: unsealing is "
                "always explicit and logged)",
            )
        blob = self._resolve_ref(ref)
        entry = {"actor": actor, "at": utc_now_iso(), "ref": ref}
        with self.exposure_log_path.open("a", encoding="utf-8") as log:
            log.write(json.dumps(entry, sort_keys=True) + "\n")
        try:
            return self._fernet.decrypt(blob.read_bytes()).decode("utf-8")
        except InvalidToken as exc:
            raise SealingError(
                REASON_SEAL_INTEGRITY,
                f"blob for {ref!r} failed authenticated decryption (tampered blob or wrong key)",
            ) from exc

    def exposures(self) -> list[dict]:
        if not self.exposure_log_path.exists():
            return []
        lines = self.exposure_log_path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines if line.strip()]


def structural_preview(plaintext: str, harm_flags: list[str]) -> str:
    """Deterministic safe-to-read preview: structure and metadata, zero content.

    Honest limit (carried): v1's preview is structural metadata only. A
    semantic grey-scale summary of the kind arXiv 2602.19124 points at cannot
    be produced deterministically without exposing content or invoking AI,
    which charter rule 1 forbids in this path; richer previews are analyst-
    written at the human gate."""
    digest = hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
    lines = plaintext.splitlines() or [""]
    flags = ", ".join(harm_flags) if harm_flags else "none recorded"
    return (
        f"[sealed content: {len(plaintext)} chars, {len(lines)} lines, "
        f"sha256 {digest[:8]}; harm flags: {flags}. "
        "Content is sealed; unseal is explicit and logged.]"
    )
