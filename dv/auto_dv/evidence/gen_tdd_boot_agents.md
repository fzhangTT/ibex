# TDD transcript: bus agents, icache RAM models, scramble-key responder, control driver and the memory
# model wired into gen_env: the "boots and retires" milestone (build step 1c)

Components: `dv/auto_dv/tb/gen_bus_if.sv` (with the `sva_rvalid_legal` self-check), `dv/auto_dv/tb/gen_scrkey_if.sv`,
`dv/auto_dv/tb/gen_ctrl_if.sv`, `dv/auto_dv/tb/gen_icache_ram.sv`, `dv/auto_dv/env/gen_cfg_pkg.sv`,
`dv/auto_dv/env/gen_agents_pkg.sv` (gen_bus_cfg, gen_bus_txn, gen_bus_driver, gen_bus_agent, gen_scrkey_driver,
gen_ctrl_driver, gen_eot_handler, gen_record_handler), `dv/auto_dv/env/gen_env_pkg.sv` (gen_bridge with MEM_PEEK
over the model, gen_cmd_dispatch, gen_env, gen_base_test), `dv/auto_dv/tb/gen_tb_top.sv`, `dv/auto_dv/tb/gen_tb.f`,
`dv/auto_dv/gen_tb/gen_image.py`. Test: `dv/auto_dv/gen_tb/gen_tests/gen_ut_boot.py` (written first): image digest at
load, MEM_PEEK read-back of 64 seeded words against Python's own parse of the .vmem, release of the core
(FETCH_EN), a retirement threshold on the bridge's own edge bit, the program's tohost store (code 1 = pass), the
finish handshake. Out-trees: `dv/auto_dv/work/tb-infra/out_1c_red/` (red), `out_1c/` (green). Owner: tb-infra.

## 1. Red (the test on the step-1b top with tied-off DUT inputs and no memory model)

```
# RED run (boots-and-retires test on the tied-off step-1b top; compile out_1c_red vcs exit 0)
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1c_red/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/localdev/fzhang/
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
105.00ns ERROR    cocotb.gen_tb_top                  GEN_UT_BOOT read-back mismatch at word 0x800000e8: sv 0x00000000 vmem 0x19c09063
115.00ns ERROR    cocotb.gen_tb_top                  GEN_UT_BOOT read-back mismatch at word 0x800000f8: sv 0x00000000 vmem 0x33333e37
125.00ns ERROR    cocotb.gen_tb_top                  GEN_UT_BOOT read-back mismatch at word 0x8000012c: sv 0x00000000 vmem 0x12511e63
135.00ns ERROR    cocotb.gen_tb_top                  GEN_UT_BOOT read-back mismatch at word 0x80000130: sv 0x00000000 vmem 0xa0a0a537
145.00ns ERROR    cocotb.gen_tb_top                  GEN_UT_BOOT read-back mismatch at word 0x80000144: sv 0x00000000 vmem 0x0e13a0a0
15.00ns ERROR    cocotb.gen_tb_top                  GEN_UT_BOOT read-back mismatch at word 0x1a110800: sv 0x00000000 vmem 0x00c0006f
155.00ns ERROR    cocotb.gen_tb_top                  GEN_UT_BOOT read-back mismatch at word 0x8000014c: sv 0x00000000 vmem 0xae3711c4
UVM_ERROR count: 64
```

Every MEM_PEEK was a collected `uvm_error` (no memory model) and the read-back assert failed; nothing
retired. 64 UVM errors, cocotb FAIL.

## 2. Green attempts (defects found on the way, disclosed)

- Compile 1: `Error-[NCE]` in `gen_icache_ram.sv` (a variable-width part-select in the random
  initialisation); fixed with a bitwise fill.
- Run 1 (compile 2, vcs exit 0): image loaded and digest verified; the read-back reported ONE mismatch
  of 64 (`0x80000398: sv 0x33333333 vmem 0x00000000`): the core had already booted and executed the Zc
  program's `cm.push`, which stores to that word, while Python was still peeking. The read-back did its
  job (it caught memory traffic); the TEST SEQUENCE was wrong. Fix: the TB drives `fetch_enable_i` from
  `+gen_fetch_en_at_reset` (new knob, default 1) through the new control driver, the boot test runs with
  `+gen_fetch_en_at_reset=0` and releases the core with the bridge command FETCH_EN(1) after the read-back
  (the FETCH_EN command gained its consumer, `gen_cmd_dispatch` -> `gen_ctrl_driver`).

