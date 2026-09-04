# Round 0 coverage tables: where the gaps are

Generated 2026-09-04T22:29:41Z by the Runtime Manager, read-only: no run, no re-merge, no file under
`dv/auto_dv/evidence/gen_round_0/` touched. Data tables only; the analysis is the DV Lead's
(`gen_round_0_coverage_analysis.md`).

The team calls this measurement **round 1**; the flow indexes it as **measured round 0**, evidence
directory `dv/auto_dv/evidence/gen_round_0`, regression tag `round_1`. Pinned commit
`4a0070285557a2a7dfb50cea9390597143b984b0`. URG report:
`/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov/report`.

**Gated scopes** (gen_tb_architecture.md Section 5): `gen_tb_top.u_dut.u_ibex_core` and
`gen_tb_top.u_dut.u_register_file`, combined per metric by summing covered and total objects.
Everything below is inside those two subtrees unless a row says otherwise.

**Self-check on the whole extraction.** The 102 gated instance rows of table (a) sum to
line 3654/4359, cond 6464/9624, toggle 16877/25044, fsm 38/86, branch 1831/2428, assert 166/179,
which is the round's gate row digit for digit. Any table below that disagrees with the record is
wrong, not the record.

## (a) Per-instance rows of the two gated trees, by missed objects

Parse: `modinfo.txt`, each `Module : <name>` block's `Module self-instances` table, rows whose
instance path is `gen_tb_top.u_dut.u_ibex_core` or `...u_register_file` or a descendant of either.
Each row is 14 whitespace tokens: score, then six metric pairs, then the full instance path.
`missed` sums line+cond+toggle+fsm+branch misses; `--` metrics contribute nothing. 102 rows.

| instance | module | missed | line | cond | toggle | fsm | branch |
|---|---|---|---|---|---|---|---|
| `u_ibex_core.g_cheriot_ex.u_ibex_cheriot_ex` | ibex_cheriot_ex | 2211 | 132/336 | 87/347 | 743/2404 | -- | 41/127 |
| `u_ibex_core.cs_registers_i` | ibex_cs_registers | 1833 | 364/441 | 421/695 | 792/2202 | -- | 218/290 |
| `u_ibex_core.g_pmp.pmp_i` | ibex_pmp | 1815 | 234/358 | 2533/3966 | 73/200 | -- | 148/279 |
| `u_ibex_core` | ibex_core | 1214 | 377/390 | 455/647 | 1919/2908 | -- | 87/107 |
| `u_ibex_core.id_stage_i.controller_i` | ibex_controller | 555 | 140/244 | 169/312 | 331/570 | 5/26 | 44/92 |
| `u_ibex_core.if_stage_i` | ibex_if_stage | 524 | 50/57 | 98/148 | 945/1400 | -- | 27/39 |
| `u_ibex_core.id_stage_i` | ibex_id_stage | 488 | 82/89 | 229/268 | 1377/1808 | -- | 76/87 |
| `u_ibex_core.wb_stage_i` | ibex_wb_stage | 414 | 35/35 | 70/91 | 407/796 | -- | 15/19 |
| `u_ibex_core.id_stage_i.decoder_i` | ibex_decoder | 392 | 426/471 | 115/157 | 585/794 | -- | 186/282 |
| `u_ibex_core.load_store_unit_i` | ibex_load_store_unit | 325 | 170/205 | 123/197 | 510/678 | 6/22 | 79/111 |
| `u_ibex_core.if_stage_i.gen_icache.icache_i` | ibex_icache | 224 | 325/331 | 908/1049 | 537/604 | 5/8 | 193/200 |
| `u_ibex_core.cs_registers_i.minstret_counter_i` | ibex_counter | 206 | 11/14 | 1/3 | 131/330 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.u_dcsr_csr` | ibex_csr | 133 | 3/4 | -- | 3/134 | -- | 2/3 |
| `u_ibex_core.cs_registers_i.u_dscratch0_csr` | ibex_csr | 133 | 3/4 | -- | 3/134 | -- | 2/3 |
| `u_ibex_core.cs_registers_i.u_dscratch1_csr` | ibex_csr | 133 | 3/4 | -- | 3/134 | -- | 2/3 |
| `u_ibex_core.cs_registers_i.u_depc_csr` | ibex_csr | 129 | 3/4 | -- | 3/130 | -- | 2/3 |
| `u_ibex_core.if_stage_i.g_mem_ecc.u_instr_intg_dec` | prim_secded_inv_39_32_dec | 112 | 41/41 | 97/195 | 146/160 | -- | -- |
| `u_ibex_core.load_store_unit_i.g_mem_rdata_ecc.u_data_intg_dec` | prim_secded_inv_39_32_dec | 112 | 41/41 | 97/195 | 146/160 | -- | -- |
| `u_ibex_core.if_stage_i.gen_icache.icache_i.gen_data_ecc_checking.gen_ecc_banks[0].data_ecc_dec` | prim_secded_inv_39_32_dec | 105 | 41/41 | 100/195 | 150/160 | -- | -- |
| `u_ibex_core.if_stage_i.gen_icache.icache_i.gen_data_ecc_checking.gen_ecc_banks[1].data_ecc_dec` | prim_secded_inv_39_32_dec | 105 | 41/41 | 100/195 | 150/160 | -- | -- |
| `u_ibex_core.cs_registers_i.gen_cntrs[7].gen_imp.mcounters_variable_i` | ibex_counter | 86 | 11/14 | 1/3 | 123/202 | -- | 5/7 |
| `u_register_file` | ibex_register_file_ff | 84 | 129/130 | 154/159 | 227/302 | -- | 105/108 |
| `u_ibex_core.cs_registers_i.gen_trigger_regs.g_dbg_tmatch_reg[0].u_tmatch_value_csr` | ibex_csr | 69 | 3/4 | -- | 67/134 | -- | 2/3 |
| `u_ibex_core.if_stage_i.gen_icache.icache_i.gen_ecc_wdata.tag_ecc_enc` | prim_secded_inv_28_22_enc | 68 | 8/8 | -- | 32/100 | -- | -- |
| `u_ibex_core.cs_registers_i.mcycle_counter_i` | ibex_counter | 66 | 14/14 | 3/3 | 136/202 | -- | 7/7 |
| `u_ibex_core.cs_registers_i.g_mshwm.u_mshwm_csr` | ibex_csr | 61 | 3/4 | -- | 59/118 | -- | 2/3 |
| `u_ibex_core.cs_registers_i.gen_cntrs[8].gen_imp.mcounters_variable_i` | ibex_counter | 59 | 11/14 | 1/3 | 86/138 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.g_mshwm.u_mshwmb_csr` | ibex_csr | 57 | 3/3 | -- | 59/116 | -- | 2/2 |
| `u_ibex_core.cs_registers_i.gen_cntrs[2].gen_imp.mcounters_variable_i` | ibex_counter | 51 | 11/14 | 1/3 | 94/138 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.gen_cntrs[4].gen_imp.mcounters_variable_i` | ibex_counter | 51 | 11/14 | 1/3 | 94/138 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.gen_cntrs[5].gen_imp.mcounters_variable_i` | ibex_counter | 51 | 11/14 | 1/3 | 94/138 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.gen_cntrs[6].gen_imp.mcounters_variable_i` | ibex_counter | 51 | 11/14 | 1/3 | 94/138 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.gen_cntrs[9].gen_imp.mcounters_variable_i` | ibex_counter | 51 | 11/14 | 1/3 | 94/138 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.gen_cntrs[3].gen_imp.mcounters_variable_i` | ibex_counter | 49 | 11/14 | 1/3 | 96/138 | -- | 5/7 |
| `u_ibex_core.if_stage_i.compressed_decoder_i` | ibex_compressed_decoder | 49 | 244/262 | 87/94 | 145/146 | 14/17 | 105/125 |
| `u_ibex_core.cs_registers_i.gen_cntrs[0].gen_imp.mcounters_variable_i` | ibex_counter | 39 | 11/14 | 1/3 | 106/138 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.gen_cntrs[1].gen_imp.mcounters_variable_i` | ibex_counter | 39 | 11/14 | 1/3 | 106/138 | -- | 5/7 |
| `u_ibex_core.cs_registers_i.u_mstack_epc_csr` | ibex_csr | 39 | 4/4 | -- | 95/134 | -- | 3/3 |
| `u_ibex_core.if_stage_i.gen_dummy_instr.dummy_instr_i.lfsr_i` | prim_lfsr | 38 | 8/18 | 11/28 | 103/106 | -- | 7/15 |
| `u_ibex_core.if_stage_i.g_secure_pc.u_prev_instr_addr_incr_buf` | prim_buf | 36 | -- | -- | 92/128 | -- | -- |

