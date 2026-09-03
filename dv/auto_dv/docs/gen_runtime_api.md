# Runtime flow API (dv/auto_dv/flow)

Owner: runtime. Build configuration: `opentitan` (fixed, DV_prompt.txt Section 2). Every script
is Python 3 in `dv/auto_dv/flow/`, run from a login shell with the environment sourced:

```
bash -lc 'source ci/env.sh && python3 dv/auto_dv/flow/<script>.py ...'
```

The flow is built from `docs/dv/SIM_RECIPE.md` alone (Sections 2 to 9). Deliverable 8 of
DV_prompt.txt Section 11 is this directory plus `gen_testlist.yaml`. Evidence that the path works:
`dv/auto_dv/evidence/gen_t010_compile_path.md`.

## 0. Site facts the flow encodes

- **Out root on shared storage.** The clone lives on `/localdev` (local NVMe of the submit host
  `soc-l-11`); LSF compute hosts cannot see it. Every out-tree that an LSF job reads or writes
  therefore lives under the out root named in `dv/auto_dv/work/runtime/gen_site.yaml`
  (`out_root:`), overridable by the environment variable `GEN_DV_OUT_ROOT`. Current value:
  `/proj_soc/user_dev/fzhang/ibex_dv_out`. Without either, the root is `dv/auto_dv/work/runtime/out`
  (correct only when the clone itself is on shared storage).
- **Compile on the submit host, simulate on LSF.** `vcs` needs the sources, so the compile runs
  where the clone is; the simulation job is a self-contained bash script that sources a copy of
  `ci/env.sh` staged into the build outdir and runs the simv from the shared out-tree. `--build-lsf`
  and `--lsf` on the build exist for a clone on shared storage.
- **cocotb runs on LSF are blocked until the clone is on shared storage**: the VPI library and the
  Python test modules live in the clone's `.venv` and tree. Pure-SV runs are unaffected. A
  cocotb build is possible today (`--cocotb`) and a cocotb run works in `--local` mode.
- **LSF paths are absolute** and the job gets `-cwd <run dir>` (the site default CWD is `/tmp`).
- **Constants home.** Paths, plusarg names, log markers, LSF defaults and schema keys live in
  `gen_flow_const.py` only. `python3 gen_flow_const.py --check` proves the plusarg names shared with
  the SV constants home `dv/auto_dv/tb/gen_tb_pkg.sv` are identical.

## 1. gen_build.py (compile one TB top)

```
gen_build.py --build <name> [--coverage] [--cond] [--diag-noconst] [--cocotb] [--waves]
             [--define NAME ...] [--outdir DIR] [--force] [--lsf] [--timeout-s N]
```

- `--build`: key under `builds:` of `gen_testlist.yaml` (tb_top, dut_instance, filelists, defines).
- Flag set: SIM_RECIPE Section 2 exactly (`-full64 -sverilog -f ... -top ... -ntb_opts uvm-1.2
  +define+UVM +define+UVM_REGEX_NO_DPI`, the `util/ibex_config.py opentitan vcs_opts` output,
  `-timescale=1ns/10ps -licqueue -LDFLAGS -CFLAGS -xlrm uniq_prior_final -lca -kdb`,
  `-debug_access+pp`, or `-debug_access+all -ucli` with `--waves`).
- `--coverage`: Section 3 compile flags `-cm line+tgl+assert+fsm+branch -cm_tgl portsonly -cm_tgl
  structarr -cm_report noinitial -cm_seqnoconst -cm_dir <outdir>/build.vdb -cm_hier <outdir>/cm_hier.cfg`.
  The hier file is rendered from the checked-in template `gen_cm_hier.cfg` as
  `+tree <tb_top>.<dut_instance>`, so only the gen_dut_top instance is instrumented.
- `--cond`: adds condition coverage (`-cm line+cond+tgl+assert+fsm+branch`). Trial result (T-010):
  VCS compiles it and URG reports it for this DUT (COND 37.41 percent, 3579/9566 in the first
  smoke report). `gen_regress.py` uses it by default (`--no-cond` drops it).
- `--diag-noconst`: adds `-diag noconst` (constant-analysis diagnostics for the exclusion work).
- `--cocotb`: Section 4 triple `+define+COCOTB_SIM +vpi -P <outdir>/gen_pli.tab -load $(cocotb-config
  --lib-name-path vpi vcs)`; also implied by `cocotb: true` on the build entry.
- Outdir: `<out root>/<build>-<utc stamp>` unless `--outdir`; an existing dir is refused unless
  `--force` (fresh outdir per knob change, Section 9). `<out root>/<build>.latest` names the newest.
