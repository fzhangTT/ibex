# Functional-coverage plan - Ibex core, opentitan configuration

Deliverable 3 (DV_prompt.txt Section 11): the definition of every functional-coverage bin (not the
implementation; TB Infra implements covergroups in the gen_ namespace from this plan). Owner: dv-lead.
Version 2 (after the Critic's advisory pre-review gen_critic_fcov_drafts_prereview_v1.md was folded in), generated 2026-09-03 09:39 UTC from dv/auto_dv/work/dv-lead/parts6/fcov_*.md.

Build configuration: `opentitan` (ibex_configs.yaml): BaseIsa=RV32IorCHERIoT (CHERIoT mode excluded
by owner ruling), RV32E=0, RV32M=RV32MSingleCycle, RV32B=RV32BOTEarlGrey, RV32ZC=RV32ZcaZcbZcmp,
RegFile=RegFileFF, BranchTargetALU=1, WritebackStage=1, ICache=1, ICacheECC=1, ICacheScramble=1,
BranchPredictor=0, DbgTriggerEn=1, SecureIbex=1, PMPEnable=1, PMPGranularity=0, PMPNumRegions=16,
MHPMCounterNum=10, MHPMCounterWidth=32.

DUT: `gen_dut_top` = `ibex_core` + `ibex_register_file_ff` (DV_prompt.txt Section 2 rulings); `ibex_top`
is not the DUT. Wrapper parameters (owner question Q-002 defaults, pending confirmation): MemECC=1
(39-bit bus data), DummyInstructions=1, ICacheTweakInfection=1, ResetAll=1, RegFileECC=0
(RegFileDataWidth=32), DbgHwBreakNum=1, DmBaseAddr=0x1A110000, DmAddrMask=0xFFF,
DmHaltAddr=0x1A110800, DmExceptionAddr=0x1A110808, CsrMvendorId=CsrMimpId=0, PMP reset values from
ibex_pkg; compiled with +define+RVFI; cheriot_enable_i tied IbexMuBiOff inside the wrapper.

# 0. Conventions

- Covergroup ID `CG-<AREA>-<nnn>` with SystemVerilog name `gen_cg_<area>_<name>` (own namespace; never
  extends an RTL covergroup). Each block: Features (F-IDs it covers), Sample (event, condition and an
  anti-vacuity note stating why the sample is not always-true and what a hit proves), Coverpoints with
  named bins (ignore_bins carry a reason; transitions are enumerated explicitly, never
  `illegal_bins = default sequence`, SIM_RECIPE.md Section 9), Crosses, Adopted (riscv-dv) and the TP
  items that must hit it. Bin references have the form `CG-<AREA>-<nnn>.cp_<name>.<bin>` (cross bins
  `...cr_<name>.<bin>`).
- Counts and ranges derive from ibex_pkg parameters and the config (PMPNumRegions, MHPMCounterNum,
  IC_NUM_WAYS, IC_LINE_BEATS, irq_fast width), never re-typed literals.
- Three randomization layers are covered in Section REG (knob values, regime phases, knob transitions,
  regime change while an event is in flight); cross-interface crosses in Section XIF; bins adopted from
  riscv-dv's coverage model in Section ADOPT, marked "adopted" and counted separately.
- Manifest rule: a test's fcov-expectation manifest lists only closure bins. Excluded from manifests
  until the probe register carries the probe: bins marked probe-gated (P1 or P4) in an area's "Probe
  candidates" section or in an item's `- Manifest:` field; informational bins (items with
  `Expected: informational`); witness bins retained for traceability. The isa area references
  auto-cross bins as `_`-joined operand names (`cr_x.a_b`) restricted to the reachable combinations
  its ignore clauses leave; the manifest generator expands them the same way.
- Layer-1 weights: each area's test-plan header carries the per-agent / per-operand-class weight
  tables (W-*) that its items reference, so DV_prompt Section 6 layer 1 is stated once per class.
- Code-coverage gate: the scope ruling is gen_tb_architecture.md Section 5 (intervention log Q-014): the
  two inner instances are gated and combined per metric by the summing rule; the wrapper is informational;
  -cm_glitch 0 on every measured build (R-002). Functional coverage gate: the URG functional-group score
  with equal group weights after ignore_bins (cross bins counted per expanded bin), not a flat ratio over
  declared bins; Section 1 states the conditions.
- Adoption policy (DV_prompt Section 3, riscv-dv ruling): a bin is "adopted" only when riscv-dv's coverage
  model was its source (CG-ADOPT-* groups, adopted=1 in the CSV, counted separately). A partition that was
  derived independently from the ISA text and coincides with a riscv-dv coverpoint is spec-derived and is
  marked in its covergroup as "coincides with riscv_instr_cover_group.sv <cg>" so the audit is possible;
  the ISA area's marks record this per coverpoint.
- Bin naming: array coverpoints use URG's form `name[N]` (e.g. fast[0]..fast[14]) in the plan, the CSV and
  the manifests, so ci/check_fcov_expectations.py finds them in the vdb by that name.
- Knob defaults and class windows: the static knob defaults are the TB defaults recorded in
  dv/auto_dv/tb/gen_tb_knobs.yaml (imem/dmem latency short/short, irq_regime quiet, irq_line_mix single);
  they govern only runs without a layer-3 schedule (bring-up, unit tests). Every measured run draws its
  regimes from the seed-derived +gen_regime_sched schedule, whose first phase is drawn from the seed as
  well (requested from TB Infra), so no measured run depends on the static default. The numeric class
  windows of the bus knobs (rvalid min1 = 1, short = 2..4, long = 5..32, random = 1..32; gnt same_cycle 0,
  short 1..3, long 4..32, random 0..32) live in the yaml's regime_windows block and match the REG and
  bus covergroups' delay bins.
- Cross-bin references claim their component coverpoint bins: an item that lists `cr_x.a_b` also owns the
  coverpoint bins a and b for the ownership count; the CSVs list them explicitly where the area author
  expanded them.
- Probe candidates: bins that cannot be sampled from the boundary or RVFI name the internal net and
  the boundary alternative; every probe needs a probe-register entry (TB Infra) and Critic approval.
  Candidates so far: P1 dummy-instruction seam nets (dummy_instr_id_o / dummy_instr_wb_o, wrapper
  internal), P2 icache hit/miss view (tag RAM model first), P3 fetch-buffer occupancy, P4 controller FSM
  state (RTL fcov_* hooks), P5 register-file seam, P6/P7 CSR write-path nets (see the CSR part). No
  checker depends on a probe.

# 1. Completeness measure (definition; DV_prompt.txt Section 4)

1. Every ACTIVE feature maps to at least one TP item and at least one bin (directly or through an
   ALIAS/FOLDED ID that resolves to it). 2. Every bin maps back to a feature through its covergroup's
   Features field (all of which must be existing F-IDs). 3. Adopted bins (riscv-dv) are counted
   separately and do not substitute for spec-derived bins. 4. A reviewer other than the author (the
   Critic) confirms the mapping. 5. Per test, the declared bins (fcov-expectation manifest) must be hit
   in that test's own run; the check is pre-merge (ci/check_fcov_expectations.py). The script
   dv/auto_dv/tools/gen_trace_check.py evaluates 1-3 over gen_feature_list.md, gen_test_plan.md,
   gen_fcov_plan.md and the two CSVs and exits non-zero on any violation.

# 1.1 Coverpoints owned by no test-plan item (regression-level; owner = the group hosting the covergroup)

Generated from the CSVs. These coverpoints are sampled and reported but no per-test manifest is held to
them; closure treats them as regression-level bins with the named owner group. gen_trace_check.py reports
the count.

| Covergroup | Coverpoint | Owner group(s) |
|---|---|---|
| CG-MUL-002 | cp_dmem_delay | gen_mul_mul, gen_mul_random, gen_mul_timing |
| CG-MUL-005 | cp_sva_checked | gen_mul_timing |
| CG-CMP-001 | cp_reg3 | gen_cmp_random, gen_cmp_zca |
| CG-CMP-006 | cp_dmem_delay | gen_cmp_random, gen_cmp_zcmp_basic, gen_cmp_zcmp_events_xfail, gen_cmp_zcmp_faults |
| CG-CMP-009 | cp_dmem_delay | gen_cmp_random, gen_cmp_zcmp_basic |
| CG-BTALU-001 | cp_taken | gen_btalu_basic, gen_btalu_dit, gen_btalu_dit_xfail, gen_btalu_hazard, gen_btalu_perf_b17_xfail, gen_btalu_random, gen_isa_cti |
| CG-BTALU-001 | cp_target_align | gen_btalu_basic, gen_btalu_dit, gen_btalu_dit_xfail, gen_btalu_hazard, gen_btalu_perf_b17_xfail, gen_btalu_random, gen_isa_cti |
| CG-BTALU-002 | cp_odd_sum | gen_btalu_basic, gen_btalu_hazard_xfail, gen_btalu_random |
| CG-BTALU-003 | cp_wb_outstanding | gen_btalu_basic, gen_btalu_hazard, gen_btalu_random |
| CG-BTALU-003 | cp_wb_error | gen_btalu_basic, gen_btalu_hazard, gen_btalu_random |
| CG-BTALU-003 | cp_dmem_delay | gen_btalu_basic, gen_btalu_hazard, gen_btalu_random |
| CG-CSR-005 | cr_alias_u_ok | gen_csr_counters, gen_csr_illegal, gen_csr_storm, gen_csr_umode |
| CG-CSR-005 | cr_alias_u_trap | gen_csr_counters, gen_csr_illegal, gen_csr_storm, gen_csr_umode |
| CG-CSR-005 | cr_alias_m | gen_csr_counters, gen_csr_illegal, gen_csr_storm, gen_csr_umode |
| CG-CSR-006 | cr_csr_form_trap | gen_csr_illegal, gen_csr_machine_info |
| CG-CSR-006 | cr_csr_u | gen_csr_illegal, gen_csr_machine_info |
| CG-CSR-006 | cr_hartid_val_rd | gen_csr_illegal, gen_csr_machine_info |
| CG-CSR-009 | cr_key_rd | gen_csr_cpuctrl, gen_csr_illegal, gen_csr_reset |
| CG-CSR-010 | cp_pulse | gen_csr_access, gen_csr_cpuctrl, gen_csr_illegal, gen_csr_reset |
| CG-CSR-010 | cr_op_form_pulse | gen_csr_access, gen_csr_cpuctrl, gen_csr_illegal, gen_csr_reset |
| CG-CSR-010 | cr_rd_value | gen_csr_access, gen_csr_cpuctrl, gen_csr_illegal, gen_csr_reset |
| CG-CSR-010 | cr_u | gen_csr_access, gen_csr_cpuctrl, gen_csr_illegal, gen_csr_reset |
| CG-CSR-013 | cr_carry | gen_csr_counters, gen_csr_storm, gen_csr_trap_handling |
| CG-CSR-017 | cp_alert_int | gen_csr_storm |
| CG-CSR-017 | cr_alert_density | gen_csr_storm |
| CG-PRV-007 | cp_mst_touched | gen_csr_cpuctrl, gen_csr_debug_csr, gen_csr_debug_csr_xfail, gen_prv_debug, gen_prv_debug_xfail, gen_prv_storm |
| CG-PRV-007 | cp_mst_after_exc | gen_csr_cpuctrl, gen_csr_debug_csr, gen_csr_debug_csr_xfail, gen_prv_debug, gen_prv_debug_xfail, gen_prv_storm |
| CG-PRV-007 | cr_entry_touched | gen_csr_cpuctrl, gen_csr_debug_csr, gen_csr_debug_csr_xfail, gen_prv_debug, gen_prv_debug_xfail, gen_prv_storm |
| CG-PRV-008 | cr_fast_id | gen_csr_illegal, gen_csr_reset, gen_csr_trap_handling, gen_csr_trap_setup, gen_prv_debug, gen_prv_illegal, gen_prv_irq, gen_prv_modes, gen_prv_mret, gen_prv_storm |
| CG-EXC-001 | cp_pc_align | gen_exc_ebreak_ecall, gen_exc_fetch_fault, gen_exc_lsu_fault, gen_exc_regime, gen_exc_sync_causes, gen_exc_trap_state |
| CG-EXC-001 | cr_cause_pcalign | gen_exc_ebreak_ecall, gen_exc_fetch_fault, gen_exc_lsu_fault, gen_exc_regime, gen_exc_sync_causes, gen_exc_trap_state |
| CG-EXC-002 | cp_pc_align | gen_exc_double_fault, gen_exc_fetch_fault, gen_exc_mret, gen_exc_priority, gen_exc_regime, gen_exc_sync_causes, gen_exc_zcmp |
| CG-EXC-002 | cr_flow_align | gen_exc_double_fault, gen_exc_fetch_fault, gen_exc_mret, gen_exc_priority, gen_exc_regime, gen_exc_sync_causes, gen_exc_zcmp |
| CG-EXC-004 | cp_mepc_align | gen_exc_debug_mode, gen_exc_ebreak_ecall, gen_exc_sync_causes, gen_exc_trap_state |
| CG-EXC-004 | cr_form_align | gen_exc_debug_mode, gen_exc_ebreak_ecall, gen_exc_sync_causes, gen_exc_trap_state |
| CG-EXC-005 | cp_pc_align | gen_exc_double_fault, gen_exc_sync_causes, gen_exc_trap_state |
| CG-EXC-005 | cr_priv_align | gen_exc_double_fault, gen_exc_sync_causes, gen_exc_trap_state |
| CG-EXC-006 | cp_irq_pending | gen_exc_lsu_fault, gen_exc_priority, gen_exc_regime, gen_exc_sync_causes, gen_exc_zcmp, gen_irq_regime, gen_irq_wfi |
| CG-EXC-006 | cr_latency_irq | gen_exc_lsu_fault, gen_exc_priority, gen_exc_regime, gen_exc_sync_causes, gen_exc_zcmp, gen_irq_regime, gen_irq_wfi |
| CG-EXC-007 | cp_irq_also | gen_exc_priority, gen_exc_priority_info |
| CG-EXC-007 | cr_pair_irq | gen_exc_priority, gen_exc_priority_info |
| CG-EXC-012 | cp_crash_dump | gen_exc_ebreak_ecall, gen_exc_fetch_fault, gen_exc_illegal, gen_exc_lsu_fault, gen_exc_mret, gen_exc_regime, gen_exc_sync_causes, gen_exc_trap_state, gen_exc_zcmp, gen_irq_lines, gen_irq_nmi, gen_irq_nmi_int |
| CG-EXC-012 | cr_kind_crash | gen_exc_ebreak_ecall, gen_exc_fetch_fault, gen_exc_illegal, gen_exc_lsu_fault, gen_exc_mret, gen_exc_regime, gen_exc_sync_causes, gen_exc_trap_state, gen_exc_zcmp, gen_irq_lines, gen_irq_nmi, gen_irq_nmi_int |
| CG-IRQ-007 | cp_mepc_align | gen_exc_priority, gen_irq_debug, gen_irq_nmi, gen_irq_nmi_int, gen_irq_regime, gen_irq_reset, gen_irq_wfi |
| CG-IRQ-007 | cr_source_align | gen_exc_priority, gen_irq_debug, gen_irq_nmi, gen_irq_nmi_int, gen_irq_regime, gen_irq_reset, gen_irq_wfi |
| CG-PMP-008 | cp_lat | gen_pmp_data_fault, gen_pmp_misaligned, gen_pmp_mprv, gen_pmp_random_regime |
| CG-PMP-008 | cr_lat | gen_pmp_data_fault, gen_pmp_misaligned, gen_pmp_mprv, gen_pmp_random_regime |
| CG-PMP-014 | cp_regime | gen_pmp_match_tor, gen_pmp_perm_mml0, gen_pmp_priority, gen_pmp_random_regime, gen_pmp_reset |
| CG-IMEM-001 | cp_gnt_knob | gen_imem_latency, gen_imem_proto_basic, gen_imem_regime |
| CG-IMEM-006 | cp_regime | gen_imem_fetch_err, gen_imem_latency, gen_imem_proto_basic, gen_imem_regime |
| CG-IMEM-007 | cp_gnt_with_req | gen_imem_proto_basic, gen_imem_proto_basic_info |
| CG-IMEM-007 | cp_gnt_regime | gen_imem_proto_basic, gen_imem_proto_basic_info |
| CG-DMEM-001 | cp_gnt_knob | gen_dmem_ctx, gen_dmem_err, gen_dmem_latency, gen_dmem_misaligned, gen_dmem_proto_basic, gen_dmem_regime |
| CG-DMEM-001 | cp_rvalid_knob | gen_dmem_ctx, gen_dmem_err, gen_dmem_latency, gen_dmem_misaligned, gen_dmem_proto_basic, gen_dmem_regime |
| CG-DMEM-009 | cp_gnt_with_req | gen_dmem_load_data, gen_dmem_proto_basic, gen_dmem_proto_basic_info |
| CG-DMEM-009 | cp_gnt_regime | gen_dmem_load_data, gen_dmem_proto_basic, gen_dmem_proto_basic_info |
| CG-FE-004 | cp_dummy_seen | gen_fe_backpressure |
| CG-IC-002 | cp_key_knob | gen_ic_inval, gen_ic_regime |
| CG-IC-006 | cp_knob | gen_ic_ecc, gen_ic_regime, gen_ic_replace_info |
| CG-IC-008 | cp_instr_mix | gen_ic_enable, gen_ic_inval, gen_ic_regime |
| CG-IC-008 | cp_imem_regime | gen_ic_enable, gen_ic_inval, gen_ic_regime |
| CG-IC-008 | cp_ecc_knob | gen_ic_enable, gen_ic_inval, gen_ic_regime |
| CG-IC-008 | cp_key_knob | gen_ic_enable, gen_ic_inval, gen_ic_regime |
| CG-DIT-002 | cp_dit | gen_dit_random, gen_dit_timing |
| CG-DIT-003 | cp_dit | gen_dit_timing |
| CG-DIT-004 | cp_dit | gen_dit_dummy, gen_dit_dummy_events, gen_dit_dummy_events_xfail, gen_dit_dummy_xfail, gen_dit_random |
| CG-DIT-004 | cp_mask | gen_dit_dummy, gen_dit_dummy_events, gen_dit_dummy_events_xfail, gen_dit_dummy_xfail, gen_dit_random |
| CG-DIT-005 | cp_dummy_en_at_write | gen_dit_secureseed, gen_dit_timing |
| CG-SEC-002 | cp_rf_wr_suppress | gen_rvfi_ext_rf_wr_suppress_xfail, gen_sec_alert_inject_dbus, gen_sec_alert_inject_dbus_clean_info, gen_sec_alert_inject_dbus_first_beat_xfail, gen_sec_alert_inject_dbus_info, gen_sec_alert_inject_ibus |
| CG-SEC-002 | cp_beat_order | gen_rvfi_ext_rf_wr_suppress_xfail, gen_sec_alert_inject_dbus, gen_sec_alert_inject_dbus_clean_info, gen_sec_alert_inject_dbus_first_beat_xfail, gen_sec_alert_inject_dbus_info, gen_sec_alert_inject_ibus |
| CG-SEC-005 | cp_key_delay | gen_rst_boot, gen_sec_cpuctrlsts, gen_sec_double_fault, gen_sec_inputs_mubi, gen_sec_scr_key |
| CG-RVFI-002 | cp_trap | gen_dit_timing, gen_rvfi_mem, gen_rvfi_random, gen_rvfi_trap |
| CG-RVFI-003 | cp_trap | gen_dit_dummy_events, gen_dit_dummy_events_xfail, gen_rst_pending_at_boot, gen_rvfi_ext, gen_rvfi_ext_rf_wr_suppress_xfail, gen_rvfi_random, gen_rvfi_zcmp, gen_sec_alert_inject_dbus, gen_sec_alert_inject_dbus_first_beat_xfail, gen_sec_alerts_neg, gen_sec_scr_key |
| CG-CHERI-001 | cp_trap | gen_cheri_off_quiet, gen_sec_boundary |

74 regression-level coverpoints of 2278 declared.

# 2. Counts

| Metric | Value |
|---|---|
| Covergroups | 207 |
| Distinct bins referenced by TP items | 15825 |
| Adopted bins (riscv-dv, counted separately) | 49 |
| ACTIVE features with >= 1 bin | 705 |
| Covergroups per area part | isa 40, csr 25, exc_irq 26, pmp 16, dbg_trg_pmc 22, mem_fetch_icache 30, sec_rst_rvfi_cheri 20, xcut 28 |

# 3. Covergroups by area

# 3.1 Areas ISA, MUL, CMP, BIT, BTALU: Instruction set: RV32I base, M (RV32MSingleCycle), compressed Zca/Zcb/Zcmp, bitmanip RV32BOTEarlGrey, branch target ALU


Scope: F-ISA-001..052, F-MUL-001..028, F-CMP-001..070, F-BIT-001..041, F-BTALU-001..016 (207
features: 170 ACTIVE, 19 ALIAS, 18 FOLDED; source dv/auto_dv/work/dv-lead/parts/gen_part_isa.md).
Features lines below may name ALIAS/FOLDED IDs; they resolve to the canonical / parent ID. Every
FOLDED feature names the bin of this file that carries it. Companion test plan: tp_isa.md. Build: opentitan (RV32IMC + RV32BOTEarlGrey + Zca/Zcb/Zcmp, BranchTargetALU=1,
WritebackStage=1, SecureIbex=1, DummyInstructions=1 per Q-002 defaults).

Conventions
- Every covergroup samples from a TB monitor transaction, never from a free-running clock. The
  primary event is the RVFI monitor's retirement transaction (one per rvfi_valid cycle: insn,
  pc_rdata, pc_wdata, trap, rs1/rs2/rs3 addr+rdata, rd addr+wdata, mem_*, ext_mcycle,
  ext_mhpmcounters, ext_expanded_insn*, mode). Operand classes are computed by the monitor from
  rvfi_rs*_rdata and the decoded immediate; "decoded" means decoded by the monitor's own table
  from rvfi_insn (never from an RTL net). A bin written `mnemonic{}` on a "decoded" coverpoint
  has the predicate "the monitor's decode table returns that mnemonic" (ENC table for Zb*).
- Retire-to-retire cycle delta ("delta") = rvfi_ext_mcycle(this) - rvfi_ext_mcycle(previous
  retirement). rvfi_ext_mcycle is captured when the instruction leaves ID (rtl/ibex_core.sv:2102),
  so the delta measures THIS instruction's ID residency plus any bubble before it entered ID;
  every delta in this file is measured from the previous retirement, never to the next one.
  Every cp_delta is `iff gap_clean`, where gap_clean = (fetch_stall == no) and
  (cpuctrlsts.dummy_instr_en == 0 in the TB CSR model for the whole gap, so no dummy instruction
  can sit in it) and (no csrw to mcycle/mcycleh/mcountinhibit retired between the two
  retirements) and (cpuctrlsts.icache_enable == 0 in the TB CSR model, so the ibus monitor sees
  every fetch). fetch_stall (ibus monitor) = the fetch data for THIS instruction's address was
  not delivered (instr_rvalid_i for that address) by the cycle the previous instruction left ID;
  it is `yes` by construction for the first retirement after a taken CTI, trap, mret, dret or
  fence.i (the redirected fetch), so those retirements never enter a clean bin; a CTI's own
  delta is measured on the CTI itself (its fetch precedes the redirect). wb_busy (dbus monitor)
  = a granted data access without response when this instruction entered ID; the clean crosses
  (cr_*_clean) additionally require wb_busy == no.
- CTI redirect delta (CG-BTALU-001.cp_delta, CG-BTALU-002.cp_delta; fix 3, rtl-arch T-053
  TP-ISA-024 / TP-BTALU-012): for a control-transfer instruction the delta bin is the REDIRECT
  delta rvfi_ext_mcycle(successor) - rvfi_ext_mcycle(CTI), the cost of the redirected fetch
  (tp_isa.md header, Timing terms); its guard is `iff redirect_clean` = (icache_enable == 0 in the
  TB CSR model) and (imem agent pinned to gnt same_cycle / rvalid min1) and (no fill request pending
  at the CTI's pc_set cycle, ibus monitor) and (target instruction word-aligned or compressed: no
  bus-word straddle) and (no dummy / mcycle write in the gap) - NOT the successor's fetch_stall,
  which is yes by construction. Minimum 2 (rtl/ibex_icache.sv:249, :703, :1030-1031;
  rtl/ibex_if_stage.sv:568-587), 3 for fence.i (the refetch always goes to the bus while
  inval_block_cache is set, rtl/ibex_icache.sv:1218, :1259-1266); exact 2 is a coverage bin and the
  checker's pass rule is >= 2. A not-taken branch under data_ind_timing = 0 has no redirect and its
  bin is its own delta (1).
- Deferred start (C-9 / X-12; fix 3): the cp_wb_busy / cp_wb_defer coverpoints record that a data
  access was outstanding when the instruction entered ID and its response arrived after that cycle;
  the multiplier / divider / two-cycle ALU op then starts in the response cycle (instr_executing
  needs ~outstanding_memory_access = (outstanding_load_wb | outstanding_store_wb) & ~lsu_resp_valid,
  rtl/ibex_id_stage.sv:1014-1016, :1059-1062), so the record delta from the access record is own
  occupancy + W (W = data_rvalid_i cycle - (access ID-exit + 1), 0 for min1); there is no
  mid-operation hold and no load-result forwarding (rtl/ibex_id_stage.sv:1117-1118). The former
  names cr_wb_hold / cp_wb_hold / cr_op_wb_hold / cp_hold_cycles / cr_class_hold are renamed
  cr_wb_defer / cp_wb_defer / cr_op_wb_defer / cp_defer_cycles / cr_class_defer.
- RVFI insn rule (C-12 / X-14; fix 3): rvfi_insn is the 32-bit expansion for every Zcmp micro-op
  including the reserved rlist 0..3 encodings (INSTR_EXPANDED tag, rtl/ibex_core.sv:2263-2267;
  rtl/ibex_compressed_decoder.sv:626, :691); non-expanded compressed instructions (c.ebreak, Zca/Zcb,
  the other illegal halfwords) are traced as the zero-extended halfword; mtval is always the
  halfword. Predicates written "rvfi_insn == zero-extended halfword" are class-dependent
  accordingly (CG-CMP-004.cp_rvfi_insn_ok). core_busy_o (IbexMuBiOff) is the sleep observable; the
  core has no core_sleep_o (C-5).
- Programmable state (privilege, cpuctrlsts.data_ind_timing/dummy_instr_en/icache_enable,
  dcsr.*, mstatus.TW, mcountinhibit) is tracked by the TB CSR model from the retired CSR writes on
  RVFI (predict-and-check), never probed. Redirects are derived from RVFI (rvfi_pc_wdata != pc +
  len and the next rvfi_pc_rdata); the ibus-derived redirect coverpoints (cp_redirect,
  cp_redirect_count, cp_redirect_once) are `iff icache_enable == 0` because a cache hit issues
  no bus request.
- Bin syntax: `name{values}`; `auto{all combinations}` on a cross means every combination of the
  listed coverpoints' bins that is not excluded by an `ignore` clause on the cross line or by an
  `ignore_bins` / probe-gated / operand-only marker on a coverpoint line. An auto cross bin is
  named by joining its operand bins with `_` in cross order (cr_op_rs1 bin `addi_zero`); the
  trace_tp_bin CSV lists every reachable auto bin by that name and never an ignored one. When a
  TP item lists `cr_x.auto` and also explicit bins of one of the cross's coverpoints, the
  expansion is restricted to those bins of that coverpoint (the item's own stimulus scope).
  "iff" gives the per-coverpoint sampling guard.
- Witness bins (`yes{1}`, `observed{1}`) are sampled only on the retirement of the very
  instruction whose property they witness, never on a free-running or unrelated event; the
  failing case is a checker error, not a bin, so no `no{0}` counterpart is declared for them.
- Operand-only coverpoints: a coverpoint marked `[operand-only: canonical CG-X.cp_y]` repeats a
  partition owned by another covergroup and exists here only as a cross operand (SV
  `option.weight = 0`); its standalone bins are in no manifest and no CSV row. Knob-class
  partitions (cp_dmem_delay = the dbus response-latency class) are operand-only everywhere in
  this file; knob values themselves are covered in the xcut REG groups.
- Probe-gated bins (`[probe-gated (P1), not in manifest]`) need an internal observation the
  probe register does not yet carry; they stay in the plan, are absent from the CSV and become
  must-hit when the probe is registered (gen_tb_architecture.md 8.3 item 5).
- Class values used repeatedly: zero=0x00000000, all_ones=0xFFFFFFFF, int_min=0x80000000,
  int_max=0x7FFFFFFF, one=1, msb_only=0x80000000, lsb_only=1; pos_rand = any other value with
  bit 31 clear, neg_rand = any other value with bit 31 set.
- Counts derive from ibex_pkg / decoder tables: Zcmp rlist 4..15 and spimm 0..3 come from
  rtl/ibex_compressed_decoder.sv cm_stack_adj_base/cm_rlist_top_reg; the legal Zb* mnemonic
  list is the ENC table (dv/auto_dv/work/rtl-arch/gen_rv32b_otearlgrey_encodings.md); micro-op
  index range 0..15 is the popretz maximum (13 loads + addi + li + ret). Performance-counter
  events are the hardwired map of rtl/ibex_cs_registers.sv:1585-1597 (mhpmcounter7 = NumJumps,
  8 = NumBranches, 9 = NumBranchesTaken; the mhpmevent selectors are read-only, :1600-1617) and
  are read through rvfi_ext_mhpmcounters[i - MHPMCOUNTER_BASE] (MHPMCOUNTER_BASE = 3,
  rtl/ibex_core.sv:2108-2126), so nothing is programmed to select them.
- Adopted bins (S-9 policy; Critic M-5 pass done 2026-09-03): vendor/google_riscv-dv/src/
  riscv_instr_cover_group.sv was read as REFERENCE ONLY and every ISA/MUL/CMP/BIT/BTALU coverpoint
  of this file was compared with it. No partition in this file was taken from riscv-dv (each was
  derived from the ISA text or the RTL), so the CSV adopted column is 0 for every bin. Where a
  partition coincides with a riscv-dv coverpoint the covergroup's `Adopted (riscv-dv)` line names
  it in the form "coincides with riscv_instr_cover_group.sv <cg>.<cp> (spec-derived, independently
  derived from the ISA text; adopted=0)"; a refinement (more bins over the same variable) is marked
  "refines". A partition that duplicates an adopted CG-ADOPT group exactly is counted once there
  and kept here as a cross operand only (CG-CMP-001.cp_reg3 -> CG-ADOPT-005.cp_c_reg_prime). The DV
  Lead records the policy (tp_isa.md OQ-2).
- Never `illegal_bins = default sequence`; no transition bins are used in this file.

---------------------------------------------------------------------------------------------------
## AREA ISA

### CG-ISA-001: gen_cg_isa_alu_imm
- Features: F-ISA-001, F-ISA-002, F-ISA-003, F-ISA-004
- Sample: RVFI retirement; condition: decoded opcode == OP-IMM and funct3 in {000,010,011,100,110,111} and rvfi_trap == 0; anti-vacuity: rvfi_valid is a subset of cycles and the funct3 guard excludes shifts, loads, and every other class; a hit proves an I-type ALU op retired with the sampled operand/immediate class.
- Coverpoints:
  - cp_op = funct3: bins addi{000}, slti{010}, sltiu{011}, xori{100}, ori{110}, andi{111}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, pos_rand{[2:0x7FFFFFFE]}, neg_rand{[0x80000001:0xFFFFFFFE]}
  - cp_imm_class = class(sext(imm12)): bins zero{0}, plus1{1}, minus1{-1}, max_pos{2047}, min_neg{-2048}, pos_rand{[2:2046]}, neg_rand{[-2047:-2]}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_rs1_eq_rd = (rs1_addr == rd_addr and rd_addr != 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, other{default}
  - cp_addi_wrap = sign(rs1) == sign(imm) and sign(result) != sign(rs1), iff addi: bins pos_wrap{rs1 >= 0 and imm > 0 and result < 0}, neg_wrap{rs1 < 0 and imm < 0 and result >= 0}, none{otherwise}
  - cp_slt_case = boundary case, iff op in {slti, sltiu}: bins eq{rs1 == sext(imm)}, slti_intmin_0{slti and rs1 == 0x80000000 and imm == 0}, slti_0_neg{slti and rs1 == 0 and imm < 0}, sltiu_imm_m1{sltiu and imm == -1}, sltiu_seqz{sltiu and imm == 1}, sltiu_ones_m1{sltiu and rs1 == 0xFFFFFFFF and imm == -1}, other{default}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_imm = cp_op x cp_imm_class: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
  - cr_slt = cp_op x cp_slt_case: bins auto{all combinations}; ignore ops other than slti/sltiu: cp_slt_case is guarded to compares; ignore slti with the sltiu_* cases and sltiu with the slti_* cases: the case names its op
- Adopted (riscv-dv): cp_imm_class refines riscv_instr_cover_group.sv addi_cg.cp_imm_sign (pos_rand/neg_rand plus the boundary values) (spec-derived, independently derived from the ISA text; adopted=0); cp_addi_wrap is the overflow subset of addi_cg.cp_sign_cross (spec-derived, independently derived from the ISA text; adopted=0)
- TP items: TP-ISA-001, TP-ISA-002, TP-ISA-003, TP-ISA-004, TP-ISA-054

### CG-ISA-002: gen_cg_isa_alu_reg
- Features: F-ISA-007, F-ISA-008, F-ISA-009, F-ISA-004, F-ISA-051
- Sample: RVFI retirement; condition: decoded opcode == OP, funct7 in {0000000, 0100000}, funct3 in {000,010,011,100,110,111}, rvfi_trap == 0; anti-vacuity: excludes shifts (funct3 001/101), M (funct7 0000001) and Zb* funct7 values; a hit proves an R-type base ALU op retired with the sampled operand classes.
- Coverpoints:
  - cp_op = funct7/funct3: bins add{0000000/000}, sub{0100000/000}, slt{010}, sltu{011}, xor{100}, or{110}, and{111}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, pos_rand{[2:0x7FFFFFFE]}, neg_rand{[0x80000001:0xFFFFFFFE]}
  - cp_rs2_class = class(rvfi_rs2_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, pos_rand{[2:0x7FFFFFFE]}, neg_rand{[0x80000001:0xFFFFFFFE]}
  - cp_sign_pair = bit31 of rs1,rs2: bins pp{00}, pn{01}, np{10}, nn{11}
  - cp_eq_operands = (rs1_rdata == rs2_rdata): bins no{0}, yes{1}
  - cp_same_regs = register-index relation: bins rs1_eq_rs2{rs1 == rs2 != rd}, all_same{rs1 == rs2 == rd != 0}, rs1_eq_rd{rs1 == rd != rs2}, rs2_eq_rd{rs2 == rd != rs1}, distinct{all different}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, other{default}
  - cp_wrap = 33-bit carry/borrow and signed overflow, iff op in {add, sub}: bins add_carry{add and rs1 + rs2 >= 2^32}, add_pos_ovf{add and both operands >= 0 and result < 0}, add_neg_ovf{add and both operands < 0 and result >= 0}, sub_borrow{sub and rs1 <u rs2}, sub_ovf{sub and rs1 == 0x80000000 and rs2 > 0}, none{otherwise}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_rs2 = cp_op x cp_rs2_class: bins auto{all combinations}
  - cr_op_sign = cp_op x cp_sign_pair: bins auto{all combinations}
  - cr_op_eq = cp_op x cp_eq_operands: bins auto{all combinations}
  - cr_op_same = cp_op x cp_same_regs: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
  - cr_wrap = cp_op x cp_wrap: bins auto{all combinations}; ignore ops other than add/sub: cp_wrap is guarded; ignore add with the sub_* cases and sub with the add_* cases: the case names its op
  - cr_slt_boundary = cp_op x cp_rs1_class x cp_rs2_class: bins auto{all combinations}; ignore ops other than slt/sltu: boundary semantics belong to compares
- Adopted (riscv-dv): cp_sign_pair {pp, pn, np, nn} coincides with riscv_instr_cover_group.sv sll_cg/srl_cg/sra_cg.cp_sign_cross (rs1_sign x rs2_sign) and with the rs1/rs2 projection of add_cg/sub_cg.cp_sign_cross (spec-derived, independently derived from the ISA text; adopted=0); the three-operand add/sub sign partition is CG-ADOPT-003.cp_addsub_sign (adopted) and is not repeated here
- TP items: TP-ISA-007, TP-ISA-008, TP-ISA-009, TP-ISA-004, TP-ISA-052, TP-ISA-054

### CG-ISA-003: gen_cg_isa_shift
- Features: F-ISA-010, F-ISA-011, F-ISA-013, F-ISA-014, F-ISA-004
- Sample: RVFI retirement; condition: decoded slli/srli/srai (OP-IMM funct3 001/101, instr[31:25] in {0000000, 0100000}) or sll/srl/sra (OP funct7 0000000/0100000, funct3 001/101) and rvfi_trap == 0; anti-vacuity: the funct7 guard excludes every Zb* shift-space encoding; a hit proves a base shift retired with the sampled amount and operand class.
- Coverpoints:
  - cp_op = decoded: bins slli{OP-IMM 001}, srli{OP-IMM 101 f7 0}, srai{OP-IMM 101 f7 0100000}, sll{OP 001}, srl{OP 101 f7 0}, sra{OP 101 f7 0100000}
  - cp_shamt = effective amount (imm[4:0] or rs2[4:0]): bins s0{0}, s1{1}, mid{[2:30]}, s31{31}
  - cp_rs2_upper = rvfi_rs2_rdata, iff register form: bins zero{rs2[31:5] == 0}, is32{32}, is33{33}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, ffffffe0{0xFFFFFFE0}, other_nonzero{default}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, lsb_only{1}, neg_rand{bit31 set, not listed}, pos_rand{bit31 clear, not listed}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, one{1}, c0000000{0xC0000000}, other{default}
- Crosses:
  - cr_op_shamt = cp_op x cp_shamt: bins auto{all combinations}
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_reg_upper = cp_op x cp_rs2_upper: bins auto{all combinations}; ignore immediate ops: cp_rs2_upper is guarded to register forms
  - cr_sra_sign = cp_op x cp_operand x cp_shamt: bins srai_neg_31{srai, neg_rand, s31}, srai_pos_31{srai, pos_rand, s31}, srai_msb_1{srai, msb_only, s1}, sra_neg_31{sra, neg_rand, s31}, sra_pos_31{sra, pos_rand, s31}, sra_msb_1{sra, msb_only, s1}, srli_msb_31{srli, msb_only, s31}, slli_lsb_31{slli, lsb_only, s31}; ignore other combinations: covered by cr_op_shamt / cr_op_operand
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-ISA-010, TP-ISA-011, TP-ISA-013, TP-ISA-014, TP-ISA-004, TP-ISA-054

### CG-ISA-004: gen_cg_isa_lui_auipc
- Features: F-ISA-005, F-ISA-006, F-ISA-004
- Sample: RVFI retirement; condition: decoded opcode in {LUI, AUIPC}, rvfi_trap == 0; anti-vacuity: two opcodes out of the full program mix; a hit proves a U-type op retired at the sampled PC alignment/region with the sampled immediate.
- Coverpoints:
  - cp_op = opcode: bins lui{0110111}, auipc{0010111}
  - cp_imm20 = imm[31:12]: bins zero{0}, all_ones{0xFFFFF}, msb{0x80000}, one{1}, rand{default}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_pc_region = rvfi_pc_rdata: bins low{[0:0xFFF]}, high{[0xFFFFF000:0xFFFFFFFF]}, mid{default}
  - cp_wrap = carry out of pc + (imm << 12), iff auipc: bins no{0}, yes{1}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_op_imm = cp_op x cp_imm20: bins auto{all combinations}
  - cr_auipc_pc = cp_op x cp_pc_align x cp_wrap: bins auipc_word_nowrap{auipc, word, no}, auipc_half_nowrap{auipc, half, no}, auipc_word_wrap{auipc, word, yes}, auipc_half_wrap{auipc, half, yes}; ignore lui: no PC dependence
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-ISA-005, TP-ISA-006, TP-ISA-004, TP-ISA-054

### CG-ISA-005: gen_cg_isa_hint_x0
- Features: F-ISA-004, F-ISA-051
- Sample: RVFI retirement; condition: rvfi_rd_addr == 0 and the decoded instruction class normally writes rd (ALU/LUI/AUIPC/load/CSR/jump/M/Zb*), rvfi_trap == 0; anti-vacuity: most retirements have rd != 0 or are stores/branches; a hit proves an x0-destination instruction retired and (via cp_x0_read) that a later read of x0 returned 0.
- Coverpoints:
  - cp_hint_class = decoded: bins canonical_nop{addi x0,x0,0}, addi_x0_nzimm{addi x0,rs1,imm != 0 or rs1 != 0}, andi_x0{andi}, ori_x0{ori}, xori_x0{xori}, slti_x0{slti}, sltiu_x0{sltiu}, lui_x0{lui}, auipc_x0{auipc}, add_x0{add}, sub_x0{sub}, sll_x0{sll}, srl_x0{srl}, sra_x0{sra}, slt_x0{slt}, sltu_x0{sltu}, xor_x0{xor}, or_x0{or}, and_x0{and}, slli_x0_semihost{slli x0,x0,0x1f}, srai_x0_semihost{srai x0,x0,7}, slli_x0_other{other slli}, srli_x0{srli}, srai_x0_other{other srai}, other{default}
  - cp_writer_class = decoded class: bins alu_imm{OP-IMM non-shift}, shift{shifts}, alu_reg{OP base}, lui_auipc{U-type}, load{LOAD}, csrr{SYSTEM csr}, jal{JAL}, jalr{JALR}, mul{mul}, mulh{mulh/mulhsu/mulhu}, div_rem{div/divu/rem/remu}, bit_1cyc{single-cycle Zb*}, bit_2cyc{two-cycle Zb*}, zcb_alu{c.zext.b/c.sext.b/c.zext.h/c.sext.h/c.not/c.mul with rd x0 impossible: see ignore}, cmp_hint{c.li/c.lui/c.slli/c.mv/c.add with rd x0}; ignore_bins zcb_alu: Zcb ALU forms address x8..x15 only
  - cp_x0_read = the next retirement reads x0 (rs1_addr == 0 or rs2_addr == 0) with rdata 0: bins rs1_zero{rs1_addr == 0 and rs1_rdata == 0}, rs2_zero{rs2_addr == 0 and rs2_rdata == 0}, none{default}
- Crosses:
  - cr_writer_read = cp_writer_class x cp_x0_read: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-ISA-004, TP-ISA-052, TP-MUL-026, TP-BIT-038, TP-CMP-013, TP-CMP-025, TP-CMP-027, TP-CMP-031

### CG-ISA-006: gen_cg_isa_jump
- Features: F-ISA-015, F-ISA-016, F-ISA-017, F-ISA-018, F-ISA-019, F-ISA-020, F-ISA-021, F-ISA-022,
  F-ISA-052, F-BTALU-002, F-BTALU-003 (parent of folded bins hosted here)
- Sample: RVFI retirement; condition: decoded jal/jalr/c.j/c.jal/c.jr/c.jalr and rvfi_trap == 0; anti-vacuity: jumps are a small fraction of retirements; a hit proves a jump retired with the sampled offset/target class and (pc_wdata) redirect.
- Coverpoints:
  - cp_op = decoded: bins jal{JAL}, jalr{JALR f3 000}, c_j{c.j}, c_jal{c.jal}, c_jr{c.jr}, c_jalr{c.jalr}
  - cp_rd_class = rvfi_rd_addr, iff jal/jalr: bins x0{0}, x1{1}, x5{5}, other{default}
  - cp_jal_off = sext(imm_j), iff jal: bins self{0}, max_fwd{0xFFFFE}, max_bwd{-0x100000}, pos_rand{[2:0xFFFFC]}, neg_rand{[-0xFFFFE:-2]}
  - cp_jalr_imm = sext(imm_i), iff jalr: bins zero{0}, max_pos{2047}, min_neg{-2048}, odd{imm[0] == 1}, pos_rand{even [2:2046]}, neg_rand{even [-2046:-2]}
  - cp_jalr_rs1 = rs1 relation, iff jalr/c.jr/c.jalr: bins x0{rs1_addr == 0}, eq_rd{rs1_addr == rd_addr != 0}, other{default}
  - cp_target_align = target[1] (rvfi_pc_wdata with bit 0 masked): bins word{0}, half{1}
  - cp_target_odd = (rs1_rdata + imm)[0], iff jalr/c.jr/c.jalr: bins no{0}, yes{1}
  - cp_wrap = carry out of pc + imm or rs1 + imm: bins no{0}, yes{1}
  - cp_pc_region = rvfi_pc_rdata: bins zero_page{[0:0xFF]}, high{[0xFFFFF000:0xFFFFFFFF]}, mid{default}
  - cp_link_len = rvfi_rd_wdata - rvfi_pc_rdata, iff rd != 0: bins pc4{4}, pc2{2}
- Crosses:
  - cr_op_align = cp_op x cp_target_align: bins auto{all combinations}
  - cr_jal_off_rd = cp_op x cp_jal_off x cp_rd_class: bins auto{all combinations}; ignore ops other than jal: cp_jal_off is guarded
  - cr_jalr_rs1_imm = cp_jalr_rs1 x cp_jalr_imm: bins auto{all combinations} (both operands sample only on jalr: c.jr/c.jalr have no immediate)
  - cr_op_wrap = cp_op x cp_wrap: bins auto{all combinations}; ignore c_jr/yes and c_jalr/yes: imm == 0, rs1 + 0 never carries
  - cr_odd = cp_op x cp_target_odd: bins jalr_odd{jalr, yes}, c_jr_odd{c_jr, yes}, c_jalr_odd{c_jalr, yes}; ignore other combinations: only the odd cases are the corner
  - cr_link = cp_op x cp_link_len: bins jal_pc4{jal, pc4}, jalr_pc4{jalr, pc4}, c_jal_pc2{c_jal, pc2}, c_jalr_pc2{c_jalr, pc2}; ignore mismatched lengths: impossible by construction (a hit is a checker failure)
  - cr_zero_page_bwd = cp_op x cp_pc_region x cp_jal_off: bins jal_zero_page_neg{jal, zero_page, neg_rand}; ignore other combinations: covered elsewhere
- Adopted (riscv-dv): cp_jal_off pos_rand/neg_rand refines riscv_instr_cover_group.sv jal_cg.cp_imm_sign (spec-derived, independently derived from the ISA text; adopted=0); the two-bin direction partition itself is CG-ADOPT-003.cp_imm_sign jal_fwd/jal_bwd (adopted); the jalr link-register pattern is CG-ADOPT-004.cp_ras (adopted)
- TP items: TP-ISA-015, TP-ISA-016, TP-ISA-017, TP-ISA-018, TP-ISA-019, TP-ISA-020, TP-ISA-022, TP-ISA-053, TP-ISA-054, TP-CMP-010, TP-CMP-011, TP-CMP-028, TP-CMP-032, TP-BTALU-004

### CG-ISA-007: gen_cg_isa_branch
- Features: F-ISA-023, F-ISA-024, F-ISA-026, F-ISA-027, F-ISA-052, F-BTALU-001 (parent of folded
  bins hosted here)
- Sample: RVFI retirement; condition: decoded BRANCH (funct3 not 010/011) or c.beqz/c.bnez, rvfi_trap == 0; anti-vacuity: branches are a subset of retirements; taken is derived from rvfi_pc_wdata != pc + len, so a hit proves the sampled outcome actually happened.
- Coverpoints:
  - cp_op = decoded: bins beq{000}, bne{001}, blt{100}, bge{101}, bltu{110}, bgeu{111}, c_beqz{c.beqz}, c_bnez{c.bnez}
  - cp_taken = (rvfi_pc_wdata != rvfi_pc_rdata + len): bins no{0}, yes{1}
  - cp_cmp_class = (rs1_rdata, rs2_rdata): bins equal{rs1 == rs2}, intmin_zero{rs1 == 0x80000000 and rs2 == 0}, zero_intmin{rs1 == 0 and rs2 == 0x80000000}, zero_ones{rs1 == 0 and rs2 == 0xFFFFFFFF}, ones_zero{rs1 == 0xFFFFFFFF and rs2 == 0}, both_msb_eq{rs1 == rs2 == 0x80000000}, slt_ugt{rs1 <s rs2 and rs1 >u rs2}, sgt_ult{rs1 >s rs2 and rs1 <u rs2}, rand{default}
  - cp_offset = sext(imm_b): bins self{0}, max_fwd{4094 (254 for c.b*)}, max_bwd{-4096 (-256 for c.b*)}, pos_rand{default positive}, neg_rand{default negative}
  - cp_target_align = target[1]: bins word{0}, half{1}
  - cp_wrap = carry out of pc + imm, iff taken: bins no{0}, yes{1}
- Crosses:
  - cr_op_taken_cmp = cp_op x cp_taken x cp_cmp_class: bins auto{all combinations}; ignore combinations the comparison decides (the monitor's outcome table per op and class, e.g. beq/equal/not-taken, bne/equal/taken, bltu/zero_ones/not-taken, beq/rand/taken and bne/rand/not-taken since rand excludes equal, c_beqz/rand/taken, c_bnez/rand/not-taken) and, for c_beqz/c_bnez, the classes with rs2 != 0 (zero_intmin, zero_ones, both_msb_eq, sgt_ult): rs2 is x0 by encoding
  - cr_op_offset_taken = cp_op x cp_offset x cp_taken: bins auto{all combinations}
  - cr_op_align = cp_op x cp_target_align: bins auto{all combinations}
  - cr_wrap = cp_op x cp_wrap: bins auto{all combinations}
- Cross-reference: branch timing and DIT (cp_delta, cp_dit, cp_fetch_stall, cr_taken_dit_delta, cr_taken_dit_redirect) are owned by CG-BTALU-001; this group owns cp_taken, cp_target_align and cp_wrap, which CG-BTALU-001 repeats operand-only.
- Adopted (riscv-dv): cp_taken {no, yes} coincides with riscv_instr_cover_group.sv beq_cg..bgeu_cg.cp_branch_hit (spec-derived, independently derived from the ISA text; adopted=0); cp_offset refines their cp_imm_sign (the two-bin direction partition is CG-ADOPT-003.cp_imm_sign branch_fwd/branch_bwd, adopted)
- TP items: TP-ISA-023, TP-ISA-024, TP-ISA-026, TP-ISA-027, TP-ISA-053, TP-ISA-054, TP-CMP-023, TP-BTALU-001, TP-BTALU-006

### CG-ISA-008: gen_cg_isa_fence
- Features: F-ISA-029, F-ISA-030, F-ISA-031
- Sample: RVFI retirement; condition: decoded MISC-MEM funct3 000 (fence) or 001 (fence.i), rvfi_trap == 0; anti-vacuity: MISC-MEM is rare in the mix; for fence.i the ibus monitor must also see a fresh request at pc+4 for cp_refetch to record yes.
- Coverpoints:
  - cp_op = funct3: bins fence{000}, fence_i{001}
  - cp_fence_fields = (fm, pred, succ, rs1, rd), iff fence: bins canonical{fm 0, pred 1111, succ 1111, rs1 0, rd 0}, tso{fm 1000, pred 0011, succ 0011}, pred_zero{pred 0000}, succ_zero{succ 0000}, rs1_nonzero{rs1 != 0}, rd_nonzero{rd != 0}, fm_other{fm not in 0000/1000}, rand{default}
  - cp_fencei_fields = (rs1, rd, imm), iff fence_i: bins canonical{rs1 0, rd 0, imm 0}, rs1_nonzero{rs1 != 0}, rd_nonzero{rd != 0}, imm_nonzero{imm != 0}, all_nonzero{rs1 != 0 and rd != 0 and imm != 0}
  - cp_icache_en = cpuctrlsts.icache_enable (TB CSR model): bins off{0}, on{1}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_refetch = ibus request to pc + 4 observed after the fence.i, iff fence_i: bins yes{1}
- Crosses:
  - cr_fencei = cp_op x cp_icache_en x cp_pc_align: bins auto{all combinations}; ignore fence: no fetch-path effect
- Cross-reference: fence.i timing (cp_delta d2) is owned by CG-BTALU-002 (cp_type.fence_i x cp_delta); the field coverpoints are guarded to their op, so no op x fields cross is declared (it would repeat the coverpoint).
- Adopted (riscv-dv): cp_op {fence, fence_i} coincides with riscv_instr_cover_group.sv rv32i_misc_cg.cp_misc bins FENCE / FENCE_I (spec-derived, independently derived from the ISA text; adopted=0)
- TP items: TP-ISA-029, TP-ISA-030, TP-ISA-031, TP-ISA-054, TP-BTALU-012

### CG-ISA-009: gen_cg_isa_system
- Features: F-ISA-032, F-ISA-033, F-ISA-034, F-ISA-035, F-ISA-036, F-ISA-037, F-ISA-038, F-ISA-039, F-ISA-040, F-ISA-041, F-ISA-042
- Sample: RVFI retirement; condition: decoded SYSTEM funct3 000 with funct12 in {0x000, 0x001, 0x302, 0x7b2, 0x105} or c.ebreak; anti-vacuity: these retire rarely and the outcome is derived from rvfi_trap, rvfi_ext_debug_mode transition, core_busy_o (IbexMuBiOff, C-5) and the handler's mcause read-back; cp_wfi_resume / cp_busy_off sample only on an executed wfi and discriminate the resume path (handler / debug / sequential) and the visibility of the busy dip; a hit proves the sampled (priv, config, outcome) tuple occurred.
- Coverpoints:
  - cp_op = decoded: bins ecall{0x000}, ebreak{0x001}, c_ebreak{0x9002}, mret{0x302}, dret{0x7b2}, wfi{0x105}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_debug_mode = rvfi_ext_debug_mode: bins no{0}, yes{1}
  - cp_ebreakm = dcsr.ebreakm (TB CSR model): bins clr{0}, set{1}
  - cp_ebreaku = dcsr.ebreaku (TB CSR model): bins clr{0}, set{1}
  - cp_tw = mstatus.TW (TB CSR model): bins clr{0}, set{1}
  - cp_outcome = derived: bins exception{rvfi_trap == 1 and handler mcause read-back 8, 11 or 3}, debug_entry{is_ebreak(rvfi_insn) and the next retirement has rvfi_ext_debug_mode == 1 with rvfi_pc_rdata == DmHaltAddr; outside debug mode this record has rvfi_trap == 0 (rtl/ibex_core.sv:1885-1886); on re-entry from debug mode rvfi_trap follows dcsr.ebreakm/ebreaku and is not used}, executed{rvfi_trap == 0 and not debug_entry: mret/dret with next rvfi_pc_rdata == mepc/dpc, or wfi retired}, illegal{rvfi_trap == 1 and mcause read-back == 2}
  - cp_wfi_wake = wake source seen by the pin monitors after a wfi retirement, iff wfi executed: bins irq{irq pin}, nmi{irq_nm_i}, debug{debug_req_i}, pending_at_entry{wake condition already true at wfi}
  - cp_wfi_resume = the retirement that follows an executed wfi and its wake (RVFI), iff wfi executed: bins handler{the next record has rvfi_intr == 1 (ordinary or NMI handler)}, debug{the next record is at DmHaltAddr with rvfi_ext_debug_mode == 1}, sequential{the next record is the instruction after the wfi}
  - cp_busy_off = core_busy_o == IbexMuBiOff observed for >= 1 cycle between the wfi record and the wake (misc monitor; C-5: visible only with no outstanding fetch beat, no invalidation and an idle LSU), iff wfi executed with a delayed wake (not pending_at_entry): bins yes{1}
- Crosses:
  - cr_op_priv_outcome = cp_op x cp_priv x cp_outcome: bins ecall_m_exc{ecall, m, exception}, ecall_u_exc{ecall, u, exception}, ebreak_m_exc{ebreak, m, exception}, ebreak_m_dbg{ebreak, m, debug_entry}, ebreak_u_exc{ebreak, u, exception}, ebreak_u_dbg{ebreak, u, debug_entry}, c_ebreak_m_exc{c_ebreak, m, exception}, c_ebreak_m_dbg{c_ebreak, m, debug_entry}, c_ebreak_u_exc{c_ebreak, u, exception}, c_ebreak_u_dbg{c_ebreak, u, debug_entry}, mret_m_exec{mret, m, executed}, mret_u_illegal{mret, u, illegal}, dret_m_exec{dret, m, executed (debug mode)}, dret_m_illegal{dret, m, illegal}, dret_u_illegal{dret, u, illegal}, wfi_m_exec{wfi, m, executed}, wfi_u_exec{wfi, u, executed (TW = 0)}, wfi_u_illegal{wfi, u, illegal (TW = 1)}; ignore the other 30 triples: ecall/ebreak never execute or decode illegal, mret is legal in M and never executes in U, dret executes only in debug mode (rvfi_mode M) and never in U, wfi never traps with an exception cause and is legal in M
  - cr_ebreak = cp_op x cp_priv x cp_ebreakm x cp_ebreaku x cp_debug_mode x cp_outcome: bins m_ebreakm0_exc{ebreak, m, clr, any, no, exception}, m_ebreakm1_dbg{ebreak, m, set, any, no, debug_entry}, u_ebreaku0_exc{ebreak, u, any, clr, no, exception}, u_ebreaku1_dbg{ebreak, u, any, set, no, debug_entry}, dbg_reentry{ebreak, m, any, any, yes, debug_entry}, c_m_exc{c_ebreak, m, clr, any, no, exception}, c_m_dbg{c_ebreak, m, set, any, no, debug_entry}, c_u_dbg{c_ebreak, u, any, set, no, debug_entry}; ignore other combinations: not corners
  - cr_wfi_tw = cp_op x cp_priv x cp_tw x cp_outcome: bins m_tw0_exec{wfi, m, clr, executed}, m_tw1_exec{wfi, m, set, executed}, u_tw0_exec{wfi, u, clr, executed}, u_tw1_illegal{wfi, u, set, illegal}; ignore other combinations: not wfi or impossible
  - cr_wfi_priv_resume = cp_priv x cp_wfi_resume: bins m_handler{m, handler}, m_sequential{m, sequential: MIE = 0}, u_handler{u, handler}, m_debug{m, debug}, u_debug{u, debug}; ignore_bins u_sequential: irq_enabled = MIE | (priv == U) (rtl/ibex_controller.sv:490), so a U-mode wake by an enabled line always enters the handler (a hit is a gen_chk_irq failure; C-6 / X-9, rtl-arch T-053 TP-ISA-040)
  - cr_dret = cp_op x cp_debug_mode x cp_priv x cp_outcome: bins dret_dbg_exec{dret, yes, m, executed}, dret_m_illegal{dret, no, m, illegal}, dret_u_illegal{dret, no, u, illegal}; ignore other combinations: not corners
  - cr_mret = cp_op x cp_priv x cp_debug_mode x cp_outcome: bins mret_m_exec{mret, m, no, executed}, mret_u_illegal{mret, u, no, illegal}, mret_dbg_exec{mret, m, yes, executed}; ignore other combinations: not corners
- Adopted (riscv-dv): cp_op bins ecall / ebreak / mret coincide with riscv_instr_cover_group.sv rv32i_misc_cg.cp_misc and wfi with wfi_cg.cp_misc (spec-derived, independently derived from the ISA text; adopted=0); c_ebreak and dret have no riscv-dv counterpart
- TP items: TP-ISA-032, TP-ISA-033, TP-ISA-034, TP-ISA-035, TP-ISA-036, TP-ISA-037, TP-ISA-038, TP-ISA-039, TP-ISA-040, TP-ISA-041, TP-ISA-042, TP-ISA-055, TP-CMP-033

### CG-ISA-010: gen_cg_isa_csr_insn
- Features: F-ISA-043, F-ISA-044, F-ISA-045, F-ISA-046
- Sample: RVFI retirement; condition: decoded SYSTEM with funct3 in {001,010,011,101,110,111} (and 100 for the illegal bin); anti-vacuity: CSR ops are a minority of retirements; outcome comes from rvfi_trap and from the TB CSR model's write-prediction confirmed by a later read-back.
- Coverpoints:
  - cp_op = funct3: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_src_zero = (instr[19:15] == 0): bins no{0}, yes{1}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_csr_class = csr_addr[11:10]: bins rw{00, 01, 10}, ro{11}
  - cp_outcome = derived: bins read_only{no trap, no write predicted}, write{no trap, write predicted and read back}, illegal{rvfi_trap}
  - cp_f3_100 = (funct3 == 100): bins illegal{rvfi_trap == 1}
- Crosses:
  - cr_op_src_rd = cp_op x cp_src_zero x cp_rd_x0: bins auto{all combinations}
  - cr_op_class_outcome = cp_op x cp_csr_class x cp_src_zero x cp_outcome: bins csrrs_ro_src0_read{csrrs, ro, yes, read_only}, csrrc_ro_src0_read{csrrc, ro, yes, read_only}, csrrsi_ro_u0_read{csrrsi, ro, yes, read_only}, csrrci_ro_u0_read{csrrci, ro, yes, read_only}, csrrw_ro_illegal{csrrw, ro, any, illegal}, csrrwi_ro_illegal{csrrwi, ro, any, illegal}, csrrs_ro_src_illegal{csrrs, ro, no, illegal}, csrrc_ro_src_illegal{csrrc, ro, no, illegal}, csrrsi_ro_u_illegal{csrrsi, ro, no, illegal}, csrrci_ro_u_illegal{csrrci, ro, no, illegal}, csrrs_rw_src0_read{csrrs, rw, yes, read_only}, csrrc_rw_src0_read{csrrc, rw, yes, read_only}, csrrw_rw_write{csrrw, rw, any, write}, csrrwi_rw_write{csrrwi, rw, any, write}, csrrs_rw_write{csrrs, rw, no, write}, csrrc_rw_write{csrrc, rw, no, write}, csrrsi_rw_write{csrrsi, rw, no, write}, csrrci_rw_write{csrrci, rw, no, write}; ignore other combinations: privilege/debug-only illegal cases belong to the CSR area
  - cr_rd_x0_write = cp_op x cp_rd_x0 x cp_outcome: bins csrrw_x0_write{csrrw, yes, write}, csrrwi_x0_write{csrrwi, yes, write}; ignore other combinations: not the corner
- Adopted (riscv-dv): none
- TP items: TP-ISA-043, TP-ISA-044, TP-ISA-045, TP-ISA-046, TP-ISA-055

### CG-ISA-011: gen_cg_isa_illegal
- Features: F-ISA-012, F-ISA-021, F-ISA-025, F-ISA-028, F-ISA-031, F-ISA-037, F-ISA-039, F-ISA-041, F-ISA-042, F-ISA-046, F-ISA-047, F-ISA-048, F-ISA-049, F-ISA-050
- Sample: RVFI retirement; condition: (rvfi_trap == 1 and the monitor's decode table classifies rvfi_insn as an illegal encoding, or the handler read-back gives mcause == 2 for mret-in-U / dret / wfi-TW, which are legal encodings) or (rvfi_trap == 0 and the record is an ebreak encoding with rs1/rd != 0 whose handler read-back gives mcause == 2: the RVFI quirk of rtl/ibex_core.sv:1885-1886 under dcsr.ebreakm/u, cp_ebreak_variant_trap.trap0_quirk, TP-ISA-057); anti-vacuity: trapping retirements are rare and the class comes from the instruction bits, not from the trap; cp_mtval_ok is recorded only when the handler's csrr mtval retires with the predicted value.
- Coverpoints:
  - cp_class = decoded: bins shift_imm_bit25{slli with instr[26:25] != 00; srli/srai with instr[26:25] == 01 - the funct3 101 patterns with instr[26] = 1 are legal fsri (F-ISA-012) and are excluded}, jalr_f3{JALR funct3 != 000}, branch_f3{BRANCH funct3 010/011}, load_f3{LOAD funct3 011/110/111}, store_f3{STORE funct3 011/1xx}, misc_mem_f3{MISC-MEM funct3 010..111}, sys_funct12_other{SYSTEM f3 000 funct12 not in the legal five: sret 0x102, uret 0x002, sfence.vma, others}, sys_rs1_nz{legal funct12 with rs1 != 0}, sys_rd_nz{legal funct12 with rd != 0}, csr_f3_100{SYSTEM f3 100}, csr_ro_write{write to addr[11:10] == 11}, mret_in_u{mret, priv U}, dret_no_debug{dret outside debug}, wfi_u_tw1{wfi, U, TW = 1}, opc_load_fp{0x07}, opc_store_fp{0x27}, opc_amo{0x2f}, opc_op32{0x3b}, opc_opimm32{0x1b}, opc_madd{0x43}, opc_msub{0x47}, opc_nmsub{0x4b}, opc_nmadd{0x4f}, opc_op_fp{0x53}, opc_custom0{0x0b}, opc_custom1{0x2b}, opc_custom2{0x5b}, opc_custom3{0x7b}, opc_reserved_other{other 32-bit major opcodes}, all_ones_word{0xFFFFFFFF}, zero_word{32-bit 0x00000000 fetched as two zero halfwords}
  - cp_len = rvfi_insn[1:0]: bins c16{not 11}, w32{11}
  - cp_mtval_ok = handler csrr mtval == predicted (halfword zero-extended or word): bins yes{1}
  - cp_mepc_ok = handler csrr mepc == rvfi_pc_rdata of the trapping instruction: bins yes{1}
  - cp_wb_outstanding = dbus monitor state when the illegal instruction was in ID: bins none{no access}, load{load outstanding}, store{store outstanding}
  - cp_wb_error = the outstanding access returned data_err_i or PMP fault: bins no{0}, yes{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_debug_mode = rvfi_ext_debug_mode: bins no{0}, yes{1}
  - cp_ebreak_variant_trap = rvfi_trap of an ebreak encoding with rs1 != 0 or rd != 0 (SYSTEM f3 000, funct12 0x001; classes sys_rs1_nz / sys_rd_nz), iff that encoding with handler mcause read-back == 2: bins trap1{1: dcsr.ebreakm/ebreaku clear for rvfi_mode}, trap0_quirk{0: dcsr.ebreakm/ebreaku set for rvfi_mode; rtl/ibex_core.sv:1885-1886 masks the record although the illegal exception was taken (RVFI quirk, informational item TP-ISA-057)}
- Crosses:
  - cr_class_priv = cp_class x cp_priv: bins auto{all combinations}; ignore mret_in_u/m and wfi_u_tw1/m: U-only by definition
  - cr_wb = cp_wb_outstanding x cp_wb_error: bins none_ok{none, no}, load_ok{load, no}, store_ok{store, no}, load_err{load, yes}, store_err{store, yes}; ignore none_err: no access cannot error
  - cr_class_debug = cp_class x cp_debug_mode: bins auto{all combinations}; ignore dret_no_debug/yes, mret_in_u/yes and wfi_u_tw1/yes: debug mode runs at M privilege and is, by definition, not outside debug
- Adopted (riscv-dv): the opc_* bins of cp_class coincide with the unimplemented-opcode subset of riscv_instr_cover_group.sv opcode_cg.cp_opcode (spec-derived, independently derived from the ISA text; adopted=0); the other classes have no riscv-dv counterpart
- TP items: TP-ISA-012, TP-ISA-021, TP-ISA-025, TP-ISA-028, TP-ISA-031, TP-ISA-037, TP-ISA-039, TP-ISA-041, TP-ISA-042, TP-ISA-045, TP-ISA-046, TP-ISA-047, TP-ISA-048, TP-ISA-049, TP-ISA-050, TP-ISA-051, TP-ISA-056, TP-ISA-057

---------------------------------------------------------------------------------------------------
## AREA MUL

### CG-MUL-001: gen_cg_mul_ops
- Features: F-MUL-001, F-MUL-002, F-MUL-003, F-MUL-004, F-MUL-005, F-MUL-006, F-MUL-007, F-MUL-008, F-MUL-026, F-MUL-027
- Sample: RVFI retirement; condition: decoded OP funct7 0000001 funct3 000..011 or c.mul, rvfi_trap == 0; anti-vacuity: multiplies are a subset of the mix; a hit proves a multiply retired with the sampled operand classes and result class.
- Coverpoints:
  - cp_op = decoded: bins mul{000}, mulh{001}, mulhsu{010}, mulhu{011}, c_mul{c.mul}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, p16{0x10000}, two{2}, neg_rand{bit31 set, other}, pos_rand{bit31 clear, other}
  - cp_rs2_class = class(rvfi_rs2_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, p16{0x10000}, two{2}, neg_rand{bit31 set, other}, pos_rand{bit31 clear, other}
  - cp_sign_pair = bit31 of rs1,rs2: bins pp{00}, pn{01}, np{10}, nn{11}
  - cp_same_regs = index relation: bins rs1_eq_rs2{rs1 == rs2 != rd}, all_same{rs1 == rs2 == rd != 0}, rs_eq_rd{rs1 == rd or rs2 == rd, rs1 != rs2}, distinct{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, fffffffe{0xFFFFFFFE}, r3fffffff{0x3FFFFFFF}, r40000000{0x40000000}, other{default}
  - cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f3{011} (funct3 100..111 are the divides, sampled by CG-MUL-003.cp_op and excluded by this group's condition)
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_rs2 = cp_op x cp_rs2_class: bins auto{all combinations}
  - cr_op_sign = cp_op x cp_sign_pair: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}; ignore c_mul/yes: c.mul writes rsd' in x8..x15
  - cr_op_same = cp_op x cp_same_regs: bins auto{all combinations}; ignore c_mul/rs1_eq_rs2 and c_mul/distinct: c.mul has rd == rs1 == rsd' by encoding
  - cr_extremes = cp_op x cp_rs1_class x cp_rs2_class: bins auto{all combinations}; ignore combinations containing pos_rand or neg_rand: only extreme-by-extreme products are the corner
  - cr_funct3_rd_x0 = cp_funct3 x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): cp_sign_pair coincides with riscv_instr_cover_group.sv mul_cg/mulh_cg/mulhsu_cg/mulhu_cg.cp_sign_cross (rs1_sign x rs2_sign) (spec-derived, independently derived from the ISA text; adopted=0)
- TP items: TP-MUL-001, TP-MUL-002, TP-MUL-003, TP-MUL-004, TP-MUL-005, TP-MUL-006, TP-MUL-007, TP-MUL-008, TP-MUL-026, TP-MUL-027, TP-MUL-028, TP-CMP-038

### CG-MUL-002: gen_cg_mul_timing
- Features: F-MUL-001, F-MUL-003, F-MUL-009, F-MUL-010, F-MUL-011
- Sample: RVFI retirement; condition: decoded mul/mulh/mulhsu/mulhu (OP funct7 0000001 funct3 000..011), rvfi_trap == 0, and not the first retirement after reset (the delta and cp_prev need a previous retirement); the coverpoints discriminate on the clean delta (d1 vs d2), the previous retirement's class, the next retirement's dependency and the WB/fetch state, so the sample is never a tautology; anti-vacuity: cp_delta is `iff gap_clean` and cr_op_delta_clean also requires wb_busy == no, so a hit there proves the multiplier's own occupancy (1 or 2 cycles) was observed; cp_wb_busy records a deferred start (C-9): the multiplier starts in the response cycle and never holds, so the record delta is 1 + W / 2 + W.
- Coverpoints:
  - cp_op = decoded: bins mul{000}, mulh{001}, mulhsu{010}, mulhu{011}
  - cp_delta = retire delta from the previous retirement, iff gap_clean: bins d1{1}, d2{2}, d3plus{[3:$]}
  - cp_prev = class of the previous retirement: bins alu{single-cycle ALU}, mul{mul}, mulh_class{mulh/mulhsu/mulhu}, load{load}, store{store}, div{div/rem}, branch{branch/jump}, other{default: CSR, fence, system} (no first-instruction class: the first retirement after reset is not sampled)
  - cp_next_dep = the next retirement reads this rd: bins no{0}, yes{1}
  - cp_wb_busy = dbus monitor: a data access outstanding when this instruction entered ID whose response arrived after that cycle (the multiply then starts in the response cycle, C-9): bins no{0}, yes{1}
  - cp_fetch_stall = ibus monitor: fetch data not available: bins no{0}, yes{1}
  - cp_dmem_delay = dbus monitor rvalid latency class of the outstanding access, iff wb_busy: bins min1{1}, short{[2:4]}, long{[5:$]} [operand-only: canonical CG-REG (xcut) knob:dmem_rvalid_delay]
- Crosses:
  - cr_op_delta_clean = cp_op x cp_delta x cp_fetch_stall x cp_wb_busy: bins mul_d1{mul, d1, no, no}, mulh_d2{mulh, d2, no, no}, mulhsu_d2{mulhsu, d2, no, no}, mulhu_d2{mulhu, d2, no, no}; ignore other combinations: stall-dependent
  - cr_seq = cp_prev x cp_op: bins auto{all combinations}
  - cr_op_next_dep = cp_op x cp_next_dep: bins auto{all combinations}
  - cr_wb_defer = cp_op x cp_wb_busy x cp_dmem_delay: bins auto{all combinations}; ignore wb_busy no: guarded (deferred start behind the outstanding access, C-9; formerly cr_wb_hold)
- Adopted (riscv-dv): none
- TP items: TP-MUL-001, TP-MUL-003, TP-MUL-005, TP-MUL-007, TP-MUL-009, TP-MUL-010, TP-MUL-011, TP-MUL-028

### CG-MUL-003: gen_cg_div_ops
- Features: F-MUL-012, F-MUL-013, F-MUL-014, F-MUL-015, F-MUL-016, F-MUL-017, F-MUL-018, F-MUL-019, F-MUL-020, F-MUL-021, F-MUL-026
- Sample: RVFI retirement; condition: decoded OP funct7 0000001 funct3 100..111, rvfi_trap == 0; anti-vacuity: divides are a subset of the mix; a hit proves a divide retired with the sampled dividend/divisor classes.
- Coverpoints:
  - cp_op = funct3: bins div{100}, divu{101}, rem{110}, remu{111}
  - cp_dividend = class(rvfi_rs1_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, two{2}, seven{7}, neg_rand{bit31 set, other}, pos_rand{bit31 clear, other}
  - cp_divisor = class(rvfi_rs2_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, two{2}, minus_two{0xFFFFFFFE}, eq_dividend{rs2 == rs1 != 0}, abs_gt_dividend{|rs2| > |rs1|, not listed}, neg_rand{bit31 set, other}, pos_rand{bit31 clear, other}
  - cp_sign_pair = bit31 of rs1,rs2: bins pp{00}, pn{01}, np{10}, nn{11}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, eq_dividend{rd_wdata == rs1_rdata}, other{default}
- Crosses:
  - cr_op_divisor = cp_op x cp_divisor: bins auto{all combinations}
  - cr_op_dividend = cp_op x cp_dividend: bins auto{all combinations}
  - cr_div0 = cp_op x cp_divisor x cp_dividend: bins auto{all combinations}; ignore divisor != zero: the divide-by-zero table is the corner
  - cr_overflow = cp_op x cp_dividend x cp_divisor: bins div_intmin_m1{div, int_min, all_ones}, rem_intmin_m1{rem, int_min, all_ones}, divu_intmin_m1{divu, int_min, all_ones}, remu_intmin_m1{remu, int_min, all_ones}; ignore other combinations: covered by cr_op_divisor
  - cr_op_sign = cp_op x cp_sign_pair: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): cp_sign_pair coincides with riscv_instr_cover_group.sv div_cg/divu_cg/rem_cg/remu_cg.cp_sign_cross (rs1_sign x rs2_sign) (spec-derived, independently derived from the ISA text; adopted=0); cr_div0 / cr_overflow refine their cp_div_result (div_result classes) (spec-derived, independently derived from the ISA text; adopted=0)
- TP items: TP-MUL-012, TP-MUL-013, TP-MUL-014, TP-MUL-015, TP-MUL-016, TP-MUL-017, TP-MUL-018, TP-MUL-019, TP-MUL-020, TP-MUL-021, TP-MUL-026, TP-MUL-028

### CG-MUL-004: gen_cg_div_timing
- Features: F-MUL-012, F-MUL-016, F-MUL-017, F-MUL-022, F-MUL-023, F-MUL-024, F-MUL-025
- Sample: RVFI retirement; condition: decoded div/divu/rem/remu (OP funct7 0000001 funct3 100..111), rvfi_trap == 0, and not the first retirement after reset (the delta needs a previous retirement); the coverpoints discriminate on the clean delta (d2 vs d37 vs other), DIT, divide-by-zero, the mid-op event, the deferred start behind an outstanding WB access (C-9: the divider starts in the response cycle, record delta 37 + W / 2 + W; no FINISH hold exists) and the neighbour classes, so the sample is never a tautology; anti-vacuity: cp_delta is `iff gap_clean` and cr_dit_div0_delta also requires wb_defer == no; the event coverpoint records a pin assertion by the irq/debug drivers strictly inside the divide's occupancy window, so a hit proves the event arrived mid-op.
- Coverpoints:
  - cp_op = funct3: bins div{100}, divu{101}, rem{110}, remu{111}
  - cp_dit = cpuctrlsts.data_ind_timing (TB CSR model): bins off{0}, on{1}
  - cp_div0 = (rvfi_rs2_rdata == 0): bins no{0}, yes{1}
  - cp_delta = retire delta from the previous retirement, iff gap_clean: bins d2{2}, d37{37}, other{default}
  - cp_event_mid = pin asserted inside the occupancy window (irq driver / debug driver timestamps vs mcycle window): bins none{0}, irq{irq_* line}, debug_req{debug_req_i}, nmi{irq_nm_i}
  - cp_wb_defer = dbus monitor: a data access outstanding when the divide entered ID whose response arrived after that cycle (the divide starts in the response cycle, MD_IDLE -> MD_FINISH 36 cycles later; there is no FINISH hold, C-9; formerly cp_wb_hold): bins no{0}, yes{1}
  - cp_prev = previous retirement class: bins load_dep{load writing rs1 or rs2}, mul{mul class}, div{div class}, alu{ALU}, other{default}
  - cp_next = next retirement class: bins dep_alu{ALU reading rd}, mul{mul class}, div{div class}, other{default}
  - cp_fetch_stall = ibus monitor: bins no{0}, yes{1}
  - cp_irq_latency = cycles from irq assertion to rvfi_intr handler entry, iff event_mid irq: bins le37{[1:37]}, gt37{[38:$]}
- Crosses:
  - cr_dit_div0_delta = cp_dit x cp_div0 x cp_delta x cp_fetch_stall x cp_wb_defer: bins dit0_div0_d2{off, yes, d2, no, no}, dit0_nodiv0_d37{off, no, d37, no, no}, dit1_div0_d37{on, yes, d37, no, no}, dit1_nodiv0_d37{on, no, d37, no, no}; ignore other combinations: stall-dependent or contradictory
  - cr_op_event = cp_op x cp_event_mid: bins auto{all combinations}
  - cr_event_div0_dit = cp_event_mid x cp_div0 x cp_dit: bins auto{all combinations}; ignore none: no event
  - cr_prev_op = cp_prev x cp_op: bins auto{all combinations}
  - cr_next_op = cp_next x cp_op: bins auto{all combinations}
  - cr_op_wb_defer = cp_op x cp_wb_defer: bins auto{all combinations} (formerly cr_op_wb_hold)
  - cr_op_div0 = cp_op x cp_div0 x cp_dit: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-MUL-012, TP-MUL-016, TP-MUL-017, TP-MUL-022, TP-MUL-023, TP-MUL-024, TP-MUL-025, TP-MUL-028, TP-MUL-029

### CG-MUL-005: gen_cg_div_fsm_guard
- Features: F-MUL-028
- Sample: RVFI retirement; condition: decoded div/divu/rem/remu, rvfi_trap == 0, not the first retirement after reset; cp_div_ctx discriminates plain divides from disturbed ones (six classes), so the sample is never a tautology; cp_sva_checked additionally needs gen_sva_multdiv (MD-1..MD-5 of rtl-arch gen_multdiv_bound_props.md) bound in the build; anti-vacuity: every context class needs a specific preceding or coincident event timestamped by the dbus/irq/debug/ibus monitors against the divide's window, so a hit proves the divide ran under that disturbance; cp_sva_checked is recorded only when the bound properties MD-1 / MD-2 / MD-2b (36-cycle full bound, 1-cycle zero fast path, full path under DIT) evaluated non-vacuously for this divide. The hold-attempt cover MD-C4 (md_state_q == MD_FINISH && !multdiv_ready_id_i) and the former freeze-arc cover (div_en_i == 0 && md_state_q != MD_IDLE) are SVA covers, not bins: both are expected to stay unhit (C-9 / H-D3) and a hit is a reachability finding; the freeze-arc assertion is structurally implied by the state-register enable (rtl/ibex_multdiv_fast.sv:99, :101-115) and is not a checker (rtl-arch T-053 TP-MUL-030).
- Coverpoints:
  - cp_op = funct3: bins div{100}, divu{101}, rem{110}, remu{111}
  - cp_div_ctx = disturbance class: bins plain{none}, slow_wb{preceding load/store response arrives after the divide entered ID}, fault_wb{the divide's first attempt was killed by a fault of the preceding access (trap between that access and the divide's retirement at the same PC)}, irq_mid{irq line asserted inside the divide window}, debug_mid{debug_req_i inside the window}, fetch_err_next{the instruction after the divide carries a fetch error}
  - cp_dit = cpuctrlsts.data_ind_timing (TB CSR model): bins off{0}, on{1}
  - cp_sva_checked = bound properties MD-1 / MD-2 / MD-2b evaluated non-vacuously with no failure for this divide: bins yes{1} [probe-gated (gen_sva_multdiv bind, probe candidate P8), not in manifest]
- Crosses:
  - cr_ctx_op = cp_div_ctx x cp_op: bins auto{all combinations}
  - cr_ctx_dit = cp_div_ctx x cp_dit: bins auto{all combinations}
- Probe status: pending probe-register ruling (candidate P8: gen_sva_multdiv bound on ibex_multdiv_fast div_en_i / md_state_q); coverpoints cp_sva_checked excluded from manifests until ruled
- Adopted (riscv-dv): none
- TP items: TP-MUL-030

---------------------------------------------------------------------------------------------------
## AREA CMP

### CG-CMP-001: gen_cg_cmp_zca
- Features: F-CMP-001, F-CMP-002, F-CMP-004, F-CMP-005, F-CMP-008, F-CMP-010, F-CMP-012, F-CMP-014, F-CMP-016, F-CMP-018, F-CMP-020, F-CMP-021, F-CMP-023, F-CMP-024, F-CMP-026, F-CMP-028, F-CMP-030, F-CMP-032
- Sample: RVFI retirement; condition: rvfi_trap == 0 and either a decoded Zca instruction (rvfi_insn[1:0] != 11) or, for cp_insn32_straddle only, a 32-bit instruction (rvfi_insn[1:0] == 11); every other coverpoint carries `iff c16` (16-bit retirement) so it never samples on the 32-bit event; anti-vacuity: compressed vs 32-bit is decided from the retired instruction bits; a hit proves the sampled instruction retired at the sampled PC alignment with the sampled neighbour length.
- Coverpoints:
  - cp_insn = decoded, iff c16: bins c_addi4spn{}, c_lw{}, c_sw{}, c_lwsp{}, c_swsp{}, c_addi{}, c_nop{}, c_jal{}, c_j{}, c_li{}, c_lui{}, c_addi16sp{}, c_srli{}, c_srai{}, c_andi{}, c_sub{}, c_xor{}, c_or{}, c_and{}, c_beqz{}, c_bnez{}, c_slli{}, c_mv{}, c_jr{}, c_add{}, c_jalr{}
  - cp_pc_align = rvfi_pc_rdata[1], iff c16: bins word{0}, half{1}
  - cp_next_len = length of the next retired instruction, iff c16: bins n16{16}, n32{32}
  - cp_pc_inc = rvfi_pc_wdata - rvfi_pc_rdata, iff c16 and not a CTI: bins two{2}
  - cp_insn32_straddle = rvfi_pc_rdata[1] of a 32-bit instruction (pc[1] == 1 spans a word boundary), iff rvfi_insn[1:0] == 11: bins no{0}, yes{1}
  - cp_reg3 = 3-bit register field (x8..x15), iff c16 and CIW/CL/CS/CA/CB format: bins r8{0}, r9{1}, r10{2}, r11{3}, r12{4}, r13{5}, r14{6}, r15{7} [operand-only: the partition is counted once in CG-ADOPT-005.cp_c_reg_prime (adopted); used here by cr_insn_reg3]
  - cp_rd_full = 5-bit rd/rs field, iff c16 and CI/CR/CSS format: bins x1{1}, x2{2}, x8_15{[8:15]}, x16_31{[16:31]}, x3_7{[3:7]}
- Crosses:
  - cr_insn_align = cp_insn x cp_pc_align: bins auto{all combinations}
  - cr_insn_next = cp_insn x cp_next_len: bins auto{all combinations}
  - cr_insn_reg3 = cp_insn x cp_reg3: bins auto{all combinations}; ignore CI/CR/CSS instructions: guarded
  - cr_insn_rdfull = cp_insn x cp_rd_full: bins auto{all combinations}; ignore 3-bit-register formats and c_nop/c_j/c_jal (no 5-bit register field): guarded; ignore c_addi16sp with x1/x3_7/x8_15/x16_31 and c_lui with x2: encoding (c.addi16sp is rd == x2 only, c.lui excludes x2)
- Adopted (riscv-dv): cp_reg3 {r8..r15} coincides with the riscv_instr_cover_group.sv compressed gpr[] bins of cp_rd/cp_rs1/cp_rs2 in the CIW_/CL_/CS_/CA_/CB_INSTR_CG_BEGIN macros and duplicates CG-ADOPT-005.cp_c_reg_prime EXACTLY: the partition is counted once in CG-ADOPT-005 (adopted) and cp_reg3 is a cross operand only here (cr_insn_reg3); no direct CSV rows
- TP items: TP-CMP-001, TP-CMP-002, TP-CMP-004, TP-CMP-005, TP-CMP-008, TP-CMP-010, TP-CMP-012, TP-CMP-014, TP-CMP-016, TP-CMP-018, TP-CMP-020, TP-CMP-021, TP-CMP-023, TP-CMP-024, TP-CMP-026, TP-CMP-028, TP-CMP-030, TP-CMP-032, TP-CMP-070

### CG-CMP-002: gen_cg_cmp_imm_edges
- Features: F-CMP-002, F-CMP-004, F-CMP-005, F-CMP-008, F-CMP-011, F-CMP-012, F-CMP-014, F-CMP-016, F-CMP-017, F-CMP-018, F-CMP-020, F-CMP-023, F-CMP-024, F-ISA-017
- Sample: RVFI retirement of a Zca instruction with an immediate; condition: rvfi_trap == 0; anti-vacuity: each coverpoint is guarded to its format so only that instruction populates it; a hit proves the immediate extreme was decoded and executed (result on RVFI).
- Coverpoints:
  - cp_addi4spn_imm = nzuimm, iff c.addi4spn: bins min{4}, max{1020}, rand{default}
  - cp_lw_sw_uimm = uimm, iff c.lw/c.sw: bins zero{0}, max{124}, rand{default}
  - cp_sp_uimm = uimm, iff c.lwsp/c.swsp: bins zero{0}, max{252}, rand{default}
  - cp_ci_op = decoded, iff c.addi/c.li/c.andi: bins c_addi{}, c_li{}, c_andi{}
  - cp_ci_imm6 = sext(imm6), iff c.addi/c.li/c.andi: bins min{-32}, minus1{-1}, zero{0}, one{1}, max{31}, rand{default}
  - cp_lui_imm = imm6 (nzimm[17:12]), iff c.lui: bins pos_min{1}, pos_max{31}, neg_min{-32}, neg_max{-1}, rand{default}
  - cp_addi16sp_imm = nzimm, iff c.addi16sp: bins min{-512}, max{496}, plus16{16}, minus16{-16}, rand{default}
  - cp_shift_op = decoded, iff c.srli/c.srai/c.slli: bins c_srli{}, c_srai{}, c_slli{}
  - cp_shamt = shamt, iff c.srli/c.srai/c.slli and shamt != 0: bins one{1}, max{31}, rand{default}
  - cp_cj_off = sext(imm), iff c.j/c.jal: bins self{0}, max_fwd{2046}, max_bwd{-2048}, pos_rand{default positive}, neg_rand{default negative}
  - cp_cb_off = sext(imm), iff c.beqz/c.bnez: bins self{0}, max_fwd{254}, max_bwd{-256}, pos_rand{default positive}, neg_rand{default negative}
  - cp_sp_wrap = x2 result crosses 0 (carry/borrow), iff c.addi16sp/c.addi4spn: bins no{0}, yes{1}
  - cp_link = rvfi_rd_wdata - rvfi_pc_rdata, iff c.jal/c.jalr: bins pc2{2}
- Crosses:
  - cr_ci = cp_ci_op x cp_ci_imm6: bins auto{all combinations}; ignore c_addi/zero: that encoding is the HINT (CG-CMP-003)
  - cr_shift = cp_shift_op x cp_shamt: bins auto{all combinations}
  - cr_sp_wrap = cp_addi16sp_imm x cp_sp_wrap: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-CMP-002, TP-CMP-004, TP-CMP-005, TP-CMP-008, TP-CMP-011, TP-CMP-012, TP-CMP-014, TP-CMP-016, TP-CMP-017, TP-CMP-018, TP-CMP-020, TP-CMP-023, TP-CMP-024, TP-CMP-032, TP-CMP-070, TP-ISA-017

### CG-CMP-003: gen_cg_cmp_hints
- Features: F-CMP-009, F-CMP-013, F-CMP-015, F-CMP-019, F-CMP-025, F-CMP-027, F-CMP-031
- Sample: RVFI retirement; condition: decoded 16-bit HINT code point, rvfi_trap == 0; anti-vacuity: HINT code points are deliberately placed by the generator and never emitted by the assembler for normal code; a hit proves the HINT retired without trapping (state change is checked by gen_isa_compare).
- Coverpoints:
  - cp_hint = decoded: bins c_nop_nzimm{c.nop imm != 0}, c_addi_imm0{c.addi rd != 0 imm 0}, c_li_x0{c.li rd x0}, c_lui_x0{c.lui rd x0 imm != 0}, c_srli_shamt0{}, c_srai_shamt0{}, c_slli_shamt0{rd != 0}, c_slli_x0{rd x0 shamt != 0}, c_slli_x0_shamt0{}, c_mv_x0{}, c_add_x0{rs2 not in x2..x5}, c_add_x0_ntl_p1{rs2 x2}, c_add_x0_ntl_pall{rs2 x3}, c_add_x0_ntl_s1{rs2 x4}, c_add_x0_ntl_all{rs2 x5}
  - cp_minstret_inc = minstret delta over the hint (csrr pair around it) == 1: bins observed{1}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
- Crosses:
  - cr_hint_align = cp_hint x cp_pc_align: bins auto{all combinations}
- Adopted (riscv-dv): cp_hint coincides with riscv_instr_cover_group.sv hint_cg.cp_hint for the nine classes c_nop_nzimm (addi), c_li_x0 (li), c_lui_x0 (lui), c_srli_shamt0 (srli64), c_srai_shamt0 (srai64), c_slli_x0 (slli), c_slli_shamt0 (slli64), c_mv_x0 (mv), c_add_x0 (add) (spec-derived, independently derived from the ISA text; adopted=0); c_addi_imm0, c_slli_x0_shamt0 and the four c_add_x0_ntl_* sub-bins are spec-derived extensions
- TP items: TP-CMP-009, TP-CMP-013, TP-CMP-015, TP-CMP-019, TP-CMP-025, TP-CMP-027, TP-CMP-031, TP-CMP-070

### CG-CMP-004: gen_cg_cmp_illegal
- Features: F-CMP-003, F-CMP-006, F-CMP-007, F-CMP-015, F-CMP-017, F-CMP-019, F-CMP-022, F-CMP-025,
  F-CMP-029, F-CMP-035, F-CMP-037, F-CMP-044, F-CMP-054, F-CMP-066, F-ISA-049, F-EXC-008 (parent of
  folded bins hosted here)
- Sample: RVFI retirement; condition: rvfi_insn[1:0] != 11 and rvfi_trap == 1 and the monitor decode table classifies the halfword as illegal; anti-vacuity: the class is derived from the instruction bits; cp_mtval_ok / cp_rvfi_insn_ok are recorded only when the handler read-back and the RVFI field match the prediction.
- Coverpoints:
  - cp_class = decoded: bins zero_hw{0x0000}, addi4spn_imm0{instr[12:5] == 0, instr != 0}, lwsp_rd0{}, c_fld{}, c_flw{}, c_fsd{}, c_fsw{}, c_fldsp{}, c_flwsp{}, c_fswsp{}, lui_imm0{}, addi16sp_imm0{}, srli_shamt5{}, srai_shamt5{}, slli_shamt5{}, subw{}, addw{}, jr_rs1_0{0x8002}, sh_bit6{}, zcb_ls_1xx{Q0 funct3 100, instr[12:10] 1xx}, zext_w{}, zcb_alu_110{}, zcb_alu_111{}, push_rlist_res{cm.push rlist 0..3}, pop_rlist_res{}, popret_rlist_res{}, popretz_rlist_res{}, q2_101_zcmt{instr[12:8] in the Zcmt cm.jt/cm.jalt space}, q2_101_other{other instr[12:8]}, q2_011xx_65_00{instr[12:10] 011, instr[6:5] 00}, q2_011xx_65_10{instr[12:10] 011, instr[6:5] 10}
  - cp_rlist_res = instr[7:4], iff Zcmp reserved class: bins r0{0}, r1{1}, r2{2}, r3{3}
  - cp_mtval_ok = handler csrr mtval == zero-extended halfword: bins yes{1}
  - cp_rvfi_insn_ok = rvfi_insn matches the class rule (C-12 / X-14): the zero-extended halfword for every non-expanded class; for push_rlist_res / pop_rlist_res / popret_rlist_res / popretz_rlist_res (tagged INSTR_EXPANDED) rvfi_ext_expanded_insn == the halfword and rvfi_insn == the synthesized 32-bit word: bins yes{1}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
- Crosses:
  - cr_class_align = cp_class x cp_pc_align: bins auto{all combinations}
  - cr_zcmp_rlist = cp_class x cp_rlist_res: bins auto{all combinations}; ignore non-Zcmp classes: guarded
  - cr_class_priv = cp_class x cp_priv: bins auto{all combinations}
- Adopted (riscv-dv): cp_class coincides with riscv_instr_cover_group.sv illegal_compressed_instr_cg.cp_point for zero_hw (c_illegal), addi4spn_imm0 (c_addi4spn), lui_imm0 (c_lui), addi16sp_imm0 (c_addi16sp), jr_rs1_0 (c_jr), lwsp_rd0 (c_lwsp), subw / addw (c_reserv_0 / c_reserv_1) (spec-derived, independently derived from the ISA text; adopted=0); the remaining classes (Zcb / Zcmp / Zcmt reserved space, RV32 FP forms) have no riscv-dv counterpart
- TP items: TP-ISA-049, TP-ISA-056, TP-CMP-003, TP-CMP-006, TP-CMP-007, TP-CMP-015, TP-CMP-017, TP-CMP-019, TP-CMP-022, TP-CMP-025, TP-CMP-029, TP-CMP-035, TP-CMP-037, TP-CMP-044, TP-CMP-054, TP-CMP-067, TP-CMP-070

### CG-CMP-005: gen_cg_cmp_zcb
- Features: F-CMP-034, F-CMP-035, F-CMP-036, F-CMP-037, F-CMP-038, F-MUL-027
- Sample: RVFI retirement; condition: decoded Zcb instruction, rvfi_trap == 0; anti-vacuity: Zcb is a small encoding space; load sign and address alignment come from rvfi_mem_addr/rdata so a hit proves the access happened with that data.
- Coverpoints:
  - cp_insn = decoded: bins c_lbu{}, c_lhu{}, c_lh{}, c_sb{}, c_sh{}, c_zext_b{}, c_sext_b{}, c_zext_h{}, c_sext_h{}, c_not{}, c_mul{}
  - cp_uimm_b = uimm, iff c.lbu/c.sb: bins u0{0}, u1{1}, u2{2}, u3{3}
  - cp_uimm_h = uimm, iff c.lhu/c.lh/c.sh: bins u0{0}, u2{2}
  - cp_data_sign = msb of the loaded byte/half, iff c.lbu/c.lhu/c.lh: bins pos{0}, neg{1}
  - cp_alu_operand = class(rvfi_rs1_rdata), iff ALU forms: bins bit7_set{bit 7 set, bit 15 clear}, bit7_clear{bits 7 and 15 clear}, bit15_set{bit 15 set}, zero{0}, all_ones{0xFFFFFFFF}, rand{default}
  - cp_addr_align = rvfi_mem_addr[1:0], iff c.lhu/c.lh/c.sh: bins aligned{00, 10}, mis1{01: misaligned, one word access with be 0110}, mis3{11: crosses the word boundary, split into two bus accesses (rtl/ibex_load_store_unit.sv:403-405)}
  - cp_regs = (rsd' == rs2'), iff c.mul: bins same{1}, distinct{0}
- Crosses:
  - cr_ls_b = cp_insn x cp_uimm_b: bins auto{all combinations}; ignore non-byte forms: guarded
  - cr_ls_h = cp_insn x cp_uimm_h: bins auto{all combinations}; ignore non-half forms: guarded
  - cr_load_sign = cp_insn x cp_data_sign: bins auto{all combinations}; ignore non-loads: guarded
  - cr_alu_operand = cp_insn x cp_alu_operand: bins auto{all combinations}; ignore non-ALU forms: guarded
  - cr_half_misaligned = cp_insn x cp_addr_align: bins auto{all combinations}; ignore non-half forms: guarded
- Adopted (riscv-dv): none
- TP items: TP-CMP-034, TP-CMP-036, TP-CMP-038, TP-CMP-070, TP-MUL-027, TP-BIT-009, TP-BIT-010

### CG-CMP-006: gen_cg_cmp_zcmp_pushpop
- Features: F-CMP-039, F-CMP-040, F-CMP-041, F-CMP-042, F-CMP-043, F-CMP-045, F-CMP-046, F-CMP-047, F-CMP-048, F-CMP-049, F-CMP-055, F-CMP-062, F-CMP-064, F-CMP-065, F-CMP-067
- Sample: RVFI retirement with rvfi_ext_expanded_insn_last == 1 of a cm.push/cm.pop/cm.popret/cm.popretz whose whole micro-op sequence retired without trap; condition: the monitor has collected every micro-op since the first rvfi_ext_expanded_insn_valid of this PC; anti-vacuity: only completed sequences sample here (interrupted/faulting ones go to CG-CMP-008); the ok-coverpoints are set only when the collected sequence matched the prediction.
- Coverpoints:
  - cp_insn = rvfi_ext_expanded_insn decoded: bins cm_push{}, cm_pop{}, cm_popret{}, cm_popretz{}
  - cp_rlist = instr[7:4]: bins r4{4}, r5{5}, r6{6}, r7{7}, r8{8}, r9{9}, r10{10}, r11{11}, r12{12}, r13{13}, r14{14}, r15{15}
  - cp_spimm = instr[3:2]: bins s0{0}, s1{1}, s2{2}, s3{3}
  - cp_stack_adj = cm_stack_adj(rlist, spimm): bins a16{16}, a32{32}, a48{48}, a64{64}, a80{80}, a96{96}, a112{112}
  - cp_sp_align = x2[1:0] before the instruction: bins aligned{00}, mis1{01}, mis2{10}, mis3{11}
  - cp_sp_wrap = address arithmetic crossing 0: bins none{no wrap}, push_below_zero{sp < 4*N: a store address wraps}, pop_above_max{sp + stack_adj >= 2^32}
  - cp_uop_count_ok = observed micro-op count == N+1 (push/pop), N+2 (popret), N+3 (popretz): bins yes{1}
  - cp_order_ok = store/load register order highest-first and addresses sp-4k / sp+adj-4k as predicted: bins yes{1}
  - cp_rvfi_tags_ok = expanded_valid on all micro-ops, last only on the final one, intermediate pc_wdata == pc_rdata, rvfi_insn == synthesized 32-bit: bins yes{1}
  - cp_minstret_once = minstret delta over the instruction == 1: bins yes{1}
  - cp_ret_align = loaded ra[1:0], iff popret/popretz: bins word{00}, half{10}, odd{x1}
  - cp_dmem_delay = dbus monitor rvalid latency class during the sequence: bins min1{1}, short{[2:4]}, long{[5:$]}, mixed{varies} [operand-only: canonical CG-REG (xcut) knob:dmem_rvalid_delay]
  - cp_dummy_en = cpuctrlsts.dummy_instr_en (TB CSR model) during the sequence: bins off{0}, on{1}
- Crosses:
  - cr_insn_rlist_spimm = cp_insn x cp_rlist x cp_spimm: bins auto{all combinations}
  - cr_insn_sp_align = cp_insn x cp_sp_align: bins auto{all combinations}
  - cr_insn_wrap = cp_insn x cp_sp_wrap: bins push_below_zero{cm_push, push_below_zero}, pop_above_max{cm_pop, pop_above_max}, popret_above_max{cm_popret, pop_above_max}, popretz_above_max{cm_popretz, pop_above_max}; ignore push/pop_above_max and pop-family/push_below_zero: direction mismatch; ignore none: not a corner
  - cr_ret_align = cp_insn x cp_ret_align: bins auto{all combinations}; ignore push/pop: guarded
  - cr_insn_delay = cp_insn x cp_dmem_delay: bins auto{all combinations}
  - cr_popret_r4 = cp_insn x cp_rlist: bins popret_r4{cm_popret, r4}, popretz_r4{cm_popretz, r4}; ignore other combinations: covered by cr_insn_rlist_spimm
  - cr_insn_dummy = cp_insn x cp_dummy_en: bins auto{all combinations} (a completed sequence under dummy insertion pressure, boundary-derived: the B8 stimulus condition of TP-CMP-065)
- Adopted (riscv-dv): none
- TP items: TP-CMP-039, TP-CMP-040, TP-CMP-041, TP-CMP-042, TP-CMP-043, TP-CMP-045, TP-CMP-046, TP-CMP-047, TP-CMP-048, TP-CMP-049, TP-CMP-055, TP-CMP-063, TP-CMP-065, TP-CMP-066, TP-CMP-068, TP-CMP-071

### CG-CMP-007: gen_cg_cmp_zcmp_mv
- Features: F-CMP-050, F-CMP-051, F-CMP-052, F-CMP-053, F-CMP-065, F-CMP-068
- Sample: RVFI retirement; condition: rvfi_ext_expanded_insn_last == 1 and the synthesized rvfi_insn decodes as cm.mvsa01/cm.mva01s (both micro-ops collected since the first rvfi_ext_expanded_insn_valid of this PC); anti-vacuity: the two-move sequence is identified from the RVFI tags; a hit proves both moves retired with the sampled register pair.
- Coverpoints:
  - cp_insn = decoded: bins cm_mvsa01{}, cm_mva01s{}
  - cp_r1s = instr[9:7]: bins s0{0}, s1{1}, s2{2}, s3{3}, s4{4}, s5{5}, s6{6}, s7{7}
  - cp_r2s = instr[4:2]: bins s0{0}, s1{1}, s2{2}, s3{3}, s4{4}, s5{5}, s6{6}, s7{7}
  - cp_equal = (r1s == r2s): bins no{0}, yes{1}
  - cp_src_values = a0 vs a1 (mvsa01) or r1s vs r2s (mva01s) values: bins distinct{differ}, same{equal}
  - cp_b2b = neighbouring instruction: bins mvsa01_then_mva01s{}, mva01s_then_mvsa01{}, none{default}
  - cp_hazard_src = source register written by the immediately preceding instruction: bins load_prev{load}, alu_prev{ALU}, none{default}
  - cp_uop_count_ok = two micro-ops, first tagged COMMIT-equivalent (no interrupt between them observed): bins yes{1}
- Crosses:
  - cr_insn_r1_r2 = cp_insn x cp_r1s x cp_r2s: bins auto{all combinations}; ignore cm_mvsa01 with r1s == r2s: reserved encoding (zcmp.adoc norm:cm-mvsa01_res, bug candidate B4), owned by cr_insn_equal.cm_mvsa01_yes (cm.mva01s has no such constraint)
  - cr_insn_equal = cp_insn x cp_equal: bins auto{all combinations}
  - cr_insn_hazard = cp_insn x cp_hazard_src: bins auto{all combinations}
  - cr_insn_b2b = cp_insn x cp_b2b: bins auto{all combinations}; ignore none: not a corner
- Adopted (riscv-dv): none
- TP items: TP-CMP-050, TP-CMP-051, TP-CMP-052, TP-CMP-053, TP-CMP-055, TP-CMP-066, TP-CMP-069, TP-CMP-071

### CG-CMP-008: gen_cg_cmp_zcmp_events
- Features: F-CMP-056, F-CMP-057, F-CMP-058, F-CMP-059, F-CMP-060, F-CMP-061, F-CMP-062, F-CMP-063,
  F-CMP-064, F-CMP-039 (parent of folded bins hosted here)
- Sample: monitor event "Zcmp sequence disturbed": an expansion is in flight (rvfi_ext_expanded_insn_valid seen without _last for this PC) and one of: a micro-op retires with rvfi_trap == 1; the next retirement has rvfi_intr == 1 or enters debug mode before _last; the dummy-instruction probe fires while the expansion is in flight; also samples the deferred case (event pin asserted mid-sequence, taken only after _last) and the pre-micro-op case (a trigger match on the cm.* PC itself enters debug before micro-op 0: the first debug-ROM record follows the previous instruction's record with no micro-op of that PC in between, X-19 (a)); condition: an expansion is in flight for this PC (rvfi_ext_expanded_insn_valid seen, _last not yet seen) AND one of the listed events is observed (rvfi_trap == 1 on a micro-op; rvfi_intr == 1 or rvfi_ext_debug_mode rising on the next retirement; a pin asserted inside the sequence window; probe P1 firing); anti-vacuity: requires an actual in-flight expansion plus an event, both derived from observed transactions; a hit proves the event landed at the recorded micro-op index/phase.
- Coverpoints:
  - cp_insn = decoded: bins cm_push{}, cm_pop{}, cm_popret{}, cm_popretz{}, cm_mvsa01{}, cm_mva01s{}
  - cp_event = kind: bins irq{external/timer/software/fast}, nmi{irq_nm_i}, debug_req{debug_req_i}, step{dcsr.step}, trigger{tdata2 match on the cm.* PC or next PC}, store_fault_pmp{}, store_fault_bus{data_err_i}, load_fault_pmp{}, load_fault_bus{}, dummy_inserted{probe P1} [probe-gated (P1), not in manifest: dummy_inserted]
  - cp_uop_idx = index of the micro-op in ID when the event arrived / that faulted: bins i0{0}, i1{1}, i2{2}, i3{3}, i4{4}, i5{5}, i6{6}, i7{7}, i8{8}, i9{9}, i10{10}, i11{11}, i12{12}, i13{13}, i14{14}, i15{15}
  - cp_phase = phase of that micro-op: bins ls_phase{store/load micro-op}, commit_phase{addi sp / li a0 / first move}, last_uop{final micro-op}, none{no micro-op in flight: the event pre-empted micro-op 0}
  - cp_outcome = derived: bins taken_between{event taken before _last, sequence abandoned}, deferred{event taken after _last}, trap_on_uop{micro-op retired with rvfi_trap}, pre_uop0{debug entry before micro-op 0: no micro-op of the cm.* PC retired, dpc = cm.* PC}
  - cp_reexec = after the handler, the same cm.* PC re-executes from micro-op 0 (repeated stores/loads observed): bins yes{1}, na{deferred: no re-execution}
  - cp_mepc_ok = mepc read-back == cm.* PC (taken_between/trap) or == next PC (deferred): bins yes{1}
  - cp_sp_unchanged_ok = x2 unchanged after an abandoned sequence: bins yes{1}
  - cp_rlist_class = instr[7:4]: bins r4{4}, r5_14{[5:14]}, r15{15}
  - cp_mis_half = faulting half of a misaligned micro-op, iff sp misaligned and fault: bins first{first half}, second{second half}
- Crosses:
  - cr_insn_event = cp_insn x cp_event: bins auto{all combinations}; ignore load faults on cm_push, store faults on pop-family, any fault on mv forms: no such access; the dummy_inserted bins are probe-gated (P1), not in manifest
  - cr_event_phase_outcome = cp_event x cp_phase x cp_outcome: bins irq_ls_taken{irq, ls_phase, taken_between}, irq_commit_deferred{irq, commit_phase, deferred}, irq_last_deferred{irq, last_uop, deferred}, nmi_ls_taken{nmi, ls_phase, taken_between}, nmi_commit_deferred{nmi, commit_phase, deferred}, debug_ls_deferred{debug_req, ls_phase, deferred}, debug_commit_deferred{debug_req, commit_phase, deferred}, step_deferred{step, last_uop, deferred}, trigger_deferred{trigger, last_uop, deferred}, nmi_last_deferred{nmi, last_uop, deferred}, trigger_pre_uop0{trigger, none, pre_uop0}, store_fault_pmp_trap{store_fault_pmp, ls_phase, trap_on_uop}, store_fault_bus_trap{store_fault_bus, ls_phase, trap_on_uop}, load_fault_pmp_trap{load_fault_pmp, ls_phase, trap_on_uop}, load_fault_bus_trap{load_fault_bus, ls_phase, trap_on_uop}, dummy_ls{dummy_inserted, ls_phase, any}, dummy_commit{dummy_inserted, commit_phase, any}; ignore irq/nmi taken in commit_phase and debug taken_between: blocked by the RTL rule (a hit is a checker failure); irq_last_deferred / nmi_last_deferred are the k >= N-2 outcomes of TP-CMP-056 (the LAST micro-op already in ID completes, C-3) and irq_commit_deferred / nmi_commit_deferred those of TP-CMP-057; dummy_ls and dummy_commit are probe-gated (P1), not in manifest
  - cr_fault_idx = cp_event x cp_uop_idx: bins auto{all combinations}; ignore non-fault events: covered by cr_irq_idx; ignore i13/i14/i15 for faults: at most 13 store/load micro-ops (rlist 15) can fault, the later indices are addi/li/ret
  - cr_irq_idx = cp_event x cp_uop_idx: bins auto{all combinations}; ignore events other than irq/nmi/debug_req: covered by cr_fault_idx
  - cr_insn_rlist_event = cp_insn x cp_rlist_class x cp_event: bins auto{all combinations}; ignore mv forms: no rlist; ignore load faults on cm_push and store faults on pop-family: no such access; dummy_inserted bins are probe-gated (P1), not in manifest
  - cr_mis_fault = cp_event x cp_mis_half: bins auto{all combinations}; ignore non-fault events: guarded
- Adopted (riscv-dv): none
- TP items: TP-CMP-056, TP-CMP-057, TP-CMP-058, TP-CMP-059, TP-CMP-060, TP-CMP-061, TP-CMP-062, TP-CMP-063, TP-CMP-064, TP-CMP-065, TP-CMP-071

### CG-CMP-009: gen_cg_cmp_zcmp_hazard
- Features: F-CMP-049, F-CMP-065, F-CMP-068, F-CMP-070
- Sample: RVFI retirement with rvfi_ext_expanded_insn_last == 1 of any cm.* instruction; condition: the monitor's instruction history identifies one of the listed neighbour patterns; anti-vacuity: the pattern requires a specific preceding/following retirement so it cannot fire on an isolated cm.*; a hit proves the hazard pattern executed.
- Coverpoints:
  - cp_hazard = pattern: bins store_same_slot_then_pop{sw to a slot the following cm.pop loads}, write_pushed_reg_then_push{ALU writes a register the following cm.push stores}, load_pushed_reg_then_push{load into a register the following cm.push stores}, load_then_mva01s{load into r1s'/r2s' then cm.mva01s}, popret_ra_fwd{retired: see ignore_bins}, popret_ra_deferred{cm.popret/popretz whose ra-load response arrived after the addi micro-op entered ID (dbus monitor): the addi starts deferred and the ret reads ra from the register file, C-9}, push_then_pop_b2b{cm.push then cm.pop}, pop_then_push_b2b{cm.pop then cm.push}, popret_then_target{cm.popret then the return target retires next}, popretz_then_target{cm.popretz then the return target retires next}, mvsa01_then_mva01s{}, popret_ft_cm{cm.popret whose PC+2 halfword is a cm.*}, popretz_ft_cm{cm.popretz whose PC+2 halfword is a cm.*}; ignore_bins popret_ra_fwd: the former 'ra still in WB when the ret enters ID' path does not exist (the addi cannot execute while the load is outstanding, rtl/ibex_id_stage.sv:1059-1062; loads are never forwarded, :1117-1118; rtl-arch T-053 TP-CMP-049)
  - cp_ft_kind = kind of the fall-through cm.* at PC+2, iff popret_ft_cm/popretz_ft_cm: bins cm_push{}, cm_pop{}, cm_popret{}, cm_popretz{}, cm_mvsa01{}, cm_mva01s{}
  - cp_ret_once = exactly one rvfi_ext_expanded_insn_last for the popret/popretz and the next rvfi_pc_rdata == ra target: bins yes{1}
  - cp_redirect_once = one ibus redirect for the ret (ibus monitor), iff icache_enable == 0: bins yes{1}
  - cp_rlist_class = instr[7:4]: bins r4{4}, r5_14{[5:14]}, r15{15}
  - cp_dmem_delay = dbus monitor rvalid latency class: bins min1{1}, short{[2:4]}, long{[5:$]} [operand-only: canonical CG-REG (xcut) knob:dmem_rvalid_delay]
  - cp_delta_uop = per-micro-op retire delta class over the sequence: bins all_one{every delta 1}, some_stall{a delta > 1}
- Crosses:
  - cr_hazard_rlist = cp_hazard x cp_rlist_class: bins auto{all combinations}; ignore mvsa01_then_mva01s and load_then_mva01s: mv has no rlist
  - cr_hazard_delay = cp_hazard x cp_dmem_delay: bins auto{all combinations}; ignore mvsa01_then_mva01s: no data access in the pattern; ignore popret_ra_deferred/min1: with the min1 response the ra data arrives in the cycle the addi enters ID, so no deferral occurs
  - cr_ft_kind = cp_hazard x cp_ft_kind: bins auto{all combinations}; ignore hazards other than popret_ft_cm/popretz_ft_cm: guarded
- Adopted (riscv-dv): none
- TP items: TP-CMP-049, TP-CMP-066, TP-CMP-069, TP-CMP-071, TP-CMP-073

### CG-CMP-010: gen_cg_cmp_zcmp_fetch_err
- Features: F-CMP-069
- Sample: RVFI retirement; condition: rvfi_trap == 1, the handler read-back gives mcause == 1 and the halfword at rvfi_pc_rdata is a Zcmp encoding (the monitor decodes the fetched halfword from the ibus stream, not from rvfi_insn, because the PMP path reports the synthesized micro-op); anti-vacuity: only an ibus-agent instr_err_i or a PMP execute denial on a Zcmp encoding produces the sample; the ok-coverpoints are recorded only when the predicted absence of data requests and the restart from micro-op 0 were observed.
- Coverpoints:
  - cp_insn = decoded halfword: bins cm_push{}, cm_pop{}, cm_popret{}, cm_popretz{}, cm_mvsa01{}, cm_mva01s{}
  - cp_err_kind = error source: bins bus{instr_err_i on the fetch}, pmp{PMP execute denied}
  - cp_expanded_tag = rvfi_ext_expanded_insn_valid on the trapping entry: bins bus_not_expanded{bus, 0}, pmp_expanded{pmp, 1 with rvfi_ext_expanded_insn_last 0}
  - cp_pc_align = rvfi_pc_rdata[1]: bins word{0}, half{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_reach = how the halfword was reached: bins sequential{fall-through}, jump_target{target of a taken CTI}
  - cp_no_dreq = no data_req_o between the previous retirement and the handler entry: bins yes{1}
  - cp_next_uop0 = the next cm.* (same PC after mret, or another) retires from micro-op 0 with its full count: bins yes{1}
  - cp_mtval_ok = handler read-back mtval == mepc == the cm.* PC: bins yes{1}
- Crosses:
  - cr_insn_err = cp_insn x cp_err_kind: bins auto{all combinations}
  - cr_err_align = cp_err_kind x cp_pc_align x cp_priv: bins auto{all combinations}
  - cr_err_reach = cp_err_kind x cp_reach: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-CMP-072

---------------------------------------------------------------------------------------------------
## AREA BIT

### CG-BIT-001: gen_cg_bit_zba_zbb_ops
- Features: F-BIT-002, F-BIT-003, F-BIT-004, F-BIT-007, F-BIT-008, F-BIT-009, F-BIT-010, F-BIT-011, F-BIT-038
- Sample: RVFI retirement; condition: decoded sh1add/sh2add/sh3add/andn/orn/xnor/min/max/minu/maxu/sext.b/sext.h/pack/packu/packh (zext.h = pack with rs2 == x0), rvfi_trap == 0; anti-vacuity: Zb* funct7 values are excluded from base ALU sampling and vice versa; a hit proves the op retired with the sampled operand classes.
- Coverpoints:
  - cp_op = decoded: bins sh1add{}, sh2add{}, sh3add{}, andn{}, orn{}, xnor{}, min{}, max{}, minu{}, maxu{}, sext_b{}, sext_h{}, zext_h{pack, rs2 == x0}, pack{rs2 != x0}, packu{}, packh{}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, e0000000{0xE0000000}, byte_msb{bit 7 set, bit 15 clear}, half_msb{bit 15 set, bit 7 clear}, pos_rand{default bit31 clear}, neg_rand{default bit31 set}
  - cp_rs2_class = class(rvfi_rs2_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, one{1}, pos_rand{default bit31 clear}, neg_rand{default bit31 set}
  - cp_eq_operands = (rs1_rdata == rs2_rdata): bins no{0}, yes{1}
  - cp_same_regs = index relation: bins rs1_eq_rs2{rs1 == rs2 != rd}, all_same{rs1 == rs2 == rd != 0}, distinct{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_sign_pair = bit31 of rs1,rs2: bins pp{00}, pn{01}, np{10}, nn{11}
  - cp_result_class = class(rvfi_rd_wdata): bins zero{0}, all_ones{0xFFFFFFFF}, int_min{0x80000000}, int_max{0x7FFFFFFF}, other{default}
  - cp_wrap = carry out of rs2 + (rs1 << n), iff shNadd: bins no{0}, yes{1}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_rs2 = cp_op x cp_rs2_class: bins auto{all combinations}; ignore sext_b/sext_h/zext_h: unary
  - cr_op_eq = cp_op x cp_eq_operands: bins auto{all combinations}; ignore unary ops: guarded
  - cr_minmax_sign = cp_op x cp_sign_pair: bins auto{all combinations}; ignore ops other than min/max/minu/maxu: sign only matters for compares
  - cr_shadd_wrap = cp_op x cp_wrap: bins auto{all combinations}; ignore non-shNadd: guarded
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
  - cr_op_same = cp_op x cp_same_regs: bins auto{all combinations}; ignore sext_b/sext_h/zext_h with rs1_eq_rs2 and all_same: unary (the rs2 field is the function code or x0)
- Adopted (riscv-dv): cp_eq_operands coincides with riscv_instr_cover_group.sv min_cg/max_cg/minu_cg/maxu_cg.cp_rs1_eq_rs2 (riscv-dv declares the equal bin only; the no bin is added) (spec-derived, independently derived from the ISA text; adopted=0); cp_sign_pair for min/max is the sign projection of their cp_rs1_gt_rs2 comparison (spec-derived, independently derived from the ISA text; adopted=0)
- TP items: TP-BIT-002, TP-BIT-003, TP-BIT-004, TP-BIT-007, TP-BIT-008, TP-BIT-009, TP-BIT-010, TP-BIT-011, TP-BIT-038, TP-BIT-041

### CG-BIT-002: gen_cg_bit_count
- Features: F-BIT-005, F-BIT-006, F-BIT-038
- Sample: RVFI retirement; condition: decoded clz/ctz/cpop (OP-IMM funct3 001, instr[31:20] 0x600/0x601/0x602), rvfi_trap == 0; anti-vacuity: three funct12 values; single-bit position is derived from the operand so a hit proves the sampled input reached the counter.
- Coverpoints:
  - cp_op = instr[31:20]: bins clz{0x600}, ctz{0x601}, cpop{0x602}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, lsb_only{1}, single_other{exactly one bit set, not bit 0/31}, alt_5{0x55555555}, alt_a{0xAAAAAAAA}, int_max{0x7FFFFFFF}, rand{default}
  - cp_single_pos = position of the set bit, iff exactly one bit set: bins p0{0}, p1{1}, p2{2}, p3{3}, p4{4}, p5{5}, p6{6}, p7{7}, p8{8}, p9{9}, p10{10}, p11{11}, p12{12}, p13{13}, p14{14}, p15{15}, p16{16}, p17{17}, p18{18}, p19{19}, p20{20}, p21{21}, p22{22}, p23{23}, p24{24}, p25{25}, p26{26}, p27{27}, p28{28}, p29{29}, p30{30}, p31{31}
  - cp_result = rvfi_rd_wdata: bins r0{0}, r1{1}, r16{16}, r31{31}, r32{32}, other{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_op_single = cp_op x cp_single_pos: bins auto{all combinations}
  - cr_op_result = cp_op x cp_result: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none taken; cp_result point bins r1 / r16 / r31 lie inside the adopted range bins of CG-ADOPT-006.cp_bitcount_result (clz_cg/ctz_cg/cpop_cg CP_VALUE_RANGE) and are not the same partition; r0 and r32 are F-BIT-006 boundary bins owned here (cross-reference, S-9)
- TP items: TP-BIT-005, TP-BIT-006, TP-BIT-038, TP-BIT-041

### CG-BIT-003: gen_cg_bit_rotate_shiftones
- Features: F-BIT-012, F-BIT-013, F-BIT-022, F-BIT-023, F-BIT-036, F-BIT-037, F-BIT-038
- Sample: RVFI retirement; condition: decoded rol/ror/rori/slo/sro/sloi/sroi, rvfi_trap == 0; anti-vacuity: the amount is the effective rs2[4:0]/imm[4:0]; a hit proves the sampled amount/operand executed. Rotate timing (d2) is owned by CG-BIT-010 (cr_op_delta_clean.rol_d2/ror_d2/rori_d2) and not repeated here; the lenient-bit coverpoints are guarded to their op, so no op x bits cross is declared.
- Coverpoints:
  - cp_op = decoded: bins rol{}, ror{}, rori{}, slo{}, sro{}, sloi{}, sroi{}
  - cp_amount = rs2[4:0] or imm[4:0]: bins a0{0}, a1{1}, mid{[2:30]}, a31{31}
  - cp_rs2_upper = rvfi_rs2_rdata, iff register form: bins zero{rs2[31:5] == 0}, is32{32}, all_ones{0xFFFFFFFF}, other_nonzero{default}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, msb_only{0x80000000}, lsb_only{1}, rand{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_sloi_bits = instr[26:25], iff sloi: bins b00{00}, b01{01}, b10{10}, b11{11}
  - cp_sroi_bit25 = instr[25], iff sroi: bins b0{0}, b1{1}
- Crosses:
  - cr_op_amount = cp_op x cp_amount: bins auto{all combinations}
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_reg_upper = cp_op x cp_rs2_upper: bins auto{all combinations}; ignore immediate forms: guarded
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-012, TP-BIT-013, TP-BIT-022, TP-BIT-023, TP-BIT-036, TP-BIT-037, TP-BIT-038, TP-BIT-041

### CG-BIT-004: gen_cg_bit_perm
- Features: F-BIT-014, F-BIT-015, F-BIT-016, F-BIT-024, F-BIT-037, F-BIT-038
- Sample: RVFI retirement; condition: decoded grev/grevi/gorc/gorci/shfl/shfli/unshfl/unshfli, rvfi_trap == 0; anti-vacuity: control value comes from rs2[4:0]/[3:0] or the immediate; a hit proves that control value executed on the sampled operand.
- Coverpoints:
  - cp_op = decoded: bins grev{}, grevi{}, gorc{}, gorci{}, shfl{}, shfli{}, unshfl{}, unshfli{}
  - cp_grev_ctrl = control[4:0], iff grev/grevi/gorc/gorci: bins c0{0}, c1{1}, c2{2}, c3{3}, c4{4}, c5{5}, c6{6}, c7{7}, c8{8}, c9{9}, c10{10}, c11{11}, c12{12}, c13{13}, c14{14}, c15{15}, c16{16}, c17{17}, c18{18}, c19{19}, c20{20}, c21{21}, c22{22}, c23{23}, c24{24}, c25{25}, c26{26}, c27{27}, c28{28}, c29{29}, c30{30}, c31{31}
  - cp_shfl_ctrl = control[3:0], iff shfl family: bins c0{0}, c1{1}, c2{2}, c3{3}, c4{4}, c5{5}, c6{6}, c7{7}, c8{8}, c9{9}, c10{10}, c11{11}, c12{12}, c13{13}, c14{14}, c15{15}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, bytes_01020304{0x01020304}, single_bit{exactly one bit set}, rand{default}
  - cp_rs2_upper = rs2 bits above the control field, iff register form: bins zero{0}, nonzero{1}
  - cp_bit25 = instr[25], iff grevi/gorci/shfli/unshfli: bins b0{0}, b1{1}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_grev_ctrl = cp_op x cp_grev_ctrl: bins auto{all combinations}; ignore shfl family: guarded
  - cr_shfl_ctrl = cp_op x cp_shfl_ctrl: bins auto{all combinations}; ignore grev family: guarded
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_lenient = cp_op x cp_bit25: bins grevi_b1{grevi, b1}, gorci_b1{gorci, b1}, shfli_b1{shfli, b1}, unshfli_b1{unshfli, b1}; ignore b0 and register forms: canonical
  - cr_reg_upper = cp_op x cp_rs2_upper: bins auto{all combinations}; ignore immediate forms: guarded
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): cp_grev_ctrl c0..c31 coincides with riscv_instr_cover_group.sv grev_cg/grevi_cg CP_VALUE_RANGE(reverse_mode, 0, XLEN-1) and cp_shfl_ctrl c0..c15 with shfl_cg/unshfl_cg CP_VALUE_RANGE(shuffle_mode, 0, XLEN/2-1) (spec-derived, independently derived from the ISA text; adopted=0)
- TP items: TP-BIT-014, TP-BIT-015, TP-BIT-016, TP-BIT-024, TP-BIT-037, TP-BIT-038, TP-BIT-041

### CG-BIT-005: gen_cg_bit_xperm
- Features: F-BIT-025, F-BIT-026, F-BIT-038
- Sample: RVFI retirement; condition: decoded xperm.n/xperm.b/xperm.h, rvfi_trap == 0; anti-vacuity: the index pattern is classified from rvfi_rs2_rdata per lane width; a hit proves the sampled pattern was looked up.
- Coverpoints:
  - cp_op = decoded: bins xperm_n{}, xperm_b{}, xperm_h{}
  - cp_index_pattern = rs2 lanes: bins identity{lane i selects i}, reverse{lane i selects N-1-i}, all_same{all lanes select one index}, all_oob{every lane out of range}, mixed_oob{some lanes out of range}, rand{default in range}
  - cp_oob_lanes = number of out-of-range lanes: bins none{0}, some{[1:N-1]}, all{N}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, distinct_lanes{every lane value unique}, rand{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_op_pattern = cp_op x cp_index_pattern: bins auto{all combinations}
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}
  - cr_op_oob = cp_op x cp_oob_lanes: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-025, TP-BIT-026, TP-BIT-038, TP-BIT-041

### CG-BIT-006: gen_cg_bit_sbit
- Features: F-BIT-017, F-BIT-018, F-BIT-019, F-BIT-038
- Sample: RVFI retirement; condition: decoded bclr/bset/binv/bext/bclri/bseti/binvi/bexti, rvfi_trap == 0; anti-vacuity: the prior bit state is read from rvfi_rs1_rdata at the effective index; a hit proves the op acted on a bit in the sampled state.
- Coverpoints:
  - cp_op = decoded: bins bclr{}, bset{}, binv{}, bext{}, bclri{}, bseti{}, binvi{}, bexti{}
  - cp_index = rs2[4:0] or imm[4:0]: bins i0{0}, mid{[1:30]}, i31{31}
  - cp_rs2_upper = rvfi_rs2_rdata, iff register form: bins zero{rs2[31:5] == 0}, all_ones{0xFFFFFFFF}, other_nonzero{default}
  - cp_prior_bit = rs1[index]: bins clear{0}, set{1}
  - cp_operand = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, rand{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_binv_twice = binv/binvi followed by binv/binvi on the same rd and index: bins yes{1}
- Crosses:
  - cr_op_index_prior = cp_op x cp_index x cp_prior_bit: bins auto{all combinations}
  - cr_reg_upper = cp_op x cp_rs2_upper: bins auto{all combinations}; ignore immediate forms: guarded
  - cr_op_operand = cp_op x cp_operand: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-017, TP-BIT-018, TP-BIT-019, TP-BIT-038, TP-BIT-041

### CG-BIT-007: gen_cg_bit_clmul_crc
- Features: F-BIT-020, F-BIT-021, F-BIT-032, F-BIT-033, F-BIT-036, F-BIT-038
- Sample: RVFI retirement; condition: decoded clmul/clmulh/clmulr or crc32.b/.h/.w or crc32c.b/.h/.w, rvfi_trap == 0; anti-vacuity: operand classes from rvfi_rs1/rs2_rdata; a hit proves the sampled operand class executed. CRC timing (d2) is owned by CG-BIT-010 (cr_op_delta_clean.crc32*_d2) and not repeated here.
- Coverpoints:
  - cp_op = decoded: bins clmul{}, clmulh{}, clmulr{}, crc32_b{}, crc32_h{}, crc32_w{}, crc32c_b{}, crc32c_h{}, crc32c_w{}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, single_bit{exactly one bit set}, high_only{bits above the op's data width set, low bits zero}, low_only{only bits inside the op's data width set}, rand{default}
  - cp_rs2_class = class(rvfi_rs2_rdata), iff clmul family: bins zero{0}, one{1}, all_ones{0xFFFFFFFF}, single_bit{exactly one bit set}, rand{default}
  - cp_bit_sum = i + j for single-bit rs1 (1<<i) and rs2 (1<<j), iff clmul family: bins lt32{[0:31]}, ge32{[32:62]}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_op_rs1 = cp_op x cp_rs1_class: bins auto{all combinations}; ignore high_only/low_only for clmul family: width classes are for crc; ignore crc32_w/crc32c_w with high_only: no bits above the 32-bit width
  - cr_clmul_rs2 = cp_op x cp_rs2_class: bins auto{all combinations}; ignore crc ops: guarded
  - cr_clmul_bitsum = cp_op x cp_bit_sum: bins auto{all combinations}; ignore crc ops: guarded
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-020, TP-BIT-021, TP-BIT-032, TP-BIT-033, TP-BIT-036, TP-BIT-038, TP-BIT-041

### CG-BIT-008: gen_cg_bit_ternary
- Features: F-BIT-027, F-BIT-028, F-BIT-029, F-BIT-036, F-BIT-038, F-BIT-039, F-ISA-012
- Sample: RVFI retirement; condition: decoded cmov/cmix/fsl/fsr/fsri (OP with instr[26] == 1 and funct3 001/101; OP-IMM funct3 101 with instr[26] == 1), rvfi_trap == 0; anti-vacuity: rs3 comes from rvfi_rs3_addr/rdata, the amount from rs2[5:0]/imm[5:0]; a hit proves the sampled ternary case executed with rs3 read. Ternary timing (d2) is owned by CG-BIT-010 (cr_op_delta_clean.cmov_d2 etc.); cp_cmov_ctrl/cp_cmix_mask are guarded to their op, so no op x ctrl cross is declared.
- Coverpoints:
  - cp_op = decoded: bins cmov{}, cmix{}, fsl{}, fsr{}, fsri{}
  - cp_cmov_ctrl = class(rvfi_rs2_rdata), iff cmov: bins zero{0}, one{1}, msb_only{0x80000000}, nonzero_rand{default}
  - cp_cmix_mask = class(rvfi_rs2_rdata), iff cmix: bins zero{0}, all_ones{0xFFFFFFFF}, alt{0x55555555 or 0xAAAAAAAA}, rand{default}
  - cp_funnel_amt = rs2[5:0] or imm[5:0], iff fsl/fsr/fsri: bins a0{0}, a1{1}, mid_lo{[2:30]}, a31{31}, a32{32}, a33{33}, mid_hi{[34:62]}, a63{63}
  - cp_fsri_hi5 = instr[31:27] (the rs3 field), iff fsri: bins srli_pattern{00000}, srai_pattern{01000}, other{default}
  - cp_rs2_upper6 = rs2[31:6], iff fsl/fsr: bins zero{0}, nonzero{1}
  - cp_rs3_choice = rvfi_rs3_addr relation: bins eq_rs1{rs3 == rs1}, eq_rs2{rs3 == rs2}, eq_rd{rs3 == rd != 0}, x0{rs3 == 0}, distinct{default}
  - cp_rs1_rs3_class = (rs1_rdata, rs3_rdata): bins zero_ones{rs1 0, rs3 0xFFFFFFFF}, ones_zero{rs1 0xFFFFFFFF, rs3 0}, equal{rs1 == rs3}, rand{default}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_funnel_amt = cp_op x cp_funnel_amt: bins auto{all combinations}; ignore cmov/cmix: guarded
  - cr_op_rs3 = cp_op x cp_rs3_choice: bins auto{all combinations}
  - cr_funnel_upper = cp_op x cp_rs2_upper6: bins fsl_nonzero{fsl, nonzero}, fsr_nonzero{fsr, nonzero}; ignore other combinations: guarded / canonical
  - cr_op_rs13 = cp_op x cp_rs1_rs3_class: bins auto{all combinations}
  - cr_op_rd_x0 = cp_op x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-027, TP-BIT-028, TP-BIT-029, TP-BIT-036, TP-BIT-038, TP-BIT-039, TP-BIT-041, TP-ISA-012

### CG-BIT-009: gen_cg_bit_bfp
- Features: F-BIT-030, F-BIT-031, F-BIT-038
- Sample: RVFI retirement; condition: decoded bfp (OP f7 0100100 f3 111), rvfi_trap == 0; anti-vacuity: len/off/data are fields of rvfi_rs2_rdata; a hit proves that control word executed; cp_delta is `iff gap_clean` and d1 is the D8 witness (bfp is single-cycle in the RTL).
- Coverpoints:
  - cp_len = rs2[27:24]: bins l0{0}, l1{1}, mid{[2:14]}, l15{15}
  - cp_off = rs2[20:16]: bins o0{0}, mid{[1:15]}, o16{16}, mid_hi{[17:30]}, o31{31}
  - cp_overflow = (off + len_eff > 32) with len_eff = 16 when len == 0: bins no{0}, yes{1}
  - cp_data_class = rs2[15:0] vs len: bins zero{0}, all_ones{0xFFFF}, above_len_set{bits above len_eff set}, rand{default}
  - cp_rs1_class = class(rvfi_rs1_rdata): bins zero{0}, all_ones{0xFFFFFFFF}, rand{default}
  - cp_ctrl_upper = rs2[31:28] and rs2[23:21]: bins zero{0}, nonzero{1}
  - cp_delta = retire delta from the previous retirement, iff gap_clean: bins d1{1}, d2plus{[2:$]}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
- Crosses:
  - cr_len_off = cp_len x cp_off: bins auto{all combinations}
  - cr_overflow_len = cp_overflow x cp_len: bins auto{all combinations}; ignore no: not the corner; ignore yes/l1: off + 1 > 32 needs off == 32, outside the 5-bit field
  - cr_data_rs1 = cp_data_class x cp_rs1_class: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-030, TP-BIT-031, TP-BIT-038, TP-BIT-041

### CG-BIT-010: gen_cg_bit_multicycle_pipe
- Features: F-BIT-036, F-BIT-039, F-BIT-041, F-BIT-012, F-BIT-027, F-BIT-028, F-BIT-032
- Sample: RVFI retirement; condition: decoded two-cycle Zb* op (rol/ror/rori/cmov/cmix/fsl/fsr/fsri/crc32.b/.h/.w/crc32c.b/.h/.w), rvfi_trap == 0, and not the first retirement after reset (the delta and the dependency class need a previous retirement); the coverpoints discriminate on the previous/next retirement's dependency, the pin timestamps inside the op's window, wb_busy and the clean delta, so the sample is never a tautology; anti-vacuity: the dependency class needs a preceding writer of the exact source register, the event class needs a pin assertion timestamped inside the op's two-cycle window, a clean d2 needs gap_clean and wb_busy == no; a hit proves the hazard/event/timing coincided with the op; cp_defer_cycles records the deferral W of the FIRST cycle behind an outstanding WB access (C-9: the op is held before its first cycle, never in its second, so the record delta is 2 + W). This group is the single owner of the two-cycle Zb* delta partition (CG-BIT-003/007/008 do not repeat it).
- Coverpoints:
  - cp_op_class = decoded: bins rot{rol/ror/rori}, ternary{cmov/cmix/fsl/fsr/fsri}, crc{crc32*}
  - cp_op = decoded: bins rol{}, ror{}, rori{}, cmov{}, cmix{}, fsl{}, fsr{}, fsri{}, crc32_b{}, crc32_h{}, crc32_w{}, crc32c_b{}, crc32c_h{}, crc32c_w{}
  - cp_prev_dep = previous retirement writes: bins alu_rs1{ALU writes rs1}, alu_rs2{ALU writes rs2}, alu_rs3{ALU writes rs3}, load_rs1{load writes rs1}, load_rs2{load writes rs2}, load_rs3{load writes rs3}, none{default}
  - cp_delta = retire delta from the previous retirement, iff gap_clean: bins d2{2}, d3plus{[3:$]}
  - cp_event_mid = pin asserted inside the two-cycle window: bins none{0}, irq{irq line}, debug_req{debug_req_i}, nmi{irq_nm_i}
  - cp_wb_busy = dbus monitor: data access outstanding when the op entered ID: bins no{0}, yes{1}
  - cp_defer_cycles = retire delta - 2 = W, the deferral of the first cycle behind the outstanding access (dbus monitor), iff wb_busy: bins h1{1}, h2_4{[2:4]}, h5plus{[5:$]} (formerly cp_hold_cycles)
  - cp_wb_kind = kind of the outstanding access, iff wb_busy: bins load{}, store{}
  - cp_fetch_stall = ibus monitor: bins no{0}, yes{1}
  - cp_rd_x0 = (rvfi_rd_addr == 0): bins no{0}, yes{1}
  - cp_next_dep = next retirement reads rd: bins no{0}, yes{1}
- Crosses:
  - cr_class_prev = cp_op_class x cp_prev_dep: bins auto{all combinations}; ignore rs3 dependencies for rot/crc: no rs3
  - cr_class_event = cp_op_class x cp_event_mid: bins auto{all combinations}
  - cr_class_wb = cp_op_class x cp_wb_busy: bins auto{all combinations}
  - cr_class_defer = cp_op_class x cp_defer_cycles x cp_wb_kind: bins auto{all combinations}; ignore wb_busy no: guarded (formerly cr_class_hold)
  - cr_class_delta_clean = cp_op_class x cp_delta x cp_fetch_stall x cp_wb_busy: bins rot_d2{rot, d2, no, no}, ternary_d2{ternary, d2, no, no}, crc_d2{crc, d2, no, no}; ignore other combinations: stall-dependent
  - cr_op_delta_clean = cp_op x cp_delta x cp_wb_busy: bins rol_d2{rol, d2, no}, ror_d2{ror, d2, no}, rori_d2{rori, d2, no}, cmov_d2{cmov, d2, no}, cmix_d2{cmix, d2, no}, fsl_d2{fsl, d2, no}, fsr_d2{fsr, d2, no}, fsri_d2{fsri, d2, no}, crc32_b_d2{crc32_b, d2, no}, crc32_h_d2{crc32_h, d2, no}, crc32_w_d2{crc32_w, d2, no}, crc32c_b_d2{crc32c_b, d2, no}, crc32c_h_d2{crc32c_h, d2, no}, crc32c_w_d2{crc32c_w, d2, no}; ignore d3plus and wb_busy yes: stall-dependent (covered by cr_class_defer)
  - cr_class_next = cp_op_class x cp_next_dep: bins auto{all combinations}
  - cr_class_rd_x0 = cp_op_class x cp_rd_x0: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-012, TP-BIT-027, TP-BIT-028, TP-BIT-032, TP-BIT-036, TP-BIT-039, TP-BIT-042, TP-BIT-043

### CG-BIT-011: gen_cg_bit_decode
- Features: F-BIT-001, F-BIT-013, F-BIT-019, F-BIT-024, F-BIT-034, F-BIT-035, F-BIT-037, F-BIT-040
- Sample: RVFI retirement; condition: decoded OP or OP-IMM encoding whose funct7/hi5 lies outside base-I/M (the Zb* decode space), or opcode OP-32/OP-IMM-32, or csrr misa; anti-vacuity: legality is decided by the monitor's ENC table; cp_legal_insn is `iff rvfi_trap == 0` and cp_illegal_class `iff rvfi_trap == 1`, so a hit in cp_legal_insn proves a legal Zb* encoding retired without trap and a hit in cp_illegal_class proves the illegal one trapped (a legal encoding trapping or an illegal one executing is a gen_isa_compare / gen_chk_bitmanip_ref failure, not a bin).
- Coverpoints:
  - cp_legal_insn = ENC table mnemonic, iff rvfi_trap == 0: bins sh1add{}, sh2add{}, sh3add{}, andn{}, orn{}, xnor{}, rol{}, ror{}, min{}, max{}, minu{}, maxu{}, pack{}, packu{}, packh{}, bclr{}, bset{}, binv{}, bext{}, bfp{}, grev{}, gorc{}, shfl{}, unshfl{}, xperm_n{}, xperm_b{}, xperm_h{}, slo{}, sro{}, clmul{}, clmulr{}, clmulh{}, cmix{}, cmov{}, fsl{}, fsr{}, sloi{}, bclri{}, bseti{}, binvi{}, shfli{}, clz{}, ctz{}, cpop{}, sext_b{}, sext_h{}, crc32_b{}, crc32_h{}, crc32_w{}, crc32c_b{}, crc32c_h{}, crc32c_w{}, fsri{}, sroi{}, rori{}, bexti{}, grevi{}, gorci{}, unshfli{}
  - cp_illegal_class = decoded, iff rvfi_trap == 1: bins bcompress{0000100/110}, bdecompress{0100100/110}, op32_any{opcode 0x3b}, opimm32_any{opcode 0x1b}, rori_bit25{}, bclri_bit25{}, bseti_bit25{}, binvi_bit25{}, bexti_bit25{}, shfli_bit26{}, opimm_001_hi5_other{OP-IMM f3 001 hi5 not in table}, opimm_101_hi5_other{OP-IMM f3 101 instr[26] 0 hi5 not in table}, opimm_0110000_rs2_other{hi5 01100 instr[26:20] not in table}, op_f7f3_other{OP funct7/funct3 not in table}
  - cp_mtval_ok = handler csrr mtval == the 32-bit word: bins yes{1}
  - cp_misa = csrr misa read-back bits: bins x_set{bit 23 == 1}, b_clear{bit 1 == 0}, m_set{bit 12 == 1}, c_set{bit 2 == 1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
- Crosses:
  - cr_illegal_priv = cp_illegal_class x cp_priv: bins auto{all combinations}
- Adopted (riscv-dv): none
- TP items: TP-BIT-001, TP-BIT-013, TP-BIT-019, TP-BIT-024, TP-BIT-030, TP-BIT-034, TP-BIT-035, TP-BIT-037, TP-BIT-040, TP-BIT-041

---------------------------------------------------------------------------------------------------
## AREA BTALU

### CG-BTALU-001: gen_cg_btalu_branch
- Features: F-BTALU-001, F-BTALU-005, F-BTALU-006, F-BTALU-007, F-BTALU-009, F-BTALU-015
- Sample: RVFI retirement; condition: decoded conditional branch (BRANCH funct3 not 010/011, or c.beqz/c.bnez), rvfi_trap == 0, and not the first retirement after reset (the delta needs a previous retirement); the coverpoints discriminate on the redirect delta (d1 vs d2 vs d3plus, conventions), DIT, the redirect, the counter increments, the WB wait and the previous CTI, so the sample is never a tautology; anti-vacuity: taken is derived from rvfi_pc_wdata, the redirect from an ibus request for the branch target (or pc + len) issued while the branch was in ID (sampled only with icache_enable == 0), the counter deltas from the hardwired rvfi_ext_mhpmcounters[8 - 3] / [9 - 3], the WB wait from the dbus monitor (a data access outstanding when the branch entered ID whose response arrived later: the branch waits in FIRST_CYCLE, C-10); a hit proves the sampled timing/redirect/count tuple was observed.
- Coverpoints:
  - cp_taken = (rvfi_pc_wdata != pc + len): bins no{0}, yes{1} [operand-only: canonical CG-ISA-007.cp_taken]
  - cp_direction = sign of imm: bins fwd{imm > 0}, bwd{imm < 0}, self{imm == 0}
  - cp_target_align = target[1]: bins word{0}, half{1} [operand-only: canonical CG-ISA-007.cp_target_align]
  - cp_distance = |imm|: bins short{[0:62]}, mid{[64:2046]}, far{[2048:4092]}, max_fwd{4094}, max_bwd{4096}
  - cp_dit = cpuctrlsts.data_ind_timing (TB CSR model): bins off{0}, on{1}
  - cp_delta = redirect delta rvfi_ext_mcycle(successor) - rvfi_ext_mcycle(branch) (for a not-taken branch under DIT = 0 this is its own retire delta; conventions), iff redirect_clean: bins d1{1}, d2{2}, d3plus{[3:$]}
  - cp_redirect = ibus monitor saw a non-sequential request (branch target, or a re-request of pc + len under DIT) issued while this branch was in ID, iff icache_enable == 0: bins no{0}, yes{1}
  - cp_fetch_stall = ibus monitor: the redirect measurement was disturbed (a fill request pending at the pc_set cycle, a 32-bit target straddling a bus word, or an imem response slower than same_cycle/min1 for the target fetch): bins no{0}, yes{1}
  - cp_tbranch_inc = delta of mhpmcounter9 (NumBranchesTaken, hardwired event 9, rtl/ibex_cs_registers.sv:1595; rvfi_ext_mhpmcounters[9 - MHPMCOUNTER_BASE]) over this branch: bins inc0{0}, inc1{1}
  - cp_branch_inc = delta of mhpmcounter8 (NumBranches, hardwired event 8, :1594; rvfi_ext_mhpmcounters[8 - MHPMCOUNTER_BASE]) over this branch: bins inc1{1}, inc2plus{[2:$]: the B17 over-count of a branch that waited in ID behind an outstanding WB access, one extra count per waiting cycle}; ignore_bins inc0: every retired conditional branch counts (a hit is a gen_chk_counters failure)
  - cp_wb_busy = dbus monitor: a data access outstanding when this branch entered ID whose response arrived after that cycle (the branch waits in FIRST_CYCLE with instr_executing = 0, C-10): bins no{0}, yes{1}
  - cp_prev_cti = the previous retirement: bins taken_branch{taken conditional branch}, jump{jal/jalr family/fence.i}, other{default}
- Crosses:
  - cr_taken_dir_align = cp_taken x cp_direction x cp_target_align: bins auto{all combinations}; ignore self with not-taken: the fall-through of a self-branch is not a target-ALU corner
  - cr_taken_dit_delta = cp_taken x cp_dit x cp_delta x cp_fetch_stall: bins nt_dit0_d1{no, off, d1, no}, t_dit0_d2{yes, off, d2, no}, nt_dit1_d2{no, on, d2, no}, t_dit1_d2{yes, on, d2, no}; ignore other combinations: stall-dependent; nt_dit1_d1 and t_*_d1 are impossible by pipeline construction (a hit is a checker failure)
  - cr_taken_dit_redirect = cp_taken x cp_dit x cp_redirect: bins nt_dit0_noredir{no, off, no}, t_dit0_redir{yes, off, yes}, nt_dit1_redir{no, on, yes}, t_dit1_redir{yes, on, yes}; ignore nt_dit0_redir, t_dit0_noredir, nt_dit1_noredir, t_dit1_noredir: contradict the RTL rule (a hit is a checker failure)
  - cr_taken_distance = cp_taken x cp_distance: bins auto{all combinations}
  - cr_perf = cp_taken x cp_dit x cp_tbranch_inc: bins t_dit0_inc1{yes, off, inc1}, nt_dit0_inc0{no, off, inc0}, t_dit1_inc1{yes, on, inc1}, nt_dit1_inc0{no, on, inc0}, nt_dit1_inc1{no, on, inc1}; ignore t_*_inc0 and nt_dit0_inc1: contradict the doc rule (a hit is a checker failure); ignore_bins nt_dit1_inc0: the spec outcome of B11, unreachable on the current RTL (re-enabled as a required bin when B11 is fixed); nt_dit1_inc1 is the B11 witness bin
  - cr_taken_prev = cp_taken x cp_prev_cti: bins auto{all combinations} (back-to-back control transfers seen from the branch: taken_branch = two consecutive taken branches, jump = a jump immediately followed by a branch)
  - cr_perf_wb = cp_wb_busy x cp_branch_inc: bins nowb_inc1{no, inc1}, wb_inc2plus{yes, inc2plus}; ignore nowb_inc2plus: contradicts the RTL rule without a wait (a hit is a gen_chk_counters failure); ignore_bins wb_inc1: the documented outcome of B17 (one count for a waiting branch), unreachable on the current RTL (rtl/ibex_id_stage.sv:886-934, :1054-1057) and re-enabled as the required bin when B17 is fixed; wb_inc2plus is the B17 witness bin (TP-BTALU-018)
  - cr_tperf_wb = cp_wb_busy x cp_taken x cp_dit x cp_tbranch_inc: bins wb_t_dit0_inc1{yes, yes, off, inc1}, wb_nt_dit0_inc0{yes, no, off, inc0}; ignore other combinations: the no-wait cases are cr_perf, the DIT cases are B11 (cr_perf), and wb_t_dit0_inc0 / wb_nt_dit0_inc1 contradict the dedup rule (branch_jump_set_done_q; a hit is a gen_chk_counters failure); counter 9 (and 7) stay exact under a WB wait (C-10, TP-BTALU-011)
- Adopted (riscv-dv): none taken (cp_taken and cp_target_align are operand-only here; the partitions are marked in CG-ISA-007); cp_direction {fwd, bwd, self} refines the adopted CG-ADOPT-003.cp_imm_sign branch_fwd/branch_bwd by the self{0} bin (spec-derived; adopted=0)
- TP items: TP-BTALU-001, TP-BTALU-005, TP-BTALU-006, TP-BTALU-007, TP-BTALU-009, TP-BTALU-011, TP-BTALU-015, TP-BTALU-016, TP-BTALU-017, TP-BTALU-018, TP-ISA-024

### CG-BTALU-002: gen_cg_btalu_jump
- Features: F-BTALU-002, F-BTALU-003, F-BTALU-004, F-BTALU-007, F-BTALU-008, F-BTALU-009, F-BTALU-012, F-BTALU-014
- Sample: RVFI retirement; condition: decoded jal/jalr/fence.i/c.j/c.jal/c.jr/c.jalr, rvfi_trap == 0, and not the first retirement after reset (the delta and cp_seq need a previous retirement; cp_seq classes that look forward wait for the next retirement); the coverpoints discriminate on the clean delta, the odd-sum bit-0 value and the neighbour pattern, so the sample is never a tautology; anti-vacuity: pc_wdata bit 0 and the next pc_rdata are both observed, so cr_odd_bit0 records the actual RVFI value for an actually-odd sum; the sequence coverpoint requires two consecutive control transfers. Target alignment, wrap and link value are owned by CG-ISA-006 (cr_op_align, cr_op_wrap, cr_link) and not repeated here.
- Coverpoints:
  - cp_type = decoded: bins jal{}, jalr{}, fence_i{}, c_j{}, c_jal{}, c_jr{}, c_jalr{}
  - cp_odd_sum = (rs1 + imm)[0], iff jalr/c.jr/c.jalr: bins no{0}, yes{1} [operand-only: canonical CG-ISA-006.cp_target_odd]
  - cp_pc_wdata_bit0 = rvfi_pc_wdata[0]: bins b0{0}, b1{1}
  - cp_delta = redirect delta rvfi_ext_mcycle(successor) - rvfi_ext_mcycle(jump) (conventions), iff redirect_clean: bins d2{2}, d3plus{[3:$]}
  - cp_seq = this jump and its neighbours: bins br_to_jump{the previous retirement is a taken conditional branch}, jal_to_jalr{this is jalr and the previous retirement is jal}, jalr_to_branch{this is jalr/c.jr/c.jalr and the next retirement is a taken conditional branch}, jump_jump{the next retirement is another jump of this group's set}, jump_to_odd_half{the next rvfi_pc_rdata has bit 1 set and its rvfi_insn[1:0] != 11 (a compressed instruction at a half-word target)}, jump_self{target == own pc}, none{default} (two consecutive taken branches are CG-BTALU-001.cr_taken_prev.yes_taken_branch)
- Crosses:
  - cr_odd_bit0 = cp_type x cp_odd_sum x cp_pc_wdata_bit0: bins jalr_odd_b1{jalr, yes, b1}, jalr_odd_b0{jalr, yes, b0}, c_jr_odd_b1{c_jr, yes, b1}, c_jr_odd_b0{c_jr, yes, b0}, c_jalr_odd_b1{c_jalr, yes, b1}, c_jalr_odd_b0{c_jalr, yes, b0}; ignore even sums and non-jalr types: bit 0 is always 0 there; ignore_bins jalr_odd_b0, c_jr_odd_b0, c_jalr_odd_b0: the spec outcome of B13 (rvfi_pc_wdata bit 0 cleared), unreachable on the current RTL and re-enabled as required bins when B13 is fixed; the *_odd_b1 bins are the B13 witnesses (TP-BTALU-008)
  - cr_type_delta = cp_type x cp_delta: bins auto{all combinations}; ignore d3plus for every type except fence_i: stall-dependent; ignore fence_i/d2: unreachable, the pc + 4 refetch always goes to the bus while the invalidation runs (rtl/ibex_icache.sv:1218, :1259-1266), so fence_i_d3plus (exactly 3 under the pinned imem) is fence.i's required bin (TP-BTALU-012; rtl-arch T-053)
  - cr_type_seq = cp_type x cp_seq: bins auto{all combinations}; ignore none: not a corner; ignore jal_to_jalr with types other than jalr, jalr_to_branch with types other than jalr/c_jr/c_jalr, and jump_self with fence_i (target is pc + 4): by definition
- Adopted (riscv-dv): none
- TP items: TP-BTALU-002, TP-BTALU-003, TP-BTALU-004, TP-BTALU-007, TP-BTALU-008, TP-BTALU-009, TP-BTALU-012, TP-BTALU-014, TP-BTALU-017, TP-ISA-019

### CG-BTALU-003: gen_cg_btalu_hazard_fault
- Features: F-BTALU-010, F-BTALU-011, F-BTALU-013
- Sample: RVFI retirement; condition: decoded control-transfer instruction (conditional branch, jal, jalr family), rvfi_trap == 0; the monitor identifies the operand source from the previous retirement(s), the WB state from the dbus monitor and the target fault from the NEXT retirement (rvfi_trap == 1 with rvfi_pc_rdata == the target and handler mcause read-back 1), so there is one sampling event; anti-vacuity: each class needs a specific preceding access, writer or faulting target; a hit proves the CTI executed under that hazard/fault condition. cp_wb_outstanding/cp_wb_error repeat CG-ISA-011's partition operand-only (the CTI-in-ID context is the distinct content, in cr_cti_wb).
- Coverpoints:
  - cp_cti = decoded: bins branch_taken{}, branch_not_taken{}, jal{}, jalr{}
  - cp_operand_src = source of rs1/rs2: bins rf{no recent writer}, fwd_alu{previous retirement is an ALU op writing rs1 or rs2}, load_stall{previous retirement is a load writing rs1 or rs2}
  - cp_wb_outstanding = dbus monitor when the CTI entered ID: bins none{no access}, load{load outstanding}, store{store outstanding} [operand-only: canonical CG-ISA-011.cp_wb_outstanding]
  - cp_wb_error = the outstanding access faulted (data_err_i or PMP): bins no{0}, yes{1} [operand-only: canonical CG-ISA-011.cp_wb_error]
  - cp_redirect_count = ibus non-sequential requests observed while this CTI was in ID, iff icache_enable == 0 and data_ind_timing == 0: bins zero{0}, one{1}, two{2}; ignore_bins two: never legal (a hit is a gen_chk_ibus_proto failure)
  - cp_target_fault = the next retirement traps on the target fetch (rvfi_trap == 1 at rvfi_pc_rdata == target, mcause 1): bins none{no trap at the target}, pmp_exec{PMP X denied per the TB PMP model: the target word IS fetched on the bus (PMP never gates instr_req_o, rtl/ibex_if_stage.sv:426-435) and the fault is attached in the IF->ID register}, bus_err{instr_err_i on the target fetch}
  - cp_mtval_target_ok = mtval read-back == target address, iff target_fault: bins yes{1}
  - cp_dmem_delay = dbus monitor rvalid latency class of the outstanding access, iff wb_outstanding: bins min1{1}, short{[2:4]}, long{[5:$]} [operand-only: canonical CG-REG (xcut) knob:dmem_rvalid_delay]
- Crosses:
  - cr_cti_src = cp_cti x cp_operand_src: bins auto{all combinations}; ignore jal with fwd_alu/load_stall: no register operand
  - cr_cti_wb = cp_cti x cp_wb_outstanding x cp_wb_error: bins auto{all combinations}; ignore none with yes: no access cannot error
  - cr_cti_redirects = cp_cti x cp_wb_outstanding x cp_redirect_count: bins auto{all combinations}; ignore two: never legal (a hit is a checker failure); ignore branch_not_taken with one and branch_taken/jal/jalr with zero: contradict the redirect rule under DIT = 0, which the coverpoint guard pins (a hit is a checker failure)
  - cr_cti_fault = cp_cti x cp_target_fault: bins auto{all combinations}; ignore branch_not_taken and none: no target fetch / not the corner
  - cr_src_delay = cp_operand_src x cp_dmem_delay: bins auto{all combinations}; ignore rf/fwd_alu: guarded
- Adopted (riscv-dv): none
- TP items: TP-BTALU-003, TP-BTALU-010, TP-BTALU-011, TP-BTALU-013, TP-BTALU-017

---------------------------------------------------------------------------------------------------
## Counts

- Covergroups: 40 (per area {'ISA': 11, 'MUL': 5, 'CMP': 10, 'BIT': 11, 'BTALU': 3})
- Coverpoints: 300 (of which 10 operand-only, weight 0); crosses: 176 (30 with named bins, 146 `auto`)
- Coverpoint bins: 1372 declared (`name{...}`; ranges count as one bin each), of which 4 ignore_bins (CG-ISA-005 zcb_alu, CG-BTALU-001 cp_branch_inc.inc0, CG-CMP-009 popret_ra_fwd (fix 3, X-12), CG-BTALU-003 cp_redirect_count.two), 2 probe-gated and 32 operand-only (not in any manifest)
- Cross bins: 167 named cross bins declared (10 ignore_bins / probe-gated, incl. the fix-3 B17 doc-outcome bin cr_perf_wb.wb_inc1 and the X-9 bin cr_wfi_priv_resume.u_sequential) plus 146 `auto` sets that expand to 4288 reachable auto bins (the ignored combinations written on the cross lines are mirrored by the CSV predicates: fix 3 retired the popret_ra_fwd expansions and fence_i_d2, added popret_ra_deferred x {short, long} and fence_i_d3plus)
- Adopted bins: 0 (Critic M-5 pass complete: 14 covergroups carry a "coincides with" / "refines" mark against riscv_instr_cover_group.sv, none was taken from it; CG-CMP-001.cp_reg3 is counted once in CG-ADOPT-005 and is a cross operand only here; see the conventions and tp_isa.md OQ-2)
- Fix 3 (rtl-arch T-053 fold): coverpoints added CG-ISA-009.cp_wfi_resume / cp_busy_off, CG-ISA-011.cp_ebreak_variant_trap, CG-BTALU-001.cp_wb_busy; crosses added CG-ISA-009.cr_wfi_priv_resume, CG-BTALU-001.cr_perf_wb / cr_tperf_wb; bins added CG-CMP-005.cp_addr_align {aligned, mis1, mis3} (replacing aligned/misaligned), CG-CMP-008 cp_phase.none / cp_outcome.pre_uop0 / nmi_last_deferred / trigger_pre_uop0, CG-CMP-009.cp_hazard.popret_ra_deferred, CG-BTALU-001.cp_branch_inc.inc2plus; renamed cr_wb_hold / cp_wb_hold / cr_op_wb_hold / cp_hold_cycles / cr_class_hold -> *_defer; redefined CG-BTALU-001/002.cp_delta as the redirect delta and CG-CMP-004.cp_rvfi_insn_ok as class-dependent.
- Trace: trace_feat_tp_isa.csv (336 rows) and trace_tp_bin_isa.csv (10985 rows, covergroup column = CG-ID, every `auto` reference expanded to its reachable bins) were updated surgically by the fix-3 script and re-verified: every bin referenced by a TP item exists here and is neither ignored, probe-gated nor operand-only; every CSV row is justified by its item's Bins line; every F-ID of the area (incl. ALIAS/FOLDED) maps to >= 1 TP item and >= 1 bin; TP/CG/F ids are consecutive per area; all five files are ASCII.

## Probe candidates

Every covergroup above samples from the RVFI monitor, the ibus/dbus monitors, the irq/debug pin
drivers' timestamps, or the TB CSR model (predicted from retired CSR writes). One bin family
cannot be sampled from the boundary or RVFI:

- CG-CMP-008.cp_event.dummy_inserted (and the derived cross bins cr_event_phase_outcome.dummy_ls,
  dummy_commit, cr_insn_event.*/dummy_inserted): needs the dummy-instruction indication while a
  Zcmp expansion is in flight. Dummy instructions are architecturally invisible and excluded from
  RVFI (rvfi_stage_valid_d[0] masks dummy_instr_id); the only boundary trace is a fetch/retire
  timing gap, which is ambiguous under memory-response randomization. Candidate signal: the
  ibex_core output port dummy_instr_id_o as wired inside gen_dut_top (tb-infra probe P1; rtl-arch
  section 9 notes it is a core port, so a wrapper-internal net observation rather than an RTL
  probe). Coverage-only; no checker depends on it (gen_chk_zcmp_seq counts stores/loads from the
  RVFI/dbus streams). These bins are probe-gated (P1), not in manifest, until the probe register
  carries P1 (gen_tb_architecture.md 8.3 item 5); meanwhile TP-CMP-065's manifest uses the
  boundary-derived CG-CMP-006.cp_dummy_en / cr_insn_dummy bins and its insertion count comes from
  minstret (dummies are counted, B7). The DV Lead decides; if P1 is rejected, the three dummy bins
  become ignore_bins with reason "probe P1 rejected".

- CG-MUL-005 (F-MUL-028, TP-MUL-030) relies on the bound SVA module gen_sva_multdiv (rtl-arch
  gen_multdiv_bound_props.md MD-1..MD-5 bound properties plus the covers MD-C1..MD-C4; the former
  freeze-arc assertion is structurally implied and kept as a cover only) inside
  ibex_multdiv_fast. The bounds have no boundary observable beyond the RVFI deltas; the bind is coverage/assertion-only
  and no checker depends on it (probe candidate P8 (probe register entry needed); tp_isa.md OQ-9). Probe status: pending probe-register ruling; cp_sva_checked is excluded from manifests until ruled.
  cp_sva_checked is the only bin that needs it and is probe-gated (not in manifest) until the bind
  is registered; if the bind is rejected it becomes ignore_bins with reason "probe rejected" and
  TP-MUL-030 keeps its RVFI fire-check.

No other bin needs an internal signal. Bins that look internal but are boundary-derived: retire
deltas (rvfi_ext_mcycle), fetch_stall / wb_busy (ibus and dbus monitor request/response timing),
redirect and redirect counts (ibus monitor, sampled only with icache_enable = 0 so a cache hit
cannot hide a request; otherwise derived from RVFI pc_wdata / next pc_rdata),
data_ind_timing / dcsr / mstatus.TW / icache_enable (TB CSR model from retired csrw on RVFI plus
csrr read-back), Zcmp micro-op index and phase (rvfi_ext_expanded_insn* tags and the synthesized
rvfi_insn), event-mid-op (pin driver assertion timestamps compared with the retirement window),
perf-counter deltas (rvfi_ext_mhpmcounters).


# 3.2 Areas CSR, PRV: Control and status registers; privilege modes M/U and mstatus semantics


T-006 subagent output for the DV Lead. Areas: CSR (F-CSR-001..103) and PRV (F-PRV-001..035).
Feature source: dv/auto_dv/work/dv-lead/parts/gen_part_csr.md. Companion test plan: tp_csr.md.

Conventions
- All covergroups live in the gen_ namespace (gen_cg_csr_*, gen_cg_prv_*); none extends an RTL
  covergroup. Sampling is from the DUT boundary and RVFI only unless the bin is listed under
  "Probe candidates" at the end.
- Parameter-derived counts: MHPMCounterNum = 10 (counters HPM_IDX = 3..2+MHPMCounterNum, i.e. 3..2+MHPMCounterNum:
  bins hpm3..hpm12 are 3..3+MHPMCounterNum-1; unimplemented indices HPM_UNIMPL_IDX =
  3+MHPMCounterNum..31), PMPNumRegions = 16 (pmpcfg0..PMPNumRegions/4-1, pmpaddr0..PMPNumRegions-1),
  $bits(irq_fast_i) = 15 (mie/mip fast bits 16+$bits(irq_fast_i)-1:16, fast ids
  f0..f{$bits(irq_fast_i)-1}, NUM_IRQ_LINES = 3 + $bits(irq_fast_i) = 18), DbgHwBreakNum = 1 (tselect
  clamp). Named constants used in bin expressions: CTR_MASK = ((1 << (3 + MHPMCounterNum)) - 1) &
  ~(1 << 1) (= 0x1FFD: mcounteren / mcountinhibit implemented bits, bit 1 forced 0); MIE_MASK =
  (((1 << $bits(irq_fast_i)) - 1) << 16) | 0x888 (= 0x7FFF_0888); DCSR_W_MASK = (1 << 15) | (1 << 12) |
  (1 << 2) | 0x3 (= 0x9007: ebreakm, ebreaku, step, prv; bit 13 ebreaks is a forced-0 field per B15,
  bit 3 nmip is B5-owned by TP-DBG-021 and excluded from the CSR compare). Bin lists written as hpm3,
  hpm4, ..., hpm12 / f0..f14 / pmpaddr0..15 are generated from the parameter, never typed; every
  literal in this file is this build's value of the named expression.
- "csr address class" (cp_aclass in CG-CSR-001) is a TB classifier of rvfi_insn[31:20]:
  rw_m = implemented M-level RW with storage (mstatus, mie, mtvec, mcounteren, mcountinhibit,
  mscratch, mepc, mcause, mtval, mcycle(h), minstret(h), mhpmcounter3..2+MHPMCounterNum, mseccfg, cpuctrlsts,
  secureseed); wi_m = implemented, writes silently ignored (misa, mstatush, menvcfg, menvcfgh,
  mhpmevent3..31, mhpmcounter3h..12h, mhpmcounter3+MHPMCounterNum..31(h), mip, mseccfgh, tdata3, mcontext,
  mscontext); trig = tselect, tdata1, tdata2; pmp = pmpcfg0..3, pmpaddr0..15; dbg_only = 0x7B0..0x7B3;
  info_ro = 0xF11..0xF15; alias_impl = 0xC00, 0xC02, 0xC03..0xC02+MHPMCounterNum and +0x80 halves; alias_unimpl =
  0xC03+MHPMCounterNum..0xC1F, 0xC83+MHPMCounterNum..0xC9F; time = 0xC01, 0xC81; s_lvl = 0x5A8; cheriot = 0xBC1, 0xBC2, 0xBC4;
  hole_lo = 0x000..0x2FF; hole_m = unimplemented addresses in 0x300..0xBFF (incl. 0x7B4..0x7BF);
  hole_ro = unimplemented addresses with [11:10] = 11 other than time.
- "illegal class set" (cp_iclass) is the TB's own evaluation of the four RTL classes (priv,
  write_ro, unimpl, dbg) after the rs1 = x0 / uimm = 0 demotion to READ; it is coverage of the
  stimulus, not a checker.
- "readback pair" = a CSR write op retired without trap followed by the next csrr of the same
  address before any other write to it; gen_chk_csr_readback compares the pair.
- Write pattern classes (cp_wpat): rand = uniform 32-bit; all1 = 0xFFFF_FFFF; all0 = 0; legal_only =
  only writable bits set; illegal_only = only read-only/legalised bits set; msb_only = 0x8000_0000.
- Bin names are [a-z0-9_]; every bin is written name{meaning}. Cross bins name the combination.
- Adopted (riscv-dv) is "none" everywhere: the riscv-dv tree is outside this subagent's read scope.
- Redirect targets (rtl-arch T-053 X-1, tp_csr.md C-1): a trap, mret or dret record carries the next
  SEQUENTIAL fetch address in rvfi_pc_wdata; every target-class coverpoint (CG-PRV-008.cp_target,
  CG-PRV-002.cr_mret_target, CG-PRV-007.cr_mret_dbg) is derived from the NEXT record's rvfi_pc_rdata.
- Probe-gated bins (S-13): CG-CSR-010.cp_pulse and cr_op_form_pulse need probe candidate P7 (PROPOSED,
  Critic ruling pending); they stay in this file as coverage-only observations, appear in no item's
  Bins line, no CSV row and no manifest until ruled; the boundary equivalent is cr_op_form_gap.
- Feature lists may name IDs that gen_part_csr.md marks ALIAS or FOLDED (Status line). Every FOLDED
  entry names the bin here that now carries it; ALIAS IDs resolve to the canonical feature of the
  owning area. No bin was added or removed for the fold: the restated edges already had bins here.

## Covergroups: CSR

### CG-CSR-001: gen_cg_csr_access_class
- Features: F-CSR-001, F-CSR-002, F-CSR-003, F-CSR-004, F-CSR-005, F-CSR-009, F-CSR-011, F-CSR-012, F-CSR-013, F-CSR-014, F-CSR-015, F-CSR-016, F-CSR-017, F-CSR-018, F-CSR-057, F-CSR-097, F-CSR-103, F-PRV-034
- Sample: rvfi_valid with rvfi_insn opcode SYSTEM (0x73) and funct3 != 000 (every CSR instruction, trapped or not); condition: rvfi_valid && is_csr_insn(rvfi_insn); anti-vacuity: non-CSR retirements never sample, so a hit proves a CSR instruction of that op / operand / address class retired or trapped in the sampled privilege and debug state; the outcome is rvfi_trap of the same retirement.
- Coverpoints:
  - cp_op = rvfi_insn[14:12]: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}, f3_100{100 illegal funct3}
  - cp_rs1 = rvfi_insn[19:15] (rs1 or uimm): bins zero{0}, nonzero{1..31}
  - cp_rd = rvfi_insn[11:7]: bins x0{0}, nonx0{1..31}
  - cp_priv = rvfi_mode: bins m{3}, u{0}; ignore_bins s_h{1,2}: priv_lvl_q only ever holds M or U
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_aclass = TB address classifier of rvfi_insn[31:20]: bins rw_m{implemented RW with storage}, wi_m{implemented write-ignored}, trig{tselect tdata1 tdata2}, pmp{pmpcfg0..3 pmpaddr0..15}, dbg_only{0x7B0..0x7B3}, info_ro{0xF11..0xF15}, alias_impl{0xC00 0xC02 0xC03..0xC02+MHPMCounterNum +0x80}, alias_unimpl{0xC03+MHPMCounterNum..0xC1F 0xC83+MHPMCounterNum..0xC9F}, time{0xC01 0xC81}, s_lvl{0x5A8}, cheriot{0xBC1 0xBC2 0xBC4}, hole_lo{0x000..0x2FF}, hole_m{unimplemented 0x300..0xBFF}, hole_ro{unimplemented [11:10]=11 except time}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_iclass = TB illegal class set after demotion: bins none{no class}, priv{priv only}, wro{write_ro only}, unimpl{unimpl only}, dbg{dbg only}, multi{two or more classes}
- Crosses:
  - cr_rs1zero_ro = cp_op x cp_rs1 x cp_aclass x cp_trap (read-only address classes only): bins csrrs_x0_info_ok{csrrs zero info_ro ok}, csrrc_x0_info_ok{csrrc zero info_ro ok}, csrrsi_0_info_ok{csrrsi zero info_ro ok}, csrrci_0_info_ok{csrrci zero info_ro ok}, csrrs_x0_alias_ok{csrrs zero alias_impl ok}, csrrc_x0_alias_ok{csrrc zero alias_impl ok}, csrrsi_0_alias_ok{csrrsi zero alias_impl ok}, csrrci_0_alias_ok{csrrci zero alias_impl ok}, csrrs_nz_info_trap{csrrs nonzero info_ro trap}, csrrc_nz_info_trap{csrrc nonzero info_ro trap}, csrrsi_nz_info_trap{csrrsi nonzero info_ro trap}, csrrci_nz_info_trap{csrrci nonzero info_ro trap}, csrrs_nz_alias_trap{csrrs nonzero alias_impl trap}, csrrc_nz_alias_trap{csrrc nonzero alias_impl trap}, csrrw_x0_info_trap{csrrw zero info_ro trap}, csrrwi_0_info_trap{csrrwi zero info_ro trap}, csrrw_x0_alias_trap{csrrw zero alias_impl trap}, csrrwi_0_alias_trap{csrrwi zero alias_impl trap}, csrrw_nz_info_trap{csrrw nonzero info_ro trap}, csrrw_nz_alias_trap{csrrw nonzero alias_impl trap}; ignore csrrs/csrrc/csrrsi/csrrci with zero operand x trap on info_ro/alias_impl in M-mode: demoted to READ, cannot trap; ignore csrrw x ok on read-only classes: always illegal_csr_write
  - cr_rd_x0_write = cp_op x cp_rd x cp_aclass: bins csrrw_rdx0_rw_m{csrrw x0 rw_m}, csrrwi_rdx0_rw_m{csrrwi x0 rw_m}, csrrs_rdx0_rw_m{csrrs x0 rw_m}, csrrc_rdx0_rw_m{csrrc x0 rw_m}, csrrsi_rdx0_rw_m{csrrsi x0 rw_m}, csrrci_rdx0_rw_m{csrrci x0 rw_m}, csrrw_rdx0_info_ro{csrrw x0 info_ro}, csrrw_rdx0_wi_m{csrrw x0 wi_m}, csrrw_rdnz_rw_m{csrrw nonx0 rw_m}
  - cr_priv_aclass_trap = cp_priv x cp_aclass x cp_trap: bins u_rw_m_trap{u rw_m trap}, u_wi_m_trap{u wi_m trap}, u_trig_trap{u trig trap}, u_pmp_trap{u pmp trap}, u_dbg_only_trap{u dbg_only trap}, u_info_ro_trap{u info_ro trap}, u_alias_impl_ok{u alias_impl ok}, u_alias_impl_trap{u alias_impl trap}, u_alias_unimpl_trap{u alias_unimpl trap}, u_time_trap{u time trap}, u_s_lvl_trap{u s_lvl trap}, u_cheriot_trap{u cheriot trap}, u_hole_lo_trap{u hole_lo trap}, u_hole_m_trap{u hole_m trap}, u_hole_ro_trap{u hole_ro trap}, m_rw_m_ok{m rw_m ok}, m_wi_m_ok{m wi_m ok}, m_trig_ok{m trig ok}, m_pmp_ok{m pmp ok}, m_dbg_only_trap{m dbg_only trap}, m_info_ro_ok{m info_ro ok}, m_alias_impl_ok{m alias_impl ok}, m_alias_unimpl_ok{m alias_unimpl ok}, m_time_trap{m time trap}, m_s_lvl_ok{m s_lvl ok (B3 evidence: scontext at the S-level address 0x5A8 reads 0 from M-mode where Sdtrig requires a trap)}, m_cheriot_trap{m cheriot trap}, m_hole_lo_trap{m hole_lo trap}, m_hole_m_trap{m hole_m trap}, m_hole_ro_trap{m hole_ro trap}; ignore u x {rw_m, wi_m, trig, pmp, dbg_only, info_ro, s_lvl, cheriot, hole_m} x ok: csr[9:8] > U always traps; ignore m x {time, cheriot, hole_lo, hole_m, hole_ro} x ok: unimplemented addresses always trap
  - cr_dbg_access = cp_dbg x cp_aclass x cp_trap: bins dbg_dbgonly_ok{dbg dbg_only ok}, nondbg_dbgonly_trap{nondbg dbg_only trap}, dbg_hole_m_trap{dbg hole_m trap incl 0x7B4..0x7BF}, dbg_trig_ok{dbg trig ok}, dbg_rw_m_ok{dbg rw_m ok}, dbg_info_ro_ok{dbg info_ro ok}; ignore nondbg x dbg_only x ok: illegal_csr_dbg always fires outside debug mode
  - cr_iclass_priv = cp_iclass x cp_priv: bins none_m{none m}, none_u{none u}, priv_u{priv u}, wro_m{wro m}, wro_u{wro u alias write}, unimpl_m{unimpl m}, unimpl_u{unimpl u U-level hole}, dbg_m{dbg m}, multi_u{multi u}, multi_m{multi m}; ignore priv_m: csr[9:8] > M is impossible
  - cr_f3_100 = cp_op x cp_trap (f3_100 only): bins f3_100_trap{f3_100 trap}; ignore f3_100_ok: decoder csr_illegal always fires
- Adopted (riscv-dv): none
- TP items: TP-CSR-001, TP-CSR-002, TP-CSR-003, TP-CSR-004, TP-CSR-005, TP-CSR-009, TP-CSR-011, TP-CSR-012, TP-CSR-013, TP-CSR-014, TP-CSR-015, TP-CSR-016, TP-CSR-017, TP-CSR-018, TP-CSR-021, TP-CSR-049, TP-CSR-055, TP-CSR-056, TP-CSR-057, TP-CSR-080, TP-CSR-083, TP-CSR-098, TP-CSR-104, TP-CSR-110, TP-CSR-111, TP-CSR-112, TP-CSR-116, TP-CSR-117, TP-CSR-118, TP-PRV-033

### CG-CSR-002: gen_cg_csr_trap_setup_warl
- Features: F-CSR-021, F-CSR-022, F-CSR-023, F-CSR-024, F-CSR-025, F-CSR-027, F-CSR-028, F-CSR-029,
  F-CSR-030, F-CSR-035, F-CSR-036, F-CSR-037, F-CSR-050, F-CSR-051, F-CSR-052, F-PRV-035, F-PMC-025
  (parent of folded bins hosted here)
- Sample: gen_chk_csr_readback pair completion for a trap-setup CSR (mstatus, misa, mie, mtvec, mcounteren, mstatush, menvcfg, menvcfgh); condition: pair closed (write retired without trap, read-back retired); anti-vacuity: pairs exist only when the program writes then reads the same CSR, so a hit proves the legalised prediction for that write pattern was compared against the read-back.
- Coverpoints:
  - cp_csr = pair address: bins mstatus{0x300}, misa{0x301}, mie{0x304}, mtvec{0x305}, mcounteren{0x306}, mstatush{0x310}, menvcfg{0x30A}, menvcfgh{0x31A}
  - cp_op = write op of the pair: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only}, illegal_only{RO or legalised bits only}, msb_only{0x8000_0000}
  - cp_rd = rd of the write: bins x0{0}, nonx0{1..31}
  - cp_mpp_w = written mstatus[12:11] iff (cp_csr == mstatus): bins u{00}, s{01}, h{10}, m{11}
  - cp_mst_mie_w = written mstatus[3] iff (cp_csr == mstatus): bins b0{0}, b1{1}
  - cp_mst_mpie_w = written mstatus[7] iff (cp_csr == mstatus): bins b0{0}, b1{1}
  - cp_mst_mprv_w = written mstatus[17] iff (cp_csr == mstatus): bins b0{0}, b1{1}
  - cp_mst_tw_w = written mstatus[21] iff (cp_csr == mstatus): bins b0{0}, b1{1}
  - cp_mtvec_mode_w = written mtvec[1:0] iff (cp_csr == mtvec): bins d00{00 direct}, v01{01 vectored}, r10{10}, r11{11}
  - cp_mtvec_lo_w = written mtvec[7:2] iff (cp_csr == mtvec): bins zero{0}, nonzero{!=0}
  - cp_mtvec_base_w = written mtvec[31:8] class iff (cp_csr == mtvec): bins low{< 0x1000}, boot_page{== boot_addr_i[31:8]}, high{bit 31 set}, rand{other}
  - cp_mie_w = written mie bit groups iff (cp_csr == mie): bins std_only{bits 3 7 11 only}, fast_only{bits 16+$bits(irq_fast_i)-1:16 only}, std_fast{both}, ro_only{only bits outside MIE_MASK}, all_fast{all $bits(irq_fast_i) fast bits}
  - cp_mcen_gate = mcounteren_writable_i at the write iff (cp_csr == mcounteren): bins on{IbexMuBiOn}, off{IbexMuBiOff}, invalid{other encodings}
  - cp_mcen_w = written mcounteren bit class iff (cp_csr == mcounteren) (CTR_MASK bits): bins cy{bit 0}, ir{bit 2}, hpm3{bit 3}, hpm4{bit 4}, hpm5{bit 5}, hpm6{bit 6}, hpm7{bit 7}, hpm8{bit 8}, hpm9{bit 9}, hpm10{bit 10}, hpm11{bit 11}, hpm12{bit 12}, tm_ro{bit 1}, hi_ro{bits 31:3+MHPMCounterNum}, all1{all bits}
- Crosses:
  - cr_csr_op = cp_csr x cp_op: bins mstatus_csrrw{mstatus csrrw}, mstatus_csrrs{mstatus csrrs}, mstatus_csrrc{mstatus csrrc}, mstatus_csrrwi{mstatus csrrwi}, mstatus_csrrsi{mstatus csrrsi}, mstatus_csrrci{mstatus csrrci}, misa_csrrw{misa csrrw}, misa_csrrs{misa csrrs}, misa_csrrc{misa csrrc}, misa_csrrwi{misa csrrwi}, misa_csrrsi{misa csrrsi}, misa_csrrci{misa csrrci}, mie_csrrw{mie csrrw}, mie_csrrs{mie csrrs}, mie_csrrc{mie csrrc}, mie_csrrwi{mie csrrwi}, mie_csrrsi{mie csrrsi}, mie_csrrci{mie csrrci}, mtvec_csrrw{mtvec csrrw}, mtvec_csrrs{mtvec csrrs}, mtvec_csrrc{mtvec csrrc}, mtvec_csrrwi{mtvec csrrwi}, mtvec_csrrsi{mtvec csrrsi}, mtvec_csrrci{mtvec csrrci}, mcounteren_csrrw{mcounteren csrrw}, mcounteren_csrrs{mcounteren csrrs}, mcounteren_csrrc{mcounteren csrrc}, mcounteren_csrrwi{mcounteren csrrwi}, mcounteren_csrrsi{mcounteren csrrsi}, mcounteren_csrrci{mcounteren csrrci}, mstatush_csrrw{mstatush csrrw}, mstatush_csrrs{mstatush csrrs}, mstatush_csrrc{mstatush csrrc}, mstatush_csrrwi{mstatush csrrwi}, mstatush_csrrsi{mstatush csrrsi}, mstatush_csrrci{mstatush csrrci}, menvcfg_csrrw{menvcfg csrrw}, menvcfg_csrrs{menvcfg csrrs}, menvcfg_csrrc{menvcfg csrrc}, menvcfg_csrrwi{menvcfg csrrwi}, menvcfg_csrrsi{menvcfg csrrsi}, menvcfg_csrrci{menvcfg csrrci}, menvcfgh_csrrw{menvcfgh csrrw}, menvcfgh_csrrs{menvcfgh csrrs}, menvcfgh_csrrc{menvcfgh csrrc}, menvcfgh_csrrwi{menvcfgh csrrwi}, menvcfgh_csrrsi{menvcfgh csrrsi}, menvcfgh_csrrci{menvcfgh csrrci}
  - cr_csr_wpat = cp_csr x cp_wpat: bins mstatus_rand{mstatus rand}, mstatus_all1{mstatus all1}, mstatus_all0{mstatus all0}, mstatus_legal{mstatus legal_only}, mstatus_illegal{mstatus illegal_only}, mstatus_msb{mstatus msb_only}, misa_rand{misa rand}, misa_all1{misa all1}, misa_all0{misa all0}, misa_legal{misa legal_only}, misa_illegal{misa illegal_only}, misa_msb{misa msb_only}, mie_rand{mie rand}, mie_all1{mie all1}, mie_all0{mie all0}, mie_legal{mie legal_only}, mie_illegal{mie illegal_only}, mie_msb{mie msb_only}, mtvec_rand{mtvec rand}, mtvec_all1{mtvec all1}, mtvec_all0{mtvec all0}, mtvec_legal{mtvec legal_only}, mtvec_illegal{mtvec illegal_only}, mtvec_msb{mtvec msb_only}, mcounteren_rand{mcounteren rand}, mcounteren_all1{mcounteren all1}, mcounteren_all0{mcounteren all0}, mcounteren_legal{mcounteren legal_only}, mcounteren_illegal{mcounteren illegal_only}, mcounteren_msb{mcounteren msb_only}, mstatush_rand{mstatush rand}, mstatush_all1{mstatush all1}, mstatush_all0{mstatush all0}, mstatush_msb{mstatush msb_only}, menvcfg_rand{menvcfg rand}, menvcfg_all1{menvcfg all1}, menvcfg_all0{menvcfg all0}, menvcfg_msb{menvcfg msb_only}, menvcfgh_rand{menvcfgh rand}, menvcfgh_all1{menvcfgh all1}, menvcfgh_all0{menvcfgh all0}, menvcfgh_msb{menvcfgh msb_only}; ignore {mstatush, menvcfg, menvcfgh} x {legal_only, illegal_only}: no writable bit exists, the classes collapse into all0/all1
  - cr_mpp_op = cp_mpp_w x cp_op: bins mpp_s_csrrw{s csrrw}, mpp_h_csrrw{h csrrw}, mpp_s_csrrs{s csrrs}, mpp_h_csrrs{h csrrs}, mpp_m_csrrw{m csrrw}, mpp_m_csrrs{m csrrs}, mpp_u_csrrw{u csrrw}, mpp_u_csrrc{u csrrc}; ignore {s, h} x {csrrwi, csrrsi, csrrci}: the 5-bit immediate cannot reach bits 12:11, so the written MPP equals the old MPP (00 or 11 after legalisation); mpp_h_csrrsi was unreachable for the same reason (S-7)
  - cr_mst_fields = cp_mst_mie_w x cp_mst_mpie_w x cp_mst_mprv_w x cp_mst_tw_w: bins all0{0 0 0 0}, all1{1 1 1 1}, mie_only{1 0 0 0}, mpie_only{0 1 0 0}, mprv_only{0 0 1 0}, tw_only{0 0 0 1}, mprv_tw{0 0 1 1}, mie_mpie{1 1 0 0}
  - cr_mtvec_mode_lo = cp_mtvec_mode_w x cp_mtvec_lo_w: bins d00_zero{d00 zero}, d00_nz{d00 nonzero}, v01_zero{v01 zero}, v01_nz{v01 nonzero}, r10_zero{r10 zero}, r10_nz{r10 nonzero}, r11_zero{r11 zero}, r11_nz{r11 nonzero}
  - cr_mtvec_base_op = cp_mtvec_base_w x cp_op: bins low_csrrw{low csrrw}, high_csrrw{high csrrw}, boot_csrrw{boot_page csrrw}, rand_csrrw{rand csrrw}, rand_csrrs{rand csrrs}, rand_csrrc{rand csrrc}, high_csrrs{high csrrs}
  - cr_mie_w_op = cp_mie_w x cp_op: bins std_csrrw{std_only csrrw}, fast_csrrw{fast_only csrrw}, both_csrrw{std_fast csrrw}, ro_csrrw{ro_only csrrw}, allfast_csrrw{all_fast csrrw}, std_csrrs{std_only csrrs}, fast_csrrs{fast_only csrrs}, std_csrrc{std_only csrrc}, fast_csrrc{fast_only csrrc}, std_csrrsi{std_only csrrsi}, std_csrrci{std_only csrrci}
  - cr_mcen_gate_w = cp_mcen_gate x cp_mcen_w: bins on_cy{on cy}, on_ir{on ir}, on_hpm3{on hpm3}, on_hpm12{on hpm12}, on_tm_ro{on tm_ro}, on_hi_ro{on hi_ro}, on_all1{on all1}, off_all1{off all1}, off_cy{off cy}, invalid_all1{invalid all1}, invalid_ir{invalid ir}
- Adopted (riscv-dv): none
- TP items: TP-CSR-003, TP-CSR-004, TP-CSR-021, TP-CSR-022, TP-CSR-023, TP-CSR-024, TP-CSR-025, TP-CSR-026, TP-CSR-027, TP-CSR-028, TP-CSR-029, TP-CSR-030, TP-CSR-031, TP-CSR-035, TP-CSR-036, TP-CSR-050, TP-CSR-051, TP-CSR-052, TP-CSR-099, TP-CSR-101, TP-CSR-116, TP-PRV-034

### CG-CSR-003: gen_cg_csr_trap_handling_warl
- Features: F-CSR-038, F-CSR-039, F-CSR-040, F-CSR-042, F-CSR-043, F-CSR-044, F-CSR-045, F-CSR-046, F-CSR-047, F-CSR-032, F-CSR-033
- Sample: gen_chk_csr_readback pair completion for mscratch, mepc, mcause, mtval, mip; condition: pair closed; anti-vacuity: as CG-CSR-002; for mip the "pair" is a write op followed by a read with the irq pins held, so a hit proves the write-ignored prediction was compared.
- Coverpoints:
  - cp_csr = pair address: bins mscratch{0x340}, mepc{0x341}, mcause{0x342}, mtval{0x343}, mip{0x344}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only}, illegal_only{RO bits only}, msb_only{0x8000_0000}
  - cp_mepc_lo_w = written mepc[1:0] iff (cp_csr == mepc): bins b00{00}, b01{01}, b10{10}, b11{11}
  - cp_mcause_hi_w = written mcause[31:30] iff (cp_csr == mcause): bins h00{00}, h01{01}, h10{10 irq_ext}, h11{11 irq_int}
  - cp_mcause_mid_w = written mcause[29:5] iff (cp_csr == mcause): bins zero{0}, nonzero{!=0}
  - cp_mcause_code_w = written mcause[4:0] iff (cp_csr == mcause): bins c0{0}, c31{31}, other{1..30}
  - cp_mip_pins = irq pin set at the mip read iff (cp_csr == mip): bins none{no pin}, sw{irq_software_i}, timer{irq_timer_i}, ext{irq_external_i}, fast_any{any irq_fast_i}, multi{two or more}
- Crosses:
  - cr_csr_op = cp_csr x cp_op: bins mscratch_csrrw{mscratch csrrw}, mscratch_csrrs{mscratch csrrs}, mscratch_csrrc{mscratch csrrc}, mscratch_csrrwi{mscratch csrrwi}, mscratch_csrrsi{mscratch csrrsi}, mscratch_csrrci{mscratch csrrci}, mepc_csrrw{mepc csrrw}, mepc_csrrs{mepc csrrs}, mepc_csrrc{mepc csrrc}, mepc_csrrwi{mepc csrrwi}, mepc_csrrsi{mepc csrrsi}, mepc_csrrci{mepc csrrci}, mcause_csrrw{mcause csrrw}, mcause_csrrs{mcause csrrs}, mcause_csrrc{mcause csrrc}, mcause_csrrwi{mcause csrrwi}, mcause_csrrsi{mcause csrrsi}, mcause_csrrci{mcause csrrci}, mtval_csrrw{mtval csrrw}, mtval_csrrs{mtval csrrs}, mtval_csrrc{mtval csrrc}, mtval_csrrwi{mtval csrrwi}, mtval_csrrsi{mtval csrrsi}, mtval_csrrci{mtval csrrci}, mip_csrrw{mip csrrw}, mip_csrrs{mip csrrs}, mip_csrrc{mip csrrc}, mip_csrrwi{mip csrrwi}, mip_csrrsi{mip csrrsi}, mip_csrrci{mip csrrci}
  - cr_csr_wpat = cp_csr x cp_wpat: bins mscratch_rand{mscratch rand}, mscratch_all1{mscratch all1}, mscratch_all0{mscratch all0}, mscratch_msb{mscratch msb_only}, mepc_rand{mepc rand}, mepc_all1{mepc all1}, mepc_all0{mepc all0}, mepc_legal{mepc legal_only}, mepc_illegal{mepc illegal_only bit0}, mepc_msb{mepc msb_only}, mcause_rand{mcause rand}, mcause_all1{mcause all1}, mcause_all0{mcause all0}, mcause_legal{mcause legal_only}, mcause_illegal{mcause illegal_only}, mcause_msb{mcause msb_only}, mtval_rand{mtval rand}, mtval_all1{mtval all1}, mtval_all0{mtval all0}, mtval_msb{mtval msb_only}, mip_rand{mip rand}, mip_all1{mip all1}, mip_all0{mip all0}, mip_msb{mip msb_only}; ignore {mscratch, mtval} x {legal_only, illegal_only}: all 32 bits writable, classes collapse into rand/all1; ignore mip x {legal_only, illegal_only}: no writable bit
  - cr_mcause_hi_mid = cp_mcause_hi_w x cp_mcause_mid_w: bins h00_zero{h00 zero}, h00_nz{h00 nonzero}, h01_zero{h01 zero}, h01_nz{h01 nonzero}, h10_zero{h10 zero}, h10_nz{h10 nonzero}, h11_zero{h11 zero}, h11_nz{h11 nonzero}
  - cr_mcause_hi_code = cp_mcause_hi_w x cp_mcause_code_w: bins h11_c0{h11 c0}, h11_c31{h11 c31}, h10_c0{h10 c0}, h10_other{h10 other}, h00_c31{h00 c31}, h01_other{h01 other}
  - cr_mepc_lo_op = cp_mepc_lo_w x cp_op: bins b01_csrrw{b01 csrrw}, b11_csrrw{b11 csrrw}, b10_csrrw{b10 csrrw}, b00_csrrw{b00 csrrw}, b01_csrrs{b01 csrrs}, b11_csrrsi{b11 csrrsi}, b01_csrrc{b01 csrrc}
  - cr_mip_pins_op = cp_mip_pins x cp_op: bins none_csrrw{none csrrw}, sw_csrrw{sw csrrw}, timer_csrrs{timer csrrs}, ext_csrrc{ext csrrc}, fast_csrrw{fast_any csrrw}, multi_csrrwi{multi csrrwi}, multi_csrrw{multi csrrw}
- Adopted (riscv-dv): none
- TP items: TP-CSR-001, TP-CSR-003, TP-CSR-032, TP-CSR-033, TP-CSR-038, TP-CSR-039, TP-CSR-040, TP-CSR-042, TP-CSR-043, TP-CSR-044, TP-CSR-045, TP-CSR-046, TP-CSR-047, TP-CSR-101, TP-CSR-116

### CG-CSR-004: gen_cg_csr_counter_warl
- Features: F-CSR-058, F-CSR-059, F-CSR-060, F-CSR-061, F-CSR-062, F-CSR-066, F-CSR-069, F-CSR-070,
  F-CSR-071, F-CSR-073, F-PMC-020 (parent of folded bins hosted here)
- Sample: gen_chk_csr_readback pair completion for a counter-family CSR (0xB00..0xB9F, 0x320, 0x323..0x33F); condition: pair closed; anti-vacuity: as CG-CSR-002; for running counters the prediction includes the elapsed-cycle / retired-instruction delta from gen_chk_counters, so a hit proves both models agreed on that write.
- Coverpoints:
  - cp_csr = pair address: bins mcycle{0xB00}, mcycleh{0xB80}, minstret{0xB02}, minstreth{0xB82}, hpm3{0xB03}, hpm4{0xB04}, hpm5{0xB05}, hpm6{0xB06}, hpm7{0xB07}, hpm8{0xB08}, hpm9{0xB09}, hpm10{0xB0A}, hpm11{0xB0B}, hpm12{0xB0C}, hpm3h{0xB83}, hpm4h{0xB84}, hpm5h{0xB85}, hpm6h{0xB86}, hpm7h{0xB87}, hpm8h{0xB88}, hpm9h{0xB89}, hpm10h{0xB8A}, hpm11h{0xB8B}, hpm12h{0xB8C}, hpm_unimpl{0xB03+MHPMCounterNum..0xB1F}, hpm_unimpl_h{0xB83+MHPMCounterNum..0xB9F}, mcountinhibit{0x320}, mhpmevent_impl{0x323..0x322+MHPMCounterNum}, mhpmevent_unimpl{0x323+MHPMCounterNum..0x33F}
  - cp_fam = counter family of cp_csr: bins cycle64{mcycle mcycleh}, instret64{minstret minstreth}, hpm32{hpm3..hpm12}, hpm32h{hpm3h..hpm12h}, hpm_unimpl{3+MHPMCounterNum..31 and h}, mcinh{mcountinhibit}, mhpmev{mhpmevent3..31}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, near_wrap{0xFFFF_FFF0..0xFFFF_FFFE}, small{1..31 uimm range}
  - cp_inhibit = the counter's mcountinhibit bit at the write: bins on{1}, off{0}
  - cp_mcinh_w = written mcountinhibit bit class (mcountinhibit pairs only): bins cy{bit 0}, ir{bit 2}, hpm3{bit 3}, hpm4{bit 4}, hpm5{bit 5}, hpm6{bit 6}, hpm7{bit 7}, hpm8{bit 8}, hpm9{bit 9}, hpm10{bit 10}, hpm11{bit 11}, hpm12{bit 12}, tm_ro{bit 1}, hi_ro{bits 31:3+MHPMCounterNum}, all1{all bits}
- Crosses:
  - cr_fam_op = cp_fam x cp_op: bins cycle64_csrrw{cycle64 csrrw}, cycle64_csrrs{cycle64 csrrs}, cycle64_csrrc{cycle64 csrrc}, cycle64_csrrwi{cycle64 csrrwi}, cycle64_csrrsi{cycle64 csrrsi}, cycle64_csrrci{cycle64 csrrci}, instret64_csrrw{instret64 csrrw}, instret64_csrrs{instret64 csrrs}, instret64_csrrc{instret64 csrrc}, instret64_csrrwi{instret64 csrrwi}, instret64_csrrsi{instret64 csrrsi}, instret64_csrrci{instret64 csrrci}, hpm32_csrrw{hpm32 csrrw}, hpm32_csrrs{hpm32 csrrs}, hpm32_csrrc{hpm32 csrrc}, hpm32_csrrwi{hpm32 csrrwi}, hpm32_csrrsi{hpm32 csrrsi}, hpm32_csrrci{hpm32 csrrci}, hpm32h_csrrw{hpm32h csrrw}, hpm32h_csrrs{hpm32h csrrs}, hpm32h_csrrc{hpm32h csrrc}, hpm32h_csrrwi{hpm32h csrrwi}, hpm32h_csrrsi{hpm32h csrrsi}, hpm32h_csrrci{hpm32h csrrci}, hpm_unimpl_csrrw{hpm_unimpl csrrw}, hpm_unimpl_csrrs{hpm_unimpl csrrs}, hpm_unimpl_csrrc{hpm_unimpl csrrc}, hpm_unimpl_csrrwi{hpm_unimpl csrrwi}, hpm_unimpl_csrrsi{hpm_unimpl csrrsi}, hpm_unimpl_csrrci{hpm_unimpl csrrci}, mcinh_csrrw{mcinh csrrw}, mcinh_csrrs{mcinh csrrs}, mcinh_csrrc{mcinh csrrc}, mcinh_csrrwi{mcinh csrrwi}, mcinh_csrrsi{mcinh csrrsi}, mcinh_csrrci{mcinh csrrci}, mhpmev_csrrw{mhpmev csrrw}, mhpmev_csrrs{mhpmev csrrs}, mhpmev_csrrc{mhpmev csrrc}, mhpmev_csrrwi{mhpmev csrrwi}, mhpmev_csrrsi{mhpmev csrrsi}, mhpmev_csrrci{mhpmev csrrci}
  - cr_fam_wpat = cp_fam x cp_wpat: bins cycle64_rand{cycle64 rand}, cycle64_all1{cycle64 all1}, cycle64_all0{cycle64 all0}, cycle64_near_wrap{cycle64 near_wrap}, cycle64_small{cycle64 small}, instret64_rand{instret64 rand}, instret64_all1{instret64 all1}, instret64_all0{instret64 all0}, instret64_near_wrap{instret64 near_wrap}, instret64_small{instret64 small}, hpm32_rand{hpm32 rand}, hpm32_all1{hpm32 all1}, hpm32_all0{hpm32 all0}, hpm32_near_wrap{hpm32 near_wrap}, hpm32_small{hpm32 small}, hpm32h_rand{hpm32h rand}, hpm32h_all1{hpm32h all1}, hpm32h_all0{hpm32h all0}, hpm_unimpl_rand{hpm_unimpl rand}, hpm_unimpl_all1{hpm_unimpl all1}, mcinh_rand{mcinh rand}, mcinh_all1{mcinh all1}, mcinh_all0{mcinh all0}, mcinh_small{mcinh small}, mhpmev_rand{mhpmev rand}, mhpmev_all1{mhpmev all1}, mhpmev_all0{mhpmev all0}
  - cr_csr_inhibit = cp_csr x cp_inhibit (writable counters): bins mcycle_on{mcycle on}, mcycle_off{mcycle off}, mcycleh_on{mcycleh on}, mcycleh_off{mcycleh off}, minstret_on{minstret on}, minstret_off{minstret off}, minstreth_on{minstreth on}, minstreth_off{minstreth off}, hpm3_on{hpm3 on}, hpm3_off{hpm3 off}, hpm4_on{hpm4 on}, hpm4_off{hpm4 off}, hpm5_on{hpm5 on}, hpm5_off{hpm5 off}, hpm6_on{hpm6 on}, hpm6_off{hpm6 off}, hpm7_on{hpm7 on}, hpm7_off{hpm7 off}, hpm8_on{hpm8 on}, hpm8_off{hpm8 off}, hpm9_on{hpm9 on}, hpm9_off{hpm9 off}, hpm10_on{hpm10 on}, hpm10_off{hpm10 off}, hpm11_on{hpm11 on}, hpm11_off{hpm11 off}, hpm12_on{hpm12 on}, hpm12_off{hpm12 off}
  - cr_mcinh_w_op = cp_mcinh_w x cp_op: bins cy_csrrs{cy csrrs}, cy_csrrc{cy csrrc}, ir_csrrs{ir csrrs}, ir_csrrc{ir csrrc}, hpm3_csrrsi{hpm3 csrrsi}, hpm12_csrrs{hpm12 csrrs}, tm_ro_csrrw{tm_ro csrrw}, hi_ro_csrrw{hi_ro csrrw}, all1_csrrw{all1 csrrw}, all1_csrrs{all1 csrrs}
- Adopted (riscv-dv): none
- TP items: TP-CSR-058, TP-CSR-059, TP-CSR-060, TP-CSR-061, TP-CSR-062, TP-CSR-064, TP-CSR-066, TP-CSR-069, TP-CSR-070, TP-CSR-071, TP-CSR-073, TP-CSR-101, TP-CSR-120

### CG-CSR-005: gen_cg_csr_umode_alias
- Features: F-CSR-015, F-CSR-050, F-CSR-053, F-CSR-054, F-CSR-055, F-CSR-056, F-CSR-057, F-CSR-011
  (parent of folded bins hosted here)
- Sample: rvfi_valid with a CSR instruction to 0xC00..0xC9F (any mode, trapped or not); condition: rvfi_valid && is_csr_insn && addr[11:8] == 0xC && addr[7:5] inside {0, 4}; anti-vacuity: only alias accesses sample; a hit proves an alias of that index was accessed in that mode with that mcounteren state and the recorded outcome.
- Coverpoints:
  - cp_alias = addr class: bins cycle{0xC00}, cycleh{0xC80}, instret{0xC02}, instreth{0xC82}, hpm3{0xC03}, hpm4{0xC04}, hpm5{0xC05}, hpm6{0xC06}, hpm7{0xC07}, hpm8{0xC08}, hpm9{0xC09}, hpm10{0xC0A}, hpm11{0xC0B}, hpm12{0xC0C}, hpm3h{0xC83}, hpm4h{0xC84}, hpm5h{0xC85}, hpm6h{0xC86}, hpm7h{0xC87}, hpm8h{0xC88}, hpm9h{0xC89}, hpm10h{0xC8A}, hpm11h{0xC8B}, hpm12h{0xC8C}, hpm_unimpl{0xC03+MHPMCounterNum..0xC1F}, hpm_unimpl_h{0xC83+MHPMCounterNum..0xC9F}, time{0xC01}, timeh{0xC81}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_mcen_bit = mcounteren[addr[4:0]] as predicted by the CSR model (na for 3+MHPMCounterNum..31): bins set{1}, clr{0}, na{index 3+MHPMCounterNum..31 or 1}
  - cp_form = op form after demotion: bins rd_only{csrrs/csrrc x0, csrrsi/csrrci 0}, wr{any write op}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_mcen_onehot = mcounteren value class at the access: bins none{0}, cy{bit 0 only}, ir{bit 2 only}, hpm3{bit 3 only}, hpm4{bit 4 only}, hpm5{bit 5 only}, hpm6{bit 6 only}, hpm7{bit 7 only}, hpm8{bit 8 only}, hpm9{bit 9 only}, hpm10{bit 10 only}, hpm11{bit 11 only}, hpm12{bit 12 only}, multi{two or more bits}
  - cp_diag = (one-hot mcounteren index == alias index): bins diag{equal}, offdiag{different}, na{not one-hot}
- Crosses:
  - cr_priv_bit_trap = cp_priv x cp_mcen_bit x cp_trap (rd_only): bins u_set_ok{u set ok}, u_clr_trap{u clr trap}, u_na_trap{u na trap}, m_set_ok{m set ok}, m_clr_ok{m clr ok}, m_na_ok{m na ok}; ignore u_set_trap and u_clr_ok: the gate is deterministic; ignore m x trap for implemented aliases: M-mode reads never trap
  - cr_alias_u_ok: RETIRED (S-7: three filtered projections of one cross merged into cr_alias_priv_trap as u_*_ok)
  - cr_alias_u_trap: RETIRED (S-7: merged into cr_alias_priv_trap as u_*_trap)
  - cr_alias_m: RETIRED (S-7: merged into cr_alias_priv_trap as the m_* bins)
  - cr_alias_priv_trap = cp_alias x cp_priv x cp_trap (cp_form == rd_only): bins u_cycle_ok{u cycle ok}, u_cycleh_ok{u cycleh ok}, u_instret_ok{u instret ok}, u_instreth_ok{u instreth ok}, u_hpm3_ok{u hpm3 ok}, u_hpm4_ok{u hpm4 ok}, u_hpm5_ok{u hpm5 ok}, u_hpm6_ok{u hpm6 ok}, u_hpm7_ok{u hpm7 ok}, u_hpm8_ok{u hpm8 ok}, u_hpm9_ok{u hpm9 ok}, u_hpm10_ok{u hpm10 ok}, u_hpm11_ok{u hpm11 ok}, u_hpm12_ok{u hpm12 ok}, u_hpm3h_ok{u hpm3h ok}, u_hpm4h_ok{u hpm4h ok}, u_hpm5h_ok{u hpm5h ok}, u_hpm6h_ok{u hpm6h ok}, u_hpm7h_ok{u hpm7h ok}, u_hpm8h_ok{u hpm8h ok}, u_hpm9h_ok{u hpm9h ok}, u_hpm10h_ok{u hpm10h ok}, u_hpm11h_ok{u hpm11h ok}, u_hpm12h_ok{u hpm12h ok}, u_cycle_trap{u cycle trap}, u_cycleh_trap{u cycleh trap}, u_instret_trap{u instret trap}, u_instreth_trap{u instreth trap}, u_hpm3_trap{u hpm3 trap}, u_hpm4_trap{u hpm4 trap}, u_hpm5_trap{u hpm5 trap}, u_hpm6_trap{u hpm6 trap}, u_hpm7_trap{u hpm7 trap}, u_hpm8_trap{u hpm8 trap}, u_hpm9_trap{u hpm9 trap}, u_hpm10_trap{u hpm10 trap}, u_hpm11_trap{u hpm11 trap}, u_hpm12_trap{u hpm12 trap}, u_hpm3h_trap{u hpm3h trap}, u_hpm12h_trap{u hpm12h trap}, u_hpm_unimpl_trap{u hpm_unimpl trap}, u_hpm_unimpl_h_trap{u hpm_unimpl_h trap}, u_time_trap{u time trap}, u_timeh_trap{u timeh trap}, m_time_trap{m time trap}, m_timeh_trap{m timeh trap}, m_hpm_unimpl_ok{m hpm_unimpl ok}, m_hpm_unimpl_h_ok{m hpm_unimpl_h ok}, m_cycle_ok{m cycle ok}, m_cycleh_ok{m cycleh ok}, m_instret_ok{m instret ok}, m_instreth_ok{m instreth ok}, m_hpm3_ok{m hpm3 ok}, m_hpm12_ok{m hpm12 ok}, m_hpm3h_ok{m hpm3h ok}; ignore u x {hpm_unimpl, hpm_unimpl_h, time, timeh} x ok: never legal in U; ignore m x implemented alias x trap: M-mode reads of implemented aliases never trap; ignore m x {time, timeh} x ok: 0xC01/0xC81 are unimplemented
  - cr_diag_u = cp_diag x cp_priv(u) x cp_trap: bins diag_ok{diag ok}, offdiag_trap{offdiag trap}; ignore diag_trap and offdiag_ok: deterministic gate
  - cr_onehot_alias = cp_mcen_onehot x cp_alias (u, ok): bins cy_cycle{cy cycle}, cy_cycleh{cy cycleh}, ir_instret{ir instret}, ir_instreth{ir instreth}, hpm3_hpm3{hpm3 hpm3}, hpm4_hpm4{hpm4 hpm4}, hpm5_hpm5{hpm5 hpm5}, hpm6_hpm6{hpm6 hpm6}, hpm7_hpm7{hpm7 hpm7}, hpm8_hpm8{hpm8 hpm8}, hpm9_hpm9{hpm9 hpm9}, hpm10_hpm10{hpm10 hpm10}, hpm11_hpm11{hpm11 hpm11}, hpm12_hpm12{hpm12 hpm12}, hpm12_hpm12h{hpm12 hpm12h}
  - cr_wr_alias = cp_form(wr) x cp_priv x cp_trap: bins wr_m_trap{wr m trap}, wr_u_trap{wr u trap}; ignore wr x ok: illegal_csr_write is unconditional in the read-only range
- Adopted (riscv-dv): none
- TP items: TP-CSR-011, TP-CSR-015, TP-CSR-051, TP-CSR-053, TP-CSR-054, TP-CSR-055, TP-CSR-056, TP-CSR-057, TP-CSR-111, TP-CSR-117, TP-PRV-033

### CG-CSR-006: gen_cg_csr_machine_info
- Features: F-CSR-011, F-CSR-013, F-CSR-019, F-CSR-020
- Sample: rvfi_valid with a CSR instruction to 0xF11..0xF15 (trapped or not); condition: rvfi_valid && is_csr_insn && addr inside {0xF11..0xF15}; anti-vacuity: only machine-information accesses sample; a hit proves that CSR was read or write-attempted in that mode with the recorded hart_id_i class.
- Coverpoints:
  - cp_csr = addr: bins mvendorid{0xF11}, marchid{0xF12}, mimpid{0xF13}, mhartid{0xF14}, mconfigptr{0xF15}
  - cp_form = op form after demotion: bins rd_only{csrrs/csrrc x0, csrrsi/csrrci 0}, wr{any write op}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_hartid_val = hart_id_i value class iff (cp_csr == mhartid && cp_form == rd_only && cp_trap == ok): bins zero{0}, all1{0xFFFF_FFFF}, walking1{single bit set}, rand{other}
- Crosses:
  - cr_csr_form_trap: RETIRED (S-7: merged into cr_csr_priv_form_trap)
  - cr_csr_u: RETIRED (S-7: merged into cr_csr_priv_form_trap as the *_u bins)
  - cr_csr_priv_form_trap = cp_csr x cp_priv x cp_form x cp_trap: bins mvendorid_rd_ok{mvendorid m rd_only ok}, mvendorid_wr_trap{mvendorid m wr trap}, marchid_rd_ok{marchid m rd_only ok}, marchid_wr_trap{marchid m wr trap}, mimpid_rd_ok{mimpid m rd_only ok}, mimpid_wr_trap{mimpid m wr trap}, mhartid_rd_ok{mhartid m rd_only ok}, mhartid_wr_trap{mhartid m wr trap}, mconfigptr_rd_ok{mconfigptr m rd_only ok}, mconfigptr_wr_trap{mconfigptr m wr trap}, mvendorid_u{mvendorid u any-form trap}, marchid_u{marchid u any-form trap}, mimpid_u{mimpid u any-form trap}, mhartid_u{mhartid u any-form trap}, mconfigptr_u{mconfigptr u any-form trap}; ignore m x rd_only x trap and m x wr x ok: the read-only range rule is unconditional; ignore u x ok: 0xF11..0xF15 are M-level, every U-mode access traps
  - cr_hartid_val_rd: RETIRED (S-7 identity cross of cp_hartid_val, which is mhartid-read-only by its iff; TP-CSR-020 references cp_hartid_val.*)
- Adopted (riscv-dv): none
- TP items: TP-CSR-011, TP-CSR-013, TP-CSR-019, TP-CSR-020, TP-CSR-110, TP-CSR-111

### CG-CSR-007: gen_cg_csr_debug_csr
- Features: F-CSR-017, F-CSR-018, F-CSR-074, F-CSR-075, F-CSR-076, F-CSR-077, F-CSR-078, F-CSR-079,
  F-DBG-012 (parent of folded bins hosted here)
- Sample: rvfi_valid with a CSR instruction to 0x7B0..0x7BF (trapped or not) plus, for write pairs in debug mode, the gen_chk_csr_readback pair closure; condition: rvfi_valid && is_csr_insn && addr[11:4] == 0x7B; anti-vacuity: only debug-CSR accesses sample; a hit proves an access of that form happened with the recorded debug-mode state, so the trap/no-trap and WARL result was checked.
- Coverpoints:
  - cp_csr = addr: bins dcsr{0x7B0}, dpc{0x7B1}, dscratch0{0x7B2}, dscratch1{0x7B3}, hole{0x7B4..0x7BF}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_form = op form after demotion: bins rd_only{demoted reads}, wr{write ops}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_op = rvfi_insn[14:12]: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class iff (cp_form == wr && cp_dbg == dbg && readback pair closed): bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only: dcsr DCSR_W_MASK, dpc bits 31:1}, illegal_only{read-only bits only}
  - cp_dcsr_prv_w = written dcsr[1:0] iff (cp_csr == dcsr && cp_form == wr && cp_dbg == dbg): bins u{00}, s{01}, h{10}, m{11}
  - cp_dcsr_ebreakm_w = written dcsr[15] iff (cp_csr == dcsr && cp_form == wr && cp_dbg == dbg): bins b0{0}, b1{1}
  - cp_dcsr_ebreaku_w = written dcsr[12] iff (cp_csr == dcsr && cp_form == wr && cp_dbg == dbg): bins b0{0}, b1{1}
  - cp_dcsr_ebreaks_w = written dcsr[13] iff (cp_csr == dcsr && cp_form == wr && cp_dbg == dbg): bins b0{0}, b1{1: B15 stimulus, the read-back is predicted 0 (TP-CSR-075/076 expected-fail)}
  - cp_dcsr_step_w = written dcsr[2] iff (cp_csr == dcsr && cp_form == wr && cp_dbg == dbg): bins b0{0}, b1{1}
  - cp_dcsr_ro_w = any read-only dcsr bit written 1 iff (cp_csr == dcsr && cp_form == wr && cp_dbg == dbg); read-only set = ~DCSR_W_MASK: xdebugver 31:28, zero fields 27:16 and 14 and 5, ebreaks 13 (B15: hardwired 0 without S-mode per core_registers.xml:163-172, the checker predicts 0), stepie 11, stopcount 10, stoptime 9, cause 8:6, mprven 4, nmip 3 (B5: owner TP-DBG-021, excluded from the CSR compare): bins none{0}, some{1}
  - cp_dpc_lo_w = written dpc[0] iff (cp_csr == dpc && cp_form == wr && cp_dbg == dbg): bins b0{0}, b1{1}
- Crosses:
  - cr_csr_dbg_trap = cp_csr x cp_dbg x cp_trap: bins dcsr_nondbg_trap{dcsr nondbg trap}, dpc_nondbg_trap{dpc nondbg trap}, dscratch0_nondbg_trap{dscratch0 nondbg trap}, dscratch1_nondbg_trap{dscratch1 nondbg trap}, dcsr_dbg_ok{dcsr dbg ok}, dpc_dbg_ok{dpc dbg ok}, dscratch0_dbg_ok{dscratch0 dbg ok}, dscratch1_dbg_ok{dscratch1 dbg ok}, hole_dbg_trap{hole dbg trap}, hole_nondbg_trap{hole nondbg trap}; ignore {dcsr, dpc, dscratch0, dscratch1} x nondbg x ok: illegal_csr_dbg unconditional; ignore {dcsr, dpc, dscratch0, dscratch1} x dbg x trap: legal in debug mode; ignore hole x ok: unimplemented
  - cr_csr_form_nondbg = cp_csr x cp_form (nondbg, trap): bins dcsr_rd{dcsr rd_only}, dcsr_wr{dcsr wr}, dpc_rd{dpc rd_only}, dpc_wr{dpc wr}, dscratch0_rd{dscratch0 rd_only}, dscratch0_wr{dscratch0 wr}, dscratch1_rd{dscratch1 rd_only}, dscratch1_wr{dscratch1 wr}
  - cr_csr_op_dbg = cp_csr x cp_op (dbg, ok): bins dcsr_csrrw{dcsr csrrw}, dcsr_csrrs{dcsr csrrs}, dcsr_csrrc{dcsr csrrc}, dcsr_csrrwi{dcsr csrrwi}, dcsr_csrrsi{dcsr csrrsi}, dcsr_csrrci{dcsr csrrci}, dpc_csrrw{dpc csrrw}, dpc_csrrs{dpc csrrs}, dpc_csrrc{dpc csrrc}, dpc_csrrwi{dpc csrrwi}, dpc_csrrsi{dpc csrrsi}, dpc_csrrci{dpc csrrci}, dscratch0_csrrw{dscratch0 csrrw}, dscratch0_csrrs{dscratch0 csrrs}, dscratch0_csrrc{dscratch0 csrrc}, dscratch0_csrrwi{dscratch0 csrrwi}, dscratch0_csrrsi{dscratch0 csrrsi}, dscratch0_csrrci{dscratch0 csrrci}, dscratch1_csrrw{dscratch1 csrrw}, dscratch1_csrrs{dscratch1 csrrs}, dscratch1_csrrc{dscratch1 csrrc}, dscratch1_csrrwi{dscratch1 csrrwi}, dscratch1_csrrsi{dscratch1 csrrsi}, dscratch1_csrrci{dscratch1 csrrci}
  - cr_csr_wpat_dbg = cp_csr x cp_wpat (dbg, ok): bins dcsr_rand{dcsr rand}, dcsr_all1{dcsr all1}, dcsr_all0{dcsr all0}, dcsr_legal{dcsr legal_only}, dcsr_illegal{dcsr illegal_only}, dpc_rand{dpc rand}, dpc_all1{dpc all1}, dpc_all0{dpc all0}, dpc_legal{dpc legal_only}, dpc_illegal{dpc illegal_only bit0}, dscratch0_rand{dscratch0 rand}, dscratch0_all1{dscratch0 all1}, dscratch0_all0{dscratch0 all0}, dscratch1_rand{dscratch1 rand}, dscratch1_all1{dscratch1 all1}, dscratch1_all0{dscratch1 all0}; ignore dscratch x {legal_only, illegal_only}: all bits writable
  - cr_prv_w_op = cp_dcsr_prv_w x cp_op: bins prv_s_csrrw{s csrrw}, prv_h_csrrw{h csrrw}, prv_u_csrrw{u csrrw}, prv_m_csrrw{m csrrw}, prv_s_csrrs{s csrrs}, prv_h_csrrsi{h csrrsi}, prv_u_csrrc{u csrrc}
  - cr_dcsr_bits = cp_dcsr_ebreakm_w x cp_dcsr_ebreaku_w x cp_dcsr_ebreaks_w x cp_dcsr_step_w: bins all0{0 0 0 0}, all1{1 1 1 1}, ebreakm_only{1 0 0 0}, ebreaku_only{0 1 0 0}, ebreaks_only{0 0 1 0}, step_only{0 0 0 1}, ebreakm_u{1 1 0 0}, step_ebreakm{1 0 0 1}
  - cr_dcsr_ro_w = cp_dcsr_ro_w x cp_op: bins some_csrrw{some csrrw}, some_csrrs{some csrrs}, none_csrrw{none csrrw}
  - cr_dpc_lo = cp_dpc_lo_w x cp_op: bins b1_csrrw{b1 csrrw}, b1_csrrsi{b1 csrrsi}, b0_csrrw{b0 csrrw}
  - cr_u_nondbg = cp_priv(u) x cp_csr x cp_trap(trap): bins u_dcsr{u dcsr trap}, u_dpc{u dpc trap}, u_dscratch0{u dscratch0 trap}, u_dscratch1{u dscratch1 trap}
- Adopted (riscv-dv): none
- TP items: TP-CSR-017, TP-CSR-018, TP-CSR-074, TP-CSR-075, TP-CSR-076, TP-CSR-077, TP-CSR-078, TP-CSR-079, TP-CSR-108, TP-CSR-110, TP-CSR-118

### CG-CSR-008: gen_cg_csr_trigger_csr
- Features: F-CSR-080, F-CSR-081, F-CSR-082, F-CSR-083, F-CSR-084, F-TRG-007 (parent of folded bins
  hosted here)
- Sample: rvfi_valid with a CSR instruction to 0x7A0..0x7A3, 0x7A8, 0x7AA, 0x5A8 (trapped or not); condition: rvfi_valid && is_csr_insn && addr in the trigger set; anti-vacuity: only trigger-CSR accesses sample; a hit proves an access of that form happened in the recorded debug/privilege state so the write-effective / write-ignored prediction was compared on the next read.
- Coverpoints:
  - cp_csr = addr: bins tselect{0x7A0}, tdata1{0x7A1}, tdata2{0x7A2}, tdata3{0x7A3}, mcontext{0x7A8}, mscontext{0x7AA}, scontext{0x5A8}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_form = op form after demotion: bins rd_only{demoted reads}, wr{write ops}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_op = rvfi_insn[14:12]: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class iff (cp_form == wr): bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only: tdata1 bit 2, tdata2 all, tselect none}, illegal_only{read-only bits only}
  - cp_tsel_w = written tselect value class iff (cp_csr == tselect && cp_form == wr): bins zero{0}, ge_num{>= DbgHwBreakNum}
  - cp_tdata1_exec_w = written tdata1[2] iff (cp_csr == tdata1 && cp_form == wr): bins b0{0}, b1{1}
  - cp_tdata1_other_w = any tdata1 bit other than 2 written 1 iff (cp_csr == tdata1 && cp_form == wr): bins none{0}, some{1}
- Crosses:
  - cr_csr_dbg_form = cp_csr x cp_dbg x cp_form (m, ok): bins tselect_nondbg_wr{tselect nondbg wr}, tselect_dbg_wr{tselect dbg wr}, tdata1_nondbg_wr{tdata1 nondbg wr}, tdata1_dbg_wr{tdata1 dbg wr}, tdata2_nondbg_wr{tdata2 nondbg wr}, tdata2_dbg_wr{tdata2 dbg wr}, tdata3_nondbg_wr{tdata3 nondbg wr (B3 evidence)}, tdata3_dbg_wr{tdata3 dbg wr (B3 evidence)}, mcontext_nondbg_wr{mcontext nondbg wr (B3 evidence)}, mscontext_nondbg_wr{mscontext nondbg wr (B3 evidence)}, scontext_nondbg_wr{scontext nondbg wr (B3 evidence)}, tselect_nondbg_rd{tselect nondbg rd_only}, tdata1_nondbg_rd{tdata1 nondbg rd_only}, tdata2_nondbg_rd{tdata2 nondbg rd_only}, tdata3_nondbg_rd{tdata3 nondbg rd_only (B3 evidence)}, mcontext_nondbg_rd{mcontext nondbg rd_only (B3 evidence)}, mscontext_nondbg_rd{mscontext nondbg rd_only (B3 evidence)}, scontext_nondbg_rd{scontext nondbg rd_only (B3 evidence)}, tdata1_dbg_rd{tdata1 dbg rd_only}, tdata2_dbg_rd{tdata2 dbg rd_only}, tselect_dbg_rd{tselect dbg rd_only}
  - cr_csr_u = cp_csr x cp_priv(u) x cp_trap(trap): bins tselect_u{tselect u trap}, tdata1_u{tdata1 u trap}, tdata2_u{tdata2 u trap}, tdata3_u{tdata3 u trap}, mcontext_u{mcontext u trap}, mscontext_u{mscontext u trap}, scontext_u{scontext u trap}
  - cr_csr_op_dbg = cp_csr x cp_op (dbg, wr): bins tselect_csrrw{tselect csrrw}, tselect_csrrs{tselect csrrs}, tselect_csrrc{tselect csrrc}, tselect_csrrwi{tselect csrrwi}, tselect_csrrsi{tselect csrrsi}, tselect_csrrci{tselect csrrci}, tdata1_csrrw{tdata1 csrrw}, tdata1_csrrs{tdata1 csrrs}, tdata1_csrrc{tdata1 csrrc}, tdata1_csrrwi{tdata1 csrrwi}, tdata1_csrrsi{tdata1 csrrsi}, tdata1_csrrci{tdata1 csrrci}, tdata2_csrrw{tdata2 csrrw}, tdata2_csrrs{tdata2 csrrs}, tdata2_csrrc{tdata2 csrrc}, tdata2_csrrwi{tdata2 csrrwi}, tdata2_csrrsi{tdata2 csrrsi}, tdata2_csrrci{tdata2 csrrci}
  - cr_csr_wpat = cp_csr x cp_wpat (wr): bins tselect_rand{tselect rand}, tselect_all1{tselect all1}, tdata1_rand{tdata1 rand}, tdata1_all1{tdata1 all1}, tdata1_all0{tdata1 all0}, tdata1_legal{tdata1 legal_only}, tdata1_illegal{tdata1 illegal_only}, tdata2_rand{tdata2 rand}, tdata2_all1{tdata2 all1}, tdata2_all0{tdata2 all0}, tdata3_all1{tdata3 all1}, mcontext_all1{mcontext all1}, mscontext_all1{mscontext all1}, scontext_all1{scontext all1}
  - cr_tdata1_w = cp_tdata1_exec_w x cp_tdata1_other_w x cp_dbg: bins dbg_e1_none{dbg 1 none}, dbg_e1_some{dbg 1 some}, dbg_e0_some{dbg 0 some}, dbg_e0_none{dbg 0 none}, nondbg_e1_none{nondbg 1 none}, nondbg_e1_some{nondbg 1 some}
  - cr_tsel_w_dbg = cp_tsel_w x cp_dbg: bins zero_dbg{zero dbg}, ge_dbg{ge_num dbg}, zero_nondbg{zero nondbg}, ge_nondbg{ge_num nondbg}
- Adopted (riscv-dv): none
- TP items: TP-CSR-080, TP-CSR-081, TP-CSR-082, TP-CSR-083, TP-CSR-084, TP-CSR-108, TP-CSR-110, TP-CSR-118

### CG-CSR-009: gen_cg_csr_cpuctrlsts
- Features: F-CSR-085, F-CSR-086, F-CSR-087, F-CSR-088, F-CSR-089, F-CSR-090, F-CSR-091, F-SEC-022
  (parent of folded bins hosted here)
- Sample: (a) rvfi_valid with a CSR instruction to 0x7C0, (b) a synchronous trap retirement (rvfi_trap with a non-interrupt cause) outside debug mode, (c) an mret retirement, (d) a double_fault_seen_o pulse, (e) an interrupt/NMI/debug entry observed on RVFI; condition: any of a..e; anti-vacuity: each event class is distinct and the sync_exc_seen / double_fault_seen model state is sampled with it, so a hit proves the model saw that transition and gen_chk_double_fault / gen_chk_csr_readback compared the resulting bits.
- Coverpoints:
  - cp_event = event class: bins sw_rd{CSR read of 0x7C0}, sw_wr{CSR write op to 0x7C0}, hw_sync_set{sync exception taken outside debug}, hw_mret_clr{mret retired}, hw_dbl_pulse{double_fault_seen_o pulse}, hw_irq{interrupt or NMI entry}, hw_dbg{debug entry or exception in debug mode}
  - cp_op = rvfi_insn[14:12] iff (cp_event inside {sw_rd, sw_wr}): bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class iff (cp_event == sw_wr): bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{bits 7:0 only}, illegal_only{bits 31:8 only}
  - cp_icache_w = written bit 0 iff (cp_event == sw_wr): bins b0{0}, b1{1}
  - cp_dit_w = written bit 1 iff (cp_event == sw_wr): bins b0{0}, b1{1}
  - cp_dummy_en_w = written bit 2 iff (cp_event == sw_wr): bins b0{0}, b1{1}
  - cp_dummy_mask_w = written bits 5:3 iff (cp_event == sw_wr): bins m0{000}, m1{001}, m2{010}, m3{011}, m4{100}, m5{101}, m6{110}, m7{111}
  - cp_sync_w = written bit 6 iff (cp_event == sw_wr): bins b0{0}, b1{1}
  - cp_dbl_w = written bit 7 iff (cp_event == sw_wr): bins b0{0}, b1{1}
  - cp_key_w = written bit 8 iff (cp_event == sw_wr): bins b0{0}, b1{1}
  - cp_hi_w = written bits 31:9 iff (cp_event == sw_wr): bins zero{0}, nonzero{!=0}
  - cp_key_pin = ic_scr_key_valid_i one cycle before the read iff (cp_event == sw_rd): bins lo{0}, hi{1}
  - cp_sync_state = sync_exc_seen model value before the event: bins s0{0}, s1{1}
  - cp_dbl_state = double_fault_seen model value before the event: bins d0{0}, d1{1}
  - cp_trap_kind = kind of hw event iff (cp_event inside {hw_sync_set, hw_mret_clr, hw_dbl_pulse, hw_irq, hw_dbg}): bins sync_exc{exception outside debug}, irq{interrupt}, nmi{NMI}, dbg_entry{debug entry}, dbgmode_exc{exception while in debug mode}
  - cp_priv = rvfi_mode iff (cp_event inside {sw_rd, sw_wr}): bins m{3}, u{0}
  - cp_trap = rvfi_trap iff (cp_event inside {sw_rd, sw_wr}): bins ok{0}, trap{1}
- Crosses:
  - cr_dbl_detect = cp_event x cp_sync_state x cp_trap_kind: bins sync_s0_set{hw_sync_set s0 sync_exc}, sync_s1_pulse{hw_dbl_pulse s1 sync_exc}, s1_irq_nopulse{hw_irq s1 irq}, s1_nmi_nopulse{hw_irq s1 nmi}, s1_dbg_nopulse{hw_dbg s1 dbg_entry}, s1_dbgmode_exc_nopulse{hw_dbg s1 dbgmode_exc}, mret_clr_s1{hw_mret_clr s1}, mret_clr_s0{hw_mret_clr s0}
  - cr_sw_sync = cp_event(sw_wr) x cp_sync_w x cp_sync_state: bins set_s0{b1 s0}, clr_s1{b0 s1}, keep_s1{b1 s1}, keep_s0{b0 s0}
  - cr_sw_dbl = cp_event(sw_wr) x cp_dbl_w x cp_dbl_state: bins set_d0{b1 d0}, clr_d1{b0 d1}, keep_d1{b1 d1}, keep_d0{b0 d0}
  - cr_key_rd: RETIRED (S-7 identity cross of cp_key_pin, which is sw_rd-only by its iff; items reference cp_key_pin.lo / cp_key_pin.hi)
  - cr_key_w = cp_key_w x cp_key_pin (sw_wr then read): bins w1_lo{b1 lo}, w1_hi{b1 hi}, w0_hi{b0 hi}
  - cr_mask_en = cp_dummy_mask_w x cp_dummy_en_w(b1): bins m0_en{m0}, m1_en{m1}, m2_en{m2}, m3_en{m3}, m4_en{m4}, m5_en{m5}, m6_en{m6}, m7_en{m7}
  - cr_ic_dit = cp_icache_w x cp_dit_w: bins ic0_dit0{0 0}, ic1_dit0{1 0}, ic0_dit1{0 1}, ic1_dit1{1 1}
  - cr_wpat_op = cp_wpat x cp_op: bins rand_csrrw{rand csrrw}, rand_csrrs{rand csrrs}, rand_csrrc{rand csrrc}, all1_csrrw{all1 csrrw}, all0_csrrw{all0 csrrw}, legal_csrrsi{legal_only csrrsi}, legal_csrrci{legal_only csrrci}, illegal_csrrw{illegal_only csrrw}, all1_csrrs{all1 csrrs}
  - cr_hi_w = cp_hi_w x cp_op: bins nz_csrrw{nonzero csrrw}, nz_csrrs{nonzero csrrs}
  - cr_u_trap = cp_priv(u) x cp_event x cp_trap(trap): bins u_rd_trap{u sw_rd trap}, u_wr_trap{u sw_wr trap}
- Adopted (riscv-dv): none
- TP items: TP-CSR-085, TP-CSR-086, TP-CSR-087, TP-CSR-088, TP-CSR-089, TP-CSR-090, TP-CSR-091, TP-CSR-094, TP-CSR-109, TP-CSR-110

### CG-CSR-010: gen_cg_csr_secureseed
- Features: F-CSR-092, F-CSR-093
- Sample: rvfi_valid with a CSR instruction to 0x7C1 (trapped or not); condition: rvfi_valid && is_csr_insn && addr == 0x7C1; anti-vacuity: only secureseed accesses sample; the boundary form of the write/read distinction is the retirement gap to the next record (a write op flushes, csr_pipe_flush rtl/ibex_id_stage.sv:593-597, a demoted read does not), so a hit on a cr_op_form_gap bin proves that op form retired with the bubble its class implies; the pulse coverpoint comes from the probe candidate below (coverage-only) and a hit on a pulse bin proves the reseed fired for exactly that op form.
- Coverpoints:
  - cp_op = rvfi_insn[14:12]: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_rs1 = rvfi_insn[19:15]: bins zero{0}, nonzero{1..31}
  - cp_form = op form after demotion: bins rd_only{demoted reads}, wr{write ops}
  - cp_pulse = dummy_instr_seed_en_o observed in the write cycle (probe-gated P7, not in manifest): bins none{0}, pulse{1}
  - cp_gap = cycles between this retirement and the next RVFI retirement, measured only with knob:imem_gnt_delay = same_cycle, knob:imem_rvalid_delay = min1, no dummy in the gap and no other stall source (S-4): bins g1{1: no flush, demoted read}, g2plus{>= 2: flush bubble, write op}
  - cp_seed_val = written seed value derived from RVFI iff (cp_form == wr) (csrrw: rs1 value; csrrwi: uimm; csrrs: rs1 value and csrrsi: uimm, because the read value is 0; csrrc/csrrci: 0), i.e. the value csr_wdata_int carries, without a probe: bins zero{0}, all1{0xFFFF_FFFF}, rand{other}
  - cp_dummy_en = cpuctrlsts.dummy_instr_en (CSR model) at the write iff (cp_form == wr): bins off{0}, on{1}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
- Crosses:
  - cr_op_form_pulse = cp_op x cp_rs1 x cp_pulse: bins csrrw_nz_pulse{csrrw nonzero pulse}, csrrw_x0_pulse{csrrw zero pulse}, csrrwi_0_pulse{csrrwi zero pulse}, csrrwi_nz_pulse{csrrwi nonzero pulse}, csrrs_nz_pulse{csrrs nonzero pulse}, csrrc_nz_pulse{csrrc nonzero pulse}, csrrsi_nz_pulse{csrrsi nonzero pulse}, csrrci_nz_pulse{csrrci nonzero pulse}, csrrs_x0_none{csrrs zero none}, csrrc_x0_none{csrrc zero none}, csrrsi_0_none{csrrsi zero none}, csrrci_0_none{csrrci zero none}; ignore demoted reads x pulse: csr_we_int is 0 for READ; ignore write forms x none in M-mode: the pulse is unconditional on csr_we_int
  - cr_op_form_gap = cp_op x cp_rs1 x cp_gap (M-mode, no trap): bins csrrw_nz_flush{csrrw nonzero g2plus}, csrrw_x0_flush{csrrw zero g2plus}, csrrwi_0_flush{csrrwi zero g2plus}, csrrwi_nz_flush{csrrwi nonzero g2plus}, csrrs_nz_flush{csrrs nonzero g2plus}, csrrc_nz_flush{csrrc nonzero g2plus}, csrrsi_nz_flush{csrrsi nonzero g2plus}, csrrci_nz_flush{csrrci nonzero g2plus}, csrrs_x0_g1{csrrs zero g1}, csrrc_x0_g1{csrrc zero g1}, csrrsi_0_g1{csrrsi zero g1}, csrrci_0_g1{csrrci zero g1}; ignore write forms x g1: a write op always flushes (rtl/ibex_id_stage.sv:593-597); ignore demoted reads x g2plus: no flush for a READ under the min-latency qualifier
  - cr_seed_en = cp_seed_val x cp_dummy_en (wr): bins zero_on{zero on}, all1_on{all1 on}, rand_on{rand on}, rand_off{rand off}, zero_off{zero off}
  - cr_rd_value: RETIRED (S-7 single-bin cross; replaced by cr_form_priv_trap.rd_m_ok)
  - cr_u: RETIRED (S-7 single-bin cross; replaced by cr_form_priv_trap.rd_u_trap / wr_u_trap)
  - cr_form_priv_trap = cp_form x cp_priv x cp_trap: bins rd_m_ok{rd_only m ok: the read returns 0}, wr_m_ok{wr m ok}, rd_u_trap{rd_only u trap}, wr_u_trap{wr u trap}; ignore m x trap: 0x7C1 is an implemented M-level address, never illegal in M; ignore u x ok: csr[9:8] = 11 always traps in U
- Probe status: candidate P7 (cs_registers_i.dummy_instr_seed_en_o / dummy_instr_seed_o and csr_wdata_int) is PROPOSED in dv/auto_dv/docs/gen_probe_register.md, Critic ruling pending; cp_pulse and cr_op_form_pulse are coverage-only, excluded from the Bins lines, the CSV and the manifests until ruled (rtl-arch T-053 UNOBSERVABLE rows TP-CSR-002/092/093); cr_op_form_gap is the boundary equivalent the items list
- Adopted (riscv-dv): none
- TP items: TP-CSR-002, TP-CSR-092, TP-CSR-093, TP-CSR-109, TP-CSR-110

### CG-CSR-011: gen_cg_csr_pmp_warl
- Features: F-CSR-094, F-CSR-095, F-CSR-096, F-CSR-098
- Sample: gen_chk_csr_readback pair completion for pmpcfg0..3, pmpaddr0..15, mseccfg, mseccfgh, sampled once per 8-bit pmpcfg entry for the entry coverpoints; condition: pair closed; anti-vacuity: as CG-CSR-002; the entry class is computed from the pre-write PMP state so a hit proves the WARL rule of that class was exercised and compared (PMP semantics themselves belong to the PMP area).
- Coverpoints:
  - cp_csr = pair address: bins cfg0{0x3A0}, cfg1{0x3A1}, cfg2{0x3A2}, cfg3{0x3A3}, addr0{0x3B0}, addr1{0x3B1}, addr2{0x3B2}, addr3{0x3B3}, addr4{0x3B4}, addr5{0x3B5}, addr6{0x3B6}, addr7{0x3B7}, addr8{0x3B8}, addr9{0x3B9}, addr10{0x3BA}, addr11{0x3BB}, addr12{0x3BC}, addr13{0x3BD}, addr14{0x3BE}, addr15{0x3BF}, mseccfg{0x747}, mseccfgh{0x757}
  - cp_fam = family of cp_csr: bins cfg{pmpcfg0..3}, addr{pmpaddr0..15}, mseccfg{0x747}, mseccfgh{0x757}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_wpat = write pattern class: bins rand{uniform}, all1{0xFFFF_FFFF}, all0{0}, legal_only{writable bits only}, illegal_only{RO or legalised bits only}
  - cp_entry_idx = pmpcfg entry within the register iff (cp_fam == cfg): bins e0{bits 7:0}, e1{15:8}, e2{23:16}, e3{31:24}
  - cp_entry_class = WARL class of the written entry iff (cp_fam == cfg): bins locked_kept{L=1 and RLB=0 before write}, mml_suppress{MML=1 RLB=0 and new entry is locked M-executable}, w_no_r{W=1 R=0 with MML=0}, resv_bits{bits 6:5 written 1}, mode_off{A=00}, mode_tor{A=01}, mode_na4{A=10}, mode_napot{A=11}, plain{no rule engaged}
  - cp_addr_class = pmpaddr write class iff (cp_fam == addr): bins writable{no lock}, locked_self{cfg[i].L=1 RLB=0}, locked_tor_next{cfg[i+1] locked TOR}, rlb_unlock{RLB=1 with L=1}
  - cp_mseccfg_w = mseccfg write class iff (cp_fam == mseccfg): bins mml_set{MML 0->1}, mml_clr_attempt{MML 1 written 0}, mmwp_set{MMWP 0->1}, mmwp_clr_attempt{MMWP 1 written 0}, rlb_set_nolock{RLB 1 no locked region}, rlb_set_locked{RLB 1 with locked region}, rlb_clr_with_rlb1{RLB 1->0}, hi_bits{bits 31:3 written 1}
- Crosses:
  - cr_fam_op = cp_fam x cp_op: bins cfg_csrrw{cfg csrrw}, cfg_csrrs{cfg csrrs}, cfg_csrrc{cfg csrrc}, cfg_csrrwi{cfg csrrwi}, cfg_csrrsi{cfg csrrsi}, cfg_csrrci{cfg csrrci}, addr_csrrw{addr csrrw}, addr_csrrs{addr csrrs}, addr_csrrc{addr csrrc}, addr_csrrwi{addr csrrwi}, addr_csrrsi{addr csrrsi}, addr_csrrci{addr csrrci}, mseccfg_csrrw{mseccfg csrrw}, mseccfg_csrrs{mseccfg csrrs}, mseccfg_csrrc{mseccfg csrrc}, mseccfg_csrrwi{mseccfg csrrwi}, mseccfg_csrrsi{mseccfg csrrsi}, mseccfg_csrrci{mseccfg csrrci}, mseccfgh_csrrw{mseccfgh csrrw}, mseccfgh_csrrs{mseccfgh csrrs}, mseccfgh_csrrc{mseccfgh csrrc}, mseccfgh_csrrwi{mseccfgh csrrwi}, mseccfgh_csrrsi{mseccfgh csrrsi}, mseccfgh_csrrci{mseccfgh csrrci}
  - cr_fam_wpat = cp_fam x cp_wpat: bins cfg_rand{cfg rand}, cfg_all1{cfg all1}, cfg_all0{cfg all0}, cfg_legal{cfg legal_only}, cfg_illegal{cfg illegal_only}, addr_rand{addr rand}, addr_all1{addr all1}, addr_all0{addr all0}, mseccfg_rand{mseccfg rand}, mseccfg_all1{mseccfg all1}, mseccfg_all0{mseccfg all0}, mseccfg_legal{mseccfg legal_only}, mseccfg_illegal{mseccfg illegal_only}, mseccfgh_rand{mseccfgh rand}, mseccfgh_all1{mseccfgh all1}; ignore addr x {legal_only, illegal_only}: all 32 bits writable; ignore mseccfgh x {legal_only, illegal_only}: no writable bit
  - cr_cfg_entry = cp_entry_idx x cp_entry_class: bins e0_locked{e0 locked_kept}, e1_locked{e1 locked_kept}, e2_locked{e2 locked_kept}, e3_locked{e3 locked_kept}, e0_plain{e0 plain}, e1_plain{e1 plain}, e2_plain{e2 plain}, e3_plain{e3 plain}, e0_w_no_r{e0 w_no_r}, e3_w_no_r{e3 w_no_r}, e1_mml_suppress{e1 mml_suppress}, e2_resv{e2 resv_bits}
  - cr_addr_last = cp_csr(addr15) x cp_addr_class: bins addr15_writable{addr15 writable}, addr15_locked_self{addr15 locked_self}; ignore addr15_locked_tor_next: no region 16 exists (PMPNumRegions)
  - cr_addr_lock = cp_addr_class x cp_op: bins locked_self_csrrw{locked_self csrrw}, locked_tor_next_csrrw{locked_tor_next csrrw}, rlb_unlock_csrrw{rlb_unlock csrrw}, writable_csrrw{writable csrrw}, writable_csrrs{writable csrrs}, writable_csrrc{writable csrrc}
- Adopted (riscv-dv): none
- TP items: TP-CSR-095, TP-CSR-096, TP-CSR-097, TP-CSR-099, TP-CSR-101, TP-CSR-109

### CG-CSR-012: gen_cg_csr_write_effect
- Features: F-CSR-006, F-CSR-007, F-CSR-026, F-CSR-031, F-CSR-033, F-CSR-100
- Sample: every CSR write op (WRITE/SET/CLEAR not demoted) retired without trap; the TB records the next RVFI retirement's class and the cycle gap between the two retirements; condition: rvfi_valid && is_csr_write && !rvfi_trap; anti-vacuity: demoted reads and trapped writes never sample; a hit proves a real write of that family was followed by the recorded next instruction with the recorded bubble, which gen_chk_csr_flush checks against the mscratch/mepc no-flush rule.
- Coverpoints:
  - cp_fam = written CSR family: bins mscratch{0x340}, mepc{0x341}, other_flush{any other writable or write-ignored CSR}
  - cp_next = class of the next retired instruction: bins csr_rd_same{csr read same address}, csr_rd_other{csr read other address}, csr_wr{csr write}, alu{integer op}, load_store{load or store}, branch_jump{branch or jump}, wfi{wfi}, mret{mret}, ecall_ebreak{ecall or ebreak}, irq_taken{interrupt handler entry rvfi_intr}, compressed{16-bit instruction}, dbg_entry{debug entry}
  - cp_gap = cycles between the two retirements: bins g1{1 no bubble}, g2_3{2..3 flush bubble}, g_more{>3}
  - cp_enable = write enables an already pending interrupt (mstatus.MIE or mie bit) : bins none{no}, enables_pending{yes}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
- Crosses:
  - cr_fam_next = cp_fam x cp_next: bins mscratch_csr_rd_same{mscratch csr_rd_same}, mepc_csr_rd_same{mepc csr_rd_same}, other_csr_rd_same{other_flush csr_rd_same}, other_csr_rd_other{other_flush csr_rd_other}, other_csr_wr{other_flush csr_wr}, other_alu{other_flush alu}, other_load_store{other_flush load_store}, other_branch_jump{other_flush branch_jump}, other_irq_taken{other_flush irq_taken}, other_wfi{other_flush wfi}, other_mret{other_flush mret}, other_compressed{other_flush compressed}, other_ecall{other_flush ecall_ebreak}, other_dbg_entry{other_flush dbg_entry}, mscratch_alu{mscratch alu}, mscratch_load_store{mscratch load_store}, mepc_mret{mepc mret}, mepc_alu{mepc alu}
  - cr_fam_gap = cp_fam x cp_gap: bins mscratch_g1{mscratch g1}, mepc_g1{mepc g1}, other_g2_3{other_flush g2_3}, other_g_more{other_flush g_more}, mscratch_g_more{mscratch g_more stalled by memory}; ignore other_g1: a flushing write always costs at least one FLUSH cycle
  - cr_enable_next = cp_enable x cp_next: bins enables_irq_taken{enables_pending irq_taken}, none_alu{none alu}, none_irq_taken{none irq_taken}
  - cr_fam_op = cp_fam x cp_op: bins mscratch_csrrw{mscratch csrrw}, mscratch_csrrs{mscratch csrrs}, mscratch_csrrc{mscratch csrrc}, mepc_csrrw{mepc csrrw}, mepc_csrrsi{mepc csrrsi}, other_csrrw{other_flush csrrw}, other_csrrs{other_flush csrrs}, other_csrrc{other_flush csrrc}, other_csrrwi{other_flush csrrwi}, other_csrrsi{other_flush csrrsi}, other_csrrci{other_flush csrrci}
- Adopted (riscv-dv): none
- TP items: TP-CSR-003, TP-CSR-006, TP-CSR-007, TP-CSR-026, TP-CSR-031, TP-CSR-033, TP-CSR-101, TP-CSR-102, TP-CSR-103, TP-CSR-115, TP-CSR-116, TP-CSR-119

### CG-CSR-013: gen_cg_csr_counter_race
- Features: F-CSR-034, F-CSR-060, F-CSR-063, F-CSR-064, F-CSR-065, F-CSR-067, F-CSR-068, F-CSR-070,
  F-CSR-072, F-CSR-073, F-PMC-007 (parent of folded bins hosted here)
- Sample: rvfi_valid with a CSR instruction to mcycle(h), minstret(h), mhpmcounter3..2+MHPMCounterNum(h) or mip; condition: rvfi_valid && is_csr_insn && addr in that set && !rvfi_trap; anti-vacuity: the race coverpoints are derived from rvfi_ext_mcycle / rvfi_ext_mhpmcounters of the writer and of the neighbouring retirements and from the irq pins, so a hit proves the hardware update and the software access were adjacent in the way the bin names, and gen_chk_counters compared the result.
- Coverpoints:
  - cp_csr = addr class: bins mcycle{0xB00}, mcycleh{0xB80}, minstret{0xB02}, minstreth{0xB82}, hpm_lo{0xB03..0xB02+MHPMCounterNum}, hpm10{0xB0A}, hpm_hi{0xB83..0xB82+MHPMCounterNum}, mip{0x344}
  - cp_kind = op after demotion: bins rd{READ}, wr{WRITE}, set{SET}, clr{CLEAR}
  - cp_inhibit = the counter's mcountinhibit bit: bins on{1}, off{0}
  - cp_coincide = a countable event for the addressed counter in the write cycle iff (cp_csr inside {minstret, minstreth, hpm_lo, hpm10, hpm_hi} && cp_kind != rd) (minstret(h): a countable instruction completing in WB in the writer's commit cycle; hpm: the counted event in that cycle; both inferred from RVFI ordering, the preceding record being a load/store retiring one cycle before the writer with knob:dmem_rvalid_delay = min1, see Probe candidates): bins none{0}, coincide{1}; mcycle/mcycleh are excluded by the iff: mcycle increments every cycle, so the coincidence would be unconditional (S-3a tautology); the mcycle write-wins rule is cr_cyc_wr.mcycle_wr_off (TP-CSR-063)
  - cp_near_wrap = low half within 16 of 0xFFFF_FFFF at the access: bins no{0}, yes{1}
  - cp_carry_win = mcycleh written in the cycle the low half carries iff (cp_csr == mcycleh && cp_kind != rd) (inferred from rvfi_ext_mcycle of the writer: low half == 0xFFFF_FFFF, see Probe candidates): bins no{0}, yes{1}
  - cp_wb_state = instruction in WB in the read cycle iff (cp_kind == rd && cp_csr inside {minstret, hpm_lo, hpm10}) (inferred from RVFI: the preceding record is a load/store retiring in the reader's ID cycle, or trapping there for retiring_err; see Probe candidates): bins idle{none}, retiring{countable retirement}, retiring_err{LSU error retirement}
  - cp_mip_toggle = irq pin change relative to the mip read cycle iff (cp_csr == mip): bins stable{no change within +-2 cycles}, toggle_before{change 1..2 cycles before}, toggle_at{change in the read cycle}
  - cp_prepost = rvfi_ext_pre_mip vs rvfi_ext_post_mip iff (cp_csr == mip): bins equal{same}, differ{different}
- Crosses:
  - cr_cyc_wr = cp_csr x cp_kind x cp_inhibit: bins mcycle_wr_off{mcycle wr off}, mcycle_set_off{mcycle set off}, mcycle_clr_off{mcycle clr off}, mcycle_wr_on{mcycle wr on}, mcycleh_wr_off{mcycleh wr off}, mcycleh_set_off{mcycleh set off}, mcycleh_clr_off{mcycleh clr off}, mcycleh_wr_on{mcycleh wr on}, mcycle_rd_on{mcycle rd on}, mcycle_rd_off{mcycle rd off}
  - cr_carry: RETIRED (S-7 identity cross of cp_carry_win, which is mcycleh-only by its iff; TP-CSR-064 references cp_carry_win.yes / cp_carry_win.no)
  - cr_near_wrap = cp_csr x cp_near_wrap(yes) x cp_kind: bins mcycle_wrap_rd{mcycle yes rd}, mcycleh_wrap_wr{mcycleh yes wr}, minstret_wrap_rd{minstret yes rd}, hpm_wrap_rd{hpm_lo yes rd}, hpm_hi_wrap_wr{hpm_hi yes wr}
  - cr_minstret_rd_wb = cp_csr x cp_wb_state x cp_inhibit (rd): bins minstret_idle{minstret idle off}, minstret_retiring{minstret retiring off}, minstret_retiring_err{minstret retiring_err off}, minstret_inh_retiring{minstret retiring on}, hpm10_idle{hpm10 idle off}, hpm10_retiring{hpm10 retiring off}, hpm_lo_retiring{hpm_lo retiring off}
  - cr_minstret_wr = cp_csr x cp_kind x cp_coincide: bins minstret_wr_coincide{minstret wr coincide}, minstret_set_coincide{minstret set coincide}, minstret_clr_coincide{minstret clr coincide}, minstreth_wr_coincide{minstreth wr coincide}, minstret_wr_none{minstret wr none}, hpm_lo_wr_coincide{hpm_lo wr coincide}, hpm_hi_wr_coincide{hpm_hi wr coincide}, hpm_lo_set_coincide{hpm_lo set coincide}
  - cr_mip_rd = cp_csr(mip) x cp_mip_toggle x cp_prepost: bins stable_equal{stable equal}, before_equal{toggle_before equal}, before_differ{toggle_before differ}, at_differ{toggle_at differ}, at_equal{toggle_at equal}
- Adopted (riscv-dv): none
- TP items: TP-CSR-032, TP-CSR-034, TP-CSR-059, TP-CSR-060, TP-CSR-062, TP-CSR-063, TP-CSR-064, TP-CSR-065, TP-CSR-066, TP-CSR-067, TP-CSR-068, TP-CSR-070, TP-CSR-072, TP-CSR-073, TP-CSR-113, TP-CSR-114, TP-CSR-119, TP-CSR-120

### CG-CSR-014: gen_cg_csr_unimpl_addr
- Features: F-CSR-009, F-CSR-010, F-CSR-016, F-CSR-018, F-CSR-055, F-CSR-097
- Sample: rvfi_valid with a CSR instruction whose address is outside the implemented set (CSR-02 list); condition: rvfi_valid && is_csr_insn && !implemented(addr); anti-vacuity: implemented addresses never sample; a hit proves an access to that hole class happened in that mode/form and gen_isa_compare checked the illegal-instruction trap with mtval = encoding.
- Coverpoints:
  - cp_range = hole range: bins r000_0ff{0x000..0x0FF}, r100_1ff{0x100..0x1FF}, r200_2ff{0x200..0x2FF}, r302_303{medeleg mideleg}, r307_309{0x307..0x309}, r30b_30f{0x30B..0x30F}, r311_319{0x311..0x319}, r31b_31f{0x31B..0x31F}, r321_322{0x321 0x322}, r345_39f{0x345..0x39F}, r3a4_3af{0x3A4..0x3AF}, r3c0_5a7{0x3C0..0x5A7}, r5a9_746{0x5A9..0x746}, r748_756{0x748..0x756}, r758_79f{0x758..0x79F}, r7a4_7a7{0x7A4..0x7A7}, r7a9{0x7A9}, r7ab_7af{0x7AB..0x7AF}, r7b4_7bf{0x7B4..0x7BF}, r7c2_7ff{0x7C2..0x7FF}, r800_aff{0x800..0xAFF}, rb01{0xB01}, rb20_b7f{0xB20..0xB7F}, rb81{0xB81}, rba0_bbf{0xBA0..0xBBF}, rbc0{0xBC0}, rbc3{0xBC3}, rbc5_bff{0xBC5..0xBFF}, rc01{time}, rc81{timeh}, rc20_c7f{0xC20..0xC7F}, rca0_f10{0xCA0..0xF10}, rf16_fff{0xF16..0xFFF}, cheriot{0xBC1 0xBC2 0xBC4}
  - cp_class = coarse class: bins lo{0x000..0x2FF}, mhole{holes in 0x3xx 0x7xx 0xBxx}, mid_unpriv{0x400..0x4FF 0x800..0x8FF}, s_h_hole{0x5xx 0x6xx 0x9xx 0xAxx 0xDxx 0xExx holes}, ro_hole{unimplemented [11:10]=11 incl time}, dbg_hole{0x7B4..0x7BF}, cheriot{0xBC1 0xBC2 0xBC4}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_form = op form after demotion: bins rd{demoted read}, wr{write op}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_trap = rvfi_trap: bins trap{1}; ignore_bins ok{0}: unimplemented addresses always trap; a hit is a gen_isa_compare failure, not a coverage target
- Crosses:
  - cr_class_priv_form = cp_class x cp_priv x cp_form: bins lo_m_rd{lo m rd}, lo_m_wr{lo m wr}, lo_u_rd{lo u rd}, lo_u_wr{lo u wr}, mhole_m_rd{mhole m rd}, mhole_m_wr{mhole m wr}, mhole_u_rd{mhole u rd}, mhole_u_wr{mhole u wr}, mid_m_rd{mid_unpriv m rd}, mid_m_wr{mid_unpriv m wr}, mid_u_rd{mid_unpriv u rd}, mid_u_wr{mid_unpriv u wr}, sh_m_rd{s_h_hole m rd}, sh_m_wr{s_h_hole m wr}, sh_u_rd{s_h_hole u rd}, sh_u_wr{s_h_hole u wr}, ro_m_rd{ro_hole m rd}, ro_m_wr{ro_hole m wr}, ro_u_rd{ro_hole u rd}, ro_u_wr{ro_hole u wr}, dbg_m_rd{dbg_hole m rd}, dbg_m_wr{dbg_hole m wr}, dbg_u_rd{dbg_hole u rd}, dbg_u_wr{dbg_hole u wr}, cher_m_rd{cheriot m rd}, cher_m_wr{cheriot m wr}, cher_u_rd{cheriot u rd}, cher_u_wr{cheriot u wr}
  - cr_dbg_hole = cp_range(r7b4_7bf) x cp_dbg x cp_trap: bins dbghole_dbg_trap{r7b4_7bf dbg trap}, dbghole_nondbg_trap{r7b4_7bf nondbg trap}; ignore x ok: unimplemented in every mode
  - cr_time = cp_range x cp_priv (time timeh): bins time_m{rc01 m}, time_u{rc01 u}, timeh_m{rc81 m}, timeh_u{rc81 u}
- Adopted (riscv-dv): none
- TP items: TP-CSR-009, TP-CSR-010, TP-CSR-014, TP-CSR-016, TP-CSR-018, TP-CSR-055, TP-CSR-098, TP-CSR-112, TP-CSR-116

### CG-CSR-015: gen_cg_csr_write_cancel
- Features: F-CSR-008, F-CSR-101, F-CSR-102, F-CSR-103, F-CSR-009 (parent of folded bins hosted
  here)
- Sample: a CSR write instruction that was in ID when a kill condition occurred, detected from RVFI: (a) the retirement immediately preceding it in program order trapped with an LSU error/PMP fault and the CSR instruction retires only after the handler's mret (re-execution), (b) the CSR instruction itself retires with rvfi_trap (fetch error, PMP fetch fault, illegal CSR), (c) debug entry with dpc == the CSR instruction PC; condition: any of a..c; anti-vacuity: an ordinary CSR write never matches; a hit proves the write was in flight when the kill happened, and gen_chk_csr_readback confirms the CSR kept its old value at the next read.
- Coverpoints:
  - cp_cause = kill cause: bins wb_lsu_err{load/store bus error in WB}, wb_lsu_pmp{load/store PMP fault in WB}, fetch_err{instr_err on the CSR instruction}, fetch_pmp{PMP fetch fault on the CSR instruction}, illegal_csr{illegal CSR access}, dbg_req_before{debug entry with dpc == csr pc}
  - cp_fam = CSR family of the killed write: bins mscratch_mepc{no-flush CSRs}, flush_csr{any other}
  - cp_op = write op: bins csrrw{001}, csrrs{010}, csrrc{011}, csrrwi{101}, csrrsi{110}, csrrci{111}
  - cp_reexec = the CSR instruction later retires successfully: bins yes{1}, no{0}
- Crosses:
  - cr_cause_fam = cp_cause x cp_fam: bins lsu_err_mscratch{wb_lsu_err mscratch_mepc}, lsu_err_flush{wb_lsu_err flush_csr}, lsu_pmp_flush{wb_lsu_pmp flush_csr}, lsu_pmp_mscratch{wb_lsu_pmp mscratch_mepc}, fetch_err_flush{fetch_err flush_csr}, fetch_pmp_flush{fetch_pmp flush_csr}, illegal_flush{illegal_csr flush_csr}, dbg_before_flush{dbg_req_before flush_csr}, dbg_before_mscratch{dbg_req_before mscratch_mepc}
  - cr_cause_reexec = cp_cause x cp_reexec: bins lsu_err_yes{wb_lsu_err yes}, lsu_err_no{wb_lsu_err no}, lsu_pmp_yes{wb_lsu_pmp yes}, fetch_err_yes{fetch_err yes}, fetch_pmp_yes{fetch_pmp yes}, illegal_no{illegal_csr no}, illegal_yes{illegal_csr yes after priv change}, dbg_before_yes{dbg_req_before yes}
  - cr_cause_op = cp_cause x cp_op: bins lsu_err_csrrw{wb_lsu_err csrrw}, lsu_err_csrrs{wb_lsu_err csrrs}, lsu_err_csrrc{wb_lsu_err csrrc}, lsu_err_csrrwi{wb_lsu_err csrrwi}, illegal_csrrw{illegal_csr csrrw}, illegal_csrrs{illegal_csr csrrs}, illegal_csrrci{illegal_csr csrrci}
- Adopted (riscv-dv): none
- TP items: TP-CSR-008, TP-CSR-102, TP-CSR-103, TP-CSR-104

### CG-CSR-016: gen_cg_csr_reset_read
- Features: F-CSR-019, F-CSR-020, F-CSR-021, F-CSR-023, F-CSR-029, F-CSR-032, F-CSR-035, F-CSR-037, F-CSR-038, F-CSR-039, F-CSR-042, F-CSR-047, F-CSR-050, F-CSR-058, F-CSR-061, F-CSR-062, F-CSR-066, F-CSR-069, F-CSR-074, F-CSR-078, F-CSR-079, F-CSR-080, F-CSR-081, F-CSR-082, F-CSR-085, F-CSR-092, F-CSR-094, F-CSR-096, F-CSR-098
- Sample: the first CSR read of an address after reset, before any software write to that address (TB tracks per-address first-write); condition: rvfi_valid && is_csr_insn && !rvfi_trap && first_read_before_write(addr); anti-vacuity: at most one sample per address per reset; a hit proves the reset value of that CSR was read back and compared by gen_chk_csr_readback against the ibex_pkg / parameter reset value.
- Coverpoints:
  - cp_csr = address class: bins mstatus{0x300}, misa{0x301}, mie{0x304}, mtvec{0x305}, mcounteren{0x306}, mstatush{0x310}, menvcfg{0x30A}, menvcfgh{0x31A}, mcountinhibit{0x320}, mhpmevent{0x323..0x322+MHPMCounterNum}, mhpmevent_unimpl{0x323+MHPMCounterNum..0x33F}, mscratch{0x340}, mepc{0x341}, mcause{0x342}, mtval{0x343}, mip{0x344}, pmpcfg{0x3A0..0x3A3}, pmpaddr{0x3B0..0x3BF}, scontext{0x5A8}, mseccfg{0x747}, mseccfgh{0x757}, tselect{0x7A0}, tdata1{0x7A1}, tdata2{0x7A2}, tdata3{0x7A3}, mcontext{0x7A8}, mscontext{0x7AA}, dcsr{0x7B0}, dpc{0x7B1}, dscratch0{0x7B2}, dscratch1{0x7B3}, cpuctrlsts{0x7C0}, secureseed{0x7C1}, mcycle{0xB00}, mcycleh{0xB80}, minstret{0xB02}, minstreth{0xB82}, hpm{0xB03..0xB02+MHPMCounterNum}, hpmh{0xB83..0xB82+MHPMCounterNum}, hpm_unimpl{0xB03+MHPMCounterNum..0xB1F 0xB83+MHPMCounterNum..0xB9F}, cycle_alias{0xC00 0xC80}, instret_alias{0xC02 0xC82}, hpm_alias{0xC03..0xC02+MHPMCounterNum 0xC83..0xC82+MHPMCounterNum}, mvendorid{0xF11}, marchid{0xF12}, mimpid{0xF13}, mhartid{0xF14}, mconfigptr{0xF15}
  - cp_when = position of the read after reset: bins first_insn{first retired instruction}, early{retirement index 2..16}, later{>16}
  - cp_boot_lo = boot_addr_i[7:0] iff (cp_csr == mtvec): bins zero{0}, nonzero{!=0}
  - cp_hart = hart_id_i class iff (cp_csr == mhartid): bins zero{0}, all1{0xFFFF_FFFF}, rand{other}
  - cp_dbg = rvfi_ext_debug_mode at the read: bins nondbg{0}, dbg{1}
- Crosses:
  - cr_mtvec_first = cp_csr(mtvec) x cp_when x cp_boot_lo: bins mtvec_first_zero{mtvec first_insn zero}, mtvec_first_nonzero{mtvec first_insn nonzero}, mtvec_early_zero{mtvec early zero}, mtvec_early_nonzero{mtvec early nonzero}
  - cr_first_csr = cp_csr x cp_when(first_insn): bins mstatus_first{mstatus}, mie_first{mie}, mcycle_first{mcycle}, minstret_first{minstret}, mhartid_first{mhartid}, misa_first{misa}, cpuctrlsts_first{cpuctrlsts}
  - cr_dbg_reset = cp_csr x cp_dbg(dbg): bins dcsr_dbg{dcsr}, dpc_dbg{dpc}, dscratch0_dbg{dscratch0}, dscratch1_dbg{dscratch1}; ignore tdata1_dbg: tdata1 is M-readable and every item that reads it (TP-CSR-081/084/108) reads it in M-mode first, so a first read inside debug mode never happens (S-3d); ignore every other cp_csr x dbg: the debug ROM reads only the debug CSRs before their first write
  - cr_hart_rd = cp_csr(mhartid) x cp_hart: bins hart_zero{zero}, hart_all1{all1}, hart_rand{rand}
- Adopted (riscv-dv): none
- TP items: TP-CSR-019, TP-CSR-020, TP-CSR-021, TP-CSR-027, TP-CSR-028, TP-CSR-032, TP-CSR-037, TP-CSR-038, TP-CSR-039, TP-CSR-042, TP-CSR-047, TP-CSR-050, TP-CSR-053, TP-CSR-058, TP-CSR-061, TP-CSR-062, TP-CSR-066, TP-CSR-069, TP-CSR-071, TP-CSR-080, TP-CSR-081, TP-CSR-082, TP-CSR-083, TP-CSR-085, TP-CSR-092, TP-CSR-095, TP-CSR-097, TP-CSR-099, TP-CSR-105, TP-CSR-106, TP-CSR-107, TP-CSR-108, TP-CSR-109

### CG-CSR-017: gen_cg_csr_storm
- Features: F-CSR-001, F-CSR-006, F-CSR-009, F-CSR-014, F-CSR-099, F-CSR-100
- Sample: once per window of 256 RVFI retirements in tests running knob:instr_mix = csr_heavy; condition: window complete; anti-vacuity: windows only close after 256 retirements, so a hit proves a full window of the recorded CSR density, privilege mix and trap density ran with alert_major_internal_o observed; density bins are stimulus coverage; the alert_major_internal_o == 0 witness is left to gen_chk_alerts (S-3b), not a closure bin, so F-CSR-099 is proven by TP-CSR-100's checker over the recorded windows.
- Coverpoints:
  - cp_density = CSR instructions in the window: bins low{<16}, mid{16..63}, high{>=64}
  - cp_trap_density = illegal-CSR traps in the window: bins none{0}, some{1..7}, many{>=8}
  - cp_priv_mix = privilege of CSR instructions in the window: bins m_only{all M}, u_only{all U}, mixed{both}
  - cp_distinct = distinct CSR addresses touched in the window: bins few{<4}, some{4..15}, many{>=16}
  - cp_alert_int: RETIRED (S-3b always-true witness; alert_major_internal_o == 0 is gen_chk_alerts' check)
  - cp_dbg_mix = window contains debug-mode CSR accesses: bins no{0}, yes{1}
  - cp_irq_mix = window contains at least one interrupt entry: bins no{0}, yes{1}
- Crosses:
  - cr_density_priv = cp_density x cp_priv_mix: bins high_mixed{high mixed}, high_m_only{high m_only}, mid_mixed{mid mixed}, mid_m_only{mid m_only}, low_u_only{low u_only}, mid_u_only{mid u_only}
  - cr_trap_density = cp_density x cp_trap_density: bins high_many{high many}, high_none{high none}, mid_some{mid some}, high_some{high some}
  - cr_distinct_density = cp_distinct x cp_density: bins many_high{many high}, some_mid{some mid}, few_high{few high}
  - cr_alert_density: RETIRED (S-3b; cp_alert_int retired)
  - cr_mix = cp_dbg_mix x cp_irq_mix x cp_density: bins dbg_irq_high{yes yes high}, dbg_noirq_high{yes no high}, nodbg_irq_high{no yes high}, nodbg_irq_mid{no yes mid}
- Adopted (riscv-dv): none
- TP items: TP-CSR-100, TP-CSR-112, TP-CSR-116, TP-CSR-117, TP-CSR-118, TP-CSR-119, TP-CSR-120

## Covergroups: PRV

### CG-PRV-001: gen_cg_prv_transition
- Features: F-PRV-001, F-PRV-002, F-PRV-006, F-PRV-009, F-PRV-010, F-PRV-021, F-PRV-022, F-PRV-023, F-PRV-025, F-PRV-026, F-PRV-027, F-PRV-033
- Sample: every RVFI retirement that is a privilege-transition EVENT: (a) a trapped retirement (rvfi_trap = 1, incl. an exception inside debug mode), (b) the first handler retirement of an interrupt or NMI (rvfi_intr), (c) an mret or dret retirement, (d) a debug entry (first retirement with rvfi_ext_debug_mode rising; the ebreak-into-debug path is is_ebreak(rvfi_insn) && !rvfi_trap && next fetch == DmHaltAddr, S-2), (e) the first retirement after reset; condition: is_prv_event(n); anti-vacuity: ordinary retirements never sample; cp_from is the mode of the event retirement (for (b) and (d) the retirement before the entry), cp_to the mode of the next retirement, and cp_mode_change discriminates same-mode events from mode-changing ones, so a hit on an m_m_* bin proves an M-mode trap was taken into M (not a tautology of the sample condition); gen_isa_compare (mode per retirement) and gen_chk_debug (entries, dret) check the transition itself.
- Coverpoints:
  - cp_from = mode before: bins m{M non-debug}, u{U}, dbg{debug mode}, reset{first retirement}
  - cp_to = mode after: bins m{M non-debug}, u{U}, dbg{debug mode}
  - cp_mode_change = (rvfi_mode, rvfi_ext_debug_mode) differ between cp_from and cp_to: bins changed{1}, same{0: M->M trap or mret, debug->debug exception}
  - cp_via = event causing the change: bins mret{mret}, ecall{ecall}, ebreak{ebreak or c.ebreak exception}, illegal{illegal instruction incl illegal CSR / mret-in-U / wfi-TW / dret}, fetch_fault{instruction access fault}, ls_fault{load/store fault}, irq{interrupt}, nmi{NMI}, dbg_req{debug_req_i}, dbg_step{single step}, dbg_trigger{trigger match}, dbg_ebreak{ebreak into debug: rvfi_trap = 0, next fetch == DmHaltAddr (S-2)}, dret{dret}, reset{reset release}, dbg_exc{exception inside debug mode}
  - cp_seq3 = last three modes at a change (M/U/D): bins m_u_m{M U M}, u_m_u{U M U}, m_d_m{M D M}, m_d_u{M D U}, u_d_u{U D U}, u_d_m{U D M}, d_u_m{D U M}, d_m_u{D M U}, m_m_u{M M U}, u_m_m{U M M}; ignore m_u_u: U cannot change to U (every trap enters M)
  - cp_u_exit = cause of leaving U-mode: bins ecall{ecall}, ebreak{ebreak}, illegal_insn{illegal opcode}, illegal_csr{illegal CSR access}, fetch_fault{fetch fault}, ls_fault{load/store fault}, irq{interrupt}, nmi{NMI}, dbg_req{debug_req_i}, step{single step}, trigger{trigger}, wfi_tw{wfi with TW=1}, mret_in_u{mret in U}, dret_in_u{dret in U}
- Crosses:
  - cr_trans = cp_from x cp_to x cp_via (legal transitions only, enumerated): bins m_m_mret{m m mret}, m_u_mret{m u mret}, u_m_ecall{u m ecall}, u_m_ebreak{u m ebreak}, u_m_illegal{u m illegal}, u_m_fetch_fault{u m fetch_fault}, u_m_ls_fault{u m ls_fault}, u_m_irq{u m irq}, u_m_nmi{u m nmi}, m_m_ecall{m m ecall}, m_m_ebreak{m m ebreak}, m_m_illegal{m m illegal}, m_m_fetch_fault{m m fetch_fault}, m_m_ls_fault{m m ls_fault}, m_m_irq{m m irq}, m_m_nmi{m m nmi}, m_dbg_req{m dbg dbg_req}, u_dbg_req{u dbg dbg_req}, m_dbg_step{m dbg dbg_step}, u_dbg_step{u dbg dbg_step}, m_dbg_trigger{m dbg dbg_trigger}, u_dbg_trigger{u dbg dbg_trigger}, m_dbg_ebreak{m dbg dbg_ebreak}, u_dbg_ebreak{u dbg dbg_ebreak}, dbg_m_dret{dbg m dret}, dbg_u_dret{dbg u dret}, dbg_dbg_exc{dbg dbg dbg_exc}, reset_m{reset m reset}; ignore u_u_any: no U to U transition exists; ignore dbg_x_mret: mret in debug mode does not leave debug mode; ignore m_u_any except mret and dret: only mret (and dret from debug) lower the privilege
  - cr_u_exit_seq = cp_u_exit x cp_seq3: bins ecall_m_u_m{ecall m_u_m}, irq_m_u_m{irq m_u_m}, nmi_m_u_m{nmi m_u_m}, illegal_csr_m_u_m{illegal_csr m_u_m}, wfi_tw_m_u_m{wfi_tw m_u_m}, mret_in_u_m_u_m{mret_in_u m_u_m}, dret_in_u_m_u_m{dret_in_u m_u_m}, dbg_req_u_d_u{dbg_req u_d_u}, step_u_d_u{step u_d_u}, trigger_u_d_m{trigger u_d_m}, ls_fault_m_u_m{ls_fault m_u_m}, fetch_fault_m_u_m{fetch_fault m_u_m}, ebreak_m_u_m{ebreak m_u_m}
- Adopted (riscv-dv): none
- TP items: TP-CSR-014, TP-CSR-024, TP-PRV-001, TP-PRV-002, TP-PRV-004, TP-PRV-005, TP-PRV-008, TP-PRV-009, TP-PRV-010, TP-PRV-014, TP-PRV-015, TP-PRV-017, TP-PRV-020, TP-PRV-021, TP-PRV-022, TP-PRV-024, TP-PRV-025, TP-PRV-026, TP-PRV-030, TP-PRV-032, TP-PRV-036, TP-PRV-037, TP-PRV-038

### CG-PRV-002: gen_cg_prv_mstatus_stack
- Features: F-PRV-002, F-PRV-003, F-PRV-004, F-PRV-006, F-PRV-007, F-PRV-008, F-PRV-011, F-PRV-012, F-PRV-024, F-PRV-031
- Sample: (a) trap entry = first handler retirement (rvfi_intr) or the retirement following a trapped instruction, (b) mret retirement; condition: either event; anti-vacuity: only trap entries and mrets sample; the pre-event MIE/priv/MPP/MPIE/MPRV values come from the TB's mstatus model (validated by read-backs), so a hit proves the stack push/pop of that shape happened and gen_isa_compare / gen_chk_csr_readback compared the resulting mstatus.
- Coverpoints:
  - cp_event = event: bins trap_entry{trap entry}, mret{mret}
  - cp_prev_priv = mode of the trapped/interrupted instruction iff (cp_event == trap_entry): bins m{3}, u{0}
  - cp_prev_mie = mstatus.MIE before the trap iff (cp_event == trap_entry): bins b0{0}, b1{1}
  - cp_cause = trap class iff (cp_event == trap_entry): bins sync_exc{exception}, irq{interrupt}, nmi{NMI external or internal}
  - cp_mpp_at_mret = mstatus.MPP before mret iff (cp_event == mret): bins u{00}, m{11}
  - cp_mpie_at_mret = mstatus.MPIE before mret iff (cp_event == mret): bins b0{0}, b1{1}
  - cp_mprv_at_mret = mstatus.MPRV before mret iff (cp_event == mret): bins b0{0}, b1{1}
  - cp_nmi_mode = mret executed inside an NMI handler iff (cp_event == mret): bins no{0}, yes{1}
  - cp_sw_mepc_in_nmi = software wrote mepc or mcause inside the NMI handler before mret iff (cp_event == mret): bins no{0}, yes{1}
  - cp_irq_at_mret = enabled interrupt pending when mret retires iff (cp_event == mret): bins none{0}, pending{1}
  - cp_mepc_odd_lsb = mepc[1] at mret (2-byte aligned target) iff (cp_event == mret): bins b0{0}, b1{1}
- Crosses:
  - cr_entry = cp_prev_priv x cp_prev_mie x cp_cause: bins u_mie0_irq{u b0 irq}, u_mie1_irq{u b1 irq}, u_mie0_sync{u b0 sync_exc}, u_mie1_sync{u b1 sync_exc}, m_mie0_sync{m b0 sync_exc}, m_mie1_sync{m b1 sync_exc}, m_mie1_irq{m b1 irq}, m_mie0_nmi{m b0 nmi}, m_mie1_nmi{m b1 nmi}, u_mie0_nmi{u b0 nmi}, u_mie1_nmi{u b1 nmi}; ignore m_mie0_irq: interrupts are not taken in M with MIE=0
  - cr_mret = cp_mpp_at_mret x cp_mpie_at_mret x cp_mprv_at_mret: bins u_0_0{u b0 b0}, u_0_1{u b0 b1}, u_1_0{u b1 b0}, u_1_1{u b1 b1}, m_0_0{m b0 b0}, m_0_1{m b0 b1}, m_1_0{m b1 b0}, m_1_1{m b1 b1}
  - cr_nmi_mret = cp_nmi_mode x cp_sw_mepc_in_nmi: bins nmi_sw_no{yes no}, nmi_sw_yes{yes yes}, nonnmi_sw_no{no no}; ignore nonnmi_sw_yes: the coverpoint is defined inside NMI handlers only
  - cr_mret_irq = cp_mpp_at_mret x cp_mpie_at_mret x cp_irq_at_mret: bins m_1_pending{m b1 pending}, m_0_pending{m b0 pending}, u_0_pending{u b0 pending}, u_1_pending{u b1 pending}, m_1_none{m b1 none}, u_1_none{u b1 none}
  - cr_mret_target = cp_mpp_at_mret x cp_mepc_odd_lsb: bins u_b1{u b1}, m_b1{m b1}, u_b0{u b0}, m_b0{m b0}
- Adopted (riscv-dv): none
- TP items: TP-CSR-040, TP-CSR-094, TP-PRV-002, TP-PRV-003, TP-PRV-005, TP-PRV-006, TP-PRV-007, TP-PRV-008, TP-PRV-010, TP-PRV-011, TP-PRV-023, TP-PRV-030, TP-PRV-036, TP-PRV-037

### CG-PRV-003: gen_cg_prv_mprv
- Features: F-PRV-013, F-PRV-014, F-PRV-015
- Sample: every retired load or store (rvfi_mem_rmask or rvfi_mem_wmask nonzero, or a trapped LSU instruction); condition: rvfi_valid && is_load_store(rvfi_insn); anti-vacuity: non-memory instructions never sample; MPRV/MPP come from the TB mstatus model, the PMP outcome from rvfi_trap plus gen_chk_pmp's prediction, so a hit proves a data access ran under that effective-privilege configuration and gen_chk_pmp checked it.
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_mprv = mstatus.MPRV: bins b0{0}, b1{1}
  - cp_mpp = mstatus.MPP: bins u{00}, m{11}
  - cp_access = access type: bins load{load}, store{store}
  - cp_outcome = PMP outcome: bins allow{no fault}, fault{access fault}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_after_dret_u = first 8 U-mode retirements after a dret that left MPRV=1: bins no{0}, yes{1}
  - cp_pmp_cfg = PMP configuration class for the address (from gen_chk_pmp): bins m_only{region allows M only}, u_rw{region allows U}, no_region{no match}
- Crosses:
  - cr_eff = cp_priv x cp_mprv x cp_mpp x cp_access x cp_outcome: bins m_1_u_load_fault{m b1 u load fault}, m_1_u_store_fault{m b1 u store fault}, m_1_u_load_allow{m b1 u load allow}, m_1_u_store_allow{m b1 u store allow}, m_1_m_load_allow{m b1 m load allow}, m_1_m_store_allow{m b1 m store allow}, m_0_u_load_allow{m b0 u load allow}, m_0_m_store_allow{m b0 m store allow}, u_1_m_load_allow{u b1 m load allow B1 window}, u_1_m_store_allow{u b1 m store allow B1 window}, u_1_u_load_fault{u b1 u load fault}, u_0_u_load_fault{u b0 u load fault}, u_0_u_store_fault{u b0 u store fault}, u_0_u_load_allow{u b0 u load allow}, u_0_m_load_allow{u b0 m load allow}
  - cr_dbg_mprv = cp_dbg(dbg) x cp_mprv x cp_mpp x cp_outcome: bins dbg_1_u_fault{dbg b1 u fault B2}, dbg_1_u_allow{dbg b1 u allow}, dbg_0_u_allow{dbg b0 u allow}, dbg_0_m_allow{dbg b0 m allow}, dbg_1_m_allow{dbg b1 m allow}
  - cr_after_dret = cp_after_dret_u(yes) x cp_pmp_cfg x cp_outcome: bins dret_m_only_allow{yes m_only allow}, dret_m_only_fault{yes m_only fault}, dret_u_rw_allow{yes u_rw allow}, dret_no_region_fault{yes no_region fault}
  - cr_mprv_cfg = cp_priv(m) x cp_mprv(b1) x cp_mpp(u) x cp_pmp_cfg x cp_outcome: bins m_only_fault{m_only fault}, u_rw_allow{u_rw allow}, no_region_fault{no_region fault}
- Adopted (riscv-dv): none
- TP items: TP-PRV-006, TP-PRV-012, TP-PRV-013, TP-PRV-014, TP-PRV-035

### CG-PRV-004: gen_cg_prv_umode_illegal
- Features: F-PRV-010, F-PRV-016, F-PRV-017, F-PRV-021, F-PRV-022, F-PRV-025, F-PRV-028
- Sample: rvfi_valid with rvfi_insn opcode SYSTEM and funct3 == 000 (ecall, ebreak, mret, dret, wfi, sret, uret, sfence.vma, others) or c.ebreak, trapped or not; condition: rvfi_valid && is_priv_insn(rvfi_insn); anti-vacuity: only privileged-instruction retirements sample; a hit proves the named instruction executed in that mode/TW/debug state with the recorded outcome, which gen_isa_compare checks (cause 2/3/8/11, mtval).
- Coverpoints:
  - cp_kind = instruction: bins ecall{0x00000073}, ebreak{0x00100073}, c_ebreak{0x9002}, mret{0x30200073}, dret{0x7B200073}, wfi{0x10500073}, sret{0x10200073}, uret{0x00200073}, sfence_vma{funct7 0001001}, other_priv{other imm with rs1=rd=0}, nz_rs1_rd{ecall/ebreak/mret/dret/wfi encoding with rs1 or rd != 0}
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_tw = mstatus.TW: bins b0{0}, b1{1}
  - cp_trap = rvfi_trap: bins ok{0}, trap{1}
  - cp_mcause = mcause read in the handler: bins ill{2}, brk{3}, ecall_u{8}, ecall_m{11}; ignore_bins other: no privileged instruction produces another cause; a hit is a gen_isa_compare failure
  - cp_ebreak_dcsr = dcsr.ebreakm/ebreaku bit for the current mode: bins b0{0}, b1{1}
  - cp_mtval = mtval read in the handler: bins zero{0}, insn{== rvfi_insn}; ignore_bins other: mtval is 0 or the encoding for every privileged-instruction trap; a hit is a gen_isa_compare failure
- Crosses:
  - cr_kind_priv_trap = cp_kind x cp_priv x cp_dbg x cp_tw x cp_trap (required subset): bins ecall_m_trap{ecall m nondbg trap}, ecall_u_trap{ecall u nondbg trap}, ebreak_m_trap{ebreak m nondbg trap}, ebreak_u_trap{ebreak u nondbg trap}, c_ebreak_m_trap{c_ebreak m nondbg trap}, c_ebreak_u_trap{c_ebreak u nondbg trap}, mret_m_ok{mret m nondbg ok}, mret_u_trap{mret u nondbg trap}, dret_m_nondbg_trap{dret m nondbg trap}, dret_u_nondbg_trap{dret u nondbg trap}, dret_dbg_ok{dret m dbg ok}, wfi_m_tw0_ok{wfi m b0 ok}, wfi_m_tw1_ok{wfi m b1 ok}, wfi_u_tw0_ok{wfi u b0 ok}, wfi_u_tw1_trap{wfi u b1 trap}, wfi_dbg_ok{wfi m dbg ok}, sret_m_trap{sret m trap}, sret_u_trap{sret u trap}, uret_m_trap{uret m trap}, uret_u_trap{uret u trap}, sfence_m_trap{sfence_vma m trap}, sfence_u_trap{sfence_vma u trap}, other_m_trap{other_priv m trap}, other_u_trap{other_priv u trap}, nz_m_trap{nz_rs1_rd m trap}, nz_u_trap{nz_rs1_rd u trap}, ecall_dbg_trap{ecall m dbg trap}, mret_dbg_ok{mret m dbg ok}; ignore mret_u_ok, wfi_u_tw1_ok, dret_nondbg_ok, sret/uret/sfence/other/nz x ok: decoder rules are unconditional
  - cr_ecall_cause = cp_kind(ecall) x cp_priv x cp_mcause x cp_mtval: bins ecall_u_8{u ecall_u zero}, ecall_m_11{m ecall_m zero}
  - cr_ebreak_cause = cp_kind x cp_ebreak_dcsr x cp_mcause x cp_mtval: bins ebreak_dcsr0_3{ebreak b0 brk zero}, c_ebreak_dcsr0_3{c_ebreak b0 brk zero}, ebreak_dcsr1_dbg{ebreak b1 debug entry}, c_ebreak_dcsr1_dbg{c_ebreak b1 debug entry}
  - cr_illegal_mtval = cp_kind x cp_trap(trap) x cp_mcause(ill) x cp_mtval(insn): bins mret_u_mtval{mret}, wfi_tw_mtval{wfi}, dret_mtval{dret}, sret_mtval{sret}, uret_mtval{uret}, sfence_mtval{sfence_vma}, nz_mtval{nz_rs1_rd}
- Adopted (riscv-dv): none
- TP items: TP-PRV-009, TP-PRV-015, TP-PRV-016, TP-PRV-019, TP-PRV-020, TP-PRV-021, TP-PRV-024, TP-PRV-027, TP-PRV-036, TP-PRV-039

### CG-PRV-005: gen_cg_prv_wfi
- Features: F-PRV-016, F-PRV-017, F-PRV-018, F-PRV-019, F-PRV-020
- Sample: every retired wfi (trapped or not) with the wake event that ended the sleep (from core_busy_o == IbexMuBiOff, irq pins, irq_nm_i, debug_req_i and the next retirement); condition: rvfi_valid && rvfi_insn == wfi; anti-vacuity: only wfi retirements sample; a hit proves a wfi in that mode/TW/MIE configuration slept for the recorded length and was ended by the recorded source, which gen_chk_sleep checks (no bus activity, correct wake set).
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_tw = mstatus.TW: bins b0{0}, b1{1}
  - cp_mie = mstatus.MIE: bins b0{0}, b1{1}
  - cp_wake = wake source: bins irq_en{irq with mie bit set, incl. already pending at the wfi}, nmi{irq_nm_i}, dbg_req{debug_req_i}, step{dcsr.step = 1 outside debug mode: FLUSH -> DBG_TAKEN_IF, WAIT_SLEEP never entered, rtl/ibex_controller.sv:985-987}, dbg_mode{wfi inside debug mode: one WAIT_SLEEP cycle, SLEEP exits on debug_mode_q, :614-616}; the former none_pending_before bin is dropped (X-8: an already-pending wake still gives the one WAIT_SLEEP cycle, it is irq_en x cp_len.one)
  - cp_irq_dis_seen = an irq pin with mie bit clear toggled during the sleep: bins no{0}, yes{1}
  - cp_len = cycles with core_busy_o == IbexMuBiOff (ibex_mubi_t, the sleep observable; per gen_tb_architecture.md 8.2 item 1 it is Off in WAIT_SLEEP only while no instruction-bus beat is outstanding, no icache invalidation is active and the LSU is idle, so the sample waits for those conditions): bins zero{0: no Off cycle - only the stepped wfi, which never enters WAIT_SLEEP (X-8)}, one{1: the unconditional WAIT_SLEEP cycle with the wake already true, rtl/ibex_controller.sv:598-604}, short{2..16}, long{>16}
  - cp_post = what follows the wfi: bins irq_taken{handler entry}, resume_next{wfi+4 retires}, dbg_entry{debug entry}, trap_tw{illegal instruction}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
- Crosses:
  - cr_priv_tw_post = cp_priv x cp_tw x cp_post: bins m_tw0_irq_taken{m b0 irq_taken}, m_tw1_irq_taken{m b1 irq_taken}, m_tw0_resume{m b0 resume_next}, m_tw1_resume{m b1 resume_next}, u_tw0_irq_taken{u b0 irq_taken}, u_tw1_trap{u b1 trap_tw}, m_tw0_dbg{m b0 dbg_entry}, u_tw0_dbg{u b0 dbg_entry}; ignore u_tw1_irq_taken, u_tw1_resume, u_tw1_dbg: TW=1 in U traps immediately; ignore u_tw0_resume: U-mode interrupts are always enabled so a wake by irq is taken
  - cr_mie_post = cp_priv(m) x cp_mie x cp_post: bins m_mie0_resume{b0 resume_next}, m_mie1_irq_taken{b1 irq_taken}, m_mie0_dbg{b0 dbg_entry}, m_mie1_dbg{b1 dbg_entry}
  - cr_len_wake = cp_len x cp_wake: bins one_irq_en{one irq_en: wake already pending at the wfi}, short_irq_en{short irq_en}, long_irq_en{long irq_en}, long_nmi{long nmi}, short_nmi{short nmi}, long_dbg_req{long dbg_req}, short_dbg_req{short dbg_req}, zero_step{zero step: C-5 stepped wfi}, one_dbg_mode{one dbg_mode: debug-mode wfi}; ignore zero x irq_en / nmi / dbg_req / dbg_mode: an unstepped wfi always passes through WAIT_SLEEP (one ctrl_busy = 0 cycle, rtl/ibex_controller.sv:598-604); ignore step x one / short / long: the stepped wfi never sleeps
  - cr_dis_irq = cp_irq_dis_seen(yes) x cp_wake: bins dis_then_irq_en{yes irq_en}, dis_then_nmi{yes nmi}, dis_then_dbg{yes dbg_req}
  - cr_dbg_wfi = cp_dbg(dbg) x cp_len: bins dbg_one{dbg one: WAIT_SLEEP entered regardless of debug_mode_q, SLEEP left in the same cycle}; ignore dbg_zero: the debug-mode wfi always shows the one WAIT_SLEEP cycle (X-8; the stepped wfi is outside debug mode); ignore dbg_short and dbg_long: SLEEP exits on debug_mode_q in its first cycle
- Adopted (riscv-dv): none
- TP items: TP-CSR-031, TP-PRV-015, TP-PRV-016, TP-PRV-017, TP-PRV-018, TP-PRV-019

### CG-PRV-006: gen_cg_prv_irq_enable
- Features: F-PRV-008, F-PRV-012, F-PRV-018, F-PRV-023, F-PRV-024, F-PRV-029, F-PRV-031
- Sample: every RVFI retirement while irq_pending_o == 1 or irq_nm_i == 1, and every interrupt entry; condition: rvfi_valid && (irq_pending_o || irq_nm_i || rvfi_intr); anti-vacuity: retirements without a pending interrupt never sample; a hit proves an interrupt was pending in the recorded mode/MIE/debug state and was or was not taken before the next retirement, which gen_chk_irq checks against the enable rule.
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{3}, u{0}
  - cp_mie = mstatus.MIE: bins b0{0}, b1{1}
  - cp_taken = interrupt taken before the next retirement: bins yes{1}, no{0}
  - cp_dbg = rvfi_ext_debug_mode: bins nondbg{0}, dbg{1}
  - cp_step = dcsr.step: bins b0{0}, b1{1}
  - cp_nmi_mode = inside an NMI handler (rvfi_ext_nmi since last mret): bins no{0}, yes{1}
  - cp_kind = highest-priority pending source: bins sw{irq_software_i}, timer{irq_timer_i}, ext{irq_external_i}, fast{irq_fast_i}, nmi{irq_nm_i}
  - cp_zcmp = retirement is inside a Zcmp expanded sequence: bins no{0}, yes{1}
- Crosses:
  - cr_priv_mie_taken = cp_priv x cp_mie x cp_taken (nondbg, step 0, no nmi_mode, no zcmp): bins m_0_no{m b0 no}, m_1_yes{m b1 yes}, u_0_yes{u b0 yes}, u_1_yes{u b1 yes}; ignore m_0_yes: MIE=0 blocks in M (NMI covered separately)
  - cr_block = cp_taken(no) x cp_dbg x cp_step x cp_nmi_mode x cp_zcmp: bins blocked_dbg{dbg}, blocked_step{step b1}, blocked_nmi_mode{nmi_mode yes}, blocked_zcmp{zcmp yes}
  - cr_kind_priv = cp_kind x cp_priv x cp_taken(yes): bins sw_m{sw m}, sw_u{sw u}, timer_m{timer m}, timer_u{timer u}, ext_m{ext m}, ext_u{ext u}, fast_m{fast m}, fast_u{fast u}, nmi_m{nmi m}, nmi_u{nmi u}
  - cr_nmi_mie = cp_kind(nmi) x cp_mie x cp_taken(yes): bins nmi_mie0{b0}, nmi_mie1{b1}
- Adopted (riscv-dv): none
- TP items: TP-CSR-026, TP-PRV-003, TP-PRV-007, TP-PRV-011, TP-PRV-017, TP-PRV-022, TP-PRV-023, TP-PRV-028, TP-PRV-030, TP-PRV-037, TP-PRV-038

### CG-PRV-007: gen_cg_prv_debug_priv
- Features: F-PRV-005, F-PRV-015, F-PRV-025, F-PRV-026, F-PRV-027, F-PRV-036, F-DBG-012 (parent of folded bins
  hosted here)
- Sample: (a) debug entry = first retirement with rvfi_ext_debug_mode rising, (b) dret retirement, (d) an mret retired with rvfi_ext_debug_mode = 1 (legal: priv is M inside debug mode; PC <- mepc, priv <- MPP, debug_mode stays 1, rtl/ibex_controller.sv:954-960, RTL-defined F-PRV-036), (c) an exception inside debug mode: a trapped retirement (rvfi_trap = 1) with rvfi_ext_debug_mode == 1 vectoring to DmExceptionAddr, or an ebreak retiring in debug mode (re-entry at DmHaltAddr per rtl/ibex_controller.sv:874-882, no CSR save, identified by next fetch == DmHaltAddr, not by rvfi_trap); condition: any of a..c; anti-vacuity: only debug-related events sample; the dcsr.prv / MPRV / MPP values come from the debug program's own CSR reads (dcsr, mstatus) inside debug mode, so a hit proves a resume of that shape happened and gen_chk_debug / gen_chk_csr_readback checked dcsr/dpc/mstatus.
- Coverpoints:
  - cp_event = event: bins entry{debug entry}, dret{dret}, exc_in_dbg{exception in debug mode}, mret_in_dbg{mret retired with rvfi_ext_debug_mode = 1}
  - cp_mret_dbg_mpp = mstatus.MPP before the debug-mode mret (CSR model, validated by the debug program's csrr) iff (cp_event == mret_in_dbg): bins u{00}, m{11}
  - cp_mret_dbg_target = class of the next record's rvfi_pc_rdata (= mepc & ~1, C-1) iff (cp_event == mret_in_dbg): bins dm_rom{inside DmBaseAddr..DmBaseAddr + DmAddrMask}, outside{outside the DM window}
  - cp_from = mode before entry iff (cp_event == entry): bins m{3}, u{0}
  - cp_cause = dcsr.cause read in debug mode iff (cp_event == entry): bins ebreak{1}, trigger{2}, haltreq{3}, step{4}
  - cp_prv_written = value the debug program wrote to dcsr.prv before dret iff (cp_event == dret): bins none{no write}, u{00}, s{01}, h{10}, m{11}
  - cp_prv_at_dret = dcsr.prv read before dret iff (cp_event == dret): bins u{00}, m{11}
  - cp_mprv_at_dret = mstatus.MPRV before dret iff (cp_event == dret): bins b0{0}, b1{1}
  - cp_mpp_at_dret = mstatus.MPP before dret iff (cp_event == dret): bins u{00}, m{11}
  - cp_mst_touched: RETIRED (S-3b checker-mirror witness; gen_chk_debug owns "M CSRs unchanged by a debug entry")
  - cp_exc_kind = exception kind in debug mode iff (cp_event == exc_in_dbg): bins illegal{illegal instruction}, ecall{ecall}, ebreak{ebreak in debug mode: re-entry at DmHaltAddr, not an exception}, ls_fault{load/store fault}, fetch_fault{fetch fault}, csr_illegal{illegal CSR}
  - cp_mst_after_exc: RETIRED (S-3b checker-mirror witness; gen_chk_debug owns "M CSRs unchanged by a debug-mode exception")
- Crosses:
  - cr_entry = cp_event(entry) x cp_from x cp_cause: bins m_ebreak{m ebreak}, u_ebreak{u ebreak}, m_trigger{m trigger}, u_trigger{u trigger}, m_haltreq{m haltreq}, u_haltreq{u haltreq}, m_step{m step}, u_step{u step}
  - cr_entry_touched: RETIRED (S-3b; cp_mst_touched retired, cr_entry covers the entries)
  - cr_dret_prv = cp_prv_written x cp_prv_at_dret: bins none_m{none m}, none_u{none u}, u_u{u u}, s_u{s u}, h_u{h u}, m_m{m m}; ignore s_m and h_m: legalised to U
  - cr_dret_mprv = cp_prv_at_dret x cp_mprv_at_dret x cp_mpp_at_dret: bins u_1_m{u b1 m B1 core case}, u_1_u{u b1 u}, u_0_u{u b0 u}, u_0_m{u b0 m}, m_1_u{m b1 u}, m_1_m{m b1 m}, m_0_m{m b0 m}, m_0_u{m b0 u}
  - cr_mret_dbg = cp_mret_dbg_mpp x cp_mret_dbg_target: bins m_dm_rom{m dm_rom}, u_dm_rom{u dm_rom}, m_outside{m outside}, u_outside{u outside: U privilege inside debug mode, RTL-defined}
  - cr_exc_dbg = cp_event(exc_in_dbg) x cp_exc_kind: bins illegal{illegal}, ecall{ecall}, ebreak{ebreak}, ls_fault{ls_fault}, fetch_fault{fetch_fault}, csr_illegal{csr_illegal} (the "M CSRs unchanged" witness moved to gen_chk_debug, S-3b)
- Adopted (riscv-dv): none
- TP items: TP-CSR-075, TP-CSR-077, TP-CSR-086, TP-PRV-004, TP-PRV-014, TP-PRV-024, TP-PRV-025, TP-PRV-026, TP-PRV-038, TP-PRV-039

### CG-PRV-008: gen_cg_prv_trap_vector
- Features: F-PRV-002, F-PRV-021, F-PRV-022, F-PRV-029, F-PRV-030, F-PRV-031, F-PRV-032, F-CSR-047
  (parent of folded bins hosted here)
- Sample: every trap entry (the record following a trapped retirement, whose rvfi_pc_rdata is the vector - C-1: the trapped record's own rvfi_pc_wdata is the sequential fetch address - or rvfi_intr on the first handler retirement); condition: rvfi_trap || rvfi_intr; anti-vacuity: ordinary retirements never sample; the target, mepc source and mtval class are computed from RVFI (rvfi_pc_rdata of the next record for the target; pc of the trapping instruction, of the next one, of the LSU instruction in WB for mepc) and the handler's CSR reads, so a hit proves a trap of that class vectored as named and gen_isa_compare compared pc/mepc/mcause/mtval.
- Coverpoints:
  - cp_cause = cause class: bins exc{synchronous exception}, irq_sw{cause 3}, irq_timer{cause 7}, irq_ext{cause 11}, irq_fast{cause 16..30}, nmi_ext{0x8000001F}, nmi_int{0xFFFFFFE0}, dbg_exc{exception in debug mode}
  - cp_fast_id = fast interrupt id iff (cp_cause == irq_fast) (ids 0..$bits(irq_fast_i)-1, generated): bins f0{0}, f1{1}, f2{2}, f3{3}, f4{4}, f5{5}, f6{6}, f7{7}, f8{8}, f9{9}, f10{10}, f11{11}, f12{12}, f13{13}, f14{14}
  - cp_target = trap target class: bins base{mtvec BASE}, base_4id{BASE + 4*id}, base_7c{BASE + 0x7C}, dm_exc_addr{DmExceptionAddr}
  - cp_base = mtvec BASE class: bins boot_page{boot_addr_i[31:8]}, sw_low{software set < 0x1000}, sw_high{software set bit 31}
  - cp_mepc_src = which PC mepc holds (RVFI-derived: the handler's mepc read compared with rvfi_pc_rdata of the trapping record, of the LSU record in WB, or of the next record; see Probe candidates): bins pc_if{next unexecuted}, pc_id{faulting instruction}, pc_wb{LSU instruction in WB}
  - cp_mtval = mtval class: bins zero{0}, insn32{32-bit encoding}, insn16{16-bit encoding zero-extended}, addr{faulting address}
  - cp_from_priv = rvfi_mode of the trapping/interrupted instruction: bins m{3}, u{0}
  - cp_younger_in_id = a younger instruction was in ID when a WB LSU fault trapped (inferred from RVFI: the younger instruction's record appears exactly once, after the handler's mret; see Probe candidates): bins no{0}, yes{1}
- Crosses:
  - cr_cause_target = cp_cause x cp_target: bins exc_base{exc base}, irq_sw_4id{irq_sw base_4id}, irq_timer_4id{irq_timer base_4id}, irq_ext_4id{irq_ext base_4id}, irq_fast_4id{irq_fast base_4id}, nmi_ext_7c{nmi_ext base_7c}, nmi_int_7c{nmi_int base_7c}, dbg_exc_dm{dbg_exc dm_exc_addr}
  - cr_fast_id: RETIRED (S-7 identity cross of cp_fast_id, which is irq_fast-only by its iff; TP-PRV-028 references cp_fast_id.f0..f14)
  - cr_cause_mepc = cp_cause x cp_mepc_src x cp_younger_in_id: bins exc_pc_id{exc pc_id no}, exc_pc_wb{exc pc_wb no}, exc_pc_wb_younger{exc pc_wb yes}, irq_pc_if{irq_sw irq_timer irq_ext irq_fast pc_if}, nmi_pc_if{nmi_ext nmi_int pc_if}
  - cr_exc_mtval = cp_cause(exc) x cp_mtval: bins exc_zero{zero ecall ebreak}, exc_insn32{insn32}, exc_insn16{insn16}, exc_addr{addr}
  - cr_base_cause = cp_base x cp_cause: bins boot_exc{boot_page exc}, boot_irq{boot_page irq_timer}, low_irq_sw{sw_low irq_sw}, high_irq_fast{sw_high irq_fast}, high_nmi{sw_high nmi_ext}, low_exc{sw_low exc}, high_exc{sw_high exc}
  - cr_from_cause = cp_from_priv x cp_cause: bins u_exc{u exc}, u_irq_fast{u irq_fast}, u_nmi{u nmi_ext}, m_exc{m exc}, m_irq_ext{m irq_ext}, m_nmi_int{m nmi_int}, u_nmi_int{u nmi_int}
- Adopted (riscv-dv): none
- TP items: TP-CSR-035, TP-CSR-037, TP-CSR-041, TP-CSR-047, TP-CSR-048, TP-CSR-049, TP-PRV-002, TP-PRV-004, TP-PRV-011, TP-PRV-020, TP-PRV-021, TP-PRV-028, TP-PRV-029, TP-PRV-030, TP-PRV-031, TP-PRV-037

## Counts

| Quantity | Count |
|---|---|
| covergroups | 25 (CG-CSR-001..017, CG-PRV-001..008) |
| coverpoints | 209 live (+16 coverpoints/crosses retired in FIX2 stay listed as RETIRED lines for traceability) |
| crosses | 120 |
| coverpoint bins | 906 |
| cross bins | 1205 |
| total bins | 2111 |
| adopted (riscv-dv) bins | 0 |
| bins referenced by at least one TP item | 1505 distinct listed in Bins lines (3570 CSV rows incl. the constituent coverpoint bins of listed cross bins; the two P7 probe-gated coverpoints are excluded) |
| ignore clauses declared | 56 (each with a reason; never-hit witnesses are checker facts, not bins) |

Traceability convention for trace_tp_bin_csr.csv: an item row for a cross bin implies rows for the
constituent coverpoint bins named in that cross bin's description (the CSV lists them explicitly:
3570 rows after the FIX3 delta - 25 P7 probe-gated / X-8-retired rows removed, 55 rows added for
cr_op_form_gap, the two new hole ranges, TP-CSR-103, TP-PRV-008/018/019 and TP-PRV-039 - from the
post-ignore bin set, adopted = 0 everywhere).
Counts and ranges derive from ibex_pkg parameters as defined in the conventions (MHPMCounterNum,
PMPNumRegions, $bits(irq_fast_i), DbgHwBreakNum); the bin lists above expand them for this build.

## Probe candidates

Bins that cannot be sampled from the DUT boundary or RVFI alone. The DV Lead decides whether the
named internal signal enters the probe register; each entry gives the boundary alternative used
if the probe is refused.

- CG-CSR-010.cp_pulse (and every cr_op_form_pulse bin): probe candidate P7 (PROPOSED in
  dv/auto_dv/docs/gen_probe_register.md, Critic ruling pending; cp_pulse and cr_op_form_pulse are
  coverage-only and excluded from the Bins lines, the CSV and the manifests until ruled):
  cs_registers_i.dummy_instr_seed_en_o and dummy_instr_seed_o (rtl/ibex_cs_registers.sv:1914-1915);
  never a fire-check or checker input (rtl-arch T-053 UNOBSERVABLE rows TP-CSR-002/092/093). The
  reseed has no boundary or RVFI footprint (dummy instructions are not reported on RVFI and their
  cadence is not deterministic). The items assert the boundary form instead: read-back 0, flush
  bubble for write ops and none for demoted reads (cr_op_form_gap, cr_form_priv_trap).
- CG-CSR-013.cp_carry_win (cp_carry_win.yes): the exact cycle of the mcycleh write commit is
  internal (cs_registers_i.csr_we_int with csr_addr == MCYCLEH; P6-class net, not requested). Boundary inference used by
  TP-CSR-064: rvfi_ext_mcycle of the retiring writer shows low == 0xFFFF_FFFF and high == written
  value; the inference is exact because rvfi_ext_mcycle is captured at the writer's retirement.
  No probe needed unless the inference is found ambiguous in simulation.
- CG-CSR-013.cp_coincide for hpm counters (cr_minstret_wr.hpm_lo_wr_coincide,
  hpm_hi_wr_coincide, hpm_lo_set_coincide): the event (load/store retiring in WB) in the CSR
  write cycle is inferred from RVFI ordering (load retirement immediately before the CSR write
  with dmem_rvalid_delay = min1). Candidate probe if the inference is too loose:
  cs_registers_i.mhpmcounter_incr[k] in the write cycle.
- CG-CSR-015.cp_cause.dbg_req_before (cr_cause_fam.dbg_before_*): inferred from dpc read in the
  debug ROM == the CSR instruction pc; no probe needed.
- CG-CSR-001.cp_iclass / CG-CSR-014 classes: TB-derived from address, op, mode and
  rvfi_ext_debug_mode; no probe.
- TP-CSR-102 witness gen_sva_csr_excl: never (cs_registers_i.csr_we_int &&
  cs_registers_i.csr_save_cause_i) is an internal assertion on P6-class nets (both operands internal,
  same cycle; witness/coverage only, never a checker);
  boundary alternative: none (the item's boundary pass criteria stand on their own; the assertion
  is an extra witness).
- CG-CSR-013.cp_wb_state and cp_coincide (instruction in WB at a minstret / hpm10 read; countable
  event in a counter write cycle): pipeline-state inferences from RVFI ordering (the preceding
  record is a load/store retiring in the reader's / writer's cycle under knob:dmem_rvalid_delay =
  min1). Listed as inferences, no probe requested; the exact nets would be wb_stage_i.instr_done_wb
  and id_stage_i.instr_perf_count_id_o in that cycle (P4-class, coverage-only if ever admitted).
- CG-PRV-008.cp_mepc_src and cp_younger_in_id (which PC mepc holds; a younger instruction in ID at a
  WB fault): inferred from RVFI (the handler's mepc read against rvfi_pc_rdata of the trapping / LSU
  / next record; the younger instruction's single record after the handler's mret). No probe
  requested; the exact net would be id_stage_i.instr_valid_i in the trap cycle (P4-class).
- CG-PRV-006.cp_nmi_mode and cr_block.blocked_nmi_mode: NMI mode is inferred from rvfi_ext_nmi on
  the entry and the following mret; no probe.
- CG-PRV-006.cp_zcmp and cr_block.blocked_zcmp: "inside a Zcmp expanded sequence" is inferred
  from rvfi_insn of the retiring cm.* instruction and the retirement gap; if the DV Lead wants
  exactness, the probe is id_stage_i.instr_expanded_q (rtl/ibex_id_stage.sv, compressed-decoder
  FSM), otherwise the RVFI inference stands.


# 3.3 Areas EXC, IRQ: Synchronous exceptions; interrupts, NMI, WFI, vectoring


Area group EXC + IRQ (F-EXC-001..069, F-IRQ-001..066). Source: dv/auto_dv/work/dv-lead/parts/
gen_part_exc_irq.md; behaviour summaries CTRL-05..19, CTRL-23, CTRL-39..44. Companion test plan:
tp_exc_irq.md (same directory).

Conventions
- Every covergroup lives in the gen_ namespace (gen_cg_exc_*, gen_cg_irq_*) inside gen_fcov_pkg or
  a gen_*_cov module bound through gen_binds.sv. No RTL covergroup is extended (the RTL has none).
- Sampling events come from monitors (RVFI monitor, ibus/dbus monitors, irq/debug pin monitor,
  gen_chk_* model events), never from a bare clock. Each Sample line carries an anti-vacuity note.
- Counts/ranges derive from ibex_pkg: fast-interrupt count = $bits(ibex_pkg::irqs_t.irq_fast) (15),
  fast id = CSR_MFIX_BIT_LOW + index (16..30), interrupt-enable positions CSR_MSIX_BIT (3),
  CSR_MTIX_BIT (7), CSR_MEIX_BIT (11), mstatus positions CSR_MSTATUS_{MIE,MPIE,MPP,MPRV,TW}_BIT,
  cause constants ExcCause* and exc_cause_t, controller states ctrl_fsm_e, PC selectors
  exc_pc_sel_e, Zcmp classes instr_exp_e, debug causes dbg_cause_e, NMI_INT_CAUSE_ECC. Array bins
  written `name[15]` expand to name_0..name_14 with 15 = $bits(irqs_t.irq_fast).
- Bins referenced by TP items and the CSV use CG-<AREA>-<nnn>.cp_<name>.<bin> and
  CG-<AREA>-<nnn>.cr_<name>.<bin>. Cross bins are named as the concatenation of their member bins
  in coverpoint order; the `bins {...}` list of a cross names the REQUIRED cross bins.
- Transition-style bins are enumerated explicitly; no `illegal_bins = default sequence` anywhere.
- "Predicted cause" and "CSR model" mean the gen_isa_compare / gen_chk_csr_readback prediction for
  the trap record, obtained from the retired handler csrr read-back (ibex_core has no rvfi_csr_*
  ports). "Program order" facts come from the test's program listing (ELF), which the TB has.
- Adopted bins: none. This subagent's task does not name riscv-dv, so no riscv-dv source was
  read; every bin below is our own (adopted = 0 in trace_tp_bin_exc_irq.csv).
- Multi-event covergroups name their events in the Sample line (ev_a, ev_b, ...) and every coverpoint
  carries `iff <event>` (S-3c); a coverpoint without a guard samples on every event of its group.
- Single owners (S-7): pc[1]/mepc[1] alignment is covered only by CG-EXC-012.cp_mepc_bit1 /
  cr_kind_bit1; "exception commit x interrupt pending" only by CG-EXC-013.cp_irq_at_commit and its
  crosses; the boundary triple (fetch stalled x data error x interrupt pending) is owned by
  fcov_xcut.md CG-XIF-001. Retired coverpoints/crosses keep their line with a RETIRED note.
- MIE_WARL_MASK = (1 << CSR_MSIX_BIT) | (1 << CSR_MTIX_BIT) | (1 << CSR_MEIX_BIT) |
  (((1 << $bits(irqs_t.irq_fast)) - 1) << CSR_MFIX_BIT_LOW) (the writable mie bits); NUM_IRQ_LINES =
  $bits(irqs_t.irq_fast) + 3.
- Decision cycle (S-4): the DECODE/FIRST_FETCH cycle N in which handle_irq holds with ID empty, no
  stall, no special request and WB done (rtl/ibex_controller.sv:704-713); IRQ_TAKEN = N + 1, where the
  LIVE pins decide (CTRL-09). N is located from the pipeline state (ID empty per RVFI / the ibus
  monitor, WB done per the dbus monitor, irq_pending_o with MIE or U-mode), never from the
  rvfi_ext_irq_valid port: that port is a LEVEL (C-13 / fact-check X-16) whose internal flop is set at
  N (rtl/ibex_core.sv:1965-1971) and which rises at N + 4 after three RVFI stages (:1992-2002,
  :2134-2141, :2192-2199; RVFI_STAGES = 2, :1837), stays high until about two cycles after the
  handler's first instruction enters ID, is not generated when ID emptied before WB drained
  (captured_valid already set, :1949-1968), never coincides with rvfi_valid, and for a SLEEP wake
  rises at W + 4 = IRQ_TAKEN + 2; where present it is compared as rise == N + 4. rvfi_ext_pre_mip is
  captured when ID first empties, which can precede the WB drain (:1949-1957), so it equals the pins
  at the CAPTURE cycle, not necessarily at N. RVFI-anchored timestamps are back-dated by one cycle
  (rvfi_valid is one flop after WB exit, :1868); commit-to-record offsets: 2 (CSR writes,
  GEN_CSR_WRITE_TO_RVFI_OFFSET), 1 (trap/mret/dret, GEN_TRAP_TO_RVFI_OFFSET); an exception commit
  (pc_set / FLUSH) = trap record - 1. Redirect targets of trap / mret / dret records are the NEXT
  record's rvfi_pc_rdata (their rvfi_pc_wdata is the next sequential fetch address, C-1 / X-1); only
  branch / jump records carry the target in rvfi_pc_wdata.
- ICache blindness (C-14): an ibus observation ("vector fetch", "no fetch at X", "first instr_req_o
  after On") is valid only when the owning item pins cpuctrlsts.icache_enable = 0 or the RTL forces
  the icache off (debug mode, the dret cycle, rtl/ibex_cs_registers.sv:1970-1971); the request is
  issued in the pc_set cycle only when no fill buffer holds an ungranted request
  (rtl/ibex_icache.sv:703, 764-776, 1030-1031). Bins that need a redirect derive it from RVFI.
- Internal-NMI latency (C-7 / X-10, D21): up to two ordinary instructions (more records with a Zcmp
  sequence) retire between the corrupted response and the NMI entry; CG-IRQ-008.cp_taken_after
  counts them and the first directed integrity-error sim confirms the bound.
- Trap-record fields (C-12 / X-14, X-15, B18): rvfi_mem_rmask / wmask are 0 on WB-trap records
  (rtl/ibex_core.sv:2156-2157; rvfi_mem_addr kept, :2164) and carry the garbage decode on ID-trap
  and non-store records; access kind / size are decoded from rvfi_insn. rvfi_insn is the 32-bit
  expansion for Zcmp micro-ops (:2263-2267, halfword on rvfi_ext_expanded_insn) and the
  zero-extended halfword 32'h00009002 for c.ebreak.
- S-2: an ebreak that enters debug mode retires with rvfi_trap == 0 (rtl/ibex_core.sv:1885-1886); the
  debug path is is_ebreak(rvfi_insn) && !rvfi_trap && next fetch == DmHaltAddr, the exception path
  rvfi_trap == 1.
- Features lines may cite ALIAS / FOLDED feature IDs (gen_part_exc_irq.md `- Status:` lines); the
  bin named in a FOLDED status is the one that carries the folded edge and exists in this file.

## Covergroups: EXC

### CG-EXC-001: gen_cg_exc_trap_entry
- Features: F-EXC-001, F-EXC-002, F-EXC-042, F-EXC-049, F-EXC-060, F-EXC-062, F-EXC-063, F-EXC-064, F-EXC-067, F-EXC-068
- Sample: ev_a = RVFI trap record; condition: rvfi_valid && rvfi_trap && !rvfi_ext_debug_mode, with the predicted cause taken from the gen_isa_compare trap model of that record; ev_b (cp_odd_target only) = a retired jalr/jal/branch whose computed target (rvfi_rs1_rdata + imm, or pc + imm) has bit 0 or bit 1 set, with rvfi_trap == 0; anti-vacuity: rvfi_trap is 0 on every normal retirement and interrupts never set it, so a hit of ev_a proves a synchronous exception committed outside debug mode; ev_b samples only control transfers to non-word-aligned targets, so a hit proves such a transfer completed without an instruction-address-misaligned trap.
- Coverpoints:
  - cp_cause iff ev_a = predicted mcause[4:0]: bins fetch_fault{1}, illegal{2}, breakpoint{3}, load_fault{5}, store_fault{7}, ecall_u{8}, ecall_m{11}; ignore_bins misaligned{0,4,6}: never generated in non-CHERIoT mode (F-EXC-029, F-EXC-067); ignore_bins cheri{28}: cheriot-out-of-scope
  - cp_priv iff ev_a = rvfi_mode of the trapping instruction: bins m{3}, u{0}; ignore_bins s_h{1,2}: privilege modes not implemented
  - cp_ilen iff ev_a = rvfi_insn[1:0] of the faulting instruction: bins c16{0,1,2}, w32{3}
  - cp_pc_align: RETIRED (S-7 single owner): pc[1] alignment of a trap is CG-EXC-012.cp_mepc_bit1 / cr_kind_bit1
  - cp_mtvec_class iff ev_a = class of the mtvec value in force (tracked from boot and retired csrw/csrs mtvec): bins boot_init{never written}, sw_aligned{written with wdata[7:0] in {0,1}}, sw_legalised{written with wdata[7:2] != 0 and legalised}
  - cp_prev_mie iff ev_a = mstatus.MIE before the trap (CSR model): bins mie0{0}, mie1{1}
  - cp_younger_killed iff ev_a = fetched-not-retired words discarded at the flush (ibus monitor vs RVFI): bins none{0}, one{1}, many{[2:$]}
  - cp_odd_target iff ev_b = target alignment of a retired control transfer: bins odd_no_trap{jalr target bit 0 set: no trap, next rvfi_pc_rdata == target & ~1}, half_target{target bit 1 set, bit 0 clear: 2-byte aligned target executes}
- Crosses:
  - cr_cause_priv_ilen = cp_cause x cp_priv x cp_ilen: bins {fetch_fault_m_c16, fetch_fault_m_w32, fetch_fault_u_c16, fetch_fault_u_w32, illegal_m_c16, illegal_m_w32, illegal_u_c16, illegal_u_w32, breakpoint_m_c16, breakpoint_m_w32, breakpoint_u_c16, breakpoint_u_w32, load_fault_m_c16, load_fault_m_w32, load_fault_u_c16, load_fault_u_w32, store_fault_m_c16, store_fault_m_w32, store_fault_u_c16, store_fault_u_w32, ecall_u_u_w32, ecall_m_m_w32}; ignore ecall_u x m, ecall_m x u: the cause encodes the privilege; ignore ecall_* x c16: there is no compressed ECALL encoding
  - cr_cause_mtvec = cp_cause x cp_mtvec_class: bins {fetch_fault_boot_init, fetch_fault_sw_aligned, fetch_fault_sw_legalised, illegal_boot_init, illegal_sw_aligned, illegal_sw_legalised, breakpoint_boot_init, breakpoint_sw_aligned, breakpoint_sw_legalised, load_fault_boot_init, load_fault_sw_aligned, load_fault_sw_legalised, store_fault_boot_init, store_fault_sw_aligned, store_fault_sw_legalised, ecall_u_boot_init, ecall_u_sw_aligned, ecall_u_sw_legalised, ecall_m_boot_init, ecall_m_sw_aligned, ecall_m_sw_legalised}
  - cr_cause_mie = cp_cause x cp_prev_mie: bins {fetch_fault_mie0, fetch_fault_mie1, illegal_mie0, illegal_mie1, breakpoint_mie0, breakpoint_mie1, load_fault_mie0, load_fault_mie1, store_fault_mie0, store_fault_mie1, ecall_u_mie0, ecall_u_mie1, ecall_m_mie0, ecall_m_mie1}
  - cr_cause_pcalign: RETIRED (S-7): see CG-EXC-012.cr_kind_bit1
  - cr_cause_killed = cp_cause x cp_younger_killed: bins {load_fault_one, store_fault_one, illegal_many, ecall_m_many, fetch_fault_none}
- Adopted (riscv-dv): none
- TP items: TP-EXC-001, TP-EXC-002, TP-EXC-007, TP-EXC-013, TP-EXC-016, TP-EXC-017, TP-EXC-022, TP-EXC-023, TP-EXC-024, TP-EXC-026, TP-EXC-034, TP-EXC-041, TP-EXC-049, TP-EXC-060, TP-EXC-062, TP-EXC-063, TP-EXC-064, TP-EXC-068, TP-EXC-069, TP-EXC-071

### CG-EXC-002: gen_cg_exc_fetch_fault
- Features: F-EXC-003, F-EXC-004, F-EXC-005, F-EXC-006, F-EXC-007, F-EXC-045, F-EXC-059
- Sample: ev_a = a trap record with predicted cause 1, correlated with the error-marked fetch words of the ibus monitor (instr_err_i=1 responses) and the gen_chk_pmp I-side deny list; ev_b = an error-marked word that is discarded (redirect derived from RVFI: the preceding retirement has rvfi_pc_wdata != pc + len, or is a trap/mret/dret record, or an interrupt/debug entry follows) without ever producing a trap record; condition: the ibus monitor holds an error mark for the word; anti-vacuity: error marks exist only under knob:imem_err_rate != none, a directed injection or a PMP deny, so a hit proves an error-marked word was consumed (trap) or dropped (no trap).
- Coverpoints:
  - cp_source = origin of the error mark: bins bus_err{instr_err_i}, pmp{I-side PMP deny}, both{same word carries both}
  - cp_half iff ev_a = which fetch word of the instruction carried the error: bins first{mtval == mepc}, second_plus2{mtval == mepc + 2}, both_words{both words errored; mtval == mepc}
  - cp_ilen iff ev_a = instruction length: bins c16{16-bit}, w32{32-bit}
  - cp_pc_align: RETIRED (S-7 single owner): CG-EXC-012.cp_mepc_bit1
  - cp_flow iff ev_a = how the faulting pc was reached: bins sequential, branch_target, jump_target, mret_target, dret_target, popret_target{ret micro-op of cm.popret/cm.popretz}, handler_first{pc == mtvec base}
  - cp_also_illegal iff ev_a = the errored word also decodes as illegal (TB decoder on the returned rdata): bins clean{0}, illegal_bits{1}
  - cp_outcome = observed outcome: bins trap{word consumed in ID}, discarded_branch, discarded_jump, discarded_exception, discarded_mret, discarded_irq, discarded_debug, discarded_dret
  - cp_prefetch_depth iff ev_b = error-marked words fetched ahead when the discard happened: bins one{1}, two_three{[2:3]}, four_plus{[4:$]}
- Crosses:
  - cr_source_half = cp_source x cp_half: bins {bus_err_first, bus_err_second_plus2, bus_err_both_words, pmp_first, pmp_second_plus2, pmp_both_words, both_first}
  - cr_half_ilen = cp_half x cp_ilen: bins {first_c16, first_w32, second_plus2_w32, both_words_w32}; ignore second_plus2 x c16, both_words x c16: a 16-bit instruction occupies one fetch word
  - cr_flow_outcome = cp_flow x cp_outcome: bins {sequential_trap, branch_target_trap, jump_target_trap, mret_target_trap, dret_target_trap, popret_target_trap, handler_first_trap, sequential_discarded_branch, sequential_discarded_jump, sequential_discarded_exception, sequential_discarded_mret, sequential_discarded_irq, sequential_discarded_debug, sequential_discarded_dret}; ignore cp_flow != sequential x discarded_*: a discarded word is always a fall-through word behind the redirect (ev_b has no target flow)
  - cr_illegal_source = cp_also_illegal x cp_source: bins {illegal_bits_bus_err, illegal_bits_pmp, clean_bus_err, clean_pmp}
  - cr_outcome_depth = cp_outcome x cp_prefetch_depth: bins {discarded_branch_one, discarded_branch_two_three, discarded_jump_four_plus, discarded_exception_one, discarded_irq_two_three}; ignore trap x any depth: cp_prefetch_depth is defined for ev_b only
  - cr_flow_align: RETIRED (S-7): see CG-EXC-012.cr_kind_bit1
- Adopted (riscv-dv): none
- TP items: TP-EXC-001, TP-EXC-002, TP-EXC-003, TP-EXC-004, TP-EXC-005, TP-EXC-006, TP-EXC-044, TP-EXC-059, TP-EXC-061, TP-EXC-071, TP-EXC-073

### CG-EXC-003: gen_cg_exc_illegal
- Features: F-EXC-008, F-EXC-009, F-EXC-010, F-EXC-011, F-EXC-012, F-EXC-013, F-EXC-014, F-EXC-015, F-EXC-016
- Sample: ev_a = a trap record with predicted cause 2, or a cause-5/7 trap record whose next program-order instruction is decode-illegal and was killed (F-EXC-016 outcome b); ev_b (cp_kind.trigger_csr_mmode_no_trap only) = a retired (rvfi_trap == 0) csrr/csrrw/csrrs/csrrc of tselect/tdata1..3 with rvfi_ext_debug_mode == 0; condition: illegal class identified from rvfi_insn / the program listing; anti-vacuity: only decode- or privilege-rejected instructions give cause 2, so a hit of ev_a proves the named illegal class executed and trapped (or was displaced by a WB fault); ev_b samples only trigger-CSR accesses outside debug mode, so a hit proves such an access retired without the trap that debug.rst:54-55 describes (doc defect D12).
- Coverpoints:
  - cp_kind = illegal class: bins decoder_reject, csr_nonexistent, csr_ro_write, csr_priv_u{U-mode access to an M CSR}, csr_debug_outside{dcsr/dpc/dscratch0/1 outside debug mode, M-mode}, trigger_csr_mmode_no_trap{tselect/tdata1..3 accessed outside debug mode in M-mode: retires with rvfi_trap == 0 (doc defect D12; sample b)}, mret_umode, wfi_tw_umode, dret_outside_debug, system_rs1rd_nonzero, zcmp_reserved_rlist
  - cp_ilen = instruction length from rvfi_insn[1:0]: bins c16, w32
  - cp_priv = privilege mode of the instruction (rvfi_mode): bins m, u
  - cp_mtval_form iff ev_a = mtval read-back: bins zext16{mtval[31:16]==0, mtval[15:0]==raw halfword}, full32{mtval == 32-bit encoding}
  - cp_wb_state iff ev_a = WB content when the illegal instruction reached ID: bins wb_empty, wb_ls_ok{outstanding load/store completed without error, illegal then taken}, wb_ls_fault{WB fault won; illegal killed}
  - cp_system_sub iff (ev_a && cp_kind == system_rs1rd_nonzero) = encoding class: bins ecall_enc, ebreak_enc, mret_enc, wfi_enc, dret_enc
- Crosses:
  - cr_kind_ilen = cp_kind x cp_ilen: bins {decoder_reject_c16, decoder_reject_w32, csr_nonexistent_w32, csr_ro_write_w32, csr_priv_u_w32, csr_debug_outside_w32, mret_umode_w32, wfi_tw_umode_w32, dret_outside_debug_w32, system_rs1rd_nonzero_w32, zcmp_reserved_rlist_c16}; ignore csr_*/mret_umode/wfi_tw_umode/dret_outside_debug/system_rs1rd_nonzero x c16: 32-bit-only encodings; ignore zcmp_reserved_rlist x w32: Zcmp is 16-bit; ignore trigger_csr_mmode_no_trap x c16: CSR instructions are 32-bit only
  - cr_kind_priv = cp_kind x cp_priv: bins {decoder_reject_m, decoder_reject_u, csr_nonexistent_m, csr_nonexistent_u, csr_ro_write_m, csr_ro_write_u, csr_priv_u_u, csr_debug_outside_m, mret_umode_u, wfi_tw_umode_u, dret_outside_debug_m, dret_outside_debug_u, system_rs1rd_nonzero_m, system_rs1rd_nonzero_u, zcmp_reserved_rlist_m, zcmp_reserved_rlist_u}; ignore csr_priv_u x m, mret_umode x m, wfi_tw_umode x m: U-mode-only causes; ignore csr_debug_outside x u: classified as csr_priv_u first; ignore trigger_csr_mmode_no_trap x u: a U-mode trigger-CSR access traps and is classified csr_priv_u (ev_b is M-mode only)
  - cr_kind_wb = cp_kind x cp_wb_state: bins {decoder_reject_wb_empty, decoder_reject_wb_ls_ok, decoder_reject_wb_ls_fault, csr_nonexistent_wb_ls_ok, csr_nonexistent_wb_ls_fault, system_rs1rd_nonzero_wb_ls_ok, zcmp_reserved_rlist_wb_ls_ok}; ignore trigger_csr_mmode_no_trap x any: ev_b is not a trap
  - cr_kind_mtval = cp_kind x cp_mtval_form: bins {decoder_reject_zext16, decoder_reject_full32, zcmp_reserved_rlist_zext16, csr_nonexistent_full32, mret_umode_full32, wfi_tw_umode_full32, dret_outside_debug_full32}; ignore trigger_csr_mmode_no_trap x any: no trap, no mtval; ignore zcmp_reserved_rlist x full32 and csr_*/mret_umode/wfi_tw_umode/dret_outside_debug/system_rs1rd_nonzero x zext16: mtval form follows the encoding length
  - cr_sub_priv = cp_system_sub x cp_priv: bins {ecall_enc_m, ecall_enc_u, ebreak_enc_m, ebreak_enc_u, mret_enc_m, wfi_enc_m, wfi_enc_u, dret_enc_m}
- Adopted (riscv-dv): none
- TP items: TP-EXC-007, TP-EXC-008, TP-EXC-009, TP-EXC-010, TP-EXC-011, TP-EXC-012, TP-EXC-013, TP-EXC-014, TP-EXC-015, TP-EXC-071

### CG-EXC-004: gen_cg_exc_ebreak
- Features: F-EXC-017, F-EXC-018, F-EXC-019, F-EXC-020, F-EXC-021, F-EXC-022
- Sample: ev_a = retirement or trap record of EBREAK (rvfi_insn == 32'h00100073, or 32'h00009002 for c.ebreak, which is traced as the zero-extended halfword and never expanded, rtl/ibex_core.sv:2263-2265, X-14 / C-12; the debug path retires with rvfi_trap == 0 and the next fetch at DmHaltAddr, S-2); ev_b = each debug-entry event reported by gen_chk_debug with dcsr.cause in {EBREAK, TRIGGER}; ev_c = each configured trigger address reached in IF (tdata2 match candidate from the program listing); condition: one of those events; anti-vacuity: samples only when an ebreak/c.ebreak retired or trapped or a tdata2 address was fetched, so a hit proves the routing decision was exercised.
- Coverpoints:
  - cp_form iff ev_a = encoding form (rvfi_insn, C-12): bins ebreak32{rvfi_insn == 32'h00100073}, c_ebreak16{rvfi_insn == 32'h00009002}
  - cp_priv iff ev_a = privilege mode of the instruction (rvfi_mode): bins m, u
  - cp_dcsr_ebreak iff ev_a = {dcsr.ebreakm, dcsr.ebreaku} from the CSR model: bins m0u0, m1u0, m0u1, m1u1
  - cp_outcome iff ev_a = observed outcome: bins exception{cause 3, rvfi_trap == 1}, debug_entry{rvfi_trap == 0, rvfi_ext_debug_mode == 0 on the ebreak, next fetch DmHaltAddr, dcsr.cause = DBG_CAUSE_EBREAK}, debug_reentry{rvfi_ext_debug_mode == 1 on the ebreak: next fetch DmHaltAddr, dcsr/dpc unchanged}
  - cp_trigger iff (ev_b || ev_c) = trigger match handling: bins trigger_entry{dcsr.cause = DBG_CAUSE_TRIGGER, no cause-3 trap}, trigger_squashed{tdata2 word discarded by a redirect from ID; no debug entry}, trigger_on_ebreak_addr{tdata2 == address of an ebreak: trigger entry, no breakpoint exception}
  - cp_mepc_align: RETIRED (S-7 single owner): CG-EXC-012.cp_mepc_bit1
- Crosses:
  - cr_priv_dcsr_outcome = cp_priv x cp_dcsr_ebreak x cp_outcome: bins {m_m0u0_exception, m_m0u1_exception, m_m1u0_debug_entry, m_m1u1_debug_entry, u_m0u0_exception, u_m1u0_exception, u_m0u1_debug_entry, u_m1u1_debug_entry}; ignore every other priv x dcsr x outcome combination: the outcome is a function of priv and the matching dcsr bit; a mismatch is a gen_chk_debug/gen_isa_compare failure, not a bin
  - cr_form_outcome = cp_form x cp_outcome: bins {ebreak32_exception, ebreak32_debug_entry, ebreak32_debug_reentry, c_ebreak16_exception, c_ebreak16_debug_entry, c_ebreak16_debug_reentry}
  - cr_form_align: RETIRED (S-7): see CG-EXC-012.cr_kind_bit1
  - cr_trigger_priv = cp_trigger x cp_priv: bins {trigger_entry_m, trigger_entry_u, trigger_squashed_m, trigger_squashed_u, trigger_on_ebreak_addr_m}
- Adopted (riscv-dv): none
- TP items: TP-EXC-016, TP-EXC-017, TP-EXC-018, TP-EXC-019, TP-EXC-020, TP-EXC-021, TP-EXC-064

### CG-EXC-005: gen_cg_exc_ecall
- Features: F-EXC-023, F-EXC-024, F-EXC-058, F-EXC-065
- Sample: a trap record with predicted cause 8 or 11; condition: rvfi_insn == 32'h00000073 && rvfi_trap; anti-vacuity: only ECALL gives causes 8/11, so a hit proves an ECALL trapped from the recorded privilege.
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{3 -> cause 11}, u{0 -> cause 8}
  - cp_mtval_pre = mtval value before the ECALL (CSR model): bins was_zero, was_nonzero
  - cp_pc_align: RETIRED (S-7 single owner): CG-EXC-012.cp_mepc_bit1
  - cp_seen_pre = cpuctrlsts.sync_exc_seen before the ECALL: bins seen0{0}, seen1{1}
  - cp_mie_pre = mstatus.MIE before: bins mie0, mie1
- Crosses:
  - cr_priv_mtval = cp_priv x cp_mtval_pre: bins {m_was_zero, m_was_nonzero, u_was_zero, u_was_nonzero}
  - cr_priv_seen = cp_priv x cp_seen_pre: bins {m_seen0, m_seen1, u_seen0, u_seen1}
  - cr_priv_align: RETIRED (S-7): see CG-EXC-012.cr_kind_bit1
  - cr_priv_mie = cp_priv x cp_mie_pre: bins {m_mie0, m_mie1, u_mie0, u_mie1}
- Adopted (riscv-dv): none
- TP items: TP-EXC-022, TP-EXC-023, TP-EXC-058, TP-EXC-066

### CG-EXC-006: gen_cg_exc_lsu_fault
- Features: F-EXC-025, F-EXC-026, F-EXC-027, F-EXC-028, F-EXC-029, F-EXC-030, F-EXC-031, F-EXC-032, F-EXC-033, F-EXC-034, F-EXC-035, F-EXC-036, F-EXC-037, F-EXC-038, F-EXC-039, F-EXC-040, F-EXC-069
- Sample: ev_a = a trap record with predicted cause 5 or 7, correlated with the dbus monitor transactions of that instruction (request pattern, error response cycle, gnt-to-rvalid latency); ev_b (cp_mis_no_trap only) = a retired misaligned access (two dbus requests for one rvfi_mem_* record) with rvfi_trap == 0; condition: ev_a rvfi_trap && cause in {5,7}, ev_b split access retired; anti-vacuity: only injected data_err_i responses or PMP-denied data accesses give cause 5/7, so a hit of ev_a proves such a fault was taken with the recorded pipeline context; ev_b samples only split accesses, so a hit proves a misaligned access completed without a cause-4/6 trap.
- Coverpoints:
  - cp_op iff ev_a = access kind decoded from rvfi_insn (rvfi_mem_rmask / wmask are zero on WB-trap records, rtl/ibex_core.sv:2156-2157, X-15 / C-12; the dbus record confirms data_we_o): bins load, store
  - cp_source iff ev_a = fault origin (dbus error response vs gen_chk_pmp deny): bins bus_err{data_err_i response}, pmp{D-side PMP deny; no bus request for that half}
  - cp_align iff ev_a = which part of the access faulted: bins aligned{single word}, mis_first{misaligned, first half faults}, mis_second{misaligned, second half faults}, mis_both{both halves fault}
  - cp_size iff ev_a = access size from rvfi_insn funct3 (the masks are zero on WB-trap records, C-12): bins byte, half, word
  - cp_zcmp iff ev_a = the faulting access is a Zcmp micro-op: bins none, cm_push_op, cm_pop_op{cm.pop/cm.popret/cm.popretz}
  - cp_op_pos iff (ev_a && cp_zcmp != none) = micro-op index within the Zcmp sequence: bins first, middle, last
  - cp_younger iff ev_a = the instruction in ID when the fault response arrived (next program-order instruction after the faulting one that did not retire before the trap): bins none{ID empty}, alu, branch, jump, load_store, csr_rw, illegal, ecall_ebreak, wfi, mret, fetch_errored
  - cp_spec_fetch iff ev_a = instr_addr_o hit the younger branch/jump target between the branch's ID arrival and the trap commit (ibus monitor, icache off per the owning items; a taken branch / jal / jalr redirects IF in its FIRST ID cycle under instr_executing_spec, rtl/ibex_id_stage.sv:889-941, 1054-1057): bins yes, no{not-taken branch, load-dependent branch / jalr held by stall_ld_hz, or the branch arrived in the error cycle}
  - cp_mtval_class iff ev_a = mtval read-back: bins eq_addr{unaligned effective address}, eq_second_word{(addr & ~3) + 4}
  - cp_resp_latency iff ev_a = gnt-to-rvalid cycles of the erroring response: bins one{1}, short{[2:4]}, long{[5:$]}
  - cp_irq_pending: RETIRED (S-7 single owner): interrupt state at an exception commit is CG-EXC-013.cp_irq_at_commit
  - cp_bus_pattern iff ev_a = requests seen on the data bus for the access: bins single_req{aligned, one request}, two_reqs{misaligned, both halves requested}, first_only{second half suppressed by PMP}, second_only{first half blocked by PMP, second issued}, none{no request at all}
  - cp_mis_no_trap iff ev_b = misaligned access retired without trap: bins half_cross{halfword at addr%4 == 3}, word_off1{word at addr%4 == 1}, word_off2{addr%4 == 2}, word_off3{addr%4 == 3}
- Crosses:
  - cr_op_source_align = cp_op x cp_source x cp_align: bins {load_bus_err_aligned, load_bus_err_mis_first, load_bus_err_mis_second, load_bus_err_mis_both, load_pmp_aligned, load_pmp_mis_first, load_pmp_mis_second, load_pmp_mis_both, store_bus_err_aligned, store_bus_err_mis_first, store_bus_err_mis_second, store_bus_err_mis_both, store_pmp_aligned, store_pmp_mis_first, store_pmp_mis_second, store_pmp_mis_both}
  - cr_align_size = cp_align x cp_size: bins {aligned_byte, aligned_half, aligned_word, mis_first_half, mis_first_word, mis_second_half, mis_second_word, mis_both_half, mis_both_word}; ignore byte x mis_*: byte accesses never split
  - cr_align_mtval = cp_align x cp_mtval_class: bins {aligned_eq_addr, mis_first_eq_addr, mis_second_eq_second_word, mis_both_eq_addr}; ignore aligned/mis_first/mis_both x eq_second_word: the RTL reports the first faulting half; a mismatch is a gen_chk_csr_readback failure
  - cr_op_younger = cp_op x cp_younger: bins {load_none, load_alu, load_branch, load_jump, load_load_store, load_csr_rw, load_illegal, load_ecall_ebreak, load_wfi, load_mret, load_fetch_errored, store_none, store_alu, store_branch, store_jump, store_load_store, store_csr_rw, store_illegal, store_ecall_ebreak, store_wfi, store_mret, store_fetch_errored}
  - cr_op_zcmp = cp_op x cp_zcmp x cp_op_pos: bins {store_cm_push_op_first, store_cm_push_op_middle, store_cm_push_op_last, load_cm_pop_op_first, load_cm_pop_op_middle, load_cm_pop_op_last}; ignore load x cm_push_op, store x cm_pop_op: push sequences contain only stores, pop sequences only loads; ignore none x any cp_op_pos: no micro-op index outside a sequence
  - cr_younger_spec = cp_younger x cp_spec_fetch: bins {branch_yes, branch_no, jump_yes, jump_no}; ignore cp_younger not in {branch, jump} x any: a speculative target fetch exists only for a control transfer in ID
  - cr_source_pattern = cp_source x cp_align x cp_bus_pattern: bins {bus_err_aligned_single_req, bus_err_mis_first_two_reqs, bus_err_mis_second_two_reqs, bus_err_mis_both_two_reqs, pmp_aligned_none, pmp_mis_first_second_only, pmp_mis_second_first_only, pmp_mis_both_none}; ignore pmp x aligned x single_req: a denied aligned access issues nothing
  - cr_latency_irq: RETIRED (S-7): the irq operand moved to CG-EXC-013.cr_wb_irq_ibus / cr_stage_irq; cp_resp_latency stays a plain coverpoint
  - cr_op_size_source = cp_op x cp_size x cp_source: bins {load_byte_bus_err, load_half_bus_err, load_word_bus_err, load_byte_pmp, load_word_pmp, store_byte_bus_err, store_half_bus_err, store_word_bus_err, store_half_pmp, store_word_pmp}
- Adopted (riscv-dv): none
- TP items: TP-EXC-024, TP-EXC-025, TP-EXC-026, TP-EXC-027, TP-EXC-028, TP-EXC-029, TP-EXC-030, TP-EXC-031, TP-EXC-032, TP-EXC-033, TP-EXC-034, TP-EXC-035, TP-EXC-036, TP-EXC-037, TP-EXC-038, TP-EXC-039, TP-EXC-042, TP-EXC-043, TP-EXC-070, TP-EXC-071, TP-EXC-073, TP-IRQ-058, TP-IRQ-072

### CG-EXC-007: gen_cg_exc_priority
- Features: F-EXC-007, F-EXC-013, F-EXC-016, F-EXC-036, F-EXC-041, F-EXC-069
- Sample: a cycle in which two or more exception conditions are present at once, built from the dbus monitor (data_rvalid_i & data_err_i response cycle -> WB fault), the ibus monitor (error-marked word in ID), the program listing (decode-illegal / rs1-rd-nonzero SYSTEM / ECALL / EBREAK encoding of the instruction in ID) (ID arrival = ibus delivery + the fixed IF->ID offset, valid only with cpuctrlsts.icache_enable = 0, S-4); condition: popcount(present causes) >= 2; anti-vacuity: the vast majority of traps have exactly one cause, so a hit proves two conditions coexisted in one cycle and the winner was compared.
- Coverpoints:
  - cp_pair = the pair present: bins st_fetch, st_illegal, st_ecall, st_ebreak, ld_fetch, ld_illegal, ld_ecall, ld_ebreak, fetch_illegal, fetch_ecall, fetch_ebreak, illegal_ecall, illegal_ebreak, triple_wb_fetch_illegal; ignore_bins ld_st: only one instruction is in WB; ignore_bins ecall_ebreak: mutually exclusive encodings
  - cp_winner = predicted cause taken: bins store_fault, load_fault, fetch_fault, illegal; ignore_bins ecall_ebreak_win{8,11,3}: never the winner of a collision
  - cp_irq_also: RETIRED (S-7 single owner): CG-EXC-013.cp_irq_at_commit / cr_stage_irq
  - cp_illegal_kind iff (cp_pair in {st_illegal, ld_illegal, fetch_illegal, illegal_ecall, illegal_ebreak, triple_wb_fetch_illegal}) = illegal sub-class: bins decoder, csr_check, system_rs1rd
- Crosses:
  - cr_pair_winner = cp_pair x cp_winner: bins {st_fetch_store_fault, st_illegal_store_fault, st_ecall_store_fault, st_ebreak_store_fault, ld_fetch_load_fault, ld_illegal_load_fault, ld_ecall_load_fault, ld_ebreak_load_fault, fetch_illegal_fetch_fault, fetch_ecall_fetch_fault, fetch_ebreak_fetch_fault, illegal_ecall_illegal, illegal_ebreak_illegal, triple_wb_fetch_illegal_store_fault, triple_wb_fetch_illegal_load_fault}; ignore all other pair x winner combinations: the winner is fixed by the RTL order; a mismatch is a gen_isa_compare failure
  - cr_pair_irq: RETIRED (S-7): see CG-EXC-013.cr_stage_irq
  - cr_pair_kind = cp_pair x cp_illegal_kind: bins {st_illegal_decoder, st_illegal_csr_check, ld_illegal_decoder, ld_illegal_csr_check, fetch_illegal_decoder, illegal_ecall_system_rs1rd, illegal_ebreak_system_rs1rd}; ignore pairs without an illegal member x any kind; ignore illegal_ecall/illegal_ebreak x decoder/csr_check: a SYSTEM encoding with rs1/rd != 0 is the only way ECALL/EBREAK bits are illegal
- Adopted (riscv-dv): none
- TP items: TP-EXC-006, TP-EXC-012, TP-EXC-015, TP-EXC-035, TP-EXC-040, TP-EXC-065, TP-EXC-072, TP-IRQ-026

### CG-EXC-008: gen_cg_exc_zcmp
- Features: F-EXC-015, F-EXC-043, F-EXC-044, F-EXC-045, F-IRQ-020, F-EXC-003 (parent of folded bins
  hosted here)
- Sample: a trap record or interrupt entry whose faulting/interrupted instruction is a Zcmp cm.* (rvfi_ext_expanded_insn_valid seen for that pc, or rvfi_insn is a cm.* encoding), and the Zcmp reserved-rlist illegal trap; condition: cm.* pc identified; anti-vacuity: only cm.push/cm.pop* instructions sample, so a hit proves a sequence was hit by a fault or an interrupt at the recorded micro-op.
- Coverpoints:
  - cp_seq = Zcmp form (encoding): bins cm_push, cm_pop, cm_popret, cm_popretz
  - cp_event = event kind: bins store_fault, load_fault, fetch_fault_ret_target{fetch fault at the popret return address, attributed to the target}, irq_during_expanded{interrupt while INSTR_EXPANDED micro-ops run: mepc = cm.* pc}, irq_during_commit_deferred{interrupt during INSTR_EXPANDED_COMMIT: taken after LAST}, reserved_rlist_illegal
  - cp_op_pos iff (cp_event in {store_fault, load_fault, irq_during_expanded}) = micro-op index at the event: bins first, middle, last
  - cp_rlist iff (cp_event != reserved_rlist_illegal) = rlist field: bins r4{4}, r5_7{[5:7]}, r8_11{[8:11]}, r12_15{[12:15]}
  - cp_after_mret iff (cp_event in {store_fault, load_fault, irq_during_expanded}) = behaviour after the handler's mret (RVFI): bins reexecuted_from_first{sequence re-runs from micro-op 0}, handler_advanced_mepc{handler skipped the cm.*}
- Crosses:
  - cr_seq_event = cp_seq x cp_event: bins {cm_push_store_fault, cm_push_irq_during_expanded, cm_push_irq_during_commit_deferred, cm_push_reserved_rlist_illegal, cm_pop_load_fault, cm_pop_irq_during_expanded, cm_pop_irq_during_commit_deferred, cm_pop_reserved_rlist_illegal, cm_popret_load_fault, cm_popret_fetch_fault_ret_target, cm_popret_irq_during_expanded, cm_popret_irq_during_commit_deferred, cm_popret_reserved_rlist_illegal, cm_popretz_load_fault, cm_popretz_fetch_fault_ret_target, cm_popretz_irq_during_expanded, cm_popretz_irq_during_commit_deferred, cm_popretz_reserved_rlist_illegal}; ignore cm_push x load_fault, cm_pop* x store_fault: one access kind per sequence; ignore cm_push/cm_pop x fetch_fault_ret_target: no return micro-op
  - cr_event_pos = cp_event x cp_op_pos: bins {store_fault_first, store_fault_middle, store_fault_last, load_fault_first, load_fault_middle, load_fault_last, irq_during_expanded_first, irq_during_expanded_middle, irq_during_expanded_last}; ignore fetch_fault_ret_target/irq_during_commit_deferred/reserved_rlist_illegal x any: no micro-op position (after the sequence, in the commit phase, or no sequence started)
  - cr_event_rlist = cp_event x cp_rlist: bins {store_fault_r4, store_fault_r12_15, load_fault_r4, load_fault_r12_15, irq_during_expanded_r5_7, irq_during_expanded_r8_11, irq_during_commit_deferred_r12_15}; ignore reserved_rlist_illegal x any: rlist 0..3 has no legal bin
  - cr_event_after = cp_event x cp_after_mret: bins {store_fault_reexecuted_from_first, load_fault_reexecuted_from_first, irq_during_expanded_reexecuted_from_first, store_fault_handler_advanced_mepc, load_fault_handler_advanced_mepc}; ignore fetch_fault_ret_target/irq_during_commit_deferred/reserved_rlist_illegal x any: the sequence is not restarted after these events; ignore irq_during_expanded x handler_advanced_mepc: the interrupt handler returns to mepc unchanged
- Adopted (riscv-dv): none
- TP items: TP-EXC-014, TP-EXC-042, TP-EXC-043, TP-EXC-044, TP-EXC-074, TP-IRQ-025, TP-IRQ-076

### CG-EXC-009: gen_cg_exc_debug_mode
- Features: F-EXC-020, F-EXC-046, F-EXC-047, F-EXC-048, F-IRQ-039
- Sample: an exception condition (any cause) while rvfi_ext_debug_mode == 1, or an exception commit in the same cycle as debug_req_i (debug pin monitor) or with dcsr.step == 1 (CSR model); condition: exception event with one of those contexts; anti-vacuity: exceptions outside debug mode without a concurrent debug request do not sample, so a hit proves the debug interplay case occurred.
- Coverpoints:
  - cp_cause = exception cause (predicted): bins fetch_fault, illegal, load_fault, store_fault, ecall, ebreak
  - cp_context = debug context at the event: bins in_debug, not_debug_req_same_cycle, not_debug_step
  - cp_dcsr_prv iff (cp_context == in_debug) = dcsr.prv at the event: bins m, u
  - cp_seen_pre = cpuctrlsts.sync_exc_seen before: bins seen0, seen1
  - cp_target = rvfi_pc_rdata of the first retirement after the event (RVFI, C-14; in debug mode and at DBG_TAKEN_IF the icache is forced off, so the ibus agrees): bins dm_exception_addr, dm_halt_addr; ignore_bins mtvec_base: the group samples only debug contexts, in which the handler never retires first (in_debug: a checker failure; same-cycle debug request / step: FLUSH -> DBG_TAKEN_IF lands at DmHaltAddr with dpc = the vector, rtl/ibex_controller.sv:985-987; the vector word may be requested speculatively but never retires)
- Crosses:
  - cr_cause_context = cp_cause x cp_context: bins {fetch_fault_in_debug, illegal_in_debug, load_fault_in_debug, store_fault_in_debug, ecall_in_debug, ebreak_in_debug, fetch_fault_not_debug_req_same_cycle, illegal_not_debug_req_same_cycle, load_fault_not_debug_req_same_cycle, store_fault_not_debug_req_same_cycle, ecall_not_debug_req_same_cycle, illegal_not_debug_step, ecall_not_debug_step, load_fault_not_debug_step}
  - cr_context_target = cp_context x cp_target: bins {in_debug_dm_exception_addr, in_debug_dm_halt_addr, not_debug_req_same_cycle_dm_halt_addr, not_debug_step_dm_halt_addr}; ignore any x mtvec_base: see cp_target; ignore not_debug_req_same_cycle/not_debug_step x dm_exception_addr: DmExceptionAddr is reachable from debug mode only
  - cr_cause_prv = cp_cause x cp_dcsr_prv: bins {illegal_u, ecall_u, load_fault_u, store_fault_u, fetch_fault_u, illegal_m, ecall_m, load_fault_m}
  - cr_context_seen = cp_context x cp_seen_pre: bins {in_debug_seen1, in_debug_seen0, not_debug_req_same_cycle_seen1}
- Adopted (riscv-dv): none
- TP items: TP-EXC-019, TP-EXC-045, TP-EXC-046, TP-EXC-047, TP-EXC-048, TP-IRQ-043

### CG-EXC-010: gen_cg_exc_double_fault
- Features: F-EXC-047, F-EXC-054, F-EXC-055, F-EXC-056, F-EXC-057, F-EXC-058, F-EXC-059, F-SEC-022
  (parent of folded bins hosted here)
- Sample: every event that moves the gen_chk_double_fault model: trap entries (sync/irq/nmi), retired mret, retired csrw/csrs/csrc cpuctrlsts, and each double_fault_seen_o pulse; condition: model event or output pulse; anti-vacuity: idle cycles never sample, so a hit proves an arming, clearing or pulse event happened and was compared against the model.
- Coverpoints:
  - cp_event = event kind: bins sync_arm{sync exception with seen 0 -> 1}, sync_double{sync exception with seen = 1: pulse}, irq_seen1{interrupt entry with seen = 1: no pulse, no clear}, nmi_seen1, mret_exc_handler{clears}, mret_irq_in_exc{mret of an interrupt handler nested inside an exception handler: clears sync_exc_seen (documented behaviour, exception_interrupts.rst:191 / cs_registers.rst:556; design-weakness note B12, not a bug candidate)}, mret_nmi_handler{clears}, sw_clear_seen, sw_set_seen, sw_clear_double, sw_set_double_no_pulse, exc_in_debug_seen1{no arm, no pulse}, storm_3plus{>= 3 consecutive vector re-entries}
  - cp_first_cause iff (cp_event in {sync_arm, sync_double}) = cause that armed: bins fetch_fault, illegal, breakpoint, load_fault, store_fault, ecall
  - cp_second_cause iff (cp_event == sync_double) = cause of the double: bins fetch_fault, illegal, breakpoint, load_fault, store_fault, ecall
  - cp_readback = cpuctrlsts read-back class: bins pulse_then_read1{cpuctrlsts.double_fault_seen reads 1 after a pulse}, sw_cleared_then_read0, seen_read1_in_handler, seen_read0_after_mret
  - cp_gap iff (cp_event in {sync_double, irq_seen1, nmi_seen1, storm_3plus}) = instructions retired between the arming trap and the event: bins zero{0}, few{[1:8]}, many{[9:$]}
- Crosses:
  - cr_first_second = cp_first_cause x cp_second_cause: bins {fetch_fault_fetch_fault, fetch_fault_illegal, fetch_fault_load_fault, illegal_illegal, illegal_ecall, illegal_load_fault, illegal_store_fault, illegal_breakpoint, breakpoint_illegal, breakpoint_breakpoint, load_fault_illegal, load_fault_load_fault, load_fault_ecall, store_fault_store_fault, store_fault_ecall, ecall_illegal, ecall_ecall, ecall_load_fault, ecall_store_fault, ecall_fetch_fault}
  - cr_event_gap = cp_event x cp_gap: bins {sync_double_zero, sync_double_few, sync_double_many, irq_seen1_few, storm_3plus_zero}
  - cr_event_readback = cp_event x cp_readback: bins {sync_double_pulse_then_read1, sw_clear_double_sw_cleared_then_read0, sync_arm_seen_read1_in_handler, mret_exc_handler_seen_read0_after_mret}
- Adopted (riscv-dv): none
- TP items: TP-EXC-047, TP-EXC-054, TP-EXC-055, TP-EXC-056, TP-EXC-057, TP-EXC-058, TP-EXC-059, TP-EXC-072

### CG-EXC-011: gen_cg_exc_mret
- Features: F-EXC-010, F-EXC-050, F-EXC-051, F-EXC-052, F-EXC-053, F-EXC-061, F-IRQ-023, F-IRQ-027, F-IRQ-029
- Sample: retirement of MRET (rvfi_insn == 32'h30200073) or its illegal-instruction trap record, with the CSR model state before the mret and the irq monitor state at the retirement cycle; condition: mret in rvfi_insn; anti-vacuity: only mret instructions sample, so a hit proves a return (or a U-mode attempt) happened with the recorded stack state.
- Coverpoints:
  - cp_priv_at = privilege at the mret (rvfi_mode): bins m, u
  - cp_mpp = mstatus.MPP class before the mret (CSR model incl. the last software write): bins m{11}, u{00}, sw01_read_u{last write 01, reads 00}, sw10_read_u{last write 10, reads 00}
  - cp_mpie = mstatus.MPIE before the mret (CSR model): bins mpie0, mpie1
  - cp_mprv = mstatus.MPRV before the mret (CSR model): bins mprv0, mprv1
  - cp_mepc_bits = mepc WARL on software write (read-back; the bit1 alignment bins are RETIRED, S-7 single owner CG-EXC-012.cp_mepc_bit1): bins sw_bit0_dropped{software wrote mepc with bit 0 set; reads 0}
  - cp_context = what the mret returns from: bins exc_handler, irq_handler, nmi_handler, plain{not inside any trap handler}
  - cp_pending_at = irq state at the mret retirement: bins none, irq_enabled{mie set, taken with restored MIE or U-mode}, irq_disabled{mie set, MPIE = 0, returning to M}, nmi
  - cp_prefetch_discarded = fall-through words fetched after the mret and never retired: bins zero{0}, one_plus{[1:$]}
- Crosses:
  - cr_mpp_mprv = cp_mpp x cp_mprv (M-mode mrets): bins {m_mprv1, u_mprv1, m_mprv0, u_mprv0, sw01_read_u_mprv1, sw10_read_u_mprv1}
  - cr_context_pending = cp_context x cp_pending_at: bins {exc_handler_none, exc_handler_irq_enabled, exc_handler_irq_disabled, exc_handler_nmi, irq_handler_none, irq_handler_irq_enabled, irq_handler_irq_disabled, irq_handler_nmi, nmi_handler_none, nmi_handler_irq_enabled, nmi_handler_nmi, plain_irq_enabled, plain_none}
  - cr_mpp_pending = cp_mpp x cp_pending_at: bins {u_irq_enabled, u_irq_disabled, m_irq_enabled, m_irq_disabled, u_nmi, m_nmi}
  - cr_mpie_pending = cp_mpie x cp_pending_at: bins {mpie0_irq_enabled, mpie1_irq_enabled, mpie0_irq_disabled}
  - cr_priv_mpp = cp_priv_at x cp_mpp: bins {m_m, m_u, m_sw01_read_u, m_sw10_read_u, u_m, u_u}
  - cr_context_prefetch = cp_context x cp_prefetch_discarded: bins {exc_handler_one_plus, irq_handler_one_plus, plain_one_plus, nmi_handler_zero}
  - cr_bits_context = cp_mepc_bits x cp_context: bins {sw_bit0_dropped_plain}; ignore sw_bit0_dropped x exc_handler/irq_handler/nmi_handler: a hardware-written mepc never has bit 0 set (trap-context alignment bins are in CG-EXC-012.cr_kind_bit1)
- Adopted (riscv-dv): none
- TP items: TP-EXC-009, TP-EXC-050, TP-EXC-051, TP-EXC-052, TP-EXC-053, TP-EXC-061, TP-IRQ-028, TP-IRQ-032, TP-IRQ-034, TP-IRQ-035, TP-IRQ-036, TP-IRQ-037

### CG-EXC-012: gen_cg_exc_trap_csrs
- Features: F-EXC-001, F-EXC-042, F-EXC-049, F-EXC-063, F-EXC-065, F-EXC-066, F-EXC-050 (parent of
  folded bins hosted here)
- Sample: completion of the handler read-back set for one trap (gen_chk_csr_readback matches the retired csrr mepc/mcause/mtval/mstatus to the trap), with crash_dump_o and the minstret read-back sampled at that point; condition: read-back set complete; anti-vacuity: samples once per trap whose handler reads the CSRs, so a hit proves the written values were observed and compared.
- Coverpoints:
  - cp_kind = trap kind (sync exception / interrupt / NMI): bins sync, irq, nmi_ext, nmi_int
  - cp_old_mie = mstatus.MIE before the trap: bins mie0, mie1
  - cp_old_priv = privilege before the trap (CSR model): bins m, u
  - cp_mtval_class = mtval read-back: bins zero, pc, pc_plus2, insn32, insn16, data_addr, data_addr_second
  - cp_mepc_bit1 = mepc[1] read-back (single owner of pc[1]/mepc[1] alignment, S-7): bins bit1_0{mepc[1] == 0: word-aligned trapped/interrupted pc}, bit1_1{mepc[1] == 1: 2-byte-aligned pc, 16-bit instruction before it}
  - cp_kept = pre-trap fields that must survive the entry: bins mprv1_kept, tw1_kept, both_zero
  - cp_crash_dump: RETIRED (S-3b): equality-with-prediction bins are checker mirrors; gen_chk_crash_dump owns the compare and cp_kind records the trap kinds at which it ran
  - cp_minstret = mcountinhibit.IR in force at the trap (CSR model): bins ir0{IR == 0: the handler's minstret read-back is compared against the retirement count excluding the trap record}, ir1{IR == 1: minstret frozen across the trap}
- Crosses:
  - cr_kind_mtval = cp_kind x cp_mtval_class: bins {sync_zero, sync_pc, sync_pc_plus2, sync_insn32, sync_insn16, sync_data_addr, sync_data_addr_second, irq_zero, nmi_ext_zero, nmi_int_data_addr}; ignore irq/nmi_ext x non-zero and nmi_int x non-data_addr: the RTL writes 0 / the captured address; a mismatch is a checker failure
  - cr_kind_mie_priv = cp_kind x cp_old_mie x cp_old_priv: bins {sync_mie0_m, sync_mie1_m, sync_mie0_u, sync_mie1_u, irq_mie1_m, irq_mie0_u, irq_mie1_u, nmi_ext_mie0_m, nmi_ext_mie1_m, nmi_ext_mie0_u, nmi_ext_mie1_u, nmi_int_mie0_m, nmi_int_mie1_m, nmi_int_mie1_u}; ignore irq x mie0 x m: not taken
  - cr_kind_kept = cp_kind x cp_kept: bins {sync_mprv1_kept, sync_tw1_kept, irq_mprv1_kept, irq_tw1_kept, nmi_ext_mprv1_kept, sync_both_zero}
  - cr_kind_bit1 = cp_kind x cp_mepc_bit1: bins {sync_bit1_1, irq_bit1_1, nmi_ext_bit1_1, nmi_int_bit1_1, sync_bit1_0, irq_bit1_0, nmi_ext_bit1_0, nmi_int_bit1_0}
  - cr_kind_crash: RETIRED (S-3b): see cp_crash_dump
- Adopted (riscv-dv): none
- TP items: TP-EXC-001, TP-EXC-003, TP-EXC-013, TP-EXC-022, TP-EXC-023, TP-EXC-024, TP-EXC-030, TP-EXC-041, TP-EXC-049, TP-EXC-063, TP-EXC-066, TP-EXC-067, TP-IRQ-001, TP-IRQ-007, TP-IRQ-013, TP-IRQ-044

### CG-EXC-013: gen_cg_exc_timing
- Features: F-EXC-016, F-EXC-035, F-EXC-060, F-EXC-062, F-EXC-069, F-IRQ-021, F-IRQ-022, F-EXC-001
  (parent of folded bins hosted here)
- Sample: an exception commit = the pc_set / FLUSH cycle = the trap record's cycle - GEN_TRAP_TO_RVFI_OFFSET (1) (S-4; the vector request on the ibus is >= that cycle and bus-visible only with the icache off, C-14, so the record, not the request, anchors the commit), with the cycle bookkeeping of the dbus/ibus monitors and the irq monitor at the trigger cycle; condition: commit detected; single owner of the exception-side "commit x interrupt pending" coverage (S-7); anti-vacuity: only exception commits sample, so a hit proves a trap was committed with the recorded latency and bus/irq context.
- Coverpoints:
  - cp_exc_stage = stage raising the exception: bins id_cause{fetch fault / illegal / ecall / ebreak}, wb_cause{load / store fault}
  - cp_latency = cycles from the trigger (ID: the instruction's arrival in ID = ibus delivery + the fixed IF->ID offset, valid only with cpuctrlsts.icache_enable = 0; WB: the error response cycle) to the commit (pc_set = trap record - 1): bins min{1}, two{2}, three_five{[3:5]}, long{[6:$]}
  - cp_vector_req_delay = cycles from the commit to instr_req_o at the vector (ibus monitor; valid only with cpuctrlsts.icache_enable = 0 per the owning items, C-14): bins same_cycle{0}, deferred{[1:$]: a fill buffer held an ungranted prefetch request, rtl/ibex_icache.sv:703, 764-776, 1030-1031}
  - cp_wb_at_id_exc iff (cp_exc_stage == id_cause) = WB content when an ID exception was requested: bins wb_empty, wb_ls_ok, wb_ls_fault_wins
  - cp_irq_at_commit = interrupt state at the commit cycle (irq monitor): bins none{irq_pending_o == 0 && !irq_nm_i}, irq_enabled{irq_pending_o && (MIE || U-mode)}, nmi{irq_nm_i || internal NMI pending}
  - cp_ibus_at_commit = instruction-bus state at the trigger cycle: bins idle, gnt_pending, rvalid_pending
  - cp_dbus_at_commit = data-bus state at the trigger cycle (dbus monitor): bins idle, gnt_pending, rvalid_pending
  - cp_killed_younger = younger instruction killed by the flush (RVFI vs ibus monitor): bins none, one
- Crosses:
  - cr_stage_latency = cp_exc_stage x cp_latency: bins {id_cause_min, id_cause_two, id_cause_three_five, id_cause_long, wb_cause_min}; ignore wb_cause x non-min: a WB fault commits on the next cycle (gen_chk_trap_timing bound); ignore id_cause x min unless WB is empty: with an outstanding access the ID cause waits for the WB drain
  - cr_wb_irq_ibus = cp_wb_at_id_exc x cp_irq_at_commit x cp_ibus_at_commit: bins {wb_ls_fault_wins_irq_enabled_rvalid_pending, wb_ls_fault_wins_irq_enabled_gnt_pending, wb_ls_fault_wins_irq_enabled_idle, wb_ls_ok_irq_enabled_rvalid_pending, wb_empty_irq_enabled_idle, wb_ls_fault_wins_nmi_rvalid_pending, wb_ls_fault_wins_none_rvalid_pending, wb_ls_ok_none_idle}; the exception-side view of the DV_prompt triple (fetch stalled x data error x interrupt pending); the boundary triple itself is fcov_xcut.md CG-XIF-001.cr_fetch_x_async (S-10)
  - cr_stage_irq = cp_exc_stage x cp_irq_at_commit: bins {id_cause_irq_enabled, wb_cause_irq_enabled, id_cause_nmi, wb_cause_nmi, id_cause_none, wb_cause_none} (absorbs the retired CG-EXC-006.cr_latency_irq and CG-EXC-007.cr_pair_irq)
  - cr_stage_dbus = cp_exc_stage x cp_dbus_at_commit: bins {id_cause_idle, id_cause_rvalid_pending, id_cause_gnt_pending, wb_cause_idle}
  - cr_stage_killed = cp_exc_stage x cp_killed_younger: bins {wb_cause_one, wb_cause_none, id_cause_none}
- Adopted (riscv-dv): none
- TP items: TP-EXC-015, TP-EXC-034, TP-EXC-060, TP-EXC-062, TP-EXC-070, TP-EXC-071, TP-EXC-072, TP-IRQ-026, TP-IRQ-027, TP-IRQ-039, TP-IRQ-072

## Covergroups: IRQ

### CG-IRQ-001: gen_cg_irq_entry
- Features: F-IRQ-001, F-IRQ-002, F-IRQ-007, F-IRQ-008, F-IRQ-016, F-IRQ-024, F-IRQ-029, F-IRQ-053,
  F-IRQ-057, F-IRQ-058, F-IRQ-045 (parent of folded bins hosted here)
- Sample: interrupt entry: rvfi_valid && rvfi_intr on the first handler instruction, with the cause from the handler csrr mcause read-back / gen_chk_irq model and the CSR model state before the entry (the rvfi_ext_irq_valid level, C-13, is recorded per entry as a marker, never used as the event); condition: rvfi_intr; anti-vacuity: rvfi_intr is 0 on every instruction that is not the first of an interrupt handler (exception handlers do not set it), so a hit proves an interrupt entry.
- Coverpoints:
  - cp_line = cause of the entry: bins software{3}, timer{7}, external{11}, fast[15]{[16:30], id = CSR_MFIX_BIT_LOW + index, count = $bits(irqs_t.irq_fast)}, nmi_ext{31}, nmi_int{0xFFFFFFE0}
  - cp_priv_pre = privilege before the entry (rvfi_mode of the last retired instruction / CSR model): bins m, u
  - cp_mie_global = mstatus.MIE before the entry: bins mie0, mie1
  - cp_others = state of the other mie-enabled lines at the entry: bins only_this, others_enabled_idle, others_pending_lower{a lower-priority line also pending}
  - cp_mepc_src = what mepc points at: bins sequential{next sequential pc}, branch_target, jump_target, mret_target, dret_target, wfi_next{wfi + 4}, boot_pc{reset-time NMI}, cm_pc{restart pc of an interrupted Zcmp sequence}
  - cp_u_path iff (cp_priv_pre == u) = how U-mode was reached: bins mret_mpp_u, dret_prv_u
  - cp_u_pending_at_return iff (cp_priv_pre == u) = line state at the return into U: bins already_pending{line pending at the mret/dret}, arrived_later
  - cp_rvfi_marks = RVFI interrupt markers: bins intr_with_pre_mip{rvfi_intr with rvfi_ext_pre_mip != 0}, irq_valid_level{rvfi_ext_irq_valid level seen for the entry, rising at N + 4 with rvfi_valid == 0 throughout (C-13 / X-16)}, irq_valid_absent{entry with no rvfi_ext_irq_valid: ID emptied before WB drained, rtl/ibex_core.sv:1949-1968}, pre_post_mip_equal, pre_post_mip_differ, nmi_flag{rvfi_ext_nmi}, nmi_int_flag{rvfi_ext_nmi_int}; ignore_bins exc_handler_first_intr0: unreachable under this group's sample (rvfi_intr is set for interrupt vectors only, rtl/ibex_core.sv:2403-2413, so an exception handler's first instruction never samples here); the negative property is owned by gen_isa_compare (S-3d)
- Crosses:
  - cr_line_priv_mie = cp_line x cp_priv_pre x cp_mie_global: bins {software_m_mie1, software_u_mie0, software_u_mie1, timer_m_mie1, timer_u_mie0, timer_u_mie1, external_m_mie1, external_u_mie0, external_u_mie1, fast_0_m_mie1, fast_0_u_mie0, fast_7_u_mie1, fast_14_m_mie1, fast_14_u_mie0, nmi_ext_m_mie0, nmi_ext_m_mie1, nmi_ext_u_mie0, nmi_ext_u_mie1, nmi_int_m_mie0, nmi_int_m_mie1, nmi_int_u_mie0}; ignore {software, timer, external, fast_*} x m x mie0: not taken in M-mode with MIE clear
  - cr_line_mepc = cp_line x cp_mepc_src: bins {software_sequential, timer_branch_target, external_jump_target, fast_3_mret_target, fast_9_dret_target, external_wfi_next, nmi_ext_boot_pc, fast_0_cm_pc, nmi_ext_wfi_next, nmi_int_sequential, software_mret_target, timer_dret_target, fast_14_sequential, external_branch_target}; ignore cp_line != nmi_ext x boot_pc: at reset mie is 0 and no data access has completed, so only the external NMI can be taken before the first instruction
  - cr_upath_pending = cp_u_path x cp_u_pending_at_return x cp_mie_global (U entries only, via the iff of both operands): bins {mret_mpp_u_already_pending_mie0, mret_mpp_u_already_pending_mie1, mret_mpp_u_arrived_later_mie0, mret_mpp_u_arrived_later_mie1, dret_prv_u_already_pending_mie0, dret_prv_u_arrived_later_mie1}
  - cr_line_others = cp_line x cp_others: bins {fast_0_others_pending_lower, external_others_pending_lower, software_others_pending_lower, timer_only_this, fast_14_others_pending_lower, software_only_this, external_others_enabled_idle}
  - cr_line_marks = cp_line x cp_rvfi_marks: bins {software_intr_with_pre_mip, fast_5_intr_with_pre_mip, nmi_ext_nmi_flag, nmi_int_nmi_int_flag, external_irq_valid_level, timer_pre_post_mip_differ}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-001, TP-IRQ-002, TP-IRQ-003, TP-IRQ-004, TP-IRQ-005, TP-IRQ-006, TP-IRQ-007, TP-IRQ-012, TP-IRQ-013, TP-IRQ-014, TP-IRQ-019, TP-IRQ-021, TP-IRQ-025, TP-IRQ-028, TP-IRQ-029, TP-IRQ-031, TP-IRQ-034, TP-IRQ-044, TP-IRQ-049, TP-IRQ-053, TP-IRQ-057, TP-IRQ-059, TP-IRQ-061, TP-IRQ-062, TP-IRQ-065, TP-IRQ-071, TP-IRQ-074

### CG-IRQ-002: gen_cg_irq_priority
- Features: F-IRQ-009, F-IRQ-010, F-IRQ-011, F-IRQ-026, F-IRQ-034, F-IRQ-041, F-IRQ-063
- Sample: the decision cycle of an interrupt (Conventions: N located from the pipeline state, C-13; lines from the pin monitor at N, not rvfi_ext_pre_mip, which is captured when ID first empties and may precede the WB drain, rtl/ibex_core.sv:1949-1957); condition: popcount(pins_at_N & mie) + irq_nm_i + internal-NMI-pending >= 2; anti-vacuity: single-line entries do not sample, so a hit proves a real arbitration between at least two takeable sources.
- Coverpoints:
  - cp_set = which sources contended: bins fast_fast{>= 2 fast lines}, fast_external, fast_software, fast_timer, external_software, external_timer, software_timer, nmi_fast, nmi_external, nmi_software, nmi_timer, nmi_ext_nmi_int, three_plus{>= 3 distinct classes}, all18{all NUM_IRQ_LINES = $bits(irqs_t.irq_fast) + 3 lines pending and enabled}
  - cp_winner = cause taken: bins nmi_ext, nmi_int, fast, external, software, timer
  - cp_fast_gap iff (cp_set == fast_fast) = the two lowest pending fast indices: bins adjacent{differ by 1}, far{differ by >= 2}, ends{0 and $bits(irqs_t.irq_fast) - 1}
  - cp_late = line change between the decision cycle and the IRQ_TAKEN cycle: bins none, higher_added, lower_added
  - cp_drain iff (an all18 drain sequence is in progress) = position within the drain: bins first, middle, last18{entry number NUM_IRQ_LINES}
- Crosses:
  - cr_set_winner = cp_set x cp_winner: bins {fast_fast_fast, fast_external_fast, fast_software_fast, fast_timer_fast, external_software_external, external_timer_external, software_timer_software, nmi_fast_nmi_ext, nmi_external_nmi_ext, nmi_software_nmi_ext, nmi_timer_nmi_ext, nmi_ext_nmi_int_nmi_ext, three_plus_fast, three_plus_external, all18_fast}; ignore the remaining combinations: the winner is fixed by the RTL order; a mismatch is a gen_chk_irq failure
  - cr_late_winner = cp_late x cp_winner: bins {higher_added_fast, higher_added_nmi_ext, higher_added_external, lower_added_external, lower_added_software, lower_added_fast, none_fast, none_external}
  - cr_gap_winner = cp_fast_gap x cp_winner: bins {adjacent_fast, far_fast, ends_fast}; ignore any gap x non-fast winner: with >= 2 fast lines pending a fast line wins unless an NMI is present (nmi_* sets are not fast_fast)
  - cr_drain_winner = cp_drain x cp_winner: bins {first_fast, middle_fast, middle_external, middle_software, last18_timer}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-014, TP-IRQ-015, TP-IRQ-016, TP-IRQ-031, TP-IRQ-038, TP-IRQ-045, TP-IRQ-065, TP-IRQ-071, TP-IRQ-073

### CG-IRQ-003: gen_cg_irq_pending_model
- Features: F-IRQ-003, F-IRQ-004, F-IRQ-005, F-IRQ-006, F-IRQ-007, F-IRQ-060
- Sample: ev_edge = a cycle in which any irq pin changes or a retired write to mie commits (irq monitor + CSR model); ev_access = a retired csrr mip / csrrw-csrrs-csrrc mip / csrr mie / csrw-csrs-csrc mie; ev_mie = a retired mstatus write or mret that changes mstatus.MIE (CSR model), with irq_pending_o sampled in the commit cycle; condition: an edge, an access or an MIE change; anti-vacuity: quiescent cycles do not sample, so a hit proves an edge, an access or a global-enable change was compared against the irq_pending_o / mip model.
- Coverpoints:
  - cp_transition iff ev_edge = irq_pending_o model transition: bins rise_enabled{pin 0 -> 1 with its mie bit set: irq_pending_o 0 -> 1}, rise_disabled{pin rise with the mie bit clear: stays 0}, rise_enabled_other_high{pin rise while irq_pending_o already 1}, fall_last{last enabled pin drops: 1 -> 0}, fall_not_last, mie_set_pin_high{mie write enables an already-high pin: 0 -> 1}, mie_clear_pin_high{mie write disables a pending line}, nmi_only_rise{irq_nm_i rises alone: irq_pending_o unchanged}
  - cp_state = core state at the edge: bins mie0_m, mie1_m, u_mode, debug_mode, nmi_mode, step, sleep
  - cp_line_kind iff ev_edge = line class (pin monitor): bins software, timer, external, fast_low{index < $bits(irqs_t.irq_fast)/3}, fast_mid{$bits(irqs_t.irq_fast)/3 <= index < 2*$bits(irqs_t.irq_fast)/3}, fast_high{index >= 2*$bits(irqs_t.irq_fast)/3}
  - cp_mip_access iff ev_access = mip access class (rvfi_insn): bins read_mie0_pins_high{csrr mip with mie = 0 and >= 1 pin high}, read_partial_mie{some pins enabled, some not}, read_all_low, write_csrrw_ignored, write_csrrs_ignored, write_csrrc_ignored
  - cp_mie_write iff (ev_access && the access is a write to mie) = mie write value class (rvfi_rs1_rdata): bins all_ones{wdata 32'hFFFFFFFF reads MIE_WARL_MASK}, zero{wdata 0}, random_masked{wdata & ~MIE_WARL_MASK != 0: those bits read 0}, fast_only{wdata & MIE_WARL_MASK confined to [CSR_MFIX_BIT_HIGH:CSR_MFIX_BIT_LOW]}
  - cp_mie_global_edge iff ev_mie = mstatus.MIE edge with the pending state (S-12): bins set_pending{MIE 0 -> 1 by csrs/csrw mstatus in M-mode with irq_pending_o == 1: the entry follows before the next retirement}, clear_pending{MIE 1 -> 0 by csrc/csrw mstatus with irq_pending_o == 1: no entry while MIE stays 0 in M-mode}, set_idle{MIE 0 -> 1 with irq_pending_o == 0}, clear_idle{MIE 1 -> 0 with irq_pending_o == 0}, mret_mpie1_pending{mret restores MIE 0 -> 1 (MPIE = 1, MPP = M) with irq_pending_o == 1: entry before the target retires}, mret_mpie0_pending{mret keeps MIE 0 (MPIE = 0, MPP = M) with irq_pending_o == 1: no entry}
- Crosses:
  - cr_transition_state = cp_transition x cp_state: bins {rise_enabled_mie0_m, rise_enabled_mie1_m, rise_enabled_u_mode, rise_enabled_debug_mode, rise_enabled_nmi_mode, rise_enabled_step, rise_enabled_sleep, fall_last_mie0_m, fall_last_mie1_m, fall_last_debug_mode, mie_clear_pin_high_mie1_m, mie_set_pin_high_mie0_m, mie_set_pin_high_mie1_m, nmi_only_rise_mie1_m, nmi_only_rise_sleep, rise_disabled_mie1_m, rise_disabled_sleep}; ignore fall_last/fall_not_last/rise_enabled_other_high x sleep: irq_pending_o == 1 ends the sleep in the same cycle (rtl/ibex_controller.sv:615), so a pending line never persists in the sleep state; ignore mie_set_pin_high/mie_clear_pin_high x sleep: no CSR write retires while asleep
  - cr_transition_line = cp_transition x cp_line_kind: bins {rise_enabled_software, rise_enabled_timer, rise_enabled_external, rise_enabled_fast_low, rise_enabled_fast_mid, rise_enabled_fast_high, fall_last_software, fall_last_timer, fall_last_external, fall_last_fast_low, fall_last_fast_high, rise_disabled_fast_mid, mie_clear_pin_high_external}
  - cr_access_state = cp_mip_access x cp_state: bins {read_mie0_pins_high_mie0_m, read_partial_mie_mie1_m, read_all_low_mie1_m, write_csrrw_ignored_mie1_m, write_csrrs_ignored_mie0_m, write_csrrc_ignored_mie1_m}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-007, TP-IRQ-008, TP-IRQ-009, TP-IRQ-010, TP-IRQ-011, TP-IRQ-012, TP-IRQ-037, TP-IRQ-043, TP-IRQ-063, TP-IRQ-064, TP-IRQ-070, TP-IRQ-071, TP-IRQ-075, TP-IRQ-077, TP-IRQ-078

### CG-IRQ-004: gen_cg_irq_timing
- Features: F-IRQ-016, F-IRQ-017, F-IRQ-018, F-IRQ-019, F-IRQ-020, F-IRQ-021, F-IRQ-022, F-IRQ-023,
  F-IRQ-024, F-IRQ-025, F-IRQ-026, F-IRQ-059, F-IRQ-060, F-IRQ-064, F-EXC-035, F-IRQ-045 (parent of
  folded bins hosted here)
- Sample: the first cycle in which an interrupt request becomes takeable (irq monitor: a line pending-and-enabled with MIE or U-mode, or irq_nm rising, outside debug/step/nmi_mode), classified by the pipeline situation of that cycle from the dbus/ibus/RVFI monitors and the program listing (ID occupancy from ibus delivery + the fixed IF->ID offset requires cpuctrlsts.icache_enable = 0, else from RVFI back-dated by one cycle, S-4); the outcome is recorded at the decision cycle N / IRQ_TAKEN N + 1 (Conventions) or at the request's abandonment; condition: one sample per request; anti-vacuity: idle cycles never sample, so a hit proves a request arrived in the named context and its outcome was compared.
- Coverpoints:
  - cp_ctx = pipeline situation at arrival: bins id_empty, id_alu, id_branch, id_jump, id_load_wait{load waiting for data_rvalid_i}, id_store_wait, id_div, id_mul, id_csr_flush{csr write not touching mie/mstatus/mtvec}, id_csr_enable{csrs mstatus.MIE or csrw/csrs mie enabling this line}, id_csr_disable{write masking this line}, id_csr_mtvec, id_mret, id_dret, id_wfi, id_exc{ecall/ebreak/illegal/fetch-error in ID}, wb_fault_same_cycle{data_err_i response this cycle}, zcmp_expanded, zcmp_commit, first_fetch_wake{FIRST_FETCH after a WFI wake}, reset_release, fetch_stall_gnt{ibus request waiting for gnt}, fetch_stall_rvalid
  - cp_rvalid_relation iff (cp_ctx in {id_load_wait, id_store_wait}) = pin rise relative to the access's data_rvalid_i: bins same_cycle_as_rvalid, before_rvalid, after_rvalid
  - cp_outcome = observed outcome: bins taken, withdrawn{line dropped before IRQ_TAKEN: no trap}, masked_by_write{csr write disabled it first}, deferred_by_exception, taken_other_line
  - cp_latency = cycles from the sample to instr_req_o at the vector: bins two{2}, three_five{[3:5]}, six_ten{[6:10]}, long{[11:$]}
  - cp_pulse_width = cycles the winning line stayed high (pin monitor): bins one{1}, two{2}, three_plus{[3:$], dropped by the driver before any ack}, level_until_ack{held until the handler's ack}
  - cp_change_before_taken = line change between the decision cycle N and IRQ_TAKEN N + 1 (pin monitor): bins stable{same enabled set}, dropped_all{no takeable source left at N + 1}, dropped_winner_other_remains{the N winner is low at N + 1, a lower line remains}, higher_added{a higher-priority line is high at N + 1}, lower_added{a lower-priority line is added at N + 1}
  - cp_records_to_entry iff (cp_outcome in {taken, taken_other_line}) = ordinary records retired between the request's arrival cycle and the entry (RVFI; the instruction in ID at the arrival completes first and, in the RVALID-wait context, so does the successor already in ID, C-3 / X-7, rtl/ibex_controller.sv:296, 700-713): bins zero{0}, one{1}, two{2}, three_plus{[3:GEN_IRQ_ENTRY_BOUND_RECORDS]: a Zcmp sequence in ID at the arrival}
- Crosses:
  - cr_ctx_outcome = cp_ctx x cp_outcome: bins {id_empty_taken, id_alu_taken, id_branch_taken, id_jump_taken, id_load_wait_taken, id_store_wait_taken, id_div_taken, id_mul_taken, id_csr_flush_taken, id_csr_enable_taken, id_csr_disable_masked_by_write, id_csr_mtvec_taken, id_mret_taken, id_dret_taken, id_wfi_taken, id_exc_deferred_by_exception, wb_fault_same_cycle_deferred_by_exception, zcmp_expanded_taken, zcmp_commit_taken, first_fetch_wake_taken, reset_release_taken, fetch_stall_gnt_taken, fetch_stall_rvalid_taken, id_empty_withdrawn, id_load_wait_withdrawn, id_empty_taken_other_line, id_div_withdrawn}; ignore id_exc/wb_fault_same_cycle x taken/taken_other_line/withdrawn/masked_by_write: an exception present at the decision wins by definition (deferred_by_exception); ignore id_csr_disable x taken: the write masks the line (masked_by_write, or taken_other_line for another line)
  - cr_ctx_records = cp_ctx x cp_records_to_entry: bins {id_empty_zero, id_alu_one, id_load_wait_one, id_load_wait_two, id_store_wait_one, id_store_wait_two, fetch_stall_gnt_zero, fetch_stall_rvalid_zero, zcmp_expanded_three_plus}; ignore id_empty x one/two/three_plus: nothing in ID or WB completes; ignore id_load_wait/id_store_wait x zero: the access in WB retires first; ignore id_alu/id_branch/id_jump/id_div/id_mul/id_csr_*/id_mret/id_dret/id_wfi x two/three_plus: one instruction in ID, the successor is blocked by halt_if
  - cr_ctx_rvalid = cp_ctx x cp_rvalid_relation: bins {id_load_wait_same_cycle_as_rvalid, id_load_wait_before_rvalid, id_load_wait_after_rvalid, id_store_wait_same_cycle_as_rvalid, id_store_wait_before_rvalid}
  - cr_ctx_latency = cp_ctx x cp_latency: bins {id_empty_two, id_load_wait_three_five, id_load_wait_six_ten, id_load_wait_long, id_div_long, id_div_six_ten, zcmp_expanded_three_five, zcmp_commit_six_ten, fetch_stall_rvalid_long, first_fetch_wake_two, id_mret_two, id_mret_three_five}
  - cr_pulse_change_outcome = cp_pulse_width x cp_change_before_taken x cp_outcome: bins {one_dropped_all_withdrawn, two_dropped_all_withdrawn, two_stable_taken, level_until_ack_stable_taken, three_plus_higher_added_taken_other_line, three_plus_lower_added_taken, three_plus_dropped_winner_other_remains_taken_other_line, three_plus_stable_taken} (two_dropped_all_withdrawn: the pulse's second cycle is the decision cycle, an instruction occupied ID during its first; two_stable_taken: the pulse's first cycle is the decision cycle, high at N + 1); ignore one x stable/higher_added/lower_added: a one-cycle pulse is low in IRQ_TAKEN (CTRL-09), so it is never stable and never taken; ignore level_until_ack x dropped_all/dropped_winner_other_remains: a level held until the ack cannot drop before IRQ_TAKEN; ignore dropped_all x taken/taken_other_line/masked_by_write and stable x withdrawn/taken_other_line and dropped_winner_other_remains x taken/withdrawn and higher_added x taken: the outcome is fixed by the N + 1 line set (CTRL-09)
- Adopted (riscv-dv): none
- TP items: TP-IRQ-012, TP-IRQ-020, TP-IRQ-021, TP-IRQ-022, TP-IRQ-023, TP-IRQ-024, TP-IRQ-025, TP-IRQ-026, TP-IRQ-027, TP-IRQ-028, TP-IRQ-029, TP-IRQ-030, TP-IRQ-031, TP-IRQ-032, TP-IRQ-049, TP-IRQ-059, TP-IRQ-063, TP-IRQ-064, TP-IRQ-066, TP-IRQ-071, TP-IRQ-072, TP-IRQ-076, TP-IRQ-077

### CG-IRQ-005: gen_cg_irq_handler_flow
- Features: F-IRQ-015, F-IRQ-023, F-IRQ-027, F-IRQ-028, F-IRQ-029, F-IRQ-016, F-IRQ-012 (parent of
  folded bins hosted here)
- Sample: a retired mret whose matching entry was an interrupt (handler return), and each nested interrupt entry (entry depth >= 2 in the gen_chk_irq entry/return stack); condition: handler return or nested entry; anti-vacuity: only handler returns and nested entries sample, so a hit proves the re-trap / nesting behaviour was exercised.
- Coverpoints:
  - cp_line_at_mret = state of the serviced line at the mret: bins still_high_same, dropped_by_ack, dropped_new_other_pending, masked_in_handler{handler cleared its mie bit while the line stays high}
  - cp_reentry = re-entry distance after the mret (RVFI): bins immediate{0 instructions retired before the next vector}, later, none
  - cp_nesting = depth reached: bins depth1, depth2_same_prio, depth2_lower{nested by a lower-priority line after MIE re-enable}, depth2_higher, depth3_plus
  - cp_mtvec_in_handler = mtvec rewritten inside the handler (CSR model): bins unchanged, rewritten
  - cp_mpp_restored = privilege the mret returns to: bins m, u
- Crosses:
  - cr_state_reentry = cp_line_at_mret x cp_reentry: bins {still_high_same_immediate, dropped_by_ack_none, dropped_by_ack_later, dropped_new_other_pending_immediate, masked_in_handler_none, masked_in_handler_later}
  - cr_nesting_mtvec = cp_nesting x cp_mtvec_in_handler: bins {depth1_unchanged, depth2_lower_unchanged, depth2_higher_unchanged, depth2_same_prio_unchanged, depth3_plus_unchanged, depth1_rewritten, depth2_same_prio_rewritten}
  - cr_state_mpp = cp_line_at_mret x cp_mpp_restored: bins {still_high_same_u, still_high_same_m, dropped_new_other_pending_u, dropped_by_ack_u, dropped_by_ack_m}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-020, TP-IRQ-028, TP-IRQ-032, TP-IRQ-033, TP-IRQ-034, TP-IRQ-071, TP-IRQ-077

### CG-IRQ-006: gen_cg_irq_vector
- Features: F-IRQ-012, F-IRQ-013, F-IRQ-014, F-IRQ-015, F-IRQ-061, F-IRQ-062
- Sample: ev_entry = interrupt entry (first handler pc from rvfi_pc_rdata with rvfi_intr / ibus monitor); ev_mtvec = retired csrw/csrs/csrc mtvec plus the first csrr mtvec after reset; condition: entry or mtvec access; anti-vacuity: samples only on entries and mtvec accesses, so a hit proves the vector arithmetic or the WARL rule was exercised for that id/base class.
- Coverpoints:
  - cp_id iff ev_entry = interrupt id: bins id3{3}, id7{7}, id11{11}, fast[15]{[16:30]}, id31_ext{31, external NMI}, id31_int{internal NMI, vector forced to 31}
  - cp_base_class = mtvec base in force: bins boot_init, sw_aligned, sw_legalised, upper_half{base[31] == 1}
  - cp_mtvec_wdata iff ev_mtvec = value class of a software write (rvfi_rs1_rdata) or the reset read-back: bins mode00, mode01, mode1x{10, 11}, base_low_nonzero{wdata[7:2] != 0}, boot_readback{first csrr mtvec == {boot_addr[31:8], 8'h01}}
- Crosses:
  - cr_id_base = cp_id x cp_base_class: bins {id3_boot_init, id3_sw_aligned, id3_sw_legalised, id3_upper_half, id7_boot_init, id7_sw_legalised, id11_sw_aligned, id11_upper_half, fast_0_boot_init, fast_0_sw_legalised, fast_14_sw_aligned, fast_14_upper_half, fast_7_sw_aligned, id31_ext_boot_init, id31_ext_sw_legalised, id31_ext_upper_half, id31_int_sw_aligned, id31_int_boot_init, id7_sw_aligned, id11_boot_init}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-001, TP-IRQ-002, TP-IRQ-003, TP-IRQ-004, TP-IRQ-005, TP-IRQ-006, TP-IRQ-007, TP-IRQ-017, TP-IRQ-018, TP-IRQ-019, TP-IRQ-071

### CG-IRQ-007: gen_cg_irq_nmi
- Features: F-IRQ-030, F-IRQ-031, F-IRQ-032, F-IRQ-033, F-IRQ-034, F-IRQ-035, F-IRQ-036, F-IRQ-038, F-IRQ-043, F-IRQ-049, F-IRQ-055, F-IRQ-066
- Sample: ev_entry = an NMI entry (rvfi_ext_nmi or rvfi_ext_nmi_int captured; mcause read-back {1'b1, ExcCauseIrqNm.lower_cause} = 32'h8000001F or {2'b11, NMI_INT_CAUSE_ECC} = 32'hFFFFFFE0); ev_mret = each mret that exits NMI mode (gen_chk_nmi model); condition: NMI event; anti-vacuity: only NMI entries/exits sample, so a hit proves an NMI was taken from the recorded context and its return compared.
- Coverpoints:
  - cp_source iff ev_entry = NMI source: bins ext{irq_nm_i}, int_ecc{internal integrity-error NMI}, both_same_cycle{irq_nm_i high with the internal flag set at the decision}
  - cp_ctx_pre iff ev_entry = what was running before the NMI: bins user_code, exc_handler, irq_handler, exc_vector_first{NMI taken at the exception vector before its first instruction: mepc == mtvec base}, wfi_sleep, reset_release, dret_exit, after_mret_still_high{re-entry right after the NMI handler's mret}
  - cp_mie_pre iff ev_entry = mstatus.MIE before the NMI (CSR model): bins mie0, mie1
  - cp_priv_pre iff ev_entry = privilege before the entry (rvfi_mode / CSR model): bins m, u
  - cp_in_handler iff ev_mret = what happened inside the NMI handler: bins none, nmi_reasserted_ignored, irq_enabled_masked{handler set MIE = 1 with a line pending: not taken}, exc_taken, int_err_pending{integrity error inside the handler}, regular_irq_pending_taken_after_mret, debug_session_nmi_mode_kept{debug entry (debug_req_i / step) and dret inside the NMI handler: pending mip & mie lines and a re-asserted irq_nm_i stay masked until the handler's mret (F-IRQ-066, H-N1)}, debug_session_then_mret_taken{after such a debug session the handler's mret is followed directly by the masked source's entry (regular cause or 32'h8000001F) with no retirement at the mret target (F-IRQ-066)}
  - cp_mstack iff ev_mret = mstack restore outcome at the exiting mret: bins restore_ok, sw_epc_write_discarded{handler wrote mcause (or mepc) with junk; the post-mret read-back is the stacked value}, sw_epc_target_used{handler wrote mepc with a valid address T: the mret jumps to T (the CURRENT mepc_q, rtl/ibex_if_stage.sv:246, rtl/ibex_controller.sv:954-957) while the post-mret mepc/mcause read-back is the stacked value (rtl/ibex_cs_registers.sv:967-975); fact-check Section 5 RTL-defined behaviour}, nested_exc_context_lost{exception inside the handler overwrote mstack}
  - cp_mepc_align: RETIRED (S-7 single owner): CG-EXC-012.cp_mepc_bit1 (nmi_ext/nmi_int bins in cr_kind_bit1)
- Crosses:
  - cr_source_ctx = cp_source x cp_ctx_pre: bins {ext_user_code, ext_exc_handler, ext_irq_handler, ext_wfi_sleep, ext_reset_release, ext_dret_exit, ext_after_mret_still_high, int_ecc_user_code, int_ecc_exc_handler, int_ecc_irq_handler, int_ecc_after_mret_still_high, ext_exc_vector_first, int_ecc_exc_vector_first, both_same_cycle_user_code, both_same_cycle_exc_handler}; ignore int_ecc/both_same_cycle x wfi_sleep/reset_release: no data access completes in sleep or before the first instruction
  - cr_ctx_priv_mie = cp_ctx_pre x cp_priv_pre x cp_mie_pre: bins {user_code_m_mie0, user_code_m_mie1, user_code_u_mie0, user_code_u_mie1, exc_handler_m_mie0, irq_handler_m_mie0, wfi_sleep_m_mie0, wfi_sleep_u_mie1, dret_exit_u_mie0, after_mret_still_high_m_mie1}; ignore exc_handler/irq_handler/exc_vector_first/reset_release x u: handlers, the vector and reset run in M-mode; ignore reset_release x mie1: mstatus.MIE resets to 0; ignore irq_handler x mie1: interrupt entry clears MIE (a handler that re-enables MIE is exc_handler-like nesting, counted under user_code by the gen_chk_irq stack only when the handler has returned)
  - cr_handler_mstack = cp_in_handler x cp_mstack: bins {none_restore_ok, none_sw_epc_write_discarded, exc_taken_nested_exc_context_lost, irq_enabled_masked_restore_ok, nmi_reasserted_ignored_restore_ok, int_err_pending_restore_ok, regular_irq_pending_taken_after_mret_restore_ok, debug_session_nmi_mode_kept_restore_ok, debug_session_then_mret_taken_restore_ok}; ignore exc_taken x restore_ok/sw_epc_write_discarded: a nested trap overwrites the single-entry mstack (F-IRQ-036); ignore cp_in_handler != exc_taken x nested_exc_context_lost: no nested trap, no loss
  - cr_source_align: RETIRED (S-7): see CG-EXC-012.cr_kind_bit1 (nmi_ext_bit1_*, nmi_int_bit1_1)
- Adopted (riscv-dv): none
- TP items: TP-IRQ-007, TP-IRQ-019, TP-IRQ-035, TP-IRQ-036, TP-IRQ-037, TP-IRQ-039, TP-IRQ-040, TP-IRQ-042, TP-IRQ-044, TP-IRQ-045, TP-IRQ-047, TP-IRQ-053, TP-IRQ-059, TP-IRQ-073, TP-IRQ-078

### CG-IRQ-008: gen_cg_irq_nmi_int
- Features: F-IRQ-040, F-IRQ-041, F-IRQ-042, F-IRQ-043, F-IRQ-044
- Sample: ev_inj = a dbus-agent integrity-error injection (corrupted data_rdata_intg_i on a load or store response) tracked by gen_chk_bus_intg_rsp to its alert and NMI; ev_mcause = a retired write to mcause; condition: injection or mcause write; anti-vacuity: injections happen only under knob:dmem_err_rate != none or a directed injection, so a hit proves an injected error was followed to its consequences.
- Coverpoints:
  - cp_err_op iff ev_inj = access kind of the corrupted response (dbus monitor): bins load, store
  - cp_err_half iff ev_inj = which part of the access carried the error (dbus monitor): bins aligned, mis_first, mis_second
  - cp_taken_after iff ev_inj = ordinary instructions retired between the error response and the internal-NMI entry (a Zcmp sequence counts as one instruction; its micro-op records are folded): bins zero{0}, one{1}, two{2: the pending flag registers one cycle after rvalid, so the instruction in ID completes and the one accepted into ID in the response cycle completes too, rtl/ibex_controller.sv:404-430, 436, 700-713; C-7 / X-10, doc mismatch D21}, three_plus{[3:$]: reachable only while the internal NMI is masked, i.e. the error arrives in debug mode or in nmi_mode and the entry waits for the dret/mret (rtl/ibex_controller.sv:498)}; outside the masked contexts gen_chk_bus_intg_rsp bounds the count to two (the first directed integrity-error sim confirms, inventory UNVERIFIED-4)
  - cp_pending_ctx iff ev_inj = state when the error arrived: bins idle, second_err_while_pending, ext_nmi_same_cycle, in_nmi_handler, in_debug_mode, in_irq_handler
  - cp_effects iff ev_inj = side effects observed (alert monitor, RVFI, read-back): bins alert_pulse{alert_major_bus_o in the error cycle}, rf_wr_suppressed{rvfi_ext_rf_wr_suppress on the load: aligned access or misaligned with the error on the SECOND beat; a misaligned load with the error on the FIRST beat writes rd (rtl/ibex_load_store_unit.sv:514, 697-698; X-11, B16, owner TP-DMEM-041), so the bin is not required for that class}, store_no_rf, mtval_first_addr{after second_err_while_pending: mtval == first error address}
  - cp_mcause_write iff ev_mcause = software mcause write class (rvfi_rs1_rdata vs read-back): bins c000xx_reads_ffffffe0, w8000xx_reads_same, w4000xx_reads_code{wdata[31:30] == 2'b01 sets neither flag: reads {27'b0, code} (rtl/ibex_cs_registers.sv:731-733, X-23)}, w20_reads_0, bits29_5_dropped
- Crosses:
  - cr_op_half = cp_err_op x cp_err_half: bins {load_aligned, load_mis_first, load_mis_second, store_aligned, store_mis_first, store_mis_second}
  - cr_op_ctx = cp_err_op x cp_pending_ctx: bins {load_idle, load_second_err_while_pending, load_ext_nmi_same_cycle, load_in_nmi_handler, load_in_debug_mode, load_in_irq_handler, store_idle, store_second_err_while_pending, store_in_nmi_handler, store_ext_nmi_same_cycle, store_in_debug_mode}
  - cr_ctx_taken = cp_pending_ctx x cp_taken_after: bins {idle_zero, idle_one, idle_two, in_irq_handler_zero, in_irq_handler_one, in_irq_handler_two, in_nmi_handler_three_plus, in_debug_mode_three_plus}; ignore idle/second_err_while_pending/ext_nmi_same_cycle/in_irq_handler x three_plus: at most two ordinary instructions outside the masked contexts (checker bound, C-7 / D21); ignore in_nmi_handler/in_debug_mode x zero: the entry waits for the mret/dret, which itself retires
  - cr_op_effects = cp_err_op x cp_effects: bins {load_alert_pulse, load_rf_wr_suppressed, store_alert_pulse, store_store_no_rf, load_mtval_first_addr, store_mtval_first_addr}
- Adopted (riscv-dv): none
- TP items: TP-IRQ-042, TP-IRQ-044, TP-IRQ-045, TP-IRQ-046, TP-IRQ-047, TP-IRQ-048, TP-IRQ-073, TP-IRQ-075

### CG-IRQ-009: gen_cg_irq_wfi
- Features: F-IRQ-045, F-IRQ-046, F-IRQ-047, F-IRQ-048, F-IRQ-049, F-IRQ-050, F-IRQ-051, F-IRQ-052, F-IRQ-053, F-IRQ-054, F-IRQ-064, F-EXC-011
- Sample: retirement of WFI (rvfi_insn == 32'h10500073) or its illegal-instruction trap record, with the gen_chk_sleep bookkeeping (core_busy_o values, instr_req_o gap length, wake source from the irq/debug pin monitor, mcycle read-back); condition: wfi in rvfi_insn; every coverpoint except cp_priv_tw and cp_wb_at_wfi is guarded iff rvfi_trap == 0 (the u_tw1 trap never sleeps); anti-vacuity: only WFI instructions sample, so a hit proves a sleep (or nop/trap path) with the recorded wake source.
- Coverpoints:
  - cp_priv_tw = privilege and mstatus.TW: bins m, u_tw0, u_tw1{illegal instruction}
  - cp_wake = what ended the sleep: bins irq_taken, irq_local_only{mie set, MIE 0, M-mode: resume without trap}, nmi_ext, nmi_int, debug_req, debug_req_and_irq{both present: debug wins}, in_debug_nop, step_nop, already_pending{wake condition true at the wfi}, masked_line_held{inside a handler with the serviced line still high}, none_long{slept >= 100 cycles before a wake}
  - cp_sleep_cycles = cycles with instr_req_o low: bins passthrough{[0:2]}, short{[3:10]}, medium{[11:100]}, long{[101:$]}
  - cp_disabled_high = a mie-disabled line was high during the sleep without waking: bins yes, no
  - cp_busy_off = core_busy_o == IbexMuBiOff observed during the wfi: bins off_seen, off_not_seen{On throughout: an instruction-bus beat outstanding, an icache invalidation active or the LSU busy in WAIT_SLEEP/SLEEP keeps if_busy/lsu_busy high (gen_tb_architecture.md 8.2 item 1; a WFI within 256 cycles of reset)}
  - cp_wb_at_wfi = WB content when the wfi reached ID: bins empty, ls_ok, ls_fault{fault wins, wfi discarded}
  - cp_mcycle = mcycle read-back across the sleep: bins counted_through_sleep{mcycle delta across the sleep == sleep cycles + fixed overhead}, no_sleep
  - cp_wake_line iff (cp_wake in {irq_taken, irq_local_only, already_pending, masked_line_held, nmi_ext}) = line that woke the core (pin monitor): bins software, timer, external, fast, nmi
- Crosses:
  - cr_priv_wake = cp_priv_tw x cp_wake: bins {m_irq_taken, m_irq_local_only, m_nmi_ext, m_nmi_int, m_debug_req, m_debug_req_and_irq, m_in_debug_nop, m_step_nop, m_already_pending, m_masked_line_held, m_none_long, u_tw0_irq_taken, u_tw0_nmi_ext, u_tw0_debug_req, u_tw0_none_long, u_tw0_already_pending}; ignore u_tw1 x any wake: it traps and never sleeps; ignore u_tw0 x irq_local_only: U-mode ignores MIE, so a locally enabled line is taken
  - cr_wake_sleep = cp_wake x cp_sleep_cycles: bins {irq_taken_passthrough, irq_taken_short, irq_taken_medium, irq_taken_long, already_pending_passthrough, in_debug_nop_passthrough, step_nop_passthrough, nmi_ext_medium, nmi_ext_short, debug_req_medium, irq_local_only_short, irq_local_only_medium, none_long_medium, none_long_long}; ignore in_debug_nop/step_nop/already_pending x short/medium/long: nop and pass-through paths never sleep; ignore none_long x passthrough/short: none_long is >= 100 cycles by definition
  - cr_wake_busy = cp_wake x cp_busy_off: bins {irq_taken_off_seen, none_long_off_seen, in_debug_nop_off_seen, step_nop_off_not_seen, already_pending_off_seen, already_pending_off_not_seen, irq_local_only_off_seen}; ignore step_nop x off_seen: the stepped WFI goes FLUSH -> DBG_TAKEN_IF and never reaches WAIT_SLEEP (F-IRQ-051), so core_busy_o never dips
  - cr_wb_priv = cp_wb_at_wfi x cp_priv_tw: bins {empty_m, ls_ok_m, ls_fault_m, ls_fault_u_tw0, empty_u_tw0}
  - cr_disabled_wake = cp_disabled_high x cp_wake: bins {yes_none_long, yes_nmi_ext, yes_debug_req, yes_irq_taken}
  - cr_wake_line = cp_wake x cp_wake_line: bins {irq_taken_software, irq_taken_timer, irq_taken_external, irq_taken_fast, irq_local_only_software, irq_local_only_fast, nmi_ext_nmi}; ignore irq_taken/irq_local_only/masked_line_held x nmi and nmi_ext x non-nmi: the wake class names the line kind (cp_wake_line is undefined for debug/nop/none_long wakes via its iff)
  - cr_wake_mcycle = cp_wake x cp_mcycle: bins {irq_taken_counted_through_sleep, none_long_counted_through_sleep, in_debug_nop_no_sleep}; ignore irq_taken/irq_local_only/nmi_*/debug_req*/none_long/masked_line_held x no_sleep and in_debug_nop/step_nop/already_pending x counted_through_sleep: the sleep class is fixed by the wake kind
- Adopted (riscv-dv): none
- TP items: TP-EXC-010, TP-IRQ-049, TP-IRQ-050, TP-IRQ-051, TP-IRQ-052, TP-IRQ-053, TP-IRQ-054, TP-IRQ-055, TP-IRQ-056, TP-IRQ-057, TP-IRQ-058, TP-IRQ-066, TP-IRQ-068, TP-IRQ-069, TP-IRQ-074

### CG-IRQ-010: gen_cg_irq_debug_interplay
- Features: F-IRQ-024, F-IRQ-037, F-IRQ-038, F-IRQ-039, F-IRQ-050, F-IRQ-051, F-IRQ-066, F-IRQ-030
  (parent of folded bins hosted here)
- Sample: an interrupt/NMI line pending-and-enabled while rvfi_ext_debug_mode == 1, or while dcsr.step == 1 outside debug mode, and each dret retirement with a pending line; for cp_mode.debug_in_nmi_handler the window is a debug session opened while the gen_chk_nmi model has nmi_mode set (entry after a base + 0x7C vector fetch and before the matching mret); condition: a line asserted inside such a window; anti-vacuity: samples only in debug/step windows with a line asserted, so a hit proves the masking and the post-exit behaviour were exercised.
- Coverpoints:
  - cp_line = line class (pin monitor): bins irq, nmi_ext, nmi_int
  - cp_mode = debug or step window (rvfi_ext_debug_mode, CSR model): bins debug_mode, step_outside, debug_in_nmi_handler{debug window opened while nmi_mode is set: the NMI handler is running (F-IRQ-066); post_exit not_taken until the handler's mret}
  - cp_duration = line held or dropped before the exit (pin monitor): bins held_through_exit, dropped_before_exit
  - cp_post_exit = behaviour after the exit (RVFI): bins taken_before_first_insn{entry with no retirement at dpc}, not_taken{>= 1 retirement at/after dpc with the line still asserted and no entry}, taken_after_nmi_mret{debug_in_nmi_handler only: not taken at the dret, taken directly after the NMI handler's mret (F-IRQ-066)}
  - cp_dcsr_prv = dcsr.prv (CSR model): bins m, u
  - cp_nmip_read iff (a csrr dcsr retires in the window) = irq_nm_i at the read: bins read_with_nmi_high, read_with_nmi_low (bit 3 is compared by the B5 owner item TP-DBG-021 only; TP-IRQ-041 masks it)
  - cp_exit_kind iff (the window ended) = how the window ended (RVFI): bins dret, step_complete{stepped instruction retires; debug re-entry}
- Crosses:
  - cr_line_mode_post = cp_line x cp_mode x cp_post_exit: bins {irq_debug_mode_taken_before_first_insn, irq_debug_mode_not_taken, nmi_ext_debug_mode_taken_before_first_insn, nmi_ext_debug_mode_not_taken, nmi_int_debug_mode_taken_before_first_insn, irq_step_outside_not_taken, nmi_ext_step_outside_not_taken, irq_debug_in_nmi_handler_not_taken, nmi_ext_debug_in_nmi_handler_not_taken, irq_debug_in_nmi_handler_taken_after_nmi_mret, nmi_ext_debug_in_nmi_handler_taken_after_nmi_mret}; ignore debug_mode/step_outside x taken_after_nmi_mret: only the nmi_mode window defers past an mret; ignore nmi_int x step_outside/debug_in_nmi_handler x taken_before_first_insn: the internal NMI stays masked until the mret in nmi_mode and a step window re-enters debug first
  - cr_line_prv = cp_line x cp_dcsr_prv: bins {irq_u, irq_m, nmi_ext_u, nmi_ext_m}
  - cr_dur_post = cp_duration x cp_post_exit: bins {held_through_exit_taken_before_first_insn, dropped_before_exit_not_taken}
  - cr_line_exit = cp_line x cp_exit_kind: bins {irq_dret, irq_step_complete, nmi_ext_dret, nmi_ext_step_complete}
  - cr_mode_exit = cp_mode x cp_exit_kind: bins {debug_mode_dret, step_outside_step_complete, debug_in_nmi_handler_dret, debug_in_nmi_handler_step_complete}; ignore debug_mode x step_complete, step_outside x dret: a debug session ends with dret, a step window with the stepped retirement
- Adopted (riscv-dv): none
- TP items: TP-IRQ-029, TP-IRQ-041, TP-IRQ-042, TP-IRQ-043, TP-IRQ-054, TP-IRQ-069, TP-IRQ-075, TP-IRQ-078

### CG-IRQ-011: gen_cg_irq_reset_fetch_en
- Features: F-IRQ-014, F-IRQ-055, F-IRQ-056, F-IRQ-065
- Sample: ev_reset = reset release (first cycle with rst_ni high) with the irq/debug pin state and the first csrr mstatus/mie/mtvec/mip retirements; ev_off = every fetch_enable_i != On window of >= 20 cycles (fetch_enable monitor), with the irq monitor state inside it; condition: one sample per reset and per Off window; anti-vacuity: samples only at reset release and in Off windows, so a hit proves the reset-time / fetch-disabled interrupt path was exercised; none_pending_while_off is a stimulus-qualified control (an Off window occurred with no line), not an always-true witness (S-3b).
- Coverpoints:
  - cp_lines_at_reset iff ev_reset = lines asserted at reset release (pin monitor): bins none, regular_only, nmi_only, nmi_and_regular, debug_and_nmi, debug_and_regular
  - cp_first_event iff ev_reset = first architectural event after reset: bins boot_insn{first retirement at the boot pc}, nmi_before_insn, debug_before_insn
  - cp_reset_reads iff ev_reset = first CSR read-backs after reset: bins mstatus_0x80, mie_0, mtvec_boot_page, mip_reflects_pins
  - cp_boot_mret iff (ev_reset && an mret retires before any trap) = boot-time mret (RVFI): bins to_u_mie1{mret as an early instruction: U-mode, MIE = 1}
  - cp_fetch_off iff ev_off = interrupt situation in the Off window: bins irq_pending_while_off_csr_updated{line pending-and-enabled before the window: entry decided while Off, mepc/mcause change without instr_req_o}, irq_arrives_while_off{line rises inside the window}, nmi_while_off{irq_nm_i rises inside the window}, none_pending_while_off{no line asserted for the whole window}
  - cp_fetch_on_after iff ev_off = first fetch after fetch_enable_i returns to On (ibus monitor): bins handler_fetched_at_on{first instr_req_o after On is the vector}, resume_at_on
- Crosses:
  - cr_lines_first = cp_lines_at_reset x cp_first_event: bins {none_boot_insn, regular_only_boot_insn, nmi_only_nmi_before_insn, nmi_and_regular_nmi_before_insn, debug_and_nmi_debug_before_insn, debug_and_regular_debug_before_insn}; ignore every other combination: the first event is a function of the pin pattern (regular lines are masked at reset, debug beats NMI); a mismatch is a gen_chk_nmi/gen_chk_debug failure
  - cr_off_on = cp_fetch_off x cp_fetch_on_after: bins {irq_pending_while_off_csr_updated_handler_fetched_at_on, nmi_while_off_handler_fetched_at_on, irq_arrives_while_off_handler_fetched_at_on, none_pending_while_off_resume_at_on}; ignore none_pending_while_off x handler_fetched_at_on and irq_*/nmi_while_off x resume_at_on: the first fetch after On is fixed by the pending state (Q-DL-8 default)
- Adopted (riscv-dv): none
- TP items: TP-IRQ-019, TP-IRQ-059, TP-IRQ-060, TP-IRQ-067

### CG-IRQ-012: gen_cg_irq_cross_stall
- Status: RETIRED (Critic pre-review S-10 / S-7). This group sampled the DV_prompt triple (fetch stalled x data error x interrupt pending) on the interrupt decision cycle, not on the coincidence, and duplicated CG-IRQ-004.cp_pulse_width (cp_hold) and the bus-state operands of CG-EXC-013. Owners now: fcov_xcut.md CG-XIF-001.cr_fetch_x_async (boundary triple, same-cycle pin fire-check), CG-EXC-013.cr_wb_irq_ibus / cr_stage_irq (exception side), CG-IRQ-004.cp_ctx fetch_stall_* / id_load_wait / cp_pulse_width (interrupt side), CG-IRQ-002.cp_set (line-set class). No bins; the ID is kept so earlier references resolve.
- Features: none (F-IRQ-017, F-IRQ-018, F-IRQ-022, F-IRQ-025, F-IRQ-027, F-EXC-025, F-EXC-069 are carried by the owners above)
- TP items: none

### CG-IRQ-013: gen_cg_irq_entry_window
- Features: F-IRQ-034, F-IRQ-032, F-IRQ-024, F-IRQ-039, F-IRQ-016
- Sample: a regular interrupt entry decided (the vector fetch on the ibus with cpuctrlsts.icache_enable = 0 pinned by its items, C-14; the rvfi_ext_irq_valid level rising at N + 4 is a secondary confirmation, C-13) that is followed, BEFORE the handler's first retirement, by a second entry: an NMI (next retirement has rvfi_ext_nmi or rvfi_ext_nmi_int with mepc read-back == the interrupt vector) or a debug entry (DmHaltAddr fetch with dpc read-back == the interrupt vector); condition: the preempting source rose between IRQ_TAKEN and the first handler retirement (pin monitor timestamp inside the window; rtl/ibex_core.sv:1949-1957 recaptures for new_debug_req / new_nmi); anti-vacuity: an interrupt entry whose handler retires normally never samples, so a hit proves the IRQ_TAKEN-to-first-retirement window was preempted (S-12 edge).
- Coverpoints:
  - cp_preempt = the preempting source: bins nmi_ext{irq_nm_i}, nmi_int{internal integrity-error NMI from a store response of the interrupted code draining in WB}, debug_req{debug_req_i}
  - cp_window_pos = where in the window the source rose (ibus monitor): bins vector_req_outstanding{vector instr_req_o issued, no rvalid yet}, vector_word_in_if{vector word returned, not yet in ID}
  - cp_line = the preempted interrupt: bins software, timer, external, fast
  - cp_resume = what happens after the preempting handler returns: bins irq_handler_runs{after the NMI's mret / the dret the next retirement is the interrupt vector with rvfi_intr == 0 and mcause read-back still the interrupt cause}, irq_lost_to_second_entry{a second regular entry re-vectors first because the line is still high and MIE was restored}
- Crosses:
  - cr_preempt_pos = cp_preempt x cp_window_pos: bins {nmi_ext_vector_req_outstanding, nmi_ext_vector_word_in_if, debug_req_vector_req_outstanding, debug_req_vector_word_in_if, nmi_int_vector_req_outstanding}
  - cr_preempt_line = cp_preempt x cp_line: bins {nmi_ext_software, nmi_ext_timer, nmi_ext_external, nmi_ext_fast, debug_req_external, debug_req_fast, debug_req_software}
  - cr_preempt_resume = cp_preempt x cp_resume: bins {nmi_ext_irq_handler_runs, debug_req_irq_handler_runs, nmi_ext_irq_lost_to_second_entry}; ignore debug_req x irq_lost_to_second_entry: the dret returns with MIE == 0 (interrupt entry cleared it) and the vector instruction retires first
- Adopted (riscv-dv): none
- TP items: TP-IRQ-079, TP-IRQ-080

## Counts

| metric | count |
|---|---|
| covergroups | 25 active (CG-EXC-001..013, CG-IRQ-001..011, CG-IRQ-013) + 1 RETIRED (CG-IRQ-012, ID kept) |
| coverpoints | 153 (retired coverpoint lines not counted) |
| coverpoint bins | 628 (array bins fast[15] expanded; ignore_bins not counted) |
| crosses | 102 |
| cross bins (required, named) | 868 |
| adopted bins (riscv-dv) | 0 |
| coverpoints owned by no TP item | 0 (fix 3: every coverpoint has >= 1 CSV row) |

Counts are produced by the fix-2 verification script (parses every `cp_`/`cr_` line, drops RETIRED
lines and ignore_bins, expands `name[N]`), which also regenerates trace_tp_bin_exc_irq.csv from the
TP items' Bins lines, so the CSV (1663 rows) and this table agree by construction. Cross bins that are
not named as required still exist in the auto-cross and are reported by urg; only the named ones are
traced. Fix-2 pass (Critic pre-review T-034): S-7 single owners for pc[1]/mepc[1] alignment
(CG-EXC-012) and exception-commit x interrupt state (CG-EXC-013), CG-IRQ-012 retired, CG-IRQ-013 added
(IRQ_TAKEN-window pre-emption), MIE global-edge bins (CG-IRQ-003.cp_mie_global_edge), F-IRQ-066 bins
(CG-IRQ-007 / CG-IRQ-010), cp_taken_after.two_plus (fix 3: split into two / three_plus) made reachable, unreachable-as-written bins turned
into ignore_bins with reasons, per-coverpoint iff guards, impossible cross combinations ignored.
Fix-3 pass (rtl-arch fact-check T-053, round-2 review residual M-6): rvfi_ext_irq_valid level semantics
(C-13; CG-IRQ-001 irq_valid_level / irq_valid_absent, CG-IRQ-002 / CG-IRQ-013 samples, Conventions),
redirect targets from the next record (C-1), exception commit anchored on the trap record with
CG-EXC-013.cp_vector_req_delay (C-14), CG-IRQ-004.cp_records_to_entry / cr_ctx_records (C-3, X-7),
CG-IRQ-008.cp_taken_after zero / one / two / three_plus and idle_two (C-7, D21), cp_effects
rf_wr_suppressed per-beat qualifier (X-11, B16), CG-IRQ-007.cp_mstack.sw_epc_target_used (mret target in
NMI mode), CG-IRQ-008.cp_mcause_write.w4000xx_reads_code (X-23), CG-EXC-006 cp_op / cp_size decoded from
rvfi_insn (X-15), CG-EXC-004 c.ebreak trace form (X-14), CG-EXC-009.cp_target from RVFI with mtvec_base
ignored; the 39 coverpoints owned by no item were given to the items that exercise them (no
"regression-level" coverpoint remains in this file).

## Probe candidates

Target is zero probes; every bin above is sampled from the DUT boundary (instruction/data buses,
irq/debug pins, alerts, core_busy_o, double_fault_seen_o, irq_pending_o, crash_dump_o), from RVFI
(incl. rvfi_ext_*), from handler CSR read-backs, or from checker-model events derived from those.
Items the DV Lead may want to promote to coverage-only probes if the boundary derivation proves
ambiguous in practice:

- CG-IRQ-004 / CG-IRQ-012 decision cycle ("first takeable cycle", IRQ_TAKEN cycle). Boundary
  derivation: pipe-empty inference from the ibus monitor, the dbus monitor and RVFI (the
  rvfi_ext_irq_valid level rises at N + 4 and is absent when ID emptied before WB drained, C-13); the
  one-cycle handshake (decision, then live capture) is inferred from the pin monitor at N and N + 1
  (rvfi_ext_pre_mip is the capture-cycle vector, not the decision-cycle vector). Probe fallback: id_stage_i.controller_i.ctrl_fsm_cs == IRQ_TAKEN (rtl/ibex_controller.sv,
  tb-infra P4, fcov_interrupt_taken hook). Coverage-only; no checker depends on it.
- CG-IRQ-004.cp_ctx zcmp_expanded vs zcmp_commit and CG-EXC-008.cp_op_pos. Boundary derivation:
  rvfi_ext_expanded_insn_valid/last plus the micro-op class implied by the cm.* encoding (rlist)
  and the dbus request count. Probe fallback: if_stage_i instr_gets_expanded (instr_exp_e) --
  coverage-only.
- CG-IRQ-008.cp_pending_ctx.second_err_while_pending. Boundary derivation: a second corrupted
  response observed by the dbus monitor before the first internal-NMI entry (RVFI). Probe fallback:
  id_stage_i.controller_i.mem_resp_intg_err_irq_pending_q (rtl/ibex_controller.sv:394). Not needed
  unless the entry timing makes the ordering ambiguous.
- CG-IRQ-007 nmi_mode context (in_handler bins) and CG-EXC-010 sync_exc_seen state. Boundary
  derivation: gen_chk_nmi / gen_chk_double_fault models built from entries, mrets and cpuctrlsts
  read-backs. Probe fallback: id_stage_i.controller_i.nmi_mode_q and
  cs_registers_i.cpuctrlsts_part_q.sync_exc_seen -- coverage-only, only if the DV Lead wants the
  models cross-checked.
- CG-EXC-013.cp_wb_at_id_exc and CG-EXC-006.cp_younger. Boundary derivation: dbus monitor
  outstanding state plus the program listing (next program-order instruction) and ibus delivery
  timestamps. No probe expected.
- CG-EXC-001.cp_mtvec_class / CG-IRQ-006.cp_base_class. Boundary derivation: CSR model tracking
  retired csrw/csrs/csrc mtvec (rvfi_rs1_rdata) and the boot init from boot_addr_i. No probe.

No bin in this file requires a probe to be samplable; the fallbacks above are listed for the DV
Lead's decision only.


# 3.4 Areas PMP: Physical memory protection and Smepmp (16 regions, G=0)


All covergroups live in the gen_ namespace and are sampled from the boundary (ibus/dbus monitors), RVFI, and the gen_chk_pmp / gen_chk_csr_readback models; no RTL covergroup is extended. Counts and ranges derive from ibex_pkg / ibex_core parameters (PMPNumRegions = 16 and PMPGranularity = 0 in this configuration; bins written as r0..r15 / e0..e15 / a0..a15 are generated over 0..PMPNumRegions-1; the granule is 2^(PMPGranularity+2) bytes; CSR addresses are the ibex_pkg names CSR_PMPCFG0.., CSR_PMPADDR0.., CSR_MSECCFG, CSR_MSECCFGH; reset values PmpCfgRst / PmpAddrRst / PmpMseccfgRst). Wrong-verdict combinations are excluded with ignore_bins and a reason (never `illegal_bins = default sequence`); mseccfg state transitions are enumerated. Truth-table bin descriptions carry the expected verdict; the verdict itself is asserted by gen_chk_pmp, so a wrong-verdict sample fails the run before it could be counted.

Grammar (fix-2, Critic M-02/S-14): every bin is written literally as `name{value or predicate}` on its coverpoint or cross line; `ignore_bins name{combination}: reason` follows the required bins after a semicolon. A coverpoint tagged `[operand-only]` exists only as a cross operand (knob values are owned by fcov_xcut CG-REG, S-5) and a coverpoint or cross tagged `[probe-gated, not in manifest]` is not a must-hit until the probe register carries its probe; neither appears in trace_tp_bin_pmp.csv. The CSV is regenerated from the required (post-ignore) bin set by expanding the `Bins:` patterns of tp_pmp.md, so no manifest can name an ignored or impossible bin (M-03).

Status resolution (Critic v1 fix): Features lines keep the original F-PMP IDs; IDs marked FOLDED in gen_part_pmp.md are carried by the bins their Status line names (all in this file), IDs marked ALIAS resolve to the canonical entry (F-EXC-005/006/035, F-PRV-005/007/015, F-DBG-055, F-CSR-024). F-PMP-087 and F-PMP-095 are canonical for F-EXC-033 and F-DBG-052. Bug candidates B1 (dret keeps MPRV) and B2 (MPRV honoured in debug mode) follow gen_bug_log.md: the checker follows the specification, the carrying items TP-PMP-073/074 are expected-fail and own only bins that encode the observed RTL outcome (CG-PMP-012.cp_mprv_after.dret_u_kept_rtl, CG-PMP-012.cr_dbg_mprv.*_fault); the spec-outcome bins are ignore_bins until the RTL is fixed.

Bin naming: `CG-PMP-nnn.cp_<name>.<bin>` for coverpoint bins and `CG-PMP-nnn.cr_<name>.<bin>` for cross bins. Truth-table cross bins are `c<LRWX>_<priv>_<type>`; no-match bins are `nm_<priv>_<type>_mml<x>_mmwp<y>`.

### CG-PMP-001: gen_cg_pmp_cfg_write
- Features: F-PMP-001, F-PMP-003, F-PMP-004, F-PMP-005, F-PMP-006, F-PMP-007, F-PMP-013, F-PMP-018, F-PMP-019, F-PMP-020, F-PMP-028, F-PMP-029, F-PMP-030, F-PMP-031, F-PMP-032, F-PMP-100
- Sample: RVFI retire of a CSR write instruction (csrrw/csrrs/csrrc and immediate forms) whose csr field is CSR_PMPCFG0..CSR_PMPCFG(PMPNumRegions/4-1); one sample per entry byte i = 4*idx + b (four samples per write); condition: rvfi_trap == 0 and the write is not read-only (rs1 != x0 / uimm != 0 for set/clear forms); anti-vacuity: only pmpcfg writes sample (most retires never do) and the outcome field is computed by the gen_chk_csr_readback model from the pre-write state, so a hit proves a pmpcfg write retired under the named lock/MML/RLB state and its per-entry outcome was predicted and compared on the following csrr
- Coverpoints:
  - cp_entry = i = 4*idx + b (0..PMPNumRegions-1): bins e0{0}, e1{1}, e2{2}, e3{3}, e4{4}, e5{5}, e6{6}, e7{7}, e8{8}, e9{9}, e10{10}, e11{11}, e12{12}, e13{13}, e14{14}, e15{15}
  - cp_op = csr op class: bins csrrw{csrrw or csrrwi}, csrrs{csrrs or csrrsi}, csrrc{csrrc or csrrci}
  - cp_wr_mode = written A field of entry i (after RMW combine): bins off{PMP_MODE_OFF}, tor{PMP_MODE_TOR}, na4{PMP_MODE_NA4}, napot{PMP_MODE_NAPOT}
  - cp_wr_lrwx = written L,R,W,X of entry i (after RMW combine): bins c0000{0000}, c0001{0001}, c0010{0010}, c0011{0011}, c0100{0100}, c0101{0101}, c0110{0110}, c0111{0111}, c1000{1000}, c1001{1001}, c1010{1010}, c1011{1011}, c1100{1100}, c1101{1101}, c1110{1110}, c1111{1111}
  - cp_res_bits = written bits 6:5 of entry i: bins zero{0}, nonzero{1..3}
  - cp_mml = mseccfg.MML at the write: bins mml0{0}, mml1{1}
  - cp_rlb = mseccfg.RLB at the write: bins rlb0{0}, rlb1{1}
  - cp_prelock = entry i L bit before the write: bins unlocked{0}, locked{1}
  - cp_outcome = readback-model outcome for entry i: bins written{stored as legalised (readback == predicted value, no drop)}, w_dropped{stored with W forced 0: written RW=01 under MML=0}, ignored_lock{unchanged: L=1 before the write and RLB=0}, ignored_mml_exec{unchanged: MML=1, RLB=0 and the written row is L=1 with X=1 or RW=01 (is_mml_m_exec_cfg)}
  - cp_word_lockmix = entries with L=1 and RLB=0 among the four of the written word: bins none{0}, some{1..3}, all{4}
- Crosses:
  - cr_rw01_mml = cp_wr_lrwx x cp_mml x cp_rlb x cp_outcome: bins rw01_mml0_wdrop{c0010 or c0011 or c1010 or c1011, mml0, any rlb, w_dropped: W cleared, X and L kept}, rw01_mml1_stored{c0010 or c0011, mml1, any rlb, written verbatim}, rw01_mml1_l1_rlb0_suppressed{c1010 or c1011, mml1, rlb0, ignored_mml_exec}, rw01_mml1_l1_rlb1_stored{c1010 or c1011, mml1, rlb1, written}; ignore_bins rw01_mml0_written{c0010 or c0011 or c1010 or c1011, mml0, written}: legalisation always clears W when MML=0 (F-PMP-004)
  - cr_lock_outcome = cp_prelock x cp_rlb x cp_outcome: bins locked_rlb0_ignored{locked, rlb0, ignored_lock}, locked_rlb1_written{locked, rlb1, written (including a write that clears L)}, unlocked_rlb0_written{unlocked, rlb0, written}, unlocked_rlb1_written{unlocked, rlb1, written}; ignore_bins locked_rlb0_written{locked, rlb0, written}: the lock always wins when RLB=0; ignore_bins unlocked_x_ignored_lock{unlocked, any rlb, ignored_lock}: an unlocked entry is never lock-ignored
  - cr_mml_exec_suppress = cp_mml x cp_rlb x cp_wr_lrwx x cp_outcome: bins rlb0_c1001_suppressed{mml1, rlb0, c1001, ignored_mml_exec}, rlb0_c1010_suppressed{mml1, rlb0, c1010, ignored_mml_exec}, rlb0_c1011_suppressed{mml1, rlb0, c1011, ignored_mml_exec}, rlb0_c1101_suppressed{mml1, rlb0, c1101, ignored_mml_exec}, rlb1_c1001_written{mml1, rlb1, c1001, written: RLB lifts the restriction}, rlb1_c1010_written{mml1, rlb1, c1010, written: RLB lifts the restriction}, rlb1_c1011_written{mml1, rlb1, c1011, written: RLB lifts the restriction}, rlb1_c1101_written{mml1, rlb1, c1101, written: RLB lifts the restriction}; ignore_bins rlb0_x_written{mml1, rlb0, c1001 or c1010 or c1011 or c1101, written}: suppression is unconditional for these rows when RLB=0 (rtl/ibex_cs_registers.sv is_mml_m_exec_cfg)
  - cr_mml_nonexec_accept = cp_mml x cp_rlb x cp_wr_lrwx x cp_outcome: bins c1000_written{mml1, rlb0, c1000, written: locked non-executable row accepted}, c1100_written{mml1, rlb0, c1100, written: locked non-executable row accepted}, c1110_written{mml1, rlb0, c1110, written: locked non-executable row accepted}, c1111_written{mml1, rlb0, c1111, written: locked non-executable row accepted}
  - cr_suppress_mode = cp_outcome x cp_wr_mode: bins off{ignored_mml_exec, PMP_MODE_OFF: A is not consulted (F-PMP-030)}, tor{ignored_mml_exec, PMP_MODE_TOR}, na4{ignored_mml_exec, PMP_MODE_NA4}, napot{ignored_mml_exec, PMP_MODE_NAPOT}
  - cr_mode_lrwx = cp_wr_mode x cp_wr_lrwx: bins off_c0000{PMP_MODE_OFF, 0000}, off_c0001{PMP_MODE_OFF, 0001}, off_c0010{PMP_MODE_OFF, 0010}, off_c0011{PMP_MODE_OFF, 0011}, off_c0100{PMP_MODE_OFF, 0100}, off_c0101{PMP_MODE_OFF, 0101}, off_c0110{PMP_MODE_OFF, 0110}, off_c0111{PMP_MODE_OFF, 0111}, off_c1000{PMP_MODE_OFF, 1000}, off_c1001{PMP_MODE_OFF, 1001}, off_c1010{PMP_MODE_OFF, 1010}, off_c1011{PMP_MODE_OFF, 1011}, off_c1100{PMP_MODE_OFF, 1100}, off_c1101{PMP_MODE_OFF, 1101}, off_c1110{PMP_MODE_OFF, 1110}, off_c1111{PMP_MODE_OFF, 1111}, tor_c0000{PMP_MODE_TOR, 0000}, tor_c0001{PMP_MODE_TOR, 0001}, tor_c0010{PMP_MODE_TOR, 0010}, tor_c0011{PMP_MODE_TOR, 0011}, tor_c0100{PMP_MODE_TOR, 0100}, tor_c0101{PMP_MODE_TOR, 0101}, tor_c0110{PMP_MODE_TOR, 0110}, tor_c0111{PMP_MODE_TOR, 0111}, tor_c1000{PMP_MODE_TOR, 1000}, tor_c1001{PMP_MODE_TOR, 1001}, tor_c1010{PMP_MODE_TOR, 1010}, tor_c1011{PMP_MODE_TOR, 1011}, tor_c1100{PMP_MODE_TOR, 1100}, tor_c1101{PMP_MODE_TOR, 1101}, tor_c1110{PMP_MODE_TOR, 1110}, tor_c1111{PMP_MODE_TOR, 1111}, na4_c0000{PMP_MODE_NA4, 0000}, na4_c0001{PMP_MODE_NA4, 0001}, na4_c0010{PMP_MODE_NA4, 0010}, na4_c0011{PMP_MODE_NA4, 0011}, na4_c0100{PMP_MODE_NA4, 0100}, na4_c0101{PMP_MODE_NA4, 0101}, na4_c0110{PMP_MODE_NA4, 0110}, na4_c0111{PMP_MODE_NA4, 0111}, na4_c1000{PMP_MODE_NA4, 1000}, na4_c1001{PMP_MODE_NA4, 1001}, na4_c1010{PMP_MODE_NA4, 1010}, na4_c1011{PMP_MODE_NA4, 1011}, na4_c1100{PMP_MODE_NA4, 1100}, na4_c1101{PMP_MODE_NA4, 1101}, na4_c1110{PMP_MODE_NA4, 1110}, na4_c1111{PMP_MODE_NA4, 1111}, napot_c0000{PMP_MODE_NAPOT, 0000}, napot_c0001{PMP_MODE_NAPOT, 0001}, napot_c0010{PMP_MODE_NAPOT, 0010}, napot_c0011{PMP_MODE_NAPOT, 0011}, napot_c0100{PMP_MODE_NAPOT, 0100}, napot_c0101{PMP_MODE_NAPOT, 0101}, napot_c0110{PMP_MODE_NAPOT, 0110}, napot_c0111{PMP_MODE_NAPOT, 0111}, napot_c1000{PMP_MODE_NAPOT, 1000}, napot_c1001{PMP_MODE_NAPOT, 1001}, napot_c1010{PMP_MODE_NAPOT, 1010}, napot_c1011{PMP_MODE_NAPOT, 1011}, napot_c1100{PMP_MODE_NAPOT, 1100}, napot_c1101{PMP_MODE_NAPOT, 1101}, napot_c1110{PMP_MODE_NAPOT, 1110}, napot_c1111{PMP_MODE_NAPOT, 1111}
  - cr_lockmix_op = cp_word_lockmix x cp_op: bins some_csrrw{some, csrrw: partial word update}, some_csrrs{some, csrrs}, some_csrrc{some, csrrc}
  - cr_res_op = cp_res_bits x cp_op: bins nonzero_csrrw{nonzero, csrrw}, nonzero_csrrs{nonzero, csrrs}, nonzero_csrrc{nonzero, csrrc}
  - cr_prelock_wrl = cp_prelock x cp_wr_lrwx x cp_outcome x cp_mml: bins setlock_c1000{unlocked, c1000, written, mml0: the write that sets L succeeds (pre-write lock state used)}, setlock_c1001{unlocked, c1001, written, mml0: the write that sets L succeeds (pre-write lock state used)}, setlock_c1100{unlocked, c1100, written, mml0: the write that sets L succeeds (pre-write lock state used)}, setlock_c1101{unlocked, c1101, written, mml0: the write that sets L succeeds (pre-write lock state used)}, setlock_c1110{unlocked, c1110, written, mml0: the write that sets L succeeds (pre-write lock state used)}, setlock_c1111{unlocked, c1111, written, mml0: the write that sets L succeeds (pre-write lock state used)}; ignore_bins setlock_c1010{unlocked, c1010, written, mml0}: RW=01 under MML=0 is legalised to W=0 (outcome w_dropped, never written); the L bit still sets and is covered by cr_rw01_mml.rw01_mml0_wdrop (S-7); ignore_bins setlock_c1011{unlocked, c1011, written, mml0}: same as setlock_c1010
- Adopted (riscv-dv): none
- TP items: TP-PMP-001, TP-PMP-003, TP-PMP-004, TP-PMP-005, TP-PMP-006, TP-PMP-007, TP-PMP-013, TP-PMP-019, TP-PMP-020, TP-PMP-021, TP-PMP-027, TP-PMP-028, TP-PMP-029, TP-PMP-030, TP-PMP-109, TP-PMP-111, TP-PMP-112

### CG-PMP-002: gen_cg_pmp_addr_write
- Features: F-PMP-002, F-PMP-008, F-PMP-009, F-PMP-010, F-PMP-011, F-PMP-012, F-PMP-014, F-PMP-018, F-PMP-028, F-PMP-100
- Sample: RVFI retire of a CSR write instruction whose csr field is CSR_PMPADDR0..CSR_PMPADDR(PMPNumRegions-1); condition: rvfi_trap == 0 and not read-only; anti-vacuity: only pmpaddr writes sample; cp_outcome comes from the readback model's pre-write lock state, so a hit proves the lock / TOR-lock rule was exercised for that index and compared on the following csrr
- Coverpoints:
  - cp_idx = pmpaddr index i (0..PMPNumRegions-1): bins a0{0}, a1{1}, a2{2}, a3{3}, a4{4}, a5{5}, a6{6}, a7{7}, a8{8}, a9{9}, a10{10}, a11{11}, a12{12}, a13{13}, a14{14}, a15{15}
  - cp_op = csr op class: bins csrrw{csrrw or csrrwi}, csrrs{csrrs or csrrsi}, csrrc{csrrc or csrrci}
  - cp_self_lock = pmpcfg(i).L & ~RLB before the write: bins unlocked{0}, locked{1}
  - cp_next_cfg = entry i+1 state before the write: bins next_unlocked_tor{i < PMPNumRegions-1, (L=0 or RLB=1), A == PMP_MODE_TOR}, next_unlocked_other{i < PMPNumRegions-1, (L=0 or RLB=1), A != PMP_MODE_TOR}, next_locked_tor{i < PMPNumRegions-1, L=1, RLB=0, A == PMP_MODE_TOR}, next_locked_other{i < PMPNumRegions-1, L=1, RLB=0, A != PMP_MODE_TOR}, top{i == PMPNumRegions-1: no next entry}
  - cp_rlb = mseccfg.RLB at the write: bins rlb0{0}, rlb1{1}
  - cp_outcome = readback-model outcome: bins written{readback == written value (full 32 bits at PMPGranularity = 0)}, ignored_self_lock{unchanged: pmpcfg(i).L=1 and RLB=0}, ignored_tor_lock{unchanged: pmpcfg(i+1) is L=1 TOR and RLB=0}
  - cp_hi_bits = wdata[31:30] (physical address bits 33:32): bins none{00}, bit30{01}, bit31{10}, both{11}
  - cp_self_mode = pmpcfg(i).A at the write: bins off{PMP_MODE_OFF}, tor{PMP_MODE_TOR}, na4{PMP_MODE_NA4}, napot{PMP_MODE_NAPOT}
- Crosses:
  - cr_tor_lock = cp_self_lock x cp_next_cfg x cp_rlb x cp_outcome: bins nl_tor_rlb0_ignored{unlocked, next_locked_tor, rlb0, ignored_tor_lock}, nl_tor_rlb1_written{unlocked, next_locked_tor, rlb1, written: RLB lifts the previous-address lock}, nl_other_rlb0_written{unlocked, next_locked_other, rlb0, written: a locked non-TOR neighbour does not protect pmpaddr(i)}, nu_tor_rlb0_written{unlocked, next_unlocked_tor, rlb0, written}, top_rlb0_written{unlocked, top, rlb0, written: index PMPNumRegions-1 has no next-entry check}; ignore_bins nl_tor_rlb0_written{unlocked, next_locked_tor, rlb0, written}: the TOR lock always wins when RLB=0; ignore_bins x_rlb1_ignored_tor_lock{any, any, rlb1, ignored_tor_lock}: no TOR lock when RLB=1
  - cr_self_lock = cp_self_lock x cp_rlb x cp_outcome: bins locked_rlb0_ignored{locked, rlb0, ignored_self_lock}, locked_rlb1_written{locked, rlb1, written}, unlocked_rlb0_written{unlocked, rlb0, written}; ignore_bins locked_rlb0_written{locked, rlb0, written}: the self lock always wins when RLB=0
  - cr_top_lock = cp_idx x cp_self_lock x cp_outcome: bins top_unlocked_written{a15 (PMPNumRegions-1), unlocked, written}, top_locked_ignored{a15 (PMPNumRegions-1), locked, ignored_self_lock}
  - cr_hi_mode = cp_hi_bits x cp_self_mode: bins bit30_off{bit30, PMP_MODE_OFF: bits 33:32 stored regardless of mode}, bit30_tor{bit30, PMP_MODE_TOR: bits 33:32 stored regardless of mode}, bit30_na4{bit30, PMP_MODE_NA4: bits 33:32 stored regardless of mode}, bit30_napot{bit30, PMP_MODE_NAPOT: bits 33:32 stored regardless of mode}, bit31_off{bit31, PMP_MODE_OFF: bits 33:32 stored regardless of mode}, bit31_tor{bit31, PMP_MODE_TOR: bits 33:32 stored regardless of mode}, bit31_na4{bit31, PMP_MODE_NA4: bits 33:32 stored regardless of mode}, bit31_napot{bit31, PMP_MODE_NAPOT: bits 33:32 stored regardless of mode}, both_off{both, PMP_MODE_OFF: bits 33:32 stored regardless of mode}, both_tor{both, PMP_MODE_TOR: bits 33:32 stored regardless of mode}, both_na4{both, PMP_MODE_NA4: bits 33:32 stored regardless of mode}, both_napot{both, PMP_MODE_NAPOT: bits 33:32 stored regardless of mode}
  - cr_idx_op = cp_idx x cp_op: bins a0_csrrw{0, csrrw}, a0_csrrs{0, csrrs}, a0_csrrc{0, csrrc}, a1_csrrw{1, csrrw}, a1_csrrs{1, csrrs}, a1_csrrc{1, csrrc}, a2_csrrw{2, csrrw}, a2_csrrs{2, csrrs}, a2_csrrc{2, csrrc}, a3_csrrw{3, csrrw}, a3_csrrs{3, csrrs}, a3_csrrc{3, csrrc}, a4_csrrw{4, csrrw}, a4_csrrs{4, csrrs}, a4_csrrc{4, csrrc}, a5_csrrw{5, csrrw}, a5_csrrs{5, csrrs}, a5_csrrc{5, csrrc}, a6_csrrw{6, csrrw}, a6_csrrs{6, csrrs}, a6_csrrc{6, csrrc}, a7_csrrw{7, csrrw}, a7_csrrs{7, csrrs}, a7_csrrc{7, csrrc}, a8_csrrw{8, csrrw}, a8_csrrs{8, csrrs}, a8_csrrc{8, csrrc}, a9_csrrw{9, csrrw}, a9_csrrs{9, csrrs}, a9_csrrc{9, csrrc}, a10_csrrw{10, csrrw}, a10_csrrs{10, csrrs}, a10_csrrc{10, csrrc}, a11_csrrw{11, csrrw}, a11_csrrs{11, csrrs}, a11_csrrc{11, csrrc}, a12_csrrw{12, csrrw}, a12_csrrs{12, csrrs}, a12_csrrc{12, csrrc}, a13_csrrw{13, csrrw}, a13_csrrs{13, csrrs}, a13_csrrc{13, csrrc}, a14_csrrw{14, csrrw}, a14_csrrs{14, csrrs}, a14_csrrc{14, csrrc}, a15_csrrw{15, csrrw}, a15_csrrs{15, csrrs}, a15_csrrc{15, csrrc}
- Adopted (riscv-dv): none
- TP items: TP-PMP-002, TP-PMP-007, TP-PMP-014, TP-PMP-015, TP-PMP-016, TP-PMP-017, TP-PMP-018, TP-PMP-020, TP-PMP-021, TP-PMP-037, TP-PMP-042, TP-PMP-109, TP-PMP-112

### CG-PMP-003: gen_cg_pmp_mseccfg
- Features: F-PMP-013, F-PMP-021, F-PMP-022, F-PMP-023, F-PMP-024, F-PMP-025, F-PMP-026, F-PMP-027, F-PMP-033
- Sample: RVFI retire of a CSR write to CSR_MSECCFG or CSR_MSECCFGH with rvfi_trap == 0 and not read-only; anti-vacuity: only these two CSRs sample; pre/post state and any_locked come from the readback model, so a hit on a transition bin proves a write attempted that transition under the named lock state and the readback was compared
- Coverpoints:
  - cp_csr = target CSR: bins mseccfg{CSR_MSECCFG}, mseccfgh{CSR_MSECCFGH}
  - cp_op = csr op class: bins csrrw{csrrw or csrrwi}, csrrs{csrrs or csrrsi}, csrrc{csrrc or csrrci}
  - cp_pre = mseccfg {mml,mmwp,rlb} before the write: bins s000{0,0,0}, s001{0,0,1}, s010{0,1,0}, s011{0,1,1}, s100{1,0,0}, s101{1,0,1}, s110{1,1,0}, s111{1,1,1}
  - cp_post = mseccfg {mml,mmwp,rlb} after the write (readback): bins s000{0,0,0}, s001{0,0,1}, s010{0,1,0}, s011{0,1,1}, s100{1,0,0}, s101{1,0,1}, s110{1,1,0}, s111{1,1,1}
  - cp_pre_mml = MML before: bins p0{0}, p1{1}
  - cp_pre_mmwp = MMWP before: bins p0{0}, p1{1}
  - cp_pre_rlb = RLB before: bins p0{0}, p1{1}
  - cp_wr_mml = written bit CSR_MSECCFG_MML_BIT after RMW combine: bins w0{0}, w1{1}
  - cp_wr_mmwp = written bit CSR_MSECCFG_MMWP_BIT after RMW combine: bins w0{0}, w1{1}
  - cp_wr_rlb = written bit CSR_MSECCFG_RLB_BIT after RMW combine: bins w0{0}, w1{1}
  - cp_any_locked = |(pmpcfg.L & ~RLB) before the write: bins none{0}, some{1}
  - cp_locked_off_only = every L=1 entry has A == PMP_MODE_OFF, iff cp_any_locked == some: bins no{at least one locked entry with A != PMP_MODE_OFF}, yes{all locked entries have A == PMP_MODE_OFF}
  - cp_hi_bits = written bits 31:3 (mseccfg) or any bit (mseccfgh): bins zero{0}, nonzero{!= 0}
- Crosses:
  - cr_mml_trans = cp_pre_mml x cp_wr_mml: bins mml_0_w0_stay0{p0, w0: readback 0}, mml_0_w1_set{p0, w1: readback 1}, mml_1_w0_hold{p1, w0: sticky, readback stays 1}, mml_1_w1_hold{p1, w1: readback 1}
  - cr_mmwp_trans = cp_pre_mmwp x cp_wr_mmwp: bins mmwp_0_w0_stay0{p0, w0}, mmwp_0_w1_set{p0, w1}, mmwp_1_w0_hold{p1, w0: sticky}, mmwp_1_w1_hold{p1, w1}
  - cr_rlb_trans = cp_pre_rlb x cp_wr_rlb x cp_any_locked x cp_locked_off_only: bins rlb_0_w1_nolock_set{p0, w1, none: RLB becomes 1}, rlb_0_w1_locked_blocked{p0, w1, some, no: stays 0}, rlb_0_w1_lockedoff_blocked{p0, w1, some, yes: stays 0, an A=OFF lock counts (F-PMP-013)}, rlb_0_w0_nolock_stay{p0, w0, none}, rlb_0_w0_locked_stay{p0, w0, some}, rlb_1_w0_clear{p1, w0, none: any_pmp_entry_locked is masked while RLB=1, the clear succeeds}, rlb_1_w1_hold{p1, w1, none}; ignore_bins rlb_1_x_locked{p1, any, some}: any_pmp_entry_locked is masked by RLB=1 (rtl/ibex_cs_registers.sv:1463,1510)
  - cr_state_trans = cp_pre x cp_post: bins s000_to_s000{s000 -> s000 (bits mml,mmwp,rlb)}, s000_to_s001{s000 -> s001 (bits mml,mmwp,rlb)}, s000_to_s010{s000 -> s010 (bits mml,mmwp,rlb)}, s000_to_s011{s000 -> s011 (bits mml,mmwp,rlb)}, s000_to_s100{s000 -> s100 (bits mml,mmwp,rlb)}, s000_to_s101{s000 -> s101 (bits mml,mmwp,rlb)}, s000_to_s110{s000 -> s110 (bits mml,mmwp,rlb)}, s000_to_s111{s000 -> s111 (bits mml,mmwp,rlb)}, s001_to_s000{s001 -> s000 (bits mml,mmwp,rlb)}, s001_to_s001{s001 -> s001 (bits mml,mmwp,rlb)}, s001_to_s010{s001 -> s010 (bits mml,mmwp,rlb)}, s001_to_s011{s001 -> s011 (bits mml,mmwp,rlb)}, s001_to_s100{s001 -> s100 (bits mml,mmwp,rlb)}, s001_to_s101{s001 -> s101 (bits mml,mmwp,rlb)}, s001_to_s110{s001 -> s110 (bits mml,mmwp,rlb)}, s001_to_s111{s001 -> s111 (bits mml,mmwp,rlb)}, s010_to_s010{s010 -> s010 (bits mml,mmwp,rlb)}, s010_to_s011{s010 -> s011 (bits mml,mmwp,rlb)}, s010_to_s110{s010 -> s110 (bits mml,mmwp,rlb)}, s010_to_s111{s010 -> s111 (bits mml,mmwp,rlb)}, s011_to_s010{s011 -> s010 (bits mml,mmwp,rlb)}, s011_to_s011{s011 -> s011 (bits mml,mmwp,rlb)}, s011_to_s110{s011 -> s110 (bits mml,mmwp,rlb)}, s011_to_s111{s011 -> s111 (bits mml,mmwp,rlb)}, s100_to_s100{s100 -> s100 (bits mml,mmwp,rlb)}, s100_to_s110{s100 -> s110 (bits mml,mmwp,rlb)}, s101_to_s100{s101 -> s100 (bits mml,mmwp,rlb)}, s101_to_s101{s101 -> s101 (bits mml,mmwp,rlb)}, s101_to_s110{s101 -> s110 (bits mml,mmwp,rlb)}, s101_to_s111{s101 -> s111 (bits mml,mmwp,rlb)}, s110_to_s110{s110 -> s110 (bits mml,mmwp,rlb)}, s111_to_s110{s111 -> s110 (bits mml,mmwp,rlb)}, s111_to_s111{s111 -> s111 (bits mml,mmwp,rlb)}; ignore_bins s_down{any pre with post.mml < pre.mml or post.mmwp < pre.mmwp}: MML and MMWP are sticky; contradicts the readback model; ignore_bins rlb_set_under_mml_locked{s100 -> s101, s100 -> s111, s110 -> s111}: RLB 0->1 requires any_pmp_entry_locked == 0 (rtl/ibex_cs_registers.sv:1463, 1514) while M-mode execution under MML=1 requires an L=1 executable rule, so (1,x,0)->(1,x,1) is unreachable outside debug mode (fact-check X-20, TP-PMP-108; debug-ROM variant OQ-PMP-10)
  - cr_mseccfgh = cp_csr x cp_hi_bits x cp_op: bins mseccfgh_nonzero_csrrw{mseccfgh, nonzero, csrrw: readback 0}, mseccfgh_nonzero_csrrs{mseccfgh, nonzero, csrrs: readback 0}, mseccfgh_nonzero_csrrc{mseccfgh, nonzero, csrrc: readback 0}
  - cr_hi_bits = cp_csr x cp_hi_bits: bins mseccfg_hi_nonzero{mseccfg, nonzero: bits 31:3 read back 0}
  - cr_op_trans = cp_op x cp_pre_mml x cp_wr_mml x cp_pre_mmwp x cp_wr_mmwp: bins csrrw_mml_hold{csrrw, pre_mml p1, wr_mml w0, any, any: csrrw attempts a clear, readback keeps 1}, csrrc_mml_hold{csrrc, pre_mml p1, wr_mml w0, any, any}, csrrw_mmwp_hold{csrrw, any, any, pre_mmwp p1, wr_mmwp w0}, csrrc_mmwp_hold{csrrc, any, any, pre_mmwp p1, wr_mmwp w0}; ignore_bins csrrs_x_hold{csrrs, (pre_mml p1 and wr_mml w0) or (pre_mmwp p1 and wr_mmwp w0)}: csrrs cannot clear a set bit: the RMW-combined write bit stays 1 (rewritten from the cross-of-a-cross form, S-7)
- Adopted (riscv-dv): none
- TP items: TP-PMP-007, TP-PMP-011, TP-PMP-012, TP-PMP-019, TP-PMP-022, TP-PMP-023, TP-PMP-024, TP-PMP-025, TP-PMP-026, TP-PMP-031, TP-PMP-108, TP-PMP-109, TP-PMP-112

### CG-PMP-004: gen_cg_pmp_csr_access
- Features: F-PMP-001, F-PMP-002, F-PMP-015, F-PMP-016, F-PMP-017, F-PMP-018, F-PMP-021, F-PMP-022
- Sample: RVFI retire of any CSR instruction whose csr field is in {CSR_PMPCFG0..CSR_PMPCFG(PMPNumRegions/4-1), CSR_PMPADDR0..CSR_PMPADDR(PMPNumRegions-1), CSR_MSECCFG, CSR_MSECCFGH}, including trapped ones (rvfi_trap == 1); anti-vacuity: only PMP CSR instructions sample; a hit proves the access happened in the named privilege/debug state and its trap outcome was compared
- Coverpoints:
  - cp_class = CSR class: bins pmpcfg{CSR_PMPCFG0..CSR_PMPCFG(PMPNumRegions/4-1)}, pmpaddr{CSR_PMPADDR0..CSR_PMPADDR(PMPNumRegions-1)}, mseccfg{CSR_MSECCFG}, mseccfgh{CSR_MSECCFGH}
  - cp_priv = rvfi_mode: bins m{PRIV_LVL_M (3)}, u{PRIV_LVL_U (0)}
  - cp_dbg = rvfi_ext_debug_mode: bins d0{0}, d1{1}
  - cp_op = csr op: bins csrrw{csrrw}, csrrs{csrrs}, csrrc{csrrc}, csrrwi{csrrwi}, csrrsi{csrrsi}, csrrci{csrrci}
  - cp_rw = read-only form (rs1 == x0 / uimm == 0 for set/clear forms) vs write: bins read_only{no write side effect}, write{csr_op_en}
  - cp_trap = rvfi_trap and cause: bins none{rvfi_trap == 0}, illegal{rvfi_trap == 1, mcause 2}
  - cp_first_after_reset = no prior write to this CSR since reset: bins no{written before}, yes{first access since reset}
- Crosses:
  - cr_priv_trap = cp_priv x cp_trap: bins m_none{m, none}, u_illegal{u, illegal}; ignore_bins m_illegal{m, illegal}: PMP CSRs exist and are legal in M; ignore_bins u_none{u, none}: a U access always traps
  - cr_u_class = cp_priv x cp_class x cp_rw: bins u_pmpcfg_read_only{u, pmpcfg, read_only}, u_pmpcfg_write{u, pmpcfg, write}, u_pmpaddr_read_only{u, pmpaddr, read_only}, u_pmpaddr_write{u, pmpaddr, write}, u_mseccfg_read_only{u, mseccfg, read_only}, u_mseccfg_write{u, mseccfg, write}, u_mseccfgh_read_only{u, mseccfgh, read_only}, u_mseccfgh_write{u, mseccfgh, write}
  - cr_dbg_class = cp_dbg x cp_class x cp_rw: bins d1_pmpcfg_read_only{d1, pmpcfg, read_only}, d1_pmpcfg_write{d1, pmpcfg, write}, d1_pmpaddr_read_only{d1, pmpaddr, read_only}, d1_pmpaddr_write{d1, pmpaddr, write}, d1_mseccfg_read_only{d1, mseccfg, read_only}, d1_mseccfg_write{d1, mseccfg, write}, d1_mseccfgh_read_only{d1, mseccfgh, read_only}, d1_mseccfgh_write{d1, mseccfgh, write}
  - cr_reset_read = cp_first_after_reset x cp_class x cp_rw: bins rst_pmpcfg{yes, pmpcfg, read_only: readback == PmpCfgRst}, rst_pmpaddr{yes, pmpaddr, read_only: readback == PmpAddrRst}, rst_mseccfg{yes, mseccfg, read_only: readback == PmpMseccfgRst}, rst_mseccfgh{yes, mseccfgh, read_only: readback == 0}
  - cr_op_class = cp_op x cp_class: bins csrrw_pmpcfg{csrrw, pmpcfg}, csrrw_pmpaddr{csrrw, pmpaddr}, csrrw_mseccfg{csrrw, mseccfg}, csrrw_mseccfgh{csrrw, mseccfgh}, csrrs_pmpcfg{csrrs, pmpcfg}, csrrs_pmpaddr{csrrs, pmpaddr}, csrrs_mseccfg{csrrs, mseccfg}, csrrs_mseccfgh{csrrs, mseccfgh}, csrrc_pmpcfg{csrrc, pmpcfg}, csrrc_pmpaddr{csrrc, pmpaddr}, csrrc_mseccfg{csrrc, mseccfg}, csrrc_mseccfgh{csrrc, mseccfgh}, csrrwi_pmpcfg{csrrwi, pmpcfg}, csrrwi_pmpaddr{csrrwi, pmpaddr}, csrrwi_mseccfg{csrrwi, mseccfg}, csrrwi_mseccfgh{csrrwi, mseccfgh}, csrrsi_pmpcfg{csrrsi, pmpcfg}, csrrsi_pmpaddr{csrrsi, pmpaddr}, csrrsi_mseccfg{csrrsi, mseccfg}, csrrsi_mseccfgh{csrrsi, mseccfgh}, csrrci_pmpcfg{csrrci, pmpcfg}, csrrci_pmpaddr{csrrci, pmpaddr}, csrrci_mseccfg{csrrci, mseccfg}, csrrci_mseccfgh{csrrci, mseccfgh}
- Adopted (riscv-dv): none
- TP items: TP-PMP-001, TP-PMP-002, TP-PMP-007, TP-PMP-008, TP-PMP-009, TP-PMP-010, TP-PMP-011, TP-PMP-012, TP-PMP-104

### CG-PMP-005: gen_cg_pmp_access_verdict
- Features: F-PMP-034, F-PMP-045, F-PMP-047, F-PMP-049, F-PMP-050, F-PMP-051, F-PMP-052, F-PMP-054, F-PMP-056, F-PMP-057, F-PMP-058, F-PMP-059, F-PMP-060, F-PMP-061, F-PMP-062, F-PMP-063, F-PMP-064, F-PMP-071
- Sample: every non-trivial PMP check performed by the gen_chk_pmp model, one sample per checked word: (a) fetch: per rvfi_valid retire on rvfi_pc_rdata with priv = rvfi_mode (M in debug mode) and type fetch; (b) second fetch half: when the retired instruction is uncompressed and pc[1] == 1, a second sample on pc + 2; (c) data: per word of each retired load/store (rvfi_mem_rmask/wmask != 0; a split misaligned access gives two samples) with priv = mstatus.MPRV ? MPP : rvfi_mode and type from rvfi_mem_wmask; condition (discriminating, S-3): the check is non-trivial, i.e. at least one entry has A != PMP_MODE_OFF, or mseccfg.MML or mseccfg.MMWP is 1, or the effective privilege is U; anti-vacuity: in the reset state (all entries OFF, mseccfg 0) M-mode accesses never sample, so cp_match.nomatch and the cr_nomatch bins are not hit by every instruction of every test; a nomatch hit proves the word was checked against at least one live region (or a no-match rule) and none covered it; a match hit proves a live region of that config decided an access of that type and privilege; the verdict was checked against rvfi_trap / bus activity
- Coverpoints:
  - cp_type = access type: bins fetch{PMP_ACC_EXEC (instruction)}, load{PMP_ACC_READ (rvfi_mem_rmask != 0)}, store{PMP_ACC_WRITE (rvfi_mem_wmask != 0)}
  - cp_priv = effective privilege of the check: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_mml = mseccfg.MML: bins mml0{0}, mml1{1}
  - cp_mmwp = mseccfg.MMWP: bins mmwp0{0}, mmwp1{1}
  - cp_match = any enabled region matches the word: bins nomatch{no enabled region covers the word}, match{lowest matching index decides}
  - cp_lrwx = L,R,W,X of the lowest matching region, iff match: bins c0000{0000}, c0001{0001}, c0010{0010}, c0011{0011}, c0100{0100}, c0101{0101}, c0110{0110}, c0111{0111}, c1000{1000}, c1001{1001}, c1010{1010}, c1011{1011}, c1100{1100}, c1101{1101}, c1110{1110}, c1111{1111}
  - cp_verdict = gen_chk_pmp model verdict: bins allow{no fault predicted}, deny{fault predicted: cause 1 / 5 / 7}
  - cp_region = index of the deciding region, iff match: bins r0{0}, r1{1}, r2{2}, r3{3}, r4{4}, r5{5}, r6{6}, r7{7}, r8{8}, r9{9}, r10{10}, r11{11}, r12{12}, r13{13}, r14{14}, r15{15}
  - cp_mode = A field of the deciding region, iff match: bins tor{PMP_MODE_TOR}, na4{PMP_MODE_NA4}, napot{PMP_MODE_NAPOT}; ignore_bins off{PMP_MODE_OFF}: an OFF entry never matches (F-PMP-034)
  - cp_off_shadow = iff nomatch: an A=OFF entry's pmpaddr, decoded as NA4/NAPOT/TOR with its stored bits, would cover the word: bins none{no OFF entry shadows the word}, off_covers{at least one OFF entry would cover the word if enabled}
- Crosses:
  - cr_truth_mml1 = cp_mml x cp_match x cp_lrwx x cp_priv x cp_type x cp_verdict: bins c0000_m_fetch{mml1, match, 0000, m, fetch, verdict deny}, c0000_m_load{mml1, match, 0000, m, load, verdict deny}, c0000_m_store{mml1, match, 0000, m, store, verdict deny}, c0000_u_fetch{mml1, match, 0000, u, fetch, verdict deny}, c0000_u_load{mml1, match, 0000, u, load, verdict deny}, c0000_u_store{mml1, match, 0000, u, store, verdict deny}, c0001_m_fetch{mml1, match, 0001, m, fetch, verdict deny}, c0001_m_load{mml1, match, 0001, m, load, verdict deny}, c0001_m_store{mml1, match, 0001, m, store, verdict deny}, c0001_u_fetch{mml1, match, 0001, u, fetch, verdict allow}, c0001_u_load{mml1, match, 0001, u, load, verdict deny}, c0001_u_store{mml1, match, 0001, u, store, verdict deny}, c0010_m_fetch{mml1, match, 0010, m, fetch, verdict deny}, c0010_m_load{mml1, match, 0010, m, load, verdict allow}, c0010_m_store{mml1, match, 0010, m, store, verdict allow}, c0010_u_fetch{mml1, match, 0010, u, fetch, verdict deny}, c0010_u_load{mml1, match, 0010, u, load, verdict allow}, c0010_u_store{mml1, match, 0010, u, store, verdict deny}, c0011_m_fetch{mml1, match, 0011, m, fetch, verdict deny}, c0011_m_load{mml1, match, 0011, m, load, verdict allow}, c0011_m_store{mml1, match, 0011, m, store, verdict allow}, c0011_u_fetch{mml1, match, 0011, u, fetch, verdict deny}, c0011_u_load{mml1, match, 0011, u, load, verdict allow}, c0011_u_store{mml1, match, 0011, u, store, verdict allow}, c0100_m_fetch{mml1, match, 0100, m, fetch, verdict deny}, c0100_m_load{mml1, match, 0100, m, load, verdict deny}, c0100_m_store{mml1, match, 0100, m, store, verdict deny}, c0100_u_fetch{mml1, match, 0100, u, fetch, verdict deny}, c0100_u_load{mml1, match, 0100, u, load, verdict allow}, c0100_u_store{mml1, match, 0100, u, store, verdict deny}, c0101_m_fetch{mml1, match, 0101, m, fetch, verdict deny}, c0101_m_load{mml1, match, 0101, m, load, verdict deny}, c0101_m_store{mml1, match, 0101, m, store, verdict deny}, c0101_u_fetch{mml1, match, 0101, u, fetch, verdict allow}, c0101_u_load{mml1, match, 0101, u, load, verdict allow}, c0101_u_store{mml1, match, 0101, u, store, verdict deny}, c0110_m_fetch{mml1, match, 0110, m, fetch, verdict deny}, c0110_m_load{mml1, match, 0110, m, load, verdict deny}, c0110_m_store{mml1, match, 0110, m, store, verdict deny}, c0110_u_fetch{mml1, match, 0110, u, fetch, verdict deny}, c0110_u_load{mml1, match, 0110, u, load, verdict allow}, c0110_u_store{mml1, match, 0110, u, store, verdict allow}, c0111_m_fetch{mml1, match, 0111, m, fetch, verdict deny}, c0111_m_load{mml1, match, 0111, m, load, verdict deny}, c0111_m_store{mml1, match, 0111, m, store, verdict deny}, c0111_u_fetch{mml1, match, 0111, u, fetch, verdict allow}, c0111_u_load{mml1, match, 0111, u, load, verdict allow}, c0111_u_store{mml1, match, 0111, u, store, verdict allow}, c1000_m_fetch{mml1, match, 1000, m, fetch, verdict deny}, c1000_m_load{mml1, match, 1000, m, load, verdict deny}, c1000_m_store{mml1, match, 1000, m, store, verdict deny}, c1000_u_fetch{mml1, match, 1000, u, fetch, verdict deny}, c1000_u_load{mml1, match, 1000, u, load, verdict deny}, c1000_u_store{mml1, match, 1000, u, store, verdict deny}, c1001_m_fetch{mml1, match, 1001, m, fetch, verdict allow}, c1001_m_load{mml1, match, 1001, m, load, verdict deny}, c1001_m_store{mml1, match, 1001, m, store, verdict deny}, c1001_u_fetch{mml1, match, 1001, u, fetch, verdict deny}, c1001_u_load{mml1, match, 1001, u, load, verdict deny}, c1001_u_store{mml1, match, 1001, u, store, verdict deny}, c1010_m_fetch{mml1, match, 1010, m, fetch, verdict allow}, c1010_m_load{mml1, match, 1010, m, load, verdict deny}, c1010_m_store{mml1, match, 1010, m, store, verdict deny}, c1010_u_fetch{mml1, match, 1010, u, fetch, verdict allow}, c1010_u_load{mml1, match, 1010, u, load, verdict deny}, c1010_u_store{mml1, match, 1010, u, store, verdict deny}, c1011_m_fetch{mml1, match, 1011, m, fetch, verdict allow}, c1011_m_load{mml1, match, 1011, m, load, verdict allow}, c1011_m_store{mml1, match, 1011, m, store, verdict deny}, c1011_u_fetch{mml1, match, 1011, u, fetch, verdict allow}, c1011_u_load{mml1, match, 1011, u, load, verdict deny}, c1011_u_store{mml1, match, 1011, u, store, verdict deny}, c1100_m_fetch{mml1, match, 1100, m, fetch, verdict deny}, c1100_m_load{mml1, match, 1100, m, load, verdict allow}, c1100_m_store{mml1, match, 1100, m, store, verdict deny}, c1100_u_fetch{mml1, match, 1100, u, fetch, verdict deny}, c1100_u_load{mml1, match, 1100, u, load, verdict deny}, c1100_u_store{mml1, match, 1100, u, store, verdict deny}, c1101_m_fetch{mml1, match, 1101, m, fetch, verdict allow}, c1101_m_load{mml1, match, 1101, m, load, verdict allow}, c1101_m_store{mml1, match, 1101, m, store, verdict deny}, c1101_u_fetch{mml1, match, 1101, u, fetch, verdict deny}, c1101_u_load{mml1, match, 1101, u, load, verdict deny}, c1101_u_store{mml1, match, 1101, u, store, verdict deny}, c1110_m_fetch{mml1, match, 1110, m, fetch, verdict deny}, c1110_m_load{mml1, match, 1110, m, load, verdict allow}, c1110_m_store{mml1, match, 1110, m, store, verdict allow}, c1110_u_fetch{mml1, match, 1110, u, fetch, verdict deny}, c1110_u_load{mml1, match, 1110, u, load, verdict deny}, c1110_u_store{mml1, match, 1110, u, store, verdict deny}, c1111_m_fetch{mml1, match, 1111, m, fetch, verdict deny}, c1111_m_load{mml1, match, 1111, m, load, verdict allow}, c1111_m_store{mml1, match, 1111, m, store, verdict deny}, c1111_u_fetch{mml1, match, 1111, u, fetch, verdict deny}, c1111_u_load{mml1, match, 1111, u, load, verdict allow}, c1111_u_store{mml1, match, 1111, u, store, verdict deny}; ignore_bins mml1_opposite{mml1, match, any row, any priv, any type, the opposite verdict}: contradicts smepmp.adoc (Appendix A); gen_chk_pmp fails before the sample
  - cr_truth_mml0 = cp_mml x cp_match x cp_lrwx x cp_priv x cp_type x cp_verdict: bins c0000_m_fetch{mml0, match, 0000, m, fetch, verdict allow}, c0000_m_load{mml0, match, 0000, m, load, verdict allow}, c0000_m_store{mml0, match, 0000, m, store, verdict allow}, c0000_u_fetch{mml0, match, 0000, u, fetch, verdict deny}, c0000_u_load{mml0, match, 0000, u, load, verdict deny}, c0000_u_store{mml0, match, 0000, u, store, verdict deny}, c0001_m_fetch{mml0, match, 0001, m, fetch, verdict allow}, c0001_m_load{mml0, match, 0001, m, load, verdict allow}, c0001_m_store{mml0, match, 0001, m, store, verdict allow}, c0001_u_fetch{mml0, match, 0001, u, fetch, verdict allow}, c0001_u_load{mml0, match, 0001, u, load, verdict deny}, c0001_u_store{mml0, match, 0001, u, store, verdict deny}, c0100_m_fetch{mml0, match, 0100, m, fetch, verdict allow}, c0100_m_load{mml0, match, 0100, m, load, verdict allow}, c0100_m_store{mml0, match, 0100, m, store, verdict allow}, c0100_u_fetch{mml0, match, 0100, u, fetch, verdict deny}, c0100_u_load{mml0, match, 0100, u, load, verdict allow}, c0100_u_store{mml0, match, 0100, u, store, verdict deny}, c0101_m_fetch{mml0, match, 0101, m, fetch, verdict allow}, c0101_m_load{mml0, match, 0101, m, load, verdict allow}, c0101_m_store{mml0, match, 0101, m, store, verdict allow}, c0101_u_fetch{mml0, match, 0101, u, fetch, verdict allow}, c0101_u_load{mml0, match, 0101, u, load, verdict allow}, c0101_u_store{mml0, match, 0101, u, store, verdict deny}, c0110_m_fetch{mml0, match, 0110, m, fetch, verdict allow}, c0110_m_load{mml0, match, 0110, m, load, verdict allow}, c0110_m_store{mml0, match, 0110, m, store, verdict allow}, c0110_u_fetch{mml0, match, 0110, u, fetch, verdict deny}, c0110_u_load{mml0, match, 0110, u, load, verdict allow}, c0110_u_store{mml0, match, 0110, u, store, verdict allow}, c0111_m_fetch{mml0, match, 0111, m, fetch, verdict allow}, c0111_m_load{mml0, match, 0111, m, load, verdict allow}, c0111_m_store{mml0, match, 0111, m, store, verdict allow}, c0111_u_fetch{mml0, match, 0111, u, fetch, verdict allow}, c0111_u_load{mml0, match, 0111, u, load, verdict allow}, c0111_u_store{mml0, match, 0111, u, store, verdict allow}, c1000_m_fetch{mml0, match, 1000, m, fetch, verdict deny}, c1000_m_load{mml0, match, 1000, m, load, verdict deny}, c1000_m_store{mml0, match, 1000, m, store, verdict deny}, c1000_u_fetch{mml0, match, 1000, u, fetch, verdict deny}, c1000_u_load{mml0, match, 1000, u, load, verdict deny}, c1000_u_store{mml0, match, 1000, u, store, verdict deny}, c1001_m_fetch{mml0, match, 1001, m, fetch, verdict allow}, c1001_m_load{mml0, match, 1001, m, load, verdict deny}, c1001_m_store{mml0, match, 1001, m, store, verdict deny}, c1001_u_fetch{mml0, match, 1001, u, fetch, verdict allow}, c1001_u_load{mml0, match, 1001, u, load, verdict deny}, c1001_u_store{mml0, match, 1001, u, store, verdict deny}, c1100_m_fetch{mml0, match, 1100, m, fetch, verdict deny}, c1100_m_load{mml0, match, 1100, m, load, verdict allow}, c1100_m_store{mml0, match, 1100, m, store, verdict deny}, c1100_u_fetch{mml0, match, 1100, u, fetch, verdict deny}, c1100_u_load{mml0, match, 1100, u, load, verdict allow}, c1100_u_store{mml0, match, 1100, u, store, verdict deny}, c1101_m_fetch{mml0, match, 1101, m, fetch, verdict allow}, c1101_m_load{mml0, match, 1101, m, load, verdict allow}, c1101_m_store{mml0, match, 1101, m, store, verdict deny}, c1101_u_fetch{mml0, match, 1101, u, fetch, verdict allow}, c1101_u_load{mml0, match, 1101, u, load, verdict allow}, c1101_u_store{mml0, match, 1101, u, store, verdict deny}, c1110_m_fetch{mml0, match, 1110, m, fetch, verdict deny}, c1110_m_load{mml0, match, 1110, m, load, verdict allow}, c1110_m_store{mml0, match, 1110, m, store, verdict allow}, c1110_u_fetch{mml0, match, 1110, u, fetch, verdict deny}, c1110_u_load{mml0, match, 1110, u, load, verdict allow}, c1110_u_store{mml0, match, 1110, u, store, verdict allow}, c1111_m_fetch{mml0, match, 1111, m, fetch, verdict allow}, c1111_m_load{mml0, match, 1111, m, load, verdict allow}, c1111_m_store{mml0, match, 1111, m, store, verdict allow}, c1111_u_fetch{mml0, match, 1111, u, fetch, verdict allow}, c1111_u_load{mml0, match, 1111, u, load, verdict allow}, c1111_u_store{mml0, match, 1111, u, store, verdict allow}; ignore_bins mml0_rw01{mml0, match, c0010 or c0011 or c1010 or c1011, any, any, any}: RW=01 is not storable while MML=0 (F-PMP-004) and MML is sticky; ignore_bins mml0_opposite{mml0, match, any storable row, the opposite verdict}: contradicts machine.adoc Locking and Privilege Mode (Appendix B); gen_chk_pmp fails before the sample
  - cr_nomatch = cp_match x cp_priv x cp_type x cp_mml x cp_mmwp x cp_verdict: bins nm_m_fetch_mml0_mmwp0{nomatch, m, fetch, mml0, mmwp0, verdict allow}, nm_m_fetch_mml0_mmwp1{nomatch, m, fetch, mml0, mmwp1, verdict deny}, nm_m_fetch_mml1_mmwp0{nomatch, m, fetch, mml1, mmwp0, verdict deny}, nm_m_fetch_mml1_mmwp1{nomatch, m, fetch, mml1, mmwp1, verdict deny}, nm_m_load_mml0_mmwp0{nomatch, m, load, mml0, mmwp0, verdict allow}, nm_m_load_mml0_mmwp1{nomatch, m, load, mml0, mmwp1, verdict deny}, nm_m_load_mml1_mmwp0{nomatch, m, load, mml1, mmwp0, verdict allow}, nm_m_load_mml1_mmwp1{nomatch, m, load, mml1, mmwp1, verdict deny}, nm_m_store_mml0_mmwp0{nomatch, m, store, mml0, mmwp0, verdict allow}, nm_m_store_mml0_mmwp1{nomatch, m, store, mml0, mmwp1, verdict deny}, nm_m_store_mml1_mmwp0{nomatch, m, store, mml1, mmwp0, verdict allow}, nm_m_store_mml1_mmwp1{nomatch, m, store, mml1, mmwp1, verdict deny}, nm_u_fetch_mml0_mmwp0{nomatch, u, fetch, mml0, mmwp0, verdict deny}, nm_u_fetch_mml0_mmwp1{nomatch, u, fetch, mml0, mmwp1, verdict deny}, nm_u_fetch_mml1_mmwp0{nomatch, u, fetch, mml1, mmwp0, verdict deny}, nm_u_fetch_mml1_mmwp1{nomatch, u, fetch, mml1, mmwp1, verdict deny}, nm_u_load_mml0_mmwp0{nomatch, u, load, mml0, mmwp0, verdict deny}, nm_u_load_mml0_mmwp1{nomatch, u, load, mml0, mmwp1, verdict deny}, nm_u_load_mml1_mmwp0{nomatch, u, load, mml1, mmwp0, verdict deny}, nm_u_load_mml1_mmwp1{nomatch, u, load, mml1, mmwp1, verdict deny}, nm_u_store_mml0_mmwp0{nomatch, u, store, mml0, mmwp0, verdict deny}, nm_u_store_mml0_mmwp1{nomatch, u, store, mml0, mmwp1, verdict deny}, nm_u_store_mml1_mmwp0{nomatch, u, store, mml1, mmwp0, verdict deny}, nm_u_store_mml1_mmwp1{nomatch, u, store, mml1, mmwp1, verdict deny}; ignore_bins nm_opposite{nomatch, any, the opposite verdict}: contradicts the no-match rules (rtl/ibex_pmp.sv access_fault_check); gen_chk_pmp fails first
  - cr_mode_type_priv_mml = cp_mode x cp_type x cp_priv x cp_mml x cp_verdict: bins tor_fetch_m_mml0_allow{PMP_MODE_TOR, fetch, m, mml0, allow}, tor_fetch_m_mml0_deny{PMP_MODE_TOR, fetch, m, mml0, deny}, tor_fetch_m_mml1_allow{PMP_MODE_TOR, fetch, m, mml1, allow}, tor_fetch_m_mml1_deny{PMP_MODE_TOR, fetch, m, mml1, deny}, tor_fetch_u_mml0_allow{PMP_MODE_TOR, fetch, u, mml0, allow}, tor_fetch_u_mml0_deny{PMP_MODE_TOR, fetch, u, mml0, deny}, tor_fetch_u_mml1_allow{PMP_MODE_TOR, fetch, u, mml1, allow}, tor_fetch_u_mml1_deny{PMP_MODE_TOR, fetch, u, mml1, deny}, tor_load_m_mml0_allow{PMP_MODE_TOR, load, m, mml0, allow}, tor_load_m_mml0_deny{PMP_MODE_TOR, load, m, mml0, deny}, tor_load_m_mml1_allow{PMP_MODE_TOR, load, m, mml1, allow}, tor_load_m_mml1_deny{PMP_MODE_TOR, load, m, mml1, deny}, tor_load_u_mml0_allow{PMP_MODE_TOR, load, u, mml0, allow}, tor_load_u_mml0_deny{PMP_MODE_TOR, load, u, mml0, deny}, tor_load_u_mml1_allow{PMP_MODE_TOR, load, u, mml1, allow}, tor_load_u_mml1_deny{PMP_MODE_TOR, load, u, mml1, deny}, tor_store_m_mml0_allow{PMP_MODE_TOR, store, m, mml0, allow}, tor_store_m_mml0_deny{PMP_MODE_TOR, store, m, mml0, deny}, tor_store_m_mml1_allow{PMP_MODE_TOR, store, m, mml1, allow}, tor_store_m_mml1_deny{PMP_MODE_TOR, store, m, mml1, deny}, tor_store_u_mml0_allow{PMP_MODE_TOR, store, u, mml0, allow}, tor_store_u_mml0_deny{PMP_MODE_TOR, store, u, mml0, deny}, tor_store_u_mml1_allow{PMP_MODE_TOR, store, u, mml1, allow}, tor_store_u_mml1_deny{PMP_MODE_TOR, store, u, mml1, deny}, na4_fetch_m_mml0_allow{PMP_MODE_NA4, fetch, m, mml0, allow}, na4_fetch_m_mml0_deny{PMP_MODE_NA4, fetch, m, mml0, deny}, na4_fetch_m_mml1_allow{PMP_MODE_NA4, fetch, m, mml1, allow}, na4_fetch_m_mml1_deny{PMP_MODE_NA4, fetch, m, mml1, deny}, na4_fetch_u_mml0_allow{PMP_MODE_NA4, fetch, u, mml0, allow}, na4_fetch_u_mml0_deny{PMP_MODE_NA4, fetch, u, mml0, deny}, na4_fetch_u_mml1_allow{PMP_MODE_NA4, fetch, u, mml1, allow}, na4_fetch_u_mml1_deny{PMP_MODE_NA4, fetch, u, mml1, deny}, na4_load_m_mml0_allow{PMP_MODE_NA4, load, m, mml0, allow}, na4_load_m_mml0_deny{PMP_MODE_NA4, load, m, mml0, deny}, na4_load_m_mml1_allow{PMP_MODE_NA4, load, m, mml1, allow}, na4_load_m_mml1_deny{PMP_MODE_NA4, load, m, mml1, deny}, na4_load_u_mml0_allow{PMP_MODE_NA4, load, u, mml0, allow}, na4_load_u_mml0_deny{PMP_MODE_NA4, load, u, mml0, deny}, na4_load_u_mml1_allow{PMP_MODE_NA4, load, u, mml1, allow}, na4_load_u_mml1_deny{PMP_MODE_NA4, load, u, mml1, deny}, na4_store_m_mml0_allow{PMP_MODE_NA4, store, m, mml0, allow}, na4_store_m_mml0_deny{PMP_MODE_NA4, store, m, mml0, deny}, na4_store_m_mml1_allow{PMP_MODE_NA4, store, m, mml1, allow}, na4_store_m_mml1_deny{PMP_MODE_NA4, store, m, mml1, deny}, na4_store_u_mml0_allow{PMP_MODE_NA4, store, u, mml0, allow}, na4_store_u_mml0_deny{PMP_MODE_NA4, store, u, mml0, deny}, na4_store_u_mml1_allow{PMP_MODE_NA4, store, u, mml1, allow}, na4_store_u_mml1_deny{PMP_MODE_NA4, store, u, mml1, deny}, napot_fetch_m_mml0_allow{PMP_MODE_NAPOT, fetch, m, mml0, allow}, napot_fetch_m_mml0_deny{PMP_MODE_NAPOT, fetch, m, mml0, deny}, napot_fetch_m_mml1_allow{PMP_MODE_NAPOT, fetch, m, mml1, allow}, napot_fetch_m_mml1_deny{PMP_MODE_NAPOT, fetch, m, mml1, deny}, napot_fetch_u_mml0_allow{PMP_MODE_NAPOT, fetch, u, mml0, allow}, napot_fetch_u_mml0_deny{PMP_MODE_NAPOT, fetch, u, mml0, deny}, napot_fetch_u_mml1_allow{PMP_MODE_NAPOT, fetch, u, mml1, allow}, napot_fetch_u_mml1_deny{PMP_MODE_NAPOT, fetch, u, mml1, deny}, napot_load_m_mml0_allow{PMP_MODE_NAPOT, load, m, mml0, allow}, napot_load_m_mml0_deny{PMP_MODE_NAPOT, load, m, mml0, deny}, napot_load_m_mml1_allow{PMP_MODE_NAPOT, load, m, mml1, allow}, napot_load_m_mml1_deny{PMP_MODE_NAPOT, load, m, mml1, deny}, napot_load_u_mml0_allow{PMP_MODE_NAPOT, load, u, mml0, allow}, napot_load_u_mml0_deny{PMP_MODE_NAPOT, load, u, mml0, deny}, napot_load_u_mml1_allow{PMP_MODE_NAPOT, load, u, mml1, allow}, napot_load_u_mml1_deny{PMP_MODE_NAPOT, load, u, mml1, deny}, napot_store_m_mml0_allow{PMP_MODE_NAPOT, store, m, mml0, allow}, napot_store_m_mml0_deny{PMP_MODE_NAPOT, store, m, mml0, deny}, napot_store_m_mml1_allow{PMP_MODE_NAPOT, store, m, mml1, allow}, napot_store_m_mml1_deny{PMP_MODE_NAPOT, store, m, mml1, deny}, napot_store_u_mml0_allow{PMP_MODE_NAPOT, store, u, mml0, allow}, napot_store_u_mml0_deny{PMP_MODE_NAPOT, store, u, mml0, deny}, napot_store_u_mml1_allow{PMP_MODE_NAPOT, store, u, mml1, allow}, napot_store_u_mml1_deny{PMP_MODE_NAPOT, store, u, mml1, deny}
  - cr_region_type = cp_region x cp_type: bins r0_fetch{0, fetch}, r0_load{0, load}, r0_store{0, store}, r1_fetch{1, fetch}, r1_load{1, load}, r1_store{1, store}, r2_fetch{2, fetch}, r2_load{2, load}, r2_store{2, store}, r3_fetch{3, fetch}, r3_load{3, load}, r3_store{3, store}, r4_fetch{4, fetch}, r4_load{4, load}, r4_store{4, store}, r5_fetch{5, fetch}, r5_load{5, load}, r5_store{5, store}, r6_fetch{6, fetch}, r6_load{6, load}, r6_store{6, store}, r7_fetch{7, fetch}, r7_load{7, load}, r7_store{7, store}, r8_fetch{8, fetch}, r8_load{8, load}, r8_store{8, store}, r9_fetch{9, fetch}, r9_load{9, load}, r9_store{9, store}, r10_fetch{10, fetch}, r10_load{10, load}, r10_store{10, store}, r11_fetch{11, fetch}, r11_load{11, load}, r11_store{11, store}, r12_fetch{12, fetch}, r12_load{12, load}, r12_store{12, store}, r13_fetch{13, fetch}, r13_load{13, load}, r13_store{13, store}, r14_fetch{14, fetch}, r14_load{14, load}, r14_store{14, store}, r15_fetch{15, fetch}, r15_load{15, load}, r15_store{15, store}
  - cr_region_mode = cp_region x cp_mode: bins r0_tor{0, tor}, r0_na4{0, na4}, r0_napot{0, napot}, r1_tor{1, tor}, r1_na4{1, na4}, r1_napot{1, napot}, r2_tor{2, tor}, r2_na4{2, na4}, r2_napot{2, napot}, r3_tor{3, tor}, r3_na4{3, na4}, r3_napot{3, napot}, r4_tor{4, tor}, r4_na4{4, na4}, r4_napot{4, napot}, r5_tor{5, tor}, r5_na4{5, na4}, r5_napot{5, napot}, r6_tor{6, tor}, r6_na4{6, na4}, r6_napot{6, napot}, r7_tor{7, tor}, r7_na4{7, na4}, r7_napot{7, napot}, r8_tor{8, tor}, r8_na4{8, na4}, r8_napot{8, napot}, r9_tor{9, tor}, r9_na4{9, na4}, r9_napot{9, napot}, r10_tor{10, tor}, r10_na4{10, na4}, r10_napot{10, napot}, r11_tor{11, tor}, r11_na4{11, na4}, r11_napot{11, napot}, r12_tor{12, tor}, r12_na4{12, na4}, r12_napot{12, napot}, r13_tor{13, tor}, r13_na4{13, na4}, r13_napot{13, napot}, r14_tor{14, tor}, r14_na4{14, na4}, r14_napot{14, napot}, r15_tor{15, tor}, r15_na4{15, na4}, r15_napot{15, napot}
  - cr_off_shadow = cp_off_shadow x cp_type x cp_priv: bins off_covers_fetch_m{off_covers, fetch, m: the OFF entry did not decide}, off_covers_fetch_u{off_covers, fetch, u: the OFF entry did not decide}, off_covers_load_m{off_covers, load, m: the OFF entry did not decide}, off_covers_load_u{off_covers, load, u: the OFF entry did not decide}, off_covers_store_m{off_covers, store, m: the OFF entry did not decide}, off_covers_store_u{off_covers, store, u: the OFF entry did not decide}
- Adopted (riscv-dv): none
- TP items: TP-PMP-006, TP-PMP-031, TP-PMP-032, TP-PMP-045, TP-PMP-046, TP-PMP-047, TP-PMP-048, TP-PMP-049, TP-PMP-050, TP-PMP-051, TP-PMP-052, TP-PMP-054, TP-PMP-055, TP-PMP-056, TP-PMP-057, TP-PMP-058, TP-PMP-059, TP-PMP-060, TP-PMP-061, TP-PMP-062, TP-PMP-063, TP-PMP-069, TP-PMP-100, TP-PMP-101, TP-PMP-102, TP-PMP-106

### CG-PMP-006: gen_cg_pmp_priority
- Features: F-PMP-045, F-PMP-046, F-PMP-047
- Sample: a CG-PMP-005 check event where the model finds two or more matching regions for the word; anti-vacuity: single-match and no-match accesses never sample; a hit proves an overlapping configuration was exercised by a real access and the lowest index decided (verdict compared by gen_chk_pmp)
- Coverpoints:
  - cp_nmatch = number of matching regions: bins two{2}, three{3}, four_plus{>= 4}
  - cp_dist = index distance between the two lowest matching regions: bins d1{1}, d2_3{2..3}, d4_7{4..7}, d8_15{8..PMPNumRegions-1}
  - cp_conflict = verdict of the lowest vs the second-lowest matching region: bins low_allow_high_deny{lowest allows, second-lowest denies: access allowed}, low_deny_high_allow{lowest denies, second-lowest allows: access denied}, agree_allow{both allow}, agree_deny{both deny}
  - cp_low_idx = lowest matching index: bins r0{0}, r1_7{1..7}, r8_14{8..PMPNumRegions-2}; ignore_bins r15{PMPNumRegions-1}: cannot be the lowest of two matches
  - cp_high_is_top = highest matching index == PMPNumRegions-1: bins no{0}, yes{1}
  - cp_type = access type: bins fetch{fetch}, load{load}, store{store}
  - cp_priv = effective privilege: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_mode_pair = modes of the two lowest matching regions: bins tor_tor{TOR, TOR}, tor_na{TOR, NA4/NAPOT}, na_tor{NA4/NAPOT, TOR}, na_na{NA4/NAPOT, NA4/NAPOT}
  - cp_mml = mseccfg.MML: bins mml0{0}, mml1{1}
- Crosses:
  - cr_conflict_dist = cp_conflict x cp_dist: bins low_allow_high_deny_d1{low_allow_high_deny, d1}, low_allow_high_deny_d2_3{low_allow_high_deny, d2_3}, low_allow_high_deny_d4_7{low_allow_high_deny, d4_7}, low_allow_high_deny_d8_15{low_allow_high_deny, d8_15}, low_deny_high_allow_d1{low_deny_high_allow, d1}, low_deny_high_allow_d2_3{low_deny_high_allow, d2_3}, low_deny_high_allow_d4_7{low_deny_high_allow, d4_7}, low_deny_high_allow_d8_15{low_deny_high_allow, d8_15}, agree_allow_d1{agree_allow, d1}, agree_allow_d2_3{agree_allow, d2_3}, agree_allow_d4_7{agree_allow, d4_7}, agree_allow_d8_15{agree_allow, d8_15}, agree_deny_d1{agree_deny, d1}, agree_deny_d2_3{agree_deny, d2_3}, agree_deny_d4_7{agree_deny, d4_7}, agree_deny_d8_15{agree_deny, d8_15}
  - cr_conflict_type = cp_conflict x cp_type: bins low_allow_high_deny_fetch{low_allow_high_deny, fetch}, low_allow_high_deny_load{low_allow_high_deny, load}, low_allow_high_deny_store{low_allow_high_deny, store}, low_deny_high_allow_fetch{low_deny_high_allow, fetch}, low_deny_high_allow_load{low_deny_high_allow, load}, low_deny_high_allow_store{low_deny_high_allow, store}, agree_allow_fetch{agree_allow, fetch}, agree_allow_load{agree_allow, load}, agree_allow_store{agree_allow, store}, agree_deny_fetch{agree_deny, fetch}, agree_deny_load{agree_deny, load}, agree_deny_store{agree_deny, store}
  - cr_conflict_top = cp_conflict x cp_high_is_top: bins low_allow_high_deny_top{low_allow_high_deny, yes: entry PMPNumRegions-1 is the overridden/agreeing one}, low_deny_high_allow_top{low_deny_high_allow, yes: entry PMPNumRegions-1 is the overridden/agreeing one}, agree_allow_top{agree_allow, yes: entry PMPNumRegions-1 is the overridden/agreeing one}, agree_deny_top{agree_deny, yes: entry PMPNumRegions-1 is the overridden/agreeing one}
  - cr_conflict_mode = cp_conflict x cp_mode_pair: bins low_allow_high_deny_tor_tor{low_allow_high_deny, tor_tor}, low_allow_high_deny_tor_na{low_allow_high_deny, tor_na}, low_allow_high_deny_na_tor{low_allow_high_deny, na_tor}, low_allow_high_deny_na_na{low_allow_high_deny, na_na}, low_deny_high_allow_tor_tor{low_deny_high_allow, tor_tor}, low_deny_high_allow_tor_na{low_deny_high_allow, tor_na}, low_deny_high_allow_na_tor{low_deny_high_allow, na_tor}, low_deny_high_allow_na_na{low_deny_high_allow, na_na}, agree_allow_tor_tor{agree_allow, tor_tor}, agree_allow_tor_na{agree_allow, tor_na}, agree_allow_na_tor{agree_allow, na_tor}, agree_allow_na_na{agree_allow, na_na}, agree_deny_tor_tor{agree_deny, tor_tor}, agree_deny_tor_na{agree_deny, tor_na}, agree_deny_na_tor{agree_deny, na_tor}, agree_deny_na_na{agree_deny, na_na}
  - cr_conflict_mml_priv = cp_conflict x cp_mml x cp_priv: bins low_allow_high_deny_mml0_m{low_allow_high_deny, mml0, m}, low_allow_high_deny_mml0_u{low_allow_high_deny, mml0, u}, low_allow_high_deny_mml1_m{low_allow_high_deny, mml1, m}, low_allow_high_deny_mml1_u{low_allow_high_deny, mml1, u}, low_deny_high_allow_mml0_m{low_deny_high_allow, mml0, m}, low_deny_high_allow_mml0_u{low_deny_high_allow, mml0, u}, low_deny_high_allow_mml1_m{low_deny_high_allow, mml1, m}, low_deny_high_allow_mml1_u{low_deny_high_allow, mml1, u}, agree_allow_mml0_m{agree_allow, mml0, m}, agree_allow_mml0_u{agree_allow, mml0, u}, agree_allow_mml1_m{agree_allow, mml1, m}, agree_allow_mml1_u{agree_allow, mml1, u}, agree_deny_mml0_m{agree_deny, mml0, m}, agree_deny_mml0_u{agree_deny, mml0, u}, agree_deny_mml1_m{agree_deny, mml1, m}, agree_deny_mml1_u{agree_deny, mml1, u}
  - cr_nmatch_low = cp_nmatch x cp_low_idx: bins two_r0{two, r0}, two_r1_7{two, r1_7}, two_r8_14{two, r8_14}, three_r0{three, r0}, three_r1_7{three, r1_7}, three_r8_14{three, r8_14}, four_plus_r0{four_plus, r0}, four_plus_r1_7{four_plus, r1_7}, four_plus_r8_14{four_plus, r8_14}
- Adopted (riscv-dv): none
- TP items: TP-PMP-043, TP-PMP-044, TP-PMP-045, TP-PMP-100, TP-PMP-101, TP-PMP-102, TP-PMP-110

### CG-PMP-007: gen_cg_pmp_boundary
- Features: F-PMP-014, F-PMP-035, F-PMP-036, F-PMP-037, F-PMP-038, F-PMP-040, F-PMP-041, F-PMP-043,
  F-PMP-044, F-PMP-048, F-PMP-002 (parent of folded bins hosted here)
- Sample: a CG-PMP-005 check event for which the model identifies a reference region: the deciding region on match, else the enabled region whose first or last byte lies within one granule (2^(PMPGranularity+2) bytes) of the access bytes (nomatch case); condition: such a region exists and has at least one byte in the 32-bit space; anti-vacuity: accesses far from any region edge never sample; a hit proves an access at or across an exact region edge of that mode and the verdict matched the model
- Coverpoints:
  - cp_mode = reference region A field: bins tor{PMP_MODE_TOR}, na4{PMP_MODE_NA4}, napot{PMP_MODE_NAPOT}
  - cp_bclass = position of the access bytes relative to the reference region: bins inside_low{first access byte == region first byte (takes precedence when both edges are touched)}, inside_high{last access byte == region last byte and not inside_low}, interior{strictly inside, touching neither edge}, outside_low{last access byte == region first byte - 1}, outside_high{first access byte == region last byte + 1}, straddle_low{access bytes span the region's lower edge (split misaligned data or i32 at 4n+2)}, straddle_high{access bytes span the region's upper edge}
  - cp_type = access type: bins fetch{fetch}, load{load}, store{store}
  - cp_size = access size: bins b8{byte}, h16{halfword}, w32{word}, c16{compressed fetch}, i32{32-bit fetch}
  - cp_napot_k = iff napot: trailing-ones count k of pmpaddr, region size 2^(3+k) bytes: bins k0{8 B}, k1{16 B}, k2{32 B}, k3_7{64 B .. 1 KiB}, k8_17{2 KiB .. 1 MiB}, k18_28{2 MiB .. 2 GiB}, k29{4 GiB, pmpaddr 0x1FFFFFFF: region == the 32-bit space}, k30{8 GiB, pmpaddr 0x3FFFFFFF: base 0}, k31{16 GiB, pmpaddr 0x7FFFFFFF: base 0}, k32{all ones, pmpaddr 0xFFFFFFFF: base 0}
  - cp_tor_zero = iff tor: reference region is entry 0 (lower bound 0): bins no{i > 0}, yes{i == 0}
  - cp_tor_empty = iff tor: pmpaddr(i-1) vs pmpaddr(i): bins nonempty{pmpaddr(i-1) < pmpaddr(i)}; ignore_bins empty_eq{pmpaddr(i-1) == pmpaddr(i)}: an empty region has no edge byte and never matches, so it is never the reference region under this group's condition; covered by CG-PMP-015 (S-7); ignore_bins empty_gt{pmpaddr(i-1) > pmpaddr(i)}: same as empty_eq; CG-PMP-015
  - cp_hi = pmpaddr bits 31:30 (physical 33:32) set on the region bound: bins none{start and bound below 2^32}, bound_hi30{TOR upper bound pmpaddr(i) bit 30 set: the region covers every 32-bit address >= start}, bound_hi31{TOR upper bound pmpaddr(i) bit 31 set}; ignore_bins base_hi30{region start bit 30 set}: a region whose start lies above 2^32 has no byte in the 32-bit space and never matches; unsamplable here; covered by CG-PMP-015 (S-7); ignore_bins base_hi31{region start bit 31 set}: same as base_hi30; CG-PMP-015
  - cp_prev_cfg = iff tor and i > 0: entry i-1 state: bins prev_off{A == PMP_MODE_OFF}, prev_tor{A == PMP_MODE_TOR}, prev_na{A == PMP_MODE_NA4 or PMP_MODE_NAPOT: sampled on the inside_high / interior / outside probes; the inside_low word pmpaddr(i-1)*4 is decided by entry i-1 itself (anchored at pmpaddr(i-1), rtl/ibex_pmp.sv:163-164; fact-check X-20, TP-PMP-038)}, prev_locked{L == 1 (any A)}
- Crosses:
  - cr_mode_bclass = cp_mode x cp_bclass: bins tor_inside_low{PMP_MODE_TOR, inside_low}, tor_inside_high{PMP_MODE_TOR, inside_high}, tor_interior{PMP_MODE_TOR, interior}, tor_outside_low{PMP_MODE_TOR, outside_low}, tor_outside_high{PMP_MODE_TOR, outside_high}, tor_straddle_low{PMP_MODE_TOR, straddle_low}, tor_straddle_high{PMP_MODE_TOR, straddle_high}, na4_inside_low{PMP_MODE_NA4, inside_low}, na4_inside_high{PMP_MODE_NA4, inside_high}, na4_interior{PMP_MODE_NA4, interior}, na4_outside_low{PMP_MODE_NA4, outside_low}, na4_outside_high{PMP_MODE_NA4, outside_high}, na4_straddle_low{PMP_MODE_NA4, straddle_low}, na4_straddle_high{PMP_MODE_NA4, straddle_high}, napot_inside_low{PMP_MODE_NAPOT, inside_low}, napot_inside_high{PMP_MODE_NAPOT, inside_high}, napot_interior{PMP_MODE_NAPOT, interior}, napot_outside_low{PMP_MODE_NAPOT, outside_low}, napot_outside_high{PMP_MODE_NAPOT, outside_high}, napot_straddle_low{PMP_MODE_NAPOT, straddle_low}, napot_straddle_high{PMP_MODE_NAPOT, straddle_high}
  - cr_mode_bclass_type = cp_mode x cp_bclass x cp_type: bins tor_inside_low_fetch{PMP_MODE_TOR, inside_low, fetch}, tor_inside_low_load{PMP_MODE_TOR, inside_low, load}, tor_inside_low_store{PMP_MODE_TOR, inside_low, store}, tor_inside_high_fetch{PMP_MODE_TOR, inside_high, fetch}, tor_inside_high_load{PMP_MODE_TOR, inside_high, load}, tor_inside_high_store{PMP_MODE_TOR, inside_high, store}, tor_interior_fetch{PMP_MODE_TOR, interior, fetch}, tor_interior_load{PMP_MODE_TOR, interior, load}, tor_interior_store{PMP_MODE_TOR, interior, store}, tor_outside_low_fetch{PMP_MODE_TOR, outside_low, fetch}, tor_outside_low_load{PMP_MODE_TOR, outside_low, load}, tor_outside_low_store{PMP_MODE_TOR, outside_low, store}, tor_outside_high_fetch{PMP_MODE_TOR, outside_high, fetch}, tor_outside_high_load{PMP_MODE_TOR, outside_high, load}, tor_outside_high_store{PMP_MODE_TOR, outside_high, store}, tor_straddle_low_fetch{PMP_MODE_TOR, straddle_low, fetch}, tor_straddle_low_load{PMP_MODE_TOR, straddle_low, load}, tor_straddle_low_store{PMP_MODE_TOR, straddle_low, store}, tor_straddle_high_fetch{PMP_MODE_TOR, straddle_high, fetch}, tor_straddle_high_load{PMP_MODE_TOR, straddle_high, load}, tor_straddle_high_store{PMP_MODE_TOR, straddle_high, store}, na4_inside_low_fetch{PMP_MODE_NA4, inside_low, fetch}, na4_inside_low_load{PMP_MODE_NA4, inside_low, load}, na4_inside_low_store{PMP_MODE_NA4, inside_low, store}, na4_inside_high_fetch{PMP_MODE_NA4, inside_high, fetch}, na4_inside_high_load{PMP_MODE_NA4, inside_high, load}, na4_inside_high_store{PMP_MODE_NA4, inside_high, store}, na4_interior_fetch{PMP_MODE_NA4, interior, fetch}, na4_interior_load{PMP_MODE_NA4, interior, load}, na4_interior_store{PMP_MODE_NA4, interior, store}, na4_outside_low_fetch{PMP_MODE_NA4, outside_low, fetch}, na4_outside_low_load{PMP_MODE_NA4, outside_low, load}, na4_outside_low_store{PMP_MODE_NA4, outside_low, store}, na4_outside_high_fetch{PMP_MODE_NA4, outside_high, fetch}, na4_outside_high_load{PMP_MODE_NA4, outside_high, load}, na4_outside_high_store{PMP_MODE_NA4, outside_high, store}, na4_straddle_low_fetch{PMP_MODE_NA4, straddle_low, fetch}, na4_straddle_low_load{PMP_MODE_NA4, straddle_low, load}, na4_straddle_low_store{PMP_MODE_NA4, straddle_low, store}, na4_straddle_high_fetch{PMP_MODE_NA4, straddle_high, fetch}, na4_straddle_high_load{PMP_MODE_NA4, straddle_high, load}, na4_straddle_high_store{PMP_MODE_NA4, straddle_high, store}, napot_inside_low_fetch{PMP_MODE_NAPOT, inside_low, fetch}, napot_inside_low_load{PMP_MODE_NAPOT, inside_low, load}, napot_inside_low_store{PMP_MODE_NAPOT, inside_low, store}, napot_inside_high_fetch{PMP_MODE_NAPOT, inside_high, fetch}, napot_inside_high_load{PMP_MODE_NAPOT, inside_high, load}, napot_inside_high_store{PMP_MODE_NAPOT, inside_high, store}, napot_interior_fetch{PMP_MODE_NAPOT, interior, fetch}, napot_interior_load{PMP_MODE_NAPOT, interior, load}, napot_interior_store{PMP_MODE_NAPOT, interior, store}, napot_outside_low_fetch{PMP_MODE_NAPOT, outside_low, fetch}, napot_outside_low_load{PMP_MODE_NAPOT, outside_low, load}, napot_outside_low_store{PMP_MODE_NAPOT, outside_low, store}, napot_outside_high_fetch{PMP_MODE_NAPOT, outside_high, fetch}, napot_outside_high_load{PMP_MODE_NAPOT, outside_high, load}, napot_outside_high_store{PMP_MODE_NAPOT, outside_high, store}, napot_straddle_low_fetch{PMP_MODE_NAPOT, straddle_low, fetch}, napot_straddle_low_load{PMP_MODE_NAPOT, straddle_low, load}, napot_straddle_low_store{PMP_MODE_NAPOT, straddle_low, store}, napot_straddle_high_fetch{PMP_MODE_NAPOT, straddle_high, fetch}, napot_straddle_high_load{PMP_MODE_NAPOT, straddle_high, load}, napot_straddle_high_store{PMP_MODE_NAPOT, straddle_high, store}
  - cr_napot_k_bclass = cp_napot_k x cp_bclass: bins k0_inside_low{k0 (8 B), inside_low}, k0_inside_high{k0 (8 B), inside_high}, k0_outside_low{k0 (8 B), outside_low}, k0_outside_high{k0 (8 B), outside_high}, k1_inside_low{k1 (16 B), inside_low}, k1_inside_high{k1 (16 B), inside_high}, k1_outside_low{k1 (16 B), outside_low}, k1_outside_high{k1 (16 B), outside_high}, k2_inside_low{k2 (32 B), inside_low}, k2_inside_high{k2 (32 B), inside_high}, k2_outside_low{k2 (32 B), outside_low}, k2_outside_high{k2 (32 B), outside_high}, k3_7_inside_low{k3_7 (64 B .. 1 KiB), inside_low}, k3_7_inside_high{k3_7 (64 B .. 1 KiB), inside_high}, k3_7_outside_low{k3_7 (64 B .. 1 KiB), outside_low}, k3_7_outside_high{k3_7 (64 B .. 1 KiB), outside_high}, k8_17_inside_low{k8_17 (2 KiB .. 1 MiB), inside_low}, k8_17_inside_high{k8_17 (2 KiB .. 1 MiB), inside_high}, k8_17_outside_low{k8_17 (2 KiB .. 1 MiB), outside_low}, k8_17_outside_high{k8_17 (2 KiB .. 1 MiB), outside_high}, k18_28_inside_low{k18_28 (2 MiB .. 2 GiB), inside_low}, k18_28_inside_high{k18_28 (2 MiB .. 2 GiB), inside_high}, k18_28_outside_low{k18_28 (2 MiB .. 2 GiB), outside_low}, k18_28_outside_high{k18_28 (2 MiB .. 2 GiB), outside_high}, k29_inside_low{k29 (4 GiB, pmpaddr 0x1FFFFFFF: region == the 32-bit space), inside_low}, k29_inside_high{k29 (4 GiB, pmpaddr 0x1FFFFFFF: region == the 32-bit space), inside_high}, k30_inside_low{k30 (8 GiB, pmpaddr 0x3FFFFFFF: base 0), inside_low}, k31_inside_low{k31 (16 GiB, pmpaddr 0x7FFFFFFF: base 0), inside_low}, k32_inside_low{k32 (all ones, pmpaddr 0xFFFFFFFF: base 0), inside_low}; ignore_bins k29_32_outside{k29 or k30 or k31 or k32, outside_low or outside_high}: the region covers the whole 32-bit space: no outside byte exists; ignore_bins k30_32_inside_high{k30 or k31 or k32, inside_high}: the region's last byte lies above 2^32 (34-bit region size >= 2^33); no 32-bit access reaches it (S-7); inside_low (address 0) stays samplable because the base is 0; ignore_bins k_interior_straddle{any k, interior or straddle_low or straddle_high}: not required here: interior/straddle bins are owned by cr_mode_bclass and cr_size_bclass
  - cr_tor_zero = cp_tor_zero x cp_bclass: bins zero_inside_low{yes, inside_low}, zero_inside_high{yes, inside_high}, zero_interior{yes, interior}, zero_outside_high{yes, outside_high}, zero_straddle_high{yes, straddle_high}; ignore_bins zero_outside_low{yes, outside_low}: no byte below address 0; ignore_bins zero_straddle_low{yes, straddle_low}: no byte below address 0
  - cr_hi_mode = cp_hi x cp_mode: bins tor_bound_hi30{bound_hi30, tor: matches every 32-bit address >= start}, tor_bound_hi31{bound_hi31, tor}; ignore_bins na_bound_hi{bound_hi30 or bound_hi31, na4 or napot}: NA modes have no separate bound; ignore_bins base_hi_any{base_hi30 or base_hi31, any mode}: see cp_hi: moved to CG-PMP-015.cr_hi_kind
  - cr_size_bclass = cp_size x cp_bclass: bins b8_inside_low{b8, inside_low}, b8_inside_high{b8, inside_high}, h16_inside_low{h16, inside_low}, h16_inside_high{h16, inside_high}, h16_straddle_low{h16, straddle_low}, h16_straddle_high{h16, straddle_high}, w32_inside_low{w32, inside_low}, w32_inside_high{w32, inside_high}, w32_straddle_low{w32, straddle_low: misaligned word (addr[1:0] != 0) spanning the edge}, w32_straddle_high{w32, straddle_high: misaligned word (addr[1:0] != 0) spanning the edge}, c16_inside_low{c16, inside_low}, c16_inside_high{c16, inside_high}, i32_inside_low{i32, inside_low}, i32_inside_high{i32, inside_high}, i32_straddle_low{i32, straddle_low}, i32_straddle_high{i32, straddle_high}; ignore_bins b8_c16_straddle{b8 or c16, straddle_low or straddle_high}: a single-granule access cannot straddle an edge (S-7); ignore_bins size_other{any size, interior or outside_low or outside_high}: not required here: owned by cr_mode_bclass
  - cr_prev_cfg = cp_mode x cp_prev_cfg: bins tor_prev_off{tor, prev_off: the TOR match ignores pmpcfg(i-1)}, tor_prev_tor{tor, prev_tor: the TOR match ignores pmpcfg(i-1)}, tor_prev_na{tor, prev_na: the TOR match ignores pmpcfg(i-1)}, tor_prev_locked{tor, prev_locked: the TOR match ignores pmpcfg(i-1)}
  - cr_na4_size = cp_mode x cp_size x cp_bclass: bins na4_b8_inside_low{na4, b8, inside_low}, na4_b8_inside_high{na4, b8, inside_high}, na4_b8_interior{na4, b8 at word+1 or word+2, interior}, na4_h16_inside_low{na4, h16 at word+0, inside_low}, na4_h16_inside_high{na4, h16 at word+2, inside_high}, na4_h16_interior{na4, misaligned h16 at word+1, interior}, na4_w32_inside_low{na4, aligned w32: fills the region, sampled as inside_low}; ignore_bins na4_w32_inside_high{na4, w32, inside_high}: an aligned word touches both edges and is sampled as inside_low; a misaligned word is split and straddles; ignore_bins na4_w32_interior{na4, w32, interior}: a word access cannot lie strictly inside a 4-byte region (S-7)
- Adopted (riscv-dv): none
- TP items: TP-PMP-033, TP-PMP-034, TP-PMP-035, TP-PMP-036, TP-PMP-038, TP-PMP-039, TP-PMP-041, TP-PMP-042, TP-PMP-065, TP-PMP-084, TP-PMP-103

### CG-PMP-008: gen_cg_pmp_data_fault
- Features: F-PMP-071, F-PMP-082, F-PMP-083, F-PMP-084, F-PMP-085, F-PMP-086, F-PMP-087, F-PMP-088, F-PMP-089, F-PMP-090, F-PMP-091
- Sample: rvfi_valid of a load/store instruction for which the model predicts a PMP denial on at least one word, or whose access is split misaligned (word at offset 1/2/3, halfword at offset 3); condition: one of the two; anti-vacuity: aligned permitted accesses never sample; a hit proves a denied or split data access was checked for bus activity (data_req_o count), trap cause and mtval readback
- Coverpoints:
  - cp_type = load or store: bins load{rvfi_mem_rmask != 0}, store{rvfi_mem_wmask != 0}
  - cp_align = split / denial pattern: bins aligned_denied{single word, denied}, mis_none{split, both words allowed}, mis_first{split, first word denied only}, mis_second{split, second word denied only}, mis_both{split, both words denied}
  - cp_size = access size: bins b8{byte}, h16{halfword}, w32{word}
  - cp_cause = rvfi_trap and mcause readback: bins none{rvfi_trap == 0}, c5{load access fault}, c7{store access fault}
  - cp_mtval = iff trap: mtval readback class: bins ea{the original (unaligned) effective address}, second_word{the word-aligned second address}
  - cp_nreq = data_req_o & data_gnt_i handshakes attributed to the instruction: bins n0{0}, n1{1}, n2{2}
  - cp_eff_priv = mstatus.MPRV ? MPP : rvfi_mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_mprv = mstatus.MPRV: bins mprv0{0}, mprv1{1}
  - cp_rd = loads: rvfi_rd_addr != 0 with a register write: bins none{no rd write}, written{rd written}
  - cp_buserr = data_err_i on the first-half response: bins none{0}, first_half_err{1}
  - cp_next_exc = exception class of the following instruction while this one faults in WB: bins none{no exception in ID}, fetch_fault{PMP-denied fetch in ID}, illegal{illegal instruction in ID}, ecall_ebreak{ecall or ebreak in ID}
  - cp_lat = cycles from the LSU request to lsu_resp_valid for aligned_denied [probe-gated, not in manifest]: bins lat2{2}, other{!= 2}
- Crosses:
  - cr_align_type = cp_align x cp_type: bins aligned_denied_load{aligned_denied, load}, aligned_denied_store{aligned_denied, store}, mis_none_load{mis_none, load}, mis_none_store{mis_none, store}, mis_first_load{mis_first, load}, mis_first_store{mis_first, store}, mis_second_load{mis_second, load}, mis_second_store{mis_second, store}, mis_both_load{mis_both, load}, mis_both_store{mis_both, store}
  - cr_align_mtval = cp_align x cp_mtval: bins aligned_denied_ea{aligned_denied, ea}, mis_first_ea{mis_first, ea: a first-half fault keeps the original EA}, mis_second_second_word{mis_second, second_word}, mis_both_ea{mis_both, ea}; ignore_bins mis_first_second_word{mis_first, second_word}: addr_update is blocked by pmp_err_q (rtl/ibex_load_store_unit.sv); ignore_bins aligned_denied_second_word{aligned_denied, second_word}: no second word; ignore_bins mis_second_ea{mis_second, ea}: a second-half fault records the aligned second address (F-PMP-088)
  - cr_align_nreq = cp_align x cp_nreq: bins aligned_denied_n0{aligned_denied, n0: no bus transaction}, mis_none_n2{mis_none, n2}, mis_first_n1{mis_first, n1: the second half is still issued (MEM-13, Q-DL-7)}, mis_second_n1{mis_second, n1: the first half is performed}, mis_both_n0{mis_both, n0}; ignore_bins nreq_other{any other combination}: contradicts MEM-13; gen_chk_pmp / gen_chk_dbus_proto fail first
  - cr_half_align = cp_size x cp_align x cp_type: bins h16_mis_none_load{h16 at offset 3, mis_none, load}, h16_mis_none_store{h16 at offset 3, mis_none, store}, h16_mis_first_load{h16 at offset 3, mis_first, load}, h16_mis_first_store{h16 at offset 3, mis_first, store}, h16_mis_second_load{h16 at offset 3, mis_second, load}, h16_mis_second_store{h16 at offset 3, mis_second, store}, h16_mis_both_load{h16 at offset 3, mis_both, load}, h16_mis_both_store{h16 at offset 3, mis_both, store}; ignore_bins b8_mis{b8, mis_none or mis_first or mis_second or mis_both, any}: bytes never split
  - cr_buserr = cp_buserr x cp_align x cp_type x cp_mtval: bins buserr_mis_second_load_ea{first_half_err, mis_second, load, ea}, buserr_mis_second_store_ea{first_half_err, mis_second, store, ea}
  - cr_priority = cp_cause x cp_next_exc: bins c5_fetch_fault{c5, fetch_fault: the WB fault outranks the ID exception}, c5_illegal{c5, illegal: the WB fault outranks the ID exception}, c5_ecall_ebreak{c5, ecall_ebreak: the WB fault outranks the ID exception}, c7_fetch_fault{c7, fetch_fault: the WB fault outranks the ID exception}, c7_illegal{c7, illegal: the WB fault outranks the ID exception}, c7_ecall_ebreak{c7, ecall_ebreak: the WB fault outranks the ID exception}
  - cr_priv_cause = cp_mprv x cp_eff_priv x cp_cause: bins mprv0_m_c5{mprv0, m, c5}, mprv0_m_c7{mprv0, m, c7}, mprv0_u_c5{mprv0, u, c5}, mprv0_u_c7{mprv0, u, c7}, mprv1_m_c5{mprv1, m, c5}, mprv1_m_c7{mprv1, m, c7}, mprv1_u_c5{mprv1, u, c5}, mprv1_u_c7{mprv1, u, c7}
  - cr_rd = cp_type x cp_cause x cp_rd: bins load_c5_none{load, c5, none: a denied load writes no rd}; ignore_bins load_c5_written{load, c5, written}: contradicts F-PMP-083; gen_isa_compare fails first
  - cr_lat = cp_align x cp_lat [probe-gated, not in manifest]: bins aligned_denied_lat2{aligned_denied, lat2}
- Adopted (riscv-dv): none
- TP items: TP-PMP-069, TP-PMP-070, TP-PMP-071, TP-PMP-080, TP-PMP-081, TP-PMP-082, TP-PMP-083, TP-PMP-084, TP-PMP-085, TP-PMP-086, TP-PMP-087, TP-PMP-088, TP-PMP-089, TP-PMP-103

### CG-PMP-009: gen_cg_pmp_fetch_fault
- Features: F-PMP-053, F-PMP-055, F-PMP-065, F-PMP-066, F-PMP-067, F-PMP-068, F-PMP-069, F-PMP-070,
  F-PMP-078, F-PMP-080, F-PMP-081, F-PMP-093, F-PMP-094, F-PMP-052 (parent of folded bins hosted
  here)
- Sample: rvfi_valid per instruction where the model predicts a fetch denial on pc or pc+2, or the instruction is uncompressed at pc[1] == 1 with a region edge at pc+2, or the instruction is a control-flow target whose word is a region edge; condition: one of the three; anti-vacuity: ordinary permitted sequential instructions never sample; a hit proves a fetch-side PMP decision with the named half pattern was checked for trap, mtval and mepc
- Coverpoints:
  - cp_pc_align = rvfi_pc_rdata[1:0]: bins a4{00}, a2{10}
  - cp_ilen = instruction length: bins c16{compressed}, i32{uncompressed}
  - cp_halves = model verdict per fetched half: bins single_allow{aligned or c16: the single word allowed}, single_deny{aligned or c16: the single word denied}, both_allow{i32 at a2: both words allowed}, fd_sa{i32 at a2: first denied, second allowed}, fa_sd{i32 at a2: first allowed, second denied}, both_deny{i32 at a2: both denied}
  - cp_next_word_denied = iff c16 at a2: word pc+2 denied for EXEC: bins no{0}, yes{1}
  - cp_mtval = iff trap: mtval readback: bins pc{== pc}, pc2{== pc + 2}
  - cp_cause = rvfi_trap and mcause: bins none{rvfi_trap == 0}, c1{instruction access fault}
  - cp_buserr = instr_err_i on the fetch of this instruction: bins none{0}, first{first word}, second{second word}
  - cp_target = how pc was reached (from the previous RVFI record / trap entry): bins seq{sequential pc}, branch{taken branch target}, jump{jal/jalr target}, mret{mret target (mepc)}, exc_entry{trap vector}, dret{dret target (dpc)}
  - cp_priv = rvfi_mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_wrap = pc == 32'hFFFFFFFE: bins normal{0}, wrap{1}
  - cp_dummy_en = cpuctrlsts.dummy_instr_en (readback model): bins off{0}, on{1}
  - cp_src = where the instruction word came from: bins bus{an ibus grant of the word occurred since the last invalidation/branch}, cache_hit{no ibus grant of the word since the last invalidation: served by the icache (boundary inference; probe alternative listed)}
- Crosses:
  - cr_plus2 = cp_ilen x cp_pc_align x cp_halves x cp_mtval: bins fd_sa_pc{i32, a2, fd_sa, pc}, fa_sd_pc2{i32, a2, fa_sd, pc2: err_plus2}, both_deny_pc{i32, a2, both_deny, pc: the first-half error masks plus2}; ignore_bins fd_sa_pc2{i32, a2, fd_sa, pc2}: masked by ~pmp_err_if_i (rtl/ibex_if_stage.sv:434-435); ignore_bins both_deny_pc2{i32, a2, both_deny, pc2}: masked by ~pmp_err_if_i
  - cr_c16_a2 = cp_ilen x cp_pc_align x cp_next_word_denied x cp_cause: bins c16_a2_nextdenied_none{c16, a2, yes, none: a compressed instruction uses PMP_I only}; ignore_bins c16_a2_nextdenied_c1{c16, a2, yes, c1}: contradicts F-PMP-067
  - cr_target = cp_target x cp_cause: bins seq_c1{seq, c1: mepc == target pc}, branch_c1{branch, c1: mepc == target pc}, jump_c1{jump, c1: mepc == target pc}, mret_c1{mret, c1: mepc == target pc}, exc_entry_c1{exc_entry, c1: mepc == target pc}, dret_c1{dret, c1: mepc == target pc}
  - cr_buserr = cp_buserr x cp_halves x cp_mtval: bins bus_first_fd_sa_pc{first, fd_sa, pc}, bus_second_fd_sa_pc{second, fd_sa, pc: the bus err_plus2 is masked by the first-half PMP error}, bus_second_single_allow_pc2{second, both_allow, pc2: pure bus error path (IMEM area reference)}, bus_first_fa_sd_pc{first, fa_sd, pc: the first-half bus error wins}, bus_none_fa_sd_pc2{none, fa_sd, pc2}; ignore_bins bus_second_fd_sa_pc2{second, fd_sa, pc2}: masked by ~pmp_err_if_i
  - cr_wrap = cp_wrap x cp_ilen x cp_cause: bins wrap_i32_none{wrap, i32, none: word 0 allowed}, wrap_i32_c1{wrap, i32, c1: word 0 denied, mtval = pc + 2 = 0}
  - cr_dummy = cp_dummy_en x cp_cause x cp_pc_align: bins on_c1_a4{on, c1, a4}, on_c1_a2{on, c1, a2}
  - cr_src = cp_src x cp_cause: bins cache_hit_none{cache_hit, none: the cached line executed after PMP made it allowed}, cache_hit_c1{cache_hit, c1: the cached line faults after PMP made it denied}
  - cr_priv_cause = cp_priv x cp_cause x cp_ilen: bins m_c1_c16{m, c1, c16}, m_c1_i32{m, c1, i32}, u_c1_c16{u, c1, c16}, u_c1_i32{u, c1, i32}
  - cr_halves_priv = cp_halves x cp_priv: bins single_deny_m{single_deny, m}, single_deny_u{single_deny, u}, fd_sa_m{fd_sa, m}, fd_sa_u{fd_sa, u}, fa_sd_m{fa_sd, m}, fa_sd_u{fa_sd, u}, both_deny_m{both_deny, m}, both_deny_u{both_deny, u}
- Adopted (riscv-dv): none
- TP items: TP-PMP-051, TP-PMP-053, TP-PMP-063, TP-PMP-064, TP-PMP-065, TP-PMP-066, TP-PMP-067, TP-PMP-068, TP-PMP-076, TP-PMP-078, TP-PMP-079, TP-PMP-092, TP-PMP-093, TP-PMP-105

### CG-PMP-010: gen_cg_pmp_ibus_denied
- Features: F-PMP-066, F-PMP-079, F-PMP-092, F-PMP-093
- Sample: ibus monitor: instr_req_o & instr_gnt_i for a word that the model's PMP state at the grant cycle (CSR values and the privilege defined by cp_priv, M in debug) denies for EXEC; anti-vacuity: fetches into currently permitted words never sample; a hit proves that fetch is not gated by PMP (F-PMP-066) and records what became of the fetched word
- Coverpoints:
  - cp_outcome = fate of the granted word: bins retired_fault{an instruction from the word retires with mcause 1}, discarded{no instruction from the word retires before the next branch/redirect}, retired_ok_recfg{retires without trap: a PMP CSR write retired between the grant and the IF/ID handoff and allowed it (the CSR flush keeps the fetch FIFO: rtl/ibex_controller.sv:816-819 sets no PC, rtl/ibex_prefetch_buffer.sv:78)}; ignore_bins retired_ok_priv{retires without trap because the privilege changed between grant and handoff}: every privilege-changing event (mret, dret, trap entry, debug entry) sets the PC and clears the fetch FIFO (branch_i), so a word granted under the old privilege never reaches ID (S-7)
  - cp_priv = privilege in force for the word: rvfi_mode of the retire that consumes it; for a discarded word the mode after the most recent privilege-changing redirect before the grant (trap/mret/dret records back-dated by the 1-record offset, gen_tb_architecture.md 8.2): bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_flush_reason = iff discarded: the PC-setting redirect that cleared the fetch FIFO: bins branch{taken branch}, jump{jal/jalr}, exc{trap/mret/dret/debug-entry redirect}; ignore_bins csr_flush{a PMP CSR write alone}: a CSR flush retains the fetch FIFO (rtl/ibex_controller.sv:816-819 sets no PC; rtl/ibex_prefetch_buffer.sv:78 clears on branch_i only); a word is discarded only by a PC-setting redirect
  - cp_later_outcome = outcome of a later execution of the same word with no ibus grant (icache hit): bins none{no later execution without a grant}, hit_fault{later hit retires with mcause 1}, hit_ok{later hit retires without trap}
  - cp_later_cause = iff later hit_ok: what changed between the first encounter and the hit: bins recfg{a PMP CSR write}, priv{mret/dret/trap changed the privilege}
- Crosses:
  - cr_outcome_priv = cp_outcome x cp_priv: bins retired_fault_m{retired_fault, m}, retired_fault_u{retired_fault, u}, discarded_m{discarded, m}, discarded_u{discarded, u}, retired_ok_recfg_m{retired_ok_recfg, m}, retired_ok_recfg_u{retired_ok_recfg, u}
  - cr_discard_reason = cp_outcome x cp_flush_reason: bins discarded_branch{discarded, branch}, discarded_jump{discarded, jump}, discarded_exc{discarded, exc}
  - cr_hit_outcome = cp_outcome x cp_later_outcome: bins fault_then_hit_fault{retired_fault, hit_fault: denied line cached, still denied}, fault_then_hit_ok{retired_fault, hit_ok: denied line cached, later allowed}, discarded_then_hit_fault{discarded, hit_fault}, discarded_then_hit_ok{discarded, hit_ok}
  - cr_hit_cause = cp_later_outcome x cp_later_cause: bins hit_ok_recfg{hit_ok, recfg}, hit_ok_priv{hit_ok, priv}
- Adopted (riscv-dv): none
- TP items: TP-PMP-064, TP-PMP-077, TP-PMP-091, TP-PMP-092, TP-PMP-105

### CG-PMP-011: gen_cg_pmp_recfg
- Features: F-PMP-020, F-PMP-033, F-PMP-055, F-PMP-065, F-PMP-092, F-PMP-100, F-PMP-007 (parent of
  folded bins hosted here)
- Sample: RVFI retire of a PMP CSR write (pmpcfg*/pmpaddr*/mseccfg) with rvfi_trap == 0; the effect fields diff the model verdict for the next retired instruction's pc (and its load/store address) before and after the write; anti-vacuity: only PMP CSR writes sample; a hit on a now_denied/now_allowed bin proves the write flipped a live verdict and the next instruction's trap/no-trap was checked against the new state; cr_bb of the earlier draft was an identity cross and is retired: the pair outcome lives in the cp_bb bin predicates
- Coverpoints:
  - cp_csr = written CSR and changed field: bins pmpcfg{a pmpcfg field changed}, pmpaddr{a pmpaddr changed}, mseccfg_mml{MML 0->1}, mseccfg_mmwp{MMWP 0->1}, mseccfg_rlb{RLB changed}, mseccfg_none{mseccfg written, no bit changed}
  - cp_next_fetch = model verdict change for the next instruction's fetch: bins unchanged{same verdict}, now_denied{allow -> deny}, now_allowed{deny -> allow}
  - cp_next_data = model verdict change for the next load/store address: bins none{the next instruction is not a load/store}, unchanged{same verdict}, now_denied{allow -> deny}, now_allowed{deny -> allow}
  - cp_next_src = where the next instruction's word came from: bins bus_prefetched{ibus grant of the word precedes the write's retire; observable only with cpuctrlsts.icache_enable == 0 (the owning item pins it, S-4); the word survives the CSR flush (rtl/ibex_controller.sv:816-819, rtl/ibex_prefetch_buffer.sv:78) and is PMP-checked on pc_if at the IF/ID handoff}, cache_hit{no ibus grant of the word since the last invalidation (icache_enable == 1)}, fresh{ibus grant after the write retired}
  - cp_self = the write removes execute permission from the code that follows it: bins none{no self fault}, mmwp_self_fault{MMWP set while executing from an unmatched region}, mml_self_fault{MML set while executing from an L=0 or unmatched region}, cfg_self_fault{pmpcfg/pmpaddr change denies the following code}
  - cp_bb = back-to-back write pair (adjacent rvfi_order): bins none{no paired write}, lock_then_addr{csrw pmpcfg setting L on entry i then csrw pmpaddr(i): the second write is ignored (readback unchanged)}, lock_then_cfg{csrw pmpcfg setting L on entry i then csrw pmpcfg of the same word: entry i unchanged}, lock_then_rlb{csrw pmpcfg setting L then csrw mseccfg with RLB=1: RLB stays 0}, rlbclr_then_cfg{csrw mseccfg clearing RLB with locked entries present then csrw pmpcfg of a locked entry: ignored}, rlbclr_then_addr{csrw mseccfg clearing RLB with locked entries present then csrw pmpaddr of a locked entry (or below a locked TOR): ignored}
  - cp_gap = instructions between the write and the affected access: bins g0{0}, g1_3{1..3}, g4_plus{>= 4}
- Crosses:
  - cr_csr_fetch = cp_csr x cp_next_fetch: bins pmpcfg_now_denied{pmpcfg, now_denied}, pmpcfg_now_allowed{pmpcfg, now_allowed}, pmpaddr_now_denied{pmpaddr, now_denied}, pmpaddr_now_allowed{pmpaddr, now_allowed}, mseccfg_mml_now_denied{mseccfg_mml, now_denied}, mseccfg_mmwp_now_denied{mseccfg_mmwp, now_denied}; ignore_bins mseccfg_mmwp_now_allowed{mseccfg_mmwp, now_allowed}: MMWP only removes permission; ignore_bins mseccfg_mml_now_allowed{mseccfg_mml, now_allowed}: MML 0->1 never turns a fetch deny into allow for any storable row or the no-match rule (Appendix A vs B: RW=01 rows are not stored under MML=0), S-7
  - cr_csr_data = cp_csr x cp_next_data: bins pmpcfg_now_denied{pmpcfg, now_denied}, pmpcfg_now_allowed{pmpcfg, now_allowed}, pmpaddr_now_denied{pmpaddr, now_denied}, pmpaddr_now_allowed{pmpaddr, now_allowed}, mseccfg_mml_now_denied{mseccfg_mml, now_denied}, mseccfg_mmwp_now_denied{mseccfg_mmwp, now_denied}; ignore_bins mseccfg_mmwp_now_allowed{mseccfg_mmwp, now_allowed}: MMWP only removes permission; ignore_bins mseccfg_mml_now_allowed{mseccfg_mml, now_allowed}: MML 0->1 never turns a data deny into allow (Appendix A vs B), S-7
  - cr_src_fetch = cp_next_src x cp_next_fetch: bins bus_prefetched_now_denied{bus_prefetched, now_denied}, bus_prefetched_now_allowed{bus_prefetched, now_allowed}, cache_hit_now_denied{cache_hit, now_denied}, cache_hit_now_allowed{cache_hit, now_allowed}, fresh_now_denied{fresh, now_denied}, fresh_now_allowed{fresh, now_allowed}
  - cr_self = cp_self x cp_gap: bins mmwp_self_fault_g0{mmwp_self_fault, g0: the next instruction traps with mcause 1}, mml_self_fault_g0{mml_self_fault, g0: the next instruction traps with mcause 1}, cfg_self_fault_g0{cfg_self_fault, g0: the next instruction traps with mcause 1}
  - cr_gap_fetch = cp_gap x cp_next_fetch: bins g0_now_denied{g0, now_denied}, g1_3_now_denied{g1_3, now_denied}, g4_plus_now_denied{g4_plus, now_denied}
- Adopted (riscv-dv): none
- TP items: TP-PMP-020, TP-PMP-031, TP-PMP-053, TP-PMP-063, TP-PMP-090, TP-PMP-091, TP-PMP-092, TP-PMP-109, TP-PMP-112

### CG-PMP-012: gen_cg_pmp_priv_mprv
- Features: F-PMP-072, F-PMP-073, F-PMP-074, F-PMP-075, F-PMP-076, F-PMP-077
- Sample: a CG-PMP-005 check event (its condition included) for which a privilege-redirection source is live: mstatus.MPRV == 1, or rvfi_ext_debug_mode == 1, or the access is the first fetch / first data access after a privilege-entry event (mret, dret, trap entry, debug entry, reset), or the last mstatus write carried an illegal MPP; anti-vacuity (S-3): M-mode accesses with MPRV=0 outside debug that do not immediately follow a privilege-entry event never sample; a hit on an mprv1 bin proves an access was checked under MPRV redirection and its verdict compared to the model's effective privilege; expected-fail items TP-PMP-073/074 own only observed-RTL-outcome bins (dret_u_kept_rtl, dbg_mprv_mppu_*_fault); the spec-outcome bins are ignore_bins; a "U-denied / M-allowed window" is one per tp_pmp.md C-PMP-MONLY (unmatched with MMWP=0 or a matching L=0 RWX=000 entry under MML=0, LRWX=1110 under MML=1; never L=1 RW under MML=0, whose L bit is ignored for U, rtl/ibex_pmp.sv:101-110; fact-check X-20)
- Coverpoints:
  - cp_type = access type: bins fetch{fetch}, load{load}, store{store}
  - cp_cur = rvfi_mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_mprv = mstatus.MPRV (readback model): bins mprv0{0}, mprv1{1}
  - cp_mpp = mstatus.MPP (legal values; illegal writes are stored as U): bins u{PRIV_LVL_U}, m{PRIV_LVL_M}
  - cp_mpp_wr_illegal = the last mstatus write carried MPP in {01, 10}: bins no{0}, yes{1}
  - cp_eff = model effective privilege: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_dbg = rvfi_ext_debug_mode: bins d0{0}, d1{1}
  - cp_entry = iff first access after a privilege-entry event: how the current privilege was entered: bins mret_u{mret with MPP=U}, mret_m{mret with MPP=M}, dret_u{dret with dcsr.prv=U}, dret_m{dret with dcsr.prv=M}, exc_m{trap entry}, reset_m{reset}, dbg_entry{debug entry}
  - cp_mprv_after = iff first data access after an xRET: MPRV state inferred from the access verdict (see Probe candidates): bins mret_u_cleared{after mret to U with MPRV=1 at the mret: the first U load/store to a U-denied/M-allowed window traps (cause 5/7): MPRV cleared}, mret_m_kept{after mret staying in M with MPRV=1: the first load/store is checked with MPP (= U after mret): a U-denied/M-allowed window traps}, dret_u_kept_rtl{after dret to U with MPRV=1 and MPP=M at the dret: the first U load/store to a U-denied/M-allowed window retires rvfi_trap == 0 (B1 observed RTL outcome; rtl/ibex_cs_registers.sv:949-951)}, dret_m_kept{after dret to M with MPRV=1 and MPP=U: the first load/store is checked as U (a U-denied/M-allowed window traps)}; ignore_bins dret_u_cleared_spec{after dret to U with MPRV=1: the first U load/store to a U-denied/M-allowed window traps (Sdext resume rule)}: the spec outcome of bug candidate B1; the RTL cannot produce it while B1 stands (M-03); re-enable when the RTL fix lands
  - cp_uvm = model verdicts for the word under U and under M: bins same{U and M verdicts equal}, u_deny_m_allow{U denied, M allowed}, u_allow_m_deny{U allowed, M denied}
  - cp_obs = observed RTL outcome: bins ok{rvfi_trap == 0}, fault{rvfi_trap == 1 (in debug mode: next fetch at DmExceptionAddr)}
- Crosses:
  - cr_eff = cp_cur x cp_mprv x cp_mpp x cp_type x cp_eff: bins m_mprv_mppu_load_effu{m, mprv1, u, load, u}, m_mprv_mppu_store_effu{m, mprv1, u, store, u}, m_mprv_mppu_fetch_effm{m, mprv1, u, fetch, m: fetch is never redirected}, m_mprv_mppm_load_effm{m, mprv1, m, load, m}, m_mprv_mppm_store_effm{m, mprv1, m, store, m}, m_mprv_mppm_fetch_effm{m, mprv1, m, fetch, m}; ignore_bins fetch_effu{m, any, any, fetch, u}: priv_mode_id is used for fetch (rtl/ibex_core.sv:1600)
  - cr_dbg_mprv = cp_dbg x cp_mprv x cp_mpp x cp_type x cp_uvm x cp_obs: bins dbg_mprv_mppu_load_fault{d1, mprv1, u, load, u_deny_m_allow, fault: B2 observed RTL outcome (checked as U outside the DM window; spec mprven=0 predicts ok)}, dbg_mprv_mppu_store_fault{d1, mprv1, u, store, u_deny_m_allow, fault: B2 observed RTL outcome}; ignore_bins dbg_mprv_mppu_ok{d1, mprv1, u, load or store, u_deny_m_allow, ok}: the Sdext mprven=0 outcome of bug candidate B2; unreachable while B2 stands (M-03); re-enable on the RTL fix
  - cr_after_ret = cp_mprv_after x cp_type: bins mret_u_cleared_load{mret_u_cleared, load}, mret_u_cleared_store{mret_u_cleared, store}, mret_m_kept_load{mret_m_kept, load}, mret_m_kept_store{mret_m_kept, store}, dret_u_kept_rtl_load{dret_u_kept_rtl, load}, dret_u_kept_rtl_store{dret_u_kept_rtl, store}, dret_m_kept_load{dret_m_kept, load}, dret_m_kept_store{dret_m_kept, store}; ignore_bins dret_u_cleared_spec_x{dret_u_cleared_spec, load or store}: see cp_mprv_after (B1 spec outcome)
  - cr_u_entry = cp_cur x cp_entry x cp_type: bins u_mret_u_fetch{u, mret_u, fetch: first fetch of the U episode}, u_mret_u_load{u, mret_u, load: first load of the U episode}, u_mret_u_store{u, mret_u, store: first store of the U episode}, u_dret_u_fetch{u, dret_u, fetch: first fetch of the U episode}, u_dret_u_load{u, dret_u, load: first load of the U episode}, u_dret_u_store{u, dret_u, store: first store of the U episode}
  - cr_illegal_mpp = cp_mpp_wr_illegal x cp_mprv x cp_type x cp_eff: bins illegal_mpp_mprv_load_effu{yes, mprv1, load, u: RTL stores U (doc mismatch D2)}, illegal_mpp_mprv_store_effu{yes, mprv1, store, u}
- Adopted (riscv-dv): none
- TP items: TP-PMP-010, TP-PMP-070, TP-PMP-071, TP-PMP-072, TP-PMP-073, TP-PMP-074, TP-PMP-075, TP-PMP-080, TP-PMP-094, TP-PMP-102

### CG-PMP-013: gen_cg_pmp_debug
- Features: F-PMP-017, F-PMP-095, F-PMP-096, F-PMP-097, F-PMP-098, F-PMP-099
- Sample: a CG-PMP-005 check event (its condition included) while rvfi_ext_debug_mode == 1, or any check event (in or out of debug) whose address satisfies (addr & ~DmAddrMask) == DmBaseAddr; mstatus.MPRV is 0 during the sampled debug episodes (B2 isolation: the owning items pin it; MPRV=1 debug episodes belong to CG-PMP-012.cr_dbg_mprv); anti-vacuity: non-debug accesses outside the DM window never sample; a hit proves a debug-mode or DM-window PMP interaction was checked
- Coverpoints:
  - cp_dbg = rvfi_ext_debug_mode: bins d0{0}, d1{1}
  - cp_in_dm = (addr & ~DmAddrMask) == DmBaseAddr: bins no{0}, yes{1}
  - cp_type = access type: bins fetch{fetch}, load{load}, store{store}
  - cp_normal = verdict the non-debug rules would give: bins allow{allow}, deny{deny}
  - cp_verdict = model verdict (MPRV pinned to 0 in the owning items, so model == RTL): bins allow{allow}, deny{deny}
  - cp_mseccfg = mseccfg state: bins none{MML=0, MMWP=0}, mmwp{MMWP=1 only}, mml{MML=1 only}, both{MML=1 and MMWP=1}
  - cp_dm_top_i32 = uncompressed instruction at DmBaseAddr + DmAddrMask - 1 (pc+2 outside the window): bins no{0}, yes{1}
  - cp_phase = position in the debug episode: bins halt_fetch{first fetch at DmHaltAddr after entry}, body{any other debug-mode access}, exc_fetch{fetch at DmExceptionAddr}, post_dret_first{first non-debug fetch after dret}
  - cp_csr_side = mcause/mepc/mtval readback after a debug-mode PMP fault: bins unchanged{== preloaded values}; ignore_bins changed{!= preloaded values}: contradicts Sdext (debug-mode exceptions update no trap CSRs); gen_chk_debug fails first
- Crosses:
  - cr_bypass = cp_dbg x cp_in_dm x cp_normal x cp_type x cp_verdict: bins bypass_fetch{d1, yes, deny, fetch, allow: DM window bypass}, bypass_load{d1, yes, deny, load, allow: DM window bypass}, bypass_store{d1, yes, deny, store, allow: DM window bypass}; ignore_bins bypass_x_deny{d1, yes, deny, any, deny}: the bypass is unconditional in debug mode (CTRL-34)
  - cr_no_bypass = cp_dbg x cp_in_dm x cp_normal x cp_type x cp_verdict: bins nodbg_dm_fetch_deny{d0, yes, deny, fetch, deny}, nodbg_dm_load_deny{d0, yes, deny, load, deny}, nodbg_dm_store_deny{d0, yes, deny, store, deny}
  - cr_dbg_outside = cp_dbg x cp_in_dm x cp_normal x cp_type x cp_verdict: bins dbg_out_fetch_deny{d1, no, deny, fetch, deny: exception in debug mode -> DmExceptionAddr}, dbg_out_load_deny{d1, no, deny, load, deny: exception in debug mode -> DmExceptionAddr}, dbg_out_store_deny{d1, no, deny, store, deny: exception in debug mode -> DmExceptionAddr}
  - cr_dbg_outside_mseccfg = cp_dbg x cp_in_dm x cp_mseccfg x cp_verdict: bins mmwp_allow{d1, no, mmwp, allow}, mmwp_deny{d1, no, mmwp, deny}, mml_allow{d1, no, mml, allow}, mml_deny{d1, no, mml, deny}, both_allow{d1, no, both, allow}, both_deny{d1, no, both, deny}
  - cr_dm_top = cp_dm_top_i32 x cp_mseccfg x cp_verdict: bins dm_top_mmwp_deny{yes, mmwp, deny: PMP_I2 checked outside the window}, dm_top_mml_deny{yes, mml, deny: PMP_I2 checked outside the window}, dm_top_both_deny{yes, both, deny: PMP_I2 checked outside the window}
  - cr_phase = cp_phase x cp_verdict: bins halt_fetch_allow{halt_fetch, allow}, body_allow{body, allow}, body_deny{body, deny}, exc_fetch_allow{exc_fetch, allow}, post_dret_first_allow{post_dret_first, allow}, post_dret_first_deny{post_dret_first, deny}; ignore_bins exc_fetch_deny{exc_fetch, deny}: DmExceptionAddr lies inside the bypassed DM window; ignore_bins halt_fetch_deny{halt_fetch, deny}: DmHaltAddr (0x1A110800) lies inside the bypassed DM window (DmBaseAddr 0x1A110000, DmAddrMask 0xFFF; CTRL-34), S-7
  - cr_csr_side = cp_dbg x cp_verdict x cp_csr_side: bins dbg_deny_unchanged{d1, deny, unchanged}; ignore_bins dbg_deny_changed{d1, deny, changed}: contradicts Sdext; gen_chk_debug fails first
  - cr_bypass_mseccfg = cp_dbg x cp_in_dm x cp_mseccfg x cp_type: bins none_fetch{d1, yes, none, fetch}, none_load{d1, yes, none, load}, none_store{d1, yes, none, store}, mmwp_fetch{d1, yes, mmwp, fetch}, mmwp_load{d1, yes, mmwp, load}, mmwp_store{d1, yes, mmwp, store}, mml_fetch{d1, yes, mml, fetch}, mml_load{d1, yes, mml, load}, mml_store{d1, yes, mml, store}, both_fetch{d1, yes, both, fetch}, both_load{d1, yes, both, load}, both_store{d1, yes, both, store}
- Adopted (riscv-dv): none
- TP items: TP-PMP-094, TP-PMP-095, TP-PMP-096, TP-PMP-097, TP-PMP-098, TP-PMP-099, TP-PMP-104

### CG-PMP-014: gen_cg_pmp_table_state
- Features: F-PMP-015, F-PMP-042, F-PMP-046, F-PMP-047, F-PMP-053, F-PMP-056, F-PMP-052 (parent of
  folded bins hosted here)
- Sample: RVFI retire of any PMP CSR write (snapshot of the table after the write) and at each regime phase start; condition: at least one instruction retires before the next table change (otherwise the sample is discarded); anti-vacuity: only table changes sample; a hit proves a live configuration with the named shape was run under
- Coverpoints:
  - cp_active = entries with A != PMP_MODE_OFF: bins n0{0}, n1{1}, n2_4{2..4}, n5_8{5..8}, n9_15{9..PMPNumRegions-1}, n16{PMPNumRegions}
  - cp_locked = entries with L == 1: bins n0{0}, n1_4{1..4}, n5_15{5..PMPNumRegions-1}, n16{PMPNumRegions}
  - cp_modes = modes present among active entries: bins none{no active entry}, tor_only{only PMP_MODE_TOR}, na_only{only NA4/NAPOT}, mixed{TOR and NA4/NAPOT}
  - cp_tor_empty = active TOR entries with pmpaddr(i-1) >= pmpaddr(i): bins none{0}, some{>= 1}
  - cp_overlap = pairs of active regions with overlapping byte ranges: bins none{0}, some{>= 1}
  - cp_regime = knob:pmp_regime (cross operand only; the knob-value bins are owned by fcov_xcut CG-REG, S-5) [operand-only]: bins off{off}, sparse{sparse}, dense{dense}, mml_on{mml_on}
  - cp_all_off_u = all entries OFF and a U-mode access follows before the next table change: bins no{0}, yes{1: every U access faults; cr_all_off_u of the earlier draft was an identity cross and is retired}
  - cp_e15 = entry PMPNumRegions-1: bins off{A == PMP_MODE_OFF}, active{A != PMP_MODE_OFF}
  - cp_e0_tor = entry 0 in PMP_MODE_TOR: bins no{0}, yes{1}
  - cp_mseccfg = mseccfg {mml,mmwp,rlb}: bins s000{0,0,0}, s001{0,0,1}, s010{0,1,0}, s011{0,1,1}, s100{1,0,0}, s101{1,0,1}, s110{1,1,0}, s111{1,1,1}
- Crosses:
  - cr_regime_active = cp_regime x cp_active: bins off_n0{off, n0}, sparse_n1{sparse, n1}, sparse_n2_4{sparse, n2_4}, dense_n5_8{dense, n5_8}, dense_n9_15{dense, n9_15}, dense_n16{dense, n16}, mml_on_n1{mml_on, n1}, mml_on_n2_4{mml_on, n2_4}, mml_on_n5_8{mml_on, n5_8}, mml_on_n9_15{mml_on, n9_15}, mml_on_n16{mml_on, n16}; ignore_bins regime_active_outside{off with n > 0, sparse with n0 or n >= 5, dense with n < 5, mml_on with n0}: outside the regime definition
  - cr_regime_mseccfg = cp_regime x cp_mseccfg: bins off_s000{off, s000}, off_s001{off, s001}, off_s010{off, s010}, off_s011{off, s011}, sparse_s000{sparse, s000}, sparse_s001{sparse, s001}, sparse_s010{sparse, s010}, sparse_s011{sparse, s011}, dense_s000{dense, s000}, dense_s001{dense, s001}, dense_s010{dense, s010}, dense_s011{dense, s011}, mml_on_s100{mml_on, s100}, mml_on_s101{mml_on, s101}, mml_on_s110{mml_on, s110}, mml_on_s111{mml_on, s111}; ignore_bins low_regime_mml{off or sparse or dense, s1xx}: MML is set only in the mml_on regime; ignore_bins mml_on_s0{mml_on, s0xx}: the regime sets MML first
  - cr_locked_regime = cp_locked x cp_regime: bins n0_sparse{n0, sparse}, n0_dense{n0, dense}, n0_mml_on{n0, mml_on}, n1_4_sparse{n1_4, sparse}, n1_4_dense{n1_4, dense}, n1_4_mml_on{n1_4, mml_on}, n5_15_dense{n5_15, dense}, n5_15_mml_on{n5_15, mml_on}, n16_dense{n16, dense}, n16_mml_on{n16, mml_on}; ignore_bins sparse_many_locks{n5_15 or n16, sparse}: the sparse regime has at most 4 active entries and draws its locks among the active entries only (TP-PMP-100 precondition); OFF-locked entries are Phase-1 stimulus (TP-PMP-019), S-7
  - cr_overlap_modes = cp_overlap x cp_modes: bins overlap_tor_only{some, tor_only}, overlap_na_only{some, na_only}, overlap_mixed{some, mixed}
  - cr_e15_e0 = cp_e15 x cp_e0_tor: bins e15_active_e0tor_no{active, no}, e15_active_e0tor_yes{active, yes}
- Adopted (riscv-dv): none
- TP items: TP-PMP-010, TP-PMP-038, TP-PMP-039, TP-PMP-040, TP-PMP-044, TP-PMP-045, TP-PMP-051, TP-PMP-100, TP-PMP-101, TP-PMP-106, TP-PMP-107

### CG-PMP-015: gen_cg_pmp_degenerate_region
- Features: F-PMP-014, F-PMP-039, F-PMP-042, F-PMP-044
- Sample: a CG-PMP-005 check event (its condition included) whose word lies within the 32-bit alias range of an enabled degenerate region, i.e. a region with no byte in the 32-bit space (cp_kind); the model excludes the entry from its match set by construction; anti-vacuity: accesses outside every alias range never sample; a hit proves a degenerate region was probed at its 32-bit alias and did not decide the access (the verdict came from the next matching rule or the default and was checked by gen_chk_pmp). Added for the Critic's S-7: cr_tor_empty and the base_hi bins of CG-PMP-007 were unsamplable under that group's condition
- Coverpoints:
  - cp_kind = degeneracy kind of the enabled region whose alias range holds the word: bins tor_empty_eq{TOR entry i with pmpaddr(i-1) == pmpaddr(i): alias range is the single word pmpaddr(i) << 2}, tor_empty_gt{TOR entry i with pmpaddr(i-1) > pmpaddr(i): alias range [pmpaddr(i) << 2, (pmpaddr(i-1) << 2) - 1] (the reversed interval)}, tor_base_hi{TOR entry i whose lower bound pmpaddr(i-1) has bit 31 or 30 set (start >= 2^32): alias range [pmpaddr(i-1)[29:0] << 2, (pmpaddr(i)[29:0] << 2) - 1] or the single word pmpaddr(i-1)[29:0] << 2 when that interval is empty}, na4_base_hi{NA4 entry with pmpaddr bit 31 or 30 set: alias is the word pmpaddr[29:0] << 2}, napot_base_hi{NAPOT entry with pmpaddr bit 31 or 30 set and a mask not covering it (k < 30 for bit 30, k < 31 for bit 31): alias range [pmpaddr[29:0] << 2 with the low k+1 bits cleared, + 2^(3+k) - 1]}
  - cp_hi = iff kind in {tor_base_hi, na4_base_hi, napot_base_hi}: which high bit: bins hi30{bit 30 only}, hi31{bit 31 only}, both{bits 31 and 30}
  - cp_type = access type: bins fetch{fetch}, load{load}, store{store}
  - cp_priv = effective privilege: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_pos = position of the access bytes in the alias range: bins alias_low{first byte of the alias range (takes precedence)}, alias_high{last byte of the alias range}, alias_interior{strictly inside the alias range}
  - cp_fallback = who decided the access (the degenerate entry never matches): bins next_rule{a higher-index matching entry decided}, default{no match: the MMWP/MML/privilege default decided}
- Crosses:
  - cr_kind_type = cp_kind x cp_type: bins tor_empty_eq_fetch{tor_empty_eq, fetch: the degenerate entry did not decide}, tor_empty_eq_load{tor_empty_eq, load: the degenerate entry did not decide}, tor_empty_eq_store{tor_empty_eq, store: the degenerate entry did not decide}, tor_empty_gt_fetch{tor_empty_gt, fetch: the degenerate entry did not decide}, tor_empty_gt_load{tor_empty_gt, load: the degenerate entry did not decide}, tor_empty_gt_store{tor_empty_gt, store: the degenerate entry did not decide}, tor_base_hi_fetch{tor_base_hi, fetch: the degenerate entry did not decide}, tor_base_hi_load{tor_base_hi, load: the degenerate entry did not decide}, tor_base_hi_store{tor_base_hi, store: the degenerate entry did not decide}, na4_base_hi_fetch{na4_base_hi, fetch: the degenerate entry did not decide}, na4_base_hi_load{na4_base_hi, load: the degenerate entry did not decide}, na4_base_hi_store{na4_base_hi, store: the degenerate entry did not decide}, napot_base_hi_fetch{napot_base_hi, fetch: the degenerate entry did not decide}, napot_base_hi_load{napot_base_hi, load: the degenerate entry did not decide}, napot_base_hi_store{napot_base_hi, store: the degenerate entry did not decide}
  - cr_hi_kind = cp_kind x cp_hi: bins tor_base_hi_hi30{tor_base_hi, hi30}, tor_base_hi_hi31{tor_base_hi, hi31}, tor_base_hi_both{tor_base_hi, both}, na4_base_hi_hi30{na4_base_hi, hi30}, na4_base_hi_hi31{na4_base_hi, hi31}, na4_base_hi_both{na4_base_hi, both}, napot_base_hi_hi30{napot_base_hi, hi30}, napot_base_hi_hi31{napot_base_hi, hi31}, napot_base_hi_both{napot_base_hi, both}
  - cr_kind_fallback = cp_kind x cp_fallback: bins tor_empty_eq_next_rule{tor_empty_eq, next_rule}, tor_empty_eq_default{tor_empty_eq, default}, tor_empty_gt_next_rule{tor_empty_gt, next_rule}, tor_empty_gt_default{tor_empty_gt, default}, tor_base_hi_next_rule{tor_base_hi, next_rule}, tor_base_hi_default{tor_base_hi, default}, na4_base_hi_next_rule{na4_base_hi, next_rule}, na4_base_hi_default{na4_base_hi, default}, napot_base_hi_next_rule{napot_base_hi, next_rule}, napot_base_hi_default{napot_base_hi, default}
  - cr_kind_pos = cp_kind x cp_pos: bins tor_empty_eq_alias_low{tor_empty_eq, alias_low}, tor_empty_gt_alias_low{tor_empty_gt, alias_low}, tor_empty_gt_alias_high{tor_empty_gt, alias_high}, tor_empty_gt_alias_interior{tor_empty_gt, alias_interior}, tor_base_hi_alias_low{tor_base_hi, alias_low}, tor_base_hi_alias_high{tor_base_hi, alias_high}, tor_base_hi_alias_interior{tor_base_hi, alias_interior}, na4_base_hi_alias_low{na4_base_hi, alias_low}, na4_base_hi_alias_high{na4_base_hi, alias_high}, na4_base_hi_alias_interior{na4_base_hi, alias_interior}, napot_base_hi_alias_low{napot_base_hi, alias_low}, napot_base_hi_alias_high{napot_base_hi, alias_high}, napot_base_hi_alias_interior{napot_base_hi, alias_interior}; ignore_bins tor_empty_eq_not_low{tor_empty_eq, alias_high or alias_interior}: the alias range is a single word: alias_low takes precedence
  - cr_kind_priv = cp_kind x cp_priv: bins tor_empty_eq_m{tor_empty_eq, m}, tor_empty_eq_u{tor_empty_eq, u}, tor_empty_gt_m{tor_empty_gt, m}, tor_empty_gt_u{tor_empty_gt, u}, tor_base_hi_m{tor_base_hi, m}, tor_base_hi_u{tor_base_hi, u}, na4_base_hi_m{na4_base_hi, m}, na4_base_hi_u{na4_base_hi, u}, napot_base_hi_m{napot_base_hi, m}, napot_base_hi_u{napot_base_hi, u}
- Adopted (riscv-dv): none
- TP items: TP-PMP-037, TP-PMP-040, TP-PMP-042

### CG-PMP-016: gen_cg_pmp_entry_mode_trans
- Features: F-PMP-006, F-PMP-001, F-PMP-092
- Sample: RVFI retire (rvfi_trap == 0) of a pmpcfg write whose RMW-combined value changes the A field of entry i, sampled only if entry i was live before the write (the model attributes at least one PMP-decided access matched by entry i, or lying within its old byte range, to the retirements since the previous change of entry i) and is probed again after it (at least one access into the old or new byte range retires before the next change of entry i; otherwise the sample is discarded); anti-vacuity: writes to idle entries and same-mode rewrites never sample; a hit proves a live entry changed matching mode and the accesses before and after were checked against the old and new geometry (S-12)
- Coverpoints:
  - cp_trans = (old A, new A) of the written entry i: bins off_tor{OFF -> TOR}, off_na4{OFF -> NA4}, off_napot{OFF -> NAPOT}, tor_off{TOR -> OFF}, tor_na4{TOR -> NA4}, tor_napot{TOR -> NAPOT}, na4_off{NA4 -> OFF}, na4_tor{NA4 -> TOR}, na4_napot{NA4 -> NAPOT}, napot_off{NAPOT -> OFF}, napot_tor{NAPOT -> TOR}, napot_na4{NAPOT -> NA4}
  - cp_entry = i: bins e0{0}, e1{1}, e2{2}, e3{3}, e4{4}, e5{5}, e6{6}, e7{7}, e8{8}, e9{9}, e10{10}, e11{11}, e12{12}, e13{13}, e14{14}, e15{15}
  - cp_effect = model verdict change for the first post-write access into the old or new byte range of entry i: bins unchanged{same verdict}, now_denied{allow -> deny}, now_allowed{deny -> allow}
  - cp_chain = distinct A values entry i has held while live since the last reset or regime phase start, the new one included: bins two{2}, three{3}, four{4: OFF, TOR, NA4 and NAPOT all visited}
  - cp_range_rel = iff old and new A != OFF: new byte range vs old byte range: bins same{identical}, shrink{strict subset}, grow{strict superset}, disjoint{no common byte}, overlap_partial{partial overlap}
- Crosses:
  - cr_trans_effect = cp_trans x cp_effect: bins off_tor_now_denied{OFF -> TOR, now_denied}, off_tor_now_allowed{OFF -> TOR, now_allowed}, off_na4_now_denied{OFF -> NA4, now_denied}, off_na4_now_allowed{OFF -> NA4, now_allowed}, off_napot_now_denied{OFF -> NAPOT, now_denied}, off_napot_now_allowed{OFF -> NAPOT, now_allowed}, tor_off_now_denied{TOR -> OFF, now_denied}, tor_off_now_allowed{TOR -> OFF, now_allowed}, tor_na4_now_denied{TOR -> NA4, now_denied}, tor_na4_now_allowed{TOR -> NA4, now_allowed}, tor_napot_now_denied{TOR -> NAPOT, now_denied}, tor_napot_now_allowed{TOR -> NAPOT, now_allowed}, na4_off_now_denied{NA4 -> OFF, now_denied}, na4_off_now_allowed{NA4 -> OFF, now_allowed}, na4_tor_now_denied{NA4 -> TOR, now_denied}, na4_tor_now_allowed{NA4 -> TOR, now_allowed}, na4_napot_now_denied{NA4 -> NAPOT, now_denied}, na4_napot_now_allowed{NA4 -> NAPOT, now_allowed}, napot_off_now_denied{NAPOT -> OFF, now_denied}, napot_off_now_allowed{NAPOT -> OFF, now_allowed}, napot_tor_now_denied{NAPOT -> TOR, now_denied}, napot_tor_now_allowed{NAPOT -> TOR, now_allowed}, napot_na4_now_denied{NAPOT -> NA4, now_denied}, napot_na4_now_allowed{NAPOT -> NA4, now_allowed}
  - cr_entry_chain = cp_entry x cp_chain: bins e0_four{0, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e1_four{1, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e2_four{2, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e3_four{3, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e4_four{4, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e5_four{5, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e6_four{6, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e7_four{7, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e8_four{8, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e9_four{9, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e10_four{10, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e11_four{11, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e12_four{12, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e13_four{13, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e14_four{14, four: the entry walked OFF/TOR/NA4/NAPOT while live}, e15_four{15, four: the entry walked OFF/TOR/NA4/NAPOT while live}
- Adopted (riscv-dv): none
- TP items: TP-PMP-111

### Appendix A: Smepmp truth table as bound to CG-PMP-005.cr_truth_mml1 (expected verdict per bin)

| LRWX | M fetch | M load | M store | U fetch | U load | U store |
|---|---|---|---|---|---|---|
| c0000 | deny | deny | deny | deny | deny | deny |
| c0001 | deny | deny | deny | allow | deny | deny |
| c0010 | deny | allow | allow | deny | allow | deny |
| c0011 | deny | allow | allow | deny | allow | allow |
| c0100 | deny | deny | deny | deny | allow | deny |
| c0101 | deny | deny | deny | allow | allow | deny |
| c0110 | deny | deny | deny | deny | allow | allow |
| c0111 | deny | deny | deny | allow | allow | allow |
| c1000 | deny | deny | deny | deny | deny | deny |
| c1001 | allow | deny | deny | deny | deny | deny |
| c1010 | allow | deny | deny | allow | deny | deny |
| c1011 | allow | allow | deny | allow | deny | deny |
| c1100 | deny | allow | deny | deny | deny | deny |
| c1101 | allow | allow | deny | deny | deny | deny |
| c1110 | deny | allow | allow | deny | deny | deny |
| c1111 | deny | allow | deny | deny | allow | deny |

### Appendix B: original PMP table as bound to CG-PMP-005.cr_truth_mml0 (RW=01 rows ignored)

| LRWX | M fetch | M load | M store | U fetch | U load | U store |
|---|---|---|---|---|---|---|
| c0000 | allow | allow | allow | deny | deny | deny |
| c0001 | allow | allow | allow | allow | deny | deny |
| c0100 | allow | allow | allow | deny | allow | deny |
| c0101 | allow | allow | allow | allow | allow | deny |
| c0110 | allow | allow | allow | deny | allow | allow |
| c0111 | allow | allow | allow | allow | allow | allow |
| c1000 | deny | deny | deny | deny | deny | deny |
| c1001 | allow | deny | deny | allow | deny | deny |
| c1100 | deny | allow | deny | deny | allow | deny |
| c1101 | allow | allow | deny | allow | allow | deny |
| c1110 | deny | allow | allow | deny | allow | allow |
| c1111 | allow | allow | allow | allow | allow | allow |

### Appendix C: RTL facts this plan rests on (verified for the fix-2 revision; fix-3 additions from the T-053 fact-check marked X-n)

- A CSR write to any PMP CSR raises csr_pipe_flush (rtl/ibex_id_stage.sv:595-597; only mscratch/mepc are exempt). The controller's FLUSH state for a flush-only request asserts halt_if and flush_id and sets no PC (rtl/ibex_controller.sv:816-819, 953-963); the fetch FIFO is cleared only by branch_i (rtl/ibex_prefetch_buffer.sv:78). A word granted on the ibus before the write retires therefore survives the flush and is PMP-checked on pc_if at the IF/ID handoff with the post-write state (rtl/ibex_core.sv:1595-1600). CG-PMP-011.cp_next_src.bus_prefetched and CG-PMP-010.cp_outcome.retired_ok_recfg are reachable; they are observable on the bus only with cpuctrlsts.icache_enable == 0 (TP-PMP-091 pins it, S-4).
- Every privilege-changing event (mret, dret, trap entry, debug entry) sets the PC, so no word granted under one privilege reaches ID under another: CG-PMP-010.cp_outcome.retired_ok_priv is an ignore_bin.
- rvfi_trap is 1 for a PMP fault taken in debug mode (rtl/ibex_core.sv:1885-1889: rvfi_trap_id / rvfi_trap_wb carry exc_req regardless of debug_mode); the redirect target is DmExceptionAddr (rtl/ibex_controller.sv:829-831).
- DmHaltAddr (0x1A110800) and DmExceptionAddr (0x1A110808) both lie inside the DM window DmBaseAddr..DmBaseAddr+DmAddrMask (0x1A110000..0x1A110FFF), which debug mode bypasses (CTRL-34): the halt/exception fetches can never be denied.
- NAPOT with pmpaddr in {0x3FFFFFFF, 0x7FFFFFFF, 0xFFFFFFFF} has base 0 and a 34-bit size >= 2^33 (rtl/ibex_pmp.sv:160-209): address 0 is the region's first byte (inside_low reachable), its last byte lies above 2^32 (inside_high unreachable).
- (X-1) rvfi_pc_wdata of a trap / mret / dret record is the next sequential fetch address, never the redirect target (rtl/ibex_core.sv:2084); redirect targets are observed as the next record's rvfi_pc_rdata. Bins keyed on a trap target (CG-PMP-009.cr_target.*, CG-PMP-013.cp_phase exc_fetch / post_dret_first) use that form.
- (X-20) Permission-table specifics: the MML row LRWX=0011 grants READ|WRITE in both modes and denies fetch (rtl/ibex_pmp.sv:66-75: cr_truth_mml1.c0011_u_fetch is a deny bin); no configuration permits a store while denying a load at the same privilege (MML=0 stores W as W&R, rtl/ibex_cs_registers.sv:1444-1445; MML=1 rows granting WRITE grant READ, rtl/ibex_pmp.sv:66-83); under MML=0 the L bit is ignored for U-mode (rtl/ibex_pmp.sv:108-109); RLB 0->1 requires no L=1 entry while RLB=0 (rtl/ibex_cs_registers.sv:1463, 1514), so with MML=1 (M-mode code needs an L=1 executable rule) the transitions (1,x,0)->(1,x,1) are unreachable outside debug mode (CG-PMP-003.cr_state_trans ignore_bins); a NA4/NAPOT entry i-1 is anchored at pmpaddr(i-1) and decides the TOR inside_low word of entry i (rtl/ibex_pmp.sv:163-164).
- (X-21) The icache is forced off in debug mode and in the dret cycle (rtl/ibex_cs_registers.sv:1970-1971), so DmHaltAddr / DmExceptionAddr / dret-target fetches are always bus-visible; every other ibus-inferred prefetch or "no grant" observation pins cpuctrlsts.icache_enable = 0 (CG-PMP-010 / CG-PMP-011 bus_* and fresh bins) or is the deliberate cache-hit path of TP-PMP-092 / TP-PMP-105.

## Counts

- covergroups: 16
- coverpoints: 143
- bins (coverpoint bins, required, post-ignore): 520
- crosses: 99
- cross bins (required, post-ignore): 1175
- adopted bins: 0 (vendor/google_riscv-dv was not in this subagent's fence; nothing adopted)
- ignore_bins entries: 66

## Probe candidates

- CG-PMP-008.cp_lat / cr_lat.aligned_denied_lat2 (F-PMP-084): the 2-cycle internal completion of a denied access is invisible at the boundary (no bus handshake; retire timing is confounded by pipeline stalls). Probe: u_ibex_core.load_store_unit_i.ls_fsm_cs and lsu_resp_valid_o (read-only, define-gated). Marked probe-gated, not in the manifest, until the probe register carries it (S-14); TP-PMP-082 keeps the boundary-observable bins only. DV Lead decides.
- CG-PMP-009.cp_src / CG-PMP-010.cp_later_outcome / CG-PMP-011.cp_next_src.cache_hit (icache hit inference, F-PMP-093): inferred from the absence of an ibus grant for the word since the last invalidation; ambiguous when the prefetch buffer still holds the word. Probe alternative: u_ibex_core.if_stage_i.gen_icache.icache_i tag-hit indication, if the boundary inference is judged too weak.
- CG-PMP-012.cp_mprv_after (dret_u_kept_rtl, F-PMP-075): mstatus.MPRV cannot be read in U-mode; the bin is inferred from the access verdict on a U-denied/M-allowed window. Probe alternative: u_ibex_core.cs_registers_i.mstatus_q.mprv. DV Lead decides.
- CG-PMP-013.cp_phase halt_fetch / post_dret_first (CTRL-34 registered debug_mode window): sampled from rvfi_ext_debug_mode and the ibus address == DmHaltAddr; the exact cycle of debug_mode_q is not needed for the bins but would sharpen the checker. Probe alternative: u_ibex_core.id_stage_i.controller_i.debug_mode_q.
- CG-PMP-016 (live-entry attribution, F-PMP-006): liveness is derived from the model's match attribution of retired accesses; no probe needed.


# 3.5 Areas DBG, TRG, PMC: External debug (Sdext), triggers (Sdtrig), performance counters


Area group DBG/TRG/PMC, T-006 subagent output. Build configuration `opentitan`, DUT gen_dut_top
(ibex_core + ibex_register_file_ff), DbgHwBreakNum=1, MHPMCounterNum=10, MHPMCounterWidth=32,
DmBaseAddr=0x1A110000, DmAddrMask=0xFFF, DmHaltAddr=0x1A110800, DmExceptionAddr=0x1A110808.

Conventions
- Every covergroup is `gen_cg_<area>_<name>` in gen_fcov_pkg (or a gen_<x>_cov module bound via
  gen_binds); none extends an RTL covergroup. Sampling events come from the RVFI monitor, the
  ibus/dbus monitors, the irq/debug_req driver monitors and the TB debug-state model
  (`dbg_model`: debug_mode, step_armed, pending irq, WB occupancy), never from a bare clock.
- Parameter-derived values: PRIV_LVL_*, DBG_CAUSE_*, CSR_* from ibex_pkg; MHPMCOUNTER_BASE (=3)
  and MHPMCounterNum, MHPMCounterWidth, DbgHwBreakNum, DmBaseAddr/DmAddrMask/DmHaltAddr/
  DmExceptionAddr from the gen_dut_top parameters; irq_fast width from $bits(irq_fast_i).
  Per-counter bins for the implemented mhpmcounterN are written as MHPMCOUNTER_BASE+k and are
  generated only for k < MHPMCounterNum (generate-guarded).
- Bins in TP items and the CSVs are referenced as CG-<AREA>-<nnn>.cp_<name>.<bin> and
  CG-<AREA>-<nnn>.cr_<name>.<bin>. Cross bins are written `<bin>{a,b[,c]}` listing the component
  bins in coverpoint order.
- No `illegal_bins`: contradictions are checker failures, not coverage. Values that cannot occur
  are `ignore_bins` with a reason.
- "readback" always means the value returned by a later csrr of the same CSR observed on
  rvfi_rd_wdata, not the predicted value.
- Bins whose only purpose is bug-candidate evidence are marked (B<n>); hitting them is expected in
  the expected-fail item and confirms the reproducer.
- Window definitions (boundary form; used wherever an item or bin names a controller state).
  W-DEC(X): the cycles instruction X occupies ID, back-dated from its RVFI record: rvfi_valid is
  one flop after WB exit (rtl/ibex_core.sv:1868) and the ID-exit-to-record offset is
  GEN_RVFI_ID_EXIT_OFFSET (2, plus the response wait for loads/stores; gen_tb_architecture.md 8.2),
  so the last ID cycle of X is record_cycle - GEN_RVFI_ID_EXIT_OFFSET. W-FLUSH(X): the single
  cycle after the last ID cycle of a special instruction X (trap, mret, dret, wfi, flushing CSR
  write); at the boundary it is the cycle of the first ibus request to X's redirect target
  (vector / mepc / dpc / X+size) and the cycle before the DmHaltAddr request when a debug entry
  follows. W-IRQTAKEN: the cycle of the first ibus request to the interrupt vector (interrupt
  marker offset 2 to its record). W-DBGTAKEN: the cycle of the DmHaltAddr request; the icache is
  disabled while debug_mode_entering is set (rtl/ibex_cs_registers.sv:1970-1971), so every entry
  fetch reaches the ibus. W-WAITSLEEP(wfi): the cycle after W-FLUSH(wfi) when no entry follows
  (never reached by a stepped wfi, C-5). Same-cycle rule (fact-check TIMING rows TP-TRG-012/020/
  023/031): the last pre-entry RVFI record (ID exit N -> record N+2; load/store response R -> record
  R+1) can be output in the SAME cycle as the DmHaltAddr request, so "record X then the DmHaltAddr
  fetch" is a record-order / at-or-before relation, never a strict cycle order. W-WB(X): the cycles
  X occupies WB (a one-cycle ALU/CSR instruction: exactly the cycle after its last ID cycle; a
  load/store: from that cycle to its final response R). A csrr/csrw Y coincides with X in WB only
  when Y's last ID cycle lies in W-WB(X): back-to-back issue for a one-cycle X (warm icache / fetch
  already delivered; a slow imem REMOVES the coincidence) or Y held by outstanding_memory_access
  behind a load/store X (Y commits in cycle R, the deterministic form used by TP-PMC-011/016/024).
  Items whose fire-check needs a redirect-target request cycle pin cpuctrlsts.icache_enable=0
  (S-4 / C-14); entry fetches never need it. Where a window is ambiguous the P4 nets (ctrl_fsm_cs,
  fcov_*) are the coverage-only fallback; no checker reads them.
- Ebreak-into-debug rule (S-2): an ebreak whose ebreakm/ebreaku bit for the current privilege is
  set produces an RVFI record with rvfi_trap = 0 (rtl/ibex_core.sv:1885-1886); the debug path is
  `is_ebreak(rvfi_insn) && !rvfi_trap && next fetch == DmHaltAddr`, the exception path is
  `rvfi_trap = 1` with the next fetch at the mtvec target. Inside debug mode an ebreak re-enters
  DmHaltAddr with rvfi_trap = !ebreak_into_debug (rtl/ibex_controller.sv:874-876 takes
  DBG_TAKEN_ID whatever the enable bit). The counter model never counts an ebreak record in
  minstret (rtl/ibex_id_stage.sv:1218), so the ebreak-into-debug record is a not-counted record
  with rvfi_trap = 0.
- core_busy_o port rule (gen_tb_architecture.md 8.2 item 1): core_busy_o = ctrl_busy | if_busy |
  lsu_busy (rtl/ibex_core.sv:498-521). The one-cycle WAIT_SLEEP dip of ctrl_busy is visible on
  core_busy_o only when no ibus beat is outstanding, no icache invalidation sweep is active (the
  256-write sweep after reset release / key valid, so a wfi within 256 cycles of it sees no dip)
  and the LSU is idle in that cycle; otherwise the dip is hidden. Dip bins carry a `hidden`
  class for that case, decoded from the bus monitors.
- Fix-brief-3 conventions (rtl-arch T-053 fact-check, plan v2b; stated once here, cited as C-n):
  C-1 the redirect target of a trap / mret / dret record is the NEXT record's rvfi_pc_rdata (or the
  DmExceptionAddr / vector fetch with the icache off); rvfi_pc_wdata of those records is the next
  sequential fetch address (rtl/ibex_core.sv:2084 captures pc_if: mret/dret leave ID in DECODE and
  their pc_set comes one cycle later in FLUSH) and is never asserted as the target; only branch/jump
  records carry the target. C-3 rvfi_ext_debug_req is the debug_req_i level at the record's IF->ID
  transfer (rtl/ibex_core.sv:1996-2001), or captured_debug_req when the request arrived on an empty
  ID (:1949-1957): the instruction in ID when the pin rises reports 0 and completes; an instruction
  whose transfer comes after the rise never enters ID outside debug mode (halt_if,
  rtl/ibex_controller.sv:700-708; entry with dpc = its pc and no record for it); the first
  debug-ROM record reports 1; {req 1, mode 0} is reachable only by a Zcmp micro-op entering ID while
  enter_debug_mode is masked (rtl/ibex_controller.sv:474-477) or by the sticky capture after a
  dropped pulse. Debug and interrupt entry need an empty ID and a ready WB (X-7, :296, :700-720):
  dpc / mepc = pc of the first not-yet-executed instruction = next pc of the last retired record
  (nominal 2 records after the pin edge, worst case 17). C-5 a stepped wfi never reaches WAIT_SLEEP
  (FLUSH -> DBG_TAKEN_IF, rtl/ibex_controller.sv:985-987): no core_busy_o dip; the one-cycle dip
  belongs to an unstepped wfi (port rule) and to a wfi executed in debug mode. C-10 HPM counters 8,
  11 and 12 over-count an instruction waiting in ID behind an outstanding WB memory access (B17,
  rtl/ibex_id_stage.sv:886-934, :1054-1057, :1226-1227): the exact classes of CG-PMC-003 carry the
  precondition "no outstanding WB access when the counted instruction is in ID"; counters 7 and 9
  are exact (deduped by branch_jump_set_done_q). C-11 mhpmeventN reads 1 << (N - MHPMCOUNTER_BASE)
  (D20); the selectors are hardwired, nothing programs them. C-12 rvfi_insn is the 32-bit expansion
  for Zcmp micro-ops (one record per micro-op; halfword on rvfi_ext_expanded_insn; c.ebreak traced
  as the zero-extended halfword). C-13 rvfi_ext_irq_valid is a LEVEL rising four cycles after the
  decision cycle and held until about two cycles after the handler's first instruction enters ID;
  it is the boundary event of an interrupt accepted with no handler record (rvfi_intr is a
  per-record field). C-14 any bin that infers "in ID" or "no bus fetch of the target" from the
  instruction bus pins cpuctrlsts.icache_enable = 0 or derives the redirect from RVFI. C-16
  fire-checks are per-seed assertions on an observable.
- Cross-operand-only coverpoints: a coverpoint marked "(cross operand only; owner CG-x.cp_y)"
  exists because SV crosses need it inside the same covergroup; its standalone bins are never
  listed in a TP Bins line or the CSV and the closure score takes them from the owner (S-7).
- Witness bins marked "(witness; not in manifest)" are always-true or check-passed values kept for
  URG readability; they never appear in a TP Bins line or the CSV (S-3b). Bins marked
  "(probe-gated P1, not in manifest)" are sampled only once the probe register carries P1 and are
  not must-hit until then (S-13).
- Entry bound: "entry follows" means within 17 RVFI records of the request (nominal 2; worst case
  a Zcmp sequence of 16 micro-op records plus the WB instruction; the WFI path adds 3 cycles and no
  record), gen_tb_architecture.md 8.2 item 5; cycle bounds derive from the agent knobs
  (DBG_ENTRY_BOUND_CYCLES = 17 x (gnt_max + rvalid_max + 2) + 40).
- Parameter shorthands: HPM_LAST = MHPMCOUNTER_BASE + MHPMCounterNum - 1 (last implemented index);
  HPM_CTRL_MASK = ((32'd1 << (MHPMCOUNTER_BASE + MHPMCounterNum)) - 1) & ~32'h2 (writable
  mcountinhibit / mcounteren bits: CY, IR and one per implemented counter; 32'h1FFD when
  MHPMCounterNum = 10); DIV_STALL_FULL = 36 (stall cycles of a full-latency div/divu/rem/remu:
  FIRST_CYCLE + ABS_A + ABS_B + 31 COMP + LAST + CHANGE_SIGN, rtl/ibex_multdiv_fast.sv:425-526,
  rtl/ibex_id_stage.sv:917,962; D7); DIV_STALL_ZERO = 1 (div/rem by zero with
  cpuctrlsts.data_ind_timing = 0 early-outs IDLE -> FINISH, rtl/ibex_multdiv_fast.sv:434,445).

---------------------------------------------------------------------------------------------------

## DBG covergroups

### CG-DBG-001: gen_cg_dbg_entry
- Features: F-DBG-001, F-DBG-002, F-DBG-003, F-DBG-004, F-DBG-007, F-DBG-008, F-DBG-009, F-DBG-010,
  F-DBG-011, F-DBG-025, F-DBG-037, F-DBG-038, F-DBG-039, F-DBG-040, F-DBG-041, F-DBG-044, F-DBG-045,
  F-DBG-046, F-DBG-047, F-DBG-048, F-DBG-049, F-DBG-058, F-DBG-061, F-DBG-064, F-DBG-066, F-DBG-068,
  F-TRG-010, F-TRG-016, F-TRG-017, F-TRG-018, F-TRG-019, F-DBG-017 (parent of folded bins hosted
  here)
- Sample: debug entry = first ibus request to DmHaltAddr while dbg_model.debug_mode==0 (ibus monitor
  event); cause/prv/dpc are taken from the debug-ROM prologue's csrr dcsr / csrr dpc retirements
  (rvfi_rd_wdata) that follow the entry; condition: `dm_halt_fetch && !dbg_model.debug_mode`;
  anti-vacuity: no non-debug program code is placed at DmHaltAddr (TB memory map), so the fetch
  alone proves an entry; the cause and dpc bins come from observed CSR reads, so a hit proves what
  the hardware recorded, not what the stimulus intended.
- Coverpoints:
  - cp_cause = dcsr.cause readback: bins ebreak{DBG_CAUSE_EBREAK}, trigger{DBG_CAUSE_TRIGGER}, haltreq{DBG_CAUSE_HALTREQ}, step{DBG_CAUSE_STEP}, none{DBG_CAUSE_NONE}; ignore_bins reserved{5,6,7}: RTL never produces resethaltreq/group/other (CTRL-25). `none` is B9 evidence.
  - cp_prv_before = dcsr.prv readback: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}; ignore_bins s_h{PRIV_LVL_S,PRIV_LVL_H}: no S/H mode, WARL-legalised to U (F-DBG-013).
  - cp_entry_ctx = dbg_model pipeline context in the decision cycle (window definitions W-*, boundary-derived; the P4 nets are the coverage-only fallback): bins idle{W-DEC of an ordinary instruction, nothing outstanding on either bus}, lsu_wait{load/store granted with rvalid pending (dbus monitor)}, div_wait{multi-cycle divide in EX: RVFI gap open on a div/rem}, zcmp{Zcmp micro-op sequence in progress when the request was first seen (dbus accesses of one cm.* between two records)}, sleep{core in SLEEP after W-WAITSLEEP: a wfi retired with no following record}, reset{no retirement since reset release (FIRST_FETCH)}, flush_exc{W-FLUSH of a trapping instruction}, flush_mret{W-FLUSH(mret)}, flush_csr{W-FLUSH of a flushing CSR write}, flush_wfi{W-FLUSH(wfi) with a haltreq or the step already registered (enter_debug_mode_prio_q): W-WAITSLEEP never entered (H-C1, C-5)}, irq_taken{W-IRQTAKEN}, after_dret{first W-DEC after dret, no retirement in between}, after_trap{first W-DEC after a trap/irq vector fetch, no handler retirement}, after_mret{first W-DEC after mret, no retirement}, ifetch_stall{IF waiting for instr_rvalid_i: a granted fetch without rvalid (ibus monitor) and no record for >= 2 cycles}
  - cp_dpc_kind = dpc readback vs the RVFI stream: bins next_seq{last retired pc + size}, br_target{taken branch/jump target}, mtvec{trap or interrupt vector}, mret_target{mepc}, ebreak_pc{pc of the ebreak}, trig_pc{== tdata2}, boot{boot_addr_i[31:8],8'h80}, wfi_next{wfi pc + 4}, dret_target{unchanged across an immediate re-halt}
  - cp_busy_dip = number of consecutive cycles core_busy_o was Off between the last non-debug retirement (or the request, if later) and the DmHaltAddr fetch, classified with the core_busy_o port rule: bins none{0 Off cycles with no masking source active in the W-WAITSLEEP cycle}, hidden{0 Off cycles while a masking source was active in that cycle: an ibus beat outstanding, the icache invalidation sweep active (within 256 cycles of reset release / key valid) or a dbus access outstanding}, one{1}, many{[2:$]}; anti-vacuity: `none` is reachable only through the FLUSH -> DBG_TAKEN_IF override (F-DBG-068), `hidden` only when the bus monitors log the masking source, `one` only when SLEEP is left in its first cycle (an unstepped wfi woken by a debug_req_i already high in that cycle, F-DBG-009 / TP-DBG-071 (b), and the debug-mode wfi of F-DBG-059; a stepped wfi never sleeps, C-5), `many` only after a real sleep (F-DBG-009).
- Crosses:
  - cr_cause_prv = cp_cause x cp_prv_before: bins ebreak_m{ebreak,m}, ebreak_u{ebreak,u}, trigger_m{trigger,m}, trigger_u{trigger,u}, haltreq_m{haltreq,m}, haltreq_u{haltreq,u}, step_m{step,m}, step_u{step,u}; ignore none x *: B9 bin is covered on cp_cause alone.
  - cr_cause_ctx = cp_cause x cp_entry_ctx: bins haltreq_idle{haltreq,idle}, haltreq_lsu{haltreq,lsu_wait}, haltreq_div{haltreq,div_wait}, haltreq_zcmp{haltreq,zcmp}, haltreq_sleep{haltreq,sleep}, haltreq_reset{haltreq,reset}, haltreq_flush_exc{haltreq,flush_exc}, haltreq_flush_mret{haltreq,flush_mret}, haltreq_flush_csr{haltreq,flush_csr}, haltreq_flush_wfi{haltreq,flush_wfi}, haltreq_irq_taken{haltreq,irq_taken}, haltreq_after_dret{haltreq,after_dret}, haltreq_ifetch{haltreq,ifetch_stall}, step_idle{step,idle}, step_lsu{step,lsu_wait}, step_div{step,div_wait}, step_zcmp{step,zcmp}, step_flush_exc{step,flush_exc}, step_flush_mret{step,flush_mret}, step_flush_csr{step,flush_csr}, step_flush_wfi{step,flush_wfi}, trigger_idle{trigger,idle}, trigger_after_dret{trigger,after_dret}, trigger_after_trap{trigger,after_trap}, trigger_after_mret{trigger,after_mret}, trigger_ifetch{trigger,ifetch_stall}, ebreak_idle{ebreak,idle}; ignore_bins step_sleep{step,sleep}: a stepped wfi never reaches WAIT_SLEEP / SLEEP (do_single_step_d sets enter_debug_mode_prio_q and FLUSH overrides WAIT_SLEEP with DBG_TAKEN_IF, rtl/ibex_controller.sv:985-987; X-8 / C-5); ignore ebreak x {lsu_wait, div_wait, zcmp, sleep, reset, irq_taken, after_*}: ebreak is decided in FLUSH with the pipe drained; ignore trigger x {sleep, reset, zcmp, irq_taken, flush_*}: trigger is a non-priority entry masked in these states (CTRL-24).
  - cr_cause_dpc = cp_cause x cp_dpc_kind: bins haltreq_next{haltreq,next_seq}, haltreq_br{haltreq,br_target}, haltreq_mtvec{haltreq,mtvec}, haltreq_mret{haltreq,mret_target}, haltreq_boot{haltreq,boot}, haltreq_wfi{haltreq,wfi_next}, haltreq_dret{haltreq,dret_target}, step_next{step,next_seq}, step_br{step,br_target}, step_mtvec{step,mtvec}, step_mret{step,mret_target}, step_wfi{step,wfi_next}, ebreak_pc{ebreak,ebreak_pc}, trigger_pc{trigger,trig_pc}; ignore ebreak x others, trigger x others: dpc is fixed by construction for these causes (a different value is a gen_chk_debug failure).
  - cr_ctx_busy = cp_entry_ctx x cp_busy_dip: bins flush_wfi_none{flush_wfi,none}, sleep_one{sleep,one}, sleep_many{sleep,many}, sleep_hidden{sleep,hidden}; ignore flush_wfi x {one, many, hidden}: the FLUSH -> DBG_TAKEN_IF arc never reaches WAIT_SLEEP (gen_chk_sleep failure); ignore sleep x none: an unmasked zero-length dip after W-WAITSLEEP is a gen_chk_sleep failure; other contexts x *: core_busy_o is high outside WAIT_SLEEP/SLEEP by construction, not covered here.
- Adopted (riscv-dv): none
- TP items: TP-DBG-001, TP-DBG-002, TP-DBG-003, TP-DBG-004, TP-DBG-005, TP-DBG-006, TP-DBG-007, TP-DBG-008, TP-DBG-009, TP-DBG-011, TP-DBG-012, TP-DBG-013, TP-DBG-014, TP-DBG-015, TP-DBG-016, TP-DBG-020, TP-DBG-022, TP-DBG-024, TP-DBG-030, TP-DBG-042, TP-DBG-043, TP-DBG-045, TP-DBG-046, TP-DBG-049, TP-DBG-050, TP-DBG-051, TP-DBG-052, TP-DBG-054, TP-DBG-067, TP-DBG-068, TP-DBG-069, TP-DBG-071, TP-TRG-010, TP-TRG-012, TP-TRG-016, TP-TRG-017, TP-TRG-018, TP-TRG-019, TP-TRG-027

### CG-DBG-002: gen_cg_dbg_req_shape
- Features: F-DBG-002, F-DBG-005, F-DBG-006, F-DBG-007, F-DBG-008, F-DBG-049, F-DBG-058, F-DBG-068, F-TRG-019
- Sample: every debug_req_i rising edge seen by the debug_req driver monitor, sampled when its
  outcome is known (entry observed, or the bounded no-entry window expired); condition:
  `debug_req_rise && outcome_known`; anti-vacuity: the driver randomizes the pulse shape, so both
  `entered` and `dropped` are reachable; `dropped` is only recorded when no DmHaltAddr fetch occurs
  within the drain bound although the request was seen, so a hit proves a lost pulse.
- Coverpoints:
  - cp_shape = driver transaction shape: bins level_held{held until entry observed}, pulse_short{released 1..3 cycles after assertion, before entry}, pulse_flush{released exactly in W-FLUSH of a coincident special request}, held_in_debug{asserted while dbg_model.debug_mode==1}, held_across_dret{still high when dret retires}, at_reset{high through reset release}
  - cp_outcome = observed effect: bins entered{DmHaltAddr fetch within the entry bound}, dropped{no DmHaltAddr fetch within the entry bound (17 records after the pulse)}, rehalt_after_dret{entry with zero retirements after dret}, ignored_in_debug{no second DmHaltAddr fetch and dcsr/dpc unchanged while debug_mode = 1}
  - cp_coincident = dbg_model event pending in the same decision cycle: bins none{no other special event in W-DEC of the instruction}, irq{enabled interrupt pending}, nmi{irq_nm_i}, sync_exc{exception in ID/WB}, ebreak_dbg{ebreak with ebreakX=1}, trigger{trigger match}, step{step armed}, mret{mret in ID}, csr_flush{CSR write flush}, wfi{wfi in ID}
- Crosses:
  - cr_shape_outcome = cp_shape x cp_outcome: bins held_entered{level_held,entered}, short_dropped{pulse_short,dropped}, short_entered{pulse_short,entered}, flush_entered{pulse_flush,entered}, indebug_ignored{held_in_debug,ignored_in_debug}, dret_rehalt{held_across_dret,rehalt_after_dret}, reset_entered{at_reset,entered}; ignore level_held x dropped: a held request is never dropped (checker failure).
  - cr_coincident_outcome = cp_coincident x cp_outcome: bins irq_entered{irq,entered}, nmi_entered{nmi,entered}, exc_entered{sync_exc,entered}, ebreak_entered{ebreak_dbg,entered}, trigger_entered{trigger,entered}, step_entered{step,entered}, mret_entered{mret,entered}, csr_entered{csr_flush,entered}, wfi_entered{wfi,entered}
- Adopted (riscv-dv): none
- TP items: TP-DBG-001, TP-DBG-003, TP-DBG-005, TP-DBG-006, TP-DBG-007, TP-DBG-008, TP-DBG-010, TP-DBG-011, TP-DBG-012, TP-DBG-013, TP-DBG-014, TP-DBG-030, TP-DBG-054, TP-DBG-068, TP-DBG-071, TP-TRG-019

### CG-DBG-003: gen_cg_dbg_ebreak
- Features: F-DBG-017, F-DBG-018, F-DBG-019, F-DBG-020, F-DBG-021, F-DBG-022, F-DBG-023, F-DBG-024, F-DBG-025, F-DBG-041, F-DBG-066, F-TRG-020
- Sample: RVFI item whose rvfi_insn is ebreak or c.ebreak, plus the WB-fault-discard case detected by
  the dbg_model (ebreak in ID when WB faults, ebreak later re-executed); condition:
  `rvfi_valid && is_ebreak(rvfi_insn)`; the record carries rvfi_trap = 1 on the exception path and
  rvfi_trap = 0 on the into-debug path (rtl/ibex_core.sv:1885-1886, S-2 rule), so rvfi_trap is not
  the outcome: the outcome bin is derived from the next fetch address (DmHaltAddr vs mtvec target)
  and the dcsr/mcause readback; anti-vacuity: the outcome is never taken from ebreakm/ebreaku, so
  a hit proves the path the hardware took, and a mismatch between rvfi_trap and the decoded
  outcome is a gen_isa_compare failure.
- Coverpoints:
  - cp_priv = rvfi_mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_ebreakm = dcsr.ebreakm (CSR model): bins off{0}, on{1}
  - cp_ebreaku = dcsr.ebreaku: bins off{0}, on{1}
  - cp_form = instruction width: bins full{32-bit ebreak}, comp{c.ebreak}
  - cp_in_debug = rvfi_ext_debug_mode: bins no{0}, yes{1}
  - cp_outcome = outcome decoded from the next fetch address and the dcsr/mcause readback: bins dbg_entry{rvfi_trap = 0, next fetch DmHaltAddr, dcsr.cause 1, dpc == ebreak pc}, bp_exc{rvfi_trap = 1, next fetch mtvec target, mcause 3, mepc == ebreak pc}, reenter{in debug mode: DmHaltAddr fetch, dcsr/dpc unchanged, rvfi_trap = !ebreak_into_debug}, discarded{WB load/store fault taken instead: no record for the ebreak until it re-executes}
  - cp_coincident = dbg_model event pending in the decision cycle: bins none{no other event in W-DEC of the ebreak}, haltreq{debug_req_i high}, step{step armed}, trig_next{tdata2 == ebreak pc + size, execute=1 (B10)}, wb_fault{load/store fault in WB}
  - cp_en_edge = change of the governing enable bit (ebreakm in M, ebreaku in U) written in the debug window that precedes this ebreak, from the post-op dcsr value of the CSR model: bins none{unchanged since the previous ebreak in this privilege}, m_set{ebreakm 0 -> 1}, m_clr{ebreakm 1 -> 0}, u_set{ebreaku 0 -> 1}, u_clr{ebreaku 1 -> 0}
- Crosses:
  - cr_priv_en_outcome = cp_priv x cp_ebreakm x cp_ebreaku x cp_outcome: bins m_off_off_exc{m,off,off,bp_exc}, m_off_on_exc{m,off,on,bp_exc}, m_on_off_dbg{m,on,off,dbg_entry}, m_on_on_dbg{m,on,on,dbg_entry}, u_off_off_exc{u,off,off,bp_exc}, u_on_off_exc{u,on,off,bp_exc}, u_off_on_dbg{u,off,on,dbg_entry}, u_on_on_dbg{u,on,on,dbg_entry}; ignore * x reenter, * x discarded: covered by cr_form_outcome / cr_coincident_outcome; ignore contradictory pairs (e.g. m,on,*,bp_exc): checker failures.
  - cr_form_outcome = cp_form x cp_outcome: bins full_dbg{full,dbg_entry}, full_exc{full,bp_exc}, full_reenter{full,reenter}, comp_dbg{comp,dbg_entry}, comp_exc{comp,bp_exc}, comp_reenter{comp,reenter}
  - cr_coincident_outcome = cp_coincident x cp_outcome: bins haltreq_dbg{haltreq,dbg_entry}, step_dbg{step,dbg_entry}, trignext_dbg{trig_next,dbg_entry}, wbfault_discarded{wb_fault,discarded}
  - cr_edge_outcome = cp_en_edge x cp_outcome: bins mset_dbg{m_set,dbg_entry}, mclr_exc{m_clr,bp_exc}, uset_dbg{u_set,dbg_entry}, uclr_exc{u_clr,bp_exc}; ignore m_set/u_set x bp_exc, m_clr/u_clr x dbg_entry: the toggle did not take effect (gen_chk_debug failure); ignore none x *: covered by cr_priv_en_outcome.
- Adopted (riscv-dv): none
- TP items: TP-DBG-022, TP-DBG-023, TP-DBG-024, TP-DBG-025, TP-DBG-026, TP-DBG-027, TP-DBG-028, TP-DBG-029, TP-DBG-030, TP-DBG-046, TP-DBG-067, TP-DBG-068, TP-DBG-073, TP-TRG-020

### CG-DBG-004: gen_cg_dbg_exc_in_debug
- Features: F-DBG-011, F-DBG-026, F-DBG-027, F-DBG-028, F-DBG-029, F-DBG-030, F-DBG-036, F-DBG-054,
  F-DBG-055, F-DBG-060, F-DBG-064, F-DBG-067, F-PRV-002 (parent of folded bins hosted here)
- Sample: RVFI item with rvfi_trap && rvfi_ext_debug_mode (synchronous exception inside debug
  mode) that is not an ebreak; target address taken from the next ibus request; condition:
  `rvfi_valid && rvfi_trap && rvfi_ext_debug_mode && !is_ebreak(rvfi_insn)` (an ebreak in debug
  mode re-enters DmHaltAddr, not DmExceptionAddr, and carries rvfi_trap = !ebreak_into_debug:
  CG-DBG-003.cp_outcome.reenter, S-2 rule); anti-vacuity: debug programs are trap-free unless the
  test injects a fault, so a hit proves an exception occurred in debug mode; the kind bin is
  decoded from rvfi_insn / dbus / PMP-model verdict, not from the test's intent.
- Coverpoints:
  - cp_kind = exception kind decoded from rvfi_insn / dbus / PMP-model verdict: bins illegal{illegal instruction (not a CSR access)}, illegal_csr{CSR access illegal (address/privilege)}, ecall{rvfi_insn == ECALL}, fetch_pmp{fetch PMP fault outside the DM window: no ibus request for the target word}, fetch_bus{instr_err_i on the fetch}, load_pmp{load with no dbus request, PMP model denies}, store_pmp{store with no dbus request, PMP model denies}, load_bus{data_err_i on load}, store_bus{data_err_i on store}
  - cp_priv_in_debug = rvfi_mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U after mret-in-debug with MPP=U}
  - cp_mprv = mstatus.MPRV/MPP (CSR model): bins off{MPRV=0}, on_mpp_u{MPRV=1,MPP=U}, on_mpp_m{MPRV=1,MPP=M}
  - cp_dret_pending = dbus state when the trap is raised: bins none{no dret in ID when the fault is raised}, dret_wait{fault raised while a dret was waiting for WB}
  - cp_seq = ordinal of the exception within the debug window: bins first{first exception in this debug window}, second{second consecutive exception in the window}
- Crosses:
  - cr_kind_priv = cp_kind x cp_priv_in_debug: bins illegal_m{illegal,m}, illegalcsr_m{illegal_csr,m}, ecall_m{ecall,m}, fetchpmp_m{fetch_pmp,m}, fetchbus_m{fetch_bus,m}, loadpmp_m{load_pmp,m}, storepmp_m{store_pmp,m}, loadbus_m{load_bus,m}, storebus_m{store_bus,m}, illegalcsr_u{illegal_csr,u}, ecall_u{ecall,u}, loadpmp_u{load_pmp,u}, fetchpmp_u{fetch_pmp,u}
  - cr_kind_mprv = cp_kind x cp_mprv: bins loadpmp_mprv_u{load_pmp,on_mpp_u}, storepmp_mprv_u{store_pmp,on_mpp_u}, loadpmp_off{load_pmp,off}, loadbus_mprv_u{load_bus,on_mpp_u}; (B2 evidence: loadpmp_mprv_u / storepmp_mprv_u)
  - cr_kind_dret = cp_kind x cp_dret_pending: bins loadpmp_dret{load_pmp,dret_wait}, loadbus_dret{load_bus,dret_wait}, storebus_dret{store_bus,dret_wait}
  - cr_kind_seq = cp_kind x cp_seq: bins illegal_second{illegal,second}, ecall_second{ecall,second}, loadbus_second{load_bus,second}
- Adopted (riscv-dv): none
- TP items: TP-DBG-031, TP-DBG-032, TP-DBG-033, TP-DBG-034, TP-DBG-035, TP-DBG-041, TP-DBG-059, TP-DBG-060, TP-DBG-064, TP-DBG-068

### CG-DBG-005: gen_cg_dbg_dret
- Features: F-DBG-007, F-DBG-013, F-DBG-031, F-DBG-032, F-DBG-033, F-DBG-034, F-DBG-035, F-DBG-036, F-DBG-042, F-DBG-056, F-DBG-057, F-DBG-066, F-TRG-016
- Sample: RVFI item with rvfi_insn == 32'h7B200073 (dret), legal (in debug mode, no trap) or
  illegal (outside debug mode, rvfi_trap); the `next` bin is closed when the following RVFI/bus
  event is observed; condition: `rvfi_valid && rvfi_insn == DRET`; anti-vacuity: dret occurs only
  in debug programs and in the directed illegal-dret items; the resume privilege is taken from
  rvfi_mode of the next retirement (or the dcsr readback when nothing retires), so a hit proves the
  observed resume mode.
- Coverpoints:
  - cp_legal = {rvfi_ext_debug_mode, rvfi_trap, rvfi_mode} of the dret item: bins ok{in debug mode, retired}, illegal_m{outside debug, M, rvfi_trap}, illegal_u{outside debug, U, rvfi_trap}
  - cp_prv_target = dcsr.prv at dret: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_prv_src = how dcsr.prv got its value: bins hw{saved by the entry}, sw_m{written 2'b11}, sw_u{written 2'b00}, sw_s{written 2'b01, legalised to U}, sw_h{written 2'b10, legalised to U}
  - cp_mprv = mstatus.MPRV at dret (CSR model): bins off{0}, on{1 with MPP=M}
  - cp_dpc_src = origin of the dpc value (hardware save vs software write): bins hw{saved by the entry}, sw_even{csrw dpc even}, sw_odd{csrw dpc odd, bit 0 dropped}
  - cp_wb_pending = dbus state when dret is in ID: bins none{no dbus access outstanding}, load{load outstanding}, store{store outstanding}, fault{outstanding access returns an error}
  - cp_next = first event after dret: bins run{ordinary retirement at dpc}, rehalt_req{held debug_req_i re-halts, zero retirements}, rehalt_ebreak{ebreak at dpc enters debug (record with rvfi_trap = 0, S-2)}, rehalt_trig{trigger at dpc}, irq_first{interrupt taken before any retirement, mepc == dpc}, nmi_first{NMI taken first}, step_one{exactly one retirement then re-entry}, fault_at_dpc{fetch at dpc faults}
  - cp_step_at_dret = dcsr.step at this dret (post-op value of the CSR model) against the previous dret of the seed: bins on{1}, off_first{0, no earlier dret with step = 1 in the seed}, off_after_on{0, the previous dret of the seed had step = 1: the step window is left and the core free-runs}
- Crosses:
  - cr_prv_next = cp_prv_target x cp_next: bins m_run{m,run}, m_rehalt_req{m,rehalt_req}, m_rehalt_ebreak{m,rehalt_ebreak}, m_rehalt_trig{m,rehalt_trig}, m_irq{m,irq_first}, m_nmi{m,nmi_first}, m_step{m,step_one}, m_fault{m,fault_at_dpc}, u_run{u,run}, u_rehalt_req{u,rehalt_req}, u_rehalt_ebreak{u,rehalt_ebreak}, u_rehalt_trig{u,rehalt_trig}, u_irq{u,irq_first}, u_nmi{u,nmi_first}, u_step{u,step_one}, u_fault{u,fault_at_dpc}
  - cr_prv_mprv = cp_prv_target x cp_mprv: bins u_on{u,on}, m_on{m,on}, u_off{u,off}, m_off{m,off}; (B1 evidence: u_on)
  - cr_prvsrc_target = cp_prv_src x cp_prv_target: bins hw_m{hw,m}, hw_u{hw,u}, swm_m{sw_m,m}, swu_u{sw_u,u}, sws_u{sw_s,u}, swh_u{sw_h,u}; ignore sw_s x m, sw_h x m: WARL result is U.
  - cr_dpcsrc_next = cp_dpc_src x cp_next: bins hw_run{hw,run}, even_run{sw_even,run}, odd_run{sw_odd,run}, hw_fault{hw,fault_at_dpc}
  - cr_wb_next = cp_wb_pending x cp_next: bins load_run{load,run}, store_run{store,run}, none_run{none,run}
  - cr_step_next = cp_step_at_dret x cp_next: bins on_step{on,step_one}, offafteron_run{off_after_on,run}, offfirst_run{off_first,run}; ignore on x run: a step-armed dret that free-runs is a gen_chk_debug failure; ignore off_* x step_one: a re-entry after one retirement with step = 0 needs another cause (covered by cp_next.rehalt_*).
- Adopted (riscv-dv): none
- TP items: TP-DBG-012, TP-DBG-019, TP-DBG-021, TP-DBG-024, TP-DBG-036, TP-DBG-037, TP-DBG-038, TP-DBG-039, TP-DBG-040, TP-DBG-041, TP-DBG-042, TP-DBG-047, TP-DBG-048, TP-DBG-053, TP-DBG-061, TP-DBG-062, TP-DBG-067, TP-DBG-068, TP-DBG-072, TP-TRG-016

### CG-DBG-006: gen_cg_dbg_step
- Features: F-DBG-037, F-DBG-038, F-DBG-039, F-DBG-040, F-DBG-041, F-DBG-042, F-DBG-043, F-DBG-044,
  F-DBG-045, F-DBG-046, F-DBG-047, F-DBG-048, F-DBG-049, F-TRG-018, F-PMC-048, F-DBG-001, F-DBG-017,
  F-PMC-007 (parent of folded bins hosted here)
- Sample: debug entry (CG-DBG-001 event) that follows a dret with dbg_model.step_armed==1, where
  step_armed is the post-op value of dcsr.step in the CSR model after the last dcsr write op of the
  preceding debug window (csrrw: wdata[2]; csrrs: old | wdata[2]; csrrc: old & ~wdata[2]),
  confirmed by the dcsr readback where the program reads it; condition: `dm_halt_fetch &&
  step_armed`; anti-vacuity: step_armed is never taken from the raw write data (a csrrc with bit 2
  set clears step, a csrrw with bit 2 clear clears it), so a sample is taken only when the model
  says the hardware had step = 1 at the dret; the stepped class comes from the zero or one
  instruction (one record, or the micro-op records of one Zcmp sequence, C-12) between the dret and
  the re-entry, so a hit proves what was stepped.
- Coverpoints:
  - cp_stepped = class of the single non-debug instruction (decoded from rvfi_insn, rvfi_pc_wdata, rvfi_mem_*mask and the bus monitors): bins alu{32-bit integer/ALU op, no memory access, no control transfer}, comp{16-bit non-branch}, load_fast{load with rvalid at minimum latency}, load_slow{load with rvalid delayed}, store_slow{store with gnt/rvalid delayed}, div{div/divu/rem/remu}, mulh{mulh/mulhsu/mulhu}, br_taken{conditional branch with rvfi_pc_wdata != pc + size}, br_not{32-bit branch not taken}, c_br_not{c.beqz/c.bnez not taken}, jal{jal/c.jal/c.j}, jalr{jalr/c.jr/c.jalr}, mret{rvfi_insn == MRET}, wfi{rvfi_insn == WFI}, fence_i{rvfi_insn == FENCE.I}, csr_flush{CSR write causing a pipeline flush}, ecall{rvfi_insn == ECALL, rvfi_trap = 1}, illegal{illegal instruction, rvfi_trap = 1}, ebreak_exc{ebreak with ebreakX=0: rvfi_trap = 1}, ebreak_dbg{ebreak with ebreakX=1: rvfi_trap = 0 (S-2)}, zcmp_push{cm.push}, zcmp_pop{cm.pop}, zcmp_popret{cm.popret/popretz}, zcmp_mv{cm.mvsa01/mva01s}, jump_fault_tgt{jump whose target fetch faults}, load_fault{load PMP/bus fault, rvfi_trap = 1}, store_fault{store PMP/bus fault, rvfi_trap = 1}, trig_hit{trigger on the first instruction, zero retirements}
  - cp_prv = privilege of the stepped instruction (rvfi_mode / dcsr.prv): bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_pending = interrupt pending during the step window: bins none{irq_pending_o = 0 and irq_nm_i = 0 throughout the window}, irq{enabled interrupt pending (irq_pending_o = 1)}, nmi{irq_nm_i = 1}
  - cp_haltreq = debug_req_i high during the step window (driver log): bins no{0}, yes{1: either the request rose after the stepped instruction entered ID (its record carries rvfi_ext_debug_req = 0, C-3; one retirement, cause 3) or it was already high in the first DECODE after the dret's FLUSH (immediate re-halt with zero retirements, cp_retired.none, TP-DBG-054)}
  - cp_cause = dcsr.cause readback at re-entry (cross operand only; owner CG-DBG-001.cp_cause): bins step{DBG_CAUSE_STEP}, ebreak{DBG_CAUSE_EBREAK}, trigger{DBG_CAUSE_TRIGGER}, haltreq{DBG_CAUSE_HALTREQ}
  - cp_retired = non-debug instructions between dret and re-entry (an expanded Zcmp sequence is ONE instruction: its micro-op records all carry rvfi_ext_expanded_insn_valid = 1 and only the last rvfi_ext_expanded_insn_last = 1, C-12): bins none{0 instructions: immediate re-halt}, one_ok{1 instruction whose record(s) have rvfi_trap = 0; includes the ebreak-into-debug record (S-2)}, one_trap{1 instruction with rvfi_trap = 1}
  - cp_minstret_delta = minstret readback delta across the step (the debug program reads minstret in every window: TP-PMC-050 only): bins zero{0}, one{1}
- Crosses:
  - cr_stepped_prv = cp_stepped x cp_prv: bins alu_m{alu,m}, comp_m{comp,m}, loadfast_m{load_fast,m}, loadslow_m{load_slow,m}, storeslow_m{store_slow,m}, div_m{div,m}, mulh_m{mulh,m}, brtaken_m{br_taken,m}, brnot_m{br_not,m}, cbrnot_m{c_br_not,m}, jal_m{jal,m}, jalr_m{jalr,m}, mret_m{mret,m}, wfi_m{wfi,m}, fencei_m{fence_i,m}, csrflush_m{csr_flush,m}, ecall_m{ecall,m}, illegal_m{illegal,m}, ebreakexc_m{ebreak_exc,m}, ebreakdbg_m{ebreak_dbg,m}, push_m{zcmp_push,m}, pop_m{zcmp_pop,m}, popret_m{zcmp_popret,m}, mv_m{zcmp_mv,m}, jumpfault_m{jump_fault_tgt,m}, loadfault_m{load_fault,m}, storefault_m{store_fault,m}, trig_m{trig_hit,m}, alu_u{alu,u}, comp_u{comp,u}, loadslow_u{load_slow,u}, brtaken_u{br_taken,u}, ecall_u{ecall,u}, illegal_u{illegal,u}, ebreakexc_u{ebreak_exc,u}, ebreakdbg_u{ebreak_dbg,u}, wfi_u{wfi,u}, push_u{zcmp_push,u}, trig_u{trig_hit,u}, loadfault_u{load_fault,u}; ignore mret x u: mret in U is an illegal instruction (illegal_u).
  - cr_pending_cause = cp_pending x cp_cause: bins irq_step{irq,step}, nmi_step{nmi,step}, none_step{none,step}
  - cr_haltreq_cause = cp_haltreq x cp_cause: bins yes_haltreq{yes,haltreq}, no_step{no,step}, yes_trigger{yes,trigger}, yes_ebreak{yes,ebreak}
  - cr_stepped_retired = cp_stepped x cp_retired: bins alu_ok{alu,one_ok}, wfi_ok{wfi,one_ok}, mret_ok{mret,one_ok}, push_ok{zcmp_push,one_ok}, popret_ok{zcmp_popret,one_ok}, ecall_trap{ecall,one_trap}, illegal_trap{illegal,one_trap}, ebreakexc_trap{ebreak_exc,one_trap}, ebreakdbg_ok{ebreak_dbg,one_ok}, loadfault_trap{load_fault,one_trap}, jumpfault_ok{jump_fault_tgt,one_ok}, trig_none{trig_hit,none}; ignore ebreak_dbg x one_trap (the former ebreakdbg_trap, retired): the ebreak-into-debug record has rvfi_trap = 0 (rtl/ibex_core.sv:1885-1886, S-2); a trap record for it is a gen_isa_compare failure.
  - cr_stepped_minstret = cp_stepped x cp_minstret_delta: bins alu_one{alu,one}, wfi_one{wfi,one}, ecall_zero{ecall,zero}, illegal_zero{illegal,zero}, push_one{zcmp_push,one}
- Adopted (riscv-dv): none
- TP items: TP-DBG-042, TP-DBG-043, TP-DBG-044, TP-DBG-045, TP-DBG-046, TP-DBG-047, TP-DBG-048, TP-DBG-049, TP-DBG-050, TP-DBG-051, TP-DBG-052, TP-DBG-053, TP-DBG-054, TP-TRG-018, TP-PMC-050

### CG-DBG-007: gen_cg_dbg_dcsr_warl
- Features: F-DBG-012, F-DBG-013, F-DBG-014, F-DBG-015, F-DBG-016, F-DBG-043, F-DBG-057
- Sample: RVFI retirement of a CSR write op (csrrw/csrrwi always; csrrs/csrrc and immediate forms
  with a non-zero source) to CSR_DCSR in debug mode, closed by the following csrr dcsr readback;
  one sample per (write op, dcsr field) pair over the 15 fields of cp_bit, where the model computes
  the field's post-op value from the op semantics applied to the model's current dcsr (csrrw:
  wdata; csrrs: old | wdata; csrrc: old & ~wdata) and compares it with the readback field;
  condition: `rvfi_valid && csr_addr == CSR_DCSR && is_write && rvfi_ext_debug_mode`;
  anti-vacuity: dcsr writes exist only in debug programs and the pattern is randomized; the
  readback class is derived from the observed read value against the post-op prediction, never
  from the raw write data, so a csrrc that clears a bit and an all-zeros pattern are classified
  correctly; a hit in `forced0` proves the hardware legalised a bit the op would have set.
- Coverpoints:
  - cp_pattern = write-data (rs1 / uimm) class of the op: bins zeros{32'h0}, ones{32'hFFFF_FFFF}, walk1{exactly one bit set}, random{>= 2 bits set and not all}, prv_only{only bits 1:0 differ between the post-op and the pre-op value}
  - cp_bit = dcsr field of the sampled (op, field) pair: bins xdebugver{31:28}, z27_16{27:16}, ebreakm{15}, z14{14}, ebreaks{13}, ebreaku{12}, stepie{11}, stopcount{10}, stoptime{9}, cause{8:6}, z5{5}, mprven{4}, nmip{3}, step{2}, prv{1:0}
  - cp_prv_w = prv value written: bins u{2'b00}, s{2'b01}, h{2'b10}, m{2'b11}
  - cp_readback = per-field readback class against the post-op prediction: bins as_written{writable field (ebreakm, ebreaku, step, prv 00/11) with readback == post-op value}, forced0{hardwired-0 field with post-op value 1: readback 0}, nop0{hardwired-0 field with post-op value 0: readback 0 (witness; not in manifest)}, forced_const{xdebugver reads 4 / cause reads the entry cause whatever the post-op value}, legalised_u{prv post-op 01/10 read 00}
  - cp_op = CSR op: bins rw{csrrw}, rs{csrrs}, rc{csrrc}, rwi{csrrwi}, rsi{csrrsi}, rci{csrrci}
- Crosses:
  - cr_bit_rb = cp_bit x cp_readback: bins ebreakm_w{ebreakm,as_written}, ebreaku_w{ebreaku,as_written}, step_w{step,as_written}, ebreaks_w{ebreaks,as_written}, prv_w{prv,as_written}, prv_leg{prv,legalised_u}, stepie_0{stepie,forced0}, stopcount_0{stopcount,forced0}, stoptime_0{stoptime,forced0}, mprven_0{mprven,forced0}, nmip_0{nmip,forced0 (B5 evidence: the RTL hardwires nmip to 0 while an NMI is held pending in debug mode)}, z27_0{z27_16,forced0}, z14_0{z14,forced0}, z5_0{z5,forced0}, cause_c{cause,forced_const}, xdv_c{xdebugver,forced_const}; ignore_bins ebreaks_0{ebreaks,forced0}: the spec-expected readback (core_registers.xml:163-172, hardwired 0 without S-mode) that the RTL cannot produce while B15 stands (rtl/ibex_cs_registers.sv:810-836 stores bit 13); re-enable when B15 is fixed; ignore ebreakm/ebreaku/step x forced0 and hardwired fields x as_written: contradictions are gen_chk_csr_readback failures; ignore * x nop0: witness. The checker's forced-0 field set is {z27_16, z14, ebreaks, stepie, stopcount, stoptime, z5, mprven, nmip} (writable mask 32'h0000_9007 plus prv WARL); ebreaks_w is the B15 evidence bin: the RTL reads bit 13 back as written and the checker fails on it (TP-DBG-018 expected-fail).
  - cr_pattern_op = cp_pattern x cp_op: bins zeros_rw{zeros,rw}, zeros_rc{zeros,rc}, ones_rw{ones,rw}, ones_rs{ones,rs}, ones_rc{ones,rc}, walk_rw{walk1,rw}, walk_rs{walk1,rs}, walk_rc{walk1,rc}, rand_rw{random,rw}, rand_rs{random,rs}, rand_rc{random,rc}, prv_rwi{prv_only,rwi}, prv_rsi{prv_only,rsi}, prv_rci{prv_only,rci}
  - cr_prvw_rb = cp_prv_w x cp_readback: bins s_leg{s,legalised_u}, h_leg{h,legalised_u}, m_w{m,as_written}, u_w{u,as_written}
- Adopted (riscv-dv): none
- TP items: TP-DBG-018, TP-DBG-019, TP-DBG-020, TP-DBG-068, TP-DBG-073

### CG-DBG-008: gen_cg_dbg_csr_access
- Features: F-DBG-012, F-DBG-035, F-DBG-050, F-DBG-051, F-DBG-060
- Sample: RVFI item whose rvfi_insn is a CSR access to CSR_DCSR, CSR_DPC, CSR_DSCRATCH0 or CSR_DSCRATCH1;
  condition: `rvfi_valid && csr_addr inside {CSR_DCSR, CSR_DPC, CSR_DSCRATCH0, CSR_DSCRATCH1}`;
  anti-vacuity: the result bin comes from rvfi_trap vs rvfi_rd_wdata and the mode from rvfi_mode /
  rvfi_ext_debug_mode, so a hit proves the access was attempted in that mode and what happened.
- Coverpoints:
  - cp_csr = CSR address decoded from rvfi_insn: bins dcsr{CSR_DCSR}, dpc{CSR_DPC}, dscratch0{CSR_DSCRATCH0}, dscratch1{CSR_DSCRATCH1}
  - cp_mode = rvfi_ext_debug_mode x rvfi_mode (cross operand only; owner CG-DBG-012.cp_mode_dbg): bins dbg_m{debug, M}, dbg_u{debug, U after mret-in-debug}, m{not debug, M}, u{not debug, U}
  - cp_op = CSR op decoded from rvfi_insn: bins read{csrrs/csrrc rs1==x0 or csrrsi/csrrci uimm==0}, write{csrrw/csrrwi}, set{csrrs/csrrsi non-zero}, clear{csrrc/csrrci non-zero}
  - cp_result = {rvfi_trap, readback relation}: bins ok{no trap}, illegal{rvfi_trap, mcause 2}
  - cp_dpc_w = dpc write data bit 0: bins even{0}, odd{1}
  - cp_scratch_pat = dscratch write data: bins zeros{0}, ones{32'hFFFF_FFFF}, alt{32'hAAAA_5555 or 32'h5555_AAAA}, random{any other value}
- Crosses:
  - cr_csr_mode_result = cp_csr x cp_mode x cp_result: bins dcsr_dbg_ok{dcsr,dbg_m,ok}, dpc_dbg_ok{dpc,dbg_m,ok}, ds0_dbg_ok{dscratch0,dbg_m,ok}, ds1_dbg_ok{dscratch1,dbg_m,ok}, dcsr_m_ill{dcsr,m,illegal}, dpc_m_ill{dpc,m,illegal}, ds0_m_ill{dscratch0,m,illegal}, ds1_m_ill{dscratch1,m,illegal}, dcsr_u_ill{dcsr,u,illegal}, dpc_u_ill{dpc,u,illegal}, ds0_u_ill{dscratch0,u,illegal}, ds1_u_ill{dscratch1,u,illegal}, dcsr_dbgu_ill{dcsr,dbg_u,illegal}; ignore * x m x ok, * x u x ok, * x dbg_m x illegal: checker failures.
  - cr_csr_op = cp_csr x cp_op: bins dcsr_rd{dcsr,read}, dcsr_wr{dcsr,write}, dcsr_set{dcsr,set}, dcsr_clr{dcsr,clear}, dpc_rd{dpc,read}, dpc_wr{dpc,write}, dpc_set{dpc,set}, dpc_clr{dpc,clear}, ds0_rd{dscratch0,read}, ds0_wr{dscratch0,write}, ds0_set{dscratch0,set}, ds0_clr{dscratch0,clear}, ds1_rd{dscratch1,read}, ds1_wr{dscratch1,write}, ds1_set{dscratch1,set}, ds1_clr{dscratch1,clear}
  - cr_dpcw_result = cp_dpc_w x cp_result: bins even_ok{even,ok}, odd_ok{odd,ok}
  - cr_scratch_pat_csr = cp_scratch_pat x cp_csr: bins zeros_ds0{zeros,dscratch0}, ones_ds0{ones,dscratch0}, alt_ds0{alt,dscratch0}, rand_ds0{random,dscratch0}, zeros_ds1{zeros,dscratch1}, ones_ds1{ones,dscratch1}, alt_ds1{alt,dscratch1}, rand_ds1{random,dscratch1}
- Adopted (riscv-dv): none
- TP items: TP-DBG-017, TP-DBG-018, TP-DBG-039, TP-DBG-040, TP-DBG-055, TP-DBG-056, TP-DBG-064, TP-DBG-068

### CG-DBG-009: gen_cg_dbg_irq_mask
- Features: F-DBG-002, F-DBG-042, F-DBG-043, F-DBG-056, F-DBG-057, F-DBG-058, F-TRG-025, F-DBG-001,
  F-DBG-037 (parent of folded bins hosted here)
- Sample: one sample per pending episode: an enabled interrupt (irq model: |(pins & mie) with
  mstatus.MIE or U-mode) or irq_nm_i is pending while dbg_model.debug_mode==1 or step_window==1, or
  in the debug-entry decision cycle; closed when the disposition is known (first post-window RVFI
  item, or the driver deasserting); condition: `irq_pending_model && (debug_mode || step_window ||
  entry_cycle)`; anti-vacuity: the irq driver runs independently of debug windows, so overlap is not
  guaranteed; a hit proves an interrupt was pending inside a debug/step window, and the disposition
  is decoded from rvfi_intr / mepc readback, not from expectation.
- Coverpoints:
  - cp_src = interrupt source pin: bins sw{irq_software_i}, timer{irq_timer_i}, ext{irq_external_i}, fast{any of $bits(irq_fast_i) lines}, nmi{irq_nm_i}
  - cp_window = dbg_model window in which the interrupt was pending: bins debug{debug_mode}, step{between dret with step=1 and re-entry}, entry_cycle{pending in the debug-entry decision cycle}, irq_taken_then_req{debug_req_i arriving while IRQ_TAKEN is in progress}
  - cp_disposition = disposition decoded from rvfi_intr / mepc readback / driver log: bins masked_then_taken{taken at the first instruction after the window, mepc == dpc}, masked_still_pending{driver deasserted before the window ended, never taken}, debug_wins_entry{debug entered instead of the handler}, handler_then_debug{handler entry completed, then debug with dpc == vector}
  - cp_prv_after = privilege after the window (dcsr.prv): bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
- Crosses:
  - cr_src_window = cp_src x cp_window: bins sw_debug{sw,debug}, timer_debug{timer,debug}, ext_debug{ext,debug}, fast_debug{fast,debug}, nmi_debug{nmi,debug}, sw_step{sw,step}, timer_step{timer,step}, ext_step{ext,step}, fast_step{fast,step}, nmi_step{nmi,step}, sw_entry{sw,entry_cycle}, ext_entry{ext,entry_cycle}, fast_entry{fast,entry_cycle}, nmi_entry{nmi,entry_cycle}, ext_irqtaken{ext,irq_taken_then_req}, fast_irqtaken{fast,irq_taken_then_req}
  - cr_window_disp = cp_window x cp_disposition: bins debug_taken{debug,masked_then_taken}, debug_pending{debug,masked_still_pending}, step_taken{step,masked_then_taken}, step_pending{step,masked_still_pending}, entry_wins{entry_cycle,debug_wins_entry}, irqtaken_handler{irq_taken_then_req,handler_then_debug}
  - cr_src_prv = cp_src x cp_prv_after: bins sw_m{sw,m}, sw_u{sw,u}, timer_m{timer,m}, timer_u{timer,u}, ext_m{ext,m}, ext_u{ext,u}, fast_m{fast,m}, fast_u{fast,u}, nmi_m{nmi,m}, nmi_u{nmi,u}
- Adopted (riscv-dv): none
- TP items: TP-DBG-003, TP-DBG-016, TP-DBG-021, TP-DBG-047, TP-DBG-048, TP-DBG-061, TP-DBG-062, TP-DBG-068, TP-TRG-025

### CG-DBG-010: gen_cg_dbg_pmp_dm
- Features: F-DBG-027, F-DBG-030, F-DBG-033, F-DBG-052, F-DBG-053, F-DBG-054, F-DBG-055
- Sample: every fetch word (ibus request) and every data access (dbus request, or a PMP-model-denied
  access with the request suppressed and rvfi_trap) while dbg_model.debug_mode==1, plus data
  accesses in the post-dret window with MPRV still set (B1); condition: `(ibus_req || dbus_req ||
  pmp_model_denied) && (debug_mode || post_dret_mprv_window)`; anti-vacuity: addresses are
  randomized inside and outside the DM window and the PMP configuration is randomized to deny or
  allow them; the verdict bin comes from gen_chk_pmp's model for the effective privilege, so
  `deny_cfg x no_fault` can only be hit when the bypass fired.
- Coverpoints:
  - cp_access = access type (ibus request / dbus request with data_we_o): bins fetch{ibus request}, load{dbus request with data_we_o = 0}, store{dbus request with data_we_o = 1}
  - cp_addr = address class vs DmBaseAddr/DmAddrMask: bins dm_base{== DmBaseAddr}, dm_top{last word of the window, (DmBaseAddr|DmAddrMask)-3}, dm_in{inside, other}, dm_straddle{4-byte fetch at (DmBaseAddr|DmAddrMask)-1, second half outside}, below{[DmBaseAddr-4 : DmBaseAddr-1]}, above{[DmBaseAddr+DmAddrMask+1 : DmBaseAddr+DmAddrMask+4]}, far{outside, other}
  - cp_verdict = gen_chk_pmp verdict at the effective privilege ignoring the DM bypass: bins allow_cfg{a matching region grants the access}, deny_cfg{region denies}, deny_mmwp{no matching region, MMWP=1}, deny_mml{MML locked region without the permission}
  - cp_lsu_priv = effective LSU privilege (mstatus.MPRV ? MPP : priv): bins m{privilege M with MPRV=0, or MPRV=1 with MPP=M}, u_mprv{MPRV=1, MPP=U}, u_mode{priv U after mret-in-debug or after dret to U}
  - cp_result = {rvfi_trap, readback relation}: bins no_fault{request issued, no trap}, fault{rvfi_trap, DmExceptionAddr fetch or mtvec fetch}
  - cp_phase = dbg_model phase of the access: bins in_debug{debug_mode}, post_dret_u_mprv{U-mode after dret with MPRV=1, MPP=M}
- Crosses:
  - cr_bypass = cp_access x cp_addr x cp_verdict x cp_result: bins f_base_deny_ok{fetch,dm_base,deny_cfg,no_fault}, f_top_deny_ok{fetch,dm_top,deny_cfg,no_fault}, f_in_deny_ok{fetch,dm_in,deny_cfg,no_fault}, l_base_deny_ok{load,dm_base,deny_cfg,no_fault}, l_top_deny_ok{load,dm_top,deny_cfg,no_fault}, l_in_deny_ok{load,dm_in,deny_cfg,no_fault}, s_base_deny_ok{store,dm_base,deny_cfg,no_fault}, s_top_deny_ok{store,dm_top,deny_cfg,no_fault}, s_in_deny_ok{store,dm_in,deny_cfg,no_fault}, f_straddle_fault{fetch,dm_straddle,deny_cfg,fault}, f_below_fault{fetch,below,deny_cfg,fault}, f_above_fault{fetch,above,deny_cfg,fault}, l_below_fault{load,below,deny_cfg,fault}, l_above_fault{load,above,deny_cfg,fault}, s_below_fault{store,below,deny_cfg,fault}, s_above_fault{store,above,deny_cfg,fault}, f_far_allow{fetch,far,allow_cfg,no_fault}, l_far_allow{load,far,allow_cfg,no_fault}, s_far_allow{store,far,allow_cfg,no_fault}, f_far_mmwp{fetch,far,deny_mmwp,fault}, f_far_mml{fetch,far,deny_mml,fault}, l_far_mmwp{load,far,deny_mmwp,fault}, s_far_mml{store,far,deny_mml,fault}, l_in_mmwp_ok{load,dm_in,deny_mmwp,no_fault}, f_in_mml_ok{fetch,dm_in,deny_mml,no_fault}; ignore dm_* x deny_* x fault while in_debug: bypass failure is a gen_chk_pmp failure.
  - cr_lsu_priv = cp_access x cp_lsu_priv x cp_verdict x cp_result: bins l_umprv_far_fault{load,u_mprv,deny_cfg,fault}, s_umprv_far_fault{store,u_mprv,deny_cfg,fault}, l_m_far_ok{load,m,allow_cfg,no_fault}, l_umprv_dm_ok{load,u_mprv,deny_cfg,no_fault}, l_umode_far_fault{load,u_mode,deny_cfg,fault}, f_umode_fault{fetch,u_mode,deny_cfg,fault}; (B2 evidence: l_umprv_far_fault, s_umprv_far_fault)
  - cr_b1 = cp_phase x cp_access x cp_verdict x cp_result: bins b1_load_ok{post_dret_u_mprv,load,deny_cfg,no_fault}, b1_store_ok{post_dret_u_mprv,store,deny_cfg,no_fault}, dbg_load_ok{in_debug,load,allow_cfg,no_fault}; (B1 evidence: b1_load_ok, b1_store_ok: the verdict is computed for privilege U, the RTL used MPP=M)
- Adopted (riscv-dv): none
- TP items: TP-DBG-032, TP-DBG-033, TP-DBG-038, TP-DBG-057, TP-DBG-058, TP-DBG-059, TP-DBG-060, TP-DBG-064, TP-DBG-068

### CG-DBG-011: gen_cg_dbg_mode_misc
- Features: F-DBG-011, F-DBG-059, F-DBG-060, F-DBG-062, F-DBG-063, F-DBG-064, F-DBG-067
- Sample: three events, each guarded per coverpoint with `iff` (S-3c): (a) RVFI retirement with
  rvfi_ext_debug_mode==1 (debug-program instruction) drives cp_insn_class, cp_wfi_pending,
  cp_mret_mpp, cp_mode and cp_wfi_busy_dip (`iff rvfi_evt`); (b) each ibus request while
  dbg_model.debug_mode==1 drives cp_fetch_repeat and cp_icache_en (`iff ibus_evt`); (c) the dret
  retirement drives cp_counter_moved with the deltas computed by gen_chk_counters over the window
  (`iff dret_evt`); condition: `(rvfi_valid && rvfi_ext_debug_mode) || (ibus_req && debug_mode)
  || dret_retired`; anti-vacuity: only debug-program instructions carry the flag; `repeat` is
  decoded from the ibus address history of the window, so a hit proves a re-fetch of an
  already-fetched address (the icache would have hit).
- Coverpoints:
  - cp_insn_class (iff rvfi_evt) = debug-program instruction class decoded from rvfi_insn: bins alu{integer op, no memory, no control transfer}, load{rvfi_mem_rmask != 0}, store{rvfi_mem_wmask != 0}, csr_dbg{CSR access to dcsr/dpc/dscratch0/1}, csr_trig{CSR access to tselect/tdata1/tdata2}, csr_other{any other CSR access}, wfi{WFI}, mret{MRET}, ecall{ECALL}, fence_i{FENCE.I}, jump{jal/jalr and compressed forms}, branch{conditional branch}, dret{DRET}, illegal{illegal encoding, rvfi_trap = 1}, ebreak{ebreak/c.ebreak (re-entry, CG-DBG-003.cp_outcome.reenter)}
  - cp_wfi_pending (iff rvfi_evt && insn == WFI) = irq pending when a wfi retires in debug mode: bins none{irq_pending_o = 0 and irq_nm_i = 0 in W-DEC(wfi)}, irq_pending{irq_pending_o = 1 or irq_nm_i = 1 in W-DEC(wfi)}
  - cp_mret_mpp (iff rvfi_evt && insn == MRET) = mstatus.MPP when mret retires in debug mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_fetch_repeat (iff ibus_evt) = ibus fetch address in the debug window: bins first{not fetched before in this window}, repeat{fetched earlier in the same window}
  - cp_icache_en (iff ibus_evt) = cpuctrlsts.icache_enable (CSR model): bins off{0}, on{1}
  - cp_counter_moved (iff dret_evt) = counter deltas across the debug window: bins mcycle{mcycle delta > 0}, minstret{minstret delta == debug-program retirements incl. dret (the debug program reads minstret)}, hpm{some mhpmcounterN, N in [MHPMCOUNTER_BASE : HPM_LAST], delta > 0 on rvfi_ext_mhpmcounters}
  - cp_mode (iff rvfi_evt) = rvfi_mode inside debug mode (cross operand only; owner CG-DBG-012.cp_mode_dbg): bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_wfi_busy_dip (iff rvfi_evt && insn == WFI) = number of consecutive core_busy_o Off cycles between a debug-mode wfi retirement and the next ibus request, classified with the core_busy_o port rule: bins one{1 with no masking source active in W-WAITSLEEP(wfi)}, hidden{0 while an ibus beat was outstanding, the invalidation sweep active or a dbus access outstanding in W-WAITSLEEP(wfi)}; anti-vacuity: sampled only on a wfi with rvfi_ext_debug_mode==1; an unmasked count other than 1 is a gen_chk_sleep failure (WAIT_SLEEP is one cycle and SLEEP stays busy with debug_mode_q set, rtl/ibex_controller.sv:598-621), so `one` proves the one-cycle shape was observed and `hidden` proves the masking source was logged.
- Crosses:
  - cr_fetch_icache = cp_fetch_repeat x cp_icache_en: bins repeat_on{repeat,on}, first_on{first,on}, repeat_off{repeat,off}; (repeat_on proves the forced-off icache: the re-fetch reached the bus although the cache was enabled)
  - cr_wfi = cp_insn_class x cp_wfi_pending: bins wfi_irq{wfi,irq_pending}, wfi_none{wfi,none}
  - cr_wfi_busy = cp_wfi_pending x cp_wfi_busy_dip: bins irq_one{irq_pending,one}, none_one{none,one}, irq_hidden{irq_pending,hidden}, none_hidden{none,hidden}
  - cr_mret_mpp = cp_insn_class x cp_mret_mpp: bins mret_m{mret,m}, mret_u{mret,u}
  - cr_class_mode = cp_insn_class x cp_mode: bins alu_u{alu,u}, csrdbg_u{csr_dbg,u}, load_u{load,u}, alu_m{alu,m}, dret_m{dret,m}, dret_u{dret,u}
- Adopted (riscv-dv): none
- TP items: TP-DBG-001, TP-DBG-028, TP-DBG-031, TP-DBG-034, TP-DBG-036, TP-DBG-063, TP-DBG-064, TP-DBG-065, TP-DBG-066, TP-DBG-068, TP-PMC-049

### CG-DBG-012: gen_cg_dbg_rvfi_flags
- Features: F-DBG-064, F-DBG-065
- Sample: every rvfi_valid; condition: `rvfi_valid`; discriminating condition (S-3a): the bins
  req1_mode0, req0_mode1, req1_mode1, u_dbg, trap_dbg, ok_dbg and every cr_flags_mode bin need a
  debug request overlapping a retirement, a debug program or a trap in debug mode; req0_mode0, m
  and ok are hit by every ordinary retirement and are witness bins (not in manifest);
  anti-vacuity: rvfi_ext_debug_req is the debug_req_i level at the record's IF->ID transfer (or
  captured_debug_req, C-3), so a hit in req1_mode0 proves one of the two mechanisms that let an
  instruction enter ID with the request registered: a Zcmp micro-op during the expansion mask
  (rtl/ibex_controller.sv:474-477) or the sticky capture after a dropped pulse
  (rtl/ibex_core.sv:1949-1957); an ordinary instruction never enters ID while debug_req_i is high
  outside debug mode (halt_if), so "slow memory" alone never produces it.
- Coverpoints:
  - cp_flags = {rvfi_ext_debug_req, rvfi_ext_debug_mode}: bins req0_mode0{2'b00 (witness; not in manifest)}, req1_mode0{2'b10: a Zcmp micro-op entering ID during the mask with debug_req_i high, or the first instruction entering ID after a dropped pulse that landed on an empty ID (TP-DBG-010)}, req0_mode1{2'b01: debug-program record with the request released}, req1_mode1{2'b11: the first debug-ROM record of a held-request entry (raw level or captured_debug_req), or any debug-program record with the request still high}
  - cp_mode_dbg = {rvfi_mode, rvfi_ext_debug_mode} (owner of the mode-in-debug coverpoint; CG-DBG-004/008/011 hold cross-operand copies): bins m_dbg{PRIV_LVL_M,1}, u_dbg{PRIV_LVL_U,1}, m{PRIV_LVL_M,0 (witness; not in manifest)}, u{PRIV_LVL_U,0}
  - cp_trap_dbg = {rvfi_trap, rvfi_ext_debug_mode}: bins trap_dbg{1,1: exception in debug mode or an ebreak re-entry with the enable bit clear (S-2)}, trap{1,0}, ok_dbg{0,1}, ok{0,0 (witness; not in manifest)}
- Crosses:
  - cr_flags_mode = cp_flags x cp_mode_dbg: bins req1_m{req1_mode0,m}, req1_u{req1_mode0,u}, mode1_m{req0_mode1,m_dbg}, mode1_u{req0_mode1,u_dbg}
- Adopted (riscv-dv): none
- TP items: TP-DBG-001, TP-DBG-002, TP-DBG-004, TP-DBG-006, TP-DBG-009, TP-DBG-010, TP-DBG-031, TP-DBG-036, TP-DBG-064, TP-DBG-068, TP-DBG-070

---------------------------------------------------------------------------------------------------

## TRG covergroups

### CG-TRG-001: gen_cg_trg_csr
- Features: F-TRG-001, F-TRG-002, F-TRG-003, F-TRG-004, F-TRG-005, F-TRG-006, F-TRG-007, F-TRG-008, F-TRG-009, F-TRG-028, F-TRG-029
- Sample: RVFI item whose rvfi_insn is a CSR access to {CSR_TSELECT, CSR_TDATA1, CSR_TDATA2,
  CSR_TDATA3, CSR_MCONTEXT, CSR_MSCONTEXT, CSR_SCONTEXT, 12'h7A4 (tinfo), 12'h7A5 (tcontrol)};
  write effect closed by the following csrr of the same CSR; condition: `rvfi_valid && csr_addr
  inside trigger_csr_set`; anti-vacuity: result bins come from rvfi_trap and the observed readback,
  so `ok_dropped` proves a write reached the CSR unit in that mode and did not stick, and `illegal`
  proves the trap.
- Coverpoints:
  - cp_csr = CSR address decoded from rvfi_insn: bins tselect{CSR_TSELECT}, tdata1{CSR_TDATA1}, tdata2{CSR_TDATA2}, tdata3{CSR_TDATA3}, mcontext{CSR_MCONTEXT}, mscontext{CSR_MSCONTEXT}, scontext{CSR_SCONTEXT}, tinfo{12'h7A4}, tcontrol{12'h7A5}
  - cp_mode = {rvfi_ext_debug_mode, rvfi_mode}: bins dbg{debug mode}, m{M, not debug}, u{U}
  - cp_op = CSR op decoded from rvfi_insn: bins read{no write}, write{csrrw/csrrwi}, set{csrrs non-zero}, clear{csrrc non-zero}
  - cp_result = {rvfi_trap, readback relation}: bins ok_applied{write, no trap, readback == the WARL prediction and != the pre-write value}, ok_dropped{write, no trap, readback unchanged}, ok_read{read, no trap}, illegal{rvfi_trap}
  - cp_tsel_w = tselect write data: bins zero{0}, one{1}, big{[2 : 32'hFFFF_FFFE]}, ones{32'hFFFF_FFFF}
  - cp_td1_w = tdata1 write-data class of the non-execute bits: bins zeros{all other bits 0}, ones{all other bits 1}, type_ne2{type field != 2}, dmode0{dmode bit 0}, ldst{load/store bits set}, match_nz{match field != 0}, action0{action field 0}, chain{chain bit}, hit1{bit 20 set}, random{any other value}
  - cp_td1_exec_w = post-op value of tdata1 bit 2 (csrrw: wdata[2]; csrrs: old_exec | wdata[2]; csrrc: old_exec & ~wdata[2]; the RTL captures the merged value, rtl/ibex_cs_registers.sv:1004-1005, :1788, so a csrrc with all-ones clears execute): bins zero{0}, one{1}
  - cp_td2_w = tdata2 write data: bins zero{0}, ones{32'hFFFF_FFFF}, odd{bit0=1}, halfword{bit1=1,bit0=0}, msb{32'h8000_0000}, random{any other value}
  - cp_td1_rb = tdata1 readback: bins dis{32'h2800_1048}, en{32'h2800_104C}, en_after_hit{32'h2800_104C read in the first debug window after a cause-2 entry: hit (bit 20) still 0, F-TRG-028 folded into F-TRG-003}
- Crosses:
  - cr_csr_mode_result = cp_csr x cp_mode x cp_result: bins tsel_dbg_drop{tselect,dbg,ok_dropped}, td1_dbg_app{tdata1,dbg,ok_applied}, td2_dbg_app{tdata2,dbg,ok_applied}, tsel_m_drop{tselect,m,ok_dropped}, td1_m_drop{tdata1,m,ok_dropped}, td2_m_drop{tdata2,m,ok_dropped}, td3_dbg_drop{tdata3,dbg,ok_dropped}, td3_m_drop{tdata3,m,ok_dropped}, mctx_dbg_drop{mcontext,dbg,ok_dropped}, mctx_m_drop{mcontext,m,ok_dropped}, msctx_dbg_drop{mscontext,dbg,ok_dropped}, msctx_m_drop{mscontext,m,ok_dropped}, sctx_dbg_drop{scontext,dbg,ok_dropped}, sctx_m_drop{scontext,m,ok_dropped}, tsel_u_ill{tselect,u,illegal}, td1_u_ill{tdata1,u,illegal}, td2_u_ill{tdata2,u,illegal}, td3_u_ill{tdata3,u,illegal}, mctx_u_ill{mcontext,u,illegal}, msctx_u_ill{mscontext,u,illegal}, sctx_u_ill{scontext,u,illegal}, tinfo_u_ill{tinfo,u,illegal}, tctl_u_ill{tcontrol,u,illegal}, tinfo_dbg_ill{tinfo,dbg,illegal}, tinfo_m_ill{tinfo,m,illegal}, tctl_dbg_ill{tcontrol,dbg,illegal}, tctl_m_ill{tcontrol,m,illegal}, tsel_dbg_rd{tselect,dbg,ok_read}, tsel_m_rd{tselect,m,ok_read}, td1_dbg_rd{tdata1,dbg,ok_read}, td1_m_rd{tdata1,m,ok_read}, td2_dbg_rd{tdata2,dbg,ok_read}, td2_m_rd{tdata2,m,ok_read}, td3_dbg_rd{tdata3,dbg,ok_read}, td3_m_rd{tdata3,m,ok_read}, mctx_dbg_rd{mcontext,dbg,ok_read}, mctx_m_rd{mcontext,m,ok_read}, msctx_dbg_rd{mscontext,dbg,ok_read}, msctx_m_rd{mscontext,m,ok_read}, sctx_dbg_rd{scontext,dbg,ok_read}, sctx_m_rd{scontext,m,ok_read}; ignore tinfo/tcontrol x ok_*: never decoded; ignore tdata3/mcontext/mscontext/scontext x ok_applied: no storage (B3 evidence bins: the tdata3/mcontext/mscontext/scontext *_drop and *_rd bins record the RTL's read-0 / write-drop where Sdtrig expects `illegal`; they are hit by the expected-fail item TP-TRG-008 only); ignore_bins tsel_dbg_app{tselect,dbg,ok_applied}: with DbgHwBreakNum = 1 tselect always reads 0, so no write can change the readback (the former must-hit bin; TP-TRG-001 now requires tsel_dbg_drop).
  - cr_td1_exec_rb = cp_td1_exec_w x cp_td1_rb: bins e0_dis{zero,dis}, e1_en{one,en}; ignore zero x en, one x dis: WARL failure is a gen_chk_csr_readback failure.
  - cr_td1w_exec = cp_td1_w x cp_td1_exec_w: bins zeros_e0{zeros,zero}, zeros_e1{zeros,one}, ones_e0{ones,zero}, ones_e1{ones,one}, type_e1{type_ne2,one}, dmode0_e1{dmode0,one}, ldst_e1{ldst,one}, ldst_e0{ldst,zero}, match_e1{match_nz,one}, action0_e1{action0,one}, chain_e1{chain,one}, hit1_e1{hit1,one}, rand_e0{random,zero}, rand_e1{random,one}
  - cr_tselw_mode = cp_tsel_w x cp_mode: bins zero_dbg{zero,dbg}, one_dbg{one,dbg}, big_dbg{big,dbg}, ones_dbg{ones,dbg}, one_m{one,m}, ones_m{ones,m}
  - cr_td2w_mode = cp_td2_w x cp_mode: bins zero_dbg{zero,dbg}, ones_dbg{ones,dbg}, odd_dbg{odd,dbg}, half_dbg{halfword,dbg}, msb_dbg{msb,dbg}, rand_dbg{random,dbg}, rand_m{random,m}
  - cr_csr_op = cp_csr x cp_op: bins tsel_set{tselect,set}, tsel_clr{tselect,clear}, td1_set{tdata1,set}, td1_clr{tdata1,clear}, td2_set{tdata2,set}, td2_clr{tdata2,clear}, td3_wr{tdata3,write}, mctx_wr{mcontext,write}, msctx_wr{mscontext,write}, sctx_wr{scontext,write}, tinfo_rd{tinfo,read}, tinfo_wr{tinfo,write}, tctl_rd{tcontrol,read}, tctl_wr{tcontrol,write}
- Adopted (riscv-dv): none
- TP items: TP-TRG-001, TP-TRG-002, TP-TRG-003, TP-TRG-004, TP-TRG-005, TP-TRG-006, TP-TRG-007, TP-TRG-008, TP-TRG-009, TP-TRG-015, TP-TRG-028, TP-TRG-029, TP-TRG-030, TP-TRG-031

### CG-TRG-002: gen_cg_trg_fire
- Features: F-TRG-010, F-TRG-011, F-TRG-012, F-TRG-013, F-TRG-014, F-TRG-015, F-TRG-016, F-TRG-017,
  F-TRG-018, F-TRG-019, F-TRG-020, F-TRG-021, F-TRG-022, F-TRG-023, F-TRG-024, F-TRG-025, F-TRG-026,
  F-TRG-027, F-TRG-030, F-DBG-066, F-DBG-001, F-DBG-031 (parent of folded bins hosted here)
- Sample: one sample each time the TB trigger model (tdata1.execute, tdata2 from the CSR model)
  sees the armed address become the next-to-execute address (derived from RVFI pc_wdata / trap and
  interrupt vectors / dret target / reset boot address), and each cause-2 debug entry; closed when
  either the DmHaltAddr fetch (fired) or the RVFI retirement of the armed address (not fired) is
  observed; condition: `armed_addr_reached || cause2_entry`; anti-vacuity: tdata2 is chosen to lie
  on real program addresses in a randomized fraction of iterations and off-path otherwise;
  `fired`/`not_fired` are decoded from the bus and RVFI, so a hit proves what happened when the
  armed address was reached.
- Coverpoints:
  - cp_ctx = how the armed address was reached / what it holds: bins seq32{32-bit instruction reached sequentially}, comp2{16-bit instruction at addr%4==2}, comp0{16-bit instruction at addr%4==0}, zcmp_first{address of a cm.* instruction}, zcmp_next{successor of a cm.* sequence}, mtvec_exc{exception vector}, mtvec_irq{interrupt vector}, mtvec_nmi{NMI vector mtvec+0x7C}, dret_tgt{dpc at dret}, jalr_tgt{jalr target}, br_tgt{taken-branch target}, fall_taken{fall-through of a taken branch}, fall_nottaken{fall-through of a not-taken branch}, fault_addr{fetch of the address faults (PMP/bus)}, dummy_slot{a dummy instruction was presented with that pc (probe-gated P1, not in manifest)}, ibus_stall{fetch outstanding on the ibus when the match is evaluated}, ebreak_next{address following an ebreak-into-debug (B10; the ebreak record has rvfi_trap = 0, S-2)}, step_first{first instruction after dret with step=1}, in_debug{address executed inside debug mode}
  - cp_priv = privilege at the armed address: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_exec = tdata1.execute: bins off{0}, on{1}
  - cp_td2_lsb = tdata2 bit 0: bins even{0}, b0{1}
  - cp_dit = cpuctrlsts.data_ind_timing: bins off{0}, on{1}
  - cp_fired = trigger disposition decoded from the DmHaltAddr fetch vs RVFI retirement of the armed address: bins fired{DmHaltAddr fetch, cause 2, no retirement of the armed address}, not_fired{armed address retired}
  - cp_cause_rb = dcsr.cause readback at the entry (cross operand only; owner CG-DBG-001.cp_cause): bins trigger{DBG_CAUSE_TRIGGER}, ebreak{DBG_CAUSE_EBREAK}; ignore_bins haltreq_step{DBG_CAUSE_HALTREQ, DBG_CAUSE_STEP}: trigger has priority over haltreq and step whenever the armed address is the next to execute (CTRL-25); `ebreak` is the spec-expected value for the B10 scenario.
  - cp_coincident = dbg_model event pending in the decision cycle: bins none{no other event in W-DEC of the armed address}, haltreq{debug_req_i high}, step{step armed}, irq{enabled interrupt pending}, nmi{irq_nm_i}, ebreak_prev{entry caused by an ebreak whose successor is the armed address}
  - cp_arm_hist = arming history of tdata2 in the seed when the armed address is reached: bins first{execute = 1 for the first time at this address}, rearmed{fired before at this address, execute cleared then set again in later debug windows}, disarmed_after_fire{fired before at this address, execute cleared in the following debug window and still 0 (tdata2 unchanged)}
  - cp_dpc_rel = dpc readback relation (sampled on entries only): bins eq_td2{dpc == tdata2}, eq_ebreak_pc{dpc == pc of the ebreak}; ignore_bins other{any other dpc value}: at a cause-2 or B10 entry dpc is one of the two by construction; any other value is a gen_chk_debug failure.
- Crosses:
  - cr_ctx_fired = cp_ctx x cp_fired: bins seq32_f{seq32,fired}, comp2_f{comp2,fired}, comp0_f{comp0,fired}, zfirst_f{zcmp_first,fired}, znext_f{zcmp_next,fired}, mtvec_exc_f{mtvec_exc,fired}, mtvec_irq_f{mtvec_irq,fired}, mtvec_nmi_f{mtvec_nmi,fired}, dret_f{dret_tgt,fired}, jalr_f{jalr_tgt,fired}, br_f{br_tgt,fired}, fallnt_f{fall_nottaken,fired}, fault_f{fault_addr,fired}, dummy_f{dummy_slot,fired (probe-gated P1, not in manifest)}, stall_f{ibus_stall,fired}, stepfirst_f{step_first,fired}, falltaken_nf{fall_taken,not_fired}, indebug_nf{in_debug,not_fired}, seq32_nf{seq32,not_fired}; ignore fall_taken x fired: a match on a squashed fall-through never enters (checker failure); ignore in_debug x fired: triggers do not fire in debug mode.
  - cr_exec_fired = cp_exec x cp_fired: bins off_nf{off,not_fired}, on_f{on,fired}; ignore off x fired: checker failure.
  - cr_lsb_fired = cp_td2_lsb x cp_fired: bins b0_nf{b0,not_fired}, even_f{even,fired}; ignore b0 x fired: pc_if[0] is always 0.
  - cr_priv_fired = cp_priv x cp_fired: bins m_f{m,fired}, u_f{u,fired}, m_nf{m,not_fired}, u_nf{u,not_fired}
  - cr_dit_fall = cp_dit x cp_ctx x cp_fired: bins dit1_fallnt_f{on,fall_nottaken,fired}, dit1_falltaken_nf{on,fall_taken,not_fired}, dit0_falltaken_nf{off,fall_taken,not_fired}, dit0_fallnt_f{off,fall_nottaken,fired}
  - cr_coinc_cause = cp_coincident x cp_cause_rb: bins none_trig{none,trigger}, haltreq_trig{haltreq,trigger}, step_trig{step,trigger}, irq_trig{irq,trigger}, nmi_trig{nmi,trigger}, ebreakprev_trig{ebreak_prev,trigger}; (B10 evidence: ebreakprev_trig)
  - cr_cause_dpc = cp_cause_rb x cp_dpc_rel: bins trig_td2{trigger,eq_td2}, trig_ebreakpc{trigger,eq_ebreak_pc}, ebreak_ebreakpc{ebreak,eq_ebreak_pc}; (B10 evidence: trig_ebreakpc, an inconsistent pair)
  - cr_hist_fired = cp_arm_hist x cp_fired: bins first_f{first,fired}, rearmed_f{rearmed,fired}, disarmed_nf{disarmed_after_fire,not_fired}; ignore disarmed_after_fire x fired: a fire with execute = 0 is a gen_chk_debug failure.
- Adopted (riscv-dv): none
- TP items: TP-DBG-067, TP-TRG-010, TP-TRG-011, TP-TRG-012, TP-TRG-013, TP-TRG-014, TP-TRG-015, TP-TRG-016, TP-TRG-017, TP-TRG-018, TP-TRG-019, TP-TRG-020, TP-TRG-021, TP-TRG-022, TP-TRG-023, TP-TRG-024, TP-TRG-025, TP-TRG-026, TP-TRG-027, TP-TRG-030, TP-TRG-031, TP-TRG-032

---------------------------------------------------------------------------------------------------

## PMC covergroups

### CG-PMC-001: gen_cg_pmc_mcycle
- Features: F-PMC-001, F-PMC-002, F-PMC-003, F-PMC-004, F-PMC-005, F-PMC-006, F-PMC-047, F-PMC-050, F-PMC-051, F-DBG-063
- Sample: two events, each guarded per coverpoint with `iff` (S-3c): (a) RVFI retirement of a CSR
  access to CSR_MCYCLE / CSR_MCYCLEH (or the cycle/cycleh aliases) drives cp_op, cp_wdata,
  cp_lo_before and cp_carry (`iff csr_evt`); (b) the end of each TB window (WFI sleep, debug
  window, inhibit window, step, inhibit-mid window) where gen_chk_counters compares the mcycle
  delta with elapsed clock cycles drives cp_ctx and cp_delta (`iff window_evt`); condition:
  `(rvfi_valid && csr_addr inside {MCYCLE, MCYCLEH, CYCLE, CYCLEH}) || window_end`; anti-vacuity:
  preload values are randomized so `near_wrap` and `carry` are reached only by construction; the
  delta class is computed from the observed readbacks against the cycle count measured at the
  boundary.
- Coverpoints:
  - cp_op (iff csr_evt) = CSR op decoded from rvfi_insn: bins rd_lo{read mcycle/cycle}, rd_hi{read mcycleh/cycleh}, wr_lo{csrrw/csrrwi mcycle}, wr_hi{csrrw/csrrwi mcycleh}, set_lo{csrrs/csrrsi mcycle, non-zero source}, set_hi{csrrs/csrrsi mcycleh, non-zero source}, clr_lo{csrrc/csrrci mcycle, non-zero source}, clr_hi{csrrc/csrrci mcycleh, non-zero source}
  - cp_wdata (iff csr_evt && is_write) = write data class: bins zeros{0}, ones{32'hFFFF_FFFF}, random{any other value}
  - cp_lo_before (iff csr_evt && is_write) = low word before the write (model value): bins near_wrap{[32'hFFFF_FF00 : 32'hFFFF_FFFF]}, mid{[1 : 32'hFFFF_FEFF]}, zero{0}
  - cp_carry (iff csr_evt && is_read) = low word wrapped with high word incremented since the previous read: bins seen{high word readback == previous high + 1 with low word readback < previous low}, none{no wrap between the two reads}
  - cp_ctx (iff window_evt) = window class: bins run{ordinary code window between two reads}, wfi_sleep{window containing a WFI sleep: core_busy_o Off}, debug{debug window}, inhibited{mcountinhibit.CY=1 for the whole window}, inhibit_mid{mcountinhibit.CY written 1 (or cleared) inside the window}, step{single-step window}
  - cp_delta (iff window_evt) = delta vs measured cycles: bins zero{0 with CY inhibited}, eq_cycles{== elapsed cycles}, eq_written{first read after a write == written + cycles since the write (write-wins rule)}, partial{== cycles before the mid-window inhibit write plus cycles after its clearing}
- Crosses:
  - cr_op_wdata = cp_op x cp_wdata: bins wrlo_z{wr_lo,zeros}, wrlo_1{wr_lo,ones}, wrlo_r{wr_lo,random}, wrhi_z{wr_hi,zeros}, wrhi_1{wr_hi,ones}, wrhi_r{wr_hi,random}, setlo_z{set_lo,zeros}, setlo_1{set_lo,ones}, setlo_r{set_lo,random}, sethi_z{set_hi,zeros}, sethi_1{set_hi,ones}, sethi_r{set_hi,random}, clrlo_z{clr_lo,zeros}, clrlo_1{clr_lo,ones}, clrlo_r{clr_lo,random}, clrhi_z{clr_hi,zeros}, clrhi_1{clr_hi,ones}, clrhi_r{clr_hi,random}
  - cr_ctx_delta = cp_ctx x cp_delta: bins run_eq{run,eq_cycles}, wfi_eq{wfi_sleep,eq_cycles}, debug_eq{debug,eq_cycles}, step_eq{step,eq_cycles}, inh_zero{inhibited,zero}, run_written{run,eq_written}, inhmid_partial{inhibit_mid,partial}; ignore inhibited x eq_cycles, inhibit_mid x eq_cycles: counting while inhibited is a gen_chk_counters failure.
  - cr_wr_lobefore = cp_op x cp_lo_before: bins wrhi_near{wr_hi,near_wrap}, wrlo_near{wr_lo,near_wrap}, wrhi_mid{wr_hi,mid}, wrlo_zero{wr_lo,zero}
  - cr_carry_ctx = cp_carry x cp_ctx: bins carry_run{seen,run}, carry_wfi{seen,wfi_sleep}, carry_debug{seen,debug}
- Adopted (riscv-dv): none
- TP items: TP-DBG-066, TP-PMC-001, TP-PMC-002, TP-PMC-003, TP-PMC-004, TP-PMC-005, TP-PMC-006, TP-PMC-007, TP-PMC-023, TP-PMC-049, TP-PMC-050, TP-PMC-052, TP-PMC-053, TP-PMC-055, TP-PMC-056

### CG-PMC-002: gen_cg_pmc_minstret
- Features: F-PMC-007, F-PMC-008, F-PMC-009, F-PMC-010, F-PMC-011, F-PMC-012, F-PMC-013, F-PMC-014,
  F-PMC-022, F-PMC-046, F-PMC-047, F-PMC-048, F-PMC-050, F-PMC-051, F-PMC-052, F-DBG-063, F-PMC-001
  (parent of folded bins hosted here)
- Sample: RVFI retirement of a CSR access to CSR_MINSTRET / CSR_MINSTRETH (or instret/instreth
  aliases); the window is everything retired since the previous minstret read; condition:
  `rvfi_valid && csr_addr inside {MINSTRET, MINSTRETH, INSTRET, INSTRETH}`; counter-model rule:
  a record is counted iff rvfi_trap = 0, it is not an ebreak (the ebreak-into-debug record has
  rvfi_trap = 0 and is not counted, rtl/ibex_id_stage.sv:1218, S-2), it is not a write to
  minstret(h) and it is the final record of a Zcmp sequence; anti-vacuity: window bins are
  classified from the RVFI items observed in the window (trap kinds, ebreak outcome from
  CG-DBG-003, Zcmp, dummies via the dummy_instr_en CSR state), so a hit proves the excluded /
  included class actually occurred; the coherence bin comes from the dbg_model WB-occupancy
  tracker in the read cycle.
- Coverpoints:
  - cp_op = CSR op decoded from rvfi_insn: bins rd_lo{read minstret/instret}, rd_hi{read minstreth/instreth}, wr_lo{csrrw/csrrwi minstret}, wr_hi{csrrw/csrrwi minstreth}, set_lo{csrrs/csrrsi minstret, non-zero source}, set_hi{csrrs/csrrsi minstreth, non-zero source}, clr_lo{csrrc/csrrci minstret, non-zero source}, clr_hi{csrrc/csrrci minstreth, non-zero source}
  - cp_window = content of the window since the previous read: bins plain{only counted instructions}, has_ecall{>= 1 ecall record (rvfi_trap = 1)}, has_ebreak_exc{>= 1 ebreak record with rvfi_trap = 1 (exception path)}, has_ebreak_dbg{>= 1 ebreak record with rvfi_trap = 0 followed by the DmHaltAddr fetch (into debug; not counted)}, has_illegal{>= 1 illegal-instruction record}, has_fetch_fault{>= 1 instruction access fault record}, has_ls_fault{>= 1 load/store fault record}, has_zcmp{cm.* sequence}, has_dummy{dummy_instr_en=1 in the window}, has_wfi{>= 1 WFI record}, has_mret{>= 1 MRET record}, has_dret{>= 1 DRET record}, has_fence_i{>= 1 FENCE.I record}, has_self_write{csrw minstret/minstreth in the window}, has_irq{interrupt taken (rvfi_intr record)}, has_debug{debug window inside}, has_step{single step}
  - cp_coherence = WB state in the read cycle: bins wb_empty{no instruction in WB}, wb_retiring{countable instruction in WB}, wb_faulting{WB load/store faults, reader flushed}
  - cp_wrap = low-word wrap detected between consecutive reads: bins carry{low word wrapped, high incremented}, none{no wrap}
  - cp_inhibit_ir = mcountinhibit.IR: bins off{0}, on{1}
  - cp_dummy_en = cpuctrlsts.dummy_instr_en: bins off{0}, on{1}
  - cp_wdata = CSR write data class: bins zeros{0}, ones{32'hFFFF_FFFF}, random{any other value}
  - cp_delta = readback delta vs counted RVFI items in the window: bins eq_rvfi{==}, gt_rvfi{> (dummies, B7)}, zero{0}, one{1}
- Crosses:
  - cr_window_delta = cp_window x cp_delta: bins plain_eq{plain,eq_rvfi}, ecall_eq{has_ecall,eq_rvfi}, ebreakexc_eq{has_ebreak_exc,eq_rvfi}, ebreakdbg_eq{has_ebreak_dbg,eq_rvfi}, illegal_eq{has_illegal,eq_rvfi}, fetchfault_eq{has_fetch_fault,eq_rvfi}, lsfault_eq{has_ls_fault,eq_rvfi}, zcmp_eq{has_zcmp,eq_rvfi}, wfi_eq{has_wfi,eq_rvfi}, mret_eq{has_mret,eq_rvfi}, dret_eq{has_dret,eq_rvfi}, fencei_eq{has_fence_i,eq_rvfi}, selfwr_eq{has_self_write,eq_rvfi}, irq_eq{has_irq,eq_rvfi}, debug_eq{has_debug,eq_rvfi}, step_one{has_step,one}, step_zero{has_step,zero}, dummy_gt{has_dummy,gt_rvfi}, dummy_eq{has_dummy,eq_rvfi}; (B7 evidence: dummy_gt)
  - cr_coherence_op = cp_coherence x cp_op: bins retiring_rd{wb_retiring,rd_lo}, empty_rd{wb_empty,rd_lo}, faulting_rd{wb_faulting,rd_lo}, retiring_rdhi{wb_retiring,rd_hi}
  - cr_inhibit_coh = cp_inhibit_ir x cp_coherence: bins on_retiring{on,wb_retiring}, off_retiring{off,wb_retiring}
  - cr_op_wdata = cp_op x cp_wdata: bins wrlo_z{wr_lo,zeros}, wrlo_1{wr_lo,ones}, wrlo_r{wr_lo,random}, wrhi_z{wr_hi,zeros}, wrhi_1{wr_hi,ones}, wrhi_r{wr_hi,random}, setlo_1{set_lo,ones}, setlo_r{set_lo,random}, sethi_r{set_hi,random}, clrlo_1{clr_lo,ones}, clrlo_r{clr_lo,random}, clrhi_r{clr_hi,random}
  - cr_wrap_op = cp_wrap x cp_op: bins carry_rdhi{carry,rd_hi}, carry_rdlo{carry,rd_lo}
  - cr_dummy_delta = cp_dummy_en x cp_delta: bins dumon_gt{on,gt_rvfi}, dumoff_eq{off,eq_rvfi}, dumon_eq{on,eq_rvfi}
- Adopted (riscv-dv): none
- TP items: TP-DBG-066, TP-PMC-008, TP-PMC-009, TP-PMC-010, TP-PMC-011, TP-PMC-012, TP-PMC-013, TP-PMC-014, TP-PMC-015, TP-PMC-023, TP-PMC-024, TP-PMC-037, TP-PMC-048, TP-PMC-049, TP-PMC-050, TP-PMC-052, TP-PMC-053, TP-PMC-054, TP-PMC-055

### CG-PMC-003: gen_cg_pmc_hpm_event
- Features: F-PMC-016, F-PMC-021, F-PMC-023, F-PMC-032, F-PMC-033, F-PMC-034, F-PMC-035, F-PMC-036, F-PMC-037, F-PMC-038, F-PMC-039, F-PMC-040, F-PMC-041, F-PMC-042, F-PMC-043, F-PMC-044, F-PMC-046, F-PMC-047, F-PMC-049, F-DBG-063
- Sample: end of each TB event window: a code window bounded by two CSR reads of the same
  mhpmcounterN (N in [MHPMCOUNTER_BASE : HPM_LAST]); one sample per counter per window; condition:
  `window_end && counter_implemented`; exactness class per index (gen_tb_architecture.md 8.2 item
  2 and C4.6; the `eq` bins are sampled only in the exact classes): exact_rvfi for loads, stores,
  jumps, branches, taken, ret_c (instruction-derived from RVFI; a misaligned load/store counts 1,
  D6; fence.i is a jump for counter 7, rtl/ibex_decoder.sv:711-720; branches (counter 8) are exact
  only in windows where no branch enters ID while a WB load/store response is outstanding, else the
  window is bound class: C-10 / B17, the RTL adds one count per waiting cycle); exact_gap for
  mul_wait and div_wait (each mulh-class retirement adds 1 (RV32MSingleCycle), mul adds 0; each
  divide adds its RVFI gap minus 1, valid only when the gap is measured from the previous
  retirement and the qualifiers hold: no fetch stall on the divide (icache_enable = 0 pinned or the
  divide already in the prefetch buffer), the previous record is a single-cycle non-memory
  instruction retired without a WB stall (so the mul/div did not wait behind an outstanding WB
  access: C-10 / B17, the deferred start adds one mul_wait / div_wait count per waiting cycle), no
  dummy instruction in the gap (dummy_instr_en = 0), no mcycle/mcountinhibit write in between;
  otherwise the window is checked as a bound and `eq` is not sampled); bound for lsu_wait and if_wait (handshake-derived bounds `0 <= delta <= cycles
  elapsed`, monotonic; `eq` sampled only for TB-constructed single-kind windows whose timing the
  agent fixed); anti-vacuity: the event count is measured independently by gen_chk_counters (dbus
  transactions, RVFI pc_wdata for jumps/branches, rvfi_insn width for compressed, ibus/dbus
  handshake gaps and multdiv opcodes for the wait counters), so `cp_events` is tied to an
  observed event count, never to the counter's own value.
- Coverpoints:
  - cp_idx = counter index: bins lsu_wait{MHPMCOUNTER_BASE+0}, if_wait{MHPMCOUNTER_BASE+1}, loads{MHPMCOUNTER_BASE+2}, stores{MHPMCOUNTER_BASE+3}, jumps{MHPMCOUNTER_BASE+4}, branches{MHPMCOUNTER_BASE+5}, taken{MHPMCOUNTER_BASE+6}, ret_c{MHPMCOUNTER_BASE+7}, mul_wait{MHPMCOUNTER_BASE+8}, div_wait{MHPMCOUNTER_BASE+9}; each bin generate-guarded by k < MHPMCounterNum
  - cp_events = independently measured event count in the window: bins zero{0}, one{1}, few{[2:15]}, many{[16:$]}, wrap{window crosses 2^32 after a preload}; for div_wait the values 1..15 are reachable only through early-out div/rem by zero (DIV_STALL_ZERO each, data_ind_timing = 0) since one full divide adds DIV_STALL_FULL (cp_div_shape carries the shape)
  - cp_div_shape = shape of the div_wait window (only for idx == div_wait): bins none{no divide in the window}, early_only{only early-out div/rem by zero with data_ind_timing = 0: DIV_STALL_ZERO per divide}, full_one{exactly one full-latency divide: DIV_STALL_FULL}, full_many{>= 2 full-latency divides}, mixed{full-latency and early-out divides}
  - cp_delta_rel = counter delta vs measured events: bins eq{==}, gt{>}, lt{< : only legal for a window containing a same-cycle counter write that drops one event, F-PMC-045}, zero{delta 0 with events > 0}, partial{== events before a mid-window inhibit write plus events after its clearing}
  - cp_inhibit = mcountinhibit[idx] over the window: bins off{0 throughout}, on{1 throughout}, set_mid{written 1 inside the window}, cleared_mid{written 0 inside the window after being 1}
  - cp_dummy_en = cpuctrlsts.dummy_instr_en (CSR model) over the window: bins off{0}, on{1}
  - cp_variant = dominant event variant of the window (single-kind windows in Phase 1, `mixed` otherwise), decoded from RVFI / dbus / ibus: bins aligned{loads/stores with address aligned to the width}, misaligned{loads/stores crossing a word boundary: two dbus beats}, pmp_denied{loads/stores denied by the PMP model: no dbus request}, straddle_pmp{misaligned access whose second beat is PMP-denied}, bus_err{loads/stores answered with data_err_i}, jal{JAL}, jalr{JALR}, c_j{C.J}, c_jal{C.JAL}, c_jr{C.JR}, c_jalr{C.JALR}, popret{cm.popret/popretz}, fence_i{FENCE.I: decoded as a jump (jump_in_dec / jump_set, rtl/ibex_decoder.sv:711-720), counter 7}, b_taken{32-bit branch taken}, b_not{32-bit branch not taken}, c_beqz_taken{c.beqz/c.bnez taken}, c_bnez_not{c.beqz/c.bnez not taken}, dit_on_taken{taken branch with data_ind_timing = 1}, dit_on_not{not-taken branch with data_ind_timing = 1}, c_alu{16-bit non-branch retirements}, zcmp{cm.* sequences}, mul{MUL}, mulh{MULH}, mulhsu{MULHSU}, mulhu{MULHU}, dummy_mul{dummy multiply inserted (probe-gated P1, not in manifest)}, div{DIV}, divu{DIVU}, rem{REM}, remu{REMU}, div_zero{divide by zero}, div_ovf{signed overflow divide}, dummy_div{dummy divide inserted (probe-gated P1, not in manifest)}, br_wb_wait{conditional branch entering ID while the preceding load/store still awaits its WB response (B17 window; measured count = branches)}, mul_wb_wait{mul / mulh-class entering ID behind an outstanding WB access (B17 window; measured count = mul 0, mulh-class 1)}, div_wb_wait{div / rem entering ID behind an outstanding WB access (B17 window; measured count = DIV_STALL_FULL or DIV_STALL_ZERO per divide)}, rvalid_delay{LSU wait from delayed rvalid}, gnt_delay{window built from one load/store with a delayed gnt and nothing waiting behind it: measured count 0, the access's own grant wait is not in perf_dside_wait (rtl/ibex_id_stage.sv:1135-1136)}, ld_use_hazard{LSU wait from a load-use dependency}, imem_latency{IF wait from imem latency}, redirect{IF wait after a taken branch/jump}, after_debug{IF wait after a debug entry/dret}, mixed{more than one variant}
  - cp_ctx = window context (RVFI flags of the window's records): bins run{no debug flag in the window}, debug{window inside debug mode}, step{window is a single step}
  - cp_dit = cpuctrlsts.data_ind_timing: bins off{0}, on{1}
- Crosses:
  - cr_idx_events = cp_idx x cp_events: bins lsu_0{lsu_wait,zero}, lsu_1{lsu_wait,one}, lsu_few{lsu_wait,few}, lsu_many{lsu_wait,many}, if_0{if_wait,zero}, if_1{if_wait,one}, if_few{if_wait,few}, if_many{if_wait,many}, ld_0{loads,zero}, ld_1{loads,one}, ld_few{loads,few}, ld_many{loads,many}, ld_wrap{loads,wrap}, st_0{stores,zero}, st_1{stores,one}, st_few{stores,few}, st_many{stores,many}, st_wrap{stores,wrap}, jmp_0{jumps,zero}, jmp_1{jumps,one}, jmp_few{jumps,few}, jmp_many{jumps,many}, jmp_wrap{jumps,wrap}, br_0{branches,zero}, br_1{branches,one}, br_few{branches,few}, br_many{branches,many}, br_wrap{branches,wrap}, tk_0{taken,zero}, tk_1{taken,one}, tk_few{taken,few}, tk_many{taken,many}, rc_0{ret_c,zero}, rc_1{ret_c,one}, rc_few{ret_c,few}, rc_many{ret_c,many}, rc_wrap{ret_c,wrap}, mul_0{mul_wait,zero}, mul_1{mul_wait,one}, mul_few{mul_wait,few}, mul_many{mul_wait,many}, div_0{div_wait,zero}, div_1{div_wait,one: one early-out div/rem by zero with data_ind_timing = 0}, div_few{div_wait,few: 2..15 early-out divides}, div_many{div_wait,many: >= 1 full-latency divide or >= 16 early-outs}; ignore lsu_wait/if_wait/taken/mul_wait/div_wait x wrap: cycle-class counters are wrapped via preload in cr_idx_inhibit items only when cheap; not required.
  - cr_div_shape = cp_idx x cp_div_shape: bins div_none{div_wait,none}, div_early{div_wait,early_only}, div_full1{div_wait,full_one}, div_fullmany{div_wait,full_many}, div_mixed{div_wait,mixed}; ignore other idx x *: cp_div_shape is defined for div_wait only.
  - cr_idx_inhibit = cp_idx x cp_inhibit x cp_delta_rel: bins lsu_inh{lsu_wait,on,zero}, if_inh{if_wait,on,zero}, ld_inh{loads,on,zero}, st_inh{stores,on,zero}, jmp_inh{jumps,on,zero}, br_inh{branches,on,zero}, tk_inh{taken,on,zero}, rc_inh{ret_c,on,zero}, mul_inh{mul_wait,on,zero}, div_inh{div_wait,on,zero}, lsu_eq{lsu_wait,off,eq}, if_eq{if_wait,off,eq}, ld_eq{loads,off,eq}, st_eq{stores,off,eq}, jmp_eq{jumps,off,eq}, br_eq{branches,off,eq}, tk_eq{taken,off,eq}, rc_eq{ret_c,off,eq}, mul_eq{mul_wait,off,eq}, div_eq{div_wait,off,eq}, ld_setmid{loads,set_mid,partial}, st_setmid{stores,set_mid,partial}, br_clrmid{branches,cleared_mid,partial}, rc_setmid{ret_c,set_mid,partial}; ignore set_mid/cleared_mid x eq, on x eq: counting while inhibited is a gen_chk_counters failure.
  - cr_idx_dummy = cp_idx x cp_dummy_en x cp_delta_rel: bins div_dum_gt{div_wait,on,gt}, mul_dum_eq{mul_wait,off,eq}, mul_dum_zero{mul_wait,on,eq}; ignore_bins mul_dum_gt{mul_wait,on,gt}: the dummy multiply is `mul` (funct3 000, rtl/ibex_dummy_instr.sv:124-131), which the RV32MSingleCycle multiplier completes in its first cycle (rtl/ibex_multdiv_fast.sv:203-217), so an ALU-only window with dummies on adds no mul_wait cycles; reachable only through the B17 over-count of a dummy mul behind an outstanding WB access, not required; (B7 evidence on the wait counters without a probe: an ALU-only window with dummies on has zero program div events, so a div_wait delta is `gt` while mul_wait stays 0 (`mul_dum_zero`))
  - cr_variant_rel = cp_variant x cp_delta_rel: bins aligned_eq{aligned,eq}, misaligned_eq{misaligned,eq}, pmpden_eq{pmp_denied,eq}, straddle_eq{straddle_pmp,eq}, buserr_eq{bus_err,eq}, jal_eq{jal,eq}, jalr_eq{jalr,eq}, cj_eq{c_j,eq}, cjal_eq{c_jal,eq}, cjr_eq{c_jr,eq}, cjalr_eq{c_jalr,eq}, popret_eq{popret,eq}, fencei_eq{fence_i,eq}, btaken_eq{b_taken,eq}, bnot_eq{b_not,eq}, cbeqz_eq{c_beqz_taken,eq}, cbnez_eq{c_bnez_not,eq}, dittaken_eq{dit_on_taken,eq}, ditnot_gt{dit_on_not,gt}, ditnot_eq{dit_on_not,eq}, calu_eq{c_alu,eq}, zcmp_eq{zcmp,eq}, mul_eq{mul,eq}, mulh_eq{mulh,eq}, mulhsu_eq{mulhsu,eq}, mulhu_eq{mulhu,eq}, dummymul_gt{dummy_mul,gt} (probe-gated P1, not in manifest), div_eq{div,eq}, divu_eq{divu,eq}, rem_eq{rem,eq}, remu_eq{remu,eq}, divzero_eq{div_zero,eq}, divovf_eq{div_ovf,eq}, dummydiv_gt{dummy_div,gt} (probe-gated P1, not in manifest), brwait_gt{br_wb_wait,gt}, mulwait_gt{mul_wb_wait,gt}, divwait_gt{div_wb_wait,gt}, rvalid_eq{rvalid_delay,eq}, gnt_eq{gnt_delay,eq}, hazard_eq{ld_use_hazard,eq}, imem_eq{imem_latency,eq}, redirect_eq{redirect,eq}, afterdbg_eq{after_debug,eq}, mixed_eq{mixed,eq}; (misaligned_eq is D6 evidence with the RTL count of one; ditnot_gt is B11 evidence on cp_idx taken; dummymul_gt/dummydiv_gt are B7 evidence once P1 is registered; cr_idx_dummy carries the probe-free B7 evidence; brwait_gt / mulwait_gt / divwait_gt are B17 evidence: the measured count is the doc count and the RTL adds one per cycle the instruction waited in ID behind the outstanding WB access (TP-PMC-058/059/060, expected-fail))
  - cr_idx_ctx = cp_idx x cp_ctx: bins lsu_dbg{lsu_wait,debug}, if_dbg{if_wait,debug}, ld_dbg{loads,debug}, st_dbg{stores,debug}, jmp_dbg{jumps,debug}, br_dbg{branches,debug}, tk_dbg{taken,debug}, rc_dbg{ret_c,debug}, mul_dbg{mul_wait,debug}, div_dbg{div_wait,debug}, ld_step{loads,step}, br_step{branches,step}
  - cr_idx_dit = cp_idx x cp_dit: bins tk_dit1{taken,on}, tk_dit0{taken,off}, br_dit1{branches,on}, br_dit0{branches,off}
- Adopted (riscv-dv): none
- TP items: TP-DBG-066, TP-PMC-013, TP-PMC-014, TP-PMC-018, TP-PMC-023, TP-PMC-025, TP-PMC-034, TP-PMC-035, TP-PMC-036, TP-PMC-037, TP-PMC-038, TP-PMC-039, TP-PMC-040, TP-PMC-041, TP-PMC-042, TP-PMC-043, TP-PMC-044, TP-PMC-045, TP-PMC-046, TP-PMC-047, TP-PMC-048, TP-PMC-049, TP-PMC-050, TP-PMC-051, TP-PMC-055, TP-PMC-056, TP-PMC-058, TP-PMC-059, TP-PMC-060

### CG-PMC-004: gen_cg_pmc_hpm_csr
- Features: F-PMC-015, F-PMC-016, F-PMC-017, F-PMC-018, F-PMC-019, F-PMC-024, F-PMC-045, F-PMC-051,
  F-PMC-001 (parent of folded bins hosted here)
- Sample: RVFI retirement of any CSR access in [CSR_MHPMCOUNTER3 : CSR_MHPMCOUNTER31],
  [CSR_MHPMCOUNTER3H : CSR_MHPMCOUNTER31H], [CSR_MHPMEVENT3 : CSR_MHPMEVENT31]; closed by the
  following read of the same CSR; condition: `rvfi_valid && csr_addr inside hpm_csr_set`;
  anti-vacuity: result from rvfi_trap, readback class from the observed read value; index class
  decoded from the address against MHPMCounterNum.
- Coverpoints:
  - cp_idx = counter index class: bins first_impl{MHPMCOUNTER_BASE}, mid_impl{[MHPMCOUNTER_BASE+1 : MHPMCOUNTER_BASE+MHPMCounterNum-2]}, last_impl{MHPMCOUNTER_BASE+MHPMCounterNum-1}, first_unimpl{MHPMCOUNTER_BASE+MHPMCounterNum}, mid_unimpl{[MHPMCOUNTER_BASE+MHPMCounterNum+1 : 30]}, last_unimpl{31}
  - cp_reg = CSR address decoded from rvfi_insn: bins cnt_lo{mhpmcounterN}, cnt_hi{mhpmcounterNh}, event{mhpmeventN}
  - cp_op = CSR op decoded from rvfi_insn: bins read{csrrs/csrrc with x0 / uimm 0}, write{csrrw/csrrwi}, set{csrrs/csrrsi non-zero}, clear{csrrc/csrrci non-zero}
  - cp_mode = {rvfi_ext_debug_mode, rvfi_mode}: bins m{0, PRIV_LVL_M}, u{0, PRIV_LVL_U}, dbg{1, any}
  - cp_result = {rvfi_trap, readback relation}: bins ok{rvfi_trap = 0}, illegal{rvfi_trap = 1, mcause 2}
  - cp_wdata = CSR write data class: bins zeros{0}, ones{32'hFFFF_FFFF}, random{any other value}
  - cp_rb = readback class: bins eq_written{implemented low word == written}, zero{reads 0}, const_onehot{mhpmeventN == 32'd1 << (N - MHPMCOUNTER_BASE): mhpmevent3 = 0x1 .. mhpmevent12 = 0x200 (rtl/ibex_cs_registers.sv:185, :1602-1619; D20, the doc says 1 << N)}
- Crosses:
  - cr_idx_reg_op = cp_idx x cp_reg x cp_op: bins fi_lo_rd{first_impl,cnt_lo,read}, fi_lo_wr{first_impl,cnt_lo,write}, fi_hi_rd{first_impl,cnt_hi,read}, fi_hi_wr{first_impl,cnt_hi,write}, fi_ev_rd{first_impl,event,read}, fi_ev_wr{first_impl,event,write}, mi_lo_rd{mid_impl,cnt_lo,read}, mi_lo_wr{mid_impl,cnt_lo,write}, mi_hi_rd{mid_impl,cnt_hi,read}, mi_hi_wr{mid_impl,cnt_hi,write}, mi_ev_rd{mid_impl,event,read}, mi_ev_wr{mid_impl,event,write}, li_lo_rd{last_impl,cnt_lo,read}, li_lo_wr{last_impl,cnt_lo,write}, li_hi_rd{last_impl,cnt_hi,read}, li_hi_wr{last_impl,cnt_hi,write}, li_ev_rd{last_impl,event,read}, li_ev_wr{last_impl,event,write}, fu_lo_rd{first_unimpl,cnt_lo,read}, fu_lo_wr{first_unimpl,cnt_lo,write}, fu_hi_rd{first_unimpl,cnt_hi,read}, fu_hi_wr{first_unimpl,cnt_hi,write}, fu_ev_rd{first_unimpl,event,read}, fu_ev_wr{first_unimpl,event,write}, mu_lo_rd{mid_unimpl,cnt_lo,read}, mu_lo_wr{mid_unimpl,cnt_lo,write}, mu_hi_rd{mid_unimpl,cnt_hi,read}, mu_hi_wr{mid_unimpl,cnt_hi,write}, mu_ev_rd{mid_unimpl,event,read}, mu_ev_wr{mid_unimpl,event,write}, lu_lo_rd{last_unimpl,cnt_lo,read}, lu_lo_wr{last_unimpl,cnt_lo,write}, lu_hi_rd{last_unimpl,cnt_hi,read}, lu_hi_wr{last_unimpl,cnt_hi,write}, lu_ev_rd{last_unimpl,event,read}, lu_ev_wr{last_unimpl,event,write}, fi_lo_set{first_impl,cnt_lo,set}, fi_lo_clr{first_impl,cnt_lo,clear}, fi_hi_set{first_impl,cnt_hi,set}, fi_ev_set{first_impl,event,set}, li_lo_set{last_impl,cnt_lo,set}, li_lo_clr{last_impl,cnt_lo,clear}, li_hi_clr{last_impl,cnt_hi,clear}, li_ev_clr{last_impl,event,clear}, fu_lo_set{first_unimpl,cnt_lo,set}, lu_ev_clr{last_unimpl,event,clear}
  - cr_mode_result = cp_mode x cp_result: bins m_ok{m,ok}, dbg_ok{dbg,ok}, u_ill{u,illegal}; ignore u x ok, m x illegal, dbg x illegal: privilege-check failure is a gen_isa_compare failure.
  - cr_idx_reg_rb = cp_idx x cp_reg x cp_rb: bins fi_lo_eq{first_impl,cnt_lo,eq_written}, mi_lo_eq{mid_impl,cnt_lo,eq_written}, li_lo_eq{last_impl,cnt_lo,eq_written}, fi_hi_0{first_impl,cnt_hi,zero}, mi_hi_0{mid_impl,cnt_hi,zero}, li_hi_0{last_impl,cnt_hi,zero}, fu_lo_0{first_unimpl,cnt_lo,zero}, mu_lo_0{mid_unimpl,cnt_lo,zero}, lu_lo_0{last_unimpl,cnt_lo,zero}, fu_hi_0{first_unimpl,cnt_hi,zero}, lu_hi_0{last_unimpl,cnt_hi,zero}, fi_ev_1h{first_impl,event,const_onehot}, mi_ev_1h{mid_impl,event,const_onehot}, li_ev_1h{last_impl,event,const_onehot}, fu_ev_0{first_unimpl,event,zero}, mu_ev_0{mid_unimpl,event,zero}, lu_ev_0{last_unimpl,event,zero}
  - cr_wdata_reg = cp_wdata x cp_reg: bins z_lo{zeros,cnt_lo}, o_lo{ones,cnt_lo}, r_lo{random,cnt_lo}, z_hi{zeros,cnt_hi}, o_hi{ones,cnt_hi}, r_hi{random,cnt_hi}, z_ev{zeros,event}, o_ev{ones,event}, r_ev{random,event}
- Adopted (riscv-dv): none
- TP items: TP-PMC-017, TP-PMC-019, TP-PMC-020, TP-PMC-021, TP-PMC-026, TP-PMC-047, TP-PMC-053, TP-PMC-055

### CG-PMC-005: gen_cg_pmc_ctrl_csr
- Features: F-PMC-020, F-PMC-021, F-PMC-022, F-PMC-023, F-PMC-024, F-PMC-025, F-PMC-026, F-PMC-031
- Sample: RVFI retirement of a CSR access to CSR_MCOUNTINHIBIT or CSR_MCOUNTEREN; a read samples
  once with cp_bit = none; a write op samples once per (op, field) pair over the fields of cp_bit,
  where the model computes the field's post-op value from the op semantics applied to the model's
  current register (csrrw: wdata; csrrs: old | wdata; csrrc: old & ~wdata) and compares it with
  the readback that closes the write; the mcounteren_writable_i pin value is sampled from the DUT
  boundary in the write cycle (W-DEC of the write, last ID cycle); condition: `rvfi_valid &&
  csr_addr inside {CSR_MCOUNTINHIBIT, CSR_MCOUNTEREN}`; anti-vacuity: result and readback come from
  RVFI; the readback class is derived against the post-op prediction (never the raw write data,
  so csrrc and zero patterns classify correctly); `dropped` is only recorded when the readback
  differs from the WARL prediction of an applied write, so a hit proves the pin gate.
- Coverpoints:
  - cp_reg = CSR address decoded from rvfi_insn: bins inhibit{CSR_MCOUNTINHIBIT}, en{CSR_MCOUNTEREN}
  - cp_bit = field of the sampled (op, field) pair: bins cy{0}, tm{1}, ir{2}, hpm_first{MHPMCOUNTER_BASE}, hpm_mid{[MHPMCOUNTER_BASE+1 : HPM_LAST-1]}, hpm_last{HPM_LAST}, upper{[HPM_LAST+1 : 31]}, none{read}
  - cp_pattern = write-data (rs1 / uimm) pattern class: bins zeros{0}, ones{32'hFFFF_FFFF}, walk1{exactly one bit set}, random{>= 2 bits set and not all}
  - cp_op = CSR op decoded from rvfi_insn: bins read{csrrs/csrrc with x0 / uimm 0}, write{csrrw/csrrwi}, set{csrrs/csrrsi non-zero}, clear{csrrc/csrrci non-zero}
  - cp_mode = {rvfi_ext_debug_mode, rvfi_mode} of the item: bins m{0, PRIV_LVL_M}, u{0, PRIV_LVL_U}, dbg{1, any}
  - cp_result = {rvfi_trap, readback relation}: bins ok{rvfi_trap = 0}, illegal{rvfi_trap = 1, mcause 2}
  - cp_rb = per-field readback against the post-op prediction: bins as_written{writable field: readback == post-op value}, forced0{hardwired-0 field (tm, upper) with post-op value 1: readback 0}, nop0{hardwired-0 field with post-op value 0: readback 0 (witness; not in manifest)}
  - cp_pin = mcounteren_writable_i in the write cycle: bins on{IbexMuBiOn}, off{IbexMuBiOff}, invalid{any other 4-bit value}
  - cp_pin_tr = mcounteren_writable_i transition between the previous mcounteren write and this one (pin monitor): bins stable{same class}, on_to_off{On -> Off}, off_to_on{Off -> On}, on_to_inv{On -> invalid}, inv_to_on{invalid -> On}
  - cp_effect = write effect (mcounteren only; mcountinhibit writes are always applied): bins applied{readback == WARL prediction of the write}, dropped{readback == pre-write value although the WARL prediction differs}
- Crosses:
  - cr_reg_bit_rb = cp_reg x cp_bit x cp_rb: bins inh_cy_w{inhibit,cy,as_written}, inh_ir_w{inhibit,ir,as_written}, inh_hf_w{inhibit,hpm_first,as_written}, inh_hm_w{inhibit,hpm_mid,as_written}, inh_hl_w{inhibit,hpm_last,as_written}, inh_tm_0{inhibit,tm,forced0}, inh_up_0{inhibit,upper,forced0}, en_cy_w{en,cy,as_written}, en_ir_w{en,ir,as_written}, en_hf_w{en,hpm_first,as_written}, en_hm_w{en,hpm_mid,as_written}, en_hl_w{en,hpm_last,as_written}, en_tm_0{en,tm,forced0}, en_up_0{en,upper,forced0}; ignore tm/upper x as_written, cy/ir/hpm_* x forced0: checker failures.
  - cr_en_pin_effect = cp_reg x cp_pin x cp_effect: bins en_on_app{en,on,applied}, en_off_drop{en,off,dropped}, en_inv_drop{en,invalid,dropped}, inh_off_app{inhibit,off,applied}, inh_inv_app{inhibit,invalid,applied}, inh_on_app{inhibit,on,applied}; ignore en x off/invalid x applied: gate failure is a gen_chk_csr_readback failure.
  - cr_pin_tr_effect = cp_reg x cp_pin_tr x cp_effect: bins en_ontooff_drop{en,on_to_off,dropped}, en_offtoon_app{en,off_to_on,applied}, en_ontoinv_drop{en,on_to_inv,dropped}, en_invtoon_app{en,inv_to_on,applied}; ignore inhibit x *: the pin does not gate mcountinhibit (covered by cr_en_pin_effect.inh_*); ignore en x on_to_off/on_to_inv x applied, en x off_to_on/inv_to_on x dropped: the pin value in the write cycle decides (gen_chk_csr_readback failure).
  - cr_reg_pattern_op = cp_reg x cp_pattern x cp_op: bins inh_z_wr{inhibit,zeros,write}, inh_1_wr{inhibit,ones,write}, inh_w_wr{inhibit,walk1,write}, inh_r_wr{inhibit,random,write}, inh_1_set{inhibit,ones,set}, inh_w_set{inhibit,walk1,set}, inh_r_set{inhibit,random,set}, inh_1_clr{inhibit,ones,clear}, inh_w_clr{inhibit,walk1,clear}, inh_r_clr{inhibit,random,clear}, en_z_wr{en,zeros,write}, en_1_wr{en,ones,write}, en_w_wr{en,walk1,write}, en_r_wr{en,random,write}, en_1_set{en,ones,set}, en_w_set{en,walk1,set}, en_r_set{en,random,set}, en_1_clr{en,ones,clear}, en_w_clr{en,walk1,clear}, en_r_clr{en,random,clear}
  - cr_reg_mode_result = cp_reg x cp_mode x cp_result: bins inh_m_ok{inhibit,m,ok}, inh_dbg_ok{inhibit,dbg,ok}, inh_u_ill{inhibit,u,illegal}, en_m_ok{en,m,ok}, en_dbg_ok{en,dbg,ok}, en_u_ill{en,u,illegal}
- Adopted (riscv-dv): none
- TP items: TP-PMC-022, TP-PMC-026, TP-PMC-027, TP-PMC-028, TP-PMC-032, TP-PMC-033, TP-PMC-055, TP-PMC-057

### CG-PMC-006: gen_cg_pmc_alias
- Features: F-PMC-024, F-PMC-027, F-PMC-028, F-PMC-029, F-PMC-030, F-PMC-031, F-PMC-021 (parent of
  folded bins hosted here)
- Sample: RVFI item whose rvfi_insn is a CSR access in [12'hC00 : 12'hC1F] or [12'hC80 : 12'hC9F];
  condition: `rvfi_valid && csr_addr inside alias_set`; anti-vacuity: result from rvfi_trap;
  mcounteren bit from the CSR model at the access; privilege from rvfi_mode; a hit in `u x set x ok`
  proves the gate opened for that bit, `u x clr x illegal` proves it closed.
- Coverpoints:
  - cp_alias = alias CSR address decoded from rvfi_insn: bins cycle{12'hC00}, time{12'hC01}, instret{12'hC02}, hpm_first{12'hC00+MHPMCOUNTER_BASE}, hpm_mid{[12'hC00+MHPMCOUNTER_BASE+1 : 12'hC00+MHPMCOUNTER_BASE+MHPMCounterNum-2]}, hpm_last{12'hC00+MHPMCOUNTER_BASE+MHPMCounterNum-1}, hpm_unimpl{[12'hC00+MHPMCOUNTER_BASE+MHPMCounterNum : 12'hC1F]}, cycleh{12'hC80}, timeh{12'hC81}, instreth{12'hC82}, hpmh_first{12'hC80+MHPMCOUNTER_BASE}, hpmh_mid{[12'hC80+MHPMCOUNTER_BASE+1 : 12'hC80+MHPMCOUNTER_BASE+MHPMCounterNum-2]}, hpmh_last{12'hC80+MHPMCOUNTER_BASE+MHPMCounterNum-1}, hpmh_unimpl{[12'hC80+MHPMCOUNTER_BASE+MHPMCounterNum : 12'hC9F]}
  - cp_en_bit = mcounteren[addr[4:0]]: bins clr{0}, set{1}
  - cp_mode = {rvfi_ext_debug_mode, rvfi_mode} of the item: bins m{0, PRIV_LVL_M}, u{0, PRIV_LVL_U}, dbg{1, any}
  - cp_op = CSR op decoded from rvfi_insn: bins read{no write}, write{csrrw/csrrwi}, set_nz{csrrs/csrrsi non-zero}, clr_nz{csrrc/csrrci non-zero}
  - cp_result = {rvfi_trap, readback relation}: bins ok{rvfi_trap = 0}, illegal{rvfi_trap = 1, mcause 2}
  - cp_inhibited = mcountinhibit[addr[4:0]]: bins no{0}, yes{1}
- Crosses:
  - cr_alias_gate = cp_alias x cp_en_bit x cp_mode x cp_result: bins cyc_u_set_ok{cycle,set,u,ok}, cyc_u_clr_ill{cycle,clr,u,illegal}, cyc_m_clr_ok{cycle,clr,m,ok}, ir_u_set_ok{instret,set,u,ok}, ir_u_clr_ill{instret,clr,u,illegal}, ir_m_clr_ok{instret,clr,m,ok}, hf_u_set_ok{hpm_first,set,u,ok}, hf_u_clr_ill{hpm_first,clr,u,illegal}, hf_m_clr_ok{hpm_first,clr,m,ok}, hm_u_set_ok{hpm_mid,set,u,ok}, hm_u_clr_ill{hpm_mid,clr,u,illegal}, hm_m_clr_ok{hpm_mid,clr,m,ok}, hl_u_set_ok{hpm_last,set,u,ok}, hl_u_clr_ill{hpm_last,clr,u,illegal}, hl_m_clr_ok{hpm_last,clr,m,ok}, cych_u_set_ok{cycleh,set,u,ok}, cych_u_clr_ill{cycleh,clr,u,illegal}, cych_m_clr_ok{cycleh,clr,m,ok}, irh_u_set_ok{instreth,set,u,ok}, irh_u_clr_ill{instreth,clr,u,illegal}, irh_m_clr_ok{instreth,clr,m,ok}, hhf_u_set_ok{hpmh_first,set,u,ok}, hhf_u_clr_ill{hpmh_first,clr,u,illegal}, hhf_m_clr_ok{hpmh_first,clr,m,ok}, hhm_u_set_ok{hpmh_mid,set,u,ok}, hhm_u_clr_ill{hpmh_mid,clr,u,illegal}, hhm_m_clr_ok{hpmh_mid,clr,m,ok}, hhl_u_set_ok{hpmh_last,set,u,ok}, hhl_u_clr_ill{hpmh_last,clr,u,illegal}, hhl_m_clr_ok{hpmh_last,clr,m,ok}, hu_u_ill{hpm_unimpl,clr,u,illegal}, hu_m_ok{hpm_unimpl,clr,m,ok}, hhu_u_ill{hpmh_unimpl,clr,u,illegal}, hhu_m_ok{hpmh_unimpl,clr,m,ok}, time_m_ill{time,clr,m,illegal}, time_u_ill{time,clr,u,illegal}, timeh_m_ill{timeh,clr,m,illegal}, timeh_u_ill{timeh,clr,u,illegal}, cyc_dbg_ok{cycle,clr,dbg,ok}, ir_dbg_ok{instret,clr,dbg,ok}, hf_dbg_ok{hpm_first,clr,dbg,ok}; ignore hpm_unimpl/hpmh_unimpl/time/timeh x set: the mcounteren bits for these indices are hardwired 0; ignore u x clr x ok, u x set x illegal (readable aliases): gate failures are gen_isa_compare failures.
  - cr_op_result = cp_op x cp_result: bins rd_ok{read,ok}, rd_ill{read,illegal}, wr_ill{write,illegal}, set_ill{set_nz,illegal}, clr_ill{clr_nz,illegal}; ignore write/set_nz/clr_nz x ok: the range is read-only in every mode.
  - cr_write_alias = cp_alias x cp_op x cp_mode: bins cyc_wr_m{cycle,write,m}, cyc_wr_u{cycle,write,u}, ir_set_m{instret,set_nz,m}, hf_clr_m{hpm_first,clr_nz,m}, cych_wr_m{cycleh,write,m}, hhu_wr_m{hpmh_unimpl,write,m}, hu_wr_u{hpm_unimpl,write,u}
  - cr_inhibit_gate = cp_inhibited x cp_en_bit x cp_mode x cp_result: bins inh_set_u_ok{yes,set,u,ok}, noinh_set_u_ok{no,set,u,ok}
- Adopted (riscv-dv): none
- TP items: TP-PMC-029, TP-PMC-030, TP-PMC-031, TP-PMC-032, TP-PMC-033, TP-PMC-055

### CG-PMC-007: gen_cg_pmc_write_timing
- Features: F-PMC-004, F-PMC-005, F-PMC-014, F-PMC-023, F-PMC-045, F-PMC-051, F-PMC-021 (parent of
  folded bins hosted here)
- Sample: each retired CSR write op to a counter CSR (mcycle(h), minstret(h), mhpmcounterN(h) for
  implemented N), with the same-cycle event state taken from gen_chk_counters' boundary model in the
  write cycle; condition: `rvfi_valid && csr_addr inside counter_csr_set && is_write`; anti-vacuity:
  the coincidence bins are reached only when the instruction stream places the target's own event
  in the write cycle (W-WB: `lw ; csrw minstret(h)` or `c.lw ; csrw mhpmcounter10(h)` with the
  csrw held behind the load's response, or back-to-back issue); the model records the write-wins
  evidence (expected value == written, not written+1), so a hit proves the coincidence occurred.
  Structurally (X-18) only mcycle(h), minstret(h) and mhpmcounter10(h) can coincide with their own
  event: the other events are asserted only while their own instruction is the valid instruction in
  ID (or while the csrw cannot commit), and the csrw is a different instruction.
- Coverpoints:
  - cp_target = counter CSR address decoded from rvfi_insn: bins mcycle{CSR_MCYCLE}, mcycleh{CSR_MCYCLEH}, minstret{CSR_MINSTRET}, minstreth{CSR_MINSTRETH}, hpm_lo{[CSR_MHPMCOUNTER3 : CSR_MHPMCOUNTER3+MHPMCounterNum-1]}, hpm_hi{[CSR_MHPMCOUNTER3H : CSR_MHPMCOUNTER3H+MHPMCounterNum-1]}
  - cp_coincident = event of the written counter firing in the write cycle (boundary model of gen_chk_counters; the mcycle tick is always present and is not a bin: the write-wins evidence for mcycle is CG-PMC-001.cp_delta.eq_written): bins none{no event of the target in the write cycle}, retire_in_wb{countable instruction retiring in WB (minstret(h) target)}, retire_c_in_wb{compressed instruction retiring in WB (mhpmcounter10(h) target)}; ignore_bins lsu_wait_cycle{ID stalled on a dbus response in the write cycle}, if_wait_cycle{ID starved by IF in the write cycle}, load_req{dbus load request in the write cycle}, store_req{dbus store request in the write cycle}, jump{jump decided in the write cycle}, branch{branch decided in the write cycle}: unreachable as the event of the WRITTEN counter (X-18: perf_load/perf_store fire in the LSU IDLE arm of the load/store itself, perf_branch/tbranch/jump from the instruction in ID, dside_wait needs outstanding_memory_access which blocks csr_op_en, iside_wait needs ~instr_valid_id; the csrw is a different instruction in ID; rtl/ibex_id_stage.sv:747-749, :889-934, :1135-1136, rtl/ibex_load_store_unit.sv:466-475, rtl/ibex_controller.sv:681-687, rtl/ibex_core.sv:635)
  - cp_inhibited = mcountinhibit bit of the target at the write: bins no{0}, yes{1}
  - cp_then = later behaviour: bins uninhibit_after{inhibit bit cleared later, counting resumed from the written value}, stay{inhibit bit unchanged until the next read}
  - cp_low_all_ones = low word == 32'hFFFF_FFFF in the write cycle (high-half writes): bins yes{low word all ones}, no{any other low word}
- Crosses:
  - cr_target_coinc = cp_target x cp_coincident: bins minstret_ret{minstret,retire_in_wb}, minstreth_ret{minstreth,retire_in_wb}, hpm_retc{hpm_lo,retire_c_in_wb}, hpmh_retc{hpm_hi,retire_c_in_wb}, hpm_none{hpm_lo,none}; ignore_bins hpm_lsu{hpm_lo,lsu_wait_cycle}, hpm_if{hpm_lo,if_wait_cycle}, hpm_load{hpm_lo,load_req}, hpm_store{hpm_lo,store_req}, hpm_jump{hpm_lo,jump}, hpm_branch{hpm_lo,branch}, hpmh_load{hpm_hi,load_req}: components unreachable (X-18); hpm_retc / hpmh_retc are hit only with the target mhpmcounter10 / mhpmcounter10h (a compressed retirement in WB is the event of no other counter): an h-half write of a 32-bit counter also asserts `we` and suppresses that cycle's increment (rtl/ibex_counter.sv:35-46, X-17), observable through hpmh_retc
  - cr_target_inh_then = cp_target x cp_inhibited x cp_then: bins mcycle_inh_resume{mcycle,yes,uninhibit_after}, minstret_inh_resume{minstret,yes,uninhibit_after}, hpm_inh_resume{hpm_lo,yes,uninhibit_after}, hpm_noinh{hpm_lo,no,stay}
  - cr_hi_lowones = cp_target x cp_low_all_ones: bins mcycleh_ones{mcycleh,yes}, minstreth_ones{minstreth,yes}, mcycleh_no{mcycleh,no}
- Adopted (riscv-dv): none
- TP items: TP-PMC-006, TP-PMC-016, TP-PMC-025, TP-PMC-047, TP-PMC-053, TP-PMC-055

### CG-PMC-008: gen_cg_pmc_rvfi_ext
- Features: F-PMC-001, F-PMC-015, F-PMC-049
- Sample: three events, each guarded per coverpoint with `iff` (S-3c): (a) the first RVFI record
  after a retired mcycle(h) write (`iff after_write_evt`), (b) the end of an inhibit window
  (mcountinhibit.CY = 1 written, >= 8 retirements, then cleared) and the end of a debug window with
  >= 8 debug retirements (`iff window_evt`), (c) every rvfi_valid for the per-record hpm
  observation (`iff rvfi_evt`); condition: `after_write_evt || window_evt || rvfi_valid`;
  discriminating condition (S-3a): the mcycle relation bins are sampled only on the write / window
  events, never per retirement; cp_hpm_moved discriminates per record (none / one / several);
  anti-vacuity: `jump_after_write` requires a preceding retired mcycle write, `eq_inhibited` a
  retired mcountinhibit write with CY=1 and a window of >= 8 records, `inc_debug` a debug window
  of >= 8 records, so a hit proves the exported value tracked the CSR under that stimulus. The
  all-zero rvfi_ext_mhpmcountersh check is gen_isa_compare's (no bin: S-3b).
- Coverpoints:
  - cp_mcycle_rel (iff after_write_evt || window_evt) = rvfi_ext_mcycle relation at the event: bins eq_after_write{first record after a retired mcycle(h) write: value == written + cycles since the write (offset per gen_tb_architecture.md 8.2)}, jump_after_write{first record after the write: discontinuity vs the previous record}, eq_inhibited{inhibit window end: every consecutive pair of records in the window has equal rvfi_ext_mcycle}, inc_debug{debug window end: rvfi_ext_mcycle strictly increasing across every consecutive pair of the >= 8 debug records}
  - cp_hpm_moved (iff rvfi_evt) = number of rvfi_ext_mhpmcounters elements that changed vs the previous item: bins none{0}, one{1}, several{[2:MHPMCounterNum]}
  - cp_debug = rvfi_ext_debug_mode of the record (or of the window): bins no{0}, yes{1}
- Crosses:
  - cr_rel_debug = cp_mcycle_rel x cp_debug: bins inc_dbg{inc_debug,yes}, jump_run{jump_after_write,no}, inh_run{eq_inhibited,no}; ignore inc_debug x no, eq_inhibited/jump_after_write x yes: not sampled (the former inc_run witness bin is retired, S-3b).
  - cr_moved_debug = cp_hpm_moved x cp_debug: bins one_dbg{one,yes}, several_run{several,no}, none_run{none,no}
- Adopted (riscv-dv): none
- TP items: TP-PMC-003, TP-PMC-005, TP-PMC-023, TP-PMC-051, TP-PMC-055

---------------------------------------------------------------------------------------------------

## Counts
- Covergroups: 22
- Coverpoints: 141 (12 of them cross-operand-only copies; owners CG-DBG-001.cp_cause and
  CG-DBG-012.cp_mode_dbg)
- Coverpoint bins: 648 legal (12 on cross-operand-only coverpoints, 8 witness / probe-gated
  "not in manifest": req0_mode0, cp_mode_dbg.m, cp_trap_dbg.ok, CG-DBG-007/CG-PMC-005 nop0,
  dummy_slot, dummy_mul, dummy_div); named ignore_bins: 21 (coverpoint: reserved, s_h,
  haltreq_step, other, CG-PMC-007.cp_coincident lsu_wait_cycle / if_wait_cycle / load_req /
  store_req / jump / branch (X-18); cross: ebreaks_0 (B15 spec-side), tsel_dbg_app (DbgHwBreakNum =
  1), step_sleep (X-8), mul_dum_gt (the dummy mul is single-cycle), hpm_lsu / hpm_if / hpm_load /
  hpm_store / hpm_jump / hpm_branch / hpmh_load (X-18))
- Cross bins: 910 legal (3 probe-gated "not in manifest": dummy_f, dummymul_gt, dummydiv_gt)
- Manifest-eligible bins: 1535 (628 coverpoint + 907 cross); every one is owned by >= 1 TP item
  (script-verified: every legal bin outside the witness / probe-gated / cross-operand-only sets
  appears in a TP Bins line or as the component of a listed cross bin)
- Adopted (riscv-dv) bins: 0
- Bins referenced by at least one TP item: 1548 distinct (the 1535 manifest-eligible bins plus 13
  cross-component copies on cross-operand-only / witness coverpoints), 2490 CSV rows
- Fix-brief-2 changes (Critic pre-review T-034): S-2 rule applied to CG-DBG-003 (sample premise,
  cp_outcome, reenter), CG-DBG-004 (ebreak excluded), CG-DBG-006 (one_ok, ebreakdbg_trap retired
  -> ebreakdbg_ok) and CG-PMC-002 (counter-model rule, has_ebreak_dbg); post-op sampling in
  CG-DBG-006 (step_armed), CG-DBG-007 and CG-PMC-005 (per (op, field) with nop0); boundary window
  definitions W-* and the core_busy_o port rule (hidden / sleep_hidden / *_hidden bins);
  per-coverpoint iff in CG-DBG-011, CG-PMC-001, CG-PMC-008; witness bins retired
  (cp_hpm_hi.all_zero, cp_mcycle_rel.inc, cr_rel_debug.inc_run, cycle_tick and mcycle(h)_tick) or
  marked (req0_mode0, m, ok); div_wait re-cut (cp_div_shape / cr_div_shape, DIV_STALL_FULL /
  DIV_STALL_ZERO); exactness class per index in CG-PMC-003; cross-operand-only copies marked
  (CG-DBG-006.cp_cause, CG-TRG-002.cp_cause_rb, CG-DBG-004/008/011 mode); S-12 bins cp_en_edge /
  cr_edge_outcome, cp_step_at_dret / cr_step_next, cp_arm_hist / cr_hist_fired, inhibit_mid /
  set_mid / cleared_mid / partial, cp_pin_tr / cr_pin_tr_effect; cr_idx_dummy as probe-free B7
  evidence; every symbolic bin carries its predicate; MHPMCounterNum-derived shorthands HPM_LAST /
  HPM_CTRL_MASK.
- Fix-brief additions (Critic v1): CG-DBG-001.cp_entry_ctx.flush_wfi, CG-DBG-001.cp_busy_dip (3 bins),
  CG-DBG-001.cr_cause_ctx.haltreq_flush_wfi, CG-DBG-001.cr_ctx_busy (3 bins) for F-DBG-068 and the
  one-cycle core_busy_o dip (F-DBG-044/059); CG-DBG-011.cp_wfi_busy_dip.one and cr_wfi_busy (2 bins);
  CG-TRG-001.cp_td1_rb.en_after_hit carries the folded F-TRG-028. Feature lists keep ALIAS/FOLDED IDs
  (traceability resolves them to the canonical or parent ID).
- Fix-brief-3 changes (rtl-arch T-053 fact-check, plan v2b): Conventions gained the same-cycle
  rule, W-WB(X) and the C-1 / C-3 / C-5 / C-10 / C-11 / C-12 / C-13 / C-14 / C-16 statements;
  CG-DBG-001: flush_wfi covers the stepped wfi, new cr_cause_ctx.step_flush_wfi, step_sleep is an
  ignore_bin (X-8; sleep_one / sleep_hidden stay reachable through the unstepped wfi woken by
  debug_req_i, TP-DBG-071 (b)), cp_busy_dip anti-vacuity re-anchored; CG-DBG-006: cp_retired and
  cp_haltreq predicates (Zcmp = one instruction, C-12; the zero-retirement re-halt, TP-DBG-054);
  CG-DBG-012: req1_mode0 / req1_mode1 predicates and anti-vacuity per X-6 (C-3); CG-TRG-001:
  cp_td1_exec_w is the post-op bit (TP-TRG-004), B3 mark extended to the *_rd bins; CG-PMC-003:
  exactness classes carry the C-10 precondition, new cp_variant fence_i / br_wb_wait / mul_wb_wait /
  div_wb_wait with fencei_eq and the B17 evidence bins brwait_gt / mulwait_gt / divwait_gt,
  gnt_delay predicate (count 0), cr_idx_dummy: mul_dum_gt ignored and mul_dum_zero added;
  CG-PMC-004: const_onehot = 1 << (N - MHPMCOUNTER_BASE) (D20); CG-PMC-007: the six ID-stage
  coincidence bins and their seven cross bins are ignore_bins (X-18), new retire_c_in_wb with
  hpm_retc / hpmh_retc (counter 10, X-17); every '- TP items' line regenerated from the items'
  Bins lines.
- Note: trace_tp_bin_dbg_trg_pmc.csv lists, for every cross bin an item names, the component
  coverpoint bins that cross bin implies (a cross hit requires them), so each item's rows are the
  full set of bins the fcov-expectation manifest must declare for it.

## Probe candidates
- CG-DBG-001.cp_entry_ctx (all bins) and CG-DBG-002.cp_coincident: derived from the TB dbg_model
  (RVFI + bus monitors). The FLUSH/IRQ_TAKEN/DBG_TAKEN_* distinction is a controller-FSM property;
  if the model proves ambiguous the fallback is the RTL's own coverage nets `fcov_debug_entry_if`,
  `fcov_debug_entry_id`, `fcov_interrupt_taken`, `fcov_pipe_flush`, `fcov_debug_wakeup`
  (rtl/ibex_controller.sv:1085-1095) or `ctrl_fsm_cs` (tb-infra probe candidate P4), coverage-only.
- CG-TRG-002.cp_ctx.dummy_slot / cr_ctx_fired.dummy_f: whether a dummy instruction occupied the
  matched pc is invisible at the boundary (RVFI excludes dummies). Boundary alternative: none
  reliable. Probe-gated on `dummy_instr_id_o` (P1, accepted coverage-only) and marked "not in
  manifest" until the probe register carries it (S-13); TP-TRG-026 proves dummy insertion from
  RVFI retirement gaps instead.
- CG-PMC-003.cp_variant.dummy_mul / dummy_div and cr_variant_rel.dummymul_gt / dummydiv_gt: binning
  the dummy type needs the same P1 probe; probe-gated, not in manifest. The probe-free B7 evidence
  is CG-PMC-002.cp_window.has_dummy (CSR state plus delta > RVFI count) and
  CG-PMC-003.cr_idx_dummy (wait counters moving in an ALU-only window with dummies on).
- CG-PMC-003 exactness classes: loads/stores/jumps/branches/taken/ret_c are exact from RVFI;
  mul_wait / div_wait are exact from RVFI gaps under the S-4 qualifiers (no probe); lsu_wait /
  if_wait are bound-class and their `eq` bins are sampled only for TB-constructed single-kind
  windows. If closure needs `eq` on lsu_wait / if_wait beyond those windows, the candidate is
  `perf_dside_wait_o` / `perf_iside_wait_o` (ibex_id_stage nets), a new coverage-only request that
  is not in the probe register (the DV Lead decides).
- Window definitions W-DEC / W-FLUSH / W-IRQTAKEN / W-DBGTAKEN / W-WAITSLEEP (Conventions) are
  boundary-derived; the P4 nets (`ctrl_fsm_cs`, `fcov_*`, conditionally accepted coverage-only) are
  the fallback only where the redirect-target request cannot be identified.
- CG-PMC-002.cp_coherence.wb_retiring / wb_faulting and CG-PMC-007.cp_coincident: WB occupancy in
  the read/write cycle is reconstructed from RVFI order and dbus timing; fallback probe
  `instr_done_wb` / `perf_instr_ret_wb_spec_o` (ibex_wb_stage), coverage-only.
- CG-TRG-002.cp_ctx.ibus_stall: "match evaluated while the fetch is outstanding" is derived from the
  ibus monitor (request granted, rvalid pending) at the time of the DmHaltAddr fetch; no probe
  needed unless the timing is ambiguous, then `pc_if_o` (ibex_if_stage), coverage-only.
No checker depends on any of these; every probe would be registered before use per tb-infra
section e.


# 3.6 Areas IMEM, DMEM, FE, IC: Instruction and data memory protocol, LSU, fetch stage, instruction cache


T-006 subagent output for the area group IMEM, DMEM, FE, IC (156 feature IDs after the Critic v1
fixes: F-IMEM-001..032, F-DMEM-001..051, F-FE-001..025, F-IC-001..048; 129 ACTIVE, 11 ALIAS, 16
FOLDED; ALIAS/FOLDED IDs may still appear in Features lists, traceability resolves them to the
canonical ID). Companion of tp_mem_fetch_icache.md. Revision 2 folds the Critic pre-review
(gen_critic_fcov_drafts_prereview_v1.md, S-3/S-5/S-7/S-8/S-12/S-14, M-02/M-04) per README_FIX2_BRIEF.md;
revision 3 folds rtl-arch's RTL fact-check (T-053, gen_tp_parts_rtl_factcheck.md Sections 1 and 3.mem_a /
3.mem_b) and the round-2 review residuals per README_FIX3_BRIEF.md (the C-n conventions are stated once in
tp_mem_fetch_icache.md's header).
Every covergroup lives in the gen_ namespace and samples from the DUT boundary, the memory/RAM/key
agents' own transaction records, or RVFI. The RAM-model shadow-tag view used by CG-IC-003 and
CG-FE-002.cp_halves_src is boundary-derived (gen_icache_ram_model mirrors every tag write it receives
on ic_tag_*; hit/miss/way/validity per lookup follow from that mirror and the bus records) and is NOT
a probe (P2 was rejected, gen_critic_tb_arch_components_v1.md C8). The only probe-gated bin is
CG-FE-004.cp_dummy_seen (P1 dummy_instr_id_o), marked "probe-gated (P1), not in manifest"; P3, P4 and
P5 have no bin (see Probe candidates).
Parameter sources: rtl/ibex_pkg.sv (IC_NUM_WAYS=2, IC_NUM_LINES=256, IC_LINE_BEATS=2, IC_INDEX_W=8,
IbexMuBiOn=4'b0101, IbexMuBiOff=4'b1010, $bits(irq_fast_i)=15); rtl/ibex_icache.sv NUM_FB=4,
FB_THRESHOLD=NUM_FB-2 (I-side outstanding bound NUM_FB*IC_LINE_BEATS, reachable only via a branch
lookup with NUM_FB-1 lines in flight; linear prefetch holds at most FB_THRESHOLD+1 = NUM_FB-1 non-stale
buffers = (NUM_FB-1)*IC_LINE_BEATS beats, F-FE-017); D-side outstanding bound GEN_DBUS_MAX_OUTSTANDING=2
(MEM-04). Bin expressions below use the parameter names; the resolved numbers appear only in
explanatory text. Informational bins (TP-IMEM-040, TP-DMEM-062, TP-DMEM-063, TP-IC-038) are excluded
from the closure measure.

Conventions: "agent record" = the per-transaction record kept by gen_imem_agent / gen_dmem_agent /
gen_icache_ram_model / gen_scr_key_agent (issue cycle, grant cycle, rvalid cycle, injected error
class, outstanding depth before/after, consumed-by-retirement mark). knob:* values are the regime knobs
of the brief; the cross-cutting subagent (fcov_xcut.md CG-REG-*) owns their bins; here a knob
coverpoint is marked "(cross operand only)" and has no closure bin of its own, it exists so that a DUT
observation can be crossed with the regime under which it happened (Critic S-5). RVFI-anchored events
are back-dated by one cycle (rvfi_valid is one flop after WB exit, rtl/ibex_core.sv:1868); an
ebreak that enters debug mode has rvfi_trap = 0 and is identified by is_ebreak(rvfi_insn) &&
!rvfi_trap && next fetch == DmHaltAddr (rtl/ibex_core.sv:1885-1886, Critic S-2). "sample (x)" in a
multi-event covergroup names the event; every coverpoint of such a group carries an "iff <event>"
guard so it samples only on the event for which it is defined (Critic S-3c). Negative and "check
passed" outcomes that a checker owns are not bins: they are named in the coverpoint text as the
checker's property and, where a value bin would be meaningless, an ignore_bins with the checker name
(Critic S-3b). Bins whose value is a predicate are written name{predicate}; bins whose value is a
number or range are written name{value}. Redirects and their targets are derived from RVFI (C-1 / C-14:
the redirect is "the next record's rvfi_pc_rdata != pc + len", its target that next rvfi_pc_rdata;
rvfi_pc_wdata carries the target only on branch / jump / fence.i records, trap / mret / dret records carry
the next sequential fetch address there, X-1); a bin that names a bus request for a redirect target is
qualified by a miss or icache_enable == 0, never inferred for a hit. Bins that credit an open
bug-candidate behaviour carry the bug tie (B16 in CG-DMEM-007).

---------------------------------------------------------------------------------------------------

## IMEM covergroups

### CG-IMEM-001: gen_cg_imem_handshake
- Features: F-IMEM-001, F-IMEM-002, F-IMEM-003, F-IMEM-004, F-IMEM-005, F-IMEM-010, F-IMEM-029
- Sample: instr_req_o & instr_gnt_i (grant cycle); condition: the gen_imem_agent record of the granted
  request is closed (issue cycle known); anti-vacuity: grants only exist while the DUT fetches; a hit
  proves a request was held for exactly the binned number of cycles under the recorded knob, and the
  stability checks of gen_sva_ibus ran over that wait. The agent's combinational-versus-registered
  grant generation (F-IMEM-004/F-IMEM-029) is a TB observation kept in the agent log, not DUT
  coverage (Critic S-5); the DUT-side evidence is cr_delay_x_knob.d0_same.
- Coverpoints:
  - cp_gnt_delay = grant cycle - issue cycle of the record: bins d0{0}, d1{1}, d2_3{[2:3]},
    d4_15{[4:15]}, d16p{[16:$]}
  - cp_b2b = instr_gnt_i && $past(instr_gnt_i) && $past(instr_req_o) (grant in this and the previous
    cycle with the request high in both): bins yes{1}, no{0}
  - cp_beat = instr_addr_o[2] of the granted word (beat within the IC_LINE_BEATS-beat line): bins
    w0{0}, w1{1}
  - cp_addr_lsb = instr_addr_o[1:0]: bins aligned{2'b00}; ignore_bins other{[1:3]}: the icache drives
    [1:0]=00 by construction (F-IMEM-002); an occurrence is a gen_sva_ibus failure, not coverage
  - cp_gnt_knob = knob:imem_gnt_delay in force at the grant (cross operand only): values same_cycle,
    short, long, random (definitions fcov_xcut.md CG-REG-002: same_cycle = 0, short = 1..3,
    long = 4..32 with 10% 33..128, random = per-request mix of the three)
- Crosses:
  - cr_delay_x_knob = cp_gnt_delay x cp_gnt_knob: bins d0_same{d0,same_cycle}, d1_short{d1,short},
    d2_3_short{d2_3,short}, d4_15_long{d4_15,long}, d16p_long{d16p,long}, d0_random{d0,random},
    d4_15_random{d4_15,random}, d16p_random{d16p,random}; ignore_bins same_cycle x d1|d2_3|d4_15|d16p,
    short x d0|d4_15|d16p, long x d0|d1|d2_3: the knob value forbids that delay
  - cr_b2b_x_beat = cp_b2b x cp_beat: bins b2b_w0{yes,w0}, b2b_w1{yes,w1} (no impossible combination;
    no x w0/w1 are unnamed auto bins, not required)
- Adopted (riscv-dv): none
- TP items: TP-IMEM-001, TP-IMEM-002, TP-IMEM-003, TP-IMEM-004, TP-IMEM-005, TP-IMEM-007,
  TP-IMEM-036

### CG-IMEM-002: gen_cg_imem_response
- Features: F-IMEM-006, F-IMEM-007, F-IMEM-008, F-IMEM-009
- Sample: instr_rvalid_i; condition: the agent record matches this response to its granted request
  (in-order queue head); anti-vacuity: responses exist only for granted requests, so every hit is
  one full req/gnt/rvalid triple whose ordering gen_chk_ibus_proto verified. The outstanding cap
  (knob:imem_outstanding_cap) is TB behaviour and has no bin here (Critic S-5); the DUT-side
  behaviour under a withheld grant is cr_held_x_depth.
- Coverpoints:
  - cp_rvalid_delay = rvalid cycle - grant cycle of the record: bins d1{1}, d2_3{[2:3]},
    d4_15{[4:15]}, d16p{[16:$]}; ignore_bins d0{0}: forbidden by the agent (rule 3, inventory s2;
    Q-DL-9 default)
  - cp_outstanding_before = granted-and-unanswered beats before this rvalid (agent count): bins
    o1{1}, o2{2}, o3{3}, o4{4}, o5{5}, o6{(NUM_FB-1)*IC_LINE_BEATS}, o7{NUM_FB*IC_LINE_BEATS-1},
    o8{NUM_FB*IC_LINE_BEATS}; ignore_bins o0{0}: an rvalid with nothing outstanding is a protocol
    violation (gen_chk_ibus_proto), not coverage; ignore_bins over{[NUM_FB*IC_LINE_BEATS+1:$]}: the
    RTL bound (F-IMEM-008), a hit is a gen_chk_ibus_proto failure. o7/o8 are reachable only through
    the branch-lookup path (NUM_FB-1 stale lines + IC_LINE_BEATS target beats, TP-IMEM-008); stale
    beats granted before a redirect stay in this count
  - cp_max_outstanding = running maximum of the outstanding count since the last redirect, sampled
    iff the count returns to 0 with this rvalid: bins m1{1}, m2{2}, m3_4{[3:4]},
    m5_7{[5:NUM_FB*IC_LINE_BEATS-1]}, m8{NUM_FB*IC_LINE_BEATS}
  - cp_burst = consecutive instr_rvalid_i cycles ending at this one: bins b1{1}, b2{2},
    b3_4{[3:4]}, b5p{[5:$]}
  - cp_err_class = injected error class of this beat (agent record): bins none{no injection},
    bus_err{instr_err_i == 1, codeword clean}, intg_single{one flipped bit in instr_rdata_i[38:0],
    instr_err_i == 0}, intg_double{two flipped bits, instr_err_i == 0}
  - cp_req_held_at_depth = instr_req_o was high and ungranted in the cycle before this rvalid (agent
    record of the waiting request): bins held{1}, no_req{0}
  - cp_rvalid_with_req = instr_req_o high in this rvalid cycle: bins yes{1}, no{0}
- Crosses:
  - cr_err_x_outstanding = cp_err_class x cp_outstanding_before: bins err_deep{bus_err x
    o5|o6|o7|o8}, intg_deep{intg_single|intg_double x o3|o4|o5|o6|o7|o8}, err_shallow{bus_err x
    o1|o2} (no impossible combination)
  - cr_delay_x_burst = cp_rvalid_delay x cp_burst: bins slow_then_burst{d16p x b3_4|b5p},
    fast_burst{d1 x b5p} (no impossible combination)
  - cr_held_x_depth = cp_req_held_at_depth x cp_outstanding_before: bins held_o1{held,o1},
    held_o2{held,o2}, held_o4{held,o4}, held_o5_7{held x o5|o6|o7}, no_req_o8{no_req,o8};
    ignore_bins held x o8: at the RTL bound the DUT does not request (F-IMEM-008); a hit is a
    gen_chk_ibus_proto failure. held_o<c> is the DUT holding its request while the agent withholds
    the grant at cap c (the DUT does not know the cap, TP-IMEM-008); no_req_o8 is the DUT's own bound
- Adopted (riscv-dv): none
- TP items: TP-IMEM-006, TP-IMEM-007, TP-IMEM-008, TP-IMEM-009, TP-IMEM-010, TP-IMEM-037

### CG-IMEM-003: gen_cg_imem_fetch_err
- Features: F-IMEM-011, F-IMEM-012, F-IMEM-013, F-IMEM-014, F-IMEM-015, F-IMEM-027, F-IMEM-028
- Sample: closure of an injected-error record (agent) correlated with RVFI: (a) rvfi_valid &
  rvfi_trap with mcause 1 for the instruction whose fetch word carried the error, or (b) the discard
  of that word (redirect / stale / hit) without a trap within the next 50 retirements, or (c) a later
  lookup of the errored line; condition: the agent injected an error on that beat; anti-vacuity: only
  injected beats sample, so every hit proves an error was delivered and the DUT's reaction (trap or
  silence) was checked by gen_isa_compare / gen_chk_bus_intg_rsp. The absence of an NMI after an
  I-side integrity error (D14) is gen_chk_bus_intg_rsp's property, not a bin.
- Coverpoints:
  - cp_outcome iff (a)|(b) = fate of the errored word: bins executed_trap{consumed by an instruction
    that retired with rvfi_trap, mcause 1}, spec_discarded_no_trap{never consumed: past a redirect
    target or the program end; no mcause-1 trap in the next 50 retirements},
    stale_after_redirect_no_trap{granted before a redirect, answered after it, discarded},
    hit_spec_ignored_no_trap{speculative branch-target request whose lookup hit; the response was
    consumed and its data discarded}
  - cp_half iff executed_trap = position of the errored beat within the consumed instruction: bins
    aligned_u32{32-bit at pc[1]==0, one word}, c16{16-bit instruction}, first_half{32-bit at
    pc[1]==1, error in the word holding pc}, second_half{error in the word holding pc+2},
    both_halves{both words errored}
  - cp_mtval iff executed_trap = handler-read mtval (rvfi_rd_wdata of the handler's csrr) relative to
    rvfi_pc_rdata: bins eq_pc{mtval == pc}, eq_pc_plus2{mtval == pc + 2}
  - cp_class = error class (agent record): bins bus_err{instr_err_i}, intg_single{1 flipped bit},
    intg_double{2 flipped bits}
  - cp_source iff executed_trap = fault attribution from the agent record and the PMP model: bins
    bus{bus error, PMP permits}, intg{integrity error, PMP permits}, pmp{PMP execute denial of pc,
    beat clean}, pmp_plus2{PMP denial of pc+2 only, beats clean}, bus_and_pmp{bus error and PMP
    denial on the same word}
  - cp_alert_major_bus = alert_major_bus_o in the rvalid cycle of the errored beat: bins pulsed{1},
    quiet{0}
  - cp_line_not_cached iff (c) = the later lookup of the errored line produced a bus request (agent
    record): bins refetch{1}; ignore_bins served_from_cache{0}: gen_chk_icache failure (F-IMEM-015)
- Crosses:
  - cr_half_x_class = cp_half x cp_class: bins first_intg{first_half x intg_single|intg_double},
    second_bus{second_half,bus_err}, both_bus{both_halves,bus_err}, c16_intg{c16,intg_double},
    aligned_bus{aligned_u32,bus_err} (no impossible combination)
  - cr_outcome_x_class = cp_outcome x cp_class: bins spec_intg{spec_discarded_no_trap x
    intg_single|intg_double}, stale_bus{stale_after_redirect_no_trap,bus_err},
    hit_spec_bus{hit_spec_ignored_no_trap,bus_err} (no impossible combination)
  - cr_half_x_mtval = cp_half x cp_mtval: bins second_plus2{second_half,eq_pc_plus2},
    first_pc{first_half,eq_pc}, both_pc{both_halves,eq_pc}, aligned_pc{aligned_u32,eq_pc},
    c16_pc{c16,eq_pc}; ignore_bins second_half x eq_pc, first_half x eq_pc_plus2, both_halves x
    eq_pc_plus2, aligned_u32 x eq_pc_plus2, c16 x eq_pc_plus2: mtval is the faulting fetch address
    (D10, F-IMEM-013/014)
- Adopted (riscv-dv): none
- TP items: TP-FE-020, TP-IMEM-011, TP-IMEM-012, TP-IMEM-013, TP-IMEM-014, TP-IMEM-015,
  TP-IMEM-016, TP-IMEM-019, TP-IMEM-030, TP-IMEM-031, TP-IMEM-034

### CG-IMEM-004: gen_cg_imem_redirect_seq
- Features: F-IMEM-016, F-IMEM-017, F-IMEM-018, F-IMEM-019, F-IMEM-020, F-IMEM-030
- Sample: (a) every redirect seen on RVFI (the next record's rvfi_pc_rdata != rvfi_pc_rdata + insn
  length, or rvfi_trap; trap/mret/dret records carry the next sequential address in rvfi_pc_wdata,
  C-1; back-dated to the pc_set cycle); (b) every grant (instr_req_o & instr_gnt_i),
  classified by the agent's address-sequence tracker; condition: for (a) the imem agent has at least
  one open or waiting record; anti-vacuity: (a) samples only while bus traffic is in flight or
  waiting across a redirect, so a hit proves stale beats were completed and discarded; (b) sequence
  kinds other than next_beat_same_line require a fill entered mid-line or a cache-state change.
  The equality rvfi_insn == memory image at rvfi_pc_rdata is gen_isa_compare's property, not a bin.
- Coverpoints:
  - cp_kind iff (a) = redirect kind from rvfi_insn / rvfi_trap / the next record: bins branch{branch
    opcode, rvfi_pc_wdata == pc + imm}, jal{JAL}, jalr{JALR}, exc{rvfi_trap && the next record is not
    rvfi_intr}, irq{the next record has rvfi_intr}, mret{MRET}, dret{DRET}, fencei{FENCE.I},
    dbg_entry{next fetch == DmHaltAddr: debug_req_i, or ebreak with rvfi_trap == 0 (S-2)}
  - cp_outstanding_at_redirect iff (a) = granted-and-unanswered beats in the redirect cycle: bins
    o0{0}, o1{1}, o2{2}, o3_4{[3:4]}, o5_8{[5:NUM_FB*IC_LINE_BEATS]}
  - cp_ungranted_req_at_redirect iff (a) = instr_req_o high and not yet granted in the redirect cycle:
    bins yes{1}, no{0}
  - cp_redirect_to_gnt_wait iff (a) && ungranted = cycles from the redirect to the grant of the
    request that was waiting (agent record): bins w1{1}, w2_3{[2:3]}, w4p{[4:$]}; the address
    stability over that wait is gen_sva_ibus's property (F-IMEM-017), not a bin
  - cp_seq_kind iff (b) = address-sequence class of this grant relative to the previous grant: bins
    next_beat_same_line{addr == prev + 4 within one IC_LINE_BYTES line}, wrap_to_w0{prev was the
    last beat of a line and this is beat 0 of the same line}, next_line{prev completed a line
    (after a wrap or from beat 0) and this is the next line's first beat},
    redirect_target{first grant after a redirect, addr == target word}, end_of_line_stop{prev was
    the last beat of a line entered mid-line and this is the next line's base with no wrap grant in
    between (cache off or invalidating)}
  - cp_cache_en iff (b) = cpuctrlsts.icache_enable at the grant (tracked from RVFI csr writes and
    rvfi_ext_debug_mode, which forces it off): bins on{1}, off{0}
  - cp_spec_hit_discard iff (a) && kind in {branch, jal, jalr} = the speculative target request's
    lookup hit; its response was consumed and the data discarded (the executed target word has no
    agent record of its own, the speculative record is marked discarded): bins yes{1}
- Crosses:
  - cr_kind_x_outstanding = cp_kind x cp_outstanding_at_redirect: bins branch_deep{branch,o5_8},
    exc_o2{exc,o2}, irq_o1{irq,o1}, fencei_o3_4{fencei,o3_4}, dbg_o1{dbg_entry,o1} (no impossible
    combination: linear prefetch can hold up to (NUM_FB-1)*IC_LINE_BEATS beats at any redirect)
  - cr_seq_x_en = cp_seq_kind x cp_cache_en: bins wrap_on{wrap_to_w0,on}, stop_off{end_of_line_stop,
    off}, target_on{redirect_target,on}, target_off{redirect_target,off}, next_line_on{next_line,on},
    next_line_off{next_line,off}; ignore_bins wrap_to_w0 x off, end_of_line_stop x on: F-IMEM-019/020
    make them impossible
- Adopted (riscv-dv): none
- TP items: TP-IMEM-003, TP-IMEM-017, TP-IMEM-018, TP-IMEM-019, TP-IMEM-020, TP-IMEM-021,
  TP-IMEM-035, TP-IMEM-038

### CG-IMEM-005: gen_cg_imem_gating
- Features: F-IMEM-021, F-IMEM-022, F-IMEM-023, F-IMEM-024, F-IMEM-025, F-IMEM-026, F-RST-010
  (parent of folded bins hosted here)
- Sample: (a) fetch-gate closure (fetch_enable_i leaves IbexMuBiOn, or core_busy_o falls to Off
  after a WFI retirement); (b) fetch-gate reopening (fetch_enable_i returns to IbexMuBiOn, or the
  wake after WFI); (c) reset release and the first instr_req_o after it; condition: the event
  happened; anti-vacuity: gate transitions are driven by the test (fetch_enable regime, WFI in the
  program, reset), so a hit proves the gate was exercised with the binned amount of traffic in
  flight. "No new line lookup while gated and instr_req_o == 0 whenever core_busy_o == Off" (C-4: the
  un-issued beats of lines open at the closure are legal; gen_chk_fetch_en / gen_chk_sleep), "no
  alert on an invalid code" (gen_chk_alerts, Q-DL-8) and "first address == boot_addr_i + 0x80" (gen_isa_compare
  / gen_chk_ibus_proto) are checker properties, not bins.
- Coverpoints:
  - cp_gate_cause iff (a)|(c) = why new requests stopped: bins wfi_sleep{core_busy_o == Off after a
    WFI retirement}, fetch_en_off{fetch_enable_i == IbexMuBiOff}, fetch_en_invalid{fetch_enable_i
    not in {IbexMuBiOn, IbexMuBiOff}}, reset_state{rst_ni low}
  - cp_fetch_en_code iff fetch_enable_i changed = the new 4-bit value: bins on{IbexMuBiOn},
    off{IbexMuBiOff}, invalid_0{4'h0}, invalid_1{4'h1}, invalid_2{4'h2}, invalid_3{4'h3},
    invalid_4{4'h4}, invalid_6{4'h6}, invalid_7{4'h7}, invalid_8{4'h8}, invalid_9{4'h9},
    invalid_b{4'hB}, invalid_c{4'hC}, invalid_d{4'hD}, invalid_e{4'hE}, invalid_f{4'hF} (the
    2**$bits(ibex_mubi_t) - 2 codes other than IbexMuBiOn and IbexMuBiOff)
  - cp_outstanding_at_gate iff (a) = beats granted and unanswered when the gate closed: bins o0{0},
    o1_4{[1:4]}, o5_8{[5:NUM_FB*IC_LINE_BEATS]}
  - cp_beats_issued_after_gate iff (a) = un-issued beats of fill buffers open at the closure that
    were requested on the bus after it (legal continuation, C-4): bins none{0}, some{[1:$]} (a hit
    on some proves the checker accepted the continuing beats and forbids only new line lookups)
  - cp_inflight_drain iff (a) && outstanding > 0 = cycles from the gate closure to the last
    outstanding rvalid (all answered while gated, beats issued after the closure included; stale
    beats are discarded, not consumed): bins c1_4{[1:4]}, c5_15{[5:15]}, c16p{[16:$]}
  - cp_resume iff (b) = first retirement after the gate reopened: bins held_pc_no_refetch{
    rvfi_pc_rdata == pc following the last pre-gate retirement, and no new bus request for that word
    (icache_enable pinned 0 by the owning item so a re-fetch is visible on the bus)},
    handler_pc{rvfi_pc_rdata == an interrupt/NMI vector or DmHaltAddr}
  - cp_first_req_cycle iff (c) = cycles from reset release to the first instr_req_o: bins c1{1},
    c2p{[2:$]}
  - cp_boot_class iff (c) = boot_addr_i: bins zero{32'h0}, low_ram{[31:28] == 0 && != 0},
    top_ffffff00{32'hFFFF_FF00}, random_aligned{any other value with [7:0] == 0}
- Crosses:
  - cr_cause_x_outstanding = cp_gate_cause x cp_outstanding_at_gate: bins wfi_o1_4{wfi_sleep,o1_4},
    fen_off_o5_8{fetch_en_off,o5_8}, fen_off_o1_4{fetch_en_off,o1_4}, fen_inv_o1_4{fetch_en_invalid,
    o1_4}; ignore_bins reset_state x o1_4|o5_8: no beat is outstanding in reset
- Adopted (riscv-dv): none
- TP items: TP-FE-028, TP-IMEM-022, TP-IMEM-023, TP-IMEM-024, TP-IMEM-025, TP-IMEM-026,
  TP-IMEM-027, TP-IMEM-028

### CG-IMEM-006: gen_cg_imem_stream_ctx
- Features: F-IMEM-008, F-IMEM-030, F-IMEM-029, F-IMEM-028
- Sample: rvfi_valid; condition: the instruction's delivery context is known from the agent records
  and the RAM-model shadow view (bus record or hit); anti-vacuity: the context classes other than
  in_order_seq need a miss in flight, a redirect or a straddle, so a hit shows the delivery context
  of an executed instruction under the recorded regime. "instr_req_o never changes in the same cycle
  as instr_gnt_i/instr_rvalid_i" (F-IMEM-029) is structural and checked by the agent's settle
  monitor, not a bin.
- Coverpoints:
  - cp_delivery = context of the executed word: bins in_order_seq{the word's record immediately
    follows the previous instruction's record}, hit_in_shadow_of_miss{the word hit while an older
    miss was outstanding; retired after the miss}, after_redirect_target{first instruction after a
    redirect, word == the target record}, straddle_two_records{rvfi_insn assembled from two records}
  - cp_regime = (knob:imem_gnt_delay, knob:imem_rvalid_delay) class in force (cross operand only):
    values fast_fast{same_cycle, min1}, slow_gnt{long, min1|short}, slow_rvalid{same_cycle|short,
    long}, both_slow{long, long}, random{either knob random}
  - cp_pmp_denied_word_on_bus iff the PMP model denies execute at the executing privilege = the agent
    saw the request for the denied word: bins seen{1} (RTL-defined, D9: the request is not gated by
    PMP; the fault is raised at ID; the owning item pins icache_enable = 0 so a hit never hides the
    request, C-14)
- Crosses:
  - cr_delivery_x_regime = cp_delivery x cp_regime: bins shadow_both_slow{hit_in_shadow_of_miss,
    both_slow}, straddle_slow_rvalid{straddle_two_records,slow_rvalid}, in_order_fast_fast{
    in_order_seq,fast_fast}, in_order_slow_gnt{in_order_seq,slow_gnt}, in_order_both_slow{
    in_order_seq,both_slow}, in_order_random{in_order_seq,random}, target_slow_gnt{
    after_redirect_target,slow_gnt} (no impossible combination)
- Adopted (riscv-dv): none
- TP items: TP-IMEM-029, TP-IMEM-030, TP-IMEM-032, TP-IMEM-033, TP-IMEM-036

### CG-IMEM-007: gen_cg_imem_driver_rules
- Features: F-IMEM-031, F-IMEM-032
- Sample: (a) instr_gnt_i; (b) instr_rvalid_i injected by the agent as unsolicited (TP-IMEM-040
  only); condition: none beyond the event; anti-vacuity: grants are agent actions, so every sample
  is one driver decision that gen_sva_ibus checked in the same cycle; the informational coverpoint
  samples only while the TP-IMEM-040 informational knob is set and is excluded from the closure
  measure. The driver rule "grant only while request" is a TB property; its coverage is the grant
  under each regime that could have produced a bare grant (cr_gnt_x_regime). "Every non-injected
  rvalid matches an outstanding beat" is gen_chk_ibus_proto's property, not a bin.
- Coverpoints:
  - cp_gnt_with_req iff (a) = instr_req_o in the grant cycle (cross operand only): bins
    with_req{1}; ignore_bins bare_gnt{0}: driver rule (inventory s2 rule 2 / s11); a hit is a
    gen_sva_ibus TB error
  - cp_gnt_regime iff (a) = knob:imem_gnt_delay at the grant (cross operand only): values
    same_cycle, short, long, random
  - cp_unsolicited_rvalid_case iff (b) (informational, TP-IMEM-040 only) = agent-injected extra
    rvalid classified by the icache state: bins no_expecting_buffer_ignored{no fill buffer awaited
    data: the beat is dropped and RVFI keeps matching the image}, expecting_buffer_consumed_shift{a
    buffer awaited data: the beat is consumed and later data shifts}, bad_secded_alert{corrupted
    codeword on the injected beat: alert_major_bus_o in that cycle}
- Crosses:
  - cr_gnt_x_regime = cp_gnt_with_req x cp_gnt_regime: bins req_same{with_req,same_cycle},
    req_short{with_req,short}, req_long{with_req,long}, req_random{with_req,random}
- Adopted (riscv-dv): none
- TP items: TP-IMEM-039, TP-IMEM-040

---------------------------------------------------------------------------------------------------

## DMEM covergroups

### CG-DMEM-001: gen_cg_dmem_handshake
- Features: F-DMEM-001, F-DMEM-002, F-DMEM-003, F-DMEM-004, F-DMEM-005, F-DMEM-006, F-DMEM-007,
  F-DMEM-008, F-DMEM-009, F-DMEM-010, F-DMEM-034, F-DMEM-035
- Sample: data_rvalid_i (one sample per completed transaction; the agent record carries the issue,
  grant and rvalid cycles and the grant-cycle payload); condition: agent record matched in order;
  anti-vacuity: samples exist only for granted data transactions, each of which passed
  gen_chk_dbus_proto's hold/stability/order checks; a hit proves the binned latency pair and depth
  occurred. Knob-by-knob crosses (gnt regime x rvalid regime) belong to fcov_xcut.md CG-REG-003
  cr_gnt_x_rvalid; here the knobs are crossed only with the measured delays.
- Coverpoints:
  - cp_gnt_delay = grant cycle - issue cycle: bins d0{0}, d1{1}, d2_3{[2:3]}, d4_15{[4:15]},
    d16p{[16:$]}
  - cp_rvalid_delay = rvalid cycle - grant cycle: bins d1{1}, d2_3{[2:3]}, d4_15{[4:15]},
    d16p{[16:$]}; ignore_bins d0{0}: forbidden by agent rule 2 (inventory s3)
  - cp_beat = role of the transaction: bins single{aligned access, one transaction}, first{first
    word of a split access}, second{second word of a split access}
  - cp_we = data_we_o of the record: bins load{0}, store{1}
  - cp_outstanding_before = granted-and-unanswered count before this rvalid: bins o1{1}, o2{2};
    ignore_bins o0{0}: unsolicited response, a protocol violation (Q-DL-9 default); ignore_bins
    over{[GEN_DBUS_MAX_OUTSTANDING+1:$]}: gen_chk_dbus_proto failure (MEM-04)
  - cp_req_with_prev_rvalid = a new data_req_o (next access) rose in this rvalid cycle: bins yes{1},
    no{0}
  - cp_addr_lsb = data_addr_o[1:0] at the grant: bins aligned{2'b00}; ignore_bins other{[1:3]}:
    gen_sva_dbus failure
  - cp_payload_changed_after_gnt = any of data_addr_o/data_we_o/data_be_o/data_wdata_o[38:0] changed
    in the cycle after the grant: bins changed{1}, same{0}
  - cp_gnt_knob = knob:dmem_gnt_delay in force (cross operand only): values same_cycle, short, long,
    random (fcov_xcut.md CG-REG-003: same_cycle = 0, short = 1..3, long = 4..32 with 10% 33..128)
  - cp_rvalid_knob = knob:dmem_rvalid_delay in force (cross operand only): values min1, short, long,
    random (min1 = exactly 1, short = 1..3, long = 4..32 with 10% 33..128)
- Crosses:
  - cr_delay_x_beat = cp_gnt_delay x cp_beat: bins d0_first{d0,first}, d16p_second{d16p,second},
    d4_15_single{d4_15,single}, d1_second{d1,second} (no impossible combination)
  - cr_b2b_x_we = cp_req_with_prev_rvalid x cp_we: bins b2b_load{yes,load}, b2b_store{yes,store}
  - cr_depth_x_beat = cp_outstanding_before x cp_beat: bins two_first{o2,first}, one_single{o1,
    single}, one_second{o1,second}; ignore_bins o2 x single: aligned accesses never have two
    outstanding (F-DMEM-008); ignore_bins o2 x second: responses are in order, the first word's
    response precedes the second's (F-DMEM-010)
  - cr_gnt_delay_x_knob = cp_gnt_delay x cp_gnt_knob: bins d0_same{d0,same_cycle}, d1_short{d1,
    short}, d2_3_short{d2_3,short}, d4_15_long{d4_15,long}, d16p_long{d16p,long}, d0_random{d0,
    random}, d16p_random{d16p,random}; ignore_bins same_cycle x d1|d2_3|d4_15|d16p, short x
    d0|d4_15|d16p, long x d0|d1|d2_3: the knob value forbids that delay
  - cr_rvalid_delay_x_knob = cp_rvalid_delay x cp_rvalid_knob: bins d1_min1{d1,min1}, d2_3_short{
    d2_3,short}, d4_15_long{d4_15,long}, d16p_long{d16p,long}, d1_random{d1,random}, d16p_random{
    d16p,random}; ignore_bins min1 x d2_3|d4_15|d16p, short x d4_15|d16p, long x d1|d2_3: the knob
    value forbids that delay
- Adopted (riscv-dv): none
- TP items: TP-DMEM-001, TP-DMEM-002, TP-DMEM-003, TP-DMEM-004, TP-DMEM-005, TP-DMEM-006,
  TP-DMEM-007, TP-DMEM-008, TP-DMEM-009, TP-DMEM-020, TP-DMEM-023, TP-DMEM-035, TP-DMEM-037,
  TP-DMEM-038, TP-DMEM-056, TP-DMEM-057

### CG-DMEM-002: gen_cg_dmem_be_lanes
- Features: F-DMEM-011, F-DMEM-012, F-DMEM-013, F-DMEM-014, F-DMEM-020, F-DMEM-035, F-DMEM-041,
  F-DMEM-050
- Sample: data_req_o & data_gnt_i; condition: agent record open; anti-vacuity: one sample per
  address phase; a hit proves the binned (size, offset, beat) produced the binned be pattern and
  the lane check of gen_chk_dbus_proto ran on it. Store-integrity correctness (zero syndrome of
  data_wdata_o[38:32] over the whole rotated word on req & gnt & we) is gen_chk_store_intg's
  property, not a bin; on loads the always-valid encoding is an RTL-defined observation covered
  only as cp_load_wdata_intg_valid (gen_tb_architecture.md 8.3 item 2; F-DMEM-050), never an error.
- Coverpoints:
  - cp_size = access size from funct3 of rvfi_insn of the owning instruction: bins byte{funct3[1:0]
    == 2'b00}, half{2'b01}, word{2'b10}
  - cp_offset = rvfi_mem_addr[1:0]: bins o0{0}, o1{1}, o2{2}, o3{3}
  - cp_beat = role of the transaction: bins single{aligned, one transaction}, first{first word of a
    split}, second{second word of a split}
  - cp_be = data_be_o: bins be_0001{4'b0001}, be_0010{4'b0010}, be_0100{4'b0100}, be_1000{4'b1000},
    be_0011{4'b0011}, be_0110{4'b0110}, be_1100{4'b1100}, be_1110{4'b1110}, be_0111{4'b0111},
    be_1111{4'b1111}; ignore_bins unreachable{4'b0000, 4'b0101, 4'b1001, 4'b1010, 4'b1011, 4'b1101}:
    no (size, offset, beat) produces them (LSU tables, MEM-08)
  - cp_we = data_we_o: bins load{0}, store{1}
  - cp_disabled_lane_nonzero iff store && be != 4'b1111 = a lane i with data_be_o[i] == 0 carries
    data_wdata_o[8*i+7:8*i] != 0: bins seen{1}, zero{0}
  - cp_load_wdata_intg_valid iff load = data_wdata_o[38:32] decodes with zero syndrome over
    data_wdata_o[31:0] (inverted 39/32 Hsiao code): bins valid{1}; ignore_bins invalid{0}:
    coverage-only observation, never an error (RTL-defined, F-DMEM-050; maps to the TB architecture's
    gen_dbus_cg.cp_load_wdata_intg_valid)
  - cp_masked_recompute_differs iff store && be != 4'b1111 = the code recomputed over the be-masked
    (zeroed) word differs from data_wdata_o[38:32]: bins yes{1: proves the store checker verifies
    the whole rotated word}, no{0: the disabled lanes happen to hold zero}
- Crosses:
  - cr_load_intg_x_size = cp_load_wdata_intg_valid x cp_size: bins valid_byte{valid,byte},
    valid_half{valid,half}, valid_word{valid,word}
  - cr_size_offset_beat_we = cp_size x cp_offset x cp_beat x cp_we, 32 legal bins:
    byte_o0_single_load, byte_o1_single_load, byte_o2_single_load, byte_o3_single_load,
    byte_o0_single_store, byte_o1_single_store, byte_o2_single_store, byte_o3_single_store,
    half_o0_single_load, half_o1_single_load, half_o2_single_load, half_o0_single_store,
    half_o1_single_store, half_o2_single_store, half_o3_first_load, half_o3_second_load,
    half_o3_first_store, half_o3_second_store, word_o0_single_load, word_o0_single_store,
    word_o1_first_load, word_o1_second_load, word_o2_first_load, word_o2_second_load,
    word_o3_first_load, word_o3_second_load, word_o1_first_store, word_o1_second_store,
    word_o2_first_store, word_o2_second_store, word_o3_first_store, word_o3_second_store (each
    bin = the tuple its name spells); ignore_bins (40 combinations): byte x o0|o1|o2|o3 x
    first|second x load|store (bytes never split), half x o0|o1|o2 x first|second x load|store
    (halfwords split only at offset 3), half x o3 x single x load|store, word x o0 x first|second x
    load|store, word x o1|o2|o3 x single x load|store: the split predicate (MEM-07) forbids them
  - cr_be_x_beat = cp_be x cp_beat, 14 legal bins: single_1111{be_1111,single}, single_0011{be_0011,
    single}, single_0110{be_0110,single}, single_1100{be_1100,single}, single_0001{be_0001,single},
    single_0010{be_0010,single}, single_0100{be_0100,single}, single_1000{be_1000,single},
    first_1110{be_1110,first}, first_1100{be_1100,first}, first_1000{be_1000,first},
    second_0001{be_0001,second}, second_0011{be_0011,second}, second_0111{be_0111,second};
    ignore_bins (16 combinations): single x be_1110|be_0111, first x
    be_0001|be_0010|be_0100|be_0011|be_0110|be_0111|be_1111, second x
    be_0010|be_0100|be_1000|be_0110|be_1100|be_1110|be_1111: the LSU tables (MEM-08) give the first
    word the upper (4 - offset) lanes and the second word the lower offset lanes
- Adopted (riscv-dv): none
- TP items: TP-DMEM-003, TP-DMEM-011, TP-DMEM-012, TP-DMEM-013, TP-DMEM-014, TP-DMEM-015,
  TP-DMEM-016, TP-DMEM-045, TP-DMEM-060

### CG-DMEM-003: gen_cg_dmem_misaligned
- Features: F-DMEM-015, F-DMEM-016, F-DMEM-017, F-DMEM-018, F-DMEM-024, F-DMEM-025, F-DMEM-026,
  F-DMEM-008 (parent of folded bins hosted here)
- Sample: final rvalid of a split access (the agent pairs the two records by the second address ==
  first + 4); condition: the pair closed; anti-vacuity: only split accesses sample; a hit proves
  the binned FSM path and per-beat latencies really occurred and gen_isa_compare checked the
  assembled data. The equality second == first + 4 is gen_chk_dbus_proto's property, not a bin.
- Coverpoints:
  - cp_type = split kind from rvfi_insn and rvfi_mem_addr[1:0]: bins lw_o1{LW, 1}, lw_o2{LW, 2},
    lw_o3{LW, 3}, lh_o3{LH, 3}, lhu_o3{LHU, 3}, sw_o1{SW, 1}, sw_o2{SW, 2}, sw_o3{SW, 3},
    sh_o3{SH, 3}
  - cp_path = second-grant timing relative to the first rvalid: bins gnt2_after_rvalid1{gnt(second)
    > rvalid(first)}, gnt2_before_rvalid1{gnt(second) < rvalid(first)}, gnt2_same_cycle_rvalid1{
    gnt(second) == rvalid(first)}
  - cp_beat1_rvalid_delay = rvalid(first) - gnt(first): bins d1{1}, d2_3{[2:3]}, d4p{[4:$]}
  - cp_beat2_gnt_delay = gnt(second) - issue(second): bins d0{0}, d1{1}, d2_3{[2:3]}, d4p{[4:$]}
  - cp_beat2_rvalid_delay = rvalid(second) - gnt(second): bins d1{1}, d2_3{[2:3]}, d4p{[4:$]}
  - cp_second_addr_page = relation of the two word addresses: bins same_page{second[31:12] ==
    first[31:12]}, page_cross{second[31:12] != first[31:12], including the wrap}
  - cp_wrap = the pair wraps the address space: bins wrapped{first == 32'hFFFF_FFFC && second ==
    32'h0}, no{0}
  - cp_gnts_done_dwell iff gnt2_before_rvalid1 = cycles between gnt(second) and rvalid(second)
    with data_req_o low (LSU in GNTS_DONE, no third request): bins c1_3{[1:3]}, c4p{[4:$]}
- Crosses:
  - cr_type_x_path = cp_type x cp_path: bins lw_o3_gnts_done{lw_o3,gnt2_before_rvalid1},
    sw_o1_wait_gnt{sw_o1,gnt2_after_rvalid1}, lh_o3_same{lh_o3,gnt2_same_cycle_rvalid1},
    sh_o3_gnts_done{sh_o3,gnt2_before_rvalid1}, lhu_o3_wait_gnt{lhu_o3,gnt2_after_rvalid1},
    sw_o2_same{sw_o2,gnt2_same_cycle_rvalid1} (no impossible combination)
  - cr_delays = cp_beat1_rvalid_delay x cp_beat2_gnt_delay x cp_beat2_rvalid_delay: bins
    all_slow{d4p,d4p,d4p}, fast_slow_fast{d1,d4p,d1}, slow_fast_slow{d4p,d0,d4p} (no impossible
    combination)
  - cr_wrap_x_type = cp_wrap x cp_type: bins wrap_lw_o1{wrapped,lw_o1}, wrap_lw_o3{wrapped,lw_o3},
    wrap_sh_o3{wrapped,sh_o3}, wrap_sw_o2{wrapped,sw_o2} (every type can wrap)
- Adopted (riscv-dv): none
- TP items: TP-DMEM-004, TP-DMEM-005, TP-DMEM-009, TP-DMEM-010, TP-DMEM-015, TP-DMEM-016,
  TP-DMEM-017, TP-DMEM-018, TP-DMEM-019, TP-DMEM-020, TP-DMEM-021, TP-DMEM-022, TP-DMEM-023

### CG-DMEM-004: gen_cg_dmem_split_err
- Features: F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-027, F-DMEM-015 (parent of folded bins hosted
  here)
- Sample: final (or abandoned second) rvalid of a split access with at least one injected error
  (agent record); condition: injected; anti-vacuity: only error-injected splits sample; a hit
  proves the trap, mtval and the second-beat behaviour were checked by gen_isa_compare /
  gen_chk_dbus_proto. Whether an errored write is committed to the memory image is the agent's
  policy (writes granted before or without an error are committed), so the DUT-side fact is the
  second-word request itself (cp_second_issued x cr_beat_x_we), not "landed".
- Coverpoints:
  - cp_err_beat = which word carried data_err_i: bins first{first word only}, second{second word
    only}, both{both words}
  - cp_we: bins load{0}, store{1}
  - cp_mtval = handler-read mtval (rvfi_rd_wdata of the handler's csrr): bins unaligned_ea{mtval ==
    rvfi_mem_addr}, second_word_aligned{mtval == (rvfi_mem_addr & ~32'h3) + 4}
  - cp_second_issued iff first|both = the second request was granted after the first-beat error
    (agent record): bins yes{1}; ignore_bins no{0}: gen_chk_dbus_proto failure (RTL-defined MEM-10;
    security note S1 of gen_bug_log.md)
  - cp_second_gnt_delay_after_err iff first|both = gnt(second) - the error rvalid cycle: bins d0{0},
    d1_3{[1:3]}, d4p{[4:$]}
  - cp_handler_ls_waited iff first|both = class of the handler's first instruction (the exception
    itself follows the abandoned second response, X-23, so the handler never overlaps it): bins
    yes{1: a load/store, its data_req_o granted after the second rvalid}, not_ls{0: not a
    load/store}
  - cp_second_rvalid_gap iff first|both = cycles from the errored first rvalid to the second rvalid,
    with no data_req_o in between (gen_chk_dbus_proto property): bins g1_9{[1:9]}, g10p{[10:$]}
- Crosses:
  - cr_beat_x_we = cp_err_beat x cp_we: bins first_load{first,load}, first_store{first,store},
    second_load{second,load}, second_store{second,store}, both_load{both,load},
    both_store{both,store}
  - cr_beat_x_mtval = cp_err_beat x cp_mtval: bins first_ea{first,unaligned_ea},
    second_aligned{second,second_word_aligned}, both_ea{both,unaligned_ea}; ignore_bins first x
    second_word_aligned, second x unaligned_ea, both x second_word_aligned: contradict MEM-10
- Adopted (riscv-dv): none
- TP items: TP-DMEM-024, TP-DMEM-025, TP-DMEM-026, TP-DMEM-027, TP-DMEM-038, TP-DMEM-055

### CG-DMEM-005: gen_cg_dmem_load_data
- Features: F-DMEM-018, F-DMEM-019, F-DMEM-040, F-DMEM-039
- Sample: rvfi_valid of a load or store; condition: no trap; anti-vacuity: one sample per retired
  load/store; a hit proves the binned (insn, offset, sign) load result was compared by
  gen_isa_compare against the agent memory. The agent's random payload on store responses is a
  TB driver rule covered by CG-DMEM-009.cp_rdata_store_resp, not here.
- Coverpoints:
  - cp_insn = rvfi_insn opcode/funct3: bins lb{LOAD, 3'b000}, lbu{LOAD, 3'b100}, lh{LOAD, 3'b001},
    lhu{LOAD, 3'b101}, lw{LOAD, 3'b010}, sb{STORE, 3'b000}, sh{STORE, 3'b001}, sw{STORE, 3'b010}
  - cp_offset = rvfi_mem_addr[1:0]: bins o0{0}, o1{1}, o2{2}, o3{3}
  - cp_sign_bit iff load = MSB of the loaded datum before extension (bit 7 / 15 / 31 for
    byte / half / word): bins s0{0}, s1{1}
  - cp_rd iff load = rvfi_rd_addr: bins x0{0}, other{[1:31]}
- Crosses:
  - cr_insn_offset_sign = cp_insn x cp_offset x cp_sign_bit, 40 load bins: lb_o0_s0, lb_o0_s1,
    lb_o1_s0, lb_o1_s1, lb_o2_s0, lb_o2_s1, lb_o3_s0, lb_o3_s1, lbu_o0_s0, lbu_o0_s1, lbu_o1_s0,
    lbu_o1_s1, lbu_o2_s0, lbu_o2_s1, lbu_o3_s0, lbu_o3_s1, lh_o0_s0, lh_o0_s1, lh_o1_s0, lh_o1_s1,
    lh_o2_s0, lh_o2_s1, lh_o3_s0, lh_o3_s1, lhu_o0_s0, lhu_o0_s1, lhu_o1_s0, lhu_o1_s1, lhu_o2_s0,
    lhu_o2_s1, lhu_o3_s0, lhu_o3_s1, lw_o0_s0, lw_o0_s1, lw_o1_s0, lw_o1_s1, lw_o2_s0, lw_o2_s1,
    lw_o3_s0, lw_o3_s1 (each bin = the tuple its name spells); ignore_bins sb|sh|sw x
    o0|o1|o2|o3 x s0|s1: stores have no loaded datum
  - cr_x0_x_insn = cp_rd x cp_insn: bins x0_lw{x0,lw}, x0_lb{x0,lb}, x0_lhu{x0,lhu}, x0_lh{x0,lh},
    x0_lbu{x0,lbu}; ignore_bins x0|other x sb|sh|sw: stores have no rd (rvfi_rd_addr reads 0 on a
    store record, F-DMEM-051)
- Adopted (riscv-dv): none
- TP items: TP-DMEM-028, TP-DMEM-029, TP-DMEM-030, TP-DMEM-031

### CG-DMEM-006: gen_cg_dmem_bus_err
- Features: F-DMEM-036, F-DMEM-037, F-DMEM-038, F-DMEM-030, F-DMEM-040, F-DMEM-032
- Sample: rvfi_valid & rvfi_trap with mcause 5 or 7 not attributed to PMP (PMP model says allowed);
  condition: agent injected data_err_i on that access; anti-vacuity: only injected errors sample,
  so a hit proves a real bus error produced the trap the checkers verified. "rd unchanged for the
  errored load" is gen_isa_compare's property, not a bin.
- Coverpoints:
  - cp_cause = handler-read mcause: bins load_5{5}, store_7{7}
  - cp_size = funct3 of the errored access: bins byte{2'b00}, half{2'b01}, word{2'b10}
  - cp_id_insn = class of the instruction in ID when the error response arrived (the next fetched
    instruction in program order, from the agent word records and RVFI): bins none{no instruction
    in ID: fetch stalled}, alu{ALU op}, illegal{illegal encoding}, ecall{ECALL}, ebreak{EBREAK},
    fetch_err{word delivered with instr_err_i}, load_store{load or store}, branch{branch or jump},
    csr{CSR access}, wfi{WFI}
  - cp_id_killed_reexecuted iff cp_id_insn != none = the ID instruction had not retired before the
    trap record and retired (or trapped) after the handler's mret: bins yes{1}
  - cp_rd_x0 iff load_5 = rvfi_rd_addr of the errored load: bins x0{0}, other{[1:31]}
  - cp_irq_pending_at_err = an enabled interrupt line (irq pins & mie) high in the error rvalid
    cycle: bins yes{1}, no{0}
  - cp_dbg_req_at_err = debug_req_i high in the error rvalid cycle: bins yes{1}, no{0}
  - cp_next_req_suppressed iff the control run of the same seed shows a back-to-back data_req_o in
    the error cycle: bins yes{1: no data_req_o in the error rvalid cycle}
  - cp_trap_order iff cp_irq_pending_at_err == yes || cp_dbg_req_at_err == yes: bins exc_first{1: the
    mcause 5/7 record precedes the interrupt / debug entry record}
  - cp_irq_taken_at iff cp_irq_pending_at_err == yes = record after which the pending ordinary
    interrupt was taken: bins after_mret{the handler's mret record}, after_mie_write{a handler
    record that set mstatus.MIE}; ignore_bins at_handler_entry{the exception record itself}: the
    trap entry clears MIE (rtl/ibex_cs_registers.sv:924, C-6), a hit is a gen_chk_irq failure
  - cp_dbg_entry_after_exc iff cp_dbg_req_at_err == yes: bins before_handler{1: no handler record
    between the exception record and the DmHaltAddr record (debug_req_i is not MIE-gated)}
  - cp_b14_records iff cp_id_insn traps on its re-execution (informational, TP-DMEM-063 only) =
    number of trap records for the pair: bins two_in_order{2: the WB error's record, then the
    re-executed ID instruction's own record}; ignore_bins one{1}: re-opens B14 (reported by the
    informational fire-check, not coverage)
- Crosses:
  - cr_cause_x_id = cp_cause x cp_id_insn: bins load_illegal{load_5,illegal}, load_ecall{load_5,
    ecall}, store_fetch_err{store_7,fetch_err}, load_ls{load_5,load_store}, store_ebreak{store_7,
    ebreak}, load_wfi{load_5,wfi}, store_illegal{store_7,illegal}, load_none{load_5,none} (no
    impossible combination)
  - cr_cause_x_irq = cp_cause x cp_irq_pending_at_err: bins load_irq{load_5,yes}, store_irq{store_7,
    yes}
  - cr_cause_x_dbg = cp_cause x cp_dbg_req_at_err: bins load_dbg{load_5,yes}, store_dbg{store_7,yes}
- Adopted (riscv-dv): none
- TP items: TP-DMEM-030, TP-DMEM-032, TP-DMEM-033, TP-DMEM-034, TP-DMEM-035, TP-DMEM-036,
  TP-DMEM-037, TP-DMEM-038, TP-DMEM-054, TP-DMEM-063

### CG-DMEM-007: gen_cg_dmem_intg
- Features: F-DMEM-041, F-DMEM-039
- Sample: data_rvalid_i with an injected integrity corruption (agent record); condition:
  injected; anti-vacuity: only corrupted responses sample; a hit proves gen_chk_bus_intg_rsp saw
  the alert, the per-beat RF-suppression rule (C-8) and the NMI it checks. The alert and suppression bins are qualified by the
  injection (the stimulus that produces them).
- Coverpoints:
  - cp_class = flipped bits in data_rdata_i[38:0]: bins single{1}, double{2}
  - cp_we: bins load{0}, store{1}
  - cp_beat: bins single{aligned}, first{first word of a split}, second{second word of a split}
  - cp_with_bus_err = data_err_i also set on that beat: bins yes{1}, no{0}
  - cp_alert = alert_major_bus_o in the rvalid cycle: bins pulsed{1}; ignore_bins quiet{0}:
    gen_chk_bus_intg_rsp failure
  - cp_rf_suppressed iff load = the load's record has rvfi_rd_addr == 0 (write suppressed) and no
    rvfi_trap: bins yes{1: aligned access, or the completing beat corrupted}, no_b16{0: rd written;
    reachable only for a split load with a first-beat-only corruption (B16 evidence, owned by the
    expected-fail item TP-DMEM-064; the bin disappears when B16 is fixed)}
  - cp_nmi_latency = ordinary retirements between the corrupted access's record and the NMI entry
    record: bins l0{0}, l1{1: the instruction in ID had a load-use hazard}, l2{2: the instruction in
    ID and the one entering ID in the response cycle both complete (C-7, D21: the pending flag
    registers one cycle after the rvalid, rtl/ibex_controller.sv:402-438)}, l3p{[3:$]: a Zcmp
    sequence in ID, a corruption in debug mode (NMI deferred to dret, TP-DMEM-043) or an NMI
    already pending or being handled (TP-DMEM-042)}
  - cp_nmi_mtval = handler-read mtval vs the access address: bins first_ea{split, first-beat
    corruption: mtval == rvfi_mem_addr}, second_word{split, second-beat corruption: mtval ==
    (rvfi_mem_addr & ~32'h3) + 4}, aligned_ea{aligned access: mtval == rvfi_mem_addr}
  - cp_second_intg_while_pending iff a second corruption lands before the NMI entry: bins
    ignored{1: exactly one NMI entry, mtval == the first address}
  - cp_nmi_in_debug_deferred iff rvfi_ext_debug_mode at the corrupted access: bins yes{1: the NMI
    entry record follows the dret record}
  - cp_split_corrupt_pattern iff split access, sampled at the final rvalid of the pair = which beats
    carried a corruption: bins first_only{first beat only}, second_only{second beat only},
    both{both beats}
- Crosses:
  - cr_class_x_we_x_beat = cp_class x cp_we x cp_beat: bins single_load_first{single,load,first: B16
    evidence, owned by TP-DMEM-064}, double_store_single{double,store,single},
    double_load_second{double,load,second}, single_store_second{single,store,second} (all 12
    combinations are possible)
  - cr_pattern_x_we = cp_split_corrupt_pattern x cp_we: bins first_only_load{first_only,load: rd
    written, B16 evidence, owned by TP-DMEM-064}, first_only_store{first_only,store},
    second_only_load{second_only,load}, second_only_store{second_only,store}, both_load{both,load},
    both_store{both,store} (no impossible combination)
  - cr_buserr_x_class = cp_with_bus_err x cp_class: bins both_single{yes,single}, both_double{yes,
    double}
- Adopted (riscv-dv): none
- TP items: TP-DMEM-039, TP-DMEM-040, TP-DMEM-041, TP-DMEM-042, TP-DMEM-043, TP-DMEM-064

### CG-DMEM-008: gen_cg_dmem_pipe_ctx
- Features: F-DMEM-028, F-DMEM-029, F-DMEM-031, F-DMEM-033, F-DMEM-042, F-DMEM-043, F-DMEM-044,
  F-DMEM-045, F-DMEM-046, F-DMEM-047, F-DMEM-051
- Sample: (a) rvfi_valid of a load/store (Zcmp micro-op records included); (b) a WFI retirement
  whose predecessor is a load/store and whose record follows that access's final rvalid by exactly
  2 cycles (the WFI was in ID while the access was outstanding, TIMING); (c) crash_dump_o at each data grant and at each error response;
  (d) each data grant (data_req_o & data_gnt_i); condition: per coverpoint (iff); anti-vacuity:
  each coverpoint's precondition (a prior store to the same address, a dependent consumer, an
  outstanding access at WFI, a PMP denial, a Zcmp expansion) is derived from the program and the
  agent record, so a hit is not a free tick. "rvfi_rd_addr == 0 on every store record" is
  gen_isa_compare's property, not a bin; loads with no prior overlapping store are the default
  case and are not a bin (Critic S-3b).
- Coverpoints:
  - cp_store_load_distance iff (a) && load with a prior store overlapping its bytes within 8
    retirements = retirements between that store and this load: bins d1{1}, d2{2}, d3_8{[3:8]}
  - cp_overlap iff same = byte overlap between that store and this load: bins full{every loaded
    byte was written by the store}, partial_byte{one byte overlaps}, partial_half{two bytes overlap}
  - cp_dep_stall iff (a) && load = the next retirement reads the load's rd (R = the load's final
    rvalid, load record at R+1): bins yes{1: it does, and its rvfi_valid is at R+3 (two cycles after
    the load's record: response wait plus the load-use hazard, C-9)}, no_consumer{0: the next
    retirement does not read rd; its rvfi_valid is at R+2 (every follower waits for the response)}
  - cp_dep_x0 iff (a) && load with rd == x0 && the next retirement reads x0: bins yes{1: the reader
    retired at R+2 like an independent follower (it waits for the response but has no hazard: one
    cycle earlier than a dependent consumer)}
  - cp_wfi_outstanding_hold iff (b) = cycles from the preceding access's grant to its final rvalid
    R while the WFI waited in ID (WFI record at R+2) with core_busy_o On throughout: bins c1_4{[1:4]},
    c5_15{[5:15]}, c16p{[16:$]}
  - cp_pmp_denied iff (a) && rvfi_trap mcause 5/7 attributed to the PMP model = denied access class
    with no data_req_o for the denied word: bins aligned_load{aligned load denied},
    aligned_store{aligned store denied}, mis_first_load{split load, first word denied, second
    permitted}, mis_first_store{split store, first word denied, second permitted},
    mis_second_load{split load, first permitted, second word denied}, mis_second_store{split store,
    first permitted, second denied}, mis_both_load{split load, both words denied},
    mis_both_store{split store, both words denied}
  - cp_pmp_second_half_issued iff mis_first_load|mis_first_store = the permitted second word's
    request was granted (agent record) although the first was denied: bins yes{1}
  - cp_pmp_second_half_store_landed iff mis_first_store = the second-word store request carried
    data_we_o == 1, the rotated upper bytes and the complementary be, and the agent memory holds
    those bytes after the trap (MEM-13 / gen_bug_log.md S1, Q-DL-7 default: RTL-defined, covered):
    bins landed{1}
  - cp_zcmp_burst iff (a) && the record carries rvfi_ext_expanded_insn_last = data transactions
    produced by one cm.push/cm.pop*, summed over its micro-op record group (first expanded record to
    the _last record; one record per micro-op, C-12): bins n1{1}, n2{2}, n3_6{[3:6]}, n7_13{[7:13]}
  - cp_zcmp_err_pos iff Zcmp record with an injected data_err_i = position of the errored
    transaction in the burst: bins first{1st}, middle{neither 1st nor last}, last{last}
  - cp_rvfi_mask iff (a) && !rvfi_trap (decoded load/store records only: non-store records carry
    rmask 4'b1111 and WB-trap records zero masks, C-12 / B18) = (rvfi_mem_rmask, rvfi_mem_wmask):
    bins r_word{rmask 4'b1111},
    r_half{rmask 4'b0011}, r_byte{rmask 4'b0001}, w_word{wmask 4'b1111}, w_half{wmask 4'b0011},
    w_byte{wmask 4'b0001}
  - cp_rvfi_mask_unshifted iff (a) && rvfi_mem_addr[1:0] != 0 = the mask equals the size mask
    unshifted: bins yes{1}
  - cp_crash_last_data_addr iff (c) = crash_dump_o.last_data_addr in the cycle after a grant (or an
    error response) vs the modelled addr_last (rtl/ibex_load_store_unit.sv:254-266, 478-482, 520,
    540): bins eq_ea_single_first{== the unaligned EA after a single or first-word grant, PMP fake
    grants included}, eq_second_word{== the word-aligned second address after a second-half grant},
    held_until_next_gnt{after an error response the erroring access's address is held until the
    handler's first data grant}, no_update_second_after_err{unchanged across the second-half grant
    that follows a first-half error (the only skipped update)}
  - cp_tag_in_at_gnt iff (d) = data_tag_i driven at the grant while data_tag_o == 0: bins in0{0},
    in1{1}; ignore_bins tag_out_one{data_tag_o == 1}: gen_chk_cheriot_quiet failure (F-DMEM-042)
  - cp_rvfi_load_latency iff (a) && load = cycles from the final data_rvalid_i of the load to its
    rvfi_valid: bins one{1}; ignore_bins other{0, [2:$]}: contradicts the RVFI pipeline
    (rtl/ibex_core.sv:1868, 1890: rvfi_wb_done registered once), F-DMEM-051
  - cp_wb_source iff (a) && rvfi_rd_addr != 0 = write source from the rvfi_insn class: bins
    wb_flop{non-load: ALU/CSR/jump result written the cycle after ID}, lsu_load{load data written
    at data return}
  - cp_load_then_alu_b2b iff (a) && load = the very next cycle carries a non-load retirement with
    rvfi_rd_addr != 0: bins yes{1} (the two write sources on consecutive cycles)
- Crosses:
  - cr_distance_x_overlap = cp_store_load_distance x cp_overlap: bins d1_full{d1,full},
    d1_partial_byte{d1,partial_byte}, d2_partial_half{d2,partial_half}, d3_8_full{d3_8,full} (no
    impossible combination)
  - cr_zcmp_err = cp_zcmp_burst x cp_zcmp_err_pos: bins long_first{n7_13,first},
    long_middle{n7_13,middle}, short_last{n2,last}; ignore_bins n1 x middle|last, n2 x middle:
    bursts of one or two transactions have no middle (or no separate last)
- Adopted (riscv-dv): none
- TP items: TP-DMEM-044, TP-DMEM-046, TP-DMEM-047, TP-DMEM-048, TP-DMEM-049, TP-DMEM-050,
  TP-DMEM-051, TP-DMEM-052, TP-DMEM-053, TP-DMEM-054, TP-DMEM-055, TP-DMEM-061

### CG-DMEM-009: gen_cg_dmem_driver_rules
- Features: F-DMEM-048, F-DMEM-049
- Sample: (a) data_gnt_i; (b) data_rvalid_i; (c) a cycle without data_rvalid_i; (d) a PMP-denied
  access classified by the PMP model (no boundary data_req_o); (e) a data_rvalid_i injected by
  the agent as unsolicited (TP-DMEM-062 only); condition: the event; anti-vacuity: grants and
  responses are agent actions checked by gen_sva_dbus in the same cycle, and the PMP-denied sample
  needs a real denial from the program's PMP configuration. "No X on data_rdata_i with rvalid"
  (driver rule 8, F-DMEM-049) is gen_sva_dbus's TB-error property, not a bin; the driver-rule
  coverage is the grant under each regime (cr_gnt_x_regime).
- Coverpoints:
  - cp_gnt_with_req iff (a) = data_req_o in the grant cycle (cross operand only): bins with_req{1};
    ignore_bins bare_gnt{0}: driver rule 1 (inventory s3); a hit is a gen_sva_dbus TB error
  - cp_gnt_regime iff (a) = knob:dmem_gnt_delay at the grant (cross operand only): values
    same_cycle, short, long, random
  - cp_no_gnt_on_pmp_denied iff (d) = no data_gnt_i in the cycles of the suppressed request: bins
    yes{1}; ignore_bins gnt_seen{0}: the agent granted a suppressed request (TB error, F-DMEM-048)
  - cp_rdata_x_between_rvalid iff (c) = the agent drove X or random data on data_rdata_i: bins
    yes{1}
  - cp_rdata_store_resp iff (b) && store = payload class the agent returned: bins fixed{the agent's
    fixed pattern}, random{random word with valid SECDED}
  - cp_unsolicited_rvalid_case iff (e) (informational, TP-DMEM-062 only) = agent-injected extra
    data_rvalid_i classified by the LSU state: bins no_outstanding_ignored{nothing outstanding: no
    trap, NMI, alert or RF write; RVFI keeps matching}, grant_cycle_consumed{rvalid in the grant
    cycle of a request: the LSU takes it as the response (rtl/ibex_load_store_unit.sv:756-757) and
    the genuine response later mismatches}, bad_secded_alert{corrupted codeword on the unsolicited
    beat: alert_major_bus_o (and NMI) although no access consumed it}
- Crosses:
  - cr_gnt_x_regime = cp_gnt_with_req x cp_gnt_regime: bins req_same{with_req,same_cycle},
    req_short{with_req,short}, req_long{with_req,long}, req_random{with_req,random}
- Adopted (riscv-dv): none
- TP items: TP-DMEM-031, TP-DMEM-058, TP-DMEM-059, TP-DMEM-062

---------------------------------------------------------------------------------------------------

## FE covergroups

### CG-FE-001: gen_cg_fe_vectors
- Features: F-FE-002, F-FE-003, F-FE-004, F-FE-005, F-FE-011, F-FE-019, F-FE-001
- Sample: (a) rvfi_valid of a record whose NEXT record's rvfi_pc_rdata != rvfi_pc_rdata + insn
  length (redirect derived from RVFI, C-1 / C-14; the redirect target is that next rvfi_pc_rdata;
  trap/mret/dret records carry the next sequential address in rvfi_pc_wdata, X-1); (b) the first
  retirement after reset; condition: redirect or first
  instruction; anti-vacuity: sequential instructions never sample; a hit proves a redirect of the
  binned kind reached RVFI and gen_isa_compare checked the target. "First pc == boot_addr_i + 0x80",
  "mtvec reset value == {boot_addr_i[31:8], 8'h01}" (gen_chk_csr_readback) and "no mcause-0 trap
  ever" are checker properties, not bins (Critic S-3b).
- Coverpoints:
  - cp_boot_class iff (b) = boot_addr_i: bins zero{32'h0}, low_ram{[31:28] == 0 && != 0},
    top{32'hFFFF_FF00}, random_aligned{any other value with [7:0] == 0}
  - cp_pc_mux iff (a)|(b) = redirect source: bins jump_jal{JAL}, jump_jalr{JALR},
    branch_taken{branch opcode, rvfi_pc_wdata == pc + imm}, exc_vector{rvfi_trap and the next record
    is not rvfi_intr: next rvfi_pc_rdata == {mtvec[31:8], 8'h00}}, irq_vector{the next record has
    rvfi_intr: next rvfi_pc_rdata == {mtvec[31:8], 1'b0, id[4:0], 2'b00}}, eret_mepc{MRET: next
    rvfi_pc_rdata == mepc}, dret_depc{DRET: next rvfi_pc_rdata == depc}, dbg_halt_addr{next
    rvfi_pc_rdata == DmHaltAddr: debug_req_i or ebreak with rvfi_trap == 0 (S-2)}, dbg_exc_addr{next
    rvfi_pc_rdata == DmExceptionAddr}, fencei_next{FENCE.I, rvfi_pc_wdata == pc + 4 (a jump in ID,
    rtl/ibex_decoder.sv:711-720)}, boot{(b): rvfi_pc_rdata == {boot_addr_i[31:8], 8'h80}}; ignore_bins
    bp{PC_BP}: BranchPredictor=0 (F-FE-019, structural exclusion)
  - cp_irq_vec_id iff irq_vector = id[4:0] of the vector slot: bins sw{3}, timer{7}, ext{11},
    fast_0{16}, fast_1{17}, fast_2{18}, fast_3{19}, fast_4{20}, fast_5{21}, fast_6{22}, fast_7{23},
    fast_8{24}, fast_9{25}, fast_10{26}, fast_11{27}, fast_12{28}, fast_13{29}, fast_14{30},
    nmi{31} (fast_0..fast_14 = 16 + [0:$bits(irq_fast_i)-1])
  - cp_target_bit1 iff (a) = the next record's rvfi_pc_rdata[1] (C-1): bins b0{0}, b1{1}
  - cp_jalr_rs1_bit0 iff (a) && JALR = rvfi_rs1_rdata[0]: bins odd{1}, even{0}
  - cp_debug_trap_slot iff (a) && rvfi_ext_debug_mode && (rvfi_trap || is_ebreak(rvfi_insn)) =
    re-entry slot of a trap taken IN debug mode: bins ebreak_halt{is_ebreak, rvfi_trap == 0 (S-2):
    next rvfi_pc_rdata == DmHaltAddr regardless of dcsr.ebreakm, rtl/ibex_controller.sv:874-882},
    exc_dmexc{non-ebreak exception: next rvfi_pc_rdata == DmExceptionAddr}
- Crosses:
  - cr_mux_x_bit1 = cp_pc_mux x cp_target_bit1: bins jalr_b1{jump_jalr,b1}, branch_b1{branch_taken,
    b1}, eret_b1{eret_mepc,b1}, dret_b1{dret_depc,b1}, jal_b1{jump_jal,b1}, fencei_b1{fencei_next,
    b1}; ignore_bins exc_vector|irq_vector|dbg_halt_addr|dbg_exc_addr|boot x b1: vectors,
    DmHaltAddr/DmExceptionAddr and boot_addr_i + 0x80 are word aligned
  - cr_jalr_odd_x_bit1 = cp_jalr_rs1_bit0 x cp_target_bit1: bins odd_b0{odd,b0}, odd_b1{odd,b1}
    (a jalr with rs1[0] == 1 retired to a target with either bit-1 value: bit 0 dropped, no
    misaligned trap, F-FE-011)
- Adopted (riscv-dv): none
- TP items: TP-FE-001, TP-FE-002, TP-FE-003, TP-FE-004, TP-FE-005, TP-FE-010, TP-FE-011, TP-FE-023,
  TP-IMEM-027, TP-IMEM-028

### CG-FE-002: gen_cg_fe_align
- Features: F-FE-006, F-FE-007, F-FE-008, F-FE-009, F-FE-010
- Sample: rvfi_valid; condition: not a trap; anti-vacuity: the straddle/hit-miss classification
  comes from the imem agent's word records (which words carried this instruction and when they
  arrived) and the RAM-model shadow-tag view (boundary-derived, not a probe), so a straddle bin
  cannot hit unless the instruction really spanned two words.
- Coverpoints:
  - cp_len = instruction length from rvfi_insn[1:0]: bins c16{!= 2'b11}, u32{2'b11}
  - cp_pc_bit1 = rvfi_pc_rdata[1]: bins b0{0}, b1{1}
  - cp_straddle iff u32 = the two halves' words: bins no{pc[1] == 0}, same_line{pc[1] == 1 and
    both words in one IC_LINE_BYTES line}, line_cross{pc[1] == 1 and pc + 2 is in the next line}
  - cp_second_word_wait iff same_line|line_cross = cycles the first half waited for the second
    word's arrival (agent record; 0 when the second word arrived first or hit): bins ready{0},
    w1{1}, w2_3{[2:3]}, w4p{[4:$]}
  - cp_delta = rvfi_pc_wdata - rvfi_pc_rdata: bins plus2{2}, plus4{4}, redirect{any other value:
    branch/jump records only; trap/mret/dret records show plus2/plus4 here (X-1) and their redirect
    is classified in CG-FE-001 from the next record}
  - cp_halves_src iff same_line|line_cross = source of the two halves (bus record present = miss;
    none and the line valid in the shadow-tag view = hit): bins hit_hit{both words hit},
    hit_miss{first word hit, second from the bus}, miss_hit{first from the bus, second hit},
    miss_miss{both from the bus, cache enabled}, bus_bus_disabled{cache disabled: both words from
    the bus, nothing allocated}
  - cp_b1_target_len iff first retirement after a redirect with rvfi_pc_rdata[1] == 1 = length of the
    instruction at the half-word-aligned target: bins u32{2'b11}, c16{!= 2'b11}
- Crosses:
  - cr_straddle_x_wait = cp_straddle x cp_second_word_wait: bins cross_w4p{line_cross,w4p},
    same_w1{same_line,w1}, cross_ready{line_cross,ready}, same_ready{same_line,ready},
    cross_w1{line_cross,w1}; ignore_bins no x ready|w1|w2_3|w4p: a non-straddling instruction has
    no second word
  - cr_len_x_bit1 = cp_len x cp_pc_bit1: bins c16_b1{c16,b1}, u32_b1{u32,b1}, c16_b0{c16,b0},
    u32_b0{u32,b0}
  - cr_straddle_x_src = cp_straddle x cp_halves_src: bins cross_hit_miss{line_cross,hit_miss},
    cross_miss_hit{line_cross,miss_hit}, cross_miss_miss{line_cross,miss_miss}, cross_hit_hit{
    line_cross,hit_hit}, same_hit_hit{same_line,hit_hit}, same_miss_miss{same_line,miss_miss},
    cross_bus_disabled{line_cross,bus_bus_disabled}; ignore_bins same_line x hit_miss|miss_hit: one
    line has one source; ignore_bins no x hit_hit|hit_miss|miss_hit|miss_miss|bus_bus_disabled: no
    second word
- Adopted (riscv-dv): none
- TP items: TP-FE-006, TP-FE-007, TP-FE-008, TP-FE-009, TP-FE-010, TP-IMEM-002, TP-IMEM-013,
  TP-IMEM-033

### CG-FE-003: gen_cg_fe_redirect
- Features: F-FE-013, F-FE-017, F-FE-025, F-FE-012
- Sample: (a) each redirect on RVFI (as CG-FE-001 (a), back-dated to the pc_set cycle: the ID-exit
  cycle of a branch/jump/fence.i record, the FLUSH cycle one later for trap/mret/dret records,
  X-1);
  (b) each retirement of a not-taken branch (branch opcode, rvfi_pc_wdata == pc + len); condition:
  the imem agent classified the traffic since the previous redirect; anti-vacuity: the
  discarded-word count is the number of granted words not consumed by any retirement, computed from
  agent records, so bins > 0 need real speculative traffic. "No instruction from a discarded stream
  retires" is gen_isa_compare's property, not a bin.
- Coverpoints:
  - cp_kind iff (a): bins branch_taken{branch opcode, taken}, jal{JAL}, jalr{JALR}, exc{rvfi_trap,
    next record not rvfi_intr}, irq{next record rvfi_intr}, mret{MRET}, dret{DRET}, fencei{FENCE.I},
    dbg_entry{next fetch == DmHaltAddr: debug_req_i or ebreak with rvfi_trap == 0 (S-2)}
  - cp_discarded_words iff (a) = granted words never executed since the previous redirect
    (address-matched against retirements; a speculative word served from the cache counts as
    consumed): bins n0{0}, n1{1}, n2_3{[2:3]}, n4_6{[4:(NUM_FB-1)*IC_LINE_BEATS]}; ignore_bins
    n7p{[(NUM_FB-1)*IC_LINE_BEATS+1:$]}: linear prefetch holds at most FB_THRESHOLD+1 = NUM_FB-1
    non-stale fill buffers between two redirects (F-FE-017); the NUM_FB*IC_LINE_BEATS bound of
    F-IMEM-008 includes stale beats granted before the previous redirect and is covered by
    CG-IMEM-002.cp_outstanding_before
  - cp_spacing iff (a) = cycles since the previous redirect (pc_set to pc_set): bins s2{2: the
    predicted GEN_MIN_REDIRECT_SPACING, pinned at bring-up (C-16)}, s3{3}, s4_5{[4:5]}, s6p{[6:$]};
    ignore_bins s1{1}: a redirecting instruction stalls ID for at least one
    cycle (pipeline_details.rst: Jump 1-N, Branch taken 1-N with BranchTargetALU=1, opentitan
    configuration) and the target enters ID at the earliest two cycles after the redirect (icache
    hit: IC0 lookup in the redirect cycle, IC1 data the next); a spacing of 1 is a gen_isa_compare /
    redirect-model failure
  - cp_target_req_same_cycle iff (a) = instr_req_o with the target word address in the redirect
    cycle (agent record): bins yes{1}, no_pending_req{0: deferred by an ungranted request; sampled
    only when the target word has a bus record (miss or icache_enable == 0): with a hit the deferred
    request is never issued, rtl/ibex_icache.sv:767-769, C-14}
  - cp_branch_not_taken iff (b) = the fall-through word's status when the branch retired: bins
    fallthrough_buffered{1: granted before the branch retired, or hit}, fallthrough_fetched_after{0:
    requested only after the branch retired}
  - cp_spec_err_discarded iff (a) = an injected instr_err_i on a word discarded by this redirect
    (agent record): bins yes{1}, no{0}
- Crosses:
  - cr_kind_x_discarded = cp_kind x cp_discarded_words: bins branch_n4_6{branch_taken,n4_6},
    exc_n2_3{exc,n2_3}, irq_n1{irq,n1}, fencei_n4_6{fencei,n4_6}, jalr_n0{jalr,n0},
    mret_n1{mret,n1}, dbg_entry_n2_3{dbg_entry,n2_3} (no impossible combination)
  - cr_spacing_x_kind = cp_spacing x cp_kind: bins storm_branch{s2,branch_taken}, storm_jal{s2,jal},
    s2_jalr{s2,jalr}, s3_jalr{s3,jalr}, s3_branch{s3,branch_taken} (no impossible combination after
    the s1 ignore)
- Adopted (riscv-dv): none
- TP items: TP-FE-012, TP-FE-013, TP-FE-014, TP-FE-015, TP-FE-024, TP-IMEM-012, TP-IMEM-018

### CG-FE-004: gen_cg_fe_backpressure
- Features: F-FE-012, F-FE-018, F-FE-024
- Sample: end of each ID stall window: a run of >= 1 cycle without rvfi_valid (back-dated) while the
  imem agent has granted words buffered or in flight and the next word is not itself awaited from
  the bus; condition: window closed; anti-vacuity: the cause is derived from RVFI (the instruction
  in ID and its hazards) and the agent count; a hit proves fetch back-pressure was observed with the
  binned cause. A dummy insertion is a one-cycle window (F-FE-018), so l1 is a required bin.
- Coverpoints:
  - cp_cause = cause of the window: bins ld_hazard{the retirement ending the window reads the rd of
    the preceding load}, ls_wait{a load/store waited for its data response}, mul_div{multi-cycle
    mul/div in ID}, zcmp_expand{Zcmp micro-op expansion}, csr_flush{CSR write / fence.i pipeline
    flush: a csr_flush window is exactly 2 cycles (DECODE(special_req) + one FLUSH cycle,
    rtl/ibex_controller.sv:815-818)}, dummy_gap{one-cycle window with none of the above and no fetch cause: dummy insertion}
  - cp_outstanding_stopped_growing = the agent's outstanding count during the window while the
    agent had free capacity: bins flat{1: did not rise}, grew{0: rose (prefetch still filling)}
  - cp_words_buffered_at_stall = non-stale granted-not-consumed words at the window start: bins
    n0{0}, n1_2{[1:2]}, n3_4{[3:4]}, n5_6{[5:(NUM_FB-1)*IC_LINE_BEATS]}; ignore_bins
    n7p{[(NUM_FB-1)*IC_LINE_BEATS+1:$]}: at most NUM_FB-1 non-stale fill buffers (F-FE-017); stale
    beats are excluded from this count
  - cp_stall_len = window length in cycles: bins l1{1}, l2_3{[2:3]}, l4_15{[4:15]}, l16p{[16:$]}
  - cp_dummy_seen = dummy instruction inserted in the window, probe-gated (P1 dummy_instr_id_o),
    not in manifest: bins yes{1}
- Crosses:
  - cr_cause_x_buffered = cp_cause x cp_words_buffered_at_stall: bins mul_div_full{mul_div,n5_6},
    zcmp_full{zcmp_expand,n5_6}, ls_wait_n3_4{ls_wait,n3_4}, ld_hazard_n1_2{ld_hazard,n1_2} (no
    impossible combination)
- Adopted (riscv-dv): none
- TP items: TP-FE-016, TP-FE-017, TP-FE-018

### CG-FE-005: gen_cg_fe_fault_path
- Features: F-FE-015, F-FE-016, F-FE-020, F-FE-022, F-FE-023, F-IMEM-011 (parent of folded bins
  hosted here)
- Sample: (a) rvfi_valid & rvfi_trap with mcause 1; (b) a retirement without trap of a compressed
  instruction whose pc + 2 is PMP-denied for the executing privilege (PMP model); (c) every
  sequential retirement (rvfi_pc_wdata == rvfi_pc_rdata + len); (d) every retirement with
  rvfi_ext_debug_mode; condition: per coverpoint (iff); anti-vacuity: (a) samples only on
  instruction access faults with the source attributed from the agent record or the PMP model;
  (b)-(d) are qualified by the PMP configuration, the sequential window and debug mode. "No side
  effect of an errored word" (gen_isa_compare) and "alert_major_internal_o never high" (gen_chk_alerts)
  are checker properties; their coverage is the stimulus class over which the check ran.
- Coverpoints:
  - cp_source iff (a): bins bus{bus error, PMP permits}, intg{integrity error, PMP permits}, pmp{PMP
    denial of pc, beat clean}, pmp_plus2{PMP denial of pc + 2 only}, bus_and_pmp{bus error and PMP
    denial on the same word}
  - cp_next_fetch iff (a) = the next record's rvfi_pc_rdata (C-1; not an ibus observation, C-14):
    bins exc_vector{{mtvec[31:8], 8'h00}}, dm_exception_addr{DmExceptionAddr}
  - cp_in_debug iff (a) = rvfi_ext_debug_mode: bins yes{1}, no{0}
  - cp_len iff (a) = faulting instruction length: bins c16{rvfi_insn[1:0] != 2'b11}, u32{2'b11}
  - cp_errored_payload iff (a) && source in {bus, intg, bus_and_pmp} = decode class of the payload
    the agent delivered on the errored word: bins store{sb/sh/sw}, csr_write{csrrw/csrrs/csrrc with
    a write effect}, jump{jal/jalr/taken branch}, rd_write{ALU op with rd != x0}, other{anything
    else}; the absence of data_req_o, rd write and redirect is gen_isa_compare's check
  - cp_c16_plus2_ignored iff (b): bins yes{1: the compressed instruction retired without trap}
  - cp_pc_incr_class iff (c) = class of the sequential retirement over which the PC-increment check
    ran with alert_major_internal_o low (gen_chk_alerts, F-FE-020): bins plus2{len 2},
    plus4{len 4, pc[1] == 0}, plus4_straddle{len 4, pc[1] == 1}, first_after_redirect{the first
    sequential retirement after a redirect}
  - cp_debug_fetch iff (d) = source of the debug-mode retirement's word: bins warm_line_bypassed{1:
    the line was valid in the shadow-tag view before entry and the word still came from the bus},
    cold_line{0: the line was not cached}
- Crosses:
  - cr_source_x_debug = cp_source x cp_in_debug: bins bus_dbg{bus,yes}, pmp_dbg{pmp,yes},
    intg_nodbg{intg,no}, bus_nodbg{bus,no}, intg_dbg{intg,yes} (pmp x yes needs a locked region
    denying M-mode execute; no impossible combination)
  - cr_source_x_len = cp_source x cp_len: bins pmp_plus2_u32{pmp_plus2,u32}, bus_c16{bus,c16},
    bus_u32{bus,u32}, intg_c16{intg,c16}; ignore_bins pmp_plus2 x c16: the +2 check is skipped for
    compressed instructions
- Adopted (riscv-dv): none
- TP items: TP-FE-019, TP-FE-020, TP-FE-021, TP-FE-022, TP-FE-023, TP-FE-025, TP-IMEM-011,
  TP-IMEM-016, TP-IMEM-030

### CG-FE-006: gen_cg_fe_wake_wrap
- Features: F-FE-014, F-FE-021, F-FE-003
- Sample: (a) the first rvfi_valid after a WFI retirement; (b) rvfi_valid with rvfi_pc_rdata >=
  32'hFFFF_FFF8; condition: per coverpoint (iff); anti-vacuity: WFI and top-of-memory execution only
  happen when the program does them; a hit proves the wake source / wrap case occurred.
- Coverpoints:
  - cp_wake_src iff (a) = what ended the WFI: bins irq{an interrupt line enabled in mie rose},
    nmi{irq_nm_i}, debug_req{debug_req_i}, step_mode{dcsr.step = 1 outside debug mode: no sleep,
    FLUSH -> DBG_TAKEN_IF, the next retirement is the debug ROM at DmHaltAddr with dpc == WFI + len
    (C-5)}, wfi_in_debug{WFI executed in debug mode: SLEEP exits at once on debug_mode_q, wfi = nop}
  - cp_resume_pc iff (a) = first retirement after the WFI: bins wfi_next_buffered{rvfi_pc_rdata ==
    WFI pc + len}, handler{rvfi_pc_rdata == an interrupt / NMI vector or DmHaltAddr}
  - cp_refetch_after_wake iff (a) && icache_enable == 0 (pinned by the owning item so a re-fetch is
    visible on the bus) = the word after WFI was requested again on the bus: bins no{0}, yes{1}
  - cp_wrap_case iff (b): bins c16_at_fffe{c16 at 32'hFFFF_FFFE}, u32_at_fffc{u32 at 32'hFFFF_FFFC},
    u32_at_fffe_straddle_zero{u32 at 32'hFFFF_FFFE, second half at 32'h0}
  - cp_next_after_wrap iff (b) && the instruction is the last before the wrap: bins zero{rvfi_pc_wdata
    == 32'h0: c16 at 32'hFFFF_FFFE or u32 at 32'hFFFF_FFFC}, two{rvfi_pc_wdata == 32'h2: u32 at
    32'hFFFF_FFFE, 31-bit adder 0x7FFF_FFFF + 2, rtl/ibex_icache.sv:1139-1147}
  - cp_fetch_seq_wrap iff (b): bins yes{1: the agent record shows instr_addr_o 32'hFFFF_FFFC
    followed by 32'h0}
- Crosses:
  - cr_wake_x_resume = cp_wake_src x cp_resume_pc: bins irq_handler{irq,handler},
    dbg_handler{debug_req,handler}, step_dbg{step_mode,handler: DmHaltAddr with dpc == WFI + len},
    indebug_next{wfi_in_debug,wfi_next_buffered}, nmi_handler{nmi,handler},
    irq_next{irq,wfi_next_buffered: mstatus.mie == 0, the pending line wakes but is not taken};
    ignore_bins nmi x wfi_next_buffered (an NMI is always taken), debug_req x wfi_next_buffered
    (debug entry always follows), step_mode x wfi_next_buffered (a stepped WFI enters debug before
    the next instruction retires, C-5), wfi_in_debug x handler (a WFI in debug mode is a nop)
  - cr_wrap_x_next = cp_wrap_case x cp_next_after_wrap: bins c16_zero{c16_at_fffe,zero},
    u32_fffc_zero{u32_at_fffc,zero}, straddle_two{u32_at_fffe_straddle_zero,two}; ignore_bins
    c16_at_fffe|u32_at_fffc x two, u32_at_fffe_straddle_zero x zero: the 31-bit adder result
- Adopted (riscv-dv): none
- TP items: TP-FE-003, TP-FE-026, TP-FE-027, TP-FE-028, TP-IMEM-022

---------------------------------------------------------------------------------------------------

## IC covergroups

### CG-IC-001: gen_cg_ic_ram_ports
- Features: F-IC-001, F-IC-002, F-IC-003, F-IC-004, F-IC-005, F-IC-006, F-IC-007, F-IC-028,
  F-IC-045, F-IC-046
- Sample: (a) any cycle with |ic_tag_req_o; (b) any cycle with |ic_data_req_o (gen_icache_ram_model
  port monitor); condition: request on that port; anti-vacuity: idle cycles never sample;
  write-side bins require the model to decode the codeword (after undoing the address-derived
  tweak), so a tweak bin is a real decode, not a tick. "Every write codeword decodes clean" and
  "never a read and a write on one port in one cycle" (F-IC-045) are gen_chk_icache's properties;
  their coverage is the tweak partition and the deferred-write contention below.
- Coverpoints:
  - cp_tag_op iff (a) = classified tag-port operation: bins lookup_both{ic_tag_req_o == all ways,
    !ic_tag_write_o}, inval_write_both{write, all ways, valid bit 0, during a sweep},
    fill_write_way0{write, req one-hot way 0, valid 1}, fill_write_way1{write, way 1, valid 1},
    ecc_write_way0{write, valid 0, way 0 only, outside a sweep}, ecc_write_way1{write, valid 0, way 1
    only, outside a sweep}, ecc_write_both{write, valid 0, both ways, outside a sweep}
  - cp_data_op iff (b): bins lookup_both{read, all ways}, fill_write_way0{write, one-hot way 0},
    fill_write_way1{write, one-hot way 1}, inval_zero_write_both{write, both ways, the ECC-encoded
    zero line, during a sweep}
  - cp_cache_en = cpuctrlsts.icache_enable tracked from RVFI csr writes and rvfi_ext_debug_mode: bins
    on{1}, off{0}
  - cp_index = ic_tag_addr_o: bins idx0{0}, idx_mid{[1:IC_NUM_LINES-2]}, idx_last{IC_NUM_LINES-1}
  - cp_tag_tweak_effective iff tag write = the raw ic_tag_wdata_o does not decode clean but decodes
    clean after undoing the index-derived tweak (the IC_INDEX_W-bit index at bits [7:0] and [21:14]
    of the 28-bit codeword, ECC bits untouched, rtl/ibex_icache.sv:389-396): bins infected{1},
    transparent{0: index 0, or an inval / ECC-correction write (tweak 0): raw and untweaked both
    decode clean}
  - cp_data_tweak_effective iff data write = both 39-bit beats of ic_data_wdata_o decode clean only
    after undoing the address-derived tweak (the line-aligned address {addr[31:3], 3'b0} on the 32
    data bits of each beat, bits [31:0] and [70:39], rtl/ibex_icache.sv:329-347): bins infected{1},
    transparent{0: zero tweak: line address 0, or an inval / ECC-correction write}
  - cp_tag_valid_bit iff tag write = valid bit of the written tag: bins valid{1}, invalid{0}
  - cp_port_contention iff a fill write became eligible (both beats closed, allocation pending) in a
    cycle whose port was used by a lookup read = cycles the write was deferred: bins deferred_1{1},
    deferred_2p{[2:$]}
  - cp_read_when_disabled iff lookup read = cp_cache_en at the read (never during INVAL_CACHE:
    every sweep cycle is a write at the inval index, rtl/ibex_icache.sv:269-283, 1244): bins
    seen{off}, on{on}
  - cp_rdata_used_next_cycle iff lookup read = the DUT acted on the model's read data one cycle
    later (hit with no bus record, or an ECC alert): bins yes{1}
- Crosses:
  - cr_tagop_x_en = cp_tag_op x cp_cache_en: bins lookup_off{lookup_both,off}, lookup_on{
    lookup_both,on}, fill0_on{fill_write_way0,on}, fill1_on{fill_write_way1,on}, inval_on{
    inval_write_both,on}, inval_off{inval_write_both,off}, ecc_both_on{ecc_write_both,on},
    ecc0_on{ecc_write_way0,on}, ecc1_on{ecc_write_way1,on}; ignore_bins fill_write_way0|
    fill_write_way1 x off: no allocation while disabled, fills in flight at a disable are dropped
    (F-IC-027); ignore_bins ecc_write_way0|ecc_write_way1|ecc_write_both x off: ECC checks act only
    on enabled lookups (F-IC-035)
  - cr_index_x_tagop = cp_index x cp_tag_op: bins idx0_inval{idx0,inval_write_both},
    idxlast_inval{idx_last,inval_write_both}, idxlast_fill{idx_last,fill_write_way1},
    idx0_fill{idx0,fill_write_way0} (no impossible combination)
- Adopted (riscv-dv): none
- TP items: TP-IC-001, TP-IC-002, TP-IC-003, TP-IC-004, TP-IC-005, TP-IC-006, TP-IC-011, TP-IC-017,
  TP-IC-018, TP-IC-030, TP-IC-035, TP-IC-036, TP-IC-045, TP-IC-046

### CG-IC-002: gen_cg_ic_inval_key
- Features: F-IC-008, F-IC-009, F-IC-010, F-IC-011, F-IC-022, F-IC-023, F-IC-024, F-IC-025,
  F-IC-026, F-IC-047
- Sample: (a) ic_scr_key_req_o pulse; (b) end of an invalidation sweep (tag write to index
  IC_NUM_LINES-1 with valid 0 after a sweep start) or its abandonment; (c) each fence.i on RVFI;
  (d) an edge of ic_scr_key_valid_i; (e) each csrr cpuctrlsts on RVFI; (f) reset release;
  condition: per coverpoint (iff); anti-vacuity: sweeps and key pulses are DUT reactions to
  reset/fence.i; a hit proves the FSM path the checker followed. "One pulse per request, never two
  consecutive", "no second pulse for a fence.i in AWAIT_SCRAMBLE_KEY" (F-IC-024) and "no tag write
  while the key is invalid with a request pending" are gen_chk_icache's properties, not bins.
- Coverpoints:
  - cp_trigger iff (b) = sweep trigger: bins reset{sweep started at reset}, fencei_from_idle{fence.i
    in INVAL_IDLE}, fencei_restart{fence.i during a running sweep}
  - cp_sweep iff (b) = sweep completion: bins complete_all{IC_NUM_LINES writes, indices 0 to
    IC_NUM_LINES-1 in order}, restarted_partial{k < IC_NUM_LINES writes, then a restart from 0}
  - cp_key_req_at_reset iff (f): bins issued{pulse in the first cycle after reset release},
    skipped_valid_high{no pulse: ic_scr_key_valid_i was 1}
  - cp_key_delay iff (a) = cycles ic_scr_key_valid_i stays low after the pulse: bins k0_1{[0:1]},
    k2_15{[2:15]}, k16_255{[16:IC_NUM_LINES-1]}, k256p{[IC_NUM_LINES:$]}, never_in_test{valid never
    rose before test end}
  - cp_key_knob iff (a) = knob:scr_key_delay (cross operand only): values immediate{low 1 cycle},
    delayed{low 2..200}, withheld_then_valid{low 201..2000} (fcov_xcut.md CG-REG-005)
  - cp_fencei_state iff (c) = invalidation FSM state at the fence.i (derived from the key/sweep
    timeline): bins idle{INVAL_IDLE}, await_key_ignored{AWAIT_SCRAMBLE_KEY: no new pulse},
    inval_cache_restart{INVAL_CACHE: sweep restarted}
  - cp_retire_during_sweep iff (b) = retirements while the sweep ran (all with bus records): bins
    r1_19{[1:19]}, r20p{[20:$]}
  - cp_fill_write_after_unsolicited_drop iff (d) fall with no request pending (INVAL_IDLE): bins
    yes{1: at least one fill tag write while the key was marked invalid} (F-IC-047: the FSM reads
    the key only in OUT_OF_RESET and AWAIT_SCRAMBLE_KEY, rtl/ibex_icache.sv:1225, 1235)
  - cp_reset_to_idle_cycles iff (b) && trigger == reset && the key was valid at reset = cycle index
    (reset release = cycle 0 = OUT_OF_RESET, cycle 1 = AWAIT_SCRAMBLE_KEY, inval writes in cycles
    2..IC_NUM_LINES+1) of the first INVAL_IDLE cycle: bins min{IC_NUM_LINES+2},
    longer{[IC_NUM_LINES+3:$]}; ignore_bins short{[0:IC_NUM_LINES+1]}: contradicts
    rtl/ibex_icache.sv:1221-1255 (MEM-23: 1 + 1 + IC_NUM_LINES cycles, F-IC-022)
  - cp_first_alloc_after_sweep iff (b) && complete_all = cycles from the last inval write to the
    first fill tag write: bins c5_8{[5:8]}, c9p{[9:$]}; ignore_bins c0_4{[0:4]}: the first
    allocating lookup needs INVAL_IDLE (inval_block_cache clears only there, rtl/ibex_icache.sv:1218,
    1265), then IC1 miss, two grants and rvalids and a fill_ram_req cycle without a lookup (TP-IC-011)
  - cp_fill_inflight_at_inval iff (c) = fill buffers open at the fence.i (none of them allocated
    afterwards): bins n0{0}, n1_2{[1:2]}, n3_4{[3:NUM_FB]}
  - cp_cpuctrlsts_bit8 iff (e) = rvfi_rd_wdata[8] vs the registered ic_scr_key_valid_i: bins
    match_1{both 1}, match_0{both 0}; ignore_bins mismatch{differ}: gen_chk_csr_readback failure
  - cp_valid_dropped_unsolicited iff (d) fall: bins yes{1: no request was pending}
  - cp_new_code_after_fencei iff (c) preceded by a store to a warm line: bins yes{1: RVFI executes
    the new word after the fence.i}
- Crosses:
  - cr_trigger_x_delay = cp_trigger x cp_key_delay: bins reset_k256p{reset,k256p},
    fencei_k0_1{fencei_from_idle,k0_1}, restart_k16_255{fencei_restart,k16_255},
    fencei_never{fencei_from_idle,never_in_test}, reset_k0_1{reset,k0_1}, fencei_k2_15{
    fencei_from_idle,k2_15} (no impossible combination)
  - cr_state_x_inflight = cp_fencei_state x cp_fill_inflight_at_inval: bins idle_n3_4{idle,n3_4},
    restart_n1_2{inval_cache_restart,n1_2}, await_n1_2{await_key_ignored,n1_2} (no impossible
    combination)
  - cr_delay_x_knob = cp_key_delay x cp_key_knob: bins k0_1_immediate{k0_1,immediate},
    k2_15_delayed{k2_15,delayed}, k16_255_delayed{k16_255,delayed}, k256p_withheld{k256p,
    withheld_then_valid}, never_withheld{never_in_test,withheld_then_valid}; ignore_bins immediate x
    k2_15|k16_255|k256p|never_in_test, delayed x k0_1|k256p|never_in_test, withheld_then_valid x
    k0_1|k2_15: the knob value forbids that delay
- Adopted (riscv-dv): none
- TP items: TP-IC-007, TP-IC-008, TP-IC-009, TP-IC-010, TP-IC-011, TP-IC-012, TP-IC-013, TP-IC-014,
  TP-IC-015, TP-IC-016, TP-IC-047

### CG-IC-003: gen_cg_ic_lookup
- Features: F-IC-014, F-IC-015, F-IC-016, F-IC-017, F-IC-018, F-IC-021, F-IC-039, F-IC-042,
  F-IC-013
- Sample: each lookup result as reconstructed by gen_icache_ram_model's shadow-tag view
  (boundary-derived: the model mirrors every tag write it receives on ic_tag_*, so the hit/miss and
  way-validity outcome of a lookup index follows from the mirror and the bus records; no probe, P2
  was rejected); condition: a lookup read occurred; anti-vacuity: the result class is a tag
  comparison whose consequence (bus request or none, allocation or none) gen_chk_icache verified.
- Coverpoints:
  - cp_result = lookup outcome: bins hit_way0{shadow tag of way 0 valid and equal, no bus record for
    the word}, hit_way1{way 1 valid and equal, no bus record}, miss_alloc_way0{no way matches, a
    fill write to way 0 follows}, miss_alloc_way1{no way matches, fill write to way 1},
    miss_no_alloc_disabled{cache disabled: bus fetch, no fill write},
    miss_no_alloc_invalidating{sweep running: bus fetch, no fill write}, miss_ecc_forced{a tag or
    data ECC error forced a miss (alert_minor_o)}
  - cp_index_fill = validity of the two ways at the index before the lookup (shadow view): bins
    none_valid{0 valid}, one_valid{1 valid}, both_valid{2 valid}
  - cp_victim iff miss_alloc_* && both_valid = replacement choice: bins rr_way0{0}, rr_way1{1}
  - cp_all_lines_valid iff miss_alloc_* = every index has both ways valid in the shadow view: bins
    yes{1}
  - cp_hit_bus_traffic iff hit_way0|hit_way1 = bus request attributable to the hit: bins none{0},
    spec_branch_only{1: the speculative branch-target request}
  - cp_hit_cadence iff hit_way0|hit_way1 = consecutive hit retirements at one instruction per cycle
    ending here: bins run2_3{[2:3]}, run4p{[4:$]}
  - cp_miss_forward_latency iff miss_alloc_*|miss_no_alloc_* = cycles from instr_rvalid_i of the
    demanded word to its rvfi_valid: bins l3{3: IF output in R, ID R+1, WB R+2, record R+3},
    l4p{[4:$]: a u32 whose second half is the next beat, or a stalled pipeline}; ignore_bins
    l1_2{[1:2]}: contradicts the pipeline (rtl/ibex_icache.sv:796-798, 1062, 1068;
    rtl/ibex_core.sv:1864-1870)
  - cp_priv = rvfi_mode at the lookup: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_two_ways_same_tag = the shadow view holds the same tag valid in both ways at this index
    (needs both ways valid before the two lookups and an odd lookup count between them, TP-IC-025):
    bins yes{1}
- Crosses:
  - cr_result_x_fill = cp_result x cp_index_fill: bins alloc0_none{miss_alloc_way0,none_valid},
    alloc1_one{miss_alloc_way1,one_valid}, alloc0_one{miss_alloc_way0,one_valid}, evict_both{
    miss_alloc_way0|miss_alloc_way1 x both_valid}, hit1_both{hit_way1,both_valid}, hit0_one{
    hit_way0,one_valid}; ignore_bins hit_way0|hit_way1 x none_valid: no valid way to hit;
    ignore_bins miss_alloc_way1 x none_valid: the lowest invalid way is chosen first (F-IC-017)
  - cr_result_x_priv = cp_result x cp_priv: bins hit0_u{hit_way0,u}, hit1_u{hit_way1,u},
    alloc_u{miss_alloc_way0|miss_alloc_way1 x u}
- Adopted (riscv-dv): none
- TP items: TP-IC-011, TP-IC-017, TP-IC-018, TP-IC-019, TP-IC-020, TP-IC-021, TP-IC-022, TP-IC-025,
  TP-IC-026, TP-IC-034, TP-IC-035, TP-IC-037, TP-IC-038, TP-IMEM-019

### CG-IC-004: gen_cg_ic_fill
- Features: F-IC-019, F-IC-020, F-IC-021, F-IC-036, F-IC-037, F-IC-043, F-IMEM-015, F-IMEM-018
- Sample: fill-buffer lifecycle closure as seen by the imem agent (a line's beats granted and
  answered) plus the RAM model's fill write or its absence; condition: closure; anti-vacuity: only
  lines fetched over the bus sample; a hit proves a fill with the binned entry/delay/redirect shape
  and the allocation decision gen_chk_icache checked. Event-occurrence bins (spec_*, same_line_*,
  pmp_*) are qualified by the stimulus that produces them (a hitting branch target, a second buffer
  for a line, a PMP denial).
- Coverpoints:
  - cp_entry_beat = first requested word of the line: bins w0{addr[2] == 0}, w1_wrap{addr[2] == 1}
  - cp_beat_delays = rvalid latency class per beat (slow = >= 4 cycles after grant): bins
    both_fast{both < 4}, first_slow{first >= 4, second < 4}, second_slow{first < 4, second >= 4},
    both_slow{both >= 4}
  - cp_redirect_during_fill = redirect relative to the fill's grants: bins none{no redirect before
    the second rvalid}, after_beat1_gnt{redirect after the first grant, before the second},
    after_beat2_gnt{redirect after both grants}, before_any_gnt_cancelled{redirect before any grant,
    non-caching line (icache_enable == 0 or sweep active): no bus traffic for the line},
    before_any_gnt_fetched{redirect before any grant, caching line: both beats fetched and the line
    written (never cancelled: fill_ext_done_d cancels only when ~fill_cache_q,
    rtl/ibex_icache.sv:767-775)}
  - cp_written_after_redirect iff after_beat1_gnt|after_beat2_gnt|before_any_gnt_fetched = the stale
    allocating fill still wrote the line: bins yes{1}, not_alloc{0: disabled, invalidating or errored}
  - cp_busy_buffers iff a fill write (allocation) = fill buffers busy at the allocation (agent count
    of open lines): bins b1{1}, b2{2}, b3{NUM_FB-1}, b4{NUM_FB}
  - cp_saturation_stall iff b4 = no new lookup request while NUM_FB lines were open: bins yes{1}
  - cp_err_line iff a beat carried an injected error = the line was written: bins not_cached{0};
    ignore_bins cached{1}: gen_chk_icache failure (F-IMEM-015)
  - cp_pmp_denied_line iff the line was PMP-denied for the executing privilege = fill write followed:
    bins cached{1} (RTL-defined, D9: no instr_pmp_err port)
  - cp_pmp_line_later_hit iff a later lookup of that line under a permitting privilege/PMP config:
    bins yes{1: no bus record}
  - cp_spec_branch_req iff a branch redirect whose target hit = a bus request for the target word:
    bins yes{1}, suppressed_other_req_pending{0: another request was pending}
  - cp_spec_resp_discarded iff cp_spec_branch_req == yes: bins yes{1: the response was consumed and
    its data unused}
  - cp_spec_err_ignored iff an injected error on that speculative beat: bins yes{1: no trap}
  - cp_same_line_two_ways iff a second buffer for a line already being filled was allocated: bins
    yes{1: two fill writes for one (index, tag) in different ways (both ways valid before, odd
    lookup count between, TP-IC-025)}, same_way_overwrite{0: both fills landed in the same lowest
    invalid way (one copy)}
- Crosses:
  - cr_entry_x_delays = cp_entry_beat x cp_beat_delays: bins w1_both_slow{w1_wrap,both_slow},
    w0_second_slow{w0,second_slow}, w1_first_slow{w1_wrap,first_slow}, w0_both_fast{w0,both_fast}
    (no impossible combination)
  - cr_redirect_x_written = cp_redirect_during_fill x cp_written_after_redirect: bins
    after1_written{after_beat1_gnt,yes}, after2_written{after_beat2_gnt,yes},
    after1_not_alloc{after_beat1_gnt,not_alloc}, before_fetched_written{before_any_gnt_fetched,yes};
    ignore_bins none|before_any_gnt_cancelled x yes|not_alloc, before_any_gnt_fetched x not_alloc: a
    fill without redirect is not "written after redirect", a cancelled line has no fill, and a caching
    line with no grant yet is always written
  - cr_busy_x_delays = cp_busy_buffers x cp_beat_delays: bins b4_both_slow{b4,both_slow},
    b3_first_slow{b3,first_slow}, b1_both_fast{b1,both_fast} (no impossible combination)
- Adopted (riscv-dv): none
- TP items: TP-IC-023, TP-IC-024, TP-IC-025, TP-IC-026, TP-IC-027, TP-IC-028, TP-IC-039, TP-IC-040,
  TP-IC-041, TP-IC-051, TP-IC-052, TP-IMEM-015, TP-IMEM-019, TP-IMEM-020

### CG-IC-005: gen_cg_ic_enable
- Features: F-IC-012, F-IC-013, F-IC-027, F-IC-040, F-IC-041, F-FE-022, F-IC-039, F-IC-048
- Sample: (a) each cpuctrlsts write on RVFI; (b) each debug entry (next fetch == DmHaltAddr) and
  exit (dret); (c) each cpuctrlsts access on RVFI (M or U mode); (d) the first lookup after (a);
  condition: per coverpoint (iff); anti-vacuity: enable transitions come only from the program; the
  in-flight count is the agent's; a hit proves the toggle landed on live traffic. "Reset value 0"
  (gen_chk_csr_readback), "every retirement while off has a bus record", "no fill write in debug
  mode" (F-IC-040) and "no tag write other than sweep/ECC writes while off" (F-IC-048) are
  gen_chk_icache / gen_chk_csr_readback properties, not bins.
- Coverpoints:
  - cp_transition iff (a) = (old bit 0, new bit 0): bins off_to_on{0 -> 1}, on_to_off{1 -> 0},
    on_to_on{1 -> 1}, off_to_off{0 -> 0}
  - cp_fills_inflight iff (a) = open lines at the write: bins n0{0}, n1_2{[1:2]}, n3_4{[3:NUM_FB]}
  - cp_inflight_alloc_dropped iff on_to_off && n >= 1: bins yes{1: no line open at the write was
    written from the cycle after the enable drop; at most one fill write in the drop cycle itself is
    legal (fill_cache_q clears one cycle later, rtl/ibex_icache.sv:744-746, 815-819)}
  - cp_no_backfill iff off_to_on && n >= 1: bins yes{1: no non-caching line open at the write was
    written afterwards}
  - cp_debug iff (b) = debug-mode effect: bins entry_with_en_forced_off{entry with icache_enable
    == 1: lookups pass through, all retirements have bus records}, exit_hits_resume{dret with
    icache_enable == 1: the first warm lookup after the depc line hits (the depc line itself is
    fetched pass-through in the dret cycle, TP-FE-022)}, entry_with_en_off{entry with icache_enable == 0}
  - cp_priv_access iff (c) = access privilege and outcome: bins m_ok{M-mode access retired},
    u_illegal_insn{U-mode access trapped, mcause 2}
  - cp_old_lines_hit_after_reenable iff off_to_on: bins yes{1: a line cached before the disable
    hit after the enable}
  - cp_effect_latency iff (d) = lookups after the csrw retirement until the new state is
    reflected: bins next_lookup{0: the first lookup already reflects it}; ignore_bins later{[1:$]}:
    gen_chk_icache failure (F-IC-041)
  - cp_off_window iff off_to_on = retirements between the preceding on_to_off and this write: bins
    short{[1:20]}, long{[21:$]}
- Crosses:
  - cr_trans_x_inflight = cp_transition x cp_fills_inflight: bins off_n3_4{on_to_off,n3_4},
    on_n1_2{off_to_on,n1_2}, off_n0{on_to_off,n0}, on_n0{off_to_on,n0} (no impossible combination)
  - cr_off_window_x_hit = cp_off_window x cp_old_lines_hit_after_reenable: bins short_hit{short,
    yes}, long_hit{long,yes} (F-IC-048: old lines hit after any disabled window length)
- Adopted (riscv-dv): none
- TP items: TP-FE-022, TP-IC-029, TP-IC-030, TP-IC-031, TP-IC-032, TP-IC-033, TP-IC-048, TP-IC-057,
  TP-IMEM-038

### CG-IC-006: gen_cg_ic_ecc
- Features: F-IC-030, F-IC-031, F-IC-032, F-IC-033, F-IC-034, F-IC-035, F-IC-042
- Sample: each injected RAM read corruption (gen_icache_ram_model record), or each lookup that read
  a never-written (uninitialised) data RAM line, closed by the DUT's reaction (alert_minor_o pulse
  and the following tag write) or by its absence; condition: injected or uninitialised read;
  anti-vacuity: only injections and uninitialised reads sample; a hit proves gen_chk_icache /
  gen_chk_alerts verified alert, invalidation and refetch. The quiet-major/NMI bin is qualified per
  injection (the stimulus that could have raised them).
- Coverpoints:
  - cp_ram iff injected: bins tag{ic_tag_rdata_i corrupted}, data{ic_data_rdata_i corrupted}
  - cp_bits iff injected = flipped bits: bins single{1}, double{2}
  - cp_way iff injected: bins way0{0}, way1{1}
  - cp_beat iff data = corrupted 39-bit beat: bins beat0{0}, beat1{1}
  - cp_alert_pulses iff injected on a valid hit lookup = alert_minor_o pulses for this injection:
    bins one{1}; ignore_bins zero{0}, many{[2:$]}: gen_chk_alerts failure
  - cp_inval_ways iff alerted = ways written invalid in the next cycle: bins all_ways{tag error},
    hit_way_only{data error}
  - cp_refetch iff alerted: bins yes{1: the lookup was served from the bus afterwards}
  - cp_major_nmi_quiet iff injected: bins yes{1: alert_major_internal_o, alert_major_bus_o and
    rvfi_ext_nmi_int stayed low over the injection window}
  - cp_lookups_blocked_next iff alerted: bins yes{1: no lookup read on any port in the ECC write
    cycle; a data-port WRITE of ECC(0) in that cycle is legal, rtl/ibex_icache.sv:280, 1000-1011}
  - cp_no_alert_case iff the corruption or read must not alert: bins unused_way_data{data of the
    non-hitting way}, disabled_cache{icache_enable == 0}, during_invalidation{sweep running},
    uninitialised_data_ram{never-written data line read, no injection}
  - cp_multiway_mismatch (informational, TP-IC-038 only) iff both ways valid with the same tag and
    differing data: bins alert_or_wrong{1: alert_minor_o or a wrong rvfi_insn}
  - cp_knob iff injected = knob:icache_ecc_err_rate (cross operand only): values none, rare,
    frequent
- Crosses:
  - cr_ram_x_bits_x_way = cp_ram x cp_bits x cp_way, 8 bins: tag_single_way0{tag,single,way0},
    tag_single_way1{tag,single,way1}, tag_double_way0{tag,double,way0}, tag_double_way1{tag,double,
    way1}, data_single_way0{data,single,way0}, data_single_way1{data,single,way1},
    data_double_way0{data,double,way0}, data_double_way1{data,double,way1}
  - cr_data_x_beat = cp_ram x cp_beat: bins data_beat0{data,beat0}, data_beat1{data,beat1};
    ignore_bins tag x beat0|beat1: the tag has no beats
  - cr_ram_x_inval = cp_ram x cp_inval_ways: bins tag_all{tag,all_ways}, data_hit{data,
    hit_way_only}; ignore_bins tag x hit_way_only, data x all_ways: contradict F-IC-030/031
  - cr_bits_x_rate = cp_bits x cp_knob: bins single_rare{single,rare}, double_rare{double,rare},
    single_frequent{single,frequent}, double_frequent{double,frequent}; ignore_bins single|double x
    none: no injection under the none regime
- Adopted (riscv-dv): none
- TP items: TP-IC-035, TP-IC-036, TP-IC-037, TP-IC-038, TP-IC-042, TP-IC-043, TP-IC-044, TP-IC-049,
  TP-IC-056

### CG-IC-007: gen_cg_ic_busy_throttle
- Features: F-IC-029, F-IC-038, F-IC-043, F-IC-044
- Sample: (a) core_busy_o transitions; (b) each sequential grant (not a redirect target); (c) each
  retirement (output-hold measurement); condition: per coverpoint (iff); anti-vacuity: busy reasons
  are derived from the sweep timeline and the agent's outstanding count; the lead and hold are
  agent-record measurements; a hit proves core_busy_o was held by the binned reason or the binned
  lead/hold occurred. "rvfi_insn equals the word delivered for its pc" (F-IC-044) is
  gen_isa_compare's property; its coverage is the hold-time partition below.
- Coverpoints:
  - cp_busy_reason iff (a) core_busy_o still On after the pipeline drained on a WFI: bins
    inval_sweep{sweep running}, fill_outstanding{fetch beats outstanding}, key_await{key request
    pending}
  - cp_wfi_after_fencei iff a WFI retired with a sweep running: bins yes{1: core_busy_o Off only
    after the sweep end}
  - cp_lead_lines iff (b) = (instr_addr_o line - line of the last retired rvfi_pc_rdata) at the
    grant: bins l0{0}, l1{1}, l2{2}, l3{NUM_FB-1}, l4_wb_stall{NUM_FB, sampled iff a data access is
    outstanding at the grant: the WB-stalled load/store delays the retirement so the RVFI pc lags
    the ID-consumed word (TIMING convention; against the ID-consumed word the lead never exceeds
    NUM_FB-1)}; ignore_bins l4_idle{NUM_FB with no data access outstanding}, l5p{[NUM_FB+1:$]}: the
    throttle caps linear prefetch at FB_THRESHOLD+1 = NUM_FB-1 non-stale buffers (F-FE-017,
    F-IC-038); the NUM_FB-th buffer is allocated only by a branch lookup, which is a redirect target
    and not a lead (CG-IC-004.cp_busy_buffers.b4 covers it)
  - cp_throttle_hold iff (b) with more than FB_THRESHOLD lines open: bins yes{1: no new sequential
    lookup was issued}
  - cp_branch_bypasses_throttle iff a branch lookup with NUM_FB-1 non-stale lines open: bins yes{1:
    the lookup was issued and NUM_FB buffers became busy} (F-IC-043)
  - cp_release_to_next_req iff a new lookup request follows a NUM_FB-open-lines interval = cycles
    from the oldest line's last rvalid to that request: bins c1_2_off{[1:2], icache_enable == 0},
    c3_4_caching{[3:4], caching: RAM write, release, lookup, IC1 miss; rtl/ibex_icache.sv:815-822,
    843-844}; ignore_bins c5p{[5:$]}: gen_chk_ibus_proto failure (TP-IC-052)
  - cp_output_hold iff (c) = cycles the retired word was held at the icache output before ID
    accepted it (agent delivery or hit cycle to ID acceptance, back-dated from RVFI): bins h0{0},
    h1{1}, h2_3{[2:3]}, h4p{[4:$]}
- Crosses:
  - cr_reason_x_wfi = cp_busy_reason x cp_wfi_after_fencei: bins sweep_wfi{inval_sweep,yes},
    key_wfi{key_await,yes}
- Adopted (riscv-dv): none
- TP items: TP-IC-009, TP-IC-050, TP-IC-051, TP-IC-052, TP-IC-053

### CG-IC-008: gen_cg_ic_regime
- Features: F-IC-013, F-IC-014, F-IC-023, F-IC-030, F-IC-008
- Sample: rvfi_valid; condition: regime schedule active; anti-vacuity: samples the fetch source of
  each retired instruction against the active knobs; a hit proves the binned source executed under
  the binned regime with the cache in the binned state. Knob-by-knob crosses (ecc rate x key delay)
  belong to fcov_xcut.md CG-REG-005 cr_ecc_x_key; here each knob is crossed only with the observed
  fetch source.
- Coverpoints:
  - cp_fetch_src = source of the retired word (agent record + shadow view): bins bus_disabled{bus
    record, icache_enable == 0}, bus_sweep{bus record, sweep running}, bus_miss{bus record, cache
    enabled and idle}, cache_hit{no bus record}, bus_key_await{bus record, key request pending}
  - cp_instr_mix = knob:instr_mix (cross operand only): values isa_only, m_heavy, compressed_heavy,
    bitmanip_heavy, csr_heavy, ls_heavy, branch_heavy, mixed
  - cp_imem_regime = knob:imem_rvalid_delay (cross operand only): values min1, short, long, random
  - cp_ecc_knob = knob:icache_ecc_err_rate (cross operand only): values none, rare, frequent
  - cp_key_knob = knob:scr_key_delay (cross operand only): values immediate, delayed,
    withheld_then_valid
- Crosses:
  - cr_src_x_mix = cp_fetch_src x cp_instr_mix: bins hit_isa_only{cache_hit,isa_only},
    hit_m_heavy{cache_hit,m_heavy}, hit_compressed{cache_hit,compressed_heavy},
    hit_bitmanip{cache_hit,bitmanip_heavy}, hit_csr{cache_hit,csr_heavy}, hit_ls{cache_hit,
    ls_heavy}, hit_branch{cache_hit,branch_heavy}, hit_mixed{cache_hit,mixed}, sweep_mixed{
    bus_sweep,mixed}, await_ls{bus_key_await,ls_heavy}, miss_branch{bus_miss,branch_heavy},
    disabled_compressed{bus_disabled,compressed_heavy} (no impossible combination)
  - cr_src_x_regime = cp_fetch_src x cp_imem_regime: bins miss_min1{bus_miss,min1}, miss_short{
    bus_miss,short}, miss_long{bus_miss,long}, miss_random{bus_miss,random}, disabled_long{
    bus_disabled,long}, hit_long{cache_hit,long}, sweep_short{bus_sweep,short}, await_random{
    bus_key_await,random} (no impossible combination)
  - cr_src_x_ecc = cp_fetch_src x cp_ecc_knob: bins hit_rare{cache_hit,rare}, hit_frequent{
    cache_hit,frequent}, miss_frequent{bus_miss,frequent}, disabled_frequent{bus_disabled,frequent}
    (no impossible combination)
  - cr_src_x_key = cp_fetch_src x cp_key_knob: bins await_withheld{bus_key_await,
    withheld_then_valid}, await_delayed{bus_key_await,delayed}, sweep_immediate{bus_sweep,
    immediate}, hit_delayed{cache_hit,delayed} (no impossible combination)
- Adopted (riscv-dv): none
- TP items: TP-IC-009, TP-IC-011, TP-IC-012, TP-IC-017, TP-IC-018, TP-IC-047, TP-IC-049, TP-IC-054,
  TP-IC-055, TP-IC-056

---------------------------------------------------------------------------------------------------

## Counts

- Covergroups: 30 (IMEM 7, DMEM 9, FE 6, IC 8)
- Coverpoints and crosses: 310 (of which 14 are cross-operand-only coverpoints with no
  closure bin: 12 knob operands and the two driver-rule cp_gnt_with_req; 1 is probe-gated (P1) and
  4 are informational)
- Coverpoint bins (closure, after ignore_bins): 638
- Cross bins (named, closure): 389
- Ignored bins / combinations: 67 ignore_bins clauses
- Adopted bins: 0
- Bug-tied bins (credit an open bug candidate, owned by the expected-fail item TP-DMEM-064): 3
  (CG-DMEM-007.cp_rf_suppressed.no_b16, cr_pattern_x_we.first_only_load,
  cr_class_x_we_x_beat.single_load_first; B16)
- Informational bins (excluded from the closure measure): 8 (CG-IMEM-007.cp_unsolicited_rvalid_case 3,
  CG-DMEM-009.cp_unsolicited_rvalid_case 3, CG-DMEM-006.cp_b14_records 1, CG-IC-006.cp_multiway_mismatch 1)
- Probe-gated bins (not in any manifest): 1 (CG-FE-004.cp_dummy_seen.yes)
- Bins referenced by trace_tp_bin_mem_fetch_icache.csv: 1035 distinct bins in 1161 rows;
  every closure bin above is owned by at least one TP item (no orphans, Critic M-04)

## Probe candidates

Bins that cannot be sampled from the boundary, the agents' records or RVFI. The DV Lead decides;
rulings so far from gen_critic_tb_arch_components_v1.md C8 and gen_tb_architecture.md 8.3 item 5.

- P1 dummy_instr_id_o (accepted, coverage-only): CG-FE-004.cp_dummy_seen. Marked "probe-gated (P1),
  not in manifest"; TP-FE-017 lists only the timing-gap bins (cp_cause.dummy_gap, cp_stall_len.l1)
  until the probe register carries P1. Without the probe the dummy_gap attribution is by exclusion
  (no bus, hazard or redirect cause) and the fire-check keeps only the timing-gap assertion.
- P2 shadow tag view (rejected): NOT needed. CG-IC-003 and CG-FE-002.cp_halves_src derive hit/miss,
  way and validity from gen_icache_ram_model's mirror of the tag writes seen on ic_tag_* plus the
  bus records; no internal signal is read. Listed here only to record that the derivation is
  boundary-based.
- P3 icache output handshake toward IF (rejected): F-IC-044 is covered indirectly by
  CG-IC-007.cp_output_hold (hold time measured from the agent's delivery cycle to ID acceptance,
  back-dated from RVFI) and checked by gen_isa_compare; a bound assertion on the icache output
  valid/ready pair would need the internal signals and stays out of the plan.
- P4 LSU CTX states (conditional, coverage-only): F-DMEM-043 has no bin. The absence of the CHERIoT
  CTX states is a code-coverage exclusion (cheriot-out-of-scope) plus the bound assertion
  IbexLsuIsCapDisabled named by gen_chk_cheriot_quiet; the boundary bin is
  CG-DMEM-008.cp_tag_in_at_gnt.
- P5 register-file write seam (rejected): the WB-flop write cycle of F-DMEM-051 is not observable at
  the boundary; TP-DMEM-061 uses the RVFI timing (CG-DMEM-008.cp_rvfi_load_latency,
  cp_wb_source, cp_load_then_alu_b2b) as the evidence.


# 3.7 Areas DIT, SEC, RST, RVFI, CHERI: Dummy instructions and data-independent timing, alerts and countermeasures, reset and boot, RVFI trace, CHERIoT carve-out


Companion of tp_sec_rst_rvfi_cheri.md. All covergroups live in the gen_ namespace and sample from
the DUT boundary or RVFI unless marked P1 (wrapper-internal dummy-instruction nets; see Probe
candidates). Conventions applied by fix brief 2 (Critic pre-review S-3/S-4/S-5/S-7/S-8/S-14):

- Parameters, never literals, in bin expressions: ibex_pkg::IbexMuBiOn / IbexMuBiOff and
  IbexMuBiWidth (= $bits(ibex_mubi_t), rtl/ibex_pkg.sv:752-760); $bits(irq_fast_i) (15 fast lines,
  rtl/ibex_core.sv:122); MHPMCounterNum (10: rvfi_ext_mhpmcounters[0..MHPMCounterNum-1]); privilege
  levels PRIV_LVL_M / PRIV_LVL_U; CSR addresses by their ibex_pkg csr_num_e names (CSR_CPUCTRLSTS,
  CSR_SECURESEED, CSR_MARCHID, CSR_MISA, CSR_MSHWM, CSR_MSHWMB, CSR_CDBG_CTRL); opcodes
  OPCODE_CHERI / OPCODE_AUICGP; exception causes by their ExcCause* localparams; marchid by
  CSR_MARCHID_VALUE; debug causes DBG_CAUSE_*. Numeric values in parentheses are documentation.
- Multi-event covergroups: a coverpoint that is defined for a subset of the group's sample events
  carries `iff <event>` in its own line; a coverpoint without iff is defined for every event of the
  group (an explicit `na` bin names the events it does not apply to).
- Witness bins (zero / none / "nothing happened"): a run-total witness is sampled once at end of
  test (eot) ONLY when the stated activity qualifier holds (the stimulus that could have produced
  the effect was present); a per-event witness is sampled once per event that could have produced
  the effect. Pure checker mirrors (a bin that only restates a checker rule on every record, such
  as "order advanced by one" or "rvfi_halt is 0") are not bins; they are named in the Retired lines.
- Timing bins (Q-TIME qualifier, S-4): "gap" = cycles from the previous rvfi_valid to this record's
  rvfi_valid, i.e. this instruction's own ID residency when the pipe flows. A record is
  timing-qualified (q_time_ok) only if: (1) a previous record exists in the same reset epoch;
  (2) no fetch stall: this instruction's fetch word was delivered (ibus rvalid, or the mem area's
  boundary-derived icache-hit model) at least 2 cycles before the previous record's rvfi_valid
  (rvfi_valid is one flop after WB exit, gen_tb_architecture.md 8.2); (3) the previous record is
  not a CSR write (csr_pipe_flush re-fetches the follower, rtl/ibex_id_stage.sv:593-597), not a
  taken branch or jump and not a trap/mret/dret/fence.i record (redirect target fetch); (4) no
  dummy in the gap: dummy_instr_en == 0 in the cfg tracked from retired cpuctrlsts writes; (5) no
  mcycle / mcountinhibit write between the two records (irrelevant for TB-cycle-counted gaps,
  stated for completeness). Under Q-TIME a gap outside the enumerated bins is a checker error and
  is an ignore_bins, not coverage.
- Cross-operand-only coverpoints: a coverpoint marked "(cross operand only; owner <CG.cp>)" exists
  so the group's crosses can use it; its standalone bins are not manifest bins and are not in the
  trace CSV (dv_principles Section 4: no duplicate coverpoints). Knob values (knob:*) are cross
  operands here; their bins are owned by fcov_xcut.md CG-REG-*.
- Probe-gated (P1) bins: all of CG-DIT-004 (including the new cp_rs2_val_zero / cr_div_zero),
  CG-DIT-005.cp_pattern_changed, CG-RST-004.cp_dummy_adjacent and cr_rd_bank_dummy,
  CG-RST-002.cp_inflight.dummy_in_id and cr_inflight_len.dummy_in_id_short. They stay in the trace
  CSV for feature traceability but are NOT manifest (must-hit) bins until the probe register
  carries P1 (gen_tb_architecture.md 8.3 item 5; Critic pre-review S-14).
- P1 level semantics (rtl-arch fact-check X-22, fix brief 3): dummy_instr_id_o / dummy_instr_wb_o
  are levels updated only on if_id_pipe_reg_we (rtl/ibex_if_stage.sv:538-544;
  rtl/ibex_wb_stage.sv:222-241) and hold the last registered value after the dummy left the
  stage; every P1 sample below is keyed on the insertion EVENT (rising dummy_instr_id_o with
  if_id_pipe_reg_we) or on the dummy's residency (from the event to the next if_id_pipe_reg_we),
  never on the held level. A dummy reading x0 gets rf_data_r0_q (the previous dummy's result,
  rtl/ibex_register_file_ff.sv:159-173), so a zero divisor is an operand value, not the index x0.
- Fact-check conventions used in the bins (tp header C-1..C-16): rvfi_ext_irq_valid is a level
  that never coincides with rvfi_valid (C-13); rvfi_ext_debug_req = 1 occurs only on debug-mode
  records (C-3); the load-suppression rule is per completing beat and the first-beat class is
  B16 (C-8); the internal NMI may follow up to two ordinary instructions (C-7, D21).
- Never `illegal_bins = default sequence`; every non-listed value is an explicit bin, an
  ignore_bins with a reason, or left to a named checker (stated). "cfg tracked" = the TB's model of
  cpuctrlsts bits 5:0 updated from retired cpuctrlsts write records (WARL-legalised).
- rvfi_trap is 0 on an ebreak that enters debug mode (rtl/ibex_core.sv:1885-1886, S-2): the debug
  path is is_ebreak(rvfi_insn) && !rvfi_trap && next rvfi_pc_rdata == DmHaltAddr; the exception
  path is rvfi_trap == 1.

---------------------------------------------------------------------------------------------------
## DIT
---------------------------------------------------------------------------------------------------

### CG-DIT-001: gen_cg_dit_cpuctrlsts_cfg
- Features: F-DIT-001, F-DIT-006, F-DIT-008, F-DIT-011, F-DIT-012, F-DIT-023, F-SEC-031, F-SEC-032,
  F-SEC-033, F-DIT-010, F-CSR-085, F-DIT-002 (parent of folded bins hosted here)
- Sample: rvfi_valid of a CSR instruction whose csr field == CSR_CPUCTRLSTS, trapped or not;
  condition: rvfi_valid && is_csr_op(rvfi_insn) && csr_addr(rvfi_insn) == ibex_pkg::CSR_CPUCTRLSTS;
  anti-vacuity: only cpuctrlsts accesses sample (a fraction of a percent of records); a hit proves
  the program configured or probed the security control register, and the toggle bins prove a
  change of DIT or dummy state happened during the run (cp_next_insn is taken from the following
  retired record, so cr_dit_next proves the hand-over scenario existed). Event classes: m_write =
  rvfi_mode == PRIV_LVL_M && csr_we(rvfi_insn) && !rvfi_trap; m_read_only = rvfi_mode == PRIV_LVL_M
  && (csrrs/csrrc with rs1 == x0 || csrrsi/csrrci with uimm == 0) && !rvfi_trap; u_trap = rvfi_mode
  == PRIV_LVL_U && rvfi_trap. This group OWNS the cfg-state coverpoints cp_dit / cp_dummy_en /
  cp_mask (the state changes only through a retired write); CG-DIT-002/003/004/005 carry
  cfg-tracked copies as cross operands only.
- Coverpoints:
  - cp_access = event class: bins m_write{m_write}, m_read_only{m_read_only}, u_trap{u_trap}
  - cp_dit = legalised new value bit 1 iff m_write: bins off{0}, on{1}
  - cp_dummy_en = legalised new value bit 2 iff m_write: bins off{0}, on{1}
  - cp_mask = new value bits 5:3 iff m_write: bins m000{3'd0}, m001{3'd1}, m010{3'd2}, m011{3'd3},
    m100{3'd4}, m101{3'd5}, m110{3'd6}, m111{3'd7}
  - cp_icache_en = new value bit 0 iff m_write: bins off{0}, on{1}
  - cp_dit_toggle = {old bit 1, new bit 1} iff m_write: bins off2on{0 -> 1}, on2off{1 -> 0},
    hold_off{0 -> 0}, hold_on{1 -> 1}
  - cp_dummy_toggle = {old bit 2, new bit 2} iff m_write: bins off2on{0 -> 1}, on2off{1 -> 0},
    hold_off{0 -> 0}, hold_on{1 -> 1}
  - cp_wr_reserved = written 1s in read-only positions iff m_write: bins none{wdata[31:8] == 0},
    bits31_9{|wdata[31:9] && !wdata[8]}, bit8{wdata[8] && !(|wdata[31:9])}, both{wdata[8] &&
    |wdata[31:9]}
  - cp_next_insn = class of the next retired record iff m_write: bins branch{conditional branch},
    div{div/divu/rem/remu}, mul{mul/mulh/mulhsu/mulhu}, load_store{load or store}, csr{CSR op},
    other{everything else}. Every cpuctrlsts write flushes the pipe and re-fetches the follower
    (csr_pipe_flush, rtl/ibex_id_stage.sv:593-597), so the follower's timing is measured by
    TP-DIT-007's control-pair method, never by the Q-TIME bins of CG-DIT-002/003.
- Crosses:
  - cr_dummy_mask = cp_dummy_en x cp_mask: on_m000, on_m001, on_m010, on_m011, on_m100, on_m101,
    on_m110, on_m111; ignore off_m*: the mask has no effect while dummies are disabled
  - cr_dit_next = cp_dit_toggle x cp_next_insn: off2on_branch, off2on_div, off2on_mul,
    off2on_load_store, on2off_branch, on2off_div, on2off_mul, on2off_load_store; ignore
    hold_*_*: no hand-over when the value does not change; ignore *_csr and *_other: not a timing
    consumer of the DIT bit (the standalone cp_next_insn bins keep them)
- Adopted (riscv-dv): none
- TP items: TP-DIT-001, TP-DIT-007, TP-DIT-009, TP-DIT-010, TP-DIT-011, TP-DIT-012, TP-DIT-013,
  TP-DIT-016, TP-DIT-025, TP-DIT-026, TP-DIT-033, TP-SEC-014, TP-SEC-033, TP-SEC-034

### CG-DIT-002: gen_cg_dit_branch_timing
- Features: F-DIT-002, F-DIT-007, F-DIT-010
- Sample: rvfi_valid of a retired conditional branch (beq/bne/blt/bge/bltu/bgeu/c.beqz/c.bnez)
  with rvfi_trap == 0 that is timing-qualified (Q-TIME, header); condition: rvfi_valid &&
  is_cond_branch(rvfi_insn) && !rvfi_trap && q_time_ok; anti-vacuity: only qualified branches
  sample (a run with dummies enabled or a slow fetch regime samples few or none); the gap is this
  branch's own ID residency: with BranchTargetALU = 1 every branch completes in FIRST_CYCLE when
  DIT is off and every branch takes MULTI_CYCLE when DIT is on, taken or not
  (rtl/ibex_id_stage.sv:920-928), so a hit proves a branch of that taken/DIT class retired with its
  timing observed; taken is derived from rvfi_pc_wdata != rvfi_pc_rdata + insn_len, not assumed.
- Coverpoints:
  - cp_dit = cfg tracked data_ind_timing at the branch (cross operand only; owner
    CG-DIT-001.cp_dit): bins off{0}, on{1}
  - cp_taken = rvfi_pc_wdata != rvfi_pc_rdata + insn_len: bins taken{1}, not_taken{0}
  - cp_compressed = rvfi_insn[1:0] != 2'b11: bins c16{1}, i32{0}
  - cp_gap = cycles since the previous rvfi_valid (Q-TIME): bins g1{1}, g2{2}; ignore_bins
    g3_plus{[3:$]}: under Q-TIME a longer gap is a gen_test_dit_branch error, not coverage
  - cp_priv = rvfi_mode: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}; ignore_bins other{PRIV_LVL_H,
    PRIV_LVL_S}: modes H/S do not exist in Ibex (checker error if seen)
  - cp_pc_wdata = kind of next pc: bins fallthrough{rvfi_pc_wdata == rvfi_pc_rdata + insn_len},
    target{rvfi_pc_wdata == rvfi_pc_rdata + branch_imm(rvfi_insn)}; ignore_bins neither{any other
    value}: a gen_isa_compare error, not a coverage case
- Crosses:
  - cr_dit_taken_c = cp_dit x cp_taken x cp_compressed: off_taken_c16, off_taken_i32, off_nt_c16,
    off_nt_i32, on_taken_c16, on_taken_i32, on_nt_c16, on_nt_i32
  - cr_dit_priv = cp_dit x cp_priv: on_m, on_u, off_m, off_u
  - cr_dit_gap = cp_dit x cp_taken x cp_gap: off_taken_g1, off_nt_g1, on_taken_g2, on_nt_g2;
    ignore off_taken_g2 and off_nt_g2: with BranchTargetALU = 1 and DIT off every branch
    completes in FIRST_CYCLE (rtl/ibex_id_stage.sv:925-927); ignore on_taken_g1 and on_nt_g1: DIT
    forces MULTI_CYCLE for every branch (:925-928); g3_plus is excluded through the cp_gap ignore
- Adopted (riscv-dv): none
- TP items: TP-DIT-002, TP-DIT-003, TP-DIT-008, TP-DIT-011, TP-DIT-033

### CG-DIT-003: gen_cg_dit_muldiv_timing
- Features: F-DIT-003, F-DIT-004, F-DIT-005, F-DIT-009, F-DIT-024
- Sample: rvfi_valid of a retired RV32M instruction with rvfi_trap == 0 that is timing-qualified
  (Q-TIME, header; in particular dummy_instr_en == 0 in the tracked cfg); condition: rvfi_valid &&
  is_rv32m(rvfi_insn) && !rvfi_trap && q_time_ok; anti-vacuity: only qualified M instructions
  sample and the gap is this instruction's own ID residency, so a hit proves the operand class and
  the observed latency class co-occurred. Latency facts: mul 1 cycle, mulh-class 2 cycles
  (RV32MSingleCycle, rtl/ibex_multdiv_fast.sv:210-235); a divide by zero with DIT off completes
  early through MD_IDLE -> MD_FINISH (2 cycles, :434,445,514-517); every other divide, and every
  divide with DIT on, takes the full 37 cycles (D7, EX-03).
- Coverpoints:
  - cp_op = funct3 decode (opcode OP, funct7 0000001): bins mul{3'b000}, mulh{3'b001},
    mulhsu{3'b010}, mulhu{3'b011}, div{3'b100}, divu{3'b101}, rem{3'b110}, remu{3'b111}
  - cp_class = op class: bins mul{mul}, mulh{mulh, mulhsu, mulhu}, div{div, divu, rem, remu}
  - cp_dit = cfg tracked data_ind_timing (cross operand only; owner CG-DIT-001.cp_dit): bins
    off{0}, on{1}
  - cp_rs2_zero = rvfi_rs2_rdata == 0: bins zero{1}, nonzero{0}
  - cp_overflow = div/rem with rvfi_rs1_rdata == 32'h80000000 && rvfi_rs2_rdata == 32'hFFFFFFFF:
    bins yes{1}, no{0}
  - cp_latency = cycles since the previous rvfi_valid (Q-TIME): bins one{1}, two{2}, full{37};
    ignore_bins other{[3:36], [38:$]}: under Q-TIME any other gap is a gen_test_dit_div /
    gen_test_dit_mul error, not coverage
  - (retired: cp_dummy_en - folded into the Q-TIME qualifier; the dummy state is owned by
    CG-DIT-001.cp_dummy_en)
- Crosses:
  - cr_div_dit_zero = cp_class x cp_dit x cp_rs2_zero: div_off_zero, div_off_nz, div_on_zero,
    div_on_nz; ignore mul_*_* and mulh_*_*: rs2 == 0 has no timing effect on the multiplier
  - cr_latency = cp_class x cp_dit x cp_rs2_zero x cp_latency: div_off_zero_two, div_off_nz_full,
    div_on_zero_full, div_on_nz_full, mul_off_zero_one, mul_off_nz_one, mul_on_zero_one,
    mul_on_nz_one, mulh_off_zero_two, mulh_off_nz_two, mulh_on_zero_two, mulh_on_nz_two; ignore
    div_on_zero_two and div_on_nz_two: DIT removes the early completion
    (rtl/ibex_multdiv_fast.sv:434,445); ignore div_off_nz_two: early completion needs a zero
    divisor; ignore div_off_zero_full: a zero divisor with DIT off always completes early; ignore
    div_*_*_one: the divider never completes in one cycle; ignore mul_*_*_two, mul_*_*_full,
    mulh_*_*_one and mulh_*_*_full: mul is single-cycle and mulh-class two-cycle, neither has a
    divide path
  - cr_op_dit = cp_op x cp_dit: div_on, divu_on, rem_on, remu_on, div_off, divu_off, rem_off,
    remu_off, mul_on, mul_off, mulh_on, mulh_off, mulhsu_on, mulhsu_off, mulhu_on, mulhu_off
- Adopted (riscv-dv): none
- TP items: TP-DIT-004, TP-DIT-005, TP-DIT-006

### CG-DIT-004: gen_cg_dit_dummy_insert (P1; probe-gated, not in manifest until the probe register carries P1)
- Features: F-DIT-009, F-DIT-011, F-DIT-012, F-DIT-013, F-DIT-015, F-DIT-016, F-DIT-017, F-DIT-018,
  F-DIT-019, F-DIT-020, F-DIT-021, F-DIT-022, F-DIT-023, F-DIT-024, F-DIT-027, F-DIT-028, F-DIT-029,
  F-DIT-030, F-RVFI-024, F-DIT-003 (parent of folded bins hosted here)
- Sample: (a) insert: rising edge of the wrapper-internal net dummy_instr_id_o while the IF/ID
  register is written; (b) window_close: the close of a test-defined measurement window (>= 200
  retired records, or >= 200 cycles for the fetch_off / wfi_sleep kinds, with the tracked cfg
  constant over the window); condition: (dummy_instr_id_o && !dummy_instr_id_o_prev) ||
  window_close_event; anti-vacuity: insert samples only when a dummy actually entered ID (enable
  alone does not sample; a hit proves insertion happened and in which context); window_close
  samples once per window, so the count bins measure real windows and every zero-count bin is
  qualified by its window kind (the stimulus that could have produced insertions is part of the
  kind's predicate).
- Coverpoints:
  - cp_event: bins insert{dummy_instr_id_o rising}, window_close{window_close_event}
  - cp_type = if_stage fcov_dummy_instr_type (P1) iff insert: bins add{0}, mul{1}, div{2}, and{3}
  - cp_rs1 = rf_raddr_a_o during the dummy iff insert: bins x0{0}, x1_15{[1:15]}, x16{16},
    x17_31{[17:31]}
  - cp_rs2 = rf_raddr_b_o during the dummy iff insert: bins x0{0}, x1_15{[1:15]}, x16{16},
    x17_31{[17:31]} (register INDEX only: x0 read by a dummy returns rf_data_r0_q, the previous
    dummy's result, rtl/ibex_register_file_ff.sv:159-173, so this coverpoint says nothing about
    the divisor value)
  - cp_rs2_val_zero (P1) = the RF read-port B data (rf_rdata_b, wrapper-internal seam net) during
    the dummy == 0 iff insert && cp_type == div: bins zero{1}, nonzero{0} (the fast-path selector
    equal_to_zero_i is this value, rtl/ibex_multdiv_fast.sv:434, :445)
  - cp_dit = cfg tracked data_ind_timing at the insertion (cross operand only; owner
    CG-DIT-001.cp_dit) iff insert: bins off{0}, on{1}
  - cp_mask = cfg tracked dummy_instr_mask at the insertion (cross operand only; owner
    CG-DIT-001.cp_mask) iff insert: bins m000{3'd0}, m001{3'd1}, m010{3'd2}, m011{3'd3}, m100{3'd4},
    m101{3'd5}, m110{3'd6}, m111{3'd7}
  - cp_context = TB context during the dummy's ID residency (from the insertion event to the next
    if_id_pipe_reg_we; an irq / debug_req edge that lands after the dummy left ID is NOT
    attributed to it, fact-check N3) iff insert: bins straight{no redirect in the
    previous 2 records, no pending event}, after_taken_branch{previous record a taken branch or
    jump}, irq_pending{irq_pending_o == 1 && mstatus.MIE model == 1}, debug_req_high{debug_req_i
    == 1}, step_active{dcsr.step model == 1 && rvfi_ext_debug_mode == 0}, in_irq_handler{rvfi_intr
    seen since the last mret}, u_mode{rvfi_mode model == PRIV_LVL_U}, in_zcmp{between
    expanded_insn first and last}, hazard_load_wb{a load with rd == rs1 or rs2 of the dummy
    outstanding in WB: no extra stall results, the dummy waits on outstanding_memory_access like
    any instruction, rtl/ibex_id_stage.sv:1059-1062; fact-check TP-DIT-031}; ignore_bins
    fetch_stalled{fetch_enable_i != IbexMuBiOn || core_busy_o ==
    IbexMuBiOff in the previous cycle}: unreachable by construction: the insertion counter advances
    only on fetch_valid or an insertion (rtl/ibex_dummy_instr.sv:100-104,115) and dummy_instr_id_o
    is written only with if_id_pipe_reg_we (rtl/ibex_if_stage.sv:538-544), neither of which occurs
    while fetch is disabled or the core sleeps; the negative is covered by
    cr_window_dummies.fetch_off_none / wfi_sleep_none (TP-DIT-030)
  - cp_back_to_back = previous accepted ID instruction was also a dummy iff insert: bins yes{1},
    no{0}
  - cp_en_cleared_in_flight = the cpuctrlsts write clearing dummy_instr_en committed in ID while
    this dummy was in WB (the dummy's insertion event immediately preceded the write's IF->ID
    transfer) iff insert: bins yes{1}, no{0}; the "dummy in ID when the write commits" case is
    unreachable (the csrw occupies ID when it commits and FLUSH halts IF, rtl/ibex_controller.sv:
    664-679, :816-820; fact-check TP-DIT-025) and is not a bin
  - cp_minstret_excess = minstret delta minus RVFI record count in the window iff window_close:
    bins zero{0}, positive{[1:$]}; ignore_bins negative{[$:-1]}: minstret can never lag the trace
  - cp_dummies_in_window = P1 insert count in the window iff window_close: bins none{0},
    few{[1:9]}, many{[10:$]}
  - cp_window_kind = kind of the closed window iff window_close: bins straight_en{dummy_instr_en
    == 1 (cfg tracked), fetch_enable_i == IbexMuBiOn and core_busy_o == IbexMuBiOn throughout,
    >= 200 records retired}, disabled{dummy_instr_en == 0 throughout, >= 200 records retired},
    fetch_off{dummy_instr_en == 1, fetch_enable_i != IbexMuBiOn throughout, >= 200 cycles},
    wfi_sleep{dummy_instr_en == 1, core_busy_o == IbexMuBiOff throughout, >= 200 cycles}
  - cp_irq_delay_by_dummy iff insert && cp_context inside {irq_pending, debug_req_high} (closed
    when the handler's / debug ROM's first record retires) = cycles the entry was delayed beyond the
    plain entry latency measured with dummies disabled: bins none{0}, single{[1:2]} (ADD/AND/MUL
    dummy), div{[3:37]} (DIV dummy; 37 = divider latency, D7); ignore_bins over{[38:$]}: a longer
    delay is a gen_chk_irq bound error, not coverage (F-DIT-030)
- Crosses:
  - cr_type_dit = cp_type x cp_dit: div_on, div_off, mul_on, mul_off, add_on, add_off, and_on,
    and_off
  - cr_type_irq = cp_type x cp_context: div_irq_pending, mul_irq_pending, add_irq_pending,
    and_irq_pending, div_debug_req_high; ignore the other cp_context values: the mask x context
    pairs belong to cr_mask_ctx (F-DIT-030)
  - cr_mask_ctx = cp_mask x cp_context: m000_straight, m111_straight, m000_after_taken_branch,
    m000_irq_pending, m000_debug_req_high, m000_step_active, m000_in_zcmp, m000_hazard_load_wb
    (fetch_stalled is excluded through the cp_context ignore)
  - cr_div_zero = cp_type x cp_rs2_val_zero x cp_dit iff cp_type == div: div_zero_on{full path
    forced by DIT}, div_zero_off{fast path, +2}, div_nz_on, div_nz_off{full path, +37}; no
    ignores (cp_rs2_val_zero is sampled only for div dummies)
  - (retired: cr_div_rs2 - it encoded the wrong premise "rs2 == x0 => divide by zero" (fact-check
    TP-DIT-010, X-22); replaced by cr_div_zero on the operand VALUE; the register-index bins stay
    in cp_rs1 / cp_rs2)
  - cr_window_dummies = cp_window_kind x cp_dummies_in_window: straight_en_few, straight_en_many,
    disabled_none, fetch_off_none, wfi_sleep_none; ignore straight_en_none: the insertion
    threshold is at most 2**TIMEOUT_CNT_W - 1 = 31 fetches (rtl/ibex_dummy_instr.sv:33,97), so a
    >= 200-record window with dummies enabled always inserts (gen_test_dit_dummy error otherwise);
    ignore disabled_few and disabled_many: insertion while disabled is a gen_test_dit_dummy error;
    ignore fetch_off_few, fetch_off_many, wfi_sleep_few and wfi_sleep_many: insertion while fetch
    is disabled or the core sleeps is the TP-DIT-030 checker error (unreachable by the cp_context
    reason)
- Probe status: pending probe-register ruling (candidate P9: if_stage_i fcov_dummy_instr_type and the IF/ID
  pipeline write enable if_id_pipe_reg_we, not among P1's registered nets); coverpoints cp_type and the
  insert sample event (cp_event.insert and every iff-insert coverpoint) excluded from manifests until ruled
- Adopted (riscv-dv): none
- TP items: TP-DIT-010, TP-DIT-012, TP-DIT-014, TP-DIT-016, TP-DIT-017, TP-DIT-018, TP-DIT-019,
  TP-DIT-020, TP-DIT-021, TP-DIT-022, TP-DIT-023, TP-DIT-024, TP-DIT-025, TP-DIT-026, TP-DIT-029,
  TP-DIT-030, TP-DIT-031, TP-DIT-032, TP-DIT-033, TP-DIT-034, TP-RVFI-027

### CG-DIT-005: gen_cg_dit_secureseed
- Features: F-DIT-014, F-DIT-025, F-DIT-026, F-DIT-010
- Sample: rvfi_valid of a CSR instruction with csr field == CSR_SECURESEED, trapped or not;
  condition: rvfi_valid && is_csr_op(rvfi_insn) && csr_addr(rvfi_insn) == ibex_pkg::CSR_SECURESEED;
  anti-vacuity: only secureseed accesses sample; the effect bins are computed from the operand
  (rs1/uimm) and the running-seed model, and cp_pattern_changed from the P1 insertion sequence
  before/after the write, so a hit proves a reseed scenario, not merely a CSR access. Event
  classes: write = rvfi_mode == PRIV_LVL_M && csr_we(rvfi_insn) && !rvfi_trap; read_only =
  rvfi_mode == PRIV_LVL_M && (csrrs/csrrc with rs1 == x0 || csrrsi/csrrci with uimm == 0) &&
  !rvfi_trap; u_trap = rvfi_mode == PRIV_LVL_U && rvfi_trap.
- Coverpoints:
  - cp_op = CSR op form (funct3): bins csrrw{3'b001}, csrrs{3'b010}, csrrc{3'b011},
    csrrwi{3'b101}, csrrsi{3'b110}, csrrci{3'b111}
  - cp_effect = event class: bins write{write}, read_only{read_only}, u_trap{u_trap}
  - cp_wdata = write data class iff write: bins zero{wdata == 0}, nonzero{wdata != 0 && wdata !=
    seed_q model}, cancels_seed{wdata == seed_q model, so the XOR gives an all-zero LFSR seed}
  - cp_dummy_en_at_write = cfg tracked dummy_instr_en (cross operand only; owner
    CG-DIT-001.cp_dummy_en) iff !rvfi_trap: bins off{0}, on{1}
  - cp_pattern_changed (P1) iff write || read_only = insertion-position sequence after the op
    differs from before: bins yes{1}, no{0}
  - (retired: cp_readback_zero - "secureseed reads 0" is a gen_chk_csr_readback rule, not a bin)
- Crosses:
  - cr_effect_dummy = cp_effect x cp_dummy_en_at_write: write_on, write_off, read_only_on,
    read_only_off; ignore u_trap_on and u_trap_off: a trapped access has no effect
  - cr_wdata_effect = cp_wdata x cp_effect: zero_write, nonzero_write, cancels_seed_write
    (cp_wdata is sampled only on writes, so no other combination exists)
- Adopted (riscv-dv): none
- TP items: TP-DIT-011, TP-DIT-015, TP-DIT-027, TP-DIT-028

---------------------------------------------------------------------------------------------------
## SEC
---------------------------------------------------------------------------------------------------

### CG-SEC-001: gen_cg_sec_alerts
- Features: F-SEC-001, F-SEC-002, F-SEC-003, F-SEC-007, F-SEC-008, F-SEC-009, F-SEC-010, F-SEC-011,
  F-SEC-013, F-SEC-034, F-SEC-035, F-SEC-036, F-DIT-017, F-DIT-022, F-SEC-004 (parent of folded bins
  hosted here)
- Sample: (a) alert events: any cycle where an alert output is high; (b) inject: any TB injection
  event; (c) reset_close: the close of a reset window at rst_ni release, and post_reset_close: the
  close of the two-cycle window after release, both sampled ONLY when the window had activity that
  could raise an alert (>= 1 response beat returned on either bus inside the window, or an alert
  pulse within the 3 cycles before the reset assertion); (d) eot: once at end of test ONLY when the
  run retired >= 1000 RVFI records including >= 10 PC redirects (the PC-increment check arms on
  sequential code and disarms on redirects, so both classes were exercised); condition:
  alert_minor_o || alert_major_internal_o || alert_major_bus_o || inject_event ||
  reset_close_event || post_reset_close_event || eot_event; anti-vacuity: alerts and injections
  are rare (a few per run); the window and eot samples carry activity qualifiers, so their zero
  bins are hit only when the stimulus that could have raised an alert was present and none came.
- Coverpoints:
  - cp_event: bins alert_minor{alert_minor_o}, alert_major_bus{alert_major_bus_o},
    alert_major_internal{alert_major_internal_o}, inject{inject_event},
    reset_close{reset_close_event}, post_reset_close{post_reset_close_event}, eot{eot_event}
  - cp_alert = {major_internal, major_bus, minor} iff !eot: at alert/inject events the same-cycle
    vector, at reset_close / post_reset_close the OR over the window: bins none{3'b000},
    minor{3'b001}, major_bus{3'b010}, major_internal{3'b100}; ignore_bins multi{3'b011, 3'b101,
    3'b110, 3'b111}: two alerts in one cycle or window have no common cause in this DUT (checker
    reports it)
  - cp_inject_kind iff inject || alert events = the injection at this event, or the most recent
    injection within the correlation window for an alert event: bins icache_ecc{tag/data RAM bit
    flip}, ibus_intg{corrupted instr_rdata_i check bits}, dbus_load_intg{corrupted data_rdata_i
    check bits on a load response}, dbus_store_intg{same on a store response},
    spurious_dbus_intg{data_rvalid_i with corrupted check bits and no request outstanding},
    spurious_dbus_clean{data_rvalid_i with valid check bits and no request outstanding},
    pc_fault{IF-stage PC perturbation, mutation build only}; an alert event with no attributable
    injection is a gen_chk_alerts error, not a bin (the former `none` bin is retired)
  - cp_phase iff alert events || inject = pipeline phase at the event: bins in_reset{rst_ni == 0},
    post_reset_2cyc{first two cycles after release}, running{rst_ni == 1, fetch_enable_i ==
    IbexMuBiOn, core_busy_o == IbexMuBiOn, rvfi_ext_debug_mode model == 0, after the first two
    cycles}, fetch_disabled{fetch_enable_i != IbexMuBiOn}, in_wfi{core_busy_o == IbexMuBiOff},
    in_debug{rvfi_ext_debug_mode model == 1}
  - cp_minor_count_per_inject iff inject close of an icache_ecc injection = alert_minor_o pulses
    attributed to that injection: bins one{1}; zero or two-plus pulses are gen_chk_alerts errors,
    not bins (the former `zero` bin is retired; the quiet-run witness is cp_minor_quiet_run)
  - cp_minor_quiet_run iff eot && zero icache_ecc injections in the run && >= 1000
    boundary-derived icache hits with icache_enable == 1 (the lookups that could have raised a
    false minor alert) = alert_minor_o pulse count in the run: bins zero{0}
  - cp_internal_total iff eot (qualified as in the Sample) = alert_major_internal_o pulse count in
    the run: bins zero{0}, nonzero{[1:$]} (nonzero only in the TP-SEC-004 mutation build)
  - cp_pulse_width iff alert events = consecutive high cycles of the sampled alert: bins
    one_cycle{1}, multi_cycle{[2:$]}
- Crosses:
  - cr_alert_inject = cp_alert x cp_inject_kind: minor_icache_ecc, major_bus_ibus_intg,
    major_bus_dbus_load_intg, major_bus_dbus_store_intg, major_bus_spurious_dbus_intg,
    none_spurious_dbus_clean, major_internal_pc_fault; ignore minor_ibus_intg, minor_dbus_*,
    minor_spurious_* and minor_pc_fault: alert_minor_o has a single source; ignore
    major_internal_icache_ecc, major_internal_*_intg and major_internal_spurious_*: RegFileECC = 0
    and ShadowCSR = 0 leave the PC check as the only internal source; ignore major_bus_icache_ecc,
    major_bus_spurious_dbus_clean and major_bus_pc_fault: the bus alert comes only from integrity
    errors; ignore none_icache_ecc, none_*_intg, none_spurious_dbus_intg and none_pc_fault: an
    injection of these kinds without its alert is a checker error
  - cr_alert_phase = cp_alert x cp_phase: major_bus_in_reset, major_bus_running,
    major_bus_fetch_disabled, minor_running, minor_in_debug; ignore minor_in_reset and
    major_internal_in_reset: no cache lookup or ID instruction exists in reset; ignore none_*: the
    no-alert case at an inject event is cr_alert_inject.none_spurious_dbus_clean and at the window
    events cr_window
  - cr_window = cp_event x cp_alert iff (reset_close || post_reset_close): reset_close_none,
    reset_close_major_bus, post_reset_close_none, post_reset_close_major_bus; ignore
    reset_close_minor, reset_close_major_internal, post_reset_close_minor and
    post_reset_close_major_internal: no cache lookup or ID instruction exists in reset or in the
    two BOOT cycles (checker error if seen)
- Adopted (riscv-dv): none
- TP items: TP-DIT-018, TP-DIT-024, TP-SEC-001, TP-SEC-002, TP-SEC-003, TP-SEC-004, TP-SEC-005,
  TP-SEC-006, TP-SEC-007, TP-SEC-008, TP-SEC-009, TP-SEC-010, TP-SEC-011, TP-SEC-013, TP-SEC-014,
  TP-SEC-015, TP-SEC-017, TP-SEC-035, TP-SEC-036, TP-SEC-037, TP-SEC-039, TP-RST-020

### CG-SEC-002: gen_cg_sec_bus_intg
- Features: F-SEC-003, F-SEC-015, F-SEC-016, F-SEC-017, F-SEC-018, F-SEC-019, F-RVFI-021,
  F-RVFI-031
- Sample: a TB integrity-injection event on a returned bus beat (rvalid with corrupted check
  bits) or an unsolicited data response, closed when the DUT response is classified (bounded
  window); condition: intg_inject_event || spurious_dbus_event; anti-vacuity: only injected or
  unsolicited beats sample (never in a clean run); the response fields are observed (alert, NMI
  record, suppress flag, trap), so a hit proves the injection class met its response class.
- Coverpoints:
  - cp_side: bins ibus{instr_rdata_i beat}, dbus{data_rdata_i beat}
  - cp_dbus_op = what the beat answered: bins load{a granted load}, store{a granted store},
    spurious{no request outstanding}, na{ibus}
  - cp_err_bits = number of flipped check/data bits: bins single{1}, double{2}, multi{[3:$]}
  - cp_ibus_consumed: bins executed{the word's PC later appears as rvfi_pc_rdata}, discarded{it
    never does}, na{dbus}
  - cp_half = misaligned position of the beat: bins aligned{single-transaction access}, first{first
    transaction of a split access}, second{second transaction}, na{ibus or spurious}
  - cp_nmi_taken = a record with rvfi_ext_nmi_int == 1 follows within the window: bins yes{1},
    no{0} (no is reachable only for the ibus side: an instruction-side integrity error gives the
    alert plus a fetch fault, no NMI (D14); every dbus beat with bad check bits, solicited or
    spurious, raises the internal NMI because mem_resp_intg_err is not qualified by an
    outstanding access, rtl/ibex_id_stage.sv:613, rtl/ibex_controller.sv:413-417; fact-check
    TP-SEC-010)
  - cp_nmi_latency iff cp_nmi_taken == yes = ordinary instructions retired between the corrupted
    beat's record and the NMI entry (a Zcmp sequence counts as one instruction, its micro-op
    records folded): bins same_insn{0}, next_insn{1}, two_insn{2}; ignore_bins later{[3:$]}: the
    pending flag registers one cycle after rvalid and at most one more instruction is accepted
    into ID in the response cycle (rtl/ibex_controller.sv:402-438; X-10, D21, C-7; checker error
    if seen)
  - cp_rf_wr_suppress = rvfi_ext_rf_wr_suppress on the answered load/store record (cross operand
    only; owner CG-RVFI-003.cp_rf_wr_suppress) iff dbus && !spurious: bins yes{1}, no{0}
  - cp_first_beat_rd_written iff dbus && load && cp_half == first = the load record shows
    rvfi_rd_addr != 0 (the RF was written with merged data although the first beat was corrupt):
    bins yes{1} (B16 evidence: RTL behaviour, rtl/ibex_load_store_unit.sv:514, :697-698); no{0}
    is the documented-intent outcome the RTL cannot produce and is not a bin (re-enable on the
    B16 fix)
  - cp_beat_order iff dbus && load && cp_half == first = whether the second half was granted
    before the first beat's response: bins second_granted_before_first_resp{1},
    second_granted_after_first_resp{0} (decides the NMI mtval: addr_last is already the
    word-aligned second-half address in the first case, rtl/ibex_load_store_unit.sv:258-266,
    rtl/ibex_controller.sv:416; fact-check N7)
  - cp_fetch_fault iff ibus = an rvfi_trap record with mcause ExcCauseInstrAccessFault follows for
    that PC: bins yes{1}, no{0}
  - cp_load_size = funct3 size of the answered load: bins byte{lb/lbu}, half{lh/lhu}, word{lw},
    na{ibus, store or spurious}
- Crosses:
  - cr_side_op = cp_side x cp_dbus_op: ibus_na, dbus_load, dbus_store, dbus_spurious; ignore
    ibus_load, ibus_store, ibus_spurious and dbus_na: undefined combinations
  - cr_load_half = cp_dbus_op x cp_half x cp_rf_wr_suppress: load_aligned_yes, load_second_yes,
    load_first_no{B16 evidence: a misaligned load whose FIRST beat was corrupted is NOT
    suppressed on this RTL, the completing (second) beat being clean; carried by the
    expected-fail items TP-SEC-040 / TP-RVFI-040 only}, store_aligned_no, store_first_no,
    store_second_no; ignore load_first_yes: the documented-intent outcome (security.rst:88) that
    the RTL cannot produce (M-03; re-enable on the B16 fix); ignore load_aligned_no and
    load_second_no: a corrupted completing beat always suppresses (checker error, not coverage);
    ignore store_*_yes: a store writes no register; ignore spurious_*_* and *_na_*:
    cp_rf_wr_suppress is not sampled there
  - cr_first_beat_order = cp_beat_order x cp_first_beat_rd_written:
    second_granted_before_first_resp, second_granted_after_first_resp (cp_first_beat_rd_written
    has the single bin yes, so the cross names carry the order only; B16 evidence)
  - cr_ibus_consumed = cp_side x cp_ibus_consumed x cp_fetch_fault: ibus_executed_yes,
    ibus_discarded_no; ignore ibus_executed_no and ibus_discarded_yes: consumed words fault,
    discarded ones cannot; ignore dbus_*: n/a
  - cr_errbits_side = cp_err_bits x cp_side: single_ibus, double_ibus, multi_ibus, single_dbus,
    double_dbus, multi_dbus
- Adopted (riscv-dv): none
- TP items: TP-SEC-007, TP-SEC-008, TP-SEC-009, TP-SEC-010, TP-SEC-011, TP-SEC-012, TP-SEC-040,
  TP-RVFI-040

### CG-SEC-003: gen_cg_sec_double_fault
- Features: F-SEC-022, F-SEC-023, F-SEC-024, F-SEC-025, F-SEC-026
- Sample: double-fault model events: (1) sync_exc: a synchronous-exception record, rvfi_valid &&
  rvfi_trap (an ebreak that enters debug mode has rvfi_trap == 0, rtl/ibex_core.sv:1885-1886, so
  it is not a sync_exc event; the entry is event 4); (2) mret: a retired mret record; (3)
  irq_entry / nmi_entry: the first handler record (rvfi_intr == 1; nmi_entry when rvfi_ext_nmi ||
  rvfi_ext_nmi_int); (4) debug_entry: rvfi_ext_debug_mode rising on a record; (5) sw_*: a retired
  cpuctrlsts write whose legalised new value changes bit 6 or bit 7; condition: rvfi_valid &&
  (rvfi_trap || is_mret(rvfi_insn) || rvfi_intr || debug_mode_rising || cpuctrlsts_b67_write);
  anti-vacuity: each event is a distinct, infrequent record class; the seen_before / pulse fields
  come from the model state and the double_fault_seen_o monitor, so a hit proves the event met
  the detector in that state.
- Coverpoints:
  - cp_event: bins sync_exc{event 1}, mret{event 2}, irq_entry{event 3, no NMI flag},
    nmi_entry{event 3 with rvfi_ext_nmi || rvfi_ext_nmi_int}, debug_entry{event 4}, sw_set_b6{write
    sets bit 6}, sw_clr_b6{write clears bit 6}, sw_set_b7{write sets bit 7}, sw_clr_b7{write clears
    bit 7}
  - cp_seen_before = model sync_exc_seen before the event: bins clear{0}, set{1}
  - cp_pulse = double_fault_seen_o pulsed within 2 cycles of the event (the pulse is in the second
    trap's FLUSH cycle, one cycle before its record; gen_tb_architecture.md 8.2): bins yes{1}, no{0}
  - cp_debug_mode = rvfi_ext_debug_mode on the event record: bins no{0}, yes{1}
  - cp_mret_context = handler the mret returns from (model): bins exc_handler{synchronous
    exception handler}, irq_handler{interrupt handler}, nmi_handler{NMI handler}, na{not an mret}
  - cp_sticky_after = cpuctrlsts bit 7 model after the event: bins clear{0}, set{1}
  - cp_sync_exc_cause = mcause read in the handler: bins illegal{ExcCauseIllegalInsn},
    ecall{ExcCauseEcallUMode, ExcCauseEcallMMode}, ebreak{ExcCauseBreakpoint: ebreak with
    dcsr.ebreakm/ebreaku == 0}, fetch_fault{ExcCauseInstrAccessFault},
    load_fault{ExcCauseLoadAccessFault}, store_fault{ExcCauseStoreAccessFault}, na{not a sync
    exception}; ignore_bins breakpoint{trigger-caused cause 3}: retired - a trigger match always
    enters debug mode (rtl/ibex_controller.sv:476-477,519), so no trigger-caused breakpoint
    exception exists in Ibex; cause 3 is the ebreak bin
- Crosses:
  - cr_event_seen = cp_event x cp_seen_before x cp_debug_mode: sync_exc_clear_no,
    sync_exc_set_no, sync_exc_set_yes, sync_exc_clear_yes, mret_set_no, irq_entry_set_no,
    nmi_entry_set_no, debug_entry_set_no, sw_set_b6_clear_no, sw_clr_b7_set_no; ignore mret_*_yes:
    mret in debug mode is not the return path (dret is); ignore irq_entry_*_yes and
    nmi_entry_*_yes: interrupts are not taken in debug mode
  - cr_mret_ctx = cp_event x cp_mret_context: mret_exc_handler, mret_irq_handler,
    mret_nmi_handler; ignore mret_na and every non-mret event: context defined only for mret
  - cr_cause_pulse = cp_sync_exc_cause x cp_pulse: illegal_yes, ecall_yes, ebreak_yes,
    fetch_fault_yes, load_fault_yes, store_fault_yes; ignore na_*: not a sync exception
- Adopted (riscv-dv): none
- TP items: TP-SEC-021, TP-SEC-022, TP-SEC-023, TP-SEC-024, TP-SEC-025, TP-SEC-026, TP-SEC-027

### CG-SEC-004: gen_cg_sec_crash_dump
- Features: F-SEC-027, F-SEC-028, F-SEC-029, F-SEC-030
- Sample: a change of any crash_dump_o field (per-field edge), plus every trap-taken event and
  reset release (so "no change" cases in debug mode can be sampled); condition: field_changed ||
  trap_taken_event || reset_release; anti-vacuity: fields change on specific pipeline events
  only; the trigger is classified from the monitors (RVFI record, pc_set class from the ibus
  redirect, data request, CSR write record), so a hit proves the field moved for that reason.
- Coverpoints:
  - cp_field = the crash_dump_o field the sample refers to: bins current_pc, next_pc,
    last_data_addr, exception_pc, exception_addr
  - cp_trigger = classified cause of the sample: bins retire{a record retired}, pc_set_branch{jump
    or branch redirect}, pc_set_trap{synchronous exception}, pc_set_irq{interrupt or NMI},
    pc_set_debug{debug entry}, data_req{data_req_o && data_gnt_i}, csr_write{csrw mepc/mtval
    retired}, reset{rst_ni low}, boot{the BOOT_SET cycle: next_pc takes the boot vector},
    first_id{the first fetched instruction after a reset enters ID: current_pc (= pc_id) leaves
    0 for the boot vector, rtl/ibex_if_stage.sv:601, :613; fact-check TP-SEC-031}
  - cp_misaligned = the data request that moved last_data_addr: bins no{aligned access},
    first_half{first transaction of a split access}, second_half{second transaction}, na{other
    fields}
  - cp_debug_mode = rvfi_ext_debug_mode model at the event: bins no{0}, yes{1}
  - cp_changed = the field value differs from the previous sample: bins yes{1}, no{0}
  - cp_value_class = value of the field: bins zero{0}, boot_page{inside {boot_addr_i[31:8], 8'h00}
    .. + 8'hFF}, program{inside the program image}, mmio{inside the TB MMIO window}
- Crosses:
  - cr_field_trigger = cp_field x cp_trigger: current_pc_retire, current_pc_first_id,
    next_pc_pc_set_branch, next_pc_pc_set_trap, next_pc_pc_set_irq, next_pc_pc_set_debug,
    next_pc_boot, last_data_addr_data_req, last_data_addr_reset, exception_pc_pc_set_trap,
    exception_pc_pc_set_irq, exception_pc_csr_write, exception_pc_reset,
    exception_addr_pc_set_trap, exception_addr_csr_write, exception_addr_reset; ignore
    current_pc_boot: pc_id stays 0 through RESET, BOOT_SET and FIRST_FETCH and changes only on
    if_id_pipe_reg_we (rtl/ibex_if_stage.sv:601, :613; X-23), so current_pc never moves in the
    BOOT_SET cycle; ignore next_pc_first_id, last_data_addr_first_id, exception_pc_first_id and
    exception_addr_first_id: only pc_id moves at that event; ignore last_data_addr_retire, last_data_addr_pc_set_*, last_data_addr_csr_write and
    last_data_addr_boot: the LSU address moves only on requests or reset; ignore
    exception_*_data_req, exception_*_pc_set_branch, exception_*_boot and exception_*_retire:
    mepc/mtval move only on traps, CSR writes and reset; ignore current_pc_data_req and
    current_pc_csr_write: unrelated
  - cr_lda_misaligned = cp_field x cp_misaligned: last_data_addr_no, last_data_addr_first_half,
    last_data_addr_second_half; ignore every other field x {no, first_half, second_half}: n/a
  - cr_exc_debug = cp_field x cp_debug_mode x cp_changed: exception_pc_yes_no,
    exception_addr_yes_no, exception_pc_no_yes, exception_addr_no_yes; ignore
    exception_pc_yes_yes and exception_addr_yes_yes: a debug-mode exception must not move
    mepc/mtval (checker error)
- Adopted (riscv-dv): none
- TP items: TP-SEC-028, TP-SEC-029, TP-SEC-030, TP-SEC-031, TP-SEC-032

### CG-SEC-005: gen_cg_sec_ctrl_inputs
- Features: F-SEC-012, F-SEC-020, F-SEC-021, F-SEC-022, F-SEC-025, F-SEC-031, F-SEC-033, F-RST-003,
  F-RST-007, F-RST-014, F-RST-025, F-RVFI-020, F-CSR-085, F-RST-010 (parent of folded bins hosted
  here)
- Sample: cpuctrl_read: rvfi_valid of a CSR op on CSR_CPUCTRLSTS with rvfi_rd_addr != 0 and
  !rvfi_trap; fetch_en_change: a value change of fetch_enable_i; mcounteren_w_change: a value change
  of mcounteren_writable_i; key_req: an ic_scr_key_req_o pulse; key_valid_change: a change of
  ic_scr_key_valid_i; mcounteren_write: a retired write to mcounteren; boot_addr_change: a change
  of boot_addr_i after the first instr_req_o; condition: cpuctrl_read || fetch_en_change ||
  mcounteren_w_change || key_req || key_valid_change || mcounteren_write || boot_addr_change
  (cp_event names the one that fired); anti-vacuity: each event is discrete and infrequent; the
  read-back bins carry the rd value against the modelled input history, so a hit proves the read
  observed the modelled input state.
- Coverpoints:
  - cp_event: bins cpuctrl_read, fetch_en_change, mcounteren_w_change, key_req, key_valid_change,
    mcounteren_write, boot_addr_change (predicates in the Sample)
  - cp_boot_addr_change_ctx iff boot_addr_change = pipeline context at the change: bins
    running{instructions retiring}, in_handler{between a trap record and its mret},
    in_wfi{core_busy_o == IbexMuBiOff}; the effect is a checker rule (gen_isa_compare: no PC
    redirect, no mtvec change, no record inside the new boot page may follow), so there is no
    effect bin (F-RST-003, F-RST-025 folded)
  - cp_bit8_readback iff cpuctrl_read = rvfi_rd_wdata[8]: bins zero{0}, one{1}
  - cp_bits67_readback iff cpuctrl_read = rvfi_rd_wdata[7:6]: bins b6_0_b7_0{2'b00},
    b6_1_b7_0{2'b01}, b6_0_b7_1{2'b10}, b6_1_b7_1{2'b11}
  - cp_icache_en_readback_in_debug iff cpuctrl_read && rvfi_ext_debug_mode = rvfi_rd_wdata[0]:
    bins one{1}, zero{0}
  - cp_fetch_en_val iff fetch_en_change = new fetch_enable_i: bins on{IbexMuBiOn},
    off{IbexMuBiOff}, invalid{every other ibex_mubi_t value: 2**IbexMuBiWidth - 2 encodings}
  - cp_mcounteren_w_val iff mcounteren_write = mcounteren_writable_i at the write: bins
    on{IbexMuBiOn}, off{IbexMuBiOff}, invalid{every other ibex_mubi_t value}
  - cp_mcounteren_write_effect iff mcounteren_write = read-back after the write: bins
    applied{value changed to the legalised write data}, dropped{unchanged}
  - cp_key_delay = knob:scr_key_delay value in force (cross operand only; knob bins owned by
    fcov_xcut.md CG-REG): bins immediate, delayed, withheld_then_valid
  - cp_key_req_context iff key_req = why the cache requested a key: bins reset_inval{the reset
    invalidation sweep}, fence_i{a retired fence.i}, debug_mode{request while rvfi_ext_debug_mode
    model == 1}, icache_disabled{request while icache_enable == 0 (cfg tracked)}
  - cp_rvfi_ext_key_valid iff cpuctrl_read = rvfi_ext_ic_scr_key_valid on the read record: bins
    zero{0}, one{1}
  - (retired: cp_bit8_vs_input - "rd[8] == ic_scr_key_valid_i delayed by one cycle" is the
    gen_chk_csr_readback rule, not a bin)
- Crosses:
  - cr_mcounteren = cp_mcounteren_w_val x cp_mcounteren_write_effect: on_applied, off_dropped,
    invalid_dropped; ignore on_dropped, off_applied and invalid_applied: checker errors, not
    coverage
  - cr_key = cp_key_delay x cp_bit8_readback: immediate_one, delayed_zero, delayed_one,
    withheld_then_valid_zero, withheld_then_valid_one; ignore immediate_zero: with an immediate
    responder the valid never drops long enough for a read to see 0 (if the poll loop does hit
    it, promote to a bin)
  - cr_key_ctx = cp_key_req_context x cp_key_delay: reset_inval_immediate, fence_i_delayed,
    fence_i_withheld_then_valid, reset_inval_withheld_then_valid, fence_i_immediate,
    reset_inval_delayed, debug_mode_delayed, icache_disabled_immediate
- Adopted (riscv-dv): none
- TP items: TP-SEC-016, TP-SEC-019, TP-SEC-020, TP-SEC-021, TP-SEC-022, TP-SEC-026, TP-SEC-033,
  TP-SEC-034, TP-RST-004, TP-RST-007, TP-RVFI-023

### CG-SEC-006: gen_cg_sec_core_busy
- Features: F-SEC-014, F-RST-016, F-RST-017, F-RVFI-028, F-DIT-028
- Sample: (a) wfi_txn: the close of a WFI transaction - a retired WFI record, closed when
  core_busy_o is On again after its Off period, or at the next retirement when it never went Off;
  the transaction carries the Off duration, the hold / pass-through cause and the wake source;
  (b) busy_change: a change of core_busy_o outside a WFI transaction (boot, debug entry, fetch
  holds); condition: wfi_txn_close || (core_busy_o != core_busy_o_prev && !in_wfi_txn);
  anti-vacuity: WFI transactions and busy changes are rare; the causes are derived from the bus
  monitors and pins (rtl/ibex_core.sv:521: core_busy_o == Off iff ctrl, IF and LSU are all idle;
  gen_tb_architecture.md 8.2 item 1), so a hit proves the busy value coincided with the named cause.
- Coverpoints:
  - cp_event: bins wfi_txn{wfi_txn_close}, busy_change{core_busy_o changed outside a WFI
    transaction}
  - cp_value = core_busy_o at the sample: bins on{IbexMuBiOn}, off{IbexMuBiOff}; every other value
    is a gen_chk_sleep error, deliberately not a bin
  - cp_transition = {previous, new} iff busy_change: bins on2off{IbexMuBiOn -> IbexMuBiOff},
    off2on{IbexMuBiOff -> IbexMuBiOn}
  - cp_off_reason iff wfi_txn = Off duration class of the transaction: bins wfi_sleep{Off for
    more than one cycle: SLEEP with no wake source}, wait_sleep{Off for exactly the WAIT_SLEEP
    cycle: a source already pending, dcsr.step set or debug mode makes SLEEP leave at once,
    rtl/ibex_controller.sv:598-621}, none{never Off: an ibus beat, a data response or the
    invalidation sweep kept if_busy / lsu_busy high through WAIT_SLEEP and SLEEP}
  - cp_hold_cause iff wfi_txn && cp_off_reason == none = why Off was invisible: bins
    fetch_outstanding{ibus beats not returned}, lsu_outstanding{data response pending},
    inval_active{reset invalidation sweep still running}
  - cp_pass_cause iff wfi_txn && cp_off_reason == wait_sleep = why SLEEP was left at once: bins
    irq_pending{irq_pending_o == 1}, nmi_pending{irq_nm_i == 1}, debug_req{debug_req_i == 1},
    debug_mode{WFI executed in debug mode}, step{dcsr.step model == 1}
  - cp_wake_source iff wfi_txn && cp_off_reason == wfi_sleep = input that ended the Off period:
    bins irq{an enabled irq line rose}, nmi{irq_nm_i rose}, debug_req{debug_req_i rose}
  - cp_priv_at_wfi iff wfi_txn = rvfi_mode of the WFI record: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_mie_at_wfi iff wfi_txn = mstatus.MIE model at the WFI: bins set{1}, clear{0}
- Crosses:
  - cr_wake = cp_off_reason x cp_wake_source: wfi_sleep_irq, wfi_sleep_nmi, wfi_sleep_debug_req
    (cp_wake_source is sampled only for wfi_sleep, so no other combination exists)
  - cr_pass = cp_off_reason x cp_pass_cause: wait_sleep_irq_pending, wait_sleep_nmi_pending,
    wait_sleep_debug_req, wait_sleep_debug_mode, wait_sleep_step (cp_pass_cause is sampled only
    for wait_sleep)
  - cr_hold = cp_off_reason x cp_hold_cause: none_fetch_outstanding, none_lsu_outstanding,
    none_inval_active (cp_hold_cause is sampled only for none)
  - cr_wfi_mie = cp_off_reason x cp_mie_at_wfi x cp_priv_at_wfi: wfi_sleep_set_m,
    wfi_sleep_clear_m, wfi_sleep_set_u, wfi_sleep_clear_u, wait_sleep_set_m; no ignores (U-mode
    WFI with TW = 0 sleeps like M-mode; the none_* and remaining wait_sleep_* combinations are
    reachable and left unrequired)
- Adopted (riscv-dv): none
- TP items: TP-DIT-030, TP-SEC-018, TP-RST-008, TP-RST-015, TP-RST-016, TP-RVFI-031

---------------------------------------------------------------------------------------------------
## RST
---------------------------------------------------------------------------------------------------

### CG-RST-001: gen_cg_rst_boot
- Features: F-RST-002, F-RST-003, F-RST-004, F-RST-005, F-RST-006, F-RST-008, F-RST-009,
  F-RST-013, F-RST-024, F-RST-025, F-RST-026, F-SEC-037
- Sample: rst_ni release, closed when the first post-reset event is classified (first retired
  record, NMI entry, debug entry, or a timeout with fetch disabled); condition:
  reset_release_event; anti-vacuity: one sample per reset; the fields are observed from the ibus
  monitor and RVFI after the release (first request address, first record's order and mode), so a
  hit proves the boot proceeded as classified.
- Coverpoints:
  - cp_boot_addr = boot_addr_i[31:8] class: bins zero{0}, low{[1:24'h0FFFFF]},
    mid{[24'h100000:24'h7FFFFF]}, high{[24'h800000:24'hFFFFFF]}
  - cp_boot_low_byte = boot_addr_i[7:0]: bins zero{0}; ignore_bins nonzero{[1:255]}: the RTL
    assertion IbexBootAddrUnaligned forbids it (TB never drives it)
  - cp_fetch_en_at_release = fetch_enable_i in the release cycle: bins on{IbexMuBiOn},
    off{IbexMuBiOff}, invalid{every other ibex_mubi_t value}
  - cp_pending = inputs pending at release: bins none{no irq, NMI or debug request high},
    irq_enabled_later{an irq line high, mie still 0}, nmi{irq_nm_i}, debug_req{debug_req_i},
    nmi_and_debug{irq_nm_i && debug_req_i}, irq_and_debug{an irq line && debug_req_i}
  - cp_first_event: bins first_instr_retire{first rvfi_valid with rvfi_intr == 0 and
    rvfi_ext_debug_mode == 0}, nmi_taken{first record has rvfi_intr && rvfi_ext_nmi},
    debug_entry{first record has rvfi_ext_debug_mode == 1}, none_fetch_disabled{no event within
    the window because fetch stayed disabled}; ignore_bins irq_taken{first record has rvfi_intr
    without an NMI flag}: mstatus.MIE and mie are 0 at reset so a maskable interrupt can never be
    the first event
  - cp_hart_id = hart_id_i: bins zero{0}, max{32'hFFFFFFFF}, random{every other value}
  - cp_reset_kind: bins power_on{first reset of the simulation}, mid_run{a reset after at least
    one retired record}
  - cp_boot_to_req_cycles = cycles from release to the first instr_req_o: bins two{2}, three{3},
    more{[4:$]}; ignore_bins fewer{[0:1]}: the RESET state never requests
  - (retired: cp_first_fetch_addr_match and cp_first_order_one - checker mirrors of the cocotb
    first-request assertion and of gen_chk_rvfi_proto; the boot vector is carried by cp_boot_addr
    x cp_reset_kind and the order by CG-RVFI-001.cp_order_step.first)
- Crosses:
  - cr_pending_first = cp_pending x cp_first_event: none_first_instr_retire,
    irq_enabled_later_first_instr_retire, nmi_nmi_taken, debug_req_debug_entry,
    nmi_and_debug_debug_entry, irq_and_debug_debug_entry; ignore *_irq_taken: excluded through
    the cp_first_event ignore; ignore nmi_first_instr_retire, debug_req_first_instr_retire,
    nmi_and_debug_first_instr_retire and irq_and_debug_first_instr_retire: a pending NMI or debug
    request is taken from FIRST_FETCH before any retirement; ignore debug_req_nmi_taken,
    irq_and_debug_nmi_taken and nmi_and_debug_nmi_taken: debug entry has priority over the NMI
    (rtl/ibex_controller.sv:474-477), so the NMI is taken after dret and is never the first
    event; ignore nmi_debug_entry, irq_enabled_later_debug_entry, none_debug_entry,
    irq_enabled_later_nmi_taken and none_nmi_taken: nothing of that kind was pending; ignore
    *_none_fetch_disabled: the fetch-disabled release is covered by cr_fetch_en_first
  - cr_fetch_en_first = cp_fetch_en_at_release x cp_first_event: on_first_instr_retire,
    off_none_fetch_disabled, invalid_none_fetch_disabled, off_first_instr_retire{fetch enabled
    later}; ignore on_none_fetch_disabled: fetch enabled means an event must occur
  - cr_boot_kind = cp_boot_addr x cp_reset_kind: zero_power_on, low_power_on, mid_power_on,
    high_power_on, zero_mid_run, low_mid_run, mid_mid_run, high_mid_run
- Adopted (riscv-dv): none
- TP items: TP-SEC-038, TP-RST-001, TP-RST-002, TP-RST-003, TP-RST-004, TP-RST-005, TP-RST-006,
  TP-RST-008, TP-RST-012, TP-RST-017, TP-RST-024, TP-RST-025, TP-RST-026, TP-RST-029, TP-RVFI-036

### CG-RST-002: gen_cg_rst_midrun
- Features: F-RST-001, F-RST-009, F-RST-018, F-RST-019, F-SEC-035, F-RVFI-033
- Sample: falling edge of rst_ni after the first instruction retired (mid-run reset) and the
  power-on reset release, closed when the post-reset response window (16 cycles) has elapsed;
  condition: reset_assert_event || power_on_release; anti-vacuity: at most a few samples per
  run; the in-flight class comes from the monitors' state at the edge and the post-response
  class from beats actually returned after release, so a hit proves the reset interrupted that
  activity.
- Coverpoints:
  - cp_inflight = DUT activity at the reset edge: bins idle{no request outstanding, pipe empty},
    fetch_outstanding{>= 1 ibus beat granted and not returned}, load_outstanding{a load response
    pending}, store_outstanding{a store response pending}, misaligned_first_done{first half of a
    split access done, second pending}, div_in_flight{a divide record not yet retired},
    zcmp_mid{expanded_insn_valid seen without last}, in_wfi{core_busy_o == IbexMuBiOff},
    in_debug{rvfi_ext_debug_mode model == 1}, in_exc_handler{between a trap record and its mret},
    in_irq_handler{between an irq entry and its mret}, in_nmi_handler{between an NMI entry and
    its mret}, fetch_disabled{fetch_enable_i != IbexMuBiOn}, dummy_in_id{P1: dummy_instr_id_o == 1}
  - cp_reset_len = cycles rst_ni held low: bins one_cycle{1}, short{[2:9]}, long{[10:$]}
  - cp_post_response = beats for pre-reset requests DRAINED by the memory models while rst_ni = 0
    (never after release: a post-release late beat is taken by the DUT as the answer to its new
    request, rtl/ibex_icache.sv:851-852, rtl/ibex_load_store_unit.sv:694-698, and is the
    out-of-spec S3 stimulus owned by TP-IMEM-040 / TP-SEC-010; fact-check TP-RST-017): bins
    none{0 beats drained (all dropped)}, good_intg{>= 1 beat drained, all check bits valid},
    bad_intg{>= 1 beat drained with corrupted check bits (alert_major_bus_o follows it in reset,
    TP-SEC-036)}
  - cp_outstanding_count = granted-but-unanswered bus beats at the edge (both sides): bins
    zero{0}, one{1}, two{2}, many{[3:$]}
  - (retired: cp_alert_during_reset - owned by CG-SEC-001.cr_window (reset_close_none /
    reset_close_major_bus with the activity qualifier); cp_outputs_at_reset_ok - checker mirror of
    gen_test_rst_values)
- Crosses:
  - cr_inflight_resp = cp_inflight x cp_post_response: idle_none, fetch_outstanding_good_intg,
    fetch_outstanding_bad_intg, load_outstanding_good_intg, load_outstanding_bad_intg,
    store_outstanding_good_intg, store_outstanding_bad_intg, misaligned_first_done_none,
    misaligned_first_done_good_intg; ignore idle_good_intg and idle_bad_intg: nothing outstanding
    can return; ignore in_wfi_*, in_debug_*, in_*_handler_*, fetch_disabled_*, div_in_flight_*,
    zcmp_mid_* and dummy_in_id_* with good_intg / bad_intg: the response class of those states is
    tracked through cp_outstanding_count instead
  - cr_inflight_len = cp_inflight x cp_reset_len: div_in_flight_one_cycle, div_in_flight_short,
    zcmp_mid_short, in_wfi_long, in_wfi_short, in_debug_short, in_irq_handler_short,
    in_nmi_handler_short, in_exc_handler_short, dummy_in_id_short, fetch_disabled_short,
    idle_long
- Adopted (riscv-dv): none
- TP items: TP-SEC-036, TP-RST-017, TP-RST-018, TP-RST-019, TP-RST-029

### CG-RST-003: gen_cg_rst_fetch_enable
- Features: F-RST-010, F-RST-011, F-RST-012, F-RST-014, F-RST-015, F-SEC-012, F-DIT-028
- Sample: a value change of fetch_enable_i while rst_ni == 1, closed when the value changes again
  (hold length known) and the retirements after the edge have been counted; condition:
  fetch_enable_i != fetch_enable_i_prev && rst_ni; anti-vacuity: the input is static in most runs
  (knob:fetch_enable_regime always_on gives zero samples); the pipe state comes from the RVFI and
  bus monitors at the edge, so a hit proves the transition interrupted that state.
- Coverpoints:
  - cp_transition = {old class, new class} with classes on = IbexMuBiOn, off = IbexMuBiOff, inv =
    any other ibex_mubi_t value: bins on2off, off2on, on2inv, inv2on, off2inv, inv2off,
    inv2inv{two different invalid values}
  - cp_hold_len = cycles until the next change: bins one_cycle{1}, short{[2:49]}, long{[50:$]}
  - cp_pipe_state = at the edge: bins empty{no instruction in ID or WB}, id_busy{instruction in
    ID}, wb_load_outstanding{load in WB, response pending}, wb_store_outstanding{store in WB,
    response pending}, misaligned_mid{first half of a split access done}, div_in_flight{divide in
    ID}, in_wfi{core_busy_o == IbexMuBiOff}, in_debug{rvfi_ext_debug_mode model == 1},
    in_handler{between a trap/irq record and its mret}
  - cp_event_during_off = input event while not On: bins none{no event}, irq{an enabled irq
    line}, nmi{irq_nm_i}, debug_req{debug_req_i}
  - cp_retire_after_off = records retired after a *2off / *2inv edge: bins zero{0}, one{1},
    two{2}; ignore_bins more{[3:$]}: the pipeline holds at most ID and WB (checker error if seen;
    Zcmp micro-ops of the instruction in ID are counted as one)
  - cp_invalid_value = the invalid encoding driven: bins all_zero{'0}, all_one{'1 (IbexMuBiWidth
    ones)}, other_invalid{the remaining 2**IbexMuBiWidth - 4 values}
  - (retired: cp_resume_pc_continuous - checker mirror of gen_chk_rvfi_proto pc continuity)
- Crosses:
  - cr_trans_pipe = cp_transition x cp_pipe_state: on2off_empty, on2off_id_busy,
    on2off_wb_load_outstanding, on2off_wb_store_outstanding, on2off_misaligned_mid,
    on2off_div_in_flight, on2off_in_wfi, on2off_in_debug, on2off_in_handler, on2inv_id_busy,
    on2inv_empty; ignore off2on_*, inv2on_*, off2inv_*, inv2off_* and inv2inv_* with id_busy,
    wb_load_outstanding, wb_store_outstanding, misaligned_mid or div_in_flight: the pipe drains
    while fetch is off, so a re-enable edge sees an empty pipe or a WFI/debug/handler context only
  - cr_off_event = cp_transition x cp_event_during_off: on2off_irq, on2off_nmi,
    on2off_debug_req, on2inv_irq, on2inv_debug_req, on2off_none; ignore off2on_* and inv2on_*:
    events during the Off period are attributed to the edge that started it
  - cr_glitch = cp_transition x cp_hold_len: on2off_one_cycle, on2inv_one_cycle, on2off_short,
    on2off_long, off2on_short, off2on_long, inv2on_short
- Adopted (riscv-dv): none
- TP items: TP-DIT-030, TP-SEC-016, TP-RST-009, TP-RST-010, TP-RST-011, TP-RST-013, TP-RST-014,
  TP-RST-029

### CG-RST-004: gen_cg_rst_regfile
- Features: F-RST-021, F-RST-022, F-RST-023, F-DIT-015, F-SEC-005, F-SEC-004 (parent of folded bins
  hosted here)
- Sample: rvfi_valid with rvfi_trap == 0 and a register-reading or register-writing format;
  condition: rvfi_valid && !rvfi_trap && (rvfi_rs1_addr != 0 || rvfi_rs2_addr != 0 || rvfi_rd_addr
  != 0 || reads_x0_explicitly(rvfi_insn)); anti-vacuity: register traffic is frequent, but the
  interesting bins (unwritten read, same-cycle forward, dummy-adjacent) depend on TB state
  (written-set model, previous record, P1) so they prove the scenario rather than the record.
- Coverpoints:
  - cp_rs1_bank = rvfi_rs1_addr: bins x0{0}, x1_15{[1:15]}, x16{16}, x17_31{[17:31]}
  - cp_rs2_bank = rvfi_rs2_addr: bins x0{0}, x1_15{[1:15]}, x16{16}, x17_31{[17:31]}
  - cp_rd_bank = rvfi_rd_addr: bins none{0}, x1_15{[1:15]}, x16{16}, x17_31{[17:31]}
  - cp_read_unwritten = rs1 or rs2 register never written since the last reset (model): bins
    yes{1}, no{0}
  - cp_fwd_same_cycle = rs1 or rs2 addr == rd addr of the previous record and gap == 1: bins
    yes{1: ALU / CSR / mul / div producer forwarded from the WB flop, rtl/ibex_wb_stage.sv:215},
    no{0: no dependency, or a LOAD producer, whose result is never forwarded (:212-215): the
    consumer stalls on stall_ld_hz and the pair has gap 2, fact-check TP-RST-023}
  - cp_dummy_adjacent (P1) = a dummy_instr_wb_o pulse in the cycle before or after this record's
    RF write: bins yes{1}, no{0}
- Crosses:
  - cr_fwd_bank = cp_fwd_same_cycle x cp_rs1_bank: yes_x1_15, yes_x16, yes_x17_31; ignore
    yes_x0: x0 is never forwarded (raddr != 0 term); ignore no_*: not the scenario
  - cr_unwritten_bank = cp_read_unwritten x cp_rs1_bank: yes_x1_15, yes_x16, yes_x17_31; ignore
    yes_x0: x0 is not a written register; ignore no_*: not the scenario
  - cr_rd_bank_dummy = cp_rd_bank x cp_dummy_adjacent (P1): x1_15_yes, x16_yes, x17_31_yes;
    ignore none_*: no RF write to be adjacent to
- Adopted (riscv-dv): none
- TP items: TP-DIT-016, TP-SEC-013, TP-RST-021, TP-RST-022, TP-RST-023, TP-RVFI-008

---------------------------------------------------------------------------------------------------
## RVFI
---------------------------------------------------------------------------------------------------

### CG-RVFI-001: gen_cg_rvfi_record
- Features: F-RVFI-001, F-RVFI-002, F-RVFI-003, F-RVFI-004, F-RVFI-005, F-RVFI-006, F-RVFI-007,
  F-RVFI-008, F-RVFI-009, F-RVFI-010, F-RVFI-024, F-RVFI-027, F-RVFI-028, F-RVFI-029, F-RVFI-034,
  F-RST-006, F-RST-026, F-DIT-016, F-DIT-017, F-SEC-008, F-SEC-007 (parent of folded bins hosted
  here)
- Sample: every rvfi_valid; condition: rvfi_valid; anti-vacuity: rvfi_valid is a pulse (one
  cycle per retired instruction, never continuous), and every coverpoint is a property of the
  record relative to the previous one (continuity, order, gap) or a discriminating record class,
  so the bins prove inter-record relations and record classes, not the mere existence of a
  record. Constant fields (rvfi_ixl == 1, rvfi_halt == 0) and "order advanced by one" are
  gen_chk_rvfi_proto rules, not bins (retired: cp_ixl, cp_halt, cp_order_step.one). This group
  OWNS cp_trap; the cp_trap copies in CG-RVFI-002/003 and CG-CHERI-001 are cross operands only.
- Coverpoints:
  - cp_trap = rvfi_trap: bins no{0}, yes{1}
  - cp_intr = rvfi_intr: bins no{0}, yes{1}
  - cp_mode = rvfi_mode: bins u{PRIV_LVL_U}, m{PRIV_LVL_M}; ignore_bins other{PRIV_LVL_H,
    PRIV_LVL_S}: not implemented (checker error if seen)
  - cp_insn_kind: bins c16{rvfi_insn[1:0] != 2'b11 && !rvfi_ext_expanded_insn_valid},
    i32{rvfi_insn[1:0] == 2'b11 && !rvfi_ext_expanded_insn_valid},
    zcmp_uop{rvfi_ext_expanded_insn_valid}
  - cp_rd = rvfi_rd_addr: bins x0{0}, nonzero{[1:31]}
  - cp_rs1 = rvfi_rs1_addr: bins x0{0}, nonzero{[1:31]}
  - cp_rs2 = rvfi_rs2_addr: bins x0{0}, nonzero{[1:31]}
  - cp_rs3 = rvfi_rs3_addr: bins zero{0}, nonzero{[1:31]}
  - cp_pc_delta = rvfi_pc_wdata - rvfi_pc_rdata: bins plus2{2}, plus4{4}, jump_fwd{> 4 on a
    non-redirect record}, jump_back{negative on a non-redirect record}, redirect_other{record is a
    trap, mret, dret or fence.i}
  - cp_order_step: bins first{rvfi_order == 1 on the first record after a reset}; "order ==
    previous + 1" on every other record is the gen_chk_rvfi_proto rule (a gap or repeat is a
    checker error, not a bin)
  - cp_pc_continuity = relation of rvfi_pc_rdata to the previous record's rvfi_pc_wdata: bins
    continuous{equal}, discontinuous_intr{rvfi_intr on this record},
    discontinuous_after_trap{previous record had rvfi_trap},
    discontinuous_after_flush_redirect{previous record was mret/dret/fence.i},
    discontinuous_debug{debug entry or dret between the records: rvfi_ext_debug_mode changed};
    any other discontinuity is a checker error
  - cp_valid_gap = cycles since the previous rvfi_valid: bins g1{1}, g2{2}, g3_plus{[3:$]}
  - cp_intr_kind = entry class of the record: bins irq{rvfi_intr && rvfi_ext_pre_mip != 0 &&
    !rvfi_ext_nmi && !rvfi_ext_nmi_int}, nmi{rvfi_intr && rvfi_ext_nmi}, nmi_int{rvfi_intr &&
    rvfi_ext_nmi_int}, none{!rvfi_intr}
  - cp_rd_source = source of the rd write on this record: bins alu_wb{rvfi_rd_addr != 0 and the
    instruction is not a load: WB-flop source}, load_lsu{rvfi_rd_addr != 0 and the instruction is
    a load: LSU return source}, none{rvfi_rd_addr == 0}; a record whose class implies a write but
    shows rd_addr == 0 (or the converse) is a gen_chk_rvfi_proto error, not a bin (F-RVFI-034)
- Crosses:
  - cr_kind_trap = cp_insn_kind x cp_trap: c16_no, c16_yes, i32_no, i32_yes, zcmp_uop_no,
    zcmp_uop_yes
  - cr_rd_source_kind = cp_rd_source x cp_insn_kind: alu_wb_i32, alu_wb_c16, alu_wb_zcmp_uop
    (cm.mv* / cm.pop register writes), load_lsu_i32, load_lsu_c16, load_lsu_zcmp_uop (cm.pop
    loads), none_i32, none_c16, none_zcmp_uop (cm.push stores) (F-RVFI-034)
  - cr_mode_trap = cp_mode x cp_trap: u_yes, m_yes, u_no, m_no
  - cr_intr_cont = cp_intr x cp_pc_continuity: yes_discontinuous_intr, no_continuous,
    no_discontinuous_after_trap, no_discontinuous_after_flush_redirect, no_discontinuous_debug;
    ignore yes_continuous, yes_discontinuous_after_trap, yes_discontinuous_after_flush_redirect
    and yes_discontinuous_debug: an interrupt entry is classified as discontinuous_intr first
  - cr_rd_kind = cp_rd x cp_insn_kind x cp_trap: x0_i32_yes, x0_c16_yes, x0_zcmp_uop_yes,
    nonzero_i32_no, nonzero_c16_no, nonzero_zcmp_uop_no, x0_i32_no, x0_c16_no; ignore
    nonzero_*_yes: rd is forced to 0 on a trap record (checker error if seen)
- Adopted (riscv-dv): none
- TP items: TP-DIT-016, TP-DIT-017, TP-DIT-018, TP-DIT-020, TP-DIT-034, TP-SEC-005, TP-RST-006,
  TP-RST-027, TP-RVFI-001, TP-RVFI-002, TP-RVFI-003, TP-RVFI-004, TP-RVFI-005, TP-RVFI-006,
  TP-RVFI-007, TP-RVFI-008, TP-RVFI-009, TP-RVFI-010, TP-RVFI-011, TP-RVFI-012, TP-RVFI-013,
  TP-RVFI-014, TP-RVFI-016, TP-RVFI-025, TP-RVFI-026, TP-RVFI-027, TP-RVFI-030, TP-RVFI-031,
  TP-RVFI-032, TP-RVFI-037, TP-RVFI-038, TP-CHERI-001, TP-CHERI-004

### CG-RVFI-002: gen_cg_rvfi_mem
- Features: F-RVFI-011, F-RVFI-012, F-RVFI-013, F-RVFI-014, F-RVFI-021, F-DIT-008
- Sample: rvfi_valid where the instruction is a load or store (decoded from rvfi_insn, so trap
  records with zeroed masks are included); condition: rvfi_valid && is_load_store(rvfi_insn);
  anti-vacuity: only memory instructions sample; offset/misaligned/fault-half come from
  rvfi_mem_addr and the dbus monitor's transaction record, so a hit proves the access shape.
- Coverpoints:
  - cp_dir: bins load{is_load(rvfi_insn)}, store{is_store(rvfi_insn)}
  - cp_size = funct3 size: bins byte{lb/lbu/sb}, half{lh/lhu/sh}, word{lw/sw}
  - cp_offset = rvfi_mem_addr[1:0]: bins o0{0}, o1{1}, o2{2}, o3{3}
  - cp_misaligned = (half && addr[0]) || (word && addr[1:0] != 0): bins no{0}, yes{1}
  - cp_trap = rvfi_trap (cross operand only; owner CG-RVFI-001.cp_trap): bins no{0}, yes{1}
  - cp_fault_half = which half of the access faulted: from the dbus monitor for a bus error (the
    errored transaction) and from the TB PMP model for a PMP fault (a PMP-denied second half never
    reaches the bus: data_req_o = data_req_out & ~pmp_req_err[PMP_D], rtl/ibex_core.sv:1063;
    fact-check TP-RVFI-017): bins none{no fault}, first{first half}, second{second half of a
    split access}
  - cp_signed = lb/lh vs lbu/lhu: bins signed{lb, lh}, unsigned{lbu, lhu}, na{word or store}
  - cp_rdata_ext = upper bits of rvfi_mem_rdata for byte/half loads: bins sign_ext_ones{signed
    load, loaded sign bit 1, upper bits all 1}, sign_ext_zeros{signed load, loaded sign bit 0,
    upper bits all 0}, zero_ext{unsigned load, upper bits 0}, na{word or store}
  - cp_mask_val = the nonzero one of rmask/wmask (or 0): bins m0000{0}, m0001{1}, m0011{3},
    m1111{15}; any other value is a checker error
  - (retired: cp_rf_wr_suppress - owned by CG-RVFI-003.cp_rf_wr_suppress)
- Crosses:
  - cr_dir_size_off = cp_dir x cp_size x cp_offset: load_byte_o0, load_byte_o1, load_byte_o2,
    load_byte_o3, load_half_o0, load_half_o1, load_half_o2, load_half_o3, load_word_o0,
    load_word_o1, load_word_o2, load_word_o3, store_byte_o0, store_byte_o1, store_byte_o2,
    store_byte_o3, store_half_o0, store_half_o1, store_half_o2, store_half_o3, store_word_o0,
    store_word_o1, store_word_o2, store_word_o3 (all 24 reachable: Ibex supports misaligned
    accesses)
  - cr_trap_half = cp_dir x cp_trap x cp_fault_half: load_yes_none{aligned or first-transaction
    fault on a non-split access}, load_yes_first, load_yes_second, store_yes_none,
    store_yes_first, store_yes_second, load_no_none, store_no_none; ignore load_no_first,
    load_no_second, store_no_first and store_no_second: a faulting transaction always traps
  - cr_mask_trap = cp_mask_val x cp_trap: m0000_yes, m0001_no, m0011_no, m1111_no; ignore
    m0000_no: a non-trapping memory record always carries a mask; ignore m0001_yes, m0011_yes and
    m1111_yes: masks are forced to 0 on trap records
  - cr_ext = cp_size x cp_signed x cp_rdata_ext iff cp_dir == load: byte_signed_sign_ext_ones,
    byte_signed_sign_ext_zeros, byte_unsigned_zero_ext, half_signed_sign_ext_ones,
    half_signed_sign_ext_zeros, half_unsigned_zero_ext; ignore word_*_*, *_na_* and *_*_na: no
    extension applies to a word load; ignore *_unsigned_sign_ext_ones and *_unsigned_sign_ext_zeros:
    zero-extension never classes as sign extension; ignore *_signed_zero_ext: a signed load is
    classed sign_ext_ones or sign_ext_zeros by construction
- Adopted (riscv-dv): none
- TP items: TP-DIT-009, TP-RVFI-014, TP-RVFI-015, TP-RVFI-016, TP-RVFI-017, TP-RVFI-037

### CG-RVFI-003: gen_cg_rvfi_ext
- Features: F-RVFI-016, F-RVFI-017, F-RVFI-018, F-RVFI-019, F-RVFI-020, F-RVFI-021, F-RVFI-022,
  F-RVFI-023, F-RVFI-031, F-RVFI-032, F-SEC-009, F-SEC-015, F-DIT-020
- Sample: a retired record or an interrupt notification, the latter sampled once at the RISING
  edge of rvfi_ext_irq_valid (a level, C-13 / X-16: it rises at decision + 4 and stays high until
  about two cycles after the handler's first instruction enters ID); condition: rvfi_valid ||
  (rvfi_ext_irq_valid && !rvfi_ext_irq_valid_prev); anti-vacuity: rvfi_valid is a pulse and the
  marker's rising edge is one per notification; the pre_mip bins require exactly one line set on
  a record (the TB drives lines so this happens), so a hit proves the field carried the intended
  value. The rvfi_ext_pre_mip / nmi / nmi_int / debug_req fields are valid on both events
  (records and notifications); the other fields are record fields and carry iff rvfi_valid.
- Coverpoints:
  - cp_irq_valid = rvfi_ext_irq_valid at the sample: bins no{0: a record}, yes{1: a marker
    rising edge}
  - cp_collision = rvfi_valid && rvfi_ext_irq_valid: bins no{0}; ignore_bins yes{1}: unreachable
    on this RTL (the decision needs ~instr_valid_id & ready_wb, the last pre-interrupt record is
    out by decision + 1 and the marker rises at decision + 4; rtl/ibex_core.sv:1965-1971,
    :1985-2004, :2192-2198; fact-check TP-RVFI-035): a hit is the T-044 sva_rvfi_irq_valid_exclusive
    checker error, not coverage
  - cp_marker_len iff cp_irq_valid == yes = consecutive high cycles of rvfi_ext_irq_valid from
    this rising edge: bins one{1: same-cycle gnt and next-cycle rvalid on the handler fetch},
    two_plus{[2:$]: stage [0] is rewritten only when the handler's first instruction enters ID,
    rtl/ibex_core.sv:1991-1992}
  - cp_marker_offset iff cp_irq_valid == yes = cycles from the last pre-interrupt record's
    rvfi_valid to this rising edge: bins min{GEN_RVFI_IRQ_MARKER_OFFSET (predicted 3; the value
    is pinned at bring-up, C-16)}, more{[GEN_RVFI_IRQ_MARKER_OFFSET+1:$]: the last record retired
    earlier than decision + 1}; ignore_bins less{[0:GEN_RVFI_IRQ_MARKER_OFFSET-1]}: would mean a
    record inside the marker window (X-16; checker error)
  - cp_entry_marker iff rvfi_valid && rvfi_intr = a marker rising edge was seen since the
    previous record: bins yes{1}, no{0: ID emptied before WB drained, captured_valid was already
    set when ready_wb came and no marker was generated, rtl/ibex_core.sv:1965; the handler's
    first record carries the captured state}
  - cp_nmi = rvfi_ext_nmi: bins no{0}, yes{1}
  - cp_nmi_int = rvfi_ext_nmi_int: bins no{0}, yes{1}
  - cp_debug_req = rvfi_ext_debug_req: bins no{0}, yes{1}
  - cp_debug_mode = rvfi_ext_debug_mode iff rvfi_valid: bins no{0}, yes{1}
  - cp_rf_wr_suppress = rvfi_ext_rf_wr_suppress iff rvfi_valid: bins no{0}, yes{1}
  - cp_pre_mip_line = rvfi_ext_pre_mip decoded: bins none{0}, sw{bit 3 only}, timer{bit 7 only},
    ext{bit 11 only}, fast[0]{bit 16 only}, fast[1]{bit 17 only}, fast[2]{bit 18 only}, fast[3]{bit 19
    only}, fast[4]{bit 20 only}, fast[5]{bit 21 only}, fast[6]{bit 22 only}, fast[7]{bit 23 only},
    fast[8]{bit 24 only}, fast[9]{bit 25 only}, fast[10]{bit 26 only}, fast[11]{bit 27 only},
    fast[12]{bit 28 only}, fast[13]{bit 29 only}, fast[14]{bit 30 only} (one bin per fast line, i =
    0..$bits(irq_fast_i)-1 at bit 16+i), multi{more than one bit set}; ignore_bins other_bits{any
    bit outside {3, 7, 11, 16..16+$bits(irq_fast_i)-1}}: never driven by the RTL (checker error if
    seen)
  - cp_post_mip_diff = rvfi_ext_post_mip != rvfi_ext_pre_mip: bins same{0}, changed{1}
  - cp_expanded = Zcmp position iff rvfi_valid: bins none{!rvfi_ext_expanded_insn_valid},
    first{valid, first micro-op of a sequence}, mid{valid, neither first nor last},
    last{rvfi_ext_expanded_insn_last}
  - cp_trap = rvfi_trap (cross operand only; owner CG-RVFI-001.cp_trap) iff rvfi_valid: bins
    no{0}, yes{1}
  - cp_hpm_index iff rvfi_valid = index i in 0..MHPMCounterNum-1 whose rvfi_ext_mhpmcounters[i]
    is nonzero on this record (one sample per nonzero index): bins i0{0}, i1{1}, i2{2}, i3{3},
    i4{4}, i5{5}, i6{6}, i7{7}, i8{8}, i9{9} (MHPMCounterNum = 10 bins)
  - cp_key_valid = rvfi_ext_ic_scr_key_valid iff rvfi_valid: bins zero{0}, one{1}
  - (retired: cp_mcycle_monotonic - "rvfi_ext_mcycle increases" is a gen_chk_counters rule on
    every record, not a bin)
- Crosses:
  - cr_irq_collision = cp_irq_valid x cp_collision: yes_no{a marker rising edge with no record in
    that cycle}, no_no{a record with the marker low}; ignore yes_yes and no_yes: cp_collision.yes
    is unreachable (see the coverpoint)
  - cr_irq_kind = cp_irq_valid x cp_nmi x cp_nmi_int: yes_no_no{plain interrupt}, yes_yes_no
    {external NMI}, yes_no_yes{internal NMI}; ignore yes_yes_yes: the controller takes one NMI
    at a time (checker error if seen); ignore no_*_*: no notification
  - cr_dbg = cp_debug_req x cp_debug_mode: yes_yes{first debug-ROM record, or a debug-mode record
    with the pin still high}, no_yes{debug-mode record with the pin released}, no_no{ordinary
    record}; ignore yes_no: unreachable (C-3 / X-6: halt_if is combinational from debug_req_i,
    rtl/ibex_controller.sv:700-708, :1020, so no instruction transfers into ID outside debug mode
    while the pin is high; the captured_debug_req path lands on the first debug-ROM record, which
    has debug_mode = 1; checker error if seen)
  - cr_expanded_trap = cp_expanded x cp_trap: first_no, mid_no, last_no, first_yes, mid_yes,
    last_yes; ignore none_*: covered by CG-RVFI-001
- Adopted (riscv-dv): none
- TP items: TP-DIT-021, TP-DIT-032, TP-SEC-006, TP-SEC-008, TP-SEC-009, TP-SEC-040, TP-RST-024,
  TP-RST-025, TP-RVFI-019, TP-RVFI-020, TP-RVFI-021, TP-RVFI-022, TP-RVFI-023, TP-RVFI-024,
  TP-RVFI-025, TP-RVFI-026, TP-RVFI-034, TP-RVFI-035, TP-RVFI-037, TP-RVFI-040

### CG-RVFI-004: gen_cg_rvfi_trap
- Features: F-RVFI-005, F-RVFI-013, F-RVFI-015, F-RVFI-025, F-RVFI-026, F-RVFI-027, F-SEC-026,
  F-DIT-022
- Sample: a trap record, or an ebreak record (trapped or entering debug mode), plus the TB model
  event "ID exception requested in the same cycle as a WB exception" (derived from the timing of
  two consecutive program instructions, for the coincidence bins); condition: rvfi_valid &&
  (rvfi_trap || is_ebreak(rvfi_insn)); anti-vacuity: trap and ebreak records are a small
  fraction of records; the cause is read back from mcause in the handler (not assumed), the
  stage from the instruction class, so a hit proves a trap of that cause was recorded.
- Coverpoints:
  - cp_cause iff rvfi_trap = mcause read in the handler: bins
    instr_access_fault{ExcCauseInstrAccessFault (1)}, illegal{ExcCauseIllegalInsn (2)},
    breakpoint{ExcCauseBreakpoint (3): ebreak with dcsr.ebreakm/ebreaku == 0},
    load_fault{ExcCauseLoadAccessFault (5)}, store_fault{ExcCauseStoreAccessFault (7)},
    ecall_u{ExcCauseEcallUMode (8)}, ecall_m{ExcCauseEcallMMode (11)}; ignore_bins
    misaligned{ExcCauseInsnAddrMisa, ExcCauseLoadAddrMisaligned, ExcCauseStoreAddrMisaligned}: Ibex
    raises no misaligned exceptions in RV32 mode (checker error if seen)
  - cp_stage iff rvfi_trap = where the exception was detected: bins id{fetch fault, illegal,
    breakpoint, ecall}, wb{load/store fault}
  - cp_coincident_wb_err iff rvfi_trap = the model event for this trap record: bins no{0},
    yes{1: this is the WB fault record of a coincidence}
  - cp_mode iff rvfi_trap = rvfi_mode: bins u{PRIV_LVL_U}, m{PRIV_LVL_M}
  - cp_insn_meaningful iff rvfi_trap: bins yes{not a fetch fault}, fetch_error_na{instruction
    access fault: rvfi_insn not compared}
  - cp_ebreak_kind iff is_ebreak(rvfi_insn) = which ebreak path: bins exception{rvfi_trap == 1},
    debug_entry{rvfi_trap == 0 && the next record has rvfi_pc_rdata == DmHaltAddr &&
    rvfi_ext_debug_mode == 1 (rtl/ibex_core.sv:1885-1886, S-2)}
  - cp_pmp_or_bus iff rvfi_trap = source of an access fault: bins pmp{PMP check}, bus_err{bus
    error response}, na{not an access fault}
  - cp_missing_record iff cp_coincident_wb_err == yes = the killed ID instruction's own record
    appears after the handler (re-executed instance): bins no{0: re-traced, the two-record
    convention}; yes{1: no record for the ID instruction at all} is a gen_chk_rvfi_proto error that
    re-opens B14, not a bin
  - cp_retrace_cause iff this trap record is the re-executed ID instruction of a coincidence
    (model) = its mcause: bins illegal{ExcCauseIllegalInsn}, ecall{ExcCauseEcallUMode,
    ExcCauseEcallMMode}, ebreak{ExcCauseBreakpoint}
  - (retired: cp_next_pc_is_vector - checker mirror of gen_isa_compare's vector rule)
- Crosses:
  - cr_cause_stage = cp_cause x cp_stage: instr_access_fault_id, illegal_id, breakpoint_id,
    ecall_u_id, ecall_m_id, load_fault_wb, store_fault_wb; ignore load_fault_id, store_fault_id,
    instr_access_fault_wb, illegal_wb, breakpoint_wb, ecall_u_wb and ecall_m_wb: exceptions are
    detected in one stage only
  - cr_cause_mode = cp_cause x cp_mode: instr_access_fault_u, instr_access_fault_m, illegal_u,
    illegal_m, breakpoint_u, breakpoint_m, load_fault_u, load_fault_m, store_fault_u,
    store_fault_m, ecall_u_u, ecall_m_m; ignore ecall_u_m and ecall_m_u: the cause encodes the
    mode
  - cr_wb_coincident = cp_stage x cp_coincident_wb_err x cp_missing_record: wb_yes_no{coincidence;
    the ID instruction is re-traced after the handler}, wb_no_no, id_no_no; ignore id_yes_*: when
    the events coincide the record that survives is the WB one by construction
    (rtl/ibex_core.sv:1851-1853); wb_yes_yes is excluded through the cp_missing_record definition
    (B14 re-opener, checker error)
  - cr_lsfault_src = cp_cause x cp_pmp_or_bus: instr_access_fault_pmp,
    instr_access_fault_bus_err, load_fault_pmp, load_fault_bus_err, store_fault_pmp,
    store_fault_bus_err; ignore illegal_*, breakpoint_*, ecall_u_* and ecall_m_* with pmp or
    bus_err: not access faults
- Adopted (riscv-dv): none
- TP items: TP-DIT-024, TP-SEC-007, TP-SEC-027, TP-RVFI-005, TP-RVFI-016, TP-RVFI-018, TP-RVFI-028,
  TP-RVFI-029, TP-RVFI-030, TP-RVFI-039

---------------------------------------------------------------------------------------------------
## CHERI
---------------------------------------------------------------------------------------------------

### CG-CHERI-001: gen_cg_cheri_off
- Features: F-CHERI-001, F-RVFI-030, F-SEC-037, F-RST-027, F-SEC-013
- Sample: (a) rvfi_valid of an instruction with opcode OPCODE_CHERI or OPCODE_AUICGP, or a CSR op
  whose csr field is in 12'hBC0..12'hBCF (the CHERIoT SCR range: CSR_MSHWM, CSR_MSHWMB,
  CSR_CDBG_CTRL and the unimplemented neighbours); (b) rvfi_valid of a CSR read of CSR_MARCHID or
  CSR_MISA; (c) eot: end of test, sampled ONLY when the run's dbus monitor counted >= 1000 stores
  and >= 1000 loads and RVFI >= 10k records (the requests on which data_tag_o and the capability
  fields could have been driven); condition: (rvfi_valid && (opcode(rvfi_insn) inside
  {OPCODE_CHERI, OPCODE_AUICGP} || (is_csr_op(rvfi_insn) && csr_addr(rvfi_insn) inside
  {[12'hBC0:12'hBCF], CSR_MARCHID, CSR_MISA}))) || eot_event; anti-vacuity: (a) and (b) are
  directed, infrequent records; the eot bins carry run totals from gen_chk_cheriot_quiet under the
  activity qualifier, so a hit proves a full run with real store/load traffic completed with the
  counts zero.
- Coverpoints:
  - cp_kind: bins op_cheri{opcode == OPCODE_CHERI}, op_auicgp{opcode == OPCODE_AUICGP},
    csr_mshwm{CSR_MSHWM}, csr_mshwmb{CSR_MSHWMB}, csr_cdbg_ctrl{CSR_CDBG_CTRL},
    csr_scr_other{12'hBC0, 12'hBC3, [12'hBC5:12'hBCF]}, id_marchid{CSR_MARCHID}, id_misa{CSR_MISA},
    eot{eot_event}
  - cp_funct3 = rvfi_insn[14:12] iff op_cheri || op_auicgp: bins f0{3'd0}, f1{3'd1}, f2{3'd2},
    f3{3'd3}, f4{3'd4}, f5{3'd5}, f6{3'd6}, f7{3'd7}
  - cp_funct7_class = rvfi_insn[31:25] iff op_cheri: bins f7_00{7'h00}, f7_01{7'h01},
    f7_7f{7'h7f}, f7_other{every other value}
  - cp_trap = rvfi_trap (cross operand only; owner CG-RVFI-001.cp_trap) iff !eot: bins yes{1},
    no{0}
  - cp_mode = rvfi_mode iff !eot: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_csr_op = CSR op form (funct3) iff csr_*: bins csrrw{3'b001}, csrrs{3'b010}, csrrc{3'b011},
    csrrwi{3'b101}, csrrsi{3'b110}, csrrci{3'b111}
  - cp_tag_zero_run iff eot (qualified as in the Sample) = data_tag_o never 1 on a data_req_o
    cycle in the run: bins yes{1}
  - cp_caps_zero_run iff eot (qualified as in the Sample) = every rvfi capability field
    (rs1_rcap, rs2_rcap, rd_wcap, mem_rcap, mem_wcap) and mem_is_cap zero / NULL_CAP on every
    record: bins yes{1}
  - (retired: cp_marchid_val and cp_misa_val - checker mirrors of gen_isa_compare
    (CSR_MARCHID_VALUE, the misa constant); the reads are covered by cp_kind x cp_mode x cp_trap;
    cp_store_seen - folded into the eot activity qualifier)
- Crosses:
  - cr_op_funct3 = cp_kind x cp_funct3: op_cheri_f0, op_cheri_f1, op_cheri_f2, op_cheri_f3,
    op_cheri_f4, op_cheri_f5, op_cheri_f6, op_cheri_f7, op_auicgp_f0, op_auicgp_f1,
    op_auicgp_f2, op_auicgp_f3, op_auicgp_f4, op_auicgp_f5, op_auicgp_f6, op_auicgp_f7
    (cp_funct3 is sampled only for the two opcodes, so no other combination exists)
  - cr_csr_op = cp_kind x cp_csr_op: csr_mshwm_csrrw, csr_mshwm_csrrs, csr_mshwm_csrrc,
    csr_mshwmb_csrrw, csr_mshwmb_csrrwi, csr_cdbg_ctrl_csrrw, csr_cdbg_ctrl_csrrsi,
    csr_scr_other_csrrw, csr_scr_other_csrrci (cp_csr_op is sampled only for the csr_* kinds)
  - cr_kind_mode_trap = cp_kind x cp_mode x cp_trap: op_cheri_m_yes, op_cheri_u_yes,
    op_auicgp_m_yes, op_auicgp_u_yes, csr_mshwm_m_yes, csr_mshwm_u_yes, csr_mshwmb_m_yes,
    csr_cdbg_ctrl_m_yes, csr_scr_other_m_yes, id_marchid_m_no, id_misa_m_no, id_marchid_u_yes,
    id_misa_u_yes; ignore op_*_*_no and csr_*_*_no: with CHERIoT off every such instruction traps
    (checker error if seen); ignore id_marchid_m_yes and id_misa_m_yes: an M-mode read of a
    read-only identification CSR never traps; ignore id_marchid_u_no and id_misa_u_no: a U-mode
    access to an M-level CSR always traps (the former ignore was inverted; Critic pre-review S-7);
    ignore eot_*_*: not a record
- Adopted (riscv-dv): none
- TP items: TP-SEC-017, TP-SEC-037, TP-SEC-038, TP-RST-020, TP-RST-028, TP-RVFI-033, TP-CHERI-001,
  TP-CHERI-002, TP-CHERI-003, TP-CHERI-004

---------------------------------------------------------------------------------------------------
## Counts
---------------------------------------------------------------------------------------------------

- Covergroups: 20
- Coverpoints: 166 (of which 9 are cross-operand-only copies, not manifest bins; retired
  coverpoints are not counted)
- Crosses: 66 (cr_div_rs2 retired; cr_div_zero and cr_first_beat_order added by fix brief 3)
- Distinct coverpoint bins referenced by TP items: 558
- Distinct cross bins referenced by TP items: 437
- Trace CSV rows: 1115 (of which 91 are probe-gated P1 rows, not in any manifest)
- Adopted (riscv-dv) bins: 0
- TP items: 147 (expected-fail: 5 = TP-DIT-019, TP-DIT-032, TP-RVFI-013, TP-SEC-040, TP-RVFI-040;
  informational: 3 = TP-SEC-010, TP-SEC-011, TP-RVFI-039)
- Method: counts are generated by the fix-brief-3 verify script (scratchpad regen_verify_fix3.py)
  from this file's `  - cp_` / `  - cr_` lines and from the Bins lines of
  tp_sec_rst_rvfi_cheri.md; every CSV row was checked to name a declared, non-ignored,
  non-cross-operand-only bin of its covergroup.

---------------------------------------------------------------------------------------------------
## Probe candidates
---------------------------------------------------------------------------------------------------

- P1 dummy_instr_id_o / dummy_instr_wb_o (ibex_core output ports wired inside gen_dut_top to the
  register file; wrapper-internal nets, not RTL probes per rtl-arch s9) and the if_stage fcov
  nets fcov_dummy_instr_type / fcov_insert_dummy_instr (rtl/ibex_if_stage.sv:817-821, present
  unless DV_FCOV_DISABLE). Bins that cannot be sampled from the boundary or RVFI without them:
  all of CG-DIT-004 (insertion event, type, operand registers, context, back-to-back, dropped
  insertion, window counts), CG-DIT-005.cp_pattern_changed, CG-RST-004.cp_dummy_adjacent and
  cr_rd_bank_dummy, CG-RST-002.cp_inflight.dummy_in_id and cr_inflight_len.dummy_in_id_short.
  Why: dummies are architecturally invisible and excluded from RVFI; the boundary shows only
  timing gaps, which cannot name the type or the operand registers and cannot see a dropped
  insertion (F-DIT-021) at all. Status: accepted coverage-only (Critic C8 ruling, tb-infra e);
  the bins are probe-gated and NOT in any test manifest until the probe register carries P1
  (gen_tb_architecture.md 8.3 item 5). The fire-checks of TP-DIT-022, TP-DIT-023 and TP-DIT-030
  are boundary-based with P1 as confirmation only. No checker depends on it.
- P9 (probe candidate, probe register entry needed): if_stage_i fcov_dummy_instr_type and the IF/ID
  pipeline write enable if_id_pipe_reg_we (rtl/ibex_if_stage.sv:538-544, 817-821) are NOT among P1's
  registered nets; CG-DIT-004.cp_type and its insert sample event need them. Probe status: pending
  probe-register ruling; excluded from manifests until ruled (Critic M-7a).
- rf_we_wb_o / rf_waddr_wb_o (same class of wrapper-internal net): used only inside the P1
  monitor to attribute an RF write to a dummy (waddr == 0 with dummy_instr_wb_o); not needed by
  any bin on its own and never a fire-check (TP-DIT-030's fire-check is boundary-only).
- None of the SEC/RST/RVFI/CHERI covergroups needs an internal probe: alerts, crash_dump_o,
  double_fault_seen_o, core_busy_o, fetch_enable_i, the bus monitors and RVFI supply every
  sampled field. The coincidence bins (CG-RVFI-004.cr_wb_coincident, cp_missing_record,
  cp_retrace_cause) use a TB timing model of two program instructions, not an RTL signal; if the
  model proves ambiguous the DV Lead may consider controller wb_exception_o as a coverage-only
  probe (P4 class), which is NOT requested here.


# 3.8 Areas REG, XIF, ADOPT: Randomization layers (regime knobs and schedule), cross-interface crosses, bins adopted from riscv-dv


Task: T-006 cross-cutting subagent. Companion: tp_xcut.md (test-plan items, knob definitions,
schedule). Build configuration `opentitan`; DUT gen_dut_top = ibex_core + ibex_register_file_ff
(README_T006_BRIEF.md). All bins here are sampled at the DUT boundary or on RVFI, except
CG-XIF-012 (probe candidate P1, see Probe candidates). Plan v2b conventions C-1..C-16 (tp_xcut.md
header) apply; S18, S19 and S21 below carry the RTL-timing facts they rest on.

Area prefixes: REG = randomization layers (regime knobs, regime schedule, transitions);
XIF = cross-interface crosses; ADOPT = bins adopted from riscv-dv's coverage model
(vendor/google_riscv-dv/src/riscv_instr_cover_group.sv, read as reference only), counted
separately in the trace CSV (adopted = 1).

Conventions: covergroup types are `gen_cg_<area>_<name>` in `gen_fcov_pkg` (contract README;
tb-infra g.). Counts and ranges derive from ibex_pkg / RTL localparams: IC_LINE_BEATS
(rtl/ibex_pkg.sv:406), IC_NUM_WAYS (:401), IC_NUM_LINES (:405), NUM_FB (rtl/ibex_icache.sv:72),
PMPNumRegions (16, ibex_configs.yaml), irq_fast_i width ($bits(irq_fast_i) = 15,
rtl/ibex_core.sv:122), IbexMuBiOn/Off. Where a bin name carries a number (cap8, k5_plus) the
number is the brief's label for this configuration; the SV bin expression uses the parameter.
Bin-name predicates used throughout: a transition bin `<a>_to_<b>` of a `cp_<knob>_tr` coverpoint
means (previous phase's applied value == a && this phase's applied value == b); a cross bin
`<x>_<y>[_<z>]` is the product of the named bins of the crossed coverpoints in the order written;
a per-coverpoint `[F: ...]` tag lists the F-IDs that coverpoint evidences (completeness rule 7).

## Sampling model (boundary-derived state used by every CG-XIF and CG-REG-008)

All signals below are computed by the TB monitors from DUT ports and RVFI; none reads inside
ibex_core.

- S1 `ibus_outst`: granted instruction beats (instr_req_o & instr_gnt_i) not yet answered by
  instr_rvalid_i; range 0..NUM_FB*IC_LINE_BEATS (gen_interface_inventory.md s2).
- S2 `fetch_stalled`: ibus_outst >= 1 && !instr_rvalid_i in this cycle.
- S3 `ibus_err_rsp`: instr_rvalid_i && instr_err_i.
- S4 `dbus_outst`: granted data requests not yet answered; range 0..2 (s3).
- S5 `dbus_split`: the dbus monitor marks two consecutive requests as one misaligned pair when
  addr2 == addr1 + 4 and the byte-enable pair is one of {1110,0001}, {1100,0011}, {1000,0111},
  {1000,0001} (F-DMEM-011..016; s3 table). `split_inflight` = first half granted and second half
  not yet answered; sub-states: `split_first_outst` (second not yet granted), `split_both_outst`
  (dbus_outst == 2), `split_second_outst` (first answered, second outstanding).
- S6 `dbus_err_rsp`: data_rvalid_i && data_err_i; `err_half` in {single, split_first,
  split_second} from S5; `we` recorded at the grant of that request.
- S7 irq state from pins: `irq_pend` = irq_pending_o (|(mip & mie), not gated by mstatus.MIE,
  s6), `nmi` = irq_nm_i.
- S8 `dbg_req` = debug_req_i.
- S9 `sleeping` = (core_busy_o == IbexMuBiOff).
- S10 `fetch_en_on` = (fetch_enable_i == IbexMuBiOn); any other value is Off (s1).
- S11 `mode_q`: privilege of the instruction stream at a boundary cycle c = rvfi_mode (2'b11 = M,
  2'b00 = U) of the record whose WB-exit cycle (rvfi_valid cycle - 1, S18) is the latest at or
  before c; `dbg_mode_q` likewise from rvfi_ext_debug_mode. No instruction retires between the
  last pre-entry retirement and the first handler / debug-ROM record, so an event inside an entry
  window belongs to the pre-entry mode exactly (the entry record itself reports the handler's
  mode, F-PRV-033). With the S18 one-cycle back-dating this is cycle-exact; probe P4 is not
  needed.
- S12 `icache_en_q`: cpuctrlsts.icache_enable tracked from retired CSR writes to 0x7C0 (reset 0,
  M-mode WARL, F-IC-012), forced 0 while dbg_mode_q (F-CSR-086). `fill_inflight` =
  icache_en_q && ibus_outst >= 1. `invalidating` = tag-write walk in progress on the
  ic_tag_write_o / ic_tag_addr_o ports (IC_NUM_LINES writes after reset or fence.i, F-IC-022/023).
- S13 `key_withheld`: an ic_scr_key_req_o pulse has been seen and ic_scr_key_valid_i is still 0.
- S14 `zcmp_inflight`: set by a retirement with rvfi_ext_expanded_insn_valid &&
  !rvfi_ext_expanded_insn_last, cleared by rvfi_ext_expanded_insn_last or by an rvfi_trap record
  inside the sequence (F-RVFI-022/023). `zcmp_kind` decoded from rvfi_ext_expanded_insn (cm.push
  / cm.pop / cm.popret / cm.popretz / cm.mvsa01 / cm.mva01s, Zcmp spec).
- S15 `fence_i_retired`: rvfi_valid && rvfi_insn[6:0] == 7'h0F && rvfi_insn[14:12] == 3'b001
  (rs1/rd/imm ignored, F-ISA-031).
- S16 `csr_write_retired(addr)`: rvfi_valid && !rvfi_trap && SYSTEM opcode with a CSR funct3 and
  a writing form (not csrrs/csrrc rs1 = x0, not csrrsi/csrrci uimm = 0; F-CSR-002). `flushing` =
  addr not in {mscratch 0x340, mepc 0x341} (F-CSR-006/007). `pmp_csr` = addr in {pmpcfg0..3
  0x3A0..0x3A3, pmpaddr0..PMPNumRegions-1 0x3B0.., mseccfg 0x747}. `irq_csr` = addr in {mie 0x304,
  mstatus 0x300, mip 0x344}.
- S17 `mret_retired`: rvfi_insn == 32'h30200073; `dret_retired`: 32'h7B200073; `wfi_retired`:
  32'h10500073 (each with !rvfi_trap).
- S18 cycle anchoring of RVFI records (exactness constants, gen_tb_architecture.md 8.2): rvfi_valid
  is exactly one flop after the instruction leaves WB (rvfi_stage_valid_d[1] = rvfi_wb_done,
  rtl/ibex_core.sv:1868), so every retirement-anchored event is back-dated by one cycle
  (`wb_exit` = rvfi_valid cycle - 1) and read cycle-exactly at the pins. Commit-to-record offsets:
  a CSR write commits GEN_CSR_WRITE_TO_RVFI_OFFSET = 2 cycles before its record (fixed; a WB stall
  delays commit and record together); trap/mret/dret records follow their commit (the FLUSH cycle,
  where pc_set is issued) by GEN_TRAP_TO_RVFI_OFFSET = 1; the interrupt marker rvfi_ext_irq_valid
  is a LEVEL that rises four cycles after the decision cycle and stays high until about two cycles
  after the handler's first instruction enters ID (C-13, X-16; not generated when ID emptied before
  WB drained): no S-state or bin of this area uses it, interrupt entry is anchored on the rvfi_intr
  record and the vector fetch below; a taken branch/jump redirects (pc_set) in its last ID cycle,
  GEN_RVFI_ID_EXIT_OFFSET = 2 cycles before its record. "Same cycle as X" therefore names one
  back-dated cycle per coverpoint, never a window. `irq_taken_window`: cycles from `wb_exit` of the
  last record before a record with rvfi_intr == 1 to the vector fetch of that handler (first
  instr_req_o at mtvec.BASE + 4*id, or + 0x7C for an NMI); the handler record's rvfi_ext_nmi /
  rvfi_ext_nmi_int tell irq from NMI. `debug_entry_window`: likewise up to the first instr_req_o
  for DmHaltAddr. No retirement lies inside either window by definition, so both are exact at the
  boundary; probe P4 is not needed for them.
- S19 `redirect`: a record that changes the control flow, derived from RVFI only (no ibus request
  is required, so icache hits are not blind): (a) a taken branch/jump: rvfi_pc_wdata !=
  rvfi_pc_rdata + insn length with bit 0 of rvfi_pc_wdata masked (B13), target = rvfi_pc_wdata;
  (b) a trap record (rvfi_trap = 1) or an S17 mret/dret record: their rvfi_pc_wdata is the NEXT
  SEQUENTIAL fetch address, never the target (C-1, X-1: rtl/ibex_core.sv:2084 captures pc_if in the
  DECODE cycle, the PC_EXC / PC_ERET / PC_DRET pc_set comes one cycle later in FLUSH), so the target
  is the NEXT record's rvfi_pc_rdata (or, with the icache off, the DmExceptionAddr / DmHaltAddr /
  vector fetch on instr_addr_o). The redirect cycle is the cycle pc_set is issued: for (a) the CTI's
  last ID cycle, rvfi_valid cycle - GEN_RVFI_ID_EXIT_OFFSET (2); for (b) the FLUSH cycle,
  rvfi_valid cycle - GEN_TRAP_TO_RVFI_OFFSET (1); bring-up confirms both constants.
- S20 `dummy_inserted`: dummy_instr_id_o rising (P1 probe candidate; ibex_core port not on the
  gen_dut_top boundary) with dummy type from the RTL fcov_dummy_instr_type net.
- S21 `ls_outst_at_id_entry(X)` for X a wfi or a CSR write: the record before X is a load/store P
  (a decoded load/store record, C-12) and X's rvfi_valid cycle == P's rvfi_valid cycle + 1.
  Derivation: nothing in ID executes or leaves DECODE while a WB memory access is outstanding
  (instr_executing requires ~outstanding_memory_access, rtl/ibex_id_stage.sv:1059-1062; en_wb_o =
  instr_done, :1224; a special_req waits for ready_wb_i, rtl/ibex_controller.sv:668-678), so X
  leaves ID in P's final data_rvalid_i cycle R at the earliest; P's WB exit is R and its record
  R + 1 (S18); X spends one WB cycle (WB_INSTR_OTHER) and records at R + 2 iff X was in ID at or
  before R, later otherwise. A one-cycle record spacing therefore proves that P's access was
  outstanding (or completing, the CG-XIF-003 count rule) in X's first ID cycle. Sub-states from S5
  on P: `single` (non-split) or `split` (misaligned pair: R is the second half's rvalid, so the
  second half was the outstanding one). At X's own WB exit the data bus is always idle, which is
  why CG-XIF-004.cp_pending_at_wfi.data_outst and CG-XIF-009.cp_prev_ls_outst are anchored here
  (fact-check TP-XIF-004 / TP-XIF-010). RVFI-only, so independent of the icache state (C-14).

Phase log (REG): every agent writes one record per regime phase it applies: {phase_idx, knob,
applied_value, start_cycle, start_rvfi_order, pinned, first_event_cycle, activity_count}. The
program-side knobs (instr_mix, priv_regime, pmp_regime) write their record when the region marker
store (TB MMIO phase-marker register, tb-infra b.8) is observed on the data bus. CG-REG-001..006,
CG-REG-009 and CG-REG-010 (run constant: one sample per run) sample a record only at the phase's
FIRST regime-relevant event
(`first_event_cycle`, table below), never at the phase start and never per clock: a value bin
proves the DUT saw >= 1 transaction under that regime, and a `_tr` transition bin (previous
phase's value -> this phase's value) is credited only when the previous phase also reached its
first event (activity_count >= 1). A phase that ends before its first event contributes no sample.
Absence-type values (none, quiet, always_on) use an activity threshold instead of one event, so
they are never credited to an idle phase.

Regime-relevant first event per knob (value bins and `_tr` bins are sampled here):

| knob | first event | absence-type threshold |
|---|---|---|
| imem_gnt_delay, imem_rvalid_delay, imem_outstanding_cap | first instr_req_o & instr_gnt_i of the phase | - |
| imem_err_rate | rare/frequent: first instr_rvalid_i & instr_err_i; none: the 64th error-free instr_rvalid_i beat | 64 beats |
| imem_intg_err_rate | rare/frequent: first corrupted instr_rdata_i[38:32] beat; none: the 64th clean beat | 64 beats |
| dmem_gnt_delay, dmem_rvalid_delay | first data_req_o & data_gnt_i of the phase | - |
| dmem_err_rate | rare/frequent: first data_rvalid_i & data_err_i; none: the 64th error-free data_rvalid_i | 64 responses |
| dmem_intg_err_rate | rare/frequent: first corrupted data_rdata_i[38:32] response; none: the 64th clean response | 64 responses |
| irq_regime, irq_line_mix, irq_hold | sparse/storm: first assertion edge on any irq line; quiet: the 500th cycle of the phase with zero new assertion edges (500 = lower bound of the short duration class) | 500 cycles |
| debug_req_regime | sparse/storm: first debug_req_i rising edge; none: the 500th cycle with no edge | 500 cycles |
| fetch_enable_regime | toggling: first fetch_enable_i Off edge; always_on: the 500th cycle held On | 500 cycles |
| icache_ecc_err_rate (iff icache_en_q, S12) | rare/frequent: first injection on a lookup with the cache enabled; none: the 64th lookup with the cache enabled and no injection | 64 lookups |
| scr_key_delay | first ic_scr_key_req_o pulse of the phase (the fence.i or reset that raised it), answered under the regime | - |
| instr_mix, priv_regime, pmp_regime | first retirement after the region marker store's record; for pmp_regime after the prologue's last PMP CSR write retired | - |
| mcounteren_writable (run constant, CG-REG-010) | the first retired mcounteren write of the run (S16), pin value read in that write's commit cycle (S18); a run that never writes mcounteren contributes no sample | - |

## Covergroups

### CG-REG-001: gen_cg_reg_imem_knobs
- Features: F-IMEM-001, F-IMEM-003, F-IMEM-004, F-IMEM-005, F-IMEM-006, F-IMEM-007, F-IMEM-008, F-IMEM-009, F-IMEM-010, F-IMEM-011, F-IMEM-012, F-IMEM-016, F-IMEM-017, F-IC-016, F-IC-019, F-IMEM-013, F-IMEM-014, F-IMEM-015, F-EXC-003
- Sample: imem agent phase-log record at the phase's first regime-relevant event (Phase log table: first granted request, first errored beat, or the 64-beat threshold for none); condition: record.knob in the imem group && activity reached; anti-vacuity: one sample per phase and knob, never per clock and never at the phase start; the record carries the value the agent APPLIED (echoed from its driver state) and the sample instant proves >= 1 transaction ran under it, so a value bin proves the DUT saw that regime and a `_tr` bin proves two consecutive phases with activity differed (an asleep or idle phase is never credited).
- Coverpoints:
  - cp_imem_gnt_delay = rec.value of knob:imem_gnt_delay [F: F-IMEM-001, F-IMEM-003, F-IMEM-004, F-IMEM-005, F-IMEM-017]: bins same_cycle{gnt in the request cycle, F-IMEM-004}, short{gnt 1..3 cycles later, F-IMEM-005}, long{gnt 4..32 (10% 33..128) cycles later, F-IMEM-003/017}, random{per-request mix 40/40/20}
  - cp_imem_gnt_delay_tr = rec.value of knob:imem_gnt_delay across consecutive phases [F: F-IMEM-001, F-IMEM-003, F-IMEM-004, F-IMEM-005, F-IMEM-017]: bins same_cycle_to_short, same_cycle_to_long, same_cycle_to_random, short_to_same_cycle, short_to_long, short_to_random, long_to_same_cycle, long_to_short, long_to_random, random_to_same_cycle, random_to_short, random_to_long
  - cp_imem_rvalid_delay = rec.value of knob:imem_rvalid_delay [F: F-IMEM-006, F-IMEM-007, F-IMEM-008, F-IMEM-009, F-IMEM-010, F-IC-016]: bins min1{exactly 1 cycle after gnt, F-IMEM-007}, short{1..3}, long{4..32 (10% 33..128), F-IMEM-008/009}, random{mix 40/40/20}
  - cp_imem_rvalid_delay_tr = knob:imem_rvalid_delay across consecutive phases [F: F-IMEM-006, F-IMEM-007, F-IMEM-008, F-IMEM-009, F-IMEM-010, F-IC-016]: bins min1_to_short, min1_to_long, min1_to_random, short_to_min1, short_to_long, short_to_random, long_to_min1, long_to_short, long_to_random, random_to_min1, random_to_short, random_to_long
  - cp_imem_err_rate = rec.value of knob:imem_err_rate [F: F-IMEM-011, F-IMEM-012, F-IMEM-013, F-IMEM-014, F-IMEM-015, F-EXC-003]: bins none{0}, rare{~1/512 beats}, frequent{~1/20 beats, F-IMEM-011..014}
  - cp_imem_err_rate_tr = knob:imem_err_rate across consecutive phases [F: F-IMEM-011, F-IMEM-012, F-IMEM-013, F-IMEM-014, F-IMEM-015, F-EXC-003]: bins none_to_rare, none_to_frequent, rare_to_none, rare_to_frequent, frequent_to_none, frequent_to_rare
  - cp_imem_outstanding_cap = rec.value of knob:imem_outstanding_cap [F: F-IMEM-008, F-IMEM-009, F-IMEM-016, F-IC-016, F-IC-019]: bins cap1{1 beat}, cap2{IC_LINE_BEATS}, cap4{2*IC_LINE_BEATS}, cap8{NUM_FB*IC_LINE_BEATS, the RTL bound}
  - cp_imem_outstanding_cap_tr = knob:imem_outstanding_cap across consecutive phases [F: F-IMEM-008, F-IMEM-009, F-IMEM-016, F-IC-016, F-IC-019]: bins cap1_to_cap2, cap1_to_cap4, cap1_to_cap8, cap2_to_cap1, cap2_to_cap4, cap2_to_cap8, cap4_to_cap1, cap4_to_cap2, cap4_to_cap8, cap8_to_cap1, cap8_to_cap2, cap8_to_cap4
- Crosses:
  - cr_gnt_x_rvalid = cp_imem_gnt_delay x cp_imem_rvalid_delay: required bins (16): same_cycle_min1, same_cycle_short, same_cycle_long, same_cycle_random, short_min1, short_short, short_long, short_random, long_min1, long_short, long_long, long_random, random_min1, random_short, random_long, random_random
  - cr_err_x_cap = cp_imem_err_rate x cp_imem_outstanding_cap: required bins (12): none_cap1, none_cap2, none_cap4, none_cap8, rare_cap1, rare_cap2, rare_cap4, rare_cap8, frequent_cap1, frequent_cap2, frequent_cap4, frequent_cap8
- Adopted (riscv-dv): none
- TP items: TP-REG-001, TP-REG-002, TP-REG-003, TP-REG-004

### CG-REG-002: gen_cg_reg_dmem_knobs
- Features: F-DMEM-001, F-DMEM-002, F-DMEM-004, F-DMEM-005, F-DMEM-006, F-DMEM-007, F-DMEM-008, F-DMEM-010, F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-024, F-DMEM-025, F-DMEM-026, F-DMEM-028, F-DMEM-036, F-DMEM-037, F-EXC-025, F-EXC-027
- Sample: dmem agent phase-log record at the phase's first regime-relevant event (Phase log table: first granted data request, first errored response, or the 64-response threshold for none); condition: record.knob in the dmem group && activity reached; anti-vacuity: as CG-REG-001 (applied value echoed by the driver, one sample per phase, credited only after the DUT issued a data access under the regime).
- Coverpoints:
  - cp_dmem_gnt_delay = rec.value of knob:dmem_gnt_delay [F: F-DMEM-001, F-DMEM-002, F-DMEM-004, F-DMEM-005, F-DMEM-024]: bins same_cycle{F-DMEM-004}, short{1..3, F-DMEM-005}, long{4..32 (10% 33..128), F-DMEM-002/024}, random{mix 40/40/20}
  - cp_dmem_gnt_delay_tr = knob:dmem_gnt_delay across consecutive phases [F: F-DMEM-001, F-DMEM-002, F-DMEM-004, F-DMEM-005, F-DMEM-024]: bins same_cycle_to_short, same_cycle_to_long, same_cycle_to_random, short_to_same_cycle, short_to_long, short_to_random, long_to_same_cycle, long_to_short, long_to_random, random_to_same_cycle, random_to_short, random_to_long
  - cp_dmem_rvalid_delay = rec.value of knob:dmem_rvalid_delay [F: F-DMEM-006, F-DMEM-007, F-DMEM-008, F-DMEM-010, F-DMEM-025, F-DMEM-026, F-DMEM-028]: bins min1{F-DMEM-006}, short{1..3}, long{4..32 (10% 33..128), F-DMEM-025/026/030}, random{mix}
  - cp_dmem_rvalid_delay_tr = knob:dmem_rvalid_delay across consecutive phases [F: F-DMEM-006, F-DMEM-007, F-DMEM-008, F-DMEM-010, F-DMEM-025, F-DMEM-026, F-DMEM-028]: bins min1_to_short, min1_to_long, min1_to_random, short_to_min1, short_to_long, short_to_random, long_to_min1, long_to_short, long_to_random, random_to_min1, random_to_short, random_to_long
  - cp_dmem_err_rate = rec.value of knob:dmem_err_rate [F: F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-036, F-DMEM-037, F-EXC-025, F-EXC-027]: bins none{0}, rare{~1/512 responses}, frequent{~1/20 responses, F-DMEM-021..023/036/037}
  - cp_dmem_err_rate_tr = knob:dmem_err_rate across consecutive phases [F: F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-036, F-DMEM-037, F-EXC-025, F-EXC-027]: bins none_to_rare, none_to_frequent, rare_to_none, rare_to_frequent, frequent_to_none, frequent_to_rare
- Crosses:
  - cr_gnt_x_rvalid = cp_dmem_gnt_delay x cp_dmem_rvalid_delay: required bins (16): same_cycle_min1, same_cycle_short, same_cycle_long, same_cycle_random, short_min1, short_short, short_long, short_random, long_min1, long_short, long_long, long_random, random_min1, random_short, random_long, random_random
  - cr_err_x_rvalid = cp_dmem_err_rate x cp_dmem_rvalid_delay: required bins (12): none_min1, none_short, none_long, none_random, rare_min1, rare_short, rare_long, rare_random, frequent_min1, frequent_short, frequent_long, frequent_random
- Adopted (riscv-dv): none
- TP items: TP-REG-005, TP-REG-006, TP-REG-007

### CG-REG-003: gen_cg_reg_irq_knobs
- Features: F-IRQ-001, F-IRQ-002, F-IRQ-009, F-IRQ-010, F-IRQ-011, F-IRQ-025, F-IRQ-026, F-IRQ-027, F-IRQ-030, F-IRQ-034, F-IRQ-052, F-IRQ-061, F-IRQ-062, F-IRQ-063, F-EXC-059
- Sample: irq driver phase-log record at the phase's first regime-relevant event (Phase log table: first assertion edge for sparse/storm; for quiet the 500th cycle of the phase with zero new edges); condition: record.knob in the irq group && activity reached; anti-vacuity: one sample per phase, never at the phase start; the driver echoes the regime it is executing (event generator state), not the schedule, and the sample instant proves the regime acted (or, for quiet, provably held) before any value or `_tr` bin is credited.
- Coverpoints:
  - cp_irq_regime = rec.value of knob:irq_regime [F: F-IRQ-001, F-IRQ-002, F-IRQ-011, F-IRQ-027, F-EXC-059]: bins quiet{no new assertion events}, sparse{geometric inter-arrival, mean ~2000 cycles, <= 1 event outstanding}, storm{mean ~20 cycles, overlapping events, immediate re-assert after ack, F-IRQ-011/027, F-EXC-059}
  - cp_irq_regime_tr = knob:irq_regime across consecutive phases [F: F-IRQ-001, F-IRQ-002, F-IRQ-011, F-IRQ-027, F-EXC-059]: bins quiet_to_sparse, quiet_to_storm, sparse_to_quiet, sparse_to_storm, storm_to_quiet, storm_to_sparse
  - cp_irq_line_mix = rec.value of knob:irq_line_mix [F: F-IRQ-009, F-IRQ-010, F-IRQ-030, F-IRQ-034, F-IRQ-061, F-IRQ-062, F-IRQ-063]: bins single{one line per event from the 3 + $bits(irq_fast_i) maskable lines}, multi{2..k lines per event, F-IRQ-009/010}, fast_only{irq_fast_i lines only, F-IRQ-010/061/062}, with_nmi{multi plus irq_nm_i at 25%, F-IRQ-030/034}
  - cp_irq_line_mix_tr = knob:irq_line_mix across consecutive phases [F: F-IRQ-009, F-IRQ-010, F-IRQ-030, F-IRQ-034, F-IRQ-061, F-IRQ-062, F-IRQ-063]: bins single_to_multi, single_to_fast_only, single_to_with_nmi, multi_to_single, multi_to_fast_only, multi_to_with_nmi, fast_only_to_single, fast_only_to_multi, fast_only_to_with_nmi, with_nmi_to_single, with_nmi_to_multi, with_nmi_to_fast_only
  - cp_irq_hold = rec.value of knob:irq_hold [F: F-IRQ-025, F-IRQ-026, F-IRQ-027, F-IRQ-052]: bins until_taken{level held until rvfi_intr then released within 0..3 cycles}, through_handler{level held until the handler's MMIO ack store, F-IRQ-027/052}, pulse{1..3 cycle pulse regardless of taking, may be dropped, F-IRQ-025/026}
  - cp_irq_hold_tr = knob:irq_hold across consecutive phases [F: F-IRQ-025, F-IRQ-026, F-IRQ-027, F-IRQ-052]: bins until_taken_to_through_handler, until_taken_to_pulse, through_handler_to_until_taken, through_handler_to_pulse, pulse_to_until_taken, pulse_to_through_handler
- Crosses:
  - cr_regime_x_mix = cp_irq_regime x cp_irq_line_mix: required bins (8): sparse_single, sparse_multi, sparse_fast_only, sparse_with_nmi, storm_single, storm_multi, storm_fast_only, storm_with_nmi; ignore quiet_single, quiet_multi, quiet_fast_only, quiet_with_nmi: a quiet phase generates no assertion events, so the line mix is inert and the cross bin would be vacuous
  - cr_regime_x_hold = cp_irq_regime x cp_irq_hold: required bins (6): sparse_until_taken, sparse_through_handler, sparse_pulse, storm_until_taken, storm_through_handler, storm_pulse; ignore quiet_until_taken, quiet_through_handler, quiet_pulse: no events in a quiet phase, hold policy inert
- Adopted (riscv-dv): none
- TP items: TP-REG-008, TP-REG-009, TP-REG-010

### CG-REG-004: gen_cg_reg_dbg_fe_knobs
- Features: F-DBG-001, F-DBG-005, F-DBG-007, F-DBG-009, F-IMEM-022, F-IMEM-023, F-IMEM-024, F-IMEM-025, F-RST-010, F-RST-014, F-SEC-012
- Sample: debug_req driver and fetch_enable driver phase-log records at the phase's first regime-relevant event (Phase log table: first debug_req_i edge / first Off edge; 500-cycle hold threshold for none / always_on); condition: record.knob in {debug_req_regime, fetch_enable_regime} && activity reached; anti-vacuity: one sample per phase, driver-echoed value, credited only after the regime acted or provably held (F-DBG-006 B9 window, F-DBG-008 and F-RST-015 are owned by the DBG / RST / XIF items and are not cited here).
- Coverpoints:
  - cp_debug_req_regime = rec.value of knob:debug_req_regime [F: F-DBG-001, F-DBG-005, F-DBG-007, F-DBG-009]: bins none{never asserted}, sparse{mean ~5000 cycles, level held until rvfi_ext_debug_mode then released; 50% kept high through dret, F-DBG-007}, storm{mean ~100 cycles incl. 20% one-cycle pulses, F-DBG-005; the B9 FLUSH-cycle pulse window is the DBG area's TP-DBG-011}
  - cp_debug_req_regime_tr = knob:debug_req_regime across consecutive phases [F: F-DBG-001, F-DBG-005, F-DBG-007, F-DBG-009]: bins none_to_sparse, none_to_storm, sparse_to_none, sparse_to_storm, storm_to_none, storm_to_sparse
  - cp_fetch_enable_regime = rec.value of knob:fetch_enable_regime [F: F-IMEM-022, F-IMEM-023, F-IMEM-024, F-IMEM-025, F-RST-010, F-RST-014, F-SEC-012]: bins always_on{IbexMuBiOn all phase}, toggling{Off windows 1..200 cycles, mean gap ~1000 cycles; Off encoding 80% IbexMuBiOff / 20% invalid $bits(ibex_mubi_t) encoding, never X, F-IMEM-023, F-RST-014, F-SEC-012}
  - cp_fetch_enable_regime_tr = knob:fetch_enable_regime across consecutive phases [F: F-IMEM-022, F-IMEM-023, F-IMEM-024, F-IMEM-025, F-RST-010, F-RST-014, F-SEC-012]: bins always_on_to_toggling, toggling_to_always_on
- Crosses:
  - cr_dbg_x_fe = cp_debug_req_regime x cp_fetch_enable_regime: required bins (6): none_always_on, none_toggling, sparse_always_on, sparse_toggling, storm_always_on, storm_toggling
- Adopted (riscv-dv): none
- TP items: TP-REG-011, TP-REG-012

### CG-REG-005: gen_cg_reg_icache_knobs
- Features: F-IC-008, F-IC-023, F-IC-024, F-IC-029, F-IC-030, F-IC-031, F-IC-033, F-IC-035, F-SEC-001, F-SEC-021
- Sample: icache RAM model and scramble-key responder phase-log records at the phase's first regime-relevant event (Phase log table: first injection on an enabled-cache lookup / 64 clean enabled lookups; first key request pulse); condition: record.knob in {icache_ecc_err_rate, scr_key_delay} && activity reached; the ECC coverpoints and cr_ecc_x_key carry `iff icache_en_q` (S12) because the injection regime is inert while the program keeps the cache disabled (tp_xcut.md knob text), so a phase with the cache off contributes no ECC sample; anti-vacuity: one sample per phase, model-echoed value, credited only after a lookup or key request happened under the regime; the effect bins (alerts, invalidations) belong to the IC area, this group only proves the regime ran (F-IC-009/010/025 are IC-area items and are not cited here).
- Coverpoints:
  - cp_icache_ecc_err_rate = rec.value of knob:icache_ecc_err_rate iff icache_en_q [F: F-IC-030, F-IC-031, F-IC-033, F-IC-035, F-SEC-001]: bins none{0}, rare{~1/2000 lookups; tag/data 50/50; 1-bit/2-bit 50/50; way uniform over IC_NUM_WAYS, F-IC-030/031/033}, frequent{~1/50 lookups, same mix}
  - cp_icache_ecc_err_rate_tr = knob:icache_ecc_err_rate across consecutive phases iff icache_en_q (both phases reached an enabled-cache lookup) [F: F-IC-030, F-IC-031, F-IC-033, F-IC-035, F-SEC-001]: bins none_to_rare, none_to_frequent, rare_to_none, rare_to_frequent, frequent_to_none, frequent_to_rare
  - cp_scr_key_delay = rec.value of knob:scr_key_delay [F: F-IC-008, F-IC-023, F-IC-024, F-IC-029, F-SEC-021]: bins immediate{ic_scr_key_valid_i low for 1 cycle after the request, F-IC-008}, delayed{low 2..200 cycles}, withheld_then_valid{low 201..2000 cycles, long enough for a second fence.i and a WFI, F-IC-024/029; the never-valid case F-IC-010 is a directed IC-area test}
  - cp_scr_key_delay_tr = knob:scr_key_delay across consecutive phases [F: F-IC-008, F-IC-023, F-IC-024, F-IC-029, F-SEC-021]: bins immediate_to_delayed, immediate_to_withheld_then_valid, delayed_to_immediate, delayed_to_withheld_then_valid, withheld_then_valid_to_immediate, withheld_then_valid_to_delayed
- Crosses:
  - cr_ecc_x_key = cp_icache_ecc_err_rate x cp_scr_key_delay iff icache_en_q: required bins (9): none_immediate, none_delayed, none_withheld_then_valid, rare_immediate, rare_delayed, rare_withheld_then_valid, frequent_immediate, frequent_delayed, frequent_withheld_then_valid
- Adopted (riscv-dv): none
- TP items: TP-REG-013, TP-REG-014

### CG-REG-006: gen_cg_reg_program_knobs
- Features: F-ISA-001, F-ISA-023, F-MUL-001, F-CMP-001, F-CMP-039, F-BIT-001, F-CSR-001, F-DMEM-015, F-PRV-001, F-PRV-002, F-PRV-006, F-PMP-006, F-PMP-021, F-PMP-023, F-PMP-045, F-PMP-053, F-PMP-056, F-PRV-003, F-IRQ-008, F-PMP-015, F-PMP-024
- Sample: program-side phase-log record (written when the region marker store to the TB MMIO phase-marker register is observed on the data bus with the region tuple in its data), sampled at the region's first regime-relevant event: the first retirement after the marker record, for pmp_regime after the prologue's last PMP CSR write retired (Phase log table); condition: marker observed && that retirement; anti-vacuity: one sample per region, never at the marker itself; the marker is emitted by the generated program at the region boundary and the first retirement proves the region's code ran, so a value bin proves the program actually executed under that knob value and a `_tr` bin proves two consecutive executed regions differed.
- Coverpoints:
  - cp_instr_mix = rec.value of knob:instr_mix [F: F-ISA-001, F-ISA-023, F-MUL-001, F-CMP-001, F-CMP-039, F-BIT-001, F-CSR-001, F-DMEM-015]: bins isa_only{RV32I only}, m_heavy{~40% mul/div}, compressed_heavy{~60% Zca/Zcb/Zcmp incl. cm.push/pop}, bitmanip_heavy{~40% legal RV32BOTEarlGrey}, csr_heavy{~30% CSR ops incl. 2% illegal accesses}, ls_heavy{~50% loads/stores, 30% misaligned}, branch_heavy{~40% branches/jumps, short loops}, mixed{flat weights}
  - cp_instr_mix_tr = knob:instr_mix across consecutive regions [F: F-ISA-001, F-ISA-023, F-MUL-001, F-CMP-001, F-CMP-039, F-BIT-001, F-CSR-001, F-DMEM-015]: bins isa_only_to_m_heavy, isa_only_to_compressed_heavy, isa_only_to_bitmanip_heavy, isa_only_to_csr_heavy, isa_only_to_ls_heavy, isa_only_to_branch_heavy, isa_only_to_mixed, m_heavy_to_isa_only, m_heavy_to_compressed_heavy, m_heavy_to_bitmanip_heavy, m_heavy_to_csr_heavy, m_heavy_to_ls_heavy, m_heavy_to_branch_heavy, m_heavy_to_mixed, compressed_heavy_to_isa_only, compressed_heavy_to_m_heavy, compressed_heavy_to_bitmanip_heavy, compressed_heavy_to_csr_heavy, compressed_heavy_to_ls_heavy, compressed_heavy_to_branch_heavy, compressed_heavy_to_mixed, bitmanip_heavy_to_isa_only, bitmanip_heavy_to_m_heavy, bitmanip_heavy_to_compressed_heavy, bitmanip_heavy_to_csr_heavy, bitmanip_heavy_to_ls_heavy, bitmanip_heavy_to_branch_heavy, bitmanip_heavy_to_mixed, csr_heavy_to_isa_only, csr_heavy_to_m_heavy, csr_heavy_to_compressed_heavy, csr_heavy_to_bitmanip_heavy, csr_heavy_to_ls_heavy, csr_heavy_to_branch_heavy, csr_heavy_to_mixed, ls_heavy_to_isa_only, ls_heavy_to_m_heavy, ls_heavy_to_compressed_heavy, ls_heavy_to_bitmanip_heavy, ls_heavy_to_csr_heavy, ls_heavy_to_branch_heavy, ls_heavy_to_mixed, branch_heavy_to_isa_only, branch_heavy_to_m_heavy, branch_heavy_to_compressed_heavy, branch_heavy_to_bitmanip_heavy, branch_heavy_to_csr_heavy, branch_heavy_to_ls_heavy, branch_heavy_to_mixed, mixed_to_isa_only, mixed_to_m_heavy, mixed_to_compressed_heavy, mixed_to_bitmanip_heavy, mixed_to_csr_heavy, mixed_to_ls_heavy, mixed_to_branch_heavy
  - cp_priv_regime = rec.value of knob:priv_regime [F: F-PRV-001, F-PRV-002, F-PRV-003, F-PRV-006, F-IRQ-008]: bins m_only{all M}, u_heavy{~70% of instructions in U-mode}, alternating{mode switch every 10..100 instructions via mret/ecall}
  - cp_priv_regime_tr = knob:priv_regime across consecutive regions [F: F-PRV-001, F-PRV-002, F-PRV-003, F-PRV-006, F-IRQ-008]: bins m_only_to_u_heavy, m_only_to_alternating, u_heavy_to_m_only, u_heavy_to_alternating, alternating_to_m_only, alternating_to_u_heavy
  - cp_pmp_regime = rec.value of knob:pmp_regime [F: F-PMP-006, F-PMP-021, F-PMP-023, F-PMP-024, F-PMP-045, F-PMP-053, F-PMP-056]: bins off{all A=OFF, mseccfg=0}, sparse{2..4 of PMPNumRegions regions, TOR/NAPOT}, dense{all PMPNumRegions regions, NA4/NAPOT/TOR, <= 25% locked, overlapping}, mml_on{mseccfg.MML=1 (+MMWP 50%, RLB 50%) with a dense MML-legal set}
  - cp_pmp_regime_tr = knob:pmp_regime across consecutive regions [F: F-PMP-006, F-PMP-021, F-PMP-023, F-PMP-024, F-PMP-015, F-PMP-045, F-PMP-053, F-PMP-056]: bins off_to_sparse, off_to_dense, off_to_mml_on, sparse_to_off, sparse_to_dense, sparse_to_mml_on, dense_to_off, dense_to_sparse, dense_to_mml_on, mml_on_to_off{reachable only across a mid-run reset}, mml_on_to_sparse{same}, mml_on_to_dense{same}; the three mml_on_to_* bins are legal, not ignored: mseccfg.MML is sticky within a reset epoch (F-PMP-023) but clears to 0 at reset (F-PMP-015), and gen_xif_reset continues the schedule across the reset (tp_xcut.md Regime schedule), so they are sampled on the first region after a reset whose predecessor region was mml_on (TP-REG-028)
- Crosses:
  - cr_priv_x_pmp = cp_priv_regime x cp_pmp_regime: required bins (12): m_only_off, m_only_sparse, m_only_dense, m_only_mml_on, u_heavy_off, u_heavy_sparse, u_heavy_dense, u_heavy_mml_on, alternating_off, alternating_sparse, alternating_dense, alternating_mml_on
  - cr_mix_x_priv = cp_instr_mix x cp_priv_regime: required bins (24): isa_only_m_only, isa_only_u_heavy, isa_only_alternating, m_heavy_m_only, m_heavy_u_heavy, m_heavy_alternating, compressed_heavy_m_only, compressed_heavy_u_heavy, compressed_heavy_alternating, bitmanip_heavy_m_only, bitmanip_heavy_u_heavy, bitmanip_heavy_alternating, csr_heavy_m_only, csr_heavy_u_heavy, csr_heavy_alternating, ls_heavy_m_only, ls_heavy_u_heavy, ls_heavy_alternating, branch_heavy_m_only, branch_heavy_u_heavy, branch_heavy_alternating, mixed_m_only, mixed_u_heavy, mixed_alternating
- Adopted (riscv-dv): none
- TP items: TP-REG-015, TP-REG-016, TP-REG-017, TP-REG-028

### CG-REG-007: gen_cg_reg_schedule
- Features: F-IMEM-001, F-DMEM-001, F-IRQ-001, F-DBG-001, F-IC-008, F-IMEM-022, F-ISA-001, F-PRV-001, F-PMP-006
- Sample: ONE instant only: the phase-END record of a TB-side phase or program-side region, written when the phase's boundary fires (for the last phase: when the run ends after the phase reached the lower bound of its duration class); the run-constant banner values (schedule length K, number of pinned knobs, derived-or-supplied schedule) are carried into every phase record, so there is no separate time-0 banner sample and no end-of-run sample; condition: record present && the phase reached its first regime-relevant event (Phase log table); anti-vacuity: a record exists only for a phase the agents consumed (gen_chk_regime asserts banner K == logged phases and measured durations in class), so a hit proves the schedule generator produced and the agents executed that phase under that run configuration; side-specific coverpoints carry `iff rec.side`. Bins map to the umbrella feature of each interface the regimes stress (DV_prompt Section 6 layer 3 is a stimulus rule, not a DUT feature; see Open questions in tp_xcut.md).
- Coverpoints:
  - cp_phase_count = rec.K (schedule length from the banner, carried in every record) [F: F-IMEM-001, F-DMEM-001, F-IRQ-001, F-DBG-001, F-IC-008, F-IMEM-022, F-ISA-001, F-PRV-001, F-PMP-006]: bins k1{1}, k2{2}, k3_4{3..4}, k5_plus{>= 5}
  - cp_duration_class = rec.measured_cycles of the phase iff rec.side == tb [F: F-IMEM-001, F-DMEM-001, F-IRQ-001, F-DBG-001, F-IC-008, F-IMEM-022]: bins short{500..2000 cycles}, medium{2001..20000 cycles}, long{20001..100000 cycles}
  - cp_region_duration_class = rec.measured_retirements of the region iff rec.side == program [F: F-ISA-001, F-PRV-001, F-PMP-006]: bins short{100..500 retired instructions}, medium{501..5000}, long{5001..20000}
  - cp_knobs_changed = number of TB-side knobs whose applied value differs from the previous phase iff rec.side == tb && rec.phase_idx > 0 [F: F-IMEM-001, F-DMEM-001, F-IRQ-001, F-DBG-001, F-IC-008, F-IMEM-022]: bins one{1}, two_three{2..3}, four_plus{>= 4}
  - cp_pinned_count = number of scheduled knobs pinned on the command line in this run (`+gen_knob_<name>=<value>` given explicitly; banner value carried in every record; tp_xcut.md knob table) [F: F-IMEM-001, F-DMEM-001, F-IRQ-001, F-DBG-001, F-IC-008, F-IMEM-022, F-ISA-001, F-PRV-001, F-PMP-006]: bins none{0}, one{1}, several{2..N_SCHED-1}, all{N_SCHED, where N_SCHED = 19 scheduled knobs: the 17 brief knobs plus imem_intg_err_rate and dmem_intg_err_rate; mcounteren_writable is a run constant, not scheduled}
  - cp_phase_idx = rec.phase_idx [F: F-IMEM-001, F-DMEM-001, F-IRQ-001, F-DBG-001, F-IC-008, F-IMEM-022, F-ISA-001, F-PRV-001, F-PMP-006]: bins first{0}, middle{1..K-2}, last{K-1}
- Crosses:
  - cr_count_x_dur = cp_phase_count x cp_duration_class: required bins (12): k1_short, k1_medium, k1_long, k2_short, k2_medium, k2_long, k3_4_short, k3_4_medium, k3_4_long, k5_plus_short, k5_plus_medium, k5_plus_long
  - cr_pinned_x_changed = cp_pinned_count x cp_knobs_changed: required bins (9): none_one, none_two_three, none_four_plus, one_one, one_two_three, one_four_plus, several_one, several_two_three, several_four_plus; ignore all_one, all_two_three, all_four_plus: with every scheduled knob pinned no TB-side knob can change at a boundary, so cp_knobs_changed's iff is never true
- Adopted (riscv-dv): none
- TP items: TP-REG-018, TP-REG-019

### CG-REG-008: gen_cg_reg_inflight_transition
- Features: F-IMEM-008, F-IMEM-016, F-DMEM-008, F-DMEM-030, F-IRQ-016, F-IRQ-020, F-IRQ-025, F-IRQ-045, F-DBG-007, F-DBG-010, F-DBG-056, F-CMP-056, F-CMP-057, F-RST-017, F-IC-029, F-IMEM-009, F-DMEM-010, F-IRQ-027, F-DBG-027, F-DBG-030
- Sample: TB-side phase boundary (and the program-side marker record for the program group); one sample per (changed KNOB, in-flight flag true at the boundary cycle), i.e. per knob and not per group: two knobs of one group changing at the same boundary each produce their own sample and cp_knob_group is derived from cp_knob_changed; flags from S1, S4, S7, S9, S11, S14; condition: that knob's applied value changed at this boundary; anti-vacuity: the boundary is a scheduled TB event and the flags come from monitors, so a hit proves the regime changed while the DUT was in that state; `none` is sampled only when no flag is true.
- Coverpoints:
  - cp_knob_group = group of the changed knob (derived from cp_knob_changed) [F: F-IMEM-008, F-IMEM-009, F-IMEM-016, F-DMEM-008, F-DMEM-010, F-DMEM-030, F-IRQ-016, F-IRQ-025, F-IRQ-027, F-IRQ-045, F-DBG-007, F-DBG-027, F-DBG-030, F-DBG-056, F-IC-029, F-CMP-056, F-CMP-057, F-IRQ-020, F-DBG-010, F-RST-017]: bins imem{imem_*}, dmem{dmem_*}, irq{irq_*}, dbg_fe{debug_req_regime, fetch_enable_regime}, icache{icache_ecc_err_rate, scr_key_delay}, program{instr_mix, priv_regime, pmp_regime}
  - cp_knob_changed = name of the changed knob (one sample per changed knob; bin name == rec.knob) [F: F-IMEM-008, F-IMEM-009, F-IMEM-016, F-DMEM-008, F-DMEM-010, F-DMEM-030, F-IRQ-016, F-IRQ-025, F-IRQ-027, F-IRQ-045, F-DBG-007, F-DBG-027, F-DBG-030, F-DBG-056, F-IC-029, F-CMP-056, F-CMP-057, F-IRQ-020, F-DBG-010, F-RST-017]: bins imem_gnt_delay, imem_rvalid_delay, imem_err_rate, imem_outstanding_cap, imem_intg_err_rate, dmem_gnt_delay, dmem_rvalid_delay, dmem_err_rate, dmem_intg_err_rate, irq_regime, irq_line_mix, irq_hold, debug_req_regime, fetch_enable_regime, icache_ecc_err_rate, scr_key_delay, instr_mix, priv_regime, pmp_regime
  - cp_inflight_event = DUT state at the boundary cycle [F: F-IMEM-008, F-IMEM-009, F-IMEM-016, F-DMEM-008, F-DMEM-010, F-DMEM-030, F-IRQ-016, F-IRQ-025, F-IRQ-027, F-IRQ-045, F-RST-017, F-IC-029, F-DBG-007, F-DBG-056, F-DBG-030, F-DBG-027, F-CMP-056, F-CMP-057, F-IRQ-020, F-DBG-010]: bins fetch_outstanding{S1 >= 1}, data_outstanding{S4 >= 1}, irq_pending{irq_pending_o || irq_nm_i, no handler entered yet}, in_wfi{S9 sleeping}, in_debug{dbg_mode_q}, mid_zcmp{S14}, none{no flag true}
- Crosses:
  - cr_group_x_inflight = cp_knob_group x cp_inflight_event: required bins (31): imem_fetch_outstanding, imem_data_outstanding, imem_irq_pending, imem_in_wfi, imem_in_debug, imem_mid_zcmp, dmem_fetch_outstanding, dmem_data_outstanding, dmem_irq_pending, dmem_in_wfi, dmem_in_debug, dmem_mid_zcmp, irq_fetch_outstanding, irq_data_outstanding, irq_irq_pending, irq_in_wfi, irq_in_debug, irq_mid_zcmp, dbg_fe_fetch_outstanding, dbg_fe_data_outstanding, dbg_fe_irq_pending, dbg_fe_in_wfi, dbg_fe_in_debug, dbg_fe_mid_zcmp, icache_fetch_outstanding, icache_data_outstanding, icache_irq_pending, icache_in_wfi, icache_in_debug, icache_mid_zcmp, program_irq_pending; ignore imem_none, dmem_none, irq_none, dbg_fe_none, icache_none, program_none, program_fetch_outstanding, program_data_outstanding, program_in_wfi, program_in_debug, program_mid_zcmp: `none` is not an in-flight event; the program-side boundary is the retirement of the marker store, at which a fetch is almost always outstanding and the marker's own data access is outstanding (vacuous), the core is executing (never in WFI), the marker is program code (never in debug mode or inside a Zcmp sequence)
  - cr_knob_x_inflight = cp_knob_changed x cp_inflight_event: required bins (25): imem_gnt_delay_fetch_outstanding, imem_rvalid_delay_fetch_outstanding, imem_err_rate_fetch_outstanding, imem_outstanding_cap_fetch_outstanding, imem_intg_err_rate_fetch_outstanding, dmem_gnt_delay_data_outstanding, dmem_rvalid_delay_data_outstanding, dmem_err_rate_data_outstanding, dmem_intg_err_rate_data_outstanding, irq_regime_irq_pending, irq_line_mix_irq_pending, irq_hold_irq_pending, irq_regime_in_wfi, irq_line_mix_in_wfi, debug_req_regime_in_wfi, fetch_enable_regime_in_wfi, debug_req_regime_in_debug, irq_regime_in_debug, imem_err_rate_in_debug, dmem_err_rate_in_debug, dmem_gnt_delay_mid_zcmp, dmem_rvalid_delay_mid_zcmp, dmem_err_rate_mid_zcmp, irq_regime_mid_zcmp, debug_req_regime_mid_zcmp; ignore all other 108 combinations: the knob does not act on the completion of that in-flight event (e.g. a scramble-key regime change while a data access is outstanding); the timing of such changes is covered at group level by cr_group_x_inflight
- Adopted (riscv-dv): none
- TP items: TP-REG-018, TP-REG-020, TP-REG-021, TP-REG-022, TP-REG-023, TP-REG-024, TP-REG-025

### CG-XIF-001: gen_cg_xif_data_err_x_fetch_irq
- Features: F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-030, F-DMEM-036, F-DMEM-037, F-DMEM-038, F-IMEM-008, F-IRQ-017, F-IRQ-022, F-DBG-003, F-EXC-025, F-EXC-027, F-EXC-069
- Sample: S6 dbus_err_rsp (data_rvalid_i && data_err_i); condition: error response on the data bus; anti-vacuity: error responses exist only at the dmem_err_rate injection rate (zero under `none`), so a hit proves an errored data response returned while the crossed fetch/interrupt state held in the same cycle (all three read at the pins in the data_rvalid_i cycle, no RVFI anchoring involved). Ownership (Critic S-10): this group owns the DV_prompt Section 6 boundary triple "fetch stalled x data error returning x interrupt pending" (cr_fetch_x_async.stalled_irq_pending); CG-EXC-013 (exc_irq) owns the exception-side view of the same coincidence and CG-IRQ-012's copy is dropped by the exc_irq area. Timing premise (C-6, X-9): the coincidence itself is read at the pins in the error cycle; WHEN the asynchronous entry happens is a separate coverpoint (cp_taken_when) attributed by the following records (C-3), because the trap entry clears mstatus.MIE (rtl/ibex_cs_registers.sv:924) and irq_enabled = MIE | (priv == U) (rtl/ibex_controller.sv:490): an ordinary interrupt pending at a synchronous exception is taken only after the fault handler's mret or an MIE write, while an NMI (:498-500) or a debug request is taken in the first empty-ID DECODE after the exception's FLUSH, before the handler's first instruction.
- Coverpoints:
  - cp_fetch_state = instruction bus state in the error cycle [F: F-IMEM-008, F-DMEM-030]: bins stalled{S2: >= 1 fetch outstanding and no rvalid}, rsp_same_cycle{ibus_outst >= 1 && instr_rvalid_i}, idle{ibus_outst == 0}
  - cp_async = asynchronous requests in the error cycle [F: F-IRQ-017, F-IRQ-022, F-DBG-003, F-EXC-069]: bins none{none of irq_pending_o, irq_nm_i, debug_req_i}, irq_pending{irq_pending_o only}, nmi{irq_nm_i only}, debug_req{debug_req_i only}, multiple{>= 2 of the three}
  - cp_err_half = S6 err_half [F: F-DMEM-021, F-DMEM-022, F-DMEM-023, F-DMEM-036, F-DMEM-037, F-DMEM-038]: bins single{aligned or non-split access}, split_first{first half of a misaligned pair, F-DMEM-021}, split_second{second half, F-DMEM-022}
  - cp_we = data_we_o at the grant of the errored request [F: F-EXC-025, F-EXC-027]: bins load{0}, store{1}
  - cp_taken_when = when the asynchronous entry happened relative to the fault handler, attributed by the records after the fault's rvfi_trap record (C-3, C-6), iff cp_async != none [F: F-IRQ-017, F-IRQ-022, F-DBG-003, F-EXC-069]: bins before_handler{the record after the trap record is the entry itself: the NMI handler's first record (rvfi_intr = 1, rvfi_ext_nmi) or the first debug-ROM record, with no fault-handler instruction in between (taken in the first empty-ID DECODE after the exception's FLUSH; mepc / dpc read back == mtvec BASE)}, after_mret{the ordinary interrupt's handler record (rvfi_intr = 1) follows the fault handler's mret record (MIE <- MPIE), X-9}, after_mie_write{the handler record follows a retired mstatus write setting MIE inside the fault handler, before its mret}, released{the source deasserted (irq_hold = pulse, or a debug_req_i pulse) before any entry: no entry record within GEN_IRQ_ENTRY_BOUND_RECORDS of the release}
- Crosses:
  - cr_fetch_x_async = cp_fetch_state x cp_async: required bins (15): stalled_none, stalled_irq_pending, stalled_nmi, stalled_debug_req, stalled_multiple, rsp_same_cycle_none, rsp_same_cycle_irq_pending, rsp_same_cycle_nmi, rsp_same_cycle_debug_req, rsp_same_cycle_multiple, idle_none, idle_irq_pending, idle_nmi, idle_debug_req, idle_multiple
  - cr_half_x_async = cp_err_half x cp_async: required bins (15): single_none, single_irq_pending, single_nmi, single_debug_req, single_multiple, split_first_none, split_first_irq_pending, split_first_nmi, split_first_debug_req, split_first_multiple, split_second_none, split_second_irq_pending, split_second_nmi, split_second_debug_req, split_second_multiple
  - cr_async_x_taken = cp_async x cp_taken_when: required bins (9): irq_pending_after_mret, irq_pending_after_mie_write, irq_pending_released, nmi_before_handler, nmi_released, debug_req_before_handler, debug_req_released, multiple_before_handler, multiple_released; ignore irq_pending_before_handler: the trap entry clears mstatus.MIE and the fault handler runs in M, so irq_enabled = MIE | (priv == U) is 0 until the mret or an MIE write (X-9, rtl/ibex_cs_registers.sv:924, rtl/ibex_controller.sv:490); ignore nmi_after_mret, nmi_after_mie_write, debug_req_after_mret, debug_req_after_mie_write, multiple_after_mret, multiple_after_mie_write: an NMI (handle_irq, rtl/ibex_controller.sv:498-500) and a debug request ignore MIE and are taken in the first empty-ID DECODE after the FLUSH, before the handler's first instruction, and `multiple` always contains one of them; ignore none_before_handler, none_after_mret, none_after_mie_write, none_released: cp_taken_when is sampled only with an asynchronous source high in the error cycle
- Adopted (riscv-dv): none
- TP items: TP-XIF-001

### CG-XIF-002: gen_cg_xif_fetch_err_x_async
- Features: F-IMEM-011, F-IMEM-012, F-IMEM-013, F-IMEM-014, F-EXC-003, F-EXC-005, F-EXC-006, F-IRQ-021, F-DBG-030, F-FE-015, F-FE-023, F-BTALU-010
- Sample: S3 ibus_err_rsp (instr_rvalid_i && instr_err_i); condition: error beat on the instruction bus; anti-vacuity: error beats exist only at the imem_err_rate injection rate; a hit proves an errored fetch beat returned while the crossed state held.
- Coverpoints:
  - cp_async = asynchronous requests in the beat cycle (pins read in the instr_rvalid_i cycle) [F: F-IRQ-021, F-DBG-030]: bins none{none of irq_pending_o, irq_nm_i, debug_req_i}, irq_pending{irq_pending_o only}, nmi{irq_nm_i only}, debug_req{debug_req_i only}, multiple{>= 2}
  - cp_window = trap-entry window the beat falls in (S18, exact at the boundary) [F: F-EXC-005, F-EXC-006, F-FE-023, F-BTALU-010]: bins irq_taken_window{beat inside an interrupt/NMI entry window}, debug_entry_window{beat inside a debug entry window}, normal{neither}
  - cp_consumed = fate of the errored word [F: F-IMEM-011, F-IMEM-012, F-IMEM-013, F-IMEM-014, F-EXC-003, F-FE-015]: bins executed_trap{a later rvfi_trap record with instruction-access-fault semantics has rvfi_pc_rdata == beat address or beat address - 2 (err_plus2, F-IMEM-013)}, discarded{no such record before the next S19 redirect, F-IMEM-012}
  - cp_outst_at_err = S1 in the beat cycle (including the beat) [F: F-IMEM-011, F-FE-015]: bins one{1}, few{2..2*IC_LINE_BEATS}, many{2*IC_LINE_BEATS+1..NUM_FB*IC_LINE_BEATS}
- Crosses:
  - cr_async_x_window = cp_async x cp_window: required bins (15): none_irq_taken_window, none_debug_entry_window, none_normal, irq_pending_irq_taken_window, irq_pending_debug_entry_window, irq_pending_normal, nmi_irq_taken_window, nmi_debug_entry_window, nmi_normal, debug_req_irq_taken_window, debug_req_debug_entry_window, debug_req_normal, multiple_irq_taken_window, multiple_debug_entry_window, multiple_normal
  - cr_consumed_x_async = cp_consumed x cp_async: required bins (10): executed_trap_none, executed_trap_irq_pending, executed_trap_nmi, executed_trap_debug_req, executed_trap_multiple, discarded_none, discarded_irq_pending, discarded_nmi, discarded_debug_req, discarded_multiple
- Adopted (riscv-dv): none
- TP items: TP-XIF-005

### CG-XIF-003: gen_cg_xif_data_outst_x_async
- Features: F-DMEM-030, F-DMEM-021, F-DMEM-022, F-DMEM-025, F-DMEM-026, F-DBG-003, F-IRQ-017, F-IRQ-018, F-IRQ-030, F-IRQ-040, F-IRQ-041, F-EXC-035, F-EXC-069, F-SEC-015, F-SEC-016, F-DBG-004, F-DBG-036, F-IRQ-022, F-IRQ-035
- Sample: rising edge of an asynchronous request (irq_pending_o 0->1, irq_nm_i 0->1, debug_req_i 0->1, or an alert_major_bus_o pulse coincident with data_rvalid_i = internal-NMI arming, F-IRQ-040) while S4 dbus_outst >= 1; one rule for the count: for the three pin edges dbus_outst is the count in the edge cycle (a response completing in that same cycle still counts); for nmi_int the arming event IS a data response, so dbus_outst is counted AFTER that corrupted response retires and the crossed access is the OTHER half of a misaligned pair still in flight (a corrupted response that completes the only outstanding access does not sample); condition: dbus_outst >= 1 under that rule; anti-vacuity: async edges are driver events and dbus_outst >= 1 holds only inside the slow-response windows of the dmem knobs; a hit proves the request arrived with a data access in flight.
- Coverpoints:
  - cp_async_src = which request rose [F: F-IRQ-017, F-IRQ-018, F-IRQ-030, F-IRQ-035, F-IRQ-040, F-IRQ-041, F-DBG-003, F-DBG-004, F-SEC-015, F-SEC-016]: bins irq_maskable{irq_pending_o 0->1}, nmi_ext{irq_nm_i 0->1}, nmi_int{alert_major_bus_o pulse in a data_rvalid_i cycle = integrity error on a data response, F-IRQ-040; count rule per Sample}, debug_req{debug_req_i 0->1}
  - cp_dbus_state = S5 state at the edge [F: F-DMEM-030, F-DMEM-021, F-DMEM-022, F-DMEM-025, F-DMEM-026, F-DBG-036]: bins single_outst{one non-split access outstanding}, split_first_outst{first half granted, second half not yet granted}, split_both_outst{dbus_outst == 2}, split_second_outst{first half answered, second half outstanding}
  - cp_rsp_outcome = the outstanding access finally returns [F: F-IRQ-022, F-DBG-003, F-EXC-035, F-EXC-069]: bins ok{data_err_i = 0}, err{data_err_i = 1, exception wins over the async request, F-IRQ-022/F-DBG-003}
  - cp_we = type of the outstanding access (data_we_o at its grant) [F: F-SEC-015, F-SEC-016]: bins load{0}, store{1}
- Crosses:
  - cr_src_x_state = cp_async_src x cp_dbus_state: required bins (13): irq_maskable_single_outst, irq_maskable_split_first_outst, irq_maskable_split_both_outst, irq_maskable_split_second_outst, nmi_ext_single_outst, nmi_ext_split_first_outst, nmi_ext_split_both_outst, nmi_ext_split_second_outst, nmi_int_split_both_outst, debug_req_single_outst, debug_req_split_first_outst, debug_req_split_both_outst, debug_req_split_second_outst; ignore nmi_int_single_outst, nmi_int_split_first_outst, nmi_int_split_second_outst: the corrupted response completes the only access in flight (a single access; a first half whose second half is not yet granted; a second half whose first half was already answered), so under the nmi_int count rule dbus_outst == 0 after it retires and the sample condition is false; only split_both_outst (corrupted first-half response while the second half is outstanding) is reachable
  - cr_src_x_outcome_x_we = cp_async_src x cp_rsp_outcome x cp_we: required bins (16): irq_maskable_ok_load, irq_maskable_ok_store, irq_maskable_err_load, irq_maskable_err_store, nmi_ext_ok_load, nmi_ext_ok_store, nmi_ext_err_load, nmi_ext_err_store, nmi_int_ok_load, nmi_int_ok_store, nmi_int_err_load, nmi_int_err_store, debug_req_ok_load, debug_req_ok_store, debug_req_err_load, debug_req_err_store
- Adopted (riscv-dv): none
- TP items: TP-XIF-002, TP-XIF-003, TP-XIF-008, TP-XIF-009

### CG-XIF-004: gen_cg_xif_wfi_wake
- Features: F-IRQ-045, F-IRQ-046, F-IRQ-047, F-IRQ-048, F-IRQ-049, F-IRQ-050, F-IRQ-051, F-IRQ-054, F-IRQ-064, F-DMEM-031, F-IC-029, F-RST-015, F-RST-017, F-PRV-016, F-PRV-017, F-PRV-018, F-PRV-019, F-PRV-020, F-FE-021, F-IMEM-021, F-DBG-009, F-DBG-044
- Sample: the wake instant after a WFI retirement (S17): the core_busy_o Off->On edge when Off lasted >= 2 consecutive cycles (SLEEP entered), otherwise the WB-exit cycle (S18) of the first record after the WFI record. C-5 (X-8): an unstepped WFI gives exactly one ctrl_busy = 0 cycle in WAIT_SLEEP (rtl/ibex_controller.sv:598-604), visible on core_busy_o only with no fetch beat outstanding, no invalidation and an idle LSU (rtl/ibex_core.sv:521), even when the wake condition is already true (SLEEP, :606-621, exits at once); a stepped WFI (dcsr.step = 1, not in debug mode) never reaches WAIT_SLEEP (FLUSH -> DBG_TAKEN_IF, :985-987) and shows no Off cycle at all; so an Off of <= 1 cycle is never sleep; condition: a wfi_retired since the previous sample; anti-vacuity: WFIs are program events (instr_mix all values include them at low weight); a hit proves the sleep/wake path completed with the crossed wake source and pending-transaction state.
- Coverpoints:
  - cp_slept = core_busy_o behaviour after the WFI [F: F-IRQ-045, F-IRQ-048, F-IRQ-051, F-DBG-044, F-RST-017, F-DMEM-031]: bins slept{IbexMuBiOff for >= 2 consecutive cycles: SLEEP held}, no_sleep{Off for <= 1 cycle: wake condition already true (F-IRQ-048), debug-mode WFI (WAIT_SLEEP then immediate SLEEP exit, F-DBG-059), stepped WFI (no WAIT_SLEEP at all, core_busy_o never Off, F-IRQ-051 / F-DBG-044), TW trap, or the one-cycle dip masked by an outstanding fetch beat, an invalidation or a busy LSU (F-RST-017, F-DMEM-031)}
  - cp_wake_src = highest-priority source high at the wake instant (debug_req > nmi > irq) [F: F-PRV-020, F-IRQ-047, F-IRQ-049, F-IRQ-050, F-DBG-009, F-RST-015]: bins irq_maskable{irq_pending_o}, nmi{irq_nm_i}, debug_req{debug_req_i}, none_needed{no_sleep with none of the three high: dcsr.step, debug mode or the TW trap}
  - cp_wake_result = first record after the WFI record [F: F-IRQ-046, F-IRQ-064, F-PRV-016, F-PRV-017, F-PRV-018, F-PRV-019, F-FE-021, F-DBG-044]: bins trap_taken{rvfi_intr = 1}, resumed_no_trap{rvfi_pc_rdata == WFI pc + 4 and rvfi_intr = 0, F-IRQ-046/F-PRV-019}, debug_entered{rvfi_ext_debug_mode = 1 and the WFI record was not: a debug_req_i wake, or the step entry after a stepped WFI, which goes FLUSH -> DBG_TAKEN_IF without sleeping (rtl/ibex_controller.sv:985-987; dpc = WFI + 4, dcsr.cause = 4; F-IRQ-051/F-DBG-044)}, illegal_trap{the WFI record itself has rvfi_trap = 1: U-mode with TW = 1, F-PRV-016}
  - cp_pending_at_wfi = activity the WFI had to wait out: fetch and icache state read in the WFI record's WB-exit cycle (S18), the data side at the WFI's ID entry (S21), because at the WFI's own WB exit the data bus is always idle (the wfi is a special_req that waits in DECODE for ready_wb_i, rtl/ibex_controller.sv:668-678, then FLUSH -> WAIT_SLEEP; fact-check TP-XIF-004) [F: F-RST-017, F-DMEM-031, F-IRQ-054, F-IC-029, F-IMEM-021]: bins none{S1 == 0 && !S21 && no S12 invalidation && !S13}, fetch_outst{S1 >= 1 at WB exit, F-RST-017}, data_outst{S21: the WFI entered ID while the preceding load/store's response was outstanding (WFI record == load/store record + 1 cycle), F-DMEM-031/F-IRQ-054}, icache_busy{S12 invalidating or S13 key_withheld at WB exit, F-IC-029}
  - cp_mode_at_wfi = rvfi_mode of the WFI record [F: F-PRV-016, F-PRV-017, F-PRV-018]: bins m{2'b11}, u{2'b00}
- Crosses:
  - cr_src_x_result = cp_wake_src x cp_wake_result: required bins (11): irq_maskable_trap_taken, irq_maskable_resumed_no_trap, irq_maskable_debug_entered, nmi_trap_taken, nmi_resumed_no_trap, nmi_debug_entered, debug_req_trap_taken, debug_req_resumed_no_trap, debug_req_debug_entered, none_needed_resumed_no_trap, none_needed_debug_entered{reached only through dcsr.step = 1: the stepped WFI goes FLUSH -> DBG_TAKEN_IF (rtl/ibex_controller.sv:985-987, never WAIT_SLEEP) with debug_req_i low, F-IRQ-051 / F-DBG-044}; ignore none_needed_trap_taken: with none of irq_pending_o, irq_nm_i, debug_req_i high at the wake instant no interrupt or NMI is pending, so the first record after the WFI cannot carry rvfi_intr (an internal NMI armed by a corrupted load response outstanding at the WFI is CG-XIF-003 nmi_int, not a WFI wake); ignore none_needed_illegal_trap, irq_maskable_illegal_trap, nmi_illegal_trap, debug_req_illegal_trap: the TW illegal-instruction trap is raised on the WFI itself before any sleep or wake, so no wake source is involved (single bin illegal_trap is kept in cr_mode_x_result)
  - cr_pending_x_src = cp_pending_at_wfi x cp_wake_src: required bins (16): none_irq_maskable, none_nmi, none_debug_req, none_none_needed, fetch_outst_irq_maskable, fetch_outst_nmi, fetch_outst_debug_req, fetch_outst_none_needed, data_outst_irq_maskable, data_outst_nmi, data_outst_debug_req, data_outst_none_needed, icache_busy_irq_maskable, icache_busy_nmi, icache_busy_debug_req, icache_busy_none_needed
  - cr_mode_x_result = cp_mode_at_wfi x cp_wake_result: required bins (7): m_trap_taken, m_resumed_no_trap, m_debug_entered, u_trap_taken, u_resumed_no_trap, u_debug_entered, u_illegal_trap; ignore m_illegal_trap: mstatus.TW does not affect M-mode WFI (F-PRV-017)
- Adopted (riscv-dv): none
- TP items: TP-XIF-004

### CG-XIF-005: gen_cg_xif_icache_fill_x_event
- Features: F-IC-010, F-IC-020, F-IC-021, F-IC-023, F-IC-024, F-IC-025, F-IC-026, F-IC-027, F-IC-029, F-IC-030, F-IC-031, F-IC-036, F-IC-037, F-IC-041, F-IMEM-015, F-IMEM-016, F-IMEM-017, F-ISA-030, F-SEC-021, F-IMEM-012, F-IC-011, F-IC-028, F-IC-032, F-IC-033, F-IC-035, F-SEC-001
- Sample: one of the events below occurring while S12 fill_inflight or S13 key_withheld; condition: (fill_inflight || key_withheld) && event; anti-vacuity: fill_inflight requires the cache to be enabled by the program and beats to be outstanding; events are program (fence.i, redirect, icache_disable) or agent (bus error, ECC injection, key) events, so a hit proves the event coincided with a fill in flight.
- Coverpoints:
  - cp_event = event type [F: F-ISA-030, F-IC-023, F-IC-025, F-IMEM-016, F-IMEM-017, F-IC-020, F-IC-021, F-IC-037, F-IMEM-015, F-IC-036, F-IMEM-012, F-IC-030, F-IC-031, F-IC-032, F-IC-033, F-IC-035, F-SEC-001, F-IC-027, F-IC-041, F-SEC-021]: bins fence_i{S15}, redirect{S19 taken branch/jump/trap retirement, RVFI-derived; event cycle = the redirect cycle of S19}, bus_err_beat{S3 on a fill beat}, ecc_inject{RAM model injects on a lookup}, icache_disable{retired CSR write clearing cpuctrlsts.icache_enable, commit cycle per S18, F-IC-027/041}, key_req{ic_scr_key_req_o pulse}
  - cp_fill_state = S1 at the event [F: F-IC-026, F-IMEM-016, F-IC-020]: bins one_beat_outst{1}, two_to_line{2..IC_LINE_BEATS}, multi_line{IC_LINE_BEATS+1..NUM_FB*IC_LINE_BEATS}
  - cp_key = scramble key state [F: F-IC-010, F-IC-011, F-IC-024, F-IC-029, F-SEC-021]: bins valid{ic_scr_key_valid_i = 1}, withheld{S13}
  - cp_inval = invalidation walk [F: F-IC-023, F-IC-025, F-IC-026, F-IC-028]: bins none{no tag-write walk in progress}, invalidating{S12 invalidating}
  - cp_stale_fill_outcome = how the fill made stale by the redirect completes, iff cp_event == redirect [F: F-IMEM-016, F-IC-020, F-IMEM-015, F-IC-036]: bins completed_ok{all its beats return without error}, completed_err{at least one stale beat returns instr_err_i = 1, F-IMEM-016/F-IC-020}
- Crosses:
  - cr_event_x_fill = cp_event x cp_fill_state: required bins (18): fence_i_one_beat_outst, fence_i_two_to_line, fence_i_multi_line, redirect_one_beat_outst, redirect_two_to_line, redirect_multi_line, bus_err_beat_one_beat_outst, bus_err_beat_two_to_line, bus_err_beat_multi_line, ecc_inject_one_beat_outst, ecc_inject_two_to_line, ecc_inject_multi_line, icache_disable_one_beat_outst, icache_disable_two_to_line, icache_disable_multi_line, key_req_one_beat_outst, key_req_two_to_line, key_req_multi_line
  - cr_event_x_key = cp_event x cp_key: required bins (11): fence_i_valid, fence_i_withheld, redirect_valid, redirect_withheld, bus_err_beat_valid, bus_err_beat_withheld, ecc_inject_valid, ecc_inject_withheld, icache_disable_valid, icache_disable_withheld, key_req_valid; ignore key_req_withheld: the icache does not re-request a key while a request is already pending (a fence.i in AWAIT_SCRAMBLE_KEY is ignored, F-IC-024; the F-IC-025 re-request happens during the invalidation walk with the key valid)
  - cr_event_x_inval = cp_event x cp_inval: required bins (12): fence_i_none, fence_i_invalidating, redirect_none, redirect_invalidating, bus_err_beat_none, bus_err_beat_invalidating, ecc_inject_none, ecc_inject_invalidating, icache_disable_none, icache_disable_invalidating, key_req_none, key_req_invalidating
  - cr_redirect_x_stale_err = cp_stale_fill_outcome x cp_fill_state: required bins (6): completed_ok_one_beat_outst, completed_ok_two_to_line, completed_ok_multi_line, completed_err_one_beat_outst, completed_err_two_to_line, completed_err_multi_line
- Adopted (riscv-dv): none
- TP items: TP-XIF-006, TP-XIF-007, TP-XIF-018, TP-XIF-022

### CG-XIF-006: gen_cg_xif_zcmp_inflight
- Features: F-CMP-056, F-CMP-057, F-CMP-058, F-CMP-059, F-CMP-060, F-CMP-061, F-CMP-063, F-IRQ-020, F-DBG-010, F-DBG-046, F-DMEM-046, F-DMEM-047, F-EXC-043, F-EXC-044, F-FE-024, F-RVFI-022, F-RVFI-023, F-TRG-023
- Sample: an asynchronous edge (irq_pending_o / irq_nm_i / debug_req_i rising), a data bus error response, or a PMP data fault record while S14 zcmp_inflight; condition: zcmp_inflight && event; anti-vacuity: Zcmp sequences exist only when the program emits cm.* (compressed_heavy / mixed) and the events are driver injections; a hit proves the event landed inside a multi-micro-op sequence.
- Coverpoints:
  - cp_zcmp_kind = S14 zcmp_kind [F: F-DMEM-046, F-RVFI-022, F-FE-024]: bins push{cm.push}, pop{cm.pop}, popret{cm.popret}, popretz{cm.popretz}, mvsa01{cm.mvsa01}, mva01s{cm.mva01s}
  - cp_phase = micro-op position when the event arrived [F: F-CMP-056, F-CMP-057, F-CMP-058, F-IRQ-020]: bins first{first micro-op record pending}, middle{neither first nor last}, last{rvfi_ext_expanded_insn_last micro-op pending}
  - cp_event = event [F: F-IRQ-020, F-CMP-056, F-CMP-057, F-CMP-059, F-DBG-010, F-DBG-046, F-TRG-023, F-DMEM-047, F-CMP-060, F-CMP-061, F-EXC-043, F-EXC-044]: bins irq_maskable{irq_pending_o 0->1 while S14}, nmi{irq_nm_i 0->1 while S14}, debug_req{debug_req_i 0->1 while S14}, step{the sequence's first micro-op record is the first record after a dret record whose dcsr.step read back 1 (CSR model from the debug ROM's retired dcsr writes): the sequence was entered by a single-step resume and is stepped as one instruction, F-DBG-046; sampled at that first micro-op record while S14 is set (zcmp_inflight is 0 at the dret itself, so the event is anchored on the micro-op, and cp_phase = first by construction)}, bus_err_store{S6 on a pushed store}, bus_err_load{S6 on a popped load}, pmp_fault{rvfi_trap load/store access fault with no bus request for that word}
  - cp_outcome = how the sequence ended [F: F-IRQ-020, F-CMP-063, F-RVFI-023, F-DBG-010, F-DBG-046]: bins completed_then_event{all micro-ops retired, then handler/debug entry}, interrupted_reexecuted{trap taken mid-sequence with mepc = cm.* pc, the data requests repeat after mret, F-IRQ-020}, trap_mid_sequence{rvfi_trap on a micro-op, F-RVFI-023}
- Crosses:
  - cr_kind_x_event = cp_zcmp_kind x cp_event: required bins (32): push_irq_maskable, push_nmi, push_debug_req, push_step, push_bus_err_store, push_pmp_fault, pop_irq_maskable, pop_nmi, pop_debug_req, pop_step, pop_bus_err_load, pop_pmp_fault, popret_irq_maskable, popret_nmi, popret_debug_req, popret_step, popret_bus_err_load, popret_pmp_fault, popretz_irq_maskable, popretz_nmi, popretz_debug_req, popretz_step, popretz_bus_err_load, popretz_pmp_fault, mvsa01_irq_maskable, mvsa01_nmi, mvsa01_debug_req, mvsa01_step, mva01s_irq_maskable, mva01s_nmi, mva01s_debug_req, mva01s_step; ignore pop_bus_err_store, popret_bus_err_store, popretz_bus_err_store, mvsa01_bus_err_store, mva01s_bus_err_store, push_bus_err_load, mvsa01_bus_err_load, mva01s_bus_err_load, mvsa01_pmp_fault, mva01s_pmp_fault: cm.pop/popret/popretz issue only loads, cm.push only stores, cm.mvsa01/mva01s issue no memory access
  - cr_event_x_outcome = cp_event x cp_outcome: required bins (9): irq_maskable_completed_then_event, irq_maskable_interrupted_reexecuted, nmi_completed_then_event, nmi_interrupted_reexecuted, debug_req_completed_then_event, step_completed_then_event, bus_err_store_trap_mid_sequence, bus_err_load_trap_mid_sequence, pmp_fault_trap_mid_sequence; ignore bus_err_store_completed_then_event, bus_err_store_interrupted_reexecuted, bus_err_load_completed_then_event, bus_err_load_interrupted_reexecuted, pmp_fault_completed_then_event, pmp_fault_interrupted_reexecuted, irq_maskable_trap_mid_sequence, nmi_trap_mid_sequence, debug_req_trap_mid_sequence, step_trap_mid_sequence, debug_req_interrupted_reexecuted, step_interrupted_reexecuted: a bus or PMP fault always traps on the micro-op (F-CMP-060/061); an interrupt or debug request never produces rvfi_trap on a micro-op; debug entry and single-step are blocked for the whole sequence (F-DBG-010/046) so they cannot interrupt it
  - cr_phase_x_irq = cp_phase x cp_event: required bins (6): first_irq_maskable, middle_irq_maskable, last_irq_maskable, first_nmi, middle_nmi, last_nmi; ignore all other 15 combinations: only interrupts can land mid-sequence (F-IRQ-020: taken during load/store micro-ops, blocked during COMMIT ops); debug waits for the sequence, step is `first` by construction, and faults are covered by cr_kind_x_event
- Adopted (riscv-dv): none
- TP items: TP-XIF-011, TP-XIF-012, TP-XIF-013

### CG-XIF-007: gen_cg_xif_flush_x_irq
- Features: F-CSR-006, F-CSR-007, F-CSR-008, F-CSR-026, F-CSR-031, F-CSR-033, F-IRQ-023, F-IRQ-024, F-IRQ-029, F-IRQ-038, F-IRQ-059, F-IRQ-060, F-PRV-008, F-PRV-012, F-DBG-056, F-DBG-058, F-EXC-061
- Sample: retirement record of a flushing CSR write (S16), a non-flushing CSR write, mret or dret (S17) with rvfi_trap = 0; the pins are read in the instruction's COMMIT cycle, back-dated from the record per S18 (rvfi_valid cycle - GEN_CSR_WRITE_TO_RVFI_OFFSET = 2 for CSR writes, - GEN_TRAP_TO_RVFI_OFFSET = 1 for mret/dret), which is the flush cycle; condition: such a retirement; anti-vacuity: these instructions retire only when the program executes them and the pins are read cycle-exactly, so a non-`none` bin proves the pipeline flush coincided with a pending asynchronous request.
- Coverpoints:
  - cp_flush_kind = retired instruction [F: F-CSR-006, F-CSR-007, F-CSR-033, F-EXC-061]: bins csr_irq{write to CSR_MIE / CSR_MSTATUS / CSR_MIP (ibex_pkg), flushing}, csr_other_flush{any other flushing CSR write}, csr_nonflush{CSR_MSCRATCH or CSR_MEPC write, F-CSR-007}, mret{S17 mret_retired}, dret{S17 dret_retired}
  - cp_irq_state = pins in the commit cycle (S18 back-dated) [F: F-IRQ-023, F-IRQ-024, F-IRQ-038, F-CSR-008, F-DBG-056, F-DBG-058]: bins none{none of irq_pending_o, irq_nm_i, debug_req_i}, irq_pending{irq_pending_o only}, nmi{irq_nm_i only}, debug_req{debug_req_i only}, multiple{>= 2}
  - cp_next = next record [F: F-IRQ-023, F-IRQ-024, F-IRQ-029, F-IRQ-038, F-PRV-008, F-PRV-012, F-CSR-026, F-DBG-056]: bins handler_irq{rvfi_intr = 1, !rvfi_ext_nmi}, handler_nmi{rvfi_intr = 1 with rvfi_ext_nmi or rvfi_ext_nmi_int}, debug_entry{rvfi_ext_debug_mode rises}, sequential{rvfi_pc_rdata == the expected next pc: this record's rvfi_pc_wdata for a CSR write (a non-redirecting record); the mret/dret TARGET (mepc & ~1 / dpc from the CSR model at the commit) for mret/dret, whose own rvfi_pc_wdata is only the next sequential fetch address (C-1, X-1)}
  - cp_enable_effect = irq_pending_o edge in the two cycles BEFORE the record, iff cp_flush_kind == csr_irq: cycle (record - 2) is the commit and (record - 1) the first cycle the new mie value is visible on the pin, so the edge precedes the record (S18; mie writes only: irq_pending_o ignores mstatus.MIE (S7) and mip writes are ignored (D1)) [F: F-IRQ-059, F-IRQ-060, F-CSR-031, F-CSR-026]: bins enables_pending{0 -> 1, F-IRQ-059}, disables_pending{1 -> 0, F-IRQ-060}, neutral{no edge in those two cycles}
  - cp_mode_to = landing privilege of the mret/dret: mstatus.MPP (mret) / dcsr.prv (dret) from the CSR model at the commit, legalised as the RTL does (rtl/ibex_cs_registers.sv:784-786, :814-815); NOT rvfi_mode of the next record, which reads M whenever that record is a handler entry; iff cp_flush_kind in {mret, dret} [F: F-IRQ-029, F-PRV-008, F-PRV-012, F-DBG-056]: bins m{PRIV_LVL_M}, u{PRIV_LVL_U}
  - cp_landing_enable = whether an ordinary interrupt is enabled in the landing context, iff cp_flush_kind in {mret, dret} (X-9 / X-15: irq_enabled = MIE | (priv == U), rtl/ibex_controller.sv:490; mret restores MIE <- MPIE, rtl/ibex_cs_registers.sv:953-956; dret leaves MIE unchanged, :949-950) [F: F-IRQ-023, F-IRQ-029, F-PRV-008, F-PRV-012, F-DBG-056]: bins enabled{landing mode U, or landing mode M with the landing MIE = 1 (mret: MPIE = 1; dret: mstatus.MIE = 1)}, disabled{landing mode M with the landing MIE = 0 (mret: MPIE = 0; dret: mstatus.MIE = 0)}
  - cp_irq_outcome = fate of the pending ordinary interrupt, iff cp_flush_kind in {mret, dret} && cp_irq_state == irq_pending && cp_next in {handler_irq, sequential} [F: F-IRQ-023, F-IRQ-029, F-PRV-008, F-PRV-012]: bins taken{cp_next == handler_irq: taken in the first empty-ID DECODE after the FLUSH, mepc read back == the mret/dret target}, deferred{cp_next == sequential with irq_pending_o still 1 at that record's WB exit}
- Crosses:
  - cr_kind_x_irq = cp_flush_kind x cp_irq_state: required bins (25): csr_irq_none, csr_irq_irq_pending, csr_irq_nmi, csr_irq_debug_req, csr_irq_multiple, csr_other_flush_none, csr_other_flush_irq_pending, csr_other_flush_nmi, csr_other_flush_debug_req, csr_other_flush_multiple, csr_nonflush_none, csr_nonflush_irq_pending, csr_nonflush_nmi, csr_nonflush_debug_req, csr_nonflush_multiple, mret_none, mret_irq_pending, mret_nmi, mret_debug_req, mret_multiple, dret_none, dret_irq_pending, dret_nmi, dret_debug_req, dret_multiple
  - cr_effect_x_next = cp_enable_effect x cp_next: required bins (11): enables_pending_handler_irq, enables_pending_handler_nmi, enables_pending_debug_entry, enables_pending_sequential, disables_pending_handler_nmi, disables_pending_debug_entry, disables_pending_sequential, neutral_handler_irq, neutral_handler_nmi, neutral_debug_entry, neutral_sequential; ignore disables_pending_handler_irq: when irq_pending_o falls to 0 no maskable interrupt remains to be taken
  - cr_mode_to_x_irq = cp_mode_to x cp_irq_state: required bins (10): m_none, m_irq_pending, m_nmi, m_debug_req, m_multiple, u_none, u_irq_pending, u_nmi, u_debug_req, u_multiple
  - cr_landing_x_outcome = cp_landing_enable x cp_irq_outcome: required bins (2): enabled_taken, disabled_deferred; ignore enabled_deferred: an enabled pending interrupt is taken before any instruction at the target (empty ID after the FLUSH, rtl/ibex_controller.sv:704-720); ignore disabled_taken: landing in M with MIE = 0 masks ordinary interrupts (X-9 / X-15; the former reading "sequential when MPIE = 0" was wrong in both directions: an mret to U with MPIE = 0 takes the handler, a dret to M with MIE = 0 does not)
- Adopted (riscv-dv): none
- TP items: TP-XIF-014, TP-XIF-015

### CG-XIF-008: gen_cg_xif_fetch_enable_off
- Features: F-IMEM-022, F-IMEM-023, F-IMEM-024, F-IMEM-025, F-RST-010, F-RST-011, F-RST-012, F-RST-013, F-RST-014, F-RST-015, F-IRQ-056, F-SEC-012, F-DIT-028
- Sample: fetch_enable_i leaving IbexMuBiOn (S10 falling); one sample per true in-flight flag (`none` only when no flag is true); condition: the Off transition; anti-vacuity: only fetch_enable_regime = toggling produces Off transitions; a hit proves the Off edge coincided with the in-flight state and that the Off window had the recorded content; the window-content coverpoints (cp_off_duration, cp_during_off, cp_retire_after) are filled when the window closes and the first post-window record retires. C-4 (X-5): the Off edge stops only new icache lookups (rtl/ibex_core.sv:648 gates req_i, consumed only by lookup_req_ic0, rtl/ibex_icache.sv:249); the remaining beats of fill buffers allocated before the edge keep requesting (fill_ext_req :756 has no req_i term; a request awaiting grant is held, :764), so instr_req_o inside the window is legal for a line open at the edge and cp_during_off.fetch_req_open_line records it; a request for a NEW line, or any instr_req_o while core_busy_o == Off, is a gen_chk_fetch_en failure, not a bin.
- Coverpoints:
  - cp_off_encoding = value driven [F: F-IMEM-023, F-RST-014, F-SEC-012]: bins mubi_off{IbexMuBiOff}, invalid_encoding{any other non-On $bits(ibex_mubi_t) value, F-IMEM-023}
  - cp_inflight = DUT state at the Off edge [F: F-IMEM-024, F-RST-010, F-RST-011, F-RST-015, F-DIT-028]: bins none{no flag true}, fetch_outst{S1 >= 1}, data_outst{S4 >= 1, F-RST-011}, split_inflight{S5}, irq_pending{irq_pending_o}, nmi{irq_nm_i}, debug_req{debug_req_i}, sleeping{S9}, in_debug{dbg_mode_q}, zcmp_inflight{S14}
  - cp_off_duration = length of the Off window [F: F-RST-014, F-IMEM-022]: bins one_cycle{1}, short{2..15}, long{16..200}
  - cp_during_off = events inside the Off window [F: F-RST-015, F-IRQ-056, F-IMEM-024, F-IMEM-022]: bins nothing{none of the four below}, async_rises{irq_pending_o, irq_nm_i or debug_req_i rises, F-RST-015/F-IRQ-056}, data_rsp_returns{data_rvalid_i, F-IMEM-024}, fetch_rsp_returns{instr_rvalid_i}, fetch_req_open_line{instr_req_o asserted inside the window for a remaining beat of a line open at the Off edge (address inside an IC_LINE_SIZE-aligned block that had a granted-but-unanswered beat or an asserted request at the edge, beat index increasing), F-IMEM-024 / X-5}
  - cp_retire_after = first record after re-enable [F: F-IMEM-025, F-RST-012, F-RST-013, F-IRQ-056]: bins resumed_sequential{rvfi_pc_rdata == the held PC = the pc of the first not-yet-executed instruction derived from the last pre-Off record (its rvfi_pc_wdata for a non-redirecting or branch/jump record; the vector / mepc / dpc target for a trap / mret / dret record, C-1), F-IMEM-025 (or the boot vector when the Off window spans a reset release, F-RST-013)}, handler{rvfi_intr = 1}, debug{rvfi_ext_debug_mode rises}
- Crosses:
  - cr_enc_x_inflight = cp_off_encoding x cp_inflight: required bins (20): mubi_off_none, mubi_off_fetch_outst, mubi_off_data_outst, mubi_off_split_inflight, mubi_off_irq_pending, mubi_off_nmi, mubi_off_debug_req, mubi_off_sleeping, mubi_off_in_debug, mubi_off_zcmp_inflight, invalid_encoding_none, invalid_encoding_fetch_outst, invalid_encoding_data_outst, invalid_encoding_split_inflight, invalid_encoding_irq_pending, invalid_encoding_nmi, invalid_encoding_debug_req, invalid_encoding_sleeping, invalid_encoding_in_debug, invalid_encoding_zcmp_inflight
  - cr_dur_x_during = cp_off_duration x cp_during_off: required bins (15): one_cycle_nothing, one_cycle_async_rises, one_cycle_data_rsp_returns, one_cycle_fetch_rsp_returns, one_cycle_fetch_req_open_line, short_nothing, short_async_rises, short_data_rsp_returns, short_fetch_rsp_returns, short_fetch_req_open_line, long_nothing, long_async_rises, long_data_rsp_returns, long_fetch_rsp_returns, long_fetch_req_open_line
  - cr_during_x_after = cp_during_off x cp_retire_after: required bins (15): nothing_resumed_sequential, nothing_handler, nothing_debug, async_rises_resumed_sequential, async_rises_handler, async_rises_debug, data_rsp_returns_resumed_sequential, data_rsp_returns_handler, data_rsp_returns_debug, fetch_rsp_returns_resumed_sequential, fetch_rsp_returns_handler, fetch_rsp_returns_debug, fetch_req_open_line_resumed_sequential, fetch_req_open_line_handler, fetch_req_open_line_debug
- Adopted (riscv-dv): none
- TP items: TP-XIF-016

### CG-XIF-009: gen_cg_xif_pmp_reconfig
- Features: F-PMP-055, F-PMP-065, F-PMP-066, F-PMP-079, F-PMP-086, F-PMP-087, F-PMP-088, F-PMP-092, F-PMP-093, F-PMP-100, F-CSR-006, F-CSR-008, F-IC-039, F-PRV-013
- Sample: retirement of a PMP CSR write (S16 pmp_csr) with rvfi_trap = 0; condition: such a retirement; anti-vacuity: mid-run PMP writes happen only in pmp_regime != off regions (and at region boundaries); a hit proves a reconfiguration retired with the recorded in-flight and verdict state.
- Coverpoints:
  - cp_csr = written register [F: F-PMP-092, F-PMP-100, F-CSR-006]: bins pmpcfg{CSR_PMPCFG0..3}, pmpaddr{CSR_PMPADDR0..PMPNumRegions-1}, mseccfg{CSR_MSECCFG}
  - cp_fetch = S1 in the write's commit cycle (S18) [F: F-PMP-066, F-PMP-079, F-PMP-092, F-PMP-093]: bins fetch_idle{0}, fetch_outst{>= 1: prefetched words that must be re-checked at IF/ID, F-PMP-092}
  - cp_prev_ls_outst = the CSR write entered ID while the previous record's load/store access was still outstanding in WB, S21 (the CSR write's record follows the load/store record by exactly one cycle; a response "after the predecessor's retirement" is impossible because the record is one cycle after the final rvalid, fact-check TP-XIF-010) [F: F-PMP-086, F-PMP-087, F-PMP-088, F-CSR-008]: bins no{previous record not a load/store, or its response returned before the CSR write entered ID (record spacing > 1 cycle)}, single{S21 with a non-split access}, split{S21 with a misaligned pair: the second half was outstanding when the CSR write entered ID, F-PMP-086..088}
  - cp_verdict_change = effect on the following instructions [F: F-PMP-055, F-PMP-065, F-PMP-066, F-PMP-092, F-PRV-013]: bins next_fetch_now_denied{next record is rvfi_trap with instruction access fault at pc == this record's pc_wdata}, next_data_now_denied{next load/store record faults with no dbus request for that word}, no_change{next records proceed}
  - cp_lock = pmpcfg write setting an L bit [F: F-PMP-100]: bins sets_lock{>= 1 L bit 0 -> 1}, no_lock{no L bit set}
  - cp_icache = S12 icache_en_q [F: F-PMP-093, F-IC-039]: bins enabled{1}, disabled{0}
- Crosses:
  - cr_csr_x_fetch_x_verdict = cp_csr x cp_fetch x cp_verdict_change: required bins (18): pmpcfg_fetch_idle_next_fetch_now_denied, pmpcfg_fetch_idle_next_data_now_denied, pmpcfg_fetch_idle_no_change, pmpcfg_fetch_outst_next_fetch_now_denied, pmpcfg_fetch_outst_next_data_now_denied, pmpcfg_fetch_outst_no_change, pmpaddr_fetch_idle_next_fetch_now_denied, pmpaddr_fetch_idle_next_data_now_denied, pmpaddr_fetch_idle_no_change, pmpaddr_fetch_outst_next_fetch_now_denied, pmpaddr_fetch_outst_next_data_now_denied, pmpaddr_fetch_outst_no_change, mseccfg_fetch_idle_next_fetch_now_denied, mseccfg_fetch_idle_next_data_now_denied, mseccfg_fetch_idle_no_change, mseccfg_fetch_outst_next_fetch_now_denied, mseccfg_fetch_outst_next_data_now_denied, mseccfg_fetch_outst_no_change
  - cr_prev_ls_x_csr = cp_prev_ls_outst x cp_csr: required bins (9): no_pmpcfg, no_pmpaddr, no_mseccfg, single_pmpcfg, single_pmpaddr, single_mseccfg, split_pmpcfg, split_pmpaddr, split_mseccfg
  - cr_icache_x_verdict = cp_icache x cp_verdict_change: required bins (6): enabled_next_fetch_now_denied, enabled_next_data_now_denied, enabled_no_change, disabled_next_fetch_now_denied, disabled_next_data_now_denied, disabled_no_change
  - cr_lock_x_verdict = cp_lock x cp_verdict_change: required bins (6): sets_lock_next_fetch_now_denied, sets_lock_next_data_now_denied, sets_lock_no_change, no_lock_next_fetch_now_denied, no_lock_next_data_now_denied, no_lock_no_change
- Adopted (riscv-dv): none
- TP items: TP-XIF-010, TP-XIF-019

### CG-XIF-010: gen_cg_xif_reset_inflight
- Features: F-RST-001, F-RST-008, F-RST-009, F-RST-018, F-RST-019, F-RST-024, F-RST-026, F-SEC-035, F-IC-009, F-IC-022, F-DBG-008, F-IRQ-055, F-RVFI-033
- Sample: rst_ni falling edge after at least one retirement since the previous reset (mid-run reset; the time-0 reset is excluded); one sample per true in-flight flag; condition: mid-run reset; anti-vacuity: mid-run resets are issued only by the reset test group at randomized instants; a hit proves the reset interrupted that state and that the post-release observation followed.
- Coverpoints:
  - cp_inflight = state at the reset edge [F: F-RST-001, F-RST-018, F-RST-019, F-IC-022, F-DBG-008, F-IRQ-055]: bins idle{no flag true}, fetch_outst{S1 >= 1}, data_outst{S4 >= 1}, split_inflight{S5}, zcmp_inflight{S14}, sleeping{S9}, in_debug{dbg_mode_q}, irq_pending{irq_pending_o}, nmi{irq_nm_i}, debug_req{debug_req_i}, fill_inflight{S12}, key_withheld{S13}, invalidating{S12 invalidating}, fetch_en_off{!S10}
  - cp_after = observation after release [F: F-RST-008, F-RST-009, F-RST-018, F-RST-024, F-RST-026, F-SEC-035, F-IC-009, F-RVFI-033]: bins first_fetch_boot_vector{instr_addr_o == {boot_addr_i[31:8], 8'h80} within 2 cycles of release, F-RST-002/008}, stale_rsp_after_release{the memory model still owed a response for a pre-reset request at release and DROPPED it (model-side event logged by the model; the DUT never sees it: S3 / Q-010, the LSU and the icache have no outstanding-request qualifier, rtl/ibex_load_store_unit.sv:694-697, so a delivered stale rvalid would be consumed as a response), F-RST-018}, async_pending_at_release{debug_req_i or irq_nm_i high at release, taken in FIRST_FETCH, F-RST-024}
  - cp_reset_len = cycles rst_ni held low [F: F-RST-001, F-SEC-035]: bins short{1..2}, long{3..64}
- Crosses:
  - cr_inflight_x_after = cp_inflight x cp_after: required bins (39): idle_first_fetch_boot_vector, idle_async_pending_at_release, fetch_outst_first_fetch_boot_vector, fetch_outst_stale_rsp_after_release, fetch_outst_async_pending_at_release, data_outst_first_fetch_boot_vector, data_outst_stale_rsp_after_release, data_outst_async_pending_at_release, split_inflight_first_fetch_boot_vector, split_inflight_stale_rsp_after_release, split_inflight_async_pending_at_release, zcmp_inflight_first_fetch_boot_vector, zcmp_inflight_stale_rsp_after_release, zcmp_inflight_async_pending_at_release, sleeping_first_fetch_boot_vector, sleeping_async_pending_at_release, in_debug_first_fetch_boot_vector, in_debug_stale_rsp_after_release, in_debug_async_pending_at_release, irq_pending_first_fetch_boot_vector, irq_pending_stale_rsp_after_release, irq_pending_async_pending_at_release, nmi_first_fetch_boot_vector, nmi_stale_rsp_after_release, nmi_async_pending_at_release, debug_req_first_fetch_boot_vector, debug_req_stale_rsp_after_release, debug_req_async_pending_at_release, fill_inflight_first_fetch_boot_vector, fill_inflight_stale_rsp_after_release, fill_inflight_async_pending_at_release, key_withheld_first_fetch_boot_vector, key_withheld_stale_rsp_after_release, key_withheld_async_pending_at_release, invalidating_first_fetch_boot_vector, invalidating_stale_rsp_after_release, invalidating_async_pending_at_release, fetch_en_off_stale_rsp_after_release, fetch_en_off_async_pending_at_release; ignore idle_stale_rsp_after_release, sleeping_stale_rsp_after_release, fetch_en_off_first_fetch_boot_vector: with no transaction outstanding (idle, or asleep which requires no outstanding access) no pre-reset response can be owed; with fetch_enable_i not On at release the boot fetch is gated (F-RST-013) so it cannot appear within the 2-cycle window
- Adopted (riscv-dv): none
- TP items: TP-XIF-017

### CG-XIF-011: gen_cg_xif_mode_x_event
- Features: F-PRV-001, F-PRV-013, F-PRV-023, F-PRV-024, F-PRV-031, F-PRV-033, F-IRQ-008, F-IRQ-029, F-IRQ-039, F-IRQ-053, F-DBG-019, F-DBG-020, F-DBG-023, F-DBG-026, F-DBG-027, F-DBG-029, F-DBG-030, F-DBG-056, F-DBG-057, F-DBG-059, F-DBG-064, F-PMP-051, F-PMP-052, F-PMP-053, F-PMP-072, F-PMP-097, F-EXC-024, F-EXC-025, F-EXC-027, F-IC-039, F-IC-040, F-FE-022, F-RVFI-027, F-CSR-014, F-TRG-012, F-TRG-013, F-DIT-010
- Sample: an interface event record: rvfi_trap record (cause class from the ISA model's expected cause and the dbus/ibus monitors: bus error vs PMP by presence/absence of the bus transaction), rvfi_intr record, debug entry (first record with rvfi_ext_debug_mode = 1 after a non-debug record, cause class from dcsr.cause read back by the debug ROM), WFI wake (CG-XIF-004 event), each attributed to cp_mode by S11; condition: event; anti-vacuity: mode is program-driven (priv_regime) and U-mode/debug events exist only when the program enters those modes; a hit proves the interface event happened in that mode.
- Coverpoints:
  - cp_mode = mode of the instruction or interrupted context (S11) [F: F-PRV-001, F-PRV-033, F-RVFI-027, F-DBG-064, F-IC-039, F-IC-040, F-FE-022, F-DIT-010]: bins m{rvfi_mode 2'b11}, u{2'b00}, debug{dbg_mode_q}
  - cp_event = event class [F: F-EXC-025, F-EXC-027, F-DBG-027, F-PMP-051, F-PMP-052, F-PMP-053, F-PMP-097, F-DBG-030, F-CSR-014, F-EXC-024, F-DBG-029, F-DBG-019, F-DBG-020, F-DBG-023, F-DBG-026, F-IRQ-008, F-IRQ-029, F-IRQ-039, F-IRQ-053, F-PRV-023, F-PRV-024, F-PRV-031, F-DBG-056, F-DBG-057, F-DBG-059, F-TRG-012, F-TRG-013]: bins load_err_bus{rvfi_trap load access fault with a data_err_i response for the word}, store_err_bus{likewise for a store}, load_fault_pmp{rvfi_trap load access fault with no data_req_o for the word}, store_fault_pmp{likewise for a store}, fetch_err_bus{rvfi_trap instruction access fault with an instr_err_i beat for pc}, fetch_fault_pmp{likewise with no errored beat}, illegal{rvfi_trap with ISA-model cause 2}, ecall{cause 8 or 11}, ebreak_trap{is_ebreak(rvfi_insn) && rvfi_trap = 1}, ebreak_debug{is_ebreak(rvfi_insn) && !rvfi_trap && next fetch == DmHaltAddr (S-2 rule, rtl/ibex_core.sv:1885-1886)}, irq_taken{rvfi_intr = 1, !rvfi_ext_nmi}, nmi_taken{rvfi_intr = 1 with rvfi_ext_nmi or rvfi_ext_nmi_int}, debug_req_entry{first debug record, dcsr.cause = 3}, trigger_entry{dcsr.cause = 2}, step_entry{dcsr.cause = 4}, wfi_wake{CG-XIF-004 wake instant}, csr_illegal_priv{CSR access denied by csr[9:8] > mode, F-CSR-014}
  - cp_mprv = mstatus.MPRV/MPP of a data-fault event (tracked from retired mstatus writes / ISA model), iff cp_event in {load_fault_pmp, store_fault_pmp} [F: F-PRV-013, F-PMP-072, F-PMP-097]: bins mprv0{MPRV = 0}, mprv1_mpp_u{MPRV = 1, MPP = U, F-PRV-013/F-PMP-072}
- Crosses:
  - cr_mode_x_event = cp_mode x cp_event: required bins (44): m_load_err_bus, m_store_err_bus, m_load_fault_pmp, m_store_fault_pmp, m_fetch_err_bus, m_fetch_fault_pmp, m_illegal, m_ecall, m_ebreak_trap, m_ebreak_debug, m_irq_taken, m_nmi_taken, m_debug_req_entry, m_trigger_entry, m_step_entry, m_wfi_wake, m_csr_illegal_priv, u_load_err_bus, u_store_err_bus, u_load_fault_pmp, u_store_fault_pmp, u_fetch_err_bus, u_fetch_fault_pmp, u_illegal, u_ecall, u_ebreak_trap, u_ebreak_debug, u_irq_taken, u_nmi_taken, u_debug_req_entry, u_trigger_entry, u_step_entry, u_wfi_wake, u_csr_illegal_priv, debug_load_err_bus, debug_store_err_bus, debug_load_fault_pmp, debug_store_fault_pmp, debug_fetch_err_bus, debug_fetch_fault_pmp, debug_illegal, debug_ecall, debug_ebreak_debug, debug_wfi_wake; ignore debug_irq_taken, debug_nmi_taken, debug_debug_req_entry, debug_trigger_entry, debug_step_entry, debug_ebreak_trap, debug_csr_illegal_priv: all interrupts incl. NMI are ignored in debug mode (F-DBG-056/057); debug_req_i is ignored while already in debug (F-DBG-007); triggers do not fire in debug mode (F-TRG-013); a step re-entry is attributed to the stepped instruction's non-debug mode; ebreak in debug mode re-enters debug and never traps (F-DBG-023); debug mode runs at M privilege so no CSR privilege check can fail (F-DBG-064)
  - cr_mprv_x_datafault = cp_mprv x cp_event: required bins (4): mprv0_load_fault_pmp, mprv0_store_fault_pmp, mprv1_mpp_u_load_fault_pmp, mprv1_mpp_u_store_fault_pmp; ignore all other 30 combinations: MPRV changes only the privilege used for PMP data checks (F-PRV-013), so it is meaningful only for PMP data faults
- Adopted (riscv-dv): none
- TP items: TP-XIF-020

### CG-XIF-012: gen_cg_xif_dummy_x_event
- Features: F-DIT-011, F-DIT-012, F-DIT-013, F-DIT-019, F-DIT-020, F-DIT-021, F-DIT-023, F-DIT-028, F-DIT-029, F-FE-018, F-PMP-094, F-TRG-026
- Sample: S20 dummy_inserted (probe P1: dummy_instr_id rising on the core-to-register-file seam, dummy type from fcov_dummy_instr_type; P1 is accepted coverage-only in dv/auto_dv/docs/gen_probe_register.md); condition: cpuctrlsts.dummy_instr_en = 1 (program-set) and the LFSR fires; anti-vacuity: dummies are architecturally invisible (no RVFI record, no bus traffic), so only the probe can sample them; a hit proves a dummy was in ID while the crossed boundary state held. Coverage-only; no checker depends on this group. PROBE-GATED (P1), NOT IN MANIFEST: no test lists these bins as must-hit until the probe register carries P1 (gen_tb_architecture.md 8.3 item 5).
- Coverpoints:
  - cp_event = boundary state in the insertion cycle [F: F-DIT-021, F-DIT-019, F-DIT-020, F-DIT-029, F-PMP-094, F-TRG-026, F-FE-018]: bins none{no flag true}, redirect{the S19 redirect cycle (rvfi_valid - GEN_RVFI_ID_EXIT_OFFSET for a branch/jump, - GEN_TRAP_TO_RVFI_OFFSET for a trap/mret/dret) equals the insertion cycle, F-DIT-021}, irq_pending{irq_pending_o, F-DIT-019}, nmi{irq_nm_i}, debug_req{debug_req_i, F-DIT-020}, data_outst_load{S4 >= 1 for a load, F-DIT-029}
  - cp_dummy_type = fcov_dummy_instr_type [F: F-DIT-011, F-DIT-013]: bins add{DUMMY_ADD}, mul{DUMMY_MUL}, div{DUMMY_DIV}, and_{DUMMY_AND}
  - cp_mask = cpuctrlsts.dummy_instr_mask tracked from retired CSR writes (F-DIT-012) [F: F-DIT-012, F-DIT-023, F-DIT-028]: bins m000{3'b000}, m001{3'b001}, m010{3'b010}, m011{3'b011}, m100{3'b100}, m101{3'b101}, m110{3'b110}, m111{3'b111}
  - cp_mode = S11 mode_q [F: F-DIT-011, F-FE-018]: bins m{2'b11}, u{2'b00}
- Crosses:
  - cr_event_x_type = cp_event x cp_dummy_type: required bins (24): none_add, none_mul, none_div, none_and_, redirect_add, redirect_mul, redirect_div, redirect_and_, irq_pending_add, irq_pending_mul, irq_pending_div, irq_pending_and_, nmi_add, nmi_mul, nmi_div, nmi_and_, debug_req_add, debug_req_mul, debug_req_div, debug_req_and_, data_outst_load_add, data_outst_load_mul, data_outst_load_div, data_outst_load_and_
  - cr_type_x_mode = cp_dummy_type x cp_mode: required bins (8): add_m, add_u, mul_m, mul_u, div_m, div_u, and__m, and__u
- Probe status: pending probe-register ruling (candidate P9: fcov_dummy_instr_type, sampled with P1 dummy_instr_id); coverpoints cp_dummy_type, cr_event_x_type, cr_type_x_mode excluded from manifests until ruled
- Adopted (riscv-dv): none
- TP items: TP-XIF-021

### CG-ADOPT-001: gen_cg_adopt_gpr_hazard
- Features: F-BIT-039, F-MUL-025, F-DMEM-028, F-DMEM-029, F-CMP-068, F-BTALU-013
- Sample: every RVFI retirement with rvfi_trap = 0, compared with the previous retirement (riscv-dv check_hazard_condition against pre_instr); condition: rvfi_valid; anti-vacuity: the hazard class depends on the register operands of two consecutive retirements (rvfi_rs1_addr/rs2_addr/rd_addr and, for the LSU class, rvfi_mem_addr), so `no_hazard` is not always true and each hazard bin proves a specific back-to-back dependency retired.
- Coverpoints:
  - cp_gpr_hazard = register dependency on the previous retirement: bins no_hazard{no shared register}, raw{this reads the previous rd}, war{this writes a register the previous read}, waw{same rd, both non-x0}
  - cp_lsu_hazard = memory dependency on the previous retirement (both load/store, same rvfi_mem_addr): bins no_hazard{not both memory ops, or different rvfi_mem_addr}, raw{load after store, same address}, war{store after load, same address}, waw{store after store, same address}
- Crosses: none
- Adopted (riscv-dv): cp_gpr_hazard (instr.gpr_hazard: NO_HAZARD/RAW_HAZARD/WAR_HAZARD/WAW_HAZARD in the R_/I_/LOAD_/STORE_/CI_/CS_ INSTR_CG_BEGIN macros) and cp_lsu_hazard (instr.lsu_hazard in LOAD_/STORE_/CL_/CS_ INSTR_CG_BEGIN), riscv_instr_cover_group.sv. Adopted because our ISA features cover forwarding for specific classes (F-BIT-039, F-MUL-025, F-DMEM-028) but no feature enumerates all four hazard classes for arbitrary back-to-back pairs; riscv-dv's per-instruction hazard coverpoints are collapsed to one class-independent group.
- TP items: TP-ADOPT-001

### CG-ADOPT-002: gen_cg_adopt_branch_history
- Features: F-ISA-023, F-ISA-024, F-BTALU-001, F-BTALU-005, F-PMC-039, F-PMC-040
- Sample: retirement of a conditional branch (beq/bne/blt/bge/bltu/bgeu/c.beqz/c.bnez) once 5 branches have retired; taken = rvfi_pc_wdata != rvfi_pc_rdata + length; condition: branch retirement; anti-vacuity: the 5-bit history changes with every branch outcome, so a pattern bin proves that outcome sequence occurred back-to-back.
- Coverpoints:
  - cp_branch_history = last five branch outcomes, MSB oldest: bins all_taken{5'b11111}, all_not_taken{5'b00000}, alt_01010{5'b01010}, alt_10101{5'b10101}, other{any other value}
- Crosses: none
- Adopted (riscv-dv): branch_hit_history_cg.cp_branch_history (5-bit branch_hit_history), riscv_instr_cover_group.sv, reduced from 32 auto bins to 5 pattern classes. Adopted because F-ISA-024 covers taken vs not-taken per branch but nothing covers outcome sequences (the RTL has no predictor in this config, so the history stresses the redirect/flush pipeline back-to-back: F-BTALU-005, F-FE-013).
- TP items: TP-ADOPT-002

### CG-ADOPT-003: gen_cg_adopt_operand_classes
- Features: F-ISA-001, F-ISA-002, F-ISA-007, F-ISA-008, F-ISA-015, F-ISA-016, F-ISA-023, F-ISA-026, F-DMEM-015, F-DMEM-016
- Sample: retirement of add/sub (sign cross), retirement of xor/or/and/xori/ori/andi (logical similarity), retirement of a branch, jal, load or store (immediate sign); values from rvfi_rs1_rdata/rs2_rdata/rd_wdata and the decoded immediate of rvfi_insn; condition: instruction class match; anti-vacuity: operand signs and the immediate are data, randomized by the generator; a bin proves that operand class retired.
- Coverpoints:
  - cp_addsub_sign = {rs1 sign, rs2 sign, rd sign} of add/sub [F: F-ISA-001, F-ISA-002, F-ISA-007, F-ISA-008]: bins ppp{+,+,+}, ppn{+,+,- overflow}, pnp{+,-,+}, pnn{+,-,-}, npp{-,+,+}, npn{-,+,-}, nnp{-,-,+ overflow}, nnn{-,-,-}
  - cp_logical_similarity = relation of rs1 to the second operand for xor/or/and/xori/ori/andi [F: F-ISA-001, F-ISA-007]: bins identical{equal}, opposite{bitwise complement}, similar{differ in <= 4 bits}, different{otherwise}
  - cp_imm_sign = sign of the immediate by class [F: F-ISA-015, F-ISA-016, F-ISA-023, F-ISA-026, F-DMEM-015, F-DMEM-016]: bins branch_fwd{branch imm >= 0}, branch_bwd{branch imm < 0}, jal_fwd{jal imm >= 0}, jal_bwd{jal imm < 0}, load_imm_pos{load imm >= 0}, load_imm_neg{load imm < 0}, store_imm_pos{store imm >= 0}, store_imm_neg{store imm < 0}
- Crosses: none
- Adopted (riscv-dv): add_cg/sub_cg cp_sign_cross (cross cp_rs1_sign, cp_rs2_sign, cp_rd_sign); xor_cg/or_cg/and_cg/xori_cg/ori_cg/andi_cg cp_logical (instr.logical_similarity); cp_imm_sign in SB_/J_/LOAD_/STORE_INSTR_CG_BEGIN, riscv_instr_cover_group.sv. Adopted because the ISA features name boundary values (F-ISA-002/008/026) but not the sign-class partition of operands, the operand-similarity classes for logic ops, or forward/backward direction per class.
- TP items: TP-ADOPT-003

### CG-ADOPT-004: gen_cg_adopt_jalr_ras
- Features: F-ISA-018, F-ISA-020, F-ISA-022, F-BTALU-003, F-PMC-038
- Sample: retirement of jalr (and c.jr / c.jalr mapped to rs1/rd); condition: jalr class; anti-vacuity: rs1/rd are generator-randomized registers; a bin proves that link-register usage pattern retired.
- Coverpoints:
  - cp_ras = {rs1 class, rd class} with class in {ra = x1, t1 = x6 (alternate link), non_link = any other register}; bin name = <rs1 class>_<rd class>: bins ra_ra, ra_t1, ra_non_link, t1_ra, t1_t1, t1_non_link, non_link_ra, non_link_t1, non_link_non_link
- Crosses: none
- Adopted (riscv-dv): jalr_cg cp_ras (cross cp_rs1_link x cp_rd_link, riscv_instr_cover_group.sv) contributes exactly the 4 bins ra_ra, ra_t1, t1_ra, t1_t1: riscv-dv declares non_link as `default`, which SystemVerilog excludes from crosses, so its cross has 4 bins. The 5 bins involving non_link (ra_non_link, t1_non_link, non_link_ra, non_link_t1, non_link_non_link) EXTEND the partition and are spec-derived (F-ISA-018/020/022; adopted = 0 in the CSV). Adopted because F-ISA-018/020 cover jalr semantics and rs1 == rd, not the call/return register conventions that generate the return-address-stack-like patterns (no RAS in Ibex; the pattern still exercises jalr with rs1 == rd == ra, F-ISA-020).
- TP items: TP-ADOPT-004

### CG-ADOPT-005: gen_cg_adopt_compressed_regs
- Features: F-CMP-002, F-CMP-004, F-CMP-018, F-CMP-020, F-CMP-021, F-CMP-023, F-CMP-034, F-CMP-036
- Sample: retirement of a compressed instruction with a 3-bit register field (CIW/CL/CS/CA/CB formats: c.addi4spn, c.lw, c.sw, c.sub/xor/or/and, c.srli/srai/andi, c.beqz/bnez, Zcb forms); the register is decoded from rvfi_insn; condition: such a retirement; anti-vacuity: the register is generator-randomized over the eight x8..x15 values; a bin proves that register value was used in a 3-bit field.
- Coverpoints:
  - cp_c_reg_prime = 3-bit register field value: bins s0{x8}, s1{x9}, a0{x10}, a1{x11}, a2{x12}, a3{x13}, a4{x14}, a5{x15}
- Crosses: none
- Adopted (riscv-dv): bins gpr[] = {S0, S1, A0, A1, A2, A3, A4, A5} on cp_rd/cp_rs1/cp_rs2 of the CIW_/CL_/CS_/CA_/CB_INSTR_CG_BEGIN macros, riscv_instr_cover_group.sv, collapsed to one register-field coverpoint. Adopted because the CMP features cover each instruction's semantics but not that every value of the 3-bit register field was decoded (the compressed decoder's x8 offset, F-CMP-001).
- TP items: TP-ADOPT-005

### CG-ADOPT-006: gen_cg_adopt_bitcount_result
- Features: F-BIT-005, F-BIT-006
- Sample: retirement of clz/ctz/cpop; result from rvfi_rd_wdata; condition: instruction class; anti-vacuity: the result depends on the generator-randomized operand; a range bin proves an operand with that many leading/trailing zeros or set bits retired.
- Coverpoints:
  - cp_bitcount_result = rvfi_rd_wdata of clz/ctz/cpop: bins r1_7{1..7}, r8_15{8..15}, r16_23{16..23}, r24_31{24..31}; result 0 (former bin r0) is not declared here: F-BIT-006's boundary bin in the isa area owns it (cross-reference, Critic S-9), as it owns 32
- Crosses: none
- Adopted (riscv-dv): clz_cg/ctz_cg/cpop_cg CP_VALUE_RANGE(num_leading_zeros / num_trailing_zeros / num_set_bits, instr.rd_value, 0, XLEN-1), riscv_instr_cover_group.sv, reduced from 32 values to 4 ranges over 1..31. Adopted because F-BIT-006 covers the boundary values (0 and 32) only; the values 0 and 32 are deliberately not adopted: 32 is outside riscv-dv's range (XLEN-1) and both are F-BIT-006's boundary bins (isa area), which would otherwise be duplicated.
- TP items: TP-ADOPT-006

### CG-REG-009: gen_cg_reg_intg_knobs
- Features: F-IMEM-027, F-SEC-017, F-SEC-019, F-DMEM-041
- Sample: ibus / dbus agent phase-log record at the phase's first regime-relevant event (Phase log table: first corrupted response beat under rare/frequent, the 64th clean beat under none); condition: record.knob in {imem_intg_err_rate, dmem_intg_err_rate} && activity reached (MemECC = 1 build, Q-002); anti-vacuity: one sample per phase and knob, never per clock and never at the phase start; the record carries the rate the agent APPLIED (+gen_ibus_intg_err_rate / +gen_dbus_intg_err_rate in per mille, regime intg_err) and the sample instant proves >= 1 response was integrity-checked under it, so a value bin proves the DUT saw that injection regime and a `_tr` bin proves two consecutive phases with activity differed.
- Coverpoints:
  - cp_imem_intg_rate = rec.value of knob:imem_intg_err_rate [F: F-IMEM-027]: bins none{0 per mille}, rare{~2 per mille (~1/512 beats)}, frequent{~50 per mille (~1/20 beats); 1-bit / 2-bit patterns 50/50}
  - cp_imem_intg_rate_tr = knob:imem_intg_err_rate across consecutive phases: bins none_to_rare, none_to_frequent, rare_to_none, rare_to_frequent, frequent_to_none, frequent_to_rare
  - cp_dmem_intg_rate = rec.value of knob:dmem_intg_err_rate [F: F-DMEM-041, F-SEC-017, F-SEC-019]: bins none{0 per mille}, rare{~2 per mille (~1/512 responses)}, frequent{~50 per mille (~1/20 responses); loads and store responses alike}
  - cp_dmem_intg_rate_tr = knob:dmem_intg_err_rate across consecutive phases: bins none_to_rare, none_to_frequent, rare_to_none, rare_to_frequent, frequent_to_none, frequent_to_rare
- Crosses:
  - cr_intg_rates = cp_imem_intg_rate x cp_dmem_intg_rate: required bins (9): none_none, none_rare, none_frequent, rare_none, rare_rare, rare_frequent, frequent_none, frequent_rare, frequent_frequent
- Adopted (riscv-dv): none
- TP items: TP-REG-026

### CG-REG-010: gen_cg_reg_mcounteren_knob
- Features: F-PMC-025, F-SEC-020
- Sample: the first retired mcounteren write of the run (S16 csr_write_retired(CSR_MCOUNTEREN)), with the value driven on mcounteren_writable_i read in that instruction's commit cycle (S18); condition: such a retirement; anti-vacuity: one sample per run, taken at the instruction whose outcome the pin decides, so a bin proves the run both drove that class and exercised the gated write (a run that never writes mcounteren contributes no sample).
- Coverpoints:
  - cp_mcounteren_writable = knob:mcounteren_writable (run constant; class of the pin value) [F: F-SEC-020, F-PMC-025]: bins on{IbexMuBiOn}, off{IbexMuBiOff}, invalid{any other $bits(ibex_mubi_t) value; acts as Off, rtl/ibex_cs_registers.sv:845}
- Crosses: none
- Adopted (riscv-dv): none
- TP items: TP-REG-027

## Completeness measure (proposal)

Definition the plan uses (DV_prompt Section 4, functional-coverage condition 2):

1. Every feature F-<AREA>-<nnn> in gen_feature_list maps to >= 1 TP item (trace_feat_tp_*.csv,
   `feature,tp_item`) and, through those items, to >= 1 bin (trace_tp_bin_*.csv,
   `tp_item,covergroup,coverpoint,bin,adopted`). A feature with a TP item but no bin, or a bin
   but no TP item, is incomplete.
2. Every bin maps back to >= 1 feature through its covergroup's `Features:` field. A covergroup
   whose Features field cites no F-ID, or cites an F-ID absent from the feature list, fails the
   check. Bin references are `CG-<AREA>-<nnn>.<cp>.<bin>` (cross bins `CG-...cr_<name>.<bin>`);
   the SV covergroup name is the `gen_cg_<area>_<name>` in the CG header and the URG key is
   `<gen_cg_name>.<cp>.<bin>`.
3. Gate definition (Critic S-11a): the 80% gate is the URG functional-coverage group score, not a
   flat declared-bin ratio: per covergroup the fraction of its bins hit AFTER ignore_bins (cross
   bins counted per expanded bin; no `illegal_bins` anywhere), averaged over the covergroups with
   equal weights (URG default weight 1 per group), read from the merged report's functional summary
   (dashboard.txt / grpinfo.txt). Adopted bins (riscv-dv) are counted separately: the adopted total
   is the bin-level hit ratio over the `adopted = 1` CSV rows (read per bin from grpinfo.txt, so a
   mixed group such as CG-ADOPT-004, whose five non_link cp_ras bins are spec-derived, splits
   correctly), reported beside the spec-derived group score; the spec-derived score excludes the
   CG-ADOPT-* groups. TEAM POLICY (stricter than DV_prompt Section 4, recorded by the DV Lead): the
   functional-coverage condition passes only if BOTH totals reach 80%. An adopted bin still needs a
   real F-ID (rule 2); the `Adopted (riscv-dv):` field names the source covergroup.
4. Per-test fcov-expectation manifest rule (dv_principles.md s6 rule 3; ci/check_fcov_expectations.py):
   every test declares in dv/auto_dv/fcov_expectations/<test>.fcov.yaml the bins it intends to
   hit; a declared bin unhit in that test's own coverage (urg -tests isolation) fails the run
   (exit 2), and an unparseable or missing manifest also fails (exit 1). The TP item's `Bins:`
   field is the set the item is responsible for closing across the regression; a test's manifest
   is the per-run reliable subset and must contain >= 1 bin from every UNCONDITIONAL coverpoint of
   every CG its items own (so a test cannot claim an item while sampling none of its group), with
   two exclusions (Critic S-11d): (a) probe-gated coverpoints (CG-XIF-012, marked "probe-gated
   (P1), not in manifest" in TP-XIF-021) are excluded until the probe register carries P1; (b)
   conditional coverpoints, i.e. those carrying an `iff` guard or defined for a subset of the
   group's events (CG-XIF-005.cp_stale_fill_outcome, CG-XIF-007.cp_enable_effect / cp_mode_to,
   CG-XIF-011.cp_mprv, CG-REG-005 ECC coverpoints, CG-REG-007 side-guarded coverpoints), enter a
   manifest only when the item's fire-check asserts the guard event in that test.
5. Regime layers are part of completeness: every knob value and every legal knob transition bin
   (CG-REG-001..006) must be hit by the regression, and every TP item of Phase 2 must list >= 1
   knob under `Knobs:` (an item with `Knobs: none` is Phase 1 only).
6. A reviewer other than the author confirms the mapping (cross-review policy): the check script
   output is attached to the review artifact AND the Critic performs a sampled semantic
   confirmation (Critic S-11b): N = 10 (feature, bin) pairs per area, drawn at random from the join
   of trace_feat_tp and trace_tp_bin, each judged "when this bin is hit, the feature's behaviour
   was evidenced" (yes/no with a one-line reason recorded in the review artifact); one "no"
   re-opens that area's mapping before promotion.
7. Bin -> feature granularity (Critic S-11c): a covergroup citing more than eight F-IDs carries
   per-coverpoint F-ID tags (`[F: ...]` inside the coverpoint expression, before `: bins`); the
   check resolves a bin to its coverpoint's tags first and to the CG `Features:` field only for an
   untagged coverpoint, and every tag must be a subset of the CG's Features. Every CG Features F-ID
   must be claimed by the `Features:` of >= 1 TP item listed under the CG's `TP items:` (Critic
   S-11e; a CG-only F-ID is either added to an owning item or dropped from the CG).

Check script inputs and outputs (proposal for the DV Lead's tooling, `gen_check_trace.py`):

- Inputs: dv/auto_dv/docs/gen_feature_list.md (F-ID universe: every `### F-` heading), the
  folded gen_test_plan.md (TP-ID universe and `Bins:` fields), gen_fcov_plan.md (CG/cp/bin
  universe from `- cp_` and `- cr_` lines, adopted flags from `Adopted (riscv-dv):`), the two
  trace CSVs per area (trace_feat_tp_<area>.csv, trace_tp_bin_<area>.csv), and optionally the
  merged URG grpinfo.txt for hit counts.
- Checks: (a) every F-ID appears in some trace_feat_tp row; (b) every tp_item in both CSVs exists
  in the test plan; (c) every (covergroup, coverpoint, bin) in trace_tp_bin exists in the fcov
  plan and its `adopted` flag matches the CG's Adopted field; (d) every CG's Features F-IDs exist;
  (e) every F-ID reaches >= 1 bin through (a)+(c); (f) every bin reaches >= 1 F-ID through (c)+(d)
  and the coverpoint tags of rule 7; (g) with URG input: the group score after ignore_bins
  (spec-derived, equal group weights) and the bin-level adopted ratio, separately; (h) every
  fcov_expectations/<test>.fcov.yaml bin exists in the plan, is neither ignored nor probe-gated,
  and covers >= 1 unconditional cp per owned CG; (i) every CG Features F-ID is claimed by an owning
  TP item (rule 7).
- Output: a table per area (features, TP items, bins, cross bins, adopted bins, unmapped
  features, orphan bins, orphan TP items) and a non-zero exit on any unmapped item; the table is
  committed under dv/auto_dv/evidence/.

## Counts

| Measure | REG | XIF | ADOPT | Total |
|---|---|---|---|---|
| covergroups | 10 | 12 | 6 | 28 |
| coverpoints (cp_*) | 48 | 55 | 9 | 112 |
| crosses (cr_*) | 15 | 33 | 0 | 48 |
| bins (coverpoint bins, legal) | 325 | 214 | 54 | 593 |
| cross bins (legal) | 207 | 477 | 0 | 684 |
| adopted bins (riscv-dv; adopted = 1) | 0 | 0 | 49 | 49 |

Of the REG coverpoint bins, 202 are knob transition bins (every ordered pair of values per knob,
explicitly enumerated, including the 12 of the two integrity-rate knobs and the 3 cross-reset
mml_on_to_* transitions; no transition is ignored). Ignored coverpoint bins: 0. Ignored cross
combinations, each with a reason: 230 (plan v2b adds the 11 of CG-XIF-001.cr_async_x_taken and the
2 of CG-XIF-007.cr_landing_x_outcome, both encoding X-9 / X-15). Spec-derived bins (adopted = 0):
1228 (544 coverpoint + 684 cross; the 5 non_link bins of CG-ADOPT-004.cp_ras are spec-derived).
Every legal bin is owned by >= 1 TP item and no CSV row references an ignored bin
(trace_tp_bin_xcut.csv has 1277 rows over 56 items; bins shared by several items appear once per
item). Counts come from the verification script run over this file's coverpoint and cross lines
after ignore_bins (plan v2b: 9 coverpoint bins and 17 cross bins added for C-4, C-6 and X-15; none
removed; the TP-XIF-004 data_outst class was re-anchored, not ignored).

## Probe candidates

- CG-XIF-012 (all bins): needs P1 `dummy_instr_id_o` (rtl/ibex_core.sv:91, an ibex_core output
  wired inside gen_dut_top but not on the wrapper boundary) and `fcov_dummy_instr_type`
  (rtl/ibex_if_stage.sv:818-821). Dummy instructions produce no RVFI record and no bus traffic
  (F-DIT-016, F-FE-018), so no boundary derivation exists. Coverage-only; recommend the DV Lead
  accept P1 or expose the two ports through gen_dut_top as coverage-only outputs (then it is a
  boundary signal, not a probe).
- CG-XIF-012.cp_dummy_type (and the crosses cr_event_x_type / cr_type_x_mode): `fcov_dummy_instr_type`
  (rtl/ibex_if_stage.sv:817-821) is NOT among P1's registered nets: probe candidate P9 (probe register
  entry needed). Probe status: pending probe-register ruling; excluded from manifests until ruled
  (Critic M-7a).
- CG-XIF-002.cp_window, CG-XIF-007 and S11 mode attribution are cycle-exact at the boundary after
  the S18 back-dating fix (rvfi_valid is one flop after WB exit, rtl/ibex_core.sv:1868; commit
  offsets 2 / 1 per gen_tb_architecture.md 8.2), so probe P4 (`ctrl_fsm_cs`, rtl/ibex_pkg.sv:291-
  302, or `fcov_interrupt_taken` / `fcov_debug_entry_if`, rtl/ibex_controller.sv:1085-1095) is NOT
  requested; the constants GEN_CSR_WRITE_TO_RVFI_OFFSET, GEN_TRAP_TO_RVFI_OFFSET and GEN_RVFI_ID_EXIT_OFFSET are confirmed
  at bring-up and a directed test pins them (C4.8 exactness table).
- CG-XIF-012 is probe-gated (P1 accepted coverage-only in gen_probe_register.md): its bins are in
  no fcov-expectation manifest until the register carries P1; TP-XIF-021 marks them so.
- CG-XIF-005 `fill_inflight` (S12) is derived from tracked cpuctrlsts.icache_enable and the ibus
  outstanding count; P2 (`fill_busy_q`) is the fallback if the boundary derivation mis-attributes
  uncached fetches during the invalidation walk. Recommend boundary first.
- CG-REG-008.cp_inflight_event.mid_zcmp and CG-XIF-006 use rvfi_ext_expanded_insn_valid/_last
  (rtl/ibex_core.sv:178-180): RVFI extension ports, not probes.

