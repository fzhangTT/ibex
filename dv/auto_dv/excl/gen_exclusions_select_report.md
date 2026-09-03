# gen_excl_select report
dump: /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_0_rebaseline/cov_unmeasured/full_exclusions
parsed entries: 8437

config check: BranchPredictor=0 BranchTargetALU=1 RV32B=RV32BOTEarlGrey (util/ibex_config.py opentitan vcs_opts)
guard analysis ibex_core: 2 dead RTL lines
guard analysis ibex_id_stage: 11 dead RTL lines
guard analysis ibex_decoder: 150 dead RTL lines
guard analysis ibex_compressed_decoder: 33 dead RTL lines
guard analysis ibex_controller: 44 dead RTL lines
guard analysis ibex_load_store_unit: 59 dead RTL lines
guard analysis ibex_cs_registers: 37 dead RTL lines
guard analysis ibex_if_stage: 85 dead RTL lines
guard analysis ibex_wb_stage: 0 dead RTL lines
guard analysis ibex_multdiv_fast: 0 dead RTL lines
guard analysis ibex_icache: 0 dead RTL lines
guard analysis ibex_register_file_ff: 2 dead RTL lines
guard analysis ibex_cheriot_ex: 265 dead RTL lines
BLOCK ibex_core [(2223, 2225)]: 1 blocks selected (dead guard); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_id_stage [(901, 908)]: 2 blocks selected (dead guard); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_decoder [(314, 323), (339, 352), (402, 407), (447, 453), (474, 482), (793, 876), (883, 891)]: 36 blocks selected (dead guard); 0 in-range blocks kept in coverage (no dead guard); 4 A.8 carve-backs kept in coverage
    carve-back: :351 Block 18 "2452896486" "illegal_insn = 1'b1;"
    carve-back: :824 Block 148 "1906098644" "illegal_insn = 1'b1;"
    carve-back: :856 Block 164 "689554920" "illegal_insn = 1'b1;"
    carve-back: :873 Block 169 "1515370181" "illegal_insn = 1'b1;"
BLOCK ibex_compressed_decoder [(230, 233), (249, 252), (329, 332), (359, 363), (391, 394), (411, 414), (557, 560), (575, 579), (615, 620), (854, 857)]: 11 blocks selected (dead guard); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_controller [(850, 858), (894, 897), (901, 908), (915, 922), (928, 948), (318, 319), (328, 331)]: 14 blocks selected (dead guard); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_load_store_unit [(139, 140), (211, 219), (437, 467), (565, 603), (616, 623), (669, 678)]: 24 blocks selected (explicit enum-default entry); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_cs_registers [(469, 475), (478, 484), (678, 698), (707, 715), (2014, 2056), (2063, 2067), (2108, 2209), (2218, 2224)]: 17 blocks selected (dead guard); 21 in-range blocks kept in coverage (no dead guard); 3 A.8 carve-backs kept in coverage
    live: :473 Block 22 "1392153817" "csr_rdata_int = mtvec_q;"
    live: :482 Block 25 "4057767857" "csr_rdata_int = mepc_q;"
    live: :682 Block 76 "3370698267" "illegal_csr = 1'b1;"
    live: :690 Block 79 "2568516718" "illegal_csr = 1'b1;"
    live: :698 Block 82 "4048553032" "illegal_csr = 1'b1;"
    live: :2018 Block 266 "3904788274" "cheriot_csr_rdata_o = (debug_mode_i ? depc_q : '0);"
    live: :2023 Block 267 "3348321698" "cheriot_csr_rdata_o = (debug_mode_i ? dscratch0_q : '0);
    live: :2028 Block 268 "3839399327" "cheriot_csr_rdata_o = (debug_mode_i ? dscratch1_q : '0);
    live: :2033 Block 269 "2583875407" "cheriot_csr_rdata_o = mtvec_q;"
    live: :2038 Block 270 "1321462793" "cheriot_csr_rdata_o = gen_scr.mtdc_data;"
    live: :2043 Block 271 "236585115" "cheriot_csr_rdata_o = gen_scr.mscratchc_data;"
    live: :2048 Block 272 "4096631128" "cheriot_csr_rdata_o = mepc_q;"
    live: :2053 Block 273 "2749661524" "cheriot_csr_rdata_o = 32'b0;"
    live: :2065 Block 275 "4291899431" "pcc_cap_q <= 112'b10000000000000000000000000000000000000
    live: :2114 Block 292 "2707070097" "mtvec_cap <= 35'b00101011110001111100000000000000000;"
    live: :2136 Block 302 "3536564520" "mepc_cap <= 35'b00101011110001111100000000000000000;"
    live: :2155 Block 311 "3315413595" "gen_scr.mtdc_cap <= 35'b00101111110001111100000000000000
    live: :2170 Block 316 "746695531" "gen_scr.mscratchc_cap <= 35'b0010100111000111110000000000
    live: :2185 Block 321 "2244136683" "depc_cap <= 35'b0;"
    live: :2203 Block 328 "2252920583" "dscratch0_cap <= 35'b0;"
    live: :2220 Block 335 "4238278554" "gen_scr.cheriot_fatal_err_q <= 1'b0;"
    carve-back: :2128 Block 297 "268972480" "gen_scr.mstack_epc_cap_q <= 35'b0;"
    carve-back: :2130 Block 299 "1318991522" "gen_scr.mstack_epc_cap_q <= mepc_cap;"
    carve-back: :2142 Block 306 "3777635196" "mepc_cap <= gen_scr.mstack_epc_cap_q;"
