# Schema migration note: 0.3.0 to 0.4.0

**Change:** a new required field, `record_type`, on every canonical
finding, plus a new sibling schema, `supersession.schema.json`, for
identity-lifecycle records. Adding a required field is a MAJOR change per
charter section 7; within pre-1.0 development that lands on the 0.x minor
position (0.3.0 to 0.4.0), the same convention D-024 used.

**Why (D-051):** the ledger now holds two kinds of record. Findings are
`record_type: "finding"`. Identity-lifecycle events (key rotation today;
canonical-form change and store merge by construction) are
`record_type: "supersession"` and validate against their own schema.
Verification dispatches on the field, so a record nothing validates
cannot enter the ledger.

**Also in this change, and NOT a schema change:** the chain head now
carries `canonical_form` (D-055). That is provenance machinery, not
schema shape, so it does not move the schema version - but it does move
`head_hash`, because the form is inside the head payload. The golden
vectors caught that move and were re-pinned with the reason recorded.
`content_hash`, attestations and `last_content_hash` are byte-identical
to their pre-change values, which is the evidence the change was scoped
to the head alone.

**Migrating existing records:** a 0.3.0 finding becomes a 0.4.0 finding
by adding `"record_type": "finding"` and setting `schema_version` to
`"0.4.0"`. Nothing else changes. Because `record_type` and
`schema_version` are both inside the hashed content, this DOES change
content hashes and therefore ids - which is precisely the situation the
supersession mechanism exists for. No production store exists, so no
migration was performed; a real one would be a `canonical-form-change`
supersession event with a full remap.

**Existing heads:** any head written before this change fails
`chain_head_internal_ok`, because it lacks `canonical_form`. Again: no
production store, so nothing to migrate. A real one would carry the same
supersession event.
