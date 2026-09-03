# gen_muldiv_directed.S: every M-extension and base R-type ALU operation over a table of operand classes (0, 1, all ones, INT_MIN,
# INT_MAX, 2^16, 2, 7, -2, a negative and a positive value), every ordered pair, with the register relations the coverage plan names
# (distinct, rd = x0, rs1 = rs2, rs = rd, all the same) and c.mul from its 16-bit encoding. The lock-step model checks every result;
# the run exists for the covergroups gen_mul_ops_cg, gen_div_ops_cg, gen_isa_alu_reg_cg. 1 to tohost at the end.
.section .text
.globl _start
_start:
  la   a0, tab
  li   s0, 0                        # i
outer:
  li   s1, 0                        # j
inner:
  slli t1, s0, 2
  add  t1, t1, a0                   # &tab[i]
  slli t2, s1, 2
  add  t2, t2, a0                   # &tab[j]
  lw   a1, 0(t1)
  lw   a2, 0(t2)
  .option push
  .option norvc
  # ---- multiplies: distinct rd, rd = x0, rs1 = rs2, rs = rd, all the same
  mul    a3, a1, a2
  mulh   a3, a1, a2
  mulhsu a3, a1, a2
  mulhu  a3, a1, a2
  mul    x0, a1, a2
  mulh   x0, a1, a2
  mulhsu x0, a1, a2
  mulhu  x0, a1, a2
  mul    a3, a1, a1
  mulh   a3, a1, a1
  mulhsu a3, a2, a2
  mulhu  a3, a2, a2
  mul    a1, a1, a2
  lw     a1, 0(t1)
  mulh   a2, a1, a2
  lw     a2, 0(t2)
  mulhsu a1, a1, a1
  lw     a1, 0(t1)
  mulhu  a2, a2, a2
  lw     a2, 0(t2)
  mul    a1, a1, a1
  lw     a1, 0(t1)
  # ---- divides
  div    a3, a1, a2
  divu   a3, a1, a2
  rem    a3, a1, a2
  remu   a3, a1, a2
  div    x0, a1, a2
  divu   x0, a1, a2
  rem    x0, a1, a2
  remu   x0, a1, a2
  div    a3, a2, a1
  rem    a3, a2, a1
  # ---- base ALU: distinct rd, rd = x0, rs1 = rs2, rs1 = rd, rs2 = rd, all the same
  add    a3, a1, a2
  sub    a3, a1, a2
  slt    a3, a1, a2
  sltu   a3, a1, a2
  xor    a3, a1, a2
  or     a3, a1, a2
  and    a3, a1, a2
  add    x0, a1, a2
  sub    x0, a1, a2
  slt    x0, a1, a2
  sltu   x0, a1, a2
  xor    x0, a1, a2
  or     x0, a1, a2
  and    x0, a1, a2
  add    a3, a1, a1
  sub    a3, a2, a2
  slt    a3, a1, a1
  sltu   a3, a2, a2
  xor    a3, a1, a1
  or     a3, a2, a2
  and    a3, a1, a1
  add    a1, a1, a2
  lw     a1, 0(t1)
  sub    a2, a1, a2
  lw     a2, 0(t2)
  slt    a1, a1, a2
  lw     a1, 0(t1)
  sltu   a2, a1, a2
  lw     a2, 0(t2)
  xor    a1, a1, a2
  lw     a1, 0(t1)
  or     a2, a1, a2
  lw     a2, 0(t2)
  and    a1, a1, a2
  lw     a1, 0(t1)
  add    a1, a1, a1
  lw     a1, 0(t1)
  sub    a2, a2, a2
  lw     a2, 0(t2)
  .option pop
  .2byte 0x9dd1                     # c.mul a1, a2 (Zcb: 100111 rsd'=011 10 rs2'=100 01): a1 = a1 * a2
  lw     a1, 0(t1)
  .2byte 0x9dcd                     # c.mul a1, a1 (rs2' = 011): all registers the same
  lw     a1, 0(t1)
  addi s1, s1, 1
  li   t3, 11
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
  .word 0x00000000, 0x00000001, 0xFFFFFFFF, 0x80000000, 0x7FFFFFFF, 0x00010000, 0x00000002, 0x00000007, 0xFFFFFFFE, 0x9ABCDEF0, 0x12345678
