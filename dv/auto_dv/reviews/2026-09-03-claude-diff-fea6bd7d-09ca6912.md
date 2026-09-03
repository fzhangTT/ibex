# Cross-model review - committed diff fea6bd7d..09ca6912

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 180cc59e-6466-4e0a-bfa9-61bd39b8bec4; sandbox: bubblewrap, filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** committed diff fea6bd7d..09ca6912 (echo at raw line 1)

---

TARGET: fea6bd7db46a7d19ad849ffa229370a5d741c44b..09ca69127a998cabdc885d62c74dc76793d908d6

Reviewer: Claude Fable 5.1 (claude-fable-5-1), fresh non-interactive session, read-only sandbox (clone and out root `/proj_soc/user_dev/fzhang/ibex_dv_out` mounted read-only; only a private `/tmp` writable, removed after use). Scope: five commits, 16 files, +1318/-617, no `rtl/` change. Flow files in the working tree are identical to 09ca691 (`git status` clean for `dv/auto_dv/flow/*.py`); `gen_tb_pkg.sv` and `gen_testlist.yaml` differ in the working tree (T-080 landing), so every retention probe below was run against the committed `gen_tb_pkg.sv` as well.

**Prior findings of `2026-09-03-claude-diff-855c13fa-fea6bd7d.md`, judged against the code**

| # | Finding | Status | Evidence |
|---|---|---|---|
| 1 (medium) | stale `gen_source.S` passed a no-op generator | ADDRESSED | `gen_stim.py:41-43` rmtree + mkdir of the program dir before the generator; `:57-59` requires regular file, size > 0, mtime at or after invocation. Retained proof `work/runtime/out/t_generator_check2_1019`: `gen_boot_zc_gen_noop_1` and `_empty_1` have only driver.log + `program/generator.log` with "source written by this invocation=False", the green run PASS with `generator_source_sha256`. My own probes (below) confirm symlink, hard link, `copy2` and `utime`-backdated sources are refused and a plain write is accepted. |
| 2 (medium) | `build_program` ran under the 1800 s default | ADDRESSED | `gen_run.py:224-225` passes `timeout_s=timeout_s` (`:182` = `--timeout-s` or testlist); both stages use it (`gen_stim.py:56`, `:78`); doc `gen_runtime_api.md:582-583` now says "each program stage bounded by the run's timeout_s". See low finding on the outer bound. |
| 3 (low) | generator inherited env without `PYTHONHASHSEED` | ADDRESSED | `gen_stim.py:46` builds one explicit env with `PYTHONHASHSEED="0"` and `GEN_BUILD_CONFIG`, used by both `run_bounded` calls. |
| 4 (low) | `dv/../../x.py` accepted | ADDRESSED | `gen_flow_util.py:302-309` `clone_relative_file`: refuses non-str, empty, absolute, any `..` part, resolved path outside `REPO_ROOT.resolve()`, non-file; loader uses it at `:418-419`. Probe with a fake clone root: in-clone file and in-clone symlink accepted; symlink to an outside file, a symlinked directory component leading outside, `dv/../dv/ok.py`, absolute path, a directory, `""`, `None`, `3` all refused. Self-test row at `:142-145` covers `..`/absolute/missing (not the symlink case, which I covered above). |
| 5 (low) | `--red-expect` CLI bypassed the empty-match refusal | ADDRESSED | `gen_flow_util.py:289-299` `red_expect_error` is the one rule; loader `:388-390`, CLI `gen_verdict.py:365-369` via `ap.error`. Probed: `--red-fixture --red-expect '.*'` exits 2 "matches the empty string"; `--red-fixture` without `--red-expect` exits 2 "must be a non-empty regex"; a real signature proceeds. |
| 6 (info) | self-tests hard-coded a clone scratch dir | ADDRESSED | `gen_flow_const.py:74-82` `GEN_DV_SELFTEST_TMP`; with it set to a private dir all three self-tests ran here: `gen_flow_util --self-test` 32 ok, PASS; `gen_verdict --self-test` 60 ok, PASS; `gen_regress --self-test` 9 ok, PASS (including `prune_plan`/`prune_exports` rows); `gen_flow_const --check` PASS. Without the override the run dies on the read-only clone exactly as the previous reviewer reported. |

**Retention (09ca691), verified**

