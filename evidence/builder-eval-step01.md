# Builder eval, STEP-01

Compiled 2026-08-24 against the ledger at commit `fa3eb53` (D-001 to D-024,
DEV-1 to DEV-3, C-001 to C-003, OB-1 to OB-4). **This is a self-evaluation:
the builder assigned the classes, chose what counts, and authored most of the
artifacts it classifies. Read the rates as "most were caught" figures, not
measurements.**

## Definitions

A defect is something wrong in an artifact (code, test, schema, doc, or a
claim about them), not a ruling, a scope decision, or a style preference.
Style-gate hits (import order, formatting) are listed but counted separately.
Finders: **B** = builder at build time or at the 4a self-review, **D** =
director's independent round-2 review, **T** = a gate/tool this project runs
(pytest, ruff, the sentinel control). "Escape" = reached the director's
review without the builder having found it.

## 1. Substantive defects, one line each

| # | Defect | Found by | Escape? |
|---|---|---|---|
| 1 | Gate record not tamper-evident (confirmed_by editable, chain clean) | B found the laundering subset; **D found the load-bearing core (R-1)** | partial escape |
| 2 | Tail truncation invisible to verify_chain (R-2) | D | escape |
| 3 | Plaintext-derived digests: refs (B, #2) + preview digest (**D extension**, R-3) | B+D | partial escape |
| 4 | Ref handling: matches[0] ambiguity (B, #3) + glob/traversal injection (**D**, R-4) | B+D | partial escape |
| 5 | Canonical JSON diverges from RFC 8785, undeclared (R-5) | D | escape |
| 6 | No key rotation path; Fernet token timestamp leak unrecorded (R-6) | D | escape |
| 7 | Key file written with default permissions (my #5 = R-7) | B and D independently | no |
| 8 | dedup canonical_ids None for unstamped findings (R-8) | D | escape |
| 9 | 64-bit id truncation nowhere stated as a limit (R-9) | D | escape |
| 10 | Env-key scrub was an ad hoc run, not a suite property (R-10) | D | escape |
| 11 | Exposure log could not distinguish failed from successful unseal (#4) | B | no |
| 12 | format annotation-only: provenance timestamps unvalidated (#6) | B | no |
| 13 | R-8 negative control modeled nothing (fixture already had an id) | T (pytest), after a premature commit | no (caught in-session) |
| 14 | Commit `a9251d4` landed with a failing test: gate run and commit chained in one command | B (self-caught on reading the output) | no |
| 15 | garak goal/triggers passed harmful-capable text in the clear to packets | T+B (sentinel control fired on the fixture) | no |

Style-gate hits, counted separately: 3 (ruff import order x2, format x1), all
found by T.

## 2. Rates, with denominators

- Substantive defects: **15**. Fully escaped to the director: **6** (rows 2,
  5, 6, 8, 9, 10) = **6/15 = 40%**. Counting the three partial escapes (rows
  1, 3, 4) as escapes: **9/15 = 60%**. Both stated; the honest headline is
  the ambiguous band **40-60%**, and the load-bearing half of row 1 escaping
  weighs heavier than the fraction shows.
- Of the director's 10 findings, fully absent from the builder's 4a review:
  **6/10**; partially present: 3/10; independently duplicated: 1/10 (R-7).
- One defect moves the substantive escape rate by ~6.7 points (1/15).
- Builder self-caught before any review: rows 11-15 plus the found halves of
  1, 3, 4 (and 7 jointly).

## 3. Two-sided accounting

- Builder escapes caught by the director: 6 full + 3 partial (above).
- Director escapes caught by the builder: 2, both precision not substance:
  C-002 (R-1 framed the exclusion as the defect; the missing guard was) and
  C-003 (R-10's "claimed, not demonstrated" was wider than the evidence),
  the second accepted only with citation because it flattered the builder.
- Tool catches with no human: rows 13, 15, and the 3 style hits. Row 15 is
  the phase's best evidence that the sentinel control can fail loudly: it
  fired on content the builder had not considered harmful-capable.

## 4. Debits before credits

The builder shipped a review-stop report calling the core proven while rows
1-10 stood in it; certified row 1's hole with a passing test; committed once
with a red suite (row 14); wrote one negative control that tested nothing
(row 13); and its committed 4a report contains a count whose parenthetical
lists seven items under "6 of 10" (see §7). The credits (reds captured
before every fix, the truncation live demo, two upheld precision notes) come
after those debits.

## 5. Repeat-class analysis

Two classes recurred: **silence-shaped failures** (rows 2, 10, 12 - things
that pass because nothing checks) and **content-derived identifiers leaking**
(rows 3, 15). The instruments built this phase target exactly these: format
assertion, suite-property scrub, head commitment, keyed digests, sentinel
controls. Whether they generalize is untested beyond this phase.

## 6. What this phase changed about the builder's method

Tools, not habits: the drift test (fired twice for real), the gate-field
static guard, the env-scrub guard, the sentinel controls. One habit change
with no tool yet: never chain a gate run and a commit in one command (row
14); a checkable form would be a commit hook, not built, not promised.

## 7. Honest limits of this document

Classes and the defect/non-defect line are the builder's own. The
counterfactual "the director would not have found row N" is unmeasurable.
The committed 4a report (`evidence/step01-4a-self-review.md` §4) contains a
sloppy count: its parenthetical supporting "6 of 10" lists R-1's core plus
five others and then appends R-9, reading as seven items. Per the
dated-reading rule that document is not rewritten; the reconciled count is
the one in §2 above (6 full, 3 partial), and the discrepancy is recorded
here, direction: the original understated nothing but was ambiguous.
Everything after commit `fa3eb53` belongs to no eval.

## 8. The question for the next boundary

Of the instruments built this phase (drift test, static gate guard, env
guard, sentinel controls, head verification), how many fire on a defect in
the transcript-in / SARIF-out phase that no human review had already found?
If the answer is zero, they are decorations and the next eval must say so.
