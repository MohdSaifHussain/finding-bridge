"""Tamper-evident provenance: SHA-256 content hashing, timestamps, hash chain.

Deterministic only (charter rule 1). Pure functions: nothing here mutates its
input, and nothing here touches the network or any AI.

Sources (fetched 2026-08-24): hashlib and datetime, official Python docs
(https://docs.python.org/3/library/hashlib.html,
https://docs.python.org/3/library/datetime.html; utcnow is deprecated since
3.12, aware datetimes used instead).

Canonical serialization is RFC 8785 (JSON Canonicalization Scheme,
https://www.rfc-editor.org/rfc/rfc8785, fetched 2026-08-24), adopted per
STEP-02 D1 / DEV-6, discharging DEV-2. What this code depends on is THE
STANDARD, not the library: RFC 8785 is a frozen specification, so the
canonical form stays fully defined and reimplementable if the rfc8785
package ever vanished (DEV-6 condition 5). The library (trailofbits
rfc8785, pinned exactly with hash in constraints.txt) raises on non-string
keys instead of converting; every value we hash originates from JSON, whose
keys are strings by construction.
"""

import copy
import hashlib
from datetime import UTC, datetime

import rfc8785

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
REASON_UNCANONICALIZABLE = "uncanonicalizable"
REASON_ATTESTATION_TAMPERED = "attestation-tampered"
REASON_ATTESTATION_MISSING = "attestation-missing"
REASON_ATTESTATION_SPURIOUS = "attestation-spurious"
REASON_ALREADY_CONFIRMED = "already-confirmed"
REASON_RESTAMP_CONFIRMED = "restamp-confirmed"

# Domain separator so an attestation hash can never collide with a content
# hash computed over crafted content.
ATTESTATION_DOMAIN = "fb-attest:"
HEAD_DOMAIN = "fb-head:"
SUPERSESSION_DOMAIN = "fb-supersede:"

# D-055: the canonical form carries its OWN version, separate from the
# schema version, because the two change independently. Every head
# declares which form its hashes speak, and every supersession event
# states the form it moved from and to.
CANONICAL_FORM_V1 = "v1"  # RFC 8785 (JCS), adopted at OB-3's discharge
CANONICAL_FORM_CURRENT = CANONICAL_FORM_V1

RECORD_TYPE_FINDING = "finding"
RECORD_TYPE_SUPERSESSION = "supersession"

REASON_SUPERSESSION_INVALID = "supersession-invalid"
REASON_HEAD_MISMATCH = "head-mismatch"
REASON_HEAD_TAMPERED = "head-tampered"


class ProvenanceError(Exception):
    """Raised on provenance violations; reason_code is machine-readable."""

    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def canonical_dumps(obj) -> bytes:
    """RFC 8785 serialization with governed refusal (S2-1 backstop, D-038).

    Translates the library's domain errors (NaN/Infinity, integers beyond
    IEEE-double exactness, non-string keys) into a ProvenanceError so no
    caller - including future adapters that skip boundary validation - can
    reach the hash path unguarded. Per D-036 the detail names the error
    CLASS, never the value: untrusted values may sit beside harmful content
    and an error message is an emission surface."""
    try:
        return rfc8785.dumps(obj)
    except rfc8785.CanonicalizationError as exc:
        raise ProvenanceError(
            REASON_UNCANONICALIZABLE,
            f"a value is not representable in RFC 8785 canonical form "
            f"({type(exc).__name__}); the value itself is withheld from this "
            "message by rule D-036",
        ) from exc


def canonical_content_bytes(finding: dict) -> bytes:
    """RFC 8785 canonical serialization of a finding's evidence content."""
    content = {k: v for k, v in finding.items() if k not in EXCLUDED_FROM_HASH}
    return canonical_dumps(content)


def content_hash(finding: dict) -> str:
    return hashlib.sha256(canonical_content_bytes(finding)).hexdigest()


def derive_id(digest: str) -> str:
    return ID_PREFIX + digest[:ID_HASH_CHARS]


def chain_head_internal_ok(head: dict) -> bool:
    """Check a head record's own integrity hash against its fields."""
    payload = canonical_dumps(
        [head.get("count"), head.get("last_content_hash"), head.get("canonical_form")]
    )
    expected = hashlib.sha256(HEAD_DOMAIN.encode("utf-8") + payload).hexdigest()
    return head.get("head_hash") == expected


