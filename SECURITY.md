# Security policy

## Reporting a vulnerability

Use GitHub's private vulnerability reporting for this repository
(Security tab, "Report a vulnerability"), which is enabled at the flip to
public and listed as a row in the release checklist. Do not open a public
issue for a security problem, and do not put harmful model output in a
report: describe the shape and the location, the way this tool's own
refusals do.

## What is in scope

- Anything that lets sealed content reach an emitted artifact, stdout,
  a log, or an error message without an explicit `unseal`.
- Anything that lets a stored finding's evidence change without `verify`
  refusing, within the stated bound below.
- Anything that lets the caged `--ai` path write to a finding, or lets the
  pipeline depend on an API key.
- Anything that puts key material inside the repository tree, the
  container image, or a committed artifact.
- Parser crashes (raw tracebacks) on untrusted input: every refusal is
  meant to carry a reason code and a location, never a value.

## What is a stated limit, not a vulnerability

The README's "Honest limits" and `docs/USAGE.md#limits` list what the tool
does not do. The ones most often mistaken for findings:

- Tamper-evidence is bounded: the chain and its head detect accident,
  drift and casual edit; they do not defend against an attacker with
  write access to both the ledger and its head at once (OB-4, open until a
  store crosses a trust boundary).
- The preview is metadata, not a summary.
- Finding ids are store-local; dedup is exact-match; inputs are capped at
  10 MiB; the reference key does not rotate.
- On Windows the key file's permissions are the operator's job (`icacls`).

If your report is one of these, it is still welcome as an issue if you
think the limit is wrong or badly stated; it is not a vulnerability.

## What to expect

This project has one operator, its director, and no security team. The
honest response expectation: an acknowledgement within seven days, a
fix or a stated-limit ruling recorded in `DECISIONS.md` when one exists,
and no guaranteed timeline beyond that. Every fix ships with a control
that was red before it and a correction row if a published claim was
wrong.

## Supported versions

| Version | Supported |
|---|---|
| 1.0.x | yes |
| earlier | no (pre-release, never published) |
