# The rule census (D-068)

**Status: DRAFT for the director's ruling. STANDARD tier, one stop, which
is this document.**

Every standing rule in this project, classified:

- **CHECK** — a tool or test fires when it is violated. Breaking it is
  visible without anyone remembering it.
- **HABIT** — a human or the builder must remember it. Nothing fires.
- **SENTENCE** — recorded, enforced by nothing, and in some cases
  correctly so.

The urgency is measured, not asserted: D-062 was broken within minutes of
being ruled, by the mechanism it names; the comparison-weakening class was
recreated by fresh code after a test had "fixed" it. Meanwhile six of nine
defects in STEP-05 were caught by machinery. **Rules did not prevent their
own class twice in one arc; instruments caught most of what went wrong.**

Inventory: 68 numbered decisions, 26 test files, 30 reason codes, 1 tool.

---

## 1. Safety rules (the charter's spine)

| Rule | Class | Enforcement |
|---|---|---|
| Deterministic core: no AI in the evidence path | **CHECK** | `test_ai_caged.py` runs the whole pipeline in a subprocess and inspects `sys.modules`; `finding_bridge.ai` must be absent |
| Zero API keys required | **CHECK** | `conftest.py` autouse scrub + `test_environment.py` guard, with a negative control |
| Sealing on by default | **CHECK** | sentinel-absence tests on every emitter, each with a positive control |
| Nothing confirmed without a human | **CHECK** | `test_gate_guard.py` AST-scans `src/` for any write of `confirmed_by` outside `core/provenance.py` |
| Identity from git config, never a fallback | **CHECK** | `gate.py` refuses `identity-missing`; tested both directions |
| Never fabricate absent values | **PARTIAL CHECK** | per-adapter tests assert nulls stay null; no general check that a NEW adapter cannot invent |
| Key never inside the repo | **CHECK** | `key-inside-repo` refusal + test; fired on its own author during W2 |
| Unsealing explicit and logged | **CHECK** | two-row exposure protocol, controls both directions |
| D-012: no real harmful content, ever | **SENTENCE** | nothing scans fixtures for real harm. *Correctly a sentence?* Arguably not — see proposal C1 |

## 2. Rules that failed and became checks (the project's best pattern)

| Rule | Was | Now | Trigger |
|---|---|---|---|
| Refusals name location, not value (D-036) | HABIT | **CHECK** | no-echo sweep across every boundary row |
| Untrusted input surfaces a reason code | HABIT | **CHECK** | the boundary table, entry AND exit sides |
| Digest comparisons must not weaken (D-060) | HABIT (failed 3×) | **CHECK** | one helper + AST bypass scan; found a miss on its first run |
| Docs must not overclaim (D-042) | SENTENCE | **CHECK** | `test_no_overclaim.py`, banned list D-046 |
| Docs must not show broken commands (D-050) | — | **CHECK** | known-broken-command test |
| Schema and field map move together (D-003) | HABIT | **CHECK** | the drift test, fired twice for real |
| Audits must not race or leave mutants (D-067) | — | **CHECK** | `tools/audit_guard.py`, acquire/release + concurrency lock |

**This table is the thesis.** Seven rules that used to be prose are now
instruments, and each became one *after* it failed.

## 3. Rules that are still HABIT — and have already been broken

