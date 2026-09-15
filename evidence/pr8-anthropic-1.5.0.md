# PR #8, anthropic 1.3.0 to 1.5.0, evidence (2026-09-16, D-096)

Dependabot PR #8 changes one line: the optional `ai` extra's pin in
`pyproject.toml`. Its five CI checks were green, but no CI job installs
anthropic: `gate.yml` installs `.[dev]`, the AI tests stub the client, and
the Dockerfile installs with `--no-deps` from `constraints.txt`, which has
no anthropic. So the green checks proved only that `pyproject.toml` still
parses. This file is the check that did install it.

## Sources

- PyPI JSON for anthropic 1.3.0 and 1.5.0: both `requires_python >=3.10`,
  the same runtime dependency list (`anyio`, `docstring-parser`, `httpx2`,
  `jiter`, `pydantic`, `sniffio`, `typing-extensions`).
- The 1.4.0 and 1.5.0 release notes
  (https://github.com/anthropics/anthropic-sdk-python/releases): no
  breaking change listed for the two calls finding-bridge makes,
  `Anthropic()` and `client.messages.create(...)`.

## Local check, Python 3.14.0 (ruled: 3.14 only)

A worktree of the PR head `1afcff1` and a fresh venv with
`pip install -e ".[dev,ai]"`:

```
anthropic 1.5.0 installed; pip check: no broken requirements
finding_bridge imported from the PR worktree's src/
python tools/gate.py        GATE: PASS (pytest 356 passed, 1 skipped; ruff check clean; ruff format clean)
python -m pytest -q         356 passed, 1 skipped (no API keys)
```

Controls against the real 1.5.0 package, no network call:

```
PASS  anthropic version is 1.5.0
PASS  no key refuses with ai-key-missing
PASS  no model refuses with ai-unavailable
PASS  dummy key builds anthropic.Anthropic
PASS  client exposes messages.create
PASS  Message content blocks give .type and .text as _ask reads them: 'hello world'
6/6 passed
```

## Merge

Merged as a merge commit (`9588940`, 2026-09-15T21:45:14Z) with
`--match-head-commit` set to the tested head, so GitHub would have refused
if the branch had moved. CI on `9588940`: `gate` success (run
35027374063), `container` success (run 35027374035), Dependency Graph
success (run 35027378346).

## Limits

No real API call was made: it needs a key and sends data out. The
`messages.create` path against 1.5.0 is covered by the release notes and
by the type-level check above, not by a live call. Python 3.12 was not
exercised locally (not installed); anthropic 1.5.0 declares Python 3.10
and newer.

## Found on the way

The fresh venv resolved ruff 0.16.7, while the main environment has ruff
0.15.20. ruff 0.16.0 (release notes, 2026-07-23): "Ruff can now format
Python code blocks in Markdown files and will do this by default." So the
gate's `ruff format --check .` covers about 71 Markdown files as well as
74 Python files wherever ruff is fresh, CI included. Everything passes.
The `dev` extra says `ruff>=0.6` with no upper bound, so the gate's scope
changed with an upstream release and no ruling. Recorded, not changed.
