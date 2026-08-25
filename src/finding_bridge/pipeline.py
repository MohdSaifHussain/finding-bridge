"""Deterministic wiring of the charter's data flow (section 5.3):
ingest -> seal -> stamp -> dedup -> human gate -> emit.

No business logic beyond ordering; every operation is a core primitive or an
adapter call. No AI, no network (charter rule 1). Sealing policy: BOTH the
probe and the response are sealed whenever present ("when in doubt on a
safety trade-off, prefer less exposure and more logging" - charter); the
preview is the store's keyed structural preview.

Dedup scope (since D-025, Finding A): the dedup key excludes
reproduction.environment, so byte-identical evidence dedups within a single
ingest and across re-ingests, regardless of per-run bookkeeping. What
remains out of scope is near-duplicate clustering (similar but not identical
evidence), per the contract.
"""

import json
from pathlib import Path

from cryptography.fernet import Fernet

from finding_bridge.adapters.in_ import garak, transcript
from finding_bridge.core import dedup as dedup_mod
from finding_bridge.core import provenance as prov
from finding_bridge.core import sealing
from finding_bridge.core.schema import validate_record

REASON_UNKNOWN_ID = "unknown-id"
REASON_HEAD_MISSING = "head-missing"
REASON_STORE_UNREADABLE = "store-unreadable"
REASON_STORE_UNWRITABLE = "store-unwritable"

CANDIDATES_FILE = "candidates.jsonl"
REJECTED_FILE = "rejected.jsonl"
LEDGER_FILE = "ledger.jsonl"
HEAD_FILE = "head.json"


class PipelineError(Exception):
    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


def _read_jsonl(path: Path) -> list[dict]:
    """Read a store file, refusing (never crashing) on unreadable content.

    Finding B (director's ritual): Notepad on Windows writes UTF-8 with a
    BOM, so encoding is utf-8-sig (accepts a BOM, harmless without one) and
    a BOM-touched ledger reaches the attestation check instead of dying in
    json.loads. Genuinely malformed content refuses with store-unreadable,
    naming the file and line."""
    if not path.exists():
        return []
    records = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise PipelineError(
                REASON_STORE_UNREADABLE,
                f"{path.name} line {lineno} is not valid JSON: {exc.msg}",
            ) from exc
    return records


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )


class Workspace:
    """A local finding workspace: candidates, sealed store, confirmed ledger."""

    def __init__(self, root: Path, key_path: Path, repo_root: Path):
        self.root = Path(root)
        try:
            self.root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            # D-036 class, workspace side (D-069): the store root is an
            # untrusted path; its failure is a governed refusal naming the
            # location and the exception class, never a traceback.
            raise PipelineError(
                REASON_STORE_UNWRITABLE,
                f"store root {self.root} is not writable ({type(exc).__name__})",
            ) from exc
        self.key_path = Path(key_path)
        self.repo_root = Path(repo_root)
        self.keyring = sealing.load_or_create_keyring(self.key_path, self.repo_root)
        self.store = sealing.SealedStore(self.root / "sealed", self.keyring)
        self.candidates_path = self.root / CANDIDATES_FILE
        self.rejected_path = self.root / REJECTED_FILE
        self.ledger_path = self.root / LEDGER_FILE
        self.head_path = self.root / HEAD_FILE

    # -- ingest --

    def ingest_garak(self, hitlog: Path) -> dict:
        processed = []
        for candidate in garak.parse_hitlog(hitlog):
            raw_probe = candidate.pop("_raw_probe", None)
            raw_response = candidate.pop("_raw_response", None)
            raw_context = candidate.pop("_raw_context", None)
            if raw_probe is not None:
                candidate["probe"]["sealed_ref"] = self.store.seal(raw_probe)
            if raw_context is not None:
                env = candidate["reproduction"]["environment"] or {}
                env["context_sealed_ref"] = self.store.seal(raw_context)
                candidate["reproduction"]["environment"] = env
            if raw_response is not None:
                candidate["raw_response_sealed"] = self.store.seal(raw_response)
                candidate["preview"] = self.store.structural_preview(
                    raw_response, candidate["harm_flags"]
                )
            processed.append(prov.stamp(candidate))
        merged = dedup_mod.mark_duplicates(_read_jsonl(self.candidates_path) + processed)
        for finding in merged:
            validate_record(finding)
        _write_jsonl(self.candidates_path, merged)
        duplicates = sum(1 for f in merged if f["dedup"]["duplicate_of"] is not None)
        return {
            "ingested": len(processed),
            "total_candidates": len(merged),
            "duplicates_marked": duplicates,
        }

    def ingest_transcript(self, text: str, metadata: dict | None = None) -> dict:
        """One transcript to one sealed, stamped candidate (STEP-03 D3).

        Reading and capping happen at the CLI boundary (adapters/reading);
        this method takes decoded text and runs the same seal/stamp/dedup
        spine as garak ingest."""
        candidate = transcript.to_candidate(text, metadata)
        raw_probe = candidate.pop("_raw_probe", None)
        raw_response = candidate.pop("_raw_response", None)
        raw_context = candidate.pop("_raw_context", None)
        if raw_probe is not None:
            candidate["probe"]["sealed_ref"] = self.store.seal(raw_probe)
        if raw_context is not None:
            env = candidate["reproduction"]["environment"] or {}
            env["context_sealed_ref"] = self.store.seal(raw_context)
            candidate["reproduction"]["environment"] = env
        if raw_response is not None:
            candidate["raw_response_sealed"] = self.store.seal(raw_response)
            candidate["preview"] = self.store.structural_preview(
                raw_response, candidate["harm_flags"]
            )
        merged = dedup_mod.mark_duplicates(
            _read_jsonl(self.candidates_path) + [prov.stamp(candidate)]
        )
        for finding in merged:
            validate_record(finding)
        _write_jsonl(self.candidates_path, merged)
        duplicates = sum(1 for f in merged if f["dedup"]["duplicate_of"] is not None)
        return {
            "ingested": 1,
            "total_candidates": len(merged),
            "duplicates_marked": duplicates,
        }

    # -- human gate (identity supplied by the caller via gate.get_git_identity) --

    def list_candidates(self) -> list[dict]:
        return _read_jsonl(self.candidates_path)

    def _pop_candidate(self, finding_id: str) -> tuple[dict, list[dict]]:
        candidates = _read_jsonl(self.candidates_path)
        remaining = [c for c in candidates if c.get("id") != finding_id]
        matched = [c for c in candidates if c.get("id") == finding_id]
        if not matched:
            raise PipelineError(REASON_UNKNOWN_ID, f"no candidate with id {finding_id!r}")
        return matched[0], remaining

    def confirm(self, finding_id: str, identity: str) -> dict:
        """Confirm one candidate into the chained ledger. confirmed_by is
        reachable ONLY through core provenance.confirm (D7 condition)."""
        candidate, remaining = self._pop_candidate(finding_id)
        ledger = _read_jsonl(self.ledger_path)
        prev = (ledger[-1].get("provenance") or {}).get("content_hash") if ledger else None
        chained = prov.stamp(candidate, prev_hash=prev)
        confirmed = prov.confirm(chained, identity)
        validate_record(confirmed)
        ledger.append(confirmed)
        _write_jsonl(self.ledger_path, ledger)
        self.head_path.write_text(
            json.dumps(prov.chain_head(ledger), sort_keys=True) + "\n", encoding="utf-8"
        )
        _write_jsonl(self.candidates_path, remaining)
        return confirmed

    def reject(self, finding_id: str) -> dict:
        candidate, remaining = self._pop_candidate(finding_id)
        rejected = _read_jsonl(self.rejected_path)
        rejected.append(candidate)
        _write_jsonl(self.rejected_path, rejected)
        _write_jsonl(self.candidates_path, remaining)
        return candidate

    # -- verification and emission --

    def confirmed_findings(self) -> list[dict]:
        return _read_jsonl(self.ledger_path)

    def rotate_key(self, identity: str, reason: str) -> dict:
        """Rotate the ENCRYPTION key as a supersession event (D-052).

        There is deliberately no other rotation path: the store exposes no
        key-swap of its own, so a rotation that is not recorded in the
        ledger cannot happen through this tool. With the D-053 split the
        ref key never moves, so refs, content hashes and ids survive and
        the remap is EMPTY - the cheapest possible exercise of the
        mechanism, and the reason D-053 was adopted inside D-051.
        """
        ledger = _read_jsonl(self.ledger_path)
        old_head = prov.chain_head(ledger)

        new_key = Fernet.generate_key().decode()
        rotating = sealing.SealedStore(
            self.root / "sealed",
            {**self.keyring, "encryption_keys": [new_key, *self.keyring["encryption_keys"]]},
        )
        rotating.reencrypt_all()

        self.keyring = {**self.keyring, "encryption_keys": [new_key]}
        sealing.write_keyring(self.key_path, self.repo_root, self.keyring)
        self.store = sealing.SealedStore(self.root / "sealed", self.keyring)

        # refs and hashes are untouched by an encryption rotation, so the
        # post-event head over the same records equals the pre-event head
        new_head = prov.chain_head(ledger)
        prev = (ledger[-1].get("provenance") or {}).get("content_hash") if ledger else None
        record = prov.make_supersession(
            event_type="key-rotation",
            old_head=old_head,
            new_head=new_head,
            remap={},
            reason=reason,
            confirmed_by=identity,
            prev_hash=prev,
        )
        validate_record(record)
        ledger.append(record)
        _write_jsonl(self.ledger_path, ledger)
        self.head_path.write_text(
            json.dumps(prov.chain_head(ledger), sort_keys=True) + "\n", encoding="utf-8"
        )
        return record

    def verify(self) -> list[dict]:
        """Verify the confirmed ledger against its head. A non-empty ledger
        with no head record is itself a failure (truncation of the head)."""
        ledger = _read_jsonl(self.ledger_path)
        if not ledger and not self.head_path.exists():
            return []
        if not self.head_path.exists():
            return [
                {
                    "index": None,
                    "reason_code": REASON_HEAD_MISSING,
                    "detail": "ledger exists but head record is missing",
                }
            ]
        try:
            head = json.loads(self.head_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise PipelineError(
                REASON_STORE_UNREADABLE,
                f"{self.head_path.name} is not valid JSON: {exc.msg}",
            ) from exc
        return prov.verify_chain(ledger, expected_head=head)
