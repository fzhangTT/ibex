# TDD transcript: T-090 step-2b re-application (tb-infra, 2026-09-03)

Assignment: re-apply the parked step-2b work (dv/auto_dv/work/tb-infra/step2b_wip/README_step2b_wip.md) on top of
4c4b9b8 plus the T-102 follow-ups, with REGIME_SET_CONSUMED rendered, the irq/debug checkers on the export-era monitor and
the misc monitor's expected-alert feed; announce the non-compiling window to Runtime (12:22Z), fresh out dirs, canary at
the end, mutants out of tree. Everything below is on disk uncommitted until the Orchestrator's landing.

## 1. Red first

The two unit tests written before the agents existed, run on the 4c4b9b8 build (out_t102/close3) with the seed-7
riscv-dv image: gen_ut_irq FAIL (IRQ_SET "has no consumer yet", uvm_error GEN_CMD_DISPATCH) and gen_ut_dbg FAIL (DBG_REQ
likewise): gen_tdd_logs/step2b/gen_red_ut_irq_t090_*, gen_red_ut_dbg_t090_*.

## 2. What was re-applied and what changed against the parked copy

- gen_tb_knobs.yaml: a `regime_set_consumer` attribute on every knob_* entry (bus / irq / dbg / scrkey / none / program);
  the codegen validates it and renders `REGIME_SET_CONSUMED` and `KNOB_CONSUMER` (gen_knobs.py; gen_test_lib's
  CONSUMED_KNOBS now reads the constant, 14 knobs) and `gen_knob_regime_set_consumed(id)` / `gen_knob_consumer(id)`
  (gen_tb_pkg.sv); the codegen unit test checks all four. The dispatcher's apply_knob is a case over the rendered
  GEN_KNOB_ID_* guarded by that predicate (the parked prefix-string tests are gone); gen_bus_cfg::apply_knob takes the
  knob id. A REGIME_SET on a knob without a run-time consumer is a collected error.
- gen_agents_pkg.sv: gen_irq_evt, gen_irq_driver (IRQ_SET / IRQ_CLR / NMI_PULSE, hold policies, regime engine, ack
  release through gen_record_handler), gen_dbg_driver (DBG_REQ, hold policies, regime engine), MEM_ERR_ARM arming and
  `intg_bad` on the response (drives gen_bus_if.intg_corrupt for alert_bus), the key responder's run-time regime.
- gen_rvfi_pkg.sv: gen_model_state published on `ap_state` after every compared record (CSR addresses from ibex_pkg,
  mret/dret from the rendered encodings).
