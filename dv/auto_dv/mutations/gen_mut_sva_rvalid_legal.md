# MUT-003: sva_rvalid_legal (gen_bus_if) caught with hidden referees inert; ablation control

Format: dv/auto_dv/mutations/README.md. The check under proof is the TB self-check `sva_rvalid_legal`
(`dv/auto_dv/tb/gen_bus_if.sv`, property p_rvalid_legal: `rvalid |-> outstanding > 0`, reported as
`uvm_report_error("sva_rvalid_legal", ...)`), knob `+gen_chk_sva_rvalid_legal` through
`chk_rvalid_legal_en` (set in `gen_agents_pkg::gen_bus_agent::build_phase` with the `+gen_chk_all` isolation
rule). The "design" it guards is the bus driver's stimulus legality, so the mutation is in the driver.
Executed 2026-09-03 (T-068); build `dv/auto_dv/work/tb-infra/out_t068_mut003` (vcs exit 0, 0 errors), module
`dv.auto_dv.gen_tb.gen_tests.gen_ut_bridge` (no image; the core fetches zeros and the bridge test passes
regardless of the DUT, so the ONLY collected failure can come from the named check), seed 1, opentitan.
Retained logs: `dv/auto_dv/evidence/gen_tdd_logs/mutations/mut003_*` (manifest `gen_tdd_logs/gen_manifest.md`).

    id: MUT-003
    file: dv/auto_dv/env/gen_agents_pkg.sv:277 (gen_bus_driver::run_phase, the grant of a pending request)
    original: vif.gnt = 1'b1;
    mutated:  vif.gnt = 1'b1; vif.rvalid = 1'b1;   // a response asserted in the grant cycle
    expected_detector: sva_rvalid_legal (uvm_error id sva_rvalid_legal; knob +gen_chk_sva_rvalid_legal)
    result: CAUGHT (2026-09-03): run mut003_isolated (+gen_chk_all=0 +gen_chk_sva_rvalid_legal=1, every other
      Zone A check disabled) -> 2 UVM_ERROR, both with id [sva_rvalid_legal], cocotb TESTS=1 PASS=1, flow verdict
      FAIL (gen_verdict.decide: assertion_failure at log line 31); run mut003_default (no knob) -> the same 2 errors.
    ablation_control: run mut003_ablation (+gen_chk_sva_rvalid_legal=0, mutation still applied) -> UVM_ERROR 0,
      the agent banner reads "sva_rvalid_legal disabled by knob", cocotb PASS, flow verdict PASS: the mutation
      SURVIVES with the detector disabled, so nothing else in the TB catches it.
    reverted: dv/auto_dv/env/gen_agents_pkg.sv restored from the pre-mutation copy; cmp reports identical
      (gen_mutations_driver_t068.log line "reverted: identical"; final line "sources identical to pre-mutation").

Attempt 1 (retained as `gen_mut003_attempt1_*`): the mutation `p.due = cycle` (respond in the grant cycle) did NOT
fire because the driver's response side runs before its request side within one falling edge, so the response
came one cycle after the grant, which is legal (0 errors in all three runs). It is kept as evidence that the
check is not trivially noisy; the recorded mutation above is the one that violates the rule.

Identifying log lines (gen_mut003_isolated_stdout.log, which carries the VCS assertion report, the UVM error and
the cocotb summary; the same UVM lines are in gen_mut003_isolated_sim.log):

```
"dv/auto_dv/tb/gen_bus_if.sv", 47: gen_tb_top.u_ibus_if.sva_rvalid_legal: started at 95000ps failed at 95000ps
	Offending '(outstanding > 0)'
UVM_ERROR @ 9500: reporter [sva_rvalid_legal] ibus: rvalid with no outstanding grant at cycle 5
UVM_ERROR @ 12500: reporter [sva_rvalid_legal] ibus: rvalid with no outstanding grant at cycle 8
[sva_rvalid_legal]     2
** TESTS=1 PASS=1 FAIL=0 SKIP=0
```
Ablation (gen_mut003_ablation_sim.log): `uvm_test_top.env.ibus_agent: sva_rvalid_legal disabled by knob`, `UVM_ERROR :    0`,
verdict.txt `verdict: PASS`.
