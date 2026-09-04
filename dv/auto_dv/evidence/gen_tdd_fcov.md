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
  (`cp_reg3` of CG-CMP-001) now renders from the plan line; the unit test still passes. Nine groups render to 2439 named bins (395 coverpoint bins, 2044 cross bins; the landing-4 record said 466 coverpoint bins because the renderer's summary counted the 71 `ignore_bins na` too, gen_critic_tb_l4.md L-1;
  gen_fu_l4_ut_fcov_codegen.log).
- Builds (wit_root): i bf213aa0edb01c6a (bit_count, zca), j 33ee96f28834a162 (+ the push/pop collector), k 893384b8eec4e6d5 (the landed sources of landing 4; the earlier wording named j, gen_critic_tb_l4.md L-2).
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
  export shows the rlist-15 pop (pc 80000108) emitting load micro-op records for x27, x26, x24, x22, x21, x20, x18, x8 only (x25, x23,
  x19, x9, x1 absent) with x18 loaded wrong, and the rlist-12 pop (pc 80000104) replaying from its first load after a lost sp adjust
  (gen_b8_row_mapping.md rows 6 and 8; an earlier wording attributed the eight-record list to the rlist-12 pop, CM74-M-3), every micro-op still tagged expanded_insn_valid and the sp-adjust tagged _last. The same
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
  Withdrawn (gen_critic_tb_l4.md M-2): the landing-4 commit subject said "the sampler unit test carries that check"; no sampler unit test
  existed at that landing. gen_ut_isa_cov (Section 5, landing 6) is that test and carries the eq count, the minstret delta and the rd = x0 result class.
- Landed sources: build k 893384b8eec4e6d5 (the slt fix, the opcode enums, the abandoned-sequence count, the yaml derivation of the drain
  window): every proof run re-done on it (bitcnt, zca, zcmp under four regimes, zcmp_mis, zcmp_dummy red, muldiv, alu, zcmp_irq_sparse)
  and the five proof manifests PASS (gen_fu_l4_k_driver.log).

## 3. Slice 3: gen_cmp_zcmp_mv_cg, gen_csr_trap_setup_warl_cg, gen_isa_branch_cg

The covergroups gen_cmp_zcmp_mv_cg (CG-CMP-007), gen_csr_trap_setup_warl_cg (CG-CSR-002) and gen_isa_branch_cg (CG-ISA-007) of evidence/gen_round0_covergroup_set.md; anchors rtl-arch gen_cg_sampling_anchors.md sections 8-10. Builds: l
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
  pairs: every cm.mva01s pair, every legal cm.mvsa01 pair, back to back both ways, load / ALU writers), gen_csr_warl_directed.S (215
  write / read-back pairs after the two mtvec patterns were added, 0 replaced; the same program under +gen_knob_mcounteren_writable=off and =invalid). Red first for the branch
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

## 4. Slice 4a: gen_bit_sbit_cg, gen_cmp_zcb_cg

The covergroups gen_bit_sbit_cg (CG-BIT-006) and gen_cmp_zcb_cg (CG-CMP-005); anchors sections 14 and 16. Programs gen_sbit_directed.S (182 records: 4 register ops x 4 indices x 6 operand /
rs2 forms, 4 immediate ops x 4 x 5, three binv-twice pairs) and gen_zcb_directed.S (71 records: every Zcb form, both data signs,
aligned / off-by-one / word-crossing half-word accesses, five ALU operand classes, c.mul with distinct and equal registers over the
operand classes). Red first: the first Zcb program put the data in s2 / s3 / s4 where the compressed register fields 2..4 are a0 / a1 /
a2, so every load read 0 (cp_data_sign.neg unhit, cr_load_sign 3 of 6; that report was not retained and the pre-fix program was
not kept, so this red is narrated only, tb_l6 L-7); the registers were corrected. Proofs (build s retained as gen_fu_l6_*, first run on build q, own vdb each):
gen_fcov_proof_slice4a.fcov.yaml PASS 22 bins (every coverpoint bin), slice4b PASS 29 bins (every coverpoint bin but cp_alu_operand.rand,
unreachable by construction). Cross coverage: gen_bit_sbit_cg 100 / 100; gen_cmp_zcb_cg 59 / 65 (the six c_mul x rand and ALU x rand
tuples). Mutants FM8 / FM9 caught with ablation controls (gen_mut_fcov.md).

