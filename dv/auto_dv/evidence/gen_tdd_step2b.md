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

## 7. Follow-up landing: the checker holes (T-134, T-136, T-137) and the T-090 review rows

Owner: tb-infra (second instance of the day, 14:18Z; the first instance left the T-134 / T-136 / T-137 edits compiled but
unrun and stopped). Builds: dv/auto_dv/work/tb-infra/out_fu2/a (the inherited edits, unchanged), out_fu2/b and out_fu2/c
(the two T-136 corrections), out_fu2/d to out_fu2/h (the NMI classification of Section 7a; h is the landed tree; gen_tb_local.sh now stamps every compile and run header with a sha256 over the TB sources,
out_fu2/h = ba59fc4cbeebfd67). Retained as gen_tdd_logs/lockstep/gen_fu_{a,c}_*; drivers gen_fu_out_fu2_*_driver.log.

- T-134 (interrupt or debug entry inside a Zcmp sequence, rtl-arch R9 (c)): entries are handled before the fold and an
  entry with `in_seq` drops the partial micro-ops (`zcmp_splits`). Red on the pre-fix tree (gen_red_zcmp_irq_sparse_t134_*,
  gen_zcmp_irq_directed.S under `knob_irq_regime=sparse`: 425 misses, isa_insn and isa_rd union rows from the appended
  micro-ops); the storm variant starved (gen_red_zcmp_irq_storm_t134_starved_*: interrupts every ~20 cycles restart every
  sequence, the program never reaches tohost; kept as the reason for the sparse regime; retained as stdout excerpt and
  verdict only, the run has no run header because it ended in cocotb's timeout before the finish handshake). Green on out_fu2/h
  (gen_fu_h_green_zcmp_irq_sparse_*): 3708 retired, 1247 compared, 2461 folded, 5 entries whose first handler record is a
  cm.push micro-op, 4 splits, 0 mismatches. Mutation MB7 (a split leaves the partial sequence open) caught under isa_rd.
- T-137 (trap legitimacy, LOG-026a form): the model's fault is armed only for a word gen_bus_driver announced
  (`gen_bus_err_log`); otherwise the model decides. Green gen_fu_h_zcmp_trap_*: 278 records, 522 folded, 1 trap,
  faults_armed 1, faults_unannounced 0, bus_err_announced 1, 0 mismatches (the trapping-Zcmp green stays green, and its
  pre-fault stores are now compared as the union; both sides store the highest rlist register first). Mutation MB6 (one
  legal store reported as a trap) caught under isa_trap: `dut trapped, model retired 1`.
- T-136 (irq_entry cause rule) needed two corrections found by the storm run before it was sound:
  (1) the inherited rule (out_fu2/a, gen_fu_a_lockstep_irq_storm_*: 131 `line N pending throughout outranks it` and 36
  bound failures in 919 entries) called a line "pending throughout" when it was in the previous record's post_mip and the
  entry record's pre_mip, although the driver had released it (UNTIL_TAKEN releases every held line on any entry) and the
  regime re-raised it inside that window; and it kept the expectation of a line the driver itself released. Fix: lines the
  driver moved in the window make no priority claim (counted as `priority undecidable`), and a driver release voids the
  expectation of that line (`expectations released`).
  (2) out_fu2/b then showed 8 `taken line was not pending-and-enabled`: a line raised after the previous record's post_mip
  SAMPLE but before that record retired is in neither mip sample, and the checker had already dropped the raise event at
  the record. Fix: the driver-event window spans two records (`raised_prev` / `released_prev`). Builds b and c survive
  only as the verdict lines of gen_fu_out_fu2_{b,c}_driver.log; the message quoted here is transcribed from build b's
  sim.log, which was not retained (the same message is in MB5's retained catch log).
  Green on out_fu2/h (gen_fu_h_lockstep_irq_storm_*): 3934 records, 919 entries, cause checked 919, mismatches 0, priority
  undecidable 371, expectations released 415, bound failures 0, irq_pending 27077 cycles 0 mismatches; gen_fu_h_ut_irq_dir
  5 entries, 5 checked, 0 mismatches (1 undecidable). The 415 released expectations and 371 undecidable entries are the
  measured cost of UNTIL_TAKEN releasing untaken lines (Critic T-090 L-4, landing 2). Mutation MB5 (the entry record's
  vector shifted by one cause) caught under irq_entry with the referees inert.
- CM5-M-2 / CR5-M-2: the two refused codegen fixtures (knob without / with an unknown regime_set_consumer) are in the
  unit test (gen_fu_knobs_codegen_ut.log, 914 checks, 0 failures) and the retained run gen_fu_h_regime_refuse_zc_* (new
  test gen_ut_regime_refuse: REGIME_SET on knob_fetch_enable_regime, consumer none) has verdict FAIL on `GEN_CMD_DISPATCH
  REGIME_SET: no run-time consumer for knob_fetch_enable_regime (regime_set_consumer none)` while its pass marker printed.
- CM5-L-5 / CR5-L-2: gen_fu_h_alert_bus_intg_s7_* (`+gen_knob_dmem_intg_err_rate=frequent`, isolation of alert_bus):
  alert_bus hits=181 mismatches=0, the positive half of the rule. The Zc image cannot serve as the vehicle (its loads are
  corrupted before it reaches tohost: the first attempt on build a, whose sim.log was not retained and whose verdict line
  is in gen_fu_out_fu2_a_driver.log; a program limit, not a checker red). The same run showed
  54 internal-NMI entries (mcause 0xFFFFFFE0 from the integrity errors) counted as cause mismatches by the T-136 rule,
  which requires a pending NMI: internal NMIs are the not-yet-built `nmi_internal` rule's and are exempted from the
  pending check in out_fu2/h (Section 7a).
- CR5-L-3: double_fault ignores records in debug mode and trapping mrets; CR5-L-5: the debug checker keeps the first open
  request's bound; CM5-L-1 (ibex_pkg constants), CM5-L-3 (irq_event_mean / dbg_event_mean regime groups rendered from the
  yaml), CM5-L-4 (docstrings) as inherited; CR5-L-1: MB3 and MB4 re-run out of tree from the landed tree; CR5-L-8 /
  CM5-M-3: the four never-high rules got their one-line pin-inversion mutants MB8..MB11 and every mutant's exact edit is
  recorded (gen_mut_step2b.md); irq_masked, dbg_masked and nmi_entry stay declared-not-trusted (programs owed).
- R10 (breakpoint mtval): shim unit test section 8 written first and run against the un-fixed shim
  (gen_tdd_logs/isa_shim/gen_fu_red_ut_isa_shim_r10.log: 3 failures, mtval 0x80000080 / 0x80000084 = the pc), then the shim
  zeroes mtval on cause 3 and the comparator requires mepc == pc and mtval == 0 on cause-3 records
  (gen_fu_green_ut_isa_shim_r10.log: 175 OK); section 9 (an ecall inside debug mode sets no cpuctrlsts flag, CR6-L-4)
  passed at once, the rule was already built. R11 (odd jalr targets, B13): gen_jalr_odd_directed.S (register-odd,
  immediate-odd, both, c.jr; 20 iterations) red on out_fu2/a (gen_fu_a_red_jalr_odd_r11_v2_*: 80 isa_pc_next misses,
  every one `dut = model | 1`, nothing else), green on out_fu2/h with the mask (gen_fu_h_green_jalr_odd_r11_*:
  b13_odd_jalr=80, 0 mismatches).
- Every run of the set on out_fu2/h PASS (boot_zc canary, lockstep zc / zc_isaoff / s7, export zc / s7, ut_irq, ut_dbg,
  debug storm 105 entries, the four batch-1 tests with GEN_TEST_PASS) except regime_refuse (FAIL by design).
- T-144 (Orchestrator, 15:3xZ): the mask is behind the new bool plusarg `+gen_isa_pc_next_mask_b13` (default 1) so the
  expected-fail test of B13 can run the raw rule. Build out_fu2/j = h plus this knob (2 lines; sources sha256
  b961b6e9ce76b202) re-ran the whole set with identical verdicts (gen_fu_out_fu2_j_driver.log) and adds the pair
  gen_fu_j_green_jalr_odd_r11_* (knob 1: b13_odd_jalr 80, 0 misses) / gen_fu_j_red_jalr_odd_unmask_* (knob 0: 80 isa_pc_next
  misses, nothing else). j is the landed tree; the gen_fu_h_* runs are from h and differ from j only by the knob.

### 7a. Internal NMI entries and the cause rule (found by the alert_bus isolation run; builds d to h)

The integrity-error run (`+gen_knob_dmem_intg_err_rate=frequent` on the seed-7 image) takes 54 NMI-vector entries, and the
inherited T-136 rule counted every one as a cause mismatch (visible only in the GEN_IRQ_CHK report of the isolation run;
the knob silenced the error). Three findings on the way to the fix, one build each:
- d: the rule classified the entry from the MODEL's mcause, stale whenever the model did not take the entry (the shim has
  no NMI emulation; the 54 entries read as `cause is not an interrupt line`, the model's mcause being the program's earlier
  ecall). The scoreboard now publishes the cause the DUT's vector names (`entry_cause` in gen_model_state, 31 = NMI) and
  the checker classifies from it.
- e / f: with the vector, the 54 entries were accepted through the record's own `rvfi_ext_nmi_int` level, the DUT's
  self-report (no independent evidence); the pin is now the only pending-NMI evidence and gen_bus_driver announces every
  data-side integrity corruption (`gen_bus_err_log::intg_announced`, beside the T-137 bus-error announcements) as the only
  internal-NMI evidence. A fixed window of two or three records around the corruption accepted only 2 of 54 (f, g).
- g diagnostic (gen_fu_g_diag_intg_s7_export_* and gen_fu_g_diag_intg_s7_nmi_analysis.txt, the run exported): the 54 entries are strictly periodic, one every 82
  records at the same pc (the riscv-dv NMI handler is 82 records long and ends in mret), while the corrupted responses fall
  anywhere inside it (last corruption 13 to 336 cycles before the entry). RTL (rtl/ibex_controller.sv:391-430): the
  internal NMI is a single pending bit set by ANY data-response integrity error, cleared when an NMI entry is taken
  without an external NMI, and never taken inside NMI mode, so a corruption anywhere in the handler is taken right after
  the mret. The checker now mirrors that bit: an NMI-vector entry without a pin NMI is accepted when a corruption was
  announced since the last such entry consumed the announcements (up to the previous record), otherwise it is a phantom
  NMI (`NMI entry without a pending NMI pin or an injected integrity error since the last NMI entry`).
Build h (the landed tree) re-ran the whole set: the new un-silenced run gen_fu_h_intg_s7_irqchk_* (`+gen_chk_isa=0`, the
irq checker and the misc monitor on) PASS with 54 NMI entries accepted as internal on announced corruptions, cause
mismatches 0, alert_bus hits 181 / mismatches 0; the storm, ut_irq and every other run unchanged; MB5 re-caught (5,
ablation PASS). Consequence for the plan: a run injecting integrity errors is still consistency-only for the model (no NMI
emulation, isa rows silenced in such runs); the internal-NMI entry is now checked for legitimacy (an announced corruption
since the last entry) but not for its latency or its mcause / mtval read-back (nmi_internal, not built).

## 8. Landing 2a: taken-line release, NMI emulation, nmi_internal, the PMP-denial red, the misc stamp rule

Developed out of tree (a scratch copy of dv/auto_dv with the clone symlinked around it) while the shared tree waited for
the delta-1b commit, then applied under one announced window. Builds in the copy: l2/b (first full set), l2/c (the
NMI-pre-empted entry rule), l2/d (the GPR snapshot undo and the storm mean; sources sha256 156eb9357b79552e). Applied to the
shared tree under one window and rebuilt there as dv/auto_dv/work/tb-infra/out_fu2/l (the same sources sha256, 23 runs PASS,
regime_refuse FAIL by design, gen_fu_out_fu2_l_driver.log). Retained as gen_tdd_logs/lockstep/gen_fu_l2_* (the copy's runs,
reds included) and gen_fu_l_* (the landed tree's set).

- CR5-L-4 (UNTIL_TAKEN released every held line on any entry): the scoreboard writes the entry's vector cause to the
  bridge (`evt_irq_taken_cause`) and the irq driver releases only that line (31 = the nm line); the line-to-bit helpers moved
  to gen_agents_pkg. Red first on build out_fu2/j (gen_fu_j_red_ut_irq_two_entries_*): gen_ut_irq's two-line mask fast14 +
  fast0 requires two entries, the second was never taken (`entry 2 of fast14+fast0 not taken within 4000 cycles`); green
  in the copy (entry 1 at cycle 2738, entry 2 at 2749, 6 entries, 0 mismatches). Consequences measured on the storm run:
  `expectations released` 415 -> 0 in the multi-line storm (the with-NMI storm and rows_nmi still release, 47 and 1 on the
  landed build: an NMI pulse is a one-cycle hold released before its entry record exists; CR8 fu2a L-1); and at the old storm
  mean of 20 cycles the program livelocked (the retained l2/c red shows the timeout only; the entry and loop-record counts
  once quoted here had no retained log and are withdrawn, CR8 fu2a L-2), so `regime_windows.irq_event_mean.storm`
  is 100 (an entry every ~30 cycles; 573 entries in 3588 records, 0 mismatches). The irq checker's bound restarts at every
  entry: a lower-priority line legitimately waits while higher ones keep being taken (43 false bound failures on l2/b).
- Shim NMI emulation: unit test sections 10-12 (external entry with MIE / MPIE / MPP / mepc / mtval and the mstack restore
  on mret, internal entry with mtval, an NMI nested in a trap handler) red 16 failures (gen_fu_l2_ut_isa_shim_red_nmi.log)
  then green 204 OK (gen_fu_l2_ut_isa_shim_green_nmi.log). The scoreboard arms the entry from the record's vector and
  `ext_nmi` sample; the DPI argument `taken_cause` (unused) became `nmi_mtval`. Green: rows_nmi with the isa rows ON (1
  entry, 0 mismatches), the with-NMI storm (175 entries, 1 NMI, 0 mismatches; the l2/c figures once quoted here for the old mean had no retained log and are
  withdrawn, CR8 fu2a L-2), the integrity run with EVERY checker and isa row on (gen_fu_l2_intg_s7_allchk_*: 54 internal NMIs
  accepted, 0 cause mismatches, 0 nmi_internal bound failures, 83 suppressed loads mirrored, 0 mismatches). Two comparator
  rules the runs demanded: (1) an interrupt entry the NMI pre-empts before its handler retires anything has no record of
  its own (the NMI's mepc points into the handler), so the record after the NMI entry that sits at a vector address without
  `rvfi_intr` is that entry and the model takes it there (`nmi_preempted`; no retained run shows it above 0, landing 2c's six-seed with-NMI storm sweep included, so the rule
  stands on its derivation, CR8 fu2a L-2 / CM25-M-1; the miss count once quoted for the rule-less build is withdrawn with the
  other unretained figures); (2) a load whose response carried an integrity error retires with `rvfi_ext_rf_wr_suppress` and the DUT keeps the
  destination's old value, so the model's write is undone from a GPR snapshot taken before the step (decoding rd from the
  compressed form is what a first attempt got wrong: 3309 misses; 1560 before the rule).
- nmi_internal: an announced corruption (the announcement now carries the address, `note_intg(addr)` / `take_intg()`) must
  produce the internal NMI entry within GEN_NMI_INT_ENTRY_BOUND_RECORDS (4) records outside NMI mode; mutant MB12 (a
  corruption announced but not injected) fires it.
- PMP denial: gen_pmp_deny_directed.S green (20 traps, all model-decided, 0 mismatches, tohost 1; first on build
  out_fu2/j as gen_fu_j_pmp_deny_probe_*, then in the copy); the Critic's red P13 (the model loses pmpaddr0 after every
  step, so its PMP entry never covers the buffer): `isa_trap dut trapped, model retired 1` with the referees inert.
- CS2-L-4: gen_ut_export asserts the misc stamp relation (MISC_CURRENT_PC_LINE_OFFSET = 2: crash_dump_o.current_pc = pc_id,
  the boot jump spends one cycle in ID and one in WB; measured 2 on records 0..3 of the retained Zc export); mutant MUT-L
  (the misc writer reports the previous sample's value; the stamp-shift form was also caught by read()'s cycle rule and
  a negedge sample is not a defect, both recorded in gen_mut_export.md).

## 9. Landing 1c: the fu1 REQUEST-CHANGES fixes (entry state before the fold, one announcement one event, the data-fault rules)

Method: every edit was made in an out-of-tree copy of the tree at c6324ef (scratchpad l1c_root; the shared working tree
was not touched until the announced copy-in window). Builds, each `sources sha256` from its compile.log
(gen_fu_l1c_compile_{a,b,c,d,f}.log): a 4027975f37afdd17 (the report-time referees, the cycle-stamped announcement log
with the two-word take, the shim's debug-mode guard on the R10 mtval rule; the entry publish and the encoding fix NOT yet
applied: the red build), b 4e3a5bdf9118ebe2 (entry state published before the fold, `gen_insn_mem_access`, one entry per
word, the load/store double-fault offset), c deea1c7de46e9d69 (a first mtval rule through the fault range: wrong), d
c7156b73ce7463ab (the shim takes `tval`; the rule still "second word": wrong the other way), e 94bb3021a5c67974 (the
failing-transaction rule: green), f a056526d879ea458 (e plus the shim unit test's section 13 moved before its summary
line; sources of the simulator unchanged, every verdict identical to e: gen_fu_l1c_f_driver.log against
gen_fu_l1c_e_driver.log; e's compile and driver logs were retained with T-205 slice 2, gen_fu_l1c_compile_e.log and gen_fu_l1c_e_driver.log). The retained set gen_fu_l1c_* is build f: 28 runs, 25 PASS; the three FAILs are the two
starved zcirq storm runs below and regime_refuse_zc, which fails by design.

- CM18-H-1 / CR7 (LOG-025), entry state before the Zcmp fold: red first on build a, gen_fu_l1c_a_zcmp_irq_sparse_*
  (gen_zcmp_irq_directed.S, sparse, multi): `irq_entries_referee scoreboard stepped 15 interrupt entries, the irq checker
  saw 0`, the new referee in gen_env's report_phase against the scoreboard's `irq_entries` (the debug twin
  `dbg_entries_referee` compares `dbg_chk.entries` with `sb.dbg_entries`). Fix: `publish_state` on the folded micro-op
  that carried the entry, before the fold's return. Green on f, gen_fu_l1c_zcmp_irq_sparse_*: 1288 records, 2540 folded,
  irq_entries=15, GEN_IRQ_CHK `entries=15 cause checked=15 mismatches=0`, zcmp_splits=4; the referees ran in every run
  of the set (lockstep_s7_dbg_storm: 105 = 105 debug entries). Mutant RC1 (the publish removed) is caught by the referee
  alone (gen_mut_step2b.md, landing-1c batch). CR7-L-8: the same program under the irq storm (mean 100) and under the
  debug storm (mean 200), gen_fu_l1c_zcmp_irq_storm_* / gen_fu_l1c_zcmp_dbg_storm_*: both FAIL on `GEN_UT_LOCKSTEP: no
  tohost store (SimTimeoutError)`, the program does not reach tohost inside the test's 20000-cycle tohost window (irq
  storm: 5739 records, 474 entries, 1 split logged, last record at cycle 30743; debug storm: 4314 records, last record
  at cycle 33641); starved, not red: no UVM_ERROR, and no ISA compare report line because the run ends in cocotb's
  timeout before the finish handshake (the run header is present, the report is not). Under a sparse debug regime the program
  completes (gen_fu_l1c_zcmp_dbg_sparse_*: 1231 records, 2408 folded, 2 debug entries, 0 splits, 0 mismatches), so the
  debug-split path of T-134 (an entry that lands inside an open Zcmp sequence) is still unexercised by a completed run;
  the interrupt-split path is (4 splits in the sparse irq run, 1 in the starved storm run).
- CM18-M-1 / CR7 (LOG-026a) / CR7-M-1(b), one announcement is one event: `gen_bus_err_log` entries carry the injection
  cycle; `take(addr, bytes)` consumes the OLDEST entry of each word the access touches (both words of a spanning access,
  two announcements for two transactions) and reports which words were announced; the first form of this landing
  deleted every entry of a word and mis-armed the second of two injections on one address (found by build a's
  dmem_err_rate run before the reds above, corrected in b). Report-time referee `bus_err_leftover`: an entry older than
  GEN_BUS_ERR_DRAIN_CYCLES (64) never consumed by a trap record fails the run. Red: mutant RM-L1 (the driver announces an
  error it does not drive) `bus_err_leftover 55 announced data-bus errors never consumed by a trap record (announced 56,
  taken 0, drain window 64 cycles)` with every isa row silent (no DUT trap, no model fault). Green: gen_fu_l1c_dmem_err_dir_*
  (below) 61 announced / 61 taken / 0 leftover, gen_fu_l1c_zcmp_trap_* 1 / 1.
- The vehicle, gen_dmem_err_directed.S (new): a buffer written and read back with every LSU access shape (aligned word,
  word-spanning `sw`/`lw` at offset 6, half, byte, `c.sw`/`c.lw`), the handler accepts causes 5 and 7 only and retries the
  access by returning to it; one probe load inside the handler may itself fault (a nested fault before the mret, a double
  fault on `double_fault_seen_o`), the nested entry only retries the probe and the outer handler restores MPP = M before
  its mret (the first version left MPP = U after the nested mret, so the outer mret returned to U-mode and the fetch was
  PMP-denied on DUT and model alike: cause 1, a program bug both sides agreed on). Under `+gen_knob_dmem_err_rate=frequent`
  on f: 2466 records, 61 trap records = 61 injected errors (15 on 16-bit encodings, 46 on 32-bit), 61 armed, 0
  unannounced, 1 double fault expected and 1 pulse, 0 mismatches, tohost 1 (gen_fu_l1c_dmem_err_dir_*); without errors
  1317 records (gen_fu_l1c_dmem_err_dir_quiet_*). Three DUT-side rules came out of it, each pre-existing at HEAD (the
  same failures on the 2b copy's build): (a) ENCODINGS: T-137's arming tested `insn[6:0]` only, so a compressed store's
  fault was never armed; red gen_fu_l1c_a_dmem_err_rate_* (riscv-dv seed 7, frequent): `isa_trap dut trapped, model
  retired 1` at order 672, pc 800017ac, insn 0000d044 (c.sw); fix `gen_tb_pkg::gen_insn_mem_access` (both encodings, Zcb
  included); mutant RC2 (c.sw armed as a load). (b) DOUBLE-FAULT OFFSET: the same run raised 113 `double_fault ... without
  a double_fault_seen_o pulse at cycle N-1`: every pulse of a load/store fault sits at the record's own cycle (the error is
  seen in WB and saved from FLUSH one cycle later while the record leaves WB: rtl/ibex_controller.sv:827-845,
  rtl/ibex_core.sv:1888-1890), ID-stage exceptions keep the offset 1; constant GEN_LSU_TRAP_TO_RVFI_OFFSET = 0, mutant RC3.
  (c) MTVAL: Ibex writes the address of the FAILING bus transaction, `lsu_addr_last` (rtl/ibex_load_store_unit.sv:258),
  which advances to the second word of a spanning access only when the first transaction had no error (:520, :540); Spike's
  tval is the effective address. Two wrong rules were red before the right one: build c (the model faults from the second
  word on) gen_fu_l1c_c_red_dmem_err_dir_*: 9 `isa_rd rd model=x22/8000026e dut=x22/80000270` (the handler's `csrr mtval`,
  compared as any rd); build d (always the second word) gen_fu_l1c_d_red_dmem_err_dir_*: 8 `isa_rd rd model=x22/80000270
  dut=x22/8000026e` where the FIRST transaction had erred. Fix: `take()` says which words were announced, the scoreboard
  derives the tval (first word announced: the effective address; else the second word) and the shim writes it to mtval
  after the faulting step (`gen_isa_arm_fault(kind, addr, size, tval)`); shim unit test section 13 (spanning load, tval =
  the second word; an unchanged tval passes through; the same load retires unarmed) green in gen_fu_l1c_ut_isa_shim_green.log
  and red on mutant RS1 (the write removed): `step tval = the second word got 0x80000186 exp 0x80000188 FAIL`, `mtval CSR
  ...FAIL`, gen_fu_l1c_RS1_ut_isa_shim_red.log; RS1 in the simulator: the isa_rd catch above.
- The riscv-dv seed-7 program is not a vehicle for injected data faults (gen_fu_l1c_b_dmem_err_rate_*): its handler skips
  the faulting instruction, a later use of the never-loaded register reads address 0x24/0x25 (order 6072) where the TB
  memory returns zeros with a collected MEM_UNMAPPED error while Spike faults (cause 5): a program limit recorded in
  gen_component_api_scoreboard.md, not a checker red.
- CR7-L-5, the R10 mtval row: gen_ebreak_directed.S (new; 4-byte `ebreak` under `.option norvc`, the assembler had
  compressed the first version, `c.ebreak` on both alignments, the handler reads mcause / mtval / mepc into registers and
  steps mepc by the encoding length): gen_fu_l1c_ebreak_r10_*: 535 records, 30 traps = 30 breakpoints, 0 mismatches. The
  row is a CONSISTENCY compare: the model's mtval 0 is the shim's convention (unit test section 8), the DUT's value reaches
  the comparator through the handler's `csrr` as an rd value; the two agree, which is what the row states, not more.
- Mutations of this landing: gen_mut_step2b.md, section "Landing 1c batch": RC1, RC2, RC3, RS1, RM-L1 and the re-run of
  MB3, MB4, MB5, MB6, MB7 (gen_mut_export.md: MUT-I, MUT-J, MUT-K) on the final tree, each with its own build's
  sources sha256 (CM18-M-2).
- Corrections of records (CR7-L-2, L-4, CM19-L-1, CS3-D): this file's Section 7 (the build a / b / c provenance lines,
  the starved run's missing report), gen_mut_step2b.md MB5 (2 + 3 messages), gen_critic_response_tb_t090.md (gen_fu_j_*
  names, the two knobs left out of the checker-id row), gen_component_api_export_sink.md Sections 2 / 2a / 2b / 2c / 4 / 8
  as built, gen_rvfi_export_addendum.md (no absent source is accepted), gen_mut_export.md MUT-K :405.
- Not in this landing: the rows Runtime's testlist needs (dv/auto_dv/work/tb-infra/gen_t150_testlist_entries_v2.yaml:
  rows_nmi with every checker on, intent-only descriptions, the gen_ut_regime_refuse red fixture) are handed over as a
  file; tb-infra does not edit the testlist.

## 10. Landing 2b: the protocol SVA layer, COV_WITNESS (T-179), the misc mirror and drain rules, dbg_dret

Method as in Section 9: an out-of-tree copy of the shared tree after landing 1c (scratch l2b_root for the SVA layer's
re-basing and its mutants, then wit_root for everything else; the shared tree untouched until the announced copy-in).
Builds: l2b/a 68a36e6ac32db967 (the SVA layer re-applied on the 1c tree: 11 canary runs PASS, gen_fu_l2b_base_*), wit/a
ea8cfe1aa2865c30 (T-179 red), wit/b 8d5824cba05661e5 (a second red), wit/c 242f0558621c52da (T-179 green), wit/e
5ca9fd98c937c26f (the landed sources: 16 runs PASS, gen_fu_l2b_*).

- T-162, the protocol SVA layer: `gen_protocol_props.sv` (rtl-arch's draft id-for-id, 50 asserts, 20 covers, nine group
  knobs) bound into gen_dut_top by `gen_binds.sv`; three draft forms had to change to compile and mean what the table says
  (an implication inside a boolean conjunction rewritten as a boolean, `valid_drops` as `|->`, the store `fields_hold` as
  `(!data_we_o || $stable(data_wdata_o))`) and the split rows became covers (gen_component_api_binds.md). Mutants
  (gen_mut_step2b.md, landing 2b): MUT-M / MUT-N on the agents, RM1 / RM2 / RM3 on the RTL, every group knob's ablation PASS.
  INCIDENT: the first RM1..RM3 batch (17:35-17:37Z) mutated the SHARED clone's rtl/ibex_core.sv and rtl/ibex_load_store_unit.sv
  through a symlinked rtl copy (mut_l2b_final.log, kept as the record of it: its start/end sha lines differ); the files were
  restored from HEAD at 17:39:28Z (shas 88b8bf3907472f1d / 86e156efaf7ac46a), Runtime and the Orchestrator were told
  (intervention log), the driver now copies rtl for real and refuses a symlink, and RM1..RM3 were re-run from a private copy
  with identical counts and an unchanged source tree (mut_l2b_rm_rerun.log). Only the re-run is cited.
- T-179, COV_WITNESS (CG-WIT-001): red on wit/a, the command in the yaml and the covergroup package present but no
  dispatcher route: gen_ut_witness FAIL `command COV_WITNESS has no consumer yet` (gen_fu_l2b_a_ut_witness_*). Second red on
  wit/b after the route: `the first witness (TP-BIT-036) counts 2 distinct bins, expected 1` and a `wit_referee` error in the retained gen_fu_l2b_b_boot_zc_* run (in gen_fu_l2b_b_ut_witness_* the cocotb assertion
  failed first, so that log has no UVM_ERROR line; lockstep_zc and the foreign fixture showed the referee only in the driver
  log, CR-2B-L-3): an `int` cast of a real rounds to nearest, so the `+ 0.5` in the distinct-bin formula double-rounded (0 read as
  1, 1 as 2; gen_fu_l2b_b_ut_witness_*, gen_fu_l2b_b_boot_zc_*). Green on wit/c and e: gen_ut_witness counts 1, 1, 2
  (`GEN_WIT witnesses=3 distinct=2 covergroup=2`), gen_ut_witness with `+gen_fcov_en=0` PASS on the bookkeeping path,
  gen_ut_witness_foreign FAILS by design (`GEN_WITNESS_FOREIGN COV_WITNESS TP-BIT-036 (index 0) belongs to
  gen_bit_multicycle, issued by gen_bit_random`, covergroup 0, no referee). Codegen: the CSV loader's refusals (repeated bin,
  missing file) are fixtures of gen_ut_knobs_codegen.py, which also mutates the rendered include like every target
  (GEN_UT_KNOBS_CODEGEN PASS, 967 checks, gen_fu_l2b_ut_knobs_codegen.log). Mutant WM1 (the covergroup never sampled):
  caught by gen_ut_witness (the peek stays 0), ablation `+gen_fcov_en=0` PASS. Protocol note for the template (Test Writer):
  arg1 is the issuing test's group index (gen_component_api_fcov.md Section 7).
- Misc rules: `crash_dump` (the mepc / mtval mirrors against the model of record at every record; LATE and EARLY named and
  counted: dmem_err_dir 2466 checked / 54 late / 0 mismatches, the 54 being the load/store faults whose save edge is the
  record's own; ebreak_r10 6 early, the handler's `csrw mepc`; s7 debug storm 2000 / 0 / 0) and `fetch_en` (no record later
  than GEN_FETCH_EN_DRAIN_CYCLES = 64 after fetch_enable_i left On; gen_ut_fetch_en: 61 records by the end of the drain
  window and 61 after 256 more idle cycles, the same under long rvalid delays on the seed-7 program: 201 / 201). Mutants
  MB13 (exception_pc offset by 4: caught at order 1) and MB14 (the DUT's fetch_enable_i tied On: a record 68 cycles after
  the Off edge), ablations PASS.
- dbg_dret from the published state: the record after a dret outside debug has `pc_rdata == dpc` and `mode == dcsr.prv`
  of the dret's model state (37 returns checked in gen_fu_l2b_lockstep_s7_dbg_storm_*, 0 failures); mutant RM4 (dret resumes
  at dpc + 4, out-of-tree RTL from a private copy): 14 errors under `+gen_chk_all=0 +gen_chk_dbg_dret=1`, ablation PASS.
- Rulings carried: the storm mean 100 and its livelock reason are in the yaml and gen_component_api_irq_agent.md (2a); the
  three landing-2a comparator conventions are rows with RTL lines in gen_component_api_scoreboard.md (LOG-037c).
- Landed sources: the shared tree was compiled twice after the copy-in, out_l2b (sources sha256 5ca9fd98c937c26f, equal to
  wit/e; gen_fu_l2b_shared_*) and, after three review lows were folded in as comment / literal changes only (CM33-L-1: the
  stale take() comment removed; CM33-L-2: CAUSE_LOAD_ACCESS in shim unit test section 13; CM25-L-1: the two false comments
  at the interrupt-entry arming rewritten), out_l2b_final (sources sha256 f7289c6b83086cd2; gen_fu_l2b_final_*: boot_zc,
  lockstep_zc, ut_witness, ut_fetch_en, dmem_err_dir, lockstep_s7_dbg_storm PASS, codegen --check up to date, shim unit test
  PASS). MUT-M, MUT-N and RM1..RM3 were built from the l2b/a sources (68a36e6ac32db967, 17:35-17:42Z) and WM1 from the wit_root copy at
  17:48Z, all before wit/e's compile (17:53Z); the three edits between those sources and wit/e do not enter any rule (CR-2B-L-2).
  The `source tree untouched` line of an out-of-tree batch is the sha256 (first 16 hex) of the SHARED tree's
  dv/auto_dv/env/gen_rvfi_pkg.sv (TB-side batches) or of rtl/ibex_core.sv, rtl/ibex_load_store_unit.sv and
  dv/auto_dv/env/gen_agents_pkg.sv (RTL batches), read after the runs: it shows the tree was not written, and the mutated
  file's identity is the `applied to ... original sha256` line of the same batch.
