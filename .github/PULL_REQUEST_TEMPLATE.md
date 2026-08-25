## What and why

<!-- one paragraph; link the issue or the numbered ruling this implements -->

## Definition of done (CLAUDE.md)

- [ ] `python tools/gate.py --verdict-file verdict.txt` reads `GATE: PASS` (no API key set)
- [ ] New behaviour has tests; safety-relevant paths have a negative control that was RED before this change (name it)
- [ ] `ruff check` and `ruff format --check` clean
- [ ] The three core rules still hold; sealing still defaults on
- [ ] No new dependency on, or duplication of, an attack or aggregation tool
- [ ] Docs updated if behaviour or interface changed; wording law respected (D-042, `tests/test_no_overclaim.py`)
- [ ] Any process claim in this description names its check or says "unchecked" (D-057)
