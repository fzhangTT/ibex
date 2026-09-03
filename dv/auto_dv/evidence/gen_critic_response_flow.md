# Runtime response to the Critic's flow verdict (gen_critic_t010_dv_principles_v1.md, REQUEST-CHANGES), to A-24 / P6 / R-01, and to every post-execution review of the flow (living file; promoted from dv/auto_dv/work/runtime/gen_critic_response_flow_v2.md, which stays as history)

Owner: runtime. Date: 2026-09-03 (T-038, extended in T-045 and T-049; v2 supersedes v1, which is kept unchanged as the file the Critic's re-review was queued on). Scope: dv/auto_dv/flow/** as of this response; validating runs
live under the out root `/proj_soc/user_dev/fzhang/ibex_dv_out` and are quoted from their manifests.
Evidence files: `dv/auto_dv/evidence/gen_t038_flow_red_runs.md` (P-01, P-02, P-09),
`dv/auto_dv/evidence/gen_t010_compile_path.md` Sections 5, 8, 8a (R-5, review fixes),
`dv/auto_dv/evidence/gen_t027_cocotb_lsf.md` (mirror, cocotb on LSF). API: `dv/auto_dv/docs/gen_runtime_api.md`.
One line per finding: FIXED (where, validated by) or DISPUTED (why).

| Finding | Status | Where (file:function) | Validating run / check |
|---|---|---|---|
| P-01 self-test on fabricated lines; no real red run | FIXED | `gen_verdict.py: REAL_FATAL / REAL_GREEN / REAL_COCOTB, self_test()` are verbatim excerpts of real runs; `gen_run.py --pass-marker` and the operator-plusarg override (`compose()`) exist for red-run evidence | `gen_t038_flow_red_runs.md`: `$fatal` run (LSF 10930762, FAIL `sv_fatal`, real `Fatal:` and `GEN_SMOKE_FAIL` lines, rc 0), TIMEOUT run (10930764, rc 124, no sim.log, TIMEOUT), missing-marker run (10930763, FAIL), green control (10930765, PASS); `python3 gen_verdict.py --self-test` PASS (27 cases at this writing; the tool prints the count). UVM_ERROR/UVM_FATAL and assertion red runs stated as not yet reachable (no UVM top, no DUT assertion trigger) in Section 4 of that file. |
| P-02 marker-substring PASS; exit code and $finish ignored; stderr not scanned | FIXED | `gen_verdict.py: marker_matches()` (marker = last whole token of its line), `decide_lines()` (PASS needs marker AND ($finish OR rc 0); rc not in {0,124} with clean log is FAIL "unexplained exit code"; crash signature in lsf.err/run.log/sim_stdout.log is FAIL); `gen_run.py` passes `stderr_logs` | self-test cases "marker but no $finish and no rc" (FAIL, the flipped case 12), "rc 139" (FAIL), "crash signature in stderr" (FAIL), "marker quoted inside a message" (FAIL); green control run PASS unchanged |
| P-03 --waves render crash; never run | FIXED (T-027) | `gen_flow_util.render_fields()` + `gen_flow_util.py --self-test`; `gen_run.py compose()` | `regress_t027_waves`: LSF 10930446, PASS, `waves.fsdb` 161985 bytes (gen_t010_compile_path.md Section 8a); side finding: compile-time `-ucli` rejected by VCS X-2025.06 (Error-[DBG_UCLI_DEP]); API doc Section 2 states which paths are evidenced |
| P-04 two documents state different coverage scopes | FIXED on the flow side; ruling PENDING | `gen_testlist.yaml builds.<name>.cov_trees` (default `[dut_instance]`) is the single source; `gen_build.py cov_trees()/cov_scopes()` render one `+tree <tb_top>.<tree>` each into `cm_hier.cfg`; `build_manifest.cov_scopes`, `coverage.dut_scope[<scope>]` per tree | Current scope `+tree gen_smoke_tb_top.u_dut` (wrapper), documented in the testlist comment as pending the DV Lead's ruling (asked by the Orchestrator); switching to `[u_dut.u_ibex_core, u_dut.u_register_file]` is a testlist edit, no code change. The duplicate statement in gen_component_api_dut_top.md Section 4 belongs to TB Infra; I asked TB Infra to point it at the testlist entry (message 06:14 UTC). Wrapper toggle objects (312/2420) stay in the denominator until the ruling. |
| P-05 -elfile without -excl_strict | FIXED (R-5 fold-in) | `gen_cov_report.merge()` adds `-excl_strict` with every `-elfile`, refuses `-excl_propagation`/`-excl_bypass_checks`; merge.log `UCAPI-ILOAD` sets `coverage.status: exclusion_violation` and `gen_regress.py` exits 3 | `regress_t010_r5_violation` (covered block excluded: FAIL, score unchanged) and `regress_t010_r5_ok` (uncovered block excluded: accepted, LINE denominator 4351 to 4349); `-excl_embed` NOT added: the merged vdb is regenerated from build vdbs every round, so embedding adds nothing the .el file does not already carry (DISPUTED in that detail). Excluded/Unreachable counts per module come from `gen_cov_report.py unreachable`; dashboard.txt has no such totals to record. |
| P-06 constants check never called; plusarg names and fcov exit codes re-typed | FIXED | `gen_flow_util.require_sv_constants()` called first in `gen_build.py`, `gen_run.py`, `gen_regress.py`; `load_testlist()` rejects a `+name` that is neither a `PLUSARG_*` of gen_tb_pkg.sv (`gen_flow_const.sv_plusarg_names()`) nor a simulator/UVM plusarg; `C.FCOV_EXIT_CODES` is the one table and `check_sv_constants()` verifies the checker's docstring still states 0/2/1 | `python3 gen_flow_const.py --check` PASS; testlist loads (gen_smoke_cycles is `PLUSARG_SMOKE_CYCLES`); a misspelt plusarg is refused at load time; `regress_t038_check` ran with the check in place |
| P-07 null fcov manifest silently exempt | FIXED | `gen_regress.summarize()` adds `runs_without_fcov_manifest` and `tests_without_fcov_manifest` to the summary and the one-line log; dashboard column "Runs w/o fcov manifest"; testlist header `fcov_manifest_required_tiers` (empty until the first covergroup) makes a null manifest FAIL on the named tiers (`fcov_policy_failures()`) | `regress_req_rtl-arch-002` summary: `runs_without_fcov_manifest: 2, tests_without_fcov_manifest: [gen_smoke]` |
| P-08 compiler_version regex never matches | FIXED | `gen_build.summarize_compile_log()`: `^\s*Version (\S+)` (the compile.log header line) | `regress_req_rtl-arch-002/build/gen_smoke/build_manifest.yaml`: `compile_summary.compiler_version: X-2025.06-SP2_Full64` |
| P-09 banner not required for PASS | FIXED | `gen_verdict.scan_log()` requires the line `GEN_CONFIG_BANNER build_config=<C.BUILD_CONFIG>`; the banner block is copied into `result.yaml: banner` | self-test cases "no config banner" and "wrong config in banner" FAIL; green run `banner_seen: true` |
| P-10 out root fallback only warns; pointer not in manifests | FIXED | `gen_regress.py`: a local-filesystem out root is refused for non-local regressions (`--allow-local-out-root` escape); `manifest.out_root`, `out_root_fs`, `site_yaml`; `gen_site.yaml.example` committed with the setup step in API Section 0 | `regress_t038_check2/manifest.yaml`: `out_root: /proj_soc/user_dev/fzhang/ibex_dv_out`, `out_root_fs: wekafs` (from `df -T`; the earlier `regress_t038_check` recorded the raw stat magic before the df-based lookup landed) |
| A-24 RTL-root override for mutation builds | FIXED | `gen_build.py --rtl-root DIR --mutation-id ID` (`absolutize_filelist()` substitutes any listed source that exists under DIR, clone-relative layout; refuses when nothing is substituted); manifest `rtl_root_override`, `mutation_id`, `rtl_substitutions` (file, original and mutated sha256); `gen_regress.py --rtl-root --mutation-id` forces every run `measured: false` (unmeasured vdb tree), records `manifest.mutation`, and refuses `--purpose 4` | mechanism in place; first use comes with the Test Writer's mutation-check runs (no mutated copy exists yet) |
| P6 debug-only CSR-flop probe never in a measured run | FIXED (mechanism) | testlist header `debug_only_plusargs` (knob names, declared once by TB Infra in the SV constants home and listed here); `gen_run.py` refuses a measured coverage run whose plusargs enable one: `result.yaml` NOT_RUN with the reason in writing, no LSF job | list empty until TB Infra names the knob (their gen_tb_knobs.yaml codegen); `gen_flow_util.plusarg_enabled()` treats `+name` and `+name=<non-zero>` as enabled |
| R-01 gen_smoke listed in tier smoke contradicts its contract | FIXED | `gen_flow_const.CHECK_TIER = "check"` outside smoke/targeted/full (selected only by `--tier check` or by name); `load_testlist()` requires `measured: false` on tier check; `gen_smoke` and `gen_cocotb_probe` are tier check, measured false; the smoke tier is empty | `regress_t038_check` (`--tier check`, 06:21 UTC): gen_smoke (LSF 10930834) and gen_cocotb_probe (10930835) PASS, both `measured: false`, coverage status `ok_no_measured_tests`, unmeasured report with 2 tests; `select_tests(smoke)` returns []; TB Infra informed (06:14 UTC), objection window open, Orchestrator's preferred option applied |

## T-027 post-execution review minors (dv/auto_dv/reviews/2026-09-03-claude-diff-daf7c356-e12f2f9f.md), same landing

| Finding | Status | Where | Validation |
|---|---|---|---|
| exit-code rule untested through decide() | FIXED | `gen_verdict.self_test()`: five file-based `decide()` cases on a temp dir (clean log rc 0 PASS; rc 1 FAIL; rc 124 + timed_out TIMEOUT; crash line in lsf.err FAIL; no sim.log + timed_out TIMEOUT) | `python3 gen_verdict.py --self-test` PASS (27 cases at this writing); evidence wording in gen_t038_flow_red_runs.md |
| two evidence claims without retained artifacts (outdirs reused with --force) | FIXED / reworded | DBG_UCLI_DEP re-created in a fresh retained outdir `<out root>/t038_evidence_ucli` (gen_t010_compile_path.md 8a); the first cocotb attempt (job 10930445) reworded as unretained with the `bhist -l` record (gen_t027_cocotb_lsf.md Section 2). Rule adopted: an outdir that evidence cites is never reused | build manifest of t038_evidence_ucli: status failed, `error_classes: ['DBG_UCLI_DEP']` |
| `gen_mirror.py --sync` without `--venv` reports fresh after a lock change | FIXED | `gen_mirror.requirements_hash()` (ci/requirements.lock, ci/requirements-cocotb.txt, ci/setup-venv.sh) recorded in `manifest.venv.requirements_sha256` at venv build; `status()` reports `stale_venv` when the clone's hash differs (or the venv has no record); a cocotb build refuses anything but `fresh` | `gen_mirror.py --sync --venv` (06:26 UTC, venv rebuilt in 9 s, manifest carries `venv.requirements_sha256`) then `--check` fresh; `regress_t038_check2` ran the cocotb probe against it (LSF 10931035, PASS) |
| gen_run.py accepted `--cov-dir == build_vdb` for an unmeasured test | FIXED | `gen_run.py main()`: an unmeasured run refuses the build vdb; default unmeasured target `<build outdir>/cov_unmeasured/<build>.vdb` (seeded copy) | local refusal test: `gen_run.py ... --measured no --cov-dir <build.vdb>` exits 1 with the reason |
| stale sentences (cwd sweep, --diag-noconst, -ucli) | FIXED | gen_runtime_api.md Sections 1 and 2; gen_run.py die message | text |
| render_fields docstring vs check | FIXED | `gen_flow_util.render_fields` docstring states the actual rule (only KNOWN names must be consumed) | `gen_flow_util.py --self-test` |
| check_mirror_for_run compares only the recorded hash | FIXED | `gen_run.check_mirror_for_run()` recomputes `tree_hash(mirror)` and requires build record == manifest == tree now | `regress_t038_check2`: gen_cocotb_probe PASS with `result.yaml: mirror.tree_sha256 b32a5b02df8b...` equal to the build record |

## T-038 post-execution review minors (dv/auto_dv/reviews/2026-09-03-claude-diff-8c22fe5e-edacfb10.md), T-045 landing

| Finding | Status | Where | Validation |
|---|---|---|---|
| red-run evidence names one discarded job | FIXED | gen_t038_flow_red_runs.md Section 5 lists 10930753-10930756 and states their out-tree was overwritten (LOG-005 standard) | text; bhist -l shows all four as `gen_dv_t038_red_gen_smoke_7` |
| standalone run on a mutation build defaults to build_vdb | already FIXED in d0a8a1c | `gen_run.py main()`: an unmeasured or mutation run defaults to `<build outdir>/cov_unmeasured/<build>.vdb` (seeded copy) and refuses the build vdb | local refusal test (T-038 minors table) |
| --rtl-root ignores typos and leftovers | FIXED | `gen_build.py`: every regular file under --rtl-root must match a filelist entry; leftovers are named and the build dies | code path; first use with the Test Writer's mutation copy |
| P6 refusal and fcov_policy_failures untested, no retained run | FIXED | `gen_flow_util.py --self-test` (plusarg_enabled cases), `gen_regress.py --self-test` (fcov_policy_failures: no covergroup / covergroups exist / header tier; fcov_summary; summarize); retained refusal run `regress_t045_p6_refusal` (measured twin of gen_smoke with `+gen_smoke_intg_flip=5` under `debug_only_plusargs`) | gen_t045_fcov_wiring.md Section 4: NOT_RUN written, no LSF job, regression exit 3 |
| fcov_policy_failures did not rewrite result.yaml | FIXED | `gen_regress.fcov_policy_failures` rewrites verdict and reason into result.yaml like post_fcov_checks | self-test + code path |
| stale doc text | FIXED | `--no-diag-noconst` everywhere (the T-010 evidence keeps the historical command with a note); `-ucli` compile-time mention removed from API Section 1; gen_run die message; gen_t010_compile_path.md 8a reason string updated to the P-02 wording | text |
| info: vcs+finish / vcs+stop allow-list entries cannot match | FIXED | `C.VCS_PLUSARG_PREFIX = "vcs+"`: any `+vcs+...` plusarg is accepted by prefix | `gen_flow_util.py --self-test` (plusarg_name keeps + inside vcs+ names) |
| info: banner rule skippable; banner collected from every log | FIXED | `gen_verdict.scan_log` requires build_config (raises otherwise); `decide()` collects the banner from sim.log lines only | self-test cases "banner in the stdout capture only does not count", "banner rule not skippable" |
| info: summarize() unused parameter | FIXED | parameter removed | compiles, self-test |
| info: --pass-marker on a measured run | FIXED | `gen_run.py` refuses `--pass-marker` when the run is measured | code path |
| info: API doc names the steps calling require_sv_constants | FIXED | gen_runtime_api.md Section 7: gen_build.py, gen_run.py, gen_regress.py | text |
| info: out_root_fs recorded as a raw stat magic | FIXED in d0a8a1c | `gen_flow_util.fs_type` uses `df -T` (wekafs); manifests before that fix keep the old string | regress_t038_check2 and later manifests: `out_root_fs: wekafs` |

## Critic re-review residuals (gen_critic_t010_dv_principles_v2.md, APPROVE) and T-052 follow-ups, next landing

| Item | Status | Where |
|---|---|---|
| record the testlist path and sha256 in every manifest | FIXED | `gen_regress.py` manifest `testlist: {path, sha256}`; `gen_run.py` result.yaml `testlist`; `gen_round.py` index entry `testlist` |
| remove the empty directory the refuse_covdir local test left | FIXED | `<out root>/t038_red/refuse_covdir` removed |
| name the fabricated self-test cases "fabricated" | FIXED | `gen_verdict.self_test()` (22 `fabricated ...`, 5 `real ...`, a closing line explains the naming), `gen_fcov.self_test()` (`fabricated manifest/report ...`) |
| reconcile self-test counts across documents | FIXED | gen_t038_flow_red_runs.md Section 3 and this file say 27 at this writing and point at the tool's own count |
| -cm_glitch 0 adoption belongs in builds.<name>.extra_vcs_args | FIXED | the `COV_GLITCH_FILTER` constant is removed from gen_flow_const.py; the API doc says adoption is a testlist build knob once ruled (LOG-008) |
| dry run must not carry the unmeasured full-exclusions dump; rounds keep theirs compressed | FIXED | `gen_round.collect()`: no dump copy for `--dry-run`; real rounds store `full_exclusions/fullexclude.<metric>.gz` (gzip, 320 KB instead of 3.2 MB on the smoke merge); exercised with `--collect ... --evidence-root <scratch>` on regress_t010_r5_ok |

## T-045 post-execution review minors (dv/auto_dv/reviews/2026-09-03-claude-diff-eccc461c-24f3dc0e.md), same landing

| Finding | Status | Where |
|---|---|---|
| evidence time window and the cited job's times | FIXED | gen_t045_fcov_wiring.md header: 06:34 to 06:38 UTC; job 10931279 submitted 06:37:22, dispatched soc-c-22, done 06:37:32 UTC (bhist) |
| proof rests on gitignored working files | FIXED | copies of the temporary testlist and manifest in `regress_t045_fcov_wiring2/inputs/` with sha256; from now on every regression writes `testlist_used.yaml` (manifest `testlist.copy`) and every fcov check writes `runs/<run>/fcov_manifest_used.yaml` (`fcov_check.manifest_copy`, `manifest_sha256`); rerun regress_t045_fcov_wiring3 shows both |
| checker's isolation assertion unexercised (RuntimeError fires first) | STATED | gen_t045_fcov_wiring.md Section 2 item 0 and the Section 1 row wording: the isolation evidence is the flow's reading of the retained tests.txt, not the checker's assertion |
| quote the urgReport listing; name the cause | FIXED | listing quoted in Section 1; `gen_fcov.protocol_cause()` names the cause from disk (`per-test urg report has no grpinfo.txt (no covergroup in this vdb)`, `per-test isolation not confirmed by the checker`, ...) and the run reason carries it |
| dashboard: "not checked (verdict X)" vs "no manifest" | FIXED | `gen_dashboard.py` uses `fcov_expectation_file` to tell the two apart |
| fcov_policy_failures must rewrite result.yaml | FIXED (was in the working tree, outside the reviewed range) | `gen_regress.fcov_policy_failures` |
| BIN_RE third group; quoted bin lines | FIXED | `[^.\s]+` (exactly three dotted parts); quoted `- "..."` lines rejected because the checker reads the raw token; self-test case added |
| declared from the validated manifest | FIXED | `run_checker(..., declared_bins=...)`: a PROTOCOL_ERROR shows declared=N, hit=0; self-test asserts declared=2 |
| document or drop the `notes` key | FIXED | dropped: allowed keys are test, owner, bins, anti_vacuity |
| COV_GLITCH_FILTER in the introducing commit | N/A | the constant was removed in the same landing (adoption goes into builds.<name>.extra_vcs_args); the landing message should say removed, not introduced |

## T-055: cross-model review of the T-049/T-052 range (dv/auto_dv/reviews/2026-09-03-claude-diff-24f3dc0e-8a8106bd.md), same landing

| Finding | Status | Where | Validation |
|---|---|---|---|
| MAJOR: metric_row fell back to the grand totals when the DUT row was missing or unparsed | FIXED | `gen_round.metric_row()` dies naming the scope; no fallback path exists | collect on a fabricated manifest with `dut_scope: {}` exits 1 with "coverage record has no DUT-scope row" and leaves no evidence directory (every refusal runs before anything is written) |
| MAJOR: run_regression ignored gen_regress.py's exit code | FIXED | `gen_round.run_regression()` dies on rc != 0 (2 = FAIL/TIMEOUT/NOT_RUN, 3 = merge or strict-exclusion failure); `--collect` recomputes the verdict from the manifest (`regression_verdict()`) and refuses a not-clean regression; the verdict is recorded in the round entry | collect on regress_t045_p6_refusal (1 NOT_RUN) exits 1 "not clean" with no directory left; clean collect on regress_t010_r5_ok indexes with `regression_verdict: clean`, `git_dirty_tracked_files: true`, the flow's git status and gzip dump copies (self-test into a scratch evidence root) |
| minor: first of several dut_scope entries used | FIXED | `metric_row()` dies on more than one scope (P-04 pending); `gen_dashboard.dut_scope_row()` shows n/a with a parse_error note instead of the first | fabricated two-scope manifest: exit 1 "coverage record has 2 DUT scopes ... no combining rule exists yet" |
| minor: group gate label and gain | FIXED | `gate_status()`: "bins >= 80 (traceability not checked here)"; `gain_against()`: max over GATED_CODE_METRICS only | summary page wording; self-test collect |
| minor: git dirty flag | FIXED | entry `git_dirty_tracked_files` (from the regression manifest) and `flow_git_status_now` (git status of dv/auto_dv/flow at collect time) | collect self-test shows both |
| minor: dry-run dump files listed but not committed | FIXED | gen_round_0_dryrun/gen_round_summary.md and gen_rounds.yaml now state the six files were removed before the commit and live in the out-tree; new dry runs copy no dump | text + index edit |
| minor: P6 refusal's temporary testlist unretained | FIXED | copy in `<out root>/regress_t045_p6_refusal/inputs/testlist_p6.yaml` (sha256 in gen_t045_fcov_wiring.md Section 4); every later regression retains `testlist_used.yaml` | text |
| info: round_no validation, GATED derived from URG_METRICS, "no round index yet" | FIXED | `collect()` dies when round_no != len(rounds) (not for a dry run); `GATED_CODE_METRICS = URG_METRICS minus group`; log line when the index is created | wrong round number (5 after round 0) exits 1 with no directory left |
| response file gitignored | FIXED | promoted with cp to dv/auto_dv/evidence/gen_critic_response_flow.md (this file); v1/v2 stay under work/ as history; updated here from now on | - |
| gen_t010 8a quoted the retired reason string | FIXED | row reworded to the current wording only | text |
| gen_mirror usage text | FIXED | docstring: run --venv once after a fresh mirror (without it the manifest reports venv MISSING and cocotb builds refuse) | text |

## T-057: DV Lead rulings applied (gen_tb_architecture.md Section 5), same landing

| Item | Status | Where | Validation |
|---|---|---|---|
| coverage scope = u_dut.u_ibex_core + u_dut.u_register_file (gated), wrapper informational | APPLIED | `gen_testlist.yaml` build entries: `cov_trees: [u_dut.u_ibex_core, u_dut.u_register_file]`, `info_trees: [u_dut]` (single source); `gen_build.py` instruments gated + info trees; `gen_cov_report.merge` parses every row and builds `gate_row` by `combine_rows` (covered and total summed per metric, percent = 100 x covered / total, n/a when no gated row reports the metric); `gen_round.metric_row` and `gen_dashboard.dut_scope_row` use the gate row, the wrapper row is listed as informational | `gen_round_0_rebaseline`: gate row LINE 1694/4351, COND 2547/9566, TOGGLE 1682/24538, FSM 6/86, BRANCH 798/2418, ASSERT 143/178 (= u_ibex_core 142/173 + u_register_file 1/5); wrapper row TOGGLE 1994/26958 (the 312/2420 wrapper port objects the ruling removes from the gate); combine self-check 50/100 + 20/20 = 70/120 = 58.33 |
| -cm_glitch 0 for every measured build | APPLIED | `extra_vcs_args: ["-cm_glitch", "0"]` on both build entries (per the Critic's residual, not a flow constant; the architecture document's sentence "Runtime makes it the default in gen_flow_const.py" describes the same intent at the testlist level); `build_manifest.glitch_filter`, `coverage.glitch_filter[<build>]`, `coverage.rulings`, round summary states the flag and that FSM is not glitch-filtered | rebaseline merge.log: zero Warning-[UCAPI-CSM], zero RCGLTCH (baseline had 14 and 1); LINE/COND/BRANCH equal the rtl-arch-001 trial numbers |
| round 0 re-baselined like for like | DONE | `gen_round.py --dry-run --tests gen_smoke --seed-list 330815564 --evidence-name gen_round_0_rebaseline`: `dv/auto_dv/evidence/gen_round_0_rebaseline/` (labelled "check tier, unmeasured until real tests exist; the new like-for-like baseline"), index `dry_runs` entry with `rulings`, `glitch_filter` and the informational row; `gen_round_0_dryrun` stays as the pre-ruling record | LSF job in regress_round_0_rebaseline; dashboard regenerated with the ruling references in its header |

## T-062: cross-model review of the T-055/T-057 range (dv/auto_dv/reviews/2026-09-03-claude-diff-8a8106bd-dc6de881.md), next landing

| Finding | Status | Where | Validation |
|---|---|---|---|
| medium: RULING_SCOPE hard-coded the instance names | FIXED | `C.RULING_SCOPE_TEMPLATE` + `ruling_scope_text(gated, info)`; `gen_regress.py` fills it from the builds' cov_scopes / info_scopes; the dashboard header uses the generic text | constants check + regenerated dashboard; the manifest text can no longer disagree with the testlist |
| medium: boots-and-retires template offered `cov_trees: [u_dut]`, lacked info_trees and the glitch flag | FIXED | gen_runtime_api.md Section 7e template: `cov_trees: [u_dut.u_ibex_core, u_dut.u_register_file]`, `info_trees: [u_dut]`, `extra_vcs_args: ["-cm_glitch", "0"]` | text |
| medium: nested gated trees accepted; combine_rows would double count | FIXED | `gen_flow_util.nested_pairs()`; `load_testlist` refuses a build whose gated trees nest; precondition stated in `combine_rows` docstring, `gate_row.rule` and API Section 3 | `gen_flow_util.py --self-test`: nested pair detected, siblings and prefix-only names (`u_dut.a` vs `u_dut.ab`) accepted, a testlist with `u_dut.u_ibex_core` + `u_dut.u_ibex_core.cs_registers_i` is refused |
| minor: regression_verdict treated a missing coverage block as clean | FIXED | `gen_round.regression_verdict()` returns `unknown` without a coverage block; `collect()` refuses it | code path |
| minor: gen_stim.main did not validate its inputs | FIXED | `ap.error` unless exactly one of `--riscv-dv-test` / `--directed` | `gen_stim.py --seed 1 --out x` exits with the usage error |
| minor: stale comments (glitch constant, dashboard docstring, cov_trees comment) | FIXED | restated as standing rules in gen_flow_const.py and gen_dashboard.py | text |
| self-tests used the shared /tmp for their scratch (F-001 rule) | FIXED | `C.SELFTEST_TMP` (dv/auto_dv/work/runtime/selftest_tmp) is the parent of every self-test temporary directory | self-tests PASS; /tmp untouched |
| minor: CONFIG_NAME second home in gen_program.py (third in gen_smoke_run.sh) | MITIGATED, owner informed | `gen_stim.py` exports `GEN_BUILD_CONFIG=opentitan` (`C.ENV_BUILD_CONFIG`) into the tool's environment; API Section 7e documents the trade-off; TB Infra (owner of both files) asked to read the variable or keep the documented duplicate | message to tb-infra |

## Defects found by real runs after T-062 (fixed in the same landing)

| Finding | Status | Where | Validation |
|---|---|---|---|
| crash-signature scan matched an ISS log line ("12000: Illegal instruction (hart 0) at PC ...") in sim_stdout.log and failed a passing gen_ut_bridge run (tb-infra-002, LSF job 10932403; marker, banner, $finish, cocotb 1/1, UVM_ERROR 0, exit 0 were all clean) | FIXED | `C.CRASH_RE` matches only the shell's process-termination report (`[bash: line N: ]<pid> Segmentation fault/Bus error/Aborted/Illegal instruction/Killed/Terminated [(core dumped)]`, `(core dumped)`, `timeout: sending signal`); `gen_run.py` scans lsf.err and run.log only (the job script's stderr), no longer the simv stdout capture | `gen_verdict.py --self-test`: the real ISS line is pinned as a PASS case, a bare shell kill report and the core-dump report as FAIL cases; tb-infra-002 re-served |

