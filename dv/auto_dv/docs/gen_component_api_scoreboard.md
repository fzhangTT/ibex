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
| `+gen_isa_pc_next_mask_b13=0|1` | `PLUSARG_ISA_PC_NEXT_MASK_B13` | 1 = `isa_pc_next` masks bit 0 of `rvfi_pc_wdata` on jalr / c.jr / c.jalr records and counts them (`b13_odd_jalr`, rtl-arch R11); 0 = the raw RVFI rule, for the expected-fail test of bug candidate B13 | 1 |

## 4. Wave-level behaviour

Stores and loads retire after their bus response (WB stage waits for it), so bus-to-record
association is by order with the response preceding the record.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `isa_pc` | model pc before the step == `rvfi_pc_rdata` (exact per record) | fetch/branch target: `rtl/ibex_if_stage.sv` pc mux, `rtl/ibex_ex_block.sv` branch target ALU | `+gen_chk_isa_pc=0` |
| `isa_insn` | model instruction bits == `rvfi_insn` | compressed decoder expansion (`rtl/ibex_compressed_decoder.sv`), fetch data path | `+gen_chk_isa_insn=0` |
| `isa_trap` | model trap <=> `rvfi_trap`; cause per handler read-back; on a breakpoint record (cause 3) the model's mepc == pc and mtval == 0 (R10); a load/store trap in either encoding (`gen_insn_mem_access`: 32-bit, c.lw/c.sw/c.lwsp/c.swsp, Zcb) arms the model's fault only for a driver-announced bus error, with the DUT's mtval (the failing transaction's address; T-137, landing 1c) | controller exception cause select (`rtl/ibex_controller.sv:299-337, 900-927`), decoder illegal detection | `+gen_chk_isa_trap=0` |
| `isa_rd` | GPR write (index, value) == `rvfi_rd_addr/rd_wdata` | ALU operator select (`rtl/ibex_alu.sv`), multiplier/divider (`rtl/ibex_multdiv_fast.sv`), decoder rd/we (`rtl/ibex_decoder.sv`), WB mux (`rtl/ibex_wb_stage.sv`) | `+gen_chk_isa_rd=0` |
| `isa_mem` | memory access address, size, store data == `rvfi_mem_*` | LSU address/data rotation and byte enables (`rtl/ibex_load_store_unit.sv:138-221`) | `+gen_chk_isa_mem=0` |
| `isa_prv` | the model's privilege BEFORE the step (`prv_before`) == `rvfi_mode`: rvfi_mode is the mode the instruction executed in, so the post-step privilege is not compared (T-102; the pre-T-102 compare fired on every mret and every U-mode trap) | privilege update on trap/mret (`rtl/ibex_cs_registers.sv:953-993`) | `+gen_chk_isa_prv=0` |
| `isa_pc_next` | model pc after the step == `rvfi_pc_wdata`; on trap, mret and dret records the expectation is `pc_rdata + instruction length` instead (plan C-1 / F-RVFI-010, rtl-arch R1: pc_if, 2 for a compressed encoding; a fetch fault, cause 1, has no length and is not compared), and the redirect target is checked by `isa_pc` on the following record (model pc versus its `pc_rdata`); on jalr / c.jr / c.jalr records bit 0 of `rvfi_pc_wdata` is masked and counted (B13, rtl-arch R11) | pc increment / redirect (`rtl/ibex_if_stage.sv`) | `+gen_chk_isa_pc_next=0` |
| `isa_csr` | every model CSR write (commit log type 4) == the legalized expectation (C5.3a) or the SPEC value (C5.3b rows); read-backs per C6 | CSR legalization and read mux (`rtl/ibex_cs_registers.sv`) | `+gen_chk_isa_csr=0` |

