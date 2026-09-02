# Building and Running Ibex DV Simulations (VCS)

This document covers the `core_ibex` UVM DV flow (`dv/uvm/core_ibex`) under
Synopsys VCS with Spike as the co-simulator, on this site's tooling. Every
command below was actually run during WS1/WS2 bring-up (see the linked
process-log reports and `docs/dv/evidence/` for each claim); wall-times are
what was observed on this host (a 192-core machine), not vendor/upstream
estimates, and are not a guarantee — see the run-to-run variance note under
"Running a single test" below.

## One-time setup

Run once per checkout (or whenever the tools move):

`ci/env.sh` is the single source of truth for the tools directory: export
`IBEX_TOOLS_DIR=/path/to/writable/dir` before sourcing it if the default it
picks does not suit you (see that script for the current default).

```bash
source ci/env.sh
bash ci/setup-venv.sh
bash ci/build-spike.sh
bash ci/get-toolchain.sh
```

- `ci/env.sh` also loads the site's VCS/licenses/dtc Modules (see Gotchas
  below), and exports `IBEX_PYTHON`, `RISCV_GCC`/`RISCV_TOOLCHAIN`,
  `SPIKE_PATH`, and the venv's `PKG_CONFIG_PATH`. Source it in every new
  shell before running anything else in this document.
- `ci/setup-venv.sh` creates `.venv/` and installs from `ci/requirements.lock`
  when present, falling back to `python-requirements.txt` (including
  riscv-dv's own requirements) otherwise, via `$IBEX_PYTHON`. Idempotent —
  safe to re-run.
- `ci/build-spike.sh` clones and builds the lowRISC fork of Spike (pinned
  revision) and installs it to `$IBEX_TOOLS_DIR/spike-ibex-cosim`. Requires
  `dtc` on PATH, which `ci/env.sh` loads via Modules. Observed: ~51s wall
  time on this host (`docs/dv/process-logs/ws1/task-3-report.md`).
- `ci/get-toolchain.sh` downloads and unpacks the lowRISC
  `rv32imcb` prebuilt GCC toolchain to
  `$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb`. Observed: ~1s to
  download the 41.8M tarball on this host's network; idempotent (skips the
  download if the tarball is already present)
  (`docs/dv/process-logs/ws1/task-4-report.md`).

## Running a single test

```bash
source ci/env.sh
cd dv/uvm/core_ibex
make clean
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1
```

Observed: **~72s total wall time** on this host for a fully fresh build
(TB compile ~39s of that; the flow's own once-off estimates for this class
of build are much larger — 30-60 min — but do not hold on this host). A
second from-scratch run during doc verification took ~156s instead (TB
compile unchanged at ~39s per VCS's own CPU-time report, so the extra ~84s
is elsewhere in the pipeline — env-sourcing/module-load overhead is one
candidate but was not isolated further; see
`docs/dv/process-logs/ws1/task-8-report.md`) — expect some run-to-run
variance on this host, not just this one number.

This one `make` invocation runs the whole flow: riscv-dv instruction
generation, cross-compile to a binary, VCS testbench build, and the VCS +
Spike cosim run. Results land under `out/`:

- `out/run/regr.log` — pass/fail summary (`100.00% PASS 1 PASSED, 0 FAILED`
  on success).
- `out/run/report.html` / `out/run/report.json` / `out/run/regr_junit.xml` —
  same result in HTML/JSON/JUnit form.
- `out/run/tests/<test>.<seed>/` — one directory per test/seed, containing
  `test.bin`, `rtl_sim_stdstreams.log` (see Gotchas), `trace_core_*.log`
  (ibex RTL trace), and `spike_cosim_trace_core_*.log` (Spike reference
  trace).
- `out/build/tb/compile_tb_stdstreams.log` — VCS testbench compile log.
- `out/build/instr_gen/build_stdout.log` — riscv-dv generator VCS build log.

## Running a regression

Same `make` invocation, varying `TEST`:

- `TEST=all` (the Makefile default) — every riscv-dv **and** directed test in both
  testlists, except a cocotb-only entry (testlist `cocotb: 1`) when `COCOTB=0` — such an
  entry needs `COCOTB=1` compiled in and is excluded from this wildcard, not failed
  (`dv/uvm/core_ibex/scripts/ibex_cmd.py:filter_cocotb_only_tests()`); name it explicitly in
  `TEST=` to select it anyway.