| Rule | Class | Times broken | What a check would cost |
|---|---|---|---|
| D-057: a process claim names its check or says "unchecked" | **HABIT** | 2 | Hard. "Did I actually do what I claimed" is not machine-decidable in general. **Correctly a sentence** for the general case; see C2 for the one checkable slice |
| D-062 / gate-half-run: never let a claim outlive a failed check | **HABIT** | **6** | **Cheap and now precisely known** — see C2 |
| D-061: ordered-check tests assert their own check's detail | **HABIT** | 1 | Moderate: an AST rule that a test asserting a shared reason code must also assert a detail substring. Worth it — see C3 |
| Never chain a gate run and a commit | **HABIT** | 2 | Same fix as C2 |
| Write files with the file tool, not heredocs | **HABIT** | **4 this arc** | Cheap — see C4 |
| Re-derive, never restate (skill rule 13) | **HABIT** | 2 (C-005 counts, C-007 is the director's) | Hard in general; the specific instances are already covered by C2 and the guard |
| PROV at the moment of temptation (D-043.1) | **HABIT** | 1 | Not checkable. **Correctly a sentence** |

## 4. Rules that are correctly SENTENCES

Recording these as sentences is a *disposition*, not a gap:

- **D-017**: a second core language needs a charter amendment. Nothing to
  check until someone tries; the rule exists to make the attempt visible.
- **D-018**: the external adapter pack's trust boundary. Constraints for
  a thing not built.
- **D-042's future half**: never claim the semantic summary until it
  ships. The banned-phrase check covers today's wording; the rule covers
  intent.
- **D-054 / D-056**: Option E parked, Option C closed with a reopening
  bar. Governance, not code.
- **D-066's precedent**: "a measure invented at the moment of reporting
  cannot settle its own claim." A judgement rule. Correctly prose.
- **Charter's "prefer less exposure"**: a tie-breaker for judgement calls.
  Not mechanizable, and mechanizing it would be worse.

## 5. Proposed new checks, with costs, for ruling

### C1 — Fixture harm scanner (~30 lines, GATE)
Scan every file under `schemas/fixtures/` for content that is NOT
sentinel-shaped. Today's fixtures use `SENTINEL-*` markers by convention;
the check makes the convention enforceable, so a future contributor
cannot paste a real jailbreak transcript into a fixture.
**Cost:** low. **Risk:** false positives on legitimately varied fixtures,
mitigated by an explicit allowlist. **Recommend: build.**

### C2 — The exit-code check (~20 lines, tooling)
The gate-half-run family's six instances share one mechanism, now pinned:
a failing command's exit code is masked, either by piping to `tail` (the
pipeline's exit status becomes tail's) or by newline-separating a script
from a `git commit` instead of `&&`.
**Proposed:** a `tools/gate.py` that runs pytest, both ruff halves, and
the audit guard, captures each exit code *unmasked*, and prints a single
`GATE: PASS/FAIL` line. Committing is then gated on that one word, and no
shell construct can hide a failure.
**Cost:** low. **Value:** the highest in this list — six instances, one
mechanism. **Recommend: build.**

### C3 — Ordered-check test linter (~40 lines, GATE)
An AST rule: a test that asserts a reason code which is raised at more
than one point in the same function must also assert a detail substring
(D-061).
**Cost:** moderate; needs a map of which codes are multiply-raised.
**Recommend: build, after C2.**

### C4 — Heredoc ban (~10 lines, advisory)
Four corruptions in one arc, each caught immediately by a syntax error,
so the *cost* of the class is low but non-zero. A check cannot see how a
file was written — but it *can* be a pre-commit scan for the signature
damage (a string literal containing a raw newline where an escape was
intended is usually a syntax error anyway).
**Assessment: NOT worth building.** The compiler already catches it
100% of the time, immediately. **Recommend: keep as habit, and record
that the decision was made deliberately.** This is a case where the honest
answer is "no check".

### C5 — Equivalence-claim register (~20 lines, AUDIT)
111 of 125 surviving mutants are dispositioned as equivalent by my
reasoning. Nothing checks those claims, and their share grows every arc.
**Proposed:** a machine-readable list of dispositioned mutants (module,
line, operator, reason) that the audit cross-references, so a survivor
that has NEVER been dispositioned fails the audit, and a disposition
whose line no longer exists is flagged as stale.
**Cost:** moderate. **Value:** converts the project's largest
reasoned-not-verified claim into a tracked one. **Recommend: build.**

## 6. The honest summary

- **CHECK: 16 rules.** Every one of the seven in section 2 became a check
  only after failing at least once — this project does not anticipate its
  classes, it converts them.
- **HABIT: 7 rules**, together broken **16 times**. Six of those are one
  mechanism (C2).
- **SENTENCE: 6 rules**, all judged correctly prose.

**The single finding:** the gate-half-run family is 6 of the 16 habit
breaches and has exactly one mechanical cause. **C2 alone would close
more of this project's recurring failure than every other proposal
combined.**

**The census's own limit:** I classified my own rules and counted my own
breaches. A rule I have forgotten entirely would not appear here, and
nothing in this document would reveal that.
