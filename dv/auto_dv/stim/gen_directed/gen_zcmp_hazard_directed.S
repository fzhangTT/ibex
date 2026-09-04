# gen_zcmp_hazard_directed.S: the neighbour patterns of gen_cmp_zcmp_hazard_cg (CG-CMP-009): a register written or loaded right before
# the cm.push that saves it, a store into a slot the following cm.pop loads, push / pop back to back both ways, a load feeding cm.mva01s
# and the two move forms back to back, calls whose cm.popret / cm.popretz return to the next record with every cm.* kind as the
# fall-through halfword (dead code after the ret), rlist 4, 5..14 and 15. The dbus regime of the run gives the ra-load deferral and the
# micro-op stall classes. The lock-step model checks every micro-op. 1 to tohost at the end.
.macro cm_insn kind, rlist, spimm
  .2byte 0xB002 | (\kind << 8) | (\rlist << 4) | (\spimm << 2)
.endm
.macro cm_mva01s r1, r2
  .2byte 0xAC62 | (\r1 << 7) | (\r2 << 2)
.endm
.macro cm_mvsa01 r1, r2
  .2byte 0xAC22 | (\r1 << 7) | (\r2 << 2)
.endm
.set PUSH, 0x18
.set POP, 0x1A
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
  li   ra, 0xDDDDDDD0
  la   t1, data_word
  # an ALU write to s0 right before the push that saves it; then push / pop back to back both ways
  addi s0, s0, 1
  cm_insn PUSH, 5, 0
  cm_insn POP, 5, 0
  cm_insn PUSH, 6, 0
  # a store into the s1 slot of that push (adj 16: ra at sp+12, s0 at sp+8, s1 at sp+4), then the pop that loads it
  li   t0, 0x12345678
  sw   t0, 4(sp)
  cm_insn POP, 6, 0
  # a load into s1 right before the push that saves it
  lw   s1, 0(t1)
  cm_insn PUSH, 6, 1
  cm_insn POP, 6, 1
  # the full register list back to back
  cm_insn PUSH, 15, 0
  cm_insn POP, 15, 0
  # the moves: a load into r1s' then cm.mva01s; cm.mvsa01 then cm.mva01s on the same pair
  lw   s2, 0(t1)
  cm_mva01s 2, 3
  cm_mvsa01 4, 5
  cm_mva01s 4, 5
  # calls returning through cm.popret / cm.popretz with every cm.* kind as the fall-through halfword
  jal  ra, fn_a
  jal  ra, fn_b
  jal  ra, fn_c
  jal  ra, fn_d
  jal  ra, fn_e
  jal  ra, fn_f
  jal  ra, fn_g
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

fn_a:
  cm_insn PUSH, 4, 0
  cm_insn POPRET, 4, 0
fn_b:                          # fn_a's fall-through halfword: this cm.push
  cm_insn PUSH, 5, 0
  addi s0, s0, 2
  cm_insn POPRETZ, 5, 0
  cm_insn POP, 4, 0            # dead: the popretz's fall-through halfword
fn_c:
  cm_insn PUSH, 4, 0
  cm_insn POPRET, 4, 0
  cm_insn POPRET, 4, 0         # dead
fn_d:
  cm_insn PUSH, 4, 0
  cm_insn POPRETZ, 4, 0
  cm_insn POPRETZ, 4, 0        # dead
fn_e:
  cm_insn PUSH, 4, 0
  cm_insn POPRET, 4, 0
  cm_mvsa01 4, 5               # dead
fn_f:
  cm_insn PUSH, 4, 0
  cm_insn POPRETZ, 4, 0
  cm_mva01s 4, 5               # dead
fn_g:
  cm_insn PUSH, 4, 0
  cm_insn POPRET, 4, 0
  nop                          # a plain fall-through: no ft pattern

.section .data
.balign 16
stack:    .space 512
stack_top:
data_word: .word 0x5A5A5A5A
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
