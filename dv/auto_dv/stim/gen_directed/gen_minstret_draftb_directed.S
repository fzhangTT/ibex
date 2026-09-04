# gen_minstret_draftb_directed.S: a minstreth write back to back after a draft-B instruction (grevi x7, x5, 8: the model cannot
# execute it, the scoreboard computes the reference and returns before the record's bookkeeping), then minstret / minstreth
# reads; the same write after a plain instruction as the control. The high-word write reloads the low word with its
# pre-increment value when an instruction retires in the write cycle, and the model measures that gap from the previous
# RECORD, so the record before the write must have updated it whatever path compared it (CM123-L-1). The lock-step compare on
# the reads is the red / green. 1 to tohost at the end, then spin.
.section .text
.globl _start
_start:
  li   x5, 0x12345678
  .word 0x6882d393                     # grevi x7, x5, 8 (draft-B: opcode OP-IMM, funct3 101, imm[11:5] 0110100)
  csrw minstreth, x0                # back to back after the draft-B record
  csrr t0, minstret
  csrr t1, minstreth
  nop
  .word 0x6882d393
  csrw minstreth, x0
  csrr t2, minstret
  nop
  csrw minstreth, x0                # the control: a plain instruction retiring in the write cycle
  csrr t3, minstret
  csrr t4, minstreth
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
