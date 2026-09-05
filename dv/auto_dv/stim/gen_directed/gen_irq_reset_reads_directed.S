# gen_irq_reset_reads_directed.S: the four read-backs CG-IRQ-011 cp_reset_reads names, each read
# before any instruction writes it, then reported in order so the test can say which value it judged.
# mip is read with a line already at level, which is what makes the read discriminating: with every
# pin low a line-indexed and a bit-positioned comparison agree, and only an asserted line separates
# them. The test raises the line while fetch_enable is Off, so it is present at the very first record.
.include "gen_mmio_map.h"
.option norvc
.section .text
.globl _start
_start:
  csrr t0, mstatus                  # reset: MPIE set, MIE clear, MPP = U
  csrr t1, mie                      # reset: every line masked
  csrr t2, mtvec                    # reset: the boot page, mode vectored
  csrr t3, mip                      # reset: whatever the pins present at this cycle
  li   t4, GEN_MM_EOT_ADDR
  sw   t0, 0(t4)
  sw   t1, 0(t4)
  sw   t2, 0(t4)
  sw   t3, 0(t4)
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