- FAIL runs are never pruned: `prune_plan` (`gen_regress.py:233`) filters on `r["verdict"]` from the in-memory `runs` list, and both later verdict flips write into those same dicts (`post_fcov_checks` `:139-145` via `RUN.apply_fcov_check(r, ...)`, `fcov_policy_failures` `:203-204`), so an fcov-unmet or policy FAIL is seen by the pruner. XFAIL, TIMEOUT, NOT_RUN are also kept.
- Ordering: `prune_exports` runs at `:539-541`, after `post_fcov_checks` (`:486`), the urg merges (`:502`, `:518`), `fcov_policy_failures` (`:528`) and the "done" manifest (`:538`). Nothing in the committed flow reads the export file afterwards (`git grep` of `gen_round.py`, `gen_cov_report.py`, `gen_run.py`: no export references); the addendum at 09ca691 `gen_rvfi_export_addendum.md:104-105` places the Python fire-checks inside the run, before the verdict. So pruning cannot remove a coverage-merge or fcov-expectation input.
- No-knob path is a recorded no-op: the committed `gen_tb_pkg.sv` has 120 `PLUSARG_*` parameters and no `PLUSARG_EXPORT_FILE`; against it `export_plusarg_name()` returns `None` and `prune_exports` returns `{export_plusarg: None, applies: False, runs_planned: 0, files_pruned: 0, ...}`, which lands in `manifest["retention"]` (`:540`). Purpose `None` gives the same block. The working-tree pkg declares `gen_export_file` "relative to the run directory", which matches `res_path.parent / fname` since the sim's cwd is the run dir (`gen_run.py:249`, `:263`).
- `keep_artifacts` is accepted by the loader (`gen_flow_const.py:219-221`, unknown-key refusal at `gen_flow_util.py:373`), counted in `runs_kept_by_keep_artifacts`.

**Other verification**

- efe1c91 plan set: ran the committed `tools/gen_trace_check.py` on the committed docs at 09ca691 and at fea6bd7: PASS both, 705/705 ACTIVE->TP, 705/705 ACTIVE->bin, 207/207 covergroups, 15825/15825 CSV bins, matching the commit message. "coverage-only" occurrences in `gen_test_plan.md` went from 29 to 252; Section 0 carries the cycle-level fire-check rule (`:43-50`).
- Rubrics: ai-slop-comments PASS (see info note on a dated ruling citation); rtl-purity PASS (no `rtl/` lines); magic-numbers PASS (`RETENTION_PRUNE_PURPOSES`, `SV_PLUSARG_EXPORT_FILE` live in the constants home; the export plusarg string is read from `gen_tb_pkg.sv`, the self-test's `+gen_export_file=...` literals are fixture data passed explicitly as the plusarg parameter); forces-and-hier-access PASS (no SV, no drives); assertion-integrity PASS (loader check moved intact into `red_expect_error`, self-test cases added, none removed or weakened).

**Findings**

[low][dv/auto_dv/flow/gen_regress.py:256] `target = res_path.parent / fname` has no containment check, so a testlist export value of `../x.txt` or an absolute path makes a purpose-4 regression delete a file outside the run directory, and the recorded path is unnormalized. Reproduced on a fabricated tree: `+gen_export_file=../outside.txt` removed `runs/outside.txt` and recorded `.../gen_a_1/../outside.txt`; an absolute value removed that file. The ruling text ("never deletes inside a run directory during a regression") assumes the file is under the run dir. - Resolve `target` and require `res_path.parent.resolve()` among its parents; otherwise leave the file and record `pruned_artifacts_skipped` with the reason (or refuse such values in the loader).

[low][dv/auto_dv/flow/gen_stim.py:57] The freshness rule compares the submit host's `time.time()` with `st_mtime` of a file on the shared out root (wekafs, `path_is_shared` True). If the filesystem's timestamp source lags the host by more than 1 s, a correct generator is refused with "source written by this invocation=False" and the run is NOT_RUN; I could not measure the skew here (out root read-only in this sandbox). The emptied directory (`:41-43`) already makes a stale file impossible, so the clock comparison only adds the symlink/hard-link/`copy2` cases. - Use a same-filesystem sentinel (write a marker in `out` just before the invocation and require `src.stat().st_mtime >= marker.stat().st_mtime`), or replace the clock test with `not src.is_symlink() and src.stat().st_nlink == 1` plus the sentinel.

[low][dv/auto_dv/flow/gen_regress.py:110] With finding 2 fixed, the generator and gen_program.py may each legitimately take up to `timeout_s`, but the driver's outer bound is `timeout_s + 20 + 300 (+ pend)`. A program stage that is slow but within its own bound eats the simulator's budget and surfaces as "gen_run.py wrote no result.yaml" instead of a timeout attributed to the right stage. - Add the program budget to `outer` when the test has a `program` block, or give the two program stages a smaller dedicated bound and say so in 7e.

[info][dv/auto_dv/evidence/gen_critic_response_flow.md:61] The retention row's "Where" names the `gen_testlist.yaml` header, but that file is not in this range and the committed testlist has no `keep_artifacts` text (the header line exists only in the working tree, held for T-080 as the commit message says). - Mark it "(held for the T-080 landing)" so the row does not read as committed.

[info][dv/auto_dv/flow/gen_stim.py:120] The `--generator` CLI path is not passed through `clone_relative_file`; my probe ran an absolute `/tmp/...` generator through it. The loader gates every testlist entry, so this is debug-only surface. - Apply the same rule or state in the help text that the CLI is unvalidated.

[info][dv/auto_dv/flow/gen_flow_const.py:222] Comment "(TB Infra export addendum v4, runtime ruling 2026-09-03)" carries a dated ruling reference; the repo's comment rule is intent-only. Kept as PASS under the rubric's bias, but the date belongs in the evidence file, not the constant's comment.

Final verdict: APPROVE-WITH-CHANGES
