# gen_zc_insn.h: GNU as macros for the Zcb and Zcmp instructions the ibex decoder accepts
# (RV32ZC = RV32ZcaZcbZcmp). The lowRISC gcc 10.2 / binutils 2.35 toolchain knows neither
# extension and rejects raw `.insn N, value`, so each macro emits the 16-bit encoding with .2byte.
# Encodings: RISC-V Zc* specification v1.0.0 (tools/specs, unprivileged manual) cross-checked
# against rtl/ibex_compressed_decoder.sv (Zcb: C0 funct3 100 at :266-326, C1 funct3 100 / funct2 11
# at :430-519; Zcmp: C2 funct3 101 at :615-760; sreg' map cm_mvsa01/cm_mva01s at :153-165).
#
# Register arguments are full x-register NUMBERS (not names): rd'/rs1'/rs2' must be 8..15;
# sreg' must be 8, 9 or 18..23. Immediates are the raw field values described per macro.
# GAS relational operators yield -1 for true; the sreg' formula below relies on that.

# ---- field helpers -------------------------------------------------------------------------
# 3-bit compressed register field for x8..x15.
.macro gen_c3 r
  .if (\r < 8) || (\r > 15)
    .error "compressed register must be x8..x15"
  .endif
.endm
# sreg' for x8,x9 -> 0,1 and x18..x23 -> 2..7 : (r - 8) - 8*(r >= 16) with GAS -1 = true.
#   x18: (18-8) + ((18>=16)*8) = 10 + (-1*8) = 2
.macro gen_sreg r
  .if !((\r == 8) || (\r == 9) || ((\r >= 18) && (\r <= 23)))
    .error "sreg' must be x8, x9 or x18..x23"
  .endif
.endm

# ---- Zcb loads/stores (C0 quadrant, funct3 100) -------------------------------------------
# c.lbu rd', uimm(rs1')   uimm in 0..3      : 100 000 rs1' uimm[0] uimm[1] rd' 00
.macro c_lbu rd, uimm, rs1
  gen_c3 \rd
  gen_c3 \rs1
  .2byte (0b100 << 13) | (0b000 << 10) | (((\rs1) - 8) << 7) | (((\uimm) & 1) << 6) | ((((\uimm) >> 1) & 1) << 5) | (((\rd) - 8) << 2) | 0b00
.endm
# c.lhu rd', uimm(rs1')   uimm in {0, 2}    : 100 001 rs1' 0 uimm[1] rd' 00
.macro c_lhu rd, uimm, rs1
  gen_c3 \rd
  gen_c3 \rs1
  .2byte (0b100 << 13) | (0b001 << 10) | (((\rs1) - 8) << 7) | (0 << 6) | ((((\uimm) >> 1) & 1) << 5) | (((\rd) - 8) << 2) | 0b00
.endm
# c.lh rd', uimm(rs1')    uimm in {0, 2}    : 100 001 rs1' 1 uimm[1] rd' 00
.macro c_lh rd, uimm, rs1
  gen_c3 \rd
  gen_c3 \rs1
  .2byte (0b100 << 13) | (0b001 << 10) | (((\rs1) - 8) << 7) | (1 << 6) | ((((\uimm) >> 1) & 1) << 5) | (((\rd) - 8) << 2) | 0b00
.endm
# c.sb rs2', uimm(rs1')   uimm in 0..3      : 100 010 rs1' uimm[0] uimm[1] rs2' 00
.macro c_sb rs2, uimm, rs1
  gen_c3 \rs2
  gen_c3 \rs1
  .2byte (0b100 << 13) | (0b010 << 10) | (((\rs1) - 8) << 7) | (((\uimm) & 1) << 6) | ((((\uimm) >> 1) & 1) << 5) | (((\rs2) - 8) << 2) | 0b00
.endm
# c.sh rs2', uimm(rs1')   uimm in {0, 2}    : 100 011 rs1' 0 uimm[1] rs2' 00
.macro c_sh rs2, uimm, rs1
  gen_c3 \rs2
  gen_c3 \rs1
  .2byte (0b100 << 13) | (0b011 << 10) | (((\rs1) - 8) << 7) | (0 << 6) | ((((\uimm) >> 1) & 1) << 5) | (((\rs2) - 8) << 2) | 0b00
.endm

