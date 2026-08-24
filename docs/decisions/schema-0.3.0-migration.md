# Schema migration note: 0.2.0 to 0.3.0

**Change:** `discovered_at` type `"string"` becomes `["string", "null"]`.
Everything else is unchanged; no keys were added or removed (the mapping
table is unaffected except its version pin).

**Why (D-024):** the garak hitlog format carries no timestamp field
(verified against NVIDIA/garak `garak/evaluators/base.py`, fetched
2026-08-24; hitlog records contain goal, prompt, output, triggers, score,
run_id, attempt_id, attempt_seq, attempt_idx, generator, probe, detector,
generations_per_prompt). The charter forbids inventing values for missing
source fields, so the honest representation of a garak finding's discovery
time is null.

**Versioning reading:** charter §7 calls a field change a major bump. Within
pre-1.0 development this lands on the 0.x minor position per semver's
initial-development convention (0.2.0 to 0.3.0), with this migration note
satisfying the charter's requirement. Jumping to 1.0.0 was rejected: it
would signal a stability the roadmap has not reached.

**Migrating existing records:** a 0.2.0 record is valid 0.3.0 unchanged
(the change only widens the type). A 0.3.0 record with null discovered_at is
NOT valid 0.2.0. Consumers pinned to 0.2.0 must treat null as absent.

**Fixtures:** both fixtures keep concrete timestamps; adapter tests cover
the null case.
