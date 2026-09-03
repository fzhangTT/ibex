# Component API: gen_pmp_model (PMP checker for fetch and data)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C4.3; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Intent-derived Smepmp model (16 regions, G = 0, TOR/NA4/NAPOT, L bit, mseccfg MML/MMWP/RLB,
privilege from `mstatus.MPRV ? MPP : prv` for data and current prv for fetch, debug-mode exemption
for the DM window) applied per word half to every fetch and data access.

## 2. Files (planned) and how to call it

`dv/auto_dv/env/gen_pmp_model.sv` (class, owned by the scoreboard); inputs: the CSR model of
record (pmpcfg/pmpaddr/mseccfg), each RVFI record (fetch pc and pc+2 for a word-crossing 32-bit
instruction; data address and size), the dbus monitor (presence/absence of transactions).

Called by the scoreboard per record; predicts fault/no-fault per half and the expected `mtval`.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_chk_pmp_fetch / _pmp_data / _pmp_csr_warl` | `PLUSARG_CHK_*` | checker enables | 1 |

## 4. Wave-level behaviour

Prediction only; no signals driven.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `pmp_fetch` | predicted fetch denial <=> `rvfi_trap` with cause 1 (cause observed through the handler's `csrr mcause`); PMP-denied fetches still appear on the bus (MEM-16) | region match / permission (`rtl/ibex_pmp.sv`), PMP_I/PMP_I2 channels (`rtl/ibex_core.sv:1590-1604`) | `+gen_chk_pmp_fetch=0` |
| `pmp_data` | predicted denial of a word half <=> no bus transaction for that word and a trap record with cause 5/7; `mtval` = original EA for a first-half fault, aligned second word for a second-half fault (MEM-13); the permitted other half still appears on the bus (RTL-defined, Q-DL-7 default). SPEC direction on B2/BUG-01: with `dcsr.mprven = 0` the model ignores `mstatus.MPRV` in debug mode; debug-mode load/store tests with MPRV set are `expected_fail: true` | PMP_D channel and request gating (`rtl/ibex_core.sv:1063`), LSU pmp_err path (`rtl/ibex_load_store_unit.sv:472-531`) | `+gen_chk_pmp_data=0` |
| `pmp_csr_warl` | pmpcfg/pmpaddr/mseccfg read-backs equal the model's legalized values (locked regions, TOR ordering, G masking, RLB/MML rules) | CSR write legalization in `rtl/ibex_cs_registers.sv` | `+gen_chk_pmp_csr_warl=0` |

## 6. Failure path and diagnostics

`uvm_error` per id with address, half, region, predicted vs observed.

## 7. Coverage hooks

`gen_pmp_cg`: mode x permission x privilege x access type, first/second-half faults, locked
regions, MML/MMWP/RLB states, DM-window exemption.

## 8. At build

Cross-check the per-half rules against rtl-arch BS MEM-13 on the first faulting waveforms.
