# Component API: gen_scoreboard (hub, CSR model of record, comparator driver)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C4.7; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

The hub: subscribes to the RVFI monitor, both bus monitors, the irq/dbg agents and the misc
monitor; owns the CSR model of record (reset values plus every retired CSR write and trap
entry/exit), the counter model, the PMP model and the irq/NMI/debug checkers as sub-checkers, and
drives the ISA-model comparator (gen_isa_shim) per record.

## 2. Files (planned) and how to call it

`dv/auto_dv/env/gen_scoreboard.sv`; analysis imps for `gen_rvfi_txn`, `gen_rvfi_irq_txn`,
`gen_bus_txn`, `gen_irq_edge`, `gen_dbg_edge`, `gen_misc_txn`.

Per RVFI record: (1) fold Zcmp micro-ops; (2) determine the asynchronous events to inject; (3)
associate the record with bus transactions by order; (4) call the shim; (5) update the CSR/counter/
PMP models; (6) run the sub-checkers. End of test: compare Python's and SV's command counters,
drain outstanding transactions, report counts.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_chk_isa=0|1` | `PLUSARG_CHK_ISA` | master enable of the ISA-model compare; per-field knobs +gen_chk_isa_{pc,insn,trap,rd,mem,prv,pc_next,csr} | 1 |
| `+gen_sb_trace=1` | `PLUSARG_SB_TRACE` | debug log of every compared record | 0 |

## 4. Wave-level behaviour

Stores and loads retire after their bus response (WB stage waits for it), so bus-to-record
association is by order with the response preceding the record.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `isa_pc` | model pc before the step == `rvfi_pc_rdata` (exact per record) | fetch/branch target: `rtl/ibex_if_stage.sv` pc mux, `rtl/ibex_ex_block.sv` branch target ALU | `+gen_chk_isa_pc=0` |
| `isa_insn` | model instruction bits == `rvfi_insn` | compressed decoder expansion (`rtl/ibex_compressed_decoder.sv`), fetch data path | `+gen_chk_isa_insn=0` |
| `isa_trap` | model trap <=> `rvfi_trap`; cause per handler read-back | controller exception cause select (`rtl/ibex_controller.sv:299-337, 900-927`), decoder illegal detection | `+gen_chk_isa_trap=0` |
| `isa_rd` | GPR write (index, value) == `rvfi_rd_addr/rd_wdata` | ALU operator select (`rtl/ibex_alu.sv`), multiplier/divider (`rtl/ibex_multdiv_fast.sv`), decoder rd/we (`rtl/ibex_decoder.sv`), WB mux (`rtl/ibex_wb_stage.sv`) | `+gen_chk_isa_rd=0` |
| `isa_mem` | memory access address, size, store data == `rvfi_mem_*` | LSU address/data rotation and byte enables (`rtl/ibex_load_store_unit.sv:138-221`) | `+gen_chk_isa_mem=0` |
| `isa_prv` | `last_inst_priv == rvfi_mode` | privilege update on trap/mret (`rtl/ibex_cs_registers.sv:953-993`) | `+gen_chk_isa_prv=0` |
| `isa_pc_next` | model pc after the step == `rvfi_pc_wdata` (not on F-RVFI-010 records) | pc increment / redirect (`rtl/ibex_if_stage.sv`) | `+gen_chk_isa_pc_next=0` |
| `isa_csr` | every model CSR write (commit log type 4) == the legalized expectation (C5.3a) or the SPEC value (C5.3b rows); read-backs per C6 | CSR legalization and read mux (`rtl/ibex_cs_registers.sv`) | `+gen_chk_isa_csr=0` |

## 6. Failure path and diagnostics

`uvm_error` with id, record order, pc, expected-versus-actual; `uvm_fatal SB_DESYNC` when the
model and DUT pcs diverge for more than `GEN_SB_DESYNC_RECORDS` records (further compares are
meaningless).

## 7. Coverage hooks

Two-source crosses (interrupt vs outstanding bus response, PMP fault vs regime, ...) sampled here.

## 8. At build

Define `GEN_SB_DESYNC_RECORDS`; implement the association queue and prove it on the first
programs.
