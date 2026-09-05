# gen_irq_ack_directed.S: interrupt program for the UNTIL_ACK hold policy. Every implemented
# interrupt is enabled (mie all-ones: the DUT and the shim keep their implemented set), MIE is set,
# and a vectored mtvec table sends every cause to one handler that reports the cause it was entered
# for to GEN_MM_EOT_ADDR, acknowledges THAT cause at GEN_MM_IRQ_ACK_ADDR and returns with mret.
# The acknowledged cause is the entry's own mcause, so an ack names exactly one interrupt line: a
# second line raised at the same time survives the first entry's ack and is taken in its own entry.
# After the loop the program stores 1 to tohost, the riscv-dv end-of-test convention, then spins.
.include "gen_mmio_map.h"
.option norvc
.section .text
.globl _start
_start:
  li   s10, GEN_MM_IRQ_ACK_ADDR
  li   s11, GEN_MM_EOT_ADDR
  la   t0, gen_ack_vec
  ori  t0, t0, 1                    # MODE 1 (vectored) is the only mode Ibex has
  csrw mtvec, t0
  li   t0, -1
  csrw mie, t0                      # WARL: the implemented bits stay set
  csrsi mstatus, 8                  # MIE
  li   x6, 4000
loop:
  addi x5, x5, 1
  bne  x5, x6, loop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

gen_ack_common:
  csrr a3, mcause
  slli a3, a3, 1                    # the interrupt bit is dropped: a3 is the lower cause alone
  srli a3, a3, 1
  sw   a3, 0(s11)                   # report which cause this entry was taken for
  sw   a3, 0(s10)                   # acknowledge that cause, and only that cause
  mret

.balign 256
gen_ack_vec:
  .rept 32
  j gen_ack_common
  .endr

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
