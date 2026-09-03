# Coverage exclusions: draft content, justification and mechanism (opentitan configuration) -- v2

Owner: rtl-arch (T-015 v1, revised to v2 under T-022 after the Critic's REQUEST-CHANGES,
dv/auto_dv/docs/gen_critic_exclusions_draft_v1.md). STATUS: DRAFT v2, 2026-09-03. Nothing here
is applied. The final, machine-generated exclusion file (gen_ prefix, under dv/auto_dv/) is what the
Critic approves, against the evidence in dv/auto_dv/work/rtl-arch/gen_unreachability_evidence.md
(evidence classes EC-1..EC-6 as the Critic defined them). Point-by-point response to the rulings:
dv/auto_dv/work/rtl-arch/gen_critic_response_exclusions_v1.md.

What changed from v1: A.1 whole-instance exclusion replaced by the object-list procedure (R-1);
class D uses six explicit entries with enum/spare-count/assertion annotations, `-line nocasedef`
dropped (R-2); class P narrowed to the inner blocks (R-3); A.8 completed with ten named items and
the authority statement (R-4); Part B gained the flow rules B.7 (R-5) and the Runtime T-010 facts
(dv/auto_dv/evidence/gen_t010_compile_path.md: instance names confirmed, FSM metric reported,
constant analysis partial, condition coverage gated, UCAPI-CSM glitch); Part C rows carry their
evidence pointer; class R carries the Critic's EC-4 property. Object inventories referenced:
gen_cheriot_carveout.md (CC, buckets A-F with file:line, gating chain G1-G8), gen_hierarchy_map.md
Part C section 1 (transition audit).

Instance paths (T-010 confirmed): the coverage tree is `<tb_top>.u_dut` (today
gen_smoke_tb_top.u_dut; the real TB top keeps u_dut), with `u_dut.u_ibex_core`,
`u_dut.u_ibex_core.g_cheriot_ex.u_ibex_cheriot_ex`, `u_dut.u_register_file`. MODULE: scope is
exact for every shared module (one instance each).

## Part A. The "cheriot-out-of-scope" carve-out as exclusion entries

