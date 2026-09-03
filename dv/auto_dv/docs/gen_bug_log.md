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
- Status: candidate, reproducer pending
- rtl-arch alias: -
- Features: F-CMP-051
- Expected-fail TP items: TP-CMP-051
- RTL: rtl/ibex_compressed_decoder.sv:779-806
- Specification / intent: riscv-isa-manual unpriv/zc.adoc cm.mvsa01: encoding with equal registers is reserved
- Notes: low severity
- Intended reproducer: Assemble cm.mvsa01 with r1s'=r2s' via .insn/.2byte; RTL executes (final value = a1); spec expects reserved -> illegal (Ibex choice: no trap).
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

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

### B8: Dummy instruction inserted mid-Zcmp sequence may skip a micro-op (static reading)
- Status: candidate, reproducer pending
- rtl-arch alias: BUG-07 (rtl-arch T-017: CONFIRMED reachable by static analysis; highest-value finding: architectural-state corruption with dummy instructions enabled, a shipped-configuration feature)
- Features: F-CMP-064; cross-ref F-DIT-032 item
- Expected-fail TP items: TP-CMP-065, TP-DIT-032
- RTL: rtl/ibex_if_stage.sv:493 (compressed-decoder id_in_ready not qualified by insert_dummy_instr)
- Specification / intent: Zcmp atomicity intent (zc.adoc push/pop sequences); Ibex doc silent
- Notes: confirmed statically by rtl-arch (chain: expander FSM advances on id_in_ready_i & ~pc_set_i, rtl/ibex_if_stage.sv:493, unqualified by insert_dummy_instr; dummy_cnt counts micro-ops; the micro-op emitted in the insertion cycle is never executed: cm.push omits one store, cm.pop omits one load or the sp adjust). Fix direction for the RTL owner: gate the expander with ~insert_dummy_instr or block insertion while gets_expanded != NOT_EXPANDED. One directed sim demonstrates it (T-041 reproducer spec).
- Intended reproducer: dummy_instr_en=1 with mask for high frequency; loop of cm.push/cm.pop pairs with a checkable stack pattern; compare memory image and registers against the ISA model; a skipped micro-op shows as a missing store or register.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B9: dcsr.cause written 0 if debug_req_i deasserts in the FLUSH cycle before DBG_TAKEN_IF
- Status: candidate, reproducer pending
- rtl-arch alias: -
- Features: F-DBG-006
- Expected-fail TP items: TP-DBG-011
- RTL: rtl/ibex_controller.sv:451-533 (debug_cause_d priority and one-cycle skew)
- Specification / intent: riscv-debug-spec Sdext.adoc (cause field must identify the entry reason)
- Notes: rtl-arch T-017: confirmed statically for the special-request path only (DECODE -> FLUSH -> DBG_TAKEN_IF); requires a debug_req_i pulse shorter than the DECODE->FLUSH span, which the debug spec forbids (haltreq is held until the hart halts). Classification: RTL-defined corner under out-of-spec stimulus, low severity; the RTL comment at rtl/ibex_controller.sv:515-518 acknowledges the window. Item TP-DBG-011 stays expected-fail only as the documenting test; not a gate item.
- Intended reproducer: Drive debug_req_i as a pulse that ends exactly in the FLUSH cycle of a trap/mret/CSR-flush instruction; read dcsr in the debug program: cause reads 0 (RTL) vs 3 (spec).
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

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
- Notes: rtl-arch T-017 confirmed statically (perf_tbranch_o = branch_set_i; branch_set_raw_d = branch_decision_i | data_ind_timing_i). Decision requested from the DV Lead (T-017 Section 6): treated as a counter bug candidate (the doc defines the event as taken branches); items TP-PMC-043 / TP-BTALU-016 stay expected-fail.
- Intended reproducer: data_ind_timing=1; 100 never-taken branches; mhpmcounter9 delta: doc 0, RTL 100. Control: data_ind_timing=0.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B12: mret from an interrupt handler clears cpuctrlsts.sync_exc_seen, weakening double-fault detection
- Status: documented behaviour, not a bug candidate: design-weakness note for the security owner (exception_interrupts.rst:191 and cs_registers.rst:556 say sync_exc_seen is cleared when mret is executed; no RISC-V specification covers double-fault detection). Carrying items expect pass with the note (Critic pre-review S-1; rtl-arch T-017 agrees)
- rtl-arch alias: -
- Features: F-SEC-025 (canonical); aliases F-EXC-057, F-CSR-091
- Expected-fail TP items: none after the reclassification (TP-EXC-056, TP-CSR-094, TP-SEC-025 expect pass with a design note)
- RTL: rtl/ibex_cs_registers.sv:964-965
- Specification / intent: doc/03_reference/security.rst double-fault detection intent (sync_exc_seen armed until the synchronous handler returns)
- Notes: design weakness; owner ruling requested (Q-DL-3 policy)
- Intended reproducer: Take a synchronous exception (ecall) -> sync_exc_seen=1; in the handler enable MIE and take an interrupt; its mret clears sync_exc_seen; a second sync exception in the original handler does not raise double_fault_seen_o (RTL) vs raises (intent).
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B13: rvfi_pc_wdata keeps bit 0 for jalr to an odd target while the fetch clears it
- Status: candidate, reproducer pending
- rtl-arch alias: -
- Features: F-BTALU-008 (canonical); cross-ref F-RVFI-013
- Expected-fail TP items: TP-BTALU-008, TP-RVFI-013
- RTL: rtl/ibex_core.sv:2084 (rvfi_pc_wdata = raw branch_target_ex when pc_set)
- Specification / intent: RVFI: pc_wdata is the address of the next instruction (riscv-formal docs/source/rvfi.rst Program counter)
- Notes: RVFI cosmetic; comparator masks bit 0 until fixed
- Intended reproducer: jalr to rs1 = odd address: rvfi_pc_wdata[0] = 1 while the next rvfi_pc_rdata[0] = 0.
- Evidence: (none yet; a committed sim log and, where useful, a waveform excerpt under dv/auto_dv/evidence/ close this field)