- Scope note (LOG-046, T-205): the misc rules and dbg_dret were re-scoped to landing 2c while this landing was already built
  and proven; they land here as built rather than being held back, so that the next windows can go to the covergroups.

## 11. Landing 2c: the suppressed-write gate (T-183), the irq checker's per-line and end-of-run rules, the NMI window, the SVA fixes, the shim's stack

Builds (wit_root, out of tree): u b7b1b3fe53bc65ec (first green with the gate, the local `intr_now` flag, the two-record NMI window,
the debug suspension, the decidability row, the SVA fixes), v cf73fd8a625e89a8 (the per-line expectation release), w e287c87e3fdf8a97
(final: the shim's stack push and unit test section 12b). Retained as gen_fu_l7_* (gen_manifest.md rows; the per-file source list of
build w is gen_fu_l7_sources_sha256_w.txt, its sha256 being the build id). Every rule below names its red and its green.

- T-183 gate (gen_rvfi_pkg.sv): `rvfi_ext_rf_wr_suppress` is accepted only when `gen_bus_err_log::take_intg_word(mem_addr)` finds an
  announced corruption of the load's word and the record reports no destination write; otherwise an `isa_rd` miss; a record inside a Zcmp
  sequence (`is_seq`) bypasses the gate and is judged by the sequence's union compare (tb_l10 L-4). Reds MUT-SUP,
  MUT-SUPB (the flag on one clean load of the Zc / Zcb images) and MUT-SUP2 (the announced address off by 0x100), ablations PASS
  (gen_mut_step2b.md). Green gen_fu_l7_intg_s7_allchk_*: 83 suppressed loads accepted, 54 internal NMIs, 0 mismatches, every checker
  and isa row on (the retained run headers of this run, boot_zc and lockstep_zc carry no +gen_chk_* plusarg, and every chk_* knob defaults
  to 1 in gen_tb_knobs.yaml except chk_sva_b8, LOG-067: that is the evidence for the claim, A2c-6). The s7 image cannot carry the clean-load red: its first 6000 records retire no load
  (gen_fu_l7_s7_trace_opcode_summary.txt).
- irq checker (gen_checkers_pkg.sv): an entry clears only the taken line of each expectation and restarts the others' bound; a line
  raised, enabled and still held at report that was never taken is an error at report. Reds MUT-NT (31 per-line bound errors; the same
  mutant PASSED both runs before the per-line rule) and MUT-NT2 (the end-of-run rule, simulator seed 3: `still held and enabled at the
  end of the run, never taken`), ablations PASS. Greens gen_fu_l7_lockstep_irq_storm_* (573 entries, 0 mismatches), _irq_storm_nmi_*,
  _ut_irq_dir_*, _rows_nmi_irqp_*. The `misc irq_entry order,cause,decidable` row: 573 rows in the storm, 1 in rows_nmi
  (gen_fu_l7_*_export_irq_entry_rows.txt). The first build with the row FATALed at time 0 in every run (`row misc irq_entry emitted by
  an unregistered writer`) until the checker registered it in end_of_elaboration_phase: the sink's T-141 rule catching a missing
  registration, recorded as an incidental red of that rule. That FATAL run was not retained: narrated only (A2c-6).
- nmi_internal: records in debug mode are not counted; the bound is TB-side (4). Red MUT-NIB (the bound at 0: 54 errors, one per
  announcement), ablation PASS; the bound-1 form (batch_tb7, build 16b938ccd6021cc1) PASSED both runs, but no retained line states that
  build's bound, so the exactly-1-record latency is the author's unretained observation (A2c-5). Greens gen_fu_l7_lockstep_s7_dbg_storm_*,
  _intg_s7_allchk_*.
- NMI classification and the pre-empt rule (gen_rvfi_pkg.sv): the scoreboard subscribes to the irq driver's events (`imp_irq`) and
  classifies external from the pin sample or a raise of the NM line in the current or previous record's window; the pre-empt rule
  works on a local `intr_now`, the monitor's transaction untouched. Greens gen_fu_l7_lockstep_irq_storm_nmi_* and
  gen_fu_l7_storm_nmi_s2..s6_* (six simulator seeds; only seed 1 took an NMI entry, nmi=1, seeds 2-6 report nmi=0: one NMI entry in
  the whole sweep, A2c-4); every one reports `nmi_preempted=0`, so the pre-empt rule has NO red and no
  observed case: it stands on its derivation until a directed raise-then-NMI timing sequence exists (not built).
- Protocol SVAs (gen_protocol_props.sv): widths from `TagSizeECC` / `LineSizeECC`, `sva_alert_minor_window` on `ICACHE_ECC_WINDOW`
  (GEN_ICACHE_ECC_WINDOW 1 -> 2 with the reason), knob names from `PLUSARG_CHK_SVA_*` / `PLUSARG_CHK_ALL`, dcsr's prv through
  `GEN_DCSR_PRV_BIT_LOW/HIGH`, the header on the tracked anchors, the two split rows covers. Greens boot_zc and lockstep_zc with all
  nine groups on (gen_fu_l7_boot_zc_*, _lockstep_zc_*); reds MS-ICRAM (397), MS-IRQ (2), MS-DBG (2), MS-ALERT (2851), each with its
  group knob's ablation PASS (gen_mut_step2b.md; the ibex_top.sv form of MS-ALERT was inert and is recorded, not counted).
- Shim (gen_isa_shim.cc): the mstatus shifts derived from the MSTATUS_* masks and the NMI causes named once in gen_isa_shim_map.h;
  the recoverable-NMI stack pushed on every exception entry outside debug mode. Unit test section 12b (a trap nested inside the NMI
  handler) red on an intermediate 2c shim (sha256 46324b7522a4dda3, between bd75f16 and cbadb7f: gen_fu_l7_ut_isa_shim_red_nested.log,
  6 failures) and, re-run for A2c-2, on the committed pre-2c shim bd75f16 (76293bbdd49351b1) with the committed 2c test
  (991603011f5b4f6f): the same 6 failures (gen_fu_l12_ut_isa_shim_red_12b_bd75f16.log), green on the landing shim
  (gen_fu_l7_ut_isa_shim.log, stamped with date, shim and test sha256, image). DUT-level greens: the with-NMI storm and the integrity
  run above.
