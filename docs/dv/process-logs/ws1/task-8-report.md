# Task 8 Report: `small`-config verification + `docs/dv/BUILD_AND_SIM.md`

Branch: `fzhang/auto-dv-setup` (verified via `git branch --show-current`
before starting and after commit).

## Step 1: Prove the Task 5 fix on a non-default config (`small`)

Command (exact, matches brief):

```bash
source ci/env.sh && cd dv/uvm/core_ibex && \
make SIMULATOR=vcs IBEX_CONFIG=small ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1 OUT=out_small
grep "TB-CONFIG" out_small/run/tests/*/rtl_sim*.log
```

Launched in the background (`nohup bash -lc '...' > $SCRATCH/task8_small_run.log 2>&1 &`),
polled the log directly with a bounded ~280s `while` loop watching for the
process to exit (not relying on the harness's own background-task
notification, per the process rule).

Result: **PASSED** cleanly (not just the time-0-banner fallback case) —

```
100.00% PASS 1 PASSED, 0 FAILED
riscv_arithmetic_basic_test.1: PASS
```

Banner:

```
out_small/run/tests/riscv_arithmetic_basic_test.1/rtl_sim_stdstreams.log:TB-CONFIG: BaseIsa=BaseIsaRV32I RegFile=RegFileFF RV32ZC=RV32Zca
```

Exact match to the expected `TB-CONFIG: BaseIsa=BaseIsaRV32I ...` mutation
proof. Compared against the opentitan banner from Task 6
(`TB-CONFIG: BaseIsa=BaseIsaRV32IorCHERIoT RegFile=RegFileFF
RV32ZC=RV32ZcaZcbZcmp`): `BaseIsa` and `RV32ZC` both changed per-config as
expected; `RegFile` correctly stayed `RegFileFF` since both `small` and
`opentitan` set `RegFile: "ibex_pkg::RegFileFF"` in `ibex_configs.yaml`
(verified by inspection, not assumed) — confirms the fix from commit
`54e01775` reaches TB elaboration for a second, independent config, not
just the one already exercised by Task 6.

Wall time: ~78s (launch ~17:48:00, `vcs_simv` built 17:48:35, `regr.log`
written 17:49:18) — consistent with Task 6's ~72s baseline.

Wrote the companion evidence note to
`docs/dv/evidence/ws1-smoke-regr-note.txt` (no pre-existing companion note
existed for `ws1-smoke-regr.log`, so this task created it, by the same
pattern as `ws1-cov-summary.txt` being the companion note for the coverage
evidence log) — contains the command, both banners side by side, and the
config-table cross-check.

`out_small/` removed after evidence capture (`out*/` never committed, per
global constraints).

## Step 2: Write `docs/dv/BUILD_AND_SIM.md`

Written per the brief's outline, using only commands actually run in Tasks
1-8 (cross-checked each against the corresponding task report and, where
needed, live repo inspection — not re-derived from memory):

- **One-time setup**: `ci/env.sh`/`ci/setup-venv.sh`/`ci/build-spike.sh`
  (~51s, Task 3)/`ci/get-toolchain.sh` (~1s download, Task 4), what each
  provides.
- **Running a single test**: the Task 6 command, ~72s observed wall time,
  where results land (`out/run/regr.log`, `report.html`/`report.json`/
  `regr_junit.xml`, `out/run/tests/<test>.<seed>/`, build logs) — verified
  these paths exist by inspecting a live `out/` tree from an earlier run
  before writing them down.
- **Running a regression**: `TEST=all` (Makefile default) /
  `all_riscvdv` / `all_directed` / comma-list semantics, confirmed by
  reading `dv/uvm/core_ibex/scripts/metadata.py`'s
  `process_riscvdv_testlist()`/`process_directed_testlist()` directly
  rather than guessing; `SEED..SEED+ITERATIONS-1` semantics confirmed from
  the same file's `for testseed in range(md.seed, md.seed + count)`.
- **Coverage**: the Task 7 (fixed) command, urg score 52.13 breakdown, the
  three artifact locations, and the `.vRefine` waiver caveat
  (`NOT-APPLIED`, confirmed by grep).
- **Configs**: the 8-config table transcribed from `ibex_configs.yaml`
  (read directly, not from memory), DV-Makefile-default-is-opentitan vs.
  top-level-Makefile-default-is-small (confirmed via
  `grep IBEX_CONFIG Makefile dv/uvm/core_ibex/Makefile`), and the
  `rtl_params` filtering mechanism described from reading
  `scripts/ibex_cmd.py:filter_tests_by_config()`'s docstring/logic
  directly.
- **Gotchas**: all 9 from the brief's list, plus the FCIBH workaround
  (commit `dbba358f`) and the IBEX_CFG define fix (commit `54e01775`) with
  both banners quoted. The `WAVES=1`/`VERDI_HOME` claim was verified
  against the actual `vcs.tcl` logic (`fsdbDumpfile` under
  `$VERDI_HOME`, else `dump -file waves.vpd`) rather than taken on faith.

## Step 3: Verify the doc against reality

Re-ran the doc's exact "single test" command from a fresh `bash -lc`
shell:

```bash
source ci/env.sh
cd dv/uvm/core_ibex
make clean
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1
```

Result: **PASSED** again —

```
100.00% PASS 1 PASSED, 0 FAILED
```

Banner reconfirmed: `TB-CONFIG: BaseIsa=BaseIsaRV32IorCHERIoT
RegFile=RegFileFF RV32ZC=RV32ZcaZcbZcmp`.

Wall time this run: ~156s (slower than Task 6's ~72s baseline; the TB
compile itself was the same ~39s per VCS's own CPU-time report — the extra
time was in env-sourcing/module-load overhead, not the build). Added a
one-sentence caveat to the doc noting this run-to-run variance so the
`~72s` figure isn't read as a hard guarantee.

`out/` removed after this re-verification (never committed).

## Step 4: Commit

```
d71e486c [docs] Add verified VCS build-and-sim instructions
```

2 files changed, 232 insertions(+): `docs/dv/BUILD_AND_SIM.md` (new),
`docs/dv/evidence/ws1-smoke-regr-note.txt` (new). `git status --short`
clean after commit — no `out*/` staged or committed.

## Self-review

- Every command in `BUILD_AND_SIM.md` is either one already verified in
  Tasks 1-7 (copied verbatim from their reports) or one I ran myself in
  this task (the `small`-config proof and the doc re-verification) —
  nothing was written from assumption.
- Cross-checked all factual claims not already spoon-fed in the
  coordinator context against the live repo: `ibex_configs.yaml` (8
  configs, exact parameter values), `Makefile`/`dv/uvm/core_ibex/Makefile`
  (default `IBEX_CONFIG` values), `scripts/metadata.py` (TEST/SEED/
  ITERATIONS semantics), `scripts/ibex_cmd.py` (`rtl_params` filtering),
  `vcs.tcl` (WAVES/VERDI_HOME behavior), `waivers/` directory contents.
- Did not dispatch any subagents, per instruction.
- No `out*/` directory was ever staged or committed at any point.

## Concerns

None. Both proof runs (small-config Step 1, doc re-verification Step 3)
passed cleanly on the first attempt with no triage needed — this matches
the pattern from Tasks 5/6 that the underlying flow is solid once the
define fix and FCIBH workaround are in place.
