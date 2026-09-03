# gen_boot_stub.S: the word the core fetches first. Ibex starts at {boot_addr_i[31:8], 8'h80};
# gen_link.ld places this section there and makes it the ELF entry, so the TB image and the ISA
# model start at the same address. .text itself carries 256-byte alignment (vectored mtvec
# handlers), so _start cannot sit at +0x80 directly.
.option norvc
.section .gen_boot, "ax", @progbits
.globl gen_boot_entry
gen_boot_entry:
  j _start
