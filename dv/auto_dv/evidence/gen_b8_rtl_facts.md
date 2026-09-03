# B8 RTL facts: dummy-instruction insertion inside a Zcmp expansion (T-225)

Owner: rtl-arch. Written 2026-09-03T19:10Z from the RTL in this clone (rtl/ibex_if_stage.sv, rtl/ibex_compressed_decoder.sv,
rtl/ibex_dummy_instr.sv, rtl/ibex_register_file_ff.sv, rtl/ibex_core.sv, rtl/ibex_controller.sv). Scope: the
RTL-side cause of bug candidate B8 (cpuctrlsts.dummy_instr_en = 1 makes cm.push / cm.pop sequences diverge from
the lock-step model). RTL is read-only; this note states the mechanism and its consequences, no fix.

## 1. Verdict

B8 is an architectural bug, not an RVFI export bug. When a dummy instruction is inserted while the compressed
decoder is expanding a cm.push / cm.pop / cm.popret / cm.popretz (or cm.mvsa01 / cm.mva01s), the expansion
FSM advances as if its current micro-op had been accepted, but the ID stage receives the dummy instruction
instead. The micro-op is never executed: a store is not issued, a load (and its register-file write) is not
performed, or the stack-pointer adjust is not applied. If the lost micro-op was the last one of the expansion,
the FSM returns to idle while the prefetch buffer still holds the cm.* halfword, and the whole expansion is
executed again from the start with the architectural state as it stands at that moment. Nothing on RVFI is
suppressed for an executed micro-op: the records that are missing correspond to micro-ops that did not happen,
and the extra records correspond to micro-ops that happened twice.

## 2. The two signals that disagree

- The Zcmp FSM in the compressed decoder advances on its id_in_ready_i port. The IF stage drives that port with
  `id_in_ready_i & ~pc_set_i` (rtl/ibex_if_stage.sv:493) and valid_i with `fetch_valid & ~fetch_err` (:492).
  Neither term contains the dummy-insertion stall.
- The IF/ID pipeline register takes the dummy instruction in the same cycle: instr_out is
  `insert_dummy_instr ? dummy_instr_data : instr_decompressed` (:526), the expansion tag presented to ID is forced
  to INSTR_NOT_EXPANDED (:528), and the register is written whenever `if_instr_valid & id_in_ready_i & ~pc_set_i`
  (instr_new_id_d :570, if_id_pipe_reg_we :587, the loads :602-612). dummy_instr_id_o is set for that entry
  (:541-542).
- The prefetch buffer is held: fetch_ready = `id_in_ready_i & ~stall_dummy_instr & !(expanded or commit tag)`
  (:808-809; the branch-predictor variant :791-793 adds the skid term), with stall_dummy_instr =
  insert_dummy_instr (:535). So the cm.* halfword stays at the decoder input and valid_i stays high.
- Consequence: in the insertion cycle the decoder sees valid_i = 1 and id_in_ready_i = 1, takes every
  `if (valid_i && id_in_ready_i)` / `if (id_in_ready_i)` branch of its FSM (rtl/ibex_compressed_decoder.sv:641,
  :653, :661, :676 for cm.push; :709, :718, :726, :745, :761, :767 for the pop family; :791, :798, :819, :826 for
  the moves), i.e. it drops the top register from cm_rlist, moves cm_sp_offset and changes cm_state, while the
  micro-op it had on instr_o (:634, :660, :675, :702, :725, :740-742, :758, :766) is discarded by the mux at :526.
- The dummy-insertion decision itself has no knowledge of the expansion: insert_dummy_instr =
  `dummy_instr_en_i & (dummy_cnt_q == dummy_cnt_threshold)` (rtl/ibex_dummy_instr.sv:115), and the counter
  advances once per accepted instruction including every micro-op (dummy_cnt_en :103-104 uses id_in_ready_i and
  fetch_valid_i), so with dummy_instr_en set a dummy lands inside an expansion whenever the threshold falls on one
  of its micro-ops. The IF stage's own PC-sequence assertion excludes exactly this combination (prev_instr_seq_d
  :664-669 masks both stall_dummy_instr and the expansion tags), which shows the interaction was known to the
  checker but not handled in the FSM.
- The only FSM reset is flush_expanded = `pc_set_i & (pc_mux_i == PC_EXC)` (rtl/ibex_if_stage.sv:483,
  rtl/ibex_compressed_decoder.sv:889): a trap or interrupt entry, not a dummy.

