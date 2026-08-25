# Showcase screenshots

Rules (STEP-06 contract, DEV-18): a screenshot here proves one claim
that text cannot prove. Each PNG is under 200 KB, the total stays in
single digits, each is named for the claim it proves, and each caption
points at the committed artifact or transcript that is the real proof.
A screenshot that proves nothing specific is not committed.

Text already proves most of this project: the transcripts under
`examples/*/output/` are the evidence for every command. Three things
only a picture shows are listed below. Each is a GUI capture for the
DIRECTOR to take; the builder verifies the file landed and is referenced
here.

## Planned captures

| File | Claim it proves | Real proof it points at | When | Capture instructions (director) |
|---|---|---|---|---|
| `01-sarif-viewer-render.png` | the emitted SARIF renders as findings in a real SARIF consumer, with the disambiguation text visible | `examples/01-garak-triage/output/findings.sarif` | stop one (available now) | In VS Code, install the Microsoft "SARIF Viewer" extension. Open the repo folder. Open `examples/01-garak-triage/output/findings.sarif`; the viewer opens automatically (or run "SARIF: Show Panel"). Expand the one result so the message and the location (`findings.fb.jsonl`, line 1) are visible. Capture the panel only, not the whole screen. Save as PNG; if over 200 KB, crop tighter. |
| `02-ci-green-both-oses.png` | the gate workflow ran green on ubuntu and windows, both Python versions, in one run | the workflow run URL, recorded in `evidence/` at stop two | stop two (after gate.yml has run) | On GitHub, Actions tab, open the first green run of `gate.yml`. Capture the run summary showing all four matrix jobs green and the job names. Crop to the jobs list. |
| `03-code-scanning-alert.png` | GitHub Code Scanning ingested our own SARIF and shows a finding-bridge alert (OB-7) | the code-scanning upload run URL, recorded at the flip | after the flip only (W8; optional, the director's call) | On GitHub, Security tab, Code scanning alerts, open the alert from the finding-bridge upload. Capture the alert header and the location line. |

## Landed

None yet. This table is filled in by the builder, one row per file,
with the byte size, as each capture arrives.

| File | Bytes | Referenced from |
|---|---|---|
