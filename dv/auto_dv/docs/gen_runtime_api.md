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
- **Setup step (once per site).** Copy `dv/auto_dv/flow/gen_site.yaml.example` to
  `dv/auto_dv/work/runtime/gen_site.yaml` and set `out_root` (and `mirror_root`, Section 10) to
  shared, writable paths; `python3 gen_flow_const.py` prints the resolved paths.
- **Compile on the submit host, simulate on LSF.** `vcs` needs the sources, so the compile runs
  where the clone is; the simulation job is a self-contained bash script that sources a copy of
  `ci/env.sh` staged into the build outdir and runs the simv from the shared out-tree. `--build-lsf`
  and `--lsf` on the build exist for a clone on shared storage.
- **cocotb runs on LSF go through the shared mirror** (Section 7b, `gen_mirror.py`): the compute
  host loads the VPI library from the mirror venv and imports the Python test modules from the
  mirror copy of the clone. Re-sync the mirror after changing anything a cocotb run imports.
- **LSF paths are absolute** and the job gets `-cwd <run dir>` (the site default CWD is `/tmp`).
- **Temporary locations (intervention log F-001).** The flow never reads or lists shared temporary
  locations (`/tmp`, `/var/tmp`) beyond paths it created and named itself; every temporary directory
  the flow or the fcov checker creates lives under the run's out directory (`TMPDIR` is pinned to
  the run dir for the checker). Any accidental listing of a path outside this clone, the shared out
  root or the mirror is a reportable event: record it in STATUS.md and report it to the Orchestrator
  for the intervention log, without the content.
- **Constants home.** Paths, plusarg names, log markers, LSF defaults and schema keys live in
  `gen_flow_const.py` only. `python3 gen_flow_const.py --check` proves the plusarg names shared with
  the SV constants home `dv/auto_dv/tb/gen_tb_pkg.sv` are identical.

## 1. gen_build.py (compile one TB top)

```
gen_build.py --build <name> [--coverage] [--cond] [--no-diag-noconst] [--cocotb] [--waves]
             [--define NAME ...] [--outdir DIR] [--force] [--lsf] [--timeout-s N]
```

- `--build`: key under `builds:` of `gen_testlist.yaml` (tb_top, dut_instance, filelists, defines).
- Flag set: SIM_RECIPE Section 2 exactly (`-full64 -sverilog -f ... -top ... -ntb_opts uvm-1.2
  +define+UVM +define+UVM_REGEX_NO_DPI`, the `util/ibex_config.py opentitan vcs_opts` output,
  `-timescale=1ns/10ps -licqueue -LDFLAGS -CFLAGS -xlrm uniq_prior_final -lca -kdb`,
  `-debug_access+pp`, or `-debug_access+all` with `--waves`; `-ucli` goes on the simv command line only,
  VCS X-2025.06 rejects it at compile time).
- `--coverage`: Section 3 compile flags `-cm line+tgl+assert+fsm+branch -cm_tgl portsonly -cm_tgl
  structarr -cm_report noinitial -cm_seqnoconst -cm_dir <outdir>/build.vdb -cm_hier <outdir>/cm_hier.cfg`.
  The hier file is rendered from the checked-in template `gen_cm_hier.cfg` as
  `+tree <tb_top>.<dut_instance>`, so only the gen_dut_top instance is instrumented.
- `--cond`: adds condition coverage (`-cm line+cond+tgl+assert+fsm+branch`). Trial result (T-010):
  VCS compiles it and URG reports it for this DUT (COND 37.41 percent, 3579/9566 in the first
  smoke report). `gen_regress.py` uses it by default (`--no-cond` drops it).
- `-diag noconst` is added to every coverage build (`--no-diag-noconst` drops it): VCS writes
  `constfile.txt`, the list of every signal it treats as constant and why, into the outdir (vcs runs
  there; no sweep of the clone root is needed).
