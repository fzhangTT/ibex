# Bug log - Ibex core, opentitan configuration

Deliverable 7 (DV_prompt.txt Section 11). Owner: dv-lead; entries are opened by the DV Lead from the
feature list / reading report and rtl-arch's behaviour summaries (gen_behaviour_summaries.md Part A
BUG-01..05, kept as aliases). Version 1, 2026-09-03 06:58 UTC. Every entry is a CANDIDATE until a committed
reproducer log exists (status "candidate, reproducer pending"); DV never modifies RTL; a candidate is
removed from the pass gate only through a recorded owner ruling (DV_prompt.txt Section 10; owner
questions Q-004/Q-005 in dv/auto_dv/docs/gen_intervention_log.md).

Policy (dv_principles.md Section 4): where the RTL contradicts a specification, the checker follows the
specification and the carrying test-plan items are `expected-fail (Bn)`; where the RTL is spec-legal and
only the Ibex documentation disagrees, the checker follows the RTL and the item is
`pass (doc mismatch Dn)`.

B-versus-D criterion for a discrepancy between the RTL and the Ibex documentation only (no RISC-V specification text): it is
a doc defect (D) when the RTL behaviour is a self-consistent, timing-independent convention that the documentation
mis-describes (a value, an encoding, a count convention, a latency bound: D6 misaligned accesses counted once, D20
mhpmevent encoding, D21 NMI latency); it is a bug candidate (B) when the RTL behaviour depends on pipeline timing so the
same program yields different architectural results (B17: the branch count depends on whether a WB access is
outstanding), or when it violates a documented functional or security intent (B7 dummies in minstret, B16 rd written on
a bad first beat, B11: NumBranchesTaken counts an event the doc excludes, a not-taken branch, under one configuration,
which is a wrong event and not a convention, unlike D6 where the doc merely mis-states the RTL's uniform counting
convention for misaligned accesses). The checker follows the RTL for a D and the documentation for a B.

## 1. Bug candidates (RTL vs specification or documented intent)

