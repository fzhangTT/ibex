# Cross-model review - committed diff eccc461c..24f3dc0e

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1; effort: high; fresh session 65752c30-1824-49d3-956d-ee0354c1b2d6 (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** committed diff eccc461c..24f3dc0e (echo at raw line 1)

---

TARGET: eccc461ce6eab46e509257b9928b0bbe58fcc5be..24f3dc0edaeac810e43018ae0d8ee65652e74472

Reviewer: Claude (model ID claude-fable-5-1, Claude Code CLI), fresh session, read-only, fallback reviewer per the recorded ruling (codex spend cap). Scope: the single commit 24f3dc0 (8 files, +422/-68, all under `dv/auto_dv/**` with the `gen_` prefix; no `rtl/` or `ci/` file touched). Verified against the committed tree (self-tests run from a `git archive` of 24f3dc0 in a scratch dir), the out root `/proj_soc/user_dev/fzhang/ibex_dv_out`, LSF history (`bhist -l`), and one re-run of the per-test `urg -tests` query into a scratch dir. Host clock is EDT; mtimes below are UTC.

## Owner focus items, verified

**1. Per test and pre-merge.** `gen_regress.main` joins every `run_one` future (LSF jobs are synchronous) before `post_fcov_checks`, which precedes both merges. `check_test` calls the checker with `--vdb <run vdb> --cm-name test_<name>_<seed>`; the retained `test_selection.txt` holds exactly `<out root>/regress_t045_fcov_wiring2/cov_unmeasured/gen_smoke/test_gen_smoke_330815564` and `urgReport/tests.txt` says `Total tests in report: 1` with that identifier. Caveat in finding 3.

**2. Declared-but-unhit FAILS as a collected mechanism.** `apply_fcov_check` turns PASS/XFAIL into FAIL with reason `fcov expectation unmet: ...` whenever `status != "PASS"`; `post_fcov_checks` rewrites `result.yaml` with verdict, reason and `fcov_check`. `gen_fcov.py --self-test` at 24f3dc0: PASS, 6 cases, and the UNHIT/absent-bin cases drive the real `ci/check_fcov_expectations.py` via `--report-dir` (the argv in each case's log names the real script). `check_fcov_expectations.py --self-test`: PASS.

**3. Protocol error is never a pass.** Exit 1 maps to `PROTOCOL_ERROR`, any unmapped code to `UNKNOWN`, both non-PASS, so both FAIL with `fcov expectation unverifiable`. A schema violation FAILs before the checker runs. The retained run confirms it: `result.yaml` verdict FAIL, `fcov_check.status: PROTOCOL_ERROR`, `exit_code: 1`.

**4. Runs without a manifest.** `summary.runs_without_fcov_manifest` counts them (t045 manifests: 0; t038: 2). `fcov_policy_failures` FAILs a PASS run on the header tiers plus, once `covergroups_exist`, on `C.TIERS = ("smoke","targeted","full")`; `CHECK_TIER` is not in `TIERS`, so the "check exempt" claim holds. `covergroups_exist` is false today (`group: n/a` in both merge totals), so the policy has still never fired.

**5. Manifest schema.** `validate_manifest` enforces stem == `test` == testlist entry, owner in `C.OWNER_ROLES`, non-empty unique bins matching `^gen_\w+\.<cp>\.\S+$`, one non-empty `anti_vacuity` note per bin, no note for an undeclared bin. Notes are copied verbatim into `result.yaml` (`anti_vacuity:` present in the retained record) and never read otherwise. Loose spots in finding 7.

**6. Evidence vs retained artifacts.** LSF 10931279 (`bhist`): submitted 06:37:22 UTC on soc-c-22, done 06:37:32, matches `result.yaml` (`started 06:37:22Z`, `finished 06:37:34Z`, host soc-c-22, job 10931279) and run-dir mtimes (06:37:22 to 06:37:40). First pass 10931237 (06:34:47 to 06:34:57, soc-c-13) has its own retained dir `regress_t045_fcov_wiring` with no `fcovexp_*` (work dir went to `/tmp`, as stated). Dashboard rows `1/0/1`, `0` runs without manifest, both tags. The evidence's cause ("no grpinfo.txt, no covergroup") holds: I re-ran the identical `urg -tests` query into a scratch dir, rc 0, seven `UCAPI-CSM` warnings, and no `grpinfo.txt` in the report. Discrepancies in findings 1 and 4.

**7. No temporary path outside the run dir.** `run_checker` sets `TMPDIR` to the run dir and the retained `fcovexp_03ur6ex8/` sits beside `result.yaml`. No flow file globs or reads `/tmp`; the only `/tmp` users are the two `--self-test` scratch dirs (fabricated data, written not read) and the checker's `mkdtemp`, which honours `TMPDIR`. The F-001 exposure is recorded in the intervention log (already committed before this range).

**8. Previous review minors (2026-09-03-claude-diff-8c22fe5e-edacfb10.md) at 24f3dc0.**
- `gen_run.py` unmeasured vdb default: applied (lines 184-195 refuse `build.vdb` for unmeasured runs; done before this range).
- Stale doc text (`[--no-diag-noconst]`, `-ucli` sentence, `gen_run.py` die text): applied.
- LSF accounting standard: applied for T-045 (both jobs named, first pass in its own retained dir).
- `fcov_policy_failures` not rewriting `result.yaml`: open (finding 6).
- `gen_build.py` `--rtl-root` leftover check: open at 24f3dc0 (addressed in 6006bfb, outside this range).
- P6 / fcov-policy self-tests and a retained refusal run: open at 24f3dc0 (same later commit).
- LOG-008 unmeasured-source wording, `render_fields`, `summarize(testlist)` unused, `vcs+finish` allow-list: not touched in this range.

## Findings

[minor][dv/auto_dv/evidence/gen_t045_fcov_wiring.md:3] The stated window "06:33 to 06:36 UTC" excludes the cited pass: job 10931279 ran 06:37:22 to 06:37:32 and the manifest was written 06:37:40; only the uncited first pass (06:34 to 06:35) falls inside. - State "06:34 to 06:38 UTC" and give the cited job's submit/finish times.

[minor][dv/auto_dv/evidence/gen_t045_fcov_wiring.md:15] The proof's inputs are a gitignored working manifest (`dv/auto_dv/work/runtime/selftest/gen_smoke.fcov.yaml`) and a temp testlist whose path is recorded nowhere in `manifest.yaml`; the declared bin survives only as an `anti_vacuity` key in `result.yaml`. - Copy the manifest and testlist into the regression outdir (or record the testlist path in `manifest.yaml`) so the run is reproducible from retained artifacts.

[minor][dv/auto_dv/evidence/gen_t045_fcov_wiring.md:15] "the isolation step works" is the author's reading of `tests.txt`; the checker's own isolation assertion (Total tests == 1 and exact identifier, `check_fcov_expectations.py:110-117`) never executed because the missing-`grpinfo.txt` RuntimeError fires first. - Say in the evidence that the checker's isolation check is still unexercised, and list it under Section 2.

[minor][dv/auto_dv/evidence/gen_t045_fcov_wiring.md:15] The retained `fcov_check.log` cannot support the stated cause: its error tail is a `UCAPI-CSM` "mismatch" warning followed by "Report written", which reads as a urg failure; only my re-run (rc 0, no `grpinfo.txt`) confirms the "no covergroup" explanation. - Quote the `urgReport/` listing (no `grpinfo.txt`) in the evidence; have the checker's error name which condition failed (rc vs missing file) when it is next touched.

[minor][dv/auto_dv/flow/gen_dashboard.py:170] A run with a manifest that was never checked (FAIL/TIMEOUT before the check, or no vdb) has no `fcov_check` and is labelled "no manifest", the same label as a run that truly lacks one. - Distinguish "not checked (verdict X)" from "no manifest" using the testlist's `fcov_expectation_file`.

[minor][dv/auto_dv/flow/gen_regress.py:198] `fcov_policy_failures` flips the in-memory verdict but still does not rewrite the run's `result.yaml` (previous review's minor, unchanged); the manifest and the per-run record will disagree once the policy fires. - Dump the updated record as `post_fcov_checks` does.

[info][dv/auto_dv/flow/gen_fcov.py:36] `BIN_RE`'s third group is `\S+`, so `gen_x_cg.cp.a.b.c` passes although Section 7c promises "three dot-separated parts"; and a YAML-quoted bin is unquoted by `validate_manifest` but kept quoted by the checker's raw-line parser, giving a spurious `MISSING-FROM-REPORT` (fail-closed, but misleading). - Tighten the third group to `[^.\s]+` and reject quoted bin lines in `validate_manifest`.

[info][dv/auto_dv/flow/gen_fcov.py:112] `declared`/`hit` are counted from parsed stdout lines, not from the manifest, so a PROTOCOL_ERROR shows "0/0 bins" on the dashboard although one bin was declared. - Take `declared` from the validated manifest data.

[info][dv/auto_dv/flow/gen_fcov.py:83] The allowed-key set admits `notes`, which Section 7c does not document. - Document it or drop it.

[info][dv/auto_dv/flow/gen_flow_const.py:109] `COV_GLITCH_FILTER`/`COV_GLITCH_FLAGS` are unrelated to T-045 and absent from the commit message (no-op while False). - Mention it in the commit or move it to the LOG-008 follow-up commit.

## Rubric results

- ai-slop-comments: `{"status": "PASS"}`. Added comments state intent (TMPDIR fence reason, single-writer rationale, glitch-filter gating); no history narration in code comments.
- rtl-purity: `{"status": "PASS"}` (no `rtl/` files in the diff).
- magic-numbers: `{"status": "PASS"}`. New literals (`-cm_glitch 0`, exit-code map, tier set) live in `gen_flow_const.py`; the `gen_tb_top.u_env.u_cov::` string is a fabricated self-test fixture.
- forces-and-hier-access: `{"status": "PASS"}`. No SV or cocotb deposits.
- assertion-integrity: `{"status": "PASS"}`. `fcov_check` is replaced by the stricter `apply_fcov_check` (XFAIL covered, schema validation, any non-PASS status fails); `fcov_policy_failures` moved later and widened; nothing disabled or weakened.

Summary: the wiring does what the duty requires. The check is per test on the single `-cm_name` identifier and runs after all writers and before both merges; an unhit or unverifiable expectation FAILs the run through `result.yaml` and the manifest; the self-test drives the real checker; the retained run and LSF history agree with each other, and the per-test urg work dir now lives in the run directory. The evidence file has a wrong time window, leans on gitignored inputs, and overstates what the checker itself proved about isolation; the dashboard label and the `result.yaml` rewrite for policy failures remain. No blocker.

Final verdict: APPROVE-WITH-CHANGES