- `--vcs-arg ARG` (repeatable): extra vcs argument for trials.
- `--cocotb`: Section 4 triple `+define+COCOTB_SIM +vpi -P <outdir>/gen_pli.tab -load $(cocotb-config
  --lib-name-path vpi vcs)`; also implied by `cocotb: true` on the build entry.
- Outdir: `<out root>/<build>-<utc stamp>` unless `--outdir`; an existing dir is refused unless
  `--force` (fresh outdir per knob change, Section 9). `<out root>/<build>.latest` names the newest.
- vcs runs with the outdir as its cwd: the filelists are copied there with absolute paths
  (`<outdir>/gen_rtl.f` and friends), so `compile_cmd.sh` is self-contained and every vcs side file
  (`constfile.txt`, `ucli.key`, the FSM schematic xml) lands in the outdir even under concurrent
  compiles. `compile_summary` classifies `Error-[...]`/`Warning-[...]` codes including hyphenated ones.
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
- **Verdict** (`gen_verdict.py`, `--self-test` pinned to real log excerpts, evidence
  `dv/auto_dv/evidence/gen_t038_flow_red_runs.md`): TIMEOUT if the budget expired (also when the
  simulator died before sim.log existed);
  FAIL on any collected mechanism in `sim.log` (UVM_FATAL/UVM_ERROR summary count > 0 or an
  `UVM_FATAL`/`UVM_ERROR` message line, `Fatal:`/`$fatal`/`GEN_*_FAIL`, `Error-[...]`/`Error:`, cocotb
  `CRITICAL` or a `** TESTS=... FAIL=n` summary with n > 0 or PASS=0, `Assertion ... failed`/`Offending`);
  FAIL when the end-of-test marker is missing (the test's `pass_marker`, matched as the last whole
  token of a line, or `$finish` when null); FAIL when the time-zero banner line
  `GEN_CONFIG_BANNER build_config=opentitan` is missing from sim.log (the rule cannot be switched
  off; the banner block is copied into result.yaml); FAIL when the marker is present but neither `$finish` was seen nor the exit code is
  0, or the exit code is neither 0 nor 124 ("unexplained exit code": one more collected mechanism,
  never the only one); FAIL on a crash signature (`Segmentation fault|Killed|core dumped|Aborted|Bus
  error|Illegal instruction`) in lsf.err, run.log or sim_stdout.log; otherwise PASS. `expected_fail: true` turns FAIL into XFAIL and PASS into FAIL (unexpected pass).
  The process exit code is recorded, never decisive.
- `--fcov-check`: runs the fcov-expectation check (Section 7c) right away (single writer); a
  declared-but-unhit bin or an unverifiable query turns a PASS into FAIL with the reason `fcov
  expectation unmet` or `fcov expectation unverifiable`. In a regression the check runs after every
  writer finished (Section 3).
- `--measured auto|yes|no`: whether the run's coverage enters a measured merge (auto = the testlist
  `measured` flag; a mutation build forces no). A measured coverage run whose plusargs enable a knob
  listed under the testlist header `debug_only_plusargs` is refused in writing (result.yaml NOT_RUN,
  no job): tb-arch ruling P6, the CSR-flop debug compare never enters a measurement.
- `--pass-marker`: overrides the testlist marker (red-run evidence only; refused on a measured run).
  An operator `--plusarg` replaces a same-name testlist plusarg (VCS honours the first occurrence).
- `--waves`: needs a `--waves` build; renders `gen_dump.tcl` into the run dir (FSDB with
  `$VERDI_HOME`, else VPD) and adds `-ucli -do dump.tcl`. Templates are rendered by
  `gen_flow_util.render_fields` (token replacement, Tcl braces untouched); `python3 gen_flow_util.py
  --self-test` renders both templates and checks them.