Model synchronisation before every record step (T-102): the scoreboard hands the record's sampled values to the model
before stepping it, `gen_isa_set_time(t.ext_mcycle)`, `gen_isa_set_hpm(k, ...)` for the `GEN_MHPM_COUNTER_NUM` counter
pairs and `gen_isa_set_status(t.ext_ic_scr_key_valid)`. RVFI samples these when the instruction leaves ID
(rtl/ibex_core.sv:2102-2120), the cycle in which a CSR read of `cycle`, `mhpmcounterN` or `cpuctrlsts` takes its value,
so the model's read equals the DUT's exactly; the monitor therefore samples the counter words on every record.
These reads under `isa_rd` are CONSISTENCY compares (record value == read value), not independent checks of the DUT
(Critic T-102 M-1): mcycle and the HPM counters (record-synced) belong to the counter checkers; minstret / instret are the exception since T-235: the model computes them itself (Ibex's inhibit and write rules in gen_component_api_isa_shim.md, fed the retirement gap of every record through `gen_isa_set_retire_gap`), so their read-backs under isa_rd are independent checks (the gen_pmc_ctrl seed-1 image: 8000 records with the pin on, 8001 with it off, 0 mismatches); the other counters still belong to the counter checkers `ctr_mcycle`, `ctr_minstret`,
`ctr_hpm_exact` and `ctr_hpm_bound` (step 2d, not built at 4c4b9b8), and cpuctrlsts bit 8 to the scramble-key
responder's `scrkey_proto` status row (record bit 8 versus the driven value at the ID-exit sample, not built); until
those land, a csrr of these CSRs passing `isa_rd` says nothing about counter or status correctness. Bit 8 in particular
is fed from `rvfi_ext_ic_scr_key_valid`, the same register the CSR read returns, so its `isa_rd` compare is an
RVFI-consistency anchor (the RVFI field agrees with the CSR read path) and nothing more: DEFERRED row until
`scrkey_proto` compares the record against the value the responder drove. The six intent-derivable HPM counters
(mhpmcounter5..10: loads, stores, jumps, branches, taken branches, compressed retired) are mirrored from the DUT today;
the independent TB-side model from the RVFI records (dv/auto_dv/evidence/gen_hpm_event_defs.md rules, expected
deviations D6, B7, B11, B17, B20) is the `ctr_hpm_exact` / `ctr_hpm_bound` landing after the event writers; only the
cycle-type counters stay record-synced as consistency compares. The cpuctrlsts bits
6 and 7 (sync_exc_seen, double_fault_seen) are hardware-set in the DUT and the shim sets them from the model's own trap
history (rtl/ibex_cs_registers.sv:935-943, :964-965), so a read of them is an independent compare. Draft-B
records (C5.5): the R4 forms (cmov, cmix, fsl, fsr, fsri) read rs3 = insn[31:27] from the model's register file; the
record's `rvfi_rs3_addr/rdata` are compared with it under `isa_rd` and the value feeds the reference.

Asynchronous entries (step 2b, T-090, found on the first interrupt-enabled and debug-storm programs): on a record with
`rvfi_intr` the model is offered exactly the interrupt the DUT's vector names (handler pc = mtvec base + 4 * cause, from
the record's pre_mip), so lines raised between the DUT's decision and the record cannot divert the model; Spike still
refuses an entry that is not pending and enabled (isa_trap), and the decision-time pending fact and the priority among
simultaneously pending lines are the irq checker's `irq_entry` cause rule (T-136, gen_component_api_irq_checker.md
Section 1), evaluated on every intr record from the previous record's `post_mip`, the entry record's `pre_mip` and the
driver's events. An NMI-vector entry (cause 31) is emulated by the model (landing 2a): the record's `ext_nmi` sample
decides external (mcause 0x8000001F) against internal (0xFFFFFFE0, mtval = the announced corruption's address from
`gen_bus_err_log::take_intg()`; when the corrupted load's record shows its first word was the announced one, the record's own address
replaces it, since the DUT's mtval is the LSU's last address, the misaligned address itself for a first-half corruption, rtl/ibex_controller.sv:416 and
rtl/ibex_load_store_unit.sv:258: landing 11 finding L11-F2, the crash_dump rule's red on gen_ut_intg_span; a store response's corruption follows the same rule without a suppressed write: the store's own address replaces the
announced word when its first word was the announced one, the same LSU line giving the raw address for a misaligned store's first half; the
handler's mtval read on gen_ut_intg_store is the red / green), and the shim performs the entry and the mstack restore on the closing mret
(gen_component_api_isa_shim.md), so NMI-enabled runs are full lock-step compares (LOG-051); integrity-error runs are full lock-step compares too since the suppressed-write gate (T-183, landing 2c; the row `suppressed register write` below). The external-versus-internal decision takes the pin sample OR a raise of the NM line reported by the irq driver's events in the current or the previous record's window (`imp_irq`, `nm_raised_since` / `nm_raised_prev`), so an NMI pulse shorter than the entry latency is classified external instead of failing the announced-corruption test (CM25-L-6). An interrupt entry the NMI pre-empted before its handler retired anything leaves no record of its own:
the record after the NMI entry then sits at a vector address without `rvfi_intr`, and the model takes that interrupt at
that record (`nmi_preempted` in the report, taken on a scoreboard-local `intr_now` flag so the monitor's transaction is never rewritten, CM25-M-1; 0 in every retained with-NMI storm run (six seeds, of which only seed 1 took an NMI entry: one entry in the whole sweep), so the rule rests on its derivation and has no red yet: a directed raise-then-NMI timing sequence is not built). The entry's vector cause is also written to the
bridge (`evt_irq_taken_cause`) for the irq driver's release rule. A load whose response carried an integrity error retires
with `rvfi_ext_rf_wr_suppress`: the DUT keeps the destination's old value, the model saw the clean word, so its write is
undone from a GPR snapshot taken before the step and the rd compare is skipped for that record (`rf_wr_suppressed`; 83 in the integrity run), but only when `gen_bus_err_log::take_intg_word` finds an announced corruption of that load's word, or of the next word when the load spans two bus words (the driver announces each response at its own word address, rtl/ibex_load_store_unit.sv:722; landing 9), and the record's rd fields report no write (rd_addr 0); the gate's list holds load announcements only (a store's corruption never suppresses a write); the flag on any other record is an `isa_rd` miss naming the unannounced address or the written register (T-183, landing 2c). On an ordinary record the pending bits that are ENABLED (M-mode with
MIE, or U-mode) are withheld from the model, because the DUT retired that instruction before taking them and Spike would
take them first; disabled pending bits are injected so a mip read compares. A debug request held through dret re-enters
debug on the very next record: the entry rule is `pc_rdata == DmHaltAddr` with `ext_debug_mode` and either the previous
record outside debug mode or the previous record a dret. Entries are handled BEFORE the Zcmp fold (T-134): a handler
whose first record is a non-last Zcmp micro-op still steps the entry first, and an interrupt or debug entry inside an
open sequence drops the partial micro-ops, since the DUT restarts the sequence from its first micro-op after mret
(rtl-arch R9 (c)); the drops are counted as `zcmp_splits` in the GEN_SB report and logged with the sequence pc. The
entry's model state is published before the fold returns (`publish_state` on a folded micro-op that carried the entry),
so the irq and debug checkers evaluate an entry whose handler starts with a micro-op like any other; two report-time
referees in gen_env (`irq_entries_referee`, `dbg_entries_referee`) fail the run when the checkers' entry counts differ
from the scoreboard's `irq_entries` / `dbg_entries` (red: gen_fu_l1c_a_zcmp_irq_sparse, 15 stepped, 0 seen; mutant RC1). Known
limit of the withholding rule (Critic T-090 L-7): a `csrr mip` that retires inside the one-record window with an
enabled pending bit reads the bit on the DUT while the model never saw it, an isa_rd miss (0 of 3934 storm records so
far); the miss names the record, so it is loud, not silent.

Trapping memory accesses (T-102c, conditioned by T-137, ruling LOG-026a): a trap record of a load or store arms the
model's bus fault on the record's address and size for that one step (`gen_isa_arm_fault`) ONLY when the data-bus driver
announced an injected or armed error response for that word (`gen_tb_pkg::gen_bus_err_log`, a cycle-stamped entry per
data-bus error gen_bus_driver injects; one announcement is one event: the arming consumes the oldest entry of each word
the access touches, both words of a spanning access, and `take()` reports which words were announced). Otherwise the model decides alone: a PMP denial is Spike's own decision from the same CSR writes, and a DUT fault
on an access nobody corrupted is an isa_trap miss (`dut trapped, model retired 1`). The GEN_SB report splits the trap
records into `faults_armed` (TB-caused) and `faults_unannounced` (the model decided) beside `bus_err_announced`; an
unannounced count above zero in a run without PMP denials is itself a finding. PMP denials: gen_pmp_deny_directed.S (a
locked NAPOT entry without R/W/X over a data buffer, ten load / store rounds into it) is green with 20 model-decided traps
and 0 mismatches (gen_fu_l2_pmp_deny_*), and mutant P13 (the model loses pmpaddr0 after every step, out of tree) is the
Critic's red: `isa_trap dut trapped, model retired 1` with the referees inert. Stated limitations: the arming trusts the
driver's announcement (a word both injected and legitimately faulting is armed once); instruction-side faults are never
armed (the model's fetch fault is its own decision from its memory map); data-side integrity corruptions are announced
separately (`gen_bus_err_log::intg_announced`) for the irq checker's internal-NMI classification, never for arming (they
raise alert_major_bus and an internal NMI, not a bus-error trap). Red for the conditioned form: MB6 in
dv/auto_dv/mutations/gen_mut_step2b.md (a legal store reported as a trap is an isa_trap miss).

Conventions the comparator adopts from the DUT (the landing-2a runs surfaced them; each names the RTL that makes it so and
the items it decides; cited as rows, ruling LOG-037c):

| convention | what the comparator does | RTL | decides |
|---|---|---|---|
| NMI-pre-empted interrupt entry | an interrupt entry the NMI pre-empts before its handler retires anything has no `rvfi_intr` record of its own: the record after the NMI's entry sits at a vector address without the flag, and the model, back from the NMI's mret in the pre-entry state, takes that interrupt then (`after_nmi_entry`, counted `nmi_preempted`) | rtl/ibex_core.sv:2403-2413 (the intr flag goes to the NMI record), rtl/ibex_controller.sv:498 | TP-IRQ-079 |
| suppressed register write | a load whose response carried an integrity error retires with `rvfi_ext_rf_wr_suppress = 1` and keeps its old destination: the model's write is undone from a GPR snapshot taken before the step (counted `rf_wr_suppressed`) when the DUT's flag is set AND the gate (T-183) finds an announced corruption of the load's word (`take_intg_word(mem_addr)`, and of the next word for a spanning load: BOTH words are consumed, so a doubly corrupted spanning load leaves nothing a later lying suppress could use, CM132-L-4, red MUT-SUP3 on gen_ut_intg_span) with rd_addr 0; otherwise an `isa_rd` miss; a record inside a Zcmp sequence (`is_seq`) bypasses the gate and is judged by the sequence's union compare (tb_l10 L-4); reds MUT-SUP (the flag asserted on clean loads) and MUT-SUP2 (the announced address off by 0x100), gen_mut_step2b.md | rtl/ibex_core.sv:2383-2385 | TP-DMEM-039 / 041 / 064, TP-RVFI-024 |
| irq_entry bound restarts at each entry | a raised, enabled line must be taken within GEN_IRQ_ENTRY_BOUND_RECORDS records counted from the LAST interrupt entry, not from the raise: the DUT serves one entry at a time and the others wait behind the handler | rtl/ibex_controller.sv:736-757 (one taken cause per entry) | TP-IRQ-001 / 012 / 022 |
| mtval of a bus fault | the failing bus transaction's address (Rules (b) below) | rtl/ibex_load_store_unit.sv:258, :520, :540 | TP-DMEM fault items |

Rules of the armed fault, from the DUT (landing 1c, gen_dmem_err_directed.S under `+gen_knob_dmem_err_rate=frequent`):
(a) both encodings: RVFI reports a compressed instruction in its 16-bit form, so the load/store test and the access size
come from `gen_tb_pkg::gen_insn_mem_access` (32-bit opcodes, c.lw / c.sw / c.lwsp / c.swsp, the Zcb byte and half forms);
a c.sw fault was never armed before it (red: gen_fu_l1c_a_dmem_err_rate, `isa_trap dut trapped, model retired 1` at a
c.sw; mutant RC2). (b) mtval: Ibex writes the address of the FAILING bus transaction, `lsu_addr_last` in
rtl/ibex_load_store_unit.sv:258, which advances to the second word of a spanning access only when the first transaction
had no error (:520, :540); the scoreboard derives it from the words `take()` consumed (the effective address when the
first word was announced, else the second word) and hands it to the shim (`gen_isa_arm_fault(kind, addr, size, tval)`),
which writes mtval after the faulting step (Spike's own tval is the effective address; shim unit test section 13,
mutant RS1). (c) Announced-never-trapped: the report-time referee `bus_err_leftover` fails the run when an announcement
older than GEN_BUS_ERR_DRAIN_CYCLES (96 = 32 + 32 + 32: the announcement is stamped at the first transaction's grant; the second half of a split access waits its own grant window, at most 32, then its response the rvalid window, at most 32, and 32 more cover the response-to-record lag with margin; a longer regime window must raise it) was never consumed by a trap record (an injected error the DUT did not trap on, or
one the TB announced without driving it: mutant RM-L1). (d) Limitation: a faulted store's memory side effect is the
driver's (`err_store_perform`) on the DUT side and none on the model's; a program that reads such a word back before a
successful retry diverges. (e) The riscv-dv seed-7 program is not a vehicle for injected data faults: its handler skips
the faulting instruction, a later use of the unloaded register reads an unmapped address, and there the TB memory
returns zeros with a collected MEM_UNMAPPED error while Spike faults (gen_fu_l1c_b_dmem_err_rate_s7, a program limit).

Zcmp sequences: a trapping Zcmp micro-op ends the sequence early (it is compared as the sequence's last record, the model
steps the whole instruction with the fault armed, and the accesses and register writes completed before the fault are
compared as the union; both sides store the highest register of rlist first, rtl/ibex_compressed_decoder.sv:626-660 and
Spike's cm_push.h, so the ordered store compare holds), and its `pc_wdata` is its own pc, since the aborted sequence
restarts from the first micro-op (rtl-arch R9; the trap-record rule uses offset 0 when `rvfi_ext_expanded_insn_valid`
is set, `insn_len(insn)` otherwise). Breakpoint exceptions (rtl-arch R10): Ibex writes mtval 0 on [c.]ebreak (spec-legal;
the pc arm is CHERIoT-only), the shim mirrors it, and on a cause-3 trap record the comparator requires the model's mepc
to equal the record's pc and its mtval to be 0 under isa_trap (counted as `breakpoints`); a shim convention, not a DUT
finding. Odd jalr targets (rtl-arch R11, bug candidate B13 in the DV Lead's log): `rvfi_pc_wdata` of a jalr / c.jr /
c.jalr record carries the raw rs1 + imm with bit 0 set while the core fetches the even address (rtl/ibex_core.sv:2084);
`isa_pc_next` masks bit 0 on exactly those records and counts them as `b13_odd_jalr` (a documented exception; the red
with the mask absent is gen_tdd_logs/lockstep/gen_fu_a_red_jalr_odd_r11_v2_*); any other odd `pc_wdata` still fails.

Model-state publication (step 2b, T-090): after every compared record the scoreboard publishes one `gen_model_state`
on `ap_state` (order, cycle, model pc after the step, insn, mie / mstatus / mcause / mepc / mtval / dcsr read from the
model, privilege after the record, trap / interrupt / mret / dret / debug flags, and whether the record wrote mie or
mstatus, and for an interrupt entry `entry_cause`, the cause the DUT's vector names, 31 for the NMI, -1 otherwise, so the
irq checker classifies the entry from the DUT's own evidence even when the model did not take it); `gen_irq_checker`,
`gen_dbg_checker` and `gen_misc_monitor` consume it and never read the shim directly.

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
