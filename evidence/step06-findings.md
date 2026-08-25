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

## F-7: the dependency lock was incomplete on Python 3.12 (builder, local W6 build; FIXED)

The lock's versions were resolved in a Python 3.14 venv; the 3.12 image
exposed `typing-extensions>=4.4.0` (a conditional dependency of
`referencing`). Pinned for every Python. Evidence: evidence/w6-local-rehearsal.md.
Class: the resolving environment was not the target environment.

## F-8: the container image could not run the human gate (builder, local W6 smoke; FIXED)

`confirm` and `unseal` inside the image refused with `identity-missing:
git is not available`: the slim base has no git and the gate never falls
back to a default identity (D-011). git is now in the runtime stage;
the operator mounts a gitconfig read-only. Cost: image 53 MB to 88 MB,
stated. Class: a runtime dependency (git) that no test declares, because
every test machine has it.

## The first layer scan was blind (builder; replaced by tools/layer_scan.py)

Recorded in evidence/w6-local-rehearsal.md section 3: the shell scan
reported clean while its positive control reported SCAN BLIND. Not
believed; replaced by a tool with a selftest and a shape-precise marker.

## W6c real-data findings (2026-08-25), for ruling before W7

### F-10: the transcript grammar refuses the most common real-world marker form (limit, raised)

The Anthropic red-team-attempts transcripts (38,961 records) write turns
as `

Human:` / `

Assistant:` (counted over the whole file: 127,217
and 127,321 occurrences; zero `USER:`). The adapter's grammar is exact
uppercase `USER:`/`ASSISTANT:`/`SYSTEM:` at column 0 (D-041, D-049), and
`Assistant:` at column 0 is refused as a case variant. As shipped, not one
real transcript from the largest public red-team corpus ingests without
a rewrite. `examples/04-real-data/fetch.py` does that rewrite outside the
tree, and says so. Proposal for ruling: none applied; options are (a) a
documented pre-processing step (what example 04 does), (b) an explicit
`--markers human-assistant` flag choosing a second exact grammar (no
guessing, D-049 intact), (c) leave as a stated limit. (b) is a product
change, Section C.

### F-11: the transcript adapter has no home for per-record source metadata (limit, raised)

Each dataset record carries `rating`, `task_description`, `model_type`,
`num_params`, `red_team_member_id`, `tags`. The adapter accepts only
`--target-model`, `--target-model-version`, `--discovered-at`; the rest
has no field and is dropped before ingestion (not by the tool, which never
sees it). `reproduction.environment` carries only `turn_count`. Proposal:
an `--environment key=value` passthrough into `reproduction.environment`
(the garak adapter already stores run facts there). Section C.

### F-12: the garak adapter SILENTLY LOSES THE PROMPT on a real garak 0.16.0 hitlog (defect, raised)

Ingesting the real hitlog (197 hits, snapshot of the run in progress):
`probe.value` null and `probe.sealed_ref` empty on 197 of 197; the
response sealed on 197 of 197. Cause, from the data and the code: garak
0.16.0 writes `prompt` as a Conversation, `{"turns": [{"role": "user",
"content": {"text": ..., "lang": ..., "data_path": ..., ...}}], "notes":
{...}}` (every one of the 197 records has exactly that shape), while
`_extract_text` (adapters/in_/garak.py:44) descends into `turns` but
treats each turn as a Message: it looks for `text` on the turn itself and
never into the turn's `content` object, so the turn yields None and the
prompt becomes null. The synthetic fixture (built from the `main` branch
evaluator on 2026-08-24) carried the older Message shape, so every test
passed. This is silent field loss on the primary adapter's primary field:
the attack prompt, the thing a red-team finding is about. The response
survived because `output` is a Message with `text` at the top level.
Proposal: descend into a turn's `content` (Message) in `_extract_text`,
with a fixture line in the exact 0.16.0 shape (synthetic text, D-012) and
a control asserting the probe is sealed; keep the older shapes. Product
code, FULL (adapter feeding the seal path), Section C.

### F-13: fields the real hitlog carries that the adapter drops (limit, raised)

`output.lang`, `output.notes`, `output.data_path`, `output.data_type`,
`output.data_checksum`, and `prompt.notes` are not mapped. `goal` and
`triggers` ARE kept: both are sealed into the context blob (garak.py:103,
120). `triggers` was null on all 197 real hits. Stated as a limit; no
proposal beyond noting `lang` as the one with a natural home
(`reproduction.environment`).

### The real ingest, as it stood (counts only)

`{"ingested": 197, "total_candidates": 197, "duplicates_marked": 7}`;
detectors `mitigation.MitigationBypass` 107, `dan.DAN` 90; probes
`dan.Ablation_Dan_11_0` 196, `dan.AutoDANCached` 1; previews from 16 to
1,208 chars; target `ollama llama3.2:1b`. 7 exact-duplicate responses
across 197 hits from a 1B model under DAN ablations.

## W6c dispositions (D-079 to D-082)

F-12 FIXED FULL (both shapes, unrecognised shape refuses; controls red
first in tests/test_real_shapes.py; FIXTURE-VERSIONS.md check). F-10 FIXED
(`--grammar human-assistant`, exact, never auto-detected, mixing refuses).
F-11/F-13 FIXED by mapping into reproduction.environment, namespaced;
`notes` sealed as context. source_tool_version: stays null with the
reason stated (D-079 d). OB-5 open, narrowed.

## F-14: the SARIF driver advertised canonicalSchemaVersion 0.4.0 after 0.5.0 (W7; FIXED)

A hard-coded label no test tied to its source. Now reads the schema's
constant; tests/test_release_labels.py.

## F-15: code-scanning alerts do not render from our SARIF (found at the flip, D-086 F6; OPEN)

Upload accepted (analysis 1668515001, 1 result, 1 rule, no warning), 0
alerts. The result's artifact location is `findings.fb.jsonl` relative to
the SARIF's own folder (D-039.3), which GitHub resolves against the
repository root, where no such file exists. The D-033 assumption held for
ingestion, not for rendering. Proposal: an emit-time option to root the
artifact URI at a repository-relative path (or emit `originalUriBaseIds`);
owner the first post-launch phase. Not a release blocker: the SARIF is
valid and consumed; the alert view is the unserved half.
