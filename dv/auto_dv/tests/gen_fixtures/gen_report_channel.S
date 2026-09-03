# gen_report_channel.S: local fixture for the template's program report channel (committed fixture, never a testlist entry).
# Stores three report words to the EOT MMIO register (each toggles evt_eot_seen), then tohost 1.
# The report words are architectural facts the program computed itself (a sum, a shifted value, a
# retirement marker), so Python can assert them.
.include "gen_report_fixture_map.h"
.section .text
.globl _start
_start:
  li   t0, 0x600d
  li   t1, 0x0bad
  add  t2, t0, t1                   # 0x6bba
  li   t3, GEN_EOT_ADDR
  sw   t2, 0(t3)                    # report 0: the sum
  slli t4, t0, 4                    # 0x600d0
  sw   t4, 0(t3)                    # report 1: the shifted value
  li   t5, 0xc0de0003
  sw   t5, 0(t3)                    # report 2: a marker
  li   gp, 1
  la   t6, tohost
  sw   gp, 0(t6)                    # end of test, pass
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
gen_min_retired: .word 12