- Products per run dir: `run_cmd.sh` (exact reproduction: `bash run_cmd.sh`), `run.log`, `sim.log`
  (VCS `-l`), `sim_stdout.log` (simv stdout and stderr: cocotb's Python logging and its result
  table bypass `-l`, so the verdict scans both files), `exit_code`, `result.yaml`, and with `--lsf`
  `bsub_cmd.txt`, `lsf.out` (LSF job report: CPU time, run time, host), `lsf.err`.
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
  `--tier full` runs everything measured. `--group G` restricts the targeted tier to tests whose
  `feature_groups` contain G (smoke tests stay in). Tier `check` (gen_smoke, the cocotb probe) sits
  outside the measured tiers: build/elaboration checks, `measured: false` by construction, run only
  with `--tier check` or by name (Critic R-01).
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
- **Mutation builds (Critic A-24).** `--rtl-root DIR --mutation-id ID` compiles from a mutated copy:
  any listed source that exists under DIR (clone-relative layout, e.g. `DIR/rtl/ibex_alu.sv`) replaces
  the clone's file; every regular file under DIR must match a filelist entry, otherwise the build dies
  naming the leftovers (a typo never silently compiles the unmutated clone); the build manifest
  records `rtl_root_override`, `mutation_id` and every substitution with both sha256 digests; every run is `measured: false` (unmeasured vdb tree);
  `--purpose 4` is refused. DV never edits `rtl/` in place.
- **Summary accounting (Critic P-07).** `summary.runs_without_fcov_manifest` and
  `tests_without_fcov_manifest` list every run without a declared-bins manifest; the testlist header
  `fcov_manifest_required_tiers` turns a null manifest into a FAIL on the named tiers once the first
  covergroup exists.
- **Out root (Critic P-10).** A non-local regression refuses an out root on a local filesystem
  (`--allow-local-out-root` for single-host debugging); every manifest records `out_root`,
  `out_root_fs` and the site pointer path.
- `--elfile`: URG exclusion files (the exclusion deliverable) applied at the measured merge with
  `-excl_strict` (Section 7a). `--dump-exclusions` (implied by `--purpose 4`) writes the
  full-exclusions dump. `--build-vcs-arg` passes an extra vcs argument to every build (trials such
  as `-cm_glitch 0`).
- `manifest.yaml` (also the results manifest of a run request): kind, tag, request, requester,
  purpose, build_config, scope {tier, tests, group, repro, seeds_override, seed_list, base_seed,
  coverage, cond, waves, local, max_parallel}, planned_runs, builds {name: dir, manifest, status,
  wall_s, vdb, lsf}, runs [result.yaml content + result_yaml + run_dir], coverage {merged_vdb,
  report_dir, dashboard_txt, merge_log, urg_rc, urg_cmd, input_vdbs, totals, dut_scope,
  limited_design}, summary {planned, pass, fail, xfail, timeout, not_run, pass_rate_pct}, lsf_cost
  {jobs, cpu_s, wall_s, pend_s, slot_s, cpu_unknown_jobs}, lsf_jobs_left, git, tools, timing,
  testlist {path, sha256} (also in every result.yaml and round index entry, so a temporary testlist
  used for a self-test is identifiable even when the file itself is not retained).
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
| build_vcs_args (optional) | list of strings | purpose 2 only: extra vcs arguments for an instrumentation trial (for example `["-cm_glitch 0"]`); refused under any other purpose because a measurement never changes the flag set |
| dump_exclusions (optional) | yes/no | add `urg -dump full_exclusions` to the merge (purpose 4 does it anyway) |

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
exits; `--watch` polls. `--extra-arg=<gen_regress argument>` (repeatable, `=` syntax because the
values start with dashes) lets the runtime operator add knobs a request asked for in its notes;
they are recorded in the manifest as `operator_extra_args`. Only the runtime role runs this
script (LSF is exclusive to it).

## 5. gen_dashboard.py (results dashboard)

```
gen_dashboard.py [--out dv/auto_dv/docs/gen_dashboard.md] [--out-root DIR] [--results-dir DIR]
```

