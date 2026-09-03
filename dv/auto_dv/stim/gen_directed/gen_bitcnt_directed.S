# gen_bitcnt_directed.S: clz / ctz / cpop over the operand classes the coverage plan names (0, all ones, INT_MIN, 1, 0x55555555,
# 0xAAAAAAAA, INT_MAX, two random-looking values) and over every single-bit value (a walking one), each with rd = x0 as well.
# The lock-step model checks every result; the run exists for gen_bit_count_cg. 1 to tohost at the end.
.section .text
.globl _start
_start:
  la   a0, tab
  li   s0, 0
tloop:
  slli t1, s0, 2
  add  t1, t1, a0
  lw   a1, 0(t1)
  clz  a3, a1
  ctz  a3, a1
  cpop a3, a1
  clz  x0, a1
  ctz  x0, a1
  cpop x0, a1
  addi s0, s0, 1
  li   t3, 9
  bne  s0, t3, tloop
  li   a1, 1
  li   s0, 0
bloop:
  clz  a3, a1
  ctz  a3, a1
  cpop a3, a1
  clz  x0, a1
  cpop x0, a1
  slli a1, a1, 1
  addi s0, s0, 1
  li   t3, 32
  bne  s0, t3, bloop
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
  .word 0x00000000, 0xFFFFFFFF, 0x80000000, 0x00000001, 0x55555555, 0xAAAAAAAA, 0x7FFFFFFF, 0x12345678, 0x9ABCDEF0
