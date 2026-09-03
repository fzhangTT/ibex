# Response file: reviews of the covergroup sampling-anchor file (dv/auto_dv/evidence/gen_cg_sampling_anchors.md)

Owner: rtl-arch. Created 2026-09-03T19:06Z. Rows answer the cross-model reviews of commit ff4637c (slices 1-5, 429
lines, sha256 74a81831de741629; artifact dv/auto_dv/reviews/2026-09-03-claude-diff-160e4737-ff4637c1.md,
verdict APPROVE-WITH-CHANGES, committed 0a2ffe4) and of commit 73988b4 (complete file, 820 lines, sha256 83ed029f1df6b7ea; artifact dv/auto_dv/reviews/2026-09-03-claude-diff-53780022-73988b49.md, APPROVE-WITH-CHANGES, committed 2a414f6). Rule: every finding
gets one row with ADDRESSED or DISPUTED, the fixed line in the work file, and the RTL evidence; the
evidence copy is promoted by the Orchestrator at the reported hash, so the hash column names the state
that carries the fix. Line numbers refer to the work file dv/auto_dv/work/rtl-arch/gen_cg_sampling_anchors.md
at that hash (identical content to the evidence copy).

## 1. Findings

| # | Review | Finding (short) | Verdict | Evidence / action |
|---|---|---|---|---|
| CM49-L-1 | cross-model ff4637c [low] section 9, line 169 | csrrs/csrrc with x0 read-only forcing attributed to id_stage csr_op_en | ADDRESSED at 83ed029f1df6b7ea | Sentence now names the decoder demotion to CSR_OP_READ, rtl/ibex_decoder.sv:251-258 (csrrs/csrrc with rs1 = x0, csrrsi/csrrci with uimm = 0), consistent with sections 13, 24 and 25. |
| CM49-L-2 | cross-model ff4637c [low] section 1, line 48 | "adder_result_ext_o[33] never leaves the ALU" not literally true | ADDRESSED at 83ed029f1df6b7ea | Reworded: the carry is not exported on RVFI; the 34-bit port feeds the EX block and the multiplier (rtl/ibex_ex_block.sv:61, :130, :152). |
| CM49-L-3 | cross-model ff4637c [low] section 4, line 81 | lsu :468-486 cites the FSM use, not the alignment rule | ADDRESSED at 83ed029f1df6b7ea | Added rtl/ibex_load_store_unit.sv:403-405 (split_misaligned_access definition: word with offset != 0, halfword with offset 3); the FSM use :468-486 kept. |
| CM49-L-4 | cross-model ff4637c [low] section 5, line 141 | sreg mapping cited at compressed_decoder :157 | ADDRESSED at 83ed029f1df6b7ea | Citation corrected to rtl/ibex_compressed_decoder.sv:156 (`dst = {(rs[2:1] > 2'd0), (rs[2:1] == 2'd0), rs[2:0]}`). |
| CM49-L-5 | cross-model ff4637c [low] lines 120, 144 | filler phrases "stated for completeness" and "Note:" | ADDRESSED at 83ed029f1df6b7ea | Both phrases removed; the sentences stand as facts. |
| CM49-I-1 | cross-model ff4637c [info] tools/specs citations | spec line anchors unverifiable from the committed tree | NOTED (no action) | Kept as file:line against an untracked local copy of the upstream riscv-isa-manual, riscv-bitmanip and riscv-debug-spec sources (allowed by the Orchestrator's ruling, unverifiable from the commit) so a reader with the same copy can check. |
| CM57-L-1 | cross-model 73988b4 [low] section 26, line 430 | id_stage anchors off by one (imm_u_type :274 region, IMM_B_U arms cited :396/:424) | ADDRESSED at 4c5701e7eef8866f | Now rtl/ibex_id_stage.sv:275 (imm_u_type declaration) and the IMM_B_U mux arms :395 / :422; :396 and :424 are the IMM_B_INCR_PC arms. |
| CM57-L-2 | cross-model 73988b4 [low] section 34, lines 558, 570 | first handler record listed as a transition event with rvfi_intr regardless of cause | ADDRESSED at 4c5701e7eef8866f | Observation point now says rvfi_intr marks the handler record only after an interrupt entry (rvfi_set_trap_pc_d raised only for EXC_PC_IRQ, rtl/ibex_core.sv:2408); a new flag bullet states that after a synchronous exception the first handler record has rvfi_intr = 0 and the transition is sampled from the trap record, matching section 47. |
| CM57-L-3 | cross-model 73988b4 [low] section 27, line 444 | cites untracked work files gen_multdiv_bound_props.md and gen_tp_parts_rtl_factcheck.md X-12 | ADDRESSED at 4c5701e7eef8866f | Work-file names kept, committed carrier added: dv/auto_dv/evidence/gen_hierarchy_map.md:1478 (H-D1) and :1509 (H-M1) record the X-12 fact. |
| CM57-L-4 | cross-model 73988b4 [low] section 47, line 771 | unfinished parenthetical about a missing RVFI doc page | ADDRESSED at 4c5701e7eef8866f | Rewritten as a plain statement: no local doc page describes the RVFI export, tools/specs/riscv-formal holds only the build skeleton, the record contract is the RTL. |
| CM57-I-1 | cross-model 73988b4 [info] tools/specs citations | ISA-manual anchors unverifiable from the committed tree | NOTED (no action) | Same as CM49-I-1: kept as file:line against an untracked local copy of the upstream riscv-isa-manual and riscv-bitmanip sources, allowed by the Orchestrator's ruling, unverifiable from the commit. |
| CM62-L-1 | cross-model 4f9c359 [low] response row CM57-I-1 | "the clone's tools/specs copies" reads as tracked; tools/specs is absent from the commit | ADDRESSED at f6604f11a1b79a7a | CM57-I-1 (and CM49-I-1 for consistency) now say: an untracked local copy of the upstream riscv-isa-manual and riscv-bitmanip sources, allowed by the Orchestrator's ruling, unverifiable from the commit. |
| CM62-L-2 | cross-model 4f9c359 [low] section 47, line 771 | claim about tools/specs/riscv-formal contents is not checkable from the commit | ADDRESSED at f6604f11a1b79a7a | Clause reduced to the checkable statement (no local doc page describes the RVFI export, so the record contract is the RTL) with the riscv-formal remark marked as an untracked local observation. |
| CM62-L-3 | cross-model 4f9c359 [low] section 34, line 559 | signal-chain sentence said "rvfi_intr on the first handler instruction" unqualified | ADDRESSED at f6604f11a1b79a7a | Now "the first interrupt-handler instruction", matching lines 558 and 570. |
| CM62-I-1 | cross-model 4f9c359 [info] finding-location column | mixes pre-fix and post-fix line numbers | NOTED (no action) | The header rule (line numbers refer to the work file at the hash in the Verdict column) makes each row self-consistent. |

## 2. State

- Work file at f6604f11a1b79a7a: 821 lines, ASCII-only, all 49 covergroups (sections 0-49) written; slices 6-10 (sections 26-49) are new relative to ff4637c and carry the five CM49 fixes in sections 1, 4, 5 and 9; the four CM57 fixes are in sections 26, 27, 34 and 47; the CM62 edits touch sections 34 and 47 and this file's I-1 rows.