Reads every `regress_*/manifest.yaml` under the out root plus every results manifest and writes
`dv/auto_dv/docs/gen_dashboard.md`: closure rounds (purpose-4 regressions) with per-metric DUT-scope
coverage, the gain versus the previous round and the LSF cost; coverage per regression; pass/fail
and runtime per test (latest run per test+seed and per-test history); LSF cost per regression;
run requests served. ASCII only. Re-run after every regression; the Orchestrator commits it.
Functional coverage (Group) comes from the URG grand total: the gen_ covergroups are TB-side
instances that never sit under the DUT instance row, and the gen_ namespace is the whole
functional set by the contract; the six code metrics come from the DUT row.

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

`schema_version: 1`. Header policies: `fcov_manifest_required_tiers` (list), `debug_only_plusargs`
(list of knob names). `builds.<name>`: `tb_top`, `dut_instance`, `filelists` (clone-root relative,
in order), optional `defines`, `cocotb`, `description`, `extra_vcs_args`, `cov_trees` (coverage
roots below tb_top, default `[dut_instance]`; the single source of the `-cm_hier` scope, Critic
P-04; the DV Lead rules wrapper versus `[u_dut.u_ibex_core, u_dut.u_register_file]`). `tests[]`: `name` (gen_
prefix, unique), `description`, `tier`, `build`, `uvm_test` (null for a top without a UVM test
class; otherwise a class identifier, anything else is rejected), `plusargs` (list of `+name=value`), `seeds` (count or list), `fcov_expectation_file`
(`dv/auto_dv/fcov_expectations/<name>.fcov.yaml` or null), `timeout_s`, `owner` (role slug),
optional `pass_marker`, `feature_groups`, `cocotb_module`, `expected_fail`, `component`, `notes`.
`gen_flow_util.load_testlist` rejects unknown keys, unknown builds, non-gen_ names, bad tiers and
owners, a tier-check test that is not `measured: false`, and any plusarg whose name is neither a
`PLUSARG_*` constant of `dv/auto_dv/tb/gen_tb_pkg.sv` nor a simulator/UVM plusarg (Critic P-06).
`gen_build.py`, `gen_run.py` and `gen_regress.py` each call `gen_flow_util.require_sv_constants()` first thing in `main()` (the SV/Python constants check); `gen_serve_requests.py` and `gen_dashboard.py` do not compile or run anything and rely on those three. The Test Writer adds test entries; TB Infra adds build entries; both through the runtime
owner (one owner per file).

## 7a. Exclusion policy in the flow (Critic ruling R-5, dv/auto_dv/work/critic/gen_critic_exclusions_draft_v1.md)

| Rule | Where the flow enforces it |
|---|---|
| R-5.1 exclusion files load with `-elfile` and `-excl_strict` | `gen_cov_report.merge` adds `-excl_strict` whenever an `--elfile` is given; a `Warning-[UCAPI-ILOAD] Illegal exclusion attempt` (or any `Error-[UCAPI...]`) in merge.log sets `coverage.status: exclusion_violation` and `gen_regress.py` exits 3 (the regression FAILS; the report is kept for triage). Verified on this host: excluding a covered line block produces UCAPI-ILOAD and leaves the score unchanged; excluding an uncovered block is accepted and removes it from the denominator. |
| R-5.2 never `-excl_propagation` | the flow never adds it; `--urg-arg -excl_propagation` (and `-excl_bypass_checks`) is refused. |
| R-5.3 commit the auto-Unreachable dump of the measured merge | `gen_regress.py --purpose 4` (or `--dump-exclusions`) adds `urg -dump full_exclusions`; the `fullexclude.<metric>` and `fullexclude_module.<metric>` files land in `<outdir>/cov/full_exclusions/` and are listed in `coverage.full_exclusions_dump`. Every coverage build also writes the constant-analysis diagnostics (`-diag noconst`, `constfile.txt` in the build outdir, `coverage.constfiles`), which is VCS's record of what it auto-excluded and why. The exclusion author copies both beside the annotated `.el` file as evidence. |
| R-5.4 annotations that depend on `+define+RVFI` say so | `coverage.build_defines` records the defines of every build in the merge, so a reviewer can check the annotation against the build. |
| R-5.5 only legal-stimulus tiers enter a measured merge | test entries carry `measured: true|false` (default true). Non-measured tests (mutation-evidence, forced-error, bring-up) run into a separate tree `<outdir>/cov_unmeasured/<build>.vdb` (a copy of the compile-time vdb, so the design data is present) and get their own informational report under `cov_unmeasured/`; the measured merge lists only `build/<name>/build.vdb`. Purpose 1 to 3 requests always get their own outdir and vdb, so they never touch a measured tree. |
| R-5.6 instance names follow T-005 | the coverage scope is `<tb_top>.<dut_instance>` from the build entry; inside it the instances are `u_ibex_core` and `u_register_file` (gen_dut_top). Exclusion files address `INSTANCE: <tb_top>.u_dut.u_ibex_core...` or `MODULE: <module>`. |

