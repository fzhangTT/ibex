# gen_branch_directed.S: every conditional branch (beq, bne, blt, bge, bltu, bgeu, c.beqz, c.bnez) over the plan's operand classes
# in both outcomes, forward and backward offsets, the maximal offsets, word- and half-aligned targets. The 32-bit forms are kept
# uncompressed (.option norvc, norelax) so target alignment is controlled (the word alignments pad with a c.nop, which needs rvc
# enabled for the directive); c.beqz / c.bnez are emitted explicitly. The lock-step model
# checks every outcome; the run exists for gen_isa_branch_cg. 1 to tohost at the end.
.option norvc
.option norelax
.section .text
.globl _start
# forward branch to a word-aligned target (taken or not by the operand class)
.macro brf op, a, b
  li   t0, \a
  li   t1, \b
  .option push
  .option rvc
  .balign 4
  .option pop
  \op  t0, t1, 1f
  nop
1:
.endm
# backward branch (the target precedes it; taken once, then the sequence continues)
.macro brb op, a, b
  li   t0, \a
  li   t1, \b
  j    2f
1:
  j    3f
2:
  \op  t0, t1, 1b
3:
.endm
# forward branch to a half-aligned target (a 16-bit nop between the branch and the target)
.macro brh op, a, b
  li   t0, \a
  li   t1, \b
  .option push
  .option rvc
  .balign 4
  .option pop
  \op  t0, t1, 1f
  .option push
  .option rvc
  c.nop
  .option pop
1:
.endm
# the operand classes: equal, intmin_zero, zero_intmin, zero_ones, ones_zero, both_msb_eq, slt_ugt, sgt_ult, rand (two orders)
.macro brset op
  brf \op, 5, 5
  brb \op, 5, 5
  brh \op, 5, 5
  brf \op, 0x80000000, 0
  brb \op, 0x80000000, 0
  brh \op, 0x80000000, 0
  brf \op, 0, 0x80000000
  brb \op, 0, 0x80000000
  brh \op, 0, 0x80000000
  brf \op, 0, -1
  brb \op, 0, -1
  brh \op, 0, -1
  brf \op, -1, 0
  brb \op, -1, 0
  brh \op, -1, 0
  brf \op, 0x80000000, 0x80000000
  brb \op, 0x80000000, 0x80000000
  brh \op, 0x80000000, 0x80000000
  brf \op, -2, 1
  brb \op, -2, 1
  brh \op, -2, 1
  brf \op, 1, -2
  brb \op, 1, -2
  brh \op, 1, -2
  brf \op, 7, 3
  brb \op, 7, 3
  brh \op, 7, 3
  brf \op, 3, 7
  brb \op, 3, 7
  brh \op, 3, 7
.endm
# c.beqz / c.bnez (rs1 in s0): forward half-aligned target, forward word-aligned target, backward target
.macro cbf op, a
  li   s0, \a
  .option push
  .option rvc
  .balign 4
  .option pop
  .option push
  .option rvc
  \op  s0, 1f
  .option pop
  nop
1:
.endm
.macro cbw op, a
  li   s0, \a
  .option push
  .option rvc
  .balign 4
  .option pop
  .option push
  .option rvc
  \op  s0, 1f
  c.nop
  .option pop
  nop
1:
.endm
.macro cbb op, a
  li   s0, \a
  j    2f
1:
  j    3f
2:
  .option push
  .option rvc
  \op  s0, 1b
  .option pop
3:
.endm
.macro cbset op
  cbf \op, 0
  cbw \op, 0
  cbb \op, 0
  cbf \op, 0x80000000
  cbw \op, 0x80000000
  cbb \op, 0x80000000
  cbf \op, -1
  cbw \op, -1
  cbb \op, -1
  cbf \op, -2
  cbw \op, -2
  cbb \op, -2
  cbf \op, 5
  cbw \op, 5
  cbb \op, 5
.endm
_start:
  brset beq
  brset bne
  brset blt
  brset bge
  brset bltu
  brset bgeu
  cbset c.beqz
  cbset c.bnez
# maximal forward offset (+4094, a half-aligned target): beq taken, bne not taken (the padding is executed); raw encodings, since
# the assembler widens a branch whose target sits at the range limit
  li   t0, 9
  li   t1, 9
  .option push
  .option rvc
  .balign 4
  .option pop
  .word 0x7e628fe3
  .fill 1022, 4, 0x00000013
  .2byte 0x0001
  .option push
  .option rvc
  .balign 4
  .option pop
  .word 0x7e629fe3
  .fill 1022, 4, 0x00000013
  .2byte 0x0001
# maximal backward offset (-4096): bne taken, beq not taken
  li   t0, 9
  li   t1, 8
  j    4f
  .option push
  .option rvc
  .balign 4
  .option pop
3:
  j    5f
  .fill 1023, 4, 0x00000013
4:
  bne  t0, t1, 3b
5:
  j    7f
  .option push
  .option rvc
  .balign 4
  .option pop
6:
  j    8f
  .fill 1023, 4, 0x00000013
7:
  beq  t0, t1, 6b
8:
# c.beqz maximal offsets: +254 (taken, raw encoding) and -256 (taken)
  li   s0, 0
  .option push
  .option rvc
  .balign 4
  .option pop
  .2byte 0xcc7d
  .fill 63, 4, 0x00000013
  j    3f
  .option push
  .option rvc
  .balign 4
  .option pop
2:
  j    4f
  .fill 63, 4, 0x00000013
3:
  .option push
  .option rvc
  c.beqz s0, 2b
  .option pop
4:
# c.bnez maximal offsets: +254 (taken, raw encoding) and -256 (taken)
  li   s0, 3
  .option push
  .option rvc
  .balign 4
  .option pop
  .2byte 0xec7d
  .fill 63, 4, 0x00000013
  j    3f
  .option push
  .option rvc
  .balign 4
  .option pop
2:
  j    4f
  .fill 63, 4, 0x00000013
3:
  .option push
  .option rvc
  c.bnez s0, 2b
  .option pop
4:
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
