---
name: covergroup-authoring
description: Author one new SystemVerilog covergroup (or extend an existing one) with mechanical bin-set validation — the bin set partitions the domain with no gap/overlap, `with`-clauses and `illegal_bins` are satisfiable, and bins size against real sequences for a plausible hit rate. Use for "add a covergroup for X" with one concrete artefact in scope; not for a full coverage plan (use analyze-cov) or closing one missing bin from a report (use coverage-closure).
---

Adapted from ChipSmart (riscv/ChipSmart) covergroup-authoring.

# Covergroup authoring

Author one new covergroup (or extend a covergroup with new bins / new coverpoints) end-to-end. The differentiating step is **mechanical bin validation**: a constraint-aware audit catches over-narrow `with` clauses, illegal-bin assertions that the testbench can't actually violate, and bin partitions with gaps — at edit time, before the sim cycle. Sister skills cover the other intents: `uvm-test-generation` for new sequences, `coverage-closure` for closing one specific missing bin, `analyze-cov` for whole-block coverage planning.

## When to apply

- "Add a covergroup for X" / "write coverage for this register / FSM / interface" with one concrete artefact in scope.
- An existing covergroup needs new bins, a new cross, or a new `illegal_bins` clause.
- The author has the intent in plain English; the testbench is already populated with constraint-bearing sequences whose bin-feasibility we can audit against.

Not for:
- A full block-level coverage plan from spec → covergroups → testplan rows → `analyze-cov`.
- Closing one specific missing bin from a regression report → `coverage-closure`.
- A new sequence to drive coverage → `uvm-test-generation`.

## Workflow

### 1. Pin the intent + sample point

One sentence: *what behaviour does the new covergroup measure, and when does it sample?* The sample point (`@(posedge clk iff …)`, explicit `.sample()` call, or `with function sample(args)`) is as important as the bin set — a perfectly-binned covergroup that never samples is dead.

EVIDENCE: the goal sentence + the SV file:line where the sample expression / event lives.

### 2. Pick the host scope

A covergroup can live in (a) a class — sampled per-object, often `option.per_instance = 1`; (b) a module bound by `bind` — sampled on RTL signals directly; (c) a package — global. Match the project's existing pattern in the same area before introducing a new shape.

EVIDENCE: name the chosen scope + a peer covergroup in the same scope as reference.

### 3. Declare the coverpoints

For each coverpoint, decide three things in order:

| Decision | Driven by |
|---|---|
| **Sampled expression** | The signal/variable whose value matters — `coverpoint x` or `coverpoint x.y[idx]` |
| **Bin set** | The spec's enumeration of interesting values (named legal modes; pass/fail outcomes; address-range bands) |
| **`iff` guard** (optional) | A predicate that masks sampling — e.g. `iff (reset_n && enable)` to exclude reset cycles |

Default to **explicit named bins** over `auto` bins. Auto-binning produces 64 bins per coverpoint regardless of intent, then forces closure-by-attrition. Named bins are documentation and a closure target.

### 4. Validate the bin set — the load-bearing step

Run the **bin-validation** capability against each coverpoint:

1. **Partition completeness** — the bins must cover the sampled domain with no gap (every value lands in some bin) and ideally no overlap (a value lands in exactly one bin, except for explicit `wildcard`/`default`). The audit returns `PARTITION_OK` / `GAPS` / `OVERLAPS` / `GAPS_AND_OVERLAPS`.
2. **`with`-clause feasibility** — for any `bins b[] = x with (predicate);`, check the predicate is satisfiable. UNSAT predicates produce dead bins.
3. **`illegal_bins` reachability** — for each `illegal_bins z = {values};`, check whether the testbench's seq library can actually produce one of those values. If no SAT-feasible seq can, the marking is correct (the impossible IS impossible). If a SAT-feasible seq can, the testbench has a real bug — the "illegal" value is reachable.
4. **Per-bin admissibility against seqs** — for each bin, check whether at least one project sequence can produce a value in that bin. Bins with zero SAT seq are *dead by construction* — flag and either drop or write the missing seq.

EVIDENCE: a per-coverpoint table — `coverpoint | bin | verdict | proposed action`.

### 5. Cross bins — only when the joint matters