- Products: `vcs_simv`, `vcs_simv.daidir/`, `compile.log`, `compile_cmd.sh` (exact command),
  `cm_hier.cfg`, `build.vdb` (compile-time coverage data), `env.sh` (staged copy of `ci/env.sh`),
  `build_manifest.yaml`.
- `build_manifest.yaml`: build, tb_top, dut_instance, build_config, command, flag_groups (one list per
  group), inputs (sha256 of every filelist, one combined sha256 over all listed sources, source
  count), staged_env_sh sha256, git (HEAD, branch, dirty flag), tools (vcs, urg, python, cocotb),
  compile_summary (error count and classes, warning classes with counts, compiler version), status
  `ok|failed`, wall_s. `status: ok` requires vcs rc 0, a simv, and zero `Error-[...]` lines.

## 2. gen_run.py (one test, one seed)

```
gen_run.py --build-dir DIR --test NAME --seed N --run-dir DIR [--cov-dir VDB | --no-coverage]
           [--lsf] [--waves] [--timeout-s N] [--plusarg +x=y ...] [--fcov-check]
```

- Composes the SIM_RECIPE Section 5 command: `<simv> +vcs+lic+wait +ntb_random_seed=<seed>
  +UVM_TESTNAME=<uvm_test> +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan
  <testlist plusargs> <--plusarg extras> -l <run dir>/sim.log` plus, on a coverage build,
  `-cm <metrics> -cm_dir <vdb> -cm_name test_<name>_<seed> -cm_log /dev/null -assert nopostproc`.
- **One seed.** The same integer goes to `+ntb_random_seed` and to the environment variable
  `RANDOM_SEED` (cocotb). Both are recorded at time zero: `run.log` line `GEN_RUN_SEED ...`, the
  job's `GEN_RUN_SEED` echo in `lsf.out`, and the `Command:` head line of `sim.log`. Seeds are
  integers in [1, 2^31-1].
- **Shared vdb.** Default `--cov-dir` is the build's compile-time `build.vdb`; every test+seed of a
  build is a distinct test record inside it (`-cm_name`). URG needs the compile-time design data,
  so a different `--cov-dir` must be merged together with `build.vdb`.
- `--lsf`: the run is `bsub -K -q regress -n 1 -R "span[hosts=1]" -J gen_dv_<test>_<seed> -cwd <run
  dir> -o lsf.out -e lsf.err -W <timeout+5 min> bash run_cmd.sh`, watched by a per-job watchdog
  (pend allowance `--pend-allowance-s`, default 3600 s; run deadline timeout_s + 120 s; `bkill` on
  expiry). Without `--lsf` the same script runs on this host.
- **Timeout.** `timeout -k 20 <timeout_s>` around the simv inside the job (exit code 124 = timed
  out); the testlist `timeout_s` is the budget, `--timeout-s` overrides it.
