# T-027 evidence: cocotb on LSF through the shared-storage mirror

Owner: runtime. Date: 2026-09-03 (05:54 to 06:03 UTC). Build configuration: `opentitan`. Clone
git HEAD at the proving run: `3c623e5452939458326911d4d7ddfe37a1166991` (branch cleanroom/run-a).
Context: intervention log Q-012 (the clone lives on `/localdev`, a disk local to the submit host;
LSF compute hosts cannot see it); the default applied while the owner decides is a shared-storage
mirror, not a move of the owner's clone. Flow: `dv/auto_dv/flow/gen_mirror.py` plus the cocotb
wiring in `gen_build.py` and `gen_run.py` (API: `dv/auto_dv/docs/gen_runtime_api.md` Section 7b).

## 1. The mirror

Commands (login shell, `ci/env.sh` sourced, from `dv/auto_dv/flow/`):

```
python3 gen_mirror.py --sync --venv --spike      # first time: 05:54:39 to 05:55:44 UTC
python3 gen_mirror.py --sync                     # every re-sync (gen_regress.py does it before a cocotb build)
python3 gen_mirror.py --check                    # fresh / stale, exit 1 when stale
```

Result at `/proj_soc/user_dev/fzhang/ibex_dv_mirror` (wekafs, visible from every compute host):

| Item | Fact |
|---|---|
| rsync | `rtl/`, `vendor/lowrisc_ip/`, `vendor/google_riscv-dv/`, `util/`, `ci/`, `dv/auto_dv/` (without `work/`), `ibex_configs.yaml`, `python-requirements.txt`, `*.core`; excludes `.git`, `__pycache__`, out-trees, vdb, fsdb. 1429 files, 5 s first time, about 1 s afterwards. |
| venv | `bash ci/setup-venv.sh` of the mirror copy (`unset PYTHONPATH`, lock check inside the script) -> `<mirror>/.venv`, 396 MB, Python 3.12.10, cocotb 1.9.2, 59 s. `<mirror>/.venv/bin/cocotb-config --lib-name-path vpi vcs` = `<mirror>/.venv/lib/python3.12/site-packages/cocotb/libs/libcocotbvpi_vcs.so`; `--libpython` = `/tools_soc/opensrc/python/python-3.12.10/lib/libpython3.12.so.1.0` (shared tools tree). Log: `<mirror>_logs/venv.log`. |
| spike | `tools/spike` install tree copied (2.2 GB, 5 s). |
| manifest | `<mirror>/gen_mirror_manifest.yaml`: clone path, git HEAD and dirty flag, sync UTC, `tree_sha256` over the run-time-consumed files (`dv/auto_dv/**/*.py`, `ci/env.sh`, `ci/setup-venv.sh`, the two requirements files), file counts, venv facts, spike presence. |
| staleness | `--check` recomputes the clone and mirror hashes; a cocotb build refuses a stale mirror (observed once: a check 12 s after a sync was already stale because another role added a Python file; `gen_regress.py` therefore syncs right before the build), and a cocotb run refuses a mirror whose manifest hash differs from the one recorded in its build manifest. |

## 2. The proving run

```
python3 gen_regress.py --tests gen_cocotb_probe --tag t027_cocotb --base-seed 1 --force
```

- Testlist entries (`dv/auto_dv/flow/gen_testlist.yaml`): build `gen_smoke_cocotb` = `gen_smoke_tb_top`
  with `cocotb: true`; test `gen_cocotb_probe`, module `dv.auto_dv.flow.gen_cocotb_probe`, tier
  targeted, `measured: false` (flow equipment, not a DUT test), pass marker `GEN_COCOTB_PROBE_PASS`.
- Mirror sync at regression start: rc 0, 1.3 s; build manifest records the mirror
  (`state_at_build: fresh`, `tree_sha256 dc642d2b549676a3...`, git HEAD `3c623e545293...`).
- Compile (submit host, clone sources, SIM_RECIPE Section 2 + Section 4 triple):
  `+define+COCOTB_SIM +vpi -P <outdir>/gen_pli.tab -load
  /proj_soc/user_dev/fzhang/ibex_dv_mirror/.venv/lib/python3.12/site-packages/cocotb/libs/libcocotbvpi_vcs.so`.
  0 errors; warnings SIOB x32, LCA_FEATURES_ENABLED x1 (as every build) plus `VPI-CT-NS` x4 (new
  with `+vpi`; see the compile.log excerpt in Section 4).
- Run: LSF job 10930476 on `soc-c-15`, CPU 1.15 s, wall 23.4 s, exit 0, verdict PASS
  (`sim_stdout.log` scanned together with `sim.log`; cocotb summary TESTS=1 PASS=1 FAIL=0).
- Job script (`runs/gen_cocotb_probe_315612868/run_cmd.sh`): `source
  /proj_soc/user_dev/fzhang/ibex_dv_mirror/ci/env.sh` (activates the mirror venv), then `MODULE=
  dv.auto_dv.flow.gen_cocotb_probe PYTHONPATH=/proj_soc/user_dev/fzhang/ibex_dv_mirror
  TOPLEVEL=gen_smoke_tb_top TOPLEVEL_LANG=verilog RANDOM_SEED=315612868 SIM_DIR=<run dir>`, then
  the simv with `+ntb_random_seed=315612868` (SIM_RECIPE Sections 4 and 5).

Log lines proving cocotb loaded on the compute host (`lsf.out` and `sim_stdout.log` of the run):

