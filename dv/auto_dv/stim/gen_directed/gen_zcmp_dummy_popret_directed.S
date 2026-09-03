# gen_zcmp_dummy_popret_directed.S: cm.push in the caller and cm.popret / cm.popretz in called functions with cpuctrlsts.dummy_instr_en
# set: the B8 case in which a dummy displaces the ret (CmPopRetRa) or the li a0, 0 (CmPopZeroA0) after sp has already moved, so the
# replayed loads read above the frame (gen_b8_rtl_facts.md section 3). Kept apart from gen_zcmp_dummy_directed.S (plain push / pop).
# The lock-step comparator flags the corrupted registers and the return; the run is the retained reproduction. 1 to tohost at the end.
.macro cm_insn kind, rlist, spimm
  .2byte 0xB002 | (\kind << 8) | (\rlist << 4) | (\spimm << 2)
.endm
.set PUSH, 0x18
.set POPRETZ, 0x1C
.set POPRET, 0x1E
.section .text
.globl _start
_start:
  la   sp, stack_top
  li   s0, 0x11111111
  li   s1, 0x22222222
  li   s2, 0x33333333
  li   s3, 0x44444444
  li   s4, 0x55555555
  li   s5, 0x66666666
  li   s6, 0x77777777
  li   s7, 0x88888888
  li   s8, 0x99999999
  li   s9, 0xAAAAAAAA
  li   s10, 0xBBBBBBBB
  li   s11, 0xCCCCCCCC
  li   t0, 4
  csrs 0x7C0, t0
  .irp n, 1, 2, 3, 4, 5, 6
  jal  ra, f_popret_\n
  jal  ra, f_popretz_\n
  .endr
  csrc 0x7C0, t0
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin
# called functions: push the register list on entry, return with cm.popret (rlist 4..15) or cm.popretz (a0 zeroed then ret)
.macro fn name, kind, rlist
\name:
  cm_insn PUSH, \rlist, 1
  addi s0, s0, 1
  addi s2, s2, 1
  cm_insn \kind, \rlist, 1
.endm
  fn f_popret_1, POPRET, 4
  fn f_popret_2, POPRET, 7
  fn f_popret_3, POPRET, 9
  fn f_popret_4, POPRET, 12
  fn f_popret_5, POPRET, 14
  fn f_popret_6, POPRET, 15
  fn f_popretz_1, POPRETZ, 4
  fn f_popretz_2, POPRETZ, 7
  fn f_popretz_3, POPRETZ, 9
  fn f_popretz_4, POPRETZ, 12
  fn f_popretz_5, POPRETZ, 14
  fn f_popretz_6, POPRETZ, 15

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 16
stack:    .space 512
stack_top:
