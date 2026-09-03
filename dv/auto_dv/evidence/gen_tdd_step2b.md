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
  sequence, the program never reaches tohost; kept as the reason for the sparse regime). Green on out_fu2/h
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
  the record. Fix: the driver-event window spans two records (`raised_prev` / `released_prev`).
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
  corrupted before it reaches tohost: gen_fu_a_* first attempt, a program limit, not a checker red). The same run showed
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
