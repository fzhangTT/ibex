# gen_pmc_wb_wait_ctrl_directed.S: the passing control of B17 (gen_pmc_wb_wait_directed.S). The same three pairs of
# windows on mhpmcounter8, 11 and 12, the same verdict word and the same end-of-test convention, with the bug's trigger
# removed by the workaround the bug log names: eight independent instructions separate the load from the event in the first
# window of every pair as well, so the response is back before the event decodes, every window meets the documented
# expectation, the verdict word stays 0 and the program stores the pass value 1. The control shows that this checking
# mechanism can pass, and that the deltas of the red run come from the outstanding access and not from the windows.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  csrw mcountinhibit, zero
  la   a3, gen_b17_buf
  li   a1, 1
  li   a2, 2                        # a1 != a2: every branch below falls through
  li   s3, 0                        # the verdict word
  li   a4, 1
  csrr t0, mhpmcounter8
  lw   a5, 0(a3)
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  beq  a1, a2, gen_b17_never
  nop
  csrr t1, mhpmcounter8
  sub  t2, t1, t0                   # documentation: 1; RTL counts one per waiting cycle
  beq  t2, a4, gen_b17_w1
  ori  s3, s3, 1
gen_b17_w1:
  csrr t3, mhpmcounter8
  lw   a5, 4(a3)
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  beq  a1, a2, gen_b17_never        # the response is back before this decodes
  nop
  csrr t4, mhpmcounter8
  sub  t5, t4, t3                   # documentation and RTL: 1
  beq  t5, a4, gen_b17_w2
  ori  s3, s3, 2
gen_b17_w2:
  csrr s0, mhpmcounter11
  lw   a5, 8(a3)
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  mul  a6, a1, a2
  csrr s1, mhpmcounter11
  sub  s2, s1, s0                   # documentation: 0, a one-cycle multiplier never stalls
  beqz s2, gen_b17_w3
  ori  s3, s3, 4
gen_b17_w3:
  csrr s4, mhpmcounter11
  lw   a5, 12(a3)
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  mul  a6, a1, a2
  csrr s5, mhpmcounter11
  sub  s6, s5, s4                   # documentation and RTL: 0
  beqz s6, gen_b17_w4
  ori  s3, s3, 8
gen_b17_w4:
  csrr s7, mhpmcounter12
  lw   a5, 16(a3)
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  div  a7, a2, a1
  csrr s8, mhpmcounter12
  sub  s9, s8, s7                   # the divider's own stall cycles plus the load's, in the RTL
gen_b17_w5:
  csrr s10, mhpmcounter12
  lw   a5, 20(a3)
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  div  a7, a2, a1                   # the same divide with the response already back
  csrr s11, mhpmcounter12
  sub  s11, s11, s10                # the divider's own stall cycles
  beq  s9, s11, gen_b17_report      # the same divide must stall the same, load or no load
  ori  s3, s3, 16
gen_b17_report:
  la   a0, gen_b17_delta
  sw   t2, 0(a0)
  sw   t5, 4(a0)
  sw   s2, 8(a0)
  sw   s6, 12(a0)
  sw   s9, 16(a0)
  sw   s11, 20(a0)
  sw   s3, 24(a0)
  li   a1, 1
  beqz s3, gen_b17_eot
  ori  a1, s3, 0x100
gen_b17_eot:
  la   t5, tohost
  sw   a1, 0(t5)
spin:
  j    spin
gen_b17_never:
  j    gen_b17_never                # no branch above is ever taken; reaching this is a program defect

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
.globl gen_b17_buf
gen_b17_buf: .word 0x11111111, 0x22222222, 0x33333333, 0x44444444, 0x55555555, 0x66666666
.balign 4
.globl gen_b17_delta
gen_b17_delta: .word 0, 0, 0, 0, 0, 0, 0
