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
drives the ISA-model comparator (gen_isa_shim) per record. AS BUILT (step 2a, ISA comparator only): `gen_rvfi_pkg::gen_scoreboard`, a `uvm_subscriber` on the RVFI monitor. `start_of_simulation_phase` builds the model through `gen_isa_dpi_pkg` (`gen_isa_reset_dpi` with boot_addr, the `+gen_isa_string` override, `+gen_isa_log`, `knob_mcounteren_writable`; `uvm_fatal ISA_INIT` on failure) and loads the same image (`gen_isa_load_vmem`, word count checked against the sidecar). Per record: Zcmp micro-op records fold to the last record: pc of the first record and the 16-bit `rvfi_ext_expanded_insn` are compared, then the UNION of the sequence's GPR writes (set of rd/value pairs over all micro-op records) is compared with the model step's logged register writes (`gen_isa_reg_write`) and the ORDERED store list (address/data) with the model's logged data writes (`gen_isa_mem_write`); ids isa_rd and isa_mem. A draft-B op (`gen_isa_is_draft_b`) is checked against the MODEL: pc_rdata against `gen_isa_get_pc`, insn against `gen_isa_fetch_insn(model pc)`, rs1/rs2 operands read from the model GPRs (`gen_isa_read_gpr` at the register indices decoded from the instruction) and compared with the DUT's rs1_rdata/rs2_rdata (id isa_rd), rd from `gen_isa_exec_reference` on the model operands compared with rd_wdata (isa_rd), next pc = model pc + 4 compared with pc_wdata (isa_pc_next); then rd and pc are written into the model. Unexercised so far (draft_b=0 in both retained programs); the model's minstret does not advance on a draft-B op (known limitation until the counter model lands). `rvfi_intr` records take an entry step first (arm `pre_mip`, expect retired 0 and an interrupt cause, vector == pc_rdata); a first debug-mode record at DmHaltAddr takes an entry step with `debug_req`; then one `gen_isa_step_dpi` per record and the field compares isa_pc, isa_insn, isa_trap (retired 0 with a trap, or retired 1 without), isa_rd (rd address/value, `rf_wr_suppress` honoured), isa_mem (access present, address, full-word store data; a DUT read is inferred from the model's access because `rvfi_mem_rmask` is asserted on every non-store record, rtl/ibex_core.sv:2085, an RVFI-port observation counted as `rvfi_rmask_on_nonload` and reported to rtl-arch), isa_pc_next (not on trap records), isa_prv; each mismatch is `uvm_error <id>` when `+gen_chk_isa` and the field knob allow (isolation `+gen_chk_all=0 +gen_chk_isa_<f>=1` uses the rendered `_set` flags) and counts into the bridge fields `evt_isa_records` / `evt_isa_mismatch`; `+gen_sb_trace=1` prints model and DUT per record. Consumed-records rule as built: `evt_isa_records` counts every RVFI record once (compared or folded); with the model on it equals the retirement count exactly, and gen_ut_lockstep asserts equality. Counters, PMP, CSR observability and the irq/debug/misc sub-checkers are later landings.

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
| `+gen_chk_isa=0|1` | `PLUSARG_CHK_ISA` | silences every isa_* row (the model still steps and publishes its state in every run, since the irq/debug/misc checkers consume it: step 2b, T-090); per-field knobs +gen_chk_isa_{pc,insn,trap,rd,mem,prv,pc_next,csr} | 1 |
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
| `isa_prv` | the model's privilege BEFORE the step (`prv_before`) == `rvfi_mode`: rvfi_mode is the mode the instruction executed in, so the post-step privilege is not compared (T-102; the pre-T-102 compare fired on every mret and every U-mode trap) | privilege update on trap/mret (`rtl/ibex_cs_registers.sv:953-993`) | `+gen_chk_isa_prv=0` |
| `isa_pc_next` | model pc after the step == `rvfi_pc_wdata`; on trap, mret and dret records the expectation is `pc_rdata + instruction length` instead (plan C-1 / F-RVFI-010, rtl-arch R1: pc_if, 2 for a compressed encoding; a fetch fault, cause 1, has no length and is not compared), and the redirect target is checked by `isa_pc` on the following record (model pc versus its `pc_rdata`) | pc increment / redirect (`rtl/ibex_if_stage.sv`) | `+gen_chk_isa_pc_next=0` |
| `isa_csr` | every model CSR write (commit log type 4) == the legalized expectation (C5.3a) or the SPEC value (C5.3b rows); read-backs per C6 | CSR legalization and read mux (`rtl/ibex_cs_registers.sv`) | `+gen_chk_isa_csr=0` |

Model synchronisation before every record step (T-102): the scoreboard hands the record's sampled values to the model
before stepping it, `gen_isa_set_time(t.ext_mcycle)`, `gen_isa_set_hpm(k, ...)` for the `GEN_MHPM_COUNTER_NUM` counter
pairs and `gen_isa_set_status(t.ext_ic_scr_key_valid)`. RVFI samples these when the instruction leaves ID
(rtl/ibex_core.sv:2102-2120), the cycle in which a CSR read of `cycle`, `mhpmcounterN` or `cpuctrlsts` takes its value,
so the model's read equals the DUT's exactly; the monitor therefore samples the counter words on every record.
These reads under `isa_rd` are CONSISTENCY compares (record value == read value), not independent checks of the DUT
(Critic T-102 M-1): mcycle, minstret and the HPM counters belong to the counter checkers `ctr_mcycle`, `ctr_minstret`,
`ctr_hpm_exact` and `ctr_hpm_bound` (step 2d, not built at 4c4b9b8), and cpuctrlsts bit 8 to the scramble-key
responder's `scrkey_proto` status row (record bit 8 versus the driven value at the ID-exit sample, not built); until
those land, a csrr of these CSRs passing `isa_rd` says nothing about counter or status correctness. The cpuctrlsts bits
6 and 7 (sync_exc_seen, double_fault_seen) are hardware-set in the DUT and the shim sets them from the model's own trap
history (rtl/ibex_cs_registers.sv:935-943, :964-965), so a read of them is an independent compare. Draft-B
records (C5.5): the R4 forms (cmov, cmix, fsl, fsr, fsri) read rs3 = insn[31:27] from the model's register file; the
record's `rvfi_rs3_addr/rdata` are compared with it under `isa_rd` and the value feeds the reference.

Asynchronous entries (step 2b, T-090, found on the first interrupt-enabled and debug-storm programs): on a record with
`rvfi_intr` the model is offered exactly the interrupt the DUT's vector names (handler pc = mtvec base + 4 * cause, from
the record's pre_mip), so lines raised between the DUT's decision and the record cannot divert the model; Spike still
refuses an entry that is not pending and enabled (isa_trap), and the priority among simultaneously pending lines is a
boundary rule for the irq checker (not built yet). On an ordinary record the pending bits that are ENABLED (M-mode with
MIE, or U-mode) are withheld from the model, because the DUT retired that instruction before taking them and Spike would
take them first; disabled pending bits are injected so a mip read compares. A debug request held through dret re-enters
debug on the very next record: the entry rule is `pc_rdata == DmHaltAddr` with `ext_debug_mode` and either the previous
record outside debug mode or the previous record a dret.

Model-state publication (step 2b, T-090): after every compared record the scoreboard publishes one `gen_model_state`
on `ap_state` (order, cycle, model pc after the step, insn, mie / mstatus / mcause / mepc / mtval / dcsr read from the
model, privilege after the record, trap / interrupt / mret / dret / debug flags, and whether the record wrote mie or
mstatus); `gen_irq_checker`, `gen_dbg_checker` and `gen_misc_monitor` consume it and never read the shim directly.

### 5a. Mutation classes per id

The locus column above names example RTL sites; this table names the class of DUT defect each id catches
and the knob forms. Isolation: `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_<id>=1`.

| Id | DUT defect class it catches | Disable knob | Isolation form |
|---|---|---|---|
| `isa_pc` | wrong fetch pc | `+gen_chk_isa_pc=0` | `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_pc=1` |
| `isa_insn` | wrong instruction fetched or expanded | `+gen_chk_isa_insn=0` | `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_insn=1` |
| `isa_trap` | spurious or missing trap or interrupt entry | `+gen_chk_isa_trap=0` | `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_trap=1` |
| `isa_rd` | wrong register result or missing writeback | `+gen_chk_isa_rd=0` | `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_rd=1` |
| `isa_mem` | wrong store address or data, or a phantom or missing access | `+gen_chk_isa_mem=0` | `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_mem=1` |
| `isa_prv` | wrong privilege after mret or trap | `+gen_chk_isa_prv=0` | `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_prv=1` |
| `isa_pc_next` | wrong next pc on branch, jump, trap or mret | `+gen_chk_isa_pc_next=0` | `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_pc_next=1` |

Proof status per id (Critic ruling D-3, dv/auto_dv/docs/gen_critic_tb_t068.md): the TB-side half of trust triad
rule 2 is done for isa_rd, isa_mem, isa_trap and isa_pc_next (MUT-004..008 in dv/auto_dv/mutations/gen_mut_isa_fields.md:
the named id fires alone, its knob silences exactly it, the flow collects the failure); the RTL-level half (a
mutation of the DUT per id, caught by the named id with hidden referees inert, Test Writer purpose-2 runs) is
OWED for every id before any isa_* id counts as mutation-proof in a measured regression. isa_pc and isa_insn have
only the forced-red evidence (a model perturbation, not per-field); isa_prv has never fired; their per-field
proofs are owed with the first U-mode program. Status words per id: isa_pc TB-side partial (forced red) / RTL owed;
isa_insn TB-side partial / RTL owed; isa_trap TB-side done / RTL owed; isa_rd TB-side done (incl. port-level
MUT-008) / RTL owed; isa_mem TB-side done / RTL owed; isa_prv TB-side done (T-102 P1, gen_mut_t102.md) / RTL owed;
isa_pc_next TB-side done (MUT-008, T-102 P2 and P11) / RTL owed; the mret/dret target check under isa_pc has its own
mutation (T-102 P10, the record after an mret reported with pc + 4).

## 6. Failure path and diagnostics

`uvm_error` with id, record order, pc, expected-versus-actual; `uvm_fatal SB_DESYNC` when the
model and DUT pcs diverge for more than `GEN_SB_DESYNC_RECORDS` records (further compares are
meaningless).

## 7. Coverage hooks

Two-source crosses (interrupt vs outstanding bus response, PMP fault vs regime, ...) sampled here.

## 8. At build

Define `GEN_SB_DESYNC_RECORDS`; implement the association queue and prove it on the first
programs.
