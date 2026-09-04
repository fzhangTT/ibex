# gen_intg_span_directed.S: one misaligned lw that spans two bus words, both halves carrying an injected integrity error (the
# cocotb test gen_ut_intg_span arms two corruptions on the buffer), so the DUT suppresses the write and takes the internal NMI;
# then a clean lw of the second word. The T-183 gate must consume BOTH announced words at the spanning load: a
# leftover second word would let a lying suppress on the later clean load pass (the TB mutant MUT-SUP3 is the red). The NMI
# vector table is one mret per entry. 1 to tohost at the end, then spin.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  la   a0, gen_span_buf
  lw   a1, 2(a0)                    # spans gen_span_buf+0 and +4: two bus accesses, both corrupted
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  lw   a2, 4(a0)                    # the clean load of the second word (MUT-SUP3 asserts the suppress flag on this record)
  nop
  nop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.option push
.option norvc
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
.globl gen_span_buf
gen_span_buf: .word 0x11111111, 0x22222222, 0x33333333, 0x44444444
