# RVFI facts: rvfi_order skips one index at an ebreak that enters debug mode (rtl-arch)

Owner: rtl-arch. Written 2026-09-08T02:52Z from the RTL in this clone, read at 2f46b1d and verified at HEAD
f85c6bb with `git diff 2f46b1d..f85c6bb -- rtl/` empty, so no cited line moved (rtl/ibex_core.sv,
rtl/ibex_controller.sv, rtl/ibex_id_stage.sv), plus the RVFI definition in this clone
(tools/specs/riscv-formal/docs/source/rvfi.rst, an allowed untracked local copy, docs/dv/FENCE.md).
Configuration: opentitan, so WritebackStage 1 and the two-stage RVFI tracking pipeline.

Scope: the Test Writer's observation of 2026-09-08, that rvfi_order skips one value at a debug entry an
instruction causes and that the skipped instruction emits no record at all. Asked of this role: which term
lets the order counter advance for an instruction that produces no record, and the classification. RTL is
read-only; no fix. The classification recommendation is the DV Lead's to accept.

## 1. Verdict

An ebreak that enters debug mode consumes one rvfi_order index and emits no record. It is a genuine RVFI
interface violation, not an RTL-defined behaviour a checker should be taught to tolerate, because the RVFI
definition forbids gaps in as many words: "The `rvfi_order` field must be set to the instruction index. No
indices must be used twice and there must be no gaps." (tools/specs/riscv-formal/docs/source/rvfi.rst:41-42).

The cause is that the index and the emission are gated by two DIFFERENT signals, and for this one class
they disagree. Architectural state is unaffected: the ebreak does not retire, dpc points at it and it
re-executes on resume, so having no record for it is right. What is wrong is that an index was spent on it.

## 2. The two signals, with every gating term

The index advances under `rvfi_id_done`:

    assign rvfi_id_done = instr_id_done | (id_stage_i.controller_i.rvfi_flush_next &
                                           id_stage_i.controller_i.id_exception_o &
                                           ~id_stage_i.controller_i.wb_exception_o);
                                                                          (rtl/ibex_core.sv:1851-1853)
    assign rvfi_stage_order_d = dummy_instr_id ? rvfi_stage_order[0] : rvfi_stage_order[0] + 64'd1;
                                                                                              (:1905)
          if (rvfi_id_done) begin                                                             (:2072)
            rvfi_stage_trap[i]  <= rvfi_trap_id;                                              (:2074)
            rvfi_stage_order[i] <= rvfi_stage_order_d;                                        (:2076)

The record is EMITTED only under `rvfi_wb_done`:

    assign rvfi_stage_valid_d[0] = (rvfi_id_done & ~dummy_instr_id) |
                                   (rvfi_stage_valid[0] & ~rvfi_wb_done);              (:1864-1865)
    assign rvfi_stage_valid_d[1] = rvfi_wb_done;                                              (:1868)
    assign rvfi_wb_done = rvfi_stage_valid[0] & (instr_done_wb | rvfi_stage_trap[0]);         (:1890)

and the deliberate term that makes them disagree is the ebreak exclusion in the trap bit:

    assign rvfi_trap_id = id_stage_i.controller_i.id_exception_o &
      ~(id_stage_i.ebrk_insn & id_stage_i.controller_i.ebreak_into_debug);              (:1885-1886)

## 3. The sequence, cycle by cycle

Cycle A, the ebreak valid in ID with the controller in DECODE and dcsr.ebreakm set:

- `ebrk_insn = ebrk_insn_i & instr_valid_i` is 1 (rtl/ibex_controller.sv:231), so
  `exc_req_d = (ecall_insn | ebrk_insn | illegal_insn_d | instr_fetch_err | ...) & (ctrl_fsm_cs != FLUSH)`
  is 1 (:268-270, the state being DECODE) and `id_exception_o = exc_req_d` is 1 (:278).
- `special_req_pc_change = mret_insn | dret_insn | exc_req_d | exc_req_wb` is 1 (:290) so
  `special_req` is 1 (:293), which sets `retain_id = 1'b1` (:668) and takes `ctrl_fsm_ns = FLUSH` (:677)
  once `ready_wb_i | wb_exception_o` (:676). `rvfi_flush_next = (ctrl_fsm_ns == FLUSH)` is therefore 1
  (:1122).
- `instr_id_done_o = en_wb_o & ready_wb_i` is 0 (rtl/ibex_id_stage.sv:1130): the instruction is retained,
  not passed to WB. So the FIRST term of :1851 is 0 and the SECOND carries `rvfi_id_done` to 1.
- `rvfi_trap_id` is 0 by :1885-1886, because this is exactly an `ebrk_insn` with `ebreak_into_debug`.
- At the edge: `rvfi_stage_order[0]` takes the incremented index (:1905, :2076), `rvfi_stage_trap[0]`
  takes 0 (:2074) and `rvfi_stage_valid[0]` becomes 1 (:2069 from :1864).

Cycle B onward, FLUSH then DBG_TAKEN_ID:

- `rvfi_wb_done` is 0 (:1890): `instr_done_wb` never asserts for this instruction because it never entered
  WB, and `rvfi_stage_trap[0]`, the term that substitutes for a trap being tracked without a WB pass, was
  forced to 0 in cycle A.
- So `rvfi_stage_valid_d[0]` stays 1 through its second term (:1865) and `rvfi_stage_valid_d[1]` stays 0
  (:1868). Stage 0 holds a valid entry that can never be promoted, and nothing is output.

The next instruction to finish ID, which is the debug ROM's first:

- Its own `rvfi_id_done` rewrites EVERY stage-0 field unconditionally (:2072-2082) and takes the next index
  (:1905). The ebreak's held entry is overwritten and its index is gone.

Net effect: exactly one index consumed, no record, which is the gap the Test Writer measured.

## 4. Why the exclusion at :1885-1886 is not itself the defect

The exclusion is right in intent. The second term of `rvfi_id_done` exists to trace flushed instructions
that took a trap, as its own comment says (:1847-1850), and an ebreak that enters debug mode did not take
a trap: no mcause, no mepc, no vector. Setting `rvfi_trap_id` for it would emit a record claiming a trap
that did not happen, which is a worse defect than a gap.

The defect is the pairing. The index is spent under a condition that includes an instruction which will
neither retire nor be reported, while the RVFI definition ties the index to reported instructions with no
gaps. Either the index should not advance for this class, or the class should be reported; the RTL does
neither. This is the same shape as B13 and B18: the trace interface is wrong while execution and
architectural state are right.

## 5. The trigger-match half: NOT CONFIRMED, with the discriminator

The observation reported two gaps and attributed the second to the trigger-matched instruction. This note
does NOT confirm that, and the RTL argues against it:

- A trigger entry goes through DBG_TAKEN_IF, reached from DECODE only under
  `if (!stall && !special_req && !id_wb_pending)` (rtl/ibex_controller.sv:704 with :707), and
  `id_wb_pending = instr_valid_i | ~ready_wb_i` (:296). So the ID stage is EMPTY when a trigger entry is
  taken, and the matched instruction is still in the fetch stage, since `trigger_match` compares `pc_if_i`
  (rtl/ibex_cs_registers.sv:1872). An instruction that never entered ID never asserted `rvfi_id_done` and
  so never took an index.
- The second term of :1851 needs `rvfi_flush_next`, which is `ctrl_fsm_ns == FLUSH` (:1122). DBG_TAKEN_IF
  is not FLUSH, so that term is 0 on this path too.

So a trigger match should consume no index, and the second gap should have another cause. The reporter's
own control observation points the same way: the gaps were seen with no trigger armed. Two things settle
it from the export, and both are cheap for whoever holds it:

- Count the debug entries the program takes THROUGH AN EBREAK. Section 3 spends exactly one index per such
  entry, so that count should equal the number of gaps. A multi-entry debug ROM reached by an ebreak each
  time gives one gap per entry.
- For each gap, read the record AFTER it. An ebreak-caused gap is followed by the debug ROM's entry point,
  with the ebreak's own address left in dpc. If any gap is followed by something else, that one needs its
  own trace and this note does not cover it.

## 6. Consequences for the testbench and the plan

- The comparator's contiguity rule is CORRECT and should not be relaxed. the rule at `gen_rvfi_pkg.sv:142-143`, whose condition is
  `t.order != last_order + 64'd1`, requiring the index to increment by one per record, is what the RVFI definition requires (rvfi.rst:41-42), so an
  exemption for a debug entry would remove a rule that is catching a real interface violation. The right
  shape is the B13 and B18 one: the carrying test records the deviation rather than the checker tolerating
  it. Which of the two, an expected-fail entry or the pass-by-policy witness those two use, is the DV
  Lead's ruling.
- Recommended rating under gen_bug_log.md Section 0.2, for the DV Lead: P3. Only the trace interface is
  wrong; execution, architectural state, dpc and the debug entry itself are right, and the ebreak
  correctly does not retire. That is the same rating and the same reasoning as B13 and B18.

## 7. Anchors

| Fact | Anchor |
|---|---|
| The index advances under rvfi_id_done | rtl/ibex_core.sv:1851-1853, :1905, :2072, :2076 |
| The record is emitted only under rvfi_wb_done | rtl/ibex_core.sv:1864-1865, :1868, :1890 |
| The deliberate ebreak exclusion in the trap bit | rtl/ibex_core.sv:1885-1886 |
| Its stated intent | rtl/ibex_core.sv:1847-1850 |
| ebreak reaches id_exception and retains ID | rtl/ibex_controller.sv:231, :268-270, :278, :290, :293, :668, :676-677 |
| rvfi_flush_next is the FLUSH transition only | rtl/ibex_controller.sv:1122 |
| A retained instruction does not reach WB | rtl/ibex_id_stage.sv:1130 |
| A trigger entry requires an empty ID stage | rtl/ibex_controller.sv:296, :704, :707; rtl/ibex_cs_registers.sv:1872 |
| No gaps are permitted in the index | tools/specs/riscv-formal/docs/source/rvfi.rst:41-42 |
| The comparator rule this bears on | dv/auto_dv/env/gen_rvfi_pkg.sv:142-143 |
