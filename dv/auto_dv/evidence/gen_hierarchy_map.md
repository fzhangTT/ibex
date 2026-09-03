# ibex_core hierarchy map, FSM inventory and cross-module control paths (opentitan configuration)

Owner: rtl-arch (T-003). This file folds two subagent analyses (subagent/hierarchy_A1.md and
subagent/fsm_paths_A2.md) under an rtl-arch verification layer. Part A below is rtl-arch's own
verified summary; Parts B and C are the subagent bodies, whose instantiation lines, generate
conditions and FSM state lists rtl-arch spot-checked against the RTL (checks listed in A.4).
Build configuration: opentitan; DUT = ibex_core + ibex_register_file_ff; cheriot_enable_i tied
IbexMuBiOff. Parameter values: gen_param_resolution.md.

## Part A. rtl-arch verified summary

### A.1 Elaborated instance tree (instantiation lines verified by grep of rtl/*.sv)

```
gen_dut_top (wrapper, TB Infra)
+- ibex_core                                          rtl/ibex_core.sv:17
|  +- g_core_busy_secure.u_fetch_enable_buf            prim_buf #(12)                 ibex_core.sv:504
|  +- if_stage_i                                       ibex_if_stage                  ibex_core.sv:528
|  |  +- g_mem_ecc.u_prim_buf_instr_rdata              prim_buf #(39)                 ibex_if_stage.sv:263
|  |  +- g_mem_ecc.u_instr_intg_dec                    prim_secded_inv_39_32_dec      ibex_if_stage.sv:268
|  |  +- gen_icache.icache_i                           ibex_icache                    ibex_if_stage.sv:300
|  |  |  +- gen_ecc_wdata.tag_ecc_enc                  prim_secded_inv_28_22_enc      ibex_icache.sv:297
|  |  |  +- gen_ecc_wdata.gen_ecc_banks[0..1].data_ecc_enc   prim_secded_inv_39_32_enc  ibex_icache.sv:306
|  |  |  +- gen_data_ecc_checking.gen_tag_ecc[0..1].data_ecc_dec  prim_secded_inv_28_22_dec ibex_icache.sv:556
|  |  |  +- gen_data_ecc_checking.gen_ecc_banks[0..1].data_ecc_dec prim_secded_inv_39_32_dec ibex_icache.sv:568
|  |  +- compressed_decoder_i                          ibex_compressed_decoder        ibex_if_stage.sv:485
|  |  +- gen_dummy_instr.dummy_instr_i                 ibex_dummy_instr               ibex_if_stage.sv:509
|  |  |  +- lfsr_i                                     prim_lfsr #(32, out 17)        ibex_dummy_instr.sv:76
|  |  +- g_secure_pc.u_prev_instr_addr_incr_buf        prim_buf #(32)                 ibex_if_stage.sv:682
|  +- id_stage_i                                       ibex_id_stage                  ibex_core.sv:663
|  |  +- decoder_i                                     ibex_decoder                   ibex_id_stage.sv:478
|  |  +- controller_i                                  ibex_controller                ibex_id_stage.sv:615
|  +- ex_block_i                                       ibex_ex_block                  ibex_core.sv:863
|  |  +- alu_i                                         ibex_alu                       ibex_ex_block.sv:116
|  |  +- gen_multdiv_fast.multdiv_i                    ibex_multdiv_fast (single-cycle variant) ibex_ex_block.sv:166
|  +- g_cheriot_ex.u_ibex_cheriot_ex                   ibex_cheriot_ex (ELABORATES; RV32I LSU path routed through it) ibex_core.sv:912
|  +- load_store_unit_i                                ibex_load_store_unit           ibex_core.sv:1066
|  |  +- g_mem_rdata_ecc.u_prim_buf_instr_rdata        prim_buf #(39)                 ibex_load_store_unit.sv:380
|  |  +- g_mem_rdata_ecc.u_data_intg_dec               prim_secded_inv_39_32_dec      ibex_load_store_unit.sv:385
|  |  +- g_mem_wdata_ecc.u_data_gen                    prim_secded_inv_39_32_enc      ibex_load_store_unit.sv:732
|  +- wb_stage_i                                       ibex_wb_stage                  ibex_core.sv:1125
|  +- cs_registers_i                                   ibex_cs_registers              ibex_core.sv:1431
|  |  +- 56 x ibex_csr (14 named CSRs, 3 CHERIoT mshwm/mshwmb/cdbg_ctrl, 16 pmpcfg, 16 pmpaddr, mseccfg, mcounteren, tselect, tdata1, tdata2, ic_scr_key_valid, cpuctrlsts)   ibex_cs_registers.sv:1072-1977
|  |  +- 12 x ibex_counter (mcycle 64b, minstret 64b, mhpmcounter3..12 32b)              ibex_cs_registers.sv:1622-1676
|  +- g_pmp.pmp_i                                      ibex_pmp #(3 channels, 16 regions) ibex_core.sv:1606
|  +- (RegFileECC=1 only) gen_regfile_ecc: prim_secded_inv_39_32_enc/dec x3, gen_cheriot_cap_ecc prim_secded_inv_64_57_enc/dec x3   ibex_core.sv:1221-1276
+- ibex_register_file_ff (g_cheriot_rf branch)         rtl/ibex_register_file_ff.sv:51
```

Not elaborated under this configuration (present in the file set): ibex_prefetch_buffer and
ibex_fetch_fifo (ICache = 1), ibex_branch_predict (BranchPredictor = 0), ibex_multdiv_slow
(RV32MSingleCycle), the fast-multiplier generate branch of ibex_multdiv_fast, gen_regfile_ecc
(if RegFileECC = 0), prim_clock_gating (dependency only), g_plain_rf of the register file.

Tool note: mcp siliconpilot hierarchy_resolve on the RTL file set with default parameters returned
22 modules with gen_prefetch_buffer, gen_multdiv_fast and no icache/pmp/cheriot_ex/dummy_instr
(default BaseIsa=RV32I, ICache=0, PMPEnable=0, DummyInstructions=0). It confirms the static
instance names above but is not authoritative for generate selection; the tree above was built
from the generate conditions and the -pvalue/derived values. siliconpilot fsm_extract (regex
backend) found 0 FSMs in ibex_controller and ibex_load_store_unit: the enums are declared in
ibex_pkg, not locally, so the regex misses them. Whether VCS infers FSMs for URG is unknown until
the first coverage run (DV_prompt Section 4 "not applicable" rule).

### A.2 FSM inventory (counts)

8 real enum FSMs elaborated: controller ctrl_fsm_e (10 states, rtl/ibex_pkg.sv:291-302,
rtl/ibex_controller.sv:137, :539-1000), LSU ls_fsm_e (8 states of which 3 CHERIoT-only never
entered, rtl/ibex_pkg.sv:816-820, rtl/ibex_load_store_unit.sv:411-609), LSU cap_rx_fsm_t (3 states,
frozen in CRX_IDLE, rtl/ibex_load_store_unit.sv:611-626), ID id_fsm_e (2, rtl/ibex_id_stage.sv:861-973),
divider md_fsm_e (7, rtl/ibex_multdiv_fast.sv:90-93, :412-526), single-cycle multiplier mult_fsm_e
(2, :142-251), icache inval_state_e (4, rtl/ibex_icache.sv:193-200, :1208-1278), Zcmp cm_state_e
(8, rtl/ibex_compressed_decoder.sv:181-196, :624-889). 6 pseudo-FSMs (bit-vector or flag state):
icache fill buffers (4 x lifecycle), icache skid buffer, dummy-instruction counter/LFSR, controller
debug_mode_q/nmi_mode_q, WB wb_valid_q, double-fault detector. 2 enum FSMs in the file set are not
elaborated (ibex_multdiv_slow md_fsm_e, ibex_multdiv_fast gen_mult_fast). Transition audit
(Part C section 1): 43 unreachable arcs in this DUT (all with a cited reason: CHERIoT tie,
BranchPredictor=0, BranchTargetALU=1, WritebackStage=1, default arms), 57 reachable-but-hard arcs
each with a stimulus hint. The controller FSM is documented only by name
(instruction_decode_execute.rst:24-35); no doc describes any transition.

### A.3 Cross-module control paths (index; bodies in Part C section 2)

P1 ID-stage stall sources; P2 flushes (FLUSH state, instr_valid_clear, pc_set); P3 bubbles;
P4 exception entry per cause; P5 interrupt entry (external, timer, sw, fast, NMI, internal NMI);
P6 debug entry/exit; P7 PMP faults fetch vs data; P8 multdiv multi-cycle; P9 misaligned split and
second-half errors; P10 writeback-stage interactions; P11 icache fill/invalidate/scramble key;
P12 dummy instruction insertion; P13 fetch_enable gating and WFI sleep/wake.

### A.4 rtl-arch spot checks performed on the subagent material

Verified by reading the cited lines: ibex_top parameter derivation (rtl/ibex_top.sv:212-233,
:369-410); every ibex_core-level instantiation line (grep); the LSU FSM transitions (whole file
read); the controller mtval/exception priority block (rtl/ibex_controller.sv:847-870); the
icache inval FSM and external request logic (rtl/ibex_icache.sv:1028-1040, :1208-1270, :1304);
if_stage icache instantiation and integrity decode (rtl/ibex_if_stage.sv:259-347); PMP debug
bypass (rtl/ibex_pmp.sv:239-240); dv_fcov_macros.svh macro bodies (:60-110). Not re-verified:
the per-module port transcriptions in Part B section 4 (taken from the module headers by the
subagent), the hand-counted instance totals, and the SVA line counts in Part B section 7.

### A.5 prim_* modules inside the DUT hierarchy (count for coverage)

prim_buf x4 (vendor/lowrisc_ip/ip/prim_generic/rtl/prim_buf.sv; combinational pass-through),
prim_secded_inv_39_32_enc x3 and _dec x4, prim_secded_inv_28_22_enc x1 and _dec x2 (all
combinational), prim_lfsr x1 (the only sequential prim; 32-bit Galois LFSR with state
permutation, vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv). With RegFileECC = 1 add
prim_secded_inv_39_32_enc x1, _dec x2, prim_secded_inv_64_57_enc x1, _dec x2. Include files:
prim_assert.sv (vendor/lowrisc_ip/ip/prim/rtl/) and dv_fcov_macros.svh
(vendor/lowrisc_ip/dv/sv/dv_utils/; DV_FCOV_SIGNAL creates fcov_* nets unless DV_FCOV_DISABLE,
:88-96). Packages: ibex_pkg, ibex_cheriot_pkg, prim_secded_pkg, prim_cipher_pkg (parse-only
dependency of prim_lfsr).

## Part B. Hierarchy detail (subagent A1 body, sections 2-8)

## 2. Elaborated hierarchy (module types and instance paths)

```
ibex_core                                            rtl/ibex_core.sv:17
+- g_core_busy_secure.u_fetch_enable_buf             prim_buf #(Width=12)                 ibex_core.sv:504-509
+- if_stage_i                                        ibex_if_stage                        ibex_core.sv:528-547
|  +- g_mem_ecc.u_prim_buf_instr_rdata               prim_buf #(Width=39)                 ibex_if_stage.sv:263
|  +- g_mem_ecc.u_instr_intg_dec                     prim_secded_inv_39_32_dec            ibex_if_stage.sv:268
|  +- gen_icache.icache_i                            ibex_icache                          ibex_if_stage.sv:300-307
|  |  +- gen_ecc_wdata.tag_ecc_enc                   prim_secded_inv_28_22_enc            ibex_icache.sv:297
|  |  +- gen_ecc_wdata.gen_ecc_banks[0..1].data_ecc_enc   prim_secded_inv_39_32_enc       ibex_icache.sv:305-306
|  |  +- gen_data_ecc_checking.gen_tag_ecc[0..1].data_ecc_dec   prim_secded_inv_28_22_dec  ibex_icache.sv:547-556
|  |  +- gen_data_ecc_checking.gen_ecc_banks[0..1].data_ecc_dec prim_secded_inv_39_32_dec  ibex_icache.sv:567-568
|  +- compressed_decoder_i                           ibex_compressed_decoder              ibex_if_stage.sv:485-489
|  +- gen_dummy_instr.dummy_instr_i                  ibex_dummy_instr                     ibex_if_stage.sv:509-512
|  |  +- lfsr_i                                      prim_lfsr #(LfsrDw=32,StateOutDw=17,...) ibex_dummy_instr.sv:76-82
|  +- g_secure_pc.u_prev_instr_addr_incr_buf         prim_buf #(Width=32)                 ibex_if_stage.sv:682
+- id_stage_i                                        ibex_id_stage                        ibex_core.sv:663-673
|  +- decoder_i                                      ibex_decoder                         ibex_id_stage.sv:478-484
|  +- controller_i                                   ibex_controller                      ibex_id_stage.sv:615-620
+- ex_block_i                                        ibex_ex_block                        ibex_core.sv:863-867
|  +- alu_i                                          ibex_alu #(RV32B=RV32BOTEarlGrey)    ibex_ex_block.sv:116-118
|  +- gen_multdiv_fast.multdiv_i                     ibex_multdiv_fast #(RV32M=RV32MSingleCycle) ibex_ex_block.sv:165-168
+- g_cheriot_ex.u_ibex_cheriot_ex                    ibex_cheriot_ex #(WritebackStage=1)  ibex_core.sv:911-914
+- load_store_unit_i                                 ibex_load_store_unit                 ibex_core.sv:1066-1070
|  +- g_mem_rdata_ecc.u_prim_buf_instr_rdata         prim_buf #(Width=39)                 ibex_load_store_unit.sv:380
|  +- g_mem_rdata_ecc.u_data_intg_dec                prim_secded_inv_39_32_dec            ibex_load_store_unit.sv:385
|  +- g_mem_wdata_ecc.u_data_gen                     prim_secded_inv_39_32_enc            ibex_load_store_unit.sv:732
+- wb_stage_i                                        ibex_wb_stage                        ibex_core.sv:1125-1129
+- cs_registers_i                                    ibex_cs_registers                    ibex_core.sv:1431-1452
|  +- u_mstatus_csr, u_mepc_csr, u_mie_csr, u_mscratch_csr, u_mcause_csr, u_mtval_csr, u_mtvec_csr,
|  |  u_dcsr_csr, u_depc_csr, u_dscratch0_csr, u_dscratch1_csr, u_mstack_csr, u_mstack_epc_csr,
|  |  u_mstack_cause_csr                             ibex_csr (14)                        ibex_cs_registers.sv:1072-1290
|  +- g_mshwm.u_mshwm_csr, .u_mshwmb_csr, .u_cdbg_ctrl_csr   ibex_csr (3)                 ibex_cs_registers.sv:1304-1336
|  +- g_pmp_registers.g_pmp_csrs[0..15].u_pmp_cfg_csr        ibex_csr (16)                ibex_cs_registers.sv:1419-1452
|  +- g_pmp_registers.g_pmp_csrs[0..15].u_pmp_addr_csr       ibex_csr (16)                ibex_cs_registers.sv:1483-1487
|  +- g_pmp_registers.u_pmp_mseccfg                  ibex_csr (1)                         ibex_cs_registers.sv:1516-1520
|  +- mcycle_counter_i                               ibex_counter #(CounterWidth=64)      ibex_cs_registers.sv:1622-1624
|  +- minstret_counter_i                             ibex_counter #(64, ProvideValUpd=1)  ibex_cs_registers.sv:1637-1640
|  +- gen_cntrs[0..9].gen_imp.mcounters_variable_i   ibex_counter #(32, ProvideValUpd=(Cnt==10)) ibex_cs_registers.sv:1667-1676
|  +- u_mcounteren_csr                               ibex_csr #(Width=13)                 ibex_cs_registers.sv:1737-1741
|  +- gen_trigger_regs.u_tselect_csr                 ibex_csr #(Width=1)                  ibex_cs_registers.sv:1793-1797
|  +- gen_trigger_regs.g_dbg_tmatch_reg[0].u_tmatch_control_csr  ibex_csr #(Width=1)      ibex_cs_registers.sv:1806-1811
|  +- gen_trigger_regs.g_dbg_tmatch_reg[0].u_tmatch_value_csr    ibex_csr #(Width=32)     ibex_cs_registers.sv:1806,1820-1824
|  +- gen_icache_enable.u_cpuctrlsts_ic_scr_key_valid_q_csr      ibex_csr #(Width=1)      ibex_cs_registers.sv:1935-1942
|  +- u_cpuctrlsts_part_csr                          ibex_csr                             ibex_cs_registers.sv:1973-1977
+- g_pmp.pmp_i                                       ibex_pmp #(PMPNumChan=3,PMPNumRegions=16) ibex_core.sv:1580,1606-1612

(wrapper sibling, mirrors ibex_top.sv:532-540)
register_file_i                                      ibex_register_file_ff                rtl/ibex_register_file_ff.sv:51
```

Instance totals (hand-counted): ibex_csr x 56 (14 + 3 + 16 + 16 + 1 + 1 + 3 + 1 + 1); ibex_counter
x 12; prim_buf x 4; prim_secded_inv_39_32_enc x 3 (2 icache + 1 LSU); prim_secded_inv_39_32_dec x 4
(1 IF + 1 LSU + 2 icache); prim_secded_inv_28_22_enc x 1; prim_secded_inv_28_22_dec x 2;
prim_lfsr x 1. Distinct module types inside ibex_core: 24 (19 ibex_* + 5 prim_*); plus
ibex_register_file_ff beside it = 25.

