# Critic verdict: T-102b (commit 50256f0, tb-infra), light check of the answers to gen_critic_tb_t102.md L-1 and M-1a

Artifacts at commit 50256f0: dv/auto_dv/env/gen_rvfi_pkg.sv (insn_len, mret/dret and trap-record C-1 compares, sync
comment), dv/auto_dv/isa/gen_isa_shim.cc (cpuctrlsts bits 6/7 from the model's traps), gen_ut_isa_shim.cc section 7,
dv/auto_dv/docs/gen_component_api_scoreboard.md (:59-62 consistency-compare paragraph), dv/auto_dv/mutations/gen_mut_t102.md
(P10, P11, out-of-tree rule), dv/auto_dv/evidence/gen_critic_response_tb_t102.md (31 lines, rows TW-/CR-/OR-/RA-),
gen_tdd_t102.md (close-out and the stale-image disclosure), retained logs gen_tdd_logs/{lockstep,mutations,export}/gen_close3_*
and gen_t102_P10_* / P11_*. Date: 2026-09-03T12:30Z   Role: Critic. The cross-model artifact of this commit was not read before this
verdict was written; section 4 is added after reading it.

CRITIC VERDICT: REQUEST-CHANGES on one medium (a false-miss path in the new trap-record compare for Zcmp records); L-1
and M-1a of my T-102 verdict are otherwise closed as asked.

## 1. Closed

- L-1 (C-1 convention check). isa_pc_next now checks `pc_wdata == pc_rdata + insn_len(insn)` on mret/dret records and on
  trap records other than fetch faults (cause 1), with insn_len 4 for a 32-bit encoding and 2 for a 16-bit one; the
  redirect target stays under isa_pc on the next record. P11 (mret pc_wdata compared off by 4) FAIL 100 under
  +gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_pc_next=1, ablation PASS; P10 (the record after an mret compared with pc + 4,
  a wrong redirect target) FAIL 100 under isa_pc, ablation PASS: the Orchestrator's requested target-corruption mutation.
  Both built out of tree (gen_t102_P10/P11_oot_compile.log; the batch log prints the shared tree's gen_rvfi_pkg.sv sha256
  unchanged), which is the rule I asked for after LOG-017; P1..P9 are disclosed as having run under the older
  announce-and-revert rule.
- M-1a (documentation half). gen_component_api_scoreboard.md:59-62 and the comment at the sync in gen_rvfi_pkg.sv state that
  isa_rd on cycle, mhpmcounterN and cpuctrlsts bit 8 is a CONSISTENCY compare (record value == read value), not an
  independent check, and name the owners: ctr_mcycle / ctr_minstret / ctr_hpm_exact / ctr_hpm_bound (step 2d, not built)
  and the scrkey_proto status row (not built). M-1b/c (the checkers themselves) stay OWED to tb-infra, outside this check.
- cpuctrlsts bits 6/7 (rtl-arch R6). The shim sets sync_exc_seen on a synchronous exception (cause bit 31 clear, debug
  entry excluded), double_fault_seen when a second one arrives while set, and clears sync_exc_seen on mret with
  double_fault_seen sticky; this follows the model's own traps, not the record, so it is a real expectation (matches
  rtl/ibex_cs_registers.sv:935-943 set and :964-965 clear). Unit test section 7 checks the three states.
- Close-out: boot_zc, lockstep_zc, lockstep_s7, export_zc and the four batch-1 tests PASS on the rebuilt tree (records
  119 / 260 / 5187 / 7965, mismatches 0). The stale-image first attempt (a Test Writer generator edit changed the images;
  6 fire-check failures on the Python side, UVM_ERROR 0) is retained as gen_close3_staleimage_* and disclosed.

## 2. M-1 (medium): insn_len misreads Zcmp micro-op records

- insn_len(insn) decides 4 or 2 from insn[1:0] of rvfi_insn. That is right for ordinary and compressed instructions
  (rtl/ibex_core.sv:2263-2265 keeps the 16-bit form for a compressed instruction that is NOT expanded) and for c.ebreak
  (zero-extended halfword). It is wrong for Zcmp micro-op records: rtl/ibex_core.sv:2266 puts the 32-bit EXPANSION in
  rvfi_insn for expanded micro-ops (plan C-12), so insn[1:0] is 2'b11 and insn_len returns 4, while the Zcmp encoding is
  16 bits and pc_if is pc + 2.
- Where it fires: the new trap-record compare (`trap && cause != 1 && t.pc_wdata != t.pc_rdata + insn_len(t.insn)`) runs on
  the LAST micro-op record of a sequence (the earlier ones fold and return at :259). A cm.push whose last store faults
  (PMP or bus error), or a cm.pop / cm.popret whose load faults, is a trap record with pc_wdata = pc + 2 and the compare
  expects pc + 4: a false isa_pc_next miss on legal DUT behaviour. Latent today (no retained run traps inside a Zcmp
  sequence; lockstep_zc has traps=0), but the plan's Zcmp fault items will hit it.
- Required: take the length from the sequence's own encoding, `t.ext_exp_valid ? 2 : insn_len(t.insn)` (or
  insn_len({16'h0, t.ext_exp_insn}) when ext_exp_valid), with one unit or directed case: a Zcmp store faulting on the last
  micro-op, expected pc_wdata = pc + 2, seen failing before the fix and passing after.
- Open question, not a finding of this landing: a trapping NON-last micro-op record folds and returns before any compare
  (:259). Whether the DUT marks a trapping micro-op as ext_expanded_insn_last, and how the fold treats a sequence cut short
  by a trap, is untested; the first Zcmp-fault test decides it, and the comparator should at least assert that a trapping
  record is never swallowed by the fold.

## 3. Lows

- L-1 The trap-record rule excludes only cause 1. An instruction access fault is the one case with no fetched length; the
  exclusion is right, but a comment naming the RVFI value the DUT does report there (pc_if of the faulting fetch) would
  let a later reader re-check it.
- L-2 P1's message text quirk is recorded (unchanged, harmless).

## 4. After reading the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-4c4b9b8d-50256f09.md, APPROVE-WITH-CHANGES), 2026-09-03T12:30Z

- Its medium is the same defect as my M-1 (insn_len on Zcmp last-micro-op records reads the expanded encoding), found
  independently on both sides; the required change above stands.
- Two of its lows I adopt after checking: (a) the RTL sets sync_exc_seen only when the exception is not a debug-mode
  save and the core is not already in debug mode (rtl/ibex_cs_registers.sv:910 `if (debug_csr_save_i)` ... :918 `else if (!debug_mode_i)`, so a
  debug-mode save and an exception inside debug mode both bypass the set; confirmed), while the shim excludes only the debug ENTRY case, so an exception taken while already in
  debug mode sets the model's bit 6 and not the DUT's: a false isa_rd miss on a later cpuctrlsts read in a debug test.
  Add the in-debug-mode exclusion (L-3). (b) The section-7 unit-test green ("159 OK") has no retained log under
  gen_tdd_logs/isa_shim/ at this commit; my section 1 statement rests on the source of the checks, not on a run. Retain
  the green log (L-4, same rule as every other claimed run).
- Its remaining lows (the stale XM-T102 "pending" row, the reused version label 4c, the missing 4a row for bits 6/7, the
  re-typed 0xC0/0x40/0x80 masks in the unit test) are bookkeeping I did not raise and do not dispute.
