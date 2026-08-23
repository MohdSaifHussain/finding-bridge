"""Tamper-evident provenance: SHA-256 content hashing, timestamps, hash chain.

Deterministic only (charter rule 1). Pure functions: nothing here mutates its
input, and nothing here touches the network or any AI.

Sources (fetched 2026-08-24): hashlib and datetime, official Python docs
(https://docs.python.org/3/library/hashlib.html,
https://docs.python.org/3/library/datetime.html; utcnow is deprecated since
3.12, aware datetimes used instead).
"""

import copy
import hashlib
import json
from datetime import UTC, datetime

# Evidence content is hashed; stamps and triage state are not. provenance
# holds the hash itself (chicken-and-egg) and dedup is mutable triage state,
# so both are excluded. id is derived FROM the hash, so it is excluded too.
EXCLUDED_FROM_HASH = ("id", "provenance", "dedup")

ID_PREFIX = "fb-"
ID_HASH_CHARS = 16

REASON_CONTENT_TAMPERED = "content-tampered"
REASON_CHAIN_BROKEN = "chain-broken"
REASON_ID_MISMATCH = "id-mismatch"
REASON_UNCONFIRMED = "unconfirmed"


class ProvenanceError(Exception):
    """Raised on provenance violations; reason_code is machine-readable."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def canonical_content_bytes(finding: dict) -> bytes:
    """Deterministic serialization of the evidence content of a finding."""
    content = {k: v for k, v in finding.items() if k not in EXCLUDED_FROM_HASH}
    return json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def content_hash(finding: dict) -> str:
    return hashlib.sha256(canonical_content_bytes(finding)).hexdigest()


def derive_id(digest: str) -> str:
    return ID_PREFIX + digest[:ID_HASH_CHARS]


def stamp(finding: dict, prev_hash: str | None = None) -> dict:
    """Return a copy with id, content_hash and prev_hash set from content."""
    stamped = copy.deepcopy(finding)
    digest = content_hash(stamped)
    stamped["id"] = derive_id(digest)
    provenance = stamped.setdefault("provenance", {})
    provenance["content_hash"] = digest
    provenance["prev_hash"] = prev_hash
    provenance.setdefault("confirmed_by", None)
    provenance.setdefault("confirmed_at", None)
    return stamped


def confirm(finding: dict, confirmed_by: str, confirmed_at: str | None = None) -> dict:
    """Return a copy confirmed by a human identity (ruling D-011).

    The caller (the human gate, D7) supplies the identity; this primitive
    refuses an empty one rather than inventing it.
    """
    if not confirmed_by or not confirmed_by.strip():
        raise ProvenanceError(REASON_UNCONFIRMED, "confirmed_by identity is empty")
    confirmed = copy.deepcopy(finding)
    provenance = confirmed.setdefault("provenance", {})
    provenance["confirmed_by"] = confirmed_by
    provenance["confirmed_at"] = confirmed_at or utc_now_iso()
    return confirmed


def verify_chain(findings: list[dict]) -> list[dict]:
    """Verify content hashes, derived ids, and chain linkage.

    Returns a list of failures, each {"index", "reason_code", "detail"};
    empty list means the chain verifies. Distinct reason code per failure
    mode (contract 3.6; skill rule 5):
    - content-tampered: stored content_hash does not match recomputed content
    - id-mismatch: stored id does not match the id derived from content
    - chain-broken: prev_hash linkage does not match the preceding record
    """
    failures: list[dict] = []
    for i, finding in enumerate(findings):
        stored = (finding.get("provenance") or {}).get("content_hash")
        recomputed = content_hash(finding)
        if stored != recomputed:
            failures.append(
                {
                    "index": i,
                    "reason_code": REASON_CONTENT_TAMPERED,
                    "detail": f"stored content_hash {stored!r} != recomputed {recomputed!r}",
                }
            )
        if finding.get("id") != derive_id(recomputed):
            failures.append(
                {
                    "index": i,
                    "reason_code": REASON_ID_MISMATCH,
                    "detail": f"id {finding.get('id')!r} != derived {derive_id(recomputed)!r}",
                }
            )
        prev = (finding.get("provenance") or {}).get("prev_hash")
        if i == 0:
            if prev is not None:
                failures.append(
                    {
                        "index": 0,
                        "reason_code": REASON_CHAIN_BROKEN,
                        "detail": f"first record prev_hash must be null, got {prev!r}",
                    }
                )
        else:
            expected = (findings[i - 1].get("provenance") or {}).get("content_hash")
            if prev != expected:
                failures.append(
                    {
                        "index": i,
                        "reason_code": REASON_CHAIN_BROKEN,
                        "detail": f"prev_hash {prev!r} != preceding content_hash {expected!r}",
                    }
                )
    return failures