## 7b. gen_mirror.py (shared-storage mirror for cocotb on LSF; intervention log Q-012 default)

```
gen_mirror.py --sync [--venv] [--spike]     # rsync the clone subset; build the venv ON shared storage; copy tools/spike
gen_mirror.py --check                       # fresh (exit 0) or stale (exit 1): clone hash == manifest == mirror tree
gen_mirror.py --status
```

- Root: `mirror_root:` of `dv/auto_dv/work/runtime/gen_site.yaml` (env override `GEN_DV_MIRROR_ROOT`).
- Content: `rtl/`, `vendor/lowrisc_ip/`, `vendor/google_riscv-dv/`, `util/`, `ci/`, `dv/auto_dv/`
  (without `work/`), `ibex_configs.yaml`, `python-requirements.txt`, `*.core`; excluded `.git`,
  `__pycache__`, out-trees, vdb and fsdb files; `--spike` adds the `tools/spike` install tree.
- Venv: `--venv` runs the MIRROR's `ci/setup-venv.sh` (PYTHONPATH cleared, lock-file check
  included), so `<mirror>/.venv` carries shared absolute paths; the manifest records the venv's
  `cocotb-config --lib-name-path vpi vcs` result, `--libpython`, and the Python version.
- Manifest `<mirror>/gen_mirror_manifest.yaml`: clone path, git HEAD and dirty flag at sync time,
  sync UTC, `tree_sha256` over (relative path, content) of every mirrored source file, file count,
  venv facts, spike presence. Logs under `<mirror>_logs/`.
- The freshness hash covers the files a compute host consumes at run time (`dv/auto_dv/**/*.py`,
  `ci/env.sh`, `ci/setup-venv.sh`, the two requirements files); RTL, TB sources and documents are
  mirrored but not hashed (they are compiled on the submit host and churn constantly).
  `gen_regress.py` re-syncs the mirror before a cocotb build (`--no-sync-mirror` to skip), so the
  build records the revision its runs import.
- Staleness fails loud: `gen_build.py` refuses a cocotb build unless the mirror is `fresh`
  (`--allow-stale-mirror` for experiments only) and records the mirror's root, tree hash and git
  HEAD in `build_manifest.yaml`; `gen_run.py` refuses a cocotb run whose mirror manifest hash
  differs from the build's record. Re-sync after every change to files a cocotb run imports
  (`gen_mirror.py --sync`, seconds; the venv and spike are kept).
