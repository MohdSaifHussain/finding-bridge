# finding-bridge packet

1 confirmed finding(s). Sealed content is stored encrypted and referenced, never inlined.

## Finding fb-bd795cd3a724693b

- Source tool: manual-transcript (version unknown)
- Target model: synthetic-model (version unknown)
- Discovered at: unknown
- Harm flags: none recorded
- Severity score: unknown (unknown); rubric E/I/D/E: unknown/unknown/unknown/unknown

### Taxonomy
- none recorded

### Preview (sealed content is never emitted)

> [sealed content: 43 chars, 1 lines, keyed digest bb2dc792; harm flags: none recorded. Content is sealed; unseal is explicit and logged.]

Sealed references: probe sealed/3c41f87ef9d7fd32, response sealed/bb2dc792433b8cd6. Unsealing is explicit and logged.

### Reproduction
1. Replay the captured 5-turn transcript against the target.

Environment: context_sealed_ref=sealed/133636f521503be2, turn_count=5

### Provenance
- Content hash: `bd795cd3a724693ba0de85b3bd0f147d3a869b7345ff7a7c88084b305a7c9021`
- Previous hash: `unknown`
- Confirmed by: MohdSaifHussain <263689115+MohdSaifHussain@users.noreply.github.com> at 2026-08-25T07:06:40.292121+00:00
- Attestation hash: `56a4816aee13fdf67362bb9f988c24e376cb756f406ef25780cc3e786e742ebc`

---

Tamper-evidence bound: the hash chain and its head detect accident, drift and casual edit; they do not defend against an attacker with write access to both the ledger and its head.