### B14: RVFI drops the ID-stage trap record when a WB load/store error coincides
- Status: downgraded to an RVFI convention note pending the confirmation simulation (rtl-arch T-041, fact-check row 48): the WB error has priority in FLUSH, the killed ID instruction re-executes after the handler and then produces its own record, so suppressing its record is correct; the confirmation program must show two trap records in order; one record re-opens it
- rtl-arch alias: BUG-04
- Features: F-RVFI-018 (canonical); cross-refs F-EXC-065 item, F-DMEM-034 item, F-ISA-051 item
- Expected-fail TP items: none as gate items (downgraded); confirmation items marked informational: TP-EXC-065, TP-ISA-051, TP-DMEM-063, TP-RVFI-039
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

## 2. Security-relevant RTL-defined behaviours (owner decision requested, not bugs)

| Ref | Behaviour | RTL | Owner question | Default applied |
|---|---|---|---|---|
| S1 (MEM-13) | Second half of a misaligned data access is issued after a first-half PMP fault; a faulting misaligned store performs its second-word write | rtl/ibex_load_store_unit.sv:489-531; rtl/ibex_core.sv:1063 | Q-DL-7 | modelled as RTL-defined, covered (F-PMP-087, TP-PMP-085) |
| S2 (CTRL-04) | Trap/debug entry updates CSRs and PC while fetch_enable_i is not On; invalid MuBi encodings act as Off with no alert | rtl/ibex_core.sv:644-649,1350-1351 | Q-DL-8 | checked as-is (F-RST-015, F-IMEM-023) |
| S3 (MEM-05/19) | No defence against unsolicited or grant-cycle rvalid on either bus; integrity check runs on such responses | rtl/ibex_load_store_unit.sv:756-757; rtl/ibex_icache.sv:721 | Q-DL-9 | never driven in passing tests; one informational test per bus (TP-IMEM-040) |

## 3. Doc defects (RTL is specification-legal or internally consistent; the Ibex doc is wrong or stale)

Merged list: reading report Section 5.3 plus rtl-arch A.2 (Critic C-23). Checker follows the RTL.

| ID | Defect | Doc location | RTL | Features |
|---|---|---|---|---|
| D1 | mip reads the raw irq pins, not qualified by mie | cs_registers.rst:246 | rtl/ibex_cs_registers.sv:408-412,495-501 | F-CSR-032 |
| D2 | Illegal mstatus.MPP value (01/10) legalises to U; doc says M | cs_registers.rst:138 | rtl/ibex_cs_registers.sv:783-786 | F-CSR-024 (BUG-05 alias) |
| D3 | mcause is software-writable; doc marks the fields read-only | cs_registers.rst:213-217 | rtl/ibex_cs_registers.sv:730-733,803 | F-CSR-046 |
| D4 | tdata1 reset/constant value is 0x2800_1048 (m=1,u=1), doc says 0x2800_1000 | cs_registers.rst:360 | rtl/ibex_cs_registers.sv:1848-1866 | F-TRG-003 / F-CSR-081 |
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
| D19 | security.rst dummy_instr_mask table lists 4 of the 8 legal values | security.rst | rtl/ibex_dummy_instr.sv:33-148 | F-DIT-012 |

## 4. Change log
- v1b (2026-09-03): expected-fail item lists refreshed from the plan parts after the Critic pre-review fold-in (B6/B12/B14 carry no expected-fail items; B15 items TP-CSR-075, TP-DBG-018).
- v1a (2026-09-03): folded rtl-arch T-017 (BUG-06 = B1, BUG-07 = B8 confirmed reachable, B9 out-of-spec stimulus, B10/B11 confirmed) and T-041 (BUG-04/B14 downgraded pending sim); B12 reclassified as documented behaviour with a design note (Critic pre-review S-1).
- v1 (2026-09-03): opened with B1..B15 (B6 reclassified per Critic C-20; B15 added per C-21; B5 re-cited per C-22), S1..S3, D1..D19 (D5 retired).