- `TEST=all_riscvdv` — only tests from `riscv_dv_extension/testlist.yaml`.
- `TEST=all_directed` — only tests from
  `directed_tests/directed_testlist.yaml`.
- `TEST=test_a,test_b` — a comma-separated list of specific test names (mix
  riscv-dv and directed names freely; `all`/`all_riscvdv`/`all_directed` can
  also appear as list entries).

`ITERATIONS=N` overrides each selected test's iteration count from its
testlist entry. `SEED=S` is the *starting* seed: for a test run with `N`
iterations, seeds `S, S+1, ..., S+N-1` are used, one per iteration
(`out/run/tests/<test>.<seed>/` per iteration). If `SEED` is omitted, the
Makefile picks a random starting seed (`$RANDOM`) — pin `SEED` explicitly
for anything you need to reproduce.

## Coverage

```bash
source ci/env.sh
cd dv/uvm/core_ibex
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1 COV=1 OUT=out_cov2
```

Result: `100.00% PASS 1 PASSED, 0 FAILED`, urg overall score `52.13`
(LINE 70.46, TOGGLE 39.37, FSM 20.93, BRANCH 62.52, ASSERT 85.63,
GROUP 33.86). This run compiles in the FCIBH workaround (see Gotchas) — it
is not a plain vanilla VCS build.

Artifacts (under `$OUT/run/coverage/`):

- `merged.vdb` — the urg-merged coverage database.
- `report/` — the urg HTML+text report (`dashboard.txt`/`dashboard.html`,
  `groups.*`, `asserts.*`).
- `fcov/` — riscv-dv's own functional-coverage analysis
  (`test.vdb` + `sim_riscv_instr_cov_test_0_0.log`).

Full evidence, including the FCIBH root-cause and fix, is in
`docs/dv/evidence/ws1-cov-summary.txt`.

**Waiver caveat:** `dv/uvm/core_ibex/waivers/aux_code.vRefine` and
`.../unr.vRefine` exist on disk but are **not** referenced by
`scripts/merge_cov.py` or any other script — coverage waivers are not
applied to the urg merge automatically. Load them manually in Verdi/urg if
you need waived coverage numbers.

## Configs

`IBEX_CONFIG` selects one of the named configs from the top-level
`ibex_configs.yaml` — that file is the single source of truth for each
config's actual parameter values; do not copy them here, they drift. The DV
Makefile's default is `opentitan` (`dv/uvm/core_ibex/Makefile`); the
top-level RTL build Makefile's default is `small` (`Makefile`) — pass
`IBEX_CONFIG` explicitly if you need one consistently across both.

| Config | Distinguishing shape (see `ibex_configs.yaml` for exact params) |
|---|---|
| `small` | 2-stage pipeline; narrowest feature set (no ICache/PMP/SecureIbex). |
| `opentitan` | Matches the OpenTitan project's Ibex integration. DV Makefile default. |
| `maxperf` | 3-stage pipeline; max performance ignoring the (unverified) branch predictor. |
| `maxperf-pmp` | `maxperf` + PMP enabled. |
| `maxperf-pmp-bmbalanced` | `maxperf-pmp` + balanced bitmanip. |
| `maxperf-pmp-bmfull` | `maxperf-pmp` + full bitmanip. |
| `maxperf-pmp-bmfull-icache` | `maxperf-pmp-bmfull` + ICache/ICacheECC enabled. |
| `experimental-branch-predictor` | `maxperf`-style config with the branch predictor on — experimental, not fully verified. |

Each riscv-dv/directed testlist entry may carry an `rtl_params` map (e.g.
`SecureIbex: 1`); `scripts/ibex_cmd.py:filter_tests_by_config()` drops any
test whose `rtl_params` aren't all satisfied by the selected config before
building the regression's test list — e.g. `SecureIbex`-gated tests are
excluded from a `small` or `maxperf` run (not failed), but not silently:
`filter_tests_by_config()` logs a `logger.warning()` naming the rejected
test and the unsatisfied parameter for every exclusion.

## cocotb (python) tests

Two make knobs opt a run into the cocotb coexistence overlay (`docs/dv/TB_CONTRACT.md`
covers the Python-side interfaces in full; this section covers running the flow):
`COCOTB=1` compiles the overlay in, `COCOTB_MODULE=<dotted.module>` picks which Python
module cocotb imports (default `dv.cocotb.ibex_cocotb`; resolved on `PYTHONPATH` from the
repo root).

