# Cross-model review - committed diff 1fc4ffa2..9fdef648

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 96608f1a-ede9-42db-8e56-e8c04cf22ac2; sandbox: bubblewrap, working directory = detached read-only checkout of commit 9fdef648bba5d47bfceeb8bd92621e3cdb8923f8 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 9fdef648bba5d47bfceeb8bd92621e3cdb8923f8
**Date:** 2026-09-03
**Target:** committed diff 1fc4ffa2..9fdef648 (echo at raw line 1)

---

TARGET: 1fc4ffa22a4412a4065412f028c04c2ea93c8318..9fdef648bba5d47bfceeb8bd92621e3cdb8923f8

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of 9fdef64; no simulation run. Verified from the repository: the 9-file diff, rtl/ibex_id_stage.sv, rtl/ibex_compressed_decoder.sv, rtl/ibex_top.sv, dv/auto_dv/isa/gen_isa_shim.cc, dv/auto_dv/docs/gen_trace_tp_bin.csv, dv/auto_dv/fcov_expectations/*.yaml, dv/auto_dv/reviews/2026-09-03-claude-diff-754bf42c-158f5bee.md (d9f66c6). Ran: gen_trace_check.py (PASS), gen_round_credit.py --self-test (ok). Not reproduced by me: the credit/promotion/covergroup-set byte-for-byte regeneration (the orchestrator's hash statement is taken as reported), gen_test_lib self-test (my invocation lacked the repo PYTHONPATH), the 1371 declared-bin recount.

Judgments requested

(1) popret_ra_fwd retirement is genuine, not a drop to satisfy the CSV. The Zcmp pop expansion is loads -> addi sp (CmPopIncrSp) -> optional li a0,0 -> ret (rtl/ibex_compressed_decoder.sv:686-770); instr_executing is gated by ~outstanding_memory_access (rtl/ibex_id_stage.sv:1059-1062), so the addi cannot execute until the last load's response has been written back, and load data is never forwarded from WB (rtl/ibex_id_stage.sv:1114-1118, stall_ld_hz). By the time the ret is in ID, ra is in the register file with the addi in WB; a "ra forwarded from WB" path cannot occur. popret_ra_deferred (the addi starting deferred) is the reachable replacement and has CSV rows (TP-CMP-049, TP-CMP-071). The plan's 12 cp_hazard bins equal the 12 distinct cp_hazard bins in gen_trace_tp_bin.csv. The bin was already an ignore_bin before this diff, so no coverage intent was lost.

(2) The ignore_bins claim holds. CG-ISA-005 zcb_alu, CG-BTALU-001 cp_branch_inc.inc0 and CG-BTALU-003 cp_redirect_count.two have no rows in gen_trace_tp_bin.csv (the zcb_alu_110/_111 hits are CG-CMP-004 cp_class bins, a different group). The other ignore_bins in the ISA-area section (nt_dit1_inc0, wb_inc1, jalr_odd_b0 family, u_sequential) are cross bins and are counted on the separate cross line, so "3 coverpoint ignore_bins" is internally consistent. gen_trace_check PASS at HEAD.

(3) CG-RST-001 expressions. cp_first_event "from RVFI" names real observation points: rvfi_valid, rvfi_intr, rvfi_ext_nmi, rvfi_ext_debug_mode are ibex_top outputs (rtl/ibex_top.sv:144, :170, :173). cp_reset_kind "from the TB's reset count" names a point that does not exist yet: no reset counter exists under dv/auto_dv/env or dv/auto_dv/tb; it is exactly the WP-11 deliverable, and the coverpoint line says so. Acceptable as written.

(4) Mid-run reset bins as owned bins of an unbuilt group: the WP-11 row follows the WP-10 pattern (NOT BUILT, dependents named, no ignore_bins). The fact "declared by no promoted manifest" is true today (no manifest mentions mid_run). The ownership reasoning is incomplete: see finding 1.

(5) CM123 caveat wording matches the d9f66c6 artifact: verdict APPROVE-WITH-CHANGES (line 50); M-1 at gen_isa_shim.cc:238 (high_write inferred from (val ^ cur) >> 32, so a minstreth write leaving the high word unchanged classifies as a low write); M-2 at :240 (gap rule assumes the write-cycle retirement was counted; cites rtl/ibex_id_stage.sv:1213-1216, verified: minstret_write excluded from instr_perf_count_id_o). The code at 158f5be (line 238-244) matches the quoted defect. The twelve as-built statements (Section 0a row plus eleven Pass criteria) all carry the caveat and the d9f66c6 citation (12 occurrences each). The three minors in the artifact are not mentioned; "two majors owed" is accurate.

(6) Rows against artifacts: Slice-A-1/2/3 and the caveat row are present in gen_critic_response_plan_set_v1.md; credit report, summary and promotion table relabelled v3f-on-1fc4ffa with the testlist sha 87ed798c77d2 unchanged and the plan sha updated; the whole diff is ASCII (no non-ASCII added bytes).

Rubrics (Zone A set): ai-slop-comments PASS (docs-only diff; the "(retired: ...)" note follows the plan's existing retired-line convention); rtl-purity PASS (no rtl/ change); magic-numbers PASS (no filtered file changed); forces-and-hier-access PASS (no sv/py change); assertion-integrity PASS (no assertion or manifest touched; the covergroup-set CSV rows are unchanged except gen_fcov_plan.md line anchors shifted by one).

Findings

[medium][dv/auto_dv/docs/gen_fcov_plan.md:5602] The cp_reset_kind note (and the WP-11 row at gen_test_plan.md:435, and Slice-A-3) says the mid_run bins "belong to gen_rst_midrun_reset ... a group with no test, so no promoted manifest declares them". gen_trace_tp_bin.csv:23579 also traces CG-RST-001.cp_reset_kind.mid_run to TP-RVFI-036, whose Test group is gen_rst_boot (a promoted group with manifest gen_test_rst_boot.fcov.yaml) and whose Stimulus reads "power-on and mid-run resets" with a Fire-check of ">= 2 reset windows". The bin is undeclared today only because TP-RVFI-036 is marked not_built for an unrelated reason (record export) in that manifest. When TP-RVFI-036 is built, the promoted manifest will declare mid_run and fail without WP-11, and the plan text gives no warning. - Name TP-RVFI-036 / gen_rst_boot as a WP-11 dependent in the WP-11 row, the cp_reset_kind note and Slice-A-3, or move the mid_run bin and the mid-run stimulus out of TP-RVFI-036 into the gen_rst_midrun_reset items.

[low][dv/auto_dv/docs/gen_test_plan.md:435] WP-11 and the cp_reset_kind note attribute the mid_run bins to "TP-RST-017, TP-RST-018, TP-RST-019", but only TP-RST-017 lists CG-RST-001 bins (TP-RST-018 and TP-RST-019 trace no CG-RST-001 bin). - Cite TP-RST-017 as the bin owner and the other two as the group's other items.

[low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:587] The caveat row states "the Test Writer's six gen_pmc_ctrl programs all contain the M-1 case"; no gen_pmc_ctrl test, manifest or program is committed at HEAD (dv/auto_dv/tests and dv/auto_dv/fcov_expectations carry none), so this is unverifiable from the repository. - Mark it as relayed by the Test Writer, or cite the handed file set and its hash.

[low][dv/auto_dv/evidence/gen_round0_covergroup_set.csv:22] The commit message says the covergroup set CSV "changed with the retired bin", but the CG-CMP-009 row is byte-identical (cp_hazard (12) before and after, since the CSV already carried 12); the only CSV change is the gen_fcov_plan.md line anchors shifting by one from the inserted retired note. - Record the change as an anchor shift, not a bin change, to keep the regeneration history accurate.

Final verdict: APPROVE-WITH-CHANGES