Top 40 of 102 rows shown, ordered by missed objects; the tail contributes
420 of the 12677 total misses.

## (b) FSM detail in the gated trees (38/86 transitions)

Parse: `modinfo.txt`, each `FSM Coverage for Module : <m>` block for a module with an instance in
the gated trees, then each `Summary for FSM :: <f>` sub-block: the `States` and `Transitions` rows
give covered/total, and the detail tables give the names marked `Not Covered`. URG excludes states
from the score ("Not included in score"), so the round's 38/86 is transitions only.

| module | FSM | states cov/tot | transitions cov/tot |
|---|---|---|---|
| ibex_controller | `ctrl_fsm_cs` | 5/10 | 5/26 |
| ibex_load_store_unit | `ls_fsm_cs` | 4/8 | 6/17 |
| ibex_load_store_unit | `cap_rx_fsm_q` | 1/3 | 0/5 |
| ibex_icache | `inval_state_q` | 4/4 | 5/8 |
| ibex_multdiv_fast | `md_state_q` | 7/7 | 8/13 |
| ibex_compressed_decoder | `cm_state_q` | 8/8 | 14/17 |
| **total** | 6 FSMs | **29/40** | **38/86** |

The transition total 38/86 equals the round's fsm gate cell.

**ibex_controller :: ctrl_fsm_cs** unhit states (5): `DBG_TAKEN_ID`, `DBG_TAKEN_IF`, `IRQ_TAKEN`, `SLEEP`, `WAIT_SLEEP`

**ibex_controller :: ctrl_fsm_cs** unhit transitions (21): `BOOT_SET->RESET`, `DBG_TAKEN_ID->DECODE`, `DBG_TAKEN_ID->RESET`, `DBG_TAKEN_IF->DECODE`, `DBG_TAKEN_IF->RESET`, `DECODE->DBG_TAKEN_IF`, `DECODE->IRQ_TAKEN`, `DECODE->RESET`, `FIRST_FETCH->DBG_TAKEN_IF`, `FIRST_FETCH->IRQ_TAKEN`, `FIRST_FETCH->RESET`, `FLUSH->DBG_TAKEN_ID`, `FLUSH->DBG_TAKEN_IF`, `FLUSH->RESET`, `FLUSH->WAIT_SLEEP`, `IRQ_TAKEN->DECODE`, `IRQ_TAKEN->RESET`, `SLEEP->FIRST_FETCH`, `SLEEP->RESET`, `WAIT_SLEEP->RESET`, `WAIT_SLEEP->SLEEP`

**ibex_load_store_unit :: ls_fsm_cs** unhit states (4): `CTX_WAIT_GNT1`, `CTX_WAIT_GNT2`, `CTX_WAIT_RESP`, `WAIT_GNT_MIS`