Verified commands (from `docs/dv/evidence/ws2-hello.log` and
`docs/dv/evidence/ws2-milestone-b.log`):

```bash
source ci/env.sh
cd dv/uvm/core_ibex
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=2 COCOTB=1 OUT=out_ma
```

`SEED=2`, not `1`: `SEED=1` hits a real, pre-existing UVM_ERROR
(`NoMemResponseWithoutPendingAccess` in `rtl/ibex_core.sv`) a few ns after the run has
already legitimately PASSED — a latent testbench characteristic that
`finish_on_completion=0` (see below) exposes on that one seed, not a cocotb-overlay bug
(full root-cause in `docs/dv/process-logs/ws2/task-5-report.md`).

```bash
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=cocotb_irq_python_test ITERATIONS=1 SEED=1 COCOTB=1 \
     COCOTB_MODULE=dv.cocotb.tests.test_irq_from_python OUT=out_mb
```

Both: `100.00% PASS 1 PASSED, 0 FAILED`.

### Gotchas specific to cocotb

- **Knob-flip caveat**: `COCOTB`/`COCOTB_MODULE` are subject to the same stale
  `metadata.pickle` characteristic as any other top-level knob — see "Stale
  `metadata.pickle`" under Gotchas below. Milestone A/B were each run with a fresh `OUT`,
  so this was not hit in evidence, but it applies here identically.
- **`finish_on_completion=0`**: cocotb, not UVM, owns ending the simulation, so UVM's own
  `finish_on_completion` is cleared for any `COCOTB=1` build. The simulation keeps
  clocking between UVM's own report/summary and the point cocotb's `finish()` observes
  completion and returns — DUT assertions can still fire in that window on an unlucky
  seed (see the `SEED=1` case above).
- **Watchdog vs. import-failure behavior differ.** A `COCOTB_MODULE` that fails to import
  (e.g. a typo) is caught by cocotb 1.9.2's own regression manager, which logs it
  `CRITICAL` with a traceback and `$finish`es cleanly at simulation time 0 — this is what
  actually fires for a bad `COCOTB_MODULE` value. The TB's own `$fatal`-at-100ns dead-cocotb
  watchdog (`core_ibex_cocotb_if.sv`) is real but guards a narrower, different failure
  class: total VPI/libpython load failure, where no Python code runs at all (not
  reachable through `COCOTB_MODULE` alone). Either way the run fails loudly — no false
  PASS — but the two failure paths are distinct and log differently
  (`docs/dv/process-logs/ws2/task-5-report.md`).
- **`timeout_ms` does not auto-scale.** `finish(dut, timeout_ms=...)`'s default (2ms)
  only covers a minimal program; a heavier generated program needs a caller-supplied
  budget sized to how long it actually takes to reach its own completion handshake, or it
  raises `TimeoutError` on an otherwise-passing run.
- **Pass/fail is log-scan only.** This flow never checks the simulator process's own exit
  code (`scripts/run_rtl.py` runs it without capturing success/failure by design) —
  `COCOTB=1` doesn't change that. Pass/fail is decided entirely by
  `scripts/check_logs.py`'s post-hoc scan of the sim log and output files, identically to
  the stock (`COCOTB=0`) flow.
