# Critic verdict v1: DV feature-list draft (T-007 part 1)

- Artifact under review: dv/auto_dv/work/dv-lead/gen_feature_list_draft.md
  (sha256 first 16: 18b5552ffeda4307; 10741 lines, 999 features, 579 edge entries)
- Companion: dv/auto_dv/work/dv-lead/gen_reading_report.md (sha256 first 16: 9a7fd26f452d1c65)
- Reference inputs (read-only): dv/auto_dv/work/rtl-arch/gen_interface_inventory.md,
  gen_param_resolution.md, gen_hierarchy_map.md, gen_cheriot_carveout.md,
  gen_behaviour_summaries.md, gen_answers_tb_infra.md, gen_rv32b_otearlgrey_encodings.md,
  gen_exclusions_draft.md; dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md
- Date (UTC): 2026-09-03 05:25
- Reviewer role: critic (Claude Fable 5.1, this session; nine unnamed subagents did the sample
  checks; every finding below with severity medium or high was re-verified by the Critic against
  the cited RTL or specification lines before being recorded)
- Build configuration: opentitan (ibex_configs.yaml); DUT = gen_dut_top (ibex_core +
  ibex_register_file_ff), cheriot_enable_i tied IbexMuBiOff

CRITIC VERDICT: REQUEST-CHANGES

Severity counts: high 1, medium 12, low 9, info 4 (26 findings, C-01..C-26).

Method. Sample of 86 features spread over all 22 ID prefixes (4 per prefix, 5 for ISA/CSR/PMP,
3 for BTALU) plus F-CHERI-001; for each sampled feature the five fields, the boundary
observability of "Observable at", the programmable nature of "Config", every spec/doc citation
and at least the first two RTL citations were checked against tools/specs, doc/ and rtl/. The
whole list was then compared with the hierarchy map (FSM states, 57 hard arcs, paths P1..P13),
the interface inventory (77 ports, 20 protocol/driver rules) and the behaviour summaries
(CTRL-01..44, MEM-01..35, CSR-01..36, SEC-01..11, EX-01..11); the 579 edge entries were parsed
and a stratified sample of 97 classified; duplicates were found by title/What similarity; the
F-CHERI-001 table was mapped row by row onto gen_cheriot_carveout.md buckets A-F and spot-read
in the RTL. Fence: only this clone's rtl/, vendor/lowrisc_ip/ip, doc/, docs/dv, tools/specs and
dv/auto_dv/work files were read; no network, no git, no sibling clone. No fence event.

---------------------------------------------------------------------------------------------------
## Q1. Traceability groundwork (source, observation interface, configuration)

### C-01 (info) Sample result
Sampled: F-ISA-007/012/020/033/046, F-MUL-005/012/016/022, F-CMP-009/026/043/060,
F-BIT-006/016/026/036, F-BTALU-003/008/013, F-CSR-014/024/040/066/092, F-PRV-005/014/023/032,
F-EXC-009/026/043/060, F-IRQ-008/024/040/056, F-PMP-013/038/063/087/088, F-DBG-009/025/042/058,
F-TRG-004/012/020/028, F-PMC-007/020/033/046, F-IMEM-004/012/020/028, F-DMEM-006/018/030/042,
F-FE-003/010/017/024, F-IC-006/018/030/042, F-DIT-004/011/018/025, F-SEC-005/014/023/032,
F-RST-004/011/018/025, F-RVFI-004/013/022/031, plus F-CHERI-001 (Q5).
- Fields: 86/86 carry non-empty What / Observable at / Config / Source / Edge. Config names
  programmable state or "none" in 86/86 (F-PMC-033 mixes in a stimulus item, "instruction memory
  latency").
- Citations: HIT 71, PARTIAL 13, MISS 2. Hit rate 82.6% strict; 97.7% when a PARTIAL counts as
  "citation exists and supports the claim". The two MISS are C-02 and C-03; the PARTIALs are
  C-04 and C-05.
- Observable at names a DUT port or RVFI field in 82/86; F-PRV-014, F-PMP-038, F-PMC-033 and
  F-DIT-025 name none (see C-07).

### C-02 (medium) F-EXC-009 states a trap that the RTL and the privileged spec do not raise
- Location: F-EXC-009 What: "if a debug CSR (dcsr/dpc/dscratch/tselect/tdata) is accessed
  outside debug mode" raises illegal instruction. Source cites doc/03_reference/debug.rst:55.
- Evidence: rtl/ibex_cs_registers.sv:402 `illegal_csr_dbg = dbg_csr & ~debug_mode_i`; dbg_csr is
  set only in the CSR_DCSR/CSR_DPC/CSR_DSCRATCH0/1 arms (:550-565); CSR_TSELECT/TDATA1/2/3 (:636-651)
  set only `illegal_csr = ~DbgTriggerEn`, so with DbgTriggerEn=1 they are legal from M-mode.
  tools/specs/riscv-isa-manual/src/priv/csrs.adoc:60-63: "0x7A0-0x7AF are accessible to machine
  mode, whereas 0x7B0-0x7BF are only visible to debug mode" (tselect=0x7A0, dcsr=0x7B0,
  rtl/ibex_pkg.sv:518,526). debug.rst:54-55 is a doc defect already recorded by rtl-arch
  (gen_behaviour_summaries.md A.2, CTRL-30); the feature inherited it.
- Required: remove tselect/tdata from the trapping list in F-EXC-009; check F-CSR-017 and
  F-DBG-050 (same topic) for the same error; add the debug.rst defect to reading report 5.3.

