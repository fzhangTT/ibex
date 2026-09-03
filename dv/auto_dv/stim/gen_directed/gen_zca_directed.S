# gen_zca_directed.S: every Zca (RVC) instruction form the coverage plan lists, at a word-aligned and at a half-aligned pc, each
# followed once by a 16-bit and once by a 32-bit instruction, with the 3-bit register field over x8..x15 and the 5-bit field over
# the classes x1, x2, x3..x7, x8..x15, x16..x31; c.jal / c.j / c.jr / c.jalr / c.beqz / c.bnez taken and not taken, a 32-bit
# instruction at a half-aligned pc (a straddle). The lock-step model checks every result; the run exists for gen_cmp_zca_cg.
# 1 to tohost at the end.
.option rvc
.macro nop32
  .option push
  .option norvc
  nop
  .option pop
.endm
.macro body
  la   sp, stack_top
  la   s0, buf
  c.mv s1, s0
  c.mv a0, s0
  c.mv a1, s0
  c.mv a2, s0
  c.mv a3, s0
  c.mv a4, s0
  c.mv a5, s0
  # CIW / CL / CS over the 3-bit field x8..x15
  c.addi4spn s0, sp, 4
  nop32
  c.addi4spn s1, sp, 8
  c.addi4spn a0, sp, 12
  c.addi4spn a1, sp, 16
  c.addi4spn a2, sp, 20
  c.addi4spn a3, sp, 24
  c.addi4spn a4, sp, 28
  c.addi4spn a5, sp, 32
  la   s0, buf
  c.mv s1, s0
  c.mv a0, s0
  c.mv a1, s0
  c.mv a2, s0
  c.mv a3, s0
  c.mv a4, s0
  c.mv a5, s0
  c.sw s0, 0(s0)
  nop32
  c.sw s1, 4(s1)
  c.sw a0, 8(a0)
  c.sw a1, 12(a1)
  c.sw a2, 16(a2)
  c.sw a3, 20(a3)
  c.sw a4, 24(a4)
  c.sw a5, 28(a5)
  c.lw s0, 0(s0)
  nop32
  la   s0, buf
  c.lw s1, 4(s1)
  c.mv s1, s0
  c.lw a0, 8(a0)
  c.lw a1, 12(a1)
  c.lw a2, 16(a2)
  c.lw a3, 20(a3)
  c.lw a4, 24(a4)
  c.lw a5, 28(a5)
  c.mv a0, s0
  c.mv a1, s0
  c.mv a2, s0
  c.mv a3, s0
  c.mv a4, s0
  c.mv a5, s0
  # CB / CA arithmetic over the 3-bit field
  c.srli s0, 1
  nop32
  c.srli s1, 2
  c.srli a0, 3
  c.srli a1, 4
  c.srli a2, 5
  c.srli a3, 6
  c.srli a4, 7
  c.srli a5, 8
  c.srai s0, 1
  nop32
  c.srai s1, 2
  c.srai a0, 3
  c.srai a1, 4
  c.srai a2, 5
  c.srai a3, 6
  c.srai a4, 7
  c.srai a5, 8
  c.andi s0, 15
  nop32
  c.andi s1, -1
  c.andi a0, 7
  c.andi a1, 3
  c.andi a2, 1
  c.andi a3, -16
  c.andi a4, 31
  c.andi a5, 0
  c.sub  s0, s1
  nop32
  c.sub  s1, a0
  c.sub  a0, a1
  c.sub  a1, a2
  c.sub  a2, a3
  c.sub  a3, a4
  c.sub  a4, a5
  c.sub  a5, s0
  c.xor  s0, a5
  nop32
  c.xor  s1, a4
  c.xor  a0, a3
  c.xor  a1, a2
  c.xor  a2, a1
  c.xor  a3, a0
  c.xor  a4, s1
  c.xor  a5, s0
  c.or   s0, s1
  nop32
  c.or   s1, a0
  c.or   a0, a1
  c.or   a1, a2
  c.or   a2, a3
  c.or   a3, a4
  c.or   a4, a5
  c.or   a5, s0
  c.and  s0, s1
  nop32
  c.and  s1, a0
  c.and  a0, a1
  c.and  a1, a2
  c.and  a2, a3
  c.and  a3, a4
  c.and  a4, a5
  c.and  a5, s0
  # CB branches over the 3-bit field: taken and not taken
  c.li   s0, 0
  c.li   s1, 1
  c.li   a0, 0
  c.li   a1, 1
  c.li   a2, 0
  c.li   a3, 1
  c.li   a4, 0
  c.li   a5, 1
  c.beqz s0, 1f
  nop32
1:
  c.beqz s1, 2f
  nop32
2:
  c.bnez a0, 3f
  c.nop
3:
  c.bnez a1, 4f
  c.nop
4:
  c.beqz a2, 5f
  c.nop
5:
  c.bnez a3, 6f
  nop32
6:
  c.beqz a4, 7f
  c.beqz a5, 7f
  c.bnez a4, 7f
7:
  c.bnez a5, 8f
  c.nop
8:
  # CI / CR forms over the 5-bit classes: x1, x2, x3..x7, x8..x15, x16..x31
  c.addi ra, 1
  nop32
  c.addi sp, -16
  c.addi t0, 2
  c.addi a0, 3
  c.addi s2, 4
  c.addi sp, 16
  c.li   ra, 5
  nop32
  c.li   t0, 6
  c.li   a0, 7
  c.li   s2, 8
  c.lui  ra, 1
  nop32
  c.lui  t0, 2
  c.lui  a0, 3
  c.lui  s2, 4
  c.addi16sp sp, -32
  nop32
  c.addi16sp sp, 32
  c.slli ra, 1
  nop32
  c.slli t0, 2
  c.slli a0, 3
  c.slli s2, 4
  c.mv   ra, a0
  nop32
  c.mv   t0, a0
  c.mv   a0, t0
  c.mv   s2, a0
  c.add  ra, t0
  nop32
  c.add  t0, ra
  c.add  a0, s2
  c.add  s2, a0
  c.swsp ra, 0(sp)
  nop32
  c.swsp sp, 4(sp)
  c.swsp t0, 8(sp)
  c.swsp a0, 12(sp)
  c.swsp s2, 16(sp)
  c.lwsp ra, 0(sp)
  nop32
  c.lwsp t0, 8(sp)
  c.lwsp a0, 12(sp)
  c.lwsp s2, 16(sp)
  c.nop
  nop32
  c.nop
  c.nop
  # jumps: c.jal / c.j / c.jr / c.jalr over the register classes
  c.jal  9f
  nop32
9:
  c.j    10f
  c.nop
10:
  la   ra, 11f
  c.jr   ra
  nop32
11:
  la   t0, 12f
  c.jr   t0
  c.nop
12:
  la   a0, 13f
  c.jr   a0
  c.nop
13:
  la   s2, 14f
  c.jr   s2
  c.nop
14:
  la   t0, 15f
  c.jalr t0
  nop32
15:
  la   a0, 16f
  c.jalr a0
  c.nop
16:
  la   s2, 17f
  c.jalr s2
  c.nop
17:
  la   ra, 18f
  c.jalr ra
  c.nop
18:
  c.nop
.endm

.section .text
.globl _start
_start:
  .balign 4
  body                    # word-aligned start
  .balign 4
  c.nop                   # half-aligned start
  body
  .balign 4
  c.nop
  nop32                   # a 32-bit instruction at a half-aligned pc: the straddle
  .balign 4
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
buf:      .space 64
stack:    .space 128
stack_top:
