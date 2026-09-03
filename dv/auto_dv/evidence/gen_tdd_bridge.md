# TDD transcript: gen_tb_top, gen_bridge_if, gen_env_pkg (bridge), gen_handles.py, gen_bridge.py (build step 1b)

Components: `dv/auto_dv/tb/gen_tb_top.sv`, `dv/auto_dv/tb/gen_bridge_if.sv`, `dv/auto_dv/env/gen_env_pkg.sv`
(gen_env_cfg, gen_cmd_item, gen_bridge, gen_env, gen_base_test), `dv/auto_dv/gen_tb/gen_handles.py`,
`dv/auto_dv/gen_tb/gen_bridge.py`, filelist `dv/auto_dv/tb/gen_tb.f`, local driver `dv/auto_dv/tb/gen_tb_local.sh`.
Tests: `dv/auto_dv/tb/unit/gen_ut_handles.py` (pure Python), `dv/auto_dv/gen_tb/gen_tests/gen_ut_bridge.py`
(cocotb, on gen_tb_top with the DUT inputs tied idle), `gen_ut_bridge_neg.py` (forced red of the alive
watchdog). Runs: `dv/auto_dv/work/tb-infra/out_1b_red/` (red), `out_1b/` (green and negatives); logs also
under `dv/auto_dv/work/tb-infra/tdd/`. Owner: tb-infra. Rule: dv_principles Section 6 (failing check first).

## 1. gen_handles.py: red then green (pure Python)

```
# RED run: 2026-09-03T07:26:25Z host=soc-l-11 cmd: python3 dv/auto_dv/tb/unit/gen_ut_handles.py
FAIL module exists (/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/gen_tb/gen_handles.py)
GEN_UT_HANDLES FAIL (1 failures)
exit=1
# GREEN run: 2026-09-03T07:28:02Z host=soc-l-11 cmd: python3 dv/auto_dv/tb/unit/gen_ut_handles.py
GEN_UT_HANDLES PASS (0 failures)
exit=0
```

## 2. Bridge: red (cocotb test against a stubbed gen_bridge whose run_phase arms nothing)

The full `gen_bridge` run_phase was replaced by an empty stub for this compile
(`dv/auto_dv/work/tb-infra/tdd/gen_env_pkg_full.sv` holds the implementation that was restored
afterwards). Two compile defects were found and fixed on the way to the red run and are disclosed:
`cap_t` needed the `ibex_cheriot_pkg::` qualifier in gen_tb_top (5 UTOPN errors), and the interface's
initialised variables could not be driven by `always_ff` (10 ICPD_INIT errors; changed to `always`).
Third compile: vcs exit 0. The red run then failed exactly where a missing bridge must fail:

```
# RED run (stubbed bridge): compile out_1b_red vcs exit 0; run ut_bridge_red
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b_red/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build
Time: 20000010 ps
CPU Time:      0.270 seconds;       Data structure size:   8.7Mb
0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
raise AssertionError(f"GEN_BRIDGE: no edge on {what} within {cycles} cycles ({type(exc).__name__})") from None
AssertionError: GEN_BRIDGE: no edge on listener_armed within 2000 cycles (SimTimeoutError)
** dv.auto_dv.gen_tb.gen_tests.gen_ut_bridge.gen_ut_bridge   FAIL       20000.01           0.05     366199.81  **
** TESTS=1 PASS=0 FAIL=1 SKIP=0                                         20000.01           0.07     300944.32  **
Time: 20000010 ps
CPU Time:      0.270 seconds;       Data structure size:   8.7Mb
```

## 3. Bridge: green (full gen_bridge restored, fresh compile `out_1b`, vcs exit 0, 0 errors)

```
ut_bridge_green:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan -l /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b/ut_bridge_green/sim.log
UVM_INFO dv/auto_dv/env/gen_env_pkg.sv(195) @ 77500: uvm_test_top [GEN_BASE_TEST] finish_req seen at cycle 73, commands consumed 6
775.00ns INFO     cocotb.gen_tb_top                  GEN_BRIDGE finished: 6 commands sent and consumed, 0 retirements counted
775.00ns INFO     cocotb.gen_tb_top                  GEN_UT_BRIDGE_PASS
** TESTS=1 PASS=1 FAIL=0 SKIP=0                                           775.01           0.02      43545.49  **
Time: 775010 ps
```

The green run proves: alive set, `listener_armed` awaited by edge, six commands (five MISC, one
REGIME_SET) each acked with the matching `cmd_ack_seq`, two cycle thresholds armed and hit by their own
edge bit (cycles 1 -> 52 -> 73 for targets +50 and +20; N-02), `cmds_consumed == 6`, finish handshake
(objection dropped on `finish_req`, `finish_ack` after the UVM report), UVM_ERROR 0, UVM_FATAL 0, cocotb
PASS=1. VPI access to the interface instance `gen_tb_top.u_bridge_if.*` works with the SIM_RECIPE
Section 4 triple.

## 4. Failure paths proven red (TB_CONTRACT Section 3: each mechanism forced once)

```
neg_noalive:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_alive_timeout=3000 -l /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b/neg_noalive/sim.log
GEN_ALIVE_TIMEOUT: Python never set the alive bit within 3000 cycles
** TESTS=1 PASS=0 FAIL=1 SKIP=0                                                     29995.00           0.04     750806.55  **
Time: 29995000 ps

neg_unknown_plusarg:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_bogus=1 -l /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b/neg_unknown_plusarg/sim.log
UVM_FATAL dv/auto_dv/env/gen_env_pkg.sv(148) @ 0: uvm_test_top [GEN_UNKNOWN_PLUSARG] unknown plusarg +gen_bogus=1 (names live in gen_tb_knobs.yaml)
** TESTS=1 PASS=0 FAIL=1 SKIP=0                                             0.00           0.01          0.00  **
Time: 00 ps

neg_bad_enum:
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_knob_irq_regime=loud -l /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/tb-infra/out_1b/neg_bad_enum/sim.log
UVM_FATAL dv/auto_dv/env/gen_env_pkg.sv(159) @ 0: uvm_test_top [GEN_BAD_KNOB] +gen_knob_irq_regime=loud not in quiet,sparse,storm
** TESTS=1 PASS=0 FAIL=1 SKIP=0                                             0.00           0.01          0.00  **
Time: 00 ps
```

The alive watchdog `$fatal`s when Python never sets `alive` (budget from `+gen_alive_timeout`); an
unknown `+gen_*` plusarg is `uvm_fatal GEN_UNKNOWN_PLUSARG` at time 0 (A-23); an enum knob value outside
its yaml set is `uvm_fatal GEN_BAD_KNOB` naming the legal values. In all three the cocotb test reports
FAIL, so the run fails through collected mechanisms, never through the exit code (simv exits 0 each time).
