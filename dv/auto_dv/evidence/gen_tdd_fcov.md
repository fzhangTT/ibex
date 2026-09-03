# TDD transcript: the plan's covergroups (T-205, LOG-046)

Owner: tb-infra. Method: out-of-tree copy (scratch wit_root, on the landing-2b sources); the shared tree untouched until the
announced window. Every slice: the renderer's include and unit test, the sampler, a lock-step run of a directed operand-walk
program per family (the model checks every result while the covergroups sample), urg on that run's own vdb, and the real
checker (`ci/check_fcov_expectations.py --report-dir`) on a manifest that declares every coverpoint bin of the slice's groups;
one red per slice and one sampler mutant. Logs: dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l3_*.

## 1. Slice 1: gen_mul_ops_cg, gen_div_ops_cg, gen_isa_alu_reg_cg, gen_bit_zba_zbb_ops_cg, gen_isa_alu_imm_cg, gen_isa_shift_cg

- Renderer first (`dv/auto_dv/tb/gen_fcov_codegen.py`, gen_component_api_fcov.md Section 8): the trace CSV keys covergroups by
  plan id, the SV name comes from the plan header, the bin order from the plan line and the cross components from the plan's
  cross line; two forms the first version could not render were found on the real inputs and fixed before any build: a
  cross whose component name contains `x` (`cp_rd_x0`, split on whitespace-delimited `x` only) and a cross with explicitly
  named tuples (`cr_overflow.div_intmin_m1{div, int_min, all_ones}`). Six groups render to 1403 named bins (250 coverpoint
  bins, 1153 cross bins). VCS refused the first include on `bins xor` (a keyword): keyword bins render as escaped identifiers
  and urg reports them plainly. Unit test gen_ut_fcov_codegen.py: --check on the tree, refusals (plan / CSV bin mismatch,
  unsplittable cross bin, cross without a plan line), a stale include caught (gen_fu_l3_ut_fcov_codegen.log).
- Sampler `gen_isa_cov` (gen_fcov_pkg.sv) subscribed to the RVFI monitor beside the scoreboard; the sample() arguments follow
  the plan's coverpoint order (the renderer's first version used the CSV's order: caught by reading the rendered signatures
  against the calls before the first build).
- Builds (wit_root): g e39aa0e0c5bb99bf (three groups), h 8452b39617094289 (six groups; the landed sources).
- Programs: gen_muldiv_directed.S (11 operand classes, every ordered pair, mul / mulh / mulhsu / mulhu / c.mul (its 16-bit
  encoding, `.2byte 0x9dd1` and `0x9dcd`) / div / divu / rem / remu / add .. and, with the distinct, rd = x0, rs1 = rs2, rs = rd
  and all-the-same register relations; 10206 records, 0 mismatches) and gen_alu_directed.S (14 classes incl. the byte / half
  sign values, 0xE0000000, 32, 33, 0xFFFFFFE0; sh1add .. packh, zext.h, sext.b/h, sll/srl/sra, slli/srli/srai with amounts 0 /
  1 / 7 / 31, addi .. andi with immediates 0 / 1 / -1 / 2047 / -2048 / 100 / -100; 22787 records, 980 draft-B reference
  compares, 0 mismatches). The first muldiv run timed out on the test's 20000-cycle tohost window (the divides take 37 cycles
  each): the retire target was raised so the window opens near the program's end; not a TB defect.
- Proof: gen_fcov_proof_slice1.fcov.yaml (128 coverpoint bins of mul / div / alu_reg) on the muldiv run's urg report: `PASS --
  all 128 declared bins hit` (gen_fu_l3_slice1_check.log); gen_fcov_proof_slice1b.fcov.yaml (122 bins of zba_zbb / alu_imm /
  shift) on the alu run's report: `PASS -- all 122 declared bins hit`. Cross coverage from urg's per-cross summary (User Defined
  Cross Bins expected / covered): mul cr_extremes 245/245, cr_op_rs1 45/45, cr_op_rs2 45/45, cr_op_sign 20/20, cr_op_rd_x0 9/9,
  cr_funct3_rd_x0 8/8, cr_op_same 15/18; div cr_op_divisor 40/40, cr_op_dividend 36/36, cr_div0 36/36, cr_overflow 4/4,
  cr_op_sign 16/16, cr_op_rd_x0 8/8; alu_reg cr_op_rs1 49/49, cr_op_rs2 49/49, cr_slt_boundary 98/98, cr_op_sign 28/28,
  cr_op_eq 14/14, cr_op_rd_x0 14/14, cr_wrap 7/7, cr_op_same 23/35; zba_zbb cr_op_rs1 160/160, cr_op_rs2 91/91, cr_op_eq 26/26,
  cr_minmax_sign 16/16, cr_shadd_wrap 6/6, cr_op_rd_x0 21/32, cr_op_same 21/42; alu_imm cr_op_imm 42/42, cr_op_rs1 42/42,
  cr_slt 9/9, cr_op_rd_x0 12/12; shift cr_op_operand 36/36, cr_op_shamt 24/24, cr_reg_upper 21/21, cr_sra_sign 8/8,
  cr_op_rd_x0 11/12. The uncovered cross bins are register-relation and rd = x0 tuples the operand walk does not form (the Test
  Writer's tests own them). Every bin the 15 promoted manifests reference for these six groups (1500) exists by name in the
  rendered include (checked by script against gen_fcov_groups.svh).
- Red: the same muldiv run with `+gen_fcov_en=0` on a fresh vdb: no covergroup instance, urg writes no grpinfo.txt, the checker
  fails with `PROTOCOL ERROR: grpinfo.txt: missing` (gen_fu_l3_nofcov_check.log): round 0's failure shape reproduced and
  removed by the groups' existence. A first attempt reused the build's vdb and passed on the previous run's data: one vdb per
  proof run from then on (the flow isolates runs by -cm_name; the local driver deletes the vdb before a proof run).
- Mutant FM1 (the sampler never decodes c.mul from its 16-bit form; the trap rtl-arch's anchors warn of): build a65d88c23c734972,
  the muldiv run PASSES the simulation, the checker on gen_fcov_proof_slice1.fcov.yaml FAILS naming
  `gen_mul_ops_cg.cp_op.c_mul = UNHIT (count=0)` (gen_fu_l3_FM1_*); ablation: the manifest without the c_mul bins passes.
- Finding for the flow (LOG-054): `ci/check_fcov_expectations.py` parses only `Summary for Variable` sections, so every cross bin
  the manifests declare is MISSING-FROM-REPORT although urg covers it (probe: `gen_mul_ops_cg.cr_op_rd_x0.mul_no =
  MISSING-FROM-REPORT` beside `cp_op.mul = HIT (count=185)`); urg's cross tables list component tuples, which the manifests'
  `_`-joined names are one to one. Reported with the fix; Runtime derives the variable form.