```
GEN_RUN_ENV env_sh=/proj_soc/user_dev/fzhang/ibex_dv_mirror/ci/env.sh VIRTUAL_ENV=/proj_soc/user_dev/fzhang/ibex_dv_mirror/.venv LIBPYTHON_LOC=/tools_soc/opensrc/python/python-3.12.10/lib/libpython3.12.so.1.0 python3=/proj_soc/user_dev/fzhang/ibex_dv_mirror/.venv/bin/python3
GEN_RUN_SEED ntb_random_seed=315612868 RANDOM_SEED=315612868 host=soc-c-15 utc=2026-09-03T06:02:41Z
     -.--ns INFO     gpi  ..mbed/gpi_embed.cpp:108  in set_program_name_in_venv  Using Python virtual environment interpreter at /proj_soc/user_dev/fzhang/ibex_dv_mirror/.venv/bin/python
     -.--ns INFO     gpi  ../gpi/GpiCommon.cpp:101  in gpi_print_registered_impl  VPI registered
     0.00ns INFO     cocotb   Running tests with cocotb v1.9.2 from /proj_soc/user_dev/fzhang/ibex_dv_mirror/.venv/lib/python3.12/site-packages/cocotb
     0.00ns INFO     cocotb   Seeding Python random module with supplied seed 315612868
     0.00ns INFO     cocotb.regression   Found test dv.auto_dv.flow.gen_cocotb_probe.gen_cocotb_probe
     0.00ns INFO     cocotb.gen_smoke_tb_top   GEN_COCOTB_PROBE alive host=soc-c-15 pid=1548249 RANDOM_SEED=315612868 cocotb=1.9.2
     0.00ns INFO     cocotb.gen_smoke_tb_top   GEN_COCOTB_PROBE toplevel=gen_smoke_tb_top python_module=/proj_soc/user_dev/fzhang/ibex_dv_mirror/dv/auto_dv/flow/gen_cocotb_probe.py
  2055.00ns INFO     cocotb.gen_smoke_tb_top   GEN_COCOTB_PROBE cycles=200 rvfi_retired_seen=197
  2055.00ns INFO     cocotb.gen_smoke_tb_top   GEN_COCOTB_PROBE_PASS
  2055.01ns INFO     cocotb.regression   gen_cocotb_probe passed
** dv.auto_dv.flow.gen_cocotb_probe.gen_cocotb_probe   PASS        2055.01           0.06      36385.70  **
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                    2055.01           0.10      21542.04  **
$finish at simulation time               205501
```

The interpreter, the cocotb package, the VPI library and the test module all resolve to the
mirror; the SV smoke top kept driving the NOP program (197 RVFI retirements in 200 observed
cycles); cocotb ended the simulation after its test, before the smoke's own `$finish` at 3000
cycles. `results.xml` (cocotb) names the mirror module path and the seed. Coverage: the probe is
`measured: false`, so its data went to `cov_unmeasured/gen_smoke_cocotb.vdb` (informational
report produced) and the measured merge reports `ok_no_measured_tests`.

First attempt (job 10930445 on `soc-c-19`, same code path, 05:58 UTC): cocotb loaded and the
probe passed identically, but the flow verdict said FAIL because the pass marker is emitted by
Python logging to stdout, which the VCS `-l` log does not capture. Fix: the job script redirects
simv stdout and stderr to `sim_stdout.log`, and `gen_verdict.decide` scans both files. The
second run (above) is the one the verdict agrees with.

## 3. Seed rule, verdict rule

One seed, both sides: `+ntb_random_seed=315612868` on the simv command line (`sim.log` head) and
`RANDOM_SEED=315612868` in the job environment, echoed as `GEN_RUN_SEED ...` at time zero and
confirmed by cocotb's "Seeding Python random module with supplied seed 315612868". Verdict from
collected mechanisms: cocotb summary FAIL count, `CRITICAL`, UVM counts, `$fatal`, marker, exit code
as one more mechanism (`gen_verdict.py`).

## 4. Compile warning new with +vpi

`Warning-[VPI-CT-NS]` x4 in `build/gen_smoke_cocotb/compile.log` (the other classes are the
T-005/T-010 ones). Excerpt copied from the log:

```
Warning-[VPI-CT-NS] VPI function is not supported
  The VPI function 'vpi_register_cb' is not supported in the compiler.
  Please fix the code being referred to by the '-load' compile option.
```

VCS reports it four times for the cocotb library's start-up callbacks; the run shows the callbacks
work (`VPI registered`, tests found and run), so the warning is informational for this cocotb
version. Recorded, not suppressed.

## 5. Limits stated

- The mirror is a copy: anything a cocotb test imports must be re-synced first (the flow does it
  at regression start; a manual `gen_run.py` against an older build fails loud on the hash).
- Parallel cocotb regressions that edit Python between their syncs would race on the single
  mirror; the run-time hash check turns that into a loud failure, not a silent one. The runtime
  role serves requests sequentially.
- Spike is mirrored but not exercised here (no DPI shim exists yet); its shared path is
  `/proj_soc/user_dev/fzhang/ibex_dv_mirror/tools/spike`.
- The probe checks only that Python sees RVFI retirements; it is flow equipment and never enters
  a measured merge.

## 6. LSF accounting

Jobs of T-027: 10930445 (first probe run, verdict fixed afterwards), 10930446 (waves repro, review
fix), 10930458 (smoke recheck), 10930476 (probe, proving run). `bjobs -w` after the last run: `No
unfinished job found`; every manifest `lsf_jobs_left: []`.
