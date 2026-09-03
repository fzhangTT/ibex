# T-090 RTL facts: interrupt and debug entry timing (rtl-arch)

Owner: rtl-arch. Written 2026-09-03 15:20Z on the Orchestrator's task (14:57Z) for tb-infra's step-2b
comparator fixes (commit 67b5971, dv/auto_dv/env/gen_rvfi_pkg.sv, gen_checkers_pkg.sv). Style follows
gen_t102_rtl_facts.md: per fix the RTL fact with file:line, then whether the TB rule matches the RTL or
hides a real check. Configuration: opentitan (cheriot_enable_i tied Off, dv/auto_dv/tb/gen_dut_top.sv:206;
BranchPredictor 0, WritebackStage 1, SecureIbex 1, DbgTriggerEn 1, DbgHwBreakNum 1). RVFI signal names as
exported by rtl/ibex_core.sv. This note reads RTL only; the checker policy is tb-infra's, the boundary
rules it owes are called out per section.

## 0. The two clocks that matter

Every RVFI record is produced at a retirement (rvfi_id_done / rvfi_wb_done, rtl/ibex_core.sv:1851-1853,
:1890). The interrupt/debug DECISION is a separate event in the controller FSM: `handle_irq` /
`enter_debug_mode` in DECODE (rtl/ibex_controller.sv:498, :476) drive the FSM to IRQ_TAKEN / DBG_TAKEN_IF
(:711-717, :705-709) only when the pipeline has drained (`!stall && !special_req && !id_wb_pending`, :704;
id_wb_pending = instr_valid_i | ~ready_wb_i, :296). So a decision happens strictly BETWEEN two retirements:
after the record of the instruction that retired last, before the record of the handler's first
instruction. The three fixes are all about which record carries which side of that gap.

## 1. Fix: the model must not take a pending enabled interrupt one record early (ordinary records)

TB change (gen_rvfi_pkg.sv:367-376): on an ordinary record, the ENABLED pending bits (M-mode with MIE, or
U-mode) are withheld from the model (`ien ? pre_mip & ~mie_m : pre_mip`), the disabled pending bits are
still injected so a `mip` CSR read compares.

RTL fact: the DUT retires an instruction and only THEN takes a pending interrupt, because the entry waits
for the pipeline to drain.
- `handle_irq = ~debug_mode_q & ~debug_single_step_i & ~nmi_mode_q & (irq_nm | (irq_pending_i & irq_enabled)) & !(INSTR_EXPANDED_COMMIT)` (rtl/ibex_controller.sv:498-500); `irq_enabled = csr_mstatus_mie_i | (priv_mode == U)` (:490); `irq_pending_o = |(mip & mie_q)` (rtl/ibex_cs_registers.sv:1044-1045).
- In DECODE the entry is gated by `!stall && !special_req && !id_wb_pending` (rtl/ibex_controller.sv:704-717): the instruction currently in ID/WB retires first; its RVFI record is emitted; the interrupt is taken on the following cycle. `PipeEmptyOnIrq` asserts the pipe is empty at entry (:1078-1079).
- The handler entry is itself a record (with rvfi_intr, section 2), so the interrupt belongs to the NEXT record, not the one the DUT just retired.
- The record's `pre_mip` is `cs_registers_i.mip` sampled when the instruction left ID (rtl/ibex_core.sv:1995 path, :2135 post_mip), i.e. the pending set is real, but the DUT demonstrably did not act on it for THIS instruction.

