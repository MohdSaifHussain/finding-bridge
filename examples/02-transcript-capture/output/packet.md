# finding-bridge packet

1 confirmed finding(s). Sealed content is stored encrypted and referenced, never inlined.

## Finding fb-2ca4ee930b9e9bb1

- Source tool: manual-transcript (version unknown)
- Target model: synthetic-model (version unknown)
- Discovered at: unknown
- Harm flags: none recorded
- Severity score: unknown (unknown); rubric E/I/D/E: unknown/unknown/unknown/unknown

### Taxonomy
- none recorded

### Preview (sealed content is never emitted)

> [sealed content: 43 chars, 1 lines, keyed digest 4af2f6e4; harm flags: none recorded. Content is sealed; unseal is explicit and logged.]

Sealed references: probe sealed/a917c6af42eb0557, response sealed/4af2f6e4cd8d1099. Unsealing is explicit and logged.

### Reproduction
1. Replay the captured 5-turn transcript against the target.

Environment: context_sealed_ref=sealed/a564f745a06fed87, grammar=user-assistant, turn_count=5

### Provenance
- Content hash: `2ca4ee930b9e9bb1b17183d961195b590417e8e65a1451f50b9bad9175dd62d1`
- Previous hash: `unknown`
- Confirmed by: MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com> at 2026-08-25T09:41:04.693210+00:00
- Attestation hash: `2e1000df43508045ee47daed46e1e297f618f10a24e2dccc36710b7772a10e03`

---

Tamper-evidence bound: the hash chain and its head detect accident, drift and casual edit; they do not defend against an attacker with write access to both the ledger and its head.
