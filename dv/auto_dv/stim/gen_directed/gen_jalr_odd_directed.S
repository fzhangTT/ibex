# gen_jalr_odd_directed.S: jalr whose rs1 + imm has bit 0 set (register-odd, immediate-odd, and both), 20 iterations,
# then 1 to tohost. The core fetches the even address (JALR clears bit 0, unpriv spec); rvfi_pc_wdata carries the raw
# sum (bug candidate B13, rtl-arch R11), so the comparator's pc_next rule on jalr records must mask bit 0 and count it.
# Any trap writes 3 to tohost and spins, so a miscompare of the trap path ends the run with a failing code.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  li   s0, 0
  li   s1, 20
loop:
  la   t1, tgt_reg_odd
  addi t1, t1, 1                    # rs1 odd, imm 0
  jalr x0, 0(t1)
  .balign 4
tgt_reg_odd:
  addi s0, s0, 1
  la   t2, tgt_imm_odd
  jalr x0, 1(t2)                    # rs1 even, imm odd
  .balign 4
tgt_imm_odd:
  addi s0, s0, 1
  la   t3, tgt_both_odd
  addi t3, t3, 3                    # rs1 + imm = target + 1
  jalr x1, -2(t3)
  .balign 4
tgt_both_odd:
  addi s0, s0, 1
  la   t4, tgt_c_jr
  addi t4, t4, 1
  c.jr t4                           # c.jr decompresses to jalr
  .balign 4
tgt_c_jr:
  addi s1, s1, -1
  bne  s1, x0, loop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

trap_fail:
  la   t5, tohost
  li   t6, 3
  sw   t6, 0(t5)
  j    spin

.balign 256
gen_vec:
  .rept 32
  j    trap_fail
  .endr

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
