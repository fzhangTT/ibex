# Task 7 Report: COV=1 coverage run

Branch: `fzhang/auto-dv-setup`

## Summary

Ran the coverage flow exactly as specified in the brief. The coverage
*infrastructure* works end-to-end — `merged.vdb`, the urg text/HTML
report, and the riscv-dv `fcov` build are all produced — but the
underlying `riscv_arithmetic_basic_test` itself **FAILED** under
`COV=1`. VCS aborts the simulation within microseconds of boot due to a
fatal `Error-[FCIBH] Illegal bin hit` on a pre-existing (2022,
in-source-TODO'd) FSM covergroup incompatibility that only surfaces
once fcov covergroups are actually built/sampled — i.e. only under
`COV=1`. This is a design/testbench-side bug, not a flow/script issue,
and is out of scope to fix here per the brief's guidance to flag rather
than debug vendor/design code.

## Step 1: Run with coverage

Command (exact, matches brief):

```bash
source ci/env.sh && cd dv/uvm/core_ibex && \
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1 COV=1 OUT=out_cov
```

Process:
1. Launched via `nohup`-style background bash redirected to a scratchpad
   log file (not relying on the harness's own background-task
   notification, per the site quirk about unreliable notifications).
2. Polled the log with a bounded ~280s deadline `while` loop watching
   for PASS/FAIL/Error markers or process exit.
3. The run finished in well under 80s wall time (fast host, matches
   Task 6's precedent) — full re-generation + re-compile in the new
   `out_cov` tree, plus coverage instrumentation overhead.

Result printed at the end of the log:

```
Building RTL testbench
Generating core configuration file
Building randomized test generator
Running randomized test generator to create assembly file .../test.S
Compiling riscvdv test assembly to create binary at .../test.bin
Running RTL simulation at .../riscv_arithmetic_basic_test.1
Collecting simulation results and checking logs of testcase at .../trr.yaml
Generating RISCV_DV functional coverage
Merging all recorded coverage data into a single report
Collecting up results of tests into report regr.log
Warning: Not generating coverage summary, unsupported simulator vcs
0.00% PASS 0 PASSED, 1 FAILED
make[1]: *** [scripts/ibex_sim.mk:109: out_cov/metadata/regr.log.stamp] Error 1
make: *** [Makefile:72: run] Error 2
```

### Root-cause triage (why the test failed)

`trr.yaml` for the test:
```
passed:                   False
failure_mode:             FILE_ERROR(2)
failure_message:          |-
  [FAILED]: Processing the ibex trace failed: Logfile .../trace_core_00000000.log not found
```

`rtl_sim_stdstreams.log` shows VCS terminated the simulation almost
immediately (2064350 ps sim time, 0.51s CPU time — normal runs are
tens of thousands of instructions / much longer) with a fatal coverage
verification error, not a normal test failure:

```
Error-[FCIBH] Illegal bin hit
/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/fcov/core_ibex_fcov_if.sv, 588
core_ibex_fcov_if, "core_ibex_fcov_if::uarch_cg"
  VERIFICATION ERROR (FUNCTIONAL COVERAGE) : At time 2064350 ps, Illegal
  transition bin illegal_transitions of coverpoint cp_controller_fsm in
  covergroup core_ibex_fcov_if::uarch_cg got hit with transition RESET=>RESET
```

The offending source (`dv/uvm/core_ibex/fcov/core_ibex_fcov_if.sv:606-613`)
already documents the limitation:

```systemverilog
cp_controller_fsm: coverpoint id_stage_i.controller_i.ctrl_fsm_cs {
  bins out_of_reset = (RESET => BOOT_SET);
  ...
  // TODO: VCS does not implement default sequence so illegal_bins will be empty
  illegal_bins illegal_transitions = default sequence;
}
```

`git blame` traces this to commit `aee235cfa` (2022-03-24, "Greg
Chadwick"), long before WS1 bring-up — **this is a pre-existing,
known VCS incompatibility, not a regression from this branch's work.**
Because VCS doesn't implement SystemVerilog's `default sequence` for
transition bins, every FSM transition (including legitimate self-loops
like `RESET=>RESET` during boot) falls into "illegal", and VCS treats
that as a fatal error rather than a benign miss.

Confirmed this is COV-specific: Task 6's `COV=0` run's `rtl_cmds` in
`out/run/tests/riscv_arithmetic_basic_test.1/trr.yaml` has **neither**
`+enable_ibex_fcov=1` nor `-cm ...` — so the fcov covergroups were never
built/sampled in that run, which is why the smoke test never hit this.

Checked `vcs -help` for a documented runtime switch to demote FCIBH
severity from fatal to warning (a cheap, bounded check, not a debugging
rabbit hole) — found none. This is not a one-flag flow fix; a real fix
requires reworking the covergroup itself (e.g., removing/restructuring
the `illegal_bins = default sequence` construct for VCS), which is
design/testbench-side work out of scope for this flow bring-up task.

## Step 2: Verify coverage artifacts

```
$ ls out_cov/run/coverage/merged.vdb && ls out_cov/run/coverage/report/ | head && ls out_cov/run/coverage/fcov 2>/dev/null | head -3
out_cov/run/coverage/merged.vdb
asserts.html
asserts.txt
css
dashboard.html
dashboard.txt
groups.html
groups.txt
grp0_1.html
grp0_2.html
asm_test
compile.log
ibex_trace_log
```

All three expected artifacts are present. `merge.log`/`merge.log.stdout`
show the `urg` merge completed cleanly (no errors) despite the
underlying test's failure — the Makefile's coverage-merge step runs
regardless of individual test pass/fail. `fcov/` contains a fully built
riscv-dv functional-coverage analysis binary (`vcs_simv` + support
files via `scripts/get_fcov.py` → vendor `cov.py`), though its
`ibex_trace_log`/`asm_test` subdirs are empty since no real trace was
produced by the aborted sim — i.e. the fcov *build* succeeded but there
was no real trace data to analyze.

urg summary line (`report/dashboard.txt`, Total Coverage Summary):

```
SCORE  LINE   TOGGLE FSM    BRANCH ASSERT GROUP
 21.73  45.17   0.51   0.00  31.47  27.05  26.17
```

**This number is not representative of real coverage** — it reflects
only the ~2 microseconds of reset-time activity captured before VCS
aborted, not a full `riscv_arithmetic_basic_test` run. Recorded verbatim
plus the full caveat in `docs/dv/evidence/ws1-cov-summary.txt`.

## Step 3: Waiver caveat check

```
$ grep -rn vRefine dv/uvm/core_ibex/scripts/ || echo NOT-APPLIED
NOT-APPLIED
```

Confirmed `dv/uvm/core_ibex/waivers/aux_code.vRefine` and
`dv/uvm/core_ibex/waivers/unr.vRefine` exist on disk but are not
referenced by `scripts/merge_cov.py` (or any other script) — a
design-time finding: coverage waivers are defined but never applied to
the urg merge output. Recorded for BUILD_AND_SIM.md gotchas.

## Step 4: Commit evidence

```
2afc18be [dv] WS1 gate evidence: COV=1 run produces merged.vdb and urg report
```

`docs/dv/evidence/ws1-cov-summary.txt` added (78 lines), containing the
exact command, artifact listing, urg summary line, the full FCIBH
root-cause writeup, and the Step 3 waiver-caveat result.

Housekeeping: also removed a stray VCS-generated FSM-schematic debug
dump (`dv/uvm/core_ibex/.fsm.sch.verilog.xml`, auto-emitted by VCS when
it hit the FCIBH error) that had leaked into the tracked directory
outside `out_cov/`, so it didn't pollute the working tree for later
tasks. `git status --short` after commit shows only the expected
untracked `out_cov/` (never committed, per global constraints).

## Wall-times

| Stage | Duration |
|---|---|
| Full run (env source through make exit, background+poll) | < 80 s |
| RTL sim (aborted early due to FCIBH) | 0.51 s CPU time / ~2 μs sim time |
| urg merge | < 5 s |
| fcov build (vendor cov.py compiling analysis simv) | ~9 s (8.239s compile + .130s elab + .518s link per VCS report) |

(No meaningful comparison to Task 6's ~72s total is possible for the
*test* itself since this run aborted almost immediately; the full
`make` invocation including TB rebuild in the fresh `out_cov` tree,
riscv-dv regen, and urg/fcov post-processing still completed in well
under 80s total.)

## Final evidence / recommendation

- Coverage **flow mechanics** (Makefile targets, `merge_cov.py`,
  `get_fcov.py`, urg invocation) all work correctly and produce
  well-formed artifacts — this part of Task 7's goal is met.
- Coverage **data validity** is currently blocked: any `COV=1` run
  deterministically fails within microseconds due to the pre-existing
  `cp_controller_fsm`/`cp_controller_fsm_sleep` `illegal_bins = default
  sequence` VCS incompatibility in
  `dv/uvm/core_ibex/fcov/core_ibex_fcov_if.sv:606-613,612-613`. This
  needs a design/testbench-side fix (not a flow/script fix) before
  `COV=1` runs produce meaningful, passing coverage data. Flagging for
  the WS1 gate owner / follow-up task rather than attempting an RTL fix
  here.
- Waiver caveat (Step 3) confirmed as expected: `*.vRefine` waivers
  exist but are unreferenced by `merge_cov.py` — a separate, smaller
  design-time gap to note in BUILD_AND_SIM.md.

---

## Fix round 1: FCIBH guard (controller ruling)

Controller ruled: guard the broken `illegal_bins ... = default sequence`
construct out for VCS specifically, since it was never functional under
VCS by upstream's own admission (the in-source TODO expected it to end
up empty) and current VCS instead false-fatals on legal self-loops.

### Changes

`dv/uvm/core_ibex/fcov/core_ibex_fcov_if.sv` — wrapped both
`illegal_bins illegal_transitions = default sequence;` blocks
(`cp_controller_fsm` line 607, `cp_controller_fsm_sleep` line 614) in
`` `ifndef FCOV_NO_DEFAULT_SEQUENCE `` / `` `endif ``, replacing each
`TODO` comment with a one-line intent comment:

```systemverilog
`ifndef FCOV_NO_DEFAULT_SEQUENCE
      // FCOV_NO_DEFAULT_SEQUENCE: VCS half-implements 'default sequence' and fatals on legal self-loops (FCIBH)
      illegal_bins illegal_transitions = default sequence;
`endif
```

`dv/uvm/core_ibex/yaml/rtl_simulation.yaml` — added
`+define+FCOV_NO_DEFAULT_SEQUENCE` to the `vcs` tool entry's compile
`cmd` only (alongside the existing `+define+UVM`/`+define+UVM_REGEX_NO_DPI`);
no other simulator entry (questa/dsim/riviera/qrun/xlm) touched. Grepped
the repo first (`grep -rn FCOV_NO_DEFAULT_SEQUENCE .`) to confirm the
macro name was unused before introducing it.

### Re-verification (fresh `OUT=out_cov2`, avoids stale `metadata.pickle`)

```bash
source ci/env.sh && cd dv/uvm/core_ibex && \
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1 COV=1 OUT=out_cov2
```

Launched in background, polled the log directly with a bounded ~280s
deadline (no reliance on the harness notification). Result:

```
100.00% PASS 1 PASSED, 0 FAILED
```

Confirmed no FCIBH recurrence:
```
$ grep -c "FCIBH" out_cov2/run/tests/riscv_arithmetic_basic_test.1/rtl_sim_stdstreams.log
0
```

Artifacts re-verified present: `out_cov2/run/coverage/merged.vdb`,
`out_cov2/run/coverage/report/` (dashboard.txt/.html etc.),
`out_cov2/run/coverage/fcov/` — this time with **real** data:
`fcov/test.vdb` (28K, non-empty) and
`fcov/sim_riscv_instr_cov_test_0_0.log` showing riscv-dv's own fcov
analysis test:

```
[uvm_test_top] : 10217 instructions processed
[uvm_test_top] TEST PASSED
UVM_ERROR :    0
UVM_WARNING :    0
```

New urg summary line (`out_cov2/run/coverage/report/dashboard.txt`,
Total Coverage Summary — real full-run data this time, not a reset-only
partial):

```
SCORE  LINE   TOGGLE FSM    BRANCH ASSERT GROUP
 52.13  70.46  39.37  20.93  62.52  85.63  33.86
```

(up from the bogus 21.73%/0.00% FSM of the aborted run — FSM coverage
in particular jumped from 0.00% to 20.93%, consistent with the fix
letting the controller FSM actually be exercised and measured instead
of aborting at reset.)

`docs/dv/evidence/ws1-cov-summary.txt` was rewritten (not just
appended) to lead with the real PASS + 52.13% result and command, with
the FCIBH root-cause/fix history and Step 3 waiver caveat kept as
supporting sections.

### Housekeeping

A stray VCS-generated `.fsm.sch.verilog.xml` FSM-schematic debug dump
reappeared in `dv/uvm/core_ibex/` (a normal `-cm fsm` compile-time
byproduct, not specific to the FCIBH bug) and was removed again before
committing, same as in the first attempt.

### Commit

```
dbba358f [dv] Guard VCS FCIBH fatal on cp_controller_fsm illegal_bins
```

3 files changed: `fcov/core_ibex_fcov_if.sv`, `yaml/rtl_simulation.yaml`,
`docs/dv/evidence/ws1-cov-summary.txt`. Commit message quotes the
`Error-[FCIBH]` line per triage conventions. `git status --short` after
commit shows only the expected untracked `out_cov/` and `out_cov2/`
(neither committed).

### Final result (superseding the "Final evidence / recommendation"
section above)

- **COV=1 test result: PASS** (100.00% PASS, 0 FAILED) — was FAIL.
- **New urg overall score: 52.13%** (LINE 70.46, TOGGLE 39.37, FSM
  20.93, BRANCH 62.52, ASSERT 85.63, GROUP 33.86) — was the
  non-representative 21.73%/0.00% FSM from the aborted run.
- `merged.vdb`, urg report, and `fcov/` all present with real data.
- Fix is VCS-scoped only (macro-gated), so other simulator flows in
  `rtl_simulation.yaml` are unaffected.
- Waiver caveat (Step 3) unchanged: `*.vRefine` waivers still
  unreferenced by `merge_cov.py` (NOT-APPLIED) — separate, smaller
  design-time gap for BUILD_AND_SIM.md.
