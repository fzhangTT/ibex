# Mutation record: the plan's covergroups (T-205)

Owner: tb-infra, 2026-09-03. Format: dv/auto_dv/mutations/gen_README.md. A covergroup has no checker to fire; its proof is the
fcov-expectation check (trust triad rule 3) and a sampler mutant is caught by that check: the mutant run PASSES the simulation
and `ci/check_fcov_expectations.py` on the slice's proof manifest names the bins the mutant leaves unhit. Out of tree (a scratch
copy of the wit_root sources plus the one edit; rtl untouched); `build` is the mutant build's `sources sha256`.

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| FM1 | gen_fcov_pkg.sv (gen_isa_cov): c.mul is never decoded from its 16-bit RVFI form (`is_cmul = 0`) | gen_ut_lockstep on gen_muldiv_directed.S, urg, checker on gen_fcov_proof_slice1.fcov.yaml | 9d7aa2572f05bb09 (original blob 68ba3dfd8d3c4205, the landed sampler; the landing-3 row named a pre-landing blob 612da583, gen_critic_tb_l3.md M-1) | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_mul_ops_cg.cp_op.c_mul` (gen_fu_l6_FM1_check.log) | gen_fcov_proof_slice1_fm1_ablation.fcov.yaml on the same report: `PASS -- all 127 declared bins hit` (gen_fu_l6_FM1_ablation_check.log) |

Exact edit: `bit is_cmul = (t.insn[1:0] == 2'b01 && t.insn[15:10] == 6'b100111 && t.insn[6:5] == 2'b10);` -> `bit is_cmul = 1'b0;`.
Red of the slice (not a mutant): the proof run with `+gen_fcov_en=0` on a fresh vdb has no covergroup, urg writes no grpinfo.txt
and the checker fails on the missing report (gen_fu_l3_nofcov_check.log).

## Slice 2 (T-205: gen_bit_count_cg, gen_cmp_zca_cg, gen_cmp_zcmp_pushpop_cg)

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| FM2 | gen_fcov_pkg.sv (gen_isa_cov): every Zca successor reported as 16-bit (`cp_next_len` never n32) | gen_ut_lockstep on gen_zca_directed.S, urg, checker on gen_fcov_proof_slice2b.fcov.yaml | 9e4835e38cc92d68 (original blob 68ba3dfd8d3c4205, the landed sampler; the landing-4 row named a pre-landing blob 86fa86e80dd8eb83) | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_cmp_zca_cg.cp_next_len.n32` (gen_fu_l6_FM2_check.log) | gen_fcov_proof_slice2b_fm2_ablation.fcov.yaml on the same report: `PASS -- all 45 declared bins hit` (gen_fu_l6_FM2_ablation_check.log) |
| FM3 | gen_fcov_pkg.sv (gen_isa_cov): the cm.pop source word decoded as cm.push | gen_ut_lockstep on gen_zcmp_directed.S, urg, checker on gen_fcov_proof_slice2c.fcov.yaml | bacda7f424609ede (original blob 68ba3dfd8d3c4205) | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_cmp_zcmp_pushpop_cg.cp_insn.cm_pop` (gen_fu_l6_FM3_check.log) | gen_fcov_proof_slice2c_fm3_ablation.fcov.yaml: `PASS -- all 37 declared bins hit` (gen_fu_l6_FM3_ablation_check.log) |

Exact edits: FM2 `zca_v[2] = (nxt == null) ? -1 : ((nxt.insn[1:0] != 2'b11 || nxt.ext_exp_valid) ? GEN_FC_CMP_ZCA_CP_NEXT_LEN_N16 : GEN_FC_CMP_ZCA_CP_NEXT_LEN_N32);`
-> `zca_v[2] = (nxt == null) ? -1 : GEN_FC_CMP_ZCA_CP_NEXT_LEN_N16;`; FM3 `5'b11010: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP;` ->
`5'b11010: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH;`. Logs: gen_fu_l4_FM2_FM3_check.log and gen_fu_l4_FM{2,3}_*.

## The cast mutant of CM51-MAJ-1 (FM4) and what the checker can and cannot see

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| FM4 | gen_fcov_pkg.sv (gen_isa_cov): the slt `eq` compare re-cast to one bit (`rs1 == logic'(32'(imm))`, the landing-3 defect) | gen_ut_lockstep on gen_alu_directed.S, urg, checker on gen_fcov_proof_slice1b.fcov.yaml | 6df309833d045c69 (original blob 68ba3dfd8d3c4205) | NOT caught by the hit / unhit verdict, as before: `PASS -- all 122 declared bins hit` (gen_fu_l6_FM4_check.log); the class is caught now by gen_ut_isa_cov: FCOV_QUERY 0 on gen_alu_directed.S must read 84 and the vector table's `slti rs1[0] == imm[0] alone is not eq` row | none: the proof manifest has no count assertion; the unit test is the control |

The record states the limit: a classifier that puts too many samples into a bin is invisible to a manifest of at-least-once bins.
Guarding this class needs a count assertion in the proof (a bin's expected count on a directed program) or a reference model of the
classifier; the transcript carries the counts of every proof run so a reviewer can compare them, and the renderer's unit test cannot
help (the classifiers are hand-written). Owed to the fcov plan owner as a note: the plan's `eq` and `other` bins of one coverpoint are
a partition, so a directed program with a known number of equal cases is the natural count check.

## Slice 3 (T-205: gen_cmp_zcmp_mv_cg, gen_csr_trap_setup_warl_cg, gen_isa_branch_cg)

Method as above: the mutant is applied to a copy of the landed sources (gen_fcov_pkg.sv sha256 68ba3dfd8d3c4205, build s 9f123de2aa16eb21; the slice-3 landing's rows named the then-current blob 17e8e582968cb01e and were re-run here),
compiled out of tree, run once with the covergroups on (the lock-step run itself passes: the mutation is in the sampler), urg on that run's
vdb, and the checker on the slice's proof manifest; the ablation is the manifest without the named bins, which is the un-mutated proof.

| id | mutation | catch run | mutant build (sources sha256) | result | ablation |
|---|---|---|---|---|---|
| FM5 | gen_fcov_pkg.sv (gen_isa_cov): c.bnez decoded as c.beqz (`op = GEN_FC_ISA_BRANCH_CP_OP_C_BEQZ` for both CB forms) | gen_ut_lockstep on gen_branch_directed.S, urg, checker on gen_fcov_proof_slice3a.fcov.yaml | 74bafee34ddf4fa7 (original blob 68ba3dfd8d3c4205) | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_isa_branch_cg.cp_op.c_bnez` (gen_fu_l6_FM5_check.log) | gen_fcov_proof_slice3a_fm5_ablation.fcov.yaml: `PASS -- all 26 declared bins hit` (gen_fu_l6_FM5_ablation_check.log) |
| FM6 | gen_fcov_pkg.sv (gen_isa_cov): the hazard tracker never sees the writer before a move (`mv_hz = ..._NONE`) | gen_ut_lockstep on gen_zcmp_mv_directed.S, urg, checker on gen_fcov_proof_slice3b.fcov.yaml | a272e110e99e5882 (original blob 68ba3dfd8d3c4205) | simulation PASS; checker `FAIL -- 2 declared bin(s) not hit: gen_cmp_zcmp_mv_cg.cp_hazard_src.alu_prev, ...load_prev` (gen_fu_l6_FM6_check.log) | gen_fcov_proof_slice3b_fm6_ablation.fcov.yaml: `PASS -- all 27 declared bins hit` (gen_fu_l6_FM6_ablation_check.log) |
| FM7 | gen_fcov_pkg.sv (gen_isa_cov): the immediate CSR forms sampled as the register forms (`csr_op = f3[1:0] - 1`, the `+ 3` for f3[2] dropped) | gen_ut_lockstep on gen_csr_warl_directed.S, urg, checker on gen_fcov_proof_slice3c.fcov.yaml | f48ec640b218605b (original blob 68ba3dfd8d3c4205) | simulation PASS; checker `FAIL -- 3 declared bin(s) not hit: gen_csr_trap_setup_warl_cg.cp_op.csrrci, .csrrsi, .csrrwi` (gen_fu_l6_FM7_check.log) | gen_fcov_proof_slice3c_fm7_ablation.fcov.yaml: `PASS -- all 62 declared bins hit` (gen_fu_l6_FM7_ablation_check.log) |

The first FM6 run (build l, before the hazard tracker decoded loads) named only load_prev, because alu_prev was not in the proof
manifest generated from that build: a mutant catch is only as wide as the manifest, so the manifests are regenerated from the landed
build's reports before the mutants are judged.

## Slice 4a and the landing-4 re-review (T-205: gen_bit_sbit_cg, gen_cmp_zcb_cg; every earlier mutant re-run)

Every sampler mutant (FM2, FM3, FM5-FM9) is applied to the landed sampler (gen_fcov_pkg.sv sha256 68ba3dfd8d3c4205, the blob of build s
9f123de2aa16eb21), and every one has its ablation manifest (the proof minus the mutant's bins) checked on the same report (gen_critic_tb_l4.md M-1).

| id | mutation | catch run | mutant build (sources sha256) | result | ablation |
|---|---|---|---|---|---|
| FM8 | gen_fcov_pkg.sv (gen_isa_cov): bext decoded as bclr | gen_ut_lockstep on gen_sbit_directed.S, urg, checker on gen_fcov_proof_slice4a.fcov.yaml | 0773ecdfa6139873 | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_bit_sbit_cg.cp_op.bext` (gen_fu_l6_FM8_check.log) | gen_fcov_proof_slice4a_fm8_ablation.fcov.yaml: `PASS -- all 21 declared bins hit` (gen_fu_l6_FM8_ablation_check.log) |
| FM9 | gen_fcov_pkg.sv (gen_isa_cov): c.lh decoded as c.lhu | gen_ut_lockstep on gen_zcb_directed.S, urg, checker on gen_fcov_proof_slice4b.fcov.yaml | 5c9cb67d711e7500 | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_cmp_zcb_cg.cp_insn.c_lh` (gen_fu_l6_FM9_check.log) | gen_fcov_proof_slice4b_fm9_ablation.fcov.yaml: `PASS -- all 28 declared bins hit` (gen_fu_l6_FM9_ablation_check.log) |

FM4 (the 1-bit cast) stays informational: the checker cannot see an over-count; the classifier unit test gen_ut_isa_cov (FCOV_QUERY 0 on
gen_alu_directed.S = 84, FCOV_SELFTEST "slti rs1[0] == imm[0] alone is not eq") is the mechanism that would catch it now.
