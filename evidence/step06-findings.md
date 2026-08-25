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

## F-6: the documented hash-verified install route did not run (builder, W5 rehearsal; FIXED as a doc defect, DEV-19 rule 4)

Rehearsing gate.yml's fresh-wheel step locally on 2026-08-25:
`pip install dist/finding_bridge-0.1.0-py3-none-any.whl -c constraints.txt`
in a fresh venv fails: "Hashes are required in --require-hashes mode, but
they are missing from some requirements" (the wheel itself). Cause, from
pip's secure-installs guide (fetched 2026-08-25): once any requirement
has a hash, hashes become required for all. The STEP-04 proof
(evidence/fresh-venv-proof-step04.md) installed the wheel WITHOUT the
constraints file; the `-c constraints.txt` wheel command was written into
README and USAGE at D-050 and never run. D-057's class: "this is the
route we test" named no check, and it was not tested.

Fix, executed before written: constraints.txt is now a full runtime lock
(11 packages, 278 hashes from PyPI's JSON API), the route is
`pip install --require-hashes -r constraints.txt` then
`pip install --no-deps <wheel>`, rehearsed in a fresh venv (import from
site-packages, `pip check` clean, `finding-bridge --help`), with a
negative control: both rfc8785 hashes zeroed, pip refuses with the
mismatch named, exit 1. (A first negative control tampered ONE of the two
hashes and passed, because pip accepts a match on either; the control was
wrong, not the lock.) README and USAGE reworded (listed for the stop-two
report as rule-4 rephrasings), gate.yml and the Dockerfile use the route,
the overclaim check bans the broken form.
