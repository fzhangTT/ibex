# gen_ebreak_directed.S: breakpoint exceptions from ebreak and c.ebreak at both alignments; the handler reads mcause, mtval
# and mepc into registers (compared by the lock-step model, rtl-arch R10: mcause 3, mtval 0, mepc = the [c.]ebreak's own
# pc), steps mepc past the 4- or 2-byte encoding and returns; ten rounds, then 1 to tohost. Any other trap ends with 3.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  li   s0, 0
  li   s1, 10
  li   s2, 0
loop:
  .option push
  .option norvc
  ebreak                            # 4-byte encoding (norvc keeps the assembler from compressing it)
  addi s0, s0, 1
  .option pop
  c.ebreak                          # 2-byte encoding on a 4-byte boundary
  c.nop
  c.ebreak                          # 2-byte encoding on a 2-byte boundary
  addi s0, s0, 1
  addi s1, s1, -1
  bne  s1, x0, loop
  li   t5, 30
  bne  s2, t5, fail                 # 30 breakpoints expected (3 per round)
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin
fail:
  la   t5, tohost
  li   t6, 3
  sw   t6, 0(t5)
  j    spin

handler:
  csrr t6, mcause                   # 3 on both encodings
  li   t5, 3
  bne  t6, t5, fail
  csrr t4, mtval                    # 0 (Ibex writes no address on a breakpoint; spec-legal)
  csrr t3, mepc                     # the trapping instruction's own pc
  lhu  t2, 0(t3)                    # its low half-word tells the encoding length
  andi t2, t2, 3
  li   t1, 3
  beq  t2, t1, four
  addi t3, t3, 2
  j    ret
four:
  addi t3, t3, 4
ret:
  addi s2, s2, 1
  csrw mepc, t3
  mret

.balign 256
gen_vec:
  .rept 32
  j    handler
  .endr

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
