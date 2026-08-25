# finding-bridge packet

1 confirmed finding(s). Sealed content is stored encrypted and referenced, never inlined.

## Finding fb-20727861f31c334a

- Source tool: manual-transcript (version unknown)
- Target model: synthetic-model (version unknown)
- Discovered at: unknown
- Harm flags: none recorded
- Severity score: unknown (unknown); rubric E/I/D/E: unknown/unknown/unknown/unknown

### Taxonomy
- none recorded

### Preview (sealed content is never emitted)

> [sealed content: 43 chars, 1 lines, keyed digest ccef321e; harm flags: none recorded. Content is sealed; unseal is explicit and logged.]

Sealed references: probe sealed/8a68ddf1b216902d, response sealed/ccef321e17787290. Unsealing is explicit and logged.

### Reproduction
1. Replay the captured 5-turn transcript against the target.

Environment: context_sealed_ref=sealed/91315e96d35fef68, turn_count=5

### Provenance
- Content hash: `20727861f31c334ac0440893a4abfda1539729aec7393dbedf0f30f9ae849595`
- Previous hash: `unknown`
- Confirmed by: MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com> at 2026-08-25T06:37:47.879130+00:00
- Attestation hash: `cd08a52a02e6053adb7a86c648db76d5b8abb35ff57202667fbb33c493feac71`

---

Tamper-evidence bound: the hash chain and its head detect accident, drift and casual edit; they do not defend against an attacker with write access to both the ledger and its head.