- How a cocotb run uses it: the simv is compiled on the submit host with `-load <mirror
  venv>/.../libcocotbvpi_vcs.so`; the LSF job script sources `<mirror>/ci/env.sh` (which activates
  the mirror venv and exports `LIBPYTHON_LOC`) and exports `MODULE=<cocotb_module>`,
  `PYTHONPATH=<mirror>`, `TOPLEVEL=<tb_top>`, `TOPLEVEL_LANG=verilog`, `RANDOM_SEED=<seed>`
  (SIM_RECIPE Section 4). Python test modules therefore import from the mirror copy of
  `dv/auto_dv/`, never from the clone. `--local-cocotb` builds against the clone venv for
  `gen_regress.py --local` runs on the submit host.
- Probe: test `gen_cocotb_probe` (build `gen_smoke_cocotb`, module
  `dv.auto_dv.flow.gen_cocotb_probe`, `measured: false`) proves the path end to end; evidence
  `dv/auto_dv/evidence/gen_t027_cocotb_lsf.md`.

## 7c. fcov-expectation wiring (trust triad rule 3; gen_fcov.py, ci/check_fcov_expectations.py)

Manifest: `dv/auto_dv/fcov_expectations/<test>.fcov.yaml` (the standing home of
`dv/auto_dv/contract/README.md`), named in the test's `fcov_expectation_file`:

```
test: gen_<name>                        # equals the file stem and the testlist entry
owner: <role slug>
bins:                                   # gen_<feature>_cg.<coverpoint>.<bin>; gen_ namespace only
  - gen_regime_cg.cp_regime.bin_fast
anti_vacuity:                           # one note per declared bin, carried into result.yaml, never interpreted
  gen_regime_cg.cp_regime.bin_fast: "sampled on the regime-change event only; fast is hit only when the schedule selects it"
```

