# Cross-model review - committed diff e4cbdd8b..56e37d75

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 87ec8d4d-86be-41c5-ad2e-27dff1c933a5; sandbox: bubblewrap, working directory = detached read-only checkout of commit 56e37d75a8b990336a4655b1cee7062c56e8cec3 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 56e37d75a8b990336a4655b1cee7062c56e8cec3
**Date:** 2026-09-03
**Target:** committed diff e4cbdd8b..56e37d75 (echo at raw line 1)

---

TARGET: e4cbdd8bd2d94545c599104895aa55507c667925..56e37d75a8b990336a4655b1cee7062c56e8cec3

**Scope reviewed.** One commit (56e37d7), 13 files: `dv/auto_dv/tests/gen_test_csr_reset.py` (schedulable tuple and docstring), `dv/auto_dv/evidence/gen_tdd_batch1.md` (new Section 13), `dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_manifest.md` (prose family entry and ten rows), and ten retained logs. No `rtl/`, `ci/`, SV, or testlist changes.

**What I verified against the repository (not the author's narrative):**

- The only code change is removing `knob_debug_req_regime` from `CsrReset.schedulable` (gen_test_csr_reset.py:138). The template draws layer 2/3 only from `self.varied`, which is a subset of `schedulable` (gen_test_template.py:98-100, 219-220), so the knob now stays at its rendered default, which is `none` (gen_knobs.py:78). The docstring's claim about the command-line default is correct.
- The plan's Knobs lines for the six hosted items name `knob:debug_req_regime` only on TP-CSR-108 (gen_test_plan.md:6241); the docstring statement that the items' Knobs lines name it is accurate, and TP-CSR-108's debug-mode reads were already a stated not-built clause (gen_test_csr_reset.py:28-29).
- `gen_csr_reset_prog.py` contains no debug-ROM or DM-window code; the memory model maps the DM window (gen_mem_pkg.sv:44) with no program content. The DM addresses quoted in the TDD match the config banner in the round-0 evidence.
- All ten retained logs match the manifest rows byte-for-byte (sizes and md5s). The as-is excerpt reproduces the round-0 runaway with `debug_req_regime=storm` drawn at c0; the `+gen_knob_debug_req_regime=none` control passes with the same remaining draw. The three `t206fix_*` runs show `GEN_TEST_KNOBS` without the debug knob, `fire_schedule_applied ok=True`, `GEN_TEST_BINS n=81`, `GEN_TEST_PASS`, `UVM_ERROR : 0`, and `[GEN_DBG] requests=0`. The red run fails on exactly `fire_tp_csr_106` (mcause re-target) and no other item. Every number in the TDD Section 13 table (reports, retired, EOT cycle, schedule reached/applied, knob draws, md5) matches the logs.
- Re-rendering the manifest read-only via `gen_fcov_manifest.py --test-module` produces output byte-identical to the committed `gen_test_csr_reset.fcov.yaml`; the "unchanged by re-render" claim holds (the renderer has no knob dependence).
- Every committed test overrides `schedulable`; none other names `knob_debug_req_regime`, so the lesson's exposure is limited to this test at HEAD.

**Rubric results.** ai-slop-comments: PASS (one nit below). rtl-purity: PASS (no `rtl/` lines). magic-numbers: PASS (no new literals; knob names are the knob table's IDs). forces-and-hier-access: PASS (no added drives). assertion-integrity: PASS (no checker removed or weakened; the declared-bins manifest is unchanged; the stimulus-range reduction is justified in the docstring and the always-on debug checker remains).

**Findings:**

[Minor][dv/auto_dv/evidence/gen_tdd_batch1.md:673] The closing paragraph names only two debug-mode bins (gen_csr_debug_csr_cg.cp_dbg.dbg, cr_csr_dbg_trap.dcsr_dbg_ok) as unreachable without a debug entry, but the committed manifest and the `GEN_TEST_BINS` line also declare gen_csr_reset_read_cg.cp_dbg.dbg, cr_dbg_reset.{dcsr,dpc,dscratch0,dscratch1}_dbg, cp_csr.{dcsr,dpc,dscratch0,dscratch1}, gen_csr_debug_csr_cg.cp_csr.dcsr and cp_trap.ok, all of which need a debug entry or a debug-mode read the program never performs. Pre-existing before this diff, and honest-by-failing once fcov is measured, but the record undercounts. - Correct the sentence to the full set and route the follow-up (template `bins_not_hit` with the reason, which the renderer already honors at gen_fcov_manifest.py:257-302, or a debug-ROM program) before the test is measured.

[Minor][dv/auto_dv/tests/gen_test_csr_reset.py:57-58] The docstring says the items' debug-mode clauses are "the not-built clauses above", which is true for TP-CSR-108, but it does not say that the test's declared manifest still carries debug-mode bins the test now structurally cannot hit; `not_built = {}` and `bins_not_hit` is unset. - Add one sentence stating the debug-mode bins remain declared and unhittable pending the bins_not_hit / debug-ROM decision, so the docstring and manifest agree.

[Info][dv/auto_dv/tests/gen_test_csr_reset.py:57] "(round-0 seed 1028791296, T-206)" is a history breadcrumb inside an intent-only docstring; the why-sentence stands without it and the seed is recorded in the TDD. Low confidence, nit only.

Final verdict: APPROVE-WITH-CHANGES
