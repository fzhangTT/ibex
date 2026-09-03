# TB architecture document - Ibex core, opentitan configuration (skeleton v1)

Deliverable 4 (DV_prompt.txt Section 11). Owner: dv-lead (this document); TB Infra owns the component
sections (Section 5) and the component API documents they point at; Test Writer contributes the test
template section (Section 6) once the first passing test exists. Version: skeleton v1, 2026-09-03.
Status: DRAFT for the T-011 cross-model pre-execution review.

Build configuration: `opentitan` (ibex_configs.yaml). DUT: `gen_dut_top` = `ibex_core` +
`ibex_register_file_ff` (DV_prompt.txt Section 2). Wrapper parameters per owner question Q-002
defaults (MemECC=1, DummyInstructions=1, ICacheTweakInfection=1, ResetAll=1, RegFileECC=0,
DbgHwBreakNum=1, Dm* defaults, vendor/imp id 0, PMP resets from ibex_pkg; +define+RVFI;
cheriot_enable_i tied IbexMuBiOff). Companion plan set: dv/auto_dv/docs/gen_feature_list.md,
gen_test_plan.md, gen_fcov_plan.md, gen_bug_log.md, gen_probe_register.md (TB Infra),
gen_trace_feature_tp.csv, gen_trace_tp_bin.csv, dv/auto_dv/tools/gen_trace_check.py.

## 1. Phase 0 step 3 scoping answers (DV Lead; sources: rtl-arch gen_interface_inventory.md,
## gen_behaviour_summaries.md, tb-infra gen_tb_scoping_notes.md, the Critic's component review)

### 1.1 Interfaces that must be driven and their protocols
| Interface | Ports (ibex_core) | Protocol summary (authority) | Agent / driver |
|---|---|---|---|
| Clock/reset | clk_i, rst_ni | async assert, sync release; mid-run reset allowed (F-RST) | TB top |
| Static config | boot_addr_i (bits [7:0] = 0), hart_id_i, fetch_enable_i (MuBi), mcounteren_writable_i (MuBi) | sampled at boot / levels; exact IbexMuBiOn required, other encodings = Off with no alert (F-IMEM-023, F-SEC-020) | env knobs (gen_component_api_env_knobs.md) |
| Instruction bus | instr_req_o, instr_gnt_i, instr_addr_o, instr_rvalid_i, instr_rdata_i[38:0], instr_err_i | req held until gnt; gnt only with req; rvalid >= 1 cycle after gnt, one per grant, in order; up to 8 outstanding beats; speculative fetches; PMP-denied fetch still on the bus (inventory Section 11) | ibus agent (gen_component_api_ibus_agent.md) + memory model |
| Data bus | data_req_o, data_gnt_i, data_addr_o, data_we_o, data_be_o, data_wdata_o[38:0], data_rvalid_i, data_rdata_i[38:0], data_err_i | same handshake; <= 2 outstanding (misaligned pair); second half = first + 4; combinational rvalid/err -> req path (memory model registers responses); valid SECDED on every wdata (MEM-15) | dbus agent (gen_component_api_dbus_agent.md) + memory model (gen_component_api_mem_model.md) |
| Icache RAMs | ic_tag_req_o/write_o/addr_o/wdata_o/rdata_i, ic_data_* | 1-cycle synchronous read; invalidation writes from reset; ECC over address-derived tweak | icache RAM model (gen_component_api_icache_ram_model.md) with ECC-error injection |
| Scramble key | ic_scr_key_req_o (1-cycle pulse), ic_scr_key_valid_i (level) | responder must latch the pulse; fetch never blocked by an invalid key | scrkey responder (gen_component_api_scrkey_responder.md) |
| Interrupts | irq_software_i, irq_timer_i, irq_external_i, irq_fast_i[14:0], irq_nm_i | levels; a one-cycle pulse can be missed; hold policies until_taken / through_handler / pulse | irq agent (gen_component_api_irq_agent.md) |
| Debug | debug_req_i | level held until debug-mode entry; one directed pulse-drop test (B9) | dbg agent (gen_component_api_dbg_agent.md) |
| Outputs monitored | alert_minor_o, alert_major_internal_o, alert_major_bus_o, double_fault_seen_o, crash_dump_o, irq_pending_o, core_busy_o, rvfi_* | see checkers | misc monitor, RVFI monitor (gen_component_api_misc_monitor.md, gen_component_api_rvfi_monitor.md) |
| CHERIoT-only ports | cheriot_enable_i (tied Off inside the wrapper), data_tag_o, cap-related rvfi_* fields | must stay constant (F-CHERI-001) | gen_chk_cheriot_quiet |

