# T-010 evidence: compile path with coverage, LSF run, URG report, run-request queue

Owner: runtime. Date: 2026-09-03 (05:18 to 05:37 UTC). Build configuration: `opentitan`
(`util/ibex_config.py opentitan vcs_opts`, verbatim in the compile command below). Git HEAD at
the time of the runs: `0b9c93c72e52f030f07d0ba71f3d01d673c6cf48` (branch cleanroom/run-a).
Tools: VCS X-2025.06-SP2_Full64, URG X-2025.06-SP2, Python 3.12.10 (clone venv), LSF 10.1 queue
`regress`. Flow scripts: `dv/auto_dv/flow/` (API: `dv/auto_dv/docs/gen_runtime_api.md`).
Out-trees (not committed) live under the shared out root `/proj_soc/user_dev/fzhang/ibex_dv_out`
(Section 1 explains why).

## 1. Site finding: the clone is on local disk; LSF needs a shared out root

- Probe job 10930240 (`hostname`) dispatched on the `regress` queue in 2 s, but `bhist -l`
  showed `Execution CWD </tmp>`: the site falls back to `/tmp` when the submission cwd does not
  exist on the compute host.
- Job 10930291 (first attempt to run `gen_run.py` from the clone) exited 1 after 16 s with no
  output: `/localdev/fzhang/ws/ibex-challenge` does not exist on `soc-c-16`. `df -hT` on the submit
  host: `/localdev` is `/dev/nvme1n1p2 xfs` (local NVMe of `soc-l-11`); `soc-l-11` is not an LSF
  execution host (`bhosts soc-l-11`: bad host name).
- Job 10930309 proved the workaround: `/proj_soc/user_dev/fzhang` (wekafs, shared) is visible and
  writable from `soc-c-16`; a copy of `ci/env.sh` sourced there with `IBEX_ENV_TOOLCHECK=off` yields
  `vcs`, `urg`, `timeout`, `VCS_HOME`, `VERDI_HOME` and the license variables. Python there is the site
  3.9 without the venv, so the LSF job is pure bash.
- Consequence built into the flow: compile on the submit host (the clone is there), out-trees on the
  shared root (`dv/auto_dv/work/runtime/gen_site.yaml`, env override `GEN_DV_OUT_ROOT`), the run
  job is `bash <run dir>/run_cmd.sh` sourcing the staged `env.sh`, all LSF paths absolute with
  `-cwd`. SIM_RECIPE Section 7 ("shared storage only") is satisfied for everything an LSF job
  touches. Open item for the owner (through the Orchestrator): cocotb runs on LSF need the clone
  (its `.venv` VPI library and Python test modules) on shared storage; pure-SV runs are unaffected.

## 2. Compile through gen_build.py with coverage scoped to the DUT instance

Command (from `gen_regress.py --tier smoke --tag t010_smoke --base-seed 1`, recorded in
`<out root>/regress_t010_smoke/build/gen_smoke/compile_cmd.sh`; identical flag set to the
standalone trial `gen_build.py --build gen_smoke --coverage --cond --diag-noconst --outdir <out
root>/t010_smoke_cov`, which added `-diag noconst`):

```
vcs -full64 -sverilog -f dv/auto_dv/tb/gen_rtl.f -f dv/auto_dv/tb/gen_smoke_tb.f \
    -top gen_smoke_tb_top -ntb_opts uvm-1.2 +define+UVM +define+UVM_REGEX_NO_DPI +define+RVFI \
    +define+BaseIsa=ibex_pkg::BaseIsaRV32IorCHERIoT -pvalue+RV32E=0 \
    +define+RV32M=ibex_pkg::RV32MSingleCycle +define+RV32B=ibex_pkg::RV32BOTEarlGrey \
    +define+RV32ZC=ibex_pkg::RV32ZcaZcbZcmp +define+RegFile=ibex_pkg::RegFileFF \
    -pvalue+BranchTargetALU=1 -pvalue+WritebackStage=1 -pvalue+ICache=1 -pvalue+ICacheECC=1 \
    -pvalue+ICacheScramble=1 -pvalue+BranchPredictor=0 -pvalue+DbgTriggerEn=1 -pvalue+SecureIbex=1 \
    -pvalue+PMPEnable=1 -pvalue+PMPGranularity=0 -pvalue+PMPNumRegions=16 -pvalue+MHPMCounterNum=10 \
    -pvalue+MHPMCounterWidth=32 \
    -timescale=1ns/10ps -licqueue -LDFLAGS '-Wl,--no-as-needed' \
    -CFLAGS '--std=c99 -fno-extended-identifiers' -xlrm uniq_prior_final -lca -kdb \
    -Mdir=<outdir>/vcs_simv.csrc -o <outdir>/vcs_simv -debug_access+pp \
    -cm line+cond+tgl+assert+fsm+branch -cm_tgl portsonly -cm_tgl structarr -cm_report noinitial \
    -cm_seqnoconst -cm_dir <outdir>/build.vdb -cm_hier <outdir>/cm_hier.cfg \
    -l <outdir>/compile.log
```

`cm_hier.cfg` (rendered from `dv/auto_dv/flow/gen_cm_hier.cfg`): `+tree gen_smoke_tb_top.u_dut`.

compile.log summary (both builds): 0 `Error-[...]`; warning classes `Warning-[SIOB]` x32 (all
`rtl/ibex_core.sv` RVFI generate loop, the class T-005 classified as benign) and
`Warning-[LCA_FEATURES_ENABLED]` x1 (from `-lca`); no warning about `-cm_hier` with `-cm_tgl
portsonly` (rtl-arch exclusion draft B.4, confirmed); `CPU time: 10.285 seconds to compile + .274
seconds to elab + .767 seconds to link`; `Verdi KDB elaboration done`. Build wall time 33 s through
the flow. Manifest: `<out root>/regress_t010_smoke/build/gen_smoke/build_manifest.yaml` (filelist
sha256, combined source sha256 over 95 files, git HEAD, tool versions, flag groups).

Condition coverage trial: VCS accepted `-cm line+cond+tgl+assert+fsm+branch` and `-diag noconst`
without a message; URG reports COND (Section 4). `gen_regress.py` therefore uses cond by default.

## 3. Run through gen_run.py on LSF, one seed

Standalone trial (out-tree `t010_smoke_cov`):

```
python3 dv/auto_dv/flow/gen_run.py --build-dir <out root>/t010_smoke_cov --test gen_smoke --seed 1 \
    --run-dir <out root>/t010_smoke_cov/runs/gen_smoke_1 --cov-dir <out root>/t010_smoke_cov/cov/gen_smoke.vdb --lsf
```

LSF job 10930316 on `soc-c-11` (pend 1.4 s, wall 10.6 s, CPU 1.33 s from the LSF job report in
`lsf.out`). Verdict PASS: `GEN_SMOKE_PASS` marker present, `$finish` seen, no collected failure
mechanism; `result.yaml` records vdb `.../cov/gen_smoke.vdb`, `cm_name: test_gen_smoke_1`.
Seed record at time zero (`run.log`): `GEN_RUN_SEED test=gen_smoke seed=1 ntb_random_seed=1
RANDOM_SEED=1`; `sim.log` head: `Command: .../vcs_simv +vcs+lic+wait +ntb_random_seed=1
+UVM_TESTNAME=none +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan
+gen_smoke_cycles=3000 -l .../sim.log -cm line+cond+tgl+assert+fsm+branch -cm_dir ... -cm_name
test_gen_smoke_1 -cm_log /dev/null -assert nopostproc`, then the eleven `GEN_CONFIG_BANNER` lines
(build_config=opentitan), `GEN_SMOKE: retired=2995 alerts=0`, `GEN_SMOKE_PASS`, and VCS's
`VCS Coverage Metrics: during simulation line, cond, FSM, branch, tgl was monitored`.

Lesson recorded in the flow: with a run-time `-cm_dir` different from the compile-time one, URG
loaded a "Limited design" (assertion data only, `Warning-[UCAPI-LDAST]`) until the compile-time
`build.vdb` was also given with `-dir`. The flow now runs every test into the build's `build.vdb`
(distinct `-cm_name` per test+seed) and merges from there.