## 3. Green: directed Zc program (compile 3, vcs exit 0, 0 errors)

```
boot_zc (out_1c):
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1c/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/localdev/fzhang/ws/ibex-challe
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(406) @ 64500: uvm_test_top.env.ctrl [GEN_CTRL] fetch_enable_i <= On (FETCH_EN arg 1)
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(245) @ 519000: uvm_test_top [GEN_BASE_TEST] finish_req seen at cycle 514, commands consumed 65, retired 169
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 519000: uvm_test_top.env.dbus_agent [gen_bus_agent] dbus gnt=1..3(short) rvalid=1..3(short) cap=2(cap2) err=0/1000(none) intg=0/1000(none)x1: grants=29 responses=28 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 519000: uvm_test_top.env.ibus_agent [gen_bus_agent] ibus gnt=1..3(short) rvalid=1..3(short) cap=8(cap8) err=0/1000(none) intg=0/1000(none)x1: grants=140 responses=139 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(160) @ 519000: uvm_test_top.env [GEN_ENV] mem: 204 words, 0 mmio writes, 0 unmapped accesses; eot stores 1 (last code 0x00000001); sig writes 0; key requests 0; commands routed 65 ignored 0
UVM_ERROR :    0
UVM_FATAL :    0
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
645.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BOOT read-back ok: 64 words
3475.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BOOT retired 100 (target 100) at cycle 343
5190.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BOOT tohost code 0x00000001
5190.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BOOT_PASS
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                      5190.01           0.05      97647.59  **
Time: 5190010 ps
```

## 4. Green: riscv-dv program (seed 7, debug section, 29375 words), same build

```
boot_rdv_s7 (out_1c):
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1c/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=/localdev/fzhang/ws/ibex-challe
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(406) @ 64500: uvm_test_top.env.ctrl [GEN_CTRL] fetch_enable_i <= On (FETCH_EN arg 1)
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(245) @ 9407500: uvm_test_top [GEN_BASE_TEST] finish_req seen at cycle 9403, commands consumed 65, retired 2000
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 9407500: uvm_test_top.env.dbus_agent [gen_bus_agent] dbus gnt=1..3(short) rvalid=1..3(short) cap=2(cap2) err=0/1000(none) intg=0/1000(none)x1: grants=547 responses=547 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(321) @ 9407500: uvm_test_top.env.ibus_agent [gen_bus_agent] ibus gnt=1..3(short) rvalid=1..3(short) cap=8(cap8) err=0/1000(none) intg=0/1000(none)x1: grants=2955 responses=2955 injected_err=0 injected_intg=0
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(160) @ 9407500: uvm_test_top.env [GEN_ENV] mem: 29375 words, 0 mmio writes, 0 unmapped accesses; eot stores 483 (last code 0x00000001); sig writes 0; key requests 5; commands routed 65 ignored 0
UVM_ERROR :    0
UVM_FATAL :    0
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
645.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BOOT read-back ok: 64 words
94075.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BOOT retired 2000 (target 2000) at cycle 9403
94075.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BOOT tohost code 0x00000001
94075.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BOOT_PASS
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                     94075.01           0.31     300962.19  **
Time: 94075010 ps
```

The riscv-dv program reaches its `test_done` tohost store with code 1 and spins on it (483 stores by the
end); the retirement threshold of 2000 was reached at cycle 9403. Bus agents in the default regimes
(gnt short 1..3, rvalid short 1..3, cap 8 / 2, no injection); `sva_rvalid_legal` armed and silent.

## 5. Bridge regression on the same build

```
ut_bridge_1c_b (out_1c):
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1c/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan -l /localdev/fzhang/ws/ibex-challenge/dv/auto_
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(245) @ 77500: uvm_test_top [GEN_BASE_TEST] finish_req seen at cycle 73, commands consumed 6, retired 9
UVM_ERROR :    0
UVM_FATAL :    0
775.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BRIDGE cycles 1 -> 52 -> 73, consumed 6
775.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BRIDGE_PASS
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                           775.01           0.03      27146.70  **
Time: 775010 ps
```

(The first re-run, `ut_bridge_1c`, produced one collected `uvm_error`: its REGIME_SET command now
reaches `gen_cmd_dispatch`, which errors on a kind without a consumer, by design; the unit test's sixth
command became a MISC and the run above is clean. REGIME_SET gets its consumer in step 2.)
