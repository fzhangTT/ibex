# TDD transcript: RVFI monitor + scoreboard with the Spike lock-step comparator (build step 2a)

Components: `dv/auto_dv/tb/gen_rvfi_if.sv`, `dv/auto_dv/env/gen_rvfi_pkg.sv` (gen_rvfi_txn, gen_rvfi_monitor,
gen_scoreboard), `dv/auto_dv/isa/gen_isa_dpi_pkg.sv` + the shim library (`gen_tdd_isa_shim.md`), the
`evt_isa_records` / `evt_isa_mismatch` bridge fields, `+gen_sb_trace`, `+gen_ut_lockstep_min_ratio_pct`.
Test: `dv/auto_dv/gen_tb/gen_tests/gen_ut_lockstep.py` (written first): the boot flow plus "every retired
record was consumed by the comparator with zero mismatches". Out-trees `dv/auto_dv/work/tb-infra/out_2a_red/`
(red), `out_2a/` (green attempts). Owner: tb-infra.

## 1. Red (the test on the step-1c top: no RVFI monitor, no scoreboard)

```
# RED run (lock-step test on the step-1c top: no RVFI monitor, no scoreboard; compile out_2a_red vcs exit 0)
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_2a_red/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
5190.00ns INFO     cocotb.gen_tb_top                  GEN_UT_LOCKSTEP retired 169 compared 0 mismatches 0 tohost 0x00000001
assert compared * 100 >= retired * min_ratio, f"GEN_UT_LOCKSTEP: compared {compared} of {retired} retired records (< {min_ratio}%)"
AssertionError: GEN_UT_LOCKSTEP: compared 0 of 169 retired records (< 90%)
** TESTS=1 PASS=0 FAIL=1 SKIP=0                                              5190.01           0.06      90266.84  **
Time: 5190010 ps
```

## 2. Attempt 1 (comparator wired; 136 collected `uvm_error`s on the Zc program, all TB-side interpretation)

- `isa_mem` on every non-store record: `rvfi_mem_rmask` is 1111 on records that read nothing, with
  `rvfi_mem_addr` = the ALU result. RTL: `rvfi_stage_mem_rmask[i] <= data_we_o ? 4'b0000 :
  rvfi_mem_mask_int` (rtl/ibex_core.sv:2085) with the mask following `lsu_type` alone (:2253-2260); no
  LSU-request qualifier. An RVFI-port deviation reported to rtl-arch and the DV Lead as a bug candidate;
  the scoreboard now infers a DUT read from the model's own access, compares `wmask` directly (it is
  gated), and counts the observation (`rvfi_rmask_on_nonload` in the GEN_SB report).
- `isa_insn` once per Zcmp sequence: the micro-op records carry the EXPANDED 32-bit instruction in
  `rvfi_insn`; the encoding the model executes as one instruction is `rvfi_ext_expanded_insn` (16 bits).
  The fold now compares that.

## 3. Attempt 2 (0 mismatches on Zc; the riscv-dv program exposed a model gap)

- Zc: retired 169, compared 148 + 21 micro-op records folded, mismatches 0; the TEST's ratio metric
  compared `compared` alone against retirements and failed at 148/169: `evt_isa_records` now counts
  records CONSUMED (compared once each, Zcmp micro-ops through their fold).
- riscv-dv seed 7: 8516 mismatches, all downstream of order 17: `csrs mseccfg, x4` (0x74725073)
  retired on the DUT but trapped (cause 2) in the model: Spike implements mseccfg only with the
  `smepmp` extension, which Ibex implements (MML/MMWP/RLB). The ISA string (single source
  `gen_tb_knobs.yaml`) gained `_smepmp`; standalone Spike (`gen_program.py --spike-check`) accepts it.
- Forced red of the compare path (TB_CONTRACT Section 3): `+gen_isa_string=rv32imc_zicsr_zifencei`
  (a model without Zc/Zb) against the Zc program: 637 collected mismatches, cocotb FAIL. The compare fires.

## 4. Green (attempt 3: `smepmp` in the model, records-consumed metric; compile `out_2a`, vcs exit 0)

Directed Zc program:

```
lockstep_zc:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_2a/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(167) @ 0: uvm_test_top.env.sb [GEN_SB] ISA model ready: pc=80000080 mtvec=80000001
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(251) @ 519000: uvm_test_top [GEN_BASE_TEST] finish_req seen at cycle 514, commands consumed 65, retired 169
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 519000: uvm_test_top.env.dbus_agent [gen_bus_agent] dbus gnt=1..3(short) rvalid=1..3(short) cap=2(cap2) err=0/1000(none) intg=0/1000(none)x1: grants=29 responses=28 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 519000: uvm_test_top.env.ibus_agent [gen_bus_agent] ibus gnt=1..3(short) rvalid=1..3(short) cap=8(cap8) err=0/1000(none) intg=0/1000(none)x1: grants=140 responses=139 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(121) @ 519000: uvm_test_top.env.rvfi_mon [GEN_RVFI_MON] records=169 irq_markers=0
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(292) @ 519000: uvm_test_top.env.sb [GEN_SB] ISA compare: records=148 mismatches=0 folded=31 draft_b=0 traps=0 irq_entries=0 dbg_entries=0 rvfi_rmask_on_nonload=126
UVM_ERROR :    0
UVM_FATAL :    0
[GEN_RVFI_MON]     1
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
5190.00ns INFO     cocotb.gen_tb_top                  GEN_UT_LOCKSTEP retired 169 compared 179 mismatches 0 tohost 0x00000001
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                              5190.01           0.07      73549.86  **
Time: 5190010 ps
```

riscv-dv seed-7 program (debug section, 29375 words), 2000 records in lock-step:

```
lockstep_s7:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_2a/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(167) @ 0: uvm_test_top.env.sb [GEN_SB] ISA model ready: pc=80000080 mtvec=80000001
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(251) @ 9407500: uvm_test_top [GEN_BASE_TEST] finish_req seen at cycle 9403, commands consumed 65, retired 2000
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 9407500: uvm_test_top.env.dbus_agent [gen_bus_agent] dbus gnt=1..3(short) rvalid=1..3(short) cap=2(cap2) err=0/1000(none) intg=0/1000(none)x1: grants=547 responses=547 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 9407500: uvm_test_top.env.ibus_agent [gen_bus_agent] ibus gnt=1..3(short) rvalid=1..3(short) cap=8(cap8) err=0/1000(none) intg=0/1000(none)x1: grants=2955 responses=2955 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(121) @ 9407500: uvm_test_top.env.rvfi_mon [GEN_RVFI_MON] records=2000 irq_markers=0
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(292) @ 9407500: uvm_test_top.env.sb [GEN_SB] ISA compare: records=2000 mismatches=0 folded=0 draft_b=0 traps=1 irq_entries=0 dbg_entries=0 rvfi_rmask_on_nonload=1452
UVM_ERROR :    0
UVM_FATAL :    0
[GEN_RVFI_MON]     1
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
94075.00ns INFO     cocotb.gen_tb_top                  GEN_UT_LOCKSTEP retired 2000 compared 2000 mismatches 0 tohost 0x00000001
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                             94075.01           0.34     275645.95  **
Time: 94075010 ps
```

Forced red kept as the proof that the compare fires (model without Zc/Zb):

```
lockstep_forced_red:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_2a/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/
UVM_INFO dv/auto_dv/env/gen_rvfi_pkg.sv(167) @ 0: uvm_test_top.env.sb [GEN_SB] ISA model ready: pc=80000080 mtvec=80000001
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
5190.00ns INFO     cocotb.gen_tb_top                  GEN_UT_LOCKSTEP retired 169 compared 179 mismatches 637 tohost 0x00000001
AssertionError: GEN_UT_LOCKSTEP: 637 ISA mismatches
** TESTS=1 PASS=0 FAIL=1 SKIP=0                                              5190.01           0.09      59807.62  **
Time: 5190010 ps
```

What green proves: every retired record of both programs was consumed by the comparator (Zcmp micro-ops
through their fold), the model stepped once per record with matching pc, instruction, retirement/trap
status, rd address and value, memory access presence, address and full-word store data, privilege and
next pc; UVM_ERROR 0, cocotb PASS. The forced red shows the same path producing 637 collected
`uvm_error`s (isa_pc, isa_insn, isa_rd, isa_pc_next) when the model diverges, so a silent comparator is
excluded. The three fixes on the way (Zcmp insn source, rmask-independent memory compare, `smepmp`) are
disclosed in Sections 2 and 3; none touched the DUT.

Bookkeeping note (found in the GEN_SB report of the green runs, fixed after them, re-verified with the
next compile): the report showed `folded=31` for the Zc program although only 21 micro-op records precede
their sequences' last records; the last record of each of the 10 sequences was counted both as compared
and as folded, so `evt_isa_records` read 179 for 169 retirements (the ratio check passed on `>=`). The
fold counter now excludes the last record; the compare itself was unaffected.