Regression path (the deliverable path), `gen_regress.py --tier smoke --tag t010_smoke --base-seed 1`:
build 33 s; run `gen_smoke` seed 330815564 (derived from base seed 1) as LSF job 10930323 on
`soc-c-11`, PASS in 14.6 s; URG merge 11 s; manifest
`<out root>/regress_t010_smoke/manifest.yaml`: 1 planned, 1 pass, `lsf_cost: jobs 1, cpu_s 1.3,
slot_s 14.6, pend_s 1.4`, `lsf_jobs_left: []`.

## 4. URG report and metric availability (DV_prompt Section 4)

Merge command (`<out root>/regress_t010_smoke/cov/urg_cmd.sh`):

```
urg -full64 -format both -dbname <cov>/merged.vdb -report <cov>/report -log <cov>/merge.log \
    -show ratios -dir <out root>/regress_t010_smoke/build/gen_smoke/build.vdb
```

`report/dashboard.txt`, Total Coverage Summary (1 test):

```
SCORE   LINE              COND              TOGGLE             FSM          BRANCH           ASSERT
 37.82   55.09 2397/4351   37.41 3579/9566    7.40 1994/26958    6.98 6/86   41.03 992/2418   79.01 143/181
```

`report/hierarchy.txt`, DUT-scope row `gen_smoke_tb_top.u_dut` (the gate number):

```
 38.04   55.09 2397/4351   37.41 3579/9566    7.40 1994/26958    6.98 6/86   41.03 992/2418   80.34 143/178  u_dut
```

Metric availability for this DUT, from the report:

| Metric | Reported by URG | Evidence |
|---|---|---|
| line | yes | LINE column, 2397/4351 |
| condition | yes | COND column, 3579/9566 (trial flag `-cm cond` accepted by VCS and URG) |
| toggle | yes | TOGGLE column, 1994/26958 (ports only, `-cm_tgl portsonly`) |
| FSM | yes | FSM column, 6/86 transitions. VCS extracted six state machines: `ibex_compressed_decoder::cm_state_q`, `ibex_controller::ctrl_fsm_cs` (10 states, 26 transitions), `ibex_load_store_unit::ls_fsm_cs` and `cap_rx_fsm_q`, `ibex_multdiv_fast::md_state_q`, `ibex_icache::inval_state_q` (report/modinfo.txt, "FSM Coverage for Module" sections). URG scores transitions; states are listed "Not included in score". So FSM is applicable, not n/a. |
| assertion | yes | ASSERT column, 143/178 in the DUT scope. The grand total 143/181 adds three `uvm_pkg` assertions (`uvm_component_name_check_visitor::visit`, `uvm_reg_map::do_read`, `uvm_reg_map::do_write`, 0 attempts) that sit outside the `-cm_hier` tree; the exclusion file should exclude them or the DUT row is used. |
| branch | yes | BRANCH column, 992/2418 |
| functional (group) | not applicable yet | no GROUP column: no covergroup exists in the smoke build. Recorded as n/a, not 0. |

Scope check: the `gen_smoke_tb_top` node and the `u_dut` node carry identical line/cond/toggle/
fsm/branch numbers, so no TB-top code was instrumented; `gen_dut_top` itself appears with toggle
objects only (its ports, 312/2420), as expected for the wrapper that is the DUT by ruling.

Coverage numbers are near-zero-effort smoke numbers (a NOP program); they prove the path only.

## 5. -cm_seqnoconst and the CHERIoT constant-tie cone (rtl-arch exclusion draft Part B.3)

