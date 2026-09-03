# Covergroup sampling anchors for tb-infra (T-204 order), rtl-arch

Owner: rtl-arch. Source of the order and the bin lists: dv/auto_dv/evidence/gen_round0_covergroup_set.md (2e596cd,
plan anchors into dv/auto_dv/docs/gen_fcov_plan.md). Per covergroup: the observation point the plan names, the
rtl/ signal and file:line it corresponds to, the sampling condition in RTL terms (which valid or fire qualifies a
sample), the doc/ or local-spec sentence that gives each coverpoint's bin semantics, and every bin the RTL cannot
distinguish or RVFI cannot observe. Anchoring: rtl/ lines, doc/ pages, and the local spec clones under tools/specs/
(riscv-isa-manual, riscv-bitmanip); no DV collateral. Configuration: opentitan (RV32MSingleCycle, RV32BOTEarlGrey,
RV32ZcaZcbZcmp, WritebackStage 1, BranchTargetALU 1; cheriot_enable_i tied Off, dv/auto_dv/tb/gen_dut_top.sv:206).
Delivered in slices of five covergroups; slice 1 = ranks 1..5.

## 0. The RVFI record every group samples on (shared anchors)

| RVFI field the plan names | RTL source (rtl/ibex_core.sv) | Meaning the TB may rely on |
|---|---|---|
| rvfi_valid | :1775 rvfi_stage_valid[RVFI_STAGES-1]; a record leaves ID at rvfi_id_done (:1851-1853) and is emitted at WB done (:1890, :2143) | one record per retired instruction or per trapping instruction; one record per Zcmp MICRO-OP (:2263-2280), never one per Zcmp instruction |
| rvfi_insn | :2263-2267: `{16'b0, instr_rdata_c_id}` for a compressed instruction that is not expanded, else the 32-bit `instr_rdata_id` | a 16-bit encoding is exported as the 16-bit word (rvfi_insn[1:0] != 2'b11); a Zcmp micro-op is exported as its synthesized 32-bit word with rvfi_ext_expanded_insn_valid = 1 (:2270-2280) and the 16-bit source in rvfi_ext_expanded_insn |
| rvfi_trap | :1778; ID exceptions (:1885) OR-ed with WB load/store errors (:1888, :2145) | `rvfi_trap == 0` in every plan condition means neither |
| rvfi_rs1_rdata, rvfi_rs2_rdata (and _addr) | :2304-2310: captured in the instruction's FIRST ID cycle from multdiv_operand_a_ex / _b_ex, zero when the decoder does not read that register (rf_ren_a / rf_ren_b); the operands are the forwarded register reads rf_rdata_a_fwd / _b_fwd (rtl/ibex_id_stage.sv:760-761) | exactly the values the ALU and the multiplier consumed, WB forwarding included; a unary op reports rs2 = 0 |
| rvfi_rd_addr, rvfi_rd_wdata | :2340-2350: captured at the WB write (rvfi_rd_we_wb); rd_wdata = rf_wdata_wb or the load data (:1806); FORCED to 0 when rd == x0 (:2344-2346) | a result class on an rd = x0 record is always `zero`, whatever the datapath computed |
| rvfi_pc_rdata, rvfi_pc_wdata | :2083 pc_id; :2084 `pc_set ? branch_target_ex : pc_if` | pc_wdata conventions: C-1 (trap/mret/dret = next sequential), R9 (Zcmp non-last micro-op = own pc), B13 (odd jalr target keeps bit 0) in gen_t102_rtl_facts.md |
| rvfi_ext_mcycle, rvfi_ext_mhpmcounters[10] | :173-174, :1833-1834, :2102-2127; index k holds mhpmcounter(k+3): [7] = mhpmcounter10 NumInstrRetC (:2122) | minstret is NOT exported (only mcycle and counters 3..12) |
| rvfi_ext_expanded_insn_valid / _insn / _last | :1838, :2270-2280 | last = 1 on the INSTR_EXPANDED_LAST micro-op only |

## 1. CG-MUL-001 gen_cg_mul_ops (gen_fcov_plan.md:513)

- Observation point named by the plan: RVFI retirement, condition decoded OP funct7 0000001 funct3 000..011 or c.mul, rvfi_trap == 0.
- RTL signal chain: rtl/ibex_decoder.sv:653-670 decodes `{7'b000_0001, funct3}` in OPCODE_OP into multdiv_operator_o / multdiv_signed_mode_o (mul: MD_OP_MULL, 2'b00 :653-656; mulh: MD_OP_MULH, 2'b11 :658-661; mulhsu: MD_OP_MULH, 2'b01 :663-666; mulhu: MD_OP_MULH, 2'b00 :668-671) and sets mult_sel_o (:1357-1369). rtl/ibex_multdiv_fast.sv single-cycle block: operands op_a_i/op_b_i = the ID operands (the same values RVFI captures), sign_a = signed_mode_i[0] & op_a_i[31], sign_b = signed_mode_i[1] & op_b_i[31] (:168-169); MULL completes in one cycle (mult_valid = mult_en_i, :203), MULH in two (states MULL -> MULH, :210-233); result multdiv_result_o (:136) -> rf write -> rvfi_rd_wdata.
- Sampling condition in RTL terms: the WB write of an instruction whose decoder saw OPCODE_OP with funct7 0000001 and funct3[2] == 0 (mult_sel_o = 1), no trap; on RVFI: rvfi_valid & ~rvfi_trap & (rvfi_insn[6:0] == 0110011 & rvfi_insn[31:25] == 0000001 & rvfi_insn[14] == 0) OR the 16-bit c.mul encoding (rvfi_insn[1:0] != 11, rvfi_insn[15:10] == 100111, rvfi_insn[6:5] == 10, rvfi_insn[1:0] == 01).
- Doc / spec per coverpoint:
  - cp_op, cp_funct3: doc/03_reference/instruction_decode_execute.rst:120-125 (single-cycle multiplier: MUL 1 cycle, MULH 2 cycles); tools/specs/riscv-isa-manual/src/unpriv/m-st-ext.adoc:22-28 (mul = lower XLEN bits; mulh, mulhu, mulhsu = upper XLEN bits of signed x signed, unsigned x unsigned, signed rs1 x unsigned rs2). c.mul: rtl/ibex_compressed_decoder.sv:462-467 expands it to `mul rsd', rsd', rs2'` (funct7 0000001, funct3 000, rd == rs1 == x8+rsd').
  - cp_rs1_class, cp_rs2_class, cp_sign_pair: the classes are TB partitions of rvfi_rs1_rdata / rvfi_rs2_rdata; bit 31 of each operand is exactly the sign the multiplier uses when its signed_mode bit is set (multdiv_fast:168-169), so cp_sign_pair is the RTL's own sign_a/sign_b pair for mulh, the (rs1 sign, ignored) pair for mulhsu and ignored for mul/mulhu.
  - cp_result_class: rvfi_rd_wdata = the written product (lower or upper word).
  - cp_same_regs, cp_rd_x0: register indices from rvfi_rs1_addr / rvfi_rs2_addr / rvfi_rd_addr (:2306, :2308, :2342).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - c_mul vs mul: internally identical after expansion (same decoder arm and multiplier path); on RVFI the c.mul record carries the 16-bit encoding (rvfi_insn[1:0] != 11, core:2263-2265), never the expanded mul word, so cp_op.c_mul MUST be decoded from the 16-bit form; a decoder that only looks for the 32-bit mul word never sees c.mul.
  - cp_result_class on rd_x0 records: rvfi_rd_wdata is forced to 0 (core:2344-2346), so `zero` is the only reachable result bin when cp_rd_x0 = yes; the plan does not cross the two, but any per-op result expectation must exclude rd = x0 records.
  - The product's discarded half is not observable (mul shows the low word, mulh* the high word): int_min/int_max classes of the OTHER half cannot be sampled from the same record.

## 2. CG-BIT-001 gen_cg_bit_zba_zbb_ops (gen_fcov_plan.md:807)

- Observation point: RVFI retirement, condition decoded sh1add/sh2add/sh3add/andn/orn/xnor/min/max/minu/maxu/sext.b/sext.h/pack/packu/packh (zext.h = pack with rs2 == x0), rvfi_trap == 0.
- RTL signal chain: OPCODE_OP arms in rtl/ibex_decoder.sv: min/max/minu/maxu `{0000101, 100/110/101/111}` :1277-1280; pack/packu/packh `{0000100,100} / {0100100,100} / {0000100,111}` :1282-1284; xnor/orn/andn `{0100000, 100/110/111}` :1286-1288; sh1add/sh2add/sh3add `{0010000, 010/100/110}` :1291-1293; sext.b/sext.h are OPCODE_OP_IMM `{0110000, rs2 field 00100/00101, funct3 001}` :1106-1107 (unary: rf_ren_b = 0). rtl/ibex_alu.sv results: andn/orn/xnor = bwlogic with operand_b inverted (:374-376, :388-389, :1326); shNadd = adder with operand_a pre-shifted `{operand_a[30:0],2'b01}` / `{[29:0],3'b001}` / `{[28:0],4'b0001}` (:75-77, :87-89, :105-107, :1329-1332); min/max/minu/maxu = `cmp_result ? operand_a : operand_b` with signed compare for MIN/MAX (:123-126, :164-167, :552, :1353-1354); pack/packu/packh (:560-567, :1361-1362); sext.b/sext.h (:575-576, :1365).
- Sampling condition in RTL terms: the WB write of an OPCODE_OP instruction whose funct7/funct3 hit one of the arms above, or an OPCODE_OP_IMM sext.b/sext.h, no trap; on RVFI decode rvfi_insn[31:25], [14:12], [6:0] (and [24:20] for sext.b/sext.h and for zext_h vs pack).
- Doc / spec per coverpoint:
  - cp_op: doc/03_reference/instruction_decode_execute.rst:67-89 (RV32B OTEarlGrey; Zba, Zbb single-cycle); tools/specs/riscv-isa-manual/src/unpriv/zb.adoc: sh1add :2197 ("shifts rs1 to the left by 1 bit and adds it to rs2"; sh2add :2273, sh3add :2370 sections), andn :102, orn :1394, xnor :2602, min :1253, minu :1306, max :1137, maxu :1200, sext.b :2104, sext.h :2150, zext.h :2790, pack :1464-1465 (lower halves, rs1 low, rs2 high), packh :1518 (least-significant bytes). packu has NO ratified sentence (it is the draft-0.92 addition, tools/specs/riscv-bitmanip changelog); the RTL is its definition: `{operand_b[31:16], operand_a[31:16]}` (alu:565).
  - cp_rs1_class (incl. e0000000, byte_msb, half_msb), cp_rs2_class, cp_sign_pair, cp_eq_operands, cp_same_regs, cp_rd_x0, cp_result_class: TB partitions of the RVFI fields listed in section 0; for min/max the sign pair is the pair the signed compare consumes (alu:123-126, :138-140).
  - cp_wrap (carry out of rs2 + (rs1 << n), shNadd only): the RTL adder takes the 32-bit TRUNCATED shifted operand (bits 31..32-n of rs1 fall off, alu:87-89) and the carry of the 33-bit sum is internal only (adder_result_ext_o[33] never leaves the ALU, :105-107); RVFI shows the 32-bit result. The TB must compute the carry as `((rs1 << n) mod 2^32) + rs2 >= 2^32` from rvfi_rs1_rdata / rvfi_rs2_rdata, which equals the RTL's carry; a formula using the full 33..35-bit product of the shift would not.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - zext_h vs pack: the same ALU operator and result (decoder :1282 maps both to ALU_PACK; with rs2 = x0 the upper half is zero, alu:567); only the rs2 index (rvfi_insn[24:20] == 0 / rvfi_rs2_addr == 0) separates the bins, as the plan already states.
  - sext_b / sext_h: rvfi_rs2_rdata and rvfi_rs2_addr are 0 (rf_ren_b = 0 for OP-IMM, core:2308): cp_rs2_class, cp_eq_operands and the rs2-based same_regs bins are meaningless for them; the plan's ignore clauses cover the crosses, the coverpoints themselves still sample `zero`.
  - cp_result_class on rd_x0 records is forced `zero` (core:2344-2346), as in section 1.
  - The internal carry / compare flags (is_greater_equal, adder carry) are not exported; every wrap/sign bin is recomputed from operands.

## 3. CG-ISA-002 gen_cg_isa_alu_reg (gen_fcov_plan.md:325)

- Observation point: RVFI retirement, condition decoded opcode OP, funct7 in {0000000, 0100000}, funct3 in {000,010,011,100,110,111}, rvfi_trap == 0 (shifts, M and Zb* excluded).
- RTL signal chain: rtl/ibex_decoder.sv:1252-1258 (`{0000000,000}` add, `{0100000,000}` sub, `{0000000,010}` slt, `{0000000,011}` sltu, `{0000000,100}` xor, `{0000000,110}` or, `{0000000,111}` and); shifts are :1259-1261 (excluded). rtl/ibex_alu.sv: add/sub through the shared adder with operand_b negated for SUB (:62, :86-107, :1329-1332); slt/sltu through the compare (cmp_signed for SLT :123-124; is_greater_equal :132-140; cmp_result = ~is_greater_equal :166-167; result `{31'h0, cmp_result}` :1350); xor/or/and through bwlogic (:388-389, :1326).
- Sampling condition in RTL terms: the WB write of an OPCODE_OP instruction with funct7 0000000 (or 0100000 with funct3 000) and funct3 not 001/101, no trap.
- Doc / spec per coverpoint:
  - cp_op: doc/03_reference/instruction_decode_execute.rst:53-66 (the execute block: ALU, adder shared with mult/div); tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc:344-351 (add :344, sub :345, "overflows are ignored and the low XLEN bits of results are written" :346, slt/sltu :347, and/or/xor :351).
  - cp_rs1_class, cp_rs2_class, cp_sign_pair, cp_eq_operands, cp_same_regs, cp_rd_x0, cp_result_class: TB partitions of the section-0 fields; for slt/sltu the sign pair is what the compare consumes (alu:123-140).
  - cp_wrap (add_carry, add_pos_ovf, add_neg_ovf, sub_borrow, sub_ovf): the 33-bit carry exists only inside the ALU (adder_result_ext_o, :105-107) and is discarded (:107 takes [32:1]); RVFI shows the 32-bit result, so every wrap bin is recomputed from rvfi_rs1_rdata / rvfi_rs2_rdata / rvfi_rd_wdata as the plan's formulas say. rv32.adoc:346 is the sentence that makes "ignored overflow" the expected behaviour.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - slt/sltu results: result_o is 0/1 only (:1350), so cp_result_class for slt/sltu can hit only `zero` and `one`; the plan's cr_slt_boundary is on operand classes, consistent.
  - cp_result_class on rd_x0 records is forced `zero` (core:2344-2346).
  - The compare's internal is_equal / is_greater_equal are not exported (cp_eq_operands is recomputed from the operands: same value as alu:132 is_equal for sub-based compare).

## 4. CG-CMP-006 gen_cg_cmp_zcmp_pushpop (gen_fcov_plan.md:699)

- Observation point: the RVFI record with rvfi_ext_expanded_insn_last == 1 of a cm.push / cm.pop / cm.popret / cm.popretz whose whole micro-op sequence retired without trap; the monitor collects every micro-op since the first rvfi_ext_expanded_insn_valid at this pc.
- RTL signal chain (rtl/ibex_compressed_decoder.sv): the 16-bit instruction is recognised at instr_i[15:13] = 101, [1:0] = 10 with [12:8] = 11000 push (:624), 11010 pop / 11100 popretz / 11110 popret (:687-689, tail selection :747-748); the state machine issues one 32-bit micro-op per ID handoff: push = stores `sw x_top, -4*k(sp)` (first with sp_offset 1 :634, then CmPushStoreReg :660) then `addi sp, sp, -stack_adj` as INSTR_EXPANDED_LAST (:673-679); pop family = loads `lw x_top, 4*(adj_words-1-k)(sp)` (:700-725) then `addi sp, sp, +stack_adj` (COMMIT, or LAST for cm.pop, :738-753), `li a0, 0` (COMMIT, popretz only, :757-762), `jalr x0, 0(ra)` (LAST, :764-770). Register order: cm_rlist_top_reg (:68-78) maps rlist 16 -> x27, 15 -> x26, ..., 7 -> x18, 6 -> x9, 5 -> x8, 4 -> x1, and rlist decrements per micro-op, so the highest-numbered register is stored first at sp-4, ra last at sp-4N (cm_push_store_reg :81-98, cm_pop_load_reg :99-108); rlist field 15 becomes internal 16 for x26+x27 (cm_rlist_init :167-176). stack_adj = stack_adj_base(rlist) + spimm*16 (:44-57; base 16/32/48/64 for rlist 4-7/8-11/12-14/15), the sp addi immediate comes from cm_sp_addi(instr_i[7:4], instr_i[3:2]) (:110-128). RVFI export: rtl/ibex_core.sv:2263-2280 (micro-op word in rvfi_insn, 16-bit source in rvfi_ext_expanded_insn, last flag), and the fetch hold that makes every non-last micro-op report pc_wdata == pc_rdata (rtl/ibex_if_stage.sv:809-810, gen_t102_rtl_facts.md R9).
- Sampling condition in RTL terms: the WB retirement of the INSTR_EXPANDED_LAST micro-op (id_stage:1218-1220 is also what makes minstret count once), with no trap on any micro-op of the same pc; a trapping micro-op (WB store/load error) flushes the rest and the sequence restarts from its first micro-op after mret (R9), which belongs to CG-CMP-008.
- Doc / spec per coverpoint:
  - cp_insn, cp_rlist, cp_spimm, cp_stack_adj: doc/01_overview/compliance.rst:58 (Zcmp supported); tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:392-450 (reg_list per rlist 4..15, `stack_adj = stack_adj_base + spimm * 16`, RV32I stack_adj_base 16/32/48/64 and the valid stack_adj values 16..112), :130 (spimm adds 16-byte increments), :135 (rlist 15 = ra, s0-s11: s10 without s11 does not exist), :385 (rlist 0..3 reserved). RTL: :44-57, :167-176.
  - cp_order_ok: zcmp.adoc:530-531 and :723 (`for(i in 27,26,...,18,9,8,1)`, addresses descending from sp) is the spec order; the RTL order is the same (cm_rlist_top_reg :68-78 with the decrementing rlist).
  - cp_uop_count_ok: N + 1 (push, pop), N + 2 (popret), N + 3 (popretz) from the state list above (:626-770).
  - cp_rvfi_tags_ok: rtl/ibex_core.sv:2270-2280 (valid on all micro-ops, last only on the final), pc_wdata == pc_rdata on non-last micro-ops (if_stage:809-810), rvfi_insn == the synthesized word (:2267).
  - cp_minstret_once: minstret increments once per sequence because instr_perf_count_id excludes INSTR_EXPANDED / INSTR_EXPANDED_COMMIT micro-ops (rtl/ibex_id_stage.sv:1218-1220; rtl/ibex_wb_stage.sv:206-210; rtl/ibex_cs_registers.sv:1588).
  - cp_ret_align (popret/popretz): the `jalr x0, 0(ra)` micro-op (cm_ret_ra :143-150) reports ra in rvfi_rs1_rdata (rf_ren_a) and the RAW target in rvfi_pc_wdata (core:2084, B13: bit 0 kept), while the fetch clears bit 0 (if_stage:288) so the next record's pc_rdata is even: bins word/half/odd are readable from rvfi_rs1_rdata[1:0] of that micro-op.
  - cp_sp_align, cp_sp_wrap: sp before the instruction = rvfi_rs1_rdata of the FIRST store/load micro-op (base x2, rf_ren_a); a misaligned sp splits every access in the LSU (rtl/ibex_load_store_unit.sv:468-486 split_misaligned_access) and is counted once by NumLoads/NumStores (D6).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - cp_minstret_once: minstret is NOT on RVFI (core:173-174 export mcycle and mhpmcounter3..12 only). Observable substitutes: rvfi_ext_mhpmcounters[7] = mhpmcounter10 NumInstrRetC (core:2122), which also increments once per Zcmp instruction (same instr_perf_count_id gate plus the compressed flag), or a csrr minstret in the test program. Flag: as written, the bin needs a CSR model or a csrr, not the RVFI record.
  - cp_dummy_en: dummy instructions produce no RVFI record (core:1864 gates valid with ~dummy_instr_id) and cpuctrlsts is not exported; the TB can only know dummy_instr_en from its own CSR-write tracking (the plan says "TB CSR model": consistent, but it is not an RTL observation).
  - cp_dmem_delay: bus-side (dbus monitor), not on RVFI.
  - cm.pop vs cm.popret vs cm.popretz share the load micro-ops; only the tail (addi LAST vs COMMIT + jalr, plus li a0) and the 16-bit source word tell them apart: decode cp_insn from rvfi_ext_expanded_insn[12:8], never from the micro-op words.
  - rlist = 15 stores 13 registers (x27 down to x1) although the field says 15 (cm_rlist_init :167-176); cp_uop_count_ok must use N = 13 for r15, N = rlist - 3 otherwise.

## 5. CG-CMP-001 gen_cg_cmp_zca (gen_fcov_plan.md:612)

- Observation point: RVFI retirement, rvfi_trap == 0 and a decoded Zca instruction (rvfi_insn[1:0] != 11), or, for cp_insn32_straddle only, a 32-bit instruction (rvfi_insn[1:0] == 11).
- RTL signal chain: the compressed flag is `instr_i[1:0] != 2'b11` (rtl/ibex_compressed_decoder.sv:883), registered per instruction into ID (rtl/ibex_if_stage.sv:609) and used by RVFI to export the 16-bit word (rtl/ibex_core.sv:2263-2265). Decode arms (rtl/ibex_compressed_decoder.sv): c.addi4spn :235, c.lw :243, c.sw :260, c.addi/c.nop :357-358, c.jal/c.j :371-372, c.li :379, c.lui :386, c.addi16sp :396, c.srli/c.srai :408-409, c.andi :424, c.sub :432, c.xor :438, c.or :444, c.and :450, c.beqz :534, c.bnez :535, c.slli :555, c.lwsp :568, c.mv :589, c.jr :593, c.add :599, c.ebreak :604, c.jalr :607, c.swsp :848; each expands to the 32-bit form the comment names, and the ID stage executes the expansion (doc/03_reference/instruction_fetch.rst:22). Alignment: the IF stage handles word- and half-word-aligned fetch (doc/03_reference/instruction_fetch.rst:79); a 32-bit instruction at pc[1] == 1 is assembled from two fetch words (rtl/ibex_fetch_fifo.sv:86-107 rdata_unaligned / valid_unaligned) and a bus error on its second half is flagged err_plus2 (:99-102; rtl/ibex_if_stage.sv:434; doc/03_reference/icache.rst:276-277).
- Sampling condition in RTL terms: the WB retirement of an instruction whose registered compressed flag is 1 (instr_is_compressed_id), no trap; on RVFI rvfi_insn[1:0] != 11 AND rvfi_ext_expanded_insn_valid == 0 (see the first flag below).
- Doc / spec per coverpoint:
  - cp_insn: the expansion comments above are the semantics the RTL implements; tools/specs/riscv-isa-manual/src/unpriv/zca.adoc is the reference (formats :165-172, :215-216, :240; stack-pointer loads/stores :269-308; c.lui :473-483; c.addi16sp :510-514).
  - cp_pc_align: rvfi_pc_rdata[1] = pc_id[1] (core:2083); instruction_fetch.rst:79.
  - cp_next_len: the next record's rvfi_insn[1:0] (TB ordering; no RTL state).
  - cp_pc_inc (non-CTI, 16-bit): rvfi_pc_wdata = pc_if = pc + 2 (core:2084 with pc_set = 0; the IF holds the sequential successor).
  - cp_insn32_straddle: rvfi_pc_rdata[1] of a 32-bit record; the RTL path is fetch_fifo:86-107 and the err_plus2 marker (:99-102, icache.rst:276-277).
  - cp_reg3, cp_rd_full: the 3-bit fields expand to x8..x15 by `{2'b01, field}` in every CIW/CL/CS/CA/CB arm (e.g. :235-246); the 5-bit fields pass through (CI/CR/CSS arms). Encoding constraints: c.addi16sp has rd = x2 by definition and shares the c.lui opcode (zca.adoc:510-514), c.lui is valid only with rd != x2 (rd = x2 is c.addi16sp; rd = x0 with imm != 0 is a HINT) (zca.adoc:477-483).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - A Zcmp micro-op record has rvfi_insn[1:0] == 11 (the synthesized 32-bit word) although the retired instruction is 16-bit: cp_insn32_straddle and cp_next_len must exclude records with rvfi_ext_expanded_insn_valid = 1, otherwise every cm.* micro-op counts as a 32-bit instruction (and the sequence's pc[1] as a straddle).
  - c.nop vs c.addi: the same decoder arm (:357-358); c.nop is c.addi with rd = x0 and imm = 0, distinguishable only by the encoding bits. The same holds for the HINT encodings of c.li, c.lui, c.mv, c.add (rd = x0, :380, :387, :590, :600), which retire as ordinary records with rd_x0 = yes and rd_wdata = 0: the plan's cp_insn bins include them unless the TB excludes rd = x0 encodings.
  - c.jal vs c.j and c.jr vs c.jalr: one arm each (:371-372, :593/:607), distinguished by bits; their pc_wdata is the raw branch target (B13 bit-0 caveat applies to c.jr/c.jalr).
  - c.ebreak (:604) is a trap record (rvfi_trap = 1) and never samples here by the plan's condition; it is the only Zca encoding that cannot appear in cp_insn.
  - The two halves of a straddling 32-bit instruction are not separately visible on RVFI; only pc_rdata[1] and (on a fetch error) rvfi_trap with mtval = pc + 2 (rtl/ibex_controller.sv:859-861, D10) reveal the straddle.

## 6. CG-BIT-002 gen_cg_bit_count (gen_fcov_plan.md:830)

- Observation point: RVFI retirement, condition decoded clz/ctz/cpop (OP-IMM funct3 001, instr[31:20] 0x600/0x601/0x602), rvfi_trap == 0.
- RTL signal chain: rtl/ibex_decoder.sv:1103-1105 (OP-IMM funct3 001 with funct7 0110000 and rs2 field 00000/00001/00010 -> ALU_CLZ / ALU_CTZ / ALU_CPOP; unary, rf_ren_b = 0). rtl/ibex_alu.sv:424-438 bit-count tree (bitcnt_ctz / bitcnt_clz select the direction, bitcnt_result = bitcnt_partial[31], 6 bits wide), result `{26'h0, bitcnt_result}` (:1357-1358).
- Sampling condition in RTL terms: the WB write of an OPCODE_OP_IMM instruction with funct3 001 and instr[31:20] in {0x600, 0x601, 0x602}, no trap.
- Doc / spec per coverpoint:
  - cp_op: doc/03_reference/instruction_decode_execute.rst:67-89 (Zbb in OTEarlGrey, single cycle); tools/specs/riscv-isa-manual/src/unpriv/zb.adoc clz :804 ("counts the number of 0's before the first 1, starting at the most-significant bit ... if the input is 0, the output is XLEN"), ctz :1026 (same from bit 0), cpop :914 ("counts the number of 1's").
  - cp_operand, cp_single_pos: TB partitions of rvfi_rs1_rdata (the ALU operand_a).
  - cp_result: rvfi_rd_wdata = the 6-bit count zero-extended (alu:1357-1358): r0..r32 only; values above 32 are unreachable by construction.
  - cp_rd_x0: rvfi_rd_addr.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - cp_result on rd_x0 records is forced `zero` (core:2344-2346): cr_op_result x rd_x0 = yes would always be r0.
  - rvfi_rs2_rdata / rvfi_rs2_addr are 0 for these unary ops (core:2308); nothing in the plan uses rs2 here, stated for completeness.
  - clz and ctz of operand 0 both give 32 and cpop of 0 gives 0: r32 is reachable only through zero for clz/ctz, r0 only through zero for cpop and through a set-bit-31 operand (clz) / set-bit-0 operand (ctz) otherwise; the plan's cr_op_result bins that contradict this (e.g. cpop/r32 needs all_ones) are TB arithmetic, not RTL ambiguity.

## 7. CG-MUL-003 gen_cg_div_ops (gen_fcov_plan.md:553)

- Observation point: RVFI retirement, condition decoded OP funct7 0000001 funct3 100..111, rvfi_trap == 0.
- RTL signal chain: rtl/ibex_decoder.sv:673-690 (div: MD_OP_DIV signed 2'b11 :673-676; divu: MD_OP_DIV 2'b00 :678-681; rem: MD_OP_REM 2'b11 :683-686; remu: MD_OP_REM 2'b00 :688-691) with div_sel_o (:1373-1377). rtl/ibex_multdiv_fast.sv divider: states MD_IDLE, MD_ABS_A, MD_ABS_B, MD_COMP, MD_LAST, MD_CHANGE_SIGN, MD_FINISH (:91); in MD_IDLE the divide-by-zero result is preloaded (`op_remainder_d = '1` for DIV, `{2'b0, op_a_i}` for REM, :427-434) and the FSM goes straight to MD_FINISH when equal_to_zero_i and data_ind_timing is off, else through the 32-step long division (:434, :445, :477-480); signs: div_sign_a = op_a[31] & signed_mode[0], div_sign_b = op_b[31] & signed_mode[1] (:406-407), quotient sign flipped when the signs differ and the divisor is not zero (:408), remainder takes the dividend's sign (:409, :502-508); result = imd_val_q_i[0] through multdiv_result_o (:136); div_valid in MD_FINISH (:514-517, valid_o :529). The int_min / -1 overflow needs no special case: the absolute-value path (:453-471 through the ALU adder) and the sign flip produce int_min and remainder 0 arithmetically.
- Sampling condition in RTL terms: the WB write of an OPCODE_OP instruction with funct7 0000001 and funct3[2] == 1 (div_sel_o = 1), no trap; on RVFI rvfi_insn[6:0] == 0110011, [31:25] == 0000001, [14] == 1.
- Doc / spec per coverpoint:
  - cp_op: doc/03_reference/instruction_decode_execute.rst:146-149 (long division, 37 cycles, 2 cycles on divide by zero); tools/specs/riscv-isa-manual/src/unpriv/m-st-ext.adoc:64-67 (div/divu signed/unsigned division; rem/remu remainder with the sign of the dividend), :71-72 (dividend = divisor x quotient + remainder except overflow).
  - cp_dividend, cp_divisor, cp_sign_pair: TB partitions of rvfi_rs1_rdata / rvfi_rs2_rdata; bit 31 of each is the divider's own div_sign_a / div_sign_b when the signed_mode bit is set (:406-407). eq_dividend and abs_gt_dividend are TB comparisons of the two operands.
  - cp_result_class, cr_div0, cr_overflow: m-st-ext.adoc:90-96 (quotient of division by zero has all bits set :91-92; remainder of division by zero equals the dividend :92; signed overflow only for int_min / -1, quotient int_min, remainder 0 :93-96), and the table at :99. RTL: :427-434 (zero preload), :408 (no sign flip on divide by zero).
  - cp_rd_x0: rvfi_rd_addr.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - The divide-by-zero fast path (2 cycles, MD_IDLE -> MD_FINISH) and the full 37-cycle path give the same architectural result; RVFI cannot tell which path ran (that is CG-MUL-004's timing domain, and data_ind_timing forces the long path for divide by zero: :434, :445).
  - cp_result_class on rd_x0 records is forced `zero` (core:2344-2346), so e.g. div-by-zero's all_ones result is unobservable when rd = x0.
  - With signed operands the divider works on absolute values (:453-471); only the final architectural result is exported, none of the intermediate quotient/remainder state.

## 8. CG-CMP-007 gen_cg_cmp_zcmp_mv (gen_fcov_plan.md:726)

- Observation point: RVFI retirement with rvfi_ext_expanded_insn_last == 1 whose 16-bit source decodes as cm.mvsa01 / cm.mva01s, both micro-ops collected since the first rvfi_ext_expanded_insn_valid at this pc.
- RTL signal chain (rtl/ibex_compressed_decoder.sv): the 16-bit instruction is [15:13] = 101, [12:10] = 011, [1:0] = 10 with [6:5] = 01 for cm.mvsa01 (:780-800) and 11 for cm.mva01s (:808-828); each expands to two `addi dst, src, 0` micro-ops built by cm_mv_reg (:129-138): cm.mvsa01 first `a0 -> r1s'` (cm_mvsa01(a01 = 0, rs = instr[9:7]) :153-159, tagged INSTR_EXPANDED_COMMIT :783-790) then `a1 -> r2s'` (a01 = 1, rs = instr[4:2], INSTR_EXPANDED_LAST :793-800); cm.mva01s first `r1s' -> a0` (cm_mva01s(rs = instr[9:7], a01 = 0) :160-166, COMMIT :811-818) then `r2s' -> a1` (LAST :821-828). The sreg mapping is `{(rs[2:1] > 0), (rs[2:1] == 0), rs}` (:157): s0/s1 -> x8/x9, s2..s7 -> x18..x23. No interrupt is taken between the two micro-ops (handle_irq excludes INSTR_EXPANDED_COMMIT, rtl/ibex_controller.sv:498-500) and no debug entry (:474-477); RVFI export as in section 0 (:2263-2280).
- Sampling condition in RTL terms: the WB retirement of the LAST micro-op with the COMMIT micro-op retired immediately before it (same pc), no trap; the moves cannot trap (addi), so the only way the pair does not complete is a fetch-side or asynchronous event before the COMMIT micro-op retires.
- Doc / spec per coverpoint:
  - cp_insn, cp_r1s, cp_r2s: tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1174 ("moves a0 into r1s' and a1 into r2s'. r1s' and r2s' must be different"), :1175 (the execution is atomic), :1163 (norm:cm-mvsa01_res: legal only when r1s' != r2s'), :1242 (cm.mva01s moves r1s' into a0 and r2s' into a1). RTL fields: instr[9:7] and instr[4:2] (:786, :795, :814, :823). Note: the RTL does not check r1s' != r2s' for cm.mvsa01 (no illegal_instr_o in the :780-800 arm); it executes two moves into the same sreg, the second winning: bug candidate B4 in the bug log, the plan ignores that cross bin.
  - cp_equal, cp_src_values: TB comparisons of the fields and of the first micro-op's rvfi_rs1_rdata pair (a0/a1 values are rvfi_rs1_rdata of the two micro-ops for mvsa01; r1s'/r2s' values likewise for mva01s).
  - cp_b2b, cp_hazard_src: TB ordering over neighbouring records; RTL forwarding makes a preceding ALU or load writer visible in the move's rvfi_rs1_rdata (core:2304-2310 captures the forwarded value).
  - cp_uop_count_ok: exactly two records with the same pc, first with _last = 0, second with _last = 1 (:790, :800, :818, :828).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - "COMMIT-equivalent" is not a tag on RVFI: rvfi_ext_expanded_insn_valid / _last do not export INSTR_EXPANDED_COMMIT, so cp_uop_count_ok can only check the count and the last flag; the no-interrupt property is what the RTL gate guarantees (controller:498-500), the TB observes it as "no intr record between the two".
  - r1s' == r2s' for cm.mvsa01 is executed, not refused (B4): a bin expecting a trap there would never hit; the plan's ignore is right.
  - The two moves retire as two separate records with rvfi_pc_wdata == rvfi_pc_rdata on the first (R9); a TB that expects one record per instruction sees a duplicate pc.

## 9. CG-CSR-002 gen_cg_csr_trap_setup_warl (gen_fcov_plan.md:1199)

- Observation point: the TB checker's write/read-back pair for mstatus, misa, mie, mtvec, mcounteren, mstatush, menvcfg, menvcfgh: the write record (csrrw/s/c[i], rvfi_trap == 0) followed by the read-back record of the same CSR. On RVFI the written value is rvfi_rs1_rdata (register forms) or the zimm in rvfi_insn[19:15] (immediate forms), the old value is the write record's rvfi_rd_wdata (rd != x0), the legalised value is the read-back record's rvfi_rd_wdata.
- RTL signal chain (rtl/ibex_cs_registers.sv): write enables per CSR in the write case (:786-880: CSR_MIE :790, CSR_MTVEC :807, CSR_MCOUNTEREN :845; mstatus :774-787); legalisation: mstatus keeps only MIE, MPIE, MPP, MPRV, TW and forces MPP to U when not M/U (:774-787); mtvec takes csr_wdata[31:8] as base and forces [7:2] = 0 and mode = 01 (:739-743, read :469-475, doc cs_registers.rst:180-188); mie takes exactly the software (3), timer (7), external (11) and fast (16..30) bits (:1103-1106); mcounteren is written only when mcounteren_writable_i == IbexMuBiOn (:845), keeps bits [MHPMCounterNum+2:0] with bit 1 forced 0 (:1563-1571), reads back mcounteren (:464); misa is hard-wired (read :452, misa_value_masked :377, no write case, doc cs_registers.rst:145-146); mstatush and menvcfg/menvcfgh read 0 (:445, :449) and have no write case (a write is legal and ignored). Reads of mstatus compose the same five fields (:435-442).
- Sampling condition in RTL terms: a CSR write retires when csr_access with a write op reaches WB without illegal_csr (csr_op_en; the M-mode program has the privilege); the read-back is the next csrr of the same address. The RVFI record of the write carries the instruction (rvfi_insn), the source (rvfi_rs1_rdata for csrrw/s/c, zimm for the i-forms) and the returned old value (rvfi_rd_wdata when rd != x0).
- Doc / spec per coverpoint:
  - cp_csr, cp_op, cp_wpat, cp_rd: doc/03_reference/cs_registers.rst:13-17 (the WARL table); the CSR instruction forms are tools/specs/riscv-isa-manual/src/unpriv (Zicsr chapter).
  - cp_mpp_w, cp_mst_*_w: cs_registers.rst mstatus section (fields MIE, MPIE, MPP, MPRV, TW); RTL :774-787 (MPP legalisation to U, mstatus read :435-442); gen_t102_rtl_facts.md R7 (SD/XS/FS read 0).
  - cp_mtvec_mode_w, cp_mtvec_lo_w, cp_mtvec_base_w: cs_registers.rst:180-188 ("mtvec[7:2] is always set to 6'b0", "MODE: always 2'b01 vectored, read-only"); RTL :739-743; boot_page = the reset value {boot_addr_i[31:8], 8'h01} (:739-741 with csr_mtvec_init).
  - cp_mie_w: cs_registers.rst:149-172 (bits 30:16 fast, 11 MEIE, 7 MTIE, 3 MSIE; all others read 0); RTL :1103-1106.
  - cp_mcen_gate, cp_mcen_w: doc/03_reference/performance_counters.rst:66-77 (mcounteren gates U-mode counter aliases; lockable by the MUBI input mcounteren_writeable); RTL :845 (write only when the input is IbexMuBiOn: any other encoding, including the invalid ones, behaves as locked), :1563-1571 (bits 0 and 2..MHPMCounterNum+2 writable, bit 1 always 0, bits above read 0). The input is a DUT port (dv/auto_dv/tb/gen_dut_top.sv:198, :390), so cp_mcen_gate is the TB's drive value at the write, not an RTL observation.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - RVFI exports no CSR state: the legalised value is visible only through the read-back record's rvfi_rd_wdata (rd != x0), so a pair whose read-back uses rd = x0 samples nothing (rd_wdata forced 0, core:2344-2346).
  - cp_mtvec_mode_w r10/r11 and cp_mtvec_lo_w nonzero: the written bits are dropped (:739-743); the read-back always shows mode 01 and [7:2] = 0, so these bins prove the WARL drop, not a stored value.
  - cp_mcen_gate invalid vs off: identical RTL behaviour (:845 compares against IbexMuBiOn only); only the TB's drive distinguishes them.
  - misa, mstatush, menvcfg, menvcfgh writes: no RTL state changes and no trap; the read-back equals the constant. A bin expecting an illegal-instruction trap on these writes would never hit.
  - The write record's rvfi_rd_wdata is the OLD value only when rd != x0 (cp_rd = x0 loses it); for csrrs/csrrc with rs1 = x0 the RTL performs no write (csr_op_en gated by rs1 != x0 for the register forms, id_stage csr_op decode), so those pairs are read-only pairs, not write pairs.

## 10. CG-ISA-007 gen_cg_isa_branch (gen_fcov_plan.md:419)

- Observation point: RVFI retirement, condition decoded BRANCH (funct3 not 010/011) or c.beqz/c.bnez, rvfi_trap == 0; taken derived from rvfi_pc_wdata != pc + len.
- RTL signal chain: rtl/ibex_decoder.sv:372-384 (OPCODE_BRANCH, branch_in_dec_o; funct3 010/011 illegal and cleared by the override :905-918) and :996-1004 (funct3 -> ALU_EQ / NE / LT / GE / LTU / GEU); c.beqz / c.bnez expand to `beq / bne rs1', x0, imm` (rtl/ibex_compressed_decoder.sv:534-535). Decision: rtl/ibex_alu.sv compare (:132-140 is_equal / is_greater_equal; :161-167 cmp_result per operator) -> branch_decision_o (rtl/ibex_ex_block.sv:92) -> branch_set (rtl/ibex_id_stage.sv:928, :815). Target: the branch-target ALU adds pc_id and imm_b (rtl/ibex_id_stage.sv:374, :383; rtl/ibex_ex_block.sv:95-101), its 33rd bit discarded (:99-100 unused_bt_carry); pc_set in the controller (rtl/ibex_controller.sv:681-687). RVFI: pc_wdata = branch_target_ex when pc_set else pc_if (core:2084), pc_rdata = pc_id (:2083); operands as in section 0 (:2304-2310).
- Sampling condition in RTL terms: the WB retirement of an instruction whose decoder set branch_in_dec_o, no trap (a branch itself traps only on a fetch-side fault, which excludes it). Taken on RVFI: rvfi_pc_wdata != rvfi_pc_rdata + (rvfi_insn[1:0] == 11 ? 4 : 2), which is exactly `pc_set` at the capture (the not-taken record carries pc_if = the sequential successor).
- Doc / spec per coverpoint:
  - cp_op: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc:539-544 (beq/bne :540; blt/bltu :541-542; bge/bgeu :543-544), :174 (offsets in multiples of 2); doc/03_reference/instruction_decode_execute.rst:32, :63 (branch target = PC + Imm in the ID/EX stage).
  - cp_taken: rv32.adoc:540-544; RTL branch_decision_o (ex_block:92) is the sampled outcome; core:2084.
  - cp_cmp_class: TB partitions of rvfi_rs1_rdata / rvfi_rs2_rdata; for c.beqz / c.bnez rs2 is x0 and rvfi_rs2_rdata is 0 (the decoder reads x0 through rf_ren_b; the value is 0 by the register file).
  - cp_offset: sext(imm_b) from rvfi_insn (the TB decodes it; the RTL's imm_b_type is id_stage:274, :421); for c.b* the 9-bit offset (compressed_decoder:534-535 expansion).
  - cp_target_align: target[1] = rvfi_pc_wdata[1] on a taken branch (branch targets are always even: imm_b is a multiple of 2, so bit 0 is never set; only bit 1 varies).
  - cp_wrap (carry out of pc + imm, taken): the adder's carry is discarded (ex_block:99-100); recompute from rvfi_pc_rdata and the decoded immediate.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - A not-taken branch leaves no trace in the RTL beyond the record itself: pc_wdata = pc_if = pc + len (core:2084 with pc_set = 0), identical to any other sequential instruction; the TB derives "not taken" from that equality, as the plan says.
  - c_beqz / c_bnez vs beq / bne: one decoder arm after expansion; only the 16-bit rvfi_insn distinguishes them (core:2263-2265).
  - The compare's internal flags (is_equal, is_greater_equal) are not exported; cp_cmp_class is recomputed from the operands, and the sampled outcome (cp_taken) is the only RTL-side confirmation.
  - Under data_ind_timing = 1 every branch takes two cycles and the not-taken path also asserts branch_set with the pc + len target (id_stage:928, :819-831): on RVFI the record is unchanged (pc_wdata = pc + len), so this group cannot see DIT; CG-BTALU-001 owns that (and B11 for the NumBranchesTaken counter).

## 11. CG-ISA-001 gen_cg_isa_alu_imm (gen_fcov_plan.md:306)

- Observation point: RVFI retirement, condition decoded OP-IMM with funct3 in {000,010,011,100,110,111}, rvfi_trap == 0 (shifts 001/101 excluded).
- RTL signal chain: rtl/ibex_decoder.sv:1081-1086 (OP-IMM funct3 -> ALU_ADD / ALU_SLT / ALU_SLTU / ALU_XOR / ALU_OR / ALU_AND); operand b is the sign-extended I-immediate (rtl/ibex_id_stage.sv:440 `alu_operand_b = (alu_op_b_mux_sel == OP_B_IMM) ? imm_b : rf_rdata_b_fwd`, imm_i_type); ALU datapath as in section 3 (adder :86-107 and :1329-1332, compare :123-140 and :1350, bwlogic :388-389 and :1326). rs2 is not read (rf_ren_b = 0), so rvfi_rs2_rdata = 0 and rvfi_rs2_addr = 0 (core:2308).
- Sampling condition in RTL terms: the WB write of an OPCODE_OP_IMM instruction whose funct3 is not 001/101, no trap; on RVFI rvfi_insn[6:0] == 0010011 and rvfi_insn[14:12] not in {001, 101}. The immediate is rvfi_insn[31:20] sign-extended (the RTL's imm_i_type).
- Doc / spec per coverpoint:
  - cp_op: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc:271 (addi adds the sign-extended 12-bit immediate), :275-278 (slti / sltiu), :283 (andi, ori, xori bitwise); doc/03_reference/instruction_decode_execute.rst:53-66 (ALU).
  - cp_rs1_class, cp_imm_class, cp_result_class, cp_rd_x0, cp_rs1_eq_rd: TB partitions of rvfi_rs1_rdata, rvfi_insn[31:20], rvfi_rd_wdata, rvfi_rd_addr, rvfi_rs1_addr.
  - cp_addi_wrap, cp_slt_case: recomputed from operands and result; the adder carry is internal (alu:105-107), rv32.adoc:346 ("overflows are ignored") is the expected behaviour; the slti/sltiu boundary bins follow rv32.adoc:275-282 (sltiu with imm = 1 is seqz; the immediate is sign-extended then treated as unsigned).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - cp_result_class on rd_x0 records is forced `zero` (core:2344-2346); addi rd = x0 encodings are HINTs/NOP (addi x0, x0, 0 is the canonical nop) and still retire as records.
  - slti/sltiu write 0/1 only (alu:1350): result classes other than zero/one are unreachable for them.
  - c.addi / c.li / c.andi / c.addi4spn / c.addi16sp arrive as OP-IMM expansions but carry the 16-bit word in rvfi_insn (core:2263-2265): this group's condition "decoded opcode == OP-IMM" only matches 32-bit encodings unless the TB also decodes the compressed forms (CG-CMP-001 owns those bins).

## 12. CG-ISA-003 gen_cg_isa_shift (gen_fcov_plan.md:349)

- Observation point: RVFI retirement, condition decoded slli/srli/srai (OP-IMM funct3 001/101, instr[31:25] in {0000000, 0100000}) or sll/srl/sra (OP funct7 0000000/0100000, funct3 001/101), rvfi_trap == 0.
- RTL signal chain: rtl/ibex_decoder.sv OP-IMM: slli `{0000000, 001}` -> ALU_SLL :1091, srli :1167 (RV32B configs) / :1192, srai :1168 / :1194; the same shift-space funct7 values carry the Zb encodings (bclri :1096, bseti :1097, binvi :1098, bexti :1173, rori :1175, and the legality block :503-551), which the plan's funct7 guard excludes; OP: sll/srl/sra :1259-1261. rtl/ibex_alu.sv shifter: the amount is operand_b_i[4:0] (:279-290), i.e. imm[4:0] or rs2[4:0], upper rs2 bits ignored; shift_result (:346-353) selected at :1335-1338; srai/sra sign-fill through the arithmetic path of the same shifter.
- Sampling condition in RTL terms: the WB write of an OPCODE_OP_IMM instruction with funct3 001 and funct7 0000000 (slli) or funct3 101 and funct7 0000000/0100000 (srli/srai), or an OPCODE_OP instruction with funct3 001/101 and funct7 0000000/0100000, no trap.
- Doc / spec per coverpoint:
  - cp_op: rv32.adoc:296-298 (slli/srli/srai definitions), :353-355 (sll/srl/sra, amount in the lower 5 bits of rs2); doc/03_reference/instruction_decode_execute.rst:53-66.
  - cp_shamt: rvfi_insn[24:20] for the immediate forms, rvfi_rs2_rdata[4:0] for the register forms (alu:279-290 uses exactly operand_b_i[4:0]).
  - cp_rs2_upper: rvfi_rs2_rdata[31:5] (register forms), ignored by the RTL (alu:279-290): the bins prove the ignore, not a datapath difference.
  - cp_operand, cp_result_class, cp_rd_x0: TB partitions of the section-0 fields.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - c.slli / c.srli / c.srai retire with the 16-bit word in rvfi_insn (core:2263-2265): a 32-bit-only decode of "OP-IMM 001/101" misses them (CG-CMP-001 owns their bins).
  - cp_result_class on rd_x0 records is forced `zero` (core:2344-2346).
  - The RTL treats rs2[31:5] identically for all values, so cp_rs2_upper bins are equivalence classes of an ignored field; is32 / is33 exist to prove the mask, and the result must equal the shamt = 0 / 1 result respectively.

## 13. CG-PMP-001 gen_cg_pmp_cfg_write (gen_fcov_plan.md:2396)

- Observation point: RVFI retirement of a CSR write (csrrw/s/c and immediate forms) to CSR_PMPCFG0..3, rvfi_trap == 0, not read-only; one sample per entry byte i = 4*idx + b; outcome from the read-back model (the following csrr).
- RTL signal chain (rtl/ibex_cs_registers.sv, g_pmp_csrs :1418-1490): per entry i, write enable `pmp_cfg_we[i] = csr_we_int & ~pmp_cfg_locked[i] & ~pmp_cfg_wr_suppress[i] & (csr_addr == PMPCFG(i/4))` (:1423-1426); `pmp_cfg_locked[i] = pmp_cfg[i].lock & ~mseccfg.rlb` (:1463); `pmp_cfg_wr_suppress[i] = mseccfg.mml & ~mseccfg.rlb & is_mml_m_exec_cfg(wdata)` (:1467-1469) where is_mml_m_exec_cfg is true for a LOCKED row with RWX in {001, 010, 011, 101} (:164-176). Field legalisation of the written byte (:1429-1446): L = bit 7; A: 00 OFF, 01 TOR, 10 NA4 (granularity 0, else OFF), 11 NAPOT; X = bit 2; W = bit 1 when mml, else bit 1 & bit 0 (R=0,W=1 forced to W=0) (:1444-1445); R = bit 0; bits 6:5 are dropped (no field) and read back as 00 (:1381). The read composes four bytes per word (:525-532). The write is a whole-word CSR write: the four entry bytes are legalised independently and each has its own enable, so a partly locked word updates only its unlocked bytes.
- Sampling condition in RTL terms: csr_we_int for the pmpcfg address (a csrrs/csrrc with rs1 = x0, or csrrsi/csrrci with uimm = 0, performs no write: read-only pair); the byte i is stored iff pmp_cfg_we[i]; the value stored is pmp_cfg_wdata[i] as legalised above. On RVFI the write record gives the instruction, the source value (rvfi_rs1_rdata or the zimm) and the old word (rvfi_rd_wdata, rd != x0); the outcome is only visible on the read-back record.
- Doc / spec per coverpoint:
  - cp_entry, cp_op: doc/03_reference/pmp.rst:16 (PMPGranularity 0), :37-38 (NA4 unavailable when G > 0); PMPNumRegions 16 (gen_param_resolution.md).
  - cp_wr_mode, cp_wr_lrwx, cp_res_bits: tools/specs/riscv-isa-manual/src/priv/machine.adoc:3406 (R/W/X collective WARL, R=0 W=1 reserved), :3539-3545 (L: writes to pmpicfg and pmpaddri ignored; TOR lock of pmpaddr(i-1)); RTL :1429-1447, :1381.
  - cp_mml, cp_rlb, cp_prelock, cp_outcome, cp_word_lockmix: tools/specs/riscv-isa-manual/src/priv/smepmp.adoc:68 (locked rules cannot be removed or modified unless mseccfg.RLB is set), :76 (MML/MMWP lock when set, RLB locks when cleared); doc/03_reference/pmp.rst:47-57 (Smepmp, mseccfg reset 0); RTL: the ignored_lock outcome is pmp_cfg_locked (:1463), ignored_mml_exec is pmp_cfg_wr_suppress (:1467-1469, :164-176), w_dropped is the W legalisation (:1444-1445), written is the remaining case. mseccfg itself: read :507-509, write :1502, RLB cannot be set while any entry is locked (:1505-1510).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - RVFI exports no CSR state: every cp_outcome bin is decided by the read-back model, and a read-back with rd = x0 shows nothing (core:2344-2346).
  - cp_res_bits nonzero: the bits are dropped on write and read as 00 (:1381), so nonzero can only be sampled from the write data, never from the stored value.
  - w_dropped vs written for RW = 01 under MML = 0: identical write enable; only the stored W differs (:1444-1445). The RTL never traps on any pmpcfg write pattern.
  - ignored_lock vs ignored_mml_exec: both leave the byte unchanged; the model must classify from the pre-write state (L, RLB, MML) and the written row, exactly the two terms of :1423-1426.
  - cp_prelock uses the PRE-write L: a write that sets L on an unlocked entry succeeds (the enable evaluates pmp_cfg[i].lock before the write, :1463), as the plan's setlock bins expect.

## 14. CG-BIT-006 gen_cg_bit_sbit (gen_fcov_plan.md:900)

- Observation point: RVFI retirement, condition decoded bclr/bset/binv/bext and their immediate forms, rvfi_trap == 0.
- RTL signal chain: rtl/ibex_decoder.sv OP: bclr `{0100100,001}` :1296, bset `{0010100,001}` :1297, binv `{0110100,001}` :1298, bext `{0100100,101}` :1299; OP-IMM: bclri :1096, bseti :1097, binvi :1098 (funct3 001 shift space), bexti :1173 (funct3 101), legality :503-551. rtl/ibex_alu.sv: the shifter builds the one-hot mask `1 << shamt` (:294 selects the single-bit path, :279-290 shamt = operand_b_i[4:0]), then bset = a | mask, bclr = a & ~mask, binv = a ^ mask, bext = {31'h0, (a >> shamt)[0]} (:582-588), selected in the result mux.
- Sampling condition in RTL terms: the WB write of an instruction decoded to ALU_BSET/BCLR/BINV/BEXT, no trap; on RVFI: OP with the funct7/funct3 pairs above, or OP-IMM with funct3 001 and rvfi_insn[31:27] in {01001 bclri, 00101 bseti, 01101 binvi} or funct3 101 and rvfi_insn[31:27] == 01001 (bexti).
- Doc / spec per coverpoint:
  - cp_op: tools/specs/riscv-isa-manual/src/unpriv/zb.adoc bclr :172, bclri :234, bext :284, bexti :346, binv :395, binvi :457, bset :506, bseti :568 (each "returns rs1 with a single bit cleared / set / inverted at the index specified in rs2 / shamt"; bext "returns a single bit extracted"); doc/03_reference/instruction_decode_execute.rst:67-89 (Zbs single cycle).
  - cp_index: rvfi_rs2_rdata[4:0] (register forms) or rvfi_insn[24:20] (immediate forms); alu:279-290.
  - cp_rs2_upper: rvfi_rs2_rdata[31:5], ignored by the RTL (only [4:0] reaches the shifter).
  - cp_prior_bit: rvfi_rs1_rdata[index] (TB computed); the RTL reads the same operand_a bit through the mask.
  - cp_operand, cp_rd_x0: section-0 fields. cp_binv_twice: TB ordering over two records (same rd and index).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - cp_rd_x0 = yes forces rvfi_rd_wdata to 0 (core:2344-2346): the effect of the bit op is unobservable on such a record; cp_prior_bit still samples from rs1.
  - bext's result is 0/1 only (alu:587); no operand class beyond the selected bit matters to the result.
  - cp_rs2_upper bins are equivalence classes of an ignored field (alu:279-290); they prove the mask, not a datapath difference.
  - bclri/bseti/binvi share the OP-IMM funct3 001 space with slli and the Zbb shift immediates; the decoder distinguishes them by instr[31:27] (:1091-1098); rvfi_insn carries the same bits, so the TB decode is exact.

## 15. CG-PMP-002 gen_cg_pmp_addr_write (gen_fcov_plan.md:2422)

- Observation point: RVFI retirement of a CSR write to CSR_PMPADDR0..15, rvfi_trap == 0, not read-only; outcome from the read-back model's pre-write lock state.
- RTL signal chain (rtl/ibex_cs_registers.sv): `pmp_addr_we[i] = csr_we_int & ~pmp_cfg_locked[i] & (~pmp_cfg_locked[i+1] | (pmp_cfg[i+1].mode != PMP_MODE_TOR)) & (csr_addr == PMPADDR(i))` for i < PMPNumRegions-1 (:1475-1477), and without the neighbour term for the top entry (:1479-1480); `pmp_cfg_locked[k] = pmp_cfg[k].lock & ~mseccfg.rlb` (:1463); the register holds all 32 written bits at PMPGranularity = 0 (PMPAddrWidth = 32, :183; wr_data csr_wdata_int[31-:PMPAddrWidth], :1490) and reads them back unmodified (:1385-1387, :533-548). The stored value is the physical address >> 2, so wdata[31:30] are physical address bits 33:32 and are stored regardless of the entry's A mode.
- Sampling condition in RTL terms: csr_we_int for a pmpaddr address (csrrs/csrrc with rs1 = x0 and the zero-uimm forms are reads); the write lands iff pmp_addr_we[i]; on RVFI the write record gives the instruction and source, the outcome is the read-back record's rvfi_rd_wdata.
- Doc / spec per coverpoint:
  - cp_idx, cp_op: PMPNumRegions 16; doc/03_reference/pmp.rst:16.
  - cp_self_lock, cp_next_cfg, cp_rlb, cp_outcome: tools/specs/riscv-isa-manual/src/priv/machine.adoc:3539-3545 ("if PMP entry i is locked, writes to pmpicfg and pmpaddri are ignored. Additionally, if PMP entry i is locked and pmpicfg.A is set to TOR, writes to pmpaddr(i-1) are ignored"); smepmp.adoc:68 (RLB lifts the locks); RTL :1475-1480, :1463. The top entry has no TOR neighbour (:1479-1480).
  - cp_hi_bits, cp_self_mode: the register stores bits 31:30 regardless of mode (:1385-1387, no mode masking at G = 0); doc/03_reference/pmp.rst:16, :37-38 (G = 0 keeps every address bit).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - RVFI exports no CSR state: written / ignored_self_lock / ignored_tor_lock are read-back-model outcomes; a read-back with rd = x0 shows nothing (core:2344-2346).
  - ignored_self_lock vs ignored_tor_lock: the same unchanged register; only the pre-write state (L of i, L and A of i+1, RLB) tells them apart, exactly the two terms of :1475-1477.
  - cp_self_mode has no RTL effect on the address write at G = 0 (:1385-1387): its bins prove the absence of masking; with G > 0 the read-back would mask low bits by mode (:1389-1407), unreachable in this configuration.
  - The RTL never traps on any pmpaddr write; a bin expecting an exception would not hit.

## 16. CG-CMP-005 gen_cg_cmp_zcb (gen_fcov_plan.md:680)

- Observation point: RVFI retirement, condition decoded Zcb instruction, rvfi_trap == 0; load sign and address alignment from rvfi_mem_addr / rvfi_mem_rdata.
- RTL signal chain (rtl/ibex_compressed_decoder.sv): c.lbu :270-274 (-> lbu rd', uimm(rs1')), c.lhu :278-282, c.lh :283-287, c.sb :295-300, c.sh :303-308; c.mul :464-467 (-> mul rsd', rsd', rs2'); c.zext.b :477-480 (-> andi rsd', rsd', 0xff), c.sext.b :483-486 (-> sext.b), c.zext.h :489-492 (-> zext.h = pack with x0), c.sext.h :495-498 (-> sext.h), c.not :506-509 (-> xori rsd', rsd', -1); all rd'/rs1'/rs2' fields expand to x8..x15 by `{2'b01, field}`. The expansion executes as the named 32-bit instruction (decoder/ALU/LSU/multiplier anchors of sections 1, 2 and 11); RVFI carries the 16-bit word (rtl/ibex_core.sv:2263-2265). Memory fields: rvfi_mem_addr = lsu_addr (:2209), rvfi_mem_wdata (:2210), rvfi_mem_rdata = rf_wdata_lsu, the ALREADY sign/zero-extended load result (:2224); masks :2085-2086 (rmask is not gated by a load, BUG-10). LSU: a half-word at offset 11 is split into two bus accesses (rtl/ibex_load_store_unit.sv:403-405 split_misaligned_access), offset 01 is one access with byte enables; sign or zero extension by data_sign_ext_q (:249, :287-290 for halves, the byte path follows).
- Sampling condition in RTL terms: the WB retirement of an instruction whose 16-bit word is a Zcb encoding (instr[1:0] = 00 with funct3 100 for the loads/stores, instr[15:10] = 100111 for the ALU forms and c.mul), no trap; on RVFI decode rvfi_insn[15:0].
- Doc / spec per coverpoint:
  - cp_insn: tools/specs/riscv-isa-manual/src/unpriv/zcb.adoc c.lbu :84, c.lhu :143, c.lh :204, c.sb :265, c.sh :326, c.zext.b :414, c.sext.b :474, c.zext.h :530, c.sext.h :587, c.not :677, c.mul :735; doc/01_overview/compliance.rst:54 (Zcb supported).
  - cp_uimm_b, cp_uimm_h: the immediate bits of the 16-bit word as the decoder assembles them (:271-274, :279-287, :296-308).
  - cp_data_sign: the loaded byte/half msb; on RVFI read rvfi_mem_rdata[7] (c.lbu) or [15] (c.lhu, c.lh), never rvfi_rd_wdata[31] for the unsigned forms (zero-extended, lsu:287-288).
  - cp_alu_operand: rvfi_rs1_rdata (rsd' is both source and destination for the ALU forms and c.mul, so rvfi_rs1_addr == rvfi_rd_addr).
  - cp_addr_align: rvfi_mem_addr[1:0] (:2209, the LSU address before splitting); mis3 = the split case (lsu:403-405).
  - cp_regs (c.mul): instr[9:7] vs instr[4:2] of the 16-bit word.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - The split half-word access (mis3) produces ONE record whose rvfi_mem_addr is the first (lower) address and whose data is the assembled half (lsu:403-405; rdata assembly in the LSU): the two bus beats are not visible on RVFI, only on the data bus.
  - rvfi_mem_rdata is the extended result, not the raw bus word (:2224): for c.lbu/c.lhu the upper bits are always 0, for c.lh they equal the sign; a TB that wants the raw bus data must take it from the bus monitor.
  - c.zext.b is an andi and c.not an xori in the RTL (:477-480, :506-509): no dedicated datapath; c.zext.h shares ALU_PACK with pack (section 2).
  - rd is never x0 for any Zcb form (x8..x15 by encoding), so no rd_x0 bins apply here.

## 17. CG-ISA-005 gen_cg_isa_hint_x0 (gen_fcov_plan.md:383)

- Observation point: RVFI retirement with rvfi_rd_addr == 0 of an instruction class that normally writes rd, rvfi_trap == 0; cp_x0_read from the next retirement's rs fields.
- RTL signal chain: the decoder does not special-case rd = x0: the instruction executes fully (ALU, multiplier, divider, LSU, CSR read) and asks for a register write; the register file discards it: x0 is not a storage element outside dummy instructions (rtl/ibex_register_file_ff.sv:144-173: rf_data[0] is WordZeroVal for a normal instruction :173, and the only write path into R0 is the dummy-instruction path we_data_r0 :158-161; without dummy instructions :189); reads of x0 return 0 through the same mux (:173, :189). RVFI: rvfi_rd_addr = 0 and rvfi_rd_wdata forced to 0 (rtl/ibex_core.sv:2344-2346). Retirement counting is unaffected (rtl/ibex_id_stage.sv:1218-1220 has no rd term; minstret and NumInstrRetC count HINTs).
- Sampling condition in RTL terms: the WB retirement of an instruction whose decoded rf_we is 1 and waddr is 0, no trap; on RVFI rvfi_rd_addr == 0 together with the instruction class decoded from rvfi_insn (the plan's list).
- Doc / spec per coverpoint:
  - cp_hint_class, cp_writer_class: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc:962-970 ("HINTs do not change any architecturally visible state, except for advancing the pc and any applicable performance counters"; "most RV32I HINTs are encoded as integer computational instructions with rd = x0"), :1008 (the HINT table, including the slli/srai x0 semihosting markers :1034-1036).
  - cp_x0_read: the next record with rvfi_rs1_addr == 0 or rvfi_rs2_addr == 0 shows rdata 0 (core:2305-2308 capture the operand the register file delivered; rtl/ibex_register_file_ff.sv:173/:189 makes it 0).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - The computed value of an rd = x0 instruction is never visible: rvfi_rd_wdata is forced 0 (core:2344-2346) and the register file drops the write, so cp_writer_class bins prove that the class retired with rd = x0, not what it computed; a load to x0 still performs the bus access and rvfi_mem_rdata (:2224) shows the data, the only observable side of such a HINT.
  - The Zcb ALU forms and c.mul cannot target x0 (rsd' in x8..x15), so zcb_alu is unreachable by encoding, as the plan says.
  - A csrr with rd = x0 is a csrrs x0, csr, x0: the RTL performs the CSR read (side effects of reading, none for these CSRs) and no write; it is a HINT-like record with rd_wdata 0.
  - Dummy instructions write the physical R0 (:158-161) but produce no RVFI record (core:1864) and never influence an RVFI-visible x0 read (:173 selects the dummy value only while dummy_instr_id is set, which is never true for a real instruction).

## 18. CG-CMP-002 gen_cg_cmp_imm_edges (gen_fcov_plan.md:630)

- Observation point: RVFI retirement of a Zca instruction with an immediate, rvfi_trap == 0; each coverpoint guarded to its format.
- RTL signal chain (rtl/ibex_compressed_decoder.sv, the immediate is assembled into the 32-bit expansion): c.addi4spn :235-241 (nzuimm[9:2] scaled by 4), c.lw/c.sw :243-266 (uimm[6:2] scaled by 4), c.lwsp/c.swsp :568-575 / :848-853 (uimm[7:2] scaled by 4), c.addi/c.nop :357-365 and c.li :379-383 (sext imm6), c.lui :386-389 (nzimm[17:12]), c.addi16sp :396-402 (nzimm scaled by 16), c.srli/c.srai :408-418 and c.slli :555-560 (shamt[4:0]), c.andi :424-428 (sext imm6), c.j/c.jal :371-377 (sext imm[11:1]), c.beqz/c.bnez :534-545 (sext imm[8:1]). The expansion then executes through the ID/EX anchors of sections 3, 10, 11, 12 and 20; the link value of c.jal/c.jalr is pc + 2 because the main ALU adds imm_b = IMM_B_INCR_PC, which is 2 for a compressed instruction (rtl/ibex_id_stage.sv:396 (BranchTargetALU generate; :424 in the other generate)), to pc_id (:363).
- Sampling condition in RTL terms: the WB retirement of a compressed instruction (instr_is_compressed_id) of the named format, no trap; on RVFI the immediate is re-decoded from rvfi_insn[15:0] (core:2263-2265); the RTL exports no immediate.
- Doc / spec per coverpoint:
  - cp_addi4spn_imm: tools/specs/riscv-isa-manual/src/unpriv/zca.adoc:532-537 (nzuimm scaled by 4, nzuimm != 0). cp_lw_sw_uimm, cp_sp_uimm: :362-379 (offset scaled by 4, base rs1') and :282, :302 (stack-pointer based, scaled by 4). cp_lui_imm: :473-483 (non-zero 6-bit immediate into bits 17-12; rd != x2). cp_addi16sp_imm: :510-514 (multiples of 16 in [-512, 496], rd = x2). cp_cj_off, cp_cb_off: offsets in multiples of 2 (rv32.adoc:174 for the base rule; the Zca forms in zca.adoc). cp_shamt: the shift sections of zca.adoc (shamt = 0 encodings are HINTs). cp_ci_imm6: sext 6-bit immediate (c.addi, c.li, c.andi sections).
  - cp_sp_wrap: the adder carry is internal (rtl/ibex_alu.sv:105-107); recompute from rvfi_rs1_rdata (x2) and the decoded immediate; rv32.adoc:346 (overflow ignored) is the expected behaviour.
  - cp_link: rvfi_rd_wdata - rvfi_pc_rdata = 2 for c.jal / c.jalr (id_stage:396).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - No immediate leaves the RTL: every bin is a TB decode of the 16-bit word; the executed effect (result, address, target) is what RVFI shows, so "decoded and executed" is proved by the result matching the decoded immediate (isa comparator), not by an RTL field.
  - c.addi with imm = 0 (the HINT, CG-CMP-003) and c.nop share the arm (:357-358); c.slli/c.srli/c.srai with shamt = 0 are HINT/reserved encodings the plan guards out (shamt != 0).
  - c.lui with rd = x2 is c.addi16sp (zca.adoc:481-482, decoder :390-402 decides on the rd field); the TB decode must apply the same rule.

## 19. CG-BIT-007 gen_cg_bit_clmul_crc (gen_fcov_plan.md:918)

- Observation point: RVFI retirement, condition decoded clmul/clmulh/clmulr or crc32.b/.h/.w or crc32c.b/.h/.w, rvfi_trap == 0.
- RTL signal chain: rtl/ibex_decoder.sv OP `{0000101, 001/010/011}` -> ALU_CLMUL :1331, ALU_CLMULR :1334, ALU_CLMULH :1337 (RV32BOTEarlGrey or Full only); OP-IMM funct3 001, funct7 0110000, rs2 field 10000..10010 / 11000..11010 -> ALU_CRC32_B/H/W :1110-1122, ALU_CRC32C_B/H/W :1128-1140, each with alu_multicycle_o = 1 (:1111-1141: two ID cycles). rtl/ibex_alu.sv: clmul_result (:409, :646, :894) selected into result_o; the CRC path uses the polynomial constants CRC32_POLYNOMIAL / CRC32C_POLYNOMIAL and their Barrett constants (:904-908), crc_op (:918-920), computed across the two cycles (instr_first_cycle_i). Operands and result on RVFI as in section 0 (crc32 ops are unary: rs2 not read, rvfi_rs2_rdata = 0).
- Sampling condition in RTL terms: the WB retirement of an OPCODE_OP instruction with funct7 0000101 and funct3 in {001, 010, 011}, or an OPCODE_OP_IMM instruction with funct3 001, funct7 0110000 and rvfi_insn[24:20] in {10000, 10001, 10010, 11000, 11001, 11010}, no trap.
- Doc / spec per coverpoint:
  - cp_op: doc/03_reference/instruction_decode_execute.rst:83-96 (Zbc in OTEarlGrey, single cycle; the Zbr CRC ops are draft v0.93, two-cycle) ; tools/specs/riscv-isa-manual/src/unpriv/zb.adoc clmul :617 ("lower half of the 2*XLEN carry-less product"), clmulh :677 ("upper half"), clmulr :738 (bits 2*XLEN-2 : XLEN-1); crc32.[bhw] / crc32c.[bhw] have no ratified sentence (draft group rvb_crc, tools/specs/riscv-bitmanip/texsrc/reference.tex:94); the RTL polynomials 0x04c11db7 (CRC-32) and 0x1edc6f41 (CRC-32C) at alu:904-908 are the definition.
  - cp_rs1_class, cp_rs2_class, cp_bit_sum: TB partitions of the section-0 fields; for single-bit operands 1<<i and 1<<j the carry-less product is the single bit 1<<(i+j) of the 63-bit product, visible in clmul when i+j < 32 and in clmulh when i+j >= 32 (clmulr shows bit i+j+1 - 32 ... i.e. the product shifted by XLEN-1).
  - cp_rd_x0: rvfi_rd_addr.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - Only one half of the 63-bit carry-less product is exported per instruction (clmul low, clmulh high, clmulr high shifted by one): cp_bit_sum on the "other" half samples a zero result; the plan's cr_clmul_bitsum bins should expect result 0 for clmul/ge32 and clmulh/lt32.
  - The two-cycle CRC execution is invisible on RVFI (one record); timing belongs to CG-BIT-010.
  - crc32 ops report rvfi_rs2_rdata = 0 (unary, core:2308); cp_rs2_class is guarded to the clmul family for that reason.
  - cp_rs1_class on rd_x0 records: result forced 0 (core:2344-2346).

## 20. CG-ISA-006 gen_cg_isa_jump (gen_fcov_plan.md:394)

- Observation point: RVFI retirement, condition decoded jal/jalr/c.j/c.jal/c.jr/c.jalr, rvfi_trap == 0.
- RTL signal chain: rtl/ibex_decoder.sv JAL :313-330 and JALR :338-366 (jump_in_dec_o, jump_set_o in the first cycle; JALR funct3 != 0 illegal :364-366 and cleared by the override :905-918); c.j/c.jal -> jal x0/x1 (rtl/ibex_compressed_decoder.sv:371-377), c.jr/c.jalr -> jalr x0/x1, rs1, 0 (:593, :607). Target: the branch-target ALU adds pc_id + imm_j (JAL) or rs1 + imm_i (JALR) (rtl/ibex_id_stage.sv:372-375 for the a-operand, :382-384 for the b-operand; rtl/ibex_ex_block.sv:95-101), carry discarded (:99-100); pc_set in DECODE (rtl/ibex_controller.sv:681-687). Link: the main ALU computes pc + 4 (pc + 2 for the compressed forms) from OP_A_CURRPC and imm_b = IMM_B_INCR_PC (rtl/ibex_id_stage.sv:363, :396 (BranchTargetALU generate; :424 in the other generate)) and writes rd. RVFI: pc_wdata = branch_target_ex at pc_set (rtl/ibex_core.sv:2084; B13: the raw sum, bit 0 not cleared for jalr), the fetch clears bit 0 (rtl/ibex_if_stage.sv:288) so the next record's pc_rdata is even; rd fields as in section 0.
- Sampling condition in RTL terms: the WB retirement of an instruction whose decoder set jump_in_dec_o (JAL, JALR; FENCE.I too, see section 3 of gen_hpm_event_defs.md, excluded here by the plan's decode), no trap.
- Doc / spec per coverpoint:
  - cp_op: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc:401 (jal: the offset is sign-extended and added to the address of the jump instruction), :426-428 (jalr: rs1 + sext imm, least-significant bit set to zero; pc + 4 to rd), :174 (offsets in multiples of 2); zca.adoc for the compressed forms; doc/03_reference/instruction_decode_execute.rst:32, :63.
  - cp_rd_class, cp_jal_off, cp_jalr_imm, cp_jalr_rs1, cp_pc_region: TB decodes of rvfi_insn / rvfi_rd_addr / rvfi_rs1_addr / rvfi_pc_rdata.
  - cp_target_align: rvfi_pc_wdata[1] (bit 0 masked, as the plan says, because of B13).
  - cp_target_odd: (rs1_rdata + imm)[0] equals rvfi_pc_wdata[0] TODAY (B13 keeps the raw bit); the architectural target has bit 0 cleared (rv32.adoc:428; if_stage:288).
  - cp_wrap: carry of pc + imm or rs1 + imm, discarded by the RTL (ex_block:99-100); recompute.
  - cp_link_len: rvfi_rd_wdata - rvfi_pc_rdata = 4 for jal/jalr, 2 for c.jal/c.jalr (id_stage:396).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - cp_target_odd is observable only through the B13 defect: once rtl/ibex_core.sv:2084 masks bit 0, the bin must be computed from rvfi_rs1_rdata + imm, never from pc_wdata; write the sampler that way from the start.
  - jal x0 / c.j and jalr x0 / c.jr: rd_wdata forced 0 (core:2344-2346); the link value is unobservable, cp_link_len is guarded to rd != 0 for that reason.
  - c.j / c.jal / c.jr / c.jalr vs jal / jalr: one decoder arm each after expansion; only the 16-bit rvfi_insn separates them (core:2263-2265).
  - The redirect itself is only visible as the next record's rvfi_pc_rdata (== target with bit 0 cleared); a jump followed by a trap on the target fetch shows the target in the trap record's pc_rdata with mtval per D10.

## 21. CG-CSR-016 gen_cg_csr_reset_read (gen_fcov_plan.md:1510)

- Observation point: the first CSR read of an address after reset, before any software write to it (TB per-address tracking), rvfi_valid && is_csr_insn && !rvfi_trap.
- RTL signal chain, reset values (rtl/ibex_cs_registers.sv; the register instance is the anchor): mstatus MSTATUS_RST_VAL = {mie 0, mpie 1, mpp U, mprv 0, tw 0} = 0x80 (:1052-1056, u_mstatus_csr :1075-1076); mepc 0 (:1092-1093); mie 0 (:1110-1111); mscratch 0 (:1124-1125); mcause 0 (:1138-1139); mtval 0 (:1152-1153); mtvec: the flop resets to 1 (:1173-1174) but is overwritten with {boot_addr_i[31:8], 6'b0, 1'b0, 1'b1} by csr_mtvec_init at the first boot fetch (rtl/ibex_if_stage.sv:256 `csr_mtvec_init_o = (pc_mux_i == PC_BOOT) & pc_set_i`; cs_registers :736-741), before any instruction can read it; dcsr DCSR_RESET_VAL = {xdebugver 4, cause 0, prv M} = 0x40000003 (:1183-1194); dpc 0 (:1210-1211); dscratch0/1 0 (:1228-1229, :1246-1247); mcounteren 0 (:1741); mcountinhibit 0 (:1725); mhpmevent hardwired 1 << (N-3) (:1602-1619, D20); mcycle/minstret/mhpmcounter 0 (ibex_counter resets, :1622-1690); cpuctrlsts 0 (:1941-1942, :1977) with ic_scr_key_valid following the input every cycle; tselect 0 (:1797), tdata1 0x28001048 (:1806-1812 with the fixed view :1848-1864, section R5 of gen_t102_rtl_facts.md), tdata2 0 (:1824); pmpcfg/pmpaddr/mseccfg from PmpCfgRst / PmpAddrRst / PmpMseccfgRst (:1451, :1486, :1519; rtl/ibex_pkg.sv:769-810, all zero); mip is the live input vector (:409-412, no storage); misa constant (:377, :452); mvendorid/mimpid = CsrMvendorId/CsrMimpId parameters (:422, :428); marchid 22 (:424-426); mhartid = hart_id_i (:432); mstatush, menvcfg, menvcfgh 0 (:445, :449). The read itself is a csrr record: rvfi_rd_wdata carries the value (rd != x0).
- Sampling condition in RTL terms: a CSR read (csr_access with csr_op READ, or any form with rd != x0) whose address has not been written since reset (csr_we_int never asserted for it: :1020); the TB tracks the "not written" part from the retired stream.
- Doc / spec per coverpoint:
  - cp_csr: doc/03_reference/cs_registers.rst "Reset Value" lines: mstatus 0x80 :116, mie 0 :154, mtvec 0x1 :178 (see the flag), mcounteren :197, mscratch :227, mepc :243, mcause :266, mtval :303, tdata1 0x2800_1000 :360 (see the flag), dcsr 0x4000_0003 :463, marchid 0x16 :617; doc/03_reference/pmp.rst:57 (all PMP CSRs including mseccfg reset to 0); mhpmevent per D20.
  - cp_when: TB retirement index (first_insn = the first record after reset).
  - cp_boot_lo: boot_addr_i[7:0] never enters mtvec (only [31:8] is used, :739-741), so both bins read the same mtvec {boot_addr[31:8], 8'h01}; the bins prove the low byte is ignored.
  - cp_hart: hart_id_i passes through unchanged (:432).
  - cp_dbg: rvfi_ext_debug_mode (rtl/ibex_core.sv:2101).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - mtvec's flop reset value 1 is unobservable: csr_mtvec_init rewrites it at the PC_BOOT fetch, before the first instruction retires (if_stage:256, cs_registers:736-741); the first read returns {boot_addr[31:8], 8'h01}. The doc line "Reset Value 0x0000_0001" (cs_registers.rst:178) describes the flop, not the readable value.
  - tdata1: the doc's reset value 0x2800_1000 (cs_registers.rst:360) contradicts the doc's own field table (m = 1 at bit 6 and u = 1 at bit 3, cs_registers.rst:362-400) and the RTL (0x28001048, :1848-1864); the RTL is the reference for the bin, and this is a documentation defect for the DV Lead (candidate, D-class like D20).
  - mip has no reset value: the first read returns the interrupt lines as driven at that cycle.
  - mcycle and minstret first reads are not 0: mcycle counts from reset (:1586) and minstret counts every retired instruction before the read (:1588); the reset value is observable only as "counter value consistent with the elapsed cycles / instructions".
  - cp_when.first_insn for a CSR other than the first instruction's target is unreachable by construction (one record).

## 22. CG-CMP-009 gen_cg_cmp_zcmp_hazard (gen_fcov_plan.md:769)

- Observation point: the RVFI record with rvfi_ext_expanded_insn_last == 1 of any cm.* instruction, classified by the monitor's instruction history (the neighbour pattern).
- RTL signal chain: the Zcmp micro-ops are ordinary instructions in ID/EX/WB (section 4), so the hazards resolve by the normal paths: a register written by the instruction in WB is forwarded to the reader in ID (rtl/ibex_id_stage.sv:1103 rf_rd_a_wb_match, :1117 `rf_rdata_a_fwd = rf_rd_a_wb_match & rf_write_wb_i ? rf_wdata_fwd_wb_i : rf_rdata_a_i`, and the b-side twins), a load whose data is still outstanding stalls its consumer (:1120 `stall_ld_hz = outstanding_load_wb_i & (rf_rd_a_hz | rf_rd_b_hz)`); a store in WB holds WB until its response (rtl/ibex_wb_stage.sv:115-116), so a following cm.pop load micro-op issues only after the store completed (id_wb_pending, rtl/ibex_controller.sv:296). popret / popretz: the LAST micro-op is `jalr x0, 0(ra)` (rtl/ibex_compressed_decoder.sv:764-770, cm_ret_ra :143-150) with ra freshly loaded by an earlier micro-op (forwarded or read from the RF by the rules above); its redirect sets the PC (rtl/ibex_controller.sv:681-687) and clears the fetch FIFO (rtl/ibex_if_stage.sv:287-288). The instruction at pc + 2 (the fall-through) never enters ID: the fetch is held while the expander is not on its LAST micro-op (if_stage:809-810) and the jalr redirect empties the FIFO before the next handover; the expander returns to CmIdle on LAST (:770).
- Sampling condition in RTL terms: the WB retirement of the LAST micro-op (rvfi_ext_expanded_insn_last) with the TB's history matching one of the patterns; every value hazard is proved by rvfi_rs1_rdata / rvfi_mem_* of the micro-ops equalling the expected forwarded values.
- Doc / spec per coverpoint:
  - cp_hazard, cp_rlist_class: tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1175 (atomic execution of the moves) and the sequence definitions of section 4; rlist field rvfi_ext_expanded_insn[7:4].
  - cp_ret_once: exactly one _last record for the popret/popretz (:764-770) and the next record's rvfi_pc_rdata == ra & ~1 (if_stage:288; ra itself is rvfi_rs1_rdata of the jalr micro-op).
  - cp_ft_kind: the encoding at pc + 2 is known to the TB from the program image; it is never a retired record (see above).
  - cp_redirect_once, cp_dmem_delay, cp_delta_uop: bus monitors and record timing (each micro-op retires at WB; deltas > 1 come from load/store responses and stall_ld_hz).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - Forwarding is invisible as such: RVFI shows the operand value the instruction consumed (core:2304-2310, captured after forwarding); the hazard classes (load_prev / alu_prev) are TB history, and their correctness is proved by the value, not by an RTL flag.
  - popret_ft_cm / popretz_ft_cm: the fall-through cm.* is never executed and never produces a record, so cp_ft_kind can only come from the program image; a bin expecting a record of the fall-through would never hit.
  - Atomicity of the COMMIT micro-ops (no interrupt between them, controller:498-500) is an RTL gate with no RVFI tag; cp_uop_count_ok-style checks count records only.
  - cp_delta_uop timing is cycle-level: rvfi_valid cycle stamps are needed; nothing in the record encodes the delta.

## 23. CG-BIT-004 gen_cg_bit_perm (gen_fcov_plan.md:864)

- Observation point: RVFI retirement, condition decoded grev/grevi/gorc/gorci/shfl/shfli/unshfl/unshfli, rvfi_trap == 0.
- RTL signal chain: rtl/ibex_decoder.sv OP: grev `{0110100,101}` :1305, gorc `{0010100,101}` :1306, shfl `{0000100,001}` :1308, unshfl `{0000100,101}` :1311 (OTEarlGrey/Full); OP-IMM: grevi :1178, gorci :1179 (funct3 101, instr[31:27] 01101 / 00101), shfli :1100 (funct3 001, instr[31:27] 00001, instr[26] = 0), unshfli :1183 (funct3 101, instr[31:27] 00001, instr[26] = 0). Legality (:553-576): grevi and gorci are legal for every control value in this configuration (illegal_insn = 0 :556, :565), instr[26] must be 0 for shfli/unshfli (:511, :573); instr[25] is not examined by any of these arms. rtl/ibex_alu.sv: the control value is shift_amt = operand_b[4:0] or the immediate (:279-290), mapped by zbp_shift_amt (:603-606, full 5 bits in OTEarlGrey/Full), grev/gorc through the staged rev_result network (:602-630, gorc ORs the original in at each stage), shfl/unshfl through the shuffle network (shuffle_result, result mux :1341-1342).
- Sampling condition in RTL terms: the WB write of an instruction decoded to ALU_GREV / GORC / SHFL / UNSHFL, no trap; on RVFI the funct7/funct3 pairs above for OP, or OP-IMM funct3 101/001 with rvfi_insn[31:27] in {01101, 00101, 00001} (and rvfi_insn[26] == 0 for the shuffles).
- Doc / spec per coverpoint:
  - cp_op: doc/03_reference/instruction_decode_execute.rst:97 (Zbp v0.93 in OTEarlGrey, single cycle). No ratified sentence exists for the general forms: tools/specs/riscv-bitmanip/texsrc/reference.tex:88 lists grev/gorc/shfl/unshfl (rvb_bextdep group) and :205-248 gives the reference C for grev, shfl, unshfl; the ratified subsets are rev8 = grevi 24 (tools/specs/riscv-isa-manual/src/unpriv/zb.adoc:1601), orc.b = gorci 7 (:1336), zip = shfli 15 and unzip = unshfli 15 (:2819, :2517), usable as checkable special cases of the same bins.
  - cp_grev_ctrl (5 bits), cp_shfl_ctrl (4 bits): rvfi_rs2_rdata[4:0] / [3:0] or rvfi_insn[24:20] / [23:20]; alu:279-290, :603-606.
  - cp_operand, cp_rd_x0: section-0 fields.
  - cp_rs2_upper: rvfi_rs2_rdata bits above the control field, ignored by the RTL (alu:279-290).
  - cp_bit25: rvfi_insn[25] on the immediate forms; the decoder ignores it (:553-576), so the instruction retires normally with rvfi_trap == 0: the b1 bins prove the lenient decode.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - Control values that differ only in ignored bits (rs2 upper bits, instr[25]) are the same operation; the bins are equivalence classes proving the ignore.
  - There is no ratified semantics sentence for grev/gorc/shfl/unshfl beyond the draft reference code; the RTL network (alu:602-630 and the shuffle stages) is the definition, cross-checked by rev8/orc.b/zip/unzip.
  - cp_operand on rd_x0 records: result forced 0 (core:2344-2346).

## 24. CG-PMP-004 gen_cg_pmp_csr_access (gen_fcov_plan.md:2469)

- Observation point: RVFI retirement of any CSR instruction addressing pmpcfg0..3, pmpaddr0..15, mseccfg or mseccfgh, including trapped ones.
- RTL signal chain (rtl/ibex_cs_registers.sv): the PMP CSRs sit at 0x3A0-0x3A3, 0x3B0-0x3BF, 0x747, 0x757, i.e. csr[9:8] = 11 (M-level) and csr[11:10] != 11 (read/write): illegal_csr_priv = csr_addr[9:8] > priv_lvl_q (:403) makes every U-mode access illegal regardless of form; illegal_csr_write (:404) never applies; the addresses exist because PMPEnable = 1 (read cases pmpcfg :525-532, pmpaddr :533-548, mseccfg :503-512, mseccfgh in the same block; with PMPEnable = 0 they would be illegal_csr :707-716); writes per sections 13 and 15 (mseccfg :1502-1510). The combined illegal flag (:405-406) becomes an illegal-instruction exception in the controller (mcause 2, mtval = the instruction word, rtl/ibex_controller.sv:866-868). Debug mode executes at M privilege (priv_lvl_d = PRIV_LVL_M on debug entry, :907; dcsr.prv saves the old one :913), so PMP CSRs are accessible in debug mode. Read-only forms: the decoder forces csr_op to READ for csrrs/csrrc with rs1 = x0 and csrrsi/csrrci with uimm = 0 (rtl/ibex_decoder.sv:251-258); csr_we_int = csr_wr & csr_op_en (:1011, :1020). RVFI: rvfi_mode (rtl/ibex_core.sv:2078), rvfi_ext_debug_mode (:2101), rvfi_trap (:1885), rvfi_insn.
- Sampling condition in RTL terms: csr_access with a PMP address in ID, retired (record) or trapped (record with rvfi_trap = 1); in U-mode the trap is raised in ID before any CSR read or write.
- Doc / spec per coverpoint:
  - cp_class, cp_op, cp_rw: tools/specs/riscv-isa-manual/src/priv/csrs.adoc:30-31 (csr[11:10] read/write vs read-only; csr[9:8] the lowest privilege that can access), :49 (writes to read-only addresses raise illegal-instruction); doc/03_reference/pmp.rst:47-57 (Smepmp CSR set).
  - cp_priv: rvfi_mode is the executing privilege (gen_t102_rtl_facts.md R2). cp_dbg: rvfi_ext_debug_mode.
  - cp_trap: illegal-instruction with mcause 2 (controller :866-868); the U-mode rule is :403.
  - cp_first_after_reset: TB tracking; reset values PmpCfgRst / PmpAddrRst / PmpMseccfgRst (rtl/ibex_pkg.sv:769-810; pmp.rst:57), mseccfgh reads 0.
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - A U-mode access traps identically whether it is a read-only form or a write (illegal_csr_priv does not look at csr_wr, :403): the read_only / write split of the u_* bins is an instruction decode, the RTL behaviour is one trap; the record shows rvfi_trap = 1, rd_wdata 0, no CSR effect.
  - In debug mode the privilege is M (:907), so d1 accesses never trap on privilege; dbg bins prove accessibility, not a distinct RTL path.
  - mseccfgh is read-only zero (no write case): a write is legal and ignored; a bin expecting a trap on it would never hit.
  - mseccfg writes with RLB while any entry is locked keep RLB at 0 (:1505-1510): visible only on the read-back.

## 25. CG-CSR-001 gen_cg_csr_access_class (gen_fcov_plan.md:1178)

- Observation point: rvfi_valid with rvfi_insn opcode SYSTEM (0x73) and funct3 != 000, trapped or not.
- RTL signal chain: rtl/ibex_decoder.sv OPCODE_SYSTEM (:730): funct3 001/010/011/101/110/111 -> csr_access_o with csr_op WRITE/SET/CLEAR (:761-772), funct3 100 -> csr_illegal -> illegal_insn (:773, :783); set/clear forms with rs1 = x0 or uimm = 0 are forced to CSR_OP_READ (:251-258). rtl/ibex_cs_registers.sv classifies the access: illegal_csr (unimplemented address, read-mux default :702-704; PMP CSRs when PMPEnable = 0 :707-716; mseccfg when !PMPEnable :511/:520; trigger CSRs when !DbgTriggerEn :636-660; U-mode counter aliases when the mcounteren bit is clear :607-632, :618, :632), illegal_csr_write (csr_addr[11:10] == 11 & csr_wr, :404, csr_wr :1011), illegal_csr_priv (csr_addr[9:8] > priv_lvl_q, :403), illegal_csr_dbg (dcsr/dpc/dscratch0/1 outside debug mode, :402, :549-565); the OR of all four raises one illegal-instruction exception (:405-406; controller mcause 2, mtval = instruction, rtl/ibex_controller.sv:866-868). RVFI: rvfi_mode (rtl/ibex_core.sv:2078), rvfi_ext_debug_mode (:2101), rvfi_trap (:1885), rvfi_rd_wdata = the CSR read value on a non-trapping record (rd != x0), rvfi_rs1_rdata = the write source for the register forms.
- Sampling condition in RTL terms: any record whose rvfi_insn[6:0] == 1110011 and rvfi_insn[14:12] != 000 (ecall/ebreak/mret/dret/wfi are funct3 000 and excluded).
- Doc / spec per coverpoint:
  - cp_op, cp_rs1, cp_rd: rvfi_insn fields; decoder :761-773, :251-258 (read-only forms).
  - cp_priv, cp_dbg: rvfi_mode (R2), rvfi_ext_debug_mode.
  - cp_aclass: the TB's address classifier; the RTL classes it must mirror are :402-406 with :702-716, :607-632, :636-660; tools/specs/riscv-isa-manual/src/priv/csrs.adoc:30-31 (address conventions), :49 (read-only writes trap), :64 (non-existent CSRs trap); doc/03_reference/cs_registers.rst:13-17 (the implemented table).
  - cp_trap, cp_iclass: rvfi_trap; the RTL does not distinguish the classes in the trap (single illegal-instruction, :405-406).
- Bins the RTL cannot distinguish or RVFI cannot observe:
  - cp_iclass.multi and the single classes produce the same trap (mcause 2, mtval = insn, :405-406, controller :866-868): the class is TB reasoning about the address and state, not an RTL observation.
  - csrrs/csrrc with rs1 = x0 (and the zero-uimm forms) to a read-only address do NOT trap (csr_op READ -> csr_wr 0 -> illegal_csr_write 0; :251-258, :404, :1011): the cr_rs1zero_ro ok bins are the RTL behaviour; the same forms to a U-inaccessible address still trap (:403 ignores csr_wr).
  - funct3 100 traps in the decoder before the CSR unit sees the address (:773, :783): cp_aclass has no meaning for that record.
  - A read of a U-accessible counter alias with the mcounteren bit clear traps in U (:618, :632) and reads in M; the same address therefore lands in two different classes by privilege, which only rvfi_mode reveals.

## Slice status

Slices 1-5 (ranks 1-25) written; slices 6.. follow the ranked order in gen_round0_covergroup_set.md.
