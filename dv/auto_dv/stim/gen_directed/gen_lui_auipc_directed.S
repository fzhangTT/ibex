# gen_lui_auipc_directed.S: the U-type immediates of gen_isa_lui_auipc_cg (CG-ISA-004): lui and auipc with the immediate
# zero, all ones, the msb alone, one and an arbitrary value, into a register and into x0, at a word-aligned and at a
# half-aligned pc (a c.nop shifts the alignment). The pc regions below 0x1000 and above 0xFFFFF000 and the auipc wrap are
# not reachable from the program window at 0x80000080. The lock-step model checks every result. 1 to tohost at the end.
.option push
.option norvc
.section .text
.globl _start
_start:
  lui   t0, 0
  lui   t0, 0xFFFFF
  lui   t0, 0x80000
  lui   t0, 1
  lui   t0, 0x12345
  lui   x0, 0xFFFFF
  lui   x0, 0x12345
  auipc t1, 0
  auipc t1, 0xFFFFF
  auipc t1, 0x80000
  auipc t1, 1
  auipc t1, 0x12345
  auipc x0, 0x12345
  auipc x0, 0
  .2byte 0x0001                     # c.nop: the following instructions retire at a half-aligned pc
  lui   t0, 0x55555
  lui   t0, 0
  lui   x0, 0x80000
  lui   x0, 1
  auipc t1, 0x7FFFF
  auipc t1, 0xFFFFF
  auipc x0, 0x80000
  auipc x0, 1
  .2byte 0x0001                     # back to word alignment
  la    t5, tohost
  li    t6, 1
  sw    t6, 0(t5)
spin:
  j     spin
.option pop

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
