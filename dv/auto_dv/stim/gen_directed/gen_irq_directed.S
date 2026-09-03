# gen_irq_directed.S: interrupt-taking program for the irq agent tests (build step 2b). Enables every
# implemented interrupt (mie written all-ones: the DUT and the shim keep their implemented set, so no
# mask is re-typed here), sets MIE, points the vectored mtvec at a 32-entry table whose every handler
# is one mret, then counts 1500 loop iterations (about 3000 retirements) and stores 1 to tohost, the riscv-dv
# end-of-test convention, then spins. The TB raises lines through the bridge; each entry returns to the loop.
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

.balign 256
gen_vec:
  .rept 32
  mret
  .endr

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