def attestation_hash(digest: str, confirmed_by: str, confirmed_at: str) -> str:
    """Bind who confirmed what and when to the content hash (review R-1)."""
    payload = canonical_dumps([digest, confirmed_by, confirmed_at])
    return hashlib.sha256(ATTESTATION_DOMAIN.encode("utf-8") + payload).hexdigest()


def stamp(finding: dict, prev_hash: str | None = None) -> dict:
    """Return a copy with id, content_hash and prev_hash set from content.

    Refuses a finding that is already confirmed: re-stamping would give
    edited content a fresh valid hash while keeping the old confirmation
    (laundering; review R-1 companion guard).
    """
    if (finding.get("provenance") or {}).get("confirmed_by") is not None:
        raise ProvenanceError(
            REASON_RESTAMP_CONFIRMED,
            "refusing to re-stamp a confirmed finding; confirmation binds identity",
        )
    stamped = copy.deepcopy(finding)
    digest = content_hash(stamped)
    stamped["id"] = derive_id(digest)
    provenance = stamped.setdefault("provenance", {})
    provenance["content_hash"] = digest
    provenance["prev_hash"] = prev_hash
    provenance.setdefault("confirmed_by", None)
    provenance.setdefault("confirmed_at", None)
    provenance["attestation_hash"] = None
    return stamped


def confirm(finding: dict, confirmed_by: str, confirmed_at: str | None = None) -> dict:
    """Return a copy confirmed by a human identity (ruling D-011).

    The caller (the human gate, D7) supplies the identity; this primitive
    refuses an empty one rather than inventing it. It verifies the stored
    content hash against recomputed content BEFORE attesting (attesting a
    tampered hash would certify garbage), refuses double confirmation, and
    writes the attestation hash that makes the gate record tamper-evident
    (review R-1).
    """
    if not confirmed_by or not confirmed_by.strip():
        raise ProvenanceError(REASON_UNCONFIRMED, "confirmed_by identity is empty")
    stored = (finding.get("provenance") or {}).get("content_hash")
    recomputed = content_hash(finding)
    if stored != recomputed:
        raise ProvenanceError(
            REASON_CONTENT_TAMPERED,
            f"stored content_hash {stored!r} != recomputed {recomputed!r}; "
            "stamp before confirm, and never edit content after stamping",
        )
    if (finding.get("provenance") or {}).get("confirmed_by") is not None:
        raise ProvenanceError(
            REASON_ALREADY_CONFIRMED,
            "finding is already confirmed; re-confirmation would overwrite the gate record",
        )
    confirmed = copy.deepcopy(finding)
    provenance = confirmed.setdefault("provenance", {})
    provenance["confirmed_by"] = confirmed_by
    provenance["confirmed_at"] = confirmed_at or utc_now_iso()
    provenance["attestation_hash"] = attestation_hash(
        recomputed, provenance["confirmed_by"], provenance["confirmed_at"]
    )
    return confirmed


def chain_head(findings: list[dict]) -> dict:
    """Commit to the chain's size and tail (review R-2).

    Modeled on RFC 9162 section 4.1's signed tree head, which commits to
    tree_size precisely so a log cannot be silently shortened; v1 commits to
    (count, last content_hash) with an internal integrity hash but does NOT
    sign it - see the recorded limit: an attacker who can rewrite both the
    ledger and its head can still truncate. Detecting that requires a trust
    anchor outside the store (signing key, remote copy), out of v1 scope.
    """
    count = len(findings)
    last = (findings[-1].get("provenance") or {}).get("content_hash") if findings else None
    form = CANONICAL_FORM_CURRENT
    payload = canonical_dumps([count, last, form])
    head_hash = hashlib.sha256(HEAD_DOMAIN.encode("utf-8") + payload).hexdigest()
    return {
        "count": count,
        "last_content_hash": last,
        "canonical_form": form,
        "head_hash": head_hash,
    }