`gen_fcov.validate_manifest` enforces: stem == `test` == testlist entry, owner is a role slug,
bins non-empty, unique, in the `gen_` namespace with three dot-separated parts, one non-empty
anti-vacuity note per bin, no note for an undeclared bin. `python3 gen_fcov.py --validate` checks
every manifest under the home. The checker itself reads only `bins:` (its parser stops at the next
top-level key), keyed `<cg>.<cp>.<bin>` from URG's grpinfo.txt with counts summed across instances
of the same covergroup (TB Infra's C7 naming: `gen_<feature>_cg`).

Flow step, per test and pre-merge: `gen_fcov.check_test` runs
`ci/check_fcov_expectations.py --manifest <file> --vdb <the run's vdb> --cm-name test_<name>_<seed>`
(the checker selects the slice with `urg -tests <vdb minus .vdb>/<cm_name>` and refuses anything but
exactly one test in the report). In a regression `gen_regress.post_fcov_checks` runs it after every
writer to the shared vdb has finished; a standalone `gen_run.py --fcov-check` runs it right away
(single writer). Result: `result.yaml: fcov_check` with status (PASS, UNHIT, PROTOCOL_ERROR,
NO_MANIFEST), per-bin HIT/UNHIT/MISSING-FROM-REPORT with counts, `unmet_bins`, the notes, the
checker log. A PASS/XFAIL run becomes FAIL with the distinct reason `fcov expectation unmet: ...`
(declared but unhit) or `fcov expectation unverifiable: ...` (protocol error: unverifiable is not a
pass). The regression manifest carries `fcov.totals` (checked, pass, unmet, unverifiable) and
`fcov.per_test`; the dashboard shows the per-test status and the per-regression triple.

Manifest-required policy: a run without a manifest is counted (`summary.runs_without_fcov_manifest`);
it FAILs on the tiers named in the testlist header `fcov_manifest_required_tiers`, and on every
measured tier (smoke, targeted, full) as soon as URG reports a GROUP total in any merge of the
regression (`fcov.covergroups_exist`), so the policy becomes live with the first covergroup. Tier
check stays exempt.

Proof status: `python3 gen_fcov.py --self-test` drives the REAL checker in `--report-dir` mode on a
fabricated grpinfo.txt (all-hit PASS, one-unhit UNHIT, absent bin unmet, missing report
unverifiable) plus the schema rules; the vdb slice selection (`urg -tests`) is exercised on the
real smoke vdb in `dv/auto_dv/evidence/gen_t045_fcov_wiring.md`; the bin-row parse on a real
covergroup remains to be proven at the first covergroup.

## 7d. gen_round.py (Phase 1 gate and closure-round measurement; DV_prompt Sections 4 and 5)

```
gen_round.py --round <n> [--label "Phase 1 gate"] [--elfile F ...] [--seeds N] [--base-seed S] [--tag T]
gen_round.py --dry-run                      # check tier, UNMEASURED; evidence gen_round_0_dryrun; never a round
gen_round.py --collect <regress outdir> --round <n>    # evidence + index from a regression that already ran
```

- One round = `gen_regress.py --tier full --purpose 4 --dump-exclusions [--elfile ...]` (coverage with
  cond, every `-elfile` loaded with `-excl_strict`, a strict violation fails the regression), then the
  evidence directory `dv/auto_dv/evidence/gen_round_<n>/` (never overwritten): `dashboard.txt`,
  `hierarchy.txt`, `tests.txt`, `hierarchy_dut_rows.txt` (the DUT-scope rows), `groups.txt` and
  `grpinfo.txt` when covergroups exist (else `groups_summary.txt` stating n/a),
  `full_exclusions/fullexclude.<metric>.gz` (the URG dump of this merge, gzip-compressed; a dry
  run copies no dump, its out-tree keeps it), `merge.log` and
  `merge_log_warnings.txt` (counts per Warning/Error/Note class), `build_manifest_<build>.yaml`,
  `testlist_snapshot.yaml` (with its sha256 in the index), `regress_manifest.yaml`, `elfiles/`, and
  `gen_round_summary.md` (the human-readable page: metrics table, gate status, deltas, gain verdict,
  streak).
- Round index `dv/auto_dv/evidence/gen_rounds.yaml`: G, N, gate percent, then one entry per round
  (metrics, gate per metric, per-metric deltas against the previous round, `max_gain`, `shows_gain`
  when `max_gain >= G`, `no_gain_streak`, `stopping_rule_fired` when the streak reaches N, exclusion
  files and strict violations, merge warning counts, git HEAD, testlist sha256). `gen_dashboard.py`
  renders Section 1 from this index; dry runs sit under `dry_runs` and never count.
- The n/a rule: a metric URG does not report (no column, or `--`) is `n/a` in the row, is not gated,
  and is skipped in the gain computation; it is never written as 0 or 100.
- Numbers: code metrics from the DUT-scope row of hierarchy.txt (`cov_trees` of the build entry);
  functional coverage (Group) from the grand total (covergroups are TB-side gen_ instances).
- The DV Lead requests a round through the queue (purpose 4, `tests: full`, `coverage: yes`); the
  runtime role runs `gen_round.py --round <n>` and the Orchestrator commits the evidence directory.
- `--evidence-root DIR` redirects the evidence directory and index (self-tests only; the committed
  homes are the defaults).
- Instrumentation changes such as `-cm_glitch 0` (LOG-008) are adopted, once ruled, as
  `builds.<name>.extra_vcs_args` in gen_testlist.yaml (the single source of the build flag set),
  and round 0 is re-measured under the new set so later gains compare like with like.

## 8. Reproduction recipe

From any manifest: `bash <run_dir>/run_cmd.sh` reruns the exact simv command with the same seed on
the current host (sources the staged env.sh). Through the flow: `gen_regress.py --repro <test>
<seed>` (fresh build, same testlist entry) or a purpose-3 request.

## 9. Cleanup rule

Every regression manifest records `lsf_jobs_left` (this regression's `gen_dv_<tag>_*` jobs still
active in `bjobs`: PEND, RUN or suspended; DONE and EXIT rows do not count); it must be empty. `gen_flow_util.lsf_jobs_left()` is the check; the runtime role runs `bjobs`
at the end of every task.
