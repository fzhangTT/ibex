# gen_div_timing_directed.S: the divider's neighbours for gen_div_timing_cg (CG-MUL-004): every one of div / divu / rem / remu
# preceded by an ALU op, a multiply, a divide, a dependent load and a store, and followed by a dependent ALU op, a multiply, a
# divide and a store; a zero and a nonzero divisor under data-independent timing off and on; then a long run of divides for the
# irq, NMI and debug-request regimes of the run (the events land inside the divides' windows). Interrupts are enabled; the vector
# table is one mret per entry, debug requests return through the debug ROM. 1 to tohost at the end.
.macro neighbours op
  add   t4, a1, a2                  # prev alu
  \op   t0, a1, a2
  add   t1, t0, a2                  # next dep_alu
  mul   t4, a1, a2                  # prev mul
  \op   t0, a1, a2
  mul   t1, a1, t0                  # next mul
  div   t4, a1, a2                  # prev div
  \op   t0, a1, a2
  divu  t1, a1, a2                  # next div
  lw    t3, 4(a0)                   # prev load_dep (rs1)
  \op   t0, t3, a2
  sw    t0, 12(a0)                  # next other
  lw    t3, 8(a0)                   # prev load_dep (rs2)
  \op   t0, a1, t3
  sw    t0, 16(a0)                  # prev other for the next one
  \op   t0, a1, a3                  # zero divisor
  sub   t1, a1, t0                  # next dep_alu
.endm
.option push
.option norvc
.section .text
.globl _start
_start:
  la    t0, gen_vec
  ori   t0, t0, 1
  csrw  mtvec, t0
  li    t0, 0x7FFF0888
  csrw  mie, t0
  csrsi mstatus, 8
  la    a0, gen_div_buf
  li    a1, 100
  li    a2, 7
  li    a3, 0
  # data-independent timing off: the zero divisor takes the fast path
  neighbours div
  neighbours divu
  neighbours rem
  neighbours remu
  # data-independent timing on: every divide takes the full count
  csrsi 0x7c0, 2
  neighbours div
  neighbours divu
  neighbours rem
  neighbours remu
  csrci 0x7c0, 2
  # the long runs: the run's event regimes land inside these windows, data-independent timing off then on
  li    a4, 60
loop:
  div   t0, a1, a2
  divu  t1, a1, a3
  rem   t2, a1, a2
  remu  t3, a1, a2
  addi  a4, a4, -1
  bnez  a4, loop
  csrsi 0x7c0, 2
  li    a4, 60
loop2:
  div   t0, a1, a3
  divu  t1, a1, a2
  rem   t2, a1, a3
  remu  t3, a1, a2
  addi  a4, a4, -1
  bnez  a4, loop2
  csrci 0x7c0, 2
  la    t5, tohost
  li    t6, 1
  sw    t6, 0(t5)
spin:
  j     spin

.balign 256
gen_vec:
  .rept 32
  mret
  .endr
.option pop

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 16
gen_div_buf: .word 0x11111111, 0x00000063, 0x00000009, 0x44444444, 0, 0, 0, 0
