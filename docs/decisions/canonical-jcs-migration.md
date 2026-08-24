# Canonical-form migration note: RFC 8785 adoption (STEP-02 D1)

**What changed:** canonical serialization for content hashing, dedup keys,
attestation payloads and chain-head payloads moved from Python
`json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)` to
RFC 8785 (JCS) via the hash-pinned `rfc8785==0.1.4` (constraints.txt).
DEV-2 (STEP-01) is discharged by this adoption; OB-3 with it. Ruled:
D-030/D-033 Q3(a), five binding conditions in STEP-02 DEV-6.

**Measured impact on existing data: none.** On the project's entire
current value space the two forms are byte-identical, so every existing
golden vector, fixture and hash verifies unchanged (goldens re-verified
and re-affirmed in the adoption commit, per DEV-6 condition 3). The forms
diverge only on: (1) property names mixing U+E000..U+FFFF with
supplementary-plane characters (JCS sorts by UTF-16 code units - the
supplementary key sorts first); (2) float serialization (ECMA-262
shortest round-trip: 4.50 -> "4.5", and integral floats collapse to
integers, so severity.score 6.0 now hashes identically to 6 - the old
form distinguished them); (3) non-string keys now RAISE
(CanonicalizationError) instead of being silently converted - nothing in
the pipeline relied on that leniency (inputs are JSON-parsed; guarded by
test_jcs_vectors.py).

**Schema version: unchanged (0.3.0).** No schema field changed; canonical
serialization is provenance machinery, not schema shape. Reading recorded
here so charter §7's bump rule is answered rather than skipped.

**Dependency posture (DEV-6 condition 5):** the dependency is the
STANDARD, not the library. RFC 8785 is a frozen specification; if the
package vanished, the canonical form remains fully defined and
reimplementable, and the permanent vector suite (tests/test_jcs_vectors.py,
vectors drawn from the RFC text, not the library) would verify any
reimplementation.
