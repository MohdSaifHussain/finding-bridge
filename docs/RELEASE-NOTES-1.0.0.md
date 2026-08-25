# finding-bridge 1.0.0 (draft release notes; published at the flip)

`pandoc` for AI red-team findings: ingest garak hitlogs and attack
transcripts, seal the harmful content by default, hash-chain the record,
gate every finding behind a human, and emit Markdown, SARIF 2.1.0,
tracker JSON, or a provisional FLARE-AI report set. No AI in the evidence
path; no API key needed, ever.

**AI-built, human-governed, every decision on the record.** Every line of
code was written by an AI under a human director who wrote none of it.
What makes the repository unusual is the apparatus around that fact,
measured in the README's provenance section.

## The two published numbers

- **349 tests: 261 exercise the product (74.8 percent), 88 exercise the
  governance instruments that keep the AI honest (25.2 percent).**
  Counted by node id from `python -m pytest --collect-only -q` at the
  release commit; the classification rule and file list are in the
  README's provenance section, and the badge-truth test
  (`tests/test_readme_badges.py`) keeps the badges honest.
- **Real-data validation: 739 of 739 real attack prompts and responses
  sealed, three independent real-string leak scans over the committed
  artifacts clean.** A real garak 0.16.0 run against llama3.2:1b (699
  hits) and 40 transcripts from Anthropic's red-team-attempts dataset
  went through the pipeline; `tools/realdata_leak_scan.py` sampled
  5,000 windows of the real text at run time and found none in anything
  committed, twice under the director's own hands. The data itself lives
  outside the tree and was never committed
  (`examples/04-real-data/`, `evidence/real-data-step06.md`).

## What real data found before release

The garak adapter had silently dropped the attack prompt on garak 0.16.0
hitlogs (699 of 699 hits) while every test passed, because the synthetic
fixture mimicked a shape the tool no longer writes. Fixed with both shapes
handled, an explicit refusal for unknown shapes, and a table recording
which tool version each fixture mimics. The duplicate count the bug had
inflated (253) was corrected to 62 and the correction is on the record
(C-011). Three emitters crashed after a key rotation; fixed. The
documented hash-verified install route had never run; replaced by a full
hash lock and pip's secure-installs route. The OWASP pin was a superseded
edition; re-pinned to 2026 with the delta stated.

## Honesty section

- The repository history carries one build artifact committed by mistake
  early on, a 38,358-byte wheel, caught and removed in the next commits
  and left in history on purpose: a provenance project does not rewrite
  its own history (D-058).
- Coverage-guided fuzzing (OB-5) is open: a 30-minute structured pass ran
  (11,063 inputs, zero escaped exceptions); the coverage-guided run waits
  for a Linux runner.
- The grey-scale preview design is research-informed, not research-proven
  (charter section 6).
- Limits, all of them: README "Honest limits" and `docs/USAGE.md#limits`.

## Install

```
pip install build
python -m build --wheel
pip install --require-hashes -r constraints.txt
pip install --no-deps dist/finding_bridge-1.0.0-py3-none-any.whl
```

Or the container: `ghcr.io/mohdsaifhussain/finding-bridge:1.0.0`
(digest-pinned base, non-root, key and gitconfig mounted from outside).

Full changelog: `CHANGELOG.md`. Full record: `DECISIONS.md`.
