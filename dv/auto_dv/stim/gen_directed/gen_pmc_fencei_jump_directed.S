# gen_pmc_fencei_jump_directed.S: B20 reproducer (TP-PMC-061). Three windows read mhpmcounter7 (NumJumps) around a fence.i,
# around two nops and around a call with its return, and the program compares each delta with the value
# doc/03_reference/performance_counters.rst defines for the event, unconditional jumps only. A violated expectation sets a
# bit of the verdict word, which the program stores to tohost as 0x100 plus the bits instead of the pass value 1, so the
# end-of-test code carries the finding and the cocotb module's own end-of-test assertion is the collected failure. The nop
# and call windows are the calibration: they show the counter is quiet without a jump and counts a real jump, so bit 0 alone
# means the fence.i was counted. The ISA shim mirrors the core's HPM values, so the lock-step comparator sees none of this;
# tb-infra's counter rule (ctr_hpm_exact, counter 7) is the independent witness when it lands, on this same program.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  csrw mcountinhibit, zero          # every implemented counter runs
  li   s3, 0                        # the verdict word
  csrr t0, mhpmcounter7
  fence.i
  csrr t1, mhpmcounter7
  sub  t2, t1, t0                   # documentation: 0; RTL counts the internal jump
  beqz t2, gen_b20_w1
  ori  s3, s3, 1
gen_b20_w1:
  csrr t3, mhpmcounter7
  nop
  nop
  csrr t4, mhpmcounter7
  sub  t5, t4, t3                   # documentation and RTL: 0, no jump in the window
  beqz t5, gen_b20_w2
  ori  s3, s3, 2
gen_b20_w2:
  csrr s0, mhpmcounter7
  jal  ra, gen_b20_leaf
  csrr s1, mhpmcounter7
  sub  s2, s1, s0                   # documentation and RTL: 2, the call and its return
  li   t6, 2
  beq  s2, t6, gen_b20_report
  ori  s3, s3, 4
gen_b20_report:
  la   a0, gen_b20_delta
  sw   t2, 0(a0)
  sw   t5, 4(a0)
  sw   s2, 8(a0)
  sw   s3, 12(a0)
  li   a1, 1                        # the pass value of the end-of-test convention
  beqz s3, gen_b20_eot
  ori  a1, s3, 0x100                # a documented expectation was violated: never the pass value
gen_b20_eot:
  la   t5, tohost
  sw   a1, 0(t5)
spin:
  j    spin

gen_b20_leaf:
  ret

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
.globl gen_b20_delta
gen_b20_delta: .word 0, 0, 0, 0
