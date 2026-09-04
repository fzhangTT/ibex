# gen_intg_store_directed.S: one misaligned sw that spans two bus words, the first half's response carrying an injected
# integrity error (the cocotb test gen_ut_intg_store arms one corruption on the buffer), so the DUT takes the internal NMI
# with mtval = the store's own address, not the word's; the handler reads mtval so the lock-step compare judges it. Then a
# clean read-back. 1 to tohost at the end, then spin.
.section .text
.globl _start
_start:
  la   t0, gen_vec
  ori  t0, t0, 1
  csrw mtvec, t0
  la   a0, gen_store_buf
  li   a1, 0x5a5a5a5a
  sw   a1, 2(a0)                    # spans gen_store_buf+0 and +4: two bus accesses, the first corrupted
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  lw   a2, 0(a0)
  nop
  nop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.option push
.option norvc
.balign 256
gen_vec:
  .rept 32
  j    gen_handler
  .endr
gen_handler:
  csrr a5, mtval
  mret
.option pop

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.balign 16
.globl gen_store_buf
gen_store_buf: .word 0x11111111, 0x22222222, 0x33333333, 0x44444444
