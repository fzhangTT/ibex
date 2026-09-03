/* gen_link.ld: linker script for generated and directed programs on the generated TB.
 * Memory map = dv/auto_dv/tb/gen_tb_pkg.sv (program window at GEN_BOOT_ADDR_DEFAULT) and the
 * gen_dut_top debug parameters (DmHaltAddr 0x1A110800, DmExceptionAddr = DmHaltAddr + 8,
 * DM window DmBaseAddr 0x1A110000 .. +DmAddrMask 0xFFF). The core's first fetch is
 * {boot_addr_i[31:8], 8'h80}: the .gen_boot entry (gen_boot_stub.S, ELF entry point) is linked
 * there and jumps to _start; .text follows at its own (256-byte, vectored mtvec) alignment.
 * Section order after .text follows the riscv-dv generator's expectations (vendor
 * google_riscv-dv/scripts/link.ld). Link with -Wl,-N (omagic) so the ELF headers are not
 * mapped into the DM window as a PT_LOAD segment. Regenerate from the knobs YAML once the
 * codegen exists. */
OUTPUT_ARCH("riscv")
ENTRY(gen_boot_entry)

MEMORY
{
  DM   (rx)  : ORIGIN = 0x1A110800, LENGTH = 0x800
  PROG (rwx) : ORIGIN = 0x80000080, LENGTH = 0x000FFF80
}

SECTIONS
{
  /* Debug ROM: entry at DmHaltAddr, exception entry at DmHaltAddr + 8 (program-provided or the
     gen_debug_rom_stub.S default). */
  .debug_rom : { KEEP(*(.debug_rom)) } > DM

  .gen_boot : { KEEP(*(.gen_boot)) } > PROG
  .text : { *(.text) } > PROG
  . = ALIGN(0x1000);
  .tohost : { *(.tohost) } > PROG
  . = ALIGN(0x1000);
  .page_table : { *(.page_table) } > PROG
  .data : { *(.data) } > PROG
  .user_stack : { *(.user_stack) } > PROG
  .kernel_data : { *(.kernel_data) } > PROG
  .kernel_stack : { *(.kernel_stack) } > PROG
  .bss : { *(.bss) } > PROG
  _end = .;
}