## 5. Landing-4 re-review fixes (gen_critic_tb_l4.md) and the sampler unit test (LOG-058)

Build q e0ed7268dea314ef carried the fixes first; the retained gen_fu_l6_*_check.log are the build-s re-runs, on which every earlier
proof manifest passes unchanged (128 / 122 / 52 / 46 / 38 / 26 / 29 / 65 / 65 / 65 / 22 / 29; the slice-3a count is 26 after the
L5R-1 wrap ruling removed cp_wrap.yes, 27 was the pre-ruling count), so no bin the proofs declared depended on the wrong mechanisms.
- H-1(a) cp_minstret_once: red = the landing-4 report (gen_fu_l4_urg_lockstep_zcmp_grpinfo.txt, yes 193 of 290: the sequences preceded
  by a 16-bit instruction); the sample now waits for the record after the sequence and takes that record's counter minus the first
  micro-op record's: yes 290 of 290 in the short, min1, long and random runs, `minstret_once no 0` on every summary line
  (gen_fu_l6_urg_lockstep_zcmp*_grpinfo.txt); the synthetic sequences of the vector table give yes and na as designed.
- H-1(b) result classes on rd = x0: red = the landing-4 bit-count report (cp_result.r0 102 of 214); now r0 = 11 (the genuine zero
  results) with cp_rd_x0.yes = 91 (gen_fu_l6_urg_lockstep_bitcnt_grpinfo.txt); every group's result class is na on x0.
- H-1(c) micro-ops in the base groups: red = alu_imm 354 on the zcmp run (landing 4); now 16, the program's own OP-IMM count
  (gen_fu_l6_lockstep_zcmp_stdout_excerpt.log).
- M-3 cp_dmem_delay from observed latencies: the random-regime run scores mixed 147, long 137, short 4, min1 2 (knob mapping: mixed
  290); short 290 / min1 290 / long 290 in the fixed regimes (gen_fu_l6_urg_lockstep_zcmp_random_grpinfo.txt and siblings).
- The landing-3 deferred defects: |divisor| from the sign-extended value, addi_wrap from the operands (vector table rows).
- gen_ut_isa_cov (dv/auto_dv/gen_tb/gen_tests/gen_ut_isa_cov.py; FCOV_SELFTEST, FCOV_QUERY): five runs PASS (gen_fu_l6_ut_isa_cov_*):
  the vector table 18 cases 0 failures in each (27 since the tb_l6 M-2 / M-3 cases, Section 6); FCOV_QUERY slt eq = 84 on gen_alu_directed.S, Zcmp sequences = 290 and minstret misses = 0
  on gen_zcmp_directed.S, rd = x0 bit-count records = 91 on gen_bitcnt_directed.S. Red first: the vector table was written against the
  corrected classifiers; its rows for the old expressions (eq on the 1-bit cast, |x| of a zero-extended negative, addi_wrap from
  rd_wdata, minstret from the predecessor) are the landing-3 / landing-4 reports quoted above.
- Renderer: the summary counts named bins only (the `ignore_bins na` are 114 across 14 groups); the operand-only exemption is gated
  on the plan's `[operand-only:` marker; unit-test cases added (GEN_UT_FCOV_CODEGEN PASS, gen_fu_l6_ut_fcov_codegen.log).
