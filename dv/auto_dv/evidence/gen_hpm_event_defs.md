# HPM event definitions for an independent counter model (rtl-arch)

Owner: rtl-arch. Written 2026-09-03 13:05Z on the Orchestrator's idle item (12:43Z) for tb-infra's T-102
review, which asks the shim or a TB counter to compute mhpmcounter5..10 independently instead of
copying the DUT. Scope: for each of the six events, the documented intent, the RTL signal chain with
file:line, the pipeline moment the count happens, the RVFI-visible rule an independent counter should
implement, and every known place where the RTL deviates from the intent. Configuration: opentitan
(dv/auto_dv/evidence/gen_param_resolution.md): MHPMCounterNum 10 (counters 3..12 exist),
MHPMCounterWidth 40 (rtl/ibex_core.sv:26), BranchTargetALU 1, WritebackStage 1, SecureIbex 1 (so
DataIndTiming 1 and the dummy-instruction generator exist), cheriot_enable_i tied Off
(dv/auto_dv/tb/gen_dut_top.sv:206), RV32ZC ZcaZcbZcmp.

Principle for the TB: count the INTENT (doc/03_reference/performance_counters.rst:30-50) from the RVFI
stream; where the RTL deviates, the deviation is a recorded DUT finding (bug-log rows D6, B7, B11, B17 =
BUG-09, plus the candidate in section 3), so a DUT-vs-model difference there is expected and belongs
in the bounded / expected-fail class, not in a TB fix. Which class each one gets is tb-infra's and the DV
Lead's decision.

## 1. Common plumbing (all counters)

- Event pulses enter rtl/ibex_cs_registers.sv:1585-1598 (`mhpmcounter_incr[i]`), one bit per event per
  cycle: a counter can move by at most 1 per cycle.
- Each counter increments on `mhpmcounter_incr[Cnt] & ~mcountinhibit[Cnt]` (rtl/ibex_cs_registers.sv:1679,
  generic loop :1667-1690); mcountinhibit resets to 0 (:1725), so every counter runs from reset until
  software inhibits it. Width 40 bits for counters 3..12 (:1674); mcycle and minstret are 64 bits
  (:1622-1650).
- The event selectors are hardwired (mhpmeventN = 1 << (N-3), :1602-1619): counter N always counts event N.
- Reads: `csrr` of mhpmcounter5..9 returns the register value in the cycle the csrr is in ID; pulses of
  older instructions have landed by then (events 5..9 fire in ID/EX, see below). mhpmcounter10 (and
  minstret) add the instruction currently in WB through the `_spec` path (:1651-1660 comment,
  :1675 `ProvideValUpd(Cnt == 10)`, rtl/ibex_wb_stage.sv:206-207), so a csrr sees a count that includes
  the compressed instruction retiring in the same cycle.
- Writes: `csrw mhpmcounterN` loads the counter (:858 `mhpmcounter_we`), low and high halves separately.
- Dummy instructions (cpuctrlsts.dummy_instr_en) are DUMMY_ADD/MUL/DIV/AND (rtl/ibex_dummy_instr.sv:37-40):
  none is a load, store, jump, branch or compressed instruction (rtl/ibex_if_stage.sv:527 flags them
  non-compressed), so events 5..10 are unaffected by them. They do count in minstret and in the mul/div
  wait counters (bug-log B7).

## 2. The six events

