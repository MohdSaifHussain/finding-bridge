# finding-bridge packet

1 confirmed finding(s). Sealed content is stored encrypted and referenced, never inlined.

## Finding fb-b1ed01896d82ccee

- Source tool: manual-transcript (version unknown)
- Target model: synthetic-model (version unknown)
- Discovered at: unknown
- Harm flags: none recorded
- Severity score: unknown (unknown); rubric E/I/D/E: unknown/unknown/unknown/unknown

### Taxonomy
- none recorded

### Preview (sealed content is never emitted)

> [sealed content: 43 chars, 1 lines, keyed digest 22392ff0; harm flags: none recorded. Content is sealed; unseal is explicit and logged.]

Sealed references: probe sealed/e478d9efae1c0bb7, response sealed/22392ff08267bf5c. Unsealing is explicit and logged.

### Reproduction
1. Replay the captured 5-turn transcript against the target.

Environment: context_sealed_ref=sealed/bc89f3a9caa95560, grammar=user-assistant, turn_count=5

### Provenance
- Content hash: `b1ed01896d82cceeb2ead7b284432d4ded21b969265676f761c4601b555e7c6d`
- Previous hash: `unknown`
- Confirmed by: MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com> at 2026-08-25T12:09:36.860305+00:00
- Attestation hash: `f6512443f6fd936f28cb4e7683626504a95096d71377103f75a9e65f474bccf4`

---

Tamper-evidence bound: the hash chain and its head detect accident, drift and casual edit; they do not defend against an attacker with write access to both the ledger and its head.