A `cross` of N coverpoints with M cells each is N×M bins. Cross only when the joint distribution carries meaning the marginal coverpoints don't. Every cross should have:
- A clear hypothesis (what scenario does this cross enumerate?)
- Explicit `ignore_bins` / `binsof(…) intersect` for the joint cells the spec says can't occur
- A check that the surviving cross cells are reachable under existing seqs (run the bin validator with the cross's combined predicate)

WHEN a cross has > 64 cells:
  DO question it. Either the cross's hypothesis is too broad (split into smaller targeted crosses) or many cells are spec-impossible (add `ignore_bins`).
  EVIDENCE the report names the bin count + the spec-impossible cells the author is consciously dropping.

### 6. Author the SV + run lint

Standard project conventions: `option.name`, `option.per_instance`, `option.weight`, `option.goal` set explicitly. Lint must pass cleanly.

### 7. Smoke — one transaction, one sample, one hit

Compile + elaborate. Run a single test driving any seq that touches the sampled signal. Required outcomes:
- At least one `.sample()` event observed (or one positive edge of the sample-control event).
- At least one bin shows a HIT in the post-run report.
- No `UVM_FATAL` / `UVM_ERROR` from cg construction or sampling.

Smoke failure modes to triage:
- `sample` fires but every bin stays at 0 → `iff` guard is too strict OR sampled expression has the wrong width OR the seq doesn't actually drive the signal yet.
- `sample` never fires → the sample-control event is wrong (e.g. clocked off a gated clock that's disabled).
- Many bins fire on first cycle → reset / X-prop wasn't masked; add `iff (reset_n)`.

## Decision rules

WHEN the bin validator returns GAPS:
  DO either add a `default` bin or widen one of the explicit ranges. Don't silently leave the gap.
  EVIDENCE the post-fix `partition_check` returns PARTITION_OK.

WHEN the bin validator returns OVERLAPS without a `wildcard`/`default`:
  DO collapse overlapping ranges into one bin (probably the original intent) OR add `wildcard` if the overlap is structural.
  EVIDENCE no value is counted in two bins.

WHEN `illegal_bins` is structurally reachable under a project seq:
  DO either remove the `illegal_bins` marking (the value isn't actually illegal — spec was wrong) OR fix the seq (the seq is generating an illegal value).
  EVIDENCE the report links the offending seq's witness assignment to the supposedly-illegal bin.

WHEN a bin has zero SAT seq across the whole library:
  DO either drop the bin (over-specified spec) OR write the missing seq via `uvm-test-generation` before merging the covergroup.
  EVIDENCE the bin's evidence row names "drop" or "needs seq X with these knobs".

WHEN a cross's surviving cell count is > 100 and most cells are reachable:
  DO add `option.cross_num_print_missing = N` and either split or accept the closure cost.
  EVIDENCE the report flags the cell count as a closure-cost call-out, not a TB bug.

## Compatible tools

| capability | concrete tools |
|---|---|
| testbench catalogue (UVM + covergroups) | UVM analyser → sqlite (`uvm_covergroups`), `sv-parser` + custom indexer, Verible AST |
| constraint validation (SMT) | Z3 or CVC5 via SMT-LIB stdin; SV → SMT-LIB translator |
| coverage audit | bin-validator that combines `partition_check`, `dead_class_sweep`, per-bin SAT enumeration |
| static lint | `verilator --lint-only`, `slang --lint-only`, project-native |
| coverage database (post-sim) | URG (`urg -format text`) + sqlite ingest |
| pattern search / file read | host-native; `grep`, `rg` |

## Output format

A unified diff (or list of new files) + a markdown report with these sections, in order:

1. **Goal + sample point** — one sentence + the file:line of the sample event.
2. **Host scope** — class / module / package; peer covergroup cited.
3. **Coverpoint table** — `name | sampled_expr | iff | n_bins | partition_verdict`.
4. **Bin validation results** — for each coverpoint, the per-bin table from step 4.
5. **Cross sections** (if any) — the cross hypothesis, surviving-cell count, ignore-bin diff.
6. **Lint result** — clean or named diagnostics.
7. **Smoke result** — sampled at least once, at least one bin HIT.

## What success looks like

- Every coverpoint's bins return `PARTITION_OK` (or have an explicit `default` documented).
- Every `illegal_bins` is either provably unreachable under all project seqs OR is fixing an actual TB bug.
- Every bin has at least one SAT-feasible seq that admits a value in it.
- Cross cells are either explicitly enabled (intended) or `ignore_bins`-excluded — no "I'll let it go to 0% and hope it lifts" entries.
- The report names the next concrete extension (more bins, a new seq for an under-covered bin, a follow-up cross) — not "good luck."
