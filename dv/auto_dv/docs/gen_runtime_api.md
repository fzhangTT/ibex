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
  for the intervention log, without the content. Flow self-tests keep their scratch under
  `dv/auto_dv/work/runtime/selftest_tmp/`.
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
- A build without `--coverage` drops the `-cm_*` entries of the build entry's `extra_vcs_args`
  (for example `-cm_glitch 0`), which mean nothing without `-cm` and only draw
  `Warning-[VCM-INSOPTMIS]`; `build_manifest.dropped_cm_args_no_coverage` records them.
- `--cond`: adds condition coverage (`-cm line+cond+tgl+assert+fsm+branch`). Trial result (T-010):
  VCS compiles it and URG reports it for this DUT (COND 37.41 percent, 3579/9566 in the first
  smoke report). `gen_regress.py` uses it by default (`--no-cond` drops it).
- `-diag noconst` is added to every coverage build (`--no-diag-noconst` drops it): VCS writes
  `constfile.txt`, the list of every signal it treats as constant and why, into the outdir (vcs runs
  there; no sweep of the clone root is needed).
- `--vcs-arg ARG` (repeatable): extra vcs argument for trials.
- `--cocotb`: Section 4 triple `+define+COCOTB_SIM +vpi -P <outdir>/gen_pli.tab -load $(cocotb-config
  --lib-name-path vpi vcs)`; also implied by `cocotb: true` on the build entry.