| Ev | Doc intent (performance_counters.rst) | RTL pulse and chain (file:line) | Moment | Independent rule from RVFI | Known deviations |
|---|---|---|---|---|---|
| 5 NumLoads (0xB05) | "Number of data memory loads. Misaligned accesses are counted as two accesses" (:34-35) | rtl/ibex_load_store_unit.sv:468-475: in ls_fsm IDLE, when the ID stage presents a request (`cpu_req_valid`), `perf_load_o = ~lsu_we_i` together with `data_req_o = 1`; no pulse in WAIT_GNT*, WAIT_RVALID* (only :425-426 defaults, :456-457 is the CHERIoT-cap path, unreachable here). Wired straight to the counter: rtl/ibex_core.sv:1121, :1557; rtl/ibex_cs_registers.sv:1591. | The cycle the LSU issues the FIRST bus request of the instruction (ID/EX), before the response and before retirement. | One per load instruction record: LB/LH/LW/LBU/LHU, c.lw/c.lwsp, Zcb c.lbu/c.lhu/c.lh, and EACH cm.pop* micro-op (RVFI emits one record per micro-op, rtl/ibex_core.sv:2263-2268, and the LSU issues one request per micro-op). Count trap records too when the trap is the load's own access fault (cause 5): the pulse fires at request time, before the fault, and a PMP-denied request still pulses (the PMP mask is applied on the core output only, rtl/ibex_core.sv:1063, not on `perf_load_o`). | D6: a misaligned load is one pulse, the doc says two (lsu:468-475, the second half runs in WAIT_*_MIS without a pulse). |
| 6 NumStores (0xB06) | "Number of data memory stores. Misaligned accesses are counted as two accesses" (:36-37) | Same arm, `perf_store_o = lsu_we_i` (rtl/ibex_load_store_unit.sv:475); rtl/ibex_core.sv:1122, :1558; rtl/ibex_cs_registers.sv:1592. | Same as 5. | One per store instruction record: SB/SH/SW, c.sw/c.swsp, Zcb c.sb/c.sh, EACH cm.push* micro-op; plus the store's own access-fault trap records (cause 7). | D6 (same as loads). |
| 7 NumJumps (0xB07) | "Number of unconditional jumps (j, jal, jr, jalr)" (:38) | Decoder first cycle: `jump_set_o = 1` for JAL (rtl/ibex_decoder.sv:313-330), JALR (:338-366) and FENCE.I (:704-720, "implemented as a jump to the next PC"); the end-of-decode override clears jump_in_dec_o and jump_set_o for every illegal encoding (:905-918), so an illegal JALR funct3 never pulses. id_stage: `jump_set_raw = jump_set_dec` in FIRST_CYCLE (rtl/ibex_id_stage.sv:941), deduplicated `jump_set = jump_set_raw & ~branch_jump_set_done_q` (:807-814). Controller DECODE: `perf_jump_o = jump_set_i` in the pc_set block (rtl/ibex_controller.sv:681-687); rtl/ibex_core.sv:828, :1554; rtl/ibex_cs_registers.sv:1593. | The first DECODE cycle of the jump (ID), when the controller sets the PC; before retirement. Exactly one pulse per instruction instance (dedup). | One per record with trap = 0 whose insn is JAL or JALR (c.j, c.jal, c.jr, c.jalr arrive decompressed as JAL/JALR, so they count; an illegal JALR encoding traps without a pulse). mret, dret are NOT jumps (special_req path, rtl/ibex_controller.sv:290-293). | (a) FENCE.I counts as a jump: candidate D-row, section 3. (b) Corner: a jump behind an outstanding WB load/store pulses speculatively (id_stage comment :807-813, `instr_executing_spec` has no outstanding-access term :1054-1057); if that access then faults, the jump is killed, re-fetched after the handler and pulses again: two pulses for one retired jump. Not seen in a run; reading only. |
| 8 NumBranches (0xB08) | "Number of branches (conditional)" (:39) | id_stage FIRST_CYCLE arm `branch_in_dec: perf_branch_o = 1` under `instr_executing_spec` (rtl/ibex_id_stage.sv:889-934, default :887); decoder `branch_in_dec_o = 1` for OPCODE_BRANCH (rtl/ibex_decoder.sv:372-384), cleared again by the end-of-decode override for every illegal encoding (:905-918), so illegal funct3 (010, 011) encodings never pulse. No dedup. rtl/ibex_core.sv:829, :1555; rtl/ibex_cs_registers.sv:1594. | Every cycle the branch is valid in ID in FIRST_CYCLE with `instr_executing_spec` true (normally exactly one cycle). | One per record with trap = 0 whose insn is BEQ/BNE/BLT/BGE/BLTU/BGEU (c.beqz, c.bnez arrive decompressed). A branch's only traps are fetch-side (instruction access fault) and those do not pulse either: `instr_executing_spec` carries ~instr_fetch_err_i (:1054-1057); illegal encodings are cleared by the decoder override (:905-918). | B17 = BUG-09: while an older load/store is still outstanding in WB, `instr_executing_spec` stays true and `id_fsm_q` does not advance (:867-868 advances only under `instr_executing`, :1059-1062), so the branch pulses in EVERY waiting cycle: over-count by about (response delay - 1). Independent model: bounded class whenever a branch immediately follows a load/store. |
| 9 NumBranchesTaken (0xB09) | "Number of taken branches (conditional)" (:40) | id_stage: `branch_set_raw_d = branch_decision_i \| data_ind_timing_i` (rtl/ibex_id_stage.sv:928); with BranchTargetALU and DIT off, `branch_set_raw = branch_set_raw_d` the same cycle (:770, :790-791); with data_ind_timing_i = 1 the flopped copy is used (:775-791). Dedup `branch_set = branch_set_raw & ~branch_jump_set_done_q` (:815). Controller DECODE `perf_tbranch_o = branch_set_i` (rtl/ibex_controller.sv:681-687); rtl/ibex_core.sv:830, :1556; rtl/ibex_cs_registers.sv:1595. | The cycle the controller sets the PC for the branch (first cycle with DIT off, second cycle with DIT on). Exactly one pulse per instruction instance (dedup). | One per conditional-branch record (trap = 0) whose next fetch address is the target: rvfi_pc_wdata != rvfi_pc_rdata + insn size (2 or 4). An illegal funct3 encoding never sets the branch (decoder override :905-918), so it does not count here. | B11: with cpuctrlsts.data_ind_timing = 1 every branch asserts branch_set (:928 ORs data_ind_timing_i), taken or not, so NumBranchesTaken counts every branch (the not-taken target is pc + size through the flopped `branch_taken` :819-831). Corner (b) of event 7 applies here too (speculative set behind a faulting WB access). |
| 10 NumInstrRetC (0xB0A) | "Number of compressed instructions retired" (:41) | rtl/ibex_wb_stage.sv:208-210: `perf_instr_ret_compressed_wb_o = perf_instr_ret_wb_o & wb_compressed_q`, with `perf_instr_ret_wb_o = instr_done_wb_o & wb_count_q & ~(lsu_resp_valid_i & lsu_resp_err_i)`; `wb_count_q <= instr_perf_count_id_i` (:150, :169) = `~ebrk_insn & ~ecall_insn_dec & ~illegal_insn_dec & ~illegal_csr_insn_i & ~instr_fetch_err_i & ~minstret_write & !(instr_gets_expanded_i inside {INSTR_EXPANDED, INSTR_EXPANDED_COMMIT})` (rtl/ibex_id_stage.sv:1218-1220); `wb_compressed_q <= instr_is_compressed_id_i` (:149, :168), the fetch-side flag `instr[1:0] != 2'b11` (rtl/ibex_compressed_decoder.sv:883; rtl/ibex_if_stage.sv:609). rtl/ibex_core.sv:1147, :1550; rtl/ibex_cs_registers.sv:1596. | Retirement (WB done), in program order: the same moment the RVFI record is produced. | One per RVFI record with trap = 0 and a 16-bit encoding, where an expanded Zcmp instruction counts ONCE, on its LAST micro-op (RVFI: one record per micro-op, rvfi_expanded_insn_valid with rvfi_expanded_insn_last on the last one, rtl/ibex_core.sv:2270-2280; the RTL excludes the non-last micro-ops through INSTR_EXPANDED / INSTR_EXPANDED_COMMIT). Excluded by the RTL and therefore by the rule: c.ebreak (ebrk_insn), compressed illegal encodings (illegal_insn_dec), any instruction with a fetch error, and a compressed load/store whose bus response is an error (`lsu_resp_err`): all of these are trap records anyway. | None known. Note the read forwarding: a csrr of mhpmcounter10 sees the compressed instruction retiring in WB in that cycle (section 1). |