A.0 Justification text carried in every ANNOTATION (DV_prompt Section 4):

  "cheriot-out-of-scope: owner ruling DV_prompt.txt Section 2 (2026-09-02). gen_dut_top ties
   ibex_core.cheriot_enable_i to ibex_pkg::IbexMuBiOff (4'b1010) (dv/auto_dv/tb/gen_dut_top.sv:202).
   Every object in this entry is reachable only when cheriot_enable_i == IbexMuBiOn (4'b0101) or
   is a constant function of that tie. Proof chain: gen_cheriot_carveout.md Part B section 0
   (G1-G8) item <Gn>, bucket <X> item <n>; machine evidence gen_unreachability_evidence.md 4.1
   (assertion <T022_name>, k-induction PASS)."

A.1 u_ibex_cheriot_ex: object-list exclusion inside the instance (R-1; whole-instance REJECTED)

Procedure (Runtime executes, rtl-arch selects, Critic approves):
1. `urg -dump full_exclusions -hier <dut_hier> -dir <measured.vdb>` for the instance
   `<tb_top>.u_dut.u_ibex_core.g_cheriot_ex.u_ibex_cheriot_ex` (all metrics).
2. Remove from the dump every object of the LIVE list below; everything left is excluded under
   one ANNOTATION_BEGIN/END carrying A.0 with "CC A1, bucket C/D item <n>".
3. Add Branch entries ONLY for the CHERIoT arms of the live ternaries (:943-960 true-arms of
   `instr_is_cheriot_i ? ... :`, and the `: 1'b0` false-arm of :970-971) and Condition entries for
   the vectors where `instr_is_cheriot_i` or `(cheriot_enable_i != IbexMuBiOn)` takes its impossible
   value; the lines themselves and the RV32I arms stay in coverage.
4. Toggle entries (`-cm_tgl portsonly`) only for the CONSTANT ports listed below.

LIVE objects (never excluded; verified in rtl/ibex_cheriot_ex.sv on 2026-09-03):
- :943 `lsu_req_o = instr_is_cheriot_i ? cheriot_lsu_req : rv32_lsu_req_i` (RV32I arm live);
  :945-948 cpu_lsu_cheriot_err / cpu_lsu_addr / cpu_lsu_we / cpu_lsu_wdata muxes (RV32I arms);
  :951-954 lsu_cheriot_err_o, lsu_we_o, lsu_addr_o, lsu_wdata_o; :958 lsu_type_o; :960
  lsu_sign_ext_o; :970-971 rv32_addr_incr_req_o (true-arm live: `(cheriot_enable_i != IbexMuBiOn)`
  is constant 1, so the select is always true); :973 rv32_addr_last_o; :991-994 csr_mshwm_set_o
  terms and csr_mshwm_new_o (toggle with lsu_addr_o; csr_mshwm_set_o itself is constant 0, see
  evidence 4.1 note: it is 0 through the mshwm/mshwmb CSR chain, not by a direct tie); :219-233
  fwd_data_merger nets and the operand gating (`instr_is_rv32lsu_i` arm live).
- Live PORTS (toggle objects that stay): lsu_req_o, lsu_we_o, lsu_addr_o, lsu_wdata_o, lsu_type_o,
  lsu_sign_ext_o, rv32_addr_incr_req_o, rv32_addr_last_o, rv32_lsu_req_i, rv32_lsu_we_i,
  rv32_lsu_type_i, rv32_lsu_wdata_i, rv32_lsu_sign_ext_i, rv32_lsu_addr_i, rv32_lsu_err (input),
  addr_incr_req_i, addr_last_i (:80-81), csr_rdata_i, csr_mstatus_mie_i (:93, :95), csr_mshwm_new_o
  (:994, dead but toggling: not excludable under EC-5), fwd_wdata_i, fwd_* selects, rf_rdata_a_i,
  rf_rdata_b_i, pc_id_i, debug_mode_i, instr_valid_i, instr_first_cycle_i, instr_is_compressed_i,
  instr_is_rv32lsu_i, clk_i, rst_ni.
- CONSTANT ports (Toggle entries, both edges): fwd_wcap_i, rf_rcap_a_i, rf_rcap_b_i, pcc_cap_i,
  pcc_cap_o, csr_mshwm_i, csr_mshwmb_i, csr_mshwm_set_o (constant 0), csr_rcap_i, csr_wcap_o,
  lsu_wcap_o (constant NULL_CAP, :959), lsu_is_cap_o, lsu_lc_clrperm_o, lsu_cheriot_err_o, and
  every cheriot_* port (CC bucket D "Port-level view").
- Evidence: EC-1 (CC A1 + G3; k-induction T022_DEC_CHERI0 `instr_is_cheriot_o == 0`, T022_ID_CHERI0
  `cheriot_exec_id_o == 0`, evidence 4.1), EC-2 (T-010: constant analysis already marks 5 line rows,
  54 condition vectors and 22 toggle rows Unreachable in this instance; the rest needs the entries),
  EC-3 (isolation assertions rtl/ibex_id_stage.sv:1297-1300, rtl/ibex_load_store_unit.sv:833-834),
  EC-5 (strict load on the measured merge).
- No `MODULE:`/`INSTANCE:` scope-wide entry anywhere in the file (applies to every shared module
  too; the DV Lead's F-CHERI-001 table follows this file, not the other way round).

A.2 Whole-file: rtl/ibex_cheriot_pkg.sv has no coverage objects of its own (package functions are
inlined into callers); nothing to exclude. rtl/ibex_trvk.sv is not in the DUT (CC A3).

A.3 Line / branch exclusions inside shared modules (CHERIoT-guarded arms)

Authoritative object list: CC Part B bucket C (per file, each item "file:line -- what the arm
does -- Off state"), restricted to items marked UNREACH or "CHERIoT side UNREACH". Items marked
TOGGLES or "live" are NOT excluded. Entry kind: `Block <id> "<checksum>" "<signature>"` (line
metric) and `Branch <id> (<vector>)` (branch metric) under `MODULE: <module>`. Block ids come from
the dump flow (B.6 step 3); the signature strings below are the match keys. Every entry carries
A.0 plus its evidence pointer (evidence 4.1 assertion name; Part C row where one exists).

MODULE: ibex_core
  ANNOTATION_BEGIN: "cheriot-out-of-scope (CC C ibex_core; evidence T022_CORE_CHERI0/_B)"
  Branch  rtl/ibex_core.sv:1000-1001  branch_target_ex mux, select `instr_valid_id & instr_is_cheriot_id` = 0 -> CHERIoT arm
  Branch  rtl/ibex_core.sv:1590-1593  g_pmp_addr_gate ternaries, `(cheriot_enable_i == IbexMuBiOn)` true-arms ('0)
  Branch  rtl/ibex_core.sv:1627-1630  g_pmp_cheriot_gate ternaries, true-arms (1'b0)
  (RVFI only, annotation states "+define+RVFI builds only") Block rtl/ibex_core.sv:2223-2225 `if (load_store_unit_i.resp_is_cap_q & lsu_resp_valid)` arm
  ANNOTATION_END
MODULE: ibex_if_stage
  Branch  rtl/ibex_if_stage.sv:222-228  exc_pc EXC_PC_EXC / EXC_PC_IRQ ternaries, CHERIoT arms ({mtvec[31:2],2'b00}) (evidence T022_IF_CHERI0)
MODULE: ibex_id_stage
  Block   rtl/ibex_id_stage.sv:901-908  `cheriot_lsu_req_dec:` case item body in FIRST_CYCLE (cheriot_lsu_req_dec = 0; Part C row 29; T022_ID_CHERI0)
  Branch  rtl/ibex_id_stage.sv:578      ex_valid_all select (instr_is_cheriot_id_o = 0), CHERIoT arm
  Branch  rtl/ibex_id_stage.sv:746-749  csr_op_en_o ternary, CHERIoT arm (instr_first_cycle)
MODULE: ibex_decoder
  Block   rtl/ibex_decoder.sv:314-323  OPCODE_JAL CHERIoT arm (CJAL)
  Block   rtl/ibex_decoder.sv:339-352  OPCODE_JALR CHERIoT arm (CJALR)
  Block   rtl/ibex_decoder.sv:402-407  OPCODE_STORE funct3 011 CHERIoT arm (CSC)
  Block   rtl/ibex_decoder.sv:447-453  OPCODE_LOAD funct3 011 CHERIoT arm (CLC)
  Block   rtl/ibex_decoder.sv:474-482  OPCODE_AUIPC CHERIoT arm (AUIPCC)
  Block   rtl/ibex_decoder.sv:793-876  OPCODE_CHERI body (the case item itself at :791 and its `else illegal_insn = 1` at :877-878 stay: reached by illegal-encoding tests)
  Block   rtl/ibex_decoder.sv:883-891  OPCODE_AUICGP body (item :881 and else :892-893 stay)
  Branch  rtl/ibex_decoder.sv:202      raddr_a CAUICGP ternary, CHERIoT arm (5'h3)
  Branch  rtl/ibex_decoder.sv:212-217  gen_16_regs ternaries, masked arms (the pass-through arms are live, A.8 item 8)
MODULE: ibex_compressed_decoder
  Block   rtl/ibex_compressed_decoder.sv:230-233, 249-252, 329-332, 359-363, 391-394, 411-414, 557-560, 575-579, 615-620, 854-857  the ten `(BaseIsa == BaseIsaRV32IorCHERIoT) && (cheriot_enable_i == IbexMuBiOn)` arms (Part C row 36 for :615-620)
MODULE: ibex_controller
  Block   rtl/ibex_controller.sv:850-858  instr_fetch_err_prio CHERIoT tag / bound violation arms (rows 2-3; T022_CORE_CHERI0_B)
  Branch  rtl/ibex_controller.sv:866-868  illegal_insn mtval ternary, CHERIoT arm (32'h0) only; the RV32I arm is live (row 4; A.8 item 2)
  Block   rtl/ibex_controller.sv:894-897  ebreak mtval = pc_id_i (CHERIoT) (row 5)
  Block   rtl/ibex_controller.sv:901-908  store_err_prio `if ((On) & lsu_err_is_cheriot_q)` arm (row 6; T022_CTRL_CHERI0)
  Block   rtl/ibex_controller.sv:915-922  load_err_prio CHERIoT arm (row 7)
  Block   rtl/ibex_controller.sv:928-948  cheriot_ex_err_prio / cheriot_wb_err_prio / cheriot_asr_err_prio case items (rows 8-10; T022_CTRL_PRIO0)
  Block   rtl/ibex_controller.sv:318-319, 328-331  g_wb_exceptions CHERIoT priority arms
MODULE: ibex_load_store_unit
  Block   rtl/ibex_load_store_unit.sv:139-140  data_be cap arm (4'b1111)
  Block   rtl/ibex_load_store_unit.sv:211-219  cap write-data arms (incl. cheriot_cap_to_mem)
  Block   rtl/ibex_load_store_unit.sv:437-467  IDLE cpu_req_erred arm and cap-access arm (rows 14-22; T022_LSU_CHERI0)
  Block   rtl/ibex_load_store_unit.sv:565-603  CTX_WAIT_GNT1 / CTX_WAIT_GNT2 / CTX_WAIT_RESP case items (never entered; T022_LSU_NO_CTX)
  Block   rtl/ibex_load_store_unit.sv:616-623  cap_rx_fsm CRX_WAIT_RESP1 / CRX_WAIT_RESP2 items and the CRX_IDLE true-arm (rows 24-28; T022_CRX_IDLE)
  Block   rtl/ibex_load_store_unit.sv:669-678  cap_lsw_* update blocks
  Branch  rtl/ibex_load_store_unit.sv:131-132, 702-709  data_offset and gen_memcap_rd ternaries, CHERIoT arms (the RV32I arms `data_addr[1:0]` and `data_rdata_ext` are live)
MODULE: ibex_wb_stage
  Branch  rtl/ibex_wb_stage.sv:182-183, 215  rf_wdata_wb_mux / rf_wdata_fwd_wb_o ternaries, wb_is_cheriot_q arms (T022_WB_CHERI0)
  (row 41 :115-116, :190-196 are Condition-only entries, A.4; never Block)
MODULE: ibex_cs_registers
  Block   rtl/ibex_cs_registers.sv:469-475, 478-484  CSR_MTVEC / CSR_MEPC `if ((dual) && (On)) illegal_csr` arms
  Block   rtl/ibex_cs_registers.sv:678-698  CSR_MSHWM / MSHWMB / CDBG_CTRL read arms under (On) (the `else illegal_csr = 1` arms are live: reads of 0xBC1/2/4 trap)
  Block   rtl/ibex_cs_registers.sv:707-715  PMP-CSR illegal block (needs !PMPEnable or On)
  Branch  rtl/ibex_cs_registers.sv:424-426  CSR_MARCHID ternary CHERIoT arm (32'hce1)
  Block   rtl/ibex_cs_registers.sv:2014-2056 (CHERIoT arms of the SCR read mux), 2063-2067 (pcc_cap_q update under On), 2108-2209 (*_en_cheriot arms of mtvec/mepc/mtdc/mscratchc/depc/dscratch caps), 2218-2224 (cheriot_fatal_err_q set) (T022_CSR_CHERI0, T022_CSR_MSHWM0)
  Annotation for the mshwm path (:879-882 write enables, :1301 set path, :1304-1330 CSRs): unreachable through the two-CSR chain rtl/ibex_cheriot_ex.sv:991 -> mshwm/mshwmb at reset 0 -> enables need On (evidence 4.1 note).
MODULE: ibex_register_file_ff
  Branch  rtl/ibex_register_file_ff.sv:113  wshared_data ternary, wcap_a_i arm (T022_RF_CAP0)
  Branch  rtl/ibex_register_file_ff.sv:227-230  rcap_a_o / rcap_b_o ternaries, cap arms
  (the bank-select and shared-flop enables :136-137, :160-161, :221-224 are LIVE x16-x31 logic: not excluded; A.8 item 8)

A.4 Condition exclusions (condition coverage IS reported and gated, T-010: explicit entries are
needed for everything URG does not mark Unreachable by itself)

Every condition vector in which the sub-term `(cheriot_enable_i == IbexMuBiOn)` (or a G1-G8
constant such as instr_is_cheriot_id, cheriot_exec_id, lsu_is_cap, cheriot_wb_err_q, cheriot_ex_err_q,
resp_is_cap_q, lsu_err_is_cheriot_q, wb_is_cheriot_q, cheriot_enabled) evaluates to 1, in the
expressions listed in CC bucket C as "term CONST 0" (e.g. rtl/ibex_core.sv:1281-1286, :1351;
rtl/ibex_controller.sv:268-276, :336-337, :681-682, :827-840; rtl/ibex_load_store_unit.sv:407-408,
:419, :688-693; rtl/ibex_wb_stage.sv:115-116, :190-196; rtl/ibex_cs_registers.sv:379-389, :741-743,
:796-797, :807-808, :1020-1023, :1062-1069, :1085-1240 *_combi; rtl/ibex_decoder.sv:238, :1459-1476;
rtl/ibex_if_stage.sv:430, :456-472). Entry kind `Condition <id> (<vector>)`; ids from the dump.
Constant analysis marks some of these Unreachable already (EC-2 partial); the rest get entries.
UCAPI-CSM status of the seven glitch-covered tie conditions (cheriot_enable_i terms
rtl/ibex_cheriot_ex.sv:970, rtl/ibex_cs_registers.sv:377, :1020, rtl/ibex_core.sv:1343; fetch_enable_i
terms rtl/ibex_core.sv:648, :649, :1414): with the standard build `-excl_strict` rejects their entries;
the trial rtl-arch-001 showed `-cm_glitch 0` removes the mismatch entirely (evidence 4.3). The
Runtime's report attributes the numerator drop to the flag (deterministic NOP smoke, identical
totals per seed), so no control run is needed; rtl-arch recommends adoption for measured builds
(evidence 4.3), the DV Lead decides (LOG-007). Until then these seven Condition entries are
generated only if the measured build carries the flag, otherwise they stay out and are listed as
"glitch-covered constants" in the report.

A.5 Toggle exclusions (with `-cm_tgl portsonly`, only module PORTS are toggle objects)

Constant CHERIoT-only ports per module (CC bucket D "Port-level view" gives the declaration
lines). Entry kind `Toggle <port>` under `MODULE:`:
- ibex_core: cheriot_enable_i, data_tag_o, data_tag_i, rf_wcap_ecc_wb_o, rf_rcap_a_ecc_i,
  rf_rcap_b_ecc_i; (RVFI builds only) rvfi_rs1_rcap, rvfi_rs2_rcap, rvfi_rd_wcap, rvfi_mem_is_cap,
  rvfi_mem_rcap, rvfi_mem_wcap. Internal nets rf_rcap_a/b (constant NULL_CAP, G8) are not ports
  and therefore not toggle objects under portsonly: no entry needed (E-01).
- ibex_if_stage: cheriot_enable_i, instr_fetch_cheriot_acc_vio_o, instr_fetch_cheriot_bound_vio_o,
  pcc_cap_i.
- ibex_id_stage: cheriot_enable_i, cheriot_exec_id_o, instr_is_cheriot_id_o, cheriot_imm12_o,
  cheriot_imm20_o, cheriot_imm21_o, cheriot_operator_o, cheriot_cs2_dec_o, cheriot_cap_field_sel_o,
  cheriot_adder_a_sel_o, cheriot_adder_b_sel_o, cheriot_setaddr_sel_o, cheriot_setbounds_sel_o,
  cheriot_load_o, cheriot_store_o, cheriot_ex_valid_i, cheriot_ex_err_i, cheriot_ex_err_info_i,
  cheriot_wb_err_i, cheriot_wb_err_info_i, cheriot_branch_req_i, cheriot_branch_target_i,
  lsu_err_is_cheriot_i, csr_pcc_perm_sr_i (constant 1 per G6), csr_mepcc_clrtag_o,
  instr_fetch_cheriot_acc_vio_i, instr_fetch_cheriot_bound_vio_i. NOT instr_is_rv32lsu_id_o
  (toggles, = lsu_req_dec).
- ibex_decoder / ibex_controller: the cheriot_* ports and csr_pcc_perm_sr_i / csr_mepcc_clrtag_o /
  instr_fetch_cheriot_*_i / instr_is_cheriot_i / lsu_err_is_cheriot_i (CC bucket D lines
  rtl/ibex_decoder.sv:92-119, rtl/ibex_controller.sv:22, :35, :46-47, :74, :77, :127-134).
- ibex_load_store_unit: cheriot_enable_i, lsu_is_cap_i, lsu_cheriot_err_i, lsu_wcap_i,
  lsu_lc_clrperm_i, lsu_rcap_o, data_tag_o, data_tag_i, lsu_err_is_cheriot_o.
- ibex_wb_stage: instr_is_cheriot_i, cheriot_load_i, cheriot_store_i, cheriot_rf_we_i,
  cheriot_rf_wdata_i, cheriot_rf_wcap_i, rf_wcap_lsu_i, rf_wcap_fwd_wb_o, rf_wcap_wb_o.
- ibex_cs_registers: cheriot_enable_i, cheriot_csr_access_i, cheriot_csr_addr_i, cheriot_csr_wdata_i,
  cheriot_csr_wcap_i, cheriot_csr_op_i, cheriot_csr_op_en_i, cheriot_csr_set_mie_i,
  cheriot_csr_clr_mie_i, cheriot_csr_rdata_o, cheriot_csr_rcap_o, csr_mshwm_o, csr_mshwmb_o,
  csr_mshwm_set_i, cheriot_branch_req_i, cheriot_branch_target_i, pcc_cap_i, pcc_cap_o,
  csr_dbg_tclr_fault_o, cheriot_fatal_err_o. NOT csr_mshwm_new_i (toggles, dead).
- ibex_compressed_decoder: cheriot_enable_i. ibex_register_file_ff: cheriot_enable_i, rcap_a_o,
  rcap_b_o, wcap_a_i.
- ibex_cheriot_ex: the CONSTANT port list of A.1 only.
Half-transition note: these are constants, so both 0to1 and 1to0 are excluded (plain `Toggle`).
Evidence: EC-1 (bucket D + G item), EC-2 (constfile.txt lists the tie; toggle rows already marked
Unreachable where propagation reached), EC-5. Data-path toggle exclusions (non-CHERIoT) are NOT part
of this draft; each comes from a URG hole with an EC-6 cone-of-influence result quoted in its
annotation (E-05); a data bit with any control fan-out is refused.

A.6 FSM exclusions (T-010: URG reports the FSM metric; six machines extracted, transitions scored)

MODULE: ibex_load_store_unit  FSM ls_fsm_cs: State CTX_WAIT_GNT1, State CTX_WAIT_GNT2,
State CTX_WAIT_RESP and every transition into/out of them (IDLE->CTX_WAIT_GNT1,
IDLE->CTX_WAIT_GNT2, CTX_WAIT_GNT1->CTX_WAIT_GNT2, CTX_WAIT_GNT1->IDLE, CTX_WAIT_GNT2->IDLE,
CTX_WAIT_GNT2->CTX_WAIT_RESP, CTX_WAIT_RESP->IDLE); FSM cap_rx_fsm_q: States CRX_WAIT_RESP1,
CRX_WAIT_RESP2 and all four transitions (the whole FSM is frozen in CRX_IDLE: lsu_go_goodcap is set
only in the gated IDLE arm, rtl/ibex_load_store_unit.sv:449-459). Justification:
gen_hierarchy_map.md Part C FSM-2 U-L1..U-L10 and FSM-3; evidence T022_LSU_NO_CTX, T022_CRX_IDLE
(k-induction PASS). Class T, EC-1/EC-2 (E-02). Constant analysis does not cover the FSM metric
(B.3), so these are explicit entries.

A.7 Assertion exclusions

MODULE: ibex_register_file_ff  Assert CheriotWaddrMSBClear, Assert CheriotRaddrAMSBClear,
Assert CheriotRaddrBMSBClear (antecedent `cheriot_enabled` is constant 0: vacuous, never
"covered"; rtl/ibex_register_file_ff.sv:237-239). The ASSERT_IF invariants with a TRUE enable
(rtl/ibex_id_stage.sv:1297-1300, rtl/ibex_load_store_unit.sv:833-834, rtl/ibex_cs_registers.sv:
1996-1997) and the controller one-hot assertion (rtl/ibex_controller.sv:377-383) are real RV32I
checkers, NOT excluded, and are the EC-3 proof objects for class T.

A.8 What is deliberately NOT excluded (CC bucket F leaks and the live halves of gated logic)

Authority statement: the final file gen_exclusions (dv/auto_dv/, gen_ prefix) is the authoritative
list; the DV Lead's F-CHERI-001 table mirrors it row for row (gen_critic_feature_list_v1.md C-16,
C-19), never the reverse. Not excluded, by name:
1. rtl/ibex_controller.sv:827-831 (FLUSH exception entry: pc_set_o, PC_EXC, exc_pc_mux_o for every
   trap) and :833-840 (csr_save_id_o / csr_save_wb_o); only the `(On) & cheriot_wb_err_q` sub-terms
   are Condition-excluded (A.4).
2. rtl/ibex_controller.sv:866-868 RV32I arm (mtval = instruction bits), :909-914 (store access fault
   arm), :923-926 (load access fault arm) (bucket F9).
3. rtl/ibex_controller.sv:255 `illegal_insn_d` (live; the bucket-C items in :234-259 are only :234,
   :236-240, :256-257, :259).
4. rtl/ibex_id_stage.sv:1033-1036 instr_kill (bucket F11) and the live lines :1012, :1093-1096 whose
   CHERIoT OR-terms (cheriot_lsu_req_dec) are Condition-only exclusions.
5. rtl/ibex_core.sv:1350-1351 alert_major_internal_o: live terms rf_ecc_err_comb |
   pc_mismatch_alert | csr_shadow_err; only the two constant OR-terms (cheriot_fatal_err,
   cheriot_enable_mubi_err) are Condition-excluded.
6. rtl/ibex_load_store_unit.sv:650-653 (ls_fsm_cs, handle_misaligned_q, pmp_err_q, lsu_err_q flops)
   and :664-667 (resp_is_cap_q / resp_lc_clrperm_q update executes on every lsu_go; line live, value
   constant).
7. rtl/ibex_core.sv:1851-1853 rvfi_id_done (bucket F10; RVFI-only; live and bug candidate BUG-04).
8. Bucket F13 register-file nets by name: rf_shared[*] (:99), wshared_data (:112-113),
   we_shared_r0, rf_shared_r0_q, rcap_r0 (F2), we_data_r0, rf_data_r0_q; bucket F5 pass-through arms
   of gen_16_regs (rtl/ibex_decoder.sv:211-217) and the CAUICGP raddr_a mux RV32 arm (:202).
9. Bucket F15 assertions kept enabled: rtl/ibex_controller.sv:377-383 one-hot, the three ASSERT_IF
   groups of A.7 (the EC-3 proof objects).
10. The live objects and live ports of u_ibex_cheriot_ex per A.1.
Plus the v1 items: rf_shared x16-x31 storage and enables; the PMP gate RV32I arms; gen_memcap_rd's
RV32I arm; the *_combi CSR write muxes; branch_target_ex; instr_is_rv32lsu_id; csr_mshwm_new;
mstack_epc_cap_q and pcc_cap_d/tf_cap/tr_cap/pcc_exc_cap (toggle in RV32I mode on traps); the
OPCODE_CHERI / OPCODE_AUICGP case items and their illegal arms; the 0xBC1/0xBC2/0xBC4 illegal-CSR arms.

## Part B. Mechanism (for the Runtime Manager; from urg -help X-2025.06-SP2, $VCS_HOME/doc/UserGuide/pdf/cov_ug_vcsmx.pdf "Exclusion Management" pp.336-357 and "Constant Analysis" pp.388-413, cov_ref.pdf pp.32-40, 58-62, 223; option names re-verified by the Critic against urg -help)

B.1 Where exclusions act. Exclusions are a REPORT/MERGE-time operation: `urg ... -elfile <file.el>`
(or `-elfilelist <list>`) marks the listed objects "Excluded" and removes them from every score
(cov_ug p.339-340). They do not change instrumentation. Options (urg -help lines 92-107):
`-excl_strict` refuses to exclude an object that some test covered (MANDATORY, B.7);
`-excl_bypass_checks` loads entries whose CHECKSUM is missing or stale (hand-written entries have
no checksum and load without version checks, cov_ug p.339, so this flag is needed only when a
tool-dumped file goes stale after an RTL change: the RTL is frozen here); `-excl_embed` stores the
exclusions inside the merged VDB; `-excl_append_annotation` keeps multiple annotations on one
object; `-excl_propagation` propagates line exclusions to the condition and branch metrics of the
same statements (NOT used, B.7); `-dump full_exclusions [line+tgl+cond+branch+fsm+assert+group]`
writes fullexclude.<metric> / fullexclude_module.<metric> files with EVERY excludable object as a
commented entry carrying its id, checksum and source signature (cov_ug p.353-357), scoped by
`-hier <hierfile>` (same +tree syntax as -cm_hier).

B.2 File syntax (cov_ug p.336-350). Scopes: `INSTANCE: <hier.path>` or `MODULE: <module>`, each
optionally preceded by `CHECKSUM: <mod> <variant>`. Entries: line `Block <id> "<checksum>"
"<signature>"`; toggle `Toggle <net>` / `Toggle 0to1 <net>[hi:lo]` / `Toggle 1to0 <net>`;
condition `Condition <id> (<vector>)`; branch `Branch <id> (<vector>)`; FSM `FSM <state_var>`,
`State <name>`, `Transition <a>-><b>`; assertion `Assert <name>`; covergroup `covergroup
<path>::<cg>` / `coveritem <cp>` / `bins <list>`. Justification: `ANNOTATION: "<text>"` before a
single object, or `ANNOTATION_BEGIN: "<text>"` ... `ANNOTATION_END` around a group; annotations
appear in the URG report's last column (p.349). Files should be machine-generated then edited;
the doc discourages hand-editing tool-dumped files only because of checksums.

B.3 Constant analysis: what it does for us (T-010 measured). SIM_RECIPE.md section 3 compiles with
`-cm_seqnoconst`; the flow adds `-diag noconst` (constfile.txt per build). Per cov_ug p.388-395
VCS recognises nets that are permanently 0/1, including a port tied to a constant at
INSTANTIATION (Example 53, p.394), and marks unhittable objects "Unreachable" (line, condition,
branch, toggle; not FSM, not assertions). T-010 result: the wrapper tie IS recognised and propagated
(constfile.txt lists u_ibex_core cheriot_enable_i[0] "0 always", 673 constant entries), but URG marks
only the DIRECTLY dependent objects Unreachable (ibex_cheriot_ex: 5 line rows, 54 condition vectors,
22 toggle rows; the module still scores 126/336 lines; ibex_decoder 136 line rows / 62 condition
vectors; ibex_core 107 / 74). So EC-2 is partial and the annotated entries of Part A remain
necessary; `-cm_constfile` is NOT needed (propagation works). Controls kept for reference:
`-cm_constfile <file>` (`<full.signal.name> <value>`, cov_ref p.39-40), URG `-show constvalues`.
"Unreachable" objects are still exclusions in the DV_prompt sense and are reviewed: the dump
(`-dump full_exclusions`, annotation dump cov_ug p.424) and constfile.txt are committed beside the
annotated file (B.7 rule 3). Known defect: UCAPI-CSM time-zero glitch on seven tie conditions (A.4);
trial `-cm_glitch 0` requested (rtl-arch-001).

B.4 Compile-time scoping (-cm_hier). The hier file takes `+tree <inst>` / `-tree <inst>`,
`+module <mod>` / `-module <mod>`, `-node <hier.signal>` / `+node`, `-module_node <mod> <sig>`
(cov_ref p.32-33, 61-62). The flow's `+tree <tb_top>.u_dut` restricts instrumentation to the DUT
(T-010: the u_dut node and the TB-top node carry identical numbers, so no TB code is instrumented);
the exclusion file addresses INSTANCE paths under that tree or MODULE names. Report-time .el is
preferred over `-node` removal so every exclusion is visible and annotated in the report.
T-010 confirmed `-cm_hier` with `-cm_tgl portsonly` compiles without a warning (the cov_ref p.60
note applies only to the portsonly-specific `+moduletree` rules). `-cm_ignore_pragma` is
irrelevant (no coverage pragmas in rtl/, and DV never edits RTL).

B.5 FSM metric (T-010: reported). VCS extracted six machines: ibex_compressed_decoder cm_state_q,
ibex_controller ctrl_fsm_cs (10 states, 26 transitions), ibex_load_store_unit ls_fsm_cs and
cap_rx_fsm_q, ibex_multdiv_fast md_state_q, ibex_icache inval_state_q; URG scores transitions,
states are listed but not scored. A.6 applies. `-fsm disable_sequence` keeps sequence coverage out
of the score. `urg -line nocasedef` is NOT used (Critic R-2c: global, would also remove the
reachable illegal-instruction / illegal-CSR default arms); class D uses explicit entries (C.2).

B.6 Suggested flow. (1) Merge the measured regression vdbs (SIM_RECIPE section 8; measured tiers
only, B.7 rule 6). (2) `urg -dump full_exclusions -hier <dut_hier> -dir <merged.vdb>` to obtain
fullexclude.<metric> with ids, checksums and signatures for every DUT object (the flow's
`--dump-exclusions` / purpose 4 does this into <outdir>/cov/full_exclusions/). (3) A checked-in
script (Runtime) selects entries by matching the signature/line references in this document and
in gen_cheriot_carveout.md, uncomments them, and inserts the ANNOTATION text from Part A/C. (4)
`urg ... -elfile gen_exclusions.el -excl_strict -excl_embed` for the reported numbers; the
"Excluded" and "Unreachable" counts appear in dashboard.txt. (5) Review: the Critic approves the
final file before step 4 runs on a measured regression. Naming: the committed exclusion file goes
under dv/auto_dv/ with the gen_ prefix (dv/auto_dv/contract/README.md).

B.7 Flow rules (Critic R-5; status of each in the Runtime flow per T-010):
1. `-excl_strict` on every measured merge (EC-5); a rejected entry is a finding, never a reason to
   drop the flag. Runtime: gen_regress.py adds -excl_strict whenever --elfile is given; a rejection
   sets coverage.status exclusion_violation and exit 3 (T-010 r5_violation test).
2. `-excl_propagation` is not used: partial-arm entries live on live lines. Runtime: not passed.
3. The auto-Unreachable set is an exclusion in the DV_prompt sense: the `-dump full_exclusions`
   files and constfile.txt of the measured merge are copied beside the annotated .el file and
   committed, so the closure report states both counts (Excluded, Unreachable). Runtime: both
   artefacts are produced (coverage.full_exclusions_dump, coverage.constfiles); rtl-arch copies them.
4. RVFI entries apply only under +define+RVFI; each such annotation states the define dependence.
5. Instance paths: confirmed by T-010 (`<tb_top>.u_dut.u_ibex_core`, `.u_register_file`); the file
   is generated only after the real TB top exists, substituting its top name.
6. Merge hygiene (R-2d): only legal-stimulus tiers enter a measured vdb; mutation-evidence,
   forced-error and bring-up tests carry `measured: false` and run into cov_unmeasured/ (T-010).
   Every class-D annotation names this rule.

## Part C. The 43 unreachable arcs from the transition audit (gen_hierarchy_map.md Part C section 1)

Legend: class T = CHERIoT tie (part of the Part A carve-out, not a separate exclusion); class P =
build-parameter constant (elaboration-time, non-CHERIoT); class D = enum default arm; class R =
reasoning-based (needs EC-4 before exclusion). Evidence = gen_unreachability_evidence.md section
4.2 row (tool, run, result) and the EC set the Critic requires (evidence 4.6). Control-logic: ALL 43
are control logic and need Critic approval on the final file (DV_prompt Section 4).

| # | Arc (audit id) | RTL | Class | Unreachability argument | Evidence (gen_unreachability_evidence.md) |
|---|---|---|---|---|---|
| 1 | U-C1 ctrl default->RESET | rtl/ibex_controller.sv:990-993 | D (2b) | ctrl_fsm_e 4-bit enum, 10 named values, 6 spare encodings (rtl/ibex_pkg.sv:291-302); guard IbexCtrlStateValid :1104-1106 | T022_CTRL_NAMED PROVED (spare encodings never held); EC-1 + EC-3 + EC-5 |
| 2-3 | U-C2, U-C3 fetch-err CHERIoT arms | :850-858 | T | `(cheriot_enable_i == IbexMuBiOn) & instr_fetch_cheriot_*_vio_i`, both factors 0 (CC G7) | T022_CORE_CHERI0_B PROVED |
| 4 | U-C4 illegal mtval CHERIoT arm | :866-867 | T | ternary select constant 0; RV32I arm live (A.8 item 2) | constant-tie |
| 5 | U-C5 ebreak mtval = pc | :894-897 | T | guarded by the On comparison | constant-tie |
| 6-7 | U-C6, U-C7 store/load err CHERIoT arms | :901-908, :915-922 | T | lsu_err_is_cheriot_q constant 0 (CC G4, G5) | T022_CTRL_CHERI0 PROVED |
| 8-10 | U-C8..U-C10 cheriot_ex/wb/asr_err_prio | :928-948 | T | prio bits constant 0 (:256-259, :318, :1054-1067) | T022_CTRL_PRIO0 PROVED |
| 11 | U-C11 pc_set via cheriot_branch_req | :681-682 | T | cheriot_branch_req_i constant 0 (CC G3) | T022_CORE_CHERI0 PROVED |
| 12 | U-C12 nt_branch_mispredict / bp variant | :684, :690-696 | P | BranchPredictor = 0; Branch entry for the TRUE arm of `pc_set_o = BranchPredictor ? ~instr_bp_taken_i : 1'b1` only (:684, else-arm live) and Block for the `if (BranchPredictor)` body :690-696 | T022_CORE_BP0 PROVED; yosys constants 1'0 (evidence 4.3); expected URG Unreachable |
| 13 | U-C13 exc_req CHERIoT terms | :269, :276 | T | condition terms constant 0 (Condition entries) | T022_CORE_CHERI0 PROVED |
| 14-22 | U-L1..U-L9 = L12..L20 LSU CHERIoT arcs | rtl/ibex_load_store_unit.sv:437-467, :565-603 | T | entry arcs need On (:437, :449); CTX_* states never entered | T022_LSU_NO_CTX, T022_LSU_CHERI0 PROVED |
| 23 | U-L10 = L21 LSU default | :605-607 | D (2b) | ls_fsm_e 4-bit enum, 8 named values, 8 spare encodings (rtl/ibex_pkg.sv:816-820); guard IbexLsuStateValid :821-824 | T022_LSU_NAMED PROVED; EC-1 + EC-3 + EC-5 |
| 24-28 | U-X1..U-X5 cap_rx FSM | :615-624 | T | lsu_go_goodcap set only in the gated IDLE arm (:449-459); FSM frozen in CRX_IDLE | T022_CRX_IDLE PROVED |
| 29 | U-I1 = I3 id_fsm cheriot_lsu_req_dec | rtl/ibex_id_stage.sv:901-909 | T | cheriot_lsu_req_dec = decoder cheriot_data_req_o = 0 (CC G1) | T022_ID_CHERI0, T022_DEC_CHERI0 PROVED |
| 30 | U-I2 = I8 jump multicycle | :936-942 | P | BranchTargetALU = 1: `BranchTargetALU ? FIRST_CYCLE : MULTI_CYCLE` false-arm and `stall_jump = ~BranchTargetALU` constant 0; Branch entry for the MULTI_CYCLE arm only | elaboration constant (config + banner) |
| 31 | U-I3 = I14 id_fsm default | :968-970 | D (2a) | id_fsm_e 1-bit enum, 2 named values, 0 spare (rtl/ibex_id_stage.sv:861) | full encoding; EC-1 + EC-5 |
| 32 | U-I4 branch !BTALU sub-term | :925-926 | P | `!BranchTargetALU && branch_decision_i` sub-term constant 0; Condition entry for that vector only | elaboration constant |
| 33 | U-D1 divider default | rtl/ibex_multdiv_fast.sv:522-524 | D (2b) | md_fsm_e 3-bit enum, 7 named values, 1 spare (3'b111) (:90-92); guard IbexMultDivStateValid :532-533 | T022_MD_NAMED PROVED; EC-1 + EC-3 + EC-5 |
| 34 | U-M1 multiplier default | :238-240 | D (2a) | mult_fsm_e 1-bit enum, 2 named values, 0 spare (:142-144) | full encoding |
| 35 | U-V1 icache inval default | rtl/ibex_icache.sv:1268 | D (2a) | inval_state_e 2-bit enum, 4 named values, 0 spare (:193-198) | full encoding |
| 36 | U-Z1 = Z20 Zcmp illegal in CHERIoT | rtl/ibex_compressed_decoder.sv:615-620 | T | guarded by the On comparison | constant-tie |
| 37-40 | U-Z2..U-Z5 = Z19 mismatched-state defaults | :682, :773, :804, :832 | R | named state paired with a different Zcmp class on instr_i; rests on the class fields being stable mid-sequence. Corrected premise: only instr_i[15:0] is stable (the icache back-fills [31:16] of a compressed instruction, rtl/ibex_icache.sv:1131-1133, :1192); the Critic's EC-4 property uses the class fields {instr_i[15:13], [12:8], [6:5], [1:0]} under cm_state_q != CmIdle && valid_i && !flush_expanded_i, implemented as T022_NEVER_zcmp_class_change plus seven per-state covers in gen_cover_props_draft.sv; EC-3 IbexPushPopFSMStable (:937) | bounded only: no CEX within 14 cycles of reset (bmc), class-mismatch cover unreached to depth 12+ (evidence 4.4, 4.5). NOT in the file until EC-4 passes on the full regression and Phase-1 URG shows the arms uncovered |
| 41 | WB CHERIoT terms | rtl/ibex_wb_stage.sv:115-116, :190-196 | T | wb_is_cheriot_q, wb_cheriot_load_q, wb_cheriot_store_q constant 0 (CC G2/G3); Condition entries ONLY (live statements) | T022_WB_CHERI0 PROVED |
| 42-43 | U-A1, U-A2 BCOMPRESS / BDECOMPRESS multicycle | rtl/ibex_decoder.sv:1342-1344, :1348-1350 | P | `RV32B == RV32BFull` constant false (RV32B = RV32BOTEarlGrey); the case items :1341 and :1347 ARE reached by the illegal encodings, so only the inner `if` bodies are excluded (Block entries for :1342-1344 and :1348-1350) | elaboration constant; legality :641-642 |

Counts: T 28, P 5, D 6, R 4 = 43. Class T is covered by the Part A carve-out justification and
needs no separate entries beyond A.3-A.7 (per arm/term granularity). Class P: explicit Branch/Block
entries at the granularity above unless URG already reports the objects Unreachable (EC-2).

C.2 Class D: six explicit entries (R-2, E-03), annotation templates:
- 2a (rows 31, 34, 35), annotation: "no spare encoding: <width>-bit enum, <n> named values
  (<file:line of the typedef>)". Entries: Branch (the default arm) and Block where the arm has
  statements. No assertion evidence required.
  - MODULE: ibex_id_stage  Branch rtl/ibex_id_stage.sv:968-970  "no spare encoding: 1-bit enum, 2 named values (rtl/ibex_id_stage.sv:861)"
  - MODULE: ibex_multdiv_fast  Branch rtl/ibex_multdiv_fast.sv:238-240  "no spare encoding: 1-bit enum, 2 named values (rtl/ibex_multdiv_fast.sv:142-144)"
  - MODULE: ibex_icache  Branch rtl/ibex_icache.sv:1268  "no spare encoding: 2-bit enum, 4 named values (rtl/ibex_icache.sv:193-198)"
- 2b (rows 1, 23, 33), annotation: "unreachable without fault injection into <state register>;
  <n> spare encodings; guarded by <assertion name> (attempts N, failures 0 in <regression id>);
  measured merge contains legal-stimulus tiers only (B.7 rule 6); k-induction proof
  gen_unreachability_evidence.md 4.1 <T022_name>".
  - MODULE: ibex_controller  Block/Branch rtl/ibex_controller.sv:990-993  ctrl_fsm_cs, 6 spare, IbexCtrlStateValid, T022_CTRL_NAMED
  - MODULE: ibex_load_store_unit  Block/Branch rtl/ibex_load_store_unit.sv:605-607  ls_fsm_cs, 8 spare, IbexLsuStateValid, T022_LSU_NAMED
  - MODULE: ibex_multdiv_fast  Block/Branch rtl/ibex_multdiv_fast.sv:522-524  md_state_q, 1 spare, IbexMultDivStateValid, T022_MD_NAMED
  The attempts/failures numbers are filled from the merged assertion coverage of the measured
  regression when the file is generated (EC-3).

C.3 Cone-of-influence status (unchanged from v1, E-04 accepted): the two siliconpilot
cone_of_influence runs used default parameters (BaseIsa = RV32I) and stopped at procedural
assignments; the tool takes no define/pvalue context, so for this build the result is "not
applicable" and EC-1/EC-2 are primary (gen_unreachability_evidence.md section 3). Data-path
toggle exclusions (none yet) get EC-6 through the yosys flattened netlist of evidence 2.1 if the
MCP tool still cannot take the context.

## Part D. Open items

- Closed by T-010: instance names (u_dut.u_ibex_core / u_register_file), FSM metric reported,
  constant-analysis propagation (works, partial marking), -cm_hier + portsonly clean.
- Open: UCAPI-CSM glitch on seven tie conditions (A.4) -> -cm_glitch 0 trial requested
  (dv/auto_dv/work/runtime/requests/rtl-arch-001.yaml); outcome to evidence 4.3.
- Open: EC-3 numbers (assertion attempts/failures) and EC-5 strict load need the first measured
  regression; EC-4 (class R) needs gen_cover_props_draft.sv compiled and bound by TB Infra.
- Open: Critic re-review of this v2 and of gen_critic_response_exclusions_v1.md.
- RegFileECC decision (owner Q-A): with 0 there is no RF-ECC object in the DUT to exclude; with 1
  the cap-ECC decoders (rtl/ibex_core.sv:1244-1290) join bucket B (CC B2) and need entries.
