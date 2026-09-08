# gen_pmc_dummy_wait_directed.S: B7's wait-counter half (TP-PMC-013, TP-DIT-019). Four windows read mhpmcounter12
# (NumCyclesDivWait) and mhpmcounter11 (NumCyclesMulWait) around the same eight divides and the same eight multiplies,
# once with cpuctrlsts.dummy_instr_en clear and once with it set; each cpuctrlsts write sits outside both windows of its
# pair, so the interval a counter rule judges holds nothing but the program's own arithmetic. The documented intent is
# that a dummy instruction has no functional impact on processor state (doc/03_reference/security.rst), so each pair's
# two windows must agree: the wait counters must count nothing beyond the program's own multiply and divide stall
# cycles. The fetch stage inserts dummy MUL and DIV instructions among its four types (rtl/ibex_dummy_instr.sv), so a
# dummy divide's stall cycles are what the disputed window can gain. A violated expectation sets a bit of the verdict
# word, which the program stores to tohost as 0x100 plus the bits instead of the pass value 1, so the cocotb module's
# own end-of-test assertion is the collected failure; tb-infra's counter rule with +gen_ctr_rtl_wait_cycles=0 is the
# independent witness. Deltas land at gen_b7w_delta as divide off, divide on, multiply off, multiply on, verdict.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  csrw mcountinhibit, zero
  li   a1, 1
  li   a2, 0x7A5A5A5A               # the same operands in every window: no data hazard between the ops
  li   s3, 0                        # the verdict word
  li   t3, 4                        # cpuctrlsts.dummy_instr_en with mask 0
  csrr t0, mhpmcounter12
  .rept 8
  div  a5, a2, a1
  .endr
  csrr t1, mhpmcounter12
  sub  t2, t1, t0                   # the program's own divide stall cycles
  csrs 0x7C0, t3                    # dummies on, outside both windows of the pair
  csrr t4, mhpmcounter12
  .rept 8
  div  a5, a2, a1
  .endr
  csrr t5, mhpmcounter12
  sub  t6, t5, t4                   # documented: the same as the window above
  csrc 0x7C0, t3
  beq  t6, t2, gen_b7w_mul
  ori  s3, s3, 1
gen_b7w_mul:
  csrr s0, mhpmcounter11
  .rept 8
  mul  a6, a2, a1
  .endr
  csrr s1, mhpmcounter11
  sub  s2, s1, s0                   # a one-cycle multiplier never stalls: 0
  csrs 0x7C0, t3
  csrr s4, mhpmcounter11
  .rept 8
  mul  a6, a2, a1
  .endr
  csrr s5, mhpmcounter11
  sub  s6, s5, s4                   # documented: the same as the window above
  csrc 0x7C0, t3
  beq  s6, s2, gen_b7w_report
  ori  s3, s3, 2
gen_b7w_report:
  la   a0, gen_b7w_delta
  sw   t2, 0(a0)
  sw   t6, 4(a0)
  sw   s2, 8(a0)
  sw   s6, 12(a0)
  sw   s3, 16(a0)
  li   a3, 1
  beqz s3, gen_b7w_eot
  ori  a3, s3, 0x100
gen_b7w_eot:
  la   t5, tohost
  sw   a3, 0(t5)
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
.balign 4
.globl gen_b7w_delta
gen_b7w_delta: .word 0, 0, 0, 0, 0
