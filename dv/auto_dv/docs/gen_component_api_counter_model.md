# Component API: gen_counter_model (mcycle, minstret, mhpmcounter3..12)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C4.6; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Predicts the performance counters from the boundary: `mcycle` from cycles since reset release
(no clock gate: sleep cycles count) minus inhibited cycles plus software writes; `minstret` per
rtl-arch CSR-20 (not counted: ebreak, ecall, illegal, fetch fault, errored loads/stores, CSR writes
to minstret(h); Zcmp counts once; dummy instructions DO count); events 3..12 from RVFI and bus
timing.

## 2. Files (planned) and how to call it

`dv/auto_dv/env/gen_counter_model.sv` (scoreboard sub-model); compared against
`rvfi_ext_mcycle`, `rvfi_ext_mhpmcounters[*]` and CSR read-backs.

Updated by the scoreboard per cycle (mcycle) and per record (events); the ISS is never the
reference for counters (CPI = 1 model, const-0 hpm counters).

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_chk_ctr_mcycle / _ctr_minstret / _ctr_hpm_exact / _ctr_hpm_bound` | `PLUSARG_CHK_*` | checker enables | 1 |
| `+gen_ctr_dummy_mode=exact|ge` | `PLUSARG_CTR_DUMMY_MODE` | with dummies enabled: `exact` needs probe P1, `ge` checks >= | ge |

## 4. Wave-level behaviour

Exactness class per counter: mcycle exact; minstret exact with dummies off (else `>=` or P1);
counters 5..10 (loads, stores, jumps, branches, taken, compressed retired) exact; counters 3, 4,
11, 12 (LSU-cycle, IF-wait, mul wait, div wait) checked as bounds and monotonic unless a boundary
model exists.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `ctr_mcycle` | `rvfi_ext_mcycle` equals the model's mcycle at `record_cycle - GEN_RVFI_ID_EXIT_OFFSET` (sampled at ID exit, rtl/ibex_core.sv:2102); class windowed(`GEN_RVFI_ID_EXIT_OFFSET`); mcycle(h) read-backs use the same offset | counter primitive (`rtl/ibex_counter.sv`), inhibit gating | `+gen_chk_ctr_mcycle=0` |
| `ctr_minstret` | exact with dummies off; `>=` with dummies on unless P1 | perf_instr_ret (`rtl/ibex_wb_stage.sv:206-210`), `incr[2]` (`rtl/ibex_cs_registers.sv:1588`) | `+gen_chk_ctr_minstret=0` |
| `ctr_hpm_exact` | counters 5..10 exact | event ORs in id/wb stage | `+gen_chk_ctr_hpm_exact=0` |
| `ctr_hpm_bound` | counters 3, 4, 11, 12 within `[0, cycles elapsed]` and monotonic; `mcountinhibit` stops them | inhibit/event wiring | `+gen_chk_ctr_hpm_bound=0` |

## 6. Failure path and diagnostics

`uvm_error` per id with counter index, expected-versus-actual.

## 7. Coverage hooks

`gen_counter_cg`: inhibit states, software writes, wrap of 32-bit counters (MHPMCounterWidth =
32), event mixes.

## 8. At build

Decide whether cycle-class events get a boundary model; state each counter's class in this
document when built.
