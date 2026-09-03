# Response file: reviews of the covergroup sampling-anchor file (dv/auto_dv/evidence/gen_cg_sampling_anchors.md)

Owner: rtl-arch. Created 2026-09-03T19:06Z. Rows answer the cross-model review of commit ff4637c (slices 1-5, 429
lines, sha256 74a81831de741629; artifact dv/auto_dv/reviews/2026-09-03-claude-diff-160e4737-ff4637c1.md,
verdict APPROVE-WITH-CHANGES, committed 0a2ffe4) and later rounds on the same file. Rule: every finding
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
| CM49-I-1 | cross-model ff4637c [info] tools/specs citations | spec line anchors unverifiable from the committed tree | NOTED (no action) | Kept as file:line against the clone's own upstream copies under tools/specs (riscv-isa-manual, riscv-bitmanip, riscv-debug-spec) so a reader with the same copy can check; the Orchestrator ruled these an allowed upstream source. |

## 2. State

- Work file at 83ed029f1df6b7ea: 820 lines, ASCII-only, all 49 covergroups (sections 0-49) written; slices 6-10 (sections 26-49) are new relative to ff4637c and carry the five fixes above in sections 1, 4, 5 and 9.
