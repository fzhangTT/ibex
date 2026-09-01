# Building and Running Ibex DV Simulations (VCS)

This document covers the `core_ibex` UVM DV flow (`dv/uvm/core_ibex`) under
Synopsys VCS with Spike as the co-simulator, on this site's tooling. Every
command below was actually run during WS1 bring-up; wall-times are what was
observed on this host (a 192-core machine), not vendor/upstream estimates.

## One-time setup

Run once per checkout (or whenever the tools move):

If you are not fzhang, first `export IBEX_TOOLS_DIR=/path/to/writable/dir` —
it defaults to `/localdev/fzhang/ws/tools`.

```bash
source ci/env.sh
bash ci/setup-venv.sh
bash ci/build-spike.sh
bash ci/get-toolchain.sh
```

- `ci/env.sh` is the single source of truth for tool paths: it loads the
  site's VCS/licenses/dtc Modules (see Gotchas below), and exports
  `IBEX_PYTHON`, `RISCV_GCC`/`RISCV_TOOLCHAIN`, `SPIKE_PATH`, and the venv's
  `PKG_CONFIG_PATH`. Source it in every new shell before running anything
  else in this document.
- `ci/setup-venv.sh` creates `.venv/` and installs from `ci/requirements.lock`
  when present, falling back to `python-requirements.txt` (including
  riscv-dv's own requirements) otherwise, via `$IBEX_PYTHON`. Idempotent —
  safe to re-run.
- `ci/build-spike.sh` clones and builds the lowRISC fork of Spike (pinned
  revision) and installs it to `$IBEX_TOOLS_DIR/spike-ibex-cosim`. Requires
  `dtc` on PATH, which `ci/env.sh` loads via Modules. Observed: ~51s wall
  time on this host.
- `ci/get-toolchain.sh` downloads and unpacks the lowRISC
  `rv32imcb` prebuilt GCC toolchain to
  `$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb`. Observed: ~1s to
  download the 41.8M tarball on this host's network; idempotent (skips the
  download if the tarball is already present).

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
second from-scratch run during doc verification took ~156s instead (same
~39s TB compile, extra time in env/module-load overhead) — expect some
run-to-run variance on this host, not just this one number.

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

- `TEST=all` (the Makefile default) — every riscv-dv **and** directed test
  in both testlists.
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

`IBEX_CONFIG` selects one of 8 named configs from the top-level
`ibex_configs.yaml`. The DV Makefile's default is `opentitan`
(`dv/uvm/core_ibex/Makefile`); the top-level RTL build Makefile's default is
`small` (`Makefile`) — pass `IBEX_CONFIG` explicitly if you need one
consistently across both.

| Config | Notes |
|---|---|
| `small` | 2-stage pipeline, no branch-target ALU, 3-cycle mul, no ICache/PMP/SecureIbex. `BaseIsa=RV32I`, `RV32ZC=Zca`. |
| `opentitan` | Matches the OpenTitan project's Ibex integration. `BaseIsa=RV32IorCHERIoT`, ICache+ECC+scramble, SecureIbex, PMP (16 regions), DbgTriggerEn. DV Makefile default. |
| `maxperf` | 3-stage pipeline, branch-target ALU, 1-cycle mul, no ICache/PMP. Max performance ignoring the (unverified) branch predictor. |
| `maxperf-pmp` | `maxperf` + PMP enabled, 16 regions. |
| `maxperf-pmp-bmbalanced` | `maxperf` + PMP + balanced bitmanip (`RV32BBalanced`). |
| `maxperf-pmp-bmfull` | `maxperf-pmp` + full bitmanip (`RV32BFull`). |
| `maxperf-pmp-bmfull-icache` | `maxperf-pmp-bmfull` + ICache/ICacheECC enabled. |
| `experimental-branch-predictor` | `maxperf`-style config with `BranchPredictor=1` — experimental, not fully verified. |

Each riscv-dv/directed testlist entry may carry an `rtl_params` map (e.g.
`SecureIbex: 1`); `scripts/ibex_cmd.py:filter_tests_by_config()` drops any
test whose `rtl_params` aren't all satisfied by the selected config before
building the regression's test list — e.g. `SecureIbex`-gated tests are
silently excluded from a `small` or `maxperf` run, not failed.

## Gotchas

- **Stale `metadata.pickle`.** After editing a testlist or
  `ibex_configs.yaml`, `metadata.py` refuses to recreate metadata if
  `out/metadata/metadata.pickle` already exists from a prior run. Use
  `make clean` or a fresh `OUT=<new_dir>` after such edits.
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
  out of scope here.
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