Packages that must be compiled: ibex_pkg (rtl/ibex_pkg.sv), ibex_cheriot_pkg
(rtl/ibex_cheriot_pkg.sv), prim_secded_pkg (vendor/lowrisc_ip/ip/prim/rtl/prim_secded_pkg.sv,
listed first in prim_secded.core:11; used by the wrapper for WordZeroVal per ibex_top.sv:539),
prim_cipher_pkg (vendor/lowrisc_ip/ip/prim/rtl/prim_cipher_pkg.sv, dependency of prim_lfsr.core:12,
referenced only inside the non-elaborated gen_out_non_linear branch at prim_lfsr.sv:461 but the
package must exist for the file to compile). prim_mubi_pkg / prim_mubi* and prim_util_pkg are
dependencies of ibex_core.core:14 (lowrisc:prim:mubi) but no RTL file in the DUT hierarchy
references any prim_mubi* module or prim_util_pkg (grep of rtl/*.sv: prim_util_pkg appears only in
rtl/ibex_lockstep.sv:138, not part of the DUT).

## 3. Generate branches: elaborated vs not elaborated under this configuration

Notation: E = elaborates, N = does not elaborate. Condition is quoted from the RTL.

### ibex_core (rtl/ibex_core.sv)
| Branch | Line | Condition | E/N |
|---|---|---|---|
| g_core_busy_secure (contains prim_buf u_fetch_enable_buf, g_core_busy_bits[0..3].g_pos/g_neg) | 498-518 | SecureIbex | E |
| g_core_busy_non_secure | 519 | !SecureIbex | N |
| g_instr_req_gated_secure | 644 | SecureIbex | E |
| g_instr_req_gated_non_secure | 650 | !SecureIbex | N |
| g_cheriot_ex (ibex_cheriot_ex) | 911 | BaseIsa == BaseIsaRV32IorCHERIoT | E |
| gen_no_cheriot_ex | 1002 | else | N |
| g_check_mem_response | 1181 | SecureIbex | E |
| g_no_check_mem_response | 1187 | !SecureIbex | N |
| gen_regfile_ecc (prim_secded_inv_39_32_enc/dec x3, gen_cheriot_cap_ecc with prim_secded_inv_64_57_enc/dec x3) | 1214-1304 | RegFileECC | N (RegFileECC = 0, ibex_top.sv:215) |
| gen_no_regfile_ecc | 1305 | !RegFileECC | E |
| gen_cheriot_enable_check | 1342 | BaseIsa == CHERIoT | E |
| gen_no_cheriot_enable_check | 1345 | else | N |
| gen_wb_stage (INC_ASSERT only) | 1369 | WritebackStage | E |
| gen_no_wb_stage | 1381 | !WritebackStage | N |
| g_pmp (ibex_pmp), g_pmp_addr_gate, g_pmp_cheriot_gate | 1580, 1589, 1626 | PMPEnable; BaseIsa == CHERIoT | E |
| g_pmp_addr_no_gate, g_pmp_no_cheriot_gate | 1594, 1631 | else | N |
| g_no_pmp | 1636 | !PMPEnable | N |
| gen_rvfi_wb_stage / g_rvfi_stages / g_rvfi_cap / g_rvfi_rf_wr_suppress_wb | 1855, 2006, 2286, 2379 | `ifdef RVFI; WritebackStage; CHERIoT | E only if RVFI defined |
| gen_rvfi_no_wb_stage, g_rvfi_cap_tieoff, g_rvfi_no_rf_wr_suppress_wb | 1891, 2296, 2396 | else | N |
| g_pmp_fcov_signals / g_pmp_region_fcov[0..15] / g_region_priority / g_region_highest_priority | 2462-2510 | `ifndef SYNTHESIS && PMPEnable | E (simulation) |

### ibex_if_stage (rtl/ibex_if_stage.sv)
| Branch | Line | Condition | E/N |
|---|---|---|---|
| gen_no_cheriot_if | 207 | BaseIsa != CHERIoT | N |
| g_mem_ecc (prim_buf, prim_secded_inv_39_32_dec) | 259 | MemECC | E |
| g_no_mem_ecc | 277 | !MemECC | N |
| gen_icache (ibex_icache icache_i) | 298 | ICache | E |
| gen_prefetch_buffer (ibex_prefetch_buffer, which contains ibex_fetch_fifo) | 348 | !ICache | N |
| gen_dummy_instr (ibex_dummy_instr) | 504 | DummyInstructions | E |
| gen_no_dummy_instr | 546 | else | N |
| g_instr_rdata_ra | 589 | ResetAll | E |
| g_instr_rdata_nr | 616 | !ResetAll | N |
| gen_cheriot_vio_regs.g_cheriot_vio_ra | 634-635 | BaseIsa == CHERIoT && ResetAll | E |
| gen_cheriot_vio_regs.g_cheriot_vio_nr / gen_cheriot_vio_tieoff | 645, 653 | | N |
| g_secure_pc (prim_buf u_prev_instr_addr_incr_buf) | 659 | PCIncrCheck | E |
| g_no_secure_pc | 690 | !PCIncrCheck | N |
| g_branch_predictor (ibex_branch_predict, skid buffer, g_bp_taken_ra/nr, g_instr_skid_ra/nr) | 694-798 | BranchPredictor | N |
| g_no_branch_predictor | 799 | !BranchPredictor | E |
| g_branch_predictor_asserts | 831 | BranchPredictor | N |
| g_no_branch_predictor_asserts | 921 | !BranchPredictor | E |

### ibex_icache (rtl/ibex_icache.sv)
| Branch | Line | Condition | E/N |
|---|---|---|---|
| g_prefetch_addr_ra, g_lookup_addr_ra, g_lookup_ind_ra, g_ecc_correction_ra, g_fill_addr_ra, g_fill_data_ra, g_skid_data_ra, g_output_addr_ra, g_inval_index_ra | 226, 474, 604, 621, 916, 966, 1075, 1149, 1282 | ResetAll | E |
| all matching *_nr branches | 234, 484, 612, 631, 924, 974, 1085, 1157, 1290 | !ResetAll | N |
| gen_ecc_wdata (prim_secded_inv_28_22_enc, gen_ecc_banks[0..1] prim_secded_inv_39_32_enc) | 286-310 | ICacheECC | E |
| gen_noecc_wdata | 312 | !ICacheECC | N |
| gen_tweak_infection, gen_ecc_tweak, gen_ecc_tweak_ic1, gen_ecc_tag_tweak, gen_ecc_tag_tweak_ic1, gen_tag_untweak[0..1] | 321, 342, 371, 389, 417, 454 | TweakInfection (=ICacheTweakInfection=1); ICacheECC | E |
| gen_no_ecc_tweak, gen_no_ecc_tweak_ic1, gen_no_ecc_tag_tweak, gen_no_ecc_tag_tweak_ic1, gen_no_tweak_infection | 350, 379, 397, 425, 433 | | N |
| gen_tag_match[0..1], gen_lowest_way[1] | 498, 521 | always (IC_NUM_WAYS=2) | E |
| gen_data_ecc_checking (gen_tag_ecc[0..1] prim_secded_inv_28_22_dec, gen_ecc_banks[0..1] prim_secded_inv_39_32_dec) | 538-573 | ICacheECC | E |
| gen_no_data_ecc | 645 | !ICacheECC | N |
| gen_caching_logic | 659 | BranchCache (default 0, not overridden at ibex_if_stage.sv:300-306) | N |
| gen_cache_all | 680 | !BranchCache | E |
| gen_fbs[0..3] (gen_fb_zero, gen_fb_rest) | 707-716 | always (NUM_FB = 4, :72) | E |
| gen_data_buf[0..1] | 945 | always (IC_LINE_BEATS) | E |

### ibex_compressed_decoder (rtl/ibex_compressed_decoder.sv)
| Branch | Line | Condition | E/N |
|---|---|---|---|
| gen_unused_valid | 34 | !(RV32ZC == ZcaZcbZcmp or ZcaZcmp) | N |
| gen_gets_expanded (first) | 202 | RV32ZC == ZcaZcbZcmp or ZcaZcmp | E |
| gen_gets_expanded (else, same label) | 204 | else | N |
| g_cm_meta_ra | 893 | ResetAll | E |
| g_cm_meta_nr | 903 | !ResetAll | N |
| gen_no_cheriot_cdec | 911 | BaseIsa != CHERIoT | N |

### ibex_dummy_instr / prim_lfsr
ibex_dummy_instr has no generate blocks. prim_lfsr (vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv)
with the parameters at rtl/ibex_dummy_instr.sv:76-81 (LfsrType default "GAL_XOR", CustomCoeffs
default 0, StatePermEn=1, NonLinearOut default 0): gen_gal_xor (:283) E, gen_gal_xor.gen_lut (:288) E,
gen_gal_xor.gen_custom (:286) N, gen_fib_xnor (:308) N, gen_unknown_type (:333) N,
gen_out_non_linear (:351) N, gen_out_passthru (:463) E, gen_state_perm (:468) E with
gen_perm_loop[0..16] and gen_tieoff_unused (:476, LfsrDw 32 > StateOutDw 17) E, gen_no_state_perm
(:481) N; SVA-only: gen_output_sva (:572) N (StatePermEn set), gen_ext_seed_sva (:580) E,
gen_lockup_mechanism_sva (:590) E, gen_max_len_sva (:600) E (MaxLenSVA default 1), gen_perm_check
(:549) E. The `ifdef SIMULATION / `ifndef VERILATOR block at :250-273 randomizes DefaultSeedLocal
30/70 via plusarg prim_lfsr_use_default_seed when SIMULATION is defined.

### ibex_id_stage (rtl/ibex_id_stage.sv)
| Branch | Line | Condition | E/N |
|---|---|---|---|
| g_btalu_muxes | 369 | BranchTargetALU | E |
| g_nobtalu | 407 | !BranchTargetALU | N |
| gen_intermediate_val_reg[0..1] | 446 | always | E |
| g_branch_set_direct | 767 | BranchTargetALU && !DataIndTiming | N (DataIndTiming = 1) |
| g_branch_set_flop | 771 | else | E |
| g_sec_branch_taken | 819 | DataIndTiming | E |
| g_nosec_branch_taken | 833 | !DataIndTiming | N |
| g_calc_nt_addr | 851 | BranchPredictor | N |
| g_n_calc_nt_addr | 853 | !BranchPredictor | E |
| gen_stall_mem | 1000 | WritebackStage | E |
| gen_no_stall_mem | 1142 | !WritebackStage | N |

### ibex_decoder (rtl/ibex_decoder.sv)
gen_rs3_flop (:172, RV32B != RV32BNone) E; gen_no_rs3_flop (:181) N; gen_16_regs (:211,
CheriLimit16Regs = (BaseIsa == CHERIoT) per :124) E; gen_regs (:218) N; gen_16reg_check_active
(:237, RV32E || CheriLimit16Regs) E; gen_16reg_check_inactive (:243) N; gen_no_cheriot_decoder
(:1478, BaseIsa != CHERIoT) N.

### ibex_controller (rtl/ibex_controller.sv)
g_cheriot_asr_err (:236) E, g_no_cheriot_asr_err (:241) N; g_wb_exceptions (:299, WritebackStage)
E, g_no_wb_exceptions (:338) N; g_intg_irq_int (:393, MemECC) E, g_no_intg_irq_int (:439) N;
g_writeback_mepc_save (:833) E, g_no_writeback_mepc_save (:841) N; gen_update_regs_cheriot (:1054)
E, gen_cheriot_tieoff (:1068) N.

### ibex_ex_block (rtl/ibex_ex_block.sv)
gen_multdiv_m (:76, RV32M != None) E, gen_multdiv_no_m (:78) N; g_branch_target_alu (:94) E,
g_no_branch_target_alu (:102) N; gen_multdiv_slow (:140, ibex_multdiv_slow) N; gen_multdiv_fast
(:165, RV32M == Fast || SingleCycle) E; gen_multdiv_sva_idle_slow (:204) N, gen_multdiv_sva_idle_fast
(:206) E, gen_multdiv_sva_idle_none (:208) N (all three under `ifdef INC_ASSERT at :199).

### ibex_alu (rtl/ibex_alu.sv)
g_alu_rvb (:412, RV32B != None) E; gen_alu_rvb_otearlgrey_full (:648, RV32B == OTEarlGrey || Full)
E incl. gen_shuffle_mask_not, gen_sel_vld_n/b/h, gen_xperm_n, gen_rev_operand_b, gen_clmul_* loops
(:665-973); gen_alu_rvb_not_otearlgrey_full (:986) N; gen_alu_rvb_full (:996, RV32B == Full) N
(bitcnt/butterfly loops :1054-1134 N); gen_alu_rvb_not_full (:1188) E; g_no_alu_rvb (:1290) N;
gen_rev_operand_a (:40), gen_rev_bfp_mask (:270) always E.

### ibex_multdiv_fast (rtl/ibex_multdiv_fast.sv)
gen_mult_single_cycle (:140, RV32M == RV32MSingleCycle) E; gen_mult_fast (:264) N.

### ibex_cheriot_ex (rtl/ibex_cheriot_ex.sv)
gen_err_wb_stage (:256, WritebackStage) E, gen_err_no_wb_stage (:258) N; gen_lsu_req_wb_stage
(:566) E, gen_lsu_req_no_wb_stage (:573) N.

### ibex_load_store_unit (rtl/ibex_load_store_unit.sv)
g_mem_rdata_ecc (:376, MemECC; prim_buf + prim_secded_inv_39_32_dec) E; g_no_mem_data_ecc (:394) N;
gen_memcap_rd (:701, BaseIsa == CHERIoT) E; gen_no_cap_rd (:710) N; g_mem_wdata_ecc (:731, MemECC;
prim_secded_inv_39_32_enc) E; g_no_mem_wdata_ecc (:736) N. `ifndef DV_FCOV_DISABLE block
(:767-800) elaborates unless DV_FCOV_DISABLE is defined.

### ibex_wb_stage (rtl/ibex_wb_stage.sv)
g_writeback_stage (:84, WritebackStage) E; g_wb_regs_ra (:126, ResetAll) E, g_wb_regs_nr (:160) N;
g_dummy_instr_wb (:222, DummyInstructions) E with g_dummy_instr_wb_regs_ra (:225) E and
g_dummy_instr_wb_regs_nr (:233) N; g_no_dummy_instr_wb (:242) N; g_bypass_wb (:248) N.

### ibex_cs_registers (rtl/ibex_cs_registers.sv)
g_mshwm (:1304, BaseIsa == CHERIoT; 3 ibex_csr) E, g_mshwm_tieoff (:1347) N; g_pmp_registers
(:1362, PMPEnable) E with g_exp_rd_data[0..15].g_implemented_regions (:1378-1379, all 16 since
PMPNumRegions = PMP_MAX_REGIONS) E, g_other_regions (:1411) N, g_pmp_g0 (:1385, PMPGranularity == 0)
E, g_pmp_g1 / g_pmp_g2 (:1389, :1398) N, g_pmp_csrs[0..15] (:1419) E with g_lower (:1474, i < 15) E
for 0..14 and g_upper (:1478) E for i = 15; g_no_pmp_tieoffs (:1532) N; gen_cntrs[0..28] (:1667)
always E, gen_imp (:1670, i < 10) E for i = 0..9, gen_unimp (:1699) E for i = 10..28,
gen_compressed_instr_cnt (:1687, Cnt == 10 i.e. i = 7) E, gen_other_cnts (:1693) E for the other
nine implemented, gen_no_compressed_instr_cnt (:1702) N (Cnt == 10 is implemented);
g_mcountinhibit_reduced (:1709, MHPMCounterNum < 29) E, g_mcountinhibit_full (:1719) N;
g_mcounteren_reduced (:1731) E, g_mcounteren_full (:1733) N; gen_trigger_regs (:1754, DbgTriggerEn)
E with g_dbg_tmatch_we[0], g_dbg_tmatch_reg[0], g_dbg_trigger_match[0] (:1776, :1806, :1871,
DbgHwBreakNum = 1) E, g_dbg_tmatch_multiple_select (:1839, DbgHwBreakNum > 1) N,
g_dbg_tmatch_single_select (:1842) E; gen_no_trigger_regs (:1876) N; gen_dit (:1892, DataIndTiming)
E, gen_no_dit (:1896) N; gen_dummy (:1908, DummyInstructions) E, gen_no_dummy (:1917) N;
gen_icache_enable (:1935, ICache) E, gen_no_icache (:1950) N; gen_scr (:2003, BaseIsa == CHERIoT;
contains no sub-instances) E, gen_no_scr (:2228) N. All ibex_csr instances get ShadowCopy =
ShadowCSR = 0 or a literal 1'b0, so ibex_csr.gen_shadow (rtl/ibex_csr.sv:38) is N everywhere and
gen_no_shadow (:51) is E everywhere.

### ibex_pmp (rtl/ibex_pmp.sv)
g_addr_exp[0..15] with g_entry0 (r == 0) / g_oth (:157-162) E; g_bitmask[b] for b = 2..33 with
g_bit0 (b == 2) / g_others (:167-171) E; g_region_addr_mask_zero_granularity (:177,
PMPGranularity == 0) E, g_region_addr_mask_other_granularity (:180) N; g_access_check[0..2]
.g_regions[0..15] (:188-189) E.

### ibex_counter (rtl/ibex_counter.sv)
g_cnt_dsp (:65, UseDsp == "yes", only under `ifdef FPGA_XILINX :53-58) N; g_cnt_no_dsp (:74) E;
for the 64-bit instances g_counter_full (:99) E with g_counter_val_upd_o (:102) E for minstret and
g_no_counter_val_upd_o (:104) E for mcycle; for the ten 32-bit instances g_counter_narrow (:86) E
with g_counter_val_upd_o (:92) E only for Cnt == 10 and g_no_counter_val_upd_o (:94) E otherwise.

### ibex_register_file_ff (rtl/ibex_register_file_ff.sv, wrapper sibling)
g_cheriot_rf (:88, BaseIsa == CHERIoT) E with g_rf_data_flops[1..15] (:116), g_rf_shared_flops[1..15]
(:131), g_dummy_r0 (:153, DummyInstructions) E, g_normal_r0 (:188) N (so g_rf_shared0_x16 /
g_rf_shared0_no_x16 :197/:207 N); g_plain_rf (:241) N (so g_rf_flops, g_dummy_r0/g_normal_r0 at
:260-296 and g_unused_raddr_msb :308 N).

### Modules present in the file list but NOT elaborated
ibex_prefetch_buffer (rtl/ibex_prefetch_buffer.sv:12; only under gen_prefetch_buffer), ibex_fetch_fifo
(rtl/ibex_fetch_fifo.sv:15; only instantiated by ibex_prefetch_buffer at :90), ibex_branch_predict
(rtl/ibex_branch_predict.sv:20; only under g_branch_predictor), ibex_multdiv_slow
(rtl/ibex_multdiv_slow.sv:14; only under gen_multdiv_slow), prim_secded_inv_64_57_enc/dec (only under
gen_regfile_ecc.gen_cheriot_cap_ecc, rtl/ibex_core.sv:1252-1276), prim_clock_gating
(vendor/lowrisc_ip/ip/prim_generic/rtl/prim_clock_gating.sv:10; dependency of ibex_core.core:12 but
instantiated only by rtl/ibex_top.sv:333 and rtl/ibex_register_file_latch.sv:92-397, neither in the
DUT), prim_mubi4/8/.._sender/sync/dec (dependency of ibex_core.core:14, never instantiated in rtl/).

## 4. Per-module detail

Port lists are transcribed from the module headers; "[w]" gives the packed width, "[..] [n]" an
unpacked array. Key control-path signals (stall, flush, valid/ready, error, exception request) are
marked with "(KEY)".

### 4.1 ibex_core  (rtl/ibex_core.sv:17-191)

Instance path: top of the DUT (instantiated by the wrapper). Generate: n/a.

Function: Top level of the core. It wires the two/three pipeline stages (IF, ID/EX, WB) together with
the CSR block, PMP checker, LSU and CHERIoT execution unit, and owns the cross-stage control nets
(instr_valid_id, id_in_ready, pc_set, exc_cause, lsu_* errors, rf_* write-back) declared at
rtl/ibex_core.sv:199-490. It builds the security hardened core_busy_o multibit from buffered copies
of ctrl_busy/if_busy/lsu_busy (:498-518), gates instruction fetch on fetch_enable_i == IbexMuBiOn
(:644-649), qualifies LSU responses with an outstanding-request expectation (:1181-1186), and drives
the three alert outputs (:1337-1353): alert_minor_o = icache ECC error, alert_major_internal_o =
regfile ECC | PC mismatch | shadow CSR | CHERIoT fatal | bad cheriot_enable_i encoding,
alert_major_bus_o = load/store/instr integrity errors. It also contains the (RVFI-only) trace
pipeline (:1653-2435) and the FCOV signal declarations (:2447-2512). Doc: doc/03_reference/
pipeline_details.rst "Pipeline Details" (:9-31) and security.rst "Outputs" (:9-15).

Parameters as instantiated: see section 1 table (every value there).

Ports:
Inputs:
- clk_i [1], rst_ni [1]
- hart_id_i [32], boot_addr_i [32], cheriot_enable_i ibex_mubi_t [4] (tied IbexMuBiOff by wrapper)
- instr_gnt_i [1] (KEY ready), instr_rvalid_i [1] (KEY valid), instr_rdata_i [39] (MemDataWidth), instr_err_i [1] (KEY error)
- data_gnt_i [1] (KEY), data_rvalid_i [1] (KEY), data_rdata_i [39], data_tag_i [1], data_err_i [1] (KEY error)
- rf_rdata_a_ecc_i [32], rf_rdata_b_ecc_i [32], rf_rcap_a_ecc_i [35], rf_rcap_b_ecc_i [35]
- ic_tag_rdata_i [28] [2], ic_data_rdata_i [78] [2], ic_scr_key_valid_i [1]
- irq_software_i [1], irq_timer_i [1], irq_external_i [1], irq_fast_i [15], irq_nm_i [1]
- debug_req_i [1] (KEY)
- fetch_enable_i ibex_mubi_t [4] (KEY: gates fetch), mcounteren_writable_i ibex_mubi_t [4]
Outputs:
- instr_req_o [1] (KEY valid), instr_addr_o [32]
- data_req_o [1] (KEY valid; = data_req_out & ~pmp_req_err[PMP_D], :1063), data_we_o [1], data_be_o [4], data_addr_o [32], data_wdata_o [39], data_tag_o [1]
- dummy_instr_id_o [1], dummy_instr_wb_o [1], rf_raddr_a_o [5], rf_raddr_b_o [5], rf_waddr_wb_o [5], rf_we_wb_o [1], rf_wdata_wb_ecc_o [32], rf_wcap_ecc_wb_o [35]
- ic_tag_req_o [2], ic_tag_write_o [1], ic_tag_addr_o [8], ic_tag_wdata_o [28], ic_data_req_o [2], ic_data_write_o [1], ic_data_addr_o [8], ic_data_wdata_o [78], ic_scr_key_req_o [1]
- irq_pending_o [1]
- crash_dump_o crash_dump_t, double_fault_seen_o [1] (KEY exception escalation)
- alert_minor_o [1], alert_major_internal_o [1], alert_major_bus_o [1] (KEY errors), core_busy_o ibex_mubi_t [4]
- `ifdef RVFI only (:136-181): rvfi_valid, rvfi_order [64], rvfi_insn [32], rvfi_trap, rvfi_halt, rvfi_intr, rvfi_mode [2], rvfi_ixl [2], rvfi_rs1_addr/rs2_addr/rs3_addr [5], rvfi_rs1_rdata/rs2_rdata/rs3_rdata [32], rvfi_rs1_rcap/rs2_rcap cap_t, rvfi_rd_addr [5], rvfi_rd_wdata [32], rvfi_rd_wcap cap_t, rvfi_pc_rdata/pc_wdata [32], rvfi_mem_is_cap, rvfi_mem_addr [32], rvfi_mem_rmask/wmask [4], rvfi_mem_rdata/wdata [32], rvfi_mem_rcap/wcap cap_t, rvfi_ext_pre_mip/post_mip [32], rvfi_ext_nmi, rvfi_ext_nmi_int, rvfi_ext_debug_req, rvfi_ext_debug_mode, rvfi_ext_rf_wr_suppress, rvfi_ext_mcycle [64], rvfi_ext_mhpmcounters [32] [10], rvfi_ext_mhpmcountersh [32] [10], rvfi_ext_ic_scr_key_valid, rvfi_ext_irq_valid, rvfi_ext_expanded_insn_valid, rvfi_ext_expanded_insn [16], rvfi_ext_expanded_insn_last.

### 4.2 ibex_if_stage  (rtl/ibex_if_stage.sv:17-134)

Instance path: ibex_core.if_stage_i (rtl/ibex_core.sv:528-547). Generate: none (always).

Function: Instruction Fetch stage. Selects the next fetch address (boot, jump target, exception
vector, mepc, depc) via fetch_addr_mux (:241-253) and exc_pc_mux (:213-233), drives the prefetch
engine (here ibex_icache, :298-347) with prefetch_branch/prefetch_addr (:287-288), decompresses
instructions through ibex_compressed_decoder (:485-501), optionally substitutes dummy instructions
(:504-545), and registers the instruction plus PC into the IF/ID pipeline register when
if_id_pipe_reg_we = instr_new_id_d = if_instr_valid & id_in_ready_i & ~pc_set_i (:568-587). With
MemECC it checks the 39-bit instruction bus word and raises instr_intg_err_o (:259-282); with
PCIncrCheck it flags pc_mismatch_alert_o when pc_if_o is not the previous PC +2/+4 (:659-688). Doc:
doc/03_reference/instruction_fetch.rst "Instruction Fetch" (:3-27).

Parameters as instantiated (rtl/ibex_core.sv:529-546): DmHaltAddr=32'h1A110800,
DmExceptionAddr=32'h1A110808, DummyInstructions=1, ICache=1, RV32ZC=RV32ZcaZcbZcmp, ICacheECC=1,
ICacheTweakInfection=1, BusSizeECC=39, TagSizeECC=28, LineSizeECC=78, PCIncrCheck=1, ResetAll=1,
RndCnstLfsrSeed=RndCnstLfsrSeedDefault, RndCnstLfsrPerm=RndCnstLfsrPermDefault, BranchPredictor=0,
MemECC=1, MemDataWidth=39, BaseIsa=BaseIsaRV32IorCHERIoT.

Ports:
Inputs:
- clk_i, rst_ni, cheriot_enable_i [4], boot_addr_i [32], req_i [1] (KEY: instr_req_gated), debug_mode_i
- instr_gnt_i (KEY), instr_rvalid_i (KEY), instr_rdata_i [39], instr_bus_err_i (KEY error)
- ic_tag_rdata_i [28] [2], ic_data_rdata_i [78] [2], ic_scr_key_valid_i
- pmp_err_if_i (KEY error), pmp_err_if_plus2_i (KEY error)
- instr_valid_clear_i (KEY flush), pc_set_i (KEY redirect), pc_mux_i pc_sel_e, nt_branch_mispredict_i, nt_branch_addr_i [32], exc_pc_mux_i exc_pc_sel_e, exc_cause exc_cause_t
- dummy_instr_en_i, dummy_instr_mask_i [3], dummy_instr_seed_en_i, dummy_instr_seed_i [32], icache_enable_i, icache_inval_i
- branch_target_ex_i [32], csr_mepc_i [32], csr_depc_i [32], csr_mtvec_i [32]
- id_in_ready_i (KEY ready), pcc_cap_i decoded_cap_t
Outputs:
- instr_req_o (KEY valid), instr_addr_o [32], instr_intg_err_o (KEY error)
- ic_tag_req_o [2], ic_tag_write_o, ic_tag_addr_o [8], ic_tag_wdata_o [28], ic_data_req_o [2], ic_data_write_o, ic_data_addr_o [8], ic_data_wdata_o [78], ic_scr_key_req_o
- instr_valid_id_o (KEY valid), instr_new_id_o, instr_rdata_id_o [32], instr_rdata_alu_id_o [32], instr_rdata_c_id_o [16], instr_is_compressed_id_o, instr_gets_expanded_id_o instr_exp_e, instr_expanded_id_o [16], instr_bp_taken_o, instr_fetch_err_o (KEY error), instr_fetch_err_plus2_o, illegal_c_insn_id_o (KEY exception), instr_fetch_cheriot_acc_vio_o, instr_fetch_cheriot_bound_vio_o, dummy_instr_id_o, pc_if_o [32], pc_id_o [32]
- icache_ecc_error_o (KEY error), csr_mtvec_init_o, pc_mismatch_alert_o (KEY error), if_busy_o

### 4.3 ibex_icache  (rtl/ibex_icache.sv:13-69)

Instance path: ibex_core.if_stage_i.gen_icache.icache_i (rtl/ibex_if_stage.sv:298-307). Generate:
gen_icache, condition `if (ICache)` with ICache = 1.

Function: 4 KiB, 2-way, 64-bit-line instruction cache that replaces the prefetch buffer and speaks
the same ready/valid instruction interface to the IF stage (ready_i/valid_o/rdata_o/addr_o/err_o).
A two-stage lookup pipeline (IC0 arbitration and RAM request, IC1 hit detection) works with NUM_FB
= 4 fill buffers (:72) that track outstanding external fetches, buffer returning data and request
allocation writes. With ICacheECC the tag and data words are protected by inverted 28/22 and 39/32
SECDED codes (:286-310, :538-585); any error in IC1 cancels the hit, forces an invalidation write
and raises ecc_error_o; with TweakInfection the encoded words are additionally XORed with an
address-derived tweak before writing and untweaked before checking (:321-454). After reset and on
icache_inval_i the tag RAM is walked and invalidated (:1282-1290 region). The RAM ports
(ic_tag_*/ic_data_*) leave ibex_core unconnected to real RAMs in this DUT; ic_scr_key_req_o requests a
new scramble key. Doc: doc/03_reference/icache.rst "Instruction Cache" (:3-30), "Sub Unit
Description" (:122-186), "Cache ECC protection" (:189-218), "Cache invalidation" (:220-225).

Parameters as instantiated (rtl/ibex_if_stage.sv:301-306): ICacheECC=1, ResetAll=1, BusSizeECC=39,
TagSizeECC=28, LineSizeECC=78, TweakInfection=1 (from ICacheTweakInfection); BranchCache keeps its
default 1'b0 (rtl/ibex_icache.sv:20).

Ports:
Inputs: clk_i, rst_ni, req_i (KEY), branch_i (KEY redirect), addr_i [32], ready_i (KEY ready),
instr_gnt_i (KEY), instr_rdata_i [32], instr_err_i (KEY error), instr_rvalid_i (KEY),
ic_tag_rdata_i [28] [2], ic_data_rdata_i [78] [2], ic_scr_key_valid_i, icache_enable_i,
icache_inval_i (KEY flush).
Outputs: valid_o (KEY valid), rdata_o [32], addr_o [32], err_o (KEY error), err_plus2_o,
instr_req_o (KEY valid), instr_addr_o [32], ic_tag_req_o [2], ic_tag_write_o, ic_tag_addr_o [8],
ic_tag_wdata_o [28], ic_data_req_o [2], ic_data_write_o, ic_data_addr_o [8], ic_data_wdata_o [78],
ic_scr_key_req_o, busy_o, ecc_error_o (KEY error).

### 4.4 ibex_compressed_decoder  (rtl/ibex_compressed_decoder.sv:17-33)

Instance path: ibex_core.if_stage_i.compressed_decoder_i (rtl/ibex_if_stage.sv:485-489). Generate:
none (always).

Function: Expands 16-bit RVC (Zca, Zcb) instructions into their 32-bit equivalents and flags
illegal compressed encodings (illegal_instr_o). With RV32ZC = RV32ZcaZcbZcmp it also implements the
Zcmp push/pop sequences: a small FSM (cm_state_q, :893-903, reset-all flops) emits several expanded
32-bit instructions for one 16-bit cm.* instruction and reports the expansion state via
gets_expanded_o (instr_exp_e), taking id_in_ready_i to advance and flush_expanded_i (pc_set on
exception, rtl/ibex_if_stage.sv:483) to abort. The cheriot_enable_i input selects CHERIoT-specific
compressed encodings when CHERIoT is active (not the case here). Doc: doc/03_reference/
instruction_fetch.rst :22 ("Compressed instructions are expanded by the IF stage ..."); no
dedicated section.

Parameters as instantiated (rtl/ibex_if_stage.sv:486-488): RV32ZC=RV32ZcaZcbZcmp, ResetAll=1,
BaseIsa=BaseIsaRV32IorCHERIoT.

Ports:
Inputs: clk_i, rst_ni, valid_i (KEY valid; = fetch_valid & ~fetch_err), id_in_ready_i (KEY ready),
instr_i [32], cheriot_enable_i [4], flush_expanded_i (KEY flush).
Outputs: instr_o [32], is_compressed_o, gets_expanded_o instr_exp_e, illegal_instr_o (KEY exception).

### 4.5 ibex_dummy_instr  (rtl/ibex_dummy_instr.sv:12-31)

Instance path: ibex_core.if_stage_i.gen_dummy_instr.dummy_instr_i (rtl/ibex_if_stage.sv:504-512).
Generate: gen_dummy_instr, condition `if (DummyInstructions)` with DummyInstructions = 1.

Function: Security countermeasure (SEC_CM: CTRL_FLOW.UNPREDICTABLE, rtl/ibex_if_stage.sv:505) that
inserts pseudo-random ADD/MUL/DIV/AND instructions targeting x0 into the pipeline. A 32-bit
prim_lfsr (:76-90) supplies a 17-bit field (2-bit type, two 5-bit register operands, 5-bit count,
:43-49); a counter of executed instructions (:97-112) compares against the masked LFSR count
(dummy_instr_mask_i shortens the interval) and asserts insert_dummy_instr_o when equal (:115),
which stalls the IF stage for one cycle while dummy_instr_data_o (:144) is fed to ID. The LFSR
advances on each insertion (:64) and can be re-seeded through the secureseed CSR path
(dummy_instr_seed_en_i/dummy_instr_seed_i, :66-74, :85-86). Doc: doc/03_reference/security.rst
"Dummy Instruction Insertion" (:41-70).

