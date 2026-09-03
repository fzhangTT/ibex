# Response rows: the T-205 covergroup landings' reviews

Owner: tb-infra, 2026-09-03. Rows keyed by the review artifact; every row says in which slice it is answered.

## Cross-model review of landing 3 (a786543, artifact 2026-09-03-claude-diff-0a2ffe48-a786543c.md, APPROVE-WITH-CHANGES)

| id | finding | status | as built |
|---|---|---|---|
| CM51-MAJ-1 | gen_fcov_pkg.sv: `rs1 == logic'(32'(imm))` casts the sign-extended immediate to one bit, so `cp_slt_case.eq` fired on `rs1 == imm[0]` (168 hits in the retained run where the plan's definition gives 84) | FIXED (slice 2) | `rs1 == 32'(imm)`; the slice-1b proof re-run on the corrected sampler (gen_fu_l4_slice1b_check.log: eq count 84); the whole sampler audited for the cast pattern (`grep logic'(` finds no other use; every other compare is between equal-width vectors or ints); mutant FM4 re-introduces the 1-bit cast: the checker's hit/unhit verdict cannot see a bin hit too often, so the catch is the eq count in the checker output (168 against 84), recorded as such in gen_mut_fcov.md. |
| CM51-MIN-1 | "1403 named bins (250 coverpoint bins, 1153 cross bins)" is wrong: 250 coverpoint + 1403 cross = 1653; the renderer's summary counted cross-bin lines only | FIXED (slice 2) | the renderer prints coverpoint bins and cross bins separately; the transcript's figures corrected (six groups 250 / 1403, nine groups 466 / 2044). |
| CM51-MIN-2 | gen_component_api_fcov.md: CG-BIT-001 "51 / 380" where the include has 373 cross bins | FIXED (slice 2) | 373. |
| CM51-MIN-3 | the FM1 row claims an ablation with no retained log | FIXED (slice 2) | gen_fcov_proof_slice1_fm1_ablation.fcov.yaml (the slice-1 manifest without the c_mul bins) against the FM1 report: PASS, 127 bins (gen_fu_l4_FM1_ablation_check.log, manifest row added). |
| CM51-NIT-1 | hand-encoded opcodes 7'b0110011 / 7'b0010011 | DONE (slice 2) | `ibex_pkg::OPCODE_OP` / `OPCODE_OP_IMM` in the sampler's compares. |
