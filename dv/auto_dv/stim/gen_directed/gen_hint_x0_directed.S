# gen_hint_x0_directed.S: the x0-destination writers of gen_isa_hint_x0_cg (CG-ISA-005): every 32-bit HINT class the plan
# names and every writer class (immediate and register ALU, shifts, U-type, load, CSR read, jal / jalr, multiply, divide,
# one- and two-cycle bit ops, the compressed hints), each followed by a reader of x0 through rs1, through rs2, or by an
# instruction that reads no register. The lock-step model checks that every later read of x0 returns 0. 1 to tohost at the end.
.option push
.option norvc
.section .text
.globl _start
_start:
  li    t1, 0x1234
  li    t2, 0x77
  la    a0, gen_hint_buf
  # alu_imm: the canonical nop, addi with rs1 / imm nonzero, andi, ori, xori, slti, sltiu
  addi  x0, x0, 0
  add   t0, x0, t1                   # rs1 reads x0
  addi  x0, t1, 0
  add   t0, t1, x0                   # rs2 reads x0
  addi  x0, x0, 5
  lui   t0, 1                        # reads no register
  andi  x0, t1, 0xff
  add   t0, x0, t1
  ori   x0, t1, 1
  add   t0, t1, x0
  xori  x0, t1, 1
  lui   t0, 2
  slti  x0, t1, 1
  add   t0, x0, t1
  sltiu x0, t1, 1
  add   t0, t1, x0
  # shift: the two semihosting hints, other slli / srai, srli
  slli  x0, x0, 0x1f
  add   t0, x0, t1
  srai  x0, x0, 7
  add   t0, t1, x0
  slli  x0, t1, 3
  lui   t0, 3
  srai  x0, t1, 3
  add   t0, x0, t1
  srli  x0, t1, 3
  add   t0, t1, x0
  # alu_reg: add sub sll srl sra slt sltu xor or and
  add   x0, t1, t2
  add   t0, x0, t1
  sub   x0, t1, t2
  add   t0, t1, x0
  sll   x0, t1, t2
  lui   t0, 4
  srl   x0, t1, t2
  add   t0, x0, t1
  sra   x0, t1, t2
  add   t0, t1, x0
  slt   x0, t1, t2
  lui   t0, 5
  sltu  x0, t1, t2
  add   t0, x0, t1
  xor   x0, t1, t2
  add   t0, t1, x0
  or    x0, t1, t2
  lui   t0, 6
  and   x0, t1, t2
  add   t0, x0, t1
  # lui_auipc
  lui   x0, 0x12345
  add   t0, x0, t1
  auipc x0, 0
  add   t0, t1, x0
  lui   x0, 1
  lui   t0, 7
  # load
  lw    x0, 0(a0)
  add   t0, x0, t1
  lw    x0, 4(a0)
  add   t0, t1, x0
  lh    x0, 2(a0)
  lui   t0, 8
  # csrr
  csrr  x0, mcycle
  add   t0, x0, t1
  csrr  x0, minstret
  add   t0, t1, x0
  csrr  x0, mhartid
  lui   t0, 9
  # jal with rd = x0 (j), each landing on its reader
  j     1f
1:
  add   t0, x0, t1
  j     2f
2:
  add   t0, t1, x0
  j     3f
3:
  lui   t0, 10
  # jalr with rd = x0 (jr)
  la    t3, 4f
  jr    t3
4:
  add   t0, x0, t1
  la    t3, 5f
  jr    t3
5:
  add   t0, t1, x0
  la    t3, 6f
  jr    t3
6:
  lui   t0, 11
  # mul, mulh class
  mul   x0, t1, t2
  add   t0, x0, t1
  mul   x0, t1, t2
  add   t0, t1, x0
  mul   x0, t1, t2
  lui   t0, 12
  mulh  x0, t1, t2
  add   t0, x0, t1
  mulhsu x0, t1, t2
  add   t0, t1, x0
  mulhu x0, t1, t2
  lui   t0, 13
  # div_rem
  div   x0, t1, t2
  add   t0, x0, t1
  divu  x0, t1, t2
  add   t0, t1, x0
  rem   x0, t1, t2
  lui   t0, 14
  remu  x0, t1, t2
  add   t0, x0, t1
  # bit_1cyc: andn, sh1add, clz, min
  andn  x0, t1, t2
  add   t0, x0, t1
  sh1add x0, t1, t2
  add   t0, t1, x0
  clz   x0, t1
  lui   t0, 15
  min   x0, t1, t2
  add   t0, x0, t1
  # bit_2cyc: rol, ror, rori
  rol   x0, t1, t2
  add   t0, x0, t1
  ror   x0, t1, t2
  add   t0, t1, x0
  rori  x0, t1, 5
  lui   t0, 16
  # compressed hints: c.li x0, c.lui x0, c.slli x0, c.mv x0, c.add x0 (explicit encodings: the rd = x0 forms are HINTs the assembler does not emit)
  .2byte 0x4015                      # c.li x0, 5
  add   t0, x0, t1
  .2byte 0x6005                      # c.lui x0, 1
  add   t0, t1, x0
  .2byte 0x0006                      # c.slli x0, 1
  lui   t0, 17
  .2byte 0x802a                      # c.mv x0, a0
  add   t0, x0, t1
  .2byte 0x902a                      # c.add x0, a0
  add   t0, t1, x0
  .2byte 0x4015                      # c.li x0, 5
  lui   t0, 18
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
.balign 16
gen_hint_buf: .word 0x11111111, 0x22222222, 0x33333333, 0x44444444
