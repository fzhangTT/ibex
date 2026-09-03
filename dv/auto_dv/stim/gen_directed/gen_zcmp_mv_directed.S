# gen_zcmp_mv_directed.S: cm.mva01s over every (r1s', r2s') pair and cm.mvsa01 over every pair with r1s' != r2s', the two forms
# back to back in both orders, a load and an ALU writer of a source immediately before a move, equal and distinct source values.
# The 16-bit encodings are emitted directly (101 011 r1s' 01/11 r2s' 10). The lock-step model checks both moves; the run exists
# for gen_cmp_zcmp_mv_cg (the reserved cm.mvsa01 with r1s' == r2s' is gen_zcmp_mv_reserved_directed.S). 1 to tohost at the end.
.macro mva01s r1, r2
  .2byte 0xAC62 | (\r1 << 7) | (\r2 << 2)
.endm
.macro mvsa01 r1, r2
  .2byte 0xAC22 | (\r1 << 7) | (\r2 << 2)
.endm
.macro sregs
  li   s0, 0x10000001
  li   s1, 0x10000002
  li   s2, 0x10000003
  li   s3, 0x10000004
  li   s4, 0x10000005
  li   s5, 0x10000006
  li   s6, 0x10000007
  li   s7, 0x10000008
.endm
.section .text
.globl _start
_start:
  la   sp, stack_top
  sregs
  li   a0, 0x0A000000
  li   a1, 0x0A000001
# every cm.mva01s pair (r1s' == r2s' gives equal source values)
  .irp r1, 0, 1, 2, 3, 4, 5, 6, 7
  .irp r2, 0, 1, 2, 3, 4, 5, 6, 7
  mva01s \r1, \r2
  .endr
  .endr
# every legal cm.mvsa01 pair; the sources a0 / a1 are distinct here
  sregs
  li   a0, 0x0A000000
  li   a1, 0x0A000001
  .irp r1, 0, 1, 2, 3, 4, 5, 6, 7
  .irp r2, 0, 1, 2, 3, 4, 5, 6, 7
  .if \r1 != \r2
  mvsa01 \r1, \r2
  .endif
  .endr
  .endr
# equal source values for cm.mvsa01 (a0 == a1)
  li   a0, 0x0B000000
  li   a1, 0x0B000000
  mvsa01 0, 1
  mvsa01 2, 3
# back to back, both orders (the second of each pair also reads what the first wrote: an ALU hazard for cm.mvsa01)
  sregs
  li   a0, 0x0C000000
  li   a1, 0x0C000001
  mvsa01 0, 1
  mva01s 2, 3
  nop
  mva01s 4, 5
  mvsa01 6, 7
  nop
# a load then a move that reads the loaded register; an ALU op then a move that reads its result
  sw   s1, 0(sp)
  sw   a1, 4(sp)
  lw   s0, 0(sp)
  mva01s 0, 1
  addi s2, s2, 1
  mva01s 2, 3
  lw   a0, 4(sp)
  mvsa01 0, 1
  addi a1, a1, 1
  mvsa01 2, 3
  nop
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
.balign 16
stack:    .space 64
stack_top:
