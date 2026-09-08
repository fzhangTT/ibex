# gen_pmc_dit_branch_directed.S: B11 reproducer (TP-PMC-043, TP-BTALU-016). Two windows read mhpmcounter9
# (NumBranchesTaken) around the same sixteen never-taken branches, the first with cpuctrlsts.data_ind_timing set and the
# second with it clear, and the program compares each delta with the value doc/03_reference/performance_counters.rst
# defines for the event, taken branches, which is zero for sixteen branches that all fall through. A violated expectation
# sets a bit of the verdict word, which the program stores to tohost as 0x100 plus the bits instead of the pass value 1, so
# the cocotb module's own end-of-test assertion is the collected failure. The second window is the calibration: the same
# branches with the mode off must move the counter by nothing, so bit 0 alone means the mode is what created the counts.
# The ISA shim mirrors the core's HPM values, so the lock-step comparator sees none of this; tb-infra's counter rule
# (ctr_hpm_exact, counter 9) is the independent witness when it lands, on this same program.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  csrw mcountinhibit, zero
  li   a1, 1
  li   a2, 2                        # a1 != a2: every branch below falls through
  li   s3, 0                        # the verdict word
  li   t0, 2                        # cpuctrlsts.data_ind_timing
  csrs 0x7C0, t0
  csrr t1, mhpmcounter9
  .rept 16
  beq  a1, a2, gen_b11_never
  .endr
  csrr t2, mhpmcounter9
  sub  t3, t2, t1                   # documentation: 0; RTL counts all sixteen under the mode
  beqz t3, gen_b11_w1
  ori  s3, s3, 1
gen_b11_w1:
  csrc 0x7C0, t0                    # the mode off: the calibration window
  csrr t4, mhpmcounter9
  .rept 16
  beq  a1, a2, gen_b11_never
  .endr
  csrr t5, mhpmcounter9
  sub  t6, t5, t4                   # documentation and RTL: 0
  beqz t6, gen_b11_report
  ori  s3, s3, 2
gen_b11_report:
  la   a0, gen_b11_delta
  sw   t3, 0(a0)
  sw   t6, 4(a0)
  sw   s3, 8(a0)
  li   a3, 1
  beqz s3, gen_b11_eot
  ori  a3, s3, 0x100
gen_b11_eot:
  la   t5, tohost
  sw   a3, 0(t5)
spin:
  j    spin
gen_b11_never:
  j    gen_b11_never                # no branch above is ever taken; reaching this is a program defect

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
.globl gen_b11_delta
gen_b11_delta: .word 0, 0, 0