## Other changes made while closing these findings

- `gen_run.py --measured auto|yes|no` (gen_regress passes it; a mutation build forces no) and
  `--pass-marker` (red-run evidence only).
- Operator `--plusarg` replaces a same-name testlist plusarg (VCS honours the first occurrence).
- A TIMEOUT that fires before sim.log exists is TIMEOUT, not FAIL "sim.log missing".
- A requested exclusion dump lands on the unmeasured merge when the regression has no measured test.
- Testlist header keys `fcov_manifest_required_tiers`, `debug_only_plusargs`; build key `cov_trees`.

## What the Critic can re-check in one pass

```
cd dv/auto_dv/flow
python3 gen_flow_const.py --check          # SV/Python constants and fcov exit-code contract
python3 gen_flow_util.py --self-test       # template rendering (Tcl braces)
python3 gen_verdict.py --self-test         # 27 verdict cases (5 'real ...' pinned to real logs, 22 'fabricated ...')
```
plus the manifests named in the table (out root `/proj_soc/user_dev/fzhang/ibex_dv_out`).

## T-049 checklist (Orchestrator's 06:35Z list), one line per item

| Item | Where closed | Row in this file |
|---|---|---|
| four discarded first-attempt jobs listed in the red-run evidence | gen_t038_flow_red_runs.md Section 5 (10930753-10930756, out-tree overwritten, LOG-005 standard) | T-038 minors table, row 1 |
| --rtl-root leftover-file check with die | gen_build.py main(): every regular file under the root must match a filelist entry | T-038 minors table, row 3 |
| P6 refusal and fcov_policy_failures self-tests plus one retained NOT_RUN refusal | gen_flow_util.py --self-test, gen_regress.py --self-test; regress_t045_p6_refusal (gen_t045_fcov_wiring.md Section 4) | T-038 minors table, row 4 |
| result.yaml rewrite on fcov_policy_failures | gen_regress.fcov_policy_failures | T-038 minors table, row 5 |
| stale doc sentences | gen_runtime_api.md Sections 1 and 2, gen_run.py die message, gen_t010_compile_path.md 8a and Section 2 note | T-038 minors table, row 6 |
| vcs+finish / vcs+stop prefix match | C.VCS_PLUSARG_PREFIX in load_testlist | T-038 minors table, row 7 |
| banner rule not skippable; banner from sim.log only | gen_verdict.scan_log raises without build_config; decide() passes sim.log lines as banner_lines | T-038 minors table, row 8 |
| summarize() unused parameter | removed | T-038 minors table, row 9 |
| --pass-marker refused on measured runs | gen_run.py main() | T-038 minors table, row 10 |
| the require_sv_constants() sentence | gen_runtime_api.md Section 7 names gen_build.py, gen_run.py, gen_regress.py | T-038 minors table, row 11 |
| out_root_fs detection records wekafs | gen_flow_util.fs_type via df -T (d0a8a1c); regress_t038_check2 and later manifests | T-038 minors table, row 12 |
| F-001 operating rules in gen_runtime_api.md | Section 0, "Temporary locations (intervention log F-001)": never read or list shared temporary locations beyond the flow's own named paths, every temporary directory under the run's out directory, any accidental listing outside the clone / out root / mirror is reportable | - |
| F-001 grep confirmation (count only) | grep -r -l of the identifier over dv/auto_dv/: 0 files | - |
