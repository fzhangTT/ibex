# Component API: gen_ibus_agent (instruction memory agent)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C3.1; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

The only driver of `instr_gnt_i`, `instr_rvalid_i`, `instr_rdata_i[MemDataWidth-1:0]` and
`instr_err_i`: a reactive slave that serves fetches from the shared memory model (gen_mem_model)
with randomized grant and response latency, in-order responses, and error/integrity injection.
The DUT's icache is the only requester; PMP-denied fetches still reach this bus and are served
normally (rtl-arch MEM-16).

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_ibus_if.sv` (interface on the wrapper's instr_* ports), `dv/auto_dv/env/
gen_ibus_pkg.sv` with `gen_ibus_cfg`, `gen_ibus_item` (regime/error-arm items), `gen_ibus_driver`,
`gen_ibus_monitor`, `gen_ibus_sequencer`, `gen_ibus_agent`; transaction type `gen_bus_txn`
{kind=FETCH, addr, data, intg, err, gnt_delay, rvalid_delay, cycle_req, cycle_gnt, cycle_rvalid,
outstanding_at_gnt, injected}.

Instantiated by `gen_env`; `gen_ibus_cfg` is built from plusargs by `gen_base_test` and placed in
`uvm_config_db`; the virtual interface handle comes from `gen_tb_top`. Runtime regime changes and
error arming arrive as `gen_ibus_item`s on the sequencer from the bridge (REGIME_SET,
MEM_ERR_ARM). The monitor publishes every transaction on analysis port `ap` (scoreboard, coverage,
checkers).

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_ibus_gnt_min=<n>` | `PLUSARG_IBUS_GNT_MIN` | grant latency window low bound (cycles; 0 = same cycle) | 0 |
| `+gen_ibus_gnt_max=<n>` | `PLUSARG_IBUS_GNT_MAX` | grant latency window high bound | 3 |
| `+gen_ibus_rvalid_min=<n>` | `PLUSARG_IBUS_RVALID_MIN` | response latency after grant; hard floor 1 (a same-cycle response is illegal for the icache) | 1 |
| `+gen_ibus_rvalid_max=<n>` | `PLUSARG_IBUS_RVALID_MAX` | response latency high bound | 4 |
| `+gen_ibus_max_outstanding=<n>` | `PLUSARG_IBUS_MAX_OUTSTANDING` | grants in flight before gnt is withheld; hard cap `GEN_IBUS_MAX_OUTSTANDING` = `GEN_ICACHE_NUM_FB * ibex_pkg::IC_LINE_BEATS` (NUM_FB = 4 is the one re-typed icache localparam, rtl/ibex_icache.sv:72) | GEN_IBUS_MAX_OUTSTANDING |
| `+gen_ibus_err_rate=<per_mille>` | `PLUSARG_IBUS_ERR_RATE` | probability of instr_err_i per transaction | 0 |
| `+gen_ibus_err_window=lo:hi` | `PLUSARG_IBUS_ERR_WINDOW` | address window where injected errors apply (any if unset) | unset |
| `+gen_ibus_intg_err_rate=<per_mille>` | `PLUSARG_IBUS_INTG_ERR_RATE` | probability of corrupting rdata integrity bits | 0 |
| `+gen_ibus_intg_bits=1|2` | `PLUSARG_IBUS_INTG_BITS` | bits flipped per corrupted response | 1 |
| `+gen_ibus_regime=<name>` | `PLUSARG_IBUS_REGIME` | named distribution set: fast, slow, bursty, stall, err_heavy, intg_err | fast |
| `+gen_chk_ibus_proto / gen_chk_ibus_outstanding / gen_chk_bus_rvalid_legal` | `PLUSARG_CHK_*` | checker enables (grant-order consistency is an agent-internal `assert`, not a checker row, v2 XM-L3) | 1 |

## 4. Wave-level behaviour

`gnt` is combinational from `req` when the drawn delay is 0, otherwise a flop-driven pulse; the
driver never asserts `gnt` without `req`. Each grant pushes {addr, latency, error/integrity
decision} into an in-order queue of depth `GEN_IBUS_MAX_OUTSTANDING`; a response pops after its
latency and is driven for exactly one cycle from flops (`rvalid`, `rdata`, `err` registered;
minimum latency 1 by construction). HARD RULE (rtl-arch T-022 evidence 5.2): `rvalid` is driven
only for a granted request, never in the grant cycle and never without an outstanding grant; the
icache does not defend against either (rtl/ibex_icache.sv:851). Enforced by construction and
asserted by the TB self-check `sva_rvalid_legal`. `rdata[31:0]` = memory word, `rdata[38:32]` = `prim_secded_inv_39_32_enc` of it
(vendor primitive used as test equipment) unless corrupted. Speculative fetches are served like
any other; the agent does not know what the core will execute.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `ibus_proto` | `req & ~gnt` => `req` and `addr` unchanged next cycle; `addr[1:0] == 0`; no X on `req` | icache request hold / arbitration (`rtl/ibex_icache.sv:756-775, 842`), address mux (`:1030-1037`) | `+gen_chk_ibus_proto=0` |
| `ibus_outstanding` | granted-unanswered `<= GEN_IBUS_MAX_OUTSTANDING`; `core_busy_o != Off` while > 0 (exact) | fill-buffer counters (`rtl/ibex_icache.sv:759-784`), `busy_o` (`:1304`) | `+gen_chk_ibus_outstanding=0` |
| `bus_rvalid_legal` | TB stimulus legality: `rvalid` only while a grant is outstanding and never in the grant cycle | TB self-check (not a DUT checker; not counted in the trust-triad evidence) | `+gen_chk_bus_rvalid_legal=0` |

## 6. Failure path and diagnostics

`uvm_error` with the checker id, cycle, expected-versus-actual. `uvm_fatal IBUS_QUEUE` if the
in-order queue overflows (a protocol-impossible state). Debug prints behind `+gen_dbg_ibus=1`.

## 7. Coverage hooks

Samples for `gen_ibus_cg` (in gen_fcov_pkg) on every grant/response: latency bins, outstanding
depth at grant (including 8), error/integrity injection, address window, regime id; the
transition covergroup samples REGIME_SET commands.

## 8. At build

Confirm the outstanding bound of 8 with a slow-rvalid/fast-gnt regime after a branch; measure the
latency needed for `GEN_IRQ_ENTRY_BOUND_RECORDS`; fill in file names once created.