Parameters as instantiated (rtl/ibex_if_stage.sv:510-511): RndCnstLfsrSeed=RndCnstLfsrSeedDefault
(32'hac533bf4), RndCnstLfsrPerm=RndCnstLfsrPermDefault (rtl/ibex_pkg.sv:741-742).

Ports:
Inputs: clk_i, rst_ni, dummy_instr_en_i, dummy_instr_mask_i [3], dummy_instr_seed_en_i,
dummy_instr_seed_i [32], fetch_valid_i (KEY valid), id_in_ready_i (KEY ready).
Outputs: insert_dummy_instr_o (KEY stall), dummy_instr_data_o [32].

### 4.6 prim_lfsr  (vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv:29-73)

Instance path: ibex_core.if_stage_i.gen_dummy_instr.dummy_instr_i.lfsr_i (rtl/ibex_dummy_instr.sv:76-82).
Generate: inside gen_dummy_instr (see 4.5).

Function: Galois-XOR linear feedback shift register with a compile-time state permutation.
next_lfsr_state = entropy ^ (coeffs masked by lfsr_q[0]) ^ (lfsr_q >> 1) using the polynomial from
the built-in LUT (:283-296); lfsr_d selects external seed (seed_en_i), the default seed on lockup
(all-zero state, :299), the next state when enabled, or holds (:345-348); the flop resets to
DefaultSeedLocal (:485-491). With StatePermEn the 17 output bits are taken from permuted positions
of the 32-bit state (:468-472); NonLinearOut is off so sbox_out = lfsr_q (:463-465). In simulation
(`ifdef SIMULATION, not VERILATOR) the reset seed is randomized 70 percent of the time unless
plusarg prim_lfsr_use_default_seed is given (:250-273). Doc: no doc section (security.rst :64-67
mentions "an LFSR" and its seed/permutation parameters).

Parameters as instantiated (rtl/ibex_dummy_instr.sv:77-81): LfsrDw=LfsrWidth=32, StateOutDw=
LFSR_OUT_W=17 ($bits of lfsr_data_t: 2+5+5+5, rtl/ibex_dummy_instr.sv:33-49), DefaultSeed=
RndCnstLfsrSeed, StatePermEn=1'b1, StatePerm=RndCnstLfsrPerm; defaults kept: LfsrType="GAL_XOR",
EntropyDw=8, CustomCoeffs='0, MaxLenSVA=1, LockupSVA=1, ExtSeedSVA=1, NonLinearOut=0.

Ports:
Inputs: clk_i, rst_ni, seed_en_i, seed_i [32], lfsr_en_i, entropy_i [8] (tied '0 at
rtl/ibex_dummy_instr.sv:88).
Outputs: state_o [17].

### 4.7 ibex_id_stage  (rtl/ibex_id_stage.sv:21-227)

Instance path: ibex_core.id_stage_i (rtl/ibex_core.sv:663-673). Generate: none (always).

Function: Instruction Decode/Execute stage controller. It hosts the decoder and the controller,
builds the ALU operand muxes (including the separate branch-target ALU operand muxes in
g_btalu_muxes :369-406), the multicycle intermediate-value registers (:446), and the ID FSM
(FIRST_CYCLE/MULTI_CYCLE) that produces the stall terms stall_ld_hz, stall_mem, stall_multdiv,
stall_branch, stall_jump, stall_alu (:259-308, :875-965). With WritebackStage it tracks
register-read-after-WB-write hazards and outstanding memory accesses in gen_stall_mem
(:1000-1141), producing en_wb_o/instr_type_wb_o toward WB and rf_waddr_id_o/rf_wdata_id_o/
rf_we_id_o. It gates all side effects with instr_executing (:463, :732-747) and, under
DataIndTiming, makes branches take a fixed number of cycles (g_sec_branch_taken :819). It also
decodes CHERIoT operand fields for ibex_cheriot_ex (cheriot_* outputs). Doc: doc/03_reference/
instruction_decode_execute.rst "Instruction Decode Block (ID)" (:16-22).

Parameters as instantiated (rtl/ibex_core.sv:664-672): RV32E=0, RV32M=RV32MSingleCycle,
RV32B=RV32BOTEarlGrey, BranchTargetALU=1, DataIndTiming=1, WritebackStage=1, BranchPredictor=0,
MemECC=1, BaseIsa=BaseIsaRV32IorCHERIoT.

Ports:
Inputs:
- clk_i, rst_ni, cheriot_enable_i [4]
- instr_valid_i (KEY valid), instr_rdata_i [32], instr_rdata_alu_i [32], instr_rdata_c_i [16], instr_is_compressed_i, instr_gets_expanded_i instr_exp_e, instr_bp_taken_i, instr_exec_i (KEY: fetch_enable)
- branch_decision_i
- illegal_c_insn_i (KEY exception), instr_fetch_err_i (KEY exception), instr_fetch_err_plus2_i, instr_fetch_cheriot_acc_vio_i, instr_fetch_cheriot_bound_vio_i, pc_id_i [32]
- ex_valid_i (KEY valid), lsu_resp_valid_i (KEY valid)
- imd_val_we_ex_i [2], imd_val_d_ex_i [34] [2]
- priv_mode_i priv_lvl_e, csr_mstatus_tw_i, illegal_csr_insn_i (KEY exception), data_ind_timing_i, csr_pcc_perm_sr_i
- lsu_req_done_i (KEY), lsu_addr_incr_req_i, lsu_addr_last_i [32]
- csr_mstatus_mie_i, irq_pending_i (KEY), irqs_i irqs_t, irq_nm_i (KEY)
- lsu_load_err_i, lsu_load_resp_intg_err_i, lsu_store_err_i, lsu_store_resp_intg_err_i (KEY exceptions), lsu_err_is_cheriot_i
- debug_req_i (KEY), debug_single_step_i, debug_ebreakm_i, debug_ebreaku_i, trigger_match_i (KEY)
- result_ex_i [32], csr_rdata_i [32], rf_rdata_a_i [32], rf_rdata_b_i [32]
- rf_waddr_wb_i [5], rf_wdata_fwd_wb_i [32], rf_write_wb_i
- ready_wb_i (KEY ready), outstanding_load_wb_i, outstanding_store_wb_i
- cheriot_ex_valid_i, cheriot_ex_err_i (KEY exception), cheriot_ex_err_info_i [12], cheriot_wb_err_i (KEY exception), cheriot_wb_err_info_i [16], cheriot_branch_req_i, cheriot_branch_target_i [32]
Outputs:
- ctrl_busy_o, illegal_insn_o (KEY exception)
- instr_req_o (KEY), instr_first_cycle_id_o, instr_valid_clear_o (KEY flush), id_in_ready_o (KEY ready/stall), icache_inval_o (KEY flush)
- pc_set_o (KEY redirect), pc_mux_o pc_sel_e, nt_branch_mispredict_o, nt_branch_addr_o [32], exc_pc_mux_o exc_pc_sel_e, exc_cause_o exc_cause_t (KEY exception)
- alu_operator_ex_o alu_op_e, alu_operand_a_ex_o [32], alu_operand_b_ex_o [32], imd_val_q_ex_o [34] [2], bt_a_operand_o [32], bt_b_operand_o [32]
- mult_en_ex_o, div_en_ex_o, mult_sel_ex_o, div_sel_ex_o, multdiv_operator_ex_o md_op_e, multdiv_signed_mode_ex_o [2], multdiv_operand_a_ex_o [32], multdiv_operand_b_ex_o [32], multdiv_ready_id_o
- csr_access_o, csr_op_o csr_op_e, csr_addr_o csr_num_e, csr_op_en_o, csr_save_if_o, csr_save_id_o, csr_save_wb_o, csr_restore_mret_id_o, csr_restore_dret_id_o, csr_save_cause_o (KEY exception commit), csr_mepcc_clrtag_o, csr_mtval_o [32]
- lsu_req_o (KEY valid), lsu_we_o, lsu_type_o [2], lsu_sign_ext_o, lsu_wdata_o [32]
- expecting_load_resp_o, expecting_store_resp_o, nmi_mode_o
- debug_mode_o, debug_mode_entering_o, debug_cause_o dbg_cause_e, debug_csr_save_o
- rf_raddr_a_o [5], rf_raddr_b_o [5], rf_ren_a_o, rf_ren_b_o, rf_waddr_id_o [5], rf_wdata_id_o [32], rf_we_id_o, rf_rd_a_wb_match_o, rf_rd_b_wb_match_o
- en_wb_o (KEY valid to WB), instr_type_wb_o wb_instr_type_e, instr_perf_count_id_o
- perf_jump_o, perf_branch_o, perf_tbranch_o, perf_dside_wait_o, perf_mul_wait_o, perf_div_wait_o, instr_id_done_o
- cheriot_exec_id_o, instr_is_cheriot_id_o, instr_is_rv32lsu_id_o, cheriot_imm12_o [12], cheriot_imm20_o [20], cheriot_imm21_o [21], cheriot_operator_o cheriot_op_t, cheriot_cs2_dec_o [5], cheriot_cap_field_sel_o, cheriot_adder_a_sel_o, cheriot_adder_b_sel_o, cheriot_setaddr_sel_o, cheriot_setbounds_sel_o, cheriot_load_o, cheriot_store_o

### 4.8 ibex_decoder  (rtl/ibex_decoder.sv:17-120)

Instance path: ibex_core.id_stage_i.decoder_i (rtl/ibex_id_stage.sv:478-484). Generate: none.

Function: Purely combinational decode of the 32-bit (already uncompressed) instruction into control
signals: ALU operator and operand-mux selects, immediates, register-file addresses and write
enable, multiplier/divider enables, CSR access/operation, LSU request/type/sign-extension,
jump/branch indications and the special instructions ecall/ebreak/mret/dret/wfi/fence.i. It raises
illegal_insn_o for undefined encodings and, in gen_16reg_check_active (:237), for x16-x31 access
when RV32E or CHERIoT is active at run time (here only when cheriot_enable_i == IbexMuBiOn, so
inactive). It also decodes the CHERIoT instruction group into cheriot_* fields for ibex_cheriot_ex;
a one-flop rs3 register for ternary bitmanip instructions exists in gen_rs3_flop (:172). Doc:
doc/03_reference/instruction_decode_execute.rst "Decoder" (:37-41).

Parameters as instantiated (rtl/ibex_id_stage.sv:479-483): RV32E=0, RV32M=RV32MSingleCycle,
RV32B=RV32BOTEarlGrey, BranchTargetALU=1, BaseIsa=BaseIsaRV32IorCHERIoT. Internal:
CheriLimit16Regs = 1 (:124).

Ports:
Inputs: clk_i, rst_ni, cheriot_enable_i [4], branch_taken_i, instr_first_cycle_i, instr_rdata_i
[32], instr_rdata_alu_i [32], illegal_c_insn_i (KEY exception).
Outputs: illegal_insn_o (KEY exception), ebrk_insn_o, mret_insn_o, dret_insn_o, ecall_insn_o,
wfi_insn_o, jump_set_o, icache_inval_o (KEY flush), imm_a_mux_sel_o imm_a_sel_e, imm_b_mux_sel_o
imm_b_sel_e, bt_a_mux_sel_o op_a_sel_e, bt_b_mux_sel_o imm_b_sel_e, imm_i_type_o [32],
imm_s_type_o [32], imm_b_type_o [32], imm_u_type_o [32], imm_j_type_o [32], zimm_rs1_type_o [32],
rf_wdata_sel_o rf_wd_sel_e, rf_we_o, rf_we_or_load_o, rf_raddr_a_o [5], rf_raddr_b_o [5],
rf_waddr_o [5], rf_ren_a_o, rf_ren_b_o, alu_operator_o alu_op_e, alu_op_a_mux_sel_o op_a_sel_e,
alu_op_b_mux_sel_o op_b_sel_e, alu_multicycle_o, mult_en_o, div_en_o, mult_sel_o, div_sel_o,
multdiv_operator_o md_op_e, multdiv_signed_mode_o [2], csr_access_o, csr_op_o csr_op_e, csr_addr_o
csr_num_e, csr_cheriot_always_ok_o, data_req_o (KEY LSU request), cheriot_data_req_o, data_we_o,
data_type_o [2], data_sign_extension_o, jump_in_dec_o, branch_in_dec_o, instr_is_cheriot_o,
instr_is_legal_cheriot_o, cheriot_imm12_o [12], cheriot_imm20_o [20], cheriot_imm21_o [21],
cheriot_operator_o cheriot_op_t, cheriot_cs2_dec_o [5], cheriot_cap_field_sel_o,
cheriot_adder_a_sel_o, cheriot_adder_b_sel_o, cheriot_setaddr_sel_o, cheriot_setbounds_sel_o.

### 4.9 ibex_controller  (rtl/ibex_controller.sv:14-135)

Instance path: ibex_core.id_stage_i.controller_i (rtl/ibex_id_stage.sv:615-620). Generate: none.

Function: The core's main FSM (ctrl_fsm_e states RESET, BOOT_SET, WAIT_SLEEP, SLEEP, FIRST_FETCH,
DECODE, FLUSH, IRQ_TAKEN, DBG_TAKEN_IF, DBG_TAKEN_ID; rtl/ibex_pkg.sv:291-302; state logic from
:582). It handles startup (boot address set), sleep/wake on WFI, exception requests exc_req_d =
ecall | ebreak | illegal | fetch error | CHERIoT faults (:268-278) and LSU errors exc_req_lsu
(:275), interrupt entry (handle_irq :498) and debug entry (enter_debug_mode :474-476), and
programs the IF stage through pc_set_o/pc_mux_o/exc_pc_mux_o/exc_cause_o while asking the CSR
block to save/restore state (csr_save_*/csr_restore_*/csr_save_cause_o). It produces the pipeline
handshake id_in_ready_o = ~stall & ~halt_if & ~retain_id (:1020), instr_valid_clear_o (:1027) and
flush_id_o (:1002); with WritebackStage the g_wb_exceptions branch (:299-337) reports load/store
errors of the instruction in WB via wb_exception_o. With MemECC the g_intg_irq_int branch
(:393-438) turns bus integrity errors into an internal interrupt. Doc: doc/03_reference/
instruction_decode_execute.rst "Controller" (:24-35) and exception_interrupts.rst (:3-18).

Parameters as instantiated (rtl/ibex_id_stage.sv:616-619): BaseIsa=BaseIsaRV32IorCHERIoT,
WritebackStage=1, BranchPredictor=0, MemECC=1.

Ports:
Inputs:
- clk_i, rst_ni, cheriot_enable_i [4]
- illegal_insn_i (KEY exception), ecall_insn_i, mret_insn_i, dret_insn_i, wfi_insn_i, ebrk_insn_i, csr_pipe_flush_i (KEY flush), csr_access_i, csr_cheriot_always_ok_i
- instr_valid_i (KEY valid), instr_i [32], instr_compressed_i [16], instr_is_compressed_i, instr_gets_expanded_i instr_exp_e, instr_bp_taken_i, instr_fetch_err_i (KEY exception), instr_fetch_err_plus2_i, instr_fetch_cheriot_acc_vio_i, instr_fetch_cheriot_bound_vio_i, pc_id_i [32]
- instr_exec_i (KEY)
- lsu_addr_last_i [32], load_err_i (KEY exception), store_err_i (KEY exception), mem_resp_intg_err_i (KEY error), lsu_err_is_cheriot_i
- branch_set_i, branch_not_set_i, jump_set_i
- csr_mstatus_mie_i, irq_pending_i (KEY), irqs_i irqs_t, irq_nm_ext_i (KEY)
- debug_req_i (KEY), debug_single_step_i, debug_ebreakm_i, debug_ebreaku_i, trigger_match_i (KEY)
- priv_mode_i priv_lvl_e, csr_pcc_perm_sr_i
- stall_id_i (KEY stall), stall_wb_i (KEY stall), ready_wb_i (KEY ready)
- instr_is_cheriot_i, cheriot_ex_valid_i, cheriot_ex_err_i (KEY exception), cheriot_wb_err_i (KEY exception), cheriot_ex_err_info_i [12], cheriot_wb_err_info_i [16], cheriot_branch_req_i, cheriot_branch_target_i [32]
Outputs:
- ctrl_busy_o, instr_valid_clear_o (KEY flush), id_in_ready_o (KEY ready), controller_run_o
- instr_req_o (KEY), pc_set_o (KEY redirect), pc_mux_o pc_sel_e, nt_branch_mispredict_o, exc_pc_mux_o exc_pc_sel_e, exc_cause_o exc_cause_t (KEY exception)
- wb_exception_o (KEY exception), id_exception_o (KEY exception), id_exception_nc_o
- nmi_mode_o, debug_cause_o dbg_cause_e, debug_csr_save_o, debug_mode_o, debug_mode_entering_o
- csr_save_if_o, csr_save_id_o, csr_save_wb_o, csr_restore_mret_id_o, csr_restore_dret_id_o, csr_save_cause_o (KEY), csr_mepcc_clrtag_o, csr_mtval_o [32]
- flush_id_o (KEY flush), perf_jump_o, perf_tbranch_o

### 4.10 ibex_ex_block  (rtl/ibex_ex_block.sv:11-54)

Instance path: ibex_core.ex_block_i (rtl/ibex_core.sv:863-867). Generate: none.

Function: Execute block. It instantiates the ALU and the multiplier/divider, muxes their results
(result_ex_o = multdiv_sel ? multdiv_result : alu_result, :89) and their intermediate-value register
writes (:83-85), derives branch_decision_o from the ALU comparison (:92), and with BranchTargetALU
computes branch_target_o = bt_a_operand_i + bt_b_operand_i in a dedicated adder (:94-101).
ex_valid_o is the multdiv valid when a mul/div is selected, otherwise the inverse of an
intermediate-register write (i.e. the last cycle of a multicycle ALU op) (:197). Under INC_ASSERT
it exposes sva_multdiv_fsm_idle for hierarchical assertions (:199-215). Doc: doc/03_reference/
instruction_decode_execute.rst "Execute Block" (:49-53).

Parameters as instantiated (rtl/ibex_core.sv:864-866): RV32M=RV32MSingleCycle,
RV32B=RV32BOTEarlGrey, BranchTargetALU=1.

Ports:
Inputs: clk_i, rst_ni, alu_operator_i alu_op_e, alu_operand_a_i [32], alu_operand_b_i [32],
alu_instr_first_cycle_i, bt_a_operand_i [32], bt_b_operand_i [32], multdiv_operator_i md_op_e,
mult_en_i, div_en_i, mult_sel_i, div_sel_i, multdiv_signed_mode_i [2], multdiv_operand_a_i [32],
multdiv_operand_b_i [32], multdiv_ready_id_i (KEY ready), data_ind_timing_i, imd_val_q_i [34] [2].
Outputs: imd_val_we_o [2], imd_val_d_o [34] [2], alu_adder_result_ex_o [32], result_ex_o [32],
branch_target_o [32], branch_decision_o, ex_valid_o (KEY valid).

### 4.11 ibex_alu  (rtl/ibex_alu.sv:9-33)

Instance path: ibex_core.ex_block_i.alu_i (rtl/ibex_ex_block.sv:116-118). Generate: none.

Function: Combinational ALU implementing RV32I arithmetic, logic, shifts and comparisons plus the
RV32B OTEarlGrey bit-manipulation subset (Zba, Zbb, Zbc, Zbs, Zbf, Zbp, Zbr, Zbt per the doc table)
in the g_alu_rvb / gen_alu_rvb_otearlgrey_full branches (:412, :648). Its adder is shared: it
serves the multiplier/divider through multdiv_operand_a_i/b_i when multdiv_sel_i is set (:18-21),
and adder_result_o feeds the LSU address (rtl/ibex_ex_block.sv:129, rtl/ibex_core.sv:899). Multicycle
bitmanip instructions (rotates, ternary, CRC) use imd_val_q_i/imd_val_d_o/imd_val_we_o to carry
state across two cycles. Doc: doc/03_reference/instruction_decode_execute.rst "Arithmetic Logic
Unit (ALU)" (:55-105).

Parameters as instantiated (rtl/ibex_ex_block.sv:117): RV32B=RV32BOTEarlGrey.

Ports:
Inputs: operator_i alu_op_e, operand_a_i [32], operand_b_i [32], instr_first_cycle_i,
multdiv_operand_a_i [33], multdiv_operand_b_i [33], multdiv_sel_i, imd_val_q_i [32] [2].
Outputs: imd_val_d_o [32] [2], imd_val_we_o [2], adder_result_o [32], adder_result_ext_o [34],
result_o [32], comparison_result_o, is_equal_result_o.

### 4.12 ibex_multdiv_fast  (rtl/ibex_multdiv_fast.sv:17-46)

Instance path: ibex_core.ex_block_i.gen_multdiv_fast.multdiv_i (rtl/ibex_ex_block.sv:165-168).
Generate: gen_multdiv_fast, condition `else if (RV32M == RV32MFast || RV32M == RV32MSingleCycle)`.

Function: Multiplier/divider. With RV32M = RV32MSingleCycle the gen_mult_single_cycle branch
(:140-260) uses three 17x17 multipliers and a 34-bit accumulator so MUL completes in one cycle and
MULH in two (FSM MULL/MULH, :142-145). Division and remainder use a 37-cycle long-division FSM
(md_fsm_e MD_IDLE, MD_ABS_A, MD_ABS_B, MD_COMP, MD_LAST, MD_CHANGE_SIGN, MD_FINISH; :90-93) that
borrows the ALU adder through alu_operand_a_o/b_o and alu_adder_ext_i (:30-36); with
data_ind_timing_i set the divide-by-zero early exit is suppressed (:434, :445). Intermediate
results live in the ID stage registers via imd_val_*. valid_o signals completion to
ibex_ex_block. Doc: doc/03_reference/instruction_decode_execute.rst "Multiplier/Divider Block
(MULT/DIV)" (:110-154).

Parameters as instantiated (rtl/ibex_ex_block.sv:167): RV32M=RV32MSingleCycle.

Ports:
Inputs: clk_i, rst_ni, mult_en_i, div_en_i, mult_sel_i, div_sel_i, operator_i md_op_e,
signed_mode_i [2], op_a_i [32], op_b_i [32], alu_adder_ext_i [34], alu_adder_i [32],
equal_to_zero_i, data_ind_timing_i, imd_val_q_i [34] [2], multdiv_ready_id_i (KEY ready).
Outputs: alu_operand_a_o [33], alu_operand_b_o [33], imd_val_d_o [34] [2], imd_val_we_o [2],
multdiv_result_o [32], valid_o (KEY valid).

### 4.13 ibex_cheriot_ex  (rtl/ibex_cheriot_ex.sv:5-120)

Instance path: ibex_core.g_cheriot_ex.u_ibex_cheriot_ex (rtl/ibex_core.sv:911-914). Generate:
g_cheriot_ex, condition `if (BaseIsa == BaseIsaRV32IorCHERIoT)` (compile-time true).

Function: CHERIoT capability execution unit. It reads the two capability operands (rf_rcap_a/b_i
with WB forwarding fwd_*), performs capability arithmetic/bounds/permission operations selected by
cheriot_operator_i and the *_sel_i fields, produces result_data_o/result_cap_o and
cheriot_rf_we_o for WB, raises cheriot_ex_err_o / cheriot_wb_err_o with error info for the
controller, drives PCC updates (pcc_cap_o, branch_req_o) and CHERIoT SCR accesses (csr_*_o), and
owns the LSU request mux: every load/store, CHERIoT or not, passes through it (rv32_lsu_* inputs
from ID are forwarded to lsu_* outputs, rtl/ibex_core.sv:960-979). Because cheriot_enable_i is tied
Off in this DUT, the capability paths are quiescent (the RTL asserts elsewhere that cheriot_*
requests stay low when cheriot_enable_i != IbexMuBiOn, e.g. rtl/ibex_id_stage.sv:1297-1300), but
the module is in the netlist and on the LSU request path. Doc: no doc section (grep of doc/ for
"cheriot" returns nothing).

Parameters as instantiated (rtl/ibex_core.sv:913): WritebackStage=1.

Ports:
Inputs: clk_i, rst_ni, cheriot_enable_i [4], debug_mode_i, fwd_we_i, fwd_waddr_i [5], fwd_wdata_i
[32], fwd_wcap_i cap_t, rf_raddr_a_i [5], rf_rdata_a_i [32], rf_rcap_a_i cap_t, rf_raddr_b_i [5],
rf_rdata_b_i [32], rf_rcap_b_i cap_t, rf_waddr_i [5], pcc_cap_i decoded_cap_t, pc_id_i [32],
cheriot_exec_id_i, instr_first_cycle_i, instr_valid_i (KEY valid), instr_is_cheriot_i,
instr_is_rv32lsu_i, instr_is_compressed_i, cheriot_imm12_i [12], cheriot_imm20_i [20],
cheriot_imm21_i [21], cheriot_cs2_dec_i [5], cheriot_operator_i cheriot_op_t,
cheriot_cap_field_sel_i, cheriot_adder_a_sel_i, cheriot_adder_b_sel_i, cheriot_setaddr_sel_i,
cheriot_setbounds_sel_i, addr_incr_req_i, addr_last_i [32], rv32_lsu_req_i (KEY), rv32_lsu_we_i,
rv32_lsu_type_i [2], rv32_lsu_wdata_i [32], rv32_lsu_sign_ext_i, rv32_lsu_addr_i [32], csr_rdata_i
[32], csr_rcap_i cap_t, csr_mstatus_mie_i, csr_mshwm_i [32], csr_mshwmb_i [32], ztop_rdata_i [32]
(tied 32'h0), ztop_rcap_i cap_t (tied NULL_CAP), csr_dbg_tclr_fault_i.
Outputs: pcc_cap_o decoded_cap_t, branch_req_o, branch_req_spec_o, branch_target_o [32],
cheriot_rf_we_o, result_data_o [32], result_cap_o cap_t, cheriot_ex_valid_o (KEY valid),
cheriot_ex_err_o (KEY exception), cheriot_ex_err_info_o [12], cheriot_wb_err_o (KEY exception),
cheriot_wb_err_info_o [16], lsu_req_o (KEY valid), lsu_cheriot_err_o, lsu_is_cap_o,
lsu_lc_clrperm_o cap_clrperm_t, lsu_we_o, lsu_addr_o [32], lsu_type_o [2], lsu_wdata_o [32],
lsu_wcap_o cap_t, lsu_sign_ext_o, rv32_addr_incr_req_o, rv32_addr_last_o [32], csr_access_o,
csr_addr_o [5], csr_wdata_o [32], csr_wcap_o cap_t, csr_op_o cheriot_csr_op_e, csr_op_en_o,
csr_set_mie_o, csr_clr_mie_o, csr_mshwm_set_o, csr_mshwm_new_o [32].

### 4.14 ibex_load_store_unit  (rtl/ibex_load_store_unit.sv:18-82)

Instance path: ibex_core.load_store_unit_i (rtl/ibex_core.sv:1066-1070). Generate: none.

Function: Data memory interface. An FSM (ls_fsm_e: IDLE, WAIT_GNT_MIS, WAIT_RVALID_MIS, WAIT_GNT,
WAIT_RVALID_MIS_GNTS_DONE, CTX_WAIT_GNT1/2, :433-565) issues word-aligned requests (data_addr_o =
{addr[31:2],2'b00}, :719-722), splits misaligned halfword/word accesses into two transactions
(addr_incr_req_o asks the ALU for addr+4), assembles/sign-extends read data and generates byte
enables. With MemECC it encodes write data with prim_secded_inv_39_32_enc (:731-735) and checks
39-bit responses through prim_buf + prim_secded_inv_39_32_dec (:376-393), asserting
load/store_resp_intg_err_o. Bus errors and PMP errors (data_pmp_err_i) become load_err_o /
store_err_o (:745 region); lsu_resp_valid_o/lsu_req_done_o handshake with ID/WB and
lsu_rdata_valid_o (:697) gates the WB register write. The gen_memcap_rd branch (:701-709) adds the
capability-load path used only when CHERIoT is enabled. Doc: doc/03_reference/load_store_unit.rst
"Load-Store Unit" (:3-10) and "Bus Integrity Checking" (:57-69).

Parameters as instantiated (rtl/ibex_core.sv:1067-1069): MemECC=1, MemDataWidth=39,
BaseIsa=BaseIsaRV32IorCHERIoT.

Ports:
Inputs: clk_i, rst_ni, cheriot_enable_i [4], data_gnt_i (KEY ready), data_rvalid_i (KEY valid),
data_bus_err_i (KEY error), data_pmp_err_i (KEY error), data_rdata_i [39], data_tag_i, lsu_we_i,
lsu_is_cap_i, lsu_cheriot_err_i, lsu_type_i [2], lsu_wdata_i [32], lsu_wcap_i cap_t,
lsu_lc_clrperm_i cap_clrperm_t, lsu_sign_ext_i, lsu_req_i (KEY valid), adder_result_ex_i [32].
Outputs: data_req_o (KEY valid), data_addr_o [32], data_we_o, data_be_o [4], data_wdata_o [39],
data_tag_o, lsu_rcap_o cap_t, lsu_rdata_o [32], lsu_rdata_valid_o (KEY), addr_incr_req_o,
addr_last_o [32], lsu_req_done_o (KEY), lsu_resp_valid_o (KEY valid), load_err_o (KEY exception),
load_resp_intg_err_o (KEY error), store_err_o (KEY exception), store_resp_intg_err_o (KEY error),
lsu_err_is_cheriot_o, busy_o, perf_load_o, perf_store_o.

### 4.15 ibex_wb_stage  (rtl/ibex_wb_stage.sv:18-73)

Instance path: ibex_core.wb_stage_i (rtl/ibex_core.sv:1125-1129). Generate: none (the module body
is almost entirely inside g_writeback_stage :84, WritebackStage = 1).

Function: Third (writeback) pipeline stage. It registers the instruction that leaves ID/EX (en_wb_i,
instr_type_wb_i, pc, rf write address/data/enable; reset-all flops in g_wb_regs_ra :126) and
completes it: for loads it waits for lsu_resp_valid_i and substitutes rf_wdata_lsu_i, for stores it
waits for the response, otherwise it writes back immediately. It reports ready_wb_o to ID,
outstanding_load_wb_o/outstanding_store_wb_o for hazard and response tracking, rf_write_wb_o and
rf_wdata_fwd_wb_o for the ID forwarding path, and instr_done_wb_o plus the perf_instr_ret_* pulses
for counters and RVFI. It also carries the dummy-instruction flag (g_dummy_instr_wb :222) and the
CHERIoT capability write data (cheriot_rf_*, rf_wcap_*). Doc: doc/03_reference/
pipeline_details.rst "Third Pipeline Stage" (:26-30; states that details are not yet documented).

Parameters as instantiated (rtl/ibex_core.sv:1126-1128): ResetAll=1, WritebackStage=1,
DummyInstructions=1.

Ports:
Inputs: clk_i, rst_ni, en_wb_i (KEY valid), instr_type_wb_i wb_instr_type_e, pc_id_i [32],
instr_is_compressed_id_i, instr_perf_count_id_i, instr_is_cheriot_i, cheriot_load_i,
cheriot_store_i, rf_waddr_id_i [5], rf_wdata_id_i [32], rf_we_id_i, cheriot_rf_we_i,
cheriot_rf_wdata_i [32], cheriot_rf_wcap_i cap_t, dummy_instr_id_i, rf_wdata_lsu_i [32],
rf_wcap_lsu_i cap_t, rf_we_lsu_i, lsu_resp_valid_i (KEY valid), lsu_resp_err_i (KEY error).
Outputs: ready_wb_o (KEY ready), rf_write_wb_o, outstanding_load_wb_o, outstanding_store_wb_o,
pc_wb_o [32], perf_instr_ret_wb_o, perf_instr_ret_compressed_wb_o, perf_instr_ret_wb_spec_o,
perf_instr_ret_compressed_wb_spec_o, rf_wdata_fwd_wb_o [32], rf_wcap_fwd_wb_o cap_t, rf_waddr_wb_o
[5], rf_wdata_wb_o [32], rf_wcap_wb_o cap_t, rf_we_wb_o, dummy_instr_wb_o, instr_done_wb_o.

### 4.16 ibex_cs_registers  (rtl/ibex_cs_registers.sv:13-160)

Instance path: ibex_core.cs_registers_i (rtl/ibex_core.sv:1431-1452). Generate: none.

Function: All control and status registers. It decodes csr_addr_i/csr_op_i into read data
(available the same cycle) and per-register write enables, holds mstatus/mie/mtvec/mepc/mcause/
mtval/mscratch, the debug CSRs (dcsr, dpc, dscratch0/1, and with DbgTriggerEn the tselect/tdata1/
tdata2 trigger registers that produce trigger_match_o), the interrupt qualification (irqs_o,
irq_pending_o from mie and the irq_* inputs), privilege-mode tracking (priv_mode_id_o/lsu_o), the
16 pmpcfg/pmpaddr registers plus mseccfg (g_pmp_registers :1362-1531, exported as csr_pmp_cfg_o/
addr_o/mseccfg_o), the mcycle/minstret 64-bit counters and ten 32-bit mhpmcounters with their
event selectors and mcountinhibit/mcounteren (:1574-1750), the custom cpuctrlsts register
(data_ind_timing_o, dummy_instr_en_o/mask_o, icache_enable_o, double_fault_seen_o) and the
secureseed path (dummy_instr_seed_en_o/seed_o), and the CHERIoT SCRs/mshwm registers (g_mshwm,
gen_scr). csr_shadow_err_o ORs the rd_error_o of shadowed CSRs; with ShadowCSR = 0 every
ibex_csr has ShadowCopy = 0 so this is constant 0. Doc: doc/03_reference/cs_registers.rst
"Control and Status Registers" (:3-6 and per-CSR sections), instruction_decode_execute.rst
"Control and Status Register Block (CSR)" (:156-164), performance_counters.rst (:3-14, :79-92),
debug.rst "Parameters" (:29-46), pmp.rst (:3-19).

Parameters as instantiated (rtl/ibex_core.sv:1432-1451): DbgTriggerEn=1, DbgHwBreakNum=1,
DataIndTiming=1, DummyInstructions=1, ShadowCSR=0, ICache=1, MHPMCounterNum=10,
MHPMCounterWidth=32, PMPEnable=1, PMPGranularity=0, PMPNumRegions=16, PMPRstCfg/PMPRstAddr/
PMPRstMsecCfg = ibex_pkg defaults, RV32E=0, RV32M=RV32MSingleCycle, RV32B=RV32BOTEarlGrey,
CsrMvendorId=0, CsrMimpId=0, BaseIsa=BaseIsaRV32IorCHERIoT. Internal localparams (:179-185):
RV32BExtra=1, RV32MEnabled=1, MisaXBit=1, PMPAddrWidth=32, MHPMCOUNTER_BASE=3.

Ports:
Inputs:
- clk_i, rst_ni, cheriot_enable_i [4], hart_id_i [32], csr_mtvec_init_i, boot_addr_i [32]
- csr_access_i, csr_addr_i csr_num_e, csr_wdata_i [32], csr_op_i csr_op_e, csr_op_en_i (KEY: write commit)
- cheriot_csr_access_i, cheriot_csr_addr_i [5], cheriot_csr_wdata_i [32], cheriot_csr_wcap_i cap_t, cheriot_csr_op_i cheriot_csr_op_e, cheriot_csr_op_en_i, cheriot_csr_set_mie_i, cheriot_csr_clr_mie_i, csr_mshwm_set_i, csr_mshwm_new_i [32]
- irq_software_i, irq_timer_i, irq_external_i, irq_fast_i [15], nmi_mode_i
- debug_mode_i, debug_mode_entering_i, debug_cause_i dbg_cause_e, debug_csr_save_i
- pc_if_i [32], pc_id_i [32], pc_wb_i [32], ic_scr_key_valid_i, mcounteren_writable_i [4]
- csr_save_if_i, csr_save_id_i, csr_save_wb_i, csr_restore_mret_i, csr_restore_dret_i, csr_save_cause_i (KEY exception commit), csr_mepcc_clrtag_i, csr_mcause_i exc_cause_t, csr_mtval_i [32]
- instr_ret_i, instr_ret_compressed_i, instr_ret_spec_i, instr_ret_compressed_spec_i, iside_wait_i, jump_i, branch_i, branch_taken_i, mem_load_i, mem_store_i, dside_wait_i, mul_wait_i, div_wait_i
- cheriot_branch_req_i, cheriot_branch_target_i [32], pcc_cap_i decoded_cap_t
Outputs:
- priv_mode_id_o priv_lvl_e, priv_mode_lsu_o priv_lvl_e, csr_mstatus_tw_o, csr_mtvec_o [32], csr_rdata_o [32]
- cheriot_csr_rdata_o [32], cheriot_csr_rcap_o cap_t, csr_mshwm_o [32], csr_mshwmb_o [32]
- irq_pending_o (KEY), irqs_o irqs_t, csr_mstatus_mie_o, csr_mepc_o [32], csr_mtval_o [32]
- csr_pmp_cfg_o pmp_cfg_t [16], csr_pmp_addr_o [34] [16], csr_pmp_mseccfg_o pmp_mseccfg_t
- csr_depc_o [32], debug_single_step_o, debug_ebreakm_o, debug_ebreaku_o, trigger_match_o (KEY)
- data_ind_timing_o, dummy_instr_en_o, dummy_instr_mask_o [3], dummy_instr_seed_en_o, dummy_instr_seed_o [32], icache_enable_o, csr_shadow_err_o (KEY error)
- illegal_csr_insn_o (KEY exception), double_fault_seen_o (KEY)
- pcc_cap_o decoded_cap_t, csr_dbg_tclr_fault_o, cheriot_fatal_err_o (KEY error)

### 4.17 ibex_csr  (rtl/ibex_csr.sv:11-24)

Instance paths: 56 instances under ibex_core.cs_registers_i (list in section 2). Generate: as listed
(top level; g_mshwm; g_pmp_registers.g_pmp_csrs[i]; gen_trigger_regs; gen_trigger_regs
.g_dbg_tmatch_reg[0]; gen_icache_enable).

Function: Generic CSR storage flop: rdata_q loads wr_data_i on wr_en_i and resets to ResetValue
(:28-36). With ShadowCopy a complemented shadow register is kept and rd_error_o flags a mismatch
(gen_shadow :38-50); with ShadowCopy = 0 (all instances here) rd_error_o is constant 0 (:51-53).
One assertion checks wr_en_i is never X (:55). Doc: security.rst "Shadow CSRs" (:128-134) for the
shadow feature; otherwise no doc section.

Parameters as instantiated (rtl/ibex_cs_registers.sv, ShadowCopy is ShadowCSR = 0 or literal 0
everywhere): u_mstatus_csr Width=$bits(status_t), ResetValue=MSTATUS_RST_VAL (:1072-1076);
u_mepc_csr 32/'0 (:1089); u_mie_csr $bits(irqs_t)/'0 (:1107); u_mscratch_csr 32/'0 (:1121);
u_mcause_csr $bits(exc_cause_t)/'0 (:1135); u_mtval_csr 32/'0 (:1149); u_mtvec_csr 32/32'd1
(:1170-1173); u_dcsr_csr $bits(dcsr_t)/DCSR_RESET_VAL (:1190); u_depc_csr 32/'0 (:1207);
u_dscratch0_csr, u_dscratch1_csr 32/'0 (:1225, :1243); u_mstack_csr $bits(status_stk_t)/
MSTACK_RESET_VAL (:1258); u_mstack_epc_csr 32/'0 (:1272); u_mstack_cause_csr $bits(exc_cause_t)/'0
(:1286); u_mshwm_csr, u_mshwmb_csr, u_cdbg_ctrl_csr 32/'0 (:1305-1336); u_pmp_cfg_csr[i]
$bits(pmp_cfg_t)/PMPRstCfg[i] (:1448-1452); u_pmp_addr_csr[i] Width=PMPAddrWidth=32/
PMPRstAddr[i][33-:32] (:1483-1487); u_pmp_mseccfg $bits(pmp_mseccfg_t)/PMPRstMsecCfg (:1516-1520);
u_mcounteren_csr Width=MHPMCounterNum+3=13/'0 (:1737-1741); u_tselect_csr Width=DbgHwNumLen=1/'0
(:1755, :1793-1797); u_tmatch_control_csr 1/'0 (:1807-1811); u_tmatch_value_csr 32/'0
(:1820-1824); u_cpuctrlsts_ic_scr_key_valid_q_csr 1/1'b0 (:1938-1942); u_cpuctrlsts_part_csr
$bits(cpu_ctrl_sts_part_t)/'0 (:1973-1977).

Ports: Inputs: clk_i, rst_ni, wr_data_i [Width], wr_en_i (KEY write). Outputs: rd_data_o [Width],
rd_error_o (KEY error, constant 0 here).

### 4.18 ibex_counter  (rtl/ibex_counter.sv:5-21)

Instance paths: ibex_core.cs_registers_i.mcycle_counter_i, .minstret_counter_i,
.gen_cntrs[0..9].gen_imp.mcounters_variable_i (rtl/ibex_cs_registers.sv:1622, :1637, :1673).
Generate: gen_cntrs[i].gen_imp, condition `if (i < MHPMCounterNum)` for i = 0..9.

Function: Parametric-width up counter with 32-bit low/high software write ports: counter_upd =
counter + 1 (:30); on counter_we_i/counterh_we_i the selected half is loaded from counter_val_i,
otherwise counter_inc_i increments (:33-51); counter_q uses an async-reset flop in g_cnt_no_dsp
(:74-83; the DSP variant exists only under FPGA_XILINX :53-58). Widths below 64 are zero-extended
(g_counter_narrow :86-98) and counter_val_upd_o exposes the incremented value only when
ProvideValUpd is set (used for minstret and mhpmcounter10, the compressed-instruction counter, so
reads can be corrected speculatively at rtl/ibex_cs_registers.sv:1687-1692). Doc:
doc/03_reference/performance_counters.rst "Performance Counters" (:3-14) and "Parametrization at
synthesis time" (:79-92).

Parameters as instantiated: mcycle_counter_i CounterWidth=64, ProvideValUpd=0 default
(rtl/ibex_cs_registers.sv:1622-1624); minstret_counter_i CounterWidth=64, ProvideValUpd=1
(:1637-1640); mcounters_variable_i CounterWidth=MHPMCounterWidth=32, ProvideValUpd=(Cnt==10), i.e.
1 only for gen_cntrs[7] (Cnt = i + 3, :1668, :1673-1676).

Ports: Inputs: clk_i, rst_ni, counter_inc_i, counterh_we_i, counter_we_i, counter_val_i [32].
Outputs: counter_val_o [64], counter_val_upd_o [64].

### 4.19 ibex_pmp  (rtl/ibex_pmp.sv:7-31)

Instance path: ibex_core.g_pmp.pmp_i (rtl/ibex_core.sv:1580, :1606-1612). Generate: g_pmp,
condition `if (PMPEnable)`.

Function: Physical Memory Protection checker for three channels (PMP_I = fetch PC, PMP_I2 = PC+2
for the second half of a misaligned 32-bit fetch, PMP_D = data; rtl/ibex_core.sv:1587-1604). For
each channel and each of the 16 regions it computes region match according to pmpcfg mode
(OFF/TOR/NA4/NAPOT with the NAPOT mask built in g_addr_exp/g_bitmask, :157-186; NA4 is available
because PMPGranularity = 0), then applies the Smepmp permission rules including mseccfg MML/MMWP/
RLB and lock bits and the debug-module address window (DmBaseAddr/DmAddrMask, debug_mode_i) to
produce pmp_req_err_o per channel (g_access_check :188). In ibex_core the PMP_D error gates
data_req_o (rtl/ibex_core.sv:1063) and all three errors are zeroed when CHERIoT is active
(g_pmp_cheriot_gate, :1626-1630; inactive here). Doc: doc/03_reference/pmp.rst "Physical Memory
Protection (PMP)" (:3-19), "PMP Integration" (:21-32), "PMP Granularity" (:34-38).

Parameters as instantiated (rtl/ibex_core.sv:1607-1611): DmBaseAddr=32'h1A110000,
DmAddrMask=32'h00000FFF, PMPGranularity=0, PMPNumChan=3, PMPNumRegions=16.

Ports: Inputs: csr_pmp_cfg_i pmp_cfg_t [16], csr_pmp_addr_i [34] [16], csr_pmp_mseccfg_i
pmp_mseccfg_t, debug_mode_i, priv_mode_i priv_lvl_e [3], pmp_req_addr_i [34] [3], pmp_req_type_i
pmp_req_e [3]. Outputs: pmp_req_err_o [1] [3] (KEY error). Purely combinational (no clock/reset
ports).

### 4.20 prim_buf  (vendor/lowrisc_ip/ip/prim_generic/rtl/prim_buf.sv:7-12)

Instance paths and Width: ibex_core.g_core_busy_secure.u_fetch_enable_buf, Width=NumBusyBits=12
(rtl/ibex_core.sv:501-506; $bits(ibex_mubi_t)=4 times 3 busy signals); ibex_core.if_stage_i
.g_mem_ecc.u_prim_buf_instr_rdata, Width=MemDataWidth=39 (rtl/ibex_if_stage.sv:263);
ibex_core.if_stage_i.g_secure_pc.u_prev_instr_addr_incr_buf, Width=32 (rtl/ibex_if_stage.sv:682);
ibex_core.load_store_unit_i.g_mem_rdata_ecc.u_prim_buf_instr_rdata, Width=39
(rtl/ibex_load_store_unit.sv:380). Generate conditions: SecureIbex, MemECC, PCIncrCheck, MemECC.

Function: Technology-independent buffer: out_o = ~(~in_i) (:14-16). Its only purpose is to create a
named hierarchy boundary so synthesis cannot merge the redundant copies of a signal that the
security countermeasures rely on (comment at rtl/ibex_if_stage.sv:681). Resolution: the fusesoc
virtual core lowrisc:prim:buf is provided by lowrisc:prim_generic:buf
(vendor/lowrisc_ip/ip/prim_generic/prim_generic_buf.core:6-14, `virtual: - lowrisc:prim:buf`), and
lowrisc:prim_generic:all maps "lowrisc:prim:buf" to it (prim_generic.core:41). There is no other
prim_buf.sv in the clone's prim trees (vendor/lowrisc_ip/ip/prim/rtl has no prim_buf.sv). Doc: no
doc section.

Ports: Inputs: in_i [Width]. Outputs: out_o [Width]. Combinational only.

### 4.21 prim_secded_inv_39_32_enc  (vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_39_32_enc.sv:7-10)

Instance paths: ibex_core.if_stage_i.gen_icache.icache_i.gen_ecc_wdata.gen_ecc_banks[0..1]
.data_ecc_enc (rtl/ibex_icache.sv:305-306); ibex_core.load_store_unit_i.g_mem_wdata_ecc.u_data_gen
(rtl/ibex_load_store_unit.sv:732). Generate conditions: ICacheECC; MemECC.

Function: Generated (util/design/secded_gen.py) Hsiao SECDED encoder: seven parity bits computed
from fixed 39-bit masks over data_i (:14-20), then the whole 39-bit word is XORed with
39'h2A00000000 so that an all-zero word is not a valid codeword (:21). No parameters. Doc:
doc/03_reference/load_store_unit.rst "Bus Integrity Checking" (:57-66) and icache.rst "Cache ECC
protection" (:189-212).

Ports: Inputs: data_i [32]. Outputs: data_o [39]. Combinational only.

### 4.22 prim_secded_inv_39_32_dec  (vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_39_32_dec.sv:7-12)

Instance paths: ibex_core.if_stage_i.g_mem_ecc.u_instr_intg_dec (rtl/ibex_if_stage.sv:268);
ibex_core.load_store_unit_i.g_mem_rdata_ecc.u_data_intg_dec (rtl/ibex_load_store_unit.sv:385);
ibex_core.if_stage_i.gen_icache.icache_i.gen_data_ecc_checking.gen_ecc_banks[0..1].data_ecc_dec
(rtl/ibex_icache.sv:567-568). Generate conditions: MemECC; MemECC; ICacheECC.

Function: Matching decoder: syndrome_o is the parity of (data_i ^ 39'h2A00000000) under seven masks
(:16-22), data_o is the single-bit-corrected data (:25-56), err_o[0] = odd syndrome (single-bit
error), err_o[1] = even non-zero syndrome (double-bit error) (:59-60). Ibex uses only err_o: the
IF stage and LSU OR both bits into instr_intg_err / data_intg_err (rtl/ibex_if_stage.sv:276,
rtl/ibex_load_store_unit.sv:393) and the icache into data_err_ic1 (rtl/ibex_icache.sv:572);
data_o/syndrome_o are left unconnected. No parameters. Doc: as 4.21.

Ports: Inputs: data_i [39]. Outputs: data_o [32], syndrome_o [7], err_o [2] (KEY error).
Combinational only.

### 4.23 prim_secded_inv_28_22_enc  (vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_28_22_enc.sv:7-10)

Instance path: ibex_core.if_stage_i.gen_icache.icache_i.gen_ecc_wdata.tag_ecc_enc
(rtl/ibex_icache.sv:297-300). Generate condition: ICacheECC.

Function: Hsiao SECDED encoder for the icache tag RAM: six parity bits over a 22-bit input (:14-19)
and inversion mask 28'hA800000 (:20). The icache zero-pads the 22-bit tag (IC_TAG_SIZE = 22 here so
the pad is empty, rtl/ibex_icache.sv:294) and stores {parity[27:22], tag[21:0]} (:302). No
parameters. Doc: icache.rst "Cache ECC protection" (:194-200).

Ports: Inputs: data_i [22]. Outputs: data_o [28]. Combinational only.

### 4.24 prim_secded_inv_28_22_dec  (vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_28_22_dec.sv:7-12)

Instance paths: ibex_core.if_stage_i.gen_icache.icache_i.gen_data_ecc_checking.gen_tag_ecc[0..1]
.data_ecc_dec (rtl/ibex_icache.sv:547-556; note the instance is named data_ecc_dec although it
decodes the tag). Generate condition: ICacheECC.

Function: Tag decoder: 6-bit syndrome over (data_i ^ 28'hA800000) (:16-21), corrected data_o
(:24-45), err_o[0] single / err_o[1] double error (:48-49). The icache ORs err_o into
tag_err_ic1[way] (rtl/ibex_icache.sv:562); tag errors invalidate all ways (:591). No parameters.
Doc: as 4.23.

Ports: Inputs: data_i [28]. Outputs: data_o [22], syndrome_o [6], err_o [2] (KEY error).
Combinational only.

### 4.25 ibex_register_file_ff  (rtl/ibex_register_file_ff.sv:51-86)  -- wrapper sibling of ibex_core

Instance path: <wrapper>.register_file_i if the wrapper mirrors ibex_top.sv:532-540 (name
unverified). Generate: in ibex_top it sits in gen_regfile_ff, condition `RegFile == RegFileFF`.

Function: Flip-flop register file with two read ports and one write port; data is available the
same cycle a read is requested and there is no write-to-read forwarding. Under BaseIsa ==
BaseIsaRV32IorCHERIoT the g_cheriot_rf branch (:88-240) builds two 16-entry banks: rf_data[16]
holds x0-x15 and rf_shared[16] (CapWidth = 35 wide) holds either the capability metadata for
x0-x15 (CHERIoT mode) or the data of x16-x31 (non-CHERIoT, the mode used here; :97-113). With
DummyInstructions the g_dummy_r0 branch (:153-186) adds a real x0 flop that is written only by
dummy instructions (dummy_instr_wb_i) and read only when dummy_instr_id_i is set, so dummy
instructions have an operand/destination without touching architectural state. rcap_a_o/rcap_b_o
return the shared bank (only meaningful in CHERIoT mode). Doc: doc/03_reference/register_file.rst
"Register File" (:3-11) and "Flip-Flop-Based Register File" (:16-24); security.rst "Dummy
Instruction Insertion" (:41-46).

Parameters (mirroring rtl/ibex_top.sv:534-539): BaseIsa=BaseIsaRV32IorCHERIoT, RV32E=0,
DataWidth=32, DummyInstructions=1, WordZeroVal=32'(SecdedInv3932ZeroWord)=32'h0, CapWidth=35 and
CapWordZeroVal='0 (defaults, :58-59).

Ports: Inputs: clk_i, rst_ni, test_en_i (unused in FF flavour), dummy_instr_id_i, dummy_instr_wb_i,
cheriot_enable_i [4], raddr_a_i [5], raddr_b_i [5], waddr_a_i [5], wdata_a_i [32], wcap_a_i [35],
we_a_i (KEY write). Outputs: rdata_a_o [32], rcap_a_o [35], rdata_b_o [32], rcap_b_o [35].

### 4.26 Modules compiled from the file list but not in the elaborated hierarchy (for scope only)

- ibex_prefetch_buffer (rtl/ibex_prefetch_buffer.sv:12-42): linear prefetcher with up to NUM_REQS
  outstanding requests, contains ibex_fetch_fifo (:90). Only under gen_prefetch_buffer (!ICache).
  Doc: instruction_fetch.rst :15-21.
- ibex_fetch_fifo (rtl/ibex_fetch_fifo.sv:15-42): 3-deep instruction FIFO with feedthrough and
  misaligned-halfword handling. Only inside ibex_prefetch_buffer. Doc: instruction_fetch.rst :17-19.
- ibex_branch_predict (rtl/ibex_branch_predict.sv:20-32): static backward-taken predictor. Only
  under g_branch_predictor (BranchPredictor = 0). Doc: instruction_fetch.rst :31-39.
- ibex_multdiv_slow (rtl/ibex_multdiv_slow.sv:14-43): Baugh-Wooley iterative multiplier. Only under
  gen_multdiv_slow (RV32M == RV32MSlow). Doc: instruction_decode_execute.rst :140-144.
- prim_secded_inv_64_57_enc/dec: only under gen_regfile_ecc.gen_cheriot_cap_ecc (RegFileECC = 0).
- prim_clock_gating (vendor/lowrisc_ip/ip/prim_generic/rtl/prim_clock_gating.sv:10-18): latch-based
  clock gate; dependency of ibex_core.core:12 but instantiated only by ibex_top.sv:333 and
  ibex_register_file_latch.sv. Resolves the same way as prim_buf (prim_generic_clock_gating.core:6-14
  is virtual lowrisc:prim:clock_gating; prim_generic.core:44 maps it).

## 5. (a) prim_* modules inside the DUT hierarchy

| prim module | Source | Instance path(s) | Purpose | Combinational-only |
|---|---|---|---|---|
| prim_buf (Width 12) | prim_generic/rtl/prim_buf.sv | ibex_core.g_core_busy_secure.u_fetch_enable_buf | Isolate 3 x 4 redundant busy bits for core_busy_o multibit | yes |
| prim_buf (Width 39) | prim_generic/rtl/prim_buf.sv | ibex_core.if_stage_i.g_mem_ecc.u_prim_buf_instr_rdata | Keep instruction bus word intact for integrity check | yes |
| prim_buf (Width 32) | prim_generic/rtl/prim_buf.sv | ibex_core.if_stage_i.g_secure_pc.u_prev_instr_addr_incr_buf | Keep expected next-PC value for hardened PC check | yes |
| prim_buf (Width 39) | prim_generic/rtl/prim_buf.sv | ibex_core.load_store_unit_i.g_mem_rdata_ecc.u_prim_buf_instr_rdata | Keep data bus word intact for integrity check | yes |
| prim_secded_inv_39_32_dec | prim/rtl/prim_secded_inv_39_32_dec.sv | ibex_core.if_stage_i.g_mem_ecc.u_instr_intg_dec | Instruction bus integrity check -> instr_intg_err / alert_major_bus_o | yes |
| prim_secded_inv_39_32_dec | same | ibex_core.load_store_unit_i.g_mem_rdata_ecc.u_data_intg_dec | Data bus integrity check -> load/store_resp_intg_err | yes |
| prim_secded_inv_39_32_enc | prim/rtl/prim_secded_inv_39_32_enc.sv | ibex_core.load_store_unit_i.g_mem_wdata_ecc.u_data_gen | Generate data_wdata_o[38:32] integrity bits | yes |
| prim_secded_inv_28_22_enc | prim/rtl/prim_secded_inv_28_22_enc.sv | ibex_core.if_stage_i.gen_icache.icache_i.gen_ecc_wdata.tag_ecc_enc | Tag RAM ECC generation | yes |
| prim_secded_inv_39_32_enc x2 | same as above | ...icache_i.gen_ecc_wdata.gen_ecc_banks[0..1].data_ecc_enc | Data RAM ECC generation per 32-bit beat | yes |
| prim_secded_inv_28_22_dec x2 | prim/rtl/prim_secded_inv_28_22_dec.sv | ...icache_i.gen_data_ecc_checking.gen_tag_ecc[0..1].data_ecc_dec | Tag RAM ECC check per way -> tag_err_ic1 | yes |
| prim_secded_inv_39_32_dec x2 | same as above | ...icache_i.gen_data_ecc_checking.gen_ecc_banks[0..1].data_ecc_dec | Data RAM ECC check per beat -> data_err_ic1 | yes |
| prim_lfsr | prim/rtl/prim_lfsr.sv | ibex_core.if_stage_i.gen_dummy_instr.dummy_instr_i.lfsr_i | Pseudo-random interval/operands for dummy instructions | no (32-bit state flop :485-491, plus SVA-only counter in gen_max_len_sva :616) |

Not in the hierarchy but pulled in by ibex_core.core dependencies: prim_clock_gating (sequential,
latch), prim_mubi* (prim:mubi), prim_secded_pkg, prim_cipher_pkg, prim_mubi_pkg, prim_util_pkg.

## 6. (b) `include files needed by the RTL

| Include | Included by | Location in clone | Notes |
|---|---|---|---|
| prim_assert.sv | rtl/ibex_core.sv:11, ibex_if_stage.sv:14, ibex_id_stage.sv:18, ibex_controller.sv:11, ibex_decoder.sv:15, ibex_compressed_decoder.sv:15, ibex_load_store_unit.sv:15, ibex_wb_stage.sv:15, ibex_cs_registers.sv:11, ibex_csr.sv:9, ibex_multdiv_fast.sv:15, ibex_multdiv_slow.sv:12, ibex_icache.sv:11, ibex_fetch_fifo.sv:13, ibex_branch_predict.sv:18, ibex_register_file_ff.sv:49 (and fpga/latch :34), ibex_top.sv:10, ibex_trvk.sv:5; prim_lfsr.sv:27, prim_buf.sv:5 | vendor/lowrisc_ip/ip/prim/rtl/prim_assert.sv | Itself includes prim_assert_dummy_macros.svh (VERILATOR or SYNTHESIS), prim_assert_yosys_macros.svh (YOSYS) or prim_assert_standard_macros.svh (default, defines INC_ASSERT) at :102-112, then prim_assert_sec_cm.svh and prim_flop_macros.sv at :187-188. All live in vendor/lowrisc_ip/ip/prim/rtl/ and are listed as include files in prim_assert.core:11-16. Default clock/reset for the macros: clk_i / !rst_ni (:17-18). ASSERT_ERROR uses uvm_report_error under `ifdef UVM else $error (:27-34). |
| dv_fcov_macros.svh | rtl/ibex_core.sv:12, ibex_if_stage.sv:15, ibex_id_stage.sv:19, ibex_controller.sv:12, ibex_load_store_unit.sv:16, ibex_wb_stage.sv:16, ibex_pmp.sv:5 | vendor/lowrisc_ip/dv/sv/dv_utils/dv_fcov_macros.svh (path as stated by the task; the fusesoc core is lowrisc:dv:dv_fcov_macros per ibex_core.core:17). This directory is outside the fence and was NOT read. | Fact: the RTL of the DUT cannot compile without this header even though vendor/lowrisc_ip/dv is not a DV library the team builds on; the include path must be provided. Macros used by the RTL: `DV_FCOV_SIGNAL(type, name, expr)` (rtl/ibex_core.sv:2457-2486, ibex_controller.sv:1085-1095, ibex_id_stage.sv:1235-1237, ibex_load_store_unit.sv:802-810, ibex_pmp.sv:255) and `DV_FCOV_SIGNAL_GEN_IF(type, name, hier_expr, gen_cond)` (rtl/ibex_core.sv:2449-2450, ibex_wb_stage.sv:308, ibex_id_stage.sv:1233, ibex_if_stage.sv:818-820). From usage, DV_FCOV_SIGNAL(logic, csr_write, ...) at ibex_core.sv:2459 creates a signal referenced as fcov_csr_write at ibex_core.sv:2483, so the macro declares `<type> fcov_<name>` and assigns it the expression; DV_FCOV_SIGNAL_GEN_IF evidently does the same only when the generate condition is true (the hierarchical reference gen_regfile_ecc.rf_ecc_err_a_id at :2449 would not resolve otherwise). The macro bodies and their behaviour when DV_FCOV_SIGNAL / DV_FCOV_DISABLE are not defined are UNVERIFIED (file not readable under the fence). The RTL itself only uses `ifndef DV_FCOV_DISABLE once (rtl/ibex_load_store_unit.sv:767-800) around plain fcov_* logic, and wraps the core FCOV block in `ifndef SYNTHESIS (rtl/ibex_core.sv:2447-2512). |
| formal_tb_frag.svh | rtl/ibex_icache.sv:1333, ibex_multdiv_fast.sv:552, ibex_multdiv_slow.sv:386 | not found under rtl/, vendor/lowrisc_ip/ip/, util/ or doc/ (find returned nothing) | Guarded by `ifdef FORMAL / `ifdef YOSYS (ibex_icache.sv:1322-1335, ibex_multdiv_fast.sv:550-553, ibex_multdiv_slow.sv:384-387); not needed for a VCS build. Location unverified. |
| prim_secded_inc.svh | none of the DUT RTL (listed as include file in prim_secded.core:48) | vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inc.svh | Not required by the instantiated secded modules (they have no `include). |

## 7. (c) SVA assertion macro count per module (grep of `ASSERT* invocations in the source)

| Module | File | `ASSERT | `ASSERT_IF | `ASSERT_KNOWN | `ASSERT_KNOWN_IF | `ASSERT_INIT | `ASSERT_I | Total lines | Notes |
|---|---|---|---|---|---|---|---|---|---|
| ibex_core | rtl/ibex_core.sv | 5 | 0 | 0 | 1 | 3 | 0 | 9 (10 grep hits incl. commented-out :2441) | :1380 and :1387 are in exclusive generate branches (WritebackStage), only :1380 elaborates; :1356-1423 block is `ifdef INC_ASSERT |
| ibex_if_stage | rtl/ibex_if_stage.sv | 9 | 2 | 1 | 0 | 0 | 0 | 12 | :797-798, :832, :906-922 are inside g_branch_predictor / g_branch_predictor_asserts (N); elaborated: :296, :829, :922 (g_no_branch_predictor_asserts IbexPcMuxValid), :932, :935, :938 |
| ibex_icache | rtl/ibex_icache.sv | 0 | 0 | 2 | 0 | 3 | 0 | 5 | :1310-1318 |
| ibex_compressed_decoder | rtl/ibex_compressed_decoder.sv | 7 | 0 | 1 | 0 | 0 | 0 | 8 | :921-937 |
| ibex_dummy_instr | rtl/ibex_dummy_instr.sv | 0 | 0 | 0 | 0 | 0 | 0 | 0 | |
| prim_lfsr | vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv | 12 | 0 | 2 | 0 | 10 | 3 | 27 | several are in non-elaborated branches (gen_fib_xnor, gen_unknown_type, gen_out_non_linear, gen_output_sva); ASSERT_I at :261/:268 only under SIMULATION and not VERILATOR |
| ibex_id_stage | rtl/ibex_id_stage.sv | 19 | 4 | 1 | 6 | 0 | 0 | 30 | :401 (g_btalu_muxes, E) / :429 (g_nobtalu, N); :1078-1100 in gen_stall_mem (E), :1162 in gen_no_stall_mem (N) |
| ibex_decoder | rtl/ibex_decoder.sv | 1 | 0 | 0 | 0 | 0 | 0 | 1 | :1488 |
| ibex_controller | rtl/ibex_controller.sv | 5 | 1 | 0 | 0 | 0 | 0 | 6 | :261, :373, :1078, :1101, :1104, :1114 |
| ibex_ex_block | rtl/ibex_ex_block.sv | 0 | 0 | 0 | 0 | 0 | 0 | 0 | exposes sva_multdiv_fsm_idle under INC_ASSERT only |
| ibex_alu | rtl/ibex_alu.sv | 0 | 0 | 0 | 0 | 0 | 0 | 0 | |
| ibex_multdiv_fast | rtl/ibex_multdiv_fast.sv | 1 | 0 | 5 | 0 | 0 | 0 | 6 | :258 (gen_mult_single_cycle, E) / :378 (gen_mult_fast, N) |
| ibex_cheriot_ex | rtl/ibex_cheriot_ex.sv | 0 | 0 | 0 | 0 | 0 | 0 | 0 | |
| ibex_load_store_unit | rtl/ibex_load_store_unit.sv | 5 | 2 | 2 | 0 | 0 | 0 | 9 | :817-834 |
| ibex_wb_stage | rtl/ibex_wb_stage.sv | 1 | 0 | 0 | 0 | 0 | 0 | 1 | :310 |
| ibex_cs_registers | rtl/ibex_cs_registers.sv | 1 | 2 | 0 | 0 | 1 | 0 | 4 | :1496 is per PMP region inside g_pmp_csrs (16 copies) |
| ibex_csr | rtl/ibex_csr.sv | 0 | 0 | 1 | 0 | 0 | 0 | 1 | :55; 56 instances |
| ibex_counter | rtl/ibex_counter.sv | 0 | 0 | 0 | 0 | 0 | 0 | 0 | |
| ibex_pmp | rtl/ibex_pmp.sv | 0 | 0 | 0 | 0 | 0 | 0 | 0 | |
| prim_buf | prim_generic/rtl/prim_buf.sv | 0 | 0 | 0 | 0 | 0 | 0 | 0 | |
| prim_secded_inv_39_32_enc/dec, prim_secded_inv_28_22_enc/dec | prim/rtl/ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | |
| ibex_register_file_ff (wrapper) | rtl/ibex_register_file_ff.sv | 5 | 0 | 0 | 0 | 1 | 0 | 6 | :91 and :162 in g_cheriot_rf (E); remaining in g_plain_rf (N) - exact split not itemized |
| not elaborated: ibex_fetch_fifo 2, ibex_branch_predict 1, ibex_multdiv_slow 1, ibex_prefetch_buffer 0 | | | | | | | | | for reference only |

Grand total of macro lines in elaborated ibex_* modules (excluding non-elaborated branches is not
attempted here): 9+12+5+8+0+30+1+6+0+0+6+0+9+1+4+1+0+0 = 92, plus 27 in prim_lfsr and 6 in the
wrapper-side register file.

## 8. Items marked unverified

1. The wrapper's parameter derivation is assumed to mirror rtl/ibex_top.sv:212-233 and :369-410;
   the wrapper source was not read (task instruction). All values in section 1 follow from that
   assumption.
2. The instance name of the register file in the wrapper (ibex_top uses register_file_i under
   gen_regfile_ff, rtl/ibex_top.sv:532-540) and the exact parameter set the wrapper passes to
   ibex_register_file_ff.
3. dv_fcov_macros.svh: its location (vendor/lowrisc_ip/dv/sv/dv_utils/ as stated by the task),
   the macro bodies, and their behaviour when DV_FCOV_* defines are absent. Only the RTL usage
   pattern was analysed (section 6).
4. formal_tb_frag.svh location (not found in any fence-allowed directory); irrelevant unless FORMAL
   and YOSYS are defined.
5. How the team's VCS file list resolves the virtual cores lowrisc:prim:buf and
   lowrisc:prim:clock_gating (fusesoc mapping in prim_generic.core:41,44 vs. direct listing). The
   only candidate sources in the clone are vendor/lowrisc_ip/ip/prim_generic/rtl/prim_buf.sv and
   prim_clock_gating.sv.
6. Numeric values computed by hand from ibex_pkg.sv expressions: IC_LINE_BYTES 8, IC_LINE_W 3,
   IC_NUM_LINES 256, IC_LINE_BEATS 2, IC_INDEX_W 8, IC_TAG_SIZE 22, BusSizeECC 39, TagSizeECC 28,
   LineSizeECC 78, LFSR_OUT_W 17, NumBusyBits 12, u_mcounteren_csr Width 13.
7. Hand-counted instance totals (56 ibex_csr, 12 ibex_counter) and the elaborated/non-elaborated
   split of assertion lines in ibex_register_file_ff.
8. lowrisc:dv:dv_fcov_macros core file location (referenced by ibex_core.core:17; not in an allowed
   path).

## Part C. FSM inventory and cross-module control paths (subagent A2 body)

## 1. FSM inventory

Legend: `U` = unreachable in this DUT (reason given), `H` = reachable but hard to hit from the core
boundary (stimulus hint given). Counters are collected in section 3.

### FSM-1  Controller main FSM `ctrl_fsm_e`

- Module/file: `ibex_controller`, rtl/ibex_controller.sv
- Type: `ctrl_fsm_e` (rtl/ibex_pkg.sv:291-302). Registers: `ctrl_fsm_cs`, `ctrl_fsm_ns`
  (rtl/ibex_controller.sv:137); reset value `RESET` (:1032); update `ctrl_fsm_cs <= ctrl_fsm_ns`
  (:1042); next-state comb block :539-1000 with default hold `ctrl_fsm_ns = ctrl_fsm_cs` (:563).
- States (10): RESET, BOOT_SET, WAIT_SLEEP, SLEEP, FIRST_FETCH, DECODE, FLUSH, IRQ_TAKEN,
  DBG_TAKEN_IF, DBG_TAKEN_ID. Validity assertion rtl/ibex_controller.sv:1104-1106.
- Doc: doc/03_reference/instruction_decode_execute.rst:24-35 ("Controller"),
  exception_interrupts.rst:27-64 (interrupt priority), :103-130 (exceptions), debug.rst.
- Key supporting flags (not enum states): `debug_mode_q` (:140, set :779/:810, cleared :964),
  `nmi_mode_q` (:139, set :745, cleared :959), `exc_req_q`/`illegal_insn_q`/`load_err_q`/
  `store_err_q` (:1037-1050), `enter_debug_mode_prio_q`, `do_single_step_q` (:1034,:1036,:1046,:1044).

Transitions:

| # | FROM -> TO | Condition | Line |
|---|---|---|---|
| C1 | RESET -> BOOT_SET | unconditional; pc_set_o=1, pc_mux=PC_BOOT, instr_req_o=0 | :582-587 |
| C2 | BOOT_SET -> FIRST_FETCH | unconditional; pc_set_o=1 PC_BOOT, instr_req_o=1 | :589-596 |
| C3 | WAIT_SLEEP -> SLEEP | unconditional; ctrl_busy_o=0, instr_req_o=0, halt_if, flush_id | :598-604 |
| C4 | SLEEP -> FIRST_FETCH | `irq_nm \|\| irq_pending_i \|\| debug_req_i \|\| debug_mode_q \|\| debug_single_step_i` | :615-616 |
| C5 | SLEEP -> SLEEP | otherwise; ctrl_busy_o=0 | :617-620 |
| C6 | FIRST_FETCH -> DECODE | `id_in_ready_o` (and neither C7 nor C8) | :625-627 |
| C7 | FIRST_FETCH -> IRQ_TAKEN | `handle_irq` (overrides C6); halt_if | :630-637 |
| C8 | FIRST_FETCH -> DBG_TAKEN_IF | `enter_debug_mode` (overrides C6, C7); halt_if | :640-645 |
| C9 | FIRST_FETCH -> FIRST_FETCH | `~id_in_ready_o & ~handle_irq & ~enter_debug_mode` | :563 default |
| C10 | DECODE -> FLUSH | `special_req & (ready_wb_i \| wb_exception_o)`; retain_id=1 | :664-679 |
| C11 | DECODE -> DBG_TAKEN_IF | `!stall & !special_req & !id_wb_pending & enter_debug_mode`; halt_if | :704-710 |
| C12 | DECODE -> IRQ_TAKEN | `!stall & !special_req & !id_wb_pending & !enter_debug_mode & handle_irq`; halt_if | :711-720 |
| C13 | DECODE -> DECODE | otherwise (incl. `special_req & ~ready_wb_i & ~wb_exception_o` waiting, retain_id=1) | :563, :668 |
| C14 | IRQ_TAKEN -> DECODE | unconditional; pc_set only if `handle_irq` still true | :725-762 |
| C15 | DBG_TAKEN_IF -> DECODE | unconditional; pc_set PC_EXC/EXC_PC_DBD, csr_save_if, debug_csr_save, debug_mode_d=1 | :764-783 |
| C16 | DBG_TAKEN_ID -> DECODE | unconditional; pc_set PC_EXC/EXC_PC_DBD; CSR save only if `ebreak_into_debug & !debug_mode_q` | :785-814 |
| C17 | FLUSH -> DECODE | default (exception taken with pc_set, or mret/dret with pc_set, or csr_pipe_flush with no pc_set) | :816-820 |
| C18 | FLUSH -> DBG_TAKEN_ID | `(exc_req_q \| store_err_q \| load_err_q) & ebrk_insn_prio & (debug_mode_q \| ebreak_into_debug)`; pc_set/flush_id suppressed | :874-883 |
| C19 | FLUSH -> WAIT_SLEEP | no exception pending & `~mret_insn & ~dret_insn & wfi_insn` | :954-968 |
| C20 | FLUSH -> DBG_TAKEN_IF | `enter_debug_mode_prio_q & !(ebrk_insn_prio & ebreak_into_debug)`; evaluated last, overrides C17/C19 and (when ebreak is not the prio cause) C18 | :985-987 |
| C21 | default -> RESET | illegal encoding | :990-993 |

Unreachable in this DUT (controller):
- U-C1: C21 `default -> RESET` (:990-993) - only reachable via state corruption (fault injection).
- U-C2, U-C3: FLUSH `instr_fetch_err_prio` CHERIoT sub-branches (tag violation :850-853, bound
  violation :854-858) - `cheriot_enable_i == IbexMuBiOn` false; only the external-error branch
  :859-861 is reachable.
- U-C4: `illegal_insn_prio` CHERIoT mtval=0 variant (:866-867); RV32 mtval = instruction (:868) reachable.
- U-C5: `ebrk_insn_prio` CHERIoT mtval=pc (:894-897).
- U-C6: `store_err_prio` CHERIoT branch (:901-908); RV32 branch :909-912 reachable.
- U-C7: `load_err_prio` CHERIoT branch (:915-922); RV32 branch :923-926 reachable.
- U-C8: `cheriot_ex_err_prio` (:928-933): `cheriot_ex_err_q <= cheriot_ex_err_d` (:1063) with
  `cheriot_ex_err_d` gated by `cheriot_enable_i == IbexMuBiOn` (:256-257) -> always 0.
- U-C9: `cheriot_wb_err_prio` (:934-944): prio term gated at :318 -> never 1.
- U-C10: `cheriot_asr_err_prio` (:945-948): `cheriot_asr_err_d` = 0 because both
  `mret_cheriot_asr_err` and `csr_cheriot_asr_err` are gated at :237-238.
- U-C11: `pc_set_o` via `cheriot_branch_req_i` in DECODE (:681-682) - gated term.
- U-C12: `nt_branch_mispredict_o` (:690-696) and `pc_set_o = ~instr_bp_taken_i` variant (:684) -
  BranchPredictor=0; pc_set_o is always 1 on branch_set/jump_set.
- U-C13: `exc_req_d` CHERIoT term (:269) and `exc_req_wb` CHERIoT term (:276) - gated; the FSM arc
  itself (C10) is reachable through the RV32 terms.
- Note (not unreachable, but structurally fixed): `g_no_wb_exceptions` (:338-371) is NOT
  elaborated (WritebackStage=1); the exception priority used is `g_wb_exceptions` :299-337 where
  store_err_q > load_err_q > instr_fetch_err > illegal_insn_q > ecall > ebrk.

Hard to hit (controller):
- H-C1: C20 via `debug_req_i`: `enter_debug_mode_prio_q` is the flop (:1046) of `enter_debug_mode_prio_d`
  (:474) sampled in the DECODE cycle that took C10. Stimulus: raise `debug_req_i` in the same cycle
  a trapping/mret/dret/wfi/csr-flush instruction is in ID with `ready_wb_i` high. Effect: debug entry
  with exception CSRs written as if the trap were taken (:971-976 comment), `instr_addr_o` = DmHaltAddr.
- H-C2: C20 via single step over a trapping instruction: dcsr.step=1 then execute ecall/illegal
  -> FLUSH -> DBG_TAKEN_IF (`do_single_step_d` :462). Easier than H-C1; still needs debug ROM.
- H-C3: C7 with the NMI at boot: after reset `mstatus.mie=0` (rtl/ibex_cs_registers.sv:1052) so
  only `irq_nm_i` satisfies `handle_irq` (:498-499) while in FIRST_FETCH. Stimulus: hold `irq_nm_i`
  high through reset release; observe `instr_addr_o` = boot fetch then mtvec+0x7C before any retire.
- H-C4: C8 at boot: `debug_req_i` high at reset release -> RESET->BOOT_SET->FIRST_FETCH->DBG_TAKEN_IF
  before the first instruction executes (`instr_addr_o` = DmHaltAddr on the 4th cycle).
- H-C5: C4 via `debug_mode_q` or `debug_single_step_i`: a WFI executed in debug mode or with
  dcsr.step=1 goes FLUSH->WAIT_SLEEP->SLEEP->FIRST_FETCH with no external wake (:614-616).
- H-C6: C10 taken through `wb_exception_o` rather than `ready_wb_i` (:676): the instruction in WB
  is a load/store whose response errors (`load_err_i | store_err_i`, :336) in the same cycle ID
  holds a special_req instruction (ecall/wfi/mret/illegal). Stimulus: store followed immediately by
  ecall; drive `data_err_i` with the store's `data_rvalid_i` two cycles later.
- H-C7: priority `store_err_q`/`load_err_q` over `instr_fetch_err`/`illegal_insn_q` (:314-323): errored
  load/store in WB while the next instruction in ID carries a fetch error or is illegal; mepc must
  come from WB (`csr_save_wb_o` :839) and mcause is the LSU fault, not the ID fault.
- H-C8: C14 with `handle_irq` false in IRQ_TAKEN (:729): irq line withdrawn exactly one cycle after
  the DECODE decision (C12). Result: no pc_set, no CSR save, halt_if released, back to DECODE.
  Stimulus: single-cycle `irq_timer_i` pulse timed to the last cycle of an instruction.
- H-C9: internal NMI selection `irq_nm_int & !irq_nm_ext_i` -> `csr_mtval_o = irq_nm_int_mtval`
  (:741-743) and the ECC IRQ being held pending while an external NMI is taken first (:407-412).
  Stimulus: corrupt `data_rdata_i[38:32]` on a load response while `irq_nm_i` is also high.
- H-C10: interrupt/debug masking during Zcmp expansion: `handle_irq` blocked only while
  `INSTR_EXPANDED_COMMIT` (:500), `enter_debug_mode` blocked while EXPANDED or COMMIT (:474-477).
  Stimulus: assert `irq_external_i` during a `cm.popret` (COMMIT phase) vs during `cm.push`
  store phase (EXPANDED, interrupt allowed).
- H-C11: `ebreak_into_debug` in U-mode uses `debug_ebreaku_i` (:481-483): needs U-mode entry
  (mret with mstatus.mpp=U) then ebreak with dcsr.ebreaku=1.
- H-C12: mret in NMI mode (:958-960) restoring from mstack (rtl/ibex_cs_registers.sv:967-974).
- H-C13: C16 without CSR update: ebreak while already in debug mode (`debug_mode_q`, :799) ->
  re-enter debug at DmHaltAddr without touching dcsr/dpc.
- H-C14: exception while in debug mode: `exc_pc_mux_o = EXC_PC_DBG_EXC` (:831) -> DmExceptionAddr
  (rtl/ibex_if_stage.sv:230); no mepc/mcause update (rtl/ibex_cs_registers.sv:918).
- H-C15: `debug_cause_d` priority race (:519-523): trigger, ebreak-into-debug, haltreq and step in
  the same cycle; the comment at :515-518 warns the cause can be recorded incorrectly.

### FSM-2  LSU main FSM `ls_fsm_e`

- Module/file: `ibex_load_store_unit`, rtl/ibex_load_store_unit.sv
- Type: `ls_fsm_e` (rtl/ibex_pkg.sv:816-820). Registers `ls_fsm_cs`, `ls_fsm_ns` (:122); reset
  `IDLE` (:638); update (:650); comb :411-609 with default hold (:412). Companion flags:
  `handle_misaligned_q` (:110, :651), `pmp_err_q` (:112, :652), `lsu_err_q` (:113, :653).
- States (8): IDLE, WAIT_GNT_MIS, WAIT_RVALID_MIS, WAIT_GNT, WAIT_RVALID_MIS_GNTS_DONE,
  CTX_WAIT_GNT1, CTX_WAIT_GNT2, CTX_WAIT_RESP. Validity assertion :821-824.
- Doc: doc/03_reference/load_store_unit.rst:71-80 ("Misaligned Accesses"), :84-95 ("Protocol").
- `split_misaligned_access` = word with offset != 0, or halfword with offset 3 (:403-405).
  `cpu_req_valid = lsu_req_i & ~(cheriot term)` = `lsu_req_i` here (:407); `cpu_req_erred` = 0 (:408).

| # | FROM -> TO | Condition | Line |
|---|---|---|---|
| L1 | IDLE -> IDLE | `cpu_req_valid & data_gnt_i & ~split_misaligned_access` (single aligned access, done) | :468-482 |
| L2 | IDLE -> WAIT_RVALID_MIS | `cpu_req_valid & data_gnt_i & split_misaligned_access` | :478-482 |
| L3 | IDLE -> WAIT_GNT | `cpu_req_valid & ~data_gnt_i & ~split` | :483-485 |
| L4 | IDLE -> WAIT_GNT_MIS | `cpu_req_valid & ~data_gnt_i & split` | :483-485 |
| L5 | IDLE -> IDLE (idle) | `~lsu_req_i` | :412 default |
| L6 | WAIT_GNT_MIS -> WAIT_RVALID_MIS | `data_gnt_i \|\| pmp_err_q` | :489-501 |
| L7 | WAIT_RVALID_MIS -> IDLE | `(data_rvalid_i \|\| pmp_err_q) & data_gnt_i` (second request granted in the cycle the first response arrives) | :510-518 |
| L8 | WAIT_RVALID_MIS -> WAIT_GNT | `(data_rvalid_i \|\| pmp_err_q) & ~data_gnt_i` | :518 |
| L9 | WAIT_RVALID_MIS -> WAIT_RVALID_MIS_GNTS_DONE | `~(data_rvalid_i \|\| pmp_err_q) & data_gnt_i` | :523-530 |
| L10 | WAIT_GNT -> IDLE | `data_gnt_i \|\| pmp_err_q` | :533-544 |
| L11 | WAIT_RVALID_MIS_GNTS_DONE -> IDLE | `data_rvalid_i` (first response) | :546-563 |
| L12 | IDLE -> IDLE (erred) | CHERIoT `cpu_req_erred` | :437-448 |
| L13 | IDLE -> CTX_WAIT_GNT2 | CHERIoT cap access `& data_gnt_i` | :449-464 |
| L14 | IDLE -> CTX_WAIT_GNT1 | CHERIoT cap access `& ~data_gnt_i` | :465-467 |
| L15 | CTX_WAIT_GNT1 -> CTX_WAIT_GNT2 | `cheriot on & data_gnt_i` | :565-573 |
| L16 | CTX_WAIT_GNT1 -> IDLE | `cheriot off` | :574-576 |
| L17 | CTX_WAIT_GNT2 -> IDLE | `cheriot on & data_gnt_i & (data_rvalid_i \| cap_rx_fsm_q==CRX_WAIT_RESP2)` | :583-584 |
| L18 | CTX_WAIT_GNT2 -> CTX_WAIT_RESP | `cheriot on & data_gnt_i & ~...` | :585-587 |
| L19 | CTX_WAIT_GNT2 -> IDLE | `cheriot off` | :588-590 |
| L20 | CTX_WAIT_RESP -> IDLE | `cheriot on & data_rvalid_i`, or `cheriot off` | :593-603 |
| L21 | default -> IDLE | illegal encoding | :605-607 |

Unreachable (LSU): U-L1..U-L10 = L12, L13, L14, L15, L16, L17, L18, L19, L20 (9 arcs; the CTX_*
states are never entered because L13/L14 require `cheriot_enable_i == IbexMuBiOn`, :437, :449)
and L21 (default). Total 10.

Hard to hit (LSU):
- H-L1: L9 (two outstanding requests): second grant arrives before the first `data_rvalid_i`.
  Stimulus: memory model with gnt in the request cycle and rvalid latency >= 2 on a misaligned
  word store/load (e.g. `sw` to addr%4==2).
- H-L2: L8: first `data_rvalid_i` arrives while the second request is still waiting for grant.
  Stimulus: rvalid latency 1, gnt withheld on the second request for >= 1 cycle.
- H-L3: PMP error on the second half only: `pmp_err_d = data_pmp_err_i` sampled in WAIT_RVALID_MIS
  (:512) / GNTS_DONE (:553). Stimulus: misaligned word at (pmp region top - 2) with a 4-byte
  granularity boundary (PMPGranularity=0). Effect: first half's bus access completes, second half
  never issued (`data_req_o` gated rtl/ibex_core.sv:1063), `load_err_o` with mtval = second
  (word-aligned) address (:258 with `addr_incr_req_o`).
- H-L4 (CORRECTED per Critic C-11, 2026-09-03): PMP error on the first half of a misaligned access:
  L4 (IDLE -> WAIT_GNT_MIS with `pmp_err_q` set; the first-half bus request is suppressed at
  rtl/ibex_core.sv:1063), then L6 with `pmp_err_q` acting as the grant (:495), then WAIT_RVALID_MIS
  DOES drive `data_req_o` with the incremented address (:503-507) because :1063 gates only on the
  current word's PMP result, and `pmp_err_q` stands in for the first-half response (:510). The
  second half is issued unless its own PMP check fails; the exception is raised when the sequence
  completes, mtval = first (misaligned) address. The v1 text "no bus request at all" was wrong;
  gen_behaviour_summaries.md MEM-13 and the DV Lead's F-PMP-087 / F-EXC-033 are right.
- H-L5: bus error on the first half (`lsu_err_d = data_bus_err_i` :514; `addr_update` suppressed :520)
  -> second half still issued and its response ignored; error reported at the second `rvalid`
  (`data_or_pmp_err` :688 includes `lsu_err_q`), mtval = first (misaligned) address.
- H-L6: bus error on the second half only: `data_bus_err_i` at the final rvalid (:688), mtval =
  second word-aligned address. Distinguishable from H-L5 only via mtval.
- H-L7: `lsu_req_done` (:632) asserted in the same cycle as `lsu_resp_valid_o` for an aligned
  access with same-cycle gnt and rvalid of the previous access (back-to-back loads, rtl/ibex_load_store_unit.sv:748-752 comment).

### FSM-3  LSU capability receive FSM `cap_rx_fsm_t`

- Module/file: `ibex_load_store_unit`, rtl/ibex_load_store_unit.sv
- Type: `cap_rx_fsm_t` (rtl/ibex_pkg.sv:822). Registers `cap_rx_fsm_q`, `cap_rx_fsm_d` (:124);
  reset `CRX_IDLE` (:645); update (:656); comb :611-626.
- States (3): CRX_IDLE, CRX_WAIT_RESP1, CRX_WAIT_RESP2.
- Doc: none.

| # | FROM -> TO | Condition | Line |
|---|---|---|---|
| X1 | CRX_IDLE -> CRX_WAIT_RESP1 | `cheriot on & lsu_go_goodcap` | :615-617 |
| X2 | CRX_WAIT_RESP1 -> CRX_WAIT_RESP2 | `data_rvalid_i` | :618-619 |
| X3 | CRX_WAIT_RESP2 -> CRX_WAIT_RESP1 | `data_rvalid_i & lsu_go_goodcap` | :620-622 |
| X4 | CRX_WAIT_RESP2 -> CRX_IDLE | `data_rvalid_i & ~lsu_go_goodcap` | :623 |
| X5 | default -> CRX_IDLE | | :624 |

Unreachable: U-X1..U-X5 = the whole FSM. `lsu_go_goodcap` is only set inside the CHERIoT IDLE
branch (:459) which is gated (:449-450); the FSM stays in CRX_IDLE forever. The consumers
`cap_lsw_*_q` (:669-678) and `lsu_rcap_o` (:704-709) are likewise dead; `lsu_rcap_o` = NULL_CAP.

### FSM-4  ID/EX stage FSM `id_fsm_e`

- Module/file: `ibex_id_stage`, rtl/ibex_id_stage.sv
- Type: `id_fsm_e {FIRST_CYCLE, MULTI_CYCLE}` (:861). Registers `id_fsm_q`, `id_fsm_d` (:862);
  reset `FIRST_CYCLE` (:866); update only when `instr_executing` (:867-868); comb :877-973 guarded by
  `instr_executing_spec` (:889).
- Doc: doc/03_reference/instruction_decode_execute.rst:16-22 ("small state machine ... multi-cycle
  instructions"), pipeline_details.rst:32-105 (stall table; note :26-30 says the table is for the
  2-stage pipeline, this DUT has WritebackStage=1).

| # | FROM -> TO | Condition (all under `instr_executing_spec`) | Line |
|---|---|---|---|
| I1 | FIRST_CYCLE -> MULTI_CYCLE | `lsu_req_dec & ~lsu_req_done_i` (WritebackStage=1 branch) | :893-899 |
| I2 | FIRST_CYCLE -> FIRST_CYCLE | `lsu_req_dec & lsu_req_done_i` (request granted first cycle) | :897 |
| I3 | FIRST_CYCLE -> MULTI_CYCLE | `cheriot_lsu_req_dec & cheriot on & ~lsu_req_done_i` | :901-909 |
| I4 | FIRST_CYCLE -> MULTI_CYCLE | `multdiv_en_dec & ~ex_valid_i` (MULH*, DIV*, REM*); rf_we_raw=0, stall_multdiv | :910-919 |
| I5 | FIRST_CYCLE -> FIRST_CYCLE | `multdiv_en_dec & ex_valid_i` (MUL single cycle) | :912 |
| I6 | FIRST_CYCLE -> MULTI_CYCLE | `branch_in_dec & (data_ind_timing_i \|\| (!BranchTargetALU && branch_decision_i))` -> with BTALU=1 only `data_ind_timing_i` | :920-928 |
| I7 | FIRST_CYCLE -> FIRST_CYCLE | `branch_in_dec & ~data_ind_timing_i` (taken or not, 1 cycle in ID; taken branch sets pc_set) | :925-926 |
| I8 | FIRST_CYCLE -> MULTI_CYCLE | `jump_in_dec & !BranchTargetALU` | :936-942 |
| I9 | FIRST_CYCLE -> FIRST_CYCLE | `jump_in_dec & BranchTargetALU` (jump_set_raw = jump_set_dec) | :939-941 |
| I10 | FIRST_CYCLE -> MULTI_CYCLE | `alu_multicycle_dec` (ROL/ROR/FSL/FSR/CMOV/CMIX/CRC32*); stall_alu, rf_we_raw=0 | :943-947 |
| I11 | FIRST_CYCLE -> FIRST_CYCLE | default (no multicycle class) | :948-950 |
| I12 | MULTI_CYCLE -> FIRST_CYCLE | `multicycle_done & ready_wb_i` | :959-960 |
| I13 | MULTI_CYCLE -> MULTI_CYCLE | otherwise; `stall_multdiv=multdiv_en_dec`, `stall_branch=branch_in_dec`, `stall_jump=jump_in_dec` | :961-965 |
| I14 | default -> FIRST_CYCLE | | :968-970 |

`multicycle_done` (WritebackStage=1) = `(lsu_req_dec | cheriot_lsu_req_dec) ? ~stall_mem : ex_valid_all`
(:1012); `ex_valid_all = instr_is_cheriot_id_o ? cheriot_ex_valid_i : ex_valid_i` (:578), and
`instr_is_cheriot_id_o` is asserted 0 when CHERIoT is off (:1299).

Unreachable (ID): U-I1 = I3 (`cheriot_lsu_req_dec` only produced under the CHERIoT-on decode,
rtl/ibex_decoder.sv:405/:451, and the arc is also gated at :902); U-I2 = I8 (BranchTargetALU=1);
U-I3 = I14 default; U-I4 = the `(!BranchTargetALU && branch_decision_i)` sub-term of I6 (BTALU=1),
so a taken branch never enters MULTI_CYCLE unless data_ind_timing is on. Total 4.
Also not elaborated: `gen_no_stall_mem` (:1142-1208), `g_branch_set_direct` (:767-770; because
DataIndTiming=1 the `g_branch_set_flop` block :771-793 is used, selecting the direct path at run
time when `data_ind_timing_i=0`, :790-791), `g_nosec_branch_taken` (:833-839; `g_sec_branch_taken`
:819-832 is used).

Hard to hit (ID):
- H-I1: I13 hold with `multicycle_done & ~ready_wb_i`: a MULH/DIV/REM/bitmanip-multicycle result is
  ready while WB still waits for a load/store response. Stimulus: `lw` with rvalid latency > 2
  (or > 37 for DIV) immediately followed by `mulh`/`div`. Observe `perf_mul_wait`/`perf_div_wait`
  (:1226-1227) vs `stall_wb` (:1133).
- H-I2: I6 (two-cycle branches) requires `cpuctrlsts.data_ind_timing=1` (rtl/ibex_cs_registers.sv:1905);
  exercise both taken and not-taken to cover `branch_set_raw_d = branch_decision_i | data_ind_timing_i`
  (:928) with `branch_taken = ~data_ind_timing_i | branch_taken_q` (:831).
- H-I3: FIRST_CYCLE held (register not updated because `instr_executing=0`, :867) while
  `instr_executing_spec=1`: `outstanding_memory_access` (:1015-1016) or `wb_exception` via
  `instr_kill` (:1033-1036). The branch/jump speculative set `branch_jump_set_done_q` (:796-805)
  prevents repeated `pc_set` (:814-815); stimulus: taken branch right after a slow load.
- H-I4 (WITHDRAWN per Critic C-11, 2026-09-03): the premise "ID mid-misaligned-request while WB
  holds an errored load" cannot arise: a new memory request starts only when
  `data_req_allowed = ~outstanding_memory_access` (rtl/ibex_id_stage.sv:1019), so WB never holds an
  outstanding load while ID issues one. What remains is the invariant IbexStallMemNoRequest
  (:1100-1101), which the regression checks as an assertion, not a hard-to-reach arc.

### FSM-5  Divider FSM `md_fsm_e` (ibex_multdiv_fast)

- Module/file: `ibex_multdiv_fast`, rtl/ibex_multdiv_fast.sv (instantiated by rtl/ibex_ex_block.sv:165-191
  for RV32MSingleCycle; `ibex_multdiv_slow` :140-164 is NOT elaborated).
- Type: `md_fsm_e` (:90-92). Registers `md_state_q`, `md_state_d` (:93); reset `MD_IDLE` (:104);
  update only when `div_en_internal = div_en_i & ~div_hold` (:99, :108-112); comb :412-526.
  Companion: `div_counter_q` (:78, :109), `div_by_zero_q` (:82, :113), intermediate values live in
  ID stage `imd_val_q` (rtl/ibex_id_stage.sv:446-456) written through `imd_val_we_o` (:125, :128).
- States (7): MD_IDLE, MD_ABS_A, MD_ABS_B, MD_COMP, MD_LAST, MD_CHANGE_SIGN, MD_FINISH. Validity :532-533.
- Doc: doc/03_reference/instruction_decode_execute.rst:110-155 ("Multiplier/Divider Block"),
  pipeline_details.rst:63-66 (1 or 37 stall cycles), security.rst:17-32 (DIT removes early divide-by-zero).

| # | FROM -> TO | Condition (all gated by `div_en_internal`) | Line |
|---|---|---|---|
| D1 | MD_IDLE -> MD_FINISH | `operator_i==MD_OP_DIV & !data_ind_timing_i & equal_to_zero_i` (result -1) | :427-434 |
| D2 | MD_IDLE -> MD_ABS_A | `operator_i==MD_OP_DIV & ~(above)`; div_by_zero_d = equal_to_zero_i | :434-437 |
| D3 | MD_IDLE -> MD_FINISH | `operator_i==MD_OP_REM & !data_ind_timing_i & equal_to_zero_i` (result = op_a) | :438-445 |
| D4 | MD_IDLE -> MD_ABS_A | `operator_i==MD_OP_REM & ~(above)` | :445 |
| D5 | MD_ABS_A -> MD_ABS_B | unconditional; div_counter_d = 31 | :453-463 |
| D6 | MD_ABS_B -> MD_COMP | unconditional | :465-475 |
| D7 | MD_COMP -> MD_COMP | `div_counter_q != 1` (31 iterations, counter 31 -> 1) | :477-484 |
| D8 | MD_COMP -> MD_LAST | `div_counter_q == 1` | :480 |
| D9 | MD_LAST -> MD_CHANGE_SIGN | unconditional | :486-500 |
| D10 | MD_CHANGE_SIGN -> MD_FINISH | unconditional; sign fix uses `div_change_sign = (sign_a ^ sign_b) & ~div_by_zero_q` (:408) | :502-512 |
| D11 | MD_FINISH -> MD_IDLE | `multdiv_ready_id_i` (div_hold = ~multdiv_ready_id_i keeps the state) ; div_valid=1 | :514-520 |
| D12 | default -> MD_IDLE | | :522-524 |

Cycle counts: D2/D4 path = IDLE, ABS_A, ABS_B, 31 x COMP, LAST, CHANGE_SIGN, FINISH = 37 cycles;
D1/D3 path = 2 cycles. `valid_o = mult_valid | div_valid` (:529) -> `ex_valid_o` (rtl/ibex_ex_block.sv:197).
Note the state register only advances while `div_en_i` is high; `div_en_i` = `instr_executing ?
div_en_dec : 0` (rtl/ibex_id_stage.sv:734), so the FSM freezes (does not reset) if `instr_executing`
drops mid-division.

Unreachable: U-D1 = D12 default. (`gen_multdiv_slow` FSM and its 7 states are not elaborated; not counted.)
Hard to hit:
- H-D1 (UNREACHABLE, T-053 X-12: div_en_i is gated by instr_executing, which is 0 while a WB memory access is outstanding, so the divider never runs with multdiv_ready_id_i = 0; rtl/ibex_id_stage.sv:733-734, :1059-1062): D11 hold (`div_hold`, :518) with `multdiv_ready_id_i = ready_wb_i = 0` (rtl/ibex_id_stage.sv:976):
  DIV finishing while WB waits for a load response > 37 cycles old. Stimulus: `lw` with a very
  slow `data_rvalid_i` followed by `div`.
- H-D2: divide-by-zero with `data_ind_timing_i=1`: full 37-cycle path, `div_by_zero_q` blocks the
  sign change (:408, :435-437), quotient must still be all-ones (`op_remainder_d='1` :432 then
  overwritten? verify at :490 vs :505 - the natural long-division result path, per comment :430-431).
  Stimulus: enable cpuctrlsts.data_ind_timing then `div x, x, zero` and `rem x, x, zero`, both signed/unsigned.