- **Effective `+define` set of a build** (read it from `<outdir>/compile_cmd.sh` or
  `build_manifest.flag_groups.defines`): `UVM`, `UVM_REGEX_NO_DPI` (SIM_RECIPE Section 2), the
  build entry's `defines` (today `RVFI`), the configuration macros from `util/ibex_config.py
  opentitan vcs_opts` (`BaseIsa`, `RV32M`, `RV32B`, `RV32ZC`, `RegFile`), plus `COCOTB_SIM` on cocotb
  builds. Nothing else: in particular `SIMULATION` is NOT defined (asked by the DV Lead for
  F-DIT-025). Effect in `vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv:250-278`: without `SIMULATION`
  the LFSR starts from the fixed `DefaultSeed` parameter (`DefaultSeedLocal = DefaultSeed`, line
  276); with `SIMULATION` (and not Verilator) an initial block randomizes `DefaultSeedLocal` 70
  percent of the time through `std::randomize` (seeded by `+ntb_random_seed`, so still reproducible
  from the run seed) unless `+prim_lfsr_use_default_seed=1`, and prints `%m: DefaultSeed = ...`.
  `SIMULATION` also gates `prim_double_lfsr.sv:87`, `prim_cdc_rand_delay.sv:27`,
  `prim_flop_macros.sv:45` and `prim_sparse_fsm_flop.sv:14`. Adding it is a build-flag change
  (`defines` of the build entry) that the DV Lead decides; the dummy-instruction LFSR
  (`ibex_dummy_instr`, prim_lfsr) therefore starts from `RndCnstLfsrSeed` in every run today.
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
  never the only one); FAIL on the shell's process-termination report in lsf.err or run.log (the job
  script's stderr: `<pid> Segmentation fault|Bus error|Aborted|Illegal instruction|Killed|Terminated`
  followed by the job's command text, which starts with the script's `timeout` word (bash quotes
  the whole simple command), `(core dumped)`, `timeout: sending signal`; TB or ISS log text such as
  "Illegal instruction (hart 0)" never matches; the two real-shaped reports are pinned in
  `gen_verdict.py --self-test`); otherwise PASS. `expected_fail: true` turns FAIL into XFAIL and PASS into FAIL (unexpected pass).
  `red_fixture: true` (a TDD fixture that fails by design, never an RTL-bug candidate) with its
  `red_expect` regex: a FAIL whose collected evidence line matches `red_expect` becomes RED-OK ("red
  fixture failed as designed (red_expect matched)"; the regex is tried against the FIRST collected
  evidence line in full, so it must name the earliest line of the designed failure; result.yaml shows
  the line cut to 300 characters for display only; a FAIL without a collected line, such as an
  unexplained exit code, a crash signature or a missing marker or banner, is never RED-OK, and the
  loader refuses a red_expect that matches the empty string), any other FAIL stays FAIL ("red fixture failed for
  an undeclared reason": a broken fixture or environment is not the designed failure), PASS becomes
  FAIL ("red fixture passed unexpectedly": the checker it proves is dead); a TIMEOUT stays TIMEOUT.
  RED-OK is never a regression failure and never coverage: the loader requires `measured: false` and a
  valid `red_expect` on such an entry and refuses `expected_fail` beside it. Failure reasons locate the
  evidence line as `<mechanism> at <file>:<line>` in the file that holds it (sim.log or the stdout
  capture), never as an index into the concatenated text; the mechanism `gen_fail_marker` names a
  `GEN_*_FAIL` line (a cocotb assertion message included), `sv_fatal` a `Fatal:` / `$fatal` line.
  The process exit code is recorded, never decisive.
  The same decision is available from the command line for scripts: `gen_verdict.py --sim-log <sim.log>
  --pass-marker <marker> --exit-code <simv rc> [--extra-log sim_stdout.log] [--stderr-log lsf.err]
  [--timed-out] [--expected-fail] [--red-fixture --red-expect <regex>] [--build-config opentitan]`;
  without `--exit-code` a clean log is FAIL (unexplained exit code None), exactly as inside the flow;
  the CLI and `gen_run.py` exit 0 for PASS, XFAIL and RED-OK.
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
  limited_design}, summary {planned, pass, fail, xfail, timeout, not_run, red_ok, pass_rate_pct (red fixtures excluded)}, lsf_cost
  {jobs, cpu_s, wall_s, pend_s, slot_s, cpu_unknown_jobs}, lsf_jobs_left, git, tools, timing,
  testlist {path, sha256} (also in every result.yaml and round index entry, so a temporary testlist
  used for a self-test is identifiable even when the file itself is not retained).
- **Coverage numbers (DV Lead ruling, gen_tb_architecture.md Section 5).** `coverage.totals` is the
  grand total of `report/dashboard.txt`; `coverage.dut_scope[<scope>]` holds the `hierarchy.txt`
  row of every gated scope (`cov_trees` of the build: `u_dut.u_ibex_core` and
  `u_dut.u_register_file`); `coverage.gate_row` is the gate number: the gated rows combined per
  metric by summing covered and total objects (from URG's `-show ratios` a/b), percent = 100 x
  covered / total, a metric no gated row reports stays `n/a` (`combine_rows` in gen_cov_report.py;
  the rule text travels in `gate_row.rule`). Precondition of the rule: the gated trees are disjoint
  subtrees (URG hierarchy rows are cumulative over their children, so nested trees would double
  count); `load_testlist` refuses a build whose `cov_trees` nest (`gen_flow_util.py --self-test`
  proves it). `coverage.rulings.scope` names the trees from the build entries, never from a constant. `coverage.info_scope[<scope>]` holds the rows of the
  `info_trees` (the wrapper `u_dut`): instrumented and reported, never gated. Functional coverage
  (Group) comes from the grand total. Ratios (covered/total) are kept next to every percentage.
  `coverage.glitch_filter[<build>]` records whether `-cm_glitch 0` was in the build's flag set;
  `coverage.rulings` carries both ruling references.

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
| elcheck (optional) | mapping `{vdb, elfile[, build]}` | purpose 2 only, with `tests: []` and `seeds: []`: report-only strict load of an exclusion file against an existing vdb (no simulation); scopes come from the build manifest of the regression the vdb belongs to (`build` names it when that regression has several) |

Purpose and the scope it allows (a larger scope is refused in writing, in the manifest):

| Purpose | Allowed scope | Refused when |
|---|---|---|
| 1 bring-up of one test | exactly one named test, at most 5 seeds | a tier word, several tests, more seeds |
| 2 TB component change | smoke tier + every test whose `component` matches + the mutation-evidence tests of that component (`feature_groups: [mutation]`) + explicitly named tests | `tests: full`; no component and no test |
| 2 with `elcheck` | two URG merges of the named vdb through the `gen_cov_report.py merge` CLI in bounded subprocesses, one with the exclusion file (`-excl_strict`, `-dump full_exclusions`) and one without, same gated and informational scopes; manifest `elcheck` carries both results, `merge_warnings`, `exclusion_violations`, `excluded_counts_gate_row` (denominators the file removed per metric) and a verdict `ok`/`failed`; a check that cannot run (no regression manifest above the vdb, a merge that dies or times out) is recorded as `verdict: failed` with `error`, the request still moves to done/ | tests or seeds non-empty; `build_vcs_args` given; no component; a purpose other than 2 |
| 3 failure reproduction | one test, one explicit seed, no coverage, waves optional | anything else |
| 4 Phase 1 gate or closure round | `tests: full` with `coverage: yes`, requester dv-lead or orchestrator | another tier, coverage no, another requester (route through the DV Lead) |

Life cycle: `requests/` -> `running/` -> `done/`; results in
`dv/auto_dv/work/runtime/results/<same-name>/manifest.yaml` with request echo, scope decision
(`accepted|refused`) and refusal reason, the regression command, and the regression manifest's
runs (test, seed, verdict, reason, sim_log, run_log, run_cmd, vdb, cm_name, waves, wall_s,
lsf_job_id), builds, coverage (report_dir, dashboard_txt, totals, dut_scope), summary, lsf_cost.
The requester is told the manifest path by message. `--once` (default) serves what is pending and
exits; `--watch` polls. Every manifest records `out_root` (the out root in force for that serve). A
file that does not parse as YAML is refused in writing like any other invalid request (the parse
error is the refusal reason; the raw text is the echo); a refused name is consumed, re-file under the
next sequence number. `--only <name>` (repeatable) serves only the named pending requests.

Concurrency (Orchestrator ruling, 2026-09-03): purpose 1 stays one test per request, but independent
purpose-1 requests pending in the same pass are served concurrently (`--max-concurrent`, default 4;
each regression keeps its own 8-wide run pool, outdir, manifest and LSF accounting), so a batch of N
single-test requests turns around in about one request's time. Before such a batch the server syncs
the mirror once (`gen_mirror.py --sync --spike`, recorded in every batch manifest as
`server_mirror_sync`) and passes `--no-sync-mirror` to the batch so concurrent regressions never race
on the mirror tree; if that sync fails or times out the batch is served one request at a time, each
regression syncing for itself (`server_mirror_sync.batch_serialized` says so). A lone purpose-1
request and purposes 2 to 4 are served one at a time in file order, each syncing for itself. `--extra-arg=<gen_regress argument>` (repeatable, `=` syntax because the
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

Exclusion markers: when an exclusion file is loaded URG appends `(x)` to an instance name that
carries exclusions and `(X)` to one that carries them below; `parse_hierarchy_row` strips the marker
(recorded as `excl_marker`) so the gated rows still parse. Pinned on real excerpts by
`gen_cov_report.py self-test` (found by the first elcheck: with the marker unhandled, every gated row
was a parse_error and a measured round with the file loaded would have died).

## 6a. Build mechanics beyond vcs: pre_build, extra_ldflags, runtime_lib_dirs

A build entry may declare the fields below. One placeholder set is rendered in all of them:
`{outdir}` (the build directory) and `{mirror}` (the tree the runs execute from: the shared mirror
root from `gen_site.yaml`, or the clone root for a `--local-cocotb` build, whose runs stay on the
submit host). Any other brace token, or `{mirror}` without a mirror root, fails the build with the
known set named; nothing is dropped silently. Consequently a `pre_build` command cannot contain bash
`${VAR}` expansions or awk-style braces: put such logic in the script the entry calls.

- `pre_build`: commands run in order before vcs, clone root as cwd, the sourced environment
  inherited (for example TB Infra's `bash dv/auto_dv/isa/gen_isa_shim_build.sh lib {outdir}/lib`,
  which builds the Spike-backed ISA shim as a shared library next to the simv). Each step is
  logged to `<outdir>/pre_build_<i>.log`; a non-zero exit stops the build; `build_manifest.pre_build`
  records command, rc, wall time and the sha256 of every file under `<outdir>/lib`.
- `extra_ldflags`: appended to the SIM_RECIPE base `-Wl,--no-as-needed` into the single `-LDFLAGS`
  string (for example `-L{outdir}/lib -lgen_isa_shim -Wl,-rpath,{outdir}/lib`);
  `build_manifest.ldflags` is the string vcs saw.
- `runtime_lib_dirs`: directories exported as `LD_LIBRARY_PATH` by every run of the build (for
  example `{outdir}/lib` and `{mirror}/tools/spike/lib`): a shared library whose own rpath points into
  the clone cannot be resolved on a compute host, LD_LIBRARY_PATH can; recorded in
  `build_manifest.runtime_lib_dirs` and visible in each run's `run_cmd.sh`. `gen_regress.py` syncs the
  mirror with `--sync --spike` before a cocotb build, so `{mirror}/tools/spike/lib` is current for
  every regression; a standalone `gen_build.py` / `gen_run.py --lsf` relies on the last sync.
The values live in the build entry only (TB Infra owns the mechanics, the flow never re-types them).

## 7. gen_testlist.yaml (schema)

Rulings applied in the testlist (single source): every build entry carries `cov_trees:
[u_dut.u_ibex_core, u_dut.u_register_file]` (gated), `info_trees: [u_dut]` (informational) and
`extra_vcs_args: ["-cm_glitch", "0"]` (glitch filter for every measured build; VCS reports
`Warning-[VCM-OPTIGN]` because the filter does not apply to FSM coverage, so FSM is recorded as not
glitch-filtered). `schema_version: 1`. Header policies: `fcov_manifest_required_tiers` (list), `debug_only_plusargs`
(list of knob names; each must be a `PLUSARG_*` of gen_tb_pkg.sv, today `gen_dbg_csr_probe` =
`PLUSARG_DBG_CSR_PROBE`, probe P6). `builds.<name>`: `tb_top`, `dut_instance`, `filelists` (clone-root relative,
in order), optional `defines`, `cocotb`, `description`, `extra_vcs_args`, `cov_trees` (gated
coverage roots below tb_top, default `[dut_instance]`; the single source of the `-cm_hier` scope;
ruled: `[u_dut.u_ibex_core, u_dut.u_register_file]`), `info_trees` (instrumented, reported
informationally, never gated; ruled: `[u_dut]`), `pre_build`, `extra_ldflags`, `runtime_lib_dirs`
(Section 6a). `tests[]`: `name` (gen_
prefix, unique), `description`, `tier`, `build`, `uvm_test` (null for a top without a UVM test
class; otherwise a class identifier, anything else is rejected), `plusargs` (list of `+name=value`), `seeds` (count or list), `fcov_expectation_file`
(`dv/auto_dv/fcov_expectations/<name>.fcov.yaml` or null), `timeout_s`, `owner` (role slug),
optional `pass_marker`, `feature_groups`, `cocotb_module`, `expected_fail`, `component`, `notes`,
`measured`, `program` (Section 7e).
`gen_flow_util.load_testlist` rejects unknown keys, unknown builds, non-gen_ names, bad tiers and
owners, a tier-check test that is not `measured: false`, and any plusarg whose name is neither a
`PLUSARG_*` constant of `dv/auto_dv/tb/gen_tb_pkg.sv` nor a simulator/UVM plusarg (Critic P-06).
`gen_build.py`, `gen_run.py` and `gen_regress.py` each call `gen_flow_util.require_sv_constants()` first thing in `main()` (the SV/Python constants check); `gen_serve_requests.py` and `gen_dashboard.py` do not compile or run anything and rely on those three. The Test Writer adds test entries; TB Infra adds build entries; both through the runtime
owner (one owner per file).
`debug_only_plusargs` has one origin: TB Infra's rendered knob table `dv/auto_dv/gen_tb/gen_knobs.py`
(`PLUSARGS[<plusarg>]['debug_only']`, names included, no naming rule re-encoded in the flow);
`load_testlist` refuses the testlist unless its list equals that set. Test entry flags: `expected_fail`
(an RTL-vs-intent bug candidate; FAIL reported as XFAIL) and `red_fixture` with `red_expect` (a TDD
fixture that fails by design; a FAIL whose evidence line matches the regex is reported as RED-OK, any
other FAIL stays FAIL, an unexpected PASS is FAIL; requires `measured: false`, exclusive with
`expected_fail`; kept out of the pass rate and of coverage).

## 7a. Exclusion policy in the flow (Critic ruling R-5, dv/auto_dv/docs/gen_critic_exclusions_draft_v1.md)

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
  `gen_regress.py` re-syncs the mirror (`gen_mirror.py --sync --spike`) before a cocotb build (`--no-sync-mirror` to skip), so the
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
bins non-empty, unique, in the `gen_` namespace with exactly three dot-separated parts, written bare
(a quoted `- "..."` line is rejected because the checker reads the raw token), one non-empty
anti-vacuity note per bin, no note for an undeclared bin, no other keys. `python3 gen_fcov.py --validate` checks
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
(declared but unhit) or `fcov expectation unverifiable: <cause>` (protocol error: unverifiable is not
a pass; the flow names the cause from what is on disk, for example `per-test urg report has no
grpinfo.txt (no covergroup in this vdb)`). `declared` counts the validated manifest's bins even when
the checker printed nothing. The manifest as used is copied to `runs/<run>/fcov_manifest_used.yaml`,
and every regression copies its testlist to `<outdir>/testlist_used.yaml`, so no proof rests on an
uncommitted working file. The regression manifest carries `fcov.totals` (checked, pass, unmet, unverifiable) and
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
  `asserts.txt` (per-assertion ATTEMPTS / REAL SUCCESSES / FAILURES: the EC-3 evidence rtl-arch's
  `gen_excl_select.py --ec3-asserts` reads from the committed copy),
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
- Hard rules of a round (cross-model review T-055, DV Lead ruling P-04): the metrics come from the
  gate row only (the gated scopes combined by the summing rule above), never from the grand total (a
  missing or unparsed gate row is a hard error naming what is missing); the regression
  must be clean (gen_regress.py exit 0: no FAIL, TIMEOUT or NOT_RUN, merge ok, no strict-exclusion
  violation) or the round is refused and not indexed; the round number must be the next one in the
  index; group is gated as "bins >= 80 (traceability not checked here)" and never counts toward the
  gain; the entry records the regression verdict, `git_dirty_tracked_files` at regression time and
  the flow's git status at collect time; a dry run copies no full-exclusions dump.
- Numbers: code metrics from the DUT-scope row of hierarchy.txt (`cov_trees` of the build entry);
  functional coverage (Group) from the grand total (covergroups are TB-side gen_ instances).
- The DV Lead requests a round through the queue (purpose 4, `tests: full`, `coverage: yes`); the
  runtime role runs `gen_round.py --round <n>` and the Orchestrator commits the evidence directory.
- `--evidence-root DIR` redirects the evidence directory and index (self-tests only; the committed
  homes are the defaults).
- Instrumentation changes such as `-cm_glitch 0` (LOG-008, ruled 2026-09-03) live in
  `builds.<name>.extra_vcs_args` of gen_testlist.yaml (the single source of the build flag set); the
  round-0 baseline was re-measured under the ruled flag set and scope as `gen_round_0_rebaseline`
  (check tier, unmeasured until real tests exist) so later gains compare like with like.
  `gen_round.py --dry-run --tests <t> --seed-list <s> --evidence-name gen_round_0_<suffix>` is the
  re-baseline form.

## 7e. Program step (gen_stim.py) and the "boots and retires" templates

A test whose stimulus is a program carries a `program:` block; `gen_run.py` builds the image on
the submit host into `<run dir>/program/` with `dv/auto_dv/stim/gen_program.py` before the job is
submitted, and appends the image plusargs the memory model declares in `gen_tb_pkg.sv`
(`PLUSARG_MEM_IMAGE`, `PLUSARG_MEM_IMAGE_CRC32`; their strings are read from the package, and a
program-driven test refuses to run until both are declared). `result.yaml: program` records the
tool command, the seed used and its source (`run` or `fixed`), `prog.vmem` with sha256, the
sidecar and its `checksum.crc32`, the generator build. The flow exports `GEN_BUILD_CONFIG=opentitan`
into the tool's environment (the one home of the configuration name is `gen_flow_const.BUILD_CONFIG`);
`gen_program.py` and `gen_smoke_run.sh` carry their own copy today, so their owner (TB Infra) can
read the variable instead, or the duplicate stays documented here as a known second home. The compiled riscv-dv generator is shared:
`riscv_dv_gen_build:` in `dv/auto_dv/work/runtime/gen_site.yaml` (built once, on the shared root).

```
program:
  riscv_dv_test: gen_rand_smoke          # entry of dv/auto_dv/stim/gen_riscv_dv_target/gen_testlist.yaml
  # directed: [dv/auto_dv/stim/gen_directed/<file>.S]   # instead of riscv_dv_test
  # generator: dv/auto_dv/tests/gen_programs/gen_<group>_prog.py   # instead of both: a per-seed program
  # generator_args: ["--red"]                                      #   generator (clone-relative script)
  seed: run                              # the run seed (default); an integer pins the program for bring-up
  extra_args: []                         # passed to gen_program.py verbatim
  spike_check: false                     # gen_program.py --spike-check