# ---- Zcb ALU (C1 quadrant, funct3 100, instr[12:10] = 111, funct2 11 / 10) -----------------
# c.zext.b / c.sext.b / c.zext.h / c.sext.h / c.not rd'  : 100 111 rd' 11 fff 01
.macro gen_c_zcb_unary rd, fff
  gen_c3 \rd
  .2byte (0b100 << 13) | (0b111 << 10) | (((\rd) - 8) << 7) | (0b11 << 5) | ((\fff) << 2) | 0b01
.endm
.macro c_zext_b rd
  gen_c_zcb_unary \rd, 0b000
.endm
.macro c_sext_b rd
  gen_c_zcb_unary \rd, 0b001
.endm
.macro c_zext_h rd
  gen_c_zcb_unary \rd, 0b010
.endm
.macro c_sext_h rd
  gen_c_zcb_unary \rd, 0b011
.endm
.macro c_not rd
  gen_c_zcb_unary \rd, 0b101
.endm
# c.mul rd', rs2'          : 100 111 rd' 10 rs2' 01
.macro c_mul rd, rs2
  gen_c3 \rd
  gen_c3 \rs2
  .2byte (0b100 << 13) | (0b111 << 10) | (((\rd) - 8) << 7) | (0b10 << 5) | (((\rs2) - 8) << 2) | 0b01
.endm

# ---- Zcmp (C2 quadrant, funct3 101) --------------------------------------------------------
# rlist: 4 = {ra}, 5 = {ra,s0}, 6 = {ra,s0-s1}, 7 = {ra,s0-s2}, 8 = s0-s3, 9 = s0-s4, 10 = s0-s5,
#        11 = s0-s6, 12 = s0-s7, 13 = s0-s8, 14 = s0-s9, 15 = s0-s11 (all with ra).
# stack_adj = stack_adj_base(rlist) + 16 * spimm, base (RV32) = 16 for rlist 4..7, 32 for 8..11,
#        48 for 12..14, 64 for 15 (rtl/ibex_compressed_decoder.sv:44-57). spimm is the raw 2-bit field.
# cm.push {rlist}, -stack_adj      : 101 11000 rlist spimm 10
.macro gen_cm_stack op5, rlist, spimm
  .if (\rlist < 4) || (\rlist > 15)
    .error "rlist must be 4..15"
  .endif
  .2byte (0b101 << 13) | ((\op5) << 8) | ((\rlist) << 4) | (((\spimm) & 3) << 2) | 0b10
.endm
.macro cm_push rlist, spimm
  gen_cm_stack 0b11000, \rlist, \spimm
.endm
# cm.pop {rlist}, stack_adj        : 101 11010 rlist spimm 10
.macro cm_pop rlist, spimm
  gen_cm_stack 0b11010, \rlist, \spimm
.endm
# cm.popretz {rlist}, stack_adj    : 101 11100 rlist spimm 10   (a0 = 0; ret)
.macro cm_popretz rlist, spimm
  gen_cm_stack 0b11100, \rlist, \spimm
.endm
# cm.popret {rlist}, stack_adj     : 101 11110 rlist spimm 10   (ret)
.macro cm_popret rlist, spimm
  gen_cm_stack 0b11110, \rlist, \spimm
.endm
# cm.mvsa01 r1s', r2s'  (r1s' = a0, r2s' = a1; r1s' != r2s') : 101 011 r1s' 01 r2s' 10
.macro cm_mvsa01 r1s, r2s
  gen_sreg \r1s
  gen_sreg \r2s
  .2byte (0b101 << 13) | (0b011 << 10) | ((((\r1s) - 8) + (((\r1s) >= 16) * 8)) << 7) | (0b01 << 5) | ((((\r2s) - 8) + (((\r2s) >= 16) * 8)) << 2) | 0b10
.endm
# cm.mva01s r1s', r2s'  (a0 = r1s', a1 = r2s')                 : 101 011 r1s' 11 r2s' 10
.macro cm_mva01s r1s, r2s
  gen_sreg \r1s
  gen_sreg \r2s
  .2byte (0b101 << 13) | (0b011 << 10) | ((((\r1s) - 8) + (((\r1s) >= 16) * 8)) << 7) | (0b11 << 5) | ((((\r2s) - 8) + (((\r2s) >= 16) * 8)) << 2) | 0b10
.endm