- H-D3: the state freeze described above: `div_en_i` dropping mid-operation would require
  `instr_executing` to fall; with WritebackStage the only candidates are `wb_exception` or
  `~controller_run` (rtl/ibex_id_stage.sv:1033-1036, :1059-1062). `outstanding_memory_access` must be
  0 for the DIV to have started, so `wb_exception` cannot arrive mid-DIV; `controller_run` drops
  only via C10-C12 which wait for `!stall` (:704). Believed unreachable; flagged as "unverified
  reasoning" for the DV team to assert (a `$stable(md_state_q)` while `div_en_i==0 && md_state_q!=MD_IDLE` cover).

### FSM-6  Single-cycle multiplier FSM `mult_fsm_e` (gen_mult_single_cycle)

- Module/file: `ibex_multdiv_fast`, generate block `gen_mult_single_cycle` (rtl/ibex_multdiv_fast.sv:140-261).
- Type: `mult_fsm_e {MULL, MULH}` (:142-144). Registers `mult_state_q`, `mult_state_d` (:145); reset
  `MULL` (:247); update only when `mult_en_internal = mult_en_i & ~mult_hold` (:98, :249-251); comb :188-243.
- Doc: doc/03_reference/instruction_decode_execute.rst:120-127 (MUL 1 cycle, MULH 2 cycles).

| # | FROM -> TO | Condition | Line |
|---|---|---|---|
| M1 | MULL -> MULL | `operator_i == MD_OP_MULL` (MUL); mult_valid=1; `mult_hold = ~multdiv_ready_id_i` | :210-217 |
| M2 | MULL -> MULH | `operator_i != MD_OP_MULL` (MULH/MULHSU/MULHU first cycle); mult_valid=0 | :211-214 |
| M3 | MULH -> MULL | unconditional; mult_valid=1; `mult_hold = ~multdiv_ready_id_i` blocks the update | :220-236 |
| M4 | default -> MULL | | :238-240 |

Unreachable: U-M1 = M4. The fast-multiplier variant `gen_mult_fast` with states ALBL/ALBH/AHBL/AHBH
(:264-382) is not elaborated (RV32MSingleCycle) - not counted.
Hard to hit:
- H-M1 (UNREACHABLE, T-053 X-12: same argument as H-D1, mult_en_i = 0 while ready_wb_i = 0): M3 held by `mult_hold` (:235): MULH result ready while `ready_wb_i=0` (load in WB waiting).
  Stimulus: `lw` with 3+ cycle rvalid followed by `mulh`.
- H-M2: MULH with `signed_mode_i` = 2'b01 (MULHSU) vs 2'b11 (MULH) vs 2'b00 (MULHU) selecting
  `mult3_sign_*` and `accum` sign extension (:168-169, :185-186, :222-225). Not timing-hard but a
  distinct data path per mode; the FSM path is identical.