```

Program forms, exactly one per block: `riscv_dv_test` (the riscv-dv generator build named by
`riscv_dv_gen_build` in gen_site.yaml), `directed` (a list of clone-relative sources), or
`generator` (a clone-relative script the flow runs first as `python3 <generator> --seed <seed> --out
<run>/program/gen_source.S <generator_args>`, clone root as cwd, bounded by the run's timeout, log
`<run>/program/generator.log`; the source it writes is then the one directed input of gen_program.py,
so the seed binding is by construction). The program record in result.yaml gains `generator`,
`generator_args`, `generator_command`, `generator_source`, `generator_source_sha256`,
`generator_wall_s`, `generator_log`. A generator that exits non-zero, times out or writes no source
stops the run before the simulator, like a failing gen_program.py (the regression records NOT_RUN
with the driver log). `program.seed` is `run` (the run seed) or an integer (pinned program).

Templates for TB Infra's first milestone ("boots and retires": gen_tb_top with the cocotb triple,
one riscv-dv program at a fixed seed, purpose 1, tier check, no coverage). Fill in the names; the
schema is fixed. Names in angle brackets are TB Infra's (from gen_tb_pkg.sv and the component API
documents); everything else is literal.

Build entry (`gen_testlist.yaml`, under `builds:`):

```
  gen_tb_top:
    description: real TB top around gen_dut_top, cocotb master, opentitan configuration
    tb_top: gen_tb_top
    dut_instance: u_dut
    cov_trees: [u_dut.u_ibex_core, u_dut.u_register_file]   # DV Lead ruling: the gated two inner instances (never nested)
    info_trees: [u_dut]                                       # the wrapper, reported informationally, never gated
    filelists:
      - dv/auto_dv/tb/gen_rtl.f
      - dv/auto_dv/tb/gen_tb.f             # TB Infra's TB-side filelist (env, agents, binds, top)
    defines:
      - RVFI
    cocotb: true
    extra_vcs_args: ["-cm_glitch", "0"]    # DV Lead ruling LOG-007/008: glitch filter on every measured build
