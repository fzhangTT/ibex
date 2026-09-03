# gen_csr_warl_directed.S: write / read-back pairs on the trap-setup CSRs (mstatus, misa, mie, mtvec, mcounteren, mstatush,
# menvcfg, menvcfgh) with every CSR instruction form, rd = x0 and rd != x0, the plan's write patterns (all0, all1, msb, legal-only,
# illegal-only, mixed) and the field values the plan names (MPP, MIE/MPIE/MPRV/TW, mtvec mode / low bits / base classes, mie bit
# groups, mcounteren single bits). Every read-back is compared against the lock-step model, which legalises like Ibex; the run
# exists for gen_csr_trap_setup_warl_cg. mstatus.MPRV is never left set across a memory access. 1 to tohost at the end.
.macro wr csr, op, val
  li   t0, \val
  \op  t1, \csr, t0
  csrr t2, \csr
.endm
.macro wr0 csr, op, val
  li   t0, \val
  \op  x0, \csr, t0
  csrr t2, \csr
.endm
.macro wi csr, op, imm
  \op  t1, \csr, \imm
  csrr t2, \csr
.endm
.macro wi0 csr, op, imm
  \op  x0, \csr, \imm
  csrr t2, \csr
.endm
# the pattern set for a CSR with no writable bit (misa, mstatush, menvcfg, menvcfgh)
.macro roset csr
  wr  \csr, csrrw, 0
  wr  \csr, csrrw, 0xFFFFFFFF
  wr  \csr, csrrw, 0x80000000
  wr  \csr, csrrw, 0x12345678
  wr  \csr, csrrs, 0xFFFFFFFF
  wr  \csr, csrrs, 0x12345678
  wr  \csr, csrrc, 0xFFFFFFFF
  wr  \csr, csrrc, 0x80000000
  wr0 \csr, csrrw, 0x12345678
  wi  \csr, csrrwi, 0
  wi  \csr, csrrwi, 31
  wi  \csr, csrrsi, 31
  wi  \csr, csrrci, 31
  wi0 \csr, csrrwi, 5
.endm
.section .text
.globl _start
_start:
# ---- mstatus: patterns, then MPP by every op, then the MIE / MPIE / MPRV / TW combinations
  wr  mstatus, csrrw, 0
  wr  mstatus, csrrw, 0xFFFFFFFF
  wr  mstatus, csrrw, 0x80000000
  wr  mstatus, csrrw, 0x00221888
  wr  mstatus, csrrw, 0x00000001
  wr  mstatus, csrrw, 0x12345678
  wr  mstatus, csrrw, 0
  wr  mstatus, csrrs, 0xFFFFFFFF
  wr  mstatus, csrrw, 0
  wr  mstatus, csrrs, 0x00000008
  wr  mstatus, csrrs, 0x00000001
  wr  mstatus, csrrs, 0x12345678
  wr  mstatus, csrrc, 0xFFFFFFFF
  wr  mstatus, csrrw, 0x00221888
  wr  mstatus, csrrc, 0x00001888
  wr  mstatus, csrrc, 0x00000001
  wr  mstatus, csrrc, 0x12345678
  wr  mstatus, csrrc, 0x80000000
  wr0 mstatus, csrrw, 0x00000088
  wr0 mstatus, csrrs, 0x00000008
  wr0 mstatus, csrrc, 0x00000008
  wi  mstatus, csrrwi, 0
  wi  mstatus, csrrwi, 31
  wi  mstatus, csrrwi, 8
  wi  mstatus, csrrwi, 7
  wi  mstatus, csrrsi, 8
  wi  mstatus, csrrsi, 7
  wi  mstatus, csrrsi, 31
  wi  mstatus, csrrci, 8
  wi  mstatus, csrrci, 7
  wi  mstatus, csrrci, 31
  wi0 mstatus, csrrwi, 8
  wi0 mstatus, csrrsi, 8
  wi0 mstatus, csrrci, 8
  wr  mstatus, csrrw, 0x00000800
  wr  mstatus, csrrw, 0x00001000
  wr  mstatus, csrrw, 0x00001800
  wr  mstatus, csrrw, 0x00000000
  wr  mstatus, csrrs, 0x00000800
  wr  mstatus, csrrw, 0
  wr  mstatus, csrrs, 0x00001000
  wr  mstatus, csrrw, 0
  wr  mstatus, csrrs, 0x00001800
  wr  mstatus, csrrc, 0x00001800
  wr  mstatus, csrrw, 0x00000008
  wr  mstatus, csrrw, 0x00000080
  wr  mstatus, csrrw, 0x00020000
  wr  mstatus, csrrw, 0x00200000
  wr  mstatus, csrrw, 0x00220000
  wr  mstatus, csrrw, 0x00000088
  wr  mstatus, csrrw, 0x00220088
  wr  mstatus, csrrw, 0x00001880
# ---- misa, mstatush (0x310), menvcfg (0x30A), menvcfgh (0x31A): nothing writable (the assembler knows no name for the last three)
  roset misa
  roset 0x310
  roset 0x30A
  roset 0x31A
# ---- mie: patterns and the bit groups (mstatus.MIE is 0 throughout)
  wr  mie, csrrw, 0
  wr  mie, csrrw, 0xFFFFFFFF
  wr  mie, csrrw, 0x80000000
  wr  mie, csrrw, 0x7FFF0888
  wr  mie, csrrw, 0x00000001
  wr  mie, csrrw, 0x12345678
  wr  mie, csrrw, 0x00000888
  wr  mie, csrrw, 0x00010000
  wr  mie, csrrw, 0x00010888
  wr  mie, csrrw, 0x7FFF0000
  wr  mie, csrrw, 0
  wr  mie, csrrs, 0x00000888
  wr  mie, csrrw, 0
  wr  mie, csrrs, 0x00010000
  wr  mie, csrrs, 0x00000001
  wr  mie, csrrs, 0x12345678
  wr  mie, csrrw, 0x7FFF0888
  wr  mie, csrrc, 0x7FFF0000
  wr  mie, csrrw, 0x00010888
  wr  mie, csrrc, 0x00000888
  wr  mie, csrrc, 0x00000001
  wr  mie, csrrc, 0x12345678
  wr  mie, csrrc, 0xFFFFFFFF
  wr0 mie, csrrw, 0x00000888
  wi  mie, csrrwi, 0
  wi  mie, csrrwi, 8
  wi  mie, csrrwi, 7
  wi  mie, csrrwi, 31
  wi  mie, csrrsi, 8
  wi  mie, csrrsi, 7
  wr  mie, csrrw, 0x00000888
  wi  mie, csrrci, 8
  wi  mie, csrrci, 7
  wi  mie, csrrci, 31
  wi0 mie, csrrwi, 8
  wr  mie, csrrw, 0
# ---- mtvec: mode, low bits and base classes (restored to the boot page at the end)
  wr  mtvec, csrrw, 0
  wr  mtvec, csrrw, 0xFFFFFFFF
  wr  mtvec, csrrw, 0x80000000
  wr  mtvec, csrrw, 0x12345600
  wr  mtvec, csrrw, 0x000000FF
  wr  mtvec, csrrw, 0x12345678
  wr  mtvec, csrrw, 0x00000100
  wr  mtvec, csrrw, 0x00000101
  wr  mtvec, csrrw, 0x00000106
  wr  mtvec, csrrw, 0x80000105
  wr  mtvec, csrrw, 0x80000001
  wr  mtvec, csrrw, 0x80000002
  wr  mtvec, csrrw, 0x80000003
  wr  mtvec, csrrw, 0x8000007C
  wr  mtvec, csrrw, 0x90000002
  wr  mtvec, csrrw, 0x90000003
  wr  mtvec, csrrw, 0x90000010
  wr  mtvec, csrrw, 0x12345601
  wr  mtvec, csrrw, 0x12345602
  wr  mtvec, csrrw, 0x12345603
  wr  mtvec, csrrw, 0x12345644
  wr  mtvec, csrrw, 0
  wr  mtvec, csrrs, 0x12345600
  wr  mtvec, csrrw, 0
  wr  mtvec, csrrs, 0x90000000
  wr  mtvec, csrrs, 0x000000FF
  wr  mtvec, csrrw, 0x12345600
  wr  mtvec, csrrc, 0x00000100
  wr  mtvec, csrrc, 0x000000FF
  wr  mtvec, csrrc, 0xFFFFFFFF
  wr0 mtvec, csrrw, 0x12345600
  wi  mtvec, csrrwi, 0
  wi  mtvec, csrrwi, 31
  wi  mtvec, csrrsi, 31
  wi  mtvec, csrrci, 31
  wi0 mtvec, csrrwi, 1
  wr  mtvec, csrrw, 0x80000001
# ---- mcounteren: patterns, every single bit, the read-only bits
  wr  mcounteren, csrrw, 0
  wr  mcounteren, csrrw, 0xFFFFFFFF
  wr  mcounteren, csrrw, 0x80000000
  wr  mcounteren, csrrw, 0x00001FFD
  wr  mcounteren, csrrw, 0x00000002
  wr  mcounteren, csrrw, 0x12345678
  wr  mcounteren, csrrw, 0x00000001
  wr  mcounteren, csrrw, 0x00000004
  wr  mcounteren, csrrw, 0x00000008
  wr  mcounteren, csrrw, 0x00000010
  wr  mcounteren, csrrw, 0x00000020
  wr  mcounteren, csrrw, 0x00000040
  wr  mcounteren, csrrw, 0x00000080
  wr  mcounteren, csrrw, 0x00000100
  wr  mcounteren, csrrw, 0x00000200
  wr  mcounteren, csrrw, 0x00000400
  wr  mcounteren, csrrw, 0x00000800
  wr  mcounteren, csrrw, 0x00001000
  wr  mcounteren, csrrw, 0x00002000
  wr  mcounteren, csrrw, 0xFFFFE000
  wr  mcounteren, csrrw, 0
  wr  mcounteren, csrrs, 0x00000001
  wr  mcounteren, csrrs, 0xFFFFFFFF
  wr  mcounteren, csrrc, 0x00001FFC
  wr  mcounteren, csrrc, 0xFFFFFFFF
  wr0 mcounteren, csrrw, 0x00000004
  wi  mcounteren, csrrwi, 0
  wi  mcounteren, csrrwi, 1
  wi  mcounteren, csrrwi, 4
  wi  mcounteren, csrrwi, 31
  wi  mcounteren, csrrsi, 4
  wi  mcounteren, csrrci, 4
  wi0 mcounteren, csrrwi, 1
  wr  mcounteren, csrrw, 0
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
