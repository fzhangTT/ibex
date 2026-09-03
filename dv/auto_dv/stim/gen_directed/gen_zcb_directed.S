# gen_zcb_directed.S: every Zcb instruction: c.lbu / c.sb with every uimm, c.lhu / c.lh / c.sh with both uimm values, loaded data with
# the sign bit clear and set, half-word accesses aligned, off by one and crossing a word boundary (split into two bus accesses), the
# ALU forms (c.zext.b, c.sext.b, c.zext.h, c.sext.h, c.not) over the operand classes, c.mul with equal and distinct registers. The
# encodings are emitted explicitly (the assembler compresses to them only when it may); the lock-step model checks every result; the
# run exists for gen_cmp_zcb_cg. 1 to tohost at the end.
.option norelax
.section .text
.globl _start
# c.lbu rd', uimm(rs1') and c.sb: 100 0 00 rs1' uimm[0] uimm[1] rd' 00  ... the 16-bit fields are assembled by the macros below
.macro c_lbu rd, rs1, u
  .2byte 0x8000 | (\rs1 << 7) | (\rd << 2) | ((\u & 1) << 6) | ((\u & 2) << 4)
.endm
.macro c_sb rs2, rs1, u
  .2byte 0x8800 | (\rs1 << 7) | (\rs2 << 2) | ((\u & 1) << 6) | ((\u & 2) << 4)
.endm
.macro c_lhu rd, rs1, u
  .2byte 0x8400 | (\rs1 << 7) | (\rd << 2) | ((\u & 2) << 4)
.endm
.macro c_lh rd, rs1, u
  .2byte 0x8440 | (\rs1 << 7) | (\rd << 2) | ((\u & 2) << 4)
.endm
.macro c_sh rs2, rs1, u
  .2byte 0x8C00 | (\rs1 << 7) | (\rs2 << 2) | ((\u & 2) << 4)
.endm
.macro c_alu rd, f
  .2byte 0x9C01 | (\rd << 7) | (\f << 2)
.endm
.macro c_mul rd, rs2
  .2byte 0x9C41 | (\rd << 7) | (\rs2 << 2)
.endm
.set ZEXT_B, 0x18
.set SEXT_B, 0x19
.set ZEXT_H, 0x1A
.set SEXT_H, 0x1B
.set NOT, 0x1D
# rd' / rs1' / rs2' fields: 0 = s0, 1 = s1, 2 = a0, 3 = a1, 4 = a2, 5 = a3, 6 = a4, 7 = a5 (x8..x15)
_start:
  la   s0, buf
# stores then loads of every uimm; the data registers (fields 1..4 = s1, a0, a1, a2) hold a byte / half with the sign bit clear and set
  li   s1, 0x7F
  li   a0, 0x80
  li   a1, 0x7FFF
  li   a2, 0x8001
  .irp u, 0, 1, 2, 3
  c_sb 1, 0, \u
  c_lbu 5, 0, \u
  c_sb 2, 0, \u
  c_lbu 5, 0, \u
  .endr
  .irp u, 0, 2
  c_sh 3, 0, \u
  c_lhu 5, 0, \u
  c_lh 5, 0, \u
  c_sh 4, 0, \u
  c_lhu 5, 0, \u
  c_lh 5, 0, \u
  .endr
# half-word accesses at base + 1 (off by one, one bus access) and base + 3 (crossing the word, two bus accesses)
  addi s0, s0, 1
  c_sh 3, 0, 0
  c_lhu 5, 0, 0
  c_lh 5, 0, 0
  c_sh 4, 0, 2
  c_lhu 5, 0, 2
  c_lh 5, 0, 2
  addi s0, s0, 2
  c_sh 3, 0, 0
  c_lhu 5, 0, 0
  c_lh 5, 0, 0
  c_sh 4, 0, 2
  c_lhu 5, 0, 2
  c_lh 5, 0, 2
# the ALU forms over the operand classes: 0, all ones, bit 7 set / bit 15 clear, bits 7 and 15 clear, bit 15 set
  .irp f, ZEXT_B, SEXT_B, ZEXT_H, SEXT_H, NOT
  li   a0, 0
  c_alu 2, \f
  li   a0, -1
  c_alu 2, \f
  li   a0, 0x12340080
  c_alu 2, \f
  li   a0, 0x12340070
  c_alu 2, \f
  li   a0, 0x12348070
  c_alu 2, \f
  .endr
# c.mul: distinct and equal registers, the first operand over the classes
  li   a1, 7
  li   a2, 9
  c_mul 3, 4
  c_mul 3, 3
  li   a1, 0
  c_mul 3, 4
  li   a1, -1
  c_mul 3, 4
  li   a1, 0x12348070
  c_mul 3, 4
  li   a1, 0x12340080
  c_mul 3, 4
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 16
buf:      .space 32
