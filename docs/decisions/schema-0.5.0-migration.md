# Schema migration note: 0.4.0 to 0.5.0

**Change (D-071, D-076; STEP-06 stop one, 2026-08-25):** three additions
and one tightening, no field required, no field removed.

1. `taxonomy.atlas`: a third taxonomy array of `{id, status}` entries for
   MITRE ATLAS technique ids. Optional; absent or empty means no claim.
2. `remediation`: string or null, optional. Written only by a human at
   the gate. Null until then (never-fabricate). The caged `--ai` path has
   no remediation capability; a suggested remediation is a parked future
   `--ai` job beside the semantic preview.
3. `pattern` constraints on every taxonomy id, pinning the vocabularies
   this project documents in `docs/STANDARDS.md`:
   - `taxonomy.owasp_llm`: `^LLM(0[1-9]|10):2026$` (OWASP Top 10 for LLM
     Applications 2026; the 2025 edition is superseded, F-5);
   - `taxonomy.saif`: the 15 saif-data risk ids at commit `fe77c44`;
   - `taxonomy.atlas`: `^AML\.T[0-9]{4}(\.[0-9]{3})?$` (ATLAS 5.6.0).
   Empty and absent stay legal everywhere: the patterns constrain the
   SHAPE of what is claimed and never require a claim.
4. `$defs.taxonomy_entry` is replaced by three per-vocabulary entry
   definitions. Entry shape is unchanged (`id`, `status` in
   `confirmed | suggested`).

**Why minor, not major:** charter section 7 says adding a field is a
minor bump; changing or removing one is major. Nothing was removed and
nothing new is required. The patterns tighten what an existing field
accepts, which is the one debatable point: a 0.4.0 record carrying a
free-text owasp id (say `LLM01`) is REFUSED by 0.5.0 with
`schema-invalid` at `$.taxonomy.owasp_llm[0].id`. Ruled acceptable
because no production store exists (D-052's trigger has not fired) and
because a silently accepted stale id is the drift the pin exists to
stop. If a store with pre-0.5.0 taxonomy claims ever appears, re-tagging
is a human act at the gate under a supersession event (D-051), never a
script.

**Migrating existing records:** a 0.4.0 finding becomes 0.5.0 by setting
`schema_version` to `"0.5.0"`; `taxonomy.atlas` and `remediation` may be
omitted (the adapters now emit `[]` and `null` explicitly). Any existing
`taxonomy.owasp_llm` id must be re-expressed in the `LLMnn:2026` form,
and any `taxonomy.saif` id in the saif-data vocabulary, by a human.
`schema_version` is inside the hashed content, so this changes content
hashes and ids, which is what the supersession mechanism is for. No
production store exists; no migration was run.

**What moved in the tree, same commit:** `field_map.json` gained rows
`taxonomy.atlas` and `remediation` and its `canonical_schema_version`
(the drift test fires otherwise); both in-adapters emit the two new
fields; both fixtures carry `0.5.0` and pinned ids (`LLM01:2026`, `PIJ`,
`AML.T0051`); the README badge and its truth test; `docs/STANDARDS.md`.
Controls in `tests/test_schema_0_5_0.py`: each pattern refuses and
accepts, empty and absent are legal, remediation accepts only string or
null, adapters never emit a claim.

**Stated limit:** no CLI writes `remediation` or `taxonomy.atlas` yet.
That is the same limit `severity.rationale` has had since 0.1.0: the
fields exist so the record can carry what the standards expect a finding
to document; the gate's editing surface is a later phase.
