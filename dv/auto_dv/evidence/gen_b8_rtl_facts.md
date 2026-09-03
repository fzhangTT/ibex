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
  `dummy_instr_en_i & (dummy_cnt_q == dummy_cnt_threshold)` (rtl/ibex_dummy_instr.sv:112), and the counter
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
  offset move on (:663-665). One register not saved.
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
  sp + adj + offset, i.e. from above the frame, and the registers receive whatever lies there (the reproduction's
  x18 = 800003ff / 00000000 instead of 33333333 is this case), then sp is incremented a second time and the ret
  executes. This is the only path that corrupts registers that were loaded correctly the first time.

cm.mvsa01 / cm.mva01s (:777-830): the first move is lost in CmIdle (:791 / :819 advance to CmMvSecondReg) or
the second is lost in CmMvSecondReg (:798 / :826 return to idle, no restart because the second move is the LAST
micro-op and the FSM is idle while the buffer still holds the instruction: the whole pair is replayed, which is
benign for cm.mva01s and, for cm.mvsa01 with the first move lost, leaves one sreg unwritten until the replay
writes both). Not part of the B8 reproduction; listed for completeness of the mechanism.

## 4. Register-file write versus RVFI record

- The lost micro-op never reaches ID (section 2), so there is no LSU request, no register-file write and no RVFI
  record. The absence on RVFI is faithful: the loads of the missing registers did not happen. This is unlike
  B13, where the write happens and only the exported value is wrong.
- The dummy instruction itself writes x0 (its rd field is 5'h00, rtl/ibex_dummy_instr.sv:144); with
  DummyInstructions the register file keeps a real x0 flop for it (rtl/ibex_register_file_ff.sv:159, :162, :173
  and :282-294) that reads as zero for real instructions. The dummy therefore changes no architectural register;
  it is excluded from RVFI (rtl/ibex_core.sv:1864, order held :1905) and from the retired-instruction counters
  (rtl/ibex_id_stage.sv:1218-1220 excludes expanded non-last micro-ops; the dummy is excluded through
  dummy_instr_id in cs_registers). The damage is entirely the discarded micro-op.
- The replayed micro-ops are real: each repeated store or load is issued on the data bus and produces an RVFI
  record with the expansion tags of its position (rtl/ibex_core.sv:2275-2280: expanded_insn_valid on every
  micro-op, expanded_insn_last on the LAST one). The duplicated records are therefore faithful too; a lock-step
  model that counts records per cm.* sees more than the list length.

## 5. Secondary exposure created by the same mechanism (not reproduced; stated from the RTL)

- The dummy in ID carries the INSTR_NOT_EXPANDED tag (rtl/ibex_if_stage.sv:528). The controller's interrupt and
  debug gates only hold an expansion together while the ID instruction is tagged EXPANDED or COMMIT
  (rtl/ibex_controller.sv:474-477, :498-500), so an interrupt or debug request can be taken on the dummy in the
  middle of a cm.* sequence. The entry flushes the FSM (flush_expanded, section 2), mepc/dpc point at the cm.*
  PC, and after the return the expansion restarts from the beginning with whatever stores/loads/sp updates had
  already executed. For a pop whose sp increment had executed this is the same corrupting replay as the
  CmPopRetRa case above.
- Both effects disappear with dummy_instr_en = 0 because insert_dummy_instr is then 0 (rtl/ibex_dummy_instr.sv
  :112) and the decoder's id_in_ready_i port equals the ID stage's readiness.

## 6. What the reproducer should observe (RTL-level signature)

- Cycle of insertion: if_stage insert_dummy_instr = 1 with compressed decoder cm_state_q != CmIdle or a cm.*
  halfword at its input, and cm_state_d != cm_state_q or cm_rlist_d != cm_rlist_q in that cycle (the FSM moves
  while instr_rdata_id loads the dummy).
- Assertion opportunity for the DV side (no RTL change): "insert_dummy_instr |-> cm_state_d == cm_state_q &&
  cm_rlist_d == cm_rlist_q" fails on every B8 event; the existing IbexPushPopFSMStable (rtl/ibex_compressed_decoder.sv
  :937) does not catch it because valid_i is high during the insertion.

## 7. Anchors table

| Fact | Anchor |
|---|---|
| FSM readiness input lacks the dummy stall | rtl/ibex_if_stage.sv:492-493 |
| Dummy replaces the micro-op at the IF/ID register | rtl/ibex_if_stage.sv:526-530, :570, :587, :602-612 |
| Prefetch buffer held during insertion and expansion | rtl/ibex_if_stage.sv:535, :791-793, :808-809 |
| FSM advance points | rtl/ibex_compressed_decoder.sv:641, :653, :661, :676, :709, :718, :726, :745, :761, :767, :791, :798, :819, :826 |
| FSM reset only on PC_EXC | rtl/ibex_if_stage.sv:483; rtl/ibex_compressed_decoder.sv:885-889 |
| Insertion decision and per-micro-op counting | rtl/ibex_dummy_instr.sv:103-104, :112 |
| Dummy writes x0 only | rtl/ibex_dummy_instr.sv:144; rtl/ibex_register_file_ff.sv:159-173, :282-294 |
| Dummy excluded from RVFI | rtl/ibex_core.sv:1864, :1905 |
| Micro-op tags on RVFI | rtl/ibex_core.sv:2264-2280 |
| Interrupt / debug gates keyed on the tag | rtl/ibex_controller.sv:474-477, :498-500 |
| Known-interaction hint in the IF assertion | rtl/ibex_if_stage.sv:664-669 |
