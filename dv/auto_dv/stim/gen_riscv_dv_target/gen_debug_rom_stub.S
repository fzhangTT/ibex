# gen_debug_rom_stub.S: default debug ROM for programs that define none. Linked at DmHaltAddr by
# gen_link.ld; the exception entry must sit at DmHaltAddr + 8, hence norvc and the padding nop.
# Both entries return immediately (dret), so a stray debug request is harmless to the program.
.option norvc
.section .debug_rom, "ax", @progbits
.globl gen_debug_rom_entry
.globl gen_debug_exception_entry
gen_debug_rom_entry:
  j 1f
  nop
gen_debug_exception_entry:
  dret
1:
  dret