### B1: dret into U-mode leaves mstatus.MPRV set
- Status: candidate, reproducer pending
- rtl-arch alias: BUG-06 (added by rtl-arch T-017; static confirmation against Sdext.adoc:202)
- Features: F-PRV-015 (canonical); aliases F-DBG-033, F-PMP-075
- Expected-fail TP items: TP-PRV-014, TP-DBG-038, TP-PMP-073
- RTL: rtl/ibex_cs_registers.sv:949-951 (csr_restore_dret_i restores priv_lvl only; compare mret :953-959 which clears MPRV when MPP != M)
- Specification / intent: riscv-debug-spec Sdext.adoc:202 (Resume: "If the new privilege mode is less privileged than M-mode, MPRV in mstatus is cleared")
- Notes: security-relevant: U-mode loads/stores then use MPP privilege for PMP
- Intended reproducer: M-mode: set PMP region denying U-mode data access to buffer X; set mstatus.MPRV=1, MPP=U; assert debug_req_i; in the debug program set dcsr.prv=U, dpc=U-code; dret; U-code loads X: RTL performs the load (MPRV still 1, MPP=U -> U privilege... no: MPRV=1 uses MPP=U; make the region deny U and allow M: then set MPP=M before dret) -> RTL: access checked at M privilege (MPRV=1, MPP=M) and succeeds; spec: MPRV cleared -> U privilege -> load access fault. Control: same with MPRV=0.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B2: mstatus.MPRV honoured for LSU PMP checks in debug mode although dcsr.mprven is hardwired 0
- Status: candidate, reproducer pending
- rtl-arch alias: BUG-01
- Features: F-DBG-055 (canonical); alias F-PMP-076
- Expected-fail TP items: TP-PRV-035, TP-DBG-060, TP-PMP-074
- RTL: rtl/ibex_cs_registers.sv:826 (dcsr_d.mprven = 0), :998 (priv_mode_lsu_o = mprv ? mpp : priv_lvl_q, no debug_mode term); consumer rtl/ibex_core.sv:1603-1604
- Specification / intent: riscv-debug-spec core_registers.xml dcsr.mprven: 0 = MPRV in mstatus is ignored in Debug Mode
- Notes: security-relevant
- Intended reproducer: PMP regions all OFF (M-mode allowed, U denied by MMWP=0 no-match rule); M-mode: mstatus.MPRV=1, MPP=U; assert debug_req_i; debug program executes lw from an address outside the DM window: RTL -> no data_req_o, PC -> DmExceptionAddr; spec -> load performed. Control: MPRV=0, load succeeds.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B3: tdata3 / mcontext / scontext / mscontext read 0 and ignore writes instead of trapping
- Status: candidate, reproducer pending
- rtl-arch alias: -
- Features: F-TRG-008 (canonical); alias in CSR part F-CSR-083 item
- Expected-fail TP items: TP-CSR-083, TP-TRG-008
- RTL: rtl/ibex_cs_registers.sv:648-663
- Specification / intent: riscv-isa-manual / riscv-debug-spec Sdtrig.adoc:370 ("Attempts to access an unimplemented Trigger Module Register raise an illegal instruction exception")
- Notes: Ibex doc (cs_registers.rst) documents read-0
- Intended reproducer: csrr t0, tdata3 (0x7A3) in M-mode: RTL returns 0 with no trap; spec expects illegal instruction (mcause 2). Repeat for 0x7A8, 0x5A8, 0x7AA.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B4: cm.mvsa01 with r1s' == r2s' executes (spec reserved encoding)
- Status: candidate, REPRODUCED by tb-infra (tb-infra landing 5, slice 3, committed a9b63ae: program dv/auto_dv/stim/gen_directed/gen_zcmp_mv_reserved_directed.S and the retained logs dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l5_lockstep_zcmp_mv_res_{run_header.txt,verdict.txt,stdout_excerpt.log,export.txt}; the verdict's first comparator row: isa_trap, dut retired while the model trapped (cause 2, tval 0xac22) at pc 80000094): the ISA model refuses the encoding (Spike require(r1s != r2s): illegal instruction, tval 0xac22) while Ibex executes it as two moves with the second winning; RTL cause stated by rtl-arch T-237, dv/auto_dv/evidence/gen_b4_rtl_facts.md at 3c3a96f (sha256 3b0f7aed4462; first landed ab3cb31, reviewed APPROVE-WITH-CHANGES at 5e05ad7): the cm.mvsa01 arm raises no illegal instruction, the only Zcmp encoding the decoder accepts that the specification reserves; RTL candidate; owner item: does Ibex's non-trapping execution of the reserved cm.mvsa01 encoding stand
- rtl-arch alias: T-237 (gen_b4_rtl_facts.md)
- Features: F-CMP-051
- Expected-fail TP items: TP-CMP-051
- RTL: rtl/ibex_compressed_decoder.sv:779-806; rtl-arch T-237, dv/auto_dv/evidence/gen_b4_rtl_facts.md at 3c3a96f (sha256 3b0f7aed4462; first landed ab3cb31, reviewed APPROVE-WITH-CHANGES at 5e05ad7): the cm.mvsa01 arm (:788-800) carries no illegal_instr_o term (the funct3-101 group's encoding-level illegal_instr_o assignments are the defaults :835, :839 and the push/pop reserved-rlist assignments :637 under the test :635 and :705 under :703; its configuration-level assignments :620, CHERIoT enable, and :843, RV32ZC without Zcmp, do not apply to this build); the first micro-op carries the COMMIT tag (:790), so the pair is atomic and the second write wins
- Specification / intent: tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1163 (norm:cm-mvsa01_res) "For the encoding to be legal r1s' != r2s'." and :1174 (norm:cm-mvsa01_op) "r1s' and r2s' must be different."; the reserved encoding has no defined behaviour, Ibex's choice is to execute it; the general reserved-encoding rule (rv32.adoc:124-130: behaviour UNSPECIFIED, a platform may require a trap) and Spike's require (tools/riscv-isa-sim/riscv/insns/cm_mvsa01.h:1-4) are quoted in the facts note Section 5
- Notes: low severity. DV Lead ruling B4-R1 (2026-09-03): the TB does not adopt the RTL behaviour as its reference before the owner rules (a shim modelling Ibex's execution of the reserved encoding refused); running the encoding with the comparators off refused; the witness bin CG-CMP-007.cr_insn_equal.cm_mvsa01_yes is TP-CMP-051's alone (expected-fail, own test): only the reserved encoding hits it and a pass test never executes that encoding under lock-step, so the TP-CMP-053 row of the trace CSV and the bin in gen_test_cmp_zcmp_basic's manifest (473 declared bins, gen_cmp_zcmp_mv_cg.cr_insn_equal.cm_mvsa01_yes) left together with the Test Writer's re-render (joint landing T-239 at 4a71798, LOG-036b)
- Intended reproducer: Assemble cm.mvsa01 with r1s'=r2s' via .insn/.2byte; RTL executes (final value = a1); spec expects reserved -> illegal (Ibex choice: no trap).
- Evidence: tb-infra landing 5, slice 3, committed a9b63ae (its review f2320ca is REQUEST-CHANGES on the mv sampler's sreg mapping, ablation and red-log retention, none of it touching these files; the re-review sha follows landing 6): program dv/auto_dv/stim/gen_directed/gen_zcmp_mv_reserved_directed.S and the retained logs dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l5_lockstep_zcmp_mv_res_{run_header.txt,verdict.txt,stdout_excerpt.log,export.txt}; the verdict's first comparator row: isa_trap, dut retired while the model trapped (cause 2, tval 0xac22) at pc 80000094; the lock-step comparator reports the trap mismatch (model illegal instruction, DUT two retiring moves)

### B5: dcsr.nmip hardwired 0 while an NMI can be pending in debug mode
- Status: candidate, reproducer pending
- rtl-arch alias: -
- Features: F-IRQ-037 (canonical)
- Expected-fail TP items: TP-DBG-021
- RTL: rtl/ibex_cs_registers.sv:825
- Specification / intent: tools/specs/riscv-debug-spec/xml/core_registers.xml:292-298 (nmip, access R: set when an NMI is pending; reliability implementation-dependent). The generated field table is absent from the clone but the XML source is on disk.
- Notes: low; read-only status field never reports
- Intended reproducer: Enter debug mode via debug_req_i; assert irq_nm_i; csrr dcsr in the debug program: bit 3 reads 0 (RTL); spec expects 1 while pending.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B7: Dummy instructions are counted in minstret and in mhpmcounter11/12 (mul/div wait)
- Status: candidate, reproducer pending
- rtl-arch alias: BUG-02
- Features: F-PMC-011 (canonical); alias F-DIT-018
- Expected-fail TP items: TP-PMC-013, TP-DIT-019
- RTL: rtl/ibex_id_stage.sv:1218-1220 (instr_perf_count_id_o has no dummy term), rtl/ibex_wb_stage.sv:150,169,208-209, rtl/ibex_cs_registers.sv:1588
- Specification / intent: doc/03_reference/security.rst:45 (dummies have no functional impact on processor state); priv spec: minstret counts retired instructions
- Notes: needs one directed simulation (static reading so far)
- Intended reproducer: csrw cpuctrlsts, 0x4 (dummy_instr_en, mask 0); csrr t0, minstret; 64 nops; csrr t1, minstret: doc predicts t1-t0 == 65; RTL gives 65 + number of dummies (compare against rvfi_order delta). Control: dummy_instr_en=0.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B8: Dummy instruction inserted mid-Zcmp sequence discards a micro-op or replays the expansion (reproduced; RTL cause stated)
- Status: candidate, REPRODUCED deterministically by tb-infra (tb-infra landing 4, T-205 slice 2, committed 5b8a0fb: program dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_directed.S and the logs dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l4_lockstep_zcmp_dummy_{run_header.txt,verdict.txt,stdout_excerpt.log,export.txt}; the committed run header reads module gen_ut_lockstep, seed 1, build_sources_sha256 893384b8eec4e6d5) and EXPLAINED by rtl-arch (dv/auto_dv/evidence/gen_b8_rtl_facts.md (rtl-arch T-225: 1eb2ede, CM59 fixes 53e8468, CM64 fixes 7d7be39, tb-infra's 27-row mapping folded 76cd2e5, CM68 / CM69 fixes ae5e58a = the explained record, sha256 b33a133f519f; cross-model APPROVE-WITH-CHANGES 68b9af3 on the CM59 copy)): an architectural bug, not an RVFI export bug; severity: architectural-state corruption (a register not saved or not restored, registers reloaded from above the frame, sp incremented twice, a ret with a stale sp) in a shipped configuration (SecureIbex dummy instructions); the RTL fix is an owner item
- rtl-arch alias: BUG-07 (rtl-arch T-017: CONFIRMED reachable by static analysis; highest-value finding: architectural-state corruption with dummy instructions enabled, a shipped-configuration feature)
- Features: F-CMP-064; cross-ref F-DIT-032 item
- Expected-fail TP items: TP-CMP-065, TP-DIT-032, TP-CMP-074 (the interrupt / debug exposure; a second reproducer for the owner)
- RTL: rtl/ibex_if_stage.sv:492-493 (the compressed decoder's valid_i and id_in_ready_i carry no dummy-insertion term) while :526-528 put the dummy into the IF/ID register with the INSTR_NOT_EXPANDED tag and :535, :808-809 hold the prefetch buffer, so the cm.* halfword stays at the decoder input; the expansion FSM takes its id_in_ready_i branches (rtl/ibex_compressed_decoder.sv:641, :653, :661, :676 for cm.push; :709, :718, :726, :745, :761, :767 for the pop family) and the micro-op on instr_o is discarded; the only FSM reset is flush_expanded on PC_EXC (rtl/ibex_if_stage.sv:483; rtl/ibex_compressed_decoder.sv:889); insertion decision rtl/ibex_dummy_instr.sv:115 with the counter advancing once per accepted micro-op (:103-104); debug gate rtl/ibex_controller.sv:474-477 (EXPANDED or COMMIT) and interrupt gate :498-500 (COMMIT tag only), both keyed on the ID tag the dummy does not carry
- Specification / intent: Zcmp atomicity intent (zc.adoc push/pop sequences); Ibex doc silent
- Notes: mechanism (dv/auto_dv/evidence/gen_b8_rtl_facts.md (rtl-arch T-225: 1eb2ede, CM59 fixes 53e8468, CM64 fixes 7d7be39, tb-infra's 27-row mapping folded 76cd2e5, CM68 / CM69 fixes ae5e58a = the explained record, sha256 b33a133f519f; cross-model APPROVE-WITH-CHANGES 68b9af3 on the CM59 copy), Sections 2-5): the FSM advances as if its micro-op had been accepted while ID receives the dummy, so that micro-op never executes (no LSU request, no register-file write, no RVFI record): a lost store leaves one register unsaved, a lost load leaves one register unrestored. A dummy on the LAST micro-op returns the FSM to idle with the cm.* halfword still in the buffer and the whole expansion replays: cm.push doubles every store at the same addresses (memory and sp end correct; the extra sp-adjust store of the reproduction); cm.popret / cm.popretz replay after sp was incremented, reloading every register from above the frame and incrementing sp a second time; a dummy on the sp increment of cm.popret / cm.popretz makes the ret execute with a stale sp. Dummies increment minstret (Section 4 as corrected by the review; B7). The two symptoms of the reproduction have one cause (Section 4): the missing RVFI records are faithful records of loads that did not happen and the extra records are the replayed micro-ops, so no RVFI-only candidate splits off. Secondary exposure (Section 5, stated from the RTL, not reproduced): the dummy in ID carries INSTR_NOT_EXPANDED, so the controller admits an interrupt inside the COMMIT window of the pop family (after the sp increment: the ret of cm.popret, the li a0, 0 or ret of cm.popretz; an interrupt between other micro-ops is by design and its restart is idempotent; the third COMMIT site, the first move of cm.mvsa01 / cm.mva01s, opens a benign window because the replay re-reads unchanged operands) and a debug request at any position of an expansion, and the PC_EXC flush restarts the expansion after mret / dret with partially applied state (TP-CMP-074). cm.mvsa01 / cm.mva01s (Section 3): a dummy on the first move leaves its destination permanently unwritten. The existing IbexPushPopFSMStable assertion (rtl/ibex_compressed_decoder.sv:937) cannot catch it because valid_i stays high; rtl-arch's TB-side assertion form (Section 6): if_id_pipe_reg_we && insert_dummy_instr |-> cm_state_d == cm_state_q && cm_rlist_d == cm_rlist_q && cm_sp_offset_d == cm_sp_offset_q (internal nets: probe P1 territory, coverage-only). Fix direction for the RTL owner (DV Lead reading; rtl-arch proposes none): qualify the expander's id_in_ready_i with ~insert_dummy_instr, or block insertion while the decoder is mid-expansion.
- Intended reproducer: dummy_instr_en=1 with mask for high frequency; loop of cm.push/cm.pop pairs with a checkable stack pattern; compare memory image and registers against the ISA model; a skipped micro-op shows as a missing store or register.
- Evidence (reproduction): after csrs 0x7C0, 4 (cpuctrlsts.dummy_instr_en) four cm.push / cm.pop pairs (rlist 4, 8, 12, 15; spimm 2) diverge from the lock-step model on 27 rows: isa_mem Zcmp stores model 1 dut 2 on the first push's sp-adjust micro-op (fd010113), loads model 1 dut 2 on its pop, stores 5/6 and loads 5/7 on the rlist-8 pair, and isa_rd Zcmp union x18 model 33333333 dut 00000000 after the pop. Symptoms: (a) ARCHITECTURAL: x18 is wrong after the pop (00000000 in the retained run: the s2 store of push rlist 8 lost in CmPushStoreReg, the slot stale, the pop's load faithful; 800003ff in an earlier unretained gen_zcmp_directed.S run: the CmPopRetRa replay reading above the frame, facts file Sections 3 and 6); (b) the rlist-15 pop's export (pc 80000108, insn 06010113, orders 0x50-0x58) emits load micro-op records for x27, x26, x24, x22, x21, x20, x18, x8 only (x25, x23, x19, x9, x1 absent), every micro-op still carrying rvfi_ext_expanded_insn_valid and the sp-adjust carrying _last: loads that did not happen; the rlist-12 pop (pc 80000104, insn 05010113, orders 0x3c-0x47) shows the replay case: a first pass x22, x21, x20, x18, x9, a second pass x23, x22, x20, x18, x9, x1, then the sp adjust, x8 never loaded (the facts note's pop rl12 losing s0, ra and the addi back to back; comparator row model wrote 10 registers, dut 8, order 71); one cause with (a), see Notes; the rlist-12 attribution of the 8-record list in tb-infra's gen_tdd_fcov.md:79 was the same mis-attribution (corrected by tb-infra in landing 6 at 61c97c1). Control: the same program without the csrs (every rlist and spimm, push/pop pairs, popret/popretz, 290 sequences) is clean under all four dmem rvalid regimes, and a misaligned-sp variant is clean, so the trigger is dummy insertion inside a Zcmp expansion. tb-infra's row mapping (dv/auto_dv/evidence/gen_b8_row_mapping.md, committed a9b63ae with landing 5, whose review f2320ca is REQUEST-CHANGES with no finding on the mapping file, the re-review sha to follow landing 6; facts file Section 3, reproduction status): all 27 comparator rows map to a lost micro-op or a full replay, 33 lost micro-ops in all (tally of lost micro-ops: CmIdle first store lost 2, CmPushStoreReg store lost 11, CmPushDecrSp addi lost with replay 2, CmIdle first load lost 2, CmPopLoadReg load lost 13, CmPopIncrSp addi lost with replay 3); the program has no popret / popretz, so a variant reaching the CmPopRetRa replay is owed by tb-infra. Testlist: gen_ut_lockstep_zcmp_dummy (Runtime touch ac5f4ab, expected_fail: red until the RTL changes, an unexpected PASS is its signal). tb-infra landing 4, T-205 slice 2, committed 5b8a0fb: program dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_directed.S and the logs dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l4_lockstep_zcmp_dummy_{run_header.txt,verdict.txt,stdout_excerpt.log,export.txt}; the committed run header reads module gen_ut_lockstep, seed 1, build_sources_sha256 893384b8eec4e6d5. Cause: dv/auto_dv/evidence/gen_b8_rtl_facts.md (rtl-arch T-225: 1eb2ede, CM59 fixes 53e8468, CM64 fixes 7d7be39, tb-infra's 27-row mapping folded 76cd2e5, CM68 / CM69 fixes ae5e58a = the explained record, sha256 b33a133f519f; cross-model APPROVE-WITH-CHANGES 68b9af3 on the CM59 copy). Evidence per symptom: lost stores / loads: the retained gen_zcmp_dummy_directed.S run above (all 27 rows); replay corruption (the CmPopRetRa reload from above the frame, x18 = 800003ff): an earlier unretained gen_zcmp_directed.S run with dummies, so a retained popret / popretz variant is owed by tb-infra in 2c beside the catching assertion; the mv-pair symptom (first move lost, destination unwritten) has no run yet (TP-CMP-065 reproducer clause). Consecutive micro-ops can be lost: dummy_cnt_threshold = lfsr cnt & {dummy_instr_mask, ones} (rtl/ibex_dummy_instr.sv:97), so with mask 0 the threshold is 0..3.

### B10: dcsr.cause = 2 (trigger) recorded on an ebreak entry when the next PC matches tdata2
- Status: candidate, reproducer pending
- rtl-arch alias: -
- Features: F-TRG-020
- Expected-fail TP items: TP-TRG-020
- RTL: rtl/ibex_controller.sv:519-523
- Specification / intent: riscv-debug-spec Sdext (cause 1 for ebreak) / Sdtrig (trigger fires on the matched instruction, not on the instruction before it)
- Notes: rtl-arch T-017: confirmed statically (trigger_match evaluated on pc_if every cycle; during the FLUSH cycle of an ebreak-into-debug pc_if holds the next address). Arming happens inside the debug ROM (trigger CSRs writable only in debug mode); T-041 reproducer spec.
- Intended reproducer: tdata1 execute trigger armed at address A; ebreak at A-4 with dcsr.ebreakm=1: dpc = A-4 but dcsr.cause reads 2 (RTL) vs 1 (spec).
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B11: NumBranchesTaken (mhpmcounter9) counts not-taken branches when cpuctrlsts.data_ind_timing=1
- Status: candidate, reproducer pending
- rtl-arch alias: -
- Features: F-PMC-041
- Expected-fail TP items: TP-PMC-043, TP-BTALU-016
- RTL: rtl/ibex_id_stage.sv:790-791,815,831,928 (branch_set forced for all branches under DIT)
- Specification / intent: doc/03_reference/performance_counters.rst (NumBranchesTaken: taken branches)
- Notes: rtl-arch T-017 confirmed statically (perf_tbranch_o = branch_set_i; branch_set_raw_d = branch_decision_i | data_ind_timing_i). Decision requested from the DV Lead (T-017 Section 6): treated as a counter bug candidate (the doc defines the event as taken branches); items TP-PMC-043 / TP-BTALU-016 stay expected-fail. Classified B, not D, by the criterion above (wrong event under a configuration, not a mis-described convention; contrast D6).
- Intended reproducer: data_ind_timing=1; 100 never-taken branches; mhpmcounter9 delta: doc 0, RTL 100. Control: data_ind_timing=0.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B13: rvfi_pc_wdata keeps bit 0 for jalr to an odd target while the fetch clears it (RVFI-only class, like BUG-10)
- Status: candidate, reproducer spec available and observed (rtl-arch R11, dv/auto_dv/evidence/gen_t102_rtl_facts.md; Test Writer batch 2: gen_test_isa_cti reports 64 of 64 comparator rows per seed of isa_pc_next dut == model | 1 on jalr / c.jr / c.jalr with an odd rs1 + imm, dv/auto_dv/evidence/gen_tdd_batch2.md; Orchestrator ruling LOG-032)
- rtl-arch alias: R11 (gen_t102_rtl_facts.md)
- Features: F-BTALU-008 (canonical); cross-ref F-RVFI-013
- Expected-fail TP items: TP-BTALU-008, TP-RVFI-013
- RTL: the branch-target ALU adds rs1 and the immediate without masking (rtl/ibex_ex_block.sv:95-101), so branch_target_ex carries bit 0; the fetch drops it (rtl/ibex_if_stage.sv:244, :288 prefetch_addr = {fetch_addr_n[31:1], 1'b0}, :416; rtl/ibex_fetch_fifo.sv:62-63) and pc_if / pc_id are even; the jalr record's rvfi_pc_wdata = pc_set ? branch_target_ex : pc_if (rtl/ibex_core.sv:2084) takes the RAW target, so RVFI reports an odd next-pc while no architectural register or fetch address ever shows bit 0
- Specification / intent: RVFI (riscv-formal docs/source/rvfi.rst, Program counter): pc_wdata is the address of the next instruction; the ISA execution is per spec (JALR clears the target LSB), the RVFI definition is violated
- Notes: RVFI-only class (like BUG-10 / B18): no architectural effect. One-line fix the RTL owner would make: mask bit 0 at rtl/ibex_core.sv:2084 ({branch_target_ex[31:1], 1'b0} when pc_set). Comparator convention (T-144): the unmask knob landed at ffa9127 (TB Infra delta 1b on ce33b4f) as +gen_isa_pc_next_mask_b13, default 1: isa_pc_next masks bit 0 of rvfi_pc_wdata on jalr / c.jr / c.jalr records and counts them as b13_odd_jalr in the GEN_SB report (gen_rvfi_pkg.sv:494-500 at ffa9127); 0 runs the raw RVFI rule; proof pair on TB Infra's build: 80 records counted with the mask, exactly 80 isa_pc_next misses without it. Caveat (delta 1b review): with the mask on the comparator does not fail on B13, so gen_btalu_hazard_xfail / TP-BTALU-008 / TP-RVFI-013 must run with +gen_isa_pc_next_mask_b13=0 to witness the defect; TB Infra's 1c (9e912bb) passed both reviewers (LOG-051), so the plan's Section 0a records the comparator as built with the mask. TP-ISA-019's verdict relies on that convention and stays not_built for the odd-target clause until then; the expected-fail test gen_btalu_hazard_xfail (TP-BTALU-008) alone runs the unmasked rule and records the bit
- Intended reproducer: jalr to rs1 + imm odd: rvfi_pc_wdata[0] = 1 while the next rvfi_pc_rdata[0] = 0 (observed in batch 2, 64 rows per seed)
- Evidence: dv/auto_dv/evidence/gen_tdd_batch2.md (gen_test_isa_cti comparator rows); rtl-arch R11

### B14: RVFI drops the ID-stage trap record when a WB load/store error coincides
- Status: downgraded to an RVFI convention note pending the confirmation simulation (rtl-arch T-041, fact-check row 48): the WB error has priority in FLUSH, the killed ID instruction re-executes after the handler and then produces its own record, so suppressing its record is correct; the confirmation program must show two trap records in order; one record re-opens it
- rtl-arch alias: BUG-04
- Features: F-RVFI-015 (canonical: ID exception while WB is already faulting, single trap record); cross-refs F-EXC-065 item, F-DMEM-034 item, F-ISA-051 item
- Expected-fail TP items: none as gate items (downgraded); confirmation items informational: TP-EXC-065, TP-ISA-051, TP-DMEM-063, TP-RVFI-039
- RTL: rtl/ibex_core.sv:1851-1853 (rvfi_id_done suppresses when wb_exception_o); rtl/ibex_controller.sv:336-337
- Specification / intent: RVFI convention: every trapping instruction is reported (rtl/ibex_core.sv:1843-1849 comment; rvfi.rst rvfi_trap)
- Notes: RVFI-only; affects the comparator, not architectural state; unverified in simulation
- Intended reproducer: Store with a slow error response followed immediately by an illegal instruction: expect two rvfi_trap records, RTL emits one.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B15: dcsr.ebreaks (bit 13) is writable although the hart has no S-mode
- Status: candidate, reproducer pending
- rtl-arch alias: BUG-03
- Features: F-DBG-016 (canonical); alias F-CSR-076
- Expected-fail TP items: TP-CSR-075, TP-CSR-076, TP-DBG-018
- RTL: rtl/ibex_cs_registers.sv:810-836 (every other field forced; bit 13 not forced)
- Specification / intent: riscv-debug-spec xml/core_registers.xml:163-172 (ebreaks hardwired to 0 if the hart does not support S-mode); misa = 0x40901104 has no S
- Notes: functional impact nil: rtl/ibex_controller.sv:481-483 never reads it
- Intended reproducer: In debug mode: li t0, 0x2000; csrs dcsr, t0; csrr t1, dcsr: RTL t1[13]=1, spec 0.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B16: Misaligned load with a bus-integrity error on the FIRST beat still writes rd
- Status: candidate, reproducer pending (rtl-arch T-053 X-11; security-relevant; owner question Q-015 worded below)
- rtl-arch alias: BUG-08 (gen_bug_reproducer_specs.md)
- Features: F-SEC-015 (canonical: load rd-write suppression on bad checkbits, security.rst:88); cross-refs F-DMEM-041, F-RVFI-024, F-SEC-017 (D-side integrity response)
- Expected-fail TP items: TP-DMEM-064, TP-SEC-040, TP-RVFI-040
- RTL: rtl/ibex_load_store_unit.sv:514 (first-half status lsu_err_d = data_bus_err_i | pmp_err_q, no integrity term), :697-698 (RF write gated only by the completing beat's data_intg_err), :756 (alert); rtl/ibex_controller.sv:402-438 (internal NMI)
- Specification / intent: doc/03_reference/security.rst:88 ("Where load data has bad checkbits the write to the load's destination register will be suppressed"); the RISC-V specification is silent (Ibex feature). RTL less complete than the documented intent (dv_principles.md Section 4): checker follows the documented intent, expected-fail for the first-beat class.
- Notes: the alert and the internal NMI do fire; only the rd write leaks the merged data. Security-relevant: owner question Q-015 (below).
- Intended reproducer: M-mode; lw x5, 2(x6) with x6 word-aligned (EA = 4n+2, two beats); the data agent corrupts the integrity bits of the FIRST rvalid beat only, both beats data_err_i = 0. Doc: rvfi_rd_addr = 0 / rvfi_ext_rf_wr_suppress = 1, one alert_major_bus_o pulse, internal NMI (mcause 0xFFFF_FFE0). RTL: rvfi_rd_addr = 5, rf_wr_suppress = 0, x5 = merged data; alert and NMI as expected. Control: the SECOND beat corrupted suppresses the write (both agree).
- Evidence: (none yet)

### B17: HPM counters 8, 11, 12 over-count instructions waiting in ID behind an outstanding WB memory access
- Status: candidate, reproducer pending (rtl-arch T-053 X-13)
- rtl-arch alias: BUG-09
- Features: F-PMC-053 (canonical: counters 8/11/12 over-count an instruction waiting in ID behind an outstanding WB memory access); counter features F-PMC-039 (mhpmcounter8 NumBranches), F-PMC-043 (mhpmcounter11 NumCyclesMulWait), F-PMC-044 (mhpmcounter12 NumCyclesDivWait); cross-ref F-PMC-041 (B11)
- Expected-fail TP items: TP-PMC-058, TP-PMC-059, TP-PMC-060, TP-BTALU-018
- RTL: rtl/ibex_id_stage.sv:886-934 (perf_branch_o in FIRST_CYCLE under instr_executing_spec), :1054-1057 (instr_executing_spec lacks ~outstanding_memory_access), :866-869 (state advances only under instr_executing), :1226-1227 (perf_mul_wait_o / perf_div_wait_o count deferred-start cycles)
- Specification / intent: doc/03_reference/performance_counters.rst:41 ("Number of branches (conditional)"): one count per branch; the RTL counts once per waiting cycle. Counters 7 (jumps) and 9 (taken) are exact (deduped by branch_jump_set_done_q). Direction (DV Lead): bug candidate, checker follows the doc for the waiting class; RTL-defined otherwise.
- Intended reproducer: mcountinhibit = 0; csrr t0, mhpmcounter8; lw x7, 0(x8); beq x9, x10, +8; nop; csrr t1, mhpmcounter8 with knob dmem_rvalid_delay = K and x9 != x10. Doc: t1 - t0 = 1. RTL: about K. Control: lw; nop...; beq spacing so the load returned before the beq enters ID gives 1.
- Evidence: (none yet)

### B18: rvfi_mem_rmask non-zero and rvfi_mem_addr = ALU result on every non-store record (RVFI-only)
- Status: candidate (RVFI-port deviation, observed in TB Infra's first lock-step run; no architectural effect; comparator classifies records by decoded opcode)
- rtl-arch alias: BUG-10
- Features: F-RVFI-011 (memory fields) canonical; cross-ref the rvfi_proto checker row
- Expected-fail TP items: none (no architectural item; the RVFI protocol item records the deviation and applies mask rules only to decoded load/store records)
- RTL: rtl/ibex_core.sv:2085 and :2253-2260 (mask derived from lsu_type without an LSU-request qualifier; wmask clean because data_we_o is decode-qualified)
- Specification / intent: tools/specs/riscv-formal/docs/source/rvfi.rst:135-136, 143-144 (rmask non-zero only for memory operations; addr holds the accessed location)
- Notes: same fact as fact-check X-15 / the TP-RVFI-014 checker caveat; ID-stage trap records also carry the garbage decode.
- Intended reproducer: any non-load, non-store record (e.g. addi): rvfi_mem_rmask == 4'b1111 and rvfi_mem_addr == the ALU result; spec: rmask == 0.
- Evidence: TB Infra lock-step observation (log to be cited by TB Infra)

### B19: rvfi_trap on illegal ebreak encoding variants (RVFI-only; pending rtl-arch confirmation)
- Status: candidate, reproducer spec available (rtl-arch confirmed at the RTL, T-053 follow-up; RVFI-only, BUG-04/BUG-10 family; no architectural effect; informational item TP-ISA-057)
- rtl-arch alias: BUG-11 (gen_bug_reproducer_specs.md)
- Features: F-RVFI-025 (canonical: ebreak that enters debug mode is not reported as a trap; the illegal-variant case is its B19 Note), F-ISA-034 (ebreak decode incl. the rs1/rd != 0 illegal variants); informational item TP-ISA-057
- Expected-fail TP items: none (informational: TP-ISA-057)
- RTL: rtl/ibex_decoder.sv:739-740 sets ebrk_insn_o for funct12 0x001 regardless of rs1/rd and :757-759 raises illegal_insn when rs1 or rd != 0 (the illegal block :912-920 does not clear ebrk_insn_o); rtl/ibex_controller.sv:312-332 gives illegal_insn_q priority over ebrk_insn (mcause 2, mtval = encoding, PC to mtvec); rtl/ibex_core.sv:1885-1886 masks rvfi_trap with ~(ebrk_insn & ebreak_into_debug), ebreak_into_debug = dcsr.ebreakm/u per mode (:481)
- Specification / intent: rvfi.rst: rvfi_trap must be set for an instruction that cannot be decoded as legal
- Notes: no architectural effect; the comparator treats the record per the decoded illegal-instruction class
- Intended reproducer: dcsr.ebreakm = 1 (or ebreaku in U-mode); execute .word 0x00100173 (ebreak encoding with rd = x2): RTL shows rvfi_trap = 0 on the record while mcause reads 2 and execution continues at mtvec; with the dcsr bit clear rvfi_trap = 1 (rvfi.rst: rvfi_trap must be set for an illegal instruction). Comparator rule: derive the trap from the pc flow for ebreak encodings with rs1/rd != 0 when ebreakm/u is set (TB Infra: not built yet; a run hitting it shows the known B19 isa_trap signature).
- Evidence: (none yet)

### B20: fence.i increments mhpmcounter7 (NumJumps), which the doc defines as unconditional jumps only
- Status: candidate, reproducer spec available (rtl-arch reading, dv/auto_dv/evidence/gen_hpm_event_defs.md section 3, D-NUMJUMPS-FENCEI; no run yet)
- rtl-arch alias: D-NUMJUMPS-FENCEI (gen_hpm_event_defs.md); rtl-arch recommends following the doc
- Features: F-PMC-038 (NumJumps); item TP-PMC-061 (expected-fail); TP-PMC-040 keeps fence.i out of its windows
- Expected-fail TP items: TP-PMC-061 (gen_pmc_hpm_b20_fencei_xfail)
- RTL: rtl/ibex_decoder.sv:704-720 implements FENCE.I as a jump to the next PC (jump_in_dec_o, and jump_set_o in the first cycle, to flush the prefetch buffer and the icache); rtl/ibex_id_stage.sv:941 and rtl/ibex_controller.sv:687 count jump_set as perf_jump, so NumJumps moves by one per fence.i
- Specification / intent: performance_counters.rst:39 "NumJumps: Number of unconditional jumps (j, jal, jr, jalr)"; the privileged spec leaves hpm events implementation-defined, so the Ibex doc is the only definition of this counter; B by the B-versus-D criterion because the counter records an event the doc excludes (the B11 class: a wrong event, not a mis-stated convention like D6/D20)
- Notes: severity low (one count per fence.i, no functional effect); the RTL fix is a one-term gate on perf_jump or a separate flush request; the owner may instead accept the RTL and re-document, in which case B20 becomes a doc defect and TP-PMC-061 a pass item (owner question to be filed by the Orchestrator, as for Q-004/Q-005); the independent counter model follows the doc and treats fence.i windows as the B20 witness (CG-PMC-003.cr_variant_rel.fencei_gt)
- Intended reproducer: csrr t0, mhpmcounter7; fence.i; csrr t1, mhpmcounter7 with mcountinhibit[7] = 0: doc predicts t1 - t0 = 0, RTL gives 1
- Evidence: (none yet)

## 1b. Retained IDs that are not bug candidates (kept so plan and review references resolve)

B6 (RTL-defined: debug mode runs at M privilege, Sdext.adoc:32/:51), B9 (RTL-defined corner reachable only under out-of-spec
debug_req_i stimulus; record-only, informational item) and B12 (documented behaviour, exception_interrupts.rst:191 and
cs_registers.rst:556; design-weakness note S4 in Section 2). None carries an expected-fail item.

### B6: RECLASSIFIED (Critic C-20): exception taken in debug mode forces priv_lvl to M
- Status: not a bug (RTL-defined, retained ID)
- rtl-arch alias: -
- Features: F-EXC-046
- Expected-fail TP items: none (TP-EXC-046, TP-DBG-034 expect pass)
- RTL: rtl/ibex_cs_registers.sv:908
- Specification / intent: Sdext.adoc:32 (debug mode runs with machine-mode privilege), :51 (privilege-changing instructions in debug mode are UNSPECIFIED)
- Notes: NOT A BUG: RTL-defined; retained ID only so earlier references resolve; TP-EXC-046 and TP-DBG-034 expect pass
- Intended reproducer: n/a
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B9: dcsr.cause written 0 if debug_req_i deasserts in the FLUSH cycle before DBG_TAKEN_IF
- Status: RTL-defined corner under out-of-spec stimulus (debug_req_i pulse shorter than the DECODE->FLUSH span; the debug spec holds haltreq until the hart halts): record only, not a gate item (rtl-arch T-041, Q-007 default); B-id retained
- rtl-arch alias: -
- Features: F-DBG-006
- Expected-fail TP items: none (record-only; informational item: TP-DBG-011)
- RTL: rtl/ibex_controller.sv:451-533 (debug_cause_d priority and one-cycle skew)
- Specification / intent: riscv-debug-spec Sdext.adoc (cause field must identify the entry reason)
- Notes: rtl-arch T-017: confirmed statically for the special-request path only (DECODE -> FLUSH -> DBG_TAKEN_IF); requires a debug_req_i pulse shorter than the DECODE->FLUSH span, which the debug spec forbids (haltreq is held until the hart halts). Classification: RTL-defined corner under out-of-spec stimulus, low severity; the RTL comment at rtl/ibex_controller.sv:515-518 acknowledges the window. TP-DBG-011 is the informational (record-only) item; no gate item exists.
- Intended reproducer: Drive debug_req_i as a pulse that ends exactly in the FLUSH cycle of a trap/mret/CSR-flush instruction; read dcsr in the debug program: cause reads 0 (RTL) vs 3 (spec).
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B12: mret from an interrupt handler clears cpuctrlsts.sync_exc_seen, weakening double-fault detection
- Status: documented behaviour, not a bug candidate: design-weakness note for the security owner (exception_interrupts.rst:191 and cs_registers.rst:556 say sync_exc_seen is cleared when mret is executed; no RISC-V specification covers double-fault detection). Carrying items expect pass with the note (Critic pre-review S-1; rtl-arch T-017 agrees)
- rtl-arch alias: -
- Features: F-SEC-025 (canonical); aliases F-EXC-057, F-CSR-091
- Expected-fail TP items: none after the reclassification (TP-EXC-056, TP-CSR-094, TP-SEC-025 expect pass with a design note)
- RTL: rtl/ibex_cs_registers.sv:964-965
- Specification / intent: documented Ibex behaviour: exception_interrupts.rst:191 and cs_registers.rst:556 ("cleared when mret is executed"); no RISC-V specification covers double-fault detection. No owner question is needed (no specification contradiction; the design-weakness note is carried to the closure report and Section 2 row S4)
- Notes: design weakness for the security owner (a second synchronous exception in the original handler is not detected after an interrupt handler's mret); not a bug candidate; items pass with the note
- Intended reproducer: Take a synchronous exception (ecall) -> sync_exc_seen=1; in the handler enable MIE and take an interrupt; its mret clears sync_exc_seen; a second sync exception in the original handler does not raise double_fault_seen_o (RTL) vs raises (intent).
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

## 2. Security-relevant RTL-defined behaviours (owner decision requested, not bugs)

| Ref | Behaviour | RTL | Owner question | Default applied |
|---|---|---|---|---|
| S1 (MEM-13) | Second half of a misaligned data access is issued after a first-half PMP fault; a faulting misaligned store performs its second-word write | rtl/ibex_load_store_unit.sv:489-531; rtl/ibex_core.sv:1063 | Q-DL-7 | modelled as RTL-defined, covered (F-PMP-087, TP-PMP-085) |
| S2 (CTRL-04) | Trap/debug entry updates CSRs and PC while fetch_enable_i is not On; invalid MuBi encodings act as Off with no alert | rtl/ibex_core.sv:644-649,1350-1351 | Q-DL-8 | checked as-is (F-RST-015, F-IMEM-023) |
| S4 (B12) | mret from an interrupt handler clears cpuctrlsts.sync_exc_seen, so a second synchronous exception in the original handler is not detected (documented behaviour) | rtl/ibex_cs_registers.sv:962-965 | none needed (documented); noted for the closure report | items pass with the design note |
| S3 (MEM-05/19) | No defence against unsolicited or grant-cycle rvalid on either bus; integrity check runs on such responses | rtl/ibex_load_store_unit.sv:756-757; rtl/ibex_icache.sv:721 | Q-DL-9 | never driven in passing tests; one informational test per bus (TP-IMEM-040) |
| S5 (WP12-F2) | A data-RAM corruption in one copy of a line held valid in two ways reports nothing when the flip clears a bit: the hit-data mux ORs the matching ways, so the other copy restores the bit, the fetched word is correct and no minor alert is signalled; a flip that sets a bit stays visible | rtl/ibex_icache.sv:506-514, :585, :591-592 | none needed: it breaches nothing documented, since icache.rst:218 and security.rst:107 both condition the alert on an error being seen or detected and the ORed word is a correct codeword; noted for the closure report | covered as a no-alert case (CG-IC-006.cp_no_alert_case.masked_duplicate_copy, F-IC-042 Notes); the duplicate is self-limiting by capacity and self-clearing on the next data error at that index |

## 3. Doc defects (RTL is specification-legal or internally consistent; the Ibex doc is wrong or stale)

Merged list: reading report Section 5.3 plus rtl-arch A.2 (Critic C-23). Checker follows the RTL.

| ID | Defect | Doc location | RTL | Features |
|---|---|---|---|---|
| D1 | mip reads the raw irq pins, not qualified by mie | cs_registers.rst:246 | rtl/ibex_cs_registers.sv:408-412,495-501 | F-CSR-032 |
| D2 | Illegal mstatus.MPP value (01/10) legalises to U; doc says M | cs_registers.rst:138 | rtl/ibex_cs_registers.sv:783-786 | F-CSR-024 (BUG-05 alias) |
| D3 | mcause is software-writable; doc marks the fields read-only | cs_registers.rst:213-217 | rtl/ibex_cs_registers.sv:730-733,803 | F-CSR-046 |
| D4 | tdata1 reset/constant value is 0x2800_1048 (m=1,u=1), doc says 0x2800_1000 | cs_registers.rst:360 | rtl/ibex_cs_registers.sv:1848-1866 | F-TRG-003 / F-CSR-081; the doc's own field table at cs_registers.rst:362-404 (m = 1 at bit 6, u = 1 at bit 3) already yields 0x2800_1048; RTL composition rtl/ibex_cs_registers.sv:1848-1864 with execute = tmatch_control_q reset 0 at :1806-1812 (rtl-arch R5, gen_t102_rtl_facts.md); read as 28001048 in the Test Writer's rst_boot_s1 log; reproducer csrr t0, tdata1 in M-mode after reset |
| D5 | RETIRED: dcsr.ebreaks writable is bug candidate B15 | - | - | - |
| D6 | NumLoads/NumStores count a misaligned access once; doc says twice | performance_counters.rst | rtl/ibex_load_store_unit.sv:468-475 | F-PMC-034/036 |
| D7 | Divide latency: RTL 37 cycles total (36 stall); docs say 37 (instruction_decode_execute.rst) and 37 stall (pipeline_details.rst:63) | instruction_decode_execute.rst, pipeline_details.rst:63 | rtl/ibex_multdiv_fast.sv:412-526 | F-MUL-012 |
| D8 | bfp executes in one cycle; doc table lists Zbf as multi-cycle | instruction_decode_execute.rst:95 | rtl/ibex_alu.sv:266-275, rtl/ibex_decoder.sv:1302 | F-BIT-030 |
| D9 | icache.rst describes instr_pmp_err_i and branch_spec_i ports that do not exist and a 72-bit data RAM (RTL: 2 x 39-bit codewords, LineSizeECC 78) | icache.rst:202-208,236-241,271-274 | rtl/ibex_icache.sv:13-69,305-310; rtl/ibex_core.sv:557 | F-IC-006, F-IMEM-028, F-IC-036 |
| D10 | mtval on an instruction access fault is the faulting fetch address (pc or pc+2), not 0 | cs_registers.rst:235 | rtl/ibex_controller.sv:859-861 | F-EXC fetch-fault entries |
| D11 | security.rst claims early completion of multiplication by zero/one is removed under DIT; the single-cycle multiplier has no such path | security.rst:27 | rtl/ibex_multdiv_fast.sv:140-260 | F-DIT-005 |
| D12 | debug.rst says trigger CSRs trap outside debug mode; RTL and cs_registers.rst:345 allow M-mode reads and silently drop M-mode writes | debug.rst:54-55 | rtl/ibex_cs_registers.sv:636-662,1775-1780 | F-DBG-050, F-TRG-007 |
| D13 | cs_registers.rst says fence.i is guaranteed to fetch a new scramble key; icache.rst:113-116 and RTL ignore fence.i while a key request is pending | cs_registers.rst:544-545 | rtl/ibex_icache.sv:1229-1240 | F-IC key-request entries |
| D14 | security.rst implies an internal NMI for any bus-integrity mismatch; instruction-side errors give the major alert plus a fetch fault, no NMI | security.rst:85-87 | rtl/ibex_id_stage.sv:613 | F-IMEM-027, F-SEC integrity entries |
| D15 | cs_registers.rst CSR table omits implemented mcounteren, mstatush, menvcfg/menvcfgh, mconfigptr and the cycle/instret/hpmcounter aliases | cs_registers.rst table | rtl/ibex_cs_registers.sv read mux | F-CSR-0xx (machine info / trap setup) |
| D16 | performance_counters.rst parameter text stale (NumMHPMCounters 1..8, WidthMHPMCounters); MHPMCounterNum=10 gives mhpmcounter3..12 | performance_counters.rst | rtl/ibex_cs_registers.sv:1667-1707 | F-PMC-020 |
| D17 | load_store_unit.rst / instruction_fetch.rst list separate 7-bit intg ports; at ibex_core they are bits [38:32] of the 39-bit ports | load_store_unit.rst:34-36,52-54; instruction_fetch.rst:68 | rtl/ibex_core.sv:74,84,86 | F-IMEM/F-DMEM width entries |
| D18 | cs_registers.rst tselect text names parameter DbgHwNumLen (it is DbgHwBreakNum); scontext heading gives 0x7AA (table and RTL: 0x5A8) | cs_registers.rst tselect/scontext | rtl/ibex_pkg.sv:511,518 | F-TRG-002, F-CSR trigger entries |
| D20 | mhpmeventN reads 1 << (N - 3) (mhpmevent3 = 0x1 .. mhpmevent12 = 0x200); doc says 1 << N | performance_counters.rst:133-147 | rtl/ibex_cs_registers.sv:185, 1602-1619 | F-PMC-020, F-CSR-061 (fact-check X-3) |
| D21 | up to two ordinary instructions can retire between a corrupted data response and the internal NMI; doc says at most one (to be confirmed by the first directed integrity-error sim, inventory UNVERIFIED-4) | exception_interrupts.rst:87-88 | rtl/ibex_controller.sv:402-438 | F-IRQ-04x internal-NMI entries (fact-check X-10) |
| D19 | security.rst dummy_instr_mask table lists 4 of the 8 legal values | security.rst | rtl/ibex_dummy_instr.sv:33-148 | F-DIT-012 |
| D22 | icache.rst gives one cause for a line allocated in several ways, a branch into an address being prefetched, and calls the consequence a minor performance inefficiency; an ECC-correction refetch is a second, undocumented cause, and with one copy corrupted the consequence extends to a corruption that reports nothing (S5) | icache.rst:73-74 | rtl/ibex_icache.sv:506-514, :534-535, :591-592 | F-IC-042, F-IC-021 |

## 4. Change log
- v1h (2026-09-03 UTC): B11 cites the B-versus-D criterion (round-4 low); criterion text names B11 and D6.
- v1g (2026-09-03 10:20 UTC): round-3 lows: B17 feature IDs (F-PMC-053/039/043/044), B19 canonical F-RVFI-025, B9 note aligned to record-only, B6/B9/B12 moved to Section 1b (retained IDs, not bug candidates), B-versus-D criterion stated.
- v1f (2026-09-03 09:39 UTC): B19 confirmed by rtl-arch as BUG-11 (RTL chain and reproducer spec).
- v1e (2026-09-03 09:30 UTC): item lists refreshed after plan v2b (B16 items TP-DMEM-064/TP-SEC-040/TP-RVFI-040; B17 items TP-PMC-058/059/060, TP-BTALU-018); B16 canonical feature F-SEC-015; B19 (RVFI-only, OQ-10) added pending rtl-arch confirmation.
- v1d (2026-09-03 08:52 UTC): B16 (BUG-08, security-relevant, Q-015), B17 (BUG-09), B18 (BUG-10) added from rtl-arch T-053 / TB Infra; D20, D21 added; B12 citation corrected and moved to a Section 2 note (S4).
- v1c (2026-09-03): B9 reclassified record-only (informational item); B14 feature corrected to F-RVFI-015; expected-fail lists refreshed after the plan v2a fold.
- v1b (2026-09-03): expected-fail item lists refreshed from the plan parts after the Critic pre-review fold-in (B6/B12/B14 carry no expected-fail items; B15 items TP-CSR-075, TP-DBG-018).
- v1a (2026-09-03): folded rtl-arch T-017 (BUG-06 = B1, BUG-07 = B8 confirmed reachable, B9 out-of-spec stimulus, B10/B11 confirmed) and T-041 (BUG-04/B14 downgraded pending sim); B12 reclassified as documented behaviour with a design note (Critic pre-review S-1).
- v1 (2026-09-03): opened with B1..B15 (B6 reclassified per Critic C-20; B15 added per C-21; B5 re-cited per C-22), S1..S3, D1..D19 (D5 retired).
- v1i (2026-09-03 12:43 UTC): B20 added from rtl-arch's HPM event definitions (fence.i counted by NumJumps; doc followed, expected-fail TP-PMC-061); rtl-arch's second candidate (illegal branch/JALR encodings counted before the trap) was withdrawn by rtl-arch (rtl/ibex_decoder.sv:905-918 clears jump/branch on illegal_insn) and gets no row; the counter model's expected deviations are D6, B7, B11, B17 and B20.
- v1j (2026-09-03 13:59 UTC): B13 promoted from RVFI-cosmetic note to a DUT bug candidate of the RVFI-only class per rtl-arch R11 and the batch-2 observation (64 of 64 rows per seed); one-line fix at rtl/ibex_core.sv:2084 and the comparator convention recorded (Orchestrator ruling). R10 (mtval = 0 on a breakpoint exception is spec-legal; the pc arm is CHERIoT-only) is a shim convention, not a bug: cited in the plan where the cause-3 mtval expectation is stated.
- v1k (2026-09-03 14:49 UTC): B13 reworded per the v2i diff review (CM12-M-2, L-3): the comparator mask is TB Infra's T-144 to encode, not a present fact (gen_rvfi_pkg.sv:452 at b8332f9 has no mask); the ruling is cited as LOG-032.
- v1l (2026-09-04 06:36 UTC): S5 and D22 added for tb-infra's finding WP12-F2 with rtl-arch's traced mechanism. Classified RTL-defined behaviour with a documentation gap, NOT a bug candidate: multi-way allocation of one line is documented (icache.rst:73), the ECC-correction refetch is an undocumented second cause of it, and the masked case never detects an error at all, so neither alert sentence (icache.rst:218, security.rst:107, both conditioned on detection) is triggered. F-IC-042's What and Notes carry the corrected consequence and both causes.