- Mutants FM2, FM3, FM5-FM9 re-run from the landed sampler with ablation manifests (gen_mut_fcov.md).
- The landing-5 cross-model review's second high (the Zcmp sreg field): the move-pair sampler mapped the 3-bit field as x(8 + r) where the
  encoding is s0 = x8, s1 = x9, s2..s7 = x18..x23, so the micro-op check passed only for pairs over s0 / s1 and the hazard sources were the
  wrong registers. Red = the build-q report (gen_fu_l6_urg_red_q_lockstep_zcmp_mv_grpinfo.txt: cp_uop_count_ok.yes 10 of 130, cp_hazard_src
  alu_prev 33 / load_prev 2 / none 95); green = build r (gen_fu_l6_urg_lockstep_zcmp_mv_grpinfo.txt: cp_uop_count_ok.yes 130 of 130,
  load_prev 2, alu_prev 6: addi s2 before mva01s 2, 3; addi a1 before mvsa01 2, 3; the three `li a1` writers that precede the first
  cm.mvsa01 of a block; and mvsa01 6, 7 after mva01s 4, 5 wrote a0 / a1).
  The vector table carries a synthetic cm.mva01s s7, s6 whose micro-ops read x23 and x22.
- The slice-3 reds are retained with this landing (the landing-5 review's third medium): gen_fu_l6_urg_red_l_lockstep_branch_grpinfo.txt
  (checker FAIL: cp_offset.max_fwd), gen_fu_l6_urg_red_l_lockstep_zcmp_mv_grpinfo.txt (FAIL: cp_hazard_src.alu_prev),
  gen_fu_l6_urg_red_l_lockstep_csrwarl_grpinfo.txt (the coverpoint manifest passes on it; the red rows are the cross tuples
  cr_mtvec_mode_lo.v01_nz and cr_mtvec_base_op.high_csrrs, 0 in that report).
- Landing 6 build: r de523e6e878f325b (the sreg fix, the ibex_pkg constants, GEN_BUS_ERR_DRAIN_CYCLES 96; the mtvec low threshold was already the whole-value test at
  f660470 and only its statement changed); every
  proof, unit-test run and mutant below was re-run on it.
- The DV Lead's rulings on the review questions, applied in the landing-6 build: cp_wrap is the address-space wrap (L5R-1: the 33-bit
  signed target outside [0, 2^32)), so the branch proof declares 26 coverpoint bins (cp_wrap.yes is reachable only near the ends of the
  map); cp_mtvec_base_w.low is the whole-value threshold (L5R-2); cp_mcen_gate reads mcounteren_writable_i from the ctrl interface at the
  write record (TP-PMC-057 moves the pin inside a run); HINT encodings count by form (TBQ-L4-1); the result classes are na on rd = x0
  (TBQ-L4-2). Report-phase referee GEN_FCOV_REF: a group the sampler fed must show coverage (gen_critic_tb_l3.md L-6).
