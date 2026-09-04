# Component API: gen_misc_monitor (alerts, crash_dump, double_fault, core_busy, fetch_enable, data_tag)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C4.2; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Samples the wrapper's miscellaneous outputs every cycle and runs the boundary checkers that need
the agents' injection bookkeeping (injected integrity and cache-ECC errors) and the scoreboard's
retirement facts (traps, mret, CSR writes). AS BUILT (step 2b, T-090): `gen_checkers_pkg::gen_misc_monitor` on
`dv/auto_dv/tb/gen_misc_if.sv` (alerts, crash_dump, double_fault_seen, core_busy, data_tag_o, fetch_enable, irq_pending):
`alert_bus` (exact: high in the rvalid cycle of a response the bus driver marked `intg_corrupt`, never otherwise),
`alert_internal` (never high), `data_tag_quiet` (never high), `alert_minor` (two halves: a pulse needs a tag-RAM ECC injection
announced through `gen_tb_pkg::gen_icram_events` within GEN_ICACHE_ECC_WINDOW cycles before it, and a QUALIFIED injection owes exactly
one pulse in that window; the tag RAM models `dv/auto_dv/tb/gen_icache_ram.sv` inject at `knob_icache_ecc_err_rate`'s rate, default none),
`double_fault` (a pulse exactly GEN_TRAP_TO_RVFI_OFFSET cycles, GEN_LSU_TRAP_TO_RVFI_OFFSET for a load/store fault, before the second synchronous trap record with no mret
between, from the model state), `crash_dump` (the exception_pc / exception_addr mirrors of mepc / mtval against the model of record at every record, the write-edge offsets named), `fetch_en` (no record later than GEN_FETCH_EN_DRAIN_CYCLES after fetch_enable_i left On); `core_busy` is not built.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_misc_if.sv` (alert_minor_o, alert_major_internal_o, alert_major_bus_o,
crash_dump_o, double_fault_seen_o, irq_pending_o, core_busy_o, data_tag_o, fetch_enable_i),
`dv/auto_dv/env/gen_misc_monitor.sv`.

Subscribes to the agents' `ap` (injected flags) and the scoreboard's model events; publishes
`gen_misc_txn` per cycle of interest.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_chk_alert_minor / _alert_bus / _alert_internal / _crash_dump / _double_fault / _core_busy / _data_tag_quiet / _fetch_en` | `PLUSARG_CHK_*` | checker enables | 1 |

## 4. Wave-level behaviour

Alerts are combinational, one cycle per offending cycle, may repeat. `core_busy_o` is exactly On
or Off. `crash_dump_o` fields are combinational mirrors (rtl-arch CTRL-35; the design documents list the port only,
doc/02_user/integration.rst:319 "a set of signals that can be captured on reset to aid crash debugging", and do not define
the fields, so the mirror's meaning is the RTL's, rtl/ibex_core.sv:1329-1330, and the rule is an RTL-anchored mirror with
named tolerances, CR-2B-L-9): `exception_pc` = live
mepc, `exception_addr` = live mtval, `last_data_addr` = last LSU address, `current_pc`/`next_pc`
pipeline state.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `alert_minor` | `alert_minor_o` pulses only within GEN_ICACHE_ECC_WINDOW of a tag-RAM ECC injection (the injections of one lookup cycle share one pulse), and every qualified injection is followed by a pulse in that window; qualified = the cache enabled per the scoreboard's cpuctrlsts tracking and no invalidation-sweep tag write within GEN_ICACHE_ECC_GRACE_CYCLES (a lookup made while disabled or invalidating reads the tag RAM unchecked, rtl/ibex_icache.sv:266, and the TB learns both states late). A sweep write is an all-ways tag write at index 0 or at the index after the previous all-ways write one cycle later (the INVAL_CACHE state writes consecutive indices on consecutive cycles); the all-ways write of an ECC correction (rtl/ibex_icache.sv:591, after a tag error) opens no grace, since the lookups after it are checked; a correction landing on index 0 is the one misclassification (1 in IC_NUM_LINES). Mutation classes: an injection not announced (MUT-ICE-ANN: the pulse-without-injection half), an announcement without a corruption (MUT-ICE-MISS: the missing-pulse half), a DUT that raised the alert late or never (the protocol SVA sva_alert_minor_window shares the window); `+gen_chk_alert_minor=0` disables both halves; `+gen_knob_icache_ecc_err_rate=none` (the default) injects nothing, so a green run without the knob proves only the first half | icache ECC error OR (`rtl/ibex_icache.sv:585`), `alert_minor_o` wiring (`rtl/ibex_core.sv:1337`) | `+gen_chk_alert_minor=0` |
| `alert_bus` | (v2, XM-L1) split by source: FETCH: `alert_major_bus_o` asserts in the `instr_rvalid_i` cycle of an injected corrupted beat whether or not the word is ever consumed (`instr_intg_err_o = instr_intg_err & instr_rvalid_i`, rtl/ibex_if_stage.sv:282; speculative and PMP-denied fetches included; class exact); DATA: asserts at the data response cycle of an injected corrupted load or store response (class windowed, `GEN_ALERT_BUS_WINDOW`, LSU registration verified at bring-up); never otherwise | integrity decoders (`rtl/ibex_load_store_unit.sv:385-393`, if_stage instruction integrity), OR at `rtl/ibex_core.sv:1353` | `+gen_chk_alert_bus=0` |
| `alert_internal` | `alert_major_internal_o == 0` always (RegFileECC = 0; only `pc_mismatch_alert` remains) | PC increment check (`rtl/ibex_if_stage.sv:658-692`), OR at `rtl/ibex_core.sv:1350` | `+gen_chk_alert_internal=0` |
| `crash_dump` | BUILT (landing 2b): at every published record `exception_pc == model mepc` and `exception_addr == model mtval` (the mirrors, rtl/ibex_core.sv:1329-1330), read live at the record's posedge; two named exceptions: LATE, the mirror still shows the previous record's values because the trap saved at the record's own edge (load/store faults, GEN_LSU_TRAP_TO_RVFI_OFFSET = 0), and EARLY, the mirror already shows the NEXT record's values (its CSR write edge is GEN_CSR_WRITE_TO_RVFI_OFFSET ahead of its record), judged when the next state arrives; counts late/early/mismatches in the GEN_MISC report (gen_fu_l2b_dmem_err_dir_*: 2466 checked, 54 late, 0 mismatches; gen_fu_l2b_ebreak_r10_*: 6 early). `last_data_addr`, `current_pc` / `next_pc` NOT compared (the export carries them). Mutation MB13 (the observed exception_pc offset by 4): caught at order 1, ablation PASS | crash_dump assigns (`rtl/ibex_core.sv:1326-1330`) | `+gen_chk_crash_dump=0` |
| `double_fault` | `double_fault_seen_o` pulses exactly when a synchronous trap record follows a previous one with no executed `mret` between (sync_exc_seen model; records in debug mode and trapping mrets are excluded, rtl/ibex_cs_registers.sv:918, :965); the pulse is GEN_TRAP_TO_RVFI_OFFSET cycles before the record for an ID-stage exception and GEN_LSU_TRAP_TO_RVFI_OFFSET (0) for a load/store fault, whose error is seen in WB and saved from FLUSH one cycle later while its record leaves WB (rtl/ibex_controller.sv:827-845, rtl/ibex_core.sv:1888-1890; landing 1c, mutant RC3); `cpuctrlsts` bits 6/7 read back per model; mutation MB11 (observed pin inverted) | set/clear/pulse logic (`rtl/ibex_cs_registers.sv:890-965`) | `+gen_chk_double_fault=0` |
| `core_busy` | always exactly On or Off; after every retired WFI it is Off for exactly one cycle (WAIT_SLEEP, `ctrl_busy_o = 0` unconditionally, rtl/ibex_controller.sv:598-604) even with a wake condition already true; Off beyond that only with no wake term and no outstanding beat (SLEEP :606-621); On the same cycle a wake input asserts; no bus requests while Off (exact) | busy generation (`rtl/ibex_core.sv:496-522`), controller WAIT_SLEEP/SLEEP (`rtl/ibex_controller.sv:598-621`) | `+gen_chk_core_busy=0` |
| `data_tag_quiet` | `data_tag_o == 0` | carve-out sanity | `+gen_chk_data_tag_quiet=0` |
| `fetch_en` | BUILT (landing 2b): after `fetch_enable_i` leaves On (sampled at the posedge), only the in-flight instructions retire: a record later than GEN_FETCH_EN_DRAIN_CYCLES (64) after that edge is a failure (intent: doc/02_user/integration.rst:323-328, fetch_enable_i allows the core to fetch, Off stops fetching and the pipeline drains; the bound is TB-derived, not read from the RTL: the longest instruction, a 37-cycle divide, plus the longest response the bus agent holds outstanding under its `long` rvalid regime, rounded up to 64; rtl/ibex_core.sv:644-656 is the mechanism, CR-2B-L-9); back On clears the window. Unit test gen_ut_fetch_en (Off after 60 records, drain, 256 idle cycles, On, tohost; also under long rvalid delays); mutation MB14 (the DUT's fetch_enable_i tied On while the TB drives Off): caught at order 90, 68 cycles after the edge, ablation PASS. NOT built: the bus-side clause (no new `instr_req_o` beyond the fill buffers) | fetch gate (`rtl/ibex_core.sv:644-656`), controller halt_if (`rtl/ibex_controller.sv:996-999`) | `+gen_chk_fetch_en=0` |

## 6. Failure path and diagnostics

`uvm_error` per id with cycle and expected-versus-actual.

## 7. Coverage hooks

`gen_alert_cg`, `gen_sleep_cg`, `gen_double_fault_cg`, fetch_enable encodings.

## 8. At build

Decide the settle window for `crash_dump`; confirm alert pulse widths on the first waveforms.

## Export event rows (T-080 step 2, addendum Section 8)

Written through `gen_export_sink::write_event` with the rendered line functions when the source is active and enabled;
alert rows (`alert_minor`, `alert_major_bus`, `alert_major_internal`, `double_fault_seen`) and misc rows (`irq_pending`, `core_busy` as the MuBi encoding, `crash_dump_current_pc`, `crash_dump_next_pc`, `crash_dump_last_data_addr`, `crash_dump_exception_pc`, `crash_dump_exception_addr`): the level at reset release, then every change, sampled at the posedge (about two crash_dump lines per retired instruction; `+gen_export_sources` without misc drops them).
