# gen_zcmp_trap_directed.S: a Zcmp sequence that traps (T-102c red/green for the trap-record length rule, plan C-1
# and C-12). The TB arms one bus error on the stack window before the core is released (bridge MEM_ERR_ARM), so the
# first cm.push store faults; the vectored mtvec table's entry 0 is an mret, which re-executes the cm.push, and the
# armed error is one-shot, so the loop completes and stores 1 to tohost.
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
  li   x6, 200
loop:
  cm_push 7, 0                      # {ra, s0-s2}, sp -= 16
  cm_pop 7, 0
  addi x5, x5, 1
  bne  x5, x6, loop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.balign 256
gen_vec:
  .rept 32
  mret
  .endr

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.align 4
gen_stack:   .fill 64, 1, 0
.globl gen_stack_top
gen_stack_top:
