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
`alert_internal` (never high), `data_tag_quiet` (never high), `alert_minor` (only within GEN_ICACHE_ECC_WINDOW of an ECC
injection announced through `gen_tb_pkg::gen_icram_events`; no injection exists yet, so any pulse is a failure),
`double_fault` (a pulse exactly GEN_TRAP_TO_RVFI_OFFSET cycles before the second synchronous trap record with no mret
between, from the model state); `crash_dump`, `core_busy` and `fetch_en` are not built.

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
or Off. `crash_dump_o` fields are combinational mirrors (rtl-arch CTRL-35): `exception_pc` = live
mepc, `exception_addr` = live mtval, `last_data_addr` = last LSU address, `current_pc`/`next_pc`
pipeline state.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `alert_minor` | `alert_minor_o` pulses only in the response window of an injected cache ECC error; exactly one pulse per injection | icache ECC error OR (`rtl/ibex_icache.sv:585`), `alert_minor_o` wiring (`rtl/ibex_core.sv:1337`) | `+gen_chk_alert_minor=0` |
| `alert_bus` | (v2, XM-L1) split by source: FETCH: `alert_major_bus_o` asserts in the `instr_rvalid_i` cycle of an injected corrupted beat whether or not the word is ever consumed (`instr_intg_err_o = instr_intg_err & instr_rvalid_i`, rtl/ibex_if_stage.sv:282; speculative and PMP-denied fetches included; class exact); DATA: asserts at the data response cycle of an injected corrupted load or store response (class windowed, `GEN_ALERT_BUS_WINDOW`, LSU registration verified at bring-up); never otherwise | integrity decoders (`rtl/ibex_load_store_unit.sv:385-393`, if_stage instruction integrity), OR at `rtl/ibex_core.sv:1353` | `+gen_chk_alert_bus=0` |
| `alert_internal` | `alert_major_internal_o == 0` always (RegFileECC = 0; only `pc_mismatch_alert` remains) | PC increment check (`rtl/ibex_if_stage.sv:658-692`), OR at `rtl/ibex_core.sv:1350` | `+gen_chk_alert_internal=0` |
| `crash_dump` | `exception_pc == model mepc`, `exception_addr == model mtval`, windowed(`GEN_CSR_WRITE_TO_RVFI_OFFSET`) around each retired CSR write / trap record; `last_data_addr` == last granted data address (exact per grant); `current_pc/next_pc` compared only while `core_busy_o == Off` | crash_dump assigns (`rtl/ibex_core.sv:1325-1330`), lsu_addr_last (`rtl/ibex_load_store_unit.sv:743`) | `+gen_chk_crash_dump=0` |
| `double_fault` | `double_fault_seen_o` pulses exactly when a synchronous trap record follows a previous one with no retired `mret` between (sync_exc_seen model); `cpuctrlsts` bits 6/7 read back per model | set/clear/pulse logic (`rtl/ibex_cs_registers.sv:890-965`) | `+gen_chk_double_fault=0` |
| `core_busy` | always exactly On or Off; after every retired WFI it is Off for exactly one cycle (WAIT_SLEEP, `ctrl_busy_o = 0` unconditionally, rtl/ibex_controller.sv:598-604) even with a wake condition already true; Off beyond that only with no wake term and no outstanding beat (SLEEP :606-621); On the same cycle a wake input asserts; no bus requests while Off (exact) | busy generation (`rtl/ibex_core.sv:496-522`), controller WAIT_SLEEP/SLEEP (`rtl/ibex_controller.sv:598-621`) | `+gen_chk_core_busy=0` |
| `data_tag_quiet` | `data_tag_o == 0` | carve-out sanity | `+gen_chk_data_tag_quiet=0` |
| `fetch_en` | while `fetch_enable_i != IbexMuBiOn`: no new `instr_req_o` except beats already owned by fill buffers, no new record with a different `pc_rdata`; trap-state changes allowed (Q-DL-8 default) | fetch gate (`rtl/ibex_core.sv:644-656`), controller halt_if (`rtl/ibex_controller.sv:996-999`) | `+gen_chk_fetch_en=0` |

## 6. Failure path and diagnostics

`uvm_error` per id with cycle and expected-versus-actual.

## 7. Coverage hooks

`gen_alert_cg`, `gen_sleep_cg`, `gen_double_fault_cg`, fetch_enable encodings.

## 8. At build

Decide the settle window for `crash_dump`; confirm alert pulse widths on the first waveforms.
