# T-235 part R (Runtime, to tb-infra's spec gen_t235_counters_spec.md): Ibex's counter CSR holders for the ISA shim

Deliverables (tb-infra's files: tb-infra reviews, integrates the install call and the minstret proxy, and copies in at its window;
Runtime never puts them in the shared tree):
- gen_isa_shim_counters.h / gen_isa_shim_counters.cc: gen_mcountinhibit_csr_t (mask computed from GEN_MHPM_COUNTER_NUM: 0x1FFD for 10;
  bit 1 and bits 31:13 read 0; reset 0; ir_inhibited() / cy_inhibited() for the proxy; Spike's own mcountinhibit untouched),
  gen_zero_csr_t (reads 0, writes ignored, no trap in M) for mhpmcounter13..31, mhpmcounter13h..31h and mhpmevent13..31 (the events
  duplicate legalize_after_reset's const-0 holders; either may stay), and gen_install_counter_holders(proc, s, out_inhibit) that places
  them in s->csrmap (idempotent per reset). Every rule cites the rtl/ibex_cs_registers.sv lines of gen_counter_csr_anchors.md section 10.
- gen_ut_isa_shim_t235.diff: the unit-test rows (section 14 of gen_ut_isa_shim.cc, 23 checks) against the tree's file; gen_ut_isa_shim.cc
  here is the tree file plus that section.
- scratch/gen_isa_shim.cc and scratch/gen_isa_shim_install_verification.diff: the verification copy of the shim with the ONE install
  line tb-infra lands (include, the g_mcountinhibit holder, the call beside the mhpmcounter loop in legalize_after_reset); not a deliverable.
- gen_t235_build_and_run.sh + gen_t235_ut_run.log: the out-of-tree verification (the shim build script's FLAGS and LIBS, the new .cc added).

Verification: `bash -lc 'source ci/env.sh && bash dv/auto_dv/work/runtime/t235/gen_t235_build_and_run.sh <zc prog.vmem>'` on
soc-l-11 with the gen_boot_zc image work/runtime/out/tick_canary_2057/runs/gen_boot_zc_1/program/prog.vmem: GEN_UT_ISA_SHIM PASS
(0 failures), 236 rows OK, the 23 new rows among them. (A first run with a non-zc image failed the 8 program-dependent rows of
sections 1 and 2 and none of the new ones; the unit test expects the Zcmp directed program, as its existing rows do.)

Integration note for tb-infra: add `#include "gen_isa_shim_counters.h"`, a `std::shared_ptr<gen_mcountinhibit_csr_t> g_mcountinhibit;`
beside g_hpm_lo/g_hpm_hi, and `gen_install_counter_holders(g_proc.get(), s, g_mcountinhibit);` in legalize_after_reset() after the
mhpmcounter loop (before the reset put_csr writes, which do not touch mcountinhibit); add gen_isa_shim_counters.cc to SRC in
gen_isa_shim_build.sh. The proxy reads g_mcountinhibit->ir_inhibited() / cy_inhibited().