## 3. Which micro-op is lost, per FSM state

cm.push (rtl/ibex_compressed_decoder.sv:623-683):
- CmIdle with the cm.push at the input (:627-657): the first store (top register of rlist at sp offset 1,
  :634) is lost; cm_rlist is already decremented and cm_sp_offset set to 2 (:647-650, :653-655). The remaining
  stores and the sp decrement execute. Result: one register is not saved; sp and the other saves are correct.
- CmPushStoreReg (:659-671): the store of the register at the top of cm_rlist_q (:660) is lost when :661 fires; rlist and
  offset move on (:663-665). One register not saved; a later pop of that slot loads the stale word faithfully, so the
  wrong register value surfaces at the pop although the loss happened at the push.
- CmPushDecrSp (:673-681): the `addi sp, sp, -adj` micro-op (:675) is lost and the FSM returns to CmIdle
  (:679). The buffer still holds the cm.push (section 2), so the next cycle restarts the expansion at :627: every
  store is issued a second time at the same addresses (sp has not moved), then the sp decrement executes. Result:
  architecturally correct memory and sp, but every store of that push appears twice on the bus and on RVFI. This
  is the "first push counted with extra stores" symptom of the reproduction.

cm.pop / cm.popret / cm.popretz (:686-774):
- CmIdle (:693-724): the load of the top register (:702) is lost; rlist and offset move on (:715-717). That
  register keeps its old value: an architectural error (no register-file write, no LSU request, no RVFI record).
- CmPopLoadReg (:726-738): the load of the register at the top of cm_rlist_q (:725) is lost when :726 fires. Same effect: one
  register is not restored. Several insertions during one long pop lose several registers, which is the
  reproduction's pattern of absent loads for a subset of the list.
- CmPopIncrSp (:740-756), plain cm.pop: the `addi sp, sp, +adj` (:740-742) is lost and the FSM returns to
  CmIdle (:750-752). The expansion restarts at :693 with sp unchanged: all loads are repeated from the same
  addresses (same values, so registers end correct), then sp is incremented once. Extra load records, correct
  state.
- CmPopIncrSp for cm.popret / cm.popretz: the FSM moves to CmPopRetRa / CmPopZeroA0 (:747-748) and the sp
  increment is lost, but the expansion does not restart yet; the ret (or the a0 zeroing then ret) executes with
  sp NOT incremented. Result: the return happens with a stale sp: an architectural error visible after the pop.
