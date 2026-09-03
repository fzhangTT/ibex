# gen_pmp_deny_directed.S: a locked PMP entry without R/W/X over a 32-byte data buffer (NAPOT), then a load and a store
# into it from M-mode: each traps (load / store access fault, causes 5 / 7), the handler steps mepc past the 4-byte
# access and returns; the model's own PMP must deny the same accesses (T-137 conditioned arming: no bus error is
# announced, the model decides). Ten rounds, then 1 to tohost. Any other trap ends with 3 in tohost.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  la   t1, denied
  srli t1, t1, 2                    # pmpaddr encodes address >> 2
  ori  t1, t1, 0x3                  # NAPOT 32 bytes: low bits 011
  csrw pmpaddr0, t1
  li   t2, 0x98                     # pmpcfg0 entry 0: L = 1, A = NAPOT (11), R/W/X = 0
  csrw pmpcfg0, t2
  li   s0, 0
  li   s1, 10
  li   s2, 0
loop:
  la   t3, denied
  lw   t4, 0(t3)                    # load access fault expected
  sw   t4, 4(t3)                    # store access fault expected
  addi s0, s0, 1
  addi s1, s1, -1
  bne  s1, x0, loop
  li   t5, 20
  bne  s2, t5, fail                 # 20 traps expected (2 per round)
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
  csrr t6, mcause
  li   t5, 5
  beq  t6, t5, skip
  li   t5, 7
  bne  t6, t5, fail
skip:
  addi s2, s2, 1
  csrr t5, mepc
  addi t5, t5, 4
  csrw mepc, t5
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
.balign 32
denied:   .fill 32, 1, 0
