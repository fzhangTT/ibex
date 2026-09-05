# Scratch fixture for the accrual red: mstatus.MIE alternates in short windows so that no run of
# records with the interrupt takeable is ever as long as the entry bound, while the total is longer.
# Every unmasked window is six records; the bound is seventeen.
.include "gen_mmio_map.h"
.option norvc
.section .text
.globl _start
_start:
  la   t0, handler
  csrw mtvec, t0                    # direct mode (bit 0 clear): every trap to one handler
  li   t0, -1
  csrw mie, t0                      # every line enabled, so any raised line is takeable when MIE is
  li   s0, 6                        # six windows of six: thirty-six takeable records against a bound of seventeen
loop:
  csrsi mstatus, 8                  # MIE set: this record and the five below are takeable
  nop
  nop
  nop
  nop
  nop
  csrci mstatus, 8                  # MIE clear: this record and the rest of the iteration are not
  nop
  nop
  nop
  nop
  nop
  addi s0, s0, -1
  bnez s0, loop
  la   t5, tohost                   # MIE is clear here and stays clear to the end of the run
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

handler:
  mret                              # an interrupt's mepc is the next instruction, so no adjustment

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
