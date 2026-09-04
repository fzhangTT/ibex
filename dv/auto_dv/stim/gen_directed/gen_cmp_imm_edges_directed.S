# gen_cmp_imm_edges_directed.S: the immediate extremes of gen_cmp_imm_edges_cg (CG-CMP-002): c.addi4spn, c.lw / c.sw,
# c.lwsp / c.swsp, c.addi / c.li / c.andi, c.lui, c.addi16sp (with the stack pointer crossing zero both ways), the three
# compressed shifts, c.j to +2046 and -2048, c.beqz / c.bnez to +254 and -256 and to themselves (not taken), c.jal and c.jalr
# for the link. The lock-step model checks every result. 1 to tohost at the end; the spin after it retires as a c.j to itself.
.macro j32 label
.option push
.option norvc
  j \label
.option pop
.endm
.section .text
.globl _start
_start:
  la    sp, gen_ie_stack
  la    a1, gen_ie_buf
  # c.addi4spn: 4, 1020, other
  c.addi4spn a0, sp, 4
  c.addi4spn a0, sp, 1020
  c.addi4spn a0, sp, 8
  # c.lw / c.sw: 0, 124, other
  c.lw  a0, 0(a1)
  c.lw  a0, 124(a1)
  c.lw  a0, 8(a1)
  c.sw  a0, 0(a1)
  c.sw  a0, 124(a1)
  c.sw  a0, 12(a1)
  # c.lwsp / c.swsp: 0, 252, other
  c.lwsp a0, 0(sp)
  c.lwsp a0, 252(sp)
  c.lwsp a0, 16(sp)
  c.swsp a0, 0(sp)
  c.swsp a0, 252(sp)
  c.swsp a0, 20(sp)
  # c.addi: -32, -1, 1, 31, other (0 is the HINT)
  c.addi a0, -32
  c.addi a0, -1
  c.addi a0, 1
  c.addi a0, 31
  c.addi a0, 7
  # c.li: -32, -1, 0, 1, 31, other
  c.li  a0, -32
  c.li  a0, -1
  c.li  a0, 0
  c.li  a0, 1
  c.li  a0, 31
  c.li  a0, 9
  # c.andi: -32, -1, 0, 1, 31, other
  c.andi a0, -32
  c.andi a0, -1
  c.andi a0, 0
  c.andi a0, 1
  c.andi a0, 31
  c.andi a0, 5
  # c.lui a0 with nzimm[17:12] = 1, 31, -32, -1, 5 (explicit encodings)
  .2byte 0x6505
  .2byte 0x657d
  .2byte 0x7501
  .2byte 0x757d
  .2byte 0x6515
  # c.addi16sp: -512, 496, 16, -16, other, then each immediate class with the stack pointer crossing zero (borrow and carry)
  c.addi16sp sp, -512
  c.addi16sp sp, 496
  c.addi16sp sp, 16
  c.addi16sp sp, -16
  c.addi16sp sp, 32
  li    sp, 0x100
  c.addi16sp sp, -512
  li    sp, -16
  c.addi16sp sp, 496
  li    sp, -16
  c.addi16sp sp, 16
  li    sp, 8
  c.addi16sp sp, -16
  li    sp, 0x10
  c.addi16sp sp, -32
  li    sp, -16
  c.addi4spn a0, sp, 32
  la    sp, gen_ie_stack
  # shifts: 1, 31, other
  c.srli a0, 1
  c.srli a0, 31
  c.srli a0, 5
  c.srai a0, 1
  c.srai a0, 31
  c.srai a0, 5
  c.slli a0, 1
  c.slli a0, 31
  c.slli a0, 5
  # branches to themselves, not taken
  li    a0, 0
  li    a1, 1
cb_self1:
  c.beqz a1, cb_self1
cb_self2:
  c.bnez a0, cb_self2
  # c.beqz +254 (taken)
  c.beqz a0, cb_fwd_t
  .fill 126, 2, 0x0001
cb_fwd_t:
  # c.bnez -256 (taken)
  j32   cb_bwd_site
cb_bwd_t:
  j32   cb_bwd_exit
  .fill 126, 2, 0x0001
cb_bwd_site:
  c.bnez a1, cb_bwd_t
cb_bwd_exit:
  # small positive and negative offsets
  c.beqz a0, cb_p
  c.nop
cb_p:
  j32   cb_n_site
cb_n_t:
  j32   cb_n_exit
  c.nop
cb_n_site:
  c.bnez a1, cb_n_t
cb_n_exit:
  # c.j +2046 and -2048, then small offsets both ways, c.jal and c.jalr for the link
  c.j   cj_fwd_t
  .fill 1022, 2, 0x0001
cj_fwd_t:
  j32   cj_bwd_site
cj_bwd_t:
  j32   cj_bwd_exit
  .fill 1022, 2, 0x0001
cj_bwd_site:
  c.j   cj_bwd_t
cj_bwd_exit:
  c.j   cj_p
  c.nop
cj_p:
  j32   cj_n_site
cj_n_t:
  j32   cj_n_exit
  c.nop
cj_n_site:
  c.j   cj_n_t
cj_n_exit:
  c.jal cjal_t
cjal_t:
  la    t0, cjalr_t
  c.jalr t0
cjalr_t:
  la    t5, tohost
  li    t6, 1
  sw    t6, 0(t5)
spin:
  j     spin

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 16
gen_ie_buf:   .space 128, 0x5a
.balign 16
gen_ie_stack: .space 512, 0
