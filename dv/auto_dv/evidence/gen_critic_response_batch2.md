# Response: Critic verdict on Phase 1 batch 2 (`dv/auto_dv/docs/gen_critic_tests_batch2_v1.md`, APPROVE with lows)

Author: test-writer, 2026-09-03 14:4x UTC. Landing 3d (follow-up) carries the rows marked FIXED (3d); evidence in
`dv/auto_dv/evidence/gen_tdd_batch2.md` and the retained logs `dv/auto_dv/evidence/gen_tdd_logs/test_writer/`.

| # | Severity | Finding | Disposition | Change and evidence |
|---|---|---|---|---|
| CR-B2-L-1 | low | isa_cti manifest header reasons differ from the class dict | FIXED (3c) | Re-rendered from the module; the self-test compares every committed manifest's full text since 3c. |
| CR-B2-L-2 | low | 76 per-item red rows labelled md5 (stdout.log) while excerpt copies are retained | FIXED (3d) | Table column relabelled and the per-item red rows recomputed over the retained excerpt copies. |
| CR-B2-L-3 | low | cmp_zca detail string names odd targets that are not drawn | FIXED (3d) | Detail reads "both alignments, x1 not written (odd targets not drawn: B13)". |
| CR-B2-L-4 | low | isa_alu 604 vs 602 in runs and transcript | FIXED (3c/3d) | Retained green l5_isa_alu_s1 with GEN_TEST_BINS n=602 (3c); the transcript summary row says 602 and names the retained run (3d). |
| CR-B2-L-5 | low | TP-ISA-019 substitution (RVFI fire-check replaced by program-visible markers) unlisted | FIXED (3d) | Named in the gen_test_isa_cti docstring as a substitute observable pending the RVFI record export. |
| CR-B2-L-6 | low | isa_alu floors count rd = x0 ops while the detail says they are counted apart | FIXED (3d) | The detail states what the floor counts (every plan op of the item) and that vacuous and degenerate ops are excluded from the value compare only; the floor semantics are unchanged and now truthfully described. |
| CR-B2-L-7 | low | literal 50 beside ODD_MIN 60; MISA_C_BIT, MPP_M, CAUSE_ECALL_M re-typed | FIXED (3d, completed 3e) | gen_isa_cti_prog.ODD_PLAN_MIN = 50 (the plan's floor) used by the generator assert and the test; MISA_C_BIT, MSTATUS_MPP_M, CAUSE_ECALL_M live in gen_prog_const; LASTC_SENTINEL stays the generator's own sentinel. Seed-1 program byte-identical. 3e: the detail string and the docstring name the constant instead of the literal (3d review L-2). |
| CR-B2-L-8 | low | mul_div filler registers inside the operand set | FIXED (3e); the 3d row was false | 3d moved FILLER_REGS to x29..x31 and asserted them disjoint from OP_REGS but left FILLER_TEMPLATES on x5..x7, so the fillers still clobbered operand registers and the row marked FIXED described work that did not touch the failing path (3d review H-1; an honesty defect under LOG-024d (c)). 3e derives the templates from FILLER_REGS, asserts at import that no template names another register, regenerates the programs (0 filler lines on x5..x7, 141 / 99 on x29..x31) and re-runs them: l8_mul_div_s1 PASS, l8_mul_div_s2 PASS, l8_mul_div_red_014 RED-OK; 30-seed sweep 660/660 (gen_tdd_batch2.md). |
| CR-B2-I-1 | info | no Runtime wave has run batch 2 | OPEN | test-writer-049..062 filed against e83614c (3c 69be96b); served once the LOG-024 gate lifts. |
| CR-B2-I-2 | info | TP-CMP-001 floor stated two ways | FIXED (3d) | One statement: >= 3000 retired per seed with the per-form floors governing (DV Lead ruling). |
| CR-B2-I-3 | info | commit message 66 vs 76 reds | NOTED | The files and the transcript carry 76; the message was the Orchestrator's, from my earlier report's number. |

## TB Infra follow-up landing 1 (ce33b4f) closes the two comparator dependencies of this batch

| # | Kind | Item | Disposition | Change and evidence |
|---|---|---|---|---|
| TB-R10 | dependency | shim mtval after c.ebreak (model pc, DUT 0): cmp_zca FAILed through isa_rd/isa_mem uvm_errors | CLOSED (3e) | l9_cmp_zca_s1 PASS with UVM_ERROR 0 and the pinned red RED-OK on out_head6 (gen_tdd_batch2.md Section 2b); docstring updated; staged red entry reads (RED-OK). |
| TB-R11 | dependency | isa_pc_next bit 0 on odd jalr/c.jr/c.jalr (B13): isa_cti FAILed through uvm_error | CLOSED (3e) | l9_isa_cti_s1 PASS with UVM_ERROR 0 and the pinned red RED-OK on out_head6 (Section 2b); the comparator counts the exception, B13's xfail item owns the bug. |

## Cross-model review of 65b7228..aa13338 (the isa_alu touch, APPROVE-WITH-CHANGES, `dv/auto_dv/reviews/` artifact d430aa1; relay ids CM106-*)

| # | Severity | Finding | Disposition | Change and evidence |
|---|---|---|---|---|
| CM106-L-1 | low | the cm92_* family prose placed the greens on out_head15 while the rows and gen_tdd_batch2.md place them on out_head16, and gen_cm92_isa_alu_wrap_sites.log reported the out_head15 draft runs | FIXED (this touch) | The family prose reads out_head16; the wrap-sites log is regenerated from the out_head16 runs (verdicts and sites from those runs and the rebuilt, byte-identical images), and Section 5 says its first version reported the draft runs. |
| CM106-L-2 | low | the seed-1 full green lacked the run header line | FIXED (this touch) | gen_cm92_isa_alu_s1_stdout.log carries its run header line first (sources_sha, template_sha, test_sha), as the excerpts do; the red and the three greens were re-run on out_head16 with the corrected test so the headers name the committed test_sha. |
| CM106-L-3 | low | the layout assert hand-encoded 0x80001000 beside a MEMORY_MAP-derived base | FIXED (this touch) | The assert states the invariant itself: base + o.off + (0x7FFFF << 12) >= 1 << 32; the placement-invariant probe re-run on this form fires for seeds 1..3 with the sites forced to the start. |
| CM106-L-4 | low | the space units were tagged wrap = False although they carry out of the 32-bit add, so check_coverage counted them toward the no-carry combos | FIXED (this touch) | The tag reads imm20 bit 19 or the space unit, with the comment corrected; the combos assert still holds (the no-carry combos come from the capped random case). |
| CM106-L-5 | low | the space predicate detects only the upward wrap; the downward wrap becomes reachable with WP-9's low page | FIXED (this touch) | The fire check's comment names the downward wrap and WP-9 as the point where the floor widens; the predicate is unchanged until then. |
| CM106-L-6 | low | the commit subject's "473 declared bins" (the manifest has 602) | NO CHANGE | The Orchestrator's, recorded in the log. |

## Cross-model review of bcaede6..4413874 (the rows touch, APPROVE-WITH-CHANGES, `dv/auto_dv/reviews/2026-09-03-claude-diff-bcaede64-44138741.md`; relay ids CM114-*; the rows on gen_test_isa_alu, its generator and its logs)

| # | Severity | Finding | Disposition | Change and evidence |
|---|---|---|---|---|
| CM114-L-1 | low | gen_cm92_isa_alu_wrap_sites.log carried a truncated cocotb line leaked from the multi-line failure excerpt | FIXED (this touch) | The log is regenerated from the out_head16 runs with the TDD-red line cut at its line end (the excerpt pattern no longer crosses newlines) and asserted free of cocotb lines; the carry-out counts now name negative immediates and space units separately. |
| CM114-L-2 | low | the fire check's comment still called the carry-out "the negative-immediate case" although the two space units also satisfy word < pc | FIXED (this touch) | The comment says the carry set holds the negative immediates, which stay in the space, plus the space units, whose carry-out is the wrap; the red and the three greens re-run on out_head16 with the corrected test so the headers carry the committed test_sha. |
| CM114-I-2 | info | the random extra auipc case draws imm in 1..0x7FFFF tagged wrap False and could carry out untagged; harmless since the tag feeds only the combos set | NOTED | The tag comment says so ("the random extra case stays untagged even when it carries out"); the draw is unchanged so the committed programs stay byte-identical. |
