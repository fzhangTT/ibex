# gen_zcmp_irq_directed.S: Zcmp sequences under interrupts (T-134 red/green). Every implemented interrupt is enabled
# (mie all-ones, MIE), every vector entry is a cm.push followed by a 2-byte jump to the common tail (cm.pop, mret), so
# the handler's FIRST record is a non-last Zcmp micro-op carrying rvfi_intr, and the loop body is a cm.push / cm.pop pair,
# so interrupts also split sequences (rtl-arch R9). 300 iterations, then 1 to tohost.
.include "gen_zc_insn.h"

.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  la   sp, gen_stack_top
  li   ra, 0x11111111
  li   s0, 0x22222222
  li   s1, 0x33333333
  li   s2, 0x44444444
  li   t0, -1
  csrw mie, t0
  csrsi mstatus, 8
  li   x6, 300
loop:
  cm_push 7, 0
  addi x5, x5, 1
  cm_pop 7, 0
  bne  x5, x6, loop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

handler_tail:
  cm_pop 7, 0
  mret

.balign 256
gen_vec:
  .rept 32
  cm_push 7, 0                      # 2 bytes: the handler's first record is a Zcmp micro-op
  c.j  handler_tail                 # 2 bytes: entry size stays 4
  .endr

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.align 4
gen_stack:   .fill 128, 1, 0
.globl gen_stack_top
gen_stack_top:
