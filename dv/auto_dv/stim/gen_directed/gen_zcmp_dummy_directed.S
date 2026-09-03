# gen_zcmp_dummy_directed.S: cm.push / cm.pop pairs with cpuctrlsts.dummy_instr_en set (dummy instructions inserted into the
# micro-op stream). Kept apart from gen_zcmp_directed.S: under dummy insertion the DUT's RVFI stream of a Zcmp sequence loses
# micro-op records and a pop returns a wrong register value, which the lock-step comparator flags (isa_mem / isa_rd); the run is
# the reproduction of that finding. 1 to tohost at the end.
.macro cm_insn kind, rlist, spimm
  .2byte 0xB002 | (\kind << 8) | (\rlist << 4) | (\spimm << 2)
.endm
.set PUSH, 0x18
.set POP, 0x1A
.section .text
.globl _start
_start:
  la   sp, stack_top
  li   s0, 0x11111111
  li   s1, 0x22222222
  li   s2, 0x33333333
  li   s3, 0x44444444
  li   s4, 0x55555555
  li   s5, 0x66666666
  li   s6, 0x77777777
  li   s7, 0x88888888
  li   s8, 0x99999999
  li   s9, 0xAAAAAAAA
  li   s10, 0xBBBBBBBB
  li   s11, 0xCCCCCCCC
  li   ra, 0xDDDDDDD0
  li   t0, 4
  csrs 0x7C0, t0
  .irp rl, 4,8,12,15
  cm_insn PUSH, \rl, 2
  cm_insn POP, \rl, 2
  .endr
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
.balign 16
stack:    .space 256
stack_top:
