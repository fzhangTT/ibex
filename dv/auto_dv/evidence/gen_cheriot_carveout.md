# CHERIoT carve-out inventory: basis for the single exclusion "cheriot-out-of-scope"

Owner: rtl-arch (T-003). Ruling: DV_prompt.txt Section 2 (CHERIoT mode out of scope; wrapper
ties cheriot_enable_i to ibex_pkg::IbexMuBiOff = 4'b1010; the invalid-encoding alert on that pin
is part of the same carve-out). This file folds subagent inventory subagent/cheriot_B.md (Part B,
verbatim) under an rtl-arch verification layer (Part A). The exclusion file itself is written
later (rtl-arch owns it); control-logic exclusions need Critic approval first.

## Part A. rtl-arch summary and verification

### A.1 The three kinds of CHERIoT presence, and what may be excluded

1. Whole module: rtl/ibex_cheriot_ex.sv, instance ibex_core.g_cheriot_ex.u_ibex_cheriot_ex
   (rtl/ibex_core.sv:911-1001, elaborates because BaseIsa is compile-time). NOT a clean
   exclusion: the RV32I load/store request path is routed THROUGH it (rtl/ibex_cheriot_ex.sv:
   943-960, :970-973: lsu_req_o, lsu_we_o, lsu_addr_o, lsu_wdata_o, lsu_type_o, lsu_sign_ext_o,
   rv32_addr_incr_req_o, rv32_addr_last_o are live RV32I nets). Exclusion must list the module
   and then re-include the ~60 live lines named in Part B A1, or exclude by named blocks/nets.
   rtl/ibex_cheriot_pkg.sv: package only (types, constants, functions); its functions
   cheriot_vec_to_regcap / cheriot_regcap_to_vec / cheriot_decode_cap / cheriot_pcc_to_mepc /
   cheriot_violation_cause are evaluated in RV32I mode from shared modules. rtl/ibex_trvk.sv is
   NOT in the DUT (only ibex_top instantiates it, rtl/ibex_top.sv:1275-1320).
2. Generate blocks inside shared modules under `BaseIsa == BaseIsaRV32IorCHERIoT` (15, Part B
   bucket B). They elaborate. Some are dead with the tie (B3 mubi check, B10/B11 controller
   CHERIoT error flops, B13 mshwm CSRs), some contain LIVE RV32I logic that must stay covered:
   B12 gen_memcap_rd (the RV32I load-data return `lsu_rdata_o = data_rdata_ext`), B4/B5 PMP
   address/error gates, B1 branch_target_ex mux, B15 the register file itself (x16-x31 live in
   rf_shared), B14 gen_scr (mstack_epc_cap_q, pcc_cap_d and friends toggle on traps).
3. Conditional arms and terms guarded by `cheriot_enable_i == IbexMuBiOn` or by an internal
   signal proven constant 0 (Part B section 0 gating chain G1-G8, bucket C ~120 items with line
   cites, bucket D ~110 constant nets/ports/enum values). These are line/condition/toggle
   exclusion candidates; the case items for OPCODE_CHERI (7'h5b) and OPCODE_AUICGP (7'h7b) are
   REACHED (they resolve to illegal instruction, rtl/ibex_decoder.sv:877-878, :892-893); only
   their inner bodies are unreachable.

### A.2 The invalid-encoding alert path (verified)

rtl/ibex_core.sv:1342-1344 (`gen_cheriot_enable_check`):
`cheriot_enable_mubi_err = instr_exec & !((cheriot_enable_i == IbexMuBiOn) || (cheriot_enable_i
== IbexMuBiOff))`, instr_exec = (fetch_enable_i == IbexMuBiOn) (:649); consumer
alert_major_internal_o (:1350-1351). With the tie the term is constant 0. Exclusion items: the
condition/branch bins of :1343-1344, the toggle of cheriot_enable_mubi_err, and the constant OR
terms `cheriot_fatal_err | cheriot_enable_mubi_err` at :1351 (cheriot_fatal_err is also constant
0: rtl/ibex_cs_registers.sv:2212-2224 sets it only under the On condition).

### A.3 Leaks into the RV32I path (NOT excludable; feature-list / bug-candidate material)

Verified highlights of Part B bucket F: (F1) x16-x31 live in the 35-bit rf_shared bank with x16
a separate flop (rtl/ibex_register_file_ff.sv:99, :131-141, :160-183): RV32I features to cover
(x16 write/read, x16 next to dummy instructions, forwarding into x16-x31). (F4) If the wrapper
sets RegFileECC=1: the cap ECC decoders see a constant codeword whose error output is masked
ONLY by the `== IbexMuBiOn` term (rtl/ibex_core.sv:1281-1286), and RegFileCapEccWidth must be
REGCAP_W+7 = 42 or the part-select at :1264/:1271 is reversed (see gen_param_resolution.md Q-A).
(F10, RVFI only) rvfi_id_done suppresses the ID-stage trap entry whenever wb_exception_o is set
(rtl/ibex_core.sv:1851-1853), which covers plain load/store errors: bug candidate for RVFI-based
checking (gen_behaviour_summaries.md BUG-04). (F12) live RV32I LSU nets inside
u_ibex_cheriot_ex. (F13) dual-purpose nets that toggle in RV32I mode inside CHERIoT-labelled
blocks (mstack_epc_cap_q, pcc_cap_d, tf_cap, tr_cap, pcc_exc_cap, mshwm_d, csr_mshwm_new,
instr_hdrm): list them by name as live, never sweep them in as CHERIoT. (F15) active
invariant assertions with a true antecedent (rtl/ibex_id_stage.sv:1297-1300,
rtl/ibex_load_store_unit.sv:833-834, rtl/ibex_cs_registers.sv:1996-1997): keep as RV32I checkers;
the three register-file Cheriot*MSBClear assertions (:237-239) are vacuous.

### A.4 Size estimate (Part B section H)

About 3100 excludable candidate lines including the whole of ibex_cheriot_ex.sv and
ibex_cheriot_pkg.sv; about 250-300 lines of live RV32I logic sit inside CHERIoT-labelled code
and must be carved back in. Exclusion approach recommended to the Critic: (1) module-level
exclusion of ibex_cheriot_pkg functions is moot (no coverage objects); (2) u_ibex_cheriot_ex:
exclude, then re-include the live nets by name; (3) shared modules: exclude by cited line/branch
lists (bucket C) and constant nets (bucket D), never by block label where the block holds live
RV32I logic (B1, B4, B5, B12, B14, B15).

### A.5 Verification performed and unverified items

Verified by reading: gating chain endpoints (rtl/ibex_load_store_unit.sv:407-408, :419, :437-467,
:565-626, :688-709, :760, whole file), the alert path (rtl/ibex_core.sv:1339-1353), the PMP gates
(:1589-1634), the decoder gen_16_regs / illegal_reg_16 (rtl/ibex_decoder.sv:211-245), the
register file g_cheriot_rf (whole file). Unverified (Part B section I): U1 wrapper parameters
(RegFileECC, RegFileCapEccWidth, RF CapWidth/CapWordZeroVal, ResetAll, RVFI) which select some
buckets; U2 value of rf_cap_ecc_err on the all-zero codeword (masked regardless); U3
rtl/ibex_cheriot_ex.sv:755-865 not read line by line; U4 DII_SIM define; U5 RVFI-dependent
items; U6 ibex_trvk only if the wrapper adds it.

## Part B. Exhaustive inventory (subagent B body, verbatim)

# CHERIoT-only RTL inventory for the dual-base-ISA "opentitan" build with cheriot_enable_i == IbexMuBiOff

Basis for the single coverage exclusion `cheriot-out-of-scope`.

Build assumed: BaseIsa = BaseIsaRV32IorCHERIoT, RV32E = 0, SecureIbex = 1, WritebackStage = 1,
ICache = 1, PMPEnable = 1, PMPNumRegions = 16, DbgTriggerEn = 1, RV32M = RV32MSingleCycle,
RV32B = RV32BOTEarlGrey, RV32ZC = RV32ZcaZcbZcmp, DummyInstructions = 1, RegFileECC = 1 (see U1),
MemECC = 1. DUT hierarchy = ibex_core and below, plus ibex_register_file_ff. cheriot_enable_i is
tied to ibex_pkg::IbexMuBiOff = 4'b1010 (rtl/ibex_pkg.sv:760; IbexMuBiOn = 4'b0101 at :759).

All paths are relative to the clone root. Every entry was verified by reading the cited lines
(sed -n / grep -n). Items marked UNVERIFIED are listed in section I.

Legend for "Off state": what the net/arm does when cheriot_enable_i == IbexMuBiOff.
- CONST: holds one value forever (toggle-coverage exclusion candidate).
- UNREACH: statement/arm/branch never executes (line/cond coverage exclusion candidate).
- TOGGLES: still changes value in RV32I mode. NOT excludable by name; see bucket F.
- NOT-ELAB: generate branch not elaborated in this build (no coverage object exists).

## 0. Gating chain (proof that the CHERIoT control signals are constant 0 with Off)

G1 Decoder. rtl/ibex_decoder.sv defaults: cheriot_data_req_o = 0 (:288), cheriot_operator_o = '0
   (:297), instr_is_cheriot_o = 0 (:298), cheriot_cap_field_sel_o = CFIELD_PERM (:299),
   cheriot_adder_a_sel_o = CHERIOT_ADDER_A_ZERO (:300), cheriot_adder_b_sel_o =
   CHERIOT_ADDER_B_ZERO (:301), cheriot_setaddr_sel_o = SETADDR_NONE (:302),
   cheriot_setbounds_sel_o = SETBOUNDS_NONE (:303). Every non-default assignment of these sits
   under `(BaseIsa == BaseIsaRV32IorCHERIoT) & (cheriot_enable_i == IbexMuBiOn)`: :314-323
   (JAL), :339-352 (JALR), :402-407 (CSC), :447-453 (CLC), :474-482 (AUIPCC), :792-876
   (OPCODE_CHERI, all operator bits at :802-870), :882-891 (AUICGP). Hence with Off:
   cheriot_operator_o == '0, instr_is_cheriot_o == 0, cheriot_data_req_o == 0,
   instr_is_legal_cheriot = |cheriot_operator_o = 0 (:1459), instr_is_legal_cheriot_o = 0
   (:1460), cheriot_cs2_dec_o = 5'h0 (:1463), cheriot_imm12_o = 12'h0 (:1465-1470),
   cheriot_imm20_o = 20'h0 (:1472-1473), cheriot_imm21_o = 21'h0 (:1475-1476),
   csr_cheriot_always_ok_o = 0 (:778-781).
G2 ID stage. rtl/ibex_id_stage.sv: cheriot_exec_id_o = (cheriot_enable_i == IbexMuBiOn) & ...
   (:1069-1075, inside gen_stall_mem :1000, elaborated because WritebackStage = 1) -> 0.
   instr_is_cheriot_id_o is the decoder's instr_is_cheriot_o (:562) -> 0. cheriot_load_o =
   cheriot_operator_o.CLOAD_CAP (:580) -> 0; cheriot_store_o = .CSTORE_CAP (:582) -> 0.
   cheriot_lsu_req_dec is the decoder's cheriot_data_req_o (:552) -> 0.
G3 CHERIoT EX. rtl/ibex_cheriot_ex.sv: outputs ANDed with cheriot_exec_id_i: cheriot_rf_we_o
   (:244), branch_req_o (:245), branch_req_spec_o (:246), csr_set_mie_o (:247), csr_clr_mie_o
   (:248), csr_op_en_o (:249), cheriot_ex_valid_o (:253), cheriot_ex_err_o (:254) -> all 0.
   cheriot_wb_err_d = cheriot_wb_err_raw & cheriot_exec_id_i & ... (:880-881) -> 0 ->
   cheriot_wb_err_q = 0 (:923-931) -> cheriot_wb_err_o = cheriot_wb_err_q (:256-257,
   WritebackStage) -> 0. main_ex `unique case (1'b1)` over cheriot_operator_i == '0 takes
   `default:;` (:556), so the defaults hold: result_data_o = 32'h0 (:268), result_cap_o =
   NULL_CAP (:269), csr_access_o = 0 (:274), csr_addr_o = 5'h0, csr_wdata_o = 0, csr_wcap_o =
   NULL_CAP, csr_op_o = CHERIOT_CSR_NULL (:275-279), branch_target_o = 32'h0 (:286),
   pcc_cap_o = NULL_DECODED_CAP (:287). cheriot_ex_err_info_o = 12'h0 (:878).
   LSU mux: lsu_req_o = rv32_lsu_req_i (:943); rv32_lsu_err = (cheriot_enable_i == IbexMuBiOn)
   & ... (:740-741) -> 0; cheriot_lsu_err = (cheriot_enable_i == IbexMuBiOn) & ... (:869-870)
   -> 0; cpu_lsu_cheriot_err (:945) -> 0 -> lsu_cheriot_err_o = 0 (:951); lsu_is_cap_o =
   instr_is_cheriot_i & cheriot_lsu_is_cap (:949, :955) -> 0; lsu_lc_clrperm_o = '0 (:957);
   lsu_type_o = rv32_lsu_type_i (:958); lsu_wcap_o = NULL_CAP (:959); lsu_sign_ext_o =
   rv32_lsu_sign_ext_i (:960). cheriot_wb_err_info_d (:905-918): every update arm requires
   cheriot_exec_id_i or rv32_lsu_err, so cheriot_wb_err_info_q stays '0 -> cheriot_wb_err_info_o
   = 16'h0 (:879). csr_mshwm_set_o (:991-993) needs lsu_addr_o[31:4] < csr_mshwm_i[31:4] with
   csr_mshwm_i == 0 (G6) -> 0. rv32_addr_incr_req_o = addr_incr_req_i because
   (cheriot_enable_i != IbexMuBiOn) is true (:970-971).
G4 LSU. rtl/ibex_load_store_unit.sv: cheriot_err_d is forced 0 at :419, :435 and only set at
   :441 under (cheriot_enable_i == IbexMuBiOn) & cpu_req_erred (:437-438) -> cheriot_err_q = 0
   (:654); lsu_err_is_cheriot_o = (cheriot_enable_i == IbexMuBiOn) & cheriot_err_q (:760) -> 0;
   resp_is_cap_q <= lsu_is_cap_i (= 0) on lsu_go (:664-665) -> 0.
G5 Controller. rtl/ibex_controller.sv: cheriot_ex_err = cheriot_ex_err_i & instr_is_cheriot_i &
   instr_valid_i (:234) -> 0; g_cheriot_asr_err (:236-240) terms ANDed with
   (cheriot_enable_i == IbexMuBiOn) -> 0; cheriot_ex_err_d (:256-257) -> 0; cheriot_asr_err_d
   (:259) -> 0; flops in gen_update_regs_cheriot (:1054-1067) load lsu_err_is_cheriot_i (0),
   cheriot_ex_err_d (0), cheriot_wb_err_i (0), cheriot_asr_err_d (0) -> all 0.
G6 CS registers. rtl/ibex_cs_registers.sv: pcc_cap_q resets to ROOT_DECODED_CAP_TX and is
   updated only when (cheriot_enable_i == IbexMuBiOn) (:2063-2067) -> CONST. ROOT perms =
   12'h1eb (rtl/ibex_cheriot_pkg.sv:157), perms_t bit 7 = SR (:39-52) -> SR = 1, so
   csr_pcc_perm_sr_i (rtl/ibex_core.sv:760 = pcc_cap_r.perms.SR) is CONST 1. mshwm_en,
   mshwmb_en, cdbg_ctrl_en = (BaseIsa == dual) & (cheriot_enable_i == IbexMuBiOn) (:879-884)
   -> 0; mshwm_en_combi = mshwm_en | csr_mshwm_set_i (:1302) -> 0 (G3), so mshwm_q, mshwmb_q,
   cdbg_ctrl_q stay at reset '0 (:1305-1343); csr_dbg_tclr_fault_o = cdbg_ctrl_q[0] (:1345)
   -> 0. mepc_cap, mtvec_cap, mtdc_cap, mscratchc_cap, depc_cap, dscratch0/1_cap update only
   under (cheriot_enable_i == IbexMuBiOn) or *_en_cheriot (which need cheriot_csr_op_en_i = 0
   per G3): :2108-2118, :2121-2146, :2149-2160, :2164-2175, :2179-2190, :2194-2209 -> CONST.
   cheriot_fatal_err_q set only under (cheriot_enable_i == IbexMuBiOn) (:2218-2224) -> 0.
G7 IF stage. rtl/ibex_if_stage.sv: cheriot_bound_vio (:456-457), cheriot_force_uc (:464-465),
   cheriot_acc_vio (:469-472) each start with `(BaseIsa == BaseIsaRV32IorCHERIoT) &
   (cheriot_enable_i == IbexMuBiOn) &` -> 0; instr_fetch_cheriot_acc_vio_o /
   instr_fetch_cheriot_bound_vio_o flops (:634-652) load those zeros -> CONST 0.
G8 Register file. rtl/ibex_register_file_ff.sv: cheriot_enabled = (cheriot_enable_i ==
   IbexMuBiOn) (:94-95) -> CONST 0; rcap_a_o / rcap_b_o = CapWordZeroVal (:227-230) -> CONST;
   therefore rtl/ibex_core.sv rf_rcap_a / rf_rcap_b = cheriot_vec_to_regcap(rf_rcap_*_ecc_i
   [REGCAP_W-1:0]) (:286-287) = NULL_CAP (assuming CapWordZeroVal = '0, see U1).

## A. Whole modules / files that are CHERIoT-only

A1. rtl/ibex_cheriot_ex.sv (1031 lines, 284 `cheri` hits). Instance `u_ibex_cheriot_ex` inside
    generate block `g_cheriot_ex`, condition `if (BaseIsa == BaseIsaRV32IorCHERIoT)` at
    rtl/ibex_core.sv:911-1001. It DOES elaborate in this build; the tie-off branch
    `gen_no_cheriot_ex` (rtl/ibex_core.sv:1002-1056) is NOT-ELAB.
    Caveat for the exclusion: the RV32I load/store path is routed THROUGH this module in the
    dual build, so a blanket module exclusion would hide live RV32I logic. Nets that TOGGLE in
    Off mode inside u_ibex_cheriot_ex:
    - pass-through LSU mux outputs: lsu_req_o (:943), lsu_we_o (:947,:952), lsu_addr_o
      (:946,:953), lsu_wdata_o (:948,:954), lsu_type_o (:958), lsu_sign_ext_o (:960),
      rv32_addr_incr_req_o (:970-971), rv32_addr_last_o (:973);
    - fwd_data_merger (:219-233): rf_rdata_ng_a/b and the compare terms toggle; rf_rcap_ng_a/b
      are CONST NULL_CAP (both sources NULL_CAP, G8 and wb_stage :216);
    - rf_rdata_a = (instr_is_cheriot_i | instr_is_rv32lsu_i) ? rf_rdata_ng_a : 0 (:232) toggles
      because instr_is_rv32lsu_i = lsu_req_dec (rtl/ibex_id_stage.sv:576) toggles;
      rf_rdata_b = 0 (:235) CONST; rf_rcap_a/b (:231,:234) CONST NULL_CAP;
    - rf_fullcap_a = cheriot_decode_cap(NULL_CAP, rf_rdata_a) (:237): base32/top33 toggle with
      the address; rf_fullcap_b (:238) CONST;
    - cs1_imm = 0 (:587-588) CONST; cs1_addr_plusimm = rf_rdata_a (:590) toggles; pc_id_nxt
      (:592) toggles; shared_adder tmp32a/tmp32b/addr_result (:601-616) CONST 0 (selectors at
      ZERO); set_address_comb / set_bounds_comb (:622-670) CONST (selectors NONE);
    - check_rv32 (:701-738): rv32_top_offset, rv32_top_size_ok, rv32_top_bound, rv32_top_vio,
      rv32_base_vio, addr_bound_vio_rv32, perm_vio_vec_rv32 ([PVIO_TAG] CONST 1, [PVIO_LD]/
      [PVIO_SD] toggle with rv32_lsu_we_i), perm_vio_rv32 toggle; rv32_lsu_err CONST 0 (:740);
    - check_cheriot (:755-865): chk_* nets depend on cs1_addr_plusimm and toggle (UNVERIFIED
      line by line, see U3); cheriot_lsu_err CONST 0 (:869-870);
    - err_cause_comb (:884-918): cheriot_err_cause, rv32_err_cause, addr_bound_vio_ext,
      ls_addr_misaligned_only toggle; cheriot_wb_err_info_d CONST (= q = 0);
    - csr_mshwm_new_o = {lsu_addr_o[31:4], 4'h0} (:994) toggles but is dead (mshwm_en_combi = 0).
    Everything else in the module is CONST/UNREACH in Off mode (main_ex arms :290-555 UNREACH,
    cheriot_lsu_* :572-585 CONST 0, all *_raw CONST 0).
    Recommendation: exclude the module, then re-include (or list as live) the toggling nets above.

A2. rtl/ibex_cheriot_pkg.sv (965 lines, 97 hits). Package-only; no instance. Items used from
    shared modules even in RV32I mode (they define types/constants of live nets and so cannot be
    "excluded" as such; listed for completeness):
    - types: cap_t (:87-98, 35 bits = REGCAP_W), decoded_cap_t (:100-115), perms_t (:39-52),
      cap_clrperm_t (:135-139), cheriot_op_t (:837-864), cheriot_cap_field_e (:866-875),
      cheriot_adder_a_sel_e (:877-883), cheriot_adder_b_sel_e (:885-889), cheriot_setaddr_sel_e
      (:891-897), cheriot_setbounds_sel_e (:899-907), cheriot_csr_op_e (:909-912).
    - constants: REGCAP_W = 35 (:28; used as parameter default rtl/ibex_core.sv:50 and
      rtl/ibex_register_file_ff.sv:58, and 9 times in rtl/ibex_core.sv), NULL_CAP (:144),
      NULL_DECODED_CAP (:145), ROOT_DECODED_CAP_TX (:154-166), ROOT_CAP_TX (:167), ROOT_CAP_TM
      (:170-180), ROOT_CAP_TS (:182-192), CHERIOT_SCR_* (:914-921), CHERIOT_CSR_NULL /
      CHERIOT_CSR_RW (:909-912).
    - functions evaluated in RV32I mode (continuous assigns, so their bodies "execute"):
      cheriot_vec_to_regcap (:810-812) at rtl/ibex_core.sv:286-287 (CONST input);
      cheriot_regcap_to_vec (:805-807) at rtl/ibex_core.sv:1253,1257 (gen_cheriot_cap_ecc, CONST
      input) and :1295,:1315 (NOT-ELAB branches); cheriot_pcc_to_mepc (:736-748) at
      rtl/ibex_cs_registers.sv:2061 (TOGGLES with exception_pc); cheriot_decode_cap (:701-724)
      at rtl/ibex_cs_registers.sv:2095 (TOGGLES with mepc_q/mtvec_q/depc_q) and
      rtl/ibex_cheriot_ex.sv:237-238 (TOGGLES with rf_rdata_a); cheriot_cap_to_mem (:795-801)
      at rtl/ibex_load_store_unit.sv:213 (UNREACH arm); cheriot_mem_to_cap (:763-790) at
      rtl/ibex_load_store_unit.sv:707 (UNREACH side of a ternary); cheriot_violation_cause
      (:937-963) at rtl/ibex_cheriot_ex.sv:885-886 (TOGGLES). The rest of the package's
      functions (:203-733, :815-830) are reached only from the above or from UNREACH arms.

A3. rtl/ibex_trvk.sv (420 lines, 7 hits). NOT in the ibex_core hierarchy. ibex_core.core file
    list (ibex_core.core:19-40) and rtl/ibex_core.f do not name it; it is listed only in
    ibex_top.core:29 and instantiated only in rtl/ibex_top.sv:1275-1320 (generate
    `gen_cheriot_trvk`, instance `i_ibex_trvk`, else `gen_no_cheriot_trvk` :1321-1354). No
    `trvk` string occurs in rtl/ibex_core.sv. Out of the DUT; no exclusion needed unless the
    wrapper adds it (UNVERIFIED, U1). Likewise outside the DUT: rtl/ibex_lockstep.sv (11 hits),
    rtl/ibex_register_file_fpga.sv (30), rtl/ibex_register_file_latch.sv (37), rtl/ibex_top.sv
    (20), rtl/ibex_top_tracing.sv (8), rtl/ibex_tracer.sv (77), rtl/ibex_tracer_pkg.sv (30).

## B. Generate blocks in shared modules elaborated under BaseIsa == BaseIsaRV32IorCHERIoT

| # | File:lines | Label | What it does | Off state |
|---|---|---|---|---|
| B1 | rtl/ibex_core.sv:911-1001 | g_cheriot_ex | instantiates u_ibex_cheriot_ex; branch_target_ex mux (:1000-1001) | instance: see A1; mux select `instr_valid_id & instr_is_cheriot_id` CONST 0, branch_target_ex = branch_target_ex_rv32 TOGGLES |
| B2 | rtl/ibex_core.sv:1244-1290 | gen_cheriot_cap_ecc (inside `if (RegFileECC)` :1218) | prim_secded_inv_64_57_enc regfile_cap_ecc_enc on {22'b0, vec(rf_wcap_wb)} (:1252-1255); rf_wcap_ecc_wb_o = {wcap_ecc_tmp[63:57], vec(rf_wcap_wb)} (:1257); prim_secded_inv_64_57_dec regfile_cap_ecc_dec_a/_b on {rf_rcap_x_ecc_i[41:35], 22'b0, rf_rcap_x_ecc_i[34:0]} (:1263-1276); rf_ecc_err_x_id include `((cheriot_enable_i == IbexMuBiOn) & \|rf_cap_ecc_err_x)` (:1281-1286) | encoder input CONST (rf_wcap_wb = NULL_CAP), wcap_ecc_tmp and rf_wcap_ecc_wb_o CONST; decoder inputs CONST (G8); rf_cap_ecc_err_a/b CONST (value UNVERIFIED, U2) and masked by the cheriot_enable term, so the CHERIoT half of :1281-1286 is CONST 0; data-ECC half TOGGLES normally. Elaboration itself depends on RegFileECC=1 and RegFileCapEccWidth=REGCAP_W+7 in the wrapper (U1) |
| B3 | rtl/ibex_core.sv:1342-1344 | gen_cheriot_enable_check | cheriot_enable_mubi_err (see E) | CONST 0 |
| B4 | rtl/ibex_core.sv:1589-1593 | g_pmp_addr_gate (inside `if (PMPEnable)` :1580) | pmp_req_addr[PMP_I/I2/D] = (On) ? '0 : {2'b00, pc_if / pc_if_inc / data_addr_o} | selects the RV32I operand; TOGGLES; the '0 side UNREACH |
| B5 | rtl/ibex_core.sv:1626-1630 | g_pmp_cheriot_gate | pmp_req_err[x] = (On) ? 1'b0 : pmp_req_err_raw[x] | pass-through, TOGGLES; 1'b0 side UNREACH |
| B6 | rtl/ibex_core.sv:2286-2295 | g_rvfi_cap (under `ifdef RVFI`) | rvfi_rs1/rs2_cap_d = rf_ren_x ? g_cheriot_ex.u_ibex_cheriot_ex.rf_rcap_x : NULL_CAP | both arms NULL_CAP (rtl/ibex_cheriot_ex.sv:231,:234 with G8) -> CONST; the select rf_ren_a/b toggles |
| B7 | rtl/ibex_if_stage.sv:634-652 | gen_cheriot_vio_regs (g_cheriot_vio_ra or g_cheriot_vio_nr by ResetAll) | flops instr_fetch_cheriot_acc_vio_o / bound_vio_o loaded on if_id_pipe_reg_we | data CONST 0 (G7); enable TOGGLES |
| B8 | rtl/ibex_decoder.sv:211-217 | gen_16_regs (CheriLimit16Regs = 1, :124) | rf_raddr_a_o/rf_raddr_b_o/rf_waddr_o = (On) ? {1'b0, x[3:0]} : x | pass-through, TOGGLES; masked side UNREACH |
| B9 | rtl/ibex_decoder.sv:237-242 | gen_16reg_check_active (`RV32E \|\| CheriLimit16Regs`) | illegal_reg_16 = (RV32E \|\| (On)) && (...) | CONST 0 (left factor 0); the right-hand sub-terms TOGGLE |
| B10 | rtl/ibex_controller.sv:236-240 | g_cheriot_asr_err | mret_cheriot_asr_err, csr_cheriot_asr_err | CONST 0 |
| B11 | rtl/ibex_controller.sv:1054-1067 | gen_update_regs_cheriot | 4 flops lsu_err_is_cheriot_q, cheriot_ex_err_q, cheriot_wb_err_q, cheriot_asr_err_q | CONST 0 |
| B12 | rtl/ibex_load_store_unit.sv:701-709 | gen_memcap_rd | lsu_rdata_o = ((On) & resp_is_cap_q) ? cap_lsw_data_q : data_rdata_ext; lsu_rcap_o = (...) ? cheriot_mem_to_cap(...) : NULL_CAP | lsu_rdata_o = data_rdata_ext TOGGLES (RV32I load data path!); lsu_rcap_o CONST NULL_CAP |
| B13 | rtl/ibex_cs_registers.sv:1304-1345 | g_mshwm | ibex_csr u_mshwm_csr (:1305-1316), u_mshwmb_csr (:1318-1329), u_cdbg_ctrl_csr (:1332-1343); csr_dbg_tclr_fault_o (:1345) | wr_en all CONST 0 -> mshwm_q, mshwmb_q, cdbg_ctrl_q CONST 0; wr_data mshwm_d (:1303) and {csr_wdata_int[31:4],4'h0} TOGGLE but dead |
| B14 | rtl/ibex_cs_registers.sv:2003-2228 | gen_scr | SCR read mux (:2014-2056); pcc_cap_q/pcc_cap_d (:2058-2105); mtvec/mepc/mtdc/mscratchc/depc/dscratch caps (:2107-2209); cheriot_fatal_err_q (:2212-2224) | read mux CONST (cheriot_csr_addr_i = 5'h0 -> default arm :2051-2055); pcc_cap_q CONST ROOT_DECODED_CAP_TX; tr_cap/tr_addr/tf_cap/pcc_cap_d (:2075-2105) TOGGLE on csr_save_cause_i / csr_restore_mret_i / dret; pcc_exc_cap (:2061) TOGGLES with exception_pc; all *_en_cheriot CONST 0; mtvec_cap/mepc_cap = ROOT_CAP_TX, mtdc_cap = ROOT_CAP_TM, mscratchc_cap = ROOT_CAP_TS, depc/dscratch0/1_cap = NULL_CAP CONST; mtdc_data/mscratchc_data CONST 0; mstack_epc_cap_q (:2127-2133) TOGGLES once NULL_CAP -> ROOT_CAP_TX on the first NMI (mstack_en set at :933); cheriot_fatal_err_q CONST 0 |
| B15 | rtl/ibex_register_file_ff.sv:88-239 | g_cheriot_rf | THE register file of this build (g_plain_rf :241-327 NOT-ELAB). cheriot_enabled (:94-95); rf_data[16] and rf_shared[16] (:98-99); we_a_dec (:105-109); wshared_data (:112-113); g_rf_data_flops (:116-127); g_rf_shared_flops (:131-141); g_dummy_r0 (:155-186, DummyInstructions = 1; g_normal_r0 :188-212 NOT-ELAB); read muxes (:221-230); assertions (:237-239) | cheriot_enabled CONST 0. rf_data[1..15] TOGGLE (x1-x15). rf_shared[1..15] TOGGLE as x17-x31 via `(!cheriot_enabled && !RV32E && we_a_dec[i] && waddr_a_i[4])` (:136-137); wshared_data = CapWidth'(wdata_a_i) TOGGLES, bits [CapWidth-1:32] CONST 0. g_dummy_r0: we_data_r0 (:159) TOGGLES, rf_data_r0_q (:164-171) TOGGLES, we_shared_r0 = x16 write (:160-161) TOGGLES, rf_shared_r0_q = x16 data (:174-181) TOGGLES, rcap_r0 = dummy_instr_id_i ? rf_shared[0] : 0 (:184) TOGGLES (x16 data on a cap net during dummy instructions; unobservable). rdata_a_o/rdata_b_o bank select `raddr_x_i[4] && !cheriot_enabled` (:221-224) TOGGLES. rcap_a_o/rcap_b_o (:227-230) CONST CapWordZeroVal. Assertions :237-239 vacuous |

## C. Conditional arms in shared always blocks / assigns guarded by CHERIoT-only conditions

Format: line(s) -- what the arm does -- Off state. "term" = an OR/AND sub-term that is constant.

### rtl/ibex_core.sv
- :1000-1001 -- branch_target_ex ternary on `instr_valid_id & instr_is_cheriot_id` -- select CONST 0, cheriot side UNREACH.
- :1281-1286 -- `((cheriot_enable_i == IbexMuBiOn) & |rf_cap_ecc_err_a/b)` terms in rf_ecc_err_a_id/b_id -- term CONST 0 (B2).
- :1343-1344 -- cheriot_enable_mubi_err (E) -- CONST 0.
- :1350-1351 -- alert_major_internal_o terms `cheriot_fatal_err | cheriot_enable_mubi_err` -- CONST 0.
- :1590-1593, :1627-1630 -- PMP gating ternaries (B4, B5) -- CHERIoT sides UNREACH.
- :2211-2212 / :2216-2217 (RVFI) -- rvfi_mem_wcap_d = lsu_wcap, rvfi_mem_is_cap_d = lsu_is_cap -- CONST NULL_CAP / 0.
- :2223-2225 (RVFI) -- `if (load_store_unit_i.resp_is_cap_q & lsu_resp_valid)` arm -- UNREACH (resp_is_cap_q CONST 0, G4); else-if :2226-2228 reachable.
- :2289-2290 (RVFI) -- rvfi_rs1/rs2_cap_d ternaries -- both arms NULL_CAP (B6).
- :2346-2349, :2356, :2361 (RVFI) -- rvfi_rd_cap_d = rf_wcap_wb / NULL_CAP / q -- all CONST NULL_CAP.

### rtl/ibex_if_stage.sv
- :222-228 -- exc_pc mux: EXC_PC_EXC and EXC_PC_IRQ ternaries `(dual) & (On) ? {mtvec[31:2],2'b00} : baseline` -- CHERIoT sides UNREACH; baseline sides reachable.
- :368 -- `.cheriot_force_uc_i (cheriot_force_uc)` into prefetch buffer -- CONST 0.
- :430 -- if_instr_err OR terms `cheriot_acc_vio | cheriot_bound_vio` -- CONST 0.
- :445 -- allow_all = (pcc_cap_i.base32 == 0) & (pcc_cap_i.top33 == 33'h1_0000_0000) -- CONST 1 (pcc_cap_i = ROOT_DECODED_CAP_TX, rtl/ibex_cheriot_pkg.sv:155-156).
- :447-449 -- instr_hdrm, hdrm_ge4, hdrm_ge2 -- TOGGLE with if_instr_addr (dead: consumers gated).
- :452 -- hdrm_ok = allow_all || ... -- CONST 1; :453 base_ok -- CONST 1.
- :456-457, :464-465, :469-472 -- cheriot_bound_vio, cheriot_force_uc, cheriot_acc_vio -- CONST 0 (G7).
- :495 -- `.cheriot_enable_i` to compressed decoder -- tie.
- :207-210 gen_no_cheriot_if -- NOT-ELAB.

### rtl/ibex_id_stage.sv
- :578 -- ex_valid_all = instr_is_cheriot_id_o ? cheriot_ex_valid_i : ex_valid_i -- select CONST 0.
- :580, :582 -- cheriot_load_o / cheriot_store_o -- CONST 0.
- :746-749 -- csr_op_en_o ternary `((dual) & (On)) ? instr_first_cycle : instr_id_done_o` -- baseline side; CHERIoT side UNREACH.
- :901-908 -- `cheriot_lsu_req_dec:` case item in FIRST_CYCLE (and its inner `if (cheriot_enable_i == IbexMuBiOn)`) -- UNREACH (cheriot_lsu_req_dec CONST 0).
- :1012 -- multicycle_done select `(lsu_req_dec | cheriot_lsu_req_dec)` -- term CONST 0.
- :1033-1036 -- instr_kill uses id_exception_nc (see F12) -- live.
- :1069-1075 -- cheriot_exec_id_o -- CONST 0.
- :1095-1096 -- stall_mem term `(lsu_req_dec | cheriot_lsu_req_dec)` -- term CONST 0.
- :1144, :1151, :1160, :1199-1200 -- inside gen_no_stall_mem (:1142) -- NOT-ELAB (WritebackStage = 1).
- :1297-1300 -- ASSERT_IF IbexCheriotLoadDisabled / StoreDisabled / IbexInstrNotCheriot / IbexCheriotExecDisabled -- active (antecedent `cheriot_enable_i != IbexMuBiOn` true); they check the invariant, keep.

### rtl/ibex_decoder.sv
- :202 -- raddr_a = cheriot_operator_o.CAUICGP ? 5'h3 : ... -- select CONST 0.
- :212-217 -- gen_16_regs ternaries (B8) -- CHERIoT side UNREACH.
- :238 -- illegal_reg_16 (B9) -- CONST 0.
- :314-323 -- OPCODE_JAL CHERIoT arm -- UNREACH; else :324-334 reachable.
- :339-352 -- OPCODE_JALR CHERIoT arm -- UNREACH; else :353-363 reachable.
- :402-407 -- OPCODE_STORE funct3 2'b11 CHERIoT arm -- UNREACH; else :408-410 (illegal, sd) reachable.
- :447-453 -- OPCODE_LOAD funct3 2'b11 CHERIoT arm -- UNREACH; else :454-456 (illegal, ld) reachable.
- :474-482 -- OPCODE_AUIPC CHERIoT arm -- UNREACH; else :483-485 reachable.
- :778-781 -- csr_cheriot_always_ok_o -- CONST 0.
- :791-878 -- OPCODE_CHERI case item: outer `if ((dual) & (On) & ~illegal_c_insn_i)` body :793-876 -- UNREACH; else :877-878 (illegal_insn = 1) reachable, so opcode 7'h5b traps as illegal in RV32I mode.
- :881-893 -- OPCODE_AUICGP: body :883-891 UNREACH; else :892-893 (illegal) reachable.
- :1459-1476 -- instr_is_legal_cheriot(_o), cheriot_cs2_dec_o, cheriot_imm12/20/21_o -- CONST (G1).
- :1478-1481 gen_no_cheriot_decoder -- NOT-ELAB. :1067 is a comment.

### rtl/ibex_compressed_decoder.sv (all arms guarded by `(dual) && (cheriot_enable_i == IbexMuBiOn)`)
- :230-233 c.addi4spn -> cincoffsetimm -- UNREACH; else :234-236 reachable.
- :249-252 c.clc -- UNREACH; else :253-255 (illegal) reachable.
- :329-332 c.csc -- UNREACH; else :333-335 (illegal) reachable.
- :359-363 c.addi hint zero-rd -- UNREACH; else :364-366 reachable.
- :391-394 c.incaddr16csp -- UNREACH; else-if :395-398 (c.addi16sp) reachable.
- :411-414 c.srli/c.srai hint zero-rd -- UNREACH; else :415-417 reachable.
- :557-560 c.slli hint zero-rd -- UNREACH; else :561-562 reachable.
- :575-579 c.clcsp -- UNREACH; else :580-582 (illegal) reachable.
- :615-620 Zcmp-illegal-in-CHERIoT -- UNREACH; else-if :621 (RV32ZC Zcmp expansion) reachable.
- :854-857 c.cscsp -- UNREACH; else :858-860 (illegal) reachable.
- :911-914 gen_no_cheriot_cdec -- NOT-ELAB. :20, :27 parameter/port.

### rtl/ibex_controller.sv
- :234 cheriot_ex_err -- CONST 0. :237-240 (B10). :256-257 cheriot_ex_err_d, :259 cheriot_asr_err_d -- CONST 0.
- :268-272 exc_req_d / exc_req_nc extra terms `((On) & cheriot_ex_err)`, `cheriot_asr_err_d` -- CONST 0 (so exc_req_d == exc_req_nc).
- :276 exc_req_wb term `((On) & cheriot_wb_err_i)` -- CONST 0.
- :318-319, :328-331 -- prio arms `((On) & cheriot_wb_err_q)`, `((On) & cheriot_ex_err_q)`, `cheriot_asr_err_q` in g_wb_exceptions -- UNREACH.
- :336-337 wb_exception_o term -- CONST 0.
- :346-367 g_no_wb_exceptions -- NOT-ELAB.
- :377-383 IbexExceptionPrioOnehot includes the three cheriot prio bits -- active, keep.
- :681-682 pc_set condition term `((On) & cheriot_branch_req_i)` -- CONST 0.
- :827-828 FLUSH exception-entry term `((On) & cheriot_wb_err_q)` -- CONST 0.
- :837-840 csr_save_id_o / csr_save_wb_o terms -- CONST 0.
- :850-858 instr_fetch_err_prio: two CHERIoT arms (ExcCauseCheriFault, csr_mepcc_clrtag_o = 1 at :858) -- UNREACH; else :859-862 reachable.
- :866-868 illegal_insn mtval ternary -- CHERIoT side (32'h0) UNREACH; baseline side reachable.
- :894-897 ebreak mtval = pc_id_i -- UNREACH.
- :901-908 store_err_prio `if ((On) & lsu_err_is_cheriot_q)` -- UNREACH; else :909-911 reachable.
- :915-922 load_err_prio same -- UNREACH; else :923-925 reachable.
- :928-933 cheriot_ex_err_prio item, :934-944 cheriot_wb_err_prio item, :945-948 cheriot_asr_err_prio item -- UNREACH.
- :549 csr_mepcc_clrtag_o default 0; only set at :858 -- CONST 0.
- :1054-1067 (B11). :1068-1075 gen_cheriot_tieoff -- NOT-ELAB. :1125-1131 unused-signal sink.

### rtl/ibex_load_store_unit.sv
- :131-132 data_offset ternary `(dual) & (On) & lsu_is_cap_i ? 2'b00 : data_addr[1:0]` -- baseline side.
- :139-140 data_be = 4'b1111 cap arm -- UNREACH; else :141+ reachable.
- :211-219 {data_wdata_tag, data_wdata_data} cap arms (incl. cheriot_cap_to_mem at :213, `ls_fsm_cs == CTX_WAIT_GNT2` at :212) -- UNREACH; else :220 `{1'b0, wdata_int}` reachable.
- :407 cpu_req_valid term `~((On) & lsu_cheriot_err_i)` -- CONST 1; :408 cpu_req_erred -- CONST 0.
- :419 cheriot_err_d = cheriot_err_q & (On) -- CONST 0.
- :437-448 IDLE first arm (cpu_req_erred) -- UNREACH; :449-467 IDLE cap-access arm (sets ls_fsm_ns = CTX_WAIT_GNT2/GNT1 at :464/:466) -- UNREACH; :468+ normal arm reachable.
- :565-603 states CTX_WAIT_GNT1, CTX_WAIT_GNT2, CTX_WAIT_RESP (incl. their inner `if (On)` and `else ls_fsm_ns = IDLE`) -- UNREACH (never entered; CTX_* assigned only at :464, :466, :570, :586).
- :610-625 cap_rx_fsm: :616-617 condition `(dual) & (On) & lsu_go_goodcap` false; CRX_WAIT_RESP1/2 items :618-623 -- UNREACH; cap_rx_fsm_q CONST CRX_IDLE.
- :654 cheriot_err_q <= 0, :656 cap_rx_fsm_q <= CRX_IDLE, :664-666 resp_is_cap_q <= 0 / resp_lc_clrperm_q <= '0 (written on lsu_go but CONST) -- CONST.
- :669-678 cap_lsw_data_q / cap_lsw_tag_q / cap_lsw_err_q updates under (On) -- UNREACH; flops CONST 0.
- :688-690 data_or_pmp_err term `((On) & (cheriot_err_q | (resp_is_cap_q & cap_lsw_err_q)))` -- CONST 0; :692-693 all_resp term -- CONST 0.
- :701-709 (B12); :710-715 gen_no_cap_rd -- NOT-ELAB.
- :740 data_tag_o = data_wdata_tag -- CONST 0.
- :760 lsu_err_is_cheriot_o -- CONST 0.
- :821-824 IbexLsuStateValid lists CTX_* -- fine. :833-834 ASSERT_IF IbexLsuIsCapDisabled / IbexLsuCheriotErrDisabled -- active, keep.

### rtl/ibex_wb_stage.sv (g_writeback_stage elaborated; g_bypass_wb :245-295 NOT-ELAB incl. :251-255, :279, :286)
- :115-116 wb_done term `~(wb_is_cheriot_q && (wb_cheriot_load_q | wb_cheriot_store_q))` -- CONST 1.
- :137-142 (reset), :152-157 / :171-176 (load) of wb_is_cheriot_q, wb_cheriot_load_q, wb_cheriot_store_q, cheriot_rf_we_q, cheriot_rf_wdata_q, cheriot_rf_wcap_q -- inputs CONST (G2, G3) -> flops CONST 0 / NULL_CAP. Which of g_wb_regs_ra (:130-158) / g_wb_regs_nr (:159-178) elaborates depends on ResetAll (U1).
- :182-183 rf_wdata_wb_mux[0] / _we[0] ternaries on wb_is_cheriot_q -- select CONST 0.
- :190-191 rf_write_wb_o terms `(wb_is_cheriot_q & cheriot_rf_we_q) | wb_cheriot_load_q` -- CONST 0; :194, :196 `| wb_cheriot_load_q`, `| wb_cheriot_store_q` -- CONST 0.
- :215 rf_wdata_fwd_wb_o ternary -- select CONST 0; :216 rf_wcap_fwd_wb_o -- CONST NULL_CAP; :217-218 rf_wcap_wb -- CONST NULL_CAP.

### rtl/ibex_cs_registers.sv
- :182 MisaXBit = RV32BExtra | 32'(dual) -- localparam 1 (RV32BExtra = 1 because RV32B != RV32BNone, :179).
- :377-391 misa_value_masked: X = `(On) || (RV32BExtra != 0)` -> 1; I = `(cheriot_enable_i != On)` -> 1; E = `(On)` -> 0 -- CONST; equals MISA_VALUE (:188-203) of a plain RV32I build with the same RV32B. Read at :452.
- :424-426 CSR_MARCHID ternary -- CSR_MARCHID_VALUE side; CSR_MARCHID_CHERIOT_VALUE (32'hce1, rtl/ibex_pkg.sv:728) UNREACH.
- :469-475 CSR_MTVEC `if ((dual) && (On)) illegal_csr` -- UNREACH; else reachable. :478-484 CSR_MEPC same.
- :504-512 CSR_MSECCFG / :516-522 CSR_MSECCFGH `PMPEnable && !((dual) && (On))` -- true; illegal else UNREACH.
- :678-698 CSR_MSHWM / CSR_MSHWMB / CSR_CDBG_CTRL `if (cheriot_enable_i == IbexMuBiOn)` read arms -- UNREACH; else `illegal_csr = 1` reachable (reads of 0xBC1/0xBC2/0xBC4 trap, same as a baseline Ibex hitting `default`).
- :707-715 PMP-CSR illegal block `(!PMPEnable || ((dual) && (On)))` -- UNREACH.
- :739-743 mtvec_d LSB `~((dual) & (On))` -- CONST 1 (vectored mode, matches baseline).
- :796-797 mepc_en, :807-808 mtvec_en `~(dual) | (cheriot_enable_i != On)` -- CONST 1 when the case item is hit.
- :879-884 mshwm_en / mshwmb_en / cdbg_ctrl_en -- case items reachable (a write to 0xBC1/2/4 is decoded) but assign CONST 0; the write is then also flagged illegal by :678-698 so the item is only hit on an illegal write.
- :1020-1023 csr_we_int term `(~(dual) | (cheriot_enable_i != On) | debug_mode_i | pcc_cap_q.perms.SR)` -- CONST 1.
- :1062-1063 mstatus_en_combi term -- CONST 0; :1066-1069 mstatus_d_combi.mie clr/set terms -- CONST, pass-through.
- :1085-1086 mepc, :1163-1167 mtvec, :1203-1204 depc, :1220-1222 dscratch0, :1238-1240 dscratch1 `*_en_combi = *_en | *_en_cheriot`, `*_d_combi` AND-OR -- cheriot halves CONST 0.
- :1302-1303 mshwm_en_combi CONST 0; mshwm_d TOGGLES (dead).
- :1996-1997 ASSERT_IF IbexCheriotClrMieDisabled / SetMieDisabled -- active, keep.
- :2003-2228 (B14); :2229-2257 gen_no_scr -- NOT-ELAB; :2259-2260 unused sink.

### rtl/ibex_register_file_ff.sv (see B15)
- :113 wshared_data ternary -- CapWidth'(wdata_a_i) side; wcap_a_i side UNREACH.
- :136-137 shared-flop enable: first OR term `(cheriot_enabled && ...)` CONST 0; second term live.
- :160-161 we_shared_r0 ternary -- x16-write side live.
- :184 rcap_r0 ternary -- TOGGLES (F2).
- :202 -- inside g_normal_r0 -- NOT-ELAB (DummyInstructions = 1).
- :221-224 rdata bank select `raddr_x_i[4] && !cheriot_enabled` -- reduces to raddr_x_i[4], live.
- :227-230 rcap_a_o / rcap_b_o ternaries -- CapWordZeroVal side; cap side UNREACH.
- :237-239 CheriotWaddrMSBClear / CheriotRaddrAMSBClear / CheriotRaddrBMSBClear -- vacuous.
- :324-325 -- inside g_plain_rf -- NOT-ELAB.

### rtl/ibex_prefetch_buffer.sv
- :30 port cheriot_force_uc_i, :104 pass to fetch_fifo -- CONST 0.

### rtl/ibex_fetch_fifo.sv
- :33 port. :120 `out_addr_o[1] & cheriot_force_uc_i` is inside `ifdef DII_SIM` (:108) -- likely NOT compiled (U4). :127 unaligned_is_compressed term `cheriot_force_uc_i |` -- CONST 0.

### Files with zero `cheri` hits (verified by grep -c): rtl/ibex_alu.sv, rtl/ibex_pmp.sv,
rtl/ibex_icache.sv, rtl/ibex_dummy_instr.sv, rtl/ibex_multdiv_fast.sv, rtl/ibex_multdiv_slow.sv,
rtl/ibex_counter.sv, rtl/ibex_csr.sv, rtl/ibex_ex_block.sv, rtl/ibex_branch_predict.sv. Nothing
to exclude there.

## D. Signals, ports, struct fields and enum values constant in RV32I mode

### rtl/ibex_core.sv ports
- cheriot_enable_i (:67) -- tie 4'b1010.
- data_tag_o (:85) -- CONST 0 (= data_wdata_tag, rtl/ibex_load_store_unit.sv:740 <- :220).
- data_tag_i (:87) -- TB-driven; sampled only under (On) at rtl/ibex_load_store_unit.sv:672, :707 -> unobservable. Exclude only if the TB ties it.
- rf_wcap_ecc_wb_o (:100) -- CONST: {secded(0)[63:57], 35'b0} via :1257 when RegFileECC = 1 (U1/U2), 35'b0 otherwise (:1295/:1315).
- rf_rcap_a_ecc_i, rf_rcap_b_ecc_i (:101-102) -- CONST CapWordZeroVal from the RF (rtl/ibex_register_file_ff.sv:227-230).
- RVFI (`ifdef RVFI`, U5): rvfi_rs1_rcap (:149), rvfi_rs2_rcap (:151), rvfi_rd_wcap (:155), rvfi_mem_is_cap (:158), rvfi_mem_rcap (:163), rvfi_mem_wcap (:165) -- CONST NULL_CAP / 0 (:1789-1803 from :2027-2030, :2090-2099, :2162-2176 with CONST _d).

### rtl/ibex_core.sv internal cap_t / decoded_cap_t nets (all CONST)
rf_wcap_wb (:281) = NULL_CAP (rtl/ibex_wb_stage.sv:217-218); rf_rcap_a, rf_rcap_b (:284) = NULL_CAP (:286-287, G8); rf_wcap_fwd_wb (:293) = NULL_CAP (rtl/ibex_wb_stage.sv:216); rf_wcap_lsu (:296) = NULL_CAP (rtl/ibex_load_store_unit.sv:704-709); lsu_wcap (:347) = NULL_CAP (rtl/ibex_cheriot_ex.sv:959); pcc_cap_r (:430) = ROOT_DECODED_CAP_TX (rtl/ibex_cs_registers.sv:2058, :2063-2067); pcc_cap_w (:430) = NULL_DECODED_CAP (rtl/ibex_cheriot_ex.sv:287); cheriot_result_cap (:450) = NULL_CAP (rtl/ibex_cheriot_ex.sv:269); cheriot_csr_wcap (:473) = NULL_CAP (:271); cheriot_csr_rcap (:477) = NULL_CAP (rtl/ibex_cs_registers.sv:2051-2055); lsu_lc_clrperm (:482, cap_clrperm_t) = '0 (rtl/ibex_cheriot_ex.sv:957). RVFI: rvfi_stage_rs1_rcap, rvfi_stage_rs2_rcap (:1676-1677), rvfi_stage_rd_wcap (:1680), rvfi_stage_mem_rcap (:1687), rvfi_stage_mem_wcap (:1689), rvfi_stage_mem_is_cap (:1690), rvfi_rs1_cap_d/q, rvfi_rs2_cap_d/q, rvfi_rd_cap_d/q (:1707-1712), rvfi_mem_is_cap_d/q (:1728-1729), rvfi_mem_rcap_d/q, rvfi_mem_wcap_d/q (:1730-1733) -- all CONST NULL_CAP / 0.

### rtl/ibex_core.sv internal control nets (CONST unless noted)
instr_fetch_cheriot_acc_vio, instr_fetch_cheriot_bound_vio (:214-215) = 0 (G7); cheriot_enable_mubi_err (:234) = 0 (E); lsu_err_is_cheriot (:250) = 0 (G4); branch_target_ex_cheriot (:262) = 32'h0 (rtl/ibex_cheriot_ex.sv:286); cheriot_branch_req, cheriot_branch_req_spec (:432-433) = 0; instr_is_cheriot_id (:434) = 0; instr_is_rv32lsu_id (:435) TOGGLES (= lsu_req_dec, rtl/ibex_id_stage.sv:576); cheriot_exec_id (:436) = 0; cheriot_imm12/imm20/imm21 (:437-439) = 0; cheriot_cs2_dec (:440) = 5'h0; cheriot_cap_field_sel (:441) = CFIELD_PERM; cheriot_adder_a_sel (:442) = CHERIOT_ADDER_A_ZERO; cheriot_adder_b_sel (:443) = CHERIOT_ADDER_B_ZERO; cheriot_setaddr_sel (:444) = SETADDR_NONE; cheriot_setbounds_sel (:445) = SETBOUNDS_NONE; cheriot_load_id, cheriot_store_id (:446-447) = 0; cheriot_rf_we (:448) = 0; cheriot_result_data (:449) = 32'h0; cheriot_ex_valid (:451) = 0; cheriot_ex_err (:452) = 0; cheriot_ex_err_info (:453) = 12'h0; cheriot_wb_err (:454) = 0; cheriot_wb_err_info (:455) = 16'h0; cheriot_operator (:457) = '0; cheriot_csr_access (:468) = 0; cheriot_csr_addr (:470) = 5'h0; cheriot_csr_wdata (:471) = 32'h0; cheriot_csr_op (:474) = CHERIOT_CSR_NULL; cheriot_csr_op_en (:475) = 0; cheriot_csr_rdata (:476) = 32'h0; cheriot_csr_set_mie, cheriot_csr_clr_mie (:478-479) = 0; lsu_is_cap, lsu_cheriot_err (:481) = 0; csr_dbg_tclr_fault (:484) = 0; cheriot_fatal_err (:485) = 0; csr_mshwm, csr_mshwmb (:487-488) = 32'h0; csr_mshwm_set (:489) = 0; csr_mshwm_new (:490) TOGGLES (dead). Port-level view of the same at rtl/ibex_id_stage.sv:203-226, rtl/ibex_decoder.sv:92-119, rtl/ibex_controller.sv:35, :46-47, :74, :127-134, rtl/ibex_cs_registers.sv:63-73, :153-159, rtl/ibex_wb_stage.sv:31-33, :49-51, rtl/ibex_load_store_unit.sv:25, :44-52, :76, rtl/ibex_if_stage.sv:40, :90-91, :133, rtl/ibex_cheriot_ex.sv:9-119.

### rtl/ibex_register_file_ff.sv
cheriot_enable_i (:69) tie; rcap_a_o (:72), rcap_b_o (:77) = CapWordZeroVal; wcap_a_i (:83) CONST (from rf_wcap_ecc_wb_o); cheriot_enabled (:94) = 0; wshared_data[CapWidth-1:32] (:113) = 0; rf_shared[i][CapWidth-1:32] = 0.

### rtl/ibex_load_store_unit.sv
ls_fsm_cs / ls_fsm_ns (:122) never take CTX_WAIT_GNT1 / CTX_WAIT_GNT2 / CTX_WAIT_RESP (ibex_pkg.sv:817-820 ls_fsm_e; assigned only at :464, :466, :570, :586 which are UNREACH); cap_rx_fsm_q / cap_rx_fsm_d (:124) = CRX_IDLE, CRX_WAIT_RESP1 / CRX_WAIT_RESP2 (rtl/ibex_pkg.sv:822) never reached; data_wdata_tag (:101) = 0; resp_is_cap_q (:116) = 0; cheriot_err_d/q (:117) = 0; resp_lc_clrperm_q (:118) = '0; lsu_go_goodcap (:119) = 0; cpu_req_erred (:120) = 0; cap_lsw_err_q (:126) = 0; cap_lsw_data_q (:127) = 0; cap_lsw_tag_q (:128) = 0; lsu_rcap_o (:52) = NULL_CAP; lsu_err_is_cheriot_o (:76) = 0.

### rtl/ibex_controller.sv
lsu_err_is_cheriot_q (:144), cheriot_ex_err_q/d (:147), cheriot_wb_err_q (:148), cheriot_asr_err_q/d (:149), cheriot_ex_err_prio / cheriot_wb_err_prio / cheriot_asr_err_prio (:159-161), cheriot_ex_err (:197), mret_cheriot_asr_err, csr_cheriot_asr_err (:198-199) = 0; csr_mepcc_clrtag_o (:110) = 0; exc_cause_o never equals ExcCauseCheriFault (rtl/ibex_pkg.sv:378-379, lower_cause 5'd28; assigned only at :852, :856, :906, :920, :930, :940, :946, all UNREACH).

### rtl/ibex_cs_registers.sv
pcc_cap_q (:286) = ROOT_DECODED_CAP_TX = {top33 33'h1_0000_0000, base32 0, perms 12'h1eb, cap_cor 0, valid 1, rsvd 0, cperms 6'b101111, otype 0, cexp 4'd15, top 9'h100, base 0} (rtl/ibex_cheriot_pkg.sv:154-166); mepc_cap (:263), mtvec_cap (:268) = ROOT_CAP_TX; mtdc_cap = ROOT_CAP_TM, mscratchc_cap = ROOT_CAP_TS, mtdc_data = mscratchc_data = 0 (:2004-2008, :2153-2175); depc_cap (:276), dscratch0_cap, dscratch1_cap (:280) = NULL_CAP; mshwm_q, mshwmb_q, cdbg_ctrl_q = 0 (:1305-1343); cheriot_csr_rdata_o (:72) = 32'h0, cheriot_csr_rcap_o (:73) = NULL_CAP; cheriot_fatal_err_o (:159) = 0; csr_dbg_tclr_fault_o (:158) = 0; mtvec_en_cheriot, mepc_en_cheriot, depc_en_cheriot, dscratch0/1_en_cheriot, mtdc_en_cheriot, mscratchc_en_cheriot = 0. CSR_MARCHID read = CSR_MARCHID_VALUE {1'b0, 31'd22} (rtl/ibex_pkg.sv:727). misa = X1 I1 E0 (see C). CSR addresses CSR_MSHWM 12'hBC1, CSR_MSHWMB 12'hBC2, CSR_CDBG_CTRL 12'hBC4 (rtl/ibex_pkg.sv:626-628): only their illegal paths are reachable.

### rtl/ibex_decoder.sv / rtl/ibex_pkg.sv opcodes
OPCODE_CHERI = 7'h5b (rtl/ibex_pkg.sv:84), OPCODE_AUICGP = 7'h7b (:85): the case items at rtl/ibex_decoder.sv:791 and :881 ARE reached (they resolve to illegal_insn at :877-878, :892-893); only their inner CHERIoT bodies are UNREACH. Do not exclude the case items themselves.

### rtl/ibex_if_stage.sv
cheriot_acc_vio, cheriot_bound_vio (:194), cheriot_force_uc (:195), instr_fetch_cheriot_acc_vio_o, instr_fetch_cheriot_bound_vio_o (:90-91) = 0; allow_all, hdrm_ok, base_ok = 1; unused_pcc_cap (:196) CONST.

### rtl/ibex_id_stage.sv
cheriot_exec_id_o, instr_is_cheriot_id_o, cheriot_load_o, cheriot_store_o (:204-205, :217-218), cheriot_lsu_req_dec (:300), csr_cheriot_always_ok (:335), instr_is_legal_cheriot (:340) = 0; all cheriot_*_o decode ports CONST as in G1.

### rtl/ibex_wb_stage.sv
wb_is_cheriot_q, wb_cheriot_load_q, wb_cheriot_store_q, cheriot_rf_we_q (:99-101) = 0; cheriot_rf_wdata_q (:102) = 0; cheriot_rf_wcap_q (:103) = NULL_CAP; rf_wcap_fwd_wb_o, rf_wcap_wb_o = NULL_CAP.

## E. MuBi invalid-encoding alert path

- Declaration: rtl/ibex_core.sv:234 `logic cheriot_enable_mubi_err;`
- Driver (generate `gen_cheriot_enable_check`, condition `BaseIsa == BaseIsaRV32IorCHERIoT`,
  rtl/ibex_core.sv:1342-1344; else `gen_no_cheriot_enable_check` :1345-1347 assigns 1'b0,
  NOT-ELAB):
  `assign cheriot_enable_mubi_err = instr_exec & !((cheriot_enable_i == IbexMuBiOn) ||
   (cheriot_enable_i == IbexMuBiOff));`
  Comment/tag at :1339-1341: "Detect invalid MuBi encoding on cheriot_enable_i (neither On nor
  Off). Gated by instr_exec ... SEC_CM: CHERIOT_ENABLE.CTRL.MUBI".
- instr_exec: rtl/ibex_core.sv:649 `assign instr_exec = fetch_enable_i == IbexMuBiOn;` (branch
  g_instr_req_gated_secure :644-650, SecureIbex = 1).
- Consumer: rtl/ibex_core.sv:1350-1351
  `assign alert_major_internal_o = rf_ecc_err_comb | pc_mismatch_alert | csr_shadow_err |
   cheriot_fatal_err | cheriot_enable_mubi_err;`
- With cheriot_enable_i tied to IbexMuBiOff (4'b1010): `(cheriot_enable_i == IbexMuBiOff)` is
  constant 1, the negated OR is constant 0, so cheriot_enable_mubi_err = instr_exec & 1'b0 =
  CONST 0. The SEC_CM is unexercisable; alert_major_internal_o reduces to
  rf_ecc_err_comb | pc_mismatch_alert | csr_shadow_err (cheriot_fatal_err is also CONST 0, G6).
  Exclusion items: line/cond bins of :1343-1344 where the result is 1, toggle of
  cheriot_enable_mubi_err, and the two CONST-0 OR terms at :1351. Note that no ibex_core
  assertion references cheriot_enable_mubi_err (grep), so nothing else depends on it.

## F. Leaks from the dual-base-ISA build into the RV32I path with Off (NOT excludable)

F1. Register-file bank structure. x16-x31 live in the CapWidth-wide `rf_shared` bank
    (rtl/ibex_register_file_ff.sv:99, :131-141), written zero-extended via wshared_data (:113)
    and read truncated via DataWidth'(rf_shared[...]) (:221-224). x16 is a separate flop
    rf_shared_r0_q inside g_dummy_r0 (:174-183) with its own enable we_shared_r0 (:160-161);
    its read is unconditional (:183) while the dummy-x0 data read is gated by dummy_instr_id_i
    (:152). RV32I-mode features to cover: x16 write/read, x16 adjacent to dummy instructions,
    x17-x31, forwarding into/out of x16-x31. Bug-candidate surface: any mismatch between the
    two banks' enables (:120-121 vs :136-137, :159-161).
F2. rcap_r0 (rtl/ibex_register_file_ff.sv:184) carries x16 data during dummy instructions
    (rf_shared[0] is the x16 flop). Unobservable because rcap_a_o/rcap_b_o are gated (:227-230),
    but the net TOGGLES; it must be listed by name, not swept in as "CHERIoT constant".
F3. Register-file assertions CheriotWaddrMSBClear / CheriotRaddrAMSBClear /
    CheriotRaddrBMSBClear (:237-239) are vacuous in this build (antecedent cheriot_enabled = 0);
    they give no RV32I protection. Do not count them as checkers.
F4. Capability ECC (if RegFileECC = 1 in the wrapper, U1): regfile_cap_ecc_enc /
    regfile_cap_ecc_dec_a / _b exist (rtl/ibex_core.sv:1252-1276). The decoders see a constant
    codeword built from CapWordZeroVal; rf_cap_ecc_err_a/b are then a constant that is very
    likely non-zero (all-zero is not a valid inverted-SECDED word; U2) and are kept out of
    rf_ecc_err_comb ONLY by the `(cheriot_enable_i == IbexMuBiOn)` term (:1281-1286). Risk: any
    change of the tie makes alert_major_internal_o fire. Parameter hazard: rtl/ibex_top.sv:215
    hard-codes `RegFileECC = 1'b0` for the main core and passes `RegFileCapEccWidth (REGCAP_W)`
    (:400) while declaring `RegFileCapEccWidth = REGCAP_W + 7` (:219) and using that only for
    the lockstep core (:1148). With RegFileECC = 1 the wrapper must pass REGCAP_W + 7 (and give
    the RF CapWidth = 42), otherwise the part-select `rf_rcap_a_ecc_i[RegFileCapEccWidth-1:
    REGCAP_W]` at rtl/ibex_core.sv:1264/:1271 is the reversed range [34:35]. Flag to owner.
F5. CheriLimit16Regs = 1 (rtl/ibex_decoder.sv:124) adds gen_16_regs muxes (:211-217), the
    CAUICGP raddr_a mux (:202) and gen_16reg_check_active (:237-242). With Off they are
    pass-through / 0 and rf_we_o = rf_we & ~illegal_reg_16 (:1454) is pass-through: no RV32I
    decode change, but x16-x31 addressing now traverses these muxes.
F6. misa (rtl/ibex_cs_registers.sv:377-391): value X=1 I=1 E=0 -- identical to a plain RV32I +
    RV32B build, so no observable leak in THIS config. (If RV32B were None the X bit would
    differ from MISA_VALUE[23]; not applicable here.)
F7. marchid reads CSR_MARCHID_VALUE (:424-426); mtvec LSB forced to 1 (:739-743) and exc_pc
    RV32I sides (rtl/ibex_if_stage.sv:222-228) equal baseline. No leak, but extra mux terms sit
    on the reset/exception PC path.
F8. CSR write-enable gating: mepc_en (:796-797), mtvec_en (:807-808), csr_we_int (:1020-1023),
    mstatus set/clr (:1062-1069), and the AND-OR *_d_combi muxes for mepc/mtvec/depc/dscratch0/1
    (:1085-1086, :1163-1167, :1203-1204, :1220-1222, :1238-1240) all carry CHERIoT terms that
    evaluate constant in Off mode. Functionally pass-through; they are RV32I CSR-write logic
    and must stay in coverage.
F9. mtval: the CHERIoT forcing (rtl/ibex_controller.sv:866-868, :894-897, :901-926) leaves the
    RV32I sides at baseline values (instruction bits / lsu_addr_last_i). No leak.
F10. RVFI (only if RVFI is defined, U5): rvfi_id_done (rtl/ibex_core.sv:1851-1853) now
    suppresses the ID-stage trap entry whenever controller wb_exception_o is set; wb_exception_o
    also covers plain load/store errors (rtl/ibex_controller.sv:336-337), so this changes RV32I
    RVFI trap reporting when an ID exception coincides with a WB load/store error. Bug candidate
    for RVFI-based checking.
F11. instr_kill uses id_exception_nc (rtl/ibex_id_stage.sv:1033-1036) instead of
    id_exception; with Off exc_req_nc == exc_req_d (rtl/ibex_controller.sv:268-272), so no
    behaviour change, but the two ports diverge only in CHERIoT mode.
F12. RV32I LSU request path routes through u_ibex_cheriot_ex (rtl/ibex_cheriot_ex.sv:943-960,
    :970-973); lsu_addr/we/wdata/type/sign_ext/req and addr_incr are live RV32I nets inside a
    CHERIoT-named module. Also LSU-side ternaries data_offset (:131-132), data_be (:139), wdata
    (:211-220), cpu_req_valid (:407) are live. lsu_rdata_o inside gen_memcap_rd (:702-703) is the
    live RV32I load-data return.
F13. Dual-purpose flops/nets that TOGGLE in Off mode inside CHERIoT-labelled blocks (list by
    name in the exclusion as "live" or leave uncovered, never claim them as CHERIoT activity):
    rtl/ibex_cs_registers.sv mstack_epc_cap_q (:2127-2133, NULL_CAP -> ROOT_CAP_TX on first NMI
    via mstack_en :933), pcc_cap_d / tf_cap / tr_cap / tr_addr (:2071-2105), pcc_exc_cap
    (:2061), mshwm_d (:1303); rtl/ibex_core.sv csr_mshwm_new (:490) and branch_target_ex
    (:263); rtl/ibex_if_stage.sv instr_hdrm / hdrm_ge4 / hdrm_ge2 (:447-449); rtl/ibex_cheriot_ex.sv
    internal nets listed in A1; rtl/ibex_register_file_ff.sv rf_shared[*], wshared_data,
    we_shared_r0, rf_shared_r0_q, rcap_r0, we_data_r0, rf_data_r0_q.
F14. PMP gating generate blocks (rtl/ibex_core.sv:1589-1593, :1626-1630) are on the live PMP
    address/error path; keep the RV32I sides.
F15. Active invariant assertions in Off mode (keep, they are RV32I-mode checkers):
    rtl/ibex_id_stage.sv:1297-1300, rtl/ibex_load_store_unit.sv:833-834,
    rtl/ibex_cs_registers.sv:1996-1997 (ASSERT_IF with a true antecedent), and
    rtl/ibex_controller.sv:377-383 (onehot over prio bits including the three CHERIoT ones).
F16. CSR addresses 0xBC1/0xBC2/0xBC4 read or write -> illegal instruction
    (rtl/ibex_cs_registers.sv:678-698): same as baseline `default`, but the decode now has
    explicit arms; RV32I-mode testable behaviour.
F17. mshwm circular dependency: csr_mshwm_set (rtl/ibex_cheriot_ex.sv:991-993) is 0 only
    because mshwm_q resets to 0 and is never written (mshwm_en CONST 0). Not gated by
    cheriot_enable_i itself. Robust today; note for any future reset-value change.

## G. Grep-hit accounting (grep -n -i cheri rtl/<file>), every hit assigned

| File | Hits | Lines -> bucket |
|---|---|---|
| ibex_core.sv | 199 | ports/decls :17, :67, :214-215, :234, :250, :262, :286-287, :432-485 -> D; instantiation connections :551, :590-591, :677, :711-712, :777, :836-857, :1074, :1103, :1117, :1137-1139, :1157-1159, :1456, :1476-1485, :1563-1568 -> D (port wiring of CONST nets); :909-1001 -> B1/A1; :1002-1056 -> NOT-ELAB; :1244-1295 -> B2; :1315 -> NOT-ELAB; :1339-1351 -> E; :1588-1592, :1625-1630 -> B4/B5; :1850 comment -> F10; :2286-2290 -> B6 |
| ibex_decoder.sv | 151 | :17, :22, :27, :92-119, :124, :148 -> D/params; :202, :206-216, :235-238 -> B8/B9/F5; :282-303 defaults -> G1; :314-323, :339-348, :402-409, :444-455, :474-482, :777-779, :788-891 -> C UNREACH; :1067 comment; :1450-1480 -> D/NOT-ELAB |
| ibex_cs_registers.sv | 167 | :13, :41, :63-73, :153-159 -> D ports; :181-182, :357-389 -> C misa/decls; :425-426, :468-517, :677-708, :741-743, :796-808, :879-884 -> C; :1015-1021, :1058-1069, :1085-1086, :1163-1167, :1203-1240 -> F8; :1304, :1331 -> B13; :1995-1997 -> F15; :2000-2228 -> B14; :2230-2260 -> NOT-ELAB/unused |
| ibex_controller.sv | 123 | :22, :35, :46-47, :74, :77, :127-134, :144-161, :197-199 -> D; :234-276 -> C/B10; :307-382 -> C; :682 -> C; :828-946 -> C; :1054-1075 -> B11/NOT-ELAB; :1125-1130 unused sink |
| ibex_id_stage.sv | 88 | :21, :30, :35, :68-69, :146, :203-226, :300, :335, :340 -> D; :488, :548-573, :623-668, :719-726 -> port wiring; :578-582, :746-748, :901-905, :1012, :1030-1035, :1064-1071, :1093-1096 -> C; :1144-1160, :1199-1200 -> NOT-ELAB; :1295-1300 -> F15 |
| ibex_wb_stage.sv | 49 | :18, :31-33, :49-51, :99-103 -> D; :113-116, :137-142, :152-157, :171-176, :182-183, :190-196, :215-218 -> C; :251-255, :279, :286 -> NOT-ELAB |
| ibex_load_store_unit.sv | 40 | :18, :25, :45, :76, :117 -> D; :131-139, :211-222, :407-408, :419, :435-471, :566-616, :644-654, :669-693, :701-707, :760 -> C/B12; :832-834 -> F15 |
| ibex_if_stage.sv | 34 | :17, :40, :90-91, :194-197, :205 -> D; :207-209 -> NOT-ELAB; :222-226, :368, :430, :455-469, :495 -> C; :634-655 -> B7 |
| ibex_compressed_decoder.sv | 24 | :20, :27 -> param/port; :230-233, :249-250, :329-330, :359-360, :391-394, :411-412, :557-558, :575, :615-617, :854 -> C UNREACH; :911-913 -> NOT-ELAB |
| ibex_register_file_ff.sv | 41 | :21-46 header comments; :58, :69 -> D; :88-239 -> B15/F1-F3; :324-325 -> NOT-ELAB |
| ibex_prefetch_buffer.sv | 2 | :30, :104 -> C |
| ibex_fetch_fifo.sv | 4 | :32-33, :120, :127 -> C |
| ibex_cheriot_ex.sv | 284 | all -> A1 |
| ibex_cheriot_pkg.sv | 97 | all -> A2 |
| ibex_pkg.sv | 4 | :38 base_isa_e, :84 OPCODE_CHERI, :378 ExcCauseCheriFault, :728 CSR_MARCHID_CHERIOT_VALUE -> D |
| ibex_trvk.sv | 7 | -> A3 (outside DUT) |

## H. Rough line counts for sizing the exclusion

- A (whole files): ibex_cheriot_ex.sv 1031 + ibex_cheriot_pkg.sv 965 = 1996 lines (ibex_trvk.sv
  420 lines outside the DUT). Of ibex_cheriot_ex.sv roughly 60 lines are live RV32I pass-through
  or toggling logic (A1 list) and must be carved out.
- B (generate blocks): core 91 + 47 + 3 + 5 + 5 + 10 = 161; if_stage 19; decoder 13; controller
  19; lsu 9; cs_registers 42 + 226 = 268; register_file_ff 152. Total about 640, of which about
  200 (register file body, g_cheriot_ex mux, gen_memcap_rd rdata, PMP gates, SCR pcc_cap_d
  logic) contain live RV32I or toggling logic.
- C (arms/terms): core ~25, if_stage ~15, id_stage ~20, decoder ~110 (OPCODE_CHERI body alone
  85), compressed_decoder ~35, controller ~70, lsu ~90, wb_stage ~30, cs_registers ~60,
  register_file ~10, prefetch/fifo 3: about 470 lines.
- D (constant nets): about 120 declarations / ports plus 3 FSM enum values (CTX_*), 2 (CRX_*),
  1 exception cause, 3 CSR addresses, 1 marchid constant.
- E: 3 lines + 2 OR terms.
- Total excludable candidate: about 3100 lines including bucket A; live/leak (F) content that
  must NOT be excluded: about 250-300 lines spread over the same files.

## I. Unverified items

U1. Wrapper parameters were not readable (dv/** fence): RegFileECC (task says 1; rtl/ibex_top.sv
    :215 hard-codes 1'b0 for the main core), RegFileCapEccWidth (ibex_top passes REGCAP_W at :400
    but declares REGCAP_W + 7 at :219), the RF instance's CapWidth / CapWordZeroVal (ibex_top
    leaves both at defaults: 35 / '0, :533-539), ResetAll (selects B7 / wb_stage flop branch),
    and whether RVFI is defined. B2/F4 and every "CapWordZeroVal = 0" statement depend on these.
U2. Constant value of rf_cap_ecc_err_a/b on the all-zero codeword (prim_secded_inv_64_57_dec
    under vendor/lowrisc_ip/ip/prim not read). Masked regardless (rtl/ibex_core.sv:1281-1286).
U3. rtl/ibex_cheriot_ex.sv:755-865 (check_cheriot body) was not read line by line; outputs are
    gated at :869-870, internal nets assumed toggling.
U4. Whether DII_SIM is defined (selects rtl/ibex_fetch_fifo.sv:120 vs :127).
U5. RVFI items (bucket C/D RVFI lines, B6, F10) apply only if RVFI is defined for the DUT.
U6. ibex_trvk.sv is outside ibex_core; if the wrapper instantiates it separately it needs its
    own inventory.
