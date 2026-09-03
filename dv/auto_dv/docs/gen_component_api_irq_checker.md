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
the RVFI stream; checks the internal NMI from injected LSU integrity errors. AS BUILT (step 2b, T-090, entry and pending
rules): `gen_checkers_pkg::gen_irq_checker` consumes the scoreboard's `gen_model_state` (mie / mstatus / mcause / prv /
debug per record, published after every compared record) and the driver's `gen_irq_evt`: `irq_pending` (every cycle,
evaluated GEN_CSR_WRITE_TO_RVFI_OFFSET + 1 cycles later against the driven pins and the model's mie history),
`irq_entry` / `nmi_entry` (a raised, enabled line not taken within GEN_IRQ_ENTRY_BOUND_RECORDS records), `irq_masked`
(an interrupt entry while M-mode with MIE clear); `nmi_internal` is not built.

Cause rule (T-136, ids `irq_entry` / `nmi_entry`, built after the first storm program showed the model following the
DUT's vector): on EVERY intr record, independent of open expectations, the taken cause must be an interrupt line that
was pending-and-enabled at the DUT's decision and the highest-priority such line (NMI, then the lowest fast id, then
external, software, timer: rtl/ibex_controller.sv:736-757, gen_mfip_id). The decision lies between the previous
record's `post_mip` and the entry record's `pre_mip` (rtl-arch gen_t090_rtl_facts.md Section 2), so two sets are
formed from the model state and the driver's events: pending-and-enabled EITHER = (previous post_mip | entry pre_mip |
lines the driver raised in between) & mie, and pending THROUGHOUT = previous post_mip & entry pre_mip & mie minus every
line the driver moved (raised or released) in between, whose level at the decision is unknown. The taken line must be
in EITHER (`taken line was not pending-and-enabled`); a line in THROUGHOUT of higher rank is an error (`line N pending
throughout outranks it`); an NMI pending in both samples and untouched by the driver outranks every line. The taken
cause is the one the DUT's vector names (`entry_cause` in the model state, 31 = NMI), never the model's mcause, which is
stale when the model did not take the entry (the shim has no NMI emulation). An NMI-vector entry needs a pending NMI pin
in either sample or a driver raise (the record's own `rvfi_ext_nmi_int` level is the DUT's self-report and counts for
nothing); without one it is accepted and counted as an internal NMI only when gen_bus_driver announced a data-side
integrity corruption since the last such entry consumed it (`gen_bus_err_log::intg_announced`), which mirrors the DUT's
single pending bit (rtl/ibex_controller.sv:391-430: set by any data-response integrity error, cleared by an NMI entry taken
without an external NMI, never taken inside NMI mode, so a corruption anywhere in the 82-record riscv-dv NMI handler is
taken right after its mret); `nmi ... (internal N, accepted on announced corruptions)` in the report. Otherwise it is a
phantom NMI (`NMI entry without a pending NMI pin or an injected integrity error since the last NMI entry`). Announcements
up to the previous record are consumed by an accepted entry, so a corruption landing between that record and the entry
record may justify the following entry (a few-cycle acceptance window, stated). The one-instruction latency and the
mcause 0xFFFFFFE0 / mtval read-back are the not-yet-built `nmi_internal` rule's. A line raised between the previous record's sample and the
decision is therefore accepted through the driver's event (the Critic's T-090 Section 6 question). Entries whose
priority claim could not be decided because a candidate line moved inside the window are counted (`priority
undecidable` in the GEN_IRQ_CHK report) instead of errored, so the frequency of the approximation is evidence. The entry
then clears only the expectations that named the taken line (or the NMI) and restarts the bound of the others (a
lower-priority line legitimately waits while higher ones keep being taken; the priority rule judges each entry, the bound
measures the quiet time after the last entry), and a driver release voids the expectation of the released line
(`expectations released`): a pulse the DUT never sampled owes no entry.

`nmi_internal` (landing 2a): an announced data-side integrity corruption (gen_bus_driver, `gen_bus_err_log::note_intg(addr)`)
must produce the internal NMI entry within `GEN_NMI_INT_ENTRY_BOUND_RECORDS` (yaml constant, 4; observed 2-3) records spent
outside NMI mode; NMI mode runs from an NMI-vector entry to the executed mret that closes it (nested traps inside it counted
by depth, rtl/ibex_controller.sv:391-430, :958-960). The entry's legitimacy is the acceptance rule above; its mcause
(0xFFFFFFE0) and mtval (the address of the corruption that set the DUT's pending bit, `take_intg()`) are compared by the
model, which emulates the NMI entry (gen_component_api_isa_shim.md). Mutant MB12 (a corruption announced but not injected)
fires the bound; the integrity run with every checker on (gen_fu_l2_intg_s7_allchk_*) shows 54 internal NMIs accepted, 0
cause mismatches, 0 bound failures. Mutation MB5 (the entry
record's vector shifted by one cause) is caught by this rule with the referees inert (gen_mut_step2b.md).

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
is class windowed (v2, XM-M5): a settle window of `GEN_CSR_WRITE_TO_RVFI_OFFSET` cycles opens at
each retired `mie` write record, the compare is suspended inside it and re-armed with the new
value; pin edges need no window (pins are visible). Entry checks: vector = mtvec base + 4 * cause
(vectored mode is fixed), cause per Ibex's priority (NMI > fast lowest id > ext > sw > timer),
mepc = pc of the first un-retired instruction, taken within `GEN_IRQ_ENTRY_BOUND_RECORDS`
records (class bound).

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `irq_pending` | `irq_pending_o == |({sw, timer, ext, fast[14:0]} & mie_q)` every cycle, not gated by MIE/debug/nmi; class windowed(`GEN_CSR_WRITE_TO_RVFI_OFFSET`): the RTL commits `mie_q` at the CSR-write commit edge while the RVFI record follows WB, so the compare uses the value committed by the record `GEN_CSR_WRITE_TO_RVFI_OFFSET` cycles later (measured in bring-up, pinned by a directed `csrw mie` test) | `irqs_o`/`irq_pending_o` (`rtl/ibex_cs_registers.sv:1044-1045`), mip wiring (`:408-412`) | `+gen_chk_irq_pending=0` |
| `irq_entry` | (bound) a raised, enabled line is taken within `GEN_IRQ_ENTRY_BOUND_RECORDS` records unless the driver released it first; (cause, T-136) every intr record's cause is a line pending-and-enabled at the decision and the highest-priority line pending throughout (Section 1); an entry clears only the expectations naming its line | controller handle_irq / IRQ_TAKEN (`rtl/ibex_controller.sv:498-511, 725-758`), priority select | `+gen_chk_irq_entry=0` |
| `irq_masked` | no interrupt entry while `mstatus.MIE == 0` in M-mode, in debug mode, or during NMI handling; an unsampled one-cycle pulse produces no entry | same | `+gen_chk_irq_masked=0` |
| `nmi_entry` | `irq_nm_i` => entry within bound regardless of MIE/mie, `mcause == 0x8000001F`, `pc_rdata == mtvec_base + 0x7C`, nested NMI ignored; `mret` restores mstatus.MPP/MPIE, mepc, mcause from the mstack model | NMI path (`rtl/ibex_controller.sv:736-745`), mstack (`rtl/ibex_cs_registers.sv`) | `+gen_chk_nmi_entry=0` |
| `nmi_internal` | injected LSU response integrity error => `alert_major_bus_o`, `rvfi_ext_rf_wr_suppress` on the load, internal NMI with `mcause 0xFFFFFFE0` and `mtval` = faulting address, at most one instruction later; fetch-side integrity errors raise no NMI | mem_resp_intg_err path (`rtl/ibex_controller.sv:436-438`) | `+gen_chk_nmi_internal=0` |

### 5a. Owed items of the irq / debug / misc boundary rules (Critic T-090 Section 1 item 2), status at this landing

| Item | Status | Where |
|---|---|---|
| (i) the taken line was pending and enabled at the DUT's decision | BUILT (T-136, EITHER set) | `check_entry_cause`, MB5 |
| (ii) the taken line was the highest-priority pending line | BUILT (T-136, THROUGHOUT set; undecidable entries counted) | `check_entry_cause` |
| (iii) `nmi_internal` | BUILT (landing 2a: legitimacy on an announced corruption, latency bound outside NMI mode; mcause / mtval through the model's NMI emulation) | `check_entry_cause`, write_state; MB12 |
| (iv) reds for `irq_masked` / `dbg_masked` | NOT BUILT | need a program masking MIE / entering debug with a line pending |
| (v) dbg checker `dbg_exc` / `dbg_dret` / `dbg_trigger` | NOT BUILT | need the C6 CSR read-back records |
| misc `crash_dump`, `core_busy`, `fetch_en` | NOT BUILT | misc monitor |
| `alert_minor` missing-pulse half | NOT BUILT | needs the icache ECC injection hook |
| never-high rules `alert_internal`, `data_tag_quiet`, `alert_minor`, `double_fault` | MUTATION-PROOF (MB8..MB11, this landing) | gen_mut_step2b.md |
| `irq_pending`, `irq_entry` (bound and cause), `dbg_entry`, `alert_bus` | MUTATION-PROOF (MB4, MB1 + MB5, MB2, MB3) | gen_mut_step2b.md |
| `irq_masked`, `dbg_masked`, `nmi_entry` | declared, not trusted (no red) | programs owed |

## 6. Failure path and diagnostics

`uvm_error` per id; the bound constant is measured in bring-up (longest instruction: 37-cycle
divide plus split access plus bus latency).

## 7. Coverage hooks

`gen_irq_cg` crosses (pending set x enable state x pipeline state), NMI in handler, entry
latency bins.

## 8. At build

Measure `GEN_IRQ_ENTRY_BOUND_RECORDS`; confirm F-RVFI-032 handling of `pre_mip` on colliding
records.