**ibex_load_store_unit :: ls_fsm_cs** unhit transitions (11): `CTX_WAIT_GNT1->CTX_WAIT_GNT2`, `CTX_WAIT_GNT1->IDLE`, `CTX_WAIT_GNT2->CTX_WAIT_RESP`, `CTX_WAIT_GNT2->IDLE`, `CTX_WAIT_RESP->IDLE`, `IDLE->CTX_WAIT_GNT1`, `IDLE->CTX_WAIT_GNT2`, `IDLE->WAIT_GNT_MIS`, `WAIT_GNT_MIS->IDLE`, `WAIT_GNT_MIS->WAIT_RVALID_MIS`, `WAIT_RVALID_MIS->WAIT_GNT`

**ibex_load_store_unit :: cap_rx_fsm_q** unhit states (2): `CRX_WAIT_RESP1`, `CRX_WAIT_RESP2`

**ibex_load_store_unit :: cap_rx_fsm_q** unhit transitions (5): `CRX_IDLE->CRX_WAIT_RESP1`, `CRX_WAIT_RESP1->CRX_IDLE`, `CRX_WAIT_RESP1->CRX_WAIT_RESP2`, `CRX_WAIT_RESP2->CRX_IDLE`, `CRX_WAIT_RESP2->CRX_WAIT_RESP1`

**ibex_icache :: inval_state_q** unhit states (0): none

**ibex_icache :: inval_state_q** unhit transitions (3): `AWAIT_SCRAMBLE_KEY->OUT_OF_RESET`, `INVAL_CACHE->OUT_OF_RESET`, `INVAL_IDLE->OUT_OF_RESET`

**ibex_multdiv_fast :: md_state_q** unhit states (0): none

**ibex_multdiv_fast :: md_state_q** unhit transitions (5): `MD_ABS_A->MD_IDLE`, `MD_ABS_B->MD_IDLE`, `MD_CHANGE_SIGN->MD_IDLE`, `MD_COMP->MD_IDLE`, `MD_LAST->MD_IDLE`

**ibex_compressed_decoder :: cm_state_q** unhit states (0): none

**ibex_compressed_decoder :: cm_state_q** unhit transitions (3): `CmPopLoadReg->CmIdle`, `CmPopZeroA0->CmIdle`, `CmPushStoreReg->CmIdle`

## (c) Unhit assertions in the gated trees (13 of 179; report-wide 229/257)

Parse: `gen_asserts.txt`, the `Assertions Uncovered:` table, first column, filtered to the two
gated subtrees. 18 assertions are uncovered report-wide; 13 are in the gated trees,
which is 179 minus 166.

- `gen_tb_top.u_dut.u_ibex_core.id_stage_i.controller_i.AlwaysInstrClearOnMispredict`
- `gen_tb_top.u_dut.u_ibex_core.id_stage_i.controller_i.IbexPipelineFlushOnChangingDebugMode`
- `gen_tb_top.u_dut.u_ibex_core.id_stage_i.controller_i.PipeEmptyOnIrq`
- `gen_tb_top.u_dut.u_ibex_core.if_stage_i.NoMispredBranch`
- `gen_tb_top.u_dut.u_ibex_core.if_stage_i.gen_b8_probe_i.sva_b8_dummy_in_expansion`
- `gen_tb_top.u_dut.u_ibex_core.if_stage_i.gen_dummy_instr.dummy_instr_i.lfsr_i.NextStateCheck_A`
- `gen_tb_top.u_dut.u_ibex_core.if_stage_i.gen_dummy_instr.dummy_instr_i.lfsr_i.NoLockups_A`
- `gen_tb_top.u_dut.u_ibex_core.if_stage_i.gen_dummy_instr.dummy_instr_i.lfsr_i.gen_lockup_mechanism_sva.LfsrLockupCheck_A`
- `gen_tb_top.u_dut.u_ibex_core.if_stage_i.gen_dummy_instr.dummy_instr_i.lfsr_i.gen_max_len_sva.MaximalLengthCheck1_A`
- `gen_tb_top.u_dut.u_register_file.g_cheriot_rf.CheriotRaddrAMSBClear`
- `gen_tb_top.u_dut.u_register_file.g_cheriot_rf.CheriotRaddrBMSBClear`
- `gen_tb_top.u_dut.u_register_file.g_cheriot_rf.CheriotWaddrMSBClear`
- `gen_tb_top.u_dut.u_register_file.g_cheriot_rf.g_dummy_r0.DummyWriteTargetsX0`