- Witness covergroup `option.weight = 0` (CR-2B-L-1): greens gen_fu_l7_ut_witness_*, _ut_witness_nofcov_*; the referee's red WM2
  (the bookkeeping mutant; the referee the only catcher, the unit test's own asserts PASS).
- cm.popret under dummy instructions (B8): gen_zcmp_dummy_popret_directed.S red by design, 9408 errors, first `Zcmp union: x2
  model=800003b0 dut=800003d0` at order 38 (gen_fu_l7_lockstep_zcmp_dummy_popret_*): the DUT's popret sequence under
  `dummy_instr_en` diverges from the fold; the dummy-in-expansion assertion waits for the C10 ruling (probe bind with a knob, or text
  only) and is NOT built; the program is retained as its vehicle.
- Provenance: the mutants were built from the wit_root copy beside build u or v; a copy time is retained nowhere, so "beside" is an
  inference from the header shas (b7b1b3fe53bc65ec = u, cf73fd8a625e89a8 = v, or the mutated TB's own sha) and the catch-run times
  (MS-ICRAM, MS-IRQ, MS-DBG, MUT-SUP2, MUT-NT, WM2 at 21:29-21:53Z; MUT-SUP 21:57Z, MUT-SUPB 21:58Z, MUT-NIB 22:06Z and MUT-NT2 22:10Z,
  the last two after build w's driver start, tb_l10 L-3), not all before w (e287c87e3fdf8a97); the edits between those builds (the per-line release, the shim's stack push,
  unit test 12b, documents) enter none of the mutated rules, and each row carries its own build sha. Regressions on w: gen_fu_l7_lockstep_muldiv_nofcov_*,
  _ut_isa_cov_zc_*, _ut_fetch_en_*, all PASS; codegen `--check` up to date for the knobs and the fcov renderer.
- Not built: the NMI-pre-empt red (above), the B8 assertion (ruling), an icram ECC injection (CM43-M-1's red impossible without it),
  the in-run mcounteren_writable command (WP-10, dv-lead).

## 12. T-235: the model's counter CSRs (Runtime's holders, tb-infra's minstret proxy and inhibit rule)

Build z e845572967179ff0 (wit_root; sources list gen_fu_l9_sources_sha256_z.txt). Runtime's part R taken as delivered (their hashes
gen_fu_l9_gen_t235_hashes.txt): gen_isa_shim_counters.h / .cc (mcountinhibit with Ibex's mask, zero holders for mhpmcounter13..31 and
mhpmevent13..31) and unit-test section 14 (23 rows). Mine: the minstret proxy (Spike's counter minus what Ibex did not count), the U-mode
instret aliases through Spike's counter proxies, the retirement derivation fixed for minstret writes, the retirement-gap DPI fed by the
scoreboard, unit-test section 15 (24 rows then, 31 since the tb_l9 rows), gen_component_api_isa_shim.md's counter section.
- Red first: sections 14 and 15 on the pre-integration shim, 8 failures (gen_fu_l9_ut_isa_shim_red_t235.log: the mask rows, a step
  under IR = 1 synthesized as a trap, the writer counted, the h-write corner, the TB write eating the next increment); green 271 OK
  (gen_fu_l9_ut_isa_shim.log).
- Measurement (the Orchestrator's item): the Test Writer's gen_pmc_ctrl seed-1 image (provenance gen_fu_l9_pmc_s1_program_provenance.txt),
  which no build could follow (every record under IR = 1 an isa_trap mismatch). First form of the inhibit rule (the IR state as the
  step began, Spike's reading): no isa_trap left (the reds' excerpts hold no isa_trap row), but 60 error rows, 47 isa_rd and 13 isa_mem
  consequences, 45 of the isa_rd rows DUT = model + 1 and 2 of them + 2 (gen_fu_l12_lockstep_pmc_s1_on_red_errors.txt, every UVM_ERROR
  line of the run; the per-row classification by the insn field, csrr minstret / instret reads against their arithmetic consequences,
  in gen_fu_l12_lockstep_pmc_s1_on_red_isa_rd_classes.txt), all after an IR clear and none under IR = 1; the reds' build y is identified
  by gen_fu_l12_compile_y.log and gen_fu_l12_sources_sha256_y.txt (e493e548da55b9ce) (retained red gen_fu_l9_lockstep_pmc_s1_on_red_*,
  _off_red_*). The
  export trace decided the rule: an instruction retires under the inhibit state it leaves behind, so the csrw that sets IR is itself not
  counted and the csrw that clears IR is (the Test Writer's docstring semantics; rtl/ibex_cs_registers.sv:1643 with the write landing
  before the writer's own retirement). With that rule build z runs the image to its end: 8000 records (pin on) / 8001 (pin off), 0 mismatches
  (gen_fu_l9_lockstep_pmc_s1_on_*, _off_*; those two runs followed the z driver's regression, so they are not in gen_fu_l9_z_driver.log), and every earlier lock-step run stays green (gen_fu_l9_lockstep_s7_*, _csrwarl_*,
  _intg_s7_allchk_*, _irq_storm_*, _s7_dbg_storm_*, _zcmp_mv_*, _muldiv_*, boot_zc, lockstep_zc, ut_isa_cov_zc, ut_witness).
- Mutant MUT-CNT (gen_mut_step2b.md): the inhibit accounting removed; 91 isa_rd misses on the same image, ablation `+gen_chk_isa_rd=0`
  PASS.
- Not modelled, stated in the shim document: the hazard variant of the high-word corner; the DUT's dummy instructions (counters knob).
- Consequence for the Test Writer: gen_pmc_ctrl's dependency sentence ("gen_isa_compare cannot follow this program yet") no longer holds
  on this shim; the group can be re-verified and its testlist entry staged.

## 13. Landing 9: the cross-model rows of landings 2c and 7, and the B8 probe (LOG-067)

Build aa 4bc32b82a3b03340 (wit_root; sources list gen_fu_l10_sources_sha256_aa.txt). Greens: boot_zc, lockstep_zc, lockstep_s7,
intg_s7_allchk, the two storms, the debug storm, ut_isa_cov_zc, ut_witness, lockstep_zcmp_mv (gen_fu_l10_*). The knobs and fcov codegen
--check were up to date on the copy against the plan the copy carried (its base commit, before the v3d..v3h touches; that output was not
retained); at 329902f the committed renderer reports STALE against the moved plan (CM132, tb_l10), and the Slice A state is up to date again
against plan v3i (gen_fu_l12_codegen_check.log).
- The B8 probe (T-225; rtl-arch's gen_b8_rtl_facts.md section 6; the C10 ruling LOG-067 = a probe bind behind a knob): tb/gen_b8_probe.sv
  bound into ibex_if_stage by gen_binds.sv, assertion `sva_b8_dummy_in_expansion` ((if_id_pipe_reg_we && insert_dummy_instr) |-> the
  Zcmp FSM's state, rlist and sp_offset unchanged), knob `+gen_chk_sva_b8` default 0. Red: the two dummy programs with the knob on,
  gen_zcmp_dummy_directed.S 35 firings (gen_fu_l10_b8_zcmp_dummy_on_*: 62 UVM_ERROR lines, of them 35 sva_b8_dummy_in_expansion; each
  firing is one VCS failure line and one UVM_ERROR line) and gen_zcmp_dummy_popret_directed.S 59 firings (gen_fu_l10_b8_zcmp_dummy_popret_on_*:
  13251 UVM_ERROR lines, of them 59 the assertion's; the knob-on run ran longer than the knob-off run's 9408 comparator rows); with the
  knob off the same programs show 0 firings (gen_fu_l10_lockstep_zcmp_dummy_*, _popret_*; those controls ran with +gen_ut_boot_retire=10 and an
  export file, not the knob-on runs' plusargs, tb_l10 L-1). Matched controls re-run on build ai with the knob-on plusargs (+gen_ut_boot_retire=1000,
  no export) and the knob off: gen_fu_l12_b8_zcmp_dummy_off_1000_* 27 UVM_ERROR lines and gen_fu_l12_b8_zcmp_dummy_popret_off_1000_* 13192, 0
  firings each, equal to the knob-on runs' non-B8 counts (62 - 35 and 13251 - 59): the knob adds exactly the assertion's lines. No green with a true antecedent exists: a dummy-enabled
  program without Zcmp is not in the stimulus set, so the assertion's silence there is vacuous and stated as such. The knob stays off by
  default because the assertion fails on the DUT's B8 defect itself, not on a TB fault. LOG-067's remaining conditions: the flow's
  refusal of a measured entry that sets the knob is built by Runtime at fa9ba21 (the testlist loader refuses a measured entry whose plusargs
  turn the knob on, and measured dispatch is refused when a canary build records it on or absent; LOG-076); the knob is named chk_sva_b8 after the per-assertion
  family, the name ruled to stand (LOG-076); the probe-register row and the SVA layer header's C10-exception note are CM132-M-2 items
  (the row in this landing, the header comment with the next source-changing landing).
- The landing-2c review rows (gen_critic_response_fu2a.md, the table "cross-model review of landing 2c"): the gate looks up both words
  of a load spanning two bus words (the second announcement sits at +4), announcements enter the gate's list for loads only, the irq
  checker's two never-taken rules are silent in NMI mode and the summary prints `never taken=`, the dbg_dret message uses the dcsr
  constants, the alert_minor window is a range over a lookup shift register with the parameter default 2, and the record corrections
  (MUT-NT2's build sha, per-mutant provenance, the export-rows excerpt header, the CM43-L-3 file name). Greens: the runs above, the
  integrity run with 83 suppressed loads through the widened gate. No red for the spanning second-half case: the retained programs
  have no corrupted second half of a spanning load (the integrity run's 83 are whole-word), stated rather than staged.
- The landing-7 review rows (gen_critic_response_fcov.md): see gen_tdd_fcov.md Section 7 (the exclusion counts only the self-test's
  own miss, every counted group refereed, the unit test's own red on the FM4 build, the record corrections).

### 12.1 The Critic's tb_l9 rows on T-235 (rows CR-9), fixed in the Slice A landing

The T-235 red gen_fu_l9_ut_isa_shim_red_t235.log ran with an intermediate test file (sha256 36128fb905fc4f4e, not kept), not the
committed test (c30369dd144e93fa): the committed test does not compile against the pre-integration shim (`gen_isa_set_retire_gap`
undeclared, gen_fu_l12_ut_isa_shim_red_t235_as_committed_compile.log), so the 24 T-235 rows have no red as committed (CM123-L-8);
the 7 rows added by tb_l9 have theirs (gen_fu_l12_ut_isa_shim_red_tbl9.log: the landing's test on the committed T-235 shim, 2 failures).

- M-1: the minstret CSR objects know their half from the address (`gen_minstret_half_csr_t` for CSR_MINSTRET and CSR_MINSTRETH over one
  64-bit view, `gen_minstret_proxy_t::write_half`), so a minstreth write of the value it already holds takes the high-word corner; new
  row "csrw minstreth of its current value at gap 1: the low word still loses the increment due".
- M-2: the gap-1 corners are skipped when the previous record was itself a minstret / minstreth writer (neither side counted it:
  Spike's written flag, rtl/ibex_id_stage.sv:1213-1220); new rows for the back-to-back pair `csrw minstret, x0; csrw minstreth, x0`
  at gap 1 (both words 0, the nop after counts one).
- Red first: the new rows on the committed T-235 shim (34559ec691021abd) FAIL, 2 failures (gen_fu_l12_ut_isa_shim_red_tbl9.log; the diff
  of that shim against the landing's is gen_fu_l12_ut_isa_shim_red_vs_landing.diff); green 278 OK (gen_fu_l12_ut_isa_shim.log). The
  gen_pmc_ctrl image stays at 0 mismatches on the landing build (the two verdict lines of gen_fu_l12_ai_driver.log, :15-16; the ai runs were not retained as files, CR-11 L-2; the b2 runs are gen_fu_l13_lockstep_pmc_s1_on_* / _off_*).
- L-1: the build-y reds are identified above; the unit-test red of Section 12 was HEAD's gen_isa_shim.cc of 22:39Z (1b51fec23d35a589) plus
  an inert gap setter, its test file the landing's; the diff idiom is retained from this landing on.
- L-2: figures corrected above (31 rows, 8000 / 8001, the classified error list, minstret's inhibit line is rtl/ibex_cs_registers.sv:1643,
  mcycle's :1627 was cited before; the pmc greens after the driver's end line).
- L-3: `g_ir_at_step` removed (the rule reads the holder after the step).
- L-4: the mutation driver's `source tree untouched` line now hashes the mutated file's copy in the source tree and each batch retains the
  mutant diff (gen_fu_l12_MUTCNT_mutant.diff from MUT-CNT's saved original; FM12..FM15 from their batches).
- L-5: gen_fu_l9_gen_t235_README.md's "236 rows OK" is Runtime's unretained claim about their out-of-tree run; the committed test's own
  count is the retained one (247 rows through section 14 at the T-235 commit, 278 now).
- I-1: the writer comment cites Ibex's exclusion (rtl/ibex_id_stage.sv:1213-1220) beside Spike's written flag.

## 14. Landing 11: the re-review landing (landings 9 and 10 gates), the tag-RAM ECC injection hook, the source fixes and their reds

Build b2 (l11_root, a detached archive of 4140581 with the landing's edits; the per-file list gen_fu_l13_sources_sha256_b2.txt), build b2r
(b2 with gen_protocol_props.sv's window slice as landing 9 committed it, gen_fu_l13_sources_sha256_b2r.txt), the four mutant builds on b2's
sources (their lists gen_fu_l13_<mutant>_sources_sha256.txt). Every retained header of this landing names one of these builds; the reds of the
landing-10 code ran on b0 / b0h (the landing-10 sources with the hook; gen_fu_l13_sources_sha256_b0h.txt).

- The tag-RAM ECC injection hook (CM132-H-1's precondition). The knob knob_icache_ecc_err_rate had no consumer (gen_icache_ram.sv's header
  said the hooks "arrive with the icram checkers in step 2"); no run before this landing had alert_minor_o high: two lockstep runs of the
  icache program on the landing-10 build with the knob at frequent and rare showed alert_minor hits 0 and sva_alert_minor_seen 0 matches
  (wit/ai/red_h1_icen_ecc_*, driver lines only), so the yaml constant's "landing 2b measured 1 or 2" had no run behind it and now says so.
  As built: the tag RAM models flip one bit of a lookup read at the regime's rate_per_mille and announce it (cycle, way, index, qualified) through
  gen_icram_events; the misc monitor's first half stands (a pulse needs an injection within GEN_ICACHE_ECC_WINDOW; the injections of one lookup
  cycle share one pulse) and the second half is new (a qualified injection owes a pulse: the cache enabled per the scoreboard's cpuctrlsts
  tracking and no invalidation-sweep tag write within GEN_ICACHE_ECC_GRACE_CYCLES, because a lookup made while disabled or invalidating reads
  the tag RAM unchecked, rtl/ibex_icache.sv:266, and the TB learns both states late). Program gen_icache_ecc_directed.S (enable once, a
  cross-line loop). Measured on b2 / b2r, rate frequent: 870 injections (682 qualified), 436 pulses, 0 mismatches, 0 missing, every pulse one
  cycle after its lookup read (the summary's latency histogram 0 / 436 / 0); rate rare with slow imem: 32 / 32 / 16 / 0 / 0.
- CM132-H-1 red and green. b2r (the landing-9 slice shifted with the register, `[ICACHE_ECC_WINDOW-1:1]`: latencies 2..N, never 1; the literal
  landing-9 form `[ICACHE_ECC_WINDOW:1]` has its red in the b0h run, 4 window failures beside the first hook's 2 missing pulses,
  gen_fu_l13_b0h_red_h1_ecc_slow_rare_x_*): sva_alert_minor_window FAILS 215 times in the frequent run (the assertion's own
  count: about half of the 436 pulses; the other 221 passed the old slice through neighbouring lookups) and 9 times in the rare run
  (gen_fu_l13_red_h1_ecc_freq_*, gen_fu_l13_red_h1_ecc_slow_rare_*); the same with every check off but the alert SVA group
  FAILS (gen_fu_l13_catch_h1_ecc_freq_*) and with every check off PASSES (gen_fu_l13_ablate_h1_ecc_freq_*). b2 ([ICACHE_ECC_WINDOW-1:0]):
  0 failures on the same runs (gen_fu_l13_green_h1_*). Why the first attempts stayed green: the fetch stream looks up nearly every cycle,
  so the neighbouring lookups set lookup_hist[2:1] when a pulse came one cycle after its own lookup; the dedicated program's loop and the
  slow-imem runs isolate lookups.
- Finding L11-F3 (the hook's first form). Two injections of one lookup produced no pulse (b0h, rate rare, slow imem: gen_fu_l13_b0h_red_h1_ecc_slow_rare_x_*);
  the FSDB of that run shows the lookup actual, IC1 valid and ecc_err_ic1 low: the decoder saw a valid codeword. The flip mask was a
  block-local variable with an initializer inside the always block (static in SystemVerilog), so flipped bits accumulated across injections
  and an even-weight pattern can land on another valid codeword. The landing's RAM model flips exactly one bit per injection; the b2 / b2r
  runs report 0 missing pulses.
- The misc monitor's two halves proven. MUT-ICE-ANN (the RAM corrupts without announcing): 436 `alert_minor_o high ... without an announced
  ECC injection`, ablation PASS. MUT-ICE-MISS (the RAM announces without corrupting): 862 `alert_minor_o missing within 2 cycles`, ablation
  PASS (gen_fu_l13_ICEANN_* / gen_fu_l13_ICEMISS_*; gen_mut_step2b.md rows).
- CM132-M-1. An expired expectation in NMI mode or debug mode is neither judged nor deleted (its bound restarts when the mask lifts).
  Red: gen_ut_irq_nmi_long on gen_nmi_long_directed.S (a 41-record NMI handler; the bridge raises NM, then the external line 6 records into
  the handler) with MUT-NT3 (irq_external withheld from the first NMI on) on the landing-10 checker and irq_entry alone: PASS, the silence
  (gen_fu_l13_red_m1_nt3_nmi_raise_old_entryonly_*; the storm form was caught by the irq_pending pin rule and by re-raises, so it proved
  nothing). On b2: catch FAIL `lines 00004 raised ... not taken within 17 records`, ablation PASS (gen_fu_l13_NT3b_*); unmutated: entries 2
  (gen_fu_l13_green_m1_nmi_raise_*); the long-NMI program under the with-NMI storm green (gen_fu_l13_green_m1_nmi_long_storm_*).
- CM132-L-4 and finding L11-F2. The gate consumes both words of a spanning load (`a0`, `a1`). Program gen_intg_span_directed.S (a
  misaligned lw over gen_span_buf+0 / +4, then a clean c.lw of +4) under gen_ut_intg_span, which arms two integrity corruptions on the buffer
  through MEM_ERR_ARM. Red: MUT-SUP3 (the flag set and the rd fields cleared on the clean c.lw, order 18) on the landing-10 gate with the isa
  rows: PASS with two suppressions accepted (gen_fu_l13_red_l4_sup3_old_isa_*); on b2: catch FAIL `asserted without an announced integrity
  corruption for 800002e4 (order=18 ... rd=x0)`, ablation PASS (gen_fu_l13_SUP3b_*). The same test on the landing-10 scoreboard raised 21
  crash_dump errors (gen_fu_l13_red_l4_intg_span_old_crash_dump_*): the DUT's internal-NMI mtval is the LSU's last address, the misaligned
  address itself when the first half is hit (rtl/ibex_controller.sv:416, rtl/ibex_load_store_unit.sv:258), the model's was the announced word;
  the suppressed record's own address now replaces the pending corruption's when its first word was announced; green on b2 with crash_dump
  mismatches 0 (gen_fu_l13_green_l4_intg_span_*).
- CM123-L-1 and finding L11-F1. The gap update sits at the top of write() for every record. gen_minstret_zcmp_directed.S (csrw minstreth at
  gap 1 after cm.push / cm.pop) is green on the landing-10 code too (gen_fu_l13_red_l1_minstret_zcmp_*): the fold reached the update. The
  draft-B path did not, and gen_minstret_draftb_directed.S (grevi then csrw minstreth) read model 3 / DUT 4 on the first minstret read:
  the model never counted the draft-B retirement, since that path never steps it (gen_fu_l13_red_l1_minstret_draftb_*). Fix: the path calls
  gen_isa_count_retire(1) (Spike's counter bumped unless IR inhibits); green on b2 (gen_fu_l13_green_l1_minstret_draftb_*).
- CM123-L-2, L-3 and tb_l11 L-5 (the shim). The carry corner is decided on Ibex's own low word; no corner and no writer mark for a TB write.
  Unit-test rows (section 15): the four new rows FAIL on the committed (73ff075) shim and pass on the landing's (gen_fu_l13_ut_isa_shim_red_73ff075.log:
  4 failures; gen_fu_l13_ut_isa_shim.log: 293 OK, stamped with the landing shim 59672952dc4fbfc8).
- The renderer rule (Slice-A-1): a bin the line's ignore clause names leaves the plan-versus-CSV comparison and renders nothing; unit-test case
  red on the landing-10 renderer, green now (gen_fu_l13_ut_fcov_codegen.log); the rendered include is unchanged (no rendered group has such a
  bin) and --check is up to date against plan v3k.
- The sampler (CM138): icache_en tracked from 0 by op, trap records sample redirect_other (the DV Lead's ruling), GEN_CSR_CPUCTRLSTS and
  cfg.hart_id, the mcounteren set / clear result; the ten history-narrating comments rewritten (CR-8 L-8).
- Regression on b2: 17 regression runs, 11 proof runs on fresh vdbs (the ten Slice A manifests and slice2c, every check PASS; slice5a /
  slice5a2 gain the trap record's redirect_other bin: 30 bins; the fetch-enabled boot run as gen_ut_boot_fe1 with one plusarg value,
  CM138-m-5) and 8 new greens: 36 PASS, 0 FAIL (gen_fu_l13_*; the pmc runs retained as files, CR-11 L-2). FM12-FM15 re-run against the
  landing sources (gen_fu_l13_FM*_*): every catch FAILS on the hidden bin, every ablation check PASSES, both stamped with the manifest's md5,
  the report and the build; the canary hashes gen_fcov_pkg.sv (51315dd2b793c8a2) and the mutant diffs are retained (CM138-Ma-1 / Ma-2,
  tb_l11 M-1 / M-2).
- Not retained and narrated: the first icen runs at frequent / rare on build ai (driver lines only); the b1 dry run (the shim changed once
  more after it, for tb_l11 L-5, so every run repeated on b2).
- Identity of the landed sources. Build b2 compiled the landing's compiled sources before gen_ut_boot_fe1.py existed (the fetch-enabled boot
  module, written for CM138-m-5 and loaded by cocotb at run time, never compiled into the simv); the landed tree's per-file list therefore
  differs from b2's by that one file, and its own sha256 is 7a083655868cb9c9 (gen_fu_l13_sources_sha256_shared_out_l12.txt, the shared-tree
  canary compile gen_fu_l13_compile_shared_out_l12.log). The seven canary runs on that build are retained as gen_fu_l13_shared_*: boot_zc,
  lockstep_zc, ut_isa_cov_zc, intg_s7_allchk (83 suppressed loads, 54 internal NMIs), the ECC program at rate frequent (436 pulses, 0 window
  failures, 0 missing), gen_ut_intg_span and gen_ut_irq_nmi_long, all PASS. Every other retained header of this landing names b2, b2r or a
  mutant build whose list equals b2's in every file but the mutated one.

## 15. Landing 13: the deferred CM148 items (the grace rule, the shim comments, the store half of the raw-address rule)

Build sb3 (sb_root = the committed landing 12 at ba3799b plus Slice B and these items; sources 98518617fecfcf64, the per-file list
gen_fu_l15_sources_sha256_sb3.txt).
- CM148-L-2, the grace rule. The misc monitor's ECC qualification opened GEN_ICACHE_ECC_GRACE_CYCLES after every all-ways tag write, which is
  the invalidation sweep's write pattern but also an ECC correction's (rtl/ibex_icache.sv:591 invalidates every way after a tag error). Now a
  sweep write is recognised by its pattern: an all-ways write at index 0, or at the index after the previous all-ways write one cycle later
  (INVAL_CACHE writes consecutive indices on consecutive cycles, rtl/ibex_icache.sv:1241-1246); the tag RAM model passes its index. Measured on
  gen_icache_ecc_directed.S at rate frequent, seed 1, the same injections on both builds (870 judged, the latency histogram 0 / 436 / 0): the
  landing-12 build qualified 682 (gen_fu_l15_b12x_green_h1_ecc_freq_*), the landing build 866 (gen_fu_l15_green_h1_ecc_freq_*), 0 missing pulses
  on both, so the 184 injections the old grace excused after corrections all pulsed as the rule requires; the four still unqualified sit in
  the reset sweep's grace. A correction landing on index 0 is the one misclassification left (1 in IC_NUM_LINES), stated in the API doc.
- CM148-L-5, the store half. A store response's corruption raises the internal NMI with mtval = the LSU's last address as a load's does; the
  model replaced the announced word by the record's own address for suppressed loads only. gen_ut_intg_store (gen_intg_store_directed.S: a
  misaligned sw whose first half's response is corrupted, the handler reading mtval): red on the landing-12 build, isa_rd on the handler's
  csrr (model x15 = 800002d0, the word; DUT 800002d2, the store's address) and the crash_dump rows for the same values
  (gen_fu_l15_red_intg_store_b12x_*, 21 UVM_ERROR lines); green on the landing build with the rule extended to store records
  (gen_fu_l15_intg_store_*: one interrupt entry, 31 records consumed, 0 mismatches).
- CM148-L-3 and L-4: the g_minstret_written comment on its own line; the review ids out of the three gen_ut_isa_shim.cc comments, its
  section-9 title, the four directed-program headers and the two landing-11 test docstrings. No behaviour change; the shim unit test is
  unchanged (293 rows).
- The sampler unit test on this build: 129 cases, 0 failures (gen_fu_l15_ut_isa_cov_zc_*; the 45 Slice B rows are gen_tdd_fcov.md Section 10's).
- Rules and retention the Critic's tb_l12 asked for (rows CR-12): a firing count is the assertion's own line count (the "of them" field of an
  excerpt header or the UVM summary), never a grep over the token; the window's upper edge is declared, not measured (every retained injection run
  puts every pulse at latency 1: histograms 0 / 436 / 0, 0 / 16 / 0, 0 / 4 / 0; the knob table says so); the red builds of landing 11 keep their
  identity here where it still exists: b0 (the landing-10 code plus the first hook) and b0h (the first hook's second form) with their per-file lists
  and compile logs (gen_fu_l15_sources_sha256_b0.txt, _b0h_, gen_fu_l15_compile_b0.log, _b0h_), b2r likewise (gen_fu_l15_sources_sha256_b2r.txt,
  gen_fu_l15_compile_b2r.log) with the MUT-WIN mutation as compiled (gen_fu_l15_MUT-WIN_mutant.diff); the mutant reds nt3_b0 and sup3c_b0 were
  built in copies since rebuilt for their landing-11 forms, so their lists are gone, and the FSDB behind L11-F3 was not retained: both stay
  narrated. Every proof and re-check log of this landing carries a stamp line; the five red checks against the landing-12 build got theirs in landing 14 (re-taken against the same reports).

## 16. Landing 14: WP-12, the data-RAM ECC injection hook, the hit judgement (forms a and b), two-bit flips, the far program

Built as w16 (sources de983a8e68063c27) and re-proved in landing 15 on build w18 (sources cff50f81508de1a9, the per-file list
gen_fu_l16_sources_sha256_w18.txt), whose 13 evidence runs give summary lines byte-identical to w16's on all 13. Every retained file this section
cites now names w18 or a w18 mutant build (build_sources_sha256 in the header; each mutant build differs from w18 in the mutated file only, checked
per file and recorded in Section 17), with no exception: the runs of the two intermediate builds and of the earlier trace copy, whose per-file lists
were never captured, are retired and their facts re-proved as named mutations and as one trace session on w18 (Section 17).
- The hook as built (gen_icache_ram.sv, IsTag = 0). A data RAM read is corrupted at the rate of knob_icache_data_ecc_err_rate (rare / frequent,
  regime_windows.rate_per_mille; default none) with one or, under knob_icache_ecc_bits = two, two distinct positions inside one 39-bit beat (the tag
  path takes the bits knob too); every instance draws from its own xorshift stream (finding WP12-F1 below). The announcement (kind inject_data)
  carries cycle, way, index, the beat, the bit count, qualified, every way's stored valid bit and tag at the read, and whether a flipped bit rose in
  the data word the DUT sees. The stored words are tweaked (SecureIbex = 1): gen_icram_events keeps a tag shadow of every tag write (the reset sweep
  and the ECC-correction writes included) and un-tweaks by index (rtl/ibex_icache.sv:388-403: the index at bit offsets 0 and 14 of the 28-bit word); a
  data flip needs no un-tweak (a flipped bit stays flipped through the XOR), and the duplicate-copy visibility (below) is computed on the un-tweaked
  data word, stored bit XOR the line-address tweak of the way's own tag (:329-348). The data word written beside an invalidation or correction tag
  write lands under the zero tweak in a way that write invalidates (CM169-L-2), so no judgement ever un-tweaks it; the API doc states it.
- The judge (gen_checkers_pkg.sv misc monitor, the data half of the alert_minor row). The DUT checks data ECC only on the way the lookup hit
  (rtl/ibex_icache.sv:499-511, :585), and the hit is not decidable from the TB's stored tags alone (lookup_addr_ic1 is internal). Two forms derive the
  lookup tag: (a) the P9 read-only probe of lookup_addr_ic1 (gen_ic_lookup_probe.sv bound in gen_binds.sv, knob probe_ic_lookup, default off and
  debug_only under LOG-079, so the P6 refusal keeps it out of measured runs; the tag of cycle c + 1 belongs to the RAM read at c) and (b) the
  retirement stream (the measured-run form): the first retirement after the read whose pc line index is the injected index reveals the tag through its
  pc, provided it and every retirement between are sequential flow; with a control-flow discontinuity among them the association is ambiguous and the
  injection unjudged (no failure, no cp_alert_pulses sample), as it is when no such retirement arrives within GEN_ICACHE_RETIRE_WINDOW = 64 cycles (a
  squashed speculative lookup) or the run ends first (reported as pending). Verdicts: the injected way is the hit way of a qualified lookup = owes one
  pulse within GEN_ICACHE_ECC_WINDOW; another way, a miss or an invalid way = owes none and excuses none (an invalid way is decided without any tag:
  the always-on rule); the line in several ways at once (finding WP12-F2) = owes a pulse only if a flipped bit rose. Pulse attribution (plan v3x,
  CM169-L-1 / CM170 as built): a pulse's window is the GEN_ICACHE_ECC_WINDOW cycles before it, the read's own cycle excluded (the check is in IC1; a
  later injection in the pulse's cycle must not take the credit; the shifted-latency observation behind this was made during development on a build
  whose per-file list was not retained, so it stands as a development note carrying no evidentiary weight); a pulse whose window holds a valid-way data injection without a verdict yet is held until every injection in its
  window has one (every data pulse is, the probe on or off: the probe's tag for the pulse's cycle is published in that cycle, so the verdict comes
  with the judgement a few cycles later), then credited to the nearest injection in the window that owes it and has none yet (a qualified tag
  injection, or a data injection judged the hit way), else to the nearest one that excuses it (an unqualified tag injection, or a data injection left
  unjudged): the tag half's attribution is extended the same way, so an unqualified injection in a grace window never takes a qualified one's pulse
  (the DV Lead's corner, not seen in any run); the injections of one cycle share the credit (a tag and a data injection of one lookup share one pulse,
  as tag injections did); a none-owed verdict never consumes a pulse, and a pulse fails the run only when nothing in its window owes or excuses it. An
  owed injection's missing verdict waits while a held pulse lies in its window; at the end of the run the injections still without a verdict are
  unjudged (reported as pending), the held pulses attributed and the owed ones closed. The ambiguity interval is GEN_ICACHE_ECC_WINDOW of the
  injection's read (CM169-I-1: the window inside which its pulse would be attributed). Both verdicts and the hit way are written back into the
  announcement; the summary counts judged / hit_way / other_or_invalid_way (other valid way) / unjudged (ambiguous, pending at the end) / missing /
  other_way_pulses / duplicate copies visible and masked, and the a/b agreement where both judged, with (b)'s retirement latency.
- Measured on w18, program gen_icache_ecc_directed.S (one 2 KB tag region), seed 1, rate frequent, probe on (gen_fu_l16_ecc_data_freq_*): 904 data
  injections judged, 494 the hit way, 410 another or an invalid way, 0 unjudged (350 ambiguous for form (b), which form (a) decided), 0 missing, 0
  pulses nobody owed, 494 pulses, 0 mismatches; duplicate copies 16 visible / 4 masked; forms a and b both judged 554 and agreed on all 554, (b)'s
  latency 7..16. The same with the probe off (gen_fu_l16_ecc_data_freq_noprobe_*): (b) judges 148 hit-way and 406 other-way injections, 350 unjudged,
  0 missing, 0 unowed pulses, 494 pulses. Two bits per flip, probe on (gen_fu_l16_ecc_data_two_*): 899 judged, 436 / 463, 0 / 0 errors, 434 pulses
  (two owed injections of one cycle shared a pulse twice), a/b 583 / 583, duplicates 20 / 2. Tag and data at once, probe on
  (gen_fu_l16_ecc_both_freq_*): 925 tag injections (912 qualified, 0 missing) and 902 data injections (445 hit way), 1309 pulses, 0 mismatches, a/b
  575 / 575, duplicates 19 / 14. Rate rare (gen_fu_l16_ecc_data_rare_*): 27 judged, 14 / 13, 14 pulses, a/b 20 / 20. The tag half on this build:
  gen_fu_l16_ecc_tag_freq_probe_* and gen_fu_l16_green_h1_ecc_freq_* (925 judged, 915 qualified, 906 pulses, latencies 0 / 906 / 0, the same numbers
  with and without the probe), gen_fu_l16_ecc_tag_two_* (940 / 931 / 916, two bits per flip). Sampler self-test 131 cases (gen_fu_l16_ut_isa_cov_zc_*,
  the two CM165-L-3 rows added), the plain icache-enable run green (gen_fu_l16_lockstep_icache_en_*).
- The far program gen_icache_ecc_far_directed.S (new): two bodies placed exactly 2 KB apart (body_a 0x80001000, body_b 0x80001800; the loop at
  0x80000800), so indices 0..6 hold the bodies' lines under two tags and indices 0..3 a third (the loop's): after the first iteration an aliased index
  holds a valid line in both ways and a data injection on either way meets a real hit-way decision, which the one-region program never produces (its
  other-way verdicts are all invalid ways or duplicate copies: other valid way 0). Measured (gen_fu_l16_ecc_far_data_freq_*): 619 judged, 180 hit way,
  438 other (165 a valid way that lost the compare), 1 unjudged (the injection pending when the run ended), 0 / 0 errors, 180 pulses; a/b both 174,
  agree 174; probe off (gen_fu_l16_ecc_far_data_noprobe_*): 27 / 147 judged, 445 unjudged (the jump every 14 instructions makes most associations
  ambiguous), 0 / 0; tag and data (gen_fu_l16_ecc_far_both_freq_*): 598 tag injections (583 qualified, 0 missing), 613 data (172 hit way, 2 pending at
  the end), 742 pulses, a/b 185 / 185.
- Alignment measured, and now retained. On the one-region program the probe's tag is 00100000 in 20448 of 20509 cycles and 00000000 in the other 61
  (before the first lookup), counted by python from the trace session's own lookup lines and retained as
  gen_fu_l16_trace17_lookup_tag_histogram.txt (landing 15; the figure rested on no retained file before, CR-15 M-1). At every one of the 904
  injections the tag of cycle c + 2 equals the tag of c + 1, so the ALIGN mutation (the tag of the wrong cycle) is silent there, and the
  (a)/(b) agreement cannot separate the cycles either. The far program changes the tag at every jump; there the ALIGN mutation is caught (below) and
  forms (a) and (b) still agree on every double-judged injection, so the probe's value at c + 1 is the tag the DUT compared for the read at c (the
  binds API doc states both).
- Form (b)'s mis-association, found by the far program and fixed. The rule of the w11 build ("the first retirement after the read whose index matches,
  provided no discontinuity retired between") accepted a jump retiring just after the read as the revealing retirement: the loop's `jal body_a` / `jal
  body_b` (index 1, the loop's tag) retire one or two cycles after the target's line-1 read and share its index, so (b) read the loop's tag for a body
  lookup. That was found during development on a build whose per-file list was not retained, so the rule is proved instead by two named mutations of it
  on w18: RETSEQ (the sequential-flow requirement dropped) and RETIDX (any retirement matched whatever its line index), both caught probe-off on the
  far program with every other check disabled (Section 17). The rule requires the revealing retirement itself to be sequential flow (a jump, trap,
  interrupt entry or return retiring after the read may have been fetched before it); on w18 the disagreements are 0 on every run and (b)'s minimum
  latency is 4 on the far program.
- Red first and the mutants (gen_mut_step2b.md, the landing-14 section; every ablation PASS with 0 errors): RED0 (red first): 988 errors, 494 `without
  an announced ECC injection`, 494 `missing within`; MUT-ICE-DATA-ANN (the pulse-without-injection half): 494 errors, 494 `without an announced ECC
  injection`; MUT-ICE-DATA-MISS (the missing-pulse half): 483 errors, 483 `missing within`; MUT-ICE-WAY (the hit judgement excuses the wrong way): 830
  errors, 453 `without an announced ECC injection`, 377 `missing within`; MUT-BITS (two bits per flip): 930 errors, 930 `missing within`; MUT-ALIGN
  (the alignment of the probe): 13 errors, 13 `every ECC injection in its window was judged not to owe it` (the true hit way judged from the wrong
  cycle's tag). The counts are the checker's own UVM_ERROR totals from the retained verdicts.
- Finding WP12-F1 (a TB defect, fixed here). Both RAM instances of a kind drew their injection decisions and positions from the shared $urandom
  stream, so every injection came as a pair (both ways, the same cycle, the same position) and the DATAWAY mutation (the announcement names the other
  way) was invisible. Each instance now seeds its own xorshift stream from $urandom and its way. The tag-half numbers of landings 11 and 13 were
  pair-counted (870 injections for 436 pulses); on this build the same program gives 925 injections, 915 qualified, 906 pulses (9 cycles in which both
  ways injected by chance). TP-SEC-001's quoted numbers are the pair-counted ones.
- Finding WP12-F2 (a DUT corner, for the plan owner and rtl-arch). After an ECC-correction refetch the DUT allocated a second copy of a line that was
  still valid in the other way: both ways held the same tag valid at one index until both were invalidated together
  (gen_fu_l16_trace17_duplicate_copies.log: every announced injection whose line was valid in both ways under the same stored tag, 20 of them at
  indices 26 and 27, from the landing-15 trace session on w18; the earlier evidence filtered one hard-coded index on a build with no retained list). The hit-data mux ORs the matching ways' un-tweaked words
  (rtl/ibex_icache.sv:507-513), so a flip that clears a data bit in one copy is restored by the other (no error, the fetched word correct) and a flip
  that sets one is visible: the judge owes a pulse for the visible case only, and the summary counts both (16 / 4 on ecc_data_freq). The correction
  after a data error invalidates the tag_match ways (:591-592), so the duplicate lives until then.
- Finding WP12-F3 (a TB defect, twice; the L11-F3 pattern). A block-local variable with an initializer inside an always block is static and keeps its
  first value: the flip mask (build w7: every data flip at one position, 593 duplicate cases "visible") and the line address of the un-tweak (build
  w9: the visibility computed with one stale tweak, 12 false unowed pulses). Both are now declared without an initializer and assigned per read; the
  RAM model's header says why.
- Items folded. CM165 L-1 (the self / gt37 bins hit), L-2 (sb2 named sb3), L-3 (hx_rs_field for c.lui, the two sampler rows) and I-1 (the have_last
  guard) with the CR-14 rows (gen_tdd_fcov.md Section 10, gen_critic_response_fcov.md); CM169 L-1, L-2 and I-1 as built (above); the five landing-13
  red checks re-stamped against their b12x reports (Section 15). The P9 row of gen_probe_register.md is APPROVED under LOG-079; Q-019 (a read-only
  probe feeding a checker in a measured run) is the owner's, so the probe-on entries stay unmeasured and the noprobe entries are the
  measured-run candidates. Those seven entries are staged as dv/auto_dv/work/tb-infra/gen_l14_testlist_entries.yaml, a gitignored work file handed to
  the Runtime Manager and parked under the landing-14 gate; they reach the tree only through the Runtime Manager's testlist merge, so no committed
  path holds them yet (CR-15 L-6). CG-IC-006's sampler is not in this landing (the IC components follow WP-8).
- Retention (gen_fu_l16_*), as landing 15 leaves it: the w18 build identity (compile log and per-file list), the thirteen evidence runs (header,
  verdict, excerpt each, the summary line kept whole), the twelve mutants (compile log, per-file list, diff, catch and ablation runs each), the trace
  session (compile log, per-file list, its run, the tag histogram and the duplicate-copy filter), the two program ties and the three driver logs of
  this pass. Section 17 lists what was retired.

## 17. Landing 15: the landing-14 review rows, the measured-run judge's own reds, and retention that keeps its figures

Build w18 (wp12_root on the committed HEAD plus this landing's edits; sources cff50f81508de1a9, per-file list
gen_fu_l16_sources_sha256_w18.txt, compile log gen_fu_l16_compile_w18.log). Every retained file of this landing names w18 or a w18 mutant build, and
each mutant build was checked to differ from w18 in exactly the file its mutation names, by comparing per-file sha256 lists: 13 roots, 13 matches, 0
mismatches. This landing answers the cross-model rows CM173 and the Critic's CR-15 on landing 14; both verdicts named the same two substantive gaps.
- Source changes, and the proof they change no behaviour. The un-tweak operands and the probe's default width now come from ibex_pkg
  (gen_icache_ram.sv: IC_TAG_SIZE-2, IC_INDEX_W-1, IC_LINE_W; gen_ic_lookup_probe.sv: ADDR_W - IC_INDEX_HI - 1, the form gen_binds.sv already passed),
  so a geometry change cannot silently mis-address them (CM173 m-1, CR-15 L-5). Under this build configuration each derived form equals the literal it
  replaces (20, 7, 3 and 21), and the 13 evidence runs give GEN_MISC summary lines byte-identical to w16's on all 13, so the change is measured to be
  behaviour-preserving rather than argued to be. The C10 note in gen_protocol_props.sv now names the P9 probe beside B8, stating that P9 carries no
  property, which keeps the B8 claim true (CR-15 L-4). The knob table's hit-way sentence now states the condition unconditionally and names both tag
  sources, since the monitor derives the hit way in both forms and only the source of the lookup tag differs; gen_tb_pkg.sv and gen_knobs.py are
  re-rendered from it and both codegen --check pass.
- Retention now keeps the figures the record quotes (CM173 M-1, CR-15 M-1). The excerpt tool capped every kept line at 400 characters while the
  GEN_MISC summary line is 713, so it was cut before the duplicate-copy, a/b agreement and latency fields: the record's proof that the measured-run
  form agrees with the probe rested on no retained file. The summary line is now kept whole and every other line still capped, the header says so, and
  every figure in Section 16 and below is re-derived from the retained line by a checked-in reader (scratchpad/gen_l15_figures.py) which fails on a
  field it cannot parse or an identity that does not hold. Two identities it enforces: the field the log calls judged is the processed total, so
  hit_way + other_or_invalid_way + unjudged must equal it; and with the probe off, ambiguous + pending must equal unjudged, while with the probe on
  unjudged equals the end-of-run pending count and ambiguous is form (b)'s own statistic measured beside form (a)'s verdict.
- Per-check-site error counts are retained (CR-15 L-1). The kind splits the mutant rows quote were counted from twelve-line samples and never
  retained. Every excerpt header now carries the count per reporting site with a digit-normalised sample of its message, so the splits are the
  checker's own totals over the whole run. The four sites of this checker: gen_checkers_pkg.sv(660) a pulse with no announced injection at all,
  (664) a pulse whose window held only injections judged not to owe it, (682) a tag-RAM injection's pulse missing, (687) a data-RAM injection's pulse
  missing.
- The measured-run form now has reds of its own (CM173 M-2, CR-15 M-2). Every landing-14 data mutant ran with the probe on, where form (a) decides, and
  the one tag-only mutant cannot cover the data judgement, so the judge a measured entry actually uses had no mutation it alone caught. Twelve mutants
  on w18, every catch failing through uvm_error under +gen_chk_all=0 +gen_chk_alert_minor=1 and every ablation passing with 0 errors:

| mutation | program, probe | catch errors | per site | ablation |
|---|---|---|---|---|
| DATAMISS (announced, not corrupted) | one-region, OFF | 150 | 687=150 | PASS 0 |
| DATAMISS | far, OFF | 21 | 687=21 | PASS 0 |
| DATAWAY (announced on the other way) | one-region, OFF | 557 | 660=453, 687=104 | PASS 0 |
| DATAWAY | far, OFF | 49 | 660=1, 664=26, 687=22 | PASS 0 |
| RETSEQ (form (b) without its sequential-flow requirement) | far, OFF | 71 | 664=42, 687=29 | PASS 0 |
| RETIDX (form (b) matching any retirement, whatever its index) | far, OFF | 22 | 664=10, 687=12 | PASS 0 |
| RED0 (the monitor before the data half) | one-region, on | 988 | 660=494, 687=494 | PASS 0 |
| DATAANN (the injection not announced) | one-region, on | 494 | 660=494 | PASS 0 |
| DATAMISS | one-region, on | 483 | 687=483 | PASS 0 |
| DATAWAY | one-region, on | 830 | 660=453, 687=377 | PASS 0 |
| BITS (the second flip on the first position) | one-region, on | 930 | 682=930 | PASS 0 |
| ALIGN (the probe's tag from the wrong cycle) | far, on | 13 | 664=13 | PASS 0 |

  The six landing-14 mutants reproduce their w16 counts exactly on w18 (988, 494, 483, 830, 930, 13), which is further evidence that the source changes
  above alter nothing. RETSEQ and RETIDX are mutations of form (b)'s own rule rather than of the RAM model, so they are the reds the Critic asked for:
  with the probe off, nothing but the retirement stream can decide the hit way, and breaking either half of that rule fails the run.
- Form (b)'s reach, stated as the checker's power (CR-15 L-3). With the probe off, of the announced valid-way injections the retirement stream decides
  a verdict for 554 of 904 on the one-region program (61.3 percent) and 174 of 619 on the far program (28.1 percent), the rest unjudged because a
  control-flow discontinuity makes the association ambiguous; the far program's jump every 14 instructions is why its reach is lower. The
  safety-relevant fraction is narrower: of the injections that actually owed a pulse, taken as form (a)'s hit-way count on the probe-on run of the same
  program, form (b) identifies 148 of 494 (30.0 percent) and 27 of 180 (15.0 percent). Every unjudged injection excuses a pulse, so on control-flow
  dense code a missing pulse would not fail the run, and a measured run's verdict must be read with that. Cross-check on the derivation: the population
  form (b) decides with the probe off equals the a/b both-judged count of the probe-on run of the same program, 554 and 174 on the two programs. The
  API document carries the figure per program; raising it is what Q-019 would decide, since a probe-on measured run would let form (a) judge.
- The trace session (CR-15 L-2, M-1). One session on w18 with only the TRACE displays applied, its own compile log, per-file list and driver log, so the
  earlier complaint that the driver log described a different session cannot recur. TRACE2's anchors no longer exist in the rebuilt judge and TRACE3
  hard-codes one index; TRACE's own injection lines carry both ways' valid bits and stored tags, so the evidence is index-general without them. It
  produced the alignment histogram above and the duplicate-copy filter: 20 announced injections whose line was valid in both ways under the same tag,
  at indices 26 and 27, which equals the ecc_data_freq run's 16 visible plus 4 masked duplicate copies, two independent artifacts agreeing.
- Retired, because their builds cannot be identified (CR-15 L-2). Twenty-one retained files are removed with their manifest rows: the two runs of the
  first intermediate build, the one run of the second, the nine files of the earlier trace copy, the driver log of the first, and the two identity files
  of the superseded landing build. Their headers carry a 16-hex build digest and no per-file list, their build trees no longer exist, and their source
  states were never committed, so the lists cannot be reconstructed; a digest is not invertible. Every fact they carried is re-proved above on w18. The
  deletion list is dv/auto_dv/work/tb-infra/gen_landing15_deletes.txt.
- The seventh ablation and the trace run's errors (CR-15 L-4). The landing-14 mutant table listed six mutants while seven ablations were retained, the
  seventh belonging to the trace copy, whose catch run carried ten errors from its pre-fix sources with no row explaining them. The trace session is no
  longer a mutant with a catch and an ablation: it is one green run (0 errors) whose purpose is the two figures above, so the count matches the table.
- Rows folded: CM173 M-1, M-2, m-1, m-2, m-3, m-4; CR-15 M-1, M-2, L-1, L-2, L-3, L-4, L-5, L-6, L-7, L-8, and I-1 (the excerpt headers now say
  counted by python, which the regenerated headers carry). I-2, I-3 and I-4 record facts and ask for nothing.