BLOCK ibex_controller [(690, 696)]: 1 blocks selected (dead guard); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_decoder [(1342, 1344), (1348, 1350)]: 2 blocks selected (dead guard); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_controller [(990, 993)]: class-D spare-encoding group HELD OUT (EC-3 not filled; --allow-unfilled-ec3 to emit)
BLOCK ibex_load_store_unit [(605, 607)]: class-D spare-encoding group HELD OUT (EC-3 not filled; --allow-unfilled-ec3 to emit)
BLOCK ibex_multdiv_fast [(522, 524)]: class-D spare-encoding group HELD OUT (EC-3 not filled; --allow-unfilled-ec3 to emit)
BLOCK ibex_id_stage [(968, 970)]: 1 blocks selected (explicit enum-default entry); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_multdiv_fast [(238, 240)]: 1 blocks selected (explicit enum-default entry); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BLOCK ibex_icache [(1268, 1268)]: 1 blocks selected (explicit enum-default entry); 0 in-range blocks kept in coverage (no dead guard); 0 A.8 carve-backs kept in coverage
BRANCH ibex_core [(1000, 1001)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 1 vectors
BRANCH ibex_core [(1590, 1593), (1627, 1630)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 6 vectors
BRANCH ibex_if_stage [(222, 228)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 0 vectors
BRANCH ibex_id_stage [(578, 578), (746, 749)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 1 vectors
BRANCH ibex_decoder [(202, 202)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 0 vectors
BRANCH ibex_decoder [(212, 217)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 3 vectors
BRANCH ibex_controller [(866, 868)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 0 vectors
BRANCH ibex_load_store_unit [(131, 132), (702, 709)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 3 vectors
BRANCH ibex_wb_stage [(182, 183), (215, 215)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 2 vectors
BRANCH ibex_cs_registers [(424, 426)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 0 vectors
BRANCH ibex_register_file_ff [(113, 113), (227, 230)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 1 vectors
BRANCH ibex_controller [(684, 684)] /\) 1"$|[a-zA-Z_\]\)] 1"$/: 0 vectors
BRANCH ibex_id_stage [(936, 942)] / 0"$/: 0 vectors
CHERIOT_EX guard analysis: 265 dead RTL lines in rtl/ibex_cheriot_ex.sv (reasons in the per-group annotations)
CHERIOT_EX dead-arm blocks 75, dead-arm branch vectors 66
Conditions: 384 condition objects, 670 vectors selected (119 A.1 all-vector, 551 A.4 impossible-value).
Conditions mentioning a CHERIoT name but NOT selected (manual follow-up; kept in coverage):
  - ibex_controller ibex_controller.sv:268 ((ecall_insn | ebrk_insn | illegal_insn_d | instr_fetch_err | ((cheriot_enable_i == ibex_pkg::IbexMuBiOn) & cheriot_ex_err) | cheriot_asr_err_d) & (ctrl_fsm_cs != FLUSH))
  - ibex_controller ibex_controller.sv:271 ((ecall_insn | ebrk_insn | illegal_insn_d | instr_fetch_err | cheriot_asr_err_d) & (ctrl_fsm_cs != FLUSH))
  - ibex_controller ibex_controller.sv:837 ( ~ (store_err_q | load_err_q | ((cheriot_enable_i == ibex_pkg::IbexMuBiOn) & cheriot_wb_err_q)) )
  - ibex_core ibex_core.sv:1405 ((fetch_enable_i != ibex_pkg::IbexMuBiOn) && (last_fetch_enable == ibex_pkg::IbexMuBiOn))
  - ibex_core ibex_core.sv:1405 (fetch_enable_i != ibex_pkg::IbexMuBiOn)
  - ibex_core ibex_core.sv:1405 (last_fetch_enable == ibex_pkg::IbexMuBiOn)
  - ibex_core ibex_core.sv:1414 (SecureIbex ? (fetch_enable_i == ibex_pkg::IbexMuBiOn) : fetch_enable_i[0])
  - ibex_core ibex_core.sv:1414 (fetch_enable_i == ibex_pkg::IbexMuBiOn)
  - ibex_core ibex_core.sv:2289 (rf_ren_a ? ibex_core.g_cheriot_ex.u_ibex_cheriot_ex.rf_rcap_a : 35'b0)
  - ibex_core ibex_core.sv:2290 (rf_ren_b ? ibex_core.g_cheriot_ex.u_ibex_cheriot_ex.rf_rcap_b : 35'b0)
  - ibex_core ibex_core.sv:648 (fetch_enable_i == ibex_pkg::IbexMuBiOn)
  - ibex_core ibex_core.sv:648 (instr_req_int & (fetch_enable_i == ibex_pkg::IbexMuBiOn))
  - ibex_core ibex_core.sv:649 (fetch_enable_i == ibex_pkg::IbexMuBiOn)
  - ibex_cs_registers ibex_cs_registers.sv:2108 (cheriot_csr_addr_i == ibex_cheriot_pkg::CHERIOT_SCR_MTCC)
  - ibex_cs_registers ibex_cs_registers.sv:2108 (cheriot_csr_op_i == CHERIOT_CSR_RW)
  - ibex_cs_registers ibex_cs_registers.sv:2121 (cheriot_csr_addr_i == ibex_cheriot_pkg::CHERIOT_SCR_MEPCC)
  - ibex_cs_registers ibex_cs_registers.sv:2121 (cheriot_csr_op_i == CHERIOT_CSR_RW)
  - ibex_cs_registers ibex_cs_registers.sv:2149 (cheriot_csr_addr_i == ibex_cheriot_pkg::CHERIOT_SCR_MTDC)
  - ibex_cs_registers ibex_cs_registers.sv:2149 (cheriot_csr_op_i == CHERIOT_CSR_RW)
  - ibex_cs_registers ibex_cs_registers.sv:2164 (cheriot_csr_addr_i == ibex_cheriot_pkg::CHERIOT_SCR_MSCRATCHC)
  - ibex_cs_registers ibex_cs_registers.sv:2164 (cheriot_csr_op_i == CHERIOT_CSR_RW)
  - ibex_cs_registers ibex_cs_registers.sv:2179 (cheriot_csr_addr_i == ibex_cheriot_pkg::CHERIOT_SCR_DEPCC)
  - ibex_cs_registers ibex_cs_registers.sv:2179 (cheriot_csr_op_i == CHERIOT_CSR_RW)
  - ibex_cs_registers ibex_cs_registers.sv:2194 (cheriot_csr_addr_i == ibex_cheriot_pkg::CHERIOT_SCR_DSCRATCHC0)
  - ibex_cs_registers ibex_cs_registers.sv:2194 (cheriot_csr_op_i == CHERIOT_CSR_RW)
  - ibex_cs_registers ibex_cs_registers.sv:2197 (cheriot_csr_addr_i == ibex_cheriot_pkg::CHERIOT_SCR_DSCRATCHC1)
  - ibex_cs_registers ibex_cs_registers.sv:2197 (cheriot_csr_op_i == CHERIOT_CSR_RW)
  - ibex_cs_registers ibex_cs_registers.sv:377 ((BaseIsa == BaseIsaRV32IorCHERIoT) ? (cheriot_enable_i != ibex_pkg::IbexMuBiOn) : MISA_VALUE[8])
  - ibex_cs_registers ibex_cs_registers.sv:377 ((BaseIsa == BaseIsaRV32IorCHERIoT) ? (cheriot_enable_i == ibex_pkg::IbexMuBiOn) : MISA_VALUE[4])
  - ibex_cs_registers ibex_cs_registers.sv:377 ({MISA_VALUE[31:24],(((BaseIsa == BaseIsaRV32IorCHERIoT) ? ((cheriot_enable_i == ibex_pkg::IbexMuBiOn) || (RV32BExtra != 0)) : MISA_VALUE[23])),MISA_VALUE[22:9],((BaseIsa == BaseIsaRV32IorCHERIoT) ? (cheriot_enable_i != ibex_pkg::IbexMuBiOn) : MISA_VALUE[8]),MISA_VALUE[7:5],((BaseIsa == BaseIsaRV32IorCHERIoT) ? (cheriot_enable_i == ibex_pkg::IbexMuBiOn) : MISA_VALUE[4]),MISA_VALUE[3:0]})
  - ibex_cs_registers ibex_cs_registers.sv:739 (csr_mtvec_init_i ? ({boot_addr_i[31:8],6'b0,1'b0,( ~ ((BaseIsa == BaseIsaRV32IorCHERIoT) & (cheriot_enable_i == ibex_pkg::IbexMuBiOn)) )}) : ({csr_wdata_int[31:8],6'b0,1'b0,( ~ ((BaseIsa == BaseIsaRV32IorCHERIoT) & (cheriot_enable_i == ibex_pkg::IbexMuBiOn)) )}))
  - ibex_cs_registers ibex_cs_registers.sv:739 ({boot_addr_i[31:8],6'b0,1'b0,( ~ ((BaseIsa == BaseIsaRV32IorCHERIoT) & (cheriot_enable_i == ibex_pkg::IbexMuBiOn)) )})
  - ibex_cs_registers ibex_cs_registers.sv:739 ({csr_wdata_int[31:8],6'b0,1'b0,( ~ ((BaseIsa == BaseIsaRV32IorCHERIoT) & (cheriot_enable_i == ibex_pkg::IbexMuBiOn)) )})
  - ibex_cs_registers ibex_cs_registers.sv:845 (mcounteren_writable_i == ibex_pkg::IbexMuBiOn)
  - ibex_decoder ibex_decoder.sv:238 ((RV32E || (cheriot_enable_i == ibex_pkg::IbexMuBiOn)) && ((raddr_a[4] && rf_ren_a_o) || (raddr_b[4] && rf_ren_b_o) || (instr_rs3[4] && use_rs3_d && rf_ren_a_o) || (instr_rd[4] && rf_we_or_load)))
  - ibex_id_stage ibex_id_stage.sv:1012 ((lsu_req_dec | cheriot_lsu_req_dec) ? ((~stall_mem)) : ex_valid_all)
  - ibex_id_stage ibex_id_stage.sv:1095 ((lsu_req_dec | cheriot_lsu_req_dec) & ((~lsu_req_done_i)))
  - ibex_id_stage ibex_id_stage.sv:1095 (gen_stall_mem.outstanding_memory_access | ((lsu_req_dec | cheriot_lsu_req_dec) & ((~lsu_req_done_i))))
  - ibex_id_stage ibex_id_stage.sv:1095 (instr_valid_i & (gen_stall_mem.outstanding_memory_access | ((lsu_req_dec | cheriot_lsu_req_dec) & ((~lsu_req_done_i)))))
  - ibex_id_stage ibex_id_stage.sv:747 (csr_access_o & instr_executing & (((BaseIsa == BaseIsaRV32IorCHERIoT) & (cheriot_enable_i == ibex_pkg::IbexMuBiOn)) ? instr_first_cycle : instr_id_done_o))
  - ibex_register_file_ff ibex_register_file_ff.sv:221 ((raddr_a_i[4] && ((!g_cheriot_rf.cheriot_enabled))) ? (32'(g_cheriot_rf.rf_shared[raddr_a_i[3:0]])) : g_cheriot_rf.rf_data[raddr_a_i[3:0]])
  - ibex_register_file_ff ibex_register_file_ff.sv:223 ((raddr_b_i[4] && ((!g_cheriot_rf.cheriot_enabled))) ? (32'(g_cheriot_rf.rf_shared[raddr_b_i[3:0]])) : g_cheriot_rf.rf_data[raddr_b_i[3:0]])
  - ibex_wb_stage ibex_wb_stage.sv:115 (((g_writeback_stage.wb_instr_type_q == WB_INSTR_OTHER) && ( ~ (g_writeback_stage.wb_is_cheriot_q && (g_writeback_stage.wb_cheriot_load_q | g_writeback_stage.wb_cheriot_store_q)) )) | lsu_resp_valid_i)
  - ibex_wb_stage ibex_wb_stage.sv:183 ((g_writeback_stage.wb_is_cheriot_q ? g_writeback_stage.cheriot_rf_we_q : g_writeback_stage.rf_we_wb_q) & g_writeback_stage.wb_valid_q)
  - ibex_wb_stage ibex_wb_stage.sv:190 (g_writeback_stage.wb_valid_q & (g_writeback_stage.rf_we_wb_q | (g_writeback_stage.wb_is_cheriot_q & g_writeback_stage.cheriot_rf_we_q) | (g_writeback_stage.wb_instr_type_q == WB_INSTR_LOAD) | g_writeback_stage.wb_cheriot_load_q))
  - ibex_wb_stage ibex_wb_stage.sv:193 (g_writeback_stage.wb_valid_q & ((g_writeback_stage.wb_instr_type_q == WB_INSTR_LOAD) | g_writeback_stage.wb_cheriot_load_q))
  - ibex_wb_stage ibex_wb_stage.sv:195 (g_writeback_stage.wb_valid_q & ((g_writeback_stage.wb_instr_type_q == WB_INSTR_STORE) | g_writeback_stage.wb_cheriot_store_q))
TOGGLE ibex_core: 47 ports (spec 12; missing: [])
TOGGLE ibex_if_stage: 25 ports (spec 4; missing: [])
TOGGLE ibex_id_stage: 52 ports (spec 27; missing: [])
TOGGLE ibex_decoder: 38 ports
TOGGLE ibex_controller: 14 ports
TOGGLE ibex_load_store_unit: 25 ports (spec 9; missing: [])
TOGGLE ibex_wb_stage: 37 ports (spec 9; missing: [])
TOGGLE ibex_cs_registers: 76 ports (spec 20; missing: [])
TOGGLE ibex_compressed_decoder: 1 ports (spec 1; missing: [])
TOGGLE ibex_register_file_ff: 4 ports (spec 4; missing: [])
TOGGLE ibex_cheriot_ex: 144 ports
FSM ibex_load_store_unit.ls_fsm_cs: 10 states+transitions
FSM ibex_load_store_unit.cap_rx_fsm_q: 7 states+transitions
ASSERT ibex_register_file_ff: 3 of 3 found: ['g_cheriot_rf.CheriotRaddrAMSBClear', 'g_cheriot_rf.CheriotRaddrBMSBClear', 'g_cheriot_rf.CheriotWaddrMSBClear']

Emitted 1421 entry lines in 41 (module, metric) scopes to dv/auto_dv/excl/gen_exclusions.el
A.8 carve-back filter removed 3 emitted lines:
  - ibex_register_file_ff: Condition 67 "2391767907" "(g_cheriot_rf.cheriot_enabled ? ((raddr_a_i[3:0] == '0) ? g_cheriot_rf.rcap_r0 : g_cheriot_rf.rf_shared[raddr_a_i[3:0]]) : CapWordZeroVal) 1 -1" (2 "1
  - ibex_register_file_ff: Condition 70 "2882321518" "(g_cheriot_rf.cheriot_enabled ? ((raddr_b_i[3:0] == '0) ? g_cheriot_rf.rcap_r0 : g_cheriot_rf.rf_shared[raddr_b_i[3:0]]) : CapWordZeroVal) 1 -1" (2 "1
  - ibex_register_file_ff: Condition 74 "2362779018" "(g_cheriot_rf.cheriot_enabled ? g_cheriot_rf.g_dummy_r0.we_data_r0 : (((!RV32E)) && g_cheriot_rf.we_a_dec[0] && waddr_a_i[4])) 1 -1" (2 "1")