Verdict: the TB rule MATCHES the RTL and does not hide a check. Spike, offered an enabled pending bit, would trap before executing the instruction; the DUT executes it and traps after. Withholding the enabled bits keeps the model in step; injecting the disabled bits preserves the `mip` read comparison (the irq_pending checker, gen_component_api_irq_checker.md section 5, still checks `irq_pending_o == |(mip & mie_q)` against the RTL every cycle, so masking the model's copy does not lose the pending-visibility check). The one thing this rule assumes is that the DUT never delays an entry past exactly one retirement; that bound is the irq_entry checker's job (below), not this record's.

## 2. Fix: the entry record's pre_mip is sampled after the decision, so offer the model the bit the DUT's vector names

TB change (gen_rvfi_pkg.sv:355-366): on a record with `rvfi_intr`, compute the cause from the vector
(`cause = (pc_rdata - (mtvec & ~0xFF)) >> 2`) and inject exactly `1 << cause` rather than the raw
`pre_mip`; NMI (cause 31) keeps `pre_mip`.

RTL fact: the vector encodes the taken line, and it is decided from the qualified pending set at the
decision cycle, which is earlier than the record's pre_mip sample.
- Vectored entry PC: `exc_pc = {mtvec[31:8], 1'b0, irq_vec, 2'b00}` (rtl/ibex_if_stage.sv:228), `irq_vec = exc_cause.lower_cause` (:214), so `pc_rdata of the entry = mtvec_base + 4*cause` and the cause is recoverable from the PC exactly as the TB does. Base is `{mtvec[31:8], 8'h00}` (non-CHERIoT path).
- The cause is chosen in IRQ_TAKEN by a fixed priority: NMI (rtl/ibex_controller.sv:736), then fast `irq_fast[14:0]` with `mfip_id` the LOWEST set fast id (:746-751; the loop :503-509 counts down so the lowest index wins), then external (:752), then software (:754), then timer (:756). That priority is the architecture's, applied to `irqs_i = mip & mie_q` at the decision.
- The record's `pre_mip` is sampled later (when the handler's first instruction is in ID, rtl/ibex_core.sv:1995, :2135), and `irqs_o` is level `mip & mie_q` (rtl/ibex_cs_registers.sv:1044) that can change between the decision and the sample (a line drops or another rises). So `pre_mip` is not a reliable record of the decision-time set; the vector is.

Verdict: the TB rule MATCHES the RTL for keeping the model in step, but it deliberately does NOT check two things, and those are correctly called out as owed to the irq checker (gen_rvfi_pkg.sv:361-363, doc section 5 `irq_entry`):
- (a) that the taken line was actually pending and enabled at the decision. The vector tells you which line the DUT claims; it does not prove the line was legitimately pending. The RTL requires `irq_pending_i & irq_enabled` at the entry (:498-499), so the checker must confirm the injected cause bit was set in the record's own `pre_mip` (or in `post_mip` of the previous record) AND enabled by `mie`/privilege. Without that, a DUT that vectored to a wrong or un-enabled cause would still pass, because the model is simply told to follow the vector.
- (b) the priority among simultaneously pending lines: NMI > fast(lowest id) > external > software > timer (rtl/ibex_controller.sv:736-757, :503-509). The model follows the vector, so it cannot catch a DUT that picked the wrong one of several pending lines. The irq_entry checker must recompute the expected highest-priority cause from `pre_mip & mie` and compare it to the vectored cause.

So this fix keeps the comparator honest (no false mismatch from a stale pre_mip) but moves the real interrupt-selection check to the irq checker; that checker is not yet built (doc section 5 marks it owed, "boundary rules"). The RTL facts it needs are exactly (a) and (b) above with those lines.

Precision on pre_mip vs post_mip: `pre_mip` is `mip` when the instruction left ID; `post_mip` is `mip` at the next stage advance (rtl/ibex_core.sv:2136). For the entry record the useful decision-time set is closest to the PREVIOUS record's `post_mip`; the checker has both and should prefer post_mip of the pre-entry record over pre_mip of the entry record when reconstructing the decision set.

## 3. Fix: a debug request held through dret re-enters debug at once

TB change (gen_rvfi_pkg.sv:377, :385): the debug-entry condition becomes `ext_debug_mode && (!dbg_q || dret_q) && pc_rdata == DmHaltAddr`, and `dret_q` is set when the previous record's insn was DRET.

