# gen_pmc_fencei_jump_ctrl_directed.S: the passing control of B20 (gen_pmc_fencei_jump_directed.S). The same three windows
# on mhpmcounter7 and the same verdict word and end-of-test convention, with the bug's trigger removed: the first window's
# fence.i is a nop, so the documented expectation of no jump count is met, the verdict word stays 0 and the program stores
# the pass value 1. The control shows that this checking mechanism, the program's own comparison against the documentation
# reported through the end-of-test code, can pass.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  csrw mcountinhibit, zero          # every implemented counter runs
  li   s3, 0                        # the verdict word
  csrr t0, mhpmcounter7
  nop                               # the fence.i removed: no jump of any kind in this window
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
