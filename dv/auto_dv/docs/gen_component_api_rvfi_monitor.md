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

Turns every `rvfi_valid` cycle into a `gen_rvfi_txn` and every `rvfi_ext_irq_valid` pulse
without a retirement into a `gen_rvfi_irq_txn`; the scoreboard's primary input and the source of
the bridge events (v2, A-01): the retirement count behind `evt_retired_target` / `evt_thresh_hit` / `evt_retired_count`, plus `evt_irq_taken`, `evt_dbg_entered`. AS BUILT (step 2a): `gen_rvfi_pkg::gen_rvfi_monitor` on `dv/auto_dv/tb/gen_rvfi_if.sv` (instance `u_rvfi_if`, every wrapper rvfi_* port assigned in gen_tb_top; vif `uvm_test_top.env.rvfi_mon*`): samples at the posedge with `valid`, publishes `gen_rvfi_txn` on `ap` (and the `rvfi_ext_irq_valid` marker without a retirement on `ap_irq`), checks `rvfi_order` (+1 per record, `rvfi_halt` never set; id rvfi_order under `+gen_chk_rvfi_proto`), toggles the bridge events `evt_dbg_entered` (first record in debug mode) and `evt_irq_taken` (`rvfi_intr`), `+gen_rvfi_trace=1` prints every record. `rvfi_pc_cont` and `rvfi_cap_quiet` follow with the misc checkers.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_rvfi_if.sv` (bundle of the wrapper's rvfi_* ports), `dv/auto_dv/env/
gen_rvfi_monitor.sv`; transaction fields: order, insn, trap, halt, intr, mode, ixl, rs1/rs2/rs3
addr+data, rd addr+data, pc_rdata, pc_wdata, mem addr/rmask/wmask/rdata/wdata, ext_pre_mip,
ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode, ext_rf_wr_suppress, ext_mcycle,
ext_mhpmcounters[10] (+h), ext_ic_scr_key_valid, ext_irq_valid, ext_expanded_insn_valid/insn/last,
cycle.

Analysis ports `ap` (records) and `ap_irq` (interrupt notifications); subscribers: gen_scoreboard,
gen_misc_monitor, coverage.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_rvfi_trace=1` | `PLUSARG_RVFI_TRACE` | write an ASCII trace file (debug only) | 0 |
| `+gen_chk_rvfi_order / _pc_cont / _cap_quiet` | `PLUSARG_CHK_*` | checker enables | 1 |

## 4. Wave-level behaviour

Sampled on the posedge where `rvfi_valid` is 1; all RVFI outputs are flops in the core (no
combinational race). With WritebackStage=1 a record appears one cycle after the instruction leaves
WB; dummy instructions produce no record and do not advance `rvfi_order`; trapping instructions
produce a record with `rvfi_trap`; `rvfi_intr` marks the first instruction of an interrupt
handler only; Zcmp micro-ops produce one record each with `ext_expanded_insn_valid`.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `rvfi_order` | `rvfi_order` increments by one per record, never repeats; `rvfi_halt == 0` | RVFI order pipeline (`rtl/ibex_core.sv:1908, 2088`) | `+gen_chk_rvfi_order=0` |
| `rvfi_pc_cont` | non-trap, non-redirect record: next `pc_rdata == pc_wdata`; on trap/mret/dret/fence.i records `pc_wdata` is not checked until F-RVFI-010 is ruled; `pc_rdata` continuity is | pc_wdata mux (`rtl/ibex_core.sv:2095`), pc_id capture | `+gen_chk_rvfi_pc_cont=0` |
| `rvfi_cap_quiet` | `*_rcap == NULL_CAP`, `mem_is_cap == 0` | carve-out sanity | `+gen_chk_rvfi_cap_quiet=0` |

## 6. Failure path and diagnostics

`uvm_error` per id with order, pc, expected-versus-actual.

## 7. Coverage hooks

Sampling event for most of `gen_fcov_pkg` (instruction classes, traps, modes, Zcmp sequences,
interrupt entries).

## 8. At build

Confirm the Zcmp record count and `rvfi_order` stepping in bring-up; rtl-arch rulings F-RVFI-010
and F-RVFI-032.
