# gen_zcmp_mv_reserved_directed.S: cm.mvsa01 with r1s' == r2s', a reserved encoding (zcmp.adoc norm:cm-mvsa01_res, the plan's B4
# candidate). Ibex executes it as two moves into the same register (the second wins: s0 = a1); the Spike model raises an illegal
# instruction, so the lock-step comparator flags the record. The run is the retained reproduction of that divergence. 1 to tohost.
.macro mvsa01 r1, r2
  .2byte 0xAC22 | (\r1 << 7) | (\r2 << 2)
.endm
.section .text
.globl _start
_start:
  li   a0, 0x0A000000
  li   a1, 0x0A000001
  li   s0, 0x10000001
  mvsa01 0, 0
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
