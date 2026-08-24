# Fresh-venv install proof (STEP-04 W2c)

Date 2026-08-25. Goal: prove the package installs and works outside the
source tree. Installability only. Nothing published, no remote.

## Steps run

```
python -m build --wheel                      # -> dist/finding_bridge-0.1.0-py3-none-any.whl
python -m venv %TEMP%\fb-venv-proof
%TEMP%\fb-venv-proof\Scripts\python.exe -m pip install dist\finding_bridge-0.1.0-py3-none-any.whl
%TEMP%\fb-venv-proof\Scripts\python.exe -m pip install pytest hypothesis jsonschema
```

Tests were copied to a work directory outside the repo, then run with the
venv's Python.

## Observed

- Wheel contains the package data:
  `finding_bridge/schemas/field_map.json`,
  `finding_bridge/schemas/finding.schema.json`.
- Wheel declares the console script:
  `finding-bridge = finding_bridge.cli:main`.
- `finding-bridge --help` runs in the venv.
- Import location control (`FB_EXPECT_INSTALLED=1`):
  `finding_bridge imported from: ...\fb-venv-proof\Lib\site-packages\finding_bridge\__init__.py`
- Suite from the work directory: **203 passed, 1 skipped**.
  (Three more than the repo run: the repo's own audit-config guard rows
  do not apply outside the repo, and the doc files were copied in.)

## One real constraint found

`pip install . -c constraints.txt` fails: pip refuses hash-checking mode
for a local directory ("Can't verify hashes for these file://
requirements because they point to directories"). Building a wheel first
is the correct route, and it is also the better proof, because it tests
the artifact a user would receive.

## Limit resolved

The old "schema is a repo file" limit is closed. Schemas now ship as
package data and load through `importlib.resources`, so a wheel install
carries them.