def verify_chain(findings: list[dict], expected_head: dict | None = None) -> list[dict]:
    """Verify content hashes, derived ids, and chain linkage.

    Returns a list of failures, each {"index", "reason_code", "detail"};
    empty list means the chain verifies. Distinct reason code per failure
    mode (contract 3.6; skill rule 5):
    - content-tampered: stored content_hash does not match recomputed content
    - id-mismatch: stored id does not match the id derived from content
    - chain-broken: prev_hash linkage does not match the preceding record
    - attestation-tampered: confirmed_by/confirmed_at do not match the
      attestation hash (the gate record was edited; review R-1)
    - attestation-missing: a record claims confirmation but carries no
      attestation hash
    - attestation-spurious: an unconfirmed record carries an attestation hash
    - head-tampered: expected_head's own head_hash does not match its fields
    - head-mismatch: the chain does not match expected_head (truncated tail,
      or a rewritten tail record; review R-2)
    """
    failures: list[dict] = []
    if expected_head is not None:
        internal = chain_head_internal_ok(expected_head)
        if not internal:
            failures.append(
                {
                    "index": None,
                    "reason_code": REASON_HEAD_TAMPERED,
                    "detail": "expected_head head_hash does not match its own fields",
                }
            )
        else:
            actual = chain_head(findings)
            if actual["head_hash"] != expected_head["head_hash"]:
                failures.append(
                    {
                        "index": None,
                        "reason_code": REASON_HEAD_MISMATCH,
                        "detail": (
                            f"chain has count={actual['count']}, "
                            f"last={actual['last_content_hash']!r}; head commits to "
                            f"count={expected_head['count']}, "
                            f"last={expected_head['last_content_hash']!r} "
                            "(truncated or rewritten tail)"
                        ),
                    }
                )
    for i, finding in enumerate(findings):
        # THE EPOCH WALK (D-051/W1d), deliberately small. One pass, two
        # record kinds. A supersession record marks a join: its attestation
        # covers the whole event, its old_head must match the running head
        # of everything before it, and its claimed remap must have actually
        # happened. The prev_hash chain is NOT broken by the join - it links
        # THROUGH the supersession record like any other record, which is
        # what keeps one unbroken chain rather than two stitched ones.
        #
        # What an epoch selects, honestly stated: which canonical form a
        # record's hashes speak. Today exactly one form exists (v1, D-055),
        # so there is one code path and the selection is proven by
        # construction, not by a second form existing. A future second form
        # adds a branch here and nowhere else. No epoch bookkeeping is
        # carried in the meantime, because dead machinery is harder to
        # audit than absent machinery - the contract's bound warning cuts
        # toward removing concepts, not keeping them warm.
        if finding.get("record_type") == RECORD_TYPE_SUPERSESSION:
            failures.extend(_verify_supersession(finding, findings, i))
        provenance = finding.get("provenance") or {}
        stored = provenance.get("content_hash")
        recomputed = content_hash(finding)
        confirmed_by = provenance.get("confirmed_by")
        confirmed_at = provenance.get("confirmed_at")
        attestation = provenance.get("attestation_hash")
        if finding.get("record_type") == RECORD_TYPE_SUPERSESSION:
            # its attestation covers the whole event, checked above; the
            # generic gate-record checks below do not apply to it
            if stored != recomputed:
                failures.append(
                    {
                        "index": i,
                        "reason_code": REASON_CONTENT_TAMPERED,
                        "detail": f"supersession stored hash {stored!r} != recomputed",
                    }
                )
            prev = provenance.get("prev_hash")
            expected_prev = (
                (findings[i - 1].get("provenance") or {}).get("content_hash") if i else None
            )
            if prev != expected_prev:
                failures.append(
                    {
                        "index": i,
                        "reason_code": REASON_CHAIN_BROKEN,
                        "detail": f"supersession prev_hash {prev!r} != preceding hash",
                    }
                )
            continue
        if confirmed_by is not None or confirmed_at is not None:
            if attestation is None:
                failures.append(
                    {
                        "index": i,
                        "reason_code": REASON_ATTESTATION_MISSING,
                        "detail": "record claims confirmation but has no attestation_hash",
                    }
                )
            else:
                expected = attestation_hash(recomputed, confirmed_by, confirmed_at)
                if attestation != expected:
                    failures.append(
                        {
                            "index": i,
                            "reason_code": REASON_ATTESTATION_TAMPERED,
                            "detail": (
                                f"attestation_hash {attestation!r} does not match "
                                f"(content_hash, confirmed_by, confirmed_at); the gate "
                                "record was edited after confirmation"
                            ),
                        }
                    )
        elif attestation is not None:
            failures.append(
                {
                    "index": i,
                    "reason_code": REASON_ATTESTATION_SPURIOUS,
                    "detail": "unconfirmed record carries an attestation_hash",
                }
            )
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


# --- supersession: the identity-lifecycle mechanism (D-051) ---

SUPERSESSION_ATTESTED_FIELDS = (
    "event_type",
    "old_head",
    "new_head",
    "remap",
    "canonical_form_from",
    "canonical_form_to",
    "reason",
)


