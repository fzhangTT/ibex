# gen_prv_debug_b1_ctrl_directed.S: the passing control of B1 (gen_prv_debug_b1_directed.S). The same four parts, the same
# PMP region, the same debug ROM and the same rejoining handler, except that mstatus.MPRV is cleared instead of set before
# each dret, so the U-mode probe's load is checked with U privilege on both sides and both take the load access fault at the
# same record: the control shows the comparator can pass on this program shape, this debug ROM and this privilege change.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  la   t0, gen_u_probe              # one execute-only region over the probe: 64 bytes, NAPOT
  srli t0, t0, 2
  ori  t0, t0, 0x7
  csrw pmpaddr0, t0
  li   t1, 0x1C                     # A = NAPOT, X = 1, R = W = L = 0
  csrw pmpcfg0, t1
  la   a6, gen_b1_probe             # the word the U-mode probe loads; no region covers it
  li   a0, 0
gen_park:
  addi a0, a0, 1                    # a retiring park loop; the debug request arrives here
  j    gen_park

.balign 64
.globl gen_u_probe
gen_u_probe:
  lw   a5, 0(a6)                    # RTL: still checked with MPP = M and completes; model: MPRV cleared by dret, U, faults
  ecall                             # only the core that completed the load reaches this, and it rejoins the model here

.option push
.option norvc
.balign 256
gen_vec:
  j    gen_done                     # every synchronous exception of this program ends both paths in one loop
  .rept 31
  mret
  .endr
gen_done:
  j    gen_done
.option pop

# The program's own debug ROM: entry at DmHaltAddr, exception entry at DmHaltAddr + 8. It arms mstatus itself before every
# resume, because the probe's ecall leaves MPP = U behind and the second debug entry must resume into the same state.
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
  li   t0, 0x1800
  csrs mstatus, t0                  # MPP = M, the privilege the PMP would use while MPRV is set
  li   t0, 0x20000
  csrc mstatus, t0                  # MPRV = 0: the bug's trigger removed
  csrr t0, 0x7b0
  andi t0, t0, -4                   # dcsr.prv = U
  csrw 0x7b0, t0
  la   t1, gen_u_probe
  csrw 0x7b1, t1                    # dpc = the U-mode probe
  dret

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 4
.globl gen_b1_probe
gen_b1_probe: .word 0xB1B1B1B1