- Landing 6 final build: s 9f123de2aa16eb21 (the DV Lead's three rulings, the ctrl-interface tap for cp_mcen_gate, the GEN_FCOV_REF
  referee, the renderer's nested-brace values); every proof re-run on it with its manifest regenerated from its own report and an
  anti_vacuity note per bin (gen_critic_tb_l3.md L-7): slice1 128, slice1b 122, slice2a 52, slice2b 46, slice2c 38, slice3a 26 (cp_wrap.yes
  no longer reachable under L5R-1), slice3b 29, slice3c 65 with the gate bins now from the pin (on / off / invalid in the three runs),
  slice4a 22, slice4b 29 (gen_fu_l6_*_check.log). The fcov-off red (gen_critic_tb_l3.md M-2) is a real run: lockstep_muldiv_nofcov with
  +gen_fcov_en=0 on its own fresh vdb; urg writes no grpinfo.txt for it (gen_fu_l6_urg_lockstep_muldiv_nofcov.cmd.txt names the vdb) and
  the checker on the slice-1 manifest fails with a protocol error, no report (gen_fu_l6_nofcov_check.log). Every mutant FM1-FM9 is built
  from this sampler (blob 68ba3dfd8d3c4205) with its ablation control (gen_mut_fcov.md).

## 6. Landing 7: the Critic's landing-6 review (gen_critic_tb_l6.md) answered

Build x a48917a3f74eeea3 (wit_root, out of tree; the per-file list gen_fu_l8_sources_sha256_x.txt). Code: the move-pair miss counter and
its GEN_FCOV_REF line, the unit-test cases, the |INT_MIN| comment, the binv tracker's reset on trap records (gen_fcov_pkg.sv); the
option-line case in gen_ut_fcov_codegen.py; the anti_vacuity notes of all 20 manifests derived from the plan's Sample lines.
- Reds: FM10 (the branch group counted, never sampled: `gen_isa_branch_cg sampled without coverage`, ablation PASS) and FM11 (the
  cm.mva01s expansion expected with swapped registers: 68 counted misses, the referee's error, ablation PASS), gen_mut_fcov.md; the
  vector case "cm.mva01s with a wrong second micro-op" (uop_count_ok na, one counted miss) inside the self-test.
- Greens on x: gen_fu_l8_ut_isa_cov_* (five runs, 27 cases, 0 failures; the zc run's report line `move pairs: 5 sampled, 1 with
  mismatching micro-ops (1 of them the self-test's)`, the other four `3 sampled`: the program's own pairs plus the self-test's three), boot_zc, lockstep_zc, ut_witness, lockstep_muldiv_nofcov; the codegen unit test 19
  OK (gen_fu_l8_ut_fcov_codegen.log).
- lockstep_zcmp_dummy_popret also ran on x and FAILED as designed (9408 errors, the B8 red of gen_tdd_step2b.md Section 11;
  gen_fu_l8_x_driver.log).
- Proofs re-run on x, fresh vdb each, the manifests with the derived notes: 128 / 122 / 52 / 46 / 38 / 26 / 29 / 65 / 65 / 65 / 22 / 29,
  every one PASS (gen_fu_l8_<slice>_check.log, urg reports gen_fu_l8_urg_<run>_grpinfo.txt with their commands); lockstep_zcmp_mv on x
  reports `move pairs: 130 sampled, 0 with mismatching micro-ops`.
- M-1 (source identity): build s and the committed 61c97c1 differ in dv/auto_dv/tb/gen_fcov_codegen.py and
  dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py only (gen_fu_l6_sources_sha256_s.txt against gen_fu_l6_sources_sha256_committed.txt);
  neither is compiled and the rendered include is identical, so the landing-6 proofs stand; the lists are retained from now on.
- Record corrections (L-1) are in Sections 4 and 5 above and in gen_mut_fcov.md; the response rows are the CR-6 table in
  gen_critic_response_fcov.md, with the CR-5 rows the tb_l5 lows lacked (L-5).

## 7. Landing 9: the cross-model review of landing 7 (ab67c6c) answered

Build aa 4bc32b82a3b03340. gen_fcov_pkg.sv: `ut_mv_miss_expected` advances by exactly the vector case's own miss (`+= n_mv_miss - miss0`),
so a real miss during a unit-test run's program is not absorbed and the referee can fire in that run too; the `GEN_FCOV_REF` referee now
covers every counted group (mul, div, alu_reg, zba_zbb, alu_imm, shift, bit_count, zca, zcmp, zcmp_mv, csr, branch, sbit, zcb: a non-zero
sampler counter with zero coverage is an error). The unit test's own red on the FM4 build (the Critic's widened M-3): gen_ut_isa_cov on
the FM4 mutant (the 1-bit slt cast re-introduced) FAILS its vector table, `slti rs1 == imm is eq ... 6 expected 0`, 27 cases 1 failure
(gen_fu_l10_FM4UT_catch_ut_isa_cov_zc_*); the same with `+gen_fcov_en=0` FAILS identically, because the vector table judges the classifier
function, not the covergroup (gen_fu_l10_FM4UT_ablate_ut_isa_cov_zc_*: the "ablation" of a unit test is not a PASS, and is retained to
show that). Record corrections: 1059 notes, the five excerpt headers say 27 cases, the "5 sampled" quote is the zc run's with the other
four qualified, FM10's first compile failure is explained, the by-design popret red on x is stated. Greens on aa: ut_isa_cov_zc, ut_witness,
lockstep_zcmp_mv, boot_zc, lockstep_zc (gen_fu_l10_*).
