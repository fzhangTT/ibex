# Component API: gen_counter_model (mcycle, minstret, mhpmcounter3..12)

Owner: tb-infra. Status: PARTLY BUILT. Counters 7, 8, 9, 11 and 12 have rules in
`dv/auto_dv/env/gen_counter_model.sv`; `ctr_mcycle`, `ctr_minstret` and the rules for counters 3, 4, 5, 6
and 10 do not exist, and Section 9 lists what that leaves open. Source of the plan:
`dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C4.6; DV_prompt.txt deliverable 4 (TB
architecture document, component API documents). Conventions (shared by every component document): every
runtime knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its id (or
`uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker, `+gen_chk_all=0 +gen_chk_<id>=1`
isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Predicts the performance counters from the boundary: `mcycle` from cycles since reset release (no clock
gate: sleep cycles count) minus inhibited cycles plus software writes; `minstret` per rtl-arch CSR-20 (not
counted: ebreak, ecall, illegal, fetch fault, errored loads/stores, CSR writes to minstret(h); Zcmp counts
once; dummy instructions DO count); events 3..12 from RVFI and bus timing.

## 2. Files and how to call it

`dv/auto_dv/env/gen_counter_model.sv` (package `gen_counter_pkg`, class `gen_counter_model`), compiled
between `gen_checkers_pkg.sv` and `gen_env_pkg.sv` in `dv/auto_dv/tb/gen_tb.f`. `gen_env` creates it as
`env.ctr` and connects it to two ports: the RVFI monitor's record port (`rvfi_mon.ap`) and the data-bus
agent's completed-transaction port (`dbus_agent.ap`).

It subscribes to the RECORD port and not to the scoreboard's model-of-record port because that port is not
published for a folded Zcmp micro-op or for a draft-B op (`gen_rvfi_pkg.sv:385-392`, `:407-441`), and
because a second subscriber on the record port does not depend on whether the scoreboard has stepped the
model yet. It reads no ISA-model state and no internal DUT signal: every term comes from
`rvfi_ext_mhpmcounters`, the record fields, and the bus transactions' grant and response stamps.

