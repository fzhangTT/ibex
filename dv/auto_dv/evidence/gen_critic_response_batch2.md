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
| CR-B2-L-7 | low | literal 50 beside ODD_MIN 60; MISA_C_BIT, MPP_M, CAUSE_ECALL_M re-typed | FIXED (3d) | gen_isa_cti_prog.ODD_PLAN_MIN = 50 (the plan's floor) used by the generator assert and the test; MISA_C_BIT, MSTATUS_MPP_M, CAUSE_ECALL_M live in gen_prog_const; LASTC_SENTINEL stays the generator's own sentinel. Seed-1 program byte-identical. |
| CR-B2-L-8 | low | mul_div filler registers inside the operand set | FIXED (3d) | FILLER_REGS = x29..x31 excluded from OP_REGS with a disjointness assertion (as mul_mul); programs re-generated and re-run (l7_mul_div_s1/s2/red_014), 30-seed sweep clean. |
| CR-B2-I-1 | info | no Runtime wave has run batch 2 | OPEN | test-writer-049..062 filed against e83614c (3c 69be96b); served once the LOG-024 gate lifts. |
| CR-B2-I-2 | info | TP-CMP-001 floor stated two ways | FIXED (3d) | One statement: >= 3000 retired per seed with the per-form floors governing (DV Lead ruling). |
| CR-B2-I-3 | info | commit message 66 vs 76 reds | NOTED | The files and the transcript carry 76; the message was the Orchestrator's, from my earlier report's number. |
