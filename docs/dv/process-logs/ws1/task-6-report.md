# Task 6 Report: E2E smoke test — riscv_arithmetic_basic_test under VCS + spike cosim

Branch: `fzhang/auto-dv-setup`

## Summary

The full end-to-end flow (riscv-dv generation -> cross-compile -> VCS TB
build -> spike cosim simulation) passed on the **first attempt**, with no
triage iterations required. No flow-script or Makefile fixes were needed.

```
100.00% PASS 1 PASSED, 0 FAILED
riscv_arithmetic_basic_test.1: PASS
```

Banner in `rtl_sim_stdstreams.log` matches the expected opentitan
configuration exactly:

```
TB-CONFIG: BaseIsa=BaseIsaRV32IorCHERIoT RegFile=RegFileFF RV32ZC=RV32ZcaZcbZcmp
```

## Step 1: Run the full flow

Command run (matches the brief exactly):

```bash
source ci/env.sh && cd dv/uvm/core_ibex && make clean && \
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1
```

Process:
1. Sourced `ci/env.sh` directly in the shell first to confirm tool
   resolution (module-load noise from the site's broken `module-hide`
   Tcl proc is expected and harmless — env.sh already tolerates it via
   `|| true` on the `dtc` load; the `synopsys/licenses` and
   `synopsys/vcs` loads print the same Tcl error but still export a
   working `vcs` on PATH, confirmed by the trailing
   `ibex env: vcs=... gcc=... spike=...` banner showing all three
   resolved).
2. Ran `( cd dv/uvm/core_ibex && ... make clean )` — removed `out/` and
   the generated `riscv_core_setting.sv`, confirming metadata.pickle
   from any prior run was gone before the fresh build.
3. Launched the build+test command via `nohup` in the background,
   redirected to a log file in the scratchpad directory, per the
   process rule against parking on background-task notifications.
4. Polled the log with a bounded (300 s deadline) `until` loop watching
   for the process to exit or for PASS/FAIL/error markers to appear,
   rather than waiting on a notification. The loop returned almost
   immediately — the run had already finished.

## Step 2: Triage loop

**Not needed.** The run passed cleanly on the first attempt:

```
Building RTL testbench
Generating core configuration file
Building randomized test generator
Running randomized test generator to create assembly file .../test.S
Compiling riscvdv test assembly to create binary at .../test.bin
Running RTL simulation at .../riscv_arithmetic_basic_test.1
Collecting simulation results and checking logs of testcase at .../trr.yaml
Collecting up results of tests into report regr.log
Warning: Not generating coverage summary, unsupported simulator vcs
100.00% PASS 1 PASSED, 0 FAILED
```

No fixes to flow scripts, Makefiles, or defines were required. The
prior tasks' work (env.sh, IBEX_CFG define fix, TB-CONFIG banner) held
up under a real VCS run.

### Sanity-checking the surprisingly fast wall time

The whole flow completed in well under a minute of wall time, far
faster than the brief's 30-60 min first-time estimate (and the
coordinator's own "well under 20 min" revised expectation). Verified
this was a genuine fresh build rather than stale/reused binaries, since
`make clean` had just removed `out/` in its entirety:

- `out/build/instr_gen/build_stdout.log`, `compile.log` (575 KB),
  `vcs_simv` (1.3 MB), and fresh `vcs_simv.csrc`/`vcs_simv.daidir`
  directories were all created at 17:24:42-17:24:55 — i.e. created
  fresh by this run, not reused from a prior build.
- `out/build/tb/compile_tb_stdstreams.log` shows a full 103-module
  recompile (`recompiling module ...` x103, `All of 103 modules done`)
  followed by:
  ```
  CPU time: 14.632 seconds to compile + .281 seconds to elab + 23.766 seconds to link
  ```
  i.e. ~39 s TB compile — this matches the coordinator's stated "TB
  compile ~40s (not the brief's 10 min)" for this host exactly.
- The riscv-dv instruction-generator VCS build (a separate VCS
  invocation) completed in roughly 13 s (`build_stdout.log` timestamp
  17:24:42 -> `vcs_simv` mtime 17:24:55).

Conclusion: the host's VCS + this repo's TB size genuinely compiles and
sims this fast — nothing was skipped or cached from a previous run.

## Step 3: Verify pass and banner

```bash
$ grep -E "PASS|FAIL" out/run/regr.log
100.00% PASS 1 PASSED, 0 FAILED
riscv_arithmetic_basic_test.1: PASS
[PASSED]

$ grep "TB-CONFIG" out/run/tests/*/rtl_sim*.log | head -1
out/run/tests/riscv_arithmetic_basic_test.1/rtl_sim_stdstreams.log:TB-CONFIG: BaseIsa=BaseIsaRV32IorCHERIoT RegFile=RegFileFF RV32ZC=RV32ZcaZcbZcmp
```

`trr.yaml` confirms:
```
passed:                   True
failure_mode:
failure_message:
testtype:                 TestType.RISCVDV
rtl_simulator:            vcs
iss_cosim:                spike
```

The `.name()` enum banner rendered correctly under VCS (no empty/garbage
output) — the documented format-specifier fallback (`%0d`) was **not**
needed.

Evidence copied:
```bash
REPO=$(git rev-parse --show-toplevel)
mkdir -p "$REPO/docs/dv/evidence"
cp out/run/regr.log "$REPO/docs/dv/evidence/ws1-smoke-regr.log"
```

## Step 4: Commit evidence

```
2e184fd7 [dv] WS1 gate evidence: riscv_arithmetic_basic_test passes under VCS+spike
```

`docs/dv/evidence/ws1-smoke-regr.log` added (22 lines). Working tree
confirmed clean after commit (`git status --short` empty); no `out*/`
directories were staged or committed.

## Wall-times per stage (approximate, from artifact mtimes / build logs)

| Stage | Duration |
|---|---|
| Env source + module loads | a few seconds (not separately timed) |
| `make clean` | < 1 s |
| riscv-dv instr-gen VCS build | ~13 s |
| Test generation (riscv-dv run.py, gen assembly) | a few seconds |
| Cross-compile (gcc + objcopy to test.bin) | < 1 s |
| TB VCS build (103 modules) | ~39 s (14.6 s compile + 0.3 s elab + 23.8 s link, per VCS's own report) |
| RTL sim + spike cosim | ~10 s (rtl_sim_stdstreams.log appeared ~10 s after test.bin) |
| **Total (launch to regr.log)** | **under 60 s** |

## Working command line for BUILD_AND_SIM.md (Task 8)

```bash
source ci/env.sh
cd dv/uvm/core_ibex
make clean
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1
```

## Final evidence

- Test verdict: **PASSED** (`riscv_arithmetic_basic_test.1: PASS`, 100.00% PASS, 0 FAILED)
- Banner observed: `TB-CONFIG: BaseIsa=BaseIsaRV32IorCHERIoT RegFile=RegFileFF RV32ZC=RV32ZcaZcbZcmp`
- Evidence file: `docs/dv/evidence/ws1-smoke-regr.log` (committed at `2e184fd7`)
- No flow/Makefile fixes were needed; no `COSIM_SIGSEGV_WORKAROUND` needed; no `%0d` banner fallback needed.
