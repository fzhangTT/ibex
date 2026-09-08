# gen_trg_ebreak_cause_ctrl_directed.S: the passing control of B10. The trigger CSRs are writable in debug mode only, so the
# program parks until a debug request arrives and its own debug ROM does the arming. The ROM counts its entries in memory:
# on the first it arms an execute-address trigger on A (the only writable tdata1 bit is execute), sets dcsr.ebreakm and
# points dpc at a sequence whose ebreak sits at A - 4; on every later entry it reads dcsr and dpc, stores both, and resumes
# past an ebreak, disarms on a trigger, or resumes where it was on a halt request. The core evaluates the trigger on the
# fetch-stage PC, which already holds A while the ebreak is in decode, so it records dcsr.cause = 2 (trigger) where the
# debug specification says 1 (ebreak); dpc is the ebreak's own address either way. The ROM's dcsr read is what carries the
# value into the lock-step comparison. The control is gen_trg_ebreak_cause_ctrl_directed.S (no trigger armed).
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  li   a0, 0
gen_park:
  addi a0, a0, 1                    # a retiring park loop; the first debug request arrives here
  j    gen_park

.option push
.option norvc
.balign 64
.globl gen_b10_seq
gen_b10_seq:
  ebreak                            # at A - 4: enters debug mode through dcsr.ebreakm
.globl gen_b10_target
gen_b10_target:
  addi a1, a1, 1                    # A: the address armed in tdata2
gen_b10_tail:
  addi a1, a1, 1
  j    gen_b10_tail                 # a retiring loop for the rest of the module's window
.option pop

.option push
.option norvc
.balign 256
gen_vec:
  .rept 32
  mret
  .endr
.option pop

.section .debug_rom, "ax", @progbits
.option norvc
.globl gen_debug_rom_entry
.globl gen_debug_exception_entry
gen_debug_rom_entry:
  j    gen_rom_body
  nop
gen_debug_exception_entry:
  dret
gen_rom_body:
  la   t0, gen_b10_count
  lw   t1, 0(t0)
  addi t1, t1, 1
  sw   t1, 0(t0)
  li   t2, 1
  beq  t1, t2, gen_rom_arm
  csrr t3, 0x7b0                    # dcsr: cause in bits 8:6
  csrr t4, 0x7b1                    # dpc
  la   t5, gen_b10_log
  slli t6, t1, 3
  add  t5, t5, t6
  sw   t3, 0(t5)
  sw   t4, 4(t5)
  srli t6, t3, 6
  andi t6, t6, 7
  li   t2, 2
  beq  t6, t2, gen_rom_trigger
  li   t2, 1
  beq  t6, t2, gen_rom_step_over
  dret                              # a halt request resumes where the core was
gen_rom_step_over:
  addi t4, t4, 4                    # an ebreak entry resumes at the instruction after it
  csrw 0x7b1, t4
  dret
gen_rom_trigger:
  csrw tdata1, zero                 # disarm and resume at dpc: correct for a genuine trigger entry, whose dpc is the
                                    # matched address, and the path B10's wrong cause sends an ebreak entry down, where
                                    # dpc still holds the ebreak and it re-executes (gen_rvfi_order_debug_entry_rtl_facts.md)
  dret
gen_rom_arm:
  csrw tselect, zero
  li   t3, 0                        # no trigger armed: the bug's trigger removed
  csrw tdata1, t3
  la   t3, gen_b10_target
  csrw tdata2, t3
  li   t3, 0x8000
  csrs 0x7b0, t3                    # dcsr.ebreakm = 1
  la   t3, gen_b10_seq
  csrw 0x7b1, t3                    # dpc = the ebreak sequence
  dret

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 4
.globl gen_b10_count
gen_b10_count: .word 0
.balign 8
.globl gen_b10_log
gen_b10_log: .space 64
