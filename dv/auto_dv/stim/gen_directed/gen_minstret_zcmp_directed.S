# gen_minstret_zcmp_directed.S: a minstreth write back to back after a Zcmp sequence (cm.push, then cm.pop), each followed by
# minstret / minstreth reads, and the same write after a plain instruction as the control. The high-word write reloads the low
# word with its pre-increment value when an instruction retires in the write cycle; the model measures that gap from the previous
# RECORD, so the gap after a folded Zcmp sequence must come from its last micro-op, not from the record before the sequence
# The lock-step compare on the reads is the red / green. 1 to tohost at the end, then spin.
.macro cm_insn kind, rlist, spimm
  .2byte 0xB002 | (\kind << 8) | (\rlist << 4) | (\spimm << 2)
.endm
.set PUSH, 0x18
.set POP, 0x1A
.section .text
.globl _start
_start:
  la   sp, stack_top
  li   ra, 0x12345678
  cm_insn PUSH, 4, 0                # cm.push {ra}, -16
  csrw minstreth, x0                # back to back after the sequence's last micro-op
  csrr t0, minstret
  csrr t1, minstreth
  cm_insn POP, 4, 0                 # cm.pop {ra}, 16
  csrw minstreth, x0
  csrr t2, minstret
  csrr t3, minstreth
  cm_insn PUSH, 6, 1                # cm.push {ra, s0-s1}, -32
  csrw minstreth, x0
  csrr t4, minstret
  cm_insn POP, 6, 1                 # cm.pop {ra, s0-s1}, 32
  nop
  csrw minstreth, x0                # the control: a plain instruction retiring in the write cycle
  csrr t5, minstret
  csrr t6, minstreth
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
stack:    .space 128
stack_top:
