# Builder eval, STEP-05

Compiled once at the arc-close commit. Counts from commands (D-031).
**Self-evaluation: the builder chose the classes.**

## 1. Substantive defects

| # | Defect | Found by | Escape? |
|---|---|---|---|
| 1 | The comparison-weakening class REPEATED in new supersession verify code, third occurrence | T (W1 mutation audit) | no |
| 2 | A kill test of mine passed for the WRONG REASON: it died at an earlier check than the one it named | T (the mutant stayed alive under a green test) | no |
| 3 | Two-rotation design bug: `old_head` compared against the epoch slice, not the running head, so a second rotation failed to verify | B (a test written for the audit) | no |
| 4 | Commit message claimed both docs updated for rotation; README was NOT - the edit script's anchor assert failed and I wrote the message anyway | B (self-caught, next report) | no |
| 5 | Commit message claimed C-007 recorded when the script had failed - **D-062's exact mechanism repeating within minutes of D-062 being ruled** | B (self-caught before the stop report) | no |
| 6 | `reproduction.steps` sent to the AI: adapter-authored prose that could carry probe text | T (the sentinel control, while W2 was written) | no |
| 7 | **A corrupted mutation measurement**: I launched a second audit while the first was still running; two processes raced one file, left live mutants in the tree, and produced a wrong number | B (read `git status`, not the run's own stale TREE-OK echo) | no |
| 8 | Heredoc `\n` collapse corrupting source, THREE times this arc (provenance, cli x2) | T (syntax error, immediately, each time) | no |
| 9 | An inline digest comparison the D-060 helper had missed, at provenance.py:351 | T (the new AST bypass check, on its first run) | no |

## 2. Rates, with denominators

Nine substantive defects. **Director escapes: 0.** Every one was caught by
the builder or by a tool the project runs, before the stop report.

That is the first arc with a zero escape count, and the honest reading is
not "the builder improved": it is that **six of the nine were caught by
machinery that did not exist three arcs ago** (the mutation audit, the
sentinel controls, the AST bypass check, the tree guard). The tools
caught what the builder does not.

## 3. Two-sided accounting

- Builder escapes caught by the director: 0 this arc.
- Director corrections caught by the same reviewer: 1 (C-007, the
  false-alarm id change, raised and killed by the director's own
  re-derivation).
- Tool catches with no human: rows 1, 2, 6, 8, 9.

## 4. Debits before credits

Row 5 is the worst thing in this arc: a rule was ruled, and the builder
broke it within minutes, by the same mechanism the rule describes. Row 7
is the most dangerous: a wrong number was produced and nearly reported,
and a mutated source file was nearly committed. Row 4 is the same family
again. Three instances of the heredoc hazard in one arc (row 8) is a
habit that has now cost more than a tool would have.

Credits after: the D-060 helper closed a three-time class in code and its
bypass check found a miss on its first run; the two-rotation bug was found
by writing a test for a case nobody had asked for; and both metric
artifacts (the schema drop at STEP-04, the annotation drop here) were
investigated rather than reported as regressions.

## 5. Repeat-class analysis

- **Gate-half-run / claim-ignores-failed-check**: instances 4 and 5 this
  arc; five lifetime. D-057 and D-062 are both rules, neither is a check.
  The mechanical cause is now named precisely: a script and a git command
  chained with a newline instead of `&&`, so a failing script does not
  stop the commit.
- **Comparison weakening**: third occurrence (row 1), now closed in code.
- **Scripted-edit hazard**: three instances this arc, still no tool.
- **Measurement corruption**: new class (row 7). The tree guard exists
  now; whether it becomes permanent is the director's ruling.

## 6. Honest limits

Nine rows, builder-assigned classes. Row 7's severity is a judgement -
nothing wrong was published, but only because of one manual check. The
zero-escape figure describes what the director had left to find AFTER the
tools ran, not builder accuracy.

## 7. The question for the next boundary

Two rules (D-057, D-062) failed to prevent their own class twice in one
arc. Is the honest conclusion that a rule which is not a check does not
change behaviour under load - and if so, which of this project's standing
rules are checks, and which are just sentences? A census of that, rule by
rule, would be a better use of a phase than any new feature.
