# Mutation record: the plan's covergroups (T-205)

Owner: tb-infra, 2026-09-03. Format: dv/auto_dv/mutations/gen_README.md. A covergroup has no checker to fire; its proof is the
fcov-expectation check (trust triad rule 3) and a sampler mutant is caught by that check: the mutant run PASSES the simulation
and `ci/check_fcov_expectations.py` on the slice's proof manifest names the bins the mutant leaves unhit. Out of tree (a scratch
copy of the wit_root sources plus the one edit; rtl untouched); `build` is the mutant build's `sources sha256`.

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| FM1 | gen_fcov_pkg.sv (gen_isa_cov): c.mul is never decoded from its 16-bit RVFI form (`is_cmul = 0`) | gen_ut_lockstep on gen_muldiv_directed.S, urg, checker on gen_fcov_proof_slice1.fcov.yaml | a65d88c23c734972 | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_mul_ops_cg.cp_op.c_mul` (and every c_mul cross tuple uncovered in urg) | gen_fcov_proof_slice1_fm1_ablation.fcov.yaml (the same manifest without the c_mul bins) on the FM1 report: `PASS -- all 127 declared bins hit` (gen_fu_l4_FM1_ablation_check.log) |

Exact edit: `bit is_cmul = (t.insn[1:0] == 2'b01 && t.insn[15:10] == 6'b100111 && t.insn[6:5] == 2'b10);` -> `bit is_cmul = 1'b0;`.
Red of the slice (not a mutant): the proof run with `+gen_fcov_en=0` on a fresh vdb has no covergroup, urg writes no grpinfo.txt
and the checker fails on the missing report (gen_fu_l3_nofcov_check.log).

## Slice 2 (T-205: gen_bit_count_cg, gen_cmp_zca_cg, gen_cmp_zcmp_pushpop_cg)

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| FM2 | gen_fcov_pkg.sv (gen_isa_cov): every Zca successor reported as 16-bit (`cp_next_len` never n32) | gen_ut_lockstep on gen_zca_directed.S, urg, checker on gen_fcov_proof_slice2b.fcov.yaml | 0dc3381eb2ca0793 | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_cmp_zca_cg.cp_next_len.n32` | the manifest without that bin passes (every other bin of the run unchanged) |
| FM3 | gen_fcov_pkg.sv (gen_isa_cov): the cm.pop source word decoded as cm.push | gen_ut_lockstep on gen_zcmp_directed.S, urg, checker on gen_fcov_proof_slice2c.fcov.yaml | 13317a26ec420c27 | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_cmp_zcmp_pushpop_cg.cp_insn.cm_pop` | the manifest without the cm_pop bin passes |

Exact edits: FM2 `zca_v[2] = (nxt == null) ? -1 : ((nxt.insn[1:0] != 2'b11 || nxt.ext_exp_valid) ? GEN_FC_CMP_ZCA_CP_NEXT_LEN_N16 : GEN_FC_CMP_ZCA_CP_NEXT_LEN_N32);`
-> `zca_v[2] = (nxt == null) ? -1 : GEN_FC_CMP_ZCA_CP_NEXT_LEN_N16;`; FM3 `5'b11010: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP;` ->
`5'b11010: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH;`. Logs: gen_fu_l4_FM2_FM3_check.log and gen_fu_l4_FM{2,3}_*.

## The cast mutant of CM51-MAJ-1 (FM4) and what the checker can and cannot see

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| FM4 | gen_fcov_pkg.sv (gen_isa_cov): the slt `eq` compare re-cast to one bit (`rs1 == logic'(32'(imm))`, the landing-3 defect) | gen_ut_lockstep on gen_alu_directed.S, urg, checker on gen_fcov_proof_slice1b.fcov.yaml | d710be74d01d442a | NOT caught by the hit / unhit verdict: `PASS -- all 122 declared bins hit`, because the mutant makes `eq` fire MORE often (168 hits against 84 on the corrected sampler, `other` 2506 against 2590); the class is visible only in the counts the checker prints (gen_fu_l4_FM4_check.log) | none: the proof manifest has no count assertion |

The record states the limit: a classifier that puts too many samples into a bin is invisible to a manifest of at-least-once bins.
Guarding this class needs a count assertion in the proof (a bin's expected count on a directed program) or a reference model of the
classifier; the transcript carries the counts of every proof run so a reviewer can compare them, and the renderer's unit test cannot
help (the classifiers are hand-written). Owed to the fcov plan owner as a note: the plan's `eq` and `other` bins of one coverpoint are
a partition, so a directed program with a known number of equal cases is the natural count check.
