# Cross-model review - committed diff b151bdfb..e83b2cce

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session a0f95fed-5bec-4b17-bdb1-aeb8289df9b6; sandbox: bubblewrap, working directory = detached read-only checkout of commit e83b2ccecd7a551d282689fa02c21e5142c9670e (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit e83b2ccecd7a551d282689fa02c21e5142c9670e
**Date:** 2026-09-03
**Target:** committed diff b151bdfb..e83b2cce (echo at raw line 1)

---

TARGET: b151bdfb4882b5315520828f158127fdd501a422..e83b2ccecd7a551d282689fa02c21e5142c9670e

Reviewer: Claude (claude-fable-5-1), fresh session, read-only detached checkout of e83b2cc. Scope: the single commit e83b2cc (11 files, 106+/90-). Verified against the repository, not against the commit message.

**Reproduction (owner point 5).** From a scratch `git archive` of e83b2cc with PYTHONPATH and GEN_TEST_STAGED_ENTRIES unset and the output files deleted first, the three generators re-create byte-identical files: `gen_covergroup_set.py --plan-sha v2u-on-0c189eb` (md + csv), `gen_promotion_table.py --plan-sha v2u-on-0c189eb`, and the credit invocation printed in the header (csv, md, summary). An independent parse of the 15 manifests the committed testlist names gives 3779 distinct bins in 48 covergroups from 3839 declarations, matching the header. The promotion table's recorded inputs (gen_test_plan.md ee59157bfbd0, gen_testlist.yaml 1d72f450cda1) equal the sha256 of the committed files.

**T-235 wording (point 1).** All eleven Pass criteria (TP-PMC-022/024/026/027/028/029/030/031/032/033/057) carry "requires tb-infra's T-235 shim, NOT BUILT" and "no record-only comparator scope exists and none is requested"; the three Notes (023/025/056) point at TP-PMC-022; the Section 0a row and the response row match. The retained phrases "shim mask" / "shim: HPM_CTRL_MASK-shaped mcounteren" / "shim models the lock" are specifications of the not-built shim, each immediately followed by NOT BUILT; no sentence describes the shim or a comparator mode as existing. One sentence does describe a non-existent artifact as running: see finding 1.

**B4-R1 (point 2).** Stated as a ruling with rationale in gen_bug_log.md B4 Notes and the response row (options a rejected, c refused, b ruled). TP-CMP-051 keeps `CG-CMP-007.cr_insn_equal.cm_mvsa01_yes` as expected-fail (B4) in its own group; TP-CMP-053's Notes disclaim the bin; the fcov plan CG-CMP-007 line carries the ruling; the CSV row (gen_trace_tp_bin.csv:4665) and the manifest line (gen_test_cmp_zcmp_basic.fcov.yaml:392, :866) are retained and explicitly declared pending the joint landing. Nothing in the plan counts the bin as reachable by a pass test. RTL anchors (:788-800 arm, :790 COMMIT tag, :835/:839 defaults, :635/:703 rlist tests, :937 assertion) verified. gen_b4_rtl_facts.md at ab3cb31 has sha256 3a060d9…, as cited (the HEAD copy differs after 3c3a96f; the pin is accurate).

**CM74 M-3 (point 3).** Verified against gen_fu_l4_lockstep_zcmp_dummy_export.txt: orders 0x50-0x58 at pc 80000108 are loads of x27, x26, x24, x22, x21, x20, x18, x8 then the sp adjust (rlist-15 pop); orders 0x3c-0x47 at pc 80000104 are x22, x21, x20, x18, x9, then x23, x22, x20, x18, x9, x1, then the sp adjust, x8 never loaded (rlist-12 pop). The comparator row "model wrote 10 registers, dut 8, order=71 pc=80000104" is in the stdout excerpt. gen_tdd_fcov.md:79 (under evidence/) carries the mis-attribution as stated. Controller anchors: :474-477 is enter_debug_mode (EXPANDED or COMMIT), :498-500 is handle_irq (COMMIT only), matching the un-swapped text in the bug log and TP-CMP-074.

**CR11 rows (point 4).** L-1..L-6 in gen_critic_plan_witness_v11.md (03c525a, ancestor) match the six response rows; the C-2 / WP-2 rewrite matches gen_fcov_pkg.sv:62-65 and gen_flow_util.py:927-928; both LIFTED records point at ff4637c Sections 1.4 (165 items) and 1.5 (246 items), verified by `git show`; the LOG-051 row carries that pointer. TP-IRQ-073/075 Notes added; TP-CSR-108 Notes state the uncredited consequence.

**LOG-055 on owed artifacts (point 6).** The popret/popretz variant is correctly still owed. The Test Writer re-render is correctly stated as pending. The B8 mapping file gen_b8_row_mapping.md is committed at a9b63ae (ancestor) but is not cited by the bug log or plan, which still cite only the folded copy in the facts file. The B4 reproducer is committed at a9b63ae yet described as pending (finding 2).

**Rubrics.** ai-slop-comments PASS (the one added comment explains why). rtl-purity PASS (no rtl/ change). magic-numbers PASS. forces-and-hier-access PASS. assertion-integrity PASS (no checker touched).

Findings:

[Medium][dv/auto_dv/docs/gen_test_plan.md:13368] "its testlist entry runs unmeasured and its results are not counted" (repeated in the ten other Pass criteria, the Section 0a row at :238 and the response row at gen_critic_response_plan_set_v1.md:470) describes a testlist entry that does not exist: gen_testlist.yaml has no gen_pmc_ctrl / gen_test_pmc_ctrl entry and 04cf523 records "no testlist entry ... until the shim lands". LOG-055 rule: describe an artifact's state only when it is committed - reword to the decision ("no testlist entry is committed; when one lands ahead of the shim it runs unmeasured and its results are not counted").

[Medium][dv/auto_dv/docs/gen_bug_log.md:61] B4 Status and Evidence (:69) say the reproducer is "retained with that slice (sha cited when it lands)", but tb-infra slice 3 landed at a9b63ae (an ancestor of this commit) with dv/auto_dv/stim/gen_directed/gen_zcmp_mv_reserved_directed.S - cite a9b63ae and drop the pending clause.

[Low][dv/auto_dv/docs/gen_test_plan.md:238] "rtl-arch T-236 anchors, to be promoted as evidence/gen_counter_csr_anchors.md" - the file has been committed since f2b9272 (before the 0c189eb base) and revised at 0c189eb and 3c3a96f - cite the committed file and its pin instead of "to be promoted".

[Low][dv/auto_dv/docs/gen_bug_log.md:102] B8 Evidence cites tb-infra's mapping only as "folded 76cd2e5" into the facts file; the standalone mapping file dv/auto_dv/evidence/gen_b8_row_mapping.md is committed at a9b63ae - add the anchor so the record names the committed artifact.

[Low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:468] CR11-L-5 and CR11-L-6 (:469) say "the CM52-L-1 fix, in this touch" / "the CM52-L-2 fix, in this touch"; gen_promotion_table.py and gen_covergroup_set.py are not in this diff (last changed at 8bd254c, plan v2t) - say "fixed at 8bd254c (CM52)".

[Low][dv/auto_dv/docs/gen_test_plan.md:349] Section 1.7's pasted credit header carries label v2u-on-ab3cb31 while the three evidence copies regenerated in the same commit carry v2u-on-0c189eb; the digests agree, but the same generated block appears with two labels in one commit - regenerate Section 1.7 from the same run or state that the plan copy is a paste of an earlier label.

[Low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:471] B4-R1 row cites "staged as dv/auto_dv/work/dv-lead/gen_b4_patch.py", a work-tree script outside the tree, as the mechanism of the coupled half - the same class CM48 flagged low; name the joint-landing task (Test Writer re-render, LOG-036b) as the mechanism and leave the work-tree script out of the committed record.

[Low][dv/auto_dv/tools/gen_round_credit.py:165] The change puts the --csv / --md paths into the header's invocation line; the tool does not print the written paths to stdout (main prints only the heading, the Total line and the plan summary). The summary "prints the output paths it wrote" should read "the invocation header now carries the output paths"; the response file has no row for this change - add one with the accurate wording.

Final verdict: APPROVE-WITH-CHANGES