- **Verdict** (`gen_verdict.py`, self-tested with `--self-test`): TIMEOUT if the budget expired;
  FAIL on any collected mechanism in `sim.log` (UVM_FATAL/UVM_ERROR summary count > 0 or an
  `UVM_FATAL`/`UVM_ERROR` message line, `Fatal:`/`$fatal`/`GEN_*_FAIL`, `Error-[...]`/`Error:`, cocotb
  `CRITICAL` or a `** TESTS=... FAIL=n` summary with n > 0 or PASS=0, `Assertion ... failed`/`Offending`);
  FAIL when the end-of-test marker is missing (the test's `pass_marker`, or `$finish` when null);
  otherwise PASS. `expected_fail: true` turns FAIL into XFAIL and PASS into FAIL (unexpected pass).
  The process exit code is recorded, never decisive.
- `--fcov-check`: runs `ci/check_fcov_expectations.py --manifest <fcov_expectation_file> --vdb <vdb>
  --cm-name test_<name>_<seed>` right away (single writer); exit 2 (unhit) or 1 (protocol error)
  turns a PASS into FAIL. In a regression the check runs after every writer finished (Section 3).
- `--waves`: needs a `--waves` build; renders `gen_dump.tcl` into the run dir (FSDB with
  `$VERDI_HOME`, else VPD) and adds `-ucli -do dump.tcl`.
- Products per run dir: `run_cmd.sh` (exact reproduction: `bash run_cmd.sh`), `run.log`, `sim.log`,
  `exit_code`, `result.yaml`, and with `--lsf` `bsub_cmd.txt`, `lsf.out` (LSF job report: CPU time,
  run time, host), `lsf.err`.
- `result.yaml`: test, seed, verdict, reason, evidence (first failing line), exit_code, timed_out,
  wall_s, started/finished UTC, build, build_dir, build_config, run_dir, sim_log, run_log, run_cmd,
  vdb, cm_name, waves, uvm_counts, cocotb_summary, finish_seen, marker_seen, expected_fail, owner,
  fcov_expectation_file, fcov_check, lsf {job_id, host, queue, slots, bsub_rc, killed_reason,
  pend_s, wall_s, cpu_s, max_mem, lsf_run_s}.

## 3. gen_regress.py (tiers, fan-out, merge, manifest)

```
gen_regress.py --tier smoke|targeted|full [--group G] [--seeds N] [--seed-list a,b] [--base-seed S]
gen_regress.py --tests gen_a,gen_b [...]
gen_regress.py --repro <test> <seed> [--waves]
   [--outdir DIR | --tag T] [--force] [--no-coverage] [--no-cond] [--max-parallel N] [--local]
   [--build-lsf] [--waves] [--elfile F ...] [--purpose P] [--request NAME] [--requester ROLE]
```

- **Tiers.** A test's `tier` is its lowest tier; `--tier targeted` runs smoke plus targeted tests,
  `--tier full` runs everything. `--group G` restricts the targeted tier to tests whose
  `feature_groups` contain G (smoke tests stay in).
- **Seeds.** A count in the testlist (or `--seeds`) derives seeds deterministically from
  `--base-seed` (default: the start time) and the test name, so a regression is repeatable from its
  manifest (`scope.base_seed`); `--seed-list` pins explicit seeds for every selected test.
- **Repro.** `--repro <test> <seed>` reruns exactly that pair, no coverage, optional waves
  (a waves build is compiled).
- Steps: fresh outdir `<out root>/regress_<tag|stamp>/`; one compile per build under `build/<name>/`
  (coverage with cond unless `--no-coverage`/`--no-cond`); runs fan out through a thread pool
  (`--max-parallel`, default 8), each thread calling `gen_run.py --lsf` (or local with `--local`);
  the fcov-expectation check for every passing run with a manifest, after all writers finished;
  URG merge (`urg -full64 -format both -dbname cov/merged.vdb -report cov/report -log cov/merge.log
  -show ratios -dir <each build vdb> [-elfile ...]`); `manifest.yaml`; a one-line summary. Exit 0
  only when no run is FAIL, TIMEOUT or NOT_RUN.
- `--elfile`: URG exclusion files (the exclusion deliverable) applied at merge time.
- `manifest.yaml` (also the results manifest of a run request): kind, tag, request, requester,
  purpose, build_config, scope {tier, tests, group, repro, seeds_override, seed_list, base_seed,
  coverage, cond, waves, local, max_parallel}, planned_runs, builds {name: dir, manifest, status,
  wall_s, vdb, lsf}, runs [result.yaml content + result_yaml + run_dir], coverage {merged_vdb,
  report_dir, dashboard_txt, merge_log, urg_rc, urg_cmd, input_vdbs, totals, dut_scope,
  limited_design}, summary {planned, pass, fail, xfail, timeout, not_run, pass_rate_pct}, lsf_cost
  {jobs, cpu_s, wall_s, pend_s, slot_s, cpu_unknown_jobs}, lsf_jobs_left, git, tools, timing.
- **Coverage numbers.** `coverage.totals` is the grand total of `report/dashboard.txt`;
  `coverage.dut_scope[<tb_top>.<dut_instance>]` is the row of the DUT instance in
  `report/hierarchy.txt` and is the gate number (it differs from the grand total only for objects
  outside the DUT tree, today the three `uvm_pkg` assertions). A metric URG does not print is `n/a`.
  Ratios (covered/total) are kept next to every percentage.

## 4. gen_serve_requests.py (run-request queue)

```
gen_serve_requests.py --once | --watch [--interval S] [--duration S] | --dry-run
```

Request file: `dv/auto_dv/work/runtime/requests/<requester>-<seq>.yaml`, requester = role slug,
seq = integer. Fields:

| Field | Type | Meaning |
|---|---|---|
| requester | role slug | must equal the file-name prefix |
| purpose | 1..4 | sets the allowed scope (below) |
| tests | list of test names, a comma list, or one tier word `smoke`/`targeted`/`full` | what to run |
| seeds | count or explicit list | seeds per test |
| coverage | yes/no | coverage instrumentation and URG report |
| notes | text | why; copied into the manifest |
| component (optional) | string | purpose 2: the TB component that changed (matches `component:` of tests) |
| waves (optional) | yes/no | purposes 1 to 3: dump waves (debug only) |
| group (optional) | string | tier targeted: feature-group filter |

Purpose and the scope it allows (a larger scope is refused in writing, in the manifest):

| Purpose | Allowed scope | Refused when |
|---|---|---|
| 1 bring-up of one test | exactly one named test, at most 5 seeds | a tier word, several tests, more seeds |
| 2 TB component change | smoke tier + every test whose `component` matches + the mutation-evidence tests of that component (`feature_groups: [mutation]`) + explicitly named tests | `tests: full`; no component and no test |
| 3 failure reproduction | one test, one explicit seed, no coverage, waves optional | anything else |
| 4 Phase 1 gate or closure round | `tests: full` with `coverage: yes`, requester dv-lead or orchestrator | another tier, coverage no, another requester (route through the DV Lead) |

Life cycle: `requests/` -> `running/` -> `done/`; results in
`dv/auto_dv/work/runtime/results/<same-name>/manifest.yaml` with request echo, scope decision
(`accepted|refused`) and refusal reason, the regression command, and the regression manifest's
runs (test, seed, verdict, reason, sim_log, run_log, run_cmd, vdb, cm_name, waves, wall_s,
lsf_job_id), builds, coverage (report_dir, dashboard_txt, totals, dut_scope), summary, lsf_cost.
The requester is told the manifest path by message. `--once` (default) serves what is pending and
exits; `--watch` polls. Only the runtime role runs this script (LSF is exclusive to it).

## 5. gen_dashboard.py (results dashboard)

```
gen_dashboard.py [--out dv/auto_dv/docs/gen_dashboard.md] [--out-root DIR] [--results-dir DIR]
```

Reads every `regress_*/manifest.yaml` under the out root plus every results manifest and writes
`dv/auto_dv/docs/gen_dashboard.md`: closure rounds (purpose-4 regressions) with per-metric DUT-scope
coverage, the gain versus the previous round and the LSF cost; coverage per regression; pass/fail
and runtime per test (latest run per test+seed and per-test history); LSF cost per regression;
run requests served. ASCII only. Re-run after every regression; the Orchestrator commits it.

## 6. gen_cov_report.py (merge and read URG)

```
gen_cov_report.py merge --cov-dir DIR --vdb A.vdb [--vdb B.vdb] [--elfile F] [--dut-scope SCOPE]
gen_cov_report.py parse --report-dir DIR [--dut-scope SCOPE]
gen_cov_report.py unreachable --report-dir DIR --module <rtl module>
```

`merge` is the SIM_RECIPE Section 8 command (`-show ratios` added; the text report is what the
parser reads). `unreachable` counts URG "Unreachable" marks (constant analysis, `-cm_seqnoconst`)
in one module's section of `modinfo.txt`, per line rows, condition vectors and toggle rows: the
machine evidence rtl-arch's exclusion draft Part B.3 asks for.

## 7. gen_testlist.yaml (schema)

`schema_version: 1`. `builds.<name>`: `tb_top`, `dut_instance`, `filelists` (clone-root relative,
in order), optional `defines`, `cocotb`, `description`, `extra_vcs_args`. `tests[]`: `name` (gen_
prefix, unique), `description`, `tier`, `build`, `uvm_test` (null for a top without a UVM test
class), `plusargs` (list of `+name=value`), `seeds` (count or list), `fcov_expectation_file`
(`dv/auto_dv/fcov_expectations/<name>.fcov.yaml` or null), `timeout_s`, `owner` (role slug),
optional `pass_marker`, `feature_groups`, `cocotb_module`, `expected_fail`, `component`, `notes`.
`gen_flow_util.load_testlist` rejects unknown keys, unknown builds, non-gen_ names, bad tiers and
owners. The Test Writer adds test entries; TB Infra adds build entries; both through the runtime
owner (one owner per file).

## 8. Reproduction recipe

From any manifest: `bash <run_dir>/run_cmd.sh` reruns the exact simv command with the same seed on
the current host (sources the staged env.sh). Through the flow: `gen_regress.py --repro <test>
<seed>` (fresh build, same testlist entry) or a purpose-3 request.

## 9. Cleanup rule

Every regression manifest records `lsf_jobs_left` (this user's `gen_dv_*` jobs still in `bjobs`);
it must be empty. `gen_flow_util.lsf_jobs_left()` is the check; the runtime role runs `bjobs`
at the end of every task.
