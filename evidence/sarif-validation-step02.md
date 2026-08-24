# SARIF dual-route validation evidence (STEP-02 D5, DEV-5/DEV-7)

Date 2026-08-24. Design-target consumer: GitHub Code Scanning (ingestion
deferred to OB-7). Director-verifiable consumer at close: VS Code SARIF
Viewer, run by hand in the ritual.

## Route 1: official OASIS schema (own check)

Vendored at schemas/sarif-schema-2.1.0.json from
docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/ (fetched
2026-08-24; declares draft-04, validated with jsonschema validator_for).
Positive: emitted SARIF from the fixture pipeline validates
(tests/test_sarif_adapter.py::test_sarif_passes_official_schema). Negative:
deleting "version" fails validation (test_own_validator_can_fail).

## Route 2: Microsoft SARIF Multitool

**Resolved and pinned version (DEV-7): @microsoft/sarif-multitool@5.6.0**
(npm view, 2026-08-24), invoked as
`npx --yes @microsoft/sarif-multitool@5.6.0 validate <file>`
(dotnet SDK absent on this machine; npm 11.18.0; R4 as amended).

Positive (observed): our emitted SARIF -> exit 0, "Analysis completed
successfully", no error lines.

Negative (observed) and a MEASURED LIMIT of the tool: fed `{not json`, the
Multitool prints
`error JSON0001: : JSON syntax error: Invalid character after parsing
property name...` **and still exits 0** ("Analysis completed
successfully"). It also silently accepts a version-less SARIF and a
runs-as-string SARIF (all probed 2026-08-24, exit 0 each). Its reliable
failure signal on this machine is the console `error JSON0001` line, not
the exit code, so the audit-cadence negative control
(tests_audit/test_sarif_multitool.py::test_multitool_flags_corrupted_input)
asserts on that text. Consequence recorded plainly: exit-code gating of
this validator is unreliable; any CI use must parse its output.

## Cadence

Multitool route runs at AUDIT cadence (tests_audit/), not GATE: npx
startup + network fetch per run, and the emitted SARIF changes only when
the adapter changes (D-032: a check belongs at the cadence of the thing it
guards). The own-schema route runs in GATE on every commit.
