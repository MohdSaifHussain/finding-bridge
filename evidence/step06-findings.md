# STEP-06 findings for the stop-one ruling

Contract 3.1: a defect a document or workflow exposes is reported, not
fixed. Each finding quotes what was run and what came back.

## F-1: workspace-setup tracebacks (FIXED by explicit ruling, D-069, DEV-20)

Captured while running the five-minute tour with an empty `$TMPDIR`:
`--store /tour-store` resolved to `C:\Program Files\Git	our-store` and
`Workspace.__init__` died with `PermissionError: [WinError 5]`. A `--key`
path whose parent is a file died with `FileExistsError`. The director
ruled both fixed now; controls red then green; see D-069.

## F-2: three of four emitters crash after any key rotation (OPEN, for ruling)

Found by the rotation drill (examples/03-rotation-drill) when it tried to
emit a packet after rotating. Re-measured on a fresh scratch store on
2026-08-25: ingest the synthetic hitlog, confirm one finding,
`rotate-key --reason x`, then each emitter:

| Command | Result |
|---|---|
| `emit-markdown` | `KeyError: 'severity'` raw traceback, exit 1 (adapters/out/markdown.py:47 `severity = finding["severity"]`) |
| `emit-sarif` | `KeyError: 'taxonomy'` raw traceback, exit 1 |
| `emit-tracker` | wrote 1 issue, exit 0 |
| `emit-flare` | `KeyError: 'severity'` raw traceback, exit 1 |

**Cause, from the code:** `Workspace.confirmed_findings()` (pipeline.py:206)
returns every ledger row, and after a rotation the ledger holds a
supersession record beside the findings. The tracker adapter skips rows
whose `record_type` is `supersession` (tracker.py:131, D-063); the three
older adapters predate supersession records and index fields a
supersession record does not have.

**Why nothing caught it:** the OB-2 phase's controls (D-064) verified the
chain across the join and unsealed after rotation; nobody emitted after
rotating. The four adapter test files each build their own findings list
and never pass a ledger that contains a supersession record. This is the
exception-escapes-as-traceback class (D-036), eighth instance, on the
emit path after a lifecycle event.

**Proposal (not applied):** filter supersession records ONCE in
`confirmed_findings()` (or a sibling that emitters call), so every
present and future emitter inherits the rule instead of each adapter
re-learning D-063; keep the tracker's own skip as belt and braces; add a
control per emitter: ledger with a supersession record emits the
findings only, red before the fix. FULL tier (identity-adjacent ledger
read path). Product-code change: Section C, needs the director's word.

**Effect on this arc's documents until ruled:** the rotation drill does
not emit after rotating, and says why in its README; the SOP's rotation
procedure carries the limit in its own text.

## F-3: no schema field for MITRE ATLAS technique ids (OPEN, for ruling)

Raised by docs/STANDARDS.md with the proposal (taxonomy.atlas, schema
0.5.0, two field-map rows). Nothing applied.

## F-4: taxonomy ids are unconstrained strings; the version pin is prose (OPEN, for ruling)

Raised by docs/STANDARDS.md with the proposal (pattern constraints so a
stale or misspelled id refuses with schema-invalid). Nothing applied.

## Q-1: no remediation field (question, not a finding)

Raised by docs/STANDARDS.md; no proposal, the director's call.

## F-5: the OWASP pin was stale (director's finding, corrected, D-076)

STANDARDS.md pinned the 2025 edition as current on 2026-08-25; the 2026
edition had been published 2026-08-03. Re-fetched from OWASP (page and
PDF), re-pinned, 2025 row kept as superseded, delta stated. Finder: the
director, from outside the record. Builder's failure class, named: I
pinned what I fetched without asking whether it was the latest.
