# STEP-01 review stop: contract 4a adversarial self-review

Standalone deliverable of the review stop, produced 2026-08-24 at commit
`712b610`, after the round-2 blocking fixes. A first in-session 4a review was
delivered before the director's independent findings arrived (it reported
seven findings, reconciled below); this report is the 4a deliverable of
record, quoting current lines. The director's ten findings (R-1..R-10) are an
independent second opinion and are answered in §4; disagreements are stated
in §5 with grounds.

## 1. Guarantee (a): determinism, no AI in the evidence path

- `src/finding_bridge/core/__init__.py:1`:
  `"""Deterministic core: schema, provenance, sealing, dedup. No AI in this path, ever."""`
- Complete import surface of `core/` (verified by reading every import line):
  `provenance.py:12-15` (`copy`, `hashlib`, `json`, `datetime`),
  `sealing.py:17-25` (`hashlib`, `hmac`, `json`, `re`, `pathlib`,
  `cryptography.fernet`, and `provenance.utc_now_iso`), `dedup.py`
  (`copy`, `hashlib`, `json`, `provenance`). No network module, no AI SDK,
  no subprocess. The `ai/` package does not exist in the tree.
- Proven by execution: the full suite (69 tests) passes with
  `ANTHROPIC_API_KEY=dummy` deliberately set and scrubbed by
  `tests/conftest.py:22-27` (autouse session fixture), guard-verified by
  `tests/test_environment.py:14-16` (observed run, this session, exit 0).

## 2. Guarantee (b): seal-by-default enforcement

- Encryption at rest: `sealing.py:97-107` (`seal()` writes only
  `self._fernet.encrypt(...)` bytes; no plaintext write path exists in the
  module). Test: `tests/test_sealing.py:53-59` asserts
  `SENTINEL.encode("utf-8") not in raw` on the stored blob, with the
  positive control at `:77-85` proving the sentinel is recoverable only via
  explicit unseal.
- Key placement guard: `sealing.py:63-67`:
  `if key_path.is_relative_to(repo_root): raise SealingError(REASON_KEY_INSIDE_REPO, ...)`.
- No content leaves the store unkeyed: `sealing.py:85-88` (`_keyed_digest`,
  HMAC-SHA256 under a domain-separated derived key) feeds refs (`:103`),
  blob filenames (`:90-91`), and preview digests (`:172`). Tests
  `test_sealing.py:137-159` assert the plain `sha256(plaintext)` prefixes
  appear in none of them.

## 3. Guarantee (c): every negative path refuses with its stated reason code

| Refusal | Code raised at | Asserted by |
|---|---|---|
| Unseal without explicit flag | `sealing.py:138-143` (`unseal-not-explicit`) | `test_sealing.py:69-74` (also: exposure log stays empty) |
| Key inside repo tree | `sealing.py:63-67` (`key-inside-repo`) | `test_sealing.py:32-35` |
| Malformed/traversal/glob ref | `sealing.py:115-122` (`malformed-ref`) | `test_sealing.py:170-186` |
| Ambiguous ref prefix | `sealing.py:126-130` (`ambiguous-ref`) | `test_sealing.py:189-196` |
| Missing blob | `sealing.py:124-125` (`blob-missing`) | `test_sealing.py:95-98` |
| Tampered blob / wrong key | `sealing.py:150-154` (`seal-integrity`) | `test_sealing.py:101-115` |
| Content edited after stamp | `provenance.py` verify loop (`content-tampered`) | `test_provenance.py:104-108` |
| Edited-and-rehashed record | linkage check (`chain-broken`) | `test_provenance.py:111-120` |
| Forged id | (`id-mismatch`) | `test_provenance.py:123-127` |
| Edited confirmed_by / confirmed_at | (`attestation-tampered`) | `test_provenance.py:148-161` |
| Injected confirmation, no attestation | (`attestation-missing`) | `test_provenance.py:164-169` |
| Attestation on unconfirmed record | (`attestation-spurious`) | `test_provenance.py:172-176` |
| Truncated or rewritten tail vs head | (`head-mismatch`) | R-2 tests in `test_provenance.py` |
| Inconsistent head record | (`head-tampered`) | R-2 tests |
| Empty confirm identity | `provenance.py:125-126` (`unconfirmed`) | `test_provenance.py:88-91` |
| Confirm over tampered content | `provenance.py:129-134` (`content-tampered`) | `test_provenance.py:186-191` |
| Double confirm / re-stamp confirmed | (`already-confirmed`, `restamp-confirmed`) | `test_provenance.py:194-205` |

Positive controls exist beside each family (valid chain `[]`, confirmed chain
`[]`, head round-trip, explicit unseal returns plaintext and logs).

## 4. Reconciliation with the director's ten findings

Builder's earlier seven findings vs R-1..R-10: my #1 (re-stamp laundering)
was a strict subset of R-1 — I caught the laundering vector, I missed that a
direct edit of confirmed_by verified clean, and my own test certified the
hole. My #2 = R-3 for refs, but I missed the preview digest leak
(sha256[:8]) while claiming "preview contains no content". My #3 = R-4's
ambiguity half; I missed the traversal/injection half. My #5 = R-7. My #4
(exposure log records attempts not outcomes), #6 (format is annotational in
2020-12), #7 (unruled defaults) were not in the director's list and still
await ruling. R-2, R-5, R-6, R-8, R-9, R-10 were escapes: found by the
director's review, not mine. Builder escape count this round: 6 of 10
director findings were not in my self-review (R-1's core, R-2, R-5, R-6,
R-8, R-10 as a suite property; R-9 I had not stated as a limit).

## 5. Disagreements, with grounds

1. **R-1, one precision, not a dispute of the remedy:** the hash exclusion at
   `provenance.py:20` is itself correct design (the hash cannot include the
   object that stores it, and dedup is mutable triage state). The defect was
   the absent second guard over the excluded fields. The fix keeps the
   exclusion and adds the attestation, and the rewritten test
   (`test_provenance.py:45-64`) now asserts the exclusion+guard PAIR, which
   is the true invariant.
2. **R-10, width of the claim:** "currently claimed, not demonstrated" is
   slightly wider than what happened: one ad-hoc `env -u ... pytest` run was
   observed and cited (D1 commit message). What the contract requires, and
   what was genuinely missing, is the scrub as an enforced suite property
   shown in the director's own run. The finding stands; the sentence narrows.
3. **R-2, one limit on the fix, stated not disputed:** RFC 9162's guarantee
   flows from the head being signed and externally witnessed. v1's head is
   unsigned; it detects truncation by any actor who cannot rewrite the head,
   and an attacker who rewrites ledger AND head together still wins. The
   docstring at `provenance.py:150-158` says so; a trust anchor outside the
   store is out of v1 scope and should be a named obligation if wanted.

No other disagreements: R-3, R-4, R-5's two named divergences, R-6's quoted
doc lines, R-8's None-id bug, and R-9's truncation math were checked and are
correct as stated.
