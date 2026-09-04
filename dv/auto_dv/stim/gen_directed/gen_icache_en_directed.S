# gen_icache_en_directed.S: enables the instruction cache (cpuctrlsts.icache_enable) and runs a short loop twice so lines are
# allocated (tag and data RAM writes) and then hit; the run exists as the stimulus of the icram protocol rows (sva_icram_*) and their
# mutant. 1 to tohost at the end.
.section .text
.globl _start
_start:
  li   t0, 1
  csrs 0x7C0, t0
  fence.i
  li   t1, 2
outer:
  li   t2, 16
  li   t3, 0
inner:
  addi t3, t3, 3
  xori t3, t3, 5
  addi t2, t2, -1
  bnez t2, inner
  addi t1, t1, -1
  bnez t1, outer
  csrc 0x7C0, t0
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
