# Fixture for the per-line enable red: a line is raised while its OWN mie bit is clear, so the design is right
# to withhold it, and the bit is set later. A checker that counts those records as takeable spends the bound
# during the window and drops the expectation before the enable arrives; one that masks on the per-line bit
# keeps it and judges it afterwards.
# The vector table is explicit because mtvec writes keep only bits [31:8] and the mode is forced vectored
# (rtl/ibex_cs_registers.sv:742-743), so a handler address cannot be chosen directly.
.include "gen_mmio_map.h"
.option norvc
.section .text
.globl _start
_start:
  csrw mie, zero                    # every line DISABLED: a raised line is not takeable however MIE reads
  csrsi mstatus, 8                  # global enable ON, so only the per-line bit withholds
  la   t0, vtable
  csrw mtvec, t0                    # base is 256-byte aligned below; the low byte is forced to vectored
  li   s0, 14
p1:
  addi s0, s0, -1                   # phase 1: about 42 records with the line raised and its own bit clear
  nop
  bnez s0, p1
  li   t0, -1
  csrw mie, t0                      # phase 2: every line ENABLED, so the expectation becomes takeable
  li   s0, 14
p2:
  addi s0, s0, -1                   # phase 2: about 42 more records, the line withheld by the mutation
  nop
  bnez s0, p2
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
done:
  j    done

.balign 256
vtable:                             # 32 slots of one jump each, base + 4 * cause
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
  j handler
handler:
  csrw mie, zero                    # a clean run that DOES take the line disables it and returns, so the
  mret                              # control ends without a storm of re-entries

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