### FSM-7  ICache invalidation FSM `inval_state_e`

- Module/file: `ibex_icache`, rtl/ibex_icache.sv (instantiated rtl/ibex_if_stage.sv:298-347; the
  `ibex_prefetch_buffer`/`ibex_fetch_fifo` pair :348-414 is NOT elaborated).
- Type: `inval_state_e` (:193-198). Registers `inval_state_q`, `inval_state_d` (:200); reset
  `OUT_OF_RESET` (:1276); update (:1278); comb :1208-1270. Companion `inval_index_q` (:203; reset
  only when ResetAll, :1282-1296), IC_INDEX_W = 8 (256 lines: rtl/ibex_pkg.sv:400-408).
- Doc: doc/03_reference/icache.rst:96-121 ("ICache Scrambling", "Scramble Key Renewal"), :220-225
  ("Cache invalidation").

| # | FROM -> TO | Condition | Line |
|---|---|---|---|
| V1 | OUT_OF_RESET -> AWAIT_SCRAMBLE_KEY | unconditional; `ic_scr_key_req_o = ~ic_scr_key_valid_i` | :1221-1228 |
| V2 | AWAIT_SCRAMBLE_KEY -> INVAL_CACHE | `ic_scr_key_valid_i`; inval_index reset to 0 | :1229-1240 |
| V3 | AWAIT_SCRAMBLE_KEY -> AWAIT_SCRAMBLE_KEY | `~ic_scr_key_valid_i` (icache_inval_i ignored here) | :1229-1240 |
| V4 | INVAL_CACHE -> AWAIT_SCRAMBLE_KEY | `icache_inval_i` (restart, new key request) | :1248-1252 |
| V5 | INVAL_CACHE -> INVAL_IDLE | `~icache_inval_i & &inval_index_q` (last index written) | :1253-1256 |
| V6 | INVAL_CACHE -> INVAL_CACHE | otherwise; `inval_write_req=1`, index++ each cycle | :1241-1247 |
| V7 | INVAL_IDLE -> AWAIT_SCRAMBLE_KEY | `icache_inval_i`; `ic_scr_key_req_o=1` | :1258-1262 |
| V8 | INVAL_IDLE -> INVAL_IDLE | otherwise; only state with `inval_block_cache=0` | :1263-1266 |
| V9 | default | hold | :1268 |

Every state except INVAL_IDLE forces `inval_block_cache=1` (:1218), which disables lookups
(`lookup_actual_ic0` :266) and allocation (`fill_cache_new` :683) - fetches still proceed from memory.
`inval_active = inval_state_q != INVAL_IDLE` (:1272) -> `busy_o` (:1304) -> `if_busy` -> `core_busy_o`.

Unreachable: U-V1 = V9 (2-bit enum fully populated; default only via corruption).
Hard to hit:
- H-V1: V4: a second `fence.i` (`icache_inval` from rtl/ibex_decoder.sv:721) while the 256-cycle
  INVAL_CACHE sweep is in progress. Stimulus: two `fence.i` within ~256 cycles with
  `ic_scr_key_valid_i` re-asserted quickly by the TB.
- H-V2: V3 swallowing a `fence.i`: TB drops `ic_scr_key_valid_i` on `ic_scr_key_req_o` and delays
  the new key; a `fence.i` during that window must have no visible effect (doc icache.rst:115-116).
- H-V3: V1 with `ic_scr_key_valid_i=1` at reset (no key request emitted) vs 0 (request emitted):
  both reset behaviours should be covered; the `cpuctrlsts.ic_scr_key_valid` read-back
  (rtl/ibex_cs_registers.sv:1938-1949) and `rvfi_ext_ic_scr_key_valid` (rtl/ibex_core.sv:2103) expose it.
- H-V4: ICache enabled (`cpuctrlsts.icache_enable`) while still in INVAL_CACHE right after reset:
  first ~256 cycles never allocate (`fill_cache_new=0`); allocation coverage requires waiting.

### FSM-8 (pseudo)  ICache fill-buffer lifecycle (per buffer, NUM_FB = 4)

- Module/file: `ibex_icache`, generate `gen_fbs` (rtl/ibex_icache.sv:707-983). No enum; the state is
  the bit vector per buffer: `fill_busy_q`, `fill_stale_q`, `fill_cache_q`, `fill_hit_q`,
  `fill_ext_cnt_q[1:0]`, `fill_ext_hold_q`, `fill_ext_done_q`, `fill_rvd_cnt_q[1:0]`, `fill_ram_done_q`,
  `fill_out_cnt_q[1:0]`, `fill_err_q[1:0]`, `fill_older_q[3:0]` (declared :130-158, flops :881-907,
  :952-958; data/addr/way :913-938). IC_LINE_BEATS = 2 (rtl/ibex_pkg.sv:402-406).
- Doc: doc/03_reference/icache.rst:150-166 ("Fill buffers"), :168-185 ("Data output").

Lifecycle as pseudo-states and arcs:

| # | FROM -> TO | Condition | Line |
|---|---|---|---|
| F1 | FREE -> BUSY (allocated) | `fill_alloc = fill_alloc_sel & lookup_grant_ic0` (lowest free buffer, :714-718) | :720-721 |
| F2 | BUSY -> BUSY+HIT | `fill_hit_ic1 = lookup_valid_ic1 & fill_in_ic1 & tag_hit_ic1 & ~ecc_err_ic1` (next cycle after alloc) | :748-749 |
| F3 | BUSY -> BUSY+EXT_REQ | `fill_ext_req = fill_busy_q & ~fill_ext_done_d`; arbitrated oldest-first (`fill_ext_arb` :842) -> `instr_req_o` | :756, :1030-1037 |
| F4 | EXT_REQ counting | `fill_ext_cnt_q += fill_ext_arb & instr_gnt_i`; speculative first request on alloc (`fill_spec_done` :704) | :759-762 |
| F5 | EXT_REQ -> EXT_HOLD | `fill_alloc & fill_spec_hold` or `fill_ext_arb & ~instr_gnt_i` | :764-765 |
| F6 | EXT_REQ -> EXT_DONE | count reached, or hit, or (uncached and stale/branch/end-of-line), and `~fill_ext_hold_q` | :767-775 |
| F7 | RVD counting | `fill_rvd_cnt_q += fill_rvd_arb` (rvalid to oldest expecting buffer, :851-852) | :779-781 |
| F8 | -> RVD_DONE | `fill_ext_done_q & ~fill_ext_hold_q & (fill_rvd_cnt_q == fill_ext_cnt_q)` | :783-784 |
| F9 | OUT counting | `fill_out_cnt_q += fill_out_grant` (output to IF, `fill_out_arb & output_ready`) | :801-806 |
| F10 | -> OUT_DONE | `fill_out_cnt_q[IC_LINE_BEATS_W]` | :808 |
| F11 | -> STALE | `fill_busy_q & branch_i` (sticky) | :741 |
| F12 | -> NO_ALLOC | `fill_cache_q` cleared when `~icache_enable_i` or `icache_inval_i` while busy | :744-746 |
| F13 | -> RAM_REQ -> RAM_DONE | all beats received, `~fill_hit_q & fill_cache_q & ~|fill_err_q & ~fill_ram_done_q`; granted when no lookup (`fill_grant_ic0` :263) | :815-822 |
| F14 | BUSY -> FREE | `fill_done` = (ram_done | hit | ~cache | err) & (out_done | stale | branch_i) & rvd_done | :729-734, :721 |
| F15 | ERR capture | `fill_err_q[b]` set by `fill_rvd_arb & instr_err_i` on beat b, sticky while busy | :947-950 |

Unreachable: none identified (BranchCache=0 so `gen_caching_logic` :659-679 is not elaborated;
`gen_cache_all` :680-684 is used).
Hard to hit:
- H-F1: F5 (`fill_ext_hold_q`): the speculative request issued in the allocation cycle is not granted.
  Stimulus: `instr_gnt_i` withheld on the first request after a branch/jump.
- H-F2: all four buffers busy: `lookup_req_ic0` blocked by `~&fill_busy_q` (:249); throttle when
  `fb_fill_level > FB_THRESHOLD(2)` (:247-249). Stimulus: long `instr_rvalid_i` latency with the
  cache disabled (every fetch is a miss with 2 beats).
- H-F3: cancellation of an uncached stale line before its ext requests complete (F6 third term
  :771-773) vs completion of a cached stale line (must finish and allocate, doc icache.rst:160).
  Stimulus: tight branch loop with cache enabled vs disabled.
- H-F4: hit cancelled by ECC error (:748 `~ecc_err_ic1`) and the forced invalidation write
  (`ecc_write_req` :640, blocking lookups :250, :263). Stimulus: TB flips a bit in `ic_tag_rdata_i`
  or `ic_data_rdata_i`; observe `alert_minor_o` (rtl/ibex_core.sv:1337) and `ic_tag_write_o` next cycle.
- H-F5: `instr_err_i` on the second beat of a line only (F15 with b=1) with the first beat already
  output; error is delivered with `err_plus2_o` semantics through the skid buffer (:1194-1197).
- H-F6: `fill_rvd_arb` to an older buffer while a younger buffer hits (out-of-order data availability,
  :846-849 `fill_data_sel`).

### FSM-9 (pseudo)  ICache output skid buffer `skid_valid_q`

- Module/file: `ibex_icache`, rtl/ibex_icache.sv:176-178, :1070-1133. One-bit state.
- Arcs: `skid_valid_q` 0 -> 1 when `data_valid & ((output_addr_q[1] & (~output_compressed | output_err)) |
  (~output_addr_q[1] & output_compressed & ~output_err & ready_i))` (:1112-1115); 1 -> 0 when
  `ready_i & ((skid_data_q[1:0] != 2'b11) | skid_err_q)` (:1109) or `branch_i` (:1107).
  `skid_complete_instr` (:1096), `err_plus2_o = skid_valid_q & ~skid_err_q` (:1197).
- Doc: icache.rst:185 (16-bit skid buffer).
- Hard: H-S1 error on the second half of a misaligned 32-bit instruction (`err_plus2_o`) -> controller
  mtval = pc+2 (rtl/ibex_controller.sv:861). Stimulus: `instr_err_i` on the beat holding the upper
  halfword of an unaligned uncompressed instruction.

### FSM-10  Zcmp expansion FSM `cm_state_e` (compressed decoder)

