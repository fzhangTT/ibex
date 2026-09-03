# Component API: gen_irq_checker (interrupt and NMI entry)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C4.4; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Predicts interrupt and NMI entry from the driven pins, the modelled `mie`/`mstatus`/priv state
and debug/NMI mode; checks `irq_pending_o` every cycle under the settle-window rule (class windowed, v2 XM-M5) and the entry vector, cause and timing on
the RVFI stream; checks the internal NMI from injected LSU integrity errors.

## 2. Files (planned) and how to call it

`dv/auto_dv/env/gen_irq_checker.sv` (scoreboard sub-checker); inputs: gen_irq_agent `ap` (pin
edges with cycles), the CSR model, the RVFI records and irq notifications, the dbus monitor's
injected-integrity events.

Called by the scoreboard per RVFI event and per cycle for `irq_pending_o`.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_chk_irq_pending / _irq_entry / _irq_masked / _nmi_entry / _nmi_internal` | `PLUSARG_CHK_*` | checker enables | 1 |
| `+gen_irq_entry_bound=<records>` | `PLUSARG_IRQ_ENTRY_BOUND` | override of `GEN_IRQ_ENTRY_BOUND_RECORDS` | gen_tb_pkg constant |

## 4. Wave-level behaviour

`irq_pending_o = |(pins & mie_q)` is combinational (rtl-arch CTRL-07), and `mie_q` is written when
the CSR instruction executes in ID/EX, at least two cycles before its RVFI record, so the compare
is class windowed (v2, XM-M5): a settle window of `GEN_CSR_COMMIT_TO_RVFI_OFFSET` cycles opens at
each retired `mie` write record, the compare is suspended inside it and re-armed with the new
value; pin edges need no window (pins are visible). Entry checks: vector = mtvec base + 4 * cause
(vectored mode is fixed), cause per Ibex's priority (NMI > fast lowest id > ext > sw > timer),
mepc = pc of the first un-retired instruction, taken within `GEN_IRQ_ENTRY_BOUND_RECORDS`
records (class bound).

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `irq_pending` | `irq_pending_o == |({sw, timer, ext, fast[14:0]} & mie_q)` every cycle, not gated by MIE/debug/nmi; class windowed(`GEN_CSR_COMMIT_TO_RVFI_OFFSET`): the RTL commits `mie_q` at the CSR-write commit edge while the RVFI record follows WB, so the compare uses the value committed by the record `GEN_CSR_COMMIT_TO_RVFI_OFFSET` cycles later (measured in bring-up, pinned by a directed `csrw mie` test) | `irqs_o`/`irq_pending_o` (`rtl/ibex_cs_registers.sv:1044-1045`), mip wiring (`:408-412`) | `+gen_chk_irq_pending=0` |
| `irq_entry` | when enable conditions hold and a line is pending, the next RVFI event is an interrupt entry (`rvfi_ext_irq_valid` or a record with `rvfi_intr`, `pc_rdata == mtvec_base + 4*id`, id = highest priority pending: NMI > fast lowest-id > ext > sw > timer) within `GEN_IRQ_ENTRY_BOUND_RECORDS`; `pre_mip` of that record contains the taken id | controller handle_irq / IRQ_TAKEN (`rtl/ibex_controller.sv:498-511, 725-758`), priority select | `+gen_chk_irq_entry=0` |
| `irq_masked` | no interrupt entry while `mstatus.MIE == 0` in M-mode, in debug mode, or during NMI handling; an unsampled one-cycle pulse produces no entry | same | `+gen_chk_irq_masked=0` |
| `nmi_entry` | `irq_nm_i` => entry within bound regardless of MIE/mie, `mcause == 0x8000001F`, `pc_rdata == mtvec_base + 0x7C`, nested NMI ignored; `mret` restores mstatus.MPP/MPIE, mepc, mcause from the mstack model | NMI path (`rtl/ibex_controller.sv:736-745`), mstack (`rtl/ibex_cs_registers.sv`) | `+gen_chk_nmi_entry=0` |
| `nmi_internal` | injected LSU response integrity error => `alert_major_bus_o`, `rvfi_ext_rf_wr_suppress` on the load, internal NMI with `mcause 0xFFFFFFE0` and `mtval` = faulting address, at most one instruction later; fetch-side integrity errors raise no NMI | mem_resp_intg_err path (`rtl/ibex_controller.sv:436-438`) | `+gen_chk_nmi_internal=0` |

## 6. Failure path and diagnostics

`uvm_error` per id; the bound constant is measured in bring-up (longest instruction: 37-cycle
divide plus split access plus bus latency).

## 7. Coverage hooks

`gen_irq_cg` crosses (pending set x enable state x pipeline state), NMI in handler, entry
latency bins.

## 8. At build

Measure `GEN_IRQ_ENTRY_BOUND_RECORDS`; confirm F-RVFI-032 handling of `pre_mip` on colliding
records.
