# gen_boot_retire_red.S: TDD red fixture for gen_test_boot_retire (dv/auto_dv/evidence/
# gen_tdd_test_template.md). Deliberately fails both halves of the test's fire-check: it ends with
# the FAIL end-of-test code (tohost 3) and declares a retirement floor (gen_min_retired) it never
# reaches. Never a regression test; runs measured: false under the name gen_test_boot_retire_red.
# Layout and end-of-test convention as dv/auto_dv/stim/gen_directed/gen_zc_directed.S.
.section .text
.globl _start
_start:
  li   t0, 0x600d
  li   t1, 0xbad
  add  t2, t0, t1
  li   gp, 3                        # FAIL verdict on purpose
  la   t5, tohost
  sw   gp, 0(t5)
1:
  j    1b

.section .data
.align 6
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.align 2
.globl gen_min_retired
gen_min_retired: .word 1000         # floor the fixture never reaches (it retires about a dozen)
