# gen_sbit_directed.S: the Zbs single-bit instructions (bclr, bset, binv, bext and their immediate forms) over the index classes
# (0, a middle index, 31), both prior bit states, the operand classes (zero, all ones, other), the rs2 upper-bit classes of the
# register forms (zero, all ones, other nonzero), rd = x0, and binv / binvi twice on the same rd and index. The lock-step model checks
# every result; the run exists for gen_bit_sbit_cg. 1 to tohost at the end.
.section .text
.globl _start
# register form over three operands with rs2 = idx, idx | upper (other nonzero), 0xFFFFFFE0 | idx (all ones when idx = 31)
.macro sb_reg op, idx
  li   t0, 0
  li   t1, \idx
  \op  t2, t0, t1
  li   t0, -1
  \op  t2, t0, t1
  li   t0, 0x5A5A5A5A
  \op  t2, t0, t1
  li   t1, 0x12340000 | \idx
  \op  t2, t0, t1
  li   t1, 0xFFFFFFE0 | \idx
  \op  t2, t0, t1
  \op  x0, t0, t1
.endm
.macro sb_imm op, idx
  li   t0, 0
  \op  t2, t0, \idx
  li   t0, -1
  \op  t2, t0, \idx
  li   t0, 0x5A5A5A5A
  \op  t2, t0, \idx
  li   t0, 0xA5A5A5A5
  \op  t2, t0, \idx
  \op  x0, t0, \idx
.endm
.macro sb_set op
  sb_reg \op, 0
  sb_reg \op, 7
  sb_reg \op, 16
  sb_reg \op, 31
.endm
.macro sbi_set op
  sb_imm \op, 0
  sb_imm \op, 7
  sb_imm \op, 16
  sb_imm \op, 31
.endm
_start:
  sb_set  bclr
  sb_set  bset
  sb_set  binv
  sb_set  bext
  sbi_set bclri
  sbi_set bseti
  sbi_set binvi
  sbi_set bexti
# binv then binv on the same rd and index (both forms, and mixed): the bit returns to its prior state
  li   t0, 0x00000F0F
  li   t1, 3
  binv t3, t0, t1
  binv t3, t3, t1
  binvi t4, t0, 9
  binvi t4, t4, 9
  binv t5, t0, t1
  binvi t5, t5, 3
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
