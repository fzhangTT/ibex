# gen_alu_directed.S: the Zba / Zbb / pack operations, the base shifts (register and immediate forms) and the OP-IMM ALU operations
# over a table of operand classes (0, 1, all ones, INT_MIN, INT_MAX, 2, a byte-sign value, a half-word-sign value, 0xE0000000,
# 32, 33, 0xFFFFFFE0, a negative and a positive value), every ordered pair, with the register relations the coverage plan names
# (distinct, rd = x0, rs1 = rs2, rs1 = rd, all the same) and the immediate classes (0, 1, -1, 2047, -2048, 100, -100; shift
# amounts 0, 1, 7, 31). The lock-step model checks every result; the run exists for gen_bit_zba_zbb_ops_cg, gen_isa_alu_imm_cg,
# gen_isa_shift_cg. 1 to tohost at the end.
.section .text
.globl _start
_start:
  la   a0, tab
  li   s0, 0
outer:
  li   s1, 0
inner:
  slli t1, s0, 2
  add  t1, t1, a0
  slli t2, s1, 2
  add  t2, t2, a0
  lw   a1, 0(t1)
  lw   a2, 0(t2)
  .option push
  .option norvc
  # ---- Zba / Zbb / pack: distinct rd, rd = x0, rs1 = rs2, all the same
  sh1add a3, a1, a2
  sh2add a3, a1, a2
  sh3add a3, a1, a2
  andn   a3, a1, a2
  orn    a3, a1, a2
  xnor   a3, a1, a2
  min    a3, a1, a2
  max    a3, a1, a2
  minu   a3, a1, a2
  maxu   a3, a1, a2
  pack   a3, a1, a2
  packu  a3, a1, a2
  packh  a3, a1, a2
  pack   a3, a1, x0
  sext.b a3, a1
  sext.h a3, a1
  sh1add x0, a1, a2
  andn   x0, a1, a2
  min    x0, a1, a2
  pack   x0, a1, a2
  sext.b x0, a1
  sh1add a3, a1, a1
  xnor   a3, a2, a2
  max    a3, a1, a1
  packh  a3, a2, a2
  minu   a1, a1, a1
  lw     a1, 0(t1)
  # ---- shifts: register forms on the pair, immediate forms on a1
  sll    a3, a1, a2
  srl    a3, a1, a2
  sra    a3, a1, a2
  sll    x0, a1, a2
  srl    x0, a1, a2
  sra    x0, a1, a2
  slli   a3, a1, 0
  slli   a3, a1, 1
  slli   a3, a1, 7
  slli   a3, a1, 31
  srli   a3, a1, 0
  srli   a3, a1, 1
  srli   a3, a1, 7
  srli   a3, a1, 31
  srai   a3, a1, 0
  srai   a3, a1, 1
  srai   a3, a1, 7
  srai   a3, a1, 31
  slli   x0, a1, 31
  srai   x0, a1, 31
  # ---- OP-IMM ALU: the immediate classes; rs1 = rd variants reload a1
  addi   a3, a1, 0
  addi   a3, a1, 1
  addi   a3, a1, -1
  addi   a3, a1, 2047
  addi   a3, a1, -2048
  addi   a3, a1, 100
  addi   a3, a1, -100
  slti   a3, a1, 0
  slti   a3, a1, 1
  slti   a3, a1, -1
  slti   a3, a1, 2047
  slti   a3, a1, -2048
  slti   a3, a1, 100
  slti   a3, a1, -100
  sltiu  a3, a1, 0
  sltiu  a3, a1, 1
  sltiu  a3, a1, -1
  sltiu  a3, a1, 2047
  sltiu  a3, a1, -2048
  sltiu  a3, a1, 100
  sltiu  a3, a1, -100
  xori   a3, a1, 0
  xori   a3, a1, 1
  xori   a3, a1, -1
  xori   a3, a1, 2047
  xori   a3, a1, -2048
  xori   a3, a1, 100
  xori   a3, a1, -100
  ori    a3, a1, 0
  ori    a3, a1, 1
  ori    a3, a1, -1
  ori    a3, a1, 2047
  ori    a3, a1, -2048
  ori    a3, a1, 100
  ori    a3, a1, -100
  andi   a3, a1, 0
  andi   a3, a1, 1
  andi   a3, a1, -1
  andi   a3, a1, 2047
  andi   a3, a1, -2048
  andi   a3, a1, 100
  andi   a3, a1, -100
  addi   x0, a1, 1
  slti   x0, a1, 1
  sltiu  x0, a1, 1
  xori   x0, a1, 1
  ori    x0, a1, 1
  andi   x0, a1, 1
  addi   a1, a1, 1
  lw     a1, 0(t1)
  slti   a1, a1, -1
  lw     a1, 0(t1)
  sltiu  a1, a1, 1
  lw     a1, 0(t1)
  xori   a1, a1, -1
  lw     a1, 0(t1)
  ori    a1, a1, 2047
  lw     a1, 0(t1)
  andi   a1, a1, -2048
  lw     a1, 0(t1)
  .option pop
  addi s1, s1, 1
  li   t3, 14
  bne  s1, t3, inner
  addi s0, s0, 1
  bne  s0, t3, outer
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 4
tab:
  .word 0x00000000, 0x00000001, 0xFFFFFFFF, 0x80000000, 0x7FFFFFFF, 0x00000002, 0x00000080, 0x00008000, 0xE0000000, 0x00000020, 0x00000021, 0xFFFFFFE0, 0x9ABCDEF0, 0x12345678
