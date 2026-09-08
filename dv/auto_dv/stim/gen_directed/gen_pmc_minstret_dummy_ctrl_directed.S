# gen_pmc_minstret_dummy_ctrl_directed.S: the passing control of B7 (gen_pmc_minstret_dummy_directed.S). The instruction
# stream is the same and the cpuctrlsts write is still executed, but its value is 0, so no dummy instruction is inserted and
# the core's minstret reads equal the model's: the control shows the comparator can pass on this program shape.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  li   t0, 0
  csrs 0x7C0, t0                    # dummy_instr_en with mask 0 (red) / nothing (control)
  csrr t1, minstret
  .rept 64
  nop
  .endr
  csrr t2, minstret
  li   t3, 4
  csrc 0x7C0, t3                    # dummies off again before the end of the test
  sub  t4, t2, t1                   # the measured delta: 65 by the privileged specification
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
