# gen_zcmp_directed.S: every Zcmp stack instruction (cm.push, cm.pop, cm.popret, cm.popretz) over every rlist 4..15 and spimm 0..3:
# push / pop pairs in the main flow, popret and popretz as the tail of called functions (word-aligned and half-aligned return
# addresses, one odd return address); a misaligned sp is gen_zcmp_misaligned_directed.S and dummy instructions are
# gen_zcmp_dummy_directed.S. The 16-bit encodings are emitted directly (101 kind rlist spimm 10). The lock-step model checks
# every micro-op; the run exists for gen_cmp_zcmp_pushpop_cg. 1 to tohost at the end.
.macro cm_insn kind, rlist, spimm
  .2byte 0xB002 | (\kind << 8) | (\rlist << 4) | (\spimm << 2)
.endm
.set PUSH, 0x18
.set POP, 0x1A
.set POPRETZ, 0x1C
.set POPRET, 0x1E
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
  # ---- push / pop pairs, every rlist and spimm
  .irp rl, 4,5,6,7,8,9,10,11,12,13,14,15
  .irp sp_, 0,1,2,3
  cm_insn PUSH, \rl, \sp_
  cm_insn POP, \rl, \sp_
  .endr
  .endr
  # ---- popret / popretz through calls: a word-aligned and a half-aligned return address
  .irp rl, 4,5,6,7,8,9,10,11,12,13,14,15
  .irp sp_, 0,1,2,3
  .balign 4
  jal  ra, fret\rl\sp_
  .balign 4
  c.nop
  jal  ra, fretz\rl\sp_
  .endr
  .endr
  # ---- an odd return address: ra = the label + 1, cleared by the return
  la   ra, odd_ret
  addi ra, ra, 1
  j    fodd
odd_ret:
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin
  # ---- the functions: push, then popret (returns) / popretz (returns with a0 = 0)
  .irp rl, 4,5,6,7,8,9,10,11,12,13,14,15
  .irp sp_, 0,1,2,3
fret\rl\sp_:
  cm_insn PUSH, \rl, \sp_
  cm_insn POPRET, \rl, \sp_
fretz\rl\sp_:
  cm_insn PUSH, \rl, \sp_
  cm_insn POPRETZ, \rl, \sp_
  .endr
  .endr
fodd:
  cm_insn PUSH, 5, 0
  cm_insn POPRET, 5, 0

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 16
stack:    .space 512
stack_top:
