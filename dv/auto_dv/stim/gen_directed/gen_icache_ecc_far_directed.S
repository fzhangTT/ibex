# gen_icache_ecc_far_directed.S: enables the instruction cache once (cpuctrlsts.icache_enable) and then loops between two bodies placed
# exactly 2 KB apart, so their lines share every cache index under two different tags: after the first iteration each aliased index holds
# a valid line in both ways and a data-RAM ECC injection on either way is judged against a real hit-way decision (the misc monitor's data
# half), while every jump between the loop, body_a and body_b changes the lookup tag from one lookup to the next, which is what makes a
# misaligned read of the P9 lookup probe visible (the ALIGN mutation). Tag and data RAM injection rates are knobs. 1 to tohost at the end.
.section .text
.globl _start
_start:
  csrsi 0x7c0, 1                    # cpuctrlsts.icache_enable
  li   x6, 300
loop:
  addi x5, x5, 1
  jal  x1, body_a
  jal  x1, body_b
  bne  x5, x6, loop
  la   t5, tohost
  li   t6, 1
  sw   t6, 0(t5)
spin:
  j    spin

.balign 2048
body_a:                             # a 2 KB-aligned body: index 0 upward under tag A
  addi x7, x7, 1
  .rept 12
  nop
  .endr
  jalr x0, 0(x1)

.balign 2048
body_b:                             # body_a + 0x800: the same indices under tag B
  addi x8, x8, 1
  .rept 12
  nop
  .endr
  jalr x0, 0(x1)

.section .data
.balign 8
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
