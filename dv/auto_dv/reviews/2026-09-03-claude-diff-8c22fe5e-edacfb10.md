# Cross-model review - committed diff 8c22fe5e..edacfb10

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1; effort: high; fresh session d0614953-37b2-4928-9eb5-e99c569d3a3c (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** committed diff 8c22fe5e..edacfb10

---

TARGET: 8c22fe5e31343ea4a718e94d47dfd84c39b3aae9..edacfb1010d3cc93ec4e1b270a2ff578bf977a4d

Reviewer: Claude (model ID claude-fable-5-1, Claude Code CLI), fresh session, read-only, fallback reviewer per the recorded ruling in the previous artifact (codex spend cap). Scope: the single commit edacfb1 (14 files, +531/-116, all under `dv/auto_dv/**` with the `gen_` prefix; no `rtl/` or `ci/` file touched). Verified against the committed tree, the out root `/proj_soc/user_dev/fzhang/ibex_dv_out`, LSF history (`bhist`), and by running the flow's own read-only self-tests. Host clock is EDT; mtimes below are converted to UTC. Note: the working tree has uncommitted edits to `gen_verdict.py`, `gen_run.py`, `gen_mirror.py`, `gen_flow_util.py` and two docs; those are outside this range and are not credited here.

## Owner focus items, verified

**1. Red runs in `gen_t038_flow_red_runs.md` map to distinct retained artifacts.** Five run dirs under `t038_red/` (`fatal`, `timeout1`, `timeout5`, `nomarker`, `green`), each with its own `result.yaml`, `run_cmd.sh`, `run.log`, `lsf.out`, `bsub_cmd.txt`. Job id and host in every `result.yaml` match the evidence table and `bhist` (10930762/soc-c-10 FAIL sv_fatal; 10930764/soc-c-05 TIMEOUT rc 124; 10930761/soc-c-20 PASS; 10930763/soc-c-03 FAIL missing marker; 10930765/soc-c-20 PASS). Timestamps: all jobs submitted 06:16:19 to 06:16:24 UTC, finished by 06:16:30, files written 06:16:19 to 06:16:32, inside the stated 06:14 to 06:17 window. `run_cmd.sh` of `fatal` carries only `+gen_smoke_cycles=1` (the override works); `timeout1` has `timeout -k 20 1` and no `sim.log`, `sim_stdout.log` shows the VCS ASLR re-exec banner only. The `$fatal` run exits 0 with LSF "Done successfully" as claimed. The verbatim excerpts pinned as `REAL_FATAL` (fatal/sim.log lines 18-23), `REAL_GREEN` (green/sim.log lines 18-22) and `REAL_COCOTB` (t027 `sim_stdout.log` lines 33, 34, 40, 43) match the retained logs character for character.

**2. PASS rule.** `scan_log` returns FAIL on any collected hit, then on missing marker (whole-token match via `marker_matches`, `(^|\s)marker\s*$`), then on missing `GEN_CONFIG_BANNER build_config=<config>` line; `decide_lines` then FAILs a would-be PASS on a crash signature, on `not (finish_seen or rc == 0)`, and on rc outside {0, 124}. So PASS = no mechanism AND marker AND banner AND ($finish OR rc 0) AND rc in {0,124} AND no crash line, as documented. `python3 gen_verdict.py --self-test` at HEAD: PASS. The committed self-test drives `decide_lines()` (20 cases) with the real excerpts; `decide()` itself is a file-reading wrapper that is only exercised by the real runs, not the self-test, at edacfb1 (see finding 5).

**3. Constants check in every step.** `require_sv_constants()` is the first action in `gen_build.py:190`, `gen_regress.py:235`, `gen_run.py:162`; `gen_serve_requests.py` reaches it through `gen_regress`. `gen_flow_const.py --check`: PASS. Plusarg validation confirmed live: `sv_plusarg_names()` returns the three `PLUSARG_*` names and the testlist loads.

**4. Mutation builds vs measured vdb.** Through `gen_regress.py`: `measured = ... and not a.mutation_id` routes every run to the unmeasured vdb; the measured merge only takes `build.vdb` when some run is `measured: true` (none), so no measured merge happens; `--purpose 4` with `--mutation-id` is an `ap.error`. `gen_serve_requests.py` has no path to `--rtl-root`, so requests cannot trigger mutation builds. Manual `gen_run.py` against a mutation build is the remaining hole (finding 2).

**5. Check tier.** `select_tests("check")` returns exactly the two check tests; `smoke`/`full` selections exclude them (verified: both return `[]` today) and `gen_regress` dies on an empty plan ("no test selected"), so an empty tier cannot pass green. `load_testlist` rejects a tier-check test that is not `measured: false`. `regress_t038_check` manifest: tier `check`, 2 PASS, coverage `ok_no_measured_tests`.

**6. Previous review minors (2026-09-03-claude-diff-daf7c356-e12f2f9f.md), status at edacfb1.**
- minor 1 (no `decide()` test): partly applied. `decide_lines` now has rc 139 / crash / no-rc cases; `decide()` file path untested at edacfb1 (added only in the uncommitted working tree). Evidence wording at `gen_t010_compile_path.md:234` still says "nonzero exit with clean log" / "self-test plus the smoke reruns"; the reason string is now "unexplained exit code".
- minor 2 (overwritten first attempts): not applied; T-038 repeats the pattern (see finding 4).
- minor 3 (mirror venv hash after lock change): open (`gen_mirror.py:202` unchanged).
- minor 4 (`gen_run.py` should refuse `build.vdb` for unmeasured): open (finding 2).
- minor 5 (stale doc sentences): the "moves it from the vcs cwd" sentence is gone; `gen_runtime_api.md:40` `[--diag-noconst]`, `:48` `-debug_access+all -ucli`, and `gen_run.py:58` die text are still stale.
- info items (render_fields docstring, `check_mirror_for_run` recomputed hash): both open.

## Findings

[minor][dv/auto_dv/evidence/gen_t038_flow_red_runs.md:81] LSF accounting is incomplete: `bhist -J "gen_dv_t038*"` shows four discarded first-attempt jobs (10930753, 10930754, 10930755, 10930756, all 06:14 UTC, one exited 124, three Done), while §5 names only 10930755. Their run dirs were reused, so no artifact of the "plusarg did not override" or "verdict import crash" states survives. - List all four jobs and state that their artifacts were overwritten (LOG-005 standard), or keep failed attempts in their own tagged dir.

[minor][dv/auto_dv/flow/gen_run.py:177] A standalone `gen_run.py` on a mutation build with no `--cov-dir` defaults `cov_vdb` to `build["build_vdb"]`, so mutation coverage lands in the `build.vdb` tree while `result.yaml` says `measured: false`; the "cannot reach a measured vdb" guarantee holds only through `gen_regress.py`. Same as the previous review's minor 4. - When `measured` is false (mutation_id set, testlist flag, or `--measured no`), refuse `cov_vdb == build_vdb` and default to the build's `cov_unmeasured/<build>.vdb`.

[minor][dv/auto_dv/flow/gen_build.py:84] Only sources listed in the filelists are substituted from `--rtl-root`; a mutated file that is not on the list (typo in the path, or a header reached through `+incdir+`, which is never redirected) is silently ignored as long as one other file substitutes. The `die` at line 104 fires only when nothing at all matches. - Walk `rtl_root`, require every regular file under it to appear in `rtl_substitutions`, and die naming the leftovers; state in the API doc that include-path headers cannot be mutated this way.

[minor][dv/auto_dv/flow/gen_run.py:184] The P6 refusal (`debug_only_plusargs`) and the P-07 `fcov_policy_failures` (`gen_regress.py:165`) are new failure paths with no self-test and no retained run; `debug_only_plusargs` and `fcov_manifest_required_tiers` are both `[]`, so neither has ever fired. This is the standard the Critic's P-01 set for the verdict. - Add `plusarg_enabled`/refusal cases to a self-test (or a `gen_run.py --self-test`), and record one NOT_RUN refusal run once TB Infra names the knob.

[minor][dv/auto_dv/flow/gen_regress.py:171] `fcov_policy_failures` flips the in-memory run to FAIL but does not rewrite the run's `result.yaml` (unlike `post_fcov_checks`, which does), so the manifest and the per-run record will disagree once the policy is switched on. - Dump the updated run record to `result_yaml` as `post_fcov_checks` does.

[minor][dv/auto_dv/docs/gen_intervention_log.md:289] LOG-008 quotes LINE 2397/4351 etc. from rtl-arch-002 as reproducing the baseline, but with `gen_smoke` now `measured: false` that regression had no measured merge (`coverage.status: ok_no_measured_tests`); the numbers come from the informational `cov_unmeasured/report`, and the regression is therefore absent from dashboard §2. - Say the source is the unmeasured merge report and give its path; the same applies to the `gen_t010_compile_path.md` rtl-arch-001 paragraph if that request is ever rerun under the new tier.

[minor][dv/auto_dv/docs/gen_runtime_api.md:40] Stale text carried over from the previous review: `[--diag-noconst]` (the flag is `--no-diag-noconst`), line 48 `-debug_access+all -ucli` with `--waves` (compile-time `-ucli` was dropped in T-027), and the `gen_run.py:58` die message `(-debug_access+all -ucli)`. Also `gen_t010_compile_path.md:234` still quotes the old reason string. - Fix the four sentences.

[info][dv/auto_dv/flow/gen_flow_const.py:191] `vcs+finish` and `vcs+stop` in `SIMULATOR_PLUSARGS` can never match: those plusargs carry their value with `+` (`+vcs+finish+100`), and `plusarg_name` returns `vcs+finish+100`. - Match allow-list entries as prefixes for the `vcs+` family, or drop them.

[info][dv/auto_dv/flow/gen_verdict.py:37] `banner_seen = build_config is None` disables the banner rule when no config is passed; every caller passes one today, but a future caller can silently opt out. - Make `build_config` required, or FAIL when it is None.

[info][dv/auto_dv/flow/gen_run.py:233] `decide()` concatenates `sim.log` and `sim_stdout.log`, so the banner block appears twice in `result.yaml` and "log line N" indexes the concatenation. - Collect `banner` from `sim.log` only, or dedupe.

[info][dv/auto_dv/flow/gen_regress.py:150] `summarize(runs, testlist)` never uses `testlist`. - Drop the parameter.

[info][dv/auto_dv/flow/gen_run.py:156] `--pass-marker` is documented as "red-run evidence only" but is accepted on measured runs too; the override is recorded in `result.yaml`, so it is auditable, not hidden. - Refuse it unless `measured` is false.

[info][dv/auto_dv/docs/gen_runtime_api.md:279] "Every flow step first runs `require_sv_constants()`" overstates: `gen_serve_requests.py`, `gen_dashboard.py`, `gen_cov_report.py`, `gen_mirror.py` do not call it (the first reaches it via `gen_regress`). Both retained T-038 manifests record `out_root_fs: unknown (0x18031977)`, i.e. the `stat -f` path; the committed `df -T` path has no retained manifest but returns `wekafs` when I ran it. - Name the three steps that check, and let the next regression manifest evidence the `df -T` path.

## Rubric results

- ai-slop-comments: `{"status": "PASS"}`. Added comments state intent with Critic anchors (A-24, P-04, P-06, P6). Below threshold: self-test case name "P-02 flipped case 12" (gen_verdict.py:179) narrates the old numbering.
- rtl-purity: `{"status": "PASS"}` (no `rtl/` files in the diff).
- magic-numbers: `{"status": "PASS"}`. New literals live in `gen_flow_const.py` (`CRASH_RE`, `FCOV_EXIT_CODES`, `SIMULATOR_PLUSARGS`, `CHECK_TIER`); `cov_trees` defaults to the one testlist `dut_instance`. Note only: `gen_verdict.py:142` types `BANNER = "GEN_CONFIG_BANNER build_config=opentitan"` and the self-test passes `"opentitan"` instead of `C.BANNER_TAG`/`C.BUILD_CONFIG`; defensible as verbatim real-log pinning.
- forces-and-hier-access: `{"status": "PASS"}`. No SV or cocotb deposits in the diff.
- assertion-integrity: `{"status": "PASS"}`. The only removed self-test expectation ("marker but no finish" = PASS) is replaced by two stricter cases; every other change adds a FAIL path (banner, crash signature, exit-code rule, check-tier and plusarg validation). Nothing disabled.

Summary: the four owner focus items hold on disk. Every red run in the evidence maps to a distinct retained directory whose job id, host and timestamps agree with LSF history, and the pinned excerpts are verbatim; the PASS rule is marker-whole-token AND banner AND ($finish OR rc 0) AND rc in {0,124} AND no crash line, self-tested through `decide_lines`; the constants check runs first in build, run and regress; mutation builds are unmeasured and refuse purpose 4 through the regression driver. Open: the standalone `gen_run.py` vdb default (previous minor 4), incomplete LSF accounting for the discarded first attempts, silent non-substitution under `--rtl-root`, two new failure paths with no test or run, and stale doc sentences from the previous review. No blocker.

Final verdict: APPROVE-WITH-CHANGES
