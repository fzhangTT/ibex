# gen: riscv-dv user_init.s, emitted right after _start. Intentionally empty: the core's first
# fetch is boot_addr_i + 0x80 and gen_link.ld places _start there, so no boot fix-up is needed.