Every rule judges the window between two ARCHITECTURAL READS of the counter, and that is the load-bearing
design decision. The event pulses of counters 7, 8 and 9 fire in the instruction's own ID cycles
(`rtl/ibex_id_stage.sv:928`, `:934`, `:941` into `rtl/ibex_controller.sv:681-687`) while
`rvfi_ext_mhpmcounters` is sampled at the record's ID exit (`rtl/ibex_core.sv:2108-2128`), so an instruction
that holds ID for one cycle does not see its own pulse and one that holds it longer does; a per-record delta
rule is therefore timing-fragile in exactly the cases the bug candidates live in. Both endpoints of a read
window are taken at the same point of the pipeline, so the asymmetry cancels: a csrr of counters 5..9
returns the register value in the cycle the csrr is in ID, older pulses having landed
(`dv/auto_dv/evidence/gen_hpm_event_defs.md` Section 1). The consequence to know when reading a coverage
report: THE CHECKER IS SILENT IN A TEST THAT NEVER READS A COUNTER. A program that reads a counter once
cannot be judged either; the reads must bracket the window and both must use a nonzero rd.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_chk_ctr_mcycle / _ctr_minstret / _ctr_hpm_exact / _ctr_hpm_bound` | `PLUSARG_CHK_*` | checker enables (the first two are declared and unbuilt) | 1 |
| `+gen_ctr_rtl_jumps_fencei` | `PLUSARG_CTR_RTL_JUMPS_FENCEI` | NumJumps counts fence.i as this RTL does; 0 = the documentation's rule | 1 |
| `+gen_ctr_rtl_taken_dit` | `PLUSARG_CTR_RTL_TAKEN_DIT` | NumBranchesTaken counts every conditional branch while data_ind_timing is set, as this RTL does; 0 = the documentation's rule | 1 |
| `+gen_ctr_rtl_branches_wait` | `PLUSARG_CTR_RTL_BRANCHES_WAIT` | NumBranches is bounded over a window that held a data access; 0 = the documentation's exact rule everywhere | 1 |
| `+gen_ctr_rtl_wait_cycles` | `PLUSARG_CTR_RTL_WAIT_CYCLES` | counters 11 and 12 keep only the one-per-cycle bound and the no-record-no-count rule; 0 = the documentation's bound | 1 |

The four direction knobs are ONE FAMILY WITH ONE SENSE: 1 follows the RTL and 0 follows the documentation,
on every one of them. That is the direction ruling in `gen_bug_log.md` Section 0.6 (the B13 convention
applied to the counter rules): the default follows the RTL so an ordinary run stays green, every
accommodation is counted per bug, the counts are reported at the end of every run, and the bug's
expected-fail test is the single run that sets its knob to 0. A run whose accommodation count is nonzero met
the candidate; a run whose count is zero did not exercise it. The report lines are `GEN_CTR` at
`UVM_LOW`: one with the window and miss counts, one with the per-bug accommodation counts, one echoing the
four knob values.

Two constants the bounds rest on, both in `gen_tb_knobs.yaml` with their RTL derivation:
`GEN_MUL_WAIT_MAX_CYCLES` = 1 (the fast multiplier runs MD_OP_MULL in one cycle and a high form as MULL then
MULH, `rtl/ibex_multdiv_fast.sv:139-232`) and `GEN_DIV_WAIT_MAX_CYCLES` = 36 (the divider FSM takes MD_IDLE,
MD_ABS_A, MD_ABS_B, 31 MD_COMP iterations, MD_LAST, MD_CHANGE_SIGN and MD_FINISH, `:91`, `:426-517`: 37
cycles of which the last retires; the zero-operand short circuit at `:434` only shortens it).

## 4. Wave-level behaviour

Exactness class per counter, AS BUILT:

| Counter | Class as built |
|---|---|
| 7 NumJumps | exact over a read window, in both knob positions |
| 8 NumBranches | exact over a read window with no load or store record in it; bounded otherwise under the default knob, exact everywhere with the knob at 0 |
| 9 NumBranchesTaken | exact over a read window, in both knob positions |
| 11 NumCyclesMulWait | bounded over a read window |
| 12 NumCyclesDivWait | bounded over a read window |
| mcycle, minstret, 3, 4, 5, 6, 10 | NOT BUILT (Section 9) |

Every upper bound carries `GEN_RVFI_ID_EXIT_OFFSET` cycles of slack, because both anchors are CSR-read
records whose distance from their own ID exit carries no memory wait but need not be identical.

A window is left UNJUDGED, and counted as such in the report, when a write to the counter or its high half
fell inside it, or when the counter's `mcountinhibit` bit was set at any record inside it. `mcountinhibit`
and `cpuctrlsts` are shadowed from the record stream by the architectural write rule (rw takes the operand,
set ORs it, clear ANDs its complement, the operand being the uimm for the immediate forms), the pattern
`gen_fcov_pkg.sv:2153-2166` already uses for `cpuctrlsts`; `mcountinhibit` resets to 0
(`rtl/ibex_cs_registers.sv:1725`). At `MHPMCounterWidth` 32, which is what the opentitan build compiles
(`ibex_configs.yaml`, `gen_param_resolution.md:45`), the h aliases read 0 and a counter wrap is the same
32-bit subtraction, so no wrap case is special.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `ctr_mcycle` | NOT BUILT. Planned: `rvfi_ext_mcycle` equals the model's mcycle at `record_cycle - GEN_RVFI_ID_EXIT_OFFSET` (sampled at ID exit, rtl/ibex_core.sv:2102); class windowed(`GEN_RVFI_ID_EXIT_OFFSET`); mcycle(h) read-backs use the same offset | counter primitive (`rtl/ibex_counter.sv`), inhibit gating | `+gen_chk_ctr_mcycle=0` |
| `ctr_minstret` | NOT BUILT as a checker. The shim's minstret proxy models the quantity on the ISA side (T-235, `gen_component_api_isa_shim.md`), so a minstret divergence appears as an `isa_rd` miss on the program's own read | perf_instr_ret (`rtl/ibex_wb_stage.sv:206-210`), `incr[2]` (`rtl/ibex_cs_registers.sv:1588`) | `+gen_chk_ctr_minstret=0` |
| `ctr_hpm_exact` | Counter 7: the read difference equals the records strictly between the two reads that are JAL or JALR in either encoding with trap 0, plus fence.i under `ctr_rtl_jumps_fencei`. Counter 8: one per conditional-branch record with trap 0. Counter 9: one per conditional-branch record whose `pc_wdata` is not `pc_rdata + insn length`, plus every not-taken conditional branch while data_ind_timing is set under `ctr_rtl_taken_dit`. A window holding a memory-access trap is bounded instead, because a jump behind an outstanding write-back access pulses speculatively and pulses again after the handler (`gen_hpm_event_defs.md` Section 2, the second corner of events 7 and 9) | the event ORs in the id and wb stages, the decoder's jump and branch decode, the `branch_jump_set_done_q` dedup | `+gen_chk_ctr_hpm_exact=0` |
| `ctr_hpm_bound` | Every counter: the read difference is at most the window's cycles, since a counter moves by at most one per cycle (`rtl/ibex_cs_registers.sv:1585-1598`); this one test also catches a decrease, which a 32-bit subtraction reports as a large difference. Counters 11 and 12: a window with no multiply (respectively divide) record and no dummy instructions must not move the counter at all; a window with such a record moves it by at most the tighter of the instruction's own latency ceiling and the window's cycles in which no data access was outstanding, under `ctr_rtl_wait_cycles` | inhibit and event wiring, the multdiv stall terms | `+gen_chk_ctr_hpm_bound=0` |

## 6. Failure path and diagnostics

`uvm_error` per id. Every message names the counter by its architectural number, the observed difference,
what was predicted or the bound and its terms, the two read values, the window's cycle range and the closing
record's order, so the failing window is locatable from the line alone.

## 7. Coverage hooks

`gen_counter_cg` (inhibit states, software writes, wrap of the 32-bit counters, event mixes) is NOT BUILT.

## 8. Unit test

`dv/auto_dv/gen_tb/gen_tests/gen_ut_counters.py` runs a program that reads a counter at both ends of a
window and reads the program's own measured differences back from memory through MEM_PEEK
(`+gen_ut_ctr_delta_sym`, `+gen_ut_ctr_delta_expect`, the latter a comma-separated list of values or `lo:hi`
ranges). That read-back is the fire-check: it proves the program met the counter behaviour under test, so a
green counter checker in the same run judged that behaviour rather than nothing. The module does not repeat
the rules' judgement and does not require the program's end-of-test code to be the pass value, because a bug
reproducer stores a failing code by design; it requires only that the program reached its store.

## 9. What is NOT built, and what that leaves open

- `ctr_mcycle` and `ctr_minstret` as checkers.
- Exact rules for counters 5 (NumLoads), 6 (NumStores) and 10 (NumInstrRetC), which
  `gen_hpm_event_defs.md` Section 2 gives RVFI-visible rules for. Counters 5 and 6 carry the D6 deviation (a
  misaligned access is one pulse where the documentation says two) and counter 10 carries the write-back
  read-forwarding wrinkle of that document's Section 1.
- Bound rules for counters 3 (NumCyclesLSU) and 4 (NumCyclesIF).
- `gen_counter_cg` (Section 7).
- The always-on floor: because every rule is anchored on an architectural read, a test that never reads a
  performance counter is not judged at all. A per-record floor would need the sample-point asymmetry of
  Section 2 modelled, which is why it is not here.
