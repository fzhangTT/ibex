# Functional-coverage plan - Ibex core, opentitan configuration

Deliverable 3 (DV_prompt.txt Section 11): the definition of every functional-coverage bin (not the
implementation; TB Infra implements covergroups in the gen_ namespace from this plan). Owner: dv-lead.
Version 1, generated 2026-09-03 06:56 UTC from dv/auto_dv/work/dv-lead/parts6/fcov_*.md.

Build configuration: `opentitan` (ibex_configs.yaml): BaseIsa=RV32IorCHERIoT (CHERIoT mode excluded
by owner ruling), RV32E=0, RV32M=RV32MSingleCycle, RV32B=RV32BOTEarlGrey, RV32ZC=RV32ZcaZcbZcmp,
RegFile=RegFileFF, BranchTargetALU=1, WritebackStage=1, ICache=1, ICacheECC=1, ICacheScramble=1,
BranchPredictor=0, DbgTriggerEn=1, SecureIbex=1, PMPEnable=1, PMPGranularity=0, PMPNumRegions=16,
MHPMCounterNum=10, MHPMCounterWidth=32.

DUT: `gen_dut_top` = `ibex_core` + `ibex_register_file_ff` (DV_prompt.txt Section 2 rulings); `ibex_top`
is not the DUT. Wrapper parameters (owner question Q-002 defaults, pending confirmation): MemECC=1
(39-bit bus data), DummyInstructions=1, ICacheTweakInfection=1, ResetAll=1, RegFileECC=0
(RegFileDataWidth=32), DbgHwBreakNum=1, DmBaseAddr=0x1A110000, DmAddrMask=0xFFF,
DmHaltAddr=0x1A110800, DmExceptionAddr=0x1A110808, CsrMvendorId=CsrMimpId=0, PMP reset values from
ibex_pkg; compiled with +define+RVFI; cheriot_enable_i tied IbexMuBiOff inside the wrapper.

# 0. Conventions

- Covergroup ID `CG-<AREA>-<nnn>` with SystemVerilog name `gen_cg_<area>_<name>` (own namespace; never
  extends an RTL covergroup). Each block: Features (F-IDs it covers), Sample (event, condition and an
  anti-vacuity note stating why the sample is not always-true and what a hit proves), Coverpoints with
  named bins (ignore_bins carry a reason; transitions are enumerated explicitly, never
  `illegal_bins = default sequence`, SIM_RECIPE.md Section 9), Crosses, Adopted (riscv-dv) and the TP
  items that must hit it. Bin references have the form `CG-<AREA>-<nnn>.cp_<name>.<bin>` (cross bins
  `...cr_<name>.<bin>`).
- Counts and ranges derive from ibex_pkg parameters and the config (PMPNumRegions, MHPMCounterNum,
  IC_NUM_WAYS, IC_LINE_BEATS, irq_fast width), never re-typed literals.
- Three randomization layers are covered in Section REG (knob values, regime phases, knob transitions,
  regime change while an event is in flight); cross-interface crosses in Section XIF; bins adopted from
  riscv-dv's coverage model in Section ADOPT, marked "adopted" and counted separately.
- Probe candidates: bins that cannot be sampled from the boundary or RVFI name the internal net and
  the boundary alternative; every probe needs a probe-register entry (TB Infra) and Critic approval.
  Candidates so far: P1 dummy-instruction seam nets (dummy_instr_id_o / dummy_instr_wb_o, wrapper
  internal), P2 icache hit/miss view (tag RAM model first), P3 fetch-buffer occupancy, P4 controller FSM
  state (RTL fcov_* hooks), P5 register-file seam, P6/P7 CSR write-path nets (see the CSR part). No
  checker depends on a probe.

# 1. Completeness measure (definition; DV_prompt.txt Section 4)

1. Every ACTIVE feature maps to at least one TP item and at least one bin (directly or through an
   ALIAS/FOLDED ID that resolves to it). 2. Every bin maps back to a feature through its covergroup's
   Features field (all of which must be existing F-IDs). 3. Adopted bins (riscv-dv) are counted
   separately and do not substitute for spec-derived bins. 4. A reviewer other than the author (the
   Critic) confirms the mapping. 5. Per test, the declared bins (fcov-expectation manifest) must be hit
   in that test's own run; the check is pre-merge (ci/check_fcov_expectations.py). The script
   dv/auto_dv/tools/gen_trace_check.py evaluates 1-3 over gen_feature_list.md, gen_test_plan.md,
   gen_fcov_plan.md and the two CSVs and exits non-zero on any violation.

# 2. Counts

| Metric | Value |
|---|---|
| Covergroups | 204 |
| Distinct bins referenced by TP items | 10234 |
| Adopted bins (riscv-dv, counted separately) | 55 |
| ACTIVE features with >= 1 bin | 765 |
| Covergroups per area part | isa 40, csr 25, exc_irq 25, pmp 14, dbg_trg_pmc 22, mem_fetch_icache 30, sec_rst_rvfi_cheri 20, xcut 28 |

# 3. Covergroups by area

# 3.1 Areas ISA, MUL, CMP, BIT, BTALU: Instruction set: RV32I base, M (RV32MSingleCycle), compressed Zca/Zcb/Zcmp, bitmanip RV32BOTEarlGrey, branch target ALU


Scope: F-ISA-001..052, F-MUL-001..028, F-CMP-001..070, F-BIT-001..041, F-BTALU-001..015 (206
features: 172 ACTIVE, 16 ALIAS, 18 FOLDED; source dv/auto_dv/work/dv-lead/parts/gen_part_isa.md).
Features lines below may name ALIAS/FOLDED IDs; they resolve to the canonical / parent ID. Every
FOLDED feature names the bin of this file that carries it. Companion test plan: tp_isa.md. Build: opentitan (RV32IMC + RV32BOTEarlGrey + Zca/Zcb/Zcmp, BranchTargetALU=1,
WritebackStage=1, SecureIbex=1, DummyInstructions=1 per Q-002 defaults).

Conventions
- Every covergroup samples from a TB monitor transaction, never from a free-running clock. The
  primary event is the RVFI monitor's retirement transaction (one per rvfi_valid cycle: insn,
  pc_rdata, pc_wdata, trap, rs1/rs2/rs3 addr+rdata, rd addr+wdata, mem_*, ext_mcycle,
  ext_mhpmcounters, ext_expanded_insn*, mode). Operand classes are computed by the monitor from
  rvfi_rs*_rdata and the decoded immediate; "decoded" means decoded by the monitor's own table
  from rvfi_insn (never from an RTL net).
- Retire-to-retire cycle delta ("delta") = rvfi_ext_mcycle(this) - rvfi_ext_mcycle(previous
  retirement); the ibus monitor supplies fetch_stall (fetch data not available when the previous
  instruction retired) and the dbus monitor supplies wb_busy (a granted data access without
  response when this instruction entered ID, inferred from request/response timing).
- Programmable state (privilege, cpuctrlsts.data_ind_timing, dcsr.*, mstatus.TW, icache_enable)
  is tracked by the TB CSR model from the retired CSR writes on RVFI (predict-and-check), never
  probed.
- Bin syntax: `name{values}`; `auto{all combinations}` on a cross means every combination of
  the listed coverpoints is a required bin (the fcov-expectation manifest expands it to the
  auto-bin set urg reports). "iff" gives the per-coverpoint sampling guard.
- Class values used repeatedly: zero=0x00000000, all_ones=0xFFFFFFFF, int_min=0x80000000,
  int_max=0x7FFFFFFF, one=1, msb_only=0x80000000, lsb_only=1; pos_rand = any other value with
  bit 31 clear, neg_rand = any other value with bit 31 set.
- Counts derive from ibex_pkg / decoder tables: Zcmp rlist 4..15 and spimm 0..3 come from
  rtl/ibex_compressed_decoder.sv cm_stack_adj_base/cm_rlist_top_reg; the legal Zb* mnemonic
  list is the ENC table (dv/auto_dv/work/rtl-arch/gen_rv32b_otearlgrey_encodings.md); micro-op
  index range 0..15 is the popretz maximum (13 loads + addi + li + ret).
- Adopted bins: none in this file. vendor/google_riscv-dv/** was not read by this subagent (the
  brief limits it to the subagent whose task names it); see fcov "Open questions" in tp_isa.md.
- Never `illegal_bins = default sequence`; no transition bins are used in this file.

---------------------------------------------------------------------------------------------------
## AREA ISA

### CG-ISA-001: gen_cg_isa_alu_imm
- Features: F-ISA-001, F-ISA-002, F-ISA-003, F-ISA-004
- Sample: RVFI retirement; condition: decoded opcode == OP-IMM and funct3 in {000,010,011,100,110,111} and rvfi_trap == 0; anti-vacuity: rvfi_valid is a subset of cycles and the funct3 guard excludes shifts, loads, and every other class; a hit proves an I-type ALU op retired with the sampled operand/immediate class.
- Coverpoints:
  - cp_op = funct3: bins addi{000}, slti{010}, sltiu{011}, xori{100}, ori{110}, andi{111}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, pos_rand{[2:0x7FFFFFFE]}, neg_rand{[0x80000001:0xFFFFFFFE]}
  - cp_imm_class = class(sext(imm12)): bins zero{0}, plus1{1}, minus1{-1}, max_pos{2047}, min_neg{-2048}, pos_rand{[2:2046]}, neg_rand{[-2047:-2]}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_rs1_eq_rd = (rs1_addr == rd_addr and rd_addr != 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, other{default}
  - cp_addi_wrap = sign(rs1) == sign(imm) and sign(result) != sign(rs1), iff addi: bins pos_wrap{rs1 >= 0 and imm > 0 and result < 0}, neg_wrap{rs1 < 0 and imm < 0 and result >= 0}, none{otherwise}
  - cp_slt_case = boundary case, iff op in {slti, sltiu}: bins eq{rs1 == sext(imm)}, slti_intmin_0{slti and rs1 == 0x80000000 and imm == 0}, slti_0_neg{slti and rs1 == 0 and imm < 0}, sltiu_imm_m1{sltiu and imm == -1}, sltiu_seqz{sltiu and imm == 1}, sltiu_ones_m1{sltiu and rs1 == 0xFFFFFFFF and imm == -1}, other{default}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_imm = cp_op x cp_imm_class: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
  - cr_slt = cp_op x cp_slt_case: bins auto{all combinations}; ignore ops other than slti/sltiu: cp_slt_case is guarded to compares
- Adopted (riscv-dv): none
- TP items: TP-ISA-001, TP-ISA-002, TP-ISA-003, TP-ISA-004, TP-ISA-054

### CG-ISA-002: gen_cg_isa_alu_reg
- Features: F-ISA-007, F-ISA-008, F-ISA-009, F-ISA-004, F-ISA-051
- Sample: RVFI retirement; condition: decoded opcode == OP, funct7 in {0000000, 0100000}, funct3 in {000,010,011,100,110,111}, rvfi_trap == 0; anti-vacuity: excludes shifts (funct3 001/101), M (funct7 0000001) and Zb* funct7 values; a hit proves an R-type base ALU op retired with the sampled operand classes.
- Coverpoints:
  - cp_op = funct7/funct3: bins add{0000000/000}, sub{0100000/000}, slt{010}, sltu{011}, xor{100}, or{110}, and{111}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, pos_rand{[2:0x7FFFFFFE]}, neg_rand{[0x80000001:0xFFFFFFFE]}
  - cp_rs2_class = class(rvfi_rs2_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, pos_rand{[2:0x7FFFFFFE]}, neg_rand{[0x80000001:0xFFFFFFFE]}
  - cp_sign_pair = bit31 of rs1,rs2: bins pp{00}, pn{01}, np{10}, nn{11}
  - cp_eq_operands = (rs1_rdata == rs2_rdata): bins no{0}, yes{1}
  - cp_same_regs = register-index relation: bins rs1_eq_rs2{rs1 == rs2 != rd}, all_same{rs1 == rs2 == rd != 0}, rs1_eq_rd{rs1 == rd != rs2}, rs2_eq_rd{rs2 == rd != rs1}, distinct{all different}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, other{default}
  - cp_wrap = 33-bit carry/borrow and signed overflow, iff op in {add, sub}: bins add_carry{add and rs1 + rs2 >= 2^32}, add_pos_ovf{add and both operands >= 0 and result < 0}, add_neg_ovf{add and both operands < 0 and result >= 0}, sub_borrow{sub and rs1 <u rs2}, sub_ovf{sub and rs1 == 0x80000000 and rs2 > 0}, none{otherwise}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_rs2 = cp_op x cp_rs2_class: bins auto{all combinations}
  - cr_op_sign = cp_op x cp_sign_pair: bins auto{all combinations}
  - cr_op_eq = cp_op x cp_eq_operands: bins auto{all combinations}
  - cr_op_same = cp_op x cp_same_regs: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
  - cr_wrap = cp_op x cp_wrap: bins auto{all combinations}; ignore ops other than add/sub: cp_wrap is guarded
  - cr_slt_boundary = cp_op x cp_rs1_class x cp_rs2_class: bins auto{all combinations}; ignore ops other than slt/sltu: boundary semantics belong to compares
- Adopted (riscv-dv): none
- TP items: TP-ISA-007, TP-ISA-008, TP-ISA-009, TP-ISA-004, TP-ISA-052, TP-ISA-054

### CG-ISA-003: gen_cg_isa_shift
- Features: F-ISA-010, F-ISA-011, F-ISA-013, F-ISA-014, F-ISA-004
- Sample: RVFI retirement; condition: decoded slli/srli/srai (OP-IMM funct3 001/101, instr[31:25] in {0000000, 0100000}) or sll/srl/sra (OP funct7 0000000/0100000, funct3 001/101) and rvfi_trap == 0; anti-vacuity: the funct7 guard excludes every Zb* shift-space encoding; a hit proves a base shift retired with the sampled amount and operand class.
- Coverpoints:
  - cp_op = decoded: bins slli{OP-IMM 001}, srli{OP-IMM 101 f7 0}, srai{OP-IMM 101 f7 0100000}, sll{OP 001}, srl{OP 101 f7 0}, sra{OP 101 f7 0100000}
  - cp_shamt = effective amount (imm[4:0] or rs2[4:0]): bins s0{0}, s1{1}, mid{[2:30]}, s31{31}
  - cp_rs2_upper = rvfi_rs2_rdata, iff register form: bins zero{rs2[31:5] == 0}, is32{32}, is33{33}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, ffffffe0{0xFFFFFFE0}, other_nonzero{default}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, lsb_only{1}, neg_rand{bit31 set, not listed}, pos_rand{bit31 clear, not listed}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, one{1}, c0000000{0xC0000000}, other{default}
- Crosses:
  - cr_op_shamt = cp_op x cp_shamt: bins auto{all combinations}
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_reg_upper = cp_op x cp_rs2_upper: bins auto{all combinations}; ignore immediate ops: cp_rs2_upper is guarded to register forms
  - cr_sra_sign = cp_op x cp_operand x cp_shamt: bins srai_neg_31{srai, neg_rand, s31}, srai_pos_31{srai, pos_rand, s31}, srai_msb_1{srai, msb_only, s1}, sra_neg_31{sra, neg_rand, s31}, sra_pos_31{sra, pos_rand, s31}, sra_msb_1{sra, msb_only, s1}, srli_msb_31{srli, msb_only, s31}, slli_lsb_31{slli, lsb_only, s31}; ignore other combinations: covered by cr_op_shamt / cr_op_operand
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-ISA-010, TP-ISA-011, TP-ISA-013, TP-ISA-014, TP-ISA-004, TP-ISA-054

### CG-ISA-004: gen_cg_isa_lui_auipc
- Features: F-ISA-005, F-ISA-006, F-ISA-004
- Sample: RVFI retirement; condition: decoded opcode in {LUI, AUIPC}, rvfi_trap == 0; anti-vacuity: two opcodes out of the full program mix; a hit proves a U-type op retired at the sampled PC alignment/region with the sampled immediate.
- Coverpoints:
  - cp_op = opcode: bins lui{0110111}, auipc{0010111}
  - cp_imm20 = imm[31:12]: bins zero{0}, all_ones{0xFFFFF}, msb{0x80000}, one{1}, rand{default}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_pc_region = rvfi_pc_rdata: bins low{[0:0xFFF]}, high{[0xFFFFF000:0xFFFFFFFF]}, mid{default}
  - cp_wrap = carry out of pc + (imm << 12), iff auipc: bins no{0}, yes{1}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_op_imm = cp_op x cp_imm20: bins auto{all combinations}
  - cr_auipc_pc = cp_op x cp_pc_align x cp_wrap: bins auipc_word_nowrap{auipc, word, no}, auipc_half_nowrap{auipc, half, no}, auipc_word_wrap{auipc, word, yes}, auipc_half_wrap{auipc, half, yes}; ignore lui: no PC dependence
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-ISA-005, TP-ISA-006, TP-ISA-004, TP-ISA-054

### CG-ISA-005: gen_cg_isa_hint_x0
- Features: F-ISA-004, F-ISA-051
- Sample: RVFI retirement; condition: rvfi_rd_addr == 0 and the decoded instruction class normally writes rd (ALU/LUI/AUIPC/load/CSR/jump/M/Zb*), rvfi_trap == 0; anti-vacuity: most retirements have rd != 0 or are stores/branches; a hit proves an x0-destination instruction retired and (via cp_x0_read) that a later read of x0 returned 0.
- Coverpoints:
  - cp_hint_class = decoded: bins canonical_nop{addi x0,x0,0}, addi_x0_nzimm{addi x0,rs1,imm != 0 or rs1 != 0}, andi_x0{andi}, ori_x0{ori}, xori_x0{xori}, slti_x0{slti}, sltiu_x0{sltiu}, lui_x0{lui}, auipc_x0{auipc}, add_x0{add}, sub_x0{sub}, sll_x0{sll}, srl_x0{srl}, sra_x0{sra}, slt_x0{slt}, sltu_x0{sltu}, xor_x0{xor}, or_x0{or}, and_x0{and}, slli_x0_semihost{slli x0,x0,0x1f}, srai_x0_semihost{srai x0,x0,7}, slli_x0_other{other slli}, srli_x0{srli}, srai_x0_other{other srai}, other{default}
  - cp_writer_class = decoded class: bins alu_imm{OP-IMM non-shift}, shift{shifts}, alu_reg{OP base}, lui_auipc{U-type}, load{LOAD}, csrr{SYSTEM csr}, jal{JAL}, jalr{JALR}, mul{mul}, mulh{mulh/mulhsu/mulhu}, div_rem{div/divu/rem/remu}, bit_1cyc{single-cycle Zb*}, bit_2cyc{two-cycle Zb*}, zcb_alu{c.zext.b/c.sext.b/c.zext.h/c.sext.h/c.not/c.mul with rd x0 impossible: see ignore}, cmp_hint{c.li/c.lui/c.slli/c.mv/c.add with rd x0}; ignore_bins zcb_alu: Zcb ALU forms address x8..x15 only
  - cp_x0_read = the next retirement reads x0 (rs1_addr == 0 or rs2_addr == 0) with rdata 0: bins rs1_zero{rs1_addr == 0 and rs1_rdata == 0}, rs2_zero{rs2_addr == 0 and rs2_rdata == 0}, none{default}
- Crosses:
  - cr_writer_read = cp_writer_class x cp_x0_read: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-ISA-004, TP-ISA-052, TP-MUL-026, TP-BIT-038, TP-CMP-013, TP-CMP-025, TP-CMP-027, TP-CMP-031

### CG-ISA-006: gen_cg_isa_jump
- Features: F-ISA-015, F-ISA-016, F-ISA-017, F-ISA-018, F-ISA-019, F-ISA-020, F-ISA-021, F-ISA-022, F-ISA-052
- Sample: RVFI retirement; condition: decoded jal/jalr/c.j/c.jal/c.jr/c.jalr and rvfi_trap == 0; anti-vacuity: jumps are a small fraction of retirements; a hit proves a jump retired with the sampled offset/target class and (pc_wdata) redirect.
- Coverpoints:
  - cp_op = decoded: bins jal{JAL}, jalr{JALR f3 000}, c_j{c.j}, c_jal{c.jal}, c_jr{c.jr}, c_jalr{c.jalr}
  - cp_rd_class = rvfi_rd_addr, iff jal/jalr: bins x0{0}, x1{1}, x5{5}, other{default}
  - cp_jal_off = sext(imm_j), iff jal: bins self{0}, max_fwd{0xFFFFE}, max_bwd{-0x100000}, pos_rand{[2:0xFFFFC]}, neg_rand{[-0xFFFFE:-2]}
  - cp_jalr_imm = sext(imm_i), iff jalr: bins zero{0}, max_pos{2047}, min_neg{-2048}, odd{imm[0] == 1}, pos_rand{even [2:2046]}, neg_rand{even [-2046:-2]}
  - cp_jalr_rs1 = rs1 relation, iff jalr/c.jr/c.jalr: bins x0{rs1_addr == 0}, eq_rd{rs1_addr == rd_addr != 0}, other{default}
  - cp_target_align = target[1] (rvfi_pc_wdata with bit 0 masked): bins word{0}, half{1}
  - cp_target_odd = (rs1_rdata + imm)[0], iff jalr/c.jr/c.jalr: bins no{0}, yes{1}
  - cp_wrap = carry out of pc + imm or rs1 + imm: bins no{0}, yes{1}
  - cp_pc_region = rvfi_pc_rdata: bins zero_page{[0:0xFF]}, high{[0xFFFFF000:0xFFFFFFFF]}, mid{default}
  - cp_link_len = rvfi_rd_wdata - rvfi_pc_rdata, iff rd != 0: bins pc4{4}, pc2{2}
- Crosses:
  - cr_op_align = cp_op x cp_target_align: bins auto{all combinations}
  - cr_jal_off_rd = cp_op x cp_jal_off x cp_rd_class: bins auto{all combinations}; ignore ops other than jal: cp_jal_off is guarded
  - cr_jalr_rs1_imm = cp_jalr_rs1 x cp_jalr_imm: bins auto{all combinations}
  - cr_op_wrap = cp_op x cp_wrap: bins auto{all combinations}
  - cr_odd = cp_op x cp_target_odd: bins jalr_odd{jalr, yes}, c_jr_odd{c_jr, yes}, c_jalr_odd{c_jalr, yes}; ignore other combinations: only the odd cases are the corner
  - cr_link = cp_op x cp_link_len: bins jal_pc4{jal, pc4}, jalr_pc4{jalr, pc4}, c_jal_pc2{c_jal, pc2}, c_jalr_pc2{c_jalr, pc2}; ignore mismatched lengths: impossible by construction (a hit is a checker failure)
  - cr_zero_page_bwd = cp_op x cp_pc_region x cp_jal_off: bins jal_zero_page_neg{jal, zero_page, neg_rand}; ignore other combinations: covered elsewhere
- Adopted (riscv-dv): none
- TP items: TP-ISA-015, TP-ISA-016, TP-ISA-017, TP-ISA-018, TP-ISA-019, TP-ISA-020, TP-ISA-022, TP-ISA-053, TP-ISA-054, TP-CMP-010, TP-CMP-011, TP-CMP-028, TP-CMP-032, TP-BTALU-004

### CG-ISA-007: gen_cg_isa_branch
- Features: F-ISA-023, F-ISA-024, F-ISA-026, F-ISA-027, F-ISA-052
- Sample: RVFI retirement; condition: decoded BRANCH (funct3 not 010/011) or c.beqz/c.bnez, rvfi_trap == 0; anti-vacuity: branches are a subset of retirements; taken is derived from rvfi_pc_wdata != pc + len, so a hit proves the sampled outcome actually happened.
- Coverpoints:
  - cp_op = decoded: bins beq{000}, bne{001}, blt{100}, bge{101}, bltu{110}, bgeu{111}, c_beqz{c.beqz}, c_bnez{c.bnez}
  - cp_taken = (rvfi_pc_wdata != rvfi_pc_rdata + len): bins no{0}, yes{1}
  - cp_cmp_class = (rs1_rdata, rs2_rdata): bins equal{rs1 == rs2}, intmin_zero{rs1 == 0x80000000 and rs2 == 0}, zero_intmin{rs1 == 0 and rs2 == 0x80000000}, zero_ones{rs1 == 0 and rs2 == 0xFFFFFFFF}, ones_zero{rs1 == 0xFFFFFFFF and rs2 == 0}, both_msb_eq{rs1 == rs2 == 0x80000000}, slt_ugt{rs1 <s rs2 and rs1 >u rs2}, sgt_ult{rs1 >s rs2 and rs1 <u rs2}, rand{default}
  - cp_offset = sext(imm_b): bins self{0}, max_fwd{4094 (254 for c.b*)}, max_bwd{-4096 (-256 for c.b*)}, pos_rand{default positive}, neg_rand{default negative}
  - cp_target_align = target[1]: bins word{0}, half{1}
  - cp_wrap = carry out of pc + imm, iff taken: bins no{0}, yes{1}
  - cp_delta = retire delta to the next retirement: bins d1{1}, d2{2}, d3plus{[3:$]}
  - cp_dit = cpuctrlsts.data_ind_timing (TB CSR model): bins off{0}, on{1}
- Crosses:
  - cr_op_taken_cmp = cp_op x cp_taken x cp_cmp_class: bins auto{all combinations}; ignore combinations the comparison makes impossible (e.g. beq/equal/not-taken, bne/equal/taken, bltu/zero_ones/not-taken): semantics
  - cr_op_offset_taken = cp_op x cp_offset x cp_taken: bins auto{all combinations}
  - cr_op_align = cp_op x cp_target_align: bins auto{all combinations}
  - cr_taken_dit_delta = cp_taken x cp_dit x cp_delta: bins nt_dit0_d1{no, off, d1}, t_dit0_d2{yes, off, d2}, t_dit0_d3plus{yes, off, d3plus}, nt_dit1_d2{no, on, d2}, t_dit1_d2{yes, on, d2}; ignore nt_dit1_d1 and t_*_d1: impossible by pipeline construction (a hit is a checker failure), ignore nt_dit0_d2/d3plus and nt/t_dit1_d3plus: stall-dependent, covered by cp_delta alone
  - cr_wrap = cp_op x cp_wrap: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-ISA-023, TP-ISA-024, TP-ISA-026, TP-ISA-027, TP-ISA-053, TP-ISA-054, TP-CMP-023, TP-BTALU-001, TP-BTALU-006

### CG-ISA-008: gen_cg_isa_fence
- Features: F-ISA-029, F-ISA-030, F-ISA-031
- Sample: RVFI retirement; condition: decoded MISC-MEM funct3 000 (fence) or 001 (fence.i), rvfi_trap == 0; anti-vacuity: MISC-MEM is rare in the mix; for fence.i the ibus monitor must also see a fresh request at pc+4 for cp_refetch to record yes.
- Coverpoints:
  - cp_op = funct3: bins fence{000}, fence_i{001}
  - cp_fence_fields = (fm, pred, succ, rs1, rd), iff fence: bins canonical{fm 0, pred 1111, succ 1111, rs1 0, rd 0}, tso{fm 1000, pred 0011, succ 0011}, pred_zero{pred 0000}, succ_zero{succ 0000}, rs1_nonzero{rs1 != 0}, rd_nonzero{rd != 0}, fm_other{fm not in 0000/1000}, rand{default}
  - cp_fencei_fields = (rs1, rd, imm), iff fence_i: bins canonical{rs1 0, rd 0, imm 0}, rs1_nonzero{rs1 != 0}, rd_nonzero{rd != 0}, imm_nonzero{imm != 0}, all_nonzero{rs1 != 0 and rd != 0 and imm != 0}
  - cp_icache_en = cpuctrlsts.icache_enable (TB CSR model): bins off{0}, on{1}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_refetch = ibus request to pc + 4 observed after the fence.i, iff fence_i: bins yes{1}
  - cp_delta = retire delta to the next retirement: bins d2{2}, d3plus{[3:$]}
- Crosses:
  - cr_fencei = cp_op x cp_icache_en x cp_pc_align: bins auto{all combinations}; ignore fence: no fetch-path effect
  - cr_fencei_fields = cp_op x cp_fencei_fields: bins auto{all combinations}; ignore fence: guarded
  - cr_fence_fields = cp_op x cp_fence_fields: bins auto{all combinations}; ignore fence_i: guarded
- Adopted (riscv-dv): none
- TP items: TP-ISA-029, TP-ISA-030, TP-ISA-031, TP-ISA-054, TP-BTALU-012

### CG-ISA-009: gen_cg_isa_system
- Features: F-ISA-032, F-ISA-033, F-ISA-034, F-ISA-035, F-ISA-036, F-ISA-037, F-ISA-038, F-ISA-039, F-ISA-040, F-ISA-041, F-ISA-042
- Sample: RVFI retirement; condition: decoded SYSTEM funct3 000 with funct12 in {0x000, 0x001, 0x302, 0x7b2, 0x105} or c.ebreak; anti-vacuity: these retire rarely and the outcome is derived from rvfi_trap, rvfi_ext_debug_mode transition, core_sleep_o and the handler's mcause read-back; a hit proves the sampled (priv, config, outcome) tuple occurred.
- Coverpoints:
  - cp_op = decoded: bins ecall{0x000}, ebreak{0x001}, c_ebreak{0x9002}, mret{0x302}, dret{0x7b2}, wfi{0x105}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_debug_mode = rvfi_ext_debug_mode: bins no{0}, yes{1}
  - cp_ebreakm = dcsr.ebreakm (TB CSR model): bins clr{0}, set{1}
  - cp_ebreaku = dcsr.ebreaku (TB CSR model): bins clr{0}, set{1}
  - cp_tw = mstatus.TW (TB CSR model): bins clr{0}, set{1}
  - cp_outcome = derived: bins exception{rvfi_trap and mcause read-back in 8/11/3}, debug_entry{debug mode entered at this instruction}, executed{no trap; mret/dret redirect or wfi retired}, illegal{rvfi_trap and mcause read-back == 2}
  - cp_wfi_wake = wake source seen by the pin monitors after a wfi retirement, iff wfi executed: bins irq{irq pin}, nmi{irq_nm_i}, debug{debug_req_i}, pending_at_entry{wake condition already true at wfi}
- Crosses:
  - cr_op_priv_outcome = cp_op x cp_priv x cp_outcome: bins auto{all combinations}; ignore impossible: ecall/ebreak executed, mret/u/executed, dret/*/executed outside debug (see cr_dret), wfi/*/exception
  - cr_ebreak = cp_op x cp_priv x cp_ebreakm x cp_ebreaku x cp_debug_mode x cp_outcome: bins m_ebreakm0_exc{ebreak, m, clr, any, no, exception}, m_ebreakm1_dbg{ebreak, m, set, any, no, debug_entry}, u_ebreaku0_exc{ebreak, u, any, clr, no, exception}, u_ebreaku1_dbg{ebreak, u, any, set, no, debug_entry}, dbg_reentry{ebreak, m, any, any, yes, debug_entry}, c_m_exc{c_ebreak, m, clr, any, no, exception}, c_m_dbg{c_ebreak, m, set, any, no, debug_entry}, c_u_dbg{c_ebreak, u, any, set, no, debug_entry}; ignore other combinations: not corners
  - cr_wfi_tw = cp_op x cp_priv x cp_tw x cp_outcome: bins m_tw0_exec{wfi, m, clr, executed}, m_tw1_exec{wfi, m, set, executed}, u_tw0_exec{wfi, u, clr, executed}, u_tw1_illegal{wfi, u, set, illegal}; ignore other combinations: not wfi or impossible
  - cr_wfi_wake = cp_op x cp_wfi_wake: bins auto{all combinations}; ignore non-wfi: guarded
  - cr_dret = cp_op x cp_debug_mode x cp_priv x cp_outcome: bins dret_dbg_exec{dret, yes, m, executed}, dret_m_illegal{dret, no, m, illegal}, dret_u_illegal{dret, no, u, illegal}; ignore other combinations: not corners
  - cr_mret = cp_op x cp_priv x cp_debug_mode x cp_outcome: bins mret_m_exec{mret, m, no, executed}, mret_u_illegal{mret, u, no, illegal}, mret_dbg_exec{mret, m, yes, executed}; ignore other combinations: not corners
- Adopted (riscv-dv): none
- TP items: TP-ISA-032, TP-ISA-033, TP-ISA-034, TP-ISA-035, TP-ISA-036, TP-ISA-037, TP-ISA-038, TP-ISA-039, TP-ISA-040, TP-ISA-041, TP-ISA-042, TP-ISA-055, TP-CMP-033

### CG-ISA-010: gen_cg_isa_csr_insn
- Features: F-ISA-043, F-ISA-044, F-ISA-045, F-ISA-046
- Sample: RVFI retirement; condition: decoded SYSTEM with funct3 in {001,010,011,101,110,111} (and 100 for the illegal bin); anti-vacuity: CSR ops are a minority of retirements; outcome comes from rvfi_trap and from the TB CSR model's write-prediction confirmed by a later read-back.
- Coverpoints:
  - cp_op = funct3: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_src_zero = (instr[19:15] == 0): bins no{0}, yes{1}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_csr_class = csr_addr[11:10]: bins rw{00, 01, 10}, ro{11}
  - cp_outcome = derived: bins read_only{no trap, no write predicted}, write{no trap, write predicted and read back}, illegal{rvfi_trap}
  - cp_f3_100 = (funct3 == 100): bins illegal{rvfi_trap == 1}
- Crosses:
  - cr_op_src_rd = cp_op x cp_src_zero x cp_rd_x0: bins auto{all combinations}
  - cr_op_class_outcome = cp_op x cp_csr_class x cp_src_zero x cp_outcome: bins csrrs_ro_src0_read{csrrs, ro, yes, read_only}, csrrc_ro_src0_read{csrrc, ro, yes, read_only}, csrrsi_ro_u0_read{csrrsi, ro, yes, read_only}, csrrci_ro_u0_read{csrrci, ro, yes, read_only}, csrrw_ro_illegal{csrrw, ro, any, illegal}, csrrwi_ro_illegal{csrrwi, ro, any, illegal}, csrrs_ro_src_illegal{csrrs, ro, no, illegal}, csrrc_ro_src_illegal{csrrc, ro, no, illegal}, csrrsi_ro_u_illegal{csrrsi, ro, no, illegal}, csrrci_ro_u_illegal{csrrci, ro, no, illegal}, csrrs_rw_src0_read{csrrs, rw, yes, read_only}, csrrc_rw_src0_read{csrrc, rw, yes, read_only}, csrrw_rw_write{csrrw, rw, any, write}, csrrwi_rw_write{csrrwi, rw, any, write}, csrrs_rw_write{csrrs, rw, no, write}, csrrc_rw_write{csrrc, rw, no, write}, csrrsi_rw_write{csrrsi, rw, no, write}, csrrci_rw_write{csrrci, rw, no, write}; ignore other combinations: privilege/debug-only illegal cases belong to the CSR area
  - cr_rd_x0_write = cp_op x cp_rd_x0 x cp_outcome: bins csrrw_x0_write{csrrw, yes, write}, csrrwi_x0_write{csrrwi, yes, write}; ignore other combinations: not the corner
- Adopted (riscv-dv): none
- TP items: TP-ISA-043, TP-ISA-044, TP-ISA-045, TP-ISA-046, TP-ISA-055

### CG-ISA-011: gen_cg_isa_illegal
- Features: F-ISA-012, F-ISA-021, F-ISA-025, F-ISA-028, F-ISA-031, F-ISA-037, F-ISA-039, F-ISA-041, F-ISA-042, F-ISA-046, F-ISA-047, F-ISA-048, F-ISA-049, F-ISA-050
- Sample: RVFI retirement; condition: rvfi_trap == 1 and the monitor's decode table classifies rvfi_insn as an illegal encoding (or the handler read-back gives mcause == 2 for mret-in-U / dret / wfi-TW, which are legal encodings); anti-vacuity: trapping retirements are rare and the class comes from the instruction bits, not from the trap; cp_mtval_ok is recorded only when the handler's csrr mtval retires with the predicted value.
- Coverpoints:
  - cp_class = decoded: bins shift_imm_bit25{slli with instr[26:25] != 00; srli/srai with instr[26:25] == 01 - the funct3 101 patterns with instr[26] = 1 are legal fsri (F-ISA-012) and are excluded}, jalr_f3{JALR funct3 != 000}, branch_f3{BRANCH funct3 010/011}, load_f3{LOAD funct3 011/110/111}, store_f3{STORE funct3 011/1xx}, misc_mem_f3{MISC-MEM funct3 010..111}, sys_funct12_other{SYSTEM f3 000 funct12 not in the legal five: sret 0x102, uret 0x002, sfence.vma, others}, sys_rs1_nz{legal funct12 with rs1 != 0}, sys_rd_nz{legal funct12 with rd != 0}, csr_f3_100{SYSTEM f3 100}, csr_ro_write{write to addr[11:10] == 11}, mret_in_u{mret, priv U}, dret_no_debug{dret outside debug}, wfi_u_tw1{wfi, U, TW = 1}, opc_load_fp{0x07}, opc_store_fp{0x27}, opc_amo{0x2f}, opc_op32{0x3b}, opc_opimm32{0x1b}, opc_madd{0x43}, opc_msub{0x47}, opc_nmsub{0x4b}, opc_nmadd{0x4f}, opc_op_fp{0x53}, opc_custom0{0x0b}, opc_custom1{0x2b}, opc_custom2{0x5b}, opc_custom3{0x7b}, opc_reserved_other{other 32-bit major opcodes}, all_ones_word{0xFFFFFFFF}, zero_word{32-bit 0x00000000 fetched as two zero halfwords}
  - cp_len = rvfi_insn[1:0]: bins c16{not 11}, w32{11}
  - cp_mtval_ok = handler csrr mtval == predicted (halfword zero-extended or word): bins yes{1}
  - cp_mepc_ok = handler csrr mepc == rvfi_pc_rdata of the trapping instruction: bins yes{1}
  - cp_wb_outstanding = dbus monitor state when the illegal instruction was in ID: bins none{no access}, load{load outstanding}, store{store outstanding}
  - cp_wb_error = the outstanding access returned data_err_i or PMP fault: bins no{0}, yes{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_debug_mode = rvfi_ext_debug_mode: bins no{0}, yes{1}
- Crosses:
  - cr_class_priv = cp_class x cp_priv: bins auto{all combinations}; ignore mret_in_u/m and wfi_u_tw1/m: U-only by definition
  - cr_class_len = cp_class x cp_len: bins auto{all combinations}; ignore c16 for every 32-bit-only class and w32 for zero_word: by construction
  - cr_wb = cp_wb_outstanding x cp_wb_error: bins none_ok{none, no}, load_ok{load, no}, store_ok{store, no}, load_err{load, yes}, store_err{store, yes}; ignore none_err: no access cannot error
  - cr_class_debug = cp_class x cp_debug_mode: bins auto{all combinations}; ignore dret_no_debug/yes: contradiction
- Adopted (riscv-dv): none
- TP items: TP-ISA-012, TP-ISA-021, TP-ISA-025, TP-ISA-028, TP-ISA-031, TP-ISA-037, TP-ISA-039, TP-ISA-041, TP-ISA-042, TP-ISA-045, TP-ISA-046, TP-ISA-047, TP-ISA-048, TP-ISA-049, TP-ISA-050, TP-ISA-051, TP-ISA-056

---------------------------------------------------------------------------------------------------
## AREA MUL

### CG-MUL-001: gen_cg_mul_ops
- Features: F-MUL-001, F-MUL-002, F-MUL-003, F-MUL-004, F-MUL-005, F-MUL-006, F-MUL-007, F-MUL-008, F-MUL-026, F-MUL-027
- Sample: RVFI retirement; condition: decoded OP funct7 0000001 funct3 000..011 or c.mul, rvfi_trap == 0; anti-vacuity: multiplies are a subset of the mix; a hit proves a multiply retired with the sampled operand classes and result class.
- Coverpoints:
  - cp_op = decoded: bins mul{000}, mulh{001}, mulhsu{010}, mulhu{011}, c_mul{c.mul}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, p16{0x10000}, two{2}, neg_rand{bit31 set, other}, pos_rand{bit31 clear, other}
  - cp_rs2_class = class(rvfi_rs2_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, p16{0x10000}, two{2}, neg_rand{bit31 set, other}, pos_rand{bit31 clear, other}
  - cp_sign_pair = bit31 of rs1,rs2: bins pp{00}, pn{01}, np{10}, nn{11}
  - cp_same_regs = index relation: bins rs1_eq_rs2{rs1 == rs2 != rd}, all_same{rs1 == rs2 == rd != 0}, rs_eq_rd{rs1 == rd or rs2 == rd, rs1 != rs2}, distinct{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, fffffffe{0xFFFFFFFE}, r3fffffff{0x3FFFFFFF}, r40000000{0x40000000}, other{default}
  - cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f3{011}, f4{100}, f5{101}, f6{110}, f7{111}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_rs2 = cp_op x cp_rs2_class: bins auto{all combinations}
  - cr_op_sign = cp_op x cp_sign_pair: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
  - cr_op_same = cp_op x cp_same_regs: bins auto{all combinations}
  - cr_extremes = cp_op x cp_rs1_class x cp_rs2_class: bins auto{all combinations}; ignore combinations containing pos_rand or neg_rand: only extreme-by-extreme products are the corner
  - cr_funct3_rd_x0 = cp_funct3 x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-MUL-001, TP-MUL-002, TP-MUL-003, TP-MUL-004, TP-MUL-005, TP-MUL-006, TP-MUL-007, TP-MUL-008, TP-MUL-026, TP-MUL-027, TP-MUL-028, TP-CMP-038

### CG-MUL-002: gen_cg_mul_timing
- Features: F-MUL-001, F-MUL-003, F-MUL-009, F-MUL-010, F-MUL-011
- Sample: RVFI retirement of mul/mulh/mulhsu/mulhu; condition: a previous retirement exists in the same run; anti-vacuity: cp_delta is meaningful only with fetch_stall == no and wb_busy == no, which the cross requires, so a hit in cr_op_delta_clean proves the multiplier's own occupancy was observed.
- Coverpoints:
  - cp_op = decoded: bins mul{000}, mulh{001}, mulhsu{010}, mulhu{011}
  - cp_delta = retire delta from the previous retirement: bins d1{1}, d2{2}, d3plus{[3:$]}
  - cp_prev = class of the previous retirement: bins alu{single-cycle ALU}, mul{mul}, mulh_class{mulh/mulhsu/mulhu}, load{load}, store{store}, div{div/rem}, branch{branch/jump}, none{first instruction}
  - cp_next_dep = the next retirement reads this rd: bins no{0}, yes{1}
  - cp_wb_busy = dbus monitor: data access outstanding when this instruction entered ID: bins no{0}, yes{1}
  - cp_fetch_stall = ibus monitor: fetch data not available: bins no{0}, yes{1}
  - cp_dmem_delay = dbus monitor rvalid latency class of the outstanding access, iff wb_busy: bins min1{1}, short{[2:4]}, long{[5:$]}
- Crosses:
  - cr_op_delta_clean = cp_op x cp_delta x cp_fetch_stall x cp_wb_busy: bins mul_d1{mul, d1, no, no}, mulh_d2{mulh, d2, no, no}, mulhsu_d2{mulhsu, d2, no, no}, mulhu_d2{mulhu, d2, no, no}; ignore other combinations: stall-dependent
  - cr_seq = cp_prev x cp_op: bins auto{all combinations}; ignore none: first instruction
  - cr_op_next_dep = cp_op x cp_next_dep: bins auto{all combinations}
  - cr_wb_hold = cp_op x cp_wb_busy x cp_dmem_delay: bins auto{all combinations}; ignore wb_busy no: guarded
- Adopted (riscv-dv): none
- TP items: TP-MUL-001, TP-MUL-003, TP-MUL-005, TP-MUL-007, TP-MUL-009, TP-MUL-010, TP-MUL-011, TP-MUL-028

### CG-MUL-003: gen_cg_div_ops
- Features: F-MUL-012, F-MUL-013, F-MUL-014, F-MUL-015, F-MUL-016, F-MUL-017, F-MUL-018, F-MUL-019, F-MUL-020, F-MUL-021, F-MUL-026
- Sample: RVFI retirement; condition: decoded OP funct7 0000001 funct3 100..111, rvfi_trap == 0; anti-vacuity: divides are a subset of the mix; a hit proves a divide retired with the sampled dividend/divisor classes.
- Coverpoints:
  - cp_op = funct3: bins div{100}, divu{101}, rem{110}, remu{111}
  - cp_dividend = class(rvfi_rs1_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, two{2}, seven{7}, neg_rand{bit31 set, other}, pos_rand{bit31 clear, other}
  - cp_divisor = class(rvfi_rs2_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, two{2}, minus_two{0xFFFFFFFE}, eq_dividend{rs2 == rs1 != 0}, abs_gt_dividend{|rs2| > |rs1|, not listed}, neg_rand{bit31 set, other}, pos_rand{bit31 clear, other}
  - cp_sign_pair = bit31 of rs1,rs2: bins pp{00}, pn{01}, np{10}, nn{11}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, eq_dividend{rd_wdata == rs1_rdata}, other{default}
- Crosses:
  - cr_op_divisor = cp_op x cp_divisor: bins auto{all combinations}
  - cr_op_dividend = cp_op x cp_dividend: bins auto{all combinations}
  - cr_div0 = cp_op x cp_divisor x cp_dividend: bins auto{all combinations}; ignore divisor != zero: the divide-by-zero table is the corner
  - cr_overflow = cp_op x cp_dividend x cp_divisor: bins div_intmin_m1{div, int_min, all_ones}, rem_intmin_m1{rem, int_min, all_ones}, divu_intmin_m1{divu, int_min, all_ones}, remu_intmin_m1{remu, int_min, all_ones}; ignore other combinations: covered by cr_op_divisor
  - cr_op_sign = cp_op x cp_sign_pair: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-MUL-012, TP-MUL-013, TP-MUL-014, TP-MUL-015, TP-MUL-016, TP-MUL-017, TP-MUL-018, TP-MUL-019, TP-MUL-020, TP-MUL-021, TP-MUL-026, TP-MUL-028

### CG-MUL-004: gen_cg_div_timing
- Features: F-MUL-012, F-MUL-016, F-MUL-017, F-MUL-022, F-MUL-023, F-MUL-024, F-MUL-025
- Sample: RVFI retirement of div/divu/rem/remu; condition: previous retirement exists; anti-vacuity: the exact-latency cross requires fetch_stall == no and wb_hold == no; the event coverpoint records a pin assertion by the irq/debug drivers strictly inside the divide's occupancy window, so a hit proves the event arrived mid-op.
- Coverpoints:
  - cp_op = funct3: bins div{100}, divu{101}, rem{110}, remu{111}
  - cp_dit = cpuctrlsts.data_ind_timing (TB CSR model): bins off{0}, on{1}
  - cp_div0 = (rvfi_rs2_rdata == 0): bins no{0}, yes{1}
  - cp_delta = retire delta from the previous retirement: bins d2{2}, d37{37}, other{default}
  - cp_event_mid = pin asserted inside the occupancy window (irq driver / debug driver timestamps vs mcycle window): bins none{0}, irq{irq_* line}, debug_req{debug_req_i}, nmi{irq_nm_i}
  - cp_wb_hold = dbus monitor: data access outstanding when the divide entered FINISH: bins no{0}, yes{1}
  - cp_prev = previous retirement class: bins load_dep{load writing rs1 or rs2}, mul{mul class}, div{div class}, alu{ALU}, other{default}
  - cp_next = next retirement class: bins dep_alu{ALU reading rd}, mul{mul class}, div{div class}, other{default}
  - cp_fetch_stall = ibus monitor: bins no{0}, yes{1}
  - cp_irq_latency = cycles from irq assertion to rvfi_intr handler entry, iff event_mid irq: bins le37{[1:37]}, gt37{[38:$]}
- Crosses:
  - cr_dit_div0_delta = cp_dit x cp_div0 x cp_delta x cp_fetch_stall x cp_wb_hold: bins dit0_div0_d2{off, yes, d2, no, no}, dit0_nodiv0_d37{off, no, d37, no, no}, dit1_div0_d37{on, yes, d37, no, no}, dit1_nodiv0_d37{on, no, d37, no, no}; ignore other combinations: stall-dependent or contradictory
  - cr_op_event = cp_op x cp_event_mid: bins auto{all combinations}
  - cr_event_div0_dit = cp_event_mid x cp_div0 x cp_dit: bins auto{all combinations}; ignore none: no event
  - cr_prev_op = cp_prev x cp_op: bins auto{all combinations}
  - cr_next_op = cp_next x cp_op: bins auto{all combinations}
  - cr_op_wb_hold = cp_op x cp_wb_hold: bins auto{all combinations}
  - cr_op_div0 = cp_op x cp_div0 x cp_dit: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-MUL-012, TP-MUL-016, TP-MUL-017, TP-MUL-022, TP-MUL-023, TP-MUL-024, TP-MUL-025, TP-MUL-028, TP-MUL-029

### CG-MUL-005: gen_cg_div_fsm_guard
- Features: F-MUL-028
- Sample: RVFI retirement of div/divu/rem/remu; condition: a previous retirement exists and gen_sva_multdiv is bound in the build; anti-vacuity: every context class needs a specific preceding or coincident event timestamped by the dbus/irq/debug/ibus monitors against the divide's window, so a hit proves the divide ran under that disturbance; cp_sva_checked is recorded only when the bound assertion evaluated non-vacuously for this divide. The reachability cover of the freeze arc itself (div_en_i == 0 && md_state_q != MD_IDLE) is an SVA cover, not a bin: it is expected to stay unhit (gen_hierarchy_map.md H-D3) and a hit is a finding.
- Coverpoints:
  - cp_op = funct3: bins div{100}, divu{101}, rem{110}, remu{111}
  - cp_div_ctx = disturbance class: bins plain{none}, slow_wb{preceding load/store response arrives after the divide entered ID}, fault_wb{the divide's first attempt was killed by a fault of the preceding access (trap between that access and the divide's retirement at the same PC)}, irq_mid{irq line asserted inside the divide window}, debug_mid{debug_req_i inside the window}, fetch_err_next{the instruction after the divide carries a fetch error}
  - cp_dit = cpuctrlsts.data_ind_timing (TB CSR model): bins off{0}, on{1}
  - cp_sva_checked = bound assertion evaluated with no failure for this divide: bins yes{1}
- Crosses:
  - cr_ctx_op = cp_div_ctx x cp_op: bins auto{all combinations}
  - cr_ctx_dit = cp_div_ctx x cp_dit: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-MUL-030

---------------------------------------------------------------------------------------------------
## AREA CMP

### CG-CMP-001: gen_cg_cmp_zca
- Features: F-CMP-001, F-CMP-002, F-CMP-004, F-CMP-005, F-CMP-008, F-CMP-010, F-CMP-012, F-CMP-014, F-CMP-016, F-CMP-018, F-CMP-020, F-CMP-021, F-CMP-023, F-CMP-024, F-CMP-026, F-CMP-028, F-CMP-030, F-CMP-032
- Sample: RVFI retirement; condition: rvfi_insn[1:0] != 11 (16-bit) and decoded Zca instruction, rvfi_trap == 0; cp_insn32_straddle samples 32-bit retirements instead; anti-vacuity: compressed vs 32-bit is decided from the retired instruction bits; a hit proves the sampled instruction retired at the sampled PC alignment with the sampled neighbour length.
- Coverpoints:
  - cp_insn = decoded: bins c_addi4spn{}, c_lw{}, c_sw{}, c_lwsp{}, c_swsp{}, c_addi{}, c_nop{}, c_jal{}, c_j{}, c_li{}, c_lui{}, c_addi16sp{}, c_srli{}, c_srai{}, c_andi{}, c_sub{}, c_xor{}, c_or{}, c_and{}, c_beqz{}, c_bnez{}, c_slli{}, c_mv{}, c_jr{}, c_add{}, c_jalr{}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_next_len = length of the next retired instruction: bins n16{16}, n32{32}
  - cp_pc_inc = rvfi_pc_wdata - rvfi_pc_rdata for non-CTI: bins two{2}
  - cp_insn32_straddle = 32-bit instruction with pc[1] == 1 (spans a word boundary): bins no{0}, yes{1}
  - cp_reg3 = 3-bit register field (x8..x15), iff CIW/CL/CS/CA/CB format: bins r8{0}, r9{1}, r10{2}, r11{3}, r12{4}, r13{5}, r14{6}, r15{7}
  - cp_rd_full = 5-bit rd/rs field, iff CI/CR/CSS format: bins x1{1}, x2{2}, x8_15{[8:15]}, x16_31{[16:31]}, x3_7{[3:7]}
- Crosses:
  - cr_insn_align = cp_insn x cp_pc_align: bins auto{all combinations}
  - cr_insn_next = cp_insn x cp_next_len: bins auto{all combinations}
  - cr_insn_reg3 = cp_insn x cp_reg3: bins auto{all combinations}; ignore CI/CR/CSS instructions: guarded
  - cr_insn_rdfull = cp_insn x cp_rd_full: bins auto{all combinations}; ignore 3-bit-register formats: guarded; ignore c_addi16sp with rd != x2 and c_lui with x2: encoding
- Adopted (riscv-dv): none
- TP items: TP-CMP-001, TP-CMP-002, TP-CMP-004, TP-CMP-005, TP-CMP-008, TP-CMP-010, TP-CMP-012, TP-CMP-014, TP-CMP-016, TP-CMP-018, TP-CMP-020, TP-CMP-021, TP-CMP-023, TP-CMP-024, TP-CMP-026, TP-CMP-028, TP-CMP-030, TP-CMP-032, TP-CMP-070

### CG-CMP-002: gen_cg_cmp_imm_edges
- Features: F-CMP-002, F-CMP-004, F-CMP-005, F-CMP-008, F-CMP-011, F-CMP-012, F-CMP-014, F-CMP-016, F-CMP-017, F-CMP-018, F-CMP-020, F-CMP-023, F-CMP-024, F-ISA-017
- Sample: RVFI retirement of a Zca instruction with an immediate; condition: rvfi_trap == 0; anti-vacuity: each coverpoint is guarded to its format so only that instruction populates it; a hit proves the immediate extreme was decoded and executed (result on RVFI).
- Coverpoints:
  - cp_addi4spn_imm = nzuimm, iff c.addi4spn: bins min{4}, max{1020}, rand{default}
  - cp_lw_sw_uimm = uimm, iff c.lw/c.sw: bins zero{0}, max{124}, rand{default}
  - cp_sp_uimm = uimm, iff c.lwsp/c.swsp: bins zero{0}, max{252}, rand{default}
  - cp_ci_op = decoded, iff c.addi/c.li/c.andi: bins c_addi{}, c_li{}, c_andi{}
  - cp_ci_imm6 = sext(imm6), iff c.addi/c.li/c.andi: bins min{-32}, minus1{-1}, zero{0}, one{1}, max{31}, rand{default}
  - cp_lui_imm = imm6 (nzimm[17:12]), iff c.lui: bins pos_min{1}, pos_max{31}, neg_min{-32}, neg_max{-1}, rand{default}
  - cp_addi16sp_imm = nzimm, iff c.addi16sp: bins min{-512}, max{496}, plus16{16}, minus16{-16}, rand{default}
  - cp_shift_op = decoded, iff c.srli/c.srai/c.slli: bins c_srli{}, c_srai{}, c_slli{}
  - cp_shamt = shamt, iff c.srli/c.srai/c.slli and shamt != 0: bins one{1}, max{31}, rand{default}
  - cp_cj_off = sext(imm), iff c.j/c.jal: bins self{0}, max_fwd{2046}, max_bwd{-2048}, pos_rand{default positive}, neg_rand{default negative}
  - cp_cb_off = sext(imm), iff c.beqz/c.bnez: bins self{0}, max_fwd{254}, max_bwd{-256}, pos_rand{default positive}, neg_rand{default negative}
  - cp_sp_wrap = x2 result crosses 0 (carry/borrow), iff c.addi16sp/c.addi4spn: bins no{0}, yes{1}
  - cp_link = rvfi_rd_wdata - rvfi_pc_rdata, iff c.jal/c.jalr: bins pc2{2}
- Crosses:
  - cr_ci = cp_ci_op x cp_ci_imm6: bins auto{all combinations}; ignore c_addi/zero: that encoding is the HINT (CG-CMP-003)
  - cr_shift = cp_shift_op x cp_shamt: bins auto{all combinations}
  - cr_sp_wrap = cp_addi16sp_imm x cp_sp_wrap: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-CMP-002, TP-CMP-004, TP-CMP-005, TP-CMP-008, TP-CMP-011, TP-CMP-012, TP-CMP-014, TP-CMP-016, TP-CMP-017, TP-CMP-018, TP-CMP-020, TP-CMP-023, TP-CMP-024, TP-CMP-032, TP-CMP-070, TP-ISA-017

### CG-CMP-003: gen_cg_cmp_hints
- Features: F-CMP-009, F-CMP-013, F-CMP-015, F-CMP-019, F-CMP-025, F-CMP-027, F-CMP-031
- Sample: RVFI retirement; condition: decoded 16-bit HINT code point, rvfi_trap == 0; anti-vacuity: HINT code points are deliberately placed by the generator and never emitted by the assembler for normal code; a hit proves the HINT retired without trapping (state change is checked by gen_isa_compare).
- Coverpoints:
  - cp_hint = decoded: bins c_nop_nzimm{c.nop imm != 0}, c_addi_imm0{c.addi rd != 0 imm 0}, c_li_x0{c.li rd x0}, c_lui_x0{c.lui rd x0 imm != 0}, c_srli_shamt0{}, c_srai_shamt0{}, c_slli_shamt0{rd != 0}, c_slli_x0{rd x0 shamt != 0}, c_slli_x0_shamt0{}, c_mv_x0{}, c_add_x0{rs2 not in x2..x5}, c_add_x0_ntl_p1{rs2 x2}, c_add_x0_ntl_pall{rs2 x3}, c_add_x0_ntl_s1{rs2 x4}, c_add_x0_ntl_all{rs2 x5}
  - cp_minstret_inc = minstret delta over the hint (csrr pair around it) == 1: bins observed{1}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
- Crosses:
  - cr_hint_align = cp_hint x cp_pc_align: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-CMP-009, TP-CMP-013, TP-CMP-015, TP-CMP-019, TP-CMP-025, TP-CMP-027, TP-CMP-031, TP-CMP-070

### CG-CMP-004: gen_cg_cmp_illegal
- Features: F-CMP-003, F-CMP-006, F-CMP-007, F-CMP-015, F-CMP-017, F-CMP-019, F-CMP-022, F-CMP-025, F-CMP-029, F-CMP-035, F-CMP-037, F-CMP-044, F-CMP-054, F-CMP-066, F-ISA-049
- Sample: RVFI retirement; condition: rvfi_insn[1:0] != 11 and rvfi_trap == 1 and the monitor decode table classifies the halfword as illegal; anti-vacuity: the class is derived from the instruction bits; cp_mtval_ok / cp_rvfi_insn_ok are recorded only when the handler read-back and the RVFI field match the prediction.
- Coverpoints:
  - cp_class = decoded: bins zero_hw{0x0000}, addi4spn_imm0{instr[12:5] == 0, instr != 0}, lwsp_rd0{}, c_fld{}, c_flw{}, c_fsd{}, c_fsw{}, c_fldsp{}, c_flwsp{}, c_fswsp{}, lui_imm0{}, addi16sp_imm0{}, srli_shamt5{}, srai_shamt5{}, slli_shamt5{}, subw{}, addw{}, jr_rs1_0{0x8002}, sh_bit6{}, zcb_ls_1xx{Q0 funct3 100, instr[12:10] 1xx}, zext_w{}, zcb_alu_110{}, zcb_alu_111{}, push_rlist_res{cm.push rlist 0..3}, pop_rlist_res{}, popret_rlist_res{}, popretz_rlist_res{}, q2_101_zcmt{instr[12:8] in the Zcmt cm.jt/cm.jalt space}, q2_101_other{other instr[12:8]}, q2_011xx_65_00{instr[12:10] 011, instr[6:5] 00}, q2_011xx_65_10{instr[12:10] 011, instr[6:5] 10}
  - cp_rlist_res = instr[7:4], iff Zcmp reserved class: bins r0{0}, r1{1}, r2{2}, r3{3}
  - cp_mtval_ok = handler csrr mtval == zero-extended halfword: bins yes{1}
  - cp_rvfi_insn_ok = rvfi_insn == zero-extended halfword: bins yes{1}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
- Crosses:
  - cr_class_align = cp_class x cp_pc_align: bins auto{all combinations}
  - cr_zcmp_rlist = cp_class x cp_rlist_res: bins auto{all combinations}; ignore non-Zcmp classes: guarded
  - cr_class_priv = cp_class x cp_priv: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-ISA-049, TP-ISA-056, TP-CMP-003, TP-CMP-006, TP-CMP-007, TP-CMP-015, TP-CMP-017, TP-CMP-019, TP-CMP-022, TP-CMP-025, TP-CMP-029, TP-CMP-035, TP-CMP-037, TP-CMP-044, TP-CMP-054, TP-CMP-067, TP-CMP-070

### CG-CMP-005: gen_cg_cmp_zcb
- Features: F-CMP-034, F-CMP-035, F-CMP-036, F-CMP-037, F-CMP-038, F-MUL-027
- Sample: RVFI retirement; condition: decoded Zcb instruction, rvfi_trap == 0; anti-vacuity: Zcb is a small encoding space; load sign and address alignment come from rvfi_mem_addr/rdata so a hit proves the access happened with that data.
- Coverpoints:
  - cp_insn = decoded: bins c_lbu{}, c_lhu{}, c_lh{}, c_sb{}, c_sh{}, c_zext_b{}, c_sext_b{}, c_zext_h{}, c_sext_h{}, c_not{}, c_mul{}
  - cp_uimm_b = uimm, iff c.lbu/c.sb: bins u0{0}, u1{1}, u2{2}, u3{3}
  - cp_uimm_h = uimm, iff c.lhu/c.lh/c.sh: bins u0{0}, u2{2}
  - cp_data_sign = msb of the loaded byte/half, iff c.lbu/c.lhu/c.lh: bins pos{0}, neg{1}
  - cp_alu_operand = class(rvfi_rs1_rdata), iff ALU forms: bins bit7_set{bit 7 set, bit 15 clear}, bit7_clear{bits 7 and 15 clear}, bit15_set{bit 15 set}, zero{0}, all_ones{0xFFFFFFFF}, rand{default}
  - cp_addr_align = rvfi_mem_addr[0], iff c.lhu/c.lh/c.sh: bins aligned{0}, misaligned{1}
  - cp_regs = (rsd' == rs2'), iff c.mul: bins same{1}, distinct{0}
- Crosses:
  - cr_ls_b = cp_insn x cp_uimm_b: bins auto{all combinations}; ignore non-byte forms: guarded
  - cr_ls_h = cp_insn x cp_uimm_h: bins auto{all combinations}; ignore non-half forms: guarded
  - cr_load_sign = cp_insn x cp_data_sign: bins auto{all combinations}; ignore non-loads: guarded
  - cr_alu_operand = cp_insn x cp_alu_operand: bins auto{all combinations}; ignore non-ALU forms: guarded
  - cr_half_misaligned = cp_insn x cp_addr_align: bins auto{all combinations}; ignore non-half forms: guarded
- Adopted (riscv-dv): none
- TP items: TP-CMP-034, TP-CMP-036, TP-CMP-038, TP-CMP-070, TP-MUL-027, TP-BIT-009, TP-BIT-010

### CG-CMP-006: gen_cg_cmp_zcmp_pushpop
- Features: F-CMP-039, F-CMP-040, F-CMP-041, F-CMP-042, F-CMP-043, F-CMP-045, F-CMP-046, F-CMP-047, F-CMP-048, F-CMP-049, F-CMP-055, F-CMP-062, F-CMP-065, F-CMP-067
- Sample: RVFI retirement with rvfi_ext_expanded_insn_last == 1 of a cm.push/cm.pop/cm.popret/cm.popretz whose whole micro-op sequence retired without trap; condition: the monitor has collected every micro-op since the first rvfi_ext_expanded_insn_valid of this PC; anti-vacuity: only completed sequences sample here (interrupted/faulting ones go to CG-CMP-008); the ok-coverpoints are set only when the collected sequence matched the prediction.
- Coverpoints:
  - cp_insn = rvfi_ext_expanded_insn decoded: bins cm_push{}, cm_pop{}, cm_popret{}, cm_popretz{}
  - cp_rlist = instr[7:4]: bins r4{4}, r5{5}, r6{6}, r7{7}, r8{8}, r9{9}, r10{10}, r11{11}, r12{12}, r13{13}, r14{14}, r15{15}
  - cp_spimm = instr[3:2]: bins s0{0}, s1{1}, s2{2}, s3{3}
  - cp_stack_adj = cm_stack_adj(rlist, spimm): bins a16{16}, a32{32}, a48{48}, a64{64}, a80{80}, a96{96}, a112{112}
  - cp_sp_align = x2[1:0] before the instruction: bins aligned{00}, mis1{01}, mis2{10}, mis3{11}
  - cp_sp_wrap = address arithmetic crossing 0: bins none{no wrap}, push_below_zero{sp < 4*N: a store address wraps}, pop_above_max{sp + stack_adj >= 2^32}
  - cp_uop_count_ok = observed micro-op count == N+1 (push/pop), N+2 (popret), N+3 (popretz): bins yes{1}
  - cp_order_ok = store/load register order highest-first and addresses sp-4k / sp+adj-4k as predicted: bins yes{1}
  - cp_rvfi_tags_ok = expanded_valid on all micro-ops, last only on the final one, intermediate pc_wdata == pc_rdata, rvfi_insn == synthesized 32-bit: bins yes{1}
  - cp_minstret_once = minstret delta over the instruction == 1: bins yes{1}
  - cp_ret_align = loaded ra[1:0], iff popret/popretz: bins word{00}, half{10}, odd{x1}
  - cp_dmem_delay = dbus monitor rvalid latency class during the sequence: bins min1{1}, short{[2:4]}, long{[5:$]}, mixed{varies}
- Crosses:
  - cr_insn_rlist_spimm = cp_insn x cp_rlist x cp_spimm: bins auto{all combinations}
  - cr_insn_sp_align = cp_insn x cp_sp_align: bins auto{all combinations}
  - cr_insn_wrap = cp_insn x cp_sp_wrap: bins push_below_zero{cm_push, push_below_zero}, pop_above_max{cm_pop, pop_above_max}, popret_above_max{cm_popret, pop_above_max}, popretz_above_max{cm_popretz, pop_above_max}; ignore push/pop_above_max and pop-family/push_below_zero: direction mismatch; ignore none: not a corner
  - cr_ret_align = cp_insn x cp_ret_align: bins auto{all combinations}; ignore push/pop: guarded
  - cr_insn_delay = cp_insn x cp_dmem_delay: bins auto{all combinations}
  - cr_popret_r4 = cp_insn x cp_rlist: bins popret_r4{cm_popret, r4}, popretz_r4{cm_popretz, r4}; ignore other combinations: covered by cr_insn_rlist_spimm
- Adopted (riscv-dv): none
- TP items: TP-CMP-039, TP-CMP-040, TP-CMP-041, TP-CMP-042, TP-CMP-043, TP-CMP-045, TP-CMP-046, TP-CMP-047, TP-CMP-048, TP-CMP-049, TP-CMP-055, TP-CMP-063, TP-CMP-066, TP-CMP-068, TP-CMP-071

### CG-CMP-007: gen_cg_cmp_zcmp_mv
- Features: F-CMP-050, F-CMP-051, F-CMP-052, F-CMP-053, F-CMP-065, F-CMP-068
- Sample: RVFI retirement with rvfi_ext_expanded_insn_last == 1 of cm.mvsa01/cm.mva01s (both micro-ops collected); anti-vacuity: the two-move sequence is identified from the RVFI tags; a hit proves both moves retired with the sampled register pair.
- Coverpoints:
  - cp_insn = decoded: bins cm_mvsa01{}, cm_mva01s{}
  - cp_r1s = instr[9:7]: bins s0{0}, s1{1}, s2{2}, s3{3}, s4{4}, s5{5}, s6{6}, s7{7}
  - cp_r2s = instr[4:2]: bins s0{0}, s1{1}, s2{2}, s3{3}, s4{4}, s5{5}, s6{6}, s7{7}
  - cp_equal = (r1s == r2s): bins no{0}, yes{1}
  - cp_src_values = a0 vs a1 (mvsa01) or r1s vs r2s (mva01s) values: bins distinct{differ}, same{equal}
  - cp_b2b = neighbouring instruction: bins mvsa01_then_mva01s{}, mva01s_then_mvsa01{}, none{default}
  - cp_hazard_src = source register written by the immediately preceding instruction: bins load_prev{load}, alu_prev{ALU}, none{default}
  - cp_uop_count_ok = two micro-ops, first tagged COMMIT-equivalent (no interrupt between them observed): bins yes{1}
- Crosses:
  - cr_insn_r1_r2 = cp_insn x cp_r1s x cp_r2s: bins auto{all combinations}
  - cr_insn_equal = cp_insn x cp_equal: bins auto{all combinations}
  - cr_insn_hazard = cp_insn x cp_hazard_src: bins auto{all combinations}
  - cr_insn_b2b = cp_insn x cp_b2b: bins auto{all combinations}; ignore none: not a corner
- Adopted (riscv-dv): none
- TP items: TP-CMP-050, TP-CMP-051, TP-CMP-052, TP-CMP-053, TP-CMP-055, TP-CMP-066, TP-CMP-069, TP-CMP-071

### CG-CMP-008: gen_cg_cmp_zcmp_events
- Features: F-CMP-056, F-CMP-057, F-CMP-058, F-CMP-059, F-CMP-060, F-CMP-061, F-CMP-062, F-CMP-063, F-CMP-064
- Sample: monitor event "Zcmp sequence disturbed": an expansion is in flight (rvfi_ext_expanded_insn_valid seen without _last for this PC) and one of: a micro-op retires with rvfi_trap == 1; the next retirement has rvfi_intr == 1 or enters debug mode before _last; the dummy-instruction probe fires while the expansion is in flight; also samples the deferred case (event pin asserted mid-sequence, taken only after _last); condition: as stated; anti-vacuity: requires an actual in-flight expansion plus an event, both derived from observed transactions; a hit proves the event landed at the recorded micro-op index/phase.
- Coverpoints:
  - cp_insn = decoded: bins cm_push{}, cm_pop{}, cm_popret{}, cm_popretz{}, cm_mvsa01{}, cm_mva01s{}
  - cp_event = kind: bins irq{external/timer/software/fast}, nmi{irq_nm_i}, debug_req{debug_req_i}, step{dcsr.step}, trigger{tdata2 match on the cm.* PC or next PC}, store_fault_pmp{}, store_fault_bus{data_err_i}, load_fault_pmp{}, load_fault_bus{}, dummy_inserted{probe P1}
  - cp_uop_idx = index of the micro-op in ID when the event arrived / that faulted: bins i0{0}, i1{1}, i2{2}, i3{3}, i4{4}, i5{5}, i6{6}, i7{7}, i8{8}, i9{9}, i10{10}, i11{11}, i12{12}, i13{13}, i14{14}, i15{15}
  - cp_phase = phase of that micro-op: bins ls_phase{store/load micro-op}, commit_phase{addi sp / li a0 / first move}, last_uop{final micro-op}
  - cp_outcome = derived: bins taken_between{event taken before _last, sequence abandoned}, deferred{event taken after _last}, trap_on_uop{micro-op retired with rvfi_trap}
  - cp_reexec = after the handler, the same cm.* PC re-executes from micro-op 0 (repeated stores/loads observed): bins yes{1}, na{deferred: no re-execution}
  - cp_mepc_ok = mepc read-back == cm.* PC (taken_between/trap) or == next PC (deferred): bins yes{1}
  - cp_sp_unchanged_ok = x2 unchanged after an abandoned sequence: bins yes{1}
  - cp_rlist_class = instr[7:4]: bins r4{4}, r5_14{[5:14]}, r15{15}
  - cp_mis_half = faulting half of a misaligned micro-op, iff sp misaligned and fault: bins first{first half}, second{second half}
- Crosses:
  - cr_insn_event = cp_insn x cp_event: bins auto{all combinations}; ignore load faults on cm_push, store faults on pop-family, any fault on mv forms: no such access
  - cr_event_phase_outcome = cp_event x cp_phase x cp_outcome: bins irq_ls_taken{irq, ls_phase, taken_between}, irq_commit_deferred{irq, commit_phase, deferred}, irq_last_deferred{irq, last_uop, deferred}, nmi_ls_taken{nmi, ls_phase, taken_between}, nmi_commit_deferred{nmi, commit_phase, deferred}, debug_ls_deferred{debug_req, ls_phase, deferred}, debug_commit_deferred{debug_req, commit_phase, deferred}, step_deferred{step, last_uop, deferred}, trigger_deferred{trigger, last_uop, deferred}, store_fault_pmp_trap{store_fault_pmp, ls_phase, trap_on_uop}, store_fault_bus_trap{store_fault_bus, ls_phase, trap_on_uop}, load_fault_pmp_trap{load_fault_pmp, ls_phase, trap_on_uop}, load_fault_bus_trap{load_fault_bus, ls_phase, trap_on_uop}, dummy_ls{dummy_inserted, ls_phase, any}, dummy_commit{dummy_inserted, commit_phase, any}; ignore irq/nmi taken in commit_phase and debug taken_between: blocked by the RTL rule (a hit is a checker failure)
  - cr_fault_idx = cp_event x cp_uop_idx: bins auto{all combinations}; ignore non-fault events: covered by cr_irq_idx; ignore indices beyond the store/load count of the sampled rlist: no such micro-op
  - cr_irq_idx = cp_event x cp_uop_idx: bins auto{all combinations}; ignore events other than irq/nmi/debug_req: covered by cr_fault_idx
  - cr_insn_rlist_event = cp_insn x cp_rlist_class x cp_event: bins auto{all combinations}; ignore mv forms x r5_14/r15: mv has no rlist
  - cr_mis_fault = cp_event x cp_mis_half: bins auto{all combinations}; ignore non-fault events: guarded
- Adopted (riscv-dv): none
- TP items: TP-CMP-056, TP-CMP-057, TP-CMP-058, TP-CMP-059, TP-CMP-060, TP-CMP-061, TP-CMP-062, TP-CMP-063, TP-CMP-064, TP-CMP-065, TP-CMP-071

### CG-CMP-009: gen_cg_cmp_zcmp_hazard
- Features: F-CMP-049, F-CMP-065, F-CMP-068, F-CMP-070
- Sample: RVFI retirement with rvfi_ext_expanded_insn_last == 1 of any cm.* instruction; condition: the monitor's instruction history identifies one of the listed neighbour patterns; anti-vacuity: the pattern requires a specific preceding/following retirement so it cannot fire on an isolated cm.*; a hit proves the hazard pattern executed.
- Coverpoints:
  - cp_hazard = pattern: bins store_same_slot_then_pop{sw to a slot the following cm.pop loads}, write_pushed_reg_then_push{ALU writes a register the following cm.push stores}, load_pushed_reg_then_push{load into a register the following cm.push stores}, load_then_mva01s{load into r1s'/r2s' then cm.mva01s}, popret_ra_fwd{cm.popret: ra load micro-op then ret}, push_then_pop_b2b{cm.push then cm.pop}, pop_then_push_b2b{cm.pop then cm.push}, popret_then_target{cm.popret then the return target retires next}, popretz_then_target{cm.popretz then the return target retires next}, mvsa01_then_mva01s{}, popret_ft_cm{cm.popret whose PC+2 halfword is a cm.*}, popretz_ft_cm{cm.popretz whose PC+2 halfword is a cm.*}
  - cp_ft_kind = kind of the fall-through cm.* at PC+2, iff popret_ft_cm/popretz_ft_cm: bins cm_push{}, cm_pop{}, cm_popret{}, cm_popretz{}, cm_mvsa01{}, cm_mva01s{}
  - cp_ret_once = exactly one rvfi_ext_expanded_insn_last for the popret/popretz and the next rvfi_pc_rdata == ra target: bins yes{1}
  - cp_redirect_once = one ibus redirect for the ret (ibus monitor): bins yes{1}
  - cp_rlist_class = instr[7:4]: bins r4{4}, r5_14{[5:14]}, r15{15}
  - cp_dmem_delay = dbus monitor rvalid latency class: bins min1{1}, short{[2:4]}, long{[5:$]}
  - cp_delta_uop = per-micro-op retire delta class over the sequence: bins all_one{every delta 1}, some_stall{a delta > 1}
- Crosses:
  - cr_hazard_rlist = cp_hazard x cp_rlist_class: bins auto{all combinations}; ignore mvsa01_then_mva01s and load_then_mva01s with r5_14/r15: mv has no rlist
  - cr_hazard_delay = cp_hazard x cp_dmem_delay: bins auto{all combinations}
  - cr_ft_kind = cp_hazard x cp_ft_kind: bins auto{all combinations}; ignore hazards other than popret_ft_cm/popretz_ft_cm: guarded
- Adopted (riscv-dv): none
- TP items: TP-CMP-049, TP-CMP-066, TP-CMP-069, TP-CMP-071, TP-CMP-073

### CG-CMP-010: gen_cg_cmp_zcmp_fetch_err
- Features: F-CMP-069
- Sample: RVFI retirement with rvfi_trap == 1 whose handler read-back gives mcause == 1 and whose PC holds a Zcmp halfword (the monitor decodes the fetched halfword from the ibus stream, not from rvfi_insn, because the PMP path reports the synthesized micro-op); anti-vacuity: only an ibus-agent instr_err_i or a PMP execute denial on a Zcmp encoding produces the sample; the ok-coverpoints are recorded only when the predicted absence of data requests and the restart from micro-op 0 were observed.
- Coverpoints:
  - cp_insn = decoded halfword: bins cm_push{}, cm_pop{}, cm_popret{}, cm_popretz{}, cm_mvsa01{}, cm_mva01s{}
  - cp_err_kind = error source: bins bus{instr_err_i on the fetch}, pmp{PMP execute denied}
  - cp_expanded_tag = rvfi_ext_expanded_insn_valid on the trapping entry: bins bus_not_expanded{bus, 0}, pmp_expanded{pmp, 1 with rvfi_ext_expanded_insn_last 0}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_reach = how the halfword was reached: bins sequential{fall-through}, jump_target{target of a taken CTI}
  - cp_no_dreq = no data_req_o between the previous retirement and the handler entry: bins yes{1}
  - cp_next_uop0 = the next cm.* (same PC after mret, or another) retires from micro-op 0 with its full count: bins yes{1}
  - cp_mtval_ok = handler read-back mtval == mepc == the cm.* PC: bins yes{1}
- Crosses:
  - cr_insn_err = cp_insn x cp_err_kind: bins auto{all combinations}
  - cr_err_align = cp_err_kind x cp_pc_align x cp_priv: bins auto{all combinations}
  - cr_err_reach = cp_err_kind x cp_reach: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-CMP-072

---------------------------------------------------------------------------------------------------
## AREA BIT

### CG-BIT-001: gen_cg_bit_zba_zbb_ops
- Features: F-BIT-002, F-BIT-003, F-BIT-004, F-BIT-007, F-BIT-008, F-BIT-009, F-BIT-010, F-BIT-011, F-BIT-038
- Sample: RVFI retirement; condition: decoded sh1add/sh2add/sh3add/andn/orn/xnor/min/max/minu/maxu/sext.b/sext.h/pack/packu/packh (zext.h = pack with rs2 == x0), rvfi_trap == 0; anti-vacuity: Zb* funct7 values are excluded from base ALU sampling and vice versa; a hit proves the op retired with the sampled operand classes.
- Coverpoints:
  - cp_op = decoded: bins sh1add{}, sh2add{}, sh3add{}, andn{}, orn{}, xnor{}, min{}, max{}, minu{}, maxu{}, sext_b{}, sext_h{}, zext_h{pack, rs2 == x0}, pack{rs2 != x0}, packu{}, packh{}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, e0000000{0xE0000000}, byte_msb{bit 7 set, bit 15 clear}, half_msb{bit 15 set, bit 7 clear}, pos_rand{default bit31 clear}, neg_rand{default bit31 set}
  - cp_rs2_class = class(rvfi_rs2_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, pos_rand{default bit31 clear}, neg_rand{default bit31 set}
  - cp_eq_operands = (rs1_rdata == rs2_rdata): bins no{0}, yes{1}
  - cp_same_regs = index relation: bins rs1_eq_rs2{rs1 == rs2 != rd}, all_same{rs1 == rs2 == rd != 0}, distinct{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_sign_pair = bit31 of rs1,rs2: bins pp{00}, pn{01}, np{10}, nn{11}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, other{default}
  - cp_wrap = carry out of rs2 + (rs1 << n), iff shNadd: bins no{0}, yes{1}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_rs2 = cp_op x cp_rs2_class: bins auto{all combinations}; ignore sext_b/sext_h/zext_h: unary
  - cr_op_eq = cp_op x cp_eq_operands: bins auto{all combinations}; ignore unary ops: guarded
  - cr_minmax_sign = cp_op x cp_sign_pair: bins auto{all combinations}; ignore ops other than min/max/minu/maxu: sign only matters for compares
  - cr_shadd_wrap = cp_op x cp_wrap: bins auto{all combinations}; ignore non-shNadd: guarded
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
  - cr_op_same = cp_op x cp_same_regs: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-002, TP-BIT-003, TP-BIT-004, TP-BIT-007, TP-BIT-008, TP-BIT-009, TP-BIT-010, TP-BIT-011, TP-BIT-038, TP-BIT-041

### CG-BIT-002: gen_cg_bit_count
- Features: F-BIT-005, F-BIT-006, F-BIT-038
- Sample: RVFI retirement; condition: decoded clz/ctz/cpop (OP-IMM funct3 001, instr[31:20] 0x600/0x601/0x602), rvfi_trap == 0; anti-vacuity: three funct12 values; single-bit position is derived from the operand so a hit proves the sampled input reached the counter.
- Coverpoints:
  - cp_op = instr[31:20]: bins clz{0x600}, ctz{0x601}, cpop{0x602}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, lsb_only{1}, single_other{exactly one bit set, not bit 0/31}, alt_5{0x55555555}, alt_a{0xAAAAAAAA}, int_max{0x7FFFFFFF}, rand{default}
  - cp_single_pos = position of the set bit, iff exactly one bit set: bins p0{0}, p1{1}, p2{2}, p3{3}, p4{4}, p5{5}, p6{6}, p7{7}, p8{8}, p9{9}, p10{10}, p11{11}, p12{12}, p13{13}, p14{14}, p15{15}, p16{16}, p17{17}, p18{18}, p19{19}, p20{20}, p21{21}, p22{22}, p23{23}, p24{24}, p25{25}, p26{26}, p27{27}, p28{28}, p29{29}, p30{30}, p31{31}
  - cp_result = rvfi_rd_wdata: bins r0{0}, r1{1}, r16{16}, r31{31}, r32{32}, other{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_op_single = cp_op x cp_single_pos: bins auto{all combinations}
  - cr_op_result = cp_op x cp_result: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-005, TP-BIT-006, TP-BIT-038, TP-BIT-041

### CG-BIT-003: gen_cg_bit_rotate_shiftones
- Features: F-BIT-012, F-BIT-013, F-BIT-022, F-BIT-023, F-BIT-036, F-BIT-037, F-BIT-038
- Sample: RVFI retirement; condition: decoded rol/ror/rori/slo/sro/sloi/sroi, rvfi_trap == 0; anti-vacuity: the amount is the effective rs2[4:0]/imm[4:0] and cp_delta only counts when fetch_stall == no; a hit proves the sampled amount/operand executed and (rotates) the two-cycle occupancy was observed.
- Coverpoints:
  - cp_op = decoded: bins rol{}, ror{}, rori{}, slo{}, sro{}, sloi{}, sroi{}
  - cp_amount = rs2[4:0] or imm[4:0]: bins a0{0}, a1{1}, mid{[2:30]}, a31{31}
  - cp_rs2_upper = rvfi_rs2_rdata, iff register form: bins zero{rs2[31:5] == 0}, is32{32}, all_ones{0xFFFFFFFF}, other_nonzero{default}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, lsb_only{1}, rand{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_delta = retire delta to the next retirement with fetch_stall == no, iff rol/ror/rori: bins d2{2}, d3plus{[3:$]}
  - cp_sloi_bits = instr[26:25], iff sloi: bins b00{00}, b01{01}, b10{10}, b11{11}
  - cp_sroi_bit25 = instr[25], iff sroi: bins b0{0}, b1{1}
- Crosses:
  - cr_op_amount = cp_op x cp_amount: bins auto{all combinations}
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_reg_upper = cp_op x cp_rs2_upper: bins auto{all combinations}; ignore immediate forms: guarded
  - cr_rot_delta = cp_op x cp_delta: bins rol_d2{rol, d2}, ror_d2{ror, d2}, rori_d2{rori, d2}; ignore other combinations: stall-dependent or not rotates
  - cr_sloi_lenient = cp_op x cp_sloi_bits: bins auto{all combinations}; ignore non-sloi: guarded
  - cr_sroi_lenient = cp_op x cp_sroi_bit25: bins auto{all combinations}; ignore non-sroi: guarded
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-012, TP-BIT-013, TP-BIT-022, TP-BIT-023, TP-BIT-036, TP-BIT-037, TP-BIT-038, TP-BIT-041

### CG-BIT-004: gen_cg_bit_perm
- Features: F-BIT-014, F-BIT-015, F-BIT-016, F-BIT-024, F-BIT-037, F-BIT-038
- Sample: RVFI retirement; condition: decoded grev/grevi/gorc/gorci/shfl/shfli/unshfl/unshfli, rvfi_trap == 0; anti-vacuity: control value comes from rs2[4:0]/[3:0] or the immediate; a hit proves that control value executed on the sampled operand.
- Coverpoints:
  - cp_op = decoded: bins grev{}, grevi{}, gorc{}, gorci{}, shfl{}, shfli{}, unshfl{}, unshfli{}
  - cp_grev_ctrl = control[4:0], iff grev/grevi/gorc/gorci: bins c0{0}, c1{1}, c2{2}, c3{3}, c4{4}, c5{5}, c6{6}, c7{7}, c8{8}, c9{9}, c10{10}, c11{11}, c12{12}, c13{13}, c14{14}, c15{15}, c16{16}, c17{17}, c18{18}, c19{19}, c20{20}, c21{21}, c22{22}, c23{23}, c24{24}, c25{25}, c26{26}, c27{27}, c28{28}, c29{29}, c30{30}, c31{31}
  - cp_shfl_ctrl = control[3:0], iff shfl family: bins c0{0}, c1{1}, c2{2}, c3{3}, c4{4}, c5{5}, c6{6}, c7{7}, c8{8}, c9{9}, c10{10}, c11{11}, c12{12}, c13{13}, c14{14}, c15{15}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, bytes_01020304{0x01020304}, single_bit{exactly one bit set}, rand{default}
  - cp_rs2_upper = rs2 bits above the control field, iff register form: bins zero{0}, nonzero{1}
  - cp_bit25 = instr[25], iff grevi/gorci/shfli/unshfli: bins b0{0}, b1{1}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_grev_ctrl = cp_op x cp_grev_ctrl: bins auto{all combinations}; ignore shfl family: guarded
  - cr_shfl_ctrl = cp_op x cp_shfl_ctrl: bins auto{all combinations}; ignore grev family: guarded
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_lenient = cp_op x cp_bit25: bins grevi_b1{grevi, b1}, gorci_b1{gorci, b1}, shfli_b1{shfli, b1}, unshfli_b1{unshfli, b1}; ignore b0 and register forms: canonical
  - cr_reg_upper = cp_op x cp_rs2_upper: bins auto{all combinations}; ignore immediate forms: guarded
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-014, TP-BIT-015, TP-BIT-016, TP-BIT-024, TP-BIT-037, TP-BIT-038, TP-BIT-041

### CG-BIT-005: gen_cg_bit_xperm
- Features: F-BIT-025, F-BIT-026, F-BIT-038
- Sample: RVFI retirement; condition: decoded xperm.n/xperm.b/xperm.h, rvfi_trap == 0; anti-vacuity: the index pattern is classified from rvfi_rs2_rdata per lane width; a hit proves the sampled pattern was looked up.
- Coverpoints:
  - cp_op = decoded: bins xperm_n{}, xperm_b{}, xperm_h{}
  - cp_index_pattern = rs2 lanes: bins identity{lane i selects i}, reverse{lane i selects N-1-i}, all_same{all lanes select one index}, all_oob{every lane out of range}, mixed_oob{some lanes out of range}, rand{default in range}
  - cp_oob_lanes = number of out-of-range lanes: bins none{0}, some{[1:N-1]}, all{N}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, distinct_lanes{every lane value unique}, rand{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_op_pattern = cp_op x cp_index_pattern: bins auto{all combinations}
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_oob = cp_op x cp_oob_lanes: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-025, TP-BIT-026, TP-BIT-038, TP-BIT-041

### CG-BIT-006: gen_cg_bit_sbit
- Features: F-BIT-017, F-BIT-018, F-BIT-019, F-BIT-038
- Sample: RVFI retirement; condition: decoded bclr/bset/binv/bext/bclri/bseti/binvi/bexti, rvfi_trap == 0; anti-vacuity: the prior bit state is read from rvfi_rs1_rdata at the effective index; a hit proves the op acted on a bit in the sampled state.
- Coverpoints:
  - cp_op = decoded: bins bclr{}, bset{}, binv{}, bext{}, bclri{}, bseti{}, binvi{}, bexti{}
  - cp_index = rs2[4:0] or imm[4:0]: bins i0{0}, mid{[1:30]}, i31{31}
  - cp_rs2_upper = rvfi_rs2_rdata, iff register form: bins zero{rs2[31:5] == 0}, all_ones{0xFFFFFFFF}, other_nonzero{default}
  - cp_prior_bit = rs1[index]: bins clear{0}, set{1}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, rand{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_binv_twice = binv/binvi followed by binv/binvi on the same rd and index: bins yes{1}
- Crosses:
  - cr_op_index_prior = cp_op x cp_index x cp_prior_bit: bins auto{all combinations}
  - cr_reg_upper = cp_op x cp_rs2_upper: bins auto{all combinations}; ignore immediate forms: guarded
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-017, TP-BIT-018, TP-BIT-019, TP-BIT-038, TP-BIT-041

### CG-BIT-007: gen_cg_bit_clmul_crc
- Features: F-BIT-020, F-BIT-021, F-BIT-032, F-BIT-033, F-BIT-036, F-BIT-038
- Sample: RVFI retirement; condition: decoded clmul/clmulh/clmulr or crc32.b/.h/.w or crc32c.b/.h/.w, rvfi_trap == 0; anti-vacuity: operand classes from rvfi_rs1/rs2_rdata; cp_delta counts only with fetch_stall == no so a hit proves the crc's two-cycle occupancy.
- Coverpoints:
  - cp_op = decoded: bins clmul{}, clmulh{}, clmulr{}, crc32_b{}, crc32_h{}, crc32_w{}, crc32c_b{}, crc32c_h{}, crc32c_w{}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, single_bit{exactly one bit set}, high_only{bits above the op's data width set, low bits zero}, low_only{only bits inside the op's data width set}, rand{default}
  - cp_rs2_class = class(rvfi_rs2_rdata), iff clmul family: bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, single_bit{exactly one bit set}, rand{default}
  - cp_bit_sum = i + j for single-bit rs1 (1<<i) and rs2 (1<<j), iff clmul family: bins lt32{[0:31]}, ge32{[32:62]}
  - cp_delta = retire delta to the next retirement with fetch_stall == no, iff crc: bins d2{2}, d3plus{[3:$]}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}; ignore high_only/low_only for clmul family: width classes are for crc
  - cr_clmul_rs2 = cp_op x cp_rs2_class: bins auto{all combinations}; ignore crc ops: guarded
  - cr_clmul_bitsum = cp_op x cp_bit_sum: bins auto{all combinations}; ignore crc ops: guarded
  - cr_crc_delta = cp_op x cp_delta: bins auto{all combinations}; ignore clmul ops and d3plus: guarded / stall-dependent
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-020, TP-BIT-021, TP-BIT-032, TP-BIT-033, TP-BIT-036, TP-BIT-038, TP-BIT-041

### CG-BIT-008: gen_cg_bit_ternary
- Features: F-BIT-027, F-BIT-028, F-BIT-029, F-BIT-036, F-BIT-038, F-BIT-039, F-ISA-012
- Sample: RVFI retirement; condition: decoded cmov/cmix/fsl/fsr/fsri (OP with instr[26] == 1 and funct3 001/101; OP-IMM funct3 101 with instr[26] == 1), rvfi_trap == 0; anti-vacuity: rs3 comes from rvfi_rs3_addr/rdata, the amount from rs2[5:0]/imm[5:0]; a hit proves the sampled ternary case executed with rs3 read.
- Coverpoints:
  - cp_op = decoded: bins cmov{}, cmix{}, fsl{}, fsr{}, fsri{}
  - cp_cmov_ctrl = class(rvfi_rs2_rdata), iff cmov: bins zero{0}, one{1}, msb_only{0x80000000}, nonzero_rand{default}
  - cp_cmix_mask = class(rvfi_rs2_rdata), iff cmix: bins zero{0}, all_ones{0xFFFFFFFF}, alt{0x55555555 or 0xAAAAAAAA}, rand{default}
  - cp_funnel_amt = rs2[5:0] or imm[5:0], iff fsl/fsr/fsri: bins a0{0}, a1{1}, mid_lo{[2:30]}, a31{31}, a32{32}, a33{33}, mid_hi{[34:62]}, a63{63}
  - cp_fsri_hi5 = instr[31:27] (the rs3 field), iff fsri: bins srli_pattern{00000}, srai_pattern{01000}, other{default}
  - cp_rs2_upper6 = rs2[31:6], iff fsl/fsr: bins zero{0}, nonzero{1}
  - cp_rs3_choice = rvfi_rs3_addr relation: bins eq_rs1{rs3 == rs1}, eq_rs2{rs3 == rs2}, eq_rd{rs3 == rd != 0}, x0{rs3 == 0}, distinct{default}
  - cp_rs1_rs3_class = (rs1_rdata, rs3_rdata): bins zero_ones{rs1 0, rs3 0xFFFFFFFF}, ones_zero{rs1 0xFFFFFFFF, rs3 0}, equal{rs1 == rs3}, rand{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_delta = retire delta to the next retirement with fetch_stall == no: bins d2{2}, d3plus{[3:$]}
- Crosses:
  - cr_funnel_amt = cp_op x cp_funnel_amt: bins auto{all combinations}; ignore cmov/cmix: guarded
  - cr_op_rs3 = cp_op x cp_rs3_choice: bins auto{all combinations}
  - cr_cmov = cp_op x cp_cmov_ctrl: bins auto{all combinations}; ignore non-cmov: guarded
  - cr_cmix = cp_op x cp_cmix_mask: bins auto{all combinations}; ignore non-cmix: guarded
  - cr_funnel_upper = cp_op x cp_rs2_upper6: bins fsl_nonzero{fsl, nonzero}, fsr_nonzero{fsr, nonzero}; ignore other combinations: guarded / canonical
  - cr_op_delta = cp_op x cp_delta: bins auto{all combinations}; ignore d3plus: stall-dependent
  - cr_op_rs13 = cp_op x cp_rs1_rs3_class: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-027, TP-BIT-028, TP-BIT-029, TP-BIT-036, TP-BIT-038, TP-BIT-039, TP-BIT-041, TP-ISA-012

### CG-BIT-009: gen_cg_bit_bfp
- Features: F-BIT-030, F-BIT-031, F-BIT-038
- Sample: RVFI retirement; condition: decoded bfp (OP f7 0100100 f3 111), rvfi_trap == 0; anti-vacuity: len/off/data are fields of rvfi_rs2_rdata; a hit proves that control word executed; cp_delta counts only with fetch_stall == no.
- Coverpoints:
  - cp_len = rs2[27:24]: bins l0{0}, l1{1}, mid{[2:14]}, l15{15}
  - cp_off = rs2[20:16]: bins o0{0}, mid{[1:15]}, o16{16}, mid_hi{[17:30]}, o31{31}
  - cp_overflow = (off + len_eff > 32) with len_eff = 16 when len == 0: bins no{0}, yes{1}
  - cp_data_class = rs2[15:0] vs len: bins zero{0}, all_ones{0xFFFF}, above_len_set{bits above len_eff set}, rand{default}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, rand{default}
  - cp_ctrl_upper = rs2[31:28] and rs2[23:21]: bins zero{0}, nonzero{1}
  - cp_delta = retire delta to the next retirement with fetch_stall == no: bins d1{1}, d2plus{[2:$]}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_len_off = cp_len x cp_off: bins auto{all combinations}
  - cr_overflow_len = cp_overflow x cp_len: bins auto{all combinations}; ignore no: not the corner
  - cr_data_rs1 = cp_data_class x cp_rs1_class: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-030, TP-BIT-031, TP-BIT-038, TP-BIT-041

### CG-BIT-010: gen_cg_bit_multicycle_pipe
- Features: F-BIT-036, F-BIT-039, F-BIT-041, F-BIT-012, F-BIT-027, F-BIT-028, F-BIT-032
- Sample: RVFI retirement of a two-cycle Zb* op (rol/ror/rori/cmov/cmix/fsl/fsr/fsri/crc32*); condition: previous retirement exists; anti-vacuity: dependency class needs a preceding writer of the exact source register, the event class needs a pin assertion timestamped inside the op's two-cycle window; a hit proves the hazard/event coincided with the op.
- Coverpoints:
  - cp_op_class = decoded: bins rot{rol/ror/rori}, ternary{cmov/cmix/fsl/fsr/fsri}, crc{crc32*}
  - cp_prev_dep = previous retirement writes: bins alu_rs1{ALU writes rs1}, alu_rs2{ALU writes rs2}, alu_rs3{ALU writes rs3}, load_rs1{load writes rs1}, load_rs2{load writes rs2}, load_rs3{load writes rs3}, none{default}
  - cp_delta = retire delta from the previous retirement: bins d2{2}, d3plus{[3:$]}
  - cp_event_mid = pin asserted inside the two-cycle window: bins none{0}, irq{irq line}, debug_req{debug_req_i}, nmi{irq_nm_i}
  - cp_wb_busy = dbus monitor: data access outstanding when the op entered ID: bins no{0}, yes{1}
  - cp_hold_cycles = retire delta - 2, iff wb_busy: bins h1{1}, h2_4{[2:4]}, h5plus{[5:$]}
  - cp_wb_kind = kind of the outstanding access, iff wb_busy: bins load{}, store{}
  - cp_fetch_stall = ibus monitor: bins no{0}, yes{1}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_next_dep = next retirement reads rd: bins no{0}, yes{1}
- Crosses:
  - cr_class_prev = cp_op_class x cp_prev_dep: bins auto{all combinations}; ignore rs3 dependencies for rot/crc: no rs3
  - cr_class_event = cp_op_class x cp_event_mid: bins auto{all combinations}
  - cr_class_wb = cp_op_class x cp_wb_busy: bins auto{all combinations}
  - cr_class_hold = cp_op_class x cp_hold_cycles x cp_wb_kind: bins auto{all combinations}; ignore wb_busy no: guarded
  - cr_class_delta_clean = cp_op_class x cp_delta x cp_fetch_stall x cp_wb_busy: bins rot_d2{rot, d2, no, no}, ternary_d2{ternary, d2, no, no}, crc_d2{crc, d2, no, no}; ignore other combinations: stall-dependent
  - cr_class_next = cp_op_class x cp_next_dep: bins auto{all combinations}
  - cr_class_rd_x0 = cp_op_class x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-012, TP-BIT-027, TP-BIT-028, TP-BIT-032, TP-BIT-036, TP-BIT-039, TP-BIT-042, TP-BIT-043

### CG-BIT-011: gen_cg_bit_decode
- Features: F-BIT-001, F-BIT-013, F-BIT-019, F-BIT-024, F-BIT-034, F-BIT-035, F-BIT-037, F-BIT-040
- Sample: RVFI retirement; condition: decoded OP or OP-IMM encoding whose funct7/hi5 lies outside base-I/M (the Zb* decode space), or opcode OP-32/OP-IMM-32, or csrr misa; anti-vacuity: legality is decided by the monitor's ENC table and compared with rvfi_trap, so a hit in cr_legal_notrap proves a legal Zb* encoding retired without trap and a hit in cr_illegal_trap proves the illegal one trapped.
- Coverpoints:
  - cp_legal_insn = ENC table mnemonic: bins sh1add{}, sh2add{}, sh3add{}, andn{}, orn{}, xnor{}, rol{}, ror{}, min{}, max{}, minu{}, maxu{}, pack{}, packu{}, packh{}, bclr{}, bset{}, binv{}, bext{}, bfp{}, grev{}, gorc{}, shfl{}, unshfl{}, xperm_n{}, xperm_b{}, xperm_h{}, slo{}, sro{}, clmul{}, clmulr{}, clmulh{}, cmix{}, cmov{}, fsl{}, fsr{}, sloi{}, bclri{}, bseti{}, binvi{}, shfli{}, clz{}, ctz{}, cpop{}, sext_b{}, sext_h{}, crc32_b{}, crc32_h{}, crc32_w{}, crc32c_b{}, crc32c_h{}, crc32c_w{}, fsri{}, sroi{}, rori{}, bexti{}, grevi{}, gorci{}, unshfli{}
  - cp_illegal_class = decoded: bins bcompress{0000100/110}, bdecompress{0100100/110}, op32_any{opcode 0x3b}, opimm32_any{opcode 0x1b}, rori_bit25{}, bclri_bit25{}, bseti_bit25{}, binvi_bit25{}, bexti_bit25{}, shfli_bit26{}, opimm_001_hi5_other{OP-IMM f3 001 hi5 not in table}, opimm_101_hi5_other{OP-IMM f3 101 instr[26] 0 hi5 not in table}, opimm_0110000_rs2_other{hi5 01100 instr[26:20] not in table}, op_f7f3_other{OP funct7/funct3 not in table}
  - cp_trap = rvfi_trap: bins no{0}, yes{1}
  - cp_mtval_ok = handler csrr mtval == the 32-bit word: bins yes{1}
  - cp_misa = csrr misa read-back bits: bins x_set{bit 23 == 1}, b_clear{bit 1 == 0}, m_set{bit 12 == 1}, c_set{bit 2 == 1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
- Crosses:
  - cr_legal_notrap = cp_legal_insn x cp_trap: bins auto{all combinations}; ignore yes: a legal encoding trapping is a checker failure, not a bin
  - cr_illegal_trap = cp_illegal_class x cp_trap: bins auto{all combinations}; ignore no: an illegal encoding executing is a checker failure
  - cr_illegal_priv = cp_illegal_class x cp_priv: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-001, TP-BIT-013, TP-BIT-019, TP-BIT-024, TP-BIT-030, TP-BIT-034, TP-BIT-035, TP-BIT-037, TP-BIT-040, TP-BIT-041

---------------------------------------------------------------------------------------------------
## AREA BTALU

### CG-BTALU-001: gen_cg_btalu_branch
- Features: F-BTALU-001, F-BTALU-005, F-BTALU-006, F-BTALU-007, F-BTALU-009, F-BTALU-015
- Sample: RVFI retirement of a conditional branch (BRANCH or c.beqz/c.bnez, rvfi_trap == 0); condition: previous and next retirements exist; anti-vacuity: taken is derived from pc_wdata, redirect from an ibus request for the branch target (or pc+len) issued after the branch was fetched, the counter deltas from rvfi_ext_mhpmcounters of the configured event counters; a hit proves the sampled timing/redirect/count tuple was observed.
- Coverpoints:
  - cp_taken = (rvfi_pc_wdata != pc + len): bins no{0}, yes{1}
  - cp_direction = sign of imm: bins fwd{imm > 0}, bwd{imm < 0}, self{imm == 0}
  - cp_target_align = target[1]: bins word{0}, half{1}
  - cp_distance = |imm|: bins short{[0:62]}, mid{[64:2046]}, far{[2048:4092]}, max_fwd{4094}, max_bwd{4096}
  - cp_dit = cpuctrlsts.data_ind_timing (TB CSR model): bins off{0}, on{1}
  - cp_delta = retire delta to the next retirement: bins d1{1}, d2{2}, d3plus{[3:$]}
  - cp_redirect = ibus monitor saw a redirect request after this branch: bins no{0}, yes{1}
  - cp_wrap = carry out of pc + imm, iff taken: bins no{0}, yes{1}
  - cp_fetch_stall = ibus monitor: bins no{0}, yes{1}
  - cp_tbranch_inc = delta of the mhpmcounter configured for taken-branch: bins inc0{0}, inc1{1}
  - cp_branch_inc = delta of the mhpmcounter configured for branch: bins inc0{0}, inc1{1}
- Crosses:
  - cr_taken_dir_align = cp_taken x cp_direction x cp_target_align: bins auto{all combinations}; ignore self with not-taken and target half for self at word pc: geometry
  - cr_taken_dit_delta = cp_taken x cp_dit x cp_delta x cp_fetch_stall: bins nt_dit0_d1{no, off, d1, no}, t_dit0_d2{yes, off, d2, no}, nt_dit1_d2{no, on, d2, no}, t_dit1_d2{yes, on, d2, no}; ignore other combinations: stall-dependent; nt_dit1_d1 and t_*_d1 are impossible by pipeline construction (a hit is a checker failure)
  - cr_taken_dit_redirect = cp_taken x cp_dit x cp_redirect: bins nt_dit0_noredir{no, off, no}, t_dit0_redir{yes, off, yes}, nt_dit1_redir{no, on, yes}, t_dit1_redir{yes, on, yes}; ignore nt_dit0_redir, t_dit0_noredir, nt_dit1_noredir, t_dit1_noredir: contradict the RTL rule (a hit is a checker failure)
  - cr_taken_distance = cp_taken x cp_distance: bins auto{all combinations}
  - cr_wrap = cp_taken x cp_wrap: bins auto{all combinations}; ignore not-taken: guarded
  - cr_perf = cp_taken x cp_dit x cp_tbranch_inc: bins t_dit0_inc1{yes, off, inc1}, nt_dit0_inc0{no, off, inc0}, t_dit1_inc1{yes, on, inc1}, nt_dit1_inc0{no, on, inc0}, nt_dit1_inc1{no, on, inc1}; ignore t_*_inc0 and nt_dit0_inc1: contradict the doc rule (a hit is a checker failure); nt_dit1_inc1 is the B11 witness bin
  - cr_perf_branch = cp_taken x cp_branch_inc: bins auto{all combinations}; ignore inc0: every branch counts
- Adopted (riscv-dv): none
- TP items: TP-BTALU-001, TP-BTALU-005, TP-BTALU-006, TP-BTALU-007, TP-BTALU-009, TP-BTALU-015, TP-BTALU-016, TP-BTALU-017

### CG-BTALU-002: gen_cg_btalu_jump
- Features: F-BTALU-002, F-BTALU-003, F-BTALU-004, F-BTALU-007, F-BTALU-008, F-BTALU-009, F-BTALU-012, F-BTALU-014
- Sample: RVFI retirement of jal/jalr/fence.i/c.j/c.jal/c.jr/c.jalr with rvfi_trap == 0; condition: next retirement exists; anti-vacuity: pc_wdata bit 0 and the next pc_rdata are both observed, so cr_odd_bit0 records the actual RVFI value for an actually-odd sum; the sequence coverpoint requires two consecutive control transfers.
- Coverpoints:
  - cp_type = decoded: bins jal{}, jalr{}, fence_i{}, c_j{}, c_jal{}, c_jr{}, c_jalr{}
  - cp_target_align = next rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_odd_sum = (rs1 + imm)[0], iff jalr/c.jr/c.jalr: bins no{0}, yes{1}
  - cp_pc_wdata_bit0 = rvfi_pc_wdata[0]: bins b0{0}, b1{1}
  - cp_wrap = carry out of the target sum: bins no{0}, yes{1}
  - cp_link_ok = rvfi_rd_wdata == pc + len, iff rd != 0: bins yes{1}
  - cp_delta = retire delta to the next retirement with fetch_stall == no: bins d2{2}, d3plus{[3:$]}
  - cp_seq = this and the previous retirement: bins br_to_jump{taken branch then this jump}, jal_to_jalr{jal then jalr}, jalr_to_branch{jalr then taken branch (sampled on the branch)}, br_br{two consecutive taken branches (sampled on the second)}, jump_to_odd_half{jump whose target is a compressed instruction at pc[1] == 1}, jump_self{target == own pc}, none{default}
- Crosses:
  - cr_type_align = cp_type x cp_target_align: bins auto{all combinations}
  - cr_odd_bit0 = cp_type x cp_odd_sum x cp_pc_wdata_bit0: bins jalr_odd_b1{jalr, yes, b1}, jalr_odd_b0{jalr, yes, b0}, c_jr_odd_b1{c_jr, yes, b1}, c_jr_odd_b0{c_jr, yes, b0}, c_jalr_odd_b1{c_jalr, yes, b1}, c_jalr_odd_b0{c_jalr, yes, b0}; ignore even sums and non-jalr types: bit 0 is always 0 there
  - cr_type_wrap = cp_type x cp_wrap: bins auto{all combinations}
  - cr_type_delta = cp_type x cp_delta: bins auto{all combinations}; ignore d3plus: stall-dependent
  - cr_type_seq = cp_type x cp_seq: bins auto{all combinations}; ignore none: not a corner; ignore jalr_to_branch/br_br with jump types: sampled on branches only
- Adopted (riscv-dv): none
- TP items: TP-BTALU-002, TP-BTALU-003, TP-BTALU-004, TP-BTALU-007, TP-BTALU-008, TP-BTALU-009, TP-BTALU-012, TP-BTALU-014, TP-BTALU-017, TP-ISA-019

### CG-BTALU-003: gen_cg_btalu_hazard_fault
- Features: F-BTALU-010, F-BTALU-011, F-BTALU-013
- Sample: RVFI retirement of a control-transfer instruction (branch/jal/jalr) or the instruction-access-fault trap entry that follows a taken transfer; condition: the monitor identifies the operand source from the previous retirement(s) and the WB state from the dbus monitor; anti-vacuity: each class needs a specific preceding access or writer; a hit proves the CTI executed under that hazard/fault condition.
- Coverpoints:
  - cp_cti = decoded: bins branch_taken{}, branch_not_taken{}, jal{}, jalr{}
  - cp_operand_src = source of rs1/rs2: bins rf{no recent writer}, fwd_alu{previous retirement is an ALU op writing rs1 or rs2}, load_stall{previous retirement is a load writing rs1 or rs2}
  - cp_wb_outstanding = dbus monitor when the CTI entered ID: bins none{}, load{}, store{}
  - cp_wb_error = the outstanding access faulted (data_err_i or PMP): bins no{0}, yes{1}
  - cp_redirect_count = ibus redirects observed for this CTI: bins zero{0}, one{1}, two{2}
  - cp_target_fault = trap on the target fetch: bins none{}, pmp_exec{PMP X denied}, bus_err{instr_err_i}
  - cp_mtval_target_ok = mtval read-back == target address, iff target_fault: bins yes{1}
  - cp_dmem_delay = dbus monitor rvalid latency class of the outstanding access, iff wb_outstanding: bins min1{1}, short{[2:4]}, long{[5:$]}
- Crosses:
  - cr_cti_src = cp_cti x cp_operand_src: bins auto{all combinations}; ignore jal with fwd_alu/load_stall: no register operand
  - cr_cti_wb = cp_cti x cp_wb_outstanding x cp_wb_error: bins auto{all combinations}; ignore none with yes: no access cannot error
  - cr_cti_redirects = cp_cti x cp_wb_outstanding x cp_redirect_count: bins auto{all combinations}; ignore two: never legal (a hit is a checker failure); ignore branch_not_taken with one: no redirect without DIT
  - cr_cti_fault = cp_cti x cp_target_fault: bins auto{all combinations}; ignore branch_not_taken and none: no target fetch / not the corner
  - cr_src_delay = cp_operand_src x cp_dmem_delay: bins auto{all combinations}; ignore rf/fwd_alu: guarded
- Adopted (riscv-dv): none
- TP items: TP-BTALU-003, TP-BTALU-010, TP-BTALU-011, TP-BTALU-013, TP-BTALU-017

---------------------------------------------------------------------------------------------------
## Counts

- Covergroups: 40 (per area {'ISA': 11, 'MUL': 5, 'CMP': 10, 'BIT': 11, 'BTALU': 3})
- Coverpoints: 304; crosses: 188
- Coverpoint bins: 1367 (explicitly named `name{...}` bins; ranges count as one bin each)
- Cross bins: 132 explicitly named cross bins plus 161 `auto` cross sets; the auto sets
  expand to at most 7084 auto-cross bins before the stated ignores (product of the crossed
  coverpoints' bin counts; the fcov-expectation manifest expands each `auto` reference to the
  auto-bin set urg reports, minus the ignores written on the cross line)
- Adopted bins: 0 (see tp_isa.md Open questions OQ-2)
- Trace: trace_feat_tp_isa.csv (332 rows) and trace_tp_bin_isa.csv (1164 rows) were
  regenerated from tp_isa.md and this file by the fix script (covergroup column = CG-ID); every bin
  referenced by a TP item exists here, every F-ID of the area (incl. ALIAS/FOLDED and the four new
  features F-MUL-028, F-CMP-069, F-CMP-070, F-BIT-041) maps to >= 1 TP item and >= 1 bin, TP/CG ids
  are consecutive per area, and all five files are ASCII (verified by the same script).

## Probe candidates

Every covergroup above samples from the RVFI monitor, the ibus/dbus monitors, the irq/debug pin
drivers' timestamps, or the TB CSR model (predicted from retired CSR writes). One bin family
cannot be sampled from the boundary or RVFI:

- CG-CMP-008.cp_event.dummy_inserted (and the derived cross bins cr_event_phase_outcome.dummy_ls,
  dummy_commit, cr_insn_event.*/dummy_inserted): needs the dummy-instruction indication while a
  Zcmp expansion is in flight. Dummy instructions are architecturally invisible and excluded from
  RVFI (rvfi_stage_valid_d[0] masks dummy_instr_id); the only boundary trace is a fetch/retire
  timing gap, which is ambiguous under memory-response randomization. Candidate signal: the
  ibex_core output port dummy_instr_id_o as wired inside gen_dut_top (tb-infra probe P1; rtl-arch
  section 9 notes it is a core port, so a wrapper-internal net observation rather than an RTL
  probe). Coverage-only; no checker depends on it (gen_chk_zcmp_seq counts stores/loads from the
  RVFI/dbus streams). Needed by TP-CMP-065 (B8 repro). The DV Lead decides; if rejected, the three
  dummy bins become ignore_bins with reason "probe P1 rejected" and TP-CMP-065 keeps its dbus-count
  fire-check without the insertion-count precondition.

- CG-MUL-005 (F-MUL-028, TP-MUL-030) relies on the bound SVA module gen_sva_multdiv (assert
  (div_en_i == 0 && md_state_q != MD_IDLE) |=> $stable(md_state_q); cover the antecedent) inside
  ibex_multdiv_fast. The freeze arc has no boundary observable; the bind is coverage/assertion-only
  and no checker depends on it (probe candidate P<n>, number assigned by TB Infra; tp_isa.md OQ-9).
  cp_sva_checked is the only bin that needs it; if the bind is rejected it becomes ignore_bins with
  reason "probe rejected" and TP-MUL-030 keeps its RVFI fire-check.

No other bin needs an internal signal. Bins that look internal but are boundary-derived: retire
deltas (rvfi_ext_mcycle), fetch_stall / wb_busy (ibus and dbus monitor request/response timing),
data_ind_timing / dcsr / mstatus.TW / icache_enable (TB CSR model from retired csrw on RVFI plus
csrr read-back), Zcmp micro-op index and phase (rvfi_ext_expanded_insn* tags and the synthesized
rvfi_insn), event-mid-op (pin driver assertion timestamps compared with the retirement window),
perf-counter deltas (rvfi_ext_mhpmcounters).


# 3.2 Areas CSR, PRV: Control and status registers; privilege modes M/U and mstatus semantics


T-006 subagent output for the DV Lead. Areas: CSR (F-CSR-001..103) and PRV (F-PRV-001..035).
Feature source: dv/auto_dv/work/dv-lead/parts/gen_part_csr.md. Companion test plan: tp_csr.md.

Conventions
- All covergroups live in the gen_ namespace (gen_cg_csr_*, gen_cg_prv_*); none extends an RTL
  covergroup. Sampling is from the DUT boundary and RVFI only unless the bin is listed under
  "Probe candidates" at the end.
- Parameter-derived counts: MHPMCounterNum = 10 (counters 3..12: bins hpm3..hpm12 are
  3..3+MHPMCounterNum-1), PMPNumRegions = 16 (pmpcfg0..3 = PMPNumRegions/4 registers, pmpaddr0..15),
  irq_fast width = 15 (mie/mip bits 30:16, fast ids f0..f14), DbgHwBreakNum = 1 (tselect clamp).
  Bin lists written as hpm3, hpm4, ..., hpm12 are generated from the parameter, never typed.
- "csr address class" (cp_aclass in CG-CSR-001) is a TB classifier of rvfi_insn[31:20]:
  rw_m = implemented M-level RW with storage (mstatus, mie, mtvec, mcounteren, mcountinhibit,
  mscratch, mepc, mcause, mtval, mcycle(h), minstret(h), mhpmcounter3..12, mseccfg, cpuctrlsts,
  secureseed); wi_m = implemented, writes silently ignored (misa, mstatush, menvcfg, menvcfgh,
  mhpmevent3..31, mhpmcounter3h..12h, mhpmcounter13..31(h), mip, mseccfgh, tdata3, mcontext,
  mscontext); trig = tselect, tdata1, tdata2; pmp = pmpcfg0..3, pmpaddr0..15; dbg_only = 0x7B0..0x7B3;
  info_ro = 0xF11..0xF15; alias_impl = 0xC00, 0xC02, 0xC03..0xC0C and +0x80 halves; alias_unimpl =
  0xC0D..0xC1F, 0xC8D..0xC9F; time = 0xC01, 0xC81; s_lvl = 0x5A8; cheriot = 0xBC1, 0xBC2, 0xBC4;
  hole_lo = 0x000..0x2FF; hole_m = unimplemented addresses in 0x300..0xBFF (incl. 0x7B4..0x7BF);
  hole_ro = unimplemented addresses with [11:10] = 11 other than time.
- "illegal class set" (cp_iclass) is the TB's own evaluation of the four RTL classes (priv,
  write_ro, unimpl, dbg) after the rs1 = x0 / uimm = 0 demotion to READ; it is coverage of the
  stimulus, not a checker.
- "readback pair" = a CSR write op retired without trap followed by the next csrr of the same
  address before any other write to it; gen_chk_csr_readback compares the pair.
- Write pattern classes (cp_wpat): rand = uniform 32-bit; all1 = 0xFFFF_FFFF; all0 = 0; legal_only =
  only writable bits set; illegal_only = only read-only/legalised bits set; msb_only = 0x8000_0000.
- Bin names are [a-z0-9_]; every bin is written name{meaning}. Cross bins name the combination.
- Adopted (riscv-dv) is "none" everywhere: the riscv-dv tree is outside this subagent's read scope.
- Feature lists may name IDs that gen_part_csr.md marks ALIAS or FOLDED (Status line). Every FOLDED
  entry names the bin here that now carries it; ALIAS IDs resolve to the canonical feature of the
  owning area. No bin was added or removed for the fold: the restated edges already had bins here.

## Covergroups: CSR

### CG-CSR-001: gen_cg_csr_access_class
- Features: F-CSR-001, F-CSR-002, F-CSR-003, F-CSR-004, F-CSR-005, F-CSR-009, F-CSR-011, F-CSR-012, F-CSR-013, F-CSR-014, F-CSR-015, F-CSR-016, F-CSR-017, F-CSR-018, F-CSR-057, F-CSR-097, F-CSR-103, F-PRV-034
- Sample: rvfi_valid with rvfi_insn opcode SYSTEM (0x73) and funct3 != 000 (every CSR instruction, trapped or not); condition: rvfi_valid && is_csr_insn(rvfi_insn); anti-vacuity: non-CSR retirements never sample, so a hit proves a CSR instruction of that op / operand / address class retired or trapped in the sampled privilege and debug state; the outcome is rvfi_trap of the same retirement.
- Coverpoints:
  - cp_op = rvfi_insn[14:12]: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}, f3_100{100 illegal funct3}
  - cp_rs1 = rvfi_insn[19:15] (rs1 or uimm): bins zero{0}, nonzero{1..31}
  - cp_rd = rvfi_insn[11:7]: bins x0{0}, nonx0{1..31}
  - cp_priv = rvfi_mode: bins m{3}, u{0}; ignore_bins s_h{1,2}: priv_lvl_q only ever holds M or U
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_aclass = TB address classifier of rvfi_insn[31:20]: bins rw_m{implemented RW with storage}, wi_m{implemented write-ignored}, trig{tselect tdata1 tdata2}, pmp{pmpcfg0..3 pmpaddr0..15}, dbg_only{0x7B0..0x7B3}, info_ro{0xF11..0xF15}, alias_impl{0xC00 0xC02 0xC03..0xC0C +0x80}, alias_unimpl{0xC0D..0xC1F 0xC8D..0xC9F}, time{0xC01 0xC81}, s_lvl{0x5A8}, cheriot{0xBC1 0xBC2 0xBC4}, hole_lo{0x000..0x2FF}, hole_m{unimplemented 0x300..0xBFF}, hole_ro{unimplemented [11:10]=11 except time}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_iclass = TB illegal class set after demotion: bins none{no class}, priv{priv only}, wro{write_ro only}, unimpl{unimpl only}, dbg{dbg only}, multi{two or more classes}
- Crosses:
  - cr_rs1zero_ro = cp_op x cp_rs1 x cp_aclass x cp_trap (read-only address classes only): bins csrrs_x0_info_ok{csrrs zero info_ro ok}, csrrc_x0_info_ok{csrrc zero info_ro ok}, csrrsi_0_info_ok{csrrsi zero info_ro ok}, csrrci_0_info_ok{csrrci zero info_ro ok}, csrrs_x0_alias_ok{csrrs zero alias_impl ok}, csrrc_x0_alias_ok{csrrc zero alias_impl ok}, csrrsi_0_alias_ok{csrrsi zero alias_impl ok}, csrrci_0_alias_ok{csrrci zero alias_impl ok}, csrrs_nz_info_trap{csrrs nonzero info_ro trap}, csrrc_nz_info_trap{csrrc nonzero info_ro trap}, csrrsi_nz_info_trap{csrrsi nonzero info_ro trap}, csrrci_nz_info_trap{csrrci nonzero info_ro trap}, csrrs_nz_alias_trap{csrrs nonzero alias_impl trap}, csrrc_nz_alias_trap{csrrc nonzero alias_impl trap}, csrrw_x0_info_trap{csrrw zero info_ro trap}, csrrwi_0_info_trap{csrrwi zero info_ro trap}, csrrw_x0_alias_trap{csrrw zero alias_impl trap}, csrrwi_0_alias_trap{csrrwi zero alias_impl trap}, csrrw_nz_info_trap{csrrw nonzero info_ro trap}, csrrw_nz_alias_trap{csrrw nonzero alias_impl trap}; ignore csrrs/csrrc/csrrsi/csrrci with zero operand x trap on info_ro/alias_impl in M-mode: demoted to READ, cannot trap; ignore csrrw x ok on read-only classes: always illegal_csr_write
  - cr_rd_x0_write = cp_op x cp_rd x cp_aclass: bins csrrw_rdx0_rw_m{csrrw x0 rw_m}, csrrwi_rdx0_rw_m{csrrwi x0 rw_m}, csrrs_rdx0_rw_m{csrrs x0 rw_m}, csrrc_rdx0_rw_m{csrrc x0 rw_m}, csrrsi_rdx0_rw_m{csrrsi x0 rw_m}, csrrci_rdx0_rw_m{csrrci x0 rw_m}, csrrw_rdx0_info_ro{csrrw x0 info_ro}, csrrw_rdx0_wi_m{csrrw x0 wi_m}, csrrw_rdnz_rw_m{csrrw nonx0 rw_m}
  - cr_priv_aclass_trap = cp_priv x cp_aclass x cp_trap: bins u_rw_m_trap{u rw_m trap}, u_wi_m_trap{u wi_m trap}, u_trig_trap{u trig trap}, u_pmp_trap{u pmp trap}, u_dbg_only_trap{u dbg_only trap}, u_info_ro_trap{u info_ro trap}, u_alias_impl_ok{u alias_impl ok}, u_alias_impl_trap{u alias_impl trap}, u_alias_unimpl_trap{u alias_unimpl trap}, u_time_trap{u time trap}, u_s_lvl_trap{u s_lvl trap}, u_cheriot_trap{u cheriot trap}, u_hole_lo_trap{u hole_lo trap}, u_hole_m_trap{u hole_m trap}, u_hole_ro_trap{u hole_ro trap}, m_rw_m_ok{m rw_m ok}, m_wi_m_ok{m wi_m ok}, m_trig_ok{m trig ok}, m_pmp_ok{m pmp ok}, m_dbg_only_trap{m dbg_only trap}, m_info_ro_ok{m info_ro ok}, m_alias_impl_ok{m alias_impl ok}, m_alias_unimpl_ok{m alias_unimpl ok}, m_time_trap{m time trap}, m_s_lvl_ok{m s_lvl ok}, m_cheriot_trap{m cheriot trap}, m_hole_lo_trap{m hole_lo trap}, m_hole_m_trap{m hole_m trap}, m_hole_ro_trap{m hole_ro trap}; ignore u x {rw_m, wi_m, trig, pmp, dbg_only, info_ro, s_lvl, cheriot, hole_m} x ok: csr[9:8] > U always traps; ignore m x {time, cheriot, hole_lo, hole_m, hole_ro} x ok: unimplemented addresses always trap
  - cr_dbg_access = cp_dbg x cp_aclass x cp_trap: bins dbg_dbgonly_ok{dbg dbg_only ok}, nondbg_dbgonly_trap{nondbg dbg_only trap}, dbg_hole_m_trap{dbg hole_m trap incl 0x7B4..0x7BF}, dbg_trig_ok{dbg trig ok}, dbg_rw_m_ok{dbg rw_m ok}, dbg_info_ro_ok{dbg info_ro ok}; ignore nondbg x dbg_only x ok: illegal_csr_dbg always fires outside debug mode
  - cr_iclass_priv = cp_iclass x cp_priv: bins none_m{none m}, none_u{none u}, priv_u{priv u}, wro_m{wro m}, wro_u{wro u alias write}, unimpl_m{unimpl m}, unimpl_u{unimpl u U-level hole}, dbg_m{dbg m}, multi_u{multi u}, multi_m{multi m}; ignore priv_m: csr[9:8] > M is impossible
  - cr_f3_100 = cp_op x cp_trap (f3_100 only): bins f3_100_trap{f3_100 trap}; ignore f3_100_ok: decoder csr_illegal always fires
- Adopted (riscv-dv): none
- TP items: TP-CSR-001, TP-CSR-002, TP-CSR-003, TP-CSR-004, TP-CSR-005, TP-CSR-009, TP-CSR-011, TP-CSR-012, TP-CSR-013, TP-CSR-014, TP-CSR-015, TP-CSR-016, TP-CSR-017, TP-CSR-018, TP-CSR-021, TP-CSR-049, TP-CSR-055, TP-CSR-056, TP-CSR-057, TP-CSR-080, TP-CSR-083, TP-CSR-098, TP-CSR-104, TP-CSR-110, TP-CSR-111, TP-CSR-112, TP-CSR-116, TP-CSR-117, TP-CSR-118, TP-PRV-033

### CG-CSR-002: gen_cg_csr_trap_setup_warl
- Features: F-CSR-021, F-CSR-022, F-CSR-023, F-CSR-024, F-CSR-025, F-CSR-027, F-CSR-028, F-CSR-029, F-CSR-030, F-CSR-035, F-CSR-036, F-CSR-037, F-CSR-050, F-CSR-051, F-CSR-052, F-PRV-035
- Sample: gen_chk_csr_readback pair completion for a trap-setup CSR (mstatus, misa, mie, mtvec, mcounteren, mstatush, menvcfg, menvcfgh); condition: pair closed (write retired without trap, read-back retired); anti-vacuity: pairs exist only when the program writes then reads the same CSR, so a hit proves the legalised prediction for that write pattern was compared against the read-back.
- Coverpoints:
  - cp_csr = pair address: bins mstatus{0x300}, misa{0x301}, mie{0x304}, mtvec{0x305}, mcounteren{0x306}, mstatush{0x310}, menvcfg{0x30A}, menvcfgh{0x31A}
  - cp_op = write op of the pair: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only}, illegal_only{RO or legalised bits only}, msb_only{0x8000_0000}
  - cp_rd = rd of the write: bins x0{0}, nonx0{1..31}
  - cp_mpp_w = written mstatus[12:11] (mstatus pairs only): bins u{00}, s{01}, h{10}, m{11}
  - cp_mst_mie_w = written mstatus[3]: bins b0{0}, b1{1}
  - cp_mst_mpie_w = written mstatus[7]: bins b0{0}, b1{1}
  - cp_mst_mprv_w = written mstatus[17]: bins b0{0}, b1{1}
  - cp_mst_tw_w = written mstatus[21]: bins b0{0}, b1{1}
  - cp_mtvec_mode_w = written mtvec[1:0] (mtvec pairs only): bins d00{00 direct}, v01{01 vectored}, r10{10}, r11{11}
  - cp_mtvec_lo_w = written mtvec[7:2]: bins zero{0}, nonzero{!=0}
  - cp_mtvec_base_w = written mtvec[31:8] class: bins low{< 0x1000}, boot_page{== boot_addr_i[31:8]}, high{bit 31 set}, rand{other}
  - cp_mie_w = written mie bit groups (mie pairs only): bins std_only{bits 3 7 11 only}, fast_only{bits 30:16 only}, std_fast{both}, ro_only{only RO bits}, all_fast{all irq_fast width bits}
  - cp_mcen_gate = mcounteren_writable_i at the write: bins on{IbexMuBiOn}, off{IbexMuBiOff}, invalid{other encodings}
  - cp_mcen_w = written mcounteren bit class (mcounteren pairs only): bins cy{bit 0}, ir{bit 2}, hpm3{bit 3}, hpm4{bit 4}, hpm5{bit 5}, hpm6{bit 6}, hpm7{bit 7}, hpm8{bit 8}, hpm9{bit 9}, hpm10{bit 10}, hpm11{bit 11}, hpm12{bit 12}, tm_ro{bit 1}, hi_ro{bits 31:13}, all1{all bits}
- Crosses:
  - cr_csr_op = cp_csr x cp_op: bins mstatus_csrrw{mstatus csrrw}, mstatus_csrrs{mstatus csrrs}, mstatus_csrrc{mstatus csrrc}, mstatus_csrrwi{mstatus csrrwi}, mstatus_csrrsi{mstatus csrrsi}, mstatus_csrrci{mstatus csrrci}, misa_csrrw{misa csrrw}, misa_csrrs{misa csrrs}, misa_csrrc{misa csrrc}, misa_csrrwi{misa csrrwi}, misa_csrrsi{misa csrrsi}, misa_csrrci{misa csrrci}, mie_csrrw{mie csrrw}, mie_csrrs{mie csrrs}, mie_csrrc{mie csrrc}, mie_csrrwi{mie csrrwi}, mie_csrrsi{mie csrrsi}, mie_csrrci{mie csrrci}, mtvec_csrrw{mtvec csrrw}, mtvec_csrrs{mtvec csrrs}, mtvec_csrrc{mtvec csrrc}, mtvec_csrrwi{mtvec csrrwi}, mtvec_csrrsi{mtvec csrrsi}, mtvec_csrrci{mtvec csrrci}, mcounteren_csrrw{mcounteren csrrw}, mcounteren_csrrs{mcounteren csrrs}, mcounteren_csrrc{mcounteren csrrc}, mcounteren_csrrwi{mcounteren csrrwi}, mcounteren_csrrsi{mcounteren csrrsi}, mcounteren_csrrci{mcounteren csrrci}, mstatush_csrrw{mstatush csrrw}, mstatush_csrrs{mstatush csrrs}, mstatush_csrrc{mstatush csrrc}, mstatush_csrrwi{mstatush csrrwi}, mstatush_csrrsi{mstatush csrrsi}, mstatush_csrrci{mstatush csrrci}, menvcfg_csrrw{menvcfg csrrw}, menvcfg_csrrs{menvcfg csrrs}, menvcfg_csrrc{menvcfg csrrc}, menvcfg_csrrwi{menvcfg csrrwi}, menvcfg_csrrsi{menvcfg csrrsi}, menvcfg_csrrci{menvcfg csrrci}, menvcfgh_csrrw{menvcfgh csrrw}, menvcfgh_csrrs{menvcfgh csrrs}, menvcfgh_csrrc{menvcfgh csrrc}, menvcfgh_csrrwi{menvcfgh csrrwi}, menvcfgh_csrrsi{menvcfgh csrrsi}, menvcfgh_csrrci{menvcfgh csrrci}
  - cr_csr_wpat = cp_csr x cp_wpat: bins mstatus_rand{mstatus rand}, mstatus_all1{mstatus all1}, mstatus_all0{mstatus all0}, mstatus_legal{mstatus legal_only}, mstatus_illegal{mstatus illegal_only}, mstatus_msb{mstatus msb_only}, misa_rand{misa rand}, misa_all1{misa all1}, misa_all0{misa all0}, misa_legal{misa legal_only}, misa_illegal{misa illegal_only}, misa_msb{misa msb_only}, mie_rand{mie rand}, mie_all1{mie all1}, mie_all0{mie all0}, mie_legal{mie legal_only}, mie_illegal{mie illegal_only}, mie_msb{mie msb_only}, mtvec_rand{mtvec rand}, mtvec_all1{mtvec all1}, mtvec_all0{mtvec all0}, mtvec_legal{mtvec legal_only}, mtvec_illegal{mtvec illegal_only}, mtvec_msb{mtvec msb_only}, mcounteren_rand{mcounteren rand}, mcounteren_all1{mcounteren all1}, mcounteren_all0{mcounteren all0}, mcounteren_legal{mcounteren legal_only}, mcounteren_illegal{mcounteren illegal_only}, mcounteren_msb{mcounteren msb_only}, mstatush_rand{mstatush rand}, mstatush_all1{mstatush all1}, mstatush_all0{mstatush all0}, mstatush_msb{mstatush msb_only}, menvcfg_rand{menvcfg rand}, menvcfg_all1{menvcfg all1}, menvcfg_all0{menvcfg all0}, menvcfg_msb{menvcfg msb_only}, menvcfgh_rand{menvcfgh rand}, menvcfgh_all1{menvcfgh all1}, menvcfgh_all0{menvcfgh all0}, menvcfgh_msb{menvcfgh msb_only}; ignore {mstatush, menvcfg, menvcfgh} x {legal_only, illegal_only}: no writable bit exists, the classes collapse into all0/all1
  - cr_mpp_op = cp_mpp_w x cp_op: bins mpp_s_csrrw{s csrrw}, mpp_h_csrrw{h csrrw}, mpp_s_csrrs{s csrrs}, mpp_h_csrrsi{h csrrsi}, mpp_m_csrrw{m csrrw}, mpp_m_csrrs{m csrrs}, mpp_u_csrrw{u csrrw}, mpp_u_csrrc{u csrrc}
  - cr_mst_fields = cp_mst_mie_w x cp_mst_mpie_w x cp_mst_mprv_w x cp_mst_tw_w: bins all0{0 0 0 0}, all1{1 1 1 1}, mie_only{1 0 0 0}, mpie_only{0 1 0 0}, mprv_only{0 0 1 0}, tw_only{0 0 0 1}, mprv_tw{0 0 1 1}, mie_mpie{1 1 0 0}
  - cr_mtvec_mode_lo = cp_mtvec_mode_w x cp_mtvec_lo_w: bins d00_zero{d00 zero}, d00_nz{d00 nonzero}, v01_zero{v01 zero}, v01_nz{v01 nonzero}, r10_zero{r10 zero}, r10_nz{r10 nonzero}, r11_zero{r11 zero}, r11_nz{r11 nonzero}
  - cr_mtvec_base_op = cp_mtvec_base_w x cp_op: bins low_csrrw{low csrrw}, high_csrrw{high csrrw}, boot_csrrw{boot_page csrrw}, rand_csrrw{rand csrrw}, rand_csrrs{rand csrrs}, rand_csrrc{rand csrrc}, high_csrrs{high csrrs}
  - cr_mie_w_op = cp_mie_w x cp_op: bins std_csrrw{std_only csrrw}, fast_csrrw{fast_only csrrw}, both_csrrw{std_fast csrrw}, ro_csrrw{ro_only csrrw}, allfast_csrrw{all_fast csrrw}, std_csrrs{std_only csrrs}, fast_csrrs{fast_only csrrs}, std_csrrc{std_only csrrc}, fast_csrrc{fast_only csrrc}, std_csrrsi{std_only csrrsi}, std_csrrci{std_only csrrci}
  - cr_mcen_gate_w = cp_mcen_gate x cp_mcen_w: bins on_cy{on cy}, on_ir{on ir}, on_hpm3{on hpm3}, on_hpm12{on hpm12}, on_tm_ro{on tm_ro}, on_hi_ro{on hi_ro}, on_all1{on all1}, off_all1{off all1}, off_cy{off cy}, invalid_all1{invalid all1}, invalid_ir{invalid ir}
- Adopted (riscv-dv): none
- TP items: TP-CSR-003, TP-CSR-004, TP-CSR-021, TP-CSR-022, TP-CSR-023, TP-CSR-024, TP-CSR-025, TP-CSR-026, TP-CSR-027, TP-CSR-028, TP-CSR-029, TP-CSR-030, TP-CSR-031, TP-CSR-035, TP-CSR-036, TP-CSR-050, TP-CSR-051, TP-CSR-052, TP-CSR-099, TP-CSR-101, TP-CSR-116, TP-PRV-034

### CG-CSR-003: gen_cg_csr_trap_handling_warl
- Features: F-CSR-038, F-CSR-039, F-CSR-040, F-CSR-042, F-CSR-043, F-CSR-044, F-CSR-045, F-CSR-046, F-CSR-047, F-CSR-032, F-CSR-033
- Sample: gen_chk_csr_readback pair completion for mscratch, mepc, mcause, mtval, mip; condition: pair closed; anti-vacuity: as CG-CSR-002; for mip the "pair" is a write op followed by a read with the irq pins held, so a hit proves the write-ignored prediction was compared.
- Coverpoints:
  - cp_csr = pair address: bins mscratch{0x340}, mepc{0x341}, mcause{0x342}, mtval{0x343}, mip{0x344}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only}, illegal_only{RO bits only}, msb_only{0x8000_0000}
  - cp_mepc_lo_w = written mepc[1:0] (mepc pairs only): bins b00{00}, b01{01}, b10{10}, b11{11}
  - cp_mcause_hi_w = written mcause[31:30] (mcause pairs only): bins h00{00}, h01{01}, h10{10 irq_ext}, h11{11 irq_int}
  - cp_mcause_mid_w = written mcause[29:5]: bins zero{0}, nonzero{!=0}
  - cp_mcause_code_w = written mcause[4:0]: bins c0{0}, c31{31}, other{1..30}
  - cp_mip_pins = irq pin set at the mip read: bins none{no pin}, sw{irq_software_i}, timer{irq_timer_i}, ext{irq_external_i}, fast_any{any irq_fast_i}, multi{two or more}
- Crosses:
  - cr_csr_op = cp_csr x cp_op: bins mscratch_csrrw{mscratch csrrw}, mscratch_csrrs{mscratch csrrs}, mscratch_csrrc{mscratch csrrc}, mscratch_csrrwi{mscratch csrrwi}, mscratch_csrrsi{mscratch csrrsi}, mscratch_csrrci{mscratch csrrci}, mepc_csrrw{mepc csrrw}, mepc_csrrs{mepc csrrs}, mepc_csrrc{mepc csrrc}, mepc_csrrwi{mepc csrrwi}, mepc_csrrsi{mepc csrrsi}, mepc_csrrci{mepc csrrci}, mcause_csrrw{mcause csrrw}, mcause_csrrs{mcause csrrs}, mcause_csrrc{mcause csrrc}, mcause_csrrwi{mcause csrrwi}, mcause_csrrsi{mcause csrrsi}, mcause_csrrci{mcause csrrci}, mtval_csrrw{mtval csrrw}, mtval_csrrs{mtval csrrs}, mtval_csrrc{mtval csrrc}, mtval_csrrwi{mtval csrrwi}, mtval_csrrsi{mtval csrrsi}, mtval_csrrci{mtval csrrci}, mip_csrrw{mip csrrw}, mip_csrrs{mip csrrs}, mip_csrrc{mip csrrc}, mip_csrrwi{mip csrrwi}, mip_csrrsi{mip csrrsi}, mip_csrrci{mip csrrci}
  - cr_csr_wpat = cp_csr x cp_wpat: bins mscratch_rand{mscratch rand}, mscratch_all1{mscratch all1}, mscratch_all0{mscratch all0}, mscratch_msb{mscratch msb_only}, mepc_rand{mepc rand}, mepc_all1{mepc all1}, mepc_all0{mepc all0}, mepc_legal{mepc legal_only}, mepc_illegal{mepc illegal_only bit0}, mepc_msb{mepc msb_only}, mcause_rand{mcause rand}, mcause_all1{mcause all1}, mcause_all0{mcause all0}, mcause_legal{mcause legal_only}, mcause_illegal{mcause illegal_only}, mcause_msb{mcause msb_only}, mtval_rand{mtval rand}, mtval_all1{mtval all1}, mtval_all0{mtval all0}, mtval_msb{mtval msb_only}, mip_rand{mip rand}, mip_all1{mip all1}, mip_all0{mip all0}, mip_msb{mip msb_only}; ignore {mscratch, mtval} x {legal_only, illegal_only}: all 32 bits writable, classes collapse into rand/all1; ignore mip x {legal_only, illegal_only}: no writable bit
  - cr_mcause_hi_mid = cp_mcause_hi_w x cp_mcause_mid_w: bins h00_zero{h00 zero}, h00_nz{h00 nonzero}, h01_zero{h01 zero}, h01_nz{h01 nonzero}, h10_zero{h10 zero}, h10_nz{h10 nonzero}, h11_zero{h11 zero}, h11_nz{h11 nonzero}
  - cr_mcause_hi_code = cp_mcause_hi_w x cp_mcause_code_w: bins h11_c0{h11 c0}, h11_c31{h11 c31}, h10_c0{h10 c0}, h10_other{h10 other}, h00_c31{h00 c31}, h01_other{h01 other}
  - cr_mepc_lo_op = cp_mepc_lo_w x cp_op: bins b01_csrrw{b01 csrrw}, b11_csrrw{b11 csrrw}, b10_csrrw{b10 csrrw}, b00_csrrw{b00 csrrw}, b01_csrrs{b01 csrrs}, b11_csrrsi{b11 csrrsi}, b01_csrrc{b01 csrrc}
  - cr_mip_pins_op = cp_mip_pins x cp_op: bins none_csrrw{none csrrw}, sw_csrrw{sw csrrw}, timer_csrrs{timer csrrs}, ext_csrrc{ext csrrc}, fast_csrrw{fast_any csrrw}, multi_csrrwi{multi csrrwi}, multi_csrrw{multi csrrw}
- Adopted (riscv-dv): none
- TP items: TP-CSR-001, TP-CSR-003, TP-CSR-032, TP-CSR-033, TP-CSR-038, TP-CSR-039, TP-CSR-040, TP-CSR-042, TP-CSR-043, TP-CSR-044, TP-CSR-045, TP-CSR-046, TP-CSR-047, TP-CSR-101, TP-CSR-116

### CG-CSR-004: gen_cg_csr_counter_warl
- Features: F-CSR-058, F-CSR-059, F-CSR-060, F-CSR-061, F-CSR-062, F-CSR-066, F-CSR-069, F-CSR-070, F-CSR-071, F-CSR-073
- Sample: gen_chk_csr_readback pair completion for a counter-family CSR (0xB00..0xB9F, 0x320, 0x323..0x33F); condition: pair closed; anti-vacuity: as CG-CSR-002; for running counters the prediction includes the elapsed-cycle / retired-instruction delta from gen_chk_counters, so a hit proves both models agreed on that write.
- Coverpoints:
  - cp_csr = pair address: bins mcycle{0xB00}, mcycleh{0xB80}, minstret{0xB02}, minstreth{0xB82}, hpm3{0xB03}, hpm4{0xB04}, hpm5{0xB05}, hpm6{0xB06}, hpm7{0xB07}, hpm8{0xB08}, hpm9{0xB09}, hpm10{0xB0A}, hpm11{0xB0B}, hpm12{0xB0C}, hpm3h{0xB83}, hpm4h{0xB84}, hpm5h{0xB85}, hpm6h{0xB86}, hpm7h{0xB87}, hpm8h{0xB88}, hpm9h{0xB89}, hpm10h{0xB8A}, hpm11h{0xB8B}, hpm12h{0xB8C}, hpm_unimpl{0xB0D..0xB1F}, hpm_unimpl_h{0xB8D..0xB9F}, mcountinhibit{0x320}, mhpmevent_impl{0x323..0x32C}, mhpmevent_unimpl{0x32D..0x33F}
  - cp_fam = counter family of cp_csr: bins cycle64{mcycle mcycleh}, instret64{minstret minstreth}, hpm32{hpm3..hpm12}, hpm32h{hpm3h..hpm12h}, hpm_unimpl{13..31 and h}, mcinh{mcountinhibit}, mhpmev{mhpmevent3..31}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, near_wrap{0xFFFF_FFF0..0xFFFF_FFFE}, small{1..31 uimm range}
  - cp_inhibit = the counter's mcountinhibit bit at the write: bins on{1}, off{0}
  - cp_mcinh_w = written mcountinhibit bit class (mcountinhibit pairs only): bins cy{bit 0}, ir{bit 2}, hpm3{bit 3}, hpm4{bit 4}, hpm5{bit 5}, hpm6{bit 6}, hpm7{bit 7}, hpm8{bit 8}, hpm9{bit 9}, hpm10{bit 10}, hpm11{bit 11}, hpm12{bit 12}, tm_ro{bit 1}, hi_ro{bits 31:13}, all1{all bits}
- Crosses:
  - cr_fam_op = cp_fam x cp_op: bins cycle64_csrrw{cycle64 csrrw}, cycle64_csrrs{cycle64 csrrs}, cycle64_csrrc{cycle64 csrrc}, cycle64_csrrwi{cycle64 csrrwi}, cycle64_csrrsi{cycle64 csrrsi}, cycle64_csrrci{cycle64 csrrci}, instret64_csrrw{instret64 csrrw}, instret64_csrrs{instret64 csrrs}, instret64_csrrc{instret64 csrrc}, instret64_csrrwi{instret64 csrrwi}, instret64_csrrsi{instret64 csrrsi}, instret64_csrrci{instret64 csrrci}, hpm32_csrrw{hpm32 csrrw}, hpm32_csrrs{hpm32 csrrs}, hpm32_csrrc{hpm32 csrrc}, hpm32_csrrwi{hpm32 csrrwi}, hpm32_csrrsi{hpm32 csrrsi}, hpm32_csrrci{hpm32 csrrci}, hpm32h_csrrw{hpm32h csrrw}, hpm32h_csrrs{hpm32h csrrs}, hpm32h_csrrc{hpm32h csrrc}, hpm32h_csrrwi{hpm32h csrrwi}, hpm32h_csrrsi{hpm32h csrrsi}, hpm32h_csrrci{hpm32h csrrci}, hpm_unimpl_csrrw{hpm_unimpl csrrw}, hpm_unimpl_csrrs{hpm_unimpl csrrs}, hpm_unimpl_csrrc{hpm_unimpl csrrc}, hpm_unimpl_csrrwi{hpm_unimpl csrrwi}, hpm_unimpl_csrrsi{hpm_unimpl csrrsi}, hpm_unimpl_csrrci{hpm_unimpl csrrci}, mcinh_csrrw{mcinh csrrw}, mcinh_csrrs{mcinh csrrs}, mcinh_csrrc{mcinh csrrc}, mcinh_csrrwi{mcinh csrrwi}, mcinh_csrrsi{mcinh csrrsi}, mcinh_csrrci{mcinh csrrci}, mhpmev_csrrw{mhpmev csrrw}, mhpmev_csrrs{mhpmev csrrs}, mhpmev_csrrc{mhpmev csrrc}, mhpmev_csrrwi{mhpmev csrrwi}, mhpmev_csrrsi{mhpmev csrrsi}, mhpmev_csrrci{mhpmev csrrci}
  - cr_fam_wpat = cp_fam x cp_wpat: bins cycle64_rand{cycle64 rand}, cycle64_all1{cycle64 all1}, cycle64_all0{cycle64 all0}, cycle64_near_wrap{cycle64 near_wrap}, cycle64_small{cycle64 small}, instret64_rand{instret64 rand}, instret64_all1{instret64 all1}, instret64_all0{instret64 all0}, instret64_near_wrap{instret64 near_wrap}, instret64_small{instret64 small}, hpm32_rand{hpm32 rand}, hpm32_all1{hpm32 all1}, hpm32_all0{hpm32 all0}, hpm32_near_wrap{hpm32 near_wrap}, hpm32_small{hpm32 small}, hpm32h_rand{hpm32h rand}, hpm32h_all1{hpm32h all1}, hpm32h_all0{hpm32h all0}, hpm_unimpl_rand{hpm_unimpl rand}, hpm_unimpl_all1{hpm_unimpl all1}, mcinh_rand{mcinh rand}, mcinh_all1{mcinh all1}, mcinh_all0{mcinh all0}, mcinh_small{mcinh small}, mhpmev_rand{mhpmev rand}, mhpmev_all1{mhpmev all1}, mhpmev_all0{mhpmev all0}
  - cr_csr_inhibit = cp_csr x cp_inhibit (writable counters): bins mcycle_on{mcycle on}, mcycle_off{mcycle off}, mcycleh_on{mcycleh on}, mcycleh_off{mcycleh off}, minstret_on{minstret on}, minstret_off{minstret off}, minstreth_on{minstreth on}, minstreth_off{minstreth off}, hpm3_on{hpm3 on}, hpm3_off{hpm3 off}, hpm4_on{hpm4 on}, hpm4_off{hpm4 off}, hpm5_on{hpm5 on}, hpm5_off{hpm5 off}, hpm6_on{hpm6 on}, hpm6_off{hpm6 off}, hpm7_on{hpm7 on}, hpm7_off{hpm7 off}, hpm8_on{hpm8 on}, hpm8_off{hpm8 off}, hpm9_on{hpm9 on}, hpm9_off{hpm9 off}, hpm10_on{hpm10 on}, hpm10_off{hpm10 off}, hpm11_on{hpm11 on}, hpm11_off{hpm11 off}, hpm12_on{hpm12 on}, hpm12_off{hpm12 off}
  - cr_mcinh_w_op = cp_mcinh_w x cp_op: bins cy_csrrs{cy csrrs}, cy_csrrc{cy csrrc}, ir_csrrs{ir csrrs}, ir_csrrc{ir csrrc}, hpm3_csrrsi{hpm3 csrrsi}, hpm12_csrrs{hpm12 csrrs}, tm_ro_csrrw{tm_ro csrrw}, hi_ro_csrrw{hi_ro csrrw}, all1_csrrw{all1 csrrw}, all1_csrrs{all1 csrrs}
- Adopted (riscv-dv): none
- TP items: TP-CSR-058, TP-CSR-059, TP-CSR-060, TP-CSR-061, TP-CSR-062, TP-CSR-064, TP-CSR-066, TP-CSR-069, TP-CSR-070, TP-CSR-071, TP-CSR-073, TP-CSR-101, TP-CSR-120

### CG-CSR-005: gen_cg_csr_umode_alias
- Features: F-CSR-015, F-CSR-050, F-CSR-053, F-CSR-054, F-CSR-055, F-CSR-056, F-CSR-057
- Sample: rvfi_valid with a CSR instruction to 0xC00..0xC9F (any mode, trapped or not); condition: rvfi_valid && is_csr_insn && addr[11:8] == 0xC && addr[7:5] inside {0, 4}; anti-vacuity: only alias accesses sample; a hit proves an alias of that index was accessed in that mode with that mcounteren state and the recorded outcome.
- Coverpoints:
  - cp_alias = addr class: bins cycle{0xC00}, cycleh{0xC80}, instret{0xC02}, instreth{0xC82}, hpm3{0xC03}, hpm4{0xC04}, hpm5{0xC05}, hpm6{0xC06}, hpm7{0xC07}, hpm8{0xC08}, hpm9{0xC09}, hpm10{0xC0A}, hpm11{0xC0B}, hpm12{0xC0C}, hpm3h{0xC83}, hpm4h{0xC84}, hpm5h{0xC85}, hpm6h{0xC86}, hpm7h{0xC87}, hpm8h{0xC88}, hpm9h{0xC89}, hpm10h{0xC8A}, hpm11h{0xC8B}, hpm12h{0xC8C}, hpm_unimpl{0xC0D..0xC1F}, hpm_unimpl_h{0xC8D..0xC9F}, time{0xC01}, timeh{0xC81}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_mcen_bit = mcounteren[addr[4:0]] as predicted by the CSR model (na for 13..31): bins set{1}, clr{0}, na{index 13..31 or 1}
  - cp_form = op form after demotion: bins rd_only{csrrs/csrrc x0, csrrsi/csrrci 0}, wr{any write op}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_mcen_onehot = mcounteren value class at the access: bins none{0}, cy{bit 0 only}, ir{bit 2 only}, hpm3{bit 3 only}, hpm4{bit 4 only}, hpm5{bit 5 only}, hpm6{bit 6 only}, hpm7{bit 7 only}, hpm8{bit 8 only}, hpm9{bit 9 only}, hpm10{bit 10 only}, hpm11{bit 11 only}, hpm12{bit 12 only}, multi{two or more bits}
  - cp_diag = (one-hot mcounteren index == alias index): bins diag{equal}, offdiag{different}, na{not one-hot}
- Crosses:
  - cr_priv_bit_trap = cp_priv x cp_mcen_bit x cp_trap (rd_only): bins u_set_ok{u set ok}, u_clr_trap{u clr trap}, u_na_trap{u na trap}, m_set_ok{m set ok}, m_clr_ok{m clr ok}, m_na_ok{m na ok}; ignore u_set_trap and u_clr_ok: the gate is deterministic; ignore m x trap for implemented aliases: M-mode reads never trap
  - cr_alias_u_ok = cp_alias x cp_priv(u) x cp_trap(ok): bins cycle{u cycle ok}, cycleh{u cycleh ok}, instret{u instret ok}, instreth{u instreth ok}, hpm3{u hpm3 ok}, hpm4{u hpm4 ok}, hpm5{u hpm5 ok}, hpm6{u hpm6 ok}, hpm7{u hpm7 ok}, hpm8{u hpm8 ok}, hpm9{u hpm9 ok}, hpm10{u hpm10 ok}, hpm11{u hpm11 ok}, hpm12{u hpm12 ok}, hpm3h{u hpm3h ok}, hpm4h{u hpm4h ok}, hpm5h{u hpm5h ok}, hpm6h{u hpm6h ok}, hpm7h{u hpm7h ok}, hpm8h{u hpm8h ok}, hpm9h{u hpm9h ok}, hpm10h{u hpm10h ok}, hpm11h{u hpm11h ok}, hpm12h{u hpm12h ok}; ignore hpm_unimpl, hpm_unimpl_h, time, timeh: never legal in U
  - cr_alias_u_trap = cp_alias x cp_priv(u) x cp_trap(trap): bins cycle{u cycle trap}, cycleh{u cycleh trap}, instret{u instret trap}, instreth{u instreth trap}, hpm3{u hpm3 trap}, hpm4{u hpm4 trap}, hpm5{u hpm5 trap}, hpm6{u hpm6 trap}, hpm7{u hpm7 trap}, hpm8{u hpm8 trap}, hpm9{u hpm9 trap}, hpm10{u hpm10 trap}, hpm11{u hpm11 trap}, hpm12{u hpm12 trap}, hpm3h{u hpm3h trap}, hpm12h{u hpm12h trap}, hpm_unimpl{u hpm_unimpl trap}, hpm_unimpl_h{u hpm_unimpl_h trap}, time{u time trap}, timeh{u timeh trap}
  - cr_alias_m = cp_alias x cp_priv(m) x cp_trap: bins m_time_trap{m time trap}, m_timeh_trap{m timeh trap}, m_hpm_unimpl_ok{m hpm_unimpl ok}, m_hpm_unimpl_h_ok{m hpm_unimpl_h ok}, m_cycle_ok{m cycle ok}, m_cycleh_ok{m cycleh ok}, m_instret_ok{m instret ok}, m_instreth_ok{m instreth ok}, m_hpm3_ok{m hpm3 ok}, m_hpm12_ok{m hpm12 ok}, m_hpm3h_ok{m hpm3h ok}
  - cr_diag_u = cp_diag x cp_priv(u) x cp_trap: bins diag_ok{diag ok}, offdiag_trap{offdiag trap}; ignore diag_trap and offdiag_ok: deterministic gate
  - cr_onehot_alias = cp_mcen_onehot x cp_alias (u, ok): bins cy_cycle{cy cycle}, cy_cycleh{cy cycleh}, ir_instret{ir instret}, ir_instreth{ir instreth}, hpm3_hpm3{hpm3 hpm3}, hpm4_hpm4{hpm4 hpm4}, hpm5_hpm5{hpm5 hpm5}, hpm6_hpm6{hpm6 hpm6}, hpm7_hpm7{hpm7 hpm7}, hpm8_hpm8{hpm8 hpm8}, hpm9_hpm9{hpm9 hpm9}, hpm10_hpm10{hpm10 hpm10}, hpm11_hpm11{hpm11 hpm11}, hpm12_hpm12{hpm12 hpm12}, hpm12_hpm12h{hpm12 hpm12h}
  - cr_wr_alias = cp_form(wr) x cp_priv x cp_trap: bins wr_m_trap{wr m trap}, wr_u_trap{wr u trap}; ignore wr x ok: illegal_csr_write is unconditional in the read-only range
- Adopted (riscv-dv): none
- TP items: TP-CSR-011, TP-CSR-015, TP-CSR-051, TP-CSR-053, TP-CSR-054, TP-CSR-055, TP-CSR-056, TP-CSR-057, TP-CSR-111, TP-CSR-117, TP-PRV-033

### CG-CSR-006: gen_cg_csr_machine_info
- Features: F-CSR-011, F-CSR-013, F-CSR-019, F-CSR-020
- Sample: rvfi_valid with a CSR instruction to 0xF11..0xF15 (trapped or not); condition: rvfi_valid && is_csr_insn && addr inside {0xF11..0xF15}; anti-vacuity: only machine-information accesses sample; a hit proves that CSR was read or write-attempted in that mode with the recorded hart_id_i class.
- Coverpoints:
  - cp_csr = addr: bins mvendorid{0xF11}, marchid{0xF12}, mimpid{0xF13}, mhartid{0xF14}, mconfigptr{0xF15}
  - cp_form = op form after demotion: bins rd_only{csrrs/csrrc x0, csrrsi/csrrci 0}, wr{any write op}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_hartid_val = hart_id_i value class (mhartid reads only): bins zero{0}, all1{0xFFFF_FFFF}, walking1{single bit set}, rand{other}
- Crosses:
  - cr_csr_form_trap = cp_csr x cp_form x cp_trap (m): bins mvendorid_rd_ok{mvendorid rd_only ok}, mvendorid_wr_trap{mvendorid wr trap}, marchid_rd_ok{marchid rd_only ok}, marchid_wr_trap{marchid wr trap}, mimpid_rd_ok{mimpid rd_only ok}, mimpid_wr_trap{mimpid wr trap}, mhartid_rd_ok{mhartid rd_only ok}, mhartid_wr_trap{mhartid wr trap}, mconfigptr_rd_ok{mconfigptr rd_only ok}, mconfigptr_wr_trap{mconfigptr wr trap}; ignore rd_only x trap in M and wr x ok: the read-only range rule is unconditional
  - cr_csr_u = cp_csr x cp_priv(u) x cp_trap(trap): bins mvendorid_u{mvendorid u trap}, marchid_u{marchid u trap}, mimpid_u{mimpid u trap}, mhartid_u{mhartid u trap}, mconfigptr_u{mconfigptr u trap}
  - cr_hartid_val_rd = cp_hartid_val x cp_form(rd_only) x cp_trap(ok): bins zero{zero}, all1{all1}, walking1{walking1}, rand{rand}
- Adopted (riscv-dv): none
- TP items: TP-CSR-011, TP-CSR-013, TP-CSR-019, TP-CSR-020, TP-CSR-110, TP-CSR-111

### CG-CSR-007: gen_cg_csr_debug_csr
- Features: F-CSR-017, F-CSR-018, F-CSR-074, F-CSR-075, F-CSR-076, F-CSR-077, F-CSR-078, F-CSR-079
- Sample: rvfi_valid with a CSR instruction to 0x7B0..0x7BF (trapped or not) plus, for write pairs in debug mode, the gen_chk_csr_readback pair closure; condition: rvfi_valid && is_csr_insn && addr[11:4] == 0x7B; anti-vacuity: only debug-CSR accesses sample; a hit proves an access of that form happened with the recorded debug-mode state, so the trap/no-trap and WARL result was checked.
- Coverpoints:
  - cp_csr = addr: bins dcsr{0x7B0}, dpc{0x7B1}, dscratch0{0x7B2}, dscratch1{0x7B3}, hole{0x7B4..0x7BF}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_form = op form after demotion: bins rd_only{demoted reads}, wr{write ops}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_op = rvfi_insn[14:12]: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only}, illegal_only{RO bits only}
  - cp_dcsr_prv_w = written dcsr[1:0] (dcsr writes): bins u{00}, s{01}, h{10}, m{11}
  - cp_dcsr_ebreakm_w = written dcsr[15]: bins b0{0}, b1{1}
  - cp_dcsr_ebreaku_w = written dcsr[12]: bins b0{0}, b1{1}
  - cp_dcsr_ebreaks_w = written dcsr[13]: bins b0{0}, b1{1}
  - cp_dcsr_step_w = written dcsr[2]: bins b0{0}, b1{1}
  - cp_dcsr_ro_w = any RO dcsr bit written 1 (xdebugver, cause, stepie, stopcount, stoptime, mprven, nmip, zero fields): bins none{0}, some{1}
  - cp_dpc_lo_w = written dpc[0]: bins b0{0}, b1{1}
- Crosses:
  - cr_csr_dbg_trap = cp_csr x cp_dbg x cp_trap: bins dcsr_nondbg_trap{dcsr nondbg trap}, dpc_nondbg_trap{dpc nondbg trap}, dscratch0_nondbg_trap{dscratch0 nondbg trap}, dscratch1_nondbg_trap{dscratch1 nondbg trap}, dcsr_dbg_ok{dcsr dbg ok}, dpc_dbg_ok{dpc dbg ok}, dscratch0_dbg_ok{dscratch0 dbg ok}, dscratch1_dbg_ok{dscratch1 dbg ok}, hole_dbg_trap{hole dbg trap}, hole_nondbg_trap{hole nondbg trap}; ignore {dcsr, dpc, dscratch0, dscratch1} x nondbg x ok: illegal_csr_dbg unconditional; ignore {dcsr, dpc, dscratch0, dscratch1} x dbg x trap: legal in debug mode; ignore hole x ok: unimplemented
  - cr_csr_form_nondbg = cp_csr x cp_form (nondbg, trap): bins dcsr_rd{dcsr rd_only}, dcsr_wr{dcsr wr}, dpc_rd{dpc rd_only}, dpc_wr{dpc wr}, dscratch0_rd{dscratch0 rd_only}, dscratch0_wr{dscratch0 wr}, dscratch1_rd{dscratch1 rd_only}, dscratch1_wr{dscratch1 wr}
  - cr_csr_op_dbg = cp_csr x cp_op (dbg, ok): bins dcsr_csrrw{dcsr csrrw}, dcsr_csrrs{dcsr csrrs}, dcsr_csrrc{dcsr csrrc}, dcsr_csrrwi{dcsr csrrwi}, dcsr_csrrsi{dcsr csrrsi}, dcsr_csrrci{dcsr csrrci}, dpc_csrrw{dpc csrrw}, dpc_csrrs{dpc csrrs}, dpc_csrrc{dpc csrrc}, dpc_csrrwi{dpc csrrwi}, dpc_csrrsi{dpc csrrsi}, dpc_csrrci{dpc csrrci}, dscratch0_csrrw{dscratch0 csrrw}, dscratch0_csrrs{dscratch0 csrrs}, dscratch0_csrrc{dscratch0 csrrc}, dscratch0_csrrwi{dscratch0 csrrwi}, dscratch0_csrrsi{dscratch0 csrrsi}, dscratch0_csrrci{dscratch0 csrrci}, dscratch1_csrrw{dscratch1 csrrw}, dscratch1_csrrs{dscratch1 csrrs}, dscratch1_csrrc{dscratch1 csrrc}, dscratch1_csrrwi{dscratch1 csrrwi}, dscratch1_csrrsi{dscratch1 csrrsi}, dscratch1_csrrci{dscratch1 csrrci}
  - cr_csr_wpat_dbg = cp_csr x cp_wpat (dbg, ok): bins dcsr_rand{dcsr rand}, dcsr_all1{dcsr all1}, dcsr_all0{dcsr all0}, dcsr_legal{dcsr legal_only}, dcsr_illegal{dcsr illegal_only}, dpc_rand{dpc rand}, dpc_all1{dpc all1}, dpc_all0{dpc all0}, dpc_legal{dpc legal_only}, dpc_illegal{dpc illegal_only bit0}, dscratch0_rand{dscratch0 rand}, dscratch0_all1{dscratch0 all1}, dscratch0_all0{dscratch0 all0}, dscratch1_rand{dscratch1 rand}, dscratch1_all1{dscratch1 all1}, dscratch1_all0{dscratch1 all0}; ignore dscratch x {legal_only, illegal_only}: all bits writable
  - cr_prv_w_op = cp_dcsr_prv_w x cp_op: bins prv_s_csrrw{s csrrw}, prv_h_csrrw{h csrrw}, prv_u_csrrw{u csrrw}, prv_m_csrrw{m csrrw}, prv_s_csrrs{s csrrs}, prv_h_csrrsi{h csrrsi}, prv_u_csrrc{u csrrc}
  - cr_dcsr_bits = cp_dcsr_ebreakm_w x cp_dcsr_ebreaku_w x cp_dcsr_ebreaks_w x cp_dcsr_step_w: bins all0{0 0 0 0}, all1{1 1 1 1}, ebreakm_only{1 0 0 0}, ebreaku_only{0 1 0 0}, ebreaks_only{0 0 1 0}, step_only{0 0 0 1}, ebreakm_u{1 1 0 0}, step_ebreakm{1 0 0 1}
  - cr_dcsr_ro_w = cp_dcsr_ro_w x cp_op: bins some_csrrw{some csrrw}, some_csrrs{some csrrs}, none_csrrw{none csrrw}
  - cr_dpc_lo = cp_dpc_lo_w x cp_op: bins b1_csrrw{b1 csrrw}, b1_csrrsi{b1 csrrsi}, b0_csrrw{b0 csrrw}
  - cr_u_nondbg = cp_priv(u) x cp_csr x cp_trap(trap): bins u_dcsr{u dcsr trap}, u_dpc{u dpc trap}, u_dscratch0{u dscratch0 trap}, u_dscratch1{u dscratch1 trap}
- Adopted (riscv-dv): none
- TP items: TP-CSR-017, TP-CSR-018, TP-CSR-074, TP-CSR-075, TP-CSR-076, TP-CSR-077, TP-CSR-078, TP-CSR-079, TP-CSR-108, TP-CSR-110, TP-CSR-118

### CG-CSR-008: gen_cg_csr_trigger_csr
- Features: F-CSR-080, F-CSR-081, F-CSR-082, F-CSR-083, F-CSR-084
- Sample: rvfi_valid with a CSR instruction to 0x7A0..0x7A3, 0x7A8, 0x7AA, 0x5A8 (trapped or not); condition: rvfi_valid && is_csr_insn && addr in the trigger set; anti-vacuity: only trigger-CSR accesses sample; a hit proves an access of that form happened in the recorded debug/privilege state so the write-effective / write-ignored prediction was compared on the next read.
- Coverpoints:
  - cp_csr = addr: bins tselect{0x7A0}, tdata1{0x7A1}, tdata2{0x7A2}, tdata3{0x7A3}, mcontext{0x7A8}, mscontext{0x7AA}, scontext{0x5A8}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_form = op form after demotion: bins rd_only{demoted reads}, wr{write ops}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_op = rvfi_insn[14:12]: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only}, illegal_only{RO bits only}
  - cp_tsel_w = written tselect value class: bins zero{0}, ge_num{>= DbgHwBreakNum}
  - cp_tdata1_exec_w = written tdata1[2]: bins b0{0}, b1{1}
  - cp_tdata1_other_w = any tdata1 bit other than 2 written 1: bins none{0}, some{1}
- Crosses:
  - cr_csr_dbg_form = cp_csr x cp_dbg x cp_form (m, ok): bins tselect_nondbg_wr{tselect nondbg wr}, tselect_dbg_wr{tselect dbg wr}, tdata1_nondbg_wr{tdata1 nondbg wr}, tdata1_dbg_wr{tdata1 dbg wr}, tdata2_nondbg_wr{tdata2 nondbg wr}, tdata2_dbg_wr{tdata2 dbg wr}, tdata3_nondbg_wr{tdata3 nondbg wr}, tdata3_dbg_wr{tdata3 dbg wr}, mcontext_nondbg_wr{mcontext nondbg wr}, mscontext_nondbg_wr{mscontext nondbg wr}, scontext_nondbg_wr{scontext nondbg wr}, tselect_nondbg_rd{tselect nondbg rd_only}, tdata1_nondbg_rd{tdata1 nondbg rd_only}, tdata2_nondbg_rd{tdata2 nondbg rd_only}, tdata3_nondbg_rd{tdata3 nondbg rd_only}, mcontext_nondbg_rd{mcontext nondbg rd_only}, mscontext_nondbg_rd{mscontext nondbg rd_only}, scontext_nondbg_rd{scontext nondbg rd_only}, tdata1_dbg_rd{tdata1 dbg rd_only}, tdata2_dbg_rd{tdata2 dbg rd_only}, tselect_dbg_rd{tselect dbg rd_only}
  - cr_csr_u = cp_csr x cp_priv(u) x cp_trap(trap): bins tselect_u{tselect u trap}, tdata1_u{tdata1 u trap}, tdata2_u{tdata2 u trap}, tdata3_u{tdata3 u trap}, mcontext_u{mcontext u trap}, mscontext_u{mscontext u trap}, scontext_u{scontext u trap}
  - cr_csr_op_dbg = cp_csr x cp_op (dbg, wr): bins tselect_csrrw{tselect csrrw}, tselect_csrrs{tselect csrrs}, tselect_csrrc{tselect csrrc}, tselect_csrrwi{tselect csrrwi}, tselect_csrrsi{tselect csrrsi}, tselect_csrrci{tselect csrrci}, tdata1_csrrw{tdata1 csrrw}, tdata1_csrrs{tdata1 csrrs}, tdata1_csrrc{tdata1 csrrc}, tdata1_csrrwi{tdata1 csrrwi}, tdata1_csrrsi{tdata1 csrrsi}, tdata1_csrrci{tdata1 csrrci}, tdata2_csrrw{tdata2 csrrw}, tdata2_csrrs{tdata2 csrrs}, tdata2_csrrc{tdata2 csrrc}, tdata2_csrrwi{tdata2 csrrwi}, tdata2_csrrsi{tdata2 csrrsi}, tdata2_csrrci{tdata2 csrrci}
  - cr_csr_wpat = cp_csr x cp_wpat (wr): bins tselect_rand{tselect rand}, tselect_all1{tselect all1}, tdata1_rand{tdata1 rand}, tdata1_all1{tdata1 all1}, tdata1_all0{tdata1 all0}, tdata1_legal{tdata1 legal_only}, tdata1_illegal{tdata1 illegal_only}, tdata2_rand{tdata2 rand}, tdata2_all1{tdata2 all1}, tdata2_all0{tdata2 all0}, tdata3_all1{tdata3 all1}, mcontext_all1{mcontext all1}, mscontext_all1{mscontext all1}, scontext_all1{scontext all1}
  - cr_tdata1_w = cp_tdata1_exec_w x cp_tdata1_other_w x cp_dbg: bins dbg_e1_none{dbg 1 none}, dbg_e1_some{dbg 1 some}, dbg_e0_some{dbg 0 some}, dbg_e0_none{dbg 0 none}, nondbg_e1_none{nondbg 1 none}, nondbg_e1_some{nondbg 1 some}
  - cr_tsel_w_dbg = cp_tsel_w x cp_dbg: bins zero_dbg{zero dbg}, ge_dbg{ge_num dbg}, zero_nondbg{zero nondbg}, ge_nondbg{ge_num nondbg}
- Adopted (riscv-dv): none
- TP items: TP-CSR-080, TP-CSR-081, TP-CSR-082, TP-CSR-083, TP-CSR-084, TP-CSR-108, TP-CSR-110, TP-CSR-118

### CG-CSR-009: gen_cg_csr_cpuctrlsts
- Features: F-CSR-085, F-CSR-086, F-CSR-087, F-CSR-088, F-CSR-089, F-CSR-090, F-CSR-091
- Sample: (a) rvfi_valid with a CSR instruction to 0x7C0, (b) a synchronous trap retirement (rvfi_trap with a non-interrupt cause) outside debug mode, (c) an mret retirement, (d) a double_fault_seen_o pulse, (e) an interrupt/NMI/debug entry observed on RVFI; condition: any of a..e; anti-vacuity: each event class is distinct and the sync_exc_seen / double_fault_seen model state is sampled with it, so a hit proves the model saw that transition and gen_chk_double_fault / gen_chk_csr_readback compared the resulting bits.
- Coverpoints:
  - cp_event = event class: bins sw_rd{CSR read of 0x7C0}, sw_wr{CSR write op to 0x7C0}, hw_sync_set{sync exception taken outside debug}, hw_mret_clr{mret retired}, hw_dbl_pulse{double_fault_seen_o pulse}, hw_irq{interrupt or NMI entry}, hw_dbg{debug entry or exception in debug mode}
  - cp_op = rvfi_insn[14:12] (sw events): bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class (sw_wr): bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{bits 7:0 only}, illegal_only{bits 31:8 only}
  - cp_icache_w = written bit 0: bins b0{0}, b1{1}
  - cp_dit_w = written bit 1: bins b0{0}, b1{1}
  - cp_dummy_en_w = written bit 2: bins b0{0}, b1{1}
  - cp_dummy_mask_w = written bits 5:3: bins m0{000}, m1{001}, m2{010}, m3{011}, m4{100}, m5{101}, m6{110}, m7{111}
  - cp_sync_w = written bit 6: bins b0{0}, b1{1}
  - cp_dbl_w = written bit 7: bins b0{0}, b1{1}
  - cp_key_w = written bit 8: bins b0{0}, b1{1}
  - cp_hi_w = written bits 31:9: bins zero{0}, nonzero{!=0}
  - cp_key_pin = ic_scr_key_valid_i one cycle before the read (sw_rd): bins lo{0}, hi{1}
  - cp_sync_state = sync_exc_seen model value before the event: bins s0{0}, s1{1}
  - cp_dbl_state = double_fault_seen model value before the event: bins d0{0}, d1{1}
  - cp_trap_kind = kind of hw event: bins sync_exc{exception outside debug}, irq{interrupt}, nmi{NMI}, dbg_entry{debug entry}, dbgmode_exc{exception while in debug mode}
  - cp_priv = rvfi_mode (sw events): bins m{3}, u{0}
  - cp_trap = rvfi_trap (sw events): bins ok{0}, trap{1}
- Crosses:
  - cr_dbl_detect = cp_event x cp_sync_state x cp_trap_kind: bins sync_s0_set{hw_sync_set s0 sync_exc}, sync_s1_pulse{hw_dbl_pulse s1 sync_exc}, s1_irq_nopulse{hw_irq s1 irq}, s1_nmi_nopulse{hw_irq s1 nmi}, s1_dbg_nopulse{hw_dbg s1 dbg_entry}, s1_dbgmode_exc_nopulse{hw_dbg s1 dbgmode_exc}, mret_clr_s1{hw_mret_clr s1}, mret_clr_s0{hw_mret_clr s0}
  - cr_sw_sync = cp_event(sw_wr) x cp_sync_w x cp_sync_state: bins set_s0{b1 s0}, clr_s1{b0 s1}, keep_s1{b1 s1}, keep_s0{b0 s0}
  - cr_sw_dbl = cp_event(sw_wr) x cp_dbl_w x cp_dbl_state: bins set_d0{b1 d0}, clr_d1{b0 d1}, keep_d1{b1 d1}, keep_d0{b0 d0}
  - cr_key_rd = cp_key_pin x cp_event(sw_rd): bins lo_rd{lo}, hi_rd{hi}
  - cr_key_w = cp_key_w x cp_key_pin (sw_wr then read): bins w1_lo{b1 lo}, w1_hi{b1 hi}, w0_hi{b0 hi}
  - cr_mask_en = cp_dummy_mask_w x cp_dummy_en_w(b1): bins m0_en{m0}, m1_en{m1}, m2_en{m2}, m3_en{m3}, m4_en{m4}, m5_en{m5}, m6_en{m6}, m7_en{m7}
  - cr_ic_dit = cp_icache_w x cp_dit_w: bins ic0_dit0{0 0}, ic1_dit0{1 0}, ic0_dit1{0 1}, ic1_dit1{1 1}
  - cr_wpat_op = cp_wpat x cp_op: bins rand_csrrw{rand csrrw}, rand_csrrs{rand csrrs}, rand_csrrc{rand csrrc}, all1_csrrw{all1 csrrw}, all0_csrrw{all0 csrrw}, legal_csrrsi{legal_only csrrsi}, legal_csrrci{legal_only csrrci}, illegal_csrrw{illegal_only csrrw}, all1_csrrs{all1 csrrs}
  - cr_hi_w = cp_hi_w x cp_op: bins nz_csrrw{nonzero csrrw}, nz_csrrs{nonzero csrrs}
  - cr_u_trap = cp_priv(u) x cp_event x cp_trap(trap): bins u_rd_trap{u sw_rd trap}, u_wr_trap{u sw_wr trap}
- Adopted (riscv-dv): none
- TP items: TP-CSR-085, TP-CSR-086, TP-CSR-087, TP-CSR-088, TP-CSR-089, TP-CSR-090, TP-CSR-091, TP-CSR-094, TP-CSR-109, TP-CSR-110

### CG-CSR-010: gen_cg_csr_secureseed
- Features: F-CSR-092, F-CSR-093
- Sample: rvfi_valid with a CSR instruction to 0x7C1 (trapped or not); condition: rvfi_valid && is_csr_insn && addr == 0x7C1; anti-vacuity: only secureseed accesses sample; the pulse coverpoint comes from the probe candidate below, so a hit on a pulse bin proves the reseed fired for exactly that op form.
- Coverpoints:
  - cp_op = rvfi_insn[14:12]: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_rs1 = rvfi_insn[19:15]: bins zero{0}, nonzero{1..31}
  - cp_form = op form after demotion: bins rd_only{demoted reads}, wr{write ops}
  - cp_pulse = dummy_instr_seed_en_o observed in the write cycle (probe): bins none{0}, pulse{1}
  - cp_seed_val = csr_wdata_int class (wr): bins zero{0}, all1{0xFFFF_FFFF}, rand{other}
  - cp_dummy_en = cpuctrlsts.dummy_instr_en at the write: bins off{0}, on{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
- Crosses:
  - cr_op_form_pulse = cp_op x cp_rs1 x cp_pulse: bins csrrw_nz_pulse{csrrw nonzero pulse}, csrrw_x0_pulse{csrrw zero pulse}, csrrwi_0_pulse{csrrwi zero pulse}, csrrwi_nz_pulse{csrrwi nonzero pulse}, csrrs_nz_pulse{csrrs nonzero pulse}, csrrc_nz_pulse{csrrc nonzero pulse}, csrrsi_nz_pulse{csrrsi nonzero pulse}, csrrci_nz_pulse{csrrci nonzero pulse}, csrrs_x0_none{csrrs zero none}, csrrc_x0_none{csrrc zero none}, csrrsi_0_none{csrrsi zero none}, csrrci_0_none{csrrci zero none}; ignore demoted reads x pulse: csr_we_int is 0 for READ; ignore write forms x none in M-mode: the pulse is unconditional on csr_we_int
  - cr_seed_en = cp_seed_val x cp_dummy_en (wr): bins zero_on{zero on}, all1_on{all1 on}, rand_on{rand on}, rand_off{rand off}, zero_off{zero off}
  - cr_rd_value = cp_form(rd_only) x cp_trap(ok): bins rd_ok{read returns 0}
  - cr_u = cp_priv(u) x cp_trap(trap): bins u_trap{u trap}
- Adopted (riscv-dv): none
- TP items: TP-CSR-002, TP-CSR-092, TP-CSR-093, TP-CSR-109, TP-CSR-110

### CG-CSR-011: gen_cg_csr_pmp_warl
- Features: F-CSR-094, F-CSR-095, F-CSR-096, F-CSR-098
- Sample: gen_chk_csr_readback pair completion for pmpcfg0..3, pmpaddr0..15, mseccfg, mseccfgh, sampled once per 8-bit pmpcfg entry for the entry coverpoints; condition: pair closed; anti-vacuity: as CG-CSR-002; the entry class is computed from the pre-write PMP state so a hit proves the WARL rule of that class was exercised and compared (PMP semantics themselves belong to the PMP area).
- Coverpoints:
  - cp_csr = pair address: bins cfg0{0x3A0}, cfg1{0x3A1}, cfg2{0x3A2}, cfg3{0x3A3}, addr0{0x3B0}, addr1{0x3B1}, addr2{0x3B2}, addr3{0x3B3}, addr4{0x3B4}, addr5{0x3B5}, addr6{0x3B6}, addr7{0x3B7}, addr8{0x3B8}, addr9{0x3B9}, addr10{0x3BA}, addr11{0x3BB}, addr12{0x3BC}, addr13{0x3BD}, addr14{0x3BE}, addr15{0x3BF}, mseccfg{0x747}, mseccfgh{0x757}
  - cp_fam = family of cp_csr: bins cfg{pmpcfg0..3}, addr{pmpaddr0..15}, mseccfg{0x747}, mseccfgh{0x757}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only}, illegal_only{RO or legalised bits only}
  - cp_entry_idx = pmpcfg entry within the register: bins e0{bits 7:0}, e1{15:8}, e2{23:16}, e3{31:24}
  - cp_entry_class = WARL class of the written entry: bins locked_kept{L=1 and RLB=0 before write}, mml_suppress{MML=1 RLB=0 and new entry is locked M-executable}, w_no_r{W=1 R=0 with MML=0}, resv_bits{bits 6:5 written 1}, mode_off{A=00}, mode_tor{A=01}, mode_na4{A=10}, mode_napot{A=11}, plain{no rule engaged}
  - cp_addr_class = pmpaddr write class: bins writable{no lock}, locked_self{cfg[i].L=1 RLB=0}, locked_tor_next{cfg[i+1] locked TOR}, rlb_unlock{RLB=1 with L=1}
  - cp_mseccfg_w = mseccfg write class: bins mml_set{MML 0->1}, mml_clr_attempt{MML 1 written 0}, mmwp_set{MMWP 0->1}, mmwp_clr_attempt{MMWP 1 written 0}, rlb_set_nolock{RLB 1 no locked region}, rlb_set_locked{RLB 1 with locked region}, rlb_clr_with_rlb1{RLB 1->0}, hi_bits{bits 31:3 written 1}
- Crosses:
  - cr_fam_op = cp_fam x cp_op: bins cfg_csrrw{cfg csrrw}, cfg_csrrs{cfg csrrs}, cfg_csrrc{cfg csrrc}, cfg_csrrwi{cfg csrrwi}, cfg_csrrsi{cfg csrrsi}, cfg_csrrci{cfg csrrci}, addr_csrrw{addr csrrw}, addr_csrrs{addr csrrs}, addr_csrrc{addr csrrc}, addr_csrrwi{addr csrrwi}, addr_csrrsi{addr csrrsi}, addr_csrrci{addr csrrci}, mseccfg_csrrw{mseccfg csrrw}, mseccfg_csrrs{mseccfg csrrs}, mseccfg_csrrc{mseccfg csrrc}, mseccfg_csrrwi{mseccfg csrrwi}, mseccfg_csrrsi{mseccfg csrrsi}, mseccfg_csrrci{mseccfg csrrci}, mseccfgh_csrrw{mseccfgh csrrw}, mseccfgh_csrrs{mseccfgh csrrs}, mseccfgh_csrrc{mseccfgh csrrc}, mseccfgh_csrrwi{mseccfgh csrrwi}, mseccfgh_csrrsi{mseccfgh csrrsi}, mseccfgh_csrrci{mseccfgh csrrci}
  - cr_fam_wpat = cp_fam x cp_wpat: bins cfg_rand{cfg rand}, cfg_all1{cfg all1}, cfg_all0{cfg all0}, cfg_legal{cfg legal_only}, cfg_illegal{cfg illegal_only}, addr_rand{addr rand}, addr_all1{addr all1}, addr_all0{addr all0}, mseccfg_rand{mseccfg rand}, mseccfg_all1{mseccfg all1}, mseccfg_all0{mseccfg all0}, mseccfg_legal{mseccfg legal_only}, mseccfg_illegal{mseccfg illegal_only}, mseccfgh_rand{mseccfgh rand}, mseccfgh_all1{mseccfgh all1}; ignore addr x {legal_only, illegal_only}: all 32 bits writable; ignore mseccfgh x {legal_only, illegal_only}: no writable bit
  - cr_cfg_entry = cp_entry_idx x cp_entry_class: bins e0_locked{e0 locked_kept}, e1_locked{e1 locked_kept}, e2_locked{e2 locked_kept}, e3_locked{e3 locked_kept}, e0_plain{e0 plain}, e1_plain{e1 plain}, e2_plain{e2 plain}, e3_plain{e3 plain}, e0_w_no_r{e0 w_no_r}, e3_w_no_r{e3 w_no_r}, e1_mml_suppress{e1 mml_suppress}, e2_resv{e2 resv_bits}
  - cr_addr_last = cp_csr(addr15) x cp_addr_class: bins addr15_writable{addr15 writable}, addr15_locked_self{addr15 locked_self}; ignore addr15_locked_tor_next: no region 16 exists (PMPNumRegions)
  - cr_addr_lock = cp_addr_class x cp_op: bins locked_self_csrrw{locked_self csrrw}, locked_tor_next_csrrw{locked_tor_next csrrw}, rlb_unlock_csrrw{rlb_unlock csrrw}, writable_csrrw{writable csrrw}, writable_csrrs{writable csrrs}, writable_csrrc{writable csrrc}
- Adopted (riscv-dv): none
- TP items: TP-CSR-095, TP-CSR-096, TP-CSR-097, TP-CSR-099, TP-CSR-101, TP-CSR-109

### CG-CSR-012: gen_cg_csr_write_effect
- Features: F-CSR-006, F-CSR-007, F-CSR-026, F-CSR-031, F-CSR-033, F-CSR-100
- Sample: every CSR write op (WRITE/SET/CLEAR not demoted) retired without trap; the TB records the next RVFI retirement's class and the cycle gap between the two retirements; condition: rvfi_valid && is_csr_write && !rvfi_trap; anti-vacuity: demoted reads and trapped writes never sample; a hit proves a real write of that family was followed by the recorded next instruction with the recorded bubble, which gen_chk_csr_flush checks against the mscratch/mepc no-flush rule.
- Coverpoints:
  - cp_fam = written CSR family: bins mscratch{0x340}, mepc{0x341}, other_flush{any other writable or write-ignored CSR}
  - cp_next = class of the next retired instruction: bins csr_rd_same{csr read same address}, csr_rd_other{csr read other address}, csr_wr{csr write}, alu{integer op}, load_store{load or store}, branch_jump{branch or jump}, wfi{wfi}, mret{mret}, ecall_ebreak{ecall or ebreak}, irq_taken{interrupt handler entry rvfi_intr}, compressed{16-bit instruction}, dbg_entry{debug entry}
  - cp_gap = cycles between the two retirements: bins g1{1 no bubble}, g2_3{2..3 flush bubble}, g_more{>3}
  - cp_enable = write enables an already pending interrupt (mstatus.MIE or mie bit) : bins none{no}, enables_pending{yes}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
- Crosses:
  - cr_fam_next = cp_fam x cp_next: bins mscratch_csr_rd_same{mscratch csr_rd_same}, mepc_csr_rd_same{mepc csr_rd_same}, other_csr_rd_same{other_flush csr_rd_same}, other_csr_rd_other{other_flush csr_rd_other}, other_csr_wr{other_flush csr_wr}, other_alu{other_flush alu}, other_load_store{other_flush load_store}, other_branch_jump{other_flush branch_jump}, other_irq_taken{other_flush irq_taken}, other_wfi{other_flush wfi}, other_mret{other_flush mret}, other_compressed{other_flush compressed}, other_ecall{other_flush ecall_ebreak}, other_dbg_entry{other_flush dbg_entry}, mscratch_alu{mscratch alu}, mscratch_load_store{mscratch load_store}, mepc_mret{mepc mret}, mepc_alu{mepc alu}
  - cr_fam_gap = cp_fam x cp_gap: bins mscratch_g1{mscratch g1}, mepc_g1{mepc g1}, other_g2_3{other_flush g2_3}, other_g_more{other_flush g_more}, mscratch_g_more{mscratch g_more stalled by memory}; ignore other_g1: a flushing write always costs at least one FLUSH cycle
  - cr_enable_next = cp_enable x cp_next: bins enables_irq_taken{enables_pending irq_taken}, none_alu{none alu}, none_irq_taken{none irq_taken}
  - cr_fam_op = cp_fam x cp_op: bins mscratch_csrrw{mscratch csrrw}, mscratch_csrrs{mscratch csrrs}, mscratch_csrrc{mscratch csrrc}, mepc_csrrw{mepc csrrw}, mepc_csrrsi{mepc csrrsi}, other_csrrw{other_flush csrrw}, other_csrrs{other_flush csrrs}, other_csrrc{other_flush csrrc}, other_csrrwi{other_flush csrrwi}, other_csrrsi{other_flush csrrsi}, other_csrrci{other_flush csrrci}
- Adopted (riscv-dv): none
- TP items: TP-CSR-003, TP-CSR-006, TP-CSR-007, TP-CSR-026, TP-CSR-031, TP-CSR-033, TP-CSR-101, TP-CSR-102, TP-CSR-115, TP-CSR-116, TP-CSR-119

### CG-CSR-013: gen_cg_csr_counter_race
- Features: F-CSR-034, F-CSR-060, F-CSR-063, F-CSR-064, F-CSR-065, F-CSR-067, F-CSR-068, F-CSR-070, F-CSR-072, F-CSR-073
- Sample: rvfi_valid with a CSR instruction to mcycle(h), minstret(h), mhpmcounter3..12(h) or mip; condition: rvfi_valid && is_csr_insn && addr in that set && !rvfi_trap; anti-vacuity: the race coverpoints are derived from rvfi_ext_mcycle / rvfi_ext_mhpmcounters of the writer and of the neighbouring retirements and from the irq pins, so a hit proves the hardware update and the software access were adjacent in the way the bin names, and gen_chk_counters compared the result.
- Coverpoints:
  - cp_csr = addr class: bins mcycle{0xB00}, mcycleh{0xB80}, minstret{0xB02}, minstreth{0xB82}, hpm_lo{0xB03..0xB0C}, hpm10{0xB0A}, hpm_hi{0xB83..0xB8C}, mip{0x344}
  - cp_kind = op after demotion: bins rd{READ}, wr{WRITE}, set{SET}, clr{CLEAR}
  - cp_inhibit = the counter's mcountinhibit bit: bins on{1}, off{0}
  - cp_coincide = hardware increment event in the write cycle (mcycle: always; minstret: a countable instruction retiring in WB; hpm: event in that cycle): bins none{0}, coincide{1}
  - cp_near_wrap = low half within 16 of 0xFFFF_FFFF at the access: bins no{0}, yes{1}
  - cp_carry_win = mcycleh written in the cycle the low half carries: bins no{0}, yes{1}
  - cp_wb_state = instruction in WB in the read cycle (minstret / hpm10 reads): bins idle{none}, retiring{countable retirement}, retiring_err{LSU error retirement}
  - cp_mip_toggle = irq pin change relative to the mip read cycle: bins stable{no change within +-2 cycles}, toggle_before{change 1..2 cycles before}, toggle_at{change in the read cycle}
  - cp_prepost = rvfi_ext_pre_mip vs rvfi_ext_post_mip: bins equal{same}, differ{different}
- Crosses:
  - cr_cyc_wr = cp_csr x cp_kind x cp_inhibit: bins mcycle_wr_off{mcycle wr off}, mcycle_set_off{mcycle set off}, mcycle_clr_off{mcycle clr off}, mcycle_wr_on{mcycle wr on}, mcycleh_wr_off{mcycleh wr off}, mcycleh_set_off{mcycleh set off}, mcycleh_clr_off{mcycleh clr off}, mcycleh_wr_on{mcycleh wr on}, mcycle_rd_on{mcycle rd on}, mcycle_rd_off{mcycle rd off}
  - cr_carry = cp_csr(mcycleh) x cp_carry_win: bins carry_yes{mcycleh yes}, carry_no{mcycleh no}
  - cr_near_wrap = cp_csr x cp_near_wrap(yes) x cp_kind: bins mcycle_wrap_rd{mcycle yes rd}, mcycleh_wrap_wr{mcycleh yes wr}, minstret_wrap_rd{minstret yes rd}, hpm_wrap_rd{hpm_lo yes rd}, hpm_hi_wrap_wr{hpm_hi yes wr}
  - cr_minstret_rd_wb = cp_csr x cp_wb_state x cp_inhibit (rd): bins minstret_idle{minstret idle off}, minstret_retiring{minstret retiring off}, minstret_retiring_err{minstret retiring_err off}, minstret_inh_retiring{minstret retiring on}, hpm10_idle{hpm10 idle off}, hpm10_retiring{hpm10 retiring off}, hpm_lo_retiring{hpm_lo retiring off}
  - cr_minstret_wr = cp_csr x cp_kind x cp_coincide: bins minstret_wr_coincide{minstret wr coincide}, minstret_set_coincide{minstret set coincide}, minstret_clr_coincide{minstret clr coincide}, minstreth_wr_coincide{minstreth wr coincide}, minstret_wr_none{minstret wr none}, hpm_lo_wr_coincide{hpm_lo wr coincide}, hpm_hi_wr_coincide{hpm_hi wr coincide}, hpm_lo_set_coincide{hpm_lo set coincide}
  - cr_mip_rd = cp_csr(mip) x cp_mip_toggle x cp_prepost: bins stable_equal{stable equal}, before_equal{toggle_before equal}, before_differ{toggle_before differ}, at_differ{toggle_at differ}, at_equal{toggle_at equal}
- Adopted (riscv-dv): none
- TP items: TP-CSR-032, TP-CSR-034, TP-CSR-059, TP-CSR-060, TP-CSR-062, TP-CSR-063, TP-CSR-064, TP-CSR-065, TP-CSR-066, TP-CSR-067, TP-CSR-068, TP-CSR-070, TP-CSR-072, TP-CSR-073, TP-CSR-113, TP-CSR-114, TP-CSR-119, TP-CSR-120

### CG-CSR-014: gen_cg_csr_unimpl_addr
- Features: F-CSR-009, F-CSR-010, F-CSR-016, F-CSR-018, F-CSR-055, F-CSR-097
- Sample: rvfi_valid with a CSR instruction whose address is outside the implemented set (CSR-02 list); condition: rvfi_valid && is_csr_insn && !implemented(addr); anti-vacuity: implemented addresses never sample; a hit proves an access to that hole class happened in that mode/form and gen_isa_compare checked the illegal-instruction trap with mtval = encoding.
- Coverpoints:
  - cp_range = hole range: bins r000_0ff{0x000..0x0FF}, r100_1ff{0x100..0x1FF}, r200_2ff{0x200..0x2FF}, r302_303{medeleg mideleg}, r307_309{0x307..0x309}, r30b_30f{0x30B..0x30F}, r311_319{0x311..0x319}, r31b_31f{0x31B..0x31F}, r321_322{0x321 0x322}, r345_39f{0x345..0x39F}, r3a4_3af{0x3A4..0x3AF}, r3c0_5a7{0x3C0..0x5A7}, r5a9_746{0x5A9..0x746}, r748_756{0x748..0x756}, r758_79f{0x758..0x79F}, r7a4_7a7{0x7A4..0x7A7}, r7a9{0x7A9}, r7ab_7af{0x7AB..0x7AF}, r7b4_7bf{0x7B4..0x7BF}, r7c2_7ff{0x7C2..0x7FF}, r800_aff{0x800..0xAFF}, rb01{0xB01}, rb81{0xB81}, rbc0{0xBC0}, rbc3{0xBC3}, rbc5_bff{0xBC5..0xBFF}, rc01{time}, rc81{timeh}, rc20_c7f{0xC20..0xC7F}, rca0_f10{0xCA0..0xF10}, rf16_fff{0xF16..0xFFF}, cheriot{0xBC1 0xBC2 0xBC4}
  - cp_class = coarse class: bins lo{0x000..0x2FF}, mhole{holes in 0x3xx 0x7xx 0xBxx}, mid_unpriv{0x400..0x4FF 0x800..0x8FF}, s_h_hole{0x5xx 0x6xx 0x9xx 0xAxx 0xDxx 0xExx holes}, ro_hole{unimplemented [11:10]=11 incl time}, dbg_hole{0x7B4..0x7BF}, cheriot{0xBC1 0xBC2 0xBC4}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_form = op form after demotion: bins rd{demoted read}, wr{write op}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_trap = rvfi_trap: bins trap{1}; ignore_bins ok{0}: unimplemented addresses always trap; a hit is a gen_isa_compare failure, not a coverage target
- Crosses:
  - cr_class_priv_form = cp_class x cp_priv x cp_form: bins lo_m_rd{lo m rd}, lo_m_wr{lo m wr}, lo_u_rd{lo u rd}, lo_u_wr{lo u wr}, mhole_m_rd{mhole m rd}, mhole_m_wr{mhole m wr}, mhole_u_rd{mhole u rd}, mhole_u_wr{mhole u wr}, mid_m_rd{mid_unpriv m rd}, mid_m_wr{mid_unpriv m wr}, mid_u_rd{mid_unpriv u rd}, mid_u_wr{mid_unpriv u wr}, sh_m_rd{s_h_hole m rd}, sh_m_wr{s_h_hole m wr}, sh_u_rd{s_h_hole u rd}, sh_u_wr{s_h_hole u wr}, ro_m_rd{ro_hole m rd}, ro_m_wr{ro_hole m wr}, ro_u_rd{ro_hole u rd}, ro_u_wr{ro_hole u wr}, dbg_m_rd{dbg_hole m rd}, dbg_m_wr{dbg_hole m wr}, dbg_u_rd{dbg_hole u rd}, dbg_u_wr{dbg_hole u wr}, cher_m_rd{cheriot m rd}, cher_m_wr{cheriot m wr}, cher_u_rd{cheriot u rd}, cher_u_wr{cheriot u wr}
  - cr_dbg_hole = cp_range(r7b4_7bf) x cp_dbg x cp_trap: bins dbghole_dbg_trap{r7b4_7bf dbg trap}, dbghole_nondbg_trap{r7b4_7bf nondbg trap}; ignore x ok: unimplemented in every mode
  - cr_time = cp_range x cp_priv (time timeh): bins time_m{rc01 m}, time_u{rc01 u}, timeh_m{rc81 m}, timeh_u{rc81 u}
- Adopted (riscv-dv): none
- TP items: TP-CSR-009, TP-CSR-010, TP-CSR-014, TP-CSR-016, TP-CSR-018, TP-CSR-055, TP-CSR-098, TP-CSR-112, TP-CSR-116

### CG-CSR-015: gen_cg_csr_write_cancel
- Features: F-CSR-008, F-CSR-101, F-CSR-102, F-CSR-103
- Sample: a CSR write instruction that was in ID when a kill condition occurred, detected from RVFI: (a) the retirement immediately preceding it in program order trapped with an LSU error/PMP fault and the CSR instruction retires only after the handler's mret (re-execution), (b) the CSR instruction itself retires with rvfi_trap (fetch error, PMP fetch fault, illegal CSR), (c) debug entry with dpc == the CSR instruction PC; condition: any of a..c; anti-vacuity: an ordinary CSR write never matches; a hit proves the write was in flight when the kill happened, and gen_chk_csr_readback confirms the CSR kept its old value at the next read.
- Coverpoints:
  - cp_cause = kill cause: bins wb_lsu_err{load/store bus error in WB}, wb_lsu_pmp{load/store PMP fault in WB}, fetch_err{instr_err on the CSR instruction}, fetch_pmp{PMP fetch fault on the CSR instruction}, illegal_csr{illegal CSR access}, dbg_req_before{debug entry with dpc == csr pc}
  - cp_fam = CSR family of the killed write: bins mscratch_mepc{no-flush CSRs}, flush_csr{any other}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_reexec = the CSR instruction later retires successfully: bins yes{1}, no{0}
- Crosses:
  - cr_cause_fam = cp_cause x cp_fam: bins lsu_err_mscratch{wb_lsu_err mscratch_mepc}, lsu_err_flush{wb_lsu_err flush_csr}, lsu_pmp_flush{wb_lsu_pmp flush_csr}, lsu_pmp_mscratch{wb_lsu_pmp mscratch_mepc}, fetch_err_flush{fetch_err flush_csr}, fetch_pmp_flush{fetch_pmp flush_csr}, illegal_flush{illegal_csr flush_csr}, dbg_before_flush{dbg_req_before flush_csr}, dbg_before_mscratch{dbg_req_before mscratch_mepc}
  - cr_cause_reexec = cp_cause x cp_reexec: bins lsu_err_yes{wb_lsu_err yes}, lsu_err_no{wb_lsu_err no}, lsu_pmp_yes{wb_lsu_pmp yes}, fetch_err_yes{fetch_err yes}, fetch_pmp_yes{fetch_pmp yes}, illegal_no{illegal_csr no}, illegal_yes{illegal_csr yes after priv change}, dbg_before_yes{dbg_req_before yes}
  - cr_cause_op = cp_cause x cp_op: bins lsu_err_csrrw{wb_lsu_err csrrw}, lsu_err_csrrs{wb_lsu_err csrrs}, lsu_err_csrrc{wb_lsu_err csrrc}, lsu_err_csrrwi{wb_lsu_err csrrwi}, illegal_csrrw{illegal_csr csrrw}, illegal_csrrs{illegal_csr csrrs}, illegal_csrrci{illegal_csr csrrci}
- Adopted (riscv-dv): none
- TP items: TP-CSR-008, TP-CSR-102, TP-CSR-103, TP-CSR-104

### CG-CSR-016: gen_cg_csr_reset_read
- Features: F-CSR-019, F-CSR-020, F-CSR-021, F-CSR-023, F-CSR-029, F-CSR-032, F-CSR-035, F-CSR-037, F-CSR-038, F-CSR-039, F-CSR-042, F-CSR-047, F-CSR-050, F-CSR-058, F-CSR-061, F-CSR-062, F-CSR-066, F-CSR-069, F-CSR-074, F-CSR-078, F-CSR-079, F-CSR-080, F-CSR-081, F-CSR-082, F-CSR-085, F-CSR-092, F-CSR-094, F-CSR-096, F-CSR-098
- Sample: the first CSR read of an address after reset, before any software write to that address (TB tracks per-address first-write); condition: rvfi_valid && is_csr_insn && !rvfi_trap && first_read_before_write(addr); anti-vacuity: at most one sample per address per reset; a hit proves the reset value of that CSR was read back and compared by gen_chk_csr_readback against the ibex_pkg / parameter reset value.
- Coverpoints:
  - cp_csr = address class: bins mstatus{0x300}, misa{0x301}, mie{0x304}, mtvec{0x305}, mcounteren{0x306}, mstatush{0x310}, menvcfg{0x30A}, menvcfgh{0x31A}, mcountinhibit{0x320}, mhpmevent{0x323..0x32C}, mhpmevent_unimpl{0x32D..0x33F}, mscratch{0x340}, mepc{0x341}, mcause{0x342}, mtval{0x343}, mip{0x344}, pmpcfg{0x3A0..0x3A3}, pmpaddr{0x3B0..0x3BF}, scontext{0x5A8}, mseccfg{0x747}, mseccfgh{0x757}, tselect{0x7A0}, tdata1{0x7A1}, tdata2{0x7A2}, tdata3{0x7A3}, mcontext{0x7A8}, mscontext{0x7AA}, dcsr{0x7B0}, dpc{0x7B1}, dscratch0{0x7B2}, dscratch1{0x7B3}, cpuctrlsts{0x7C0}, secureseed{0x7C1}, mcycle{0xB00}, mcycleh{0xB80}, minstret{0xB02}, minstreth{0xB82}, hpm{0xB03..0xB0C}, hpmh{0xB83..0xB8C}, hpm_unimpl{0xB0D..0xB1F 0xB8D..0xB9F}, cycle_alias{0xC00 0xC80}, instret_alias{0xC02 0xC82}, hpm_alias{0xC03..0xC0C 0xC83..0xC8C}, mvendorid{0xF11}, marchid{0xF12}, mimpid{0xF13}, mhartid{0xF14}, mconfigptr{0xF15}
  - cp_when = position of the read after reset: bins first_insn{first retired instruction}, early{retirement index 2..16}, later{>16}
  - cp_boot_lo = boot_addr_i[7:0]: bins zero{0}, nonzero{!=0}
  - cp_hart = hart_id_i class: bins zero{0}, all1{0xFFFF_FFFF}, rand{other}
  - cp_dbg = rvfi_ext_debug_mode at the read: bins nondbg{0}, dbg{1}
- Crosses:
  - cr_mtvec_first = cp_csr(mtvec) x cp_when x cp_boot_lo: bins mtvec_first_zero{mtvec first_insn zero}, mtvec_first_nonzero{mtvec first_insn nonzero}, mtvec_early_zero{mtvec early zero}, mtvec_early_nonzero{mtvec early nonzero}
  - cr_first_csr = cp_csr x cp_when(first_insn): bins mstatus_first{mstatus}, mie_first{mie}, mcycle_first{mcycle}, minstret_first{minstret}, mhartid_first{mhartid}, misa_first{misa}, cpuctrlsts_first{cpuctrlsts}
  - cr_dbg_reset = cp_csr x cp_dbg(dbg): bins dcsr_dbg{dcsr}, dpc_dbg{dpc}, dscratch0_dbg{dscratch0}, dscratch1_dbg{dscratch1}, tdata1_dbg{tdata1}
  - cr_hart_rd = cp_csr(mhartid) x cp_hart: bins hart_zero{zero}, hart_all1{all1}, hart_rand{rand}
- Adopted (riscv-dv): none
- TP items: TP-CSR-019, TP-CSR-020, TP-CSR-021, TP-CSR-027, TP-CSR-028, TP-CSR-032, TP-CSR-037, TP-CSR-038, TP-CSR-039, TP-CSR-042, TP-CSR-047, TP-CSR-050, TP-CSR-053, TP-CSR-058, TP-CSR-061, TP-CSR-062, TP-CSR-066, TP-CSR-069, TP-CSR-071, TP-CSR-080, TP-CSR-081, TP-CSR-082, TP-CSR-083, TP-CSR-085, TP-CSR-092, TP-CSR-095, TP-CSR-097, TP-CSR-099, TP-CSR-105, TP-CSR-106, TP-CSR-107, TP-CSR-108, TP-CSR-109

### CG-CSR-017: gen_cg_csr_storm
- Features: F-CSR-001, F-CSR-006, F-CSR-009, F-CSR-014, F-CSR-099, F-CSR-100
- Sample: once per window of 256 RVFI retirements in tests running knob:instr_mix = csr_heavy; condition: window complete; anti-vacuity: windows only close after 256 retirements, so a hit proves a full window of the recorded CSR density, privilege mix and trap density ran with alert_major_internal_o observed; density bins are stimulus coverage, the alert bin is a witness that the shadow-CSR path never fires (F-CSR-099).
- Coverpoints:
  - cp_density = CSR instructions in the window: bins low{<16}, mid{16..63}, high{>=64}
  - cp_trap_density = illegal-CSR traps in the window: bins none{0}, some{1..7}, many{>=8}
  - cp_priv_mix = privilege of CSR instructions in the window: bins m_only{all M}, u_only{all U}, mixed{both}
  - cp_distinct = distinct CSR addresses touched in the window: bins few{<4}, some{4..15}, many{>=16}
  - cp_alert_int = alert_major_internal_o asserted in the window: bins none{0}; ignore_bins seen{1}: a hit is a gen_chk_alerts failure, not a coverage target
  - cp_dbg_mix = window contains debug-mode CSR accesses: bins no{0}, yes{1}
  - cp_irq_mix = window contains at least one interrupt entry: bins no{0}, yes{1}
- Crosses:
  - cr_density_priv = cp_density x cp_priv_mix: bins high_mixed{high mixed}, high_m_only{high m_only}, mid_mixed{mid mixed}, mid_m_only{mid m_only}, low_u_only{low u_only}, mid_u_only{mid u_only}
  - cr_trap_density = cp_density x cp_trap_density: bins high_many{high many}, high_none{high none}, mid_some{mid some}, high_some{high some}
  - cr_distinct_density = cp_distinct x cp_density: bins many_high{many high}, some_mid{some mid}, few_high{few high}
  - cr_alert_density = cp_alert_int x cp_density: bins none_high{none high}, none_mid{none mid}
  - cr_mix = cp_dbg_mix x cp_irq_mix x cp_density: bins dbg_irq_high{yes yes high}, dbg_noirq_high{yes no high}, nodbg_irq_high{no yes high}, nodbg_irq_mid{no yes mid}
- Adopted (riscv-dv): none
- TP items: TP-CSR-100, TP-CSR-112, TP-CSR-116, TP-CSR-117, TP-CSR-118, TP-CSR-119, TP-CSR-120

## Covergroups: PRV

### CG-PRV-001: gen_cg_prv_transition
- Features: F-PRV-001, F-PRV-002, F-PRV-006, F-PRV-009, F-PRV-010, F-PRV-021, F-PRV-022, F-PRV-023, F-PRV-025, F-PRV-026, F-PRV-027, F-PRV-033
- Sample: every change of the effective mode (rvfi_mode, rvfi_ext_debug_mode) between consecutive RVFI retirements, plus the first retirement after reset; condition: mode(n) != mode(n-1) or debug(n) != debug(n-1) or first retirement; anti-vacuity: straight-line code in one mode never samples; a hit proves a transition of the named kind happened through the named instruction/event, which gen_isa_compare (mode per retirement) and gen_chk_debug (debug entries/dret) check.
- Coverpoints:
  - cp_from = mode before: bins m{M non-debug}, u{U}, dbg{debug mode}, reset{first retirement}
  - cp_to = mode after: bins m{M non-debug}, u{U}, dbg{debug mode}
  - cp_via = event causing the change: bins mret{mret}, ecall{ecall}, ebreak{ebreak or c.ebreak exception}, illegal{illegal instruction incl illegal CSR / mret-in-U / wfi-TW / dret}, fetch_fault{instruction access fault}, ls_fault{load/store fault}, irq{interrupt}, nmi{NMI}, dbg_req{debug_req_i}, dbg_step{single step}, dbg_trigger{trigger match}, dbg_ebreak{ebreak into debug}, dret{dret}, reset{reset release}, dbg_exc{exception inside debug mode}
  - cp_seq3 = last three modes at a change (M/U/D): bins m_u_m{M U M}, u_m_u{U M U}, m_d_m{M D M}, m_d_u{M D U}, u_d_u{U D U}, u_d_m{U D M}, d_u_m{D U M}, d_m_u{D M U}, m_m_u{M M U}, u_m_m{U M M}; ignore m_u_u: U cannot change to U (every trap enters M)
  - cp_u_exit = cause of leaving U-mode: bins ecall{ecall}, ebreak{ebreak}, illegal_insn{illegal opcode}, illegal_csr{illegal CSR access}, fetch_fault{fetch fault}, ls_fault{load/store fault}, irq{interrupt}, nmi{NMI}, dbg_req{debug_req_i}, step{single step}, trigger{trigger}, wfi_tw{wfi with TW=1}, mret_in_u{mret in U}, dret_in_u{dret in U}
- Crosses:
  - cr_trans = cp_from x cp_to x cp_via (legal transitions only, enumerated): bins m_m_mret{m m mret}, m_u_mret{m u mret}, u_m_ecall{u m ecall}, u_m_ebreak{u m ebreak}, u_m_illegal{u m illegal}, u_m_fetch_fault{u m fetch_fault}, u_m_ls_fault{u m ls_fault}, u_m_irq{u m irq}, u_m_nmi{u m nmi}, m_m_ecall{m m ecall}, m_m_ebreak{m m ebreak}, m_m_illegal{m m illegal}, m_m_fetch_fault{m m fetch_fault}, m_m_ls_fault{m m ls_fault}, m_m_irq{m m irq}, m_m_nmi{m m nmi}, m_dbg_req{m dbg dbg_req}, u_dbg_req{u dbg dbg_req}, m_dbg_step{m dbg dbg_step}, u_dbg_step{u dbg dbg_step}, m_dbg_trigger{m dbg dbg_trigger}, u_dbg_trigger{u dbg dbg_trigger}, m_dbg_ebreak{m dbg dbg_ebreak}, u_dbg_ebreak{u dbg dbg_ebreak}, dbg_m_dret{dbg m dret}, dbg_u_dret{dbg u dret}, dbg_dbg_exc{dbg dbg dbg_exc}, reset_m{reset m reset}; ignore u_u_any: no U to U transition exists; ignore dbg_x_mret: mret in debug mode does not leave debug mode; ignore m_u_any except mret and dret: only mret (and dret from debug) lower the privilege
  - cr_u_exit_seq = cp_u_exit x cp_seq3: bins ecall_m_u_m{ecall m_u_m}, irq_m_u_m{irq m_u_m}, nmi_m_u_m{nmi m_u_m}, illegal_csr_m_u_m{illegal_csr m_u_m}, wfi_tw_m_u_m{wfi_tw m_u_m}, mret_in_u_m_u_m{mret_in_u m_u_m}, dret_in_u_m_u_m{dret_in_u m_u_m}, dbg_req_u_d_u{dbg_req u_d_u}, step_u_d_u{step u_d_u}, trigger_u_d_m{trigger u_d_m}, ls_fault_m_u_m{ls_fault m_u_m}, fetch_fault_m_u_m{fetch_fault m_u_m}, ebreak_m_u_m{ebreak m_u_m}
- Adopted (riscv-dv): none
- TP items: TP-CSR-014, TP-CSR-024, TP-PRV-001, TP-PRV-002, TP-PRV-004, TP-PRV-005, TP-PRV-008, TP-PRV-009, TP-PRV-010, TP-PRV-014, TP-PRV-015, TP-PRV-017, TP-PRV-020, TP-PRV-021, TP-PRV-022, TP-PRV-024, TP-PRV-025, TP-PRV-026, TP-PRV-030, TP-PRV-032, TP-PRV-036, TP-PRV-037, TP-PRV-038

### CG-PRV-002: gen_cg_prv_mstatus_stack
- Features: F-PRV-002, F-PRV-003, F-PRV-004, F-PRV-006, F-PRV-007, F-PRV-008, F-PRV-011, F-PRV-012, F-PRV-024, F-PRV-031
- Sample: (a) trap entry = first handler retirement (rvfi_intr) or the retirement following a trapped instruction, (b) mret retirement; condition: either event; anti-vacuity: only trap entries and mrets sample; the pre-event MIE/priv/MPP/MPIE/MPRV values come from the TB's mstatus model (validated by read-backs), so a hit proves the stack push/pop of that shape happened and gen_isa_compare / gen_chk_csr_readback compared the resulting mstatus.
- Coverpoints:
  - cp_event = event: bins trap_entry{trap entry}, mret{mret}
  - cp_prev_priv = mode of the trapped/interrupted instruction: bins m{3}, u{0}
  - cp_prev_mie = mstatus.MIE before the trap: bins b0{0}, b1{1}
  - cp_cause = trap class: bins sync_exc{exception}, irq{interrupt}, nmi{NMI external or internal}
  - cp_mpp_at_mret = mstatus.MPP before mret: bins u{00}, m{11}
  - cp_mpie_at_mret = mstatus.MPIE before mret: bins b0{0}, b1{1}
  - cp_mprv_at_mret = mstatus.MPRV before mret: bins b0{0}, b1{1}
  - cp_nmi_mode = mret executed inside an NMI handler: bins no{0}, yes{1}
  - cp_sw_mepc_in_nmi = software wrote mepc or mcause inside the NMI handler before mret: bins no{0}, yes{1}
  - cp_irq_at_mret = enabled interrupt pending when mret retires: bins none{0}, pending{1}
  - cp_mepc_odd_lsb = mepc[1] at mret (2-byte aligned target): bins b0{0}, b1{1}
- Crosses:
  - cr_entry = cp_prev_priv x cp_prev_mie x cp_cause: bins u_mie0_irq{u b0 irq}, u_mie1_irq{u b1 irq}, u_mie0_sync{u b0 sync_exc}, u_mie1_sync{u b1 sync_exc}, m_mie0_sync{m b0 sync_exc}, m_mie1_sync{m b1 sync_exc}, m_mie1_irq{m b1 irq}, m_mie0_nmi{m b0 nmi}, m_mie1_nmi{m b1 nmi}, u_mie0_nmi{u b0 nmi}, u_mie1_nmi{u b1 nmi}; ignore m_mie0_irq: interrupts are not taken in M with MIE=0
  - cr_mret = cp_mpp_at_mret x cp_mpie_at_mret x cp_mprv_at_mret: bins u_0_0{u b0 b0}, u_0_1{u b0 b1}, u_1_0{u b1 b0}, u_1_1{u b1 b1}, m_0_0{m b0 b0}, m_0_1{m b0 b1}, m_1_0{m b1 b0}, m_1_1{m b1 b1}
  - cr_nmi_mret = cp_nmi_mode x cp_sw_mepc_in_nmi: bins nmi_sw_no{yes no}, nmi_sw_yes{yes yes}, nonnmi_sw_no{no no}; ignore nonnmi_sw_yes: the coverpoint is defined inside NMI handlers only
  - cr_mret_irq = cp_mpp_at_mret x cp_mpie_at_mret x cp_irq_at_mret: bins m_1_pending{m b1 pending}, m_0_pending{m b0 pending}, u_0_pending{u b0 pending}, u_1_pending{u b1 pending}, m_1_none{m b1 none}, u_1_none{u b1 none}
  - cr_mret_target = cp_mpp_at_mret x cp_mepc_odd_lsb: bins u_b1{u b1}, m_b1{m b1}, u_b0{u b0}, m_b0{m b0}
- Adopted (riscv-dv): none
- TP items: TP-CSR-040, TP-CSR-094, TP-PRV-002, TP-PRV-003, TP-PRV-005, TP-PRV-006, TP-PRV-007, TP-PRV-008, TP-PRV-010, TP-PRV-011, TP-PRV-023, TP-PRV-030, TP-PRV-036, TP-PRV-037

### CG-PRV-003: gen_cg_prv_mprv
- Features: F-PRV-013, F-PRV-014, F-PRV-015
- Sample: every retired load or store (rvfi_mem_rmask or rvfi_mem_wmask nonzero, or a trapped LSU instruction); condition: rvfi_valid && is_load_store(rvfi_insn); anti-vacuity: non-memory instructions never sample; MPRV/MPP come from the TB mstatus model, the PMP outcome from rvfi_trap plus gen_chk_pmp's prediction, so a hit proves a data access ran under that effective-privilege configuration and gen_chk_pmp checked it.
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_mprv = mstatus.MPRV: bins b0{0}, b1{1}
  - cp_mpp = mstatus.MPP: bins u{00}, m{11}
  - cp_access = access type: bins load{load}, store{store}
  - cp_outcome = PMP outcome: bins allow{no fault}, fault{access fault}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_after_dret_u = first 8 U-mode retirements after a dret that left MPRV=1: bins no{0}, yes{1}
  - cp_pmp_cfg = PMP configuration class for the address (from gen_chk_pmp): bins m_only{region allows M only}, u_rw{region allows U}, no_region{no match}
- Crosses:
  - cr_eff = cp_priv x cp_mprv x cp_mpp x cp_access x cp_outcome: bins m_1_u_load_fault{m b1 u load fault}, m_1_u_store_fault{m b1 u store fault}, m_1_u_load_allow{m b1 u load allow}, m_1_u_store_allow{m b1 u store allow}, m_1_m_load_allow{m b1 m load allow}, m_1_m_store_allow{m b1 m store allow}, m_0_u_load_allow{m b0 u load allow}, m_0_m_store_allow{m b0 m store allow}, u_1_m_load_allow{u b1 m load allow B1 window}, u_1_m_store_allow{u b1 m store allow B1 window}, u_1_u_load_fault{u b1 u load fault}, u_0_u_load_fault{u b0 u load fault}, u_0_u_store_fault{u b0 u store fault}, u_0_u_load_allow{u b0 u load allow}, u_0_m_load_allow{u b0 m load allow}
  - cr_dbg_mprv = cp_dbg(dbg) x cp_mprv x cp_mpp x cp_outcome: bins dbg_1_u_fault{dbg b1 u fault B2}, dbg_1_u_allow{dbg b1 u allow}, dbg_0_u_allow{dbg b0 u allow}, dbg_0_m_allow{dbg b0 m allow}, dbg_1_m_allow{dbg b1 m allow}
  - cr_after_dret = cp_after_dret_u(yes) x cp_pmp_cfg x cp_outcome: bins dret_m_only_allow{yes m_only allow}, dret_m_only_fault{yes m_only fault}, dret_u_rw_allow{yes u_rw allow}, dret_no_region_fault{yes no_region fault}
  - cr_mprv_cfg = cp_priv(m) x cp_mprv(b1) x cp_mpp(u) x cp_pmp_cfg x cp_outcome: bins m_only_fault{m_only fault}, u_rw_allow{u_rw allow}, no_region_fault{no_region fault}
- Adopted (riscv-dv): none
- TP items: TP-PRV-006, TP-PRV-012, TP-PRV-013, TP-PRV-014, TP-PRV-035

### CG-PRV-004: gen_cg_prv_umode_illegal
- Features: F-PRV-010, F-PRV-016, F-PRV-017, F-PRV-021, F-PRV-022, F-PRV-025, F-PRV-028
- Sample: rvfi_valid with rvfi_insn opcode SYSTEM and funct3 == 000 (ecall, ebreak, mret, dret, wfi, sret, uret, sfence.vma, others) or c.ebreak, trapped or not; condition: rvfi_valid && is_priv_insn(rvfi_insn); anti-vacuity: only privileged-instruction retirements sample; a hit proves the named instruction executed in that mode/TW/debug state with the recorded outcome, which gen_isa_compare checks (cause 2/3/8/11, mtval).
- Coverpoints:
  - cp_kind = instruction: bins ecall{0x00000073}, ebreak{0x00100073}, c_ebreak{0x9002}, mret{0x30200073}, dret{0x7B200073}, wfi{0x10500073}, sret{0x10200073}, uret{0x00200073}, sfence_vma{funct7 0001001}, other_priv{other imm with rs1=rd=0}, nz_rs1_rd{ecall/ebreak/mret/dret/wfi encoding with rs1 or rd != 0}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_tw = mstatus.TW: bins b0{0}, b1{1}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_mcause = mcause read in the handler: bins ill{2}, brk{3}, ecall_u{8}, ecall_m{11}; ignore_bins other: no privileged instruction produces another cause; a hit is a gen_isa_compare failure
  - cp_ebreak_dcsr = dcsr.ebreakm/ebreaku bit for the current mode: bins b0{0}, b1{1}
  - cp_mtval = mtval read in the handler: bins zero{0}, insn{== rvfi_insn}; ignore_bins other: mtval is 0 or the encoding for every privileged-instruction trap; a hit is a gen_isa_compare failure
- Crosses:
  - cr_kind_priv_trap = cp_kind x cp_priv x cp_dbg x cp_tw x cp_trap (required subset): bins ecall_m_trap{ecall m nondbg trap}, ecall_u_trap{ecall u nondbg trap}, ebreak_m_trap{ebreak m nondbg trap}, ebreak_u_trap{ebreak u nondbg trap}, c_ebreak_m_trap{c_ebreak m nondbg trap}, c_ebreak_u_trap{c_ebreak u nondbg trap}, mret_m_ok{mret m nondbg ok}, mret_u_trap{mret u nondbg trap}, dret_m_nondbg_trap{dret m nondbg trap}, dret_u_nondbg_trap{dret u nondbg trap}, dret_dbg_ok{dret m dbg ok}, wfi_m_tw0_ok{wfi m b0 ok}, wfi_m_tw1_ok{wfi m b1 ok}, wfi_u_tw0_ok{wfi u b0 ok}, wfi_u_tw1_trap{wfi u b1 trap}, wfi_dbg_ok{wfi m dbg ok}, sret_m_trap{sret m trap}, sret_u_trap{sret u trap}, uret_m_trap{uret m trap}, uret_u_trap{uret u trap}, sfence_m_trap{sfence_vma m trap}, sfence_u_trap{sfence_vma u trap}, other_m_trap{other_priv m trap}, other_u_trap{other_priv u trap}, nz_m_trap{nz_rs1_rd m trap}, nz_u_trap{nz_rs1_rd u trap}, ecall_dbg_trap{ecall m dbg trap}, mret_dbg_ok{mret m dbg ok}; ignore mret_u_ok, wfi_u_tw1_ok, dret_nondbg_ok, sret/uret/sfence/other/nz x ok: decoder rules are unconditional
  - cr_ecall_cause = cp_kind(ecall) x cp_priv x cp_mcause x cp_mtval: bins ecall_u_8{u ecall_u zero}, ecall_m_11{m ecall_m zero}
  - cr_ebreak_cause = cp_kind x cp_ebreak_dcsr x cp_mcause x cp_mtval: bins ebreak_dcsr0_3{ebreak b0 brk zero}, c_ebreak_dcsr0_3{c_ebreak b0 brk zero}, ebreak_dcsr1_dbg{ebreak b1 debug entry}, c_ebreak_dcsr1_dbg{c_ebreak b1 debug entry}
  - cr_illegal_mtval = cp_kind x cp_trap(trap) x cp_mcause(ill) x cp_mtval(insn): bins mret_u_mtval{mret}, wfi_tw_mtval{wfi}, dret_mtval{dret}, sret_mtval{sret}, uret_mtval{uret}, sfence_mtval{sfence_vma}, nz_mtval{nz_rs1_rd}
- Adopted (riscv-dv): none
- TP items: TP-PRV-009, TP-PRV-015, TP-PRV-016, TP-PRV-019, TP-PRV-020, TP-PRV-021, TP-PRV-024, TP-PRV-027, TP-PRV-036

### CG-PRV-005: gen_cg_prv_wfi
- Features: F-PRV-016, F-PRV-017, F-PRV-018, F-PRV-019, F-PRV-020
- Sample: every retired wfi (trapped or not) with the wake event that ended the sleep (from core_busy_o, irq pins, irq_nm_i, debug_req_i and the next retirement); condition: rvfi_valid && rvfi_insn == wfi; anti-vacuity: only wfi retirements sample; a hit proves a wfi in that mode/TW/MIE configuration slept for the recorded length and was ended by the recorded source, which gen_chk_sleep checks (no bus activity, correct wake set).
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_tw = mstatus.TW: bins b0{0}, b1{1}
  - cp_mie = mstatus.MIE: bins b0{0}, b1{1}
  - cp_wake = wake source: bins irq_en{irq with mie bit set}, nmi{irq_nm_i}, dbg_req{debug_req_i}, step{dcsr.step}, none_pending_before{irq already pending no sleep}
  - cp_irq_dis_seen = an irq pin with mie bit clear toggled during the sleep: bins no{0}, yes{1}
  - cp_len = core_busy_o low cycles: bins zero{0}, short{1..16}, long{>16}
  - cp_post = what follows the wfi: bins irq_taken{handler entry}, resume_next{wfi+4 retires}, dbg_entry{debug entry}, trap_tw{illegal instruction}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
- Crosses:
  - cr_priv_tw_post = cp_priv x cp_tw x cp_post: bins m_tw0_irq_taken{m b0 irq_taken}, m_tw1_irq_taken{m b1 irq_taken}, m_tw0_resume{m b0 resume_next}, m_tw1_resume{m b1 resume_next}, u_tw0_irq_taken{u b0 irq_taken}, u_tw1_trap{u b1 trap_tw}, m_tw0_dbg{m b0 dbg_entry}, u_tw0_dbg{u b0 dbg_entry}; ignore u_tw1_irq_taken, u_tw1_resume, u_tw1_dbg: TW=1 in U traps immediately; ignore u_tw0_resume: U-mode interrupts are always enabled so a wake by irq is taken
  - cr_mie_post = cp_priv(m) x cp_mie x cp_post: bins m_mie0_resume{b0 resume_next}, m_mie1_irq_taken{b1 irq_taken}, m_mie0_dbg{b0 dbg_entry}, m_mie1_dbg{b1 dbg_entry}
  - cr_len_wake = cp_len x cp_wake: bins zero_irq_en{zero irq_en}, short_irq_en{short irq_en}, long_irq_en{long irq_en}, long_nmi{long nmi}, short_nmi{short nmi}, long_dbg_req{long dbg_req}, short_dbg_req{short dbg_req}, zero_none_pending{zero none_pending_before}
  - cr_dis_irq = cp_irq_dis_seen(yes) x cp_wake: bins dis_then_irq_en{yes irq_en}, dis_then_nmi{yes nmi}, dis_then_dbg{yes dbg_req}
  - cr_dbg_wfi = cp_dbg(dbg) x cp_len: bins dbg_zero{dbg zero}
- Adopted (riscv-dv): none
- TP items: TP-CSR-031, TP-PRV-015, TP-PRV-016, TP-PRV-017, TP-PRV-018, TP-PRV-019

### CG-PRV-006: gen_cg_prv_irq_enable
- Features: F-PRV-008, F-PRV-012, F-PRV-018, F-PRV-023, F-PRV-024, F-PRV-029, F-PRV-031
- Sample: every RVFI retirement while irq_pending_o == 1 or irq_nm_i == 1, and every interrupt entry; condition: rvfi_valid && (irq_pending_o || irq_nm_i || rvfi_intr); anti-vacuity: retirements without a pending interrupt never sample; a hit proves an interrupt was pending in the recorded mode/MIE/debug state and was or was not taken before the next retirement, which gen_chk_irq checks against the enable rule.
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_mie = mstatus.MIE: bins b0{0}, b1{1}
  - cp_taken = interrupt taken before the next retirement: bins yes{1}, no{0}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_step = dcsr.step: bins b0{0}, b1{1}
  - cp_nmi_mode = inside an NMI handler (rvfi_ext_nmi since last mret): bins no{0}, yes{1}
  - cp_kind = highest-priority pending source: bins sw{irq_software_i}, timer{irq_timer_i}, ext{irq_external_i}, fast{irq_fast_i}, nmi{irq_nm_i}
  - cp_zcmp = retirement is inside a Zcmp expanded sequence: bins no{0}, yes{1}
- Crosses:
  - cr_priv_mie_taken = cp_priv x cp_mie x cp_taken (nondbg, step 0, no nmi_mode, no zcmp): bins m_0_no{m b0 no}, m_1_yes{m b1 yes}, u_0_yes{u b0 yes}, u_1_yes{u b1 yes}; ignore m_0_yes: MIE=0 blocks in M (NMI covered separately)
  - cr_block = cp_taken(no) x cp_dbg x cp_step x cp_nmi_mode x cp_zcmp: bins blocked_dbg{dbg}, blocked_step{step b1}, blocked_nmi_mode{nmi_mode yes}, blocked_zcmp{zcmp yes}
  - cr_kind_priv = cp_kind x cp_priv x cp_taken(yes): bins sw_m{sw m}, sw_u{sw u}, timer_m{timer m}, timer_u{timer u}, ext_m{ext m}, ext_u{ext u}, fast_m{fast m}, fast_u{fast u}, nmi_m{nmi m}, nmi_u{nmi u}
  - cr_nmi_mie = cp_kind(nmi) x cp_mie x cp_taken(yes): bins nmi_mie0{b0}, nmi_mie1{b1}
- Adopted (riscv-dv): none
- TP items: TP-CSR-026, TP-PRV-003, TP-PRV-007, TP-PRV-011, TP-PRV-017, TP-PRV-022, TP-PRV-023, TP-PRV-028, TP-PRV-030, TP-PRV-037, TP-PRV-038

### CG-PRV-007: gen_cg_prv_debug_priv
- Features: F-PRV-005, F-PRV-015, F-PRV-025, F-PRV-026, F-PRV-027
- Sample: (a) debug entry = first retirement with rvfi_ext_debug_mode rising, (b) dret retirement, (c) a trapped retirement while rvfi_ext_debug_mode == 1; condition: any of a..c; anti-vacuity: only debug-related events sample; the dcsr.prv / MPRV / MPP values come from the debug program's own CSR reads (dcsr, mstatus) inside debug mode, so a hit proves a resume of that shape happened and gen_chk_debug / gen_chk_csr_readback checked dcsr/dpc/mstatus.
- Coverpoints:
  - cp_event = event: bins entry{debug entry}, dret{dret}, exc_in_dbg{exception in debug mode}
  - cp_from = mode before entry: bins m{3}, u{0}
  - cp_cause = dcsr.cause read in debug mode: bins ebreak{1}, trigger{2}, haltreq{3}, step{4}
  - cp_prv_written = value the debug program wrote to dcsr.prv before dret: bins none{no write}, u{00}, s{01}, h{10}, m{11}
  - cp_prv_at_dret = dcsr.prv read before dret: bins u{00}, m{11}
  - cp_mprv_at_dret = mstatus.MPRV before dret: bins b0{0}, b1{1}
  - cp_mpp_at_dret = mstatus.MPP before dret: bins u{00}, m{11}
  - cp_mst_touched = mstatus/mepc/mcause/mtval changed across the debug entry (read before and after): bins no{0}; ignore_bins yes{1}: a hit is a gen_chk_debug failure
  - cp_exc_kind = exception kind in debug mode: bins illegal{illegal instruction}, ecall{ecall}, ebreak{ebreak}, ls_fault{load/store fault}, fetch_fault{fetch fault}, csr_illegal{illegal CSR}
  - cp_mst_after_exc = mstatus/mepc/mcause/mtval changed by the debug-mode exception: bins no{0}; ignore_bins yes{1}: a hit is a gen_chk_debug failure
- Crosses:
  - cr_entry = cp_event(entry) x cp_from x cp_cause: bins m_ebreak{m ebreak}, u_ebreak{u ebreak}, m_trigger{m trigger}, u_trigger{u trigger}, m_haltreq{m haltreq}, u_haltreq{u haltreq}, m_step{m step}, u_step{u step}
  - cr_entry_touched = cp_event(entry) x cp_mst_touched: bins entry_no{no}; ignore entry_yes: a hit is a gen_chk_debug failure (M CSRs changed by a debug entry), not a coverage target
  - cr_dret_prv = cp_prv_written x cp_prv_at_dret: bins none_m{none m}, none_u{none u}, u_u{u u}, s_u{s u}, h_u{h u}, m_m{m m}; ignore s_m and h_m: legalised to U
  - cr_dret_mprv = cp_prv_at_dret x cp_mprv_at_dret x cp_mpp_at_dret: bins u_1_m{u b1 m B1 core case}, u_1_u{u b1 u}, u_0_u{u b0 u}, u_0_m{u b0 m}, m_1_u{m b1 u}, m_1_m{m b1 m}, m_0_m{m b0 m}, m_0_u{m b0 u}
  - cr_exc_dbg = cp_event(exc_in_dbg) x cp_exc_kind x cp_mst_after_exc: bins illegal_no{illegal no}, ecall_no{ecall no}, ebreak_no{ebreak no}, ls_fault_no{ls_fault no}, fetch_fault_no{fetch_fault no}, csr_illegal_no{csr_illegal no}
- Adopted (riscv-dv): none
- TP items: TP-CSR-075, TP-CSR-077, TP-CSR-086, TP-PRV-004, TP-PRV-014, TP-PRV-024, TP-PRV-025, TP-PRV-026, TP-PRV-038

### CG-PRV-008: gen_cg_prv_trap_vector
- Features: F-PRV-002, F-PRV-021, F-PRV-022, F-PRV-029, F-PRV-030, F-PRV-031, F-PRV-032
- Sample: every trap entry (rvfi_pc_wdata of a trapped retirement, or rvfi_intr on the first handler retirement); condition: rvfi_trap || rvfi_intr; anti-vacuity: ordinary retirements never sample; the target, mepc source and mtval class are computed from RVFI (pc of the trapping instruction, of the next one, of the LSU instruction in WB) and the handler's CSR reads, so a hit proves a trap of that class vectored as named and gen_isa_compare compared pc/mepc/mcause/mtval.
- Coverpoints:
  - cp_cause = cause class: bins exc{synchronous exception}, irq_sw{cause 3}, irq_timer{cause 7}, irq_ext{cause 11}, irq_fast{cause 16..30}, nmi_ext{0x8000001F}, nmi_int{0xFFFFFFE0}, dbg_exc{exception in debug mode}
  - cp_fast_id = fast interrupt id (irq_fast only; irq_fast width 15): bins f0{0}, f1{1}, f2{2}, f3{3}, f4{4}, f5{5}, f6{6}, f7{7}, f8{8}, f9{9}, f10{10}, f11{11}, f12{12}, f13{13}, f14{14}
  - cp_target = trap target class: bins base{mtvec BASE}, base_4id{BASE + 4*id}, base_7c{BASE + 0x7C}, dm_exc_addr{DmExceptionAddr}
  - cp_base = mtvec BASE class: bins boot_page{boot_addr_i[31:8]}, sw_low{software set < 0x1000}, sw_high{software set bit 31}
  - cp_mepc_src = which PC mepc holds: bins pc_if{next unexecuted}, pc_id{faulting instruction}, pc_wb{LSU instruction in WB}
  - cp_mtval = mtval class: bins zero{0}, insn32{32-bit encoding}, insn16{16-bit encoding zero-extended}, addr{faulting address}
  - cp_from_priv = rvfi_mode of the trapping/interrupted instruction: bins m{3}, u{0}
  - cp_younger_in_id = a younger instruction was in ID when a WB LSU fault trapped: bins no{0}, yes{1}
- Crosses:
  - cr_cause_target = cp_cause x cp_target: bins exc_base{exc base}, irq_sw_4id{irq_sw base_4id}, irq_timer_4id{irq_timer base_4id}, irq_ext_4id{irq_ext base_4id}, irq_fast_4id{irq_fast base_4id}, nmi_ext_7c{nmi_ext base_7c}, nmi_int_7c{nmi_int base_7c}, dbg_exc_dm{dbg_exc dm_exc_addr}
  - cr_fast_id = cp_fast_id x cp_target(base_4id): bins f0{f0}, f1{f1}, f2{f2}, f3{f3}, f4{f4}, f5{f5}, f6{f6}, f7{f7}, f8{f8}, f9{f9}, f10{f10}, f11{f11}, f12{f12}, f13{f13}, f14{f14}
  - cr_cause_mepc = cp_cause x cp_mepc_src x cp_younger_in_id: bins exc_pc_id{exc pc_id no}, exc_pc_wb{exc pc_wb no}, exc_pc_wb_younger{exc pc_wb yes}, irq_pc_if{irq_sw irq_timer irq_ext irq_fast pc_if}, nmi_pc_if{nmi_ext nmi_int pc_if}
  - cr_exc_mtval = cp_cause(exc) x cp_mtval: bins exc_zero{zero ecall ebreak}, exc_insn32{insn32}, exc_insn16{insn16}, exc_addr{addr}
  - cr_base_cause = cp_base x cp_cause: bins boot_exc{boot_page exc}, boot_irq{boot_page irq_timer}, low_irq_sw{sw_low irq_sw}, high_irq_fast{sw_high irq_fast}, high_nmi{sw_high nmi_ext}, low_exc{sw_low exc}, high_exc{sw_high exc}
  - cr_from_cause = cp_from_priv x cp_cause: bins u_exc{u exc}, u_irq_fast{u irq_fast}, u_nmi{u nmi_ext}, m_exc{m exc}, m_irq_ext{m irq_ext}, m_nmi_int{m nmi_int}, u_nmi_int{u nmi_int}
- Adopted (riscv-dv): none
- TP items: TP-CSR-035, TP-CSR-037, TP-CSR-041, TP-CSR-047, TP-CSR-048, TP-CSR-049, TP-PRV-002, TP-PRV-004, TP-PRV-011, TP-PRV-020, TP-PRV-021, TP-PRV-028, TP-PRV-029, TP-PRV-030, TP-PRV-031, TP-PRV-037

## Counts

| Quantity | Count |
|---|---|
| covergroups | 25 (CG-CSR-001..017, CG-PRV-001..008) |
| coverpoints | 208 |
| crosses | 128 |
| coverpoint bins | 897 |
| cross bins | 1213 |
| total bins | 2110 |
| adopted (riscv-dv) bins | 0 |
| bins referenced by at least one TP item | 2110 (all) |
| ignore_bins declared | 47 (each with a reason; never-hit witnesses are ignores, not targets) |

Traceability convention for trace_tp_bin_csr.csv: an item row for a cross bin implies rows for the
constituent coverpoint bins named in that cross bin's description (the CSV lists them explicitly:
1820 direct rows plus 1744 derived constituent rows = 3564 rows, adopted = 0 everywhere).
Counts and ranges derive from ibex_pkg parameters as stated in the conventions (MHPMCounterNum,
PMPNumRegions, irq_fast width, DbgHwBreakNum); the bin lists above expand them for this build.

## Probe candidates

Bins that cannot be sampled from the DUT boundary or RVFI alone. The DV Lead decides whether the
named internal signal enters the probe register; each entry gives the boundary alternative used
if the probe is refused.

- CG-CSR-010.cp_pulse (and every cr_op_form_pulse bin): probe candidate P7 (probe register entry
  needed; P1-P6 are taken in dv/auto_dv/docs/gen_probe_register.md): cs_registers_i.dummy_instr_seed_en_o
  and dummy_instr_seed_o (rtl/ibex_cs_registers.sv:1914-1915); coverage and fire-check only, never a
  checker input (F-CSR-092/093). The reseed has no boundary or RVFI
  footprint (dummy instructions are not reported on RVFI and their cadence is not deterministic).
  Alternative if refused: keep the read-back-0 / no-trap / no-flush bins only (cr_rd_value,
  cr_u, cp_op x cp_rs1) and drop cp_pulse; TP-CSR-092/093 then lose their pulse fire-check.
- CG-CSR-013.cp_carry_win (cr_carry.carry_yes): the exact cycle of the mcycleh write commit is
  internal (cs_registers_i.csr_we_int with csr_addr == MCYCLEH; P6-class net, not requested). Boundary inference used by
  TP-CSR-064: rvfi_ext_mcycle of the retiring writer shows low == 0xFFFF_FFFF and high == written
  value; the inference is exact because rvfi_ext_mcycle is captured at the writer's retirement.
  No probe needed unless the inference is found ambiguous in simulation.
- CG-CSR-013.cp_coincide for hpm counters (cr_minstret_wr.hpm_lo_wr_coincide,
  hpm_hi_wr_coincide, hpm_lo_set_coincide): the event (load/store retiring in WB) in the CSR
  write cycle is inferred from RVFI ordering (load retirement immediately before the CSR write
  with dmem_rvalid_delay = min1). Candidate probe if the inference is too loose:
  cs_registers_i.mhpmcounter_incr[k] in the write cycle.
- CG-CSR-015.cp_cause.dbg_req_before (cr_cause_fam.dbg_before_*): inferred from dpc read in the
  debug ROM == the CSR instruction pc; no probe needed.
- CG-CSR-001.cp_iclass / CG-CSR-014 classes: TB-derived from address, op, mode and
  rvfi_ext_debug_mode; no probe.
- TP-CSR-102 witness gen_sva_csr_excl: never (cs_registers_i.csr_we_int &&
  cs_registers_i.csr_save_cause_i) is an internal assertion on P6-class nets (both operands internal,
  same cycle; witness/coverage only, never a checker);
  boundary alternative: none (the item's boundary pass criteria stand on their own; the assertion
  is an extra witness).
- CG-PRV-006.cp_nmi_mode and cr_block.blocked_nmi_mode: NMI mode is inferred from rvfi_ext_nmi on
  the entry and the following mret; no probe.
- CG-PRV-006.cp_zcmp and cr_block.blocked_zcmp: "inside a Zcmp expanded sequence" is inferred
  from rvfi_insn of the retiring cm.* instruction and the retirement gap; if the DV Lead wants
  exactness, the probe is id_stage_i.instr_expanded_q (rtl/ibex_id_stage.sv, compressed-decoder
  FSM), otherwise the RVFI inference stands.


# 3.3 Areas EXC, IRQ: Synchronous exceptions; interrupts, NMI, WFI, vectoring


Area group EXC + IRQ (F-EXC-001..069, F-IRQ-001..066). Source: dv/auto_dv/work/dv-lead/parts/
gen_part_exc_irq.md; behaviour summaries CTRL-05..19, CTRL-23, CTRL-39..44. Companion test plan:
tp_exc_irq.md (same directory).

Conventions
- Every covergroup lives in the gen_ namespace (gen_cg_exc_*, gen_cg_irq_*) inside gen_fcov_pkg or
  a gen_*_cov module bound through gen_binds.sv. No RTL covergroup is extended (the RTL has none).
- Sampling events come from monitors (RVFI monitor, ibus/dbus monitors, irq/debug pin monitor,
  gen_chk_* model events), never from a bare clock. Each Sample line carries an anti-vacuity note.
- Counts/ranges derive from ibex_pkg: fast-interrupt count = $bits(ibex_pkg::irqs_t.irq_fast) (15),
  fast id = CSR_MFIX_BIT_LOW + index (16..30), interrupt-enable positions CSR_MSIX_BIT (3),
  CSR_MTIX_BIT (7), CSR_MEIX_BIT (11), mstatus positions CSR_MSTATUS_{MIE,MPIE,MPP,MPRV,TW}_BIT,
  cause constants ExcCause* and exc_cause_t, controller states ctrl_fsm_e, PC selectors
  exc_pc_sel_e, Zcmp classes instr_exp_e, debug causes dbg_cause_e, NMI_INT_CAUSE_ECC. Array bins
  written `name[15]` expand to name_0..name_14 with 15 = $bits(irqs_t.irq_fast).
- Bins referenced by TP items and the CSV use CG-<AREA>-<nnn>.cp_<name>.<bin> and
  CG-<AREA>-<nnn>.cr_<name>.<bin>. Cross bins are named as the concatenation of their member bins
  in coverpoint order; the `bins {...}` list of a cross names the REQUIRED cross bins.
- Transition-style bins are enumerated explicitly; no `illegal_bins = default sequence` anywhere.
- "Predicted cause" and "CSR model" mean the gen_isa_compare / gen_chk_csr_readback prediction for
  the trap record, obtained from the retired handler csrr read-back (ibex_core has no rvfi_csr_*
  ports). "Program order" facts come from the test's program listing (ELF), which the TB has.
- Adopted bins: none. This subagent's task does not name riscv-dv, so no riscv-dv source was
  read; every bin below is our own (adopted = 0 in trace_tp_bin_exc_irq.csv).
- Features lines may cite ALIAS / FOLDED feature IDs (gen_part_exc_irq.md `- Status:` lines); the
  bin named in a FOLDED status is the one that carries the folded edge and exists in this file.

## Covergroups: EXC

### CG-EXC-001: gen_cg_exc_trap_entry
- Features: F-EXC-001, F-EXC-002, F-EXC-042, F-EXC-049, F-EXC-060, F-EXC-062, F-EXC-063, F-EXC-064, F-EXC-067, F-EXC-068
- Sample: (a) RVFI trap record; condition: rvfi_valid && rvfi_trap && !rvfi_ext_debug_mode, with the predicted cause taken from the gen_isa_compare trap model of that record; (b) for cp_odd_target only: a retired jalr/jal/branch whose computed target (rvfi_rs1_rdata + imm, or pc + imm) has bit 0 or bit 1 set, with rvfi_trap == 0; anti-vacuity: rvfi_trap is 0 on every normal retirement and interrupts never set it, so a hit of (a) proves a synchronous exception committed outside debug mode; (b) samples only control transfers to non-word-aligned targets, so a hit proves such a transfer completed without an instruction-address-misaligned trap.
- Coverpoints:
  - cp_cause = predicted mcause[4:0]: bins fetch_fault{1}, illegal{2}, breakpoint{3}, load_fault{5}, store_fault{7}, ecall_u{8}, ecall_m{11}; ignore_bins misaligned{0,4,6}: never generated in non-CHERIoT mode (F-EXC-029, F-EXC-067); ignore_bins cheri{28}: cheriot-out-of-scope
  - cp_priv = rvfi_mode of the trapping instruction: bins m{3}, u{0}; ignore_bins s_h{1,2}: privilege modes not implemented
  - cp_ilen = rvfi_insn[1:0] of the faulting instruction: bins c16{0,1,2}, w32{3}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_mtvec_class = class of the mtvec value in force (tracked from boot and retired csrw/csrs mtvec): bins boot_init{never written}, sw_aligned{written with wdata[7:0] in {0,1}}, sw_legalised{written with wdata[7:2] != 0 and legalised}
  - cp_prev_mie = mstatus.MIE before the trap (CSR model): bins mie0{0}, mie1{1}
  - cp_younger_killed = fetched-not-retired words discarded at the flush (ibus monitor vs RVFI): bins none{0}, one{1}, many{[2:$]}
  - cp_odd_target = target alignment of a retired control transfer (sample b): bins odd_no_trap{jalr target bit 0 set: no trap, next rvfi_pc_rdata == target & ~1}, half_target{target bit 1 set, bit 0 clear: 2-byte aligned target executes}
- Crosses:
  - cr_cause_priv_ilen = cp_cause x cp_priv x cp_ilen: bins {fetch_fault_m_c16, fetch_fault_m_w32, fetch_fault_u_c16, fetch_fault_u_w32, illegal_m_c16, illegal_m_w32, illegal_u_c16, illegal_u_w32, breakpoint_m_c16, breakpoint_m_w32, breakpoint_u_c16, breakpoint_u_w32, load_fault_m_c16, load_fault_m_w32, load_fault_u_c16, load_fault_u_w32, store_fault_m_c16, store_fault_m_w32, store_fault_u_c16, store_fault_u_w32, ecall_u_u_w32, ecall_m_m_w32}; ignore ecall_u x m, ecall_m x u: the cause encodes the privilege; ignore ecall_* x c16: there is no compressed ECALL encoding
  - cr_cause_mtvec = cp_cause x cp_mtvec_class: bins {fetch_fault_boot_init, fetch_fault_sw_aligned, fetch_fault_sw_legalised, illegal_boot_init, illegal_sw_aligned, illegal_sw_legalised, breakpoint_boot_init, breakpoint_sw_aligned, breakpoint_sw_legalised, load_fault_boot_init, load_fault_sw_aligned, load_fault_sw_legalised, store_fault_boot_init, store_fault_sw_aligned, store_fault_sw_legalised, ecall_u_boot_init, ecall_u_sw_aligned, ecall_u_sw_legalised, ecall_m_boot_init, ecall_m_sw_aligned, ecall_m_sw_legalised}
  - cr_cause_mie = cp_cause x cp_prev_mie: bins {fetch_fault_mie0, fetch_fault_mie1, illegal_mie0, illegal_mie1, breakpoint_mie0, breakpoint_mie1, load_fault_mie0, load_fault_mie1, store_fault_mie0, store_fault_mie1, ecall_u_mie0, ecall_u_mie1, ecall_m_mie0, ecall_m_mie1}
  - cr_cause_pcalign = cp_cause x cp_pc_align: bins {fetch_fault_half, illegal_half, breakpoint_half, load_fault_half, store_fault_half, ecall_u_half, ecall_m_half, fetch_fault_word, illegal_word, load_fault_word, store_fault_word}
  - cr_cause_killed = cp_cause x cp_younger_killed: bins {load_fault_one, store_fault_one, illegal_many, ecall_m_many, fetch_fault_none}
- Adopted (riscv-dv): none
- TP items: TP-EXC-001, TP-EXC-002, TP-EXC-007, TP-EXC-013, TP-EXC-016, TP-EXC-017, TP-EXC-022, TP-EXC-023, TP-EXC-024, TP-EXC-026, TP-EXC-034, TP-EXC-041, TP-EXC-049, TP-EXC-060, TP-EXC-062, TP-EXC-063, TP-EXC-064, TP-EXC-068, TP-EXC-069, TP-EXC-071

### CG-EXC-002: gen_cg_exc_fetch_fault
- Features: F-EXC-003, F-EXC-004, F-EXC-005, F-EXC-006, F-EXC-007, F-EXC-045, F-EXC-059
- Sample: (a) a trap record with predicted cause 1, correlated with the error-marked fetch words of the ibus monitor (instr_err_i=1 responses) and the gen_chk_pmp I-side deny list; (b) an error-marked word that is discarded (pc_set redirect) without ever producing a trap record; condition: the ibus monitor holds an error mark for the word; anti-vacuity: error marks exist only under knob:imem_err_rate != none, a directed injection or a PMP deny, so a hit proves an error-marked word was consumed (trap) or dropped (no trap).
- Coverpoints:
  - cp_source = origin of the error mark: bins bus_err{instr_err_i}, pmp{I-side PMP deny}, both{same word carries both}
  - cp_half = which fetch word of the instruction carried the error: bins first{mtval == mepc}, second_plus2{mtval == mepc + 2}, both_words{both words errored; mtval == mepc}
  - cp_ilen = instruction length: bins c16{16-bit}, w32{32-bit}
  - cp_pc_align = pc[1]: bins word{0}, half{1}
  - cp_flow = how the faulting pc was reached: bins sequential, branch_target, jump_target, mret_target, dret_target, popret_target{ret micro-op of cm.popret/cm.popretz}, handler_first{pc == mtvec base}
  - cp_also_illegal = the errored word also decodes as illegal: bins clean{0}, illegal_bits{1}
  - cp_outcome = observed outcome: bins trap{word consumed in ID}, discarded_branch, discarded_jump, discarded_exception, discarded_mret, discarded_irq, discarded_debug, discarded_dret
  - cp_prefetch_depth = error-marked words fetched ahead when the discard happened: bins one{1}, two_three{[2:3]}, four_plus{[4:$]}
- Crosses:
  - cr_source_half = cp_source x cp_half: bins {bus_err_first, bus_err_second_plus2, bus_err_both_words, pmp_first, pmp_second_plus2, pmp_both_words, both_first}
  - cr_half_ilen = cp_half x cp_ilen: bins {first_c16, first_w32, second_plus2_w32, both_words_w32}; ignore second_plus2 x c16, both_words x c16: a 16-bit instruction occupies one fetch word
  - cr_flow_outcome = cp_flow x cp_outcome: bins {sequential_trap, branch_target_trap, jump_target_trap, mret_target_trap, dret_target_trap, popret_target_trap, handler_first_trap, sequential_discarded_branch, sequential_discarded_jump, sequential_discarded_exception, sequential_discarded_mret, sequential_discarded_irq, sequential_discarded_debug, sequential_discarded_dret}
  - cr_illegal_source = cp_also_illegal x cp_source: bins {illegal_bits_bus_err, illegal_bits_pmp, clean_bus_err, clean_pmp}
  - cr_outcome_depth = cp_outcome x cp_prefetch_depth: bins {discarded_branch_one, discarded_branch_two_three, discarded_jump_four_plus, discarded_exception_one, discarded_irq_two_three}
  - cr_flow_align = cp_flow x cp_pc_align: bins {branch_target_half, jump_target_half, sequential_half, popret_target_half}
- Adopted (riscv-dv): none
- TP items: TP-EXC-001, TP-EXC-002, TP-EXC-003, TP-EXC-004, TP-EXC-005, TP-EXC-006, TP-EXC-044, TP-EXC-059, TP-EXC-061, TP-EXC-071, TP-EXC-073

### CG-EXC-003: gen_cg_exc_illegal
- Features: F-EXC-008, F-EXC-009, F-EXC-010, F-EXC-011, F-EXC-012, F-EXC-013, F-EXC-014, F-EXC-015, F-EXC-016
- Sample: (a) a trap record with predicted cause 2, or a cause-5/7 trap record whose next program-order instruction is decode-illegal and was killed (F-EXC-016 outcome b); (b) for cp_kind.trigger_csr_mmode_no_trap only: a retired (rvfi_trap == 0) csrr/csrrw/csrrs/csrrc of tselect/tdata1..3 with rvfi_ext_debug_mode == 0; condition: illegal class identified from rvfi_insn / the program listing; anti-vacuity: only decode- or privilege-rejected instructions give cause 2, so a hit of (a) proves the named illegal class executed and trapped (or was displaced by a WB fault); (b) samples only trigger-CSR accesses outside debug mode, so a hit proves such an access retired without the trap that debug.rst:54-55 describes (doc defect D12).
- Coverpoints:
  - cp_kind = illegal class: bins decoder_reject, csr_nonexistent, csr_ro_write, csr_priv_u{U-mode access to an M CSR}, csr_debug_outside{dcsr/dpc/dscratch0/1 outside debug mode, M-mode}, trigger_csr_mmode_no_trap{tselect/tdata1..3 accessed outside debug mode in M-mode: retires with rvfi_trap == 0 (doc defect D12; sample b)}, mret_umode, wfi_tw_umode, dret_outside_debug, system_rs1rd_nonzero, zcmp_reserved_rlist
  - cp_ilen = instruction length from rvfi_insn[1:0]: bins c16, w32
  - cp_priv = privilege mode of the instruction (rvfi_mode): bins m, u
  - cp_mtval_form = mtval read-back: bins zext16{mtval[31:16]==0, mtval[15:0]==raw halfword}, full32{mtval == 32-bit encoding}
  - cp_wb_state = WB content when the illegal instruction reached ID: bins wb_empty, wb_ls_ok{outstanding load/store completed without error, illegal then taken}, wb_ls_fault{WB fault won; illegal killed}
  - cp_system_sub = encoding class for system_rs1rd_nonzero: bins ecall_enc, ebreak_enc, mret_enc, wfi_enc, dret_enc
- Crosses:
  - cr_kind_ilen = cp_kind x cp_ilen: bins {decoder_reject_c16, decoder_reject_w32, csr_nonexistent_w32, csr_ro_write_w32, csr_priv_u_w32, csr_debug_outside_w32, mret_umode_w32, wfi_tw_umode_w32, dret_outside_debug_w32, system_rs1rd_nonzero_w32, zcmp_reserved_rlist_c16}; ignore csr_*/mret_umode/wfi_tw_umode/dret_outside_debug/system_rs1rd_nonzero x c16: 32-bit-only encodings; ignore zcmp_reserved_rlist x w32: Zcmp is 16-bit
  - cr_kind_priv = cp_kind x cp_priv: bins {decoder_reject_m, decoder_reject_u, csr_nonexistent_m, csr_nonexistent_u, csr_ro_write_m, csr_ro_write_u, csr_priv_u_u, csr_debug_outside_m, mret_umode_u, wfi_tw_umode_u, dret_outside_debug_m, dret_outside_debug_u, system_rs1rd_nonzero_m, system_rs1rd_nonzero_u, zcmp_reserved_rlist_m, zcmp_reserved_rlist_u}; ignore csr_priv_u x m, mret_umode x m, wfi_tw_umode x m: U-mode-only causes; ignore csr_debug_outside x u: classified as csr_priv_u first
  - cr_kind_wb = cp_kind x cp_wb_state: bins {decoder_reject_wb_empty, decoder_reject_wb_ls_ok, decoder_reject_wb_ls_fault, csr_nonexistent_wb_ls_ok, csr_nonexistent_wb_ls_fault, system_rs1rd_nonzero_wb_ls_ok, zcmp_reserved_rlist_wb_ls_ok}
  - cr_kind_mtval = cp_kind x cp_mtval_form: bins {decoder_reject_zext16, decoder_reject_full32, zcmp_reserved_rlist_zext16, csr_nonexistent_full32, mret_umode_full32, wfi_tw_umode_full32, dret_outside_debug_full32}
  - cr_sub_priv = cp_system_sub x cp_priv: bins {ecall_enc_m, ecall_enc_u, ebreak_enc_m, ebreak_enc_u, mret_enc_m, wfi_enc_m, wfi_enc_u, dret_enc_m}
- Adopted (riscv-dv): none
- TP items: TP-EXC-007, TP-EXC-008, TP-EXC-009, TP-EXC-010, TP-EXC-011, TP-EXC-012, TP-EXC-013, TP-EXC-014, TP-EXC-015, TP-EXC-071

### CG-EXC-004: gen_cg_exc_ebreak
- Features: F-EXC-017, F-EXC-018, F-EXC-019, F-EXC-020, F-EXC-021, F-EXC-022
- Sample: retirement or trap record of EBREAK (rvfi_insn == 32'h00100073 after c.ebreak expansion), each debug-entry event reported by gen_chk_debug with dcsr.cause in {EBREAK, TRIGGER}, and each configured trigger address reached in IF (tdata2 match candidate from the program listing); condition: one of those events; anti-vacuity: samples only when an ebreak/c.ebreak retired or trapped or a tdata2 address was fetched, so a hit proves the routing decision was exercised.
- Coverpoints:
  - cp_form = encoding form (rvfi_insn before expansion): bins ebreak32, c_ebreak16
  - cp_priv = privilege mode of the instruction (rvfi_mode): bins m, u
  - cp_dcsr_ebreak = {dcsr.ebreakm, dcsr.ebreaku} from the CSR model: bins m0u0, m1u0, m0u1, m1u1
  - cp_outcome = observed outcome: bins exception{cause 3, rvfi_trap}, debug_entry{DmHaltAddr, dcsr.cause = DBG_CAUSE_EBREAK, no rvfi_trap}, debug_reentry{already in debug mode: DmHaltAddr, dcsr/dpc unchanged}
  - cp_trigger = trigger match handling: bins trigger_entry{dcsr.cause = DBG_CAUSE_TRIGGER, no cause-3 trap}, trigger_squashed{tdata2 word discarded by a redirect from ID; no debug entry}, trigger_on_ebreak_addr{tdata2 == address of an ebreak: trigger entry, no breakpoint exception}
  - cp_mepc_align = pc[1] of the ebreak: bins word{0}, half{1}
- Crosses:
  - cr_priv_dcsr_outcome = cp_priv x cp_dcsr_ebreak x cp_outcome: bins {m_m0u0_exception, m_m0u1_exception, m_m1u0_debug_entry, m_m1u1_debug_entry, u_m0u0_exception, u_m1u0_exception, u_m0u1_debug_entry, u_m1u1_debug_entry}; ignore every other priv x dcsr x outcome combination: the outcome is a function of priv and the matching dcsr bit; a mismatch is a gen_chk_debug/gen_isa_compare failure, not a bin
  - cr_form_outcome = cp_form x cp_outcome: bins {ebreak32_exception, ebreak32_debug_entry, ebreak32_debug_reentry, c_ebreak16_exception, c_ebreak16_debug_entry, c_ebreak16_debug_reentry}
  - cr_form_align = cp_form x cp_mepc_align: bins {c_ebreak16_half, c_ebreak16_word, ebreak32_half, ebreak32_word}
  - cr_trigger_priv = cp_trigger x cp_priv: bins {trigger_entry_m, trigger_entry_u, trigger_squashed_m, trigger_squashed_u, trigger_on_ebreak_addr_m}
- Adopted (riscv-dv): none
- TP items: TP-EXC-016, TP-EXC-017, TP-EXC-018, TP-EXC-019, TP-EXC-020, TP-EXC-021, TP-EXC-064

### CG-EXC-005: gen_cg_exc_ecall
- Features: F-EXC-023, F-EXC-024, F-EXC-058, F-EXC-065
- Sample: a trap record with predicted cause 8 or 11; condition: rvfi_insn == 32'h00000073 && rvfi_trap; anti-vacuity: only ECALL gives causes 8/11, so a hit proves an ECALL trapped from the recorded privilege.
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{3 -> cause 11}, u{0 -> cause 8}
  - cp_mtval_pre = mtval value before the ECALL (CSR model): bins was_zero, was_nonzero
  - cp_pc_align = pc[1]: bins word{0}, half{1}
  - cp_seen_pre = cpuctrlsts.sync_exc_seen before the ECALL: bins seen0{0}, seen1{1}
  - cp_mie_pre = mstatus.MIE before: bins mie0, mie1
- Crosses:
  - cr_priv_mtval = cp_priv x cp_mtval_pre: bins {m_was_zero, m_was_nonzero, u_was_zero, u_was_nonzero}
  - cr_priv_seen = cp_priv x cp_seen_pre: bins {m_seen0, m_seen1, u_seen0, u_seen1}
  - cr_priv_align = cp_priv x cp_pc_align: bins {m_word, m_half, u_word, u_half}
  - cr_priv_mie = cp_priv x cp_mie_pre: bins {m_mie0, m_mie1, u_mie0, u_mie1}
- Adopted (riscv-dv): none
- TP items: TP-EXC-022, TP-EXC-023, TP-EXC-058, TP-EXC-066

### CG-EXC-006: gen_cg_exc_lsu_fault
- Features: F-EXC-025, F-EXC-026, F-EXC-027, F-EXC-028, F-EXC-029, F-EXC-030, F-EXC-031, F-EXC-032, F-EXC-033, F-EXC-034, F-EXC-035, F-EXC-036, F-EXC-037, F-EXC-038, F-EXC-039, F-EXC-040, F-EXC-069
- Sample: (a) a trap record with predicted cause 5 or 7, correlated with the dbus monitor transactions of that instruction (request pattern, error response cycle, gnt-to-rvalid latency) and the irq monitor state at the error cycle; (b) for cp_mis_no_trap only: a retired misaligned access (two dbus requests for one rvfi_mem_* record) with rvfi_trap == 0; condition: (a) rvfi_trap && cause in {5,7}, (b) split access retired; anti-vacuity: only injected data_err_i responses or PMP-denied data accesses give cause 5/7, so a hit of (a) proves such a fault was taken with the recorded pipeline context; (b) samples only split accesses, so a hit proves a misaligned access completed without a cause-4/6 trap.
- Coverpoints:
  - cp_op = access kind (rvfi_mem_rmask vs rvfi_mem_wmask): bins load, store
  - cp_source = fault origin (dbus error response vs gen_chk_pmp deny): bins bus_err{data_err_i response}, pmp{D-side PMP deny; no bus request for that half}
  - cp_align = which part of the access faulted: bins aligned{single word}, mis_first{misaligned, first half faults}, mis_second{misaligned, second half faults}, mis_both{both halves fault}
  - cp_size = access size from the RVFI mask: bins byte, half, word
  - cp_zcmp = the faulting access is a Zcmp micro-op: bins none, cm_push_op, cm_pop_op{cm.pop/cm.popret/cm.popretz}
  - cp_op_pos = micro-op index within the Zcmp sequence (Zcmp only): bins first, middle, last
  - cp_younger = the instruction in ID when the fault response arrived (next program-order instruction after the faulting one that did not retire before the trap): bins none{ID empty}, alu, branch, jump, load_store, csr_rw, illegal, ecall_ebreak, wfi, mret, fetch_errored
  - cp_spec_fetch = instr_addr_o hit the younger branch/jump target before the vector (ibus monitor): bins yes, no
  - cp_mtval_class = mtval read-back: bins eq_addr{unaligned effective address}, eq_second_word{(addr & ~3) + 4}
  - cp_resp_latency = gnt-to-rvalid cycles of the erroring response: bins one{1}, short{[2:4]}, long{[5:$]}
  - cp_irq_pending = irq state at the error response cycle: bins none, pending{irq_pending_o && (MIE || U-mode)}, nmi{irq_nm_i}
  - cp_bus_pattern = requests seen on the data bus for the access: bins single_req{aligned, one request}, two_reqs{misaligned, both halves requested}, first_only{second half suppressed by PMP}, second_only{first half blocked by PMP, second issued}, none{no request at all}
  - cp_mis_no_trap = misaligned access retired without trap (sample b): bins half_cross{halfword at addr%4 == 3}, word_off1{word at addr%4 == 1}, word_off2{addr%4 == 2}, word_off3{addr%4 == 3}
- Crosses:
  - cr_op_source_align = cp_op x cp_source x cp_align: bins {load_bus_err_aligned, load_bus_err_mis_first, load_bus_err_mis_second, load_bus_err_mis_both, load_pmp_aligned, load_pmp_mis_first, load_pmp_mis_second, load_pmp_mis_both, store_bus_err_aligned, store_bus_err_mis_first, store_bus_err_mis_second, store_bus_err_mis_both, store_pmp_aligned, store_pmp_mis_first, store_pmp_mis_second, store_pmp_mis_both}
  - cr_align_size = cp_align x cp_size: bins {aligned_byte, aligned_half, aligned_word, mis_first_half, mis_first_word, mis_second_half, mis_second_word, mis_both_half, mis_both_word}; ignore byte x mis_*: byte accesses never split
  - cr_align_mtval = cp_align x cp_mtval_class: bins {aligned_eq_addr, mis_first_eq_addr, mis_second_eq_second_word, mis_both_eq_addr}; ignore aligned/mis_first/mis_both x eq_second_word: the RTL reports the first faulting half; a mismatch is a gen_chk_csr_readback failure
  - cr_op_younger = cp_op x cp_younger: bins {load_none, load_alu, load_branch, load_jump, load_load_store, load_csr_rw, load_illegal, load_ecall_ebreak, load_wfi, load_mret, load_fetch_errored, store_none, store_alu, store_branch, store_jump, store_load_store, store_csr_rw, store_illegal, store_ecall_ebreak, store_wfi, store_mret, store_fetch_errored}
  - cr_op_zcmp = cp_op x cp_zcmp x cp_op_pos: bins {store_cm_push_op_first, store_cm_push_op_middle, store_cm_push_op_last, load_cm_pop_op_first, load_cm_pop_op_middle, load_cm_pop_op_last}; ignore load x cm_push_op, store x cm_pop_op: push sequences contain only stores, pop sequences only loads
  - cr_younger_spec = cp_younger x cp_spec_fetch: bins {branch_yes, branch_no, jump_yes, jump_no}
  - cr_source_pattern = cp_source x cp_align x cp_bus_pattern: bins {bus_err_aligned_single_req, bus_err_mis_first_two_reqs, bus_err_mis_second_two_reqs, bus_err_mis_both_two_reqs, pmp_aligned_none, pmp_mis_first_second_only, pmp_mis_second_first_only, pmp_mis_both_none}; ignore pmp x aligned x single_req: a denied aligned access issues nothing
  - cr_latency_irq = cp_resp_latency x cp_irq_pending: bins {one_none, one_pending, short_pending, long_pending, long_nmi, short_nmi}
  - cr_op_size_source = cp_op x cp_size x cp_source: bins {load_byte_bus_err, load_half_bus_err, load_word_bus_err, load_byte_pmp, load_word_pmp, store_byte_bus_err, store_half_bus_err, store_word_bus_err, store_half_pmp, store_word_pmp}
- Adopted (riscv-dv): none
- TP items: TP-EXC-024, TP-EXC-025, TP-EXC-026, TP-EXC-027, TP-EXC-028, TP-EXC-029, TP-EXC-030, TP-EXC-031, TP-EXC-032, TP-EXC-033, TP-EXC-034, TP-EXC-035, TP-EXC-036, TP-EXC-037, TP-EXC-038, TP-EXC-039, TP-EXC-042, TP-EXC-043, TP-EXC-070, TP-EXC-071, TP-EXC-073, TP-IRQ-058, TP-IRQ-072

### CG-EXC-007: gen_cg_exc_priority
- Features: F-EXC-007, F-EXC-013, F-EXC-016, F-EXC-036, F-EXC-041, F-EXC-069, F-IRQ-021, F-IRQ-022
- Sample: a cycle in which two or more exception conditions are present at once, built from the dbus monitor (data_rvalid_i & data_err_i response cycle -> WB fault), the ibus monitor (error-marked word in ID), the program listing (decode-illegal / rs1-rd-nonzero SYSTEM / ECALL / EBREAK encoding of the instruction in ID) and the irq monitor; condition: popcount(present causes) >= 2; anti-vacuity: the vast majority of traps have exactly one cause, so a hit proves two conditions coexisted in one cycle and the winner was compared.
- Coverpoints:
  - cp_pair = the pair present: bins st_fetch, st_illegal, st_ecall, st_ebreak, ld_fetch, ld_illegal, ld_ecall, ld_ebreak, fetch_illegal, fetch_ecall, fetch_ebreak, illegal_ecall, illegal_ebreak, triple_wb_fetch_illegal; ignore_bins ld_st: only one instruction is in WB; ignore_bins ecall_ebreak: mutually exclusive encodings
  - cp_winner = predicted cause taken: bins store_fault, load_fault, fetch_fault, illegal; ignore_bins ecall_ebreak_win{8,11,3}: never the winner of a collision
  - cp_irq_also = interrupt state in the same cycle: bins none, irq_enabled, nmi
  - cp_illegal_kind = for pairs involving illegal: bins decoder, csr_check, system_rs1rd
- Crosses:
  - cr_pair_winner = cp_pair x cp_winner: bins {st_fetch_store_fault, st_illegal_store_fault, st_ecall_store_fault, st_ebreak_store_fault, ld_fetch_load_fault, ld_illegal_load_fault, ld_ecall_load_fault, ld_ebreak_load_fault, fetch_illegal_fetch_fault, fetch_ecall_fetch_fault, fetch_ebreak_fetch_fault, illegal_ecall_illegal, illegal_ebreak_illegal, triple_wb_fetch_illegal_store_fault, triple_wb_fetch_illegal_load_fault}; ignore all other pair x winner combinations: the winner is fixed by the RTL order; a mismatch is a gen_isa_compare failure
  - cr_pair_irq = cp_pair x cp_irq_also: bins {st_illegal_irq_enabled, ld_illegal_irq_enabled, ld_fetch_irq_enabled, fetch_illegal_irq_enabled, illegal_ecall_irq_enabled, st_fetch_nmi, ld_illegal_nmi, st_illegal_none, ld_fetch_none}
  - cr_pair_kind = cp_pair x cp_illegal_kind: bins {st_illegal_decoder, st_illegal_csr_check, ld_illegal_decoder, ld_illegal_csr_check, fetch_illegal_decoder, illegal_ecall_system_rs1rd, illegal_ebreak_system_rs1rd}
- Adopted (riscv-dv): none
- TP items: TP-EXC-006, TP-EXC-012, TP-EXC-015, TP-EXC-035, TP-EXC-040, TP-EXC-065, TP-EXC-072, TP-IRQ-026

### CG-EXC-008: gen_cg_exc_zcmp
- Features: F-EXC-015, F-EXC-043, F-EXC-044, F-EXC-045, F-IRQ-020
- Sample: a trap record or interrupt entry whose faulting/interrupted instruction is a Zcmp cm.* (rvfi_ext_expanded_insn_valid seen for that pc, or rvfi_insn is a cm.* encoding), and the Zcmp reserved-rlist illegal trap; condition: cm.* pc identified; anti-vacuity: only cm.push/cm.pop* instructions sample, so a hit proves a sequence was hit by a fault or an interrupt at the recorded micro-op.
- Coverpoints:
  - cp_seq = Zcmp form (encoding): bins cm_push, cm_pop, cm_popret, cm_popretz
  - cp_event = event kind: bins store_fault, load_fault, fetch_fault_ret_target{fetch fault at the popret return address, attributed to the target}, irq_during_expanded{interrupt while INSTR_EXPANDED micro-ops run: mepc = cm.* pc}, irq_during_commit_deferred{interrupt during INSTR_EXPANDED_COMMIT: taken after LAST}, reserved_rlist_illegal
  - cp_op_pos = micro-op index at the event: bins first, middle, last
  - cp_rlist = rlist field: bins r4{4}, r5_7{[5:7]}, r8_11{[8:11]}, r12_15{[12:15]}
  - cp_after_mret = behaviour after the handler's mret (RVFI): bins reexecuted_from_first{sequence re-runs from micro-op 0}, handler_advanced_mepc{handler skipped the cm.*}
- Crosses:
  - cr_seq_event = cp_seq x cp_event: bins {cm_push_store_fault, cm_push_irq_during_expanded, cm_push_irq_during_commit_deferred, cm_push_reserved_rlist_illegal, cm_pop_load_fault, cm_pop_irq_during_expanded, cm_pop_irq_during_commit_deferred, cm_pop_reserved_rlist_illegal, cm_popret_load_fault, cm_popret_fetch_fault_ret_target, cm_popret_irq_during_expanded, cm_popret_irq_during_commit_deferred, cm_popret_reserved_rlist_illegal, cm_popretz_load_fault, cm_popretz_fetch_fault_ret_target, cm_popretz_irq_during_expanded, cm_popretz_irq_during_commit_deferred, cm_popretz_reserved_rlist_illegal}; ignore cm_push x load_fault, cm_pop* x store_fault: one access kind per sequence; ignore cm_push/cm_pop x fetch_fault_ret_target: no return micro-op
  - cr_event_pos = cp_event x cp_op_pos: bins {store_fault_first, store_fault_middle, store_fault_last, load_fault_first, load_fault_middle, load_fault_last, irq_during_expanded_first, irq_during_expanded_middle, irq_during_expanded_last}
  - cr_event_rlist = cp_event x cp_rlist: bins {store_fault_r4, store_fault_r12_15, load_fault_r4, load_fault_r12_15, irq_during_expanded_r5_7, irq_during_expanded_r8_11, irq_during_commit_deferred_r12_15}
  - cr_event_after = cp_event x cp_after_mret: bins {store_fault_reexecuted_from_first, load_fault_reexecuted_from_first, irq_during_expanded_reexecuted_from_first, store_fault_handler_advanced_mepc, load_fault_handler_advanced_mepc}
- Adopted (riscv-dv): none
- TP items: TP-EXC-014, TP-EXC-042, TP-EXC-043, TP-EXC-044, TP-EXC-074, TP-IRQ-025, TP-IRQ-076

### CG-EXC-009: gen_cg_exc_debug_mode
- Features: F-EXC-020, F-EXC-046, F-EXC-047, F-EXC-048, F-IRQ-039
- Sample: an exception condition (any cause) while rvfi_ext_debug_mode == 1, or an exception commit in the same cycle as debug_req_i (debug pin monitor) or with dcsr.step == 1 (CSR model); condition: exception event with one of those contexts; anti-vacuity: exceptions outside debug mode without a concurrent debug request do not sample, so a hit proves the debug interplay case occurred.
- Coverpoints:
  - cp_cause = exception cause (predicted): bins fetch_fault, illegal, load_fault, store_fault, ecall, ebreak
  - cp_context = debug context at the event: bins in_debug, not_debug_req_same_cycle, not_debug_step
  - cp_dcsr_prv = dcsr.prv at the event (in_debug): bins m, u
  - cp_seen_pre = cpuctrlsts.sync_exc_seen before: bins seen0, seen1
  - cp_target = first fetch address after the event (ibus monitor): bins dm_exception_addr, dm_halt_addr, mtvec_base
- Crosses:
  - cr_cause_context = cp_cause x cp_context: bins {fetch_fault_in_debug, illegal_in_debug, load_fault_in_debug, store_fault_in_debug, ecall_in_debug, ebreak_in_debug, fetch_fault_not_debug_req_same_cycle, illegal_not_debug_req_same_cycle, load_fault_not_debug_req_same_cycle, store_fault_not_debug_req_same_cycle, ecall_not_debug_req_same_cycle, illegal_not_debug_step, ecall_not_debug_step, load_fault_not_debug_step}
  - cr_context_target = cp_context x cp_target: bins {in_debug_dm_exception_addr, in_debug_dm_halt_addr, not_debug_req_same_cycle_dm_halt_addr, not_debug_step_dm_halt_addr}; ignore in_debug x mtvec_base: the handler is never fetched in debug mode (checker failure)
  - cr_cause_prv = cp_cause x cp_dcsr_prv: bins {illegal_u, ecall_u, load_fault_u, store_fault_u, fetch_fault_u, illegal_m, ecall_m, load_fault_m}
  - cr_context_seen = cp_context x cp_seen_pre: bins {in_debug_seen1, in_debug_seen0, not_debug_req_same_cycle_seen1}
- Adopted (riscv-dv): none
- TP items: TP-EXC-019, TP-EXC-045, TP-EXC-046, TP-EXC-047, TP-EXC-048, TP-IRQ-043

### CG-EXC-010: gen_cg_exc_double_fault
- Features: F-EXC-047, F-EXC-054, F-EXC-055, F-EXC-056, F-EXC-057, F-EXC-058, F-EXC-059
- Sample: every event that moves the gen_chk_double_fault model: trap entries (sync/irq/nmi), retired mret, retired csrw/csrs/csrc cpuctrlsts, and each double_fault_seen_o pulse; condition: model event or output pulse; anti-vacuity: idle cycles never sample, so a hit proves an arming, clearing or pulse event happened and was compared against the model.
- Coverpoints:
  - cp_event = event kind: bins sync_arm{sync exception with seen 0 -> 1}, sync_double{sync exception with seen = 1: pulse}, irq_seen1{interrupt entry with seen = 1: no pulse, no clear}, nmi_seen1, mret_exc_handler{clears}, mret_irq_in_exc{mret of an interrupt handler nested inside an exception handler: clears (B12)}, mret_nmi_handler{clears}, sw_clear_seen, sw_set_seen, sw_clear_double, sw_set_double_no_pulse, exc_in_debug_seen1{no arm, no pulse}, storm_3plus{>= 3 consecutive vector re-entries}
  - cp_first_cause = cause that armed: bins fetch_fault, illegal, breakpoint, load_fault, store_fault, ecall
  - cp_second_cause = cause of the double: bins fetch_fault, illegal, breakpoint, load_fault, store_fault, ecall
  - cp_readback = cpuctrlsts read-back class: bins pulse_then_read1{cpuctrlsts.double_fault_seen reads 1 after a pulse}, sw_cleared_then_read0, seen_read1_in_handler, seen_read0_after_mret
  - cp_gap = instructions retired between the arming trap and the double: bins zero{0}, few{[1:8]}, many{[9:$]}
- Crosses:
  - cr_first_second = cp_first_cause x cp_second_cause: bins {fetch_fault_fetch_fault, fetch_fault_illegal, fetch_fault_load_fault, illegal_illegal, illegal_ecall, illegal_load_fault, illegal_store_fault, illegal_breakpoint, breakpoint_illegal, breakpoint_breakpoint, load_fault_illegal, load_fault_load_fault, load_fault_ecall, store_fault_store_fault, store_fault_ecall, ecall_illegal, ecall_ecall, ecall_load_fault, ecall_store_fault, ecall_fetch_fault}
  - cr_event_gap = cp_event x cp_gap: bins {sync_double_zero, sync_double_few, sync_double_many, irq_seen1_few, storm_3plus_zero}
  - cr_event_readback = cp_event x cp_readback: bins {sync_double_pulse_then_read1, sw_clear_double_sw_cleared_then_read0, sync_arm_seen_read1_in_handler, mret_exc_handler_seen_read0_after_mret}
- Adopted (riscv-dv): none
- TP items: TP-EXC-047, TP-EXC-054, TP-EXC-055, TP-EXC-056, TP-EXC-057, TP-EXC-058, TP-EXC-059, TP-EXC-072

### CG-EXC-011: gen_cg_exc_mret
- Features: F-EXC-010, F-EXC-050, F-EXC-051, F-EXC-052, F-EXC-053, F-EXC-061, F-IRQ-023, F-IRQ-027, F-IRQ-029
- Sample: retirement of MRET (rvfi_insn == 32'h30200073) or its illegal-instruction trap record, with the CSR model state before the mret and the irq monitor state at the retirement cycle; condition: mret in rvfi_insn; anti-vacuity: only mret instructions sample, so a hit proves a return (or a U-mode attempt) happened with the recorded stack state.
- Coverpoints:
  - cp_priv_at = privilege at the mret (rvfi_mode): bins m, u
  - cp_mpp = mstatus.MPP class before the mret (CSR model incl. the last software write): bins m{11}, u{00}, sw01_read_u{last write 01, reads 00}, sw10_read_u{last write 10, reads 00}
  - cp_mpie = mstatus.MPIE before the mret (CSR model): bins mpie0, mpie1
  - cp_mprv = mstatus.MPRV before the mret (CSR model): bins mprv0, mprv1
  - cp_mepc_bits = mepc low bits (read-back): bins bit1_0{mepc[1] == 0}, bit1_1{mepc[1] == 1}, sw_bit0_dropped{software wrote mepc with bit 0 set; reads 0}
  - cp_context = what the mret returns from: bins exc_handler, irq_handler, nmi_handler, plain{not inside any trap handler}
  - cp_pending_at = irq state at the mret retirement: bins none, irq_enabled{mie set, taken with restored MIE or U-mode}, irq_disabled{mie set, MPIE = 0, returning to M}, nmi
  - cp_prefetch_discarded = fall-through words fetched after the mret and never retired: bins zero{0}, one_plus{[1:$]}
- Crosses:
  - cr_mpp_mprv = cp_mpp x cp_mprv (M-mode mrets): bins {m_mprv1, u_mprv1, m_mprv0, u_mprv0, sw01_read_u_mprv1, sw10_read_u_mprv1}
  - cr_context_pending = cp_context x cp_pending_at: bins {exc_handler_none, exc_handler_irq_enabled, exc_handler_irq_disabled, exc_handler_nmi, irq_handler_none, irq_handler_irq_enabled, irq_handler_irq_disabled, irq_handler_nmi, nmi_handler_none, nmi_handler_irq_enabled, nmi_handler_nmi, plain_irq_enabled, plain_none}
  - cr_mpp_pending = cp_mpp x cp_pending_at: bins {u_irq_enabled, u_irq_disabled, m_irq_enabled, m_irq_disabled, u_nmi, m_nmi}
  - cr_mpie_pending = cp_mpie x cp_pending_at: bins {mpie0_irq_enabled, mpie1_irq_enabled, mpie0_irq_disabled}
  - cr_priv_mpp = cp_priv_at x cp_mpp: bins {m_m, m_u, m_sw01_read_u, m_sw10_read_u, u_m, u_u}
  - cr_context_prefetch = cp_context x cp_prefetch_discarded: bins {exc_handler_one_plus, irq_handler_one_plus, plain_one_plus, nmi_handler_zero}
  - cr_bits_context = cp_mepc_bits x cp_context: bins {bit1_1_exc_handler, bit1_1_irq_handler, bit1_0_exc_handler, sw_bit0_dropped_plain}
- Adopted (riscv-dv): none
- TP items: TP-EXC-009, TP-EXC-050, TP-EXC-051, TP-EXC-052, TP-EXC-053, TP-EXC-061, TP-IRQ-028, TP-IRQ-032, TP-IRQ-034, TP-IRQ-035, TP-IRQ-036, TP-IRQ-037

### CG-EXC-012: gen_cg_exc_trap_csrs
- Features: F-EXC-001, F-EXC-042, F-EXC-049, F-EXC-063, F-EXC-065, F-EXC-066
- Sample: completion of the handler read-back set for one trap (gen_chk_csr_readback matches the retired csrr mepc/mcause/mtval/mstatus to the trap), with crash_dump_o and the minstret read-back sampled at that point; condition: read-back set complete; anti-vacuity: samples once per trap whose handler reads the CSRs, so a hit proves the written values were observed and compared.
- Coverpoints:
  - cp_kind = trap kind (sync exception / interrupt / NMI): bins sync, irq, nmi_ext, nmi_int
  - cp_old_mie = mstatus.MIE before the trap: bins mie0, mie1
  - cp_old_priv = privilege before the trap (CSR model): bins m, u
  - cp_mtval_class = mtval read-back: bins zero, pc, pc_plus2, insn32, insn16, data_addr, data_addr_second
  - cp_mepc_bit1 = mepc[1] read-back: bins bit1_0, bit1_1
  - cp_kept = pre-trap fields that must survive the entry: bins mprv1_kept, tw1_kept, both_zero
  - cp_crash_dump = crash_dump_o fields vs read-back: bins exc_pc_match{crash_dump_o.exception_pc == mepc}, exc_addr_match{exception_addr == mtval}, both_match
  - cp_minstret = minstret read-back delta class: bins unchanged_by_trapper{delta across the trapping instruction == 0}, counted_handler{handler instructions counted}
- Crosses:
  - cr_kind_mtval = cp_kind x cp_mtval_class: bins {sync_zero, sync_pc, sync_pc_plus2, sync_insn32, sync_insn16, sync_data_addr, sync_data_addr_second, irq_zero, nmi_ext_zero, nmi_int_data_addr}; ignore irq/nmi_ext x non-zero and nmi_int x non-data_addr: the RTL writes 0 / the captured address; a mismatch is a checker failure
  - cr_kind_mie_priv = cp_kind x cp_old_mie x cp_old_priv: bins {sync_mie0_m, sync_mie1_m, sync_mie0_u, sync_mie1_u, irq_mie1_m, irq_mie0_u, irq_mie1_u, nmi_ext_mie0_m, nmi_ext_mie1_m, nmi_ext_mie0_u, nmi_ext_mie1_u, nmi_int_mie0_m, nmi_int_mie1_m, nmi_int_mie1_u}; ignore irq x mie0 x m: not taken
  - cr_kind_kept = cp_kind x cp_kept: bins {sync_mprv1_kept, sync_tw1_kept, irq_mprv1_kept, irq_tw1_kept, nmi_ext_mprv1_kept, sync_both_zero}
  - cr_kind_bit1 = cp_kind x cp_mepc_bit1: bins {sync_bit1_1, irq_bit1_1, nmi_ext_bit1_1, sync_bit1_0}
  - cr_kind_crash = cp_kind x cp_crash_dump: bins {sync_both_match, irq_both_match, nmi_int_both_match}
- Adopted (riscv-dv): none
- TP items: TP-EXC-001, TP-EXC-003, TP-EXC-013, TP-EXC-022, TP-EXC-023, TP-EXC-024, TP-EXC-030, TP-EXC-041, TP-EXC-049, TP-EXC-063, TP-EXC-066, TP-EXC-067, TP-IRQ-001, TP-IRQ-007, TP-IRQ-013, TP-IRQ-044

### CG-EXC-013: gen_cg_exc_timing
- Features: F-EXC-016, F-EXC-035, F-EXC-060, F-EXC-062, F-EXC-069, F-IRQ-021, F-IRQ-022
- Sample: an exception commit (ibus monitor: instr_req_o to mtvec base or DmExceptionAddr immediately following a trap record), with the cycle bookkeeping of the dbus/ibus monitors and the irq monitor at the trigger cycle; condition: commit detected; anti-vacuity: only exception commits sample, so a hit proves a trap was committed with the recorded latency and bus/irq context.
- Coverpoints:
  - cp_exc_stage = stage raising the exception: bins id_cause{fetch fault / illegal / ecall / ebreak}, wb_cause{load / store fault}
  - cp_latency = cycles from the trigger (ID: the instruction's arrival in ID; WB: the error response cycle) to instr_req_o at the vector: bins min{1}, two{2}, three_five{[3:5]}, long{[6:$]}
  - cp_wb_at_id_exc = WB content when an ID exception was requested: bins wb_empty, wb_ls_ok, wb_ls_fault_wins
  - cp_irq_at_commit = interrupt state at the commit cycle (irq monitor): bins none, irq_enabled, nmi
  - cp_ibus_at_commit = instruction-bus state at the trigger cycle: bins idle, gnt_pending, rvalid_pending
  - cp_dbus_at_commit = data-bus state at the trigger cycle (dbus monitor): bins idle, gnt_pending, rvalid_pending
  - cp_killed_younger = younger instruction killed by the flush (RVFI vs ibus monitor): bins none, one
- Crosses:
  - cr_stage_latency = cp_exc_stage x cp_latency: bins {id_cause_min, id_cause_two, id_cause_three_five, id_cause_long, wb_cause_min}; ignore wb_cause x non-min: a WB fault commits on the next cycle (gen_chk_trap_timing bound)
  - cr_wb_irq_ibus = cp_wb_at_id_exc x cp_irq_at_commit x cp_ibus_at_commit: bins {wb_ls_fault_wins_irq_enabled_rvalid_pending, wb_ls_fault_wins_irq_enabled_gnt_pending, wb_ls_fault_wins_irq_enabled_idle, wb_ls_ok_irq_enabled_rvalid_pending, wb_empty_irq_enabled_idle, wb_ls_fault_wins_nmi_rvalid_pending, wb_ls_fault_wins_none_rvalid_pending, wb_ls_ok_none_idle}
  - cr_stage_irq = cp_exc_stage x cp_irq_at_commit: bins {id_cause_irq_enabled, wb_cause_irq_enabled, id_cause_nmi, wb_cause_nmi, id_cause_none, wb_cause_none}
  - cr_stage_dbus = cp_exc_stage x cp_dbus_at_commit: bins {id_cause_idle, id_cause_rvalid_pending, id_cause_gnt_pending, wb_cause_idle}
  - cr_stage_killed = cp_exc_stage x cp_killed_younger: bins {wb_cause_one, wb_cause_none, id_cause_none}
- Adopted (riscv-dv): none
- TP items: TP-EXC-015, TP-EXC-034, TP-EXC-060, TP-EXC-062, TP-EXC-070, TP-EXC-071, TP-EXC-072, TP-IRQ-026, TP-IRQ-027, TP-IRQ-039, TP-IRQ-072

## Covergroups: IRQ

### CG-IRQ-001: gen_cg_irq_entry
- Features: F-IRQ-001, F-IRQ-002, F-IRQ-007, F-IRQ-008, F-IRQ-016, F-IRQ-024, F-IRQ-029, F-IRQ-053, F-IRQ-057, F-IRQ-058
- Sample: interrupt entry: rvfi_valid && rvfi_intr on the first handler instruction (or an rvfi_ext_irq_valid pulse followed by the handler pc), with the cause from the handler csrr mcause read-back / gen_chk_irq model and the CSR model state before the entry; condition: rvfi_intr or rvfi_ext_irq_valid; anti-vacuity: rvfi_intr is 0 on every instruction that is not the first of an interrupt handler (exception handlers do not set it), so a hit proves an interrupt entry.
- Coverpoints:
  - cp_line = cause of the entry: bins software{3}, timer{7}, external{11}, fast[15]{[16:30], id = CSR_MFIX_BIT_LOW + index, count = $bits(irqs_t.irq_fast)}, nmi_ext{31}, nmi_int{0xFFFFFFE0}
  - cp_priv_pre = privilege before the entry (rvfi_mode of the last retired instruction / CSR model): bins m, u
  - cp_mie_global = mstatus.MIE before the entry: bins mie0, mie1
  - cp_others = state of the other mie-enabled lines at the entry: bins only_this, others_enabled_idle, others_pending_lower{a lower-priority line also pending}
  - cp_mepc_src = what mepc points at: bins sequential{next sequential pc}, branch_target, jump_target, mret_target, dret_target, wfi_next{wfi + 4}, boot_pc{reset-time NMI}, cm_pc{restart pc of an interrupted Zcmp sequence}
  - cp_u_path = how U-mode was reached (U entries only): bins mret_mpp_u, dret_prv_u
  - cp_u_pending_at_return = for U entries: bins already_pending{line pending at the mret/dret}, arrived_later
  - cp_rvfi_marks = RVFI interrupt markers: bins intr_with_pre_mip{rvfi_intr with rvfi_ext_pre_mip != 0}, irq_valid_pulse{rvfi_ext_irq_valid seen}, pre_post_mip_equal, pre_post_mip_differ, nmi_flag{rvfi_ext_nmi}, nmi_int_flag{rvfi_ext_nmi_int}, exc_handler_first_intr0{first instruction of an exception handler has rvfi_intr == 0}
- Crosses:
  - cr_line_priv_mie = cp_line x cp_priv_pre x cp_mie_global: bins {software_m_mie1, software_u_mie0, software_u_mie1, timer_m_mie1, timer_u_mie0, timer_u_mie1, external_m_mie1, external_u_mie0, external_u_mie1, fast_0_m_mie1, fast_0_u_mie0, fast_7_u_mie1, fast_14_m_mie1, fast_14_u_mie0, nmi_ext_m_mie0, nmi_ext_m_mie1, nmi_ext_u_mie0, nmi_ext_u_mie1, nmi_int_m_mie0, nmi_int_m_mie1, nmi_int_u_mie0}; ignore {software, timer, external, fast_*} x m x mie0: not taken in M-mode with MIE clear
  - cr_line_mepc = cp_line x cp_mepc_src: bins {software_sequential, timer_branch_target, external_jump_target, fast_3_mret_target, fast_9_dret_target, external_wfi_next, nmi_ext_boot_pc, fast_0_cm_pc, nmi_ext_wfi_next, nmi_int_sequential, software_mret_target, timer_dret_target, fast_14_sequential, external_branch_target}
  - cr_upath_pending = cp_u_path x cp_u_pending_at_return x cp_mie_global: bins {mret_mpp_u_already_pending_mie0, mret_mpp_u_already_pending_mie1, mret_mpp_u_arrived_later_mie0, mret_mpp_u_arrived_later_mie1, dret_prv_u_already_pending_mie0, dret_prv_u_arrived_later_mie1}
  - cr_line_others = cp_line x cp_others: bins {fast_0_others_pending_lower, external_others_pending_lower, software_others_pending_lower, timer_only_this, fast_14_others_pending_lower, software_only_this, external_others_enabled_idle}
  - cr_line_marks = cp_line x cp_rvfi_marks: bins {software_intr_with_pre_mip, fast_5_intr_with_pre_mip, nmi_ext_nmi_flag, nmi_int_nmi_int_flag, external_irq_valid_pulse, timer_pre_post_mip_differ}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-001, TP-IRQ-002, TP-IRQ-003, TP-IRQ-004, TP-IRQ-005, TP-IRQ-006, TP-IRQ-007, TP-IRQ-012, TP-IRQ-013, TP-IRQ-014, TP-IRQ-019, TP-IRQ-021, TP-IRQ-025, TP-IRQ-028, TP-IRQ-029, TP-IRQ-031, TP-IRQ-034, TP-IRQ-044, TP-IRQ-049, TP-IRQ-053, TP-IRQ-057, TP-IRQ-059, TP-IRQ-061, TP-IRQ-062, TP-IRQ-065, TP-IRQ-071, TP-IRQ-074

### CG-IRQ-002: gen_cg_irq_priority
- Features: F-IRQ-009, F-IRQ-010, F-IRQ-011, F-IRQ-026, F-IRQ-034, F-IRQ-041, F-IRQ-063
- Sample: the trap-decision cycle of an interrupt (rvfi_ext_pre_mip captured by the irq monitor, one cycle before IRQ_TAKEN) where popcount(pre_mip & mie) + irq_nm_i + internal-NMI-pending >= 2; anti-vacuity: single-line entries do not sample, so a hit proves a real arbitration between at least two takeable sources.
- Coverpoints:
  - cp_set = which sources contended: bins fast_fast{>= 2 fast lines}, fast_external, fast_software, fast_timer, external_software, external_timer, software_timer, nmi_fast, nmi_external, nmi_software, nmi_timer, nmi_ext_nmi_int, three_plus{>= 3 distinct classes}, all18{all 18 lines pending and enabled}
  - cp_winner = cause taken: bins nmi_ext, nmi_int, fast, external, software, timer
  - cp_fast_gap = the two lowest pending fast indices: bins adjacent{differ by 1}, far{differ by >= 2}, ends{0 and 14}
  - cp_late = line change between the decision cycle and the IRQ_TAKEN cycle: bins none, higher_added, lower_added
  - cp_drain = position within an all18 drain sequence: bins first, middle, last18
- Crosses:
  - cr_set_winner = cp_set x cp_winner: bins {fast_fast_fast, fast_external_fast, fast_software_fast, fast_timer_fast, external_software_external, external_timer_external, software_timer_software, nmi_fast_nmi_ext, nmi_external_nmi_ext, nmi_software_nmi_ext, nmi_timer_nmi_ext, nmi_ext_nmi_int_nmi_ext, three_plus_fast, three_plus_external, all18_fast}; ignore the remaining combinations: the winner is fixed by the RTL order; a mismatch is a gen_chk_irq failure
  - cr_late_winner = cp_late x cp_winner: bins {higher_added_fast, higher_added_nmi_ext, higher_added_external, lower_added_external, lower_added_software, lower_added_fast, none_fast, none_external}
  - cr_gap_winner = cp_fast_gap x cp_winner: bins {adjacent_fast, far_fast, ends_fast}
  - cr_drain_winner = cp_drain x cp_winner: bins {first_fast, middle_fast, middle_external, middle_software, last18_timer}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-014, TP-IRQ-015, TP-IRQ-016, TP-IRQ-031, TP-IRQ-038, TP-IRQ-045, TP-IRQ-065, TP-IRQ-071, TP-IRQ-073

### CG-IRQ-003: gen_cg_irq_pending_model
- Features: F-IRQ-003, F-IRQ-004, F-IRQ-005, F-IRQ-006, F-IRQ-007, F-IRQ-060
- Sample: cycles in which any irq pin changes or a retired write to mie commits (irq monitor + CSR model), and retired csrr mip / csrrw-csrrs-csrrc mip / csrr mie; condition: an edge or an access; anti-vacuity: quiescent cycles do not sample, so a hit proves an edge or an access was compared against the irq_pending_o / mip model.
- Coverpoints:
  - cp_transition = irq_pending_o model transition: bins rise_enabled{pin 0 -> 1 with its mie bit set: irq_pending_o 0 -> 1}, rise_disabled{pin rise with the mie bit clear: stays 0}, rise_enabled_other_high{pin rise while irq_pending_o already 1}, fall_last{last enabled pin drops: 1 -> 0}, fall_not_last, mie_set_pin_high{mie write enables an already-high pin: 0 -> 1}, mie_clear_pin_high{mie write disables a pending line}, nmi_only_rise{irq_nm_i rises alone: irq_pending_o unchanged}
  - cp_state = core state at the edge: bins mie0_m, mie1_m, u_mode, debug_mode, nmi_mode, step, sleep
  - cp_line_kind = line class (pin monitor): bins software, timer, external, fast_low{index 0..4}, fast_mid{5..9}, fast_high{10..14}
  - cp_mip_access = mip access class (rvfi_insn): bins read_mie0_pins_high{csrr mip with mie = 0 and >= 1 pin high}, read_partial_mie{some pins enabled, some not}, read_all_low, write_csrrw_ignored, write_csrrs_ignored, write_csrrc_ignored
  - cp_mie_write = mie write value class (rvfi_rs1_rdata): bins all_ones{wdata 0xFFFFFFFF reads 0x7FFF0888}, zero, random_masked{bits outside 3/7/11/30:16 set and dropped}, fast_only{[30:16] only}
- Crosses:
  - cr_transition_state = cp_transition x cp_state: bins {rise_enabled_mie0_m, rise_enabled_mie1_m, rise_enabled_u_mode, rise_enabled_debug_mode, rise_enabled_nmi_mode, rise_enabled_step, rise_enabled_sleep, fall_last_mie0_m, fall_last_mie1_m, fall_last_debug_mode, fall_last_sleep, mie_clear_pin_high_mie1_m, mie_set_pin_high_mie0_m, mie_set_pin_high_mie1_m, nmi_only_rise_mie1_m, nmi_only_rise_sleep, rise_disabled_mie1_m, rise_disabled_sleep}
  - cr_transition_line = cp_transition x cp_line_kind: bins {rise_enabled_software, rise_enabled_timer, rise_enabled_external, rise_enabled_fast_low, rise_enabled_fast_mid, rise_enabled_fast_high, fall_last_software, fall_last_timer, fall_last_external, fall_last_fast_low, fall_last_fast_high, rise_disabled_fast_mid, mie_clear_pin_high_external}
  - cr_access_state = cp_mip_access x cp_state: bins {read_mie0_pins_high_mie0_m, read_partial_mie_mie1_m, read_all_low_mie1_m, write_csrrw_ignored_mie1_m, write_csrrs_ignored_mie0_m, write_csrrc_ignored_mie1_m}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-007, TP-IRQ-008, TP-IRQ-009, TP-IRQ-010, TP-IRQ-011, TP-IRQ-012, TP-IRQ-037, TP-IRQ-043, TP-IRQ-063, TP-IRQ-064, TP-IRQ-070, TP-IRQ-071, TP-IRQ-075, TP-IRQ-077, TP-IRQ-078

### CG-IRQ-004: gen_cg_irq_timing
- Features: F-IRQ-016, F-IRQ-017, F-IRQ-018, F-IRQ-019, F-IRQ-020, F-IRQ-021, F-IRQ-022, F-IRQ-023, F-IRQ-024, F-IRQ-025, F-IRQ-026, F-IRQ-059, F-IRQ-060, F-IRQ-064
- Sample: the first cycle in which an interrupt request becomes takeable (irq monitor: a line pending-and-enabled with MIE or U-mode, or irq_nm rising, outside debug/step/nmi_mode), classified by the pipeline situation of that cycle from the dbus/ibus/RVFI monitors and the program listing; the outcome is recorded at the decision or its abandonment; condition: one sample per request; anti-vacuity: idle cycles never sample, so a hit proves a request arrived in the named context and its outcome was compared.
- Coverpoints:
  - cp_ctx = pipeline situation at arrival: bins id_empty, id_alu, id_branch, id_jump, id_load_wait{load waiting for data_rvalid_i}, id_store_wait, id_div, id_mul, id_csr_flush{csr write not touching mie/mstatus/mtvec}, id_csr_enable{csrs mstatus.MIE or csrw/csrs mie enabling this line}, id_csr_disable{write masking this line}, id_csr_mtvec, id_mret, id_dret, id_wfi, id_exc{ecall/ebreak/illegal/fetch-error in ID}, wb_fault_same_cycle{data_err_i response this cycle}, zcmp_expanded, zcmp_commit, first_fetch_wake{FIRST_FETCH after a WFI wake}, reset_release, fetch_stall_gnt{ibus request waiting for gnt}, fetch_stall_rvalid
  - cp_rvalid_relation = for id_load_wait/id_store_wait: bins same_cycle_as_rvalid, before_rvalid, after_rvalid
  - cp_outcome = observed outcome: bins taken, withdrawn{line dropped before IRQ_TAKEN: no trap}, masked_by_write{csr write disabled it first}, deferred_by_exception, taken_other_line
  - cp_latency = cycles from the sample to instr_req_o at the vector: bins two{2}, three_five{[3:5]}, six_ten{[6:10]}, long{[11:$]}
  - cp_pulse_width = cycles the line stayed high: bins one{1}, two{2}, three_plus{[3:$]}, level_until_ack
  - cp_change_before_taken = line change between the decision cycle and IRQ_TAKEN: bins stable, dropped_all, dropped_winner_other_remains, higher_added, lower_added
- Crosses:
  - cr_ctx_outcome = cp_ctx x cp_outcome: bins {id_empty_taken, id_alu_taken, id_branch_taken, id_jump_taken, id_load_wait_taken, id_store_wait_taken, id_div_taken, id_mul_taken, id_csr_flush_taken, id_csr_enable_taken, id_csr_disable_masked_by_write, id_csr_mtvec_taken, id_mret_taken, id_dret_taken, id_wfi_taken, id_exc_deferred_by_exception, wb_fault_same_cycle_deferred_by_exception, zcmp_expanded_taken, zcmp_commit_taken, first_fetch_wake_taken, reset_release_taken, fetch_stall_gnt_taken, fetch_stall_rvalid_taken, id_empty_withdrawn, id_load_wait_withdrawn, id_empty_taken_other_line, id_div_withdrawn}
  - cr_ctx_rvalid = cp_ctx x cp_rvalid_relation: bins {id_load_wait_same_cycle_as_rvalid, id_load_wait_before_rvalid, id_load_wait_after_rvalid, id_store_wait_same_cycle_as_rvalid, id_store_wait_before_rvalid}
  - cr_ctx_latency = cp_ctx x cp_latency: bins {id_empty_two, id_load_wait_three_five, id_load_wait_six_ten, id_load_wait_long, id_div_long, id_div_six_ten, zcmp_expanded_three_five, zcmp_commit_six_ten, fetch_stall_rvalid_long, first_fetch_wake_two, id_mret_two, id_mret_three_five}
  - cr_pulse_change_outcome = cp_pulse_width x cp_change_before_taken x cp_outcome: bins {one_dropped_all_withdrawn, two_dropped_all_withdrawn, one_stable_taken, two_stable_taken, level_until_ack_stable_taken, three_plus_higher_added_taken_other_line, three_plus_lower_added_taken, level_until_ack_dropped_winner_other_remains_taken_other_line, three_plus_stable_taken}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-012, TP-IRQ-020, TP-IRQ-021, TP-IRQ-022, TP-IRQ-023, TP-IRQ-024, TP-IRQ-025, TP-IRQ-026, TP-IRQ-027, TP-IRQ-028, TP-IRQ-029, TP-IRQ-030, TP-IRQ-031, TP-IRQ-032, TP-IRQ-049, TP-IRQ-059, TP-IRQ-063, TP-IRQ-064, TP-IRQ-066, TP-IRQ-071, TP-IRQ-072, TP-IRQ-076, TP-IRQ-077

### CG-IRQ-005: gen_cg_irq_handler_flow
- Features: F-IRQ-015, F-IRQ-023, F-IRQ-027, F-IRQ-028, F-IRQ-029
- Sample: a retired mret whose matching entry was an interrupt (handler return), and each nested interrupt entry (entry depth >= 2 in the gen_chk_irq entry/return stack); condition: handler return or nested entry; anti-vacuity: only handler returns and nested entries sample, so a hit proves the re-trap / nesting behaviour was exercised.
- Coverpoints:
  - cp_line_at_mret = state of the serviced line at the mret: bins still_high_same, dropped_by_ack, dropped_new_other_pending, masked_in_handler{handler cleared its mie bit while the line stays high}
  - cp_reentry = re-entry distance after the mret (RVFI): bins immediate{0 instructions retired before the next vector}, later, none
  - cp_nesting = depth reached: bins depth1, depth2_same_prio, depth2_lower{nested by a lower-priority line after MIE re-enable}, depth2_higher, depth3_plus
  - cp_mtvec_in_handler = mtvec rewritten inside the handler (CSR model): bins unchanged, rewritten
  - cp_mpp_restored = privilege the mret returns to: bins m, u
- Crosses:
  - cr_state_reentry = cp_line_at_mret x cp_reentry: bins {still_high_same_immediate, dropped_by_ack_none, dropped_by_ack_later, dropped_new_other_pending_immediate, masked_in_handler_none, masked_in_handler_later}
  - cr_nesting_mtvec = cp_nesting x cp_mtvec_in_handler: bins {depth1_unchanged, depth2_lower_unchanged, depth2_higher_unchanged, depth2_same_prio_unchanged, depth3_plus_unchanged, depth1_rewritten, depth2_same_prio_rewritten}
  - cr_state_mpp = cp_line_at_mret x cp_mpp_restored: bins {still_high_same_u, still_high_same_m, dropped_new_other_pending_u, dropped_by_ack_u, dropped_by_ack_m}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-020, TP-IRQ-028, TP-IRQ-032, TP-IRQ-033, TP-IRQ-034, TP-IRQ-071, TP-IRQ-077

### CG-IRQ-006: gen_cg_irq_vector
- Features: F-IRQ-012, F-IRQ-013, F-IRQ-014, F-IRQ-015, F-IRQ-061, F-IRQ-062
- Sample: interrupt entry (first handler pc from rvfi_pc_rdata with rvfi_intr / ibus monitor) and retired csrw/csrs/csrc mtvec plus the first csrr mtvec after reset; condition: entry or mtvec access; anti-vacuity: samples only on entries and mtvec accesses, so a hit proves the vector arithmetic or the WARL rule was exercised for that id/base class.
- Coverpoints:
  - cp_id = interrupt id: bins id3{3}, id7{7}, id11{11}, fast[15]{[16:30]}, id31_ext{31, external NMI}, id31_int{internal NMI, vector forced to 31}
  - cp_base_class = mtvec base in force: bins boot_init, sw_aligned, sw_legalised, upper_half{base[31] == 1}
  - cp_mtvec_wdata = value class of a software write: bins mode00, mode01, mode1x{10, 11}, base_low_nonzero{wdata[7:2] != 0}, boot_readback{first csrr mtvec == {boot_addr[31:8], 8'h01}}
- Crosses:
  - cr_id_base = cp_id x cp_base_class: bins {id3_boot_init, id3_sw_aligned, id3_sw_legalised, id3_upper_half, id7_boot_init, id7_sw_legalised, id11_sw_aligned, id11_upper_half, fast_0_boot_init, fast_0_sw_legalised, fast_14_sw_aligned, fast_14_upper_half, fast_7_sw_aligned, id31_ext_boot_init, id31_ext_sw_legalised, id31_ext_upper_half, id31_int_sw_aligned, id31_int_boot_init, id7_sw_aligned, id11_boot_init}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-001, TP-IRQ-002, TP-IRQ-003, TP-IRQ-004, TP-IRQ-005, TP-IRQ-006, TP-IRQ-007, TP-IRQ-017, TP-IRQ-018, TP-IRQ-019, TP-IRQ-071

### CG-IRQ-007: gen_cg_irq_nmi
- Features: F-IRQ-030, F-IRQ-031, F-IRQ-032, F-IRQ-033, F-IRQ-034, F-IRQ-035, F-IRQ-036, F-IRQ-038, F-IRQ-043, F-IRQ-049, F-IRQ-055, F-IRQ-066
- Sample: an NMI entry (rvfi_ext_nmi or rvfi_ext_nmi_int captured; mcause read-back 0x8000001F or 0xFFFFFFE0) and each mret that exits NMI mode (gen_chk_nmi model); condition: NMI event; anti-vacuity: only NMI entries/exits sample, so a hit proves an NMI was taken from the recorded context and its return compared.
- Coverpoints:
  - cp_source = fault origin (dbus error response vs gen_chk_pmp deny): bins ext, int_ecc, both_same_cycle
  - cp_ctx_pre = what was running before the NMI: bins user_code, exc_handler, irq_handler, exc_vector_first{NMI taken at the exception vector before its first instruction: mepc == mtvec base}, wfi_sleep, reset_release, dret_exit, after_mret_still_high{re-entry right after the NMI handler's mret}
  - cp_mie_pre = mstatus.MIE before the NMI (CSR model): bins mie0, mie1
  - cp_priv_pre = privilege before the entry (rvfi_mode / CSR model): bins m, u
  - cp_in_handler = what happened inside the NMI handler: bins none, nmi_reasserted_ignored, irq_enabled_masked{handler set MIE = 1 with a line pending: not taken}, exc_taken, int_err_pending{integrity error inside the handler}, regular_irq_pending_taken_after_mret, debug_session_nmi_mode_kept{debug entry (debug_req_i / step) and dret inside the NMI handler: pending mip & mie lines and a re-asserted irq_nm_i stay masked until the handler's mret (F-IRQ-066, H-N1)}
  - cp_mstack = mstack restore outcome at the exiting mret: bins restore_ok, sw_epc_write_discarded{handler wrote mepc/mcause; mret restored the stacked values}, nested_exc_context_lost{exception inside the handler overwrote mstack}
  - cp_mepc_align = mepc[1] read-back: bins word, half
- Crosses:
  - cr_source_ctx = cp_source x cp_ctx_pre: bins {ext_user_code, ext_exc_handler, ext_irq_handler, ext_wfi_sleep, ext_reset_release, ext_dret_exit, ext_after_mret_still_high, int_ecc_user_code, int_ecc_exc_handler, int_ecc_irq_handler, int_ecc_after_mret_still_high, ext_exc_vector_first, int_ecc_exc_vector_first, both_same_cycle_user_code, both_same_cycle_exc_handler}; ignore int_ecc x wfi_sleep/reset_release: no data access completes in sleep or before the first instruction
  - cr_ctx_priv_mie = cp_ctx_pre x cp_priv_pre x cp_mie_pre: bins {user_code_m_mie0, user_code_m_mie1, user_code_u_mie0, user_code_u_mie1, exc_handler_m_mie0, irq_handler_m_mie0, wfi_sleep_m_mie0, wfi_sleep_u_mie1, dret_exit_u_mie0, after_mret_still_high_m_mie1}
  - cr_handler_mstack = cp_in_handler x cp_mstack: bins {none_restore_ok, none_sw_epc_write_discarded, exc_taken_nested_exc_context_lost, irq_enabled_masked_restore_ok, nmi_reasserted_ignored_restore_ok, int_err_pending_restore_ok, regular_irq_pending_taken_after_mret_restore_ok, debug_session_nmi_mode_kept_restore_ok}
  - cr_source_align = cp_source x cp_mepc_align: bins {ext_word, ext_half, int_ecc_word, int_ecc_half}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-007, TP-IRQ-019, TP-IRQ-035, TP-IRQ-036, TP-IRQ-037, TP-IRQ-039, TP-IRQ-040, TP-IRQ-042, TP-IRQ-044, TP-IRQ-045, TP-IRQ-047, TP-IRQ-053, TP-IRQ-059, TP-IRQ-073, TP-IRQ-078

### CG-IRQ-008: gen_cg_irq_nmi_int
- Features: F-IRQ-040, F-IRQ-041, F-IRQ-042, F-IRQ-043, F-IRQ-044
- Sample: a dbus-agent integrity-error injection (corrupted data_rdata_intg_i on a load or store response) tracked by gen_chk_bus_intg_rsp to its alert and NMI, plus retired writes to mcause; condition: injection or mcause write; anti-vacuity: injections happen only under knob:dmem_err_rate != none or a directed injection, so a hit proves an injected error was followed to its consequences.
- Coverpoints:
  - cp_err_op = access kind of the corrupted response (dbus monitor): bins load, store
  - cp_err_half = which part of the access carried the error (dbus monitor): bins aligned, mis_first, mis_second
  - cp_taken_after = instructions retired between the error response and the NMI entry: bins zero{0}, one{1}; ignore_bins two_plus{[2:$]}: violates "at most one instruction" (gen_chk_bus_intg_rsp failure)
  - cp_pending_ctx = state when the error arrived: bins idle, second_err_while_pending, ext_nmi_same_cycle, in_nmi_handler, in_debug_mode, in_irq_handler
  - cp_effects = side effects observed (alert monitor, RVFI, read-back): bins alert_pulse{alert_major_bus_o in the error cycle}, rf_wr_suppressed{rvfi_ext_rf_wr_suppress on the load}, store_no_rf, mtval_first_addr{after second_err_while_pending: mtval == first error address}
  - cp_mcause_write = software mcause write class (rvfi_rs1_rdata vs read-back): bins c000xx_reads_ffffffe0, w8000xx_reads_same, w20_reads_0, bits29_5_dropped
- Crosses:
  - cr_op_half = cp_err_op x cp_err_half: bins {load_aligned, load_mis_first, load_mis_second, store_aligned, store_mis_first, store_mis_second}
  - cr_op_ctx = cp_err_op x cp_pending_ctx: bins {load_idle, load_second_err_while_pending, load_ext_nmi_same_cycle, load_in_nmi_handler, load_in_debug_mode, load_in_irq_handler, store_idle, store_second_err_while_pending, store_in_nmi_handler, store_ext_nmi_same_cycle, store_in_debug_mode}
  - cr_ctx_taken = cp_pending_ctx x cp_taken_after: bins {idle_zero, idle_one, in_irq_handler_zero, in_irq_handler_one}
  - cr_op_effects = cp_err_op x cp_effects: bins {load_alert_pulse, load_rf_wr_suppressed, store_alert_pulse, store_store_no_rf, load_mtval_first_addr, store_mtval_first_addr}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-042, TP-IRQ-044, TP-IRQ-045, TP-IRQ-046, TP-IRQ-047, TP-IRQ-048, TP-IRQ-073, TP-IRQ-075

### CG-IRQ-009: gen_cg_irq_wfi
- Features: F-IRQ-045, F-IRQ-046, F-IRQ-047, F-IRQ-048, F-IRQ-049, F-IRQ-050, F-IRQ-051, F-IRQ-052, F-IRQ-053, F-IRQ-054, F-IRQ-064, F-EXC-011
- Sample: retirement of WFI (rvfi_insn == 32'h10500073) or its illegal-instruction trap record, with the gen_chk_sleep bookkeeping (core_busy_o values, instr_req_o gap length, wake source from the irq/debug pin monitor, mcycle read-back); condition: wfi in rvfi_insn; anti-vacuity: only WFI instructions sample, so a hit proves a sleep (or nop/trap path) with the recorded wake source.
- Coverpoints:
  - cp_priv_tw = privilege and mstatus.TW: bins m, u_tw0, u_tw1{illegal instruction}
  - cp_wake = what ended the sleep: bins irq_taken, irq_local_only{mie set, MIE 0, M-mode: resume without trap}, nmi_ext, nmi_int, debug_req, debug_req_and_irq{both present: debug wins}, in_debug_nop, step_nop, already_pending{wake condition true at the wfi}, masked_line_held{inside a handler with the serviced line still high}, none_long{slept >= 100 cycles before a wake}
  - cp_sleep_cycles = cycles with instr_req_o low: bins passthrough{[0:2]}, short{[3:10]}, medium{[11:100]}, long{[101:$]}
  - cp_disabled_high = a mie-disabled line was high during the sleep without waking: bins yes, no
  - cp_busy_off = core_busy_o == IbexMuBiOff observed during the wfi: bins off_seen, off_not_seen
  - cp_wb_at_wfi = WB content when the wfi reached ID: bins empty, ls_ok, ls_fault{fault wins, wfi discarded}
  - cp_mcycle = mcycle read-back across the sleep: bins counted_through_sleep{mcycle delta across the sleep == sleep cycles + fixed overhead}, no_sleep
  - cp_wake_line = line that woke the core (pin monitor): bins software, timer, external, fast, nmi
- Crosses:
  - cr_priv_wake = cp_priv_tw x cp_wake: bins {m_irq_taken, m_irq_local_only, m_nmi_ext, m_nmi_int, m_debug_req, m_debug_req_and_irq, m_in_debug_nop, m_step_nop, m_already_pending, m_masked_line_held, m_none_long, u_tw0_irq_taken, u_tw0_nmi_ext, u_tw0_debug_req, u_tw0_none_long, u_tw0_already_pending}; ignore u_tw1 x any wake: it traps and never sleeps; ignore u_tw0 x irq_local_only: U-mode ignores MIE, so a locally enabled line is taken
  - cr_wake_sleep = cp_wake x cp_sleep_cycles: bins {irq_taken_passthrough, irq_taken_short, irq_taken_medium, irq_taken_long, already_pending_passthrough, in_debug_nop_passthrough, step_nop_passthrough, nmi_ext_medium, nmi_ext_short, debug_req_medium, irq_local_only_short, irq_local_only_medium, none_long_medium, none_long_long}
  - cr_wake_busy = cp_wake x cp_busy_off: bins {irq_taken_off_seen, none_long_off_seen, in_debug_nop_off_seen, step_nop_off_seen, already_pending_off_seen, already_pending_off_not_seen, irq_local_only_off_seen}
  - cr_wb_priv = cp_wb_at_wfi x cp_priv_tw: bins {empty_m, ls_ok_m, ls_fault_m, ls_fault_u_tw0, empty_u_tw0}
  - cr_disabled_wake = cp_disabled_high x cp_wake: bins {yes_none_long, yes_nmi_ext, yes_debug_req, yes_irq_taken}
  - cr_wake_line = cp_wake x cp_wake_line: bins {irq_taken_software, irq_taken_timer, irq_taken_external, irq_taken_fast, irq_local_only_software, irq_local_only_fast, nmi_ext_nmi}
  - cr_wake_mcycle = cp_wake x cp_mcycle: bins {irq_taken_counted_through_sleep, none_long_counted_through_sleep, in_debug_nop_no_sleep}
- Adopted (riscv-dv): none
- TP items: TP-EXC-010, TP-IRQ-049, TP-IRQ-050, TP-IRQ-051, TP-IRQ-052, TP-IRQ-053, TP-IRQ-054, TP-IRQ-055, TP-IRQ-056, TP-IRQ-057, TP-IRQ-058, TP-IRQ-066, TP-IRQ-068, TP-IRQ-069, TP-IRQ-074

### CG-IRQ-010: gen_cg_irq_debug_interplay
- Features: F-IRQ-024, F-IRQ-037, F-IRQ-038, F-IRQ-039, F-IRQ-050, F-IRQ-051, F-IRQ-066
- Sample: an interrupt/NMI line pending-and-enabled while rvfi_ext_debug_mode == 1, or while dcsr.step == 1 outside debug mode, and each dret retirement with a pending line; for cp_mode.debug_in_nmi_handler the window is a debug session opened while the gen_chk_nmi model has nmi_mode set (entry after a base + 0x7C vector fetch and before the matching mret); condition: a line asserted inside such a window; anti-vacuity: samples only in debug/step windows with a line asserted, so a hit proves the masking and the post-exit behaviour were exercised.
- Coverpoints:
  - cp_line = line class (pin monitor): bins irq, nmi_ext, nmi_int
  - cp_mode = debug or step window (rvfi_ext_debug_mode, CSR model): bins debug_mode, step_outside, debug_in_nmi_handler{debug window opened while nmi_mode is set: the NMI handler is running (F-IRQ-066); post_exit not_taken until the handler's mret}
  - cp_duration = line held or dropped before the exit (pin monitor): bins held_through_exit, dropped_before_exit
  - cp_post_exit = behaviour after the exit (RVFI): bins taken_before_first_insn, not_taken
  - cp_dcsr_prv = dcsr.prv (CSR model): bins m, u
  - cp_nmip_read = csrr dcsr in debug mode: bins read_with_nmi_high, read_with_nmi_low
  - cp_exit_kind = how the window ended (RVFI): bins dret, step_complete{stepped instruction retires; debug re-entry}
- Crosses:
  - cr_line_mode_post = cp_line x cp_mode x cp_post_exit: bins {irq_debug_mode_taken_before_first_insn, irq_debug_mode_not_taken, nmi_ext_debug_mode_taken_before_first_insn, nmi_ext_debug_mode_not_taken, nmi_int_debug_mode_taken_before_first_insn, irq_step_outside_not_taken, nmi_ext_step_outside_not_taken, irq_debug_in_nmi_handler_not_taken, nmi_ext_debug_in_nmi_handler_not_taken}
  - cr_line_prv = cp_line x cp_dcsr_prv: bins {irq_u, irq_m, nmi_ext_u, nmi_ext_m}
  - cr_dur_post = cp_duration x cp_post_exit: bins {held_through_exit_taken_before_first_insn, dropped_before_exit_not_taken}
  - cr_line_exit = cp_line x cp_exit_kind: bins {irq_dret, irq_step_complete, nmi_ext_dret, nmi_ext_step_complete}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-029, TP-IRQ-041, TP-IRQ-042, TP-IRQ-043, TP-IRQ-054, TP-IRQ-069, TP-IRQ-075, TP-IRQ-078

### CG-IRQ-011: gen_cg_irq_reset_fetch_en
- Features: F-IRQ-014, F-IRQ-055, F-IRQ-056, F-IRQ-065
- Sample: reset release (first cycle with rst_ni high) with the irq/debug pin state, the first csrr mstatus/mie/mtvec/mip retirements, and every fetch_enable_i != On window during which a line is pending (fetch_enable monitor + irq monitor); condition: one sample per reset and per Off window; anti-vacuity: samples only at reset release and in Off windows, so a hit proves the reset-time / fetch-disabled interrupt path was exercised.
- Coverpoints:
  - cp_lines_at_reset = lines asserted at reset release (pin monitor): bins none, regular_only, nmi_only, nmi_and_regular, debug_and_nmi, debug_and_regular
  - cp_first_event = first architectural event after reset: bins boot_insn{first retirement at the boot pc}, nmi_before_insn, debug_before_insn
  - cp_reset_reads = first CSR read-backs after reset: bins mstatus_0x80, mie_0, mtvec_boot_page, mip_reflects_pins
  - cp_boot_mret = mret executed before any trap (RVFI): bins to_u_mie1{mret as an early instruction: U-mode, MIE = 1}
  - cp_fetch_off = interrupt situation in a fetch_enable_i Off window: bins irq_pending_while_off_csr_updated{entry decided while Off: mepc/mcause change without instr_req_o}, irq_arrives_while_off, nmi_while_off, none_pending_while_off
  - cp_fetch_on_after = first fetch after fetch_enable_i returns to On (ibus monitor): bins handler_fetched_at_on{first instr_req_o after On is the vector}, resume_at_on
- Crosses:
  - cr_lines_first = cp_lines_at_reset x cp_first_event: bins {none_boot_insn, regular_only_boot_insn, nmi_only_nmi_before_insn, nmi_and_regular_nmi_before_insn, debug_and_nmi_debug_before_insn, debug_and_regular_debug_before_insn}
  - cr_off_on = cp_fetch_off x cp_fetch_on_after: bins {irq_pending_while_off_csr_updated_handler_fetched_at_on, nmi_while_off_handler_fetched_at_on, irq_arrives_while_off_handler_fetched_at_on, none_pending_while_off_resume_at_on}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-019, TP-IRQ-059, TP-IRQ-060, TP-IRQ-067

### CG-IRQ-012: gen_cg_irq_cross_stall
- Features: F-IRQ-017, F-IRQ-018, F-IRQ-022, F-IRQ-025, F-IRQ-027, F-EXC-025, F-EXC-069
- Sample: as CG-IRQ-004 (first takeable cycle of an interrupt request, and the decision cycle), joined with the dbus/ibus monitor states of that cycle and the observed hold behaviour of the line; condition: as CG-IRQ-004; anti-vacuity: as CG-IRQ-004; the triple cross proves the three conditions of the DV_prompt example (fetch stalled, data error returning, interrupt pending) coexisted in one cycle.
- Coverpoints:
  - cp_dbus = data-bus state at the sample: bins idle, gnt_pending, rvalid_pending, rvalid_err_now{data_rvalid_i & data_err_i this cycle}, rvalid_ok_now
  - cp_ibus = instruction-bus state at the sample: bins idle, gnt_pending, rvalid_pending, rvalid_err_now
  - cp_irq_class = pending line set class (irq monitor): bins single, multi, with_nmi, nmi_int_only
  - cp_hold = observed line behaviour: bins pulse1, held_until_taken, held_through_handler
- Crosses:
  - cr_triple = cp_dbus x cp_ibus x cp_irq_class: bins {rvalid_err_now_rvalid_pending_single, rvalid_err_now_rvalid_pending_multi, rvalid_err_now_rvalid_pending_with_nmi, rvalid_err_now_gnt_pending_single, rvalid_err_now_idle_single, rvalid_ok_now_rvalid_pending_single, rvalid_pending_rvalid_pending_single, rvalid_pending_gnt_pending_multi, gnt_pending_rvalid_pending_single, idle_rvalid_err_now_single, idle_idle_single, rvalid_err_now_rvalid_err_now_single, rvalid_err_now_rvalid_pending_nmi_int_only, idle_idle_multi, idle_idle_with_nmi}
  - cr_hold_class = cp_hold x cp_irq_class: bins {pulse1_single, pulse1_multi, held_until_taken_single, held_until_taken_multi, held_until_taken_with_nmi, held_through_handler_single, held_through_handler_multi, held_through_handler_with_nmi}
  - cr_dbus_hold = cp_dbus x cp_hold: bins {rvalid_pending_pulse1, rvalid_err_now_pulse1, rvalid_pending_held_until_taken, rvalid_err_now_held_through_handler}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-014, TP-IRQ-022, TP-IRQ-023, TP-IRQ-027, TP-IRQ-030, TP-IRQ-032, TP-IRQ-038, TP-IRQ-071, TP-IRQ-072, TP-IRQ-073

## Counts

| metric | count |
|---|---|
| covergroups | 25 (CG-EXC-001..013, CG-IRQ-001..012) |
| coverpoints | 158 |
| coverpoint bins | 637 (array bins fast[15] expanded; ignore_bins not counted) |
| crosses | 108 |
| cross bins (required, named) | 906 |
| adopted bins (riscv-dv) | 0 |

Counts are produced by the parser that also generates trace_tp_bin_exc_irq.csv, so the CSV and this
table agree by construction (fix pass: +1 bin in CG-EXC-003, +1/+1 in CG-IRQ-007, +1/+2 in
CG-IRQ-010 for D12 and F-IRQ-066; the validation script re-derives the totals). Cross bins that are
not named as required still exist in the auto-cross and are reported by urg; only the named ones are
traced.

## Probe candidates

Target is zero probes; every bin above is sampled from the DUT boundary (instruction/data buses,
irq/debug pins, alerts, core_busy_o, double_fault_seen_o, irq_pending_o, crash_dump_o), from RVFI
(incl. rvfi_ext_*), from handler CSR read-backs, or from checker-model events derived from those.
Items the DV Lead may want to promote to coverage-only probes if the boundary derivation proves
ambiguous in practice:

- CG-IRQ-004 / CG-IRQ-012 decision cycle ("first takeable cycle", IRQ_TAKEN cycle). Boundary
  derivation: pipe-empty inference from the ibus monitor and RVFI plus rvfi_ext_irq_valid; the
  one-cycle handshake (decision, then live capture) is inferred from rvfi_ext_pre_mip vs the pin
  monitor. Probe fallback: id_stage_i.controller_i.ctrl_fsm_cs == IRQ_TAKEN (rtl/ibex_controller.sv,
  tb-infra P4, fcov_interrupt_taken hook). Coverage-only; no checker depends on it.
- CG-IRQ-004.cp_ctx zcmp_expanded vs zcmp_commit and CG-EXC-008.cp_op_pos. Boundary derivation:
  rvfi_ext_expanded_insn_valid/last plus the micro-op class implied by the cm.* encoding (rlist)
  and the dbus request count. Probe fallback: if_stage_i instr_gets_expanded (instr_exp_e) --
  coverage-only.
- CG-IRQ-008.cp_pending_ctx.second_err_while_pending. Boundary derivation: a second corrupted
  response observed by the dbus monitor before the first internal-NMI entry (RVFI). Probe fallback:
  id_stage_i.controller_i.mem_resp_intg_err_irq_pending_q (rtl/ibex_controller.sv:394). Not needed
  unless the entry timing makes the ordering ambiguous.
- CG-IRQ-007 nmi_mode context (in_handler bins) and CG-EXC-010 sync_exc_seen state. Boundary
  derivation: gen_chk_nmi / gen_chk_double_fault models built from entries, mrets and cpuctrlsts
  read-backs. Probe fallback: id_stage_i.controller_i.nmi_mode_q and
  cs_registers_i.cpuctrlsts_part_q.sync_exc_seen -- coverage-only, only if the DV Lead wants the
  models cross-checked.
- CG-EXC-013.cp_wb_at_id_exc and CG-EXC-006.cp_younger. Boundary derivation: dbus monitor
  outstanding state plus the program listing (next program-order instruction) and ibus delivery
  timestamps. No probe expected.
- CG-EXC-001.cp_mtvec_class / CG-IRQ-006.cp_base_class. Boundary derivation: CSR model tracking
  retired csrw/csrs/csrc mtvec (rvfi_rs1_rdata) and the boot init from boot_addr_i. No probe.

No bin in this file requires a probe to be samplable; the fallbacks above are listed for the DV
Lead's decision only.


# 3.4 Areas PMP: Physical memory protection and Smepmp (16 regions, G=0)


All covergroups live in the gen_ namespace and are sampled from the boundary (ibus/dbus monitors), RVFI, and the gen_chk_pmp / gen_chk_csr_readback models; no RTL covergroup is extended. Counts and ranges derive from ibex_pkg parameters (PMPNumRegions = 16 in this configuration; bins written as r0..r15 / e0..e15 / a0..a15 are generated over 0..PMPNumRegions-1). Wrong-verdict combinations are excluded with ignore_bins and a reason (never `illegal_bins = default sequence`); mseccfg state transitions are enumerated. Truth-table bin names carry the expected verdict in their description; the verdict itself is asserted by gen_chk_pmp, so a wrong-verdict sample fails the run before it could be counted.

Status resolution (Critic v1 fix): Features lines keep the original F-PMP IDs; IDs marked FOLDED in gen_part_pmp.md are carried by the bins their Status line names (all in this file), IDs marked ALIAS resolve to the canonical entry (F-EXC-005/006/035, F-PRV-005/007/015, F-DBG-055, F-CSR-024). F-PMP-087 and F-PMP-095 are canonical for F-EXC-033 and F-DBG-052.

Bin naming: `CG-PMP-nnn.cp_<name>.<bin>` for coverpoint bins and `CG-PMP-nnn.cr_<name>.<bin>` for cross bins. Truth-table cross bins are `c<LRWX>_<priv>_<type>`; no-match bins are `nm_<priv>_<type>_mml<x>_mmwp<y>`.

### CG-PMP-001: gen_cg_pmp_cfg_write
- Features: F-PMP-001, F-PMP-003, F-PMP-004, F-PMP-005, F-PMP-006, F-PMP-007, F-PMP-013, F-PMP-018, F-PMP-019, F-PMP-020, F-PMP-028, F-PMP-029, F-PMP-030, F-PMP-031, F-PMP-032, F-PMP-100
- Sample: RVFI retire of a CSR write instruction (csrrw/csrrs/csrrc and immediate forms) whose csr field is pmpcfg0..3; one sample per entry byte i = 4*idx + b (four samples per write); condition: rvfi_trap == 0 and the write is not read-only (rs1 != x0 / uimm != 0 for set/clear forms); anti-vacuity: only PMP cfg writes sample (most retires never do), and the outcome field is computed by the gen_chk_csr_readback model from pre-write state, so a hit proves a pmpcfg write retired under the named lock/MML/RLB state and its per-entry outcome was predicted
- Coverpoints:
  - cp_entry = i (0..PMPNumRegions-1): bins e0{0}, e1{1}, e2{2}, e3{3}, e4{4}, e5{5}, e6{6}, e7{7}, e8{8}, e9{9}, e10{10}, e11{11}, e12{12}, e13{13}, e14{14}, e15{15}
  - cp_op = csr op class: bins csrrw{csrrw/csrrwi}, csrrs{csrrs/csrrsi}, csrrc{csrrc/csrrci}
  - cp_wr_mode = written A field of entry i (after RMW combine): bins off{0}, tor{1}, na4{2}, napot{3}
  - cp_wr_lrwx = written {L,R,W,X} of entry i (after RMW combine): bins c0000{0000}, c0001{0001}, c0010{0010}, c0011{0011}, c0100{0100}, c0101{0101}, c0110{0110}, c0111{0111}, c1000{1000}, c1001{1001}, c1010{1010}, c1011{1011}, c1100{1100}, c1101{1101}, c1110{1110}, c1111{1111}
  - cp_res_bits = written bits [6:5] of entry i: bins zero{0}, nonzero{1..3}
  - cp_mml = mseccfg.mml at write: bins mml0{0}, mml1{1}
  - cp_rlb = mseccfg.rlb at write: bins rlb0{0}, rlb1{1}
  - cp_prelock = entry i L bit before the write: bins unlocked{0}, locked{1}
  - cp_outcome = model outcome for entry i: bins written{stored as legalised}, w_dropped{stored with W forced 0 (RW=01, MML=0)}, ignored_lock{L=1 and RLB=0}, ignored_mml_exec{MML=1, RLB=0, is_mml_m_exec_cfg}
  - cp_word_lockmix = number of entries with L=1 (RLB=0) among the four of the written word: bins none{0}, some{1..3}, all{4}
- Crosses:
  - cr_rw01_mml = cp_wr_lrwx{RW=01 rows} x cp_mml x cp_rlb x cp_outcome: rw01_mml0_wdrop (c0010/c0011/c1010/c1011 with mml0 -> w_dropped (W cleared, X/L kept)), rw01_mml1_stored (c0010/c0011 with mml1 -> written verbatim), rw01_mml1_l1_rlb0_suppressed (c1010/c1011 with mml1, rlb0 -> ignored_mml_exec), rw01_mml1_l1_rlb1_stored (c1010/c1011 with mml1, rlb1 -> written); ignore rw01_mml0_written: legalisation always clears W when MML=0 (F-PMP-004)
  - cr_lock_outcome = cp_prelock x cp_rlb x cp_outcome: locked_rlb0_ignored (pre-locked entry, RLB=0 -> ignored_lock), locked_rlb1_written (pre-locked entry, RLB=1 -> written (incl. clearing L)), unlocked_rlb0_written, unlocked_rlb1_written; ignore locked_rlb0_written: lock always wins when RLB=0; ignore unlocked_x_ignored_lock: an unlocked entry is never lock-ignored
  - cr_mml_exec_suppress = cp_mml{mml1} x cp_rlb x cp_wr_lrwx{c1001,c1010,c1011,c1101} x cp_outcome: rlb0_c1001_suppressed (ignored_mml_exec), rlb0_c1010_suppressed (ignored_mml_exec), rlb0_c1011_suppressed (ignored_mml_exec), rlb0_c1101_suppressed (ignored_mml_exec), rlb1_c1001_written (RLB lifts the restriction), rlb1_c1010_written (RLB lifts the restriction), rlb1_c1011_written (RLB lifts the restriction), rlb1_c1101_written (RLB lifts the restriction); ignore rlb0_x_written: suppression is unconditional for these rows when RLB=0
  - cr_mml_nonexec_accept = cp_mml{mml1} x cp_rlb{rlb0} x cp_wr_lrwx{c1000,c1100,c1110,c1111} x cp_outcome{written}: c1000_written (locked non-executable rows accepted), c1100_written (locked non-executable rows accepted), c1110_written (locked non-executable rows accepted), c1111_written (locked non-executable rows accepted)
  - cr_suppress_mode = cp_outcome{ignored_mml_exec} x cp_wr_mode: off (A=OFF still suppressed (F-PMP-030)), tor, na4, napot
  - cr_mode_lrwx = cp_wr_mode x cp_wr_lrwx: 64 required bins: off_c0000, off_c0001, off_c0010, off_c0011, off_c0100, off_c0101, off_c0110, off_c0111, off_c1000, off_c1001, off_c1010, off_c1011, off_c1100, off_c1101, off_c1110, off_c1111, tor_c0000, tor_c0001, tor_c0010, tor_c0011, tor_c0100, tor_c0101, tor_c0110, tor_c0111, tor_c1000, tor_c1001, tor_c1010, tor_c1011, tor_c1100, tor_c1101, tor_c1110, tor_c1111, na4_c0000, na4_c0001, na4_c0010, na4_c0011, na4_c0100, na4_c0101, na4_c0110, na4_c0111, na4_c1000, na4_c1001, na4_c1010, na4_c1011, na4_c1100, na4_c1101, na4_c1110, na4_c1111, napot_c0000, napot_c0001, napot_c0010, napot_c0011, napot_c0100, napot_c0101, napot_c0110, napot_c0111, napot_c1000, napot_c1001, napot_c1010, napot_c1011, napot_c1100, napot_c1101, napot_c1110, napot_c1111
  - cr_lockmix_op = cp_word_lockmix{some} x cp_op: some_csrrw (partial word update), some_csrrs, some_csrrc
  - cr_res_op = cp_res_bits{nonzero} x cp_op: nonzero_csrrw, nonzero_csrrs, nonzero_csrrc
  - cr_prelock_wrl = cp_prelock{unlocked} x cp_wr_lrwx{L=1 rows} x cp_outcome{written} x cp_mml{mml0}: setlock_c1000 (the write that sets L succeeds (pre-write lock state used)), setlock_c1001 (the write that sets L succeeds (pre-write lock state used)), setlock_c1010 (the write that sets L succeeds (pre-write lock state used)), setlock_c1011 (the write that sets L succeeds (pre-write lock state used)), setlock_c1100 (the write that sets L succeeds (pre-write lock state used)), setlock_c1101 (the write that sets L succeeds (pre-write lock state used)), setlock_c1110 (the write that sets L succeeds (pre-write lock state used)), setlock_c1111 (the write that sets L succeeds (pre-write lock state used))
- Adopted (riscv-dv): none
- TP items: TP-PMP-001, TP-PMP-003, TP-PMP-004, TP-PMP-005, TP-PMP-006, TP-PMP-007, TP-PMP-013, TP-PMP-019, TP-PMP-020, TP-PMP-021, TP-PMP-027, TP-PMP-028, TP-PMP-029, TP-PMP-030, TP-PMP-109

### CG-PMP-002: gen_cg_pmp_addr_write
- Features: F-PMP-002, F-PMP-008, F-PMP-009, F-PMP-010, F-PMP-011, F-PMP-012, F-PMP-014, F-PMP-018, F-PMP-028, F-PMP-100
- Sample: RVFI retire of a CSR write instruction whose csr field is pmpaddr0..15; condition: rvfi_trap == 0 and not read-only; anti-vacuity: only pmpaddr writes sample; cp_outcome comes from the readback model's pre-write lock state, so a hit proves the lock/TOR-lock rule was exercised for that index
- Coverpoints:
  - cp_idx = pmpaddr index: bins a0{0}, a1{1}, a2{2}, a3{3}, a4{4}, a5{5}, a6{6}, a7{7}, a8{8}, a9{9}, a10{10}, a11{11}, a12{12}, a13{13}, a14{14}, a15{15}
  - cp_op = csr op class: bins csrrw, csrrs, csrrc
  - cp_self_lock = pmpcfg(i).L & ~RLB before write: bins unlocked{0}, locked{1}
  - cp_next_cfg = entry i+1 state before write: bins next_unlocked_tor{L=0 or RLB, A=TOR}, next_unlocked_other{L=0 or RLB, A!=TOR}, next_locked_tor{L=1, RLB=0, A=TOR}, next_locked_other{L=1, RLB=0, A!=TOR}, top{i == PMPNumRegions-1 (no next entry)}
  - cp_rlb = mseccfg.rlb: bins rlb0{0}, rlb1{1}
  - cp_outcome = model outcome: bins written, ignored_self_lock, ignored_tor_lock
  - cp_hi_bits = wdata[31:30] (physical bits 33:32): bins none{00}, bit30{01}, bit31{10}, both{11}
  - cp_self_mode = pmpcfg(i).A at write: bins off, tor, na4, napot
- Crosses:
  - cr_tor_lock = cp_next_cfg x cp_rlb x cp_outcome (self unlocked): nl_tor_rlb0_ignored (next locked TOR, RLB=0 -> ignored_tor_lock), nl_tor_rlb1_written (RLB lifts the previous-address lock), nl_other_rlb0_written (next locked but not TOR -> written), nu_tor_rlb0_written (next TOR but unlocked -> written), top_rlb0_written (index PMPNumRegions-1 has no next check); ignore nl_tor_rlb0_written: TOR lock always wins when RLB=0; ignore x_rlb1_ignored_tor_lock: no TOR lock when RLB=1
  - cr_self_lock = cp_self_lock x cp_rlb x cp_outcome: locked_rlb0_ignored, locked_rlb1_written, unlocked_rlb0_written; ignore locked_rlb0_written: self lock always wins when RLB=0
  - cr_top_lock = cp_idx{a15 = PMPNumRegions-1} x cp_self_lock x cp_outcome: top_unlocked_written, top_locked_ignored
  - cr_hi_mode = cp_hi_bits{bit30,bit31,both} x cp_self_mode: bit30_off, bit30_tor, bit30_na4, bit30_napot, bit31_off, bit31_tor, bit31_na4, bit31_napot, both_off, both_tor, both_na4, both_napot
  - cr_idx_op = cp_idx x cp_op: 48 required bins: a0_csrrw, a0_csrrs, a0_csrrc, a1_csrrw, a1_csrrs, a1_csrrc, a2_csrrw, a2_csrrs, a2_csrrc, a3_csrrw, a3_csrrs, a3_csrrc, a4_csrrw, a4_csrrs, a4_csrrc, a5_csrrw, a5_csrrs, a5_csrrc, a6_csrrw, a6_csrrs, a6_csrrc, a7_csrrw, a7_csrrs, a7_csrrc, a8_csrrw, a8_csrrs, a8_csrrc, a9_csrrw, a9_csrrs, a9_csrrc, a10_csrrw, a10_csrrs, a10_csrrc, a11_csrrw, a11_csrrs, a11_csrrc, a12_csrrw, a12_csrrs, a12_csrrc, a13_csrrw, a13_csrrs, a13_csrrc, a14_csrrw, a14_csrrs, a14_csrrc, a15_csrrw, a15_csrrs, a15_csrrc
- Adopted (riscv-dv): none
- TP items: TP-PMP-002, TP-PMP-007, TP-PMP-014, TP-PMP-015, TP-PMP-016, TP-PMP-017, TP-PMP-018, TP-PMP-020, TP-PMP-021, TP-PMP-037, TP-PMP-042, TP-PMP-109

### CG-PMP-003: gen_cg_pmp_mseccfg
- Features: F-PMP-013, F-PMP-021, F-PMP-022, F-PMP-023, F-PMP-024, F-PMP-025, F-PMP-026, F-PMP-027, F-PMP-033
- Sample: RVFI retire of a CSR write to mseccfg (0x747) or mseccfgh (0x757), rvfi_trap == 0, not read-only; anti-vacuity: only these two CSRs sample; pre/post state and any_locked come from the readback model, so a hit on a transition bin proves a write attempted that transition under the named lock state
- Coverpoints:
  - cp_csr = target CSR: bins mseccfg{0x747}, mseccfgh{0x757}
  - cp_op = csr op class: bins csrrw, csrrs, csrrc
  - cp_pre = {mml,mmwp,rlb} before write: bins s000, s001, s010, s011, s100, s101, s110, s111
  - cp_post = {mml,mmwp,rlb} after write (readback): bins s000, s001, s010, s011, s100, s101, s110, s111
  - cp_pre_mml = mml before: bins p0, p1
  - cp_pre_mmwp = mmwp before: bins p0, p1
  - cp_pre_rlb = rlb before: bins p0, p1
  - cp_wr_mml = written bit 0 (after RMW combine): bins w0, w1
  - cp_wr_mmwp = written bit 1: bins w0, w1
  - cp_wr_rlb = written bit 2: bins w0, w1
  - cp_any_locked = |(pmpcfg.L & ~RLB) before write: bins none{0}, some{1}
  - cp_locked_off_only = every L=1 entry has A=OFF (iff cp_any_locked=some): bins no, yes
  - cp_hi_bits = written bits [31:3] (mseccfg) or any bit (mseccfgh): bins zero, nonzero
- Crosses:
  - cr_mml_trans = cp_pre_mml x cp_wr_mml (enumerated): mml_0_w0_stay0, mml_0_w1_set, mml_1_w0_hold (sticky: readback stays 1), mml_1_w1_hold
  - cr_mmwp_trans = cp_pre_mmwp x cp_wr_mmwp (enumerated): mmwp_0_w0_stay0, mmwp_0_w1_set, mmwp_1_w0_hold (sticky), mmwp_1_w1_hold
  - cr_rlb_trans = cp_pre_rlb x cp_wr_rlb x cp_any_locked x cp_locked_off_only (enumerated): rlb_0_w1_nolock_set (no locked entry -> RLB becomes 1), rlb_0_w1_locked_blocked (locked entry exists -> stays 0), rlb_0_w1_lockedoff_blocked (only A=OFF locked entries -> still stays 0 (F-PMP-013)), rlb_0_w0_nolock_stay, rlb_0_w0_locked_stay, rlb_1_w0_clear (any_locked is 0 while RLB=1; clear succeeds), rlb_1_w1_hold; ignore rlb_1_x_locked: any_pmp_entry_locked is masked by RLB=1 (rtl 1463,1510)
  - cr_state_trans = cp_pre x cp_post: legal transitions enumerated (MML/MMWP monotone): 36 required bins: s000_to_s000, s000_to_s001, s000_to_s010, s000_to_s011, s000_to_s100, s000_to_s101, s000_to_s110, s000_to_s111, s001_to_s000, s001_to_s001, s001_to_s010, s001_to_s011, s001_to_s100, s001_to_s101, s001_to_s110, s001_to_s111, s010_to_s010, s010_to_s011, s010_to_s110, s010_to_s111, s011_to_s010, s011_to_s011, s011_to_s110, s011_to_s111, s100_to_s100, s100_to_s101, s100_to_s110, s100_to_s111, s101_to_s100, s101_to_s101, s101_to_s110, s101_to_s111, s110_to_s110, s110_to_s111, s111_to_s110, s111_to_s111; ignore any pre with post mml/mmwp lower than pre: sticky bits; contradicts the readback model
  - cr_mseccfgh = cp_csr{mseccfgh} x cp_hi_bits{nonzero} x cp_op: mseccfgh_nonzero_csrrw (readback 0), mseccfgh_nonzero_csrrs (readback 0), mseccfgh_nonzero_csrrc (readback 0)
  - cr_hi_bits = cp_csr{mseccfg} x cp_hi_bits{nonzero}: mseccfg_hi_nonzero (bits 31:3 read back 0)
  - cr_op_trans = cp_op x cr_mml_trans{mml_1_w0_hold} / cr_mmwp_trans{mmwp_1_w0_hold}: csrrw_mml_hold, csrrc_mml_hold, csrrw_mmwp_hold, csrrc_mmwp_hold; ignore csrrs_x_hold: csrrs cannot attempt a clear
- Adopted (riscv-dv): none
- TP items: TP-PMP-007, TP-PMP-011, TP-PMP-012, TP-PMP-019, TP-PMP-022, TP-PMP-023, TP-PMP-024, TP-PMP-025, TP-PMP-026, TP-PMP-031, TP-PMP-108, TP-PMP-109

### CG-PMP-004: gen_cg_pmp_csr_access
- Features: F-PMP-001, F-PMP-002, F-PMP-015, F-PMP-016, F-PMP-017, F-PMP-018, F-PMP-021, F-PMP-022
- Sample: RVFI retire of any CSR instruction whose csr field is in {pmpcfg0..3, pmpaddr0..15, mseccfg, mseccfgh}, including trapped ones (rvfi_trap == 1); anti-vacuity: only PMP CSR instructions sample; a hit proves the access happened in the named privilege/debug state and its trap outcome was compared
- Coverpoints:
  - cp_class = CSR class: bins pmpcfg, pmpaddr, mseccfg, mseccfgh
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_dbg = rvfi_ext_debug_mode: bins d0, d1
  - cp_op = csr op: bins csrrw, csrrs, csrrc, csrrwi, csrrsi, csrrci
  - cp_rw = read-only form (rs1=x0 / uimm=0 for set/clear) vs write: bins read_only, write
  - cp_trap = rvfi_trap and cause: bins none{0}, illegal{cause 2}
  - cp_first_after_reset = no prior write to this CSR since reset: bins no, yes
- Crosses:
  - cr_priv_trap = cp_priv x cp_trap: m_none, u_illegal; ignore m_illegal: PMP CSRs exist and are legal in M; ignore u_none: U access always traps
  - cr_u_class = cp_priv{u} x cp_class x cp_rw: u_pmpcfg_read_only, u_pmpcfg_write, u_pmpaddr_read_only, u_pmpaddr_write, u_mseccfg_read_only, u_mseccfg_write, u_mseccfgh_read_only, u_mseccfgh_write
  - cr_dbg_class = cp_dbg{d1} x cp_class x cp_rw: d1_pmpcfg_read_only, d1_pmpcfg_write, d1_pmpaddr_read_only, d1_pmpaddr_write, d1_mseccfg_read_only, d1_mseccfg_write, d1_mseccfgh_read_only, d1_mseccfgh_write
  - cr_reset_read = cp_first_after_reset{yes} x cp_class x cp_rw{read_only}: rst_pmpcfg (readback == ibex_pkg reset value), rst_pmpaddr (readback == ibex_pkg reset value), rst_mseccfg (readback == ibex_pkg reset value), rst_mseccfgh (readback == ibex_pkg reset value)
  - cr_op_class = cp_op x cp_class: csrrw_pmpcfg, csrrw_pmpaddr, csrrw_mseccfg, csrrw_mseccfgh, csrrs_pmpcfg, csrrs_pmpaddr, csrrs_mseccfg, csrrs_mseccfgh, csrrc_pmpcfg, csrrc_pmpaddr, csrrc_mseccfg, csrrc_mseccfgh, csrrwi_pmpcfg, csrrwi_pmpaddr, csrrwi_mseccfg, csrrwi_mseccfgh, csrrsi_pmpcfg, csrrsi_pmpaddr, csrrsi_mseccfg, csrrsi_mseccfgh, csrrci_pmpcfg, csrrci_pmpaddr, csrrci_mseccfg, csrrci_mseccfgh
- Adopted (riscv-dv): none
- TP items: TP-PMP-001, TP-PMP-002, TP-PMP-007, TP-PMP-008, TP-PMP-009, TP-PMP-010, TP-PMP-011, TP-PMP-012, TP-PMP-104

### CG-PMP-005: gen_cg_pmp_access_verdict
- Features: F-PMP-034, F-PMP-045, F-PMP-047, F-PMP-049, F-PMP-050, F-PMP-051, F-PMP-052, F-PMP-054, F-PMP-056, F-PMP-057, F-PMP-058, F-PMP-059, F-PMP-060, F-PMP-061, F-PMP-062, F-PMP-063, F-PMP-064, F-PMP-071
- Sample: every PMP check performed by the gen_chk_pmp model: (a) fetch: per rvfi_valid retire on rvfi_pc_rdata with priv = rvfi_mode (M in debug mode) and type EXEC; (b) second fetch half: when the retired instruction is uncompressed and pc[1] = 1, a second sample on pc + 2; (c) data: per word of each retired load/store (rvfi_mem_rmask/wmask != 0; a split misaligned access gives two samples) with priv = mstatus.MPRV ? MPP : rvfi_mode and type from rvfi_mem_wmask; anti-vacuity: every retire samples, but the match/lrwx/region fields are only non-trivial when a configured region decides the access, so a hit on a match bin proves a live region of that config decided an access of that type and privilege and the verdict was checked against rvfi_trap / bus activity
- Coverpoints:
  - cp_type = access type: bins fetch, load, store
  - cp_priv = effective privilege: bins m, u
  - cp_mml = mseccfg.mml: bins mml0, mml1
  - cp_mmwp = mseccfg.mmwp: bins mmwp0, mmwp1
  - cp_match = any region matches: bins nomatch, match
  - cp_lrwx = {L,R,W,X} of the lowest matching region (iff match): bins c0000{0000}, c0001{0001}, c0010{0010}, c0011{0011}, c0100{0100}, c0101{0101}, c0110{0110}, c0111{0111}, c1000{1000}, c1001{1001}, c1010{1010}, c1011{1011}, c1100{1100}, c1101{1101}, c1110{1110}, c1111{1111}
  - cp_verdict = model verdict: bins allow, deny
  - cp_region = index of the deciding region (iff match): bins r0{0}, r1{1}, r2{2}, r3{3}, r4{4}, r5{5}, r6{6}, r7{7}, r8{8}, r9{9}, r10{10}, r11{11}, r12{12}, r13{13}, r14{14}, r15{15}
  - cp_mode = A field of the deciding region (iff match): bins tor, na4, napot; ignore_bins off: an OFF entry never matches (F-PMP-034)
  - cp_off_shadow = iff nomatch: an A=OFF entry's pmpaddr range would cover the address if enabled: bins none, off_covers
- Crosses:
  - cr_truth_mml1 = cp_mml{mml1} x cp_match{match} x cp_lrwx x cp_priv x cp_type x cp_verdict (Smepmp truth table): 96 required bins: c0000_m_fetch, c0000_m_load, c0000_m_store, c0000_u_fetch, c0000_u_load, c0000_u_store, c0001_m_fetch, c0001_m_load, c0001_m_store, c0001_u_fetch, c0001_u_load, c0001_u_store, c0010_m_fetch, c0010_m_load, c0010_m_store, c0010_u_fetch, c0010_u_load, c0010_u_store, c0011_m_fetch, c0011_m_load, c0011_m_store, c0011_u_fetch, c0011_u_load, c0011_u_store, c0100_m_fetch, c0100_m_load, c0100_m_store, c0100_u_fetch, c0100_u_load, c0100_u_store, c0101_m_fetch, c0101_m_load, c0101_m_store, c0101_u_fetch, c0101_u_load, c0101_u_store, c0110_m_fetch, c0110_m_load, c0110_m_store, c0110_u_fetch, c0110_u_load, c0110_u_store, c0111_m_fetch, c0111_m_load, c0111_m_store, c0111_u_fetch, c0111_u_load, c0111_u_store, c1000_m_fetch, c1000_m_load, c1000_m_store, c1000_u_fetch, c1000_u_load, c1000_u_store, c1001_m_fetch, c1001_m_load, c1001_m_store, c1001_u_fetch, c1001_u_load, c1001_u_store, c1010_m_fetch, c1010_m_load, c1010_m_store, c1010_u_fetch, c1010_u_load, c1010_u_store, c1011_m_fetch, c1011_m_load, c1011_m_store, c1011_u_fetch, c1011_u_load, c1011_u_store, c1100_m_fetch, c1100_m_load, c1100_m_store, c1100_u_fetch, c1100_u_load, c1100_u_store, c1101_m_fetch, c1101_m_load, c1101_m_store, c1101_u_fetch, c1101_u_load, c1101_u_store, c1110_m_fetch, c1110_m_load, c1110_m_store, c1110_u_fetch, c1110_u_load, c1110_u_store, c1111_m_fetch, c1111_m_load, c1111_m_store, c1111_u_fetch, c1111_u_load, c1111_u_store; ignore any row with the opposite verdict: contradicts smepmp.adoc; gen_chk_pmp fails before the sample
  - cr_truth_mml0 = cp_mml{mml0} x cp_match{match} x cp_lrwx x cp_priv x cp_type x cp_verdict (original PMP): 72 required bins: c0000_m_fetch, c0000_m_load, c0000_m_store, c0000_u_fetch, c0000_u_load, c0000_u_store, c0001_m_fetch, c0001_m_load, c0001_m_store, c0001_u_fetch, c0001_u_load, c0001_u_store, c0100_m_fetch, c0100_m_load, c0100_m_store, c0100_u_fetch, c0100_u_load, c0100_u_store, c0101_m_fetch, c0101_m_load, c0101_m_store, c0101_u_fetch, c0101_u_load, c0101_u_store, c0110_m_fetch, c0110_m_load, c0110_m_store, c0110_u_fetch, c0110_u_load, c0110_u_store, c0111_m_fetch, c0111_m_load, c0111_m_store, c0111_u_fetch, c0111_u_load, c0111_u_store, c1000_m_fetch, c1000_m_load, c1000_m_store, c1000_u_fetch, c1000_u_load, c1000_u_store, c1001_m_fetch, c1001_m_load, c1001_m_store, c1001_u_fetch, c1001_u_load, c1001_u_store, c1100_m_fetch, c1100_m_load, c1100_m_store, c1100_u_fetch, c1100_u_load, c1100_u_store, c1101_m_fetch, c1101_m_load, c1101_m_store, c1101_u_fetch, c1101_u_load, c1101_u_store, c1110_m_fetch, c1110_m_load, c1110_m_store, c1110_u_fetch, c1110_u_load, c1110_u_store, c1111_m_fetch, c1111_m_load, c1111_m_store, c1111_u_fetch, c1111_u_load, c1111_u_store; ignore c0010,c0011,c1010,c1011 rows: RW=01 is not storable while MML=0 (F-PMP-004) and MML is sticky; ignore any row with the opposite verdict: contradicts machine.adoc Locking and Privilege Mode
  - cr_nomatch = cp_match{nomatch} x cp_priv x cp_type x cp_mml x cp_mmwp x cp_verdict: nm_m_fetch_mml0_mmwp0 (verdict allow), nm_m_fetch_mml0_mmwp1 (verdict deny), nm_m_fetch_mml1_mmwp0 (verdict deny), nm_m_fetch_mml1_mmwp1 (verdict deny), nm_m_load_mml0_mmwp0 (verdict allow), nm_m_load_mml0_mmwp1 (verdict deny), nm_m_load_mml1_mmwp0 (verdict allow), nm_m_load_mml1_mmwp1 (verdict deny), nm_m_store_mml0_mmwp0 (verdict allow), nm_m_store_mml0_mmwp1 (verdict deny), nm_m_store_mml1_mmwp0 (verdict allow), nm_m_store_mml1_mmwp1 (verdict deny), nm_u_fetch_mml0_mmwp0 (verdict deny), nm_u_fetch_mml0_mmwp1 (verdict deny), nm_u_fetch_mml1_mmwp0 (verdict deny), nm_u_fetch_mml1_mmwp1 (verdict deny), nm_u_load_mml0_mmwp0 (verdict deny), nm_u_load_mml0_mmwp1 (verdict deny), nm_u_load_mml1_mmwp0 (verdict deny), nm_u_load_mml1_mmwp1 (verdict deny), nm_u_store_mml0_mmwp0 (verdict deny), nm_u_store_mml0_mmwp1 (verdict deny), nm_u_store_mml1_mmwp0 (verdict deny), nm_u_store_mml1_mmwp1 (verdict deny); ignore opposite verdict: contradicts the no-match rules
  - cr_mode_type_priv_mml = cp_mode x cp_type x cp_priv x cp_mml x cp_verdict: 72 required bins: tor_fetch_m_mml0_allow, tor_fetch_m_mml0_deny, tor_fetch_m_mml1_allow, tor_fetch_m_mml1_deny, tor_fetch_u_mml0_allow, tor_fetch_u_mml0_deny, tor_fetch_u_mml1_allow, tor_fetch_u_mml1_deny, tor_load_m_mml0_allow, tor_load_m_mml0_deny, tor_load_m_mml1_allow, tor_load_m_mml1_deny, tor_load_u_mml0_allow, tor_load_u_mml0_deny, tor_load_u_mml1_allow, tor_load_u_mml1_deny, tor_store_m_mml0_allow, tor_store_m_mml0_deny, tor_store_m_mml1_allow, tor_store_m_mml1_deny, tor_store_u_mml0_allow, tor_store_u_mml0_deny, tor_store_u_mml1_allow, tor_store_u_mml1_deny, na4_fetch_m_mml0_allow, na4_fetch_m_mml0_deny, na4_fetch_m_mml1_allow, na4_fetch_m_mml1_deny, na4_fetch_u_mml0_allow, na4_fetch_u_mml0_deny, na4_fetch_u_mml1_allow, na4_fetch_u_mml1_deny, na4_load_m_mml0_allow, na4_load_m_mml0_deny, na4_load_m_mml1_allow, na4_load_m_mml1_deny, na4_load_u_mml0_allow, na4_load_u_mml0_deny, na4_load_u_mml1_allow, na4_load_u_mml1_deny, na4_store_m_mml0_allow, na4_store_m_mml0_deny, na4_store_m_mml1_allow, na4_store_m_mml1_deny, na4_store_u_mml0_allow, na4_store_u_mml0_deny, na4_store_u_mml1_allow, na4_store_u_mml1_deny, napot_fetch_m_mml0_allow, napot_fetch_m_mml0_deny, napot_fetch_m_mml1_allow, napot_fetch_m_mml1_deny, napot_fetch_u_mml0_allow, napot_fetch_u_mml0_deny, napot_fetch_u_mml1_allow, napot_fetch_u_mml1_deny, napot_load_m_mml0_allow, napot_load_m_mml0_deny, napot_load_m_mml1_allow, napot_load_m_mml1_deny, napot_load_u_mml0_allow, napot_load_u_mml0_deny, napot_load_u_mml1_allow, napot_load_u_mml1_deny, napot_store_m_mml0_allow, napot_store_m_mml0_deny, napot_store_m_mml1_allow, napot_store_m_mml1_deny, napot_store_u_mml0_allow, napot_store_u_mml0_deny, napot_store_u_mml1_allow, napot_store_u_mml1_deny
  - cr_region_type = cp_region x cp_type: 48 required bins: r0_fetch, r0_load, r0_store, r1_fetch, r1_load, r1_store, r2_fetch, r2_load, r2_store, r3_fetch, r3_load, r3_store, r4_fetch, r4_load, r4_store, r5_fetch, r5_load, r5_store, r6_fetch, r6_load, r6_store, r7_fetch, r7_load, r7_store, r8_fetch, r8_load, r8_store, r9_fetch, r9_load, r9_store, r10_fetch, r10_load, r10_store, r11_fetch, r11_load, r11_store, r12_fetch, r12_load, r12_store, r13_fetch, r13_load, r13_store, r14_fetch, r14_load, r14_store, r15_fetch, r15_load, r15_store
  - cr_region_mode = cp_region x cp_mode: 48 required bins: r0_tor, r0_na4, r0_napot, r1_tor, r1_na4, r1_napot, r2_tor, r2_na4, r2_napot, r3_tor, r3_na4, r3_napot, r4_tor, r4_na4, r4_napot, r5_tor, r5_na4, r5_napot, r6_tor, r6_na4, r6_napot, r7_tor, r7_na4, r7_napot, r8_tor, r8_na4, r8_napot, r9_tor, r9_na4, r9_napot, r10_tor, r10_na4, r10_napot, r11_tor, r11_na4, r11_napot, r12_tor, r12_na4, r12_napot, r13_tor, r13_na4, r13_napot, r14_tor, r14_na4, r14_napot, r15_tor, r15_na4, r15_napot
  - cr_off_shadow = cp_off_shadow{off_covers} x cp_type x cp_priv: off_covers_fetch_m, off_covers_fetch_u, off_covers_load_m, off_covers_load_u, off_covers_store_m, off_covers_store_u
- Adopted (riscv-dv): none
- TP items: TP-PMP-006, TP-PMP-010, TP-PMP-031, TP-PMP-032, TP-PMP-045, TP-PMP-046, TP-PMP-047, TP-PMP-048, TP-PMP-049, TP-PMP-050, TP-PMP-051, TP-PMP-052, TP-PMP-054, TP-PMP-055, TP-PMP-056, TP-PMP-057, TP-PMP-058, TP-PMP-059, TP-PMP-060, TP-PMP-061, TP-PMP-062, TP-PMP-063, TP-PMP-069, TP-PMP-100, TP-PMP-101, TP-PMP-102, TP-PMP-106

### CG-PMP-006: gen_cg_pmp_priority
- Features: F-PMP-045, F-PMP-046, F-PMP-047
- Sample: a CG-PMP-005 check event where the model finds two or more matching regions for the address; anti-vacuity: single-match and no-match accesses never sample; a hit proves an overlapping configuration was exercised by a real access and the lowest index decided
- Coverpoints:
  - cp_nmatch = number of matching regions: bins two{2}, three{3}, four_plus{>=4}
  - cp_dist = index distance between the two lowest matching regions: bins d1{1}, d2_3{2..3}, d4_7{4..7}, d8_15{8..PMPNumRegions-1}
  - cp_conflict = verdict of lowest vs second-lowest matching region: bins low_allow_high_deny{override: access allowed}, low_deny_high_allow{access denied}, agree_allow, agree_deny
  - cp_low_idx = lowest matching index: bins r0{0}, r1_7{1..7}, r8_14{8..PMPNumRegions-2}; ignore_bins r15: cannot be lowest of two matches
  - cp_high_is_top = highest matching index == PMPNumRegions-1: bins no, yes
  - cp_type = access type: bins fetch, load, store
  - cp_priv = effective privilege: bins m, u
  - cp_mode_pair = modes of the two lowest matching regions (na = NA4 or NAPOT): bins tor_tor, tor_na, na_tor, na_na
  - cp_mml = mseccfg.mml: bins mml0, mml1
- Crosses:
  - cr_conflict_dist = cp_conflict x cp_dist: low_allow_high_deny_d1, low_allow_high_deny_d2_3, low_allow_high_deny_d4_7, low_allow_high_deny_d8_15, low_deny_high_allow_d1, low_deny_high_allow_d2_3, low_deny_high_allow_d4_7, low_deny_high_allow_d8_15, agree_allow_d1, agree_allow_d2_3, agree_allow_d4_7, agree_allow_d8_15, agree_deny_d1, agree_deny_d2_3, agree_deny_d4_7, agree_deny_d8_15
  - cr_conflict_type = cp_conflict x cp_type: low_allow_high_deny_fetch, low_allow_high_deny_load, low_allow_high_deny_store, low_deny_high_allow_fetch, low_deny_high_allow_load, low_deny_high_allow_store, agree_allow_fetch, agree_allow_load, agree_allow_store, agree_deny_fetch, agree_deny_load, agree_deny_store
  - cr_conflict_top = cp_conflict x cp_high_is_top{yes}: low_allow_high_deny_top (entry PMPNumRegions-1 is the overridden/agreeing one), low_deny_high_allow_top (entry PMPNumRegions-1 is the overridden/agreeing one), agree_allow_top (entry PMPNumRegions-1 is the overridden/agreeing one), agree_deny_top (entry PMPNumRegions-1 is the overridden/agreeing one)
  - cr_conflict_mode = cp_conflict x cp_mode_pair: low_allow_high_deny_tor_tor, low_allow_high_deny_tor_na, low_allow_high_deny_na_tor, low_allow_high_deny_na_na, low_deny_high_allow_tor_tor, low_deny_high_allow_tor_na, low_deny_high_allow_na_tor, low_deny_high_allow_na_na, agree_allow_tor_tor, agree_allow_tor_na, agree_allow_na_tor, agree_allow_na_na, agree_deny_tor_tor, agree_deny_tor_na, agree_deny_na_tor, agree_deny_na_na
  - cr_conflict_mml_priv = cp_conflict x cp_mml x cp_priv: low_allow_high_deny_mml0_m, low_allow_high_deny_mml0_u, low_allow_high_deny_mml1_m, low_allow_high_deny_mml1_u, low_deny_high_allow_mml0_m, low_deny_high_allow_mml0_u, low_deny_high_allow_mml1_m, low_deny_high_allow_mml1_u, agree_allow_mml0_m, agree_allow_mml0_u, agree_allow_mml1_m, agree_allow_mml1_u, agree_deny_mml0_m, agree_deny_mml0_u, agree_deny_mml1_m, agree_deny_mml1_u
  - cr_nmatch_low = cp_nmatch x cp_low_idx: two_r0, two_r1_7, two_r8_14, three_r0, three_r1_7, three_r8_14, four_plus_r0, four_plus_r1_7, four_plus_r8_14
- Adopted (riscv-dv): none
- TP items: TP-PMP-043, TP-PMP-044, TP-PMP-045, TP-PMP-100, TP-PMP-101, TP-PMP-102, TP-PMP-110

### CG-PMP-007: gen_cg_pmp_boundary
- Features: F-PMP-014, F-PMP-035, F-PMP-036, F-PMP-037, F-PMP-038, F-PMP-039, F-PMP-040, F-PMP-041, F-PMP-042, F-PMP-043, F-PMP-044, F-PMP-048
- Sample: a CG-PMP-005 check event for which the model identifies a reference region: the deciding region on match, else the enabled region whose first or last byte lies within 4 bytes of the access bytes (nomatch case); condition: such a region exists; anti-vacuity: accesses far from any region edge never sample; a hit proves an access at or across an exact region edge of that mode and the verdict matched the model
- Coverpoints:
  - cp_mode = reference region A field: bins tor, na4, napot
  - cp_bclass = position of the access bytes relative to the region: bins inside_low{first access byte == region first byte}, inside_high{last access byte == region last byte}, interior{strictly inside, not touching an edge}, outside_low{last access byte == region first byte - 1}, outside_high{first access byte == region last byte + 1}, straddle_low{access bytes span the region's lower edge (split misaligned or i32 at 4n+2)}, straddle_high{access bytes span the upper edge}
  - cp_type = access type: bins fetch, load, store
  - cp_size = access size: bins b8{byte}, h16{halfword}, w32{word}, c16{compressed fetch}, i32{32-bit fetch}
  - cp_napot_k = iff napot: trailing-ones count k of pmpaddr, size 2^(3+k) bytes: bins k0{8 B}, k1{16 B}, k2{32 B}, k3_7{64 B .. 1 KiB}, k8_17{2 KiB .. 1 MiB}, k18_28{2 MiB .. 2 GiB}, k29{4 GiB (pmpaddr 0x1FFFFFFF)}, k30{8 GiB (0x3FFFFFFF)}, k31{16 GiB (0x7FFFFFFF)}, k32{all ones (0xFFFFFFFF)}
  - cp_tor_zero = iff tor: reference region is entry 0 (lower bound 0): bins no, yes
  - cp_tor_empty = iff tor: pmpaddr(i-1) vs pmpaddr(i): bins nonempty{lt}, empty_eq{eq}, empty_gt{gt}
  - cp_hi = pmpaddr bits [31:30] set on base (start) or bound (TOR end): bins none, base_hi30, base_hi31, bound_hi30, bound_hi31
  - cp_prev_cfg = iff tor and i>0: entry i-1 state: bins prev_off, prev_tor, prev_na, prev_locked
- Crosses:
  - cr_mode_bclass = cp_mode x cp_bclass: tor_inside_low, tor_inside_high, tor_interior, tor_outside_low, tor_outside_high, tor_straddle_low, tor_straddle_high, na4_inside_low, na4_inside_high, na4_interior, na4_outside_low, na4_outside_high, na4_straddle_low, na4_straddle_high, napot_inside_low, napot_inside_high, napot_interior, napot_outside_low, napot_outside_high, napot_straddle_low, napot_straddle_high
  - cr_mode_bclass_type = cp_mode x cp_bclass x cp_type: 63 required bins: tor_inside_low_fetch, tor_inside_low_load, tor_inside_low_store, tor_inside_high_fetch, tor_inside_high_load, tor_inside_high_store, tor_interior_fetch, tor_interior_load, tor_interior_store, tor_outside_low_fetch, tor_outside_low_load, tor_outside_low_store, tor_outside_high_fetch, tor_outside_high_load, tor_outside_high_store, tor_straddle_low_fetch, tor_straddle_low_load, tor_straddle_low_store, tor_straddle_high_fetch, tor_straddle_high_load, tor_straddle_high_store, na4_inside_low_fetch, na4_inside_low_load, na4_inside_low_store, na4_inside_high_fetch, na4_inside_high_load, na4_inside_high_store, na4_interior_fetch, na4_interior_load, na4_interior_store, na4_outside_low_fetch, na4_outside_low_load, na4_outside_low_store, na4_outside_high_fetch, na4_outside_high_load, na4_outside_high_store, na4_straddle_low_fetch, na4_straddle_low_load, na4_straddle_low_store, na4_straddle_high_fetch, na4_straddle_high_load, na4_straddle_high_store, napot_inside_low_fetch, napot_inside_low_load, napot_inside_low_store, napot_inside_high_fetch, napot_inside_high_load, napot_inside_high_store, napot_interior_fetch, napot_interior_load, napot_interior_store, napot_outside_low_fetch, napot_outside_low_load, napot_outside_low_store, napot_outside_high_fetch, napot_outside_high_load, napot_outside_high_store, napot_straddle_low_fetch, napot_straddle_low_load, napot_straddle_low_store, napot_straddle_high_fetch, napot_straddle_high_load, napot_straddle_high_store
  - cr_napot_k_bclass = cp_napot_k x cp_bclass{inside_low,inside_high,outside_low,outside_high}: 32 required bins: k0_inside_low, k0_inside_high, k0_outside_low, k0_outside_high, k1_inside_low, k1_inside_high, k1_outside_low, k1_outside_high, k2_inside_low, k2_inside_high, k2_outside_low, k2_outside_high, k3_7_inside_low, k3_7_inside_high, k3_7_outside_low, k3_7_outside_high, k8_17_inside_low, k8_17_inside_high, k8_17_outside_low, k8_17_outside_high, k18_28_inside_low, k18_28_inside_high, k18_28_outside_low, k18_28_outside_high, k29_inside_low, k29_inside_high, k30_inside_low, k30_inside_high, k31_inside_low, k31_inside_high, k32_inside_low, k32_inside_high; ignore k29..k32 x outside_low/outside_high: mask covers address bits 2..31: the region is the whole 32-bit space, no outside byte exists
  - cr_tor_zero = cp_tor_zero{yes} x cp_bclass: zero_inside_low, zero_inside_high, zero_interior, zero_outside_low, zero_outside_high, zero_straddle_low, zero_straddle_high; ignore zero_outside_low: no byte below address 0; ignore zero_straddle_low: no byte below address 0
  - cr_tor_empty = cp_tor_empty{empty_eq,empty_gt} x cp_type (access inside [addr(i), addr(i-1)) -> nomatch): empty_eq_fetch, empty_eq_load, empty_eq_store, empty_gt_fetch, empty_gt_load, empty_gt_store
  - cr_hi_mode = cp_hi{base/bound hi} x cp_mode: napot_base_hi30 (never matches unless mask covers), napot_base_hi31, na4_base_hi30 (never matches), na4_base_hi31, tor_bound_hi30 (matches every 32-bit address >= start), tor_bound_hi31, tor_base_hi30 (empty for 32-bit addresses), tor_base_hi31; ignore na4/napot bound_hi: NA modes have no separate bound
  - cr_size_bclass = cp_size x cp_bclass{inside_low,inside_high,straddle_low,straddle_high}: b8_inside_low, b8_inside_high, b8_straddle_low, b8_straddle_high, h16_inside_low, h16_inside_high, h16_straddle_low, h16_straddle_high, w32_inside_low, w32_inside_high, w32_straddle_low, w32_straddle_high, c16_inside_low, c16_inside_high, c16_straddle_low, c16_straddle_high, i32_inside_low, i32_inside_high, i32_straddle_low, i32_straddle_high; ignore b8/c16 x straddle: single-granule accesses cannot straddle; ignore w32 x straddle for aligned words: only misaligned words straddle; sampled under the same bin when addr[1:0] != 0
  - cr_prev_cfg = cp_mode{tor} x cp_prev_cfg: tor_prev_off, tor_prev_tor, tor_prev_na, tor_prev_locked
  - cr_na4_size = cp_mode{na4} x cp_size{b8,h16,w32} x cp_bclass{inside_low,inside_high,interior}: na4_b8_inside_low, na4_b8_inside_high, na4_b8_interior, na4_h16_inside_low, na4_h16_inside_high, na4_h16_interior, na4_w32_inside_low, na4_w32_inside_high, na4_w32_interior; ignore na4_w32_interior: a word access fills the 4-byte NA4 region; it is inside_low and inside_high at once, sampled as inside_low
- Adopted (riscv-dv): none
- TP items: TP-PMP-033, TP-PMP-034, TP-PMP-035, TP-PMP-036, TP-PMP-037, TP-PMP-038, TP-PMP-039, TP-PMP-040, TP-PMP-041, TP-PMP-042, TP-PMP-065, TP-PMP-084, TP-PMP-103

### CG-PMP-008: gen_cg_pmp_data_fault
- Features: F-PMP-071, F-PMP-082, F-PMP-083, F-PMP-084, F-PMP-085, F-PMP-086, F-PMP-087, F-PMP-088, F-PMP-089, F-PMP-090, F-PMP-091
- Sample: rvfi_valid of a load/store instruction for which the model predicts a PMP denial on at least one word, or whose access is split misaligned (word at offset 1/2/3, halfword at offset 3); condition: one of the two; anti-vacuity: aligned permitted accesses never sample; a hit proves a denied or split data access was checked for bus activity (data_req_o count), trap cause and mtval readback
- Coverpoints:
  - cp_type = load/store: bins load, store
  - cp_align = split/denial pattern: bins aligned_denied{single word denied}, mis_none{split, both allowed}, mis_first{split, first word denied only}, mis_second{split, second word denied only}, mis_both{split, both denied}
  - cp_size = access size: bins b8, h16, w32; ignore_bins b8 with mis_*: bytes never split
  - cp_cause = rvfi_trap cause (mcause readback): bins none, c5{load access fault}, c7{store access fault}
  - cp_mtval = iff trap: mtval readback class: bins ea{original effective address}, second_word{word-aligned second address}
  - cp_nreq = data_req_o & data_gnt_i count attributed to the instruction: bins n0, n1, n2
  - cp_eff_priv = MPRV ? MPP : mode: bins m, u
  - cp_mprv = mstatus.mprv: bins mprv0, mprv1
  - cp_rd = loads: rvfi_rd_addr != 0 with write: bins none, written
  - cp_buserr = data_err_i on the first half response: bins none, first_half_err
  - cp_next_exc = exception class of the following instruction while this one faults in WB: bins none, fetch_fault{PMP-denied fetch in ID}, illegal, ecall_ebreak
  - cp_lat = PROBE: cycles from LSU request to lsu_resp_valid for aligned_denied: bins lat2{2}, other
- Crosses:
  - cr_align_type = cp_align x cp_type: aligned_denied_load, aligned_denied_store, mis_none_load, mis_none_store, mis_first_load, mis_first_store, mis_second_load, mis_second_store, mis_both_load, mis_both_store
  - cr_align_mtval = cp_align x cp_mtval (trapping accesses): aligned_denied_ea, mis_first_ea (first-half fault keeps the original EA), mis_second_second_word, mis_both_ea; ignore mis_first_second_word: addr_update blocked by pmp_err_q; ignore aligned_denied_second_word: no second word; ignore mis_second_ea: second-half fault records the aligned second address
  - cr_align_nreq = cp_align x cp_nreq: aligned_denied_n0 (no bus transaction), mis_none_n2, mis_first_n1 (second half still issued (MEM-13, Q-DL-7)), mis_second_n1 (first half performed), mis_both_n0; ignore other combinations: contradict MEM-13; gen_chk_pmp / gen_chk_dbus_proto fail first
  - cr_half_align = cp_size{h16} x cp_align{mis_*} x cp_type: h16_mis_none_load, h16_mis_none_store, h16_mis_first_load, h16_mis_first_store, h16_mis_second_load, h16_mis_second_store, h16_mis_both_load, h16_mis_both_store
  - cr_buserr = cp_buserr{first_half_err} x cp_align{mis_second} x cp_type x cp_mtval{ea}: buserr_mis_second_load_ea, buserr_mis_second_store_ea
  - cr_priority = cp_cause{c5,c7} x cp_next_exc{fetch_fault,illegal,ecall_ebreak}: c5_fetch_fault, c5_illegal, c5_ecall_ebreak, c7_fetch_fault, c7_illegal, c7_ecall_ebreak
  - cr_priv_cause = cp_mprv x cp_eff_priv x cp_cause{c5,c7}: mprv0_m_c5, mprv0_m_c7, mprv0_u_c5, mprv0_u_c7, mprv1_m_c5, mprv1_m_c7, mprv1_u_c5, mprv1_u_c7
  - cr_rd = cp_type{load} x cp_cause{c5} x cp_rd: load_c5_none (denied load writes no rd); ignore load_c5_written: contradicts F-PMP-083; gen_isa_compare fails first
  - cr_lat = cp_align{aligned_denied} x cp_lat: aligned_denied_lat2 (PROBE candidate)
- Adopted (riscv-dv): none
- TP items: TP-PMP-069, TP-PMP-070, TP-PMP-080, TP-PMP-081, TP-PMP-082, TP-PMP-083, TP-PMP-084, TP-PMP-085, TP-PMP-086, TP-PMP-087, TP-PMP-088, TP-PMP-089, TP-PMP-103

### CG-PMP-009: gen_cg_pmp_fetch_fault
- Features: F-PMP-053, F-PMP-055, F-PMP-065, F-PMP-066, F-PMP-067, F-PMP-068, F-PMP-069, F-PMP-070, F-PMP-078, F-PMP-080, F-PMP-081, F-PMP-093, F-PMP-094
- Sample: rvfi_valid per instruction where the model predicts a fetch denial on pc or pc+2, or the instruction is uncompressed at pc[1] = 1 with a region edge at pc+2, or the instruction is a control-flow target whose word is a region edge; condition: one of the three; anti-vacuity: ordinary permitted sequential instructions never sample; a hit proves a fetch-side PMP decision with the named half pattern was checked for trap, mtval and mepc
- Coverpoints:
  - cp_pc_align = pc[1:0]: bins a4{00}, a2{10}
  - cp_ilen = instruction length: bins c16, i32
  - cp_halves = model verdict per half (second half only for i32 at a2): bins single_allow, single_deny, both_allow, fd_sa{first denied, second allowed}, fa_sd{first allowed, second denied}, both_deny
  - cp_next_word_denied = iff c16 at a2: word pc+2 denied for EXEC: bins no, yes
  - cp_mtval = iff trap: mtval readback: bins pc, pc2{pc + 2}
  - cp_cause = rvfi_trap cause: bins none, c1{instruction access fault}
  - cp_buserr = instr_err_i on the fetch of this instruction: bins none, first{first word}, second{second word}
  - cp_target = how pc was reached: bins seq, branch, jump, mret, exc_entry{trap vector}, dret
  - cp_priv = rvfi_mode: bins m, u
  - cp_wrap = pc == 32'hFFFFFFFE: bins normal, wrap
  - cp_dummy_en = cpuctrlsts.dummy_instr_en: bins off, on
  - cp_src = instruction word seen on ibus since the last flush/invalidation: bins bus, cache_hit{no ibus fetch: served by the icache}
- Crosses:
  - cr_plus2 = cp_ilen{i32} x cp_pc_align{a2} x cp_halves{fd_sa,fa_sd,both_deny} x cp_mtval: fd_sa_pc, fa_sd_pc2 (err_plus2: mtval = pc + 2), both_deny_pc (first-half error masks plus2); ignore fd_sa_pc2: masked by ~pmp_err_if_i; ignore both_deny_pc2: masked by ~pmp_err_if_i
  - cr_c16_a2 = cp_ilen{c16} x cp_pc_align{a2} x cp_next_word_denied{yes} x cp_cause: c16_a2_nextdenied_none (compressed instruction uses PMP_I only); ignore c16_a2_nextdenied_c1: contradicts F-PMP-067
  - cr_target = cp_target x cp_cause{c1}: seq_c1 (mepc == target pc), branch_c1 (mepc == target pc), jump_c1 (mepc == target pc), mret_c1 (mepc == target pc), exc_entry_c1 (mepc == target pc), dret_c1 (mepc == target pc)
  - cr_buserr = cp_buserr x cp_halves x cp_mtval: bus_first_fd_sa_pc, bus_second_fd_sa_pc (bus err_plus2 masked by first-half PMP error), bus_second_single_allow_pc2 (pure bus error path, IMEM area reference), bus_first_fa_sd_pc (first-half bus error wins: mtval pc), bus_none_fa_sd_pc2; ignore bus_second_fd_sa_pc2: masked by ~pmp_err_if_i
  - cr_wrap = cp_wrap{wrap} x cp_ilen{i32} x cp_cause: wrap_i32_none (word 0 allowed), wrap_i32_c1 (word 0 denied: mtval pc + 2 = 0)
  - cr_dummy = cp_dummy_en{on} x cp_cause{c1} x cp_pc_align: on_c1_a4, on_c1_a2
  - cr_src = cp_src{cache_hit} x cp_cause: cache_hit_none (cached line executed after PMP made it allowed), cache_hit_c1 (cached line faults after PMP made it denied)
  - cr_priv_cause = cp_priv x cp_cause{c1} x cp_ilen: m_c1_c16, m_c1_i32, u_c1_c16, u_c1_i32
  - cr_halves_priv = cp_halves{single_deny,fd_sa,fa_sd,both_deny} x cp_priv: single_deny_m, single_deny_u, fd_sa_m, fd_sa_u, fa_sd_m, fa_sd_u, both_deny_m, both_deny_u
- Adopted (riscv-dv): none
- TP items: TP-PMP-051, TP-PMP-053, TP-PMP-063, TP-PMP-064, TP-PMP-065, TP-PMP-066, TP-PMP-067, TP-PMP-068, TP-PMP-076, TP-PMP-078, TP-PMP-079, TP-PMP-092, TP-PMP-093, TP-PMP-105

### CG-PMP-010: gen_cg_pmp_ibus_denied
- Features: F-PMP-066, F-PMP-079, F-PMP-092, F-PMP-093
- Sample: ibus monitor: instr_req_o & instr_gnt_i for a word that the model's PMP state at the grant cycle (CSR values, rvfi_mode of the last retire, M in debug) denies for EXEC; anti-vacuity: fetches into currently permitted words never sample; a hit proves that fetch is not gated by PMP and records what became of the fetched word
- Coverpoints:
  - cp_outcome = fate of the fetched word: bins retired_fault{an instruction from the word retires with cause 1}, discarded{never retires}, retired_ok_recfg{retires without trap: a PMP CSR write between grant and handoff allowed it}, retired_ok_priv{retires without trap: privilege changed between grant and handoff}
  - cp_priv = privilege at grant: bins m, u
  - cp_flush_reason = iff discarded: cause of the discard: bins branch, jump, exc{trap/mret/dret redirect}, csr_flush{PMP CSR write flush}
  - cp_later_hit = the same word executes later with no ibus fetch (icache hit): bins no, yes
- Crosses:
  - cr_outcome_priv = cp_outcome x cp_priv: retired_fault_m, retired_fault_u, discarded_m, discarded_u, retired_ok_recfg_m, retired_ok_recfg_u, retired_ok_priv_m, retired_ok_priv_u
  - cr_discard_reason = cp_outcome{discarded} x cp_flush_reason: discarded_branch, discarded_jump, discarded_exc, discarded_csr_flush
  - cr_hit_outcome = cp_later_hit{yes} x cp_outcome: hit_retired_fault (denied line cached, later hit faults), hit_retired_ok_recfg (denied line cached, later hit allowed after PMP change)
- Adopted (riscv-dv): none
- TP items: TP-PMP-064, TP-PMP-077, TP-PMP-091, TP-PMP-092, TP-PMP-105

### CG-PMP-011: gen_cg_pmp_recfg
- Features: F-PMP-020, F-PMP-033, F-PMP-055, F-PMP-065, F-PMP-092, F-PMP-100
- Sample: RVFI retire of a PMP CSR write (pmpcfg*/pmpaddr*/mseccfg) with rvfi_trap == 0; the effect fields diff the model verdict for the next retired instruction's pc (and its load/store address) before and after the write; anti-vacuity: only PMP CSR writes sample; a hit on a now_denied/now_allowed bin proves the write flipped a live verdict and the next instruction's trap/no-trap was checked against the new state
- Coverpoints:
  - cp_csr = written CSR and changed field: bins pmpcfg, pmpaddr, mseccfg_mml{mml 0->1}, mseccfg_mmwp{mmwp 0->1}, mseccfg_rlb{rlb changed}, mseccfg_none{no bit changed}
  - cp_next_fetch = verdict change for the next instruction's fetch: bins unchanged, now_denied, now_allowed
  - cp_next_data = verdict change for the next load/store address: bins none{next instruction is not a load/store}, unchanged, now_denied, now_allowed
  - cp_next_src = where the next instruction's word came from: bins bus_prefetched{granted on ibus before the write retired}, cache_hit, fresh{granted after the write retired}
  - cp_self = the write removes execute permission from the code that follows it: bins none, mmwp_self_fault, mml_self_fault, cfg_self_fault{pmpcfg/pmpaddr change}
  - cp_bb = back-to-back write pair: bins none, lock_then_addr{csrw pmpcfg (L=1 on i) then csrw pmpaddr(i)}, lock_then_cfg{then csrw pmpcfg same entry}, lock_then_rlb{then csrw mseccfg RLB=1}
  - cp_gap = instructions between the write and the affected access: bins g0{0}, g1_3{1..3}, g4_plus{>=4}
- Crosses:
  - cr_csr_fetch = cp_csr{pmpcfg,pmpaddr,mseccfg_mml,mseccfg_mmwp} x cp_next_fetch{now_denied,now_allowed}: pmpcfg_now_denied, pmpcfg_now_allowed, pmpaddr_now_denied, pmpaddr_now_allowed, mseccfg_mml_now_denied, mseccfg_mml_now_allowed, mseccfg_mmwp_now_denied, mseccfg_mmwp_now_allowed; ignore mseccfg_mmwp_now_allowed: MMWP only removes permission; ignore mseccfg_mml_now_allowed for M fetch: MML only removes M-mode fetch permission; U-mode allowed case kept
  - cr_csr_data = cp_csr{pmpcfg,pmpaddr,mseccfg_mml,mseccfg_mmwp} x cp_next_data{now_denied,now_allowed}: pmpcfg_now_denied, pmpcfg_now_allowed, pmpaddr_now_denied, pmpaddr_now_allowed, mseccfg_mml_now_denied, mseccfg_mml_now_allowed, mseccfg_mmwp_now_denied, mseccfg_mmwp_now_allowed; ignore mseccfg_mmwp_now_allowed: MMWP only removes permission
  - cr_src_fetch = cp_next_src x cp_next_fetch{now_denied,now_allowed}: bus_prefetched_now_denied, bus_prefetched_now_allowed, cache_hit_now_denied, cache_hit_now_allowed, fresh_now_denied, fresh_now_allowed
  - cr_self = cp_self{mmwp_self_fault,mml_self_fault,cfg_self_fault} x cp_gap{g0}: mmwp_self_fault_g0 (next instruction traps with cause 1), mml_self_fault_g0 (next instruction traps with cause 1), cfg_self_fault_g0 (next instruction traps with cause 1)
  - cr_bb = cp_bb{lock_then_addr,lock_then_cfg,lock_then_rlb}: lock_then_addr (second write ignored), lock_then_cfg (second write ignored), lock_then_rlb (RLB stays 0)
  - cr_gap_fetch = cp_gap x cp_next_fetch{now_denied}: g0_now_denied, g1_3_now_denied, g4_plus_now_denied
- Adopted (riscv-dv): none
- TP items: TP-PMP-020, TP-PMP-031, TP-PMP-053, TP-PMP-063, TP-PMP-090, TP-PMP-091, TP-PMP-092, TP-PMP-109

### CG-PMP-012: gen_cg_pmp_priv_mprv
- Features: F-PMP-072, F-PMP-073, F-PMP-074, F-PMP-075, F-PMP-076, F-PMP-077
- Sample: each CG-PMP-005 check event, capturing the privilege sources; anti-vacuity: mprv/mpp fields vary only when the program writes mstatus, so a hit on an mprv1 bin proves an access was checked under MPRV redirection and its verdict compared to the model's effective privilege
- Coverpoints:
  - cp_type = access type: bins fetch, load, store
  - cp_cur = rvfi_mode: bins m, u
  - cp_mprv = mstatus.mprv: bins mprv0, mprv1
  - cp_mpp = mstatus.mpp (legal values; illegal writes are stored as U): bins u, m
  - cp_mpp_wr_illegal = last mstatus write carried MPP in {01,10}: bins no, yes
  - cp_eff = model effective privilege: bins m, u
  - cp_dbg = rvfi_ext_debug_mode: bins d0, d1
  - cp_entry = how the current privilege was entered: bins mret_u, mret_m, dret_u, dret_m, exc_m, reset_m, dbg_entry
  - cp_mprv_after = first data access after an xRET: mprv state vs return target: bins mret_u_cleared, mret_m_kept, dret_u_kept_rtl{B1 RTL behaviour}, dret_u_cleared_spec{Sdext resume rule}, dret_m_kept
- Crosses:
  - cr_eff = cp_cur{m} x cp_mprv{mprv1} x cp_mpp x cp_type x cp_eff: m_mprv_mppu_load_effu, m_mprv_mppu_store_effu, m_mprv_mppu_fetch_effm (fetch never redirected), m_mprv_mppm_load_effm, m_mprv_mppm_store_effm, m_mprv_mppm_fetch_effm; ignore fetch_effu: priv_mode_id is used for fetch
  - cr_dbg_mprv = cp_dbg{d1} x cp_mprv{mprv1} x cp_mpp{u} x cp_type{load,store}: dbg_mprv_mppu_load (B2 scenario), dbg_mprv_mppu_store (B2 scenario)
  - cr_after_ret = cp_mprv_after x cp_type{load,store}: mret_u_cleared_load, mret_u_cleared_store, mret_m_kept_load, mret_m_kept_store, dret_u_kept_rtl_load, dret_u_kept_rtl_store, dret_u_cleared_spec_load, dret_u_cleared_spec_store, dret_m_kept_load, dret_m_kept_store
  - cr_u_entry = cp_cur{u} x cp_entry{mret_u,dret_u} x cp_type: u_mret_u_fetch, u_mret_u_load, u_mret_u_store, u_dret_u_fetch, u_dret_u_load, u_dret_u_store
  - cr_illegal_mpp = cp_mpp_wr_illegal{yes} x cp_mprv{mprv1} x cp_type{load,store} x cp_eff{u}: illegal_mpp_mprv_load_effu (RTL stores U (doc mismatch D2)), illegal_mpp_mprv_store_effu
- Adopted (riscv-dv): none
- TP items: TP-PMP-070, TP-PMP-071, TP-PMP-072, TP-PMP-073, TP-PMP-074, TP-PMP-075, TP-PMP-102

### CG-PMP-013: gen_cg_pmp_debug
- Features: F-PMP-017, F-PMP-095, F-PMP-096, F-PMP-097, F-PMP-098, F-PMP-099
- Sample: a CG-PMP-005 check event while rvfi_ext_debug_mode == 1, or any check event (in or out of debug) whose address satisfies (addr & ~DmAddrMask) == DmBaseAddr; anti-vacuity: non-debug accesses outside the DM window never sample; a hit proves a debug-mode or DM-window PMP interaction was checked
- Coverpoints:
  - cp_dbg = rvfi_ext_debug_mode: bins d0, d1
  - cp_in_dm = (addr & ~DmAddrMask) == DmBaseAddr: bins no, yes
  - cp_type = access type: bins fetch, load, store
  - cp_normal = verdict the non-debug rules would give: bins allow, deny
  - cp_verdict = model verdict: bins allow, deny
  - cp_mseccfg = mseccfg state: bins none, mmwp, mml, both
  - cp_dm_top_i32 = uncompressed instruction at DmBaseAddr + DmAddrMask - 1 (pc+2 outside the window): bins no, yes
  - cp_phase = position in the debug episode: bins halt_fetch{first fetch at DmHaltAddr after entry}, body, exc_fetch{fetch at DmExceptionAddr}, post_dret_first{first non-debug fetch after dret}
  - cp_csr_side = mcause/mepc/mtval readback after a debug-mode PMP fault: bins unchanged, changed
- Crosses:
  - cr_bypass = cp_dbg{d1} x cp_in_dm{yes} x cp_normal{deny} x cp_type x cp_verdict{allow}: bypass_fetch (DM window bypass), bypass_load (DM window bypass), bypass_store (DM window bypass); ignore bypass_x_deny: bypass is unconditional in debug mode
  - cr_no_bypass = cp_dbg{d0} x cp_in_dm{yes} x cp_normal{deny} x cp_type x cp_verdict{deny}: nodbg_dm_fetch_deny, nodbg_dm_load_deny, nodbg_dm_store_deny
  - cr_dbg_outside = cp_dbg{d1} x cp_in_dm{no} x cp_normal{deny} x cp_type x cp_verdict{deny}: dbg_out_fetch_deny (exception in debug mode -> DmExceptionAddr), dbg_out_load_deny (exception in debug mode -> DmExceptionAddr), dbg_out_store_deny (exception in debug mode -> DmExceptionAddr)
  - cr_dbg_outside_mseccfg = cp_dbg{d1} x cp_in_dm{no} x cp_mseccfg{mmwp,mml,both} x cp_verdict: mmwp_allow, mmwp_deny, mml_allow, mml_deny, both_allow, both_deny
  - cr_dm_top = cp_dm_top_i32{yes} x cp_mseccfg{mmwp,mml,both} x cp_verdict{deny}: dm_top_mmwp_deny (PMP_I2 checked outside the window), dm_top_mml_deny (PMP_I2 checked outside the window), dm_top_both_deny (PMP_I2 checked outside the window)
  - cr_phase = cp_phase x cp_verdict: halt_fetch_allow, halt_fetch_deny, body_allow, body_deny, exc_fetch_allow, exc_fetch_deny, post_dret_first_allow, post_dret_first_deny; ignore exc_fetch_deny: DmExceptionAddr is inside the DM window
  - cr_csr_side = cp_dbg{d1} x cp_verdict{deny} x cp_csr_side: dbg_deny_unchanged; ignore dbg_deny_changed: contradicts Sdext; gen_chk_debug fails first
  - cr_bypass_mseccfg = cp_dbg{d1} x cp_in_dm{yes} x cp_mseccfg x cp_type: none_fetch, none_load, none_store, mmwp_fetch, mmwp_load, mmwp_store, mml_fetch, mml_load, mml_store, both_fetch, both_load, both_store
- Adopted (riscv-dv): none
- TP items: TP-PMP-074, TP-PMP-094, TP-PMP-095, TP-PMP-096, TP-PMP-097, TP-PMP-098, TP-PMP-099, TP-PMP-104

### CG-PMP-014: gen_cg_pmp_table_state
- Features: F-PMP-015, F-PMP-042, F-PMP-046, F-PMP-047, F-PMP-053, F-PMP-056
- Sample: RVFI retire of any PMP CSR write (snapshot of the table after the write) and at each regime phase start; condition: at least one PMP-checked access retires before the next table change (otherwise the sample is discarded); anti-vacuity: only table changes sample; a hit proves a live configuration with the named shape was run under
- Coverpoints:
  - cp_active = entries with A != OFF: bins n0{0}, n1{1}, n2_4{2..4}, n5_8{5..8}, n9_15{9..PMPNumRegions-1}, n16{PMPNumRegions}
  - cp_locked = entries with L = 1: bins n0{0}, n1_4{1..4}, n5_15{5..PMPNumRegions-1}, n16{PMPNumRegions}
  - cp_modes = modes present among active entries: bins none, tor_only, na_only{NA4/NAPOT only}, mixed
  - cp_tor_empty = active TOR entries with addr(i-1) >= addr(i): bins none, some
  - cp_overlap = pairs of active regions with overlapping byte ranges: bins none, some
  - cp_regime = knob:pmp_regime: bins off, sparse, dense, mml_on
  - cp_all_off_u = all entries OFF and a U-mode access follows: bins no, yes
  - cp_e15 = entry PMPNumRegions-1: bins off, active
  - cp_e0_tor = entry 0 in TOR mode: bins no, yes
  - cp_mseccfg = {mml,mmwp,rlb}: bins s000, s001, s010, s011, s100, s101, s110, s111
- Crosses:
  - cr_regime_active = cp_regime x cp_active: off_n0, sparse_n1, sparse_n2_4, dense_n5_8, dense_n9_15, dense_n16, mml_on_n1, mml_on_n2_4, mml_on_n5_8, mml_on_n9_15, mml_on_n16; ignore off_n>0, sparse_n0/n>=5, dense_n<5, mml_on_n0: outside the regime definition
  - cr_regime_mseccfg = cp_regime x cp_mseccfg: off_s000, off_s001, off_s010, off_s011, sparse_s000, sparse_s001, sparse_s010, sparse_s011, dense_s000, dense_s001, dense_s010, dense_s011, mml_on_s100, mml_on_s101, mml_on_s110, mml_on_s111; ignore off/sparse/dense x s1xx: MML is set only in the mml_on regime; ignore mml_on x s0xx: regime sets MML first
  - cr_locked_regime = cp_locked x cp_regime{sparse,dense,mml_on}: n0_sparse, n0_dense, n0_mml_on, n1_4_sparse, n1_4_dense, n1_4_mml_on, n5_15_sparse, n5_15_dense, n5_15_mml_on, n16_sparse, n16_dense, n16_mml_on; ignore sparse_n5_15/n16: sparse has at most 4 active entries; locked OFF entries are allowed so n5_15 stays samplable only via OFF locks - kept
  - cr_overlap_modes = cp_overlap{some} x cp_modes{tor_only,na_only,mixed}: overlap_tor_only, overlap_na_only, overlap_mixed
  - cr_all_off_u = cp_all_off_u{yes} x cp_active{n0}: all_off_u_n0 (every U access faults)
  - cr_e15_e0 = cp_e15{active} x cp_e0_tor: e15_active_e0tor_no, e15_active_e0tor_yes
- Adopted (riscv-dv): none
- TP items: TP-PMP-010, TP-PMP-039, TP-PMP-040, TP-PMP-044, TP-PMP-045, TP-PMP-051, TP-PMP-100, TP-PMP-101, TP-PMP-106, TP-PMP-107

### Appendix A: Smepmp truth table as bound to CG-PMP-005.cr_truth_mml1 (expected verdict per bin)

| LRWX | M fetch | M load | M store | U fetch | U load | U store |
|---|---|---|---|---|---|---|
| c0000 | deny | deny | deny | deny | deny | deny |
| c0001 | deny | deny | deny | allow | deny | deny |
| c0010 | deny | allow | allow | deny | allow | deny |
| c0011 | deny | allow | allow | deny | allow | allow |
| c0100 | deny | deny | deny | deny | allow | deny |
| c0101 | deny | deny | deny | allow | allow | deny |
| c0110 | deny | deny | deny | deny | allow | allow |
| c0111 | deny | deny | deny | allow | allow | allow |
| c1000 | deny | deny | deny | deny | deny | deny |
| c1001 | allow | deny | deny | deny | deny | deny |
| c1010 | allow | deny | deny | allow | deny | deny |
| c1011 | allow | allow | deny | allow | deny | deny |
| c1100 | deny | allow | deny | deny | deny | deny |
| c1101 | allow | allow | deny | deny | deny | deny |
| c1110 | deny | allow | allow | deny | deny | deny |
| c1111 | deny | allow | deny | deny | allow | deny |

### Appendix B: original PMP table as bound to CG-PMP-005.cr_truth_mml0 (RW=01 rows ignored)

| LRWX | M fetch | M load | M store | U fetch | U load | U store |
|---|---|---|---|---|---|---|
| c0000 | allow | allow | allow | deny | deny | deny |
| c0001 | allow | allow | allow | allow | deny | deny |
| c0100 | allow | allow | allow | deny | allow | deny |
| c0101 | allow | allow | allow | allow | allow | deny |
| c0110 | allow | allow | allow | deny | allow | allow |
| c0111 | allow | allow | allow | allow | allow | allow |
| c1000 | deny | deny | deny | deny | deny | deny |
| c1001 | allow | deny | deny | allow | deny | deny |
| c1100 | deny | allow | deny | deny | allow | deny |
| c1101 | allow | allow | deny | allow | allow | deny |
| c1110 | deny | allow | allow | deny | allow | allow |
| c1111 | allow | allow | allow | allow | allow | allow |

## Counts

- covergroups: 14
- coverpoints: 129
- bins (coverpoint bins): 461
- crosses: 94
- cross bins: 1119
- adopted bins: 0 (vendor/google_riscv-dv was not in this subagent's fence; nothing adopted)

## Probe candidates

- CG-PMP-008.cp_lat / cr_lat.aligned_denied_lat2 (F-PMP-084): the 2-cycle internal completion of a denied access is invisible at the boundary (no bus handshake; retire timing is confounded by pipeline stalls). Probe: u_ibex_core.load_store_unit_i.ls_fsm_cs and lsu_resp_valid_o (read-only, define-gated). DV Lead decides.
- CG-PMP-009.cp_src / CG-PMP-010.cp_later_hit (icache hit inference, F-PMP-093): inferred from the absence of an ibus fetch for the word since the last flush; ambiguous when the prefetch buffer still holds the word. Probe alternative: u_ibex_core.if_stage_i.gen_icache.icache_i lookup hit indication (ic_tag_write_o / tag hit) if the boundary inference is judged too weak.
- CG-PMP-012.cp_mprv_after (dret_u_* bins, F-PMP-075): mstatus.MPRV cannot be read in U-mode; the bin is inferred from the access verdict. Probe alternative: u_ibex_core.cs_registers_i.mstatus_q.mprv. DV Lead decides.
- CG-PMP-013.cp_phase halt_fetch / post_dret_first (CTRL-34 registered debug_mode window): sampled from rvfi_ext_debug_mode and the ibus address == DmHaltAddr; the exact cycle of debug_mode_q is not needed for the bins but would sharpen the checker. Probe alternative: u_ibex_core.id_stage_i.controller_i.debug_mode_q.



# 3.5 Areas DBG, TRG, PMC: External debug (Sdext), triggers (Sdtrig), performance counters


Area group DBG/TRG/PMC, T-006 subagent output. Build configuration `opentitan`, DUT gen_dut_top
(ibex_core + ibex_register_file_ff), DbgHwBreakNum=1, MHPMCounterNum=10, MHPMCounterWidth=32,
DmBaseAddr=0x1A110000, DmAddrMask=0xFFF, DmHaltAddr=0x1A110800, DmExceptionAddr=0x1A110808.

Conventions
- Every covergroup is `gen_cg_<area>_<name>` in gen_fcov_pkg (or a gen_<x>_cov module bound via
  gen_binds); none extends an RTL covergroup. Sampling events come from the RVFI monitor, the
  ibus/dbus monitors, the irq/debug_req driver monitors and the TB debug-state model
  (`dbg_model`: debug_mode, step_armed, pending irq, WB occupancy), never from a bare clock.
- Parameter-derived values: PRIV_LVL_*, DBG_CAUSE_*, CSR_* from ibex_pkg; MHPMCOUNTER_BASE (=3)
  and MHPMCounterNum, MHPMCounterWidth, DbgHwBreakNum, DmBaseAddr/DmAddrMask/DmHaltAddr/
  DmExceptionAddr from the gen_dut_top parameters; irq_fast width from $bits(irq_fast_i).
  Per-counter bins for mhpmcounter3..12 are written as MHPMCOUNTER_BASE+k and are generated only
  for k < MHPMCounterNum (generate-guarded).
- Bins in TP items and the CSVs are referenced as CG-<AREA>-<nnn>.cp_<name>.<bin> and
  CG-<AREA>-<nnn>.cr_<name>.<bin>. Cross bins are written `<bin>{a,b[,c]}` listing the component
  bins in coverpoint order.
- No `illegal_bins`: contradictions are checker failures, not coverage. Values that cannot occur
  are `ignore_bins` with a reason.
- "readback" always means the value returned by a later csrr of the same CSR observed on
  rvfi_rd_wdata, not the predicted value.
- Bins whose only purpose is bug-candidate evidence are marked (B<n>); hitting them is expected in
  the expected-fail item and confirms the reproducer.

---------------------------------------------------------------------------------------------------

## DBG covergroups

### CG-DBG-001: gen_cg_dbg_entry
- Features: F-DBG-001, F-DBG-002, F-DBG-003, F-DBG-004, F-DBG-007, F-DBG-008, F-DBG-009, F-DBG-010, F-DBG-011, F-DBG-025, F-DBG-037, F-DBG-038, F-DBG-039, F-DBG-040, F-DBG-041, F-DBG-044, F-DBG-045, F-DBG-046, F-DBG-047, F-DBG-048, F-DBG-049, F-DBG-058, F-DBG-061, F-DBG-064, F-DBG-066, F-DBG-068, F-TRG-010, F-TRG-016, F-TRG-017, F-TRG-018, F-TRG-019
- Sample: debug entry = first ibus request to DmHaltAddr while dbg_model.debug_mode==0 (ibus monitor
  event); cause/prv/dpc are taken from the debug-ROM prologue's csrr dcsr / csrr dpc retirements
  (rvfi_rd_wdata) that follow the entry; condition: `dm_halt_fetch && !dbg_model.debug_mode`;
  anti-vacuity: no non-debug program code is placed at DmHaltAddr (TB memory map), so the fetch
  alone proves an entry; the cause and dpc bins come from observed CSR reads, so a hit proves what
  the hardware recorded, not what the stimulus intended.
- Coverpoints:
  - cp_cause = dcsr.cause readback: bins ebreak{DBG_CAUSE_EBREAK}, trigger{DBG_CAUSE_TRIGGER}, haltreq{DBG_CAUSE_HALTREQ}, step{DBG_CAUSE_STEP}, none{DBG_CAUSE_NONE}; ignore_bins reserved{5,6,7}: RTL never produces resethaltreq/group/other (CTRL-25). `none` is B9 evidence.
  - cp_prv_before = dcsr.prv readback: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}; ignore_bins s_h{PRIV_LVL_S,PRIV_LVL_H}: no S/H mode, WARL-legalised to U (F-DBG-013).
  - cp_entry_ctx = dbg_model pipeline context in the decision cycle: bins idle{DECODE, nothing outstanding}, lsu_wait{load/store outstanding in WB}, div_wait{multi-cycle divide in EX}, zcmp{Zcmp micro-op sequence in progress when the request was first seen}, sleep{WFI sleep}, reset{FIRST_FETCH after reset release}, flush_exc{synchronous exception in FLUSH}, flush_mret{mret in FLUSH}, flush_csr{CSR-write pipeline flush}, flush_wfi{wfi in FLUSH with the request already registered: WAIT_SLEEP never entered (H-C1)}, irq_taken{IRQ_TAKEN in progress}, after_dret{first cycle after dret, no retirement in between}, after_trap{first DECODE after a trap/irq vector, no handler retirement}, after_mret{first DECODE after mret, no retirement}, ifetch_stall{IF waiting for instr_rvalid_i}
  - cp_dpc_kind = dpc readback vs the RVFI stream: bins next_seq{last retired pc + size}, br_target{taken branch/jump target}, mtvec{trap or interrupt vector}, mret_target{mepc}, ebreak_pc{pc of the ebreak}, trig_pc{== tdata2}, boot{boot_addr_i[31:8],8'h80}, wfi_next{wfi pc + 4}, dret_target{unchanged across an immediate re-halt}
  - cp_busy_dip = number of consecutive cycles core_busy_o was Off between the last non-debug retirement (or the request, if later) and the DmHaltAddr fetch: bins none{0}, one{1}, many{[2:$]}; anti-vacuity: `none` for a wfi context is reachable only through the FLUSH -> DBG_TAKEN_IF override (F-DBG-068), `one` only when SLEEP is left in its first cycle (F-DBG-044/059 shape), `many` only after a real sleep (F-DBG-009).
- Crosses:
  - cr_cause_prv = cp_cause x cp_prv_before: bins ebreak_m{ebreak,m}, ebreak_u{ebreak,u}, trigger_m{trigger,m}, trigger_u{trigger,u}, haltreq_m{haltreq,m}, haltreq_u{haltreq,u}, step_m{step,m}, step_u{step,u}; ignore none x *: B9 bin is covered on cp_cause alone.
  - cr_cause_ctx = cp_cause x cp_entry_ctx: bins haltreq_idle{haltreq,idle}, haltreq_lsu{haltreq,lsu_wait}, haltreq_div{haltreq,div_wait}, haltreq_zcmp{haltreq,zcmp}, haltreq_sleep{haltreq,sleep}, haltreq_reset{haltreq,reset}, haltreq_flush_exc{haltreq,flush_exc}, haltreq_flush_mret{haltreq,flush_mret}, haltreq_flush_csr{haltreq,flush_csr}, haltreq_flush_wfi{haltreq,flush_wfi}, haltreq_irq_taken{haltreq,irq_taken}, haltreq_after_dret{haltreq,after_dret}, haltreq_ifetch{haltreq,ifetch_stall}, step_idle{step,idle}, step_lsu{step,lsu_wait}, step_div{step,div_wait}, step_zcmp{step,zcmp}, step_sleep{step,sleep}, step_flush_exc{step,flush_exc}, step_flush_mret{step,flush_mret}, step_flush_csr{step,flush_csr}, trigger_idle{trigger,idle}, trigger_after_dret{trigger,after_dret}, trigger_after_trap{trigger,after_trap}, trigger_after_mret{trigger,after_mret}, trigger_ifetch{trigger,ifetch_stall}, ebreak_idle{ebreak,idle}; ignore ebreak x {lsu_wait, div_wait, zcmp, sleep, reset, irq_taken, after_*}: ebreak is decided in FLUSH with the pipe drained; ignore trigger x {sleep, reset, zcmp, irq_taken, flush_*}: trigger is a non-priority entry masked in these states (CTRL-24).
  - cr_cause_dpc = cp_cause x cp_dpc_kind: bins haltreq_next{haltreq,next_seq}, haltreq_br{haltreq,br_target}, haltreq_mtvec{haltreq,mtvec}, haltreq_mret{haltreq,mret_target}, haltreq_boot{haltreq,boot}, haltreq_wfi{haltreq,wfi_next}, haltreq_dret{haltreq,dret_target}, step_next{step,next_seq}, step_br{step,br_target}, step_mtvec{step,mtvec}, step_mret{step,mret_target}, step_wfi{step,wfi_next}, ebreak_pc{ebreak,ebreak_pc}, trigger_pc{trigger,trig_pc}; ignore ebreak x others, trigger x others: dpc is fixed by construction for these causes (a different value is a gen_chk_debug failure).
  - cr_ctx_busy = cp_entry_ctx x cp_busy_dip: bins flush_wfi_none{flush_wfi,none}, sleep_one{sleep,one}, sleep_many{sleep,many}; ignore flush_wfi x {one, many}: the FLUSH -> DBG_TAKEN_IF arc never reaches WAIT_SLEEP (gen_chk_sleep failure); ignore sleep x none: a SLEEP-context entry always passed WAIT_SLEEP; other contexts x *: core_busy_o is high outside WAIT_SLEEP/SLEEP by construction, not covered here.
- Adopted (riscv-dv): none
- TP items: TP-DBG-001, TP-DBG-002, TP-DBG-003, TP-DBG-004, TP-DBG-005, TP-DBG-006, TP-DBG-007, TP-DBG-008, TP-DBG-009, TP-DBG-011, TP-DBG-012, TP-DBG-013, TP-DBG-014, TP-DBG-015, TP-DBG-016, TP-DBG-022, TP-DBG-024, TP-DBG-042, TP-DBG-043, TP-DBG-044, TP-DBG-045, TP-DBG-046, TP-DBG-049, TP-DBG-050, TP-DBG-051, TP-DBG-052, TP-DBG-053, TP-DBG-054, TP-DBG-067, TP-DBG-068, TP-DBG-069, TP-DBG-071, TP-TRG-010, TP-TRG-012, TP-TRG-016, TP-TRG-017, TP-TRG-018, TP-TRG-019, TP-TRG-027

### CG-DBG-002: gen_cg_dbg_req_shape
- Features: F-DBG-002, F-DBG-005, F-DBG-006, F-DBG-007, F-DBG-008, F-DBG-049, F-DBG-058, F-DBG-068, F-TRG-019
- Sample: every debug_req_i rising edge seen by the debug_req driver monitor, sampled when its
  outcome is known (entry observed, or the bounded no-entry window expired); condition:
  `debug_req_rise && outcome_known`; anti-vacuity: the driver randomizes the pulse shape, so both
  `entered` and `dropped` are reachable; `dropped` is only recorded when no DmHaltAddr fetch occurs
  within the drain bound although the request was seen, so a hit proves a lost pulse.
- Coverpoints:
  - cp_shape = driver transaction shape: bins level_held{held until entry observed}, pulse_short{released 1..3 cycles after assertion, before entry}, pulse_flush{released exactly in the FLUSH cycle of a coincident special request}, held_in_debug{asserted while dbg_model.debug_mode==1}, held_across_dret{still high when dret retires}, at_reset{high through reset release}
  - cp_outcome = observed effect: bins entered{DmHaltAddr fetch}, dropped{no entry within bound}, rehalt_after_dret{entry with zero retirements after dret}, ignored_in_debug{no state change}
  - cp_coincident = dbg_model event pending in the same decision cycle: bins none{}, irq{enabled interrupt pending}, nmi{irq_nm_i}, sync_exc{exception in ID/WB}, ebreak_dbg{ebreak with ebreakX=1}, trigger{trigger match}, step{step armed}, mret{mret in ID}, csr_flush{CSR write flush}, wfi{wfi in ID}
- Crosses:
  - cr_shape_outcome = cp_shape x cp_outcome: bins held_entered{level_held,entered}, short_dropped{pulse_short,dropped}, short_entered{pulse_short,entered}, flush_entered{pulse_flush,entered}, indebug_ignored{held_in_debug,ignored_in_debug}, dret_rehalt{held_across_dret,rehalt_after_dret}, reset_entered{at_reset,entered}; ignore level_held x dropped: a held request is never dropped (checker failure).
  - cr_coincident_outcome = cp_coincident x cp_outcome: bins irq_entered{irq,entered}, nmi_entered{nmi,entered}, exc_entered{sync_exc,entered}, ebreak_entered{ebreak_dbg,entered}, trigger_entered{trigger,entered}, step_entered{step,entered}, mret_entered{mret,entered}, csr_entered{csr_flush,entered}, wfi_entered{wfi,entered}
- Adopted (riscv-dv): none
- TP items: TP-DBG-003, TP-DBG-006, TP-DBG-007, TP-DBG-008, TP-DBG-010, TP-DBG-011, TP-DBG-012, TP-DBG-013, TP-DBG-014, TP-DBG-030, TP-DBG-054, TP-DBG-068, TP-DBG-071, TP-TRG-019

### CG-DBG-003: gen_cg_dbg_ebreak
- Features: F-DBG-017, F-DBG-018, F-DBG-019, F-DBG-020, F-DBG-021, F-DBG-022, F-DBG-023, F-DBG-024, F-DBG-025, F-DBG-041, F-DBG-066, F-TRG-020
- Sample: RVFI item whose rvfi_insn is ebreak or c.ebreak (both the trap-recorded and the
  into-debug case carry rvfi_trap, F-DBG-017), plus the WB-fault-discard case detected by the
  dbg_model (ebreak in ID when WB faults, ebreak later re-executed); condition:
  `rvfi_valid && is_ebreak(rvfi_insn)`; anti-vacuity: the outcome bin is derived from the next
  fetch (DmHaltAddr vs mtvec target) and the dcsr readback, not from ebreakm/ebreaku, so a hit
  proves the path the hardware took.
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_ebreakm = dcsr.ebreakm (CSR model): bins off{0}, on{1}
  - cp_ebreaku = dcsr.ebreaku: bins off{0}, on{1}
  - cp_form = instruction width: bins full{32-bit ebreak}, comp{c.ebreak}
  - cp_in_debug = rvfi_ext_debug_mode: bins no{0}, yes{1}
  - cp_outcome = outcome decoded from the next fetch address and the dcsr/mcause readback: bins dbg_entry{cause 1 entry, dpc == ebreak pc}, bp_exc{mcause 3 trap, mepc == ebreak pc}, reenter{in debug: DmHaltAddr fetch, dcsr/dpc unchanged}, discarded{WB load/store fault taken instead}
  - cp_coincident = dbg_model event pending in the decision cycle: bins none{}, haltreq{debug_req_i high}, step{step armed}, trig_next{tdata2 == ebreak pc + size, execute=1 (B10)}, wb_fault{load/store fault in WB}
- Crosses:
  - cr_priv_en_outcome = cp_priv x cp_ebreakm x cp_ebreaku x cp_outcome: bins m_off_off_exc{m,off,off,bp_exc}, m_off_on_exc{m,off,on,bp_exc}, m_on_off_dbg{m,on,off,dbg_entry}, m_on_on_dbg{m,on,on,dbg_entry}, u_off_off_exc{u,off,off,bp_exc}, u_on_off_exc{u,on,off,bp_exc}, u_off_on_dbg{u,off,on,dbg_entry}, u_on_on_dbg{u,on,on,dbg_entry}; ignore * x reenter, * x discarded: covered by cr_form_outcome / cr_coincident_outcome; ignore contradictory pairs (e.g. m,on,*,bp_exc): checker failures.
  - cr_form_outcome = cp_form x cp_outcome: bins full_dbg{full,dbg_entry}, full_exc{full,bp_exc}, full_reenter{full,reenter}, comp_dbg{comp,dbg_entry}, comp_exc{comp,bp_exc}, comp_reenter{comp,reenter}
  - cr_coincident_outcome = cp_coincident x cp_outcome: bins haltreq_dbg{haltreq,dbg_entry}, step_dbg{step,dbg_entry}, trignext_dbg{trig_next,dbg_entry}, wbfault_discarded{wb_fault,discarded}
- Adopted (riscv-dv): none
- TP items: TP-DBG-022, TP-DBG-023, TP-DBG-024, TP-DBG-025, TP-DBG-026, TP-DBG-027, TP-DBG-028, TP-DBG-029, TP-DBG-030, TP-DBG-046, TP-DBG-067, TP-DBG-068, TP-TRG-020

### CG-DBG-004: gen_cg_dbg_exc_in_debug
- Features: F-DBG-011, F-DBG-026, F-DBG-027, F-DBG-028, F-DBG-029, F-DBG-030, F-DBG-036, F-DBG-054, F-DBG-055, F-DBG-060, F-DBG-064, F-DBG-067
- Sample: RVFI item with rvfi_trap && rvfi_ext_debug_mode (synchronous exception inside debug
  mode); target address taken from the next ibus request; condition:
  `rvfi_valid && rvfi_trap && rvfi_ext_debug_mode`; anti-vacuity: debug programs are trap-free
  unless the test injects a fault, so a hit proves an exception occurred in debug mode; the kind bin
  is decoded from rvfi_insn / dbus / PMP-model verdict, not from the test's intent.
- Coverpoints:
  - cp_kind = exception kind decoded from rvfi_insn / dbus / PMP-model verdict: bins illegal{illegal instruction}, illegal_csr{CSR access illegal (address/privilege)}, ecall{}, fetch_pmp{fetch PMP fault outside DM window}, fetch_bus{instr_err_i}, load_pmp{}, store_pmp{}, load_bus{data_err_i on load}, store_bus{data_err_i on store}
  - cp_priv_in_debug = rvfi_mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U after mret-in-debug with MPP=U}
  - cp_mprv = mstatus.MPRV/MPP (CSR model): bins off{MPRV=0}, on_mpp_u{MPRV=1,MPP=U}, on_mpp_m{MPRV=1,MPP=M}
  - cp_dret_pending = dbus state when the trap is raised: bins none{}, dret_wait{fault raised while a dret was waiting for WB}
  - cp_seq = ordinal of the exception within the debug window: bins first{first exception in this debug window}, second{second consecutive exception in the window}
- Crosses:
  - cr_kind_priv = cp_kind x cp_priv_in_debug: bins illegal_m{illegal,m}, illegalcsr_m{illegal_csr,m}, ecall_m{ecall,m}, fetchpmp_m{fetch_pmp,m}, fetchbus_m{fetch_bus,m}, loadpmp_m{load_pmp,m}, storepmp_m{store_pmp,m}, loadbus_m{load_bus,m}, storebus_m{store_bus,m}, illegalcsr_u{illegal_csr,u}, ecall_u{ecall,u}, loadpmp_u{load_pmp,u}, fetchpmp_u{fetch_pmp,u}
  - cr_kind_mprv = cp_kind x cp_mprv: bins loadpmp_mprv_u{load_pmp,on_mpp_u}, storepmp_mprv_u{store_pmp,on_mpp_u}, loadpmp_off{load_pmp,off}, loadbus_mprv_u{load_bus,on_mpp_u}; (B2 evidence: loadpmp_mprv_u / storepmp_mprv_u)
  - cr_kind_dret = cp_kind x cp_dret_pending: bins loadpmp_dret{load_pmp,dret_wait}, loadbus_dret{load_bus,dret_wait}, storebus_dret{store_bus,dret_wait}
  - cr_kind_seq = cp_kind x cp_seq: bins illegal_second{illegal,second}, ecall_second{ecall,second}, loadbus_second{load_bus,second}
- Adopted (riscv-dv): none
- TP items: TP-DBG-031, TP-DBG-032, TP-DBG-033, TP-DBG-034, TP-DBG-035, TP-DBG-041, TP-DBG-059, TP-DBG-060, TP-DBG-064, TP-DBG-068

### CG-DBG-005: gen_cg_dbg_dret
- Features: F-DBG-007, F-DBG-013, F-DBG-031, F-DBG-032, F-DBG-033, F-DBG-034, F-DBG-035, F-DBG-036, F-DBG-042, F-DBG-056, F-DBG-057, F-DBG-066, F-TRG-016
- Sample: RVFI item with rvfi_insn == 32'h7B200073 (dret), legal (in debug mode, no trap) or
  illegal (outside debug mode, rvfi_trap); the `next` bin is closed when the following RVFI/bus
  event is observed; condition: `rvfi_valid && rvfi_insn == DRET`; anti-vacuity: dret occurs only
  in debug programs and in the directed illegal-dret items; the resume privilege is taken from
  rvfi_mode of the next retirement (or the dcsr readback when nothing retires), so a hit proves the
  observed resume mode.
- Coverpoints:
  - cp_legal = {rvfi_ext_debug_mode, rvfi_trap, rvfi_mode} of the dret item: bins ok{in debug mode, retired}, illegal_m{outside debug, M, rvfi_trap}, illegal_u{outside debug, U, rvfi_trap}
  - cp_prv_target = dcsr.prv at dret: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_prv_src = how dcsr.prv got its value: bins hw{saved by the entry}, sw_m{written 2'b11}, sw_u{written 2'b00}, sw_s{written 2'b01, legalised to U}, sw_h{written 2'b10, legalised to U}
  - cp_mprv = mstatus.MPRV at dret (CSR model): bins off{0}, on{1 with MPP=M}
  - cp_dpc_src = origin of the dpc value (hardware save vs software write): bins hw{saved by the entry}, sw_even{csrw dpc even}, sw_odd{csrw dpc odd, bit 0 dropped}
  - cp_wb_pending = dbus state when dret is in ID: bins none{}, load{load outstanding}, store{store outstanding}, fault{outstanding access returns an error}
  - cp_next = first event after dret: bins run{ordinary retirement at dpc}, rehalt_req{held debug_req_i re-halts, zero retirements}, rehalt_ebreak{ebreak at dpc enters debug}, rehalt_trig{trigger at dpc}, irq_first{interrupt taken before any retirement, mepc == dpc}, nmi_first{NMI taken first}, step_one{exactly one retirement then re-entry}, fault_at_dpc{fetch at dpc faults}
- Crosses:
  - cr_prv_next = cp_prv_target x cp_next: bins m_run{m,run}, m_rehalt_req{m,rehalt_req}, m_rehalt_ebreak{m,rehalt_ebreak}, m_rehalt_trig{m,rehalt_trig}, m_irq{m,irq_first}, m_nmi{m,nmi_first}, m_step{m,step_one}, m_fault{m,fault_at_dpc}, u_run{u,run}, u_rehalt_req{u,rehalt_req}, u_rehalt_ebreak{u,rehalt_ebreak}, u_rehalt_trig{u,rehalt_trig}, u_irq{u,irq_first}, u_nmi{u,nmi_first}, u_step{u,step_one}, u_fault{u,fault_at_dpc}
  - cr_prv_mprv = cp_prv_target x cp_mprv: bins u_on{u,on}, m_on{m,on}, u_off{u,off}, m_off{m,off}; (B1 evidence: u_on)
  - cr_prvsrc_target = cp_prv_src x cp_prv_target: bins hw_m{hw,m}, hw_u{hw,u}, swm_m{sw_m,m}, swu_u{sw_u,u}, sws_u{sw_s,u}, swh_u{sw_h,u}; ignore sw_s x m, sw_h x m: WARL result is U.
  - cr_dpcsrc_next = cp_dpc_src x cp_next: bins hw_run{hw,run}, even_run{sw_even,run}, odd_run{sw_odd,run}, hw_fault{hw,fault_at_dpc}
  - cr_wb_next = cp_wb_pending x cp_next: bins load_run{load,run}, store_run{store,run}, none_run{none,run}
- Adopted (riscv-dv): none
- TP items: TP-DBG-012, TP-DBG-019, TP-DBG-036, TP-DBG-037, TP-DBG-038, TP-DBG-039, TP-DBG-040, TP-DBG-041, TP-DBG-042, TP-DBG-053, TP-DBG-061, TP-DBG-062, TP-DBG-067, TP-DBG-068, TP-TRG-016

### CG-DBG-006: gen_cg_dbg_step
- Features: F-DBG-037, F-DBG-038, F-DBG-039, F-DBG-040, F-DBG-041, F-DBG-042, F-DBG-043, F-DBG-044, F-DBG-045, F-DBG-046, F-DBG-047, F-DBG-048, F-DBG-049, F-TRG-018, F-PMC-048
- Sample: debug entry (CG-DBG-001 event) that follows a dret with dbg_model.step_armed==1 (dcsr.step
  written 1 in the preceding debug window); condition: `dm_halt_fetch && step_armed`; anti-vacuity:
  step is armed only by an observed csrw dcsr retirement with bit 2 set; the stepped class comes
  from the zero or one RVFI item between the dret and the re-entry, so a hit proves what was
  stepped.
- Coverpoints:
  - cp_stepped = class of the single non-debug instruction: bins alu{}, comp{16-bit non-branch}, load_fast{rvalid at minimum latency}, load_slow{rvalid delayed}, store_slow{store gnt/rvalid delayed}, div{div/divu/rem/remu}, mulh{mulh/mulhsu/mulhu}, br_taken{}, br_not{32-bit not taken}, c_br_not{c.beqz/c.bnez not taken}, jal{}, jalr{}, mret{}, wfi{}, fence_i{}, csr_flush{CSR write causing a pipeline flush}, ecall{}, illegal{}, ebreak_exc{ebreak with ebreakX=0}, ebreak_dbg{ebreak with ebreakX=1}, zcmp_push{cm.push}, zcmp_pop{cm.pop}, zcmp_popret{cm.popret/popretz}, zcmp_mv{cm.mvsa01/mva01s}, jump_fault_tgt{jump whose target fetch faults}, load_fault{load PMP/bus fault}, store_fault{}, trig_hit{trigger on the first instruction, zero retirements}
  - cp_prv = privilege of the stepped instruction (rvfi_mode / dcsr.prv): bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_pending = interrupt pending during the step window: bins none{}, irq{enabled interrupt}, nmi{irq_nm_i}
  - cp_haltreq = debug_req_i high during the step: bins no{0}, yes{1}
  - cp_cause = dcsr.cause readback at re-entry: bins step{DBG_CAUSE_STEP}, ebreak{DBG_CAUSE_EBREAK}, trigger{DBG_CAUSE_TRIGGER}, haltreq{DBG_CAUSE_HALTREQ}
  - cp_retired = RVFI items between dret and re-entry: bins none{0 items}, one_ok{1 item, no trap}, one_trap{1 item with rvfi_trap}
  - cp_minstret_delta = minstret readback delta across the step: bins zero{0}, one{1}
- Crosses:
  - cr_stepped_prv = cp_stepped x cp_prv: bins alu_m{alu,m}, comp_m{comp,m}, loadfast_m{load_fast,m}, loadslow_m{load_slow,m}, storeslow_m{store_slow,m}, div_m{div,m}, mulh_m{mulh,m}, brtaken_m{br_taken,m}, brnot_m{br_not,m}, cbrnot_m{c_br_not,m}, jal_m{jal,m}, jalr_m{jalr,m}, mret_m{mret,m}, wfi_m{wfi,m}, fencei_m{fence_i,m}, csrflush_m{csr_flush,m}, ecall_m{ecall,m}, illegal_m{illegal,m}, ebreakexc_m{ebreak_exc,m}, ebreakdbg_m{ebreak_dbg,m}, push_m{zcmp_push,m}, pop_m{zcmp_pop,m}, popret_m{zcmp_popret,m}, mv_m{zcmp_mv,m}, jumpfault_m{jump_fault_tgt,m}, loadfault_m{load_fault,m}, storefault_m{store_fault,m}, trig_m{trig_hit,m}, alu_u{alu,u}, comp_u{comp,u}, loadslow_u{load_slow,u}, brtaken_u{br_taken,u}, ecall_u{ecall,u}, illegal_u{illegal,u}, ebreakexc_u{ebreak_exc,u}, ebreakdbg_u{ebreak_dbg,u}, wfi_u{wfi,u}, push_u{zcmp_push,u}, trig_u{trig_hit,u}, loadfault_u{load_fault,u}; ignore mret x u: mret in U is an illegal instruction (illegal_u).
  - cr_pending_cause = cp_pending x cp_cause: bins irq_step{irq,step}, nmi_step{nmi,step}, none_step{none,step}
  - cr_haltreq_cause = cp_haltreq x cp_cause: bins yes_haltreq{yes,haltreq}, no_step{no,step}, yes_trigger{yes,trigger}, yes_ebreak{yes,ebreak}
  - cr_stepped_retired = cp_stepped x cp_retired: bins alu_ok{alu,one_ok}, wfi_ok{wfi,one_ok}, mret_ok{mret,one_ok}, push_ok{zcmp_push,one_ok}, popret_ok{zcmp_popret,one_ok}, ecall_trap{ecall,one_trap}, illegal_trap{illegal,one_trap}, ebreakexc_trap{ebreak_exc,one_trap}, ebreakdbg_trap{ebreak_dbg,one_trap}, loadfault_trap{load_fault,one_trap}, jumpfault_ok{jump_fault_tgt,one_ok}, trig_none{trig_hit,none}
  - cr_stepped_minstret = cp_stepped x cp_minstret_delta: bins alu_one{alu,one}, wfi_one{wfi,one}, ecall_zero{ecall,zero}, illegal_zero{illegal,zero}, push_one{zcmp_push,one}
- Adopted (riscv-dv): none
- TP items: TP-DBG-042, TP-DBG-043, TP-DBG-044, TP-DBG-045, TP-DBG-046, TP-DBG-047, TP-DBG-048, TP-DBG-049, TP-DBG-050, TP-DBG-051, TP-DBG-052, TP-DBG-053, TP-DBG-054, TP-DBG-068, TP-TRG-018, TP-PMC-050

### CG-DBG-007: gen_cg_dbg_dcsr_warl
- Features: F-DBG-012, F-DBG-013, F-DBG-014, F-DBG-015, F-DBG-016, F-DBG-043, F-DBG-057
- Sample: RVFI retirement of a CSR write op (csrrw/csrrs/csrrc and immediate forms with a non-zero
  source) to CSR_DCSR in debug mode, sampled once per set bit of the effective write data, and closed
  by the following csrr dcsr readback; condition: `rvfi_valid && csr_addr == CSR_DCSR && is_write &&
  rvfi_ext_debug_mode`; anti-vacuity: dcsr writes exist only in debug programs and the pattern is
  randomized; the readback class is derived from the observed read value, so a hit in `forced0`
  proves the hardware legalised that bit rather than the model assuming it.
- Coverpoints:
  - cp_pattern = write-data class: bins zeros{32'h0}, ones{32'hFFFF_FFFF}, walk1{single bit}, random{}, prv_only{only bits 1:0 changed}
  - cp_bit = field containing the sampled set bit: bins xdebugver{31:28}, z27_16{27:16}, ebreakm{15}, z14{14}, ebreaks{13}, ebreaku{12}, stepie{11}, stopcount{10}, stoptime{9}, cause{8:6}, z5{5}, mprven{4}, nmip{3}, step{2}, prv{1:0}
  - cp_prv_w = prv value written: bins u{2'b00}, s{2'b01}, h{2'b10}, m{2'b11}
  - cp_readback = per-field readback class: bins as_written{}, forced0{written 1, read 0}, forced_const{xdebugver reads 4 / cause unchanged}, legalised_u{prv 01/10 read 00}
  - cp_op = CSR op: bins rw{csrrw}, rs{csrrs}, rc{csrrc}, rwi{csrrwi}, rsi{csrrsi}, rci{csrrci}
- Crosses:
  - cr_bit_rb = cp_bit x cp_readback: bins ebreakm_w{ebreakm,as_written}, ebreaku_w{ebreaku,as_written}, step_w{step,as_written}, ebreaks_w{ebreaks,as_written}, prv_w{prv,as_written}, prv_leg{prv,legalised_u}, stepie_0{stepie,forced0}, stopcount_0{stopcount,forced0}, stoptime_0{stoptime,forced0}, mprven_0{mprven,forced0}, nmip_0{nmip,forced0}, z27_0{z27_16,forced0}, z14_0{z14,forced0}, z5_0{z5,forced0}, cause_c{cause,forced_const}, xdv_c{xdebugver,forced_const}; ignore ebreakm/ebreaku/step x forced0 and hardwired fields x as_written: contradictions are gen_chk_csr_readback failures. (ebreaks_w is B15 evidence: the spec-expected readback of bit 13 is 0, core_registers.xml:163-172.)
  - cr_pattern_op = cp_pattern x cp_op: bins zeros_rw{zeros,rw}, zeros_rc{zeros,rc}, ones_rw{ones,rw}, ones_rs{ones,rs}, ones_rc{ones,rc}, walk_rw{walk1,rw}, walk_rs{walk1,rs}, walk_rc{walk1,rc}, rand_rw{random,rw}, rand_rs{random,rs}, rand_rc{random,rc}, prv_rwi{prv_only,rwi}, prv_rsi{prv_only,rsi}, prv_rci{prv_only,rci}
  - cr_prvw_rb = cp_prv_w x cp_readback: bins s_leg{s,legalised_u}, h_leg{h,legalised_u}, m_w{m,as_written}, u_w{u,as_written}
- Adopted (riscv-dv): none
- TP items: TP-DBG-017, TP-DBG-018, TP-DBG-019, TP-DBG-020, TP-DBG-021, TP-DBG-048, TP-DBG-062, TP-DBG-068

### CG-DBG-008: gen_cg_dbg_csr_access
- Features: F-DBG-012, F-DBG-035, F-DBG-050, F-DBG-051, F-DBG-060
- Sample: RVFI item whose rvfi_insn is a CSR access to CSR_DCSR..CSR_DSCRATCH1 (0x7B0..0x7B3);
  condition: `rvfi_valid && csr_addr inside {CSR_DCSR, CSR_DPC, CSR_DSCRATCH0, CSR_DSCRATCH1}`;
  anti-vacuity: the result bin comes from rvfi_trap vs rvfi_rd_wdata and the mode from rvfi_mode /
  rvfi_ext_debug_mode, so a hit proves the access was attempted in that mode and what happened.
- Coverpoints:
  - cp_csr = CSR address decoded from rvfi_insn: bins dcsr{CSR_DCSR}, dpc{CSR_DPC}, dscratch0{CSR_DSCRATCH0}, dscratch1{CSR_DSCRATCH1}
  - cp_mode = rvfi_ext_debug_mode x rvfi_mode: bins dbg_m{debug, M}, dbg_u{debug, U after mret-in-debug}, m{not debug, M}, u{not debug, U}
  - cp_op = CSR op decoded from rvfi_insn: bins read{csrrs/csrrc rs1==x0 or csrrsi/csrrci uimm==0}, write{csrrw/csrrwi}, set{csrrs/csrrsi non-zero}, clear{csrrc/csrrci non-zero}
  - cp_result = {rvfi_trap, readback relation}: bins ok{no trap}, illegal{rvfi_trap, mcause 2}
  - cp_dpc_w = dpc write data bit 0: bins even{0}, odd{1}
  - cp_scratch_pat = dscratch write data: bins zeros{0}, ones{32'hFFFF_FFFF}, alt{32'hAAAA_5555 or 32'h5555_AAAA}, random{}
- Crosses:
  - cr_csr_mode_result = cp_csr x cp_mode x cp_result: bins dcsr_dbg_ok{dcsr,dbg_m,ok}, dpc_dbg_ok{dpc,dbg_m,ok}, ds0_dbg_ok{dscratch0,dbg_m,ok}, ds1_dbg_ok{dscratch1,dbg_m,ok}, dcsr_m_ill{dcsr,m,illegal}, dpc_m_ill{dpc,m,illegal}, ds0_m_ill{dscratch0,m,illegal}, ds1_m_ill{dscratch1,m,illegal}, dcsr_u_ill{dcsr,u,illegal}, dpc_u_ill{dpc,u,illegal}, ds0_u_ill{dscratch0,u,illegal}, ds1_u_ill{dscratch1,u,illegal}, dcsr_dbgu_ill{dcsr,dbg_u,illegal}; ignore * x m x ok, * x u x ok, * x dbg_m x illegal: checker failures.
  - cr_csr_op = cp_csr x cp_op: bins dcsr_rd{dcsr,read}, dcsr_wr{dcsr,write}, dcsr_set{dcsr,set}, dcsr_clr{dcsr,clear}, dpc_rd{dpc,read}, dpc_wr{dpc,write}, dpc_set{dpc,set}, dpc_clr{dpc,clear}, ds0_rd{dscratch0,read}, ds0_wr{dscratch0,write}, ds0_set{dscratch0,set}, ds0_clr{dscratch0,clear}, ds1_rd{dscratch1,read}, ds1_wr{dscratch1,write}, ds1_set{dscratch1,set}, ds1_clr{dscratch1,clear}
  - cr_dpcw_result = cp_dpc_w x cp_result: bins even_ok{even,ok}, odd_ok{odd,ok}
  - cr_scratch_pat_csr = cp_scratch_pat x cp_csr: bins zeros_ds0{zeros,dscratch0}, ones_ds0{ones,dscratch0}, alt_ds0{alt,dscratch0}, rand_ds0{random,dscratch0}, zeros_ds1{zeros,dscratch1}, ones_ds1{ones,dscratch1}, alt_ds1{alt,dscratch1}, rand_ds1{random,dscratch1}
- Adopted (riscv-dv): none
- TP items: TP-DBG-017, TP-DBG-018, TP-DBG-040, TP-DBG-055, TP-DBG-056, TP-DBG-064, TP-DBG-068

### CG-DBG-009: gen_cg_dbg_irq_mask
- Features: F-DBG-002, F-DBG-042, F-DBG-043, F-DBG-056, F-DBG-057, F-DBG-058, F-TRG-025
- Sample: one sample per pending episode: an enabled interrupt (irq model: |(pins & mie) with
  mstatus.MIE or U-mode) or irq_nm_i is pending while dbg_model.debug_mode==1 or step_window==1, or
  in the debug-entry decision cycle; closed when the disposition is known (first post-window RVFI
  item, or the driver deasserting); condition: `irq_pending_model && (debug_mode || step_window ||
  entry_cycle)`; anti-vacuity: the irq driver runs independently of debug windows, so overlap is not
  guaranteed; a hit proves an interrupt was pending inside a debug/step window, and the disposition
  is decoded from rvfi_intr / mepc readback, not from expectation.
- Coverpoints:
  - cp_src = interrupt source pin: bins sw{irq_software_i}, timer{irq_timer_i}, ext{irq_external_i}, fast{any of $bits(irq_fast_i) lines}, nmi{irq_nm_i}
  - cp_window = dbg_model window in which the interrupt was pending: bins debug{debug_mode}, step{between dret with step=1 and re-entry}, entry_cycle{pending in the debug-entry decision cycle}, irq_taken_then_req{debug_req_i arriving while IRQ_TAKEN is in progress}
  - cp_disposition = disposition decoded from rvfi_intr / mepc readback / driver log: bins masked_then_taken{taken at the first instruction after the window, mepc == dpc}, masked_still_pending{driver deasserted before the window ended, never taken}, debug_wins_entry{debug entered instead of the handler}, handler_then_debug{handler entry completed, then debug with dpc == vector}
  - cp_prv_after = privilege after the window (dcsr.prv): bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
- Crosses:
  - cr_src_window = cp_src x cp_window: bins sw_debug{sw,debug}, timer_debug{timer,debug}, ext_debug{ext,debug}, fast_debug{fast,debug}, nmi_debug{nmi,debug}, sw_step{sw,step}, timer_step{timer,step}, ext_step{ext,step}, fast_step{fast,step}, nmi_step{nmi,step}, sw_entry{sw,entry_cycle}, ext_entry{ext,entry_cycle}, fast_entry{fast,entry_cycle}, nmi_entry{nmi,entry_cycle}, ext_irqtaken{ext,irq_taken_then_req}, fast_irqtaken{fast,irq_taken_then_req}
  - cr_window_disp = cp_window x cp_disposition: bins debug_taken{debug,masked_then_taken}, debug_pending{debug,masked_still_pending}, step_taken{step,masked_then_taken}, step_pending{step,masked_still_pending}, entry_wins{entry_cycle,debug_wins_entry}, irqtaken_handler{irq_taken_then_req,handler_then_debug}
  - cr_src_prv = cp_src x cp_prv_after: bins sw_m{sw,m}, sw_u{sw,u}, timer_m{timer,m}, timer_u{timer,u}, ext_m{ext,m}, ext_u{ext,u}, fast_m{fast,m}, fast_u{fast,u}, nmi_m{nmi,m}, nmi_u{nmi,u}
- Adopted (riscv-dv): none
- TP items: TP-DBG-003, TP-DBG-016, TP-DBG-021, TP-DBG-047, TP-DBG-048, TP-DBG-061, TP-DBG-062, TP-DBG-068, TP-TRG-025

### CG-DBG-010: gen_cg_dbg_pmp_dm
- Features: F-DBG-027, F-DBG-030, F-DBG-033, F-DBG-052, F-DBG-053, F-DBG-054, F-DBG-055
- Sample: every fetch word (ibus request) and every data access (dbus request, or a PMP-model-denied
  access with the request suppressed and rvfi_trap) while dbg_model.debug_mode==1, plus data
  accesses in the post-dret window with MPRV still set (B1); condition: `(ibus_req || dbus_req ||
  pmp_model_denied) && (debug_mode || post_dret_mprv_window)`; anti-vacuity: addresses are
  randomized inside and outside the DM window and the PMP configuration is randomized to deny or
  allow them; the verdict bin comes from gen_chk_pmp's model for the effective privilege, so
  `deny_cfg x no_fault` can only be hit when the bypass fired.
- Coverpoints:
  - cp_access = access type (ibus request / dbus request with data_we_o): bins fetch{}, load{}, store{}
  - cp_addr = address class vs DmBaseAddr/DmAddrMask: bins dm_base{== DmBaseAddr}, dm_top{last word of the window, (DmBaseAddr|DmAddrMask)-3}, dm_in{inside, other}, dm_straddle{4-byte fetch at (DmBaseAddr|DmAddrMask)-1, second half outside}, below{[DmBaseAddr-4 : DmBaseAddr-1]}, above{[DmBaseAddr+DmAddrMask+1 : DmBaseAddr+DmAddrMask+4]}, far{outside, other}
  - cp_verdict = gen_chk_pmp verdict at the effective privilege ignoring the DM bypass: bins allow_cfg{}, deny_cfg{region denies}, deny_mmwp{no matching region, MMWP=1}, deny_mml{MML locked region without the permission}
  - cp_lsu_priv = effective LSU privilege (mstatus.MPRV ? MPP : priv): bins m{}, u_mprv{MPRV=1, MPP=U}, u_mode{priv U after mret-in-debug or after dret to U}
  - cp_result = {rvfi_trap, readback relation}: bins no_fault{request issued, no trap}, fault{rvfi_trap, DmExceptionAddr fetch or mtvec fetch}
  - cp_phase = dbg_model phase of the access: bins in_debug{debug_mode}, post_dret_u_mprv{U-mode after dret with MPRV=1, MPP=M}
- Crosses:
  - cr_bypass = cp_access x cp_addr x cp_verdict x cp_result: bins f_base_deny_ok{fetch,dm_base,deny_cfg,no_fault}, f_top_deny_ok{fetch,dm_top,deny_cfg,no_fault}, f_in_deny_ok{fetch,dm_in,deny_cfg,no_fault}, l_base_deny_ok{load,dm_base,deny_cfg,no_fault}, l_top_deny_ok{load,dm_top,deny_cfg,no_fault}, l_in_deny_ok{load,dm_in,deny_cfg,no_fault}, s_base_deny_ok{store,dm_base,deny_cfg,no_fault}, s_top_deny_ok{store,dm_top,deny_cfg,no_fault}, s_in_deny_ok{store,dm_in,deny_cfg,no_fault}, f_straddle_fault{fetch,dm_straddle,deny_cfg,fault}, f_below_fault{fetch,below,deny_cfg,fault}, f_above_fault{fetch,above,deny_cfg,fault}, l_below_fault{load,below,deny_cfg,fault}, l_above_fault{load,above,deny_cfg,fault}, s_below_fault{store,below,deny_cfg,fault}, s_above_fault{store,above,deny_cfg,fault}, f_far_allow{fetch,far,allow_cfg,no_fault}, l_far_allow{load,far,allow_cfg,no_fault}, s_far_allow{store,far,allow_cfg,no_fault}, f_far_mmwp{fetch,far,deny_mmwp,fault}, f_far_mml{fetch,far,deny_mml,fault}, l_far_mmwp{load,far,deny_mmwp,fault}, s_far_mml{store,far,deny_mml,fault}, l_in_mmwp_ok{load,dm_in,deny_mmwp,no_fault}, f_in_mml_ok{fetch,dm_in,deny_mml,no_fault}; ignore dm_* x deny_* x fault while in_debug: bypass failure is a gen_chk_pmp failure.
  - cr_lsu_priv = cp_access x cp_lsu_priv x cp_verdict x cp_result: bins l_umprv_far_fault{load,u_mprv,deny_cfg,fault}, s_umprv_far_fault{store,u_mprv,deny_cfg,fault}, l_m_far_ok{load,m,allow_cfg,no_fault}, l_umprv_dm_ok{load,u_mprv,deny_cfg,no_fault}, l_umode_far_fault{load,u_mode,deny_cfg,fault}, f_umode_fault{fetch,u_mode,deny_cfg,fault}; (B2 evidence: l_umprv_far_fault, s_umprv_far_fault)
  - cr_b1 = cp_phase x cp_access x cp_verdict x cp_result: bins b1_load_ok{post_dret_u_mprv,load,deny_cfg,no_fault}, b1_store_ok{post_dret_u_mprv,store,deny_cfg,no_fault}, dbg_load_ok{in_debug,load,allow_cfg,no_fault}; (B1 evidence: b1_load_ok, b1_store_ok: the verdict is computed for privilege U, the RTL used MPP=M)
- Adopted (riscv-dv): none
- TP items: TP-DBG-032, TP-DBG-033, TP-DBG-038, TP-DBG-057, TP-DBG-058, TP-DBG-059, TP-DBG-060, TP-DBG-064, TP-DBG-068

### CG-DBG-011: gen_cg_dbg_mode_misc
- Features: F-DBG-011, F-DBG-059, F-DBG-060, F-DBG-062, F-DBG-063, F-DBG-064, F-DBG-067
- Sample: RVFI retirement with rvfi_ext_debug_mode==1 (debug-program instruction); the fetch-repeat
  coverpoint samples on each ibus request while dbg_model.debug_mode==1; the counter coverpoint
  samples at dret with the deltas computed by gen_chk_counters over the window; condition:
  `(rvfi_valid && rvfi_ext_debug_mode) || (ibus_req && debug_mode) || dret_retired`; anti-vacuity:
  only debug-program instructions carry the flag; `repeat` is decoded from the ibus address history
  of the window, so a hit proves a re-fetch of an already-fetched address (the icache would have hit).
- Coverpoints:
  - cp_insn_class = debug-program instruction class: bins alu{}, load{}, store{}, csr_dbg{dcsr/dpc/dscratch}, csr_trig{tselect/tdata*}, csr_other{}, wfi{}, mret{}, ecall{}, fence_i{}, jump{}, branch{}, dret{}, illegal{}, ebreak{}
  - cp_wfi_pending = irq pending when a wfi retires in debug mode: bins none{}, irq_pending{}
  - cp_mret_mpp = mstatus.MPP when mret retires in debug mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_fetch_repeat = ibus fetch address in the debug window: bins first{not fetched before in this window}, repeat{fetched earlier in the same window}
  - cp_icache_en = cpuctrlsts.icache_enable (CSR model): bins off{0}, on{1}
  - cp_counter_moved = counter deltas across the debug window: bins mcycle{mcycle delta > 0}, minstret{minstret delta == debug-program retirements incl. dret}, hpm{some mhpmcounter3..12 delta > 0}
  - cp_mode = rvfi_mode inside debug mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_wfi_busy_dip = number of consecutive core_busy_o Off cycles between a debug-mode wfi retirement and the next ibus request: bins one{1}; anti-vacuity: sampled only on a wfi with rvfi_ext_debug_mode==1; any other count is a gen_chk_sleep failure (WAIT_SLEEP is one cycle and SLEEP stays busy with debug_mode_q set, rtl/ibex_controller.sv:598-621), so the bin proves the one-cycle shape was observed, not assumed.
- Crosses:
  - cr_fetch_icache = cp_fetch_repeat x cp_icache_en: bins repeat_on{repeat,on}, first_on{first,on}, repeat_off{repeat,off}; (repeat_on proves the forced-off icache: the re-fetch reached the bus although the cache was enabled)
  - cr_wfi = cp_insn_class x cp_wfi_pending: bins wfi_irq{wfi,irq_pending}, wfi_none{wfi,none}
  - cr_wfi_busy = cp_wfi_pending x cp_wfi_busy_dip: bins irq_one{irq_pending,one}, none_one{none,one}
  - cr_mret_mpp = cp_insn_class x cp_mret_mpp: bins mret_m{mret,m}, mret_u{mret,u}
  - cr_class_mode = cp_insn_class x cp_mode: bins alu_u{alu,u}, csrdbg_u{csr_dbg,u}, load_u{load,u}, alu_m{alu,m}, dret_m{dret,m}, dret_u{dret,u}
- Adopted (riscv-dv): none
- TP items: TP-DBG-001, TP-DBG-031, TP-DBG-035, TP-DBG-063, TP-DBG-064, TP-DBG-065, TP-DBG-066, TP-DBG-068, TP-PMC-049

### CG-DBG-012: gen_cg_dbg_rvfi_flags
- Features: F-DBG-064, F-DBG-065
- Sample: every rvfi_valid; condition: `rvfi_valid`; anti-vacuity: the four flag combinations need a
  debug request that overlaps retirements (req1_mode0) and a debug program (mode1); a hit in
  req1_mode0 proves the request was visible on a non-debug retirement, which only happens when the
  pipe was not yet drained.
- Coverpoints:
  - cp_flags = {rvfi_ext_debug_req, rvfi_ext_debug_mode}: bins req0_mode0{2'b00}, req1_mode0{2'b10}, req0_mode1{2'b01}, req1_mode1{2'b11}
  - cp_mode_dbg = {rvfi_mode, rvfi_ext_debug_mode}: bins m_dbg{PRIV_LVL_M,1}, u_dbg{PRIV_LVL_U,1}, m{PRIV_LVL_M,0}, u{PRIV_LVL_U,0}
  - cp_trap_dbg = {rvfi_trap, rvfi_ext_debug_mode}: bins trap_dbg{1,1}, trap{1,0}, ok_dbg{0,1}, ok{0,0}
- Crosses:
  - cr_flags_mode = cp_flags x cp_mode_dbg: bins req1_m{req1_mode0,m}, req1_u{req1_mode0,u}, mode1_m{req0_mode1,m_dbg}, mode1_u{req0_mode1,u_dbg}
- Adopted (riscv-dv): none
- TP items: TP-DBG-001, TP-DBG-002, TP-DBG-064, TP-DBG-068, TP-DBG-070

---------------------------------------------------------------------------------------------------

## TRG covergroups

### CG-TRG-001: gen_cg_trg_csr
- Features: F-TRG-001, F-TRG-002, F-TRG-003, F-TRG-004, F-TRG-005, F-TRG-006, F-TRG-007, F-TRG-008, F-TRG-009, F-TRG-028, F-TRG-029
- Sample: RVFI item whose rvfi_insn is a CSR access to {CSR_TSELECT, CSR_TDATA1, CSR_TDATA2,
  CSR_TDATA3, CSR_MCONTEXT, CSR_MSCONTEXT, CSR_SCONTEXT, 12'h7A4 (tinfo), 12'h7A5 (tcontrol)};
  write effect closed by the following csrr of the same CSR; condition: `rvfi_valid && csr_addr
  inside trigger_csr_set`; anti-vacuity: result bins come from rvfi_trap and the observed readback,
  so `ok_dropped` proves a write reached the CSR unit in that mode and did not stick, and `illegal`
  proves the trap.
- Coverpoints:
  - cp_csr = CSR address decoded from rvfi_insn: bins tselect{CSR_TSELECT}, tdata1{CSR_TDATA1}, tdata2{CSR_TDATA2}, tdata3{CSR_TDATA3}, mcontext{CSR_MCONTEXT}, mscontext{CSR_MSCONTEXT}, scontext{CSR_SCONTEXT}, tinfo{12'h7A4}, tcontrol{12'h7A5}
  - cp_mode = {rvfi_ext_debug_mode, rvfi_mode}: bins dbg{debug mode}, m{M, not debug}, u{U}
  - cp_op = CSR op decoded from rvfi_insn: bins read{no write}, write{csrrw/csrrwi}, set{csrrs non-zero}, clear{csrrc non-zero}
  - cp_result = {rvfi_trap, readback relation}: bins ok_applied{write, readback changed as predicted}, ok_dropped{write, no trap, readback unchanged}, ok_read{read, no trap}, illegal{rvfi_trap}
  - cp_tsel_w = tselect write data: bins zero{0}, one{1}, big{[2 : 32'hFFFF_FFFE]}, ones{32'hFFFF_FFFF}
  - cp_td1_w = tdata1 write-data class of the non-execute bits: bins zeros{all other bits 0}, ones{all other bits 1}, type_ne2{type field != 2}, dmode0{dmode bit 0}, ldst{load/store bits set}, match_nz{match field != 0}, action0{action field 0}, chain{chain bit}, hit1{bit 20 set}, random{}
  - cp_td1_exec_w = tdata1 write data bit 2: bins zero{0}, one{1}
  - cp_td2_w = tdata2 write data: bins zero{0}, ones{32'hFFFF_FFFF}, odd{bit0=1}, halfword{bit1=1,bit0=0}, msb{32'h8000_0000}, random{}
  - cp_td1_rb = tdata1 readback: bins dis{32'h2800_1048}, en{32'h2800_104C}, en_after_hit{32'h2800_104C read in the first debug window after a cause-2 entry: hit (bit 20) still 0, F-TRG-028 folded into F-TRG-003}
- Crosses:
  - cr_csr_mode_result = cp_csr x cp_mode x cp_result: bins tsel_dbg_app{tselect,dbg,ok_applied}, td1_dbg_app{tdata1,dbg,ok_applied}, td2_dbg_app{tdata2,dbg,ok_applied}, tsel_m_drop{tselect,m,ok_dropped}, td1_m_drop{tdata1,m,ok_dropped}, td2_m_drop{tdata2,m,ok_dropped}, td3_dbg_drop{tdata3,dbg,ok_dropped}, td3_m_drop{tdata3,m,ok_dropped}, mctx_dbg_drop{mcontext,dbg,ok_dropped}, mctx_m_drop{mcontext,m,ok_dropped}, msctx_dbg_drop{mscontext,dbg,ok_dropped}, msctx_m_drop{mscontext,m,ok_dropped}, sctx_dbg_drop{scontext,dbg,ok_dropped}, sctx_m_drop{scontext,m,ok_dropped}, tsel_u_ill{tselect,u,illegal}, td1_u_ill{tdata1,u,illegal}, td2_u_ill{tdata2,u,illegal}, td3_u_ill{tdata3,u,illegal}, mctx_u_ill{mcontext,u,illegal}, msctx_u_ill{mscontext,u,illegal}, sctx_u_ill{scontext,u,illegal}, tinfo_u_ill{tinfo,u,illegal}, tctl_u_ill{tcontrol,u,illegal}, tinfo_dbg_ill{tinfo,dbg,illegal}, tinfo_m_ill{tinfo,m,illegal}, tctl_dbg_ill{tcontrol,dbg,illegal}, tctl_m_ill{tcontrol,m,illegal}, tsel_dbg_rd{tselect,dbg,ok_read}, tsel_m_rd{tselect,m,ok_read}, td1_dbg_rd{tdata1,dbg,ok_read}, td1_m_rd{tdata1,m,ok_read}, td2_dbg_rd{tdata2,dbg,ok_read}, td2_m_rd{tdata2,m,ok_read}, td3_dbg_rd{tdata3,dbg,ok_read}, td3_m_rd{tdata3,m,ok_read}, mctx_dbg_rd{mcontext,dbg,ok_read}, mctx_m_rd{mcontext,m,ok_read}, msctx_dbg_rd{mscontext,dbg,ok_read}, msctx_m_rd{mscontext,m,ok_read}, sctx_dbg_rd{scontext,dbg,ok_read}, sctx_m_rd{scontext,m,ok_read}; ignore tinfo/tcontrol x ok_*: never decoded; ignore tdata3/mcontext/mscontext/scontext x ok_applied: no storage (B3 evidence bins are the *_drop bins).
  - cr_td1_exec_rb = cp_td1_exec_w x cp_td1_rb: bins e0_dis{zero,dis}, e1_en{one,en}; ignore zero x en, one x dis: WARL failure is a gen_chk_csr_readback failure.
  - cr_td1w_exec = cp_td1_w x cp_td1_exec_w: bins zeros_e0{zeros,zero}, zeros_e1{zeros,one}, ones_e0{ones,zero}, ones_e1{ones,one}, type_e1{type_ne2,one}, dmode0_e1{dmode0,one}, ldst_e1{ldst,one}, ldst_e0{ldst,zero}, match_e1{match_nz,one}, action0_e1{action0,one}, chain_e1{chain,one}, hit1_e1{hit1,one}, rand_e0{random,zero}, rand_e1{random,one}
  - cr_tselw_mode = cp_tsel_w x cp_mode: bins zero_dbg{zero,dbg}, one_dbg{one,dbg}, big_dbg{big,dbg}, ones_dbg{ones,dbg}, one_m{one,m}, ones_m{ones,m}
  - cr_td2w_mode = cp_td2_w x cp_mode: bins zero_dbg{zero,dbg}, ones_dbg{ones,dbg}, odd_dbg{odd,dbg}, half_dbg{halfword,dbg}, msb_dbg{msb,dbg}, rand_dbg{random,dbg}, rand_m{random,m}
  - cr_csr_op = cp_csr x cp_op: bins tsel_set{tselect,set}, tsel_clr{tselect,clear}, td1_set{tdata1,set}, td1_clr{tdata1,clear}, td2_set{tdata2,set}, td2_clr{tdata2,clear}, td3_wr{tdata3,write}, mctx_wr{mcontext,write}, msctx_wr{mscontext,write}, sctx_wr{scontext,write}, tinfo_rd{tinfo,read}, tinfo_wr{tinfo,write}, tctl_rd{tcontrol,read}, tctl_wr{tcontrol,write}
- Adopted (riscv-dv): none
- TP items: TP-TRG-001, TP-TRG-002, TP-TRG-003, TP-TRG-004, TP-TRG-005, TP-TRG-006, TP-TRG-007, TP-TRG-008, TP-TRG-009, TP-TRG-028, TP-TRG-029, TP-TRG-030, TP-TRG-031

### CG-TRG-002: gen_cg_trg_fire
- Features: F-TRG-010, F-TRG-011, F-TRG-012, F-TRG-013, F-TRG-014, F-TRG-015, F-TRG-016, F-TRG-017, F-TRG-018, F-TRG-019, F-TRG-020, F-TRG-021, F-TRG-022, F-TRG-023, F-TRG-024, F-TRG-025, F-TRG-026, F-TRG-027, F-TRG-030, F-DBG-066
- Sample: one sample each time the TB trigger model (tdata1.execute, tdata2 from the CSR model)
  sees the armed address become the next-to-execute address (derived from RVFI pc_wdata / trap and
  interrupt vectors / dret target / reset boot address), and each cause-2 debug entry; closed when
  either the DmHaltAddr fetch (fired) or the RVFI retirement of the armed address (not fired) is
  observed; condition: `armed_addr_reached || cause2_entry`; anti-vacuity: tdata2 is chosen to lie
  on real program addresses in a randomized fraction of iterations and off-path otherwise;
  `fired`/`not_fired` are decoded from the bus and RVFI, so a hit proves what happened when the
  armed address was reached.
- Coverpoints:
  - cp_ctx = how the armed address was reached / what it holds: bins seq32{32-bit instruction reached sequentially}, comp2{16-bit instruction at addr%4==2}, comp0{16-bit instruction at addr%4==0}, zcmp_first{address of a cm.* instruction}, zcmp_next{successor of a cm.* sequence}, mtvec_exc{exception vector}, mtvec_irq{interrupt vector}, mtvec_nmi{NMI vector mtvec+0x7C}, dret_tgt{dpc at dret}, jalr_tgt{jalr target}, br_tgt{taken-branch target}, fall_taken{fall-through of a taken branch}, fall_nottaken{fall-through of a not-taken branch}, fault_addr{fetch of the address faults (PMP/bus)}, dummy_slot{a dummy instruction was presented with that pc}, ibus_stall{fetch outstanding on the ibus when the match is evaluated}, ebreak_next{address following an ebreak-into-debug (B10)}, step_first{first instruction after dret with step=1}, in_debug{address executed inside debug mode}
  - cp_priv = privilege at the armed address: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_exec = tdata1.execute: bins off{0}, on{1}
  - cp_td2_lsb = tdata2 bit 0: bins even{0}, b0{1}
  - cp_dit = cpuctrlsts.data_ind_timing: bins off{0}, on{1}
  - cp_fired = trigger disposition decoded from the DmHaltAddr fetch vs RVFI retirement of the armed address: bins fired{DmHaltAddr fetch, cause 2, no retirement of the armed address}, not_fired{armed address retired}
  - cp_cause_rb = dcsr.cause readback at the entry: bins trigger{DBG_CAUSE_TRIGGER}, ebreak{DBG_CAUSE_EBREAK}; ignore_bins haltreq_step{DBG_CAUSE_HALTREQ, DBG_CAUSE_STEP}: trigger has priority over haltreq and step whenever the armed address is the next to execute (CTRL-25); `ebreak` is the spec-expected value for the B10 scenario.
  - cp_coincident = dbg_model event pending in the decision cycle: bins none{}, haltreq{debug_req_i high}, step{step armed}, irq{enabled interrupt pending}, nmi{irq_nm_i}, ebreak_prev{entry caused by an ebreak whose successor is the armed address}
  - cp_dpc_rel = dpc readback relation (sampled on entries only): bins eq_td2{dpc == tdata2}, eq_ebreak_pc{dpc == pc of the ebreak}; ignore_bins other{}: at a cause-2 or B10 entry dpc is one of the two by construction; any other value is a gen_chk_debug failure.
- Crosses:
  - cr_ctx_fired = cp_ctx x cp_fired: bins seq32_f{seq32,fired}, comp2_f{comp2,fired}, comp0_f{comp0,fired}, zfirst_f{zcmp_first,fired}, znext_f{zcmp_next,fired}, mtvec_exc_f{mtvec_exc,fired}, mtvec_irq_f{mtvec_irq,fired}, mtvec_nmi_f{mtvec_nmi,fired}, dret_f{dret_tgt,fired}, jalr_f{jalr_tgt,fired}, br_f{br_tgt,fired}, fallnt_f{fall_nottaken,fired}, fault_f{fault_addr,fired}, dummy_f{dummy_slot,fired}, stall_f{ibus_stall,fired}, stepfirst_f{step_first,fired}, falltaken_nf{fall_taken,not_fired}, indebug_nf{in_debug,not_fired}, seq32_nf{seq32,not_fired}; ignore fall_taken x fired: a match on a squashed fall-through never enters (checker failure); ignore in_debug x fired: triggers do not fire in debug mode.
  - cr_exec_fired = cp_exec x cp_fired: bins off_nf{off,not_fired}, on_f{on,fired}; ignore off x fired: checker failure.
  - cr_lsb_fired = cp_td2_lsb x cp_fired: bins b0_nf{b0,not_fired}, even_f{even,fired}; ignore b0 x fired: pc_if[0] is always 0.
  - cr_priv_fired = cp_priv x cp_fired: bins m_f{m,fired}, u_f{u,fired}, m_nf{m,not_fired}, u_nf{u,not_fired}
  - cr_dit_fall = cp_dit x cp_ctx x cp_fired: bins dit1_fallnt_f{on,fall_nottaken,fired}, dit1_falltaken_nf{on,fall_taken,not_fired}, dit0_falltaken_nf{off,fall_taken,not_fired}, dit0_fallnt_f{off,fall_nottaken,fired}
  - cr_coinc_cause = cp_coincident x cp_cause_rb: bins none_trig{none,trigger}, haltreq_trig{haltreq,trigger}, step_trig{step,trigger}, irq_trig{irq,trigger}, nmi_trig{nmi,trigger}, ebreakprev_trig{ebreak_prev,trigger}; (B10 evidence: ebreakprev_trig)
  - cr_cause_dpc = cp_cause_rb x cp_dpc_rel: bins trig_td2{trigger,eq_td2}, trig_ebreakpc{trigger,eq_ebreak_pc}, ebreak_ebreakpc{ebreak,eq_ebreak_pc}; (B10 evidence: trig_ebreakpc, an inconsistent pair)
- Adopted (riscv-dv): none
- TP items: TP-TRG-010, TP-TRG-011, TP-TRG-012, TP-TRG-013, TP-TRG-014, TP-TRG-015, TP-TRG-016, TP-TRG-017, TP-TRG-018, TP-TRG-019, TP-TRG-020, TP-TRG-021, TP-TRG-022, TP-TRG-023, TP-TRG-024, TP-TRG-025, TP-TRG-026, TP-TRG-027, TP-TRG-030, TP-TRG-031, TP-DBG-067

---------------------------------------------------------------------------------------------------

## PMC covergroups

### CG-PMC-001: gen_cg_pmc_mcycle
- Features: F-PMC-001, F-PMC-002, F-PMC-003, F-PMC-004, F-PMC-005, F-PMC-006, F-PMC-047, F-PMC-050, F-PMC-051, F-DBG-063
- Sample: RVFI retirement of a CSR access to CSR_MCYCLE / CSR_MCYCLEH (or the cycle/cycleh aliases),
  and the end of each TB window (WFI sleep, debug window, inhibit window, step) where
  gen_chk_counters compares the mcycle delta with elapsed clock cycles; condition: `rvfi_valid &&
  csr_addr inside {MCYCLE, MCYCLEH, CYCLE, CYCLEH} || window_end`; anti-vacuity: preload values are
  randomized so `near_wrap` and `carry` are reached only by construction; the delta class is
  computed from the observed readbacks against the cycle count measured at the boundary.
- Coverpoints:
  - cp_op = CSR op decoded from rvfi_insn: bins rd_lo{read mcycle}, rd_hi{read mcycleh}, wr_lo{csrrw mcycle}, wr_hi{csrrw mcycleh}, set_lo{csrrs}, set_hi{}, clr_lo{csrrc}, clr_hi{}
  - cp_wdata = write data class: bins zeros{0}, ones{32'hFFFF_FFFF}, random{}
  - cp_lo_before = low word before the write: bins near_wrap{[32'hFFFF_FF00 : 32'hFFFF_FFFF]}, mid{}, zero{0}
  - cp_carry = low word wrapped with high word incremented since the previous read: bins seen{}, none{}
  - cp_ctx = window class: bins run{}, wfi_sleep{core_busy_o low}, debug{debug window}, inhibited{mcountinhibit.CY=1}, step{single-step window}
  - cp_delta = delta vs measured cycles: bins zero{inhibited}, eq_cycles{== elapsed cycles}, eq_written{first read after a write == written (+ cycles since)}
- Crosses:
  - cr_op_wdata = cp_op x cp_wdata: bins wrlo_z{wr_lo,zeros}, wrlo_1{wr_lo,ones}, wrlo_r{wr_lo,random}, wrhi_z{wr_hi,zeros}, wrhi_1{wr_hi,ones}, wrhi_r{wr_hi,random}, setlo_z{set_lo,zeros}, setlo_1{set_lo,ones}, setlo_r{set_lo,random}, sethi_z{set_hi,zeros}, sethi_1{set_hi,ones}, sethi_r{set_hi,random}, clrlo_z{clr_lo,zeros}, clrlo_1{clr_lo,ones}, clrlo_r{clr_lo,random}, clrhi_z{clr_hi,zeros}, clrhi_1{clr_hi,ones}, clrhi_r{clr_hi,random}
  - cr_ctx_delta = cp_ctx x cp_delta: bins run_eq{run,eq_cycles}, wfi_eq{wfi_sleep,eq_cycles}, debug_eq{debug,eq_cycles}, step_eq{step,eq_cycles}, inh_zero{inhibited,zero}, run_written{run,eq_written}
  - cr_wr_lobefore = cp_op x cp_lo_before: bins wrhi_near{wr_hi,near_wrap}, wrlo_near{wr_lo,near_wrap}, wrhi_mid{wr_hi,mid}, wrlo_zero{wr_lo,zero}
  - cr_carry_ctx = cp_carry x cp_ctx: bins carry_run{seen,run}, carry_wfi{seen,wfi_sleep}, carry_debug{seen,debug}
- Adopted (riscv-dv): none
- TP items: TP-PMC-001, TP-PMC-002, TP-PMC-003, TP-PMC-004, TP-PMC-005, TP-PMC-006, TP-PMC-007, TP-PMC-049, TP-PMC-052, TP-PMC-053, TP-PMC-055, TP-DBG-066

### CG-PMC-002: gen_cg_pmc_minstret
- Features: F-PMC-007, F-PMC-008, F-PMC-009, F-PMC-010, F-PMC-011, F-PMC-012, F-PMC-013, F-PMC-014, F-PMC-022, F-PMC-046, F-PMC-047, F-PMC-048, F-PMC-050, F-PMC-051, F-PMC-052, F-DBG-063
- Sample: RVFI retirement of a CSR access to CSR_MINSTRET / CSR_MINSTRETH (or instret/instreth
  aliases); the window is everything retired since the previous minstret read; condition:
  `rvfi_valid && csr_addr inside {MINSTRET, MINSTRETH, INSTRET, INSTRETH}`; anti-vacuity: window
  bins are classified from the RVFI items observed in the window (trap kinds, Zcmp, dummies via the
  dummy_instr_en CSR state), so a hit proves the excluded/included class actually occurred; the
  coherence bin comes from the dbg_model WB-occupancy tracker in the read cycle.
- Coverpoints:
  - cp_op = CSR op decoded from rvfi_insn: bins rd_lo{}, rd_hi{}, wr_lo{}, wr_hi{}, set_lo{}, set_hi{}, clr_lo{}, clr_hi{}
  - cp_window = content of the window since the previous read: bins plain{only counted instructions}, has_ecall{}, has_ebreak_exc{}, has_ebreak_dbg{ebreak into debug}, has_illegal{}, has_fetch_fault{}, has_ls_fault{}, has_zcmp{cm.* sequence}, has_dummy{dummy_instr_en=1 in the window}, has_wfi{}, has_mret{}, has_dret{}, has_fence_i{}, has_self_write{csrw minstret/minstreth in the window}, has_irq{interrupt taken}, has_debug{debug window inside}, has_step{single step}
  - cp_coherence = WB state in the read cycle: bins wb_empty{}, wb_retiring{countable instruction in WB}, wb_faulting{WB load/store faults, reader flushed}
  - cp_wrap = low-word wrap detected between consecutive reads: bins carry{low word wrapped, high incremented}, none{}
  - cp_inhibit_ir = mcountinhibit.IR: bins off{0}, on{1}
  - cp_dummy_en = cpuctrlsts.dummy_instr_en: bins off{0}, on{1}
  - cp_wdata = CSR write data class: bins zeros{0}, ones{32'hFFFF_FFFF}, random{}
  - cp_delta = readback delta vs counted RVFI items in the window: bins eq_rvfi{==}, gt_rvfi{> (dummies, B7)}, zero{0}, one{1}
- Crosses:
  - cr_window_delta = cp_window x cp_delta: bins plain_eq{plain,eq_rvfi}, ecall_eq{has_ecall,eq_rvfi}, ebreakexc_eq{has_ebreak_exc,eq_rvfi}, ebreakdbg_eq{has_ebreak_dbg,eq_rvfi}, illegal_eq{has_illegal,eq_rvfi}, fetchfault_eq{has_fetch_fault,eq_rvfi}, lsfault_eq{has_ls_fault,eq_rvfi}, zcmp_eq{has_zcmp,eq_rvfi}, wfi_eq{has_wfi,eq_rvfi}, mret_eq{has_mret,eq_rvfi}, dret_eq{has_dret,eq_rvfi}, fencei_eq{has_fence_i,eq_rvfi}, selfwr_eq{has_self_write,eq_rvfi}, irq_eq{has_irq,eq_rvfi}, debug_eq{has_debug,eq_rvfi}, step_one{has_step,one}, step_zero{has_step,zero}, dummy_gt{has_dummy,gt_rvfi}, dummy_eq{has_dummy,eq_rvfi}; (B7 evidence: dummy_gt)
  - cr_coherence_op = cp_coherence x cp_op: bins retiring_rd{wb_retiring,rd_lo}, empty_rd{wb_empty,rd_lo}, faulting_rd{wb_faulting,rd_lo}, retiring_rdhi{wb_retiring,rd_hi}
  - cr_inhibit_coh = cp_inhibit_ir x cp_coherence: bins on_retiring{on,wb_retiring}, off_retiring{off,wb_retiring}
  - cr_op_wdata = cp_op x cp_wdata: bins wrlo_z{wr_lo,zeros}, wrlo_1{wr_lo,ones}, wrlo_r{wr_lo,random}, wrhi_z{wr_hi,zeros}, wrhi_1{wr_hi,ones}, wrhi_r{wr_hi,random}, setlo_1{set_lo,ones}, setlo_r{set_lo,random}, sethi_r{set_hi,random}, clrlo_1{clr_lo,ones}, clrlo_r{clr_lo,random}, clrhi_r{clr_hi,random}
  - cr_wrap_op = cp_wrap x cp_op: bins carry_rdhi{carry,rd_hi}, carry_rdlo{carry,rd_lo}
  - cr_dummy_delta = cp_dummy_en x cp_delta: bins dumon_gt{on,gt_rvfi}, dumoff_eq{off,eq_rvfi}, dumon_eq{on,eq_rvfi}
- Adopted (riscv-dv): none
- TP items: TP-PMC-008, TP-PMC-009, TP-PMC-010, TP-PMC-011, TP-PMC-012, TP-PMC-013, TP-PMC-014, TP-PMC-015, TP-PMC-016, TP-PMC-024, TP-PMC-048, TP-PMC-049, TP-PMC-050, TP-PMC-052, TP-PMC-053, TP-PMC-054, TP-PMC-055, TP-DBG-066

### CG-PMC-003: gen_cg_pmc_hpm_event
- Features: F-PMC-016, F-PMC-021, F-PMC-023, F-PMC-032, F-PMC-033, F-PMC-034, F-PMC-035, F-PMC-036, F-PMC-037, F-PMC-038, F-PMC-039, F-PMC-040, F-PMC-041, F-PMC-042, F-PMC-043, F-PMC-044, F-PMC-046, F-PMC-047, F-PMC-049, F-DBG-063
- Sample: end of each TB event window: a code window bounded by two CSR reads of the same
  mhpmcounterN (N in [MHPMCOUNTER_BASE : MHPMCOUNTER_BASE+MHPMCounterNum-1]); one sample per counter
  per window; condition: `window_end && counter_implemented`; anti-vacuity: the event count is
  measured independently by gen_chk_counters (dbus transactions, RVFI pc_wdata for jumps/branches,
  rvfi_insn width for compressed, ibus/dbus handshake gaps and multdiv opcodes for the wait
  counters), so `cp_events` is tied to an observed event count, never to the counter's own value.
- Coverpoints:
  - cp_idx = counter index: bins lsu_wait{MHPMCOUNTER_BASE+0}, if_wait{MHPMCOUNTER_BASE+1}, loads{MHPMCOUNTER_BASE+2}, stores{MHPMCOUNTER_BASE+3}, jumps{MHPMCOUNTER_BASE+4}, branches{MHPMCOUNTER_BASE+5}, taken{MHPMCOUNTER_BASE+6}, ret_c{MHPMCOUNTER_BASE+7}, mul_wait{MHPMCOUNTER_BASE+8}, div_wait{MHPMCOUNTER_BASE+9}; each bin generate-guarded by k < MHPMCounterNum
  - cp_events = independently measured event count in the window: bins zero{0}, one{1}, few{[2:15]}, many{[16:$]}, wrap{window crosses 2^32 after a preload}
  - cp_delta_rel = counter delta vs measured events: bins eq{==}, gt{>}, lt{< : only legal for a window containing a same-cycle counter write that drops one event, F-PMC-045}, zero{delta 0 with events > 0}
  - cp_inhibit = mcountinhibit[idx]: bins off{0}, on{1}
  - cp_variant = dominant event variant of the window (single-kind windows in Phase 1, `mixed` otherwise): bins aligned{}, misaligned{}, pmp_denied{}, straddle_pmp{}, bus_err{}, jal{}, jalr{}, c_j{}, c_jal{}, c_jr{}, c_jalr{}, popret{}, b_taken{}, b_not{}, c_beqz_taken{}, c_bnez_not{}, dit_on_taken{}, dit_on_not{}, c_alu{}, zcmp{}, mul{}, mulh{}, mulhsu{}, mulhu{}, dummy_mul{}, div{}, divu{}, rem{}, remu{}, div_zero{}, div_ovf{}, dummy_div{}, rvalid_delay{}, gnt_delay{}, ld_use_hazard{}, imem_latency{}, redirect{}, after_debug{}, mixed{}
  - cp_ctx = how the armed address was reached (RVFI / vector / dret / dummy probe / ibus state): bins run{}, debug{window inside debug mode}, step{window is a single step}
  - cp_dit = cpuctrlsts.data_ind_timing: bins off{0}, on{1}
- Crosses:
  - cr_idx_events = cp_idx x cp_events: bins lsu_0{lsu_wait,zero}, lsu_1{lsu_wait,one}, lsu_few{lsu_wait,few}, lsu_many{lsu_wait,many}, if_0{if_wait,zero}, if_1{if_wait,one}, if_few{if_wait,few}, if_many{if_wait,many}, ld_0{loads,zero}, ld_1{loads,one}, ld_few{loads,few}, ld_many{loads,many}, ld_wrap{loads,wrap}, st_0{stores,zero}, st_1{stores,one}, st_few{stores,few}, st_many{stores,many}, st_wrap{stores,wrap}, jmp_0{jumps,zero}, jmp_1{jumps,one}, jmp_few{jumps,few}, jmp_many{jumps,many}, jmp_wrap{jumps,wrap}, br_0{branches,zero}, br_1{branches,one}, br_few{branches,few}, br_many{branches,many}, br_wrap{branches,wrap}, tk_0{taken,zero}, tk_1{taken,one}, tk_few{taken,few}, tk_many{taken,many}, rc_0{ret_c,zero}, rc_1{ret_c,one}, rc_few{ret_c,few}, rc_many{ret_c,many}, rc_wrap{ret_c,wrap}, mul_0{mul_wait,zero}, mul_1{mul_wait,one}, mul_few{mul_wait,few}, mul_many{mul_wait,many}, div_0{div_wait,zero}, div_1{div_wait,one}, div_few{div_wait,few}, div_many{div_wait,many}; ignore lsu_wait/if_wait/taken/mul_wait/div_wait x wrap: cycle-class counters are wrapped via preload in cr_idx_inhibit items only when cheap; not required.
  - cr_idx_inhibit = cp_idx x cp_inhibit x cp_delta_rel: bins lsu_inh{lsu_wait,on,zero}, if_inh{if_wait,on,zero}, ld_inh{loads,on,zero}, st_inh{stores,on,zero}, jmp_inh{jumps,on,zero}, br_inh{branches,on,zero}, tk_inh{taken,on,zero}, rc_inh{ret_c,on,zero}, mul_inh{mul_wait,on,zero}, div_inh{div_wait,on,zero}, lsu_eq{lsu_wait,off,eq}, if_eq{if_wait,off,eq}, ld_eq{loads,off,eq}, st_eq{stores,off,eq}, jmp_eq{jumps,off,eq}, br_eq{branches,off,eq}, tk_eq{taken,off,eq}, rc_eq{ret_c,off,eq}, mul_eq{mul_wait,off,eq}, div_eq{div_wait,off,eq}
  - cr_variant_rel = cp_variant x cp_delta_rel: bins aligned_eq{aligned,eq}, misaligned_eq{misaligned,eq}, pmpden_eq{pmp_denied,eq}, straddle_eq{straddle_pmp,eq}, buserr_eq{bus_err,eq}, jal_eq{jal,eq}, jalr_eq{jalr,eq}, cj_eq{c_j,eq}, cjal_eq{c_jal,eq}, cjr_eq{c_jr,eq}, cjalr_eq{c_jalr,eq}, popret_eq{popret,eq}, btaken_eq{b_taken,eq}, bnot_eq{b_not,eq}, cbeqz_eq{c_beqz_taken,eq}, cbnez_eq{c_bnez_not,eq}, dittaken_eq{dit_on_taken,eq}, ditnot_gt{dit_on_not,gt}, ditnot_eq{dit_on_not,eq}, calu_eq{c_alu,eq}, zcmp_eq{zcmp,eq}, mul_eq{mul,eq}, mulh_eq{mulh,eq}, mulhsu_eq{mulhsu,eq}, mulhu_eq{mulhu,eq}, dummymul_gt{dummy_mul,gt}, div_eq{div,eq}, divu_eq{divu,eq}, rem_eq{rem,eq}, remu_eq{remu,eq}, divzero_eq{div_zero,eq}, divovf_eq{div_ovf,eq}, dummydiv_gt{dummy_div,gt}, rvalid_eq{rvalid_delay,eq}, gnt_eq{gnt_delay,eq}, hazard_eq{ld_use_hazard,eq}, imem_eq{imem_latency,eq}, redirect_eq{redirect,eq}, afterdbg_eq{after_debug,eq}, mixed_eq{mixed,eq}; (misaligned_eq is D6 evidence with the RTL count of one; ditnot_gt is B11 evidence on cp_idx taken; dummymul_gt/dummydiv_gt are B7 evidence)
  - cr_idx_ctx = cp_idx x cp_ctx: bins lsu_dbg{lsu_wait,debug}, if_dbg{if_wait,debug}, ld_dbg{loads,debug}, st_dbg{stores,debug}, jmp_dbg{jumps,debug}, br_dbg{branches,debug}, tk_dbg{taken,debug}, rc_dbg{ret_c,debug}, mul_dbg{mul_wait,debug}, div_dbg{div_wait,debug}, ld_step{loads,step}, br_step{branches,step}
  - cr_idx_dit = cp_idx x cp_dit: bins tk_dit1{taken,on}, tk_dit0{taken,off}, br_dit1{branches,on}, br_dit0{branches,off}
- Adopted (riscv-dv): none
- TP items: TP-PMC-018, TP-PMC-023, TP-PMC-025, TP-PMC-034, TP-PMC-035, TP-PMC-036, TP-PMC-037, TP-PMC-038, TP-PMC-039, TP-PMC-040, TP-PMC-041, TP-PMC-042, TP-PMC-043, TP-PMC-044, TP-PMC-045, TP-PMC-046, TP-PMC-048, TP-PMC-049, TP-PMC-051, TP-PMC-055, TP-DBG-066

### CG-PMC-004: gen_cg_pmc_hpm_csr
- Features: F-PMC-015, F-PMC-016, F-PMC-017, F-PMC-018, F-PMC-019, F-PMC-024, F-PMC-045, F-PMC-051
- Sample: RVFI retirement of any CSR access in [CSR_MHPMCOUNTER3 : CSR_MHPMCOUNTER31],
  [CSR_MHPMCOUNTER3H : CSR_MHPMCOUNTER31H], [CSR_MHPMEVENT3 : CSR_MHPMEVENT31]; closed by the
  following read of the same CSR; condition: `rvfi_valid && csr_addr inside hpm_csr_set`;
  anti-vacuity: result from rvfi_trap, readback class from the observed read value; index class
  decoded from the address against MHPMCounterNum.
- Coverpoints:
  - cp_idx = counter index class: bins first_impl{MHPMCOUNTER_BASE}, mid_impl{[MHPMCOUNTER_BASE+1 : MHPMCOUNTER_BASE+MHPMCounterNum-2]}, last_impl{MHPMCOUNTER_BASE+MHPMCounterNum-1}, first_unimpl{MHPMCOUNTER_BASE+MHPMCounterNum}, mid_unimpl{[MHPMCOUNTER_BASE+MHPMCounterNum+1 : 30]}, last_unimpl{31}
  - cp_reg = CSR address decoded from rvfi_insn: bins cnt_lo{mhpmcounterN}, cnt_hi{mhpmcounterNh}, event{mhpmeventN}
  - cp_op = CSR op decoded from rvfi_insn: bins read{}, write{}, set{}, clear{}
  - cp_mode = {rvfi_ext_debug_mode, rvfi_mode}: bins m{}, u{}, dbg{}
  - cp_result = {rvfi_trap, readback relation}: bins ok{}, illegal{rvfi_trap}
  - cp_wdata = CSR write data class: bins zeros{0}, ones{32'hFFFF_FFFF}, random{}
  - cp_rb = readback class: bins eq_written{implemented low word == written}, zero{reads 0}, const_onehot{mhpmeventN == 1 << N}
- Crosses:
  - cr_idx_reg_op = cp_idx x cp_reg x cp_op: bins fi_lo_rd{first_impl,cnt_lo,read}, fi_lo_wr{first_impl,cnt_lo,write}, fi_hi_rd{first_impl,cnt_hi,read}, fi_hi_wr{first_impl,cnt_hi,write}, fi_ev_rd{first_impl,event,read}, fi_ev_wr{first_impl,event,write}, mi_lo_rd{mid_impl,cnt_lo,read}, mi_lo_wr{mid_impl,cnt_lo,write}, mi_hi_rd{mid_impl,cnt_hi,read}, mi_hi_wr{mid_impl,cnt_hi,write}, mi_ev_rd{mid_impl,event,read}, mi_ev_wr{mid_impl,event,write}, li_lo_rd{last_impl,cnt_lo,read}, li_lo_wr{last_impl,cnt_lo,write}, li_hi_rd{last_impl,cnt_hi,read}, li_hi_wr{last_impl,cnt_hi,write}, li_ev_rd{last_impl,event,read}, li_ev_wr{last_impl,event,write}, fu_lo_rd{first_unimpl,cnt_lo,read}, fu_lo_wr{first_unimpl,cnt_lo,write}, fu_hi_rd{first_unimpl,cnt_hi,read}, fu_hi_wr{first_unimpl,cnt_hi,write}, fu_ev_rd{first_unimpl,event,read}, fu_ev_wr{first_unimpl,event,write}, mu_lo_rd{mid_unimpl,cnt_lo,read}, mu_lo_wr{mid_unimpl,cnt_lo,write}, mu_hi_rd{mid_unimpl,cnt_hi,read}, mu_hi_wr{mid_unimpl,cnt_hi,write}, mu_ev_rd{mid_unimpl,event,read}, mu_ev_wr{mid_unimpl,event,write}, lu_lo_rd{last_unimpl,cnt_lo,read}, lu_lo_wr{last_unimpl,cnt_lo,write}, lu_hi_rd{last_unimpl,cnt_hi,read}, lu_hi_wr{last_unimpl,cnt_hi,write}, lu_ev_rd{last_unimpl,event,read}, lu_ev_wr{last_unimpl,event,write}, fi_lo_set{first_impl,cnt_lo,set}, fi_lo_clr{first_impl,cnt_lo,clear}, fi_hi_set{first_impl,cnt_hi,set}, fi_ev_set{first_impl,event,set}, li_lo_set{last_impl,cnt_lo,set}, li_lo_clr{last_impl,cnt_lo,clear}, li_hi_clr{last_impl,cnt_hi,clear}, li_ev_clr{last_impl,event,clear}, fu_lo_set{first_unimpl,cnt_lo,set}, lu_ev_clr{last_unimpl,event,clear}
  - cr_mode_result = cp_mode x cp_result: bins m_ok{m,ok}, dbg_ok{dbg,ok}, u_ill{u,illegal}; ignore u x ok, m x illegal, dbg x illegal: privilege-check failure is a gen_isa_compare failure.
  - cr_idx_reg_rb = cp_idx x cp_reg x cp_rb: bins fi_lo_eq{first_impl,cnt_lo,eq_written}, mi_lo_eq{mid_impl,cnt_lo,eq_written}, li_lo_eq{last_impl,cnt_lo,eq_written}, fi_hi_0{first_impl,cnt_hi,zero}, mi_hi_0{mid_impl,cnt_hi,zero}, li_hi_0{last_impl,cnt_hi,zero}, fu_lo_0{first_unimpl,cnt_lo,zero}, mu_lo_0{mid_unimpl,cnt_lo,zero}, lu_lo_0{last_unimpl,cnt_lo,zero}, fu_hi_0{first_unimpl,cnt_hi,zero}, lu_hi_0{last_unimpl,cnt_hi,zero}, fi_ev_1h{first_impl,event,const_onehot}, mi_ev_1h{mid_impl,event,const_onehot}, li_ev_1h{last_impl,event,const_onehot}, fu_ev_0{first_unimpl,event,zero}, mu_ev_0{mid_unimpl,event,zero}, lu_ev_0{last_unimpl,event,zero}
  - cr_wdata_reg = cp_wdata x cp_reg: bins z_lo{zeros,cnt_lo}, o_lo{ones,cnt_lo}, r_lo{random,cnt_lo}, z_hi{zeros,cnt_hi}, o_hi{ones,cnt_hi}, r_hi{random,cnt_hi}, z_ev{zeros,event}, o_ev{ones,event}, r_ev{random,event}
- Adopted (riscv-dv): none
- TP items: TP-PMC-017, TP-PMC-018, TP-PMC-019, TP-PMC-020, TP-PMC-021, TP-PMC-026, TP-PMC-047, TP-PMC-053, TP-PMC-055

### CG-PMC-005: gen_cg_pmc_ctrl_csr
- Features: F-PMC-020, F-PMC-021, F-PMC-022, F-PMC-023, F-PMC-024, F-PMC-025, F-PMC-026, F-PMC-031
- Sample: RVFI retirement of a CSR access to CSR_MCOUNTINHIBIT or CSR_MCOUNTEREN, sampled once per
  set bit of the effective write data (reads sample once with cp_bit = none); the write effect is
  closed by the following read; the mcounteren_writable_i pin value is sampled from the DUT
  boundary in the write cycle; condition: `rvfi_valid && csr_addr inside {CSR_MCOUNTINHIBIT,
  CSR_MCOUNTEREN}`; anti-vacuity: result and readback come from RVFI; `dropped` is only recorded when
  the readback differs from the WARL prediction of an applied write, so a hit proves the pin gate.
- Coverpoints:
  - cp_reg = CSR address decoded from rvfi_insn: bins inhibit{CSR_MCOUNTINHIBIT}, en{CSR_MCOUNTEREN}
  - cp_bit = field of the sampled set bit: bins cy{0}, tm{1}, ir{2}, hpm_first{MHPMCOUNTER_BASE}, hpm_mid{[MHPMCOUNTER_BASE+1 : MHPMCOUNTER_BASE+MHPMCounterNum-2]}, hpm_last{MHPMCOUNTER_BASE+MHPMCounterNum-1}, upper{[MHPMCOUNTER_BASE+MHPMCounterNum : 31]}, none{read}
  - cp_pattern = write-data pattern class: bins zeros{0}, ones{32'hFFFF_FFFF}, walk1{single bit}, random{}
  - cp_op = CSR op decoded from rvfi_insn: bins read{}, write{}, set{}, clear{}
  - cp_mode = {rvfi_ext_debug_mode, rvfi_mode} of the item: bins m{}, u{}, dbg{}
  - cp_result = {rvfi_trap, readback relation}: bins ok{}, illegal{rvfi_trap}
  - cp_rb = per-bit readback: bins as_written{}, forced0{written 1, read 0}
  - cp_pin = mcounteren_writable_i: bins on{IbexMuBiOn}, off{IbexMuBiOff}, invalid{any other 4-bit value}
  - cp_effect = write effect: bins applied{}, dropped{}
- Crosses:
  - cr_reg_bit_rb = cp_reg x cp_bit x cp_rb: bins inh_cy_w{inhibit,cy,as_written}, inh_ir_w{inhibit,ir,as_written}, inh_hf_w{inhibit,hpm_first,as_written}, inh_hm_w{inhibit,hpm_mid,as_written}, inh_hl_w{inhibit,hpm_last,as_written}, inh_tm_0{inhibit,tm,forced0}, inh_up_0{inhibit,upper,forced0}, en_cy_w{en,cy,as_written}, en_ir_w{en,ir,as_written}, en_hf_w{en,hpm_first,as_written}, en_hm_w{en,hpm_mid,as_written}, en_hl_w{en,hpm_last,as_written}, en_tm_0{en,tm,forced0}, en_up_0{en,upper,forced0}; ignore tm/upper x as_written, cy/ir/hpm_* x forced0: checker failures.
  - cr_en_pin_effect = cp_reg x cp_pin x cp_effect: bins en_on_app{en,on,applied}, en_off_drop{en,off,dropped}, en_inv_drop{en,invalid,dropped}, inh_off_app{inhibit,off,applied}, inh_inv_app{inhibit,invalid,applied}, inh_on_app{inhibit,on,applied}; ignore en x off/invalid x applied: gate failure is a gen_chk_csr_readback failure.
  - cr_reg_pattern_op = cp_reg x cp_pattern x cp_op: bins inh_z_wr{inhibit,zeros,write}, inh_1_wr{inhibit,ones,write}, inh_w_wr{inhibit,walk1,write}, inh_r_wr{inhibit,random,write}, inh_1_set{inhibit,ones,set}, inh_w_set{inhibit,walk1,set}, inh_r_set{inhibit,random,set}, inh_1_clr{inhibit,ones,clear}, inh_w_clr{inhibit,walk1,clear}, inh_r_clr{inhibit,random,clear}, en_z_wr{en,zeros,write}, en_1_wr{en,ones,write}, en_w_wr{en,walk1,write}, en_r_wr{en,random,write}, en_1_set{en,ones,set}, en_w_set{en,walk1,set}, en_r_set{en,random,set}, en_1_clr{en,ones,clear}, en_w_clr{en,walk1,clear}, en_r_clr{en,random,clear}
  - cr_reg_mode_result = cp_reg x cp_mode x cp_result: bins inh_m_ok{inhibit,m,ok}, inh_dbg_ok{inhibit,dbg,ok}, inh_u_ill{inhibit,u,illegal}, en_m_ok{en,m,ok}, en_dbg_ok{en,dbg,ok}, en_u_ill{en,u,illegal}
- Adopted (riscv-dv): none
- TP items: TP-PMC-022, TP-PMC-023, TP-PMC-024, TP-PMC-025, TP-PMC-026, TP-PMC-027, TP-PMC-028, TP-PMC-033, TP-PMC-055

### CG-PMC-006: gen_cg_pmc_alias
- Features: F-PMC-024, F-PMC-027, F-PMC-028, F-PMC-029, F-PMC-030, F-PMC-031
- Sample: RVFI item whose rvfi_insn is a CSR access in [12'hC00 : 12'hC1F] or [12'hC80 : 12'hC9F];
  condition: `rvfi_valid && csr_addr inside alias_set`; anti-vacuity: result from rvfi_trap;
  mcounteren bit from the CSR model at the access; privilege from rvfi_mode; a hit in `u x set x ok`
  proves the gate opened for that bit, `u x clr x illegal` proves it closed.
- Coverpoints:
  - cp_alias = alias CSR address decoded from rvfi_insn: bins cycle{12'hC00}, time{12'hC01}, instret{12'hC02}, hpm_first{12'hC00+MHPMCOUNTER_BASE}, hpm_mid{[12'hC00+MHPMCOUNTER_BASE+1 : 12'hC00+MHPMCOUNTER_BASE+MHPMCounterNum-2]}, hpm_last{12'hC00+MHPMCOUNTER_BASE+MHPMCounterNum-1}, hpm_unimpl{[12'hC00+MHPMCOUNTER_BASE+MHPMCounterNum : 12'hC1F]}, cycleh{12'hC80}, timeh{12'hC81}, instreth{12'hC82}, hpmh_first{12'hC80+MHPMCOUNTER_BASE}, hpmh_mid{[12'hC80+MHPMCOUNTER_BASE+1 : 12'hC80+MHPMCOUNTER_BASE+MHPMCounterNum-2]}, hpmh_last{12'hC80+MHPMCOUNTER_BASE+MHPMCounterNum-1}, hpmh_unimpl{[12'hC80+MHPMCOUNTER_BASE+MHPMCounterNum : 12'hC9F]}
  - cp_en_bit = mcounteren[addr[4:0]]: bins clr{0}, set{1}
  - cp_mode = {rvfi_ext_debug_mode, rvfi_mode} of the item: bins m{}, u{}, dbg{}
  - cp_op = CSR op decoded from rvfi_insn: bins read{no write}, write{csrrw/csrrwi}, set_nz{csrrs/csrrsi non-zero}, clr_nz{csrrc/csrrci non-zero}
  - cp_result = {rvfi_trap, readback relation}: bins ok{}, illegal{rvfi_trap}
  - cp_inhibited = mcountinhibit[addr[4:0]]: bins no{0}, yes{1}
- Crosses:
  - cr_alias_gate = cp_alias x cp_en_bit x cp_mode x cp_result: bins cyc_u_set_ok{cycle,set,u,ok}, cyc_u_clr_ill{cycle,clr,u,illegal}, cyc_m_clr_ok{cycle,clr,m,ok}, ir_u_set_ok{instret,set,u,ok}, ir_u_clr_ill{instret,clr,u,illegal}, ir_m_clr_ok{instret,clr,m,ok}, hf_u_set_ok{hpm_first,set,u,ok}, hf_u_clr_ill{hpm_first,clr,u,illegal}, hf_m_clr_ok{hpm_first,clr,m,ok}, hm_u_set_ok{hpm_mid,set,u,ok}, hm_u_clr_ill{hpm_mid,clr,u,illegal}, hm_m_clr_ok{hpm_mid,clr,m,ok}, hl_u_set_ok{hpm_last,set,u,ok}, hl_u_clr_ill{hpm_last,clr,u,illegal}, hl_m_clr_ok{hpm_last,clr,m,ok}, cych_u_set_ok{cycleh,set,u,ok}, cych_u_clr_ill{cycleh,clr,u,illegal}, cych_m_clr_ok{cycleh,clr,m,ok}, irh_u_set_ok{instreth,set,u,ok}, irh_u_clr_ill{instreth,clr,u,illegal}, irh_m_clr_ok{instreth,clr,m,ok}, hhf_u_set_ok{hpmh_first,set,u,ok}, hhf_u_clr_ill{hpmh_first,clr,u,illegal}, hhf_m_clr_ok{hpmh_first,clr,m,ok}, hhm_u_set_ok{hpmh_mid,set,u,ok}, hhm_u_clr_ill{hpmh_mid,clr,u,illegal}, hhm_m_clr_ok{hpmh_mid,clr,m,ok}, hhl_u_set_ok{hpmh_last,set,u,ok}, hhl_u_clr_ill{hpmh_last,clr,u,illegal}, hhl_m_clr_ok{hpmh_last,clr,m,ok}, hu_u_ill{hpm_unimpl,clr,u,illegal}, hu_m_ok{hpm_unimpl,clr,m,ok}, hhu_u_ill{hpmh_unimpl,clr,u,illegal}, hhu_m_ok{hpmh_unimpl,clr,m,ok}, time_m_ill{time,clr,m,illegal}, time_u_ill{time,clr,u,illegal}, timeh_m_ill{timeh,clr,m,illegal}, timeh_u_ill{timeh,clr,u,illegal}, cyc_dbg_ok{cycle,clr,dbg,ok}, ir_dbg_ok{instret,clr,dbg,ok}, hf_dbg_ok{hpm_first,clr,dbg,ok}; ignore hpm_unimpl/hpmh_unimpl/time/timeh x set: the mcounteren bits for these indices are hardwired 0; ignore u x clr x ok, u x set x illegal (readable aliases): gate failures are gen_isa_compare failures.
  - cr_op_result = cp_op x cp_result: bins rd_ok{read,ok}, rd_ill{read,illegal}, wr_ill{write,illegal}, set_ill{set_nz,illegal}, clr_ill{clr_nz,illegal}; ignore write/set_nz/clr_nz x ok: the range is read-only in every mode.
  - cr_write_alias = cp_alias x cp_op x cp_mode: bins cyc_wr_m{cycle,write,m}, cyc_wr_u{cycle,write,u}, ir_set_m{instret,set_nz,m}, hf_clr_m{hpm_first,clr_nz,m}, cych_wr_m{cycleh,write,m}, hhu_wr_m{hpmh_unimpl,write,m}, hu_wr_u{hpm_unimpl,write,u}
  - cr_inhibit_gate = cp_inhibited x cp_en_bit x cp_mode x cp_result: bins inh_set_u_ok{yes,set,u,ok}, noinh_set_u_ok{no,set,u,ok}
- Adopted (riscv-dv): none
- TP items: TP-PMC-026, TP-PMC-029, TP-PMC-030, TP-PMC-031, TP-PMC-032, TP-PMC-033, TP-PMC-055

### CG-PMC-007: gen_cg_pmc_write_timing
- Features: F-PMC-004, F-PMC-005, F-PMC-014, F-PMC-023, F-PMC-045, F-PMC-051
- Sample: each retired CSR write op to a counter CSR (mcycle(h), minstret(h), mhpmcounterN(h) for
  implemented N), with the same-cycle event state taken from gen_chk_counters' boundary model in the
  write cycle; condition: `rvfi_valid && csr_addr inside counter_csr_set && is_write`; anti-vacuity:
  the coincidence bins are reached only when the randomized instruction stream places an event in the
  write cycle; the model records the write-wins evidence (expected value == written, not written+1),
  so a hit proves the coincidence occurred.
- Coverpoints:
  - cp_target = counter CSR address decoded from rvfi_insn: bins mcycle{CSR_MCYCLE}, mcycleh{CSR_MCYCLEH}, minstret{CSR_MINSTRET}, minstreth{CSR_MINSTRETH}, hpm_lo{[CSR_MHPMCOUNTER3 : CSR_MHPMCOUNTER3+MHPMCounterNum-1]}, hpm_hi{[CSR_MHPMCOUNTER3H : CSR_MHPMCOUNTER3H+MHPMCounterNum-1]}
  - cp_coincident = event of the written counter firing in the write cycle: bins none{}, retire_in_wb{countable instruction retiring in WB}, lsu_wait_cycle{}, if_wait_cycle{}, load_req{}, store_req{}, jump{}, branch{}, cycle_tick{always true for mcycle(h)}
  - cp_inhibited = mcountinhibit bit of the target at the write: bins no{0}, yes{1}
  - cp_then = later behaviour: bins uninhibit_after{inhibit bit cleared later, counting resumed from the written value}, stay{}
  - cp_low_all_ones = low word == 32'hFFFF_FFFF in the write cycle (high-half writes): bins yes{}, no{}
- Crosses:
  - cr_target_coinc = cp_target x cp_coincident: bins mcycle_tick{mcycle,cycle_tick}, mcycleh_tick{mcycleh,cycle_tick}, minstret_ret{minstret,retire_in_wb}, minstreth_ret{minstreth,retire_in_wb}, hpm_lsu{hpm_lo,lsu_wait_cycle}, hpm_if{hpm_lo,if_wait_cycle}, hpm_load{hpm_lo,load_req}, hpm_store{hpm_lo,store_req}, hpm_jump{hpm_lo,jump}, hpm_branch{hpm_lo,branch}, hpmh_load{hpm_hi,load_req}, hpm_none{hpm_lo,none}
  - cr_target_inh_then = cp_target x cp_inhibited x cp_then: bins mcycle_inh_resume{mcycle,yes,uninhibit_after}, minstret_inh_resume{minstret,yes,uninhibit_after}, hpm_inh_resume{hpm_lo,yes,uninhibit_after}, hpm_noinh{hpm_lo,no,stay}
  - cr_hi_lowones = cp_target x cp_low_all_ones: bins mcycleh_ones{mcycleh,yes}, minstreth_ones{minstreth,yes}, mcycleh_no{mcycleh,no}
- Adopted (riscv-dv): none
- TP items: TP-PMC-005, TP-PMC-006, TP-PMC-016, TP-PMC-025, TP-PMC-047, TP-PMC-053, TP-PMC-055

### CG-PMC-008: gen_cg_pmc_rvfi_ext
- Features: F-PMC-001, F-PMC-015, F-PMC-049
- Sample: every rvfi_valid; condition: `rvfi_valid`; anti-vacuity: the relation bins compare
  consecutive items' rvfi_ext_mcycle / rvfi_ext_mhpmcounters with the retired CSR writes in the same
  stream; `jump_after_write` requires a preceding retired mcycle write, `eq_inhibited` a retired
  mcountinhibit write with CY=1, so a hit proves the exported value tracked the CSR.
- Coverpoints:
  - cp_mcycle_rel = rvfi_ext_mcycle vs previous item: bins inc{greater, no write in between}, eq_after_write{== written value + cycles}, jump_after_write{discontinuity following a retired mcycle(h) write}, eq_inhibited{unchanged while CY inhibited}
  - cp_hpm_hi = rvfi_ext_mhpmcountersh: bins all_zero{every element 0}
  - cp_hpm_moved = number of rvfi_ext_mhpmcounters elements that changed vs the previous item: bins none{0}, one{1}, several{[2:MHPMCounterNum]}
  - cp_debug = rvfi_ext_debug_mode: bins no{0}, yes{1}
- Crosses:
  - cr_rel_debug = cp_mcycle_rel x cp_debug: bins inc_dbg{inc,yes}, inc_run{inc,no}, jump_run{jump_after_write,no}, inh_run{eq_inhibited,no}
  - cr_moved_debug = cp_hpm_moved x cp_debug: bins one_dbg{one,yes}, several_run{several,no}, none_run{none,no}
- Adopted (riscv-dv): none
- TP items: TP-PMC-001, TP-PMC-003, TP-PMC-017, TP-PMC-051, TP-PMC-055

---------------------------------------------------------------------------------------------------

## Counts
- Covergroups: 22
- Coverpoints: 136
- Coverpoint bins: 619
- Cross bins: 884
- Adopted (riscv-dv) bins: 0
- Bins referenced by at least one TP item: 1503 of 1503
- Fix-brief additions (Critic v1): CG-DBG-001.cp_entry_ctx.flush_wfi, CG-DBG-001.cp_busy_dip (3 bins),
  CG-DBG-001.cr_cause_ctx.haltreq_flush_wfi, CG-DBG-001.cr_ctx_busy (3 bins) for F-DBG-068 and the
  one-cycle core_busy_o dip (F-DBG-044/059); CG-DBG-011.cp_wfi_busy_dip.one and cr_wfi_busy (2 bins);
  CG-TRG-001.cp_td1_rb.en_after_hit carries the folded F-TRG-028. Feature lists keep ALIAS/FOLDED IDs
  (traceability resolves them to the canonical or parent ID).
- Note: trace_tp_bin_dbg_trg_pmc.csv lists, for every cross bin an item names, the component
  coverpoint bins that cross bin implies (a cross hit requires them), so each item's rows are the
  full set of bins the fcov-expectation manifest must declare for it.

## Probe candidates
- CG-DBG-001.cp_entry_ctx (all bins) and CG-DBG-002.cp_coincident: derived from the TB dbg_model
  (RVFI + bus monitors). The FLUSH/IRQ_TAKEN/DBG_TAKEN_* distinction is a controller-FSM property;
  if the model proves ambiguous the fallback is the RTL's own coverage nets `fcov_debug_entry_if`,
  `fcov_debug_entry_id`, `fcov_interrupt_taken`, `fcov_pipe_flush`, `fcov_debug_wakeup`
  (rtl/ibex_controller.sv:1085-1095) or `ctrl_fsm_cs` (tb-infra probe candidate P4), coverage-only.
- CG-TRG-002.cp_ctx.dummy_slot: whether a dummy instruction occupied the matched pc is invisible at
  the boundary (RVFI excludes dummies). Boundary alternative: none reliable. Needs
  `dummy_instr_id_o` (ibex_core port wired inside gen_dut_top; tb-infra probe candidate P1),
  coverage-only.
- CG-PMC-002.cp_window.has_dummy, CG-PMC-003.cp_variant.dummy_mul / dummy_div: "a dummy was inserted
  in the window" is inferred from cpuctrlsts.dummy_instr_en=1 plus a delta > RVFI count; to bin the
  dummy type (mul/div) the same `dummy_instr_id_o` probe (P1) is needed, coverage-only.
- CG-PMC-003.cp_idx.lsu_wait / if_wait / mul_wait / div_wait with cp_delta_rel.eq: the exact
  cycle-class event count is measured from bus handshake gaps and multdiv latency tables; if the
  boundary model cannot reach cycle accuracy the bins degrade to bounds (gen_chk_counters checks
  bounds) and `eq` becomes a probe candidate on `perf_dside_wait_o`, `perf_iside_wait_o`,
  `perf_mul_wait_o`, `perf_div_wait_o` (ibex_id_stage / ibex_core internal nets), coverage-only.
- CG-PMC-002.cp_coherence.wb_retiring / wb_faulting and CG-PMC-007.cp_coincident: WB occupancy in
  the read/write cycle is reconstructed from RVFI order and dbus timing; fallback probe
  `instr_done_wb` / `perf_instr_ret_wb_spec_o` (ibex_wb_stage), coverage-only.
- CG-TRG-002.cp_ctx.ibus_stall: "match evaluated while the fetch is outstanding" is derived from the
  ibus monitor (request granted, rvalid pending) at the time of the DmHaltAddr fetch; no probe
  needed unless the timing is ambiguous, then `pc_if_o` (ibex_if_stage), coverage-only.
No checker depends on any of these; every probe would be registered before use per tb-infra
section e.


# 3.6 Areas IMEM, DMEM, FE, IC: Instruction and data memory protocol, LSU, fetch stage, instruction cache


T-006 subagent output for the area group IMEM, DMEM, FE, IC (156 feature IDs after the Critic v1
fixes: F-IMEM-001..032, F-DMEM-001..051, F-FE-001..025, F-IC-001..048; 129 ACTIVE, 11 ALIAS, 16
FOLDED; ALIAS/FOLDED IDs may still appear in Features lists, traceability resolves them to the
canonical ID). Companion of tp_mem_fetch_icache.md. Every covergroup lives in the gen_ namespace
and samples from the DUT boundary, the memory/RAM/key agents' own transaction records, or RVFI;
the exceptions are marked as probe candidates P1 (dummy_instr_id_o, CG-FE-004) and P2 (shadow tag
view, CG-IC-003); P3 (icache output handshake), P4 (LSU CTX states) and P5 (register-file seam)
are named in the feature part and have no bin until a probe register entry exists.
Parameter sources: rtl/ibex_pkg.sv (IC_NUM_WAYS=2, IC_NUM_LINES=256, IC_LINE_BEATS=2,
IC_INDEX_W=8); rtl/ibex_icache.sv NUM_FB=4, FB_THRESHOLD=NUM_FB-2=2 (I-side outstanding bound
NUM_FB*IC_LINE_BEATS=8, reachable only via a branch lookup with 3 lines in flight; linear prefetch
holds at most FB_THRESHOLD+1=3 non-stale buffers = 6 beats, F-FE-017); D-side outstanding bound 2
(MEM-04). Bin values written as numbers below are the resolved values of those parameters, never
literals in the generated SV. Informational bins (TP-IMEM-040) are excluded from the closure
measure.

Conventions: "agent record" = the per-transaction record kept by gen_imem_agent / gen_dmem_agent /
gen_icache_ram_model / gen_scr_key_agent (issue cycle, grant cycle, rvalid cycle, injected error
class, outstanding depth before/after). knob:* values are the regime knobs of the brief; the
cross-cutting subagent owns their own bins, they appear here only inside crosses.

---------------------------------------------------------------------------------------------------

## IMEM covergroups

### CG-IMEM-001: gen_cg_imem_handshake
- Features: F-IMEM-001, F-IMEM-002, F-IMEM-003, F-IMEM-004, F-IMEM-005, F-IMEM-010, F-IMEM-029
- Sample: instr_req_o & instr_gnt_i (grant cycle); condition: gen_imem_agent record of the granted
  request is closed; anti-vacuity: grants only exist while the DUT fetches; a hit proves a request
  was held for exactly the binned number of cycles under the recorded knob, and the stability
  checks of gen_sva_ibus ran over that wait.
- Coverpoints:
  - cp_gnt_delay = cycles from instr_req_o rise (agent record) to this grant: bins d0{0}, d1{1},
    d2_3{[2:3]}, d4_15{[4:15]}, d16p{[16:$]}
  - cp_b2b = instr_gnt_i also high in the previous cycle with instr_req_o high in both: bins
    yes{1}, no{0}
  - cp_beat = instr_addr_o[2] of the granted word: bins w0{0}, w1{1}
  - cp_addr_lsb = instr_addr_o[1:0]: bins aligned{0}; ignore_bins other{[1:3]}: the icache drives
    [1:0]=00 by construction (F-IMEM-002); an occurrence is a gen_sva_ibus failure, not coverage
  - cp_knob = knob:imem_gnt_delay in force: bins same_cycle, short, long, random
  - cp_gnt_comb = agent mode computing instr_gnt_i combinationally from instr_req_o: bins
    comb{1}, registered{0}
- Crosses:
  - cr_delay_x_knob = cp_gnt_delay x cp_knob: bins d0_same{d0,same_cycle}, d16p_long{d16p,long},
    d4_15_random{d4_15,random}, d1_short{d1,short}; ignore d16p x same_cycle: the knob forbids it
  - cr_b2b_x_beat = cp_b2b x cp_beat: bins b2b_w0{yes,w0}, b2b_w1{yes,w1}
- Adopted (riscv-dv): none
- TP items: TP-IMEM-001, TP-IMEM-002, TP-IMEM-003, TP-IMEM-004, TP-IMEM-005, TP-IMEM-007,
  TP-IMEM-036

### CG-IMEM-002: gen_cg_imem_response
- Features: F-IMEM-006, F-IMEM-007, F-IMEM-008, F-IMEM-009
- Sample: instr_rvalid_i; condition: agent record matches this response to its granted request
  (in-order queue head); anti-vacuity: responses exist only for granted requests, so every hit is
  one full req/gnt/rvalid triple whose ordering gen_chk_ibus_proto verified.
- Coverpoints:
  - cp_rvalid_delay = cycles from grant to rvalid (agent record): bins d1{1}, d2_3{[2:3]},
    d4_15{[4:15]}, d16p{[16:$]}; ignore_bins d0{0}: forbidden by the agent (rule 3, inventory s2)
  - cp_outstanding_before = granted-and-unanswered count before this rvalid: bins
    o1{1}, o2{2}, o3{3}, o4{4}, o5{5}, o6{6}, o7{7}, o8{8} (upper bound NUM_FB*IC_LINE_BEATS);
    ignore_bins o0{0}: an rvalid with nothing outstanding is a protocol violation, not coverage
  - cp_max_outstanding = running maximum of the outstanding count since the last redirect, sampled
    when it falls back to 0: bins m1{1}, m2{2}, m3_4{[3:4]}, m5_7{[5:7]}, m8{8}; o7/o8 and m8 are
    reachable only through the branch-lookup path (3 stale lines + 2 target beats, F-IMEM-008,
    TP-IMEM-008); stale beats granted before the redirect stay in this count
  - cp_burst = consecutive rvalid cycles ending here: bins b1{1}, b2{2}, b3_4{[3:4]}, b5p{[5:$]}
  - cp_err_class = injected error class (agent record): bins none, bus_err, intg_single,
    intg_double
  - cp_cap = knob:imem_outstanding_cap: bins c1{1}, c2{2}, c4{4}, c8{8}
  - cp_rvalid_with_req = instr_req_o high in the same cycle: bins yes{1}, no{0}
- Crosses:
  - cr_outstanding_x_cap = cp_outstanding_before x cp_cap: bins full_c1{o1,c1}, full_c2{o2,c2},
    full_c4{o4,c4}, full_c8{o8,c8}; ignore depth > cap: the agent withholds grants at the cap
  - cr_err_x_outstanding = cp_err_class x cp_outstanding_before: bins err_deep{bus_err,o5..o8},
    intg_deep{intg_single or intg_double, o3..o8}
  - cr_delay_x_burst = cp_rvalid_delay x cp_burst: bins slow_then_burst{d16p,b3_4 or b5p}
- Adopted (riscv-dv): none
- TP items: TP-IMEM-006, TP-IMEM-007, TP-IMEM-008, TP-IMEM-009, TP-IMEM-010, TP-IMEM-037

### CG-IMEM-003: gen_cg_imem_fetch_err
- Features: F-IMEM-011, F-IMEM-012, F-IMEM-013, F-IMEM-014, F-IMEM-015, F-IMEM-027, F-IMEM-028
- Sample: closure of an injected-error record (agent) correlated with RVFI: either rvfi_valid &
  rvfi_trap for the instruction whose fetch word carried the error, or the discard of that word
  (redirect / stale / hit) without a trap; condition: the agent injected an error on that beat;
  anti-vacuity: only injected beats sample, so every hit proves an error was delivered and the
  DUT's reaction (trap or silence) was checked by gen_isa_compare / gen_chk_bus_intg_rsp.
- Coverpoints:
  - cp_outcome = what happened to the errored word: bins executed_trap, spec_discarded_no_trap,
    stale_after_redirect_no_trap, hit_spec_ignored_no_trap
  - cp_half = position of the errored beat in the consumed instruction: bins aligned_u32, c16,
    first_half, second_half, both_halves
  - cp_mtval = mtval read in the handler vs pc: bins eq_pc, eq_pc_plus2
  - cp_class = error class: bins bus_err, intg_single, intg_double
  - cp_source = fault source per RVFI/PMP model: bins bus, intg, pmp, pmp_plus2, bus_and_pmp
  - cp_alert_major_bus = alert_major_bus_o pulsed in the rvalid cycle: bins pulsed{1}, quiet{0}
  - cp_nmi_after_ifetch_intg = rvfi_ext_nmi_int within 2 retirements after an I-side intg error:
    bins none{0}; ignore_bins taken{1}: the I side raises no NMI (MEM-28); a hit is a checker fail
  - cp_line_not_cached = later fetch of the errored line reached the bus again: bins refetch{1}
- Crosses:
  - cr_half_x_class = cp_half x cp_class: bins first_intg{first_half,intg_single or intg_double},
    second_bus{second_half,bus_err}, both_bus{both_halves,bus_err}, c16_intg{c16,intg_double}
  - cr_outcome_x_class = cp_outcome x cp_class: bins spec_intg{spec_discarded_no_trap,intg_single
    or intg_double}, stale_bus{stale_after_redirect_no_trap,bus_err}
  - cr_half_x_mtval = cp_half x cp_mtval: bins second_plus2{second_half,eq_pc_plus2},
    first_pc{first_half,eq_pc}, both_pc{both_halves,eq_pc}; ignore second_half x eq_pc and
    first_half x eq_pc_plus2: contradict F-IMEM-013/014
- Adopted (riscv-dv): none
- TP items: TP-FE-020, TP-IMEM-011, TP-IMEM-012, TP-IMEM-013, TP-IMEM-014, TP-IMEM-015,
  TP-IMEM-016, TP-IMEM-019, TP-IMEM-030, TP-IMEM-031, TP-IMEM-034

### CG-IMEM-004: gen_cg_imem_redirect_seq
- Features: F-IMEM-016, F-IMEM-017, F-IMEM-018, F-IMEM-019, F-IMEM-020, F-IMEM-030
- Sample: (a) every redirect seen on RVFI (rvfi_pc_wdata != rvfi_pc_rdata + insn length, or a
  trap) and (b) every grant, classified by the agent's address-sequence tracker; condition: the
  imem agent has at least one open record for (a); anti-vacuity: (a) samples only while bus
  traffic is in flight across a redirect, so a hit proves stale beats were completed and
  discarded; (b) sample kinds other than next_line require a fill to have been entered mid-line.
- Coverpoints:
  - cp_kind = redirect kind: bins branch, jal, jalr, exc, irq, mret, dret, fencei, dbg_entry
  - cp_outstanding_at_redirect = granted-and-unanswered beats at the redirect: bins o0{0}, o1{1},
    o2{2}, o3_4{[3:4]}, o5_8{[5:8]}
  - cp_ungranted_req_at_redirect = instr_req_o high and not yet granted in the redirect cycle: bins
    yes{1}, no{0}
  - cp_req_stable_across_redirect = the ungranted request's address unchanged until grant: bins
    held{1}; ignore_bins changed{0}: gen_sva_ibus failure
  - cp_seq_kind = address-sequence class of this grant: bins next_beat_same_line, wrap_to_w0,
    next_line, redirect_target, end_of_line_stop
  - cp_cache_en = cpuctrlsts.icache_enable at the grant (tracked from RVFI csr writes and debug
    mode): bins on{1}, off{0}
  - cp_spec_hit_discard = speculative branch request whose lookup hit; response consumed and data
    discarded (RVFI insn came from cache, not from the bus word): bins yes{1}
  - cp_stream_match = rvfi_insn equals the agent memory image at rvfi_pc_rdata at fetch time: bins
    match{1}; ignore_bins mismatch{0}: gen_isa_compare failure
- Crosses:
  - cr_kind_x_outstanding = cp_kind x cp_outstanding_at_redirect: bins branch_deep{branch,o5_8},
    exc_o2{exc,o2}, irq_o1{irq,o1}, fencei_o3_4{fencei,o3_4}
  - cr_seq_x_en = cp_seq_kind x cp_cache_en: bins wrap_on{wrap_to_w0,on}, stop_off{end_of_line_stop,
    off}, target_on{redirect_target,on}, target_off{redirect_target,off}; ignore wrap_to_w0 x off
    and end_of_line_stop x on: F-IMEM-019/020 make them impossible
- Adopted (riscv-dv): none
- TP items: TP-IMEM-003, TP-IMEM-009, TP-IMEM-017, TP-IMEM-018, TP-IMEM-019, TP-IMEM-020,
  TP-IMEM-021, TP-IMEM-029, TP-IMEM-035, TP-IMEM-038

### CG-IMEM-005: gen_cg_imem_gating
- Features: F-IMEM-021, F-IMEM-022, F-IMEM-023, F-IMEM-024, F-IMEM-025, F-IMEM-026
- Sample: on each transition of the fetch-gate state (fetch_enable_i changes, core_busy_o falls
  for WFI, reset release) plus the first instr_req_o after reset; condition: the transition
  happened; anti-vacuity: gate transitions are driven by the test (fetch_enable regime, WFI in
  the program), so a hit proves the gate was exercised with the binned amount of traffic in flight.
- Coverpoints:
  - cp_gate_cause = why new requests stopped: bins wfi_sleep, fetch_en_off, fetch_en_invalid,
    reset_state
  - cp_fetch_en_code = fetch_enable_i value: bins on{IbexMuBiOn}, off{IbexMuBiOff},
    invalid[]{all 14 other 4-bit codes, one bin each}
  - cp_outstanding_at_gate = beats in flight when the gate closed: bins o0{0}, o1_4{[1:4]},
    o5_8{[5:8]}
  - cp_new_req_while_gated = instr_req_o rose for a NEW lookup while gated: bins none{0};
    ignore_bins seen{1}: gen_chk_fetch_en / gen_chk_sleep failure
  - cp_inflight_completed = all outstanding beats answered and consumed while gated: bins yes{1}
  - cp_resume = first retirement after the gate reopened: bins held_pc_no_refetch, handler_pc
  - cp_alert_on_invalid = alert_major_internal_o pulsed on an invalid fetch_enable_i code: bins
    quiet{0}; ignore_bins pulsed{1}: RTL raises none (Q-DL-8 default: check RTL as-is)
  - cp_first_req_cycle = cycles from reset release to the first instr_req_o: bins c1{1}, c2p{[2:$]}
  - cp_first_addr = first instr_addr_o == {boot_addr_i[31:8],8'h80}: bins eq{1}; ignore_bins
    ne{0}: gen_isa_compare / gen_chk_ibus_proto failure
  - cp_boot_class = boot_addr_i class: bins zero, low_ram, top_ffffff00, random_aligned
- Crosses:
  - cr_cause_x_outstanding = cp_gate_cause x cp_outstanding_at_gate: bins wfi_o1_4{wfi_sleep,o1_4},
    fen_off_o5_8{fetch_en_off,o5_8}, fen_inv_o1_4{fetch_en_invalid,o1_4}
- Adopted (riscv-dv): none
- TP items: TP-FE-028, TP-IMEM-022, TP-IMEM-023, TP-IMEM-024, TP-IMEM-025, TP-IMEM-026,
  TP-IMEM-027, TP-IMEM-028

### CG-IMEM-006: gen_cg_imem_stream_ctx
- Features: F-IMEM-008, F-IMEM-030, F-IMEM-029, F-IMEM-028
- Sample: rvfi_valid; condition: the instruction was fetched over the bus (agent record exists for
  its word(s), not a cache hit); anti-vacuity: cache hits do not sample, so a hit shows the bus
  delivery context of an executed instruction under the recorded regime.
- Coverpoints:
  - cp_delivery = context of the executed word: bins in_order_seq, hit_in_shadow_of_miss,
    after_redirect_target, straddle_two_records
  - cp_regime = knob:imem_rvalid_delay x knob:imem_gnt_delay class: bins fast_fast, slow_gnt,
    slow_rvalid, both_slow, random
  - cp_pmp_denied_word_on_bus = the fetched word was PMP-denied for the executing privilege (PMP
    model) yet the agent saw the request: bins seen{1}
  - cp_req_dep_on_gnt = instr_req_o changed in the same cycle as instr_gnt_i/instr_rvalid_i with a
    combinational agent: bins never{0}; ignore_bins seen{1}: contradicts F-IMEM-029 (structural)
- Crosses:
  - cr_delivery_x_regime = cp_delivery x cp_regime: bins shadow_both_slow{hit_in_shadow_of_miss,
    both_slow}, straddle_slow_rvalid{straddle_two_records,slow_rvalid}
- Adopted (riscv-dv): none
- TP items: TP-IMEM-004, TP-IMEM-029, TP-IMEM-030, TP-IMEM-032, TP-IMEM-033, TP-IMEM-036

### CG-IMEM-007: gen_cg_imem_driver_rules
- Features: F-IMEM-031, F-IMEM-032
- Sample: instr_gnt_i | instr_rvalid_i (any cycle with a grant or a response); condition: none
  beyond the event; anti-vacuity: grants and responses are agent actions, so every sample is one
  driver decision that gen_sva_ibus checked in the same cycle; the informational coverpoint samples
  only while the TP-IMEM-040 informational knob is set and is excluded from the closure measure.
- Coverpoints:
  - cp_gnt_with_req = instr_req_o in a cycle with instr_gnt_i: bins with_req{1}; ignore_bins
    bare_gnt{0}: driver rule (inventory s2 rule 2 / s11); a hit is a gen_sva_ibus TB error
  - cp_gnt_regime = knob:imem_gnt_delay at the grant: bins same_cycle, short, long, random
  - cp_rvalid_matched = a non-injected rvalid matched an outstanding granted beat (agent queue
    head): bins yes{1}; ignore_bins no{0}: gen_chk_ibus_proto failure
  - cp_unsolicited_rvalid_case (informational, TP-IMEM-040 only) = agent-injected extra rvalid
    classified by the icache state: bins no_expecting_buffer_ignored,
    expecting_buffer_consumed_shift, bad_secded_alert
- Crosses:
  - cr_gnt_x_regime = cp_gnt_with_req x cp_gnt_regime: bins req_same{with_req,same_cycle},
    req_long{with_req,long}
- Adopted (riscv-dv): none
- TP items: TP-IMEM-039, TP-IMEM-040

---------------------------------------------------------------------------------------------------

## DMEM covergroups

### CG-DMEM-001: gen_cg_dmem_handshake
- Features: F-DMEM-001, F-DMEM-002, F-DMEM-003, F-DMEM-004, F-DMEM-005, F-DMEM-006, F-DMEM-007,
  F-DMEM-008, F-DMEM-009, F-DMEM-010, F-DMEM-034, F-DMEM-035
- Sample: data_rvalid_i (one sample per completed transaction, the agent record carries the grant
  and issue cycles); condition: agent record matched in order; anti-vacuity: samples exist only
  for granted data transactions, each of which passed gen_chk_dbus_proto's hold/stability/order
  checks; a hit proves the binned latency pair and depth occurred.
- Coverpoints:
  - cp_gnt_delay = cycles from data_req_o rise to data_gnt_i: bins d0{0}, d1{1}, d2_3{[2:3]},
    d4_15{[4:15]}, d16p{[16:$]}
  - cp_rvalid_delay = cycles from grant to rvalid: bins d1{1}, d2_3{[2:3]}, d4_15{[4:15]},
    d16p{[16:$]}; ignore_bins d0{0}: forbidden by agent rule 2 (inventory s3)
  - cp_beat = transaction role: bins single, first, second
  - cp_we = data_we_o: bins load{0}, store{1}
  - cp_outstanding_before = granted-and-unanswered count before this rvalid: bins o1{1}, o2{2};
    ignore_bins o0{0}: unsolicited response is a protocol violation (Q-DL-9 default)
  - cp_req_with_prev_rvalid = data_req_o of the next instruction rose in this rvalid cycle: bins
    yes{1}, no{0}
  - cp_addr_lsb = data_addr_o[1:0] at grant: bins aligned{0}; ignore_bins other{[1:3]}:
    gen_sva_dbus failure
  - cp_payload_changed_after_gnt = any of addr/we/be/wdata changed the cycle after grant: bins
    changed{1}, same{0}
  - cp_gnt_knob = knob:dmem_gnt_delay: bins same_cycle, short, long, random
  - cp_rvalid_knob = knob:dmem_rvalid_delay: bins min1, short, long, random
- Crosses:
  - cr_delay_x_beat = cp_gnt_delay x cp_beat: bins d0_first{d0,first}, d16p_second{d16p,second},
    d4_15_single{d4_15,single}, d1_second{d1,second}
  - cr_b2b_x_we = cp_req_with_prev_rvalid x cp_we: bins b2b_load{yes,load}, b2b_store{yes,store}
  - cr_depth_x_beat = cp_outstanding_before x cp_beat: bins two_first{o2,first}; ignore o2 x single:
    aligned accesses never have two outstanding (F-DMEM-008)
  - cr_gnt_x_rvalid_knob = cp_gnt_knob x cp_rvalid_knob: bins both_long{long,long},
    same_min1{same_cycle,min1}, random_random{random,random}
- Adopted (riscv-dv): none
- TP items: TP-DMEM-001, TP-DMEM-002, TP-DMEM-003, TP-DMEM-004, TP-DMEM-005, TP-DMEM-006,
  TP-DMEM-007, TP-DMEM-008, TP-DMEM-009, TP-DMEM-020, TP-DMEM-023, TP-DMEM-035, TP-DMEM-037,
  TP-DMEM-038, TP-DMEM-056, TP-DMEM-057

### CG-DMEM-002: gen_cg_dmem_be_lanes
- Features: F-DMEM-011, F-DMEM-012, F-DMEM-013, F-DMEM-014, F-DMEM-020, F-DMEM-035, F-DMEM-041,
  F-DMEM-050
- Sample: data_req_o & data_gnt_i; condition: agent record open; anti-vacuity: one sample per
  address phase; a hit proves the binned (size, offset, beat) produced the binned be pattern and
  the lane/integrity checks of gen_chk_dbus_proto / gen_chk_store_intg ran on it.
- Coverpoints:
  - cp_size = access size from rvfi_insn of the owning instruction: bins byte, half, word
  - cp_offset = effective address [1:0] (rvfi_mem_addr): bins o0{0}, o1{1}, o2{2}, o3{3}
  - cp_beat: bins single, first, second
  - cp_be = data_be_o: bins be_0001, be_0010, be_0100, be_1000, be_0011, be_0110, be_1100,
    be_1110, be_0111, be_1111; ignore_bins unreachable{0000,0101,1001,1010,1011,1101}: no
    (size, offset, beat) produces them (LSU tables MEM-08)
  - cp_we: bins load{0}, store{1}
  - cp_lane_check = store lanes equal rs2 rotated by 8*offset on the enabled lanes: bins ok{1};
    ignore_bins bad{0}: gen_chk_dbus_proto failure
  - cp_disabled_lane_nonzero = a disabled lane carries non-zero rotated data: bins seen{1}, zero{0}
  - cp_wdata_intg = data_wdata_o[38:32] decodes with zero syndrome: bins ok{1}; ignore_bins
    bad{0}: gen_chk_store_intg failure
  - cp_wdata_intg_on_load = integrity valid on a load's data_wdata_o: bins ok{1}
  - cp_masked_recompute_differs = check bits recomputed over the be-masked (zeroed) word differ
    from data_wdata_o[38:32]: bins yes{1}, no{0} (a yes proves the checker verifies the whole word,
    F-DMEM-050; no occurs when the disabled lanes happen to be zero)
- Crosses:
  - cr_wdata_intg_x_we = cp_wdata_intg x cp_we: bins load_ok{ok,load}, store_ok{ok,store}
  - cr_intg_x_disabled_lane = cp_wdata_intg x cp_disabled_lane_nonzero: bins ok_nonzero{ok,seen}
  - cr_size_offset_beat_we = cp_size x cp_offset x cp_beat x cp_we: bins all legal 32 combos named
    <size>_<offset>_<beat>_<we>, e.g. word_o1_first_store, half_o3_second_load, byte_o2_single_store;
    ignore byte x first/second, half x o0/o1/o2 x first/second, word x o0 x first/second, and
    single x (word x o1/o2/o3, half x o3): the split predicate (MEM-07) forbids them
  - cr_be_x_beat = cp_be x cp_beat: bins second_0001{be_0001,second}, second_0011{be_0011,second},
    second_0111{be_0111,second}, first_1000{be_1000,first}; ignore be_1111 x first/second,
    be_0010/0100/0110 x first/second: unreachable per tables
- Adopted (riscv-dv): none
- TP items: TP-DMEM-003, TP-DMEM-011, TP-DMEM-012, TP-DMEM-013, TP-DMEM-014, TP-DMEM-015,
  TP-DMEM-016, TP-DMEM-045, TP-DMEM-060

### CG-DMEM-003: gen_cg_dmem_misaligned
- Features: F-DMEM-015, F-DMEM-016, F-DMEM-017, F-DMEM-018, F-DMEM-024, F-DMEM-025, F-DMEM-026
- Sample: final rvalid of a split access (agent pairs the two records by the second address =
  first + 4); condition: the pair closed; anti-vacuity: only split accesses sample; a hit proves
  the binned FSM path and per-beat latencies really occurred and gen_isa_compare checked the
  assembled data.
- Coverpoints:
  - cp_type = split kind: bins lw_o1, lw_o2, lw_o3, lh_o3, lhu_o3, sw_o1, sw_o2, sw_o3, sh_o3
  - cp_path = second-grant timing relative to first rvalid: bins gnt2_after_rvalid1,
    gnt2_before_rvalid1, gnt2_same_cycle_rvalid1
  - cp_beat1_rvalid_delay: bins d1{1}, d2_3{[2:3]}, d4p{[4:$]}
  - cp_beat2_gnt_delay: bins d0{0}, d1{1}, d2_3{[2:3]}, d4p{[4:$]}
  - cp_beat2_rvalid_delay: bins d1{1}, d2_3{[2:3]}, d4p{[4:$]}
  - cp_second_addr = data_addr_o(second) == data_addr_o(first) + 4: bins ok{1}; ignore_bins
    bad{0}: gen_chk_dbus_proto failure
  - cp_wrap = first word at 0xFFFF_FFFC and second at 0x0000_0000: bins wrapped{1}, no{0}
  - cp_req_low_between = data_req_o low while both beats in flight (GNTS_DONE): bins yes{1}
- Crosses:
  - cr_type_x_path = cp_type x cp_path: bins lw_o3_gnts_done{lw_o3,gnt2_before_rvalid1},
    sw_o1_wait_gnt{sw_o1,gnt2_after_rvalid1}, lh_o3_same{lh_o3,gnt2_same_cycle_rvalid1},
    sh_o3_gnts_done{sh_o3,gnt2_before_rvalid1}
  - cr_delays = cp_beat1_rvalid_delay x cp_beat2_gnt_delay x cp_beat2_rvalid_delay: bins
    all_slow{d4p,d4p,d4p}, fast_slow_fast{d1,d4p,d1}, slow_fast_slow{d4p,d0,d4p}
  - cr_wrap_x_type = cp_wrap x cp_type: bins wrap_lw_o1{wrapped,lw_o1}, wrap_lw_o3{wrapped,lw_o3},
    wrap_sh_o3{wrapped,sh_o3}, wrap_sw_o2{wrapped,sw_o2}
- Adopted (riscv-dv): none
- TP items: TP-DMEM-004, TP-DMEM-005, TP-DMEM-009, TP-DMEM-010, TP-DMEM-015, TP-DMEM-016,
  TP-DMEM-017, TP-DMEM-018, TP-DMEM-019, TP-DMEM-020, TP-DMEM-021, TP-DMEM-022, TP-DMEM-023

### CG-DMEM-004: gen_cg_dmem_split_err
- Features: F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-027
- Sample: final rvalid of a split access with at least one injected error (agent record);
  condition: injected; anti-vacuity: only error-injected splits sample; a hit proves the trap,
  mtval and the second-beat behaviour were checked by gen_isa_compare / gen_chk_dbus_proto.
- Coverpoints:
  - cp_err_beat: bins first, second, both
  - cp_we: bins load{0}, store{1}
  - cp_mtval = handler-read mtval class: bins unaligned_ea, second_word_aligned
  - cp_second_issued = second request appeared on the bus after a first-beat error: bins yes{1};
    ignore_bins no{0}: gen_chk_dbus_proto failure (doc rule, MEM-10)
  - cp_second_gnt_delay_after_err: bins d0{0}, d1_3{[1:3]}, d4p{[4:$]}
  - cp_handler_ls_waited = first handler instruction is a load/store and its data_req_o waited for
    the abandoned second rvalid: bins yes{1}, not_ls{0}
  - cp_memory_side_effect = store second-half write landed in agent memory although the
    instruction trapped: bins landed{1}, none{0}
- Crosses:
  - cr_beat_x_we = cp_err_beat x cp_we: bins first_load{first,load}, first_store{first,store},
    second_load{second,load}, second_store{second,store}, both_load{both,load}, both_store{both,store}
  - cr_beat_x_mtval = cp_err_beat x cp_mtval: bins first_ea{first,unaligned_ea},
    second_aligned{second,second_word_aligned}, both_ea{both,unaligned_ea}; ignore first x
    second_word_aligned, second x unaligned_ea, both x second_word_aligned: contradict MEM-10
- Adopted (riscv-dv): none
- TP items: TP-DMEM-024, TP-DMEM-025, TP-DMEM-026, TP-DMEM-027, TP-DMEM-038, TP-DMEM-055

### CG-DMEM-005: gen_cg_dmem_load_data
- Features: F-DMEM-018, F-DMEM-019, F-DMEM-040, F-DMEM-039
- Sample: rvfi_valid of a load or store; condition: no trap; anti-vacuity: one sample per retired
  load/store; a hit proves the binned (insn, offset, sign) load result was compared by
  gen_isa_compare against the agent memory.
- Coverpoints:
  - cp_insn: bins lb, lbu, lh, lhu, lw, sb, sh, sw
  - cp_offset: bins o0{0}, o1{1}, o2{2}, o3{3}
  - cp_sign_bit = MSB of the loaded datum before extension: bins s0{0}, s1{1}
  - cp_rd = destination register: bins x0{0}, other{[1:31]}
  - cp_store_rdata_random = agent returned random data_rdata_i on a store response: bins yes{1}
- Crosses:
  - cr_insn_offset_sign = cp_insn x cp_offset x cp_sign_bit: bins all 40 load combos named
    <insn>_<offset>_<sign>, e.g. lb_o3_s1, lh_o3_s0, lhu_o1_s1, lw_o2_s1; ignore sb/sh/sw x *:
    stores have no sign bit
  - cr_x0_x_insn = cp_rd x cp_insn: bins x0_lw{x0,lw}, x0_lb{x0,lb}, x0_lhu{x0,lhu}; ignore x0 x
    sb/sh/sw: stores have no rd
- Adopted (riscv-dv): none
- TP items: TP-DMEM-028, TP-DMEM-029, TP-DMEM-030, TP-DMEM-031

### CG-DMEM-006: gen_cg_dmem_bus_err
- Features: F-DMEM-036, F-DMEM-037, F-DMEM-038, F-DMEM-030, F-DMEM-040, F-DMEM-032
- Sample: rvfi_valid & rvfi_trap with mcause 5 or 7 not attributed to PMP (PMP model says
  allowed); condition: agent injected data_err_i on that access; anti-vacuity: only injected
  errors sample, so a hit proves a real bus error produced the trap the checkers verified.
- Coverpoints:
  - cp_cause: bins load_5, store_7
  - cp_size: bins byte, half, word
  - cp_id_insn = instruction in ID when the error response arrived (next RVFI candidate): bins
    none, alu, illegal, ecall, ebreak, fetch_err, load_store, branch, csr, wfi
  - cp_id_killed_reexecuted = the ID instruction did not retire before the trap and retired after
    the handler returned: bins yes{1}
  - cp_rd_x0: bins x0{1}, other{0}
  - cp_irq_pending_at_err = an enabled interrupt line was high in the error cycle: bins yes{1}, no{0}
  - cp_dbg_req_at_err = debug_req_i high in the error cycle: bins yes{1}, no{0}
  - cp_next_req_suppressed = a back-to-back data_req_o that would have issued in the error cycle
    did not appear: bins yes{1}
  - cp_rf_unchanged = rvfi_rd_wdata not written for the errored load: bins ok{1}; ignore_bins
    written{0}: gen_isa_compare failure
  - cp_trap_order = trap retired before the pending IRQ/debug entry: bins exc_first{1}
- Crosses:
  - cr_cause_x_id = cp_cause x cp_id_insn: bins load_illegal{load_5,illegal}, load_ecall{load_5,
    ecall}, store_fetch_err{store_7,fetch_err}, load_ls{load_5,load_store}, store_ebreak{store_7,
    ebreak}, load_wfi{load_5,wfi}
  - cr_cause_x_irq = cp_cause x cp_irq_pending_at_err: bins load_irq{load_5,yes}, store_irq{store_7,
    yes}
  - cr_cause_x_dbg = cp_cause x cp_dbg_req_at_err: bins load_dbg{load_5,yes}, store_dbg{store_7,yes}
- Adopted (riscv-dv): none
- TP items: TP-DMEM-030, TP-DMEM-032, TP-DMEM-033, TP-DMEM-034, TP-DMEM-035, TP-DMEM-036,
  TP-DMEM-037, TP-DMEM-038, TP-DMEM-054

### CG-DMEM-007: gen_cg_dmem_intg
- Features: F-DMEM-041, F-DMEM-039
- Sample: data_rvalid_i with an injected integrity corruption (agent record); condition:
  injected; anti-vacuity: only corrupted responses sample; a hit proves gen_chk_bus_intg_rsp saw
  the alert, RF suppression and NMI it checks.
- Coverpoints:
  - cp_class: bins single, double
  - cp_we: bins load{0}, store{1}
  - cp_beat: bins single, first, second
  - cp_with_bus_err = data_err_i also set on that beat: bins yes{1}, no{0}
  - cp_alert = alert_major_bus_o pulsed in the rvalid cycle: bins pulsed{1}; ignore_bins
    quiet{0}: gen_chk_bus_intg_rsp failure
  - cp_rf_suppressed = load rd not written (rvfi_rd_wdata absent) and instruction retired without
    trap: bins yes{1}
  - cp_nmi_latency = retirements between the corrupted access and the NMI entry: bins l0{0}, l1{1};
    ignore_bins l2p{[2:$]}: exceeds the documented window (exception_interrupts.rst)
  - cp_nmi_mtval = handler-read mtval vs access address: bins first_ea, second_word, aligned_ea
  - cp_second_intg_while_pending = a second corruption before the NMI was taken: bins ignored{1}
  - cp_nmi_in_debug_deferred = corruption while in debug mode; NMI taken after dret: bins yes{1}
- Crosses:
  - cr_class_x_we_x_beat = cp_class x cp_we x cp_beat: bins single_load_first{single,load,first},
    double_store_single{double,store,single}, double_load_second{double,load,second},
    single_store_second{single,store,second}
  - cr_buserr_x_class = cp_with_bus_err x cp_class: bins both_single{yes,single}, both_double{yes,
    double}
- Adopted (riscv-dv): none
- TP items: TP-DMEM-039, TP-DMEM-040, TP-DMEM-041, TP-DMEM-042, TP-DMEM-043

### CG-DMEM-008: gen_cg_dmem_pipe_ctx
- Features: F-DMEM-028, F-DMEM-029, F-DMEM-031, F-DMEM-033, F-DMEM-042, F-DMEM-043, F-DMEM-044,
  F-DMEM-045, F-DMEM-046, F-DMEM-047, F-DMEM-051
- Sample: rvfi_valid of a load/store (and, for cp_wfi_*, core_busy_o falling); condition: as per
  coverpoint; anti-vacuity: each coverpoint's precondition (a prior store to the same address, a
  dependent consumer, an outstanding access at WFI, a PMP denial, a Zcmp expansion) is derived from
  the program and the agent record, so a hit is not a free tick.
- Coverpoints:
  - cp_store_load_distance = retirements between a store and a later load overlapping its bytes:
    bins d1{1}, d2{2}, d3_8{[3:8]}, none{no prior store}
  - cp_overlap = byte overlap between that store and load: bins full, partial_byte, partial_half
  - cp_dep_stall = consumer of the load's rd retired the cycle after rvalid (stall_ld_hz): bins
    yes{1}, no_consumer{0}
  - cp_dep_x0 = consumer reads x0 written by a load to x0; no stall: bins yes{1}
  - cp_wfi_outstanding = WFI retired while a load/store response was outstanding; core_busy_o
    stayed On until rvalid: bins yes{1}
  - cp_pmp_denied = PMP-denied access class with no data_req_o on the bus: bins aligned_load,
    aligned_store, mis_first_load, mis_first_store, mis_second_load, mis_second_store,
    mis_both_load, mis_both_store
  - cp_pmp_second_half_issued = permitted second half on the bus after a denied first half: bins
    yes{1}
  - cp_zcmp_burst = data transactions produced by one cm.push/cm.pop*: bins n1{1}, n2{2},
    n3_6{[3:6]}, n7_13{[7:13]}
  - cp_zcmp_err_pos = errored transaction inside the burst: bins first, middle, last
  - cp_rvfi_mask = (rvfi_mem_rmask, rvfi_mem_wmask) class: bins r_word{4'b1111}, r_half{4'b0011},
    r_byte{4'b0001}, w_word, w_half, w_byte
  - cp_rvfi_mask_unshifted = mask unshifted while rvfi_mem_addr[1:0] != 0: bins yes{1}
  - cp_crash_last_data_addr = crash_dump_o.last_data_addr vs agent record: bins eq_last_gnt,
    frozen_on_err
  - cp_data_tag_zero = data_tag_o: bins zero{0}; ignore_bins one{1}: gen_chk_cheriot_quiet failure
  - cp_rvfi_load_latency = cycles from the final data_rvalid_i of a load to its rvfi_valid: bins
    one{1}; ignore_bins other{0,[2:$]}: contradicts the RVFI pipeline (rtl/ibex_core.sv:1868,
    1890: rvfi_wb_done registered once), F-DMEM-051
  - cp_store_no_rd = rvfi_rd_addr == 0 on a store retirement: bins yes{1}; ignore_bins no{0}:
    gen_isa_compare failure (stores never write, F-DMEM-051)
  - cp_wb_source = write source of a retirement with rvfi_rd_addr != 0, from rvfi_insn class: bins
    wb_flop, lsu_load; wb_flop = ALU/CSR/jump result written the cycle after ID, lsu_load = load
    data written at data return
  - cp_load_then_alu_b2b = a load retirement immediately followed (next cycle) by a non-load
    retirement with rvfi_rd_addr != 0: bins yes{1} (the two write sources on consecutive cycles)
- Crosses:
  - cr_distance_x_overlap = cp_store_load_distance x cp_overlap: bins d1_full{d1,full},
    d1_partial_byte{d1,partial_byte}, d2_partial_half{d2,partial_half}
  - cr_zcmp_err = cp_zcmp_burst x cp_zcmp_err_pos: bins long_first{n7_13,first},
    long_middle{n7_13,middle}, short_last{n2,last}; ignore n1 x middle/last: single-op bursts
- Adopted (riscv-dv): none
- TP items: TP-DMEM-044, TP-DMEM-046, TP-DMEM-047, TP-DMEM-048, TP-DMEM-049, TP-DMEM-050,
  TP-DMEM-051, TP-DMEM-052, TP-DMEM-053, TP-DMEM-054, TP-DMEM-055, TP-DMEM-061

### CG-DMEM-009: gen_cg_dmem_driver_rules
- Features: F-DMEM-048, F-DMEM-049
- Sample: data_gnt_i | data_rvalid_i | a PMP-denied access classified by the PMP model (no boundary
  data_req_o); condition: event; anti-vacuity: grants and responses are agent actions checked by
  gen_sva_dbus in the same cycle, and the PMP-denied sample needs a real denial from the program's
  PMP configuration.
- Coverpoints:
  - cp_gnt_with_req = data_req_o in a cycle with data_gnt_i: bins with_req{1}; ignore_bins
    bare_gnt{0}: driver rule 1 (inventory s3); a hit is a gen_sva_dbus TB error
  - cp_gnt_regime = knob:dmem_gnt_delay at the grant: bins same_cycle, short, long, random
  - cp_no_gnt_on_pmp_denied = a PMP-denied access (LSU requesting internally, boundary data_req_o
    suppressed) saw no data_gnt_i: bins yes{1}; ignore_bins gnt_seen{0}: agent granted a
    suppressed request (TB error, F-DMEM-048)
  - cp_rdata_known_on_rvalid = !$isunknown(data_rdata_i) at data_rvalid_i: bins known{1};
    ignore_bins x{0}: driver rule 8 (F-DMEM-049); a hit is a gen_sva_dbus TB error
  - cp_rdata_x_between_rvalid = the agent drove X or random data_rdata_i in a cycle without rvalid:
    bins yes{1}
  - cp_rdata_store_resp = payload class on a store response: bins fixed, random
- Crosses:
  - cr_gnt_x_regime = cp_gnt_with_req x cp_gnt_regime: bins req_same{with_req,same_cycle},
    req_long{with_req,long}
- Adopted (riscv-dv): none
- TP items: TP-DMEM-058, TP-DMEM-059

---------------------------------------------------------------------------------------------------

## FE covergroups

### CG-FE-001: gen_cg_fe_vectors
- Features: F-FE-002, F-FE-003, F-FE-004, F-FE-005, F-FE-011, F-FE-019, F-FE-001
- Sample: rvfi_valid where the next PC is not sequential (rvfi_pc_wdata != rvfi_pc_rdata + len)
  and the first retirement after reset; condition: redirect or first instruction; anti-vacuity:
  sequential instructions never sample; a hit proves a redirect of the binned kind reached RVFI
  and gen_isa_compare checked the target.
- Coverpoints:
  - cp_first_pc = first rvfi_pc_rdata == {boot_addr_i[31:8],8'h80}: bins eq{1}; ignore_bins
    ne{0}: gen_isa_compare failure
  - cp_mtvec_reset = first csrr mtvec read == {boot_addr_i[31:8],8'h01}: bins eq{1}
  - cp_boot_class = boot_addr_i: bins zero{0}, top{32'hFFFF_FF00}, random_aligned{other, [7:0]=0}
  - cp_pc_mux = redirect source: bins jump_jal, jump_jalr, branch_taken, exc_vector, irq_vector,
    eret_mepc, dret_depc, dbg_halt_addr, dbg_exc_addr, fencei_next, boot; ignore_bins bp{PC_BP}:
    BranchPredictor=0 (F-FE-019, structural exclusion)
  - cp_irq_vec_id = interrupt vector slot {mtvec[31:8],1'b0,id[4:0],2'b00} class: bins sw{3},
    timer{7}, ext{11}, fast[]{[16:30] one bin per fast line, width from ibex_pkg}, nmi{31}
  - cp_target_bit1 = target address bit 1: bins b0{0}, b1{1}
  - cp_jalr_rs1_bit0 = rs1 bit 0 of a jalr whose target had bit 0 set before dropping: bins
    odd{1}, even{0}
  - cp_misaligned_exc = rvfi_trap with mcause 0: bins never{0}; ignore_bins seen{1}: impossible
    with C (F-FE-011); a hit is a gen_isa_compare failure
- Crosses:
  - cr_mux_x_bit1 = cp_pc_mux x cp_target_bit1: bins jalr_b1{jump_jalr,b1}, branch_b1{branch_taken,
    b1}, eret_b1{eret_mepc,b1}, dret_b1{dret_depc,b1}; ignore exc_vector/irq_vector/dbg_* x b1:
    vectors are word aligned
  - cr_boot_x_first = cp_boot_class x cp_first_pc: bins top_ok{top,eq}, zero_ok{zero,eq}
- Adopted (riscv-dv): none
- TP items: TP-FE-001, TP-FE-002, TP-FE-003, TP-FE-004, TP-FE-005, TP-FE-010, TP-FE-011, TP-FE-023,
  TP-IMEM-027, TP-IMEM-028

### CG-FE-002: gen_cg_fe_align
- Features: F-FE-006, F-FE-007, F-FE-008, F-FE-009, F-FE-010
- Sample: rvfi_valid; condition: not a trap; anti-vacuity: the straddle/hit-miss classification
  comes from the imem agent's word records (which words carried this instruction and when they
  arrived), so a straddle bin cannot hit unless the instruction really spanned two words.
- Coverpoints:
  - cp_len = instruction length: bins c16, u32
  - cp_pc_bit1 = rvfi_pc_rdata[1]: bins b0{0}, b1{1}
  - cp_straddle = u32 at pc[1]=1: bins no, same_line, line_cross
  - cp_second_word_wait = cycles the first half waited for the second word's rvalid (agent record):
    bins ready{0}, w1{1}, w2_3{[2:3]}, w4p{[4:$]}
  - cp_delta = rvfi_pc_wdata - rvfi_pc_rdata: bins plus2{2}, plus4{4}, redirect{other}
  - cp_halves_src = source of the two halves (P2 tag-model view): bins hit_hit, hit_miss, miss_hit,
    miss_miss, bus_bus_disabled
  - cp_first_retire_after_branch_to_b1 = branch target with bit 1 set followed by a u32: bins yes{1}
- Crosses:
  - cr_straddle_x_wait = cp_straddle x cp_second_word_wait: bins cross_w4p{line_cross,w4p},
    same_w1{same_line,w1}, cross_ready{line_cross,ready}
  - cr_len_x_bit1 = cp_len x cp_pc_bit1: bins c16_b1{c16,b1}, u32_b1{u32,b1}, c16_b0{c16,b0},
    u32_b0{u32,b0}
  - cr_straddle_x_src = cp_straddle x cp_halves_src: bins cross_hit_miss{line_cross,hit_miss},
    cross_miss_hit{line_cross,miss_hit}, cross_miss_miss{line_cross,miss_miss}; ignore same_line x
    hit_miss/miss_hit: one line has one source
- Adopted (riscv-dv): none
- TP items: TP-FE-006, TP-FE-007, TP-FE-008, TP-FE-009, TP-FE-010, TP-IMEM-002, TP-IMEM-013,
  TP-IMEM-033

### CG-FE-003: gen_cg_fe_redirect
- Features: F-FE-013, F-FE-017, F-FE-025, F-FE-012
- Sample: each redirect on RVFI; condition: imem agent classified the traffic since the previous
  redirect; anti-vacuity: the discarded-word count is the number of granted words not consumed by
  any retirement, computed from agent records, so bins > 0 need real speculative traffic.
- Coverpoints:
  - cp_kind: bins branch_taken, jal, jalr, exc, irq, mret, dret, fencei, dbg_entry, dbg_exit
  - cp_discarded_words = granted words never executed since the previous redirect (address-matched
    against retirements, so a speculative word served from the cache counts as consumed): bins
    n0{0}, n1{1}, n2_3{[2:3]}, n4_6{[4:6]}; ignore_bins n7p{[7:$]}: linear prefetch holds at most 3
    non-stale fill buffers (6 beats) between two redirects (F-FE-017, FB_THRESHOLD = NUM_FB-2); the
    8-beat bound of F-IMEM-008 includes stale beats granted before the previous redirect and is
    covered by CG-IMEM-002.cp_outstanding_before
  - cp_spacing = cycles since the previous redirect: bins s1{1}, s2{2}, s3_4{[3:4]}, s5p{[5:$]}
  - cp_target_req_same_cycle = instr_req_o with the target word address in the redirect cycle: bins
    yes{1}, no_pending_req{0}
  - cp_stale_retired = an instruction from the discarded stream retired: bins never{0};
    ignore_bins seen{1}: gen_isa_compare failure
  - cp_branch_not_taken_no_redirect = not-taken branch with sequential next PC: bins yes{1}
  - cp_spec_err_discarded = an injected instr_err_i on a word discarded by this redirect (agent
    record): bins yes{1}, no{0}
- Crosses:
  - cr_kind_x_discarded = cp_kind x cp_discarded_words: bins branch_n4_6{branch_taken,n4_6},
    exc_n2_3{exc,n2_3}, irq_n1{irq,n1}, fencei_n4_6{fencei,n4_6}, jalr_n0{jalr,n0}
  - cr_spacing_x_kind = cp_spacing x cp_kind: bins storm_branch{s1,branch_taken},
    storm_jal{s1,jal}, s2_jalr{s2,jalr}
- Adopted (riscv-dv): none
- TP items: TP-FE-012, TP-FE-013, TP-FE-014, TP-FE-015, TP-FE-024, TP-IMEM-012, TP-IMEM-017,
  TP-IMEM-018

### CG-FE-004: gen_cg_fe_backpressure
- Features: F-FE-012, F-FE-018, F-FE-024
- Sample: end of each ID stall window (a gap of >= 2 cycles between rvfi_valid pulses while
  instr_rvalid_i traffic exists); condition: window closed; anti-vacuity: the cause is derived
  from RVFI (the instruction in ID and its hazards) and the agent count; a hit proves fetch
  back-pressure was observed with the binned cause.
- Coverpoints:
  - cp_cause: bins ld_hazard, ls_wait, mul_div, zcmp_expand, csr_flush, dummy_gap
  - cp_outstanding_stopped_growing = outstanding count did not rise during the window while
    the agent had free capacity: bins yes{1}
  - cp_words_buffered_at_stall = non-stale granted-not-consumed words at stall start: bins n0{0},
    n1_2{[1:2]}, n3_4{[3:4]}, n5_6{[5:6]}; ignore_bins n7p{[7:$]}: at most 3 non-stale fill buffers
    (F-FE-017); stale beats are excluded from this count
  - cp_stall_len = window length in cycles: bins l2_3{[2:3]}, l4_15{[4:15]}, l16p{[16:$]}
  - cp_dummy_seen = dummy instruction inserted (P1 probe dummy_instr_id_o): bins yes{1}
- Crosses:
  - cr_cause_x_buffered = cp_cause x cp_words_buffered_at_stall: bins mul_div_full{mul_div,n5_6},
    zcmp_full{zcmp_expand,n5_6}, ls_wait_n3_4{ls_wait,n3_4}
- Adopted (riscv-dv): none
- TP items: TP-FE-016, TP-FE-017, TP-FE-018

### CG-FE-005: gen_cg_fe_fault_path
- Features: F-FE-015, F-FE-016, F-FE-020, F-FE-022, F-FE-023
- Sample: rvfi_valid & rvfi_trap with mcause 1; condition: trap; anti-vacuity: only instruction
  access faults sample; the source class comes from the agent record or the PMP model, so every
  hit is an attributed fault whose consequences gen_isa_compare checked.
- Coverpoints:
  - cp_source: bins bus, intg, pmp, pmp_plus2, bus_and_pmp
  - cp_next_fetch = first instr_addr_o after the trap: bins exc_vector, dm_exception_addr
  - cp_in_debug: bins yes{1}, no{0}
  - cp_len = faulting instruction length: bins c16, u32
  - cp_side_effects = rd write or data_req_o attributable to the faulting instruction: bins none{0};
    ignore_bins seen{1}: gen_isa_compare failure
  - cp_c16_plus2_ignored = compressed instruction with pc+2 PMP-denied executed without trap: bins
    yes{1}
  - cp_pc_incr_alert = alert_major_internal_o pulsed during sequential execution: bins never{0};
    ignore_bins pulsed{1}: gen_chk_alerts failure (F-FE-020 is an always-low check)
  - cp_debug_fetch_on_bus = every debug-mode retirement had a bus record: bins yes{1}
- Crosses:
  - cr_source_x_debug = cp_source x cp_in_debug: bins bus_dbg{bus,yes}, pmp_dbg{pmp,yes},
    intg_nodbg{intg,no}
  - cr_source_x_len = cp_source x cp_len: bins pmp_plus2_u32{pmp_plus2,u32}, bus_c16{bus,c16};
    ignore pmp_plus2 x c16: the +2 check is skipped for compressed instructions
- Adopted (riscv-dv): none
- TP items: TP-FE-019, TP-FE-020, TP-FE-021, TP-FE-022, TP-FE-023, TP-FE-025, TP-IMEM-011,
  TP-IMEM-016, TP-IMEM-030

### CG-FE-006: gen_cg_fe_wake_wrap
- Features: F-FE-014, F-FE-021, F-FE-003
- Sample: (a) first rvfi_valid after core_busy_o rose from Off; (b) rvfi_valid with rvfi_pc_rdata
  >= 32'hFFFF_FFF8; condition: as stated; anti-vacuity: sleep and top-of-memory execution only
  happen when the program does them; a hit proves the wake source / wrap case occurred.
- Coverpoints:
  - cp_wake_src: bins irq, nmi, debug_req, step_mode
  - cp_resume_pc = first retirement after wake: bins wfi_next_buffered, handler
  - cp_refetch_after_wake = the word after WFI was fetched again from the bus: bins no{0}, yes{1}
  - cp_wrap_case: bins c16_at_fffe, u32_at_fffc, u32_at_fffe_straddle_zero
  - cp_next_after_wrap = rvfi_pc_wdata == 0 after the wrap instruction: bins zero{1}
  - cp_fetch_seq_wrap = instr_addr_o 0xFFFF_FFFC followed by 0x0000_0000: bins yes{1}
- Crosses:
  - cr_wake_x_resume = cp_wake_src x cp_resume_pc: bins irq_handler{irq,handler},
    dbg_handler{debug_req,handler}, step_next{step_mode,wfi_next_buffered}
- Adopted (riscv-dv): none
- TP items: TP-FE-003, TP-FE-026, TP-FE-027, TP-FE-028, TP-IMEM-022

---------------------------------------------------------------------------------------------------

## IC covergroups

### CG-IC-001: gen_cg_ic_ram_ports
- Features: F-IC-001, F-IC-002, F-IC-003, F-IC-004, F-IC-005, F-IC-006, F-IC-007, F-IC-028,
  F-IC-045, F-IC-046
- Sample: any cycle with |ic_tag_req_o or |ic_data_req_o (gen_icache_ram_model port monitor);
  condition: request; anti-vacuity: idle cycles never sample; write-side bins require the model
  to decode the codeword (after undoing the address-derived tweak), so an ecc_ok hit is a real
  check, not a tick.
- Coverpoints:
  - cp_tag_op = classified tag-port operation: bins lookup_both, inval_write_both, fill_write_way0,
    fill_write_way1, ecc_write_way0, ecc_write_way1, ecc_write_both
  - cp_data_op: bins lookup_both, fill_write_way0, fill_write_way1, inval_zero_write_both
  - cp_cache_en = icache_enable as tracked from RVFI csr writes and debug mode: bins on{1}, off{0}
  - cp_index = ic_tag_addr_o: bins idx0{0}, idx_mid{[1:IC_NUM_LINES-2]}, idx_last{IC_NUM_LINES-1}
  - cp_tag_wdata_ecc = tag write codeword (tweak undone) decodes clean: bins ok{1}; ignore_bins
    bad{0}: gen_chk_icache failure
  - cp_data_wdata_ecc = both 39-bit beats decode clean: bins ok{1}; ignore_bins bad{0}:
    gen_chk_icache failure
  - cp_tag_valid_bit = valid bit of the written tag: bins valid{1}, invalid{0}
  - cp_same_port_rw = read and write on one RAM port in one cycle: bins never{0}; ignore_bins
    seen{1}: single-port RAM violation (F-IC-045), gen_chk_icache failure
  - cp_read_when_disabled = lookup read while cp_cache_en == off: bins seen{1}
  - cp_rdata_used_next_cycle = model read returned 1 cycle later and the DUT acted on it (hit or
    ecc alert): bins yes{1}
- Crosses:
  - cr_tagop_x_en = cp_tag_op x cp_cache_en: bins lookup_off{lookup_both,off}, fill0_on{
    fill_write_way0,on}, fill1_on{fill_write_way1,on}, inval_on{inval_write_both,on},
    inval_off{inval_write_both,off}, ecc_both_on{ecc_write_both,on}
  - cr_index_x_tagop = cp_index x cp_tag_op: bins idx0_inval{idx0,inval_write_both},
    idxlast_inval{idx_last,inval_write_both}, idxlast_fill{idx_last,fill_write_way1}
- Adopted (riscv-dv): none
- TP items: TP-IC-001, TP-IC-002, TP-IC-003, TP-IC-004, TP-IC-005, TP-IC-006, TP-IC-011, TP-IC-030,
  TP-IC-035, TP-IC-036, TP-IC-045, TP-IC-046

### CG-IC-002: gen_cg_ic_inval_key
- Features: F-IC-008, F-IC-009, F-IC-010, F-IC-011, F-IC-022, F-IC-023, F-IC-024, F-IC-025,
  F-IC-026, F-IC-047
- Sample: (a) ic_scr_key_req_o pulse; (b) end of an invalidation sweep (tag write to index
  IC_NUM_LINES-1 with valid=0 after a sweep start) or its abandonment; (c) each fence.i on RVFI;
  condition: event; anti-vacuity: sweeps and key pulses are DUT reactions to reset/fence.i; a hit
  proves the FSM path the checker followed.
- Coverpoints:
  - cp_trigger = sweep trigger: bins reset, fencei_from_idle, fencei_restart
  - cp_sweep = sweep completion: bins complete_256, restarted_partial
  - cp_key_req_at_reset: bins issued, skipped_valid_high
  - cp_key_delay = cycles ic_scr_key_valid_i low after a pulse: bins k0_1{[0:1]}, k2_15{[2:15]},
    k16_255{[16:255]}, k256p{[256:$]}, never_in_test
  - cp_key_knob = knob:scr_key_delay: bins immediate, delayed, withheld_then_valid
  - cp_fencei_state = invalidation FSM state at the fence.i (derived from the key/sweep timeline):
    bins idle, await_key_ignored, inval_cache_restart
  - cp_second_pulse_for_await_fencei = a second ic_scr_key_req_o for a fence.i in AWAIT: bins
    none{0}; ignore_bins seen{1}: contradicts F-IC-024, gen_chk_icache failure
  - cp_consecutive_pulses = ic_scr_key_req_o high two cycles in a row: bins never{0}; ignore_bins
    seen{1}: gen_chk_icache failure
  - cp_fetch_during_sweep = retirements while the sweep ran, all with bus records: bins yes{1}
  - cp_tag_write_while_key_invalid = fill/inval tag write while ic_scr_key_valid_i is low AND the
    invalidation FSM is in AWAIT_SCRAMBLE_KEY (a request pending, derived from the key/sweep
    timeline): bins none{0}; ignore_bins seen{1}: gen_chk_icache failure. Fill writes during an
    unsolicited drop in INVAL_IDLE are legal (F-IC-047) and counted below, not here
  - cp_fill_write_after_unsolicited_drop = fill tag write while ic_scr_key_valid_i is low with no
    request pending (INVAL_IDLE): bins yes{1} (F-IC-047: the FSM reads the key only in OUT_OF_RESET
    and AWAIT_SCRAMBLE_KEY, rtl/ibex_icache.sv:1225, 1235)
  - cp_reset_to_idle_cycles = cycle index (reset release = 0) of the first cycle after the
    invalidation write of index IC_NUM_LINES-1, i.e. the first INVAL_IDLE cycle, for seeds with the
    key valid at reset: bins min{258}, longer{[259:$]}; ignore_bins short{[0:257]}: contradicts
    rtl/ibex_icache.sv:1221-1255 (MEM-23: 1 + 1 + IC_NUM_LINES cycles, F-IC-022)
  - cp_first_alloc_after_sweep = first fill write after the sweep end: bins yes{1}
  - cp_fill_inflight_at_inval = fills outstanding when fence.i hit; none allocated: bins n0{0},
    n1_2{[1:2]}, n3_4{[3:4]}
  - cp_cpuctrlsts_bit8 = csrr cpuctrlsts bit 8 vs ic_scr_key_valid_i (registered): bins match_1,
    match_0; ignore_bins mismatch: gen_chk_csr_readback failure
  - cp_valid_dropped_unsolicited = ic_scr_key_valid_i fell without a request: bins yes{1}
  - cp_new_code_after_fencei = store, fence.i, execute: RVFI shows the new instruction: bins yes{1}
- Crosses:
  - cr_trigger_x_delay = cp_trigger x cp_key_delay: bins reset_k256p{reset,k256p},
    fencei_k0_1{fencei_from_idle,k0_1}, restart_k16_255{fencei_restart,k16_255},
    fencei_never{fencei_from_idle,never_in_test}
  - cr_state_x_inflight = cp_fencei_state x cp_fill_inflight_at_inval: bins idle_n3_4{idle,n3_4},
    restart_n1_2{inval_cache_restart,n1_2}
- Adopted (riscv-dv): none
- TP items: TP-IC-007, TP-IC-008, TP-IC-009, TP-IC-010, TP-IC-011, TP-IC-012, TP-IC-013, TP-IC-014,
  TP-IC-015, TP-IC-016, TP-IC-047

### CG-IC-003: gen_cg_ic_lookup
- Features: F-IC-014, F-IC-015, F-IC-016, F-IC-017, F-IC-018, F-IC-021, F-IC-039, F-IC-042,
  F-IC-013
- Sample: each lookup result as reconstructed by gen_icache_ram_model's shadow tag view (P2: the
  model mirrors every tag write it receives, so the hit/miss and way-validity outcome of a lookup
  index is derivable from the boundary; boundary derivation first, probe only if it fails);
  condition: a lookup read occurred with the cache enabled and not invalidating; anti-vacuity:
  pass-through lookups do not sample; a hit proves a tag comparison whose consequence (bus request
  or none) gen_chk_icache verified.
- Coverpoints:
  - cp_result: bins hit_way0, hit_way1, miss_alloc_way0, miss_alloc_way1, miss_no_alloc_disabled,
    miss_no_alloc_invalidating, miss_ecc_forced
  - cp_index_fill = validity of the two ways at the index before the lookup: bins none_valid,
    one_valid, both_valid
  - cp_victim = replacement choice on a miss with both ways valid: bins rr_way0, rr_way1
  - cp_all_lines_valid = every index has both ways valid (model view) at a miss: bins yes{1}
  - cp_hit_bus_traffic = a hit produced a bus request: bins none{0}, spec_branch_only{1}
  - cp_hit_cadence = consecutive hit retirements at 1 instruction/cycle: bins run2_3{[2:3]},
    run4p{[4:$]}
  - cp_miss_forward_latency = instr_rvalid_i to rvfi_valid of the demanded word: bins l1_2{[1:2]},
    l3p{[3:$]}
  - cp_priv = privilege at the lookup (RVFI mode): bins m, u
  - cp_two_ways_same_tag = model holds the same tag valid in both ways at one index: bins yes{1}
- Crosses:
  - cr_result_x_fill = cp_result x cp_index_fill: bins alloc0_none{miss_alloc_way0,none_valid},
    alloc1_one{miss_alloc_way1,one_valid}, evict_both{miss_alloc_way0 or miss_alloc_way1,both_valid},
    hit1_both{hit_way1,both_valid}; ignore hit_* x none_valid: no valid way to hit
  - cr_result_x_priv = cp_result x cp_priv: bins hit0_u{hit_way0,u}, alloc_u{miss_alloc_way0 or
    miss_alloc_way1,u}
- Adopted (riscv-dv): none
- TP items: TP-IC-017, TP-IC-018, TP-IC-019, TP-IC-020, TP-IC-021, TP-IC-022, TP-IC-025, TP-IC-026,
  TP-IC-034, TP-IC-035, TP-IC-037, TP-IC-038, TP-IMEM-019

### CG-IC-004: gen_cg_ic_fill
- Features: F-IC-019, F-IC-020, F-IC-021, F-IC-036, F-IC-037, F-IC-043, F-IMEM-015, F-IMEM-018
- Sample: fill-buffer lifecycle closure as seen by the imem agent (a line's beats granted and
  answered) plus the ram model's fill write or its absence; condition: closure; anti-vacuity:
  only lines fetched over the bus sample; a hit proves a fill with the binned entry/delay/redirect
  shape and the allocation decision gen_chk_icache checked.
- Coverpoints:
  - cp_entry_beat = first requested word of the line: bins w0, w1_wrap
  - cp_beat_delays = rvalid latency class per beat: bins both_fast, first_slow, second_slow,
    both_slow
  - cp_redirect_during_fill = redirect relative to the fill's grants: bins none, after_beat1_gnt,
    after_beat2_gnt, before_any_gnt_cancelled
  - cp_written_after_redirect = stale allocating fill still wrote the line: bins yes{1}, not_alloc{0}
  - cp_busy_buffers = fill buffers busy at allocation (agent count of open lines): bins b1{1}, b2{2},
    b3{3}, b4{4}
  - cp_saturation_stall = new lookups stopped while 4 lines were open under slow rvalid: bins yes{1}
  - cp_err_line = a beat carried an injected error; no fill write, later refetch on bus: bins
    not_cached{1}; ignore_bins cached{0}: gen_chk_icache failure
  - cp_pmp_denied_line = line PMP-denied for the executing privilege was allocated: bins cached{1}
  - cp_pmp_line_later_hit = that line hit later under a permitting privilege/PMP config: bins yes{1}
  - cp_spec_branch_req = branch target lookup issued a bus request although it hit: bins yes{1},
    suppressed_other_req_pending{0}
  - cp_spec_resp_discarded = the speculative beat's response consumed, data unused: bins yes{1}
  - cp_spec_err_ignored = injected error on that speculative beat produced no trap: bins yes{1}
  - cp_same_line_two_ways = second buffer for a line under fill allocated; two fill writes: bins
    yes{1}
- Crosses:
  - cr_entry_x_delays = cp_entry_beat x cp_beat_delays: bins w1_both_slow{w1_wrap,both_slow},
    w0_second_slow{w0,second_slow}, w1_first_slow{w1_wrap,first_slow}
  - cr_redirect_x_written = cp_redirect_during_fill x cp_written_after_redirect: bins
    after1_written{after_beat1_gnt,yes}, after2_written{after_beat2_gnt,yes}
  - cr_busy_x_delays = cp_busy_buffers x cp_beat_delays: bins b4_both_slow{b4,both_slow},
    b3_first_slow{b3,first_slow}
- Adopted (riscv-dv): none
- TP items: TP-IC-023, TP-IC-024, TP-IC-025, TP-IC-026, TP-IC-027, TP-IC-028, TP-IC-039, TP-IC-040,
  TP-IC-041, TP-IC-052, TP-IMEM-015, TP-IMEM-019, TP-IMEM-020

### CG-IC-005: gen_cg_ic_enable
- Features: F-IC-012, F-IC-013, F-IC-027, F-IC-040, F-IC-041, F-FE-022, F-IC-039, F-IC-048
- Sample: each cpuctrlsts write on RVFI that changes bit 0, each debug entry/exit, and each U-mode
  cpuctrlsts access; condition: event; anti-vacuity: enable transitions come only from the
  program; the in-flight count is the agent's; a hit proves the toggle landed on live traffic.
- Coverpoints:
  - cp_transition: bins off_to_on, on_to_off, on_to_on, off_to_off
  - cp_fills_inflight = open lines at the write: bins n0{0}, n1_2{[1:2]}, n3_4{[3:4]}
  - cp_inflight_alloc_dropped = a line in flight at on_to_off was not written: bins yes{1}
  - cp_no_backfill = a non-caching line in flight at off_to_on was not written: bins yes{1}
  - cp_reset_value = first csrr cpuctrlsts bit 0 == 0: bins zero{1}
  - cp_all_fetch_on_bus_when_off = every retirement while off had a bus record: bins yes{1}
  - cp_debug = debug-mode effect: bins entry_with_en_forced_off, exit_hits_resume,
    entry_with_en_off
  - cp_debug_alloc = fill write during debug mode: bins none{0}; ignore_bins seen{1}: contradicts
    F-IC-040
  - cp_priv_access = cpuctrlsts access privilege: bins m_ok, u_illegal_insn
  - cp_old_lines_hit_after_reenable = a line cached before on_to_off hit after off_to_on: bins yes{1}
  - cp_effect_latency = first lookup after the csrw that reflected the new enable: bins next_cycle
  - cp_off_window = retirements between an on_to_off and the following off_to_on: bins short{[1:20]},
    long{[21:$]}
  - cp_no_tag_write_while_off = no tag write other than invalidation/ECC writes between the disable
    and the re-enable (model): bins yes{1}; ignore_bins no{0}: gen_chk_icache failure (F-IC-048:
    disabling never invalidates or allocates)
- Crosses:
  - cr_trans_x_inflight = cp_transition x cp_fills_inflight: bins off_n3_4{on_to_off,n3_4},
    on_n1_2{off_to_on,n1_2}, off_n0{on_to_off,n0}
  - cr_off_window_x_hit = cp_off_window x cp_old_lines_hit_after_reenable: bins short_hit{short,yes},
    long_hit{long,yes} (F-IC-048: old lines hit after any disabled window length)
- Adopted (riscv-dv): none
- TP items: TP-FE-022, TP-IC-017, TP-IC-029, TP-IC-030, TP-IC-031, TP-IC-032, TP-IC-033, TP-IC-048,
  TP-IC-057, TP-IMEM-038

### CG-IC-006: gen_cg_ic_ecc
- Features: F-IC-030, F-IC-031, F-IC-032, F-IC-033, F-IC-034, F-IC-035, F-IC-042
- Sample: each injected RAM read corruption (gen_icache_ram_model record) closed by the DUT's
  reaction (alert_minor_o pulse and the following tag write) or by its absence; condition:
  injected; anti-vacuity: only injections sample; a hit proves gen_chk_icache / gen_chk_alerts
  verified alert, invalidation and refetch.
- Coverpoints:
  - cp_ram: bins tag, data
  - cp_bits: bins single, double
  - cp_way: bins way0{0}, way1{1}
  - cp_beat = corrupted data beat: bins beat0, beat1; ignore_bins tag_na: not applicable to tag
  - cp_alert_pulses = alert_minor_o pulses for this injection: bins one{1}; ignore_bins
    zero{0}, many{[2:$]}: gen_chk_alerts failure
  - cp_inval_ways = ways written invalid next cycle: bins all_ways, hit_way_only
  - cp_refetch = the lookup was served from the bus afterwards: bins yes{1}
  - cp_major_nmi_quiet = alert_major_* and rvfi_ext_nmi_int stayed low: bins yes{1}; ignore_bins
    no{0}: gen_chk_alerts failure
  - cp_lookups_blocked_next = no lookup read in the ecc write cycle: bins yes{1}
  - cp_no_alert_case = corruption that must NOT alert: bins unused_way_data, disabled_cache,
    during_invalidation, uninitialised_data_ram
  - cp_multiway_mismatch = both ways valid same tag, differing data (informational): bins
    alert_or_wrong{1}
  - cp_knob = knob:icache_ecc_err_rate: bins none, rare, frequent
- Crosses:
  - cr_ram_x_bits_x_way = cp_ram x cp_bits x cp_way: bins all 8 combos named <ram>_<bits>_<way>,
    e.g. tag_single_way0, data_double_way1
  - cr_data_x_beat = cp_ram x cp_beat: bins data_beat0{data,beat0}, data_beat1{data,beat1}; ignore
    tag x beat0/beat1: tag has no beats
  - cr_ram_x_inval = cp_ram x cp_inval_ways: bins tag_all{tag,all_ways}, data_hit{data,hit_way_only};
    ignore tag x hit_way_only and data x all_ways: contradict F-IC-030/031
- Adopted (riscv-dv): none
- TP items: TP-IC-035, TP-IC-036, TP-IC-037, TP-IC-038, TP-IC-042, TP-IC-043, TP-IC-044, TP-IC-049,
  TP-IC-056

### CG-IC-007: gen_cg_ic_busy_throttle
- Features: F-IC-029, F-IC-038, F-IC-043, F-IC-044
- Sample: (a) core_busy_o transitions; (b) each grant (lead computation); condition: event;
  anti-vacuity: busy reasons are derived from the sweep timeline and the agent's outstanding
  count; a hit proves core_busy_o was held by the binned reason.
- Coverpoints:
  - cp_busy_reason = why core_busy_o stayed On after the pipeline drained: bins inval_sweep,
    fill_outstanding, key_await
  - cp_wfi_after_fencei = WFI retired with the sweep running; core_busy_o Off only after the
    sweep: bins yes{1}
  - cp_lead_lines = (instr_addr_o line - rvfi_pc_rdata line) at a sequential grant (not a redirect
    target): bins l0{0}, l1{1}, l2{2}, l3{3}; ignore_bins l4p{[4:$]}: the throttle caps linear
    prefetch at FB_THRESHOLD+1 = 3 non-stale buffers (F-FE-017, F-IC-038); the 4th buffer is
    allocated only by a branch lookup, which is a redirect target and not a lead
    (CG-IC-004.cp_busy_buffers.b4 covers it)
  - cp_throttle_hold = no new sequential lookup while > FB_THRESHOLD lines open: bins yes{1}
  - cp_branch_bypasses_throttle = branch lookup issued with 3 non-stale lines open (the only way to
    4 busy buffers, F-IC-043): bins yes{1}
  - cp_output_stable = rvfi_insn equals the word delivered for its pc (indirect F-IC-044): bins
    ok{1}
- Crosses:
  - cr_reason_x_wfi = cp_busy_reason x cp_wfi_after_fencei: bins sweep_wfi{inval_sweep,yes},
    key_wfi{key_await,yes}
- Adopted (riscv-dv): none
- TP items: TP-IC-009, TP-IC-050, TP-IC-051, TP-IC-052, TP-IC-053

### CG-IC-008: gen_cg_ic_regime
- Features: F-IC-013, F-IC-014, F-IC-023, F-IC-030, F-IC-008
- Sample: rvfi_valid; condition: regime schedule active; anti-vacuity: samples the fetch source of
  each retired instruction against the active knobs; a hit proves the binned mix executed under
  the binned regime with the cache in the binned state.
- Coverpoints:
  - cp_fetch_src = source of the retired word (agent + model): bins bus_disabled, bus_sweep,
    bus_miss, cache_hit, bus_key_await
  - cp_instr_mix = knob:instr_mix: bins isa_only, m_heavy, compressed_heavy, bitmanip_heavy,
    csr_heavy, ls_heavy, branch_heavy, mixed
  - cp_imem_regime = knob:imem_rvalid_delay: bins min1, short, long, random
  - cp_ecc_knob = knob:icache_ecc_err_rate: bins none, rare, frequent
  - cp_key_knob = knob:scr_key_delay: bins immediate, delayed, withheld_then_valid
- Crosses:
  - cr_src_x_mix = cp_fetch_src x cp_instr_mix: bins hit_branch{cache_hit,branch_heavy},
    hit_compressed{cache_hit,compressed_heavy}, sweep_mixed{bus_sweep,mixed},
    await_ls{bus_key_await,ls_heavy}
  - cr_src_x_regime = cp_fetch_src x cp_imem_regime: bins miss_long{bus_miss,long},
    disabled_long{bus_disabled,long}, hit_long{cache_hit,long}
  - cr_ecc_x_key = cp_ecc_knob x cp_key_knob: bins frequent_withheld{frequent,withheld_then_valid},
    rare_delayed{rare,delayed}
- Adopted (riscv-dv): none
- TP items: TP-IC-009, TP-IC-011, TP-IC-012, TP-IC-017, TP-IC-018, TP-IC-047, TP-IC-049, TP-IC-054,
  TP-IC-055, TP-IC-056


# 3.7 Areas DIT, SEC, RST, RVFI, CHERI: Dummy instructions and data-independent timing, alerts and countermeasures, reset and boot, RVFI trace, CHERIoT carve-out


Companion of tp_sec_rst_rvfi_cheri.md. All covergroups live in the gen_ namespace and sample from
the DUT boundary or RVFI unless marked P1 (wrapper-internal dummy-instruction nets; see Probe
candidates). Parameter-derived sizes: irq_fast_i is [14:0] (15 fast lines, rtl/ibex_core.sv:122),
MHPMCounterNum = 10 (mhpmcounter3..12, rvfi_ext_mhpmcounters[0..9]), divider latency 37 cycles
(EX-03), IbexMuBiOn = 4'b0101 / IbexMuBiOff = 4'b1010 (rtl/ibex_pkg.sv:759-760). Never
`illegal_bins = default sequence`; every non-listed value is either an explicit bin, an
ignore_bins with a reason, or left to a checker (stated). "gap" = cycles between consecutive
rvfi_valid pulses. "cfg tracked" = the TB's model of cpuctrlsts bits 5:0 updated from retired
cpuctrlsts write records (WARL-legalised).

---------------------------------------------------------------------------------------------------
## DIT
---------------------------------------------------------------------------------------------------

### CG-DIT-001: gen_cg_dit_cpuctrlsts_cfg
- Features: F-DIT-001, F-DIT-006, F-DIT-008, F-DIT-011, F-DIT-012, F-DIT-023, F-SEC-031, F-SEC-032,
  F-SEC-033, F-DIT-010
- Sample: rvfi_valid of a CSR instruction whose csr field == 0x7C0 (cpuctrlsts), trapped or not;
  condition: rvfi_valid && is_csr_op(rvfi_insn) && csr_addr(rvfi_insn) == 12'h7C0; anti-vacuity:
  only cpuctrlsts accesses sample (a fraction of a percent of records); a hit proves the program
  configured or probed the security control register, and the toggle bins prove a change of DIT
  or dummy state happened during the run (the "next_insn" class is taken from the following
  retired record, so the cross proves the hand-over scenario existed).
- Coverpoints:
  - cp_access = {mode, write-effect}: bins m_write{M-mode op with csr_we}, m_read_only{M-mode
    csrrs/csrrc with rs1 == x0 or csrrsi/csrrci with uimm == 0}, u_trap{rvfi_mode == 0 &&
    rvfi_trap}
  - cp_dit = legalised new value bit 1 (m_write only): bins off{0}, on{1}
  - cp_dummy_en = new value bit 2: bins off{0}, on{1}
  - cp_mask = new value bits 5:3: bins m000{0}, m001{1}, m010{2}, m011{3}, m100{4}, m101{5},
    m110{6}, m111{7}
  - cp_icache_en = new value bit 0: bins off{0}, on{1}
  - cp_dit_toggle = {old bit 1, new bit 1}: bins off2on{0->1}, on2off{1->0}, hold_off{0->0},
    hold_on{1->1}
  - cp_dummy_toggle = {old bit 2, new bit 2}: bins off2on, on2off, hold_off, hold_on
  - cp_wr_reserved = written 1s in read-only positions: bins none{wdata[31:8] == 0},
    bits31_9{|wdata[31:9] && !wdata[8]}, bit8{wdata[8] && !(|wdata[31:9])}, both{wdata[8] &&
    |wdata[31:9]}
  - cp_next_insn = class of the next retired record: bins branch{conditional branch},
    div{div/divu/rem/remu}, mul{mul/mulh/mulhsu/mulhu}, load_store{load or store}, csr{CSR op},
    other{everything else}
- Crosses:
  - cr_dummy_mask = cp_dummy_en x cp_mask: on_m000, on_m001, on_m010, on_m011, on_m100, on_m101,
    on_m110, on_m111; ignore off_m*: the mask has no effect while dummies are disabled
  - cr_dit_next = cp_dit_toggle x cp_next_insn: off2on_branch, off2on_div, off2on_mul,
    off2on_load_store, on2off_branch, on2off_div, on2off_mul, on2off_load_store; ignore
    hold_*_*: no hand-over when the value does not change
- Adopted (riscv-dv): none
- TP items: TP-DIT-001, TP-DIT-007, TP-DIT-009, TP-DIT-011, TP-DIT-012, TP-DIT-013, TP-DIT-016,
  TP-DIT-025, TP-DIT-033, TP-SEC-014, TP-SEC-033, TP-SEC-034

### CG-DIT-002: gen_cg_dit_branch_timing
- Features: F-DIT-002, F-DIT-007, F-DIT-010
- Sample: rvfi_valid of a retired conditional branch (beq/bne/blt/bge/bltu/bgeu/c.beqz/c.bnez)
  with rvfi_trap == 0, sampled when the NEXT rvfi_valid arrives (so the gap is known);
  condition: is_cond_branch(rvfi_insn) && !rvfi_trap; anti-vacuity: only branches sample, the gap
  is computed from a following record (a hit proves a branch retired and its timing was
  observed); taken is derived from rvfi_pc_wdata != rvfi_pc_rdata + insn_len, not assumed.
- Coverpoints:
  - cp_dit = cfg tracked data_ind_timing at the branch: bins off{0}, on{1}
  - cp_taken = pc_wdata != pc_rdata + len: bins taken{1}, not_taken{0}
  - cp_compressed = rvfi_insn[1:0] != 2'b11: bins c16{1}, i32{0}
  - cp_gap = cycles to the next rvfi_valid: bins g1{1}, g2{2}, g3{3}, g4_plus{[4:$]}
  - cp_priv = rvfi_mode: bins m{3}, u{0}; ignore_bins other{1,2}: modes S/reserved do not exist
    in Ibex (checker flags them)
  - cp_pc_wdata = kind of next pc: bins fallthrough{pc_wdata == pc_rdata + len},
    target{pc_wdata == branch target}; ignore_bins neither: any other value is a checker error,
    not a coverage case
- Crosses:
  - cr_dit_taken_c = cp_dit x cp_taken x cp_compressed: off_taken_c16, off_taken_i32, off_nt_c16,
    off_nt_i32, on_taken_c16, on_taken_i32, on_nt_c16, on_nt_i32
  - cr_dit_priv = cp_dit x cp_priv: on_m, on_u, off_m, off_u
  - cr_dit_gap = cp_dit x cp_taken x cp_gap: on_taken_g2, on_nt_g2, on_taken_g3, on_nt_g3,
    off_nt_g1, off_taken_g2; no ignores (larger gaps are regime effects; the checker compares
    taken vs not-taken distributions within a regime)
- Adopted (riscv-dv): none
- TP items: TP-DIT-002, TP-DIT-003, TP-DIT-008, TP-DIT-011, TP-DIT-033

### CG-DIT-003: gen_cg_dit_muldiv_timing
- Features: F-DIT-003, F-DIT-004, F-DIT-005, F-DIT-009, F-DIT-024
- Sample: rvfi_valid of a retired RV32M instruction with rvfi_trap == 0, sampled when the next
  rvfi_valid arrives; condition: is_rv32m(rvfi_insn) && !rvfi_trap; anti-vacuity: only M
  instructions sample and the latency is measured (a hit proves the operand class and the
  observed latency class co-occurred).
- Coverpoints:
  - cp_op = funct3/funct7 decode: bins mul, mulh, mulhsu, mulhu, div, divu, rem, remu
  - cp_class = op class: bins mul{mul}, mulh{mulh, mulhsu, mulhu}, div{div, divu, rem, remu}
  - cp_dit = cfg tracked data_ind_timing: bins off{0}, on{1}
  - cp_rs2_zero = rvfi_rs2_rdata == 0: bins zero{1}, nonzero{0}
  - cp_overflow = div/rem with rs1 == 32'h80000000 && rs2 == 32'hFFFFFFFF: bins yes{1}, no{0}
  - cp_latency = gap to the next record: bins fast{[1:2]}, full{37}, other{[3:36], [38:$]}
  - cp_dummy_en = cfg tracked dummy_instr_en: bins off{0}, on{1}
- Crosses:
  - cr_div_dit_zero = cp_class x cp_dit x cp_rs2_zero: div_off_zero, div_off_nz, div_on_zero,
    div_on_nz; ignore mul*_*_*: rs2 == 0 has no timing effect on the single-cycle multiplier
  - cr_latency = cp_class x cp_dit x cp_rs2_zero x cp_latency: div_off_zero_fast,
    div_off_nz_full, div_on_zero_full, div_on_nz_full, mul_off_fast, mul_on_fast, mulh_off_fast,
    mulh_on_fast; ignore div_on_*_fast: DIT removes the fast path; no ignore on *_other: an
    "other" latency is a checker error unless dummies are enabled (a dummy stall inside the gap),
    so it stays visible as a plain bin
  - cr_op_dit = cp_op x cp_dit: div_on, divu_on, rem_on, remu_on, div_off, divu_off, rem_off,
    remu_off, mul_on, mul_off, mulh_on, mulh_off, mulhsu_on, mulhsu_off, mulhu_on, mulhu_off
- Adopted (riscv-dv): none
- TP items: TP-DIT-004, TP-DIT-005, TP-DIT-006, TP-DIT-010, TP-DIT-026

### CG-DIT-004: gen_cg_dit_dummy_insert (P1)
- Features: F-DIT-009, F-DIT-011, F-DIT-012, F-DIT-013, F-DIT-015, F-DIT-016, F-DIT-017,
  F-DIT-018, F-DIT-019, F-DIT-020, F-DIT-021, F-DIT-022, F-DIT-023, F-DIT-024, F-DIT-027,
  F-DIT-028, F-DIT-029, F-DIT-030, F-RVFI-024
- Sample: (a) rising edge of the wrapper-internal net dummy_instr_id_o while the IF/ID register
  is written (cp_event = insert), (b) the close of a test-defined dummy measurement window
  (cp_event = window_close); condition: (dummy_instr_id_o && !dummy_instr_id_o_prev) ||
  window_close_event; anti-vacuity: insert samples only when a dummy actually entered ID
  (enable alone does not sample; a hit proves insertion happened and in which context);
  window_close samples once per window so the minstret bins count real measurements.
- Coverpoints:
  - cp_event: bins insert, window_close
  - cp_type = if_stage fcov_dummy_instr_type (P1): bins add{0}, mul{1}, div{2}, and{3}
  - cp_rs1 = rf_raddr_a_o during the dummy: bins x0{0}, x1_15{[1:15]}, x16{16}, x17_31{[17:31]}
  - cp_rs2 = rf_raddr_b_o during the dummy: bins x0{0}, x1_15{[1:15]}, x16{16}, x17_31{[17:31]}
  - cp_dit = cfg tracked data_ind_timing: bins off{0}, on{1}
  - cp_mask = cfg tracked dummy_instr_mask: bins m000, m001, m010, m011, m100, m101, m110, m111
  - cp_context = TB context at the insertion cycle: bins straight{no redirect in the previous 2
    records, no pending event}, after_taken_branch{previous record a taken branch/jump},
    irq_pending{irq_pending_o == 1 and interrupts enabled}, debug_req_high{debug_req_i == 1},
    step_active{dcsr.step model set and not in debug mode}, in_irq_handler{rvfi_intr seen since
    the last mret}, u_mode{rvfi_mode model == 0}, in_zcmp{between expanded_insn first and last},
    fetch_stalled{fetch_enable_i != On or core asleep in the previous cycle},
    hazard_load_wb{a load with rd == rs1/rs2 of the dummy outstanding in WB}
  - cp_back_to_back = previous accepted ID instruction was also a dummy: bins yes{1}, no{0}
  - cp_en_cleared_in_flight = a cpuctrlsts write clearing dummy_instr_en retired while this dummy
    was in ID or WB: bins yes{1}, no{0}
  - cp_minstret_excess (window_close) = minstret delta minus RVFI record count in the window:
    bins zero{0}, positive{[1:$]}; ignore_bins negative: minstret can never lag the trace
  - cp_dummies_in_window (window_close) = P1 insert count in the window: bins none{0},
    few{[1:9]}, many{[10:$]}
  - cp_irq_delay_by_dummy (insert with cp_context irq_pending or debug_req_high; closed when the
    handler's / debug ROM's first record retires) = cycles the entry was delayed beyond the plain
    entry latency measured with dummies disabled: bins none{0}, single{[1:2]} (ADD/AND/MUL dummy),
    div{[3:37]} (DIV dummy; 37 = divider latency, D7); ignore_bins over{[38:$]}: a longer delay is
    a gen_chk_irq bound error, not coverage (F-DIT-030)
- Crosses:
  - cr_type_dit = cp_type x cp_dit: div_on, div_off, mul_on, mul_off, add_on, add_off, and_on,
    and_off
  - cr_type_irq = cp_type x cp_context (event contexts only): div_irq_pending, mul_irq_pending,
    add_irq_pending, and_irq_pending, div_debug_req_high; ignore the other cp_context values: the
    mask x context pairs belong to cr_mask_ctx (F-DIT-030)
  - cr_mask_ctx = cp_mask x cp_context: m000_straight, m111_straight, m000_after_taken_branch,
    m000_irq_pending, m000_debug_req_high, m000_step_active, m000_in_zcmp, m000_hazard_load_wb;
    ignore *_fetch_stalled: insertion is impossible while fetch is stalled (the bin exists on
    cp_context to prove the negative was watched; the cross stays unhit by construction)
  - cr_div_rs2 = cp_type x cp_rs2 x cp_dit: div_x0_on, div_x0_off, div_x17_31_on, div_x1_15_off
- Adopted (riscv-dv): none
- TP items: TP-DIT-010, TP-DIT-012, TP-DIT-013, TP-DIT-014, TP-DIT-016, TP-DIT-017, TP-DIT-018,
  TP-DIT-019, TP-DIT-020, TP-DIT-021, TP-DIT-022, TP-DIT-023, TP-DIT-024, TP-DIT-025,
  TP-DIT-026, TP-DIT-029, TP-DIT-030, TP-DIT-031, TP-DIT-032, TP-DIT-033, TP-DIT-034, TP-RVFI-027

### CG-DIT-005: gen_cg_dit_secureseed
- Features: F-DIT-014, F-DIT-025, F-DIT-026, F-DIT-010
- Sample: rvfi_valid of a CSR instruction with csr field == 0x7C1 (secureseed), trapped or not;
  condition: rvfi_valid && is_csr_op(rvfi_insn) && csr_addr(rvfi_insn) == 12'h7C1;
  anti-vacuity: only secureseed accesses sample; the effect bins are computed from the operand
  (rs1/uimm) and the running-seed model, and cp_pattern_changed from the P1 insertion sequence
  before/after the write, so a hit proves a reseed scenario, not merely a CSR access.
- Coverpoints:
  - cp_op = CSR op form: bins csrrw, csrrs, csrrc, csrrwi, csrrsi, csrrci
  - cp_effect: bins write{csr_we, mode M}, read_only{csrrs/csrrc rs1 == x0 or csrrsi/csrrci
    uimm == 0, mode M}, u_trap{rvfi_mode == 0 && rvfi_trap}
  - cp_wdata = write data class: bins zero{0}, nonzero{!= 0 and != seed_q model},
    cancels_seed{== seed_q model, so the XOR gives an all-zero LFSR seed}
  - cp_dummy_en_at_write = cfg tracked dummy_instr_en: bins off{0}, on{1}
  - cp_readback_zero = rvfi_rd_wdata == 0 on a read: bins yes{1}; mismatch (nonzero read) is a
    checker error, not a bin
  - cp_pattern_changed (P1) = insertion-position sequence after the op differs from before:
    bins yes{1}, no{0}
- Crosses:
  - cr_effect_dummy = cp_effect x cp_dummy_en_at_write: write_on, write_off, read_only_on,
    read_only_off
  - cr_wdata_effect = cp_wdata x cp_effect: zero_write, nonzero_write, cancels_seed_write; ignore
    *_read_only and *_u_trap: no write data takes effect
- Adopted (riscv-dv): none
- TP items: TP-DIT-011, TP-DIT-015, TP-DIT-027, TP-DIT-028

---------------------------------------------------------------------------------------------------
## SEC
---------------------------------------------------------------------------------------------------

### CG-SEC-001: gen_cg_sec_alerts
- Features: F-SEC-001, F-SEC-002, F-SEC-003, F-SEC-007, F-SEC-008, F-SEC-009, F-SEC-010,
  F-SEC-011, F-SEC-013, F-SEC-034, F-SEC-035, F-SEC-036, F-DIT-017, F-DIT-022
- Sample: any cycle where an alert output is high, any TB injection event, and once at end of
  test (eot); condition: alert_minor_o || alert_major_internal_o || alert_major_bus_o ||
  inject_event || eot; anti-vacuity: alerts and injections are rare (a few per run) so the
  sample is far from always-true; the eot sample carries run totals so "zero" bins are hit only
  when a full run completed with the count actually zero.
- Coverpoints:
  - cp_event: bins alert_minor, alert_major_bus, alert_major_internal, inject, eot
  - cp_alert = {minor, major_bus, major_internal} at the sample: bins none{000}, minor{001},
    major_bus{010}, major_internal{100}; ignore_bins multi: two alerts in one cycle have no
    common cause in this DUT (checker reports it)
  - cp_inject_kind = most recent injection within the correlation window: bins none, icache_ecc,
    ibus_intg, dbus_load_intg, dbus_store_intg, spurious_dbus_intg, pc_fault
  - cp_phase: bins in_reset{rst_ni == 0}, post_reset_2cyc{first two cycles after release},
    running, fetch_disabled{fetch_enable_i != On}, in_wfi{core_busy_o == Off},
    in_debug{rvfi_ext_debug_mode model}
  - cp_minor_count_per_inject (eot or per injection close) = alert_minor_o pulses attributed to
    one icache_ecc injection: bins zero{0}, one{1}; other values (two or more pulses) are
    gen_chk_alerts errors, not bins
  - cp_internal_total (eot) = alert_major_internal_o pulse count in the run: bins zero{0},
    nonzero{[1:$]}
  - cp_pulse_width = consecutive high cycles of the sampled alert: bins one_cycle{1},
    multi_cycle{[2:$]}
- Crosses:
  - cr_alert_inject = cp_alert x cp_inject_kind: minor_icache_ecc, major_bus_ibus_intg,
    major_bus_dbus_load_intg, major_bus_dbus_store_intg, major_bus_spurious_dbus_intg,
    major_internal_pc_fault, none_none; ignore minor_{ibus_intg, dbus_*, spurious_*, pc_fault,
    none}: alert_minor_o has a single source; ignore major_internal_{icache_ecc, *_intg, none}:
    RegFileECC = 0 and ShadowCSR = 0 leave the PC check as the only internal source; ignore
    major_bus_{icache_ecc, pc_fault, none}: bus alert only from integrity errors
  - cr_alert_phase = cp_alert x cp_phase: major_bus_in_reset, major_bus_running,
    major_bus_fetch_disabled, minor_running, minor_in_debug, none_in_reset, none_post_reset_2cyc;
    ignore minor_in_reset and major_internal_in_reset: no cache lookup or ID instruction exists
    in reset
- Adopted (riscv-dv): none
- TP items: TP-DIT-018, TP-DIT-024, TP-SEC-001, TP-SEC-002, TP-SEC-003, TP-SEC-004, TP-SEC-005,
  TP-SEC-006, TP-SEC-007, TP-SEC-008, TP-SEC-009, TP-SEC-010, TP-SEC-011, TP-SEC-013,
  TP-SEC-014, TP-SEC-015, TP-SEC-017, TP-SEC-035, TP-SEC-036, TP-SEC-037, TP-SEC-039, TP-RST-020

### CG-SEC-002: gen_cg_sec_bus_intg
- Features: F-SEC-003, F-SEC-015, F-SEC-016, F-SEC-017, F-SEC-018, F-SEC-019, F-RVFI-021,
  F-RVFI-031
- Sample: a TB integrity-injection event on a returned bus beat (rvalid with corrupted check
  bits) or an unsolicited data response, closed when the DUT response is classified (bounded
  window); condition: intg_inject_event || spurious_dbus_event; anti-vacuity: only injected or
  unsolicited beats sample (never in a clean run); the response fields are observed (alert,
  NMI record, suppress flag, trap), so a hit proves the injection class met its response class.
- Coverpoints:
  - cp_side: bins ibus, dbus
  - cp_dbus_op = what the beat answered: bins load, store, spurious{no request outstanding},
    na{ibus}
  - cp_err_bits = number of flipped check/data bits: bins single{1}, double{2}, multi{[3:$]}
  - cp_ibus_consumed: bins executed{the word's PC later appears as rvfi_pc_rdata},
    discarded{it never does}, na{dbus}
  - cp_half = misaligned position of the beat: bins aligned, first, second, na{ibus/spurious}
  - cp_nmi_taken = a record with rvfi_ext_nmi_int == 1 follows within the window: bins yes, no
  - cp_nmi_latency = instructions retired between the faulting record and the NMI entry: bins
    same_insn{0}, next_insn{1}; ignore_bins later{[2:$]}: the RTL takes the internal NMI at most
    one instruction later (checker error if seen)
  - cp_rf_wr_suppress = rvfi_ext_rf_wr_suppress on the load record: bins yes, no
  - cp_fetch_fault = an rvfi_trap with mcause 1 follows for that PC: bins yes, no
  - cp_load_size: bins byte, half, word, na
- Crosses:
  - cr_side_op = cp_side x cp_dbus_op: ibus_na, dbus_load, dbus_store, dbus_spurious; ignore
    ibus_{load, store, spurious} and dbus_na: undefined combinations
  - cr_load_half = cp_dbus_op x cp_half x cp_rf_wr_suppress: load_aligned_yes, load_first_yes,
    load_second_yes, store_aligned_no, store_first_no, store_second_no; ignore store_*_yes: a
    store writes no register; ignore load_*_no: a corrupted load response always suppresses
    (checker error, not coverage)
  - cr_ibus_consumed = cp_side x cp_ibus_consumed x cp_fetch_fault: ibus_executed_yes,
    ibus_discarded_no; ignore ibus_executed_no and ibus_discarded_yes: consumed words fault,
    discarded ones cannot; ignore dbus_*: n/a
  - cr_errbits_side = cp_err_bits x cp_side: single_ibus, double_ibus, multi_ibus, single_dbus,
    double_dbus, multi_dbus
- Adopted (riscv-dv): none
- TP items: TP-SEC-007, TP-SEC-008, TP-SEC-009, TP-SEC-010, TP-SEC-011, TP-SEC-012

### CG-SEC-003: gen_cg_sec_double_fault
- Features: F-SEC-022, F-SEC-023, F-SEC-024, F-SEC-025, F-SEC-026
- Sample: double-fault model events: a synchronous-exception record (rvfi_trap && !debug-entry
  ebreak), a retired mret, an interrupt/NMI handler entry (rvfi_intr), a debug entry
  (rvfi_ext_debug_mode rising), a cpuctrlsts write touching bit 6 or 7; condition: any of those;
  anti-vacuity: each event is a distinct, infrequent record class; the seen_before/pulse fields
  come from the model state and the double_fault_seen_o monitor, so a hit proves the event met
  the detector in that state.
- Coverpoints:
  - cp_event: bins sync_exc, mret, irq_entry, nmi_entry, debug_entry, sw_set_b6, sw_clr_b6,
    sw_set_b7, sw_clr_b7
  - cp_seen_before = model sync_exc_seen before the event: bins clear{0}, set{1}
  - cp_pulse = double_fault_seen_o pulsed within 2 cycles of the event: bins yes, no
  - cp_debug_mode = event happened in debug mode: bins no, yes
  - cp_mret_context = handler the mret returns from: bins exc_handler, irq_handler, nmi_handler,
    na{not an mret}
  - cp_sticky_after = cpuctrlsts bit 7 model after the event: bins clear, set
  - cp_sync_exc_cause: bins illegal, ecall, ebreak, fetch_fault, load_fault, store_fault,
    breakpoint{trigger-caused}, na{not a sync exception}
- Crosses:
  - cr_event_seen = cp_event x cp_seen_before x cp_debug_mode: sync_exc_clear_no,
    sync_exc_set_no, sync_exc_set_yes, sync_exc_clear_yes, mret_set_no, irq_entry_set_no,
    nmi_entry_set_no, debug_entry_set_no, sw_set_b6_clear_no, sw_clr_b7_set_no; ignore mret_*_yes:
    mret in debug mode is not the return path (dret is); ignore irq_entry_*_yes and
    nmi_entry_*_yes: interrupts are not taken in debug mode
  - cr_mret_ctx = cp_event x cp_mret_context: mret_exc_handler, mret_irq_handler,
    mret_nmi_handler; ignore mret_na and non-mret events: context defined only for mret
  - cr_cause_pulse = cp_sync_exc_cause x cp_pulse: illegal_yes, ecall_yes, ebreak_yes,
    fetch_fault_yes, load_fault_yes, store_fault_yes, breakpoint_yes; ignore na_*: not a sync
    exception
- Adopted (riscv-dv): none
- TP items: TP-SEC-021, TP-SEC-022, TP-SEC-023, TP-SEC-024, TP-SEC-025, TP-SEC-026, TP-SEC-027

### CG-SEC-004: gen_cg_sec_crash_dump
- Features: F-SEC-027, F-SEC-028, F-SEC-029, F-SEC-030
- Sample: a change of any crash_dump_o field (per-field edge), plus every trap-taken event and
  reset release (so "no change" cases in debug mode can be sampled); condition: field_changed ||
  trap_taken_event || reset_release; anti-vacuity: fields change on specific pipeline events
  only; the trigger is classified from the monitors (RVFI record, pc_set class from the ibus
  redirect, data request, CSR write record), so a hit proves the field moved for that reason.
- Coverpoints:
  - cp_field: bins current_pc, next_pc, last_data_addr, exception_pc, exception_addr
  - cp_trigger: bins retire{record retired}, pc_set_branch{jump/branch redirect},
    pc_set_trap{synchronous exception}, pc_set_irq{interrupt/NMI}, pc_set_debug{debug entry},
    data_req{data_req_o & gnt}, csr_write{csrw mepc/mtval retired}, reset{rst_ni low},
    boot{BOOT_SET cycle}
  - cp_misaligned = the data request that moved last_data_addr: bins no{aligned},
    first_half{first transaction of a split}, second_half{second transaction}, na{other fields}
  - cp_debug_mode: bins no, yes
  - cp_changed = the field value differs from the previous sample: bins yes, no
  - cp_value_class: bins zero{0}, boot_page{[boot_addr_i[31:8] page]}, program{inside the
    program image}, mmio{inside the TB MMIO window}
- Crosses:
  - cr_field_trigger = cp_field x cp_trigger: current_pc_retire, current_pc_boot,
    next_pc_pc_set_branch, next_pc_pc_set_trap, next_pc_pc_set_irq, next_pc_pc_set_debug,
    next_pc_boot, last_data_addr_data_req, last_data_addr_reset, exception_pc_pc_set_trap,
    exception_pc_pc_set_irq, exception_pc_csr_write, exception_pc_reset,
    exception_addr_pc_set_trap, exception_addr_csr_write, exception_addr_reset; ignore
    last_data_addr_{retire, pc_set_*, csr_write, boot}: the LSU address moves only on requests
    or reset; ignore exception_*_{data_req, pc_set_branch, boot, retire}: mepc/mtval move only on
    traps, CSR writes and reset; ignore current_pc_{data_req, csr_write}: unrelated
  - cr_lda_misaligned = cp_field x cp_misaligned: last_data_addr_no, last_data_addr_first_half,
    last_data_addr_second_half; ignore other fields x {no, first_half, second_half}: n/a
  - cr_exc_debug = cp_field x cp_debug_mode x cp_changed: exception_pc_yes_no,
    exception_addr_yes_no, exception_pc_no_yes, exception_addr_no_yes; ignore
    exception_*_yes_yes: a debug-mode exception must not move mepc/mtval (checker error)
- Adopted (riscv-dv): none
- TP items: TP-SEC-028, TP-SEC-029, TP-SEC-030, TP-SEC-031, TP-SEC-032

### CG-SEC-005: gen_cg_sec_ctrl_inputs
- Features: F-SEC-012, F-SEC-020, F-SEC-021, F-SEC-022, F-SEC-025, F-SEC-031, F-SEC-033,
  F-RST-003, F-RST-007, F-RST-014, F-RST-025, F-RVFI-020
- Sample: (a) rvfi_valid of a csrr reading cpuctrlsts, (b) a value change of fetch_enable_i or
  mcounteren_writable_i, (c) an ic_scr_key_req_o pulse or ic_scr_key_valid_i change, (d) a
  retired mcounteren write, (e) a change of boot_addr_i after the first instr_req_o; condition:
  any of (a)-(e), cp_event says which; anti-vacuity: each event is discrete and infrequent; the readback bins compare the rd value against the input
  history, so a hit proves the read observed the modelled input state.
- Coverpoints:
  - cp_event: bins cpuctrl_read, fetch_en_change, mcounteren_w_change, key_req,
    key_valid_change, mcounteren_write, boot_addr_change
  - cp_boot_addr_change_ctx (boot_addr_change) = pipeline context at the change: bins
    running{instructions retiring}, in_handler{between a trap record and its mret},
    in_wfi{core_busy_o == Off}; the effect is a checker rule (gen_isa_compare / gen_chk_ibus_proto:
    no PC redirect and no mtvec change may follow), so there is no effect bin (F-RST-003, F-RST-025
    folded)
  - cp_bit8_readback (cpuctrl_read) = rd[8]: bins zero, one
  - cp_bit8_vs_input (cpuctrl_read) = rd[8] == ic_scr_key_valid_i one cycle before the read's
    ID completion: bins match_delayed{1}, na{other events}; the mismatch case is a checker error
    (not a bin) so the coverpoint cannot be satisfied by a wrong read
  - cp_bits67_readback (cpuctrl_read) = rd[7:6]: bins b6_0_b7_0, b6_1_b7_0, b6_0_b7_1, b6_1_b7_1
  - cp_icache_en_readback_in_debug (cpuctrl_read with rvfi_ext_debug_mode) = rd[0]: bins one,
    zero
  - cp_fetch_en_val = new fetch_enable_i: bins on{4'b0101}, off{4'b1010}, invalid{all other 14
    values}
  - cp_mcounteren_w_val = mcounteren_writable_i at the write: bins on, off, invalid
  - cp_mcounteren_write_effect = read-back after the write: bins applied{value changed to the
    legalised write data}, dropped{unchanged}
  - cp_key_delay = knob:scr_key_delay value in force: bins immediate, delayed, withheld_then_valid
  - cp_key_req_context = why the cache requested a key: bins reset_inval, fence_i, debug_mode,
    icache_disabled
  - cp_rvfi_ext_key_valid (cpuctrl_read) = rvfi_ext_ic_scr_key_valid on the read record: bins
    zero, one
- Crosses:
  - cr_mcounteren = cp_mcounteren_w_val x cp_mcounteren_write_effect: on_applied, off_dropped,
    invalid_dropped; ignore on_dropped, off_applied, invalid_applied: checker errors, not
    coverage
  - cr_key = cp_key_delay x cp_bit8_readback: immediate_one, delayed_zero, delayed_one,
    withheld_then_valid_zero, withheld_then_valid_one; ignore immediate_zero: with an immediate
    responder the valid never drops long enough for a read to see 0 (if the poll loop does hit
    it, promote to a bin)
  - cr_key_ctx = cp_key_req_context x cp_key_delay: reset_inval_immediate, fence_i_delayed,
    fence_i_withheld_then_valid, reset_inval_withheld_then_valid, fence_i_immediate,
    reset_inval_delayed, debug_mode_delayed, icache_disabled_immediate
- Adopted (riscv-dv): none
- TP items: TP-SEC-016, TP-SEC-019, TP-SEC-020, TP-SEC-021, TP-SEC-022, TP-SEC-026, TP-SEC-033,
  TP-SEC-034, TP-RST-004, TP-RST-007, TP-RVFI-023

### CG-SEC-006: gen_cg_sec_core_busy
- Features: F-SEC-014, F-RST-016, F-RST-017, F-RVFI-028, F-DIT-028
- Sample: a change of core_busy_o, a retired WFI record, and a wake event (an irq/NMI/debug
  input rising while core_busy_o == Off); condition: core_busy_o != core_busy_o_prev ||
  wfi_retired || wake_event; anti-vacuity: transitions are rare (sleep entry/exit), and the hold
  causes are derived from the bus monitors and pins, so a hit proves the busy value coincided
  with the named cause.
- Coverpoints:
  - cp_value = core_busy_o: bins on{4'b0101}, off{4'b1010}; every other value is a
    gen_chk_sleep error, deliberately not a bin
  - cp_transition: bins on2off, off2on
  - cp_off_reason = why Off: bins wfi_sleep{SLEEP with no wake source}, wait_sleep{the WAIT_SLEEP
    cycle immediately after the WFI drained}
  - cp_on_hold_cause = why still On after a WFI retired: bins fetch_outstanding{ibus beats not
    returned}, lsu_outstanding{data response pending}, irq_pending{irq_pending_o == 1},
    debug_req{debug_req_i == 1}, debug_mode{WFI in debug mode}, step{dcsr.step set}
  - cp_wake_source = input that ended the Off period: bins irq, nmi, debug_req, step{dcsr.step
    set: Off limited to the WAIT_SLEEP cycle}, none{a source was already pending at the WFI: Off
    limited to the WAIT_SLEEP cycle or absent}
  - cp_priv_at_wfi = rvfi_mode of the WFI record: bins m{3}, u{0}
  - cp_mie_at_wfi = mstatus.MIE model at the WFI: bins set, clear
- Crosses:
  - cr_wake = cp_transition x cp_wake_source: off2on_irq, off2on_nmi, off2on_debug_req,
    off2on_step{the WAIT_SLEEP -> SLEEP -> FIRST_FETCH path with step set}; ignore on2off_*: the
    wake source is defined for the Off -> On edge only
  - cr_hold = cp_value x cp_on_hold_cause: on_fetch_outstanding, on_lsu_outstanding,
    on_irq_pending, on_debug_req, on_debug_mode, on_step; ignore off_*: a hold cause implies On
  - cr_wfi_mie = cp_off_reason x cp_mie_at_wfi x cp_priv_at_wfi: wfi_sleep_set_m,
    wfi_sleep_clear_m, wfi_sleep_set_u, wfi_sleep_clear_u, wait_sleep_set_m; no ignores (U-mode
    WFI with TW = 0 sleeps like M-mode)
- Adopted (riscv-dv): none
- TP items: TP-DIT-030, TP-SEC-018, TP-RST-008, TP-RST-015, TP-RST-016, TP-RVFI-031

---------------------------------------------------------------------------------------------------
## RST
---------------------------------------------------------------------------------------------------

### CG-RST-001: gen_cg_rst_boot
- Features: F-RST-002, F-RST-003, F-RST-004, F-RST-005, F-RST-006, F-RST-008, F-RST-009,
  F-RST-013, F-RST-024, F-RST-025, F-RST-026, F-SEC-037
- Sample: rst_ni release, closed when the first post-reset event is classified (first retired
  record, irq/NMI entry, debug entry, or a timeout with fetch disabled); condition:
  reset_release_event; anti-vacuity: one sample per reset; the fields are observed from the
  ibus monitor and RVFI after the release (first request address, first record's order and
  mode), so a hit proves the boot proceeded as classified.
- Coverpoints:
  - cp_boot_addr = boot_addr_i[31:8] class: bins zero{0}, low{[1:32'h0FFFFF]},
    mid{[32'h100000:32'h7FFFFF]}, high{[32'h800000:32'hFFFFFF]}
  - cp_boot_low_byte = boot_addr_i[7:0]: bins zero{0}; ignore_bins nonzero: the RTL assertion
    IbexBootAddrUnaligned forbids it (TB never drives it)
  - cp_fetch_en_at_release = fetch_enable_i in the release cycle: bins on, off, invalid
  - cp_pending = inputs pending at release: bins none, irq_enabled_later{an irq line high, mie
    still 0}, nmi{irq_nm_i}, debug_req{debug_req_i}, nmi_and_debug, irq_and_debug
  - cp_first_event: bins first_instr_retire, nmi_taken, debug_entry, none_fetch_disabled{no
    event within the window because fetch stayed disabled}; ignore_bins irq_taken: mstatus.MIE
    and mie are 0 at reset so a maskable interrupt can never be the first event
  - cp_hart_id = hart_id_i: bins zero{0}, max{32'hFFFFFFFF}, random{other}
  - cp_first_fetch_addr_match = first instr_addr_o == {boot_addr_i[31:8], 8'h80}: bins yes{1};
    the mismatch is a checker error (no bin)
  - cp_first_order_one = first rvfi_order == 1: bins yes{1}; mismatch is a checker error
  - cp_reset_kind: bins power_on, mid_run
  - cp_boot_to_req_cycles = cycles from release to the first instr_req_o: bins two{2}, three{3},
    more{[4:$]}; ignore_bins fewer{[0:1]}: RESET state never requests
- Crosses:
  - cr_pending_first = cp_pending x cp_first_event: none_first_instr_retire,
    irq_enabled_later_first_instr_retire, nmi_nmi_taken, debug_req_debug_entry,
    nmi_and_debug_debug_entry, nmi_and_debug_nmi_taken, irq_and_debug_debug_entry; ignore
    irq_enabled_later_irq_taken: MIE and mie are 0 at reset so an interrupt cannot be the first
    event; ignore none_{irq_taken, nmi_taken, debug_entry}: nothing pending
  - cr_fetch_en_first = cp_fetch_en_at_release x cp_first_event: on_first_instr_retire,
    off_none_fetch_disabled, invalid_none_fetch_disabled, off_first_instr_retire{fetch enabled
    later}; ignore on_none_fetch_disabled: fetch enabled means an event must occur
  - cr_boot_kind = cp_boot_addr x cp_reset_kind: zero_power_on, low_power_on, mid_power_on,
    high_power_on, zero_mid_run, low_mid_run, mid_mid_run, high_mid_run
- Adopted (riscv-dv): none
- TP items: TP-RST-001, TP-RST-002, TP-RST-003, TP-RST-004, TP-RST-005, TP-RST-006, TP-RST-008,
  TP-RST-012, TP-RST-017, TP-RST-024, TP-RST-025, TP-RST-026, TP-RST-027, TP-RST-029, TP-SEC-038

### CG-RST-002: gen_cg_rst_midrun
- Features: F-RST-001, F-RST-009, F-RST-018, F-RST-019, F-SEC-035, F-RVFI-033
- Sample: falling edge of rst_ni after the first instruction retired (mid-run reset) and the
  power-on reset release, closed when the post-reset response window (16 cycles) has elapsed;
  condition: reset_assert_event || power_on_release; anti-vacuity: at most a few samples per
  run; the in-flight class comes from the monitors' state at the edge and the post-response
  class from beats actually returned after release, so a hit proves the reset interrupted that
  activity.
- Coverpoints:
  - cp_inflight = DUT activity at the reset edge: bins idle, fetch_outstanding,
    load_outstanding, store_outstanding, misaligned_first_done{first half done, second pending},
    div_in_flight, zcmp_mid, in_wfi, in_debug, in_exc_handler, in_irq_handler, in_nmi_handler,
    fetch_disabled, dummy_in_id{P1}
  - cp_reset_len = cycles rst_ni held low: bins one_cycle{1}, short{[2:9]}, long{[10:$]}
  - cp_post_response = beats returned by the memory models after release for pre-reset requests:
    bins none, good_intg, bad_intg
  - cp_outstanding_count = granted-but-unanswered bus beats at the edge (both sides): bins
    zero{0}, one{1}, two{2}, many{[3:$]}
  - cp_alert_during_reset = alerts seen while rst_ni == 0: bins none, major_bus; ignore_bins
    minor_or_internal: no cache lookup or ID instruction in reset (checker error if seen)
  - cp_outputs_at_reset_ok = every output at its reset value within the assert cycle: bins yes{1};
    the failure is a checker error, not a bin
- Crosses:
  - cr_inflight_resp = cp_inflight x cp_post_response: idle_none, fetch_outstanding_good_intg,
    fetch_outstanding_bad_intg, load_outstanding_good_intg, load_outstanding_bad_intg,
    store_outstanding_good_intg, store_outstanding_bad_intg, misaligned_first_done_none,
    misaligned_first_done_good_intg; ignore idle_{good_intg, bad_intg}: nothing outstanding can
    return; ignore {in_wfi, in_debug, in_*_handler, fetch_disabled, div_in_flight, zcmp_mid,
    dummy_in_id}_{good_intg, bad_intg} unless a bus beat was also outstanding: the response class
    is tracked through cp_outstanding_count instead
  - cr_inflight_len = cp_inflight x cp_reset_len: div_in_flight_one_cycle, div_in_flight_short,
    zcmp_mid_short, in_wfi_long, in_wfi_short, in_debug_short, in_irq_handler_short,
    in_nmi_handler_short, in_exc_handler_short, dummy_in_id_short, fetch_disabled_short,
    idle_long
- Adopted (riscv-dv): none
- TP items: TP-RST-001, TP-RST-017, TP-RST-018, TP-RST-019, TP-RST-029, TP-SEC-035, TP-SEC-036,
  TP-RVFI-036

### CG-RST-003: gen_cg_rst_fetch_enable
- Features: F-RST-010, F-RST-011, F-RST-012, F-RST-014, F-RST-015, F-SEC-012, F-DIT-028
- Sample: a value change of fetch_enable_i while rst_ni == 1, closed when the value changes again
  (hold length known) and the retirements after the edge have been counted; condition:
  fetch_enable_i != fetch_enable_i_prev; anti-vacuity: the input is static in most runs
  (knob:fetch_enable_regime always_on gives zero samples); the pipe state comes from the RVFI and
  bus monitors at the edge, so a hit proves the transition interrupted that state.
- Coverpoints:
  - cp_transition = {old class, new class} with classes on/off/inv: bins on2off, off2on, on2inv,
    inv2on, off2inv, inv2off, inv2inv{different invalid values}
  - cp_hold_len = cycles until the next change: bins one_cycle{1}, short{[2:49]}, long{[50:$]}
  - cp_pipe_state = at the edge: bins empty, id_busy{instruction in ID}, wb_load_outstanding,
    wb_store_outstanding, misaligned_mid, div_in_flight, in_wfi, in_debug, in_handler
  - cp_event_during_off = input event while not On: bins none, irq, nmi, debug_req
  - cp_resume_pc_continuous = first record after re-enable has pc_rdata == last pc_wdata: bins
    yes{1}; mismatch is a checker error
  - cp_retire_after_off = records retired after a *2off/*2inv edge: bins zero{0}, one{1},
    two{2}; ignore_bins more{[3:$]}: the pipeline holds at most ID and WB (checker error if seen;
    Zcmp micro-ops of the instruction in ID are counted as one)
  - cp_invalid_value = the invalid encoding driven: bins all_zero{4'b0000}, all_one{4'b1111},
    other_invalid{the remaining 12 values}
- Crosses:
  - cr_trans_pipe = cp_transition x cp_pipe_state: on2off_empty, on2off_id_busy,
    on2off_wb_load_outstanding, on2off_wb_store_outstanding, on2off_misaligned_mid,
    on2off_div_in_flight, on2off_in_wfi, on2off_in_debug, on2off_in_handler, on2inv_id_busy,
    on2inv_empty; ignore {off2on, inv2on, off2inv, inv2off, inv2inv}_{id_busy, wb_*,
    misaligned_mid, div_in_flight}: the pipe drains while fetch is off, so a re-enable edge sees
    an empty pipe or a WFI/debug/handler context only
  - cr_off_event = cp_transition x cp_event_during_off: on2off_irq, on2off_nmi,
    on2off_debug_req, on2inv_irq, on2inv_debug_req, on2off_none; ignore {off2on, inv2on}_*:
    events during the Off period are attributed to the edge that started it
  - cr_glitch = cp_transition x cp_hold_len: on2off_one_cycle, on2inv_one_cycle, on2off_short,
    on2off_long, off2on_short, off2on_long, inv2on_short
- Adopted (riscv-dv): none
- TP items: TP-DIT-030, TP-SEC-016, TP-RST-009, TP-RST-010, TP-RST-011, TP-RST-013, TP-RST-014,
  TP-RST-029

### CG-RST-004: gen_cg_rst_regfile
- Features: F-RST-021, F-RST-022, F-RST-023, F-DIT-015, F-SEC-005
- Sample: rvfi_valid with rvfi_trap == 0 and (rvfi_rs1_addr != 0 || rvfi_rs2_addr != 0 ||
  rvfi_rd_addr != 0), plus records reading x0 explicitly (rs1_addr == 0 with a register-reading
  format); condition: as stated; anti-vacuity: register traffic is frequent, but the interesting
  bins (unwritten read, same-cycle forward, dummy-adjacent) depend on TB state (written-set
  model, previous record, P1) so they prove the scenario rather than the record.
- Coverpoints:
  - cp_rs1_bank = rvfi_rs1_addr: bins x0{0}, x1_15{[1:15]}, x16{16}, x17_31{[17:31]}
  - cp_rs2_bank = rvfi_rs2_addr: bins x0{0}, x1_15{[1:15]}, x16{16}, x17_31{[17:31]}
  - cp_rd_bank = rvfi_rd_addr: bins none{0}, x1_15{[1:15]}, x16{16}, x17_31{[17:31]}
  - cp_read_unwritten = rs1 or rs2 register never written since the last reset (model): bins
    yes{1}, no{0}
  - cp_fwd_same_cycle = rs1 or rs2 addr == rd addr of the previous record and gap == 1: bins
    yes{1}, no{0}
  - cp_dummy_adjacent (P1) = a dummy_instr_wb_o pulse in the cycle before or after this record's
    RF write: bins yes{1}, no{0}
- Crosses:
  - cr_fwd_bank = cp_fwd_same_cycle x cp_rs1_bank: yes_x1_15, yes_x16, yes_x17_31; ignore
    yes_x0: x0 is never forwarded (raddr != 0 term); ignore no_*: not the scenario
  - cr_unwritten_bank = cp_read_unwritten x cp_rs1_bank: yes_x1_15, yes_x16, yes_x17_31; ignore
    yes_x0: x0 is not a written register; ignore no_*: not the scenario
  - cr_rd_bank_dummy = cp_rd_bank x cp_dummy_adjacent: x1_15_yes, x16_yes, x17_31_yes; ignore
    none_*: no RF write to be adjacent to
- Adopted (riscv-dv): none
- TP items: TP-DIT-016, TP-SEC-013, TP-RST-021, TP-RST-022, TP-RST-023, TP-RVFI-008

---------------------------------------------------------------------------------------------------
## RVFI
---------------------------------------------------------------------------------------------------

### CG-RVFI-001: gen_cg_rvfi_record
- Features: F-RVFI-001, F-RVFI-002, F-RVFI-003, F-RVFI-004, F-RVFI-005, F-RVFI-006, F-RVFI-007,
  F-RVFI-008, F-RVFI-009, F-RVFI-010, F-RVFI-024, F-RVFI-027, F-RVFI-028, F-RVFI-029,
  F-RVFI-034, F-RST-006, F-RST-026, F-DIT-016, F-DIT-017, F-SEC-008
- Sample: every rvfi_valid; condition: rvfi_valid; anti-vacuity: rvfi_valid is a pulse (one
  cycle per retired instruction, never continuous), and every coverpoint is a property of the
  record relative to the previous one (continuity, order step, gap), so the bins prove
  inter-record relations, not the mere existence of a record.
- Coverpoints:
  - cp_trap = rvfi_trap: bins no{0}, yes{1}
  - cp_intr = rvfi_intr: bins no{0}, yes{1}
  - cp_mode = rvfi_mode: bins u{0}, m{3}; ignore_bins other{1,2}: not implemented (checker
    error if seen)
  - cp_ixl = rvfi_ixl: bins rv32{1}; other values are checker errors
  - cp_insn_kind: bins c16{rvfi_insn[1:0] != 2'b11 && !rvfi_ext_expanded_insn_valid},
    i32{rvfi_insn[1:0] == 2'b11 && !expanded}, zcmp_uop{rvfi_ext_expanded_insn_valid}
  - cp_rd = rvfi_rd_addr: bins x0{0}, nonzero{[1:31]}
  - cp_rs1 = rvfi_rs1_addr: bins x0{0}, nonzero{[1:31]}
  - cp_rs2 = rvfi_rs2_addr: bins x0{0}, nonzero{[1:31]}
  - cp_rs3 = rvfi_rs3_addr: bins zero{0}, nonzero{[1:31]}
  - cp_pc_delta = rvfi_pc_wdata - rvfi_pc_rdata: bins plus2{2}, plus4{4}, jump_fwd{> 4, non-
    redirect record}, jump_back{negative, non-redirect record}, redirect_other{record is a trap,
    mret, dret or fence.i}
  - cp_order_step: bins one{order == prev_order + 1}, first{order == 1 after a reset}; the "gap
    or repeat" case is a checker error (no bin)
  - cp_pc_continuity = relation of pc_rdata to the previous record's pc_wdata: bins
    continuous{equal}, discontinuous_intr{rvfi_intr on this record},
    discontinuous_after_trap{previous record had rvfi_trap}, discontinuous_after_flush_redirect
    {previous record was mret/dret/fence.i}, discontinuous_debug{debug entry or dret between the
    records: rvfi_ext_debug_mode changed}; any other discontinuity is a checker error
  - cp_valid_gap = cycles since the previous rvfi_valid: bins g1{1}, g2{2}, g3_plus{[3:$]}
  - cp_intr_kind = on rvfi_intr records: bins irq{pre_mip nonzero, no nmi}, nmi{rvfi_ext_nmi},
    nmi_int{rvfi_ext_nmi_int}, none{rvfi_intr == 0}
  - cp_halt = rvfi_halt: bins zero{0}; a one is a checker error
  - cp_rd_source = source of the rd write on this record: bins alu_wb{rd_addr != 0 and the
    instruction is not a load: WB-flop source}, load_lsu{rd_addr != 0 and the instruction is a
    load: LSU return source}, none{rd_addr == 0}; a record whose class implies a write but shows
    rd_addr == 0 (or the converse) is a gen_chk_rvfi_proto error, not a bin (F-RVFI-034)
- Crosses:
  - cr_kind_trap = cp_insn_kind x cp_trap: c16_no, c16_yes, i32_no, i32_yes, zcmp_uop_no,
    zcmp_uop_yes
  - cr_rd_source_kind = cp_rd_source x cp_insn_kind: alu_wb_i32, alu_wb_c16, alu_wb_zcmp_uop
    (cm.mv* / cm.pop register writes), load_lsu_i32, load_lsu_c16, load_lsu_zcmp_uop (cm.pop
    loads), none_i32, none_c16, none_zcmp_uop (cm.push stores) (F-RVFI-034)
  - cr_mode_trap = cp_mode x cp_trap: u_yes, m_yes, u_no, m_no
  - cr_intr_cont = cp_intr x cp_pc_continuity: yes_discontinuous_intr, no_continuous,
    no_discontinuous_after_trap, no_discontinuous_after_flush_redirect, no_discontinuous_debug;
    ignore yes_{continuous, discontinuous_after_trap, discontinuous_after_flush_redirect,
    discontinuous_debug}: an interrupt entry is classified as discontinuous_intr first
  - cr_rd_kind = cp_rd x cp_insn_kind x cp_trap: x0_i32_yes, x0_c16_yes, x0_zcmp_uop_yes,
    nonzero_i32_no, nonzero_c16_no, nonzero_zcmp_uop_no, x0_i32_no, x0_c16_no; ignore
    nonzero_*_yes: rd is forced to 0 on a trap record (checker error if seen)
- Adopted (riscv-dv): none
- TP items: TP-DIT-016, TP-DIT-017, TP-DIT-018, TP-DIT-020, TP-SEC-005, TP-RST-006, TP-RST-027, TP-RVFI-001,
  TP-RVFI-002, TP-RVFI-003, TP-RVFI-004, TP-RVFI-005, TP-RVFI-006, TP-RVFI-007, TP-RVFI-008,
  TP-RVFI-009, TP-RVFI-010, TP-RVFI-011, TP-RVFI-012, TP-RVFI-013, TP-RVFI-025, TP-RVFI-026,
  TP-RVFI-027, TP-RVFI-030, TP-RVFI-031, TP-RVFI-032, TP-RVFI-036, TP-RVFI-037, TP-RVFI-038

### CG-RVFI-002: gen_cg_rvfi_mem
- Features: F-RVFI-011, F-RVFI-012, F-RVFI-013, F-RVFI-014, F-RVFI-021, F-DIT-008
- Sample: rvfi_valid where the instruction is a load or store (decoded from rvfi_insn, so trap
  records with zeroed masks are included); condition: rvfi_valid && is_load_store(rvfi_insn);
  anti-vacuity: only memory instructions sample; offset/misaligned/fault-half come from
  rvfi_mem_addr and the dbus monitor's transaction record, so a hit proves the access shape.
- Coverpoints:
  - cp_dir: bins load, store
  - cp_size = from funct3: bins byte, half, word
  - cp_offset = rvfi_mem_addr[1:0]: bins o0{0}, o1{1}, o2{2}, o3{3}
  - cp_misaligned = (half && addr[0]) || (word && addr[1:0] != 0): bins no{0}, yes{1}
  - cp_trap = rvfi_trap: bins no{0}, yes{1}
  - cp_fault_half = which bus transaction faulted (dbus monitor): bins none, first, second
  - cp_signed = lb/lh vs lbu/lhu: bins signed, unsigned, na{word or store}
  - cp_rdata_ext = upper bits of rvfi_mem_rdata for byte/half loads: bins sign_ext_ones{loaded
    sign bit 1 and upper bits all 1}, zero_ext{upper bits 0}, na{word, store, or sign bit 0 on a
    signed load}
  - cp_mask_val = the nonzero one of rmask/wmask (or 0): bins m0000{0}, m0001{1}, m0011{3},
    m1111{15}; any other value is a checker error
  - cp_rf_wr_suppress = rvfi_ext_rf_wr_suppress: bins no{0}, yes{1}
- Crosses:
  - cr_dir_size_off = cp_dir x cp_size x cp_offset: load_byte_o0, load_byte_o1, load_byte_o2,
    load_byte_o3, load_half_o0, load_half_o1, load_half_o2, load_half_o3, load_word_o0,
    load_word_o1, load_word_o2, load_word_o3, store_byte_o0, store_byte_o1, store_byte_o2,
    store_byte_o3, store_half_o0, store_half_o1, store_half_o2, store_half_o3, store_word_o0,
    store_word_o1, store_word_o2, store_word_o3 (all 24 reachable: Ibex supports misaligned
    accesses)
  - cr_trap_half = cp_dir x cp_trap x cp_fault_half: load_yes_none{aligned or first-transaction
    fault on a non-split access}, load_yes_first, load_yes_second, store_yes_none,
    store_yes_first, store_yes_second, load_no_none, store_no_none; ignore *_no_{first, second}:
    a faulting transaction always traps
  - cr_mask_trap = cp_mask_val x cp_trap: m0000_yes, m0001_no, m0011_no, m1111_no; ignore
    m0000_no: a non-trapping memory record always carries a mask; ignore {m0001, m0011,
    m1111}_yes: masks are forced to 0 on trap records
  - cr_ext = cp_size x cp_signed x cp_rdata_ext: byte_signed_sign_ext_ones,
    byte_unsigned_zero_ext, half_signed_sign_ext_ones, half_unsigned_zero_ext; ignore
    *_unsigned_sign_ext_ones and word_*: undefined
- Adopted (riscv-dv): none
- TP items: TP-DIT-009, TP-RVFI-014, TP-RVFI-015, TP-RVFI-016, TP-RVFI-017, TP-RVFI-024,
  TP-RVFI-037

### CG-RVFI-003: gen_cg_rvfi_ext
- Features: F-RVFI-016, F-RVFI-017, F-RVFI-018, F-RVFI-019, F-RVFI-020, F-RVFI-021, F-RVFI-022,
  F-RVFI-023, F-RVFI-031, F-RVFI-032, F-SEC-009, F-SEC-015, F-DIT-020
- Sample: rvfi_valid || rvfi_ext_irq_valid; condition: as stated; anti-vacuity: both are pulses;
  the collision bin requires both in one cycle (rare); the pre_mip bins require exactly one line
  set on a record (the TB drives lines so this happens), so a hit proves the field carried the
  intended value.
- Coverpoints:
  - cp_irq_valid = rvfi_ext_irq_valid: bins no{0}, yes{1}
  - cp_collision = rvfi_valid && rvfi_ext_irq_valid: bins no{0}, yes{1}
  - cp_nmi = rvfi_ext_nmi: bins no{0}, yes{1}
  - cp_nmi_int = rvfi_ext_nmi_int: bins no{0}, yes{1}
  - cp_debug_req = rvfi_ext_debug_req: bins no{0}, yes{1}
  - cp_debug_mode = rvfi_ext_debug_mode: bins no{0}, yes{1}
  - cp_rf_wr_suppress = rvfi_ext_rf_wr_suppress: bins no{0}, yes{1}
  - cp_pre_mip_line = rvfi_ext_pre_mip decoded: bins none{0}, sw{bit 3 only}, timer{bit 7 only},
    ext{bit 11 only}, fast_0 .. fast_14{bit 16+i only, i = 0..14 = width of irq_fast_i},
    multi{more than one bit}; ignore_bins other_bits{any bit outside {3, 7, 11, 30:16}}: never
    driven by the RTL (checker error if seen)
  - cp_post_mip_diff = rvfi_ext_post_mip != rvfi_ext_pre_mip: bins same{0}, changed{1}
  - cp_expanded = Zcmp position: bins none{!expanded_insn_valid}, first{valid, first micro-op of
    a sequence}, mid{valid, neither first nor last}, last{expanded_insn_last}
  - cp_trap = rvfi_trap: bins no{0}, yes{1}
  - cp_mcycle_monotonic = rvfi_ext_mcycle > previous record's value: bins yes{1}; a non-increase
    is a checker error
  - cp_hpm_index = index i in 0..MHPMCounterNum-1 whose rvfi_ext_mhpmcounters[i] is nonzero on
    this record (one sample per nonzero index): bins i0, i1, i2, i3, i4, i5, i6, i7, i8, i9
  - cp_key_valid = rvfi_ext_ic_scr_key_valid: bins zero{0}, one{1}
- Crosses:
  - cr_irq_collision = cp_irq_valid x cp_collision: yes_no, yes_yes, no_no; ignore no_yes: a
    collision implies irq_valid
  - cr_irq_kind = cp_irq_valid x cp_nmi x cp_nmi_int: yes_no_no{plain interrupt}, yes_yes_no
    {external NMI}, yes_no_yes{internal NMI}; ignore yes_yes_yes: the controller takes one NMI
    at a time (checker error if seen); ignore no_*_*: no notification
  - cr_dbg = cp_debug_req x cp_debug_mode: yes_no, yes_yes, no_yes, no_no
  - cr_expanded_trap = cp_expanded x cp_trap: first_no, mid_no, last_no, first_yes, mid_yes,
    last_yes; ignore none_*: covered by CG-RVFI-001
- Adopted (riscv-dv): none
- TP items: TP-DIT-021, TP-DIT-032, TP-SEC-006, TP-SEC-008, TP-SEC-009, TP-RST-024, TP-RST-025,
  TP-RVFI-019, TP-RVFI-020, TP-RVFI-021, TP-RVFI-022, TP-RVFI-023, TP-RVFI-024, TP-RVFI-025,
  TP-RVFI-026, TP-RVFI-034, TP-RVFI-035, TP-RVFI-037

### CG-RVFI-004: gen_cg_rvfi_trap
- Features: F-RVFI-005, F-RVFI-013, F-RVFI-015, F-RVFI-025, F-RVFI-026, F-RVFI-027, F-SEC-026,
  F-DIT-022
- Sample: rvfi_valid && rvfi_trap, plus the TB model event "ID exception requested in the same
  cycle as a WB exception" (for the B14 bins, derived from the timing of two consecutive program
  instructions); condition: as stated; anti-vacuity: trap records are a small fraction of
  records; the cause is read back from mcause in the handler (not assumed), the stage from the
  instruction class, so a hit proves a trap of that cause was recorded.
- Coverpoints:
  - cp_cause = mcause read in the handler: bins instr_access_fault{1}, illegal{2},
    breakpoint{3}, load_fault{5}, store_fault{7}, ecall_u{8}, ecall_m{11}; ignore_bins
    misaligned{0, 4, 6}: Ibex raises no misaligned exceptions in RV32 mode (checker error if
    seen)
  - cp_stage = where the exception was detected: bins id{fetch fault, illegal, breakpoint,
    ecall}, wb{load/store fault}
  - cp_coincident_wb_err = the model event: bins no{0}, yes{1}
  - cp_mode = rvfi_mode: bins u{0}, m{3}
  - cp_insn_meaningful: bins yes{not a fetch fault}, fetch_error_na{instruction access fault:
    rvfi_insn not compared}
  - cp_next_pc_is_vector = the next record's pc_rdata equals the predicted exception vector:
    bins yes{1}; mismatch is a checker error
  - cp_ebreak_kind = for ebreak instructions: bins exception{rvfi_trap == 1},
    debug_entry{rvfi_trap == 0 and the next record has debug_mode}, na{not ebreak}
  - cp_pmp_or_bus = source of an access fault: bins pmp, bus_err, na
  - cp_missing_record = (model event) the ID instruction produced no record before the handler
    and was not re-traced after it: bins no{0}, yes{1}
- Crosses:
  - cr_cause_stage = cp_cause x cp_stage: instr_access_fault_id, illegal_id, breakpoint_id,
    ecall_u_id, ecall_m_id, load_fault_wb, store_fault_wb; ignore {load_fault, store_fault}_id
    and {instr_access_fault, illegal, breakpoint, ecall_*}_wb: exceptions are detected in one
    stage only
  - cr_cause_mode = cp_cause x cp_mode: instr_access_fault_u, instr_access_fault_m, illegal_u,
    illegal_m, breakpoint_u, breakpoint_m, load_fault_u, load_fault_m, store_fault_u,
    store_fault_m, ecall_u_u, ecall_m_m; ignore ecall_u_m and ecall_m_u: the cause encodes the
    mode
  - cr_wb_coincident = cp_stage x cp_coincident_wb_err x cp_missing_record: wb_yes_yes{B14
    observed}, wb_yes_no{RTL re-traces the ID instruction}, wb_no_no, id_no_no; ignore id_yes_*:
    when the events coincide the record that survives is the WB one by construction; ignore
    *_no_yes: a missing record without a coincidence is a checker error
  - cr_lsfault_src = cp_cause x cp_pmp_or_bus: instr_access_fault_pmp,
    instr_access_fault_bus_err, load_fault_pmp, load_fault_bus_err, store_fault_pmp,
    store_fault_bus_err; ignore {illegal, breakpoint, ecall_*}_{pmp, bus_err}: not access faults
- Adopted (riscv-dv): none
- TP items: TP-DIT-024, TP-SEC-007, TP-SEC-027, TP-RVFI-005, TP-RVFI-016, TP-RVFI-018,
  TP-RVFI-028, TP-RVFI-029, TP-RVFI-030

---------------------------------------------------------------------------------------------------
## CHERI
---------------------------------------------------------------------------------------------------

### CG-CHERI-001: gen_cg_cheri_off
- Features: F-CHERI-001, F-RVFI-030, F-SEC-037, F-RST-027, F-SEC-013
- Sample: (a) rvfi_valid of an instruction with opcode 7'h5b or 7'h7b, or a CSR op whose csr
  field is in 12'hBC0..12'hBCF, (b) rvfi_valid of csrr marchid / csrr misa, (c) end of test
  (whole-run quiet bins); condition: as stated (cp_kind says which); anti-vacuity: (a) and (b)
  are directed, infrequent records; the eot bins carry run totals from gen_chk_cheriot_quiet
  (data_tag_o high count, nonzero cap-field count, store count), so "yes" proves a full run
  with stores completed with the count zero.
- Coverpoints:
  - cp_kind: bins op_cheri{opcode 0x5b}, op_auicgp{opcode 0x7b}, csr_mshwm{0xBC1},
    csr_mshwmb{0xBC2}, csr_cdbg_ctrl{0xBC4}, csr_scr_other{0xBC0, 0xBC3, 0xBC5..0xBCF},
    id_marchid, id_misa, eot
  - cp_funct3 = rvfi_insn[14:12] for op_cheri/op_auicgp: bins f0, f1, f2, f3, f4, f5, f6, f7
  - cp_funct7_class = rvfi_insn[31:25] for op_cheri: bins f7_00{0}, f7_01{1}, f7_7f{7'h7f},
    f7_other{all other values}
  - cp_trap = rvfi_trap: bins yes{1}, no{0}
  - cp_mode = rvfi_mode: bins m{3}, u{0}
  - cp_csr_op = CSR op form for csr_* kinds: bins csrrw, csrrs, csrrc, csrrwi, csrrsi, csrrci
  - cp_marchid_val (id_marchid) = rvfi_rd_wdata: bins is22{32'd22}; any other value is a
    checker error
  - cp_misa_val (id_misa) = rvfi_rd_wdata: bins expected{MXL 1, I, M, C, U, X set, E clear,
    others 0}; any other value is a checker error
  - cp_tag_zero_run (eot) = data_tag_o never 1 on a data_req_o cycle: bins yes{1}
  - cp_caps_zero_run (eot) = all rvfi cap fields and mem_is_cap zero on every record: bins yes{1}
  - cp_store_seen (eot) = at least one store transaction in the run: bins yes{1}
- Crosses:
  - cr_op_funct3 = cp_kind x cp_funct3: op_cheri_f0, op_cheri_f1, op_cheri_f2, op_cheri_f3,
    op_cheri_f4, op_cheri_f5, op_cheri_f6, op_cheri_f7, op_auicgp_f0, op_auicgp_f1,
    op_auicgp_f2, op_auicgp_f3, op_auicgp_f4, op_auicgp_f5, op_auicgp_f6, op_auicgp_f7; ignore
    csr_*/id_*/eot x f*: funct3 is a CHERIoT-opcode attribute here
  - cr_csr_op = cp_kind x cp_csr_op: csr_mshwm_csrrw, csr_mshwm_csrrs, csr_mshwm_csrrc,
    csr_mshwmb_csrrw, csr_mshwmb_csrrwi, csr_cdbg_ctrl_csrrw, csr_cdbg_ctrl_csrrsi,
    csr_scr_other_csrrw, csr_scr_other_csrrci; ignore op_*/id_*/eot x *: not CSR ops
  - cr_kind_mode_trap = cp_kind x cp_mode x cp_trap: op_cheri_m_yes, op_cheri_u_yes,
    op_auicgp_m_yes, op_auicgp_u_yes, csr_mshwm_m_yes, csr_mshwm_u_yes, csr_mshwmb_m_yes,
    csr_cdbg_ctrl_m_yes, csr_scr_other_m_yes; ignore {op_*, csr_*}_*_no: with CHERIoT off every
    such instruction traps (checker error if seen); ignore id_*_*_yes: the id CSRs are readable
    in M-mode (U-mode id reads are covered by the CSR area)
- Adopted (riscv-dv): none
- TP items: TP-SEC-017, TP-SEC-037, TP-SEC-038, TP-RST-020, TP-RST-028, TP-RVFI-033,
  TP-CHERI-001, TP-CHERI-002, TP-CHERI-003, TP-CHERI-004

---------------------------------------------------------------------------------------------------
## Counts
---------------------------------------------------------------------------------------------------

- Covergroups: 20
- Coverpoints: 178
- Coverpoint bins: 590
- Crosses: 63
- Cross bins (named required bins): 424
- Adopted (riscv-dv) bins: 0
- Bins referenced by TP items: 1014 of 1014
- TP items: 144 (expected-fail: 5)

---------------------------------------------------------------------------------------------------
## Probe candidates
---------------------------------------------------------------------------------------------------

- P1 dummy_instr_id_o / dummy_instr_wb_o (ibex_core output ports wired inside gen_dut_top to the
  register file; wrapper-internal nets, not RTL probes per rtl-arch s9) and the if_stage fcov
  nets fcov_dummy_instr_type / fcov_insert_dummy_instr (rtl/ibex_if_stage.sv:817-821, present
  unless DV_FCOV_DISABLE). Bins that cannot be sampled from the boundary or RVFI without them:
  all of CG-DIT-004 (insertion event, type, operand registers, context, back-to-back, dropped
  insertion), CG-DIT-005.cp_pattern_changed, CG-RST-004.cp_dummy_adjacent and
  cr_rd_bank_dummy, CG-RST-002.cp_inflight.dummy_in_id. Why: dummies are architecturally
  invisible and excluded from RVFI; the boundary shows only timing gaps, which cannot name the
  type or the operand registers and cannot see a dropped insertion (F-DIT-021) at all.
  Recommendation: accept P1 as coverage-only (tb-infra e); the fire-checks of TP-DIT-022 and
  TP-DIT-023 stay boundary-based with P1 as confirmation. No checker depends on it.
- rf_we_wb_o / rf_waddr_wb_o (same class of wrapper-internal net): used only inside the P1
  monitor to attribute an RF write to a dummy (waddr == 0 with dummy_instr_wb_o); not needed by
  any bin on its own.
- None of the SEC/RST/RVFI/CHERI covergroups needs an internal probe: alerts, crash_dump_o,
  double_fault_seen_o, core_busy_o, fetch_enable_i, the bus monitors and RVFI supply every
  sampled field. The B14 bins (CG-RVFI-004.cr_wb_coincident) use a TB timing model of two
  program instructions, not an RTL signal; if the model proves ambiguous the DV Lead may
  consider controller wb_exception_o as a coverage-only probe (P4 class), which is NOT requested
  here.


# 3.8 Areas REG, XIF, ADOPT: Randomization layers (regime knobs and schedule), cross-interface crosses, bins adopted from riscv-dv


Task: T-006 cross-cutting subagent. Companion: tp_xcut.md (test-plan items, knob definitions,
schedule). Build configuration `opentitan`; DUT gen_dut_top = ibex_core + ibex_register_file_ff
(README_T006_BRIEF.md). All bins here are sampled at the DUT boundary or on RVFI, except
CG-XIF-012 (probe candidate P1, see Probe candidates).

Area prefixes: REG = randomization layers (regime knobs, regime schedule, transitions);
XIF = cross-interface crosses; ADOPT = bins adopted from riscv-dv's coverage model
(vendor/google_riscv-dv/src/riscv_instr_cover_group.sv, read as reference only), counted
separately in the trace CSV (adopted = 1).

Conventions: covergroup types are `gen_cg_<area>_<name>` in `gen_fcov_pkg` (contract README;
tb-infra g.). Counts and ranges derive from ibex_pkg / RTL localparams: IC_LINE_BEATS
(rtl/ibex_pkg.sv:406), IC_NUM_WAYS (:401), IC_NUM_LINES (:405), NUM_FB (rtl/ibex_icache.sv:72),
PMPNumRegions (16, ibex_configs.yaml), irq_fast_i width ($bits(irq_fast_i) = 15,
rtl/ibex_core.sv:122), IbexMuBiOn/Off. Where a bin name carries a number (cap8, k5_plus) the
number is the brief's label for this configuration; the SV bin expression uses the parameter.

## Sampling model (boundary-derived state used by every CG-XIF and CG-REG-008)

All signals below are computed by the TB monitors from DUT ports and RVFI; none reads inside
ibex_core.

- S1 `ibus_outst`: granted instruction beats (instr_req_o & instr_gnt_i) not yet answered by
  instr_rvalid_i; range 0..NUM_FB*IC_LINE_BEATS (gen_interface_inventory.md s2).
- S2 `fetch_stalled`: ibus_outst >= 1 && !instr_rvalid_i in this cycle.
- S3 `ibus_err_rsp`: instr_rvalid_i && instr_err_i.
- S4 `dbus_outst`: granted data requests not yet answered; range 0..2 (s3).
- S5 `dbus_split`: the dbus monitor marks two consecutive requests as one misaligned pair when
  addr2 == addr1 + 4 and the byte-enable pair is one of {1110,0001}, {1100,0011}, {1000,0111},
  {1000,0001} (F-DMEM-011..016; s3 table). `split_inflight` = first half granted and second half
  not yet answered; sub-states: `split_first_outst` (second not yet granted), `split_both_outst`
  (dbus_outst == 2), `split_second_outst` (first answered, second outstanding).
- S6 `dbus_err_rsp`: data_rvalid_i && data_err_i; `err_half` in {single, split_first,
  split_second} from S5; `we` recorded at the grant of that request.
- S7 irq state from pins: `irq_pend` = irq_pending_o (|(mip & mie), not gated by mstatus.MIE,
  s6), `nmi` = irq_nm_i.
- S8 `dbg_req` = debug_req_i.
- S9 `sleeping` = (core_busy_o == IbexMuBiOff).
- S10 `fetch_en_on` = (fetch_enable_i == IbexMuBiOn); any other value is Off (s1).
- S11 `mode_q`: rvfi_mode of the most recent retirement (2'b11 = M, 2'b00 = U); `dbg_mode_q`:
  rvfi_ext_debug_mode of the most recent retirement. Events between a non-debug retirement and
  the first debug-ROM retirement are attributed to the pre-entry mode (documented approximation;
  probe P4 would remove it, see Probe candidates).
- S12 `icache_en_q`: cpuctrlsts.icache_enable tracked from retired CSR writes to 0x7C0 (reset 0,
  M-mode WARL, F-IC-012), forced 0 while dbg_mode_q (F-CSR-086). `fill_inflight` =
  icache_en_q && ibus_outst >= 1. `invalidating` = tag-write walk in progress on the
  ic_tag_write_o / ic_tag_addr_o ports (IC_NUM_LINES writes after reset or fence.i, F-IC-022/023).
- S13 `key_withheld`: an ic_scr_key_req_o pulse has been seen and ic_scr_key_valid_i is still 0.
- S14 `zcmp_inflight`: set by a retirement with rvfi_ext_expanded_insn_valid &&
  !rvfi_ext_expanded_insn_last, cleared by rvfi_ext_expanded_insn_last or by an rvfi_trap record
  inside the sequence (F-RVFI-022/023). `zcmp_kind` decoded from rvfi_ext_expanded_insn (cm.push
  / cm.pop / cm.popret / cm.popretz / cm.mvsa01 / cm.mva01s, Zcmp spec).
- S15 `fence_i_retired`: rvfi_valid && rvfi_insn[6:0] == 7'h0F && rvfi_insn[14:12] == 3'b001
  (rs1/rd/imm ignored, F-ISA-031).
- S16 `csr_write_retired(addr)`: rvfi_valid && !rvfi_trap && SYSTEM opcode with a CSR funct3 and
  a writing form (not csrrs/csrrc rs1 = x0, not csrrsi/csrrci uimm = 0; F-CSR-002). `flushing` =
  addr not in {mscratch 0x340, mepc 0x341} (F-CSR-006/007). `pmp_csr` = addr in {pmpcfg0..3
  0x3A0..0x3A3, pmpaddr0..PMPNumRegions-1 0x3B0.., mseccfg 0x747}. `irq_csr` = addr in {mie 0x304,
  mstatus 0x300, mip 0x344}.
- S17 `mret_retired`: rvfi_insn == 32'h30200073; `dret_retired`: 32'h7B200073; `wfi_retired`:
  32'h10500073 (each with !rvfi_trap).
- S18 `irq_taken_window`: cycles from the last rvfi_valid before a record with rvfi_intr == 1 to
  the vector fetch of that handler (first instr_req_o at mtvec.BASE + 4*id or + 0x7C); the
  handler record's rvfi_ext_nmi / rvfi_ext_nmi_int tell irq from NMI. `debug_entry_window`:
  likewise up to the first fetch of DmHaltAddr. "Same cycle as X" at the boundary means X's event
  falls inside the window (RVFI reports two stages late, so cycle-exactness is not available at
  the boundary; probe P4 is the exact alternative).
- S19 `redirect`: a retirement whose rvfi_pc_wdata != rvfi_pc_rdata + insn length (taken
  branch/jump, mret/dret, trap), confirmed by a non-sequential instr_addr_o request.
- S20 `dummy_inserted`: dummy_instr_id_o rising (P1 probe candidate; ibex_core port not on the
  gen_dut_top boundary) with dummy type from the RTL fcov_dummy_instr_type net.

Phase log (REG): every agent writes one record per regime phase it applies: {phase_idx, knob,
applied_value, start_cycle, start_rvfi_order, pinned}. The program-side knobs (instr_mix,
priv_regime, pmp_regime) write their record when the region marker store (TB MMIO phase-marker
register, tb-infra b.8) is observed on the data bus. CG-REG-* sample these records, never a
clock.

## Covergroups

### CG-REG-001: gen_cg_reg_imem_knobs
- Features: F-IMEM-001, F-IMEM-003, F-IMEM-004, F-IMEM-005, F-IMEM-006, F-IMEM-007, F-IMEM-008, F-IMEM-009, F-IMEM-010, F-IMEM-011, F-IMEM-012, F-IMEM-016, F-IMEM-017, F-IC-016, F-IC-019, F-IMEM-013, F-IMEM-014, F-IMEM-015, F-EXC-003
- Sample: imem agent phase-log record (TB-side phase start); condition: record.knob in the imem group; anti-vacuity: one sample per phase and knob, never per clock; the record carries the value the agent APPLIED (echoed from its driver state), so a value bin proves the agent ran that regime for a phase and a transition bin proves two consecutive phases differed.
- Coverpoints:
  - cp_imem_gnt_delay = rec.value of knob:imem_gnt_delay: bins same_cycle{gnt in the request cycle, F-IMEM-004}, short{gnt 1..3 cycles later, F-IMEM-005}, long{gnt 4..32 (10% 33..128) cycles later, F-IMEM-003/017}, random{per-request mix 40/40/20}
  - cp_imem_gnt_delay_tr = rec.value of knob:imem_gnt_delay across consecutive phases: bins same_cycle_to_short, same_cycle_to_long, same_cycle_to_random, short_to_same_cycle, short_to_long, short_to_random, long_to_same_cycle, long_to_short, long_to_random, random_to_same_cycle, random_to_short, random_to_long
  - cp_imem_rvalid_delay = rec.value of knob:imem_rvalid_delay: bins min1{exactly 1 cycle after gnt, F-IMEM-007}, short{1..3}, long{4..32 (10% 33..128), F-IMEM-008/009}, random{mix 40/40/20}
  - cp_imem_rvalid_delay_tr = knob:imem_rvalid_delay across consecutive phases: bins min1_to_short, min1_to_long, min1_to_random, short_to_min1, short_to_long, short_to_random, long_to_min1, long_to_short, long_to_random, random_to_min1, random_to_short, random_to_long
  - cp_imem_err_rate = rec.value of knob:imem_err_rate: bins none{0}, rare{~1/512 beats}, frequent{~1/20 beats, F-IMEM-011..014}
  - cp_imem_err_rate_tr = knob:imem_err_rate across consecutive phases: bins none_to_rare, none_to_frequent, rare_to_none, rare_to_frequent, frequent_to_none, frequent_to_rare
  - cp_imem_outstanding_cap = rec.value of knob:imem_outstanding_cap: bins cap1{1 beat}, cap2{IC_LINE_BEATS}, cap4{2*IC_LINE_BEATS}, cap8{NUM_FB*IC_LINE_BEATS, the RTL bound}
  - cp_imem_outstanding_cap_tr = knob:imem_outstanding_cap across consecutive phases: bins cap1_to_cap2, cap1_to_cap4, cap1_to_cap8, cap2_to_cap1, cap2_to_cap4, cap2_to_cap8, cap4_to_cap1, cap4_to_cap2, cap4_to_cap8, cap8_to_cap1, cap8_to_cap2, cap8_to_cap4
- Crosses:
  - cr_gnt_x_rvalid = cp_imem_gnt_delay x cp_imem_rvalid_delay: required bins (16): same_cycle_min1, same_cycle_short, same_cycle_long, same_cycle_random, short_min1, short_short, short_long, short_random, long_min1, long_short, long_long, long_random, random_min1, random_short, random_long, random_random
  - cr_err_x_cap = cp_imem_err_rate x cp_imem_outstanding_cap: required bins (12): none_cap1, none_cap2, none_cap4, none_cap8, rare_cap1, rare_cap2, rare_cap4, rare_cap8, frequent_cap1, frequent_cap2, frequent_cap4, frequent_cap8
- Adopted (riscv-dv): none
- TP items: TP-REG-001, TP-REG-002, TP-REG-003, TP-REG-004

### CG-REG-002: gen_cg_reg_dmem_knobs
- Features: F-DMEM-001, F-DMEM-002, F-DMEM-004, F-DMEM-005, F-DMEM-006, F-DMEM-007, F-DMEM-008, F-DMEM-010, F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-024, F-DMEM-025, F-DMEM-026, F-DMEM-028, F-DMEM-036, F-DMEM-037, F-EXC-025, F-EXC-027
- Sample: dmem agent phase-log record; condition: record.knob in the dmem group; anti-vacuity: as CG-REG-001 (applied value echoed by the driver, one sample per phase).
- Coverpoints:
  - cp_dmem_gnt_delay = rec.value of knob:dmem_gnt_delay: bins same_cycle{F-DMEM-004}, short{1..3, F-DMEM-005}, long{4..32 (10% 33..128), F-DMEM-002/024}, random{mix 40/40/20}
  - cp_dmem_gnt_delay_tr = knob:dmem_gnt_delay across consecutive phases: bins same_cycle_to_short, same_cycle_to_long, same_cycle_to_random, short_to_same_cycle, short_to_long, short_to_random, long_to_same_cycle, long_to_short, long_to_random, random_to_same_cycle, random_to_short, random_to_long
  - cp_dmem_rvalid_delay = rec.value of knob:dmem_rvalid_delay: bins min1{F-DMEM-006}, short{1..3}, long{4..32 (10% 33..128), F-DMEM-025/026/030}, random{mix}
  - cp_dmem_rvalid_delay_tr = knob:dmem_rvalid_delay across consecutive phases: bins min1_to_short, min1_to_long, min1_to_random, short_to_min1, short_to_long, short_to_random, long_to_min1, long_to_short, long_to_random, random_to_min1, random_to_short, random_to_long
  - cp_dmem_err_rate = rec.value of knob:dmem_err_rate: bins none{0}, rare{~1/512 responses}, frequent{~1/20 responses, F-DMEM-021..023/036/037}
  - cp_dmem_err_rate_tr = knob:dmem_err_rate across consecutive phases: bins none_to_rare, none_to_frequent, rare_to_none, rare_to_frequent, frequent_to_none, frequent_to_rare
- Crosses:
  - cr_gnt_x_rvalid = cp_dmem_gnt_delay x cp_dmem_rvalid_delay: required bins (16): same_cycle_min1, same_cycle_short, same_cycle_long, same_cycle_random, short_min1, short_short, short_long, short_random, long_min1, long_short, long_long, long_random, random_min1, random_short, random_long, random_random
  - cr_err_x_rvalid = cp_dmem_err_rate x cp_dmem_rvalid_delay: required bins (12): none_min1, none_short, none_long, none_random, rare_min1, rare_short, rare_long, rare_random, frequent_min1, frequent_short, frequent_long, frequent_random
- Adopted (riscv-dv): none
- TP items: TP-REG-005, TP-REG-006, TP-REG-007

### CG-REG-003: gen_cg_reg_irq_knobs
- Features: F-IRQ-001, F-IRQ-002, F-IRQ-009, F-IRQ-010, F-IRQ-011, F-IRQ-025, F-IRQ-026, F-IRQ-027, F-IRQ-030, F-IRQ-034, F-IRQ-052, F-IRQ-061, F-IRQ-062, F-IRQ-063, F-EXC-059
- Sample: irq driver phase-log record; condition: record.knob in the irq group; anti-vacuity: one sample per phase; the driver echoes the regime it is executing (event generator state), not the schedule.
- Coverpoints:
  - cp_irq_regime = rec.value of knob:irq_regime: bins quiet{no new assertion events}, sparse{geometric inter-arrival, mean ~2000 cycles, <= 1 event outstanding}, storm{mean ~20 cycles, overlapping events, immediate re-assert after ack, F-IRQ-011/027, F-EXC-059}
  - cp_irq_regime_tr = knob:irq_regime across consecutive phases: bins quiet_to_sparse, quiet_to_storm, sparse_to_quiet, sparse_to_storm, storm_to_quiet, storm_to_sparse
  - cp_irq_line_mix = rec.value of knob:irq_line_mix: bins single{one line per event from the 3 + $bits(irq_fast_i) maskable lines}, multi{2..k lines per event, F-IRQ-009/010}, fast_only{irq_fast_i lines only, F-IRQ-010/061/062}, with_nmi{multi plus irq_nm_i at 25%, F-IRQ-030/034}
  - cp_irq_line_mix_tr = knob:irq_line_mix across consecutive phases: bins single_to_multi, single_to_fast_only, single_to_with_nmi, multi_to_single, multi_to_fast_only, multi_to_with_nmi, fast_only_to_single, fast_only_to_multi, fast_only_to_with_nmi, with_nmi_to_single, with_nmi_to_multi, with_nmi_to_fast_only
  - cp_irq_hold = rec.value of knob:irq_hold: bins until_taken{level held until rvfi_intr then released within 0..3 cycles}, through_handler{level held until the handler's MMIO ack store, F-IRQ-027/052}, pulse{1..3 cycle pulse regardless of taking, may be dropped, F-IRQ-025/026}
  - cp_irq_hold_tr = knob:irq_hold across consecutive phases: bins until_taken_to_through_handler, until_taken_to_pulse, through_handler_to_until_taken, through_handler_to_pulse, pulse_to_until_taken, pulse_to_through_handler
- Crosses:
  - cr_regime_x_mix = cp_irq_regime x cp_irq_line_mix: required bins (8): sparse_single, sparse_multi, sparse_fast_only, sparse_with_nmi, storm_single, storm_multi, storm_fast_only, storm_with_nmi; ignore quiet_single, quiet_multi, quiet_fast_only, quiet_with_nmi: a quiet phase generates no assertion events, so the line mix is inert and the cross bin would be vacuous
  - cr_regime_x_hold = cp_irq_regime x cp_irq_hold: required bins (6): sparse_until_taken, sparse_through_handler, sparse_pulse, storm_until_taken, storm_through_handler, storm_pulse; ignore quiet_until_taken, quiet_through_handler, quiet_pulse: no events in a quiet phase, hold policy inert
- Adopted (riscv-dv): none
- TP items: TP-REG-008, TP-REG-009, TP-REG-010

### CG-REG-004: gen_cg_reg_dbg_fe_knobs
- Features: F-DBG-001, F-DBG-005, F-DBG-006, F-DBG-007, F-DBG-008, F-DBG-009, F-IMEM-022, F-IMEM-023, F-IMEM-024, F-IMEM-025, F-RST-010, F-RST-014, F-RST-015, F-SEC-012
- Sample: debug_req driver and fetch_enable driver phase-log records; condition: record.knob in {debug_req_regime, fetch_enable_regime}; anti-vacuity: one sample per phase, driver-echoed value.
- Coverpoints:
  - cp_debug_req_regime = rec.value of knob:debug_req_regime: bins none{never asserted}, sparse{mean ~5000 cycles, level held until rvfi_ext_debug_mode then released; 50% kept high through dret, F-DBG-007}, storm{mean ~100 cycles incl. 20% one-cycle pulses, F-DBG-005/006}
  - cp_debug_req_regime_tr = knob:debug_req_regime across consecutive phases: bins none_to_sparse, none_to_storm, sparse_to_none, sparse_to_storm, storm_to_none, storm_to_sparse
  - cp_fetch_enable_regime = rec.value of knob:fetch_enable_regime: bins always_on{IbexMuBiOn all phase}, toggling{Off windows 1..200 cycles, mean gap ~1000 cycles; Off encoding 80% IbexMuBiOff / 20% invalid MuBi, never X, F-IMEM-023, F-SEC-012}
  - cp_fetch_enable_regime_tr = knob:fetch_enable_regime across consecutive phases: bins always_on_to_toggling, toggling_to_always_on
- Crosses:
  - cr_dbg_x_fe = cp_debug_req_regime x cp_fetch_enable_regime: required bins (6): none_always_on, none_toggling, sparse_always_on, sparse_toggling, storm_always_on, storm_toggling
- Adopted (riscv-dv): none
- TP items: TP-REG-011, TP-REG-012

### CG-REG-005: gen_cg_reg_icache_knobs
- Features: F-IC-008, F-IC-009, F-IC-010, F-IC-023, F-IC-024, F-IC-025, F-IC-029, F-IC-030, F-IC-031, F-IC-033, F-IC-035, F-SEC-001, F-SEC-021
- Sample: icache RAM model and scramble-key responder phase-log records; condition: record.knob in {icache_ecc_err_rate, scr_key_delay}; anti-vacuity: one sample per phase, model-echoed value; the effect bins (alerts, invalidations) belong to the IC area, this group only proves the regime ran.
- Coverpoints:
  - cp_icache_ecc_err_rate = rec.value of knob:icache_ecc_err_rate: bins none{0}, rare{~1/2000 lookups; tag/data 50/50; 1-bit/2-bit 50/50; way random, F-IC-030/031/033}, frequent{~1/50 lookups, same mix}
  - cp_icache_ecc_err_rate_tr = knob:icache_ecc_err_rate across consecutive phases: bins none_to_rare, none_to_frequent, rare_to_none, rare_to_frequent, frequent_to_none, frequent_to_rare
  - cp_scr_key_delay = rec.value of knob:scr_key_delay: bins immediate{ic_scr_key_valid_i low for 1 cycle after the request, F-IC-008}, delayed{low 2..200 cycles}, withheld_then_valid{low 201..2000 cycles, long enough for a second fence.i and a WFI, F-IC-024/029/010}
  - cp_scr_key_delay_tr = knob:scr_key_delay across consecutive phases: bins immediate_to_delayed, immediate_to_withheld_then_valid, delayed_to_immediate, delayed_to_withheld_then_valid, withheld_then_valid_to_immediate, withheld_then_valid_to_delayed
- Crosses:
  - cr_ecc_x_key = cp_icache_ecc_err_rate x cp_scr_key_delay: required bins (9): none_immediate, none_delayed, none_withheld_then_valid, rare_immediate, rare_delayed, rare_withheld_then_valid, frequent_immediate, frequent_delayed, frequent_withheld_then_valid
- Adopted (riscv-dv): none
- TP items: TP-REG-013, TP-REG-014

### CG-REG-006: gen_cg_reg_program_knobs
- Features: F-ISA-001, F-ISA-023, F-MUL-001, F-CMP-001, F-CMP-039, F-BIT-001, F-CSR-001, F-DMEM-015, F-PRV-001, F-PRV-002, F-PRV-006, F-PMP-006, F-PMP-021, F-PMP-023, F-PMP-045, F-PMP-053, F-PMP-056, F-PRV-003, F-IRQ-008
- Sample: program-side phase-log record, written when the region marker store (TB MMIO phase-marker register) is observed on the data bus with the region tuple in its data; condition: marker store observed; anti-vacuity: one sample per region; the marker is emitted by the generated program at the region boundary, so a value bin proves the program actually entered a region generated with that knob value.
- Coverpoints:
  - cp_instr_mix = rec.value of knob:instr_mix: bins isa_only{RV32I only}, m_heavy{~40% mul/div}, compressed_heavy{~60% Zca/Zcb/Zcmp incl. cm.push/pop}, bitmanip_heavy{~40% legal RV32BOTEarlGrey}, csr_heavy{~30% CSR ops incl. 2% illegal accesses}, ls_heavy{~50% loads/stores, 30% misaligned}, branch_heavy{~40% branches/jumps, short loops}, mixed{flat weights}
  - cp_instr_mix_tr = knob:instr_mix across consecutive regions: bins isa_only_to_m_heavy, isa_only_to_compressed_heavy, isa_only_to_bitmanip_heavy, isa_only_to_csr_heavy, isa_only_to_ls_heavy, isa_only_to_branch_heavy, isa_only_to_mixed, m_heavy_to_isa_only, m_heavy_to_compressed_heavy, m_heavy_to_bitmanip_heavy, m_heavy_to_csr_heavy, m_heavy_to_ls_heavy, m_heavy_to_branch_heavy, m_heavy_to_mixed, compressed_heavy_to_isa_only, compressed_heavy_to_m_heavy, compressed_heavy_to_bitmanip_heavy, compressed_heavy_to_csr_heavy, compressed_heavy_to_ls_heavy, compressed_heavy_to_branch_heavy, compressed_heavy_to_mixed, bitmanip_heavy_to_isa_only, bitmanip_heavy_to_m_heavy, bitmanip_heavy_to_compressed_heavy, bitmanip_heavy_to_csr_heavy, bitmanip_heavy_to_ls_heavy, bitmanip_heavy_to_branch_heavy, bitmanip_heavy_to_mixed, csr_heavy_to_isa_only, csr_heavy_to_m_heavy, csr_heavy_to_compressed_heavy, csr_heavy_to_bitmanip_heavy, csr_heavy_to_ls_heavy, csr_heavy_to_branch_heavy, csr_heavy_to_mixed, ls_heavy_to_isa_only, ls_heavy_to_m_heavy, ls_heavy_to_compressed_heavy, ls_heavy_to_bitmanip_heavy, ls_heavy_to_csr_heavy, ls_heavy_to_branch_heavy, ls_heavy_to_mixed, branch_heavy_to_isa_only, branch_heavy_to_m_heavy, branch_heavy_to_compressed_heavy, branch_heavy_to_bitmanip_heavy, branch_heavy_to_csr_heavy, branch_heavy_to_ls_heavy, branch_heavy_to_mixed, mixed_to_isa_only, mixed_to_m_heavy, mixed_to_compressed_heavy, mixed_to_bitmanip_heavy, mixed_to_csr_heavy, mixed_to_ls_heavy, mixed_to_branch_heavy
  - cp_priv_regime = rec.value of knob:priv_regime: bins m_only{all M}, u_heavy{~70% of instructions in U-mode}, alternating{mode switch every 10..100 instructions via mret/ecall}
  - cp_priv_regime_tr = knob:priv_regime across consecutive regions: bins m_only_to_u_heavy, m_only_to_alternating, u_heavy_to_m_only, u_heavy_to_alternating, alternating_to_m_only, alternating_to_u_heavy
  - cp_pmp_regime = rec.value of knob:pmp_regime: bins off{all A=OFF, mseccfg=0}, sparse{2..4 of PMPNumRegions regions, TOR/NAPOT}, dense{all PMPNumRegions regions, NA4/NAPOT/TOR, <= 25% locked, overlapping}, mml_on{mseccfg.MML=1 (+MMWP 50%, RLB 50%) with a dense MML-legal set}
  - cp_pmp_regime_tr = knob:pmp_regime across consecutive regions: bins off_to_sparse, off_to_dense, off_to_mml_on, sparse_to_off, sparse_to_dense, sparse_to_mml_on, dense_to_off, dense_to_sparse, dense_to_mml_on, mml_on_to_off, mml_on_to_sparse, mml_on_to_dense; ignore_bins mml_on_to_off, mml_on_to_sparse, mml_on_to_dense: mseccfg.MML is sticky once set (F-PMP-023), so a region after mml_on inherits MML=1 within one reset epoch; the schedule never spans a reset
- Crosses:
  - cr_priv_x_pmp = cp_priv_regime x cp_pmp_regime: required bins (12): m_only_off, m_only_sparse, m_only_dense, m_only_mml_on, u_heavy_off, u_heavy_sparse, u_heavy_dense, u_heavy_mml_on, alternating_off, alternating_sparse, alternating_dense, alternating_mml_on
  - cr_mix_x_priv = cp_instr_mix x cp_priv_regime: required bins (24): isa_only_m_only, isa_only_u_heavy, isa_only_alternating, m_heavy_m_only, m_heavy_u_heavy, m_heavy_alternating, compressed_heavy_m_only, compressed_heavy_u_heavy, compressed_heavy_alternating, bitmanip_heavy_m_only, bitmanip_heavy_u_heavy, bitmanip_heavy_alternating, csr_heavy_m_only, csr_heavy_u_heavy, csr_heavy_alternating, ls_heavy_m_only, ls_heavy_u_heavy, ls_heavy_alternating, branch_heavy_m_only, branch_heavy_u_heavy, branch_heavy_alternating, mixed_m_only, mixed_u_heavy, mixed_alternating
- Adopted (riscv-dv): none
- TP items: TP-REG-015, TP-REG-016, TP-REG-017

### CG-REG-007: gen_cg_reg_schedule
- Features: F-IMEM-001, F-DMEM-001, F-IRQ-001, F-DBG-001, F-IC-008, F-IMEM-022, F-ISA-001, F-PRV-001, F-PMP-006
- Sample: schedule generator banner at time 0 (phase_count, pinned_count) and every TB-side / program-side phase-start record (duration class, knobs changed, phase index); condition: record present; anti-vacuity: the banner is one sample per run and phase records are one per phase; a hit proves the schedule generator produced and the agents consumed that many phases (the phase log, not the plusarg, is sampled). Bins map to the umbrella feature of each interface the regimes stress (DV_prompt Section 6 layer 3 is a stimulus rule, not a DUT feature; see Open questions in tp_xcut.md).
- Coverpoints:
  - cp_phase_count = number of phases observed in the phase log at end of run: bins k1{1}, k2{2}, k3_4{3..4}, k5_plus{>= 5}
  - cp_duration_class = TB-side phase duration class: bins short{500..2000 cycles}, medium{2001..20000 cycles}, long{20001..100000 cycles}
  - cp_region_duration_class = program-side region duration class: bins short{100..500 retired instructions}, medium{501..5000}, long{5001..20000}
  - cp_knobs_changed = TB-side knobs whose applied value differs from the previous phase (phase 0 excluded): bins one{1}, two_three{2..3}, four_plus{>= 4}
  - cp_pinned_count = knobs pinned by +gen_knob_<name>= in this run (banner): bins none{0}, one{1}, several{2..16}, all{17}
  - cp_phase_idx = position of the phase in the schedule: bins first{0}, middle{1..K-2}, last{K-1}
- Crosses:
  - cr_count_x_dur = cp_phase_count x cp_duration_class: required bins (12): k1_short, k1_medium, k1_long, k2_short, k2_medium, k2_long, k3_4_short, k3_4_medium, k3_4_long, k5_plus_short, k5_plus_medium, k5_plus_long
  - cr_pinned_x_changed = cp_pinned_count x cp_knobs_changed: required bins (9): none_one, none_two_three, none_four_plus, one_one, one_two_three, one_four_plus, several_one, several_two_three, several_four_plus; ignore all_one, all_two_three, all_four_plus: with every knob pinned no TB-side knob can change at a boundary, so cp_knobs_changed is never sampled
- Adopted (riscv-dv): none
- TP items: TP-REG-018, TP-REG-019

### CG-REG-008: gen_cg_reg_inflight_transition
- Features: F-IMEM-008, F-IMEM-016, F-DMEM-008, F-DMEM-030, F-IRQ-016, F-IRQ-020, F-IRQ-025, F-IRQ-045, F-DBG-007, F-DBG-010, F-DBG-056, F-CMP-056, F-CMP-057, F-RST-017, F-IC-029, F-IMEM-009, F-DMEM-010, F-IRQ-027, F-DBG-027, F-DBG-030
- Sample: TB-side phase boundary (and the program-side marker for group program); one sample per (knob group whose value changed, in-flight flag true at the boundary cycle); flags from S1, S4, S7, S9, S11, S14; condition: at least one knob of the group changed; anti-vacuity: the boundary is a scheduled TB event and the flags come from monitors, so a hit proves the regime changed while the DUT was in that state; `none` is sampled only when no flag is true.
- Coverpoints:
  - cp_knob_group = group of the changed knob: bins imem{imem_*}, dmem{dmem_*}, irq{irq_*}, dbg_fe{debug_req_regime, fetch_enable_regime}, icache{icache_ecc_err_rate, scr_key_delay}, program{instr_mix, priv_regime, pmp_regime}
  - cp_knob_changed = name of the changed knob: bins imem_gnt_delay, imem_rvalid_delay, imem_err_rate, imem_outstanding_cap, dmem_gnt_delay, dmem_rvalid_delay, dmem_err_rate, irq_regime, irq_line_mix, irq_hold, debug_req_regime, fetch_enable_regime, icache_ecc_err_rate, scr_key_delay, instr_mix, priv_regime, pmp_regime
  - cp_inflight_event = DUT state at the boundary cycle: bins fetch_outstanding{S1 >= 1}, data_outstanding{S4 >= 1}, irq_pending{irq_pending_o || irq_nm_i, no handler entered yet}, in_wfi{S9 sleeping}, in_debug{dbg_mode_q}, mid_zcmp{S14}, none{no flag true}
- Crosses:
  - cr_group_x_inflight = cp_knob_group x cp_inflight_event: required bins (31): imem_fetch_outstanding, imem_data_outstanding, imem_irq_pending, imem_in_wfi, imem_in_debug, imem_mid_zcmp, dmem_fetch_outstanding, dmem_data_outstanding, dmem_irq_pending, dmem_in_wfi, dmem_in_debug, dmem_mid_zcmp, irq_fetch_outstanding, irq_data_outstanding, irq_irq_pending, irq_in_wfi, irq_in_debug, irq_mid_zcmp, dbg_fe_fetch_outstanding, dbg_fe_data_outstanding, dbg_fe_irq_pending, dbg_fe_in_wfi, dbg_fe_in_debug, dbg_fe_mid_zcmp, icache_fetch_outstanding, icache_data_outstanding, icache_irq_pending, icache_in_wfi, icache_in_debug, icache_mid_zcmp, program_irq_pending; ignore imem_none, dmem_none, irq_none, dbg_fe_none, icache_none, program_none, program_fetch_outstanding, program_data_outstanding, program_in_wfi, program_in_debug, program_mid_zcmp: `none` is not an in-flight event; the program-side boundary is the retirement of the marker store, at which a fetch is almost always outstanding and the marker's own data access is outstanding (vacuous), the core is executing (never in WFI), the marker is program code (never in debug mode or inside a Zcmp sequence)
  - cr_knob_x_inflight = cp_knob_changed x cp_inflight_event: required bins (23): imem_gnt_delay_fetch_outstanding, imem_rvalid_delay_fetch_outstanding, imem_err_rate_fetch_outstanding, imem_outstanding_cap_fetch_outstanding, dmem_gnt_delay_data_outstanding, dmem_rvalid_delay_data_outstanding, dmem_err_rate_data_outstanding, irq_regime_irq_pending, irq_line_mix_irq_pending, irq_hold_irq_pending, irq_regime_in_wfi, irq_line_mix_in_wfi, debug_req_regime_in_wfi, fetch_enable_regime_in_wfi, debug_req_regime_in_debug, irq_regime_in_debug, imem_err_rate_in_debug, dmem_err_rate_in_debug, dmem_gnt_delay_mid_zcmp, dmem_rvalid_delay_mid_zcmp, dmem_err_rate_mid_zcmp, irq_regime_mid_zcmp, debug_req_regime_mid_zcmp; ignore all other 96 combinations: the knob does not act on the completion of that in-flight event (e.g. a scramble-key regime change while a data access is outstanding); the timing of such changes is covered at group level by cr_group_x_inflight
- Adopted (riscv-dv): none
- TP items: TP-REG-018, TP-REG-020, TP-REG-021, TP-REG-022, TP-REG-023, TP-REG-024, TP-REG-025

### CG-XIF-001: gen_cg_xif_data_err_x_fetch_irq
- Features: F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-030, F-DMEM-036, F-DMEM-037, F-DMEM-038, F-IMEM-008, F-IRQ-017, F-IRQ-022, F-DBG-003, F-EXC-025, F-EXC-027, F-EXC-069
- Sample: S6 dbus_err_rsp (data_rvalid_i && data_err_i); condition: error response on the data bus; anti-vacuity: error responses exist only at the dmem_err_rate injection rate (zero under `none`), so a hit proves an errored data response returned while the crossed fetch/interrupt state held in the same cycle.
- Coverpoints:
  - cp_fetch_state = instruction bus state in the error cycle: bins stalled{S2: >= 1 fetch outstanding and no rvalid}, rsp_same_cycle{ibus_outst >= 1 && instr_rvalid_i}, idle{ibus_outst == 0}
  - cp_async = asynchronous requests in the error cycle: bins none{none of irq_pending_o, irq_nm_i, debug_req_i}, irq_pending{irq_pending_o only}, nmi{irq_nm_i only}, debug_req{debug_req_i only}, multiple{>= 2 of the three}
  - cp_err_half = S6 err_half: bins single{aligned or non-split access}, split_first{first half of a misaligned pair, F-DMEM-021}, split_second{second half, F-DMEM-022}
  - cp_we = data_we_o at the grant of the errored request: bins load{0}, store{1}
- Crosses:
  - cr_fetch_x_async = cp_fetch_state x cp_async: required bins (15): stalled_none, stalled_irq_pending, stalled_nmi, stalled_debug_req, stalled_multiple, rsp_same_cycle_none, rsp_same_cycle_irq_pending, rsp_same_cycle_nmi, rsp_same_cycle_debug_req, rsp_same_cycle_multiple, idle_none, idle_irq_pending, idle_nmi, idle_debug_req, idle_multiple
  - cr_half_x_async = cp_err_half x cp_async: required bins (15): single_none, single_irq_pending, single_nmi, single_debug_req, single_multiple, split_first_none, split_first_irq_pending, split_first_nmi, split_first_debug_req, split_first_multiple, split_second_none, split_second_irq_pending, split_second_nmi, split_second_debug_req, split_second_multiple
- Adopted (riscv-dv): none
- TP items: TP-XIF-001

### CG-XIF-002: gen_cg_xif_fetch_err_x_async
- Features: F-IMEM-011, F-IMEM-012, F-IMEM-013, F-IMEM-014, F-EXC-003, F-EXC-005, F-EXC-006, F-IRQ-021, F-DBG-030, F-FE-015, F-FE-023, F-BTALU-010
- Sample: S3 ibus_err_rsp (instr_rvalid_i && instr_err_i); condition: error beat on the instruction bus; anti-vacuity: error beats exist only at the imem_err_rate injection rate; a hit proves an errored fetch beat returned while the crossed state held.
- Coverpoints:
  - cp_async = asynchronous requests in the beat cycle: bins none, irq_pending{irq_pending_o only}, nmi{irq_nm_i only}, debug_req{debug_req_i only}, multiple{>= 2}
  - cp_window = trap-entry window the beat falls in (S18): bins irq_taken_window{beat inside an interrupt/NMI entry window}, debug_entry_window{beat inside a debug entry window}, normal{neither}
  - cp_consumed = fate of the errored word: bins executed_trap{a later rvfi_trap record with instruction-access-fault semantics has rvfi_pc_rdata == beat address or beat address - 2 (err_plus2, F-IMEM-013)}, discarded{no such record before the next redirect, F-IMEM-012}
  - cp_outst_at_err = S1 in the beat cycle (including the beat): bins one{1}, few{2..2*IC_LINE_BEATS}, many{2*IC_LINE_BEATS+1..NUM_FB*IC_LINE_BEATS}
- Crosses:
  - cr_async_x_window = cp_async x cp_window: required bins (15): none_irq_taken_window, none_debug_entry_window, none_normal, irq_pending_irq_taken_window, irq_pending_debug_entry_window, irq_pending_normal, nmi_irq_taken_window, nmi_debug_entry_window, nmi_normal, debug_req_irq_taken_window, debug_req_debug_entry_window, debug_req_normal, multiple_irq_taken_window, multiple_debug_entry_window, multiple_normal
  - cr_consumed_x_async = cp_consumed x cp_async: required bins (10): executed_trap_none, executed_trap_irq_pending, executed_trap_nmi, executed_trap_debug_req, executed_trap_multiple, discarded_none, discarded_irq_pending, discarded_nmi, discarded_debug_req, discarded_multiple
- Adopted (riscv-dv): none
- TP items: TP-XIF-005

### CG-XIF-003: gen_cg_xif_data_outst_x_async
- Features: F-DMEM-030, F-DMEM-031, F-DMEM-021, F-DMEM-022, F-DMEM-025, F-DMEM-026, F-DBG-003, F-IRQ-017, F-IRQ-018, F-IRQ-030, F-IRQ-040, F-IRQ-041, F-EXC-035, F-EXC-069, F-SEC-015, F-SEC-016, F-DBG-004, F-DBG-036, F-IRQ-022, F-IRQ-035
- Sample: rising edge of an asynchronous request (irq_pending_o 0->1, irq_nm_i 0->1, debug_req_i 0->1, or an alert_major_bus_o pulse coincident with data_rvalid_i = internal-NMI arming, F-IRQ-040) while S4 dbus_outst >= 1 (counted before the response of that cycle is retired); condition: dbus_outst >= 1 at the edge; anti-vacuity: async edges are driver events and dbus_outst >= 1 holds only inside the slow-response windows of the dmem knobs; a hit proves the request arrived with a data access in flight.
- Coverpoints:
  - cp_async_src = which request rose: bins irq_maskable, nmi_ext{irq_nm_i}, nmi_int{integrity error on a data response, F-IRQ-040}, debug_req
  - cp_dbus_state = S5 state at the edge: bins single_outst{one non-split access outstanding}, split_first_outst, split_both_outst, split_second_outst
  - cp_rsp_outcome = the outstanding access finally returns: bins ok{data_err_i = 0}, err{data_err_i = 1, exception wins over the async request, F-IRQ-022/F-DBG-003}
  - cp_we = type of the outstanding access: bins load, store
- Crosses:
  - cr_src_x_state = cp_async_src x cp_dbus_state: required bins (15): irq_maskable_single_outst, irq_maskable_split_first_outst, irq_maskable_split_both_outst, irq_maskable_split_second_outst, nmi_ext_single_outst, nmi_ext_split_first_outst, nmi_ext_split_both_outst, nmi_ext_split_second_outst, nmi_int_split_first_outst, nmi_int_split_both_outst, nmi_int_split_second_outst, debug_req_single_outst, debug_req_split_first_outst, debug_req_split_both_outst, debug_req_split_second_outst; ignore nmi_int_single_outst: the integrity error arrives on the response that completes the only outstanding access, so no other access is in flight at that edge
  - cr_src_x_outcome_x_we = cp_async_src x cp_rsp_outcome x cp_we: required bins (16): irq_maskable_ok_load, irq_maskable_ok_store, irq_maskable_err_load, irq_maskable_err_store, nmi_ext_ok_load, nmi_ext_ok_store, nmi_ext_err_load, nmi_ext_err_store, nmi_int_ok_load, nmi_int_ok_store, nmi_int_err_load, nmi_int_err_store, debug_req_ok_load, debug_req_ok_store, debug_req_err_load, debug_req_err_store
- Adopted (riscv-dv): none
- TP items: TP-XIF-002, TP-XIF-003, TP-XIF-008, TP-XIF-009

### CG-XIF-004: gen_cg_xif_wfi_wake
- Features: F-IRQ-045, F-IRQ-046, F-IRQ-047, F-IRQ-048, F-IRQ-049, F-IRQ-050, F-IRQ-051, F-IRQ-054, F-IRQ-064, F-DMEM-031, F-IC-029, F-RST-015, F-RST-017, F-PRV-016, F-PRV-017, F-PRV-018, F-PRV-019, F-PRV-020, F-FE-021, F-IMEM-021, F-DBG-009, F-DBG-044
- Sample: the wake event after a WFI retirement (S17): core_busy_o Off->On, or, when the core never reached Off, the first retirement after the WFI; condition: a wfi_retired since the previous sample; anti-vacuity: WFIs are program events (instr_mix all values include them at low weight); a hit proves the sleep/wake path completed with the crossed wake source and pending-transaction state.
- Coverpoints:
  - cp_slept = core_busy_o reached IbexMuBiOff: bins slept{yes}, no_sleep{never Off: wake condition already true (F-IRQ-048), WFI in debug/step (F-IRQ-051), or TW trap}
  - cp_wake_src = highest-priority source high at the wake edge (debug_req > nmi > irq): bins irq_maskable{irq_pending_o}, nmi{irq_nm_i}, debug_req{debug_req_i}, none_needed{no_sleep with no source high}
  - cp_wake_result = first record after the WFI: bins trap_taken{rvfi_intr = 1}, resumed_no_trap{rvfi_pc_rdata == WFI pc + 4 and rvfi_intr = 0, F-IRQ-046/F-PRV-019}, debug_entered{rvfi_ext_debug_mode = 1 and the WFI record was not}, illegal_trap{the WFI record itself has rvfi_trap = 1: U-mode with TW = 1, F-PRV-016}
  - cp_pending_at_wfi = transactions outstanding when the WFI retired: bins none, fetch_outst{S1 >= 1, F-RST-017}, data_outst{S4 >= 1, F-DMEM-031/F-IRQ-054}, icache_busy{S12 invalidating or S13 key_withheld, F-IC-029}
  - cp_mode_at_wfi = rvfi_mode of the WFI record: bins m, u
- Crosses:
  - cr_src_x_result = cp_wake_src x cp_wake_result: required bins (12): irq_maskable_trap_taken, irq_maskable_resumed_no_trap, irq_maskable_debug_entered, nmi_trap_taken, nmi_resumed_no_trap, nmi_debug_entered, debug_req_trap_taken, debug_req_resumed_no_trap, debug_req_debug_entered, none_needed_trap_taken, none_needed_resumed_no_trap, none_needed_debug_entered; ignore none_needed_illegal_trap, irq_maskable_illegal_trap, nmi_illegal_trap, debug_req_illegal_trap: the TW illegal-instruction trap is raised on the WFI itself before any sleep or wake, so no wake source is involved (single bin illegal_trap is kept in cr_mode_x_result)
  - cr_pending_x_src = cp_pending_at_wfi x cp_wake_src: required bins (16): none_irq_maskable, none_nmi, none_debug_req, none_none_needed, fetch_outst_irq_maskable, fetch_outst_nmi, fetch_outst_debug_req, fetch_outst_none_needed, data_outst_irq_maskable, data_outst_nmi, data_outst_debug_req, data_outst_none_needed, icache_busy_irq_maskable, icache_busy_nmi, icache_busy_debug_req, icache_busy_none_needed
  - cr_mode_x_result = cp_mode_at_wfi x cp_wake_result: required bins (7): m_trap_taken, m_resumed_no_trap, m_debug_entered, u_trap_taken, u_resumed_no_trap, u_debug_entered, u_illegal_trap; ignore m_illegal_trap: mstatus.TW does not affect M-mode WFI (F-PRV-017)
- Adopted (riscv-dv): none
- TP items: TP-XIF-004

### CG-XIF-005: gen_cg_xif_icache_fill_x_event
- Features: F-IC-010, F-IC-020, F-IC-021, F-IC-023, F-IC-024, F-IC-025, F-IC-026, F-IC-027, F-IC-029, F-IC-030, F-IC-031, F-IC-036, F-IC-037, F-IC-041, F-IMEM-015, F-IMEM-016, F-IMEM-017, F-ISA-030, F-SEC-021, F-IMEM-012, F-IC-011, F-IC-028, F-IC-032, F-IC-033, F-IC-035, F-SEC-001
- Sample: one of the events below occurring while S12 fill_inflight or S13 key_withheld; condition: (fill_inflight || key_withheld) && event; anti-vacuity: fill_inflight requires the cache to be enabled by the program and beats to be outstanding; events are program (fence.i, redirect, icache_disable) or agent (bus error, ECC injection, key) events, so a hit proves the event coincided with a fill in flight.
- Coverpoints:
  - cp_event = event type: bins fence_i{S15}, redirect{S19 taken branch/jump/trap retirement}, bus_err_beat{S3 on a fill beat}, ecc_inject{RAM model injects on a lookup}, icache_disable{retired CSR write clearing cpuctrlsts.icache_enable, F-IC-027/041}, key_req{ic_scr_key_req_o pulse}
  - cp_fill_state = S1 at the event: bins one_beat_outst{1}, two_to_line{2..IC_LINE_BEATS}, multi_line{IC_LINE_BEATS+1..NUM_FB*IC_LINE_BEATS}
  - cp_key = scramble key state: bins valid{ic_scr_key_valid_i = 1}, withheld{S13}
  - cp_inval = invalidation walk: bins none, invalidating{S12 invalidating}
  - cp_stale_fill_outcome = for cp_event == redirect, how the fill made stale by the redirect completes: bins completed_ok{all its beats return without error}, completed_err{at least one stale beat returns instr_err_i = 1, F-IMEM-016/F-IC-020}
- Crosses:
  - cr_event_x_fill = cp_event x cp_fill_state: required bins (18): fence_i_one_beat_outst, fence_i_two_to_line, fence_i_multi_line, redirect_one_beat_outst, redirect_two_to_line, redirect_multi_line, bus_err_beat_one_beat_outst, bus_err_beat_two_to_line, bus_err_beat_multi_line, ecc_inject_one_beat_outst, ecc_inject_two_to_line, ecc_inject_multi_line, icache_disable_one_beat_outst, icache_disable_two_to_line, icache_disable_multi_line, key_req_one_beat_outst, key_req_two_to_line, key_req_multi_line
  - cr_event_x_key = cp_event x cp_key: required bins (11): fence_i_valid, fence_i_withheld, redirect_valid, redirect_withheld, bus_err_beat_valid, bus_err_beat_withheld, ecc_inject_valid, ecc_inject_withheld, icache_disable_valid, icache_disable_withheld, key_req_valid; ignore key_req_withheld: the icache does not re-request a key while a request is already pending (a fence.i in AWAIT_SCRAMBLE_KEY is ignored, F-IC-024; the F-IC-025 re-request happens during the invalidation walk with the key valid)
  - cr_event_x_inval = cp_event x cp_inval: required bins (12): fence_i_none, fence_i_invalidating, redirect_none, redirect_invalidating, bus_err_beat_none, bus_err_beat_invalidating, ecc_inject_none, ecc_inject_invalidating, icache_disable_none, icache_disable_invalidating, key_req_none, key_req_invalidating
  - cr_redirect_x_stale_err = cp_stale_fill_outcome x cp_fill_state: required bins (6): completed_ok_one_beat_outst, completed_ok_two_to_line, completed_ok_multi_line, completed_err_one_beat_outst, completed_err_two_to_line, completed_err_multi_line
- Adopted (riscv-dv): none
- TP items: TP-XIF-006, TP-XIF-007, TP-XIF-018, TP-XIF-022

### CG-XIF-006: gen_cg_xif_zcmp_inflight
- Features: F-CMP-056, F-CMP-057, F-CMP-058, F-CMP-059, F-CMP-060, F-CMP-061, F-CMP-063, F-IRQ-020, F-DBG-010, F-DBG-046, F-DMEM-046, F-DMEM-047, F-EXC-043, F-EXC-044, F-FE-024, F-RVFI-022, F-RVFI-023, F-TRG-023
- Sample: an asynchronous edge (irq_pending_o / irq_nm_i / debug_req_i rising), a data bus error response, or a PMP data fault record while S14 zcmp_inflight; condition: zcmp_inflight && event; anti-vacuity: Zcmp sequences exist only when the program emits cm.* (compressed_heavy / mixed) and the events are driver injections; a hit proves the event landed inside a multi-micro-op sequence.
- Coverpoints:
  - cp_zcmp_kind = S14 zcmp_kind: bins push, pop, popret, popretz, mvsa01, mva01s
  - cp_phase = micro-op position when the event arrived: bins first{first micro-op record pending}, middle{neither first nor last}, last{rvfi_ext_expanded_insn_last micro-op pending}
  - cp_event = event: bins irq_maskable, nmi, debug_req, step{dcsr.step = 1 resume into the cm.* instruction, F-DBG-046}, bus_err_store{S6 on a pushed store}, bus_err_load{S6 on a popped load}, pmp_fault{rvfi_trap load/store access fault with no bus request for that word}
  - cp_outcome = how the sequence ended: bins completed_then_event{all micro-ops retired, then handler/debug entry}, interrupted_reexecuted{trap taken mid-sequence with mepc = cm.* pc, the data requests repeat after mret, F-IRQ-020}, trap_mid_sequence{rvfi_trap on a micro-op, F-RVFI-023}
- Crosses:
  - cr_kind_x_event = cp_zcmp_kind x cp_event: required bins (32): push_irq_maskable, push_nmi, push_debug_req, push_step, push_bus_err_store, push_pmp_fault, pop_irq_maskable, pop_nmi, pop_debug_req, pop_step, pop_bus_err_load, pop_pmp_fault, popret_irq_maskable, popret_nmi, popret_debug_req, popret_step, popret_bus_err_load, popret_pmp_fault, popretz_irq_maskable, popretz_nmi, popretz_debug_req, popretz_step, popretz_bus_err_load, popretz_pmp_fault, mvsa01_irq_maskable, mvsa01_nmi, mvsa01_debug_req, mvsa01_step, mva01s_irq_maskable, mva01s_nmi, mva01s_debug_req, mva01s_step; ignore pop_bus_err_store, popret_bus_err_store, popretz_bus_err_store, mvsa01_bus_err_store, mva01s_bus_err_store, push_bus_err_load, mvsa01_bus_err_load, mva01s_bus_err_load, mvsa01_pmp_fault, mva01s_pmp_fault: cm.pop/popret/popretz issue only loads, cm.push only stores, cm.mvsa01/mva01s issue no memory access
  - cr_event_x_outcome = cp_event x cp_outcome: required bins (9): irq_maskable_completed_then_event, irq_maskable_interrupted_reexecuted, nmi_completed_then_event, nmi_interrupted_reexecuted, debug_req_completed_then_event, step_completed_then_event, bus_err_store_trap_mid_sequence, bus_err_load_trap_mid_sequence, pmp_fault_trap_mid_sequence; ignore bus_err_store_completed_then_event, bus_err_store_interrupted_reexecuted, bus_err_load_completed_then_event, bus_err_load_interrupted_reexecuted, pmp_fault_completed_then_event, pmp_fault_interrupted_reexecuted, irq_maskable_trap_mid_sequence, nmi_trap_mid_sequence, debug_req_trap_mid_sequence, step_trap_mid_sequence, debug_req_interrupted_reexecuted, step_interrupted_reexecuted: a bus or PMP fault always traps on the micro-op (F-CMP-060/061); an interrupt or debug request never produces rvfi_trap on a micro-op; debug entry and single-step are blocked for the whole sequence (F-DBG-010/046) so they cannot interrupt it
  - cr_phase_x_irq = cp_phase x cp_event: required bins (6): first_irq_maskable, middle_irq_maskable, last_irq_maskable, first_nmi, middle_nmi, last_nmi; ignore all other 15 combinations: only interrupts can land mid-sequence (F-IRQ-020: taken during load/store micro-ops, blocked during COMMIT ops); debug/step wait for the sequence and faults are covered by cr_kind_x_event
- Adopted (riscv-dv): none
- TP items: TP-XIF-011, TP-XIF-012, TP-XIF-013

### CG-XIF-007: gen_cg_xif_flush_x_irq
- Features: F-CSR-006, F-CSR-007, F-CSR-008, F-CSR-026, F-CSR-031, F-CSR-033, F-IRQ-023, F-IRQ-024, F-IRQ-029, F-IRQ-038, F-IRQ-059, F-IRQ-060, F-PRV-008, F-PRV-012, F-DBG-056, F-DBG-058, F-EXC-061
- Sample: retirement of a flushing CSR write (S16), a non-flushing CSR write, mret or dret (S17) with rvfi_trap = 0; condition: such a retirement; anti-vacuity: these instructions retire only when the program executes them and cp_irq_state is read from the pins in the retirement cycle, so a non-`none` bin proves the pipeline flush coincided with a pending asynchronous request.
- Coverpoints:
  - cp_flush_kind = retired instruction: bins csr_irq{write to mie/mstatus/mip, flushing}, csr_other_flush{any other flushing CSR write}, csr_nonflush{mscratch or mepc write, F-CSR-007}, mret, dret
  - cp_irq_state = pins in the retirement cycle: bins none, irq_pending{irq_pending_o only}, nmi{irq_nm_i only}, debug_req{debug_req_i only}, multiple{>= 2}
  - cp_next = next record: bins handler_irq{rvfi_intr = 1, !rvfi_ext_nmi}, handler_nmi{rvfi_intr = 1 with rvfi_ext_nmi or rvfi_ext_nmi_int}, debug_entry{rvfi_ext_debug_mode rises}, sequential{pc == this record's rvfi_pc_wdata}
  - cp_enable_effect = irq_pending_o edge within 2 cycles after the retirement (csr_irq only): bins enables_pending{0 -> 1, F-IRQ-059}, disables_pending{1 -> 0, F-IRQ-060}, neutral{no edge}
  - cp_mode_to = rvfi_mode of the next record after mret/dret: bins m, u
- Crosses:
  - cr_kind_x_irq = cp_flush_kind x cp_irq_state: required bins (25): csr_irq_none, csr_irq_irq_pending, csr_irq_nmi, csr_irq_debug_req, csr_irq_multiple, csr_other_flush_none, csr_other_flush_irq_pending, csr_other_flush_nmi, csr_other_flush_debug_req, csr_other_flush_multiple, csr_nonflush_none, csr_nonflush_irq_pending, csr_nonflush_nmi, csr_nonflush_debug_req, csr_nonflush_multiple, mret_none, mret_irq_pending, mret_nmi, mret_debug_req, mret_multiple, dret_none, dret_irq_pending, dret_nmi, dret_debug_req, dret_multiple
  - cr_effect_x_next = cp_enable_effect x cp_next: required bins (11): enables_pending_handler_irq, enables_pending_handler_nmi, enables_pending_debug_entry, enables_pending_sequential, disables_pending_handler_nmi, disables_pending_debug_entry, disables_pending_sequential, neutral_handler_irq, neutral_handler_nmi, neutral_debug_entry, neutral_sequential; ignore disables_pending_handler_irq: when irq_pending_o falls to 0 no maskable interrupt remains to be taken
  - cr_mode_to_x_irq = cp_mode_to x cp_irq_state: required bins (10): m_none, m_irq_pending, m_nmi, m_debug_req, m_multiple, u_none, u_irq_pending, u_nmi, u_debug_req, u_multiple
- Adopted (riscv-dv): none
- TP items: TP-XIF-014, TP-XIF-015

### CG-XIF-008: gen_cg_xif_fetch_enable_off
- Features: F-IMEM-022, F-IMEM-023, F-IMEM-024, F-IMEM-025, F-RST-010, F-RST-011, F-RST-012, F-RST-013, F-RST-014, F-RST-015, F-IRQ-056, F-SEC-012, F-DIT-028
- Sample: fetch_enable_i leaving IbexMuBiOn (S10 falling); one sample per true in-flight flag (`none` only when no flag is true); condition: the Off transition; anti-vacuity: only fetch_enable_regime = toggling produces Off transitions; a hit proves the Off edge coincided with the in-flight state and that the Off window had the recorded content.
- Coverpoints:
  - cp_off_encoding = value driven: bins mubi_off{IbexMuBiOff}, invalid_encoding{any other non-On encoding, F-IMEM-023}
  - cp_inflight = DUT state at the Off edge: bins none, fetch_outst{S1 >= 1}, data_outst{S4 >= 1, F-RST-011}, split_inflight{S5}, irq_pending{irq_pending_o}, nmi{irq_nm_i}, debug_req{debug_req_i}, sleeping{S9}, in_debug{dbg_mode_q}, zcmp_inflight{S14}
  - cp_off_duration = length of the Off window: bins one_cycle{1}, short{2..15}, long{16..200}
  - cp_during_off = events inside the Off window: bins nothing, async_rises{irq_pending_o, irq_nm_i or debug_req_i rises, F-RST-015/F-IRQ-056}, data_rsp_returns{data_rvalid_i, F-IMEM-024}, fetch_rsp_returns{instr_rvalid_i}
  - cp_retire_after = first record after re-enable: bins resumed_sequential{pc == held PC, F-IMEM-025}, handler{rvfi_intr = 1}, debug{rvfi_ext_debug_mode rises}
- Crosses:
  - cr_enc_x_inflight = cp_off_encoding x cp_inflight: required bins (20): mubi_off_none, mubi_off_fetch_outst, mubi_off_data_outst, mubi_off_split_inflight, mubi_off_irq_pending, mubi_off_nmi, mubi_off_debug_req, mubi_off_sleeping, mubi_off_in_debug, mubi_off_zcmp_inflight, invalid_encoding_none, invalid_encoding_fetch_outst, invalid_encoding_data_outst, invalid_encoding_split_inflight, invalid_encoding_irq_pending, invalid_encoding_nmi, invalid_encoding_debug_req, invalid_encoding_sleeping, invalid_encoding_in_debug, invalid_encoding_zcmp_inflight
  - cr_dur_x_during = cp_off_duration x cp_during_off: required bins (12): one_cycle_nothing, one_cycle_async_rises, one_cycle_data_rsp_returns, one_cycle_fetch_rsp_returns, short_nothing, short_async_rises, short_data_rsp_returns, short_fetch_rsp_returns, long_nothing, long_async_rises, long_data_rsp_returns, long_fetch_rsp_returns
  - cr_during_x_after = cp_during_off x cp_retire_after: required bins (12): nothing_resumed_sequential, nothing_handler, nothing_debug, async_rises_resumed_sequential, async_rises_handler, async_rises_debug, data_rsp_returns_resumed_sequential, data_rsp_returns_handler, data_rsp_returns_debug, fetch_rsp_returns_resumed_sequential, fetch_rsp_returns_handler, fetch_rsp_returns_debug
- Adopted (riscv-dv): none
- TP items: TP-XIF-016

### CG-XIF-009: gen_cg_xif_pmp_reconfig
- Features: F-PMP-055, F-PMP-065, F-PMP-066, F-PMP-079, F-PMP-086, F-PMP-087, F-PMP-088, F-PMP-092, F-PMP-093, F-PMP-100, F-CSR-006, F-CSR-008, F-IC-039, F-PRV-013
- Sample: retirement of a PMP CSR write (S16 pmp_csr) with rvfi_trap = 0; condition: such a retirement; anti-vacuity: mid-run PMP writes happen only in pmp_regime != off regions (and at region boundaries); a hit proves a reconfiguration retired with the recorded in-flight and verdict state.
- Coverpoints:
  - cp_csr = written register: bins pmpcfg, pmpaddr, mseccfg
  - cp_fetch = S1 at the retirement: bins fetch_idle{0}, fetch_outst{>= 1: prefetched words that must be re-checked, F-PMP-092}
  - cp_prev_ls_outst = the previous record was a load/store whose response arrived after that record's retirement (the CSR write sat in ID while the access was in WB): bins no, single{non-split access}, split{misaligned pair in flight, F-PMP-086..088}
  - cp_verdict_change = effect on the following instructions: bins next_fetch_now_denied{next record is rvfi_trap with instruction access fault at pc == this record's pc_wdata}, next_data_now_denied{next load/store record faults with no dbus request for that word}, no_change{next records proceed}
  - cp_lock = pmpcfg write setting an L bit: bins sets_lock, no_lock
  - cp_icache = S12 icache_en_q: bins enabled, disabled
- Crosses:
  - cr_csr_x_fetch_x_verdict = cp_csr x cp_fetch x cp_verdict_change: required bins (18): pmpcfg_fetch_idle_next_fetch_now_denied, pmpcfg_fetch_idle_next_data_now_denied, pmpcfg_fetch_idle_no_change, pmpcfg_fetch_outst_next_fetch_now_denied, pmpcfg_fetch_outst_next_data_now_denied, pmpcfg_fetch_outst_no_change, pmpaddr_fetch_idle_next_fetch_now_denied, pmpaddr_fetch_idle_next_data_now_denied, pmpaddr_fetch_idle_no_change, pmpaddr_fetch_outst_next_fetch_now_denied, pmpaddr_fetch_outst_next_data_now_denied, pmpaddr_fetch_outst_no_change, mseccfg_fetch_idle_next_fetch_now_denied, mseccfg_fetch_idle_next_data_now_denied, mseccfg_fetch_idle_no_change, mseccfg_fetch_outst_next_fetch_now_denied, mseccfg_fetch_outst_next_data_now_denied, mseccfg_fetch_outst_no_change
  - cr_prev_ls_x_csr = cp_prev_ls_outst x cp_csr: required bins (9): no_pmpcfg, no_pmpaddr, no_mseccfg, single_pmpcfg, single_pmpaddr, single_mseccfg, split_pmpcfg, split_pmpaddr, split_mseccfg
  - cr_icache_x_verdict = cp_icache x cp_verdict_change: required bins (6): enabled_next_fetch_now_denied, enabled_next_data_now_denied, enabled_no_change, disabled_next_fetch_now_denied, disabled_next_data_now_denied, disabled_no_change
  - cr_lock_x_verdict = cp_lock x cp_verdict_change: required bins (6): sets_lock_next_fetch_now_denied, sets_lock_next_data_now_denied, sets_lock_no_change, no_lock_next_fetch_now_denied, no_lock_next_data_now_denied, no_lock_no_change
- Adopted (riscv-dv): none
- TP items: TP-XIF-010, TP-XIF-019

### CG-XIF-010: gen_cg_xif_reset_inflight
- Features: F-RST-001, F-RST-008, F-RST-009, F-RST-018, F-RST-019, F-RST-024, F-RST-026, F-SEC-035, F-IC-009, F-IC-022, F-DBG-008, F-IRQ-055, F-RVFI-033
- Sample: rst_ni falling edge after at least one retirement since the previous reset (mid-run reset; the time-0 reset is excluded); one sample per true in-flight flag; condition: mid-run reset; anti-vacuity: mid-run resets are issued only by the reset test group at randomized instants; a hit proves the reset interrupted that state and that the post-release observation followed.
- Coverpoints:
  - cp_inflight = state at the reset edge: bins idle, fetch_outst{S1 >= 1}, data_outst{S4 >= 1}, split_inflight{S5}, zcmp_inflight{S14}, sleeping{S9}, in_debug{dbg_mode_q}, irq_pending{irq_pending_o}, nmi{irq_nm_i}, debug_req{debug_req_i}, fill_inflight{S12}, key_withheld{S13}, invalidating{S12 invalidating}, fetch_en_off{!S10}
  - cp_after = observation after release: bins first_fetch_boot_vector{instr_addr_o == {boot_addr_i[31:8], 8'h80} within 2 cycles of release, F-RST-002/008}, stale_rsp_after_release{a response for a pre-reset request arrives after release, F-RST-018}, async_pending_at_release{debug_req_i or irq_nm_i high at release, taken in FIRST_FETCH, F-RST-024}
  - cp_reset_len = cycles rst_ni held low: bins short{1..2}, long{3..64}
- Crosses:
  - cr_inflight_x_after = cp_inflight x cp_after: required bins (39): idle_first_fetch_boot_vector, idle_async_pending_at_release, fetch_outst_first_fetch_boot_vector, fetch_outst_stale_rsp_after_release, fetch_outst_async_pending_at_release, data_outst_first_fetch_boot_vector, data_outst_stale_rsp_after_release, data_outst_async_pending_at_release, split_inflight_first_fetch_boot_vector, split_inflight_stale_rsp_after_release, split_inflight_async_pending_at_release, zcmp_inflight_first_fetch_boot_vector, zcmp_inflight_stale_rsp_after_release, zcmp_inflight_async_pending_at_release, sleeping_first_fetch_boot_vector, sleeping_async_pending_at_release, in_debug_first_fetch_boot_vector, in_debug_stale_rsp_after_release, in_debug_async_pending_at_release, irq_pending_first_fetch_boot_vector, irq_pending_stale_rsp_after_release, irq_pending_async_pending_at_release, nmi_first_fetch_boot_vector, nmi_stale_rsp_after_release, nmi_async_pending_at_release, debug_req_first_fetch_boot_vector, debug_req_stale_rsp_after_release, debug_req_async_pending_at_release, fill_inflight_first_fetch_boot_vector, fill_inflight_stale_rsp_after_release, fill_inflight_async_pending_at_release, key_withheld_first_fetch_boot_vector, key_withheld_stale_rsp_after_release, key_withheld_async_pending_at_release, invalidating_first_fetch_boot_vector, invalidating_stale_rsp_after_release, invalidating_async_pending_at_release, fetch_en_off_stale_rsp_after_release, fetch_en_off_async_pending_at_release; ignore idle_stale_rsp_after_release, sleeping_stale_rsp_after_release, fetch_en_off_first_fetch_boot_vector: with no transaction outstanding (idle, or asleep which requires no outstanding access) no stale response can arrive; with fetch_enable_i not On at release the boot fetch is gated (F-RST-013) so it cannot appear within the 2-cycle window
- Adopted (riscv-dv): none
- TP items: TP-XIF-017

### CG-XIF-011: gen_cg_xif_mode_x_event
- Features: F-PRV-001, F-PRV-013, F-PRV-023, F-PRV-024, F-PRV-031, F-PRV-033, F-IRQ-008, F-IRQ-029, F-IRQ-039, F-IRQ-053, F-DBG-019, F-DBG-020, F-DBG-023, F-DBG-026, F-DBG-027, F-DBG-029, F-DBG-030, F-DBG-056, F-DBG-057, F-DBG-059, F-DBG-064, F-PMP-051, F-PMP-052, F-PMP-053, F-PMP-072, F-PMP-097, F-EXC-024, F-EXC-025, F-EXC-027, F-IC-039, F-IC-040, F-FE-022, F-RVFI-027, F-CSR-014, F-TRG-012, F-TRG-013, F-DIT-010
- Sample: an interface event record: rvfi_trap record (cause class from the ISA model's expected cause and the dbus/ibus monitors: bus error vs PMP by presence/absence of the bus transaction), rvfi_intr record, debug entry (first record with rvfi_ext_debug_mode = 1 after a non-debug record, cause class from dcsr.cause read back by the debug ROM), WFI wake (CG-XIF-004 event), each attributed to cp_mode by S11; condition: event; anti-vacuity: mode is program-driven (priv_regime) and U-mode/debug events exist only when the program enters those modes; a hit proves the interface event happened in that mode.
- Coverpoints:
  - cp_mode = mode of the instruction or interrupted context: bins m, u, debug{dbg_mode_q}
  - cp_event = event class: bins load_err_bus, store_err_bus, load_fault_pmp, store_fault_pmp, fetch_err_bus, fetch_fault_pmp, illegal, ecall, ebreak_trap, ebreak_debug, irq_taken, nmi_taken, debug_req_entry, trigger_entry, step_entry, wfi_wake, csr_illegal_priv{CSR access denied by csr[9:8] > mode, F-CSR-014}
  - cp_mprv = mstatus.MPRV/MPP of a data-fault event (tracked from retired mstatus writes / ISA model): bins mprv0, mprv1_mpp_u{MPRV = 1, MPP = U, F-PRV-013/F-PMP-072}
- Crosses:
  - cr_mode_x_event = cp_mode x cp_event: required bins (44): m_load_err_bus, m_store_err_bus, m_load_fault_pmp, m_store_fault_pmp, m_fetch_err_bus, m_fetch_fault_pmp, m_illegal, m_ecall, m_ebreak_trap, m_ebreak_debug, m_irq_taken, m_nmi_taken, m_debug_req_entry, m_trigger_entry, m_step_entry, m_wfi_wake, m_csr_illegal_priv, u_load_err_bus, u_store_err_bus, u_load_fault_pmp, u_store_fault_pmp, u_fetch_err_bus, u_fetch_fault_pmp, u_illegal, u_ecall, u_ebreak_trap, u_ebreak_debug, u_irq_taken, u_nmi_taken, u_debug_req_entry, u_trigger_entry, u_step_entry, u_wfi_wake, u_csr_illegal_priv, debug_load_err_bus, debug_store_err_bus, debug_load_fault_pmp, debug_store_fault_pmp, debug_fetch_err_bus, debug_fetch_fault_pmp, debug_illegal, debug_ecall, debug_ebreak_debug, debug_wfi_wake; ignore debug_irq_taken, debug_nmi_taken, debug_debug_req_entry, debug_trigger_entry, debug_step_entry, debug_ebreak_trap, debug_csr_illegal_priv: all interrupts incl. NMI are ignored in debug mode (F-DBG-056/057); debug_req_i is ignored while already in debug (F-DBG-007); triggers do not fire in debug mode (F-TRG-013); a step re-entry is attributed to the stepped instruction's non-debug mode; ebreak in debug mode re-enters debug and never traps (F-DBG-023); debug mode runs at M privilege so no CSR privilege check can fail (F-DBG-064)
  - cr_mprv_x_datafault = cp_mprv x cp_event: required bins (4): mprv0_load_fault_pmp, mprv0_store_fault_pmp, mprv1_mpp_u_load_fault_pmp, mprv1_mpp_u_store_fault_pmp; ignore all other 30 combinations: MPRV changes only the privilege used for PMP data checks (F-PRV-013), so it is meaningful only for PMP data faults
- Adopted (riscv-dv): none
- TP items: TP-XIF-020

### CG-XIF-012: gen_cg_xif_dummy_x_event
- Features: F-DIT-011, F-DIT-012, F-DIT-013, F-DIT-019, F-DIT-020, F-DIT-021, F-DIT-023, F-DIT-028, F-DIT-029, F-FE-018, F-PMP-094, F-TRG-026
- Sample: S20 dummy_inserted (probe candidate P1: dummy_instr_id_o rising, dummy type from fcov_dummy_instr_type); condition: cpuctrlsts.dummy_instr_en = 1 (program-set) and the LFSR fires; anti-vacuity: dummies are architecturally invisible (no RVFI record, no bus traffic), so only the probe can sample them; a hit proves a dummy was in ID while the crossed boundary state held. Coverage-only; no checker depends on this group.
- Coverpoints:
  - cp_event = boundary state in the insertion cycle: bins none, redirect{S19 in the same cycle, F-DIT-021}, irq_pending{irq_pending_o, F-DIT-019}, nmi{irq_nm_i}, debug_req{debug_req_i, F-DIT-020}, data_outst_load{S4 >= 1 for a load, F-DIT-029}
  - cp_dummy_type = fcov_dummy_instr_type: bins add, mul, div, and_
  - cp_mask = cpuctrlsts.dummy_instr_mask tracked from retired CSR writes (F-DIT-012): bins m000, m001, m010, m011, m100, m101, m110, m111
  - cp_mode = S11 mode_q: bins m, u
- Crosses:
  - cr_event_x_type = cp_event x cp_dummy_type: required bins (24): none_add, none_mul, none_div, none_and_, redirect_add, redirect_mul, redirect_div, redirect_and_, irq_pending_add, irq_pending_mul, irq_pending_div, irq_pending_and_, nmi_add, nmi_mul, nmi_div, nmi_and_, debug_req_add, debug_req_mul, debug_req_div, debug_req_and_, data_outst_load_add, data_outst_load_mul, data_outst_load_div, data_outst_load_and_
  - cr_type_x_mode = cp_dummy_type x cp_mode: required bins (8): add_m, add_u, mul_m, mul_u, div_m, div_u, and__m, and__u
- Adopted (riscv-dv): none
- TP items: TP-XIF-021

### CG-ADOPT-001: gen_cg_adopt_gpr_hazard
- Features: F-BIT-039, F-MUL-025, F-DMEM-028, F-DMEM-029, F-CMP-068, F-BTALU-013
- Sample: every RVFI retirement with rvfi_trap = 0, compared with the previous retirement (riscv-dv check_hazard_condition against pre_instr); condition: rvfi_valid; anti-vacuity: the hazard class depends on the register operands of two consecutive retirements (rvfi_rs1_addr/rs2_addr/rd_addr and, for the LSU class, rvfi_mem_addr), so `no_hazard` is not always true and each hazard bin proves a specific back-to-back dependency retired.
- Coverpoints:
  - cp_gpr_hazard = register dependency on the previous retirement: bins no_hazard{no shared register}, raw{this reads the previous rd}, war{this writes a register the previous read}, waw{same rd, both non-x0}
  - cp_lsu_hazard = memory dependency on the previous retirement (both load/store, same rvfi_mem_addr): bins no_hazard, raw{load after store, same address}, war{store after load, same address}, waw{store after store, same address}
- Crosses: none
- Adopted (riscv-dv): cp_gpr_hazard (instr.gpr_hazard: NO_HAZARD/RAW_HAZARD/WAR_HAZARD/WAW_HAZARD in the R_/I_/LOAD_/STORE_/CI_/CS_ INSTR_CG_BEGIN macros) and cp_lsu_hazard (instr.lsu_hazard in LOAD_/STORE_/CL_/CS_ INSTR_CG_BEGIN), riscv_instr_cover_group.sv. Adopted because our ISA features cover forwarding for specific classes (F-BIT-039, F-MUL-025, F-DMEM-028) but no feature enumerates all four hazard classes for arbitrary back-to-back pairs; riscv-dv's per-instruction hazard coverpoints are collapsed to one class-independent group.
- TP items: TP-ADOPT-001

### CG-ADOPT-002: gen_cg_adopt_branch_history
- Features: F-ISA-023, F-ISA-024, F-BTALU-001, F-BTALU-005, F-PMC-039, F-PMC-040
- Sample: retirement of a conditional branch (beq/bne/blt/bge/bltu/bgeu/c.beqz/c.bnez) once 5 branches have retired; taken = rvfi_pc_wdata != rvfi_pc_rdata + length; condition: branch retirement; anti-vacuity: the 5-bit history changes with every branch outcome, so a pattern bin proves that outcome sequence occurred back-to-back.
- Coverpoints:
  - cp_branch_history = last five branch outcomes, MSB oldest: bins all_taken{5'b11111}, all_not_taken{5'b00000}, alt_01010{5'b01010}, alt_10101{5'b10101}, other{any other value}
- Crosses: none
- Adopted (riscv-dv): branch_hit_history_cg.cp_branch_history (5-bit branch_hit_history), riscv_instr_cover_group.sv, reduced from 32 auto bins to 5 pattern classes. Adopted because F-ISA-024 covers taken vs not-taken per branch but nothing covers outcome sequences (the RTL has no predictor in this config, so the history stresses the redirect/flush pipeline back-to-back: F-BTALU-005, F-FE-013).
- TP items: TP-ADOPT-002

### CG-ADOPT-003: gen_cg_adopt_operand_classes
- Features: F-ISA-001, F-ISA-002, F-ISA-007, F-ISA-008, F-ISA-015, F-ISA-016, F-ISA-023, F-ISA-026, F-DMEM-015, F-DMEM-016
- Sample: retirement of add/sub (sign cross), retirement of xor/or/and/xori/ori/andi (logical similarity), retirement of a branch, jal, load or store (immediate sign); values from rvfi_rs1_rdata/rs2_rdata/rd_wdata and the decoded immediate of rvfi_insn; condition: instruction class match; anti-vacuity: operand signs and the immediate are data, randomized by the generator; a bin proves that operand class retired.
- Coverpoints:
  - cp_addsub_sign = {rs1 sign, rs2 sign, rd sign} of add/sub: bins ppp{+,+,+}, ppn{+,+,- overflow}, pnp, pnn, npp, npn, nnp{-,-,+ overflow}, nnn
  - cp_logical_similarity = relation of rs1 to the second operand for xor/or/and/xori/ori/andi: bins identical{equal}, opposite{bitwise complement}, similar{differ in <= 4 bits}, different{otherwise}
  - cp_imm_sign = sign of the immediate by class: bins branch_fwd{branch imm >= 0}, branch_bwd{branch imm < 0}, jal_fwd, jal_bwd, load_imm_pos, load_imm_neg, store_imm_pos, store_imm_neg
- Crosses: none
- Adopted (riscv-dv): add_cg/sub_cg cp_sign_cross (cross cp_rs1_sign, cp_rs2_sign, cp_rd_sign); xor_cg/or_cg/and_cg/xori_cg/ori_cg/andi_cg cp_logical (instr.logical_similarity); cp_imm_sign in SB_/J_/LOAD_/STORE_INSTR_CG_BEGIN, riscv_instr_cover_group.sv. Adopted because the ISA features name boundary values (F-ISA-002/008/026) but not the sign-class partition of operands, the operand-similarity classes for logic ops, or forward/backward direction per class.
- TP items: TP-ADOPT-003

### CG-ADOPT-004: gen_cg_adopt_jalr_ras
- Features: F-ISA-018, F-ISA-020, F-ISA-022, F-BTALU-003, F-PMC-038
- Sample: retirement of jalr (and c.jr / c.jalr mapped to rs1/rd); condition: jalr class; anti-vacuity: rs1/rd are generator-randomized registers; a bin proves that link-register usage pattern retired.
- Coverpoints:
  - cp_ras = {rs1 class, rd class} with class in {ra = x1, t1 = x6 (alternate link), non_link}: bins ra_ra, ra_t1, ra_non_link, t1_ra, t1_t1, t1_non_link, non_link_ra, non_link_t1, non_link_non_link
- Crosses: none
- Adopted (riscv-dv): jalr_cg cp_ras (cross cp_rs1_link, cp_rd_link with bins ra, t1, non_link), riscv_instr_cover_group.sv. Adopted because F-ISA-018/020 cover jalr semantics and rs1 == rd, not the call/return register conventions that generate the return-address-stack-like patterns (no RAS in Ibex; the pattern still exercises jalr with rs1 == rd == ra, F-ISA-020).
- TP items: TP-ADOPT-004

### CG-ADOPT-005: gen_cg_adopt_compressed_regs
- Features: F-CMP-002, F-CMP-004, F-CMP-018, F-CMP-020, F-CMP-021, F-CMP-023, F-CMP-034, F-CMP-036
- Sample: retirement of a compressed instruction with a 3-bit register field (CIW/CL/CS/CA/CB formats: c.addi4spn, c.lw, c.sw, c.sub/xor/or/and, c.srli/srai/andi, c.beqz/bnez, Zcb forms); the register is decoded from rvfi_insn; condition: such a retirement; anti-vacuity: the register is generator-randomized over the eight x8..x15 values; a bin proves that register value was used in a 3-bit field.
- Coverpoints:
  - cp_c_reg_prime = 3-bit register field value: bins s0{x8}, s1{x9}, a0{x10}, a1{x11}, a2{x12}, a3{x13}, a4{x14}, a5{x15}
- Crosses: none
- Adopted (riscv-dv): bins gpr[] = {S0, S1, A0, A1, A2, A3, A4, A5} on cp_rd/cp_rs1/cp_rs2 of the CIW_/CL_/CS_/CA_/CB_INSTR_CG_BEGIN macros, riscv_instr_cover_group.sv, collapsed to one register-field coverpoint. Adopted because the CMP features cover each instruction's semantics but not that every value of the 3-bit register field was decoded (the compressed decoder's x8 offset, F-CMP-001).
- TP items: TP-ADOPT-005

### CG-ADOPT-006: gen_cg_adopt_bitcount_result
- Features: F-BIT-005, F-BIT-006
- Sample: retirement of clz/ctz/cpop; result from rvfi_rd_wdata; condition: instruction class; anti-vacuity: the result depends on the generator-randomized operand; a range bin proves an operand with that many leading/trailing zeros or set bits retired.
- Coverpoints:
  - cp_bitcount_result = rvfi_rd_wdata of clz/ctz/cpop: bins r0{0}, r1_7{1..7}, r8_15{8..15}, r16_23{16..23}, r24_31{24..31}
- Crosses: none
- Adopted (riscv-dv): clz_cg/ctz_cg/cpop_cg CP_VALUE_RANGE(num_leading_zeros / num_trailing_zeros / num_set_bits, instr.rd_value, 0, XLEN-1), riscv_instr_cover_group.sv, reduced from 32 values to 5 ranges. Adopted because F-BIT-006 covers the boundary values (0 and 32) only; the value 32 (all-zero operand) is intentionally not adopted since riscv-dv's range stops at XLEN-1 and F-BIT-006 already owns it.
- TP items: TP-ADOPT-006

### CG-REG-009: gen_cg_reg_intg_knobs
- Features: F-IMEM-027, F-SEC-017, F-SEC-019, F-DMEM-041
- Sample: regime phase start (agent phase log); condition: MemECC=1 build; anti-vacuity: sampled
  once per phase, so a bin hit proves that phase ran with that knob value; the none value is
  distinguished from "no phase ran" by the phase-count coverpoint of CG-REG-001
- Coverpoints:
  - cp_imem_intg_rate = knob:imem_intg_err_rate: bins none{none}, rare{rare}, frequent{frequent}
  - cp_dmem_intg_rate = knob:dmem_intg_err_rate: bins none{none}, rare{rare}, frequent{frequent}
- Crosses:
  - cr_intg_rates = cp_imem_intg_rate x cp_dmem_intg_rate: all 9 bins
- Adopted (riscv-dv): none
- TP items: TP-REG-026

### CG-REG-010: gen_cg_reg_mcounteren_knob
- Features: F-PMC-025, F-SEC-020
- Sample: time 0 of each run (driver knob value); condition: always (one sample per run);
  anti-vacuity: one sample per run, bins hit only by runs that actually drove that value
- Coverpoints:
  - cp_mcounteren_writable = knob:mcounteren_writable: bins on{on}, off{off}, invalid{invalid}
- Crosses: none
- Adopted (riscv-dv): none
- TP items: TP-REG-027

## Completeness measure (proposal)

Definition the plan uses (DV_prompt Section 4, functional-coverage condition 2):

1. Every feature F-<AREA>-<nnn> in gen_feature_list maps to >= 1 TP item (trace_feat_tp_*.csv,
   `feature,tp_item`) and, through those items, to >= 1 bin (trace_tp_bin_*.csv,
   `tp_item,covergroup,coverpoint,bin,adopted`). A feature with a TP item but no bin, or a bin
   but no TP item, is incomplete.
2. Every bin maps back to >= 1 feature through its covergroup's `Features:` field. A covergroup
   whose Features field cites no F-ID, or cites an F-ID absent from the feature list, fails the
   check. Bin references are `CG-<AREA>-<nnn>.<cp>.<bin>` (cross bins `CG-...cr_<name>.<bin>`);
   the SV covergroup name is the `gen_cg_<area>_<name>` in the CG header and the URG key is
   `<gen_cg_name>.<cp>.<bin>`.
3. Adopted bins (riscv-dv) are counted separately: `adopted = 1` rows are reported as their own
   total and excluded from the spec-derived totals, so the 80%-of-declared-bins gate is reported
   twice (spec-derived, adopted) and passes only if both pass. An adopted bin still needs a real
   F-ID (rule 2); the `Adopted (riscv-dv):` field names the source covergroup.
4. Per-test fcov-expectation manifest rule (dv_principles.md s6 rule 3; ci/check_fcov_expectations.py):
   every test declares in dv/auto_dv/fcov_expectations/<test>.fcov.yaml the bins it intends to
   hit; a declared bin unhit in that test's own coverage (urg -tests isolation) fails the run
   (exit 2), and an unparseable or missing manifest also fails (exit 1). The TP item's `Bins:`
   field is the set the item is responsible for closing across the regression; a test's manifest
   is the per-run reliable subset and must contain >= 1 bin from every coverpoint of every CG its
   items own (so a test cannot claim an item while sampling none of its group).
5. Regime layers are part of completeness: every knob value and every legal knob transition bin
   (CG-REG-001..006) must be hit by the regression, and every TP item of Phase 2 must list >= 1
   knob under `Knobs:` (an item with `Knobs: none` is Phase 1 only).
6. A reviewer other than the author confirms the mapping (cross-review policy); the check script
   output is attached to the review artifact.

Check script inputs and outputs (proposal for the DV Lead's tooling, `gen_check_trace.py`):

- Inputs: dv/auto_dv/docs/gen_feature_list.md (F-ID universe: every `### F-` heading), the
  folded gen_test_plan.md (TP-ID universe and `Bins:` fields), gen_fcov_plan.md (CG/cp/bin
  universe from `- cp_` and `- cr_` lines, adopted flags from `Adopted (riscv-dv):`), the two
  trace CSVs per area (trace_feat_tp_<area>.csv, trace_tp_bin_<area>.csv), and optionally the
  merged URG grpinfo.txt for hit counts.
- Checks: (a) every F-ID appears in some trace_feat_tp row; (b) every tp_item in both CSVs exists
  in the test plan; (c) every (covergroup, coverpoint, bin) in trace_tp_bin exists in the fcov
  plan and its `adopted` flag matches the CG's Adopted field; (d) every CG's Features F-IDs exist;
  (e) every F-ID reaches >= 1 bin through (a)+(c); (f) every bin reaches >= 1 F-ID through (c)+(d);
  (g) with URG input: hit ratio of declared bins, spec-derived and adopted separately; (h) every
  fcov_expectations/<test>.fcov.yaml bin exists in the plan and covers >= 1 cp per owned CG.
- Output: a table per area (features, TP items, bins, cross bins, adopted bins, unmapped
  features, orphan bins, orphan TP items) and a non-zero exit on any unmapped item; the table is
  committed under dv/auto_dv/evidence/.

## Counts

| Measure | REG | XIF | ADOPT | Total |
|---|---|---|---|---|
| covergroups | 8 | 12 | 6 | 26 |
| coverpoints (cp_*) | 43 | 52 | 9 | 104 |
| crosses (cr_*) | 14 | 31 | 0 | 45 |
| bins (coverpoint bins, legal) | 299 | 205 | 55 | 559 |
| cross bins (legal) | 196 | 463 | 0 | 659 |
| adopted bins (riscv-dv; adopted = 1) | 0 | 0 | 55 | 55 |

Of the REG coverpoint bins, 187 are knob transition bins (every ordered pair of values per knob, explicitly enumerated; 3 transitions ignored with a reason). Ignored cross combinations with a reason: 202. Spec-derived bins (adopted = 0): 1163 (504 coverpoint + 659 cross). Every bin is owned by >= 1 TP item (trace_tp_bin_xcut.csv has 1218 rows over 53 items; bins shared by several items appear once per item).

## Probe candidates

- CG-XIF-012 (all bins): needs P1 `dummy_instr_id_o` (rtl/ibex_core.sv:91, an ibex_core output
  wired inside gen_dut_top but not on the wrapper boundary) and `fcov_dummy_instr_type`
  (rtl/ibex_if_stage.sv:818-821). Dummy instructions produce no RVFI record and no bus traffic
  (F-DIT-016, F-FE-018), so no boundary derivation exists. Coverage-only; recommend the DV Lead
  accept P1 or expose the two ports through gen_dut_top as coverage-only outputs (then it is a
  boundary signal, not a probe).
- CG-XIF-002.cp_window, CG-XIF-007 "same cycle" semantics and S11 mode attribution during entry
  windows are boundary approximations (S18). Exact cycle attribution would need P4
  `ctrl_fsm_cs` (IRQ_TAKEN / DBG_TAKEN_IF / FLUSH, rtl/ibex_pkg.sv:291-302) or the RTL's own
  `fcov_interrupt_taken` / `fcov_debug_entry_if` nets (rtl/ibex_controller.sv:1085-1095).
  Recommend the window definition first; P4 only if a bin stays ambiguous in review.
- CG-XIF-005 `fill_inflight` (S12) is derived from tracked cpuctrlsts.icache_enable and the ibus
  outstanding count; P2 (`fill_busy_q`) is the fallback if the boundary derivation mis-attributes
  uncached fetches during the invalidation walk. Recommend boundary first.
- CG-REG-008.cp_inflight_event.mid_zcmp and CG-XIF-006 use rvfi_ext_expanded_insn_valid/_last
  (rtl/ibex_core.sv:178-180): RVFI extension ports, not probes.