RTL fact: dret leaves debug mode on one instruction and a still-asserted `debug_req_i` re-enters on the
very next.
- dret clears debug mode in FLUSH: `dret_insn: debug_mode_d = 1'b0; csr_restore_dret_id_o = 1'b1` (rtl/ibex_controller.sv:961-964); privilege restored to `dcsr.prv` (rtl/ibex_cs_registers.sv:949-951).
- Re-entry is level-sensitive: `new_debug_req = debug_req_i & ~debug_mode` (rtl/ibex_core.sv:1928) and `enter_debug_mode_prio_d = (debug_req_i | do_single_step_d) & ~debug_mode_q & ...` (rtl/ibex_controller.sv:474-476). Once dret clears `debug_mode_q`, a held `debug_req_i` makes `enter_debug_mode` true again the next cycle, so the DUT goes DBG_TAKEN_IF and the next retired record is the debug-ROM entry (`pc_rdata == DmHaltAddr`, EXC_PC_DBD = DmHaltAddr, rtl/ibex_if_stage.sv:229; :764-783). There is no "one normal instruction first": debug entry is a priority entry that halts IF before a new instruction is accepted (:700-708).
- `dcsr.cause` for the re-entry is HALTREQ = 3 (rtl/ibex_controller.sv:519-523 `debug_cause_d = ... debug_req_i ? DBG_CAUSE_HALTREQ`), written at DBG_TAKEN_IF (rtl/ibex_cs_registers.sv:910-914).

Verdict: the TB rule MATCHES the RTL. Without the `dret_q` term the model would expect one retired instruction between dret and re-entry and would mismatch the immediate re-entry (the entry record's `dbg_q` from the previous non-debug record is 0 anyway on the first entry; the `|| dret_q` covers the case where the previous record was IN debug mode via the dret). One caveat for the debug checker (gen_component_api_debug_checker.md `dbg_dret`, `dbg_masked`): the immediate re-entry is HALTREQ, but if `dcsr.step` was set, the re-entry after dret is a STEP entry (cause 4) after exactly one retired instruction, a different record from the held-req case; the checker must read `dcsr.cause` in the debug ROM (as `dbg_entry` already says) to tell them apart. Also, a debug request is NOT taken during a Zcmp COMMIT micro-op (rtl/ibex_controller.sv:474-477 exclude INSTR_EXPANDED/COMMIT), so "the very next record" is the next record that is not a non-last Zcmp micro-op; `dbg_masked` already states "a request held during a Zcmp sequence enters only after _last", which matches (rtl/ibex_controller.sv:498-500 for irq, :474-477 for debug).

## 4. Cross-checks and what each checker still owes

- irq_entry (owed, doc section 5): recompute the highest-priority enabled pending cause from the pre-entry record's `post_mip & mie` and compare to the vectored cause; confirm the cause was enabled. RTL: rtl/ibex_controller.sv:736-757 (priority), :498-499 (enable), rtl/ibex_cs_registers.sv:1044 (irqs_o = mip & mie_q). This is the check section 2 moves off the model.
- irq_masked: no entry while `mstatus.MIE == 0` in M-mode / debug / NMI (rtl/ibex_controller.sv:498). A one-cycle pending pulse that the DUT never sampled produces no entry and no record; the model, told to follow the vector, never sees a phantom entry, so this holds.
- nmi_entry: NMI ignores MIE/mie (`irq_nm` term is outside the `& irq_enabled`, rtl/ibex_controller.sv:499), cause 0x8000001F, vector `mtvec_base + 0x7C` (irq_vec = ExcCauseIrqNm.lower_cause = 31, rtl/ibex_if_stage.sv:218). The TB keeps `pre_mip` for NMI (gen_rvfi_pkg.sv:363), correct because NMI is not in `mip`.
- rvfi_ext_irq_valid: the no-retire notification (rtl/ibex_core.sv:1965-1971) is a LEVEL that rises four cycles after the decision (gen_interface_inventory.md row), so the irq checker's "next event" can be this notification OR the next intr record; the doc section 5 already allows both.

## 5. What this note does not decide

Whether each boundary rule lives in gen_checkers_pkg.sv or the shim, and the bound constant
GEN_IRQ_ENTRY_BOUND_RECORDS, are tb-infra's. Every RTL statement is by reading; the step-2b retained
logs (gen_ut_irq, gen_ut_dbg) exercised the three fixes but I did not re-run them. A waveform of any
entry sequence is available on request. Two items are genuinely OWED and not yet checked anywhere: the
decision-time pending fact and the priority among simultaneously pending lines (section 2 a/b); until the
irq_entry checker computes them, a DUT that vectors to a wrong enabled cause passes the comparator.
