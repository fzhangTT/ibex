# Component API: gen_rvfi_monitor (retirement trace monitor)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C4.1; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Turns every `rvfi_valid` cycle into a `gen_rvfi_txn` and every rising edge of the `rvfi_ext_irq_valid`
level into an interrupt marker (a `gen_rvfi_txn` sampled at the rise cycle, published on `ap_irq`); the scoreboard's primary input and the source of
the bridge events (v2, A-01): the retirement count behind `evt_retired_target` / `evt_retired_hit` / `evt_retired_count` (the bridge's cycle threshold `evt_cycle_hit` is its sibling, fed by `cycle_count`, not by this monitor), plus `evt_irq_taken`, `evt_dbg_entered`. AS BUILT (step 2a): `gen_rvfi_pkg::gen_rvfi_monitor` on `dv/auto_dv/tb/gen_rvfi_if.sv` (instance `u_rvfi_if`, every wrapper rvfi_* port assigned in gen_tb_top; vif `uvm_test_top.env.rvfi_mon*`): samples at the posedge with `valid`, publishes `gen_rvfi_txn` on `ap` (and the `rvfi_ext_irq_valid` marker on `ap_irq`, once per rising edge of the level, Section 4), hands every record and marker to `gen_export_sink` (Section 8), checks `rvfi_order` (+1 per record, `rvfi_halt` never set; id rvfi_order under `+gen_chk_rvfi_proto`), toggles the bridge events `evt_dbg_entered` (first record in debug mode) and `evt_irq_taken` (`rvfi_intr`), `+gen_rvfi_trace=1` prints every record. `rvfi_pc_cont` and `rvfi_cap_quiet` follow with the misc checkers.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_rvfi_if.sv` (bundle of the wrapper's rvfi_* ports), `dv/auto_dv/env/
gen_rvfi_monitor.sv`; transaction fields: order, insn, trap, halt, intr, mode, ixl, rs1/rs2/rs3
addr+data, rd addr+data, pc_rdata, pc_wdata, mem addr/rmask/wmask/rdata/wdata, ext_pre_mip,
ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode, ext_rf_wr_suppress, ext_mcycle,
ext_mhpmcounters[10] (+h), ext_ic_scr_key_valid, ext_irq_valid, ext_expanded_insn_valid/insn/last,
cycle.

Analysis ports `ap` (records) and `ap_irq` (interrupt notifications); subscribers: gen_scoreboard,
gen_misc_monitor, coverage.

AS BUILT: the monitor is class `gen_rvfi_monitor` in `dv/auto_dv/env/gen_rvfi_pkg.sv` (no separate
`gen_rvfi_monitor.sv`); `ext_mhpmcounters[10]` and `ext_mhpmcountersh[10]` are sampled from the interface into the
txn only under `+gen_export_counters=1` (Section 8); the export hand-off is the `sink` handle that `gen_env` sets in
`connect_phase`.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_rvfi_trace=1` | `PLUSARG_RVFI_TRACE` | write an ASCII trace file (debug only) | 0 |
| `+gen_chk_rvfi_order / _pc_cont / _cap_quiet` | `PLUSARG_CHK_*` | checker enables | 1 |
| `+gen_export_file=<path>` | `PLUSARG_EXPORT_FILE` | consumed through the `sink` handle: every record and marker is handed to `gen_export_sink`, which writes them only when this knob names a file (gen_component_api_export_sink.md Section 3) | unset |
| `+gen_export_counters=1` | `PLUSARG_EXPORT_COUNTERS` | sample `ext_mhpmcounters` / `ext_mhpmcountersh` from the interface into the txn and append the 20 words to the `R` line | 0 |
| `+gen_export_sources=<csv>`, `+gen_export_flush_every=<n>` | `PLUSARG_EXPORT_SOURCES`, `PLUSARG_EXPORT_FLUSH_EVERY` | sink knobs, not read by the monitor: gen_component_api_export_sink.md Section 3 | `all`, 0 |

## 4. Wave-level behaviour

Sampled on the posedge where `rvfi_valid` is 1; all RVFI outputs are flops in the core (no
combinational race). With WritebackStage=1 a record appears one cycle after the instruction leaves
WB; dummy instructions produce no record and do not advance `rvfi_order`; trapping instructions
produce a record with `rvfi_trap`; `rvfi_intr` marks the first instruction of an interrupt
handler only; Zcmp micro-ops produce one record each with `ext_expanded_insn_valid`.

Interrupt markers: `rvfi_ext_irq_valid` is a LEVEL (rtl-arch rule X-16, plan convention C-13: it rises four
cycles after the interrupt decision and stays high until about two cycles after the handler's first instruction
enters ID). The monitor keeps the previous cycle's value and acts exactly once per rising edge, at the rise cycle,
with or without a retirement in that cycle: `ap_irq.write` once, `irq_markers++` once, one `I` line to the sink
(Section 8). The earlier per-cycle publication (a marker on every high cycle without a retirement) was a defect
corrected in this landing; it had never fired (irq_markers=0 in every retained run).

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `rvfi_order` | `rvfi_order` increments by one per record, never repeats; `rvfi_halt == 0` | RVFI order pipeline (`rtl/ibex_core.sv:1908, 2088`) | `+gen_chk_rvfi_order=0` |
| `rvfi_pc_cont` | non-trap, non-redirect record: next `pc_rdata == pc_wdata`; on trap/mret/dret/fence.i records `pc_wdata` is not checked until F-RVFI-010 is ruled; `pc_rdata` continuity is | pc_wdata mux (`rtl/ibex_core.sv:2095`), pc_id capture | `+gen_chk_rvfi_pc_cont=0` |
| `rvfi_cap_quiet` | `*_rcap == NULL_CAP`, `mem_is_cap == 0` | carve-out sanity | `+gen_chk_rvfi_cap_quiet=0` |

Known RVFI observations that are NOT DUT failures (gen_bug_log.md v1e, cited so neither `rvfi_proto` nor the
comparator flags them): B18 (rtl-arch BUG-10; the lock-step observation of step 2a): `rvfi_mem_rmask` is
`4'b1111` and `rvfi_mem_addr` equals the ALU result on every non-store record, so the mask rules apply only to
records the comparator classifies as loads or stores from the model's own access (`gen_scoreboard`: a DUT
read is inferred from the model, `rvfi_mem_wmask` is compared directly, the observation is counted as
`rvfi_rmask_on_nonload`); `rvfi_proto` never checks `rmask` on its own. B19 (pending rtl-arch confirmation;
rtl/ibex_core.sv:1885-1886): `rvfi_trap` is masked on an illegal ebreak variant while `dcsr.ebreakm/u` is set;
the plan's rule is that the comparator classifies that record by the `mcause` read-back rather than by
`rvfi_trap`. Status as built: B18 handling is built; the B19 classification is NOT built yet, so until it
lands a program that hits B19 reports an `isa_trap` mismatch, which a test must treat as the known B19
signature, not as a new DUT failure. Both rows are the DV Lead's plan v2b alignment items.

## 6. Failure path and diagnostics

`uvm_error` per id with order, pc, expected-versus-actual; `uvm_fatal GEN_RVFI_MON` when `vif`, `bridge_vif` or
`cfg` is missing from `uvm_config_db`. Export failures are the sink's, not the monitor's: `uvm_fatal GEN_EXPORT`
(the file cannot be opened; an unknown source name; `EXPORT_FLUSH` without the file knob), `uvm_error GEN_EXPORT`
(`$ferror` after a flush or at the end) and the Python `AssertionError` of `gen_export.read()`
(gen_component_api_export_sink.md Section 6). Diagnostics: the `report_phase` line `GEN_RVFI_MON records=<n>
irq_markers=<m>` must agree with the sink's `export: records=<n> markers=<m>` line; `+gen_rvfi_trace=1` prints
every record.

## 7. Coverage hooks

Sampling event for most of `gen_fcov_pkg` (instruction classes, traps, modes, Zcmp sequences,
interrupt entries).

## 8. Record export

What the monitor hands to `gen_export_sink` (the one writer of the export file): one `R` line per record, formatted
by the rendered function `gen_export_record_line(t, cfg.export_counters)` (`dv/auto_dv/env/
gen_export_record_line.svh`, included inside `gen_rvfi_pkg` after `gen_rvfi_txn`; its argument order is the yaml's
`export_record_fields`, 36 fields including `rs3_addr` and `rs3_rdata`, which the txn carries sampled from the
interface like `rs1`/`rs2`; the CHERIoT capability fields and `mem_is_cap` are not exported; the 20 counter words
follow only when the counters knob is on) through
`sink.write_record(line)`, in the same active-region step as `records++` and `ap.write(t)`; and one `I` line per
marker rising edge, `I <cycle> <ext_pre_mip> <ext_post_mip> <ext_nmi> <ext_nmi_int> <ext_debug_req>
<ext_debug_mode>` (all hex), through `sink.write_marker(line)` in the same step as `ap_irq.write`. The monitor
never touches the file, the header, the flush or the end marker, and issues no `$fflush`; the `sink` handle is set by
`gen_env`, and with `+gen_export_file` absent no line is formatted or handed over (the calls sit inside the `sink.enabled` guard).
The file format, the completeness rule of `gen_export.read(path, seq)`, the `EXPORT_FLUSH` command, the event
channel, the failure ids and the cost are in `dv/auto_dv/docs/gen_component_api_export_sink.md`.

## 9. At build

Confirm the Zcmp record count and `rvfi_order` stepping in bring-up; rtl-arch rulings F-RVFI-010
and F-RVFI-032.
