---
name: regression-optimization
description: Grade a finished regression's per-test coverage to a minimal test set (drop redundant tests/seeds), recommend the next tests/seeds worth running under a CPU budget, and gate coverage run-over-run for staleness. Use to minimize/grade a finished regression or compare two runs — not a fresh coverage plan (analyze-cov) or single-hole stimulus (coverage-closure); needs per-test coverage retention (see Prerequisite below).
---

Adapted from ChipSmart (riscv/ChipSmart) regression-optimization.

# Regression optimization

Take a regression that already ran and make its *test set* efficient: the smallest
set of tests/seeds that holds the coverage, the next tests/seeds worth running, and
a run-over-run verdict on whether a change helped or quietly hurt coverage. The
input is the **per-test** coverage attribution (which test hit which coverpoint /
code node) plus each test's CPU time and pass/fail — so the answers are exact set
operations, not heuristics.

Sister skills, different intent: `coverage-closure` closes one specific missing
bin with new stimulus; `analyze-cov` plans coverage from a spec;
`covergroup-authoring` writes a covergroup. This skill never authors RTL/TB — it
decides which existing tests to keep, drop, or repeat.

## When to apply

- "Grade / minimise my regression", "which tests or seeds can I drop", "smallest
  set for the same coverage".
- "What should I run next to lift coverage fastest", "how many more seeds of test
  X", under an optional CPU budget.
- "Did my change lose coverage", "compare run A vs run B", "is my coverage stale".

Do **not** apply for closing a named hole (coverage-closure), authoring coverage
(covergroup-authoring / analyze-cov), or fault coverage.

## Prerequisite — per-test data

Grading, recommendation, and node-level compare need **per-test → per-node
hit-lists**, which exist only when the regression flow *retained per-test data*
(per-test coverage databases, or a no-drop merge that includes the design
database). Ingest them first:

1. Ingest per-test coverage + identity (testname, seed, knob signature, cpu_time,
   pass/fail) into the coverage DB for the target.
2. If only an aggregate merged score exists (per-test data was dropped at merge),
   say so — grade/recommend are unavailable; fall back to metric-level compare and
   recommend re-running with per-test retention enabled.

## Workflow

### 1. Grade the test set
Run the grader over the run's hit-lists. Read out, in this order:
- **minimal set** — the cost-aware greedy selection (each pick maximises
  *new coverage / cpu_time*) that holds the full coverage; report tests-cut and
  cpu-saved vs the full set up front (that is the headline ROI).
- **ranked order + coverage curve** — the sequence to run for the fastest coverage
  ramp (useful for smoke / early-exit).
- **redundant tests** — contribute nothing the rest don't → drop candidates.
- **seed caps** — per testname, how many seeds actually earned inclusion (the rest
  are redundant seeds of that test).
- **failing variants** — previously-failed tests to re-prioritise next run.

### 2. Recommend what to run next
- From **already-observed** tests under a budget → the cost-aware *recommend*: the
  next N tests that add the most new coverage per second given what's already run.
- For **unrun seeds** (predict the value of *another* seed of a test) → the
  predictive recommender: it models per-(testname, node) hit probability, applies
  diminishing returns (a reliably-hit node drops out for the next seed), and a
  diversity bonus for under-sampled tests. Express the goal as a CPU **budget**
  (ideally a fraction of the baseline regression's compute) and stop when the
  marginal gain falls below a threshold.

### 3. Gate coverage run-over-run
- **compare** two runs → per-metric deltas, **gained vs lost** bins, hole
  attribution (which new variant closed a bin), and new-variant value (did an
  added test/seed add *unique* coverage or is it redundant). **Lost bins = a
  silent coverage regression** — stop and investigate before merging.
- **lifecycle** → group runs into RTL epochs (a design-version change re-baselines
  coverage), flag **staleness** (latest coverage measured on older RTL), and the
  run set the predictive model should train on (current epoch only). If stale,
  re-ingest fresh coverage before trusting grade/recommend.

## Decision rules

- **Never subtract coverage across an RTL change.** If `lifecycle` shows the two
  runs are in different epochs, deltas are not comparable — re-baseline first.
- **Minimal-set must hold full coverage**: covered(minimal) == covered(full); if
  not, the hit-lists are incomplete (per-test data partially dropped) — flag it.
- **Cost-aware by default** (coverage per CPU-second); use raw-gain ordering only
  when the user asks "fewest tests regardless of runtime".
- **Diminishing returns governs seed counts**: stop adding seeds of a test when the
  predicted marginal new coverage drops below ε.
- **Lost bins block merge.** A compare verdict of REGRESSION is a hard gate, not a
  warning.
- **Dead bins are not holes.** If a "hole" is provably unreachable, it belongs to
  coverage-closure's exclusion path, not the recommend budget.

## Compatible tools

| capability used | concrete tools |
|---|---|
| per-test coverage ingest | per-test coverage DB reader (URG `-show tests` on a no-drop merge, or per-test vdb reader) → sqlite |
| coverage database | sqlite coverage DB with per-node contributing-test hit-lists + per-test cpu_time/pass-fail |
| set-cover / greedy grade | popcount/union over packed hit-lists (pure host code; no solver) |
| predictive recommend | per-(testname,node) frequency model + diminishing-returns + UCB (pure host code; optional gradient-boosted regressor when enough run history exists) |
| run-over-run compare | sqlite set-diff over two runs' hit-lists + run metadata |
| identity resolution | per-test run metadata (testname / seed / knob args / cpu_time / pass-fail) |
| pattern search / file read | `grep`, `rg`, host-native file viewer |

At least one open-source / license-free option exists for every capability above;
the host binds them to its actual tool surface. None of this requires a coverage-
optimization license.

## Output format

A markdown report, in order:

1. **Headline ROI** — full set (tests, CPU) → minimal set (tests, CPU); tests cut,
   CPU saved, coverage held (covered/total nodes).
2. **Minimal regression** — ranked table: test, seed, marginal new bins,
   cumulative coverage, cpu.
3. **Seed caps** — table: testname, seeds kept / seeds available.
4. **Redundant tests** — drop list (contribute zero unique coverage).
5. **Next-run recommendation** — table: testname, extra seeds, predicted new bins,
   cpu, under the stated budget; plus the predicted total new coverage.
6. **Run-over-run verdict** (when two runs given) — score deltas, gained/lost bin
   counts, the lost-bin list (silent regressions), and a one-line
   PROGRESS / REGRESSION / NEUTRAL verdict. Staleness called out if present.

## What success looks like

- The minimal set provably holds the same coverage as the full set (stated, not
  assumed), with a concrete tests-cut / CPU-saved number.
- Seed caps name specific testnames and counts, not "reduce seeds".
- The next-run recommendation is budget-bounded and ordered by coverage-per-CPU,
  with diminishing returns visible (later picks predict less).
- A run-over-run comparison gives a hard PASS/REGRESSION verdict with the lost
  bins named — the user can gate a merge on it without re-reading raw reports.
- When per-test data was dropped at merge, the report says so up front and points
  at the retention fix, instead of fabricating a minimal set from aggregate scores.
