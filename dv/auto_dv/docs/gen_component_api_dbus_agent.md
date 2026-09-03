# Component API: gen_dbus_agent (data memory agent)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C3.2; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Driver of `data_gnt_i`, `data_rvalid_i`, `data_rdata_i[MemDataWidth-1:0]`, `data_err_i`;
consumer of `data_req_o/we/be/addr/wdata[38:0]/tag_o`. Performs stores into the memory model
(enabled byte lanes only), serves loads, sinks the MMIO windows, injects bus and integrity
errors including per-half injection on split misaligned accesses.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_dbus_if.sv`, `dv/auto_dv/env/gen_dbus_pkg.sv` (`gen_dbus_cfg`,
`gen_dbus_item`, `gen_dbus_driver`, `gen_dbus_monitor`, `gen_dbus_sequencer`, `gen_dbus_agent`);
transaction `gen_bus_txn` with kind LOAD/STORE and `injected`.

As gen_ibus_agent (config in `uvm_config_db`, sequencer fed by the bridge for REGIME_SET and
MEM_ERR_ARM). Every injected error is published with `injected = 1` so the scoreboard arms the
ISA model fault and the NMI/alert checkers.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_dbus_gnt_min/max, gen_dbus_rvalid_min/max` | `PLUSARG_DBUS_GNT_MIN/MAX, PLUSARG_DBUS_RVALID_MIN/MAX` | as the instruction agent; rvalid floor 1 | 0/3, 1/4 |
| `+gen_dbus_max_outstanding=<n>` | `PLUSARG_DBUS_MAX_OUTSTANDING` | hard cap `GEN_DBUS_MAX_OUTSTANDING` (= 2: the two halves of one split access, rtl/ibex_load_store_unit.sv:403-405, rtl/ibex_top.sv:229-233) | GEN_DBUS_MAX_OUTSTANDING |
| `+gen_dbus_err_rate, gen_dbus_err_window` | `PLUSARG_DBUS_ERR_RATE, PLUSARG_DBUS_ERR_WINDOW` | data_err_i injection probability and address window | 0, unset |
| `+gen_dbus_err_half=first|second|both|any` | `PLUSARG_DBUS_ERR_HALF` | which half of a split access an injected error hits | any |
| `+gen_dbus_err_store_perform=0|1` | `PLUSARG_DBUS_ERR_STORE_PERFORM` | whether an errored store still updates the memory model | 1 |
| `+gen_dbus_intg_err_rate, gen_dbus_intg_bits` | `PLUSARG_DBUS_INTG_ERR_RATE, PLUSARG_DBUS_INTG_BITS` | rdata integrity corruption (loads and store responses) | 0, 1 |
| `+gen_dbus_regime=<name>` | `PLUSARG_DBUS_REGIME` | fast, slow, bursty, stall, err_heavy, intg_err, mis_err_first, mis_err_second | fast |
| `+gen_chk_dbus_proto / _outstanding / _split / _store_intg` | `PLUSARG_CHK_*` | checker enables | 1 |

## 4. Wave-level behaviour

As the instruction agent, with response registers only: the LSU may issue the next request in
the response cycle (rtl-arch AN s5), so a combinational rvalid path would loop. The same HARD RULE
applies: `rvalid` only for a granted request, never in the grant cycle (`sva_rvalid_legal`). Errored responses
still carry integrity-valid `rdata` unless an integrity error is also injected; for stores the
agent returns a constant integrity-valid word (the core checks store-response integrity too).
Split misaligned accesses: two word-aligned transactions, first the word holding the start
address, then the next word; byte enables and lane placement per rtl-arch MEM-08.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `dbus_proto` | `req & ~gnt` => `req`, `addr`, `we`, `be`, `wdata[38:0]` unchanged next cycle; `addr[1:0]==0`; `data_tag_o == 0` | LSU output muxes (`rtl/ibex_load_store_unit.sv:719-724`), addr_last update (`:254-266`) | `+gen_chk_dbus_proto=0` |
| `dbus_outstanding` | granted-unanswered `<= GEN_DBUS_MAX_OUTSTANDING`, and 2 only for the two halves of one split access (exact) | LSU FSM (`:431-600`) | `+gen_chk_dbus_outstanding=0` |
| `dbus_split` | split predicate `(word & off!=0) | (half & off==3)`; second address = first word + 4; be/lane table (MEM-08); second half issued after a first-half error, its response ignored (MEM-10) | split logic (`:403-405`), be generation (`:138-191`), wdata rotation (`:199-208`), WAIT_RVALID_MIS path (`:503-531`) | `+gen_chk_dbus_split=0` |
| `dbus_store_intg` | STORES only (`req & gnt & we`): `wdata[38:32]` decodes with zero syndrome over the full rotated 32-bit word incl. disabled lanes; on LOADS `wdata` is architecturally don't-care (F-DMEM-035): X-tolerant, observed only as coverage `gen_dbus_cg.cp_load_wdata_intg_valid` | encoder wiring (`rtl/ibex_load_store_unit.sv:731-735`) | `+gen_chk_dbus_store_intg=0` |

## 6. Failure path and diagnostics

`uvm_error` per checker id; `uvm_fatal DBUS_QUEUE` on queue overflow; `uvm_error MEM_UNMAPPED` on
an access outside every mapped region unless `+gen_mem_unmapped_ok=1` (then an error response is
returned, which is how bus-error stimulus by address works). Debug behind `+gen_dbg_dbus=1`.

## 7. Coverage hooks

`gen_dbus_cg`: latency, outstanding depth, split cases (type x offset), be patterns, error/half
crosses, integrity injection, MMIO window hits, regime id and transitions.

## 8. At build

Confirm the second-half byte-enable table against the first waveforms; decide the MMIO window
addresses in gen_tb_pkg (signature, irq-ack, end-of-test).
