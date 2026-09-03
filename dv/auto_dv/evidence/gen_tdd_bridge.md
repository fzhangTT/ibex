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

## 5. T-068 (2026-09-03): retention audit, the uvm_error path forced red, new guards

Retained logs: `dv/auto_dv/evidence/gen_tdd_logs/bridge/` (manifest `gen_tdd_logs/gen_manifest.md`). The 1b
logs quoted in Sections 1-4 are retained there as `gen_handles_red.log`, `gen_handles_green.log`, `gen_bridge_red.log`,
`gen_ut_bridge_red_1b_sim.log`, `gen_ut_bridge_green_1b_*.log`, `gen_neg_noalive_1b_*.log`, `gen_neg_unknown_plusarg_1b_*.log`,
`gen_neg_bad_enum_1b_*.log`.

Correction to Section 2: the two compile defects disclosed there (5 UTOPN, 10 ICPD_INIT) have no retained
compile log; `out_1b_red/compile.log` is the third, clean compile. They are UNRETAINED (the fixes are visible in
the code: `ibex_cheriot_pkg::cap_t`, `always` in gen_bridge_if).

### 5.1 The uvm_error failure path forced red through the flow's verdict (Critic 1b M-1)

The dangerous form for a cocotb-master TB is cocotb PASS with UVM_ERROR > 0. Two runs show it and the flow's
verdict (`gen_verdict.decide`, the same function `gen_run.py` uses) fails both:

1. Accidental evidence from step 1c (retained `gen_ut_bridge_1c_uvm_error_sim.log` / `_stdout.log`): gen_ut_bridge's
   REGIME_SET command reached `gen_cmd_dispatch`, which errors on a kind without a consumer:
   ```
   UVM_ERROR dv/auto_dv/env/gen_env_pkg.sv(84) @ 5500: uvm_test_top.env.dispatch [GEN_CMD_DISPATCH] command REGIME_SET has no consumer yet
   UVM_ERROR :    1
   ** TESTS=1 PASS=1 FAIL=0 SKIP=0
   ```
   Verdict on that log (run by the step-1c reviewer and again in T-068): FAIL, uvm_error.
2. Deliberate run on the T-068 build, `neg_uvm_error_cocotb_pass` (gen_ut_bridge with `+gen_boot_addr=00000000`:
   the first fetch hits the unmapped page, every fetch is a collected `MEM_UNMAPPED` error, the bridge test
   itself passes). Retained `gen_neg_uvm_error_cocotb_pass_t068_sim.log`, `_stdout.log`, `_verdict.txt`:
   ```
   UVM_ERROR @ 9000: reporter [MEM_UNMAPPED] read of unmapped address 0x00000080
   UVM_ERROR :   23
   ** TESTS=1 PASS=1 FAIL=0 SKIP=0
   verdict: FAIL
   reason: uvm_error at log line 30
   uvm_counts: {'INFO': 13, 'WARNING': 1, 'ERROR': 23, 'FATAL': 0}
   cocotb_summary: {'tests': 1, 'passed': 1, 'failed': 0, 'skipped': 0}
   ```
   The Critic named MEM_PEEK-without-a-model as the provoker; at HEAD `gen_env` always builds the memory model,
   so that branch of `gen_bridge::peek_word` is unreachable from a run. The unmapped-boot form exercises the same
   mechanism (a `uvm_error` raised by a TB component while Python finishes cleanly).

### 5.2 New guards proven red on the T-068 build

- Bare bool plusarg (`gen_neg_bare_bool_t068_sim.log`): `+gen_chk_all` without `=`:
  `UVM_FATAL dv/auto_dv/env/gen_env_pkg.sv(200) @ 0: uvm_test_top [GEN_BARE_PLUSARG] +gen_chk_all needs =0 or =1 (a bare bool plusarg would be a silent no-op)`; verdict FAIL uvm_fatal.
- Vacuous-pass guard (TB_CONTRACT Section 6): a pure-SV build of gen_tb_top (no `+define+COCOTB_SIM`, no cocotb
  triple; `dv/auto_dv/work/tb-infra/out_t068_nococotb`, vcs exit 0) run directly (`gen_neg_no_cocotb_t068_sim.log`):
  `UVM_FATAL dv/auto_dv/env/gen_env_pkg.sv(210) @ 0: uvm_test_top [GEN_NO_COCOTB] gen_tb_top tests are cocotb-driven; a pure-SV build of this top would pass vacuously (TB_CONTRACT Section 6)`.
- The three 1b negatives re-run on the T-068 build with the flow's verdict: `neg_noalive` (`GEN_ALIVE_TIMEOUT:
  Python never set the alive bit within 3000 cycles`, verdict FAIL sv_fatal), `neg_unknown_plusarg` and
  `neg_bad_enum` (UVM_FATAL at 0, verdict FAIL uvm_fatal); the negative module now resolves its handles through
  `GenHandles` and waits with one `Timer` instead of 20000 `ClockCycles`.
- Green re-run `gen_ut_bridge_green_t068_*`: `GEN_UT_BRIDGE_PASS`, `UVM_ERROR : 0`, `TESTS=1 PASS=1`, verdict PASS.

### 5.3 Behaviour changes in this landing

`GenBridge.finish()` asserts the command accounting first, then drops `stim_active`, then raises `finish_req`
(TB_CONTRACT Section 2 ordering) and takes its default budget from `+gen_finish_timeout` (whose default is the
rendered `GEN_FINISH_TIMEOUT_CYCLES_DEFAULT`); the banner prints `boot_addr` and `hart_id`
(`GEN_CONFIG_BANNER boot_addr=0x80000000 hart_id=0x00000000 alive_timeout=100000 finish_timeout=20000 ...`);
`gen_cmd_item::kind_name()` uses the rendered `gen_cmd_name()`; the clock half period is written in explicit ns.
Each local run now writes `run_header.txt` (UTC stamp, host, seed, module, plusargs) and `verdict.txt`.

### 5.4 df83749 review follow-up: the +gen_finish_timeout path exercised, the negative test's budget derived

`gen_ut_bridge` passes no finish budget, so `GenBridge.finish()` takes `+gen_finish_timeout` or its rendered default
and logs the source. Retained (`gen_tdd_logs/bridge/*_t068b_*`, build `gen_compile_t068b.log`, vcs exit 0):
`gen_ut_bridge_green_plusarg_budget`: `GEN_BRIDGE finish budget 20000 cycles (+gen_finish_timeout or its default)`,
PASS; `gen_ut_bridge_green_finish_timeout_50`: `finish budget 50 cycles`, PASS; `gen_neg_finish_timeout_1`:
`finish budget 1 cycles`, and the run PASSES: the finish handshake (objection drop, UVM report, `finish_ack` in
final_phase) completes within one cycle of `finish_req`, so no budget can trip it on this TB; the timeout path is
the `_edge` helper that the step-1b bridge red run proved (`no edge on listener_armed within 2000 cycles`). The
negative module derives its wait from the alive timeout in force (`2 x +gen_alive_timeout`):
`gen_neg_noalive_derived`: `GEN_ALIVE_TIMEOUT: Python never set the alive bit within 3000 cycles`, verdict FAIL sv_fatal.