- gen_checkers_pkg.sv (was untracked): irq_pending / irq_entry / nmi_entry / irq_masked, dbg_entry / dbg_masked,
  alert_bus / alert_internal / data_tag_quiet / double_fault as parked, plus alert_minor against the RAM models'
  announcement queue `gen_tb_pkg::gen_icram_events` (no injection exists yet, so a pulse is a failure; the "missing
  pulse after an injection" half waits for the ECC hook) and the back-to-back debug entry rule below.
- gen_env_pkg.sv: dispatcher cases, checkers, connections, an irq/debug knobs banner line; gen_tb_top.sv: the three
  interfaces replace the tie-offs; gen_tb.f; gen_bus_if.sv. API documents: irq_agent, dbg_agent, irq_checker,
  misc_monitor, icache_ram_model, bridge, env_knobs, scoreboard.
- Not re-applied: the schedule generator's seed-drawn first phase lives in the Test Writer's gen_test_lib (told them);
  nmi_internal, crash_dump, core_busy, fetch_en checkers and the icache ECC injection hook are not built.

## 3. Build a (out_t090/a, compile clean on the first try) and the two findings

Green: boot_zc, lockstep_zc, lockstep_s7, bridge_zc, export_zc, gen_ut_dbg (2 entries, 0 mismatches, dbg_chk entries 2
bound failures 0), the four batch-1 tests (regenerated images) PASS (gen_tdd_logs/step2b/gen_a_*).
gen_ut_irq on the seed-7 image FAILED on its own assertion (fast3 not taken within 4000 cycles): the riscv-dv
gen_rand_smoke program never enables interrupts (mie and mstatus.MIE stay 0), so the raised line is correctly not taken
and the irq checker correctly expects nothing (gen_a_ut_irq_s7_noirqenable_t090). A directed program that enables every
implemented interrupt (mie written all-ones: no mask re-typed), sets MIE and points the vectored mtvec at a 32-entry table
of mrets was written (dv/auto_dv/stim/gen_directed/gen_irq_directed.S; tohost after 5000 loop iterations). On it two
comparator findings, both on the first interrupt-enabled program this TB ran:
- F1 (gen_a_ut_irq_dir_earlytake_t090): on an ORDINARY record the scoreboard injected the record's pre_mip into the model;
  with MIE set Spike took the pending enabled interrupt before stepping the instruction the DUT had retired (order 302:
  model trap cause 0x80000013, DUT retired c.addi; 168 mismatches). Rule now: on a record without intr the enabled
  pending bits are withheld (pre_mip & ~mie when M-mode MIE or U-mode); the entry comes with the next record's intr and
  its own pre_mip, as before.
- F2 (gen_a_lockstep_s7_dbg_storm_reentry_t090): a debug request held through dret re-enters debug at once; the
  scoreboard detected an entry only when the previous record was not in debug mode, so the re-entry record (pc DM_HALT,
  ext_debug_mode 1, previous record dret) was stepped as a normal instruction (order 1868, 421 mismatches). Rule now:
  entry when `!dbg_q || dret_q`; the same in gen_dbg_checker's entry count.
- The first lockstep run on the interrupt program timed out on tohost (gen_a_lockstep_irq_storm_notohost_t090): the
  program's first version never stored tohost; fixed in the program, not in the TB.

## 4. Builds b, c, d: the interrupt-entry rule and the model-state feed

- Build b (F1 and F2 fixed): gen_ut_irq on the directed program PASS (5 lines taken, 0 mismatches), the debug storm
  lock-step run PASS (105 entries, 0 mismatches), canary, bridge, export and the four tests PASS. The multi-line interrupt
  storm run (gen_b_lockstep_irq_storm_priority_t090) failed under isa_pc: the model took fast line 1 where the DUT took
  fast 10, 3, 12 ... Ibex and Spike agree on the priority (lowest fast index first; rtl/ibex_controller.sv:502-512 and
  Spike's ctz over the nonstandard bits), so the difference is the candidate SET.
- F3 (gen_c_irq_storm_premip_analysis_t090.txt): the entry record's pre_mip is sampled when the handler's first
  instruction is in ID (rtl/ibex_core.sv:1993), after the decision; under storm with the UNTIL_TAKEN policy (every held
  line released on any entry) the bit the DUT's vector names is often absent from that pre_mip, and other lines are
  present. Build c offered the model the vector's bit only when pre_mip carried it (still 650 misses); build d offers it
  unconditionally for causes 0..30: the DUT's vector is the record of the taken interrupt, Spike refuses an entry that is
  not enabled, and "the taken line was pending at the decision" plus the priority among pending lines are boundary rules
  for the irq checker (owed, not built). Build d: comparator clean on the storm run (UVM_ERROR 0); the lock-step test
  then timed out on tohost because the program stored it after 10000 retirements (gen_d_lockstep_irq_storm_notohost_t090);
  the program now stores after 1500 iterations.
- The first out-of-tree mutation batch (MB1..MB4 on gen_ut_boot with `+gen_chk_all=0 +gen_chk_<row>=1`) showed a design
  fault of the isolation form: the scoreboard did not build the model when the isa rows were off, so the irq/debug
  checkers never received a model state and irq_entry / dbg_entry could not fire (MB1, MB2 uncaught; MB3 alert_bus and
  MB4 irq_pending caught with clean ablations, they need no model state). Rule now: the model steps and publishes in
  every run; the knobs silence only the isa_* rows. Build e reruns everything (Section 5).

## 5. Build e (final tree) and the mutations

Fresh compile dv/auto_dv/work/tb-infra/out_t090/e (gen_compile_t090e.log, vcs exit 0); every run PASS, UVM_ERROR 0
(gen_tdd_logs/step2b/gen_e_*): boot_zc, lockstep_zc, lockstep_zc_isaoff (+gen_chk_all=0: the lock-step test green with
the isa rows silenced, the model stepping), lockstep_s7, bridge_zc, export_zc, gen_ut_irq on the interrupt program
(5 lines taken, 10 events), gen_ut_dbg (2 entries), lockstep_irq_storm (multi-line storm on the interrupt program:
3934 records, 919 interrupt entries in lock-step, irq_pending checked 27077 cycles, 0 mismatches), lockstep_irq_storm_s7
(the riscv-dv program keeps interrupts disabled: 0 entries, the checker expects none), lockstep_s7_dbg_storm (105 debug
entries in lock-step), the four batch-1 tests. Mutations MB1..MB4 caught with clean ablations, out of tree
(dv/auto_dv/mutations/gen_mut_step2b.md). The edit pass closes on this build; Runtime told.

## 6. Owed

- irq checker: the taken line pending at the DUT's decision cycle and the priority among pending lines (F3); nmi_internal;
  double_fault, irq_masked, dbg_masked mutations need programs with those events; the dbg checker's exc/dret/trigger rules.
- misc monitor: crash_dump, core_busy, fetch_en rules; alert_minor's "missing pulse" half with the icache ECC hook.
- The regime schedule's seed-drawn first phase (Test Writer's generator); ICACHE_ECC_ARM and COV_WITNESS consumers.