Constant analysis recognises the wrapper tie. `-diag noconst` wrote `constfile.txt` (moved by the
flow into `<out root>/t010_smoke_cov/constfile.txt`, 673 constant entries): for instance
`gen_smoke_tb_top.u_dut.u_ibex_core` it lists `cheriot_enable_i[0]` value `0 always`,
`cheriot_enable_i[2:1]` value `1 always`, `cheriot_enable_i[3]` value `1 always`, each with
`declaration: rtl/ibex_core.sv:67` and `location: dv/auto_dv/tb/gen_dut_top.sv:274 ... input:
CheriotEnable`; the same constants propagate into `if_stage_i` (`rtl/ibex_core.sv:547`), and 36
entries belong to `gen_smoke_tb_top.u_dut.u_ibex_core.g_cheriot_ex.u_ibex_cheriot_ex`. 441 of the
673 entries mention `cheriot`.

URG marks only the directly dependent objects Unreachable. `gen_cov_report.py unreachable
--report-dir <cov2>/report --module ibex_cheriot_ex` on the trial report: 5 line rows, 54 condition
vectors and 22 toggle rows marked Unreachable (132 marks in the section), yet the module is still
scored `LINE 37.50 126/336, COND 19.60 68/347, TOGGLE 1.25 30/2404, BRANCH 28.35 36/127`. For
comparison `ibex_decoder`: 136 unreachable line rows, 62 condition vectors; `ibex_core`: 107 line
rows, 74 condition vectors. Conclusion for rtl-arch: the tie is propagated (no `-cm_constfile`
needed to declare it), the first report shows a partial automatic carve-out, and the remaining
CHERIoT-only logic (decode of `instr_is_cheriot`, the cheriot_ex data path) needs the annotated
`.el` entries of Part A; `gen_regress.py --elfile` applies them at merge time. Instance names
confirmed for the exclusion file: `gen_smoke_tb_top.u_dut.u_ibex_core`,
`gen_smoke_tb_top.u_dut.u_register_file`; the real TB top will substitute its own top name.

## 6. Run-request queue served end to end

Three self-test requests written to `dv/auto_dv/work/runtime/requests/` and served by
`python3 dv/auto_dv/flow/gen_serve_requests.py --once` (05:34 to 05:35 UTC); all moved to `done/`,
results under `dv/auto_dv/work/runtime/results/<name>/manifest.yaml`:

| Request | Purpose | Content | Decision | Result |
|---|---|---|---|---|
| runtime-001 | 1 | gen_smoke, 2 seeds, coverage yes | accepted (`--tests gen_smoke --seeds 2`) | seeds 2011856945 and 416127737, LSF jobs 10930325 and 10930326, both PASS; URG report `<out root>/regress_req_runtime-001/cov/report` (2 tests in report) |
| runtime-002 | 1 | `tests: full` | refused in the manifest: "purpose 1 (bring-up) runs exactly one named test, got ['full']" | no job submitted |
| runtime-003 | 3 | gen_smoke seed 330815564, coverage no | accepted (`--repro gen_smoke 330815564`) | LSF job 10930333, PASS, no coverage (repro) |

`dv/auto_dv/docs/gen_dashboard.md` was generated from these manifests by `gen_dashboard.py`
(3 regressions, 3 requests, closure-round count 0).

## 7. LSF accounting

Jobs of this task: 10930240, 10930304, 10930309 (probes), 10930291 (failed: local-disk clone),
10930316 (gen_run trial), 10930323 (t010_smoke), 10930325 and 10930326 (runtime-001), 10930333
(runtime-003). `bjobs -w` at the end: `No unfinished job found`. Every regression manifest records
`lsf_jobs_left: []`.

## 8. Acceptance (task statement)

- Green compile with coverage instrumentation scoped to the gen_dut_top instance: yes (Section 2).
- LSF run through gen_run.py with one seed, per-test vdb, URG report: yes (Sections 3 and 4).
- Condition and FSM coverage availability stated from the report: yes (Section 4 table).
- -cm_seqnoconst effect on the CHERIoT cone stated: partial, with counts (Section 5).
- A run request written by another role can be served end to end: yes (Section 6, the queue
  accepts any role slug; the self-test used the runtime slug).
- `bjobs` shows nothing left: yes (Section 7).
- cocotb triple: compiled into a build only on request (`--cocotb`); not exercised in T-010 because
  no cocotb test exists yet and cocotb runs on LSF are blocked by Section 1 until the clone is on
  shared storage. Recorded, not hidden.
