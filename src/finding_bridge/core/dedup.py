"""Content-hash dedup. Exact matches only in v1; clustering is a carried limit.

Deterministic only (charter rule 1). Pure functions.

The dedup key excludes discovered_at in addition to provenance's exclusions:
the duplicate case this exists for (charter Pain-4, "did we already find
this") is the same probe and response found again at a different time, so a
timestamp in the key would make every duplicate unique. The key is recomputed
from content, never read from a stored field (skill rule 13: re-derive from
the artifact, not the row).
"""

import copy
import hashlib
import json

from finding_bridge.core.provenance import EXCLUDED_FROM_HASH

DEDUP_EXCLUDED = (*EXCLUDED_FROM_HASH, "discovered_at")

CLUSTER_PREFIX = "cl-"
CLUSTER_HASH_CHARS = 16

REASON_UNSTAMPED = "unstamped-finding"


class DedupError(Exception):
    """Raised on dedup misuse; reason_code is machine-readable."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def dedup_key(finding: dict) -> str:
    content = {k: v for k, v in finding.items() if k not in DEDUP_EXCLUDED}
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def mark_duplicates(findings: list[dict]) -> list[dict]:
    """Return copies with dedup fields set by exact content match.

    First occurrence of a key is canonical (duplicate_of stays null). Later
    occurrences get duplicate_of = canonical finding's id. Every member of a
    key group with more than one member gets the shared cluster_id; unique
    findings keep cluster_id null. Order is preserved; inputs are not
    mutated; content hashes are unaffected because dedup is excluded from
    hashing (provenance chain stays valid after marking).
    """
    # R-8 (D-021): an unstamped finding has no id, canonical_ids[key] would
    # be None, and every duplicate in that group would silently pass as
    # canonical. Refuse instead.
    for i, f in enumerate(findings):
        if not f.get("id"):
            raise DedupError(
                REASON_UNSTAMPED,
                f"finding at index {i} has no id; stamp findings before dedup",
            )
    marked = [copy.deepcopy(f) for f in findings]
    keys = [dedup_key(f) for f in marked]
    counts: dict[str, int] = {}
    for key in keys:
        counts[key] = counts.get(key, 0) + 1
    canonical_ids: dict[str, str | None] = {}
    for finding, key in zip(marked, keys, strict=True):
        dd = finding.setdefault("dedup", {})
        if key in canonical_ids:
            dd["duplicate_of"] = canonical_ids[key]
        else:
            canonical_ids[key] = finding.get("id")
            dd.setdefault("duplicate_of", None)
        dd["cluster_id"] = CLUSTER_PREFIX + key[:CLUSTER_HASH_CHARS] if counts[key] > 1 else None
    return marked


def unique_findings(findings: list[dict]) -> list[dict]:
    """The canonical (non-duplicate) findings, dedup fields set."""
    return [f for f in mark_duplicates(findings) if f["dedup"]["duplicate_of"] is None]
