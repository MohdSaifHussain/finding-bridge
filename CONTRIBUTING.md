# Contributing

finding-bridge is built the governed way: a written phase contract
before any build, numbered rulings by the director, declared review
stops, controls that are red before they are green, and claims no wider
than their evidence. A contribution is welcome when it fits that shape.
The record of how the project works is `DECISIONS.md` and
`docs/decisions/`; read `CLAUDE.md` first.

## Before you open a pull request

- Run the gate: `python tools/gate.py --verdict-file verdict.txt` and
  read the verdict file. Never pipe the gate (D-074).
- Every new behaviour ships with a test; every safety-relevant behaviour
  ships with a negative control that was observed red before the fix
  and a positive control (skill rule 5). Say in the PR which test was red.
- Never weaken or skip a safety test to get green. Fix the code.
- Fixtures are synthetic with `SENTINEL-*` stand-ins; no real harmful
  model output enters this repository in any form (D-012;
  `tools/fixture_scan.py` refuses it).
- Refusals name a location, never a value (D-036).
- Adapters are pure translation: no sealing, hashing, or confirmation
  outside `core/`.
- Docs obey the wording law (D-042): "sealed, with a safe metadata
  preview"; the tamper-evidence bound stated wherever the guarantee is;
  nothing promised that is not shipped. `tests/test_no_overclaim.py`
  enforces it.
- A process claim ("I ran X for all Y") names the check that enforces
  it or carries the word unchecked (D-057).

## What a pull request needs

The PR template's checklist is the definition of done from `CLAUDE.md`.
Product-code changes beyond a fix with controls need a director's
ruling first: open an issue describing the finding, its evidence, and a
proposal, and wait for the numbered decision.

## Reporting a security problem

`SECURITY.md`. Do not paste harmful model output into an issue.
