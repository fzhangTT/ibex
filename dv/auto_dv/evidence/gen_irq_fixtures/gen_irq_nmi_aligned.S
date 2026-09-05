# NMI-mode exit red, rebuilt at an ALIGNED vector base. The earlier version put its handler at 0x800000c0
# and never ran: a csrw of mtvec keeps only bits [31:8] and forces vectored mode
# (rtl/ibex_cs_registers.sv:742-743), so an unaligned base is discarded and every trap vectors elsewhere.
# Here the table is 256-byte aligned, the NMI takes slot 31 and a synchronous exception takes slot 0.
# The NMI handler deliberately takes a nested ecall: the design leaves NMI mode at that INNER mret
# (rtl/ibex_controller.sv:954-960, no nesting count) while the handler still has records to run, so a line
# raised in that window is takeable by the design and a checker counting nesting depth still masks it.
.include "gen_mmio_map.h"
.option norvc
.section .text
.globl _start
_start:
  la   t0, vtable
  csrw mtvec, t0                    # 256-byte aligned, so the base survives the write
  li   t0, -1
  csrw mie, t0                      # every line enabled
  csrsi mstatus, 8                  # M0 = 1: the outer mret will restore MIE to 1
  li   s0, 200
pre:
  addi s0, s0, -1                   # room for the test to raise the NMI at retired 200
  nop
  bnez s0, pre
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
done:
  j    done

.balign 256
vtable:
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j exc_handler
  j nmi_handler

exc_handler:
  csrr t2, mepc                     # step over the faulting instruction and return
  addi t2, t2, 4
  csrw mepc, t2
  mret                              # THIS is the mret that leaves NMI mode in the design

nmi_handler:
  ecall                             # nested exception, two records in
  csrsi mstatus, 8                  # the ecall's mret restored MIE from a cleared MPIE, so set it again
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  mret

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
