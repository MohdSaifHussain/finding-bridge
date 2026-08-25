# D-090 currency check: first runs (2026-08-25)

Both dispatched from the same commit (f723daa), both success, both on
ubuntu-latest, log lines quoted from the runs.

Positive control, run 32852502075 (`test_mode=0.15.0`, dry run):
```
currency selftest: ok (pin parsed; duplicate detector discriminates by version)
garak: pinned 0.15.0, latest 0.16.0 (github-releases): WOULD-OPEN
standards: OWASP Top 10 for LLM Applications: pinned 2026, observed 2026: current
standards: MITRE ATLAS: pinned 5.6.0, observed 5.6.0: current
```
The issue path CAN fire; dry run created nothing (open currency issues: 0).

Real check, run 32852514642:
```
garak: pinned 0.16.0, latest 0.16.0 (github-releases): current
standards: OWASP Top 10 for LLM Applications: pinned 2026, observed 2026: current
standards: MITRE ATLAS: pinned 5.6.0, observed 5.6.0: current
manually-checked-only: OWASP GenAI Red Teaming Guide; Google SAIF; NIST AI 600-1 (D-076)
```
Nothing due; nothing opened. Negative control on the duplicate path:
the selftest proves the detector discriminates by version; the live
"already-open" branch is exercised the first time a real issue exists
and the weekly run repeats (recorded as the one branch not yet observed
live).

Next scheduled run: Mondays 06:17 UTC.