def supersession_attestation(record: dict) -> str:
    """Attestation over the WHOLE event plus who confirmed it and when.

    Everything a reader must trust about the join is inside this hash: the
    event type, both heads, the full remap, both canonical form versions,
    the reason, and the human. Editing any of them without recomputing
    this value fails verification; recomputing it requires being the
    person who re-signs the event, which is the point of the gate.
    """
    provenance = record.get("provenance") or {}
    payload = canonical_dumps(
        [record.get(field) for field in SUPERSESSION_ATTESTED_FIELDS]
        + [provenance.get("confirmed_by"), provenance.get("confirmed_at")]
    )
    return hashlib.sha256(SUPERSESSION_DOMAIN.encode("utf-8") + payload).hexdigest()


def make_supersession(
    *,
    event_type: str,
    old_head: dict,
    new_head: dict,
    remap: dict,
    reason: str,
    confirmed_by: str,
    prev_hash: str | None,
    canonical_form_from: str = CANONICAL_FORM_CURRENT,
    canonical_form_to: str = CANONICAL_FORM_CURRENT,
    confirmed_at: str | None = None,
) -> dict:
    """Build one attested supersession record. Human-gated by construction:
    it refuses without an identity, exactly as confirm() does."""
    if not confirmed_by or not confirmed_by.strip():
        raise ProvenanceError(REASON_UNCONFIRMED, "confirmed_by identity is empty")
    record = {
        "record_type": RECORD_TYPE_SUPERSESSION,
        "event_type": event_type,
        "old_head": old_head,
        "new_head": new_head,
        "remap": remap,
        "canonical_form_from": canonical_form_from,
        "canonical_form_to": canonical_form_to,
        "reason": reason,
        "provenance": {
            "content_hash": None,
            "prev_hash": prev_hash,
            "confirmed_by": confirmed_by,
            "confirmed_at": confirmed_at or utc_now_iso(),
            "attestation_hash": None,
        },
    }
    record["provenance"]["attestation_hash"] = supersession_attestation(record)
    record["provenance"]["content_hash"] = content_hash(record)
    return record


def _verify_supersession(record: dict, records: list[dict], i: int) -> list[dict]:
    """Verify one join. Four checks, each with its own failure detail:

    1. the attestation covers the event as written;
    2. old_head is internally consistent AND matches the RUNNING head of
       every record before this join (the value head.json holds);
    3. new_head is internally consistent;
    4. every id the remap CLAIMS to have produced actually appears in the
       records after this one - a remap claimed but not performed fails.
    """
    failures: list[dict] = []
    provenance = record.get("provenance") or {}

    if provenance.get("attestation_hash") != supersession_attestation(record):
        failures.append(
            {
                "index": i,
                "reason_code": REASON_ATTESTATION_TAMPERED,
                "detail": "supersession attestation does not match the event as written",
            }
        )

    old_head = record.get("old_head") or {}
    if not chain_head_internal_ok(old_head):
        failures.append(
            {
                "index": i,
                "reason_code": REASON_SUPERSESSION_INVALID,
                "detail": "old_head's own head_hash does not match its fields",
            }
        )
    else:
        # The RUNNING head, i.e. every record before this join - the same
        # value head.json holds and a reader sees. An earlier version
        # compared against the current epoch's slice instead; the second
        # rotation in a store proved that wrong, because the state a
        # rotation supersedes is the whole ledger's head, not the segment
        # since the previous rotation. Fixing it REMOVED a concept rather
        # than adding one, which is the direction the contract's bound
        # warning asks for.
        actual = chain_head(records[:i])
        if actual["head_hash"] != old_head.get("head_hash"):
            failures.append(
                {
                    "index": i,
                    "reason_code": REASON_SUPERSESSION_INVALID,
                    "detail": (
                        f"old_head commits to count={old_head.get('count')}, but the "
                        f"epoch it closes has count={actual['count']}"
                    ),
                }
            )

    new_head = record.get("new_head") or {}
    if not chain_head_internal_ok(new_head):
        failures.append(
            {
                "index": i,
                "reason_code": REASON_SUPERSESSION_INVALID,
                "detail": "new_head's own head_hash does not match its fields",
            }
        )

    remap = record.get("remap") or {}
    produced = {r.get("id") for r in records[i + 1 :]}
    unperformed = sorted(new_id for new_id in remap.values() if new_id not in produced)
    if unperformed:
        failures.append(
            {
                "index": i,
                "reason_code": REASON_SUPERSESSION_INVALID,
                "detail": (
                    f"remap claims {len(unperformed)} id(s) this store does not contain "
                    "after the event; a remap claimed but not performed is not a remap"
                ),
            }
        )
    return failures
