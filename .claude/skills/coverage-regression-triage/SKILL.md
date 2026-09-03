---
name: coverage-regression-triage
description: Decide whether a design or TB change helped or hurt coverage — compares two coverage runs, attributes gained/lost bins, rules out a stale RTL-epoch rebaseline, and routes each silent coverage regression to sim-debug. Use as the merge gate for "did my change hurt coverage" (not a test-set optimizer — that's regression-optimization — and not a single-hole closer — that's coverage-closure).
---

Adapted from ChipSmart (riscv/ChipSmart) coverage-regression-triage.

# Coverage regression triage

Answer one question with evidence: **did this change help or hurt coverage, and if
it hurt, why?** Two coverage runs in, a PASS/REGRESSION verdict out — with the lost
bins named and each one routed to debug. This is the gate you put in front of a
merge, distinct from `regression-optimization` (make the test set efficient) and
`coverage-closure` (close a specific new hole).

## When to apply

- A commit / RTL edit / TB change landed and the user wants to know if coverage
  regressed against the last known-good run.
- "Why did coverage drop", "what did we lose", "is this change safe to merge".

Not for: minimising/grading a test set (`regression-optimization`); closing a
named bin with stimulus (`coverage-closure`); planning from spec (`analyze-cov`).

## Workflow

### 1. Diff the two runs
Compare the candidate run against the baseline: per-metric score deltas,
**gained vs lost** covered bins, hole attribution (which new variant closed a
gained bin), and new-variant value (did an added test add unique coverage). **Lost
bins are the headline** — a bin covered in the baseline and not in the candidate is
a *silent coverage regression*: the change quietly removed the stimulus that hit it.

### 2. Rule out a re-baseline first
Check the run lineage. If the two runs are in **different RTL epochs** (the design
filelist changed between them), the coverage is not directly comparable — old bins
may simply no longer exist. Separate "lost because the logic changed" (expected,
re-baseline) from "lost because stimulus regressed" (a real bug). When the RTL
changed, also pull the changed-logic bins — coverage near the change is *expected*
to move and should be re-targeted, not flagged.

### 3. Root-cause each silent regression
For every genuinely-lost bin (same RTL epoch, still defined, now 0): hand it to the
**debug workflow** — find a baseline test that hit it, replay it on the candidate,
and use waveform + log debugging to find why the stimulus no longer reaches it
(a constraint tightened, a default changed, a sequence dropped). Do **not**
re-derive debug logic here — delegate to the `sim-debug` skill / `ibex-debug-analyzer` agent.

When the candidate run *failed tests* (not just lost bins), first **localise the
fault by spectrum**: rank coverage nodes by how strongly their execution correlates
with the failing tests versus the passing ones (Ochiai / Tarantula / D*), purely
from the per-test hit-lists and pass/fail already in the coverage DB. The top-ranked
nodes name the RTL region to open in waveform first — a cheap pre-filter that points
the debug workflow at a starting point instead of a blank slate. Needs a no-drop
merge (failing seeds retained with their per-test hit-lists); skip it if the run is
all-pass or all-fail (the correlation signal is undefined without both).

### 4. Verdict
Emit a single gate result: **PASS** (no lost bins, or all losses explained by a
re-baseline), or **REGRESSION** (N bins lost with no RTL reason) — with the lost-bin
list and, per bin, the root-cause one-liner from step 3.

## Decision rules

- **Re-baseline before regression.** Never report a coverage loss as a regression
  until the RTL-epoch check rules out a design change as the cause.
- **A lost bin is a hard gate.** An unexplained lost bin blocks the merge; it is not
  a warning to note and move past.
- **Delegate debug, don't reimplement it.** Step 3 is the existing `sim-debug` skill
  applied to a specific bin's baseline test — compose it, don't duplicate it.
- **Gained-only is PASS, but report redundancy.** If a change only adds coverage,
  still note whether the added variants contributed *unique* bins or are redundant.

## Compatible tools

| capability used | concrete tools |
|---|---|
| run A/B coverage diff | verdi-cov MCP (`vdb_find`/`vdb_functional`/`vdb_lines`/`vdb_toggles`) compare over two runs |
| spectrum fault localisation | rank coverage nodes by failing-vs-passing-test correlation (Ochiai / Tarantula / D*) over the per-test hit-lists + pass/fail |
| RTL-epoch / staleness check | run lineage grouped by `src_files.yml` / design-filelist hash |
| changed-logic set | structural diff of two elaborated design-DB snapshots (siliconpilot MCP `rtl_analyze`) |
| root-cause debug | the `sim-debug` skill / `ibex-debug-analyzer` agent |
| pattern search / file read | `grep`, `rg`, Read/Grep tools |

At least one license-free option exists for every capability; the host binds them
to its tool surface.

## Output format

1. **Verdict** — PASS / REGRESSION, one line.
2. **Score deltas** — per-metric before → after.
3. **Lost bins** — table: bin, baseline test that hit it, root-cause one-liner,
   re-baseline? (yes/no).
4. **Gained bins** — count + whether new variants added unique coverage.
5. **Re-baseline note** — if the runs span an RTL change, which losses it explains.

## What success looks like

- A binary merge gate (PASS/REGRESSION), not a coverage dump.
- Every reported regression is a *same-epoch* loss with a named baseline test and a
  root cause — re-baseline losses are separated out, not miscounted as bugs.
- Debug is delegated to the host's waveform/log workflow, not re-derived here.
