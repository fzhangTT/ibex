# gen_isa_jump_directed.S: the jumps of gen_isa_jump_cg (CG-ISA-006): jal with every link class forward and backward, jalr
# with the immediate zero, 2047, -2048, odd, positive and negative even, from a base equal to and different from the link
# register, with even and odd targets, c.j / c.jal / c.jr / c.jalr, each op landing on a word-aligned and on a half-aligned
# target. The 1 MB offsets, an x0 base, the zero page and the high region and a wrap of the address space are not
# reachable from the program window at 0x80000080 (an unmapped fetch is a memory-model error). 1 to tohost at the end; the spin
# after it retires as a jal to itself.
.macro cj label
.option push
.option rvc
  c.j \label
.option pop
.endm
.macro cjal label
.option push
.option rvc
  c.jal \label
.option pop
.endm
.macro cjr reg
.option push
.option rvc
  c.jr \reg
.option pop
.endm
.macro cjalr reg
.option push
.option rvc
  c.jalr \reg
.option pop
.endm
.option push
.option norvc
.section .text
.globl _start
_start:
  # jal forward: rd x0 / x1 / x5 / other
  jal   x0, 1f
1:
  jal   ra, 2f
2:
  jal   t0, 3f
3:
  jal   t1, 4f
4:
  # jal backward: the same four link classes (each forward jump skips its backward partner)
  j     10f
11:
  jal   x0, 12f
10:
  jal   ra, 11b
12:
  j     13f
14:
  jal   t0, 15f
13:
  jal   t1, 14b
15:
  j     16f
17:
  j     18f
16:
  jal   x0, 17b
18:
  j     19f
20:
  jal   ra, 21f
19:
  jal   t0, 20b
21:
  # jal onto half-aligned targets
  jal   ra, 22f
  .2byte 0x0001
22:
  jal   x0, 23f
  .2byte 0x0001
23:
  .2byte 0x0001
  # jalr: base register different from the link register (other) and equal to it (eq_rd), each immediate class
  la    t0, 30f
  jalr  ra, 0(t0)
30:
  la    t0, 31f
  addi  t0, t0, -2047
  jalr  ra, 2047(t0)
31:
  la    t0, 32f
  addi  t0, t0, 2047
  addi  t0, t0, 1
  jalr  ra, -2048(t0)
32:
  la    t0, 33f
  addi  t0, t0, -3
  jalr  ra, 3(t0)
33:
  la    t0, 34f
  addi  t0, t0, -8
  jalr  ra, 8(t0)
34:
  la    t0, 35f
  addi  t0, t0, 8
  jalr  ra, -8(t0)
35:
  la    t0, 40f
  jalr  t0, 0(t0)
40:
  la    t0, 41f
  addi  t0, t0, -2047
  jalr  t0, 2047(t0)
41:
  la    t0, 42f
  addi  t0, t0, 2047
  addi  t0, t0, 1
  jalr  t0, -2048(t0)
42:
  la    t0, 43f
  addi  t0, t0, -5
  jalr  t0, 5(t0)
43:
  la    t0, 44f
  addi  t0, t0, -16
  jalr  t0, 16(t0)
44:
  la    t0, 45f
  addi  t0, t0, 16
  jalr  t0, -16(t0)
45:
  # jalr with rd x0 / x5 / other and odd targets (the low bit of the target is dropped)
  la    t0, 50f
  addi  t0, t0, 1
  jalr  x0, 0(t0)
50:
  la    t0, 51f
  addi  t0, t0, 1
  jalr  t1, 0(t0)
51:
  la    t0, 52f
  addi  t0, t0, -2
  jalr  t0, 3(t0)
52:
  la    t1, 53f
  jalr  x0, 0(t1)
53:
  la    t1, 54f
  jalr  t1, 0(t1)
54:
  # jalr onto half-aligned targets, even and odd
  la    t0, 55f
  jalr  ra, 0(t0)
  .2byte 0x0001
55:
  la    t0, 56f
  addi  t0, t0, 1
  jalr  ra, 0(t0)
  .2byte 0x0001
56:
  .2byte 0x0001
  # c.j, c.jal forward and backward, onto word and half targets
  cj    60f
60:
  cj    61f
  .2byte 0x0001
61:
  .2byte 0x0001
  cjal  62f
62:
  cjal  63f
  .2byte 0x0001
63:
  .2byte 0x0001
  j     64f
65:
  cj    66f
64:
  cj    65b
66:
  j     67f
68:
  cjal  69f
67:
  cjal  68b
69:
  # c.jr, c.jalr: even and odd targets, word and half targets
  la    t0, 70f
  cjr   t0
70:
  la    t0, 71f
  addi  t0, t0, 1
  cjr   t0
71:
  la    t0, 72f
  cjalr t0
72:
  la    t0, 73f
  addi  t0, t0, 1
  cjalr t0
73:
  la    t0, 74f
  cjr   t0
  .2byte 0x0001
74:
  la    t0, 75f
  cjalr t0
  .2byte 0x0001
75:
  .2byte 0x0001
  la    t5, tohost
  li    t6, 1
  sw    t6, 0(t5)
spin:
  j     spin
.option pop

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
