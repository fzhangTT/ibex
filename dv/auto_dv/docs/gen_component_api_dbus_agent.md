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
errors including per-half injection on split misaligned accesses. AS BUILT (step 1c): the same `gen_agents_pkg::gen_bus_agent` as the instruction side, instance `dbus_agent` on `gen_bus_if u_dbus_if` (`is_data = 1`): stores are performed into `gen_mem_model` with the byte enables at grant (an errored store still lands unless `+gen_dbus_err_store_perform=0`), loads read the model, the response carries a valid encoding of zero for stores; knobs `+gen_knob_dmem_*` map as on the instruction side, cap fixed at GEN_DBUS_MAX_OUTSTANDING = 2; MMIO windows (signature, irq ack, end-of-test, phase marker) and the tohost watch are the model's. (T-068) latency windows and injection rates come from the rendered `gen_regime_window` / `gen_regime_scalar` functions of gen_tb_pkg (source: the `regime_windows` block of gen_tb_knobs.yaml; rvalid classes min1 1, short 2..4, long 5..32, random 1..32 aligned with the fcov plan; gnt same_cycle 0, short 1..3, long 4..32, random 0..32; rates none 0, rare 2, frequent 50 per mille; caps 1/2/4/8); `chk_rvalid_legal_en` follows `+gen_chk_sva_rvalid_legal` with the `+gen_chk_all` isolation rule; the published `gen_bus_txn` carries the real grant latency (`gnt_delay`, `cycle_req` = the first cycle req was seen); the integrity geometry derives from the interface data width, guarded by a build-time fatal when it is not 39 bits.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_dbus_if.sv`, `dv/auto_dv/env/gen_dbus_pkg.sv` (`gen_dbus_cfg`,
`gen_dbus_item`, `gen_dbus_driver`, `gen_dbus_monitor`, `gen_dbus_sequencer`, `gen_dbus_agent`);
transaction `gen_bus_txn` with kind LOAD/STORE and `injected`.

As gen_ibus_agent (config in `uvm_config_db`, sequencer fed by the bridge for REGIME_SET and
MEM_ERR_ARM). Every injected error is published with `injected = 1` so the scoreboard arms the
ISA model fault and the NMI/alert checkers. AS BUILT (T-137): gen_bus_driver announces every bus-error response it
injects on the data bus (armed by MEM_ERR_ARM kind `GEN_MEM_ERR_ARM_KIND_ERR`, or drawn by the `err_rate` regime) to
`gen_tb_pkg::gen_bus_err_log` (word address; the last 256), and the scoreboard arms the model's fault only for an
announced word and consumes the announcement; data-side integrity corruptions (`GEN_MEM_ERR_ARM_KIND_INTG`,
`intg_err_rate`) are announced apart (`note_intg(addr)`: `intg_announced` and the address of the corruption that set
the DUT's pending bit, consumed by the scoreboard at the internal-NMI entry as the model's mtval): they raise alert_major_bus and an internal NMI rather than a
bus-error trap, and the irq checker accepts an NMI-vector entry without a pin NMI only after such a corruption. The
GEN_SB report's `bus_err_announced` is the error count.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_dbus_gnt_min/max, gen_dbus_rvalid_min/max` | `PLUSARG_DBUS_GNT_MIN/MAX, PLUSARG_DBUS_RVALID_MIN/MAX` | as the instruction agent; rvalid floor 1 | 0/3, 1/4 |
| `+gen_dbus_max_outstanding=<n>` | `PLUSARG_DBUS_MAX_OUTSTANDING` | hard cap `GEN_DBUS_MAX_OUTSTANDING` (= 2: the two halves of one split access, rtl/ibex_load_store_unit.sv:403-405, rtl/ibex_top.sv:229-233) | GEN_DBUS_MAX_OUTSTANDING |
| `+gen_dbus_err_rate, gen_dbus_err_window` | `PLUSARG_DBUS_ERR_RATE, PLUSARG_DBUS_ERR_WINDOW` | data_err_i injection probability and address window | 0, unset |
| `+gen_dbus_err_half=first|second|both|any` | `PLUSARG_DBUS_ERR_HALF` | which half of a split access an injected error hits | any |
| `+gen_dbus_err_store_perform=0|1` | `PLUSARG_DBUS_ERR_STORE_PERFORM` | whether an errored store still updates the memory model | 1 |
| `+gen_dbus_intg_err_rate, gen_dbus_intg_bits` | `PLUSARG_DBUS_INTG_ERR_RATE, PLUSARG_DBUS_INTG_BITS` | rdata integrity corruption (loads and store responses) | 0, 1 |
| `+gen_knob_dmem_gnt_delay=same_cycle|short|long|random` | `PLUSARG_KNOB_DMEM_GNT_DELAY` | layer-2 grant latency regime (value set and default from gen_tb_knobs.yaml; windows as the instruction agent) | short |
| `+gen_knob_dmem_rvalid_delay=min1|short|long|random` | `PLUSARG_KNOB_DMEM_RVALID_DELAY` | layer-2 response latency regime | short |
| `+gen_knob_dmem_err_rate=none|rare|frequent` | `PLUSARG_KNOB_DMEM_ERR_RATE` | data_err_i injection regime (none 0, rare 2, frequent 50 per mille) | none |
| `+gen_knob_dmem_intg_err_rate=none|rare|frequent` | `PLUSARG_KNOB_DMEM_INTG_ERR_RATE` | data integrity corruption regime | none |
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

## Export event rows (T-080 step 2, addendum Section 8)

Written through `gen_export_sink::write_event` with the rendered line functions when the source is active and enabled;
dbus rows: `req`, `gnt`, `rvalid` as for ibus (we and be from the request); the driver increments `evt_dbus_grants` in the grant beat.