- **`results.xml`** (cocotb's own JUnit report) is written into the current working
  directory (`dv/uvm/core_ibex/`), not under `OUT` — `.gitignore`d, but don't rely on the
  flow to clean it up; delete it manually if it isn't wanted between runs.

## Gotchas

- **Stale `metadata.pickle`.** After editing a testlist or
  `ibex_configs.yaml`, `metadata.py` refuses to recreate metadata if
  `out/metadata/metadata.pickle` already exists from a prior run. Use
  `make clean` or a fresh `OUT=<new_dir>` after such edits. The same
  create-once behavior blocks flipping *any* top-level knob (`COCOTB`,
  `COCOTB_MODULE`, `WAVES`, `COV`, `SIMULATOR`, ...) in a persisted `OUT`: the Makefile's own
  dependency tracking still prints a "Repeating ..." rebuild message and
  *looks* like it picked up the new value, but the recompiled command line
  silently keeps the old one. `rm -rf <OUT>/metadata` (not the whole `OUT`
  tree) forces a re-parse while keeping other build artifacts
  (`docs/dv/process-logs/ws2/task-4-report.md`).
- **riscv-dv generator is VCS-compiled too.** The instruction generator
  (`out/build/instr_gen/`) is its own separate VCS build, distinct from the
  TB build (`out/build/tb/`) — a fresh regression run consumes two VCS
  builds and two VCS licenses, not one.
- **Site `module` command exits 1 even on success.** This site's Modules
  install prints `Module ERROR: invalid command name "module-hide"` Tcl
  noise on every load (harmless) and returns exit status 1 regardless of
  whether the load succeeded. Never `&&`-chain a `module load`;
  `ci/env.sh` already accounts for this.
- **VCS `-l` quirk: sim stdout lands in `rtl_sim_stdstreams.log`,** not
  `rtl_sim.log` (the latter also exists and duplicates the same content).
  Similarly: TB compile log is
  `out/build/tb/compile_tb_stdstreams.log`; the riscv-dv generator build
  log is `out/build/instr_gen/build_stdout.log`; the per-test
  cross-compile log is `out/run/tests/<test>.<seed>/compile.riscvdv.log`
  (0 bytes on a clean compile — benign).
- **`.vRefine` waivers are not applied automatically** — see Coverage
  section above.
- **`WAVES=1` needs `$VERDI_HOME` for FSDB waveforms** (`vcs.tcl`); without
  it, VCS falls back to VPD (`waves.vpd` instead of `waves.fsdb`).
- **FCIBH workaround (VCS-only).** VCS half-implements SystemVerilog's
  `default sequence` for transition-bin coverage: under `COV=1`,
  `core_ibex_fcov_if.sv`'s `cp_controller_fsm`/`cp_controller_fsm_sleep`
  covergroups fatally errored (`Error-[FCIBH] Illegal bin hit`) on legal FSM
  self-loops (e.g. `RESET=>RESET`) because VCS treats every unlisted
  transition as illegal rather than the empty set upstream intended. Fixed
  by guarding the `illegal_bins ... = default sequence;` blocks behind
  `` `ifndef FCOV_NO_DEFAULT_SEQUENCE ``, with that macro defined only in
  the `vcs` tool's compile command in
  `dv/uvm/core_ibex/yaml/rtl_simulation.yaml` (commit `dbba358f`) — no other
  simulator's build is affected. A real fix requires enumerating the FSM's
  legal transitions explicitly instead of relying on `default sequence`;
  tracked as a follow-up in `docs/dv/known-followups.md`.
- **`IBEX_CFG_*` define-name mismatch (fixed, commit `54e01775`).** The TB
  (`dv/uvm/core_ibex/tb/core_ibex_tb_top.sv`) previously guarded on
  `IBEX_CFG_BASE_ISA`/`IBEX_CFG_REG_FILE` while `util/ibex_config.py` emits
  `+define+IBEX_CFG_BaseIsa`/`+define+IBEX_CFG_RegFile` — the spelling
  mismatch meant the `` `ifdef ``s never matched, so every config silently
  elaborated with the TB's own CHERIoT-capable defaults regardless of
  `IBEX_CONFIG`. `RV32ZC` had no TB forwarding at all. All three are fixed;
  the TB now prints a `TB-CONFIG: BaseIsa=... RegFile=... RV32ZC=...`
  banner at time 0 as permanent runtime evidence that a given config
  actually reached elaboration — e.g. `opentitan` prints
  `TB-CONFIG: BaseIsa=BaseIsaRV32IorCHERIoT RegFile=RegFileFF
  RV32ZC=RV32ZcaZcbZcmp`, `small` prints
  `TB-CONFIG: BaseIsa=BaseIsaRV32I RegFile=RegFileFF RV32ZC=RV32Zca`
  (see `docs/dv/evidence/ws1-smoke-regr-note.txt`).
- **Direct `scripts/*.py` invocation needs `PYTHONPATH`.** Running any
  `dv/uvm/core_ibex/scripts/*.py` script directly (bypassing `make`) needs
  `PYTHONPATH` set via `scripts.setup_imports.get_pythonpath()` first — the
  Makefile does this automatically for every target; a bare
  `python3 scripts/metadata.py --help` will fail with
  `ModuleNotFoundError: No module named 'ibex_config'` otherwise.