```

Test entry (under `tests:`; tier check because a bring-up milestone is not a regression-tier test):

```
  - name: gen_boot_retire
    description: boots gen_tb_top from a riscv-dv program at a fixed seed, retires it, ends through the TB handshake
    tier: check
    build: gen_tb_top
    uvm_test: null                        # or the UVM test class name
    plusargs: []                          # +<PLUSARG_*> knobs of gen_tb_pkg.sv only; the image plusargs are added by the flow
    program:
      riscv_dv_test: gen_rand_smoke
      seed: 1
    seeds: [1]
    fcov_expectation_file: null
    timeout_s: 1800
    owner: tb-infra
    pass_marker: <the TB's end-of-test line, e.g. GEN_TEST_PASS>
    feature_groups: [bringup]
    cocotb_module: dv.auto_dv.<path>.<module>   # the cocotb test module (imported from the mirror on LSF)
    expected_fail: false
    component: gen_tb_top
    measured: false
```

Run request (`dv/auto_dv/work/runtime/requests/tb-infra-<seq>.yaml`):

```
requester: tb-infra
purpose: 1
tests: [gen_boot_retire]
seeds: [1]
coverage: no
notes: first boots-and-retires milestone of gen_tb_top; fixed program seed 1; waves not needed
```

The flow then: syncs the mirror, compiles gen_tb_top with the Section 4 triple against the mirror
venv, builds the program, runs one LSF job, and writes `results/tb-infra-<seq>/manifest.yaml`.

## 8. Reproduction recipe

From any manifest: `bash <run_dir>/run_cmd.sh` reruns the exact simv command with the same seed on
the current host (sources the staged env.sh). Through the flow: `gen_regress.py --repro <test>
<seed>` (fresh build, same testlist entry) or a purpose-3 request.

## 9. Cleanup rule

Every regression manifest records `lsf_jobs_left` (this regression's `gen_dv_<tag>_*` jobs still
active in `bjobs`: PEND, RUN or suspended; DONE and EXIT rows do not count); it must be empty. `gen_flow_util.lsf_jobs_left()` is the check (bjobs shows a finished job as RUN for a few seconds after `bsub -K` returns, so a non-empty answer is re-polled every 3 s for up to 15 s before it is recorded); the runtime role runs `bjobs`
at the end of every task.
