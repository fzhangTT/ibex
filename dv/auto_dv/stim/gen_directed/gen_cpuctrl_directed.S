# gen_cpuctrl_directed.S: reads cpuctrlsts around a synchronous exception and a nested one (a double fault), so the read-back
# bins of gen_sec_ctrl_inputs_cg (bits 7:6 = double_fault_seen / sync_exc_seen, bit 8 = ic_scr_key_valid) are all reached;
# the double fault is deliberate, so the run disables the misc never-high rule of double_fault_seen; mstatus.MPP is set to M before each
# mret that follows a nested return (an mret leaves MPP at U). 1 to tohost at the end.
.section .text
.globl _start
_start:
  la   t0, handler
  csrw mtvec, t0
  li   t0, 0x1800
  csrs mstatus, t0
  li   s0, 0
  csrr a0, 0x7C0
  ecall
  csrr a1, 0x7C0
  li   t1, 0x80
  csrc 0x7C0, t1
  csrr a2, 0x7C0
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.balign 256
handler:
  csrr a3, 0x7C0
  bnez s0, nested
  csrr s1, mepc
  li   s0, 1
  ecall
  csrr a4, 0x7C0
  addi s1, s1, 4
  csrw mepc, s1
  li   t2, 0x1800
  csrs mstatus, t2
  mret
nested:
  csrr t2, mepc
  addi t2, t2, 4
  csrw mepc, t2
  mret

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