- Module/file: `ibex_compressed_decoder`, rtl/ibex_compressed_decoder.sv (instantiated
  rtl/ibex_if_stage.sv:485-501 with `valid_i = fetch_valid & ~fetch_err` (:492) and
  `id_in_ready_i = id_in_ready_i & ~pc_set_i` (:493)).
- Type: `cm_state_e` (:181-193). Registers `cm_state_q`, `cm_state_d` (:196); reset `CmIdle` (:887);
  update `cm_state_q <= flush_expanded_i ? CmIdle : cm_state_d` (:889). Companions `cm_rlist_q`,
  `cm_sp_offset_q` (:194-195; reset only if ResetAll, :893-909). `flush_expanded = pc_set_i &
  (pc_mux_i == PC_EXC)` (rtl/ibex_if_stage.sv:483).
- States (8): CmIdle, CmPushStoreReg, CmPushDecrSp, CmPopLoadReg, CmPopIncrSp, CmPopZeroA0,
  CmPopRetRa, CmMvSecondReg.
- Output `gets_expanded_o` (INSTR_NOT_EXPANDED / INSTR_EXPANDED / INSTR_EXPANDED_COMMIT /
  INSTR_EXPANDED_LAST, rtl/ibex_pkg.sv:319-324) gates IF `fetch_ready` (rtl/ibex_if_stage.sv:808-809),
  controller irq/debug masking (rtl/ibex_controller.sv:474-477, :500), PC-increment check
  (rtl/ibex_if_stage.sv:667-669) and `instr_perf_count_id_o` (rtl/ibex_id_stage.sv:1218-1220).
- Doc: doc/03_reference/pipeline_details.rst:96-105 (Zcmp push/pop, move).

| # | FROM -> TO | Condition (instruction class from `instr_i[15:13]=3'b101, [1:0]=2'b10`, `[12:8]`) | Line |
|---|---|---|---|
| Z1 | CmIdle -> CmIdle (illegal) | cm.push/pop* with `rlist <= 3` -> `illegal_instr_o` | :635-637, :703-705 |
| Z2 | CmIdle -> CmPushDecrSp | cm.push, `rlist == 4` (only ra), `valid_i & id_in_ready_i` | :638-643 |
| Z3 | CmIdle -> CmPushStoreReg | cm.push, `rlist > 4`, `valid_i & id_in_ready_i`; sp_offset := 2 | :644-656 |
| Z4 | CmPushStoreReg -> CmPushStoreReg | `id_in_ready_i & cm_rlist_q != 4` (next register) | :658-672 |
| Z5 | CmPushStoreReg -> CmPushDecrSp | `id_in_ready_i & cm_rlist_q == 4` | :666-670 |
| Z6 | CmPushDecrSp -> CmIdle | `id_in_ready_i`; `gets_expanded = INSTR_EXPANDED_LAST` | :673-681 |
| Z7 | CmIdle -> CmPopIncrSp | cm.pop/popretz/popret, `rlist == 4`, `valid_i & id_in_ready_i` | :706-711 |
| Z8 | CmIdle -> CmPopLoadReg | cm.pop*, `rlist > 4`, `valid_i & id_in_ready_i` | :712-721 |
| Z9 | CmPopLoadReg -> CmPopLoadReg | `id_in_ready_i & cm_rlist_q != 4` | :723-737 |
| Z10 | CmPopLoadReg -> CmPopIncrSp | `id_in_ready_i & cm_rlist_q == 4` | :731-735 |
| Z11 | CmPopIncrSp -> CmPopZeroA0 | cm.popretz (`[12:8]=5'b11100`) & `id_in_ready_i`; COMMIT | :744-747 |
| Z12 | CmPopIncrSp -> CmPopRetRa | cm.popret (`5'b11110`) & `id_in_ready_i`; COMMIT | :748 |
| Z13 | CmPopIncrSp -> CmIdle | cm.pop & `id_in_ready_i`; LAST | :749-753 |
| Z14 | CmPopZeroA0 -> CmPopRetRa | `id_in_ready_i`; COMMIT | :757-764 |
| Z15 | CmPopRetRa -> CmIdle | `id_in_ready_i`; LAST (`ret` micro-op, causes pc_set PC_JUMP from ID) | :765-772 |
| Z16 | CmIdle -> CmMvSecondReg | cm.mvsa01 (`[12:8]=5'b011??`, `[6:5]=2'b01`) or cm.mva01s (`[6:5]=2'b11`), `valid_i & id_in_ready_i`; COMMIT | :785-794, :813-822 |
| Z17 | CmMvSecondReg -> CmIdle | `id_in_ready_i`; LAST | :795-803, :823-831 |
| Z18 | any -> CmIdle | `flush_expanded_i` (exception/IRQ/debug entry PC set) | :889 |
| Z19 | mismatched-state defaults -> CmIdle | `cm_state_q` not matching the instruction class | :682, :773, :804, :832 |
| Z20 | Zcmp in CHERIoT mode -> illegal | `cheriot_enable_i == IbexMuBiOn` | :615-620 |

Unreachable: U-Z1 = Z20 (CHERIoT off). U-Z2..U-Z5 = the four Z19 defaults: the decoder input
`instr_i` is frozen while expanding because `fetch_ready` is low (rtl/ibex_if_stage.sv:808-809), so a
different instruction class cannot appear with a non-idle `cm_state_q`; any redirect goes through Z18
or the ret micro-op completes Z15 first. Total 5 (the Z19 claim is by reasoning over :808-809 and
:889; label "unverified by simulation").
Hard to hit:
- H-Z1: Z18 mid-sequence via a data-side fault: cm.pop `lw` micro-op gets `data_err_i` -> WB
  exception -> FLUSH -> `pc_set & PC_EXC` -> `flush_expanded` -> CmIdle; mepc = pc_wb (the cm.pop PC).
  Stimulus: `cm.pop {ra,s0-s2},32` with an error on the 2nd load response.
- H-Z2: Z18 via interrupt while `gets_expanded == INSTR_EXPANDED` (allowed) but not during COMMIT
  (rtl/ibex_controller.sv:500): assert `irq_timer_i` during a long `cm.push {ra,s0-s11},64` and
  check that mepc points at the cm.push and re-execution restarts from CmIdle (stores repeat).
- H-Z3: debug request during expansion (masked :474-477): `debug_req_i` during cm.popret must
  wait until INSTR_EXPANDED_LAST; dpc = next PC after the `ret`.
- H-Z4: `id_in_ready_i` port de-asserted by `pc_set_i` (rtl/ibex_if_stage.sv:493) in the CmPopRetRa
  cycle: the `ret` sets pc_set the cycle it executes in ID, one cycle after Z15; verify no double step.
- H-Z5: `rlist` = 15 (x26/x27 via `cm_rlist_init` returning 16, :170-175) - longest sequences (13 stores).
- H-Z6: illegal Z1 after a legal partial? Not possible (rlist is static per instruction); but an
  illegal cm.* with `valid_i=0` must not move the FSM (assert :937 `IbexPushPopFSMStable`).

### FSM-11 (pseudo)  Dummy-instruction inserter

- Module/file: `ibex_dummy_instr`, rtl/ibex_dummy_instr.sv (instantiated rtl/ibex_if_stage.sv:504-545).
- The enum `dummy_instr_e {DUMMY_ADD, DUMMY_MUL, DUMMY_DIV, DUMMY_AND}` (:36-41) is an instruction
  type selector taken from LFSR bits (:93, :118-141), not a state register. The sequencing state is
  the counter `dummy_cnt_q` (:53; flop :106-112) plus the LFSR state in `prim_lfsr` (`lfsr_q`,
  vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv:246, :485-489).
- Arcs: COUNT -> COUNT: `dummy_cnt_en = dummy_instr_en_i & id_in_ready_i & (fetch_valid_i |
  insert_dummy_instr)` increments (:98-104); COUNT -> INSERT: `insert_dummy_instr = dummy_instr_en_i &
  (dummy_cnt_q == dummy_cnt_threshold)` (:115) where threshold = LFSR cnt field & mask (:97);
  INSERT -> COUNT(0): `dummy_cnt_d = 0` on insert (:100), LFSR advances on `lfsr_en = insert &
  id_in_ready_i` (:64); reseed on `dummy_instr_seed_en_i` (:66-74, :85-86).
- Doc: doc/03_reference/security.rst:41-70.
- Unreachable: none. Hard: H-Y1 threshold 0 (mask & LFSR field = 0) gives back-to-back dummies;
  H-Y2 DUMMY_DIV (`dummy_set=7'b0000001, opcode=3'b100`, :128-131) inserts a 37-cycle divide -
  combine with an interrupt to check the dummy is not visible (RVFI suppression rtl/ibex_core.sv:1864,
  :1905); H-Y3 dummy inserted while an expansion or exception is pending (`instr_err_out` forced 0 for
  dummies :530, `stall_dummy_instr` :535). `prim_lfsr` lockup protection (prim_lfsr.sv:299) is
  unreachable from a non-zero seed under normal operation (unverified, by LFSR maximal-length property).

### FSM-12 (pseudo)  Controller mode flags `debug_mode_q` / `nmi_mode_q`

- rtl/ibex_controller.sv:139-140, flops :1033/:1035, :1043/:1045.
- `debug_mode_q`: 0 -> 1 in DBG_TAKEN_IF (:779) or DBG_TAKEN_ID (:810); 1 -> 0 in FLUSH on `dret_insn`
  (:961-965). Consumers: `enter_debug_mode*` (:474-477), `handle_irq` (:498), `ebrk` handling (:875),
  `exc_pc_mux_o` (:831), `do_single_step_d` (:462), cs_registers `debug_mode_i` (rtl/ibex_cs_registers.sv:
  402 illegal debug CSR access, :918 no CSR update on exception in debug, :1970-1971 icache disabled
  in debug), pmp `debug_mode_i` (rtl/ibex_pmp.sv:239-240 DM range allowed), id_stage `illegal_dret_insn` (:604).
- `nmi_mode_q`: 0 -> 1 in IRQ_TAKEN when `irq_nm & !nmi_mode_q` (:736-745); 1 -> 0 in FLUSH on mret
  (:958-960). Consumers: `handle_irq` (:498), cs_registers `nmi_mode_i` (mstack restore :967-974).
- Unreachable: none. Hard: H-N1 dret while `nmi_mode_q` (debug entered during an NMI handler,
  then dret) leaves `nmi_mode_q` set; H-N2 NMI arriving while `debug_mode_q` is ignored (:498) and
  must be taken after dret (level-sensitive).

### FSM-13 (pseudo)  Writeback stage valid `wb_valid_q`

- rtl/ibex_wb_stage.sv:91, :107 (`wb_valid_d = (en_wb_i & ready_wb_o) | (wb_valid_q & ~wb_done)`),
  :118-124. `wb_done = (type == WB_INSTR_OTHER & ~cheriot ld/st) | lsu_resp_valid_i` (:115-116);
  `ready_wb_o = ~wb_valid_q | wb_done` (:185).
- Pseudo-states: EMPTY; VALID_OTHER (done same cycle); VALID_LOAD / VALID_STORE (wait for
  `lsu_resp_valid_i`). Arcs: EMPTY -> VALID_x on `en_wb_i` (:143-158 capture); VALID_LOAD/STORE ->
  EMPTY or directly -> VALID_x (back-to-back with `en_wb_i & ready_wb_o`) on `lsu_resp_valid_i`.
- Unreachable: the `wb_is_cheriot_q & (load|store)` terms (:115-116, :190-196) are constant 0 because
  `instr_is_cheriot_id_o`, `cheriot_load_o`, `cheriot_store_o` are asserted 0 with CHERIoT off
  (rtl/ibex_id_stage.sv:1297-1299) - 1 unreachable term. `g_bypass_wb` (:248-295) not elaborated.
- Hard: H-W1 VALID_LOAD held for many cycles while ID retires nothing (`stall_wb`, rtl/ibex_id_stage.sv:1133)
  with a following non-memory instruction ready; H-W2 store in WB receiving `lsu_resp_err_i` with
  `perf_instr_ret_wb_o` suppressed (:208-209) - check minstret does not count the faulting store.

### FSM-14 (pseudo)  Double-fault detector (cpuctrlsts.sync_exc_seen / double_fault_seen)

- rtl/ibex_cs_registers.sv:935-945 (set on synchronous exception when `!debug_mode_i`), :962-965
  (cleared on mret), :942-943 (`double_fault_seen_o` pulse and sticky CSR bit); CSR flop is
  `u_cpuctrlsts_part_csr` (:1973-1984).
- Pseudo-states: CLEAN -> SYNC_SEEN (first sync exception) -> DOUBLE (second sync exception before
  mret; `double_fault_seen_o` = 1 for one cycle, rtl/ibex_core.sv:131) ; SYNC_SEEN -> CLEAN on mret.
  Interrupts (`mcause.irq_ext|irq_int`) do not set the flag (:935).
- Doc: doc/03_reference/exception_interrupts.rst:183-195.
- Hard: H-DF1 exception inside the exception handler before mret (e.g. illegal instruction at
  mtvec) ; H-DF2 exception in debug mode must NOT set the flag (:918).

### Not FSMs (checked and excluded)

- `prim_secded_inv_39_32_enc/dec`, `prim_secded_inv_64_57_*`, `prim_secded_inv_28_22_*`: purely
  combinational (`always_comb` only; zero `always_ff` across vendor/lowrisc_ip/ip/prim/rtl/prim_secded_*.sv).
- `prim_lfsr`: single shift register `lfsr_q` (prim_lfsr.sv:246, :485-489) with lockup reseed; no FSM.
- `ibex_alu`: combinational; multicycle bitmanip ops use `imd_val_we_o` (rtl/ibex_alu.sv:1205-1287)
  and the ID `imd_val_q` registers, sequenced by FSM-4 (`alu_multicycle_dec`, rtl/ibex_decoder.sv:
  1111-1141 CRC32*, :1159 FSR imm, :1176 ROR imm, :1212-1239 CMIX/CMOV/FSL/FSR, :1267-1273 ROL/ROR).
  With RV32BOTEarlGrey, BCOMPRESS/BDECOMPRESS (:1344-1350) are RV32BFull only -> those `alu_multicycle_o`
  branches are unreachable (2 arcs, counted in section 3 as U-A1, U-A2).
- `ibex_decoder`: one flop `use_rs3_q` (rtl/ibex_decoder.sv:174-181), a 1-cycle delay, not an FSM.
- `ibex_cheriot_ex`: flops `cheriot_wb_err_q`, `cheriot_wb_err_info_q` (rtl/ibex_cheriot_ex.sv:925-938);
  `cheriot_wb_err_d` is gated by `cheriot_exec_id_i` (:880) which is 0 with CHERIoT off
  (rtl/ibex_id_stage.sv:1069, :1300). Passthrough for the RV32 LSU path verified: `lsu_req_o`
  (:943), `rv32_addr_incr_req_o = ((cheriot_enable_i != IbexMuBiOn) | instr_is_rv32lsu_i) ? addr_incr_req_i : 0`
  (:970-971), `rv32_addr_last_o = addr_last_i` (:973).
- `ibex_counter`, `ibex_csr`: plain registers (rtl/ibex_counter.sv:67-76, rtl/ibex_csr.sv:28-41).
- `ibex_register_file_ff`: register array only (rtl/ibex_register_file_ff.sv:88-240 `g_cheriot_rf`
  is elaborated for BaseIsaRV32IorCHERIoT; with CHERIoT off the shared bank holds x16-x31 data, :99, :131-142).
- `ibex_pmp`: combinational (rtl/ibex_pmp.sv, no always_ff).
- `ibex_wb_stage` (see FSM-13), `ibex_if_stage` `instr_valid_id_q` (rtl/ibex_if_stage.sv:568-580):
  1-bit valid, described under paths P2/P3.
- Not elaborated at all in this DUT: `ibex_multdiv_slow` (md_fsm_e, rtl/ibex_multdiv_slow.sv:47),
  `gen_mult_fast` ALBL/ALBH/AHBL/AHBH (rtl/ibex_multdiv_fast.sv:264-382), `ibex_prefetch_buffer`,
  `ibex_fetch_fifo`, `ibex_branch_predict` (rtl/ibex_if_stage.sv:348-414, :694-798).

## 2. Cross-module control paths worth covering

Notation: `module.port` with the driving/consuming file:line. "Boundary" = observable at the
ibex_core ports (instr_*/data_* buses, irq_pending_o, core_busy_o, alert_*, double_fault_seen_o,
ic_*/rf_* ports, RVFI). Instance names: `if_stage_i`, `id_stage_i` (contains `controller_i`,
`decoder_i`), `ex_block_i` (contains `alu_i`, `multdiv_i`), `g_cheriot_ex.u_ibex_cheriot_ex`,
`load_store_unit_i`, `wb_stage_i`, `cs_registers_i`, `g_pmp.pmp_i`, `if_stage_i.gen_icache.icache_i`,
`if_stage_i.compressed_decoder_i`, `if_stage_i.gen_dummy_instr.dummy_instr_i`.

### P1  ID-stage stall sources

- Aggregation: `id_stage.stall_id = stall_ld_hz | stall_mem | stall_multdiv | stall_jump | stall_branch | stall_alu`
  (rtl/ibex_id_stage.sv:983); `stall_wb = en_wb_o & ~ready_wb_i` (:1133); both -> `controller.stall_id_i/stall_wb_i`
  (:710-711) -> `controller.stall` (rtl/ibex_controller.sv:1017) -> `id_in_ready_o = ~stall & ~halt_if & ~retain_id`
  (:1020) -> `id_stage.id_in_ready_o` (:653) -> `if_stage.id_in_ready_i` (rtl/ibex_core.sv:626) ->
  `fetch_ready` (rtl/ibex_if_stage.sv:808) -> `icache.ready_i` (:316).
- multdiv: `stall_multdiv` (:917, :962) from `~ex_valid_i` (:912) where `ex_block.ex_valid_o = multdiv_sel ?
  multdiv_valid : ~|alu_imd_val_we` (rtl/ibex_ex_block.sv:197), `multdiv_valid = mult_valid | div_valid`
  (rtl/ibex_multdiv_fast.sv:529). Enables `mult_en_ex_o/div_en_ex_o = instr_executing ? *_dec : 0` (:733-734, :755-756).
- load/store: `stall_mem = instr_valid_i & (outstanding_memory_access | (lsu_req_dec & ~lsu_req_done_i))`
  (:1095-1096); `lsu.lsu_req_done_o` (rtl/ibex_load_store_unit.sv:632-633) -> core :1109 -> id :768;
  `outstanding_memory_access = (outstanding_load_wb_i | outstanding_store_wb_i) & ~lsu_resp_valid_i` (:1015-1016)
  from `wb_stage.outstanding_*_wb_o` (rtl/ibex_wb_stage.sv:193-196) and `lsu.lsu_resp_valid_o` (:694).
- branch: `stall_branch = (~BranchTargetALU & branch_decision_i) | data_ind_timing_i` (:927) -> only DIT stalls;
  `branch_decision_i` = `ex_block.branch_decision_o = alu_cmp_result` (rtl/ibex_ex_block.sv:92).
- jump: `stall_jump = ~BranchTargetALU` (:940) = 0. The jump cost is the IF bubble after `pc_set` (P3).
- WB hazard: `stall_ld_hz = outstanding_load_wb_i & (rf_rd_a_hz | rf_rd_b_hz)` (:1120), matches at :1103-1104
  against `wb_stage.rf_waddr_wb_o` (:181); non-load results are forwarded instead (:1117-1118 using
  `wb_stage.rf_write_wb_o` :190 and `rf_wdata_fwd_wb_o` :215).
- fetch not valid: `instr_valid_id = 0` -> `instr_executing_spec = 0` (:1054-1057); `perf_iside_wait =
  id_in_ready & ~instr_valid_id` (rtl/ibex_core.sv:635) -> `cs_registers.iside_wait_i` (:1553) -> mhpmcounter.
- CSR: `csr_pipe_flush` (:595-597; exempt mscratch/mepc :593) -> `controller.csr_pipe_flush_i` (:633) ->
  `special_req_flush_only` (rtl/ibex_controller.sv:287) -> C10 FLUSH with no pc_set (1-cycle bubble, IF held by halt_if).
  Also `illegal_csr_insn_i` from `cs_registers.illegal_csr_insn_o` (rtl/ibex_core.sv:1544) kills the write (:463).
- Boundary: no bus activity for multdiv/ALU stalls; mhpmcounter values (`mul_wait_i`, `div_wait_i`,
  `dside_wait_i`, `iside_wait_i`, rtl/ibex_core.sv:1553-1561), RVFI retire spacing, `core_busy_o` stays On.

### P2  Pipeline flushes (controller FLUSH, instr_valid_clear, pc_set)

- `controller.flush_id` (rtl/ibex_controller.sv:602, :611, :770, :793, :819) -> `flush_id_o` (:1002) ->
  `id_stage.flush_id` (:712) -> `instr_done = ~stall_id & ~flush_id & instr_executing` (:991) -> `en_wb_o` (:1224)
  = 0 so the flushed instruction never enters WB; `rf_we_id_o` depends on `instr_executing` (:463) which is
  killed by `instr_kill` (:1033-1036) for fetch-error/WB-exception/`~controller_run` cases.
- `controller.instr_valid_clear_o = ~(stall | retain_id) | flush_id` (:1027) -> `if_stage.instr_valid_clear_i`
  (rtl/ibex_core.sv:601) -> `instr_valid_id_d` (rtl/ibex_if_stage.sv:568-569); `retain_id` (:668) holds the
  instruction valid across the DECODE -> FLUSH wait.
- `controller.pc_set_o` (:585, :593, :730, :771, :795, :829, :956, :963) with `pc_mux_o`/`exc_pc_mux_o`
  -> `if_stage.pc_set_i/pc_mux_i/exc_pc_mux_i` (rtl/ibex_core.sv:602-605) -> `fetch_addr_n` (rtl/ibex_if_stage.sv:241-253),
  `branch_req = pc_set_i` (:418) -> `prefetch_branch` (:287) -> `icache.branch_i/addr_i` (:313-314) ->
  `fill_stale` (rtl/ibex_icache.sv:741), `output_addr_d` (:1147), skid clear (:1107), immediate lookup
  (:249-251) and speculative `instr_req_o` (:1030-1031, :703).
- Boundary: `instr_req_o` with `instr_addr_o` = new target in the same cycle as `pc_set` (if `req_i` and a
  fill buffer is free); `csr_mtvec_init_o` (:256) on the boot pc_set; RVFI `rvfi_trap` (rtl/ibex_core.sv:1885-1886,
  :2074), `rvfi_pc_wdata = pc_set ? branch_target_ex : pc_if` (:2084), `rvfi_flush_next` (rtl/ibex_controller.sv:1122).
- Zcmp: `flush_expanded = pc_set_i & (pc_mux_i == PC_EXC)` (rtl/ibex_if_stage.sv:483) resets FSM-10 (Z18).

### P3  Bubbles (IF/ID valid gaps)

- Sources of `~instr_valid_id` with `id_in_ready`: fetch latency after any `pc_set` (P2); `halt_if` in DECODE while
  waiting for `id_wb_pending` before IRQ/debug (rtl/ibex_controller.sv:700-702), in FLUSH/WAIT_SLEEP/SLEEP (:601, :610, :818),
  and when `~instr_exec_i` (:996-999); dummy insertion `stall_dummy_instr` (rtl/ibex_if_stage.sv:535, :808)
  which occupies an ID slot with `dummy_instr_id`; Zcmp expansion holding `fetch_ready` low (:808-809);
  icache throttling (`lookup_throttle` rtl/ibex_icache.sv:247-249), all fill buffers busy (:249), ECC
  correction write (:250), invalidation blocking allocation (:266, :683); `req_i` low (fetch_enable, WFI).
- `if_stage.instr_new_id_o` (:570, :584) distinguishes a fresh instruction from a held one (RVFI only, rtl/ibex_core.sv:1858).
- Boundary: gaps in `instr_req_o`/`instr_rvalid_i` consumption, `perf_iside_wait` counter, RVFI `rvfi_valid` gaps.

### P4  Exception entry by cause

- Fetch bus error: `instr_err_i` (rtl/ibex_core.sv:75 -> if_stage :562) -> `instr_err = instr_intg_err | instr_bus_err_i`
  (rtl/ibex_if_stage.sv:281) -> `icache.instr_err_i` (:328) -> `fill_err_q` (rtl/ibex_icache.sv:947-950) -> `err_o/err_plus2_o`
  (:1194-1197) -> `if_instr_err` (:430) -> `instr_fetch_err_o` flop (:606-607) -> `id_stage.instr_fetch_err_i` (:709)
  -> `controller.instr_fetch_err` (rtl/ibex_controller.sv:233) -> `exc_req_d` (:268) -> C10 -> `ExcCauseInstrAccessFault`,
  `csr_mtval_o = pc_id (+2 if plus2)` (:859-861), `csr_save_id_o` (:837). `instr_kill` blocks execution (rtl/ibex_id_stage.sv:1033).
- Fetch integrity (MemECC): `instr_intg_err` (rtl/ibex_if_stage.sv:268-276) also -> `instr_intg_err_o = & instr_rvalid_i`
  (:282) -> `alert_major_bus_o` (rtl/ibex_core.sv:1353) in the response cycle, plus the same fetch-error trap later.
- Fetch PMP: `g_pmp.pmp_i.pmp_req_err_o[PMP_I/PMP_I2]` (rtl/ibex_pmp.sv:251; addresses `pc_if`, `pc_if+2`,
  rtl/ibex_core.sv:1587-1602) -> `if_stage.pmp_err_if_i/pmp_err_if_plus2_i` (:597-598) -> `if_instr_pmp_err` (rtl/ibex_if_stage.sv:426-427)
  -> same trap path; `instr_req_o` is NOT suppressed (see section 0 note).
- Illegal instruction: `decoder.illegal_insn_o` (rtl/ibex_decoder.sv:1451) | `illegal_csr_insn_i` (cs_registers, rtl/ibex_core.sv:1544)
  | `illegal_dret_insn` | `illegal_umode_insn` (rtl/ibex_id_stage.sv:604-611) -> `controller.illegal_insn_i` -> `illegal_insn_d/q`
  (rtl/ibex_controller.sv:255, :1050) -> `exc_req_d` -> C10 -> `ExcCauseIllegalInsn`, mtval = instruction bits (:864-868).
  Compressed-decoder illegal: `illegal_c_insn` (rtl/ibex_if_stage.sv:500 -> :612) -> `decoder.illegal_c_insn_i` (rtl/ibex_id_stage.sv:504).
- ECALL / EBREAK: `decoder.ecall_insn_o` (rtl/ibex_decoder.sv:736) / `ebrk_insn_o` (:740) -> controller :227/:231 ->
  `exc_req_d` -> C10 -> `ExcCauseEcallMMode/UMode` by `priv_mode_i` (:870-873); EBREAK -> C18 (debug) or `ExcCauseBreakpoint` (:892).
- Load/store bus error: `data_err_i` (rtl/ibex_core.sv:88 -> lsu :1079) -> `data_or_pmp_err` (rtl/ibex_load_store_unit.sv:688)
  -> `load_err_o/store_err_o` qualified by `lsu_resp_valid_o` (:746-747) -> `g_check_mem_response` requires
  `outstanding_load_wb | expecting_load_resp_id` (rtl/ibex_core.sv:1184-1185; `expecting_*` are 0 with WB, rtl/ibex_id_stage.sv:1140-1141)
  -> `id_stage.lsu_load_err_i/lsu_store_err_i` (:773, :775) -> `controller.load_err_i/store_err_i` (:667, :670) ->
  `exc_req_wb` (rtl/ibex_controller.sv:275-276), `wb_exception_o` (:336) -> C10 via `wb_exception_o`; in FLUSH
  `csr_save_wb_o` (:839) so mepc = `pc_wb` (rtl/ibex_cs_registers.sv:901-903); cause :910/:924, mtval = `lsu_addr_last_i`.
