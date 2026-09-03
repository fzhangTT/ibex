# gen_zc_directed.S: self-checking directed program for the Zcb and Zcmp instructions, built with
# the gen_zc_insn.h macros (gcc 10.2 knows neither extension). Ends by storing 1 (pass) or 3
# (fail, exit code 1) to tohost, the same end-of-test convention riscv-dv programs use.
# Expected values come from the Zc* specification v1.0.0: cm.push stores the register list from
# the highest register down starting at sp-4 (so ra lands at the lowest address, sp_old -
# stack_adj_base) and decrements sp by stack_adj; cm.pop reverses it; cm.mvsa01 copies a0/a1 into
# two s registers; cm.mva01s copies two s registers into a0/a1. rtl/ibex_compressed_decoder.sv
# cm_push_store_reg stores cm_rlist_top_reg first at sp-4, matching this order.
.include "gen_zc_insn.h"

.section .text
.globl _start
_start:
  la   sp, gen_stack_top
  mv   t0, sp                       # remember the initial sp

  # ---- cm.push {ra, s0-s2}, -16 : rlist 7, spimm 0 (base 16) -----------------------------
  li   ra, 0x11111111
  li   s0, 0x22222222
  li   s1, 0x33333333
  li   s2, 0x44444444
  cm_push 7, 0
  sub  t1, t0, sp
  li   t2, 16
  bne  t1, t2, fail                 # sp decremented by 16
  lw   t3, 12(sp)
  bne  t3, s2, fail                 # top register s2 at old sp - 4
  lw   t3, 8(sp)
  bne  t3, s1, fail
  lw   t3, 4(sp)
  bne  t3, s0, fail
  lw   t3, 0(sp)
  bne  t3, ra, fail                 # ra at old sp - 16

  # ---- cm.pop {ra, s0-s2}, 16 restores what cm.push saved --------------------------------
  li   ra, 0
  li   s0, 0
  li   s1, 0
  li   s2, 0
  cm_pop 7, 0
  bne  sp, t0, fail
  li   t3, 0x11111111
  bne  ra, t3, fail
  li   t3, 0x22222222
  bne  s0, t3, fail
  li   t3, 0x33333333
  bne  s1, t3, fail
  li   t3, 0x44444444
  bne  s2, t3, fail

  # ---- cm.push with spimm = 1 (stack_adj 32 for rlist 5 = {ra, s0}) ----------------------
  cm_push 5, 1
  sub  t1, t0, sp
  li   t2, 32
  bne  t1, t2, fail
  lw   t3, 28(sp)                   # s0 at old sp - 4 = new sp + 28
  bne  t3, s0, fail
  lw   t3, 24(sp)                   # ra at old sp - 8
  bne  t3, ra, fail
  cm_pop 5, 1
  bne  sp, t0, fail

  # ---- cm.mvsa01 s0, s1 (a0 -> s0, a1 -> s1) and cm.mva01s s2, s3 (s2 -> a0, s3 -> a1) ---
  li   a0, 0xa0a0a0a0
  li   a1, 0xa1a1a1a1
  cm_mvsa01 8, 9
  li   t3, 0xa0a0a0a0
  bne  s0, t3, fail
  li   t3, 0xa1a1a1a1
  bne  s1, t3, fail
  li   s2, 0x52525252
  li   s3, 0x53535353
  li   a0, 0
  li   a1, 0
  cm_mva01s 18, 19
  li   t3, 0x52525252
  bne  a0, t3, fail
  li   t3, 0x53535353
  bne  a1, t3, fail

  # ---- Zcb byte/half stores and loads through x8..x15 registers ---------------------------
  la   s0, gen_scratch              # rs1' = x8
  li   s1, 0xffffff85               # rs2' = x9 : byte 0x85 (negative as signed byte)
  c_sb 9, 1, 8                      # sb s1, 1(s0)
  li   s1, 0x00001234
  c_sh 9, 2, 8                      # sh s1, 2(s0)
  c_lbu 10, 1, 8                    # a0 = lbu 1(s0) -> 0x85
  li   t3, 0x85
  bne  a0, t3, fail
  c_lhu 10, 2, 8                    # a0 = lhu 2(s0) -> 0x1234
  li   t3, 0x1234
  bne  a0, t3, fail
  li   s1, 0xffff8001
  c_sh 9, 0, 8                      # sh s1, 0(s0) -> 0x8001
  c_lh 10, 0, 8                     # a0 = lh 0(s0) -> sign-extended 0xffff8001
  li   t3, 0xffff8001
  bne  a0, t3, fail

  # ---- Zcb ALU ---------------------------------------------------------------------------
  li   a2, 0x12345678
  c_zext_b 12                       # a2 = 0x78
  li   t3, 0x78
  bne  a2, t3, fail
  li   a2, 0x12345680
  c_sext_b 12                       # a2 = 0xffffff80
  li   t3, 0xffffff80
  bne  a2, t3, fail
  li   a2, 0x1234abcd
  c_zext_h 12                       # a2 = 0xabcd
  li   t3, 0xabcd
  bne  a2, t3, fail
  li   a2, 0x1234abcd
  c_sext_h 12                       # a2 = 0xffffabcd
  li   t3, 0xffffabcd
  bne  a2, t3, fail
  li   a2, 0x0f0f0f0f
  c_not 12                          # a2 = 0xf0f0f0f0
  li   t3, 0xf0f0f0f0
  bne  a2, t3, fail
  li   a2, 7
  li   a3, -6
  c_mul 12, 13                      # a2 = a2 * a3 = -42
  li   t3, -42
  bne  a2, t3, fail

  # ---- cm.popret {ra}, 16 returns through ra -----------------------------------------------
  la   ra, popret_target
  cm_push 4, 0                      # {ra}, stack_adj 16
  li   ra, 0
  cm_popret 4, 0                    # pops ra, adds 16 to sp, jumps to ra
  j    fail                         # never reached
popret_target:
  bne  sp, t0, fail

  # ---- cm.popretz {ra}, 16: a0 = 0 then return ---------------------------------------------
  la   ra, popretz_target
  cm_push 4, 0
  li   a0, 0x5a5a5a5a
  cm_popretz 4, 0
  j    fail
popretz_target:
  bne  a0, zero, fail
  bne  sp, t0, fail

pass:
  li   gp, 1
  j    write_tohost
fail:
  li   gp, 3                        # exit code 1 on Spike (payload >> 1)
write_tohost:
  la   t5, tohost
  sw   gp, 0(t5)
1:
  j    1b

.section .data
.align 6
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.align 4
gen_scratch: .fill 16, 1, 0
.align 4
gen_stack:   .fill 256, 1, 0
gen_stack_top:
