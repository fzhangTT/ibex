# gen_prv_debug_b2_ctrl_directed.S: the passing control of B2 (gen_prv_debug_b2_directed.S). Identical except that
# mstatus.MPRV stays 0, so the debug ROM's load is checked with the core's own M privilege on both sides and the lock-step
# comparator sees no divergence: the control shows the checking mechanism can pass on this program shape and this debug ROM.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  li   t1, 0x1800
  csrc mstatus, t1                  # MPP = U
  li   t2, 0x20000
  csrc mstatus, t2                  # MPRV = 0: the bug's trigger removed
  li   a0, 0
  li   a1, 0
gen_park:
  addi a0, a0, 1
  addi a1, a1, 2
  j    gen_park

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
  la   t3, gen_b2_probe
  lw   t4, 0(t3)                    # M privilege on both sides: completes
  dret

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 4
.globl gen_b2_probe
gen_b2_probe: .word 0x5A5AA5A5