Insn-size rule for events 9 and 10 from RVFI: a record is compressed iff `rvfi_insn[1:0] != 2'b11` for
non-expanded records (rtl/ibex_core.sv:2263-2265 puts the 16-bit encoding in rvfi_insn); for expanded
micro-ops rvfi_insn holds the 32-bit micro-op and `rvfi_expanded_insn` the 16-bit source.

## 3. Candidate for the bug log (DV Lead decides; doc-vs-RTL, reading only, no run yet)

- D-NUMJUMPS-FENCEI: NumJumps (mhpmcounter7) increments on FENCE.I. RTL: rtl/ibex_decoder.sv:704-720
  (`jump_in_dec_o = 1`, `jump_set_o = 1` in the first cycle: FENCE.I is implemented as a jump to the next
  PC; FENCE.I is legal, so the illegal-encoding override at :905-918 does not clear it) ->
  rtl/ibex_id_stage.sv:941, :814 -> rtl/ibex_controller.sv:687. Doc: performance_counters.rst:38 lists
  "j, jal, jr, jalr" only. Reproducer: `csrr t0, mhpmcounter7; fence.i; csrr t1, mhpmcounter7`: doc
  predicts 0, RTL gives 1. Class: doc-vs-RTL like D20.
  Recommended direction: the DOC. The counter is defined by the doc as the number of unconditional
  jump instructions; the PC redirect on FENCE.I is how the RTL flushes the prefetch buffer and icache,
  an implementation artifact that happens to share the jump path, and no software reading NumJumps
  expects fences in it. So the plan's counter checker should follow the doc (no increment on FENCE.I),
  the RTL difference is an expected-fail item until the owner rules, and the RTL fix is a one-term gate
  (perf_jump_o without the FENCE.I case, or a separate flush request) rather than a semantic change.
  Severity low: no functional effect, one count per fence.i.

- Withdrawn (13:30Z, was D-COUNT-ILLEGAL-ENC): the first version of this note claimed that illegal
  conditional-branch funct3 encodings (010, 011) and illegal JALR funct3 encodings pulse NumBranches /
  NumJumps once before trapping. Wrong: the decoder's end-of-decode override (rtl/ibex_decoder.sv:905-918)
  clears jump_in_dec_o, jump_set_o and branch_in_dec_o whenever illegal_insn is set, so neither counter
  moves. The rows of section 2 now say so. Kept here so the earlier claim cannot be cited by mistake.

## 4. What this note does not decide

Whether the independent counter runs in the shim or in a TB component, and which deviation goes in which
comparison class, is tb-infra's; adding section 3 to the bug log is the DV Lead's. Every RTL statement
above is by reading. The four batch-1 logs do not exercise any deviation of section 2 or 3: their
counter mismatches (csr_reset_s1 orders 35 and 52, mhpmcounter4 and mhpmcounter6) come from the shim
modelling every HPM counter as 0, not from a DUT-vs-intent difference. A waveform confirmation of any
row is available on request.
