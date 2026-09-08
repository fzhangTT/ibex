# gen_prv_debug_b2_directed.S: B2 reproducer (TP-PRV-035). All PMP regions stay OFF, so a data access checked as U-mode is
# denied by the no-match rule; the program sets mstatus.MPRV = 1 with MPP = U and parks. The debug ROM below then loads a word
# outside the debug-module window: the RTL checks that load with the MPP privilege although dcsr.mprven reads 0 and takes an
# exception inside debug mode, while the model ignores MPRV in debug mode and completes it, so the lock-step comparator
# diverges on the ROM's load record. The control is gen_prv_debug_b2_ctrl_directed.S (MPRV = 0).
# No load or store follows the MPRV write: with MPP = U every data access of the parked program would be denied too, so the
# program keeps to registers and never signals tohost (gen_ut_dbg ends through the bridge handshake, not the tohost store).
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  li   t1, 0x1800
  csrc mstatus, t1                  # MPP = U
  li   t2, 0x20000
  csrs mstatus, t2                  # MPRV = 1
  li   a0, 0
  li   a1, 0
gen_park:
  addi a0, a0, 1                    # a retiring park loop: no data access can follow the MPRV write
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

# The program's own debug ROM replaces gen_debug_rom_stub.S: entry at DmHaltAddr, exception entry at DmHaltAddr + 8.
.section .debug_rom, "ax", @progbits
.option norvc
.globl gen_debug_rom_entry
.globl gen_debug_exception_entry
gen_debug_rom_entry:
  j    gen_rom_body
  nop
gen_debug_exception_entry:
  dret                              # where the RTL lands: its MPRV-checked load was denied
gen_rom_body:
  la   t3, gen_b2_probe
  lw   t4, 0(t3)                    # RTL: checked as U and denied; model: MPRV ignored in debug mode, completes
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
