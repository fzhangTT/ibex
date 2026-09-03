# gen_dmem_err_directed.S: data-bus faults under an injected error rate. A buffer is written and read back with every
# access shape the LSU has (aligned and word-spanning 32-bit, half, byte, 16-bit c.sw/c.lw forms); the handler accepts
# only load/store access faults (5 / 7) and retries the faulting access by returning to it, so every injected error is one
# trap and the program still ends. Inside the handler one probe load may itself fault: a nested access fault before the
# mret (a double fault the DUT reports on double_fault_seen_o); the nested entry only retries the probe, and the outer
# handler restores MPP = M before its mret (a nested mret leaves MPP = U). 1 to tohost at the end, 3 on any other cause.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  la   a0, buf
  li   a1, 0x01020304
  li   s1, 100
  li   s2, 0                        # faults taken
  li   s4, 0                        # 1 while the handler's probe is in flight
loop:
  .option push
  .option norvc
  sw   a1, 0(a0)                    # aligned word
  lw   a2, 0(a0)
  sw   a1, 6(a0)                    # spans two words (bytes 6..9)
  lw   a2, 6(a0)
  sh   a1, 2(a0)
  lhu  a2, 2(a0)
  sb   a1, 1(a0)
  lbu  a2, 1(a0)
  .option pop
  c.sw a1, 12(a0)                   # 16-bit forms
  c.lw a2, 12(a0)
  addi a1, a1, 1
  addi s1, s1, -1
  bne  s1, x0, loop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin
fail:
  la   t5, tohost
  li   t6, 3
  sw   t6, 0(t5)
  j    spin

handler:
  csrr s5, mepc                     # read back into registers the lock-step model compares
  csrr s6, mtval
  csrr t6, mcause
  li   t5, 5
  beq  t6, t5, fault
  li   t5, 7
  bne  t6, t5, fail
fault:
  addi s2, s2, 1
  bne  s4, x0, ret                  # nested: the probe faulted, return to it
  csrr s3, mepc                     # keep the outer return address across the probe
  li   s4, 1
  lw   t4, 16(a0)                   # the probe (may fault -> nested trap)
  li   s4, 0
  csrw mepc, s3
  li   t5, 0x1800                   # the nested mret left MPP = U; return to M-mode
  csrs mstatus, t5
ret:
  mret

.balign 256
gen_vec:
  .rept 32
  j    handler
  .endr

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
buf:      .space 32
