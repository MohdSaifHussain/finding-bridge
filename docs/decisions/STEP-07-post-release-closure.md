# STEP-07: post-release closure (STANDARD)

**Project:** finding-bridge | **Phase:** 7 | **Date:** 2026-08-25
**Status:** RATIFIED from the director's word. Tier STANDARD (no
release act, no visibility change; three named items, nothing else in
scope). Sections B-G in force. One stop at the end.

## Deliverables

| ID | Deliverable | Standard |
|---|---|---|
| P1 | F-15: code-scanning alerts render from our SARIF. Fetch GitHub's official SARIF-support doc for artifact URI rules (uriBaseId / %SRCROOT%); fix the emitter; control red first; DEV-4's locationSemantics disambiguation survives; prove by re-uploading our own SARIF and capturing the RENDERED alert into docs/showcase/. Closes F-15 and OB-7's narrowing. | GitHub code-scanning SARIF support (fetched); SARIF 2.1.0 |
| P2 | OB-5: a workflow_dispatch-only fuzz workflow on ubuntu-latest with Atheris, 30-minute box in the workflow, both ingest parsers, seeded from the corpus shapes; report uploaded as a run artifact; run once now; rule discharged or narrowed on the run's evidence, not the workflow's existence. | D-027 audit cadence; Atheris official README |
| P3 | container.yml gains `on: push: tags: ['v*']` so the next release's :X.Y.Z tag comes from the workflow; verify it does NOT run on a plain push; the positive case waits for the next tag by design (no test tag on the public repo). | DEV-17 workflow details |
| P4 | GHCR package visibility public (the director's click), API-verified, F1 closed with timestamp. | D-086 |

## Requirements
- 3.1 Product code changes only inside P1 (the SARIF emitter's artifact
  location); any other defect is a finding.
- 3.2 No release act: no tag, no Release, no visibility change by the
  builder.
- 3.3 Claims at the width of the evidence: a rendered alert is a
  capture, a fuzz verdict is a read report.

## Stop
One stop at the end: the close report with the rendered-alert capture,
the fuzz run URL and verdict, the workflow diff, the visibility
verification, and the register after. Push under the standard delta
audit.

## Deviations
(none yet)
