# gen_zcmp_misaligned_directed.S: cm.push / cm.pop pairs with the stack pointer misaligned by 1, 2 and 3 bytes (every stack access
# splits into two bus transactions). Kept apart from gen_zcmp_directed.S: the lock-step comparator's Zcmp fold counts the split
# accesses per transaction on the DUT side and per access on the model side (finding recorded for landing 2c). 1 to tohost at the end.
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
  li   ra, 0xDDDDDDD0
  addi sp, sp, 1
  cm_insn PUSH, 6, 0
  cm_insn POP, 6, 0
  addi sp, sp, 1
  cm_insn PUSH, 9, 1
  cm_insn POP, 9, 1
  addi sp, sp, 1
  cm_insn PUSH, 15, 3
  cm_insn POP, 15, 3
  addi sp, sp, -3
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
