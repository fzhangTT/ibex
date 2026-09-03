---
name: coverage-closure
description: Convert a merged urg/vdb coverage report into a ranked list of holes, each resolved to a constraint-diff against the closest existing sequence or one new targeted-stimulus stub, via a cross-DB join (coverage bins to UVM sequence to RTL module). Use when a regression just finished and specific covergroup/cross/FSM bins need closing (not a fresh plan — use analyze-cov) — prefers mutating an existing test over a net-new one.
---

Adapted from ChipSmart (riscv/ChipSmart) coverage-closure.

# Coverage closure

Take a merged coverage report (URG / VDB / UCDB / equivalent), rank the holes by yield (how many bins one stimulus could close), trace each hole back through the testbench to a UVM sequence item with the right rand knobs, and emit one constraint stub per pattern.

## Scope — ALWAYS whole-design (non-negotiable)

Closure is measured and graded on the **whole design**, never a part in isolation:

- **Build once, instrument the whole DUT.** One coverage model covers the entire design top (e.g. `<tb>.u_dut`, auto-discovered); never per-module cov builds.
- **Run the FULL regression, merge + grade design-wide.** A closure iteration runs the complete closure testlist (all hole-targeting existing tests + seed bumps **together**), merges every per-test vdb against the compile-shape vdb, and reports the **design-wide** score across all metrics. The result of a closure pass is the whole-design number moving — a single covergroup/module/instance lighting up is only a *byproduct*, never the deliverable.
- **The hole model SELECTS, the design is the TARGET.** Rank holes design-wide to decide which existing tests/seeds to add (then seeds, then — last — new stimulus, per `existing-tests-first`), but the regression that executes and the report that's graded are always whole-design. Do NOT grade or "declare done" on one module/covergroup graded alone.
- **Close ALL instances, not just [0].** Generate-block symmetry (step 4) means a hole usually repeats across `<blk>[0..N-1]`. Stimulus that hits only index 0 is NOT closure — sweep every instance (`+idx=N` / a per-instance sequence) so the whole-design number reflects all N.
- **`focus.f` / directed bias is OPTIONAL and LAYERED, never a substitute.** A per-hole `+sp_focus_file` may bias randomization toward reachable holes to converge faster, but it rides ON TOP of the full whole-design regression and grading — it never replaces them, and you never grade only the focused part. Over-fitting one part (biasing only its bins) is a closure anti-pattern.

Everything below operates within this whole-design frame.

## Mandatory final step — emit the closure report (every run)

[not applicable in this repo — no `verification_dashboard` tool or `/proj_risc_regr`
site path; ibex has no unified-dashboard generator]. In place of it: every closure
run ends with the markdown report from "Output format" below, committed under
`dv/auto_dv/reviews/` alongside the regression's `out*/` artifacts it was graded
against, so the ranked-hole table and the constraint diffs are reviewable evidence,
not a transient chat answer.

## RTL is read-only — bug report + work around (never fix RTL)

Verification does not edit the design. The DV/TB tree is yours (UVM sequences,
tests, **coverage binds** like `*_coverage_bind.sv`, testlists, exclusion files);
the `rtl/` design source is **off-limits**.

When a hole — or a mismatch found while closing one — traces to an **RTL bug**
or **RTL-caused unreachability** (a bin that can't be hit because the RTL never
drives the signal / has a logic error), do NOT patch the RTL. Instead:

1. **File a bug report** — a markdown report under `dv/auto_dv/reviews/<module>_<short>.md`
   with: RTL `module:line`, the symptom (which coverage hole or mismatch), the
   root-cause analysis (signal trace / waveform evidence — facts, not guesses),
   reproduction, severity, and a *suggested* fix for the design team (text only).
2. **Work around it** so closure/regression proceeds:
   - If the bug blocks a path → adjust the **test/sequence** (TB side) to avoid or
     gate the broken path, or mark the affected test expected-fail, so the
     regression isn't wedged.
   - If it makes a bin **unreachable** → exclude that bin via `vdb_exclude` (verdi-cov
     MCP) with a waiver whose comment cites the bug-report path. The score then
     reflects `covered/(total−K)` honestly, and the exclusion is removed once RTL is
     fixed.
3. **Never** let an RTL edit be the closure mechanism. A covergroup lighting up
   only because RTL was changed is invalid — the bug must be reported and the
   design team must own the fix. (Contrast: a *coverage-bind* fix — wiring a
   covergroup to the right signal in `*_coverage_bind.sv` — is DV-side and fine;
   that is NOT an RTL edit.)

## When to apply

- The prompt references a merged-coverage dir, a coverage score, or asks "what should we cover next?" / "why is FSM at 58%?" / "which bins are still 0?"
- A regression just finished and the user wants targeted tests to lift specific covergroup / cross / FSM bins, not a fresh coverage plan.
- The user wants to mutate an existing test rather than write one from scratch.

Not for:
- Authoring a coverage plan from spec + RTL — `analyze-cov`.
- Closing fault holes — not applicable in this repo (no fault campaign in scope).
- Code coverage on a single test in isolation — that's a one-shot waveform/coverage-database query, not a closure workflow.

## Workflow

### 1. Index the merged coverage report

Use the **coverage database** capability to ingest the merged report into a queryable DB sibling to any pre-existing design / UVM catalogues. Re-ingest replaces all rows; record the ingest timestamp so downstream queries know how stale the data is.

Stop if: no merged report exists yet. There is nothing to query — direct the user to run the merge first.

### 2. Score the overall picture, pick the metric to chase

Read the per-metric totals (Line / Cond / Toggle / FSM / Branch / Group / Assert). Pick the lowest-scoring metric — that's where one new test moves the needle most. Don't optimise a metric already above target.

Stop if: every metric is above the target the user named. Report "no closure work" and exit.

### 3. Enumerate the holes for that metric, by yield

Use the **coverage database** to list uncovered items sorted by *expected bins per hole* (a single cross with 40 missing bins outweighs ten coverpoints with 2 each).

EVIDENCE: a ranked table — `qualified_name | bins_missing | score`. The top row is the candidate.

### 4. Detect generate-block / array symmetry

Real designs instantiate the same covergroup N times under `<repeat_block>[0..N-1]`. The DB reports each as a distinct row. Collapse by stripping the index substring from the qualified name; if N rows share one pattern, **one stimulus closes all N**. Emit one stub, not N.

### 5. Cross-DB JOIN — hole to UVM owner to RTL owner

For the top-ranked hole pattern, use the **coverage database** plus a **testbench catalogue** (UVM class / agent / sequence-item DB if one exists) and the **design database** (RTL module / signal-driver DB if one exists) via cross-database joins. Three pieces of evidence to collect:

- **Who declares the covergroup** — class file + line. If the class is never instantiated by any current test, the 0% has a structural cause (missing build vs missing stimulus).
- **Which RTL module the sampled signal lives in** — surfaces high-complexity / low-coverage modules.
- **Which sequence-item exposes the right rand knobs** — match covergroup variable names against rand field names (exact, then leaf substring).

EVIDENCE: a 3-line ownership chain `covergroup | uvm_class | rtl_module` plus a list of candidate rand knobs.

### 6. Pick the closest existing test, then read its constraints

Search the test catalogue for a test whose name signal-matches the target covergroup (shared prefix / shared module name). That test sits closest to the hole. **Read its sequence body** — every `constraint` block, every `dist`/`inside`/`==` clause on the rand knobs identified in step 5.

EVIDENCE: a per-knob row — `knob | declared type | current admissible set` — extracted from the SV source, not guessed.

### 7. Per-bin constraint-vs-bin solve loop

For each missing bin / cross-cell from step 4, run the **SMT solver** independently. The shape of the loop:

```
for bin in missing_bins:
    pred = sv_predicate_for(bin)               # e.g. "addr[15:0] > 16'h8000"
    verdict = solver.solve(seq_class, pred)    # SAT | UNSAT | UNKNOWN | UNTRANSLATABLE
    classify(bin, verdict)
```

Per-bin verdicts drive per-bin fixes:

| Verdict | Bin classification | Fix shape |
|---|---|---|
| **SAT (with witness)** | *admissible-just-unlikely* | `dist`-weight tuning toward the witness values |
| **UNSAT (with core)** | *excluded-by-current-constraint* | widening diff that drops/extends the clauses in the core |
| **UNKNOWN (timeout)** | *too-hard-to-decide* | retry with longer timeout once; if still UNKNOWN treat as UNTRANSLATABLE |
| **UNTRANSLATABLE** | *out-of-solver-scope* | textual-diff fallback — read the constraint by eye |

**Then group by shared unsat-core** before authoring the fix. Most missing bins in a closure session share a small set of root causes — one clause blocks N bins. The solver returns the named blocking clauses; cluster missing bins by their core fingerprint and emit ONE widening diff per cluster rather than N. The output table:

| Core fingerprint | Missing bins blocked | Single fix |
|---|---|---|
| `{c5}` | bin_A, bin_B, bin_C | drop / widen clause c5 |
| `{c2,c7}` | bin_D | drop one of {c2, c7} |
| `(no core — SAT)` | bin_E, bin_F | dist re-weight |

EVIDENCE: the grouped table; for each cluster, the proposed fix names the SV line(s) it touches.

### 7a. Automated path (host shortcut, when available)

[not applicable in this repo — verdi-cov-mcp exposes `vdb_exclude`/`vdb_find`/
`vdb_functional`/`vdb_lines`/`vdb_toggles` only, no `directed`/`rtl_diff` reachability
modes]. Use the manual recipe (steps 5–7) always; `vdb_exclude` still backs the
dead-bin exclusion-file step once a bin is proven unreachable by the manual solve.

The manual recipe (steps 5–7) remains the fallback and the explanation layer —
the automated verdict still needs the ownership chain (step 5) and the
minimum-disruption diff (step 8) to become an actionable artefact.

### 8. Emit the minimum-disruption output

Pick the smallest valid response per the **Decision rules** below. Three shapes possible, in order of preference: a `dist`-weight tuning diff against an existing constraint, an `inside`-set widening diff, or a new sequence stub. In all three cases, end with a `VERIFY:` comment line naming the exact bins expected to flip MISSING → HIT. Closing the loop (rerun, re-ingest, re-query) is the user's job.

## Decision rules

WHEN the SMT solver returns SAT for every missing bin's predicate against the existing constraints:
  DO emit a `dist`-weight tuning diff only — re-weight the existing `dist` toward the solver-witness values.
  EVIDENCE a unified-diff against the existing constraint block; each new weight cites the witness assignment that justifies it.

WHEN the SMT solver returns UNSAT with a non-empty unsat-core:
  DO emit a widening diff naming the exact clauses from the core — drop the pin, extend the `inside` set, or add an `||` alternative.
  EVIDENCE the diff names the core's clause identifiers; the change is the minimum that admits the missing values; existing covered bins remain reachable.

WHEN N missing bins return the SAME unsat-core fingerprint:
  DO emit ONE widening diff that addresses the shared core, not N independent fixes.
  EVIDENCE the closure artefact lists every bin the single fix is expected to flip MISSING → HIT, not just the one whose verdict you happened to run first.

WHEN the SMT solver returns UNTRANSLATABLE or UNKNOWN:
  DO fall back to the textual-diff path — read the constraint by eye, classify each bin, propose the diff manually.
  EVIDENCE the report explicitly flags the missing solver verdict and explains which construct (foreach / function call / etc.) blocked the translation.

WHEN a missing bin samples a field the current sequence does not randomise:
  DO emit a new derived sequence that extends the closest existing one and adds rand fields + constraints.
  EVIDENCE the new class extends an existing base, names only real rand fields from the testbench catalogue, and the `VERIFY:` line lists the specific new bins.

WHEN two missing-bin families share one root cause (one knob excluded by one pin):
  DO emit ONE diff that closes both — do not fragment into two patches.
  EVIDENCE the diff names every bin it expects to close.

WHEN the rand-field match against covergroup variables returns zero:
  DO fall back to leaf-name substring match, then to the sequence's parent agent's `*_transaction` class.
  EVIDENCE a non-empty knob list, or an explicit "no rand surface — directed walker required" note.

WHEN the target `*_transaction` class has no rand fields:
  DO emit a directed walker sequence (iterate values explicitly) instead of a constraint-randomised one.
  EVIDENCE the stub uses explicit field assignment + `uvm_send`, not `randomize() with`.

WHEN N rows of the gap table share one pattern (generate-block symmetry):
  DO emit one stub parameterised over the instance index.
  EVIDENCE the stub's constraint walks `inside {[0:N-1]}` on the instance field.

WHEN the covergroup's `source_file` points at a path that doesn't exist locally:
  DO surface the path verbatim and stop — do not invent a closer match.
  EVIDENCE the report names the missing path so the user can resolve the indirection.

WHEN no UVM / design catalogue is built yet:
  DO degrade to coverage-DB-only output (rank + stub skeleton, no ownership chain).
  EVIDENCE the report explicitly flags the missing JOINs so the user knows what's heuristic.

## Compatible tools

| capability used | concrete tools |
|---|---|
| coverage database | URG (`urg -format text`) + sqlite ingest, UCDB query (`vsim -do ucdb`), `pyucis` for IEEE-1800.2 UCIS |
| testbench catalogue (UVM) | UVM analyser → sqlite DB, `sv-parser` + custom indexer, Verible AST + grep |
| design database (RTL) | slang + sqlite DB, Verible elaborated AST, `sv-parser` |
| constraint extraction | parse the existing sequence's `constraint` blocks via `sv-parser` / Verible AST, or pattern-search + file read as fallback |
| SMT solver | Z3 or CVC5 driven by SMT-LIB stdin (e.g. `z3 -in`); a SV → SMT-LIB translator sits between the constraint AST and the solver |
| pattern search | `grep`, `rg` |
| file read | host-native file viewer |
| file edit | host-native patch / find-and-replace (for emitting diffs against existing sequences) |

At least one open-source option exists for every capability above; the host binds them to its actual tool surface.

## Output format

A markdown report with these sections, in order:

1. **Top-N covergroup gaps** — table: rank, base covergroup, instance count, var bins missing, cross bins missing, total.
2. **#1 ownership chain** — two-column table: layer (covergroup file / vars / cross / owning agent / payload class / driving stimulus / closest existing sequence) vs identity.
3. **Existing constraint surface** — for the closest existing sequence, the per-knob admissible set extracted from its `constraint` blocks (current `dist`, `inside`, `==` clauses verbatim).
4. **Constraint-vs-bin solve** — three-column table: `missing bin | solver verdict (SAT/UNSAT/UNTRANSLATABLE) + witness or core | proposed change` (one of: re-weight dist, widen inside-set, add knob). The verdict and witness/core are cited from the SMT run, not guessed.
5. **Closure artefact** — one of these three, whichever is smallest:
   - a unified diff against the existing sequence's constraint block (preferred when knobs already exist), OR
   - a derived sequence class (≤ 40 lines, extends the closest existing one) that adds the missing rand fields, OR
   - a directed-walker sequence when the target transaction has no rand surface at all.
   In all three cases, the artefact ends with a `// VERIFY: …` comment naming the exact bins / coverpoints expected to flip MISSING → HIT.
6. **Cost estimate** — bins closed per artefact, plus the one failure mode that would leave bins still at 0 after rerun (e.g. the live transaction stream doesn't cross the programmed threshold; the `solve … before …` order leaves a knob unreachable).

## What success looks like

- The top-1 stub's `VERIFY:` line names specific bins (not "improve coverage").
- Generate-block symmetry is collapsed — one stub per pattern, not N.
- Every claim about an owning UVM class / RTL module is backed by a row from the cross-DB JOIN, not a guess.
- When no UVM/design catalogue exists, the report says so up front instead of fabricating ownership.
- The user can rerun the regression with the emitted stub and re-ingest the merge to verify, without further LLM intervention.