## (d) Toggle misses

Parse: `modinfo.txt`, each `Toggle Coverage for Module` block for a module instantiated in the
gated trees. Per module the `Total Bits` row gives total and covered; missed is the difference.
Per signal the `Port Details` / `Signal Details` rows give the two directions; a bit counts as
missed once per direction marked `No`, and the width comes from the `[msb:lsb]` suffix (1 if none).
`Unreachable` is counted separately and is NOT included in the missed column, because URG has
already judged those bits unreachable rather than unexercised.

| module | missed toggle bits |
|---|---|
| ibex_cheriot_ex | 1661 |
| ibex_cs_registers | 1410 |
| ibex_core | 989 |
| ibex_if_stage | 455 |
| ibex_id_stage | 431 |
| ibex_wb_stage | 389 |
| ibex_controller | 239 |
| ibex_decoder | 209 |
| ibex_load_store_unit | 168 |
| ibex_counter | 163 |
| ibex_pmp | 127 |
| ibex_register_file_ff | 75 |
| prim_secded_inv_28_22_enc | 68 |
| ibex_icache | 67 |
| gen_ic_lookup_probe | 17 |
| prim_secded_inv_28_22_dec | 14 |
| prim_secded_inv_39_32_dec | 10 |
| ibex_dummy_instr | 5 |
| gen_b8_probe | 3 |
| prim_lfsr | 3 |
| **all 25 gated modules** | **6508** |

Signal-name families, top 20 by missed bits. A family is the port or signal name with any bit
range and any struct field suffix removed, so `fwd_wcap_i.base[8:0]` and `fwd_wcap_i.top[8:0]`
both fall under `fwd_wcap_i`.

| family | missed bits | unreachable bits |
|---|---|---|
| `pcc_cap_i` | 672 | 0 |
| `counter_val_o` | 597 | 640 |
| `pcc_cap_o` | 448 | 0 |
| `counter_val_upd_o` | 231 | 1344 |
| `boot_addr_i` | 192 | 0 |
| `cheriot_branch_target_i` | 186 | 6 |
| `hart_id_i` | 128 | 0 |
| `csr_pmp_cfg_i` | 119 | 0 |
| `csr_pmp_cfg_o` | 119 | 0 |
| `cheriot_operator_o` | 104 | 0 |
| `rvfi_order` | 97 | 0 |
| `pc_id_i` | 80 | 10 |
| `cheriot_imm20_o` | 80 | 0 |
| `cheriot_imm21_o` | 80 | 4 |
| `data_i` | 73 | 0 |
| `irqs_i` | 72 | 0 |
| `fwd_wcap_i` | 70 | 0 |
| `rf_rcap_a_i` | 70 | 0 |
| `rf_rcap_b_i` | 70 | 0 |
| `result_cap_o` | 70 | 0 |

## (e) Covergroups (26 in the report) and zero-hit coverpoints

Parse: `gen_groups.txt` summary table, columns COVERED EXPECTED SCORE then the group name.
The witness ledger `gen_wit_cycle_clause_cg` is marked: it is a traceability ledger, not coverage,
and gen_cov_report excludes it from the weight-averaged score while URG's report-wide bin total
includes it. That is the origin of the three group figures in the round record (81.47 with the
ledger, 78.29 weight-averaged without it, 85.89 bins without it).

