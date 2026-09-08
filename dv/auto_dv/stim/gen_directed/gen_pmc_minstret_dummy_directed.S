# gen_pmc_minstret_dummy_directed.S: B7 reproducer (TP-PMC-013, TP-DIT-019). cpuctrlsts.dummy_instr_en is set with mask 0
# (the highest insertion rate), then minstret is read around a block of 64 nops. The RTL counts every inserted dummy
# instruction in minstret while RVFI emits no record for one, so the core's second read exceeds the model's, which serves
# minstret from its own retirement count; the lock-step comparator raises isa_rd on that read. The control is
# gen_pmc_minstret_dummy_ctrl_directed.S: the same instruction stream with the enable value 0.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  li   t0, 4
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
