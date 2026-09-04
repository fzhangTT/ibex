# gen_icache_ecc_directed.S: enables the instruction cache once (cpuctrlsts.icache_enable) and then loops over a body spread across
# several cache lines with taken branches, so the cache is looked up, filled and hit for the rest of the run while the tag RAM
# models inject ECC errors (+gen_knob_icache_ecc_err_rate). The run exists for the alert_minor_o window: every qualified
# injection owes one alert_minor_o pulse within GEN_ICACHE_ECC_WINDOW of its lookup (gen_misc_monitor) and the protocol SVA
# sva_alert_minor_window must accept the observed latency. 1 to tohost at the end, then spin.
.section .text
.globl _start
_start:
  csrsi 0x7c0, 1                    # cpuctrlsts.icache_enable
  li   x6, 400
loop:
  addi x5, x5, 1
  jal  x1, far_a
  jal  x1, far_b
  bne  x5, x6, loop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.balign 64
far_a:
  addi x7, x7, 1
  .rept 12
  nop
  .endr
  jalr x0, 0(x1)

.balign 64
far_b:
  addi x8, x8, 1
  .rept 20
  nop
  .endr
  jalr x0, 0(x1)

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