| covergroup | covered | expected | score | |
|---|---|---|---|---|
| `gen_wit_cycle_clause_cg` | 0 | 220 | 0.00 | **LEDGER, not coverage** |
| `gen_ic_ecc_cg` | 1 | 40 | 2.50 | below 80 |
| `gen_rst_boot_cg` | 11 | 44 | 25.00 | below 80 |
| `gen_sec_ctrl_inputs_cg` | 17 | 51 | 33.33 | below 80 |
| `gen_div_timing_cg` | 44 | 122 | 36.07 | below 80 |
| `gen_mul_timing_cg` | 33 | 80 | 41.25 | below 80 |
| `gen_cmp_zcmp_pushpop_cg` | 204 | 291 | 70.10 | below 80 |
| `gen_isa_jump_cg` | 75 | 103 | 72.82 | below 80 |
| `gen_isa_branch_cg` | 153 | 208 | 73.56 | below 80 |
| `gen_cmp_zcmp_hazard_cg` | 79 | 102 | 77.45 | below 80 |
| `gen_bit_zba_zbb_ops_cg` | 357 | 424 | 84.20 |  |
| `gen_rvfi_record_cg` | 60 | 70 | 85.71 |  |
| `gen_csr_trap_setup_warl_cg` | 184 | 208 | 88.46 |  |
| `gen_cmp_zcb_cg` | 88 | 95 | 92.63 |  |
| `gen_isa_lui_auipc_cg` | 32 | 34 | 94.12 |  |
| `gen_cmp_zca_cg` | 279 | 296 | 94.26 |  |
| `gen_bit_sbit_cg` | 115 | 122 | 94.26 |  |
| `gen_div_ops_cg` | 168 | 176 | 95.45 |  |
| `gen_isa_hint_x0_cg` | 82 | 84 | 97.62 |  |
| `gen_cmp_zcmp_mv_cg` | 161 | 163 | 98.77 |  |
| `gen_mul_ops_cg` | 435 | 436 | 99.77 |  |
| `gen_isa_alu_reg_cg` | 340 | 340 | 100.00 |  |
| `gen_cmp_imm_edges_cg` | 83 | 83 | 100.00 |  |
| `gen_isa_alu_imm_cg` | 145 | 145 | 100.00 |  |
| `gen_isa_shift_cg` | 132 | 132 | 100.00 |  |
| `gen_bit_count_cg` | 199 | 199 | 100.00 |  |

Zero-hit coverpoints, for every covergroup below 80. Parse: `gen_grpinfo.txt`, each
`Variables for Group <g>` table, rows whose COVERED column is 0.

- **gen_wit_cycle_clause_cg** (2 of 3 coverpoints at zero): `cp_clause`, `Crosses`
- **gen_ic_ecc_cg** (15 of 18 coverpoints at zero): `cp_ram`, `cp_bits`, `cp_way`, `cp_beat`, `cp_alert_pulses`, `cp_inval_ways`, `cp_refetch`, `cp_major_nmi_quiet`, `cp_lookups_blocked_next`, `cp_multiway_mismatch`, `cp_knob`, `cr_ram_x_bits_x_way`, `cr_ram_x_inval`, `cr_data_x_beat`, `cr_bits_x_rate`
- **gen_sec_ctrl_inputs_cg** (2 of 16 coverpoints at zero): `cp_boot_addr_change_ctx`, `cp_icache_en_readback_in_debug`
- **gen_div_timing_cg** (2 of 19 coverpoints at zero): `cp_irq_latency`, `cr_event_div0_dit`
- **gen_mul_timing_cg** (2 of 13 coverpoints at zero): `cp_dmem_delay`, `cr_wb_defer`
- **gen_cmp_zcmp_pushpop_cg** (1 of 22 coverpoints at zero): `cr_insn_wrap`
- **gen_isa_jump_cg** (1 of 19 coverpoints at zero): `cr_zero_page_bwd`

