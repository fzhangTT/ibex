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
and the checker fails on the missing report (gen_fu_l3_nofcov_check.log at landing 3; re-run at landing 6 on the slice-1 manifest, gen_fu_l6_nofcov_check.log).

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
| FM5 | gen_fcov_pkg.sv (gen_isa_cov): c.bnez decoded as c.beqz (`op = GEN_FC_ISA_BRANCH_CP_OP_C_BEQZ` for both CB forms) | gen_ut_lockstep on gen_branch_directed.S, urg, checker on gen_fcov_proof_slice3a.fcov.yaml | 74bafee34ddf4fa7 (original blob 68ba3dfd8d3c4205) | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_isa_branch_cg.cp_op.c_bnez` (gen_fu_l6_FM5_check.log) | gen_fcov_proof_slice3a_fm5_ablation.fcov.yaml: `PASS -- all 25 declared bins hit` (gen_fu_l6_FM5_ablation_check.log; the FM_all driver log's FM5 line reports two unhit bins because it ran the 27-bin pre-L5R-1 manifest with cp_wrap.yes, the retained check is the 26-bin manifest re-check) |
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

## Landing 7 (the Critic tb_l6 fixes): the report-phase referees have reds

Built out of tree from the wit_root copy at build x (a48917a3f74eeea3), row `referee`: the catch runs with the default knobs, the
ablation with `+gen_fcov_en=0` (no covergroup, so the referee has nothing to judge and the bookkeeping path alone runs).

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| FM10 | gen_fcov_pkg.sv (gen_isa_cov): `br_cg.sample(...)` removed while `n_br++` stays, so the branch group is counted and never sampled | gen_ut_lockstep on gen_branch_directed.S, 8000 retirements | 1094004eeaa5f94b | FAIL (UVM_ERROR 1): `GEN_FCOV_REF gen_isa_branch_cg sampled without coverage` (tb_l6 M-4) | PASS (0) |
| FM4UT | the FM4 text (the slt eq compare on the 1-bit cast) run under the sampler unit test gen_ut_isa_cov, zc image, every knob default | b3d31097833751a4 | FAIL: `GEN_FCOV_UT slti rs1 == imm is eq: ... 6 expected 0`, self-test 27 cases 1 failure (the unit test's own red for FM4, tb_l6 M-3 as widened) | `+gen_fcov_en=0`: FAILS with 11 of 27 cases (the FM4 case and ten cases that need the covergroups on) (the vector table judges the classifier, not the covergroup), retained as such |
| FM11 | gen_fcov_pkg.sv (gen_isa_cov): the cm.mva01s expansion expected with its registers swapped (`want_rd = sreg; want_rs1 = areg`), so every legal pair mismatches | gen_ut_lockstep on gen_zcmp_mv_directed.S, 1000 retirements | 1def4880d2bdaa6c | FAIL (UVM_ERROR 1): `GEN_FCOV_REF gen_cmp_zcmp_mv_cg: 68 legal move pairs whose micro-ops did not match the expansion`; report line `move pairs: 130 sampled, 68 with mismatching micro-ops` (tb_l6 M-2) | PASS (0) |

FM10's first compile FAILED (the mutant text put its comment on the argument line of the multi-line `br_cg.sample(` call and
commented the arguments out; the first compile's log was not kept and the batch log gen_fu_l8_oot_mutation_batch_fm.log records only
`FM10: compile FAILED`, so the compiler's message is not retained, tb_l10 L-3) and was re-run with the comment
moved (gen_fu_l8_oot_mutation_batch_fm10.log). The unmutated build x reports `move pairs: 130 sampled, 0 with mismatching micro-ops` on the same program, and the unit-test run
`5 sampled, 1 with mismatching micro-ops (1 of them the self-test's)`: the self-test's own miss vector is excluded from the referee
by `ut_mv_miss_expected`, which the vector case sets after asserting the count.

## Slice A (gen_rvfi_record_cg, gen_mul_timing_cg, gen_rst_boot_cg, gen_sec_ctrl_inputs_cg)

Built out of tree from the wit_root copy beside build ag, row `fcov` (the catch is the slice's proof manifest failing on the mutant's report;
the ablation is the same manifest minus the bins the mutant hides, PASS on the same report). The mutated file's original sha256 is the
landing's gen_fcov_pkg.sv (8faf5e0d8b481186).

| mutant | what is broken | run, manifest | build | catch | ablation |
|---|---|---|---|---|---|
| FM12 | gen_fcov_pkg.sv: a 32-bit sequential record classed plus2 (`rec_pc_delta_cls`) | gen_ut_lockstep s7 image debug storm, gen_fcov_proof_slice5a.fcov.yaml | 62d7aff8f43a9e23 | checker `FAIL -- 1 declared bin(s) not hit: gen_rvfi_record_cg.cp_pc_delta.plus4` (gen_fu_l12_FM12_check.log) | gen_fcov_proof_slice5a_fm12_ablation.fcov.yaml `PASS -- all 29 declared bins hit` |
| FM13 | gen_fcov_pkg.sv: a load before the multiply classed ALU (`mt_prev_cls`) | gen_ut_lockstep on gen_muldiv_directed.S, gen_fcov_proof_slice5b.fcov.yaml | 6be9ba5bbda6f01e | `FAIL -- 1 declared bin(s) not hit: gen_mul_timing_cg.cp_prev.load` | slice5b_fm13_ablation `PASS -- all 13 declared bins hit` |
| FM14 | gen_fcov_pkg.sv: a high boot page classed mid (`rst_boot_cls`) | gen_ut_boot zc, gen_fcov_proof_slice5c.fcov.yaml | 1742c09b93471f84 | `FAIL -- 1 declared bin(s) not hit: gen_rst_boot_cg.cp_boot_addr.high` | slice5c_fm14_ablation `PASS -- all 7 declared bins hit` |
| FM15 | gen_fcov_pkg.sv: the cpuctrlsts read-back keeps bit 6 only (double_fault_seen dropped) | gen_ut_lockstep on gen_cpuctrl_directed.S, gen_fcov_proof_slice5d.fcov.yaml | d51e743703bfcf74 | `FAIL -- 2 declared bin(s) not hit: cp_bits67_readback.b6_1_b7_1, .b6_0_b7_1` | slice5d_fm15_ablation `PASS -- all 8 declared bins hit` |

A first FM15 form swapped bits 7 and 6; with both mixed bins hit by the program the swap is invisible to a bin checker, so the mutant
drops one bit instead (recorded so that nobody re-tries the swap).

## Landing 11: FM12-FM15 against the landing sources

The landing-10 batch (fm_sliceA over an older mut_oot_fcov.sh) hashed gen_rvfi_pkg.sv as its canary (1d9e2f8d9e5927dd) and its ablation step
crashed (mkablation.py built every mutant's ablation from any directory), so the landing-10 ablation checks were run by hand without a stamp
and the mutant diffs were not retained (CM138-Ma-1 / Ma-2, tb_l11 M-1 / M-2). Re-run in landing 11 (fm_l11.sh): the mutant copies come from
l11_root, the canary line hashes the mutated file's copy in the source tree (`dv/auto_dv/env/gen_fcov_pkg.sv sha256 51315dd2b793c8a2`), the
mutation as applied is retained (gen_fu_l13_FM1x_mutant.diff), the checker runs on the slice's proof manifest and on its ablation manifest
against the mutant's own urg report, and both check logs carry a stamp (manifest path and md5, report directory, build sha, mutant id).

| id | catch (the checker on the proof manifest) | ablation (the manifest without the hidden bins) |
|---|---|---|
| FM12 (gen_rvfi_record_cg: plus4 classed as plus2) | FAIL: `1 declared bin(s) not hit: gen_rvfi_record_cg.cp_pc_delta.plus4` (gen_fu_l13_FM12_check.log; build e76e09cd462bb372) | PASS, all 29 declared bins hit (gen_fu_l13_FM12_ablation_check.log) |
| FM13 (gen_mul_timing_cg: a load before the multiply classed as ALU) | FAIL: `cp_prev.load` not hit (gen_fu_l13_FM13_check.log; ce582876c7996cb2) | PASS, 13 bins (gen_fu_l13_FM13_ablation_check.log) |
| FM14 (gen_rst_boot_cg: a high boot page classed as mid) | FAIL: `cp_boot_addr.high` not hit (gen_fu_l13_FM14_check.log; 7ad31f53e2025083) | PASS, 7 bins (gen_fu_l13_FM14_ablation_check.log) |
| FM15 (gen_sec_ctrl_inputs_cg: the read-back drops double_fault_seen) | FAIL: `cp_bits67_readback.b6_1_b7_1, b6_0_b7_1` not hit (gen_fu_l13_FM15_check.log; e86e513b22de3b85) | PASS, 8 bins (gen_fu_l13_FM15_ablation_check.log) |

The batch driver log is gen_fu_l13_oot_mutation_batch_fm_l11.log; the ablation manifests in evidence/ are the ones checked (identical to the
mutant directories' copies).
