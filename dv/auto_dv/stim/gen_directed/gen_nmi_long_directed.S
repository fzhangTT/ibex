# gen_nmi_long_directed.S: the interrupt-taking program of gen_irq_directed.S with a LONG NMI handler (40 nops before its mret),
# so an interrupt expectation can outlive GEN_IRQ_ENTRY_BOUND_RECORDS inside NMI mode. Every other vector is one mret. The irq
# checker must neither judge nor forget a line while NMI mode masks every interrupt, and must judge it after the handler's mret
# (the irq checker's NMI-mode rule); the TB mutant that withholds a line from the NMI on is the red. 1 to tohost at the end, then spin.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1                    # MODE 1 (vectored) is the only mode Ibex has
  csrw mtvec, t0
  li   t0, -1
  csrw mie, t0                      # WARL: the implemented bits stay set
  csrsi mstatus, 8                  # MIE
  li   x6, 1500
loop:
  addi x5, x5, 1
  bne  x5, x6, loop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.option push
.option norvc
.balign 256
gen_vec:
  .rept 31
  mret
  .endr
  j    gen_nmi_handler              # entry 31 = mtvec base + 0x7C, the NMI vector (rtl/ibex_pkg.sv ExcCauseIrqNm)
gen_nmi_handler:
  .rept 40
  nop
  .endr
  mret
.option pop

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
