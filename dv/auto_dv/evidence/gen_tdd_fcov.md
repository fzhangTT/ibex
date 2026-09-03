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
  named tuples (`cr_overflow.div_intmin_m1{div, int_min, all_ones}`). Six groups render to 1653 named bins (250 coverpoint
  bins, 1403 cross bins; the renderer's first summary line counted cross bins only and called them named bins, corrected). VCS refused the first include on `bins xor` (a keyword): keyword bins render as escaped identifiers
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

## 2. Slice 2: gen_bit_count_cg, gen_cmp_zca_cg, gen_cmp_zcmp_pushpop_cg

- Renderer: a coverpoint the trace CSV does not list (operand-only, counted in an adopted group) but a cross references
  (`cp_reg3` of CG-CMP-001) now renders from the plan line; the unit test still passes. Nine groups render to 2510 named bins (466 coverpoint bins, 2044 cross bins;
  gen_fu_l4_ut_fcov_codegen.log).
- Builds (wit_root): i bf213aa0edb01c6a (bit_count, zca), j 33ee96f28834a162 (+ the push/pop collector; the landed sources).
- gen_bit_count_cg: gen_bitcnt_directed.S (the operand classes, a walking one over all 32 positions, rd = x0 variants; 214
  samples), gen_fcov_proof_slice2a.fcov.yaml `PASS -- all 52 declared bins hit` (gen_fu_l4_slice2a_check.log).
- gen_cmp_zca_cg: the existing programs left c.lw, c.jal, c.jr, c.jalr, c.swsp and the x1 destination unhit (zc: 19 of 46,
  seed-7: 39 of 46), so gen_zca_directed.S runs every form at a word- and a half-aligned pc, each followed by a 16-bit and a
  32-bit instruction, the 3-bit field over x8..x15, the 5-bit field over x1 / x2 / x3..x7 / x8..x15 / x16..x31, branches taken and
  not, and one 32-bit instruction at a half-aligned pc (439 records, 0 mismatches, 344 Zca samples); gen_fcov_proof_slice2b.fcov.yaml
  `PASS -- all 46 declared bins hit` (gen_fu_l4_slice2b_check.log).
- gen_cmp_zcmp_pushpop_cg: gen_zcmp_directed.S (push / pop pairs over every rlist 4..15 and spimm 0..3, popret and popretz as
  function tails with word- and half-aligned return addresses and one odd one; 290 sequences, 517-519 records, 0 mismatches under
  the short, min1, long and random dmem regimes: gen_fu_l4_lockstep_zcmp{,_min1,_long,_random}_*); every cross of cr_insn_rlist_spimm
  (192 / 192) and cr_popret_r4 (2 / 2) covered, cr_insn_delay 4 / 16 per regime run (one delay class per run, all four classes
  across the runs), cr_ret_align 3 / 6 (the pop-family word / half / odd), cr_insn_sp_align 10 / 16; gen_fcov_proof_slice2c.fcov.yaml
  declares the 38 coverpoint bins the short-regime run hits: `PASS -- all 38 declared bins hit` (gen_fu_l4_slice2c_check.log). Not
  declared and why: cp_sp_wrap push_below_zero / pop_above_max (a stack wrapping the address space reads unmapped memory), the
  other three delay classes (one regime per run, hit in the retained min1 / long / random runs), cp_sp_align mis1..mis3 (hit by
  gen_zcmp_misaligned_directed.S, 6 sequences, 0 mismatches: gen_fu_l4_lockstep_zcmp_mis_*), cp_dummy_en.on (below).
- FINDING (plan B8, TP-CMP-065 "dummy mid-Zcmp skips a micro-op, needs repro"): gen_zcmp_dummy_directed.S (four push / pop pairs
  after `csrs 0x7C0, 4`) fails the comparator on 27 rows: `isa_mem Zcmp stores: model 1, dut 2` on the first push, `Zcmp loads:
  model 1, dut 2`, `stores: model 5, dut 6`, `loads: model 5, dut 7`, `isa_rd Zcmp union: x18 model=33333333 dut=00000000`; the
  export shows the rlist-12 pop emitting load micro-op records for x27, x26, x24, x22, x21, x20, x18, x8 only (x25, x23, x19,
  x9, x1 absent) with x18 loaded wrong, every micro-op still tagged expanded_insn_valid and the sp-adjust tagged _last. The same
  pairs without the csrs are clean, so the trigger is dummy insertion inside a Zcmp expansion. Reported to the Orchestrator at
  18:56Z; retained gen_fu_l4_lockstep_zcmp_dummy_* (verdict, header, excerpt, the export). A first reading of the first red run
  blamed the misaligned-sp pairs that preceded the dummy stretch in the same program; splitting the program into three showed
  the misaligned pairs clean and the dummy pairs red (recorded so the two programs' names make sense).
- Sampler mutants (gen_mut_fcov.md): FM2 (every Zca successor reported 16-bit) and FM3 (cm.pop sampled as cm.push), each caught by the
  checker on the slice's proof manifest with the run itself passing.
- CM51-MAJ-1 (the landing-3 review's major): `rs1 == logic'(32'(imm))` cast the sign-extended immediate to one bit, so `cp_slt_case.eq`
  fired on `rs1 == imm[0]`; fixed to `rs1 == 32'(imm)` and the sampler audited (no other `logic'(` cast). On the corrected sampler
  (build k 893384b8eec4e6d5) the alu run counts eq 84, slti_intmin_0 14, slti_0_neg 56, sltiu_imm_m1 182, sltiu_seqz 588,
  sltiu_ones_m1 14, other 2590 (gen_fu_l4_urg_slice1b_grpinfo.txt); mutant FM4 re-introduces the cast and counts eq 168 / other 2506
  while the checker still passes (gen_mut_fcov.md: a bin hit too often is not a miss).
- Landed sources: build k 893384b8eec4e6d5 (the slt fix, the opcode enums, the abandoned-sequence count, the yaml derivation of the drain
  window): every proof run re-done on it (bitcnt, zca, zcmp under four regimes, zcmp_mis, zcmp_dummy red, muldiv, alu, zcmp_irq_sparse)
  and the five proof manifests PASS (gen_fu_l4_k_driver.log).

## 3. Slice 3: gen_cmp_zcmp_mv_cg, gen_csr_trap_setup_warl_cg, gen_isa_branch_cg

Ranks 8, 9 and 10 of evidence/gen_round0_covergroup_set.md. Anchors: rtl-arch gen_cg_sampling_anchors.md sections 8-10. Builds: l
(2935ce47b627e0d5, the first green set) and m (86c7caf1d034cdec, the landed sources: the load decode of the hazard tracker, the
mtvec patterns, `option.cross_auto_bin_max = 0`); the retained logs are the build-m runs (gen_tdd_logs/fcov/gen_fu_l5_*).

- Renderer: the plan's cross lines for CG-CSR-002 name their tuples space-separated (`mstatus_csrrw{mstatus csrrw}`) and by bit value
  (`all0{0 0 0 0}` over four 1-bit coverpoints); the tuple parser now splits on commas or spaces and maps a value part to the `b<value>`
  bin (unit-test cases added, GEN_UT_FCOV_CODEGEN PASS). Red first: with the three ids in IMPLEMENTED the renderer refused
  `CG-CSR-002.cr_csr_wpat.misa_illegal: does not split` (comma-only tuples) and then `cr_mst_fields.all0` (value tuples) before the fix.
  Rendered: 12 covergroups, 619 coverpoint bins, 2501 cross bins (the three groups: 28 / 180, 29 / 134, 67 / 143).
- Automatic cross bins: the build-l reports showed bracketed auto bins beside the named ones (`[c_bnez]_[yes]_[equal]`, the tuples the
  plan ignores; 52 of them in the slice-1 report too), because a cross with user bins still auto-creates bins for the remaining tuples.
  `option.cross_auto_bin_max = 0` in every rendered group removes them: 0 bracketed bins in every build-m report, the earlier five
  proof manifests still PASS on build m (128 / 122 / 52 / 46 / 38 bins: gen_fu_l5_slice1_check.log ... slice2c).
- Programs (all lock-step PASS on build m, 0 UVM_ERROR): gen_branch_directed.S (218 branch samples: 6 ops x 10 operand pairs x
  forward / backward / half-aligned, c.beqz / c.bnez x 5 values x 3 forms, the four maximal offsets), gen_zcmp_mv_directed.S (130 move
  pairs: every cm.mva01s pair, every legal cm.mvsa01 pair, back to back both ways, load / ALU writers), gen_csr_warl_directed.S (214
  write / read-back pairs, 0 replaced; the same program under +gen_knob_mcounteren_writable=off and =invalid). Red first for the branch
  program: build l counted 26 of 28 coverpoint bins; `cp_offset.max_fwd` was unhit because the assembler had widened the four
  maximal forward branches (beq / bne +4094 emitted as `bne + jal`, c.beqz / c.bnez +254 as 32-bit branches at +256), and
  `cr_op_align.c_bnez_word` because `.balign 4` under `.option norvc` cannot pad by two bytes and left the code misaligned; the program
  now emits the maximal branches as raw words (`.word 0x7e628fe3`, `.2byte 0xcc7d`), aligns with rvc enabled for the directive and
  runs with `.option norelax` (the disassembly checked: every 32-bit branch at a word address, targets +6 half / +8 word / -4 word for
  the CB forms, offsets 4094 / -4096 / 254 / -256 present). Red first for the move program: `cp_hazard_src.alu_prev` was unhit on
  build l because the tracker took rvfi_mem_rmask != 0 as "the previous instruction was a load", and Ibex reports a non-zero rmask on
  non-memory records too (the B8 export shows `csrs` with rmask f); the tracker now decodes the instruction (gen_insn_mem_access).
  Red first for the CSR program: `cr_mtvec_mode_lo.v01_nz` and `cr_mtvec_base_op.high_csrrs` were unhit (no pattern with mode 01 and
  a non-zero [7:2]; `csrrs 0x80000000` from 0 lands on the boot page, not `high`); patterns 0x80000105 and `csrrs 0x90000000` added.
- Proofs (gen_fu_l5_*_check.log, each on the run's own fresh vdb): gen_fcov_proof_slice3a.fcov.yaml PASS 27 bins (every coverpoint bin
  but cp_offset.self); slice3b PASS 29 bins (every coverpoint bin); slice3c PASS 65 bins, slice3c_off and slice3c_inv PASS 65 each
  (cp_mcen_gate.off / .invalid in place of .on). Cross coverage from urg's per-cross summaries: gen_isa_branch_cg 140 / 180 (the 40
  unhit are the 16 `self` tuples and the maximal offsets of the six ops not exercised at the limit: only beq / bne / c.beqz / c.bnez
  branch by +-max), gen_cmp_zcmp_mv_cg 133 / 134 (cm_mvsa01_yes, below), gen_csr_trap_setup_warl_cg 137 / 143 in the On run
  (misa_legal / misa_illegal unreachable by construction; the four off / invalid gate tuples hit in the other two runs: 2 / 11 each).
- FINDING (B4, zcmp.adoc norm:cm-mvsa01_res): gen_zcmp_mv_reserved_directed.S executes one cm.mvsa01 with r1s' == r2s'. Ibex retires
  two moves into s0 (the record shows rd = x8 written with a1's value), the Spike model raises an illegal instruction (tools/riscv-isa-sim/
  riscv/insns/cm_mvsa01.h `require(insn.rvc_r1sc() != insn.rvc_r2sc())`), and the comparator flags the record (`isa_trap dut retired,
  model retired 0 trap=1 cause=00000002 tval=0000ac22`, then isa_rd / isa_pc_next; 32 UVM_ERROR rows, the model's pc parked at the
  handler). Retained gen_fu_l5_lockstep_zcmp_mv_res_* (verdict, header, excerpt, export). The promoted manifest gen_test_cmp_zcmp_basic
  declares cr_insn_equal.cm_mvsa01_yes, which no lock-step run can hit; reported to the Orchestrator 19:56Z. Ruling B4-R1 (DV Lead,
  gen_bug_log.md): the bin is TP-CMP-051's alone (an expected-fail test of its own), leaves the pass test's manifest with the Test
  Writer's re-render, and the TB does not adopt the RTL behaviour as its reference (a shim override refused, comparators-off refused).
- Sampler mutants (gen_mut_fcov.md): FM5 (c.bnez sampled as c.beqz), FM6 (the writer before a move never seen), FM7 (the immediate CSR
  forms sampled as the register forms), each built from the landed sampler and caught by the checker on the slice's proof manifest
  with the run itself passing (1, 2 and 3 unhit bins named).
- Testlist entries for Runtime: dv/auto_dv/work/tb-infra/gen_l5_testlist_entries.yaml (the three lock-step runs and the B4 red as expected_fail).
