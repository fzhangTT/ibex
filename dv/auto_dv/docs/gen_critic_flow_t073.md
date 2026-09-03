# Critic re-review: flow gap-sweep remediation (T-073) at commit 42e6f28

Artifacts under review (committed at 42e6f28 = HEAD at review time; sha256 first 16 hex):
- dv/auto_dv/evidence/gen_critic_response_flow.md (T-073 table)                845b073b884083ee
- dv/auto_dv/flow/gen_flow_const.py, gen_flow_util.py, gen_verdict.py, gen_fcov.py, gen_build.py, gen_run.py,
  gen_regress.py, gen_stim.py; dv/auto_dv/docs/gen_runtime_api.md Sections 2, 6a, 7b (all committed, cited by line)
- Answered artifact: dv/auto_dv/reviews/2026-09-03-claude-diff-1908ddd7-280b4e96.md (APPROVE-WITH-CHANGES; flow findings:
  CRASH_RE medium, selftest_tmp triplication low, placeholder rendering low, gen_stim fallback low)
Date: 2026-09-03 (UTC). Role: Critic (re-review of a remediation against the committed code, not the table's claims).

CRITIC VERDICT: APPROVE

Each of the four rows is verified in the code, the self-tests pass when I run them, the two red paths the table
describes as ad hoc were reproduced by me, and every claimed run maps to a retained artifact with consistent stamps.
No finding blocks; four notes follow.

## 1. Verification per row

(a) CRASH_RE and the job script's timeout-wrapped kill reports.
- One constant: gen_flow_const.py:177 `JOB_TIMEOUT_CMD = "timeout"`; the job script emits it as the first word of the
  simv line (gen_run.py:123) and the regex's trailing alternation admits it (gen_flow_const.py:279-281:
  `re.escape(JOB_TIMEOUT_CMD) + r"( |$)|\S*simv\S*|bash|$"`), so the shell's report `<pid> Killed  timeout -k 20 900
  .../vcs_simv ...` matches. A future change of the job line's first word stays coupled through the constant.
- Two real-shaped reports pinned verbatim (gen_verdict.py:177-180) and run as FAIL cases on a clean log with rc 0
  (:198-199); the six signal words checked against the same shape (:221-223); the ISS line "Illegal instruction (hart 0)
  at PC" pinned clean (:225-227) and the real tb-infra-002 log line kept as a PASS case (:200-201).
- My run of `python3 dv/auto_dv/flow/gen_verdict.py --self-test`: 38 "ok", 0 "BAD", SELF-TEST: PASS (the table says
  38 cases). The two real-shaped cases report FAIL on rc 0 as stated.
- Artifact rule: the capture is retained at dv/auto_dv/work/runtime/selftest_tmp/crash_shape/ (08:35Z local 04:35):
  run_cmd_SEGV.sh / run_cmd_KILL.sh in the job-script form, stand-in vcs_simv (`kill -SEGV $$`), exit codes 139 and
  137, run_SEGV.err / run_KILL.err whose first lines are byte-identical to REAL_SHAPE_SEGV / REAL_SHAPE_KILL (checked).

(b) One SELFTEST_TMP and one placeholder set.
- gen_flow_const.py:68 `SELFTEST_TMP` and :71-74 the single `selftest_tmp()`; the only definition in the flow (grep);
  callers gen_flow_util.py:231, gen_fcov.py:193, gen_verdict.py:230 use `C.selftest_tmp()`; the three pasted copies are
  gone (diff).
- gen_build.py:177-185 `build_fields()` ({outdir}; {mirror} = the mirror root, or the clone root under --local-cocotb);
  :188-197 `render_build_field()` replaces tokens and dies naming the leftover and the known set; used for
  extra_ldflags (:118-119), pre_build (:204) and runtime_lib_dirs (:218-219). gen_run.py:68 no longer filters a
  MIRROR_UNSET sentinel. Reproduced: `{mirror}` without a mirror root and `{outdir}/{zzz}` both die with the known set
  named; `{outdir}` and `{mirror}` with a root render.
- gen_regress.py:358-363 syncs with `--sync --spike`, records `mirror_sync.spike: true`, dies on failure; t073_local2's
  manifest shows mirror_sync rc 0, 1.3 s, spike true (the table says 1.3 s).
- gen_runtime_api.md 6a (:307-330) states the one placeholder set, the loud failure and the sync rule; 7b (:385-389)
  names `--sync --spike`.

(c) gen_stim fallback removed; ModuleNotFoundError scoped.
- gen_stim.py:70-87: the helper module name is the constant gen_flow_const.py:215 `IMAGE_HELPER_MODULE`; on
  ModuleNotFoundError the code dies by name only when `e.name` is the helper or one of its parent packages and re-raises
  otherwise; the two-plusarg fallback, `image_plusarg_names()` and the SV_PLUSARG_MEM_IMAGE* constants are gone (diff);
  `build_program` is unchanged. Reproduced: a missing parent package dies by name; the real helper imports (the call then
  fails on my fake image path, proving the import succeeded).
- t073_local2 result.yaml (both runs): `image_plusargs_source: dv.auto_dv.gen_tb.gen_image GenImage.plusargs()`.

(d) -cm_* dropped on no-coverage builds.
- gen_build.py:141-149 (landed in 0d06da4, the commit before 42e6f28): without --coverage every extra_vcs_args token that
  starts with `-cm` and the token following it are removed and recorded; manifest key `dropped_cm_args_no_coverage`
  (:329). Both retained build manifests (t073_local2/build/gen_tb, 08:41:05Z; t_wt_precheck_0827, 08:27:57Z) show
  coverage false, `dropped_cm_args_no_coverage: ['-cm_glitch', '0']`, a compile command without `-cm`, and compile logs
  with 0 VCM-INSOPTMIS lines (warning set: 32 SIOB, 1 LCA_FEATURES_ENABLED). gen_runtime_api.md Section 2 (:135-143)
  states the crash-report rule as implemented.

## 2. Claimed runs against retained artifacts

| Claim | Artifact | Stamp | Content | Result |
|---|---|---|---|---|
| real-shaped capture, bash 4.4.20, 08:35Z | work/runtime/selftest_tmp/crash_shape/ | 04:35:10-14 local | exit codes 139/137; .err lines equal the pinned strings | consistent |
| t073_local: first pass NOT_RUN x2 (build_program cut), disclosed | work/runtime/out/t073_local/manifest.yaml, runs/*/driver.log | 08:39:47Z | not_run 2; driver.log `AttributeError: module 'gen_stim' has no attribute 'build_program'` | consistent, honest |
| t073_local2 PASS x2 | work/runtime/out/t073_local2/ | 08:41:10Z | gen_boot_zc and gen_ut_lockstep PASS; mirror_sync spike 1.3 s; image_plusargs_source as claimed | consistent |
| t_wt_precheck_0827 warning set has no VCM-INSOPTMIS | work/runtime/out/t_wt_precheck_0827/ | 08:27:57Z | 0 matches; dropped list recorded | consistent |
| 38 self-test cases PASS | my own run | now | 38 ok, 0 BAD | consistent |

gen_regress.py:453 counts not_run with fail and timeout, so a driver crash like t073_local can never yield a green
regression.

## 3. Notes (none blocking)

N-1 The -cm_* drop is in 0d06da4, one commit before 42e6f28; the response text says "included in the same landing". Cite
the commit when the table is next edited.
N-2 The drop rule removes the token after any `-cm*` token (gen_build.py:145); that is right for `-cm_glitch 0` and
`-cm_hier <file>` and would also remove a value that follows a bare `-cm`, which is intended since `-cm` without
coverage is meaningless. Stated for the record.
N-3 The table's proof for the two placeholder red paths ("both die") was an ad hoc check with no retained log; I
reproduced both, so the claim stands, but a self-test case in gen_build.py or gen_flow_util.py would retain it.
N-4 The real-shaped reports live under work/runtime/selftest_tmp (gitignored); the committed copy is the verbatim pin in
gen_verdict.py:179-180 with the capture method in its comment, which is the accepted pattern for tooling evidence.

## 4. Method and fence record
Read the diff of 42e6f28 for the nine files, the committed code at the cited lines, the response table and the
gap-sweep artifact; ran the four flow self-tests and the constants check under ci/env.sh; reproduced the two placeholder
red paths and the gen_stim die-by-name with throwaway Python calls; audited the retained captures and run trees. No LSF
command; no fence event.