- Load/store PMP: `pmp_req_err[PMP_D]` (rtl/ibex_core.sv:1630/:1634; address `data_addr_o`, type by `data_we_o`,
  privilege `priv_mode_lsu` with MPRV, :1597-1604, rtl/ibex_cs_registers.sv:998) -> `data_req_o` gated (:1063) and
  `lsu.data_pmp_err_i` (:1080) -> `pmp_err_d` (rtl/ibex_load_store_unit.sv:434, :472, :512, :553) -> `all_resp` (:692)
  -> response without any bus transaction -> same exception path (`ls_pmp_exception` fcov :803).
- Misaligned: no misaligned trap for RV32 accesses (split, rtl/ibex_load_store_unit.sv:403-405); `ExcCauseLoad/StoreAddrMisaligned`
  only via CHERIoT (rtl/ibex_controller.sv:903, :917) - unreachable. Instruction misaligned impossible (doc exception_interrupts.rst:128-130).
- Boundary: `instr_addr_o` = `{mtvec[31:8], 8'h00}` (rtl/ibex_if_stage.sv:222-224); RVFI `rvfi_trap`; `double_fault_seen_o`
  on a second synchronous trap (FSM-14); `crash_dump_o.exception_pc/exception_addr` (rtl/ibex_core.sv:1329-1330).

### P5  Interrupt entry

- External/timer/software/fast: `irq_*_i` (rtl/ibex_core.sv:119-122) -> `cs_registers` (:1493-1496) -> `mip` (rtl/ibex_cs_registers.sv:409-412)
  -> `irqs_o = mip & mie_q` (:1044), `irq_pending_o = |irqs_o` (:1045) -> core `irq_pending_o` (boundary, combinational, :1498)
  and -> `id_stage.irq_pending_i/irqs_i` (:784-785) -> `controller.handle_irq = ~debug_mode_q & ~debug_single_step_i & ~nmi_mode_q
  & (irq_nm | (irq_pending_i & irq_enabled)) & !(COMMIT)` (rtl/ibex_controller.sv:498-500), `irq_enabled = csr_mstatus_mie_i |
  (priv_mode_i == PRIV_LVL_U)` (:490) -> C12/C7 -> IRQ_TAKEN: cause priority fast(lowest id) > external > software > timer
  (:746-758, `mfip_id` :503-511); `pc_set_o`, `csr_save_if_o`, `csr_save_cause_o` (:730-733) -> `if_stage.exc_pc =
  {mtvec[31:8], 1'b0, irq_vec, 2'b00}` (rtl/ibex_if_stage.sv:225-228) ; `cs_registers` mepc = pc_if, mstatus.mie = 0 (:895-896, :921-931).
- NMI: `irq_nm_i` (rtl/ibex_core.sv:123 -> id :786 -> controller `irq_nm_ext_i` :684) -> `irq_nm` (:487) -> `handle_irq` regardless
  of mie -> `nmi_mode_d = 1` (:745), `ExcCauseIrqNm` (:738) -> vector 31 (mtvec + 0x7C); `nmi_mode_o` -> `cs_registers.nmi_mode_i`
  (:1497) -> mstack save/restore (:933, :967-974).
- Internal NMI (ECC): `lsu.load/store_resp_intg_err_o` (rtl/ibex_load_store_unit.sv:756-757) -> `id_stage.mem_resp_intg_err`
  (:613) -> `controller.mem_resp_intg_err_i` -> `g_intg_irq_int` pending flop (rtl/ibex_controller.sv:393-438) -> `irq_nm_int`
  -> cause `{irq_int:1, NMI_INT_CAUSE_ECC}` (:739), mtval = captured `lsu_addr_last_i` (:416, :742); `if_stage` forces
  `irq_vec` to the NMI vector for `irq_int` (rtl/ibex_if_stage.sv:216-219); cleared on `entering_nmi & !irq_nm_ext_i` (:410).
  Same event also raises `alert_major_bus_o` (rtl/ibex_core.sv:1353) and suppresses the RF write (rtl/ibex_load_store_unit.sv:697-698).
- Boundary: `irq_pending_o`, `instr_addr_o` = handler vector, RVFI `rvfi_intr` (rtl/ibex_core.sv:2403-2415), `rvfi_ext_irq_valid`,
  `rvfi_ext_pre_mip/post_mip`, `rvfi_ext_nmi/nmi_int` (:1928-2004).

### P6  Debug entry / exit

- haltreq: `debug_req_i` (rtl/ibex_core.sv:127 -> id :794 -> controller :704) -> `enter_debug_mode_prio_d` (rtl/ibex_controller.sv:474)
  -> C11 (or C8, C20) -> DBG_TAKEN_IF: `pc_set_o`, `PC_EXC/EXC_PC_DBD` (:765-771) -> `if_stage.exc_pc = DmHaltAddr` (rtl/ibex_if_stage.sv:229);
  `csr_save_if_o + debug_csr_save_o + csr_save_cause_o` (:773-776) -> `cs_registers` dcsr.cause/prv, depc = pc_if (rtl/ibex_cs_registers.sv:910-917);
  `debug_mode_d = 1` (:779) -> `debug_mode_o` -> `cs_registers.debug_mode_i` (rtl/ibex_core.sv:1512), `pmp_i.debug_mode_i` (:1617),
  icache disabled while in/entering debug (rtl/ibex_cs_registers.sv:1970-1971 -> `icache_enable`).
- ebreak: `decoder.ebrk_insn_o` (rtl/ibex_decoder.sv:740) -> C10 -> C18 when `ebreak_into_debug` (:481-483, from `dcsr.ebreakm/ebreaku`
  rtl/ibex_cs_registers.sv:1039-1040 -> rtl/ibex_core.sv:1517-1518) -> DBG_TAKEN_ID: `csr_save_id_o` (:803) so dpc = pc_id; cause EBREAK (:520).
- trigger: `cs_registers.trigger_match_o = |(tmatch_control_q & (pc_if_i == tmatch_value_q))` (rtl/ibex_cs_registers.sv:1872-1874;
  tdata1/tdata2 writable only in debug mode :1775-1779) -> `controller.trigger_match_i` (:476) -> non-priority `enter_debug_mode`
  -> C11 -> cause TRIGGER (:519). Matches on the IF-stage PC so the trapped instruction has not executed.
- step: `dcsr.step` (rtl/ibex_cs_registers.sv:1038) -> `do_single_step_d` (rtl/ibex_controller.sv:462) -> prio -> C11 or C20; cause STEP (:522);
  interrupts masked while stepping (:498).
- dret: `decoder.dret_insn_o` (rtl/ibex_decoder.sv:746) -> C10 -> FLUSH: `PC_DRET`, `debug_mode_d = 0`, `csr_restore_dret_id_o` (:961-965)
  -> `cs_registers.priv_lvl_d = dcsr.prv` (:949-951); `if_stage.fetch_addr_n = csr_depc_i` (rtl/ibex_if_stage.sv:247).
  dret outside debug = illegal (rtl/ibex_id_stage.sv:604).
- Boundary: `instr_addr_o` = DmHaltAddr / DmExceptionAddr (rtl/ibex_if_stage.sv:229-230); `rvfi_ext_debug_mode`, `rvfi_ext_debug_req`;
  `alert_*` unaffected; `core_busy_o` On.

### P7  PMP faults: fetch vs data

- Channels: PMP_I (`pc_if`), PMP_I2 (`pc_if + 2`), PMP_D (`data_addr_o`) (rtl/ibex_core.sv:1587-1604; PMPNumChan = 3, :193);
  privilege: `priv_mode_id` for I-side, `priv_mode_lsu = mprv ? mpp : priv_lvl` for D-side (rtl/ibex_cs_registers.sv:996-998).
- Check: `region_match_all` by mode OFF/NA4/NAPOT/TOR (rtl/ibex_pmp.sv:201-213), permissions with Smepmp `mml` (:59-97) or
  original (:101-110), default-deny rules `mmwp`/U-mode (:138-139), lowest region wins (:144-149), debug-module range bypass in
  debug mode (:239-251).
- Fetch side effect: error rides with the instruction (rtl/ibex_if_stage.sv:426-435) -> trap at execution (P4); the external
  fetch still happens (no gating of `instr_req_o` in rtl/ibex_core.sv). Plus-2 case only for unaligned uncompressed (:427, :434).
- Data side effect: `data_req_o = data_req_out & ~pmp_req_err[PMP_D]` (rtl/ibex_core.sv:1063) - no transaction, LSU completes
  from `pmp_err_q` (P4, FSM-2 H-L3/H-L4), mtval from `addr_last_q`.
- CSR side: `csr_pmp_cfg_o/addr_o/mseccfg_o` (rtl/ibex_cs_registers.sv:1498-1546); writes flush the pipe (P1 CSR).
- Boundary: for I-side, `instr_req_o` present then trap; for D-side, absent `data_req_o`; both show `instr_addr_o` = mtvec.

### P8  Multi-cycle multiply / divide

- Enables: `id_stage.mult_en_ex_o/div_en_ex_o` (rtl/ibex_id_stage.sv:733-734, :755-756) -> `ex_block.mult_en_i/div_en_i`
  (rtl/ibex_core.sv:883-884) -> `multdiv_fast.mult_en_i/div_en_i` (rtl/ibex_ex_block.sv:171-172); selectors `mult_sel/div_sel`
  static from decoder (rtl/ibex_decoder.sv:1447-1448 gate `*_en_o` by `illegal_insn_o`).
- Ready/hold: `multdiv_ready_id_o = ready_wb_i` (rtl/ibex_id_stage.sv:976) -> core :741 -> ex :188 -> `mult_hold`/`div_hold`
  (rtl/ibex_multdiv_fast.sv:216, :235, :518).
- Intermediate values: `imd_val_we_o/imd_val_d_o` (rtl/ibex_multdiv_fast.sv:124-128) -> `ex_block` mux (rtl/ibex_ex_block.sv:83-85)
  -> `id_stage.imd_val_q` (rtl/ibex_id_stage.sv:446-456) -> back as `imd_val_q_i`. Divider also borrows the ALU adder
  (`alu_operand_a_o/b_o` :419-420 -> `alu_i.multdiv_operand_*` rtl/ibex_ex_block.sv:126-128, `multdiv_sel_i` :128).
- Timing: MUL 1 cycle (M1), MULH 2 (M2, M3), DIV/REM 37 (D2..D11), div-by-zero 2 (D1/D3) unless `data_ind_timing`
  (`cs_registers.data_ind_timing_o` rtl/ibex_cs_registers.sv:1905 -> rtl/ibex_core.sv:1525 -> :891 -> rtl/ibex_ex_block.sv:184).
- Boundary: no bus traffic; `perf_mul_wait/div_wait` (rtl/ibex_id_stage.sv:1226-1227 -> rtl/ibex_core.sv:1560-1561); RVFI retire
  spacing and `rvfi_rd_wdata`.

### P9  Misaligned load/store splitting and the second-half error

- Detection: `split_misaligned_access` (rtl/ibex_load_store_unit.sv:403-405) from `lsu_type_i`/`data_offset` (:131-132; offset
  = `data_addr[1:0]` with CHERIoT off).
- Second address: `lsu.addr_incr_req_o` (:507, :535, :549) -> core `lsu_addr_incr_req` -> `u_ibex_cheriot_ex.addr_incr_req_i`
  (rtl/ibex_core.sv:970) -> `rv32_addr_incr_req_o` passthrough (rtl/ibex_cheriot_ex.sv:970-971) -> `id_stage.lsu_addr_incr_req_i`
  (rtl/ibex_core.sv:770) -> operand muxes `OP_A_FWD` (= `lsu_addr_last_i`) and `IMM_B_INCR_ADDR` (= 4) (rtl/ibex_id_stage.sv:347-349,
  :362, :397) -> ALU add -> `alu_adder_result_ex` -> `u_ibex_cheriot_ex.rv32_lsu_addr_i` (rtl/ibex_core.sv:977) -> `lsu_addr_o`
  (rtl/ibex_cheriot_ex.sv:946, :953) -> `lsu.adder_result_ex_i` (rtl/ibex_core.sv:1104) -> `data_addr_o` word-aligned (:719-722).
  `lsu_addr_last_i` = `lsu.addr_last_o` (:743; `addr_last_q` :258-266, path via rtl/ibex_cheriot_ex.sv:973).
- Byte enables and data: first/second half BE (:143-175), write-data rotation (:200-208), read assembly from `rdata_q` (:230-237, :269-277).
- Error cases: first-half bus error -> `lsu_err_q` (:514), address not updated (:520) -> final `load_err_o/store_err_o` with mtval =
  first address; second-half bus error -> `data_bus_err_i` at the final rvalid (:688) with mtval = second word address;
  PMP error on either half (:472, :512, :553). Doc load_store_unit.rst:78-80.
- Pipeline: the instruction stays in ID (`stall_mem` via `~lsu_req_done_i`, rtl/ibex_id_stage.sv:1095-1096) until the second
  request is granted (`lsu_req_done` :632), then moves to WB; the exception is precise from WB (P4).
- Boundary: two `data_req_o` beats with consecutive word addresses and complementary `data_be_o`; `rvfi_mem_addr/rmask/wmask`
  (rtl/ibex_core.sv:2085-2086, :2207-2219, :2252-2261 report the un-split access).

### P10  Writeback-stage interactions

- Handshake: `id_stage.en_wb_o = instr_done` (rtl/ibex_id_stage.sv:1224) -> `wb_stage.en_wb_i` (rtl/ibex_core.sv:1132);
  `wb_stage.ready_wb_o` (rtl/ibex_wb_stage.sv:185) -> `id_stage.ready_wb_i` (:823) and `controller.ready_wb_i` (:713).
- RF write arbitration: `rf_wdata_wb_mux_we[0] = rf_we_wb_q & wb_valid_q` (:183; CHERIoT term 0) vs
  `rf_wdata_wb_mux_we[1] = rf_we_lsu_i` (:220) where `rf_we_lsu = lsu_rdata_valid & (outstanding_load_wb | expecting_load_resp_id)`
  (rtl/ibex_core.sv:1186); OR-mux (:301-303), one-hot assertion (:310) -> `rf_we_wb_o/rf_waddr_wb_o/rf_wdata_wb_ecc_o`
  (rtl/ibex_core.sv:1210-1211, :1221-1224 with ECC or :1313 without) -> `ibex_register_file_ff.we_a_i/waddr_a_i/wdata_a_i`
  (rtl/ibex_register_file_ff.sv:82-85; write decode :105-109, :116-142).
- Forwarding: `rf_wdata_fwd_wb_o` (:215) and `rf_write_wb_o` (:190) -> `id_stage` (:1117-1118); load data is never forwarded
  (`stall_ld_hz`, :1120). `u_ibex_cheriot_ex.fwd_*` (rtl/ibex_core.sv:919-922) also consume them (inert here).
- Outstanding memory: `outstanding_load_wb_o/store` (:193-196) -> `data_req_allowed` (rtl/ibex_id_stage.sv:1019), `stall_mem`,
  `perf_dside_wait` (:1135-1136).
- Exception in WB: `lsu_resp_err = lsu_load_err | lsu_store_err` (rtl/ibex_core.sv:1064) -> `wb_stage.lsu_resp_err_i` (:1176)
  suppresses `perf_instr_ret_wb_o` (rtl/ibex_wb_stage.sv:208-209); controller `wb_exception_o` kills ID (P4); `csr_save_wb` uses
  `pc_wb_o` (:198). `instr_done_wb_o` (:200) -> `rvfi_wb_done` (rtl/ibex_core.sv:1890) and `perf_instr_ret_wb` -> minstret
  (rtl/ibex_core.sv:1549).
- Dummy: `dummy_instr_wb_o` (:241) -> core `dummy_instr_wb_o` (:1208) -> `ibex_register_file_ff.dummy_instr_wb_i` x0 write
  enable (rtl/ibex_register_file_ff.sv:159, :282); `rvfi_ext_rf_wr_suppress` for integrity-suppressed loads (rtl/ibex_core.sv:2384-2395).
- Boundary: `rf_*_wb_o` ports (visible at the ibex_core/regfile seam), RVFI `rvfi_rd_addr/rvfi_rd_wdata` (:2339-2363), minstret.

### P11  ICache fill / invalidate / scramble-key request

- Enable: `cs_registers.icache_enable_o = cpuctrlsts.icache_enable & ~(debug_mode_i | debug_mode_entering_i)` (rtl/ibex_cs_registers.sv:1970-1971)
  -> rtl/ibex_core.sv:1530 -> `if_stage.icache_enable_i` (:611) -> `icache.icache_enable_i` (rtl/ibex_if_stage.sv:343) ->
  `lookup_actual_ic0` (rtl/ibex_icache.sv:266), `fill_cache_new` (:683), `fill_spec_req` (:703), `instr_req` (:1030).
- Invalidate: `decoder.icache_inval_o` on FENCE.I first cycle (rtl/ibex_decoder.sv:721; also `jump_set_o` :720 so FENCE.I is a jump to PC+4)
  -> `id_stage.icache_inval_o` (rtl/ibex_id_stage.sv:498) -> core :707 -> `if_stage.icache_inval_i` (:612) -> `icache.icache_inval_i`
  (rtl/ibex_if_stage.sv:344) -> FSM-7 V4/V7 and `fill_cache_d` clear (rtl/ibex_icache.sv:746).
- Scramble key: `icache.ic_scr_key_req_o` (:1213, :1226, :1251, :1261) -> `if_stage` (:341) -> core `ic_scr_key_req_o` (:576, boundary);
  `ic_scr_key_valid_i` (rtl/ibex_core.sv:115 -> :575 -> rtl/ibex_if_stage.sv:340 -> rtl/ibex_icache.sv:1225, :1235) and ->
  `cs_registers.ic_scr_key_valid_i` (:1532) -> `cpuctrlsts.ic_scr_key_valid` (rtl/ibex_cs_registers.sv:1938-1949) -> RVFI
  `rvfi_ext_ic_scr_key_valid` (rtl/ibex_core.sv:2103).
- RAM traffic: `ic_tag_req_o/ic_tag_write_o/ic_tag_addr_o/ic_tag_wdata_o` (rtl/ibex_icache.sv:445-450) - during INVAL_CACHE one tag write
  per cycle with valid bit 0 (:257, :270, :277); allocations write tag + data (`fill_grant_ic0` :263-264, data :459-464); lookups read
  both ways (:276). ECC encode/decode (:286-315, :538-644); `ecc_error_o` -> `alert_minor_o` (rtl/ibex_core.sv:1337).
- Busy: `busy_o = inval_active | |(fill_busy_q & ~fill_rvd_done)` (:1304) -> `if_busy` (rtl/ibex_if_stage.sv:421) -> `core_busy_o`
  (rtl/ibex_core.sv:498-522, multi-bit for SecureIbex).
- Boundary: `ic_scr_key_req_o` pulse pattern, `ic_tag_*`/`ic_data_*` RAM ports, `instr_req_o` pattern (2 beats per line on miss,
  none on hit), `alert_minor_o`, `core_busy_o`.

### P12  Dummy instruction insertion

- Config: `cs_registers.dummy_instr_en_o/mask_o` (rtl/ibex_cs_registers.sv:1931-1932), `dummy_instr_seed_en_o/seed_o` on secureseed
  write (:1914-1919) -> rtl/ibex_core.sv:1526-1529 -> `if_stage` (:607-610) -> `dummy_instr_i` (rtl/ibex_if_stage.sv:515-518).
- Insertion: `insert_dummy_instr` (rtl/ibex_dummy_instr.sv:115) -> `instr_out` mux (rtl/ibex_if_stage.sv:526-530: R-type op with rd = x0,
  rtl/ibex_dummy_instr.sv:144; not compressed; no error) ; `stall_dummy_instr` -> `fetch_ready = 0` (:535, :808) so the real
  instruction waits one slot; `dummy_instr_id_o` flop (:538-544) -> core `dummy_instr_id_o` (:1207) -> `ibex_register_file_ff.
  dummy_instr_id_i` makes x0 read the dummy register (rtl/ibex_register_file_ff.sv:173, :186) -> `wb_stage.dummy_instr_id_i`
  (rtl/ibex_core.sv:1155) -> `dummy_instr_wb_o` (P10).
- Suppression: RVFI skips dummies (`rvfi_stage_valid_d` rtl/ibex_core.sv:1864, order :1905); PC-increment check disabled
  (rtl/ibex_if_stage.sv:667-669); `instr_perf_count_id_o` (rtl/ibex_id_stage.sv:1218-1220) has no dummy exclusion - whether
  dummies increment minstret is left "unverified" here (worth a directed check).
- Types: DUMMY_MUL/DUMMY_DIV use the multiplier/divider (rtl/ibex_dummy_instr.sv:124-131) -> P8 stalls up to 37 cycles.
- Boundary: only timing (RVFI gaps, `instr_req_o` cadence) and `rf_raddr_*`/`rf_we_wb_o` with `waddr = 0` and `dummy_instr_wb_o`
  at the regfile seam.

### P13  fetch_enable_i gating and WFI sleep / wake

- Gating: `instr_req_gated = instr_req_int & (fetch_enable_i == IbexMuBiOn)` (rtl/ibex_core.sv:648) -> `if_stage.req_i` (:553) ->
  `icache.req_i` (rtl/ibex_if_stage.sv:311) -> `lookup_req_ic0` (rtl/ibex_icache.sv:249): no new fetches, outstanding fills complete.
  `instr_exec = (fetch_enable_i == IbexMuBiOn)` (:649) -> `id_stage.instr_exec_i` (:699) -> `controller.instr_exec_i` (:655) ->
  `halt_if = 1` (rtl/ibex_controller.sv:996-999) -> `id_in_ready_o = 0`: the instruction already in ID finishes, no new one is accepted
  (assertion NoExecWhenFetchEnableNotOn rtl/ibex_core.sv:1419-1421). Any non-On MuBi value counts as off. `core_busy_o` stays On
  (ctrl_busy = 1 in DECODE). Related: `cheriot_enable_mubi_err = instr_exec & !(On | Off)` -> `alert_major_internal_o` (:1343, :1350).
- WFI: `decoder.wfi_insn_o` (rtl/ibex_decoder.sv:749) -> `controller.wfi_insn` (:230) -> `special_req_flush_only` (:287) -> C10 ->
  C19 WAIT_SLEEP -> C3 SLEEP; `ctrl_busy_o = 0`, `instr_req_o = 0` (:599-600, :609, :619) -> `instr_req_int` -> `instr_req_gated`
  -> `icache.req_i = 0`; `lsu_busy = ls_fsm_cs != IDLE` (rtl/ibex_load_store_unit.sv:762); `core_busy_o` -> IbexMuBiOff once
  `ctrl_busy | if_busy | lsu_busy` are all 0 (rtl/ibex_core.sv:498-522). U-mode WFI with `mstatus.tw` is illegal (rtl/ibex_id_stage.sv:606-608).
- Wake: C4 on `irq_nm | irq_pending_i | debug_req_i | debug_mode_q | debug_single_step_i` (rtl/ibex_controller.sv:615) - note
  `irq_pending_i` is `|(mip & mie)` and does NOT include `mstatus.mie`, so with mie = 0 the core wakes into FIRST_FETCH -> DECODE
  and resumes after the WFI without trapping. `instr_req_o` returns to 1 (:541) -> icache resumes at `prefetch_addr_q`
  (rtl/ibex_icache.sv:251; no pc_set on wake). If `handle_irq`: C7 IRQ_TAKEN.
- Boundary: `instr_req_o` quiescence, `core_busy_o == IbexMuBiOff` (ibex_top would gate the clock on this, rtl/ibex_top.sv:314),
  `irq_pending_o`, `data_req_o` absent, then `instr_addr_o` = wfi+4 or handler.

## 3. Counts and unverified items

FSMs found: 8 real enum FSMs elaborated in this DUT (FSM-1 ctrl_fsm_e, FSM-2 ls_fsm_e, FSM-3 cap_rx_fsm_t,
FSM-4 id_fsm_e, FSM-5 md_fsm_e, FSM-6 mult_fsm_e single-cycle, FSM-7 inval_state_e, FSM-10 cm_state_e)
plus 6 pseudo-FSMs (FSM-8 fill buffers, FSM-9 skid buffer, FSM-11 dummy counter, FSM-12 mode flags,
FSM-13 wb_valid, FSM-14 double-fault) = 14. Two enum FSMs exist in the file set but are not elaborated
(gen_mult_fast ALBL..AHBH, ibex_multdiv_slow md_fsm_e) and one whole FSM (FSM-3) is elaborated but frozen.

Unreachable arcs/branches (this DUT): controller 13 (U-C1..U-C13), LSU 10 (U-L1..U-L10), cap_rx 5
(U-X1..U-X5), id_fsm 4 (U-I1..U-I4), divider 1 (U-D1), multiplier 1 (U-M1), inval 1 (U-V1), Zcmp 5
(U-Z1..U-Z5), wb 1 (CHERIoT terms), ALU multicycle 2 (U-A1, U-A2) = **43**.

Hard-to-reach arcs/scenarios: controller 15 (H-C1..H-C15), LSU 7 (H-L1..H-L7), id_fsm 4 (H-I1..H-I4),
divider 3 (H-D1..H-D3), multiplier 2 (H-M1..H-M2), inval 4 (H-V1..H-V4), fill buffers 6 (H-F1..H-F6),
skid 1 (H-S1), Zcmp 6 (H-Z1..H-Z6), dummy 3 (H-Y1..H-Y3), mode flags 2 (H-N1..H-N2), wb 2 (H-W1..H-W2),
double fault 2 (H-DF1..H-DF2) = **57**.

Unverified items (not directly confirmed by reading; flagged in text):
1. FSM-5 H-D3: claim that `div_en_i` cannot drop mid-division is by reasoning over rtl/ibex_id_stage.sv:1033-1062 and
   rtl/ibex_controller.sv:704; not proven - suggest a cover/assert.
2. FSM-5 H-D2: exact quotient/remainder value path for divide-by-zero under data_ind_timing (rtl/ibex_multdiv_fast.sv:430-431
   comment vs :490/:505 data path) - value correctness not traced bit-by-bit.
3. FSM-10 U-Z2..U-Z5: unreachability of the Z19 default arcs relies on `fetch_ready` being low during expansion
   (rtl/ibex_if_stage.sv:808-809) and the icache holding `rdata_o` stable while `ready_i` is low (doc icache.rst:246); not
   simulated.
4. FSM-11: `prim_lfsr` lockup-protection arc unreachable from a nonzero seed - by LFSR property, not traced through
   prim_lfsr.sv:290-350.
5. P12: whether dummy instructions increment minstret (`instr_perf_count_id_o` rtl/ibex_id_stage.sv:1218-1220 has no dummy term;
   `wb_count_q` rtl/ibex_wb_stage.sv:150) - effect not traced into `cs_registers` counters.
6. Section 0: the TB's actual `RegFileECC`/`ResetAll` parameter values for the standalone ibex_core DUT are unknown to this
   analysis; both variants are described.
7. ibex_tracer / ibex_top_tracing / ibex_lockstep / ibex_trvk were not read (outside the ibex_core.core file set).