- CmPopZeroA0 (:758-763): `li a0, 0` (:758) is lost, ret follows; a0 keeps the callee's value.
- CmPopRetRa (:765-771): the `ret` (:766) is lost, the FSM returns to CmIdle
  (:770) and the expansion restarts
  at :693 while sp has ALREADY been incremented by the executed CmPopIncrSp: every load is repeated from
  sp + adj + offset, i.e. from above the frame, and the registers receive whatever lies there (the x18 = 800003ff seen in an earlier, unretained run of
  gen_zcmp_directed.S with dummy insertion enabled, whose cm.popret tail at pc 0x8000040a hit this case, is a
  return-address-like value read from above the frame; that exact value is not in a retained artifact; the retained red-by-design run lockstep_zcmp_dummy_popret
  (dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l7_lockstep_zcmp_dummy_popret_{run_header.txt, stdout_excerpt.log,
  verdict.txt}; 9408 UVM_ERROR rows by the excerpt header's grep count, first 12 kept) witnesses the double sp increment of this
  replay, not the above-frame register corruption: at order 38, on a ret micro-op, only x2 diverges (model 800003b0, DUT
  800003d0, one stack frame too far); the register values read from above the frame are not among the kept rows; the per-row
  mapping is tb-infra's, as for the plain-pop run; the x18 = 00000000 of the retained gen_zcmp_dummy_directed.S
  run is NOT this case, that program has no popret, see section 6), then sp is incremented a second time and the ret
  executes. This is the only path that corrupts registers that were loaded correctly the first time.

cm.mvsa01 / cm.mva01s (:777-830): a dummy in CmIdle (:791 / :819) loses the FIRST move; the FSM proceeds to
CmMvSecondReg, the second move executes with the LAST tag, the FSM idles and fetch_ready releases the buffer, so
there is no replay: the first destination (r1s' for cm.mvsa01, a0 for cm.mva01s) stays permanently unwritten, an
architectural error. A dummy in CmMvSecondReg (:798 / :826) loses the SECOND move; the FSM returns to idle while
the buffer still holds the halfword (LAST is set in the same cycle as the stall), so the pair is replayed from the
first move: benign for both instructions, the first move repeats with the same operands and the second then
executes. Not part of the B8 reproduction; listed because the same mechanism applies.

## 4. Register-file write versus RVFI record

- The lost micro-op never reaches ID (section 2), so there is no LSU request, no register-file write and no RVFI
  record. The absence on RVFI is faithful: the loads of the missing registers did not happen. This is unlike
  B13, where the write happens and only the exported value is wrong.
- The dummy instruction itself writes x0 (its rd field is 5'h00, rtl/ibex_dummy_instr.sv:144); with
  DummyInstructions the register file keeps a real x0 flop for it (rtl/ibex_register_file_ff.sv:159, :162, :173
  and :282-294) that reads as zero for real instructions. The dummy therefore changes no architectural register;
  it is excluded from RVFI (rtl/ibex_core.sv:1864, order held :1905) but NOT from minstret: instr_perf_count_id_o
  (rtl/ibex_id_stage.sv:1218-1220) has no dummy term, the WB stage latches it unconditionally into wb_count_q
  (rtl/ibex_wb_stage.sv:150, :169) and perf_instr_ret_wb (:208-209) drives instr_ret_i into mhpmcounter_incr[2]
  (rtl/ibex_core.sv:1549, rtl/ibex_cs_registers.sv:1588), so every dummy increments minstret while rvfi_order
  stands still; a lock-step model must expect minstret minus rvfi_order to grow by one per dummy. The damage to
  the program is entirely the discarded micro-op.
- The replayed micro-ops are real: each repeated store or load is issued on the data bus and produces an RVFI
  record with the expansion tags of its position (rtl/ibex_core.sv:2275-2280: expanded_insn_valid on every
  micro-op, expanded_insn_last on the LAST one). The duplicated records are therefore faithful too; a lock-step
  model that counts records per cm.* sees more than the list length.

## 5. Secondary exposure created by the same mechanism (not reproduced; stated from the RTL)

- The dummy in ID carries the INSTR_NOT_EXPANDED tag (rtl/ibex_if_stage.sv:528). The controller's debug gates hold an
  expansion together while the ID instruction is tagged EXPANDED or COMMIT (rtl/ibex_controller.sv:474-477), but
  handle_irq is gated only on the COMMIT tag (:498-500): by design an interrupt may be taken between any two
  micro-ops except after a COMMIT-tagged one: the sp increment (CmPopIncrSp, rtl/ibex_compressed_decoder.sv:744), li a0, 0 (CmPopZeroA0, :760)
  and the first move of cm.mvsa01 / cm.mva01s (:790, :818); the entry
  flushes the FSM (flush_expanded, section 2) with mepc at the cm.* PC and the expansion restarts from scratch
  after mret, which is idempotent because the sp update is the last micro-op (push) or COMMIT-protected (pop).
  The dummy changes two things. For interrupts the new exposure is only the COMMIT window: a dummy that displaces
  the micro-op following a COMMIT-tagged one (the ret of cm.popret; li a0, 0 or the ret of cm.popretz; the second
  move of cm.mvsa01 / cm.mva01s) sits in ID with NOT_EXPANDED, so an interrupt can be taken exactly where the tag
  was meant to forbid it. For the pop family sp is already incremented, and after mret the expansion restarts and
  repeats the loads from above the frame, the same corruption as the CmPopRetRa replay in section 3; for the move
  pair the restart repeats the first move with unchanged operands and is benign, as in section 3. For debug requests the exposure is at every micro-op position: the
  dummy's NOT_EXPANDED tag opens the debug gates (:474-477) that otherwise block entry for the whole expansion,
  dpc points at the cm.* PC, and the expansion restarts after dret with whatever stores, loads and sp updates had
  already executed.
- Both effects disappear with dummy_instr_en = 0 because insert_dummy_instr is then 0 (rtl/ibex_dummy_instr.sv
  :115) and the decoder's id_in_ready_i port equals the ID stage's readiness.

## 6. What the reproducer should observe (RTL-level signature)

- Cycle of insertion: if_stage insert_dummy_instr = 1 with compressed decoder cm_state_q != CmIdle or a cm.*
  halfword at its input, and cm_state_d != cm_state_q, cm_rlist_d != cm_rlist_q or cm_sp_offset_d != cm_sp_offset_q in that cycle (the FSM moves
  while instr_rdata_id loads the dummy).
- Assertion opportunity for the DV side (no RTL change): "if_id_pipe_reg_we && insert_dummy_instr |-> cm_state_d == cm_state_q &&
  cm_rlist_d == cm_rlist_q && cm_sp_offset_d == cm_sp_offset_q" (the qualifier matters: insert_dummy_instr does
  not depend on fetch_valid, and the CmIdle branch computes cm_rlist_d from instr_i even when nothing valid is
  there; at the decoder the equivalent qualifier is valid_i && id_in_ready_i) fails on every B8 event; the existing IbexPushPopFSMStable (rtl/ibex_compressed_decoder.sv
  :937) does not catch it because valid_i is high during the insertion.

- Reproduction status (tb-infra's row mapping of the retained run of dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_directed.S,
  four cm.push / cm.pop pairs with rlist 4 / 8 / 12 / 15, plain cm.pop only, dummy_instr_mask 0, reported 2026-09-03;
  the mapping is dv/auto_dv/evidence/gen_b8_row_mapping.md, tally table at its lines 37-45): all 27
  comparator rows map to a section-3 case; they summarise 33 lost micro-ops, one row covering several losses.
  Tally of lost micro-ops: CmIdle first store lost 2, CmPushStoreReg store lost 11,
  CmPushDecrSp addi lost with full replay 2, CmIdle first load lost 2, CmPopLoadReg load lost 13, CmPopIncrSp addi
  lost on a plain cm.pop with full replay 3; no popret / popretz / move case in that program. Every wrong register
  value in that run is a lost store leaving a slot stale and a faithful later load of it, or a lost load leaving the
  register unwritten (x18 = 00000000: push rl8 lost its s2 store in CmPushStoreReg in both passes, slot 0x80000228
  stayed stale, pop rl8 loaded it faithfully); no load in that run reads above the frame. Consecutive losses occur
  (pop rl12 lost s0, ra and the addi back to back) because the threshold is lfsr.cnt masked by {dummy_instr_mask,
  ones} (rtl/ibex_dummy_instr.sv:97), so with mask 0 a threshold of 0 right after an insertion inserts again. The
  CmPopRetRa replay is retained as lockstep_zcmp_dummy_popret (section 3 names the logs; red by design, 9408 UVM_ERROR rows
  by grep count): order 38 shows sp one frame too high on the ret micro-op (the double increment); order 46 shows "model wrote
  3 registers, dut 2" and "model wrote x10/00000000, dut did not", the lost li a0, 0 of a popretz (CmPopZeroA0 case), while its
  x2 and load-address mismatches are the same +0x20 sp offset inherited from order 38 (the DUT's push at order 41 stored to
  800003cc), not a second loss. The x18 = 800003ff value itself is only in the unretained run named in section 3.
- Assertion status: the TB-side assertion of section 6 is not built; LOG-067 rules it a probe bind behind a knob, tb-infra's
  next touch.

## 7. Anchors table

| Fact | Anchor |
|---|---|
| FSM readiness input lacks the dummy stall | rtl/ibex_if_stage.sv:492-493 |
| Dummy replaces the micro-op at the IF/ID register | rtl/ibex_if_stage.sv:526-530, :570, :587, :602-612 |
| Prefetch buffer held during insertion and expansion | rtl/ibex_if_stage.sv:535, :791-793, :808-809 |
| FSM advance points | rtl/ibex_compressed_decoder.sv:641, :653, :661, :676, :709, :718, :726, :745, :761, :767, :791, :798, :819, :826 |
| FSM reset only on PC_EXC | rtl/ibex_if_stage.sv:483; rtl/ibex_compressed_decoder.sv:885-889 |
| Insertion decision and per-micro-op counting | rtl/ibex_dummy_instr.sv:103-104, :115 |
| Dummy writes x0 only | rtl/ibex_dummy_instr.sv:144; rtl/ibex_register_file_ff.sv:159-173, :282-294 |
| Dummy excluded from RVFI | rtl/ibex_core.sv:1864, :1905 |
| Micro-op tags on RVFI | rtl/ibex_core.sv:2264-2280 |
| Interrupt / debug gates keyed on the tag | rtl/ibex_controller.sv:474-477, :498-500 |
| Known-interaction hint in the IF assertion | rtl/ibex_if_stage.sv:664-669 |
