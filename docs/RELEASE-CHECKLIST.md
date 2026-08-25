# Release checklist, v1.0.0

Every row names the check that decides it. A row is green only when its
check has been run and its result recorded; "clicked" is not "confirmed".
Rows marked FLIP happen on the director's one-line word and not
otherwise; nothing here performs the flip.

## Before the flip (builder, then the director's STOP THREE read)

| # | Row | Check | Result |
|---|---|---|---|
| 1 | Version is 1.0.0 everywhere | `tests/test_release_labels.py` (pyproject == package == SARIF driver) | green, 2026-08-25 |
| 2 | Gate green locally | `python tools/gate.py --verdict-file` | GATE: PASS, 2026-08-25 |
| 3 | Gate green on CI, both OSes, both Pythons | the `gate` runs on the release commit, four jobs | pending the W7 push |
| 4 | Container built, scanned, smoked, pushed private | the `container` run on the release commit | pending the W7 push |
| 5 | Fresh-wheel proof with the hash lock | the gate's fresh-wheel step; `tools/lock.py --check` | lock IN SYNC 2026-08-25; CI pending |
| 6 | CHANGELOG has one 1.0.0 entry in Keep a Changelog form | `tests/test_no_overclaim.py` scans it (D-046); read by eye | written 2026-08-25 |
| 7 | Every user doc passes the wording law | `tests/test_no_overclaim.py` over README, USAGE, SOP, STANDARDS, showcase, examples, CHANGELOG, SECURITY | green, 2026-08-25 |
| 8 | Badges are true | `tests/test_readme_badges.py` | green |
| 9 | Fixtures and example outputs carry no harm | `tools/fixture_scan.py` | CONFORMING (10 fixtures, 18 outputs), 2026-08-25 |
| 10 | Committed real-data artifacts carry no real string | `tools/realdata_leak_scan.py` (needs the local data) | CLEAN x3 (two by the director), 2026-08-25 |
| 11 | Examples equal a fresh run modulo the volatile list | `python examples/run_example.py --all --check` | SAME x4, 2026-08-25 |
| 12 | Full-history audit: no secret, no local path, no key/store/real-data file, uniform identity | `evidence/pre-public-audit-step06.md` | clean, 111 commits / 451 blobs, 2026-08-25 |
| 13 | The 38,358-byte wheel blob in history is known and named | `git rev-list --objects --all | grep .whl` | one blob, D-058, named in the release notes |
| 14 | License and NOTICE present and named in the wheel | `LICENSE`, `NOTICE`; wheel metadata `License-Expression: Apache-2.0` (D-048) | verified 2026-08-25 |
| 15 | OB-7 prepared: informationUri wired, SARIF2005 gone | `tests/test_release_labels.py`; `tests_audit/test_sarif_multitool.py` (warning set empty) | green, 2026-08-25 |
| 16 | Dependabot alerts and automated security fixes ON, API-verified | `gh api repos/.../vulnerability-alerts` returns 204; `automated-security-fixes` enabled=true | verified 2026-08-25 |
| 17 | Standards pins re-checked for a newer edition within days of the flip (D-076) | re-fetch the five sources' index pages; update `docs/STANDARDS.md` rows' "successor last checked" dates | pending: run on flip day |
| 18 | Release notes drafted with the two ruled numbers, each naming its check | `docs/RELEASE-NOTES-1.0.0.md` | drafted 2026-08-25 |
| 19 | Pre-push delta audit on the release push | the standard delta audit | pending the W7 push |
| 20 | Director's STOP THREE read | by hand | pending |

## At the flip (director's word; then the builder verifies each by API)

| # | Row | Check |
|---|---|---|
| F1 | Repository visibility public and package visibility public, one ruling | `gh repo view --json visibility`; `gh api user/packages/container/finding-bridge` visibility |
| F2 | Branch-protection ruleset on master: block force-push and deletion, require the four gate checks; single-operator admin bypass recorded | `gh api repos/.../rulesets` (rulesets need Pro or a public repo: 403 while private, so this row runs immediately after F1; the precondition, gate.yml having run, is already met) |
| F3 | Secret scanning and push protection enabled | `gh api repos/... --jq .security_and_analysis` |
| F4 | Private vulnerability reporting enabled | `gh api repos/.../private-vulnerability-reporting` |
| F5 | Tag v1.0.0 on the release commit, GitHub Release published from the drafted notes | `git tag -v` / `gh release view v1.0.0` |
| F6 | OB-7 verified: informationUri resolves; optional code-scanning ingestion of our own SARIF | `curl -I` the URL; the code-scanning upload run |
| F7 | Row 17 (pins) done on the day | `docs/STANDARDS.md` dates |
| F8 | Record closed: census, register, builder eval updated | `DECISIONS.md`, `docs/RULE-CENSUS.md`, `evidence/builder-eval-step06.md` |
