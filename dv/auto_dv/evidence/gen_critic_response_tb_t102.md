# Response file: T-102 lock-step comparator and shim conventions (tb-infra, 2026-09-03)

Answers, one row per finding, to: the Test Writer's batch-1 findings (TW-, message of 10:56Z), the Critic's T-102 verdict
(CR-, dv/auto_dv/docs/gen_critic_tb_t102.md, APPROVE with one medium), the Orchestrator's rule (OR-, 11:20Z and the
d0c0d15 landing note), and rtl-arch's RTL facts (RA-, dv/auto_dv/evidence/gen_t102_rtl_facts.md rows R1..R8). Code state:
d0c0d15 (T-102) plus the follow-up pass on disk after 4c4b9b8 ("this landing"). Status words: FIXED (code and retained run),
ADDRESSED (text), OWED (named owner and landing), NOTED. Evidence: dv/auto_dv/evidence/gen_tdd_t102.md,
dv/auto_dv/mutations/gen_mut_t102.md, retained logs under dv/auto_dv/evidence/gen_tdd_logs/{isa_shim,lockstep,mutations}/.

| Row | Finding | Status | Where |
|---|---|---|---|
| TW-1 | isa_pc_next fires on every mret record (pc_wdata is pc + 4, C-1) | FIXED (d0c0d15 skipped the records; this landing compares them, see OR-1) | gen_rvfi_pkg.sv: on mret/dret records `pc_wdata == pc_rdata + insn_len`; the target is checked by isa_pc on the next record; P2 (skip removed at d0c0d15), P10, P11. |
| TW-2 | isa_prv compares the post-step privilege with rvfi_mode (the executing privilege) | FIXED (d0c0d15) | step record `prv_before`; compare `prv_b[1:0] != t.mode`; P1 caught (314), ablation PASS; unit test section 6. |
| TW-3 | shim gaps: mstatus XS/SD, cpuctrlsts bit 8, tdata1 reset, marchid, mcycle sync never called, mhpmcounter, mhpmevent | FIXED (d0c0d15; bits 6/7 this landing) | views and syncs in gen_isa_shim.cc (Section 3 of the transcript); P3..P7, P9; unit test sections 5 and 7. |
| TW-4 | C5.5 references beyond grev/gorc | FIXED (d0c0d15) | gen_isa_exec_reference covers pack/packu/packh, slo/sro(i), shfl/unshfl(i), xperm.n/b/h, cmov/cmix, fsl/fsr/fsri, bfp, crc32/crc32c; rs3 compared; unit vectors (41 red, then green); P8. |
| CR-M1a | scoreboard API and comment must say isa_rd on cycle / mhpmcounterN / cpuctrlsts bit 8 is a consistency compare and name the owning checker | ADDRESSED (this landing) | gen_component_api_scoreboard.md sync paragraph; gen_rvfi_pkg.sv comment at the sync: counters -> ctr_mcycle / ctr_minstret / ctr_hpm_exact / ctr_hpm_bound (step 2d), bit 8 -> scrkey_proto status row. |
| CR-M1b | scrkey_proto status row (record bit 8 versus the driven value at the ID-exit sample) before a cpuctrlsts read is credited | OWED: tb-infra, with the scramble-key responder checker landing (step 2b/2c) | not built; nothing credits bit 8 reads until then. |
| CR-M1c | ctr_* checkers before counter reads are credited | OWED: tb-infra, step 2d | not built. |
| CR-L1 | add the C-1 convention check on mret/dret records under isa_pc_next | FIXED (this landing) | `pc_wdata == pc_rdata + insn_len(insn)` (2 for a compressed encoding, rtl-arch R1); also on trap records except fetch faults (cause 1); P11 caught (100), ablation PASS. |
| CR-L2 | P1's message prints prv_b while the compare used prv | NOTED | the record says so; harmless. |
| CR-L3 | reference functions unit-vectored only; RTL-level mutation halves owed (D-3) | OWED: Test Writer TP-BIT-022..033 for the DUT exercise; RTL-level halves per isa id with the purpose-2 runs | transcript Section 6. |
| OR-1 | do not skip isa_pc_next on mret/dret: compare pc + insn_length and verify the redirect through the next record's pc_rdata against the model; add a mutation that corrupts the mret target | FIXED (this landing) | compare as CR-L1; the next record's isa_pc is the target check (model pc after mret vs pc_rdata); P10: the record after an mret reported with pc + 4 -> isa_pc FAIL (100), ablation PASS (out of tree). |
| RA-R1 | mret/dret pc_wdata = pc_if; pc + 2 for c.ebreak | FIXED | `insn_len` from insn[1:0] (RVFI reports the compressed form); trap records use the same rule. |
| RA-R2 | rvfi_mode is the pre-step privilege (ID-done capture) | FIXED | prv_before (TW-2). |
| RA-R3 | marchid 0x16 | FIXED | `GEN_CSR_MARCHID_VALUE` derived from ibex_pkg; P3. |
| RA-R4 | mhpmeventN = 1 << (N-3) for N 3..12, 0 beyond, read-only | FIXED | gen_const_csr_t rows; unit test. |
| RA-R5 | tdata1 fixed view + execute bit; tdata1/tdata2 writable in debug mode only | FIXED | gen_trigger_view_t; P9; unit test. |
| RA-R6 | cpuctrlsts bit 8 per-cycle status; bits 6/7 hardware-set (a mask alone does not model them) | FIXED (bit 8 at d0c0d15 from the RVFI ext field; bits 6/7 this landing) | the shim sets sync_exc_seen on a synchronous exception, double_fault_seen on a second one while set, clears sync_exc_seen on mret (rtl/ibex_cs_registers.sv:935-943, :964-965); unit test section 7 (written with the implementation, not red-first: its red is R6's caution). |
| RA-R7 | mstatus reads TW/MPRV/MPP/MPIE/MIE only; XS/SD read 0 | FIXED | gen_mstatus_view_t masks XS and SD on read and write; P7. |
| RA-R8 | HPM counters not ISA-derivable; counters 8, 11, 12 unsafe for exact compare (BUG-09) | ADDRESSED | the sync is a follow, not a check (CR-M1a); no equality is asserted on any counter's count; the counter checkers own them. |
| XM-T102 | cross-model post-execution review of d0c0d15 | pending (artifact not yet on disk) | rows added when it lands. |
