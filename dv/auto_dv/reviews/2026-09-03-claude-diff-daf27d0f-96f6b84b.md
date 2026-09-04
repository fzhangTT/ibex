# Cross-model review - committed diff daf27d0f..96f6b84b

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 6564fce6-6612-4421-b2ab-f693ea97ba01; sandbox: bubblewrap, working directory = detached read-only checkout of commit 96f6b84b5b31d5aaf5d3d340804871ac05191c0c (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 96f6b84b5b31d5aaf5d3d340804871ac05191c0c
**Date:** 2026-09-03
**Target:** committed diff daf27d0f..96f6b84b (echo at raw line 3)

---

All checks are reproduced. Writing the review now.

TARGET: daf27d0f01350b3b5afc053e2a346974c87472e6..96f6b84b5b31d5aaf5d3d340804871ac05191c0c

Reviewer: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of 96f6b84. Scope: the single commit 96f6b84, seven files, 68 insertions / 12 deletions.

**What I reproduced (from the checkout, self-tests with GEN_DV_SELFTEST_TMP relocated because the tree is read-only):**
- All three .py compile; all seven files ASCII; every new name carries the gen_ prefix (PLUSARG_CHK_ALL follows the PLUSARG_* constant convention).
- gen_flow_const --check PASS: PLUSARG_CHK_ALL = "gen_chk_all" is in SV_SHARED_CONSTANTS and gen_tb_pkg.sv:92 declares the same string.
- gen_flow_util --self-test rc 0, ok=100 (the twelve LOG-077 cases pass, including the four new master-enable cases); gen_run --self-test rc 0, ok=21 (the operator-restores and the master-off cases pass); the loader dumps 85 entries; --check-red-signatures PASS.
- Manifest: all seven evidence rows verify by md5 and byte count; gen_log077_red2.log is 1239 bytes, md5 cc6584b37c1fe68356a5aeefeeb98ec9.
- (1) Precedence against the SV. gen_checkers_pkg.sv:19 `cfg.chk_all ? val : (set && val)`; gen_env_cfg_knobs.svh:166/365 give chk_all default 1, set by `+gen_chk_all=%d`; :210/387 give chk_alert_minor default 1, set by `=%d`. checker_row_on: a row named by a plusarg returns its value (matches both branches when set=1: `chk_all ? val : val`); an unnamed row returns master AND row default (matches `chk_all ? 1 : 0` with the table default 1). Probed directly: master default + row unmentioned runs; master =0 + row unmentioned refuses; master =0 + row =1 runs (isolation mode); master =1 + row =0 refuses; master =0 with rate none runs (not triggered); fabricated master default 0 refuses. The master default is read from the rendered table (gen_knobs.py:88 `chk_all` default 1) through knob_default_by_plusarg, the same reader the trigger uses.
- (2) The red is discriminating. Before the fix the old code read the row alone, so exactly the three cases that need the master (util: master off + row unmentioned; fabricated master default 0; gen_run: operator master off) print BAD, while the isolation-mode case and the row-set-off case pass under both old and new code, as the log shows. The green then also rules out a naive `master AND row` implementation because the isolation-mode case (master off, row set on, expect run) is in the set.
- (3) Rows against the artifact 2026-09-03-claude-diff-b5167470-cd9638a5.md: it has 1 Medium, 2 Low, 3 Info, verdict APPROVE-WITH-CHANGES; CM152 has six rows in the same order with matching content. L-1: the reduced expression is the one the reviewer proposed. L-2: the loader message now reads "is measured and carries +rate=... while +row reads off (row ..., +gen_chk_all ...); LOG-077 ..." (one clause). I-1: the gen_run.py:332 comment names the MEASURED_KNOB_CONDITIONS rows. I-2: the case at gen_run.py:257 has entry row =0, operator row =1, measured, expect run. I-3 recorded as left as is with the reason; gen_env_cfg_knobs.svh:444 does refuse the enum at start.
- Rubrics: rtl-purity n/a (no rtl/ lines); forces/hier-access PASS; magic-numbers PASS (the new plusarg name is a constant bound to the SV by the const check); assertion-integrity PASS (the change only refuses more measured runs, no checker disabled); ai-slop-comments PASS (comments are intent-only; the constant's comment cites the SV anchor with a gloss). Review ids appear only inside self-test label strings (gen_flow_util.py:764, gen_run.py:257-258), not in comments, following the LOG-077 label precedent.
- gen_runtime_api.md Section 2 carries the precedence sentence and it matches the code.

**Findings**

[Low][dv/auto_dv/flow/gen_flow_util.py:1211] The `on` lambda and `row_set` treat a bare `+gen_chk_alert_minor` as "set to 1", but the SV parses `=%d` only, so a bare form leaves `chk_alert_minor_set = 0`. With `+gen_chk_all=0 +gen_chk_alert_minor` (bare) the gate reads the row on and runs (verified: checker_row_on returns True, refusal None) while the sim reads `chk_all=0, set=0` and the row is off. The earlier review's "bare = 1 is consistent with the sim" held only while the master was not judged; with the master in the judgment the bare form matters in isolation mode. No testlist entry uses the bare form today. Recommendation: count a row as set only when the plusarg carries `=`, or refuse a bare checker plusarg in the loader; add the case.

[Low][dv/auto_dv/flow/gen_flow_util.py:1211] `+gen_chk_all=00` reads on in the flow (`strip() not in ("0", "")`) but the SV `%d` parse yields 0, so the master is off in the sim: `+gen_knob_icache_ecc_err_rate=frequent +gen_chk_all=00` passes the gate (verified) with the alert_minor row off. The gen_run.py:197 docstring frames "=00 as on" as stricter than the `%d` parse, which is true for a must-be-off knob but is the lenient direction for a must-be-on row. Recommendation: normalize the value as the SV does (`int(v, 10) != 0`, non-numeric falls to the default) in `on`, or state the gap in the docstring.

[Info][dv/auto_dv/flow/gen_flow_util.py:1204] `checker_row_on` calls `effective_knob_value` for the row and then `any(plusarg_name(pa) == row ...)` separately, scanning the plusargs twice for the same name; harmless, but a single helper returning (present, value) would make the "set" semantics one place to fix for the two findings above.

[Info][dv/auto_dv/evidence/gen_tdd_logs/flow/gen_log077_red2.log:8] Two ok lines in the retained red are clipped mid-message ("LOG-077 (Q-0"), the same clipping the self-test printer applies to the earlier LOG-077 red; the BAD lines that carry the discrimination are intact, so no action needed.

Final verdict: APPROVE-WITH-CHANGES
