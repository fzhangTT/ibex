# Cross-model review - committed diff daf7c356..e12f2f9f

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1; effort: high; fresh session dfc52a44-d9d1-4785-a8d2-45a38519e5fc (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** committed diff daf7c356..e12f2f9f

---

TARGET: daf7c3562e29adae4ea812cfbd1962b426ae8baa..e12f2f9fcdbc9882e4fb5385157dcae178df4acb

Reviewer: Claude (model ID claude-fable-5-1), fresh session, read-only. Scope: the single commit e12f2f9 (18 files, +946/-131, all under `dv/auto_dv/**` with the `gen_` prefix). Verification was done against the committed tree, the out root `/proj_soc/user_dev/fzhang/ibex_dv_out`, the mirror `/proj_soc/user_dev/fzhang/ibex_dv_mirror`, LSF history (`bhist`), and by running the flow's own read-only self-tests. Host clock is EDT; all artifact mtimes below were converted to UTC and match the evidence.

## Owner focus items, verified

**Seven findings of the previous review (0b8d60b4..8fa6b7a0)**

1. Waves rendering: `str.format` replaced by `gen_flow_util.render_fields` (token replacement). `python3 gen_flow_util.py --self-test` run by me: 6/6 checks PASS. Real waves run exists: `regress_t027_waves/runs/gen_smoke_330815564/` holds the rendered `dump.tcl` with intact Tcl braces, `waves.fsdb` 161985 bytes (05:58:27 UTC), `novas_dump.log`, `result.yaml` PASS, LSF job 10930446 on soc-c-20 (bhist: Done successfully 01:58:27 EDT). Build manifest has `-debug_access+all` and no compile-time `-ucli`, consistent with LOG-006.
2. Nonzero exit on clean log: `gen_verdict.decide` line 84 turns a would-be PASS with rc not in {0, 124} into FAIL. Applied; see finding 1 on test coverage.
3. `uvm_test: null` in the testlist; `load_testlist` rejects non-null non-identifier values. Loaded the testlist: `gen_smoke -> None`, `gen_cocotb_probe -> None`.
4. Hyphenated VCS codes: `[\w-]+` in both regexes. Applied; see finding 2 on its evidence.
5. Dashboard GROUP source: `dut_scope_row` takes the six code metrics from the DUT row and Group from the grand total; `load_manifests` annotation fixed to a tuple. Documented in `gen_runtime_api.md` §5.
6. Per-build cwd: vcs runs with `cwd=outdir` over absolute-path filelist copies; `sweep_side_files` and `VCS_CWD_SIDE_FILES` removed. The two filelists contain only `+incdir+` directives and file paths, which `absolutize_filelist` handles. `constfile.txt` present in `regress_t010_r5_ok/build/gen_smoke/`; the clone root holds no `vcs.key`/`ucli.key`/`constfile.txt`/`.fsm.sch.verilog.xml`.
7. Duplicate `coverage` assignment removed; `gen_site.yaml.example` checked in; §0 setup step added.

**Shared-storage mirror**

- Content hash: `tree_hash` covers `dv/auto_dv/**/*.py`, `ci/env.sh`, `ci/setup-venv.sh`, both requirements files (20 files in clone and mirror). Build side: `cocotb_lib` refuses a non-`fresh` mirror unless `--allow-stale-mirror` and records root/hash/HEAD/state in `build_manifest.yaml` (confirmed: `state_at_build: fresh`, `tree_sha256 dc642d2b…`, `git_head 3c623e5…`). Run side: `check_mirror_for_run` refuses when the mirror manifest hash differs from the build's record; `result.yaml` records the mirror used. `gen_mirror.py --check` run by me now reports `stale` with exit 1 (clone hash moved on since 06:02:07Z), proving the refusal path is live.
- Venv on shared storage: `build_venv` runs the mirror's own `ci/setup-venv.sh` (ROOT derives from the script location, so `.venv` lands under the mirror); `venv.log` shows `-r /proj_soc/.../ibex_dv_mirror/ci/requirements-cocotb.txt`; the VPI `.so` and `python3` symlink live under the mirror; `/proj_soc` is `wekafs`. `venv_info` requires the reported lib to sit inside the mirror.
- Mirror manifest: git HEAD 3c623e5 with `dirty_tracked_files: true`, synced 06:02:07Z; commit timestamps confirm HEAD was 3c623e5 until a4137b5 at 06:03:51Z, so the claim is consistent. Mirror Python files equal the e12f2f9 versions except `gen_serve_requests.py` (the `build_vcs_args`/`--extra-arg` additions were made after the sync); that file is not imported by the probe, so the proving run is unaffected.

**cocotb on LSF evidence** (`regress_t027_cocotb`, all mtimes 06:02:08 to 06:03:09 UTC)

- `manifest.yaml`: `mirror_sync rc 0 / 1.3 s`, build ok 27.9 s, run wall 23.4 s, `lsf_jobs_left: []`, coverage `ok_no_measured_tests`, unmeasured merge ok with `input_vdbs: [cov_unmeasured/gen_smoke_cocotb.vdb]`.
- `build_manifest.yaml`/`compile.log`: `-load /proj_soc/.../ibex_dv_mirror/.venv/.../libcocotbvpi_vcs.so`, 0 `Error-[`, warnings SIOB 32, LCA_FEATURES_ENABLED 1, VPI-CT-NS 4 (grep count 4).
- `run_cmd.sh`: sources the mirror `ci/env.sh`, exports MODULE/PYTHONPATH(mirror)/TOPLEVEL/TOPLEVEL_LANG/RANDOM_SEED, `+ntb_random_seed=315612868`, `-cm_dir cov_unmeasured/gen_smoke_cocotb.vdb`, stdout to `sim_stdout.log`.
- `lsf.out`: `GEN_RUN_ENV … VIRTUAL_ENV=<mirror>/.venv LIBPYTHON_LOC=/tools_soc/…/libpython3.12.so.1.0`, `GEN_RUN_SEED … host=soc-c-15 utc=2026-09-03T06:02:41Z`, `GEN_RUN_EXIT rc=0`. bhist job 10930476: dispatched soc-c-15, Done 02:02:59 EDT.
- `sim_stdout.log`: every quoted line in the evidence is present verbatim (venv interpreter, VPI registered, cocotb v1.9.2 from the mirror, seed 315612868, module path under the mirror, `cycles=200 rvfi_retired_seen=197`, `GEN_COCOTB_PROBE_PASS`, `TESTS=1 PASS=1 FAIL=0`, `$finish at 205501`). `results.xml` names the mirror module path and seed. `result.yaml`: PASS, exit 0, cocotb summary 1/1/0.

**Exclusion flow (R-5)**

- `merge()` appends `-excl_strict` whenever an `-elfile` is given, refuses `-excl_propagation`/`-excl_bypass_checks`, classifies `Warning-[UCAPI-ILOAD]`/`Illegal exclusion attempt`/`Error-[UCAPI` as `exclusion_violation`; `gen_regress.py` returns 3 on any merge status other than ok/ok_no_measured_tests.
- `regress_t010_r5_ok`: `urg_cmd.sh` has `-elfile … -excl_strict -dump full_exclusions`; `coverage.status: ok`, `excl_strict: true`, DUT row LINE 2397/4349 in `hierarchy.txt`, 12 files in `cov/full_exclusions/`, `constfile.txt` 284 KB, `build_defines` and `constfiles` recorded. The `.el` excludes the uncovered `rf_rdata_ng_a = fwd_wdata_i;` block as stated.
- `regress_t010_r5_violation`: `merge.log` line 11 `Warning-[UCAPI-ILOAD] Illegal exclusion attempt`; `coverage.status: exclusion_violation`; LINE unchanged 2397/4351; the `.el` excludes the covered `rf_rdata_ng_a = rf_rdata_a_i;` block. The exit-3 claim follows from the code path; the exit code itself is not an on-disk artifact.

**Measured vs unmeasured vdb**

- `compile_build` copies the compile-time vdb to `cov_unmeasured/<build>.vdb`; `run_one` routes `measured: false` runs there; the measured merge lists only `build/<name>/build.vdb`. `regress_t010_r5_split`: `build/gen_smoke/build.vdb/…/testdata/` contains only `test_gen_smoke_330815564`; `cov_unmeasured/gen_smoke.vdb/…/testdata/` contains only `test_gen_smoke_unmeasured_1737715210`; the measured merge's `input_vdbs` has one entry. Per-regression job tags confirmed (`-J gen_dv_regress_t010_jobtag_gen_smoke_330815564`; t027 jobs carry the tag in bhist, the earlier r5 jobs do not, matching the change order).

Other checks run: `gen_flow_const.py --check` PASS; `gen_verdict.py --self-test` 12/12 PASS; the `--build-vcs-arg "-cm_glitch 0"` single-token form was accepted by VCS in a later build (`regress_req_rtl-arch-001`, status ok), so it is not a defect.

## Findings

[minor][dv/auto_dv/flow/gen_verdict.py:84] The new exit-code rule has no test: `self_test()` (line 94) exercises `scan_log` only, never `decide()`, and the evidence row "self-test plus the smoke reruns" (gen_t010_compile_path.md:223) is therefore inaccurate; the smoke reruns only show rc=0 stays PASS, nothing shows a clean log with rc=1 becomes FAIL. - Add `decide()` cases on a temp file: clean log + rc 1 -> FAIL, rc 0 -> PASS, rc 124 + timed_out -> TIMEOUT; correct the evidence wording.

[minor][dv/auto_dv/evidence/gen_t010_compile_path.md:222] Two evidence claims have no retained artifact: the first waves attempt (`Error-[DBG_UCLI_DEP]`, `error_classes: ['DBG_UCLI_DEP']`, "status failed although vcs returned 0") and the first cocotb attempt's FAIL verdict (gen_t027_cocotb_lsf.md:81, job 10930445). Both outdirs were reused with `--force`; no `compile.log` or manifest under the out root contains `DBG_UCLI_DEP`, and only `bhist` still shows job 10930445 (Done, soc-c-19, 05:58 UTC). The hyphenated-code fix is thus verified by code reading, not by the cited artifact. - Keep failed attempts in their own tagged outdir, or state in the evidence that the artifact was not retained (LOG-005 standard).

[minor][dv/auto_dv/flow/gen_mirror.py:202] `--sync` without `--venv` re-reads `venv_info(dst)` and writes a manifest whose `tree_sha256` includes the requirements/lock files, so the mirror reports `fresh` after a lock change while its venv was built from the old lock. - Record the requirements-file hash at venv build time and report `stale`/refuse unless `--venv` when it differs.

[minor][dv/auto_dv/flow/gen_regress.py:91] The measured/unmeasured separation is enforced only here; `gen_run.py` has the testlist entry and `build_vdb` but accepts any `--cov-dir` for a `measured: false` test (no `measured` reference in the file), so a manual `gen_run.py` can write mutation-evidence data into a `build.vdb`. - Have `gen_run.py` refuse `--cov-dir == build_vdb` when the test is `measured: false`.

[minor][dv/auto_dv/docs/gen_runtime_api.md:56] Added text says the flow "moves it from the vcs cwd into the outdir (with the other cwd side files…)", contradicting the new behaviour stated nine lines lower (vcs runs with the outdir as cwd; no sweep). Also stale: line 40 `[--diag-noconst]`, line 48 `-debug_access+all -ucli`, and the `gen_run.py:56` die message `(-debug_access+all -ucli)`. - Fix the four sentences.

[info][dv/auto_dv/flow/gen_flow_util.py:171] Docstring claims "an unknown {token} fails loud", but the leftover check only tests names already in `fields`, which cannot remain after replacement; unknown tokens pass silently. - Either fail on any leftover `{identifier}` (the Tcl template's braces contain spaces, so it tolerates this) or correct the docstring.

[info][dv/auto_dv/flow/gen_run.py:87] `check_mirror_for_run` compares the recorded manifest hash, not a recomputed mirror tree hash, so a direct edit to the mirror without `--sync` is undetected. - Recompute `tree_hash(root)` (20 files) and require it to equal the manifest too.

## Rubric results

- ai-slop-comments: PASS. Added comments state intent and site gotchas (the `DBG_UCLI_DEP` note, the cwd rationale, the stdout-capture reason). `gen_flow_util.py:183` "(review finding, T-010)" is mild provenance narration, below the flag threshold.
- rtl-purity: PASS (no `rtl/` files in the diff).
- magic-numbers: PASS. Mirror paths, URG option sets, exit codes and env names live in the flow constants homes; `PROBE_CYCLES = 200` is a test-local bound with an adjacent comment; the DUT hierarchy path appears only in the testlist. Note only: `GEN_COCOTB_PROBE_PASS` is typed in both the probe module and the testlist `pass_marker`, with no cross-check like the one `gen_flow_const.py --check` does for plusargs.
- forces-and-hier-access: PASS. `gen_cocotb_probe.py` only reads `rst_n`, `clk`, `rvfi_valid`; no deposits.
- assertion-integrity: PASS. Nothing disabled or removed; one Python assert added; removing compile-time `-ucli` is a tool-compatibility change, not a checker change; `-assert nopostproc` is unchanged SIM_RECIPE §3 usage.

Summary: all seven prior findings are applied and the six owner focus items are backed by on-disk artifacts with consistent timestamps and LSF history; the mirror, strict exclusion, and vdb-separation mechanisms behave as documented on the exercised paths. Remaining items are a missing test for the new verdict rule, two evidence claims whose artifacts were overwritten, a venv-freshness gap, a single-script enforcement gap, and stale documentation sentences.

Final verdict: APPROVE-WITH-CHANGES