### 1.2 Internal signals to probe
Target: zero probes for checking. The probe register (dv/auto_dv/docs/gen_probe_register.md, TB Infra
owner, Critic approval) records: RVFI as a define-gated DUT boundary interface; P1 (dummy-instruction
and register-file seam nets inside the wrapper) accepted for coverage and the B7 quantification only;
P2/P3/P5 rejected (boundary derivations exist); P4 (controller FSM state and RTL fcov_* nets)
conditional, coverage-only; P6 (CSR flops) off, debug-only. The fcov plan's probe candidates (Section 0
of gen_fcov_plan.md) map onto these entries; any new candidate goes through the register first.

### 1.3 Constants to centralize
One home per language domain (dv_principles.md Section 5): SV `gen_tb_pkg` (memory map, DmHaltAddr /
DmExceptionAddr alias, MuBi constants imported from ibex_pkg, plusarg and knob names, checker enable
knob names `+gen_chk_<name>_en`, regime knob names `+gen_knob_<name>`); a generated C header for the
ISA shim and test programs derived from gen_tb_pkg; one Python handles module for cocotb (hierarchy
paths and plusarg names) - see gen_component_api_constants_handles.md. Counts and ranges come from
ibex_pkg parameters and the config, never literals.

### 1.4 Sim-only features that need binds into the RTL
Through the single binds home (gen_component_api_binds.md, dv/auto_dv/tb/gen_binds.sv): protocol SVAs
gen_sva_ibus / gen_sva_dbus (assertion coverage), P1/P4 coverage-only observation binds, the requested
gen_sva_multdiv (F-MUL-028) and gen_sva_csr_excl, and fault-injection points for mutation evidence
(PC increment check, bus integrity) - the last are evidence-run-only and never enabled in a measured
regression. Error injection on rdata/integrity/ECC is done in the agents and RAM models, not by binds.

## 2. Checking strategy (summary; details in the component API documents)
- Reference model: upstream Spike (tools/riscv-isa-sim, pinned commit per SIM_RECIPE.md Section 11)
  behind a DPI-C shim (gen_component_api_isa_shim.md), step-locked to RVFI retirements, with a documented
  legalization layer for Ibex WARL choices (mtvec vectored-only, mip raw pins, fast irq mie bits, PMP
  reset values, misa, mcounteren gate, custom CSRs cpuctrlsts/secureseed, debug ROM addresses, NMI and
  internal-NMI emulation, mstack). Comparator gen_isa_compare: pc, insn, trap, rd write, mem access,
  mode, order; Zcmp micro-ops folded at rvfi_ext_expanded_insn_last; dummies excluded (RVFI never
  reports them). Draft-bitmanip instructions Spike lacks are checked by gen_chk_bitmanip_ref (new).
- Passive checkers (always on, uvm_error/uvm_fatal, each with a disable knob for mutation evidence):
  gen_chk_csr_readback, gen_chk_ibus_proto, gen_chk_dbus_proto, gen_chk_store_intg,
  gen_chk_bus_intg_rsp, gen_chk_pmp (own Smepmp model, gen_component_api_pmp_model.md), gen_chk_irq
  (gen_component_api_irq_checker.md), gen_chk_nmi, gen_chk_debug (gen_component_api_debug_checker.md),
  gen_chk_alerts, gen_chk_icache, gen_chk_crash_dump, gen_chk_double_fault, gen_chk_counters
  (gen_component_api_counter_model.md), gen_chk_sleep, gen_chk_fetch_en, gen_chk_cheriot_quiet;
  scoreboard gen_component_api_scoreboard.md. New checkers requested by the test plan (Section 2 of
  gen_test_plan.md): gen_chk_bitmanip_ref, gen_chk_timing_isa, gen_chk_zcmp_seq, gen_chk_csr_flush,
  gen_chk_exc_flush, gen_chk_trap_timing, gen_chk_rvfi_proto, gen_chk_regime, gen_chk_reset,
  gen_sva_multdiv, gen_sva_csr_excl, plus the extension lists per area. TB Infra accepts or pushes back
  on each in its component sections.
- Active checks live in tests: fire-checks per TP item (cocotb assertions) and read-backs.
- Bug-candidate direction (gen_bug_log.md): checker follows the spec for B1..B5, B7..B15 (expected-fail
  items); RTL for doc defects D1..D19 and RTL-defined behaviours (B6 reclassified, S1..S3).

## 3. Stimulus architecture (summary)
Programs in C/assembly and riscv-dv-generated streams loaded into the memory model and fetched over the
instruction bus; cocotb (Python) controls the run, the regime schedule and the agents through the bridge
(gen_component_api_bridge.md) without per-cycle polling; UVM agents drive the buses, interrupts and
debug request. Three randomization layers per DV_prompt.txt Section 6: per-transaction distributions
in the agents, regime knobs (gen_fcov_plan.md Section REG: 19 knobs, `+gen_knob_<name>=<value>` pins
one), and a randomized regime schedule per test (`+gen_regime_seed`, transitions covered). One run seed
(`+ntb_random_seed` = `RANDOM_SEED`) drives everything (TB_CONTRACT.md Section 1). Handshake, alive-bit
watchdog, objection holder and ASCII-only logging follow TB_CONTRACT.md Sections 2-4.

## 4. Coverage architecture (summary)
Covergroups in the gen_cg_ namespace implemented by TB Infra from gen_fcov_plan.md
(gen_component_api_coverage.md); sampling at boundary events and RVFI; probe-based sampling only per the
probe register. Code coverage scoped to the DUT hierarchy by the -cm_hier file (SIM_RECIPE.md Section
3); exclusions authored by rtl-arch (gen_exclusions_draft.md) with Critic approval. Per-test
fcov-expectation manifest (dv/auto_dv/fcov_expectations/) declares the bins each test must hit;
ci/check_fcov_expectations.py enforces it pre-merge. Completeness measure: gen_fcov_plan.md Section 1;
checked by dv/auto_dv/tools/gen_trace_check.py.

## 5. Component sections (TB Infra owns; each points at its API document)
| Component | API document | Status |
|---|---|---|
| gen_dut_top wrapper and filelist | gen_component_api_dut_top.md | delivered (T-005) |
| TB top, binds home | gen_component_api_binds.md | see doc |
| Constants and handles | gen_component_api_constants_handles.md | see doc |
| Environment knobs | gen_component_api_env_knobs.md | see doc |
| cocotb/UVM bridge | gen_component_api_bridge.md | see doc |
| Instruction bus agent | gen_component_api_ibus_agent.md | see doc |
| Data bus agent | gen_component_api_dbus_agent.md | see doc |
| Memory model | gen_component_api_mem_model.md | see doc |
| Icache RAM model | gen_component_api_icache_ram_model.md | see doc |
| Scramble-key responder | gen_component_api_scrkey_responder.md | see doc |
| Interrupt agent / checker | gen_component_api_irq_agent.md, gen_component_api_irq_checker.md | see doc |
| Debug agent / checker | gen_component_api_dbg_agent.md, gen_component_api_debug_checker.md | see doc |
| ISA shim (Spike) | gen_component_api_isa_shim.md | see doc |
| Scoreboard | gen_component_api_scoreboard.md | see doc |
| PMP model | gen_component_api_pmp_model.md | see doc |
| Counter model | gen_component_api_counter_model.md | see doc |
| RVFI monitor | gen_component_api_rvfi_monitor.md | see doc |
| Misc monitor (alerts, crash dump, double fault, core_busy, irq_pending) | gen_component_api_misc_monitor.md | see doc |
| Coverage | gen_component_api_coverage.md | see doc |
| Checkers requested by the test plan (Section 2) | (to be added by TB Infra) | open |

## 6. Test template (Test Writer; placeholder)
Setup (config banner, seed log, knob pinning), regime schedule, stimulus body, fire-check(s),
fcov-expectation declaration, finish handshake - written from the TB as built once the first passing
test exists (agent_team_prompt.txt Test Writer section).

## 7. Decisions and open items
- Wrapper representation: split *_intg ports (pure wiring) and no clock gate in the wrapper (DV Lead
  decision, reading report 6a); core_busy_o is the sleep observable.
- Pending owner questions affecting the TB: Q-002 (wrapper parameters), Q-003 (executed), Q-004/Q-005
  (checker direction for B1/B2 and B7), Q-DL-7..10 (partial misaligned store, fetch_enable behaviour,
  unsolicited rvalid policy, local Spike patch).
- Open items from the test plan's per-area "Open questions" subsections are triaged by the DV Lead in
  gen_reading_report.md; those needing TB Infra decisions are the new-checker list and the probe
  candidates.