### C-03 (low) F-PMP-038 arithmetic error
- Location: F-PMP-038 What: "pmpaddr = 0x1FFFFFFF (30 trailing ones, 2^32 bytes ...)".
- Evidence: 0x1FFFFFFF = 2^29 - 1 has 29 trailing ones; machine.adoc:3480-3488 (yy01..1 pattern,
  29 ones for XLEN=32 gives 2^XLEN). The region sizes in the claim are right.
- Required: fix the count; name an observable (rvfi_trap absent / data_req_o present).

### C-04 (low) Wrong-file, wrong-line or incomplete citations found in the sample
- F-DBG-042: "rtl/ibex_controller.sv:822 (stepie forced 0)" -> the fact is
  rtl/ibex_cs_registers.sv:821-822 (`dcsr_d.stepie = 1'b0`); controller.sv:822 is a comment.
- F-TRG-028: rtl/ibex_cs_registers.sv:1850 is maskmax; hit is :1851.
- F-PMC-046: rtl/ibex_id_stage.sv:1135 is perf_dside_wait_o; instr_kill is :1033-1036.
- F-DMEM-042: rtl/ibex_load_store_unit.sv:710-715 is gen_no_cap_rd, NOT elaborated under
  BaseIsaRV32IorCHERIoT; the elaborated arm is gen_memcap_rd :701-709 (data_tag_i gated at :704).
- F-ISA-046: add rtl/ibex_decoder.sv:912-919 (where csr_access_o is cleared).
- F-IMEM-028: PMP_I assignment is rtl/ibex_core.sv:1590 (range starts one line late).
- F-IRQ-056: doc path is doc/02_user/integration.rst:323-331, not doc/03_reference.
- F-EXC-060: doc/03_reference/pipeline_details.rst "Pipeline Details" is the document title and
  contains no exception-flush text (:27-30 says WB behaviour is undocumented); the feature is
  RTL-defined.
- F-PMC-007: machine.adoc "Environment Call and Breakpoint" does not say ecall/ebreak do not
  retire; only unpriv/zicntr.adoc:172-174 (also cited) does.
- Required: correct each citation; re-run the author's own grep/sed check on the parts.

### C-05 (medium) Factual or mechanism errors in sampled features
- F-ISA-012 What: "slli/srli/srai encodings whose instr[26:25] != 00 raise an illegal-instruction
  exception". rtl/ibex_decoder.sv:540-546: under funct3=101, instr[26]=1 decodes as fsri (legal
  with RV32B != None) before the instr[31:27] case; only instr[25]=1 with instr[26]=0 is illegal
  for srli/srai. A test expecting cause 2 for instr[26]=1 would be wrong.
- F-MUL-022: "because div_by_zero_q suppresses the final sign change" holds for div/divu only
  (rtl/ibex_multdiv_fast.sv:408); rem_change_sign (:409) has no div_by_zero_q term; results
  claimed are right, mechanism is wrong for rem/remu.
- F-FE-017: "up to 4 lines (32 bytes) ... can be requested before a redirect". rtl/ibex_icache.sv:
  247-250 with FB_THRESHOLD=2 (:74) and fb_fill_level (:690-697, counts the line being output):
  linear prefetch allocates at most 3 fill buffers (current line + 2 ahead); the 4th needs a
  branch lookup. Depth bins derived from 4 would be unreachable.
- F-IC-006: cited icache.rst:202-208 states a 72-bit data word (checkbits [71:64] over [63:0]),
  which contradicts the What (2 x 39-bit codewords). RTL (rtl/ibex_icache.sv:305-310,
  rtl/ibex_top.sv:221-223) supports the What; the feature must record the doc defect (as
  F-IMEM-028 does) instead of citing the doc as support.
- F-DIT-025: "prim_lfsr reloads DefaultSeed on the next lfsr_en": vendor/lowrisc_ip/ip/prim/rtl/
  prim_lfsr.sv:345-346 reloads DefaultSeedLocal, which under `ifdef SIMULATION on a non-Verilator
  simulator is randomised in about 70% of runs unless +prim_lfsr_use_default_seed=1 (:250-276).
  Whether the team's VCS build defines SIMULATION is unverified; the feature must state the
  dependency. Observable at names no port/RVFI field.
- F-SEC-032: "csrrs/csrrc read-modify-write must preserve the HW-owned bits 6/7 as read".
  rtl/ibex_cs_registers.sv:1967-1968 pass the raw write value for double_fault_seen and
  sync_exc_seen and :874-876 write them on every cpuctrlsts write; cs_registers.rst:551-557 marks
  them RW. Software can set or clear both bits. The checker expectation as written is wrong.
- Required: correct the six What fields; F-IC-006 adds the doc defect to reading report 5.3.

### C-06 (medium) Wrong RTL facts found outside the sample during cross-checks
- F-DBG-044 ("core_busy_o is low for the WAIT_SLEEP/SLEEP cycles only") and F-DBG-059
  ("core_busy_o dip of about two cycles"): rtl/ibex_controller.sv:606-621 clears ctrl_busy_o in
  SLEEP only in the else-branch of `irq_nm || irq_pending_i || debug_req_i || debug_mode_q ||
  debug_single_step_i`; with step set or in debug mode the SLEEP cycle stays busy, so the dip is
  exactly one cycle (WAIT_SLEEP, :598-604). gen_interface_inventory.md core_busy_o row and
  F-RST-016 have it right.
- F-RST-008 ("FIRST_FETCH until the first instruction is accepted by ID, then DECODE"):
  rtl/ibex_controller.sv:623-626 leaves FIRST_FETCH when id_in_ready_o, which is 1 in an empty
  pipe (:1020), so FIRST_FETCH is one cycle and DECODE waits for the instruction (CTRL-03,
  inventory reset paragraph: cycle 2 FIRST_FETCH, cycle 3 DECODE).
- Required: correct both; these define checker expectations for core_busy_o and the boot
  sequence.

### C-07 (medium) "Observable at" names no DUT port or RVFI field in 87 features
- Location: 87 features (61 of them edge entries) whose Observable at contains none of: rvfi_*,
  instr_*, data_*, irq_*, alert_*, core_busy_o, crash_dump_o, double_fault_seen_o, ic_*,
  debug_req_i, fetch_enable_i, boot_addr_i, hart_id_i, mcounteren_writable_i, rf_*, csrr /
  read-back, minstret/mcycle/mhpmcounter. Edge-entry list: F-PRV-014, F-EXC-005/007/013/014/022/
  024/042, F-IRQ-008/011/022/027/028/031/033/034/038/041/042/043/049/052/053/054/063/064,
  F-PMP-038/039/042, F-DBG-021/022/024/025/039/041/043/045/049/053/066, F-TRG-011/012/014/015/
  016/018/019/020/021/022/025/026/030, F-PMC-004/016/019/031/045, F-DIT-006/021/025. Most say
  "mcause=..., mtval=..." or "dpc = ..." without the csrr path, or "vector base+0x7C" without
  instr_addr_o. F-DBG-067 calls double_fault_seen_o "internal to cs_registers" although it is an
  ibex_core output (rtl/ibex_core.sv, port list :61-191; F-EXC-054 and F-CSR-091 use it).
- Evidence: DV_prompt.txt Section 5 step 1 ("at which interface it is observable"); Section 0 of
  the draft defines the csrr read-back convention but the field must still name it.
- Required: every Observable at names the port or RVFI field, using the Section 0 shorthand
  ("csrr read-back on rvfi_rd_wdata", "instr_addr_o = vector"); fix F-DBG-067.

### C-08 (low) Internal probe points named as observables
- F-DIT-011 (rf_raddr_*/dummy_instr_id_o, with a disclaimer), F-FE-012 ("internal ready/valid
  (bind point)"), F-CSR-001 ("hierarchical cs_registers_i.csr_wdata_int"). DV_prompt.txt Section 7:
  every probe needs a probe-register entry with rationale and reviewer approval; rf_*/dummy_*
  are wrapper-internal seam nets (rtl-arch answers section 9, item "e P1"), the other two are
  RTL internals.
- Required: mark each as "probe candidate (probe register entry needed)" or replace with the
  boundary observable; hand the list to TB Infra.

---------------------------------------------------------------------------------------------------
## Q2. Completeness against the RTL (hierarchy map, interface inventory, behaviour summaries)

### C-09 (medium) Hard arcs and control paths with no feature
Map: gen_hierarchy_map.md Part C. All reachable states of the 7 real FSMs and all 13 paths have
at least one feature; 50 of 57 hard arcs are covered. Uncovered or partial:
1. H-C1 non-exception variants (FSM-1 C20): debug_req_i sampled in the DECODE cycle in which a
   wfi / mret / dret / flushing CSR write takes FLUSH; entry to DBG_TAKEN_IF from FLUSH overrides
   WAIT_SLEEP (wfi never sleeps, core_busy_o never drops, dpc = wfi+4) or follows the mret
   (dpc = mepc, dcsr.prv = MPP) (rtl/ibex_controller.sv:985-987; CTRL-24). Only the exception
   variant is covered (F-DBG-004, F-EXC-048).
2. H-N1 (FSM-12): debug entry while executing the NMI handler (nmi_mode_q=1), then dret:
   nmi_mode_q stays 1, so pending mip&mie interrupts and a re-asserted irq_nm_i stay masked until
   the handler's mret; observable as no vector fetch / no rvfi_intr while irq_pending_o is high.
   F-IRQ-037/038 and F-DBG-056/057 cover only NMI arriving in debug mode (H-N2).
3. H-Z6 (FSM-10): cm.push/pop*/mv* halfword arriving with a fetch error (instr_err_i or PMP):
   expander must not start (valid_i=0, assertion IbexPushPopFSMStable), trap cause 1 with
   mtval = PC, no data_req_o. F-EXC-045 is the return-target case only.
4. H-I1 ALU class: two-cycle bitmanip op (rol/ror/cmov/fsl/fsr/crc32*/rori/fsri) whose second
   cycle is held by ready_wb_i=0 (slow load in WB); covered for mult/div (F-MUL-011/024), not for
   F-BIT-036/039.
5. H-D3 (FSM-5): divider FSM must not move while div_en_i=0 and state != MD_IDLE (map: believed
   unreachable, "DV should assert") - add as an assertion feature with a cover.
6. H-Z4 (FSM-10): the ret micro-op's pc_set de-asserts the expander's id_in_ready in the
   CmPopRetRa cycle (rtl/ibex_if_stage.sv:493): exactly one ret retires, single redirect.
7. P10: WB register-file write arbitration is one-hot (rf_we_wb_q & wb_valid_q vs rf_we_lsu,
   rtl/ibex_wb_stage.sv:183, :220, :310) - only F-RVFI-009 mentions the source select.
8. H-Y2: explicit cross of a dummy DIV (37 cycles) in ID with an arriving interrupt (F-DIT-019
   and F-DIT-024 imply it; no entry names it).
- Required: add one feature per item (or an explicit edge entry on the named parent) with a
  boundary observable.

### C-10 (medium) Protocol rules and behaviour-summary clauses with no feature
Inventory (gen_interface_inventory.md) and summaries (gen_behaviour_summaries.md); 77/77 ports
and every CTRL/MEM/CSR/SEC/EX heading map to a feature; the following rules or clauses do not:
1. "gnt must never be driven while req is 0": every LSU wait state takes a bare gnt as a grant
   (rtl/ibex_load_store_unit.sv:478,495,518,537); icache counts `fill_ext_arb & instr_gnt_i`
   (rtl/ibex_icache.sv:759-762). Inventory section 2 rule 2, section 3 driver rule 1, section 11.
2. Instruction-side unsolicited rvalid (MEM-19): silently ignored with no expecting buffer,
   otherwise consumed and shifting later responses. F-IMEM-007 covers only the same-cycle-as-grant
   case; F-SEC-017/019 are data side. Q-DL-9 names it as a design note; a feature is still needed
   for the informational directed test the DV Lead proposes there.
3. Driver rule 8 (never drive X on data_rdata_i while rvalid; the decoder sees X as an error).
4. MEM-08/MEM-15: the 7 SECDED bits of data_wdata_o cover all 32 bits including disabled lanes,
   and valid ECC is driven for loads too. F-DMEM-014/041 give rotation and width only; F-DMEM-035
   calls load wdata don't-care, which conflicts with MEM-15 and with the store-integrity checker
   TB Infra plans (STATUS item 10).
5. MEM-23: 258-cycle minimum from reset release to INVAL_IDLE (rtl/ibex_icache.sv:1221-1255);
   F-IC-022 states only the 256 write cycles.
6. MEM-26: disabling the cache does not invalidate; re-enabling makes old lines hittable (only the
   debug-mode case, F-IC-040).
7. CTRL-24 mret / CSR-flush debug-entry variant (same as C-09 item 1).
8. EX-09: writeback write timings (WB-flop write the cycle after ID; load write at data return
   directly from the LSU; stores never write; one-hot sources).
- Required: add features (protocol rules become passive assertions per the IMEM part preamble);
  reconcile F-DMEM-035 with MEM-15.

### C-11 (info) Cross-check results that are rtl-arch's to fix, not the draft's
- gen_hierarchy_map.md H-L4 ("PMP error on the first half of a misaligned access ... no bus
  request at all") is wrong; F-PMP-087/F-EXC-033 and MEM-13 are right: WAIT_RVALID_MIS drives
  data_req_o with the second address (rtl/ibex_load_store_unit.sv:503-507, :510) and
  rtl/ibex_core.sv:1063 gates only on the current word's PMP result.
- gen_behaviour_summaries.md CSR-23 ("misaligned = 2" loads) repeats the doc; F-PMC-034/036 are
  right (perf_load_o only in the IDLE request branch, :474-475).
- H-I4's premise (ID mid-misaligned-request while WB holds a load) is prevented by
  data_req_allowed = ~outstanding_memory_access (rtl/ibex_id_stage.sv:1019); restate or drop.
- P12 "dummies increment minstret: unverified" is resolved by F-DIT-018/F-PMC-011 (BUG-02).
- EX-04 says sroi/grevi/gorci/unshfli ignore instr[26:25]; F-BIT-037 is right that only
  instr[25] is lenient (instr[26]=1 is fsri, rtl/ibex_decoder.sv:540-541).
- rtl-arch A.1 lacks B1 (dret leaves MPRV set); the DV Lead's follow-up stands. Sdext.adoc:202
  ("If the new privilege mode is less privileged than M-mode, MPRV in mstatus is cleared") confirms
  the spec rule; rtl/ibex_cs_registers.sv:949-951 only restores priv_lvl.
The Critic will forward these to rtl-arch through the Orchestrator; no change to the draft.

---------------------------------------------------------------------------------------------------
## Q3. Edge cases (distinct, boundary-observable scenarios or restatements)

### C-12 (medium) About one edge entry in four is a restatement of its parent
- Data: 579 edge entries, 0 dangling parents, 27 depth-2 chains (C-13). Stratified sample of 97
  (every 6th): GENUINE 75, RESTATEMENT 22, UNOBSERVABLE 0 (22.7%; extrapolated about 130 of 579).
  All 13 ISA/CMP operand-extreme entries (F-ISA-002/003/006/008/009/011/016/022/026/027,
  F-CMP-011/017/067) are genuine: concrete boundary values with distinct expected results.
- Restatement patterns with the sampled instances:
  (a) one row or term of the parent's own enumeration or truth table: F-PMP-062 (two rows of
      F-PMP-056's Smepmp table), F-IRQ-034 and F-IRQ-063 (rows of F-IRQ-009's priority table),
      F-SEC-016 (one OR term of F-SEC-003), F-DBG-027, F-FE-024, F-IRQ-049;
  (b) the parent's own Config variable at another value: F-DIT-004 (DIT off vs F-DIT-003 on),
      F-DBG-034, F-PRV-003;
  (c) the parent's What repeated: F-CMP-033 (c.ebreak, already in F-ISA-034), F-CMP-066 (mtval =
      zero-extended halfword, already in F-ISA-047), F-EXC-039 ("no rollback" already in
      F-EXC-027), F-CSR-052, F-DMEM-005 (delayed grant is F-DMEM-001's scenario), F-IRQ-027;
  (d) checker bullets without a distinct stimulus: F-EXC-063, F-RVFI-029, F-PRV-032; and
      F-BIT-011 (a base feature mislabelled as an edge of its own special case), F-BIT-036,
      F-BTALU-005 (not-taken is the other half of F-BTALU-001).
- Evidence: DV_prompt.txt Section 5 step 2 (edge cases are their own items with their own bins;
  the examples are coincidences and full/empty structures); dv_principles.md Section 4 ("No
  duplicate coverpoints - extend, don't re-cover"). A restated edge becomes a duplicate bin and
  inflates the completeness measure.
- Required: review all 579 edge entries; keep an entry as an edge only if its What names a
  stimulus condition or timing coincidence the parent does not, and its Observable at differs;
  otherwise fold it into the parent as one of the parent's bins (pattern (a)) or delete it
  (patterns (b)-(d)). Record the rule in Section 0.

### C-13 (low) Edge bookkeeping errors
- F-EXC-047 ("Exception in debug mode does not arm double-fault detection") is "Edge: yes, of
  F-EXC-053" (mstatus.MPP WARL); the parent is F-EXC-054 (double-fault detection).
- 27 edge entries point at a parent that is itself an edge: F-ISA-051, F-MUL-022, F-BIT-039,
  F-EXC-034/040/047, F-IRQ-022/027/029/036/038, F-PMP-005/039/044/065/099/100, F-TRG-022,
  F-PMC-051, F-DMEM-023/025/026/027, F-FE-022, F-IC-042, F-DIT-027, F-RVFI-014. Point them at
  the base feature so the traceability table has one level.
- Required: fix the parent IDs.

---------------------------------------------------------------------------------------------------
## Q4. Duplicates and overlaps beyond Section 3

### C-14 (medium) About 60 duplicate clusters (about 140 features) are not acknowledged
Section 3 names 10 overlap clusters. Reading the candidate pairs found these additional clusters
whose members state the same behaviour, observable and config (canonical owner is the DV Lead's
choice; the first ID is a suggestion):
- ebreak into debug mode: F-ISA-035, F-EXC-019, F-DBG-017, F-DBG-019; c.ebreak = ebreak:
  F-EXC-018, F-DBG-022, F-CMP-033 (and parent F-ISA-034); ebreak in debug mode: F-EXC-020, F-DBG-023
- mret in U-mode illegal: F-ISA-037, F-EXC-010, F-PRV-010; dret outside debug illegal: F-ISA-039,
  F-EXC-012, F-DBG-032, F-PRV-025; wfi in U-mode with TW: F-ISA-041, F-EXC-011, F-PRV-016
- CSR instruction rules: F-ISA-044/F-CSR-002/F-CSR-012; F-ISA-045/F-CSR-003/F-CSR-013;
  F-ISA-046/F-CSR-005; illegal reporting F-ISA-047/F-EXC-008; F-ISA-050/F-EXC-016;
  instruction-address-misaligned never raised: F-ISA-052, F-FE-011, F-EXC-067
- Counter CSRs listed in full twice (CSR vs PMC): F-CSR-062/F-PMC-001, F-CSR-063/F-PMC-004,
  F-CSR-064/F-PMC-005, F-CSR-066/F-PMC-007, F-CSR-050(+052)/F-PMC-025, F-CSR-058(+060)/F-PMC-020
- Debug CSRs (CSR vs DBG): F-CSR-017/F-DBG-050, F-CSR-074/F-DBG-012, F-CSR-076/F-DBG-016,
  F-CSR-082/F-TRG-007; cpuctrlsts: F-CSR-085/F-SEC-031; icache off in debug mode listed five
  times: F-CSR-086, F-SEC-033, F-DBG-062, F-IC-040, F-FE-022; id CSRs F-CSR-019/F-SEC-037;
  mhartid F-CSR-020/F-RST-005; mtvec WARL F-CSR-035/F-IRQ-013; F-CSR-026/F-IRQ-059
- PRV vs IRQ: F-PRV-011/F-IRQ-032, F-PRV-012/F-IRQ-023, F-PRV-018/F-IRQ-053, F-PRV-019/F-IRQ-046,
  F-PRV-020/F-IRQ-045, F-PRV-024/F-IRQ-008, F-PRV-029/F-IRQ-009, F-PRV-031/F-IRQ-030(+033);
  F-PRV-005/F-DBG-026(+F-PMP-099); F-PRV-007/F-PMP-074/F-EXC-052; F-PRV-014/F-PMP-073
- Faults listed from the exception side and the bus/PMP side: F-EXC-005/F-IMEM-013/F-PMP-068;
  F-EXC-006/F-IMEM-012/F-PMP-079; F-EXC-025/F-DMEM-036; F-EXC-027/F-DMEM-037;
  F-EXC-026/F-EXC-028/F-PMP-082; F-EXC-031/F-DMEM-022; F-EXC-032/F-PMP-088(+F-PMC-037,
  F-RVFI-014); F-EXC-035/F-PMP-085/F-DMEM-038
- Double fault: F-EXC-054/F-SEC-022/F-CSR-089; F-EXC-057/F-SEC-025/F-CSR-091;
  F-EXC-047/F-DBG-067/F-SEC-023
- Others: F-IRQ-056/F-RST-015 (same owner question twice), F-IRQ-039/F-DBG-056,
  F-IRQ-016/F-RVFI-029, F-IRQ-065/F-RST-006 (What Jaccard 0.83), F-PMP-095/F-DBG-052,
  F-DBG-065/F-RVFI-018, F-DBG-008/F-RST-024, F-IMEM-025/F-RST-012, F-IC-011/F-SEC-021,
  F-FE-020/F-SEC-007
- Evidence: DV_prompt.txt Section 4 (completeness = every feature maps to an item and a bin;
  duplicates count a behaviour several times); dv_principles.md Section 4 (no duplicate
  coverpoints).
- Required: extend Section 3 to every cluster with one canonical entry and cross-references (the
  T-006 promotion rule already planned); count each behaviour once in the completeness measure;
  where two members differ only by area perspective, keep the member whose area owns the
  observable and reference it from the other area's test-plan item.

### C-15 (low) Section 3 references that do not resolve
- "F-DMEM-02x split-access entries" (misaligned PMP item): F-DMEM-020..027 are bus-error and
  grant-timing variants, not PMP; the PMP second-half cluster is F-PMP-088, F-EXC-032,
  F-PMC-037, F-RVFI-014, F-CMP-062.
- "F-RST (canonical)" -> F-RST-002/003/004/025; "F-CSR mtvec entries" -> F-CSR-035/036/037;
  "F-DBG Zcmp entries" -> F-DBG-010/046; "F-SEC" -> F-SEC-002/010; "F-PMP notes" -> no F-PMP
  feature mentions shadow CSRs (only the part preamble at line 4897).
- Carriers not named: F-PMP-097 (MPRV in debug mode), F-CMP-059/063, F-TRG-023, F-DMEM-046
  (Zcmp masking), F-IRQ-014 and F-IMEM-026 (boot mtvec / reset PC).
- Required: resolve every reference to explicit IDs.

---------------------------------------------------------------------------------------------------
## Q5. CHERIoT carve-out (F-CHERI-001 table vs gen_cheriot_carveout.md buckets A-F)

Facts: the table has 71 data rows (the reading report says 60). Exclusion name
"cheriot-out-of-scope" is identical in the feature, the carve-out and gen_exclusions_draft.md.
The isolation assertions (rtl/ibex_id_stage.sv:1295-1300, rtl/ibex_load_store_unit.sv:832-834,
rtl/ibex_cs_registers.sv:1995-1997: keep enabled) and the vacuous register-file
Cheriot*MSBClear assertions (:235-239: exclude) are treated the same way in both documents; the
csr_mshwm_set_o note agrees with carve-out G3/F17 (rtl/ibex_cheriot_ex.sv:991-994 verified).
Row agreement count: 39 agree, 15 lump an unreachable sub-arm under "yes" (harmless, the
exclusion file handles the sub-arm), 11 disagree on classification without hiding RV32I
coverage (C-17), 6 mark live RV32I logic "no" (C-16), 0 rows wholly unmapped, 5 carve-out items
have no row (C-18).

### C-16 (high) Six "no" rows would exclude live RV32I logic
"Reachable when Off = no" is defined in the table as dead logic to exclude. The Critic read each
row's cited lines in the RTL:
1. rtl/ibex_controller.sv:828-840 ("CHERI fault causes (28), mtval encodings" -> no): :827-831
   is the FLUSH exception entry for EVERY trap (`if (exc_req_q || store_err_q || load_err_q ||
   ...) pc_set_o = 1; pc_mux_o = PC_EXC; exc_pc_mux_o = ...`) and :833-840 selects mepc source
   (csr_save_id_o / csr_save_wb_o). Only the `(cheriot_enable_i == IbexMuBiOn) & cheriot_wb_err_q`
   terms are dead.
2. rtl/ibex_controller.sv:901-921 (same row): :909-913 is the live store access-fault arm
   (`exc_cause_o = ExcCauseStoreAccessFault; csr_mtval_o = lsu_addr_last_i`) and :914 the load
   priority header; the dead ranges are :901-908 and :915-922 (carve-out bucket C).
3. rtl/ibex_controller.sv:866-867 (same row): one statement, the illegal-instruction mtval assign
   (:866-868); its RV32I arm is live (carve-out F9). Only a branch exclusion of the CHERIoT arm
   is legitimate, never a line exclusion.
4. rtl/ibex_controller.sv:234-259 (no): :255 `illegal_insn_d = illegal_insn_i & (ctrl_fsm_cs !=
   FLUSH)` is live; the carve-out covers only :234, :236-240, :256-257, :259.
5. rtl/ibex_id_stage.sv:1030-1035 (no): :1033-1036 `instr_kill = instr_fetch_err_i | wb_exception
   | id_exception_nc | ~controller_run` gates instr_executing for every instruction (carve-out
   F11 "live"); :1012 and :1093-1096 in the same row are live lines with one constant-0 OR term
   (condition-bin exclusion only).
6. rtl/ibex_cs_registers.sv:1058-1070 (no): mstatus_en_combi / mstatus_d_combi are the write
   enable and next-value mux for ALL mstatus writes (`mstatus_en | 0`; `mstatus_d.mie & ~0 | 0`),
   carve-out F8 "must stay in coverage".
7. rtl/ibex_load_store_unit.sv:642-656 (no, "stays CRX_IDLE"): :650-653 are the live LSU FSM
   state flop and handle_misaligned_q / pmp_err_q / lsu_err_q; dead lines are :642-648, :654, :656.
8. rtl/ibex_core.sv:1350-1351 (no): the alert_major_internal_o assign with live terms
   rf_ecc_err_comb | pc_mismatch_alert | csr_shadow_err; only the two constant-0 OR terms are
   excludable (carve-out E; gen_exclusions_draft.md A.4).
- Evidence: gen_cheriot_carveout.md A.3/A.4 (list live nets by name, never sweep them in;
  exclude by cited line/branch lists, never by block label where the block holds live RV32I
  logic); DV_prompt.txt Section 4 (control-logic exclusions need an unreachability argument and
  reviewer approval). Applying these rows as written would silently hide coverage on trap entry,
  mstatus writes, instruction kill and the security alert.
- Required: rewrite each row to cite exactly the dead sub-arm or term, with the exclusion kind
  (line / branch / condition / toggle) as gen_exclusions_draft.md Part A does; add "yes (live)"
  rows for the RV32I lines now swept in; state in the feature that gen_exclusions_draft.md (rtl-
  arch) is the authoritative exclusion list and the table must match it row for row.

### C-17 (medium) Row verdicts that disagree with the carve-out classification
- Rows citing the UNREACHABLE CHERIoT arm while saying "yes" and describing the other arm:
  rtl/ibex_decoder.sv:314-323, 339-348 (RV32 jump arms are :324-334, :353-363); :474-482 (RV32
  auipc is :483-485); :788-870 and :882-891 ("yes as illegal instruction": the illegal arms are
  :877-878 and :892-893, outside the cited ranges; the cited bodies are dead); :402-409, 444-455
  (:408-410, :454-456 live); the rtl/ibex_compressed_decoder.sv row cites only the `== IbexMuBiOn`
  arms (dead) although the standard-RVC else-arms are the live ones.
- rtl/ibex_core.sv:214-215,234,286-287,430-490 "yes (constant 0)": csr_mshwm_new (:490) toggles
  (rtl/ibex_cheriot_ex.sv:994 `csr_mshwm_new_o = {lsu_addr_o[31:4], 4'h0}`); carve-out bucket D /
  F13 lists it as toggling-but-dead.
- rtl/ibex_cheriot_ex.sv row "yes for ... wcap muxes": lsu_wcap_o (:959) is constant NULL_CAP.
- rtl/ibex_load_store_unit.sv:419-471 "yes" (row 36) overlaps :464-466 "no" (row 37).
- rtl/ibex_if_stage.sv:368,445-472 "no" and rtl/ibex_cs_registers.sv:2000-2257 "no": carve-out
  marks instr_hdrm/hdrm_ge* (:447-449) and the gen_scr nets pcc_exc_cap/tr_cap/tf_cap/pcc_cap_d/
  mstack_epc_cap_q (:2061, :2079-2105, :2126-2132) as TOGGLING; gen_exclusions_draft.md A.3
  excludes gen_scr only by sub-blocks (:2014-2056, :2063-2067, :2108-2209, :2218-2224). No RV32I
  behaviour is hidden, but the table must not exclude by block label where the carve-out forbids it.
- Notes: "RegFileCapEccWidth = REGCAP_W (35) as ibex_top does" contradicts carve-out F4 (must be
  REGCAP_W+7 = 42 if RegFileECC=1, else the part-select at rtl/ibex_core.sv:1264/:1271 is
  reversed). State RegFileECC=0 explicitly (Q-DL-1 default) and the consequence.
- Required: cite the live arm in "yes" rows, the dead arm in "no" rows; fix the three factual
  notes; remove the row-36/37 overlap.

### C-18 (medium) Carve-out entries missing from the table
- rtl/ibex_cs_registers.sv:707-715 (PMP-CSR illegal block, UNREACH; gen_exclusions_draft.md A.3
  block exclusion).
- Bucket F8: depc/dscratch0/dscratch1 *_en_combi / *_d_combi (:1203-1204, :1220-1222,
  :1238-1240) - live RV32I CSR-write logic; the table's row 59 has mepc/mtvec only.
- Bucket F10: rtl/ibex_core.sv:1851-1853 rvfi_id_done suppression (live; BUG-04).
- rtl/ibex_load_store_unit.sv:664-667 (resp_is_cap_q update on lsu_go); rtl/ibex_core.sv:
  2346-2361 rvfi_rd_cap_d (constant).
- Bucket F items F8, F9, F10, F11, F13 are not represented as live anywhere in the table.
- Required: add rows; every bucket-F item appears as "yes (live RV32I, never excluded)".

### C-19 (low) Table bookkeeping
- 71 rows, not 60 (gen_reading_report.md Section 7 item 3).
- Eleven "yes (constant 0)" rows (ports and internal nets) describe constant nets that need a
  toggle exclusion (carve-out bucket D, gen_exclusions_draft.md A.5), but the table's closing
  note says only "no" rows are excluded. State the rule: the exclusion file is authoritative,
  the table records the DV consequence (negative check / constant-value monitor) per row.
- Required: fix the count; add the rule sentence.

---------------------------------------------------------------------------------------------------
## Q6. Bug-candidate consistency (reading report Section 5 vs rtl-arch A.1 and security flags)

Consistent and correctly classified (verified): B1 = Sdext.adoc:202 rule vs
rtl/ibex_cs_registers.sv:949-951 (spec violation; absent from rtl-arch A.1, follow-up filed);
B2 = BUG-01; B3 supported by Sdtrig.adoc:370 ("Attempts to access an unimplemented Trigger
Module Register raise an illegal instruction exception") vs :648-663 reading 0; B7 = BUG-02;
B14 = BUG-04; MPP legalisation = BUG-05 (5.3, RTL spec-legal, doc wrong); MEM-13 / CTRL-04 /
MEM-05+19 = Q-DL-7/8/9; B8-B13 marked static-reading / needs repro, which is honest.

### C-20 (medium) B6 is misclassified as "RTL contradicts a specification"
- Location: reading report 5.1 B6 (F-EXC-046): "Exception taken in debug mode forces priv to M".
- Evidence: Sdext.adoc:32 "All operations are executed with machine mode privilege" (in debug
  mode); :51 "Almost all instructions that change the privilege mode have UNSPECIFIED behavior"
  in debug mode. rtl/ibex_cs_registers.sv:908 sets priv_lvl_d = M for every exception including
  debug entry, so the hart is already at M throughout debug mode; dcsr.prv is untouched (:918
  guard). The only path to a non-M priv_lvl inside debug mode is mret in debug mode (CTRL-31),
  which the spec leaves UNSPECIFIED. There is no observable spec contradiction.
- Required: move B6 to "RTL-defined (spec UNSPECIFIED)"; no expected-fail test; keep the
  behaviour as a feature (F-EXC-046) with the RTL as reference.

### C-21 (medium) BUG-03 (dcsr.ebreaks writable) belongs in 5.1, not 5.3
- Location: reading report 5.3 "dcsr bit 13 (ebreaks) writable, doc says other fields read zero
  (F-CSR-076, F-DBG-016)" - filed as a doc mismatch where the RTL is spec-legal.
- Evidence: tools/specs/riscv-debug-spec/xml/core_registers.xml:163-172, dcsr.ebreaks: "This bit
  is hardwired to 0 if the hart does not support S-mode". Ibex has no S-mode (misa =
  0x40901104, rtl/ibex_cs_registers.sv:373-391). rtl/ibex_cs_registers.sv:810-836 forces every
  other field but not bit 13. This is a WARL hardwire violation of the debug specification, as
  rtl-arch classifies it (BUG-03).
- Required: move to 5.1 with checker direction "reads 0", expected-fail until ruled; the
  functional impact is nil (rtl/ibex_controller.sv:481-483 never reads it) and should be stated.

### C-22 (low) B5 cites the wrong document
- Location: 5.1 B5 (F-IRQ-037): "Sdext.adoc defines nmip". Sdext.adoc contains no occurrence of
  nmip; the definition is tools/specs/riscv-debug-spec/xml/core_registers.xml:292-298 (access R:
  "When set, there is a Non-Maskable-Interrupt (NMI) pending for the hart ... This is
  implementation-dependent"). The argument (a read-only status field that never reports a
  pending NMI) still stands but must be stated against that text.
- Required: re-cite; note the generated-field-table location for every dcsr/tdata claim
  (reading report Section 3 item 4 already plans to read xml/ in T-006).

### C-23 (low) Section 5.3 is not reconciled with rtl-arch A.2
- rtl-arch doc defects with no entry in 5.3 or in a feature Note: debug.rst:54-55 trigger CSRs
  "Debug Mode only" (CTRL-30; the draft adopts the wrong claim, C-02); cs_registers.rst:544-545
  vs icache.rst:113-116 on fence.i and the scramble key (D4; no feature mentions "guaranteed to
  fetch a new key"); icache.rst branch_spec_i port (D2; 0 mentions); pipeline_details.rst:63
  "37 stall cycles" vs 36 stall / 37 total (EX-03); cs_registers.rst CSR table omissions
  mcounteren/mstatush/menvcfg/mconfigptr (CSR-02); tselect "DbgHwNumLen" and scontext 0x7AA
  (present in the draft: confirm they are marked as doc defects).
- Required: one merged doc-defect list (rtl-arch A.2 + reading report 5.3) with feature IDs.

### C-24 (info) rtl-arch items the DV Lead should push back on
- H-L4 and CSR-23 (C-11) are rtl-arch errors that contradict correct features; the
  reconciliation task T-017 should correct the map and the summary, not the features.

---------------------------------------------------------------------------------------------------
## Q7. Honesty and fence

### C-25 (info) No sign of adopted Ibex DV collateral; no silent narrowing
- grep of the draft for riscv-dv, core_ibex, testplan, adopted, cosim, uvm, testlist, lowRISC /
  OpenTitan DV: no hits (one allowed mention of Spike as the reference model). Every "out of
  scope" / "excluded" statement traces to the CHERIoT ruling, the lockstep ruling (line 9671) or
  a CHERIoT-only FSM state. The DV Lead's STATUS records no web search and no fetch; the
  reading report lists sources per area. Consistent with DV_prompt.txt Sections 3 and 10.

### C-26 (low) Three overstated statements
- Section 0: "every RTL line citation was verified by the author with grep/sed": the sample has 2
  MISS and 13 PARTIAL of 86, including wrong-file (F-DBG-042), wrong-generate-arm (F-DMEM-042)
  and off-by-one (F-TRG-028) cites, and the F-CHERI-001 rows in C-16 cite line ranges whose
  content the row text does not describe. Rephrase to what was done (spot-checked) or make it
  true.
- Section 1 table: "27 ID prefixes"; there are 22 (ISA, MUL, CMP, BIT, BTALU, CSR, PRV, EXC,
  IRQ, PMP, DBG, TRG, PMC, IMEM, DMEM, FE, IC, DIT, SEC, RST, RVFI, CHERI). The reading report
  repeats 27.
- Reading report Section 7 item 3: "60 rows"; the table has 71.
- Evidence: dv_principles.md Section 4 "Evidence over inference ... State unverified claims as
  unverified"; DV_prompt.txt Section 10.
- Required: correct the three statements.

---------------------------------------------------------------------------------------------------
## What the DV Lead must change before promoting the list to dv/auto_dv/docs/gen_feature_list.md

Fix the F-CHERI-001 table so that no "no" row contains live RV32I logic and every carve-out
bucket-F item appears as live (C-16, C-17, C-18), and make gen_exclusions_draft.md the
authoritative exclusion list the table mirrors. Correct the wrong RTL facts that a checker would
inherit (C-02 trigger CSRs, C-05 six features, C-06 core_busy_o in SLEEP and FIRST_FETCH) and
the wrong-file / wrong-line citations (C-03, C-04). Give every feature a boundary observable in
its own field (C-07, C-08). Add the eight uncovered hard arcs and the eight uncovered protocol
rules / summary clauses as features (C-09, C-10). Re-examine the 579 edge entries against the
"distinct stimulus condition and distinct boundary observable" rule and fold the restatements
into their parents' bins (C-12, C-13). Extend Section 3 to all duplicate clusters with one
canonical entry per behaviour and resolve every dangling reference (C-14, C-15). Reclassify B6
as RTL-defined and BUG-03 as a spec violation, re-cite B5, and merge the doc-defect lists
(C-20..C-23). Correct the three overstated counts / claims (C-26). REQUEST-CHANGES stands until
every high and medium finding is addressed or the owner overrules through the intervention log;
the Critic re-reviews the promoted file (T-007 part 2) together with the test plan and coverage
plan traceability.

Notes for other roles (forwarded through the Orchestrator, no action in this draft): rtl-arch
H-L4, CSR-23, H-I4, EX-04 bit-26 wording, P12 minstret (C-11, C-24); TB Infra: probe candidates
in C-08, F-DMEM-035 vs MEM-15 store-integrity checker scope (C-10 item 4).
