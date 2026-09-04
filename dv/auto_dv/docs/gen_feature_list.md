# DV feature list - Ibex core, opentitan configuration

Deliverable 1 (DV_prompt.txt Section 11). Version 2 (promoted from the T-002 draft after the Critic's
verdict v1, dv/auto_dv/docs/gen_critic_feature_list_v1.md, findings C-02..C-26 addressed).
Owner: dv-lead. Generated 2026-09-04 13:14 UTC from the area parts under dv/auto_dv/work/dv-lead/parts/. Part-file names in this document (tp_<area>.md, fcov_<area>.md, gen_part_<area>.md, trace_*_<area>.csv and the README_*_BRIEF.md briefs) are this plan set's own gitignored sources, named as provenance: the content they hold is in the corresponding area of gen_test_plan.md, gen_fcov_plan.md or gen_feature_list.md, and the bug and doc-defect number series they define are in gen_bug_log.md. No claim in this document rests on opening one. Three rtl-arch notes this plan set cites are committed references, not work files: dv/auto_dv/evidence/gen_multdiv_bound_props.md (the MD-n bound properties and covers), dv/auto_dv/evidence/gen_bug_reproducer_specs.md (the reproducer recipes behind the bug log) and dv/auto_dv/evidence/gen_interface_inventory.md (the numbered driver and protocol rules); citations name them by basename and resolve there.

Build configuration: `opentitan` (ibex_configs.yaml): BaseIsa=RV32IorCHERIoT (CHERIoT mode excluded
by owner ruling), RV32E=0, RV32M=RV32MSingleCycle, RV32B=RV32BOTEarlGrey, RV32ZC=RV32ZcaZcbZcmp,
RegFile=RegFileFF, BranchTargetALU=1, WritebackStage=1, ICache=1, ICacheECC=1, ICacheScramble=1,
BranchPredictor=0, DbgTriggerEn=1, SecureIbex=1, PMPEnable=1, PMPGranularity=0, PMPNumRegions=16,
MHPMCounterNum=10, MHPMCounterWidth=32.

DUT: `gen_dut_top` = `ibex_core` + `ibex_register_file_ff` (DV_prompt.txt Section 2 rulings); `ibex_top`
is not the DUT. Wrapper parameters (owner question Q-002 defaults, pending confirmation): MemECC=1
(39-bit bus data), DummyInstructions=1, ICacheTweakInfection=1, ResetAll=1, RegFileECC=0
(RegFileDataWidth=32), DbgHwBreakNum=1, DmBaseAddr=0x1A110000, DmAddrMask=0xFFF,
DmHaltAddr=0x1A110800, DmExceptionAddr=0x1A110808, CsrMvendorId=CsrMimpId=0, PMP reset values from
ibex_pkg; compiled with +define+RVFI; cheriot_enable_i tied IbexMuBiOff inside the wrapper.

# 0. How to read this list

- One entry per feature, ID `F-<AREA>-<nnn>`, stable once assigned: never renumbered, never deleted.
  Fields: What / Observable at (a DUT port or RVFI field; CSR state is observed as "csrr read-back on
  rvfi_rd_wdata"; trap targets as "instr_addr_o = <vector>") / Config (programmable state only: CSR
  fields, PMP, counters, triggers, privilege; never a build parameter) / Source (spec section, doc
  file:section, or `RTL-defined rtl/<file>.sv:<lines>`) / Edge / Status / Notes.
- Status: `ACTIVE` entries are the features; they alone count in the completeness measure.
  `ALIAS of F-x` marks a duplicate stated from another area's perspective; `FOLDED into F-x (bin b)`
  marks a former edge entry that restated its parent and now lives on as the named bin of the parent's
  covergroup. Test-plan items may cite ALIAS/FOLDED IDs; traceability resolves them to the canonical
  ACTIVE entry. Section 3 lists every alias cluster and every fold.
- Edge rule (Critic C-12): an entry is an edge (`Edge: yes, of F-x`) only if its What names a stimulus
  condition or timing coincidence the parent does not AND its observable or expected outcome differs;
  otherwise it is folded. Edges point at base features only (no depth-2 chains).
- "Source: RTL-defined" marks behaviour no specification or Ibex document describes; every such item
  is listed for the RTL/Arch Engineer in the reading report and needs a behaviour summary.
- Doc defects are cited as D1..D21 and bug candidates as B1..B20; both are defined in
  dv/auto_dv/docs/gen_bug_log.md (the single list; Section 1b holds the retained IDs B6, B9 and B12 that are
  not bug candidates).
- Observability caveat: `ibex_core` exposes no `rvfi_csr_*` ports (verified by grep). Internal nets
  are never observables; where a bin needs one, the entry says "probe candidate P<n> (probe register
  entry needed)" and names the boundary alternative first.
- Verification status of citations: the area authors re-dumped every RTL citation with sed/grep after
  the Critic's sample found 2 misses and 13 partials in 86 (v1); the Critic re-reviews v2.

# 1. Summary by area

| Prefix | ACTIVE | ALIAS | FOLDED | Total IDs | ACTIVE edges | New in v2 |
|---|---|---|---|---|---|---|
| F-ISA | 38 | 12 | 2 | 52 | 19 | 0 |
| F-MUL | 25 | 1 | 2 | 28 | 17 | 1 |
| F-CMP | 62 | 1 | 7 | 70 | 34 | 2 |
| F-BIT | 37 | 2 | 2 | 41 | 15 | 1 |
| F-BTALU | 8 | 3 | 5 | 16 | 5 | 0 |
| F-CSR | 52 | 21 | 30 | 103 | 21 | 0 |
| F-PRV | 14 | 11 | 11 | 36 | 5 | 0 |
| F-EXC | 40 | 17 | 12 | 69 | 18 | 0 |
| F-IRQ | 36 | 10 | 20 | 66 | 23 | 1 |
| F-PMP | 67 | 8 | 25 | 100 | 30 | 0 |
| F-DBG | 42 | 11 | 15 | 68 | 26 | 1 |
| F-TRG | 19 | 0 | 11 | 30 | 9 | 0 |
| F-PMC | 40 | 2 | 11 | 53 | 16 | 0 |
| F-IMEM | 23 | 6 | 3 | 32 | 7 | 2 |
| F-DMEM | 42 | 5 | 4 | 51 | 10 | 4 |
| F-FE | 19 | 4 | 2 | 25 | 6 | 0 |
| F-IC | 40 | 0 | 8 | 48 | 15 | 1 |
| F-DIT | 23 | 1 | 6 | 30 | 14 | 1 |
| F-SEC | 24 | 5 | 8 | 37 | 9 | 0 |
| F-RST | 22 | 1 | 4 | 27 | 9 | 0 |
| F-RVFI | 31 | 1 | 2 | 34 | 9 | 1 |
| F-CHERI | 1 | 0 | 0 | 1 | 0 | 0 |
| ALL (22 prefixes) | 705 | 122 | 190 | 1017 | 317 | 15 |

Area code key: ISA base RV32I incl. SYSTEM/MISC-MEM decode; MUL M extension; CMP compressed
(Zca/Zcb/Zcmp); BIT bitmanip RV32BOTEarlGrey; BTALU branch target ALU; CSR control/status registers;
PRV privilege modes and mstatus; EXC synchronous exceptions; IRQ interrupts/NMI/WFI; PMP physical
memory protection + Smepmp; DBG external debug; TRG triggers; PMC performance counters; IMEM
instruction bus protocol; DMEM data bus protocol + LSU; FE fetch stage; IC instruction cache; DIT
dummy instructions + data-independent timing; SEC alerts and countermeasures; RST reset and boot;
RVFI trace interface; CHERI CHERIoT carve-out (F-CHERI-001, exclusion name "cheriot-out-of-scope";
its table mirrors dv/auto_dv/excl/gen_exclusions.el at 9ebf2d9 row for row, the file urg loads; the
rtl-arch draft is the file's source, never the authority).

# 2. Wrapper-parameter assumptions

Features that exist only under the Q-002 default parameters: MemECC=1: bus-integrity alert and
internal NMI entries (F-IRQ-040..043, F-IMEM-027, F-DMEM-041, F-DMEM-050, F-IC-007, F-SEC integrity
entries) and 39-bit bus data widths. DummyInstructions=1: all F-DIT entries, cpuctrlsts[5:2]
writability (F-CSR-085/087/092), secureseed, F-CMP-064, F-PMC-011. RegFileECC=0: in-core RF ECC
alert is unreachable; F-SEC-004..006 are negative checks (alert_major_internal_o must not fire) and
the only live internal-major source is the PC increment check (ShadowCSR is a hardwired 0,
rtl/ibex_core.sv:197). ResetAll=1: X-free outputs at time 0 (F-RST entries).

# 3. Alias clusters and folds (generated from the Status fields)

## 3.1 Alias clusters (canonical <- aliases)

| Canonical (ACTIVE) | Aliases |
|---|---|
| F-BTALU-001 | F-ISA-024 |
| F-CMP-038 | F-MUL-027 |
| F-CMP-044 | F-EXC-015 |
| F-CMP-060 | F-DMEM-047 |
| F-CSR-002 | F-CSR-012, F-ISA-044 |
| F-CSR-003 | F-CSR-013, F-ISA-045 |
| F-CSR-005 | F-ISA-046 |
| F-CSR-011 | F-PMC-029 |
| F-CSR-019 | F-SEC-037 |
| F-CSR-020 | F-RST-005 |
| F-CSR-021 | F-BIT-040 |
| F-CSR-024 | F-EXC-053, F-PMP-077 |
| F-CSR-026 | F-IRQ-059 |
| F-CSR-032 | F-IRQ-004 |
| F-CSR-033 | F-IRQ-005 |
| F-CSR-035 | F-IRQ-013, F-IRQ-014 |
| F-CSR-060 | F-PMC-022 |
| F-CSR-085 | F-SEC-031 |
| F-DBG-004 | F-EXC-048 |
| F-DBG-012 | F-CSR-074 |
| F-DBG-013 | F-CSR-077 |
| F-DBG-016 | F-CSR-076 |
| F-DBG-017 | F-EXC-019, F-ISA-035 |
| F-DBG-023 | F-EXC-020 |
| F-DBG-032 | F-EXC-012, F-ISA-039, F-PRV-025 |
| F-DBG-050 | F-CSR-017 |
| F-DBG-055 | F-PMP-076 |
| F-DBG-056 | F-IRQ-039 |
| F-DIT-002 | F-BTALU-006 |
| F-EXC-005 | F-IMEM-013, F-PMP-068 |
| F-EXC-006 | F-IMEM-012, F-PMP-079 |
| F-EXC-008 | F-ISA-047 |
| F-EXC-013 | F-ISA-042 |
| F-EXC-016 | F-ISA-050 |
| F-EXC-017 | F-DBG-020 |
| F-EXC-023 | F-PRV-021 |
| F-EXC-025 | F-DMEM-036 |
| F-EXC-027 | F-DMEM-037 |
| F-EXC-035 | F-DMEM-038, F-PMP-085 |
| F-EXC-055 | F-SEC-024 |
| F-EXC-067 | F-FE-011, F-ISA-052 |
| F-IC-011 | F-SEC-021 |
| F-IC-037 | F-IMEM-018 |
| F-IC-040 | F-CSR-086, F-DBG-062, F-FE-022, F-SEC-033 |
| F-IRQ-007 | F-PRV-023 |
| F-IRQ-008 | F-PRV-024 |
| F-IRQ-009 | F-PRV-029 |
| F-IRQ-016 | F-RVFI-029 |
| F-IRQ-023 | F-PRV-012 |
| F-IRQ-030 | F-IRQ-033, F-PRV-031 |
| F-IRQ-032 | F-PRV-011 |
| F-IRQ-037 | F-DBG-057 |
| F-IRQ-045 | F-PRV-018, F-PRV-019, F-PRV-020 |
| F-ISA-034 | F-CMP-033, F-DBG-022, F-EXC-018 |
| F-MUL-023 | F-BIT-036, F-IRQ-019 |
| F-PMC-001 | F-CSR-062 |
| F-PMC-004 | F-CSR-063 |
| F-PMC-005 | F-CSR-064 |
| F-PMC-007 | F-CSR-066 |
| F-PMC-009 | F-CSR-068 |
| F-PMC-011 | F-DIT-018 |
| F-PMC-015 | F-CSR-069 |
| F-PMC-016 | F-CSR-070 |
| F-PMC-018 | F-CSR-061 |
| F-PMC-020 | F-CSR-058 |
| F-PMC-025 | F-CSR-050 |
| F-PMC-039 | F-BTALU-016 |
| F-PMC-040 | F-BTALU-015 |
| F-PMP-067 | F-FE-016 |
| F-PMP-082 | F-DMEM-033 |
| F-PMP-087 | F-EXC-033 |
| F-PMP-088 | F-EXC-032 |
| F-PMP-095 | F-DBG-052 |
| F-PMP-097 | F-DBG-054 |
| F-PRV-005 | F-DBG-026, F-PMP-099 |
| F-PRV-007 | F-EXC-052, F-PMP-074 |
| F-PRV-010 | F-EXC-010, F-ISA-037 |
| F-PRV-015 | F-DBG-033, F-PMP-075 |
| F-PRV-016 | F-EXC-011, F-ISA-041 |
| F-RST-002 | F-IMEM-026 |
| F-RST-006 | F-IRQ-065 |
| F-RST-010 | F-IMEM-022 |
| F-RST-012 | F-IMEM-025 |
| F-RST-015 | F-IRQ-056 |
| F-RST-024 | F-DBG-008 |
| F-RVFI-018 | F-DBG-065 |
| F-SEC-007 | F-FE-020 |
| F-SEC-022 | F-CSR-089, F-DBG-067, F-EXC-047, F-EXC-054 |
| F-SEC-025 | F-CSR-091, F-EXC-057 |
| F-TRG-007 | F-CSR-082 |
| F-TRG-008 | F-CSR-083 |
| F-TRG-010 | F-EXC-021 |
| F-TRG-021 | F-EXC-022 |

93 clusters, 122 aliases.

## 3.2 Folded edge entries (former edge -> parent bin)

| Folded ID | Parent | Bin |
|---|---|---|
| F-ISA-017 | F-ISA-015 | CG-ISA-006.cr_link.c_jal_pc2 |
| F-ISA-033 | F-ISA-032 | CG-ISA-009.cr_op_priv_outcome.ecall_m_exc |
| F-MUL-010 | F-MUL-003 | CG-MUL-002.cr_seq.auto |
| F-MUL-019 | F-MUL-012 | CG-MUL-003.cr_op_sign.auto |
| F-CMP-042 | F-CMP-039 | CG-CMP-006.cr_insn_rlist_spimm.auto |
| F-CMP-043 | F-CMP-039 | CG-CMP-006.cr_insn_rlist_spimm.auto |
| F-CMP-046 | F-CMP-045 | CG-CMP-006.cp_order_ok.yes |
| F-CMP-053 | F-CMP-052 | CG-CMP-007.cr_insn_equal.auto |
| F-CMP-063 | F-CMP-039 | CG-CMP-008.cp_reexec.yes |
| F-CMP-065 | F-CMP-039 | CG-CMP-006.cr_insn_delay.auto |
| F-CMP-066 | F-EXC-008 | CG-CMP-004.cp_mtval_ok.yes |
| F-BIT-034 | F-BIT-001 | CG-BIT-011.cp_illegal_class.bcompress |
| F-BIT-035 | F-BIT-001 | CG-BIT-011.cp_illegal_class.op32_any |
| F-BTALU-004 | F-BTALU-002 | CG-ISA-006.cr_link.jal_pc4 |
| F-BTALU-005 | F-BTALU-001 | CG-BTALU-001.cr_taken_dit_redirect.nt_dit0_noredir |
| F-BTALU-007 | F-BTALU-003 | CG-ISA-006.cp_target_align.half |
| F-BTALU-009 | F-BTALU-001 | CG-ISA-007.cp_wrap.yes |
| F-BTALU-012 | F-ISA-030 | CG-ISA-008.cp_refetch.yes |
| F-CSR-004 | F-CSR-001 | CG-CSR-001.cr_rd_x0_write.csrrw_rdx0_rw_m, csrrwi_rdx0_rw_m, csrrs_rdx0_rw_m, csrrc_rdx0_rw_m |
| F-CSR-007 | F-CSR-006 | CG-CSR-012.cr_fam_gap.mscratch_g1, mepc_g1; CG-CSR-012.cr_fam_next.mscratch_csr_rd_same, mepc_csr_rd_same |
| F-CSR-010 | F-CSR-009 | CG-CSR-014.cp_range.r302_303 |
| F-CSR-015 | F-CSR-014 | CG-CSR-001.cr_priv_aclass_trap.u_info_ro_trap |
| F-CSR-022 | F-CSR-021 | CG-CSR-002.cr_csr_wpat.misa_all1 |
| F-CSR-025 | F-CSR-023 | CG-CSR-002.cr_csr_wpat.mstatus_all1 |
| F-CSR-030 | F-CSR-029 | CG-CSR-002.cr_csr_wpat.mie_all1 |
| F-CSR-036 | F-CSR-035 | CG-CSR-002.cr_mtvec_mode_lo.d00_nz |
| F-CSR-037 | F-CSR-035 | CG-CSR-016.cr_mtvec_first.mtvec_first_nonzero |
| F-CSR-040 | F-CSR-039 | CG-CSR-003.cr_mepc_lo_op.b01_csrrw |
| F-CSR-043 | F-CSR-042 | CG-CSR-003.cr_mcause_hi_mid.h00_nz |
| F-CSR-044 | F-CSR-042 | CG-CSR-003.cr_mcause_hi_mid.h11_zero |
| F-CSR-045 | F-CSR-042 | CG-CSR-003.cr_mcause_hi_mid.h01_zero |
| F-CSR-046 | F-CSR-042 | CG-CSR-003.cr_csr_op.mcause_csrrw |
| F-CSR-048 | F-CSR-047 | CG-PRV-008.cr_exc_mtval.exc_insn16 |
| F-CSR-049 | F-CSR-047 | CG-PRV-008.cr_exc_mtval.exc_insn32 |
| F-CSR-051 | F-PMC-025 | CG-CSR-002.cr_mcen_gate_w.off_all1 |
| F-CSR-052 | F-PMC-025 | CG-CSR-002.cr_mcen_gate_w.on_all1 |
| F-CSR-054 | F-CSR-053 | CG-CSR-005.cr_diag_u.offdiag_trap |
| F-CSR-057 | F-CSR-011 | CG-CSR-005.cr_wr_alias.wr_m_trap |
| F-CSR-059 | F-PMC-020 | CG-CSR-004.cr_csr_inhibit.mcycle_on |
| F-CSR-067 | F-PMC-007 | CG-CSR-013.cr_minstret_wr.minstret_wr_none |
| F-CSR-072 | F-PMC-007 | CG-CSR-013.cr_minstret_rd_wb.hpm10_retiring |
| F-CSR-075 | F-DBG-012 | CG-CSR-007.cr_csr_wpat_dbg.dcsr_all1 |
| F-CSR-084 | F-TRG-007 | CG-CSR-008.cr_csr_dbg_form.tdata2_nondbg_wr |
| F-CSR-087 | F-CSR-085 | CG-CSR-009.cr_mask_en.m0_en |
| F-CSR-088 | F-CSR-085 | CG-CSR-009.cr_wpat_op.all1_csrrw |
| F-CSR-090 | F-SEC-022 | CG-CSR-009.cr_dbl_detect.sync_s1_pulse |
| F-CSR-093 | F-CSR-092 | CG-CSR-010.cr_op_form_gap.csrrs_nz_flush, csrrc_nz_flush, csrrsi_0_g1, csrrci_0_g1; CG-CSR-010.cp_seed_val.zero; the probe-gated cr_op_form_pulse bins are coverage-only |
| F-CSR-103 | F-CSR-009 | CG-CSR-015.cr_cause_reexec.illegal_no |
| F-PRV-003 | F-PRV-002 | CG-PRV-002.cr_entry.u_mie0_sync |
| F-PRV-004 | F-PRV-002 | CG-PRV-002.cr_entry.m_mie0_sync |
| F-PRV-008 | F-PRV-006 | CG-PRV-002.cr_mret_irq.m_0_pending |
| F-PRV-009 | F-PRV-006 | CG-PRV-001.cp_from.reset, CG-PRV-001.cr_trans.m_u_mret |
| F-PRV-014 | F-PRV-013 | CG-PRV-003.cr_eff.m_1_m_load_allow, CG-PRV-003.cr_eff.m_1_m_store_allow |
| F-PRV-017 | F-PRV-016 | CG-PRV-005.cr_priv_tw_post.m_tw1_resume |
| F-PRV-026 | F-DBG-012 | CG-PRV-007.cr_dret_prv.s_u |
| F-PRV-032 | F-PRV-002 | CG-PRV-008.cr_cause_mepc.exc_pc_wb_younger |
| F-PRV-033 | F-PRV-001 | CG-PRV-001.cr_trans.u_m_ecall |
| F-PRV-034 | F-CSR-014 | CG-CSR-001.cr_iclass_priv.wro_u |
| F-PRV-035 | F-CSR-023 | CG-CSR-002.cr_mst_fields.mprv_tw |
| F-EXC-024 | F-EXC-023 | CG-EXC-005.cp_priv.u |
| F-EXC-028 | F-EXC-026 | CG-EXC-006.cr_op_source_align.store_pmp_aligned |
| F-EXC-034 | F-EXC-025 | CG-EXC-006.cr_align_mtval.mis_both_eq_addr |
| F-EXC-038 | F-EXC-035 | CG-EXC-006.cp_younger.load_store, CG-EXC-006.cr_op_younger.load_load_store |
| F-EXC-039 | F-EXC-027 | CG-EXC-006.cr_op_source_align.store_bus_err_aligned |
| F-EXC-040 | F-EXC-035 | CG-EXC-006.cr_op_younger.load_load_store |
| F-EXC-042 | F-EXC-001 | CG-EXC-012.cp_mepc_bit1.bit1_1, CG-EXC-012.cr_kind_bit1.sync_bit1_1; CG-EXC-001.cr_cause_priv_ilen.illegal_m_c16 |
| F-EXC-045 | F-EXC-003 | CG-EXC-002.cp_flow.popret_target, CG-EXC-002.cr_flow_outcome.popret_target_trap; CG-EXC-008.cp_event.fetch_fault_ret_target |
| F-EXC-051 | F-EXC-050 | CG-EXC-012.cp_mepc_bit1.bit1_1, CG-EXC-012.cr_kind_bit1.sync_bit1_1 |
| F-EXC-058 | F-SEC-022 | CG-EXC-010.cp_first_cause.ecall |
| F-EXC-062 | F-EXC-001 | CG-EXC-013.cr_stage_latency.id_cause_min |
| F-EXC-063 | F-EXC-001 | CG-EXC-012.cp_minstret.ir0 |
| F-IRQ-010 | F-IRQ-009 | CG-IRQ-002.cr_set_winner.fast_fast_fast |
| F-IRQ-011 | F-IRQ-009 | CG-IRQ-002.cp_drain.first, middle, last18; CG-IRQ-002.cr_drain_winner.first_fast, middle_fast, middle_external, middle_software, last18_timer |
| F-IRQ-015 | F-IRQ-012 | CG-IRQ-006.cp_base_class.sw_aligned, sw_legalised; CG-IRQ-005.cp_mtvec_in_handler.rewritten, CG-IRQ-005.cr_nesting_mtvec.depth1_rewritten |
| F-IRQ-017 | F-IRQ-016 | CG-IRQ-004.cp_ctx.id_load_wait, id_store_wait; CG-IRQ-004.cr_ctx_outcome.id_load_wait_taken, id_store_wait_taken; CG-IRQ-004.cr_ctx_rvalid.id_load_wait_before_rvalid, id_load_wait_same_cycle_as_rvalid, id_load_wait_after_rvalid |
| F-IRQ-022 | F-EXC-035 | CG-IRQ-004.cr_ctx_outcome.wb_fault_same_cycle_deferred_by_exception |
| F-IRQ-026 | F-IRQ-009 | CG-IRQ-002.cp_late.higher_added, lower_added; CG-IRQ-002.cr_late_winner.higher_added_fast, higher_added_nmi_ext, higher_added_external, lower_added_external |
| F-IRQ-027 | F-IRQ-016 | CG-IRQ-005.cr_state_reentry.still_high_same_immediate |
| F-IRQ-029 | F-IRQ-016 | CG-IRQ-001.cr_upath_pending.mret_mpp_u_already_pending_mie0 |
| F-IRQ-034 | F-IRQ-009 | CG-IRQ-002.cr_set_winner.nmi_fast_nmi_ext |
| F-IRQ-038 | F-IRQ-030 | CG-IRQ-010.cr_line_mode_post.nmi_ext_debug_mode_taken_before_first_insn |
| F-IRQ-046 | F-IRQ-045 | CG-IRQ-009.cp_wake.irq_local_only, CG-IRQ-009.cr_priv_wake.m_irq_local_only |
| F-IRQ-047 | F-IRQ-045 | CG-IRQ-009.cp_disabled_high.yes, CG-IRQ-009.cr_disabled_wake.yes_none_long, yes_nmi_ext, yes_debug_req, yes_irq_taken |
| F-IRQ-049 | F-IRQ-045 | CG-IRQ-009.cp_wake.nmi_ext |
| F-IRQ-052 | F-IRQ-045 | CG-IRQ-009.cp_wake.masked_line_held |
| F-IRQ-053 | F-IRQ-045 | CG-IRQ-009.cp_priv_tw.u_tw0, CG-IRQ-009.cr_priv_wake.u_tw0_irq_taken, u_tw0_nmi_ext, u_tw0_debug_req, u_tw0_none_long, u_tw0_already_pending; CG-IRQ-001.cr_line_priv_mie.software_u_mie0, timer_u_mie0 |
| F-IRQ-058 | F-IRQ-002 | CG-IRQ-001.cp_mepc_src.branch_target, jump_target, mret_target, dret_target; CG-IRQ-001.cr_line_mepc.timer_branch_target, external_jump_target, fast_3_mret_target, fast_9_dret_target |
| F-IRQ-061 | F-IRQ-012 | CG-IRQ-006.cp_id.fast[14] |
| F-IRQ-062 | F-IRQ-012 | CG-IRQ-006.cp_id.fast[0] |
| F-IRQ-063 | F-IRQ-009 | CG-IRQ-002.cr_drain_winner.last18_timer |
| F-IRQ-064 | F-IRQ-045 | CG-IRQ-004.cr_ctx_latency.first_fetch_wake_two |
| F-PMP-003 | F-PMP-001 | CG-PMP-001.cp_res_bits.nonzero, CG-PMP-001.cr_res_op.nonzero_csrrw, nonzero_csrrs, nonzero_csrrc |
| F-PMP-005 | F-PMP-001 | CG-PMP-001.cr_rw01_mml.rw01_mml1_stored |
| F-PMP-010 | F-PMP-009 | CG-PMP-002.cr_tor_lock.nl_other_rlb0_written |
| F-PMP-011 | F-PMP-009 | CG-PMP-002.cr_tor_lock.nu_tor_rlb0_written |
| F-PMP-017 | F-PMP-016 | CG-PMP-004.cp_dbg.d1, CG-PMP-004.cr_dbg_class.d1_pmpcfg_read_only, d1_pmpcfg_write, d1_pmpaddr_read_only, d1_pmpaddr_write, d1_mseccfg_read_only, d1_mseccfg_write |
| F-PMP-019 | F-PMP-007 | CG-PMP-001.cr_lockmix_op.some_csrrw |
| F-PMP-031 | F-PMP-029 | CG-PMP-001.cr_mml_nonexec_accept.c1000_written, CG-PMP-001.cr_mml_nonexec_accept.c1100_written, CG-PMP-001.cr_mml_nonexec_accept.c1110_written, CG-PMP-001.cr_mml_nonexec_accept.c1111_written |
| F-PMP-032 | F-PMP-029 | CG-PMP-001.cr_mml_exec_suppress.rlb1_c1001_written, CG-PMP-001.cr_mml_exec_suppress.rlb1_c1010_written, CG-PMP-001.cr_mml_exec_suppress.rlb1_c1011_written, CG-PMP-001.cr_mml_exec_suppress.rlb1_c1101_written |
| F-PMP-039 | F-PMP-002 | CG-PMP-007.cr_hi_mode.napot_base_hi30, CG-PMP-007.cr_hi_mode.napot_base_hi31 |
| F-PMP-046 | F-PMP-045 | CG-PMP-006.cp_conflict.low_allow_high_deny, CG-PMP-006.cp_conflict.low_deny_high_allow |
| F-PMP-053 | F-PMP-052 | CG-PMP-014.cp_all_off_u.yes; CG-PMP-009.cr_priv_cause.u_c1_c16, u_c1_i32 |
| F-PMP-057 | F-PMP-056 | CG-PMP-005.cr_truth_mml1.c0001_m_fetch, CG-PMP-005.cr_truth_mml1.c0001_m_load, CG-PMP-005.cr_truth_mml1.c0001_m_store, CG-PMP-005.cr_truth_mml1.c0100_m_fetch, CG-PMP-005.cr_truth_mml1.c0100_m_load, CG-PMP-005.cr_truth_mml1.c0100_m_store, CG-PMP-005.cr_truth_mml1.c0101_m_fetch, CG-PMP-005.cr_truth_mml1.c0101_m_load, CG-PMP-005.cr_truth_mml1.c0101_m_store, CG-PMP-005.cr_truth_mml1.c0110_m_fetch, CG-PMP-005.cr_truth_mml1.c0110_m_load, CG-PMP-005.cr_truth_mml1.c0110_m_store, CG-PMP-005.cr_truth_mml1.c0111_m_fetch, CG-PMP-005.cr_truth_mml1.c0111_m_load, CG-PMP-005.cr_truth_mml1.c0111_m_store |
| F-PMP-058 | F-PMP-056 | CG-PMP-005.cr_truth_mml1.c1001_u_fetch, CG-PMP-005.cr_truth_mml1.c1001_u_load, CG-PMP-005.cr_truth_mml1.c1001_u_store, CG-PMP-005.cr_truth_mml1.c1100_u_fetch, CG-PMP-005.cr_truth_mml1.c1100_u_load, CG-PMP-005.cr_truth_mml1.c1100_u_store, CG-PMP-005.cr_truth_mml1.c1101_u_fetch, CG-PMP-005.cr_truth_mml1.c1101_u_load, CG-PMP-005.cr_truth_mml1.c1101_u_store, CG-PMP-005.cr_truth_mml1.c1110_u_fetch, CG-PMP-005.cr_truth_mml1.c1110_u_load, CG-PMP-005.cr_truth_mml1.c1110_u_store |
| F-PMP-059 | F-PMP-056 | CG-PMP-005.cr_truth_mml1.c0010_m_fetch, CG-PMP-005.cr_truth_mml1.c0010_m_load, CG-PMP-005.cr_truth_mml1.c0010_m_store, CG-PMP-005.cr_truth_mml1.c0010_u_fetch, CG-PMP-005.cr_truth_mml1.c0010_u_load, CG-PMP-005.cr_truth_mml1.c0010_u_store, CG-PMP-005.cr_truth_mml1.c0011_m_fetch, CG-PMP-005.cr_truth_mml1.c0011_m_load, CG-PMP-005.cr_truth_mml1.c0011_m_store, CG-PMP-005.cr_truth_mml1.c0011_u_fetch, CG-PMP-005.cr_truth_mml1.c0011_u_load, CG-PMP-005.cr_truth_mml1.c0011_u_store |
| F-PMP-060 | F-PMP-056 | CG-PMP-005.cr_truth_mml1.c1010_m_fetch, CG-PMP-005.cr_truth_mml1.c1010_m_load, CG-PMP-005.cr_truth_mml1.c1010_m_store, CG-PMP-005.cr_truth_mml1.c1010_u_fetch, CG-PMP-005.cr_truth_mml1.c1010_u_load, CG-PMP-005.cr_truth_mml1.c1010_u_store, CG-PMP-005.cr_truth_mml1.c1011_m_fetch, CG-PMP-005.cr_truth_mml1.c1011_m_load, CG-PMP-005.cr_truth_mml1.c1011_m_store, CG-PMP-005.cr_truth_mml1.c1011_u_fetch, CG-PMP-005.cr_truth_mml1.c1011_u_load, CG-PMP-005.cr_truth_mml1.c1011_u_store |
| F-PMP-061 | F-PMP-056 | CG-PMP-005.cr_truth_mml1.c1111_m_fetch, CG-PMP-005.cr_truth_mml1.c1111_m_load, CG-PMP-005.cr_truth_mml1.c1111_m_store, CG-PMP-005.cr_truth_mml1.c1111_u_fetch, CG-PMP-005.cr_truth_mml1.c1111_u_load, CG-PMP-005.cr_truth_mml1.c1111_u_store |
| F-PMP-062 | F-PMP-056 | CG-PMP-005.cr_truth_mml1.c0000_m_fetch, CG-PMP-005.cr_truth_mml1.c0000_m_load, CG-PMP-005.cr_truth_mml1.c0000_m_store, CG-PMP-005.cr_truth_mml1.c0000_u_fetch, CG-PMP-005.cr_truth_mml1.c0000_u_load, CG-PMP-005.cr_truth_mml1.c0000_u_store, CG-PMP-005.cr_truth_mml1.c1000_m_fetch, CG-PMP-005.cr_truth_mml1.c1000_m_load, CG-PMP-005.cr_truth_mml1.c1000_m_store, CG-PMP-005.cr_truth_mml1.c1000_u_fetch, CG-PMP-005.cr_truth_mml1.c1000_u_load, CG-PMP-005.cr_truth_mml1.c1000_u_store |
| F-PMP-064 | F-PMP-056 | CG-PMP-005.cr_truth_mml1.c0001_m_fetch, CG-PMP-005.cr_truth_mml1.c0101_m_fetch, CG-PMP-005.cr_truth_mml1.c0111_m_fetch |
| F-PMP-073 | F-PMP-072 | CG-PMP-012.cr_eff.m_mprv_mppm_load_effm, CG-PMP-012.cr_eff.m_mprv_mppm_store_effm |
| F-PMP-080 | F-PMP-078 | CG-PMP-009.cr_target.branch_c1, CG-PMP-009.cr_target.jump_c1, CG-PMP-009.cr_target.mret_c1, CG-PMP-009.cr_target.exc_entry_c1, CG-PMP-009.cr_target.dret_c1 |
| F-PMP-083 | F-PMP-082 | CG-PMP-008.cr_rd.load_c5_none |
| F-PMP-084 | F-PMP-082 | CG-PMP-008.cr_lat.aligned_denied_lat2, CG-PMP-008.cr_align_nreq.aligned_denied_n0 |
| F-PMP-090 | F-PMP-086 | CG-PMP-008.cr_half_align.h16_mis_none_load, CG-PMP-008.cr_half_align.h16_mis_none_store, CG-PMP-008.cr_half_align.h16_mis_first_load, CG-PMP-008.cr_half_align.h16_mis_first_store, CG-PMP-008.cr_half_align.h16_mis_second_load, CG-PMP-008.cr_half_align.h16_mis_second_store, CG-PMP-008.cr_half_align.h16_mis_both_load, CG-PMP-008.cr_half_align.h16_mis_both_store |
| F-PMP-096 | F-PMP-095 | CG-PMP-013.cr_no_bypass.nodbg_dm_fetch_deny, CG-PMP-013.cr_no_bypass.nodbg_dm_load_deny, CG-PMP-013.cr_no_bypass.nodbg_dm_store_deny |
| F-PMP-100 | F-PMP-007 | CG-PMP-011.cr_bb.lock_then_addr, CG-PMP-011.cr_bb.lock_then_cfg |
| F-DBG-014 | F-DBG-012 | CG-DBG-007.cr_bit_rb.cause_c |
| F-DBG-015 | F-DBG-012 | CG-DBG-007.cr_bit_rb.stepie_0, stopcount_0, stoptime_0, mprven_0, nmip_0, z27_0, z14_0, z5_0 |
| F-DBG-019 | F-DBG-017 | CG-DBG-003.cr_priv_en_outcome.u_off_on_dbg, u_on_on_dbg; CG-DBG-001.cr_cause_prv.ebreak_u |
| F-DBG-021 | F-DBG-017 | CG-DBG-003.cr_priv_en_outcome.m_off_on_exc, u_on_off_exc |
| F-DBG-027 | F-PRV-002 | CG-DBG-004.cp_kind.load_pmp, store_pmp, load_bus, store_bus |
| F-DBG-028 | F-PRV-002 | CG-DBG-004.cp_kind.illegal, illegal_csr |
| F-DBG-029 | F-PRV-002 | CG-DBG-004.cp_kind.ecall |
| F-DBG-030 | F-PRV-002 | CG-DBG-004.cp_kind.fetch_pmp, fetch_bus |
| F-DBG-034 | F-DBG-031 | CG-DBG-005.cr_prvsrc_target.swu_u, swm_m; CG-DBG-005.cr_prv_next.u_run |
| F-DBG-038 | F-DBG-037 | CG-DBG-006.cr_stepped_prv.brtaken_m, jal_m, jalr_m; CG-DBG-001.cp_dpc_kind.br_target |
| F-DBG-039 | F-DBG-037 | CG-DBG-006.cr_stepped_prv.brnot_m, cbrnot_m, comp_m; CG-DBG-001.cr_cause_dpc.step_next |
| F-DBG-041 | F-DBG-017 | CG-DBG-003.cr_coincident_outcome.step_dbg; CG-DBG-006.cr_stepped_retired.ebreakdbg_ok |
| F-DBG-043 | F-DBG-037 | CG-DBG-006.cr_pending_cause.nmi_step; CG-DBG-009.cr_src_window.nmi_step |
| F-DBG-046 | F-DBG-001 | CG-DBG-006.cr_stepped_retired.push_ok, popret_ok; CG-DBG-001.cr_cause_ctx.step_zcmp |
| F-DBG-047 | F-DBG-037 | CG-DBG-006.cr_stepped_prv.loadslow_m, storeslow_m, div_m |
| F-TRG-002 | F-TRG-001 | CG-TRG-001.cr_csr_mode_result.tsel_m_drop, CG-TRG-001.cr_tselw_mode.one_m, ones_m |
| F-TRG-011 | F-TRG-010 | CG-TRG-002.cr_exec_fired.off_nf |
| F-TRG-012 | F-TRG-010 | CG-TRG-002.cr_priv_fired.u_f; CG-DBG-001.cr_cause_prv.trigger_u |
| F-TRG-013 | F-TRG-010 | CG-TRG-002.cp_ctx.in_debug, CG-TRG-002.cr_ctx_fired.indebug_nf |
| F-TRG-014 | F-TRG-010 | CG-TRG-002.cp_ctx.comp2, CG-TRG-002.cr_ctx_fired.comp2_f |
| F-TRG-016 | F-DBG-031 | CG-DBG-005.cr_prv_next.m_rehalt_trig, u_rehalt_trig; CG-TRG-002.cr_ctx_fired.dret_f |
| F-TRG-022 | F-TRG-010 | CG-TRG-002.cr_dit_fall.dit1_falltaken_nf, dit1_fallnt_f |
| F-TRG-025 | F-DBG-001 | CG-TRG-002.cr_coinc_cause.irq_trig, nmi_trig; CG-DBG-009.cr_window_disp.entry_wins |
| F-TRG-026 | F-TRG-010 | CG-TRG-002.cr_ctx_fired.dummy_f |
| F-TRG-028 | F-TRG-003 | CG-TRG-001.cp_td1_rb.en_after_hit |
| F-TRG-030 | F-TRG-010 | CG-TRG-002.cr_ctx_fired.jalr_f, seq32_f, br_f |
| F-PMC-002 | F-PMC-001 | CG-PMC-001.cr_ctx_delta.wfi_eq, debug_eq |
| F-PMC-003 | F-PMC-001 | CG-PMC-001.cp_carry.seen, CG-PMC-001.cr_carry_ctx.carry_run |
| F-PMC-008 | F-PMC-007 | CG-PMC-002.cr_window_delta.selfwr_eq |
| F-PMC-013 | F-PMC-007 | CG-PMC-002.cp_wrap.carry, CG-PMC-002.cr_wrap_op.carry_rdhi, carry_rdlo |
| F-PMC-023 | F-PMC-021 | CG-PMC-007.cr_target_inh_then.hpm_inh_resume, mcycle_inh_resume, minstret_inh_resume |
| F-PMC-031 | F-PMC-021 | CG-PMC-006.cr_inhibit_gate.inh_set_u_ok |
| F-PMC-035 | F-PMC-034 | CG-PMC-003.cr_variant_rel.pmpden_eq |
| F-PMC-037 | F-PMC-034 | CG-PMC-003.cp_variant.straddle_pmp, CG-PMC-003.cr_variant_rel.straddle_eq |
| F-PMC-048 | F-PMC-007 | CG-PMC-002.cr_window_delta.step_one, step_zero; CG-DBG-006.cr_stepped_minstret.alu_one, wfi_one, ecall_zero |
| F-PMC-051 | F-PMC-001 | CG-PMC-001.cr_op_wdata.wrlo_z, wrlo_1, wrhi_z, wrhi_1; CG-PMC-002.cr_op_wdata.wrlo_z, wrlo_1, wrhi_z, wrhi_1; CG-PMC-004.cr_wdata_reg.z_lo, o_lo, z_hi, o_hi |
| F-PMC-052 | F-PMC-007 | CG-PMC-002.cr_window_delta.irq_eq |
| F-IMEM-005 | F-IMEM-001 | CG-IMEM-001.cp_gnt_delay.d16p |
| F-IMEM-020 | F-IMEM-019 | CG-IMEM-004.cp_seq_kind.end_of_line_stop |
| F-IMEM-023 | F-RST-010 | CG-IMEM-005.cp_gate_cause.fetch_en_invalid, CG-IMEM-005.cp_fetch_en_code.invalid_0, invalid_f |
| F-DMEM-005 | F-DMEM-001 | CG-DMEM-001.cp_gnt_delay.d16p |
| F-DMEM-020 | F-DMEM-014 | CG-DMEM-002.cr_be_x_beat.second_0001 |
| F-DMEM-023 | F-DMEM-015 | CG-DMEM-004.cp_err_beat.both |
| F-DMEM-025 | F-DMEM-008 | CG-DMEM-003.cp_path.gnt2_before_rvalid1 |
| F-FE-023 | F-IMEM-011 | CG-FE-005.cp_next_fetch.exc_vector |
| F-FE-024 | F-FE-012 | CG-FE-004.cp_cause.zcmp_expand |
| F-IC-009 | F-IC-008 | CG-IC-002.cp_key_req_at_reset.skipped_valid_high |
| F-IC-015 | F-IC-014 | CG-IC-003.cp_hit_cadence.run4p |
| F-IC-016 | F-IC-014 | CG-IC-003.cp_miss_forward_latency.l3 |
| F-IC-018 | F-IC-017 | CG-IC-003.cr_result_x_fill.evict_both |
| F-IC-032 | F-IC-030 | CG-IC-006.cp_lookups_blocked_next.yes |
| F-IC-033 | F-IC-030 | CG-IC-006.cp_bits.single, CG-IC-006.cp_bits.double |
| F-IC-034 | F-IC-030 | CG-IC-006.cp_major_nmi_quiet.yes |
| F-IC-041 | F-IC-012 | CG-IC-005.cp_effect_latency.next_lookup |
| F-DIT-004 | F-DIT-003 | CG-DIT-003.cr_latency.div_off_zero_two; CG-DIT-003.cr_div_dit_zero.div_off_zero |
| F-DIT-007 | F-DIT-002 | CG-DIT-002.cr_dit_taken_c.on_nt_c16, CG-DIT-002.cp_compressed.c16 |
| F-DIT-009 | F-DIT-003 | CG-DIT-004.cr_type_dit.div_on, div_off; CG-DIT-004.cr_div_zero.div_zero_on, div_zero_off |
| F-DIT-010 | F-DIT-002 | CG-DIT-002.cr_dit_priv.on_u; CG-DIT-002.cr_dit_priv.off_u; CG-DIT-001.cp_access.u_trap |
| F-DIT-012 | F-DIT-011 | CG-DIT-001.cp_mask.m000; CG-DIT-001.cp_mask.m001; CG-DIT-001.cp_mask.m010; CG-DIT-001.cp_mask.m011; CG-DIT-001.cp_mask.m100; CG-DIT-001.cp_mask.m101; CG-DIT-001.cp_mask.m110; CG-DIT-001.cp_mask.m111; CG-DIT-001.cr_dummy_mask.on_m000; CG-DIT-001.cr_dummy_mask.on_m001; CG-DIT-001.cr_dummy_mask.on_m010; CG-DIT-001.cr_dummy_mask.on_m011; CG-DIT-001.cr_dummy_mask.on_m100; CG-DIT-001.cr_dummy_mask.on_m101; CG-DIT-001.cr_dummy_mask.on_m110; CG-DIT-001.cr_dummy_mask.on_m111 |
| F-DIT-024 | F-DIT-013 | CG-DIT-004.cr_type_dit.div_off; CG-DIT-004.cr_type_dit.mul_off; CG-DIT-004.cr_type_dit.add_off; CG-DIT-004.cr_type_dit.and_off |
| F-SEC-005 | F-SEC-004 | CG-RST-004.cr_fwd_bank.yes_x1_15; CG-RST-004.cr_fwd_bank.yes_x16; CG-RST-004.cr_fwd_bank.yes_x17_31 |
| F-SEC-006 | F-SEC-004 | CG-SEC-001.cp_internal_total.zero |
| F-SEC-008 | F-SEC-007 | CG-RVFI-001.cp_pc_delta.plus2; CG-RVFI-001.cp_pc_delta.plus4; CG-SEC-001.cp_internal_total.zero |
| F-SEC-012 | F-RST-010 | CG-RST-003.cp_transition.on2inv; CG-SEC-005.cp_fetch_en_val.invalid |
| F-SEC-016 | F-SEC-003 | CG-SEC-002.cr_side_op.dbus_store; CG-SEC-001.cr_alert_inject.major_bus_dbus_store_intg |
| F-SEC-023 | F-SEC-022 | CG-SEC-003.cp_debug_mode.yes |
| F-SEC-030 | F-SEC-027 | CG-SEC-004.cp_debug_mode.yes, CG-SEC-004.cr_exc_debug.exception_pc_yes_no |
| F-SEC-032 | F-CSR-085 | CG-DIT-001.cp_wr_reserved.bits31_9; CG-DIT-001.cp_wr_reserved.bit8; CG-DIT-001.cp_wr_reserved.both; CG-SEC-005.cp_bits67_readback.b6_1_b7_1 |
| F-RST-011 | F-RST-010 | CG-XIF-008.cp_inflight.data_outst, CG-XIF-008.cr_enc_x_inflight.mubi_off_data_outst; CG-RST-003.cp_pipe_state.id_busy |
| F-RST-017 | F-RST-016 | CG-SEC-006.cp_hold_cause.fetch_outstanding, CG-SEC-006.cp_off_reason.none |
| F-RST-025 | F-RST-003 | CG-SEC-005.cp_event.boot_addr_change; CG-SEC-005.cp_boot_addr_change_ctx.running |
| F-RST-026 | F-RVFI-003 | CG-RVFI-001.cp_order_step.first |
| F-RVFI-024 | F-DIT-016 | CG-DIT-004.cp_event.insert; CG-RVFI-001.cp_valid_gap.g2 |
| F-RVFI-033 | F-RST-009 | CG-RST-001.cp_reset_kind.power_on; CG-RST-001.cp_reset_kind.mid_run |

190 folds.

# 4. Features


# 4.1 Areas ISA, MUL, CMP, BIT, BTALU: Instruction set: RV32I base, M (RV32MSingleCycle), compressed Zca/Zcb/Zcmp, bitmanip RV32BOTEarlGrey, branch target ALU


Build: `opentitan` config (RV32I, RV32MSingleCycle, RV32BOTEarlGrey, RV32ZcaZcbZcmp, BranchTargetALU=1,
WritebackStage=1, SecureIbex=1). CHERIoT mode out of scope (cheriot_enable_i tied off): every
`cheriot_enable_i == IbexMuBiOn` branch in the decoder/compressed decoder is dead for this DUT.

Conventions used below:
- Status field (added after the Critic's v1 review, README_FIX_BRIEF rule 1): ACTIVE = counted in the
  completeness measure; ALIAS of F-x = the same behaviour stated from this area's perspective, the
  canonical entry is F-x; FOLDED into F-x (bin b) = a former edge entry that restated its parent, the
  parent's coverage bin b now carries it. ALIAS/FOLDED blocks keep their ID, title, Source and Edge
  line so existing test-plan citations resolve; only ACTIVE entries count.
- Edge rule (Critic C-12) applied to every "Edge: yes" entry of this part: kept only if its What names a
  stimulus condition or timing coincidence the parent does not, and its observable or expected outcome
  differs; otherwise folded into the parent's bin. Concrete boundary operand values with distinct
  results, minimal/maximal structures (rlist 4 / 15) and event coincidences are kept; rows of the
  parent's own enumeration, the parent's Config at another value and checker bullets are folded.
- Observable at names ibex_core ports (instr_req_o/instr_addr_o, data_req_o/data_addr_o/data_we_o/
  data_be_o/data_wdata_o, core_busy_o, irq_pending_o, ic_tag_req_o/ic_tag_write_o) or RVFI fields
  (rvfi_valid/rvfi_insn/rvfi_pc_rdata/rvfi_pc_wdata/rvfi_rs1_*/rvfi_rs2_*/rvfi_rs3_*/rvfi_rd_addr/
  rvfi_rd_wdata/rvfi_trap/rvfi_intr/rvfi_mode/rvfi_mem_*/rvfi_ext_mcycle/rvfi_ext_mhpmcounters/
  rvfi_ext_debug_mode/rvfi_ext_expanded_insn*, rtl/ibex_core.sv:137-181). CSR state is observed as
  "csrr read-back on rvfi_rd_wdata", exceptions as "rvfi_trap + csrr read-back of mcause/mtval", trap
  and redirect targets as "instr_addr_o = <vector>". The core has NO rvfi_csr_* ports and no
  core_sleep_o (that port is ibex_top's; sleep is observed as core_busy_o low). Internal nets are
  named only as "probe candidate P<n> (probe register entry needed)" with the boundary alternative first.

---------------------------------------------------------------------------------------------------
## AREA ISA: RV32I base integer instructions and SYSTEM/MISC-MEM decode

### F-ISA-001: Register-immediate ALU instructions (addi, slti, sltiu, xori, ori, andi)
- What: I-type ops on rs1 and the sign-extended 12-bit immediate; result written to rd; no arithmetic
  exceptions. Single cycle in ID/EX.
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_rs1_rdata, rvfi_insn)
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Integer Register-Immediate Instructions" |
  RTL-defined: rtl/ibex_decoder.sv:488-499, rtl/ibex_decoder.sv:1075-1087, rtl/ibex_alu.sv:104-109,
  rtl/ibex_alu.sv:361-397
- Edge: no
- Status: ACTIVE
- Notes: funct3 010/011/100/110/111 have no funct7 sub-decode; the whole imm field is data.

### F-ISA-002: addi overflow wraps to low 32 bits
- What: addi rs1=0x7FFFFFFF, imm=+1 gives 0x80000000; rs1=0x80000000, imm=-1 gives 0x7FFFFFFF.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Immediate Instructions" (norm:addi_overflow) |
  RTL-defined: rtl/ibex_alu.sv:105-107 (33-bit adder, bit 32 discarded)
- Edge: yes, of F-ISA-001
- Status: ACTIVE

### F-ISA-003: slti/sltiu boundary comparisons
- What: slti with rs1 == imm gives 0; slti(INT_MIN, 0)=1; slti(0, INT_MIN)=0; sltiu treats the
  sign-extended imm as unsigned (sltiu rs1, -1 compares against 0xFFFFFFFF); sltiu rs1, 1 is seqz.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Immediate Instructions" (norm:slti_sltiu_op) |
  RTL-defined: rtl/ibex_alu.sv:119-142, rtl/ibex_alu.sv:159-171
- Edge: yes, of F-ISA-001
- Status: ACTIVE

### F-ISA-004: HINT encodings with rd=x0 execute as no-ops
- What: addi/andi/ori/xori/slti/sltiu/lui/auipc/add/sub/sll/... with rd=x0 (including the canonical
  nop addi x0,x0,0) are legal, advance the PC, increment minstret, and change no register.
- Observable at: RVFI (rvfi_rd_addr = 0, rvfi_rd_wdata = 0, rvfi_trap = 0); csrr read-back of
  minstret on rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "HINT Instructions", "NOP Instruction" | RTL-defined: rtl/ibex_decoder.sv:469-471,
  rtl/ibex_decoder.sv:488-491, rtl/ibex_decoder.sv:588-591 (rf_we asserted, x0 write discarded by RF)
- Edge: yes, of F-ISA-001
- Status: ACTIVE
- Notes: Ibex has no HINT-specific behaviour; only x0 discard. Semihosting markers slli x0,x0,0x1f /
  srai x0,x0,7 must also decode legal.

### F-ISA-005: lui and auipc
- What: lui rd = imm[31:12] << 12; auipc rd = pc + (imm[31:12] << 12).
- Observable at: RVFI rvfi_rd_wdata, rvfi_pc_rdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Immediate Instructions" (norm:lui_op, norm:auipc_op) |
  RTL-defined: rtl/ibex_decoder.sv:469-486, rtl/ibex_decoder.sv:1059-1073
- Edge: no
- Status: ACTIVE

### F-ISA-006: lui/auipc immediate extremes and PC wrap
- What: lui with imm=0xFFFFF gives 0xFFFFF000; lui imm=0 gives 0; auipc executed at PC 0xFFFFF000 with
  imm=0x00001 wraps to 0x00000000; auipc imm=0 returns the PC of the instruction (also for a
  compressed-adjacent 2-byte aligned PC).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Immediate Instructions" | RTL-defined: rtl/ibex_alu.sv:105-107
- Edge: yes, of F-ISA-005
- Status: ACTIVE

### F-ISA-007: Register-register ALU instructions (add, sub, slt, sltu, xor, or, and)
- What: R-type ops on rs1/rs2 with funct7 0000000 (0100000 for sub); result to rd; single cycle.
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_rs1_rdata, rvfi_rs2_rdata)
- Config: none
- Source: spec: rv32.adoc "Integer Register-Register Instructions" | RTL-defined: rtl/ibex_decoder.sv:588-606,
  rtl/ibex_decoder.sv:1250-1258
- Edge: no
- Status: ACTIVE

### F-ISA-008: add/sub overflow wrap
- What: add 0xFFFFFFFF + 1 = 0; sub 0 - 1 = 0xFFFFFFFF; sub INT_MIN - 1 = INT_MAX; add INT_MAX + INT_MAX.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Register Instructions" (norm:add_sub_overflow) |
  RTL-defined: rtl/ibex_alu.sv:94-107
- Edge: yes, of F-ISA-007
- Status: ACTIVE

### F-ISA-009: slt/sltu sign and equality boundaries
- What: slt with rs1==rs2 gives 0; slt(INT_MIN, INT_MAX)=1; sltu(0x80000000, 1)=0; sltu(x0, rs2)
  (snez) gives 1 iff rs2 != 0; sltu(0xFFFFFFFF, 0xFFFFFFFF)=0.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Register Instructions" (norm:slt_sltu_op) |
  RTL-defined: rtl/ibex_alu.sv:119-171
- Edge: yes, of F-ISA-007
- Status: ACTIVE

### F-ISA-010: Shift-immediate instructions (slli, srli, srai)
- What: shamt = instr[24:20]; slli zero-fills low, srli zero-fills high, srai copies sign; funct7 must be
  0000000 (slli/srli) or 0100000 (srai).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Immediate Instructions" (norm:slli_op, norm:srli_op, norm:srai_op) |
  RTL-defined: rtl/ibex_decoder.sv:500-502, rtl/ibex_decoder.sv:543-545, rtl/ibex_decoder.sv:1091,
  rtl/ibex_decoder.sv:1167-1168, rtl/ibex_alu.sv:329-355
- Edge: no
- Status: ACTIVE

### F-ISA-011: Shift amount 0 and 31, sign propagation
- What: shift by 0 returns rs1 unchanged; slli by 31 of 1 gives 0x80000000; srai by 31 of a negative
  gives 0xFFFFFFFF; srai by 31 of positive gives 0; srli by 31 of 0x80000000 gives 1; srai of
  0x80000000 by 1 gives 0xC0000000.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Immediate Instructions" | RTL-defined: rtl/ibex_alu.sv:342-353
- Edge: yes, of F-ISA-010
- Status: ACTIVE

### F-ISA-012: Reserved shift-immediate encodings: which trap and which decode as fsri
- What: Trap (illegal instruction): slli (instr[31:27] = 00000) with instr[26:25] in {01, 10, 11},
  and srli/srai (instr[31:27] = 00000 / 01000) with instr[26:25] = 01. Do NOT trap: under funct3 =
  101 any encoding with instr[26] = 1 decodes as the Zbt fsri (legal with RV32B != None; rs3 =
  instr[31:27], shamt = instr[25:20]) before the instr[31:27] case is reached, so the srli/srai bit
  patterns with instr[26:25] in {10, 11} execute as fsri (rs3 = x0 for the srli pattern, x8 for the
  srai pattern); under funct3 = 001 instr[31:27] = 00100 (sloi) executes for any instr[26:25]
  (F-BIT-037).
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (the 32-bit word) on rvfi_rd_wdata
  for the trapping encodings; rvfi_trap = 0 with rvfi_rs3_addr = instr[31:27] and rvfi_rd_wdata =
  the fsri result for the instr[26] = 1 encodings
- Config: none
- Source: spec: rv32.adoc "Integer Register-Immediate Instructions" (shift amount is the lower 5
  bits; reserved encodings UNSPECIFIED) | RTL-defined: rtl/ibex_decoder.sv:500-505 (slli / sloi),
  rtl/ibex_decoder.sv:539-546 (fsri takes precedence, then srli/srai)
- Edge: yes, of F-ISA-010
- Status: ACTIVE
- Notes: Ibex chooses illegal-instruction for the truly reserved patterns. A reference model without
  Zbt (Spike) would predict a trap for the instr[26] = 1 forms; the checker for those is
  gen_chk_bitmanip_ref (Critic C-05).

### F-ISA-013: Shift-register instructions (sll, srl, sra)
- What: shift rs1 by rs2[4:0].
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_rs1_rdata, rvfi_rs2_rdata)
- Config: none
- Source: spec: rv32.adoc "Integer Register-Register Instructions" (norm:sll_srl_sra_op) |
  RTL-defined: rtl/ibex_decoder.sv:604-606, rtl/ibex_decoder.sv:1259-1261, rtl/ibex_alu.sv:286-288
- Edge: no
- Status: ACTIVE

### F-ISA-014: Shift-register ignores rs2 upper bits
- What: rs2 = 32, 0xFFFFFFE0, 0x80000000 all shift by 0; rs2 = 0xFFFFFFFF shifts by 31; rs2 = 33 shifts by 1.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: rv32.adoc "Integer Register-Register Instructions" ("lower 5 bits of register rs2") |
  RTL-defined: rtl/ibex_alu.sv:286-288 (shift_amt[4:0] = operand_b_i[4:0])
- Edge: yes, of F-ISA-013
- Status: ACTIVE

### F-ISA-015: jal
- What: target = pc + sign-extended J-immediate (multiple of 2); rd = pc + 4 (pc + 2 when the jal came from
  c.jal/c.j). With BranchTargetALU=1 the jump completes in one ID cycle (target from BTALU, link from main
  ALU) and the IF stage is redirected.
- Observable at: RVFI (rvfi_rd_wdata, rvfi_pc_wdata), instr_req_o/instr_addr_o redirect
- Config: none
- Source: spec: rv32.adoc "Unconditional Jumps" (norm:jal_target, norm:jal_op) |
  RTL-defined: rtl/ibex_decoder.sv:324-335, rtl/ibex_decoder.sv:952-972, rtl/ibex_id_stage.sv:936-942
- Edge: no
- Status: ACTIVE

### F-ISA-016: jal rd=x0 (j), rd=x1/x5, offset extremes and wrap
- What: rd=x0 writes nothing; offset +0xFFFFE (max forward) and -0x100000 (max backward); jal at PC
  0x00000000 with negative offset wraps to high memory; jal to itself (offset 0) loops.
- Observable at: RVFI rvfi_pc_wdata, rvfi_rd_addr
- Config: none
- Source: spec: rv32.adoc "Unconditional Jumps" | RTL-defined: rtl/ibex_decoder.sv:165 (imm_j),
  rtl/ibex_ex_block.sv:98-101 (carry discarded)
- Edge: yes, of F-ISA-015
- Status: ACTIVE

### F-ISA-017: Link value is pc + instruction length
- What: Folded into F-ISA-015 (bin CG-ISA-006.cr_link.c_jal_pc2): link value is pc + 4 for 32-bit
  jal/jalr and pc + 2 for c.jal/c.jalr (IMM_B_INCR_PC), already stated by the parent.
- Observable at: see F-ISA-015
- Config: see F-ISA-015
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/zca.adoc "Control Transfer Instructions" (c.jal, c.jalr
  write pc+2) | RTL-defined: rtl/ibex_decoder.sv:966-970, rtl/ibex_decoder.sv:988-992,
  rtl/ibex_id_stage.sv:396
- Edge: yes, of F-ISA-015
- Status: FOLDED into F-ISA-015 (bin CG-ISA-006.cr_link.c_jal_pc2)

### F-ISA-018: jalr
- What: target = (rs1 + sign-extended I-imm) with bit 0 cleared; rd = pc + 4; funct3 must be 000.
- Observable at: RVFI (rvfi_rs1_rdata, rvfi_rd_wdata, rvfi_pc_wdata), instr_addr_o
- Config: none
- Source: spec: rv32.adoc "Unconditional Jumps" (norm:jalr_target, norm:jalr_op) |
  RTL-defined: rtl/ibex_decoder.sv:353-369, rtl/ibex_decoder.sv:974-994, rtl/ibex_if_stage.sv:244,
  rtl/ibex_if_stage.sv:288
- Edge: no
- Status: ACTIVE

### F-ISA-019: jalr odd target: LSB cleared, no exception
- What: rs1+imm with bit 0 = 1 fetches from the even address; no instruction-address-misaligned exception
  (IALIGN=16 with Zca). The clear happens in the IF stage, not in the BTALU (see F-BTALU-008 for the RVFI
  consequence).
- Observable at: instr_addr_o (bit 0 = 0), rvfi_pc_rdata of the next instruction
- Config: none
- Source: spec: rv32.adoc "Unconditional Jumps" (norm:jalr_target, norm:jump_misaligned_c_no_exception),
  zca.adoc "Zca_no_misaligned" | RTL-defined: rtl/ibex_if_stage.sv:288, rtl/ibex_if_stage.sv:416
- Edge: yes, of F-ISA-018
- Status: ACTIVE

### F-ISA-020: jalr with rs1 == rd
- What: jalr x1, x1, 0 uses the old x1 as target and then writes pc+4 to x1 (single-cycle, operands read
  before write).
- Observable at: RVFI rvfi_rs1_rdata, rvfi_rd_wdata, rvfi_pc_wdata
- Config: none
- Source: spec: rv32.adoc "Unconditional Jumps" (rd=rs1 case in RAS hints table) |
  RTL-defined: rtl/ibex_id_stage.sv:369-377 (bt_a from rf_rdata_a_fwd), rtl/ibex_decoder.sv:353-369
- Edge: yes, of F-ISA-018
- Status: ACTIVE

### F-ISA-021: jalr funct3 != 000 is illegal
- What: opcode 1100111 with funct3 001..111 raises illegal-instruction; rd/rs1 fields are not checked.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (the 32-bit word) on
  rvfi_rd_wdata; no instr_addr_o redirect for the encoding
- Config: none
- Source: RTL-defined: rtl/ibex_decoder.sv:364-366 (spec: encodings UNSPECIFIED/reserved)
- Edge: yes, of F-ISA-018
- Status: ACTIVE

### F-ISA-022: jalr target wrap and rs1=x0 base
- What: rs1=0xFFFFFFF0 + imm 0x20 wraps to 0x00000010; rs1=x0 with negative imm targets high 2 KiB; imm
  -2048/+2047 extremes.
- Observable at: instr_addr_o, RVFI rvfi_pc_wdata
- Config: none
- Source: spec: rv32.adoc "Unconditional Jumps" | RTL-defined: rtl/ibex_ex_block.sv:98-101
- Edge: yes, of F-ISA-018
- Status: ACTIVE

### F-ISA-023: Conditional branches (beq, bne, blt, bge, bltu, bgeu)
- What: compare rs1/rs2 (signed for blt/bge, unsigned for bltu/bgeu); if taken, target = pc + B-imm
  (multiple of 2, +-4 KiB). Comparison result comes from the main ALU in the first cycle
  (branch_decision_i); target from the BTALU.
- Observable at: RVFI rvfi_pc_wdata, instr_req_o/instr_addr_o redirect, rvfi_ext_mhpmcounters
  (branch / taken-branch events)
- Config: none
- Source: spec: rv32.adoc "Conditional Branches" (norm:br_target, norm:beq_bne_op, norm:blt_bltu_op,
  norm:bge_bgeu_op) | RTL-defined: rtl/ibex_decoder.sv:372-387, rtl/ibex_decoder.sv:996-1028,
  rtl/ibex_alu.sv:159-171, rtl/ibex_id_stage.sv:920-935
- Edge: no
- Status: ACTIVE

### F-ISA-024: Branch not taken vs taken timing
- What: Alias of F-BTALU-001: ISA-side statement of the branch not-taken/taken timing that the
  branch-target-ALU feature owns; see the canonical entry.
- Observable at: see F-BTALU-001 (canonical)
- Config: see F-BTALU-001
- Source: RTL-defined: rtl/ibex_id_stage.sv:771-793 (g_branch_set_flop is the elaborated block under
  SecureIbex/DataIndTiming=1; :790-791 select the direct path when data_ind_timing_i = 0),
  rtl/ibex_id_stage.sv:920-935 | doc: doc/03_reference/pipeline_details.rst "Multi- and Single-Cycle
  Instructions" (Branch rows)
- Edge: yes, of F-ISA-023
- Status: ALIAS of F-BTALU-001

### F-ISA-025: Branch funct3 010/011 illegal
- What: opcode 1100011 with funct3 010 or 011 raises illegal-instruction (rs1/rs2 still read-enabled but
  branch suppressed).
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval on rvfi_rd_wdata; no instr_addr_o
  redirect to pc + offset
- Config: none
- Source: RTL-defined: rtl/ibex_decoder.sv:375-383, rtl/ibex_decoder.sv:912-920
- Edge: yes, of F-ISA-023
- Status: ACTIVE

### F-ISA-026: Branch to self and offset extremes
- What: beq x0,x0,0 (offset 0, taken) re-executes itself (infinite loop; use interrupt/debug to leave);
  offsets +4094 and -4096; branch target wrapping around address 0.
- Observable at: RVFI rvfi_pc_wdata == rvfi_pc_rdata
- Config: none
- Source: spec: rv32.adoc "Conditional Branches" | RTL-defined: rtl/ibex_decoder.sv:163 (imm_b)
- Edge: yes, of F-ISA-023
- Status: ACTIVE

### F-ISA-027: Branch comparison at sign/unsigned boundaries
- What: blt(INT_MIN, 0) taken, bltu(INT_MIN, 0) not taken; bge with equal operands taken; bgeu(0,
  0xFFFFFFFF) not taken; bne(x, x) not taken; beq(0x80000000, 0x80000000) taken.
- Observable at: RVFI rvfi_pc_wdata
- Config: none
- Source: spec: rv32.adoc "Conditional Branches" | RTL-defined: rtl/ibex_alu.sv:119-171
- Edge: yes, of F-ISA-023
- Status: ACTIVE

### F-ISA-028: Load/store decode legality (semantics owned elsewhere)
- What: Legal: lb/lh/lw/lbu/lhu (funct3 000/001/010/100/101), sb/sh/sw (funct3 000/001/010). Illegal:
  lwu (funct3 110), load funct3 011 (ld) and 111, store funct3 011 (sd) and 1xx.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval on rvfi_rd_wdata for the illegal
  forms; data_req_o never asserted for them
- Config: none
- Source: spec: rv32.adoc "Load and Store Instructions" | RTL-defined: rtl/ibex_decoder.sv:399-411,
  rtl/ibex_decoder.sv:433-461, rtl/ibex_decoder.sv:912-920
- Edge: no
- Status: ACTIVE
- Notes: In this build (BaseIsa=RV32IorCHERIoT, cheriot off) funct3 011 load/store hits the `else`
  illegal branch (rtl/ibex_decoder.sv:454-457, 408-411).

### F-ISA-029: fence is a nop
- What: fence (MISC-MEM funct3 000) executes as a single-cycle nop regardless of fm/pred/succ/rs1/rd
  (including fence.tso fm=1000 and HINT forms pred=0 or succ=0). No memory ordering action is needed
  because Ibex issues data accesses strictly in order.
- Observable at: RVFI (rvfi_valid, no rd write), rvfi_ext_mcycle
- Config: none
- Source: spec: rv32.adoc "Memory Ordering Instructions" (norm:fence_op, norm:fence_unused_flds_rsv) |
  RTL-defined: rtl/ibex_decoder.sv:706-709, rtl/ibex_decoder.sv:1399-1404
- Edge: no
- Status: ACTIVE

### F-ISA-030: fence.i flushes the fetch path
- What: fence.i (MISC-MEM funct3 001) is executed as a jump to pc+4: jump_set in the first cycle,
  icache_inval_o asserted, prefetch buffer flushed, outstanding fetch responses dropped; next fetch
  restarts at pc+4.
- Observable at: instr_req_o/instr_addr_o (fetch restarts at pc + 4), ic_tag_req_o/ic_tag_write_o
  (invalidation walk when the icache is enabled), rvfi_pc_wdata = pc + 4, rvfi_ext_mcycle (stall)
- Config: none (cpuctrlsts.icache_enable affects icache invalidation path)
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/zifencei.adoc "fence.i" (norm:fence_i_op) |
  doc: doc/03_reference/pipeline_details.rst "Instruction Fence" row | RTL-defined:
  rtl/ibex_decoder.sv:710-723, rtl/ibex_decoder.sv:1405-1416
- Edge: no
- Status: ACTIVE

### F-ISA-031: fence.i ignores rs1/rd/imm; other MISC-MEM funct3 illegal
- What: fence.i with nonzero rs1, rd or imm[11:0] executes normally (reserved fields ignored); MISC-MEM
  funct3 010..111 raise illegal-instruction.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval on rvfi_rd_wdata for the illegal
  funct3; instr_addr_o restart at pc + 4 and rvfi_trap = 0 for the fence.i variants
- Config: none
- Source: spec: zifencei.adoc (norm:fence_i_rsv) | RTL-defined: rtl/ibex_decoder.sv:705-727
- Edge: yes, of F-ISA-030
- Status: ACTIVE

### F-ISA-032: ecall
- What: SYSTEM funct12 0x000, rs1=rd=0: synchronous exception; mepc = PC of the ecall; no other state
  change; not counted in minstret.
- Observable at: rvfi_trap = 1; rvfi_pc_wdata = trap vector (instr_addr_o = mtvec base); csrr
  read-back of mcause / mepc / mtval on rvfi_rd_wdata
- Config: privilege mode (mstatus.MPP after mret / U-mode entry), mtvec
- Source: spec: rv32.adoc "Environment Call and Breakpoints"; tools/specs/riscv-isa-manual/src/priv/machine.adoc
  "Environment Call and Breakpoint" (norm:ecall_ebreak_epc_value, norm:ecall_ebreak_no_minstret_inc) |
  RTL-defined: rtl/ibex_decoder.sv:734-736, rtl/ibex_controller.sv:870-873, rtl/ibex_id_stage.sv:1218-1220
- Edge: no
- Status: ACTIVE

### F-ISA-033: ecall cause depends on privilege mode
- What: Folded into F-ISA-032 (bin CG-ISA-009.cr_op_priv_outcome.ecall_m_exc): ecall cause 11 in M-mode, 8
  in U-mode, mtval 0 - the parent's Config (privilege) at its other value.
- Observable at: see F-ISA-032
- Config: see F-ISA-032
- Source: spec: machine.adoc "Environment Call and Breakpoint" (norm:ecall_op2) |
  RTL-defined: rtl/ibex_controller.sv:870-873, rtl/ibex_pkg.sv:374-377
- Edge: yes, of F-ISA-032
- Status: FOLDED into F-ISA-032 (bin CG-ISA-009.cr_op_priv_outcome.ecall_m_exc)
- Notes: the U-mode iterations need the PMP prologue (X-2): with every PMP entry OFF (reset) an unmatched
  U access faults (rtl/ibex_pmp.sv:136-139).

### F-ISA-034: ebreak (and c.ebreak)
- What: SYSTEM funct12 0x001: breakpoint exception (mcause=3), mepc = PC of ebreak, mtval=0, not
  counted in minstret. c.ebreak expands to the same encoding.
- Observable at: rvfi_trap = 1 (rvfi_insn = 0x00100073 / 0x9002); csrr read-back of mcause (3) /
  mtval (0) / mepc on rvfi_rd_wdata
- Config: dcsr.ebreakm / dcsr.ebreaku = 0 (with either set the ebreak enters debug mode: F-DBG-017,
  the canonical entry behind F-ISA-035)
- Source: spec: rv32.adoc "Environment Call and Breakpoints"; machine.adoc "Environment Call and Breakpoint"
  (norm:ebreak_op2), "Machine Trap Value (mtval) Register" (ebreak mtval zero or address) |
  RTL-defined: rtl/ibex_decoder.sv:738-740, rtl/ibex_controller.sv:874-899, rtl/ibex_compressed_decoder.sv:603-605
- Edge: no
- Status: ACTIVE
- Notes: Ibex writes mtval=0 for ebreak (csr_mtval_o default) which the spec permits; rtl-arch R10 (dv/auto_dv/evidence/gen_t102_rtl_facts.md): the pc-writing breakpoint arm is CHERIoT-only (rtl/ibex_controller.sv:894-897), c.ebreak expands to ebreak 0x00100073 and takes the same arm; the shim models mtval = 0 for cause 3 (convention, not a bug).

### F-ISA-035: ebreak enters debug mode when dcsr.ebreakm/ebreaku set
- What: Alias of F-DBG-017: ISA-decode perspective of ebreak entering debug mode; see the canonical
  entry.
- Observable at: see F-DBG-017 (canonical)
- Config: see F-DBG-017
- Source: RTL-defined: rtl/ibex_controller.sv:481-483, rtl/ibex_controller.sv:875-883,
  rtl/ibex_controller.sv:785-814 (debug spec owned by the debug area)
- Edge: yes, of F-ISA-034
- Status: ALIAS of F-DBG-017

### F-ISA-036: mret decode
- What: SYSTEM funct12 0x302, rs1=rd=0: pipeline flush, pc = mepc, privilege/MIE stack pop
  (CSR semantics owned by the CSR/trap area).
- Observable at: the NEXT record's rvfi_pc_rdata = mepc (rvfi_pc_wdata of the mret record is the next
  sequential fetch address pc + 4, never the target: PC_ERET pc_set happens in FLUSH one cycle after the
  record's capture, X-1 / C-1); instr_addr_o = mepc when the target is not cached; rvfi_mode of the next
  retirement = MPP (also for an mret executed in debug mode, rtl/ibex_cs_registers.sv:953-954)
- Config: mepc, mstatus.MPP/MPIE, privilege mode
- Source: spec: machine.adoc "Trap-Return Instructions" (norm:xret_op) | RTL-defined:
  rtl/ibex_decoder.sv:742-743, rtl/ibex_controller.sv:954-960
- Edge: no
- Status: ACTIVE

### F-ISA-037: mret in U-mode is illegal
- What: Alias of F-PRV-010: ISA-decode perspective of mret in U-mode; see the canonical entry.
- Observable at: see F-PRV-010 (canonical)
- Config: see F-PRV-010
- Source: spec: machine.adoc "Trap-Return Instructions" (norm:xret_in_lower_mode) |
  RTL-defined: rtl/ibex_id_stage.sv:606-611
- Edge: yes, of F-ISA-036
- Status: ALIAS of F-PRV-010

### F-ISA-038: dret decode
- What: SYSTEM funct12 0x7b2, rs1=rd=0: in debug mode, pc = dpc, leave debug mode, privilege = dcsr.prv.
- Observable at: rvfi_ext_debug_mode falls; instr_addr_o = dpc; rvfi_mode of the next retirement =
  dcsr.prv
- Config: debug mode, dpc, dcsr.prv
- Source: RTL-defined: rtl/ibex_decoder.sv:745-746, rtl/ibex_controller.sv:961-965 (debug spec:
  tools/specs/riscv-debug-spec, owned by the debug area)
- Edge: no
- Status: ACTIVE

### F-ISA-039: dret outside debug mode is illegal
- What: Alias of F-DBG-032: ISA-decode perspective of dret outside debug mode; see the canonical
  entry.
- Observable at: see F-DBG-032 (canonical)
- Config: see F-DBG-032
- Source: RTL-defined: rtl/ibex_id_stage.sv:603-604, rtl/ibex_id_stage.sv:610-611
- Edge: yes, of F-ISA-038
- Status: ALIAS of F-DBG-032

### F-ISA-040: wfi decode
- What: SYSTEM funct12 0x105, rs1=rd=0: pipeline flush and controller enters WAIT_SLEEP/SLEEP until an
  interrupt or debug request wakes the core (sleep semantics owned by the interrupt area).
- Observable at: core_busy_o low while asleep (core_sleep_o exists only at ibex_top, not on the
  ibex_core boundary); instr_req_o idle during sleep; RVFI (wfi retires with rvfi_trap = 0)
- Config: mstatus.TW, privilege mode, mie
- Source: spec: machine.adoc "Wait for Interrupt" (norm:wfi_op, norm:wfi_resume_reason) |
  RTL-defined: rtl/ibex_decoder.sv:748-749, rtl/ibex_controller.sv:287, rtl/ibex_controller.sv:966-968
- Edge: no
- Status: ACTIVE
- Notes: irq_enabled = mstatus.MIE | (priv_mode == U) (rtl/ibex_controller.sv:490): in U-mode an enabled
  interrupt wakes AND is taken regardless of MIE; only an M-mode wfi with MIE = 0 resumes at the next
  instruction (X-9). The sleep is visible as core_busy_o == IbexMuBiOff only while no fetch beat is
  outstanding, no invalidation runs and the LSU is idle (X-8).

### F-ISA-041: wfi in U-mode with mstatus.TW=1 is illegal
- What: Alias of F-PRV-016: ISA-decode perspective of wfi in U-mode with mstatus.TW; see the
  canonical entry.
- Observable at: see F-PRV-016 (canonical)
- Config: see F-PRV-016
- Source: spec: machine.adoc "Wait for Interrupt" (norm:wfi_ill_exc) | RTL-defined: rtl/ibex_id_stage.sv:606-608
- Edge: yes, of F-ISA-040
- Status: ALIAS of F-PRV-016

### F-ISA-042: SYSTEM funct3=000 operand and funct12 checks
- What: Alias of F-EXC-013: ISA perspective (SYSTEM funct3 = 000 with rs1 != 0 or rd != 0, or any
  funct12 outside the five legal values, is an illegal instruction; illegal wins over ecall/ebreak),
  see canonical.
- Edge: yes, of F-ISA-032
- Status: ALIAS of F-EXC-013

### F-ISA-043: CSR instruction encodings (Zicsr)
- What: csrrw/csrrs/csrrc (funct3 001/010/011) use rs1; csrrwi/csrrsi/csrrci (101/110/111) use
  zero-extended uimm[4:0] from the rs1 field. Old CSR value zero-extended to rd; CSR address = instr[31:20].
- Observable at: RVFI rvfi_rd_wdata (old CSR value), rvfi_rs1_rdata; csrr read-back of the written
  CSR on rvfi_rd_wdata
- Config: privilege mode (CSR address bits [9:8]), debug mode (dcsr etc.)
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/zicsr.adoc "CSR Instructions" |
  RTL-defined: rtl/ibex_decoder.sv:760-784, rtl/ibex_decoder.sv:1421-1441, rtl/ibex_decoder.sv:167-170
- Edge: no
- Status: ACTIVE

### F-ISA-044: csrrs/csrrc with rs1=x0 and csrrsi/csrrci with uimm=0 do not write
- What: Alias of F-CSR-002: ISA-decode perspective of the csrrs/csrrc rs1 = x0 read-only demotion;
  see the canonical entry.
- Observable at: see F-CSR-002 (canonical)
- Config: see F-CSR-002
- Source: spec: zicsr.adoc "CSR Instructions" (norm:csrrs_csrrc_rs1_x0, norm:csrrsi_csrrci_uimm_zero) |
  RTL-defined: rtl/ibex_decoder.sv:250-259, rtl/ibex_cs_registers.sv:404, rtl/ibex_cs_registers.sv:1011
- Edge: yes, of F-ISA-043
- Status: ALIAS of F-CSR-002

### F-ISA-045: csrrw/csrrwi with rd=x0 still writes; writes to read-only CSRs are illegal
- What: Alias of F-CSR-003: ISA-decode perspective of csrrw rd = x0 writes and read-only-CSR writes;
  see the canonical entry.
- Observable at: see F-CSR-003 (canonical)
- Config: see F-CSR-003
- Source: spec: zicsr.adoc "CSR Instructions" (norm:csrrw_op, table csrsideeffects) |
  RTL-defined: rtl/ibex_cs_registers.sv:402-406, rtl/ibex_cs_registers.sv:1011
- Edge: yes, of F-ISA-043
- Status: ALIAS of F-CSR-003

### F-ISA-046: CSR funct3=100 is illegal
- What: Alias of F-CSR-005: ISA-decode perspective of SYSTEM funct3 = 100; see the canonical entry.
- Observable at: see F-CSR-005 (canonical)
- Config: see F-CSR-005
- Source: RTL-defined: rtl/ibex_decoder.sv:769-774 (csr_illegal), rtl/ibex_decoder.sv:783,
  rtl/ibex_decoder.sv:912-919 (csr_access_o cleared together with rf_we/data_req_o/jump/branch when
  illegal_insn)
- Edge: yes, of F-ISA-043
- Status: ALIAS of F-CSR-005

### F-ISA-047: Illegal-instruction exception reporting
- What: Alias of F-EXC-008: ISA-decode perspective of illegal-instruction reporting; see the
  canonical entry.
- Observable at: see F-EXC-008 (canonical)
- Config: see F-EXC-008
- Source: spec: machine.adoc "Machine Trap Value (mtval) Register" (norm:mtval_instr_bits_list,
  norm:mtval_ill_instr_exc_in_low_bits) | RTL-defined: rtl/ibex_decoder.sv:902-920,
  rtl/ibex_controller.sv:864-869, rtl/ibex_id_stage.sv:610-611, rtl/ibex_id_stage.sv:1218-1220
- Edge: no
- Status: ALIAS of F-EXC-008

### F-ISA-048: Reserved / unimplemented major opcodes are illegal
- What: Opcodes not in {LOAD, MISC-MEM, OP-IMM, AUIPC, STORE, OP, LUI, BRANCH, JALR, JAL, SYSTEM} raise
  illegal-instruction: e.g. LOAD-FP 0x07, STORE-FP 0x27, AMO 0x2f, OP-32 0x3b, OP-IMM-32 0x1b, MADD..,
  custom-0/1/2/3, and the CHERI opcodes 0x5b / 0x7b (dead in non-CHERIoT mode).
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (the 32-bit word) on
  rvfi_rd_wdata; no data_req_o and no instr_addr_o redirect
- Config: none
- Source: spec: rv32.adoc "Base Instruction Formats" (reserved behaviour UNSPECIFIED) |
  RTL-defined: rtl/ibex_decoder.sv:791-793, rtl/ibex_decoder.sv:876-878, rtl/ibex_decoder.sv:881-895,
  rtl/ibex_decoder.sv:897-899
- Edge: no
- Status: ACTIVE

### F-ISA-049: All-ones and all-zero instruction words
- What: 0xFFFFFFFF (opcode 1111111) is illegal; 0x0000 halfword is the defined illegal compressed
  instruction (F-CMP-003); 0x00000000 as a 32-bit fetch is two illegal 0x0000 halfwords.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval on rvfi_rd_wdata (0 for the
  all-zero halfword, 0xFFFFFFFF for the all-ones word); rvfi_insn
- Config: none
- Source: spec: zca.adoc "Defined Illegal Instruction" (norm:Zca_illegal) | RTL-defined:
  rtl/ibex_decoder.sv:897-899, rtl/ibex_compressed_decoder.sv:239
- Edge: yes, of F-ISA-048
- Status: ACTIVE

### F-ISA-050: Illegal instruction while a load/store is outstanding in WB
- What: Alias of F-EXC-016: ISA-decode perspective of an illegal instruction behind an outstanding
  WB access; see the canonical entry.
- Observable at: see F-EXC-016 (canonical)
- Config: see F-EXC-016
- Source: RTL-defined: rtl/ibex_controller.sv:664-679, rtl/ibex_id_stage.sv:985-989 (assertion
  IllegalInsnStallMustBeMemStall), rtl/ibex_controller.sv:299-330
- Edge: yes, of F-ISA-047
- Status: ALIAS of F-EXC-016

### F-ISA-051: Writes to x0 are discarded for every instruction class
- What: any rd=x0 result (ALU, load, csrr, jal link) leaves x0 == 0; subsequent reads of x0 return 0.
- Observable at: RVFI rvfi_rd_addr=0 with rvfi_rd_wdata=0; later rvfi_rs1_rdata
- Config: none
- Source: spec: rv32.adoc "Programmers' Model for Base Integer ISA" (norm:x0eq0) |
  RTL-defined: rtl/ibex_core.sv:2340-2345 (RVFI zeroes wdata for x0)
- Edge: no
- Status: ACTIVE

### F-ISA-052: Instruction-address-misaligned exception is never raised
- What: Alias of F-EXC-067: ISA-decode perspective of instruction-address-misaligned never raised;
  see the canonical entry.
- Observable at: see F-EXC-067 (canonical)
- Config: see F-EXC-067
- Source: spec: zca.adoc (norm:Zca_no_misaligned); rv32.adoc "Base Instruction Formats"
  (norm:taken_cti_misaligned_exc) | RTL-defined: rtl/ibex_controller.sv:561, rtl/ibex_if_stage.sv:288
- Edge: no
- Status: ALIAS of F-EXC-067

---------------------------------------------------------------------------------------------------
## AREA MUL: M extension under RV32MSingleCycle

### F-MUL-001: mul
- What: rd = low 32 bits of rs1*rs2 (sign-agnostic). Computed in one cycle by three 17x17 multipliers
  (al*bl, al*bh, ah*bl); no ID stall.
- Observable at: RVFI rvfi_rd_wdata, rvfi_ext_mcycle
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/m-st-ext.adoc "Multiplication Operations" (norm:mul_op) |
  doc: doc/03_reference/instruction_decode_execute.rst "Multiplier/Divider Block (MULT/DIV)" |
  RTL-defined: rtl/ibex_decoder.sv:653-657, rtl/ibex_multdiv_fast.sv:140-218
- Edge: no
- Status: ACTIVE

### F-MUL-002: mul operand extremes and wrap
- What: 0xFFFFFFFF*0xFFFFFFFF = 1; 0x10000*0x10000 = 0; INT_MIN*-1 = INT_MIN; x*0 = 0; x*1 = x;
  0x7FFFFFFF*2 = 0xFFFFFFFE; result independent of operand sign interpretation.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: m-st-ext.adoc "Multiplication Operations" | RTL-defined: rtl/ibex_multdiv_fast.sv:197-202
- Edge: yes, of F-MUL-001
- Status: ACTIVE

### F-MUL-003: mulh
- What: rd = upper 32 bits of the signed 64-bit product; two cycles (MULL state computes partials, MULH
  state adds ah*bh with sign extension); ID stalls one cycle.
- Observable at: RVFI rvfi_rd_wdata, rvfi_ext_mcycle
- Config: none
- Source: spec: m-st-ext.adoc "Multiplication Operations" (norm:mulh_mulhu_mulhsu_op) |
  doc: pipeline_details.rst "Multiplication" row (0/1 stall) | RTL-defined: rtl/ibex_decoder.sv:658-662,
  rtl/ibex_multdiv_fast.sv:210-236, rtl/ibex_id_stage.sv:910-919
- Edge: no
- Status: ACTIVE

### F-MUL-004: mulh sign combinations and extremes
- What: (+,+): 0x7FFFFFFF*0x7FFFFFFF -> 0x3FFFFFFF; (-,-): INT_MIN*INT_MIN -> 0x40000000; -1*-1 -> 0;
  (-,+): -1*1 -> 0xFFFFFFFF; INT_MIN*1 -> 0xFFFFFFFF; INT_MIN*-1 -> 0; x*0 -> 0.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: m-st-ext.adoc "Multiplication Operations" | RTL-defined: rtl/ibex_multdiv_fast.sv:168-169,
  rtl/ibex_multdiv_fast.sv:185-186, rtl/ibex_multdiv_fast.sv:220-236
- Edge: yes, of F-MUL-003
- Status: ACTIVE

### F-MUL-005: mulhu
- What: rd = upper 32 bits of the unsigned 64-bit product; two cycles.
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_rs1_rdata, rvfi_rs2_rdata)
- Config: none
- Source: spec: m-st-ext.adoc "Multiplication Operations" | RTL-defined: rtl/ibex_decoder.sv:668-672
  (signed_mode 00), rtl/ibex_multdiv_fast.sv:135, rtl/ibex_multdiv_fast.sv:168-169
- Edge: no
- Status: ACTIVE

### F-MUL-006: mulhu extremes
- What: 0xFFFFFFFF*0xFFFFFFFF -> 0xFFFFFFFE; 0x80000000*2 -> 1; 0x80000000*0x80000000 -> 0x40000000;
  0xFFFFFFFF*1 -> 0.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: m-st-ext.adoc "Multiplication Operations" | RTL-defined: rtl/ibex_multdiv_fast.sv:220-236
- Edge: yes, of F-MUL-005
- Status: ACTIVE

### F-MUL-007: mulhsu
- What: rd = upper 32 bits of signed(rs1) * unsigned(rs2); only signed_mode[0] (rs1) is set.
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_rs1_rdata, rvfi_rs2_rdata)
- Config: none
- Source: spec: m-st-ext.adoc "Multiplication Operations" | RTL-defined: rtl/ibex_decoder.sv:663-667
  (signed_mode 01), rtl/ibex_multdiv_fast.sv:168-169
- Edge: no
- Status: ACTIVE

### F-MUL-008: mulhsu asymmetry
- What: mulhsu(-1, 0xFFFFFFFF) -> 0xFFFFFFFF; mulhsu(0xFFFFFFFF as rs2, -1 as rs1) differs from operand
  swap; mulhsu(INT_MIN, 0xFFFFFFFF) -> 0x80000000; mulhsu(1, 0xFFFFFFFF) -> 0; mulhsu(-1, 1) -> 0xFFFFFFFF.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: m-st-ext.adoc "Multiplication Operations" (mulhsu note) | RTL-defined:
  rtl/ibex_multdiv_fast.sv:178-182, rtl/ibex_multdiv_fast.sv:191-195
- Edge: yes, of F-MUL-007
- Status: ACTIVE

### F-MUL-009: mul back-to-back single-cycle throughput
- What: consecutive mul instructions retire every cycle; mul result forwarded to a dependent instruction
  next cycle via the WB forwarding path.
- Observable at: RVFI rvfi_ext_mcycle deltas, rvfi_rs1_rdata of the consumer
- Config: none
- Source: doc: pipeline_details.rst "Multiplication" row | RTL-defined: rtl/ibex_multdiv_fast.sv:203,
  rtl/ibex_multdiv_fast.sv:215-217, rtl/ibex_id_stage.sv:1117-1118
- Edge: yes, of F-MUL-001
- Status: ACTIVE

### F-MUL-010: mulh two-cycle latency and mixed sequences
- What: Folded into F-MUL-003 (bin CG-MUL-002.cr_seq.auto): mulh-class two-cycle latency and
  mulh/mul mixed sequences restart the MULL/MULH FSM each time; results independent of history.
- Observable at: see F-MUL-003
- Config: see F-MUL-003
- Source: RTL-defined: rtl/ibex_multdiv_fast.sv:208-243, rtl/ibex_multdiv_fast.sv:245-253
- Edge: yes, of F-MUL-003
- Status: FOLDED into F-MUL-003 (bin CG-MUL-002.cr_seq.auto)

### F-MUL-011: Multiplier start deferred behind an outstanding WB memory access (no mid-operation hold)
- What: While a load/store is outstanding in WB the multiply cannot start: mult_en_id = instr_executing ?
  mult_en_dec : 0 and instr_executing requires ~outstanding_memory_access (= (outstanding_load_wb |
  outstanding_store_wb) & ~lsu_resp_valid), so the multiplier is enabled first in the response cycle;
  multdiv_ready_id_i (= ready_wb_i) is 1 in that cycle, hence mult_hold with mult_en_i = 1 is
  unreachable and there is no partial result to hold. Observable: record delta from the access record
  = 1 + W (mul) / 2 + W (mulh class), W = the response delay beyond min1; result unchanged.
- Observable at: RVFI rvfi_rd_wdata correct and rvfi_ext_mcycle delta 1 + W / 2 + W after a preceding
  slow load/store (the dbus monitor supplies W)
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:733-734 (mult_en_id gated by instr_executing),
  rtl/ibex_id_stage.sv:1014-1016 (outstanding_memory_access), rtl/ibex_id_stage.sv:1059-1062
  (instr_executing), rtl/ibex_id_stage.sv:976 (multdiv_ready_id = ready_wb), rtl/ibex_wb_stage.sv:185,
  rtl/ibex_multdiv_fast.sv:98, :216, :235 (mult_hold, unreachable while enabled) | fact-check:
  rtl-arch T-053 X-12; gen_multdiv_bound_props.md Section 1
- Edge: yes, of F-MUL-003
- Status: ACTIVE
- Notes: mechanism corrected by rtl-arch T-053 (X-12): the former "result held by mult_hold" statement
  described an unreachable path (hierarchy map H-M1).

### F-MUL-012: div
- What: signed quotient rounded toward zero; long division: IDLE, ABS_A, ABS_B, 31 COMP iterations,
  LAST, CHANGE_SIGN, FINISH = 37 cycles in ID (36 stall cycles) when the divisor is non-zero.
- Observable at: RVFI rvfi_rd_wdata, rvfi_ext_mcycle
- Config: cpuctrlsts.data_ind_timing (see F-MUL-022)
- Source: spec: m-st-ext.adoc "Division Operations" (norm:div_divu_op) | doc: instruction_decode_execute.rst
  "Divider" (37 cycles), pipeline_details.rst "Division/Remainder" row | RTL-defined:
  rtl/ibex_decoder.sv:673-677, rtl/ibex_multdiv_fast.sv:412-526
- Edge: no
- Status: ACTIVE
- Notes: RTL FSM count gives 37 cycles total occupancy; pipeline_details.rst states "37" stall cycles
  under its "X stall = X+1 cycles" convention, i.e. 38 total. One of the two documents is off by one;
  verify in simulation.

### F-MUL-013: divu
- What: unsigned quotient; both operands treated unsigned (signed_mode 00).
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_rs1_rdata, rvfi_rs2_rdata)
- Config: none
- Source: spec: m-st-ext.adoc "Division Operations" | RTL-defined: rtl/ibex_decoder.sv:678-682,
  rtl/ibex_multdiv_fast.sv:406-407
- Edge: no
- Status: ACTIVE

### F-MUL-014: rem
- What: signed remainder; sign of a non-zero remainder equals the sign of the dividend; dividend =
  divisor*quotient + remainder (except overflow).
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_rs1_rdata, rvfi_rs2_rdata)
- Config: none
- Source: spec: m-st-ext.adoc "Division Operations" (norm:rem_remu_op, norm:rem_result_sign) |
  RTL-defined: rtl/ibex_decoder.sv:683-687, rtl/ibex_multdiv_fast.sv:409, rtl/ibex_multdiv_fast.sv:506-507
- Edge: no
- Status: ACTIVE

### F-MUL-015: remu
- What: unsigned remainder.
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_rs1_rdata, rvfi_rs2_rdata)
- Config: none
- Source: spec: m-st-ext.adoc "Division Operations" | RTL-defined: rtl/ibex_decoder.sv:688-692
- Edge: no
- Status: ACTIVE

### F-MUL-016: Division by zero returns all ones with a 2-cycle fast path
- What: div x, 0 -> 0xFFFFFFFF (-1); divu x, 0 -> 0xFFFFFFFF, for every dividend including 0 and INT_MIN.
  With data_ind_timing=0 the FSM goes IDLE -> FINISH directly (2 cycles, 1 stall).
- Observable at: RVFI rvfi_rd_wdata, rvfi_ext_mcycle
- Config: cpuctrlsts.data_ind_timing = 0
- Source: spec: m-st-ext.adoc "Division Operations" table divby0 (norm:div_by_zero) | doc:
  pipeline_details.rst "1 stall cycle if divide by 0" | RTL-defined: rtl/ibex_multdiv_fast.sv:427-437
- Edge: yes, of F-MUL-012
- Status: ACTIVE

### F-MUL-017: Remainder by zero returns the dividend
- What: rem x, 0 -> x; remu x, 0 -> x (including x = INT_MIN, 0, 0xFFFFFFFF); 2-cycle fast path.
- Observable at: RVFI rvfi_rd_wdata
- Config: cpuctrlsts.data_ind_timing = 0
- Source: spec: m-st-ext.adoc "Division Operations" (norm:rem_by_zero) | RTL-defined:
  rtl/ibex_multdiv_fast.sv:438-446
- Edge: yes, of F-MUL-014
- Status: ACTIVE

### F-MUL-018: Signed overflow INT_MIN / -1
- What: div INT_MIN, -1 -> INT_MIN (0x80000000); rem INT_MIN, -1 -> 0. Full 37-cycle path (divisor non-zero).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: m-st-ext.adoc "Division Operations" (norm:signed_div_overflow) | RTL-defined:
  rtl/ibex_multdiv_fast.sv:453-475 (abs), rtl/ibex_multdiv_fast.sv:502-512 (negate quotient)
- Edge: yes, of F-MUL-012
- Status: ACTIVE

### F-MUL-019: div/rem sign combinations
- What: Folded into F-MUL-012 (bin CG-MUL-003.cr_op_sign.auto): div/rem sign quadrants ((-7)/2 = -3
  rem -1 etc.) restate round-toward-zero and remainder-sign-of-dividend from the parents.
- Observable at: see F-MUL-012
- Config: see F-MUL-012
- Source: spec: m-st-ext.adoc "Division Operations" | RTL-defined: rtl/ibex_multdiv_fast.sv:406-409,
  rtl/ibex_multdiv_fast.sv:502-512
- Edge: yes, of F-MUL-012
- Status: FOLDED into F-MUL-012 (bin CG-MUL-003.cr_op_sign.auto)

### F-MUL-020: divu/remu with MSB-set operands
- What: divu 0xFFFFFFFF, 2 -> 0x7FFFFFFF; divu 0x80000000, 0xFFFFFFFF -> 0; remu 0x80000000, 0xFFFFFFFF
  -> 0x80000000; divu 0xFFFFFFFF, 0xFFFFFFFF -> 1.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: m-st-ext.adoc "Division Operations" | RTL-defined: rtl/ibex_multdiv_fast.sv:398-404
- Edge: yes, of F-MUL-013
- Status: ACTIVE

### F-MUL-021: Divide corner values
- What: dividend 0 (quotient 0, remainder 0); divisor 1 (quotient = dividend); divisor == dividend
  (quotient 1, remainder 0); |divisor| > |dividend| (quotient 0, remainder = dividend); divisor -1 with
  non-INT_MIN dividend (negation); dividend INT_MIN with divisor 2, -2, INT_MIN.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: m-st-ext.adoc "Division Operations" | RTL-defined: rtl/ibex_multdiv_fast.sv:477-500
- Edge: yes, of F-MUL-012
- Status: ACTIVE

### F-MUL-022: data_ind_timing=1 forces full-latency divide-by-zero
- What: With cpuctrlsts.data_ind_timing = 1 a division by zero runs the complete 37-cycle sequence
  (MD_IDLE -> MD_ABS_A instead of the MD_FINISH shortcut). The result is still all ones for div/divu
  and the dividend for rem/remu: the long division by zero naturally yields quotient all ones and
  remainder |dividend|; for div/divu div_by_zero_q masks div_change_sign so the final negation is
  skipped even when the operand signs differ; for rem/remu no mask exists (rem_change_sign =
  div_sign_a) and the normal sign change restores the dividend's sign, which is the required result.
- Observable at: rvfi_ext_mcycle (constant 37-cycle occupancy), rvfi_rd_wdata
- Config: cpuctrlsts.data_ind_timing = 1
- Source: RTL-defined: rtl/ibex_multdiv_fast.sv:427-446 (state choice and div_by_zero_d),
  rtl/ibex_multdiv_fast.sv:408-409 (div_change_sign masked by ~div_by_zero_q; rem_change_sign not),
  rtl/ibex_multdiv_fast.sv:502-508 (MD_CHANGE_SIGN), rtl/ibex_cs_registers.sv:1905
- Edge: yes, of F-MUL-012
- Status: ACTIVE
- Notes: Mechanism text corrected per Critic C-05; edge re-pointed at the base feature (C-13).

### F-MUL-023: Interrupt, NMI or debug request during a multi-cycle instruction is deferred until it retires
- What: The controller waits for the instruction in ID to finish (!stall && !id_wb_pending,
  rtl/ibex_controller.sv:698-721) before IRQ_TAKEN / DBG_TAKEN_IF, so an enabled interrupt, irq_nm_i
  or debug_req_i arriving during a divide (up to 37 cycles of added latency), a mulh-class op or a
  two-cycle Zbb/Zbt op (rol/ror/rori/cmov/cmix/fsl/fsr/fsri/crc32*, F-BIT-012) is deferred: the
  instruction retires with its full result (rs3 read in the second cycle for the ternary forms), then
  the trap or debug entry follows with mepc / dpc = the next PC. Canonical for the cluster F-IRQ-019 /
  F-BIT-036 (Critic M-10).
- Observable at: RVFI: the multi-cycle op retires (rvfi_trap = 0, rvfi_rd_wdata correct, rvfi_rs3_*
  populated for ternary ops) before the handler entry (rvfi_intr = 1) or before rvfi_ext_debug_mode
  rises; csrr read-back of mepc / dpc on rvfi_rd_wdata = the next PC; irq_pending_o high across the op.
- Config: mie / mstatus.MIE, dcsr.step, debug_req_i; none for the op itself.
- Source: RTL-defined: rtl/ibex_controller.sv:698-721; rtl/ibex_id_stage.sv:943-947 (stall_alu,
  MULTI_CYCLE), 954-966 (exit of MULTI_CYCLE), 983
- Edge: yes, of F-MUL-012
- Status: ACTIVE
- Notes: Canonical entry; aliases F-IRQ-019 (IRQ) and F-BIT-036 (bitmanip). The writeback-busy
  coincidence is F-BIT-041.

### F-MUL-024: Divider start deferred behind an outstanding WB memory access (no FINISH hold)
- What: div_en_id = instr_executing ? div_en_dec : 0, so the divider FSM leaves MD_IDLE first in the cycle
  the outstanding load/store response arrives; MD_FINISH (valid_o) follows exactly 36 cycles later (1 cycle
  for divide by zero with data_ind_timing = 0) with multdiv_ready_id_i = 1, so div_hold in MD_FINISH is
  unreachable and the result is never held. Observable: record delta from the access record = 37 + W
  (2 + W for the fast path), W = the response delay beyond min1; result unchanged.
- Observable at: RVFI rvfi_rd_wdata correct and rvfi_ext_mcycle delta 37 + W / 2 + W when a slow store or
  load precedes the divide (the dbus monitor supplies W)
- Config: cpuctrlsts.data_ind_timing (fast path only when 0)
- Source: RTL-defined: rtl/ibex_id_stage.sv:733-734, :1014-1016, :1059-1062, :976; rtl/ibex_multdiv_fast.sv:99,
  :514-520 (div_hold, unreachable while enabled) | fact-check: rtl-arch T-053 X-12;
  gen_multdiv_bound_props.md MD-1..MD-3
- Edge: yes, of F-MUL-012
- Status: ACTIVE
- Notes: mechanism corrected by rtl-arch T-053 (X-12): the former "held in FINISH" statement described an
  unreachable path (hierarchy map H-D1).

### F-MUL-025: Back-to-back multdiv and dependency forwarding
- What: div followed by a dependent add (forwarding from WB), div followed by mul, mul followed by div,
  divide whose rs1/rs2 was written by the immediately preceding load (stall_ld_hz) all produce correct
  results; the divider always restarts from MD_IDLE.
- Observable at: RVFI rvfi_rd_wdata, rvfi_rs1_rdata
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:1109-1120, rtl/ibex_multdiv_fast.sv:101-115
- Edge: yes, of F-MUL-012
- Status: ACTIVE

### F-MUL-026: M-extension decode: funct7 0000001 with any funct3, rd=x0 forms
- What: All eight funct3 values under funct7 0000001 are legal (mul, mulh, mulhsu, mulhu, div, divu, rem,
  remu); with rd=x0 they still execute (and stall) but write nothing.
- Observable at: RVFI, rvfi_ext_mcycle
- Config: none
- Source: spec: m-st-ext.adoc | RTL-defined: rtl/ibex_decoder.sv:653-692, rtl/ibex_decoder.sv:1355-1386
- Edge: yes, of F-MUL-001
- Status: ACTIVE

### F-MUL-027: c.mul reaches the multiplier
- What: Alias of F-CMP-038: multiplier-side perspective of c.mul (the compressed area owns the
  expansion); see the canonical entry.
- Observable at: see F-CMP-038 (canonical)
- Config: see F-CMP-038
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/zcb.adoc "c.mul" | RTL-defined:
  rtl/ibex_compressed_decoder.sv:462-471
- Edge: yes, of F-MUL-001
- Status: ALIAS of F-CMP-038

### F-MUL-028: Divider / multiplier bound properties and the unreachable hold arc (assertion feature)
- What: The divider state register updates only under div_en_internal = div_en_i & ~div_hold; div_en_i
  (= div_en_id = instr_executing ? div_en_dec : 0) is 1 only while the divide is the executing
  instruction in ID and cannot drop mid-operation (a WB access outstanding at the start defers the
  start instead, X-12), so the freeze-arc property (div_en_i == 0 && md_state_q != MD_IDLE |=>
  $stable(md_state_q)) is structurally implied by the flop enable and is kept as a COVER only. The
  assertion content of the feature is rtl-arch's bound set (gen_multdiv_bound_props.md): MD-1 a
  non-fast-path divide start reaches MD_FINISH with valid_o exactly 36 cycles later (valid_o low in
  between); MD-2 divide by zero with data_ind_timing = 0 reaches MD_FINISH in the next cycle; MD-2b
  under data_ind_timing = 1 it takes the full path; MD-3 MD_FINISH implies multdiv_ready_id_i (div_hold
  never engages while enabled: the X-12 argument, expected never to fire); MD-4 the state arcs; MD-5 MUL
  valid in its first cycle, MULH class in the second; covers MD-C1..C3 (paths seen) and MD-C4 (hold
  attempt, expected 0). A cover hit on MD-C4 or the freeze arc is a reachability finding, an MD-1..MD-5
  failure is a bug.
- Observable at: rvfi_rd_wdata / rvfi_ext_mcycle of every divide issued under the stimuli that could
  disturb it (result correct, 37 + W / 2 + W latency, exactly one retirement); the bounds themselves
  have no boundary observable - probe candidate P8 (probe register entry needed): bind into
  u_dut.u_ibex_core.ex_block_i.gen_multdiv_fast.multdiv_i on md_state_q, div_en_i, mult_en_i,
  operator_i, equal_to_zero_i, data_ind_timing_i, multdiv_ready_id_i, valid_o, div_counter_q,
  mult_state_q (assert + cover, coverage-only, no checker depends on it)
- Config: cpuctrlsts.data_ind_timing (both values); PMP / data_err_i injection / irq_* / debug_req_i
  / instr_err_i as the disturbing stimuli
- Source: RTL-defined: rtl/ibex_multdiv_fast.sv:99 (div_en_internal),
  rtl/ibex_multdiv_fast.sv:101-115 (state flop enabled by div_en_internal only),
  rtl/ibex_multdiv_fast.sv:412-526 (FSM), rtl/ibex_id_stage.sv:734 (div_en_id = instr_executing ?
  div_en_dec : 0), rtl/ibex_id_stage.sv:1033-1036 (instr_kill), rtl/ibex_id_stage.sv:1059-1062
  (instr_executing) | map: dv/auto_dv/evidence/gen_hierarchy_map.md H-D3 and "Unverified items"
  1
- Edge: yes, of F-MUL-012
- Status: ACTIVE
- Notes: Added for Critic C-09 item 5 (H-D3); rewritten by fix 3 (rtl-arch T-053 X-12 and
  gen_multdiv_bound_props.md): the freeze-arc property is structurally implied by the flop enable and
  the hold arc is unreachable, so the value of the feature is the MD-1..MD-5 bounds (36-cycle divide,
  1-cycle zero fast path with DIT off, 0/1-cycle multiplier), the MD-C4 / freeze-arc reachability covers
  and the check that a divide disturbed by any listed event still retires exactly once with the right
  result and the C-9 delta.

---------------------------------------------------------------------------------------------------
## AREA CMP: compressed instructions (Zca, Zcb, Zcmp)

### F-CMP-001: 16-bit instruction expansion and PC increment
- What: Any halfword with instr[1:0] != 11 is expanded to a 32-bit equivalent in the IF stage; the
  instruction retires with rvfi_insn = 16-bit encoding (zero-extended) and the next PC = pc + 2; 32-bit
  instructions may start at any 2-byte boundary.
- Observable at: RVFI rvfi_insn, rvfi_pc_rdata/rvfi_pc_wdata, instr_req_o/instr_addr_o
- Config: none
- Source: spec: zca.adoc (norm:Zca_align16) | RTL-defined: rtl/ibex_compressed_decoder.sv:213-225,
  rtl/ibex_compressed_decoder.sv:883, rtl/ibex_core.sv:2263-2269, rtl/ibex_id_stage.sv:396
- Edge: no
- Status: ACTIVE

### F-CMP-002: c.addi4spn
- What: addi rd', x2, nzuimm (zero-extended, scaled by 4, range 4..1020).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zca.adoc "Integer Register-Immediate Operations" (norm:c-addi4spn_op) |
  RTL-defined: rtl/ibex_compressed_decoder.sv:229-240
- Edge: no
- Status: ACTIVE

### F-CMP-003: c.addi4spn nzuimm=0 and the all-zero halfword are illegal
- What: instr[12:5]==0 makes the encoding illegal (includes 0x0000); mtval = 16-bit value.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (= zero-extended halfword, 0 for
  0x0000) on rvfi_rd_wdata; rvfi_insn
- Config: none
- Source: spec: zca.adoc (norm:c-addi4spn_rsv, norm:Zca_illegal) | RTL-defined: rtl/ibex_compressed_decoder.sv:239
- Edge: yes, of F-CMP-002
- Status: ACTIVE

### F-CMP-004: c.lw / c.sw
- What: lw rd', uimm(rs1') and sw rs2', uimm(rs1') with zero-extended offset scaled by 4 (0..124),
  registers x8-x15.
- Observable at: data_req_o/data_addr_o, RVFI rvfi_mem_addr / rvfi_mem_rmask / rvfi_mem_wmask
- Config: none
- Source: spec: zca.adoc "Register-Based Loads and Stores" | RTL-defined: rtl/ibex_compressed_decoder.sv:242-246,
  rtl/ibex_compressed_decoder.sv:259-264
- Edge: no
- Status: ACTIVE

### F-CMP-005: c.lwsp / c.swsp
- What: lw rd, uimm(x2) and sw rs2, uimm(x2), offset scaled by 4 (0..252), any rd/rs2.
- Observable at: data_req_o/data_addr_o (= x2 + uimm), RVFI rvfi_mem_addr / rvfi_mem_rmask /
  rvfi_mem_wmask, rvfi_rd_wdata
- Config: none
- Source: spec: zca.adoc "Stack-Pointer-Based Loads and Stores" | RTL-defined:
  rtl/ibex_compressed_decoder.sv:567-572, rtl/ibex_compressed_decoder.sv:847-851
- Edge: no
- Status: ACTIVE

### F-CMP-006: c.lwsp with rd=x0 is illegal
- What: reserved code point traps (mtval = halfword); c.swsp with rs2=x0 is legal (stores zero).
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (halfword) on rvfi_rd_wdata for
  c.lwsp x0, no data_req_o; c.swsp x0: rvfi_trap = 0 and data_wdata_o = 0
- Config: none
- Source: spec: zca.adoc (norm:c-lwsp_rsv) | RTL-defined: rtl/ibex_compressed_decoder.sv:571
- Edge: yes, of F-CMP-005
- Status: ACTIVE

### F-CMP-007: Floating-point compressed opcodes are illegal
- What: Q0 funct3 001 (c.fld), 011 (c.flw), 101 (c.fsd), 111 (c.fsw) and Q2 funct3 001 (c.fldsp), 011
  (c.flwsp), 111 (c.fswsp) raise illegal-instruction (no F/D; CHERIoT reuse dead).
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (= zero-extended halfword) on
  rvfi_rd_wdata; no data_req_o
- Config: none
- Source: spec: zca.adoc "Zca opcode map" | RTL-defined: rtl/ibex_compressed_decoder.sv:248-257,
  rtl/ibex_compressed_decoder.sv:328-345, rtl/ibex_compressed_decoder.sv:574-584,
  rtl/ibex_compressed_decoder.sv:853-870
- Edge: yes, of F-CMP-001
- Status: ACTIVE

### F-CMP-008: c.addi and c.nop
- What: addi rd, rd, nzimm (6-bit sign-extended); rd=x0 encodes c.nop.
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_insn = the 16-bit encoding)
- Config: none
- Source: spec: zca.adoc (norm:c-addi_op, norm:c-nop_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:356-368
- Edge: no
- Status: ACTIVE

### F-CMP-009: c.addi/c.nop HINT code points execute without state change
- What: c.addi rd!=0, imm=0 and c.nop with imm!=0 are HINTs: legal, no register change, PC advances.
- Observable at: RVFI (no rd write or rd written with its own value), minstret increments
- Config: none
- Source: spec: zca.adoc "HINT Instructions" (norm:c-addi_hint, norm:c-nop_hint) |
  RTL-defined: rtl/ibex_compressed_decoder.sv:364-367
- Edge: yes, of F-CMP-008
- Status: ACTIVE

### F-CMP-010: c.jal / c.j
- What: c.jal -> jal x1, imm (writes pc+2 to x1); c.j -> jal x0, imm; +-2 KiB range.
- Observable at: RVFI rvfi_rd_wdata (=pc+2), rvfi_pc_wdata
- Config: none
- Source: spec: zca.adoc "Control Transfer Instructions" (norm:c-j_op, norm:c-jal_op) |
  RTL-defined: rtl/ibex_compressed_decoder.sv:370-376
- Edge: no
- Status: ACTIVE

### F-CMP-011: c.jal link is pc+2 and target extremes
- What: link = pc+2 (not pc+4); offset +2046 / -2048; c.j to itself.
- Observable at: RVFI rvfi_rd_wdata, rvfi_pc_wdata
- Config: none
- Source: spec: zca.adoc (norm:c-jal_op) | RTL-defined: rtl/ibex_id_stage.sv:396, rtl/ibex_decoder.sv:966-970
- Edge: yes, of F-CMP-010
- Status: ACTIVE

### F-CMP-012: c.li
- What: addi rd, x0, imm (6-bit sign-extended).
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_insn = the 16-bit encoding)
- Config: none
- Source: spec: zca.adoc (norm:c-li_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:378-383
- Edge: no
- Status: ACTIVE

### F-CMP-013: c.li rd=x0 is a HINT
- What: legal, no state change.
- Observable at: RVFI (rvfi_rd_addr = 0, rvfi_rd_wdata = 0, rvfi_trap = 0)
- Config: none
- Source: spec: zca.adoc (norm:c-li_hint) | RTL-defined: rtl/ibex_compressed_decoder.sv:381-382
- Edge: yes, of F-CMP-012
- Status: ACTIVE

### F-CMP-014: c.lui
- What: lui rd, nzimm (imm[17:12] sign-extended into bits 31:17); rd != x0, x2.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zca.adoc (norm:c-lui_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:385-388
- Edge: no
- Status: ACTIVE

### F-CMP-015: c.lui imm=0 illegal, rd=x0 HINT
- What: {instr[12], instr[6:2]}==0 raises illegal-instruction; rd=x0 with imm!=0 executes as lui x0 (HINT).
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (halfword) on rvfi_rd_wdata for
  imm = 0; rvfi_trap = 0 with rvfi_rd_addr = 0 for the rd = x0 HINT
- Config: none
- Source: spec: zca.adoc (norm:c-lui_rsv, norm:c-lui_hint) | RTL-defined: rtl/ibex_compressed_decoder.sv:401
- Edge: yes, of F-CMP-014
- Status: ACTIVE

### F-CMP-016: c.addi16sp
- What: rd field = x2 selects addi x2, x2, nzimm scaled by 16 (range -512..496).
- Observable at: RVFI rvfi_rd_wdata (x2)
- Config: none
- Source: spec: zca.adoc (norm:c-addi16sp_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:395-399
- Edge: no
- Status: ACTIVE

### F-CMP-017: c.addi16sp nzimm=0 illegal; extremes
- What: nzimm=0 traps (shared check with c.lui); nzimm=-512 and +496 boundaries; sp wrap around 0.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (halfword) on rvfi_rd_wdata for
  nzimm = 0; rvfi_rd_wdata (x2) for the extremes and the wrap
- Config: none
- Source: spec: zca.adoc (norm:c-addi16sp_rsv) | RTL-defined: rtl/ibex_compressed_decoder.sv:401
- Edge: yes, of F-CMP-016
- Status: ACTIVE

### F-CMP-018: c.srli / c.srai
- What: srli/srai rd', rd', shamt (shamt = instr[6:2], 1..31).
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_insn = the 16-bit encoding)
- Config: none
- Source: spec: zca.adoc (norm:c-srli_op, norm:c-srai_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:406-421
- Edge: no
- Status: ACTIVE

### F-CMP-019: c.srli/c.srai shamt[5]=1 illegal, shamt=0 HINT
- What: instr[12]=1 (RV64 shamt bit / custom space) raises illegal-instruction; shamt=0 executes as a
  shift by 0 (no change).
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (halfword) on rvfi_rd_wdata for
  instr[12] = 1; rvfi_rd_wdata == rvfi_rs1_rdata for shamt = 0
- Config: none
- Source: spec: zca.adoc (norm:c-srli_shamt5, norm:c-srli_hint) | RTL-defined: rtl/ibex_compressed_decoder.sv:420
- Edge: yes, of F-CMP-018
- Status: ACTIVE

### F-CMP-020: c.andi
- What: andi rd', rd', imm (6-bit sign-extended).
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_insn = the 16-bit encoding)
- Config: none
- Source: spec: zca.adoc (norm:c-andi_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:423-427
- Edge: no
- Status: ACTIVE

### F-CMP-021: c.sub / c.xor / c.or / c.and
- What: CA-format register ops on x8-x15.
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_insn = the 16-bit encoding)
- Config: none
- Source: spec: zca.adoc "Integer Register-Register Operations" | RTL-defined:
  rtl/ibex_compressed_decoder.sv:431-453
- Edge: no
- Status: ACTIVE

### F-CMP-022: c.subw / c.addw are illegal on RV32
- What: {instr[12], instr[6:5]} = 100 / 101 raise illegal-instruction.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (= zero-extended halfword) on
  rvfi_rd_wdata
- Config: none
- Source: spec: zca.adoc (c.addw/c.subw XLEN=64-only) | RTL-defined: rtl/ibex_compressed_decoder.sv:455-460
- Edge: yes, of F-CMP-021
- Status: ACTIVE

### F-CMP-023: c.beqz / c.bnez
- What: beq/bne rs1', x0, imm; +-256 B range.
- Observable at: RVFI rvfi_pc_wdata
- Config: none
- Source: spec: zca.adoc (norm:c-beqz_op, norm:c-bnez_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:533-539
- Edge: no
- Status: ACTIVE

### F-CMP-024: c.slli
- What: slli rd, rd, shamt (shamt = instr[6:2]).
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_insn = the 16-bit encoding)
- Config: none
- Source: spec: zca.adoc (norm:c-slli_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:554-565
- Edge: no
- Status: ACTIVE

### F-CMP-025: c.slli shamt[5]=1 illegal; shamt=0 or rd=x0 HINT
- What: instr[12]=1 traps; shamt=0 / rd=x0 execute as no-ops.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (halfword) on rvfi_rd_wdata for
  instr[12] = 1; rvfi_trap = 0 with rd unchanged / rvfi_rd_addr = 0 for the HINTs
- Config: none
- Source: spec: zca.adoc (norm:c-slli_shamt5, norm:c-slli_hint) | RTL-defined: rtl/ibex_compressed_decoder.sv:564
- Edge: yes, of F-CMP-024
- Status: ACTIVE

### F-CMP-026: c.mv
- What: add rd, x0, rs2 (rs2 != x0).
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata = rvfi_rs2_rdata, rvfi_insn = the 16-bit
  encoding)
- Config: none
- Source: spec: zca.adoc (norm:c-mv_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:588-591
- Edge: no
- Status: ACTIVE

### F-CMP-027: c.mv rd=x0 HINT
- What: legal, no state change.
- Observable at: RVFI (rvfi_rd_addr = 0, rvfi_rd_wdata = 0, rvfi_trap = 0)
- Config: none
- Source: spec: zca.adoc (norm:c-mv_hint) | RTL-defined: rtl/ibex_compressed_decoder.sv:591
- Edge: yes, of F-CMP-026
- Status: ACTIVE

### F-CMP-028: c.jr
- What: jalr x0, rs1, 0 (rs2 field = 0, instr[12]=0).
- Observable at: RVFI rvfi_pc_wdata, instr_addr_o = target (bit 0 cleared)
- Config: none
- Source: spec: zca.adoc (norm:c-jr_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:592-596
- Edge: no
- Status: ACTIVE

### F-CMP-029: c.jr rs1=x0 is illegal
- What: encoding 0x8002 raises illegal-instruction.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (0x8002) on rvfi_rd_wdata; no
  instr_addr_o redirect to address 0
- Config: none
- Source: spec: zca.adoc (norm:c-jr_rsv) | RTL-defined: rtl/ibex_compressed_decoder.sv:595
- Edge: yes, of F-CMP-028
- Status: ACTIVE

### F-CMP-030: c.add
- What: add rd, rd, rs2 (rs2 != x0, instr[12]=1).
- Observable at: RVFI (rvfi_rd_addr, rvfi_rd_wdata, rvfi_insn = the 16-bit encoding)
- Config: none
- Source: spec: zca.adoc (norm:c-add_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:598-601
- Edge: no
- Status: ACTIVE

### F-CMP-031: c.add rd=x0 HINT (including c.ntl.* encodings)
- What: rd=x0, rs2 != 0 execute as no-ops (rs2 = x2..x5 are the NTL hints).
- Observable at: RVFI (rvfi_rd_addr = 0, rvfi_rd_wdata = 0, rvfi_trap = 0)
- Config: none
- Source: spec: zca.adoc "HINT Instructions" (norm:c-add_hint) | RTL-defined: rtl/ibex_compressed_decoder.sv:601
- Edge: yes, of F-CMP-030
- Status: ACTIVE

### F-CMP-032: c.jalr
- What: jalr x1, rs1, 0 with link = pc+2 (rs1 != 0, instr[12]=1, rs2 field 0).
- Observable at: RVFI rvfi_rd_wdata (x1 = pc+2), rvfi_pc_wdata
- Config: none
- Source: spec: zca.adoc (norm:c-jalr_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:606-609
- Edge: no
- Status: ACTIVE

### F-CMP-033: c.ebreak
- What: Alias of F-ISA-034: compressed-encoding perspective of ebreak (c.ebreak expands to
  0x00100073); see the canonical entry.
- Observable at: see F-ISA-034 (canonical)
- Config: see F-ISA-034
- Source: spec: zca.adoc "Breakpoint Instruction" (norm:c-ebreak_op) | RTL-defined:
  rtl/ibex_compressed_decoder.sv:603-605
- Edge: yes, of F-ISA-034
- Status: ALIAS of F-ISA-034

### F-CMP-034: Zcb loads and stores (c.lbu, c.lhu, c.lh, c.sb, c.sh)
- What: byte/halfword forms with 2-bit (byte) or 1-bit (halfword, scaled by 2) zero-extended offsets;
  c.lh sign-extends, c.lbu/c.lhu zero-extend; registers x8-x15.
- Observable at: data_be_o/data_addr_o, RVFI rvfi_mem_addr / rvfi_mem_rmask / rvfi_mem_wmask,
  rvfi_rd_wdata
- Config: none
- Source: spec: zcb.adoc "c.lbu", "c.lhu", "c.lh", "c.sb", "c.sh" | RTL-defined:
  rtl/ibex_compressed_decoder.sv:266-321, rtl/ibex_load_store_unit.sv:403-405
- Edge: no
- Status: ACTIVE
- Notes: only a halfword at addr[1:0] = 3 splits into two bus accesses; a halfword at addr[1:0] = 1 is
  misaligned but one word access with be 0110 (rtl/ibex_load_store_unit.sv:403-405; X-23).

### F-CMP-035: Zcb load/store reserved code points
- What: c.sh encoding with instr[6]=1 is illegal; Q0 funct3 100 with instr[12:10] = 1xx is illegal.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (= zero-extended halfword) on
  rvfi_rd_wdata; no data_req_o
- Config: none
- Source: spec: zcb.adoc "c.sh" encoding (bit 6 = 0) | RTL-defined: rtl/ibex_compressed_decoder.sv:308-320
- Edge: yes, of F-CMP-034
- Status: ACTIVE

### F-CMP-036: Zcb ALU forms (c.zext.b, c.sext.b, c.zext.h, c.sext.h, c.not)
- What: expand to andi rsd',rsd',0xff / sext.b / pack rsd',rsd',x0 (zext.h) / sext.h / xori rsd',rsd',-1.
  sext.b/sext.h/zext.h rely on Zbb being enabled (it is under RV32BOTEarlGrey).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zcb.adoc "c.zext.b", "c.sext.b", "c.zext.h", "c.sext.h", "c.not" | RTL-defined:
  rtl/ibex_compressed_decoder.sv:473-519
- Edge: no
- Status: ACTIVE

### F-CMP-037: c.zext.w and unused Zcb funct codes are illegal
- What: instr[4:2] = 100 (c.zext.w, RV64 only), 110, 111 under funct 100111 raise illegal-instruction.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (= zero-extended halfword) on
  rvfi_rd_wdata
- Config: none
- Source: spec: zcb.adoc "c.zext.w" (RV64 only) | RTL-defined: rtl/ibex_compressed_decoder.sv:500-503,
  rtl/ibex_compressed_decoder.sv:511-513
- Edge: yes, of F-CMP-036
- Status: ACTIVE

### F-CMP-038: c.mul
- What: c.mul rsd', rs2' (CA format: instr[15:10] = 100111, instr[6:5] = 10, op = 10) expands to mul
  rsd', rsd', rs2' (rtl/ibex_compressed_decoder.sv:462-471: instr_o = {7'b0000001, rs2', rsd',
  3'b000, rsd', OPCODE_OP}); the expanded instruction executes in the single-cycle multiplier and
  writes rsd' (x8..x15). Without Zcb in RV32ZC the encoding is illegal (:468-470). Multiplier-side
  alias: F-MUL-027.
- Observable at: RVFI (rvfi_rd_addr in x8..x15, rvfi_rd_wdata, rvfi_insn = the 16-bit encoding)
- Config: none
- Source: spec: zcb.adoc "c.mul" | RTL-defined: rtl/ibex_compressed_decoder.sv:462-471
- Edge: no
- Status: ACTIVE

### F-CMP-039: cm.push
- What: Expanded into a micro-op sequence: for each register in rlist from highest (x27) to ra, a
  `sw reg, -4*k(sp)` (k = 1..N), then `addi sp, sp, -stack_adj`. Each micro-op retires separately;
  the 16-bit instruction stays in IF until the last micro-op is accepted.
- Observable at: data_req_o/data_addr_o/data_wdata_o (N stores at sp-4, sp-8, ...), RVFI per
  micro-op (rvfi_insn = expanded 32-bit word, rvfi_ext_expanded_insn_valid = 1,
  rvfi_ext_expanded_insn = the 16-bit encoding, rvfi_ext_expanded_insn_last on the addi),
  rvfi_rd_wdata (x2) on the last micro-op
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc "cm.push" (norm:cm-push_op), "Software view
  of the push sequence" | doc: pipeline_details.rst "Zcmp Push/Pop" row | RTL-defined:
  rtl/ibex_compressed_decoder.sv:624-684, rtl/ibex_compressed_decoder.sv:81-97,
  rtl/ibex_compressed_decoder.sv:110-127, rtl/ibex_core.sv:2271-2282
- Edge: no
- Status: ACTIVE

### F-CMP-040: cm.push with rlist=4 ({ra})
- What: minimal sequence: sw x1,-4(sp); addi sp,sp,-(16+16*spimm). Two micro-ops.
- Observable at: data_req_o/data_addr_o (one store at sp-4), RVFI (2 entries,
  rvfi_ext_expanded_insn_last on the second)
- Config: none
- Source: spec: zcmp.adoc "cm.push" (rlist 4) | RTL-defined: rtl/ibex_compressed_decoder.sv:638-643
- Edge: yes, of F-CMP-039
- Status: ACTIVE

### F-CMP-041: cm.push with rlist=15 ({ra, s0-s11})
- What: 13 stores: x27,x26,x25,x24,x23,x22,x21,x20,x19,x18,x9,x8,x1 at -4..-52(sp), then addi sp,
  -(64+16*spimm); internal rlist initialised to 16 to reach x27.
- Observable at: data_req_o/data_addr_o (13 stores), RVFI (14 entries)
- Config: none
- Source: spec: zcmp.adoc "cm.push {ra, s0-s11},-112" example | RTL-defined:
  rtl/ibex_compressed_decoder.sv:167-176, rtl/ibex_compressed_decoder.sv:68-79
- Edge: yes, of F-CMP-039
- Status: ACTIVE

### F-CMP-042: cm.push register mapping for rlist 5..14
- What: Folded into F-CMP-039 (bin CG-CMP-006.cr_insn_rlist_spimm.auto): register mapping for rlist
  5..14 (store count rlist-3, top register 3+rlist for 5..6, 11+rlist for 7..14) is the parent's own
  rlist enumeration.
- Observable at: see F-CMP-039
- Config: see F-CMP-039
- Source: spec: zcmp.adoc "cm.push" register list table, "Register list handling" | RTL-defined:
  rtl/ibex_compressed_decoder.sv:68-79
- Edge: yes, of F-CMP-039
- Status: FOLDED into F-CMP-039 (bin CG-CMP-006.cr_insn_rlist_spimm.auto)

### F-CMP-043: cm.push/pop stack_adj for every spimm and rlist group
- What: Folded into F-CMP-039 (bin CG-CMP-006.cr_insn_rlist_spimm.auto): stack_adj = base(rlist) +
  16*spimm (16/32/48/64 + 0..48) for every rlist/spimm combination is the parent's own stack-adjust
  enumeration.
- Observable at: see F-CMP-039
- Config: see F-CMP-039
- Source: spec: zcmp.adoc "Stack pointer adjustment handling", "cm.push" stack_adj table | RTL-defined:
  rtl/ibex_compressed_decoder.sv:44-66
- Edge: yes, of F-CMP-039
- Status: FOLDED into F-CMP-039 (bin CG-CMP-006.cr_insn_rlist_spimm.auto)

### F-CMP-044: cm.push/cm.pop/cm.popret/cm.popretz with rlist 0..3 are illegal
- What: reserved (future EABI) rlist values raise illegal-instruction on the first micro-op; mtval = the
  16-bit encoding; FSM stays idle. RVFI shows rvfi_ext_expanded_insn_valid=1 with rvfi_trap=1.
- Observable at: rvfi_trap (with rvfi_ext_expanded_insn_valid = 1) + csrr read-back of mcause (2) /
  mtval (= zero-extended halfword) on rvfi_rd_wdata; no data_req_o
- Config: none
- Source: spec: zcmp.adoc "cm.push" note (rlist 0-3 reserved) | RTL-defined:
  rtl/ibex_compressed_decoder.sv:635-637, rtl/ibex_compressed_decoder.sv:703-705
- Edge: yes, of F-CMP-039
- Status: ACTIVE
- Notes: Canonical for the EXC alias F-EXC-015 (M-10 pass; the RVFI expanded tag on the trap record
  is verified against rtl/ibex_compressed_decoder.sv:198-207, 626-640).

### F-CMP-045: cm.pop
- What: loads registers from highest to ra: lw reg, (stack_adj-4*k)(sp) for k=1..N, then addi sp, sp,
  +stack_adj. sp used as base is the pre-adjust value.
- Observable at: data_req_o/data_addr_o (N loads), RVFI per micro-op (rvfi_rd_addr per load, x2 on
  the last)
- Config: none
- Source: spec: zcmp.adoc "cm.pop" (norm:cm-pop_op), "Example RV32I push/pop sequences" |
  RTL-defined: rtl/ibex_compressed_decoder.sv:687-756, rtl/ibex_compressed_decoder.sv:99-108
- Edge: no
- Status: ACTIVE

### F-CMP-046: cm.pop load address and register order for each rlist/spimm
- What: Folded into F-CMP-045 (bin CG-CMP-006.cp_order_ok.yes): cm.pop load addresses sp + stack_adj
  - 4k, highest register first, worked for rlist 8/spimm 1 and rlist 15/spimm 3.
- Observable at: see F-CMP-045
- Config: see F-CMP-045
- Source: spec: zcmp.adoc "cm.pop {ra, s0-s3},48", "cm.pop {ra, s0-s4},64" examples | RTL-defined:
  rtl/ibex_compressed_decoder.sv:696-702, rtl/ibex_compressed_decoder.sv:59-66
- Edge: yes, of F-CMP-045
- Status: FOLDED into F-CMP-045 (bin CG-CMP-006.cp_order_ok.yes)

### F-CMP-047: cm.popret
- What: cm.pop sequence followed by `jalr x0, x1, 0` (ret) as the final micro-op; the addi sp micro-op
  is marked INSTR_EXPANDED_COMMIT so it commits atomically with the ret.
- Observable at: data_req_o/data_addr_o, RVFI (last micro-op rvfi_insn = 0x00008067, rvfi_pc_wdata =
  the loaded ra), instr_addr_o = ra after the redirect
- Config: none
- Source: spec: zcmp.adoc "cm.popret" (norm:cm-popret_op) | RTL-defined: rtl/ibex_compressed_decoder.sv:743-748,
  rtl/ibex_compressed_decoder.sv:765-772, rtl/ibex_compressed_decoder.sv:143-151
- Edge: no
- Status: ACTIVE

### F-CMP-048: cm.popretz
- What: cm.pop sequence, then `addi a0, x0, 0`, then `ret`; the sp adjust and li a0 are COMMIT micro-ops.
- Observable at: RVFI (rvfi_rd_addr = 10, rvfi_rd_wdata = 0 on the li micro-op), instr_addr_o = ra
- Config: none
- Source: spec: zcmp.adoc "cm.popretz" (norm:cm-popretz_op) | RTL-defined:
  rtl/ibex_compressed_decoder.sv:747, rtl/ibex_compressed_decoder.sv:757-764, rtl/ibex_compressed_decoder.sv:139-141
- Edge: no
- Status: ACTIVE

### F-CMP-049: cm.popret return target uses the ra just loaded
- What: the ret micro-op reads x1 written by an earlier load micro-op of the same instruction; the value
  always comes from the register file: the intervening addi micro-op cannot execute while the ra load is
  outstanding (instr_executing & ~outstanding_memory_access: deferred start, X-12) and loads are never
  forwarded (rf_rdata_*_fwd uses rf_wdata_fwd_wb, which excludes load data), so by the time the ret
  enters ID the load has left WB; with rlist=4 the load and the ret are separated only by the addi.
- Observable at: RVFI rvfi_rs1_rdata of the ret == rvfi_rd_wdata of the ra load; rvfi_pc_wdata; the addi
  micro-op's record delta 1 + W when the response was late (dbus monitor)
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:1059-1062, rtl/ibex_id_stage.sv:1109-1120 (:1117-1118 no load
  forwarding), rtl/ibex_compressed_decoder.sv:765-772 | fact-check: rtl-arch T-053
  TP-CMP-049 (UNREACHABLE-PRECONDITION corrected)
- Edge: yes, of F-CMP-047
- Status: ACTIVE

### F-CMP-050: cm.mvsa01
- What: two micro-ops: addi r1s', a0, 0 then addi r2s', a1, 0; sreg mapping r=0..7 -> x8,x9,x18..x23.
  First micro-op is COMMIT (atomic with the second).
- Observable at: RVFI (2 entries, rvfi_rd_addr = the mapped registers, rvfi_ext_expanded_insn_last
  on the second)
- Config: none
- Source: spec: zcmp.adoc "cm.mvsa01" (norm:cm-mvsa01_op, norm:cm-mvsa01_sreg) | doc: pipeline_details.rst
  "Zcmp Move" row | RTL-defined: rtl/ibex_compressed_decoder.sv:781-806, rtl/ibex_compressed_decoder.sv:153-158
- Edge: no
- Status: ACTIVE

### F-CMP-051: cm.mvsa01 with r1s' == r2s' is reserved but executed by the RTL
- What: Spec: "For the encoding to be legal r1s' != r2s'". RTL performs both moves to the same register
  (final value = a1) without raising illegal-instruction.
- Observable at: RVFI (no rvfi_trap, rd written twice)
- Config: none
- Source: spec: zcmp.adoc "cm.mvsa01" (norm:cm-mvsa01_res) | RTL-defined: rtl/ibex_compressed_decoder.sv:779-806
  (no r1s'==r2s' check)
- Edge: yes, of F-CMP-050
- Status: ACTIVE
- Notes: RTL/spec disagreement (bug candidate). Spec says reserved, not that an exception is required;
  owner ruling needed on the expected behaviour.

### F-CMP-052: cm.mva01s
- What: two micro-ops: addi a0, r1s', 0 then addi a1, r2s', 0.
- Observable at: RVFI (2 entries, rvfi_rd_addr = 10 then 11, rvfi_rd_wdata = the mapped source
  values)
- Config: none
- Source: spec: zcmp.adoc "cm.mva01s" (norm:cm-mva01s_op) | RTL-defined:
  rtl/ibex_compressed_decoder.sv:809-834, rtl/ibex_compressed_decoder.sv:160-165
- Edge: no
- Status: ACTIVE

### F-CMP-053: cm.mva01s with r1s' == r2s'
- What: Folded into F-CMP-052 (bin CG-CMP-007.cr_insn_equal.auto): cm.mva01s with r1s' == r2s' is
  legal and moves the same source into a0 and a1.
- Observable at: see F-CMP-052
- Config: see F-CMP-052
- Source: spec: zcmp.adoc "cm.mva01s" (no distinctness constraint) | RTL-defined: rtl/ibex_compressed_decoder.sv:809-834
- Edge: yes, of F-CMP-052
- Status: FOLDED into F-CMP-052 (bin CG-CMP-007.cr_insn_equal.auto)

### F-CMP-054: Illegal Zcmp/Zcmt code points in Q2 funct3 101
- What: instr[12:8] values other than 11000/11010/11100/11110/011xx raise illegal-instruction (this
  includes the Zcmt cm.jt/cm.jalt space 000xx..); within 011xx, instr[6:5] = 00 or 10 is illegal.
- Observable at: rvfi_trap + csrr read-back of mcause (2) / mtval (= zero-extended halfword) on
  rvfi_rd_wdata
- Config: none
- Source: spec: zcmp.adoc encodings; zca.adoc opcode map (FSDSP slot) | RTL-defined:
  rtl/ibex_compressed_decoder.sv:835, rtl/ibex_compressed_decoder.sv:839
- Edge: yes, of F-CMP-039
- Status: ACTIVE

### F-CMP-055: Zcmp micro-op visibility on RVFI and counters
- What: every micro-op produces an rvfi_valid with rvfi_pc_rdata = PC of the cm.* instruction,
  rvfi_insn = the synthesized 32-bit instruction, rvfi_ext_expanded_insn_valid = 1,
  rvfi_ext_expanded_insn = the 16-bit encoding, rvfi_ext_expanded_insn_last = 1 only on the final
  micro-op; minstret increments once (only the LAST micro-op counts); rvfi_pc_wdata of intermediate
  micro-ops equals rvfi_pc_rdata (IF has not advanced).
- Observable at: RVFI rvfi_ext_expanded_insn_valid / rvfi_ext_expanded_insn /
  rvfi_ext_expanded_insn_last, rvfi_order, rvfi_pc_wdata; csrr read-back of minstret on
  rvfi_rd_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_core.sv:2263-2282, rtl/ibex_core.sv:2084, rtl/ibex_id_stage.sv:1218-1220,
  rtl/ibex_if_stage.sv:808-809
- Edge: no
- Status: ACTIVE
- Notes: the reference-model comparison must fold micro-ops into one architectural retire. RTL-defined
  fact folded from rtl-arch's fact-check (X-14, Section 5): the rvfi_insn = expansion rule also holds
  for a trapping micro-op and for the reserved rlist 0..3 encodings (tagged INSTR_EXPANDED,
  rtl/ibex_compressed_decoder.sv:626, :691), while a non-expanded compressed instruction (c.ebreak,
  Zca/Zcb, the other illegal halfwords) is traced as the zero-extended halfword; mtval is always the
  halfword (rtl/ibex_controller.sv:866-868).

### F-CMP-056: Interrupt during the cm.push store phase
- What: An interrupt pending while a store micro-op (INSTR_EXPANDED) is in ID is taken between micro-ops:
  IF is halted, the in-flight store completes, IRQ_TAKEN saves mepc = PC of the cm.push (pc_if still
  points at it), the compressed-decoder FSM is reset (flush_expanded), sp is NOT adjusted. After mret the
  whole cm.push re-executes and repeats the stores. The micro-op in ID when the request arrives completes
  first (halt_if stops only new entries, X-7); with the pin edge at the RVFI record of store k, stores
  k+1 (WB) and k+2 (ID) complete, so k+2 or k+3 stores retire, and for k >= N-2 the addi (LAST) can
  already be in ID: the whole cm.push then completes before the interrupt (mepc = PC + 2, sp adjusted, no
  re-execution).
- Observable at: data_req_o/data_addr_o (stores repeated after mret), RVFI (partial micro-op
  sequence, then the handler entry with rvfi_intr = 1); csrr read-back of mepc on rvfi_rd_wdata
- Config: mie, mstatus.MIE, irq_* inputs
- Source: spec: zcmp.adoc "push/pop Fault handling" (norm:interrupts_allowed_in_pushpop), "Software view of
  the push sequence" | RTL-defined: rtl/ibex_controller.sv:498-500, rtl/ibex_controller.sv:698-721,
  rtl/ibex_controller.sv:729-733, rtl/ibex_if_stage.sv:482-483, rtl/ibex_compressed_decoder.sv:885-891
- Edge: yes, of F-CMP-039
- Status: ACTIVE

### F-CMP-057: Interrupt during the cm.pop/popret load phase
- What: same mechanism as F-CMP-056; registers already loaded keep their new values (spec permits), sp
  unchanged, the ret/li a0 not executed; full re-execution after mret. For k >= N-2 the addi sp (COMMIT)
  is in ID at the pin edge, completes and blocks handle_irq until the ret/LAST retires: the sequence
  finishes with the ret executed once before the handler (mepc = ra target; X-7).
- Observable at: RVFI rvfi_rd_wdata of the completed loads, rvfi_intr on the handler entry; csrr
  read-back of mepc on rvfi_rd_wdata
- Config: mie, mstatus.MIE
- Source: spec: zcmp.adoc "Software view of the pop/popret sequence" | RTL-defined: rtl/ibex_controller.sv:498-500
- Edge: yes, of F-CMP-045
- Status: ACTIVE

### F-CMP-058: Interrupts are blocked during the COMMIT micro-ops
- What: While the micro-op in ID is INSTR_EXPANDED_COMMIT (addi sp / li a0 of popret/popretz, first move
  of mvsa01/mva01s) handle_irq is masked, so the following LAST micro-op (ret / second move) always
  enters ID and completes before the interrupt is taken; the interrupt then sees mepc = ret target.
- Observable at: RVFI (the COMMIT and LAST micro-ops always retire together; rvfi_intr on the
  following entry); csrr read-back of mepc on rvfi_rd_wdata
- Config: mie, mstatus.MIE
- Source: spec: zcmp.adoc (norm:Zcmp_pop_sp_commit: "once the stack pointer adjustment has been committed the
  ret must execute") | RTL-defined: rtl/ibex_controller.sv:498-500, rtl/ibex_compressed_decoder.sv:743-764,
  rtl/ibex_compressed_decoder.sv:789-790, rtl/ibex_compressed_decoder.sv:817-818, rtl/ibex_controller.sv:1020
- Edge: yes, of F-CMP-047
- Status: ACTIVE

### F-CMP-059: Debug request, single step and trigger during a Zcmp sequence
- What: enter_debug_mode is masked while the ID micro-op is EXPANDED or COMMIT, so debug entry (debug_req_i,
  dcsr.step, trigger match) waits until the LAST micro-op has retired; dpc = next PC (cm.* PC + 2, or
  the ra target for cm.popret/popretz since dpc = pc_if after the ret's pc_set); a single step covers
  the entire cm.* instruction. A trigger on the cm.* PC itself matches pc_if while the PREVIOUS
  instruction is in ID (the mask reads that instruction's NOT_EXPANDED tag, rtl/ibex_cs_registers.sv:1872)
  and enters debug BEFORE micro-op 0 with dpc = cm.* PC; only a trigger on the next PC is deferred
  (X-19).
- Observable at: rvfi_ext_debug_mode; csrr read-back of dpc on rvfi_rd_wdata in the debug ROM; RVFI
  micro-op count before the debug entry
- Config: dcsr.step, tdata1/tdata2 (trigger), debug_req_i
- Source: RTL-defined: rtl/ibex_controller.sv:473-477, rtl/ibex_controller.sv:698-710
- Edge: yes, of F-CMP-039
- Status: ACTIVE

### F-CMP-060: Store access fault (PMP or bus error) on a pushed store
- What: The faulting store is detected in WB; the following micro-op in ID is held (outstanding_memory_access)
  and killed (wb_exception); mepc = PC of the cm.push (csr_save_wb), mcause = 7, mtval = faulting address;
  sp unchanged; earlier stores are visible in memory; FSM flushed by PC_EXC. Re-execution after the
  handler repeats all stores.
- Observable at: rvfi_trap on the store micro-op; data_req_o/data_addr_o (earlier stores issued,
  none after the fault); csrr read-back of mcause (7) / mtval / mepc on rvfi_rd_wdata
- Config: PMP region config (pmpcfg/pmpaddr), mseccfg
- Source: spec: zcmp.adoc "push/pop Fault handling" (norm:Zcmp_trap, norm:Zcmp_push_sp_commit) |
  RTL-defined: rtl/ibex_id_stage.sv:1015-1019, rtl/ibex_id_stage.sv:1033-1036, rtl/ibex_id_stage.sv:1059-1062,
  rtl/ibex_controller.sv:833-845, rtl/ibex_controller.sv:900-913
- Edge: yes, of F-CMP-039
- Status: ACTIVE
- Notes: Canonical for the DMEM alias F-DMEM-047 (M-10 pass).

### F-CMP-061: Load access fault on a popped load
- What: as F-CMP-060 with mcause = 5; registers loaded before the fault retain new values; sp unchanged;
  no li a0 / ret executed.
- Observable at: rvfi_trap on the load micro-op; rvfi_rd_wdata of the earlier loads; csrr read-back
  of mcause (5) / mtval / mepc on rvfi_rd_wdata
- Config: PMP region config
- Source: spec: zcmp.adoc "Software view of the pop/popret sequence" | RTL-defined:
  rtl/ibex_controller.sv:914-927, rtl/ibex_id_stage.sv:1059-1062
- Edge: yes, of F-CMP-045
- Status: ACTIVE

### F-CMP-062: Misaligned sp during cm.push/cm.pop
- What: Ibex never raises load/store-address-misaligned; a word access with sp[1:0] != 0 is split into
  two bus accesses per micro-op (doubling DMEM transactions); either half can PMP-fault, mtval then
  reports the address of the faulting half.
- Observable at: data_req_o/data_addr_o (two requests per micro-op), RVFI rvfi_mem_addr; csrr
  read-back of mtval on rvfi_rd_wdata for the faulting half
- Config: PMP region config
- Source: spec: rv32.adoc "Load and Store Instructions" (misaligned behaviour EEI-defined) |
  RTL-defined: rtl/ibex_load_store_unit.sv:402-405, rtl/ibex_load_store_unit.sv:254-258
- Edge: yes, of F-CMP-039
- Status: ACTIVE

### F-CMP-063: Exception mid-sequence resets the expansion FSM
- What: Folded into F-CMP-039 (bin CG-CMP-008.cp_reexec.yes): any pc_set with PC_EXC (exception,
  interrupt, debug entry) resets cm_state to CmIdle so the next cm.* starts from micro-op 0 - the
  re-execution rule already stated by F-CMP-056/060.
- Observable at: see F-CMP-039
- Config: see F-CMP-039
- Source: RTL-defined: rtl/ibex_if_stage.sv:482-483, rtl/ibex_compressed_decoder.sv:885-891
- Edge: yes, of F-CMP-039
- Status: FOLDED into F-CMP-039 (bin CG-CMP-008.cp_reexec.yes)

### F-CMP-064: Dummy instruction insertion during a Zcmp sequence (bug candidate)
- What: With SecureIbex dummy instructions enabled (cpuctrlsts.dummy_instr_en=1) the IF stage may
  substitute a dummy instruction into ID on a cycle where id_in_ready_i=1. The compressed decoder FSM
  advances on the same id_in_ready_i (not qualified by insert_dummy_instr), so the micro-op it was
  presenting that cycle is skipped (e.g. one store of cm.push or one load of cm.pop is lost); a dummy on the LAST
  micro-op returns the FSM to idle with the cm.* halfword still buffered and the whole expansion replays.
- Observable at: data_req_o/data_addr_o (a store or load missing), RVFI micro-op count,
  rvfi_ext_expanded_insn sequence
- Config: cpuctrlsts.dummy_instr_en, cpuctrlsts.dummy_instr_mask (frequency)
- Source: RTL-defined: rtl/ibex_if_stage.sv:493 (id_in_ready_i & ~pc_set_i only), rtl/ibex_if_stage.sv:526-535,
  rtl/ibex_dummy_instr.sv:103-104, rtl/ibex_dummy_instr.sv:115, rtl/ibex_compressed_decoder.sv:658-672
- Edge: yes, of F-CMP-039
- Status: ACTIVE
- Notes: reproduced deterministically by tb-infra (program dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_directed.S, slice 2) and
  explained by rtl-arch (dv/auto_dv/evidence/gen_b8_rtl_facts.md, 1eb2ede): the micro-op of the insertion cycle is discarded;
  a replay doubles cm.push stores and, for cm.popret / cm.popretz, reloads from above the frame after the sp increment; the
  dummy's INSTR_NOT_EXPANDED tag admits an interrupt (commit phase) or a debug request mid-expansion (TP-CMP-074).
  gen_bug_log.md B8. Requires DummyInstructions=1 in gen_dut_top (ibex_top derives it from SecureIbex, rtl/ibex_top.sv:214).

### F-CMP-065: Zcmp latency and back-to-back sequences
- What: Folded into F-CMP-039 (bin CG-CMP-006.cr_insn_delay.auto): micro-op count N+1/N+2/N+3/2,
  per-micro-op LSU timing and back-to-back cm.* sequences (no hazard) restate the parents.
- Observable at: see F-CMP-039
- Config: see F-CMP-039
- Source: doc: pipeline_details.rst "Zcmp Push/Pop" (2 - N), "Zcmp Move" (2) rows | RTL-defined:
  rtl/ibex_compressed_decoder.sv:624-834
- Edge: yes, of F-CMP-039
- Status: FOLDED into F-CMP-039 (bin CG-CMP-006.cr_insn_delay.auto)

### F-CMP-066: Illegal compressed instruction mtval and rvfi_insn
- What: Folded into F-ISA-047 (bin CG-CMP-004.cp_mtval_ok.yes): illegal 16-bit encoding: mtval =
  {16'b0, halfword} always; rvfi_insn = the zero-extended halfword for every non-expanded encoding, but
  for the Zcmp reserved rlist 0..3 encodings rvfi_insn is the synthesized 32-bit word with the halfword
  on rvfi_ext_expanded_insn (INSTR_EXPANDED tag, X-14); already stated by F-ISA-047 (canonical
  F-EXC-008).
- Observable at: see F-ISA-047
- Config: see F-ISA-047
- Source: spec: machine.adoc "Machine Trap Value (mtval) Register" (shortest of the faulting instruction) |
  RTL-defined: rtl/ibex_controller.sv:864-869, rtl/ibex_decoder.sv:902-905, rtl/ibex_core.sv:2263-2269
- Edge: yes, of F-EXC-008
- Status: FOLDED into F-EXC-008 (bin CG-CMP-004.cp_mtval_ok.yes)

### F-CMP-067: cm.push with sp near address 0 / wrap
- What: stores at sp-4.. wrap below 0 to 0xFFFFFFFC etc.; addi result wraps.
- Observable at: data_addr_o (wrapped store addresses), RVFI rvfi_rd_wdata (x2)
- Config: none
- Source: RTL-defined: rtl/ibex_compressed_decoder.sv:81-97 (12-bit negative offsets), rtl/ibex_alu.sv:105-107
- Edge: yes, of F-CMP-039
- Status: ACTIVE

### F-CMP-068: Zcmp micro-op register hazards with the surrounding code
- What: cm.pop immediately after a store to the same stack slots (memory ordering), cm.push right after an
  instruction writing one of the pushed registers (WB forwarding into the store data), cm.mva01s right
  after a load into r1s'/r2s' (stall_ld_hz on the move micro-op).
- Observable at: data_wdata_o, RVFI rvfi_rs1_rdata / rvfi_rs2_rdata of the micro-ops
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:1103-1120
- Edge: yes, of F-CMP-039
- Status: ACTIVE

### F-CMP-069: Zcmp halfword arriving with a fetch error (instr_err_i or PMP) executes no micro-op
- What: A cm.push/cm.pop/cm.popret/cm.popretz/cm.mvsa01/cm.mva01s halfword whose fetch returned
  instr_err_i, or whose fetch address is PMP-denied for execute, traps with cause 1 (instruction
  access fault), mtval = mepc = PC of the cm.* halfword, issues no data_req_o, leaves sp and the
  rlist registers unchanged, and the next cm.* (a re-execution of the same one after the handler, or
  a different one) starts from micro-op 0. Two RTL paths: (a) bus error - fetch_err gates the
  expander's valid_i, gets_expanded_o is forced INSTR_NOT_EXPANDED and the FSM stays in CmIdle
  (assertion IbexPushPopFSMStable); the trapping RVFI entry has rvfi_ext_expanded_insn_valid = 0 and
  rvfi_insn = the zero-extended halfword. (b) PMP fetch error - it is merged into if_instr_err only,
  so the expander does start (gets_expanded = INSTR_EXPANDED, the FSM leaves CmIdle when ID accepts
  the first micro-op); instr_fetch_err then kills that micro-op in ID (instr_kill, no lsu_req), the
  exception's pc_set / PC_EXC flush_expanded returns the FSM to CmIdle, and the single trapping RVFI
  entry carries rvfi_ext_expanded_insn_valid = 1 (not _last) with rvfi_insn = the synthesized first
  micro-op.
- Observable at: rvfi_trap + csrr read-back of mcause (1) / mtval (= PC) / mepc (= PC) on
  rvfi_rd_wdata; rvfi_ext_expanded_insn_valid on the trapping entry (0 for the bus error, 1 for
  PMP); data_req_o never asserted for the instruction; instr_addr_o = mtvec after the trap; the next
  cm.* retires its full micro-op sequence from micro-op 0 (rvfi_ext_expanded_insn*)
- Config: PMP region without X covering the cm.* halfword (pmpcfg/pmpaddr, privilege), or
  instr_err_i from the TB memory on that fetch
- Source: RTL-defined: rtl/ibex_if_stage.sv:492 (valid_i = fetch_valid & ~fetch_err),
  rtl/ibex_if_stage.sv:426-430 (PMP error merged into if_instr_err, not into fetch_err),
  rtl/ibex_compressed_decoder.sv:202-203 (gets_expanded_o forced INSTR_NOT_EXPANDED when !valid_i),
  rtl/ibex_compressed_decoder.sv:641, 653, 709, 718, 791, 819 (FSM leaves CmIdle only under valid_i
  && id_in_ready_i), rtl/ibex_compressed_decoder.sv:937 (IbexPushPopFSMStable),
  rtl/ibex_compressed_decoder.sv:885-891 and rtl/ibex_if_stage.sv:482-483 (flush_expanded on
  PC_EXC), rtl/ibex_id_stage.sv:732 (lsu_req gated by instr_executing),
  rtl/ibex_id_stage.sv:1033-1036 (instr_kill), rtl/ibex_controller.sv:233,
  rtl/ibex_controller.sv:320-321 (fetch-error priority), rtl/ibex_controller.sv:859-861 (cause 1,
  mtval = pc_id_i), rtl/ibex_core.sv:2263-2282 (rvfi_insn and expanded tags) | map:
  gen_hierarchy_map.md H-Z6
- Edge: yes, of F-CMP-039
- Status: ACTIVE
- Notes: Added for Critic C-09 item 3 (H-Z6). The fix brief stated "expander must not start" for
  both error sources; the RTL guarantees that only for the bus error - for the PMP error the FSM
  starts and is reset by the exception flush. Architecturally both paths are identical; the
  rvfi_ext_expanded_insn_valid tag is the only visible difference. F-EXC-045 covers the fetch fault
  on cm.popret's return target, not on the cm.* itself.

### F-CMP-070: ret micro-op redirect with a cm.* halfword at the fall-through address
- What: In the cycle the ret micro-op of cm.popret/cm.popretz executes in ID (jump_set -> pc_set)
  the expander is already presenting the sequential halfword at PC + 2. The IF stage masks the
  expander's id_in_ready_i with ~pc_set_i (and the IF/ID register write with ~pc_set_i), so when
  that fall-through halfword is itself a cm.push/pop/popret/popretz/mvsa01/mva01s the FSM does not
  leave CmIdle for it, none of its micro-ops enters ID, exactly one ret micro-op retires (one
  rvfi_ext_expanded_insn_last per cm.popret/popretz), exactly one fetch redirect to ra is issued,
  and when the fall-through cm.* is later executed (reached through a jump) it starts from micro-op
  0.
- Observable at: RVFI (the entry after the ret has rvfi_pc_rdata = ra target; one
  rvfi_ext_expanded_insn_last per cm.popret/popretz; no entry with rvfi_pc_rdata = PC + 2 before the
  target's instruction); instr_req_o/instr_addr_o (one redirect to ra); when the fall-through cm.*
  executes later its first micro-op is micro-op 0 (rvfi_insn = store/load of the top register or the
  first move)
- Config: none
- Source: RTL-defined: rtl/ibex_if_stage.sv:493 (id_in_ready_i & ~pc_set_i to the expander),
  rtl/ibex_if_stage.sv:568-570 (instr_valid_id_d / instr_new_id_d masked by ~pc_set_i),
  rtl/ibex_compressed_decoder.sv:765-772 (CmPopRetRa -> CmIdle with INSTR_EXPANDED_LAST on
  id_in_ready_i), rtl/ibex_compressed_decoder.sv:628-657 (a new expansion starts only under valid_i
  && id_in_ready_i), rtl/ibex_id_stage.sv:936-942 (single-cycle jump_set),
  rtl/ibex_controller.sv:681-684 (pc_set on jump_set) | map: gen_hierarchy_map.md H-Z4
- Edge: yes, of F-CMP-047
- Status: ACTIVE
- Notes: Added for Critic C-09 item 6 (H-Z4). Without the ~pc_set_i mask the squashed fall-through
  cm.* would advance cm_state_q and the next cm.* would start mid-sequence (a "double step"). The
  mask applies to a cm.* at the fall-through of any taken CTI; the ret micro-op is the case where
  the redirecting instruction is itself the last micro-op of an expansion.

---------------------------------------------------------------------------------------------------
## AREA BIT: bit-manipulation under RV32BOTEarlGrey

### F-BIT-001: RV32BOTEarlGrey legal instruction set
- What: The decoder enables the ratified Zba/Zbb/Zbs/Zbc sets plus the draft (bitmanip 0.93) Zbp/Zbt/Zbf/Zbr
  sets, and excludes Zbe (bcompress/bdecompress). Every Zbkb/Zbkc/Zbkx RV32 encoding is also accepted
  because it aliases a decoded instruction. Full table below; "legal" means illegal_insn=0 for that
  encoding in this build.
- Observable at: RVFI rvfi_trap (0 for legal, 1 for illegal), rvfi_rd_wdata
- Config: none
- Source: doc: doc/03_reference/instruction_decode_execute.rst "Bit-Manipulation Extension" table;
  doc/01_overview/compliance.rst "Ibex Instruction Set Extensions" (B: 1.0.0 + 0.93) |
  spec: tools/specs/riscv-isa-manual/src/unpriv/zba.adoc, zbb.adoc, zbs.adoc, zbc.adoc, zbkb.adoc, zb.adoc
  "Instructions (in alphabetical order)" | RTL-defined: rtl/ibex_decoder.sv:500-586, rtl/ibex_decoder.sv:588-651
- Edge: no
- Status: ACTIVE
- Notes: The draft 0.93 instructions have NO specification on disk (only the ratified manual is in
  tools/specs); their reference semantics can only be taken from rtl/ibex_alu.sv comments (spec gap).

| Mnemonic | Sub-ext (status) | Encoding (funct7 / funct3 or funct12) | Legal in OTEarlGrey | Cycles | Decoder cite (rtl/ibex_decoder.sv) |
|---|---|---|---|---|---|
| sh1add/sh2add/sh3add | Zba (ratified) | 0010000 / 010,100,110 | yes | 1 | 609-611, 1291-1293 |
| add.uw, sh1add.uw, sh2add.uw, sh3add.uw, slli.uw | Zba RV64-only | opcode 0x3b / 0x1b | no (illegal opcode) | - | 897-899 |
| andn/orn/xnor | Zbb, Zbkb (ratified) | 0100000 / 111,110,100 | yes | 1 | 613-615, 1286-1288 |
| clz/ctz/cpop | Zbb (ratified) | OP-IMM 0110000 + rs2 00000/00001/00010, funct3 001 | yes | 1 | 517-523, 1103-1105 |
| clzw/ctzw/cpopw | Zbb RV64-only | OP-IMM-32 | no | - | 897-899 |
| min/max/minu/maxu | Zbb (ratified) | 0000101 / 100,110,101,111 | yes | 1 | 618-621, 1277-1280 |
| sext.b/sext.h | Zbb (ratified) | OP-IMM 0110000 + rs2 00100/00101, funct3 001 | yes | 1 | 522-523, 1106-1107 |
| zext.h | Zbb (ratified) = pack rd,rs1,x0 | 0000100 / 100, rs2=0 | yes | 1 | 622, 1282 |
| rol/ror | Zbb, Zbkb (ratified) | 0110000 / 001,101 | yes | 2 | 616-617, 1264-1275 |
| rori | Zbb, Zbkb (ratified) | OP-IMM 0110000 / 101 (instr[26:25]=00) | yes | 2 | 550-552, 1174-1177 |
| rolw/rorw/roriw | Zbb RV64-only | OP-32 / OP-IMM-32 | no | - | 897-899 |
| orc.b | Zbb (ratified) = gorci 7 | OP-IMM funct12 0x287 | yes | 1 | 563-571, 1179 |
| rev8 | Zbb, Zbkb (ratified) = grevi 24 | OP-IMM funct12 0x698 | yes | 1 | 554-562, 1178 |
| brev8 | Zbkb (ratified) = grevi 7 | OP-IMM funct12 0x687 | yes | 1 | 554-562, 1178 |
| pack/packh | Zbkb (ratified) | 0000100 / 100, 111 | yes | 1 | 622, 624, 1282, 1284 |
| packu | Zbp (draft 0.93) | 0100100 / 100 | yes | 1 | 623, 1283 |
| zip/unzip | Zbkb RV32 (ratified) = shfli/unshfli 15 | OP-IMM 0000100 + rs2 01111, funct3 001/101 | yes | 1 | 510-516, 572-577, 1100, 1181-1185 |
| bclr/bset/binv/bext | Zbs (ratified) | 0100100/001, 0010100/001, 0110100/001, 0100100/101 | yes | 1 | 626-629, 1296-1299 |
| bclri/bseti/binvi | Zbs (ratified) | OP-IMM 0100100/0010100/0110100, funct3 001, instr[26:25]=00 | yes | 1 | 506-509, 1096-1098 |
| bexti | Zbs (ratified) | OP-IMM 0100100 / 101, instr[26:25]=00 | yes | 1 | 550-552, 1173 |
| clmul/clmulr/clmulh | Zbc, Zbkc (ratified; clmulr Zbc only) | 0000101 / 001,010,011 | yes | 1 | 643-647, 1330-1338 |
| xperm4 (= xperm.n) | Zbkx (ratified) / Zbp draft | 0010100 / 010 | yes | 1 | 637, 1313-1315 |
| xperm8 (= xperm.b) | Zbkx (ratified) / Zbp draft | 0010100 / 100 | yes | 1 | 638, 1316-1318 |
| xperm.h | Zbp (draft) | 0010100 / 110 | yes | 1 | 639, 1319-1321 |
| slo/sro | Zbp (draft) | 0010000 / 001,101 | yes | 1 | 640-641, 1322-1327 |
| sloi/sroi | Zbp (draft) | OP-IMM 0010000 / 001,101 | yes | 1 | 503-505, 547-549, 1093-1095, 1170-1172 |
| grev/gorc | Zbp (draft) | 0110100/101, 0010100/101 | yes | 1 | 633-634, 1305-1306 |
| grevi/gorci (any shamt) | Zbp (draft) | OP-IMM 0110100/0010100, funct3 101 | yes | 1 | 554-571, 1178-1179 |
| shfl/unshfl | Zbp (draft) | 0000100 / 001,101 | yes | 1 | 635-636, 1307-1312 |
| shfli/unshfli (any shamt) | Zbp (draft) | OP-IMM 0000100, funct3 001/101, instr[26]=0 | yes | 1 | 510-516, 572-577 |
| cmov/cmix | Zbt (draft) | instr[26:25]=11, funct3 101/001, rs3=instr[31:27] | yes | 2 | 592-593, 1210-1227 |
| fsl/fsr | Zbt (draft) | instr[26:25]=10, funct3 001/101, rs3=instr[31:27] | yes | 2 | 592-593, 1228-1245 |
| fsri | Zbt (draft) | OP-IMM funct3 101, instr[26]=1, rs3=instr[31:27], shamt=instr[25:20] | yes | 2 | 540-541, 1157-1164 |
| bfp | Zbf (draft) | 0100100 / 111 | yes | 1 (doc says 2) | 630-631, 1302 |
| crc32.b/h/w, crc32c.b/h/w | Zbr (draft) | OP-IMM 0110000 + rs2 10000/10001/10010/11000/11001/11010, funct3 001 | yes | 2 | 524-531, 1108-1143 |
| bcompress/bdecompress | Zbe (draft) | 0000100/110, 0100100/110 | NO (RV32BFull only) | - | 649-650 |
| cmov/cmix/fsl/fsr/fsri, xperm.h, slo*, gorc*/grev* generic, shfl*, packu, bfp, crc32* | not in any ratified spec | - | yes | - | see rows |

### F-BIT-002: Zba sh1add / sh2add / sh3add
- What: rd = rs2 + (rs1 << 1/2/3); single cycle via the shifted adder input.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "sh1add", "sh2add", "sh3add" (norm:sh1add_op) | RTL-defined: rtl/ibex_decoder.sv:609-611,
  rtl/ibex_alu.sv:75-92
- Edge: no
- Status: ACTIVE

### F-BIT-003: shNadd shift-out and wrap
- What: sh3add with rs1 = 0xE0000000 (top bits shifted out), rs1 = 0xFFFFFFFF; sum wrapping past 2^32;
  rs1 = rs2.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "sh3add" | RTL-defined: rtl/ibex_alu.sv:87-89
- Edge: yes, of F-BIT-002
- Status: ACTIVE

### F-BIT-004: Zbb andn / orn / xnor
- What: rs1 & ~rs2, rs1 | ~rs2, ~(rs1 ^ rs2).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "andn", "orn", "xnor" | RTL-defined: rtl/ibex_alu.sv:371-397
- Edge: no
- Status: ACTIVE

### F-BIT-005: Zbb clz / ctz / cpop
- What: leading/trailing zero count and population count via the Brent-Kung prefix counter; 6-bit result.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "clz", "ctz", "cpop" | RTL-defined: rtl/ibex_decoder.sv:517-523, rtl/ibex_alu.sv:435-546
- Edge: no
- Status: ACTIVE

### F-BIT-006: Bit-count boundary values
- What: clz(0) = 32, ctz(0) = 32, cpop(0) = 0, cpop(0xFFFFFFFF) = 32, clz(0x80000000) = 0, ctz(1) = 0,
  clz(1) = 31, ctz(0x80000000) = 31, single-bit inputs at every position.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "clz" ("if the input is 0, the output is XLEN"), "ctz", "cpop" |
  RTL-defined: rtl/ibex_alu.sv:440-464
- Edge: yes, of F-BIT-005
- Status: ACTIVE

### F-BIT-007: Zbb min / max / minu / maxu
- What: signed/unsigned minimum and maximum.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "min", "max", "minu", "maxu" | RTL-defined: rtl/ibex_alu.sv:119-171, rtl/ibex_alu.sv:552
- Edge: no
- Status: ACTIVE

### F-BIT-008: min/max with equal operands and mixed-sign inputs
- What: equal operands return that value; min(-1, 1) = -1 but minu(0xFFFFFFFF, 1) = 1; max(INT_MIN,
  INT_MAX) = INT_MAX; maxu(0x80000000, 0x7FFFFFFF) = 0x80000000.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "min"/"max" operation pseudocode | RTL-defined: rtl/ibex_alu.sv:552, rtl/ibex_alu.sv:136-142
- Edge: yes, of F-BIT-007
- Status: ACTIVE

### F-BIT-009: Zbb sext.b / sext.h
- What: sign-extend bit 7 / bit 15.
- Observable at: RVFI rvfi_rd_wdata (0x80 -> 0xFFFFFF80, 0x7F -> 0x7F, 0x8000 -> 0xFFFF8000)
- Config: none
- Source: spec: zb.adoc "sext.b", "sext.h" | RTL-defined: rtl/ibex_alu.sv:575-576
- Edge: no
- Status: ACTIVE

### F-BIT-010: Zbb zext.h via pack with rs2=x0
- What: zext.h rd, rs = pack rd, rs, x0 -> {16'h0, rs[15:0]}.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "zext.h" (RV32 encoding), "pack" note | RTL-defined: rtl/ibex_decoder.sv:622,
  rtl/ibex_alu.sv:563-569
- Edge: no
- Status: ACTIVE

### F-BIT-011: pack / packh / packu with arbitrary rs2
- What: pack -> {rs2[15:0], rs1[15:0]}; packh -> {16'h0, rs2[7:0], rs1[7:0]}; packu (draft) ->
  {rs2[31:16], rs1[31:16]}; rs1 == rs2 duplicates the half.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "pack", "packh" (Zbkb) | RTL-defined: rtl/ibex_alu.sv:558-569
- Edge: no
- Status: ACTIVE
- Notes: packu has no on-disk spec (draft Zbp).

### F-BIT-012: Zbb rol / ror / rori (two-cycle)
- What: rotate by rs2[4:0] or shamt; implemented as two shifts across two ID cycles (imd_val register),
  stall_alu for one cycle.
- Observable at: RVFI rvfi_rd_wdata, rvfi_ext_mcycle
- Config: none
- Source: spec: zb.adoc "rol", "ror", "rori" | doc: instruction_decode_execute.rst table (rol, ror[i] multi-cycle) |
  RTL-defined: rtl/ibex_decoder.sv:1174-1177, rtl/ibex_decoder.sv:1264-1275, rtl/ibex_alu.sv:1227-1240,
  rtl/ibex_id_stage.sv:943-947
- Edge: no
- Status: ACTIVE

### F-BIT-013: Rotate amount 0, 31, 32 and rori shamt[5]
- What: rol/ror by 0 and by 32 (rs2[4:0]=0) return rs1 (special case in the ALU); ror by 31 == rol by 1;
  rs2 upper bits ignored; rori with shamt[5]=1 (instr[25]) is illegal (reserved in RV32).
- Observable at: RVFI rvfi_rd_wdata; rvfi_trap + csrr read-back of mcause (2) on rvfi_rd_wdata for
  rori with instr[25] = 1
- Config: none
- Source: spec: zb.adoc "rori" ("shamt[5]=1 are reserved"), "rol"/"ror" (shamt = rs2[4:0]) |
  RTL-defined: rtl/ibex_alu.sv:1229-1233, rtl/ibex_decoder.sv:550-552
- Edge: yes, of F-BIT-012
- Status: ACTIVE

### F-BIT-014: Zbb orc.b
- What: each byte becomes 0x00 if zero else 0xFF (encoded as gorci rs1, 7).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "orc.b" (norm:orc_b_op) | RTL-defined: rtl/ibex_decoder.sv:563-571, rtl/ibex_alu.sv:599-627
- Edge: no
- Status: ACTIVE

### F-BIT-015: Zbb rev8
- What: byte reversal (grevi rs1, 24).
- Observable at: RVFI rvfi_rd_wdata (0x01020304 -> 0x04030201)
- Config: none
- Source: spec: zb.adoc "rev8" (RV32 encoding 0x698) | RTL-defined: rtl/ibex_decoder.sv:554-562, rtl/ibex_alu.sv:629-641
- Edge: no
- Status: ACTIVE

### F-BIT-016: Generic grevi / gorci and brev8
- What: all 32 grevi control values (bit-reverse within 2/4/8/16/32-bit groups: brev8 = grevi 7 reverses
  bits in each byte; grevi 31 reverses the whole word) and all 32 gorci values are legal (draft Zbp).
  grev/gorc register forms use rs2[4:0].
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "brev8" (Zbkb, encoding 0x687) | RTL-defined: rtl/ibex_alu.sv:599-642
- Edge: no
- Status: ACTIVE
- Notes: only rev8, orc.b, brev8 have ratified semantics; other control values are draft-defined.

### F-BIT-017: Zbs register forms bclr / bset / binv / bext
- What: index = rs2[4:0]; bext returns bit as 0/1.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "bclr", "bset", "binv", "bext" | RTL-defined: rtl/ibex_alu.sv:292-294, rtl/ibex_alu.sv:582-589
- Edge: no
- Status: ACTIVE

### F-BIT-018: Zbs immediate forms bclri / bseti / binvi / bexti
- What: index = shamt[4:0] = instr[24:20].
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "bclri", "bseti", "binvi", "bexti" (RV32 encodings) | RTL-defined:
  rtl/ibex_decoder.sv:506-509, rtl/ibex_decoder.sv:550-552, rtl/ibex_decoder.sv:1096-1098, rtl/ibex_decoder.sv:1173
- Edge: no
- Status: ACTIVE

### F-BIT-019: Single-bit index 0 and 31, rs2 upper bits, shamt[5] reserved
- What: index 0 and 31 for all four ops; bset on an already-set bit; bclr on a clear bit; binv twice;
  rs2 = 0xFFFFFFFF selects bit 31; bclri/bseti/binvi/bexti with instr[25]=1 (shamt[5]) raise illegal.
- Observable at: RVFI rvfi_rd_wdata; rvfi_trap + csrr read-back of mcause (2) on rvfi_rd_wdata for
  the instr[25] = 1 immediate forms
- Config: none
- Source: spec: zb.adoc "bclri" (norm:bclri_shamt_rsv_rv32) and siblings | RTL-defined:
  rtl/ibex_decoder.sv:508-509, rtl/ibex_decoder.sv:551-552, rtl/ibex_alu.sv:286-288
- Edge: yes, of F-BIT-017
- Status: ACTIVE

### F-BIT-020: Zbc clmul / clmulh / clmulr
- What: carry-less product low half, high half, and bits [62:31]; single cycle via a 32x32 AND/XOR tree.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "clmul", "clmulh", "clmulr" (norm:clmul_op, norm:clmulh_op, norm:clmulr_op) |
  RTL-defined: rtl/ibex_decoder.sv:643-647, rtl/ibex_alu.sv:883-985
- Edge: no
- Status: ACTIVE

### F-BIT-021: clmul corner values
- What: clmul(x, 0) = 0; clmul(x, 1) = x; clmul(0xFFFFFFFF, 0xFFFFFFFF) = 0x55555555; clmulh(0xFFFFFFFF,
  0xFFFFFFFF) = 0x55555555; clmulr = (clmulh << 1) | (bit 31 of clmul) relation; single-bit operands
  (1<<i) x (1<<j) with i+j >= 32 land in clmulh.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "clmulr" note (bit-reversed clmul) | RTL-defined: rtl/ibex_alu.sv:977-985
- Edge: yes, of F-BIT-020
- Status: ACTIVE

### F-BIT-022: Draft Zbp slo / sro / sloi / sroi
- What: shift left/right filling with ones (shift_ones into the 33rd bit).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_decoder.sv:503-505, rtl/ibex_decoder.sv:547-549, rtl/ibex_decoder.sv:640-641,
  rtl/ibex_alu.sv:322-324, rtl/ibex_alu.sv:342-343 (no on-disk spec)
- Edge: no
- Status: ACTIVE

### F-BIT-023: slo/sro by 0 and 31, register amount masking
- What: slo x, 0 = x; slo 0, 31 = 0x7FFFFFFF; sro 0, 1 = 0x80000000; sro by 31 of 0 = 0xFFFFFFFE; rs2 upper
  bits ignored.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_alu.sv:329-355
- Edge: yes, of F-BIT-022
- Status: ACTIVE

### F-BIT-024: Draft Zbp shfl / unshfl (and zip / unzip)
- What: bit shuffle controlled by rs2[3:0] / shamt[3:0]; zip = shfli 15, unzip = unshfli 15 (Zbkb RV32
  ratified encodings); shfli with instr[26]=1 is illegal.
- Observable at: RVFI rvfi_rd_wdata; rvfi_trap + csrr read-back of mcause (2) on rvfi_rd_wdata for
  shfli with instr[26] = 1
- Config: none
- Source: spec: zb.adoc "zip", "unzip" (Zbkb) | RTL-defined: rtl/ibex_decoder.sv:510-516, rtl/ibex_decoder.sv:572-577,
  rtl/ibex_alu.sv:654-730
- Edge: no
- Status: ACTIVE

### F-BIT-025: Draft Zbp xperm.n / xperm.b / xperm.h (xperm4 / xperm8)
- What: nibble/byte/halfword crossbar lookup of rs1 indexed by rs2 fields; xperm4 and xperm8 (Zbkx) share
  the xperm.n / xperm.b encodings.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "xperm4", "xperm8" (Zbkx) | RTL-defined: rtl/ibex_decoder.sv:637-639, rtl/ibex_alu.sv:742-820
- Edge: no
- Status: ACTIVE

### F-BIT-026: xperm out-of-range index gives zero
- What: any index whose upper bits are non-zero (nibble index >= 8, byte index >= 4, halfword index >= 2)
  yields a zero element; identity permutation; all-same index.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: spec: zb.adoc "xperm4"/"xperm8" ("zero if the index is out of bounds") | RTL-defined:
  rtl/ibex_alu.sv:752-771, rtl/ibex_alu.sv:817-819
- Edge: yes, of F-BIT-025
- Status: ACTIVE

### F-BIT-027: Draft Zbt cmov / cmix (two-cycle, rs3)
- What: cmov rd,rs2,rs1,rs3: rd = (rs2 != 0) ? rs1 : rs3; cmix rd,rs2,rs1,rs3: rd = (rs1 & rs2) |
  (rs3 & ~rs2). rs3 = instr[31:27] is read in the second cycle through the rs1 read port.
- Observable at: RVFI rvfi_rd_wdata, rvfi_rs3_addr/rvfi_rs3_rdata, rvfi_ext_mcycle
- Config: none
- Source: RTL-defined: rtl/ibex_decoder.sv:592-593, rtl/ibex_decoder.sv:1207-1227, rtl/ibex_decoder.sv:172-203,
  rtl/ibex_alu.sv:1207-1225, rtl/ibex_core.sv:2303-2319 (no on-disk spec)
- Edge: no
- Status: ACTIVE

### F-BIT-028: Draft Zbt fsl / fsr / fsri (two-cycle funnel shifts)
- What: 64-bit funnel {rs1,rs3} shifted by rs2[5:0] (fsri: imm[5:0]); rs3 = instr[31:27].
- Observable at: RVFI rvfi_rd_wdata, rvfi_rs3_*, rvfi_ext_mcycle
- Config: none
- Source: RTL-defined: rtl/ibex_decoder.sv:540-541, rtl/ibex_decoder.sv:1155-1164, rtl/ibex_decoder.sv:1228-1245,
  rtl/ibex_alu.sv:204-224 (pseudocode), rtl/ibex_alu.sv:277-290, rtl/ibex_alu.sv:1227-1240
- Edge: no
- Status: ACTIVE

### F-BIT-029: Funnel shift amounts 0, 31, 32, 33, 63
- What: amount 0 -> rs1; 32 -> rs3; 1..31 normal; 33..63 swap the operand roles (shift_amt[5]); rs2
  bits above [5] ignored.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_alu.sv:210-224, rtl/ibex_alu.sv:1229-1233
- Edge: yes, of F-BIT-028
- Status: ACTIVE

### F-BIT-030: Draft Zbf bfp (bit-field place)
- What: len = rs2[27:24] (0 means 16), off = rs2[20:16], data = rs2[len-1:0]; rd = rs1 with bits
  [off+len-1:off] replaced by data. Single cycle in RTL.
- Observable at: RVFI rvfi_rd_wdata, rvfi_ext_mcycle
- Config: none
- Source: doc: instruction_decode_execute.rst table (Zbf listed as multi-cycle) | RTL-defined:
  rtl/ibex_decoder.sv:630-631, rtl/ibex_decoder.sv:1302 (no alu_multicycle), rtl/ibex_alu.sv:257-275
- Edge: no
- Status: ACTIVE
- Notes: doc/RTL disagreement: doc says all Zbf instructions take 2 cycles; RTL executes bfp in 1.

### F-BIT-031: bfp len=0 and field overflow
- What: len field 0 places 16 bits; off + len > 32 truncates at bit 31 (e.g. off=31,len=16 places one bit);
  data bits above len are ignored.
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_alu.sv:266-275
- Edge: yes, of F-BIT-030
- Status: ACTIVE

### F-BIT-032: Draft Zbr crc32.b/h/w and crc32c.b/h/w (two-cycle)
- What: one CRC-32 (poly 0x04C11DB7) or CRC-32C (0x1EDC6F41) reduction step over the low 8/16/32 bits of rs1
  using a Barrett-reduction with clmul in two cycles.
- Observable at: RVFI rvfi_rd_wdata, rvfi_ext_mcycle
- Config: none
- Source: RTL-defined: rtl/ibex_decoder.sv:524-531, rtl/ibex_decoder.sv:1108-1143, rtl/ibex_alu.sv:851-949,
  rtl/ibex_alu.sv:1242-1262 (no on-disk spec)
- Edge: no
- Status: ACTIVE

### F-BIT-033: crc32 corner inputs
- What: crc32.w(0) = 0 and crc32c.w(0) = 0 (linear operation); crc32.b/.h results DEPEND on the high bits
  linearly: rd = clmul_part(rs1[7:0]) ^ (rs1 >> 8) (resp. rs1[15:0], >> 16), the draft's crc32(x, n)
  that shifts x right n times, so two inputs differing only above bit 8 (16) give results differing by
  delta >> 8 (>> 16); all-ones inputs; known vectors from the RTL equation rd = (rs1 >> n) ^
  rev(rev(rs1 << (32-n)) cx rev(mu) cx P).
- Observable at: RVFI rvfi_rd_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_alu.sv:859-881, rtl/ibex_alu.sv:932-938, rtl/ibex_alu.sv:1247-1248
  (^ (operand_a >> 8 / 16)) | fact-check: rtl-arch T-053 TP-BIT-033
- Edge: yes, of F-BIT-032
- Status: ACTIVE
- Notes: corrected by rtl-arch T-053 (X-23): the former "crc32.b ignores rs1[31:8]" statement was wrong.

### F-BIT-034: Zbe bcompress / bdecompress are illegal in OTEarlGrey
- What: Folded into F-BIT-001 (bin CG-BIT-011.cp_illegal_class.bcompress): Zbe bcompress/bdecompress
  (0000100/110, 0100100/110) are illegal in OTEarlGrey - a row of the parent's legality table.
- Observable at: see F-BIT-001
- Config: see F-BIT-001
- Source: doc: instruction_decode_execute.rst ("OTEarlGrey version comprises all sub-extensions except for
  the Zbe") | RTL-defined: rtl/ibex_decoder.sv:649-650
- Edge: yes, of F-BIT-001
- Status: FOLDED into F-BIT-001 (bin CG-BIT-011.cp_illegal_class.bcompress)

### F-BIT-035: RV64-only bitmanip encodings are illegal
- What: Folded into F-BIT-001 (bin CG-BIT-011.cp_illegal_class.op32_any): RV64-only Zb* encodings
  (OP-32 0x3b / OP-IMM-32 0x1b) hit the illegal-opcode default - a row of the parent's legality
  table.
- Observable at: see F-BIT-001
- Config: see F-BIT-001
- Source: spec: zb.adoc "add.uw" etc. (OP-32 encodings) | RTL-defined: rtl/ibex_decoder.sv:897-899
- Edge: yes, of F-BIT-001
- Status: FOLDED into F-BIT-001 (bin CG-BIT-011.cp_illegal_class.op32_any)

### F-BIT-036: Interrupt, NMI or debug request arriving during a two-cycle bitmanip op is deferred
- What: Alias of F-MUL-023: bitmanip perspective (the two-cycle
  rol/ror/rori/cmov/cmix/fsl/fsr/fsri/crc32* class of the canonical's multi-cycle set, including the
  rs3 read in the second cycle for the ternary forms), see canonical. The writeback-busy coincidence
  is F-BIT-041.
- Edge: yes, of F-BIT-012
- Status: ALIAS of F-MUL-023

### F-BIT-037: Non-canonical funct7 bits accepted for some OP-IMM bitmanip forms (RTL leniency)
- What: sloi (instr[31:27]=00100) is accepted with any instr[26:25]; sroi/grevi/gorci/unshfli accept any
  instr[25]; shfli requires instr[26]=0 but accepts instr[25]. Spec-reserved encodings therefore execute
  as the draft instruction instead of trapping. Contrast: slli/srli/srai/rori/bclri/bseti/binvi/bexti
  require instr[26:25]=00.
- Observable at: rvfi_trap = 0 with rvfi_rd_wdata = the canonical form's result for the reserved
  encodings
- Config: none
- Source: RTL-defined: rtl/ibex_decoder.sv:503-505, rtl/ibex_decoder.sv:547-549, rtl/ibex_decoder.sv:554-577
- Edge: yes, of F-BIT-001
- Status: ACTIVE
- Notes: candidate owner question: treat as expected (don't-care bits) or as illegal-decode gaps?

### F-BIT-038: Bitmanip with rd=x0
- What: all Zb* forms with rd=x0 execute (including 2-cycle ones) and write nothing.
- Observable at: RVFI rvfi_rd_addr=0, rvfi_ext_mcycle
- Config: none
- Source: spec: rv32.adoc "HINT Instructions" (analogous) | RTL-defined: rtl/ibex_decoder.sv:588-591
- Edge: yes, of F-BIT-001
- Status: ACTIVE

### F-BIT-039: Bitmanip operand forwarding and hazards
- What: a two-cycle op whose rs1/rs2/rs3 was written by the previous instruction (WB forwarding) or by a
  load still in WB (stall_ld_hz, incl. rs3 read in the second cycle) returns the architecturally correct
  result.
- Observable at: RVFI rvfi_rs1_rdata/rvfi_rs3_rdata, rvfi_rd_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:1103-1120, rtl/ibex_decoder.sv:201-203
- Edge: yes, of F-BIT-012
- Status: ACTIVE

### F-BIT-040: misa.X reflects the draft bitmanip extensions
- What: Alias of F-CSR-021: bitmanip perspective of the misa value (X bit set by RV32BExtra); see
  the canonical entry.
- Observable at: see F-CSR-021 (canonical)
- Config: see F-CSR-021
- Source: RTL-defined: rtl/ibex_cs_registers.sv:377-391
- Edge: yes, of F-BIT-001
- Status: ALIAS of F-CSR-021

### F-BIT-041: Two-cycle bitmanip op deferred in its first cycle by an outstanding WB memory access
- What: When a rol/ror/rori/cmov/cmix/fsl/fsr/fsri/crc32* enters ID while WB still waits for the response
  of a preceding load or store, the op is held BEFORE its first cycle: instr_executing requires
  ~outstanding_memory_access and id_fsm_q advances only under instr_executing, so FIRST_CYCLE executes
  in the response cycle and MULTI_CYCLE one cycle later, when the access has left WB and ready_wb_i is
  1 (multicycle_done & ready_wb_i exits at once). The ALU writes its intermediate value once, in the
  deferred first cycle; the register write happens once, on instr_id_done. Analogue of F-MUL-011 /
  F-MUL-024 (deferred start) for the ALU multicycle class; a second-cycle hold does not occur.
- Observable at: RVFI retire spacing (rvfi_ext_mcycle delta of the two-cycle op from the access record
  = 2 + W, W = the response delay beyond min1) with rvfi_rd_wdata correct and rvfi_rs3_* populated for
  the ternary forms; exactly one retirement; dbus (data_rvalid_i of the preceding access arrives after
  the op entered ID, timed by the dbus monitor against the previous retirement)
- Config: none (the dbus response latency is the stimulus)
- Source: RTL-defined: rtl/ibex_id_stage.sv:1054-1062 (instr_executing needs ~outstanding_memory_access),
  rtl/ibex_id_stage.sv:864-868 (id_fsm_q advances only under instr_executing),
  rtl/ibex_id_stage.sv:943-947 (first cycle: stall_alu, MULTI_CYCLE), rtl/ibex_id_stage.sv:954-966
  (exit on multicycle_done & ready_wb_i, reached after the access completed),
  rtl/ibex_id_stage.sv:1012, rtl/ibex_id_stage.sv:1130-1133, rtl/ibex_alu.sv:1235-1239 and
  rtl/ibex_alu.sv:1252-1256 (imd_val_we only in the first cycle) | fact-check:
  rtl-arch T-053 X-12 (TP-BIT-043) | map: gen_hierarchy_map.md H-I1
- Edge: yes, of F-BIT-012
- Status: ACTIVE
- Notes: Added for Critic C-09 item 4 (H-I1); mechanism corrected by rtl-arch T-053 (X-12): the former
  "held in its second cycle" statement described an unreachable path.

---------------------------------------------------------------------------------------------------
## AREA BTALU: branch target ALU (BranchTargetALU=1)

### F-BTALU-001: Branch target computed in parallel with the condition
- What: bt_a = pc_id, bt_b = imm_b_type; branch_target = bt_a + bt_b (33-bit add, carry dropped)
  while the main ALU evaluates the condition in the same (first) cycle; taken branch: branch_set the
  same cycle, pc_set to the IF stage, one ID cycle total (stall only for the refetch). A not-taken
  branch with data_ind_timing = 0 does not redirect: branch_set stays 0, no pc_set and no IF flush,
  rvfi_pc_wdata = pc + len, and the branch completes in FIRST_CYCLE with no stall
  (rtl/ibex_id_stage.sv:925-928); the taken / not-taken pair is the timing statement that F-ISA-024
  aliases and F-BTALU-005 folds here.
- Observable at: instr_addr_o (target request for a taken branch; no non-sequential request for a
  not-taken one), RVFI rvfi_pc_wdata (target or pc + len), rvfi_ext_mcycle
- Config: cpuctrlsts.data_ind_timing (see F-BTALU-006)
- Source: doc: pipeline_details.rst "Branch (Taken)" row (1 - N with Branch Target ALU) |
  RTL-defined: rtl/ibex_decoder.sv:1008-1012, rtl/ibex_id_stage.sv:369-388,
  rtl/ibex_ex_block.sv:94-101, rtl/ibex_id_stage.sv:771-793 (g_branch_set_flop is the elaborated
  block under SecureIbex; :790-791 select the direct branch_set_raw_d path when data_ind_timing_i =
  0), rtl/ibex_id_stage.sv:925-928
- Edge: no
- Status: ACTIVE

### F-BTALU-002: jal target via BTALU, single cycle
- What: bt_a = pc, bt_b = imm_j; jump_set in the first cycle; no MULTI_CYCLE state (stall_jump = 0); link
  written the same cycle by the main ALU.
- Observable at: instr_addr_o = target, RVFI rvfi_rd_wdata (= pc + 4), rvfi_ext_mcycle
- Config: none
- Source: doc: pipeline_details.rst "Jump" row | RTL-defined: rtl/ibex_decoder.sv:953-956, rtl/ibex_decoder.sv:327-330,
  rtl/ibex_id_stage.sv:936-942
- Edge: no
- Status: ACTIVE

### F-BTALU-003: jalr target via BTALU (rs1 + imm_i), LSB cleared in IF
- What: bt_a = forwarded rs1, bt_b = imm_i; the BTALU sum is passed unmodified to IF where bit 0 is dropped.
- Observable at: instr_addr_o = (rs1 + imm) & ~1
- Config: none
- Source: spec: rv32.adoc "Unconditional Jumps" (norm:jalr_target) | RTL-defined: rtl/ibex_decoder.sv:975-978,
  rtl/ibex_id_stage.sv:372-377, rtl/ibex_if_stage.sv:288
- Edge: no
- Status: ACTIVE

### F-BTALU-004: Link value written by the main ALU concurrently
- What: Folded into F-BTALU-002 (bin CG-ISA-006.cr_link.jal_pc4): the link value pc + (2|4) is
  written by the main ALU in the same (first) cycle as the BTALU target, already stated by the
  parent.
- Observable at: see F-BTALU-002
- Config: see F-BTALU-002
- Source: RTL-defined: rtl/ibex_decoder.sv:327-330, rtl/ibex_decoder.sv:356-359, rtl/ibex_decoder.sv:965-971
- Edge: yes, of F-BTALU-002
- Status: FOLDED into F-BTALU-002 (bin CG-ISA-006.cr_link.jal_pc4)

### F-BTALU-005: Not-taken branch does not redirect (data_ind_timing=0)
- What: Folded into F-BTALU-001 (bin CG-BTALU-001.cr_taken_dit_redirect.nt_dit0_noredir): not-taken
  branch with data_ind_timing = 0: no pc_set, no IF flush, rvfi_pc_wdata = pc + len - the other half
  of the parent's taken/not-taken statement.
- Observable at: see F-BTALU-001
- Config: see F-BTALU-001
- Source: doc: pipeline_details.rst "Branch (Not-Taken)" row | RTL-defined: rtl/ibex_id_stage.sv:925-928
- Edge: yes, of F-BTALU-001
- Status: FOLDED into F-BTALU-001 (bin CG-BTALU-001.cr_taken_dit_redirect.nt_dit0_noredir)

### F-BTALU-006: data_ind_timing=1 makes every branch two cycles and redirects not-taken branches
- What: Alias of F-DIT-002: branch-target-ALU perspective of data_ind_timing branch timing (bt_b =
  IMM_B_INCR_PC redirects a not-taken branch to pc + len); see the canonical entry.
- Observable at: see F-DIT-002 (canonical)
- Config: see F-DIT-002
- Source: RTL-defined: rtl/ibex_id_stage.sv:771-793, rtl/ibex_id_stage.sv:819-831, rtl/ibex_id_stage.sv:925-928,
  rtl/ibex_decoder.sv:1008-1012, rtl/ibex_cs_registers.sv:1905
- Edge: yes, of F-BTALU-001
- Status: ALIAS of F-DIT-002

### F-BTALU-007: Targets with bit 1 set and odd targets: no exception
- What: Folded into F-BTALU-003 (bin CG-ISA-006.cp_target_align.half): half-aligned (addr[1] = 1)
  targets fetch normally and odd jalr sums drop bit 0 with no exception - restates F-BTALU-003,
  F-CMP-001 and F-EXC-067 (F-ISA-052).
- Observable at: see F-BTALU-003
- Config: see F-BTALU-003
- Source: spec: rv32.adoc "Conditional Branches" (norm:branch_misaligned_c_no_exception); zca.adoc
  (norm:Zca_no_misaligned) | RTL-defined: rtl/ibex_decoder.sv:163-165, rtl/ibex_if_stage.sv:288,
  rtl/ibex_controller.sv:561
- Edge: yes, of F-BTALU-003
- Status: FOLDED into F-BTALU-003 (bin CG-ISA-006.cp_target_align.half)

### F-BTALU-008: rvfi_pc_wdata keeps bit 0 for jalr to an odd target (RVFI bug candidate)
- What: rvfi_stage_pc_wdata is loaded from branch_target_ex (raw BTALU sum) when pc_set; for jalr with
  rs1+imm odd, rvfi_pc_wdata[0] = 1 while the actual next PC (and the next rvfi_pc_rdata) has bit 0 = 0.
- Observable at: RVFI rvfi_pc_wdata vs next rvfi_pc_rdata
- Config: none
- Source: RTL-defined: rtl/ibex_core.sv:2084, rtl/ibex_core.sv:1000, rtl/ibex_ex_block.sv:98-101,
  rtl/ibex_if_stage.sv:288
- Edge: yes, of F-BTALU-003
- Status: ACTIVE
- Notes: not an architectural bug; the trace comparator must mask bit 0 or the RTL should clear it.

### F-BTALU-009: BTALU carry-out discarded (address wrap)
- What: Folded into F-BTALU-001 (bin CG-ISA-007.cp_wrap.yes): the BTALU carry-out is discarded so
  pc + imm / rs1 + imm wrap at 2^32 - the parent says "carry dropped"; the wrap stimuli are
  F-ISA-016/022/026.
- Observable at: see F-BTALU-001
- Config: see F-BTALU-001
- Source: RTL-defined: rtl/ibex_ex_block.sv:95-101 (unused_bt_carry)
- Edge: yes, of F-BTALU-001
- Status: FOLDED into F-BTALU-001 (bin CG-ISA-007.cp_wrap.yes)

### F-BTALU-010: Fetch fault at a branch/jump target: the transfer retires, the target traps
- What: CTI side of a fetch fault at the target: a taken branch, jal or jalr whose target is
  PMP-denied for execute or returns instr_err_i retires normally (rvfi_trap = 0) and issues exactly
  one fetch redirect to the target; the instruction access fault (cause 1, mtval = mepc = target) is
  attributed to the target instruction and is owned by F-EXC-003 (bus error), F-EXC-004 (PMP) and
  F-PMP-080 (target inside a denied region). A not-taken branch whose target would fault never
  fetches it and raises nothing.
- Observable at: RVFI (the CTI retires with rvfi_trap = 0; the next entry has rvfi_trap = 1 with
  rvfi_pc_rdata = target); instr_req_o/instr_addr_o (one request to the target; none for the
  not-taken case); csrr read-back of mcause (1) / mtval / mepc on rvfi_rd_wdata
- Config: PMP execute permission of the target page; instr_err_i from the TB memory for the target
  word
- Source: spec: rv32.adoc "Control Transfer Instructions" (norm:ia_fault_exc_on_target) |
  RTL-defined: rtl/ibex_controller.sv:849-862 (cause 1 / mtval on the target),
  rtl/ibex_if_stage.sv:426-430 (PMP and bus errors merged into if_instr_err of the fetched target),
  rtl/ibex_id_stage.sv:795-815 (single branch/jump set)
- Edge: yes, of F-BTALU-001
- Status: ACTIVE
- Notes: Canonical cause/CSR features: F-EXC-003, F-EXC-004, F-PMP-080; this entry keeps only the
  CTI-side observable (C-14 rule for fault clusters). PMP never gates instr_req_o
  (rtl/ibex_if_stage.sv:426-435): the denied target word is fetched on the bus and the fault is attached
  in the IF->ID register (X-23), so "one request to the target" holds for the PMP case too.

### F-BTALU-011: branch_set/jump_set issued once while the instruction is held for an outstanding WB access
- What: when a load/store is outstanding in WB, instr_executing_spec allows the speculative fetch redirect
  (branch_set_raw) but the branch cannot retire until the WB access completes; branch_jump_set_done_q
  prevents a second pc_set; if the WB access errors, the branch is killed and the exception taken (the
  redirected fetch is discarded).
- Observable at: instr_req_o/instr_addr_o (a single redirect for the CTI), RVFI (the branch retires
  after the load, or never when the access errors)
- Config: PMP / slow data memory responses
- Source: RTL-defined: rtl/ibex_id_stage.sv:795-815, rtl/ibex_id_stage.sv:1054-1062, rtl/ibex_id_stage.sv:844-845
- Edge: yes, of F-BTALU-001
- Status: ACTIVE

### F-BTALU-012: fence.i uses the BTALU for pc + 4
- What: Folded into F-ISA-030 (bin CG-ISA-008.cp_refetch.yes): fence.i computes pc + 4 on the BTALU
  (bt_b = IMM_B_INCR_PC) with jump_set + icache_inval in the first cycle - the parent's mechanism.
- Observable at: see F-ISA-030
- Config: see F-ISA-030
- Source: RTL-defined: rtl/ibex_decoder.sv:1405-1416, rtl/ibex_decoder.sv:710-723
- Edge: yes, of F-ISA-030
- Status: FOLDED into F-ISA-030 (bin CG-ISA-008.cp_refetch.yes)

### F-BTALU-013: Branch/jalr operands from the WB forwarding path or after a load hazard
- What: a branch comparing a register written by the previous ALU instruction uses the forwarded value;
  a branch/jalr reading a register being loaded (load in WB) stalls (stall_ld_hz) then uses the loaded
  value for both the condition and the jalr target.
- Observable at: RVFI rvfi_rs1_rdata, rvfi_pc_wdata, rvfi_ext_mcycle
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:1109-1120, rtl/ibex_id_stage.sv:373
- Edge: yes, of F-BTALU-003
- Status: ACTIVE

### F-BTALU-014: Back-to-back control transfers
- What: taken branch whose target is a jump; jal to a jalr; jalr to a taken branch; two consecutive
  taken branches; branch to a compressed instruction at an odd halfword within a word.
- Observable at: instr_req_o/instr_addr_o request sequence, RVFI rvfi_pc_rdata / rvfi_pc_wdata chain
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:681-688, rtl/ibex_id_stage.sv:920-942
- Edge: yes, of F-BTALU-001
- Status: ACTIVE

### F-BTALU-015: Branch/jump performance counter events
- What: Alias of F-PMC-040: branch-target-ALU perspective of NumBranchesTaken (mhpmcounter9 counts
  branch_set_i, the BT-ALU redirect, with data_ind_timing = 0), see canonical. Sized to one
  canonical (Critic L-7): NumBranches (F-PMC-039) and NumJumps (F-PMC-038) are not aliased here;
  CG-BTALU-001.cp_branch_inc / cp_tbranch_inc are operand-only counters in this area.
- Observable at: see F-PMC-040 (canonical)
- Config: see F-PMC-040
- Source: RTL-defined: rtl/ibex_controller.sv:681-688, rtl/ibex_id_stage.sv:934
- Edge: yes, of F-BTALU-001
- Status: ALIAS of F-PMC-040
- Notes: B17 (gen_bug_log.md; X-13): mhpmcounter8 counts a conditional branch once per cycle it waits in
  ID behind an outstanding WB access; counters 7 and 9 are exact (deduped by branch_jump_set_done_q).
  The waiting class is F-BTALU-016 / TP-BTALU-018; exact-count items require no WB wait.

### F-BTALU-016: NumBranches (mhpmcounter8) over-counts a branch waiting in ID behind an outstanding WB access (B17)
- What: Alias of F-PMC-039 (NumBranches), branch-target-ALU perspective of bug candidate B17: while a
  load/store is outstanding in WB a conditional branch stays in FIRST_CYCLE (instr_executing = 0) but
  perf_branch_o is asserted in every such cycle under instr_executing_spec, which lacks the
  ~outstanding_memory_access term, so mhpmcounter8 advances once per waiting cycle (1 + W per branch
  instead of the documented 1); branch_set / jump_set are deduped by branch_jump_set_done_q, so
  mhpmcounter9 (taken) and mhpmcounter7 (jumps) stay exact under the same wait (the F-BTALU-011
  mechanism). Counters 11/12 (mul/div wait) count the deferred-start cycles the same way (PMC area).
- Observable at: rvfi_ext_mhpmcounters[8 - MHPMCOUNTER_BASE] delta over the waiting branch and the csrr
  mhpmcounter8 pair around it (1 + W on the RTL; 1 per doc/03_reference/performance_counters.rst:41);
  dbus monitor timestamp of the response versus the branch's ID entry
- Config: mcountinhibit bit 8 clear; slow data-memory responses (knob:dmem_rvalid_delay)
- Source: doc: doc/03_reference/performance_counters.rst:41 ("Number of branches (conditional)") |
  RTL-defined: rtl/ibex_id_stage.sv:886-934 (perf_branch_o in FIRST_CYCLE under instr_executing_spec),
  rtl/ibex_id_stage.sv:1054-1057 (instr_executing_spec), rtl/ibex_id_stage.sv:866-869 (state advances
  only under instr_executing), rtl/ibex_id_stage.sv:795-815 (branch_jump_set_done_q dedup) | bug log:
  dv/auto_dv/docs/gen_bug_log.md B17 (rtl-arch BUG-09, fact-check X-13)
- Edge: yes, of F-BTALU-011
- Status: ALIAS of F-PMC-039
- Notes: added by fix 3 (T-053 fold); the carrying item TP-BTALU-018 is expected-fail (B17); the exact
  class (no WB wait) is TP-BTALU-015 and counter 7/9 exactness under a wait is TP-BTALU-011.

---------------------------------------------------------------------------------------------------


# 4.2 Areas CSR, PRV: Control and status registers; privilege modes M/U and mstatus semantics


Subagent output for dv-lead T-002. Areas: CSR (every implemented CSR, WARL legalisation,
illegal-access classes, RMW atomicity, counters, custom CSRs, CHERIoT CSR gates) and PRV
(privilege modes, mstatus stack, mret/dret/wfi/ecall, interrupt-enable rule).

Build configuration assumed (fixed, from ibex_configs.yaml `opentitan` and the brief): BaseIsa =
BaseIsaRV32IorCHERIoT with cheriot_enable_i tied to IbexMuBiOff, RV32B = RV32BOTEarlGrey,
RV32M = RV32MSingleCycle, DbgTriggerEn = 1, SecureIbex = 1 (=> DataIndTiming = 1,
rtl/ibex_core.sv:195), PMPEnable = 1, PMPNumRegions = 16, MHPMCounterNum = 10,
MHPMCounterWidth = 32, ICache = 1. Parameters that the DUT wrapper (gen_dut_top) must choose and
that change CSR behaviour: DummyInstructions (ibex_core default 0; ibex_top derives it as
SecureIbex, rtl/ibex_top.sv:214), DbgHwBreakNum (default 1), CsrMvendorId / CsrMimpId (default 0),
and the PMP reset parameters. See "Candidate owner questions". ShadowCSR is a localparam fixed to
0 inside ibex_core (rtl/ibex_core.sv:197), so no shadow-CSR checking exists in this DUT.

Observability conventions used below:
- "csrr readback" = rvfi_rd_wdata of a CSR read instruction (rvfi_insn shows the encoding).
- rvfi_trap = 1 on the CSR/SYSTEM instruction that raised an exception; rvfi_intr = 1 on the
  first handler instruction of an INTERRUPT or NMI only (EXC_PC_IRQ entries,
  rtl/ibex_core.sv:2403-2411; a synchronous-exception handler entry is the record after the
  trapped record, identified by rvfi_pc_rdata = mtvec BASE); rvfi_mode = current privilege (3 = M,
  0 = U) of the retiring instruction; rvfi_pc_wdata of a trap / mret / dret record = the next
  SEQUENTIAL fetch address, never the vector / mepc / dpc (rtl/ibex_core.sv:2084 captures pc_if in
  the DECODE cycle, the redirecting pc_set comes one cycle later in FLUSH; rtl-arch T-053 X-1): a
  redirect target is observed as the NEXT record's rvfi_pc_rdata; only branch/jump records carry
  their target in pc_wdata.
- RVFI extension fields present on ibex_core (rtl/ibex_core.sv:166-180): rvfi_ext_pre_mip,
  rvfi_ext_post_mip, rvfi_ext_mcycle, rvfi_ext_mhpmcounters[10], rvfi_ext_mhpmcountersh[10],
  rvfi_ext_ic_scr_key_valid, rvfi_ext_rf_wr_suppress, rvfi_ext_nmi, rvfi_ext_nmi_int,
  rvfi_ext_debug_mode, rvfi_ext_irq_valid. There are NO rvfi_csr_* ports on ibex_core; internal
  CSR flops are only reachable by hierarchical probe (cs_registers_i.<name>_q, probe P6: debug-only
  aid, never a checker input) or by a csrr; every checked observable below is the csrr read-back.
- Core ports: irq_pending_o (= |(mip & mie)), double_fault_seen_o, alert_major_internal_o,
  instr_req_o/instr_addr_o (trap-vector fetch address), core_busy_o (WFI sleep).

Status field (README_FIX_BRIEF rules 1-2): every block carries `- Status:` after `- Edge:`.
ACTIVE entries count in the completeness measure. `ALIAS of F-x` marks a duplicate stated from this
area's perspective (canonical entry named; one-line What). `FOLDED into F-x (bin ...)` marks an
edge entry that restated its parent (Critic C-12 patterns a-d); the named fcov_csr.md bin now
carries it. TP items may keep citing ALIAS/FOLDED IDs; traceability resolves them to the canonical
ID. Doc defects use the canonical D-numbers (D1..D21, D5 retired) and bug candidates the B-numbers
(B1..B18) of dv/auto_dv/docs/gen_bug_log.md v1d.

## Implemented CSR map

Access column is the behaviour as implemented in this configuration (cheriot Off), not the spec
label. "RO-zero" = reads 0, writes silently ignored (address is in a read/write range so no trap).
"RO" = reads a value, any write op traps (address in the csr[11:10] = 11 range).
"dbg" = read and write raise illegal instruction outside debug mode.

| Address | Name | Access | Reset value | WARL / legalisation notes | RTL line (read / write) |
|---|---|---|---|---|---|
| 0xF11 | mvendorid | RO | CsrMvendorId (0 default) | write op traps (RO range) | rtl/ibex_cs_registers.sv:422 |
| 0xF12 | marchid | RO | 0x0000_0016 (22) | cheriot Off selects CSR_MARCHID_VALUE | 424-426; rtl/ibex_pkg.sv:727 |
| 0xF13 | mimpid | RO | CsrMimpId (0 default) | | 428 |
| 0xF14 | mhartid | RO | hart_id_i (live input) | reads follow the input every cycle | 430 |
| 0xF15 | mconfigptr | RO | 0 | | 432; rtl/ibex_pkg.sv:735 |
| 0x300 | mstatus | RW | 0x0000_0080 | fields MIE[3] MPIE[7] MPP[12:11] MPRV[17] TW[21]; MPP 01/10 -> 00 (U); all other bits RO-zero | 435-442 / 774-787, 1052-1056 |
| 0x301 | misa | RO-hardwired | 0x4090_1104 | writes ignored, no trap (RW address, no write decode) | 452, 373-391, 188-202 |
| 0x304 | mie | RW | 0 | bits 3, 7, 11, 30:16 writable; rest RO-zero | 455-461 / 790, 1103-1106 |
| 0x305 | mtvec | RW | 0x0000_0001, then boot_addr_i[31:8],8'h01 on first fetch | bits 7:2 -> 0, MODE[1:0] -> 01 always | 469-475 / 736-743, 1170-1181 |
| 0x306 | mcounteren | RW (gated) | 0 | bits 12:0 writable except bit 1 (RO-zero); bits 31:13 RO-zero; write only when mcounteren_writable_i == IbexMuBiOn | 464 / 845, 1563-1571, 1737-1748 |
| 0x30A | menvcfg | RO-zero | 0 | | 449 |
| 0x310 | mstatush | RO-zero | 0 | | 445 |
| 0x31A | menvcfgh | RO-zero | 0 | | 449 |
| 0x320 | mcountinhibit | RW | 0 | bits 12:0 writable except bit 1; bits 31:13 RO-zero | 568 / 846, 1553-1561, 1709-1729 |
| 0x323-0x32C | mhpmevent3-12 | RO-hardwired | 1 << (n - 3) (n = 3..12: 0x1..0x200; D20, performance_counters.rst says 1 << n) | writes ignored, no trap | 569-578, 1602-1619 |
| 0x32D-0x33F | mhpmevent13-31 | RO-zero | 0 | | 569-578, 1615-1618 |
| 0x340 | mscratch | RW | 0 | full 32 bits; write does not flush pipeline | 466 / 792, 1121-1132 |
| 0x341 | mepc | RW | 0 | bit 0 RO-zero; bit 1 writable; write does not flush pipeline | 478-484 / 729, 796-797, 1089-1100 |
| 0x342 | mcause | RW (D3: doc marks R) | 0 | storage {irq_int, irq_ext, code[4:0]}; write: irq_ext = wdata[31:30]==10, irq_int = wdata[31:30]==11, code = wdata[4:0]; read: bit31 = irq_ext or irq_int, bits 30:5 = all ones iff irq_int else 0 | 487-489 / 731-733, 1135-1146 |
| 0x343 | mtval | RW | 0 | full 32 bits | 492 / 735, 1149-1160 |
| 0x344 | mip | RO (writes ignored, no trap) | follows irq inputs (D1: not masked by mie) | bits 3, 7, 11, 30:16 = irq_software_i, irq_timer_i, irq_external_i, irq_fast_i[14:0]; NOT masked by mie | 408-412, 495-501 |
| 0x3A0-0x3A3 | pmpcfg0-3 | RW (PMP part) | PMPRstCfg param | see PMP part | 525-532, 1419-1470 |
| 0x3B0-0x3BF | pmpaddr0-15 | RW (PMP part) | PMPRstAddr param | see PMP part | 533-548, 1474-1494 |
| 0x5A8 | scontext | RO-zero (S-level address: U-mode trap) | 0 | | 656-659 |
| 0x747 | mseccfg | RW | PMPRstMsecCfg (0) | MML/MMWP sticky-1, RLB cannot be set while a locked region exists; bits 31:3 RO-zero | 503-513, 1502-1527 |
| 0x757 | mseccfgh | RO-zero | 0 | | 515-522 |
| 0x7A0 | tselect | RW (write effective in debug mode only) | 0 | value >= DbgHwBreakNum -> DbgHwBreakNum-1; with 1 trigger always 0 | 636-639, 1775, 1785-1786, 1837 |
| 0x7A1 | tdata1 | RW (write effective in debug mode only) | 0x2800_1048 (D4: doc says 0x2800_1000) | only bit 2 (execute) writable | 640-643, 1777-1778, 1789, 1848-1864 |
| 0x7A2 | tdata2 | RW (write effective in debug mode only) | 0 | | 644-647, 1779-1780, 1867 |
| 0x7A3 | tdata3 | RO-zero | 0 | | 648-651 |
| 0x7A8 | mcontext | RO-zero | 0 | | 652-655 |
| 0x7AA | mscontext | RO-zero | 0 | | 660-663 |
| 0x7B0 | dcsr | RW, dbg | 0x4000_0003 | xdebugver RO 4; prv 01/10 -> 00; cause RO; stepie, stopcount, stoptime, mprven, nmip, bits 5, 14, 27:16 RO-zero; ebreakm[15], ebreaks[13] (B15: must read 0 without S-mode), ebreaku[12], step[2], prv[1:0] writable | 550-553 / 810-835, 1184-1201 |
| 0x7B1 | dpc | RW, dbg | 0 | bit 0 RO-zero | 554-557 / 746, 838 |
| 0x7B2 | dscratch0 | RW, dbg | 0 | | 558-561 / 840 |
| 0x7B3 | dscratch1 | RW, dbg | 0 | | 562-565 / 841 |
| 0x7C0 | cpuctrlsts | RW | 0 | [0] icache_enable, [1] data_ind_timing, [2] dummy_instr_en*, [5:3] dummy_instr_mask*, [6] sync_exc_seen, [7] double_fault_seen, [8] ic_scr_key_valid (RO); bits 31:9 RO-zero (* writable only if DummyInstructions = 1) | 666-670 / 874-877, 1888-1984 |
| 0x7C1 | secureseed | write-only (reads 0) | 0 | write pulses dummy_instr_seed_en_o (DummyInstructions = 1 only) | 673-675 / 1914-1915 |
| 0xB00 / 0xB80 | mcycle / mcycleh | RW | 0 | 64-bit; write wins over increment | 580-604 / 848-872, 1622-1633 |
| 0xB02 / 0xB82 | minstret / minstreth | RW | 0 | 64-bit; writer instruction not counted | 1637-1658; rtl/ibex_id_stage.sv:1213-1220 |
| 0xB03-0xB0C / 0xB83-0xB8C | mhpmcounter3-12 / h | RW / RO-zero | 0 | 32-bit counters: h half reads 0, writes to h ignored | 1667-1707; rtl/ibex_counter.sv:86-98 |
| 0xB0D-0xB1F / 0xB8D-0xB9F | mhpmcounter13-31 / h | RO-zero | 0 | writes ignored, no trap | 1699-1706, 1716-1718 |
| 0xBC1 | mshwm | illegal (cheriot Off) | n/a | cheriot-out-of-scope candidate | 678-684, 879-880 |
| 0xBC2 | mshwmb | illegal (cheriot Off) | n/a | cheriot-out-of-scope candidate | 686-692, 881-882 |
| 0xBC4 | cdbg_ctrl | illegal (cheriot Off) | n/a | cheriot-out-of-scope candidate | 694-700, 883-884 |
| 0xC00 / 0xC80 | cycle / cycleh | RO; U-mode needs mcounteren[0] | alias of mcycle | | 607-633 |
| 0xC02 / 0xC82 | instret / instreth | RO; U-mode needs mcounteren[2] | alias of minstret | | 607-633 |
| 0xC03-0xC0C / 0xC83-0xC8C | hpmcounter3-12 / h | RO; U-mode needs mcounteren[n] | alias | | 607-633 |
| 0xC0D-0xC1F / 0xC8D-0xC9F | hpmcounter13-31 / h | RO-zero in M; always illegal in U (mcounteren bit not implemented) | 0 | | 607-633, 1731-1735 |
| 0xC01 / 0xC81 | time / timeh | not implemented -> illegal in every mode | n/a | | 702-704 (default) |
| any other | - | illegal instruction | n/a | | 702-704 |

Illegal-access classes (rtl/ibex_cs_registers.sv:402-406): unimplemented address (illegal_csr),
write op to csr[11:10] == 11 (illegal_csr_write), csr[9:8] > current privilege (illegal_csr_priv),
debug-only CSR outside debug mode (illegal_csr_dbg). All four OR into illegal_csr_insn_o which
feeds illegal_insn_o (rtl/ibex_id_stage.sv:610-611), suppresses the rd write
(rtl/ibex_id_stage.sv:463) and the CSR write (rtl/ibex_cs_registers.sv:1020-1023), and produces
mcause 2 with mtval = instruction bits (rtl/ibex_controller.sv:864-869).

## Features: CSR

### F-CSR-001: CSR instruction operation classes and single-cycle read-modify-write
- What: SYSTEM funct3 001/010/011 (csrrw/csrrs/csrrc) and 101/110/111 (csrrwi/csrrsi/csrrci) decode
  to CSR_OP_WRITE/SET/CLEAR with rs1 or zero-extended uimm[4:0] as operand. The CSR is read and
  written in the same cycle: rd receives the pre-write value, the CSR receives wdata (WRITE), rdata
  | wdata (SET) or rdata & ~wdata (CLEAR). The write commits when the instruction leaves ID
  (csr_op_en = csr_access & instr_executing & instr_id_done).
- Observable at: csrr read-back on rvfi_rd_wdata: the op's own rd returns the pre-write value and
  the following csrr returns the written value after legalisation; rvfi_insn gives the op class. The
  internal csr_wdata_int is not an observable: probe candidate P6 (probe register entry needed; P6
  is accepted only as a debug-only aid, never a checker input,
  dv/auto_dv/docs/gen_probe_register.md).
- Config: none.
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/zicsr.adoc "CSR Instructions" | RTL-defined:
  rtl/ibex_decoder.sv:759-784, rtl/ibex_cs_registers.sv:1001-1011, rtl/ibex_id_stage.sv:747-749
- Edge: no
- Status: ACTIVE
- Notes: The decoder maps funct3[1:0] only; the immediate form is distinguished by instr[14]
  (rtl/ibex_decoder.sv:765-767, 1433-1438).

### F-CSR-002: csrrs/csrrc with rs1 = x0 and csrrsi/csrrci with uimm = 0 are pure reads
- What: The decoder converts SET/CLEAR with rs1 field == 0 to CSR_OP_READ. No CSR write occurs, no
  write side effect (no seed pulse, no counter reload), no pipeline flush, and no illegal
  instruction for a read-only CSR address.
- Observable at: rvfi_rd_wdata (value returned), rvfi_trap = 0 on csrr of 0xF11..0xF15 / 0xC00, no
  bubble after the instruction (rvfi_order/timing), CSR unchanged on readback.
- Config: none.
- Source: spec: zicsr.adoc "CSR Instructions" (table "Conditions determining whether a CSR
  instruction reads or writes") | RTL-defined: rtl/ibex_decoder.sv:250-259,
  rtl/ibex_cs_registers.sv:1011, rtl/ibex_id_stage.sv:595-597
- Edge: yes, of F-CSR-001
- Status: ACTIVE
- Notes: Canonical entry; aliases: F-ISA-044, F-CSR-012.

### F-CSR-003: csrrw/csrrwi with rs1 = x0 / uimm = 0 writes zero
- What: WRITE with a zero operand is a real write of 0 (not suppressed), so it traps on read-only
  addresses and flushes the pipeline.
- Observable at: csrr readback = 0 for mscratch; rvfi_trap = 1 for csrrw x0, mvendorid, x0.
- Config: none.
- Source: spec: zicsr.adoc "CSR Instructions" (csrrw with rs1 = x0 attempts to write zero) |
  RTL-defined: rtl/ibex_decoder.sv:770, rtl/ibex_cs_registers.sv:1003
- Edge: yes, of F-CSR-001
- Status: ACTIVE
- Notes: Canonical entry; aliases: F-ISA-045, F-CSR-013.

### F-CSR-004: csrrw/csrrwi with rd = x0 still reads internally; no CSR has read side effects
- What: Folded into F-CSR-001: rd = x0 is one value of the parent's rd field with the parent's
  outcome (the CSR receives wdata; no implemented CSR has a read side effect, so the spec's "shall
  not read" rule has no observable content) (v2 edge rule, second pass; Critic M-9); carried by the
  parent's rd = x0 write bins.
- Source: spec: zicsr.adoc "CSR Instructions" (csrrw rd = x0) | RTL-defined:
  rtl/ibex_cs_registers.sv:415-717 (read mux is unconditional)
- Edge: yes, of F-CSR-001
- Status: FOLDED into F-CSR-001 (bin CG-CSR-001.cr_rd_x0_write.csrrw_rdx0_rw_m, csrrwi_rdx0_rw_m, csrrs_rdx0_rw_m, csrrc_rdx0_rw_m)

### F-CSR-005: SYSTEM with funct3 = 100 is an illegal instruction
- What: funct3 = 100 is not a CSR operation; decoder sets csr_illegal, illegal instruction exception
  (mcause 2, mtval = instruction).
- Observable at: rvfi_trap = 1 + csrr read-back of mcause (2) / mtval (encoding) on rvfi_rd_wdata.
- Config: none.
- Source: spec: zicsr.adoc "CSR Instructions" (encoding table) | RTL-defined:
  rtl/ibex_decoder.sv:769-774, 783
- Edge: yes, of F-CSR-001
- Status: ACTIVE
- Notes: Canonical entry; alias: F-ISA-046.

### F-CSR-006: CSR write causes a pipeline flush (except mscratch and mepc)
- What: Any executed CSR write op (WRITE/SET/CLEAR with csr_op_en) to an address other than mscratch
  or mepc raises csr_pipe_flush; the controller enters FLUSH and refetches the next instruction, so
  the following instruction observes the new CSR state (mstatus.MIE, mie, mcountinhibit,
  cpuctrlsts.icache_enable, PMP, mtvec).
- Observable at: instr_req_o/instr_addr_o refetch of PC+4/PC+2 after the CSR write; multi-cycle
  bubble in rvfi_valid; interrupt taken before the next instruction when MIE is set with a pending
  irq.
- Config: none.
- Source: spec: zicsr.adoc "CSR Access Ordering"; machine.adoc "Machine Interrupt (mip and mie)
  Registers" (evaluate interrupt conditions immediately after a CSR write) | RTL-defined:
  rtl/ibex_id_stage.sv:590-597, rtl/ibex_controller.sv:287, 664-679, 816-820
- Edge: no
- Status: ACTIVE

### F-CSR-007: mscratch and mepc writes do not flush; back-to-back write/read still coherent
- What: Folded into F-CSR-006: the parent's own exception clause ("except mscratch and mepc"); the
  back-to-back write/read coherence is the negative of the parent's refetch observable (v2 edge
  rule, second pass; Critic M-9); carried by the parent's family x gap bins.
- Source: RTL-defined: rtl/ibex_id_stage.sv:593
- Edge: yes, of F-CSR-006
- Status: FOLDED into F-CSR-006 (bin CG-CSR-012.cr_fam_gap.mscratch_g1, mepc_g1; CG-CSR-012.cr_fam_next.mscratch_csr_rd_same, mepc_csr_rd_same)

### F-CSR-008: CSR write in ID is cancelled when the instruction in WB raises a load/store error
- What: A CSR instruction waits in ID while a memory access is outstanding (instr_executing includes
  ~outstanding_memory_access). If that access returns an error, wb_exception kills the ID
  instruction: no CSR write, no rd write, and the CSR instruction is re-executed after the handler
  returns. mepc = PC of the load/store (csr_save_wb) and mtval = the faulting data address
  (rtl/ibex_cs_registers.sv:918-922), so a killed write to mepc or mtval is not distinguishable
  from the trap's own write (TP-CSR-008 excludes both).
- Observable at: CSR unchanged on readback inside the handler, rvfi_trap on the load/store, csrr
  mepc = load/store PC, the CSR instruction retires later with rvfi_order after mret.
- Config: PMP or bus error source to make the access fail.
- Source: spec: zicsr.adoc "CSR Access Ordering" | RTL-defined: rtl/ibex_id_stage.sv:1033-1036,
  1059-1062, 747-749; rtl/ibex_controller.sv:833-840
- Edge: yes, of F-CSR-006
- Status: ACTIVE

### F-CSR-009: Access to an unimplemented CSR address raises illegal instruction
- What: Any address not in the read mux raises illegal_csr (read or write), giving mcause 2, mtval =
  the CSR instruction encoding, mepc = its PC; rd not written; no CSR state changes; the instruction
  is not counted in minstret.
- Observable at: rvfi_trap = 1 + csrr read-back of mcause (2) / mtval (encoding) / mepc (pc) on
  rvfi_rd_wdata; the rd register reads back unchanged and the minstret read-back excludes the
  trapping access (folded F-CSR-103).
- Config: privilege mode (M or U; both trap).
- Source: spec: tools/specs/riscv-isa-manual/src/priv/csrs.adoc "CSR Address Mapping Conventions"
  (non-existent CSR accesses are reserved) | doc: doc/03_reference/cs_registers.rst "Time Registers
  (time(h))" | RTL-defined: rtl/ibex_cs_registers.sv:702-704, 405-406; rtl/ibex_id_stage.sv:463,
  610-611, 1218-1219; rtl/ibex_controller.sv:864-869
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-CSR-010 (explicit hole list, CG-CSR-014.cp_range bins) and F-CSR-103
  (rd write suppressed, minstret exclusion: rtl/ibex_id_stage.sv:463, 1218-1219).

### F-CSR-010: Address holes inside implemented ranges are illegal
- What: Folded into F-CSR-009: the explicit hole list (0x302/0x303, 0x307-0x309, 0x30B-0x30F,
  0x311-0x319, 0x31B-0x31F, 0x321/0x322, 0x345-0x39F, 0x3A4-0x3AF, 0x3C0-0x5A7, 0x5A9-0x746,
  0x748-0x756, 0x758-0x79F, 0x7A4-0x7A7, 0x7A9, 0x7AB-0x7AF, 0x7B4-0x7BF, 0x7C2-0x7FF, 0x800-0xAFF,
  0xB01, 0xB20-0xB7F, 0xB81, 0xBA0-0xBBF, 0xBC0, 0xBC3, 0xBC5-0xBFF, 0xC01, 0xC81, 0xC20-0xC7F,
  0xCA0-0xF10, 0xF16-0xFFF, 0x000-0x2FF; 0x800-0xAFF, 0xB20-0xB7F and 0xBA0-0xBBF added per the
  rtl-arch T-053 note on TP-CSR-010) is the parent's own enumeration with the same trap outcome;
  carried by every CG-CSR-014.cp_range bin and TP-CSR-010.
- Edge: yes, of F-CSR-009
- Status: FOLDED into F-CSR-009 (bin CG-CSR-014.cp_range.r302_303)

### F-CSR-011: Write op to a read-only address range raises illegal instruction (also in M-mode)
- What: csr_addr[11:10] == 11 with a write op (WRITE/SET/CLEAR) sets illegal_csr_write. Applies to
  0xF11-0xF15 and 0xC00-0xC9F and to every unimplemented 0xC00-0xFFF address.
- Observable at: rvfi_trap = 1 + csrr read-back of mcause (2) / mtval (encoding) on rvfi_rd_wdata;
  the CSR and rd read back unchanged.
- Config: none.
- Source: spec: csrs.adoc "CSR Address Mapping Conventions" (attempts to write a read-only CSR raise
  illegal-instruction) | RTL-defined: rtl/ibex_cs_registers.sv:404, 1011
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-CSR-057 (write op to a 0xC00-0xC9F alias traps in M-mode,
  CG-CSR-005.cr_wr_alias).

### F-CSR-012: csrrs/csrrc x0 (and csrrsi/csrrci uimm = 0) on a read-only CSR is a legal read
- What: Alias of F-CSR-002: read-only-address perspective (the demoted READ raises no
  illegal_csr_write), see canonical.
- Edge: yes, of F-CSR-011
- Status: ALIAS of F-CSR-002

### F-CSR-013: csrrw rd = x0 / csrrwi with zero immediate to a read-only CSR still traps
- What: Alias of F-CSR-003: read-only-address perspective (csrrw x0 / csrrwi 0 is still a write and
  traps on 0xF11-0xF15 and 0xC00-0xC9F), see canonical.
- Edge: yes, of F-CSR-011
- Status: ALIAS of F-CSR-003

### F-CSR-014: Privilege check: csr[9:8] above the current mode raises illegal instruction
- What: illegal_csr_priv = csr_addr[9:8] > priv_lvl_q. In U-mode (00) every address with csr[9:8] !=
  00 traps on read and write: all M-level CSRs (0x3xx, 0x7xx, 0xBxx, 0xFxx), S-level (0x1xx, 0x5xx,
  0x9xx, 0xDxx incl. scontext 0x5A8) and H-level (0x2xx, 0x6xx, 0xAxx, 0xExx). In M-mode the check
  never fires.
- Observable at: rvfi_trap = 1 with rvfi_mode = 0; csrr read-back of mcause (2) and mstatus.MPP (00)
  in the handler on rvfi_rd_wdata.
- Config: privilege mode (enter U via mret with MPP = 0).
- Source: spec: csrs.adoc "CSR Address Mapping Conventions" (attempts to access a CSR without
  sufficient privilege raise illegal-instruction) | RTL-defined: rtl/ibex_cs_registers.sv:403
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-CSR-015 (U-mode read of a harmless M-level CSR traps; only the
  0xC00-0xC9F aliases are readable from U, per F-CSR-053) and F-PRV-034 (no writable CSR exists in
  U-mode: every write form traps by the priv or write_ro class, CG-CSR-001.cr_iclass_priv.wro_u).

### F-CSR-015: U-mode read of an M-level read-only CSR (e.g. mhartid, mcycle) traps
- What: Folded into F-CSR-014: U-mode reads of mhartid/mcycle/mstatus are rows of the parent's
  csr[9:8] rule with the same trap; the readable 0xC00 alias under mcounteren is F-CSR-053.
- Edge: yes, of F-CSR-014
- Status: FOLDED into F-CSR-014 (bin CG-CSR-001.cr_priv_aclass_trap.u_info_ro_trap)

### F-CSR-016: Multiple illegal-access classes on one instruction yield one illegal exception
- What: U-mode write to 0xF11 (priv + RO), U-mode access to dcsr (priv + dbg), M-mode write to
  unimplemented 0xF16 (unimplemented + RO): the OR of classes produces a single mcause 2 trap with
  the same mtval/mepc as any single class.
- Observable at: rvfi_trap = 1 exactly once per instruction (the next instruction retires once,
  after mret); csrr read-back of mcause (2), mtval (encoding), mepc (pc) on rvfi_rd_wdata.
- Config: privilege mode.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:405-406
- Edge: yes, of F-CSR-014
- Status: ACTIVE

### F-CSR-017: Debug-only CSRs (dcsr, dpc, dscratch0, dscratch1) trap outside debug mode
- What: Alias of F-DBG-050: CSR-area perspective, see canonical. Corrected fact: only 0x7B0-0x7B3
  (dcsr, dpc, dscratch0, dscratch1) set dbg_csr, so only they raise illegal instruction outside
  debug mode (rtl/ibex_cs_registers.sv:402, 550-565); tselect/tdata1/tdata2/tdata3 (0x7A0-0x7A3) are
  legal from M-mode with DbgTriggerEn = 1 (reads succeed, writes are dropped, :636-651, 1775-1781;
  csrs.adoc:60-63) - doc defect D12: debug.rst:54-55 says all of them are Debug-Mode only.
- Edge: no
- Status: ALIAS of F-DBG-050

### F-CSR-018: 0x7B4-0x7BF in debug mode is illegal (unimplemented), 0x7B0-0x7B3 legal
- What: Only four debug CSRs exist; the rest of the debug-only range falls to the default branch
  even inside debug mode.
- Observable at: rvfi_trap = 1 with rvfi_ext_debug_mode = 1 and the next record's rvfi_pc_rdata =
  DmExceptionAddr (X-1; instr_addr_o also fetches DmExceptionAddr, the icache is forced off in debug
  mode) for csrr 0x7B4 in debug mode; outside debug mode the same access traps to mtvec (the next
  record's rvfi_pc_rdata = mtvec.BASE; instr_addr_o shows it only with the icache disabled, X-21).
- Config: debug mode.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:702-704
- Edge: yes, of F-CSR-009
- Status: ACTIVE
- Notes: Parent re-pointed from F-CSR-017 (now ALIAS of F-DBG-050) to the base unimplemented-address
  rule F-CSR-009; the edge is the debug-mode trap target.

### F-CSR-019: mvendorid, marchid, mimpid, mconfigptr constant read values
- What: mvendorid = CsrMvendorId (0), marchid = 22 (0x16, cheriot Off), mimpid = CsrMimpId (0),
  mconfigptr = 0. Reads in M-mode return these constants; any write op traps (F-CSR-011).
- Observable at: rvfi_rd_wdata.
- Config: none.
- Source: spec: machine.adoc "Machine Vendor ID (mvendorid) Register", "Machine Architecture ID
  (marchid) Register", "Machine Implementation ID (mimpid) Register", "Machine Configuration Pointer
  (mconfigptr) Register" | doc: cs_registers.rst "Machine Vendor ID (mvendorid)", "Machine
  Architecture ID (marchid)", "Machine Implementation ID (mimpid)" | RTL-defined:
  rtl/ibex_cs_registers.sv:422-432, rtl/ibex_pkg.sv:727-735
- Edge: no
- Status: ACTIVE
- Notes: marchid MSB is 0 (open-source ID) as the spec requires. Doc defect D15: the
  cs_registers.rst CSR table omits mconfigptr (and mcounteren, mstatush, menvcfg, menvcfgh); the RTL
  implements them. Canonical entry; alias: F-SEC-037.

### F-CSR-020: mhartid returns the live hart_id_i input
- What: csr_rdata = hart_id_i with no register; a change on the input is visible on the next read.
- Observable at: rvfi_rd_wdata vs. driven hart_id_i.
- Config: none (hart_id_i is a DUT input).
- Source: spec: machine.adoc "Hart ID (mhartid) Register" | doc: cs_registers.rst "Hardware Thread
  ID (mhartid)" | RTL-defined: rtl/ibex_cs_registers.sv:430
- Edge: no
- Status: ACTIVE
- Notes: The TB should randomize hart_id_i per test (incl. 0 and 0xFFFF_FFFF) but hold it stable
  within a test; the spec requires one hart with ID 0 only at system level. Canonical entry; alias:
  F-RST-005.

### F-CSR-021: misa is hardwired to 0x4090_1104; writes are ignored without trap
- What: MXL = 1 (bit 30), X (bit 23, non-standard bitmanip sub-extensions), U (bit 20), M (bit 12),
  I (bit 8), C (bit 2). E, S, N, F, D, A, B = 0. There is no write decode for misa, so csrrw misa
  completes (pipeline flush) and the value is unchanged.
- Observable at: rvfi_rd_wdata = 0x4090_1104 before and after any write; rvfi_trap = 0.
- Config: none.
- Source: spec: machine.adoc "Machine ISA (misa) Register" | doc: cs_registers.rst "Machine ISA
  Register (misa)" | RTL-defined: rtl/ibex_cs_registers.sv:178-202, 373-391, 452
- Edge: no
- Status: ACTIVE
- Notes: misa.B (bit 1) is 0 although RV32BOTEarlGrey implements Zba/Zbb/Zbs; the spec allows a
  WARL/hardwired report, so this is a documentation point, not a bug. The X bit is set because of
  the non-ratified bitmanip sub-extensions (RV32BExtra), independent of CHERIoT. Carries the folded
  F-CSR-022 (all-ones / all-zeros writes read back unchanged, CG-CSR-002.cr_csr_wpat.misa_all1 /
  misa_all0).

### F-CSR-022: misa write of all-ones or all-zeros reads back unchanged
- What: Folded into F-CSR-021: csrrs/csrrc misa, -1 leaving 0x4090_1104 is the parent's
  write-ignored rule at the all-ones / all-zeros patterns (bins misa_all1, misa_all0).
- Edge: yes, of F-CSR-021
- Status: FOLDED into F-CSR-021 (bin CG-CSR-002.cr_csr_wpat.misa_all1)

### F-CSR-023: mstatus implemented fields, read/write and reset value 0x0000_0080
- What: MIE[3], MPIE[7], MPP[12:11], MPRV[17], TW[21] are stored; all other bits read 0. Reset: MIE
  = 0, MPIE = 1, MPP = U (00), MPRV = 0, TW = 0. Writes set all five fields at once.
- Observable at: rvfi_rd_wdata after reset = 0x0000_0080; readback after write.
- Config: none.
- Source: spec: machine.adoc "Privilege and Global Interrupt-Enable Stack in mstatus register",
  "Memory Privilege in mstatus Register", "Virtualization Support in mstatus Register", "Reset" |
  doc: cs_registers.rst "Machine Status (mstatus)" | RTL-defined: rtl/ibex_cs_registers.sv:204-210,
  435-442, 774-787, 1052-1056
- Edge: no
- Status: ACTIVE
- Notes: Spec requires only MIE and MPRV to reset to 0; MPIE = 1 and MPP = U at reset are
  Ibex-defined. SIE/SPIE/SPP/SUM/MXR/TVM/TSR/FS/VS/XS/UBE/SD read-only 0 as required for a hart
  without S-mode, FP or vector. Carries the folded F-CSR-025 (all-ones write reads back 0x0022_1888,
  CG-CSR-002.cr_csr_wpat.mstatus_all1) and F-PRV-035 (TW and MPRV writable independently,
  CG-CSR-002.cr_mst_fields.mprv_tw / tw_only / mprv_only).

### F-CSR-024: mstatus.MPP WARL: values 01 and 10 are legalised to 00 (U)
- What: A write with MPP = 01 (S) or 10 (H) stores PRIV_LVL_U; a following mret goes to U-mode. MPP
  = 11 stores M.
- Observable at: csrr mstatus readback bits 12:11 = 00; rvfi_mode = 0 after the mret.
- Config: none.
- Source: spec: machine.adoc "Privilege and Global Interrupt-Enable Stack in mstatus register" (xPP
  WARL, only implemented modes) | doc: cs_registers.rst "Machine Status (mstatus)" | RTL-defined:
  rtl/ibex_cs_registers.sv:783-786
- Edge: yes, of F-CSR-023
- Status: ACTIVE
- Notes: Doc defect D2: cs_registers.rst:138 says an unsupported MPP value 'will be interpreted as
  Machine Mode'; the RTL converts it to U-mode (rtl/ibex_cs_registers.sv:783-786). Both are
  spec-legal WARL choices; the checker follows the RTL (U) and TP-CSR-024 is `pass (doc mismatch
  D2)`. Canonical entry of the MPP-legalisation cluster (Section 3; F-EXC-053 is a member).

### F-CSR-025: mstatus write of all-ones reads back 0x0022_1888
- What: Folded into F-CSR-023: 0xFFFF_FFFF -> 0x0022_1888 is the parent's field list (bits 3, 7, 11,
  12, 17, 21) at the all-ones pattern.
- Edge: yes, of F-CSR-023
- Status: FOLDED into F-CSR-023 (bin CG-CSR-002.cr_csr_wpat.mstatus_all1)

### F-CSR-026: Setting mstatus.MIE with an enabled interrupt pending takes the interrupt before the
next instruction
- What: The CSR write flushes the pipeline; the controller re-evaluates handle_irq in DECODE and
  enters IRQ_TAKEN with mepc = PC of the instruction following the csrrs.
- Observable at: rvfi_intr on the first handler instruction; csrr mepc = csrrs PC + 4; no
  instruction between csrrs and the handler retires.
- Config: mie bit set, irq_* input high.
- Source: spec: machine.adoc "Machine Interrupt (mip and mie) Registers" (evaluated immediately
  following an explicit write to mstatus) | RTL-defined: rtl/ibex_id_stage.sv:595-597,
  rtl/ibex_controller.sv:490, 498-500, 704-721
- Edge: yes, of F-CSR-023
- Status: ACTIVE
- Notes: Canonical entry; alias: F-IRQ-059.

### F-CSR-027: mstatush (0x310) reads 0 and ignores writes
- What: No storage, no trap (address is MRW). MBE = 0 (little endian only).
- Observable at: rvfi_rd_wdata = 0 after csrrw mstatush, -1; rvfi_trap = 0.
- Config: none.
- Source: spec: machine.adoc "Machine Status (mstatus and mstatush) Registers", "Endianness Control
  in mstatus and mstatush Registers" | RTL-defined: rtl/ibex_cs_registers.sv:445
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D15: the cs_registers.rst CSR table omits mstatush (also mcounteren, menvcfg,
  menvcfgh, mconfigptr).

### F-CSR-028: menvcfg (0x30A) and menvcfgh (0x31A) read 0 and ignore writes
- What: No menvcfg feature (FIOM, PBMTE, STCE, CBIE/CBCFE/CBZE) is implemented; both halves are
  read-only zero without trap.
- Observable at: rvfi_rd_wdata = 0, rvfi_trap = 0.
- Config: none.
- Source: spec: machine.adoc "Machine Environment Configuration (menvcfg) Register" | RTL-defined:
  rtl/ibex_cs_registers.sv:449
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D15: the cs_registers.rst CSR table omits menvcfg and menvcfgh.

### F-CSR-029: mie implemented bits (MSIE 3, MTIE 7, MEIE 11, fast 30:16) and reset 0
- What: mie stores 18 bits; a write updates all of them; the qualified interrupt vector irqs_o = mip
  & mie drives irq_pending_o and the controller.
- Observable at: rvfi_rd_wdata; irq_pending_o level change one cycle after the write.
- Config: none.
- Source: spec: machine.adoc "Machine Interrupt (mip and mie) Registers" | doc: cs_registers.rst
  "Machine Interrupt Enable Register (mie)" | RTL-defined: rtl/ibex_cs_registers.sv:455-461, 790,
  1103-1118, 1044-1045
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-CSR-030 (all-ones write reads back 0x7FFF_0888,
  CG-CSR-002.cr_csr_wpat.mie_all1).

### F-CSR-030: mie write of all-ones reads back 0x7FFF_0888
- What: Folded into F-CSR-029: 0xFFFF_FFFF -> 0x7FFF_0888 is the parent's implemented-bit set (3, 7,
  11, 30:16) at the all-ones pattern.
- Edge: yes, of F-CSR-029
- Status: FOLDED into F-CSR-029 (bin CG-CSR-002.cr_csr_wpat.mie_all1)

### F-CSR-031: mie write is visible to irq_pending_o and to WFI wake on the next cycle
- What: irq_pending_o = |(mip & mie_q) is combinational on the flop output; enabling a bit whose irq
  input is already high raises irq_pending_o the cycle after the write. Disabling all bits in the
  cycle an interrupt becomes pending prevents the interrupt.
- Observable at: irq_pending_o (rises one cycle after the write's commit edge, i.e. one cycle
  before the write's RVFI record, rtl-arch T-053 row TP-CSR-031), rvfi_intr on the next retired
  instruction.
- Config: mstatus.MIE (M-mode) or U-mode.
- Source: spec: machine.adoc "Machine Interrupt (mip and mie) Registers" | RTL-defined:
  rtl/ibex_cs_registers.sv:1044-1045
- Edge: yes, of F-CSR-029
- Status: ACTIVE

### F-CSR-032: mip is read-only and mirrors the raw irq inputs, not masked by mie
- What: mip[3] = irq_software_i, mip[7] = irq_timer_i, mip[11] = irq_external_i, mip[30:16] =
  irq_fast_i[14:0], purely combinational; all other bits 0. NMI is not visible.
- Observable at: rvfi_rd_wdata of csrr mip vs. driven irq inputs; rvfi_ext_pre_mip /
  rvfi_ext_post_mip.
- Config: none (mie does not affect the read value).
- Source: spec: machine.adoc "Machine Interrupt (mip and mie) Registers" (meip/mtip/msip read-only
  in mip; NMI not visible via mip) | doc: cs_registers.rst "Machine Interrupt Pending Register
  (mip)" | RTL-defined: rtl/ibex_cs_registers.sv:408-412, 495-501
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D1: cs_registers.rst:246 says a mip bit reads one only 'if the interrupt is
  enabled in the mie CSR'; the RTL reads the raw input regardless of mie
  (rtl/ibex_cs_registers.sv:408-412). The RTL matches the priv spec; the checker follows the RTL and
  TP-CSR-032 is `pass (doc mismatch D1)`. Canonical mip entry (Section 3 cluster).

### F-CSR-033: Writes to mip are ignored without trap (but still flush the pipeline)
- What: 0x344 is an MRW address so csrrw/csrrs/csrrc mip do not trap; there is no write decode, so
  mip is unchanged (it is combinational anyway). The write op still triggers csr_pipe_flush.
- Observable at: rvfi_trap = 0; csrr mip unchanged; refetch bubble on instr_req_o.
- Config: none.
- Source: spec: csrs.adoc "CSR Address Mapping Conventions" (writes to read-only bits ignored) |
  RTL-defined: rtl/ibex_cs_registers.sv:772-887 (no CSR_MIP case), rtl/ibex_id_stage.sv:595-597
- Edge: yes, of F-CSR-032
- Status: ACTIVE
- Notes: Canonical for the IRQ alias F-IRQ-005 (M-10 pass).

### F-CSR-034: mip read samples the irq input level of the read cycle
- What: With an irq input toggling, csrr mip returns the level in the cycle the read mux is sampled
  (the cycle the CSR instruction is in ID). rvfi_ext_pre_mip captures mip when the instruction
  enters ID and rvfi_ext_post_mip when it retires.
- Observable at: rvfi_rd_wdata vs rvfi_ext_pre_mip/rvfi_ext_post_mip.
- Config: none.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:408-412; rtl/ibex_core.sv:1813-1826, 1956, 1993
- Edge: yes, of F-CSR-032
- Status: ACTIVE

### F-CSR-035: mtvec WARL: BASE 256-byte aligned, MODE forced to vectored; boot initialisation
- What: A write stores wdata[31:8] with bits 7:2 = 0 and MODE = 01. Reset value is 0x1; on the first
  boot fetch (pc_mux == PC_BOOT & pc_set) the register is loaded with {boot_addr_i[31:8], 8'h01}.
  Interrupts vector to BASE + 4*cause, exceptions to BASE.
- Observable at: rvfi_rd_wdata of csrr mtvec; rvfi_pc_rdata of the first handler record (X-1: the
  trapping record's rvfi_pc_wdata is the fall-through address); instr_addr_o of the trap fetch only
  with the icache disabled (X-21).
- Config: none.
- Source: spec: machine.adoc "Machine Trap-Vector Base-Address (mtvec) Register" | doc:
  cs_registers.rst "Machine Trap-Vector Base Address (mtvec)"; doc/03_reference/
  exception_interrupts.rst (vector table initialised to boot address) | RTL-defined:
  rtl/ibex_cs_registers.sv:736-743, 807-808, 1170-1181; rtl/ibex_if_stage.sv:256
- Edge: no
- Status: ACTIVE
- Notes: Direct mode (MODE = 0) is not selectable; the spec permits this WARL restriction. Canonical
  entry; alias: F-IRQ-013. Carries the folded F-CSR-036 (MODE / bits 7:2 legalised on write,
  CG-CSR-002.cr_mtvec_mode_lo) and F-CSR-037 (boot_addr_i[7:0] ignored for the boot value,
  CG-CSR-016.cr_mtvec_first).

### F-CSR-036: mtvec write with MODE = 00/10/11 or bits 7:2 set reads back legalised
- What: Folded into F-CSR-035: 0x1234_56FF -> 0x1234_5601, 0x8000_0000 -> 0x8000_0001 and csrrc
  mtvec, 1 leaving MODE = 1 are the parent's mask {wdata[31:8], 8'h01} at specific values (bins
  d00_nz, r10_*, r11_*, cr_csr_wpat.mtvec_illegal).
- Edge: yes, of F-CSR-035
- Status: FOLDED into F-CSR-035 (bin CG-CSR-002.cr_mtvec_mode_lo.d00_nz)

### F-CSR-037: boot_addr_i low byte is ignored for the mtvec boot value
- What: Folded into F-CSR-035: the boot value {boot_addr_i[31:8], 8'h01} already discards
  boot_addr_i[7:0] (rtl/ibex_cs_registers.sv:371, 739-741); bins mtvec_first_nonzero /
  mtvec_early_nonzero carry the nonzero low byte.
- Edge: yes, of F-CSR-035
- Status: FOLDED into F-CSR-035 (bin CG-CSR-016.cr_mtvec_first.mtvec_first_nonzero)

### F-CSR-038: mscratch is a full 32-bit read/write register, reset 0
- What: Any 32-bit value is stored and read back; csrrs/csrrc operate bit-wise.
- Observable at: rvfi_rd_wdata.
- Config: none.
- Source: spec: machine.adoc "Machine Scratch (mscratch) Register" | doc: cs_registers.rst table row
  0x340 | RTL-defined: rtl/ibex_cs_registers.sv:466, 792, 1121-1132
- Edge: no
- Status: ACTIVE

### F-CSR-039: mepc: bit 0 read-only zero, bit 1 writable (IALIGN = 16), reset 0
- What: SW write stores {wdata[31:1], 0}. Trap entry writes the faulting PC (see F-CSR-041).
- Observable at: rvfi_rd_wdata; rvfi_pc_rdata of the record after the mret (X-1).
- Config: none.
- Source: spec: machine.adoc "Machine Exception Program Counter (mepc) Register" | doc:
  cs_registers.rst "Machine Exception PC (mepc)" | RTL-defined: rtl/ibex_cs_registers.sv:729,
  796-797, 1089-1100
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-CSR-040 (odd write reads back even with bit 1 preserved; the mret to
  the 2-byte-aligned target is CG-PRV-002.cr_mret_target).

### F-CSR-040: mepc write of an odd value reads back even; bit 1 preserved
- What: Folded into F-CSR-039: 0x3 -> 0x2 is the parent's bit-0 rule at one value; the mret resuming
  at the 2-byte-aligned target is F-PRV-006 (CG-PRV-002.cr_mret_target.m_b1).
- Edge: yes, of F-CSR-039
- Status: FOLDED into F-CSR-039 (bin CG-CSR-003.cr_mepc_lo_op.b01_csrrw)

### F-CSR-041: mepc hardware value depends on the exception class
- What: Interrupts: mepc = pc_if (next unexecuted instruction); synchronous exceptions from ID
  (illegal, ecall, ebreak, fetch error, illegal CSR): mepc = pc_id; load/store errors detected in
  WB: mepc = pc_wb. Debug entry writes dpc instead and leaves mepc untouched.
- Observable at: csrr read-back of mepc on rvfi_rd_wdata in the handler vs. rvfi_pc_rdata of the
  faulting instruction (pc_id), of the load/store in WB (pc_wb) or of the next unexecuted
  instruction (pc_if).
- Config: none.
- Source: spec: machine.adoc "Machine Exception Program Counter (mepc) Register", "Environment Call
  and Breakpoint" (epc = address of ECALL/EBREAK itself) | RTL-defined:
  rtl/ibex_cs_registers.sv:893-905, 910-917, 928-929; rtl/ibex_controller.sv:732, 802-803, 833-840
- Edge: yes, of F-CSR-039
- Status: ACTIVE

### F-CSR-042: mcause storage is 7 bits; read format {int, fill, code[4:0]}; reset 0
- What: Stored: irq_int (internal NMI), irq_ext (interrupt), lower_cause[4:0]. Read: bit 31 =
  irq_ext | irq_int; bits 30:5 = all ones when irq_int else 0; bits 4:0 = code. SW write: irq_ext =
  (wdata[31:30] == 10), irq_int = (wdata[31:30] == 11), code = wdata[4:0].
- Observable at: rvfi_rd_wdata.
- Config: none.
- Source: spec: machine.adoc "Machine Cause (mcause) Register" (Exception Code is WLRL) | doc:
  cs_registers.rst "Machine Cause (mcause)" | RTL-defined: rtl/ibex_cs_registers.sv:487-489,
  731-733, 800, 1135-1146; rtl/ibex_pkg.sv:343-347
- Edge: no
- Status: ACTIVE
- Notes: Hardware values: exceptions 0x0000_0001/2/3/5/7/8/11 (codes 1,2,3,5,7,8,11); interrupts
  0x8000_0003/7/B, fast 0x8000_0010 + id, external NMI 0x8000_001F, internal NMI (integrity)
  0xFFFF_FFE0. Doc defect D3: cs_registers.rst:213 marks mcause bit 31 (and 4:0) R although the RTL
  accepts software writes (mcause_en, rtl/ibex_cs_registers.sv:800) as the priv spec requires; the
  checker follows the RTL and TP-CSR-046 is `pass (doc mismatch D3)`. Carries the folded
  F-CSR-043/044/045 (the read/write mapping at [31:30] = 00/01/10/11, CG-CSR-003.cr_mcause_hi_mid)
  and F-CSR-046 (software-writable, CG-CSR-003.cr_csr_op.mcause_*).

### F-CSR-043: mcause write with bits 29:5 set (and [31:30] != 11) reads them back as 0
- What: Folded into F-CSR-042: 0x3FFF_FFFF -> 0x1F and 0x8FFF_FFFE -> 0x8000_001E follow from the
  parent's 7-bit storage (bits 29:5 not stored); bins h00_nz, h01_nz, h10_nz.
- Edge: yes, of F-CSR-042
- Status: FOLDED into F-CSR-042 (bin CG-CSR-003.cr_mcause_hi_mid.h00_nz)

### F-CSR-044: mcause write with bits 31:30 = 11 reads back with bits 30:5 all ones
- What: Folded into F-CSR-042: [31:30] = 11 -> irq_int -> read bits 30:5 all ones (0xC000_0000 ->
  0xFFFF_FFE0) is the parent's read formula and the internal-NMI encoding alias; bins h11_zero,
  h11_nz, cr_mcause_hi_code.h11_c0 / h11_c31.
- Edge: yes, of F-CSR-042
- Status: FOLDED into F-CSR-042 (bin CG-CSR-003.cr_mcause_hi_mid.h11_zero)

### F-CSR-045: mcause write with bits 31:30 = 01 reads back with bit 31 = 0
- What: Folded into F-CSR-042: [31:30] = 01 sets neither irq_ext nor irq_int (0x4000_0002 -> 0x2)
  per the parent's write mapping; bins h01_zero, cr_mcause_hi_code.h01_other.
- Edge: yes, of F-CSR-042
- Status: FOLDED into F-CSR-042 (bin CG-CSR-003.cr_mcause_hi_mid.h01_zero)

### F-CSR-046: mcause is software-writable although the Ibex doc marks its fields R
- What: Folded into F-CSR-042: software writes to mcause are the parent's 'SW write' clause; doc
  defect D3 (cs_registers.rst:213 marks the fields R) is recorded on F-CSR-042 and TP-CSR-046 stays
  `pass (doc mismatch D3)`.
- Edge: yes, of F-CSR-042
- Status: FOLDED into F-CSR-042 (bin CG-CSR-003.cr_csr_op.mcause_csrrw)

### F-CSR-047: mtval: full 32-bit RW; hardware value per trap cause
- What: Illegal instruction: the faulting instruction bits (compressed: zero-extended 16 bits);
  instruction access fault: faulting PC (pc_id, or pc_id + 2 when the second half of a 32-bit
  instruction faulted); load/store access fault: the faulting data address (LSU part); ecall,
  ebreak, external interrupts: 0; internal NMI (integrity error): faulting address. SW writes store
  all 32 bits.
- Observable at: csrr read-back of mtval on rvfi_rd_wdata in the handler; rvfi_insn of the faulting
  instruction (encoding cases), rvfi_pc_rdata (fetch-fault case), rvfi_mem_addr (load/store-fault
  case).
- Config: none.
- Source: spec: machine.adoc "Machine Trap Value (mtval) Register" | doc: cs_registers.rst "Machine
  Trap Value (mtval)" | RTL-defined: rtl/ibex_cs_registers.sv:492, 735, 803, 921-922;
  rtl/ibex_controller.sv:550, 741-743, 859-869, 909-912, 923-926
- Edge: no
- Status: ACTIVE
- Notes: ebreak mtval = 0 (spec allows 0 or the ebreak address). WFI/mret/dret illegal traps report
  their encodings (0x10500073, 0x30200073, 0x7B200073). Doc defect D10: cs_registers.rst:235 says
  mtval is 0 'for all other exceptions', but on an instruction access fault the RTL writes the
  faulting fetch address (pc_id or pc_id + 2, rtl/ibex_controller.sv:861). Carries the folded
  F-CSR-048 (illegal compressed encoding zero-extended, CG-PRV-008.cr_exc_mtval.exc_insn16) and
  F-CSR-049 (illegal CSR access reports the CSR instruction encoding, exc_insn32).

### F-CSR-048: mtval for an illegal compressed instruction has bits 31:16 = 0
- What: Folded into F-CSR-047: the parent already states 'compressed: zero-extended 16 bits'
  (rtl/ibex_controller.sv:866-868).
- Edge: yes, of F-CSR-047
- Status: FOLDED into F-CSR-047 (bin CG-PRV-008.cr_exc_mtval.exc_insn16)

### F-CSR-049: mtval for an illegal CSR access equals the CSR instruction encoding
- What: Folded into F-CSR-047: an illegal CSR access is an illegal-instruction trap, so mtval = the
  CSR instruction encoding (mtval[31:20] = CSR address) is the parent's rule; TP-CSR-049 keeps the
  decode check.
- Edge: yes, of F-CSR-047
- Status: FOLDED into F-CSR-047 (bin CG-PRV-008.cr_exc_mtval.exc_insn32)

### F-CSR-050: mcounteren: 13 implemented bits (bit 1 read-only 0), write gated by
mcounteren_writable_i, reset 0
- What: Alias of F-PMC-025: CSR-area perspective, see canonical (13 implemented bits, bit 1
  read-only 0, bits 31:13 read 0, reset 0, write accepted only while mcounteren_writable_i ==
  IbexMuBiOn, rtl/ibex_cs_registers.sv:845). Carries the folded F-CSR-051 (gate Off or any invalid
  MuBi encoding drops the write silently) and F-CSR-052 (all-ones write reads back 0x0000_1FFD).
- Edge: no
- Status: ALIAS of F-PMC-025

### F-CSR-051: mcounteren write with mcounteren_writable_i != IbexMuBiOn is silently ignored
- What: Folded into F-CSR-050 (canonical F-PMC-025): the parent's gate variable at its other values
  (IbexMuBiOff and the 14 invalid encodings) - no trap, old value read back; bins off_all1, off_cy,
  invalid_all1, invalid_ir.
- Edge: yes, of F-PMC-025
- Status: FOLDED into F-PMC-025 (bin CG-CSR-002.cr_mcen_gate_w.off_all1)

### F-CSR-052: mcounteren all-ones write reads back 0x0000_1FFD
- What: Folded into F-CSR-050 (canonical F-PMC-025): 0xFFFF_FFFF -> 0x0000_1FFD is the parent's mask
  at the all-ones pattern.
- Edge: yes, of F-PMC-025
- Status: FOLDED into F-PMC-025 (bin CG-CSR-002.cr_mcen_gate_w.on_all1)

### F-CSR-053: U-mode counter aliases cycle/instret/hpmcounter3-12 (and h) gated per bit by
mcounteren; M-mode always readable
- What: For 0xC00-0xC0C and 0xC80-0xC8C the read returns the same 64-bit counter as the M-mode
  alias; in U-mode the access is illegal when mcounteren[idx] = 0 (idx = csr[4:0]).
- Observable at: rvfi_rd_wdata equal to the mcycle/minstret/mhpmcounter value (modulo elapsed
  cycles); rvfi_trap in U-mode with the bit clear; rvfi_ext_mcycle / rvfi_ext_mhpmcounters.
- Config: mcounteren, privilege mode.
- Source: spec: machine.adoc "Machine Counter-Enable (mcounteren) Register" (read-only shadows) |
  doc: performance_counters.rst | RTL-defined: rtl/ibex_cs_registers.sv:607-633
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-CSR-054 (one-hot mcounteren matrix: alias y traps in U iff bit idx(y)
  is clear, CG-CSR-005.cr_diag_u / cr_onehot_alias); the write-op case F-CSR-057 is folded into
  F-CSR-011.

### F-CSR-054: U-mode read of a counter alias with its mcounteren bit clear traps; with it set,
the read succeeds and equals the M-mode value
- What: Folded into F-CSR-053: the x/y one-hot matrix is the parent's per-bit gate evaluated
  exhaustively (TP-CSR-054 keeps the sweep; bins diag_ok, offdiag_trap, cr_onehot_alias.*).
- Edge: yes, of F-CSR-053
- Status: FOLDED into F-CSR-053 (bin CG-CSR-005.cr_diag_u.offdiag_trap)

### F-CSR-055: time (0xC01) and timeh (0xC81) trap in every privilege mode
- What: Not implemented; unimplemented-address class (mcounteren[1] is read-only 0 and never
  consulted because the address is not decoded).
- Observable at: rvfi_trap = 1 in M-mode and U-mode.
- Config: none.
- Source: doc: cs_registers.rst "Time Registers (time(h))" | RTL-defined:
  rtl/ibex_cs_registers.sv:702-704 (CSR_TIME not in csr_num_e, rtl/ibex_pkg.sv:463-694)
- Edge: yes, of F-CSR-053
- Status: ACTIVE

### F-CSR-056: hpmcounter13-31 (and h) always trap in U-mode but read 0 in M-mode
- What: mcounteren[13..31] are constant 0, so the U-mode gate always fails for 0xC0D-0xC1F and
  0xC8D-0xC9F, while M-mode reads return 0 (counter not implemented).
- Observable at: rvfi_trap = 1 (U), rvfi_rd_wdata = 0 (M).
- Config: privilege mode.
- Source: spec: machine.adoc "Hardware Performance Monitor" (read-only 0 counters legal) |
  RTL-defined: rtl/ibex_cs_registers.sv:618, 632, 1699-1700, 1731-1732
- Edge: yes, of F-CSR-053
- Status: ACTIVE

### F-CSR-057: Write op to a 0xC00-0xC9F alias traps even in M-mode
- What: Folded into F-CSR-011: a write op to 0xC00-0xC9F is the read-only-range rule (csr[11:10] =
  11) applied to the alias addresses; the x0 forms read per F-CSR-002 (bins wr_m_trap, wr_u_trap).
- Edge: yes, of F-CSR-011
- Status: FOLDED into F-CSR-011 (bin CG-CSR-005.cr_wr_alias.wr_m_trap)

### F-CSR-058: mcountinhibit: 13 implemented bits, bit 1 read-only 0, reset 0 (all counting)
- What: Alias of F-PMC-020: CSR-area perspective (13 implemented bits, bit 1 read-only 0, reset 0;
  inhibition only stops incrementing), see canonical. Carries the folded F-CSR-059 (an inhibited
  counter holds its value and still accepts CSR writes exactly, CG-CSR-004.cr_csr_inhibit.*_on).
- Edge: no
- Status: ALIAS of F-PMC-020

### F-CSR-059: Inhibited counter holds its value; a CSR write to it still takes effect
- What: Folded into F-CSR-058 (canonical F-PMC-020): 'holds its value, remains writable' is the
  parent's own clause (rtl/ibex_counter.sv:44-50); bins mcycle_on .. hpm12_on and
  CG-CSR-013.cr_cyc_wr.mcycle_wr_on.
- Edge: yes, of F-PMC-020
- Status: FOLDED into F-PMC-020 (bin CG-CSR-004.cr_csr_inhibit.mcycle_on)

### F-CSR-060: minstret read in ID with mcountinhibit[2] = 1 returns the raw flop value without the
speculative WB increment
- What: The ID-stage read mux for mhpmcounter[2] is instr_ret_spec_i & ~mcountinhibit[2] ? minstret_next
  : minstret_raw (rtl/ibex_cs_registers.sv:1658), so with IR inhibited a csrr minstret placed right
  after a retiring instruction returns the raw flop value (no +1 for the instruction in WB), while the
  same read with IR = 0 returns the incremented value (F-CSR-068); mhpmcounter10 follows the same rule
  with mcountinhibit[10] (:1690-1692). The all-ones write-mask fact (read-back 0x0000_1FFD) stays with
  the canonical F-PMC-020.
- Observable at: csrr read-back of minstret on rvfi_rd_wdata in the cycle a countable instruction
  retires in WB: equal to the number of previously retired countable instructions EXCLUDING the one in
  WB when mcountinhibit[2] = 1 and INCLUDING it when 0; rvfi_order gives the retirement order.
- Config: mcountinhibit[2] (and [10] for the compressed-instruction counter).
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1651-1658, 1687-1692
- Edge: yes, of F-PMC-020
- Status: ACTIVE
- Notes: Re-activated (Critic M-10 over-merge): the inhibited speculative read is an RTL-defined
  behaviour distinct from the write-mask fact of F-PMC-020 and from the uninhibited speculative read
  F-CSR-068; bin CG-CSR-013.cr_minstret_rd_wb.minstret_inh_retiring (TP-CSR-060; cited by
  TP-CSR-068). Canonical for the PMC alias F-PMC-022.

### F-CSR-061: mhpmevent3-12 read hardwired one-hot (1 << (n - 3)); mhpmevent13-31 read 0; writes ignored
- What: Alias of F-PMC-018: CSR-area perspective (mhpmevent3..12 read 1 << (N - 3), i.e. 0x1..0x200,
  rtl/ibex_cs_registers.sv:185, :1602-1619; performance_counters.rst:133-147 says 1 << N: doc
  mismatch D20, checker follows the RTL, rtl-arch T-053 X-3; writes to 0x323-0x33F
  are accepted without trap and without effect; the zero-reading 13..31 selectors are F-PMC-019),
  see canonical.
- Edge: no
- Status: ALIAS of F-PMC-018

### F-CSR-062: mcycle/mcycleh: 64-bit cycle counter, RW both halves, reset 0
- What: Alias of F-PMC-001: CSR-area perspective (64-bit mcycle/mcycleh, both halves RW, reset 0, a
  write to one half preserves the other), see canonical.
- Edge: no
- Status: ALIAS of F-PMC-001

### F-CSR-063: Write to mcycle while counting: the write wins and the increment of that cycle is
lost
- What: Alias of F-PMC-004: CSR-area perspective (counter_we has priority over counter_inc, the
  write cycle does not count, rtl/ibex_counter.sv:44-47), see canonical.
- Edge: yes, of F-CSR-062
- Status: ALIAS of F-PMC-004

### F-CSR-064: mcycleh write preserves the low half; carry into mcycleh at low = 0xFFFF_FFFF
- What: Alias of F-PMC-005: CSR-area perspective (mcycleh write in the carry cycle drops only that
  cycle's increment: the counter is {H, 0xFFFF_FFFF} after the write, the next enabled cycle wraps
  low and carries into high = H + 1, rtl/ibex_counter.sv:33-47; rtl-arch T-053 row TP-CSR-064), see
  canonical.
- Edge: yes, of F-CSR-062
- Status: ALIAS of F-PMC-005

### F-CSR-065: csrrs/csrrc on mcycle is atomic: stored value = (value returned in rd) op mask
- What: csr_wdata_int uses csr_rdata_o of the same cycle; no increment can interleave between the
  read and the write of one CSR instruction.
- Observable at: rvfi_rd_wdata (old) and next csrr (old | mask + elapsed).
- Config: none.
- Source: spec: zicsr.adoc "CSR Instructions" (atomically read-modify-write) | RTL-defined:
  rtl/ibex_cs_registers.sv:1001-1009; rtl/ibex_counter.sv:44-47
- Edge: yes, of F-PMC-001
- Status: ACTIVE
- Notes: Edge re-pointed to the canonical F-PMC-001 (F-CSR-062 is its CSR-area alias); the edge is
  F-CSR-001's RMW atomicity under a concurrent hardware increment.

### F-CSR-066: minstret/minstreth: 64-bit retired-instruction counter; exclusions
- What: Alias of F-PMC-007: CSR-area perspective (64-bit minstret/minstreth; not counted: trapping
  instructions, ecall, ebreak, minstret(h) write ops; a Zcmp sequence counts once; a countable
  instruction retiring from WB in a minstret(h) write's commit cycle loses its increment, we over
  inc, rtl/ibex_counter.sv:44-45, rtl-arch T-053 X-17; reset 0), see canonical. Carries the folded F-CSR-067 (the writer is not counted: csrrw minstret, X ; csrr -> X,
  CG-CSR-013.cr_minstret_wr.minstret_wr_none).
- Edge: no
- Status: ALIAS of F-PMC-007

### F-CSR-067: Value read after a minstret write equals the written value (writer not counted)
- What: Folded into F-CSR-066 (canonical F-PMC-007): 'read after write equals the written value' is
  the parent's minstret_write exclusion (rtl/ibex_id_stage.sv:1213-1219) at one observation.
- Edge: yes, of F-PMC-007
- Status: FOLDED into F-PMC-007 (bin CG-CSR-013.cr_minstret_wr.minstret_wr_none)

### F-CSR-068: minstret read in ID includes the retirement of the instruction still in WB
- What: Alias of F-PMC-009: CSR-area perspective (a csrr minstret / mhpmcounter10 in ID returns
  minstret_next when an instruction retires in WB in the same cycle, instr_ret_spec), see canonical.
  The inhibited read is F-CSR-060 (ACTIVE); the mhpmcounter10 twin F-CSR-072 is folded into
  F-PMC-007.
- Edge: yes, of F-PMC-007
- Status: ALIAS of F-PMC-009

### F-CSR-069: mhpmcounter3-12: 32-bit event counters; high half reads 0 and writes to it are
ignored; hardwired event mapping
- What: Alias of F-PMC-015: CSR-area perspective (mhpmcounter3-12 are 32-bit event counters with the
  hardwired event map 3 = data-side wait, 4 = fetch wait, 5 = loads, 6 = stores, 7 = jumps, 8 =
  branches, 9 = taken branches, 10 = compressed retired, 11 = multiply wait, 12 = divide wait; the h
  halves read 0 and drop writes), see canonical.
- Edge: no
- Status: ALIAS of F-PMC-015

### F-CSR-070: 32-bit mhpmcounter wraps from 0xFFFF_FFFF to 0 with no carry into the h half
- What: Alias of F-PMC-016: CSR-area perspective (a 32-bit mhpmcounter wraps from 0xFFFF_FFFF to 0
  with no carry into the h half), see canonical.
- Edge: yes, of F-PMC-015
- Status: ALIAS of F-PMC-016

### F-CSR-071: mhpmcounter13-31 and their h halves read 0 and ignore writes without trap
- What: Addresses 0xB0D-0xB1F and 0xB8D-0xB9F are decoded; mhpmcounter[Cnt] is tied to 0 and the
  write enables are unused.
- Observable at: rvfi_trap = 0, rvfi_rd_wdata = 0 after a write of all-ones.
- Config: none.
- Source: spec: machine.adoc "Hardware Performance Monitor" (read-only 0 legal) | RTL-defined:
  rtl/ibex_cs_registers.sv:580-604, 1699-1700, 1716-1718
- Edge: yes, of F-PMC-015
- Status: ACTIVE

### F-CSR-072: mhpmcounter10 (compressed retired) read includes the compressed instruction in WB
- What: Folded into F-PMC-007 (through F-CSR-068): the same speculative-next read
  (rtl/ibex_cs_registers.sv:1687-1692) for counter 10 (compressed retired); bins hpm10_idle,
  hpm10_retiring.
- Edge: yes, of F-PMC-007
- Status: FOLDED into F-PMC-007 (bin CG-CSR-013.cr_minstret_rd_wb.hpm10_retiring)

### F-CSR-073: Write to mhpmcounterNh (N = 3..12) is a no-op for the low half
- What: counterh_we selects counter_load[31:0] = current low value, so the low half is preserved
  (the increment of that cycle is still lost because we has priority).
- Observable at: rvfi_rd_wdata of csrr mhpmcounter3 after csrrw mhpmcounter3h.
- Config: none.
- Source: RTL-defined: rtl/ibex_counter.sv:38-47, 86-90
- Edge: yes, of F-PMC-015
- Status: ACTIVE
- Notes: Edge re-pointed to the canonical F-PMC-015 (F-CSR-069 is its CSR-area alias); the distinct
  fact here is the lost increment in the h-write cycle (the low-half case is F-PMC-045).

### F-CSR-074: dcsr: debug-only RW register with WARL fields, reset 0x4000_0003
- What: Alias of F-DBG-012: CSR-area perspective (debug-only RW; xdebugver = 4 and cause read-only;
  ebreakm/ebreaku/step/prv writable; stepie, stopcount, stoptime, mprven, nmip and bits 27:16, 14, 5
  forced 0; reset 0x4000_0003), see canonical. Carries the folded F-CSR-075 (all-ones write reads
  back 0x4000_B007 | cause << 6 on current RTL, CG-CSR-007.cr_csr_wpat_dbg.dcsr_all1).
- Edge: no
- Status: ALIAS of F-DBG-012

### F-CSR-075: dcsr write of all-ones reads back 0x4000_B007 | (cause << 6)
- What: Folded into F-CSR-074 (canonical F-DBG-012): 0xFFFF_FFFF -> 0x4000_B007 | (cause << 6) is
  the parent's WARL mask at the all-ones pattern (RTL-as-is; under B15 bit 13 reads 0, giving
  0x4000_9007).
- Edge: yes, of F-DBG-012
- Status: FOLDED into F-DBG-012 (bin CG-CSR-007.cr_csr_wpat_dbg.dcsr_all1)

### F-CSR-076: dcsr.ebreaks (bit 13) is writable and readable although S-mode does not exist
- What: Alias of F-DBG-016: CSR-area perspective, see canonical. BUG CANDIDATE B15 (spec violation):
  dcsr.ebreaks (bit 13) is stored and read back although
  tools/specs/riscv-debug-spec/xml/core_registers.xml:163-172 hardwires ebreaks to 0 when the hart
  has no S-mode (misa 0x4090_1104); rtl/ibex_cs_registers.sv:811-835 forces every other unsupported
  field but not bit 13; functional impact nil (rtl/ibex_controller.sv:481-483 never reads it);
  checker direction 'reads 0', TP-CSR-076 expected-fail (B15). Formerly filed as a doc mismatch
  against cs_registers.rst:467 ('Other bit fields read as zero'); D5 is retired.
- Edge: yes, of F-CSR-074
- Status: ALIAS of F-DBG-016

### F-CSR-077: dcsr.prv WARL: 01 and 10 legalise to 00 (U)
- What: Alias of F-DBG-013: CSR-area perspective (dcsr.prv = S or H stores U; dret then resumes in
  U), see canonical. The fold F-PRV-026 now hangs on the canonical's base feature F-DBG-012.
- Edge: yes, of F-DBG-012
- Status: ALIAS of F-DBG-013

### F-CSR-078: dpc: debug-only, bit 0 read-only zero, reset 0
- What: SW write stores {wdata[31:1], 0}; hardware writes the resume PC on debug entry.
- Observable at: rvfi_rd_wdata in debug mode; rvfi_pc_rdata of the record after the dret (X-1).
- Config: debug mode.
- Source: doc: cs_registers.rst "Debug PC Register (dpc)" | RTL-defined:
  rtl/ibex_cs_registers.sv:554-557, 746, 838, 916-917, 1207-1218
- Edge: no
- Status: ACTIVE

### F-CSR-079: dscratch0/dscratch1: debug-only full 32-bit RW, reset 0
- What: Plain storage, only accessible in debug mode.
- Observable at: rvfi_rd_wdata in debug mode.
- Config: debug mode.
- Source: doc: cs_registers.rst "Debug Scratch Register 0/1" | RTL-defined:
  rtl/ibex_cs_registers.sv:558-565, 840-841, 1225-1254
- Edge: no
- Status: ACTIVE

### F-CSR-080: tselect: M-mode readable, reads 0, writes effective only in debug mode and
legalised to the highest implemented trigger index
- What: With DbgHwBreakNum = 1, tselect_d is always 0; tselect_we requires debug_mode_i. In M-mode
  the write is silently ignored (no trap).
- Observable at: rvfi_rd_wdata = 0 after csrrw tselect, 5 in either mode; rvfi_trap = 0.
- Config: debug mode.
- Source: spec: tools/specs/riscv-debug-spec/Sdtrig.adoc "Trigger Module Registers", "Enumeration" |
  doc: cs_registers.rst "Trigger Select Register (tselect)" | RTL-defined:
  rtl/ibex_cs_registers.sv:636-639, 1775, 1785-1786, 1837
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D12: debug.rst:54-55 says tselect/tdata1/tdata2 are 'accessible from Debug Mode
  only' and trap otherwise; the RTL and cs_registers.rst allow M-mode reads and drop M-mode writes
  (illegal_csr = ~DbgTriggerEn only, rtl/ibex_cs_registers.sv:636-639). Doc defect D18:
  cs_registers.rst:348 names the parameter 'DbgHwNumLen'; the RTL parameter is DbgHwBreakNum
  (DbgHwNumLen is its derived bit width).

### F-CSR-081: tdata1 reads 0x2800_1048 (execute = 0) or 0x2800_104C; only bit 2 writable in
debug mode
- What: type = 2, dmode = 1, action = 1, m = 1, u = 1 are constant; execute (bit 2) is the only
  stored bit and is written only in debug mode.
- Observable at: rvfi_rd_wdata.
- Config: debug mode.
- Source: spec: Sdtrig.adoc "Trigger Module Registers" (WARL) | doc: cs_registers.rst "Trigger Data
  Register 1 (tdata1)" | RTL-defined: rtl/ibex_cs_registers.sv:640-643, 1777-1778, 1789, 1848-1864
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D4: cs_registers.rst:360 gives the reset value 0x2800_1000, but its own field
  table (m = 1 at bit 6, u = 1 at bit 3) and the RTL (rtl/ibex_cs_registers.sv:1848-1864) yield
  0x2800_1048; the checker follows the RTL and TP-CSR-081/108 are `pass (doc mismatch D4)`. Doc
  defect D12 (debug.rst:54-55 'Debug Mode only') applies as for F-CSR-080.

### F-CSR-082: tdata2: 32-bit match address, writable only in debug mode
- What: Alias of F-TRG-007: CSR-area perspective (32-bit match address; tmatch_value_we requires
  debug_mode_i, M-mode writes ignored without trap - doc defect D12), see canonical. Carries the
  folded F-CSR-084 (M-mode writes to tselect/tdata1/tdata2 change nothing and arm no trigger,
  CG-CSR-008.cr_csr_dbg_form.*_nondbg_wr).
- Edge: no
- Status: ALIAS of F-TRG-007

### F-CSR-083: tdata3 (0x7A3), mcontext (0x7A8), mscontext (0x7AA), scontext (0x5A8) read 0 and
ignore writes
- What: Alias of F-TRG-008: CSR-area perspective (tdata3/mcontext/mscontext/scontext are decoded
  because DbgTriggerEn = 1, have no storage, read 0 and drop writes; bug candidate B3, doc defect
  D18; TP-CSR-083 stays expected-fail (B3)), see canonical. The U-mode trap on the S-level address
  0x5A8 is the privilege-class rule F-CSR-014.
- Edge: no
- Status: ALIAS of F-TRG-008

### F-CSR-084: M-mode (non-debug) writes to tselect/tdata1/tdata2 change nothing and do not trap
- What: Folded into F-CSR-082 (canonical F-TRG-007): 'M-mode writes ignored, no trap, trigger not
  armed' is the parent's debug_mode_i write gate (rtl/ibex_cs_registers.sv:1775-1781); bins
  tselect/tdata1/tdata2_nondbg_wr, cr_tdata1_w.nondbg_e1_none.
- Edge: yes, of F-TRG-007
- Status: FOLDED into F-TRG-007 (bin CG-CSR-008.cr_csr_dbg_form.tdata2_nondbg_wr)

### F-CSR-085: cpuctrlsts (0x7C0): custom M-mode RW register, reset 0, field map
- What: [0] icache_enable (ICache = 1: writable), [1] data_ind_timing (DataIndTiming = 1: writable),
  [2] dummy_instr_en and [5:3] dummy_instr_mask (writable iff DummyInstructions), [6] sync_exc_seen
  (RW, HW set/clear), [7] double_fault_seen (RW, HW set), [8] ic_scr_key_valid (read-only, sampled
  from ic_scr_key_valid_i with one cycle latency), [31:9] read 0.
- Observable at: csrr read-back on rvfi_rd_wdata; rvfi_ext_ic_scr_key_valid (bit 8 mirror);
  double_fault_seen_o (bit 7 hardware set); the icache_enable and data_ind_timing effects are
  observed at instr_req_o / retirement timing by the IC and EX areas.
- Config: cpuctrlsts itself.
- Source: doc: cs_registers.rst "CPU Control and Status Register (cpuctrlsts)";
  doc/03_reference/security.rst "Data Independent Timing", "Dummy Instruction Insertion" |
  RTL-defined: rtl/ibex_cs_registers.sv:239-246, 666-670, 874-877, 1888-1984
- Edge: no
- Status: ACTIVE
- Notes: Canonical entry; alias: F-SEC-031. Carries the folded F-CSR-087 (dummy_instr_en/mask
  writable iff DummyInstructions; the wrapper fixes DummyInstructions = 1, so the read-only-zero arm
  is not reachable in this DUT, CG-CSR-009.cr_mask_en) and F-CSR-088 (all-ones write reads back
  0x0FF | key << 8, CG-CSR-009.cr_wpat_op.all1_csrrw, cr_key_w).

### F-CSR-086: cpuctrlsts.icache_enable drives icache_enable_o, masked while in or entering debug
mode
- What: Alias of F-IC-040: CSR-area perspective (icache_enable_o = cpuctrlsts.icache_enable &
  ~(debug_mode | debug_mode_entering), rtl/ibex_cs_registers.sv:1970-1971; the CSR bit itself reads
  back unchanged in debug mode), see canonical.
- Edge: yes, of F-CSR-085
- Status: ALIAS of F-IC-040

### F-CSR-087: cpuctrlsts.dummy_instr_en / dummy_instr_mask are read-only zero when the DUT is
built with DummyInstructions = 0
- What: Folded into F-CSR-085: the parent's build parameter (DummyInstructions) at its other value;
  gen_dut_top fixes DummyInstructions = 1 (owner default Q-002), so only the writable arm
  (rtl/ibex_cs_registers.sv:1908-1929; bins cr_mask_en.m0_en .. m7_en, cp_dummy_en_w) is reachable.
- Edge: yes, of F-CSR-085
- Status: FOLDED into F-CSR-085 (bin CG-CSR-009.cr_mask_en.m0_en)

### F-CSR-088: cpuctrlsts write of all-ones reads back 0x0FF (DummyInstructions = 1) or 0x0C3
(= 0), plus bit 8 as driven by ic_scr_key_valid_i
- What: Folded into F-CSR-085: 0xFFFF_FFFF -> 0x0FF | (ic_scr_key_valid_i << 8) is the parent's
  field map at the all-ones pattern (bins all1_csrrw, all1_csrrs, cr_key_w.*).
- Edge: yes, of F-CSR-085
- Status: FOLDED into F-CSR-085 (bin CG-CSR-009.cr_wpat_op.all1_csrrw)

### F-CSR-089: cpuctrlsts.sync_exc_seen set by hardware on any synchronous exception and cleared by
mret; double_fault_seen set on a second synchronous exception; both software-writable
- What: Alias of F-SEC-022: CSR-area perspective (sync_exc_seen set on any synchronous exception
  outside debug mode and cleared by mret; a second synchronous exception sets double_fault_seen and
  pulses double_fault_seen_o for one cycle; interrupts and NMI neither set nor check the flag; both
  bits software RW and a software write never pulses; rtl/ibex_cs_registers.sv:935-945, 964-965,
  1967-1968), see canonical. Carries the folded F-CSR-090 (ecall inside a handler pulses exactly one
  cycle; interrupts, debug entry and debug-mode exceptions do not, CG-CSR-009.cr_dbl_detect).
- Edge: no
- Status: ALIAS of F-SEC-022

### F-CSR-090: Double fault: ecall inside an exception handler (before mret) pulses
double_fault_seen_o exactly one cycle and sets bit 7; interrupts and debug entry do not
- What: Folded into F-CSR-089 (canonical F-SEC-022): the one-cycle pulse and the interrupt/NMI
  exclusion are the parent's clauses; the debug-mode exclusion is F-SEC-023 (bins sync_s1_pulse,
  s1_irq_nopulse, s1_nmi_nopulse, s1_dbg_nopulse, s1_dbgmode_exc_nopulse).
- Edge: yes, of F-SEC-022
- Status: FOLDED into F-SEC-022 (bin CG-CSR-009.cr_dbl_detect.sync_s1_pulse)

### F-CSR-091: Software-set sync_exc_seen followed by any synchronous exception is reported as a
double fault; software-cleared sync_exc_seen inside a handler suppresses detection
- What: Alias of F-SEC-025: CSR-area perspective (csrrs cpuctrlsts, 0x40 then ecall pulses
  double_fault_seen_o; clearing bit 6 inside a handler suppresses detection; a software write of bit
  7 never pulses), see canonical.
- Edge: yes, of F-CSR-089
- Status: ALIAS of F-SEC-025

### F-CSR-092: secureseed (0x7C1): write pulses the dummy-instruction LFSR reseed; reads return 0
- What: With DummyInstructions = 1, a CSR write op (WRITE/SET/CLEAR, not READ) asserts
  dummy_instr_seed_en_o for one cycle with dummy_instr_seed_o = csr_wdata_int. The value is not
  stored; any read returns 0. M-mode only (0x7C1 is an M-level address).
- Observable at: csrr read-back on rvfi_rd_wdata = 0 for every read; rvfi_trap = 0 in M-mode, 1 in
  U-mode; a write op flushes the pipeline (csr_pipe_flush, rtl/ibex_id_stage.sv:593-597) and a
  demoted read does not; the reseed pulse has no boundary footprint (dummies are not on RVFI) -
  probe candidate P7 (PROPOSED in gen_probe_register.md, Critic ruling pending):
  cs_registers_i.dummy_instr_seed_en_o / dummy_instr_seed_o (rtl/ibex_cs_registers.sv:1914-1915),
  coverage only, never a fire-check or checker input (rtl-arch T-053 UNOBSERVABLE rows).
- Config: cpuctrlsts.dummy_instr_en for an observable effect.
- Source: doc: cs_registers.rst "Security Feature Seed Register (secureseed)"; security.rst "Dummy
  Instruction Insertion" | RTL-defined: rtl/ibex_cs_registers.sv:673-675, 1913-1915, 1927-1928
- Edge: no
- Status: ACTIVE

### F-CSR-093: secureseed RMW semantics: csrrs writes rs1, csrrc writes 0, csrrsi/csrrci with
uimm = 0 do not reseed
- What: Folded into F-CSR-092: the SET/CLEAR and uimm = 0 forms are the parent's own rule ("a CSR
  write op (WRITE/SET/CLEAR, not READ) pulses the reseed with csr_wdata_int; reads return 0")
  evaluated per op form: rdata = 0 makes SET carry wdata and CLEAR carry 0, and the demoted x0 /
  uimm = 0 forms are READs (Critic M-9); carried by the parent's op-form bins.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1001-1009, 1914-1915; rtl/ibex_decoder.sv:255-258
- Edge: yes, of F-CSR-092
- Status: FOLDED into F-CSR-092 (bin CG-CSR-010.cr_op_form_gap.csrrs_nz_flush, csrrc_nz_flush, csrrsi_0_g1, csrrci_0_g1; CG-CSR-010.cp_seed_val.zero; the probe-gated cr_op_form_pulse bins are coverage-only)

### F-CSR-094: mseccfg (0x747) RW with MML/MMWP/RLB; mseccfgh (0x757) read-only zero; reset 0
- What: Accessible because PMPEnable = 1 and cheriot Off. Bits 31:3 of mseccfg read 0. mseccfgh
  ignores writes. Field semantics for PMP checking belong to the PMP part.
- Observable at: rvfi_rd_wdata.
- Config: mseccfg.
- Source: spec: machine.adoc "Machine Security Configuration (mseccfg) Register" (address/ presence
  only) | doc: cs_registers.rst "Machine Security Configuration (mseccfg/mseccfgh)" | RTL-defined:
  rtl/ibex_cs_registers.sv:503-522, 1502-1527
- Edge: no
- Status: ACTIVE

### F-CSR-095: mseccfg WARL: MML and MMWP are sticky once set; RLB cannot be set while any region
is locked with RLB = 0
- What: pmp_mseccfg_d.mml = mml_q ? 1 : wdata[0] (same for mmwp); rlb_d = any_pmp_entry_locked ? 0 :
  wdata[2], where any_pmp_entry_locked = |(lock & ~rlb_q). Writing 0 to MML after 1 reads 1; writing
  RLB = 1 with a locked region reads 0; with RLB already 1, locked regions do not block keeping RLB
  = 1 (pmp_cfg_locked is 0 while rlb_q = 1).
- Observable at: rvfi_rd_wdata.
- Config: mseccfg, pmpcfg lock bits.
- Source: doc: cs_registers.rst "Machine Security Configuration (mseccfg/mseccfgh)" | RTL-defined:
  rtl/ibex_cs_registers.sv:1463, 1504-1514
- Edge: yes, of F-CSR-094
- Status: ACTIVE
- Notes: Detailed PMP/Smepmp semantics are owned by the PMP part; listed here as CSR legalisation
  only.

### F-CSR-096: PMP CSRs pmpcfg0-3 (0x3A0-0x3A3) and pmpaddr0-15 (0x3B0-0x3BF) exist and are
M-mode RW (semantics owned by the PMP part)
- What: 16 regions, G = 0 (pmpaddr read unmodified). CSR-level legalisation in the RTL: pmpcfg
  reserved bits 6:5 read 0; W = 1/R = 0 forces W = 0 when MML = 0; mode 2'b10 = NA4 (G = 0); locked
  regions ignore writes; pmpaddr[i] write blocked when region i+1 is locked TOR; MML write
  suppression of M-mode-executable configs unless RLB. Reset values from PMPRstCfg/PMPRstAddr
  parameters.
- Observable at: csrr read-back on rvfi_rd_wdata; the PMP consequences (rvfi_trap with mcause 1/5/7,
  absent data_req_o) belong to the PMP area.
- Config: pmpcfg/pmpaddr/mseccfg.
- Source: spec: machine.adoc "Physical Memory Protection CSRs" | doc: cs_registers.rst "PMP
  Configuration Register (pmpcfgx)", "PMP Address Register (pmpaddrx)" | RTL-defined:
  rtl/ibex_cs_registers.sv:525-548, 1362-1546
- Edge: no
- Status: ACTIVE
- Notes: Listed for completeness of the CSR map; do not duplicate PMP tests here.

### F-CSR-097: CHERIoT CSRs mshwm (0xBC1), mshwmb (0xBC2), cdbg_ctrl (0xBC4) raise illegal
instruction when cheriot_enable_i != IbexMuBiOn
- What: The read mux sets illegal_csr for these addresses unless cheriot is On; the write enables
  are also gated by cheriot On. With the DUT tie-off (Off) they behave exactly like unimplemented
  addresses (mcause 2, mtval = encoding), in M-mode and U-mode.
- Observable at: rvfi_trap = 1 + csrr read-back of mcause (2) / mtval (encoding) on rvfi_rd_wdata in
  M and U; the registers are never readable.
- Config: none.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:678-700, 879-884, 1299-1356
- Edge: no
- Status: ACTIVE
- Notes: cheriot-out-of-scope candidate for the register semantics (stack high-water mark, debug
  fault control). The illegal-access behaviour IS in scope and is covered by F-CSR-009/010. The
  flops exist (g_mshwm, BaseIsa = RV32IorCHERIoT) and csr_mshwm_set_i could still update mshwm_q
  internally, but nothing observes it with cheriot Off.

### F-CSR-098: CHERIoT gating of mtvec, mepc, misa, marchid, mseccfg and the PMP CSRs is inactive
with cheriot_enable_i = Off (registers behave as plain RV32)
- What: With cheriot Off: mtvec/mepc are readable and writable (not replaced by MTCC/MEPCC), misa
  reports I = 1, E = 0, X = 1 (bitmanip), marchid = 22, mseccfg/mseccfgh and pmpcfg/pmpaddr are
  accessible, mtvec MODE = 01. The CHERIoT SCR block (gen_scr) and cheriot_csr_*/
  cheriot_csr_set_mie_i/clr_mie_i inputs are quiescent (assertions IbexCheriotClrMieDisabled /
  IbexCheriotSetMieDisabled).
- Observable at: rvfi_rd_wdata of misa (0x4090_1104), marchid (0x16), mtvec, mepc, mseccfg.
- Config: none.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:373-391, 424-426, 469-484, 503-522, 707-716,
  739-743, 796-797, 807-808, 1062-1070, 1996-1997, 2003-2257
- Edge: no
- Status: ACTIVE
- Notes: cheriot-out-of-scope candidate: gen_scr (SCR reads/writes, pcc_cap, mtdc/mscratchc,
  cheriot_fatal_err_o) is only reachable with cheriot On. cheriot_fatal_err_o is constant 0 here
  (rtl/ibex_cs_registers.sv:2218-2225 requires cheriot On).

### F-CSR-099: Shadow-CSR glitch detection is not present in this DUT: csr_shadow_err_o is
constant 0 and never contributes to alert_major_internal_o
- What: ibex_core fixes ShadowCSR = 0; every ibex_csr instance in cs_registers gets ShadowCopy = 0
  or ShadowCSR = 0, so rd_error_o = 0 and csr_shadow_err_o = 0.
- Observable at: alert_major_internal_o never asserts due to CSR state (only rf ECC, PC mismatch,
  cheriot).
- Config: none.
- Source: doc: security.rst "Shadow CSRs" (feature not used when SecureIbex is set) | RTL-defined:
  rtl/ibex_core.sv:197, 1350-1351; rtl/ibex_cs_registers.sv:1986-1987; rtl/ibex_csr.sv:38-53
- Edge: no
- Status: ACTIVE
- Notes: Coverage of ibex_csr.sv gen_shadow is unreachable in this configuration; exclude it.
  Canonical entry of the shadow-CSR cluster (Section 3).

### F-CSR-100: CSR reads return pre-instruction state; CSR writes are visible to the next
instruction (program-order CSR access ordering)
- What: For every RW CSR, csrrw X then csrr returns X (after legalisation); the write commits at ID
  completion and the flush (or the mscratch/mepc bypass) guarantees the following instruction sees
  it. Counter CSRs read the value before the instruction's own retirement.
- Observable at: rvfi_rd_wdata sequences; rvfi_order.
- Config: none.
- Source: spec: zicsr.adoc "CSR Access Ordering" | RTL-defined: rtl/ibex_cs_registers.sv:1020-1025;
  rtl/ibex_id_stage.sv:595-597, 747-749
- Edge: no
- Status: ACTIVE

### F-CSR-101: Same-cycle collision: an exception entry and a software CSR write never coincide
(exception controller has priority)
- What: The write block runs first and the "exception controller gets priority" case overrides
  mstatus/mepc/mcause/mtval/priv. In practice csr_we_int (needs instr_executing in DECODE) and
  csr_save_cause_i (FLUSH/IRQ_TAKEN/DBG_TAKEN states) are mutually exclusive, so a CSR write that
  raises no exception always completes and a trapping CSR instruction never writes.
- Observable at: csrr read-back on rvfi_rd_wdata: the handler's reads of mstatus/mepc/mcause/mtval
  show the hardware trap values and the software-written value appears only if the writing
  instruction retired (rvfi_valid without rvfi_trap). The mutual exclusion itself is internal: probe
  candidate P6 (probe register entry needed): cs_registers_i.csr_we_int / csr_save_cause_i, witness
  and assertion coverage only (bound assertion gen_sva_csr_excl in gen_binds.sv), never a checker.
- Config: none.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:771, 890-891, 1020-1023; rtl/ibex_controller.sv:
  655, 725-733, 816-845
- Edge: yes, of F-CSR-100
- Status: ACTIVE
- Notes: Candidate bound assertion for the TB (gen_binds.sv, assertion coverage, not an observable):
  never (csr_we_int & csr_save_cause_i).

### F-CSR-102: CSR access with an instruction fetch error or during a flush does not write the CSR
- What: instr_kill (fetch error, wb_exception, id_exception, ~controller_run) clears
  instr_executing, so csr_op_en_o is 0 and the CSR keeps its value; an illegal CSR access also never
  writes (csr_we_int & ~illegal_csr_insn_o).
- Observable at: csrr read-back on rvfi_rd_wdata unchanged after a CSR instruction that retired with
  rvfi_trap = 1 (fetch error, PMP fetch fault, illegal CSR) or whose pc equals dpc after a debug
  entry; the debug case exists only when debug_req_i was seen in an empty-ID DECODE cycle before
  the CSR instruction entered ID: a CSR write already valid in ID completes first and dpc is the
  next pc (rtl/ibex_controller.sv:296, :700-704; rtl-arch T-053 X-7).
- Config: none.
- Source: RTL-defined: rtl/ibex_id_stage.sv:1033-1036, 1059-1062, 747-749;
  rtl/ibex_cs_registers.sv:1020-1023
- Edge: yes, of F-CSR-100
- Status: ACTIVE

### F-CSR-103: Illegal CSR access is excluded from minstret and suppresses the rd write
- What: Folded into F-CSR-009: 'rd not written, not counted in minstret' are the parent's own
  clauses (rtl/ibex_id_stage.sv:463, 1218-1219); TP-CSR-104 keeps the sentinel / minstret check.
- Edge: yes, of F-CSR-009
- Status: FOLDED into F-CSR-009 (bin CG-CSR-015.cr_cause_reexec.illegal_no)

## Features: PRV

### F-PRV-001: Two privilege modes (M = 11, U = 00); reset in M-mode
- What: priv_lvl_q resets to PRIV_LVL_M and only ever holds M or U. The current mode is exported to
  the decoder (priv_mode_id) and reported per retired instruction.
- Observable at: rvfi_mode (3 after reset, 0 in U-mode); csrr misa bit 20 = 1 (U), bit 18 = 0 (no
  S).
- Config: none.
- Source: spec: machine.adoc "Reset" (privilege mode set to M) | doc: exception_interrupts.rst
  "Privilege Modes" | RTL-defined: rtl/ibex_cs_registers.sv:987-998; rtl/ibex_pkg.sv:224-229
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-PRV-033 (rvfi_mode of the trapping instruction is its own mode, the
  handler's first retirement reports M; rvfi_intr = 1 only for interrupt/NMI entries,
  rtl/ibex_core.sv:2403-2411, CG-PRV-001.cr_trans.u_m_*).

### F-PRV-002: Trap entry (exception or interrupt) switches to M-mode and pushes the mstatus stack
- What: On csr_save_cause (not debug entry, not in debug mode): priv <= M; mstatus.MPIE <= MIE; MIE
  <= 0; MPP <= previous priv; mepc <= exception PC; mcause <= cause; mtval <= value; the nonstandard
  mstack copies of MPIE/MPP/mepc/mcause are saved for NMI recovery.
- Observable at: the first handler instruction with rvfi_mode = 3 (rvfi_intr = 1 for interrupt/NMI
  entries; for a synchronous exception it is the record after the trapped record, rvfi_pc_rdata =
  mtvec BASE, rvfi_intr = 0); csrr mstatus in handler shows MIE = 0, MPIE = old MIE, MPP = old mode;
  csrr mepc/mcause/mtval.
- Config: mstatus.MIE, mie (interrupts).
- Source: spec: machine.adoc "Privilege and Global Interrupt-Enable Stack in mstatus register" |
  doc: cs_registers.rst "Machine Status (mstatus)"; exception_interrupts.rst "Recoverable
  Non-Maskable Interrupt" | RTL-defined: rtl/ibex_cs_registers.sv:893-947, 1256-1297
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-PRV-003 (MPP = mode of the trapping instruction,
  CG-PRV-002.cr_entry.u_* / m_*), F-PRV-004 (trap with MIE = 0 saves MPIE = 0, cr_entry.m_mie0_sync)
  and F-PRV-032 (mepc source per trap class, CG-PRV-008.cr_cause_mepc; the per-class rule is
  F-CSR-041).

### F-PRV-003: Trap from U-mode records MPP = 00; trap from M-mode records MPP = 11
- What: Folded into F-PRV-002: 'MPP <= previous priv' evaluated for U and M
  (rtl/ibex_cs_registers.sv:927); bins cr_entry.u_mie0_sync, u_mie1_sync, m_mie0_sync, m_mie1_sync.
- Edge: yes, of F-PRV-002
- Status: FOLDED into F-PRV-002 (bin CG-PRV-002.cr_entry.u_mie0_sync)

### F-PRV-004: Trap taken with MIE already 0 saves MPIE = 0; interrupts stay disabled after mret
- What: Folded into F-PRV-002: 'MPIE <= MIE' with MIE = 0 (nested exception) and the mret restoring
  MIE = 0 / MPIE = 1 are the parent's and F-PRV-006's clauses at that value; bins
  cr_entry.m_mie0_sync, CG-PRV-002.cr_mret.m_0_0.
- Edge: yes, of F-PRV-002
- Status: FOLDED into F-PRV-002 (bin CG-PRV-002.cr_entry.m_mie0_sync)

### F-PRV-005: Exceptions taken while in debug mode do not update mstatus/mepc/mcause/mtval or the
double-fault flags
- What: Only priv_lvl_d <= M (already M in debug mode); csr_save_cause with debug_mode_i = 1 and no
  debug_csr_save skips every M-mode CSR update.
- Observable at: csrr read-back on rvfi_rd_wdata of mepc/mcause/mtval/mstatus/cpuctrlsts (from debug
  ROM code and after dret) unchanged after an exception executed in debug mode; rvfi_trap = 1 with
  rvfi_ext_debug_mode = 1 and the next record's rvfi_pc_rdata = DmExceptionAddr (X-1);
  double_fault_seen_o silent.
- Config: debug mode.
- Source: spec: Sdext.adoc "Debug Mode" (traps do not update mepc, mcause, mtval) | RTL-defined:
  rtl/ibex_cs_registers.sv:908, 918-946; rtl/ibex_controller.sv:831
- Edge: yes, of F-PRV-002
- Status: ACTIVE
- Notes: Canonical entry; alias: F-DBG-026 (F-PMP-099 stays ACTIVE only for the PMP-side
  observable). An ebreak executed inside debug mode is not an exception: it re-enters the debug ROM
  at DmHaltAddr with no CSR save (rtl/ibex_controller.sv:874-882), so the DmExceptionAddr /
  rvfi_trap = 1 observable above does not apply to it; TP-PRV-004 carries it as a separate case (S-2).
  The M privilege of the debug-mode exception is B6, RTL-defined (gen_bug_log.md; Sdext.adoc:51).

### F-PRV-006: mret: priv <= MPP, MIE <= MPIE, MPIE <= 1, MPP <= U, pc <= mepc,
cpuctrlsts.sync_exc_seen <= 0
- What: Standard xRET semantics with U as the least-privileged supported mode; also clears the
  double-fault tracking flag.
- Observable at: rvfi_mode of the instruction after mret; rvfi_pc_rdata of the record after the mret
  = mepc & ~1 (X-1: the mret record's own rvfi_pc_wdata is mret pc + 4); csrr mstatus afterwards
  (MPIE = 1, MPP = 00, MIE = old MPIE); csrr cpuctrlsts bit 6 = 0.
- Config: mstatus.MPP/MPIE, mepc.
- Source: spec: machine.adoc "Privilege and Global Interrupt-Enable Stack in mstatus register",
  "Trap-Return Instructions" | doc: cs_registers.rst "Machine Status (mstatus)";
  exception_interrupts.rst "Double Fault Detection" | RTL-defined: rtl/ibex_cs_registers.sv:
  953-980; rtl/ibex_controller.sv:954-960
- Edge: no
- Status: ACTIVE
- Notes: Carries the folded F-PRV-008 (mret with MPIE = 0 returns with MIE = 0 in M; interrupts are
  taken anyway on return to U per F-PRV-023, CG-PRV-002.cr_mret_irq.m_0_pending / u_0_pending).

### F-PRV-007: mret to U-mode clears mstatus.MPRV; mret with MPP = M leaves MPRV unchanged
- What: if (mpp != M) mprv <= 0. Set MPRV = 1, MPP = U, mret -> csrr mstatus (after re-entering M
  via ecall) shows MPRV = 0. With MPP = M, MPRV stays 1.
- Observable at: csrr read-back on rvfi_rd_wdata of mstatus bit 17 in the next handler; PMP
  consequence: rvfi_trap / no data_req_o for a U-mode load to an M-only region after the mret (PMP
  area).
- Config: mstatus.MPRV/MPP.
- Source: spec: machine.adoc "Memory Privilege in mstatus Register" (an mret that changes to a mode
  less privileged than M also sets MPRV = 0) | RTL-defined: rtl/ibex_cs_registers.sv:958-960
- Edge: yes, of F-PRV-006
- Status: ACTIVE
- Notes: Canonical entry; alias: F-EXC-052 (F-PMP-074 stays ACTIVE only for the PMP-side
  observable).

### F-PRV-008: mret with MPIE = 0 returns with interrupts disabled; a pending enabled interrupt is
then not taken until MIE is set
- What: Folded into F-PRV-006: 'MIE <= MPIE' at MPIE = 0 (rtl/ibex_cs_registers.sv:956); the U-mode
  target taking the interrupt anyway is F-PRV-023 / F-IRQ-008; bins cr_mret_irq.m_0_pending,
  u_0_pending.
- Edge: yes, of F-PRV-006
- Status: FOLDED into F-PRV-006 (bin CG-PRV-002.cr_mret_irq.m_0_pending)

### F-PRV-009: mret immediately after reset (MPP = U, mepc = 0) enters U-mode at PC 0
- What: Folded into F-PRV-006: an mret with the reset values (MPP = U, MPIE = 1, mepc = 0) is one
  instance of the parent's xRET rule with the parent's rvfi_mode / pc observable (v2 edge rule,
  second pass; Critic M-9); carried by the parent's transition bins.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1052-1056, 1089-1100, 953-980
- Edge: yes, of F-PRV-006
- Status: FOLDED into F-PRV-006 (bin CG-PRV-001.cp_from.reset, CG-PRV-001.cr_trans.m_u_mret)

### F-PRV-010: mret executed in U-mode raises illegal instruction (mcause 2, mtval 0x30200073)
- What: illegal_umode_insn = (priv != M) & mret_insn; the trap goes to M-mode with mepc = the mret
  PC.
- Observable at: rvfi_trap = 1 with rvfi_mode = 0; csrr read-back of mcause (2), mtval
  (0x3020_0073), mepc (mret pc) on rvfi_rd_wdata.
- Config: U-mode.
- Source: spec: machine.adoc "Trap-Return Instructions" (xRET in a less privileged mode raises
  illegal-instruction) | RTL-defined: rtl/ibex_id_stage.sv:606-611
- Edge: yes, of F-PRV-006
- Status: ACTIVE
- Notes: Canonical entry; aliases: F-ISA-037, F-EXC-010.

### F-PRV-011: mret while in NMI mode restores MPIE/MPP/mepc/mcause from the nonstandard mstack
and exits NMI mode
- What: Alias of F-IRQ-032: PRV-area perspective (mret with nmi_mode_i restores the MPIE/MPP/mepc/
  mcause CSR VALUES from the mstack copies, overriding software writes to mepc/mcause inside the
  NMI handler, rtl/ibex_cs_registers.sv:967-975; the JUMP TARGET is the current mepc_q read in the
  FLUSH cycle, i.e. a software-written mepc, rtl/ibex_if_stage.sv:246, rtl/ibex_cs_registers.sv:1028
  - RTL-defined, exception_interrupts.rst:93-100 documents only the CSR backup; rtl-arch T-053 X-23
  / prv_xcut note 5, TP-PRV-010; owner question Q4), see canonical.
- Edge: yes, of F-PRV-006
- Status: ALIAS of F-IRQ-032

### F-PRV-012: mret with an enabled interrupt pending takes the interrupt before executing the
return target (mepc of the new trap = old mepc)
- What: Alias of F-IRQ-023: PRV-area perspective (an enabled interrupt pending at mret is taken
  before the return target with mepc = old mepc and MPP = the restored mode), see canonical.
- Edge: yes, of F-PRV-006
- Status: ALIAS of F-IRQ-023

### F-PRV-013: mstatus.MPRV = 1 makes loads and stores use MPP as the privilege for PMP checks;
instruction fetches always use the current mode
- What: priv_mode_lsu_o = MPRV ? MPP : priv; priv_mode_id_o drives fetch/PMP_I and the decoder.
- Observable at: rvfi_trap = 1 + csrr read-back of mcause (5/7) and mtval (address) on
  rvfi_rd_wdata, and no data_req_o, for a data access denied under MPP privilege; instruction
  fetches keep issuing on instr_req_o with rvfi_trap = 0 when only the data privilege changes (the
  PMP area owns the region setup).
- Config: mstatus.MPRV, mstatus.MPP, PMP regions.
- Source: spec: machine.adoc "Memory Privilege in mstatus Register" | doc: cs_registers.rst "Machine
  Status (mstatus)" | RTL-defined: rtl/ibex_cs_registers.sv:996-998; rtl/ibex_core.sv: 1600-1604
- Edge: no
- Status: ACTIVE

### F-PRV-014: MPRV = 1 with MPP = M in M-mode has no effect
- What: Folded into F-PRV-013: the MPP = M value of the parent's own formula (priv_mode_lsu = MPRV ?
  MPP : priv gives M either way), same observable as the MPRV = 0 run (Critic M-9); carried by the
  parent's effective-privilege bins. The PMP-side twin F-PMP-073 is folded into F-PMP-072 the same
  way.
- Source: spec: machine.adoc "Memory Privilege in mstatus Register" | RTL-defined:
  rtl/ibex_cs_registers.sv:998
- Edge: yes, of F-PRV-013
- Status: FOLDED into F-PRV-013 (bin CG-PRV-003.cr_eff.m_1_m_load_allow, CG-PRV-003.cr_eff.m_1_m_store_allow)

### F-PRV-015: dret to U-mode does not clear mstatus.MPRV, so U-mode loads/stores can run with
MPP (possibly M) privilege
- What: The dret branch only sets priv_lvl_d = dcsr.prv. A debugger that sets mstatus.MPRV = 1, MPP
  = M, dcsr.prv = U and executes dret leaves U-mode with MPRV = 1 and MPP = M: priv_mode_lsu = M for
  all U-mode data accesses until the next trap/mret. The debug spec requires MPRV to be cleared when
  resuming into a mode less privileged than M.
- Observable at: rvfi_mode = 0 after dret while a U-mode load to an M-only PMP region retires with
  rvfi_trap = 0 and data_req_o issued (PMP area); csrr read-back on rvfi_rd_wdata of mstatus (after
  trapping back to M) shows MPRV still 1.
- Config: debug mode, dcsr.prv = 0, mstatus.MPRV = 1, MPP = 3, PMP region M-only.
- Source: spec: Sdext.adoc "Resume" (if the new privilege mode is less privileged than M-mode, MPRV
  in mstatus is cleared); machine.adoc "Memory Privilege in mstatus Register" | RTL-defined:
  rtl/ibex_cs_registers.sv:949-951
- Edge: yes, of F-PRV-013
- Status: ACTIVE
- Notes: BUG CANDIDATE B1 (RTL vs debug spec Sdext.adoc:202 'If the new privilege mode is less
  privileged than M-mode, MPRV in mstatus is cleared'; rtl/ibex_cs_registers.sv:949-951 only
  restores priv_lvl). Security-relevant: U-mode code gains M-mode PMP privilege for data accesses
  after a debugger resume. Owner question Q5; TP-PRV-014 expected-fail (B1). Canonical entry;
  aliases: F-DBG-033, F-PMP-075.

### F-PRV-016: mstatus.TW = 1 makes WFI in U-mode an immediate illegal instruction; TW = 0 lets
U-mode WFI sleep
- What: illegal_umode_insn includes (tw & wfi_insn) when priv != M: no timeout, immediate trap
  (mcause 2, mtval 0x10500073). With TW = 0 the U-mode WFI enters SLEEP like M-mode WFI.
- Observable at: rvfi_trap = 1 on wfi with rvfi_mode = 0 (TW = 1); core_busy_o drops / no retirement
  until wake (TW = 0).
- Config: mstatus.TW, privilege mode.
- Source: spec: machine.adoc "Virtualization Support in mstatus Register" (implementation may have
  WFI always raise illegal-instruction in less-privileged modes when TW = 1), "Wait for Interrupt" |
  doc: cs_registers.rst "Machine Status (mstatus)" | RTL-defined: rtl/ibex_id_stage.sv:606-608;
  rtl/ibex_controller.sv:966-967, 606-621
- Edge: no
- Status: ACTIVE
- Notes: Canonical entry; aliases: F-ISA-041, F-EXC-011. Carries the folded F-PRV-017 (M-mode WFI
  unaffected by TW, CG-PRV-005.cr_priv_tw_post.m_tw1_resume / m_tw1_irq_taken).

### F-PRV-017: M-mode WFI is unaffected by TW
- What: Folded into F-PRV-016: TW qualifies only with priv != M (rtl/ibex_id_stage.sv:606-608) - the
  parent's condition at the other privilege value; bins m_tw1_resume, m_tw1_irq_taken,
  CG-PRV-004.cr_kind_priv_trap.wfi_m_tw1_ok.
- Edge: yes, of F-PRV-016
- Status: FOLDED into F-PRV-016 (bin CG-PRV-005.cr_priv_tw_post.m_tw1_resume)

### F-PRV-018: U-mode WFI wake by an enabled interrupt takes the interrupt immediately
(mepc = wfi PC + 4, MPP = U)
- What: Alias of F-IRQ-045: PRV-area perspective (U-mode WFI with TW = 0 wakes on an enabled
  interrupt which is taken at once: mepc = wfi + 4, MPP = U), see canonical.
- Edge: yes, of F-PRV-016
- Status: ALIAS of F-IRQ-045

### F-PRV-019: M-mode WFI with MIE = 0 wakes on a pending enabled interrupt but does not trap;
execution resumes at wfi + 4
- What: Alias of F-IRQ-045: PRV-area perspective (M-mode WFI with MIE = 0 wakes on mip & mie without
  trapping and resumes at wfi + 4), see canonical.
- Edge: yes, of F-PRV-016
- Status: ALIAS of F-IRQ-045

### F-PRV-020: WFI wake sources are mip & mie (irq_pending), NMI, debug request, debug mode and
single-step; a disabled interrupt (mie bit 0) does not wake; WFI in debug mode is a NOP
- What: Alias of F-IRQ-045: PRV-area perspective (wake set = irq_pending | irq_nm | debug_req_i |
  debug_mode | single step, rtl/ibex_controller.sv:615; a disabled line does not wake; WFI in debug
  mode still passes through the one unconditional WAIT_SLEEP cycle before SLEEP exits on
  debug_mode_q, :598-604, :614-616; a stepped WFI never enters WAIT_SLEEP, FLUSH -> DBG_TAKEN_IF
  :985-987; rtl-arch T-053 X-8), see canonical.
- Edge: yes, of F-PRV-016
- Status: ALIAS of F-IRQ-045

### F-PRV-021: ECALL cause codes: 8 from U-mode, 11 from M-mode; mepc = ecall PC; mtval = 0
- What: Alias of F-EXC-023: PRV perspective (exc_cause = priv == M ? 11 : 8; mepc = ecall PC; mtval
  = 0; the ecall itself does not retire and is not counted in minstret), see canonical.
- Edge: no
- Status: ALIAS of F-EXC-023

### F-PRV-022: EBREAK without debug redirection: mcause 3, mepc = ebreak PC, mtval = 0
- What: When dcsr.ebreakm/ebreaku for the current mode is 0 (and not in debug mode), ebreak/
  c.ebreak trap as breakpoint exception; the same instruction enters debug mode when the matching
  dcsr bit is set (debug part).
- Observable at: rvfi_trap; csrr mcause = 3, mtval = 0; rvfi_insn = 0x00100073 or 0x9002.
- Config: dcsr.ebreakm/ebreaku = 0, privilege mode.
- Source: spec: machine.adoc "Environment Call and Breakpoint", "Machine Trap Value (mtval)
  Register" (ebreak mtval zero or address) | RTL-defined: rtl/ibex_controller.sv:481-483, 874-899
- Edge: no
- Status: ACTIVE

### F-PRV-023: Interrupt-enable rule: in M-mode interrupts require mstatus.MIE = 1; in U-mode they
are always enabled
- What: Alias of F-IRQ-007: PRV perspective of the interrupt-enable rule irq_enabled = MIE | (priv
  == U) (rtl/ibex_controller.sv:490): the M-mode arm is the canonical and the U-mode arm is
  F-IRQ-008; the other handle_irq masks are owned by F-IRQ-039 (debug mode and single step),
  F-IRQ-030 (NMI mode) and F-IRQ-020 (Zcmp commit step), see canonical.
- Edge: no
- Status: ALIAS of F-IRQ-007

### F-PRV-024: U-mode with mstatus.MIE = 0 and a pending enabled interrupt: the interrupt is taken
and MPIE is saved as 0
- What: Alias of F-IRQ-008: PRV-area perspective (U-mode ignores mstatus.MIE; the handler sees MPIE
  = 0, MPP = 00 when MIE was 0), see canonical.
- Edge: yes, of F-IRQ-007
- Status: ALIAS of F-IRQ-008

### F-PRV-025: DRET outside debug mode raises illegal instruction (mtval 0x7B200073); in debug mode
it restores priv from dcsr.prv and pc from dpc
- What: Alias of F-DBG-032: PRV-area perspective (dret outside debug mode: illegal instruction,
  mtval 0x7B20_0073; in debug mode priv <= dcsr.prv and pc <= dpc, rtl/ibex_id_stage.sv:603-604,
  rtl/ibex_cs_registers.sv:949-951), see canonical; the resume mechanics are DBG-owned.
- Edge: no
- Status: ALIAS of F-DBG-032

### F-PRV-026: dcsr.prv written to U before dret resumes in U-mode; written to S/H resumes in U
- What: Folded into F-DBG-012 (through F-CSR-077): dcsr.prv WARL (01/10 -> 00) followed by dret is
  F-CSR-077's own scenario; bins cr_dret_prv.u_u, s_u, h_u, m_m.
- Edge: yes, of F-DBG-012
- Status: FOLDED into F-DBG-012 (bin CG-PRV-007.cr_dret_prv.s_u)

### F-PRV-027: Debug entry records dcsr.prv = current mode and dcsr.cause, writes dpc, switches to
M-mode and leaves mstatus/mepc/mcause/mtval untouched
- What: csr_save_cause with debug_csr_save: dcsr.prv <= priv_lvl_q, dcsr.cause <= debug cause, depc
  <= exception PC, priv <= M; mstatus stack not touched.
- Observable at: csrr dcsr/dpc in debug mode; rvfi_ext_debug_mode; csrr mstatus unchanged.
- Config: debug_req_i, dcsr.step, ebreakm/ebreaku, trigger.
- Source: spec: Sdext.adoc "Halt" (dcsr.cause, dcsr.prv updated) | RTL-defined:
  rtl/ibex_cs_registers.sv:908-917
- Edge: no
- Status: ACTIVE
- Notes: Entry mechanics (which PC goes to dpc) belong to the debug part.

### F-PRV-028: SRET, URET, SFENCE.VMA and other PRIV encodings are illegal; ECALL/EBREAK/MRET/DRET/
WFI with rs1 or rd != 0 are illegal
- What: SYSTEM funct3 = 000 accepts only imm 0x000 (ecall), 0x001 (ebreak), 0x302 (mret), 0x7B2
  (dret), 0x105 (wfi), each with rs1 = rd = 0; everything else (0x102 sret, 0x002 uret, 0x120
  sfence.vma, 0x7B3, ...) is an illegal instruction.
- Observable at: rvfi_trap = 1 + csrr read-back of mcause (2) / mtval (encoding) on rvfi_rd_wdata.
- Config: none.
- Source: spec: machine.adoc "Trap-Return Instructions" (SRET should raise illegal-instruction when
  S-mode unsupported) | RTL-defined: rtl/ibex_decoder.sv:730-758
- Edge: no
- Status: ACTIVE

### F-PRV-029: Interrupt mcause values and M-mode priority: fast irq (0x8000_0010 + id, lowest id
first) > external (0x8000_000B) > software (0x8000_0003) > timer (0x8000_0007); NMI 0x8000_001F
- What: Alias of F-IRQ-009: PRV-area perspective (mcause encodings 0x8000_0010 + id,
  0x8000_000B/3/7, 0x8000_001F and the priority chain fast > external > software > timer; vector =
  mtvec.BASE + 4*cause), see canonical.
- Edge: no
- Status: ALIAS of F-IRQ-009

### F-PRV-030: Trap vector: exceptions jump to mtvec.BASE, interrupts to BASE + 4*cause[4:0]
(NMI -> BASE + 0x7C), debug exceptions to the debug exception address
- What: MODE is fixed vectored (F-CSR-035); exception PC selection is EXC_PC_EXC (BASE), EXC_PC_IRQ
  (BASE + 4*id), EXC_PC_DBD/DBG_EXC in debug (debug part).
- Observable at: rvfi_pc_rdata of the first handler record (X-1); instr_addr_o only with the icache
  disabled or for DmExceptionAddr (X-21).
- Config: mtvec.
- Source: spec: machine.adoc "Machine Trap-Vector Base-Address (mtvec) Register" | doc:
  exception_interrupts.rst (interrupts handled in vectored mode; NMI at +0x7C) | RTL-defined:
  rtl/ibex_controller.sv:726-727, 829-831; rtl/ibex_cs_registers.sv:1030
- Edge: no
- Status: ACTIVE

### F-PRV-031: NMI ignores mstatus.MIE and mie, is taken from U or M, blocks all interrupts while in
NMI mode, and nested NMIs are not taken
- What: Alias of F-IRQ-030: PRV-area perspective (NMI ignores MIE/mie, is taken from U or M, blocks
  interrupts in NMI mode, nested NMIs are not taken; MPP = mode at NMI, MIE cleared, mstack saved),
  see canonical.
- Edge: yes, of F-PRV-029
- Status: ALIAS of F-IRQ-030

### F-PRV-032: mepc for interrupts is the PC of the next unexecuted instruction; for synchronous
exceptions the PC of the faulting instruction; for load/store errors the PC of the memory
instruction in WB even when a younger instruction is in ID
- What: Folded into F-PRV-002: 'mepc <= exception PC' per source (pc_if / pc_id / pc_wb) is the
  parent's mepc clause and F-CSR-041's rule - a checker bullet, not a new stimulus (bins
  cr_cause_mepc.*).
- Edge: yes, of F-PRV-002
- Status: FOLDED into F-PRV-002 (bin CG-PRV-008.cr_cause_mepc.exc_pc_wb_younger)

### F-PRV-033: Privilege mode of the trapping instruction is what rvfi_mode reports; the handler's
first instruction reports M
- What: Folded into F-PRV-001: rvfi_mode reporting (trapping instruction in its own mode, handler
  entry in M; rvfi_intr only on interrupt/NMI entries) is the parent's observable, not a new stimulus
  (rtl/ibex_core.sv:2078, 1778-1781, 2403-2411).
- Edge: yes, of F-PRV-001
- Status: FOLDED into F-PRV-001 (bin CG-PRV-001.cr_trans.u_m_ecall)

### F-PRV-034: U-mode has no writable CSR at all; the only legal U-mode CSR accesses are reads of
0xC00-0xC0C / 0xC80-0xC8C under mcounteren
- What: Folded into F-CSR-014: every U-mode write form traps by the priv (csr[9:8] != 00) or
  write_ro class, and the 0x000-0x0FF / 0x400-0x4FF / 0x800-0x8FF ranges are unimplemented
  (F-CSR-009); bins cr_iclass_priv.wro_u, priv_u, unimpl_u.
- Edge: yes, of F-CSR-014
- Status: FOLDED into F-CSR-014 (bin CG-CSR-001.cr_iclass_priv.wro_u)

### F-PRV-035: mstatus.TW and MPRV are writable (U-mode implemented); write/readback of each bit
- What: Folded into F-CSR-023: TW (bit 21) and MPRV (bit 17) are two of the parent's five stored
  fields (rtl/ibex_cs_registers.sv:440-441, 780-781); bins cr_mst_fields.tw_only, mprv_only,
  mprv_tw.
- Edge: yes, of F-CSR-023
- Status: FOLDED into F-CSR-023 (bin CG-CSR-002.cr_mst_fields.mprv_tw)

### F-PRV-036: mret executed inside debug mode is legal and executes fully while debug_mode stays 1
- What: Inside debug mode the privilege is M (rtl/ibex_cs_registers.sv:908), so mret is not illegal
  (illegal_umode_insn needs priv != M, rtl/ibex_id_stage.sv:606-611) and FLUSH executes it fully:
  PC <- mepc, priv <- MPP, MIE <= MPIE, MPIE <= 1, MPP <= U, MPRV cleared when MPP != M
  (rtl/ibex_controller.sv:954-960, rtl/ibex_cs_registers.sv:953-980) while debug_mode_q stays 1: the
  core leaves the debug ROM to mepc and may run at U privilege inside debug mode. Sdext.adoc:51
  leaves privilege-changing instructions in debug mode UNSPECIFIED (same family as B6): RTL-defined.
- Observable at: the mret record with rvfi_ext_debug_mode = 1 and rvfi_trap = 0; the next record's
  rvfi_pc_rdata = mepc & ~1 and rvfi_mode = MPP with rvfi_ext_debug_mode still 1 (X-1); csrr mstatus
  afterwards; the debug-mode ebreak (re-entry at DmHaltAddr) or exception (DmExceptionAddr) that
  brings the flow back to the debug ROM.
- Config: debug mode; mstatus.MPP / mepc written by the debug program.
- Source: spec: Sdext.adoc "Debug Mode" (:51 UNSPECIFIED) | RTL-defined: rtl/ibex_controller.sv:
  954-960; rtl/ibex_cs_registers.sv:908, 953-980; rtl/ibex_id_stage.sv:606-611 (rtl-arch T-053
  fact-check Section 5 / prv_xcut note 6)
- Edge: yes, of F-PRV-006
- Status: ACTIVE
- Notes: A random program that reaches an mret inside debug mode must point mepc back into the debug
  ROM or accept running outside it in debug mode (TP-PRV-036 constraint); TP-PRV-039 is the directed
  item (bins CG-PRV-007.cr_mret_dbg.*, CG-PRV-004.cr_kind_priv_trap.mret_dbg_ok). A following dret
  restores priv from dcsr.prv as usual.


# 4.3 Areas EXC, IRQ: Synchronous exceptions; interrupts, NMI, WFI, vectoring


Scope: Ibex `opentitan` configuration (WritebackStage=1, PMPEnable=1, SecureIbex=1,
DbgTriggerEn=1, RV32ZC=RV32ZcaZcbZcmp, CHERIoT mode off). DUT is gen_dut_top = ibex_core +
register file. All CHERIoT-only exception paths (ExcCauseCheriFault, cheriot_*_err) are out of
scope and are not listed.

Observability convention used below: ibex_core has NO rvfi_csr_* ports (rtl/ibex_core.sv:136-181).
CSR values written by a trap are observed by a following csrr in the handler whose result appears
on rvfi_rd_wdata (with rvfi_insn showing the csrr); written below as "csrr read-back on
rvfi_rd_wdata". Trap taken is visible as rvfi_trap on the trapping instruction
(rtl/ibex_core.sv:140,1885-1888), the handler fetch as instr_req_o/instr_addr_o (written
"instr_addr_o = <vector>"), the first handler instruction on rvfi_pc_rdata, and interrupt entry as
rvfi_intr / rvfi_ext_irq_valid. Internal nets (cs_registers_i.*, controller state, fetch FIFO bits)
are NOT observables (Critic C-07/C-08); where a bin would need one, fcov_exc_irq.md lists it as a
probe candidate with the boundary derivation first.

Status convention (fix pass after Critic verdict v1): every block carries `- Status: ACTIVE` |
`- Status: ALIAS of F-<id>` | `- Status: FOLDED into F-<id> (bin <name>)`. Edge rule (C-12):
`Edge: yes` is kept only where the What names a stimulus condition or timing coincidence the parent
does not AND the observable or the expected outcome differs; restatements are FOLDED into the named
parent bin of fcov_exc_irq.md. Depth-2 edge chains point at the base feature (C-13). Doc defects
use the canonical D-numbers and bug candidates the canonical B-numbers of the fix brief
(dv/auto_dv/work/dv-lead/parts/README_FIX_BRIEF.md).

## Reference tables derived from RTL

RTL exception priority (WritebackStage=1), highest first, rtl/ibex_controller.sv:314-332:
  1. store_err_q (store access fault, instruction in WB)
  2. load_err_q (load access fault, instruction in WB)
  3. instr_fetch_err (instruction access fault, instruction in ID)
  4. illegal_insn_q (illegal instruction, ID)
  5. ecall_insn (ID)
  6. ebrk_insn (ID)
Items 1-2 belong to the OLDER instruction (in WB); items 3-6 to the instruction in ID. The spec
priority table (machine.adoc "Synchronous exception priority in decreasing priority order") only
orders exceptions of ONE instruction: instr addr breakpoint > instr access fault > {illegal,
instr addr misaligned, ecall, ebreak, ld/st addr breakpoint} > [ld/st misaligned] > ld/st access
fault > [ld/st misaligned]. The RTL ordering is consistent with it: within one instruction only
fetch-err vs illegal (fetch-err wins, spec agrees) and illegal vs ecall/ebreak (illegal wins,
same spec priority class; only reachable with rs1/rd != 0 which is not a valid ECALL/EBREAK
encoding) can co-occur. Load/store faults are on the older instruction and must win by program
order. Instruction address breakpoints (triggers) enter debug mode before the instruction is
decoded (rtl/ibex_cs_registers.sv:1855,1871-1874) and never produce a breakpoint exception.

RTL interrupt priority, highest first, rtl/ibex_controller.sv:736-758 and 503-511:
  1. NMI: external irq_nm_i (cause 31) over internal integrity NMI (cause 0 with irq_int)
  2. irq_fast_i[0] (cause 16) ... irq_fast_i[14] (cause 30): lowest index wins
  3. irq_external_i (cause 11)
  4. irq_software_i (cause 3)
  5. irq_timer_i (cause 7, the fall-through "else")
Spec (machine.adoc "Machine Interrupt (mip and mie) Registers"): MEI > MSI > MTI for standard
causes; bits 16+ platform-defined, "typically chosen to have the highest service priority"; NMI
highest by definition (machine.adoc "Non-Maskable Interrupts"). No disagreement for standard
causes. Fast-IRQ ordering and NMI-over-fast are Ibex/platform choices (doc
exception_interrupts.rst "Interrupts" lines 52-57 states them).
## Features: EXC
### F-EXC-001: Synchronous exception trap entry (common mechanism)
- What: When the instruction in ID (or a load/store in WB) raises a synchronous exception the
  controller goes DECODE -> FLUSH, kills the pipeline, sets the PC to the mtvec base, switches to
  M-mode, writes mepc/mcause/mtval, and updates mstatus (MPIE<-MIE, MIE<-0, MPP<-priv). The mstack
  backup CSRs are also loaded on every trap.
- Observable at: instr_req_o/instr_addr_o = {mtvec[31:8],8'h00}; rvfi_trap = 1 on the faulting
  instruction; rvfi_pc_rdata of the next retired instruction = mtvec base with rvfi_intr = 0; csrr
  read-back of mepc/mcause/mtval/mstatus on rvfi_rd_wdata; crash_dump_o.exception_pc/exception_addr.
- Config: mtvec base; privilege mode; mstatus.MIE.
- Source: spec tools/specs/riscv-isa-manual/src/priv/machine.adoc "Privilege and Global
  Interrupt-Enable Stack in mstatus register", "Machine Trap-Vector Base-Address (mtvec) Register",
  "Machine Exception Program Counter (mepc) Register", "Machine Cause (mcause) Register" | doc:
  doc/03_reference/exception_interrupts.rst "Exceptions and Interrupts" (lines 6-11) | RTL-defined:
  rtl/ibex_controller.sv:664-679,816-845; rtl/ibex_cs_registers.sv:890-933;
  rtl/ibex_if_stage.sv:222-224
- Edge: no
- Status: ACTIVE
- Notes: mstack (mstatus.MPIE/MPP, mepc, mcause backup) is written on EVERY trap including
  exceptions (rtl/ibex_cs_registers.sv:933,751-755); it is only consumed by mret in NMI mode.

### F-EXC-002: All synchronous exceptions vector to mtvec base (never base+4*cause)
- What: mtvec.MODE is fixed to 1 (vectored) but the exception PC mux always selects {mtvec[31:8],
  8'h00} for synchronous exceptions; only interrupts are vectored.
- Observable at: instr_addr_o = {mtvec[31:8],8'h00} after the trap (never base + 4*cause);
  rvfi_pc_rdata of the first handler instruction.
- Config: mtvec base.
- Source: spec machine.adoc "Machine Trap-Vector Base-Address (mtvec) Register" (Vectored: sync
  exceptions to base) | doc exception_interrupts.rst lines 9-10 | RTL-defined:
  rtl/ibex_if_stage.sv:222-224,231
- Edge: no
- Status: ACTIVE

### F-EXC-003: Instruction access fault from instruction-side bus error (instr_err_i)
- What: A fetch that returns instr_err_i=1 is marked in the prefetch buffer; when that instruction
  reaches ID with instr_valid the controller raises cause 1 (ExcCauseInstrAccessFault), mepc = PC of
  the instruction, mtval = PC of the faulting word.
- Observable at: rvfi_trap on the faulting instruction; csrr read-back on rvfi_rd_wdata of mcause
  (1), mepc (= rvfi_pc_rdata of the trapped instruction) and mtval (= faulting fetch address);
  instr_addr_o = {mtvec[31:8],8'h00}.
- Config: none (PMP off for the address).
- Source: spec machine.adoc "Machine Cause (mcause) Register" (code 1), "Machine Trap Value (mtval)
  Register" (faulting address on instruction access fault) | doc exception_interrupts.rst
  "Exceptions" table code 1; doc/03_reference/instruction_fetch.rst line 70 | doc defect D10:
  cs_registers.rst:235 says mtval is 0 for exceptions other than LSU errors and illegal instruction;
  RTL writes the faulting fetch address (rtl/ibex_controller.sv:861) | RTL-defined:
  rtl/ibex_if_stage.sv:430,606-607; rtl/ibex_controller.sv:233,320-321,849,859-862
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D10 (cs_registers.rst:235): the checker follows the RTL and the ISA spec (mtval
  = faulting address). TP-EXC-001..004/006/044/071 are `Expected: pass (doc mismatch D10)`.
  Bus/fetch-side counterpart (Critic M-10): F-IMEM-011 owns the beat marking, the travel of the
  error with the word and the RF/LSU suppression; this entry owns the cause/CSR effect.

### F-EXC-004: Instruction access fault from PMP fetch violation
- What: pmp_req_err[PMP_I] on the fetch address is merged into if_instr_err and produces the same
  cause-1 exception with mtval = PC; the fetch is still issued on the bus (PMP I-side error is not
  gating instr_req_o; only the D-side request is gated).
- Observable at: rvfi_trap; csrr read-back of mcause (1), mepc and mtval (= pc) on rvfi_rd_wdata;
  instr_req_o/instr_addr_o still issued for the denied fetch address (ibus monitor).
- Config: pmpcfg/pmpaddr regions covering the fetch address; privilege mode (U-mode fetch without X
  permission, or M-mode with MML/MMWP settings).
- Source: spec machine.adoc "Physical Memory Protection" (access fault on violation) | RTL- defined:
  rtl/ibex_core.sv:597-598; rtl/ibex_if_stage.sv:426-427,430
- Edge: no
- Status: ACTIVE
- Notes: PMP region semantics belong to the PMP area; only the exception reporting is here.

### F-EXC-005: Fault on the second half of a misaligned 32-bit instruction
- What: A 32-bit instruction whose first half is at addr[1]=1 needs two fetches; if only the second
  word faults (bus error or PMP), instr_fetch_err_plus2 is set and mtval = PC + 2 while mepc = PC
  (start of the instruction).
- Observable at: rvfi_trap + csrr read-back of mcause (1) and mtval (= mepc + 2) on rvfi_rd_wdata;
  instr_addr_o = {mtvec[31:8],8'h00}; the ibus monitor shows the error (instr_err_i or PMP deny)
  only on the second fetch word.
- Config: PMP boundary at a 4-byte boundary that splits the instruction (for the PMP variant).
- Source: spec machine.adoc "Machine Trap Value (mtval) Register" ("portion of the instruction that
  caused the fault", mepc points to beginning) | RTL-defined: rtl/ibex_if_stage.sv:434-435, 607;
  rtl/ibex_controller.sv:861
- Edge: yes, of F-EXC-003
- Status: ACTIVE
- Notes: if_instr_err_plus2 is cleared when the first half also faults (& ~pmp_err_if_i), so a
  double fault reports the first-half address.

### F-EXC-006: Fetch error on an instruction that is never executed does not trap
- What: Fetch errors are attached to the instruction word and only raise an exception when that
  instruction becomes valid in ID. Prefetched words discarded by a branch, jump, exception or mret
  (pc_set) never trap.
- Observable at: instr_err_i = 1 response for a word the ibus monitor sees discarded by a redirect
  (instr_addr_o jumps away) followed by no rvfi_trap and no instr_addr_o = {mtvec[31:8],8'h00}
  fetch; the rvfi_valid stream continues at the redirect target.
- Config: none
- Source: spec machine.adoc "Machine Cause (mcause) Register" note ("Instruction address- misaligned
  exceptions are raised by control-flow ... rather than by the act of fetching") | RTL-defined:
  rtl/ibex_controller.sv:233; rtl/ibex_if_stage.sv:568-570
- Edge: yes, of F-EXC-003
- Status: ACTIVE

### F-EXC-007: Fetch error and illegal instruction bits on the same instruction
- What: When a fetch-errored word also decodes as illegal, the instruction access fault (cause 1) is
  reported, not illegal instruction.
- Observable at: rvfi_trap + csrr read-back of mcause (1, not 2) and mtval (= pc, not the
  instruction bits) on rvfi_rd_wdata.
- Config: none
- Source: spec machine.adoc "Synchronous exception priority" (access fault above illegal) |
  RTL-defined: rtl/ibex_controller.sv:320-323
- Edge: yes, of F-EXC-003
- Status: ACTIVE

### F-EXC-008: Illegal instruction exception from decoder
- What: Any encoding the decoder rejects raises cause 2 (ExcCauseIllegalInsn) with mepc = PC of the
  instruction and mtval = the faulting instruction bits.
- Observable at: rvfi_trap; csrr read-back of mcause (2) and mtval (= rvfi_insn, 32-bit) on
  rvfi_rd_wdata; instr_addr_o = {mtvec[31:8],8'h00}.
- Config: none
- Source: spec machine.adoc "Machine Cause (mcause) Register" (code 2), "Machine Trap Value (mtval)
  Register" (faulting instruction bits, right-justified) | doc exception_interrupts.rst "Exceptions"
  code 2; doc/03_reference/cs_registers.rst "Machine Trap Value (mtval)" line 233 | RTL-defined:
  rtl/ibex_id_stage.sv:610-611; rtl/ibex_controller.sv:255,322-323,864-869
- Edge: no
- Status: ACTIVE

### F-EXC-009: Illegal instruction from CSR access checks (dcsr/dpc/dscratch0/1 trap outside debug mode; trigger CSRs do not)
- What: A CSR instruction is illegal if the CSR does not exist (illegal_csr), if it writes a
  read-only CSR (addr[11:10] == 2'b11 with a write op), if the CSR privilege (addr[9:8]) exceeds the
  current mode, or if a debug-mode-only CSR (dcsr 0x7B0, dpc 0x7B1, dscratch0/1 0x7B2/0x7B3) is
  accessed outside debug mode. The trigger CSRs tselect/tdata1/tdata2/tdata3 (0x7A0-0x7A3) are legal
  from M-mode with DbgTriggerEn = 1: reads return the trigger state and M-mode writes are dropped
  (write enables gated by debug_mode_i); they never raise cause 2 outside debug mode.
- Observable at: rvfi_trap on the CSR instruction + csrr read-back of mcause (2) and mtval (= the
  CSR encoding) on rvfi_rd_wdata; for tselect/tdata* in M-mode the access retires with rvfi_trap = 0
  and rvfi_rd_wdata = the trigger state.
- Config: privilege mode; debug mode.
- Source: spec machine.adoc "Machine Cause (mcause) Register";
  tools/specs/riscv-isa-manual/src/priv/csrs.adoc:60-63 (0x7A0-0x7AF accessible to machine mode,
  0x7B0-0x7BF only visible to debug mode) | doc cs_registers.rst:345 (tselect "Accessible in Debug
  Mode or M-Mode") | doc defect D12: debug.rst:54-55 says all debug registers incl. tselect/tdata
  are Debug-Mode only and trap otherwise; RTL allows M-mode reads and drops M-mode writes |
  RTL-defined: rtl/ibex_cs_registers.sv:402-406 (illegal_csr_dbg = dbg_csr & ~debug_mode_i), 550-565
  (dbg_csr set only in the dcsr/dpc/dscratch0/1 arms), 636-651 (tselect/tdata*: illegal_csr =
  ~DbgTriggerEn only), 1775-1779 (trigger write enables require debug_mode_i);
  rtl/ibex_id_stage.sv:610-611; rtl/ibex_pkg.sv:518,526
- Edge: no
- Status: ACTIVE
- Notes: Critic C-02: tselect/tdata removed from the trapping list (doc defect D12). CSR field
  semantics belong to the CSR/DBG areas (F-CSR-017 / F-DBG-050 carry the debug-CSR access rules);
  only the trap consequence is listed here.

### F-EXC-010: MRET in U-mode is an illegal instruction
- What: Alias of F-PRV-010: EXC perspective (cause 2, mtval 0x30200073 for mret in U-mode), see
  canonical.
- Observable at: as F-PRV-010: rvfi_trap + csrr read-back of mcause (2) / mtval on rvfi_rd_wdata.
- Config: privilege mode U (via prior mret with MPP=U).
- Source: spec machine.adoc "Trap-Return Instructions" (xRET in a less privileged mode raises
  illegal-instruction) | RTL-defined: rtl/ibex_id_stage.sv:606-608
- Edge: no
- Status: ALIAS of F-PRV-010

### F-EXC-011: WFI in U-mode with mstatus.TW=1 is an illegal instruction
- What: Alias of F-PRV-016: EXC perspective (cause 2, mtval 0x10500073 for wfi in U-mode with TW =
  1; TW = 0 sleeps, see F-IRQ-053), see canonical.
- Observable at: as F-PRV-016: rvfi_trap + csrr read-back of mcause (2) / mtval on rvfi_rd_wdata;
  instr_req_o never idles (no sleep).
- Config: mstatus.TW; privilege mode U.
- Source: spec machine.adoc "Wait for Interrupt" (may raise illegal-instruction when TW=1) | doc
  cs_registers.rst "Machine Status (mstatus)" bit 21 | RTL-defined: rtl/ibex_id_stage.sv: 606-608
- Edge: no
- Status: ALIAS of F-PRV-016

### F-EXC-012: DRET outside debug mode is an illegal instruction
- What: Alias of F-DBG-032: EXC perspective (cause 2, mtval 0x7b200073 for dret outside debug mode),
  see canonical.
- Observable at: as F-DBG-032: rvfi_trap + csrr read-back of mcause (2) / mtval on rvfi_rd_wdata.
- Config: not in debug mode.
- Source: RTL-defined: rtl/ibex_id_stage.sv:604 (debug spec makes dret outside debug mode illegal;
  belongs to debug area)
- Edge: no
- Status: ALIAS of F-DBG-032

### F-EXC-013: SYSTEM instructions with rs1/rd != 0 are illegal (illegal wins over ECALL/EBREAK)
- What: The decoder asserts ecall_insn_o/ebrk_insn_o/mret/wfi/dret from instr[31:20] and separately
  asserts illegal_insn when rs1 or rd is non-zero. The controller priority picks illegal_insn_q over
  ecall/ebreak, so mcause=2 with mtval = the encoding.
- Observable at: rvfi_trap + csrr read-back of mcause (2, not 8/11/3) and mtval (= the encoding) on
  rvfi_rd_wdata.
- Config: none
- Source: spec machine.adoc "Synchronous exception priority" (illegal and ecall in same class;
  implementation choice) | RTL-defined: rtl/ibex_decoder.sv:730-758; rtl/ibex_controller.sv: 322-327
- Edge: yes, of F-EXC-008
- Status: ACTIVE
- Notes: Canonical for the ISA alias F-ISA-042 (M-10 pass).

### F-EXC-014: Illegal compressed instruction: mtval holds the 16-bit encoding zero-extended
- What: For an illegal 16-bit instruction mtval = {16'b0, instr_compressed} and mepc = the
  2-byte-aligned PC of the compressed instruction.
- Observable at: rvfi_trap + csrr read-back on rvfi_rd_wdata of mtval ([31:16] = 0, [15:0] = the
  compressed encoding) and mepc (bit 1 kept: mepc[1:0] = 2'b10 at pc % 4 == 2).
- Config: none
- Source: spec machine.adoc "Machine Trap Value (mtval) Register" (shortest of the faulting
  instruction, right-justified) | doc instruction_fetch.rst line 22 | RTL-defined:
  rtl/ibex_controller.sv:866-868
- Edge: yes, of F-EXC-008
- Status: ACTIVE

### F-EXC-015: Zcmp reserved rlist raises illegal instruction, sequence not started
- What: Alias of F-CMP-044: EXC perspective (cm.push/cm.pop* with rlist 0..3 is reserved: the
  compressed decoder flags illegal_instr_o on the first micro-op, the sequence is not started and
  the trap is a normal illegal instruction with mtval = the zero-extended halfword), see canonical.
  Correction (RTL rtl/ibex_compressed_decoder.sv:626-640, 198-207): gets_expanded is set to
  INSTR_EXPANDED before the rlist check and is gated to INSTR_NOT_EXPANDED only by valid_i, so the
  trap record carries rvfi_ext_expanded_insn_valid = 1, as F-CMP-044 states; the former "no
  rvfi_ext_expanded_insn_valid" sentence here was wrong. The trap record's rvfi_insn is the 32-bit
  first micro-op and the 16-bit cm.* word is on rvfi_ext_expanded_insn (rtl/ibex_core.sv:2263-2277;
  fact-check X-14); mtval = zext16(cm.* word) (rtl/ibex_controller.sv:866-868).
- Edge: yes, of F-EXC-008
- Status: ALIAS of F-CMP-044

### F-EXC-016: Illegal instruction in ID waits for an outstanding WB load/store
- What: An illegal instruction stalls in ID (stall_mem) while a load/store is outstanding in WB; if
  the WB access faults, the WB fault is taken and the illegal instruction is discarded; else the
  illegal instruction trap is taken after the response.
- Observable at: rvfi_trap on the load/store (WB fault) vs on the illegal instruction; csrr
  read-back of mcause (5/7 vs 2) on rvfi_rd_wdata; cycle of instr_addr_o = {mtvec[31:8],8'h00}
  relative to data_rvalid_i.
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:985-989,1095-1096; rtl/ibex_controller.sv:314-323,
  676-678
- Edge: yes, of F-EXC-008
- Status: ACTIVE

### F-EXC-017: Breakpoint exception from EBREAK (dcsr.ebreakm/ebreaku clear)
- What: ebreak in M-mode with dcsr.ebreakm=0 (or U-mode with ebreaku=0) raises cause 3 with mepc =
  address of the EBREAK itself and mtval = 0.
- Observable at: rvfi_trap on the ebreak; csrr read-back on rvfi_rd_wdata of mcause (3), mepc (=
  ebreak pc) and mtval (0); instr_addr_o = {mtvec[31:8],8'h00} (not DmHaltAddr).
- Config: dcsr.ebreakm, dcsr.ebreaku (written in debug mode); privilege mode.
- Source: spec machine.adoc "Environment Call and Breakpoint" (epc = address of EBREAK; mtval zero
  or address) ; tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Environment Call and Breakpoints"
  | doc exception_interrupts.rst "Exceptions" code 3; cs_registers.rst "Debug Control and Status
  Register (dcsr)" bits 15/12 | RTL-defined: rtl/ibex_controller.sv:481-483, 874-899;
  rtl/ibex_cs_registers.sv:1039-1040
- Edge: no
- Status: ACTIVE

### F-EXC-018: C.EBREAK behaves as EBREAK
- What: Alias of F-ISA-034: EXC perspective (c.ebreak 0x9002 takes the same cause-3 / debug-entry
  path as ebreak; mepc/dpc 2-byte aligned), see canonical.
- Observable at: as F-ISA-034: rvfi_trap + csrr read-back of mcause (3) / mepc on rvfi_rd_wdata, or
  instr_addr_o = DmHaltAddr; rvfi_insn = 32'h00009002 (a compressed, non-expanded instruction is
  traced as the zero-extended halfword, rtl/ibex_core.sv:2263-2265, fact-check X-14; never the
  expanded 0x00100073).
- Config: as F-EXC-017.
- Source: spec machine.adoc "Environment Call and Breakpoint" note (c.ebreak same operation) |
  RTL-defined: rtl/ibex_controller.sv:874-899
- Edge: yes, of F-EXC-017
- Status: ALIAS of F-ISA-034

### F-EXC-019: EBREAK enters debug mode when dcsr.ebreakm/ebreaku is set
- What: Alias of F-DBG-017: EXC perspective (ebreak with dcsr.ebreakm/ebreaku set enters debug mode
  instead of raising cause 3: no mepc/mcause/mtval/mstatus update, no rvfi_trap), see canonical.
- Observable at: as F-DBG-017: instr_addr_o = DmHaltAddr; rvfi_trap = 0 for the ebreak;
  rvfi_ext_debug_mode = 1 afterwards; csrr read-back of dcsr.cause (1) / dpc on rvfi_rd_wdata.
- Config: dcsr.ebreakm/ebreaku; privilege mode.
- Source: doc cs_registers.rst "dcsr" bits 15/12 | RTL-defined: rtl/ibex_controller.sv:481-483,
  785-814,875-883; rtl/ibex_cs_registers.sv:910-917; rtl/ibex_core.sv:1885-1886
- Edge: no
- Status: ALIAS of F-DBG-017

### F-EXC-020: EBREAK while already in debug mode re-enters debug mode without CSR update
- What: Alias of F-DBG-023: EXC perspective (ebreak in debug mode re-enters at DmHaltAddr without a
  dcsr/dpc update), see canonical.
- Observable at: as F-DBG-023: instr_addr_o = DmHaltAddr; csrr read-back of dpc/dcsr on
  rvfi_rd_wdata unchanged.
- Config: debug mode.
- Source: RTL-defined: rtl/ibex_controller.sv:785-814 (comment 786-791), 875-883
- Edge: yes, of F-EXC-019
- Status: ALIAS of F-DBG-023

### F-EXC-021: Hardware trigger (instruction address breakpoint) enters debug mode, never a breakpoint exception
- What: Alias of F-TRG-010: EXC perspective (a hardware trigger match enters debug mode with
  dcsr.cause = 2 and dpc = tdata2 and never raises a breakpoint exception; tdata1.action is fixed to
  1), see canonical.
- Edge: no
- Status: ALIAS of F-TRG-010

### F-EXC-022: Trigger match discarded when control flow changes
- What: Alias of F-TRG-021: EXC perspective (a trigger match on pc_if is discarded when the
  instruction in ID redirects the PC, so no debug entry occurs), see canonical.
- Edge: yes, of F-TRG-010
- Status: ALIAS of F-TRG-021

### F-EXC-023: ECALL from M-mode (cause 11) and from U-mode (cause 8)
- What: ecall raises cause 11 from M-mode and cause 8 from U-mode; mepc = ECALL pc, mtval = 0, priv
  <- M, mstatus.MPP = the previous privilege (M or U); the ecall itself does not retire (not counted
  in minstret); subsequent M-level CSR accesses in the handler succeed.
- Observable at: rvfi_trap on the ecall; csrr read-back on rvfi_rd_wdata of mcause (11 or 8), mepc
  and mstatus.MPP (3 or 0); rvfi_mode of the handler = 3.
- Config: privilege mode (M or U).
- Source: spec machine.adoc "Environment Call and Breakpoint"; rv32.adoc "Environment Call and
  Breakpoints" | doc exception_interrupts.rst "Exceptions" codes 8 and 11 | RTL-defined:
  rtl/ibex_controller.sv:870-873; rtl/ibex_cs_registers.sv:908,927
- Edge: no
- Status: ACTIVE
- Notes: F-EXC-024 (U-mode ECALL) is folded here as bin CG-EXC-005.cp_priv.u (Critic C-12 pattern
  b). Canonical for the PRV alias F-PRV-021 (Critic M-10).

### F-EXC-024: ECALL from U-mode
- What: Folded into F-EXC-023 (bin CG-EXC-005.cp_priv.u): U-mode ECALL is the parent's privilege
  variable at another value (cause 8, MPP = U).
- Observable at: rvfi_trap + csrr read-back of mcause (8) and mstatus.MPP (0) on rvfi_rd_wdata;
  rvfi_mode 0 before, 3 in the handler.
- Config: privilege mode U.
- Source: spec machine.adoc "Environment Call and Breakpoint" | doc exception_interrupts.rst code 8
  | RTL-defined: rtl/ibex_controller.sv:870-873; rtl/ibex_cs_registers.sv:908,927
- Edge: yes, of F-EXC-023
- Status: FOLDED into F-EXC-023 (bin CG-EXC-005.cp_priv.u)

### F-EXC-025: Load access fault from data bus error response
- What: A load whose response has data_err_i=1 raises cause 5 from the WB stage: mepc = PC of the
  load (pc_wb), mtval = the access address (lsu_addr_last), rd is NOT written.
- Observable at: rvfi_trap on the load after the data_err_i response (rvfi_mem_addr = the access
  address, rvfi_mem_rmask = 0 on the WB-trap record, rtl/ibex_core.sv:2156, 2164; fact-check X-15);
  csrr read-back on rvfi_rd_wdata of mcause (5), mepc (= load pc) and mtval (= access address);
  rvfi_rd_addr = 0 (no RF write).
- Config: none
- Source: spec machine.adoc "Machine Cause (mcause) Register" (code 5), "Machine Trap Value (mtval)
  Register" (faulting address) | doc exception_interrupts.rst code 5; cs_registers.rst "mtval" line
  231; load_store_unit.rst line 93 | RTL-defined: rtl/ibex_load_store_unit.sv: 688-698,746;
  rtl/ibex_controller.sv:275-276,314-317,837-840,914-927; rtl/ibex_wb_stage.sv: 115-116,198
- Edge: no
- Status: ACTIVE

### F-EXC-026: Load/store access fault from PMP (no bus request issued)
- What: pmp_req_err[PMP_D] during the address phase gates data_req_o off; the LSU FSM treats
  pmp_err_q as the response and reports cause 5 (load) or cause 7 (store) with mtval = access
  address. Stores follow the same path with data_we (formerly F-EXC-028).
- Observable at: data_req_o stays low for the denied word (dbus monitor); rvfi_trap; csrr read-back
  of mcause (5/7) and mtval on rvfi_rd_wdata.
- Config: pmpcfg/pmpaddr; privilege mode; mstatus.MPRV/MPP (priv_mode_lsu).
- Source: spec machine.adoc "Physical Memory Protection" | RTL-defined: rtl/ibex_core.sv:1063;
  rtl/ibex_load_store_unit.sv:472,688-694,746-747; rtl/ibex_cs_registers.sv:998
- Edge: no
- Status: ACTIVE
- Notes: F-EXC-028 (store variant) is folded here as bin
  CG-EXC-006.cr_op_source_align.store_pmp_aligned.

### F-EXC-027: Store access fault from data bus error response
- What: A store whose response has data_err_i=1 raises cause 7 from WB: mepc = store PC, mtval =
  access address. The store data was already presented on the bus (no rollback).
- Observable at: data_req_o/data_we_o/data_wdata_o issued for the store (dbus monitor), then
  rvfi_trap; csrr read-back of mcause (7), mepc and mtval on rvfi_rd_wdata; rvfi_mem_wmask = 0 on
  the trapped store's WB-trap record (rtl/ibex_core.sv:2157, fact-check X-15; the store is
  identified by rvfi_insn and the dbus write record).
- Config: none
- Source: spec machine.adoc "Machine Cause (mcause) Register" (code 7) | doc
  exception_interrupts.rst code 7 | RTL-defined: rtl/ibex_load_store_unit.sv:747;
  rtl/ibex_controller.sv:314-315,900-913
- Edge: no
- Status: ACTIVE
- Notes: F-EXC-039 (memory modified, no rollback) is folded here: the write left the core before the
  error response (bins CG-EXC-006.cr_op_source_align.store_bus_err_aligned,
  cr_source_pattern.bus_err_aligned_single_req). Spec gap: the ISA does not define memory side
  effects of a store that receives an access fault after issue; RTL-defined (the memory agent
  decides whether it committed the write).

### F-EXC-028: Store access fault from PMP (no bus request issued)
- What: Folded into F-EXC-026 (bin CG-EXC-006.cr_op_source_align.store_pmp_aligned): a PMP-denied
  store is the parent's access kind at another value (no data_req_o, cause 7).
- Observable at: data_req_o low; rvfi_trap + csrr read-back of mcause (7) / mtval on rvfi_rd_wdata.
- Config: PMP; privilege; MPRV.
- Source: RTL-defined: rtl/ibex_core.sv:1063; rtl/ibex_load_store_unit.sv:472,747
- Edge: yes, of F-EXC-026
- Status: FOLDED into F-EXC-026 (bin CG-EXC-006.cr_op_source_align.store_pmp_aligned)

### F-EXC-029: Load/store address misaligned exceptions (causes 4 and 6) are never raised
- What: Misaligned word/halfword accesses are split into two word-aligned bus accesses; no cause-4/6
  exception exists in non-CHERIoT mode. The pkg constants ExcCauseLoadAddrMisaligned/
  StoreAddrMisaligned are only used on CHERIoT paths.
- Observable at: two data_req_o for one rvfi_mem_* record; no rvfi_trap; csrr read-back of mcause is
  never 4 or 6.
- Config: none
- Source: spec machine.adoc "Machine Cause (mcause) Register" note (misaligned optional) | doc
  exception_interrupts.rst "Exceptions" table (4/6 absent); load_store_unit.rst "Misaligned
  Accesses" | RTL-defined: rtl/ibex_load_store_unit.sv:403-405; rtl/ibex_controller.sv:903,917
  (CHERIoT-only uses)
- Edge: no
- Status: ACTIVE

### F-EXC-030: Misaligned access, first half faults (bus error)
- What: The first part's error is recorded (lsu_err_q); the second bus transaction is still issued
  and its response ignored; one cause-5/7 exception with mtval = the original (unaligned) effective
  address of the access.
- Observable at: two data_req_o (dbus monitor); rvfi_trap; csrr read-back on rvfi_rd_wdata of mtval
  (= rvfi_mem_addr, the unaligned effective address) and mcause (5/7).
- Config: none
- Source: spec machine.adoc "Machine Trap Value (mtval) Register" (address of the portion that
  faulted) | doc load_store_unit.rst lines 78-79; cs_registers.rst "mtval" line 232 | RTL- defined:
  rtl/ibex_load_store_unit.sv:258,503-531 (514,520),688
- Edge: yes, of F-EXC-025
- Status: ACTIVE
- Notes: F-EXC-034 (both halves fault) is folded here as bin
  CG-EXC-006.cr_align_mtval.mis_both_eq_addr: the ignored second response is also in error, same
  single trap and mtval. Bus-side view (M-10 pass): F-DMEM-021 owns the second-beat issue and the
  ignored response; this entry owns the cause/mtval effect.

### F-EXC-031: Misaligned access, second half faults (bus error)
- What: The first half completes; the second word's error produces the exception with mtval = the
  word-aligned address of the second half (addr_last updated on addr_incr_req).
- Observable at: rvfi_trap + csrr read-back on rvfi_rd_wdata of mtval (= (rvfi_mem_addr & ~3) + 4)
  and mcause (5/7); rvfi_rd_addr = 0 for loads.
- Config: none
- Source: doc cs_registers.rst "mtval" line 232 ("address of the missing transaction part") |
  RTL-defined: rtl/ibex_load_store_unit.sv:258,546-560 (555),688,746-747
- Edge: yes, of F-EXC-025
- Status: ACTIVE
- Notes: Bus-side view (Critic M-10): F-DMEM-022 owns which beat of the pair carries data_err_i and
  the rdata_q capture of the clean first beat; this entry owns the cause/mtval effect.

### F-EXC-032: Misaligned access, second half PMP-faults
- What: Alias of F-PMP-088: EXC perspective (PMP is checked on both word addresses; a violation on
  the second word only is reported as cause 5/7 with mtval = the second-half word address after the
  first word's bus access completed), see canonical. Decision (Critic M-10): PMP owns the per-word
  bus activity and the mtval address choice, and this entry stated both sides, so it is the alias.
- Edge: yes, of F-EXC-026
- Status: ALIAS of F-PMP-088

### F-EXC-033: Misaligned access, first half PMP-faults
- What: Alias of F-PMP-087: EXC perspective (misaligned access whose first half is PMP-denied: the
  second half is still issued if its own check passes, one cause-5/7 trap with mtval = original
  address), see canonical.
- Observable at: as F-PMP-087: data_req_o pattern (second half only); rvfi_trap + csrr read-back of
  mcause / mtval on rvfi_rd_wdata.
- Config: PMP region starting on a 4-byte boundary the access straddles.
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:472,489-501,503-531,807-808 (fcov
  ls_mis_pmp_err_1); rtl/ibex_core.sv:1063
- Edge: yes, of F-EXC-026
- Status: ALIAS of F-PMP-087

### F-EXC-034: Misaligned access, both halves fault
- What: Folded into F-EXC-025 (through F-EXC-030) (bin CG-EXC-006.cr_align_mtval.mis_both_eq_addr):
  both halves faulting is the parent's scenario with the ignored second response also in error; same
  single trap and mtval.
- Observable at: single rvfi_trap + csrr read-back of mtval (= unaligned address) on rvfi_rd_wdata;
  two data_req_o.
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:514,520,688
- Edge: yes, of F-EXC-025
- Status: FOLDED into F-EXC-025 (bin CG-EXC-006.cr_align_mtval.mis_both_eq_addr)

### F-EXC-035: Exception from WB (load/store fault) while a younger instruction is in ID
- What: The WB fault has priority; the ID instruction is killed (instr_kill via wb_exception),
  performs no RF write, no CSR write, no LSU request, and no PC change; mepc = pc_wb. The killed
  instruction is re-fetched after mret.
- Observable at: rvfi_trap on the load/store only; the younger instruction has no rvfi_valid until
  re-executed after mret; no data_req_o from it (dbus monitor) and no CSR side effect in the csrr
  read-backs; csrr read-back of mepc = the load/store pc.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:311-317,336-337,676-678,837-840;
  rtl/ibex_id_stage.sv:1033-1036,1054-1062,1083-1084
- Edge: no
- Status: ACTIVE

### F-EXC-036: WB fault while the ID instruction would itself trap
- What: If ID holds an illegal/ecall/ebreak/fetch-errored instruction when the WB load/store faults,
  only the WB fault is reported (store_err_q/load_err_q above all ID causes); exc_req_q for the ID
  instruction is dropped in FLUSH.
- Observable at: single rvfi_trap (on the load/store) + csrr read-back of mcause (5/7, not
  1/2/3/8/11) on rvfi_rd_wdata.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:255,268-270,314-327
- Edge: yes, of F-EXC-035
- Status: ACTIVE

### F-EXC-037: WB fault while ID holds a jump/branch (speculative PC redirect)
- What: Branch/jump requests use instr_executing_spec, which does not factor in an outstanding dmem
  access or an incoming error; a taken branch / jal / jalr redirects IF to its target in its FIRST ID
  cycle, before the WB error response, and FLUSH then redirects to the exception vector
  (rtl/ibex_id_stage.sv:889-941, 1054-1057; fact-check TP-EXC-036 row). A not-taken branch, a
  load-dependent branch / jalr (stall_ld_hz) and a branch arriving in the error cycle do not
  redirect. Architecturally the branch is not retired.
- Observable at: instr_addr_o sequence (younger branch/jump target, then the exception vector) on
  the ibus monitor; rvfi shows only the trapping load/store.
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:1047-1057 (comment); rtl/ibex_controller.sv:
  681-688,816-831
- Edge: yes, of F-EXC-035
- Status: ACTIVE

### F-EXC-038: WB fault while ID holds the next load/store
- What: Folded into F-EXC-035: the parent already states that the killed ID instruction performs no
  LSU request; a load/store in ID is one row of that statement with the parent's no-data_req_o
  observable (v2 edge rule, second pass; Critic M-9); carried by the parent's younger-instruction
  bins.
- Source: RTL-defined: rtl/ibex_id_stage.sv:1015-1019,1059-1062,1083-1084,1095-1096;
  rtl/ibex_load_store_unit.sv:748-752 (comment)
- Edge: yes, of F-EXC-035
- Status: FOLDED into F-EXC-035 (bin CG-EXC-006.cp_younger.load_store, CG-EXC-006.cr_op_younger.load_load_store)

### F-EXC-039: Store fault after the store data has been sent (no rollback)
- What: Folded into F-EXC-027 (bin CG-EXC-006.cr_op_source_align.store_bus_err_aligned): the store
  data on data_wdata_o before the error response is the parent's own observable ("no rollback").
- Observable at: data_we_o/data_wdata_o observed before rvfi_trap; rvfi_mem_addr (wmask is 0 on the
  WB-trap record, X-15) on the trapped
  store.
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:747; rtl/ibex_wb_stage.sv:208-209
- Edge: yes, of F-EXC-027
- Status: FOLDED into F-EXC-027 (bin CG-EXC-006.cr_op_source_align.store_bus_err_aligned)

### F-EXC-040: Back-to-back loads where the older one faults
- What: Folded into F-EXC-035 (through F-EXC-038) (bin CG-EXC-006.cr_op_younger.load_load_store):
  the younger load's request is blocked on the error cycle exactly as the parent states for any
  younger load/store.
- Observable at: exactly one data_req_o for the pair; single rvfi_trap.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:336-337; rtl/ibex_id_stage.sv:1015-1019,1059-1062
- Edge: yes, of F-EXC-035
- Status: FOLDED into F-EXC-035 (bin CG-EXC-006.cr_op_younger.load_load_store)

### F-EXC-041: Exception priority selection (RTL order vs spec table)
- What: The FLUSH-state cause mux selects exactly one of store_err > load_err > instr_fetch_err >
  illegal > ecall > ebreak (one-hot assertion IbexExceptionPrioOnehot).
- Observable at: rvfi_trap + csrr read-back of mcause on rvfi_rd_wdata for constructed collisions
  (F-EXC-007, F-EXC-013, F-EXC-036).
- Config: none
- Source: spec machine.adoc "Synchronous exception priority in decreasing priority order" |
  RTL-defined: rtl/ibex_controller.sv:299-337,373-383,848-951
- Edge: no
- Status: ACTIVE
- Notes: See the reference table at the top; no spec disagreement found. Coverage should cross every
  reachable pair.

### F-EXC-042: Exception on a compressed instruction: mepc alignment
- What: Folded into F-EXC-001: mepc = the 2-byte-aligned PC of a compressed instruction is the
  parent's mepc = faulting PC at a pc % 4 == 2 value; mepc[1] writability is F-CSR-039 (v2 edge
  rule, second pass; Critic M-9); carried by the trap-CSR alignment bins.
- Source: spec machine.adoc "Machine Exception Program Counter (mepc) Register" (mepc[0] always
  zero; IALIGN=16 keeps bit 1) | RTL-defined: rtl/ibex_cs_registers.sv:729,893-905,928-929
- Edge: yes, of F-EXC-001
- Status: FOLDED into F-EXC-001 (bin CG-EXC-012.cp_mepc_bit1.bit1_1, CG-EXC-012.cr_kind_bit1.sync_bit1_1; CG-EXC-001.cr_cause_priv_ilen.illegal_m_c16)

### F-EXC-043: Load/store fault inside a Zcmp cm.push sequence
- What: All micro-ops of an expanded cm.push share pc_id = PC of the cm.push (IF holds pc_if during
  expansion). A store fault on micro-op k reports mepc = cm.push PC, mtval = faulting address; the
  expander state is flushed (flush_expanded on PC_EXC). After mret the whole sequence re-executes
  (earlier stores repeat, sp unchanged since the sp update is the LAST op).
- Observable at: rvfi_trap with rvfi_pc_rdata = cm.push PC; rvfi_ext_expanded_insn*; repeated
  data_req_o after mret.
- Config: none
- Source: RTL-defined: rtl/ibex_if_stage.sv:483,808-809; rtl/ibex_compressed_decoder.sv: 626-681;
  rtl/ibex_controller.sv:837-840
- Edge: yes, of F-EXC-027
- Status: ACTIVE

### F-EXC-044: Load fault inside a Zcmp cm.pop/cm.popret/cm.popretz sequence
- What: Loads are the INSTR_EXPANDED micro-ops; sp increment, a0 zeroing and ret are
  INSTR_EXPANDED_COMMIT/LAST and issue only after all loads. A load fault gives mepc = cm.pop PC and
  leaves sp intact, so the sequence is restartable.
- Observable at: rvfi_trap with rvfi_pc_rdata = cm.pop pc; no rvfi_rd_addr = 2 (sp) write before the
  trap record; after mret the sequence restarts (data_req_o addresses repeat).
- Config: none
- Source: RTL-defined: rtl/ibex_compressed_decoder.sv:691-769 (744,751,760,769)
- Edge: yes, of F-EXC-025
- Status: ACTIVE

### F-EXC-045: Fetch fault on the return target of cm.popret
- What: Folded into F-EXC-003: the fault is attributed to the target instruction by the parent's own
  rule; the cm.popret return is one control-transfer source (the CTI-side statement is F-BTALU-010)
  (v2 edge rule, second pass; Critic M-9); carried by the parent's flow bins.
- Source: RTL-defined: rtl/ibex_compressed_decoder.sv:765-769; rtl/ibex_controller.sv:233
- Edge: yes, of F-EXC-003
- Status: FOLDED into F-EXC-003 (bin CG-EXC-002.cp_flow.popret_target, CG-EXC-002.cr_flow_outcome.popret_target_trap; CG-EXC-008.cp_event.fetch_fault_ret_target)

### F-EXC-046: Exception while in debug mode jumps to DmExceptionAddr; privilege forced to M (RTL-defined)
- What: Any synchronous exception with debug_mode_q=1 selects EXC_PC_DBG_EXC (DmExceptionAddr);
  mepc/mcause/mtval/mstatus/dpc/dcsr are NOT written; debug mode is retained; priv_lvl is forced to
  M by the trap path.
- Observable at: instr_addr_o = DmExceptionAddr; csrr read-back of
  mepc/mcause/mtval/mstatus/dpc/dcsr on rvfi_rd_wdata unchanged; rvfi_ext_debug_mode = 1; rvfi_mode
  = 3 for the debug-program instructions after the exception (also when dcsr.prv was U).
- Config: debug mode; dcsr.prv.
- Source: doc/03_reference/debug.rst:22 parameter table (DmExceptionAddr) | spec
  tools/specs/riscv-debug-spec/Sdext.adoc:32 (all operations in debug mode execute with machine-mode
  privilege), :51 (instructions that change the privilege mode have UNSPECIFIED behaviour in debug
  mode) | RTL-defined: rtl/ibex_controller.sv:831; rtl/ibex_if_stage.sv:230;
  rtl/ibex_cs_registers.sv:908,918-919,949-951
- Edge: no
- Status: ACTIVE
- Notes: B6 RECLASSIFIED (Critic C-20): priv_lvl_d = PRIV_LVL_M at rtl/ibex_cs_registers.sv:908 also
  runs for exceptions taken in debug mode, so a debug session that set dcsr.prv = U (or lowered
  priv_lvl by an mret in debug mode) runs at M privilege after the exception until dret restores
  dcsr.prv (:949-951). The debug spec says debug mode executes at M privilege (Sdext.adoc:32) and
  leaves privilege changes in debug mode UNSPECIFIED (:51): RTL-defined, not a spec contradiction,
  not a bug candidate. The checker follows the RTL (rvfi_mode = M), TP-EXC-046 is `Expected: pass`,
  owner question 6 is closed.

### F-EXC-047: Exception in debug mode does not arm double-fault detection
- What: Alias of F-SEC-022: EXC perspective (exceptions taken in debug mode neither arm
  sync_exc_seen nor pulse double_fault_seen_o), see canonical.
- Observable at: as F-SEC-023: double_fault_seen_o stays 0; csrr read-back of cpuctrlsts on
  rvfi_rd_wdata unchanged.
- Config: debug mode; cpuctrlsts.sync_exc_seen=1 beforehand.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:918,935-945
- Edge: yes, of F-EXC-054
- Status: ALIAS of F-SEC-022

### F-EXC-048: Exception simultaneous with debug_req or single-step: CSRs updated, then debug entry at the handler
- What: Alias of F-DBG-004: EXC perspective (an exception in FLUSH with debug_req_i or dcsr.step
  asserted writes mepc/mcause/mtval/mstatus normally and then enters debug mode at the handler: dpc
  = mtvec base, dcsr.cause 3 or 4, no handler instruction executes; ebreak-into-debug has priority
  over both), see canonical.
- Edge: yes, of F-EXC-001
- Status: ALIAS of F-DBG-004

### F-EXC-049: mstatus/privilege update on trap entry
- What: On every trap (exception or interrupt) taken outside debug mode: priv <- M, mstatus.MPIE <-
  MIE, MIE <- 0, MPP <- previous priv; MPRV and TW unchanged.
- Observable at: csrr read-back of mstatus on rvfi_rd_wdata in the handler: bit 3 (MIE) = 0, bit 7
  (MPIE) = old MIE, bits 12:11 (MPP) = old priv, bits 17 (MPRV) and 21 (TW) unchanged.
- Config: mstatus.MIE; privilege mode.
- Source: spec machine.adoc "Privilege and Global Interrupt-Enable Stack in mstatus register" | doc
  cs_registers.rst "Machine Status (mstatus)" line 132 | RTL-defined: rtl/ibex_cs_registers.sv
  :908,923-927
- Edge: no
- Status: ACTIVE

### F-EXC-050: MRET: return from trap
- What: mret (M-mode) sets PC <- mepc, priv <- MPP, MIE <- MPIE, MPIE <- 1, MPP <- U, and MPRV <- 0
  when MPP != M; the pipeline is flushed (FLUSH state, PC_ERET). Also clears
  cpuctrlsts.sync_exc_seen and exits NMI mode if active.
- Observable at: instr_addr_o = mepc (icache off); the NEXT record's rvfi_pc_rdata = mepc (the mret
  record's rvfi_pc_wdata is the next sequential fetch address, never mepc: pc_wdata is captured at ID
  exit while PC_ERET is set one cycle later in FLUSH, rtl/ibex_core.sv:2084,
  rtl/ibex_controller.sv:954-956; fact-check X-1); csrr read-back of mstatus and
  cpuctrlsts.sync_exc_seen (0) on rvfi_rd_wdata afterwards; rvfi_mode change on the next retirement.
- Config: mepc; mstatus.MPP/MPIE/MPRV; nmi_mode.
- Source: spec machine.adoc "Privilege and Global Interrupt-Enable Stack in mstatus register",
  "Trap-Return Instructions" | doc exception_interrupts.rst line 11, cs_registers.rst line 133 |
  RTL-defined: rtl/ibex_controller.sv:954-960; rtl/ibex_if_stage.sv:246; rtl/ibex_cs_registers.sv
  :953-980
- Edge: no
- Status: ACTIVE

### F-EXC-051: MRET with mepc[1]=1 (2-byte aligned return)
- What: Folded into F-EXC-050: a return to a 2-byte-aligned mepc is the parent's PC <- mepc with
  mepc[1] = 1 (mepc bit 0 always 0, F-CSR-039), same instr_addr_o / rvfi_pc_rdata observable (v2
  edge rule, second pass; Critic M-9); carried by the mepc alignment bins (single owner CG-EXC-012).
- Source: spec machine.adoc "Machine Exception Program Counter (mepc) Register" | RTL-defined:
  rtl/ibex_cs_registers.sv:729
- Edge: yes, of F-EXC-050
- Status: FOLDED into F-EXC-050 (bin CG-EXC-012.cp_mepc_bit1.bit1_1, CG-EXC-012.cr_kind_bit1.sync_bit1_1)

### F-EXC-052: MRET clears MPRV only when returning to U-mode
- What: Alias of F-PRV-007: EXC perspective (mret clears mstatus.MPRV only when MPP = U), see
  canonical.
- Observable at: as F-PRV-007: csrr read-back of mstatus bit 17 on rvfi_rd_wdata after the mret.
- Config: mstatus.MPRV=1; mstatus.MPP.
- Source: spec machine.adoc privstack ("If y != M, xRET also sets MPRV=0") | RTL-defined:
  rtl/ibex_cs_registers.sv:958-960
- Edge: yes, of F-EXC-050
- Status: ALIAS of F-PRV-007

### F-EXC-053: mstatus.MPP WARL: unsupported values written as U (doc says M)
- What: Alias of F-CSR-024: EXC perspective (mstatus.MPP written 01/10 reads U and mret returns to
  U-mode), see canonical.
- Observable at: as F-CSR-024: csrr read-back of mstatus bits 12:11 on rvfi_rd_wdata; rvfi_mode
  after the mret.
- Config: mstatus write.
- Source: spec machine.adoc privstack ("xPP fields are WARL ... can hold only ... implemented
  privilege mode") | doc cs_registers.rst "Machine Status (mstatus)" line 138 | RTL-defined:
  rtl/ibex_cs_registers.sv:783-786
- Edge: yes, of F-EXC-050
- Status: ALIAS of F-CSR-024
- Notes: Doc defect D2 (cs_registers.rst:138 says unsupported MPP values are interpreted as Machine
  Mode; RTL legalises to U, a spec-legal WARL choice). Owner question 3.

### F-EXC-054: Double fault detection (cpuctrlsts.sync_exc_seen / double_fault_seen_o)
- What: Alias of F-SEC-022: EXC perspective (any synchronous exception outside debug mode sets
  cpuctrlsts.sync_exc_seen, mret clears it, a second one pulses double_fault_seen_o), see canonical.
  Parent of the EXC double-fault edges F-EXC-055/056/059 (F-EXC-058 folded).
- Observable at: as F-SEC-022: double_fault_seen_o; csrr read-back of cpuctrlsts bits 7:6 on
  rvfi_rd_wdata.
- Config: cpuctrlsts.sync_exc_seen (software writable).
- Source: doc exception_interrupts.rst "Double Fault Detection"; cs_registers.rst "cpuctrlsts" bits
  7/6 | RTL-defined: rtl/ibex_cs_registers.sv:935-945,964-965,1967-1968; rtl/ibex_core.sv: 131
- Edge: no
- Status: ALIAS of F-SEC-022

### F-EXC-055: Interrupts do not arm or trigger double-fault detection
- What: Interrupt traps (irq_ext or irq_int set) do not set sync_exc_seen and are not counted as
  double faults even when sync_exc_seen=1.
- Observable at: double_fault_seen_o = 0 on the interrupt entry inside an exception handler; csrr
  read-back of cpuctrlsts on rvfi_rd_wdata: sync_exc_seen unchanged, double_fault_seen 0.
- Config: sync_exc_seen=1; pending interrupt with MIE re-enabled in handler.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:935
- Edge: yes, of F-SEC-022
- Status: ACTIVE
- Notes: Canonical for the SEC alias F-SEC-024 (M-10 pass).

### F-EXC-056: mret from an interrupt handler also clears sync_exc_seen
- What: Any mret clears sync_exc_seen, including an mret returning from an interrupt taken inside an
  exception handler; a later exception in the still-running exception handler is then not detected
  as a double fault.
- Observable at: double_fault_seen_o = 0 on the second exception of that sequence; csrr read-back of
  cpuctrlsts.sync_exc_seen on rvfi_rd_wdata = 0 after the interrupt handler's mret.
- Config: MIE re-enabled inside exception handler; pending interrupt.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:953-965
- Edge: yes, of F-SEC-022
- Status: ACTIVE
- Notes: Bug candidate B12: the checker follows the documented intent (an mret that returns from a
  nested interrupt handler must not disarm detection); TP-EXC-056 is expected-fail (B12). Owner
  question 5.

### F-EXC-057: Software writes to cpuctrlsts.sync_exc_seen / double_fault_seen
- What: Alias of F-SEC-025: EXC perspective (software RW of cpuctrlsts.sync_exc_seen /
  double_fault_seen; writes never drive double_fault_seen_o), see canonical.
- Observable at: as F-SEC-025: csrr read-back of cpuctrlsts on rvfi_rd_wdata; double_fault_seen_o
  unchanged by the csrw.
- Config: cpuctrlsts write.
- Source: doc exception_interrupts.rst lines 194-195; cs_registers.rst bits 7/6 | RTL-defined:
  rtl/ibex_cs_registers.sv:874-877,1967-1968
- Edge: yes, of F-EXC-054
- Status: ALIAS of F-SEC-025

### F-EXC-058: ECALL counts as the first synchronous exception of a double fault
- What: Folded into F-EXC-054 (bin CG-EXC-010.cp_first_cause.ecall): ECALL is one row of the
  parent's "any synchronous exception" arming rule.
- Observable at: double_fault_seen_o pulse on the second trap; csrr read-back of cpuctrlsts on
  rvfi_rd_wdata.
- Config: none
- Source: RTL-defined: rtl/ibex_cs_registers.sv:935-945
- Edge: yes, of F-SEC-022
- Status: FOLDED into F-SEC-022 (bin CG-EXC-010.cp_first_cause.ecall)

### F-EXC-059: Back-to-back exceptions at the handler entry (trap storm)
- What: If the first instruction at mtvec base itself faults (e.g. fetch error at the vector or
  illegal word there), a new trap is taken with mepc = mtvec base, MPIE <- 0, and
  double_fault_seen_o pulses on every subsequent trap; the core loops without deadlock.
- Observable at: repeating instr_addr_o = {mtvec[31:8],8'h00}; double_fault_seen_o pulse train; csrr
  read-back of mepc (= mtvec base) on rvfi_rd_wdata once the imem agent ends the storm.
- Config: mtvec pointing at faulting memory.
- Source: spec machine.adoc privstack note on trap handler infinite loops | RTL-defined:
  rtl/ibex_cs_registers.sv:935-945
- Edge: yes, of F-SEC-022
- Status: ACTIVE

### F-EXC-060: Pipeline flush on exception
- What: On exception the IF stage is halted (halt_if), the ID instruction is flushed (flush_id), the
  prefetch buffer and the Zcmp expander are flushed by pc_set with PC_EXC, and any non-faulting
  instruction in WB completes first (FLUSH is entered only when ready_wb_i or wb_exception). Younger
  instructions never retire.
- Observable at: rvfi_valid gap; rvfi_order continuity; instr_req_o burst at the new pc
  (instr_addr_o = vector).
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:664-679,816-820,1020,1027;
  rtl/ibex_if_stage.sv:483,568-570 (no doc support: doc/03_reference/pipeline_details.rst:27-30
  states the writeback-stage behaviour is not documented and the file has no exception-flush text;
  Critic C-04)
- Edge: no
- Status: ACTIVE

### F-EXC-061: Pipeline flush on mret and dret
- What: mret/dret are special requests: IF halted, one FLUSH cycle, then PC set to mepc/depc;
  prefetched fall-through instructions are discarded.
- Observable at: no rvfi_valid for the instructions following the mret/dret in memory; instr_addr_o
  = mepc / dpc.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:287-293,664-679,954-965
- Edge: yes, of F-EXC-060
- Status: ACTIVE

### F-EXC-062: Exception latency and handler fetch timing
- What: Folded into F-EXC-001 (bins CG-EXC-013.cr_stage_latency.id_cause_min / wb_cause_min): the
  commit latency and the one-shot exception flops are checker bullets (gen_chk_trap_timing) on the
  parent's trap entry, not a distinct stimulus.
- Observable at: cycle distance from data_rvalid_i & data_err_i (or the ibus delivery of the
  faulting word) to the commit (pc_set = trap record - 1); the vector instr_req_o is >= the commit
  cycle (issued in the pc_set cycle only when no fill buffer holds an ungranted request,
  rtl/ibex_icache.sv:703, 764-776, 1030-1031; fact-check TP-EXC-062 row) and bus-visible only with
  the icache off; exactly one vector fetch per rvfi_trap.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:255,263-270,676-678,816-831,1030-1052
- Edge: yes, of F-EXC-001
- Status: FOLDED into F-EXC-001 (bin CG-EXC-013.cr_stage_latency.id_cause_min)

### F-EXC-063: Trapping instructions do not retire or count
- What: Folded into F-EXC-001 (bin CG-EXC-012.cp_minstret.ir0: the handler's minstret read-back is
  compared against the retirement count excluding the trap record): the retire-count exclusion of
  trapping instructions is a checker bullet on the parent (the counters area owns minstret).
- Observable at: csrr read-back of minstret on rvfi_rd_wdata before/after the trapping instruction
  (delta 0); rvfi_valid with rvfi_trap = 1.
- Config: mcountinhibit.
- Source: spec machine.adoc "Environment Call and Breakpoint" (not considered to retire) |
  RTL-defined: rtl/ibex_id_stage.sv:1218-1220; rtl/ibex_wb_stage.sv:208-209
- Edge: yes, of F-EXC-001
- Status: FOLDED into F-EXC-001 (bin CG-EXC-012.cp_minstret.ir0)

### F-EXC-064: rvfi_trap reporting of exceptions
- What: rvfi_trap is set for ID exceptions (fetch err, illegal, ecall, ebreak) and for WB exceptions
  (load/store fault) and is suppressed for EBREAK entering debug mode. The trapping instruction is
  still traced with rvfi_valid.
- Observable at: rvfi_valid & rvfi_trap; rvfi_insn; rvfi_pc_rdata.
- Config: dcsr.ebreakm/u.
- Source: RTL-defined: rtl/ibex_core.sv:1842-1853,1885-1890
- Edge: no
- Status: ACTIVE
- Notes: B14 (rtl/ibex_core.sv:1851-1853: the ID trap record is suppressed when a WB load/store
  error coincides) is downgraded to an RVFI convention note (gen_bug_log.md v1d): the killed ID
  instruction re-executes and produces its own record; TP-EXC-065 is the informational confirmation.
  Trap-record fields (fact-check X-14 / X-15, B18): rvfi_mem_rmask / wmask are zero on WB-trap
  records (:2156-2157, rvfi_mem_addr kept, :2164) and carry the garbage decode on ID-trap records;
  rvfi_insn is the 32-bit expansion for Zcmp micro-ops (:2263-2267, halfword on
  rvfi_ext_expanded_insn) and the zero-extended halfword 32'h00009002 for c.ebreak. rvfi_intr is
  never set for exception handlers (F-IRQ-057).

### F-EXC-065: mtval is written to zero for ECALL, EBREAK and interrupts
- What: csr_mtval_o defaults to 0 and is only overridden for fetch faults, illegal instruction,
  load/store faults and internal NMI; every trap writes mtval (mtval_en on csr_save_cause).
- Observable at: csrr read-back of mtval on rvfi_rd_wdata = 0 in ecall/ebreak/interrupt handlers
  even when software pre-wrote a non-zero value.
- Config: mtval pre-written by software.
- Source: spec machine.adoc "Machine Trap Value (mtval) Register" ("For other traps, mtval is set to
  zero") | doc cs_registers.rst "mtval" line 235 | RTL-defined: rtl/ibex_controller.sv: 550,870-899;
  rtl/ibex_cs_registers.sv:921-922
- Edge: yes, of F-EXC-001
- Status: ACTIVE

### F-EXC-066: crash_dump_o mirrors exception state
- What: crash_dump_o.exception_pc = mepc, exception_addr = mtval, current_pc = pc_id, next_pc =
  pc_if, last_data_addr = lsu_addr_last, continuously.
- Observable at: crash_dump_o fields after a trap.
- Config: none
- Source: doc/02_user/integration.rst ports table (crash_dump_o) | RTL-defined:
  rtl/ibex_core.sv:1325-1330; rtl/ibex_pkg.sv:16-22
- Edge: no
- Status: ACTIVE

### F-EXC-067: Instruction address misaligned (cause 0) is never raised
- What: With the C extension always present every branch/jump target is 2-byte aligned; cause 0
  cannot occur (JALR drops bit 0). ExcCauseInsnAddrMisa is only the default value of the cause mux.
- Observable at: no rvfi_trap with csrr read-back mcause = 0; after a jalr to an odd target
  instr_addr_o and rvfi_pc_rdata = target & ~1.
- Config: none
- Source: doc exception_interrupts.rst lines 128-130 | RTL-defined: rtl/ibex_controller.sv:561
- Edge: no
- Status: ACTIVE

### F-EXC-068: Exceptions cannot be disabled
- What: Illegal instruction, instruction access fault, LSU faults and ECALL are always active; there
  is no medeleg/mask.
- Observable at: rvfi_trap + csrr read-back of mcause on rvfi_rd_wdata under randomized CSR state
  (mie, mstatus, mcountinhibit, cpuctrlsts, PMP off): no CSR write suppresses the trap record.
- Config: none
- Source: doc exception_interrupts.rst line 126
- Edge: no
- Status: ACTIVE

### F-EXC-069: WB fault while the core waits to take an interrupt or enter debug
- What: If an interrupt/debug request is pending and ID is empty but WB has an outstanding
  load/store, the controller waits (id_wb_pending); if that access faults the exception path is
  taken first (exc_req_wb is a special request); an ORDINARY interrupt is then masked by MIE=0 and
  remains pending until the handler's mret or an MIE write, while an NMI ignores MIE and is taken in
  the first empty-ID DECODE after the exception's FLUSH, before the handler's first instruction
  (mepc = mtvec base, the exception's mepc/mcause pushed to mstack; rtl/ibex_controller.sv:498-500,
  704-713; rtl/ibex_cs_registers.sv:932, 967-975; fact-check X-9), and a debug request is honoured
  at the handler (F-EXC-048).
- Observable at: rvfi_trap on the load/store + csrr read-back of mcause (5/7) on rvfi_rd_wdata;
  instr_addr_o = {mtvec[31:8],8'h00} (not the interrupt vector); irq_pending_o stays high; rvfi_intr
  = 0 on the handler's first instruction (an ordinary interrupt is taken only after mret / MIE
  re-enable; an NMI's rvfi_intr retirement follows the trap record directly with mepc = mtvec base;
  a debug request is honoured at the handler with instr_addr_o = DmHaltAddr).
- Config: MIE=1; pending interrupt.
- Source: RTL-defined: rtl/ibex_controller.sv:290,296,664-679,700-721
- Edge: yes, of F-EXC-035
- Status: ACTIVE
- Notes: F-IRQ-022 (interrupt in the same cycle as a WB fault) is folded here as bin
  CG-IRQ-004.cr_ctx_outcome.wb_fault_same_cycle_deferred_by_exception.

## Features: IRQ

### F-IRQ-001: Interrupt sources and mcause encodings
- What: irq_software_i -> mcause 0x8000_0003, irq_timer_i -> 0x8000_0007, irq_external_i ->
  0x8000_000B, irq_fast_i[n] -> 0x8000_0010 + n (n = 0..14), irq_nm_i -> 0x8000_001F.
- Observable at: csrr read-back of mcause on rvfi_rd_wdata in the handler; instr_addr_o = base +
  4*id; rvfi_intr on the first handler instruction; rvfi_ext_pre_mip/post_mip.
- Config: mie bits; mstatus.MIE; privilege mode.
- Source: spec machine.adoc "Machine Cause (mcause) Register" table (3,7,11 standard; >=16 platform)
  | doc exception_interrupts.rst "Interrupts" table | RTL-defined: rtl/ibex_pkg.sv: 349-356;
  rtl/ibex_controller.sv:736-758; rtl/ibex_cs_registers.sv:487-489
- Edge: no
- Status: ACTIVE

### F-IRQ-002: Interrupt trap entry
- What: When an enabled interrupt is pending and the pipeline is empty the controller enters
  IRQ_TAKEN: mepc <- pc_if (next instruction to execute), mcause <- interrupt code, mtval <- 0,
  mstatus MPIE<-MIE/MIE<-0/MPP<-priv, priv <- M, PC <- mtvec base + 4*cause.
- Observable at: instr_addr_o = base + 4*cause; rvfi_intr = 1 on the first handler instruction;
  rvfi_ext_irq_valid level (F-IRQ-057, fact-check X-16); csrr read-back of mepc/mcause/mstatus on
  rvfi_rd_wdata.
- Config: mie, mstatus.MIE, mtvec base, privilege mode.
- Source: spec machine.adoc "Machine Interrupt (mip and mie) Registers" (trap conditions), "Machine
  Trap-Vector Base-Address (mtvec) Register" (vectored) | doc exception_interrupts.rst lines 8-10 |
  RTL-defined: rtl/ibex_controller.sv:725-762; rtl/ibex_cs_registers.sv:895-896, 918-933;
  rtl/ibex_if_stage.sv:225-228; rtl/ibex_core.sv:2405-2414
- Edge: no
- Status: ACTIVE

### F-IRQ-003: mie CSR
- What: mie bits 3 (MSIE), 7 (MTIE), 11 (MEIE) and 30:16 (fast) are writable; all other bits
  read-only 0; reset 0 (all interrupts disabled after reset).
- Observable at: csrr read-back of mie on rvfi_rd_wdata after csrw 0xFFFF_FFFF = 0x7FFF_0888; first
  csrr mie after reset = 0.
- Config: mie.
- Source: spec machine.adoc "Machine Interrupt (mip and mie) Registers" (non-writable bits read-only
  zero) | doc cs_registers.rst "Machine Interrupt Enable Register (mie)" | RTL-defined:
  rtl/ibex_cs_registers.sv:455-461,790,1103-1116; rtl/ibex_pkg.sv:712-716
- Edge: no
- Status: ACTIVE

### F-IRQ-004: mip CSR reflects the raw interrupt pins (read-only)
- What: Alias of F-CSR-032: IRQ perspective (mip mirrors the raw irq_*_i pins, not qualified by mie;
  NMI not visible; no write path), see canonical.
- Observable at: as F-CSR-032: csrr read-back of mip on rvfi_rd_wdata with lines driven and mie = 0
  equals the pin vector.
- Config: none (mie irrelevant to the read value).
- Source: spec machine.adoc "Machine Interrupt (mip and mie) Registers" (mip read-only positions;
  NMI not visible in mip) | doc cs_registers.rst "Machine Interrupt Pending Register (mip)" |
  RTL-defined: rtl/ibex_cs_registers.sv:408-412,495-501
- Edge: no
- Status: ALIAS of F-CSR-032
- Notes: Doc defect D1 (cs_registers.rst:246 says a mip bit reads one only if enabled in mie; RTL
  returns the raw pin, spec-legal). The TB models mip = pins. Owner question 4.

### F-IRQ-005: CSR write to mip is silently ignored
- What: Alias of F-CSR-033: IRQ perspective (a CSR write to mip raises no exception and changes
  nothing; the read value is the pin state; the write still flushes the pipeline), see canonical.
- Edge: yes, of F-CSR-032
- Status: ALIAS of F-CSR-033

### F-IRQ-006: irq_pending_o output semantics
- What: irq_pending_o = |(mip & mie): any locally enabled interrupt line, independent of
  mstatus.MIE, privilege mode, debug mode, NMI mode and irq_nm_i. It is the wake source for clock
  gating in ibex_top and is exported at the core boundary.
- Observable at: irq_pending_o port.
- Config: mie.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1042-1045; rtl/ibex_core.sv:124,1498;
  rtl/ibex_top.sv:325 (context only, not in DUT)
- Edge: no
- Status: ACTIVE

### F-IRQ-007: Global enable in M-mode (mstatus.MIE)
- What: In M-mode an interrupt is taken only when mstatus.MIE=1 and the mie bit is set; with MIE=0
  the interrupt stays pending (irq_pending_o=1) and is taken when MIE becomes 1 (csrs or mret
  restoring MPIE).
- Observable at: no rvfi_intr and no instr_addr_o vector fetch while MIE = 0 with irq_pending_o = 1;
  rvfi_intr on the first handler instruction right after the csrs that sets MIE; csrr read-back of
  mepc on rvfi_rd_wdata = the instruction after the csrs.
- Config: mstatus.MIE; mie.
- Source: spec machine.adoc privstack ("interrupts are globally enabled when xIE=1"), "Machine
  Interrupt (mip and mie) Registers" condition (a) | RTL-defined: rtl/ibex_controller.sv:490,
  498-500
- Edge: no
- Status: ACTIVE

### F-IRQ-008: Interrupts in U-mode ignore mstatus.MIE
- What: When priv=U, any mie-enabled interrupt is taken regardless of MIE (M-mode interrupts cannot
  be masked from a lower privilege).
- Observable at: rvfi_intr on the first handler instruction (rvfi_mode 3) after U-mode execution
  (rvfi_mode 0) with MIE = 0; csrr read-back of mstatus on rvfi_rd_wdata: MPP = 0, MPIE = 0;
  instr_addr_o = base + 4*id.
- Config: privilege U (mret with MPP=U); mstatus.MIE=0.
- Source: spec machine.adoc privstack ("Interrupts for higher-privilege modes ... always globally
  enabled"), mip/mie condition (a) | RTL-defined: rtl/ibex_controller.sv:490
- Edge: yes, of F-IRQ-007
- Status: ACTIVE

### F-IRQ-009: Interrupt priority among simultaneously pending sources
- What: NMI > fast[0..14] (lowest index first) > external > software > timer (see reference table).
  The cause is chosen in the IRQ_TAKEN cycle from the lines present then.
- Observable at: csrr read-back of mcause on rvfi_rd_wdata and instr_addr_o = base + 4*id with
  several irq_*_i lines asserted together (irq pin monitor).
- Config: mie bits for the contending sources.
- Source: spec machine.adoc "Machine Interrupt (mip and mie) Registers" (MEI > MSI > MTI; platform
  bits typically highest) | doc exception_interrupts.rst lines 52-57 | RTL-defined:
  rtl/ibex_controller.sv:503-511,736-758
- Edge: no
- Status: ACTIVE
- Notes: No disagreement with the spec for standard causes; fast-over-standard and NMI ordering are
  Ibex-defined and documented. Rows of this table folded here (Critic C-12 pattern a): F-IRQ-010
  (lowest fast index, bin CG-IRQ-002.cr_set_winner.fast_fast_fast), F-IRQ-034 (NMI over a regular
  line, bins CG-IRQ-002.cr_set_winner.nmi_*_nmi_ext), F-IRQ-063 (timer fall-through, bin
  CG-IRQ-002.cr_drain_winner.last18_timer).

### F-IRQ-010: Multiple fast interrupts pending: lowest index wins
- What: Folded into F-IRQ-009 (bins CG-IRQ-002.cr_set_winner.fast_fast_fast,
  cr_gap_winner.adjacent_fast/far_fast/ends_fast): lowest fast index first is one row of the
  parent's priority table.
- Observable at: csrr read-back of mcause on rvfi_rd_wdata (0x8000_0013 with irq_fast_i[3] and [9]
  high); instr_addr_o = base + 0x4C.
- Config: mie[30:16].
- Source: doc exception_interrupts.rst line 54 | RTL-defined: rtl/ibex_controller.sv:503-511
- Edge: yes, of F-IRQ-009
- Status: FOLDED into F-IRQ-009 (bin CG-IRQ-002.cr_set_winner.fast_fast_fast)

### F-IRQ-011: All interrupt lines pending together, drained by priority
- What: Folded into F-IRQ-009: draining all 18 lines by priority is the parent's priority table
  exercised exhaustively with the parent's mcause / vector observable (v2 edge rule, second pass;
  Critic M-9); carried by the parent's drain bins.
- Source: RTL-defined: rtl/ibex_controller.sv:746-758 (757 timer fall-through, 513 timer input
  otherwise unused)
- Edge: yes, of F-IRQ-009
- Status: FOLDED into F-IRQ-009 (bin CG-IRQ-002.cp_drain.first, middle, last18; CG-IRQ-002.cr_drain_winner.first_fast, middle_fast, middle_external, middle_software, last18_timer)

### F-IRQ-012: Vectored target address per cause
- What: PC = {mtvec[31:8], 1'b0, cause[4:0], 2'b00} = base + 4*cause: software base+0x0C, timer
  base+0x1C, external base+0x2C, fast n base+0x40+4n, NMI (and internal NMI) base+0x7C.
- Observable at: instr_addr_o = base + 4*cause at the trap; rvfi_pc_rdata of the first handler
  instruction (rvfi_intr).
- Config: mtvec base.
- Source: spec machine.adoc "Machine Trap-Vector Base-Address (mtvec) Register" ("interrupts cause
  the pc to be set to base plus four times the interrupt cause number") | doc
  exception_interrupts.rst line 10, 57 | RTL-defined: rtl/ibex_if_stage.sv:213-228
- Edge: no
- Status: ACTIVE
- Notes: F-IRQ-061 (fast 14, base + 0x78) and F-IRQ-062 (fast 0, base + 0x40) are rows of this table
  folded here (bins CG-IRQ-006.cp_id.fast[14] / fast[0]); the full sweep is TP-IRQ-004.

### F-IRQ-013: mtvec is WARL: MODE fixed to vectored, BASE 256-byte aligned
- What: Alias of F-CSR-035: IRQ perspective (mtvec WARL: MODE fixed to vectored, BASE 256-byte
  aligned, reset 0x1), see canonical.
- Observable at: as F-CSR-035: csrr read-back of mtvec on rvfi_rd_wdata after csrw 0x1234_56FE =
  0x1234_5601.
- Config: mtvec write.
- Source: spec machine.adoc "Machine Trap-Vector Base-Address (mtvec) Register" (WARL, mode may
  impose alignment) | doc cs_registers.rst "Machine Trap-Vector Base Address (mtvec)" | RTL-
  defined: rtl/ibex_cs_registers.sv:736-743,807-808,1170-1181
- Edge: no
- Status: ALIAS of F-CSR-035

### F-IRQ-014: mtvec initialised from boot_addr_i at reset
- What: Alias of F-CSR-035 (boot initialisation of mtvec from boot_addr_i; the reset PC is
  F-RST-002): IRQ perspective, see canonical. The interrupt-side observable (a reset-time NMI
  vectors to boot_addr_i[31:8] + 0x7C) is carried by F-IRQ-055.
- Observable at: as F-CSR-035 / F-RST-002: first instr_addr_o = {boot_addr_i[31:8], 8'h80}; csrr
  read-back of mtvec on rvfi_rd_wdata = {boot_addr_i[31:8], 8'h01}.
- Config: boot_addr_i (static input).
- Source: doc exception_interrupts.rst lines 13-18; integration.rst boot_addr_i row | RTL- defined:
  rtl/ibex_if_stage.sv:243,256; rtl/ibex_controller.sv:582-596; rtl/ibex_cs_registers.sv :736-741
- Edge: no
- Status: ALIAS of F-CSR-035

### F-IRQ-015: Interrupt after a software mtvec write uses the new base
- What: Folded into F-IRQ-012: the vector after a software mtvec write is the parent's formula with
  the new base (the write's pipeline flush is F-CSR-006 / F-CSR-035) (v2 edge rule, second pass;
  Critic M-9); carried by the base-class and handler-rewrite bins.
- Source: spec machine.adoc mip/mie ("evaluated immediately following ... an explicit write to a CSR
  on which these interrupt trap conditions expressly depend") | RTL-defined:
  rtl/ibex_id_stage.sv:593-597; rtl/ibex_controller.sv:287,704-721
- Edge: yes, of F-IRQ-012
- Status: FOLDED into F-IRQ-012 (bin CG-IRQ-006.cp_base_class.sw_aligned, sw_legalised; CG-IRQ-005.cp_mtvec_in_handler.rewritten, CG-IRQ-005.cr_nesting_mtvec.depth1_rewritten)

### F-IRQ-016: Interrupts are taken only between instructions with an empty pipeline
- What: IRQ_TAKEN is entered only when ID holds no valid instruction and WB is ready; the
  instruction in ID always completes (including its RF write and memory access) first (assertion
  PipeEmptyOnIrq). When the request arrives while a load/store drains in WB with its successor
  already in ID, that successor completes too, so mepc is the pc of the first not-yet-executed
  instruction (nominal 2 records after the pin edge, worst case 17; halt_if only blocks IF,
  rtl/ibex_controller.sv:296, 700-720; fact-check X-7).
- Observable at: rvfi_valid of the last instruction before the trap (its rvfi_rd_wdata / rvfi_mem_*
  effects complete); csrr read-back of mepc on rvfi_rd_wdata = its successor; rvfi_intr on the first
  handler instruction.
- Config: none
- Source: spec: interrupts are precise between instructions (machine.adoc "Machine Exception Program
  Counter (mepc) Register": address of the instruction that was interrupted) | RTL- defined:
  rtl/ibex_controller.sv:296,698-721,1078-1079
- Edge: no
- Status: ACTIVE

### F-IRQ-017: Interrupt arriving while ID is stalled on an LSU access
- What: Folded into F-IRQ-016: the parent already states that the instruction in ID completes
  "including its memory access" before IRQ_TAKEN; the LSU-stall arrival is that row with the
  parent's mepc observable (v2 edge rule, second pass; Critic M-9); carried by the parent's context
  bins.
- Source: RTL-defined: rtl/ibex_controller.sv:698-702,704-721; rtl/ibex_wb_stage.sv:115-116,185
- Edge: yes, of F-IRQ-016
- Status: FOLDED into F-IRQ-016 (bin CG-IRQ-004.cp_ctx.id_load_wait, id_store_wait; CG-IRQ-004.cr_ctx_outcome.id_load_wait_taken, id_store_wait_taken; CG-IRQ-004.cr_ctx_rvalid.id_load_wait_before_rvalid, id_load_wait_same_cycle_as_rvalid, id_load_wait_after_rvalid)

### F-IRQ-018: Interrupt taken on the cycle a stall clears
- What: If the interrupt line rises in the cycle the stalled access finishes (data_rvalid_i), the
  successor already in ID (stalled on ready_wb) completes in that cycle and retires, and DECODE ->
  IRQ_TAKEN follows once ID is empty: mepc = the pc of the first not-yet-executed instruction (the
  successor's successor or its target); only when the successor has not reached ID (fetch stall) is
  mepc = load/store pc + length (rtl/ibex_controller.sv:296, 700-713; rtl/ibex_id_stage.sv:1130-1133;
  fact-check X-7 / TP-IRQ-023 row).
- Observable at: rvfi_order continuity; csrr read-back of mepc on rvfi_rd_wdata = rvfi_pc_wdata of
  the last record before the entry (the first not-yet-executed instruction), which retires first
  after the mret (rvfi_pc_rdata).
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:704-721
- Edge: yes, of F-IRQ-016
- Status: ACTIVE

### F-IRQ-019: Interrupt during a multi-cycle ALU/multiply/divide instruction
- What: Alias of F-MUL-023: IRQ perspective (an interrupt or debug request arriving during a
  multi-cycle instruction is deferred until that instruction retires; mepc = the next PC), see
  canonical.
- Edge: yes, of F-IRQ-016
- Status: ALIAS of F-MUL-023

### F-IRQ-020: Interrupt during a Zcmp expanded sequence
- What: handle_irq is blocked during INSTR_EXPANDED_COMMIT micro-ops (sp update, a0 zero) but not
  during INSTR_EXPANDED micro-ops (the stores/loads) or the LAST op. An interrupt during the stores
  of cm.push (or loads of cm.pop) halts IF; once ID empties the trap is taken with mepc = pc_if = PC
  of the cm.* instruction (IF holds pc_if while expanding), so the whole sequence re-executes on
  mret. During COMMIT ops IF keeps issuing and the interrupt is taken after LAST with mepc = the
  following instruction (or the return target for cm.popret).
- Observable at: rvfi_ext_expanded_insn_valid/last; csrr read-back of mepc on rvfi_rd_wdata (= cm.*
  pc for an interrupt during EXPANDED micro-ops, = the following pc / return target after COMMIT
  ops); repeated data_req_o addresses after mret; rvfi_intr.
- Config: MIE=1; enabled source.
- Source: RTL-defined: rtl/ibex_controller.sv:498-500; rtl/ibex_if_stage.sv:808-809;
  rtl/ibex_compressed_decoder.sv:626,678,744,751,760,769,790,800
- Edge: yes, of F-IRQ-016
- Status: ACTIVE
- Notes: Debug entry is blocked for EXPANDED and COMMIT (rtl/ibex_controller.sv:474-477), so
  debug_req/step waits for the whole sequence, unlike interrupts. The Zcmp masking canonical is
  F-CMP-056..058 (Section 3 cluster); this entry stays ACTIVE for the interrupt-side observable
  (mepc value, deferral during COMMIT, re-execution after mret) and cross-references the CMP
  canonical.

### F-IRQ-021: Interrupt in the same cycle as an ID exception: exception wins
- What: special_req (exception) blocks the interrupt path; the exception trap is taken, MIE is
  cleared, and the interrupt stays pending until MIE is re-enabled or mret.
- Observable at: rvfi_trap on the ID instruction + csrr read-back of mcause (exception code) on
  rvfi_rd_wdata; irq_pending_o stays 1; rvfi_intr only after the handler's mret or MIE re-enable.
- Config: MIE=1.
- Source: RTL-defined: rtl/ibex_controller.sv:664-679,704 (!special_req)
- Edge: yes, of F-IRQ-016
- Status: ACTIVE

### F-IRQ-022: Interrupt in the same cycle as a WB load/store fault: exception wins
- What: Folded into F-EXC-035 (through F-EXC-069) (bin
  CG-IRQ-004.cr_ctx_outcome.wb_fault_same_cycle_deferred_by_exception): the WB-fault-beats-interrupt
  coincidence is F-EXC-069 stated from the IRQ side.
- Observable at: rvfi_trap on the load/store + csrr read-back of mcause (5/7) on rvfi_rd_wdata;
  rvfi_intr only after mret / MIE re-enable; irq_pending_o stays 1.
- Config: MIE=1.
- Source: RTL-defined: rtl/ibex_controller.sv:276,290,676-678
- Edge: yes, of F-EXC-035
- Status: FOLDED into F-EXC-035 (bin CG-IRQ-004.cr_ctx_outcome.wb_fault_same_cycle_deferred_by_exception)

### F-IRQ-023: Interrupt pending during mret
- What: mret completes (MIE <- MPIE, priv <- MPP, PC <- mepc) and the interrupt is evaluated in the
  next DECODE with the restored state: if enabled it is taken before the first instruction at mepc
  executes, with new mepc = old mepc and MPP = restored privilege.
- Observable at: instr_addr_o = mepc then immediately the vector (base + 4*id) with rvfi_intr; csrr
  read-back on rvfi_rd_wdata of mepc (unchanged value) and mstatus.MPP (the restored privilege).
- Config: MPIE=1 (or MPP=U); pending source.
- Source: spec machine.adoc mip/mie ("must also be evaluated immediately following the execution of
  an xRET instruction") | RTL-defined: rtl/ibex_controller.sv:954-960,704-721;
  rtl/ibex_cs_registers.sv:953-957
- Edge: yes, of F-IRQ-016
- Status: ACTIVE
- Notes: Folded here: F-IRQ-027 (level line held through the handler: immediate re-trap after mret,
  bin CG-IRQ-005.cr_state_reentry.still_high_same_immediate) and F-IRQ-029 (return to U-mode with a
  line pending, bin CG-IRQ-001.cr_upath_pending.mret_mpp_u_already_pending_mie0).

### F-IRQ-024: Interrupt pending during dret
- What: After dret leaves debug mode, an enabled interrupt is taken before the first instruction at
  dpc when irq_enabled = mstatus.MIE | (dcsr.prv == U) holds (rtl/ibex_controller.sv:490, 498-500;
  fact-check X-9): mepc = dpc; privilege = dcsr.prv restored then MPP = that value. With MIE = 0 and
  dcsr.prv = M execution resumes at dpc and the line stays pending.
- Observable at: instr_addr_o = dpc then the vector (base + 4*id) with rvfi_intr; csrr read-back of
  mepc (= dpc) and mstatus.MPP (= dcsr.prv) on rvfi_rd_wdata; rvfi_mode.
- Config: dcsr.prv; MIE; pending source.
- Source: RTL-defined: rtl/ibex_controller.sv:961-965,498-500; rtl/ibex_cs_registers.sv:949-951
- Edge: yes, of F-IRQ-016
- Status: ACTIVE

### F-IRQ-025: Interrupt request withdrawn before it is taken (no spurious trap)
- What: The trap decision is re-evaluated in IRQ_TAKEN (if handle_irq); if the line dropped between
  the DECODE decision and IRQ_TAKEN, no pc_set/CSR save happens and the controller returns to
  DECODE after one cycle in IRQ_TAKEN with halt_if (the prefetch buffer keeps fetching, so no ibus
  bubble is architecturally defined; fact-check TP-IRQ-030 row).
- Observable at: no rvfi_intr and no instr_addr_o vector fetch (icache off); csrr read-back of
  mepc/mcause/mstatus on rvfi_rd_wdata unchanged. The decision cycle is inferred from the pipeline
  state, never from rvfi_ext_irq_valid (a level rising at N + 4, absent when ID emptied before WB
  drained, F-IRQ-057).
- Config: MIE=1.
- Source: RTL-defined: rtl/ibex_controller.sv:729-761
- Edge: yes, of F-IRQ-002
- Status: ACTIVE

### F-IRQ-026: Higher-priority interrupt arriving one cycle before IRQ_TAKEN
- What: Folded into F-IRQ-009: the parent already states that the cause is chosen in the IRQ_TAKEN
  cycle from the lines present then; a higher-priority line arriving one cycle before is that rule
  with the parent's mcause observable (v2 edge rule, second pass; Critic M-9); carried by the
  parent's late-arrival bins.
- Source: RTL-defined: rtl/ibex_controller.sv:729-758; rtl/ibex_core.sv:1907-1932 (comment)
- Edge: yes, of F-IRQ-009
- Status: FOLDED into F-IRQ-009 (bin CG-IRQ-002.cp_late.higher_added, lower_added; CG-IRQ-002.cr_late_winner.higher_added_fast, higher_added_nmi_ext, higher_added_external, lower_added_external)

### F-IRQ-027: Level-sensitive lines held through the handler re-trap after mret
- What: Folded into F-IRQ-016 (through F-IRQ-023) (bin
  CG-IRQ-005.cr_state_reentry.still_high_same_immediate): a level line held through the handler is
  the parent's "interrupt pending during mret" with the same source.
- Observable at: repeated instr_addr_o = base + 4*id fetch right after the mret with rvfi_intr; csrr
  read-back of mepc on rvfi_rd_wdata equal across iterations.
- Config: MIE/MPIE=1.
- Source: doc exception_interrupts.rst lines 61-62 | RTL-defined: rtl/ibex_cs_registers.sv: 408-412;
  rtl/ibex_controller.sv:704-721
- Edge: yes, of F-IRQ-016
- Status: FOLDED into F-IRQ-016 (bin CG-IRQ-005.cr_state_reentry.still_high_same_immediate)

### F-IRQ-028: Software nesting by re-enabling MIE inside a handler
- What: Hardware clears MIE on entry; if the handler sets MIE=1 (after saving mepc/mstatus) any
  enabled interrupt, including lower-priority ones, is taken and overwrites mepc/mcause/mstatus; no
  hardware nesting limit; mie can be used to keep lower priorities masked.
- Observable at: nested instr_addr_o = base + 4*id fetch with rvfi_intr inside the first handler;
  csrr read-back on rvfi_rd_wdata of mepc (= an address inside the first handler) and mcause (= the
  nested cause).
- Config: MIE set by software in handler; mie mask.
- Source: doc exception_interrupts.rst "Nested Interrupt/Exception Handling" | spec machine.adoc
  privstack note on trap handlers | RTL-defined: rtl/ibex_controller.sv:498-500
- Edge: yes, of F-IRQ-007
- Status: ACTIVE

### F-IRQ-029: Handler returns to U-mode with an interrupt still pending
- What: Folded into F-IRQ-016 (through F-IRQ-023) (bin
  CG-IRQ-001.cr_upath_pending.mret_mpp_u_already_pending_mie0): the parent's MPP variable at U
  combined with F-IRQ-008 (U-mode ignores MIE).
- Observable at: csrr read-back of mstatus.MPP (0) on rvfi_rd_wdata in the nested handler; rvfi_mode
  0 -> 3 with rvfi_intr; instr_addr_o = mepc then the vector.
- Config: MPP=U; pending source; MPIE=0.
- Source: spec machine.adoc privstack | RTL-defined: rtl/ibex_controller.sv:490
- Edge: yes, of F-IRQ-016
- Status: FOLDED into F-IRQ-016 (bin CG-IRQ-001.cr_upath_pending.mret_mpp_u_already_pending_mie0)

### F-IRQ-030: Non-maskable interrupt (irq_nm_i)
- What: irq_nm_i is taken regardless of mstatus.MIE and mie: mcause 0x8000_001F, mtval 0, PC = base
  + 0x7C, mepc = next instruction, nmi_mode set; mstack saves the previous mstatus.MPIE/MPP, mepc
  and mcause for recovery. Not visible in mip and not counted in irq_pending_o. While nmi_mode is
  set, regular interrupts (mip & mie, even with MIE = 1 written by the handler) and a second
  irq_nm_i are masked until the handler's mret (formerly F-IRQ-033).
- Observable at: instr_addr_o = base + 0x7C with rvfi_intr; csrr read-back of mcause (0x8000_001F) /
  mtval (0) / mepc on rvfi_rd_wdata; rvfi_ext_nmi; no further vector fetch / rvfi_intr while
  irq_pending_o = 1 inside the handler.
- Config: none (MIE/mie irrelevant).
- Source: spec machine.adoc "Non-Maskable Interrupts" | doc exception_interrupts.rst lines 35,
  56-59, "Recoverable Non-Maskable Interrupt" | RTL-defined: rtl/ibex_controller.sv:487,498-500,
  736-745; rtl/ibex_cs_registers.sv:751-755,933,1257-1297
- Edge: no
- Status: ACTIVE
- Notes: F-IRQ-033 (regular interrupts masked in NMI mode) is an alias of this entry; F-IRQ-066
  covers nmi_mode held across a debug session inside the handler.

### F-IRQ-031: Nested NMI not supported: NMI ignored while in NMI mode, re-taken after mret
- What: While nmi_mode_q=1 a new (or still-asserted) irq_nm_i is ignored; mret exits NMI mode and an
  NMI still asserted is taken again immediately (mepc = mret target).
- Observable at: no second instr_addr_o = base + 0x7C fetch and no rvfi_intr during the handler
  while irq_nm_i is high; instr_addr_o = base + 0x7C with rvfi_intr right after the mret; csrr
  read-back of mepc = the mret target.
- Config: none
- Source: doc exception_interrupts.rst lines 58-59, 178-179 | RTL-defined:
  rtl/ibex_controller.sv:498,736,958-960
- Edge: yes, of F-IRQ-030
- Status: ACTIVE

### F-IRQ-032: mret in NMI mode restores mstatus.MPIE/MPP, mepc and mcause from mstack
- What: When nmi_mode_i=1, mret restores MPIE/MPP from mstack and rewrites mepc/mcause with the
  stacked values (the interrupted handler's context), instead of MPIE<-1/MPP<-U. The mret's jump
  target is the CURRENT mepc_q (PC_ERET = csr_mepc_i, evaluated in FLUSH before the mstack restore
  commits): a software mepc write inside the NMI handler steers the return while the post-mret
  mepc/mcause read the stacked values (rtl/ibex_if_stage.sv:246, rtl/ibex_controller.sv:954-957,
  rtl/ibex_cs_registers.sv:967-975; fact-check Section 5 RTL-defined behaviour; bin
  CG-IRQ-007.cp_mstack.sw_epc_target_used, TP-IRQ-036).
- Observable at: csrr read-back of mepc/mcause/mstatus on rvfi_rd_wdata after returning from the NMI
  into an interrupt handler (values of the interrupted handler restored).
- Config: NMI taken while inside another trap handler.
- Source: doc exception_interrupts.rst "Recoverable Non-Maskable Interrupt" | RTL-defined:
  rtl/ibex_cs_registers.sv:967-974
- Edge: yes, of F-IRQ-030
- Status: ACTIVE

### F-IRQ-033: Regular interrupts are masked while in NMI mode
- What: Alias of F-IRQ-030: regular interrupts are masked while nmi_mode is set even with MIE = 1
  written in the NMI handler (stated in the canonical What).
- Observable at: as F-IRQ-030: no instr_addr_o vector fetch / no rvfi_intr while irq_pending_o = 1
  inside the NMI handler; taken (rvfi_intr) right after its mret.
- Config: MIE=1 set inside NMI handler; pending source.
- Source: doc exception_interrupts.rst line 178 | RTL-defined: rtl/ibex_controller.sv:492-500
- Edge: yes, of F-IRQ-030
- Status: ALIAS of F-IRQ-030

### F-IRQ-034: NMI and regular interrupt in the same cycle
- What: Folded into F-IRQ-009 (bins CG-IRQ-002.cr_set_winner.nmi_fast_nmi_ext / nmi_external_nmi_ext
  / nmi_software_nmi_ext / nmi_timer_nmi_ext): NMI over a regular line in the same cycle is the top
  row of the parent's priority table.
- Observable at: csrr read-back of mcause on rvfi_rd_wdata = 0x8000_001F first (instr_addr_o = base
  + 0x7C), the regular cause after the NMI handler's mret (instr_addr_o = base + 4*id);
  irq_pending_o stays 1 in between.
- Config: MIE=1; both lines.
- Source: RTL-defined: rtl/ibex_controller.sv:736-746
- Edge: yes, of F-IRQ-009
- Status: FOLDED into F-IRQ-009 (bin CG-IRQ-002.cr_set_winner.nmi_fast_nmi_ext)

### F-IRQ-035: NMI in the same cycle as a synchronous exception
- What: The exception is taken first (special_req); the NMI is then taken immediately in the next
  DECODE (MIE does not gate it) with mepc = mtvec base (first handler instruction never executes);
  mstack captures the exception's mstatus.MPIE/MPP, mepc, mcause; mret from the NMI handler restores
  them and resumes the exception handler.
- Observable at: instr_addr_o sequence {mtvec[31:8],8'h00} then base + 0x7C (rvfi_intr on the NMI
  handler's first instruction, none for the exception handler); csrr read-back on rvfi_rd_wdata of
  mepc (= mtvec base) in the NMI handler and of mepc/mcause/mstatus after both mrets.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:664-679,704-721,736-745;
  rtl/ibex_cs_registers.sv:751-755,933,967-974
- Edge: yes, of F-IRQ-030
- Status: ACTIVE

### F-IRQ-036: Synchronous exception inside the NMI handler
- What: The exception's trap entry overwrites mstack with the NMI handler's own context. The nested
  mret (nmi_mode still 1) exits NMI mode and restores mstack (returning correctly into the NMI
  handler), but the final mret from the NMI handler is now a plain mret: mepc/mcause are not
  restored and the originally interrupted context's mepc/mcause are lost. NMIs are also re-enabled
  inside the remainder of the NMI handler.
- Observable at: csrr read-back of mepc/mcause on rvfi_rd_wdata after the final mret (stacked values
  lost); second instr_addr_o = base + 0x7C fetch with rvfi_intr during the NMI handler tail if
  irq_nm_i re-asserts.
- Config: none
- Source: doc exception_interrupts.rst line 175 ("Nesting ... in hardware is not supported") |
  RTL-defined: rtl/ibex_controller.sv:958-960; rtl/ibex_cs_registers.sv:751-755,933,967-979
- Edge: yes, of F-IRQ-030
- Status: ACTIVE
- Notes: Candidate owner question: accepted limitation or checker expectation? Recommend the
  reference model treat mstack as single-entry and flag the scenario as "software must avoid".

### F-IRQ-037: NMI while in debug mode is ignored; dcsr.nmip reads 0
- What: handle_irq is masked by debug_mode_q, so irq_nm_i is held pending until dret. dcsr.nmip is
  hardwired 0 (never reports the pending NMI).
- Observable at: no instr_addr_o = base + 0x7C fetch while rvfi_ext_debug_mode = 1 with irq_nm_i
  high; NMI taken right after dret (instr_addr_o = base + 0x7C, rvfi_intr) with csrr read-back of
  mepc = dpc; csrr read-back of dcsr on rvfi_rd_wdata: bit 3 (nmip) = 0.
- Config: debug mode.
- Source: doc exception_interrupts.rst line 64 |
  tools/specs/riscv-debug-spec/xml/core_registers.xml:292-298 (dcsr.nmip, access R: "When set, there
  is a Non-Maskable-Interrupt (NMI) pending for the hart"; reliability "implementation-dependent") |
  RTL-defined: rtl/ibex_controller.sv:498; rtl/ibex_cs_registers.sv:825 (dcsr_d.nmip = 1'b0)
- Edge: yes, of F-IRQ-030
- Status: ACTIVE
- Notes: Bug candidate B5 (Critic C-22 re-cite: core_registers.xml:292-298, not Sdext.adoc): nmip is
  a read-only status field that never reports a pending NMI although NMIs are held pending in debug
  mode; TP-IRQ-041 expects 1 and is expected-fail pending the debug owner's ruling (owner question
  8). F-IRQ-038 (NMI pending at dret taken before the first instruction at dpc) is folded here (bin
  CG-IRQ-010.cr_line_mode_post.nmi_ext_debug_mode_taken_before_first_insn).

### F-IRQ-038: NMI pending at dret is taken before the first instruction at dpc
- What: Folded into F-IRQ-030 (through F-IRQ-037) (bin
  CG-IRQ-010.cr_line_mode_post.nmi_ext_debug_mode_taken_before_first_insn): "NMI taken after dret
  with mepc = dpc" is already the parent's outcome (F-IRQ-024 with the NMI line).
- Observable at: instr_addr_o = base + 0x7C right after the dpc fetch with rvfi_intr; csrr read-back
  of mepc (= dpc) on rvfi_rd_wdata.
- Config: debug mode exit with irq_nm_i high.
- Source: RTL-defined: rtl/ibex_controller.sv:961-965,498-500
- Edge: yes, of F-IRQ-030
- Status: FOLDED into F-IRQ-030 (bin CG-IRQ-010.cr_line_mode_post.nmi_ext_debug_mode_taken_before_first_insn)

### F-IRQ-039: All interrupts (incl. NMI) ignored in debug mode and while single stepping
- What: Alias of F-DBG-056: IRQ perspective (all interrupts incl. NMI ignored in debug mode and
  while single-stepping; dcsr.stepie forced 0), see canonical.
- Observable at: as F-DBG-056: no instr_addr_o vector fetch / rvfi_intr while rvfi_ext_debug_mode =
  1 or dcsr.step = 1; csrr read-back of dcsr bit 11 = 0 on rvfi_rd_wdata.
- Config: dcsr.step; debug mode.
- Source: doc exception_interrupts.rst line 64 | tools/specs/riscv-debug-spec/introduction.adoc line
  177 (NMIs disabled by stepie) | RTL-defined: rtl/ibex_controller.sv:498;
  rtl/ibex_cs_registers.sv:822
- Edge: no
- Status: ALIAS of F-DBG-056

### F-IRQ-040: Internal NMI from load/store data integrity (ECC) error
- What: With MemECC (SecureIbex) a bad data_rdata_i checkbit pattern sets an internal NMI pending
  flop and captures lsu_addr_last; it is taken like an NMI: mcause 0xFFFF_FFE0 (irq_int=1, code 0 =
  NMI_INT_CAUSE_ECC), mtval = faulting address, PC = base + 0x7C (irq_int forces the NMI vector),
  nmi_mode set; alert_major_bus_o asserts; a load's RF write is suppressed
  (rvfi_ext_rf_wr_suppress) when the beat that completes the access carries the error; a misaligned
  load with the error on the FIRST beat still writes rd (rtl/ibex_load_store_unit.sv:514, 697-698;
  fact-check X-11, bug candidate B16, owner TP-DMEM-041). The pending flag registers one cycle after
  the corrupted rvalid (rtl/ibex_controller.sv:402-438), so up to TWO ordinary instructions (more
  records with a Zcmp sequence) can retire between the corrupted response and the NMI entry; the
  doc's "at most one" (exception_interrupts.rst:87-88) is doc mismatch D21 (fact-check X-10; the
  first directed integrity-error sim confirms the count, inventory UNVERIFIED-4). TP-IRQ-044 /
  TP-IRQ-047 are `pass (doc mismatch D21)`.
- Observable at: alert_major_bus_o; instr_addr_o = base + 0x7C; csrr read-back of mcause
  (0xFFFF_FFE0) / mtval (faulting address) on rvfi_rd_wdata; rvfi_ext_nmi_int;
  rvfi_ext_rf_wr_suppress.
- Config: none (SecureIbex build; MemECC must be 1 in gen_dut_top).
- Source: doc exception_interrupts.rst "Internal Interrupts" table (0xFFFFFFE0); security.rst "Bus
  integrity checking" | RTL-defined: rtl/ibex_controller.sv:389-448,736-745;
  rtl/ibex_if_stage.sv:216-219; rtl/ibex_cs_registers.sv:487-489; rtl/ibex_core.sv:1353, 2384-2385;
  rtl/ibex_pkg.sv:381-384
- Edge: no
- Status: ACTIVE
- Notes: ibex_core's MemECC parameter defaults to 0 (rtl/ibex_core.sv:50); ibex_top derives it from
  SecureIbex (rtl/ibex_top.sv:41). The DUT wrapper must pass MemECC=SecureIbex or this entire
  feature is absent. Candidate owner question. ICache ECC errors raise alert_minor_o only
  (security.rst "ICache ECC") and register-file ECC lives in the lockstep shadow (not in DUT):
  neither produces an internal NMI in this DUT.

### F-IRQ-041: Internal and external NMI pending together
- What: External NMI is reported first (cause 31, mtval 0) and the internal NMI is NOT cleared
  (clear only when entering NMI with irq_nm_ext_i low); it is taken after the external NMI handler's
  mret.
- Observable at: two consecutive instr_addr_o = base + 0x7C entries (rvfi_intr twice); csrr
  read-back of mcause on rvfi_rd_wdata 0x8000_001F then 0xFFFF_FFE0 (mtval 0 then the captured
  address); rvfi_ext_nmi then rvfi_ext_nmi_int.
- Config: none
- Source: doc exception_interrupts.rst line 73 | RTL-defined: rtl/ibex_controller.sv:407-412,
  736-743
- Edge: yes, of F-IRQ-040
- Status: ACTIVE

### F-IRQ-042: Second integrity error while an internal NMI is pending
- What: Further ECC errors are ignored while the pending flop is set; the captured address is the
  first error's address.
- Observable at: one instr_addr_o = base + 0x7C entry with rvfi_ext_nmi_int; csrr read-back of mtval
  on rvfi_rd_wdata = the first faulting address; alert_major_bus_o pulses for each corrupted
  response.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:413-418 (comment 414-415)
- Edge: yes, of F-IRQ-040
- Status: ACTIVE

### F-IRQ-043: Integrity error inside an NMI handler
- What: The internal NMI stays pending (nmi_mode masks it) and is taken right after the NMI
  handler's mret.
- Observable at: instr_addr_o = base + 0x7C re-entry right after the NMI handler's mret (rvfi_intr,
  rvfi_ext_nmi_int); csrr read-back of mcause = 0xFFFF_FFE0 on rvfi_rd_wdata; alert_major_bus_o
  pulse at the error response inside the handler.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:498,736
- Edge: yes, of F-IRQ-040
- Status: ACTIVE

### F-IRQ-044: Software write to mcause (WLRL) and the internal-interrupt encoding
- What: A csrw mcause decodes wdata[31:30]: 2'b10 sets irq_ext, 2'b11 sets irq_int, 2'b01 and 2'b00
  set neither (rtl/ibex_cs_registers.sv:731-733; fact-check X-23); bits [4:0] are the code and bits
  29:5 are dropped. Writing 0xC000_00xx reads 0xFFFF_FFE0 | code; 0x8000_00xx reads back
  0x8000_00xx; 0x4000_00xx reads {27'b0, code}; 0x0000_0020 reads 0. csrs/csrc operate on the
  legalised read value.
- Observable at: csrr read-back of mcause on rvfi_rd_wdata after each csrw.
- Config: mcause write.
- Source: spec machine.adoc "Machine Cause (mcause) Register" (WLRL exception code) | RTL- defined:
  rtl/ibex_cs_registers.sv:731-733,487-489,800
- Edge: yes, of F-IRQ-040
- Status: ACTIVE
- Notes: Doc defect D3: cs_registers.rst:213 marks the mcause fields R while the RTL implements the
  write path (rtl/ibex_cs_registers.sv:800); the checker follows the RTL (WLRL per the spec).
  TP-IRQ-048 is `Expected: pass (doc mismatch D3)`.

### F-IRQ-045: WFI: sleep and wake-up
- What: wfi is a special request: FLUSH -> WAIT_SLEEP -> SLEEP; instr_req_o is held low, IF and ID
  are flushed, core_busy_o goes off (in SLEEP). The core wakes (FIRST_FETCH) when irq_pending_i (any
  mip&mie bit), irq_nm, debug_req_i, debug_mode or dcsr.step is set. If the waking interrupt is
  globally enabled it is taken with mepc = wfi+4 (pc_if); otherwise execution resumes at wfi+4.
- Observable at: instr_req_o low during the sleep; core_busy_o = IbexMuBiOff; wake latency (irq pin
  edge to the next instr_req_o); csrr read-back of mepc on rvfi_rd_wdata = wfi pc + 4 with
  rvfi_intr, or rvfi_valid of wfi + 4 without rvfi_intr.
- Config: mie; mstatus.MIE; privilege mode.
- Source: spec machine.adoc "Wait for Interrupt" (trap on following instruction, mepc = pc+4;
  unaffected by global MIE; honor individual enables; resume at pc+4) | doc integration.rst
  core_sleep_o row; exception_interrupts.rst (mip purely combinational note) | RTL-defined:
  rtl/ibex_controller.sv:287,598-646,966-968; rtl/ibex_core.sv:496-522; rtl/ibex_cs_registers.sv
  :1042-1045
- Edge: no
- Status: ACTIVE
- Notes: Folded here: F-IRQ-049 (woken by NMI, bin CG-IRQ-009.cp_wake.nmi_ext) and F-IRQ-064
  (FIRST_FETCH wake-to-vector latency, bin CG-IRQ-004.cr_ctx_latency.first_fetch_wake_two).

### F-IRQ-046: WFI wake by a locally enabled but globally disabled interrupt (M-mode, MIE=0)
- What: Folded into F-IRQ-045: the parent's wake rule already says "if the waking interrupt is
  globally enabled it is taken ... otherwise execution resumes at wfi+4"; MIE = 0 in M-mode is that
  otherwise-arm with the same wfi+4 / no-rvfi_intr observable (Critic M-9); carried by the parent's
  wake bins. F-IRQ-052 (line still held inside a handler) and the PRV alias F-PRV-019 move to the
  parent.
- Source: spec machine.adoc "Wait for Interrupt" ("can also be executed when interrupts are disabled
  ... resume ... pc+4") | RTL-defined: rtl/ibex_controller.sv:615,490,498-500
- Edge: yes, of F-IRQ-045
- Status: FOLDED into F-IRQ-045 (bin CG-IRQ-009.cp_wake.irq_local_only, CG-IRQ-009.cr_priv_wake.m_irq_local_only)

### F-IRQ-047: WFI does not wake on an interrupt disabled in mie
- What: Folded into F-IRQ-045: a line whose mie bit is clear is outside the parent's wake condition
  (irq_pending_i = any mip & mie bit); not waking is the complement of the parent's rule with the
  parent's sleep observable (v2 edge rule, second pass; Critic M-9); carried by the parent's
  disabled-line bins.
- Source: spec machine.adoc "Wait for Interrupt" ("should honor the individual interrupt enables") |
  RTL-defined: rtl/ibex_controller.sv:615; rtl/ibex_cs_registers.sv:1044-1045
- Edge: yes, of F-IRQ-045
- Status: FOLDED into F-IRQ-045 (bin CG-IRQ-009.cp_disabled_high.yes, CG-IRQ-009.cr_disabled_wake.yes_none_long, yes_nmi_ext, yes_debug_req, yes_irq_taken)

### F-IRQ-048: WFI with the wake condition already true
- What: If an enabled interrupt (or NMI/debug_req) is already pending when wfi executes, the core
  passes through WAIT_SLEEP/SLEEP in two cycles and resumes/traps; no hang and no missed interrupt.
- Observable at: instr_req_o gap of about 2 cycles (ibus monitor); trap taken with rvfi_intr and
  csrr read-back of mepc = wfi + 4 on rvfi_rd_wdata (or rvfi_valid of wfi + 4 for a masked wake).
- Config: pending source before wfi.
- Source: RTL-defined: rtl/ibex_controller.sv:598-621
- Edge: yes, of F-IRQ-045
- Status: ACTIVE

### F-IRQ-049: WFI woken by NMI
- What: Folded into F-IRQ-045 (bin CG-IRQ-009.cp_wake.nmi_ext): the NMI is one of the parent's
  listed wake sources with the parent's outcome (trap with mepc = wfi + 4).
- Observable at: instr_addr_o = base + 0x7C after the sleep with rvfi_intr; csrr read-back of mepc
  (= wfi + 4) on rvfi_rd_wdata.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:615,630-637
- Edge: yes, of F-IRQ-045
- Status: FOLDED into F-IRQ-045 (bin CG-IRQ-009.cp_wake.nmi_ext)

### F-IRQ-050: WFI woken by debug_req (debug beats a simultaneous interrupt)
- What: debug_req_i wakes the core; in FIRST_FETCH enter_debug_mode is evaluated after handle_irq
  and overrides it, so debug entry wins: dpc = wfi+4, dcsr.cause = 3; the interrupt stays pending.
- Observable at: instr_addr_o = DmHaltAddr (no interrupt vector); csrr read-back of dpc (= wfi + 4)
  and dcsr.cause (3) on rvfi_rd_wdata in the debug program; irq_pending_o stays 1.
- Config: debug_req_i; optionally a pending enabled interrupt.
- Source: RTL-defined: rtl/ibex_controller.sv:615,623-646
- Edge: yes, of F-IRQ-045
- Status: ACTIVE

### F-IRQ-051: WFI with dcsr.step = 1 outside debug mode never sleeps (FLUSH -> DBG_TAKEN_IF)
- What: WFI with dcsr.step = 1 (single-step over wfi, outside debug mode) never sleeps: the wfi
  is a special request, DECODE goes to FLUSH, and in FLUSH the debug-entry override (enter_debug_mode_prio_q,
  rtl/ibex_controller.sv:985-987) takes precedence over the WAIT_SLEEP arm (:966-967), so the FSM goes
  FLUSH -> DBG_TAKEN_IF; core_busy_o stays On and no wake source is needed. (WFI executed inside debug
  mode does reach WAIT_SLEEP: see F-DBG-059 for the port-level busy rule.)
- Observable at: after the stepped WFI retires, the next instr_addr_o fetch is DmHaltAddr and the
  next record carries rvfi_ext_debug_mode = 1; core_busy_o never equals IbexMuBiOff in between; csrr
  read-back of dpc = WFI + 4, dcsr.cause = 4.
- Config: dcsr.step = 1; not in debug mode.
- Source: RTL-defined: rtl/ibex_controller.sv:598-604 (WAIT_SLEEP, ctrl_busy_o = 0), 606-621 (SLEEP:
  busy cleared only in the else branch), 613-616 (comment 614); rtl/ibex_core.sv core_busy_o
  composition (if_busy_o, lsu_busy_o, ctrl_busy)
- Edge: yes, of F-IRQ-045
- Status: ACTIVE
- Notes: Cross-reference (Critic M-10): the WFI-in-debug-mode case (WAIT_SLEEP reached, ctrl_busy
  dip visible at core_busy_o only under the port rule) is F-DBG-059; this entry is the step-over-WFI
  case, which never reaches WAIT_SLEEP, so for cp_wake = step_nop
  CG-IRQ-009.cp_busy_off.off_not_seen is the only legal outcome (off_seen belongs to in_debug_nop).
  The DBG-side statement of the same case is F-DBG-044.

### F-IRQ-052: WFI inside a handler while the level line is still asserted
- What: Folded into F-IRQ-045 (through F-IRQ-046) (bin CG-IRQ-009.cp_wake.masked_line_held): a wake
  by a locally enabled line that is globally masked (MIE = 0 in a handler, or nmi_mode) is the
  parent's mechanism.
- Observable at: rvfi_valid of the instruction after the wfi with no rvfi_intr; no instr_addr_o
  vector fetch; instr_req_o gap in the pass-through class.
- Config: MIE=0 / nmi_mode; source held high.
- Source: spec machine.adoc "Wait for Interrupt" (implementation may resume for any reason) |
  RTL-defined: rtl/ibex_controller.sv:615,498
- Edge: yes, of F-IRQ-045
- Status: FOLDED into F-IRQ-045 (bin CG-IRQ-009.cp_wake.masked_line_held)

### F-IRQ-053: WFI in U-mode with TW=0
- What: Folded into F-IRQ-045: a U-mode WFI with TW = 0 sleeps and wakes by the parent's rule
  (U-mode interrupts are always enabled, F-IRQ-008; MPP = U is the trap-entry rule F-PRV-002); the
  TW = 1 trap is F-EXC-011 (v2 edge rule, second pass; Critic M-9); carried by the parent's
  privilege x wake bins.
- Source: spec machine.adoc "Wait for Interrupt" (optionally available to U-mode) | RTL-defined:
  rtl/ibex_id_stage.sv:606-608; rtl/ibex_controller.sv:490,615
- Edge: yes, of F-IRQ-045
- Status: FOLDED into F-IRQ-045 (bin CG-IRQ-009.cp_priv_tw.u_tw0, CG-IRQ-009.cr_priv_wake.u_tw0_irq_taken, u_tw0_nmi_ext, u_tw0_debug_req, u_tw0_none_long, u_tw0_already_pending; CG-IRQ-001.cr_line_priv_mie.software_u_mie0, timer_u_mie0)

### F-IRQ-054: WFI with an outstanding WB load/store
- What: FLUSH is entered only when WB is ready; if the outstanding access faults, the fault is taken
  instead and the wfi (younger) is discarded and re-executed after mret.
- Observable at: rvfi_trap on the load/store + csrr read-back of mcause (5/7) and mepc (= load/store
  pc) on rvfi_rd_wdata; rvfi_valid of the wfi only after the mret; without a fault, data_rvalid_i
  precedes the instr_req_o gap.
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:664-679,290
- Edge: yes, of F-IRQ-045
- Status: ACTIVE

### F-IRQ-055: Interrupt state at reset release
- What: mstatus.MIE and mie reset to 0 so regular interrupts asserted at reset are only pending
  (irq_pending_o=0 until mie is written). irq_nm_i asserted at reset release is taken in FIRST_FETCH
  before any instruction executes: mepc = boot_addr[31:8]+0x80, PC = boot_addr[31:8]+0x7C,
  mstatus.MPP=M, MPIE=0.
- Observable at: first instr_req_o addresses (instr_addr_o = {boot_addr_i[31:8],8'h7C} before any
  retirement at {boot_addr_i[31:8],8'h80}); irq_pending_o = 0 until mie is written; csrr read-back
  of mepc (= boot pc) and mstatus (MPP = 3, MPIE = 0) on rvfi_rd_wdata in the NMI handler.
- Config: none
- Source: spec machine.adoc "Reset" (MIE reset 0, priv M) | doc exception_interrupts.rst line 48 |
  RTL-defined: rtl/ibex_cs_registers.sv:987-993,1052-1056; rtl/ibex_controller.sv:582-596, 623-646
- Edge: no
- Status: ACTIVE

### F-IRQ-056: Interrupt taken while fetch_enable_i is off
- What: Alias of F-RST-015: IRQ perspective (interrupt decided while fetch_enable_i is Off: CSR/PC
  state advances, the handler is fetched only after On), see canonical.
- Observable at: as F-RST-015: no instr_req_o while Off; csrr read-back of mepc/mcause on
  rvfi_rd_wdata changed; instr_addr_o = vector as the first fetch after fetch_enable_i = On (with
  cpuctrlsts.icache_enable = 0; a cached vector line issues no request, fact-check X-21) and the
  first retirement after On is the handler's first instruction (rvfi_intr).
- Config: fetch_enable_i (MuBi); pending enabled interrupt.
- Source: doc doc/02_user/integration.rst:323-331 (fetch_enable_i row: pause fetching, halt once
  in-flight instructions have finished; Critic C-04 path fix) | RTL-defined:
  rtl/ibex_controller.sv:996-999,704-721; rtl/ibex_core.sv:643-656
- Edge: yes, of F-IRQ-016
- Status: ALIAS of F-RST-015

### F-IRQ-057: RVFI reporting of interrupts
- What: rvfi_intr is set on the first retired instruction after an interrupt entry (only EXC_PC_IRQ;
  NOT for synchronous exception entries). rvfi_ext_irq_valid is a LEVEL, not a pulse: the internal
  flop is set at the decision cycle N when ID is empty with WB ready and a new interrupt / NMI /
  debug request is captured (rtl/ibex_core.sv:1965-1971), the port rises at N + 4 after the three
  RVFI stages (:1992-2002, :2134-2141, :2192-2199; RVFI_STAGES = 2, :1837) and stays high until about
  two cycles after the handler's first instruction enters ID; it is not generated when ID emptied
  before WB drained (captured_valid already set, :1949-1968) and never coincides with rvfi_valid;
  for a SLEEP wake it rises at W + 4 = IRQ_TAKEN + 2 (fact-check X-16). rvfi_ext_pre_mip/post_mip
  and rvfi_ext_nmi/nmi_int carry the line state captured when ID first emptied, which can precede
  the decision cycle while WB drains (:1949-1957).
- Observable at: rvfi_intr, rvfi_ext_irq_valid, rvfi_ext_pre_mip, rvfi_ext_post_mip, rvfi_ext_nmi,
  rvfi_ext_nmi_int.
- Config: none
- Source: RTL-defined: rtl/ibex_core.sv:1907-1977,2400-2414,1813-1837
- Edge: no
- Status: ACTIVE
- Notes: rvfi_intr is not asserted for exception handlers (rtl/ibex_core.sv:2408 checks EXC_PC_IRQ
  only); the TB must not use it to detect exception entry. The TB never locates the decision cycle
  from rvfi_ext_irq_valid (the earlier N + 1 / N + 3 offsets were wrong; rtl-arch's architecture fact-check
  2.1 corrected to N + 4, level); TP-IRQ-061 asserts rise == N + 4 and the absent case.

### F-IRQ-058: mepc for interrupts after a control-flow change
- What: Folded into F-IRQ-002: mepc = the redirect target is the parent's mepc <- pc_if evaluated
  after a control transfer, with the parent's mepc read-back observable (v2 edge rule, second pass;
  Critic M-9); carried by the parent's mepc-source bins.
- Source: spec machine.adoc "Machine Exception Program Counter (mepc) Register" | RTL-defined:
  rtl/ibex_controller.sv:732; rtl/ibex_cs_registers.sv:895-896
- Edge: yes, of F-IRQ-002
- Status: FOLDED into F-IRQ-002 (bin CG-IRQ-001.cp_mepc_src.branch_target, jump_target, mret_target, dret_target; CG-IRQ-001.cr_line_mepc.timer_branch_target, external_jump_target, fast_3_mret_target, fast_9_dret_target)

### F-IRQ-059: Interrupt immediately after a CSR write that enables it
- What: Alias of F-CSR-026: IRQ perspective (interrupt taken immediately after the CSR write that
  enables it; mepc = the following instruction), see canonical.
- Observable at: as F-CSR-026: rvfi_valid of the csr instruction then instr_addr_o = vector with
  rvfi_intr; csrr read-back of mepc on rvfi_rd_wdata.
- Config: pending line; mie/mstatus write.
- Source: spec machine.adoc mip/mie ("evaluated immediately following ... an explicit write to a
  CSR") | RTL-defined: rtl/ibex_id_stage.sv:593-597; rtl/ibex_controller.sv:498-500,704-721
- Edge: yes, of F-IRQ-007
- Status: ALIAS of F-CSR-026

### F-IRQ-060: CSR write that disables a pending interrupt in the same cycle
- What: csrc mstatus MIE or csrc mie while the line is pending: the instruction completes first
  (interrupts wait for ID to empty) and the flopped MIE/mie then prevents the trap; no interrupt is
  taken.
- Observable at: no instr_addr_o vector fetch and no rvfi_intr; irq_pending_o drops (mie case) or
  stays 1 (MIE case).
- Config: pending line; MIE=1 before the write.
- Source: RTL-defined: rtl/ibex_controller.sv:296,704-721; rtl/ibex_cs_registers.sv:1036, 1044-1045
- Edge: yes, of F-IRQ-007
- Status: ACTIVE

### F-IRQ-061: Fast interrupt 14 vectors adjacent to the NMI vector
- What: Folded into F-IRQ-012 (bin CG-IRQ-006.cp_id.fast[14]): fast 14 (base + 0x78, adjacent to the
  NMI vector base + 0x7C) is the top row of the parent's vector table.
- Observable at: instr_addr_o = base + 0x78 (not base + 0x7C); csrr read-back of mcause =
  0x8000_001E on rvfi_rd_wdata.
- Config: mie[30].
- Source: RTL-defined: rtl/ibex_controller.sv:746-751; rtl/ibex_if_stage.sv:225-228;
  rtl/ibex_pkg.sv:334-341
- Edge: yes, of F-IRQ-012
- Status: FOLDED into F-IRQ-012 (bin CG-IRQ-006.cp_id.fast[14])

### F-IRQ-062: Fast interrupt 0 vector
- What: Folded into F-IRQ-012 (bin CG-IRQ-006.cp_id.fast[0]): fast 0 (base + 0x40) is the bottom row
  of the parent's fast-interrupt vector range.
- Observable at: instr_addr_o = base + 0x40; csrr read-back of mcause = 0x8000_0010 on
  rvfi_rd_wdata.
- Config: mie[16].
- Source: RTL-defined: rtl/ibex_controller.sv:746-751
- Edge: yes, of F-IRQ-012
- Status: FOLDED into F-IRQ-012 (bin CG-IRQ-006.cp_id.fast[0])

### F-IRQ-063: Timer interrupt is the lowest priority and the mux fall-through
- What: Folded into F-IRQ-009 (bins CG-IRQ-002.cr_drain_winner.last18_timer, cp_winner.timer): the
  timer as the mux fall-through is the last row of the parent's priority table.
- Observable at: csrr read-back of mcause on rvfi_rd_wdata = 0x8000_0007 with instr_addr_o = base +
  0x1C only when irq_timer_i is the sole pending enabled line (pin monitor).
- Config: mie[7]; other mie bits clear or lines low.
- Source: RTL-defined: rtl/ibex_controller.sv:513,756-757
- Edge: yes, of F-IRQ-009
- Status: FOLDED into F-IRQ-009 (bin CG-IRQ-002.cr_drain_winner.last18_timer)

### F-IRQ-064: Interrupt during the cycle after a WFI wake-up (FIRST_FETCH path)
- What: Folded into F-IRQ-045 (bin CG-IRQ-004.cr_ctx_latency.first_fetch_wake_two): the fixed
  wake-to-vector latency is a checker bullet (gen_chk_trap_timing) on the parent's wake, not a
  distinct stimulus.
- Observable at: fixed cycle count from the wake edge on the irq pin (SLEEP, W) to pc_set at
  IRQ_TAKEN (W + 2, via FIRST_FETCH W + 1; rtl/ibex_controller.sv:606-635, 725-733); the vector
  instr_req_o (instr_addr_o = base + 4*id) is >= that cycle and constant only with the icache off and
  an idle bus (fact-check TP-IRQ-066 row; bring-up-pinned constant GEN_WFI_WAKE_TO_VECTOR).
- Config: none
- Source: RTL-defined: rtl/ibex_controller.sv:623-646
- Edge: yes, of F-IRQ-045
- Status: FOLDED into F-IRQ-045 (bin CG-IRQ-004.cr_ctx_latency.first_fetch_wake_two)

### F-IRQ-065: mstatus reset value and interrupt stack fields at reset
- What: Alias of F-RST-006: IRQ perspective (mstatus resets to 0x0000_0080: MIE = 0, MPIE = 1, MPP =
  U; mstack resets to MPIE = 1, MPP = U; priv resets to M), see canonical.
- Observable at: as F-RST-006: csrr read-back of mstatus on rvfi_rd_wdata at boot = 0x80; an mret at
  boot returns to U-mode (rvfi_mode 0) with MIE = 1.
- Config: none
- Source: spec machine.adoc "Reset" (MIE, MPRV reset 0) | doc cs_registers.rst mstatus reset value |
  RTL-defined: rtl/ibex_cs_registers.sv:1052-1056,1257,987-993
- Edge: yes, of F-IRQ-055
- Status: ALIAS of F-RST-006

### F-IRQ-066: Debug entry inside the NMI handler keeps NMI mode across dret (H-N1)
- What: nmi_mode_q is set on NMI entry (IRQ_TAKEN) and cleared only by mret. A debug_req_i (or
  dcsr.step / trigger) that enters debug mode while the NMI handler runs (nmi_mode_q = 1) and the
  following dret leave nmi_mode_q = 1 (no DBG_TAKEN_IF/ID or dret path writes it), so after the dret
  the resumed handler still masks pending mip & mie interrupts (even with MIE = 1) and a re-asserted
  irq_nm_i until the handler's mret; that mret exits NMI mode, restores mstack, and the pending
  sources are taken.
- Observable at: no instr_addr_o vector fetch and no rvfi_intr between the dret (rvfi_ext_debug_mode
  1 -> 0) and the handler's mret while irq_pending_o = 1 (or irq_nm_i high); the first rvfi_intr /
  vector fetch follows the mret; csrr read-back of dcsr.cause (3) and dpc (a handler pc) on
  rvfi_rd_wdata in the debug program.
- Config: debug_req_i timing (inside the NMI handler); mie / mstatus.MIE written by the NMI handler;
  dcsr.step optional.
- Source: doc exception_interrupts.rst lines 58, 64, 178 (all interrupts ignored while handling the
  NMI / in debug mode) | RTL-defined: rtl/ibex_controller.sv:498-500 (handle_irq masked by
  nmi_mode_q), 574 (nmi_mode_d holds by default), 736-745 (set in IRQ_TAKEN), 958-960 (cleared only
  by mret), 961-965 (dret leaves it), 640-645 and 785-814 (DBG_TAKEN_IF / DBG_TAKEN_ID entry paths
  do not write nmi_mode_d), 474-477 (debug entry itself is not masked by nmi_mode_q), 1033,1043
  (flop); dv/auto_dv/evidence/gen_hierarchy_map.md H-N1
- Edge: yes, of F-IRQ-030
- Status: ACTIVE
- Notes: NEW (Critic C-09 item 2). Differs from F-IRQ-037 (NMI arriving while already in debug mode,
  H-N2): here the NMI handler is already running when debug mode is entered. TP-IRQ-078; bins
  CG-IRQ-007.cp_in_handler.debug_session_nmi_mode_kept, CG-IRQ-010.cp_mode.debug_in_nmi_handler.

## Status summary (fix pass after Critic verdict v1)

| status | EXC | IRQ | total |
|---|---|---|---|
| ACTIVE (incl. 1 NEW: F-IRQ-066) | 49 | 46 | 95 |
| ALIAS | 12 | 8 | 20 |
| FOLDED | 8 | 12 | 20 |
| all IDs (none renumbered or deleted) | 69 | 66 | 135 |

ALIAS: F-EXC-010->F-PRV-010, 011->F-PRV-016, 012->F-DBG-032, 018->F-ISA-034, 019->F-DBG-017,
020->F-DBG-023, 033->F-PMP-087, 047->F-SEC-023, 052->F-PRV-007, 053->F-CSR-024, 054->F-SEC-022,
057->F-SEC-025; F-IRQ-004->F-CSR-032, 013->F-CSR-035, 014->F-CSR-035, 033->F-IRQ-030,
039->F-DBG-056, 056->F-RST-015, 059->F-CSR-026, 065->F-RST-006.
FOLDED (parent, bin): F-EXC-024 (023), 028 (026), 034 (030), 039 (027), 040 (038), 058 (054),
062 (001), 063 (001); F-IRQ-010 (009), 022 (F-EXC-069), 027 (023), 029 (023), 034 (009), 038 (037),
049 (045), 052 (046), 061 (012), 062 (012), 063 (009), 064 (045). Every named bin exists in
fcov_exc_irq.md.
Canonical entries of this part that other areas alias: F-EXC-005/006/008/016/025/026/027/031/032/
035/067, F-IRQ-008/009/016/023/030/032/045/046/053 (all cited by TP items of tp_exc_irq.md).
Doc defects used: D1 (F-IRQ-004), D2 (F-EXC-053), D3 (F-IRQ-044), D10 (F-EXC-003), D12 (F-EXC-009),
D21 (F-IRQ-040, fact-check X-10).
Bug candidates used: B5 (F-IRQ-037), B12 (F-EXC-056, documented behaviour), B14 (F-EXC-064,
downgraded); B6 reclassified RTL-defined (F-EXC-046); referenced with their owners elsewhere: B16
(F-IRQ-040, owner TP-DMEM-041), B18 (F-EXC-064, owner RVFI).
Fix 3 (rtl-arch fact-check T-053): X-1 (F-EXC-050), X-7 (F-IRQ-016/018), X-9 (F-EXC-069, F-IRQ-024),
X-10/X-11 (F-IRQ-040), X-14/X-15 (F-EXC-015/018/025/027/064), X-16 (F-IRQ-002/025/057), X-23
(F-IRQ-044), Section 5 RTL-defined behaviour (F-IRQ-032 mret target); no feature added or renumbered.


# 4.4 Areas PMP: Physical memory protection and Smepmp (16 regions, G=0)


Build configuration assumed: PMPEnable=1, PMPGranularity=0, PMPNumRegions=16, RV32I (non-CHERIoT),
WritebackStage=1, ICache=1, BranchPredictor=0, SecureIbex=1 (dummy instructions available).
PMPNumChan=3: PMP_I (fetch, pc_if), PMP_I2 (fetch, pc_if+2), PMP_D (data). ShadowCSR is a fixed
localparam 0 in rtl/ibex_core.sv:197, so PMP shadow-register alerts cannot occur in this DUT.

Observability note: ibex_core has no rvfi_csr_* ports (rtl/ibex_core.sv:137-176). mcause/mtval/
mepc and PMP CSR contents are observed through a following csrr whose result appears on
rvfi_rd_wdata, plus rvfi_trap for the trap itself; the trap target is the NEXT record's
rvfi_pc_rdata (rvfi_pc_wdata of a trap / mret / dret record is the next sequential fetch address,
rtl/ibex_core.sv:2084; fact-check X-1). Bus-side effects are observed on
data_req_o/data_addr_o/data_we_o/data_be_o/data_wdata_o and instr_req_o/instr_addr_o.

Status and edge conventions (Critic v1 C-07/C-12/C-13/C-14): every block carries `- Status:`
ACTIVE | ALIAS of F-<id> | FOLDED into F-<id> (bin <name>). Only ACTIVE entries count in the
completeness measure; an ALIAS is the same behaviour stated from the PMP perspective (canonical
entry named); a FOLDED entry restated its parent and is now one of the parent's bins in
fcov_pmp.md. An entry keeps `Edge: yes` only if its What names a stimulus condition or timing
coincidence the parent does not AND its Observable at or expected outcome differs. Every Edge line
names a base (Edge: no) feature; where a folded entry's bin lives under an intermediate ACTIVE
feature the Status line names that feature. Observable at names a DUT port or RVFI field: CSR
state is "csrr read-back on rvfi_rd_wdata", exceptions are "rvfi_trap + csrr read-back of
mcause/mtval", trap targets are "instr_addr_o = <vector>"; internal nets appear only as "probe
candidate P<n>" behind a boundary alternative (P1: LSU ls_fsm_cs/lsu_resp_valid_o, F-PMP-082).
Canonical entries of this part: F-PMP-087 (misaligned first-half-denied; F-EXC-033 aliases to it)
and F-PMP-095 (debug-mode DM-window bypass; F-DBG-052 aliases to it). Bug candidates B1 (dret
leaves MPRV set) and B2 (MPRV honoured in debug mode) are canonical in F-PRV-015 and F-DBG-055;
doc defect D2 (illegal mstatus.MPP -> U) is canonical in F-CSR-024; F-PMP-075/076/077 alias them.

## CSR access and WARL behaviour

### F-PMP-001: pmpcfg0-3 read/write packing
- What: pmpcfg0..3 (0x3A0..0x3A3) each hold four 8-bit entry configs; entry i lives in byte i%4 of
  pmpcfg(i/4). Reads return {L, 2'b00, A[1:0], X, W, R} per entry; writes update each entry
  independently (per-entry write enable).
- Observable at: rvfi_rd_wdata of csrr pmpcfgN; rvfi_trap=0 for legal M-mode access.
- Config: privilege mode M; MML/RLB state (affects WARL, see F-PMP-004/007/025).
- Source: spec: tools/specs/riscv-isa-manual/src/priv/machine.adoc "Physical Memory Protection CSRs"
  | doc: doc/03_reference/cs_registers.rst CSR table (0x3A0-0x3A3) | RTL: rtl/ibex_cs_registers.sv:525-532
  (read), 1423-1426 (per-entry we), 1381-1382 (read packing), rtl/ibex_pkg.sv:697
- Edge: no
- Status: ACTIVE

### F-PMP-002: pmpaddr0-15 read/write
- What: pmpaddr0..15 (0x3B0..0x3BF) are full 32-bit WARL registers at G=0; pmpaddr[31:0] encodes
  physical address bits [33:2]. Read returns the stored value unmodified (G=0 path).
- Observable at: rvfi_rd_wdata of csrr pmpaddrN.
- Config: privilege mode M; lock state of entry N and N+1 (F-PMP-008/009).
- Source: spec: machine.adoc "Physical Memory Protection CSRs" (pmpaddr encodes bits 33-2) | doc:
  cs_registers.rst CSR table (0x3B0-0x3BF) | RTL: rtl/ibex_cs_registers.sv:183 (PMPAddrWidth=32),
  1385-1387 (g_pmp_g0), 1483-1494, 1499 ({pmp_addr_rdata, 2'b00} to the PMP unit)
- Edge: no
- Status: ACTIVE

### F-PMP-003: pmpcfg reserved bits [6:5] read as zero, writes ignored
- What: Folded into F-PMP-001: the parent's read format {L, 2'b00, A, X, W, R} already states that
  bits 6:5 read 0; writing them is the parent's write with the same read-back observable (v2 edge
  rule, second pass; Critic M-9); carried by the parent's reserved-bit bins.
- Source: spec: machine.adoc "Physical Memory Protection CSRs" (all fields WARL) | RTL:
  rtl/ibex_cs_registers.sv:1381-1382, 1429-1446 (only bits 0-4 and 7 are decoded)
- Edge: yes, of F-PMP-001
- Status: FOLDED into F-PMP-001 (bin CG-PMP-001.cp_res_bits.nonzero, CG-PMP-001.cr_res_op.nonzero_csrrw, nonzero_csrrs, nonzero_csrrc)

### F-PMP-004: R/W/X WARL: with MML=0 the reserved R=0,W=1 is legalised to W=0; with MML=1 W is stored as written
- What: When mseccfg.MML=0 the reserved combination R=0/W=1 is not storable: the written W bit is
  replaced by (W & R); X and L are stored as written. When mseccfg.MML=1 the write path stores W
  verbatim, so RW=01 (Smepmp shared-region encodings) becomes programmable. Applies to
  CSRRW/CSRRS/CSRRC alike because the legalisation is applied to the combined write value
  (csr_wdata_int).
- Observable at: csrr read-back on rvfi_rd_wdata of pmpcfgN after writing an entry with RW=01
  (MML=0: reads back RW=00 with X/L unchanged; MML=1: reads back RW=01).
- Config: mseccfg.MML (0: legalised, 1: verbatim).
- Source: spec: machine.adoc "Physical Memory Protection CSRs" (R=0,W=1 reserved; RWX collective
  WARL); "Machine Security Configuration (mseccfg) Register" (RW=01 encodes a Shared-Region when
  MML set) | RTL-defined: rtl/ibex_cs_registers.sv:1442-1445, 1002-1009 (csr_wdata_int)
- Edge: yes, of F-PMP-001
- Status: ACTIVE
- Notes: The spec only says reserved; the specific legalisation (clear W, keep X) is Ibex-defined.
  A reference model (e.g. Spike) may legalise differently; see owner question Q1. The MML=1 arm
  (former F-PMP-005) is carried by bin CG-PMP-001.cr_rw01_mml.rw01_mml1_stored.

### F-PMP-005: R/W/X with MML=1: RW=01 stored as written
- What: Folded into F-PMP-001 (through F-PMP-004): the MML=1 arm of the same WARL rule (W stored
  verbatim).
- Observable at: csrr read-back on rvfi_rd_wdata of pmpcfgN (see F-PMP-004).
- Config: mseccfg.MML=1.
- Source: spec: machine.adoc "Machine Security Configuration (mseccfg) Register" | RTL:
  rtl/ibex_cs_registers.sv:1444
- Edge: yes, of F-PMP-001
- Status: FOLDED into F-PMP-001 (bin CG-PMP-001.cr_rw01_mml.rw01_mml1_stored)

### F-PMP-006: A field encodings OFF/TOR/NA4/NAPOT all selectable at G=0
- What: A=0 OFF, A=1 TOR, A=2 NA4, A=3 NAPOT are stored as written. NA4 is legal because
  PMPGranularity=0 (with G>0 it would be legalised to OFF).
- Observable at: rvfi_rd_wdata of csrr pmpcfgN; subsequent match behaviour (F-PMP-031..041).
- Config: pmpcfg.A per entry.
- Source: spec: machine.adoc "Address Matching" (A encoding; "When G >= 1, the NA4 mode is not
  selectable") | doc: doc/03_reference/pmp.rst "PMP Granularity" | RTL:
  rtl/ibex_cs_registers.sv:1430-1439
- Edge: no
- Status: ACTIVE

### F-PMP-007: Locked entry: pmpcfg write to that entry ignored, other entries in the same CSR still written
- What: If pmpcfg(i).L=1 (and RLB=0) a write to pmpcfg(i/4) leaves entry i unchanged (including
  its L bit) while the unlocked entries in the same 32-bit CSR are updated, whatever the mix of
  locked and unlocked entries in the word.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpcfgN after write.
- Config: pmpcfg.L per entry; mseccfg.RLB=0.
- Source: spec: machine.adoc "Locking and Privilege Mode" ("If PMP entry i is locked, writes to
  pmpicfg and pmpaddri are ignored") | RTL: rtl/ibex_cs_registers.sv:1423-1426, 1463
- Edge: no
- Status: ACTIVE
- Notes: Per-entry granularity of the "ignore" is RTL-defined (spec speaks of pmpicfg, the entry).
  The mixed-lock word case (former F-PMP-019) is carried by bins
  CG-PMP-001.cr_lockmix_op.some_csrrw / some_csrrs / some_csrrc.

### F-PMP-008: Locked entry: pmpaddr(i) write ignored
- What: With pmpcfg(i).L=1 and RLB=0, writes to pmpaddr(i) are ignored.
- Observable at: rvfi_rd_wdata of csrr pmpaddrN after write.
- Config: pmpcfg(i).L; mseccfg.RLB=0.
- Source: spec: machine.adoc "Locking and Privilege Mode" | RTL: rtl/ibex_cs_registers.sv:1474-1481
- Edge: no
- Status: ACTIVE

### F-PMP-009: TOR lock of the previous address: pmpcfg(i+1) locked and A=TOR blocks pmpaddr(i)
- What: If entry i+1 is locked (L=1, RLB=0) and pmpcfg(i+1).A=TOR, writes to pmpaddr(i) are
  ignored even when entry i itself is unlocked. The lock needs both conditions: a locked i+1 in
  OFF/NA4/NAPOT mode, or an unlocked TOR i+1, leaves pmpaddr(i) writable.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpaddr(i) after write.
- Config: pmpcfg(i+1).L, pmpcfg(i+1).A; mseccfg.RLB.
- Source: spec: machine.adoc "Locking and Privilege Mode" ("if PMP entry i is locked and pmpicfg.A
  is set to TOR, writes to pmpaddr(i-1) are ignored") | RTL: rtl/ibex_cs_registers.sv:1474-1477
- Edge: no
- Status: ACTIVE
- Notes: The two negative arms (former F-PMP-010/011) are bins
  CG-PMP-002.cr_tor_lock.nl_other_rlb0_written and nu_tor_rlb0_written.

### F-PMP-010: pmpaddr(i) writable when pmpcfg(i+1) is locked but not TOR
- What: Folded into F-PMP-009: the locked-but-not-TOR arm of the previous-address lock condition.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpaddr(i) (see F-PMP-009).
- Config: pmpcfg(i+1).L=1, A in {OFF,NA4,NAPOT}.
- Source: spec: machine.adoc "Locking and Privilege Mode" | RTL: rtl/ibex_cs_registers.sv:1476
- Edge: yes, of F-PMP-009
- Status: FOLDED into F-PMP-009 (bin CG-PMP-002.cr_tor_lock.nl_other_rlb0_written)

### F-PMP-011: pmpaddr(i) writable when pmpcfg(i+1) is TOR but unlocked
- What: Folded into F-PMP-009: the TOR-but-unlocked arm of the previous-address lock condition.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpaddr(i) (see F-PMP-009).
- Config: pmpcfg(i+1).L=0, A=TOR.
- Source: spec: machine.adoc "Locking and Privilege Mode" | RTL: rtl/ibex_cs_registers.sv:1476
- Edge: yes, of F-PMP-009
- Status: FOLDED into F-PMP-009 (bin CG-PMP-002.cr_tor_lock.nu_tor_rlb0_written)

### F-PMP-012: pmpaddr15 has no next-entry TOR lock check
- What: Entry 15 is the last implemented entry; pmpaddr15 writes depend only on pmpcfg15.L (and
  RLB).
- Observable at: rvfi_rd_wdata of csrr pmpaddr15.
- Config: pmpcfg15.L.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1478-1481 (g_upper)
- Edge: yes, of F-PMP-009
- Status: ACTIVE

### F-PMP-013: L bit locks an entry even when A=OFF
- What: An entry with L=1 and A=OFF is locked (cfg and addr writes ignored, RLB sticky-off
  considers it) although it matches nothing.
- Observable at: rvfi_rd_wdata of csrr pmpcfgN/pmpaddrN; mseccfg.RLB read-back.
- Config: pmpcfg.L=1, A=OFF.
- Source: spec: machine.adoc "Locking and Privilege Mode" (note: "Setting the L bit locks the PMP
  entry even when the A field is set to OFF"); mseccfg section ("including disabled entries") |
  RTL: rtl/ibex_cs_registers.sv:1463 (mode not consulted), 1510
- Edge: yes, of F-PMP-007
- Status: ACTIVE

### F-PMP-014: pmpaddr bits [31:30] (physical address bits 33:32) are stored and readable but unreachable
- What: All 32 pmpaddr bits are writable and read back, but Ibex issues only 32-bit addresses
  (pmp_req_addr = {2'b00, addr}); an NA4/NAPOT region whose unmasked base bits include bit 32 or
  33 never matches a request; for TOR see F-PMP-044.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpaddrN; rvfi_trap and data_req_o show the
  no-match verdict (not the entry's permission) for every address when the entry cannot match.
- Config: pmpaddr values with bit 30 or 31 set.
- Source: spec: machine.adoc "Physical Memory Protection CSRs" (34-bit physical address for
  RV32) | RTL-defined: rtl/ibex_cs_registers.sv:183, 1490; rtl/ibex_core.sv:1595-1597;
  rtl/ibex_pmp.sv:191-199
- Edge: yes, of F-PMP-002
- Status: ACTIVE
- Notes: The NAPOT never-matches case (former F-PMP-039) is carried by bins
  CG-PMP-007.cr_hi_mode.napot_base_hi30 / napot_base_hi31.

### F-PMP-015: Reset values of PMP CSRs
- What: After reset all pmpcfg entries are {L=0, A=OFF, X=W=R=0}, all pmpaddr are 0 and mseccfg
  is 0 (PmpCfgRst/PmpAddrRst/PmpMseccfgRst defaults). Hence at reset M-mode has full access and
  U-mode has none.
- Observable at: rvfi_rd_wdata of csrr of each PMP CSR as first instructions after reset.
- Config: none (reset state).
- Source: doc: doc/03_reference/pmp.rst "Custom Reset Values" | RTL: rtl/ibex_pkg.sv:769-786,
  791-808, 810; rtl/ibex_cs_registers.sv:26-28, 1451, 1486, 1519
- Edge: no
- Status: ACTIVE
- Notes: The DUT wrapper could override PMPRstCfg/PMPRstAddr/PMPRstMsecCfg; see owner question Q7.

### F-PMP-016: PMP and mseccfg CSRs are M-mode only
- What: pmpcfg*, pmpaddr*, mseccfg and mseccfgh have CSR address bits [9:8]=2'b11; any access from
  U-mode raises an illegal instruction exception (cause 2) and performs no write.
- Observable at: rvfi_trap=1 + csrr read-back of mcause=2 on rvfi_rd_wdata; rvfi_mode=0 for the
  trapping instruction; a later csrr read-back of the target CSR from M-mode shows no change.
- Config: privilege mode U.
- Source: spec: machine.adoc "Physical Memory Protection CSRs" ("PMP CSRs are only accessible to
  M-mode") | RTL: rtl/ibex_cs_registers.sv:403-406
- Edge: no
- Status: ACTIVE

### F-PMP-017: PMP CSRs accessible in debug mode
- What: Folded into F-PMP-016: debug mode runs at M privilege (F-PRV-005), so the parent's
  M-mode-only rule already admits program-buffer accesses; there is no debug-only gating to observe
  (v2 edge rule, second pass; Critic M-9); carried by the parent's debug-mode access bins.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:908 (priv_lvl_d = M on any exception/debug entry),
  402 (illegal_csr_dbg only for debug CSRs)
- Edge: yes, of F-PMP-016
- Status: FOLDED into F-PMP-016 (bin CG-PMP-004.cp_dbg.d1, CG-PMP-004.cr_dbg_class.d1_pmpcfg_read_only, d1_pmpcfg_write, d1_pmpaddr_read_only, d1_pmpaddr_write, d1_mseccfg_read_only, d1_mseccfg_write)

### F-PMP-018: CSRRS/CSRRC on PMP CSRs read-modify-write through the WARL rules
- What: For set/clear operations the write value is (rdata | wdata) or (rdata & ~wdata) and is
  then subject to the same lock, RW=01 and Smepmp suppression rules as a plain write.
- Observable at: rvfi_rd_wdata of the csrrs/csrrc (old value) and of a following csrr.
- Config: any PMP state.
- Source: RTL: rtl/ibex_cs_registers.sv:1002-1009, 1011, 1020-1023
- Edge: yes, of F-PMP-001
- Status: ACTIVE

### F-PMP-019: Writing pmpcfg where some entries in the word are locked gives a partial update
- What: Folded into F-PMP-007: the mixed-lock word is the parent's own statement.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpcfgN (see F-PMP-007).
- Config: mixed L bits within one pmpcfg word; RLB=0.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1423-1426
- Edge: yes, of F-PMP-007
- Status: FOLDED into F-PMP-007 (bin CG-PMP-001.cr_lockmix_op.some_csrrw)

### F-PMP-020: A pmpcfg write that sets L on entry i takes effect (lock evaluated on the pre-write state)
- What: The lock check uses the current (pre-write) L bit, so the write that sets L succeeds; a
  following write to the same entry or its pmpaddr is ignored, also when the two writes are
  back-to-back (the pipeline flush between them does not change the outcome).
- Observable at: csrr read-back on rvfi_rd_wdata of pmpcfgN and pmpaddrN after a csrw pmpcfg then
  csrw pmpaddr.
- Config: pmpcfg.L transition 0 to 1; RLB=0.
- Source: RTL: rtl/ibex_cs_registers.sv:1463 (pmp_cfg[i].lock is the registered value), 1423-1426,
  1474-1481
- Edge: yes, of F-PMP-007
- Status: ACTIVE
- Notes: The back-to-back sequence (former F-PMP-100) is carried by bins
  CG-PMP-011.cr_bb.lock_then_addr / lock_then_cfg.

## mseccfg (Smepmp)

### F-PMP-021: mseccfg read/write of MML (bit 0), MMWP (bit 1), RLB (bit 2); other bits zero
- What: mseccfg (0x747) exposes exactly MML, MMWP and RLB; bits 31:3 read 0 and writes to them
  are ignored.
- Observable at: rvfi_rd_wdata of csrr mseccfg.
- Config: mseccfg.
- Source: spec: machine.adoc "Machine Security Configuration (mseccfg) Register" | doc:
  cs_registers.rst CSR table (0x747) | RTL: rtl/ibex_cs_registers.sv:503-513, 1502-1527;
  rtl/ibex_pkg.sv:514, 719-721
- Edge: no
- Status: ACTIVE

### F-PMP-022: mseccfgh reads zero, writes ignored
- What: mseccfgh (0x757) is implemented as read-only zero (no storage).
- Observable at: rvfi_rd_wdata of csrr mseccfgh after a csrw of all-ones; rvfi_trap=0.
- Config: none.
- Source: spec: machine.adoc mseccfg section ("mseccfgh ... aliases bits 63:32 of mseccfg") | doc:
  cs_registers.rst CSR table (0x757) | RTL: rtl/ibex_cs_registers.sv:515-522; rtl/ibex_pkg.sv:515
- Edge: no
- Status: ACTIVE

### F-PMP-023: MML is sticky: once set, cannot be cleared
- What: A write with MML=0 after MML=1 leaves MML=1 (csrw and csrrc alike). Only reset clears it.
- Observable at: rvfi_rd_wdata of csrr mseccfg.
- Config: mseccfg.MML.
- Source: spec: machine.adoc mseccfg section ("MML ... sticky bit") | RTL:
  rtl/ibex_cs_registers.sv:1505
- Edge: no
- Status: ACTIVE

### F-PMP-024: MMWP is sticky: once set, cannot be cleared
- What: As F-PMP-023 for MMWP.
- Observable at: rvfi_rd_wdata of csrr mseccfg.
- Config: mseccfg.MMWP.
- Source: spec: machine.adoc mseccfg section ("MMWP ... sticky bit") | RTL:
  rtl/ibex_cs_registers.sv:1506
- Edge: no
- Status: ACTIVE

### F-PMP-025: RLB freely settable and clearable while no entry is locked
- What: When no implemented entry has L=1 (or RLB is currently 1), a mseccfg write sets RLB to the
  written value.
- Observable at: rvfi_rd_wdata of csrr mseccfg.
- Config: all pmpcfg.L=0.
- Source: spec: machine.adoc mseccfg section (RLB) | RTL: rtl/ibex_cs_registers.sv:1510, 1514
- Edge: no
- Status: ACTIVE
- Notes: (fact-check X-20) RLB 0->1 needs no L=1 entry at all while RLB=0; since M-mode execution
  under MML=1 needs an L=1 executable rule, the mseccfg transitions (1,x,0)->(1,x,1) are
  unreachable from M-mode code (TP-PMP-108; CG-PMP-003 ignore_bins; debug-ROM variant OQ-PMP-10).

### F-PMP-026: RLB sticky-off: with RLB=0 and any L=1 entry (including A=OFF entries) RLB writes are ignored
- What: any_pmp_entry_locked = |(L & ~RLB); when set the RLB write value is forced to 0.
- Observable at: rvfi_rd_wdata of csrr mseccfg after attempting to set RLB.
- Config: mseccfg.RLB=0, at least one pmpcfg.L=1 (any A).
- Source: spec: machine.adoc mseccfg section ("When mseccfg.RLB is 0 and pmpcfg.L is 1 in any rule
  or entry (including disabled entries), then mseccfg.RLB remains 0") | RTL:
  rtl/ibex_cs_registers.sv:1463, 1510, 1514
- Edge: no
- Status: ACTIVE

### F-PMP-027: Clearing RLB while locked entries exist makes it permanently 0
- What: With RLB=1 and locked entries present, a write of RLB=0 succeeds (any_pmp_entry_locked is 0
  while RLB=1); from then on F-PMP-026 applies.
- Observable at: rvfi_rd_wdata of csrr mseccfg over the sequence set-RLB, lock entry, clear RLB,
  attempt set RLB.
- Config: mseccfg.RLB transitions with pmpcfg.L=1 present.
- Source: spec: machine.adoc mseccfg section | RTL: rtl/ibex_cs_registers.sv:1463, 1510, 1514
- Edge: yes, of F-PMP-026
- Status: ACTIVE

### F-PMP-028: RLB=1 bypasses all lock effects on PMP CSR writes
- What: With RLB=1, pmp_cfg_locked is 0 for every entry: locked cfg entries can be rewritten
  (including clearing L), locked pmpaddr can be written, and the TOR previous-address lock is
  lifted.
- Observable at: rvfi_rd_wdata of csrr pmpcfgN/pmpaddrN after writes under RLB=1.
- Config: mseccfg.RLB=1; pmpcfg.L=1 entries.
- Source: spec: machine.adoc mseccfg section ("When mseccfg.RLB is 1, locked PMP rules may be
  removed or modified") | RTL: rtl/ibex_cs_registers.sv:1463, 1474-1481
- Edge: no
- Status: ACTIVE

### F-PMP-029: MML=1, RLB=0: writing an M-mode-executable locked config is ignored (per entry)
- What: With MML=1 and RLB=0, a pmpcfg write whose new value for entry i has L=1 and RWX in
  {001, 010, 011, 101} (M-mode-only executable or locked Shared-Region with execute) is dropped for
  that entry; the other entries of the same pmpcfg word are still written. Locked non-executable
  values (L=1, RWX in {000, 100, 110, 111}) are accepted, and RLB=1 lifts the suppression
  entirely (boot-time use case).
- Observable at: csrr read-back on rvfi_rd_wdata of pmpcfgN.
- Config: mseccfg.MML=1; mseccfg.RLB (0: suppress, 1: lift); write data per entry.
- Source: spec: machine.adoc mseccfg section rule 2 ("Adding a rule with executable privileges
  that either is M-mode-only or a locked Shared-Region is not possible and such pmpcfg writes are
  ignored, leaving pmpcfg unchanged"; "This restriction can be temporarily lifted by setting
  mseccfg.RLB") | RTL: rtl/ibex_cs_registers.sv:164-176 (is_mml_m_exec_cfg), 1467-1469, 1425
- Edge: no
- Status: ACTIVE
- Notes: Spec ambiguity: whether the whole pmpcfg CSR write or only the offending entry is
  ignored; Ibex drops only the offending entry. Owner question Q5. The accepted rows (former
  F-PMP-031) are bins CG-PMP-001.cr_mml_nonexec_accept.*; the RLB=1 lift (former F-PMP-032) is
  bins CG-PMP-001.cr_mml_exec_suppress.rlb1_*.

### F-PMP-030: MML=1, RLB=0: suppression also applies when the written A field is OFF
- What: is_mml_m_exec_cfg ignores the A field, so writing L=1,X=1 (with RWX in the set of
  F-PMP-029) together with A=OFF is also ignored even though an A=OFF entry is not a "rule" per
  the Smepmp definition.
- Observable at: rvfi_rd_wdata of csrr pmpcfgN.
- Config: mseccfg.MML=1, RLB=0; wdata A=OFF, L=1, X=1.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:165 (unused_cfg = mode), 168-173 | spec:
  smepmp.adoc terms ("PMP Rule ... pmpcfg[i].A != OFF")
- Edge: yes, of F-PMP-029
- Status: ACTIVE
- Notes: Stricter than the literal spec rule; flagged as candidate disagreement (conservative
  direction). Owner question Q5.

### F-PMP-031: MML=1, RLB=0: locked non-executable configs remain writable
- What: Folded into F-PMP-029: the complement rows of the parent's suppression set.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpcfgN (see F-PMP-029).
- Config: mseccfg.MML=1, RLB=0.
- Source: spec: machine.adoc mseccfg section rule 2 | RTL: rtl/ibex_cs_registers.sv:169-171
- Edge: yes, of F-PMP-029
- Status: FOLDED into F-PMP-029 (bin CG-PMP-001.cr_mml_nonexec_accept.c1000_written, CG-PMP-001.cr_mml_nonexec_accept.c1100_written, CG-PMP-001.cr_mml_nonexec_accept.c1110_written, CG-PMP-001.cr_mml_nonexec_accept.c1111_written)

### F-PMP-032: MML=1 with RLB=1 lifts the executable-rule suppression
- What: Folded into F-PMP-029: the parent's RLB configuration at its other value.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpcfgN (see F-PMP-029).
- Config: mseccfg.MML=1, RLB=1.
- Source: spec: machine.adoc mseccfg section rule 2 ("This restriction can be temporarily lifted
  by setting mseccfg.RLB") | RTL: rtl/ibex_cs_registers.sv:1468
- Edge: yes, of F-PMP-029
- Status: FOLDED into F-PMP-029 (bin CG-PMP-001.cr_mml_exec_suppress.rlb1_c1001_written, CG-PMP-001.cr_mml_exec_suppress.rlb1_c1010_written, CG-PMP-001.cr_mml_exec_suppress.rlb1_c1011_written, CG-PMP-001.cr_mml_exec_suppress.rlb1_c1101_written)

### F-PMP-033: Setting MML does not modify or revalidate existing entries
- What: Entries programmed before MML=1 (including L=1 executable ones and entries whose RW=01
  had been legalised to 00 under MML=0) keep their stored bits; only their interpretation changes.
- Observable at: rvfi_rd_wdata of csrr pmpcfgN before/after setting MML; fault behaviour per the
  MML=1 truth table.
- Config: mseccfg.MML transition 0 to 1 with populated entries.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1502-1506 (mseccfg write touches no pmpcfg);
  rtl/ibex_pmp.sv:113-125 (interpretation selected by current MML)
- Edge: yes, of F-PMP-023
- Status: ACTIVE

## Address matching

### F-PMP-034: A=OFF matches no address
- What: A disabled entry never matches, regardless of pmpaddr.
- Observable at: rvfi_trap (no fault attributable to that entry), data_req_o.
- Config: pmpcfg.A=OFF.
- Source: spec: machine.adoc "Address Matching" ("When A=0, this PMP entry is disabled and matches
  no addresses") | RTL: rtl/ibex_pmp.sv:204
- Edge: no
- Status: ACTIVE

### F-PMP-035: NA4 matches exactly the 4-byte word at pmpaddr
- What: With A=NA4 the mask is all-ones for bits [33:2]; the access word address must equal
  pmpaddr. Byte and halfword accesses inside that word match; the adjacent words do not.
- Observable at: rvfi_trap, data_req_o for accesses at pmpaddr*4 .. pmpaddr*4+3 vs +4/-1.
- Config: pmpcfg.A=NA4, pmpaddr.
- Source: spec: machine.adoc "Address Matching" (NA4) | RTL: rtl/ibex_pmp.sv:170, 178-179 (mask
  is 1 when mode != NAPOT), 191-193, 205
- Edge: no
- Status: ACTIVE

### F-PMP-036: NAPOT size encoded by trailing ones of pmpaddr
- What: With A=NAPOT, address bit b (b>2) is masked when pmpaddr bits [b-1:2] are all ones; bit 2
  is always masked. Region size is 2^(3+k) bytes for k trailing ones, base is pmpaddr with those
  bits cleared.
- Observable at: rvfi_trap/data_req_o at region base, base+size-1 (match) and base-1, base+size
  (no match).
- Config: pmpcfg.A=NAPOT, pmpaddr pattern.
- Source: spec: machine.adoc "Address Matching" (NAPOT range encoding table) | RTL:
  rtl/ibex_pmp.sv:167-185, 191-193, 206
- Edge: no
- Status: ACTIVE

### F-PMP-037: NAPOT minimum size 8 bytes (pmpaddr ends in 0)
- What: pmpaddr = yyyy...y0 gives an 8-byte region: bit 2 masked, bit 3 compared.
- Observable at: rvfi_trap/data_req_o at the two words of the region vs neighbours.
- Config: pmpcfg.A=NAPOT, pmpaddr[0]=0.
- Source: spec: machine.adoc "Address Matching" (8-byte NAPOT range) | RTL: rtl/ibex_pmp.sv:170
- Edge: yes, of F-PMP-036
- Status: ACTIVE

### F-PMP-038: NAPOT covering the whole reachable space (2^32, 2^33, 2^34 byte regions)
- What: pmpaddr = 0x1FFFFFFF (2^29-1: 29 trailing ones, 2^32 bytes from base 0), 0x3FFFFFFF (30
  ones, 2^33), 0x7FFFFFFF (31 ones, 2^34) and 0xFFFFFFFF (32 ones) all match every 32-bit
  address; only 0xFFFFFFFF / 0x7FFFFFFF mask all compared bits (33:2), the two smaller encodings
  match because request bits 33:32 are always 00.
- Observable at: when the entry permits: rvfi_trap=0 for every fetch and data_req_o asserted for
  every load/store, checked at 0x00000000 and 0xFFFFFFFC; when it denies: rvfi_trap=1 + csrr
  read-back of mcause 1/5/7, data_req_o absent for the denied word, at the same addresses.
- Config: pmpcfg.A=NAPOT, pmpaddr all-ones patterns.
- Source: spec: machine.adoc "Address Matching" (NAPOT table rows yy01...1111 = 2^XLEN through
  1111...1111 = 2^(XLEN+3)) | RTL: rtl/ibex_pmp.sv:177-179, 191-193
- Edge: yes, of F-PMP-036
- Status: ACTIVE

### F-PMP-039: NAPOT region with base above 4 GiB never matches
- What: Folded into F-PMP-002 (through F-PMP-014), whose What already states the NA4/NAPOT
  never-matches rule.
- Observable at: rvfi_trap and data_req_o follow the no-match verdict (see F-PMP-014).
- Config: pmpcfg.A=NAPOT, pmpaddr with bit 30/31 set and few trailing ones.
- Source: RTL-defined: rtl/ibex_core.sv:1595-1597 ({2'b00, addr}); rtl/ibex_pmp.sv:191-193
- Edge: yes, of F-PMP-002
- Status: FOLDED into F-PMP-002 (bin CG-PMP-007.cr_hi_mode.napot_base_hi30, CG-PMP-007.cr_hi_mode.napot_base_hi31)

### F-PMP-040: TOR matches pmpaddr(i-1) <= addr < pmpaddr(i), independent of pmpcfg(i-1)
- What: For A=TOR the start is pmpaddr(i-1) (whatever entry i-1's mode/lock is) and the end is
  pmpaddr(i) exclusive; comparisons are on word addresses (bits 33:2).
- Observable at: rvfi_trap/data_req_o for addresses inside vs outside.
- Config: pmpcfg(i).A=TOR, pmpaddr(i-1), pmpaddr(i); pmpcfg(i-1) arbitrary.
- Source: spec: machine.adoc "Address Matching" (TOR paragraph, "irrespective of the value of
  pmpcfg(i-1)") | RTL: rtl/ibex_pmp.sv:163-164, 194-199, 207-210
- Edge: no
- Status: ACTIVE
- Notes: (fact-check X-20, TP-PMP-038) a NA4/NAPOT entry i-1 is anchored at pmpaddr(i-1)
  (rtl/ibex_pmp.sv:163-164), so it covers the TOR inside_low word pmpaddr(i-1)*4 and decides it by
  priority; the TOR probe at that word observes entry i's verdict only when entry i-1 is OFF, TOR
  or gives the same verdict.

### F-PMP-041: TOR for entry 0 uses address 0 as lower bound
- What: pmpcfg0.A=TOR matches any address < pmpaddr0.
- Observable at: rvfi_trap/data_req_o for address 0 and pmpaddr0*4-4 (match) vs pmpaddr0*4 (no).
- Config: pmpcfg0.A=TOR, pmpaddr0.
- Source: spec: machine.adoc "Address Matching" ("If PMP entry 0's A field is set to TOR, zero is
  used for the lower bound") | RTL: rtl/ibex_pmp.sv:159-161
- Edge: yes, of F-PMP-040
- Status: ACTIVE

### F-PMP-042: TOR with pmpaddr(i-1) >= pmpaddr(i) is an empty region
- What: Equal or inverted bounds match nothing (start >= end); pmpaddr0 = 0 with TOR on entry 0 is
  also empty.
- Observable at: accesses to word addresses in [pmpaddr(i), pmpaddr(i-1)) take the no-match
  verdict instead of entry i's permission: U-mode rvfi_trap=1 + csrr read-back of mcause 1/5/7
  and no data_req_o for the denied word; M-mode (MMWP=0, MML=0) rvfi_trap=0 and data_req_o
  asserted.
- Config: pmpcfg(i).A=TOR with pmpaddr(i-1) >= pmpaddr(i).
- Source: spec: machine.adoc "Address Matching" (note: "If pmpaddr(i-1) >= pmpaddr(i) and
  pmpcfg(i).A=TOR, then PMP entry i matches no addresses") | RTL: rtl/ibex_pmp.sv:194-199, 208-209
- Edge: yes, of F-PMP-040
- Status: ACTIVE

### F-PMP-043: TOR boundary bytes: lower bound inclusive, upper bound exclusive
- What: An access to word pmpaddr(i-1) matches (region_match_eq); an access to word pmpaddr(i)
  does not (region_match_lt false). The byte at pmpaddr(i)*4-1 matches.
- Observable at: rvfi_trap/data_req_o at the exact boundary words.
- Config: pmpcfg(i).A=TOR.
- Source: spec: machine.adoc "Address Matching" (pmpaddr(i-1) <= y < pmpaddr(i)) | RTL:
  rtl/ibex_pmp.sv:191-199, 208-209
- Edge: yes, of F-PMP-040
- Status: ACTIVE

### F-PMP-044: TOR bounds above 4 GiB
- What: A TOR entry whose upper bound pmpaddr(i) has bit 30/31 set matches every 32-bit address
  >= the lower bound (and the whole space if the lower bound is 0); a lower bound with bit 30/31
  set makes the region empty for 32-bit addresses.
- Observable at: rvfi_trap/data_req_o across the address space (entry verdict everywhere above
  the start for the high upper bound; no-match verdict everywhere for the high lower bound).
- Config: pmpcfg(i).A=TOR, pmpaddr values with bits 31:30 set.
- Source: spec: machine.adoc "Address Matching" (note on 2^(XLEN+2) top of range) | RTL-defined:
  rtl/ibex_core.sv:1595-1597; rtl/ibex_pmp.sv:194-199
- Edge: yes, of F-PMP-040
- Status: ACTIVE

### F-PMP-045: Static priority: the lowest-numbered matching entry decides
- What: The match/permission loop stops at the first (lowest index) matching entry; higher-numbered
  matching entries are ignored for the decision, so a low-index deny beats a high-index allow and
  a low-index allow beats a high-index deny (the MMWP/no-match default is not consulted).
- Observable at: rvfi_trap/data_req_o with two overlapping entries of different permissions.
- Config: two or more entries covering the same address.
- Source: spec: machine.adoc "Priority and Matching Logic" ("The lowest-numbered PMP entry that
  matches any byte of a memory operation determines whether that operation succeeds or fails") |
  RTL: rtl/ibex_pmp.sv:142-149
- Edge: no
- Status: ACTIVE
- Notes: The two opposite-permission cases (former F-PMP-046) are bins
  CG-PMP-006.cp_conflict.low_allow_high_deny / low_deny_high_allow.

### F-PMP-046: Overlapping entries: low-numbered deny beats high-numbered allow, and vice versa
- What: Folded into F-PMP-045: the two concrete cases of the parent's priority rule.
- Observable at: rvfi_trap/data_req_o (see F-PMP-045).
- Config: overlapping entries j<k with opposite permissions.
- Source: spec: machine.adoc "Priority and Matching Logic" | RTL: rtl/ibex_pmp.sv:144-149
- Edge: yes, of F-PMP-045
- Status: FOLDED into F-PMP-045 (bin CG-PMP-006.cp_conflict.low_allow_high_deny, CG-PMP-006.cp_conflict.low_deny_high_allow)

### F-PMP-047: All 16 entries are functional including entry 15
- What: Every implemented entry can match and decide; entry 15 is the lowest priority. TOR on entry
  15 uses pmpaddr14 as its base.
- Observable at: rvfi_trap/data_req_o with only entry 15 configured.
- Config: pmpcfg15/pmpaddr15 (with pmpaddr14 for TOR).
- Source: spec: machine.adoc "Physical Memory Protection CSRs" (lowest-numbered entries implemented
  first) | RTL: rtl/ibex_pmp.sv:144-149, 157-165
- Edge: yes, of F-PMP-045
- Status: ACTIVE

### F-PMP-048: Matching is performed on the word address of each bus transaction
- What: Both channels present word-aligned addresses (data_addr_o is word aligned; pc_if bit 1 may
  be set but bits [1:0] are not compared); bits [1:0] are unused. A single word-aligned transaction
  therefore always lies wholly within one 4-byte granule, so a partial match within one transaction
  cannot occur; partial matches only arise across the two halves of a split misaligned access.
- Observable at: rvfi_trap/data_req_o for byte/halfword accesses inside a NA4 region.
- Config: any region config.
- Source: spec: machine.adoc "Priority and Matching Logic" ("The matching PMP entry must match all
  bytes of a memory operation") | RTL: rtl/ibex_pmp.sv:191-199, 229-232;
  rtl/ibex_load_store_unit.sv:719; rtl/ibex_core.sv:1595-1597
- Edge: no
- Status: ACTIVE

## Permission check, MML=0 (original PMP)

### F-PMP-049: MML=0, M-mode, matching entry with L=0: access always allowed
- What: In M-mode a matching unlocked entry is "ignored": any RWX including 000 permits the access.
- Observable at: rvfi_trap=0, data_req_o asserted.
- Config: mseccfg.MML=0; pmpcfg.L=0; priv M (or MPRV/MPP=M for data).
- Source: spec: machine.adoc "Locking and Privilege Mode" ("When the L bit is clear, any M-mode
  access matching the PMP entry will succeed") | RTL: rtl/ibex_pmp.sv:104-107
- Edge: no
- Status: ACTIVE

### F-PMP-050: MML=0, M-mode, matching entry with L=1: R/W/X enforced
- What: A locked entry enforces its permission bits on M-mode: fetch needs X, load needs R, store
  needs W; L=1 with RWX=000 denies everything.
- Observable at: rvfi_trap=1 + csrr read-back of mcause 1/5/7; data_req_o absent for the denied
  word.
- Config: mseccfg.MML=0; pmpcfg.L=1; priv M.
- Source: spec: machine.adoc "Locking and Privilege Mode"; "Priority and Matching Logic" | RTL:
  rtl/ibex_pmp.sv:104-107, 216-219
- Edge: no
- Status: ACTIVE

### F-PMP-051: MML=0, U-mode: R/W/X enforced regardless of L
- What: In U-mode a matching entry's RWX bits decide; L has no effect on the check.
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7; data_req_o per word.
- Config: mseccfg.MML=0; priv U (or MPRV/MPP=U for data).
- Source: spec: machine.adoc "Locking and Privilege Mode" ("the R/W/X permissions apply only to S
  and U modes") | RTL: rtl/ibex_pmp.sv:108-109
- Edge: no
- Status: ACTIVE

### F-PMP-052: No matching entry: M-mode allowed, U-mode denied
- What: Without a match the default is allow for M-mode (when MMWP=0 and, for fetch, MML=0) and
  deny for U-mode.
- Observable at: rvfi_trap; data_req_o.
- Config: mseccfg.MMWP=0, MML=0; regions not covering the address.
- Source: spec: machine.adoc "Priority and Matching Logic" ("If no PMP entry matches an M-mode
  memory operation, the operation succeeds. If no PMP entry matches an S-mode or U-mode memory
  operation, the operation fails if at least one PMP entry is implemented") | RTL:
  rtl/ibex_pmp.sv:138-139
- Edge: no
- Status: ACTIVE

### F-PMP-053: U-mode with all entries OFF: every fetch and data access faults
- What: Folded into F-PMP-052: with every entry OFF nothing matches, so every U-mode fetch and data
  access takes the parent's U-mode no-match deny with the parent's fault observable (v2 edge rule,
  second pass; Critic M-9); carried by the all-OFF and U-mode fault bins.
- Source: spec: machine.adoc "Priority and Matching Logic" (note: "If at least one PMP entry is
  implemented, but all PMP entries' A fields are set to OFF, then all S-mode and U-mode memory
  accesses will fail") | RTL: rtl/ibex_pmp.sv:138, 204
- Edge: yes, of F-PMP-052
- Status: FOLDED into F-PMP-052 (bin CG-PMP-014.cp_all_off_u.yes; CG-PMP-009.cr_priv_cause.u_c1_c16, u_c1_i32)

### F-PMP-054: MMWP=1: M-mode access with no matching entry is denied
- What: With MMWP set, unmatched M-mode fetches, loads and stores fault (instruction/load/store
  access fault). Matching entries still decide by their own permissions (a matching L=0 entry
  under MML=0 still allows).
- Observable at: rvfi_trap/mcause; data_req_o; instr side fault on next unmatched fetch.
- Config: mseccfg.MMWP=1.
- Source: spec: machine.adoc mseccfg section (MMWP "changes the default PMP policy for M-mode ...
  to denied instead of ignored") | RTL: rtl/ibex_pmp.sv:138, 144-149
- Edge: no
- Status: ACTIVE

### F-PMP-055: Setting MMWP while executing from an unmatched region faults the next fetch
- What: The csrw that sets MMWP completes; the following instruction (already prefetched) is
  checked at IF/ID with the new state and takes an instruction access fault if its address has no
  matching entry. Software must cover its own code with an M-mode rule first.
- Observable at: rvfi_trap=1 on the instruction after the csrw mseccfg; mcause=1, mtval per
  F-PMP-078/068.
- Config: mseccfg.MMWP 0 to 1 with code outside any region.
- Source: RTL-defined: rtl/ibex_core.sv:1595 (pc_if checked), rtl/ibex_if_stage.sv:426-427,
  606-607; rtl/ibex_id_stage.sv:595-597 (csr_pipe_flush)
- Edge: yes, of F-PMP-054
- Status: ACTIVE

## Permission check, MML=1 (Smepmp)

### F-PMP-056: MML=1 full truth table (16 L/R/W/X rows x {M, U})
- What: The permission result for every LRWX encoding in M and U mode follows the Smepmp truth
  table; see section "Smepmp truth table vs RTL" below for the row-by-row RTL mapping. No
  disagreement was found. The row groups formerly listed as separate entries (F-PMP-057 S/U-only
  rules deny M; F-PMP-058 M-only rules deny U; F-PMP-059 shared data L=0 RW=01; F-PMP-060 shared
  code L=1 RW=01; F-PMP-061 LRWX=1111 shared read-only; F-PMP-062 inaccessible rows 0000/1000;
  F-PMP-064 M-mode fetch from an S/U-only rule) are rows of this table and are carried by its
  bins.
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7 for fetch, load and store in M and U
  for each of the 16 rows; data_req_o per word for the data rows.
- Config: mseccfg.MML=1; pmpcfg L/R/W/X per entry; privilege mode; MPRV/MPP for data.
- Source: spec: tools/specs/riscv-isa-manual/src/priv/smepmp.adoc "Smepmp Physical Memory
  Protection Rules" (truth table); machine.adoc mseccfg section rules 1-3 | RTL:
  rtl/ibex_pmp.sv:59-97, 113-125, 138-139
- Edge: no
- Status: ACTIVE
- Notes: Bins: CG-PMP-005.cr_truth_mml1 (96 required bins, Appendix A of fcov_pmp.md gives the
  expected verdict per bin).

### F-PMP-057: MML=1 L=0 rules are S/U-only: M-mode access to them is denied
- What: Folded into F-PMP-056: the L=0, RW!=01 rows of the Smepmp table in M-mode.
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7 (see F-PMP-056).
- Config: mseccfg.MML=1; pmpcfg.L=0, RW != 01; priv M.
- Source: spec: machine.adoc mseccfg section (S/U-mode-only rule) | RTL: rtl/ibex_pmp.sv:92-93
- Edge: yes, of F-PMP-056
- Status: FOLDED into F-PMP-056 (bin CG-PMP-005.cr_truth_mml1.c0001_m_fetch, CG-PMP-005.cr_truth_mml1.c0001_m_load, CG-PMP-005.cr_truth_mml1.c0001_m_store, CG-PMP-005.cr_truth_mml1.c0100_m_fetch, CG-PMP-005.cr_truth_mml1.c0100_m_load, CG-PMP-005.cr_truth_mml1.c0100_m_store, CG-PMP-005.cr_truth_mml1.c0101_m_fetch, CG-PMP-005.cr_truth_mml1.c0101_m_load, CG-PMP-005.cr_truth_mml1.c0101_m_store, CG-PMP-005.cr_truth_mml1.c0110_m_fetch, CG-PMP-005.cr_truth_mml1.c0110_m_load, CG-PMP-005.cr_truth_mml1.c0110_m_store, CG-PMP-005.cr_truth_mml1.c0111_m_fetch, CG-PMP-005.cr_truth_mml1.c0111_m_load, CG-PMP-005.cr_truth_mml1.c0111_m_store)

### F-PMP-058: MML=1 L=1 rules are M-only: U-mode access to them is denied
- What: Folded into F-PMP-056: the L=1, RW!=01, RWX!=111 rows of the Smepmp table in U-mode.
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7 (see F-PMP-056).
- Config: mseccfg.MML=1; pmpcfg.L=1, RW != 01, RWX != 111; priv U.
- Source: spec: machine.adoc mseccfg section (M-mode-only rule) | RTL: rtl/ibex_pmp.sv:92-93
- Edge: yes, of F-PMP-056
- Status: FOLDED into F-PMP-056 (bin CG-PMP-005.cr_truth_mml1.c1001_u_fetch, CG-PMP-005.cr_truth_mml1.c1001_u_load, CG-PMP-005.cr_truth_mml1.c1001_u_store, CG-PMP-005.cr_truth_mml1.c1100_u_fetch, CG-PMP-005.cr_truth_mml1.c1100_u_load, CG-PMP-005.cr_truth_mml1.c1100_u_store, CG-PMP-005.cr_truth_mml1.c1101_u_fetch, CG-PMP-005.cr_truth_mml1.c1101_u_load, CG-PMP-005.cr_truth_mml1.c1101_u_store, CG-PMP-005.cr_truth_mml1.c1110_u_fetch, CG-PMP-005.cr_truth_mml1.c1110_u_load, CG-PMP-005.cr_truth_mml1.c1110_u_store)

### F-PMP-059: MML=1 shared data region L=0, RW=01
- What: Folded into F-PMP-056: rows LRWX=0010/0011 of the Smepmp table. Both rows grant READ (and
  WRITE per the table) and deny fetch in both modes: a U-mode fetch from an LRWX=0011 window traps
  (rtl/ibex_pmp.sv:66-75; fact-check X-20, TP-PMP-062).
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7 (see F-PMP-056).
- Config: mseccfg.MML=1; pmpcfg L=0 R=0 W=1, X in {0,1}.
- Source: spec: smepmp.adoc truth table rows LRWX=0010/0011; machine.adoc mseccfg section (Shared-Region, L not set) | RTL: rtl/ibex_pmp.sv:66-75
- Edge: yes, of F-PMP-056
- Status: FOLDED into F-PMP-056 (bin CG-PMP-005.cr_truth_mml1.c0010_m_fetch, CG-PMP-005.cr_truth_mml1.c0010_m_load, CG-PMP-005.cr_truth_mml1.c0010_m_store, CG-PMP-005.cr_truth_mml1.c0010_u_fetch, CG-PMP-005.cr_truth_mml1.c0010_u_load, CG-PMP-005.cr_truth_mml1.c0010_u_store, CG-PMP-005.cr_truth_mml1.c0011_m_fetch, CG-PMP-005.cr_truth_mml1.c0011_m_load, CG-PMP-005.cr_truth_mml1.c0011_m_store, CG-PMP-005.cr_truth_mml1.c0011_u_fetch, CG-PMP-005.cr_truth_mml1.c0011_u_load, CG-PMP-005.cr_truth_mml1.c0011_u_store)

### F-PMP-060: MML=1 shared code region L=1, RW=01
- What: Folded into F-PMP-056: rows LRWX=1010/1011 of the Smepmp table.
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7 (see F-PMP-056).
- Config: mseccfg.MML=1; pmpcfg L=1 R=0 W=1, X in {0,1}.
- Source: spec: smepmp.adoc truth table rows LRWX=1010/1011; machine.adoc mseccfg section (Shared-Region, L set) | RTL: rtl/ibex_pmp.sv:76-81
- Edge: yes, of F-PMP-056
- Status: FOLDED into F-PMP-056 (bin CG-PMP-005.cr_truth_mml1.c1010_m_fetch, CG-PMP-005.cr_truth_mml1.c1010_m_load, CG-PMP-005.cr_truth_mml1.c1010_m_store, CG-PMP-005.cr_truth_mml1.c1010_u_fetch, CG-PMP-005.cr_truth_mml1.c1010_u_load, CG-PMP-005.cr_truth_mml1.c1010_u_store, CG-PMP-005.cr_truth_mml1.c1011_m_fetch, CG-PMP-005.cr_truth_mml1.c1011_m_load, CG-PMP-005.cr_truth_mml1.c1011_m_store, CG-PMP-005.cr_truth_mml1.c1011_u_fetch, CG-PMP-005.cr_truth_mml1.c1011_u_load, CG-PMP-005.cr_truth_mml1.c1011_u_store)

### F-PMP-061: MML=1 LRWX=1111 is a shared read-only region
- What: Folded into F-PMP-056: row LRWX=1111 of the Smepmp table.
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7 (see F-PMP-056).
- Config: mseccfg.MML=1; pmpcfg L=1 R=1 W=1 X=1.
- Source: spec: smepmp.adoc truth table row 1111; machine.adoc mseccfg section (LRWX=1111) | RTL: rtl/ibex_pmp.sv:85-88
- Edge: yes, of F-PMP-056
- Status: FOLDED into F-PMP-056 (bin CG-PMP-005.cr_truth_mml1.c1111_m_fetch, CG-PMP-005.cr_truth_mml1.c1111_m_load, CG-PMP-005.cr_truth_mml1.c1111_m_store, CG-PMP-005.cr_truth_mml1.c1111_u_fetch, CG-PMP-005.cr_truth_mml1.c1111_u_load, CG-PMP-005.cr_truth_mml1.c1111_u_store)

### F-PMP-062: MML=1 LRWX=0000 and 1000 are inaccessible in both modes
- What: Folded into F-PMP-056: rows LRWX=0000/1000 of the Smepmp table (Critic v1 C-12 pattern a).
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7 (see F-PMP-056).
- Config: mseccfg.MML=1; pmpcfg RWX=000 with L=0 or L=1.
- Source: spec: smepmp.adoc truth table rows 0000/1000 | RTL: rtl/ibex_pmp.sv:92-93, 216-219
- Edge: yes, of F-PMP-056
- Status: FOLDED into F-PMP-056 (bin CG-PMP-005.cr_truth_mml1.c0000_m_fetch, CG-PMP-005.cr_truth_mml1.c0000_m_load, CG-PMP-005.cr_truth_mml1.c0000_m_store, CG-PMP-005.cr_truth_mml1.c0000_u_fetch, CG-PMP-005.cr_truth_mml1.c0000_u_load, CG-PMP-005.cr_truth_mml1.c0000_u_store, CG-PMP-005.cr_truth_mml1.c1000_m_fetch, CG-PMP-005.cr_truth_mml1.c1000_m_load, CG-PMP-005.cr_truth_mml1.c1000_m_store, CG-PMP-005.cr_truth_mml1.c1000_u_fetch, CG-PMP-005.cr_truth_mml1.c1000_u_load, CG-PMP-005.cr_truth_mml1.c1000_u_store)

### F-PMP-063: MML=1: M-mode fetch with no matching entry is denied even when MMWP=0
- What: With MML=1, M-mode execution is only possible from a matching M-only or locked shared
  executable rule; an unmatched M-mode fetch raises an instruction access fault. M-mode data
  accesses without a match remain allowed unless MMWP=1.
- Observable at: rvfi_trap=1 + csrr read-back of mcause=1 on an M-mode fetch outside all regions;
  loads/stores outside all regions still complete (data_req_o asserted, rvfi_trap=0) when MMWP=0.
- Config: mseccfg.MML=1, MMWP=0.
- Source: spec: machine.adoc mseccfg section rule 3 ("Executing code from a region without a
  matching rule ... is denied") | RTL: rtl/ibex_pmp.sv:138-139
- Edge: yes, of F-PMP-056
- Status: ACTIVE

### F-PMP-064: MML=1: M-mode fetch from a matching S/U-only rule is denied
- What: Folded into F-PMP-056: the M-mode fetch column of the L=0, X=1, RW!=01 rows.
- Observable at: rvfi_trap + csrr read-back of mcause 1/5/7 (see F-PMP-056).
- Config: mseccfg.MML=1; pmpcfg L=0 X=1 covering the code; priv M.
- Source: spec: machine.adoc mseccfg section rule 3 ("or with a matching S/U-mode-only rule is denied") | RTL: rtl/ibex_pmp.sv:92-93
- Edge: yes, of F-PMP-056
- Status: FOLDED into F-PMP-056 (bin CG-PMP-005.cr_truth_mml1.c0001_m_fetch, CG-PMP-005.cr_truth_mml1.c0101_m_fetch, CG-PMP-005.cr_truth_mml1.c0111_m_fetch)

### F-PMP-065: Setting MML while executing from an L=0 or unmatched region faults the next fetch
- What: Analogous to F-PMP-055: the instruction after csrw mseccfg (MML=1) is checked with the new
  interpretation; code not covered by an L=1 executable rule faults immediately.
- Observable at: rvfi_trap=1 + csrr read-back of mcause=1 on the instruction following the csrw;
  rvfi_pc_wdata of the trapping instruction = mtvec target (instr_addr_o = vector).
- Config: mseccfg.MML 0 to 1.
- Source: RTL-defined: rtl/ibex_pmp.sv:113-125, 138-139; rtl/ibex_if_stage.sv:426-427, 606-607
- Edge: yes, of F-PMP-056
- Status: ACTIVE

## Channels and effective privilege

### F-PMP-066: Fetch check (PMP_I) is applied to pc_if at the IF/ID handoff, not to the bus request
- What: The PMP_I channel checks the PC of the instruction being handed from IF to ID (pc_if) with
  priv_mode_id and type EXEC. instr_req_o is never gated by PMP: prefetch buffer / icache fetches
  proceed to the bus for denied regions. The error is registered into ID with the instruction
  (instr_fetch_err) and raised when that instruction would execute.
- Observable at: instr_req_o/instr_addr_o still issued for denied addresses; rvfi_trap=1 later
  with mcause=1.
- Config: any PMP config; priv mode.
- Source: doc: doc/03_reference/pmp.rst "PMP Integration" ("The request coming from the
  instruction fetch unit are not gated by the PMP check") | RTL: rtl/ibex_core.sv:1595, 1599-1600;
  rtl/ibex_if_stage.sv:420, 426-427, 430, 606-607; rtl/ibex_prefetch_buffer.sv (no pmp input);
  rtl/ibex_icache.sv (no pmp input)
- Edge: no
- Status: ACTIVE

### F-PMP-067: Second fetch channel (PMP_I2) checks pc_if+2 for unaligned 32-bit instructions
- What: When pc_if[1]=1 and the instruction is not compressed, the upper halfword lives in the next
  word; PMP_I2 checks pc_if+2 (EXEC, priv_mode_id). Its result is ORed into the fetch error only
  under that condition; compressed unaligned instructions use PMP_I alone.
- Observable at: rvfi_trap=1 mcause=1 for a 32-bit instruction at 4n+2 whose upper half is in a
  denied region; no trap for a compressed instruction at the same pc.
- Config: region boundary placed between 4n+2 and 4n+4.
- Source: spec: machine.adoc "Priority and Matching Logic" (PMP checking on each memory operation;
  matching entry must match all bytes) | RTL: rtl/ibex_core.sv:1587, 1596, 1601-1602;
  rtl/ibex_if_stage.sv:426-427
- Edge: no
- Status: ACTIVE
- Notes: Canonical for the FE alias F-FE-016 (M-10 pass).

### F-PMP-068: Unaligned 32-bit fetch: first half allowed, second half denied gives mtval = pc+2
- What: Alias of F-EXC-005: PMP perspective, see canonical (the PMP-side mechanism, PMP_I2 on
  pc_if+2, is F-PMP-067).
- Observable at: rvfi_trap + csrr read-back of mcause/mtval (see F-EXC-005).
- Config: region boundary at 4n+4 with the lower region executable and the upper one not.
- Source: spec: machine.adoc "Machine Trap Value (mtval) Register" | RTL: rtl/ibex_if_stage.sv:434-435;
  rtl/ibex_controller.sv:860-861
- Edge: yes, of F-PMP-067
- Status: ALIAS of F-EXC-005

### F-PMP-069: Unaligned 32-bit fetch: first half denied gives mtval = pc regardless of the second half
- What: if_instr_err_plus2 is masked by ~pmp_err_if_i, so when the first halfword is denied
  mtval = pc even if the second half is also denied or has a bus error.
- Observable at: rvfi_trap=1 + csrr read-back of mtval on rvfi_rd_wdata = rvfi_pc_rdata of the
  trapping instruction.
- Config: lower region non-executable; second half denied or instr_err_i asserted.
- Source: RTL-defined: rtl/ibex_if_stage.sv:434-435; rtl/ibex_controller.sv:861
- Edge: yes, of F-PMP-067
- Status: ACTIVE
- Notes: Complements F-EXC-005 (second-half fault only, mtval = pc+2); the masking case is the
  distinct both-halves-erroneous stimulus.

### F-PMP-070: PMP_I2 address wraps at 0xFFFFFFFE
- What: pc_if_inc = pc_if + 2 is a 32-bit add; for pc_if = 0xFFFFFFFE the second-half check uses
  address 0x00000000.
- Observable at: rvfi_trap/mtval for an instruction placed at 0xFFFFFFFE with region 0 covering
  address 0 (or not).
- Config: regions at the top and bottom of the address space.
- Source: RTL-defined: rtl/ibex_core.sv:1587
- Edge: yes, of F-PMP-067
- Status: ACTIVE

### F-PMP-071: Data check (PMP_D) uses the word-aligned data address, type from data_we_o, privilege priv_mode_lsu
- What: The PMP_D channel checks data_addr_o (word aligned) with type WRITE when data_we_o=1 else
  READ, at the address phase of every bus transaction, with the LSU effective privilege.
- Observable at: data_req_o suppressed for denied accesses; rvfi_trap.
- Config: pmp regions; privilege; mstatus.MPRV/MPP.
- Source: spec: machine.adoc "Physical Memory Protection" (load/store access faults) | RTL:
  rtl/ibex_core.sv:1597, 1603-1604, 1063; rtl/ibex_load_store_unit.sv:719, 722-724
- Edge: no
- Status: ACTIVE
- Notes: (fact-check X-20) no PMP configuration permits a store while denying a load at the same
  privilege: under MML=0 W is stored as W&R (rtl/ibex_cs_registers.sv:1444-1445); under MML=1
  every row granting WRITE also grants READ (rtl/ibex_pmp.sv:66-83). A store-denied window is an
  R-only row; a load-denied window is a row without R (TP-PMP-069).

### F-PMP-072: MPRV=1 makes data accesses use MPP privilege for the PMP check; fetch is unaffected
- What: priv_mode_lsu = MPRV ? MPP : current privilege. In M-mode with MPRV=1, MPP=U loads/stores
  are checked as U-mode (e.g. denied on unmatched regions, denied on L=1 non-shared rules under
  MML) while instruction fetches keep M-mode checks; with MPP=M the effective data privilege is M
  regardless of MPRV.
- Observable at: rvfi_trap + csrr read-back of mcause 5/7 on loads/stores in M-mode with MPRV set
  and MPP=U; data_req_o absent for the denied word; no fetch faults for the same code; no
  difference to MPRV=0 when MPP=M.
- Config: mstatus.MPRV=1, mstatus.MPP in {U, M}; pmp regions.
- Source: spec: machine.adoc "Memory Privilege in mstatus Register"; "Physical Memory Protection"
  ("data accesses in M-mode when the MPRV bit in mstatus is set and the MPP field in mstatus
  contains S or U") | doc: cs_registers.rst mstatus bit 17 | RTL: rtl/ibex_cs_registers.sv:998;
  rtl/ibex_core.sv:1600, 1604
- Edge: no
- Status: ACTIVE
- Notes: PMP-side counterpart of F-PRV-013 (mechanism) - this entry owns the PMP verdict
  observable. The MPP=M case (former F-PMP-073) is bins CG-PMP-012.cr_eff.m_mprv_mppm_load_effm /
  m_mprv_mppm_store_effm.

### F-PMP-073: MPRV=1 with MPP=M changes nothing
- What: Folded into F-PMP-072: the MPP=M value of the parent's own formula (also stated in
  F-PRV-014).
- Observable at: rvfi_trap unchanged versus MPRV=0 (see F-PMP-072).
- Config: mstatus.MPRV=1, MPP=M.
- Source: spec: machine.adoc "Memory Privilege in mstatus Register" | RTL:
  rtl/ibex_cs_registers.sv:998
- Edge: yes, of F-PMP-072
- Status: FOLDED into F-PMP-072 (bin CG-PMP-012.cr_eff.m_mprv_mppm_load_effm, CG-PMP-012.cr_eff.m_mprv_mppm_store_effm)

### F-PMP-074: mret to U-mode clears MPRV; mret staying in M keeps it
- What: Alias of F-PRV-007: PMP perspective, see canonical. No U-mode data access can reveal the
  MPRV state after mret to U (MPP=U gives U checks either way), so there is no PMP-side scenario.
- Observable at: csrr read-back of mstatus on rvfi_rd_wdata after re-entering M (see F-PRV-007).
- Config: mstatus.MPRV=1 before mret, MPP in {U, M}.
- Source: spec: machine.adoc "Memory Privilege in mstatus Register" | RTL:
  rtl/ibex_cs_registers.sv:953-959
- Edge: yes, of F-PMP-072
- Status: ALIAS of F-PRV-007

### F-PMP-075: dret to U-mode does NOT clear MPRV (bug candidate B1)
- What: Alias of F-PRV-015: PMP perspective, see canonical (B1; the PMP-visible effect is a
  U-mode load/store to an M-allowed / U-denied region that retires with rvfi_trap=0 and data_req_o
  asserted). Such a region is unmatched with MMWP=0 or a matching L=0 RWX=000 entry under MML=0, or
  LRWX=1110 under MML=1; "L=1 RW under MML=0" is U-accessible (L is ignored for U, rtl/ibex_pmp.sv:
  101-110) and "MMWP=1 with no U rule" denies M too (fact-check X-20, TP-PMP-073).
- Observable at: data_req_o asserted and rvfi_trap=0 for a U-mode access to an M-only region after
  dret (see F-PRV-015).
- Config: debug mode; mstatus.MPRV=1, MPP=M; dcsr.prv=U; then dret.
- Source: spec: tools/specs/riscv-debug-spec/Sdext.adoc "Resume" ("If the new privilege mode
  is less privileged than M-mode, MPRV in mstatus is cleared") | RTL-defined:
  rtl/ibex_cs_registers.sv:949-951, 998
- Edge: yes, of F-PMP-072
- Status: ALIAS of F-PRV-015

### F-PMP-076: MPRV is honoured in debug mode although dcsr.mprven reads 0 (bug candidate B2)
- What: Alias of F-DBG-055: PMP perspective, see canonical (B2).
- Observable at: data_req_o absent and instr_addr_o = DmExceptionAddr for a debug-mode load/store
  outside the DM window that U-mode rules deny while MPRV=1/MPP=U (see F-DBG-055).
- Config: debug mode; mstatus.MPRV=1, MPP=U; regions outside the DM window.
- Source: spec: tools/specs/riscv-debug-spec/xml/core_registers.xml dcsr.mprven field (value 0:
  "mprv in mstatus is ignored in Debug Mode") | RTL-defined: rtl/ibex_cs_registers.sv:826, 998
- Edge: yes, of F-PMP-072
- Status: ALIAS of F-DBG-055

### F-PMP-077: Illegal mstatus.MPP write value legalised to U (RTL) vs doc statement "Machine Mode"
- What: Alias of F-CSR-024: PMP perspective, see canonical (doc defect D2: cs_registers.rst:138
  says M, RTL stores U; with MPRV=1 this decides whether data accesses are checked as U or M).
- Observable at: csrr read-back of mstatus on rvfi_rd_wdata after writing MPP=01 (see F-CSR-024);
  rvfi_trap of a following load with MPRV=1 follows U-mode rules.
- Config: mstatus write with MPP in {01, 10}.
- Source: doc defect D2: doc/03_reference/cs_registers.rst:138 says "interpreted as Machine Mode";
  RTL stores U: rtl/ibex_cs_registers.sv:784-787
- Edge: yes, of F-PMP-072
- Status: ALIAS of F-CSR-024

## Fault generation and reporting

### F-PMP-078: Instruction access fault (cause 1) is raised when the faulting instruction reaches ID as a valid instruction
- What: A PMP-denied fetch produces instr_fetch_err registered with the instruction; the exception
  is taken only when that instruction is the valid instruction in ID (not speculative). mepc = pc
  of the instruction, mtval = pc (or pc+2, F-EXC-005), mcause = 1, however the pc was reached
  (sequential, branch, jump, mret, trap vector, dret; for mret to U this is the first U-mode
  instruction). The instruction does not execute (instr_kill, no register/memory side effects).
- Observable at: rvfi_valid=1, rvfi_trap=1, rvfi_pc_rdata = pc; csrr read-back of
  mcause/mepc/mtval on rvfi_rd_wdata in the handler; rvfi_pc_wdata = mtvec target (instr_addr_o =
  vector).
- Config: region without X covering the code; privilege mode.
- Source: spec: machine.adoc "Physical Memory Protection" ("Attempting to fetch an instruction from
  a PMP region that does not have execute permissions raises an instruction access-fault
  exception"; "PMP violations are always trapped precisely") | doc: exception_interrupts.rst
  "Exceptions" (code 1) | RTL: rtl/ibex_if_stage.sv:606-607; rtl/ibex_id_stage.sv:1033;
  rtl/ibex_controller.sv:233, 268, 320-321, 860-861
- Edge: no
- Status: ACTIVE
- Notes: The control-flow-target case (former F-PMP-080) is bins CG-PMP-009.cr_target.*.

### F-PMP-079: Speculatively prefetched denied instructions that never reach ID do not fault
- What: Alias of F-EXC-006: PMP perspective, see canonical (the PMP-side part, denied fetches
  still issued on instr_req_o, is F-PMP-066).
- Observable at: instr_req_o/instr_addr_o show fetches into the denied region while rvfi_trap
  stays 0 (see F-EXC-006).
- Config: denied region immediately after a taken branch.
- Source: RTL-defined: rtl/ibex_controller.sv:233 (instr_fetch_err qualified by instr_valid_i);
  rtl/ibex_prefetch_buffer.sv:78, 128 (branch flush/discard)
- Edge: yes, of F-PMP-078
- Status: ALIAS of F-EXC-006

### F-PMP-080: Denied instruction at a branch/jump/mret/exception target faults with mepc = target
- What: Folded into F-PMP-078: mepc = pc of the instruction is the parent's statement for every
  way the pc is reached.
- Observable at: rvfi_trap=1 with rvfi_pc_rdata = target; csrr read-back of mepc (see F-PMP-078).
- Config: target inside a region without X for the new privilege.
- Source: spec: machine.adoc "Physical Memory Protection" | RTL: rtl/ibex_controller.sv:860-861
- Edge: yes, of F-PMP-078
- Status: FOLDED into F-PMP-078 (bin CG-PMP-009.cr_target.branch_c1, CG-PMP-009.cr_target.jump_c1, CG-PMP-009.cr_target.mret_c1, CG-PMP-009.cr_target.exc_entry_c1, CG-PMP-009.cr_target.dret_c1)

### F-PMP-081: Fetch PMP error and instruction bus error on the same instruction
- What: Both are ORed into if_instr_err; the fault is an instruction access fault either way; the
  plus2 rule of F-PMP-068/069 applies (bus err_plus2 also masked by a first-half PMP error).
- Observable at: rvfi_trap=1, mcause=1, mtval per plus2 rule.
- Config: denied region and instr_err_i asserted by the memory model.
- Source: RTL-defined: rtl/ibex_if_stage.sv:430, 434-435; rtl/ibex_fetch_fifo.sv:95-102
- Edge: yes, of F-PMP-078
- Status: ACTIVE

### F-PMP-082: Data PMP fault: bus request suppressed, load/store access fault, mtval = access address
- What: When PMP denies a load/store the external data_req_o is gated off (no transaction), the
  LSU generates an internal error response and the core raises load access fault (5) or store
  access fault (7) with mtval = the (unaligned) effective address and mepc = the instruction. The
  denied load writes no rd (lsu_rdata_valid gated by ~data_or_pmp_err). For an aligned denied
  access the LSU FSM runs IDLE (pmp_err_d) -> WAIT_GNT (pmp_err_q forces progress) -> IDLE where
  all_resp is driven by pmp_err_q, so load_err/store_err assert two cycles after the request
  without any bus handshake.
- Observable at: data_req_o stays 0 for the denied word (data_gnt_i never needed); rvfi_trap=1 +
  csrr read-back of mcause/mtval; rvfi_mem_rmask/wmask for the faulting access; rvfi_rd_addr /
  rvfi_rd_wdata show no write for a denied load. The 2-cycle internal completion is not boundary
  observable: probe candidate P1 (probe register entry needed): load_store_unit_i.ls_fsm_cs and
  lsu_resp_valid_o; the boundary alternative is the absence of any data_req_o for the access.
- Config: region without R (load) or W (store) matching the address; privilege/MPRV.
- Source: spec: machine.adoc "Physical Memory Protection" (load/store access faults); "Machine
  Trap Value (mtval) Register" (faulting address) | doc: pmp.rst "PMP Integration" ("The output of
  PMP check is used to gate the external request of the load-store unit") | RTL:
  rtl/ibex_core.sv:1063; rtl/ibex_load_store_unit.sv:433-486, 472, 533-544, 254-266, 688-694,
  697, 746-747; rtl/ibex_controller.sv:910-911, 924-925
- Edge: no
- Status: ACTIVE
- Notes: PMP/bus-side entry (no data_req_o for the denied word); the cause/CSR effect is canonical
  in F-EXC-026 (load) and F-EXC-028 (store). Former F-PMP-083 (no rd write) is bin
  CG-PMP-008.cr_rd.load_c5_none; former F-PMP-084 (2-cycle completion) is bins
  CG-PMP-008.cr_lat.aligned_denied_lat2 (probe candidate) and cr_align_nreq.aligned_denied_n0.
  Round-2 review M-10 (cluster F-EXC-026 / F-PMP-082 / F-DMEM-033): kept ACTIVE as the PMP-side
  observable (no data_req_o for the denied word, mtval = EA); F-EXC-026 owns the cause/CSR effect
  and F-DMEM-033 the bus-error path. Ruling requested from the DV Lead: keep the three-way split
  or alias this entry to F-EXC-026 (the PMP area then keeps only the bus observable as a bin).

### F-PMP-083: Denied load does not write the destination register
- What: Folded into F-PMP-082: a checker bullet of the parent with no distinct stimulus.
- Observable at: rvfi_rd_addr/rvfi_rd_wdata (no write) together with rvfi_trap=1 (see F-PMP-082).
- Config: region without R.
- Source: RTL: rtl/ibex_load_store_unit.sv:697
- Edge: yes, of F-PMP-082
- Status: FOLDED into F-PMP-082 (bin CG-PMP-008.cr_rd.load_c5_none)

### F-PMP-084: Denied access response timing: fake response two cycles after the request cycle
- What: Folded into F-PMP-082: the internal completion timing of the parent's denied access (no
  distinct stimulus; not boundary observable, probe candidate P1).
- Observable at: absence of any data_req_o for the access; probe candidate P1 (see F-PMP-082).
- Config: any denied aligned access.
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:433-486, 533-544, 688-694, 746-747
- Edge: yes, of F-PMP-082
- Status: FOLDED into F-PMP-082 (bin CG-PMP-008.cr_lat.aligned_denied_lat2, CG-PMP-008.cr_align_nreq.aligned_denied_n0)

### F-PMP-085: Exception priority: WB load/store access fault beats ID instruction access fault
- What: Alias of F-EXC-035: PMP perspective, see canonical (the PMP-specific coincidence, a
  PMP-denied load/store in WB with a PMP-denied fetch in ID, is bin CG-PMP-008.cr_priority.*).
- Observable at: rvfi_trap on the older load/store with csrr read-back of mcause 5/7; no rvfi
  retire for the younger instruction (see F-EXC-035).
- Config: denied load/store followed immediately by an instruction in a denied fetch region or an
  illegal instruction.
- Source: RTL-defined: rtl/ibex_controller.sv:314-327, 336
- Edge: yes, of F-PMP-082
- Status: ALIAS of F-EXC-035

### F-PMP-086: Misaligned data access is split into two word transactions, each PMP-checked independently
- What: Word accesses at offset 1/2/3 and halfword accesses at offset 3 are split; the first
  transaction uses the aligned base word, the second uses base+4. PMP_D is evaluated at each
  address phase. A halfword at 4n+3 splits into single bytes (data_be_o 4'b1000 then 4'b0001) and
  takes the same outcomes as a split word (F-PMP-087..089).
- Observable at: two data_req_o/data_addr_o phases (when allowed) with the per-half data_be_o;
  rvfi_mem_addr.
- Config: region boundary between the two words; word or halfword size.
- Source: spec: machine.adoc "Priority and Matching Logic" ("misaligned loads, stores ... may be
  decomposed into multiple memory operations ... PMP checking is performed on each memory operation
  independently") | doc: load_store_unit.rst "Misaligned Accesses" | RTL:
  rtl/ibex_load_store_unit.sv:403-405, 433-562; rtl/ibex_core.sv:1063
- Edge: no
- Status: ACTIVE
- Notes: The halfword-at-offset-3 case (former F-PMP-090) is bins CG-PMP-008.cr_half_align.*.

### F-PMP-087: Misaligned: first half denied, second half allowed: second transaction is still issued
- What: The first request is suppressed (pmp_err_q=1) and the FSM proceeds as if granted; in
  WAIT_RVALID_MIS the second request is driven with the incremented address and, since PMP allows
  it, appears on the bus (for a store, the upper bytes are written). The fault is then reported as
  load/store access fault with mtval = the original (unaligned) address; the second-half response
  is waited for and ignored.
- Observable at: exactly one data_req_o with data_addr_o = base+4 and partial data_be_o; store
  data visible in memory; rvfi_trap=1 + csrr read-back of mtval = original address.
- Config: region without permission covering the base word but not base+4.
- Source: spec: machine.adoc "Priority and Matching Logic" ("a portion of a misaligned store that
  passes the PMP check may become visible, even if another portion fails"); mtval section (address
  of the portion that faulted) | RTL-defined: rtl/ibex_load_store_unit.sv:489-500, 503-531
  (addr_update gated by ~pmp_err_q), 254-266, 807-808 (fcov ls_mis_pmp_err_1);
  rtl/ibex_core.sv:1063
- Edge: yes, of F-PMP-086
- Status: ACTIVE
- Notes: Canonical for the misaligned first-half-denied behaviour (F-EXC-033 aliases to it).
  Spec-permitted (no atomicity), but this is a visible side effect the scoreboard must model: the
  second half of a store whose first half is denied does reach memory. Owner question Q4 (accept
  as RTL-defined or file as security concern). gen_hierarchy_map.md H-L4 ("PMP error on the first
  half of a misaligned access ... no bus request at all") is wrong (Critic v1 C-11): WAIT_RVALID_MIS
  drives data_req_o with the incremented address (rtl/ibex_load_store_unit.sv:503-507, :510) and
  rtl/ibex_core.sv:1063 gates data_req_o only on the current word's PMP result.

### F-PMP-088: Misaligned: first half allowed, second half denied: first performed, fault with mtval = second word address
- What: PMP/bus-side effect: the first word transaction is issued and completes on the bus (store
  data written; load data returned and discarded), the second word request is suppressed
  (data_req_o never asserted for base+4); after the first rvalid the FSM moves to WAIT_GNT where
  pmp_err_q forces completion and addr_last is updated to the word-aligned second address, so the
  reported mtval is base+4 (aligned), not the effective address.
- Observable at: exactly one data_req_o, at data_addr_o = base word; rvfi_trap=1 + csrr read-back
  of mtval = base+4; rvfi_rd_addr/rvfi_rd_wdata show no write for a load.
- Config: region boundary at base+4 with the upper word denied.
- Source: spec: machine.adoc mtval section ("mtval will contain the virtual address of the portion
  of the access that caused the fault") | RTL-defined: rtl/ibex_load_store_unit.sv:503-544,
  254-266, 809-810 (fcov ls_mis_pmp_err_2)
- Edge: yes, of F-PMP-086
- Status: ACTIVE
- Notes: The cause/CSR effect is canonical in F-EXC-032; this entry owns the bus activity per word
  and the mtval address choice (addr_last update in WAIT_GNT).

### F-PMP-089: Misaligned: both halves denied: no bus transaction, mtval = original address
- What: Both requests are suppressed; the FSM runs through WAIT_GNT_MIS/WAIT_RVALID_MIS/WAIT_GNT on
  pmp_err_q alone and reports the fault with the original unaligned address.
- Observable at: data_req_o never asserted; rvfi_trap=1; mtval via csrr.
- Config: both words inside a denied region (or two different denied regions).
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:489-544, 254-266
- Edge: yes, of F-PMP-086
- Status: ACTIVE

### F-PMP-090: Misaligned halfword at offset 3 crossing a region boundary
- What: Folded into F-PMP-086: the halfword split is named in the parent's What; outcomes are
  those of F-PMP-087..089.
- Observable at: data_be_o patterns 4'b1000 then 4'b0001; rvfi_trap; csrr read-back of mtval (see
  F-PMP-086).
- Config: region boundary at 4n+4; lsu_type halfword.
- Source: RTL: rtl/ibex_load_store_unit.sv:403-405 | spec: machine.adoc "Priority and Matching
  Logic"
- Edge: yes, of F-PMP-086
- Status: FOLDED into F-PMP-086 (bin CG-PMP-008.cr_half_align.h16_mis_none_load, CG-PMP-008.cr_half_align.h16_mis_none_store, CG-PMP-008.cr_half_align.h16_mis_first_load, CG-PMP-008.cr_half_align.h16_mis_first_store, CG-PMP-008.cr_half_align.h16_mis_second_load, CG-PMP-008.cr_half_align.h16_mis_second_store, CG-PMP-008.cr_half_align.h16_mis_both_load, CG-PMP-008.cr_half_align.h16_mis_both_store)

### F-PMP-091: Misaligned: first half bus error plus second half PMP denial
- What: lsu_err_q captures the first-half bus error; the second half is not issued; addr_last is not
  updated in WAIT_GNT (addr_update = ~lsu_err_q), so mtval = original address and the cause is
  load/store access fault.
- Observable at: rvfi_trap=1; mtval via csrr = original address; single bus transaction with
  data_err_i=1.
- Config: memory model returns data_err_i for the first word; second word denied by PMP.
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:512-514, 533-544
- Edge: yes, of F-PMP-086
- Status: ACTIVE

## Reconfiguration timing, caches, dummy instructions, debug

### F-PMP-092: PMP CSR writes take effect for the next instruction (fetch and data) via pipeline flush
- What: Any write to pmpcfg*/pmpaddr*/mseccfg triggers csr_pipe_flush (only mscratch/mepc are
  exempt): IF is halted and ID flushed; the next instruction, even if already in the prefetch
  buffer or icache, is PMP-checked at the IF/ID handoff against the updated CSRs; the next
  load/store is checked at its address phase with the updated CSRs. There is no window in which
  an already-fetched instruction executes under the old configuration after the CSR write retires.
- Observable at: rvfi_trap on the instruction immediately after the csrw when the new config
  denies it; data_req_o gating of the next load/store.
- Config: PMP CSR write that changes the verdict for the following instruction/data address.
- Source: spec: machine.adoc "Physical Memory Protection and Paging" ("If page-based virtual
  memory is not implemented, memory accesses check the PMP settings synchronously") |
  RTL-defined: rtl/ibex_id_stage.sv:590-597; rtl/ibex_controller.sv:287, 664-677, 816-820;
  rtl/ibex_core.sv:1595 (check on pc_if at handoff); rtl/ibex_if_stage.sv:426-427, 606-607
- Edge: no
- Status: ACTIVE

### F-PMP-093: PMP does not gate icache fills or prefetches; cached instructions are still faulted at IF/ID
- What: With ICache=1 the cache fills lines from denied regions (side-effect-free instruction
  memory is assumed by the integration doc). A cache hit for an instruction in a region that has
  since become non-executable still faults because the check is on pc_if at handoff.
- Observable at: instr_req_o/instr_addr_o activity into denied regions; rvfi_trap=1 for
  instructions served from the cache after a PMP change.
- Config: icache enabled (cpuctrlsts.icache_enable) and PMP change between two executions of the
  same code.
- Source: doc: pmp.rst "PMP Integration" | RTL-defined: rtl/ibex_icache.sv (no pmp input);
  rtl/ibex_core.sv:1595; rtl/ibex_if_stage.sv:426-427
- Edge: yes, of F-PMP-066
- Status: ACTIVE

### F-PMP-094: Dummy instructions never take a PMP fetch fault; the real instruction's fault is deferred
- What: When a dummy instruction is inserted, instr_err_out is forced 0 for it; the real
  instruction stays in IF and its PMP error is delivered when it is handed over afterwards.
- Observable at: no rvfi retire for dummies; rvfi_trap=1 on the real instruction with unchanged
  mepc/mtval.
- Config: cpuctrlsts.dummy_instr_en=1; denied fetch region.
- Source: RTL-defined: rtl/ibex_if_stage.sv:525-530
- Edge: yes, of F-PMP-078
- Status: ACTIVE

### F-PMP-095: Debug mode: accesses inside the Debug Module address range bypass PMP on all channels
- What: When debug_mode=1 and (addr & ~DmAddrMask) == DmBaseAddr, pmp_req_err is forced 0 for PMP_I,
  PMP_I2 and PMP_D regardless of regions, MML/MMWP and privilege. Outside debug mode
  (debug_mode_allowed_access requires debug_mode_i) the same addresses obey the PMP rules like any
  other.
- Observable at: no rvfi_trap for program-buffer fetches and data accesses to the DM range while
  rvfi_ext_debug_mode=1; data_req_o asserted; with rvfi_ext_debug_mode=0 the same accesses take
  the normal verdict (rvfi_trap + csrr read-back of mcause 1/5/7, data_req_o absent when denied).
- Config: debug mode (or not); regions/MMWP configured to deny the DM range.
- Source: spec: tools/specs/riscv-debug-spec/implementations.adoc ("The PMP must not disallow
  fetches, loads, or stores in the address range associated with the Debug Module when the hart is
  in Debug Mode") | doc: pmp.rst "Debug Mode" | RTL: rtl/ibex_pmp.sv:235-240, 251;
  rtl/ibex_core.sv:52-53, 1607-1608, 1617
- Edge: no
- Status: ACTIVE
- Notes: Canonical for the DM-window bypass (F-DBG-052 aliases to it). DmBaseAddr/DmAddrMask are
  core parameters (default 0x1A110000/0xFFF); the DUT wrapper's values must be known to place
  tests. Owner question Q6. The outside-debug-mode arm (former F-PMP-096) is bins
  CG-PMP-013.cr_no_bypass.*.

### F-PMP-096: Outside debug mode the Debug Module range is checked normally
- What: Folded into F-PMP-095: the parent's debug-mode condition at its other value.
- Observable at: rvfi_trap/data_req_o for DM-range accesses with rvfi_ext_debug_mode=0 (see
  F-PMP-095).
- Config: regions denying the DM range; not in debug mode.
- Source: RTL: rtl/ibex_pmp.sv:239
- Edge: yes, of F-PMP-095
- Status: FOLDED into F-PMP-095 (bin CG-PMP-013.cr_no_bypass.nodbg_dm_fetch_deny, CG-PMP-013.cr_no_bypass.nodbg_dm_load_deny, CG-PMP-013.cr_no_bypass.nodbg_dm_store_deny)

### F-PMP-097: Debug mode: accesses outside the DM range are PMP-checked with M-mode (fetch) / MPRV rules (data)
- What: Debug entry sets priv_lvl to M, so program-buffer code fetching or accessing addresses
  outside the DM range is checked as M-mode (MMWP/MML apply); data accesses additionally follow
  MPRV (F-DBG-055, B2). Allowed accesses proceed; denied ones take the debug-mode exception path.
- Observable at: allowed: data_req_o asserted / instruction retires with rvfi_ext_debug_mode=1 and
  rvfi_trap=0; denied: data_req_o absent for the word and instr_addr_o = DmExceptionAddr (the
  trap-side effect, no mcause/mepc/mtval update, is canonical in F-PRV-005).
- Config: debug mode; MMWP=1 or MML=1 with regions not covering the target.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:908, 918-919; rtl/ibex_controller.sv:831;
  rtl/ibex_pmp.sv:239-251
- Edge: yes, of F-PMP-095
- Status: ACTIVE
- Notes: Canonical for the DBG alias F-DBG-054 (M-10 pass).

### F-PMP-098: Debug mode: 32-bit instruction at the last halfword of the DM range
- What: For pc = DmBaseAddr + DmAddrMask - 1 (unaligned, uncompressed), PMP_I is bypassed but PMP_I2
  (pc+2, outside the range) is checked; with MMWP=1 or MML=1 and no covering rule this yields an
  instruction access fault in debug mode.
- Observable at: instr_addr_o = DmExceptionAddr after the fetch; csrr read-back of mcause/mtval
  unchanged (trap-side canonical F-PRV-005); the same instruction one word lower retires with
  rvfi_trap=0.
- Config: debug mode; MMWP or MML set; 32-bit instruction at the top of the DM range.
- Source: RTL-defined: rtl/ibex_pmp.sv:239-240 (per-channel bypass); rtl/ibex_core.sv:1587, 1596;
  rtl/ibex_if_stage.sv:426-427
- Edge: yes, of F-PMP-095
- Status: ACTIVE

### F-PMP-099: PMP fault taken while in debug mode goes to DmExceptionAddr and updates no CSRs
- What: Alias of F-PRV-005: PMP perspective, see canonical (the PMP-side entries are F-PMP-097 and
  F-PMP-098).
- Observable at: instr_addr_o = DmExceptionAddr after the fault; csrr read-back of mcause/mtval
  unchanged (see F-PRV-005).
- Config: debug mode; denied access outside the DM range.
- Source: spec: Sdext.adoc "Debug Mode" ("Traps don't take place ... they do not update registers
  such as mepc, mcause, mtval") | RTL: rtl/ibex_controller.sv:831; rtl/ibex_cs_registers.sv:918-919
- Edge: yes, of F-PMP-095
- Status: ALIAS of F-PRV-005

### F-PMP-100: Back-to-back PMP CSR writes: lock in write 1 blocks write 2
- What: Folded into F-PMP-007 (through F-PMP-020): the back-to-back sequence is the parent's own
  statement.
- Observable at: csrr read-back on rvfi_rd_wdata of pmpaddr(i)/pmpcfg after the sequence (see
  F-PMP-020).
- Config: RLB=0.
- Source: RTL: rtl/ibex_cs_registers.sv:1423-1426, 1463, 1474-1481
- Edge: yes, of F-PMP-007
- Status: FOLDED into F-PMP-007 (bin CG-PMP-011.cr_bb.lock_then_addr, CG-PMP-011.cr_bb.lock_then_cfg)

## Smepmp truth table vs RTL (mseccfg.MML=1)

Legend: X=exec, R=read, W=write. RTL lines refer to rtl/ibex_pmp.sv. "basic" = region_basic_perm_check
(216-219) i.e. the RWX bit for the access type. Row source: tools/specs/riscv-isa-manual/src/priv/
smepmp.adoc "Smepmp Physical Memory Protection Rules".

| L | R | W | X | Spec: M-mode                | Spec: S/U-mode              | RTL path (ibex_pmp.sv)                          | Agree |
|---|---|---|---|-----------------------------|-----------------------------|-------------------------------------------------|-------|
| 0 | 0 | 0 | 0 | denied                      | denied                      | 84-95: basic(000)=0 in both modes                | yes   |
| 0 | 0 | 0 | 1 | denied                      | execute-only                | 92-93: M: basic & L(0)=0; U: basic & ~L = X     | yes   |
| 0 | 0 | 1 | 0 | read/write                  | read-only                   | 66-72: READ any mode, WRITE only if M           | yes   |
| 0 | 0 | 1 | 1 | read/write                  | read/write                  | 66-68, 74-75: READ or WRITE any mode            | yes   |
| 0 | 1 | 0 | 0 | denied                      | read-only                   | 92-93: M: 0; U: basic (R)                       | yes   |
| 0 | 1 | 0 | 1 | denied                      | read/execute                | 92-93: M: 0; U: basic (R,X)                     | yes   |
| 0 | 1 | 1 | 0 | denied                      | read/write                  | 92-93: M: 0; U: basic (R,W)                     | yes   |
| 0 | 1 | 1 | 1 | denied                      | read/write/execute          | 92-93: M: 0; U: basic (R,W,X)                   | yes   |
| 1 | 0 | 0 | 0 | denied (locked)             | denied                      | 92-93: basic(000)=0 in both modes               | yes   |
| 1 | 0 | 0 | 1 | execute-only (locked)       | denied                      | 92-93: M: basic & L = X; U: basic & ~L(1)=0     | yes   |
| 1 | 0 | 1 | 0 | execute-only (locked)       | execute-only                | 66-68, 77: EXEC any mode                        | yes   |
| 1 | 0 | 1 | 1 | read/execute (locked)       | execute-only                | 66-68, 79-81: EXEC any mode, READ only if M     | yes   |
| 1 | 1 | 0 | 0 | read-only (locked)          | denied                      | 92-93: M: basic (R); U: 0                       | yes   |
| 1 | 1 | 0 | 1 | read/execute (locked)       | denied                      | 92-93: M: basic (R,X); U: 0                     | yes   |
| 1 | 1 | 1 | 0 | read/write (locked)         | denied                      | 92-93: M: basic (R,W); U: 0                     | yes   |
| 1 | 1 | 1 | 1 | read-only (locked, shared)  | read-only                   | 85-88: READ any mode                            | yes   |

No-match rows (MML=1): M-mode EXEC denied (138-139); M-mode READ/WRITE allowed unless MMWP (138);
S/U denied (138). Spec: machine.adoc mseccfg rule 3 and MMWP paragraph. Agree.

Write-suppression set (MML=1, RLB=0): L=1 with RWX in {001, 010, 011, 101} =
rows 1001, 1010, 1011, 1101 = exactly the M-mode executable rows above (rtl/ibex_cs_registers.sv:
164-176). Agree; see F-PMP-029/030 for the A=OFF and per-entry nuances (F-PMP-031/032 folded into
F-PMP-029).

Truth table, MML=0 (original PMP; rtl/ibex_pmp.sv:101-110):

| L | priv | Result                                             | RTL       | Spec (machine.adoc "Locking and Privilege Mode") | Agree |
|---|------|----------------------------------------------------|-----------|--------------------------------------------------|-------|
| 0 | M    | allowed for any RWX (ignored)                      | 107       | "any M-mode access matching ... will succeed"    | yes   |
| 1 | M    | basic RWX enforced                                 | 107       | "enforced for all privilege modes"               | yes   |
| x | U    | basic RWX enforced                                 | 109       | "R/W/X permissions apply only to S and U modes"  | yes   |
| - | M    | no match: allowed unless MMWP                      | 138       | "If no PMP entry matches an M-mode ... succeeds" | yes   |
| - | U    | no match: denied                                   | 138       | "fails if at least one PMP entry is implemented" | yes   |

RW=01 rows do not exist in storage under MML=0 (legalised to W=0, rtl/ibex_cs_registers.sv:1444-
1445), so the reserved combination is never evaluated by the MML=0 checker.


# 4.5 Areas DBG, TRG, PMC: External debug (Sdext), triggers (Sdtrig), performance counters


Scope: `opentitan` build config (DbgTriggerEn=1, DbgHwBreakNum=1 default, MHPMCounterNum=10,
MHPMCounterWidth=32, SecureIbex=1 so DummyInstructions=1 and DataIndTiming=1, WritebackStage=1,
PMPEnable=1). DUT is ibex_core (no clock gate, so mcycle behaviour in sleep differs from ibex_top).
CHERIoT mode is out of scope; all CHERIoT-conditional branches in the cited RTL are inactive.

Naming used below: "debug CSRs" = dcsr (0x7B0), dpc (0x7B1), dscratch0 (0x7B2), dscratch1 (0x7B3).
"trigger CSRs" = tselect (0x7A0), tdata1 (0x7A1), tdata2 (0x7A2), tdata3 (0x7A3), mcontext (0x7A8),
mscontext (0x7AA), scontext (0x5A8). DmHaltAddr/DmExceptionAddr/DmBaseAddr/DmAddrMask are build
parameters (defaults 0x1A110800 / 0x1A110808 / 0x1A110000 / 0x00000FFF).

Spec-fence note: the field-level register text of the debug spec (dcsr, dpc, tdata1/mcontrol, tinfo)
lives in `build/core_registers.adoc` and `build/hwbp_registers.adoc`, which are outside the fenced
set; their generated sources `tools/specs/riscv-debug-spec/xml/core_registers.xml` and
`xml/hwbp_registers.xml` are inside it and are cited for field-level claims (dcsr.ebreaks
core_registers.xml:163-172, dcsr.nmip :292-298). Everything else is derived from the Sdext/Sdtrig
prose plus doc/03_reference/cs_registers.rst.

Status field (Critic verdict v1, fix brief rules 1-2): every block carries `- Status:` after `-
Edge:`. ACTIVE entries count in the completeness measure. `ALIAS of F-<id>` marks a duplicate stated
from this area's perspective whose canonical entry is elsewhere. `FOLDED into F-<id> (bin <name>)`
marks an edge entry that restates its parent (one row of the parent's enumeration, the parent's
Config variable at another value, the parent's What repeated, or a checker bullet without its own
stimulus); the named bin of the parent now carries it. An entry stays `Edge: yes` only if its What
names a stimulus condition or timing coincidence the parent does not AND its observable or expected
outcome differs. Edges point at the base feature (no depth-2 chains). Canonical entries owned by
this part (other areas alias to them): F-DBG-012/016/017/023/032/050/055/056, F-TRG-007,
F-PMC-001/004/005/007/011/020/025/053. Doc defects use the canonical D numbers (D4 tdata1 reset value,
D6 misaligned counted once, D12 debug.rst trigger CSRs "Debug Mode only", D16
performance_counters.rst parameter text, D18 cs_registers.rst DbgHwNumLen / scontext 0x7AA, D20 mhpmeventN = 1 << (N - 3); D5 is
RETIRED in favour of B15) and bug candidates the canonical B numbers (B1 dret/MPRV, B2 MPRV in debug
mode, B3 tdata3/context CSRs read 0, B5 dcsr.nmip, B7 dummies in minstret, B10 trigger cause on
ebreak entry, B11 NumBranchesTaken under DIT, B15 dcsr.ebreaks writable, B17 HPM counters 8/11/12
over-count behind an outstanding WB access; B6 is reclassified RTL-defined and B9 (dcsr.cause 0
window under out-of-spec stimulus) is record-only). Fix brief 3 (rtl-arch T-053) corrections are
marked "fact-check X-n / C-n" in the blocks below. Observables use the shorthands "csrr read-back on rvfi_rd_wdata" (CSR
state) and "instr_addr_o = <vector>" (trap targets).

---------------------------------------------------------------------------------------------------

## DBG: external debug (Sdext as implemented)

### F-DBG-001: Halt request entry via debug_req_i (cause 3)
- What: When debug_req_i is high and the core is not in debug mode, the controller waits for the
  instruction in ID/WB to finish, flushes the pipeline, and enters debug mode: PC := DmHaltAddr,
  dpc := PC of the next instruction to execute (pc_if), dcsr.cause := 3 (HALTREQ), dcsr.prv := the
  privilege mode at entry, current privilege becomes M. mepc/mcause/mtval/mstatus are not changed.
- Observable at: instr_req_o/instr_addr_o (first fetch after entry is DmHaltAddr);
  rvfi_ext_debug_req, rvfi_ext_debug_mode (subsequent retirements report debug_mode=1); csrr
  read-back of dcsr/dpc on rvfi_rd_wdata in the debug program; no rvfi_trap for the entry itself.
- Config: dcsr.step=0; privilege mode (M or U) at entry; PMP must allow fetch from DmHaltAddr.
- Source: spec tools/specs/riscv-debug-spec/Sdext.adoc "Halt" | doc doc/03_reference/debug.rst
  "Interface" | RTL-defined rtl/ibex_controller.sv:474-477 (enter_debug_mode), 519-523 (cause),
  704-711 (DECODE), 764-783 (DBG_TAKEN_IF, csr_save_if_o :773); rtl/ibex_cs_registers.sv:891-917
  (dpc/dcsr save, priv M); rtl/ibex_if_stage.sv:229 (EXC_PC_DBD = DmHaltAddr)
- Edge: no
- Status: ACTIVE
- Notes: dpc for haltreq is pc_if (the IF-stage address), which is the next instruction in program
  order after the last retired instruction (rtl/ibex_controller.sv:773 csr_save_if_o).
  Canonical entry of the haltreq family; edges F-DBG-002..010 and F-DBG-068 hang off it.

### F-DBG-002: debug_req_i and interrupt pending in the same cycle: debug entry wins
- What: In DECODE the controller checks enter_debug_mode before handle_irq; in FIRST_FETCH the debug
  branch overrides the IRQ branch. The interrupt is not taken; it remains pending and is taken after
  dret (if still asserted and enabled). No handler instruction executes before debug entry. The
  same priority applies to a trigger match coincident with a pending interrupt (enter_debug_mode
  includes trigger_match_i): former F-TRG-025, folded here.
- Observable at: instr_addr_o == DmHaltAddr (not mtvec vector); rvfi_ext_irq_valid / rvfi_intr not
  set for the debug entry; csrr read-back of mcause/mepc on rvfi_rd_wdata unchanged.
- Config: mstatus.MIE=1, mie bit set, matching irq_*_i asserted; dcsr.step=0.
- Source: spec Sdext.adoc "Debug Mode" item "All interrupts (including NMI) are masked" |
  RTL-defined rtl/ibex_controller.sv:634-646 (FIRST_FETCH), 704-722 (DECODE priority)
- Edge: yes, of F-DBG-001
- Status: ACTIVE

### F-DBG-003: debug_req_i while an LSU transaction is outstanding in WB
- What: Debug entry is deferred until the instruction in WB completes (ready_wb_i) and the ID stage
  is empty; IF is halted meanwhile. If the outstanding load/store returns an error, that exception
  is taken first (mepc/mcause/mtval written, PC := mtvec) and debug mode is then entered with dpc :=
  the trap handler address (see F-DBG-004). The instruction already in ID behind the load/store (if
  any) also completes: halt_if only stops IF (rtl/ibex_controller.sv:700-708) and the entry needs
  id_wb_pending = 0 (:296), so dpc = pc of the first not-yet-executed instruction = next pc of the
  last retired record, which is "load pc + size" only when nothing had entered ID behind the load
  (fact-check X-7, C-3).
- Observable at: data_rvalid_i timing vs. first fetch of DmHaltAddr on instr_addr_o; rvfi of the
  load/store (and of the instruction behind it, both with rvfi_ext_debug_req = 0, C-3) retires
  before rvfi_ext_debug_mode goes high; the first debug-ROM record carries rvfi_ext_debug_req = 1;
  csrr read-back of dpc on rvfi_rd_wdata == next pc of the last pre-entry record.
- Config: none (memory model must delay data_gnt_i / data_rvalid_i).
- Source: spec Sdext.adoc "Halt" | RTL-defined rtl/ibex_controller.sv:700-702 (halt_if while
  id_wb_pending), 704-707, 296 (id_wb_pending)
- Edge: yes, of F-DBG-001
- Status: ACTIVE

### F-DBG-004: debug_req_i asserted in the same window as a synchronous exception
- What: When the ID instruction raises an exception (or WB raises a load/store fault) while
  debug_req_i is high, the controller goes to FLUSH, performs the exception architecturally (mepc,
  mcause, mtval, mstatus.MIE/MPIE/MPP written, PC := mtvec target), and then goes to DBG_TAKEN_IF
  instead of DECODE: dpc := trap handler address, dcsr.cause := 3. No handler instruction executes.
- Observable at: rvfi_trap for the faulting instruction X, whose record carries rvfi_ext_debug_req
  = 0 (the flag is sampled at X's IF->ID transfer, before the rise; fact-check X-6, C-3; a request
  already high before X's transfer pre-empts X instead: halt_if, plain haltreq entry with dpc = X pc
  and no record for X); csrr read-back of mepc/mcause on rvfi_rd_wdata; instr_addr_o sequence
  (mtvec target is fetched, then DmHaltAddr; needs cpuctrlsts.icache_enable = 0, C-14); csrr
  read-back of dpc == mtvec target; the first debug-ROM record carries rvfi_ext_debug_req = 1.
- Config: mtvec; the exception type (illegal, ecall, ebreak with ebreakm=0, fetch error,
  load/store).
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" (trap-first semantics stated for step;
  applied by RTL to haltreq too) | RTL-defined rtl/ibex_controller.sv:971-987 (FLUSH ->
  DBG_TAKEN_IF via enter_debug_mode_prio_q)
- Edge: yes, of F-DBG-001
- Status: ACTIVE
- Notes: For haltreq the spec does not mandate whether the exception or the halt is first; RTL
  always completes the exception. Reference model must match this ordering. Canonical for the EXC
  alias F-EXC-048 (M-10 pass).

### F-DBG-005: debug_req_i must be level-held; a short pulse can be dropped
- What: enter_debug_mode is combinational on debug_req_i and is only acted on when the pipeline is
  idle (DECODE with !stall && !id_wb_pending, or FIRST_FETCH). A pulse that ends while an
  instruction is still in ID/WB is lost; no debug entry happens.
- Observable at: absence of the DmHaltAddr fetch within the entry bound (driver log + ibus monitor).
  The retiring instruction does NOT show the pulse: rvfi_ext_debug_req is sampled at the IF->ID
  transfer (fact-check X-6, C-3) and the instruction in ID entered before the pulse. An RVFI trace
  exists only when ID was EMPTY during the pulse (WB busy): captured_debug_req is sticky
  (rtl/ibex_core.sv:1949-1957) and the NEXT instruction entering ID reports rvfi_ext_debug_req = 1
  with rvfi_ext_debug_mode = 0; with an instruction stalled in ID or a divide in ID there is no
  trace at all.
- Config: none.
- Source: RTL-defined rtl/ibex_controller.sv:474-477, 704-722 (no latching of debug_req_i in the
  controller); rtl/ibex_core.sv:1949-1957, 1996-2001 (RVFI-side sticky capture)
- Edge: yes, of F-DBG-001
- Status: ACTIVE
- Notes: Debug spec assumes the DM holds haltreq until the hart reports halted; TB stimulus must
  hold debug_req_i until debug entry is observed, or treat dropped pulses as expected.

### F-DBG-006: debug_req_i deasserting in the FLUSH cycle records dcsr.cause = 0 (bug candidate)
- What: The FLUSH -> DBG_TAKEN_IF decision uses the registered enter_debug_mode_prio_q (previous
  cycle) but dcsr.cause is written from debug_cause_q, which is computed from debug_req_i and
  do_single_step_d in the FLUSH cycle. If debug_req_i drops exactly in the FLUSH cycle (and step=0),
  debug mode is still entered but dcsr.cause reads 0 (DBG_CAUSE_NONE, a reserved encoding).
- Observable at: csrr read-back of dcsr on rvfi_rd_wdata in the debug program shows cause field 0.
- Config: dcsr.step=0.
- Source: RTL-defined rtl/ibex_controller.sv:515-533 (comment acknowledges window), 985-987
- Edge: yes, of F-DBG-001
- Status: ACTIVE
- Notes: B9, record-only (gen_bug_log.md v1d): the window needs a debug_req_i pulse shorter than
  the DECODE -> FLUSH span, which the debug spec forbids (haltreq is held until the hart halts);
  TP-DBG-011 is the informational `_info` item, never gated. The ecall's record carries
  rvfi_ext_debug_req = 0 (C-3); the entry is identified from the driver log. Owner question Q1
  below (Q-007 default applied).

### F-DBG-007: debug_req_i held high while in debug mode is ignored; re-halts immediately after dret
- What: enter_debug_mode is gated by ~debug_mode_q, so a held debug_req_i has no effect inside debug
  mode. After dret, if debug_req_i is still high, the core re-enters debug mode before executing any
  instruction: dpc := the dret target (unchanged value), dcsr.cause := 3, dcsr.prv := dcsr.prv value
  restored by dret.
- Observable at: instr_addr_o fetches dpc target then DmHaltAddr with no retirement in between (rvfi
  shows no non-debug instruction); csrr read-back of dpc on rvfi_rd_wdata unchanged.
- Config: dcsr.prv.
- Source: spec Sdext.adoc "Resume", "Halt" | RTL-defined rtl/ibex_controller.sv:474-477, 704-707
- Edge: yes, of F-DBG-001
- Status: ACTIVE

### F-DBG-008: Alias of F-RST-024
- What: Alias of F-RST-024: DBG perspective (debug_req_i high at reset release halts before the
  first instruction, dpc = boot address, dcsr.cause = 3, dcsr.prv = M), see canonical.
- Edge: yes, of F-DBG-001
- Status: ALIAS of F-RST-024

### F-DBG-009: debug_req_i wakes the core from WFI sleep and enters debug mode
- What: In SLEEP, debug_req_i (like an interrupt) moves the controller to FIRST_FETCH; the WFI is
  considered complete and debug mode is entered with dpc := address after the WFI (WFI+4).
- Observable at: core_busy_o low for the whole sleep window (WAIT_SLEEP plus every SLEEP cycle
  before the request) then high; instr_req_o resumes; instr_addr_o == DmHaltAddr; csrr read-back of
  dpc == wfi_pc+4 on rvfi_rd_wdata.
- Config: mstatus.MIE may be 0 (debug wake does not depend on interrupt enables).
- Source: spec Sdext.adoc "Wait for Interrupt Instruction" | doc doc/02_user/integration.rst
  "core_sleep_o" row | RTL-defined rtl/ibex_controller.sv:606-621 (SLEEP exit terms), 634-646
- Edge: yes, of F-DBG-001
- Status: ACTIVE

### F-DBG-010: debug entry is deferred while a Zcmp expanded sequence is in progress
- What: enter_debug_mode (haltreq, step, and trigger) is masked while the instruction in ID is a
  Zcmp micro-op that is not the last (INSTR_EXPANDED or INSTR_EXPANDED_COMMIT). The full cm.push /
  cm.pop / cm.popret / cm.popretz / cm.mvsa01 / cm.mva01s sequence completes, then debug mode is
  entered with dpc := next instruction (or the popret target).
- Observable at: all memory accesses of the sequence appear on data_req_o before instr_addr_o ==
  DmHaltAddr; rvfi_ext_expanded_insn_* retire the whole sequence; csrr read-back of dpc on
  rvfi_rd_wdata.
- Config: none.
- Source: spec Sdtrig.adoc "Multiple State Change Instructions" (partial-execution caveat) |
  RTL-defined rtl/ibex_controller.sv:473-477
- Notes: The step instance (former F-DBG-046) is a bin of this entry.
- Edge: yes, of F-DBG-001
- Status: ACTIVE

### F-DBG-011: Debug entry PC is DmHaltAddr; exceptions inside debug mode vector to DmExceptionAddr
- What: All debug entries (haltreq, step, trigger, ebreak-into-debug, ebreak-in-debug) set PC :=
  DmHaltAddr (exc_pc_mux EXC_PC_DBD). Any synchronous exception raised while debug_mode=1 sets
  PC := DmExceptionAddr (EXC_PC_DBG_EXC) instead of mtvec. mtvec.MODE/vectoring is not applied.
- Observable at: instr_addr_o; rvfi_pc_wdata of the faulting instruction (trap target).
- Config: none (parameters, not programmable).
- Source: doc doc/03_reference/debug.rst "Parameters" | doc doc/02_user/integration.rst parameter
  table (DmHaltAddr, DmExceptionAddr) | RTL-defined rtl/ibex_if_stage.sv:221-232;
  rtl/ibex_controller.sv:765-766, 827-831
- Edge: no
- Status: ACTIVE

### F-DBG-012: dcsr register layout, reset value, implemented fields
- What: dcsr resets to 0x4000_0003 (xdebugver=4, cause=0, prv=M). Implemented writable fields:
  ebreakm (bit 15), ebreaku (bit 12), step (bit 2), prv (bits 1:0). Read-only: xdebugver (31:28)=4,
  cause (8:6). Hardwired 0: stepie (11), stopcount (10), stoptime (9), mprven (4), nmip (3), bits
  27:16, 14, 5. Bit 13 (ebreaks) is writable although it should read 0: bug candidate B15
  (F-DBG-016). Reads outside debug mode are illegal (F-DBG-050). The read-only cause field and the
  hardwired-zero fields (former F-DBG-014/015) are bins of CG-DBG-007.
- Observable at: csrr read-back of dcsr on rvfi_rd_wdata in the debug program; write-then-read.
- Config: debug mode.
- Source: spec Sdext.adoc "Core Debug Registers", "Debug Mode" (stopcount/stoptime/mprven
  semantics); tools/specs/riscv-debug-spec/xml/core_registers.xml (dcsr field table: ebreaks
  :163-172, nmip :292-298) | doc doc/03_reference/cs_registers.rst "Debug Control and Status
  Register (dcsr)" | RTL-defined rtl/ibex_cs_registers.sv:216-233 (dcsr_t), 810-834 (write WARL),
  1183-1200 (reset)
- Edge: no
- Status: ACTIVE
- Notes: Canonical for F-CSR-074.

### F-DBG-013: dcsr.prv is WARL over {M, U}; writes of S (01) or H (10) read back as U
- What: A dcsr write with prv=01 or prv=10 stores prv=00 (U). prv=11 (M) and prv=00 (U) are stored
  as written. dret then resumes in the stored mode.
- Observable at: csrr read-back of dcsr on rvfi_rd_wdata; rvfi_mode of the first retirement after
  dret.
- Config: debug mode.
- Source: doc doc/03_reference/cs_registers.rst dcsr table (prv WARL) | RTL-defined
  rtl/ibex_cs_registers.sv:813-816
- Edge: yes, of F-DBG-012
- Status: ACTIVE

### F-DBG-014: dcsr.cause is read-only from software
- What: Restates the read-only field list of F-DBG-012 (cause is written only by hardware at entry,
  rtl/ibex_cs_registers.sv:819, 913-915); carried by the parent's readback bin.
- Source: RTL-defined rtl/ibex_cs_registers.sv:819, 913-915
- Edge: yes, of F-DBG-012
- Status: FOLDED into F-DBG-012 (bin CG-DBG-007.cr_bit_rb.cause_c)

### F-DBG-015: dcsr hardwired-zero fields cannot be set (stepie, stopcount, stoptime, mprven, nmip)
- What: Restates the hardwired-zero field list of F-DBG-012 (bits 27:16, 14, 11, 10, 9, 5, 4, 3 read
  0 after a write of 0xFFFF_FFFF, rtl/ibex_cs_registers.sv:821-833); carried by the parent's forced0
  bins.
- Source: RTL-defined rtl/ibex_cs_registers.sv:821-833
- Edge: yes, of F-DBG-012
- Status: FOLDED into F-DBG-012 (bin CG-DBG-007.cr_bit_rb.stepie_0, stopcount_0, stoptime_0, mprven_0, nmip_0, z27_0, z14_0, z5_0)

### F-DBG-016: dcsr bit 13 (ebreaks) is writable and readable although S-mode is absent (bug candidate B15)
- What: The write path forces every unimplemented field to 0 except ebreaks (dcsr_t bit 13). A write
  with bit 13 set reads back 1. The debug spec hardwires ebreaks to 0 on a hart without S-mode
  (misa has no S bit). Functional impact nil: rtl/ibex_controller.sv:481-483 never reads the bit.
- Observable at: csrr read-back of dcsr on rvfi_rd_wdata after csrw dcsr, 0x0000_2000: RTL returns
  bit 13 = 1, spec-expected value 0.
- Config: debug mode.
- Source: spec tools/specs/riscv-debug-spec/xml/core_registers.xml:163-172 (ebreaks WARL, "hardwired
  to 0 if the hart does not support S-mode") | doc cs_registers.rst dcsr ("Other bit fields read as
  zero", ebreaks not listed) | RTL-defined rtl/ibex_cs_registers.sv:222 (field), 810-834 (no force
  to 0); rtl/ibex_controller.sv:481-483 (ebreak_into_debug uses ebreakm/ebreaku only)
- Edge: yes, of F-DBG-012
- Status: ACTIVE
- Notes: Bug candidate B15 (spec violation, formerly doc-defect D5 which is RETIRED). The checker
  expects bit 13 = 0; TP-DBG-018 is `expected-fail (B15)`. Canonical for F-CSR-076. Owner question
  Q2.

### F-DBG-017: ebreak with dcsr.ebreakm=1 (M-mode) or dcsr.ebreaku=1 (U-mode) enters debug mode (cause 1, dpc = ebreak PC)
- What: ebreak decoded in ID with ebreak_into_debug set for the current privilege (ebreakm governs
  M-mode, ebreaku governs U-mode; the other bit is irrelevant) goes DECODE -> FLUSH -> DBG_TAKEN_ID:
  PC := DmHaltAddr, dpc := PC of the ebreak (pc_id), dcsr.cause := 1, dcsr.prv := privilege at
  entry (M or U), privilege inside debug mode is M. mepc/mcause/mtval are not written; the ebreak
  does not retire (minstret unchanged); no breakpoint exception. After dret the core resumes in the
  entry privilege.
- Observable at: RVFI item for the ebreak with rvfi_trap = 0 (rtl/ibex_core.sv:1885-1886: the
  into-debug ebreak is excluded from rvfi_trap; the debug path is is_ebreak(rvfi_insn) &&
  !rvfi_trap && next fetch == DmHaltAddr, the exception path is rvfi_trap = 1) followed by
  instr_addr_o == DmHaltAddr; csrr read-back of mcause unchanged on rvfi_rd_wdata; csrr read-back
  of dpc (== ebreak PC) and dcsr (cause 1, prv = entry mode) on rvfi_rd_wdata; rvfi_mode of the
  first retirement after dret == entry mode. Counter model: the ebreak-into-debug record is a
  not-counted record (minstret unchanged, rtl/ibex_id_stage.sv:1218).
- Config: dcsr.ebreakm (M-mode) / dcsr.ebreaku (U-mode); privilege at the ebreak.
- Source: spec Sdext.adoc "Debug Mode" item 9 (ebreak), tools/specs/riscv-isa-manual/src/priv/
  machine.adoc "Environment Call and Breakpoint" ("Unless overridden by an external debug
  environment") | doc cs_registers.rst dcsr (ebreakm, ebreaku) | RTL-defined
  rtl/ibex_controller.sv:481-483, 874-883, 785-814; rtl/ibex_cs_registers.sv:909-913 (prv);
  rtl/ibex_id_stage.sv:1218 (not counted)
- Edge: no
- Status: ACTIVE
- Notes: Canonical for F-ISA-035 and F-EXC-019. The U-mode case (former F-DBG-019) and the
  {ebreakm, ebreaku} x {M, U} selection matrix (former F-DBG-021) are bins of CG-DBG-003.

### F-DBG-018: ebreak in M-mode with dcsr.ebreakm=0 raises a breakpoint exception
- What: PC := mtvec base (exception code 3, non-vectored), mepc := PC of the ebreak, mcause := 3,
  mtval := 0, mstatus.MPIE := MIE, MIE := 0, MPP := M. The ebreak is not counted in minstret.
- Observable at: rvfi_trap; csrr read-back of mcause/mepc/mtval on rvfi_rd_wdata in the handler;
  instr_addr_o == mtvec base.
- Config: dcsr.ebreakm=0 (reset value); mtvec.
- Source: spec machine.adoc "Environment Call and Breakpoint" (epc = address of EBREAK, no minstret
  increment), "Machine Trap Value (mtval) Register" (mtval zero or address on EBREAK) | doc
  doc/03_reference/exception_interrupts.rst "Exceptions" (code 3) | RTL-defined
  rtl/ibex_controller.sv:884-897, 550 (csr_mtval_o default 0)
- Edge: no
- Status: ACTIVE

### F-DBG-019: ebreak in U-mode with dcsr.ebreaku=1 enters debug mode with dcsr.prv = U
- What: The U-mode instance of F-DBG-017 (same path, dcsr.prv := 0, dret returns to U); carried by
  the parent's privilege bins.
- Source: RTL-defined rtl/ibex_controller.sv:481-483; rtl/ibex_cs_registers.sv:909-913
- Edge: yes, of F-DBG-017
- Status: FOLDED into F-DBG-017 (bin CG-DBG-003.cr_priv_en_outcome.u_off_on_dbg, u_on_on_dbg; CG-DBG-001.cr_cause_prv.ebreak_u)

### F-DBG-020: ebreak in U-mode with dcsr.ebreaku=0 raises a breakpoint exception into M-mode
- What: Alias of F-EXC-017: DBG perspective (the U-mode / dcsr.ebreaku = 0 row of the breakpoint
  exception: cause 3 taken in M-mode with mstatus.MPP := U and mepc := the ebreak PC), see
  canonical.
- Edge: no
- Status: ALIAS of F-EXC-017

### F-DBG-021: ebreak outcome is selected strictly by the current privilege ({ebreakm, ebreaku} x {M, U})
- What: The cross-setting rows of F-DBG-017's selection rule (ebreakm=1 does not affect a U-mode
  ebreak and vice versa, rtl/ibex_controller.sv:481-483); carried by the parent's matrix bins.
- Source: RTL-defined rtl/ibex_controller.sv:481-483
- Edge: yes, of F-DBG-017
- Status: FOLDED into F-DBG-017 (bin CG-DBG-003.cr_priv_en_outcome.m_off_on_exc, u_on_off_exc)

### F-DBG-022: Alias of F-ISA-034
- What: Alias of F-ISA-034: DBG perspective (c.ebreak expands to ebreak; dpc/mepc = PC of the 16-bit
  instruction, resume at PC+2), see canonical.
- Edge: yes, of F-DBG-017
- Status: ALIAS of F-ISA-034

### F-DBG-023: ebreak while already in debug mode re-enters at DmHaltAddr without touching dcsr/dpc
- What: With debug_mode=1 an ebreak (regardless of ebreakm/ebreaku) goes to DBG_TAKEN_ID with
  csr_save disabled: PC := DmHaltAddr, dpc, dcsr.cause and dcsr.prv are unchanged, no exception CSRs
  are written, debug_mode stays 1.
- Observable at: instr_addr_o == DmHaltAddr; csrr read-back of dpc/dcsr on rvfi_rd_wdata unchanged;
  rvfi_ext_debug_mode stays 1.
- Config: debug mode; any ebreakm/ebreaku.
- Source: spec Sdext.adoc "Debug Mode" item 9 ("ebreak ... ends execution of the Program Buffer")
  | RTL-defined rtl/ibex_controller.sv:785-814 (comment case 1), 875-883
- Edge: yes, of F-DBG-017
- Status: ACTIVE
- Notes: Canonical for F-EXC-020.

### F-DBG-024: ebreak in ID while the load/store in WB faults: the WB fault wins, ebreak is discarded
- What: Exception prioritisation gives store_err/load_err from WB precedence over ebrk_insn in ID.
  The load/store access fault is taken (or, in debug mode, vectors to DmExceptionAddr); the ebreak
  never enters debug mode and is re-executed when the handler returns to it.
- Observable at: rvfi_trap on the load/store item with csrr read-back of mcause (5/7, not 3) on
  rvfi_rd_wdata; instr_addr_o == mtvec base (or DmExceptionAddr in debug mode), never DmHaltAddr
  for this event; csrr read-back of dcsr unchanged; the ebreak re-appears later as an RVFI item.
- Config: dcsr.ebreakm=1; PMP region or bus error on the preceding load/store.
- Source: spec machine.adoc "Synchronous exception priority" (earlier instruction first) |
  RTL-defined rtl/ibex_controller.sv:313-331 (prio), 985 (ebrk_insn_prio gate)
- Edge: yes, of F-DBG-017
- Status: ACTIVE

### F-DBG-025: ebreak (ebreakm=1) and debug_req_i / step in the same cycle: ebreak has priority
- What: If an ebreak that should enter debug mode is in FLUSH when enter_debug_mode_prio_q is set,
  the controller goes to DBG_TAKEN_ID (not DBG_TAKEN_IF): dcsr.cause := 1, dpc := ebreak PC.
- Observable at: csrr read-back on rvfi_rd_wdata of dcsr.cause (1) and dpc (== ebreak PC, not
  ebreak PC + 4); instr_addr_o == DmHaltAddr.
- Config: dcsr.ebreakm=1 (or step=1 for the step variant).
- Source: RTL-defined rtl/ibex_controller.sv:978-987 (priority comment), 519-523
- Edge: yes, of F-DBG-017
- Status: ACTIVE
- Notes: The step instance (former F-DBG-041) is a bin of this entry.

### F-DBG-026: Alias of F-PRV-005
- What: Alias of F-PRV-005: DBG perspective (synchronous exception in debug mode: instr_addr_o =
  DmExceptionAddr, mepc/mcause/mtval/mstatus/cpuctrlsts not written, privilege stays M,
  rvfi_ext_debug_mode stays 1). The kind variants F-DBG-027/028/029/030 are folded into
  CG-DBG-004.cp_kind, see canonical.
- Edge: no
- Status: ALIAS of F-PRV-005

### F-DBG-027: Load/store access fault raised from WB while in debug mode
- What: One row of the exception-kind enumeration of F-DBG-026 (alias of the canonical F-PRV-005;
  WB-stage PMP or bus fault in debug mode: instr_addr_o = DmExceptionAddr, no CSR update, rd not
  written); carried by the parent's kind bins. Base feature F-PRV-002 (the former target F-PRV-005
  is an edge or alias of it).
- Source: RTL-defined rtl/ibex_controller.sv:313-317 (WB error priority), 827-831, 900-924
- Edge: yes, of F-PRV-002
- Status: FOLDED into F-PRV-002 (bin CG-DBG-004.cp_kind.load_pmp, store_pmp, load_bus, store_bus)

### F-DBG-028: Illegal instruction in debug mode (including access to a non-existent CSR)
- What: One row of the exception-kind enumeration of F-DBG-026 (alias of the canonical F-PRV-005;
  illegal instruction in debug mode: instr_addr_o = DmExceptionAddr, mtval not written); carried by
  the parent's kind bins. Base feature F-PRV-002 (the former target F-PRV-005 is an edge or alias of
  it).
- Source: RTL-defined rtl/ibex_controller.sv:864-869 (illegal_insn_prio arm), 827-831
- Edge: yes, of F-PRV-002
- Status: FOLDED into F-PRV-002 (bin CG-DBG-004.cp_kind.illegal, illegal_csr)

### F-DBG-029: ecall in debug mode vectors to DmExceptionAddr (spec: UNSPECIFIED)
- What: One row of the exception-kind enumeration of F-DBG-026 (alias of the canonical F-PRV-005;
  ecall in debug mode, which Sdext.adoc "Debug Mode" item 9 leaves UNSPECIFIED, is treated by the
  RTL as an ordinary exception: instr_addr_o = DmExceptionAddr, no CSR update); carried by the
  parent's kind bin. Base feature F-PRV-002 (the former target F-PRV-005 is an edge or alias of it).
- Source: spec Sdext.adoc "Debug Mode" item 9 | RTL-defined rtl/ibex_controller.sv:870-873
  (ecall_insn_prio arm), 827-831
- Edge: yes, of F-PRV-002
- Status: FOLDED into F-PRV-002 (bin CG-DBG-004.cp_kind.ecall)

### F-DBG-030: Instruction fetch error (PMP or bus) in debug mode
- What: One row of the exception-kind enumeration of F-DBG-026 (alias of the canonical F-PRV-005;
  fetch outside the DM region failing PMP at privilege M, or instr_err_i: instr_addr_o =
  DmExceptionAddr, no mtval/mepc update); carried by the parent's kind bins; the PMP-side statement
  is F-DBG-054. Base feature F-PRV-002 (the former target F-PRV-005 is an edge or alias of it).
- Source: RTL-defined rtl/ibex_controller.sv:849-863 (instr_fetch_err_prio arm), 827-831;
  rtl/ibex_core.sv:1587-1600 (fetch PMP channels)
- Edge: yes, of F-PRV-002
- Status: FOLDED into F-PRV-002 (bin CG-DBG-004.cp_kind.fetch_pmp, fetch_bus)

### F-DBG-031: dret resumes: PC := dpc, privilege := dcsr.prv, debug mode exits, pipeline flushed
- What: dret in debug mode is a special request: FLUSH -> pc_mux PC_DRET (fetch dpc), debug_mode :=
  0, priv_lvl := dcsr.prv. dcsr, dpc, mstatus are otherwise unchanged. dret itself retires (counts
  in minstret). The resume privilege is whatever dcsr.prv holds, including a value written by the
  debugger (former F-DBG-034, now a bin of CG-DBG-005).
- Observable at: instr_addr_o == dpc; rvfi_ext_debug_mode falls; rvfi_mode of the next retired
  instruction == dcsr.prv. rvfi_pc_wdata of the dret record is dret pc + 4, the sequential fetch
  address (the dret leaves ID in DECODE and PC_DRET is set one cycle later in FLUSH,
  rtl/ibex_core.sv:2084, rtl/ibex_id_stage.sv:991, :1130, rtl/ibex_controller.sv:957-966; fact-check
  X-1, C-1): the resume target is the NEXT record's rvfi_pc_rdata == dpc, never the dret's pc_wdata.
- Config: dpc, dcsr.prv.
- Source: spec Sdext.adoc "Resume" | doc cs_registers.rst "Debug PC Register (dpc)" | RTL-defined
  rtl/ibex_controller.sv:961-966; rtl/ibex_cs_registers.sv:949-951; rtl/ibex_if_stage.sv:247;
  rtl/ibex_decoder.sv:745-746
- Edge: no
- Status: ACTIVE

### F-DBG-032: dret outside debug mode is an illegal instruction (M-mode and U-mode)
- What: The decoder recognises dret in any mode, but id_stage flags illegal_dret_insn when
  debug_mode=0. Exception code 2, mtval := instruction bits (0x7B200073), mepc := dret PC.
- Observable at: rvfi_trap; csrr read-back of mcause (2) and mtval (0x7B200073) on rvfi_rd_wdata;
  instr_addr_o == mtvec base.
- Config: priv M or U; debug_mode=0.
- Source: spec Sdext.adoc "Core Debug Registers" (debug CSRs/dret are debug-mode only; illegal
  otherwise) | RTL-defined rtl/ibex_id_stage.sv:603-611
- Edge: yes, of F-DBG-031
- Status: ACTIVE
- Notes: Canonical for F-ISA-039, F-EXC-012, F-PRV-025.

### F-DBG-033: Alias of F-PRV-015
- What: Alias of F-PRV-015: DBG perspective (dret to U with mstatus.MPRV=1 leaves MPRV set: bug
  candidate B1, Sdext.adoc "Resume" vs rtl/ibex_cs_registers.sv:949-951), see canonical.
- Edge: yes, of F-DBG-031
- Status: ALIAS of F-PRV-015

### F-DBG-034: dret when dcsr.prv was modified by the debugger changes the resume privilege
- What: The parent's "privilege := dcsr.prv" with the Config variable dcsr.prv at a software-written
  value (rtl/ibex_cs_registers.sv:949-951); carried by the parent's prv-source bins.
- Source: doc cs_registers.rst dcsr prv | RTL-defined rtl/ibex_cs_registers.sv:949-951
- Edge: yes, of F-DBG-031
- Status: FOLDED into F-DBG-031 (bin CG-DBG-005.cr_prvsrc_target.swu_u, swm_m; CG-DBG-005.cr_prv_next.u_run)

### F-DBG-035: dpc is WARL with bit 0 hardwired 0
- What: A CSR write to dpc stores {wdata[31:1], 1'b0}. Hardware entry writes pc values (always
  2-byte aligned). dret to an odd dpc write therefore fetches the even address.
- Observable at: csrr read-back of dpc on rvfi_rd_wdata after csrw dpc, 0x...01 returns 0x...00;
  instr_addr_o after dret is the even address.
- Config: debug mode.
- Source: doc cs_registers.rst "Debug PC Register (dpc)" | RTL-defined rtl/ibex_cs_registers.sv:
  746 (depc_d), 838, 1206-1216
- Edge: yes, of F-DBG-031
- Status: ACTIVE

### F-DBG-036: dret while a load/store issued in debug mode is still outstanding in WB
- What: dret is a special request; the controller waits for ready_wb_i before FLUSH, so the
  debug-mode load/store completes (and may fault, taking priority and vectoring to DmExceptionAddr
  instead of resuming).
- Observable at: data_rvalid_i before instr_addr_o == dpc; on fault instr_addr_o == DmExceptionAddr
  and rvfi_ext_debug_mode stays 1.
- Config: debug mode; memory latency.
- Source: RTL-defined rtl/ibex_controller.sv:664-677 (special_req waits for ready_wb_i |
  wb_exception), 313-331
- Edge: yes, of F-DBG-031
- Status: ACTIVE

### F-DBG-037: Single step: dcsr.step=1 executes exactly one instruction after dret, then re-enters (cause 4)
- What: After dret with step=1, the first valid instruction outside debug mode sets do_single_step;
  once it leaves ID/WB the controller enters DBG_TAKEN_IF: dpc := next PC (pc_if), dcsr.cause := 4,
  dcsr.prv := current privilege. IF is halted so no second instruction enters ID. For a sequential
  instruction dpc is PC+2 / PC+4 (former F-DBG-039, now a bin of CG-DBG-006).
- Observable at: exactly one rvfi retirement with rvfi_ext_debug_mode=0 between two debug-mode
  periods; csrr read-back on rvfi_rd_wdata of dpc (== PC of the following instruction) and
  dcsr.cause (4).
- Config: dcsr.step=1 written in debug mode before dret.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" | doc cs_registers.rst dcsr (step) |
  RTL-defined rtl/ibex_controller.sv:451-477 (do_single_step_d), 700-711
- Edge: no
- Status: ACTIVE

### F-DBG-038: Step over a taken branch or jump: dpc = branch/jump target
- What: Folded into F-DBG-037: dpc = branch/jump target is the parent's own formula dpc := next PC
  (pc_if) evaluated for a control transfer, with the parent's dpc read-back observable (the
  sequential value was already folded as F-DBG-039) (v2 edge rule, second pass; Critic M-9); carried
  by the parent's stepped-kind and dpc bins.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" | RTL-defined rtl/ibex_controller.sv:
  773 (csr_save_if_o); rtl/ibex_if_stage.sv:420
- Edge: yes, of F-DBG-037
- Status: FOLDED into F-DBG-037 (bin CG-DBG-006.cr_stepped_prv.brtaken_m, jal_m, jalr_m; CG-DBG-001.cp_dpc_kind.br_target)

### F-DBG-039: Step over a not-taken branch and over a compressed instruction: dpc = PC+4 / PC+2
- What: The parent's default "dpc := next PC" for sequential instructions (2 for a 16-bit
  instruction incl. a not-taken c.beqz/c.bnez, 4 otherwise); carried by the parent's stepped-class
  bins.
- Source: RTL-defined rtl/ibex_controller.sv:773 (csr_save_if_o); rtl/ibex_if_stage.sv:420
- Edge: yes, of F-DBG-037
- Status: FOLDED into F-DBG-037 (bin CG-DBG-006.cr_stepped_prv.brnot_m, cbrnot_m, comp_m; CG-DBG-001.cr_cause_dpc.step_next)

### F-DBG-040: Step over an instruction that traps: exception is taken, dpc = trap handler address
- What: If the stepped instruction raises a synchronous exception (illegal, ecall, ebreak with
  ebreakm=0, fetch error, load/store fault), mepc/mcause/mtval/mstatus are updated and PC := mtvec
  target; debug mode is then re-entered immediately with dpc := mtvec target, dcsr.cause := 4,
  dcsr.prv := M (handler privilege). No handler instruction executes.
- Observable at: rvfi_trap on the stepped instruction; instr_addr_o sequence mtvec base then
  DmHaltAddr with no rvfi_valid item in between; csrr read-back on rvfi_rd_wdata of dpc (== mtvec
  base) and dcsr.prv (M even if the step started in U-mode).
- Config: dcsr.step=1; mtvec; priv M or U.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" ("Debug Mode is re-entered immediately
  after the PC is changed to the trap handler, and the appropriate tval and cause registers are
  updated") | RTL-defined rtl/ibex_controller.sv:971-987
- Edge: yes, of F-DBG-037
- Status: ACTIVE

### F-DBG-041: Step over ebreak with ebreakm/ebreaku=1: cause 1 wins over cause 4
- What: The step instance of F-DBG-025 (ebreak-into-debug in FLUSH with enter_debug_mode_prio_q set
  goes to DBG_TAKEN_ID: dcsr.cause := 1, dpc := ebreak PC); carried by that entry's bins. Base
  feature F-DBG-017 (the former target F-DBG-025 is an edge or alias of it).
- Source: RTL-defined rtl/ibex_controller.sv:978-987, 519-523
- Edge: yes, of F-DBG-017
- Status: FOLDED into F-DBG-017 (bin CG-DBG-003.cr_coincident_outcome.step_dbg; CG-DBG-006.cr_stepped_retired.ebreakdbg_ok)

### F-DBG-042: Step with an interrupt pending: the interrupt is not taken during the step (stepie=0)
- What: handle_irq is masked by debug_single_step_i, so with dcsr.step=1 no interrupt (incl. NMI) is
  taken between dret and the re-entry. After the debugger clears step and resumes, the interrupt is
  taken before the first instruction (mepc := dpc). irq_nm_i is masked by the same term (former
  F-DBG-043, now a bin of CG-DBG-006/009).
- Observable at: no rvfi_intr during the step; irq_pending_o stays high; after resume with step=0
  rvfi_intr with csrr read-back of mepc == dpc on rvfi_rd_wdata.
- Config: dcsr.step=1; mstatus.MIE=1, mie bit; irq_*_i held.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" ("if the cause was a pending interrupt no
  instructions might be executed at all" applies only when stepie=1); introduction.adoc "Minor
  Changes from 0.13 to 1.0" ("NMIs are disabled by dcsr.stepie") | RTL-defined
  rtl/ibex_controller.sv:492-500; rtl/ibex_cs_registers.sv:821-822 (stepie forced 0)
- Edge: yes, of F-DBG-037
- Status: ACTIVE

### F-DBG-043: Step with NMI (irq_nm_i) pending: NMI deferred like other interrupts
- What: The irq_nm_i instance of F-DBG-042 (handle_irq masks irq_nm with the same
  debug_single_step_i term; dcsr.nmip reads 0, B5 / F-DBG-057); carried by that entry's bins. Base
  feature F-DBG-037 (the former target F-DBG-042 is an edge or alias of it).
- Source: RTL-defined rtl/ibex_controller.sv:498-500; rtl/ibex_cs_registers.sv:825 (nmip forced 0)
- Edge: yes, of F-DBG-037
- Status: FOLDED into F-DBG-037 (bin CG-DBG-006.cr_pending_cause.nmi_step; CG-DBG-009.cr_src_window.nmi_step)

### F-DBG-044: Step over WFI: no sleep, direct debug entry from FLUSH; dpc = WFI PC + 4; core_busy_o stays On
- What: With dcsr.step = 1 outside debug mode, do_single_step_d = 1 for the wfi in DECODE
  (rtl/ibex_controller.sv:462) and enter_debug_mode_prio_d = 1 (:474-475); wfi is a special request
  (:287-293) so DECODE goes to FLUSH (:664-677). In FLUSH the `else if (wfi_insn) ctrl_fsm_ns =
  WAIT_SLEEP` (:966-967) is overridden by `if (enter_debug_mode_prio_q ...) ctrl_fsm_ns =
  DBG_TAKEN_IF` (:985-987, flop :1046): WAIT_SLEEP and SLEEP are never entered, the core does not
  sleep, no interrupt is needed, dpc = WFI + 4 and dcsr.cause = 4 (step). ctrl_busy never drops, so
  core_busy_o stays On throughout (rtl/ibex_core.sv:496-522). (Critic plan-set review M-1 and its
  Section 5 correction of v1 C-06.)
- Observable at: rvfi_ext_debug_mode = 1 on the first record after the stepped WFI, whose
  rvfi_pc_rdata is DmHaltAddr (instr_addr_o fetch of DmHaltAddr follows the WFI directly); csrr
  read-back of dpc = WFI + 4 and dcsr.cause = 4 on rvfi_rd_wdata; core_busy_o never equals
  IbexMuBiOff between the WFI retirement and the debug-ROM fetch; no dependence on irq_*_i.
- Config: dcsr.step=1; mstatus.TW=0 (else WFI in U-mode is illegal and F-DBG-040 applies).
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" ("If the instruction being stepped over
  would normally stall the hart, then instead the instruction is treated as a nop. This includes
  wfi") | RTL-defined rtl/ibex_controller.sv:598-604 (WAIT_SLEEP), 606-621 (SLEEP exit terms),
  634-646
- Edge: yes, of F-DBG-037
- Status: ACTIVE
- Notes: fact-check X-8 / C-5 confirms: NO dip for the stepped WFI (the v1 C-06 one-cycle-dip wording
  is retired; TP-DBG-049 asserts no Off cycle and CG-DBG-001.cr_cause_ctx.step_sleep is an
  ignore_bin). The haltreq-coincident WFI (F-DBG-068) never reaches WAIT_SLEEP either; an unstepped
  WFI woken by debug_req_i (F-DBG-009) shows the one-cycle WAIT_SLEEP dip when the request is
  already high in the first SLEEP cycle and the full sleep length otherwise; a WFI executed in debug
  mode (F-DBG-059) shows the one-cycle dip.

### F-DBG-045: Step over mret: dpc = mepc, dcsr.prv = new privilege (mstatus.MPP)
- What: mret executes fully in FLUSH (priv := MPP, MIE := MPIE, MPRV cleared if MPP != M), then
  DBG_TAKEN_IF: dpc := mepc, dcsr.prv := the new privilege.
- Observable at: csrr read-back on rvfi_rd_wdata of dpc (== mepc), dcsr.prv (== previous
  mstatus.MPP) and mstatus (MIE := MPIE); instr_addr_o == DmHaltAddr with no rvfi_valid item at
  mepc before it.
- Config: dcsr.step=1; mstatus.MPP, MPIE; mepc.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr", "Halt" (prv reflects current mode) |
  RTL-defined rtl/ibex_controller.sv:953-960, 985-987; rtl/ibex_cs_registers.sv:953-963
- Edge: yes, of F-DBG-037
- Status: ACTIVE
- Notes: Same FLUSH -> DBG_TAKEN_IF arc as the haltreq variant F-DBG-068.

### F-DBG-046: Step over a Zcmp instruction (cm.push/cm.pop/cm.popret/cm.popretz/cm.mvsa01/cm.mva01s)
- What: The step instance of F-DBG-010 (enter_debug_mode masked while expanded micro-ops are in ID;
  the whole sequence completes, dpc := next PC or the popret target); carried by that entry's bins.
  Base feature F-DBG-001 (the former target F-DBG-010 is an edge or alias of it). One RVFI record
  per micro-op (fact-check X-14, C-12: rvfi_insn = the 32-bit expansion, the halfword on
  rvfi_ext_expanded_insn, every record with rvfi_ext_debug_mode = 0 and rvfi_ext_expanded_insn_valid
  = 1, only the last with rvfi_ext_expanded_insn_last = 1); micro-ops entering ID while debug_req_i
  is high during the mask report rvfi_ext_debug_req = 1 (C-3). The step checker counts the sequence
  as one instruction (TP-DBG-051).
- Source: RTL-defined rtl/ibex_controller.sv:473-477; rtl/ibex_id_stage.sv:1218-1220
- Edge: yes, of F-DBG-001
- Status: FOLDED into F-DBG-001 (bin CG-DBG-006.cr_stepped_retired.push_ok, popret_ok; CG-DBG-001.cr_cause_ctx.step_zcmp)

### F-DBG-047: Step over a load/store with slow memory or a multi-cycle divide
- What: Folded into F-DBG-037: waiting for the LSU response or the divider is the parent's own "once
  it leaves ID/WB" mechanism; slow memory or a divide is a timing variation with the parent's dpc =
  PC + 4 outcome (v2 edge rule, second pass; Critic M-9); carried by the parent's stepped-kind bins.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" | RTL-defined rtl/ibex_controller.sv:
  700-711 (stall || id_wb_pending)
- Edge: yes, of F-DBG-037
- Status: FOLDED into F-DBG-037 (bin CG-DBG-006.cr_stepped_prv.loadslow_m, storeslow_m, div_m)

### F-DBG-048: Step over a jump to an address whose fetch faults: the fault is deferred to the next resume
- What: The jump completes and debug mode is entered with dpc := target; the fetch error (PMP or
  bus) attached to the target instruction in IF is discarded by the flush and only raised when the
  instruction is actually executed after the next dret.
- Observable at: no rvfi_trap and no mtvec fetch on instr_addr_o during the step; csrr read-back of
  dpc == target on rvfi_rd_wdata; after resume with step=0 rvfi_trap with csrr read-back of mepc ==
  target.
- Config: dcsr.step=1; PMP region denying execute at the target, or a TB-injected instr_err_i.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" ("that exception does not occur until the
  next time the hart is resumed") | RTL-defined rtl/ibex_controller.sv:700-711, 764-783 (flush_id)
- Edge: yes, of F-DBG-037
- Status: ACTIVE

### F-DBG-049: Step and debug_req_i both active: cause 3 (haltreq) is recorded, one instruction executes
- What: debug_cause_d prioritises debug_req_i over do_single_step_d (rtl/ibex_controller.sv:519-523).
  The entry timing depends on when the request is seen (fact-check X-7, C-3): a request already high
  in the first DECODE after the dret's FLUSH (ID empty) takes DBG_TAKEN_IF at once (:704-708): ZERO
  instructions retire, dpc unchanged, cause 3 (the F-DBG-007 re-halt arc; the step does not force
  one instruction). Only a request rising after the stepped instruction entered ID lets that
  instruction complete: one retirement (its record carries rvfi_ext_debug_req = 0), cause 3, dpc =
  next pc.
- Observable at: csrr read-back of dcsr.cause == 3 on rvfi_rd_wdata; zero (request high at the
  resume) or exactly one (request rising in the stepped instruction's ID window) rvfi_valid item
  with rvfi_ext_debug_mode=0 between the two debug windows, classified from the driver timestamp
  (TP-DBG-054).
- Config: dcsr.step=1; debug_req_i high across the dret.
- Source: RTL-defined rtl/ibex_controller.sv:519-523, 474-475
- Edge: yes, of F-DBG-037
- Status: ACTIVE
- Notes: Spec leaves the cause choice implementation-defined; the debug spec's step text
  ("regardless of the reason for resuming") describes the armed step, while haltreq requires the
  hart to halt "as soon as possible": the zero-instruction re-halt is RTL-defined and both classes
  are checked (pass).

### F-DBG-050: Debug CSRs (dcsr, dpc, dscratch0, dscratch1) are accessible only in debug mode; trigger CSRs are not so restricted
- What: Any CSR access (read or write, any csr op) to 0x7B0-0x7B3 with debug_mode=0 raises an
  illegal instruction exception in M-mode and U-mode: illegal_csr_dbg = dbg_csr & ~debug_mode_i
  (rtl/ibex_cs_registers.sv:402) and dbg_csr is set only in the CSR_DCSR/CSR_DPC/CSR_DSCRATCH0/1
  read arms (:550-565). Inside debug mode (privilege M) the access succeeds. The trigger CSRs
  tselect/ tdata1/tdata2/tdata3 (0x7A0-0x7A3) and mcontext/mscontext/scontext are NOT in this set:
  their arms (:636-663) set only illegal_csr = ~DbgTriggerEn, so with DbgTriggerEn=1 they are legal
  from M-mode (reads return the value, M-mode writes are silently dropped: F-TRG-002/005/029), as
  csrs.adoc requires (0x7A0-0x7AF machine-mode accessible, 0x7B0-0x7BF debug-mode only).
- Observable at: rvfi_trap with csrr read-back of mcause (2) and mtval (instruction bits) on
  rvfi_rd_wdata for 0x7B0-0x7B3 outside debug mode; rvfi_rd_wdata returns the CSR value inside debug
  mode; no rvfi_trap for tselect/tdata* from M-mode.
- Config: debug_mode; privilege.
- Source: spec tools/specs/riscv-isa-manual/src/priv/csrs.adoc:60-63 ("0x7A0-0x7AF are accessible to
  machine mode, whereas 0x7B0-0x7BF are only visible to debug mode"); Sdext.adoc "Core Debug
  Registers" | RTL-defined rtl/ibex_cs_registers.sv:348, 402-406, 550-565, 636-663
- Edge: no
- Status: ACTIVE
- Notes: Canonical for F-CSR-017 and F-EXC-009 (Critic C-02). Doc defect D12: doc/03_reference/
  debug.rst:54-55 says the trigger registers are "accessible from Debug Mode only" and trap
  otherwise; the RTL and cs_registers.rst allow M-mode reads and drop M-mode writes.

### F-DBG-051: dscratch0 / dscratch1 are full 32-bit read/write scratch registers
- What: Any value written reads back unchanged; reset value 0; no side effects.
- Observable at: csrr read-back on rvfi_rd_wdata in debug mode; all-ones / all-zeros / alternating.
- Config: debug mode.
- Source: doc cs_registers.rst "Debug Scratch Register 0/1" | RTL-defined rtl/ibex_cs_registers.sv:
  840-841, 1224-1235, 1242-1253
- Edge: no
- Status: ACTIVE

### F-DBG-052: Alias of F-PMP-095
- What: Alias of F-PMP-095: DBG perspective (PMP bypass for DM-region accesses in debug mode,
  rtl/ibex_pmp.sv:239-240, :251). Boundary and outside-region variants F-DBG-053/054 stay ACTIVE as
  its edges, see canonical.
- Edge: no
- Status: ALIAS of F-PMP-095

### F-DBG-053: DM-region bypass boundaries: DmBaseAddr, DmBaseAddr+DmAddrMask, one past, one before
- What: Address exactly DmBaseAddr and DmBaseAddr|DmAddrMask are bypassed; DmBaseAddr-4 and
  DmBaseAddr+DmAddrMask+1 are PMP-checked. For a 4-byte fetch at DmBaseAddr|DmAddrMask-1 (32-bit
  instruction straddling the region end) the second-half channel (pc_if+2) is outside the region and
  is checked.
- Observable at: rvfi_trap on the straddling fetch with instr_addr_o == DmExceptionAddr; data_req_o
  asserted and no rvfi_trap for loads at DmBaseAddr and (DmBaseAddr|DmAddrMask)-3; data_req_o
  suppressed and rvfi_trap for DmBaseAddr-4 and DmBaseAddr+DmAddrMask+1.
- Config: PMP denying everything (e.g. MMWP=1 with no regions) in debug mode.
- Source: RTL-defined rtl/ibex_pmp.sv:239-240 (mask compare); rtl/ibex_core.sv:1587, 1591
  (PMP_I2 = pc_if+2)
- Edge: yes, of F-PMP-095
- Status: ACTIVE
- Notes: The straddling-instruction case (PMP_I2 checked at DmBaseAddr + DmAddrMask - 1) is stated
  by F-PMP-098; this entry owns the four boundary addresses.

### F-DBG-054: PMP still applies in debug mode outside the DM region (fetch with M privilege)
- What: Alias of F-PMP-097: DBG perspective (fetches outside the DM range are PMP-checked with M
  privilege in debug mode; with MMWP = 1 and no matching region, or an MML locked region without X,
  the fetch faults and vectors to DmExceptionAddr), see canonical.
- Edge: yes, of F-PMP-095
- Status: ALIAS of F-PMP-097

### F-DBG-055: mstatus.MPRV is honoured for data accesses in debug mode although dcsr.mprven=0 (bug candidate)
- What: priv_mode_lsu_o = mstatus.mprv ? mstatus.mpp : priv_lvl_q has no debug_mode term. With
  MPRV=1/MPP=U set (by the debug program or before halting), debug-mode loads/stores outside the DM
  region are PMP-checked as U-mode and can fault to DmExceptionAddr. dcsr.mprven is hardwired 0,
  which per Sdext means MPRV is ignored in debug mode.
- Observable at: data_req_o suppressed and rvfi_trap with instr_addr_o == DmExceptionAddr for an
  M-permitted, U-denied region while rvfi_ext_debug_mode=1 with MPRV=1, MPP=U.
- Config: mstatus.MPRV=1, MPP=U; PMP region with M-only permission; debug mode.
- Source: spec Sdext.adoc "Debug Mode" item 2 ("mprv in mstatus may be ignored according to
  dcsr.mprven") and NOTE | RTL-defined rtl/ibex_cs_registers.sv:826 (mprven=0), 998
  (priv_mode_lsu_o); rtl/ibex_core.sv:1604
- Edge: no
- Status: ACTIVE
- Notes: Bug candidate B2 (RTL/spec disagreement). Canonical (F-PMP-097 is the PMP-side carrier).
  Owner question Q4.

### F-DBG-056: All interrupts including NMI are ignored in debug mode; taken after dret before any instruction
- What: handle_irq is masked by debug_mode_q. A pending enabled interrupt (or irq_nm_i) is taken in
  the first DECODE cycle after dret, with mepc := dpc (the resume address) and no instruction
  retired in between. Interrupt state (mip) remains visible.
- Observable at: no IRQ_TAKEN/rvfi_intr while rvfi_ext_debug_mode=1; after dret rvfi_intr on the
  first instruction with csrr read-back of mepc == dpc on rvfi_rd_wdata; irq_pending_o high
  throughout.
- Config: mstatus.MIE, mie; dcsr.step=0; dcsr.prv (interrupts in U-mode are always enabled).
- Source: spec Sdext.adoc "Debug Mode" item 3 | doc doc/03_reference/exception_interrupts.rst
  "Interrupts" ("In Debug Mode, all interrupts including the NMI are ignored") | RTL-defined
  rtl/ibex_controller.sv:492-500
- Edge: no
- Status: ACTIVE
- Notes: Canonical for F-IRQ-039.

### F-DBG-057: NMI arriving in debug mode: dcsr.nmip stays 0; NMI taken after dret to mtvec+0x7C
- What: Alias of F-IRQ-037: DBG perspective (dcsr.nmip reads 0 while an NMI is held pending in debug
  mode, bug candidate B5, core_registers.xml:292-298; after dret the NMI is taken at mtvec + 0x7C
  with mepc = dpc), see canonical.
- Edge: yes, of F-DBG-056
- Status: ALIAS of F-IRQ-037

### F-DBG-058: debug_req_i arriving while IRQ_TAKEN is in progress: handler entry completes, then debug
- What: IRQ_TAKEN does not sample debug_req_i; the interrupt CSRs are written and PC := vector. In
  the following DECODE (ID empty) debug mode is entered with dpc := vector address; no handler
  instruction executes; mstatus.MIE is already 0.
- Observable at: no rvfi_valid item with rvfi_intr before rvfi_ext_debug_mode=1; csrr read-back on
  rvfi_rd_wdata of dpc (== vector address) and mepc (== interrupted PC).
- Config: enabled interrupt; debug_req_i rising one cycle after the interrupt is accepted.
- Source: RTL-defined rtl/ibex_controller.sv:729-762 (IRQ_TAKEN), 704-707
- Edge: yes, of F-DBG-056
- Status: ACTIVE

### F-DBG-059: WFI executed in debug mode acts as a nop (ctrl_busy dip visible on core_busy_o only when the bus and icache are idle)
- What: WFI in debug mode goes FLUSH -> WAIT_SLEEP -> SLEEP. WAIT_SLEEP clears ctrl_busy_o for its
  single cycle (rtl/ibex_controller.sv:598-604); in SLEEP the exit term is true because
  debug_mode_q=1, so ctrl_busy_o stays high and the FSM leaves for FIRST_FETCH at once (:606-621,
  else-branch not taken). ctrl_busy is low for exactly one cycle; execution continues at WFI+4 in
  debug mode. Port rule (gen_tb_architecture.md 8.2 item 1): core_busy_o = ctrl_busy | if_busy |
  lsu_busy, so the dip reaches core_busy_o only when no instruction-bus beat is outstanding, no
  icache invalidation is active and the LSU is idle in that cycle; otherwise it is invisible.
- Observable at: core_busy_o == IbexMuBiOff for exactly one cycle (instr_req_o low in that cycle)
  only when the port rule holds in that cycle (no instruction-bus beat outstanding, no icache
  invalidation sweep active, LSU idle: core_busy_o = ctrl_busy | if_busy | lsu_busy,
  rtl/ibex_core.sv:496-522); otherwise no dip is visible at the port and the ctrl_busy fact is not
  observable; the next fetch on instr_addr_o is WFI+4 and its retirement carries
  rvfi_ext_debug_mode=1; no dependence on irq_*_i / irq_nm_i.
- Config: debug mode.
- Source: spec Sdext.adoc "Debug Mode" item 8 ("Instructions that place the hart into a stalled
  state act as a nop") | RTL-defined rtl/ibex_controller.sv:598-604, 606-621
- Edge: no
- Status: ACTIVE
- Notes: Critic C-06 correction (the draft said the dip lasted the WAIT_SLEEP and SLEEP cycles).
  Cross-reference (Critic M-10): the step-over-WFI case outside debug mode never reaches WAIT_SLEEP
  and keeps core_busy_o On; it is F-IRQ-051 / F-DBG-044, not this entry.

### F-DBG-060: mret executed in debug mode (spec UNSPECIFIED): RTL performs the mret and stays in debug mode
- What: mret in debug mode is executed as in M-mode: priv := MPP, MIE := MPIE, MPRV cleared if MPP
  != M, PC := mepc, debug_mode stays 1. If MPP=U the core is then in debug mode with U privilege:
  debug CSR and trigger CSR accesses (0x7A0-0x7B3 are M-level addresses) raise illegal instruction
  (-> DmExceptionAddr) and fetch PMP checks use U.
- Observable at: rvfi_mode == U while rvfi_ext_debug_mode == 1; a subsequent csrr dcsr item carries
  rvfi_trap and instr_addr_o == DmExceptionAddr.
- Config: mstatus.MPP, mepc.
- Source: spec Sdext.adoc "Debug Mode" item 9 (UNSPECIFIED) | RTL-defined rtl/ibex_controller.sv:
  953-960; rtl/ibex_cs_registers.sv:403 (illegal_csr_priv), 953-976
- Edge: no
- Status: ACTIVE
- Notes: Owner question Q5: exclude mret/ecall-in-debug from random stimulus or model RTL behaviour.
  B6 ("exception in debug mode forces privilege M", F-EXC-046) is reclassified RTL-defined: Sdext
  runs debug mode at M privilege and leaves privilege changes UNSPECIFIED, so TP-DBG-034 is
  `Expected: pass`, not expected-fail (Critic C-20).

### F-DBG-061: Debug entry flushes the pipeline; the instruction in IF at entry is not executed
- What: DBG_TAKEN_IF/ID assert flush_id and pc_set; the IF-stage instruction (whose address became
  dpc) is dropped and re-fetched after dret. Register file and memory state reflect only the
  instructions that retired before entry.
- Observable at: rvfi order continuity across the debug window; instr_addr_o re-fetches dpc after
  dret.
- Config: none.
- Source: RTL-defined rtl/ibex_controller.sv:764-783, 1108-1115 (assertion
  IbexPipelineFlushOnChangingDebugMode)
- Edge: no
- Status: ACTIVE

### F-DBG-062: Alias of F-IC-040
- What: Alias of F-IC-040: DBG perspective (icache_enable_o forced off in and when entering debug
  mode, rtl/ibex_cs_registers.sv:1970-1971), see canonical.
- Edge: no
- Status: ALIAS of F-IC-040

### F-DBG-063: Performance counters keep counting in debug mode (dcsr.stopcount hardwired 0)
- What: mcycle, minstret and mhpmcounter3-12 increment for debug-mode cycles/instructions exactly as
  outside debug mode (subject only to mcountinhibit).
- Observable at: csrr read-back of mcycle/minstret on rvfi_rd_wdata before dret vs. after entry;
  rvfi_ext_mcycle, rvfi_ext_mhpmcounters on debug-mode retirements.
- Config: mcountinhibit.
- Source: spec Sdext.adoc "Debug Mode" item 6 ("If dcsr.stopcount is 0 then counters continue") |
  RTL-defined rtl/ibex_cs_registers.sv:827, 1622-1649 (no debug term in counter_inc_i)
- Edge: no
- Status: ACTIVE

### F-DBG-064: Privilege inside debug mode is M; dcsr.prv records the pre-entry privilege
- What: priv_lvl_d := M on every debug entry (csr_save_cause with debug_csr_save). All M-level CSRs
  are accessible in debug mode. U-mode entry (haltreq, step, ebreaku, trigger from U) records prv=0.
- Observable at: csrr read-back of dcsr.prv on rvfi_rd_wdata; rvfi_mode == 3 for retirements with
  rvfi_ext_debug_mode=1.
- Config: privilege at entry.
- Source: spec Sdext.adoc "Debug Mode" item 2, "Halt" item 2 | RTL-defined
  rtl/ibex_cs_registers.sv:909-913
- Edge: no
- Status: ACTIVE

### F-DBG-065: Alias of F-RVFI-018
- What: Alias of F-RVFI-018: DBG perspective (rvfi_ext_debug_req / rvfi_ext_debug_mode), see
  canonical.
- Notes: DBG-side semantics (fact-check X-6, C-3): rvfi_ext_debug_req is the debug_req_i level at
  the record's IF->ID transfer (rtl/ibex_core.sv:1996-2001), or captured_debug_req when the request
  arrived on an empty ID (:1949-1957); the instruction in ID at the rise reports 0; the first
  debug-ROM record reports 1; {req 1, mode 0} is reachable only by a Zcmp micro-op entering ID
  during the expansion mask (rtl/ibex_controller.sv:474-477) or by the sticky capture after a
  dropped pulse (TP-DBG-010 / TP-DBG-070).
- Edge: no
- Status: ALIAS of F-RVFI-018

### F-DBG-066: Back-to-back debug entries: dret landing on an ebreak (ebreakm=1) or on a trigger address
- What: The first instruction after dret can immediately cause re-entry (ebreak -> cause 1, dpc :=
  its PC; trigger -> cause 2, dpc := its PC == tdata2, i.e. dpc unchanged). No instruction retires
  in between. The trigger half (former F-TRG-016) is a bin of CG-DBG-005.
- Observable at: consecutive DmHaltAddr fetches on instr_addr_o with zero rvfi_valid items having
  rvfi_ext_debug_mode=0 in between; csrr read-back on rvfi_rd_wdata of dcsr.cause (1 or 2) and dpc.
- Config: dcsr.ebreakm; tdata1.execute/tdata2.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" (trigger at new address fires when
  executed) | RTL-defined rtl/ibex_controller.sv:474-477, 874-883
- Edge: yes, of F-DBG-031
- Status: ACTIVE

### F-DBG-067: Alias of F-SEC-023
- What: Alias of F-SEC-022: DBG perspective (two exceptions in debug mode do not assert the
  ibex_core output double_fault_seen_o nor set cpuctrlsts.sync_exc_seen,
  rtl/ibex_cs_registers.sv:918-946), see canonical.
- Edge: yes, of F-DBG-026 (ALIAS of F-PRV-005)
- Status: ALIAS of F-SEC-022

### F-DBG-068: debug_req_i sampled in the DECODE cycle of a wfi / mret / flushing CSR write: entry from FLUSH (H-C1 non-exception variants)
- What: enter_debug_mode_prio_d (debug_req_i & ~debug_mode_q, rtl/ibex_controller.sv:474-475) is
  registered in the DECODE cycle in which a special request (wfi, mret, csr_pipe_flush; :287-293)
  takes the controller to FLUSH. In FLUSH the special arm runs first (:953-967: mret restores
  privilege/MIE and sets PC_ERET; wfi selects ctrl_fsm_ns = WAIT_SLEEP) and the priority check
  (:985-987) then overrides ctrl_fsm_ns to DBG_TAKEN_IF. Consequences: (wfi) WAIT_SLEEP/SLEEP are
  never entered, core_busy_o never drops, dpc := wfi PC + 4; (mret) the mret completes, dpc := mepc,
  dcsr.prv := old mstatus.MPP, mstatus.MIE := MPIE, MPRV cleared if MPP != M; (CSR flush) dpc :=
  csrw PC + 4 and the CSR write is committed. dcsr.cause := 3. No instruction retires in between.
  A request already high BEFORE the special instruction's IF->ID transfer does not produce this
  arc: halt_if blocks the instruction (:700-708) and the RTL takes a plain haltreq entry with dpc =
  its pc (the instruction executes after dret) (fact-check X-6 / X-7). dret is not an instance of
  this arc: during the dret's DECODE cycle debug_mode_q=1 masks
  enter_debug_mode_prio_d, so a held debug_req_i re-halts through the DECODE -> DBG_TAKEN_IF arc in
  the first cycle after the flush (F-DBG-007).
- Observable at: the wfi/mret/csrw record carries rvfi_ext_debug_req == 0 (the flag is sampled at
  its IF->ID transfer, before the rise, rtl/ibex_core.sv:1996-2001; fact-check X-6, C-3) and no
  rvfi_valid item lies between it and the first rvfi_ext_debug_mode=1 item, which carries
  rvfi_ext_debug_req == 1; the arc is identified from the driver timestamp inside the
  instruction's ID window, its record and the DmHaltAddr fetch; instr_addr_o == DmHaltAddr; core_busy_o
  stays high throughout (wfi variant); csrr read-back on rvfi_rd_wdata of dpc (wfi+4 / mepc /
  csrw+4), dcsr (cause 3, prv = old MPP for mret) and mstatus (MIE restored for mret).
- Config: dcsr.step=0; mstatus.MPP/MPIE and mepc (mret variant); the flushing CSR (mstatus, mie,
  mtvec, cpuctrlsts, pmpcfg*; rtl/ibex_id_stage.sv:595-597); mstatus.TW=0 for a U-mode wfi.
- Source: spec Sdext.adoc "Halt" (halt completes the current instruction), "Wait for Interrupt
  Instruction" | RTL-defined rtl/ibex_controller.sv:287-293 (special_req), 474-475, 664-677
  (DECODE -> FLUSH), 953-967 (FLUSH special arm), 985-987 (priority override), 598-604 (WAIT_SLEEP
  not reached); rtl/ibex_cs_registers.sv:953-963 (mret restore), 891-917 (dpc from pc_if)
- Edge: yes, of F-DBG-001
- Status: ACTIVE
- Notes: Added for Critic C-09 item 1 (hierarchy map H-C1 / FSM-1 arc C20, CTRL-24). The step
  variants are F-DBG-044 (wfi) and F-DBG-045 (mret); the exception variant is F-DBG-004. The
  hierarchy map lists dret among the C20 sources; per the RTL the dret case takes the DECODE arc.

---------------------------------------------------------------------------------------------------

## TRG: hardware triggers (Sdtrig, mcontrol type 2, execute-address-before only)

### F-TRG-001: One trigger implemented; tselect is WARL and reads 0
- What: DbgHwBreakNum=1: tselect holds 1 bit. Writes of any value >= 1 store MaxTselect = 0; writes
  of 0 store 0. Read always returns 0 (upper 31 bits zero).
- Observable at: csrr read-back of tselect on rvfi_rd_wdata after writing 0, 1, 0xFFFFFFFF.
- Config: debug mode (writes), M-mode or debug mode (reads).
- Source: spec Sdtrig.adoc "Enumeration" (read back tselect) | doc cs_registers.rst "Trigger Select
  Register (tselect)" | RTL-defined rtl/ibex_cs_registers.sv:1754-1756, 1785-1786, 1835-1837
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D18: cs_registers.rst:348 says "configured by the DbgHwNumLen parameter"; the
  parameter is DbgHwBreakNum (DbgHwNumLen is an internal localparam, rtl/ibex_cs_registers.sv:1755).

### F-TRG-002: tselect writes from M-mode (not debug mode) are silently ignored
- What: Folded into F-TRG-001: with one trigger tselect always reads 0, so an M-mode write that is
  dropped is indistinguishable from the parent's WARL store of 0 (same no-trap / read-0 observable)
  (v2 edge rule, second pass; Critic M-9); carried by the parent's mode x result bins.
- Source: spec Sdtrig.adoc intro ("M-Mode and Debug Mode accesses to trigger CSRs ... must succeed")
  | RTL-defined rtl/ibex_cs_registers.sv:1775
- Edge: yes, of F-TRG-001
- Status: FOLDED into F-TRG-001 (bin CG-TRG-001.cr_csr_mode_result.tsel_m_drop, CG-TRG-001.cr_tselw_mode.one_m, ones_m)

### F-TRG-003: tdata1 (mcontrol) read value: fixed fields plus writable execute bit; reset 0x2800_1048
- What: tdata1 reads {type=2, dmode=1, maskmax=0, hit=0, select=0, timing=0, sizelo=0, action=1,
  chain=0, match=0, m=1, bit5=0, s=0, u=1, execute=tmatch_control_q, store=0, load=0}. With
  execute=0 the value is 0x2800_1048; with execute=1 it is 0x2800_104C. Bit 20 (hit) reads 0 also
  after a match (former F-TRG-028, now a bin of CG-TRG-001).
- Observable at: csrr read-back of tdata1 on rvfi_rd_wdata.
- Config: M-mode or debug mode for read.
- Source: spec Sdtrig.adoc "Actions" (action=1 requires dmode=1), "Trigger Module Registers" (WARL)
  | doc cs_registers.rst "Trigger Data Register 1 (tdata1)" | RTL-defined
  rtl/ibex_cs_registers.sv:1847-1864
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D4: cs_registers.rst states reset value 0x2800_1000, but m=1 (bit 6) and u=1
  (bit 3) are hardwired 1 in RTL, giving 0x2800_1048.

### F-TRG-004: tdata1 write in debug mode captures only bit 2 (execute); all other bits are WARL-ignored
- What: Writing 0xFFFF_FFFF stores execute=1 and reads back 0x2800_104C; writing 0 stores execute=0
  and reads back 0x2800_1048 (non-zero, as Sdtrig requires for a disabled trigger). Writing with
  type != 2, action != 1, dmode = 0, load/store = 1, match != 0 does not change those fields. The
  captured bit is the POST-OP value after the set/clear merge with the current tdata1 read value
  (csrrs: old_exec | wdata[2]; csrrc: old_exec & ~wdata[2]; rtl/ibex_cs_registers.sv:1004-1005,
  :1788; fact-check TP-TRG-004): a csrrc with all-ones CLEARS execute; readback = 32'h2800_1048 |
  (post_op[2] << 2).
- Observable at: csrr read-back of tdata1 on rvfi_rd_wdata.
- Config: debug mode; tselect=0.
- Source: spec Sdtrig.adoc "Trigger Module Registers" ("Write 0 to tdata1 ... will result in tdata1
  containing a non-zero value, since the register is WARL") | RTL-defined
  rtl/ibex_cs_registers.sv:1777-1778, 1789
- Edge: no
- Status: ACTIVE

### F-TRG-005: tdata1 / tdata2 writes from M-mode (dmode=1) are ignored without exception
- What: tmatch_control_we / tmatch_value_we require debug_mode_i. M-mode csrw/csrs/csrc to tdata1 or
  tdata2 complete normally and leave the trigger configuration unchanged; the read part of csrrw
  returns the current value.
- Observable at: no rvfi_trap; csrr read-back of tdata1/tdata2 on rvfi_rd_wdata unchanged.
- Config: M-mode, debug_mode=0.
- Source: spec Sdtrig.adoc "Actions" (dmode=1 semantics), intro (M-mode accesses must succeed) |
  doc cs_registers.rst tdata1/tdata2 ("writes to this register from M-Mode will be ignored") |
  RTL-defined rtl/ibex_cs_registers.sv:1776-1781
- Edge: no
- Status: ACTIVE

### F-TRG-006: Trigger CSR access from U-mode raises illegal instruction
- What: tselect/tdata1/tdata2/tdata3/mcontext/mscontext (0x7A0-0x7AA) and scontext (0x5A8) have
  address bits [9:8] > U, so any U-mode access traps (code 2) regardless of debug/trigger state.
- Observable at: rvfi_trap; csrr read-back of mcause == 2 on rvfi_rd_wdata.
- Config: U-mode.
- Source: spec machine.adoc CSR address privilege convention (implicit in Sdtrig "M-Mode and Debug
  Mode accesses") | RTL-defined rtl/ibex_cs_registers.sv:403-406
- Edge: no
- Status: ACTIVE

### F-TRG-007: tdata2 is a full 32-bit read/write address register (debug-mode writes only)
- What: Any 32-bit value written in debug mode reads back exactly (no masking, no alignment
  forcing). Reset value 0. A trigger with execute=1 and tdata2 = 0 would match a fetch of address 0.
- Observable at: csrr read-back of tdata2 on rvfi_rd_wdata for 0, all-ones, odd values, 0x8000_0000.
- Config: debug mode; tselect=0.
- Source: spec Sdtrig.adoc "Address Matches" (tdata2 must read back all valid addresses) | doc
  cs_registers.rst "Trigger Data Register 2 (tdata2)" | RTL-defined rtl/ibex_cs_registers.sv:
  1779-1780, 1790, 1866-1867
- Edge: no
- Status: ACTIVE
- Notes: Canonical for F-CSR-082.

### F-TRG-008: tdata3, mcontext, scontext, mscontext read zero; writes are ignored; accessible in M/debug
- What: 0x7A3, 0x7A8, 0x5A8, 0x7AA return 0 and accept writes without effect or exception in M-mode
  and debug mode.
- Observable at: csrr read-back on rvfi_rd_wdata == 0; no rvfi_trap on write.
- Config: M-mode or debug mode.
- Source: spec Sdtrig.adoc intro ("Accessing trigger CSRs that are not used by any of the
  implemented triggers must result in an illegal instruction exception") | doc cs_registers.rst
  "Trigger Data Register 3 (tdata3)", "Machine Context Register (mcontext)", "Supervisor Context
  Register (scontext)" | RTL-defined rtl/ibex_cs_registers.sv:648-663
- Edge: no
- Status: ACTIVE
- Notes: Bug candidate B3: Sdtrig says unused trigger CSRs must trap; Ibex returns 0
  (doc-conformant, spec-deviant; checker follows Sdtrig, TP-TRG-008 expected-fail). scontext is
  decoded at 0x5A8 (rtl/ibex_pkg.sv:511) although S-mode does not exist; access from M works. Doc
  defect D18: cs_registers.rst:445-448 heads the scontext section with CSR address 0x7AA (that is
  mscontext). Owner question Q6.

### F-TRG-009: tinfo (0x7A4) and tcontrol (0x7A5) are not implemented: illegal instruction
- What: Not in the CSR decode; any access from any mode traps (code 2). The Sdtrig enumeration
  algorithm therefore falls back to reading tdata1.type (=2).
- Observable at: rvfi_trap; csrr read-back of mcause == 2 on rvfi_rd_wdata.
- Config: none.
- Source: spec Sdtrig.adoc "Enumeration" step 4, "Trigger Module Registers" ("Attempts to access an
  unimplemented Trigger Module Register raise an illegal instruction exception") | RTL-defined
  rtl/ibex_cs_registers.sv:702-704 (default illegal)
- Edge: no
- Status: ACTIVE

### F-TRG-010: Trigger fires on instruction-address match before execution: debug entry cause 2, dpc = matched PC
- What: With execute=1, when the IF-stage address (pc_if) equals tdata2 and the core is not in debug
  mode, the controller waits for ID/WB to drain, then enters DBG_TAKEN_IF: PC := DmHaltAddr, dpc :=
  matched address, dcsr.cause := 2, dcsr.prv := current privilege. The matched instruction does not
  execute (no retirement, no side effects). The match has no privilege term (m=1, u=1 hardwired), so
  it fires from M and U with dcsr.prv recording the mode; execute=0 disables it; a dummy instruction
  presented with the matching PC fires like a real one; the standard arming sequence followed by
  dret elsewhere fires when PC reaches tdata2 by any path (former F-TRG-011/012/026/030, now bins of
  CG-TRG-002).
- Observable at: no rvfi_valid item for the matched PC before rvfi_ext_debug_mode=1; csrr read-back
  on rvfi_rd_wdata of dpc (== tdata2) and dcsr (cause 2, prv = mode at the match); instr_addr_o ==
  DmHaltAddr.
- Config: tdata1.execute=1, tdata2 = target PC (written in debug mode).
- Source: spec Sdtrig.adoc "Actions" (action 1: dpc = next instruction to preserve program flow),
  "Priority" ("mcontrol execute address before") | doc cs_registers.rst tdata1 (timing=0 "Break
  before the instruction") | RTL-defined rtl/ibex_cs_registers.sv:1869-1874;
  rtl/ibex_controller.sv:476-477, 704-711, 764-783, 519
- Edge: no
- Status: ACTIVE
- Notes: Canonical for the EXC alias F-EXC-021 (M-10 pass); F-EXC-022 aliases F-TRG-021.

### F-TRG-011: No match when tdata1.execute=0
- What: The parent's Config variable (execute) at its disabled value: tmatch_control_q=0 forces
  trigger_match=0 (rtl/ibex_cs_registers.sv:1872); carried by the parent's exec bin.
- Source: RTL-defined rtl/ibex_cs_registers.sv:1872
- Edge: yes, of F-TRG-010
- Status: FOLDED into F-TRG-010 (bin CG-TRG-002.cr_exec_fired.off_nf)

### F-TRG-012: Trigger fires in both M-mode and U-mode (m=1, u=1 hardwired; no per-mode gating)
- What: The parent with the privilege at its other value (trigger_match has no privilege term,
  rtl/ibex_cs_registers.sv:1858, 1861, 1872; a U-mode hit records dcsr.prv=0); carried by the
  parent's privilege bins. The "tdata1.m=0" scenario cannot be programmed (m is read-only 1).
- Source: doc cs_registers.rst tdata1 (m=1, u=1 read-only) | RTL-defined
  rtl/ibex_cs_registers.sv:1858, 1861, 1872
- Edge: yes, of F-TRG-010
- Status: FOLDED into F-TRG-010 (bin CG-TRG-002.cr_priv_fired.u_f; CG-DBG-001.cr_cause_prv.trigger_u)

### F-TRG-013: Triggers do not fire in debug mode
- What: Folded into F-TRG-010: "not in debug mode" is a term of the parent's own match condition
  (trigger_match_i & ~debug_mode_q, rtl/ibex_controller.sv:476-477), so the debug-mode non-fire is
  the parent's condition evaluated false with the parent's not-fired observable (Critic M-9);
  carried by the parent's context bins.
- Source: spec Sdtrig.adoc intro ("Triggers do not fire while in Debug Mode"); Sdext.adoc "Debug
  Mode" item 5 | RTL-defined rtl/ibex_controller.sv:476-477
- Edge: yes, of F-TRG-010
- Status: FOLDED into F-TRG-010 (bin CG-TRG-002.cp_ctx.in_debug, CG-TRG-002.cr_ctx_fired.indebug_nf)

### F-TRG-014: Trigger on a compressed instruction (tdata2 with bit 1 set)
- What: Folded into F-TRG-010: a halfword-aligned tdata2 is one value of the parent's 32-bit pc_if
  compare with the parent's outcome (dpc = tdata2, DmHaltAddr) (v2 edge rule, second pass; Critic
  M-9); carried by the parent's context bins.
- Source: spec Sdtrig.adoc "Address Matches" | RTL-defined rtl/ibex_cs_registers.sv:1872
- Edge: yes, of F-TRG-010
- Status: FOLDED into F-TRG-010 (bin CG-TRG-002.cp_ctx.comp2, CG-TRG-002.cr_ctx_fired.comp2_f)

### F-TRG-015: tdata2 with bit 0 set never matches (all PCs are 2-byte aligned)
- What: pc_if[0] is always 0, so tdata2[0]=1 disables matching without any read-back change.
- Observable at: rvfi_valid item with rvfi_pc_rdata == tdata2 & ~1 retires and no DmHaltAddr fetch
  appears on instr_addr_o; csrr read-back of tdata2 on rvfi_rd_wdata keeps bit 0.
- Config: tdata2 odd.
- Source: spec Sdtrig.adoc "Address Matches / Invalid Addresses" (implementation may inhibit
  matching against invalid addresses) | RTL-defined rtl/ibex_cs_registers.sv:1872;
  rtl/ibex_icache.sv:1193 (addr_o bit 0 = 0)
- Edge: yes, of F-TRG-010
- Status: ACTIVE

### F-TRG-016: Trigger set on the dret target (dpc): immediate re-entry, cause 2, dpc unchanged
- What: The trigger half of F-DBG-066 (after dret pc_if == dpc == tdata2 with ID empty: DBG_TAKEN_IF
  at once, zero retirements, dcsr.cause := 2); carried by that entry's bins. Base feature F-DBG-031
  (the former target F-DBG-066 is an edge or alias of it).
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" | RTL-defined
  rtl/ibex_controller.sv:476-477, 704-711
- Edge: yes, of F-DBG-031
- Status: FOLDED into F-DBG-031 (bin CG-DBG-005.cr_prv_next.m_rehalt_trig, u_rehalt_trig; CG-TRG-002.cr_ctx_fired.dret_f)

### F-TRG-017: Trigger set on the trap-handler entry address (mtvec target)
- What: When an exception or interrupt vectors to tdata2, the trigger fires before the first handler
  instruction: mepc/mcause/mtval/mstatus are already updated, dpc := handler address, dcsr.cause :=
  2, dcsr.prv := M.
- Observable at: the rvfi_trap record (exception variant) or the rvfi_ext_irq_valid level (interrupt
  / NMI variants: rvfi_intr is a per-record field and no handler record exists; C-13), then
  instr_addr_o sequence vector -> DmHaltAddr with no rvfi_valid item at the vector; csrr read-back on rvfi_rd_wdata of dpc (== vector) and
  dcsr.cause (2).
- Config: tdata2 = mtvec base (exceptions) or mtvec base + 4*cause (interrupts); tdata1.execute=1.
- Source: spec Sdtrig.adoc "Native Triggers" (etrigger/itrigger discussion; for mcontrol the handler
  address is simply the next executed address) | RTL-defined rtl/ibex_controller.sv:476-477,
  704-711
- Edge: yes, of F-TRG-010
- Status: ACTIVE

### F-TRG-018: Trigger and single step on the same instruction: cause 2 reported, instruction not executed
- What: With dcsr.step=1 and tdata2 = the first instruction after dret, debug_cause_d selects
  TRIGGER; the instruction does not execute (trigger is "before").
- Observable at: csrr read-back on rvfi_rd_wdata of dcsr.cause (2) and dpc (== tdata2); zero
  rvfi_valid items with rvfi_ext_debug_mode=0 between the two debug windows.
- Config: dcsr.step=1; tdata1.execute=1; tdata2 = dpc.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" ("dcsr.cause is set to 2 (trigger)
  instead of 4 (single step)") | RTL-defined rtl/ibex_controller.sv:519-523
- Edge: yes, of F-TRG-010
- Status: ACTIVE

### F-TRG-019: Trigger match and debug_req_i in the same cycle: cause 2 recorded
- What: debug_cause_d prioritises trigger_match_i over debug_req_i; entry timing is identical; dpc
  is the matched address in both interpretations.
- Observable at: csrr read-back on rvfi_rd_wdata of dcsr.cause (2) and dpc (== tdata2); instr_addr_o
  == DmHaltAddr.
- Config: tdata1.execute=1; debug_req_i high when pc_if == tdata2.
- Source: RTL-defined rtl/ibex_controller.sv:519-523
- Edge: yes, of F-TRG-010
- Status: ACTIVE
- Notes: Spec does not rank haltreq vs. trigger; either cause is defensible. Reference model must
  match RTL.

### F-TRG-020: ebreak entering debug mode while the following instruction's address matches tdata2: cause misreported as 2 (bug candidate)
- What: In the FLUSH cycle of an ebreak-into-debug, pc_if holds the next sequential address. If it
  equals tdata2 (execute=1), debug_cause_d = TRIGGER and DBG_TAKEN_ID writes dcsr.cause := 2 while
  dpc := ebreak PC. The trigger's instruction was never about to execute.
- Observable at: csrr read-back on rvfi_rd_wdata of dcsr.cause == 2 with dpc == ebreak PC (an
  inconsistent pair: trigger entries have dpc == tdata2).
- Config: dcsr.ebreakm=1 (or ebreaku=1); tdata2 = ebreak PC + 2 or + 4.
- Source: spec Sdext.adoc "Single Step / Step Bit In Dcsr" (trigger fires only when the instruction
  is attempted); Sdtrig.adoc "Priority" | RTL-defined rtl/ibex_controller.sv:519-523, 785-814
- Edge: yes, of F-TRG-010
- Status: ACTIVE
- Notes: Bug candidate B10 (RTL/spec disagreement; needs repro). Owner question Q7.

### F-TRG-021: Trigger address on the fall-through of a taken branch does not fire
- What: While a taken branch is in ID, pc_if may equal tdata2 (fall-through) and trigger_match_i=1,
  but entry is deferred (ID busy); after the branch sets the PC, pc_if changes to the target and the
  match disappears. No debug entry occurs. For a NOT-taken branch the fall-through is executed and
  the trigger fires (dpc == branch PC + size). The same holds with cpuctrlsts.data_ind_timing=1
  (former F-TRG-022, now a bin of CG-TRG-002).
- Observable at: rvfi_valid item at the branch target retires and no DmHaltAddr fetch appears on
  instr_addr_o; for the not-taken case csrr read-back of dpc == branch PC + size on rvfi_rd_wdata.
- Config: tdata2 = branch PC + 4 (or +2); branch taken.
- Source: RTL-defined rtl/ibex_controller.sv:468-472 (comment: trigger is not a priority entry so it
  can be ignored when control flow changes), 704-711
- Edge: yes, of F-TRG-010
- Status: ACTIVE

### F-TRG-022: Trigger address on the fall-through of a taken branch with data_ind_timing=1
- What: F-TRG-021 with the Config variable cpuctrlsts.data_ind_timing at 1 (two-cycle branches,
  branch_set forced, rtl/ibex_id_stage.sv:790-791, 831, 928): same outcome, fires only when the
  branch is not taken; carried by F-TRG-021's DIT bins. Base feature F-TRG-010 (the former target
  F-TRG-021 is an edge or alias of it).
- Source: RTL-defined rtl/ibex_id_stage.sv:790-791, 831, 928; rtl/ibex_controller.sv:704-711
- Edge: yes, of F-TRG-010
- Status: FOLDED into F-TRG-010 (bin CG-TRG-002.cr_dit_fall.dit1_falltaken_nf, dit1_fallnt_f)

### F-TRG-023: Trigger on a Zcmp instruction address fires before the first micro-op; cannot fire mid-sequence
- What: The whole cm.* sequence shares one PC; a match on it fires before any micro-op. Once the
  sequence has started, enter_debug_mode is masked until the last micro-op, so a trigger cannot
  split it. A trigger on the instruction after the sequence fires after all micro-ops complete.
- Observable at: no data_req_o for the pushes/pops when the trigger hits the cm.* address; all
  accesses present when the trigger is on the successor.
- Config: tdata2 = cm.push PC, or = successor PC.
- Source: spec Sdtrig.adoc "Multiple State Change Instructions", "Combined Accesses" | RTL-defined
  rtl/ibex_controller.sv:473-477
- Edge: yes, of F-TRG-010
- Status: ACTIVE

### F-TRG-024: Trigger match on an address whose fetch faults: trigger wins over instruction access fault
- What: The match is on pc_if before the instruction enters ID; the fetch error attached to the IF
  instruction is discarded by the debug flush. dpc := address, no mcause/mtval update.
- Observable at: csrr read-back on rvfi_rd_wdata of dcsr.cause (2) and mcause (unchanged); no
  rvfi_trap; instr_addr_o == DmHaltAddr.
- Config: tdata2 = address in a PMP-denied region (or TB instr_err_i on that address).
- Source: spec machine.adoc "Synchronous exception priority" (Instruction address breakpoint is
  highest); Sdtrig.adoc "Priority" | RTL-defined rtl/ibex_controller.sv:704-711, 764-783
- Edge: yes, of F-TRG-010
- Status: ACTIVE

### F-TRG-025: Trigger match and enabled interrupt pending simultaneously: debug entry wins
- What: The trigger instance of F-DBG-002 (DECODE evaluates enter_debug_mode, which includes
  trigger_match_i, before handle_irq; rtl/ibex_controller.sv:704-722); carried by that entry's bins.
  Base feature F-DBG-001 (the former target F-DBG-002 is an edge or alias of it).
- Source: RTL-defined rtl/ibex_controller.sv:476-477, 704-722
- Edge: yes, of F-DBG-001
- Status: FOLDED into F-DBG-001 (bin CG-TRG-002.cr_coinc_cause.irq_trig, nmi_trig; CG-DBG-009.cr_window_disp.entry_wins)

### F-TRG-026: Trigger match while the IF instruction is a SecureIbex dummy instruction
- What: A dummy instruction is presented with the PC of the next real instruction
  (rtl/ibex_if_stage.sv:532-535); a match on it is indistinguishable at the boundary from a normal
  hit (dpc == tdata2, the real instruction executes after dret); carried by the parent's ctx bin.
- Source: RTL-defined rtl/ibex_if_stage.sv:526-535; rtl/ibex_cs_registers.sv:1872
- Edge: yes, of F-TRG-010
- Status: FOLDED into F-TRG-010 (bin CG-TRG-002.cr_ctx_fired.dummy_f)

### F-TRG-027: Trigger match while the IF fetch has not yet returned (bus stall)
- What: pc_if is the registered fetch address (icache output_addr) and is valid before
  instr_rvalid_i; the match, and therefore debug entry with dpc := tdata2, can complete before the
  instruction data arrives. The outstanding fetch is discarded.
- Observable at: instr_addr_o == DmHaltAddr issued while the tdata2 fetch is still pending on
  instr_gnt_i/instr_rvalid_i; csrr read-back of dpc == tdata2 on rvfi_rd_wdata.
- Config: TB instruction-memory latency; tdata1.execute=1.
- Source: RTL-defined rtl/ibex_icache.sv:1193; rtl/ibex_if_stage.sv:420; rtl/ibex_cs_registers.sv:
  1872
- Edge: yes, of F-TRG-010
- Status: ACTIVE

### F-TRG-028: tdata1.hit stays 0 after a trigger fires (hit not supported)
- What: Restates the fixed hit=0 field of F-TRG-003 (rtl/ibex_cs_registers.sv:1851) read after a
  cause-2 entry; carried by the parent's post-hit readback bin.
- Source: doc cs_registers.rst tdata1 (hit: 0 not supported) | RTL-defined
  rtl/ibex_cs_registers.sv:1851
- Edge: yes, of F-TRG-003
- Status: FOLDED into F-TRG-003 (bin CG-TRG-001.cp_td1_rb.en_after_hit)

### F-TRG-029: Trigger CSR reads succeed in M-mode outside debug mode
- What: csrr tselect/tdata1/tdata2/tdata3/mcontext/mscontext/scontext in M-mode return the current
  values without exception (DbgTriggerEn=1).
- Observable at: rvfi_rd_wdata; no rvfi_trap.
- Config: M-mode.
- Source: spec Sdtrig.adoc intro ("M-Mode and Debug Mode accesses ... must succeed");
  tools/specs/riscv-isa-manual/src/priv/csrs.adoc:60-63 (0x7A0-0x7AF machine-mode accessible) | doc
  cs_registers.rst tselect ("Accessible in Debug Mode or M-Mode") | RTL-defined
  rtl/ibex_cs_registers.sv:636-663
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D12: debug.rst:54-55 claims these registers trap outside debug mode (see
  F-DBG-050).

### F-TRG-030: Writing tdata2 then enabling execute inside the same debug session, then dret to a different address
- What: The parent's normal arming flow (tdata1 := 0, tdata2 := addr, execute := 1, dret elsewhere,
  cause-2 entry when PC reaches addr by any path incl. a jalr target); carried by the parent's ctx
  bins.
- Source: spec Sdtrig.adoc "Trigger Module Registers" | RTL-defined
  rtl/ibex_cs_registers.sv:1775-1790, 1872
- Edge: yes, of F-TRG-010
- Status: FOLDED into F-TRG-010 (bin CG-TRG-002.cr_ctx_fired.jalr_f, seq32_f, br_f)

---------------------------------------------------------------------------------------------------

## PMC: performance counters (Zicntr / Zihpm as implemented)

### F-PMC-001: mcycle / mcycleh is a 64-bit cycle counter, reset 0, increments every clock
- What: mcycle increments by 1 every clk_i cycle in which mcountinhibit.CY=0, from reset value 0,
  through sleep (WFI) because ibex_core has no clock gate, and through debug mode. mcycleh is the
  upper half of the same 64-bit register. Counting through WFI sleep and debug mode (former
  F-PMC-002) is a bin of CG-PMC-001.
- Observable at: csrr read-back of mcycle/mcycleh on rvfi_rd_wdata; rvfi_ext_mcycle on every
  retirement.
- Config: mcountinhibit.CY.
- Source: spec machine.adoc "Hardware Performance Monitor" (64-bit precision), zicntr.adoc "Zicntr
  Extension for Base Counters and Timers" | doc doc/03_reference/performance_counters.rst
  ("mcycle(h) and minstret(h) are always available and 64 bit wide") | RTL-defined
  rtl/ibex_cs_registers.sv:1586, 1622-1633; rtl/ibex_counter.sv:30, 44-50
- Edge: no
- Status: ACTIVE
- Notes: In ibex_top the core clock is gated during sleep, so mcycle would pause; with the ibex_core
  DUT it keeps counting. Model must follow the DUT. Canonical for F-CSR-062.

### F-PMC-002: mcycle keeps counting in WFI sleep (ibex_core DUT) and in debug mode
- What: Restates the parent's "through sleep (WFI) ... and through debug mode" (counter_inc_i for
  mcycle is 1 & ~mcountinhibit[0], rtl/ibex_cs_registers.sv:1627); carried by the parent's window
  bins.
- Source: spec zicntr.adoc NOTE on sleep; Sdext.adoc "Debug Mode" item 6 | RTL-defined
  rtl/ibex_cs_registers.sv:1627
- Edge: yes, of F-PMC-001
- Status: FOLDED into F-PMC-001 (bin CG-PMC-001.cr_ctx_delta.wfi_eq, debug_eq)

### F-PMC-003: mcycle low-word wrap carries into mcycleh
- What: Folded into F-PMC-001: the low-word carry into mcycleh is the parent's "64-bit register"
  statement at the 0xFFFF_FFFF boundary with the parent's read-back observable (v2 edge rule, second
  pass; Critic M-9); carried by the parent's carry bins.
- Source: spec zicntr.adoc sample code for 64-bit read | RTL-defined rtl/ibex_counter.sv:30
  (CounterWidth=64 add), 99-100
- Edge: yes, of F-PMC-001
- Status: FOLDED into F-PMC-001 (bin CG-PMC-001.cp_carry.seen, CG-PMC-001.cr_carry_ctx.carry_run)

### F-PMC-004: mcycle write while counting: the write wins and the increment for that cycle is lost
- What: ibex_counter gives we priority over counter_inc_i; the cycle in which the CSR write lands
  does not increment. The read part of csrrw returns the pre-write value (including that cycle's
  count).
- Observable at: csrr read-back on rvfi_rd_wdata: the csrrw's own rvfi_rd_wdata is the pre-write
  value; a csrr mcycle N cycles after the write returns written + (N - 1), one less than a model
  that also counts the write cycle; rvfi_ext_mcycle on the retirements after the write.
- Config: mcountinhibit.CY=0.
- Source: spec machine.adoc "Hardware Performance Monitor" ("Any CSR write takes effect after the
  writing instruction has otherwise completed") | RTL-defined rtl/ibex_counter.sv:44-50
- Edge: yes, of F-PMC-001
- Status: ACTIVE
- Notes: Canonical for F-CSR-063.

### F-PMC-005: mcycleh write in the cycle the low word is 0xFFFF_FFFF: no increment that cycle, carry next cycle
- What: counterh write loads {wdata, old_low}; the increment is suppressed for that cycle; on the
  next counting cycle the low word wraps and the newly written high word is incremented (wdata+1).
- Observable at: csrr read-back of mcycleh on rvfi_rd_wdata shortly after the write == wdata+1;
  rvfi_ext_mcycle[63:32] on the next retirements.
- Config: mcycle preloaded to 0xFFFF_FFFF - k with k tuned so the write lands at all-ones.
- Source: RTL-defined rtl/ibex_counter.sv:36-50
- Edge: yes, of F-PMC-001
- Status: ACTIVE
- Notes: Canonical for F-CSR-064.

### F-PMC-006: mcycle / mcycleh CSR write semantics: low write leaves high untouched and vice versa; csrrs/csrrc are RMW
- What: counter_we loads bits [31:0] only; counterh_we loads bits [63:32] only. For CSR_OP_SET/CLEAR
  the write data is wdata | rdata or ~wdata & rdata where rdata is the current counter half.
- Observable at: csrr read-back on rvfi_rd_wdata after independent writes to mcycle and mcycleh;
  csrs mcycle, x0 does not write (read-only op).
- Config: none.
- Source: spec machine.adoc "Hardware Performance Monitor" (writes change only bits 31-0 / 63-32) |
  RTL-defined rtl/ibex_counter.sv:33-41; rtl/ibex_cs_registers.sv:1002-1011 (csr_wdata_int,
  csr_wr), 1020-1023 (csr_we_int)
- Edge: yes, of F-PMC-001
- Status: ACTIVE

### F-PMC-007: minstret / minstreth is a 64-bit retired-instruction counter, reset 0
- What: Increments once per instruction that retires from WB (instr_done_wb & wb_count_q & no LSU
  error). Excluded: instructions that trap (ecall, ebreak incl. ebreak-into-debug, illegal
  instruction incl. illegal CSR access and dret outside debug mode, instruction fetch error,
  load/store access fault), the instruction that writes minstret/minstreth, and non-final Zcmp
  micro-ops. Included: mret, dret, wfi, csr accesses to other CSRs, nops, fence, dummy
  instructions (see F-PMC-011). The self-write exclusion, single-step windows and interrupt
  windows (former F-PMC-008/048/052) are bins of CG-PMC-002.
- Observable at: csrr read-back of minstret/minstreth on rvfi_rd_wdata equals the count of
  rvfi_valid & ~rvfi_trap items since the last write (dummy caveat F-PMC-011).
- Config: mcountinhibit.IR.
- Source: spec machine.adoc "Hardware Performance Monitor" (minstret counts retired instructions);
  tools/specs/riscv-isa-manual/src/unpriv/zicntr.adoc:172-174 ("Instructions that cause synchronous
  exceptions, including ecall and ebreak, are not considered to retire") | doc
  performance_counters.rst "Event Selector" (NumInstrRet) | RTL-defined
  rtl/ibex_id_stage.sv:1210-1220; rtl/ibex_wb_stage.sv:149-150, 206-210;
  rtl/ibex_cs_registers.sv:1588, 1637-1649
- Edge: no
- Status: ACTIVE
- Notes: Canonical for F-CSR-066. The machine.adoc "Environment Call and Breakpoint" section does
  not state the no-retire rule (Critic C-04); only zicntr.adoc does.

### F-PMC-008: The instruction that writes minstret or minstreth is itself not counted
- What: One row of the parent's exclusion list (minstret_write clears instr_perf_count_id,
  rtl/ibex_id_stage.sv:1213-1219, so csrw minstret, N; csrr minstret returns N); carried by the
  parent's window bin.
- Source: spec machine.adoc "Hardware Performance Monitor" | RTL-defined
  rtl/ibex_id_stage.sv:1213-1219
- Edge: yes, of F-PMC-007
- Status: FOLDED into F-PMC-007 (bin CG-PMC-002.cr_window_delta.selfwr_eq)

### F-PMC-009: minstret read coherence: a read in ID sees the instruction retiring in WB in the same cycle
- What: mhpmcounter[2] presented to the read mux is minstret_next when instr_ret_spec (WB holds a
  countable instruction) and IR not inhibited; so back-to-back "csrr minstret" reads differ by
  exactly 1 and a read immediately after an ALU instruction includes it.
- Observable at: csrr read-back of minstret on rvfi_rd_wdata in a straight-line sequence: each read
  returns the number of prior retirements.
- Config: mcountinhibit.IR=0 (when IR=1 the speculative +1 is not applied).
- Source: RTL-defined rtl/ibex_cs_registers.sv:1651-1658
- Edge: yes, of F-PMC-007
- Status: ACTIVE
- Notes: Canonical for the CSR alias F-CSR-068 (M-10 pass); the inhibited read is F-CSR-060.

### F-PMC-010: minstret speculative read when the WB instruction then faults
- What: If the WB load/store faults, the ID instruction (which may have read minstret including the
  +1) is flushed, so the incorrect speculative value never retires. minstret itself is not
  incremented for the faulting load/store.
- Observable at: csrr read-back of minstret on rvfi_rd_wdata in the handler excludes the faulting
  load; no rvfi_valid item for the flushed reader.
- Config: PMP or bus error on a load followed by csrr minstret.
- Source: RTL-defined rtl/ibex_cs_registers.sv:1651-1658 (comment); rtl/ibex_wb_stage.sv:208-209
- Edge: yes, of F-PMC-007
- Status: ACTIVE

### F-PMC-011: SecureIbex dummy instructions increment minstret and the div-wait counter (bug candidate); the dummy mul adds no mul-wait cycles
- What: Dummy instructions (ADD/MUL/DIV/AND with rd=x0) inserted by the IF stage pass through ID/WB
  with instr_perf_count_id=1 (no dummy exclusion), so each dummy increments minstret; a dummy DIV
  adds DIV_STALL_FULL to mhpmcounter12; the dummy MUL is `mul` (funct3 000,
  rtl/ibex_dummy_instr.sv:124-131), which the RV32MSingleCycle multiplier completes in its first
  cycle (rtl/ibex_multdiv_fast.sv:203-217), so mhpmcounter11 does not move in an ALU-only window
  (fact-check TP-PMC-013); mcycle counts their cycles. They are excluded from RVFI.
- Observable at: csrr read-back of minstret on rvfi_rd_wdata over a code window exceeds the number
  of rvfi_valid items when cpuctrlsts.dummy_instr_en=1; equal when 0.
- Config: cpuctrlsts.dummy_instr_en, dummy_instr_mask; mcountinhibit.
- Source: doc doc/03_reference/security.rst "Dummy Instruction Insertion" ("no functional impact on
  processor state") | RTL-defined rtl/ibex_id_stage.sv:1218-1220 (no dummy term);
  rtl/ibex_wb_stage.sv:149-150, 206-210; rtl/ibex_core.sv:1136, 1864 (RVFI excludes dummies);
  rtl/ibex_dummy_instr.sv:143-144
- Edge: yes, of F-PMC-007
- Status: ACTIVE
- Notes: Bug candidate B7 (RTL/doc disagreement: minstret is architectural state). Canonical for
  F-DIT-018 counting claims. Owner question Q8. Until ruled, tests
  that check exact minstret must run with dummy_instr_en=0 or tolerate the dummy count.

### F-PMC-012: Zcmp sequences count as one retired instruction (and one compressed instruction)
- What: Only the last micro-op (INSTR_EXPANDED_LAST or not expanded) has instr_perf_count_id=1; the
  earlier micro-ops are excluded from minstret and mhpmcounter10. Loads/stores of the sequence are
  each counted in mhpmcounter5/6.
- Observable at: csrr read-back on rvfi_rd_wdata: minstret +1 and mhpmcounter10 +1 per
  cm.push/cm.pop; mhpmcounter5/6 + number of registers; rvfi_ext_mhpmcounters[2]/[3]/[7].
- Config: mcountinhibit=0.
- Source: RTL-defined rtl/ibex_id_stage.sv:1218-1220; rtl/ibex_wb_stage.sv:149, 210
- Edge: yes, of F-PMC-007
- Status: ACTIVE

### F-PMC-013: minstret low-word wrap carries into minstreth
- What: Folded into F-PMC-007: the low-word carry into minstreth is the parent's "64-bit counter"
  statement at the boundary with the parent's read-back observable (v2 edge rule, second pass;
  Critic M-9); carried by the parent's wrap bins.
- Source: spec machine.adoc "Hardware Performance Monitor" | RTL-defined rtl/ibex_counter.sv:30,
  99-100; rtl/ibex_cs_registers.sv:1637-1649
- Edge: yes, of F-PMC-007
- Status: FOLDED into F-PMC-007 (bin CG-PMC-002.cp_wrap.carry, CG-PMC-002.cr_wrap_op.carry_rdhi, carry_rdlo)

### F-PMC-014: minstret write while an instruction retires in WB in the same cycle: write wins
- What: The retirement of the previous instruction (in WB when the csrw in ID commits) is not added;
  the final value is exactly the written value, which is architecturally equivalent (retire then
  overwrite).
- Observable at: csrr read-back of minstret on rvfi_rd_wdata == written value (+ later
  retirements).
- Config: none.
- Source: RTL-defined rtl/ibex_counter.sv:44-50; rtl/ibex_id_stage.sv:747-749 (csr_op_en timing)
- Edge: yes, of F-PMC-007
- Status: ACTIVE

### F-PMC-015: mhpmcounter3..12 exist as 32-bit counters; mhpmcounter3h..12h read zero and ignore writes
- What: MHPMCounterWidth=32: counter_val_o[63:32] is 0; counterh writes are dropped
  (unused_counter_load). Low-word writes load the 32-bit register.
- Observable at: csrr read-back of mhpmcounterNh on rvfi_rd_wdata == 0 after writing 0xFFFF_FFFF to
  it; no rvfi_trap on the write; rvfi_ext_mhpmcountersh all zero.
- Config: none.
- Source: spec zihpm.adoc "Zihpm Extension for Hardware Performance Counters" (implemented width is
  platform-specific); machine.adoc "Hardware Performance Monitor" (mhpmcounters are WARL, up to 64
  bits) | doc performance_counters.rst "Parametrization at synthesis time" | RTL-defined
  rtl/ibex_counter.sv:86-98; rtl/ibex_cs_registers.sv:1667-1697
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D16: performance_counters.rst:85-90 describes parameters WidthMHPMCounters and
  NumMHPMCounters (1..8, mhpmcounter3..10); the RTL parameters are MHPMCounterWidth and
  MHPMCounterNum (rtl/ibex_cs_registers.sv:21-22; opentitan: 10 counters, mhpmcounter3..12).
  Canonical for the CSR alias F-CSR-069 (M-10 pass); F-CSR-071 (13..31 read 0) and F-CSR-073 (h
  write no-op, increment lost) are edges of this entry. Fact-check X-17: an h-half write still
  asserts `we`, which reloads the unchanged low word and suppresses that cycle's increment
  (rtl/ibex_counter.sv:35-49); observable only for counter 10, the one HPM counter whose event can
  coincide with its own write (X-18, F-PMC-045).

### F-PMC-016: mhpmcounter3..12 wrap at 2^32 to 0 without carrying into the h half
- What: 32-bit add; 0xFFFF_FFFF + event -> 0x0000_0000; h half stays 0.
- Observable at: after csrw mhpmcounterN, 0xFFFF_FFFF and one event, csrr read-back on rvfi_rd_wdata
  of mhpmcounterN == 0 and mhpmcounterNh == 0; rvfi_ext_mhpmcounters[N-3] wraps to 0.
- Config: mcountinhibit bit N = 0.
- Source: RTL-defined rtl/ibex_counter.sv:30, 86-90
- Edge: yes, of F-PMC-015
- Status: ACTIVE
- Notes: Canonical for the CSR alias F-CSR-070 (M-10 pass).

### F-PMC-017: mhpmcounter13..31 and mhpmcounter13h..31h read zero; writes ignored; no exception (M-mode)
- What: gen_unimp ties the counter to 0; write enables are unused. Access from M-mode is legal.
- Observable at: csrr read-back on rvfi_rd_wdata == 0 after a write; no rvfi_trap.
- Config: M-mode.
- Source: spec machine.adoc "Hardware Performance Monitor" ("a legal implementation is to make both
  the counter and its corresponding event selector be read-only 0") | doc performance_counters.rst
  ("Unavailable counters always read 0") | RTL-defined rtl/ibex_cs_registers.sv:1699-1700,
  1709-1718
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D16 (parameter text, see F-PMC-015).

### F-PMC-018: mhpmevent3..12 are hardwired one-hot selectors, 1 << (N - MHPMCOUNTER_BASE) for counter N, and read-only (doc says 1 << N: D20)
- What: mhpmeventN reads 32'd1 << (N - MHPMCOUNTER_BASE) for N=3..12 (mhpmevent3 = 0x1, mhpmevent4 =
  0x2, ..., mhpmevent12 = 0x200): `mhpmevent[i][i - MHPMCOUNTER_BASE] = 1` with MHPMCOUNTER_BASE = 3
  (rtl/ibex_cs_registers.sv:185, :1602-1619; fact-check X-3). performance_counters.rst:133-147 says
  0x8 .. 0x400: doc mismatch D20 (the RTL is spec-legal, the encoding is platform-defined; the
  checker follows the RTL). The counter-to-event map is fixed and nothing programs a selector
  (X-4). There is no write case:
  csrw/csrs/ csrc to 0x323-0x32C complete without exception and without effect.
- Observable at: csrr read-back on rvfi_rd_wdata == 1 << (N - 3); no rvfi_trap on write.
- Config: M-mode.
- Source: spec machine.adoc "Hardware Performance Monitor" (mhpmevent WARL) | doc
  performance_counters.rst "Parametrization at synthesis time" (event selector table) | RTL-defined
  rtl/ibex_cs_registers.sv:569-578, 1602-1619, 771-887 (no mhpmevent write case)
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D20 (performance_counters.rst:133-147 lists 1 << N); TP-PMC-020 is `pass (doc
  mismatch D20)`.

### F-PMC-019: mhpmevent13..31 read zero; writes ignored
- What: gen_mhpmevent_inactive zeroes selectors above MHPMCOUNTER_BASE+MHPMCounterNum.
- Observable at: csrr read-back on rvfi_rd_wdata == 0; no rvfi_trap on read or write.
- Config: M-mode.
- Source: spec machine.adoc "Hardware Performance Monitor" (event 0 = no event) | doc
  performance_counters.rst ("The remaining event selector CSRs are tied to 0") | RTL-defined
  rtl/ibex_cs_registers.sv:1614-1618
- Edge: yes, of F-PMC-018
- Status: ACTIVE
- Notes: Doc defect D16 (parameter text, see F-PMC-015).

### F-PMC-020: mcountinhibit: bits 0 (CY), 2 (IR), 3..12 (HPM3..12) writable; bit 1 read-only 0; bits 13..31 read 0
- What: 13-bit register; write data bits [12:0] captured with bit 1 forced 0; reset 0 (all counters
  counting). Bits 13..31 ignored on write, read 0.
- Observable at: csrr read-back of mcountinhibit on rvfi_rd_wdata after writing 0xFFFF_FFFF ==
  0x0000_1FFD.
- Config: M-mode.
- Source: spec machine.adoc "Machine Counter-Inhibit (mcountinhibit) Register" (WARL, cy/ir/hpm
  bits) | doc performance_counters.rst "Controlling the counters from software" | RTL-defined
  rtl/ibex_cs_registers.sv:1553-1560, 1709-1729
- Edge: no
- Status: ACTIVE
- Notes: Canonical for F-CSR-058; F-CSR-060 (inhibited speculative minstret read) is a distinct
  ACTIVE edge of this entry.

### F-PMC-021: mcountinhibit.CY / IR / HPMn stop the corresponding counter; accessibility unaffected
- What: counter_inc_i is gated with ~mcountinhibit[N]; the counter holds its value while the bit is
  1 and resumes when cleared. Reads and writes to the counter still work while inhibited. The
  inhibit takes effect the cycle after the CSR write. Accessibility is unaffected also for U-mode
  alias reads gated by mcounteren, and a value written while inhibited persists and is counted from
  once the bit clears (former F-PMC-031/023, now bins of CG-PMC-006/007).
- Observable at: csrr read-back on rvfi_rd_wdata unchanged over an inhibited window;
  rvfi_ext_mcycle / rvfi_ext_mhpmcounters constant across it; U-mode alias reads (no rvfi_trap)
  still permitted if mcounteren allows.
- Config: mcountinhibit bits.
- Source: spec machine.adoc "Machine Counter-Inhibit (mcountinhibit) Register" ("only control
  whether the counters increment; their accessibility is not affected") | RTL-defined
  rtl/ibex_cs_registers.sv:1627, 1643, 1679
- Edge: no
- Status: ACTIVE

### F-PMC-022: mcountinhibit.IR=1 also removes the speculative +1 from minstret reads
- What: Alias of F-CSR-060: PMC perspective (mcountinhibit.IR = 1 selects minstret_raw in the ID
  read mux, so the read excludes the instruction retiring in WB; same for mhpmcounter10 with HPM10),
  see canonical. Decision note (Critic M-10): the DV Lead re-activated F-CSR-060 as the carrier of
  this behaviour; this PMC statement was not in the Critic's view and is recorded as its alias.
- Edge: yes, of F-PMC-021
- Status: ALIAS of F-CSR-060

### F-PMC-023: Writing a counter while it is inhibited then un-inhibiting: counting resumes from the written value
- What: Restates the parent's "holds its value while inhibited, writes still work, resumes when
  cleared" (rtl/ibex_counter.sv:44-50; rtl/ibex_cs_registers.sv:1627); carried by the write-timing
  bins.
- Source: RTL-defined rtl/ibex_counter.sv:44-50; rtl/ibex_cs_registers.sv:1627
- Edge: yes, of F-PMC-021
- Status: FOLDED into F-PMC-021 (bin CG-PMC-007.cr_target_inh_then.hpm_inh_resume, mcycle_inh_resume, minstret_inh_resume)

### F-PMC-024: mcountinhibit, mcounteren, mhpmevent*, mhpmcounter* (0xB00-0xB9F, 0x306, 0x320-0x33F) are M-mode only
- What: Address bits [9:8] == 2'b11 make any U-mode access an illegal instruction regardless of
  mcounteren.
- Observable at: rvfi_trap; csrr read-back of mcause == 2 on rvfi_rd_wdata for a U-mode csrr mcycle.
- Config: U-mode.
- Source: spec machine.adoc "Machine Counter-Enable (mcounteren) Register" (U-mode uses the 0xC00
  shadows) | RTL-defined rtl/ibex_cs_registers.sv:403
- Edge: no
- Status: ACTIVE

### F-PMC-025: mcounteren: bits 0 (CY), 2 (IR), 3..12 (HPM3..12) writable; bit 1 (TM) read-only 0; bits 13..31 read 0; reset 0
- What: 13-bit register with bit 1 forced 0; after reset every U-mode counter alias read is illegal.
- Observable at: csrr read-back of mcounteren on rvfi_rd_wdata after writing 0xFFFF_FFFF ==
  0x0000_1FFD.
- Config: M-mode; mcounteren_writable_i == IbexMuBiOn.
- Source: spec machine.adoc "Machine Counter-Enable (mcounteren) Register" (must exist with U-mode,
  fields WARL, may be read-only zero) | doc performance_counters.rst "User-Mode Counter Access
  (mcounteren)" | RTL-defined rtl/ibex_cs_registers.sv:1563-1570, 1731-1748
- Edge: no
- Status: ACTIVE
- Notes: Canonical for F-CSR-050 and F-CSR-052.

### F-PMC-026: mcounteren writes are gated by the mcounteren_writable_i multi-bit input
- What: When mcounteren_writable_i != IbexMuBiOn, csrw/csrs/csrc to mcounteren complete without
  exception but do not change the register; reads still work.
- Observable at: csrr read-back of mcounteren on rvfi_rd_wdata unchanged; no rvfi_trap; DUT input
  mcounteren_writable_i.
- Config: mcounteren_writable_i (DUT port), M-mode.
- Source: doc performance_counters.rst "User-Mode Counter Access (mcounteren)" (MUBI lock) |
  RTL-defined rtl/ibex_cs_registers.sv:845; rtl/ibex_core.sv:186
- Edge: yes, of F-PMC-025
- Status: ACTIVE
- Notes: Invalid MuBi values (neither On nor Off) also block the write (compare is == On).

### F-PMC-027: U-mode reads of cycle/instret/hpmcounter3..12 (0xC00..) and their h halves are gated by mcounteren
- What: In U-mode, a read of 0xC00+N or 0xC80+N is legal iff mcounteren[N]=1 and returns the same
  value as the M-mode CSR (including the speculative +1 for instret/hpmcounter10); otherwise illegal
  instruction (code 2). In M-mode these addresses are always readable regardless of mcounteren.
- Observable at: rvfi_trap vs rvfi_rd_wdata; csrr read-back of mcause == 2 on rvfi_rd_wdata.
- Config: mcounteren bits; privilege.
- Source: spec machine.adoc "Machine Counter-Enable (mcounteren) Register" (illegal-instruction
  exception when bit clear; read-only shadows); zicntr.adoc, zihpm.adoc | doc
  performance_counters.rst "User-Mode Counter Access (mcounteren)" | RTL-defined
  rtl/ibex_cs_registers.sv:606-633
- Edge: no
- Status: ACTIVE

### F-PMC-028: U-mode read of hpmcounter13..31 (and h) is always illegal; M-mode read of 0xC0D..0xC1F returns 0
- What: mcounteren[13..31] are hardwired 0, so the U-mode check always fails; in M-mode the read
  returns the (zero) unimplemented counter.
- Observable at: rvfi_trap in U-mode even after csrw mcounteren, -1; rvfi_rd_wdata == 0 in M-mode.
- Config: mcounteren; privilege.
- Source: spec zihpm.adoc ("Accessing an unimplemented counter may cause an illegal-instruction
  exception or may return a constant value") | RTL-defined rtl/ibex_cs_registers.sv:617-618,
  631-632, 1731-1732
- Edge: yes, of F-PMC-027
- Status: ACTIVE

### F-PMC-029: Any write to the read-only counter range 0xC00-0xC9F is an illegal instruction (all modes)
- What: Alias of F-CSR-011: PMC perspective (a write op to the read-only counter range 0xC00-0xC9F
  is the csr_addr[11:10] == 11 rule; csrrs x0 / csrrsi 0 are reads and legal, subject to mcounteren
  in U-mode), see canonical.
- Edge: yes, of F-PMC-027
- Status: ALIAS of F-CSR-011

### F-PMC-030: time / timeh (0xC01 / 0xC81) are not implemented: illegal instruction in all modes
- What: Not decoded; default illegal. mcounteren.TM is read-only 0 accordingly.
- Observable at: rvfi_trap; csrr read-back of mcause == 2 on rvfi_rd_wdata for rdtime in M-mode
  and U-mode.
- Config: none.
- Source: spec zicntr.adoc (time CSR), machine.adoc "Machine Counter-Enable" (time is a shadow of
  mtime) | doc cs_registers.rst "Time Registers (time(h))" ("Any access to these registers will
  trap") | RTL-defined rtl/ibex_cs_registers.sv:702-704, 1567
- Edge: no
- Status: ACTIVE

### F-PMC-031: mcounteren bit set for an inhibited counter: U-mode read allowed, value frozen
- What: Restates F-PMC-021's "accessibility unaffected ... U-mode alias reads still permitted if
  mcounteren allows" (rtl/ibex_cs_registers.sv:617-618, 1679); carried by the alias gate bin.
- Source: spec machine.adoc "Machine Counter-Inhibit" | RTL-defined
  rtl/ibex_cs_registers.sv:617-618, 1679
- Edge: yes, of F-PMC-021
- Status: FOLDED into F-PMC-021 (bin CG-PMC-006.cr_inhibit_gate.inh_set_u_ok)

### F-PMC-032: mhpmcounter3 (NumCyclesLSU) counts cycles the ID instruction waits on the data side
- What: dside_wait = instr_valid_id & ~instr_kill & (outstanding_memory_access | stall_ld_hz):
  cycles in which a VALID next instruction sits in ID while WB holds a load/store still awaiting
  data_rvalid_i, or is stalled by a load-use hazard on the WB load. The access's OWN wait-for-grant
  cycles in ID (stall_mem: lsu_req_dec & ~lsu_req_done_i) are NOT counted (fact-check TP-PMC-034;
  rtl/ibex_id_stage.sv:1015-1016, :1095-1096, :1120, :1135-1136) and nothing is counted while ID is
  empty. Counted per cycle, not per access.
- Observable at: csrr read-back of mhpmcounter3 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[0]) across a
  load with N-cycle response latency followed by a dependent instruction.
- Config: mcountinhibit[3]=0; memory latency; instruction mix.
- Source: doc performance_counters.rst "Event Selector" (NumCyclesLSU) | RTL-defined
  rtl/ibex_id_stage.sv:1135-1136; rtl/ibex_cs_registers.sv:1589
- Edge: no
- Status: ACTIVE

### F-PMC-033: mhpmcounter4 (NumCyclesIF) counts cycles ID is ready but no instruction is available
- What: iside_wait = id_in_ready & ~instr_valid_id: fetch-starvation cycles (after branches, on
  instruction-memory latency, after debug/exception redirect). Not counted while ID is stalled.
- Observable at: csrr read-back of mhpmcounter4 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[1]) across a
  jump into uncached code with slow instr_rvalid_i.
- Config: mcountinhibit[4]=0; cpuctrlsts.icache_enable (instruction-memory latency is stimulus,
  not configuration).
- Source: doc performance_counters.rst (NumCyclesIF) | RTL-defined rtl/ibex_core.sv:635;
  rtl/ibex_cs_registers.sv:1590
- Edge: no
- Status: ACTIVE
- Notes: fact-check TP-PMC-052: the count is independent of the instruction stream (a run of csrr
  with imem latency moves counter 4), so items asserting "hpm counters unchanged" exclude counter 4
  or pin a warm icache with back-to-back delivery.

### F-PMC-034: mhpmcounter5 (NumLoads) counts load instructions once; misaligned loads count once (doc says twice)
- What: perf_load asserts only in the LSU IDLE state when the first request of a load is issued,
  independent of grant timing. The second request of a misaligned load (WAIT_GNT_MIS /
  WAIT_RVALID_MIS states) does not assert it, so a misaligned load adds 1, not 2. It is asserted
  even when the request is suppressed by a PMP error (perf_load_o set in the same branch as
  pmp_err_d), so a PMP-denied load also counts (former F-PMC-035, now a bin of CG-PMC-003).
- Observable at: csrr read-back of mhpmcounter5 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[2]) ==
  number of load instructions issued to the LSU (aligned or not); data_req_o shows two beats for a
  misaligned load while the counter moves by 1.
- Config: mcountinhibit[5]=0; PMP; misaligned addresses.
- Source: doc performance_counters.rst "Event Selector" (NumLoads: "Misaligned accesses are counted
  as two accesses") | RTL-defined rtl/ibex_load_store_unit.sv:425-426 (defaults), 468-475 (IDLE
  normal access, perf_load_o/perf_store_o), 489-544 (WAIT_GNT_MIS / WAIT_RVALID_MIS: no perf
  assert); rtl/ibex_core.sv:1063 (data_req_o gating), 1557; rtl/ibex_cs_registers.sv:1591
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D6: the doc states misaligned accesses count as two, RTL counts one per
  instruction (checker follows the RTL, `pass (doc mismatch D6)`). Owner question Q10.

### F-PMC-035: PMP-denied load/store still increments NumLoads/NumStores
- What: Restates the parent's "asserted even when the request is suppressed by a PMP error"
  (rtl/ibex_load_store_unit.sv:468-475; rtl/ibex_core.sv:1063); carried by the parent's variant bin.
- Source: RTL-defined rtl/ibex_load_store_unit.sv:468-475; rtl/ibex_core.sv:1063
- Edge: yes, of F-PMC-034
- Status: FOLDED into F-PMC-034 (bin CG-PMC-003.cr_variant_rel.pmpden_eq)

### F-PMC-036: mhpmcounter6 (NumStores) counts store instructions once; misaligned stores count once (doc says twice)
- What: Symmetric to F-PMC-034 with lsu_we=1: one increment per store instruction issued, including
  PMP-denied stores; the second beat of a misaligned store is not counted.
- Observable at: csrr read-back of mhpmcounter6 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[3]) vs.
  store instruction count; data_req_o & data_we_o beats exceed the delta by the number of
  misaligned stores.
- Config: mcountinhibit[6]=0.
- Source: doc performance_counters.rst (NumStores: "Misaligned accesses are counted as two
  accesses") | RTL-defined rtl/ibex_load_store_unit.sv:468-475, 489-544; rtl/ibex_cs_registers.sv:
  1592
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D6 as F-PMC-034 (owner question Q10).

### F-PMC-037: Misaligned load/store spanning a PMP boundary: counted once, first half issued, second half faults
- What: Folded into F-PMC-034: the parent already states that perf_load/perf_store asserts once from
  the IDLE request, never from the second (misaligned) request, and also when the request is
  PMP-denied; a PMP-denied second half is that rule with the fault itself owned by F-PMP-088 (Critic
  M-9); carried by the parent's straddle bins.
- Source: RTL-defined rtl/ibex_load_store_unit.sv:468-475, 503-544 (WAIT_RVALID_MIS pmp_err_d for
  the second part)
- Edge: yes, of F-PMC-034
- Status: FOLDED into F-PMC-034 (bin CG-PMC-003.cp_variant.straddle_pmp, CG-PMC-003.cr_variant_rel.straddle_eq)

### F-PMC-038: mhpmcounter7 (NumJumps) counts jal/jalr (including c.j, c.jal, c.jr, c.jalr, cm.popret's return jump); the RTL also counts fence.i against the doc (B20)
- What: perf_jump pulses once per jump when the controller sets the PC (jump_set, deduped by
  branch_jump_set_done_q, rtl/ibex_id_stage.sv:806-815), in DECODE. fence.i is implemented as a jump
  to pc + 4 (jump_in_dec_o / jump_set_o, rtl/ibex_decoder.sv:704-720) and therefore increments NumJumps
  (fact-check X-23), which the doc's definition (performance_counters.rst:39: j, jal, jr, jalr) excludes:
  bug candidate B20 (TP-PMC-061, expected-fail; the checker follows the doc; TP-PMC-040 keeps fence.i
  out of its windows).
- Observable at: csrr read-back of mhpmcounter7 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[4]) equals
  the number of retired jal/jalr-class instructions.
- Config: mcountinhibit[7]=0.
- Source: doc performance_counters.rst (NumJumps) | RTL-defined rtl/ibex_controller.sv:681-687;
  rtl/ibex_cs_registers.sv:1593
- Edge: no
- Status: ACTIVE
- Notes: mret/dret and exception redirects are not jumps for this counter (pc_set via other paths). An illegal JALR encoding (funct3 != 0) does NOT count: the decoder's end-of-decode override clears jump_set_o for every illegal encoding (rtl/ibex_decoder.sv:905-918; rtl-arch withdrew its D-COUNT-ILLEGAL-ENC candidate). Reading-only corner (rtl-arch event-7 (b), dv/auto_dv/evidence/gen_hpm_event_defs.md): a jump behind an outstanding WB load/store pulses perf_jump speculatively (instr_executing_spec has no outstanding-access term, rtl/ibex_id_stage.sv:1054-1057); if that access faults the jump is killed and re-fetched after the handler and pulses again, two pulses for one retired jump; not seen in a run; the exact items exclude it by precondition, the bound class (C-10-like) admits it.

### F-PMC-039: mhpmcounter8 (NumBranches) counts every conditional branch, taken or not
- What: perf_branch asserts in the FIRST_CYCLE arm of the ID FSM while the branch is the valid
  instruction in ID under instr_executing_spec (rtl/ibex_id_stage.sv:886-934). instr_executing_spec
  lacks the ~outstanding_memory_access term (:1054-1057) while id_fsm_q advances only under
  instr_executing (:866-869), so the count is exactly one per branch only when the branch enters ID
  with no WB load/store response outstanding; a branch waiting in ID behind an outstanding access
  counts once per waiting cycle (fact-check X-13; bug candidate B17, F-PMC-053). Counters 7 and 9
  are exact (branch_set / jump_set deduped by branch_jump_set_done_q).
- Observable at: csrr read-back of mhpmcounter8 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[5]) equals
  the retired beq/bne/blt/bge/bltu/bgeu/c.beqz/c.bnez count when no branch waited behind an
  outstanding WB access (C-10 precondition of the exact items).
- Config: mcountinhibit[8]=0; cpuctrlsts.data_ind_timing either value.
- Source: doc performance_counters.rst (NumBranches) | RTL-defined rtl/ibex_id_stage.sv:934;
  rtl/ibex_cs_registers.sv:1594
- Edge: no
- Status: ACTIVE
- Notes: the waiting class is carried by F-PMC-053 (expected-fail B17, TP-PMC-058); TP-PMC-041 is
  the exact-class pass item. An illegal conditional-branch encoding (funct3 010/011) does NOT count: the decoder's
  end-of-decode override clears branch_in_dec_o for every illegal encoding (rtl/ibex_decoder.sv:905-918).

### F-PMC-040: mhpmcounter9 (NumBranchesTaken) counts taken conditional branches (data_ind_timing=0)
- What: perf_tbranch = branch_set_i in the controller; with data-independent timing off, branch_set
  is only asserted for a true branch_decision.
- Observable at: csrr read-back of mhpmcounter9 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[6]) equals
  the taken-branch count from RVFI (rvfi_pc_wdata != rvfi_pc_rdata + size).
- Config: cpuctrlsts.data_ind_timing=0; mcountinhibit[9]=0.
- Source: doc performance_counters.rst (NumBranchesTaken) | RTL-defined
  rtl/ibex_controller.sv:686; rtl/ibex_id_stage.sv:790-791, 928; rtl/ibex_cs_registers.sv:1595
- Edge: no
- Status: ACTIVE

### F-PMC-041: mhpmcounter9 over-counts with cpuctrlsts.data_ind_timing=1: not-taken branches also count (bug candidate)
- What: With data_ind_timing=1, branch_set_raw_d = branch_decision | data_ind_timing = 1 for every
  branch, and the controller's perf_tbranch_o = branch_set_i, so NumBranchesTaken increments for
  not-taken branches too (the PC is "set" to PC+4).
- Observable at: csrr read-back on rvfi_rd_wdata: mhpmcounter9 == mhpmcounter8 over any window with
  data_ind_timing=1, even when some branches are not taken (rvfi_pc_wdata sequential).
- Config: cpuctrlsts.data_ind_timing=1 (SecureIbex build parameter DataIndTiming=1 enables the
  path); mcountinhibit[9]=0.
- Source: doc performance_counters.rst (NumBranchesTaken: "Number of taken branches (conditional)")
  | RTL-defined rtl/ibex_id_stage.sv:790-791, 815, 831, 928; rtl/ibex_controller.sv:681-687
- Edge: yes, of F-PMC-040
- Status: ACTIVE
- Notes: Bug candidate B11 (RTL/doc disagreement; needs repro). Owner question Q9.

### F-PMC-042: mhpmcounter10 (NumInstrRetC) counts retired 16-bit instructions
- What: perf_instr_ret_compressed = perf_instr_ret & wb_compressed_q. Same exclusions as minstret
  (trapping c.ebreak / illegal compressed encodings not counted). Zcmp instructions count once.
  Dummy instructions are not compressed and do not count here. The read path applies the same
  speculative +1 as minstret.
- Observable at: csrr read-back of mhpmcounter10 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[7]) equals
  the number of rvfi_valid items with a 16-bit rvfi_insn and no rvfi_trap.
- Config: mcountinhibit[10]=0.
- Source: doc performance_counters.rst (NumInstrRetC) | RTL-defined rtl/ibex_wb_stage.sv:207, 210;
  rtl/ibex_cs_registers.sv:1596, 1687-1692; rtl/ibex_if_stage.sv:527
- Edge: no
- Status: ACTIVE

### F-PMC-043: mhpmcounter11 (NumCyclesMulWait) counts multiplier stall cycles; with RV32MSingleCycle only mulh/mulhsu/mulhu stall (1 cycle)
- What: perf_mul_wait = stall_multdiv & mult_en_dec (rtl/ibex_id_stage.sv:1226). In the single-cycle
  multiplier configuration mul completes without stall (0 counted); mulh-class instructions stall
  one cycle (1 counted each). These per-instruction constants hold only when the multiply does not
  wait in ID behind an outstanding WB load/store: mult_en_id = instr_executing ? mult_en_dec : 0
  (:733), so while outstanding_memory_access holds the multiply does not start, ex_valid stays 0,
  stall_multdiv = 1 and every waiting cycle is counted, for `mul` too (fact-check X-12 / X-13; B17,
  F-PMC-053). The dummy MUL (SecureIbex) is `mul` and adds no wait cycle (F-PMC-011).
- Observable at: csrr read-back of mhpmcounter11 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[8]) ==
  number of mulh/mulhsu/mulhu executed, when no multiply waited behind an outstanding WB access
  (C-10).
- Config: mcountinhibit[11]=0; cpuctrlsts.dummy_instr_en.
- Source: doc performance_counters.rst (NumCyclesMulWait) | doc integration.rst RV32M table
  ("RV32MSingleCycle: 1-2 cycle multiplier") | RTL-defined rtl/ibex_id_stage.sv:1226;
  rtl/ibex_cs_registers.sv:1597
- Edge: no
- Status: ACTIVE

### F-PMC-044: mhpmcounter12 (NumCyclesDivWait) counts iterative divider stall cycles
- What: perf_div_wait = stall_multdiv & div_en_dec for div/divu/rem/remu (rtl/ibex_id_stage.sv:1227;
  iterative divider: DIV_STALL_FULL = 36 stall cycles, DIV_STALL_ZERO = 1 for divide-by-zero with
  data_ind_timing = 0; signed overflow iterates fully). A divide behind an outstanding WB load/store
  does not start until the response (div_en_id gated by instr_executing, :734; C-9): its RVFI gap is
  37 + W and the W deferred-start cycles are counted too (fact-check X-12 / X-13; B17, F-PMC-053).
  Dummy DIV instructions also count (F-PMC-011).
- Observable at: csrr read-back of mhpmcounter12 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[9]) per div
  instruction equals its latency minus 1 (the final non-stall cycle) when the divide did not wait
  behind an outstanding WB access (C-10).
- Config: mcountinhibit[12]=0; cpuctrlsts.dummy_instr_en.
- Source: doc performance_counters.rst (NumCyclesDivWait) | RTL-defined rtl/ibex_id_stage.sv:1227;
  rtl/ibex_cs_registers.sv:1598
- Edge: no
- Status: ACTIVE

### F-PMC-045: Event counter write while its event fires in the same cycle: write wins, event lost
- What: Same ibex_counter priority as F-PMC-004 for mhpmcounter3..12. Among the HPM counters the
  coincidence is structurally reachable only for mhpmcounter10(h) (fact-check X-18): `c.xxx ; csrw
  mhpmcounter10` with the compressed instruction retiring in WB in the write cycle (c.lw with a
  delayed response, or back-to-back issue). For counters 3..9, 11, 12 the event is asserted only
  while its own instruction is the valid instruction in ID (or while the csrw cannot commit:
  dside_wait needs outstanding_memory_access, which blocks csr_op_en; iside_wait needs
  ~instr_valid_id) and the csrw is a different instruction, so "csrw mhpmcounter3 while WB waits on
  a load" never commits in a counted cycle.
- Observable at: csrr read-back of mhpmcounter10(h) on rvfi_rd_wdata after the write == written +
  events after the write cycle (the coincident event is not added; an h write also drops it, X-17);
  rvfi_ext_mhpmcounters[7] on the following retirements (TP-PMC-047).
- Config: mcountinhibit[N]=0.
- Source: RTL-defined rtl/ibex_counter.sv:44-50
- Edge: yes, of F-PMC-015
- Status: ACTIVE

### F-PMC-046: Flushed instructions do not retire and do not count in minstret/NumInstrRetC; already-issued events remain
- What: Instructions behind a taken branch, exception or debug entry never reach WB (no count). An
  instruction killed by a WB fault (instr_kill) is not counted. Events that were already asserted
  (perf_load for a request already issued; perf_branch for a branch that was in ID when the WB load
  faulted, asserted once per cycle it waited because instr_executing_spec ignores wb_exception and
  outstanding_memory_access, rtl/ibex_id_stage.sv:1033-1035, :1054-1062 - the B17 class,
  F-PMC-053 - and then flushed) are not rolled back.
- Observable at: csrr read-back of minstret on rvfi_rd_wdata == rvfi_valid & ~rvfi_trap count; csrr
  read-back of mhpmcounter5 exceeds the number of retired loads by the number of faulting loads.
- Config: none.
- Source: RTL-defined rtl/ibex_wb_stage.sv:208-209; rtl/ibex_id_stage.sv:1033-1036 (instr_kill),
  1218-1220
- Edge: yes, of F-PMC-007
- Status: ACTIVE

### F-PMC-047: Counters do not stop in debug mode; debug-mode instructions retire into minstret
- What: dcsr.stopcount is hardwired 0. mcycle counts debug-mode cycles; minstret counts
  debug-program instructions (dret included); hpm counters count their events.
- Observable at: csrr read-back on rvfi_rd_wdata before dret vs. after debug entry; rvfi_ext_mcycle
  continuity.
- Config: mcountinhibit.
- Source: spec Sdext.adoc "Debug Mode" item 6 | RTL-defined rtl/ibex_cs_registers.sv:827,
  1622-1649, 1679
- Edge: no
- Status: ACTIVE

### F-PMC-048: minstret with single step: exactly +1 per stepped instruction unless it traps
- What: The parent's retirement rule applied inside a single-step window (stepped instruction
  counted, trapping one not, wfi-as-nop counted); carried by the parent's step bins.
- Source: spec zicntr.adoc NOTE; Sdext.adoc "Single Step / Step Bit In Dcsr" | RTL-defined
  rtl/ibex_wb_stage.sv:208-209; rtl/ibex_controller.sv:700-711
- Edge: yes, of F-PMC-007
- Status: FOLDED into F-PMC-007 (bin CG-PMC-002.cr_window_delta.step_one, step_zero; CG-DBG-006.cr_stepped_minstret.alu_one, wfi_one, ecall_zero)

### F-PMC-049: RVFI exposes counter state per retirement: rvfi_ext_mcycle, rvfi_ext_mhpmcounters[10], rvfi_ext_mhpmcountersh[10]
- What: Sampled from the counters when the instruction leaves ID (values for mhpmcounter3..12 low/
  high halves; h halves are 0 with 32-bit counters). minstret is not exported on RVFI (read via CSR
  only).
- Observable at: rvfi_ext_mcycle, rvfi_ext_mhpmcounters, rvfi_ext_mhpmcountersh.
- Config: none.
- Source: RTL-defined rtl/ibex_core.sv:173-175, 2102, 2108-2127
- Edge: no
- Status: ACTIVE

### F-PMC-050: Counter reads are non-destructive and do not affect counting
- What: csrr of any counter or of mcounteren/mcountinhibit has no side effect; the reading
  instruction itself retires and is counted in minstret.
- Observable at: csrr read-back on rvfi_rd_wdata: repeated reads increase minstret by 1 each; hpm
  counters unchanged by reads.
- Config: none.
- Source: spec machine.adoc "Machine Counter-Enable" ("The act of reading or writing this register
  does not affect the underlying counters") | doc performance_counters.rst ("Reads to all these
  registers are non-destructive") | RTL-defined rtl/ibex_cs_registers.sv:1020-1023 (csr_wr only)
- Edge: no
- Status: ACTIVE

### F-PMC-051: All-ones and zero writes to mcycle/minstret/mhpmcounterN are stored exactly (32-bit halves)
- What: Folded into F-PMC-001: "stored exactly" for all-ones and zero is a checker bullet on the
  counter write semantics (F-PMC-006 / F-PMC-015 own the halves; no WARL masking exists) (v2 edge
  rule, second pass; Critic M-9); carried by the write-pattern bins of the counter groups.
- Source: spec machine.adoc "Hardware Performance Monitor" (can be written with a given value) |
  RTL-defined rtl/ibex_counter.sv:33-50
- Edge: yes, of F-PMC-001
- Status: FOLDED into F-PMC-001 (bin CG-PMC-001.cr_op_wdata.wrlo_z, wrlo_1, wrhi_z, wrhi_1; CG-PMC-002.cr_op_wdata.wrlo_z, wrlo_1, wrhi_z, wrhi_1; CG-PMC-004.cr_wdata_reg.z_lo, o_lo, z_hi, o_hi)

### F-PMC-052: Interrupt taken and instruction retirement: the interrupted (last) instruction is counted
- What: The parent's retirement rule across an interrupt (IRQ_TAKEN only with ID empty and WB ready,
  rtl/ibex_controller.sv:1078-1079, so nothing in flight is lost); carried by the parent's window
  bin.
- Source: RTL-defined rtl/ibex_controller.sv:1078-1079 (PipeEmptyOnIrq), 704-722
- Edge: yes, of F-PMC-007
- Status: FOLDED into F-PMC-007 (bin CG-PMC-002.cr_window_delta.irq_eq)

### F-PMC-053: HPM counters 8 (NumBranches), 11 (NumCyclesMulWait) and 12 (NumCyclesDivWait) over-count an instruction waiting in ID behind an outstanding WB memory access (bug candidate B17)
- What: A conditional branch, multiply or divide that enters ID while the preceding load/store still
  awaits its WB response is held by outstanding_memory_access (instr_executing = 0,
  rtl/ibex_id_stage.sv:1059-1062), but perf_branch_o is asserted in the FIRST_CYCLE arm under
  instr_executing_spec, which lacks that term (:886-934, :1054-1057), and perf_mul_wait_o /
  perf_div_wait_o = stall_multdiv & *_en_dec (:1226-1227) are asserted while the unit has not
  started (mult_en_id / div_en_id gated by instr_executing, :733-734): each waiting cycle adds one
  count. Counters 7 (jumps) and 9 (taken) are exact (branch_set / jump_set deduped by
  branch_jump_set_done_q, :806-815).
- Observable at: csrr read-back of mhpmcounter8 / 11 / 12 on rvfi_rd_wdata (rvfi_ext_mhpmcounters[5]
  / [8] / [9]) over a window of `lw ; beq` (`lw ; mul`, `lw ; div`) pairs with the data agent
  holding rvalid for K cycles: doc count (1 per branch; mul 0 / mulh 1; DIV_STALL_FULL per divide)
  vs RTL count (+ about K per pair); the control with an ALU instruction between the load and the
  counted instruction gives the doc count.
- Config: mcountinhibit[8/11/12]=0; dummy_instr_en=0; knob:dmem_rvalid_delay.
- Source: doc performance_counters.rst:41 ("Number of branches (conditional)"), NumCyclesMulWait /
  NumCyclesDivWait rows | RTL-defined rtl/ibex_id_stage.sv:733-734, 866-869, 886-934, 1054-1062,
  1226-1227 (fact-check X-12 / X-13; rtl-arch gen_bug_reproducer_specs.md BUG-09)
- Edge: yes, of F-PMC-039 (also qualifies F-PMC-043 / F-PMC-044)
- Status: ACTIVE
- Notes: Bug candidate B17 (gen_bug_log.md v1d; DV Lead direction: the checker follows the doc for
  the waiting class, RTL-defined otherwise). Canonical for the B17 items TP-PMC-058 (counter 8),
  TP-PMC-059 (counter 11), TP-PMC-060 (counter 12), each expected-fail in its own `_xfail` test;
  the exact-count items of F-PMC-039/043/044 carry the precondition "no outstanding WB memory access
  when the counted instruction is in ID" and pass (C-10).

---------------------------------------------------------------------------------------------------


# 4.6 Areas IMEM, DMEM, FE, IC: Instruction and data memory protocol, LSU, fetch stage, instruction cache


Subagent output for dv-lead T-002 (feature-list fan-out). Areas: IMEM (instruction memory
interface protocol), DMEM (data memory interface protocol and LSU), FE (instruction fetch),
IC (instruction cache). Build configuration is the fixed `opentitan` config of
ibex_configs.yaml (ICache=1, ICacheECC=1, ICacheScramble=1, WritebackStage=1, BranchTargetALU=1,
BranchPredictor=0, SecureIbex=1, PMPEnable=1). CHERIoT mode is out of scope (cheriot_enable_i tied
Off in the wrapper); CHERIoT-only paths are listed once each as carve-outs so they can be excluded
from coverage on purpose rather than by accident.

Two structural findings that shape the whole part:

1. With ICache=1 the prefetch buffer and fetch FIFO are NOT instantiated
   (rtl/ibex_if_stage.sv:298-347 instantiates ibex_icache; the ibex_prefetch_buffer path is the
   else-branch at 348-414). Every "prefetch buffer" behaviour asked for in the brief is implemented
   by the icache fill buffers (NUM_FB=4) and its 16-bit skid buffer. FE entries below say so.
2. The memory interface protocol is not a RISC-V specification item. It is defined by
   doc/03_reference/load_store_unit.rst "Protocol", doc/03_reference/instruction_fetch.rst
   "Instruction-Side Memory Interface"/"Protocol", doc/02_user/integration.rst "Interfaces", and
   the RTL. Every protocol rule is a feature below (they become passive protocol assertions).

Status field (Critic verdict v1 fixes): every block carries `- Status:` = ACTIVE | ALIAS of F-<id>
| FOLDED into F-<id> (bin <name>). Only ACTIVE entries count in the completeness measure. An
ALIAS is the same behaviour stated from this area's perspective (canonical entry named); a FOLDED
entry is an edge that restated its parent (Critic C-12 patterns a-d) and is now one of the
parent's bins. Counts: 156 IDs (F-IMEM-001..032, F-DMEM-001..051, F-FE-001..025, F-IC-001..048);
ACTIVE 129 (7 of them NEW: F-IMEM-031, F-IMEM-032, F-DMEM-048..051, F-IC-048), ALIAS 11,
FOLDED 16. Edge rule applied to all 63 edge entries: `Edge: yes` is kept only where the What names
a stimulus condition or timing coincidence the parent does not AND the observable or the expected
outcome differs. Generate arms: the opentitan config sets BaseIsa = BaseIsaRV32IorCHERIoT
(ibex_configs.yaml:42), so the elaborated arms are g_pmp_addr_gate (rtl/ibex_core.sv:1589-1593)
and gen_memcap_rd (rtl/ibex_load_store_unit.sv:701-709); citations below name those arms.

Fact-check fold (README_FIX3_BRIEF.md; rtl-arch T-053, Sections 1 and
3.mem_a / 3.mem_b): the What / Observable / Notes of F-IMEM-021/022/023/024/028, F-DMEM-027/028/030/031/
041/044/045/046, F-FE-004/005/010/012/014/017/021/022/023/025 and F-IC-004/006/007/016/020/021/022/038/
042/043 are corrected to the RTL as verified there, and the "RTL-defined behaviour" list is extended.
Convention labels C-n refer to the header of dv/auto_dv/work/dv-lead/parts6/tp_mem_fetch_icache.md. No
feature ID is added, renumbered or retired by this fold (the new expected-fail item TP-DMEM-064 and the
doc mismatch D21 attach to F-DMEM-041).

Constants derived from rtl/ibex_pkg.sv:395-416 for this config: IC_SIZE_BYTES=4096, IC_NUM_WAYS=2,
IC_LINE_SIZE=64 (IC_LINE_BYTES=8, IC_LINE_W=3), IC_NUM_LINES=256, IC_LINE_BEATS=2,
IC_INDEX_W=8 (index = addr[10:3]), IC_TAG_SIZE=22 (21 tag bits addr[31:11] + 1 valid bit),
IC_DATA_ECC_SIZE=7, IC_TAG_ECC_SIZE=6. With ICacheECC=1 (rtl/ibex_top.sv:221-225): BusSizeECC=39,
LineSizeECC=78, TagSizeECC=28. ls_fsm_e (rtl/ibex_pkg.sv:816-820): IDLE, WAIT_GNT_MIS,
WAIT_RVALID_MIS, WAIT_GNT, WAIT_RVALID_MIS_GNTS_DONE, CTX_WAIT_GNT1, CTX_WAIT_GNT2, CTX_WAIT_RESP
(the three CTX_* states are CHERIoT-only).

---------------------------------------------------------------------------------------------------

## IMEM: instruction memory interface protocol at the ibex_core boundary

### F-IMEM-001: Request held until grant
- What: Once instr_req_o is asserted it stays asserted until instr_gnt_i is high for one cycle.
  The icache tracks an ungranted external request in the owning fill buffer (fill_ext_hold) and
  refuses to complete or cancel that buffer's external phase while the hold is set.
- Observable at: instr_req_o, instr_gnt_i
- Config: none
- Source: doc: doc/03_reference/instruction_fetch.rst "Instruction-Side Memory Interface"
  (instr_req_o row) and "Protocol" | doc: doc/03_reference/load_store_unit.rst "Protocol" step 1 |
  RTL: rtl/ibex_icache.sv:703-705, 763-765, 774-775, 1030-1037
- Edge: no
- Status: ACTIVE
- Notes: passive assertion candidate: instr_req_o & ~instr_gnt_i |=> instr_req_o.

### F-IMEM-002: Fetch address is always word aligned
- What: instr_addr_o[1:0] is always 2'b00. Half-word instruction addresses are handled inside the
  core; the LSB of the internal fetch address is ignored.
- Observable at: instr_addr_o
- Config: none
- Source: doc: doc/03_reference/instruction_fetch.rst "Instruction-Side Memory Interface"
  (instr_addr_o row) and "Misaligned Accesses" | RTL: rtl/ibex_icache.sv:1037,
  rtl/ibex_if_stage.sv:938 (IbexInstrAddrUnaligned)
- Edge: no
- Status: ACTIVE

### F-IMEM-003: Address stable while a request waits for grant
- What: While instr_req_o is high and not yet granted, instr_addr_o does not change. The address
  comes from the oldest fill buffer with an external request (fill_addr_q plus beat offset); that
  buffer cannot retire its external phase while it holds an ungranted request, so the arbitration
  winner and the address are stable.
- Observable at: instr_req_o, instr_addr_o, instr_gnt_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" step 2 (address may change only
  after grant; applies to the I-side per instruction_fetch.rst "Protocol") | RTL:
  rtl/ibex_icache.sv:767-775, 842, 989-997, 1033-1037
- Edge: no
- Status: ACTIVE
- Notes: passive assertion candidate: instr_req_o & ~instr_gnt_i |=> $stable(instr_addr_o).

### F-IMEM-004: Grant in the same cycle as the request
- What: instr_gnt_i may be asserted in the very cycle instr_req_o rises. The icache counts a
  speculative request granted immediately (fill_spec_done) in the fill buffer's external count.
- Observable at: instr_req_o, instr_gnt_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" step 1 ("same cycle ... or any
  number of cycles later") | RTL: rtl/ibex_icache.sv:703-705, 759-762
- Edge: yes, of F-IMEM-001
- Status: ACTIVE

### F-IMEM-005: Grant delayed by an arbitrary number of cycles
- What: Folded into F-IMEM-001: a delayed grant is the hold scenario of F-IMEM-001 itself (pattern
  c); carried by CG-IMEM-001.cp_gnt_delay.d4_15 / d16p and cr_delay_x_knob (knob:imem_gnt_delay).
- Edge: yes, of F-IMEM-001
- Status: FOLDED into F-IMEM-001 (bin CG-IMEM-001.cp_gnt_delay.d16p)

### F-IMEM-006: One rvalid per granted request; rdata/err meaningful only with rvalid
- What: The memory returns exactly one instr_rvalid_i pulse per granted request. instr_rdata_i and
  instr_err_i are sampled by the core only in a cycle where instr_rvalid_i is high (fill_rvd_arb).
- Observable at: instr_rvalid_i, instr_rdata_i, instr_err_i
- Config: none
- Source: doc: doc/03_reference/instruction_fetch.rst "Instruction-Side Memory Interface"
  (instr_rvalid_i row) | doc: doc/03_reference/load_store_unit.rst "Protocol" step 3 | RTL:
  rtl/ibex_icache.sv:851-852, 947-950, 962-964
- Edge: no
- Status: ACTIVE
- Notes: TB may drive instr_rdata_i/instr_err_i to random values whenever rvalid is low.

### F-IMEM-007: rvalid at the earliest one cycle after grant, never in the grant cycle
- What: A response is legal one or more cycles after the grant. The icache attributes an incoming
  rvalid to the oldest fill buffer that is busy and expects data; a buffer allocated in the current
  cycle is not busy until the next cycle, so a response in the grant cycle would be dropped or
  attributed to an older request.
- Observable at: instr_gnt_i, instr_rvalid_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" step 3 ("one or more cycles after
  the grant") | RTL: rtl/ibex_icache.sv:721, 851-852, 894-895
- Edge: yes, of F-IMEM-006
- Status: ACTIVE
- Notes: TB memory model constraint (must not respond in the grant cycle). Candidate passive
  assertion: count(gnt) - count(rvalid) >= 1 whenever rvalid is high, sampled before the grant.

### F-IMEM-008: Multiple outstanding requests
- What: The icache can have several granted requests awaiting rvalid. Bound: NUM_FB=4 fill buffers,
  each issuing up to IC_LINE_BEATS=2 external requests, so up to 8 granted requests can be
  outstanding. New lookups (and so new external requests) are throttled when more than
  FB_THRESHOLD=2 non-stale fill buffers are busy, unless the lookup is a branch. Linear prefetch
  alone therefore holds at most 3 non-stale buffers (6 beats, F-FE-017); the 8-beat bound is
  reached only through the branch-lookup path: a taken branch while 3 lines are in flight under
  slow rvalid makes them stale (their beats stay outstanding) and allocates the 4th buffer for the
  target line, whose 2 beats bring the count to 8.
- Observable at: instr_req_o, instr_gnt_i, instr_rvalid_i (outstanding count)
- Config: none
- Source: doc: doc/03_reference/icache.rst "Fill buffers" | RTL: rtl/ibex_icache.sv:72-74,
  247-250, 690-697, 756-784
- Edge: no
- Status: ACTIVE
- Notes: 8 is the static upper bound; it is reachable only via the branch-lookup path above
  (TP-IMEM-008 stimulus; fcov bin on outstanding count 0..8). TB response FIFO depth must be at
  least 8.

### F-IMEM-009: Responses return in request order
- What: When multiple requests are outstanding the memory returns rvalid in the order the requests
  were granted. The icache assigns each rvalid to the oldest expecting fill buffer and the next
  expected beat within it; out-of-order return corrupts the fetched instruction stream silently.
- Observable at: instr_gnt_i, instr_rvalid_i, instr_rdata_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" step 4 | RTL:
  rtl/ibex_icache.sv:833-835, 851-852
- Edge: no
- Status: ACTIVE
- Notes: the DUT cannot detect a violation; the TB memory model must be in-order by construction
  and the scoreboard must check delivered instruction words against memory.

### F-IMEM-010: Back-to-back requests
- What: instr_req_o may stay high across a grant with a new address presented in the next cycle
  (the second beat of a line, or the next fill buffer's request). Each grant advances the beat
  counter of the arbitrated fill buffer.
- Observable at: instr_req_o, instr_addr_o, instr_gnt_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Back-to-back Memory Transaction" wavedrom |
  RTL: rtl/ibex_icache.sv:759-762, 1030-1037
- Edge: yes, of F-IMEM-001
- Status: ACTIVE

### F-IMEM-011: Bus error on a fetched instruction travels with the word and is raised only when that word executes
- What: Bus/fetch-side effect: instr_err_i with rvalid marks that beat errored in the icache fill
  buffer or the prefetch FIFO; the mark travels with the word through IF into ID (instr_fetch_err),
  is dropped with the word when the word is discarded before ID (F-EXC-006), and while the errored
  instruction is the valid instruction in ID its register write and memory request are suppressed.
  The trap itself (cause 1, mepc = PC, mtval = faulting fetch address, D10) is canonical in F-EXC-003.
- Observable at: instr_err_i on beat k of the ibus monitor and the RVFI record of exactly the word
  delivered by that beat carrying rvfi_trap = 1 (beat-to-instruction association); no data_req_o and
  no rvfi_rd_wdata effect for that record; rvfi_pc_wdata = the trap vector.
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Control Transfer Instructions"
  (norm ia_fault_exc_on_target: fault reported on the target instruction) | doc:
  doc/03_reference/exception_interrupts.rst "Exceptions" (code 1) | doc: doc/03_reference/icache.rst
  "Detailed behaviour" (err_o) | RTL: rtl/ibex_icache.sv:947-958, 1194;
  rtl/ibex_if_stage.sv:281, 606, 622; rtl/ibex_id_stage.sv:291-292, 1033; rtl/ibex_controller.sv:233,
  268, 320-321, 849-862; rtl/ibex_pkg.sv:360-361
- Edge: no
- Status: ACTIVE
- Notes: Cross-reference (Critic M-10 cluster F-EXC-003 / F-IMEM-011): this entry keeps the bus- and
  fetch-side effect (beat marking, travel with the word, RF/LSU suppression) and F-EXC-003 the
  cause/CSR effect, the same split as F-PMP-082 / F-EXC-026; the fetch-error edges F-IMEM-012..015 and
  F-FE-016 stay attached here and F-FE-023 is folded here.

### F-IMEM-012: Error on a speculatively fetched instruction that is never executed causes no exception
- What: Alias of F-EXC-006: IMEM perspective (instr_err_i on a word discarded before ID), see
  canonical.
- Edge: yes, of F-IMEM-011
- Status: ALIAS of F-EXC-006

### F-IMEM-013: Error on the second half of an unaligned 32-bit instruction (err_plus2)
- What: Alias of F-EXC-005: IMEM perspective (instr_err_i on the second fetch word only, icache
  err_plus2_o); the bus-side first-half timing case stays F-IMEM-014, see canonical.
- Edge: yes, of F-IMEM-011
- Status: ALIAS of F-EXC-005

### F-IMEM-014: Error on the first half of an unaligned 32-bit instruction is reported without waiting for the second half
- What: If the first (lower) half of a straddling instruction is errored, the skid buffer marks the
  instruction complete immediately (skid_complete_instr) and delivers it with err_o; the core does
  not wait for the second word. mtval = PC (err_plus2 = 0 because skid_err_q is set).
- Observable at: rvfi_trap, mtval (pc), instr_req_o timing
- Config: none
- Source: doc: doc/03_reference/icache.rst "Detailed behaviour" | RTL: rtl/ibex_icache.sv:1094-1101,
  1126-1133, 1194-1197
- Edge: yes, of F-IMEM-011
- Status: ACTIVE
- Notes: the case "both halves errored" collapses into this one (err_plus2 = 0).

### F-IMEM-015: Errored fetch data is never allocated to the cache
- What: A fill buffer with any errored beat does not request a RAM write (no allocation); a later
  fetch of the same line goes to the bus again. Errors accumulated on a speculative external
  request that turned out to be a cache hit are ignored.
- Observable at: instr_req_o/instr_addr_o (re-fetch of the errored line), ic_tag_write_o (absent)
- Config: cpuctrlsts.icache_enable = 1
- Source: RTL-defined: rtl/ibex_icache.sv:815-819, 1021
- Edge: yes, of F-IMEM-011
- Status: ACTIVE

### F-IMEM-016: Redirect (branch/exception/fence.i) while requests are outstanding
- What: On branch_i all busy fill buffers become stale; their remaining responses are still
  accepted in order and their data discarded. External beats already issued are completed; a
  buffer that has not yet issued any external request is cancelled (unless it will be cached).
- Observable at: instr_rvalid_i consumed after pc_set; instr_req_o
- Config: none
- Source: doc: doc/03_reference/icache.rst "Fill buffers" ("If a fill buffer has not made any
  external requests it will be cancelled by an intervening branch, if it has made requests then the
  requests will be completed") | RTL: rtl/ibex_icache.sv:729-734, 741, 767-775, 796
- Edge: no
- Status: ACTIVE
- Notes: TB must respond to every granted request even after a redirect (no "kill" on the bus).
  This replaces the prefetch buffer "branch_discard" counter of rtl/ibex_prefetch_buffer.sv:
  127-128, 211-227, which is not instantiated in this config.

### F-IMEM-017: Redirect while a request waits for grant keeps the request on the bus
- What: A branch cannot cancel an external request that has not been granted; instr_req_o and
  instr_addr_o stay stable until instr_gnt_i, after which the response is discarded as stale.
- Observable at: instr_req_o, instr_addr_o across pc_set
- Config: none
- Source: RTL-defined: rtl/ibex_icache.sv:774-775
- Edge: yes, of F-IMEM-016
- Status: ACTIVE

### F-IMEM-018: Response of a speculative request that hit in the cache is consumed and discarded
- What: Alias of F-IC-037: IMEM perspective (the speculative branch request whose lookup hit is
  still answered and the response consumed), see canonical.
- Edge: yes, of F-IMEM-016
- Status: ALIAS of F-IC-037

### F-IMEM-019: Fetch address sequence within and across cache lines
- What: With the cache enabled a fill fetches its 8-byte line in wrapping order starting at the
  requested word (branch into the upper word fetches word 1 then word 0), then the prefetch
  address advances by one line (+8). Within a line the beat offset is fill_addr[2] plus the beat
  count, truncated to one bit.
- Observable at: instr_addr_o sequence
- Config: cpuctrlsts.icache_enable
- Source: doc: doc/03_reference/icache.rst "Performance notes" ("wrapping address order") and
  "Prefetch Address" | RTL: rtl/ibex_icache.sv:211-224, 830-835, 989-997
- Edge: no
- Status: ACTIVE

### F-IMEM-020: Cache disabled: no wrap, fetch stops at the line end
- What: Folded into F-IMEM-019: the parent's own Config (cpuctrlsts.icache_enable) at the other
  value (pattern b); no-wrap / stop at the line end is carried by
  CG-IMEM-004.cp_seq_kind.end_of_line_stop and cr_seq_x_en.stop_off.
- Edge: yes, of F-IMEM-019
- Status: FOLDED into F-IMEM-019 (bin CG-IMEM-004.cp_seq_kind.end_of_line_stop)

### F-IMEM-021: No new fetches while the core sleeps (WFI) or fetch is halted
- What: In WAIT_SLEEP/SLEEP the controller drives instr_req (req_i to the icache) low; req_i stays
  1 through DECODE and FLUSH (rtl/ibex_controller.sv:541, 600, 609, 623), so lookups made up to the
  FLUSH cycle and the un-issued beats of every allocated fill buffer are still requested on the bus
  at and after the WFI's record; the icache makes no new lookups, completes the open lines and then
  stops. The exact quiet rule is instr_req_o == 0 whenever core_busy_o == Off (core_busy_o includes
  the icache busy_o = invalidation active or beats outstanding, rtl/ibex_icache.sv:1304; C-4).
  instr_req_o resumes when the core wakes (FIRST_FETCH drives req_i for one cycle before the
  IRQ_TAKEN pc_set, so a sequential lookup may precede the vector fetch).
- Observable at: instr_req_o, core_busy_o
- Config: none (WFI instruction, mstatus.mie/mie for wake)
- Source: doc: doc/03_reference/icache.rst "High-level operation" (req_i) and "Detailed
  behaviour" (req_i paragraph) | RTL: rtl/ibex_controller.sv:598-611; rtl/ibex_icache.sv:249;
  rtl/ibex_core.sv:553, 648
- Edge: no
- Status: ACTIVE

### F-IMEM-022: fetch_enable_i gates instruction fetch and execution
- What: Alias of F-RST-010: IMEM perspective (new fetches are issued only while fetch_enable_i ==
  IbexMuBiOn, instr_exec forces halt_if, any other value stops fetch and halts after in-flight
  instructions complete; an invalid MuBi code acts as Off without an alert), see canonical. The
  bus-side in-flight statement is F-IMEM-024; F-IMEM-023 is folded into the canonical.
- Edge: no
- Status: ALIAS of F-RST-010
- Notes: rtl-arch fact-check X-5 (C-4): fetch_enable_i gates only req_i (new lookups,
  rtl/ibex_core.sv:648); the remaining beats of already allocated fill buffers keep requesting and
  a request awaiting grant is never withdrawn (rtl/ibex_icache.sv:756, 764-775, 1030-1031). Rule:
  no new line allocation after the Off edge; instr_req_o == 0 whenever core_busy_o == Off. The ibus
  protocol checker needs no tolerance for a withdrawn request (the canonical F-RST-010 carries the
  same rule).

### F-IMEM-023: Invalid MuBi encoding on fetch_enable_i behaves as Off without an alert
- What: Folded into F-RST-010 (through F-IMEM-022): the parent already states that fetch continues
  only while fetch_enable_i == IbexMuBiOn and stops for "any other value", which is the invalid-MuBi
  statement (Critic M-9); the absence of an alert for an invalid code is added to the parent's
  observable; carried by the parent's gate-cause and code bins.
- Source: RTL-defined: rtl/ibex_core.sv:648-649 (equality with IbexMuBiOn only); contrast
  rtl/ibex_core.sv:1339-1347 (cheriot_enable_i MuBi check)
- Edge: yes, of F-RST-010
- Status: FOLDED into F-RST-010 (bin CG-IMEM-005.cp_gate_cause.fetch_en_invalid, CG-IMEM-005.cp_fetch_en_code.invalid_0, invalid_f)
- Notes: an invalid code stops new line lookups exactly like Off (C-4: the beats of open lines
  complete, no request is withdrawn); no alert (Q-DL-8 / Q-009 default).

### F-IMEM-024: fetch_enable_i deasserted with instructions and bus transactions in flight
- What: When fetch_enable_i leaves On, the instruction in ID/EX and WB complete (including waiting
  for an outstanding data response), the un-issued beats of already allocated fill buffers are still
  requested and every outstanding fetch completes (no request is withdrawn, C-4), no new line is
  looked up, and no new instruction becomes valid in ID; the PC in ID stays at the value it had at
  disable.
- Observable at: rvfi_valid (last retirements), data_rvalid_i/instr_rvalid_i consumed, instr_req_o
- Config: none
- Source: doc: doc/02_user/integration.rst "Interfaces" (fetch_enable_i row) | RTL:
  rtl/ibex_core.sv:1396-1421 (NoExecWhenFetchEnableNotOn assertion)
- Edge: yes, of F-RST-010
- Status: ACTIVE

### F-IMEM-025: fetch_enable_i re-asserted resumes from the held PC
- What: Alias of F-RST-012: IMEM perspective (instr_req_o resumes without re-requesting already
  granted words), see canonical.
- Edge: yes, of F-RST-010
- Status: ALIAS of F-RST-012

### F-IMEM-026: First fetch after reset targets boot_addr_i + 0x80
- What: Alias of F-RST-002: IMEM perspective (first instr_addr_o = {boot_addr_i[31:8], 8'h80}, no
  instr_req_o in the RESET cycle); the FE-side entry is F-FE-002, see canonical.
- Edge: no
- Status: ALIAS of F-RST-002

### F-IMEM-027: instr_rdata_i width and bus integrity at the ibex_core boundary depend on MemECC
- What: ibex_core has parameter MemECC (default 0) giving instr_rdata_i[MemDataWidth-1:0]. With
  MemECC=0 the port is 32 bits and no integrity check exists. With MemECC=1 (ibex_top sets
  MemECC = SecureIbex) the port is 39 bits; bits [38:32] are an inverted 39/32 Hsiao code checked
  on every rvalid; any error (1 or 2 bit) is treated as a fetch error (instruction access fault
  when executed) and pulses alert_major_bus_o in the rvalid cycle.
- Observable at: instr_rdata_i width, alert_major_bus_o, rvfi_trap
- Config: none
- Source: doc: doc/03_reference/instruction_fetch.rst "Instruction-Side Memory Interface"
  (instr_rdata_intg_i row) | doc: doc/03_reference/security.rst "Bus integrity checking" | RTL:
  rtl/ibex_core.sv:50-51, 74, 1353; rtl/ibex_if_stage.sv:259-282; rtl/ibex_top.sv:41
- Edge: no
- Status: ACTIVE
- Notes: OWNER QUESTION: the gen_dut_top wrapper is not yet in dv/auto_dv; it must state MemECC
  (and ICacheTweakInfection) explicitly (Q-002 default: MemECC=1). Everything marked "(MemECC)"
  below is conditional. Doc defect D14: doc/03_reference/security.rst:85-87 says an internal
  interrupt is generated for a bus-integrity mismatch without distinguishing the sides; the I-side
  gives alert_major_bus_o plus an instruction access fault when the word executes and no NMI
  (rtl/ibex_controller.sv:393-438 only counts load/store integrity errors). Doc defect D17:
  doc/03_reference/instruction_fetch.rst:68 lists a separate instr_rdata_intg_i[6:0]; at the
  ibex_core boundary the integrity bits are instr_rdata_i[38:32] (rtl/ibex_core.sv:51, 74; the
  split port exists only in ibex_top).

### F-IMEM-028: PMP-denied instruction fetches still appear on the instruction bus
- What: instr_req_o is not gated by PMP. The PMP instruction channel is evaluated on pc_if (the
  instruction being presented to ID) and pc_if+2, not on the bus address; a fetch to a PMP-denied
  region is issued, granted and answered normally, and the fault is raised only when that
  instruction reaches ID. The icache in this RTL has no instr_pmp_err_i port.
- Observable at: instr_req_o/instr_addr_o (request to a denied region), rvfi_trap (mcause 1)
- Config: PMP region config (pmpcfg/pmpaddr), privilege mode
- Source: RTL-defined: rtl/ibex_core.sv:557, 1063 (only data_req_o is PMP-gated), 1590-1600
  (PMP_I address = pc_if at :1590 in g_pmp_addr_gate, the elaborated arm; PMP_I2 = pc_if+2 at
  :1591); rtl/ibex_if_stage.sv:323, 426-435
- Edge: no
- Status: ACTIVE
- Notes: doc defect D9: doc/03_reference/icache.rst "Detailed behaviour" describes an
  instr_pmp_err_i input that squashes the request; that port does not exist in
  rtl/ibex_icache.sv:22-69. The TB memory model must therefore serve fetches from any address.
  TP-IMEM-030 pins cpuctrlsts.icache_enable = 0 so the denied word's request is never hidden by a
  cache hit (C-14); the cached case is F-IC-036 / TP-IC-028.

### F-IMEM-029: No combinational path from instr_gnt_i / instr_rvalid_i to instr_req_o
- What: instr_req_o depends only on registered fill-buffer state and the lookup grant; grant and
  rvalid inputs affect only next-state. A TB memory model may therefore compute instr_gnt_i
  combinationally from instr_req_o (same-cycle grant) without creating a loop.
- Observable at: instr_req_o never changes in the same cycle as instr_gnt_i / instr_rvalid_i under
  a combinational agent (CG-IMEM-006.cp_req_dep_on_gnt); a TB memory model computing instr_gnt_i
  from instr_req_o in the same cycle runs without a zero-delay loop
- Config: none
- Source: RTL-defined: rtl/ibex_icache.sv:756-775, 1030-1031
- Edge: no
- Status: ACTIVE
- Notes: contrast F-DMEM-032 (D-side has a feedthrough from data_rvalid_i/data_err_i to
  data_req_o).

### F-IMEM-030: Instruction fetch order is preserved for the executed stream
- What: Regardless of gnt/rvalid latencies, out-of-order internal completion (hit in the shadow of
  a miss) and prefetch depth, instructions are delivered to ID in program order with correct PCs;
  the icache arbitrates output by fill-buffer age.
- Observable at: rvfi_pc_rdata / rvfi_insn sequence versus the TB memory image
- Config: none
- Source: doc: doc/03_reference/icache.rst "Fill buffers" (age matrix) | RTL:
  rtl/ibex_icache.sv:723-725, 845-849, 1065-1068
- Edge: no
- Status: ACTIVE
- Notes: end-to-end check: every rvfi_insn equals the memory word(s) at rvfi_pc_rdata at fetch
  time (needed because the DUT cannot detect an out-of-order TB response).

### F-IMEM-031: Grant is legal only while a request is pending (driver rule, passive assertion)
- What: instr_gnt_i has meaning only in a cycle where instr_req_o is high. The DUT never checks a
  grant against its own request: the icache counts fill_ext_arb & instr_gnt_i into the external
  beat count and fill_spec_req & instr_gnt_i as an immediately granted speculative request, and
  the LSU takes a bare data_gnt_i as a grant in every wait state where it samples it (F-DMEM-048).
  A grant driven while instr_req_o is low is therefore a TB protocol error that the DUT cannot
  flag; the TB agent must derive instr_gnt_i from the boundary instr_req_o only and a passive
  assertion on gen_sva_ibus (instr_gnt_i |-> instr_req_o) enforces the rule as a TB-error class.
- Observable at: instr_gnt_i versus instr_req_o in the same cycle (assertion)
- Config: none
- Source: rtl-arch inventory (gen_interface_inventory.md section 2 rule 2, section 11) |
  doc: doc/03_reference/load_store_unit.rst:89 (Protocol step 1: the memory answers a request with
  gnt; by reference from instruction_fetch.rst:86-87) | RTL: rtl/ibex_icache.sv:703-705, 759-762
  (grant consumed unqualified by the request)
- Edge: no
- Status: ACTIVE
- Notes: protocol assertion, no DUT checker; the D-side twin is F-DMEM-048.

### F-IMEM-032: Unsolicited instruction-side rvalid is not defended (MEM-19)
- What: An instr_rvalid_i with no fill buffer expecting a beat is silently ignored (fill_rvd_arb
  requires fill_rvd_exp; the icache assertion block has no rvalid check). If some buffer is
  expecting a beat, the extra rvalid is consumed as that beat and every later response shifts by
  one, corrupting the fetched stream without any DUT indication. Integrity is checked on every
  rvalid (instr_intg_err_o = intg_err & instr_rvalid_i), so an unsolicited beat with bad SECDED
  also pulses alert_major_bus_o. Per the Q-DL-9 default, passing tests never violate the protocol;
  one directed informational test (TP-IMEM-040) demonstrates the two cases and is excluded from
  the pass gate.
- Observable at: instr_rvalid_i versus the outstanding count of the ibus monitor; rvfi_insn versus
  the memory image (shift case); alert_major_bus_o (bad-SECDED case)
- Config: none
- Source: RTL-defined: rtl/ibex_icache.sv:851-852, 947-950, 962-964, 1306-1335 (assertion block,
  no rvalid property); rtl/ibex_if_stage.sv:282 | rtl-arch MEM-19 |
  doc: doc/03_reference/load_store_unit.rst:93 (Protocol step 3: exactly one rvalid per request; by
  reference from instruction_fetch.rst:86-87)
- Edge: no
- Status: ACTIVE
- Notes: informational directed test only (Q-DL-9); the D-side counterpart is F-SEC-017/019. The
  same-cycle-as-grant case is F-IMEM-007.

---------------------------------------------------------------------------------------------------

## DMEM: data memory interface protocol and LSU

### F-DMEM-001: Request held until grant
- What: data_req_o stays high until data_gnt_i is high for one cycle (LSU states WAIT_GNT /
  WAIT_GNT_MIS keep data_req_o asserted).
- Observable at: data_req_o, data_gnt_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Data-Side Memory Interface" (data_req_o row)
  and "Protocol" step 1 | RTL: rtl/ibex_load_store_unit.sv:468-486, 489-501, 533-544
- Edge: no
- Status: ACTIVE

### F-DMEM-002: Address, we, be and wdata stable until grant
- What: While data_req_o is high and ungranted, data_addr_o, data_we_o, data_be_o and data_wdata_o
  are held. They are combinational from ID-stage operands that the ID stage holds by stalling
  (stall_mem) until lsu_req_done.
- Observable at: data_addr_o, data_we_o, data_be_o, data_wdata_o while data_req_o & ~data_gnt_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" steps 1-2 | RTL:
  rtl/ibex_load_store_unit.sv:130-132, 199-208, 719-724; rtl/ibex_id_stage.sv:1095-1096
- Edge: no
- Status: ACTIVE
- Notes: passive assertion candidate. After grant the doc explicitly allows them to change
  (F-DMEM-034).

### F-DMEM-003: data_addr_o is word aligned; the byte offset is carried by data_be_o
- What: data_addr_o[1:0] is always 2'b00 ({addr[31:2], 2'b00}); the accessed bytes within the word
  are indicated by data_be_o.
- Observable at: data_addr_o, data_be_o
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Data-Side Memory Interface" (data_addr_o
  "Address, word aligned") | RTL: rtl/ibex_load_store_unit.sv:718-722, 830 (IbexDataAddrUnaligned)
- Edge: no
- Status: ACTIVE

### F-DMEM-004: Grant in the same cycle as the request
- What: data_gnt_i in the request cycle completes the address phase immediately (IDLE with
  data_gnt_i: ctrl/addr captured, next state IDLE or WAIT_RVALID_MIS).
- Observable at: data_req_o, data_gnt_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" step 1 | RTL:
  rtl/ibex_load_store_unit.sv:478-482
- Edge: yes, of F-DMEM-001
- Status: ACTIVE

### F-DMEM-005: Grant delayed by an arbitrary number of cycles
- What: Folded into F-DMEM-001: a delayed grant is the hold scenario of F-DMEM-001 itself (Critic
  C-12 pattern c); WAIT_GNT / WAIT_GNT_MIS are carried by CG-DMEM-001.cp_gnt_delay.d4_15 / d16p and
  cr_delay_x_beat.
- Edge: yes, of F-DMEM-001
- Status: FOLDED into F-DMEM-001 (bin CG-DMEM-001.cp_gnt_delay.d16p)

### F-DMEM-006: Exactly one rvalid per granted request, at the earliest the cycle after grant
- What: data_rvalid_i is high for exactly one cycle per request, one or more cycles after the
  grant, and carries data_err_i / data_rdata_i in the same cycle. The core asserts (simulation
  only) that no rvalid arrives without an outstanding load/store.
- Observable at: data_gnt_i, data_rvalid_i, data_rdata_i, data_err_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Data-Side Memory Interface" (data_rvalid_i
  row) and "Protocol" step 3 | RTL: rtl/ibex_core.sv:1360-1391 (NoMemResponseWithoutPendingAccess);
  rtl/ibex_load_store_unit.sv:692-698
- Edge: no
- Status: ACTIVE
- Notes: TB memory model must not respond in the grant cycle.

### F-DMEM-007: rdata and err are sampled only with rvalid
- What: data_rdata_i / data_err_i are ignored unless data_rvalid_i is high (lsu_resp_valid_o and
  the rdata capture are qualified by data_rvalid_i).
- Observable at: data_rvalid_i, data_rdata_i, data_err_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Data-Side Memory Interface" (data_rvalid_i
  row) | RTL: rtl/ibex_load_store_unit.sv:509-516, 551-559, 692-698
- Edge: no
- Status: ACTIVE
- Notes: TB may randomise rdata/err when rvalid is low.

### F-DMEM-008: At most one non-split transaction outstanding; the next request may issue in the response cycle
- What: With the writeback stage, a load/store waits in WB for its response; the next load/store in
  ID may issue its request (data_req_o) in the same cycle the previous response (data_rvalid_i)
  arrives (data_req_allowed = ~outstanding_memory_access where the outstanding term is cleared by
  lsu_resp_valid). So aligned accesses never have two granted requests outstanding, but a request
  and a response can coincide.
- Observable at: data_req_o, data_rvalid_i (same cycle), data_gnt_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst intro ("stall the ID/EX stage for at least a
  cycle to await the response") | RTL: rtl/ibex_id_stage.sv:1015-1019, 1095-1096;
  rtl/ibex_wb_stage.sv:115-116, 185, 193-196; rtl/ibex_load_store_unit.sv:748-755
- Edge: no
- Status: ACTIVE
- Notes: doc/03_reference/pipeline_details.rst states its stall table applies only to the 2-stage
  pipeline; the 3-stage behaviour here is RTL-defined.

### F-DMEM-009: Two granted requests outstanding only for a split misaligned access
- What: For a split access the second beat may be granted before the first beat's rvalid arrives
  (WAIT_RVALID_MIS -> WAIT_RVALID_MIS_GNTS_DONE). This is the only way the D-side has two
  outstanding responses.
- Observable at: data_gnt_i count minus data_rvalid_i count (max 2)
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" step 4 | RTL:
  rtl/ibex_load_store_unit.sv:523-529, 546-563
- Edge: yes, of F-DMEM-008
- Status: ACTIVE

### F-DMEM-010: Responses return in request order
- What: When two requests are outstanding (split access) the memory must return the first beat's
  rvalid first; the LSU assumes order (first rvalid captures rdata_q for the low part).
- Observable at: data_rvalid_i order versus data_gnt_i order
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" step 4 | RTL:
  rtl/ibex_load_store_unit.sv:509-516, 551-559
- Edge: no
- Status: ACTIVE

### F-DMEM-011: Byte-enable pattern for word accesses
- What: Aligned word: be = 4'b1111. Misaligned word first beat: offset 1 -> 4'b1110, offset 2 ->
  4'b1100, offset 3 -> 4'b1000. Second beat: offset 1 -> 4'b0001, offset 2 -> 4'b0011, offset 3 ->
  4'b0111.
- Observable at: data_be_o with data_req_o
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:142-161
- Edge: no
- Status: ACTIVE
- Notes: the RTL comment at :154 notes the second-beat offset-0 pattern (4'b0000) is unreachable.

### F-DMEM-012: Byte-enable pattern for halfword accesses
- What: offset 0 -> 4'b0011, offset 1 -> 4'b0110, offset 2 -> 4'b1100 (single transaction each);
  offset 3 -> first beat 4'b1000, second beat 4'b0001 (split).
- Observable at: data_be_o
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:163-175
- Edge: no
- Status: ACTIVE

### F-DMEM-013: Byte-enable pattern for byte accesses
- What: one-hot lane select by offset: 4'b0001, 4'b0010, 4'b0100, 4'b1000; never split.
- Observable at: data_be_o
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:177-186, 403-405
- Edge: no
- Status: ACTIVE

### F-DMEM-014: Store write-data lane placement is a byte rotation by address offset
- What: data_wdata_o = rs2 rotated left by 8*offset bytes: offset 0 -> {b3,b2,b1,b0}; offset 1 ->
  {b2,b1,b0,b3}; offset 2 -> {b1,b0,b3,b2}; offset 3 -> {b0,b3,b2,b1}. Data is not replicated;
  the same rotated word is driven for both beats of a split store, and data_be_o selects the
  meaningful lanes.
- Observable at: data_wdata_o, data_be_o
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Load and Store Instructions"
  (norm ldst_little_endian_op, sw_sh_sb_op) | RTL: rtl/ibex_load_store_unit.sv:199-208, 219-220,
  731-738
- Edge: no
- Status: ACTIVE

### F-DMEM-015: Misaligned accesses are split into two word-aligned transactions
- What: Word accesses at offsets 1, 2, 3 and halfword accesses at offset 3 are performed as two
  word-aligned bus transactions; no address-misaligned exception is raised (mcause 4/6 are never
  produced in RV32 mode). Halfwords at offsets 0-2 and all bytes are single transactions.
- Observable at: data_req_o count per instruction (2), data_addr_o, data_be_o
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Load and Store Instructions"
  (norm misaligned_ldst_eei_dependent_behavior, misaligned_ldst_hw_support) | doc:
  doc/03_reference/load_store_unit.rst "Misaligned Accesses" | RTL:
  rtl/ibex_load_store_unit.sv:403-405, 481-484; rtl/ibex_controller.sv:899-926 (misaligned causes
  only on the CHERIoT path); rtl/ibex_pkg.sv:366-371
- Edge: no
- Status: ACTIVE

### F-DMEM-016: Second transaction address = first word-aligned address + 4
- What: For the second beat the LSU asserts addr_incr_req; the ID stage re-steers the ALU to
  addr_last + 4 (OP_A_FWD + IMM_B_INCR_ADDR) where addr_last is the word-aligned first address.
- Observable at: data_addr_o of the second request
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:346-349, 362; rtl/ibex_load_store_unit.sv:254-266,
  503-507, 533-536
- Edge: no
- Status: ACTIVE

### F-DMEM-017: Address wrap on a split access at the top of memory
- What: A misaligned access whose second word lies above 0xFFFF_FFFC (e.g. lw at 0xFFFF_FFFD..FF)
  issues its second transaction at 0x0000_0000 (32-bit ALU add wraps).
- Observable at: data_addr_o second beat = 0
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:346-349 (32-bit ALU increment); spec silent on the
  physical wrap (rv32.adoc "Load and Store Instructions" defines only the 32-bit effective address)
- Edge: yes, of F-DMEM-016
- Status: ACTIVE
- Notes: spec gap: nothing forbids the wrap; PMP checks apply to each word separately.

### F-DMEM-018: Read-data assembly for misaligned loads across two beats
- What: The first beat's data_rdata_i[31:8] is captured in rdata_q; on the second beat the word is
  reassembled: offset 1 -> {rdata2[7:0], rdata1[31:8]}, offset 2 -> {rdata2[15:0], rdata1[31:16]},
  offset 3 -> {rdata2[23:0], rdata1[31:24]}; halfword at offset 3 -> {rdata2[7:0], rdata1[31:24]}.
- Observable at: rvfi_rd_wdata, rvfi_mem_rdata
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Load and Store Instructions"
  (lw_op, lh_op, little endian) | RTL: rtl/ibex_load_store_unit.sv:230-237, 268-277, 310-316
- Edge: no
- Status: ACTIVE

### F-DMEM-019: Sign / zero extension for lb, lbu, lh, lhu at every offset
- What: Byte loads select the lane by offset and sign- or zero-extend (lsu_sign_ext); halfword loads
  at offsets 0-2 select 16 bits within the word, at offset 3 combine bytes from two beats, then
  extend from bit 15.
- Observable at: rvfi_rd_wdata
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Load and Store Instructions"
  (norm lh_op, lhu_op, lb_lbu_op) | RTL: rtl/ibex_load_store_unit.sv:283-369
- Edge: no
- Status: ACTIVE
- Notes: cross-coverage: {lb,lbu,lh,lhu,lw} x offset {0,1,2,3} x sign bit {0,1}.

### F-DMEM-020: Misaligned store data split across two beats
- What: Folded into F-DMEM-014: F-DMEM-014 already states that the same rotated word is driven on
  both beats of a split store and F-DMEM-011/012 give the per-beat lane selects (pattern c); carried
  by CG-DMEM-002.cr_be_x_beat.* and cr_size_offset_beat_we.*_first_store / *_second_store.
- Edge: yes, of F-DMEM-014
- Status: FOLDED into F-DMEM-014 (bin CG-DMEM-002.cr_be_x_beat.second_0001)

### F-DMEM-021: Bus error on the first beat of a split access
- What: If data_err_i is set on the first beat's rvalid, the second transaction is still issued and
  follows the normal protocol, but its response is ignored; the instruction takes a load/store
  access fault with mtval = the original (unaligned) effective address (addr_last is not updated on
  error).
- Observable at: data_req_o (second beat still present), rvfi_trap, mtval (unaligned address)
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Misaligned Accesses" ("second transaction will
  still be issued ... response/data will be ignored") | RTL: rtl/ibex_load_store_unit.sv:254-258,
  509-522, 540, 555-557, 688-694, 746-747; rtl/ibex_controller.sv:899-926
- Edge: yes, of F-DMEM-015
- Status: ACTIVE
- Notes: Cause-side canonical: F-EXC-030 (mtval = the original unaligned address).

### F-DMEM-022: Bus error on the second beat of a split access
- What: Bus-side view of F-EXC-031: the first beat's rvalid is clean (its rdata is captured in
  rdata_q) and data_err_i arrives on the second beat's rvalid; the access fault is raised when
  that second rvalid arrives and mtval = the word-aligned address of the second beat (addr_last
  was updated to first+4 on the successful first beat). Which beat of the pair carries the error
  decides the mtval address (contrast F-DMEM-021).
- Observable at: data_rvalid_i pair with data_err_i on the second only; rvfi_trap + csrr read-back
  of mcause/mtval (second-beat word address) on rvfi_rd_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:254-258, 519-520, 688-694, 746-747;
  rtl/ibex_controller.sv:911, 925
- Edge: yes, of F-DMEM-015
- Status: ACTIVE
- Notes: spec: machine.adoc "Machine Trap Value (mtval) Register" allows mtval to be any address
  within the faulting access for misaligned accesses; the RTL choice (first+4) is RTL-defined.

### F-DMEM-023: Both beats errored
- What: Folded into F-DMEM-015 (through F-DMEM-021): both beats errored has the same outcome as a
  first-beat error (first error wins, mtval = unaligned address, second response ignored); a row of
  the parent (pattern a); carried by CG-DMEM-004.cp_err_beat.both and cr_beat_x_mtval.both_ea.
- Edge: yes, of F-DMEM-015
- Status: FOLDED into F-DMEM-015 (bin CG-DMEM-004.cp_err_beat.both)

### F-DMEM-024: Grant delayed on the second beat of a split access
- What: If the second request is not granted when the first rvalid arrives, the FSM goes
  WAIT_RVALID_MIS -> WAIT_GNT with addr_incr_req held, keeping the second address and be stable
  until grant.
- Observable at: data_req_o, data_addr_o, data_gnt_i
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:517-522, 533-544
- Edge: yes, of F-DMEM-015
- Status: ACTIVE

### F-DMEM-025: Second grant before first rvalid (both beats in flight)
- What: Folded into F-DMEM-008 (through F-DMEM-009): the second grant before the first rvalid
  (WAIT_RVALID_MIS_GNTS_DONE, data_req_o low) is exactly the scenario F-DMEM-009 describes (pattern
  c); carried by CG-DMEM-003.cp_path.gnt2_before_rvalid1 and cp_req_low_between.yes.
- Edge: yes, of F-DMEM-008
- Status: FOLDED into F-DMEM-008 (bin CG-DMEM-003.cp_path.gnt2_before_rvalid1)

### F-DMEM-026: First rvalid and second grant in the same cycle
- What: When data_rvalid_i (first beat) and data_gnt_i (second beat) coincide in WAIT_RVALID_MIS the
  FSM returns to IDLE directly and awaits the second rvalid there.
- Observable at: data_rvalid_i & data_gnt_i same cycle
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:509-522
- Edge: yes, of F-DMEM-015
- Status: ACTIVE

### F-DMEM-027: New load/store while an abandoned second beat is outstanding is not serviced
- What: After a first-beat error the LSU still waits for the second response: load_err_o /
  store_err_o are qualified by lsu_resp_valid_o = all_resp & (ls_fsm_cs == IDLE), so the error, the
  exception and the pipeline flush to the handler all follow the FINAL (abandoned second) response
  (rtl/ibex_load_store_unit.sv:692-694, 746-747). Between the two responses WB holds the next
  request (no data_req_o); the handler's first load/store, when present, is therefore always issued
  after the second response, and the handler fetch never precedes it (X-23).
- Observable at: no data_req_o between the two rvalids; trap record at the earliest one cycle after
  the second rvalid; data_rvalid_i consumed
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Misaligned Accesses" (last sentence) | RTL:
  rtl/ibex_load_store_unit.sv:431-433, 468-470 (a new request is issued only in IDLE), 630-633, 762
- Edge: yes, of F-DMEM-015
- Status: ACTIVE

### F-DMEM-028: Load followed by a dependent instruction stalls until the load data returns
- What: Every instruction after a load/store waits in ID until the response cycle R (stall_mem:
  instr_executing needs ~outstanding_memory_access, rtl/ibex_id_stage.sv:1059-1062, 1095-1096); a
  consumer of the load's rd additionally stalls one cycle for the load-use hazard (stall_ld_hz,
  :1103-1120) because load data is not on the forwarding path (rtl/ibex_wb_stage.sv:212-215: only
  the WB-flop result rf_wdata_wb_q is forwarded). A reader of x0 after a load to x0 has no hazard
  and behaves like an independent follower (C-9).
- Observable at: rvfi_valid timing relative to the load's final data_rvalid_i R: load record R+1,
  independent or x0-reading follower R+2, dependent consumer R+3
- Config: none
- Source: RTL-defined: rtl/ibex_id_stage.sv:1103-1120; rtl/ibex_wb_stage.sv:187-196, 212-215
- Edge: no
- Status: ACTIVE

### F-DMEM-029: Store followed by a load to the same address relies on memory ordering
- What: There is no store-to-load forwarding; the load request is issued after (or in the same
  cycle as) the store response and the memory must return the stored value. In-order bus
  completion guarantees correctness.
- Observable at: data_req_o sequence, rvfi_rd_wdata of the load
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Memory Ordering Instructions"
  (single-hart program order; FENCE is a NOP in Ibex per rtl/ibex_decoder.sv:707) | RTL:
  rtl/ibex_id_stage.sv:1015-1019
- Edge: no
- Status: ACTIVE

### F-DMEM-030: Interrupt or debug request while a load/store is outstanding waits for completion
- What: The controller only enters IRQ_TAKEN / DBG_TAKEN_IF when no instruction is pending in ID or
  WB (id_wb_pending = instr_valid | ~ready_wb); a load/store in WB keeps ready_wb low until its
  rvalid. IF is halted meanwhile. The outstanding transaction therefore always completes before
  the trap, and its result (or error exception) is architecturally visible first.
- Observable at: irq_* / debug_req_i asserted during an outstanding access; rvfi order (load/store
  retires, then the trap); the entry target as the next record's rvfi_pc_rdata (C-1; the vector word
  may hit in the cache, so no ibus observation, C-14)
- Config: mstatus.mie, mie, dcsr
- Source: RTL-defined: rtl/ibex_controller.sv:296, 629-645, 700-721; rtl/ibex_wb_stage.sv:115-116,
  185
- Edge: no
- Status: ACTIVE
- Notes: edge worth its own test (TP-DMEM-036): data_err_i on that outstanding access with an IRQ
  pending: the exception wins; the ordinary IRQ is taken only after the handler's mret or an MIE
  write, because the trap entry clears mstatus.MIE (rtl/ibex_cs_registers.sv:924;
  rtl/ibex_controller.sv:490; C-6); a pending debug request enters right after the exception's
  FLUSH (not MIE-gated).

### F-DMEM-031: WFI does not sleep the core while a data access is outstanding
- What: WFI is a special_req; the controller waits for ready_wb (load/store completed) before FLUSH
  -> WAIT_SLEEP. lsu_busy (FSM not IDLE) also keeps core_busy_o On.
- Observable at: core_busy_o, data_rvalid_i before core_busy_o goes Off
- Config: none
- Source: doc: doc/02_user/integration.rst "Interfaces" (core_sleep_o: "no outstanding data or
  instruction accesses") | RTL: rtl/ibex_controller.sv:664-679, 966-967, 598-604;
  rtl/ibex_core.sv:498-521; rtl/ibex_load_store_unit.sv:762
- Edge: no
- Status: ACTIVE
- Notes: TIMING (fact-check TP-DMEM-047): the WFI stays in DECODE (retain_id) until ready_wb_i = the
  response cycle R; its RVFI record is at R+2 and ctrl_busy drops in WAIT_SLEEP at R+2 at the
  earliest; "WFI retired while the access was outstanding" is unobservable.

### F-DMEM-032: Combinational path from data_rvalid_i / data_err_i to data_req_o
- What: A load/store error response suppresses a same-cycle new request: data_err_i with rvalid sets
  wb_exception, which kills instr_executing, which gates lsu_req and thus data_req_o in the same
  cycle. The RTL relies on this so back-to-back loads need no bubble.
- Observable at: data_err_i -> data_req_o (same cycle)
- Config: none
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:748-755; rtl/ibex_controller.sv:336-337;
  rtl/ibex_id_stage.sv:732, 1033-1036, 1059-1062
- Edge: no
- Status: ACTIVE
- Notes: TB constraint: the data memory model must register data_rvalid_i/data_err_i (never derive
  them combinationally from data_req_o) or a zero-delay loop results.

### F-DMEM-033: PMP-denied data access produces no bus request
- What: Alias of F-PMP-082: DMEM perspective (data_req_o = data_req_out & ~pmp_req_err[PMP_D], so a
  denied word never appears on the bus and the LSU takes pmp_err as the response), see canonical;
  the split access whose denied first beat still lets an allowed second beat issue is F-PMP-087.
- Edge: no
- Status: ALIAS of F-PMP-082

### F-DMEM-034: Outputs may change the cycle after grant
- What: After data_gnt_i the LSU may change data_addr_o, data_we_o, data_be_o and data_wdata_o in the
  next cycle; the memory must have captured them at grant.
- Observable at: data_* outputs the cycle after data_gnt_i
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Protocol" step 2 and data_gnt_i row | RTL:
  rtl/ibex_load_store_unit.sv:719-724 (combinational outputs)
- Edge: yes, of F-DMEM-002
- Status: ACTIVE
- Notes: TB memory model must sample at req & gnt, not at rvalid time.

### F-DMEM-035: data_we_o, data_be_o and data_wdata_o are valid only with data_req_o
- What: data_we_o mirrors lsu_we_i at all times and data_be_o/data_wdata_o are combinational from
  the ID operands; their values are meaningful only in cycles where data_req_o is high. For loads
  data_be_o still marks the bytes to read; data_wdata_o[31:0] carries the rotated operand-B value
  whose payload the memory ignores (architecturally don't-care on a load). The RTL also drives a
  valid inverted 39/32 SECDED codeword in data_wdata_o[38:32] on loads; that is the RTL-defined
  observation F-DMEM-050 (coverage only), not a requirement of this feature.
- Observable at: data_we_o, data_be_o, data_wdata_o
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Data-Side Memory Interface" (we/be/wdata
  "sent together with data_req_o"; be "set for the bytes to write/read") | RTL:
  rtl/ibex_load_store_unit.sv:723-724, 737
- Edge: no
- Status: ACTIVE
- Notes: passive assertion: data_req_o |-> be pattern legal for the size/offset (F-DMEM-011..013);
  gen_chk_store_intg checks data_wdata_o[38:32] on stores only (req & gnt & we); on loads the
  encoding is recorded as coverage (F-DMEM-050), never an error.

### F-DMEM-036: Load bus error: register write suppressed, load access fault from WB
- What: Alias of F-EXC-025: DMEM perspective (data_err_i on a load response: rdata discarded, no rd
  write, cause 5 from WB), see canonical.
- Edge: no
- Status: ALIAS of F-EXC-025

### F-DMEM-037: Store bus error: store access fault from WB
- What: Alias of F-EXC-027: DMEM perspective (data_err_i on a store response, cause 7), see
  canonical.
- Edge: no
- Status: ALIAS of F-EXC-027

### F-DMEM-038: WB load/store error takes priority over exceptions of the instruction in ID
- What: Alias of F-EXC-035: DMEM perspective (WB load/store error outranks the ID exception; the
  killed ID instruction issues no data_req_o), see canonical.
- Edge: yes, of F-DMEM-036
- Status: ALIAS of F-EXC-035

### F-DMEM-039: Store response data is ignored
- What: data_rdata_i on a store's rvalid has no effect (no register write, no capture) when MemECC=0.
- Observable at: rvfi_rd_wdata / register state unchanged
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Bus Integrity Checking" ("For stores the
  response data is otherwise ignored") | RTL: rtl/ibex_load_store_unit.sv:697-698 (~data_we_q)
- Edge: no
- Status: ACTIVE

### F-DMEM-040: Loads to rd = x0 still perform the bus access and can fault
- What: The LSU has no knowledge of rd; a load with rd = x0 issues the request and, on data_err_i,
  raises a load access fault; the written value is discarded by the register file.
- Observable at: data_req_o, rvfi_trap
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Load and Store Instructions"
  (norm load_exc_x0) | RTL: rtl/ibex_load_store_unit.sv:468-486 (no rd input)
- Edge: yes, of F-DMEM-001
- Status: ACTIVE

### F-DMEM-041: Bus integrity on the data interface (MemECC only)
- What: With MemECC=1 data_wdata_o is 39 bits ({7 inverted-Hsiao check bits, 32 data}) generated
  per request, and data_rdata_i (39 bits) is checked on every rvalid for loads and stores. A
  mismatch sets load_resp_intg_err/store_resp_intg_err: alert_major_bus_o pulses, the load's
  register write is suppressed when the error is on the beat that COMPLETES the access (aligned
  response, or the second beat of a split: lsu_rdata_valid_o = IDLE & rvalid & ~err & ~we &
  ~data_intg_err, rtl/ibex_load_store_unit.sv:697-698), and an internal NMI (mcause 0xFFFFFFE0,
  mtval = faulting address) is taken within up to two ordinary records after the access's record
  (the pending flag registers one cycle after the corrupted rvalid, rtl/ibex_controller.sv:402-438;
  D21: the doc says at most one instruction). Per-beat rule (X-11, B16): a split LOAD whose FIRST
  beat alone is corrupted still writes the merged word to rd, because the first-half status
  lsu_err_d = data_bus_err_i | pmp_err_q has no integrity term (:514); alert and NMI fire as
  documented. With MemECC=0 the ports are 32 bits and none of this exists.
- Observable at: data_wdata_o[38:32], alert_major_bus_o, rvfi_ext_nmi_int, rvfi_trap/mcause in the
  NMI handler
- Config: none
- Source: doc: doc/03_reference/load_store_unit.rst "Bus Integrity Checking" | doc:
  doc/03_reference/exception_interrupts.rst "Internal Interrupts" | doc:
  doc/03_reference/security.rst "Bus integrity checking" | RTL: rtl/ibex_load_store_unit.sv:20-21,
  376-396, 697-698, 731-738, 756-757; rtl/ibex_core.sv:1353; rtl/ibex_controller.sv:393-438;
  rtl/ibex_pkg.sv:383
- Edge: no
- Status: ACTIVE
- Notes: conditional on the owner question in F-IMEM-027 (Q-002 default MemECC=1). Store
  responses need valid integrity on data_rdata_i even though the data is ignored (doc lsu
  "recommended ... fixed value"). Write-data integrity: checked on stores over all 32 bits
  (disabled lanes included); the load-side codeword is the coverage-only observation F-DMEM-050. Doc defect D17: doc/03_reference/load_store_unit.rst:34 and :52 list separate
  data_wdata_intg_o[6:0] / data_rdata_intg_i[6:0] ports; at the ibex_core boundary they are bits
  [38:32] of data_wdata_o / data_rdata_i (rtl/ibex_core.sv:84, 86); the split exists only in
  ibex_top. B16 (gen_bug_log.md, owner question Q-015): the first-beat-only split-load class is the
  expected-fail item TP-DMEM-064 (checker follows security.rst:88 "the write to the load's
  destination register will be suppressed"); the aligned and second-beat classes pass (TP-DMEM-039 /
  TP-DMEM-041) under the per-beat rule. D21: the internal-NMI latency bound is two ordinary records
  (TP-DMEM-039 is `pass (doc mismatch D21)`).

### F-DMEM-042: data_tag_o / data_tag_i (CHERIoT capability tag) are inert in RV32 mode
- What: ibex_core exposes data_tag_o (output) and data_tag_i (input). With cheriot_enable_i Off
  data_tag_o is constant 0 and data_tag_i is never consumed: in the elaborated gen_memcap_rd arm
  it feeds lsu_rcap_o only under (cheriot_enable_i == IbexMuBiOn) & resp_is_cap_q.
- Observable at: data_tag_o == 0 always
- Config: none (cheriot_enable_i tied Off by wrapper)
- Source: RTL-defined: rtl/ibex_core.sv:85, 87; rtl/ibex_load_store_unit.sv:210-220, 701-709
  (gen_memcap_rd, elaborated under BaseIsa = BaseIsaRV32IorCHERIoT; data_tag_i gated at :704-707),
  740
- Edge: no
- Status: ACTIVE
- Notes: CHERIoT carve-out; passive assertion data_tag_o == 0 is cheap.

### F-DMEM-043: CHERIoT-only LSU FSM states and capability receive FSM are unreachable (carve-out)
- What: ls_fsm_e states CTX_WAIT_GNT1, CTX_WAIT_GNT2, CTX_WAIT_RESP and the cap_rx_fsm_t machine are
  entered only when cheriot_enable_i == IbexMuBiOn and lsu_is_cap_i; in this configuration they are
  unreachable and must be excluded from FSM coverage.
- Observable at: data_req_o count per instruction never exceeds 2 and data_tag_o == 0 (F-DMEM-042)
  at the boundary; the FSM states themselves are probe candidate P4 (probe register entry needed):
  load_store_unit ls_fsm_cs never in CTX_WAIT_GNT1/CTX_WAIT_GNT2/CTX_WAIT_RESP and cap_rx_fsm_q ==
  CRX_IDLE, for the coverage exclusion and the assertions IbexLsuIsCapDisabled /
  IbexLsuCheriotErrDisabled
- Config: none
- Source: RTL-defined: rtl/ibex_pkg.sv:816-822; rtl/ibex_load_store_unit.sv:437-467, 565-603,
  611-626, 833-834
- Edge: no
- Status: ACTIVE

### F-DMEM-044: RVFI memory fields for loads and stores
- What: rvfi_mem_addr is the effective (possibly unaligned) byte address computed in the first cycle
  of the instruction; rvfi_mem_rmask/wmask are size masks (word 4'b1111, halfword 4'b0011, byte
  4'b0001) that are NOT shifted by the byte offset; rvfi_mem_wdata is the unrotated rs2 value;
  rvfi_mem_rdata is the assembled, sign/zero-extended load result.
- Observable at: rvfi_mem_addr, rvfi_mem_rmask, rvfi_mem_wmask, rvfi_mem_rdata, rvfi_mem_wdata
- Config: none
- Source: RTL-defined: rtl/ibex_core.sv:2085-2086, 2205-2228, 2253-2260
- Edge: no
- Status: ACTIVE
- Notes: the unshifted mask is a scoreboard convention to know about (do not compare it with
  data_be_o directly). The field rules apply only to decoded load/store records that did not trap:
  every non-store record carries rmask 4'b1111 and rvfi_mem_addr = the ALU result (B18, RVFI-only,
  rtl/ibex_core.sv:2085, 2253-2260), and WB-trap records have both masks zeroed
  (rtl/ibex_core.sv:2156-2157, X-15 / C-12).

### F-DMEM-045: Last data address is exposed on crash_dump_o
- What: crash_dump_o.last_data_addr = addr_last_q: updated the cycle after EVERY LSU-side grant
  (bus grant or PMP fake grant) with the unaligned effective address of a single or first-word
  access and the word-aligned second address after a second-half grant; it is NOT frozen on error
  (the handler's first data grant overwrites the erroring address); the only skipped update is the
  second-half grant that follows a first-half error (rtl/ibex_load_store_unit.sv:254-266, 478-482,
  520, 540, 743; rtl/ibex_core.sv:1328). The integration.rst wording "frozen on error" does not
  describe the RTL; the checker follows the RTL.
- Observable at: crash_dump_o.last_data_addr
- Config: none
- Source: doc: doc/02_user/integration.rst "Interfaces" (crash_dump_o row) | RTL:
  rtl/ibex_core.sv:1328; rtl/ibex_load_store_unit.sv:254-266, 743
- Edge: no
- Status: ACTIVE

### F-DMEM-046: Zcmp push/pop and cm.mvsa01/mva01s expand to multiple LSU transactions
- What: cm.push/cm.pop* are expanded in IF into a sequence of sw/lw plus stack-pointer updates, so
  one instruction produces N data transactions that must follow all protocol rules above; debug
  entry and interrupts are held off during the committing part of the sequence.
- Observable at: data_req_o burst per cm.push/pop, rvfi_ext_expanded_insn*
- Config: none
- Source: doc: doc/03_reference/pipeline_details.rst "Multi- and Single-Cycle Instructions" (Zcmp
  rows) | RTL: rtl/ibex_controller.sv:474-477, 498-500; rtl/ibex_if_stage.sv:808-809
- Edge: no
- Status: ACTIVE
- Notes: the Zc area owns the expansion semantics; listed here so protocol assertions are known
  to cover bursts and so a bus error inside a push/pop sequence gets a test. Each micro-op passes
  ID as its own instruction and produces its own RVFI record (rvfi_insn = the 32-bit expansion, the
  halfword on rvfi_ext_expanded_insn, _last on the final one; rvfi_order advances per micro-op,
  rtl/ibex_core.sv:2263-2282, X-14 / C-12): a push/pop burst is attributed to the record group,
  never to one retirement.

### F-DMEM-047: Bus error inside a Zcmp push/pop sequence
- What: Alias of F-CMP-060: DMEM perspective (a data_err_i on one expanded store of cm.push raises
  the access fault on that micro-op with mepc = the cm.push PC and sp unchanged; the popped-load
  case is F-CMP-061), see canonical.
- Edge: yes, of F-DMEM-046
- Status: ALIAS of F-CMP-060

### F-DMEM-048: Grant is legal only while a request is pending on the data bus (driver rule, passive assertion)
- What: data_gnt_i has meaning only in a cycle where the boundary data_req_o is high. The LSU takes
  any data_gnt_i it samples as a grant (IDLE :478, WAIT_GNT_MIS :495, WAIT_RVALID_MIS :518,
  WAIT_GNT :537) without checking its own request, and the boundary data_req_o is PMP-gated
  (data_req_out & ~pmp_req_err[PMP_D], rtl/ibex_core.sv:1063) while the LSU FSM keeps requesting
  internally: a grant driven against a PMP-suppressed request would be consumed as a real grant and
  desynchronise the FSM from the bus. The TB agent must derive data_gnt_i from the boundary
  data_req_o only; a passive assertion on gen_sva_dbus (data_gnt_i |-> data_req_o) enforces the
  rule as a TB-error class.
- Observable at: data_gnt_i versus data_req_o in the same cycle (assertion); PMP-denied accesses
  (PMP model) with no data_gnt_i
- Config: pmpcfg/pmpaddr (to create PMP-suppressed requests)
- Source: rtl-arch inventory (gen_interface_inventory.md section 3 driver rule 1, section 11) |
  doc: doc/03_reference/load_store_unit.rst:89 (Protocol step 1) | RTL:
  rtl/ibex_load_store_unit.sv:478, 495, 518, 537; rtl/ibex_core.sv:1063
- Edge: no
- Status: ACTIVE
- Notes: protocol assertion, no DUT checker; the I-side twin is F-IMEM-031.

### F-DMEM-049: Never drive X on data_rdata_i while rvalid (driver rule 8)
- What: The 39/32 SECDED decoder on the response path (prim_secded_inv_39_32_dec) sees an X on any
  data_rdata_i bit in an rvalid cycle as an integrity error: data_intg_err becomes set, which
  pulses alert_major_bus_o, suppresses the load's rd write and raises the internal NMI (F-DMEM-041)
  for a response that carried no real corruption. The TB agent must drive a known 39-bit value on
  every rvalid (store responses and error responses included); between responses X or random
  values are legal (F-DMEM-007). A passive assertion on gen_sva_dbus (data_rvalid_i |->
  !$isunknown(data_rdata_i)) enforces the rule as a TB-error class.
- Observable at: alert_major_bus_o stays low on every clean response; data_rdata_i known at
  data_rvalid_i (assertion)
- Config: none
- Source: rtl-arch inventory (gen_interface_inventory.md section 3 driver rule 8) | RTL:
  rtl/ibex_load_store_unit.sv:376-396 (decoder, X-pessimistic err_o), 697-698, 756-757;
  rtl/ibex_core.sv:1353
- Edge: no
- Status: ACTIVE
- Notes: the I-side has the same decoder (rtl/ibex_if_stage.sv:259-282); the imem agent obeys the
  same rule under F-IMEM-006.

### F-DMEM-050: RTL-defined observation: a valid SECDED codeword is driven on loads too; store integrity covers all 32 bits (MEM-08/MEM-15)
- What: data_wdata_o[38:32] is the inverted 39/32 Hsiao code of the full rotated 32-bit word
  data_wdata_o[31:0], computed every cycle regardless of data_be_o and data_we_o. Two consequences:
  (1) on stores the disabled lanes carry the rotated (non-zero) operand bytes and are covered by the
  check bits, so the store-integrity checker (gen_chk_store_intg, req & gnt & we) decodes the whole
  word and never a be-masked (zeroed) copy; (2) on loads the RTL drives a valid codeword over its
  (architecturally don't-care, F-DMEM-035) operand-B payload. Consequence (2) is an RTL-defined
  observation, not an architectural requirement: it is covered as
  gen_dbus_cg.cp_load_wdata_intg_valid (coverage only; plan bin
  CG-DMEM-002.cp_load_wdata_intg_valid.valid) and the store-integrity checker checks stores only
  (gen_tb_architecture.md 8.3 item 2, Critic C-10 item 4).
- Observable at: data_wdata_o[38:32] on every data_req_o (zero syndrome when decoded over
  data_wdata_o[31:0]): checked on stores, observed on loads; data_wdata_o disabled lanes non-zero on
  stores
- Config: none (MemECC=1 per Q-002 default)
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:199-208 (rotation), 219-220 (encoder input is
  the whole rotated word), 731-735 (prim_secded_inv_39_32_enc every cycle), 737 | rtl-arch MEM-08,
  MEM-15 | doc: doc/03_reference/security.rst:89 ("Write data can be checked against the supplied
  checkbits at its destination"); doc defect D17: load_store_unit.rst:34 lists a separate
  data_wdata_intg_o[6:0] port, the ibex_core boundary has one 39-bit data_wdata_o
- Edge: no
- Status: ACTIVE
- Notes: checker gen_chk_store_intg decodes the whole 39-bit word on every store request (req &
  gnt & we) and never errors on a load; the load observation is coverage only. F-DMEM-035 stands
  (load wdata payload architecturally don't-care). TP-DMEM-045 / TP-DMEM-060 pass criteria = the
  store check plus the coverage observation on loads.

### F-DMEM-051: Writeback register-write timings (EX-09)
- What: With WritebackStage=1 a non-load result is written to the register file in the WB-flop
  cycle, one cycle after the instruction leaves ID (rf_we_wb_q & wb_valid_q); a load writes in
  the cycle its data returns, directly from the LSU (rf_we_lsu = lsu_rdata_valid & outstanding
  load in WB); a store never writes; the two write sources are one-hot (assertion
  RFWriteFromOneSourceOnly). Forwarding to ID covers the WB-flop result only; a load-use is a stall
  (F-DMEM-028).
- Observable at: rvfi_valid of a load asserted exactly one cycle after its final data_rvalid_i with
  rvfi_rd_wdata = the assembled data (RVFI picks rf_wdata_lsu for loads); rvfi_rd_addr = 0 on every
  store retirement; one rvfi_valid per cycle, so a load's write and the next instruction's WB-flop
  write are reported in consecutive cycles. The WB-flop write cycle itself is probe candidate P5
  (probe register entry needed): rf_we_wb_o / rf_wdata_wb_o at the wrapper register-file seam
- Config: none
- Source: RTL-defined: rtl/ibex_wb_stage.sv:107, 115-116, 182-183, 185, 220, 310;
  rtl/ibex_core.sv:1186, 1806-1807, 1868, 1890, 2339-2356 | rtl-arch EX-09 | doc:
  doc/03_reference/pipeline_details.rst:26-30 (WB stage not documented)
- Edge: no
- Status: ACTIVE
- Notes: a direct register-file write monitor (if P5 is granted) must accept both timings.

---------------------------------------------------------------------------------------------------

## FE: instruction fetch stage (with ICache=1 the icache replaces the prefetch buffer)

### F-FE-001: Prefetch buffer and fetch FIFO are not instantiated; the icache provides the fetch buffer
- What: With ICache=1 rtl/ibex_prefetch_buffer.sv (NUM_REQS=2) and rtl/ibex_fetch_fifo.sv (DEPTH=3)
  are not in the design. Their roles (linear prefetch, request tracking, discard on branch,
  compressed realignment) are implemented by the icache's 4 fill buffers and 16-bit skid buffer.
- Observable at: instr_req_o / instr_gnt_i / instr_rvalid_i behaviour follows the icache entries
  (up to 8 outstanding beats, F-IMEM-008, versus 2 for the prefetch buffer); the structural absence
  is asserted at elaboration by gen_test_fe_structure
- Config: none
- Source: doc: doc/03_reference/instruction_fetch.rst intro ("If Ibex has been configured with an
  instruction cache ... the prefetch buffer is replaced by the icache module"; DEPTH=3) | RTL:
  rtl/ibex_if_stage.sv:298-347 (gen_icache), 348-414 (gen_prefetch_buffer, not generated);
  rtl/ibex_prefetch_buffer.sv:44; rtl/ibex_fetch_fifo.sv:44; rtl/ibex_icache.sv:72, 173-178
- Edge: no
- Status: ACTIVE
- Notes: coverage exclusion for the two modules; do not write features against them.

### F-FE-002: Reset PC and mtvec initialisation from boot_addr_i
- What: The first PC is {boot_addr_i[31:8], 8'h80}; in the same BOOT_SET cycle csr_mtvec_init writes
  mtvec = {boot_addr_i[31:8], 8'h01} (vectored mode). boot_addr_i[7:0] must be 0. No instr_req_o is
  issued while in reset or in the RESET state (rtl/ibex_controller.sv:583); the first request
  follows in BOOT_SET/FIRST_FETCH (bus-side view formerly F-IMEM-026, alias of F-RST-002).
- Observable at: instr_addr_o (first fetch), rvfi_pc_rdata of the first instruction, csrr read-back
  of mtvec on rvfi_rd_wdata
- Config: none (boot_addr_i stimulus)
- Source: spec: tools/specs/riscv-isa-manual/src/priv/machine.adoc "Reset" (norm pc_rst:
  implementation-defined reset vector) | doc: doc/03_reference/exception_interrupts.rst intro |
  RTL: rtl/ibex_if_stage.sv:243, 256, 932; rtl/ibex_cs_registers.sv:739-741;
  rtl/ibex_controller.sv:582-596
- Edge: no
- Status: ACTIVE

### F-FE-003: Boot with boot_addr_i at the top of the address space
- What: boot_addr_i = 0xFFFF_FF00 gives a first fetch at 0xFFFF_FF80 and fetching proceeds until
  the PC wraps to 0 (see F-FE-014).
- Observable at: instr_addr_o
- Config: none
- Source: RTL-defined: rtl/ibex_if_stage.sv:243
- Edge: yes, of F-FE-002
- Status: ACTIVE

### F-FE-004: Next-PC selection mux
- What: On pc_set the fetch address is chosen by pc_mux: PC_BOOT (boot vector), PC_JUMP (branch or
  jump target from EX, also used for fence.i = PC+4/2), PC_EXC (exception/interrupt vector),
  PC_ERET (mepc), PC_DRET (depc). PC_BP is never selected (BranchPredictor=0). Bit 0 of the target
  is dropped.
- Observable at: the next record's rvfi_pc_rdata (every class); rvfi_pc_wdata only for branch /
  jump / fence.i records (trap, mret and dret records carry the next sequential fetch address there:
  rtl/ibex_core.sv:2084 captures pc_if when the instruction leaves ID and their pc_set is one cycle
  later in FLUSH, X-1 / C-1); instr_addr_o only when the target misses or the cache is off (C-14)
- Config: mtvec, mepc, depc
- Source: doc: doc/03_reference/exception_interrupts.rst intro | RTL: rtl/ibex_if_stage.sv:237-253,
  287-288, 416, 922-928; rtl/ibex_pkg.sv:310-315
- Edge: no
- Status: ACTIVE

### F-FE-005: Exception and interrupt vector addresses
- What: Synchronous exceptions fetch from {mtvec[31:8], 8'h00}; interrupts fetch from
  {mtvec[31:8], 1'b0, irq_id[4:0], 2'b00} (vectored, 4 bytes per ID; internal NMI uses the NMI
  vector 31); debug entry fetches DmHaltAddr; a NON-ebreak exception inside debug mode fetches
  DmExceptionAddr (exc_pc_mux = EXC_PC_DBG_EXC); an ebreak executed in debug mode re-enters at
  DmHaltAddr regardless of dcsr.ebreakm (FLUSH -> DBG_TAKEN_ID, rtl/ibex_controller.sv:874-882,
  X-19).
- Observable at: the next record's rvfi_pc_rdata (C-1; rvfi_pc_wdata of the trapping record is the
  next sequential address, X-1); instr_addr_o only for a miss or with the cache forced off (debug
  mode), C-14
- Config: mtvec
- Source: doc: doc/03_reference/exception_interrupts.rst intro (vectored interrupts) | RTL:
  rtl/ibex_if_stage.sv:212-233; rtl/ibex_pkg.sv:328-331
- Edge: no
- Status: ACTIVE

### F-FE-006: Compressed instruction alignment: PC advances by 2 or 4
- What: The icache output address counter increments by 2 when the delivered instruction has
  rdata[1:0] != 2'b11 (compressed) and by 4 otherwise; the compressed decoder expands the 16-bit
  form so ID always sees 32-bit encodings, while the raw 16 bits are kept for mtval.
- Observable at: rvfi_pc_rdata deltas, rvfi_insn
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc "Base Instruction Formats" (IALIGN
  relaxed to 16 with C) | doc: doc/03_reference/icache.rst "Detailed behaviour" (address counter) |
  doc: doc/03_reference/instruction_fetch.rst intro | RTL: rtl/ibex_icache.sv:1103, 1136-1147;
  rtl/ibex_if_stage.sv:485-501, 608, 624
- Edge: no
- Status: ACTIVE

### F-FE-007: 32-bit instruction straddling two fetch words
- What: An uncompressed instruction at a half-word-aligned PC is assembled from the upper half of
  one word (held in the 16-bit skid buffer) and the lower half of the next word; the output is
  {word_n+1[15:0], word_n[31:16]}.
- Observable at: rvfi_insn versus memory image, instr_req_o (two words fetched)
- Config: none
- Source: doc: doc/03_reference/icache.rst "Data output" (skid buffer) and "Detailed behaviour" |
  RTL: rtl/ibex_icache.sv:1070-1133, 1165-1192
- Edge: no
- Status: ACTIVE

### F-FE-008: Straddling instruction whose second half is not yet fetched stalls
- What: valid_o is withheld while the skid buffer holds the lower half of an uncompressed
  instruction and the next word has not arrived (no error); ID sees no valid instruction until
  the second word's rvalid.
- Observable at: instr_rvalid_i to rvfi_valid latency; perf: no retirement in between
- Config: none
- Source: RTL-defined: rtl/ibex_icache.sv:1094-1101, 1129-1133
- Edge: yes, of F-FE-007
- Status: ACTIVE

### F-FE-009: Straddling instruction across a cache line boundary
- What: The two halves come from different lines (different fill buffers, possibly one hit and one
  miss, or one already errored); assembly and error attribution (err_plus2) still hold.
- Observable at: rvfi_insn, rvfi_trap/mtval on error
- Config: cpuctrlsts.icache_enable
- Source: RTL-defined: rtl/ibex_icache.sv:845-849, 1044-1063, 1094-1133, 1194-1197
- Edge: yes, of F-FE-007
- Status: ACTIVE
- Notes: cross: {hit,miss} x {hit,miss} for the two lines, x error on {none,first,second}.

### F-FE-010: Branch to a half-word-aligned target
- What: Targets with bit 1 set start output in the upper half of the fetched word; the icache loads
  the skid buffer if the instruction is uncompressed, or delivers the compressed 16 bits directly.
  addr_i[0] is always 0 (forced by IF).
- Observable at: rvfi_pc_rdata odd multiples of 2; instr_addr_o word address only when the target
  has a bus record (miss or icache_enable = 0, C-14)
- Config: none
- Source: doc: doc/03_reference/icache.rst "Detailed behaviour" (branch_i / addr_i alignment) | RTL:
  rtl/ibex_if_stage.sv:288; rtl/ibex_icache.sv:1099, 1105-1115, 1147
- Edge: yes, of F-FE-006
- Status: ACTIVE

### F-FE-011: Instruction-address-misaligned exception is impossible
- What: Alias of F-EXC-067: FE perspective (bit 0 of computed targets dropped in IF), see canonical.
- Edge: no
- Status: ALIAS of F-EXC-067

### F-FE-012: Back-pressure from ID holds the fetch output stable
- What: When ID is not ready (fetch_ready low: stall, dummy instruction insertion, Zcmp expansion),
  the icache keeps valid_o/rdata_o/addr_o/err_o stable until accepted or until branch_i; no new
  lookups are issued once all fill buffers are busy.
- Observable at: instr_req_o pauses while ID stalls; the outstanding granted fetches not yet
  retired (granted-not-consumed count of the ibus monitor) stop growing during the stall window;
  rvfi_valid gap
- Config: none
- Source: doc: doc/03_reference/icache.rst "Detailed behaviour" (ready/valid handshake) | RTL:
  rtl/ibex_if_stage.sv:808-809; rtl/ibex_icache.sv:249, 1101, 1136
- Edge: no
- Status: ACTIVE
- Notes: a CSR write with pipeline flush holds IF for exactly 2 cycles (DECODE(special_req) + one
  FLUSH cycle, no pc_set, rtl/ibex_controller.sv:232, 287, 815-818; rtl/ibex_id_stage.sv:593-597);
  longer back-pressure windows come from the other causes.

### F-FE-013: Pipeline flush on any PC redirect discards buffered instructions
- What: pc_set (branch, jump, exception, interrupt, mret, dret, debug entry/exit, fence.i) asserts
  branch_i to the icache: the skid buffer is invalidated, all fill buffers become stale, the output
  address is set to the target, and the instruction currently entering ID is squashed.
- Observable at: rvfi_pc_rdata continuity (no stale instruction retires), instr_addr_o jumps to the
  target
- Config: none
- Source: doc: doc/03_reference/instruction_fetch.rst intro ("flushing it on
  branches/jumps/exception") | RTL: rtl/ibex_if_stage.sv:287-288, 418, 568-570;
  rtl/ibex_icache.sv:741, 1105-1107, 1147
- Edge: no
- Status: ACTIVE

### F-FE-014: PC wrap-around at the top of the address space
- What: A compressed instruction at 0xFFFF_FFFE (or an uncompressed one at 0xFFFF_FFFC) is followed
  by PC 0x0000_0000; the icache output counter is a 31-bit adder over addr[31:1] and wraps. An
  uncompressed instruction at 0xFFFF_FFFE needs the word at 0x0000_0000 as its second half and is
  followed by PC 0x0000_0002 (0x7FFF_FFFF + 2 in 31 bits = 1, rtl/ibex_icache.sv:1139-1147); the
  bus sequence is 0xFFFF_FFFC then 0x0000_0000 in all three cases.
- Observable at: rvfi_pc_rdata sequence, instr_addr_o (0xFFFFFFFC then 0x00000000)
- Config: none
- Source: RTL-defined: rtl/ibex_icache.sv:1142-1147; rtl/ibex_if_stage.sv:679 (PC increment check
  also wraps)
- Edge: yes, of F-FE-006
- Status: ACTIVE
- Notes: spec gap: the unprivileged spec does not define fetch wrap behaviour.

### F-FE-015: Fetch error: instruction is delivered to ID marked errored and not decoded/executed
- What: An errored word still moves into ID (with instr_fetch_err); the compressed decoder is not
  enabled for it, register reads are suppressed, and the controller raises the exception. rdata is
  unspecified for errored fetches.
- Observable at: rvfi_trap, absence of side effects
- Config: none
- Source: doc: doc/03_reference/icache.rst "Detailed behaviour" (rdata_o unspecified on err_o) |
  RTL: rtl/ibex_if_stage.sv:492, 606, 622; rtl/ibex_id_stage.sv:291-292, 1033
- Edge: no
- Status: ACTIVE

### F-FE-016: PMP fault on instruction fetch, including the +2 check for straddling instructions
- What: Alias of F-PMP-067: FE perspective (the PMP_I2 channel checks pc_if + 2 for an uncompressed
  instruction at 4n+2; a denied second half faults with err_plus2 and mtval = pc + 2 unless the
  first half is also denied, F-PMP-069; a compressed instruction ignores the +2 check), see
  canonical.
- Edge: yes, of F-IMEM-011
- Status: ALIAS of F-PMP-067

### F-FE-017: Speculative prefetch depth beyond the executed stream
- What: The icache prefetches linearly ahead of ID. The lookup throttle (lookup_throttle =
  fb_fill_level > FB_THRESHOLD with FB_THRESHOLD = NUM_FB - 2 = 2, where fb_fill_level counts the
  busy non-stale fill buffers including the line currently being output) lets linear prefetch hold
  at most 3 fill buffers: the line being output plus 2 lines ahead, i.e. up to 16 bytes (4 words)
  beyond the line being consumed and at most 6 granted words that a redirect can discard. The 4th
  buffer is allocated only by a branch lookup, which bypasses the throttle (F-IMEM-008 reaches its
  8-beat bound that way). Prefetched words are discarded on redirect.
- Observable at: instr_addr_o beyond a taken branch/exception PC: sequential grants lead the line of
  the word being consumed into ID by at most 3 lines; against the last retired rvfi_pc_rdata the
  lead is transiently 4 while a load/store is stalled in WB (the record lags ID consumption by that
  wait; TIMING, fact-check TP-FE-013 / TP-IC-051) and never 5; granted-not-executed words per
  redirect (ibus monitor) at most 6
- Config: none
- Source: doc: doc/03_reference/instruction_fetch.rst intro ("fetches instructions linearly until it
  is full") | RTL: rtl/ibex_icache.sv:72-74 (FB_THRESHOLD), 211-224, 247-250 (lookup_throttle),
  690-697 (fb_fill_level counts busy & ~stale)
- Edge: no
- Status: ACTIVE
- Notes: the TB memory must serve any address the prefetcher reaches (including past the end of
  the program image); errors there are speculative (F-IMEM-012 / F-EXC-006). Depth bins derived
  from 4 lines are unreachable for linear prefetch (Critic C-05); the 4-busy-buffer state is
  covered separately through the branch path (CG-IC-004.cp_busy_buffers.b4).

### F-FE-018: Dummy instruction insertion point
- What: With cpuctrlsts.dummy_instr_en, dummy instructions are multiplexed between the fetch output
  and the IF/ID register; they are not fetched from memory, take the PC of the next real
  instruction, and stall the fetch output for one cycle.
- Observable at: rvfi (dummies are not reported), instr_req_o unaffected
- Config: cpuctrlsts.dummy_instr_en, cpuctrlsts.dummy_instr_mask
- Source: RTL-defined: rtl/ibex_if_stage.sv:503-545
- Edge: no
- Status: ACTIVE
- Notes: DIT/security area owns the semantics; listed to mark the insertion point relative to the
  fetch stream.

### F-FE-019: Branch predictor residual logic (BranchPredictor=0)
- What: predict_branch_taken is tied to 0, pc_mux_internal = pc_mux_i, if_instr_* come straight from
  the icache, nt_branch_mispredict_i is never asserted and instr_bp_taken_o is 0.
- Observable at: instr_addr_o never redirects without a matching rvfi_pc_wdata change (no
  predicted-taken speculation on the bus); rvfi_pc_wdata
- Config: none
- Source: doc: doc/03_reference/instruction_fetch.rst "Branch Prediction" | RTL:
  rtl/ibex_if_stage.sv:237-238, 287-296, 799-810
- Edge: no
- Status: ACTIVE
- Notes: coverage exclusion for g_branch_predictor.

### F-FE-020: Sequential PC increment check (PCIncrCheck = SecureIbex)
- What: Alias of F-SEC-007: FE perspective (sequential PC increment check in IF), see canonical.
- Edge: no
- Status: ALIAS of F-SEC-007

### F-FE-021: Wake from WFI resumes fetch at the instruction after WFI
- What: In SLEEP the controller holds instr_req low; an interrupt line enabled in mie (regardless of
  mstatus.MIE), an NMI, a debug request, or being in debug mode moves to FIRST_FETCH and fetch
  resumes with the already-buffered next instruction (no re-fetch of the WFI; FIRST_FETCH drives
  req_i for one cycle, so a sequential prefetch may precede the redirect). A WFI with dcsr.step = 1
  outside debug mode never sleeps: FLUSH goes to DBG_TAKEN_IF (rtl/ibex_controller.sv:462, 474-475,
  985-987) and the debug ROM is entered with dpc = WFI + len and no ctrl_busy dip (C-5). A WFI
  executed in debug mode passes WAIT_SLEEP and SLEEP exits at once on debug_mode_q (wfi = nop), so
  WFI + len retires next.
- Observable at: instr_req_o resumes, rvfi_pc_rdata of the next retirement (handler, WFI+len, or
  DmHaltAddr with dpc == WFI+len for the stepped case)
- Config: mstatus.mie, mie, dcsr.step
- Source: spec: tools/specs/riscv-isa-manual/src/priv/machine.adoc "Wait for Interrupt" | RTL:
  rtl/ibex_controller.sv:598-627
- Edge: yes, of F-IMEM-021
- Status: ACTIVE

### F-FE-022: Fetch in debug mode bypasses the cache
- What: Alias of F-IC-040: FE perspective (every debug-mode fetch reaches instr_req_o), see
  canonical.
- Edge: yes, of F-IC-012
- Status: ALIAS of F-IC-040
- Notes: in the dret (FLUSH) cycle debug_mode_i is still 1, so the depc line is looked up
  pass-through, fetched from the bus from the target word to the line end and not allocated
  (rtl/ibex_cs_registers.sv:1970-1971; rtl/ibex_controller.sv:960-964; rtl/ibex_icache.sv:266, 683,
  703, 771-773); hits resume with the next line (TP-FE-022 / TP-IC-030 exempt the depc line).

### F-FE-023: After a fetch error the next fetch is the trap vector
- What: Folded into F-IMEM-011: the redirect to the vector after a fetch fault is the parent's own
  consequence (rvfi_pc_wdata = vector), a checker bullet without a distinct stimulus (pattern d);
  carried by CG-FE-005.cp_next_fetch.exc_vector / dm_exception_addr.
- Edge: yes, of F-IMEM-011
- Status: FOLDED into F-IMEM-011 (bin CG-FE-005.cp_next_fetch.exc_vector)
- Notes: the vector is observed as the next record's rvfi_pc_rdata (C-1); outside debug mode the
  vector word may hit and stale beats of open lines may follow the redirect on the bus, so no ibus
  clause (C-14); in debug mode DmExceptionAddr is always bus-visible.

### F-FE-024: Zcmp expansion holds the fetch interface
- What: Folded into F-FE-012: Zcmp expansion is one of the fetch_ready-low causes F-FE-012
  enumerates (pattern a); carried by CG-FE-004.cp_cause.zcmp_expand and
  cr_cause_x_buffered.zcmp_full.
- Edge: yes, of F-FE-012
- Status: FOLDED into F-FE-012 (bin CG-FE-004.cp_cause.zcmp_expand)

### F-FE-025: Instruction fetch after a taken branch appears on the bus in the redirect cycle
- What: With BranchTargetALU=1 the target is available in the branch's first ID cycle; pc_set and
  branch_i occur in that cycle and (when no external request is pending) the target word address
  appears on instr_addr_o with instr_req_o in the same cycle.
- Observable at: instr_req_o/instr_addr_o relative to the branch's rvfi_valid
- Config: none
- Source: doc: doc/03_reference/pipeline_details.rst "Multi- and Single-Cycle Instructions" (Jump,
  Branch (Taken) rows) | RTL: rtl/ibex_icache.sv:703-705, 1030-1037
- Edge: no
- Status: ACTIVE
- Notes: the same-cycle request is the speculative branch request fill_spec_req = branch_i &
  ~|fill_ext_req: it exists only when no fill buffer has an ungranted request; a target that hits
  never issues the deferred request (fill_ext_done_d via fill_hit_ic1, rtl/ibex_icache.sv:767-769),
  so the deferred class is observable only on a miss or with icache_enable = 0 (C-14).

---------------------------------------------------------------------------------------------------

## IC: instruction cache (ICache=1, ICacheECC=1, ICacheScramble=1) at the ibex_core boundary

### F-IC-001: Cache geometry and RAM port widths
- What: 4 KiB, 2 ways, 256 lines per way, 64-bit lines (2 beats). Index = addr[10:3], tag =
  addr[31:11] plus a valid bit (22 bits). At the ibex_core boundary: ic_tag_req_o[1:0],
  ic_tag_write_o, ic_tag_addr_o[7:0], ic_tag_wdata_o[27:0] (22 + 6 ECC), ic_tag_rdata_i[2][27:0];
  ic_data_req_o[1:0], ic_data_write_o, ic_data_addr_o[7:0], ic_data_wdata_o[77:0] (2 x (32 + 7
  ECC)), ic_data_rdata_i[2][77:0].
- Observable at: the ic_* ports (widths, index range)
- Config: none
- Source: doc: doc/03_reference/icache.rst "RAM Arrangement" and "Cache ECC protection" | RTL:
  rtl/ibex_pkg.sv:395-416; rtl/ibex_top.sv:221-225; rtl/ibex_core.sv:104-116
- Edge: no
- Status: ACTIVE
- Notes: doc defect D9: doc/03_reference/icache.rst:202-208 "Cache ECC protection" shows the data
  RAM as 72 bits (checkbits [71:64]); the RTL uses two independent 39/32 codes (78 bits,
  checkbits per 32-bit beat: [38:32] and [77:71]).

### F-IC-002: Tag RAM read protocol: request in IC0, data used in IC1 (one-cycle synchronous RAM)
- What: A lookup asserts ic_tag_req_o for all ways with ic_tag_write_o low and the index; the core
  uses ic_tag_rdata_i in the following cycle (tag compare in IC1). The TB RAM model must be a
  synchronous single-cycle-latency RAM.
- Observable at: ic_tag_req_o, ic_tag_addr_o, ic_tag_rdata_i (next cycle)
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Cache Pipeline" | RTL: rtl/ibex_icache.sv:269-277,
  445-456, 466-491, 497-504
- Edge: no
- Status: ACTIVE

### F-IC-003: Data RAM read protocol
- What: In parallel with the tag read, ic_data_req_o is asserted for all ways with the same index;
  ic_data_rdata_i of the hitting way is used in IC1 (hit_data mux). The RAM model latency rule is
  the same as F-IC-002.
- Observable at: ic_data_req_o, ic_data_addr_o, ic_data_rdata_i
- Config: cpuctrlsts.icache_enable = 1
- Source: RTL-defined: rtl/ibex_icache.sv:280-283, 459-464, 506-514
- Edge: no
- Status: ACTIVE

### F-IC-004: Tag RAM reads happen even with the cache disabled (result masked); none during the invalidation sweep
- What: tag_req_ic0 includes every lookup regardless of icache_enable; lookup_actual (which makes
  IC1 consider the result) is gated by icache_enable and ~inval_block_cache. So ic_tag_req_o /
  ic_data_req_o pulse on every lookup in pass-through mode and in OUT_OF_RESET / AWAIT_SCRAMBLE_KEY.
  During INVAL_CACHE no lookup read happens: every tag-port and data-port cycle of the sweep is a
  write at the inval index (tag_write_ic0 = fill_grant | inval_write_req | ecc_write_req,
  data_write_ic0 = tag_write_ic0, rtl/ibex_icache.sv:269-283, 1244; a coinciding lookup only makes
  the data port write ECC(0), F-IC-028).
- Observable at: ic_tag_req_o, ic_data_req_o with cpuctrlsts.icache_enable = 0
- Config: cpuctrlsts.icache_enable
- Source: RTL-defined: rtl/ibex_icache.sv:249-250, 266, 269, 280, 466-470
- Edge: yes, of F-IC-002
- Status: ACTIVE
- Notes: a passive checker "no RAM reads when cache disabled" would be wrong.

### F-IC-005: Fill write protocol: one way, tag and data written together
- What: An allocation asserts ic_tag_req_o and ic_data_req_o for the selected way only, with
  ic_tag_write_o and ic_data_write_o high, the line index, the ECC-encoded {valid=1, tag} and the
  ECC-encoded 64-bit line. Fill writes lose arbitration to lookups, invalidation writes and ECC
  correction writes.
- Observable at: ic_tag_req_o (one-hot), ic_tag_write_o, ic_tag_wdata_o, ic_data_write_o,
  ic_data_wdata_o
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Cache Pipeline" (arbitration) | RTL:
  rtl/ibex_icache.sv:255-283, 815-823, 843-844, 999-1011
- Edge: no
- Status: ACTIVE

### F-IC-006: ECC encoding of tag and data writes
- What: Tag: {valid, tag[20:0]} zero-padded to 22 bits, encoded with the inverted 28/22 Hsiao code;
  wdata = {6 checkbits, 22 bits}. Data: each 32-bit beat encoded with the inverted 39/32 Hsiao code;
  wdata = {beat1[38:0], beat0[38:0]}.
- Observable at: ic_tag_wdata_o, ic_data_wdata_o (checkable against
  vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_28_22_enc.sv and prim_secded_inv_39_32_enc.sv)
- Config: none
- Source: RTL-defined: rtl/ibex_icache.sv:286-315; rtl/ibex_top.sv:221-223 (BusSizeECC = 39,
  LineSizeECC = 78) | doc defect D9: doc/03_reference/icache.rst:202-208 says a 72-bit data word
  with checkbits [71:64] over data [63:0]; the RTL writes two 39-bit codewords (the tag layout at
  icache.rst:194-200 matches the RTL)
- Edge: no
- Status: ACTIVE
- Notes: with ICacheTweakInfection=1 the written value is additionally XORed (F-IC-007): tag tweak
  = the index at bits [7:0] and [21:14] of the 28-bit codeword, data tweak = the line-aligned
  address on the 32 data bits of each beat (bits [31:0] and [70:39]); ECC bits are never tweaked.

### F-IC-007: Tweak infection XORs address-derived tweaks into RAM write/read data (ICacheTweakInfection)
- What: If ICacheTweakInfection=1 (ibex_top sets it = SecureIbex), tag write data is XORed with the
  IC_INDEX_W-bit tag index placed at bits [7:0] and [21:14] of the 28-bit tag codeword (ECC bits
  untouched, rtl/ibex_icache.sv:389-396), and data write data with the 32-bit line-aligned address
  {addr[31:3], 3'b0} XORed onto the 32 data bits of each 39-bit beat codeword (bits [31:0] and
  [70:39] of the 78-bit word, :329-347); invalidation and ECC-correction writes use tweak 0; the
  same XOR (from the IC0 address / index registered one cycle) is undone on read before ECC
  checking (:361-368, 406-423). If 0, no XOR.
- Observable at: ic_tag_wdata_o, ic_data_wdata_o (not a plain ECC codeword when enabled)
- Config: none
- Source: doc: doc/03_reference/security.rst "ICache Tweak Infection" | RTL:
  rtl/ibex_icache.sv:321-438, 450, 455, 464, 511; rtl/ibex_top.sv:45
- Edge: no
- Status: ACTIVE
- Notes: OWNER QUESTION (same as F-IMEM-027): the wrapper must set ICacheTweakInfection explicitly.
  A transparent TB RAM model is unaffected; an ECC-checking RAM monitor must undo the tweak.

### F-IC-008: Scramble-key request handshake at the core boundary
- What: ic_scr_key_req_o is a one-cycle pulse issued (a) in the first cycle out of reset if
  ic_scr_key_valid_i is low, and (b) on every icache_inval_i (fence.i) seen in INVAL_IDLE or
  INVAL_CACHE. After a request the icache waits in AWAIT_SCRAMBLE_KEY until ic_scr_key_valid_i is
  high, then starts invalidation. Requests are not re-issued while waiting.
- Observable at: ic_scr_key_req_o, ic_scr_key_valid_i
- Config: none
- Source: doc: doc/03_reference/icache.rst "ICache Scrambling" and "Scramble Key Renewal" | RTL:
  rtl/ibex_icache.sv:1203-1280
- Edge: no
- Status: ACTIVE
- Notes: reference for the TB key agent: rtl/ibex_top.sv:628-655 drops key_valid on the request and
  holds scramble_req_o until a new key arrives; the TB must latch the single-cycle pulse and may
  hold ic_scr_key_valid_i low for a random number of cycles before re-asserting it.

### F-IC-009: No key request at reset if the key is already valid
- What: Folded into F-IC-008: F-IC-008 already states the request is issued at reset only if
  ic_scr_key_valid_i is low; the valid-high case is the other row of that condition (pattern a);
  carried by CG-IC-002.cp_key_req_at_reset.skipped_valid_high.
- Edge: yes, of F-IC-008
- Status: FOLDED into F-IC-008 (bin CG-IC-002.cp_key_req_at_reset.skipped_valid_high)

### F-IC-010: Key never re-validated after a request: cache stays uninitialised, fetch continues uncached
- What: If ic_scr_key_valid_i stays low after a request, the invalidation FSM stays in
  AWAIT_SCRAMBLE_KEY forever: every lookup is a miss, nothing is allocated, busy_o stays high, and
  instruction fetch and execution proceed from the bus indefinitely.
- Observable at: instr_req_o (all fetches), ic_tag_write_o (none), core_busy_o (never Off)
- Config: none
- Source: doc: doc/03_reference/icache.rst "Scramble Key Renewal" ("cache lookups will always
  miss until the invalidation is complete") | RTL: rtl/ibex_icache.sv:266, 683, 1215-1218,
  1229-1240, 1304
- Edge: yes, of F-IC-008
- Status: ACTIVE

### F-IC-011: ic_scr_key_valid_i is mirrored into cpuctrlsts.ic_scr_key_valid every cycle
- What: cpuctrlsts[8] reads the registered value of ic_scr_key_valid_i (sampled every cycle, read
  only); it is also exported as rvfi_ext_ic_scr_key_valid.
- Observable at: csrr cpuctrlsts (rvfi_rd_wdata bit 8), rvfi_ext_ic_scr_key_valid
- Config: none
- Source: doc: doc/03_reference/cs_registers.rst "CPU Control and Status Register (cpuctrlsts)"
  (bit 8) | RTL: rtl/ibex_cs_registers.sv:666-670, 1936-1949; rtl/ibex_core.sv:176, 2103
- Edge: no
- Status: ACTIVE
- Notes: software contract (doc): issue fence.i only when this bit reads 1 to guarantee a new key.
  Doc defect D13: doc/03_reference/cs_registers.rst:544-545 says "a fence.i instruction is
  guaranteed to fetch a new key"; doc/03_reference/icache.rst:113-116 and the RTL
  (rtl/ibex_icache.sv:1229-1240) ignore a fence.i that arrives while a key request is pending
  (F-IC-024), so the guarantee holds only when this bit reads 1.

### F-IC-012: icache_enable: reset 0 (cache off), M-mode-only WARL bit
- What: cpuctrlsts[0] resets to 0 so the cache starts in pass-through; software enables it with a
  CSR write (cpuctrlsts is 0x7C0, machine mode only; U-mode access is an illegal instruction).
  The bit is masked to 0 while in debug mode.
- Observable at: instr_req_o per fetch (pass-through) versus cache hits (no request); csrr
  cpuctrlsts
- Config: cpuctrlsts.icache_enable, privilege mode
- Source: doc: doc/03_reference/cs_registers.rst "CPU Control and Status Register (cpuctrlsts)"
  (reset value, bit 0, "Accessible in Machine Mode only") | doc: doc/03_reference/icache.rst
  "High-level operation" | RTL: rtl/ibex_cs_registers.sv:874-877, 1935-1937, 1970-1984;
  rtl/ibex_pkg.sv:692
- Edge: no
- Status: ACTIVE

### F-IC-013: Pass-through mode (icache_enable = 0)
- What: Every lookup issues an external request (speculative request in parallel with the masked
  lookup); nothing is allocated; fetched data is discarded after use or on a branch. Fetch beats
  stop at the line end (no wrap).
- Observable at: instr_req_o for every word executed, ic_tag_write_o absent
- Config: cpuctrlsts.icache_enable = 0
- Source: doc: doc/03_reference/icache.rst "High-level operation" and "Detailed behaviour"
  (icache_enable_i paragraph) | RTL: rtl/ibex_icache.sv:266, 683, 703, 767-775, 1030-1031
- Edge: no
- Status: ACTIVE

### F-IC-014: Enabled: misses allocate, hits are served from RAM without a bus request
- What: With icache_enable = 1 and invalidation idle, a miss fills the line (2 beats) and allocates
  it once all beats are received without error; a later lookup of the line hits in IC1 and needs
  no external request (except the speculative branch request of F-IC-023).
- Observable at: instr_req_o absent on hits (sequential code re-executed in a loop),
  ic_tag_write_o/ic_data_write_o on allocation
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Fill buffers" and "Data output" | RTL:
  rtl/ibex_icache.sv:497-504, 683, 744-749, 815-823, 942-943
- Edge: no
- Status: ACTIVE

### F-IC-015: Hit data timing: first word in IC1, remaining beat from the fill buffer
- What: Folded into F-IC-014: hit data timing (first word from IC1, other beat from the fill buffer)
  is a timing detail of the parent's hit path with no distinct stimulus (pattern d); carried by
  CG-IC-003.cp_hit_cadence.run2_3 / run4p and cp_hit_bus_traffic.none.
- Edge: yes, of F-IC-014
- Status: FOLDED into F-IC-014 (bin CG-IC-003.cp_hit_cadence.run4p)

### F-IC-016: Miss data timing: demand beat forwarded directly from the bus
- What: Folded into F-IC-014: forwarding the demanded beat from the bus is a timing detail of the
  parent's miss path with no distinct stimulus (pattern d); carried by
  CG-IC-003.cp_miss_forward_latency (minimum 3 cycles from the demanded beat's rvalid to
  rvfi_valid: IF output R, ID R+1, WB R+2, record R+3; TIMING, fact-check TP-IC-020).
- Edge: yes, of F-IC-014
- Status: FOLDED into F-IC-014 (bin CG-IC-003.cp_miss_forward_latency.l3)

### F-IC-017: Way selection: first invalid way, else round-robin
- What: The victim is the lowest-numbered invalid way at that index; if both ways are valid, a
  global one-hot round-robin pointer selects the way. The pointer rotates on every valid lookup
  (not only on allocations) and resets to way 0.
- Observable at: ic_tag_req_o one-hot pattern on fills
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Cache Pipeline" ("victim way is chosen
  pseudo-randomly using a counter") | RTL: rtl/ibex_icache.sv:516-535, 913-938
- Edge: no
- Status: ACTIVE
- Notes: not an LFSR; the doc wording "pseudo-random" is a global rotating pointer in the RTL.

### F-IC-018: Cache full at an index (both ways valid): round-robin victim replaced
- What: Folded into F-IC-017: the both-ways-valid row is already in F-IC-017's selection rule
  (pattern a); carried by CG-IC-003.cr_result_x_fill.evict_both, cp_victim.rr_way0 / rr_way1 and
  cp_all_lines_valid.yes (stride-2-KiB loop stimulus in TP-IC-022).
- Edge: yes, of F-IC-017
- Status: FOLDED into F-IC-017 (bin CG-IC-003.cr_result_x_fill.evict_both)

### F-IC-019: Line fill order and allocation only after both beats
- What: A fill issues both beats (wrapping, F-IMEM-019) and requests the RAM write only when
  fill_rvd_cnt reaches 2, no beat errored, the buffer still allocates, and it did not hit.
- Observable at: two instr_gnt_i then ic_tag_write_o
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Fill buffers" | RTL: rtl/ibex_icache.sv:815-823,
  830-835
- Edge: no
- Status: ACTIVE

### F-IC-020: Branch redirect during a fill: fill completes and (if allocating) is still written
- What: A fill buffer that already issued external requests when branch_i arrives is marked stale:
  its output is suppressed, but it still receives its beats and, if it was allocating, still
  writes the line into the cache. A buffer with no external request yet is released without any
  bus traffic only when it will NOT be cached (cache disabled or invalidation active); a caching
  buffer whose lookup preceded the branch fetches both beats and is allocated even with no grant yet
  (fill_ext_done_d cancels only when ~fill_cache_q, rtl/ibex_icache.sv:741, 744-746, 767-775).
- Observable at: instr_rvalid_i after redirect, ic_tag_write_o for a line never executed
- Config: cpuctrlsts.icache_enable
- Source: doc: doc/03_reference/icache.rst "Fill buffers" | RTL: rtl/ibex_icache.sv:729-734, 741,
  767-775, 796
- Edge: yes, of F-IC-019
- Status: ACTIVE

### F-IC-021: Same line allocated in both ways after a branch into a line being prefetched
- What: If the core branches to an address whose line is currently being filled by a stale-able
  buffer, a second buffer for the same line can be allocated. Each buffer captures its way at its
  own IC1 (fill_way_q <= sel_way_ic1): with an invalid way at the index both pick the same lowest
  invalid way and the second fill overwrites the first (one copy); two copies in different ways need
  both ways already valid at that index (round-robin) and an odd number of valid lookups between
  the two lookups (the pointer rotates on every lookup_valid_ic1, rtl/ibex_icache.sv:519-535, 914,
  932-938). A later multi-way hit ORs both ways, harmless when contents match.
- Observable at: two ic_tag_write_o for the same tag/index in different ways
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Performance notes" (second paragraph) and "Detailed
  behaviour" (last paragraph) | RTL: rtl/ibex_icache.sv:506-514, 699-700
- Edge: yes, of F-IC-019
- Status: ACTIVE
- Notes: with self-modifying code without fence.i the two copies may differ; software constraint
  per doc, not a DUT check.

### F-IC-022: Invalidation at reset: cache unusable until 256 tag writes complete
- What: Out of reset (after the key is valid) the icache writes an invalid tag (valid = 0, ECC
  correct) to every index for all ways, one index per cycle (256 cycles), with ic_tag_write_o high
  and both ic_tag_req_o bits set. Lookups during this time are treated as misses and nothing is
  allocated; fetch proceeds from the bus. The minimum from reset release to INVAL_IDLE is 258
  cycles: 1 (OUT_OF_RESET) + 1 (AWAIT_SCRAMBLE_KEY with the key already valid) + 256 tag writes
  (MEM-23); the first fill write needs a lookup in INVAL_IDLE (inval_block_cache clears only there,
  rtl/ibex_icache.sv:1218, 1265), an IC1 miss, two grants and rvalids and a RAM cycle free of
  lookups, so it lands >= 5 cycles after the last inval write (not before cycle 262 after reset
  release, reset release = cycle 0), and any key delay adds to it.
- Observable at: ic_tag_req_o = 2'b11, ic_tag_write_o, ic_tag_addr_o counting 0..255,
  ic_tag_wdata_o (valid bit 0), instr_req_o for all fetches meanwhile; first fill write no earlier
  than 262 cycles after reset release (>= 5 cycles after the last inval write)
- Config: none
- Source: doc: doc/03_reference/icache.rst "Cache invalidation" and "Detailed behaviour"
  (icache_inval_i paragraph) | RTL: rtl/ibex_icache.sv:255-258, 269-277, 1203-1257 (FSM
  OUT_OF_RESET :1221-1228, AWAIT_SCRAMBLE_KEY :1229-1240, INVAL_CACHE :1241-1255)
- Edge: no
- Status: ACTIVE
- Notes: TB RAM model must accept writes before any read; tag RAM contents before init are never
  used (lookup_valid_ic1 = 0), so X in an uninitialised tag RAM is safe.

### F-IC-023: fence.i requests a new key and re-invalidates the whole cache
- What: fence.i is decoded as a jump to the next PC plus a one-cycle icache_inval pulse. The
  icache pulses ic_scr_key_req_o, waits for ic_scr_key_valid_i, then rewrites all 256 tags
  invalid. Cache lookups miss until the invalidation completes; the jump flushes the fetch buffers
  so the instruction after fence.i is re-fetched from memory.
- Observable at: ic_scr_key_req_o, ic_tag_write_o burst, instr_req_o for the next PC, rvfi order
- Config: none
- Source: spec: tools/specs/riscv-isa-manual/src/unpriv/zifencei.adoc (norm fence_i_op) | doc:
  doc/03_reference/pipeline_details.rst (Instruction Fence row) | doc: doc/03_reference/icache.rst
  "Scramble Key Renewal" | RTL: rtl/ibex_decoder.sv:711-722, 1406-1415;
  rtl/ibex_id_stage.sv:52, 498; rtl/ibex_icache.sv:1258-1267
- Edge: no
- Status: ACTIVE
- Notes: correctness test: store new code, fence.i, execute it; without fence.i the stale line
  may execute (F-IC-021 note).

### F-IC-024: fence.i while a key request is outstanding is ignored
- What: An icache_inval_i arriving in AWAIT_SCRAMBLE_KEY has no effect (no second request); the
  current request/invalidation proceeds.
- Observable at: ic_scr_key_req_o (single pulse for two fence.i)
- Config: none
- Source: doc: doc/03_reference/icache.rst "Scramble Key Renewal" (case 1) | RTL:
  rtl/ibex_icache.sv:1229-1240
- Edge: yes, of F-IC-023
- Status: ACTIVE
- Notes: doc defect D13: doc/03_reference/cs_registers.rst:544-545 ("a fence.i instruction is
  guaranteed to fetch a new key") contradicts this behaviour and icache.rst:113-116; the RTL follows
  icache.rst.

### F-IC-025: fence.i during an in-progress invalidation restarts it with a new key
- What: An icache_inval_i arriving in INVAL_CACHE issues a new ic_scr_key_req_o, returns to
  AWAIT_SCRAMBLE_KEY and, once the key is valid, restarts the tag rewrite from index 0.
- Observable at: ic_scr_key_req_o second pulse, ic_tag_addr_o restarting at 0
- Config: none
- Source: doc: doc/03_reference/icache.rst "Scramble Key Renewal" (case 2) | RTL:
  rtl/ibex_icache.sv:1241-1257
- Edge: yes, of F-IC-023
- Status: ACTIVE

### F-IC-026: Invalidation while a fill is outstanding stops its allocation
- What: icache_inval_i clears fill_cache for busy fill buffers so lines whose fills complete during
  or after the invalidation request are not written into the cache; the fill's external requests
  still complete.
- Observable at: ic_tag_write_o (only invalidation writes, no fill write), instr_rvalid_i consumed
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Cache invalidation" ("nothing will be allocated") |
  RTL: rtl/ibex_icache.sv:744-746, 815-819
- Edge: yes, of F-IC-023
- Status: ACTIVE

### F-IC-027: Disabling the cache while fills are in flight stops their allocation; enabling does not backfill
- What: Clearing icache_enable clears fill_cache on busy buffers (no write). Setting icache_enable
  while a buffer allocated as non-caching is in flight does not make it allocate.
- Observable at: ic_tag_write_o
- Config: cpuctrlsts.icache_enable toggled by CSR write
- Source: RTL-defined: rtl/ibex_icache.sv:683, 744-746
- Edge: yes, of F-IC-014
- Status: ACTIVE
- Notes: stimulus: csrw cpuctrlsts inside a loop so the write lands while a miss is in flight.

### F-IC-028: Coincident lookup during an invalidation write also writes the data RAM
- What: Invalidation asserts tag_write for the invalidation index, but data_req_ic0 is
  lookup_req | fill_req, so if the core is fetching (lookup) while a tag is being invalidated,
  ic_data_req_o (all ways) and ic_data_write_o are also asserted at the invalidation index with
  ECC-encoded zero data. Functionally harmless (tag invalid), but visible on the data RAM ports.
- Observable at: ic_data_req_o & ic_data_write_o during invalidation
- Config: none
- Source: RTL-defined: rtl/ibex_icache.sv:270-283
- Edge: yes, of F-IC-022
- Status: ACTIVE
- Notes: a checker "data RAM written only on fills" would be wrong. Candidate owner question
  (intended?).

### F-IC-029: Cache busy keeps the core awake
- What: busy_o (if_busy) is high while an invalidation is in progress or any fill buffer has
  outstanding bus responses; core_busy_o is On while ctrl_busy, if_busy or lsu_busy. Therefore a
  WFI issued right after fence.i keeps core_busy_o On for at least the invalidation duration.
- Observable at: core_busy_o
- Config: none
- Source: doc: doc/03_reference/icache.rst "Detailed behaviour" (busy_o) | doc:
  doc/02_user/integration.rst "Interfaces" (core_sleep_o row) | RTL: rtl/ibex_icache.sv:1302-1304;
  rtl/ibex_if_stage.sv:421; rtl/ibex_core.sv:498-521
- Edge: no
- Status: ACTIVE

### F-IC-030: ECC error on a tag read: treated as a miss, all ways at the index invalidated, minor alert
- What: Tag ECC is checked on every lookup for every way (regardless of hit). Any tag error (1 or 2
  bits, any way) cancels the hit, marks all ways at that index for invalidation, and pulses
  alert_minor_o for one cycle. The request is then served from the bus.
- Observable at: alert_minor_o, ic_tag_write_o next cycle (both ways), instr_req_o for the
  re-fetch
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Cache ECC protection" | doc:
  doc/03_reference/security.rst "ICache ECC" | RTL: rtl/ibex_icache.sv:546-563, 585, 591-592,
  620-644, 748; rtl/ibex_core.sv:1337
- Edge: no
- Status: ACTIVE
- Notes: stimulus: TB RAM model flips 1 or 2 bits of ic_tag_rdata_i on a read.

### F-IC-031: ECC error on data read: only on a hit, only the hitting way invalidated
- What: Data ECC is checked only for the way that hit (unused ways may hold garbage). Any error
  cancels the hit, invalidates the matching way(s) at that index, pulses alert_minor_o, and the
  data is fetched from the bus.
- Observable at: alert_minor_o, ic_tag_write_o (one way), instr_req_o
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Cache ECC protection" | RTL:
  rtl/ibex_icache.sv:565-592, 940-943
- Edge: yes, of F-IC-030
- Status: ACTIVE

### F-IC-032: ECC correction write blocks lookups for one cycle and writes an invalid tag
- What: Folded into F-IC-030: the correction write and its one-cycle lookup block are the parent's
  own consequence (ic_tag_write_o next cycle is already F-IC-030's observable), a checker bullet
  without a distinct stimulus (pattern d); carried by CG-IC-006.cp_lookups_blocked_next.yes and
  cp_inval_ways.
- Edge: yes, of F-IC-030
- Status: FOLDED into F-IC-030 (bin CG-IC-006.cp_lookups_blocked_next.yes)

### F-IC-033: Single-bit and double-bit ECC errors are handled identically; no correction
- What: Folded into F-IC-030: single- versus double-bit injection is a stimulus variable whose
  expected outcome is identical to the parent's (same alert, same invalidation), so it is not a
  distinct edge; carried by CG-IC-006.cp_bits.single / double (the cross cr_ram_x_bits_x_way covers
  all 8 combinations).
- Edge: yes, of F-IC-030
- Status: FOLDED into F-IC-030 (bin CG-IC-006.cp_bits.single, CG-IC-006.cp_bits.double)

### F-IC-034: ICache ECC errors do not raise a major alert or an internal NMI
- What: Folded into F-IC-030: "no major alert and no NMI" is a checker bullet on the parent's
  stimulus without a distinct condition (pattern d); carried by CG-IC-006.cp_major_nmi_quiet.yes.
- Edge: yes, of F-IC-030
- Status: FOLDED into F-IC-030 (bin CG-IC-006.cp_major_nmi_quiet.yes)

### F-IC-035: ECC errors on unused ways or before initialisation do not alert
- What: Data ECC is checked only on a valid-tag hit; tag ECC is checked only for lookups with
  lookup_valid_ic1 (cache enabled, not invalidating). Uninitialised data RAM and pre-init tag RAM
  cannot cause false minor alerts.
- Observable at: alert_minor_o stays low with random uninitialised RAM contents
- Config: cpuctrlsts.icache_enable
- Source: RTL-defined: rtl/ibex_icache.sv:466-470, 580-585
- Edge: yes, of F-IC-030
- Status: ACTIVE
- Notes: the TB RAM model can leave data RAM random; the tag RAM must return a valid ECC codeword
  once written by invalidation (a transparent model does).

### F-IC-036: Bus-error lines are not cached; PMP-denied lines can be cached
- What: A line with instr_err_i on any beat is never allocated. PMP is not visible to the icache, so
  a line in a region that is currently PMP-denied for the executing privilege can be fetched and
  allocated; the fault is raised per instruction at IF output using the privilege at that time. A
  later PMP change (or M-mode access) can hit that line.
- Observable at: ic_tag_write_o for a denied region, instr_req_o absent on the later hit
- Config: pmpcfg/pmpaddr, privilege mode
- Source: RTL-defined: rtl/ibex_icache.sv:815-819; rtl/ibex_core.sv:1590-1600 (g_pmp_addr_gate,
  the elaborated arm); rtl/ibex_if_stage.sv:426-435
- Edge: no
- Status: ACTIVE
- Notes: doc defect D9 (icache.rst "Detailed behaviour" instr_pmp_err_i squash) as in F-IMEM-028.

### F-IC-037: Every branch issues a speculative bus request even when the target hits
- What: When no external request is pending, a branch lookup always issues an external request for
  the target word in parallel with the tag lookup (fill_spec_req = ~icache_enable | branch_i). If
  the lookup hits the response is discarded; if another buffer is already requesting, no
  speculative request is made.
- Observable at: instr_req_o on branch targets that are cache hits
- Config: cpuctrlsts.icache_enable = 1
- Source: RTL-defined: rtl/ibex_icache.sv:703-705, 1030-1031
- Edge: yes, of F-IC-014
- Status: ACTIVE
- Notes: a scoreboard expecting "no bus traffic on a warm loop" must exempt the branch target
  word of each iteration.

### F-IC-038: Lookup throttle bounds prefetch to about three lines ahead
- What: New non-branch lookups are suppressed when more than FB_THRESHOLD (2) non-stale fill
  buffers are busy; the count includes the line being output, so linear prefetch never holds more
  than 3 non-stale buffers (F-FE-017). Branches bypass the throttle and can allocate the 4th
  buffer, but never more than NUM_FB=4 busy (lookup_req_ic0 requires ~&fill_busy_q).
- Observable at: instr_addr_o lead over the line of the word consumed into ID for sequential grants:
  at most 3 lines (against the last retired rvfi_pc_rdata transiently 4 while a load/store is
  stalled in WB, never 5; TIMING); a 4th busy buffer only right after a branch lookup (ibus monitor
  line count)
- Config: none
- Source: doc: doc/03_reference/icache.rst "Cache Pipeline" ("lookup requests ... naturally
  throttle themselves as fill buffer resources run out") | RTL: rtl/ibex_icache.sv:72-74, 247-250,
  690-697
- Edge: no
- Status: ACTIVE

### F-IC-039: Cache behaviour in U-mode
- What: Privilege has no effect on caching: hits/misses/allocation are identical in U-mode; only the
  PMP check at IF output uses the privilege. cpuctrlsts (the enable) is not accessible from U-mode.
- Observable at: instr_req_o pattern identical across modes; illegal instruction on U-mode csrr
  cpuctrlsts
- Config: privilege mode, cpuctrlsts
- Source: doc: doc/03_reference/cs_registers.rst "CPU Control and Status Register (cpuctrlsts)"
  ("Accessible in Machine Mode only") | RTL: rtl/ibex_icache.sv:22-69 (no privilege input);
  rtl/ibex_core.sv:1590-1591, 1599-1602 (PMP_I/PMP_I2 use priv_mode_id, g_pmp_addr_gate arm)
- Edge: no
- Status: ACTIVE

### F-IC-040: Cache disabled in debug mode
- What: icache_enable is forced 0 while debug_mode or debug_mode_entering, so the debug ROM and all
  debug-mode execution are pass-through; existing lines remain valid and hit again after dret.
- Observable at: instr_req_o for every debug-mode fetch; hits resume after dret
- Config: cpuctrlsts.icache_enable = 1, debug_req_i / ebreak into debug
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1970-1971
- Edge: yes, of F-IC-012
- Status: ACTIVE

### F-IC-041: icache_enable toggled with fetches in flight (CSR write timing)
- What: Folded into F-IC-012: the enable taking effect for the next lookup with no stall or flush is
  a timing detail of the CSR write itself; the fills-in-flight coincidence is F-IC-027 (pattern d);
  carried by CG-IC-005.cp_effect_latency.next_lookup and cp_transition.*.
- Edge: yes, of F-IC-012
- Status: FOLDED into F-IC-012 (bin CG-IC-005.cp_effect_latency.next_lookup)

### F-IC-042: Multi-way hit is ORed
- What: If both ways match (possible after F-IC-021), the hit data is the bitwise OR of both ways
  and ECC is checked on the ORed value; identical contents are benign. Where the copies differ the
  outcome depends on how they came to differ. When one copy is a corrupted image of the other,
  which is what a data-RAM ECC injection produces, the OR restores every bit the good copy holds
  set, so a flip that clears a bit of the un-tweaked word the mux ORs is masked (no ECC error, no
  minor alert, the fetched word correct) and a flip that sets one reaches the check and produces an
  ECC error (minor alert). When the copies are two independently written codewords, which is what
  the self-modifying-code path of TP-IC-038 produces, set and clear have no reference copy: the
  check bits differ, so the OR is in general not a codeword and the per-bank decoder flags it
  (rtl/ibex_icache.sv:568-573), and an OR that happens to equal one codeword delivers that
  copy's data, which is stale when the matched copy is the pre-store one and current when it is the
  newly written one.
- Observable at: alert_minor_o, rvfi_insn
- Config: cpuctrlsts.icache_enable = 1
- Source: doc: doc/03_reference/icache.rst "Detailed behaviour" (last two paragraphs) | RTL:
  rtl/ibex_icache.sv:506-514, 565-585
- Edge: yes, of F-IC-019
- Status: ACTIVE
- Notes: needs a genuine two-way copy (both ways valid at the index, F-IC-021; a cold index yields
  one copy), which arises two ways. The documented one is a branch into an address being prefetched
  (doc/03_reference/icache.rst:73, which calls the consequence a minor performance inefficiency at
  :74). The second is RTL-defined and undocumented (doc defect D22): after an ECC-correction refetch
  the core allocates a second copy of a line still valid in the other way, because each fill
  captures its allocation way in the IC1 cycle of its own lookup while the correction's invalidation
  write lands two cycles after the erroring read, and nothing compares the captured fill addresses,
  so two fills of one line both write. With IC_NUM_WAYS = 2 (rtl/ibex_pkg.sv:401), and while the other
  way is invalid at the erroring lookup, the two selections differ exactly when the erroring copy
  sits in way 0, because allocation takes the lowest invalid way whenever any way is invalid and the
  round-robin pointer otherwise (rtl/ibex_icache.sv:534-535). Landing 16 put the observation back on
  retained evidence after landing 15 retired the earlier trace: the tag-write history at the duplicated
  indices (dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_trace17_tagwrite_history.log)
  reconstructs 16 coexistence episodes, 13 at index 26 and 3 at index 27, each with its start and end
  cycle, its shared tag and the way whose copy was added second, and all 16 added into way 0. That
  aggregate is read narrowly as the artifact's own header directs: it evidences the direction of each
  episode it lists, not the way-selection policy, which stays the RTL terms above, since it is one
  program at one seed. The masking precondition is also not index-specific: 20 announced injections met
  the two-way-valid equal-tag condition at those two indices
  (gen_fu_l16_trace17_duplicate_copies.log). When the other way instead holds a valid
  different line, the first fill takes round_robin_way_q and the copies differ when that pointer is not
  the erroring way. The
  copies then differ either from self-modifying code without fence.i (a software constraint per doc)
  or from a corruption of one copy, which the TB injects as WP-12 stimulus with no software
  constraint broken; in the second case a flip clearing a bit of the un-tweaked word the mux ORs is
  masked and reports nothing (S5,
  CG-IC-006.cp_no_alert_case.masked_duplicate_copy). The duplicate is self-limiting, since a
  duplicated line leaves no invalid way at its index so the next lookup of another line there evicts
  one copy (rtl/ibex_icache.sv:534-535), and self-clearing, since the next data error at that index
  invalidates both matching ways in one write (:591-592). No RTL
  assertion forbids multiple tag matches. TP-IC-038 is informational (own `_info` test,
  gen_chk_alerts on), candidate owner question 5.

### F-IC-043: Fill buffer release and reuse
- What: A fill buffer frees when its RAM write (or non-allocation/hit/error) is done, its output is
  done (or stale), and all its expected beats have arrived. A stream of linear misses with slow
  memory is throttled at 3 non-stale buffers (F-FE-017); all 4 buffers are busy only after a branch
  lookup while 3 lines are in flight (the stale ones stay busy until their beats arrive), after
  which every new lookup, branch or not, stalls until the oldest buffer frees (lookup_req_ic0
  requires ~&fill_busy_q).
- Observable at: instr_req_o gaps under slow rvalid after a branch with 3 lines in flight
- Config: none
- Source: doc: doc/03_reference/icache.rst "Fill buffers" | RTL: rtl/ibex_icache.sv:713-734
- Edge: no
- Status: ACTIVE
- Notes: release-to-next-request timing (TP-IC-052): with icache_enable = 0 the next new request
  follows the oldest line's last rvalid within 2 cycles; when caching the stale line is first
  written to the RAM (fill_ram_req c+1, ram_done c+2, release c+3, lookup c+3, IC1 miss and request
  c+4; rtl/ibex_icache.sv:815-822, 843-844), so 4 cycles.

### F-IC-044: Output handshake stability toward IF
- What: Once valid_o is high, rdata_o/addr_o/err_o/err_plus2_o stay stable until accepted or
  branch_i, except after an error is passed (then unconstrained until the next branch). Upper 16
  bits of rdata_o are unconstrained for a compressed instruction.
- Observable at: rvfi_insn equals the memory word(s) at rvfi_pc_rdata (indirect, gen_isa_compare);
  the icache-to-IF handshake itself is probe candidate P3 (probe register entry needed): gen_icache
  valid_o / ready_i / rdata_o / addr_o / err_o for a bound stability assertion
- Config: none
- Source: doc: doc/03_reference/icache.rst "Detailed behaviour" (ready/valid rules) | RTL:
  rtl/ibex_icache.sv:1129-1136, 1191-1197
- Edge: no
- Status: ACTIVE
- Notes: not a DUT-boundary signal; the bound assertion needs the P3 probe entry.

### F-IC-045: Cache reads and writes are never issued for the same RAM in the same cycle
- What: Tag/data RAM ports are single-ported: request is either a read (write low) or a write; the
  IC0 arbiter picks one of lookup, fill, invalidation write, ECC write per cycle.
- Observable at: ic_tag_req_o with ic_tag_write_o (one operation per cycle)
- Config: none
- Source: doc: doc/03_reference/icache.rst "Cache Pipeline" (arbitration) | RTL:
  rtl/ibex_icache.sv:261-283
- Edge: no
- Status: ACTIVE
- Notes: passive assertion: never (fill write) & (lookup read) on the same port in one cycle; but
  see F-IC-028 for the invalidation/lookup overlap that yields a write.

### F-IC-046: RAM port values are don't-care when req is low
- What: ic_tag_addr_o/ic_data_addr_o/wdata carry the muxed IC0 values every cycle; they are
  meaningful only when the corresponding req bit is set. The TB RAM model must ignore them
  otherwise.
- Observable at: ic_* ports
- Config: none
- Source: RTL-defined: rtl/ibex_icache.sv:445-464
- Edge: no
- Status: ACTIVE

### F-IC-047: Scramble-key validity drop without a request has no effect on the icache
- What: ic_scr_key_valid_i is read by the invalidation FSM only in OUT_OF_RESET and
  AWAIT_SCRAMBLE_KEY. If the key agent drops ic_scr_key_valid_i while the FSM is in INVAL_IDLE
  (external key rotation without a request), the icache does not react: no ic_scr_key_req_o, no
  invalidation, lookups keep hitting and fills keep allocating while the key is marked invalid;
  only cpuctrlsts.ic_scr_key_valid reads 0 (F-IC-011). Lines written under the old key stay
  hittable; in a real system ibex_top's RAM scrambling (outside the DUT) would corrupt them, which
  is why software must fence.i (F-IC-023) after a key change. With a plain-array TB RAM model
  there is no data effect.
- Observable at: ic_scr_key_req_o absent, ic_tag_write_o (fill writes continue), instr_req_o absent
  on hits during the drop, csrr read-back of cpuctrlsts bit 8 on rvfi_rd_wdata
- Config: none (ic_scr_key_valid_i stimulus)
- Source: RTL-defined: rtl/ibex_icache.sv:1225, 1235 (the only reads of ic_scr_key_valid_i),
  1258-1267 (INVAL_IDLE reacts to icache_inval_i only); rtl/ibex_top.sv:623-656 (reference only,
  outside the DUT) | doc: doc/03_reference/icache.rst "ICache Scrambling" and "Scramble Key
  Renewal" (describe only the request-driven renewal)
- Edge: yes, of F-IC-008
- Status: ACTIVE
- Notes: TP-IC-016 is the directed test. CG-IC-002.cp_tag_write_while_key_invalid is qualified by
  the AWAIT_SCRAMBLE_KEY state so that fill writes during an unsolicited drop are counted as legal
  (cp_fill_write_after_unsolicited_drop), not as a checker failure.

### F-IC-048: Disabling the cache does not invalidate it; re-enabling makes old lines hittable (MEM-26)
- What: Clearing cpuctrlsts.icache_enable only masks the lookup result (lookup_actual_ic0) and stops
  new allocation (fill_cache_new; fill_cache_d drops for busy buffers): no tag write happens and
  the tag RAM keeps its valid lines. Setting the bit again makes a lookup of a line cached before
  the disable hit, with no bus request. Only fence.i (F-IC-023) and ECC errors (F-IC-030)
  invalidate; the debug-mode force-off (F-IC-040) is the same mechanism.
- Observable at: instr_req_o absent for the words of a line cached before the disable when it is
  re-executed after the re-enable (ibus monitor shows no request while RVFI retires them, except
  the branch-target speculative word of F-IC-037); ic_tag_write_o absent between the disable and
  the re-enable other than invalidation/ECC writes
- Config: cpuctrlsts.icache_enable toggled 1 -> 0 -> 1 by CSR writes
- Source: RTL-defined: rtl/ibex_icache.sv:266, 683, 744-746; rtl/ibex_cs_registers.sv:874-877,
  1970-1971 | rtl-arch MEM-26 | doc: doc/03_reference/icache.rst:24 (pass-through when low; no
  invalidation stated), :283-289 (only icache_inval_i invalidates)
- Edge: no
- Status: ACTIVE
- Notes: stale-code hazard: code modified while the cache was disabled hits the old line after the
  re-enable unless fence.i is executed (software constraint, as F-IC-021). TP-IC-032 covers the
  in-flight line case (F-IC-027); TP-IC-057 covers this feature.

---------------------------------------------------------------------------------------------------


# 4.7 Areas DIT, SEC, RST, RVFI, CHERI: Dummy instructions and data-independent timing, alerts and countermeasures, reset and boot, RVFI trace, CHERIoT carve-out


Scope: dummy instruction insertion and data-independent timing (DIT), security features and
alerts at the ibex_core boundary (SEC), reset and boot (RST), the RISC-V Formal Interface (RVFI),
and the CHERIoT carve-out inventory (CHERI). Build configuration `opentitan` (SecureIbex=1 so
DataIndTiming=1, PCIncrCheck=1; ShadowCSR is hard-wired 0 in rtl/ibex_core.sv:197).

DUT boundary assumptions used below (gen_dut_top = ibex_core + ibex_register_file_ff):
- cheriot_enable_i tied to IbexMuBiOff (owner ruling).
- Wrapper parameters per owner-question Q-002 defaults: MemECC=1, DummyInstructions=1,
  ResetAll=1, RegFileECC=0 (RegFileDataWidth=32), +define+RVFI. This mirrors ibex_top (NOT in the
  DUT), which sets DummyInstructions = SecureIbex (rtl/ibex_top.sv:214), MemECC = SecureIbex
  (:41), RegFileECC = 1'b0 and RegFileDataWidth = 32 (:215,217); the register-file ECC of
  SecureIbex lives in the lockstep shadow core (RegFileLockstepECC, :216,
  rtl/ibex_lockstep.sv:477-527), which is not in the DUT. Consequence: the in-core RF ECC alert
  path is a negative check (F-SEC-004) and every RegFileECC=1 statement below is conditional.
- ibex_core has no core_sleep_o, test_en_i, scan_rst_ni, ram_cfg_* or scramble_key_* ports;
  those are ibex_top ports (rtl/ibex_top.sv:70-74,125-128,191,194). ibex_core exposes core_busy_o
  (mubi), ic_scr_key_req_o / ic_scr_key_valid_i and the icache RAM ports instead.

Status field (fix brief rule 1): every block carries `- Status:` = ACTIVE | ALIAS of F-<id> |
FOLDED into F-<id> (bin <name>). Only ACTIVE entries count in the completeness measure; ALIAS and
FOLDED IDs stay citable by test-plan items and resolve to the canonical / parent ID. Edge rule
(Critic C-12) applied to all 63 edge entries of this part: an entry keeps `Edge: yes` only if its
What names a stimulus condition or timing coincidence the parent does not AND its observable or
expected outcome differs; otherwise it is FOLDED into the parent bin named in its Status line.
Depth-2 edge chains (C-13) now point at the base feature (F-DIT-027, F-RVFI-014). Observables
(C-07/C-08) name a DUT port or RVFI field; wrapper-internal seam nets (dummy_instr_*_o,
rf_*_o) appear only as "probe candidate P1 (probe register entry needed)" after the boundary
alternative.

Every RTL line cited in a block changed for this fix was re-verified with sed -n on 2026-09-03;
the remaining citations were spot-checked with grep -n / cat -n.

---------------------------------------------------------------------------------------------------
## DIT: dummy instruction insertion and data-independent timing
---------------------------------------------------------------------------------------------------

### F-DIT-001: cpuctrlsts.data_ind_timing enable bit
- What: Bit 1 of the custom CSR cpuctrlsts (0x7C0) enables data-independent timing. It is a
  plain RW flop (WARL, reset 0) whose registered value drives data_ind_timing into ID/EX.
  Because DataIndTiming = SecureIbex = 1 the bit is writable in this build.
- Observable at: CSR read-back of cpuctrlsts (rvfi_rd_wdata of a csrr), instruction timing on
  rvfi_valid spacing and instr_req_o/instr_addr_o (see F-DIT-002/003).
- Config: cpuctrlsts.data_ind_timing; privilege mode (M-mode only CSR).
- Source: doc: doc/03_reference/cs_registers.rst "CPU Control and Status Register (cpuctrlsts)"
  (bit 1) | doc: doc/03_reference/security.rst "Data Independent Timing" | RTL-defined:
  rtl/ibex_cs_registers.sv:239-246,1892-1905,1973-1984; rtl/ibex_core.sv:195
- Edge: no
- Status: ACTIVE
- Notes: The CSR write takes effect on cpuctrlsts_part_q at the end of the CSR instruction; the
  next instruction to enter ID sees the new value.

### F-DIT-002: Conditional branches take identical time when DIT is on
- What: With data_ind_timing set every conditional branch is treated as taken for timing:
  the ID FSM goes to MULTI_CYCLE, stall_branch is asserted and branch_set_raw_d is forced to 1
  regardless of branch_decision (rtl/ibex_id_stage.sv:920-935). The branch-set is flopped
  (g_branch_set_flop, 771-791) so branches take two cycles even with BranchTargetALU=1. A
  not-taken branch therefore also asserts pc_set and redirects fetch to the fall-through
  address (branch_taken = ~data_ind_timing | branch_taken_q selects the fall-through target,
  rtl/ibex_id_stage.sv:819-837,497).
- Observable at: instr_req_o/instr_addr_o (a not-taken branch causes a prefetch flush and a new
  request for PC+4/PC+2), rvfi_pc_wdata (= branch_target_ex when pc_set, rtl/ibex_core.sv:2084),
  cycle count between consecutive rvfi_valid pulses, mhpmcounter events for branches;
  alert_major_internal_o stays 0 across the redirect (the hardened PC-increment check is disarmed by
  branch_req, rtl/ibex_if_stage.sv:664-669,688)
- Config: cpuctrlsts.data_ind_timing.
- Source: doc: doc/03_reference/security.rst "Data Independent Timing" ("Branches execute
  identically regardless of their taken/not-taken status") | doc:
  doc/03_reference/pipeline_details.rst "Multi- and Single-Cycle Instructions" (Branch rows) |
  RTL-defined: rtl/ibex_id_stage.sv:767-793,819-837,920-935
- Edge: no
- Status: ACTIVE
- Notes: pipeline_details.rst documents only the non-DIT timing (0 stall not-taken, 1 stall
  taken with BranchTargetALU). The DIT timing (every branch 1 stall + fetch redirect) is only in
  the RTL.

### F-DIT-003: DIV/REM never complete early when DIT is on
- What: In ibex_multdiv_fast (used for RV32MSingleCycle, rtl/ibex_ex_block.sv:165-166) a divide
  by zero normally jumps straight to MD_FINISH; with data_ind_timing the FSM proceeds through the
  full long division (MD_ABS_A ...) and the result (-1 for DIV, dividend for REM) falls out
  naturally. Division therefore always takes the full-length latency.
- Observable at: cycles between rvfi_valid of the div and the next instruction; rvfi_rd_wdata is
  unchanged (-1 / operand a).
- Config: cpuctrlsts.data_ind_timing.
- Source: doc: doc/03_reference/security.rst "Data Independent Timing" ("Early completion of
  divide by zero is removed") | doc: doc/03_reference/pipeline_details.rst "Multi- and
  Single-Cycle Instructions" (Division/Remainder row: "1 or 37") | RTL-defined:
  rtl/ibex_multdiv_fast.sv:428-446
- Edge: no
- Status: ACTIVE

### F-DIT-004: Divide-by-zero timing with DIT off vs on
- What: FOLDED into F-DIT-003: the same rs2 = 0 divide takes the short path with DIT off and the
  full path with DIT on (rtl/ibex_multdiv_fast.sv:434,437,445), architectural results identical.
  This is F-DIT-003's Config at its other value (Critic C-12 pattern b); the parent bins carry it.
- Observable at: rvfi_valid spacing, rvfi_rd_wdata identical in both runs.
- Config: cpuctrlsts.data_ind_timing.
- Source: RTL-defined: rtl/ibex_multdiv_fast.sv:434,437,445 | doc:
  doc/03_reference/pipeline_details.rst "Multi- and Single-Cycle Instructions"
- Edge: yes, of F-DIT-003
- Status: FOLDED into F-DIT-003 (bin CG-DIT-003.cr_latency.div_off_zero_two; CG-DIT-003.cr_div_dit_zero.div_off_zero)

### F-DIT-005: MUL/MULH timing is unaffected by DIT in this build
- What: security.rst says "Early completion of multiplication by zero/one is removed", but the
  fast/single-cycle multiplier has no data_ind_timing term (grep of rtl/ibex_multdiv_fast.sv
  shows DIT only in the divider at 434/445). With RV32MSingleCycle MUL takes 1 cycle and MULH 2
  cycles regardless of operands or DIT.
- Observable at: rvfi_valid spacing for mul/mulh/mulhu/mulhsu.
- Config: cpuctrlsts.data_ind_timing.
- Source: doc defect D11: doc/03_reference/security.rst "Data Independent Timing" ("Early
  completion of multiplication by zero/one is removed") | RTL-defined:
  rtl/ibex_multdiv_fast.sv:33,428-446 (no mult DIT path); rtl/ibex_ex_block.sv:165-166
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D11: the security.rst statement has no RTL counterpart in the
  RV32MSingleCycle multiplier (it applies only to the slow multiplier). Not a bug; the check
  records the constant latency (TP-DIT-006, Expected: pass (doc mismatch D11)).

### F-DIT-006: DIT written by the instruction immediately preceding a div or branch
- What: cpuctrlsts_part_q updates on the clock edge that completes the CSR write; the following
  instruction enters ID in the next cycle and samples the new data_ind_timing. There is no way to
  toggle DIT while a div is in flight (single-issue: the div occupies ID until done).
- Observable at: rvfi_valid spacing of the record that follows the cpuctrlsts write (its gap
  shows the latency of the NEW data_ind_timing value); csrr read-back on rvfi_rd_wdata of
  cpuctrlsts.
- Config: cpuctrlsts.data_ind_timing.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:874-877,1905,1973-1984; rtl/ibex_id_stage.sv:925-928
- Edge: yes, of F-DIT-001
- Status: ACTIVE

### F-DIT-007: Not-taken compressed branch under DIT redirects to PC+2
- What: Folded into F-DIT-002: the parent already states that a not-taken branch under DIT asserts
  pc_set and redirects fetch to the fall-through address "PC+4/PC+2"; the compressed form is the len
  = 2 value of that statement with the same observable, and the disarmed PC-increment check (no
  alert) is added to the parent's observable (Critic M-9); carried by the parent's compressed
  not-taken bins.
- Source: RTL-defined: rtl/ibex_id_stage.sv:819-837,925-928; rtl/ibex_if_stage.sv:664-669,688
- Edge: yes, of F-DIT-002
- Status: FOLDED into F-DIT-002 (bin CG-DIT-002.cr_dit_taken_c.on_nt_c16, CG-DIT-002.cp_compressed.c16)

### F-DIT-008: DIT has no effect on load/store timing (misaligned accesses still split)
- What: The LSU has no data_ind_timing input; misaligned accesses still produce two bus
  transactions and their timing depends on the address (documented leak).
- Observable at: data_req_o count per instruction independent of cpuctrlsts.data_ind_timing.
- Config: cpuctrlsts.data_ind_timing.
- Source: doc: doc/03_reference/security.rst "Data Independent Timing" (unaligned note) |
  RTL-defined: rtl/ibex_load_store_unit.sv:18-80 (no DIT port), 403
- Edge: yes, of F-DIT-001
- Status: ACTIVE

### F-DIT-009: Dummy DIV under DIT takes the full division latency
- What: Folded into F-DIT-003: a dummy DIV is a DIV, so the parent's "never completes early with DIT
  on" applies to it unchanged; the dummy kind is a stimulus variable with the parent's latency
  outcome (v2 edge rule, second pass; Critic M-9); carried by the probe-gated (P1/P9) dummy-type
  bins. The zero-divisor case is a matter of the operand VALUE the LFSR-chosen rs2 register holds,
  not of the register index: a dummy that reads x0 gets rf_data_r0_q, the previous dummy's result
  (rtl/ibex_register_file_ff.sv:159-173, :221-224; rtl-arch fact-check X-22), so "rs2 = x0" is
  not a divide-by-zero premise (TP-DIT-010 corrected).
- Source: RTL-defined: rtl/ibex_dummy_instr.sv:128-131,144; rtl/ibex_multdiv_fast.sv:434,445;
  rtl/ibex_register_file_ff.sv:159-173
- Edge: yes, of F-DIT-003
- Status: FOLDED into F-DIT-003 (bin CG-DIT-004.cr_type_dit.div_on, div_off; CG-DIT-004.cr_div_zero.div_zero_on, div_zero_off)

### F-DIT-010: DIT applies in U-mode although cpuctrlsts is M-mode only
- What: FOLDED into F-DIT-002: data_ind_timing shapes branch and divide timing in U-mode exactly
  as in M-mode (the effect is not privilege-gated); the parent's Config (privilege mode) at its
  other value (Critic C-12 pattern b). The U-mode cpuctrlsts access trap (0x7C0 is M-mode only,
  illegal_csr_priv, rtl/ibex_cs_registers.sv:403-406) belongs to the cpuctrlsts layout entry
  F-SEC-031 (alias of F-CSR-085).
- Observable at: rvfi_valid spacing of U-mode branches / divides (rvfi_mode = 0); rvfi_trap +
  csrr read-back of mcause for the U-mode cpuctrlsts access.
- Config: privilege mode, cpuctrlsts.data_ind_timing.
- Source: doc: doc/03_reference/cs_registers.rst "CPU Control and Status Register (cpuctrlsts)"
  ("Accessible in Machine Mode only") | RTL-defined: rtl/ibex_cs_registers.sv:403-406
- Edge: yes, of F-DIT-002
- Status: FOLDED into F-DIT-002 (bin CG-DIT-002.cr_dit_priv.on_u; CG-DIT-002.cr_dit_priv.off_u; CG-DIT-001.cp_access.u_trap)

### F-DIT-011: Dummy instruction insertion mechanism (counter and LFSR threshold)
- What: When cpuctrlsts.dummy_instr_en is set, ibex_dummy_instr counts instructions accepted by
  ID (dummy_cnt_en = en & id_in_ready & (fetch_valid | insert)) and inserts a dummy when the
  5-bit counter equals a threshold taken from the LFSR state masked by dummy_instr_mask
  (threshold = lfsr.cnt & {mask, 2'b11}). On insertion the counter clears and the LFSR advances
  (lfsr_en = insert & id_in_ready). The IF stage muxes the dummy in place of the real
  instruction and stalls the fetch path (stall_dummy_instr) so the real instruction follows.
- Observable at: rvfi_valid spacing (a dummy occupies a pipeline slot and produces no record: an
  extra gap in straight-line code); csrr read-back on rvfi_rd_wdata of minstret vs the record
  count (F-PMC-011); probe candidate P1 (probe register entry needed; wrapper-internal seam nets):
  dummy_instr_id_o / dummy_instr_wb_o and rf_raddr_a_o / rf_raddr_b_o, which name the dummy type
  and operands the boundary cannot.
- Config: cpuctrlsts.dummy_instr_en, cpuctrlsts.dummy_instr_mask, secureseed writes.
- Source: doc: doc/03_reference/security.rst "Dummy Instruction Insertion" | RTL-defined:
  rtl/ibex_dummy_instr.sv:33-64,95-115; rtl/ibex_if_stage.sv:504-545
- Edge: no
- Status: ACTIVE
- Notes: Doc defect D19: doc/03_reference/security.rst:51-62 lists dummy_instr_mask values
  000/001/011/111 only; the RTL accepts all eight 3-bit values (rtl/ibex_dummy_instr.sv:97,
  threshold = lfsr.cnt & {mask, 2'b11}); 010/100/101/110 are legal with non-contiguous threshold
  sets (the doc says "less predictable impact"). The mask intervals (F-DIT-012, folded here) are
  bins of this feature; the dummy DIV / interrupt cross is F-DIT-030.

### F-DIT-012: dummy_instr_mask interval control, all 8 values
- What: FOLDED into F-DIT-011: the 3-bit mask ANDs the top three bits of the 5-bit LFSR count
  (rtl/ibex_dummy_instr.sv:97): 000 -> threshold 0..3, 001 -> 0..7, 011 -> 0..15, 111 -> 0..31;
  010/100/101/110 are legal with non-contiguous threshold sets. The parent's Config at its other
  values (Critic C-12 pattern b); doc defect D19 (security.rst:51-62 lists 4 of the 8 legal
  values) is recorded on F-DIT-011.
- Observable at: distribution of gaps between consecutive rvfi_valid pulses per mask value.
- Config: cpuctrlsts.dummy_instr_mask.
- Source: doc defect D19: doc/03_reference/security.rst "Dummy Instruction Insertion" (mask table
  lists 4 of 8 values) | RTL-defined: rtl/ibex_dummy_instr.sv:97
- Edge: yes, of F-DIT-011
- Status: FOLDED into F-DIT-011 (bin CG-DIT-001.cp_mask.m000; CG-DIT-001.cp_mask.m001; CG-DIT-001.cp_mask.m010; CG-DIT-001.cp_mask.m011; CG-DIT-001.cp_mask.m100; CG-DIT-001.cp_mask.m101; CG-DIT-001.cp_mask.m110; CG-DIT-001.cp_mask.m111; CG-DIT-001.cr_dummy_mask.on_m000; CG-DIT-001.cr_dummy_mask.on_m001; CG-DIT-001.cr_dummy_mask.on_m010; CG-DIT-001.cr_dummy_mask.on_m011; CG-DIT-001.cr_dummy_mask.on_m100; CG-DIT-001.cr_dummy_mask.on_m101; CG-DIT-001.cr_dummy_mask.on_m110; CG-DIT-001.cr_dummy_mask.on_m111)

### F-DIT-013: Dummy instruction kinds and encoding
- What: The LFSR selects one of ADD (funct7 0000000/funct3 000), MUL (0000001/000), DIV
  (0000001/100) or AND (0000000/111); rs1 and rs2 are 5-bit LFSR fields (any of x0..x31), rd is
  always x0, opcode 0x33 (R-type). The result is written to the physical x0 shadow register.
- Observable at: rvfi_valid gap class of the stall (+1 cycle for ADD/AND/MUL; + the full
  divider latency for a DIV under DIT or with a nonzero divisor; F-DIT-024 folded here); probe
  candidate P1 (probe register entry needed; wrapper-internal seam nets): rf_raddr_a_o /
  rf_raddr_b_o while dummy_instr_id_o = 1 and the if_stage fcov net fcov_dummy_instr_type.
- Config: cpuctrlsts.dummy_instr_en.
- Source: doc: doc/03_reference/security.rst "Dummy Instruction Insertion" ("inserts multiply and
  divide instructions") | RTL-defined: rtl/ibex_dummy_instr.sv:36-48,117-144
- Edge: no
- Status: ACTIVE
- Notes: SecureIbex with RV32MNone is rejected (rtl/ibex_core.sv:2438). The stall lengths (dummy
  DIV = the 37-cycle divider latency of D7, or the 2-cycle fast path when DIT is off and the
  divisor VALUE is 0; MUL/ADD/AND one cycle; rtl-arch gen_multdiv_bound_props.md:
  GEN_DIV_FULL_CYCLES = 36 / GEN_DIV_ZERO_CYCLES = 1 start-to-valid) are bins of this feature
  (F-DIT-024 folded). Consecutive dummies (threshold 0, F-DIT-027) add their stalls, so an
  observed extra gap is the sum of the classes of the dummies P1 attributes to it (fact-check
  TP-DIT-026).

### F-DIT-014: LFSR reseeding through the secureseed CSR
- What: A write to secureseed (0x7C1) asserts dummy_instr_seed_en with the CSR write data. The
  dummy module keeps a running seed (seed_q <= seed_q ^ wdata) and loads the LFSR with that XOR
  value (prim_lfsr seed_en_i takes precedence over lfsr_en_i). secureseed reads as 0.
- Observable at: change of the dummy insertion pattern after the write; rvfi_rd_wdata = 0 for a
  csrr secureseed.
- Config: secureseed write value; cpuctrlsts.dummy_instr_en.
- Source: doc: doc/03_reference/cs_registers.rst "Security Feature Seed Register (secureseed)" |
  doc: doc/03_reference/security.rst "Dummy Instruction Insertion" | RTL-defined:
  rtl/ibex_cs_registers.sv:673-675,1914-1915; rtl/ibex_dummy_instr.sv:63-90;
  vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv:345-346
- Edge: no
- Status: ACTIVE

### F-DIT-015: Dummy instructions leave architectural state unchanged (x0 shadow register)
- What: The register file implements a physical x0 (g_dummy_r0) that is written only when
  dummy_instr_wb_i is set and read only when dummy_instr_id_i is set; real instructions always
  read x0 as zero. Dummy operands may come from any register including ones with a pending
  writeback (normal forwarding applies).
- Observable at: RVFI (no record for the dummy, next record's rs values unchanged), rvfi_rd_wdata
  of subsequent instructions reading x0 = 0.
- Config: cpuctrlsts.dummy_instr_en.
- Source: doc: doc/03_reference/security.rst "Dummy Instruction Insertion" ("no functional impact
  on processor state") | RTL-defined: rtl/ibex_register_file_ff.sv:144-187 (g_cheriot_rf/
  g_dummy_r0, active because BaseIsa = BaseIsaRV32IorCHERIoT), 162 (DummyWriteTargetsX0 assert);
  rtl/ibex_core.sv:91-92,1207-1208; rtl/ibex_wb_stage.sv:222-241
- Edge: no
- Status: ACTIVE
- Notes: Because BaseIsa = RV32IorCHERIoT the RF uses the banked g_cheriot_rf layout even with
  CHERIoT off (x0-x15 in rf_data, x16-x31 in the 35-bit-wide rf_shared flops, rtl/
  ibex_register_file_ff.sv:88-142,221-224). RTL-defined behaviour (rtl-arch fact-check X-22, fix
  brief 3): a dummy instruction that reads x0 sees the PREVIOUS dummy's result, not 0:
  `rf_data[0] = dummy_instr_id_i ? rf_data_r0_q : WordZeroVal` (rtl/ibex_register_file_ff.sv:
  159-173), where rf_data_r0_q is written by every dummy (we_data_r0 = we_a_dec[0] &
  ~waddr_a_i[4] & dummy_instr_wb_i). Real instructions still read x0 as 0. Consequence for the
  plan: a dummy DIV with rs2 = x0 divides by the last dummy's result, so the zero-divisor
  (fast-path) class is defined by the operand value (TP-DIT-010); architecturally invisible.

### F-DIT-016: Dummy instructions are suppressed on RVFI and do not consume rvfi_order
- What: rvfi_stage_valid_d[0] is gated with ~dummy_instr_id and rvfi_stage_order_d does not
  increment for a dummy.
- Observable at: rvfi_valid, rvfi_order (strictly +1 between consecutive records across dummies).
- Config: cpuctrlsts.dummy_instr_en.
- Source: RTL-defined: rtl/ibex_core.sv:1864-1865,1905
- Edge: no
- Status: ACTIVE

### F-DIT-017: Dummy instruction PC and the PC-increment check
- What: The dummy takes the PC of the next real instruction (the prefetch buffer is stalled), is
  flagged not-compressed / not-expanded / no fetch error, and the hardened PC-increment check is
  disarmed for it (prev_instr_seq_d excludes stall_dummy_instr).
- Observable at: alert_major_internal_o stays 0 across dummies; rvfi_pc_rdata of consecutive real
  retirements stays contiguous across an insertion (no PC gap or repeat attributable to the dummy).
  The dummy's own pc_id and the disarm term are internal: probe candidate P11 (probe register entry
  needed): if_stage_i pc_id / stall_dummy_instr while dummy_instr_id is set, coverage only.
- Config: cpuctrlsts.dummy_instr_en.
- Source: RTL-defined: rtl/ibex_if_stage.sv:526-535,664-669
- Edge: yes, of F-DIT-011
- Status: ACTIVE

### F-DIT-018: Dummy instructions are counted by minstret and the mul/div wait events
- What: Alias of F-PMC-011: DIT perspective of bug candidate B7 (dummies advance minstret and the
  mul/div wait events although security.rst says they have no functional impact), see canonical.
- Observable at: csrr read-back on rvfi_rd_wdata of minstret/minstreth vs the count of rvfi_valid
  records; mhpmcounter mul/div wait events.
- Config: cpuctrlsts.dummy_instr_en, mcountinhibit.
- Source: RTL-defined: rtl/ibex_id_stage.sv:1218-1220; rtl/ibex_wb_stage.sv:150,169,206-210;
  rtl/ibex_cs_registers.sv:1588
- Edge: no
- Status: ALIAS of F-PMC-011

### F-DIT-019: Interrupt arrives while a dummy instruction is in ID
- What: The controller waits for the instruction in ID (the dummy) to finish before IRQ_TAKEN
  (halt_if, then csr_save_if). mepc is pc_if, which is the PC of the next real instruction (the
  same PC the dummy carries).
- Observable at: rvfi_intr on the handler's first record, rvfi_ext_irq_valid; csrr read-back on
  rvfi_rd_wdata of mepc (= PC of the next real instruction); no rvfi_valid between the last real
  instruction and the handler.
- Config: cpuctrlsts.dummy_instr_en, mie/mstatus.MIE.
- Source: RTL-defined: rtl/ibex_controller.sv:698-721,725-733; rtl/ibex_if_stage.sv:532-535
- Edge: yes, of F-DIT-011
- Status: ACTIVE

### F-DIT-020: Debug request or single step while a dummy instruction is in ID
- What: A debug request behaves like the interrupt case (dummy completes, then DBG_TAKEN_IF,
  dpc = PC of the next real instruction). With dcsr.step the "one instruction" that retires
  before re-entering debug mode can be a dummy, so a step may execute no architecturally visible
  instruction (no RVFI record) yet dpc advances by zero.
- Observable at: rvfi_ext_debug_mode; csrr read-back on rvfi_rd_wdata of dpc (debug ROM);
  absence of an rvfi_valid record for the step.
- Config: cpuctrlsts.dummy_instr_en, dcsr.step, debug_req_i.
- Source: RTL-defined: rtl/ibex_controller.sv:698-711; rtl/ibex_if_stage.sv:504-545
- Edge: yes, of F-DIT-011
- Status: ACTIVE
- Notes: Owner question: is a single-step that consumes only a dummy acceptable (dummy insertion
  in debug/step contexts is not documented)?

### F-DIT-021: Dummy insertion coincident with pc_set (branch/exception redirect)
- What: insert_dummy_instr does not depend on pc_set, but the dummy is only registered into ID
  when if_id_pipe_reg_we = if_instr_valid & id_in_ready & ~pc_set. When pc_set is high in the
  insertion cycle the dummy is dropped silently while lfsr_en/dummy_cnt still fire (counter
  cleared, LFSR advanced).
- Observable at: boundary: no distinct observable (a dropped insertion has no architectural
  effect; rvfi_order / rvfi_pc_rdata continuity across taken branches is the negative check);
  probe candidate P1 (probe register entry needed; wrapper-internal seam nets):
  fcov_insert_dummy_instr high with no dummy_instr_id_o in the following cycle.
- Config: cpuctrlsts.dummy_instr_en.
- Source: RTL-defined: rtl/ibex_dummy_instr.sv:64,100-115; rtl/ibex_if_stage.sv:568-570,587
- Edge: yes, of F-DIT-011
- Status: ACTIVE

### F-DIT-022: Dummy instructions never fault but can trigger an RF ECC alert
- What: A dummy has its fetch error masked (instr_err_out = 0) and its encoding is always legal,
  so it cannot take an exception. If RegFileECC is enabled in gen_dut_top, a corrupted operand
  read by a dummy (rf_ren & instr_valid_id) raises alert_major_internal_o like any instruction.
- Observable at: rvfi_trap never set by a dummy (no record at all); alert_major_internal_o.
- Config: cpuctrlsts.dummy_instr_en; RegFileECC=0 per Q-002 default (alert half is a negative check).
- Source: RTL-defined: rtl/ibex_if_stage.sv:529-530; rtl/ibex_core.sv:1281-1289 (RegFileECC=1
  branch), 1305-1319 (RegFileECC=0: rf_ecc_err_comb = 0)
- Edge: yes, of F-DIT-011
- Status: ACTIVE
- Notes: With RegFileECC=0 (Q-002 default) alert_major_internal_o stays 0 even when a dummy reads
  a corrupted flop (no decoder exists, rtl/ibex_core.sv:1305-1319); the "never faults" half is the
  distinct expected outcome (a dummy with a fetch error or an illegal encoding cannot exist).

### F-DIT-023: dummy_instr_en cleared while a dummy is in WB (the in-ID case is unreachable)
- What: The dummy_instr_id / dummy_instr_wb flags travel with the instruction (registered in IF,
  re-registered in WB) so a dummy already in the pipeline still writes the x0 shadow and is
  still suppressed on RVFI after software clears the enable. Only the dummy-in-WB case is
  reachable: the clearing csrw itself occupies ID when it commits and its csr_pipe_flush halts IF
  (rtl/ibex_controller.sv:664-679,816-820), so no dummy can be in ID at the commit (rtl-arch
  fact-check TP-DIT-025); the dummy_instr_id_o level may still read 1 afterwards because it is
  updated only on if_id_pipe_reg_we (rtl/ibex_if_stage.sv:538-544, X-22).
- Observable at: rvfi_valid (no stray record for the in-flight dummy); rvfi_rs1_rdata / rvfi_rs2_rdata
  of x0 read 0 afterwards.
- Config: cpuctrlsts.dummy_instr_en toggling.
- Source: RTL-defined: rtl/ibex_if_stage.sv:537-544; rtl/ibex_wb_stage.sv:222-241;
  rtl/ibex_core.sv:1864
- Edge: yes, of F-DIT-011
- Status: ACTIVE

### F-DIT-024: Dummy DIV stall length and dummy MUL single-cycle
- What: FOLDED into F-DIT-013: a dummy DIV occupies ID for the full divider latency (37 cycles,
  D7; shorter only with DIT off and a zero divisor, F-DIT-009), a dummy MUL/ADD/AND for one
  cycle; the parent's kinds with their latencies (Critic C-12 pattern c).
- Observable at: gap between rvfi_valid pulses; instr_req_o stalls.
- Config: cpuctrlsts.dummy_instr_en, cpuctrlsts.data_ind_timing.
- Source: doc: doc/03_reference/pipeline_details.rst "Multi- and Single-Cycle Instructions" (D7:
  37 cycles total per RTL) | RTL-defined: rtl/ibex_dummy_instr.sv:117-141
- Edge: yes, of F-DIT-013
- Status: FOLDED into F-DIT-013 (bin CG-DIT-004.cr_type_dit.div_off; CG-DIT-004.cr_type_dit.mul_off; CG-DIT-004.cr_type_dit.add_off; CG-DIT-004.cr_type_dit.and_off)

### F-DIT-025: secureseed write of 0 or a value that yields an all-zero LFSR seed
- What: Writing 0 reloads the LFSR with the unchanged running seed (seed_en_i loads seed_q ^ 0,
  rtl/ibex_dummy_instr.sv:66-74). If the XOR result is all-zero the LFSR enters its lockup state
  (lockup = ~|lfsr_q, vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv:298-299) and on the next
  lfsr_en reloads DefaultSeedLocal (:345-346). DefaultSeedLocal equals the DefaultSeed parameter
  unless the build defines SIMULATION on a non-Verilator simulator: then prim_lfsr randomises it
  in about 70% of runs unless +prim_lfsr_use_default_seed=1 is passed (:250-276). Whether the
  team's VCS build defines SIMULATION is UNVERIFIED (docs/dv/SIM_RECIPE.md shows no
  +define+SIMULATION; the compile options are Runtime's): the insertion pattern after a lockup is
  reproducible only with the plusarg or without the define. Insertion never hangs either way.
- Observable at: rvfi_valid spacing: dummy stalls continue after the write and the program reaches
  its end marker (no hang); probe candidate P1 (probe register entry needed; wrapper-internal seam
  net): dummy_instr_id_o insertion sequence before/after the write, which is the only way to see
  the reload value.
- Config: secureseed write value; +prim_lfsr_use_default_seed plusarg (if SIMULATION is defined).
- Source: RTL-defined: rtl/ibex_dummy_instr.sv:66-74; vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv:
  250-276,298-299,345-346
- Edge: yes, of F-DIT-014
- Status: ACTIVE
- Notes: Critic C-05 correction (v1 said "reloads DefaultSeed"). Owner question 11: does the VCS
  build define SIMULATION; if yes the regression should pass +prim_lfsr_use_default_seed=1.

### F-DIT-026: secureseed access corner cases
- What: (a) A write while dummy_instr_en = 0 still reseeds (seed_en is independent of enable).
  (b) csrrs/csrrc with rs1 = x0 are read-only ops and do not reseed (csr_we_int needs csr_wr).
  (c) U-mode access is an illegal instruction (0x7C1 is M-mode only). (d) Reads return 0.
- Observable at: rvfi_trap (c), rvfi_rd_wdata = 0 (d), insertion pattern (a,b).
- Config: privilege mode, cpuctrlsts.dummy_instr_en.
- Source: doc: doc/03_reference/cs_registers.rst "Security Feature Seed Register (secureseed)" |
  RTL-defined: rtl/ibex_cs_registers.sv:403-406,673-675,1011,1020-1023,1914
- Edge: yes, of F-DIT-014
- Status: ACTIVE

### F-DIT-027: Back-to-back dummy instructions (mask = 000, threshold 0)
- What: With mask 000 the threshold is 0..3; when the next LFSR value gives threshold 0 the
  counter (cleared to 0 on insertion) matches immediately, so two or more dummies can be
  inserted consecutively.
- Observable at: rvfi_valid gap of exactly +2 between two single-cycle records (two one-cycle
  dummies back to back); probe candidate P1 (probe register entry needed; wrapper-internal seam
  net): dummy_instr_id_o high in two consecutive accepted ID cycles.
- Config: cpuctrlsts.dummy_instr_mask = 000.
- Source: RTL-defined: rtl/ibex_dummy_instr.sv:97-115
- Edge: yes, of F-DIT-011
- Status: ACTIVE
- Notes: Depth-2 chain fixed (Critic C-13): the parent was F-DIT-012, now folded into F-DIT-011.

### F-DIT-028: No dummy insertion while fetch is disabled or the core sleeps
- What: Insertion requires id_in_ready and a valid real instruction in IF (if_id_pipe_reg_we);
  with fetch_enable_i not On (halt_if) or in SLEEP/WAIT_SLEEP no dummies enter ID and the
  counter does not advance.
- Observable at: no rvfi_valid and no new icache line allocation while fetch_enable_i != On
  (remaining beats of open fill buffers are legal, X-5) or core_busy_o == Off, and no extra gaps
  once fetch resumes beyond the resume latency (negative check); probe candidate P1 (probe
  register entry needed; wrapper-internal seam nets): zero insertion EVENTS (if_id_pipe_reg_we
  with insert_dummy_instr) in the window. The dummy_instr_id_o LEVEL is not the observable: it is
  updated only on if_id_pipe_reg_we and holds 1 for the whole Off window when the last accepted
  instruction before the edge was a dummy (rtl/ibex_if_stage.sv:538-544; rtl-arch fact-check
  TP-DIT-030, X-22).
- Config: cpuctrlsts.dummy_instr_en, fetch_enable_i, WFI.
- Source: RTL-defined: rtl/ibex_dummy_instr.sv:103-104; rtl/ibex_if_stage.sv:568-570,587;
  rtl/ibex_controller.sv:598-621,996-999
- Edge: yes, of F-DIT-011
- Status: ACTIVE

### F-DIT-029: Dummy operand hazard against a load in WB
- What: A dummy whose LFSR-chosen rs1/rs2 equals the rd of a load still in WB is subject to the
  load-data hazard exactly like a real instruction (the dummy is a normal ID-stage instruction).
  The hazard adds NO extra cycle: every instruction behind an outstanding load already waits in ID
  until the response (instr_executing requires ~outstanding_memory_access,
  rtl/ibex_id_stage.sv:1015-1016,1059-1062), so a dummy after a load adds exactly its own class
  latency to the post-load gap whether or not it reads the load's rd (rtl-arch fact-check
  TP-DIT-031, UNOBSERVABLE).
- Observable at: the post-load gap between rvfi_valid records is bounded by load latency + the
  dummy's class latency, hazard or not (boundary); the hazard itself is visible only on P1
  (rf_raddr_a_o / rf_raddr_b_o == the load's rd at the insertion event), coverage only.
- Config: cpuctrlsts.dummy_instr_en.
- Source: RTL-defined: rtl/ibex_dummy_instr.sv:144; rtl/ibex_id_stage.sv:1111-1120 (stall_ld_hz =
  outstanding_load_wb & (rf_rd_a_hz | rf_rd_b_hz))
- Edge: yes, of F-DIT-015
- Status: ACTIVE

### F-DIT-030: Interrupt arrives while a dummy DIV occupies ID for the full divider latency
- What: Explicit cross of F-DIT-019 with the dummy kind (gen_hierarchy_map.md H-Y2): a dummy DIV
  (37-cycle divider latency, D7; always full-length with DIT on, F-DIT-009) holds ID through
  stall_multdiv (rtl/ibex_id_stage.sv:910-917,955-962), so an interrupt arriving in that window
  waits until the dummy completes (handle_irq is honoured only with !stall && !id_wb_pending,
  rtl/ibex_controller.sv:700-721; stall = stall_id_i | stall_wb_i, :1017). The interrupt entry
  latency is therefore bounded by the divider latency plus the plain entry latency; the dummy
  leaves no record and mepc is the PC of the next real instruction (pc_if,
  rtl/ibex_if_stage.sv:532-535).
- Observable at: rvfi_ext_irq_valid pulse and rvfi_intr on the handler's first record; the gap
  between the last pre-interrupt rvfi_valid and the handler record (bounded by 37 plus the plain
  entry latency measured with dummies disabled); no rvfi_valid record for the dummy; csrr
  read-back on rvfi_rd_wdata of mepc = rvfi_pc_rdata of the first post-handler record.
- Config: cpuctrlsts.dummy_instr_en, cpuctrlsts.dummy_instr_mask, cpuctrlsts.data_ind_timing,
  mie/mstatus.MIE, debug_req_i (same wait for the debug variant, F-DIT-020).
- Source: RTL-defined: rtl/ibex_controller.sv:700-721,1017; rtl/ibex_id_stage.sv:910-917,955-962;
  rtl/ibex_dummy_instr.sv:117-141; rtl/ibex_multdiv_fast.sv:428-446; gen_hierarchy_map.md H-Y2
- Edge: yes, of F-DIT-011
- Status: ACTIVE
- Notes: NEW for Critic C-09 item 8. Distinct from F-DIT-019 by the timing coincidence (the
  interrupt lands inside a 37-cycle dummy) and the expected outcome (entry latency bound).

---------------------------------------------------------------------------------------------------
## SEC: security features and alerts at the ibex_core boundary
---------------------------------------------------------------------------------------------------

### F-SEC-001: alert_minor_o is driven only by the ICache ECC error
- What: alert_minor_o = icache_ecc_error (single source). It is a pulse, one cycle per detected
  error, and is not sticky. Nothing else in ibex_core feeds it (lockstep minor alert is an
  ibex_top addition).
- Observable at: alert_minor_o.
- Config: cpuctrlsts.icache_enable (cache must be in use for an ECC error to be detected).
- Source: doc: doc/02_user/integration.rst "Interfaces" (alert_minor_o row) | doc:
  doc/03_reference/security.rst "ICache ECC" | RTL-defined: rtl/ibex_core.sv:1337,613;
  rtl/ibex_top.sv:1369 (not in DUT)
- Edge: no
- Status: ACTIVE
- Notes: ICache-internal behaviour (which errors, tweak infection) is owned by the ICache part;
  this entry covers only the alert mapping and its pulse semantics.

### F-SEC-002: alert_major_internal_o source enumeration
- What: alert_major_internal_o = rf_ecc_err_comb | pc_mismatch_alert | csr_shadow_err |
  cheriot_fatal_err | cheriot_enable_mubi_err. In this DUT: rf_ecc_err_comb is 0 unless the
  wrapper sets RegFileECC=1 (F-SEC-004); csr_shadow_err is constant 0 (ShadowCSR = 0,
  F-SEC-010); cheriot_fatal_err is 0 with CHERIoT off (only set when cheriot_enable_i == On,
  rtl/ibex_cs_registers.sv:2221-2222); cheriot_enable_mubi_err is 0 with a valid tie
  (F-SEC-013). The only live source with the expected wrapper is pc_mismatch_alert
  (F-SEC-007). The output is combinational (level while the condition holds), not sticky.
- Observable at: alert_major_internal_o.
- Config: none (fault injection only).
- Source: doc: doc/02_user/integration.rst "Interfaces" (alert_major_internal_o row: "pulse, but
  might be set for multiple cycles") | doc: doc/03_reference/security.rst "Outputs" | RTL-defined:
  rtl/ibex_core.sv:1349-1351
- Edge: no
- Status: ACTIVE
- Notes: There is no controller-FSM glitch / one-hot alert source; those checks are
  simulation-only assertions (F-SEC-011).

### F-SEC-003: alert_major_bus_o source enumeration (bus integrity, MemECC)
- What: alert_major_bus_o = lsu_load_resp_intg_err | lsu_store_resp_intg_err | instr_intg_err.
  With MemECC = 1 the 39-bit instr_rdata_i / data_rdata_i carry inverted SECDED(39,32) check
  bits; any decoder error (correctable or not) on a cycle with rvalid raises the alert for that
  cycle. Data write data (data_wdata_o[38:32]) carries generated check bits. If the wrapper sets
  MemECC = 0 all three terms are constant 0 and the alert is tied low.
- Observable at: alert_major_bus_o (pulse aligned with instr_rvalid_i / data_rvalid_i),
  data_wdata_o[38:32].
- Config: none.
- Source: doc: doc/03_reference/security.rst "Bus integrity checking" | RTL-defined:
  rtl/ibex_core.sv:1353,50-51,74,84,86; rtl/ibex_if_stage.sv:258-282;
  rtl/ibex_load_store_unit.sv:376-396,731-738,756-757
- Edge: no
- Status: ACTIVE
- Notes: The internal NMI raised on a load/store integrity error and the mtval/mcause encoding
  belong to the interrupt part (rtl/ibex_controller.sv:395-448). ibex_top's additional bus-alert
  sources (trvk revocation-bitmap errors, rtl/ibex_top.sv:1365-1368) are NOT in the DUT.

### F-SEC-004: Register-file ECC check inside ibex_core (RegFileECC)
- What: When RegFileECC=1, ibex_core encodes rf_wdata_wb into a 39-bit inverted SECDED word
  (rf_wdata_wb_ecc_o) and decodes both read ports; any error on a port that is actually read
  (rf_ren_x), not being forwarded from WB (~(rf_rd_x_wb_match & rf_write_wb)), while
  instr_valid_id, sets rf_ecc_err_comb -> alert_major_internal_o. No correction is done. With
  RegFileECC=0 (ibex_top's choice) the 32-bit data passes straight through and the term is 0.
- Observable at: alert_major_internal_o (level while the faulty operand is being read in ID); with
  RegFileECC=0 (Q-002 default) a negative check: it never fires. The seam nets rf_wdata_wb_ecc_o /
  rf_rdata_a_ecc_i / rf_rdata_b_ecc_i are wrapper-internal, not observables: probe candidate P10
  (probe register entry needed), fault injection and coverage only.
- Config: none (requires fault injection into the RF flops or the core-RF wires inside the DUT).
- Source: doc: doc/03_reference/security.rst "Register file ECC" (describes the lockstep-based
  scheme, not the in-core one) | RTL-defined: rtl/ibex_core.sv:47-48,1214-1242,1291-1319;
  rtl/ibex_top.sv:215-217,539 (RegFileECC=0, RegFileDataWidth=32, WordZeroVal)
- Edge: no
- Status: ACTIVE
- Notes: Q-002 default RegFileECC=0 (mirrors ibex_top): RF ECC is unverifiable in this DUT and
  F-SEC-004 (with F-SEC-005/006 folded here) and F-DIT-022 are negative checks (alert never
  fires). If a later ruling sets RegFileECC=1 the RF must be instantiated with DataWidth=39,
  WordZeroVal = SecdedInv3932ZeroWord (39'h2A00000000,
  vendor/lowrisc_ip/ip/prim/rtl/prim_secded_pkg.sv:275) and RegFileCapEccWidth = REGCAP_W+7 =
  42 (F-CHERI-001 notes).

### F-SEC-005: RF ECC error masked by same-cycle writeback forwarding
- What: FOLDED into F-SEC-004: the parent's own qualification term `~(rf_rd_x_wb_match &
  rf_write_wb)` (a corrupted register being written by WB in the same cycle is forwarded, not
  read, so it is not flagged); Critic C-12 pattern a.
- Observable at: alert_major_internal_o stays 0 for that read (negative with RegFileECC=0 anyway).
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1281-1286,1298-1299
- Edge: yes, of F-SEC-004
- Status: FOLDED into F-SEC-004 (bin CG-RST-004.cr_fwd_bank.yes_x1_15; CG-RST-004.cr_fwd_bank.yes_x16; CG-RST-004.cr_fwd_bank.yes_x17_31)

### F-SEC-006: RF ECC error on a register that is addressed but not read
- What: FOLDED into F-SEC-004: the parent's own rf_ren_a / rf_ren_b qualification (a register
  index carried by an encoding that does not read it, e.g. an I-type immediate aliasing rs2,
  cannot alert); Critic C-12 pattern a.
- Observable at: alert_major_internal_o stays 0 (negative with RegFileECC=0 anyway).
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1283,1286
- Edge: yes, of F-SEC-004
- Status: FOLDED into F-SEC-004 (bin CG-SEC-001.cp_internal_total.zero)

### F-SEC-007: Hardened PC (PC increment check, PCIncrCheck)
- What: The IF stage remembers whether the previous instruction was sequential and checks that
  pc_if equals pc_id + (2 if compressed else 4). The check is disarmed after any branch_req
  (jump, taken branch, exception, interrupt, debug entry, boot), after a fetch error, for dummy
  instructions, while inside a Zcmp expansion (INSTR_EXPANDED / INSTR_EXPANDED_COMMIT) and after
  reset (prev_instr_seq_q resets to 0). A mismatch drives pc_mismatch_alert ->
  alert_major_internal_o as a level.
- Observable at: alert_major_internal_o.
- Config: none (fault injection on the IF PC path).
- Source: doc: doc/03_reference/security.rst "Hardened PC" | RTL-defined:
  rtl/ibex_if_stage.sv:658-692; rtl/ibex_core.sv:196,232,628,1350
- Edge: no
- Status: ACTIVE

### F-SEC-008: PC check across compressed/uncompressed instruction sizes
- What: FOLDED into F-SEC-007: the parent's increment rule (pc_id + 2 if compressed else 4,
  rtl/ibex_if_stage.sv:679,688) applied to mixed 16/32-bit straight-line code including a 32-bit
  instruction straddling a word boundary; one term of the parent's rule with the same observable
  and outcome (Critic C-12 pattern a).
- Observable at: alert_major_internal_o = 0 throughout mixed-size straight-line code.
- Config: none.
- Source: RTL-defined: rtl/ibex_if_stage.sv:679,688
- Edge: yes, of F-SEC-007
- Status: FOLDED into F-SEC-007 (bin CG-RVFI-001.cp_pc_delta.plus2; CG-RVFI-001.cp_pc_delta.plus4; CG-SEC-001.cp_internal_total.zero)

### F-SEC-009: PC check re-arming after a Zcmp expanded sequence
- What: prev_instr_seq_d is cleared while instr_gets_expanded is INSTR_EXPANDED or
  INSTR_EXPANDED_COMMIT but not for INSTR_EXPANDED_LAST, so the check resumes on the last
  micro-op using pc_id (the cm.* instruction PC) + 2 as the expected next PC.
- Observable at: alert_major_internal_o = 0 after cm.push/cm.pop/cm.mvsa01/cm.mva01s and
  their successors.
- Config: none.
- Source: RTL-defined: rtl/ibex_if_stage.sv:667-669; rtl/ibex_pkg.sv:319-324
- Edge: yes, of F-SEC-007
- Status: ACTIVE

### F-SEC-010: Shadow CSRs are compiled out (ShadowCSR = 0); csr_shadow_err is constant 0
- What: ibex_core hard-codes ShadowCSR = 1'b0 so every ibex_csr instance uses gen_no_shadow and
  rd_error_o = 0. csr_shadow_err_o (= mstatus_err | mtvec_err | pmp_csr_err | cpuctrlsts_part_err
  | cpuctrlsts_ic_scr_key_err) is therefore 0 and can never raise alert_major_internal_o. The
  shadow mechanism itself (complemented copy, compare every cycle) exists in rtl/ibex_csr.sv but
  is unreachable in this build.
- Observable at: alert_major_internal_o never fires from CSR glitches (negative check only).
- Config: none.
- Source: doc: doc/03_reference/security.rst "Shadow CSRs" ("not currently used when the
  SecureIbex parameter is set") | RTL-defined: rtl/ibex_core.sv:197,1436; rtl/ibex_csr.sv:38-53;
  rtl/ibex_cs_registers.sv:1072-1083,1170-1181,1938-1949,1973-1987
- Edge: no
- Status: ACTIVE
- Notes: The set that WOULD be shadowed: mstatus, mtvec, pmpcfg/pmpaddr/mseccfg, cpuctrlsts
  (part), cpuctrlsts.ic_scr_key_valid, and the CHERIoT mshwm/mshwmb/cdbg_ctrl flops.

### F-SEC-011: Controller FSM and exception-priority integrity are assertion-only
- What: The controller has no glitch detector feeding an alert. IbexCtrlStateValid (state is one
  of the ten legal encodings) and IbexExceptionPrioOnehot are SVA checks compiled under
  INC_ASSERT; they do not drive alert_major_internal_o.
- Observable at: alert_major_internal_o stays 0 (negative check: neither property reaches a port).
  The FSM-state and priority one-hot properties are assertion coverage, not observables: the RTL
  assertions IbexCtrlStateValid / IbexExceptionPrioOnehot are compiled under INC_ASSERT and the TB
  binds its own copies (gen_sva_ctrl_state_valid / gen_sva_exc_prio_onehot in gen_binds.sv) so that
  the assertion summary and cover counts are collected per run.
- Config: none.
- Source: RTL-defined: rtl/ibex_controller.sv:373-383,1104-1106; rtl/ibex_core.sv:1349-1351
- Edge: no
- Status: ACTIVE
- Notes: The lockstep comparison that would catch FSM faults is in ibex_top (rtl/ibex_top.sv:873)
  and is out of scope.

### F-SEC-012: fetch_enable_i must be exactly IbexMuBiOn; invalid encodings behave as Off
- What: FOLDED into F-RST-010: with SecureIbex the fetch gate compares the full 4-bit
  fetch_enable_i against IbexMuBiOn (rtl/ibex_core.sv:637-649; rtl/ibex_pkg.sv:752-760); Off
  (4'b1010) and every other encoding stop fetch and execution identically and raise no alert.
  Restates F-RST-010 / F-RST-014 (Critic C-12 pattern c).
- Observable at: instr_req_o stops, rvfi_valid stops, alert outputs unchanged.
- Config: none.
- Source: doc: doc/02_user/integration.rst "Interfaces" (fetch_enable_i row) | RTL-defined:
  rtl/ibex_core.sv:637-649; rtl/ibex_pkg.sv:752-760
- Edge: yes, of F-RST-010
- Status: FOLDED into F-RST-010 (bin CG-RST-003.cp_transition.on2inv; CG-SEC-005.cp_fetch_en_val.invalid)

### F-SEC-013: cheriot_enable_i invalid MuBi encoding raises alert_major_internal_o
- What: While instr_exec (fetch_enable_i == On) the core flags cheriot_enable_i that is neither
  On (0101) nor Off (1010). With the wrapper tie to IbexMuBiOff this is unreachable; if the tie
  were X/invalid the alert would be a permanent level whenever fetch is enabled.
- Observable at: alert_major_internal_o.
- Config: none (wrapper tie).
- Source: RTL-defined: rtl/ibex_core.sv:1339-1347,1350-1351
- Edge: no
- Status: ACTIVE
- Notes: The gate by instr_exec means the alert is also silent while fetch_enable_i is not On.

### F-SEC-014: core_busy_o multi-bit encoding (SecureIbex)
- What: core_busy_o is an ibex_mubi_t built bit-by-bit from separate prim_buf copies of
  ctrl_busy, if_busy and lsu_busy: each bit equals the corresponding IbexMuBiOn bit when any
  source is busy and the IbexMuBiOff bit otherwise. It never takes an invalid encoding.
- Observable at: core_busy_o (On = 4'b0101 while busy, Off = 4'b1010 when idle in sleep).
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:496-522,190
- Edge: no
- Status: ACTIVE
- Notes: ibex_top derives clock_en / core_sleep_o from this (rtl/ibex_top.sv:303-331) - not in
  the DUT (see F-RST-016).

### F-SEC-015: Load data write suppressed on a bus integrity error (rf_wr_suppress)
- What: When the beat that COMPLETES a load arrives with bad check bits the RF write is suppressed
  (lsu_rdata_valid_o = IDLE & rvalid & ~err & ~we & ~data_intg_err,
  rtl/ibex_load_store_unit.sv:697-698; rvfi_ext_rf_wr_suppress = instr_done_wb & ~rf_we_wb_o &
  outstanding_load_wb & lsu_load_resp_intg_err, rtl/ibex_core.sv:2384-2385) while
  alert_major_bus_o pulses and the internal NMI is raised. The instruction still retires. Per-beat
  rule (rtl-arch fact-check X-11): the suppression keys only on the integrity of the completing
  beat; for a misaligned load whose FIRST beat is corrupted and whose second beat is clean the
  first-half status has no integrity term (lsu_err_d = data_bus_err_i | pmp_err_q, :514), so the
  merged data IS written to rd (rf_wr_suppress = 0) while the alert (:756) and the internal NMI
  still fire.
- Observable at: rvfi_ext_rf_wr_suppress, rvfi_rd_addr / rvfi_rd_wdata (write present or absent),
  alert_major_bus_o, the internal-NMI handler record (rvfi_ext_nmi_int).
- Config: none.
- Source: doc: doc/03_reference/security.rst:88 "Where load data has bad checkbits the write to
  the load's destination register will be suppressed" | RTL-defined:
  rtl/ibex_core.sv:2379-2398,1353; rtl/ibex_load_store_unit.sv:514,697-698,756
- Edge: no
- Status: ACTIVE
- Notes: Bug candidate B16 (rtl-arch BUG-08, bug log v1d; security-relevant, owner question
  Q-015): the first-beat class contradicts the documented intent (security.rst:88), so the
  checker follows the doc and the first-beat class is its own expected-fail item (TP-SEC-040;
  RVFI view TP-RVFI-040); the aligned and second-beat classes pass (TP-SEC-008, TP-RVFI-024).
  The internal NMI may be taken up to two ordinary instructions after the corrupted response
  (X-10, D21) and its mtval is lsu_addr_last at the corrupted beat (the word-aligned second-half
  address when the second half was granted before the first response). gen_bug_log.md B16 names
  F-SEC-017 as the canonical D-side integrity feature; this entry is the load-suppression feature
  the bug describes (F-SEC-017 is the spurious-response entry) - alignment item for the DV Lead.

### F-SEC-016: Store response with a bus integrity error
- What: FOLDED into F-SEC-003: the lsu_store_resp_intg_err OR term of the parent (a store
  response with bad check bits pulses alert_major_bus_o; there is no RF write to suppress);
  Critic C-12 pattern a.
- Observable at: alert_major_bus_o, rvfi_ext_rf_wr_suppress stays 0.
- Config: none.
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:757; rtl/ibex_core.sv:1353
- Edge: yes, of F-SEC-003
- Status: FOLDED into F-SEC-003 (bin CG-SEC-002.cr_side_op.dbus_store; CG-SEC-001.cr_alert_inject.major_bus_dbus_store_intg)

### F-SEC-017: Integrity error on an unexpected (spurious) data response
- What: g_check_mem_response gates load/store errors and RF writes with "a response is expected"
  (outstanding_*_wb | expecting_*_resp_id), but alert_major_bus_o uses the raw
  lsu_*_resp_intg_err terms, so a spurious data_rvalid_i with bad check bits still pulses the bus
  alert while causing no exception and no RF write. The internal NMI is ALSO raised:
  mem_resp_intg_err (rtl/ibex_id_stage.sv:613) is not qualified by an outstanding access, so the
  controller's pending flag is set (rtl/ibex_controller.sv:413-417,436) and the handler is
  entered with mcause 0xFFFFFFE0 and mtval = the stale lsu_addr_last (rtl-arch fact-check
  TP-SEC-010, WRONG-RTL-FACT).
- Observable at: alert_major_bus_o = 1, rvfi_trap = 0, no RF write, an internal-NMI handler
  record (rvfi_ext_nmi_int = 1).
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1181-1186,1353; rtl/ibex_load_store_unit.sv:756-757;
  rtl/ibex_id_stage.sv:613; rtl/ibex_controller.sv:413-417,436
- Edge: yes, of F-SEC-003
- Status: ACTIVE
- Notes: The NoMemResponseWithoutPendingAccess assertion (rtl/ibex_core.sv:1390-1391) will fire
  under INC_ASSERT; such a test must waive it. Out-of-spec stimulus: bug-log S3 (informational
  item TP-SEC-010, Q-DL-9). Per-beat rule and B16 (bug log v1d names this entry as the canonical
  D-side integrity feature): suppression of the load's RF write keys only on the integrity of the
  beat that completes the access (rtl/ibex_load_store_unit.sv:514,697-698; X-11); a misaligned
  load whose FIRST beat is corrupted writes merged data to rd while the alert and the internal NMI
  fire - bug candidate B16 (rtl-arch BUG-08, security-relevant, owner question Q-015), carried as
  the expected-fail items TP-SEC-040 / TP-RVFI-040; the load-suppression feature itself is
  F-SEC-015.

### F-SEC-018: Instruction fetch integrity error on a speculative fetch
- What: instr_intg_err is asserted with instr_rvalid_i for any returned word with bad check bits,
  whether or not that word is ever executed (prefetch after a branch, second half of a discarded
  line). The alert pulses immediately; the exception (instruction access fault) only occurs if
  the erroneous word reaches ID.
- Observable at: alert_major_bus_o pulse without a matching rvfi_trap.
- Config: none.
- Source: RTL-defined: rtl/ibex_if_stage.sv:276-282; rtl/ibex_core.sv:1353
- Edge: yes, of F-SEC-003
- Status: ACTIVE

### F-SEC-019: Spurious data response without integrity error is ignored (secure response check)
- What: With SecureIbex, data_rvalid_i when no load/store is outstanding does not cause a
  load/store error exception (even with data_err_i = 1) and does not write the RF.
- Observable at: rvfi_trap = 0, no rf write, alert outputs 0.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1181-1186
- Edge: yes, of F-SEC-003
- Status: ACTIVE
- Notes: Same assertion waiver as F-SEC-017.

### F-SEC-020: mcounteren_writable_i MuBi gate on mcounteren writes
- What: A CSR write to mcounteren takes effect only when mcounteren_writable_i == IbexMuBiOn;
  any other encoding silently drops the write (read returns the old value). No alert.
- Observable at: rvfi_rd_wdata of a following csrr mcounteren; U-mode counter access legality.
- Config: mcounteren, privilege mode; mcounteren_writable_i tie.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:844-845,122; rtl/ibex_core.sv:186
- Edge: no
- Status: ACTIVE
- Notes: Owner question: what does gen_dut_top tie mcounteren_writable_i to (On, Off, or a TB
  knob)? Off makes mcounteren read-only zero and all U-mode counter reads illegal.

### F-SEC-021: ICache scramble-key request/valid at the DUT boundary and cpuctrlsts.ic_scr_key_valid
- What: Alias of F-IC-011: SEC perspective of the ic_scr_key_req_o / ic_scr_key_valid_i handshake
  and of cpuctrlsts bit 8 (read-only, one-flop delayed copy of ic_scr_key_valid_i), see canonical.
- Observable at: ic_scr_key_req_o; csrr read-back on rvfi_rd_wdata of cpuctrlsts bit 8;
  rvfi_ext_ic_scr_key_valid.
- Config: cpuctrlsts.icache_enable; ic_scr_key_valid_i driven by the TB.
- Source: RTL-defined: rtl/ibex_core.sv:115-116,575-576,1532; rtl/ibex_cs_registers.sv:236-238,
  666-670,1938-1949
- Edge: no
- Status: ALIAS of F-IC-011

### F-SEC-022: double_fault_seen_o and cpuctrlsts.sync_exc_seen / double_fault_seen
- What: On every synchronous exception taken outside debug mode (csr_save_cause & not an
  interrupt & not debug entry) cs_registers sets cpuctrlsts.sync_exc_seen; if it was already set
  the core pulses double_fault_seen_o for exactly one cycle and sets the sticky
  cpuctrlsts.double_fault_seen. MRET clears sync_exc_seen. Both bits are also software writable;
  writing double_fault_seen has no effect on the output.
- Observable at: double_fault_seen_o (1-cycle pulse); csrr read-back on rvfi_rd_wdata of
  cpuctrlsts bits 6/7.
- Config: cpuctrlsts.sync_exc_seen / double_fault_seen (software writes), privilege mode.
- Source: doc: doc/03_reference/exception_interrupts.rst "Double Fault Detection" | doc:
  doc/03_reference/cs_registers.rst "CPU Control and Status Register (cpuctrlsts)" (bits 6,7) |
  RTL-defined: rtl/ibex_cs_registers.sv:239-246,769,890-947,953-965,1967-1968;
  rtl/ibex_core.sv:131,1546
- Edge: no
- Status: ACTIVE

### F-SEC-023: Double fault detection is inactive in debug mode and on debug entry
- What: Folded into F-SEC-022: the parent's arming condition already excludes exceptions taken in
  debug mode and debug entry itself (csr_save_cause & not debug entry, outside debug mode); the
  debug case is that condition evaluated false with the parent's double_fault_seen_o = 0 observable
  (v2 edge rule, second pass; Critic M-9); carried by the debug-mode bins.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:910-918,935-945
- Edge: yes, of F-SEC-022
- Status: FOLDED into F-SEC-022 (bin CG-SEC-003.cp_debug_mode.yes)

### F-SEC-024: Interrupt or NMI between two synchronous exceptions
- What: Alias of F-EXC-055: SEC perspective (interrupts and NMIs neither set nor clear
  sync_exc_seen, so a synchronous exception inside an interrupt handler that pre-empted an exception
  handler is a double fault; the mret of an NMI handler clears the flag, the B12 behaviour stated by
  F-EXC-056), see canonical.
- Edge: yes, of F-SEC-022
- Status: ALIAS of F-EXC-055

### F-SEC-025: Software-written sync_exc_seen / double_fault_seen
- What: csrw cpuctrlsts with bit 6 = 1 arms the detector so the next synchronous exception is a
  double fault; writing bit 7 = 0 clears the sticky bit; writing bit 7 = 1 sets it without
  pulsing double_fault_seen_o.
- Observable at: double_fault_seen_o, cpuctrlsts read-back.
- Config: cpuctrlsts writes.
- Source: doc: doc/03_reference/exception_interrupts.rst "Double Fault Detection" ("writing ...
  has no effect on the double_fault_seen_o output") | RTL-defined: rtl/ibex_cs_registers.sv:
  874-877,1967-1968
- Edge: yes, of F-SEC-022
- Status: ACTIVE

### F-SEC-026: CSR write to cpuctrlsts coinciding with an exception in WB
- What: The write path sets cpuctrlsts_part_d from the CSR data and the exception path then
  overrides only sync_exc_seen/double_fault_seen ("exception controller gets priority",
  rtl/ibex_cs_registers.sv:890). Whether a cpuctrlsts write in ID can be committed in the same
  cycle a WB load/store error is taken needs RTL confirmation (wb_exception_o blocks ID
  execution); if it cannot, this is unreachable and should be documented as such.
- Observable at: csrr read-back on rvfi_rd_wdata of cpuctrlsts after the handler.
- Config: cpuctrlsts write racing a faulting load/store.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:871-877,890-945; rtl/ibex_controller.sv:335-337
- Edge: yes, of F-SEC-022
- Status: ACTIVE
- Notes: Candidate RTL/Arch question.

### F-SEC-027: crash_dump_o field semantics
- What: crash_dump_o.current_pc = pc_id (PC of the instruction in ID/EX), next_pc = pc_if (PC
  the IF stage will deliver next), last_data_addr = LSU addr_last_q (address of the most recent
  data transaction, updated on each request), exception_pc = mepc, exception_addr = mtval. All
  are live (combinational from flops), meant to be captured on reset by the SoC.
- Observable at: crash_dump_o.{current_pc,next_pc,last_data_addr,exception_pc,exception_addr}.
- Config: none.
- Source: doc: doc/02_user/integration.rst "Interfaces" (crash_dump_o row) | RTL-defined:
  rtl/ibex_core.sv:1325-1330,1503; rtl/ibex_pkg.sv:16-22; rtl/ibex_load_store_unit.sv:258-264,743;
  rtl/ibex_cs_registers.sv:1028,1031
- Edge: no
- Status: ACTIVE
- Notes: The relation of current_pc/next_pc to rvfi_pc_rdata/pc_wdata gives a cheap checker:
  when rvfi_valid the previous cycle's crash_dump values are consistent with the retiring
  instruction only for a 2-stage view; with WritebackStage the ID PC is one instruction ahead.

### F-SEC-028: crash_dump_o.last_data_addr for a misaligned (split) access
- What: addr_last_d = addr_incr_req ? data_addr_w_aligned : data_addr, so after a misaligned
  load/store the field holds the word-aligned address of the second transaction, not the
  instruction's effective address.
- Observable at: crash_dump_o.last_data_addr vs rvfi_mem_addr.
- Config: none.
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:258,743; rtl/ibex_core.sv:1328
- Edge: yes, of F-SEC-027
- Status: ACTIVE

### F-SEC-029: crash_dump_o values out of reset
- What: last_data_addr, exception_pc and exception_addr reset to 0 (addr_last_q, mepc, mtval
  reset values). current_pc/next_pc come from IF-stage PC flops that are reset only when ResetAll
  = 1 (rtl/ibex_if_stage.sv:589-592; parameter rtl/ibex_core.sv:42). With the Q-002 default
  ResetAll=1 both read 0 in reset; next_pc (the icache address register loaded by the RESET-state
  pc_set, rtl/ibex_icache.sv:1147-1160,1193) takes the boot vector in BOOT_SET, while current_pc
  (= pc_id, rtl/ibex_if_stage.sv:601,613) STAYS 0 through RESET, BOOT_SET and FIRST_FETCH and
  first changes when the first fetched instruction enters ID (pc_id updates only on
  if_id_pipe_reg_we; rtl-arch fact-check TP-SEC-031, X-23). Without ResetAll they would be X
  until the first fetch.
- Observable at: crash_dump_o during and just after reset.
- Config: none.
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:261-262; rtl/ibex_cs_registers.sv:1088-1100,
  1149-1158 (mepc/mtval ResetValue '0); rtl/ibex_core.sv:42; rtl/ibex_if_stage.sv:589-592
- Edge: yes, of F-SEC-027
- Status: ACTIVE
- Notes: Resolved by Q-002 default ResetAll=1 (as ibex_top via Lockstep): the X-checker on
  crash_dump_o runs from time 0 (F-RST-009, TP-SEC-031).

### F-SEC-030: crash_dump_o.exception_pc/exception_addr are frozen in debug mode
- What: Folded into F-SEC-027: exception_pc / exception_addr are mepc / mtval by the parent's
  definition, and exceptions in debug mode do not write them (F-PRV-005); the frozen value is that
  rule seen through the parent's fields (v2 edge rule, second pass; Critic M-9); carried by the
  parent's debug-mode bins.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:910-931
- Edge: yes, of F-SEC-027
- Status: FOLDED into F-SEC-027 (bin CG-SEC-004.cp_debug_mode.yes, CG-SEC-004.cr_exc_debug.exception_pc_yes_no)

### F-SEC-031: cpuctrlsts register layout and access rules
- What: Alias of F-CSR-085: SEC perspective of the cpuctrlsts (0x7C0) layout and access rules
  (bit 8 RO, bits 7/6 RW, 5:3 / 2 / 1 / 0 WARL, 31:9 zero; M-mode only), see canonical. The
  reserved-bit write behaviour (F-SEC-032) is folded here and carried by CG-DIT-001.cp_wr_reserved.
- Observable at: csrr read-back on rvfi_rd_wdata of cpuctrlsts; rvfi_trap + csrr read-back of
  mcause for a U-mode access.
- Config: cpuctrlsts, privilege mode.
- Source: doc: doc/03_reference/cs_registers.rst "CPU Control and Status Register (cpuctrlsts)" |
  RTL-defined: rtl/ibex_cs_registers.sv:239-246,666-670,874-877,1888-1889,1938-1949,1973-1984
- Edge: no
- Status: ALIAS of F-CSR-085

### F-SEC-032: cpuctrlsts write with reserved or read-only bits set
- What: Folded into F-CSR-085 (the canonical of the SEC alias F-SEC-031): writes to bits 31:9 and to
  bit 8 are dropped (the cast to the 8-bit part struct, rtl/ibex_cs_registers.sv:1888-1889; bit 8 is
  loaded only from ic_scr_key_valid_i, :1938-1949), which the canonical already states. Bits 6/7 are
  plain RW for software: a csrrw/csrrs/csrrc sets or clears them exactly as written (the raw write
  value is passed through at :1967-1968 and written on every cpuctrlsts write at :874-876;
  cs_registers.rst:551-557 marks both RW), so a read-modify-write does NOT need to preserve them and
  the checker models software writes as applied (Critic C-05 correction; software-written bits are
  F-SEC-025).
- Observable at: csrr read-back on rvfi_rd_wdata of cpuctrlsts.
- Config: cpuctrlsts writes.
- Source: doc: doc/03_reference/cs_registers.rst:551-557 (bits 6/7 RW) | RTL-defined:
  rtl/ibex_cs_registers.sv:874-876,1888-1889,1938-1949,1967-1968
- Edge: yes, of F-CSR-085
- Status: FOLDED into F-CSR-085 (bin CG-DIT-001.cp_wr_reserved.bits31_9; CG-DIT-001.cp_wr_reserved.bit8; CG-DIT-001.cp_wr_reserved.both; CG-SEC-005.cp_bits67_readback.b6_1_b7_1)

### F-SEC-033: cpuctrlsts.icache_enable is forced off in debug mode
- What: Alias of F-IC-040: cpuctrlsts perspective of icache_enable forced off in debug mode
  (icache_enable_o = cpuctrlsts.icache_enable & ~(debug_mode | debug_mode_entering),
  rtl/ibex_cs_registers.sv:1970-1971; the CSR bit reads back unchanged), see canonical.
- Observable at: instr_req_o pattern (no cache fills) while rvfi_ext_debug_mode = 1; csrr read-back
  on rvfi_rd_wdata of cpuctrlsts bit 0 unchanged.
- Config: cpuctrlsts.icache_enable, debug_req_i.
- Source: RTL-defined: rtl/ibex_cs_registers.sv:1970-1971
- Edge: yes, of F-SEC-031
- Status: ALIAS of F-IC-040

### F-SEC-034: Alert outputs are combinational levels, not sticky, and are cleared by reset
- What: None of the alert sources is latched at the ibex_core boundary: rf_ecc_err_comb and
  pc_mismatch_alert hold while their condition holds (possibly several cycles when ID is
  stalled), cheriot_enable_mubi_err holds while the input is invalid, bus integrity terms are
  one cycle per rvalid, alert_minor_o is a pulse. Asserting rst_ni clears every contributing
  flop.
- Observable at: alert_minor_o, alert_major_internal_o, alert_major_bus_o.
- Config: none.
- Source: doc: doc/02_user/integration.rst "Interfaces" (alert rows) | RTL-defined:
  rtl/ibex_core.sv:1337,1350-1353; rtl/ibex_if_stage.sv:688; rtl/ibex_load_store_unit.sv:756-757
- Edge: no
- Status: ACTIVE

### F-SEC-035: Alert outputs during reset and in the cycle after reset release
- What: While rst_ni is low the alert outputs still follow their combinational inputs:
  alert_major_bus_o follows data_rvalid_i/instr_rvalid_i with bad check bits, and
  alert_major_internal_o follows cheriot_enable_mubi_err (fetch_enable_i == On and an invalid
  cheriot_enable_i). With quiescent inputs all three are 0 during reset and in the first cycles
  after release (prev_instr_seq_q = 0, instr_valid_id = 0).
- Observable at: alert_* during rst_ni = 0 and the first cycles after.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1337-1353; rtl/ibex_if_stage.sv:671-676;
  rtl/ibex_load_store_unit.sv:756-757
- Edge: yes, of F-SEC-034
- Status: ACTIVE

### F-SEC-036: What ibex_top adds around ibex_core (explicitly NOT in the DUT)
- What: ibex_top adds: the lockstep shadow core and comparators (Lockstep = SecureIbex) with its
  own alert outputs; the RF-ECC-in-shadow scheme (RegFileLockstepECC); scrambled ICache RAMs
  (prim_ram_1p_scr) with the scramble key/nonce handshake and RAM cfg pass-through; the ibex_trvk
  capability revocation unit on the data bus (CHERIoT); the core clock gate driven by core_busy
  and core_sleep_o = ~clock_en; prim_buf on fetch_enable_i/mcounteren_writable_i; alert OR-ing
  (core | lockstep | icache RAM mubi | trvk). None of these are DUT features.
- Observable at: the gen_dut_top port list at elaboration (no core_sleep_o, scramble_key_*,
  ram_cfg_*, lockstep or trvk ports); TP-SEC-037 compares it with gen_tb_scoping_notes a.2.
- Config: none.
- Source: doc: doc/02_user/integration.rst "Core Integration" | doc:
  doc/03_reference/security.rst "Dual core lockstep", "Register file ECC" | RTL-defined:
  rtl/ibex_top.sv:212-219,303-336,345-353,623-671,685-849,873,1360-1369
- Edge: no
- Status: ACTIVE

### F-SEC-037: marchid / mvendorid / mimpid identification values
- What: Alias of F-CSR-019: SEC perspective of the identification CSRs (marchid =
  CSR_MARCHID_VALUE = 22 with CHERIoT off, 0xCE1 only when cheriot_enable_i == On; mvendorid =
  CsrMvendorId = 0; mimpid = CsrMimpId = 0; mhartid = hart_id_i live), see canonical.
- Observable at: rvfi_rd_wdata of csrr marchid/mvendorid/mimpid/mhartid.
- Config: none.
- Source: doc: doc/02_user/integration.rst "Identification CSRs" | RTL-defined:
  rtl/ibex_cs_registers.sv:422-430; rtl/ibex_pkg.sv:727-728; rtl/ibex_core.sv:56-59
- Edge: no
- Status: ALIAS of F-CSR-019

---------------------------------------------------------------------------------------------------
## RST: reset and boot
---------------------------------------------------------------------------------------------------

### F-RST-001: rst_ni is an active-low asynchronous reset for all core state
- What: Every state element in ibex_core and ibex_register_file_ff uses
  always_ff @(posedge clk_i or negedge rst_ni) with the reset branch first, so assertion of
  rst_ni takes effect immediately (asynchronously) and release is sampled on the next clock edge.
  There is no synchronous reset input and no reset synchroniser in the DUT.
- Observable at: every output port (instr_req_o, data_req_o, alert_*_o, core_busy_o, rvfi_valid,
  crash_dump_o, ...) returns to its reset value within the reset-assert cycle (F-RST-009).
- Config: none.
- Source: doc: doc/02_user/integration.rst "Interfaces" (rst_ni row: "Active-low asynchronous
  reset") | RTL-defined: e.g. rtl/ibex_controller.sv:1030-1040; rtl/ibex_csr.sv:28-34;
  rtl/ibex_register_file_ff.sv:118-124; rtl/ibex_core.sv:2007-2067
- Edge: no
- Status: ACTIVE

### F-RST-002: Reset vector = {boot_addr_i[31:8], 8'h80}
- What: The first fetch after reset goes to boot_addr_i with the low byte forced to 0x80.
  boot_addr_i[7:0] is ignored (tied off as unused) and an assertion requires it to be 0 (256-byte
  alignment).
- Observable at: instr_addr_o of the first instr_req_o after reset; rvfi_pc_rdata of the first
  record.
- Config: none (boot_addr_i is a static input).
- Source: doc: doc/02_user/integration.rst "Interfaces" (boot_addr_i row: "First program
  counter after reset = boot_addr_i + 0x80") | spec:
  tools/specs/riscv-isa-manual/src/priv/machine.adoc "Reset" ("The pc is set to an
  implementation-defined reset vector") | RTL-defined: rtl/ibex_if_stage.sv:243,199,932;
  rtl/ibex_controller.sv:582-596
- Edge: no
- Status: ACTIVE

### F-RST-003: boot_addr_i is consumed only in the RESET and BOOT_SET cycles
- What: PC_BOOT is selected with pc_set in the RESET and BOOT_SET states (the first two cycles
  after reset release) and mtvec is initialised from boot_addr_i in the same BOOT_SET cycle
  (csr_mtvec_init = pc_set & pc_mux == PC_BOOT). After that boot_addr_i has no effect until the
  next reset (the remaining PC_BOOT/default mux arms are unreachable without a branch predictor).
- Observable at: instr_addr_o and csrr read-back on rvfi_rd_wdata of mtvec unchanged when
  boot_addr_i changes mid-run (F-RST-025 folded here; CG-SEC-005.cp_event.boot_addr_change).
- Config: none.
- Source: RTL-defined: rtl/ibex_controller.sv:582-596; rtl/ibex_if_stage.sv:241-256;
  rtl/ibex_cs_registers.sv:736-743
- Edge: no
- Status: ACTIVE

### F-RST-004: mtvec after boot = boot_addr_i[31:8] with vectored MODE
- What: mtvec has ResetValue 32'd1, then BOOT_SET writes {boot_addr_i[31:8], 6'b0, 1'b0, 1'b1}
  (MODE = 01 vectored) so software reading mtvec before writing it sees boot_addr | 1.
- Observable at: rvfi_rd_wdata of csrr mtvec before any mtvec write; exception target addresses.
- Config: none.
- Source: doc: doc/03_reference/cs_registers.rst "Machine Trap-Vector Base Address (mtvec)"
  ("Reset Value: 0x0000_0001") | RTL-defined: rtl/ibex_cs_registers.sv:736-743,1170-1181;
  rtl/ibex_if_stage.sv:256
- Edge: no
- Status: ACTIVE
- Notes: The documented reset value (1) is only visible for one cycle and never to software; the
  architecturally visible boot value is RTL-defined.

### F-RST-005: hart_id_i is read live by mhartid
- What: Alias of F-CSR-020: RST perspective (mhartid returns hart_id_i combinationally; it is not
  sampled at reset), see canonical.
- Observable at: rvfi_rd_wdata of csrr mhartid tracks hart_id_i changes.
- Config: none.
- Source: doc: doc/02_user/integration.rst "Interfaces" (hart_id_i row "usually static") |
  RTL-defined: rtl/ibex_cs_registers.sv:430
- Edge: no
- Status: ALIAS of F-CSR-020

### F-RST-006: Privilege and mstatus reset state
- What: priv_lvl resets to M. mstatus resets to MIE=0, MPIE=1, MPP=U(00), MPRV=0, TW=0 (reads
  0x0000_0080).
- Observable at: rvfi_mode of the first record = 3; rvfi_rd_wdata of csrr mstatus = 0x80;
  interrupts not taken until MIE is set.
- Config: none.
- Source: spec: tools/specs/riscv-isa-manual/src/priv/machine.adoc "Reset" (priv = M; MIE and
  MPRV = 0) | doc: doc/03_reference/cs_registers.rst "Machine Status (mstatus)" ("Reset Value:
  0x0000_0080") | RTL-defined: rtl/ibex_cs_registers.sv:987-993,1052-1056,1072-1083
- Edge: no
- Status: ACTIVE
- Notes: MPIE=1 / MPP=U at reset are implementation choices (spec leaves them unspecified).

### F-RST-007: Other CSR reset values relevant to boot
- What: mcause = 0 (spec: "value indicating the cause of the reset"; 0 = most complete reset),
  mepc = 0, mie = 0, mtval = 0, mscratch = 0, dcsr = {xdebugver=4, cause=0, prv=M, rest 0},
  depc/dscratch = 0, cpuctrlsts = 0 (bit 8 tracks the input), mstack = MSTACK_RESET_VAL,
  PMP CSRs from PMPRstCfg/PMPRstAddr/PMPRstMsecCfg, mcountinhibit/mcounteren = 0.
- Observable at: CSR read-back via rvfi_rd_wdata after reset.
- Config: none.
- Source: spec: tools/specs/riscv-isa-manual/src/priv/machine.adoc "Reset" | doc:
  doc/03_reference/cs_registers.rst (mie/mepc/mcause "Reset Value" lines) | RTL-defined:
  rtl/ibex_cs_registers.sv:1085-1160 (mepc/mie/mscratch/mcause/mtval ibex_csr instances,
  ResetValue '0), 1184-1200 (dcsr), 1973-1984 (cpuctrlsts), 1450-1519 (PMP)
- Edge: no
- Status: ACTIVE
- Notes: The PMP/counter reset details belong to their own parts; listed for completeness of the
  boot-state check.

### F-RST-008: Controller boot sequence RESET -> BOOT_SET -> FIRST_FETCH -> DECODE
- What: Out of reset the controller is in RESET (cycle 0 after release: instr_req_o low, pc_set
  with PC_BOOT), then BOOT_SET (cycle 1: pc_set again, instr_req allowed, csr_mtvec_init), then
  FIRST_FETCH for exactly ONE cycle (cycle 2): it leaves when id_in_ready_o, which is 1 in an
  empty pipe (rtl/ibex_controller.sv:623-626; id_in_ready_o = ~stall & ~halt_if & ~retain_id,
  :1020), so DECODE is entered at cycle 3 and it is DECODE that waits for the first instruction
  to arrive from IF (CTRL-03; interface inventory reset paragraph). A debug_req_i or irq_nm_i
  pending at release is taken from FIRST_FETCH (F-RST-024). The first bus request appears once
  the prefetch buffer issues the boot-address fetch (the BOOT_SET cycle with fetch enabled).
- Observable at: instr_req_o first rises in the BOOT_SET cycle (second cycle after release) with
  instr_addr_o = {boot_addr_i[31:8], 8'h80}; the first rvfi_valid follows after the fetch latency
  plus the ID/WB pipeline with no dependence on FIRST_FETCH (one cycle regardless of imem
  latency); core_busy_o = On from the first cycle (ctrl_busy defaults to 1).
- Config: fetch_enable_i must be On for the first request (F-RST-013).
- Source: RTL-defined: rtl/ibex_controller.sv:540-596,623-646,1017-1020,1030-1032;
  rtl/ibex_pkg.sv:290-302; rtl-arch's behaviour summaries CTRL-03
- Edge: no
- Status: ACTIVE
- Notes: Critic C-06 correction (v1 said FIRST_FETCH lasts until the first instruction is accepted
  by ID).

### F-RST-009: Reset values of the ibex_core output ports
- What: instr_req_o = 0 (controller RESET state, prefetch idle); data_req_o = 0; data_we_o/
  data_be_o/data_addr_o/data_wdata_o/data_tag_o from LSU flops (0; data_tag_o is 0 with CHERIoT
  off); ic_tag_req_o / ic_data_req_o = 0 until INVAL_CACHE; ic_scr_key_req_o is COMBINATIONAL
  from the reset-state scramble FSM and the pin (OUT_OF_RESET & ~ic_scr_key_valid_i,
  rtl/ibex_icache.sv:1221-1227,1276): it reads 1 while rst_ni = 0 and in the first post-release
  cycle whenever the TB holds ic_scr_key_valid_i = 0, and 0 only when the key is driven valid
  through reset (rtl-arch fact-check TP-RST-001); irq_pending_o = 0 (mie = 0);
  crash_dump_o per F-SEC-029; double_fault_seen_o = 0; alert_*_o = 0 given quiescent inputs
  (F-SEC-035); core_busy_o = IbexMuBiOn (ctrl_busy = 1 in RESET); rvfi_valid = 0, rvfi_mode =
  PRIV_LVL_M, rvfi_ixl = 1, all other rvfi_* = 0 / NULL_CAP; rf_we_wb_o = 0, dummy_instr_*_o =
  0 (wrapper-internal seam nets, P1 class).
- Observable at: every output port during reset and on the first cycle after release;
  rf_we_wb_o / dummy_instr_*_o are wrapper-internal seam nets (probe candidate P1) checked by the
  P1 monitor only.
- Config: none.
- Source: RTL-defined: rtl/ibex_controller.sv:565,582-587; rtl/ibex_core.sv:498-522,2007-2067;
  rtl/ibex_cs_registers.sv:1044-1045 (irq_pending_o);
  rtl/ibex_wb_stage.sv:222-241
- Edge: no
- Status: ACTIVE
- Notes: ResetAll=1 per Q-002 default: crash_dump_o.current_pc/next_pc reset to 0 (F-SEC-029)
  and the X-checker runs from time 0.

### F-RST-010: fetch_enable_i semantics (On starts, not-On stops after in-flight instructions)
- What: instr_req_gated = instr_req_int & (fetch_enable_i == IbexMuBiOn) blocks new instruction
  fetch requests, and instr_exec = (fetch_enable_i == On) drives the controller's halt_if so ID
  stops accepting instructions from IF. Instructions already in ID/EX and WB complete normally
  (including outstanding loads/stores). The assertion NoExecWhenFetchEnableNotOn encodes the
  contract.
- Observable at: instr_req_o stops rising; rvfi_valid stops after at most the instructions
  already in ID/WB; core_busy_o remains On while anything is outstanding.
- Config: none.
- Source: doc: doc/02_user/integration.rst "Interfaces" (fetch_enable_i row) | RTL-defined:
  rtl/ibex_core.sv:637-657,1394-1421; rtl/ibex_controller.sv:996-999
- Edge: no
- Status: ACTIVE
- Notes: Canonical for the IMEM alias F-IMEM-022 (M-10 pass); carries the folded F-IMEM-023 (invalid
  MuBi codes act as Off without an alert, alert_major_internal_o stays low, unlike cheriot_enable_i:
  rtl/ibex_core.sv:648-649 vs 1339-1347; CG-IMEM-005 code bins) and F-RST-011. Candidate owner
  question kept from F-IMEM-023: is silent acceptance of an invalid fetch_enable_i encoding intended
  in a SecureIbex configuration? Bus-side rule (rtl-arch fact-check X-5): fetch_enable_i != On
  stops only NEW icache lookups (req_i reaches only lookup_req_ic0, rtl/ibex_icache.sv:249); the
  remaining beats of already allocated fill buffers keep requesting (fill_ext_req = fill_busy_q &
  ~fill_ext_done_d has no req_i term, :756, :1030-1031) and a request awaiting grant is held
  until gnt, never withdrawn (:764-775); so "no new line allocation after the Off edge, beats of
  open lines legal, instr_req_o == 0 whenever core_busy_o == Off", and the ibus protocol checker
  needs no withdrawn-request tolerance.

### F-RST-011: fetch_enable_i goes Off while an LSU transaction is outstanding
- What: Folded into F-RST-010: the parent already states that instructions in ID/EX and WB complete
  normally including outstanding loads/stores; the LSU-outstanding Off edge is that sentence with
  the parent's rvfi_valid / core_busy_o observable (the bus-side in-flight statement is F-IMEM-024)
  (v2 edge rule, second pass; Critic M-9); carried by the in-flight bins.
- Source: doc: doc/02_user/integration.rst "Interfaces" (fetch_enable_i: "halt once any in-flight
  instructions in the ID/EX and WB stages have finished") | RTL-defined:
  rtl/ibex_controller.sv:996-999,1020; rtl/ibex_core.sv:1181-1186
- Edge: yes, of F-RST-010
- Status: FOLDED into F-RST-010 (bin CG-XIF-008.cp_inflight.data_outst, CG-XIF-008.cr_enc_x_inflight.mubi_off_data_outst; CG-RST-003.cp_pipe_state.id_busy)

### F-RST-012: fetch_enable_i Off then On resumes from the held PC
- What: On re-enable the IF stage delivers the instruction that was held (prefetch buffer / skid
  contents are kept, no re-fetch of already fetched words) and pc_id continues from
  pc_at_fetch_disable.
- Observable at: rvfi_pc_rdata continuity across the pause; instr_addr_o does not re-request
  already-granted addresses.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:644-649,1394-1409; rtl/ibex_controller.sv:996-999
- Edge: yes, of F-RST-010
- Status: ACTIVE

### F-RST-013: fetch_enable_i not On at reset release
- What: RESET/BOOT_SET still run (pc_set to the boot vector, mtvec initialised) but no
  instruction request leaves the core until fetch_enable_i becomes On; the first request then
  targets the boot vector.
- Observable at: instr_req_o = 0 after reset until fetch_enable_i = On; mtvec already initialised.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:648; rtl/ibex_controller.sv:582-596;
  rtl/ibex_if_stage.sv:256
- Edge: yes, of F-RST-010
- Status: ACTIVE

### F-RST-014: fetch_enable_i invalid encodings and glitches
- What: Any 4-bit value other than 0101 disables fetch; a single-cycle glitch to a non-On value
  causes at most a one-cycle fetch stall (instr_req_gated low, halt_if high) and no alert.
- Observable at: instr_req_o gap; alert outputs unchanged.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:644-649; rtl/ibex_pkg.sv:759-760
- Edge: yes, of F-RST-010
- Status: ACTIVE

### F-RST-015: Interrupt or debug request while fetch_enable_i is not On
- What: handle_irq and enter_debug_mode are not gated by instr_exec: with an empty pipeline the
  controller still moves to IRQ_TAKEN / DBG_TAKEN_IF, saves mepc/mcause (or dpc/dcsr) and asserts
  pc_set to the handler, but the handler fetch request is blocked until fetch_enable_i is On.
- Observable at: rvfi_ext_irq_valid pulse with no following rvfi_valid; csrr read-back on
  rvfi_rd_wdata of mepc/mcause (or dpc/dcsr) after re-enable; instr_req_o low while fetch_enable_i
  != On.
- Config: mie/mstatus.MIE, debug_req_i.
- Source: RTL-defined: rtl/ibex_controller.sv:498-500,623-646,700-721,725-733,996-999;
  rtl/ibex_core.sv:648
- Edge: yes, of F-RST-010
- Status: ACTIVE
- Notes: Owner question: is taking a trap while fetch is disabled acceptable (the doc only says
  fetch pauses)? The check should at least pin the RTL behaviour.

### F-RST-016: core_busy_o semantics; core_sleep_o is not a DUT port
- What: core_busy_o (mubi) is On while ctrl_busy | if_busy | lsu_busy. ctrl_busy is 0 only in
  WAIT_SLEEP and in SLEEP with no wake-up source (irq_nm, irq_pending, debug_req, debug_mode,
  single step); if_busy is the prefetch/icache busy; lsu_busy while a data transaction is
  outstanding. ibex_top turns this into the clock gate and core_sleep_o = ~clock_en; the DUT
  exposes only core_busy_o.
- Observable at: core_busy_o == IbexMuBiOff exactly when the core is asleep after WFI with no
  outstanding accesses.
- Config: WFI, mie/mstatus.MIE, debug_req_i.
- Source: doc: doc/02_user/integration.rst "Interfaces" (core_sleep_o row, ibex_top port) |
  RTL-defined: rtl/ibex_core.sv:496-522; rtl/ibex_controller.sv:598-621; rtl/ibex_top.sv:303-331
  (not in DUT)
- Edge: no
- Status: ACTIVE
- Notes: Owner question: should gen_dut_top add a core_sleep_o equivalent
  (~(core_busy != Off | debug_req_i | irq_pending | irq_nm_i)) for checking, or check
  core_busy_o directly?

### F-RST-017: core_busy_o stays On during WFI while a fetch is outstanding
- What: Folded into F-RST-016: the parent defines core_busy_o = ctrl_busy | if_busy | lsu_busy, so
  "stays On while a fetch is outstanding during WFI" is the if_busy term of the parent's formula
  with the same port observable (Critic M-9); carried by the parent's hold-cause bin.
- Source: RTL-defined: rtl/ibex_core.sv:496-522; rtl/ibex_if_stage.sv:421
- Edge: yes, of F-RST-016
- Status: FOLDED into F-RST-016 (bin CG-SEC-006.cp_hold_cause.fetch_outstanding, CG-SEC-006.cp_off_reason.none)

### F-RST-018: Mid-run reset assertion with bus transactions outstanding
- What: Asserting rst_ni mid-run returns all state to reset values immediately. The DUT cannot
  tell a late response to a pre-reset request from the answer to a new request (rtl-arch
  fact-check TP-RST-017): on the I-side any instr_rvalid_i goes to the oldest expecting fill
  buffer and the boot fetch buffer is allocated in BOOT_SET (rtl/ibex_icache.sv:851-852,700), so
  a late beat from cycle 1 after release on becomes the boot instruction (bad integrity -> alert
  AND instruction access fault at the boot vector); on the D-side a data_rvalid_i while a new
  load/store is outstanding is that access's response (rtl/ibex_load_store_unit.sv:694-698;
  rtl/ibex_wb_stage.sv:220) and with nothing outstanding the exception/RF-write paths are masked
  (rtl/ibex_core.sv:1181-1186) but a bad-integrity beat still raises alert_major_bus_o and the
  internal NMI (F-SEC-017). Responses drained while rst_ni = 0 reach only consumers held in reset
  (a bad-integrity beat still pulses the combinational alert_major_bus_o, F-SEC-035).
- Observable at: all outputs at reset values; alert_major_bus_o if the TB drains a bad-ECC beat in
  reset.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1181-1186,1390-1391; rtl/ibex_load_store_unit.sv:694-698,
  756-757; rtl/ibex_icache.sv:700,851-852; rtl/ibex_wb_stage.sv:220
- Edge: yes, of F-RST-001
- Status: ACTIVE
- Notes: The TB memory model must either drain (while rst_ni = 0) or drop responses to pre-reset
  requests, never return them after release (Q-010); a post-release late response is the
  unsolicited-response stimulus of bug-log S3 (TP-IMEM-040 / TP-SEC-010 informational items).
  Recorded policy: TP-RST-017.
  fetch_enable_i Off before or across the reset (TP-RST-019 case f) does not change this policy:
  Off stops only NEW icache lookups (req_i reaches only lookup_req_ic0), while the remaining beats
  of already allocated fill buffers keep requesting and their responses are consumed, never
  withdrawn or ignored (rtl-arch X-5; rtl/ibex_icache.sv:756-775; rtl/ibex_core.sv:553, :648;
  F-RST-010 Notes, TP-RST-009, TP-XIF-017).

### F-RST-019: Reset during a multi-cycle instruction or a split misaligned access
- What: Reset during a 37-cycle division, a Zcmp expansion or between the two halves of a
  misaligned store abandons the instruction: no second data request is issued after release,
  no RF write, no RVFI record, and the LSU FSM restarts in IDLE.
- Observable at: data_req_o count, rvfi_valid absence, first post-reset instr_addr_o = boot
  vector.
- Config: none.
- Source: RTL-defined: rtl/ibex_load_store_unit.sv:640-656; rtl/ibex_controller.sv:1030-1040;
  rtl/ibex_core.sv:2007-2067
- Edge: yes, of F-RST-001
- Status: ACTIVE

### F-RST-020: test_en_i, scan_rst_ni and ram_cfg ports are not on ibex_core
- What: test_en_i (clock gate test enable, also routed to the RF where the FF implementation
  leaves it unused), scan_rst_ni (DFT reset mux) and ram_cfg_icache_{tag,data}_{i,o} (RAM
  configuration pass-through to prim_ram_1p*) exist only on ibex_top. gen_dut_top must tie the RF
  test_en_i (any value; unused) and has no scan/ram_cfg to drive.
- Observable at: the gen_dut_top port list at elaboration (absence of test_en_i at the top,
  scan_rst_ni and ram_cfg_*).
- Config: none.
- Source: doc: doc/02_user/integration.rst "Interfaces" (test_en_i, scan_rst_ni, ram_cfg rows) |
  RTL-defined: rtl/ibex_top.sv:70-74,194,685-849; rtl/ibex_register_file_ff.sv:65,232-233
- Edge: no
- Status: ACTIVE

### F-RST-021: Register file reset values (x0 hard zero, x1..x31 reset to zero)
- What: In the g_cheriot_rf layout used because BaseIsa = RV32IorCHERIoT, x1..x15 data flops and
  the x16..x31 shared flops reset to WordZeroVal / CapWordZeroVal. With RegFileDataWidth = 32
  the WordZeroVal ibex_top passes (RegFileDataWidth'(SecdedInv3932ZeroWord)) truncates to
  32'h0, so every register reads 0 after reset. x0 reads 0 for real instructions (the dummy
  shadow register also resets to 0).
- Observable at: rvfi_rs1_rdata/rvfi_rs2_rdata of the first instructions reading unwritten
  registers = 0.
- Config: none.
- Source: spec: tools/specs/riscv-isa-manual/src/priv/machine.adoc "Reset" ("All other hart state
  is UNSPECIFIED") | doc: doc/03_reference/register_file.rst "Register File" | RTL-defined:
  rtl/ibex_register_file_ff.sv:56,59,116-142,164-186; rtl/ibex_top.sv:539;
  vendor/lowrisc_ip/ip/prim/rtl/prim_secded_pkg.sv:275
- Edge: no
- Status: ACTIVE
- Notes: If gen_dut_top chooses RegFileECC=1 with DataWidth=39 the reset value becomes the
  39-bit zero codeword 0x2A00000000 (data bits still 0). Owner question (see F-SEC-004).

### F-RST-022: x16..x31 storage in the shared bank (non-CHERIoT mode)
- What: With CHERIoT off, writes with waddr[4] = 1 go to the 35-bit rf_shared flops
  (zero-extended data) and reads with raddr[4] = 1 return the low 32 bits; x16 uses the special
  rf_shared[0] flop (we_shared_r0 path when DummyInstructions = 1). Behaviour must be
  indistinguishable from a flat 31-entry RF.
- Observable at: rvfi_rs*_rdata / rvfi_rd_wdata for x16..x31, especially x16 and x31.
- Config: none.
- Source: RTL-defined: rtl/ibex_register_file_ff.sv:99-113,128-142,159-161,175-186,221-224
- Edge: yes, of F-RST-021
- Status: ACTIVE

### F-RST-023: Same-cycle RF write and read of the same register
- What: The RF has no write-to-read forwarding; the ID stage forwards WB data itself
  (rf_rd_*_wb_match). Reading a register that WB is writing in the same cycle must return the
  new value at the architectural level. Forwarding covers ALU, CSR, mul and div producers only
  (rf_wdata_fwd_wb_o = rf_wdata_wb_q, rtl/ibex_wb_stage.sv:212-215: "load data returns too late");
  a consumer of a LOAD result stalls on stall_ld_hz while the load is in WB
  (rtl/ibex_id_stage.sv:1114-1120) and reads the RF one cycle after the load's WB, so a load ->
  consumer record gap is 2, never 1 (rtl-arch fact-check TP-RST-023, TIMING).
- Observable at: rvfi_rs*_rdata equals the previous instruction's rvfi_rd_wdata (gap 1 for
  non-load producers, gap 2 for load producers).
- Config: none.
- Source: doc: doc/03_reference/register_file.rst "Register File" ("no write to read forwarding
  path") | RTL-defined: rtl/ibex_register_file_ff.sv:116-126; rtl/ibex_id_stage.sv:1111-1120;
  rtl/ibex_wb_stage.sv:212-215
- Edge: yes, of F-RST-021
- Status: ACTIVE

### F-RST-024: Interrupt or debug request pending at reset release
- What: A pending interrupt at boot is not taken (mstatus.MIE = 0, mie = 0) so the first
  instruction executes; a pending debug_req_i is taken from FIRST_FETCH before any instruction
  executes (DBG_TAKEN_IF) with dpc = boot vector and dcsr.cause = haltreq. An NMI (irq_nm_i)
  pending at boot is taken before the first instruction (not maskable).
- Observable at: rvfi_ext_debug_req / rvfi_ext_debug_mode on the first record, rvfi_ext_irq_valid;
  csrr read-back on rvfi_rd_wdata of dpc / mepc.
- Config: mie, debug_req_i, irq_nm_i.
- Source: RTL-defined: rtl/ibex_controller.sv:498-500,623-646; rtl/ibex_cs_registers.sv:1052-1056,
  1102-1110
- Edge: yes, of F-RST-008
- Status: ACTIVE

### F-RST-025: boot_addr_i changed after boot has no effect
- What: FOLDED into F-RST-003: a change of boot_addr_i after BOOT_SET changes neither the PC nor
  mtvec (PC_BOOT is selected only in RESET/BOOT_SET, rtl/ibex_controller.sv:582-596;
  csr_mtvec_init only there, rtl/ibex_if_stage.sv:256); restates the parent (Critic C-12
  pattern c).
- Observable at: instr_addr_o; csrr read-back on rvfi_rd_wdata of mtvec.
- Config: none.
- Source: RTL-defined: rtl/ibex_if_stage.sv:243,256; rtl/ibex_controller.sv:582-596
- Edge: yes, of F-RST-003
- Status: FOLDED into F-RST-003 (bin CG-SEC-005.cp_event.boot_addr_change; CG-SEC-005.cp_boot_addr_change_ctx.running)

### F-RST-026: First RVFI record after reset has rvfi_order = 1
- What: FOLDED into F-RVFI-003: rvfi_stage_order resets to 0 so the first retired instruction
  after every reset is recorded with rvfi_order = 0 + 1 (rtl/ibex_core.sv:1905,2012); the parent
  already states "starts at 1 after reset" (Critic C-12 pattern c).
- Observable at: rvfi_order of the first rvfi_valid.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1905,2012
- Edge: yes, of F-RVFI-003
- Status: FOLDED into F-RVFI-003 (bin CG-RVFI-001.cp_order_step.first)

### F-RST-027: misa reflects the RV32I base after reset (CHERIoT off)
- What: misa.I = 1, misa.E = 0, misa.X = (RV32BExtra != 0) with cheriot_enable_i != On; the
  register is read-only.
- Observable at: rvfi_rd_wdata of csrr misa.
- Config: none.
- Source: spec: tools/specs/riscv-isa-manual/src/priv/machine.adoc "Reset" (misa maximal set) |
  doc: doc/03_reference/cs_registers.rst "Machine ISA Register (misa)" | RTL-defined:
  rtl/ibex_cs_registers.sv:373-391
- Edge: no
- Status: ACTIVE

---------------------------------------------------------------------------------------------------
## RVFI: RISC-V Formal Interface outputs of ibex_core
---------------------------------------------------------------------------------------------------

The riscv-formal RVFI specification (rvfi.md) is NOT on disk; doc/03_reference/rvfi.rst only
links to it. All semantics below are therefore RTL-defined and cited to rtl/ibex_core.sv. The
ports exist only when the RVFI macro is defined (RISCV_FORMAL or RVFI, rtl/ibex_core.sv:7-9,136).

### F-RVFI-001: RVFI port inventory of this RTL
- What: Standard fields: rvfi_valid, rvfi_order[63:0], rvfi_insn[31:0], rvfi_trap, rvfi_halt,
  rvfi_intr, rvfi_mode[1:0], rvfi_ixl[1:0], rvfi_rs1_addr/rs2_addr/rs3_addr[4:0],
  rvfi_rs1_rdata/rs2_rdata/rs3_rdata[31:0], rvfi_rd_addr[4:0], rvfi_rd_wdata[31:0],
  rvfi_pc_rdata/pc_wdata[31:0], rvfi_mem_addr[31:0], rvfi_mem_rmask/wmask[3:0],
  rvfi_mem_rdata/wdata[31:0]. CHERIoT fields (cap_t, all NULL_CAP/0 with CHERIoT off):
  rvfi_rs1_rcap, rvfi_rs2_rcap, rvfi_rd_wcap, rvfi_mem_is_cap, rvfi_mem_rcap, rvfi_mem_wcap.
  Ibex extensions: rvfi_ext_pre_mip[31:0], rvfi_ext_post_mip[31:0], rvfi_ext_nmi,
  rvfi_ext_nmi_int, rvfi_ext_debug_req, rvfi_ext_debug_mode, rvfi_ext_rf_wr_suppress,
  rvfi_ext_mcycle[63:0], rvfi_ext_mhpmcounters[10][31:0], rvfi_ext_mhpmcountersh[10][31:0],
  rvfi_ext_ic_scr_key_valid, rvfi_ext_irq_valid, rvfi_ext_expanded_insn_valid,
  rvfi_ext_expanded_insn[15:0], rvfi_ext_expanded_insn_last. There are NO rvfi_csr_* ports.
- Observable at: the listed rvfi_* ports (presence and width at elaboration; TP-RVFI-001).
- Config: none.
- Source: doc: doc/03_reference/rvfi.rst "RISC-V Formal Interface" | RTL-defined:
  rtl/ibex_core.sv:133-181
- Edge: no
- Status: ACTIVE

### F-RVFI-002: rvfi_valid timing (two-stage tracking pipeline with WritebackStage)
- What: Stage 0 captures the instruction when it leaves ID/EX (rvfi_id_done) and holds while it
  sits in WB; stage 1 (the output) becomes valid the cycle after the instruction leaves WB
  (rvfi_wb_done = stage0 valid & (instr_done_wb | trap)). rvfi_valid is a one-cycle pulse per
  instruction; all outputs come straight from flops.
- Observable at: rvfi_valid exactly one cycle after the data_rvalid_i that completed a load in
  WB (boundary); for non-load instructions the WB completion is visible only as the record itself
  (rf_we_wb_o is a wrapper-internal seam net, probe candidate P1 class, not an observable).
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1654-1660,1855-1890,2069
- Edge: no
- Status: ACTIVE

### F-RVFI-003: rvfi_order increments by exactly 1 per retired instruction
- What: rvfi_stage_order_d = order + 1 for every non-dummy instruction, including trapping ones
  and every Zcmp micro-op; 64-bit, starts at 1 after reset, never repeats or skips.
- Observable at: rvfi_order.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1905,2012,2076
- Edge: no
- Status: ACTIVE

### F-RVFI-004: rvfi_insn encoding for compressed and expanded instructions
- What: For a 16-bit instruction that is not expanded, rvfi_insn = {16'b0, instr_rdata_c};
  otherwise (32-bit, or a Zcmp micro-op) rvfi_insn = instr_rdata_id (the 32-bit decoded/expanded
  form).
- Observable at: rvfi_insn.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:2263-2269
- Edge: no
- Status: ACTIVE

### F-RVFI-005: rvfi_trap for synchronous exceptions; rvfi_halt is constant 0
- What: rvfi_trap is set when the instruction raises an exception in ID (id_exception, excluding
  ebreak that enters debug mode) or in WB (exc_req_wb: load/store error). Trapping instructions
  are pushed through the tracking pipeline even though the core flushes them, so they appear as
  one record with rvfi_trap = 1. rvfi_halt is always 0.
- Observable at: rvfi_trap, rvfi_halt.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1842-1853,1885-1890,2073-2074,2145
- Edge: no
- Status: ACTIVE

### F-RVFI-006: rvfi_intr marks the first instruction of an INTERRUPT handler only
- What: rvfi_set_trap_pc is set when pc_set with PC_EXC and exc_pc_mux == EXC_PC_IRQ; the next
  instruction to finish ID gets rvfi_intr = 1. Synchronous exception handlers (EXC_PC_EXC),
  debug entry (EXC_PC_DBD) and NMI (EXC_PC_IRQ, so yes for NMI) follow from this: exception
  handlers' first instruction has rvfi_intr = 0.
- Observable at: rvfi_intr.
- Config: mie/mstatus.MIE, irq inputs.
- Source: RTL-defined: rtl/ibex_core.sv:2400-2425
- Edge: no
- Status: ACTIVE
- Notes: Spec gap: riscv-formal's definition of rvfi_intr ("first instruction of a trap handler")
  cannot be checked against the on-disk sources; Ibex restricts it to interrupts/NMIs.

### F-RVFI-007: rvfi_mode and rvfi_ixl
- What: rvfi_mode = priv_mode_id sampled at rvfi_id_done (3 = M, 0 = U); rvfi_ixl = CSR_MISA_MXL
  = 1 (RV32). Reset values are M and 1. rvfi_mode may change only when the previous record is a
  trap / mret / dret record or the current record is the first after an interrupt or debug entry:
  interrupt entry and debug entry from U set priv <- M without a trap record
  (rtl/ibex_cs_registers.sv:908; the handler / debug-ROM record carries rvfi_intr = 1 or
  rvfi_ext_debug_mode = 1) and dret restores priv <- dcsr.prv (:950) (rtl-arch fact-check
  TP-RVFI-007).
- Observable at: rvfi_mode, rvfi_ixl.
- Config: privilege mode (mret to U), interrupts and debug entry from U, dret into U.
- Source: RTL-defined: rtl/ibex_core.sv:2014-2015,2078-2079; rtl/ibex_pkg.sv:225-229,709;
  rtl/ibex_cs_registers.sv:908,950
- Edge: no
- Status: ACTIVE

### F-RVFI-008: rs1/rs2/rs3 address and read data capture
- What: rs1/rs2 are captured in the first ID cycle and are zero when the register port is not
  read (rf_ren_a/rf_ren_b); the data is the forwarded operand (multdiv_operand_a/b_ex =
  rf_rdata_*_fwd) so it reflects a same-cycle WB writeback. rs3 is captured from RF read port A in
  EVERY non-first ID cycle of a multi-cycle instruction (rtl/ibex_core.sv:2316-2317) and is zero
  for single-cycle instructions; the decoder drives the rs3 field (instr[31:27]) on port A only
  for ternary ops (use_rs3, rtl/ibex_decoder.sv:203), so on mulh / div / misaligned load-store /
  DIT two-cycle branch records rvfi_rs3_addr = the rs1 field and rvfi_rs3_rdata = the rs1 value
  (rtl-arch fact-check TP-RVFI-009).
- Observable at: rvfi_rs1_addr/rs2_addr/rs3_addr, rvfi_rs1_rdata/rs2_rdata/rs3_rdata.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:2284-2337,760-761 (id_stage operand assign at
  rtl/ibex_id_stage.sv:760-761); rtl/ibex_decoder.sv:203
- Edge: no
- Status: ACTIVE
- Notes: The ISA model comparison must accept rs3 as an Ibex-specific field (used by ternary
  bitmanip such as cmov/fsl/fsr and by multi-cycle sequences); "rs3_addr != 0" alone does not
  identify a ternary op: compare rs3 against instr[31:27] only for ternary ops and against rs1 for
  the other multi-cycle records.

### F-RVFI-009: rd_addr / rd_wdata capture in WB; zero when no write or rd = x0
- What: With WritebackStage the output stage captures rd_addr/rd_wdata when the RF write happens
  (rf_we_wb | rf_we_lsu); rd_wdata for loads is rf_wdata_lsu. If the instruction writes no
  register, or writes x0, rd_addr and rd_wdata are 0.
- Observable at: rvfi_rd_addr, rvfi_rd_wdata.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1805-1807,2168-2176,2339-2377
- Edge: no
- Status: ACTIVE

### F-RVFI-010: pc_rdata and pc_wdata
- What: rvfi_pc_rdata = pc_id at ID done; rvfi_pc_wdata = branch_target_ex if pc_set is asserted
  in that cycle, else pc_if. For jumps/taken branches (and DIT not-taken branches) this is the
  target; for straight-line code it is the next sequential PC. RTL-defined (rtl-arch fact-check
  X-1): trap, mret and dret records carry the NEXT SEQUENTIAL fetch address (pc_if), never the
  redirect target: mret/dret leave ID in the DECODE cycle (rtl/ibex_id_stage.sv:991,1130; the
  controller sets retain_id and decides FLUSH, rtl/ibex_controller.sv:664-680) and their pc_set
  (PC_ERET / PC_DRET) is issued one cycle later in FLUSH (:953-965); ID-stage trap records are
  captured in the DECODE cycle through rvfi_flush_next (rtl/ibex_core.sv:1851-1853;
  rtl/ibex_controller.sv:1122) while PC_EXC is set in FLUSH (:826-833). Only branches and jumps
  (pc_set in their ID-exit cycle) carry the target; fence.i is a jump to pc + 4
  (rtl/ibex_decoder.sv:711-720), so its pc_wdata is both its target and the next sequential
  address.
- Observable at: rvfi_pc_rdata, rvfi_pc_wdata; a redirect target is observed as the NEXT record's
  rvfi_pc_rdata (or the DmHaltAddr / DmExceptionAddr / vector fetch on the ibus with the icache
  off).
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1851-1853,2083-2084; rtl/ibex_controller.sv:664-680,
  826-833,953-965,1122; rtl/ibex_id_stage.sv:991,1130; rtl/ibex_decoder.sv:711-720
- Edge: no
- Status: ACTIVE
- Notes: Candidate owner question 6 (pc_wdata of FLUSH-redirect records) is RESOLVED by X-1: the
  value is pc_if (next sequential fetch address) and is compared as such (TP-RVFI-012); the
  comparator observes the target on the following record (TB Infra convention C-1). Related:
  B13 (jalr to an odd target keeps bit 0 in pc_wdata, rtl/ibex_core.sv:2084 with the raw
  branch_target_ex) stands. Evidence (TB Infra first green export run, dv/auto_dv/evidence/gen_tdd_export.md attempt 3 (b)): the seed-7 program's single trap record (order 466, ecall at 0x80002164) has pc_wdata 0x80002168 = pc + 4, not the handler 0x80001700, confirming the RTL-defined rule above and convention C-1; the export test's pc-continuity rule excludes trap, mret and dret records (gen_ut_export.py); rtl-arch T-102 fact R1 (dv/auto_dv/evidence/gen_t102_rtl_facts.md) confirms mret/dret pc_wdata = pc_if (+4 for a 32-bit instruction, +2 for c.ebreak) from rtl/ibex_core.sv:2084. Zcmp precision (rtl-arch R9, dv/auto_dv/evidence/gen_t102_rtl_facts.md, confirmed by tb-infra run red_zcmp_trap): a trapping non-last cm.* micro-op record, and an illegal cm.* encoding, report pc_wdata == pc_rdata == the cm.* pc (offset 0), because expansion holds the fetch (rtl/ibex_if_stage.sv:809-810) and pc_if stays at the cm.* pc for every micro-op except the last; the whole sequence restarts from micro-op 0 after mret (flush_expanded, rtl/ibex_if_stage.sv:482-483); the export continuity rule excludes trap and micro-op records; the comparator rule is TB Infra's T-102c (T-134, landed 18470dd: the trapping micro-op ends the sequence and is compared as its last record).
### F-RVFI-011: mem_addr / rmask / wmask for loads and stores (single record, unshifted mask)
- What: rvfi_mem_addr = lsu_addr captured in the first ID cycle (the effective, possibly
  misaligned, byte address). rmask/wmask are derived from lsu_type only: word 4'b1111, half
  4'b0011, byte 4'b0001, placed at bit 0 regardless of address offset; rmask for loads, wmask for
  stores (the other is 0). A misaligned access that splits into two bus transactions produces
  ONE record.
- Observable at: rvfi_mem_addr, rvfi_mem_rmask, rvfi_mem_wmask vs data_addr_o/data_be_o.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:2085-2086,2206-2219,2252-2261
- Edge: no
- Status: ACTIVE
- Notes: The mask is relative to mem_addr, not to the aligned word. An ISA-model comparison that
  expects word-lane masks must translate. Bug candidate B18 (rtl-arch BUG-10, bug log v1d;
  RVFI-only, no architectural effect): the mask is derived from lsu_type without an LSU-request
  qualifier (rtl/ibex_core.sv:2085, :2253-2260; wmask is clean only because data_we_o is
  decode-qualified), so EVERY non-store record that is not a load (ALU, CSR, branch, jump,
  ID-stage trap) shows rvfi_mem_rmask = 4'b1111 and rvfi_mem_addr = the ALU adder result (and
  rvfi_mem_rdata = the previous load's data), whereas rvfi.rst:135-136, 143-144 wants rmask
  nonzero only for memory operations and addr to hold the accessed location. Masks are zeroed
  only for WB-trap records (:2156-2157). Consequence: the mask / address rules of
  gen_chk_rvfi_proto and the comparator apply only to records DECODED as loads or stores
  (TP-RVFI-014 checker caveat; TP-RVFI-029 for ID-trap records); no expected-fail item. Evidence (dv/auto_dv/evidence/gen_tdd_export.md attempt 3 (a)): a store's RVFI record retires a few cycles after the memory model sees the bus store (WB waits for the response; the tohost store, order 170, landed after a flush marker taken 4 cycles after the end-of-test edge), confirming the record-versus-dbus timing anchors (S21, C-3) used by the TP-DMEM store-timing items.
### F-RVFI-012: mem_rdata and mem_wdata contents
- What: rvfi_mem_rdata is the LSU result (rf_wdata_lsu) captured when lsu_resp_valid: already
  byte-selected and sign/zero-extended, and for a misaligned load the merged value of both
  halves. rvfi_mem_wdata is the unshifted store data (lsu_wdata) from the first ID cycle.
- Observable at: rvfi_mem_rdata, rvfi_mem_wdata vs data_rdata_i/data_wdata_o.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:2206-2251
- Edge: no
- Status: ACTIVE
- Notes: For a lb of 0xFF, rvfi_mem_rdata = 0xFFFFFFFF, not 0x000000FF.

### F-RVFI-013: Record of a load/store that faults (bus error or PMP) in WB
- What: The record carries rvfi_trap = 1 (rvfi_trap_wb), rmask/wmask forced to 0, rd_addr/
  rd_wdata 0 (no RF write happened), mem_addr = effective address.
- Observable at: rvfi_trap, rvfi_mem_rmask/wmask = 0, rvfi_rd_addr = 0.
- Config: PMP config, data_err_i.
- Source: RTL-defined: rtl/ibex_core.sv:1888,2145,2156-2157,2339-2363
- Edge: yes, of F-RVFI-011
- Status: ACTIVE

### F-RVFI-014: Fault on the second half of a misaligned load/store
- What: Still one record: rvfi_trap = 1, masks 0, rvfi_mem_addr = first (misaligned) address.
  The first half's bus write (for a store) has already happened, so memory state and the RVFI
  record diverge from an ISA model that treats the access atomically.
- Observable at: rvfi_mem_addr, rvfi_trap; data_we_o first-half write on the bus.
- Config: PMP region boundary or data_err_i on the second transaction.
- Source: RTL-defined: rtl/ibex_core.sv:2206-2219,2156-2157; rtl/ibex_load_store_unit.sv:403,
  481-484
- Edge: yes, of F-RVFI-011
- Status: ACTIVE
- Notes: Candidate owner question on the comparison policy for partially performed misaligned
  stores. Depth-2 chain fixed (Critic C-13): the parent was F-RVFI-013.

### F-RVFI-015: ID exception while WB is already faulting (single trap record)
- What: If a load/store in WB raises an exception in the same cycle the instruction in ID would
  raise its own (e.g. illegal instruction), rvfi_id_done suppresses the ID-stage trace
  (~wb_exception_o) so only one rvfi_trap record (the WB one) is emitted; the ID instruction is
  re-executed after the handler and traced then.
- Observable at: exactly one rvfi_trap record; rvfi_order continuity.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:1847-1853; rtl/ibex_controller.sv:335-337
- Edge: yes, of F-RVFI-005
- Status: ACTIVE

### F-RVFI-016: Interrupt/NMI/debug notification via rvfi_ext_irq_valid and captured state
- What: When the pipeline has emptied to take an interrupt/NMI (not a debug request) and nothing
  was captured yet, rvfi_irq_valid is set for one cycle and the mip/nmi/nmi_int/debug_req state
  at the trap decision cycle is pushed up the RVFI pipeline (visible on rvfi_ext_pre_mip,
  rvfi_ext_nmi, rvfi_ext_nmi_int, rvfi_ext_debug_req together with rvfi_ext_irq_valid). Captured
  values are cleared when a new instruction enters ID and re-captured for a later debug request
  or NMI. RTL-defined level semantics (rtl-arch fact-check X-16): the port rvfi_ext_irq_valid is
  a LEVEL, not a pulse: it rises four cycles after the decision cycle (rvfi_irq_valid flop
  :1965-1971, stage [0] :1992-2002, stage [1] :2134-2141, stage [2] = the port :1837 with
  RVFI_STAGES = 2, :2192-2199), stays high until about two cycles after the handler's first
  instruction enters ID (stage [0] is rewritten only when a new instruction enters ID; one cycle
  only with same-cycle gnt and next-cycle rvalid), never coincides with rvfi_valid (the last
  pre-interrupt record is out by decision + 1) and is NOT generated at all when ID emptied before
  WB drained (captured_valid already set, :1965): the handler's first record then carries the
  captured state without a marker.
- Observable at: rvfi_ext_irq_valid (rising edge = one notification), rvfi_ext_pre_mip,
  rvfi_ext_nmi, rvfi_ext_nmi_int, rvfi_ext_debug_req.
- Config: mie/mstatus.MIE, irq inputs, debug_req_i.
- Source: RTL-defined: rtl/ibex_core.sv:1837,1907-2004,2130-2141,2188-2199
- Edge: no
- Status: ACTIVE
- Notes: Checkers count marker rising edges (at most one per interrupt entry) and accept an entry
  without a marker whose handler first record carries the captured state (TP-RVFI-019); the
  predicted marker offset from the last pre-interrupt record's rvfi_valid is 3 cycles
  (GEN_RVFI_IRQ_MARKER_OFFSET, pinned at bring-up; rtl-arch's architecture fact-check 2.1 corrected from
  N+3 to N+4 for the decision-to-port offset).

### F-RVFI-017: rvfi_ext_pre_mip / post_mip bit layout and sampling points
- What: pre_mip is mip when the instruction entered ID (or the captured value for a trap),
  post_mip is mip when the instruction left ID. Layout: bit 3 software, bit 7 timer, bit 11
  external, bits 30:16 fast[14:0]; other bits 0.
- Observable at: rvfi_ext_pre_mip, rvfi_ext_post_mip.
- Config: irq inputs (mip is combinational from them).
- Source: RTL-defined: rtl/ibex_core.sv:1809-1827,1993-1994,2136; rtl/ibex_pkg.sv:712-716;
  rtl/ibex_cs_registers.sv:408-412
- Edge: no
- Status: ACTIVE

### F-RVFI-018: rvfi_ext_debug_req and rvfi_ext_debug_mode
- What: debug_req is the raw debug_req_i sampled at the instruction's IF->ID transfer
  (instr_valid_id_d & instr_new_id_d, rtl/ibex_core.sv:1996-2001), or captured_debug_req when the
  request arrived on an empty ID (:1949-1957); debug_mode is the core's debug_mode flag when the
  instruction left ID. RTL-defined consequences (rtl-arch fact-check X-6): a high debug_req_i lets
  no new instruction enter ID outside debug mode (DECODE halts IF and enters DBG_TAKEN_IF once ID
  and WB are empty, rtl/ibex_controller.sv:700-708; halt_if is combinational from the request,
  :1020), so the instruction in ID when the pin rises reports debug_req = 0 and completes, an
  instruction whose transfer would follow the rise never enters (entry with dpc = its pc, no
  record), and the first debug-ROM record reports debug_req = 1 with debug_mode = 1; a record with
  debug_req = 1 and debug_mode = 0 never exists.
- Observable at: rvfi_ext_debug_req, rvfi_ext_debug_mode.
- Config: debug_req_i, dcsr.
- Source: RTL-defined: rtl/ibex_core.sv:1928,1949-1957,1996-2001,2101,2178;
  rtl/ibex_controller.sv:700-708,1020
- Edge: no
- Status: ACTIVE
- Notes: Fire-checks for "entry from FLUSH" key on the driver timestamp, the last record before
  entry and the DmHaltAddr fetch with no record in between (TB Infra convention C-3); dpc = pc of
  the first not-yet-executed instruction, derived from the last retired record (X-7).

### F-RVFI-019: rvfi_ext_mcycle and rvfi_ext_mhpmcounters[0..9]
- What: Sampled at rvfi_id_done from the live counters: mcycle (64-bit) and mhpmcounter[3..12]
  low/high halves mapped to indexes 0..9 (MHPMCounterNum = 10). The values are those visible
  when the instruction left ID, before its own retirement increments minstret-type events in WB.
- Observable at: rvfi_ext_mcycle, rvfi_ext_mhpmcounters, rvfi_ext_mhpmcountersh.
- Config: mcountinhibit, mhpmevent selects.
- Source: RTL-defined: rtl/ibex_core.sv:174-175,2102,2108-2127
- Edge: no
- Status: ACTIVE
- Notes: minstret is not exported on rvfi_ext (only via CSR reads).

### F-RVFI-020: rvfi_ext_ic_scr_key_valid
- What: The cpuctrlsts ic_scr_key_valid flop sampled at ID done, travelling with the record.
- Observable at: rvfi_ext_ic_scr_key_valid.
- Config: ic_scr_key_valid_i stimulus.
- Source: RTL-defined: rtl/ibex_core.sv:2103,2180
- Edge: no
- Status: ACTIVE

### F-RVFI-021: rvfi_ext_rf_wr_suppress
- What: Set on a load record whose RF write was suppressed because the beat that COMPLETES the
  load had a bus integrity error (rvfi_rf_wr_suppress_wb = instr_done_wb & ~rf_we_wb_o &
  outstanding_load_wb & lsu_load_resp_intg_err, rtl/ibex_core.sv:2384-2385, keyed on the
  data_intg_err of the current rvalid, rtl/ibex_load_store_unit.sv:697-698,756; see F-SEC-015);
  otherwise 0. Per-beat rule (rtl-arch fact-check X-11): a misaligned load whose FIRST beat is
  corrupted and whose second beat is clean is written to the RF with the merged data and its
  record shows rf_wr_suppress = 0 and rvfi_rd_addr = rd (the first-half status lsu_err_d has no
  integrity term, :514); the flag truthfully reports the un-suppressed write.
- Observable at: rvfi_ext_rf_wr_suppress with rvfi_valid; rvfi_rd_addr on the same record.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:2379-2398; rtl/ibex_load_store_unit.sv:514,697-698,756
- Edge: no
- Status: ACTIVE
- Notes: Bug candidate B16 (rtl-arch BUG-08, bug log v1d, owner question Q-015): the first-beat
  class is the expected-fail item TP-RVFI-040 (checker follows security.rst:88: suppress on any
  bad beat); the aligned and second-beat classes pass (TP-RVFI-024).

### F-RVFI-022: Zcmp expanded sequences produce one record per micro-op
- What: Each micro-op of cm.push/cm.pop/cm.popret/cm.popretz/cm.mvsa01/cm.mva01s completes ID
  separately, so each produces its own record with its own rvfi_order, rvfi_insn = the 32-bit
  micro-op, the same rvfi_pc_rdata, rvfi_ext_expanded_insn_valid = 1, rvfi_ext_expanded_insn =
  the original 16-bit encoding and rvfi_ext_expanded_insn_last = 1 on the final micro-op.
- Observable at: rvfi_ext_expanded_insn_valid/expanded_insn/expanded_insn_last, rvfi_order.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:2263-2282,2104-2106; rtl/ibex_pkg.sv:319-324
- Edge: no
- Status: ACTIVE
- Notes: Owner question: the ISA model retires one instruction; the comparison must fold the
  micro-op records (e.g. compare state at expanded_insn_last).

### F-RVFI-023: Zcmp micro-op that traps mid-sequence
- What: A fault on the n-th micro-op produces a trap record for that micro-op (expanded_insn_last
  may be 0); earlier micro-ops have already retired with their own records and RF/memory effects.
- Observable at: rvfi_trap with rvfi_ext_expanded_insn_valid = 1 and expanded_insn_last = 0.
- Config: PMP / data_err_i on one of the stack accesses.
- Source: RTL-defined: rtl/ibex_core.sv:1885-1890,2271-2282
- Edge: yes, of F-RVFI-022
- Status: ACTIVE

### F-RVFI-024: Dummy instructions produce no record (cross-reference)
- What: FOLDED into F-DIT-016: dummies produce no rvfi_valid and do not advance rvfi_order
  (rvfi_stage_valid_d[0] gated with ~dummy_instr_id, rtl/ibex_core.sv:1864-1865,1905); a pure
  cross-reference (Critic C-12 pattern c).
- Observable at: rvfi_valid, rvfi_order.
- Config: cpuctrlsts.dummy_instr_en.
- Source: RTL-defined: rtl/ibex_core.sv:1864-1865,1905
- Edge: yes, of F-DIT-016
- Status: FOLDED into F-DIT-016 (bin CG-DIT-004.cp_event.insert; CG-RVFI-001.cp_valid_gap.g2)

### F-RVFI-025: ebreak that enters debug mode is not reported as a trap
- What: rvfi_trap_id excludes ebrk_insn & ebreak_into_debug, so the ebreak record has
  rvfi_trap = 0; debug entry is visible on the following record's rvfi_ext_debug_mode = 1 and
  the PC jump to DmHaltAddr in rvfi_pc_rdata.
- Observable at: rvfi_trap = 0 on the ebreak, rvfi_ext_debug_mode.
- Config: dcsr.ebreakm / ebreaku, privilege mode.
- Source: RTL-defined: rtl/ibex_core.sv:1885-1886; rtl/ibex_controller.sv:481
- Edge: yes, of F-RVFI-005
- Status: ACTIVE

### F-RVFI-026: Record of an instruction with a fetch error (bus error, PMP exec fault)
- What: rvfi_trap = 1 with rvfi_insn = whatever data was captured for the failed fetch (not
  meaningful), rvfi_pc_rdata = the faulting PC, rvfi_rd_addr / rvfi_rd_wdata = 0. The memory
  fields are NOT zero: an ID-stage trap record keeps the garbage decode of the faulting word
  (rvfi_mem_rmask = mask(lsu_type) with the decoder default 2'b00 -> 4'b1111, zeroed only when
  data_we_o; rvfi_mem_addr = alu_adder_result_ex; rvfi_mem_wdata = the rs2 value; rvfi_mem_rdata =
  the previous load's data; rtl/ibex_core.sv:2085-2086,1024-1025,2207-2209,2222-2233;
  rtl/ibex_decoder.sv:285; rtl/ibex_load_store_unit.sv:723); masks are zeroed only for WB traps
  (:2156-2157) (rtl-arch fact-check X-15 / TP-RVFI-029; same mechanism as B18). mtval is the
  faulting fetch address (pc or pc + 2, rtl/ibex_controller.sv:859-861; D10).
- Observable at: rvfi_trap, rvfi_pc_rdata, rvfi_rd_addr = 0.
- Config: PMP config, instr_err_i.
- Source: RTL-defined: rtl/ibex_core.sv:1885-1886,2074-2077,2085-2086,2156-2157;
  rtl/ibex_controller.sv:268-270,859-861
- Edge: yes, of F-RVFI-005
- Status: ACTIVE
- Notes: Checkers must not compare rvfi_insn or the rvfi_mem_* fields for fetch-error records;
  only rd_addr / rd_wdata == 0 is checked (TP-RVFI-029).

### F-RVFI-027: rvfi_mode of a trapping instruction is the mode it executed in
- What: rvfi_id_done for a trapping instruction happens the cycle before FLUSH (rvfi_flush_next),
  and priv_lvl changes to M during FLUSH (csr_save_cause), so a U-mode ecall is recorded with
  rvfi_mode = 0.
- Observable at: rvfi_mode on rvfi_trap records.
- Config: privilege mode.
- Source: RTL-defined: rtl/ibex_core.sv:1851-1853,2078; rtl/ibex_cs_registers.sv:893-908
- Edge: yes, of F-RVFI-007
- Status: ACTIVE

### F-RVFI-028: WFI record and sleep
- What: WFI retires (one record) before the core enters WAIT_SLEEP/SLEEP; no records are emitted
  while asleep; the wake-up interrupt's handler first instruction carries rvfi_intr = 1 and a
  preceding rvfi_ext_irq_valid pulse.
- Observable at: rvfi_valid gap, rvfi_intr, core_busy_o.
- Config: mie/mstatus.MIE.
- Source: RTL-defined: rtl/ibex_controller.sv:598-621; rtl/ibex_core.sv:1965-1970,2400-2415
- Edge: yes, of F-RVFI-016
- Status: ACTIVE

### F-RVFI-029: Instructions killed in IF by an interrupt never appear
- What: Alias of F-IRQ-016: RVFI perspective (the controller takes an interrupt only with ID/WB
  empty, so the instruction in ID always completes and is recorded; only IF-stage words are
  discarded and re-fetched, so rvfi_order has no holes around interrupts), see canonical.
- Observable at: rvfi_order continuity; rvfi_pc_rdata of the post-handler instruction equals mepc
  (csrr read-back on rvfi_rd_wdata).
- Config: irq inputs.
- Source: RTL-defined: rtl/ibex_controller.sv:698-721,1078-1079 (PipeEmptyOnIrq)
- Edge: yes, of F-RVFI-016
- Status: ALIAS of F-IRQ-016

### F-RVFI-030: CHERIoT capability fields are constant NULL_CAP / 0 with CHERIoT off
- What: rvfi_rs1_rcap/rs2_rcap come from the RF rcap ports, which are forced to CapWordZeroVal
  when cheriot_enable_i != On; rvfi_rd_wcap comes from rf_wcap_wb which wb_stage forces to
  NULL_CAP for non-CHERIoT instructions; rvfi_mem_is_cap/rcap/wcap come from lsu_is_cap/lsu_wcap
  (0/NULL_CAP from g_cheriot_ex when instr_is_cheriot is 0) and the LSU cap path.
- Observable at: rvfi_rs1_rcap, rvfi_rs2_rcap, rvfi_rd_wcap, rvfi_mem_is_cap, rvfi_mem_rcap,
  rvfi_mem_wcap all zero on every record.
- Config: none (cheriot_enable_i tie).
- Source: RTL-defined: rtl/ibex_core.sv:2286-2295,2339-2350,2206-2233;
  rtl/ibex_register_file_ff.sv:227-230; rtl/ibex_wb_stage.sv:215-218; rtl/ibex_cheriot_ex.sv:955-960
- Edge: no
- Status: ACTIVE
- Notes: Cheap invariant checker for the CHERIoT exclusion.

### F-RVFI-031: rvfi_ext_nmi vs rvfi_ext_nmi_int
- What: rvfi_ext_nmi reflects the external irq_nm_i; rvfi_ext_nmi_int reflects the controller's
  internal NMI (bus integrity error interrupt, irq_nm_int). Both captured at IF->ID or at the
  trap decision.
- Observable at: rvfi_ext_nmi, rvfi_ext_nmi_int.
- Config: irq_nm_i; bus integrity error injection.
- Source: RTL-defined: rtl/ibex_core.sv:1929-1930,1995-1999; rtl/ibex_controller.sv:434-438
- Edge: no
- Status: ACTIVE

### F-RVFI-032: rvfi_ext_irq_valid never coincides with rvfi_valid
- What: The ext fields advance on (rvfi_id_done | irq_valid) at stage 0 and (rvfi_wb_done |
  irq_valid) at stage 1, so structurally a notification and a record could share a stage; on this
  RTL they never share a cycle at the port (rtl-arch fact-check X-16 / TP-RVFI-035): the
  interrupt decision needs ~instr_valid_id & ready_wb, so the last pre-interrupt record is out by
  decision + 1 while the marker passes four flops and rises at decision + 4, and the handler's
  first record comes one cycle after the marker falls; no instruction retires in between
  (rtl/ibex_core.sv:1965-1971,1985-2004,2192-2198). The record fields and the notification's
  pre_mip/nmi/debug_req fields are therefore never overwritten by each other.
- Observable at: rvfi_valid & rvfi_ext_irq_valid never both high (negative property, T-044
  sva_rvfi_irq_valid_exclusive).
- Config: irq inputs.
- Source: RTL-defined: rtl/ibex_core.sv:1965-1971,1985-2004,2130-2141,2188-2199
- Edge: yes, of F-RVFI-016
- Status: ACTIVE
- Notes: Candidate owner question 10 (pre_mip on a colliding cycle) is RESOLVED by X-16: no
  collision exists; the checker keeps the exclusivity assertion (TP-RVFI-035) and TP-RVFI-019
  counts marker rising edges.

### F-RVFI-033: RVFI reset values
- What: FOLDED into F-RST-009: on reset all rvfi_* are 0/NULL_CAP except rvfi_mode = PRIV_LVL_M
  and rvfi_ixl = 1, and rvfi_valid = 0 until the first instruction retires
  (rtl/ibex_core.sv:2007-2067); the parent lists these values (Critic C-12 pattern c).
- Observable at: rvfi_* during reset.
- Config: none.
- Source: RTL-defined: rtl/ibex_core.sv:2007-2067
- Edge: yes, of F-RST-009
- Status: FOLDED into F-RST-009 (bin CG-RST-001.cp_reset_kind.power_on; CG-RST-001.cp_reset_kind.mid_run)

### F-RVFI-034: Register-file write arbitration in WB is one-hot; exactly one rd write per retired instruction
- What: The WB stage merges two write sources into the single RF write port: the WB flop
  (rf_wdata_wb_mux_we[0] = rf_we_wb_q & wb_valid_q, rtl/ibex_wb_stage.sv:183) and the LSU load
  return (rf_wdata_wb_mux_we[1] = rf_we_lsu_i, :220); the RTL assertion RFWriteFromOneSourceOnly
  requires $onehot0 of the two enables (:310) and rf_wcap_wb_o follows the same select
  (:305-306). The WB-flop write happens the cycle after ID for non-load instructions, the load
  write at data return directly from the LSU, stores never write (EX-09; path P10). RVFI captures
  rd_addr/rd_wdata from whichever source fires (F-RVFI-009), so every retired instruction shows at
  most one rd write whose source is consistent with its class.
- Observable at: rvfi_rd_addr != 0 exactly on the records whose instruction class writes a
  register (never on stores, branches, trap records or rd = x0); rvfi_rd_wdata = rvfi_mem_rdata on
  load records and the ALU/CSR/mul-div result otherwise (gen_isa_compare); one rd write per
  rvfi_order value.
- Config: none.
- Source: RTL-defined: rtl/ibex_wb_stage.sv:183,220,305-306,310; rtl/ibex_core.sv:2339-2377;
  rtl-arch's behaviour summaries EX-09; gen_hierarchy_map.md P10
- Edge: no
- Status: ACTIVE
- Notes: NEW for Critic C-09 item 7 (P10). The one-hot property itself is an RTL assertion
  (INC_ASSERT) plus a gen_chk_rvfi_proto rule; the boundary consequence of a violation would be
  a wrong rvfi_rd_wdata source or a stray write visible on the next read (gen_isa_compare).
  rf_we_wb_o / rf_waddr_wb_o are wrapper-internal seam nets (probe candidate P1 class).

---------------------------------------------------------------------------------------------------
## CHERI: CHERIoT carve-out inventory
---------------------------------------------------------------------------------------------------

### F-CHERI-001: CHERIoT mode excluded by owner ruling (exclusion name: cheriot-out-of-scope)
- What: The opentitan build sets BaseIsa = BaseIsaRV32IorCHERIoT, so the RTL contains the full
  CHERIoT datapath (ibex_cheriot_ex, capability-tagged register file bank, capability CSRs/SCRs,
  capability load/store FSM, CHERIoT decode of OPCODE_CHERI 0x5b and OPCODE_AUICGP 0x7b, CHERI
  fault cause 28). All of it is runtime-gated on cheriot_enable_i == IbexMuBiOn (4'b0101). The
  DUT wrapper ties cheriot_enable_i to IbexMuBiOff (4'b1010), so CHERIoT behaviour is out of
  scope. What remains in scope is the "off" behaviour of every gate: CHERIoT opcodes and SCR CSRs
  must trap as illegal instructions, capability outputs must be constant zero, the invalid-MuBi
  alert must stay low, and the RV32 paths that are routed THROUGH CHERIoT modules (the LSU
  request path passes through ibex_cheriot_ex; the register file uses the banked layout) must
  behave exactly like plain Ibex.
- Observable at: rvfi_trap + csrr read-back of mcause (= 2) for 0x5b/0x7b opcodes and for CSR
  accesses to 0xBC1/0xBC2/0xBC4; data_tag_o == 0 always; rvfi_*cap and rvfi_mem_is_cap == 0
  always; alert_major_internal_o unaffected; rvfi_rd_wdata of csrr marchid = 22 and of csrr misa
  (I = 1, E = 0).
- Config: none (cheriot_enable_i tie).
- Source: RTL-defined: rtl/ibex_core.sv:67,1339-1347; rtl/ibex_pkg.sv:36-39,84-85,378-379,
  626-628,728,759-760; dv/auto_dv/excl/gen_exclusions.el as committed at 9ebf2d9 (pass 13; the
  exclusion deliverable, rtl-arch T-069; entry set identical to 4125c36; Critic approval of the file
  pending, it changes no row) with dv/auto_dv/excl/gen_exclusions_README.md (section 2 content
  table, section 4 refuted entries, section 5 notes, 5a soundness, 5b in-range objects kept live,
  6 Critic conditions, 7 EC-3 fill procedure) and dv/auto_dv/excl/gen_exclusions_select_report.md
  of the same run; dv/auto_dv/evidence/gen_exclusions_draft_v2.md (the source the file is generated
  from); dv/auto_dv/evidence/gen_cheriot_carveout.md buckets A-F and gating chain G1-G8; table below
- Edge: no
- Status: ACTIVE
- Exclusion authority: dv/auto_dv/excl/gen_exclusions.el at 9ebf2d9 (md5 9b642ef57393d8b3af8de9485a8f6f88), the file urg loads, with its README dv/auto_dv/excl/gen_exclusions_README.md; the rtl-arch draft is the file's source, never the authority.
- Exclusion verdict: Critic APPROVE in draft form (dv/auto_dv/docs/gen_critic_exclusions_v3.md line 15); final-file conditions F-1 and F-3 stay open until the first measured regression, whose delta rtl-arch sends.
- Notes: Ports that exist only for CHERIoT and what gen_dut_top must do with them:
  - cheriot_enable_i (rtl/ibex_core.sv:67; also on ibex_register_file_ff:69): tie both to
    IbexMuBiOff = 4'b1010. Any other value than On/Off raises alert_major_internal_o while
    fetch is enabled (F-SEC-013).
  - data_tag_i (rtl/ibex_core.sv:87): tie 0. data_tag_o (85): leave observable; expect constant 0
    (rtl/ibex_load_store_unit.sv:211-222,740 - tag only produced for capability stores).
  - rf_wcap_ecc_wb_o / rf_rcap_a_ecc_i / rf_rcap_b_ecc_i (rtl/ibex_core.sv:100-102) connect to
    the RF wcap_a_i / rcap_a_o / rcap_b_o (rtl/ibex_register_file_ff.sv:74,79,84) inside the
    wrapper. RegFileECC=0 per the Q-002 default, so no capability ECC decoder is elaborated and
    RegFileCapEccWidth is unused; the RF returns CapWordZeroVal when CHERIoT is off. Parameter
    hazard if RegFileECC=1 were ever chosen: rtl/ibex_top.sv passes RegFileCapEccWidth =
    REGCAP_W (:400) while declaring REGCAP_W + 7 (:219); with RegFileECC=1 the wrapper must pass
    REGCAP_W + 7 = 42 (and RF CapWidth = 42), otherwise the part-select
    rf_rcap_*_ecc_i[RegFileCapEccWidth-1:REGCAP_W] at rtl/ibex_core.sv:1264/:1271 is the reversed
    range [34:35] (carve-out F4; Critic C-17 correction of the v1 "REGCAP_W (35) as ibex_top
    does" note).
  - rvfi_rs1_rcap, rvfi_rs2_rcap, rvfi_rd_wcap, rvfi_mem_is_cap, rvfi_mem_rcap, rvfi_mem_wcap
    (rtl/ibex_core.sv:149,151,155,158,163,165): observe, expect 0/NULL_CAP (F-RVFI-030).
  - ibex_trvk (capability revocation, rtl/ibex_trvk.sv:9-67) is instantiated only in ibex_top
    (rtl/ibex_top.sv:257-272,425-435) - not in the DUT. No trvk reference exists in ibex_core.

Carve-out construct table. Authority statement (fix brief 3; round-3 review F-CHERI-001): this
table mirrors dv/auto_dv/excl/gen_exclusions.el as committed at 9ebf2d9 (pass 13; rtl-arch confirms
the entry set is final through pass 13 and identical to 4125c36, the pass-13 regeneration changed
annotations only) row for row, read together with dv/auto_dv/excl/gen_exclusions_README.md (section
2 content table, section 4 refuted entries, section 5 notes, 5a soundness, 5b in-range objects kept
live, 6 Critic conditions, 7 EC-3 fill procedure) and
dv/auto_dv/excl/gen_exclusions_select_report.md of the same run. Critic approval of the file is
pending; it changes no row. The file, never this table, is what urg loads (-excl_strict); where a
row and the file disagree the file wins and the row is corrected. How the file selects (README
section 1): A.1 = a guard analysis of rtl/ibex_cheriot_ex.sv (a line is dead when an enclosing if /
case arm requires a constant-0 term or follows a constant-1 one; constants from yosys propagation
under the tie plus the decoder defaults), giving Blocks, Branch vectors and Condition objects on
the 265 dead lines; A.3 = Blocks and true-arm Branch vectors in the shared modules, selected only
inside an approved draft range AND under a dead guard or an explicit never-held-state / enum cone;
A.4 = Condition vectors in which a constant-tie operand takes its impossible value; A.5 = constant
CHERIoT-only ports (struct fields as entries); A.6 = the two capability FSMs; A.7 = the three
vacuous register-file assertions; class P = the two build-parameter arms; class D 2a = the three
default arms with no spare encoding; class D 2b (the three spare-encoding default arms) is HELD OUT
until the first measured regression fills EC-3 (row 169); class R rows 37-40 are OUT until EC-4
passes (row 171); the A.8 carve-back table is the last filter (mstack_epc_cap_q and its read-back,
the cs_registers :473 / :482 else arms and the three register-file shared-net Condition vectors are
live, rows 128, 150, 151, 158, 160); the strict load of pass 13 is clean (README section 3,
rtl-arch-007). Objects the file keeps live although in a draft range are listed in README section
5b and read "live, not excluded" below. Carve-out = dv/auto_dv/evidence/gen_cheriot_carveout.md
(promoted copy of the rtl-arch working file), referenced as buckets A-F, gating chain G1-G8 and the
F-leak items. Column "Reachable when Off": yes = the construct affects behaviour with
cheriot_enable_i == IbexMuBiOff and is covered as plain-Ibex behaviour, as a negative check or as a
constant-value monitor; "yes (live RV32I, never excluded)" = a bucket-F leak or the live half of a
gated statement, which no exclusion may touch; no = dead with the tie (excluded, or held out with
the reason). Column "Exclusion" names the gen_exclusions.el entry class exactly: Block (line
metric), Branch vector, Condition vector, Toggle, Fsm/State/Transition, Assert, or none (with the
reason: folded by VCS, no dead guard, carve-back, held out, live, or not in the file). Rules
(Critic C-16..C-19): this table records the DV consequence per row (negative check / constant-value
monitor / live coverage); constant CHERIoT-only ports carry a toggle exclusion (A.5). No "no" row
contains live RV32I logic; every "no" row cites exactly the dead sub-arm or term with its entry
class; every bucket-F item (F1-F17) appears as live; the file holds no block-label exclusion where
the block holds live or toggling RV32I logic (B1, B4, B5, B12, B14, B15): A.3 Blocks are per-object
entries (id, checksum, text). Row count: 176 data rows (rows 1-165 from the v2 draft alignment;
rows 166-176 for the README content-table classes P, D, R, the objects the predicate keeps live and
the notes; gen_reading_report.md Section 7 item 3 said 60 and must be corrected to 176). Row
numbers are stable: retired statements are rewritten in place, never renumbered; the rows
re-aligned to 9ebf2d9 in this revision are listed in the closing note.

| # | File:lines | Construct | Reachable when Off | Exclusion (gen_exclusions.el entry class) | DV consequence |
|---|---|---|---|---|---|
| 1 | rtl/ibex_core.sv:17 | imports ibex_cheriot_pkg (types only) | n/a | none (A.2: the package has no coverage objects) | none |
| 2 | rtl/ibex_core.sv:49,67,85,87,100-102 | CHERIoT-only ports: RegFileCapEccWidth, cheriot_enable_i, data_tag_o, data_tag_i, rf_wcap_ecc_wb_o, rf_rcap_a/b_ecc_i | yes (constant 0 / tie) | Toggle A.5 (ibex_core list) | tie cheriot_enable_i = IbexMuBiOff and data_tag_i = 0 in gen_dut_top; constant-value monitor data_tag_o == 0 (TP-CHERI-003) |
| 3 | rtl/ibex_core.sv:149,151,155,158,163,165 | rvfi_rs1_rcap, rvfi_rs2_rcap, rvfi_rd_wcap, rvfi_mem_is_cap, rvfi_mem_rcap, rvfi_mem_wcap (RVFI builds) | yes (constant NULL_CAP / 0) | Toggle A.5 (RVFI-only entries, B.7 rule 4) | constant-value monitor (F-RVFI-030, TP-RVFI-033) |
| 4 | rtl/ibex_core.sv:214-215,234,250,262,432-489 | CHERIoT internal control / capability nets (bucket D: instr_fetch_cheriot_*_vio, cheriot_enable_mubi_err, lsu_err_is_cheriot, branch_target_ex_cheriot, cheriot_* selects and operands, csr_mshwm / csr_mshwmb / csr_mshwm_set) | yes (constant) | none: internal nets are not toggle objects under -cm_tgl portsonly (A.5 note E-01) | none |
| 5 | rtl/ibex_core.sv:490 | csr_mshwm_new = {lsu_addr_o[31:4], 4'h0} (from rtl/ibex_cheriot_ex.sv:994) | yes (toggles with every data address; dead: mshwm_en_combi = 0) | none: bucket D / F13 toggling-but-dead net, not excludable (EC-5) | none (never claimed as CHERIoT activity) |
| 6 | rtl/ibex_core.sv:263,435 | branch_target_ex (= branch_target_ex_rv32), instr_is_rv32lsu_id (= lsu_req_dec) | yes (live RV32I, never excluded) | none (A.8 v1 items; bucket F13) | live coverage through every jump/branch and load/store |
| 7 | rtl/ibex_core.sv:911-999 | g_cheriot_ex: instance u_ibex_cheriot_ex | see the rtl/ibex_cheriot_ex.sv rows | A.1 object-list procedure inside the instance (no whole-instance entry) | see the rtl/ibex_cheriot_ex.sv rows |
| 8 | rtl/ibex_core.sv:1000-1001 | branch_target_ex ternary on instr_valid_id & instr_is_cheriot_id | yes (live RV32I arm branch_target_ex_rv32; bucket B1) | Branch A.3: CHERIoT arm only (select constant 0; 1 vector, MODULE ibex_core Branch 3) plus Condition A.4 vectors of the :1000 select with instr_is_cheriot_id at its impossible value 1 | live coverage of the RV32 arm (every jump/branch) |
| 9 | rtl/ibex_core.sv:1002-1056 | gen_no_cheriot_ex tie-offs | NOT-ELAB (other generate arm) | none (no objects) | none |
| 10 | rtl/ibex_core.sv:1244-1290 | gen_cheriot_cap_ecc encoder / decoders and the `(On) & OR-reduce(rf_cap_ecc_err_x)` terms of :1281-1286 | NOT-ELAB with RegFileECC=0 (Q-002 default; inside `if (RegFileECC)` :1218) | none while RegFileECC=0; with RegFileECC=1: bucket B2 entries plus Condition A.4 for :1281-1286 (Part D open item) | none; if RegFileECC=1 were chosen, RegFileCapEccWidth must be REGCAP_W+7 = 42 (see note) |
| 11 | rtl/ibex_core.sv:1342-1344 | gen_cheriot_enable_check: cheriot_enable_mubi_err = instr_exec & !(On or Off) | yes (constant 0 with the valid Off tie; live only if the tie were invalid) | Condition A.4 (the :1343 vectors with the tie compare at its impossible value; the top-level negation is encoded by the inner value, README section 1 rule 4; glitch-covered, -cm_glitch 0 build only, row 176); the net is internal (no toggle object) | negative check: alert_major_internal_o never fires from this source (F-SEC-013, TP-SEC-017) |
| 12 | rtl/ibex_core.sv:1350-1351 | alert_major_internal_o = rf_ecc_err_comb OR pc_mismatch_alert OR csr_shadow_err OR cheriot_fatal_err OR cheriot_enable_mubi_err | yes (live RV32I, never excluded: the first three terms) | Condition A.4 for the two constant OR terms cheriot_fatal_err / cheriot_enable_mubi_err only (A.8 item 5); no line exclusion | live coverage of the alert (F-SEC-002, TP-SEC-003/004) |
| 13 | rtl/ibex_core.sv:1590-1593 | g_pmp_addr_gate ternaries pmp_req_addr[PMP_I / PMP_I2 / PMP_D] | yes (live RV32I: the Off arm is the PMP address path; bucket B4 / F14) | Branch A.3: `(On)` true-arms ('0) only (3 of the 6 vectors of the ibex_core g_pmp group) plus Condition A.4 vectors of the :1590 / :1591 / :1592 selects | live PMP coverage (PMP area) |
| 14 | rtl/ibex_core.sv:1627-1630 | g_pmp_cheriot_gate ternaries pmp_req_err[x] | yes (live RV32I: pass-through of pmp_req_err_raw; bucket B5 / F14) | Branch A.3: true-arms (1'b0) only (3 of the 6 vectors of the ibex_core g_pmp group) plus Condition A.4 vectors of the :1627 / :1628 / :1630 selects | live PMP coverage |
| 15 | rtl/ibex_core.sv:1851-1853 | rvfi_id_done = instr_id_done OR (rvfi_flush_next & id_exception_o & ~wb_exception_o) (RVFI builds) | yes (live RV32I, never excluded; bucket F10) | none (A.8 item 7) | B14 RVFI convention note (F-RVFI-015; TP-RVFI-018 pass, TP-RVFI-039 informational confirmation) |
| 16 | rtl/ibex_core.sv:2211-2212,2216-2217 | rvfi_mem_wcap_d = lsu_wcap, rvfi_mem_is_cap_d = lsu_is_cap (RVFI) | yes (lines live; values constant NULL_CAP / 0) | none on the lines (Toggle A.5 covers the ports) | constant-value monitor rvfi_mem_wcap / rvfi_mem_is_cap |
| 17 | rtl/ibex_core.sv:2223-2225 | `if (load_store_unit_i.resp_is_cap_q & lsu_resp_valid)` arm of the read-data capture (RVFI) | no (resp_is_cap_q constant 0, G4) | Block A.3 (RVFI only; 1 Block `rvfi_mem_rdata_d = rf_wdata_lsu;`, MODULE ibex_core Block 60) plus Condition A.4 of the :2223 guard (resp_is_cap_q at 1); the else-if :2226-2228 is live | none (the live arm carries rvfi_mem_rdata, F-RVFI-012) |
| 18 | rtl/ibex_core.sv:2286-2295 | g_rvfi_cap: rvfi_rs1/rs2_cap_d ternaries on rf_ren_a/b (RVFI) | yes (both arms NULL_CAP; the select toggles; bucket B6) | none (lines live) | constant-value monitor rvfi_rs1_rcap / rvfi_rs2_rcap |
| 19 | rtl/ibex_core.sv:2346-2349,2356,2361 | rvfi_rd_cap_d = rf_wcap_wb / NULL_CAP / rvfi_rd_cap_q (RVFI) | yes (lines live with rvfi_rd_wdata_d; values constant NULL_CAP) | none | constant-value monitor rvfi_rd_wcap |
| 20 | rtl/ibex_core.sv:1676-1690,1707-1733,2027-2030,2090-2099,2162-2176 | RVFI capability tracking flops and stage arrays | yes (lines execute; values constant) | none (internal nets; RVFI-only) | constant-value monitor at the six rvfi_*cap ports |
| 21 | rtl/ibex_if_stage.sv:40,90-91,133,194-197 | cheriot_enable_i, instr_fetch_cheriot_acc/bound_vio_o, pcc_cap_i; cheriot_acc_vio / bound_vio / force_uc nets | yes (constant 0 / tie) | Toggle A.5 (cheriot_enable_i, instr_fetch_cheriot_acc_vio_o, instr_fetch_cheriot_bound_vio_o, pcc_cap_i) | none |
| 22 | rtl/ibex_if_stage.sv:207-210 | gen_no_cheriot_if | NOT-ELAB | none | none |
| 23 | rtl/ibex_if_stage.sv:222-228 | exc_pc mux: EXC_PC_EXC / EXC_PC_IRQ ternaries | yes (live RV32I arms: {mtvec[31:8], 8'h00} and the vectored layout) | none: the constant-select assign-ternary has NO branch object in the dump (VCS folded it, README section 5 item 1; select report "BRANCH ibex_if_stage [(222, 228)]: 0 vectors"); only the A.4 Condition vectors of :222 / :225 with the tie term at its impossible value are in the file | live coverage of trap / interrupt vectors (instr_addr_o = vector; EXC / IRQ areas) |
| 24 | rtl/ibex_if_stage.sv:368 | .cheriot_force_uc_i(cheriot_force_uc) into the prefetch buffer | yes (constant 0) | none in gen_exclusions.el (re-checked at 9ebf2d9: 41 scopes, 13 modules, no MODULE ibex_prefetch_buffer / ibex_fetch_fifo scope; the connection is not an if_stage port): the prefetch-buffer / fetch-fifo cheriot_force_uc_i ports are not A.5 entries and stay in coverage; candidate explicit entries at the first measured regression (README section 5 item 2 rule; open request (3) to rtl-arch, closing note) | none |
| 25 | rtl/ibex_if_stage.sv:430 | if_instr_err = bus_err OR pmp_err OR cheriot_acc_vio OR cheriot_bound_vio | yes (live line; two constant OR terms) | Condition A.4 (vectors with a cheriot term = 1) | live coverage of fetch faults (F-RVFI-026) |
| 26 | rtl/ibex_if_stage.sv:445-446,452-453 | allow_all, hdrm_ok, base_ok (constant 1 with pcc_cap_i = ROOT_DECODED_CAP_TX) | yes (constant 1) | none explicit (internal nets; EC-2 constant analysis where propagated) | none |
| 27 | rtl/ibex_if_stage.sv:447-449 | instr_hdrm, hdrm_ge4, hdrm_ge2 | yes (toggle with if_instr_addr; dead: consumers gated) | none: bucket F13 toggling nets, listed by name as live, never swept in under the block label | none |
| 28 | rtl/ibex_if_stage.sv:456-457,464-465,469-472 | cheriot_bound_vio, cheriot_force_uc, cheriot_acc_vio assigns (G7) | yes (constant 0) | Condition A.4 (the `(On)` factor is never 1) | none |
| 29 | rtl/ibex_if_stage.sv:634-652 | gen_cheriot_vio_regs (g_cheriot_vio_ra with ResetAll=1): flops loaded on if_id_pipe_reg_we | yes (lines execute on every IF->ID transfer; data constant 0; bucket B7) | none on the lines; Toggle A.5 on the two output ports | none |
| 30 | rtl/ibex_if_stage.sv:495 | .cheriot_enable_i to the compressed decoder | tie | Toggle A.5 (ibex_compressed_decoder cheriot_enable_i) | none |
| 31 | rtl/ibex_prefetch_buffer.sv:30,104; rtl/ibex_fetch_fifo.sv:32-33,127 | cheriot_force_uc_i port and pass-through; `cheriot_force_uc_i OR ...` term of unaligned_is_compressed (:127) | yes (constant 0 -> standard unaligned-compressed decode) | none in gen_exclusions.el (re-checked at 9ebf2d9: neither module has a scope in the file; the :127 vector and the constant ports are not selected): kept in coverage; candidate explicit entries at the first measured regression (README section 5 item 2 rule; open request (3) to rtl-arch, closing note); :120 is inside `ifdef DII_SIM (U4) | live coverage of the RV32 unaligned-compressed path (FE area) |
| 32 | rtl/ibex_id_stage.sv:35,68-69,146,203-226,300,335,340 | CHERIoT ports and constant nets (bucket D) | yes (constant) | Toggle A.5 (id_stage list; NOT instr_is_rv32lsu_id_o, which toggles) | none |
| 33 | rtl/ibex_id_stage.sv:488,548-573,623-668,719-726 | port wiring of constant CHERIoT nets to decoder / controller | yes (wiring) | none (no coverage objects) | none |
| 34 | rtl/ibex_id_stage.sv:576 | instr_is_rv32lsu_id_o = lsu_req_dec | yes (live RV32I, never excluded) | none (A.8 v1 item) | live coverage through every load/store |
| 35 | rtl/ibex_id_stage.sv:578 | ex_valid_all = instr_is_cheriot_id_o ? cheriot_ex_valid_i : ex_valid_i | yes (live RV32I arm) | Branch A.3: CHERIoT arm only (the single id_stage Branch vector, `instr_is_cheriot_id_o` true arm, Branch 5) plus Condition A.4 of the :578 select | live coverage (every instruction completion) |
| 36 | rtl/ibex_id_stage.sv:580,582 | cheriot_load_o / cheriot_store_o = cheriot_operator_o fields | yes (constant 0) | Toggle A.5 (ports) | none |
| 37 | rtl/ibex_id_stage.sv:746-749 | csr_op_en_o ternary: (dual & On) ? instr_first_cycle : instr_id_done_o | yes (live RV32I arm instr_id_done_o) | none as Branch in 9ebf2d9 (select report: 1 vector for the (578) and (746-749) ranges together, the :578 one); Condition A.4 vectors of the :747 select's tie term (two groups) are in the file; the parent ternary-as-operand vector is not selected (row 175) | live coverage of CSR writes (CSR area) |
| 38 | rtl/ibex_id_stage.sv:901-908 | `cheriot_lsu_req_dec:` case item body in FIRST_CYCLE | no (cheriot_lsu_req_dec constant 0, G1) | Block A.3 (2 Blocks `id_fsm_d = MULTI_CYCLE;`, Blocks 62 / 64; Part C row 29; T022_ID_CHERI0) plus Condition A.4 of the :902 guard | none |
| 39 | rtl/ibex_id_stage.sv:1012 | multicycle_done select (lsu_req_dec OR cheriot_lsu_req_dec) | yes (live line; one constant OR term) | Condition A.4 only (A.8 item 4) | live coverage |
| 40 | rtl/ibex_id_stage.sv:1033-1036 | instr_kill = instr_fetch_err_i OR wb_exception OR id_exception_nc OR ~controller_run | yes (live RV32I, never excluded; gates instr_executing for every instruction; bucket F11) | none (A.8 item 4) | live coverage (every kill: fetch error, WB exception, ID exception, controller not running) |
| 41 | rtl/ibex_id_stage.sv:1069-1075 | cheriot_exec_id_o = (On) & ... | yes (constant 0; the continuous assign is a live line) | Toggle A.5 (port); Condition A.4 (vectors with the tie term = 1) | none (EC-1 proof object T022_ID_CHERI0) |
| 42 | rtl/ibex_id_stage.sv:1093-1096 | stall_mem term (lsu_req_dec OR cheriot_lsu_req_dec) & ~lsu_req_done_i | yes (live line; one constant OR term) | Condition A.4 only (A.8 item 4) | live coverage of load/store stalls |
| 43 | rtl/ibex_id_stage.sv:1142-1160,1199-1200 | gen_no_stall_mem | NOT-ELAB (WritebackStage = 1) | none | none |
| 44 | rtl/ibex_id_stage.sv:1297-1300 | ASSERT_IF IbexCheriotLoadDisabled / IbexCheriotStoreDisabled / IbexInstrNotCheriot / IbexCheriotExecDisabled | yes (live RV32I checkers; antecedent true; bucket F15) | none (A.7: kept; EC-3 proof objects) | keep enabled in every build (INC_ASSERT); zero failures required |
| 45 | rtl/ibex_decoder.sv:27,92-119,148,282-303,1459-1476 | CHERIoT ports, default assigns, instr_is_legal_cheriot / cs2 / imm12 / imm20 / imm21 assigns (G1) | yes (constant; the defaults are live lines) | Toggle A.5 (ports); Condition A.4 (:1451, :1454, :1460, :1463, :1465, :1472, :1475 vectors) | none |
| 46 | rtl/ibex_decoder.sv:202 | raddr_a = cheriot_operator_o.CAUICGP ? 5'h3 : (rs3 / rs1 select) | yes (live RV32I arm incl. the rs3 select) | none as a Branch: the assign-ternary has NO branch object (VCS folded it; select report "BRANCH ibex_decoder [(202, 202)]: 0 vectors", README section 5 item 1); the A.4 Condition vectors of :202 with cheriot_operator_o.CAUICGP = 1 are in the file | live coverage (rs1 / rs3 reads; rs3 on port A only for ternary ops, F-RVFI-008) |
| 47 | rtl/ibex_decoder.sv:211-217 | gen_16_regs ternaries rf_raddr_a_o / rf_raddr_b_o / rf_waddr_o (CheriLimit16Regs) | yes (live RV32I pass-through arms; x16-x31 addressing traverses them; bucket F5) | Branch A.3: masked arms only (3 vectors, decoder Branch 7 / 8 / 9; A.8 item 8) plus Condition A.4 of the :212 / :214 / :216 selects | live coverage (F-RST-022) |
| 48 | rtl/ibex_decoder.sv:237-242 | gen_16reg_check_active: illegal_reg_16 = (RV32E OR On) AND (...) | yes (constant 0; the right-hand sub-terms toggle; bucket B9) | Condition A.4 (:238) | negative check: no illegal-register trap for x16-x31 (F-RST-022) |
| 49 | rtl/ibex_decoder.sv:314-323 | OPCODE_JAL CHERIoT arm (CJAL) | no | Block A.3 plus Condition A.4 of the :314 arm guard; the RV32 jump arm :324-334 is live | live coverage of jal (ISA area) |
| 50 | rtl/ibex_decoder.sv:339-352 | OPCODE_JALR CHERIoT arm (CJALR) | no | Block A.3 plus Condition A.4 of the :339 arm guard; the RV32 jump arm :353-363 is live; :351 `illegal_insn = 1'b1` inside the arm is kept live by the A.8 carve-back table (conservative: the statement text matches the illegal_insn carve-back; select report carve-back, README section 5b) | live coverage of jalr (ISA area) |
| 51 | rtl/ibex_decoder.sv:402-407 | OPCODE_STORE funct3 011 CHERIoT arm (CSC) | no | Block A.3 plus Condition A.4 of the :402 arm guard; the else arm :408-410 (illegal_insn = 1: sd encoding) is live | negative check: the sd encoding traps illegal (ISA area) |
| 52 | rtl/ibex_decoder.sv:447-453 | OPCODE_LOAD funct3 011 CHERIoT arm (CLC) | no | Block A.3 plus Condition A.4 of the :447 arm guard; the else arm :454-456 (illegal_insn = 1: ld encoding) is live | negative check: the ld encoding traps illegal (ISA area) |
| 53 | rtl/ibex_decoder.sv:474-482 | OPCODE_AUIPC CHERIoT arm (AUIPCC) | no | Block A.3 plus Condition A.4 of the :474 arm guard; the RV32 auipc arm :483-485 is live | live coverage of auipc (ISA area) |
| 54 | rtl/ibex_decoder.sv:778-781 | csr_cheriot_always_ok_o | yes (constant 0) | Condition A.4 (:778); no toggle entry in 9ebf2d9 (csr_cheriot_always_ok_o is not in the decoder A.5 list of 38 entries; constant 0, a hole for the first measured regression to rule on) | none |
| 55 | rtl/ibex_decoder.sv:791,877-878 | OPCODE_CHERI case item and its `else illegal_insn = 1` | yes (live RV32I: opcode 0x5b traps as illegal instruction) | none as Block (the case item :791 and its else arm :877-878 stay live, A.3 note); Condition A.4 vectors of the :792 `(dual) && (On)` guard are in the file | live coverage TP-CHERI-001 (rvfi_trap + csrr read-back of mcause = 2) |
| 56 | rtl/ibex_decoder.sv:793-876 | OPCODE_CHERI body (all cheriot_operator bits) | no | Block A.3 (the :793-876 body under the dead :792 guard); the :824, :856 and :873 `illegal_insn = 1'b1` default / else arms inside the body are kept live by the A.8 carve-back table (select report carve-back Blocks 148 / 164 / 169; README section 5b) | none |
| 57 | rtl/ibex_decoder.sv:881,892-893 | OPCODE_AUICGP case item and its else illegal arm | yes (live RV32I: opcode 0x7b traps as illegal instruction) | none as Block (the case item :881 and its else arm :892-893 stay live); Condition A.4 vectors of the :882 guard are in the file | live coverage TP-CHERI-001 |
| 58 | rtl/ibex_decoder.sv:883-891 | OPCODE_AUICGP body | no | Block A.3 | none |
| 59 | rtl/ibex_decoder.sv:1478-1481 | gen_no_cheriot_decoder | NOT-ELAB | none | none |
| 60 | rtl/ibex_compressed_decoder.sv:20,27 | parameter / cheriot_enable_i port | tie | Toggle A.5 | none |
| 61 | rtl/ibex_compressed_decoder.sv:230-233,249-252,329-332,359-363,391-394,411-414,557-560,575-579,615-620,854-857 | the ten `(dual) && (On)` arms (c.incaddr4cspn, c.clc, c.csc, c.addi hint, c.incaddr16csp, c.srli/c.srai hint, c.slli hint, c.clcsp, Zcmp-illegal-in-CHERIoT, c.cscsp) | no | Block A.3 (11 Blocks in the ten arms: the :575-579 c.clcsp arm holds two statements, instr_o and its rd == 0 illegal_instr_o; Part C row 36 for :615-620) plus Condition A.4 (10 vectors: the `(dual) && (On)` guards at :230, :249, :329, :359, :391, :411, :557, :575, :615, :854) | none |
| 62 | rtl/ibex_compressed_decoder.sv:234-236,253-255,333-335,364-366,395-398,415-417,561-562,580-582,621 ff.,858-860 | the standard-RVC / Zc else-arms of the same case items | yes (live RV32I: every c.* decode and the RV32 illegal c.ld / c.sd / c.ldsp / c.sdsp arms) | none (never excluded) | live coverage (CMP area) |
| 63 | rtl/ibex_compressed_decoder.sv:911-914 | gen_no_cheriot_cdec | NOT-ELAB | none | none |
| 64 | rtl/ibex_load_store_unit.sv:25,44-52,76,101,116-128 | CHERIoT ports (cheriot_enable_i, lsu_is_cap_i, lsu_cheriot_err_i, lsu_wcap_i, lsu_lc_clrperm_i, lsu_rcap_o, data_tag_o, data_tag_i, lsu_err_is_cheriot_o) and constant nets (data_wdata_tag, resp_is_cap_q, cheriot_err_d/q, cap_rx_fsm_q/d, cap_lsw_*) | yes (constant) | Toggle A.5 (the nine ports) | constant-value monitor data_tag_o == 0 (TP-CHERI-003) |
| 65 | rtl/ibex_load_store_unit.sv:131-132 | data_offset ternary | yes (live RV32I arm data_addr[1:0]) | Branch A.3: CHERIoT arm (2'b00) only (LSU Branch 0) plus Condition A.4 of the :131 select | live coverage of byte offsets (DMEM area) |
| 66 | rtl/ibex_load_store_unit.sv:139-140 | data_be = 4'b1111 cap arm | no | Block A.3 (1 Block) plus Condition A.4 of the :139 guard; the else arm :141 ff. (lsu_type case) is live | live coverage of byte enables |
| 67 | rtl/ibex_load_store_unit.sv:211-219 | cap write-data arms incl. cheriot_cap_to_mem (:213) and the CTX_WAIT_GNT2 term (:212) | no | Block A.3 (2 Blocks) plus Condition A.4 of the :211 guard; the else arm :220 `{1'b0, wdata_int}` is live | constant-value monitor data_tag_o (:740 = data_wdata_tag) |
| 68 | rtl/ibex_load_store_unit.sv:407-408 | cpu_req_valid = lsu_req_i & ~((On) & lsu_cheriot_err_i); cpu_req_erred | yes (live line; constant term / constant 0) | Condition A.4 (:407-408) | live coverage (every request) |
| 69 | rtl/ibex_load_store_unit.sv:419,435 | cheriot_err_d default = cheriot_err_q & (On); IDLE clear | yes (constant 0; lines live) | Condition A.4 (:419) | none |
| 70 | rtl/ibex_load_store_unit.sv:437-448 | IDLE first arm (cpu_req_erred: CHERIoT access error without a bus request) | no | Block A.3 (:437-467 entry; Part C rows 14-22; T022_LSU_CHERI0) plus Condition A.4 of the :437 guard | none |
| 71 | rtl/ibex_load_store_unit.sv:449-467 | IDLE cap-access arm (lsu_go_goodcap; ls_fsm_ns = CTX_WAIT_GNT2 / CTX_WAIT_GNT1 at :464 / :466) | no | Block A.3 (same entry) plus Condition A.4 of the :449 guard; replaces the former overlapping rows :419-471 "yes" and :464-466 "no" | none (replaces the former overlapping rows :419-471 "yes" and :464-466 "no") |
| 72 | rtl/ibex_load_store_unit.sv:468-563 | IDLE normal arm (:468 ff.) and the WAIT_GNT_MIS / WAIT_RVALID_MIS / WAIT_GNT / WAIT_RVALID_MIS_GNTS_DONE states | yes (live RV32I LSU FSM) | none | live coverage (DMEM area: aligned, misaligned, PMP, bus error) |
| 73 | rtl/ibex_load_store_unit.sv:565-603 | CTX_WAIT_GNT1 / CTX_WAIT_GNT2 / CTX_WAIT_RESP case items | no (never entered: CTX_* assigned only at :464, :466, :570, :586) | Block A.3 under the explicit never-held-state cone (README section 1 rule 2 and 5b: the guard predicate alone would not select the :575 / :589 / :601 `ls_fsm_ns = IDLE` statements) plus Condition A.4 of the :566 / :580 / :594 guards plus FSM A.6 (ls_fsm_cs 3 states, 7 transitions; T022_LSU_NO_CTX) | none (IbexLsuStateValid :821-824 lists CTX_*: fine) |
| 74 | rtl/ibex_load_store_unit.sv:616-617,618-623 | cap_rx_fsm: CRX_IDLE true-arm (lsu_go_goodcap), CRX_WAIT_RESP1 / CRX_WAIT_RESP2 items | no (frozen in CRX_IDLE) | Block A.3 under the explicit cone (:619 / :623 `cap_rx_fsm_d = ...`) plus Condition A.4 of the :616 / :621 guards plus FSM A.6 (cap_rx_fsm_q 2 states, 5 transitions; T022_CRX_IDLE) | none |
| 75 | rtl/ibex_load_store_unit.sv:650-653 | LSU FSM flops: ls_fsm_cs, handle_misaligned_q, pmp_err_q, lsu_err_q | yes (live RV32I, never excluded; A.8 item 6) | none | live coverage |
| 76 | rtl/ibex_load_store_unit.sv:654,656 | cheriot_err_q <= cheriot_err_d; cap_rx_fsm_q <= cap_rx_fsm_d | yes (lines execute every clock; values constant) | none (internal nets, not toggle objects) | none |
| 77 | rtl/ibex_load_store_unit.sv:664-667 | resp_is_cap_q / resp_lc_clrperm_q update on lsu_go | yes (line live: executes on every lsu_go; value constant 0) | none (A.8 item 6) | none |
| 78 | rtl/ibex_load_store_unit.sv:669-678 | cap_lsw_data_q / cap_lsw_tag_q / cap_lsw_err_q update blocks under (On) | no | Block A.3 plus Condition A.4 of the :669 / :675 guards | none |
| 79 | rtl/ibex_load_store_unit.sv:688-693 | data_or_pmp_err and all_resp constant terms | yes (live lines) | Condition A.4 | live coverage of load/store error reporting |
| 80 | rtl/ibex_load_store_unit.sv:701-709 | gen_memcap_rd: lsu_rdata_o = ((On) & resp_is_cap_q) ? cap_lsw_data_q : data_rdata_ext; lsu_rcap_o ternary | yes (live RV32I: lsu_rdata_o = data_rdata_ext is THE load-data return; bucket B12 / F12) | Branch A.3: CHERIoT arms of :702-703 and :704-709 only (LSU Branch 4 / 5) plus Condition A.4 of the :702 / :704 selects; never a Block | live coverage of every load (F-RVFI-012) |
| 81 | rtl/ibex_load_store_unit.sv:710-715 | gen_no_cap_rd | NOT-ELAB | none | none |
| 82 | rtl/ibex_load_store_unit.sv:740 | data_tag_o = data_wdata_tag | yes (constant 0) | Toggle A.5 (port) | constant-value monitor (TP-CHERI-003) |
| 83 | rtl/ibex_load_store_unit.sv:760 | lsu_err_is_cheriot_o = (On) & cheriot_err_q | yes (constant 0) | Toggle A.5 (port); Condition A.4 | none |
| 84 | rtl/ibex_load_store_unit.sv:821-824,833-834 | IbexLsuStateValid (lists CTX_*); ASSERT_IF IbexLsuIsCapDisabled / IbexLsuCheriotErrDisabled | yes (live checkers; bucket F15) | none (A.7: kept; EC-3) | keep enabled; zero failures required |
| 85 | rtl/ibex_cheriot_ex.sv (instance u_ibex_cheriot_ex) | capability ALU / bounds / seal / permission ops (main_ex :290-555), the capability LSU request path (:562-661), check_cheriot (:753-863), err_cause_comb (:869-922), SCR access | no for the capability operations | A.1 guard analysis (README section 1 rule 3; 9ebf2d9): 265 dead RTL lines give 75 Blocks (dead-arm bodies at :296-521, :603-660, :754-856, :910-920), 66 Branch vectors (32 arms of the :293 `case (1'b1)` operator mux; :602, :610, :624, :647; :753, :763, :770, :785, :817; :908) and 246 Condition vectors (119 whole objects on dead lines, 127 impossible-value vectors) plus 144 Toggle entries, in 218 annotation groups each naming its dead guard and constant term (yosys constants under the tie plus the decoder defaults rtl/ibex_decoder.sv:297-303; T022_DEC_CHERI0 / T022_ID_CHERI0); no whole-instance entry (R-1); reachable-but-masked logic (check_rv32 :699-737, the all-false arms of check_cheriot, the :922 fall-through, always_comb defaults, the shared adder) is not excluded (README section 5b last row) | none |
| 86 | rtl/ibex_cheriot_ex.sv:943-948,951-954 | lsu_req_o / cpu_lsu_addr / cpu_lsu_we / cpu_lsu_wdata muxes on instr_is_cheriot_i and the lsu_we_o / lsu_addr_o / lsu_wdata_o assigns | yes (live RV32I arms: the whole RV32 request path passes through; bucket F12) | none as Branch in 9ebf2d9 (the guard analysis selects if / case arms; these assign-ternaries carry no Branch entry): Condition vectors of the :943 and :945-:948 selects with instr_is_cheriot_i at its impossible value 1 are in the file (A.1 groups); the lines and the RV32I arms stay in coverage | live coverage of every load/store (DMEM area, F-RVFI-011) |
| 87 | rtl/ibex_cheriot_ex.sv:958,960 | lsu_type_o = ~instr_is_cheriot_i ? rv32_lsu_type_i : 2'b00; lsu_sign_ext_o likewise | yes (live RV32I arms) | none as Branch; Condition vectors of the :958 / :960 selects (`~instr_is_cheriot_i` at its impossible value 0) are in the file | live coverage |
| 88 | rtl/ibex_cheriot_ex.sv:945,949,951,955,957,959 | cpu_lsu_cheriot_err / lsu_cheriot_err_o, cpu_lsu_is_cap / lsu_is_cap_o, lsu_lc_clrperm_o, lsu_wcap_o = instr_is_cheriot_i ? cheriot_lsu_wcap : NULL_CAP | yes (constant 0 / NULL_CAP; lsu_wcap_o is constant NULL_CAP, not a live mux) | Toggle A.1 (constant ports lsu_cheriot_err_o, lsu_is_cap_o, lsu_lc_clrperm_o fields, lsu_wcap_o fields); Condition vectors of the :949 / :957 / :959 selects; no Branch entry | constant-value monitor via rvfi_mem_wcap / rvfi_mem_is_cap (F-RVFI-030) |
| 89 | rtl/ibex_cheriot_ex.sv:970-971 | rv32_addr_incr_req_o = ((cheriot_enable_i != On) OR instr_is_rv32lsu_i) ? addr_incr_req_i : 1'b0 | yes (live: the true-arm is always selected) | none as Branch (the `: 1'b0` false arm has no entry in 9ebf2d9); Condition A.4 for the tie term at :970 (two groups: the whole select constant 1 and `cheriot_enable_i != On` constant 1; glitch-covered, row 176) | live coverage of misaligned accesses |
| 90 | rtl/ibex_cheriot_ex.sv:973 | rv32_addr_last_o = addr_last_i | yes (live) | none (LIVE list) | live (crash_dump_o.last_data_addr, F-SEC-027/028) |
| 91 | rtl/ibex_cheriot_ex.sv:991-993 | csr_mshwm_set_o = lsu_req_o & ~lsu_cheriot_err_o & lsu_we_o & (addr >= mshwmb) & (addr < mshwm) | yes (line live; result constant 0 through the mshwm / mshwmb CSR chain, bucket F17: mshwm_q = 0 so `addr[31:4] < 0` is never true) | Toggle A.1 (csr_mshwm_set_o constant 0; evidence 4.1 note) plus the :991 Condition vector (`~lsu_cheriot_err_o` constant 1); no Block | none (mshwm is readable only when On: unobservable; accepted) |
| 92 | rtl/ibex_cheriot_ex.sv:994 | csr_mshwm_new_o = {lsu_addr_o[31:4], 4'h0} | yes (toggles with every data address; dead consumer) | none: LIVE port list ("dead but toggling: not excludable under EC-5"); bucket D / F13 | none |
| 93 | rtl/ibex_cheriot_ex.sv:219-238 and the other Off-mode toggling nets of carve-out A1 (rf_rdata_a :232, rf_fullcap_a :237, cs1_addr_plusimm :590, pc_id_nxt :592, check_rv32 :701-738, err_cause_comb :884-918) | fwd_data_merger nets and the operand gating (instr_is_rv32lsu_i arm live); the rest toggle but are dead | yes (toggle; :219-233 is the live RV32I operand path, the rest is dead) | :219-233 lines never excluded (live RV32I operand path); Condition vectors with instr_is_cheriot_i at 1 on :231-:254 are in the file (A.1 groups); the toggling-but-dead internal nets are not toggle objects (-cm_tgl portsonly) and their lines are excluded only under a dead guard (guard analysis); check_rv32 :699-737, the all-false arms of check_cheriot :753-863, the err_cause_comb fall-through :922 and the always_comb defaults stay in coverage (README section 5b); a -excl_strict rejection of a covered object is a finding for rtl-arch (B.7 rule 1), never a reason to widen the exclusion | none |
| 94 | rtl/ibex_wb_stage.sv:18,31-33,49-51,56,60,64,82,99-103 | CHERIoT ports and flops (instr_is_cheriot_i, cheriot_load/store_i, cheriot_rf_we/wdata/wcap_i, rf_wcap_lsu_i, rf_wcap_fwd_wb_o, rf_wcap_wb_o; wb_is_cheriot_q and friends) | yes (constant) | Toggle A.5 (wb_stage port list) | constant-value monitor rvfi_rd_wcap |
| 95 | rtl/ibex_wb_stage.sv:115-116 | wb_done term ~(wb_is_cheriot_q && (wb_cheriot_load_q OR wb_cheriot_store_q)) | yes (live line; constant term) | Condition A.4 only (Part C row 41: never Block) | live coverage (every WB completion) |
| 96 | rtl/ibex_wb_stage.sv:137-142,152-157,171-176 | reset / load of the CHERIoT WB flops (g_wb_regs_ra with ResetAll=1) | yes (lines execute; values constant 0 / NULL_CAP) | none (internal nets) | none |
| 97 | rtl/ibex_wb_stage.sv:182-183 | rf_wdata_wb_mux[0] / rf_wdata_wb_mux_we[0] ternaries on wb_is_cheriot_q | yes (live RV32I arms rf_wdata_wb_q / rf_we_wb_q & wb_valid_q) | Branch A.3: wb_is_cheriot_q arms (the wb group holds 2 vectors, Branch 1 / 2, for the three ternaries :182, :183, :215; T022_WB_CHERI0) plus Condition A.4 of the :182 / :183 selects | live coverage (F-RVFI-034 one-hot arbitration, F-RVFI-009) |
| 98 | rtl/ibex_wb_stage.sv:190-196 | rf_write_wb_o / outstanding_load_wb_o / outstanding_store_wb_o constant OR terms | yes (live lines) | Condition A.4 only | live coverage (hazards, forwarding) |
| 99 | rtl/ibex_wb_stage.sv:215 | rf_wdata_fwd_wb_o ternary | yes (live RV32I arm rf_wdata_wb_q) | Branch A.3: shares the 2-vector wb group with row 97 (one of :182 / :183 / :215 has no vector in the dump) plus Condition A.4 of the :215 select | live coverage (F-RST-023 forwarding) |
| 100 | rtl/ibex_wb_stage.sv:216-218,305-306 | rf_wcap_fwd_wb_o, rf_wcap_wb, rf_wcap_wb_o | yes (constant NULL_CAP) | Toggle A.5 (rf_wcap_fwd_wb_o, rf_wcap_wb_o fields) plus Condition A.4 of the :216 / :217 selects | constant-value monitor rvfi_rd_wcap |
| 101 | rtl/ibex_wb_stage.sv:220,310 | rf_wdata_wb_mux_we[1] = rf_we_lsu_i; ASSERT RFWriteFromOneSourceOnly | yes (live RV32I) | none | live coverage; assertion kept enabled (F-RVFI-034) |
| 102 | rtl/ibex_wb_stage.sv:245-295 | g_bypass_wb | NOT-ELAB (WritebackStage = 1) | none | none |
| 103 | rtl/ibex_controller.sv:22,35,46-47,74,77,127-134,144-161,197-199 | CHERIoT ports and constant nets (bucket D; exc_cause_o never equals ExcCauseCheriFault = 28) | yes (constant) | Toggle A.5 (controller port list) | negative check: mcause is never 28 (rvfi_trap + csrr read-back of mcause) |
| 104 | rtl/ibex_controller.sv:234,236-240,256-257,259 | cheriot_ex_err, g_cheriot_asr_err (mret_cheriot_asr_err, csr_cheriot_asr_err; bucket B10), cheriot_ex_err_d, cheriot_asr_err_d | yes (constant 0; continuous assigns are live lines) | Condition A.4 (tie terms); these are the only bucket-C items inside :234-259 (A.8 item 3) | none |
| 105 | rtl/ibex_controller.sv:255 | illegal_insn_d = illegal_insn_i & (ctrl_fsm_cs != FLUSH) | yes (live RV32I, never excluded; A.8 item 3) | none | live coverage (every illegal instruction, F-RVFI-005) |
| 106 | rtl/ibex_controller.sv:268-276 | exc_req_d / exc_req_nc / exc_req_wb with constant CHERIoT terms | yes (live lines) | Condition A.4 (:268, :271, :276 sub-term vectors; T022_CORE_CHERI0); the mixed-operator parents of :268 / :271 are not selected (row 175) | live coverage of exception requests |
| 107 | rtl/ibex_controller.sv:318-319,328-331 | g_wb_exceptions priority arms cheriot_wb_err / cheriot_ex_err / cheriot_asr_err | no | Block A.3 (3 Blocks `*_err_prio = 1'b1;`) plus Condition A.4 of the :318 / :328 guards; the RV32I priority chain :314-317 and :320-327 is live | live coverage of exception priority (EXC area) |
| 108 | rtl/ibex_controller.sv:336-337 | wb_exception_o constant term ((On) & cheriot_wb_err_i) | yes (live line) | Condition A.4 | live coverage (WB exceptions block ID; B14 context) |
| 109 | rtl/ibex_controller.sv:346-367 | g_no_wb_exceptions | NOT-ELAB | none | none |
| 110 | rtl/ibex_controller.sv:377-383 | IbexExceptionPrioOnehot over all prio bits incl. the three CHERIoT ones | yes (live checker; bucket F15) | none (A.7: kept) | keep enabled (F-SEC-011) |
| 111 | rtl/ibex_controller.sv:549,858 | csr_mepcc_clrtag_o default 0 / set only in the UNREACH arm | yes (constant 0) | Toggle A.5 (port) | none |
| 112 | rtl/ibex_controller.sv:681-682 | DECODE pc_set condition term ((On) & cheriot_branch_req_i) | yes (live line) | Condition A.4 (Part C row 11) | live coverage of jumps / branches |
| 113 | rtl/ibex_controller.sv:827-831 | FLUSH exception entry for EVERY trap: pc_set_o = 1, pc_mux_o = PC_EXC, exc_pc_mux_o | yes (live RV32I, never excluded; A.8 item 1) | Condition A.4 for the `(On) & cheriot_wb_err_q` sub-term of :827-828 only; no line exclusion | live coverage of every trap entry (instr_addr_o = vector; rvfi_trap) |
| 114 | rtl/ibex_controller.sv:833-840 | csr_save_id_o / csr_save_wb_o (mepc source select) | yes (live RV32I, never excluded; A.8 item 1) | Condition A.4 for the `(On) & cheriot_wb_err_q` sub-terms only | live coverage (mepc = ID PC vs WB PC; EXC area) |
| 115 | rtl/ibex_controller.sv:850-858 | instr_fetch_err_prio CHERIoT tag / bound violation arms (ExcCauseCheriFault, csr_mepcc_clrtag_o) | no | Block A.3 (Part C rows 2-3; T022_CORE_CHERI0_B; the exc_cause_o = 28 and csr_mepcc_clrtag_o arms) plus Condition A.4 of the :850 / :854 guards; the else arm :859-862 (instruction access fault, mtval = faulting fetch address, D10) is live | live coverage (F-RVFI-026; EXC area) |
| 116 | rtl/ibex_controller.sv:866-868 | illegal_insn mtval ternary: (dual & On) ? 32'h0 : instruction bits | yes (live RV32I arm: mtval = instruction bits; bucket F9) | none as Branch: the constant-select assign-ternary has NO branch object (VCS folded it; select report "BRANCH ibex_controller [(866, 868)]: 0 vectors", README section 5 item 1); Condition A.4 vectors of the :866 select (two groups: the `(dual) & (On)` term and the inner compare) are in the file; no line exclusion (A.8 item 2) | live coverage (rvfi_trap + csrr read-back of mtval) |
| 117 | rtl/ibex_controller.sv:894-897 | ebreak mtval = pc_id_i (CHERIoT) | no | Block A.3 (Part C row 5) plus Condition A.4 of the :894 guard | none (the RV32I ebreak leaves mtval at its default; EXC area) |
| 118 | rtl/ibex_controller.sv:901-908 | store_err_prio `if ((On) & lsu_err_is_cheriot_q)` arm | no | Block A.3 (Part C row 6; T022_CTRL_CHERI0) plus Condition A.4 of the :901 guard | none |
| 119 | rtl/ibex_controller.sv:909-913 | store access-fault arm: exc_cause_o = ExcCauseStoreAccessFault, csr_mtval_o = lsu_addr_last_i | yes (live RV32I, never excluded; bucket F9; A.8 item 2) | none | live coverage (F-RVFI-013; EXC area) |
| 120 | rtl/ibex_controller.sv:915-922 | load_err_prio CHERIoT arm | no | Block A.3 (Part C row 7) plus Condition A.4 of the :915 guard | none |
| 121 | rtl/ibex_controller.sv:923-926 | load access-fault arm: exc_cause_o = ExcCauseLoadAccessFault, csr_mtval_o = lsu_addr_last_i | yes (live RV32I, never excluded; A.8 item 2) | none | live coverage (F-RVFI-013; EXC area) |
| 122 | rtl/ibex_controller.sv:928-948 | cheriot_ex_err_prio / cheriot_wb_err_prio / cheriot_asr_err_prio case items | no | Block A.3 (Part C rows 8-10; T022_CTRL_PRIO0) plus Condition A.4 of the :929 / :935 guards | none |
| 123 | rtl/ibex_controller.sv:1054-1067 | gen_update_regs_cheriot: lsu_err_is_cheriot_q, cheriot_ex_err_q, cheriot_wb_err_q, cheriot_asr_err_q flops | yes (lines execute every clock; values constant 0; bucket B11) | none (internal nets, not toggle objects) | none |
| 124 | rtl/ibex_controller.sv:1068-1075,1125-1131 | gen_cheriot_tieoff (NOT-ELAB); unused-signal sink | n/a | none | none |
| 125 | rtl/ibex_cs_registers.sv:41,63-79,153-159,263-286,357-369 | CHERIoT ports, capability CSR storage (mepc / mtvec / depc / dscratch caps, mshwm / mshwmb / cdbg_ctrl, pcc_cap), *_en_cheriot declarations | yes (constant) | Toggle A.5 (cs_registers port list; NOT csr_mshwm_new_i, which toggles) | none |
| 126 | rtl/ibex_cs_registers.sv:377-391 | misa_value_masked: X = (On) OR RV32BExtra, I = (cheriot_enable_i != On), E = (On) | yes (constant: X=1, I=1, E=0 = a plain RV32I+B value) | Condition A.4 (:379-389 vectors) | live coverage of csrr misa (F-RST-027, TP-RST-028) |
| 127 | rtl/ibex_cs_registers.sv:424-426 | CSR_MARCHID ternary | yes (live RV32I arm CSR_MARCHID_VALUE = 22) | none as Branch: the constant-select assign-ternary has NO branch object (VCS folded it; select report "BRANCH ibex_cs_registers [(424, 426)]: 0 vectors", README section 5 item 1); Condition A.4 vectors of the :424 select (two groups) are in the file | live coverage (F-SEC-037 -> F-CSR-019, TP-SEC-038, TP-CHERI-004) |
| 128 | rtl/ibex_cs_registers.sv:469-475,478-484 | CSR_MTVEC / CSR_MEPC `if ((dual) && (On)) illegal_csr` arms | no | Block A.3 (2 Blocks `illegal_csr = 1'b1;`, Blocks 21 / 24) plus Condition A.4 of the :470 / :479 guards; the else arms :473 `csr_rdata_int = mtvec_q` / :482 `csr_rdata_int = mepc_q` are live, not excluded (README section 4 and 5b: every RV32I read of mtvec / mepc executes them; excluded in dca91fd, back in coverage since 4125c36; select report "live") | live coverage of mtvec / mepc reads (CSR area) |
| 129 | rtl/ibex_cs_registers.sv:504-512,516-522 | CSR_MSECCFG / CSR_MSECCFGH: read arms under PMPEnable && !((dual) && (On)); else illegal_csr (:510-512, :519-521) | yes for the read arms (live RV32I); the else arms are UNREACH | Condition A.4 vectors of the :504 / :516 guards (tie term at its impossible value) are in the file; NO Block entry for the else arms :510-512 / :519-521 in 9ebf2d9 (outside the selected cs_registers ranges 469-475, 478-484, 678-698, 707-715, 2014-2056, 2063-2067, 2108-2209, 2218-2224, select report): kept in coverage although the carve-out lists them as UNREACH (open request (2) to rtl-arch, closing note; a Critic ruling per entry) | live coverage of mseccfg reads (PMP area) |
| 130 | rtl/ibex_cs_registers.sv:678-698 | CSR_MSHWM / CSR_MSHWMB / CSR_CDBG_CTRL read arms under (On) | no | Block A.3 (3 Blocks `csr_rdata_int = mshwm_q / mshwmb_q / cdbg_ctrl_q;`, Blocks 75 / 78 / 81; T022_CSR_MSHWM0) plus Condition A.4 of the :679 / :687 / :695 guards; the `else illegal_csr = 1` arms :682 / :690 / :698 are live, not excluded (README section 5b: reads of 0xBC1 / 0xBC2 / 0xBC4 trap; select report "live") | negative check TP-CHERI-002 (rvfi_trap + csrr read-back of mcause = 2) |
| 131 | rtl/ibex_cs_registers.sv:707-715 | PMP-CSR illegal block `if (!PMPEnable OR ((dual) && (On)))` | no (UNREACH: PMPEnable = 1 and the tie) | Block A.3 (1 Block `illegal_csr = 1'b1;`, Block 86) plus Condition A.4 of the :707 guard | none (row added for Critic C-18) |
| 132 | rtl/ibex_cs_registers.sv:736-743 | mtvec_d LSB = ~((dual) & (On)) (vectored mode) | yes (live line; constant term = 1) | Condition A.4 (:741-743) | live coverage (F-RST-004 boot value, TP-RST-003) |
| 133 | rtl/ibex_cs_registers.sv:796-797,807-808 | mepc_en / mtvec_en = ~(dual) OR (cheriot_enable_i != On) | yes (live lines; constant 1 when the case item is hit) | Condition A.4 | live coverage of mepc / mtvec software writes |
| 134 | rtl/ibex_cs_registers.sv:879-884 | mshwm_en / mshwmb_en / cdbg_ctrl_en case items | yes (the case items are reached by a write to 0xBC1/2/4, which is illegal; the assigns are constant 0) | Condition A.4 (:879, :881, :883 tie terms); no Block (the case items are outside the selected ranges and their assigns are live lines) | negative check TP-CHERI-002 (the write traps) |
| 135 | rtl/ibex_cs_registers.sv:1020-1023 | csr_we_int term (~(dual) OR (cheriot_enable_i != On) OR debug_mode_i OR pcc_cap_q.perms.SR) | yes (live line; term constant 1) | Condition A.4 (UCAPI-CSM glitch list :1020) | live coverage of every CSR write |
| 136 | rtl/ibex_cs_registers.sv:1058-1070 | mstatus_en_combi (:1062-1063) and mstatus_d_combi (:1065-1070): the write enable and next-value mux of ALL mstatus writes, with constant CHERIoT set/clr-MIE terms | yes (live RV32I, never excluded; bucket F8) | Condition A.4 for the `(On) & cheriot_csr_clr/set_mie_i` sub-terms only; no line exclusion | live coverage of mstatus writes (CSR area) |
| 137 | rtl/ibex_cs_registers.sv:1085-1086 | mepc_en_combi = mepc_en OR mepc_en_cheriot; mepc_d_combi AND-OR mux | yes (live RV32I, never excluded; bucket F8) | Condition A.4 sub-terms only | live coverage (mepc writes by traps and software) |
| 138 | rtl/ibex_cs_registers.sv:1163-1167 | mtvec_en_combi / mtvec_d_combi | yes (live RV32I, never excluded; bucket F8) | Condition A.4 sub-terms only | live coverage (mtvec writes incl. the boot init) |
| 139 | rtl/ibex_cs_registers.sv:1203-1204 | depc_en_combi / depc_d_combi | yes (live RV32I, never excluded; bucket F8) | Condition A.4 sub-terms only | live coverage (dpc writes on debug entry and by software; DBG area) |
| 140 | rtl/ibex_cs_registers.sv:1220-1222 | dscratch0_en_combi / dscratch0_d_combi | yes (live RV32I, never excluded; bucket F8) | Condition A.4 sub-terms only | live coverage (DBG area) |
| 141 | rtl/ibex_cs_registers.sv:1238-1240 | dscratch1_en_combi / dscratch1_d_combi | yes (live RV32I, never excluded; bucket F8) | Condition A.4 sub-terms only | live coverage (DBG area) |
| 142 | rtl/ibex_cs_registers.sv:1301-1303 | mshwm_en_combi = mshwm_en OR csr_mshwm_set_i (constant 0); mshwm_d = csr_mshwm_set_i ? csr_mshwm_new_i : {csr_wdata_int[31:4], 4'h0} (toggles, dead) | yes (lines live; mshwm_d toggles with csr_wdata_int; the enable is constant 0) | Condition A.4 (:1301 `mshwm_en` and `csr_mshwm_set_i` at their impossible value 1; :1302 select at 1); no Block (mshwm_d toggles with csr_wdata_int and is never swept in as CHERIoT, F13) | none (mshwm is unobservable with Off) |
| 143 | rtl/ibex_cs_registers.sv:1304-1345 | g_mshwm: ibex_csr instances u_mshwm_csr / u_mshwmb_csr / u_cdbg_ctrl_csr; csr_dbg_tclr_fault_o | yes (instances elaborate; wr_en constant 0 so the flops stay 0; bucket B13) | Toggle A.5 (csr_mshwm_o, csr_mshwmb_o, csr_dbg_tclr_fault_o ports); no Block or Condition entry on :1304-1345 (the T022_CSR_MSHWM0 proof is cited by the cs_registers Block group for the :678-698 read arms, row 130) | none |
| 144 | rtl/ibex_cs_registers.sv:1996-1997 | ASSERT_IF IbexCheriotClrMieDisabled / IbexCheriotSetMieDisabled | yes (live checkers; bucket F15) | none (A.7: kept; EC-3) | keep enabled; zero failures required |
| 145 | rtl/ibex_cs_registers.sv:2003-2013 | gen_scr declarations | n/a | none | none |
| 146 | rtl/ibex_cs_registers.sv:2014-2056 | SCR read mux on cheriot_csr_addr_i (= 5'h0 -> default arm :2051-2055) | no for the named SCR arms; the default arm executes (constant); all items kept live by the file (see Exclusion) | none in 9ebf2d9: the SCR read-mux items :2018-2048 and the default :2053 are live, not excluded (README section 5 item 7 and 5b: the selector cheriot_csr_addr_i is constant 0 and the SCR literals resolve to 24..31, but the indentation-based analysis does not parse this case statement's item layout; select report "live" Blocks 266-273; candidates for explicit entries with their cone at the first measured regression); the `case (cheriot_csr_addr_i)` header is never selected (rule 2); Toggle A.5 covers cheriot_csr_rdata_o / cheriot_csr_rcap_o | none (cheriot_csr_rdata_o / rcap_o constant: Toggle A.5) |
| 147 | rtl/ibex_cs_registers.sv:2059,2061 | pcc_cap_o = pcc_cap_q (constant ROOT_DECODED_CAP_TX); pcc_exc_cap = cheriot_pcc_to_mepc(pcc_cap_q, exception_pc, ...) | yes (pcc_cap_o constant; pcc_exc_cap TOGGLES with exception_pc; bucket F13) | Toggle A.5 (pcc_cap_o); pcc_exc_cap listed by name as live, never swept in under the gen_scr label | none |
| 148 | rtl/ibex_cs_registers.sv:2063-2067 | pcc_cap_q update `else if (cheriot_enable_i == IbexMuBiOn)` | no | Block A.3 (1 Block `pcc_cap_q <= pcc_cap_d;`, Block 277) plus Condition A.4 of the :2066 guard; the reset arm :2065 is live (README section 5b) | none |
| 149 | rtl/ibex_cs_registers.sv:2075-2105 | tr_cap / tr_addr / tf_cap / pcc_cap_d (update on csr_save_cause_i / csr_restore_mret_i / dret) | yes (TOGGLE on every trap, mret and dret in RV32I mode; bucket F13) | none: listed by name as live (A.8 v1 items), never excluded by the gen_scr block label | none (values unobservable; the lines are covered by trap traffic) |
| 150 | rtl/ibex_cs_registers.sv:2108-2125,2133-2209 | *_en_cheriot assigns and the cap flops mtvec_cap / mepc_cap / mtdc_cap / mscratchc_cap / depc_cap / dscratch0/1_cap updated only under *_en_cheriot or (On) | no for the update arms (all enables constant 0, G6); the RESET arms of these flops execute | Block A.3 per object (10 update-arm Blocks in 9ebf2d9: `mtvec_cap <= cheriot_csr_wcap_i`, `mepc_cap <= gen_scr.pcc_exc_cap`, `mepc_cap <= cheriot_csr_wcap_i`, mtdc / mscratchc / dscratch0 / dscratch1 `<= cheriot_csr_wcap_i`, `depc_cap <= gen_scr.pcc_exc_cap`, `depc_cap <= cheriot_csr_wcap_i`) plus Condition A.4 of the :2108, :2121, :2137, :2140, :2149, :2164, :2179, :2186, :2194, :2197 guards; the reset-value assignments :2114, :2136, :2155, :2170, :2185, :2203 are live, not excluded (README section 5b: `if (!rst_ni)` arms execute at every reset; select report "live"); :2142 `mepc_cap <= gen_scr.mstack_epc_cap_q` is live, not excluded (row 151) | none |
| 151 | rtl/ibex_cs_registers.sv:2126-2132 | mstack_epc_cap_q <= mepc_cap when mstack_en (NULL_CAP -> ROOT_CAP_TX on the first NMI) | yes (TOGGLES on the first non-debug trap in RV32I mode: `else if (mstack_en)` with mstack_en set on every non-debug trap entry, rtl/ibex_cs_registers.sv:2129-2131, :933; bucket F13) | live, not excluded (README section 5b; Critic CR-M-1 / M-1): the update arm :2130 Block 299, its reset arm :2128 Block 297 and the :2142 read-back Block 306 `mepc_cap <= gen_scr.mstack_epc_cap_q` (dead guard, kept on the conservative side) are removed by the A.8 carve-back table as the last filter (select report "carve-back"); since 4125c36 none of the three has an entry (grep of 9ebf2d9 for mstack_epc_cap_q: no entry line); request (1) of the closing note is closed | none (unobservable; the line is covered by the first non-debug trap, TP-RST-025 / IRQ area) |
| 152 | rtl/ibex_cs_registers.sv:2212-2224 | cheriot_fatal_err_q set `if ((On) && csr_save_cause_i && ~mtvec_cap.valid)` (:2221-2222) | no (set only when On) | Block A.3 (:2218-2224; T022_CSR_CHERI0); Toggle A.5 (cheriot_fatal_err_o) | negative check: alert_major_internal_o never fires from this source (F-SEC-002) |
| 153 | rtl/ibex_cs_registers.sv:2229-2257,2259-2260 | gen_no_scr (NOT-ELAB); unused-signal sink | n/a | none | none |
| 154 | rtl/ibex_register_file_ff.sv:21-46,58-59,69,74,79,84 | header comments, REGCAP_W / CapWidth parameters, cheriot_enable_i, rcap_a_o, rcap_b_o, wcap_a_i | yes (tie / constant) | Toggle A.5 (cheriot_enable_i, rcap_a_o, rcap_b_o, wcap_a_i) | constant-value monitor via rvfi_rs1_rcap / rvfi_rs2_rcap |
| 155 | rtl/ibex_register_file_ff.sv:88-142 | g_cheriot_rf: THE register file of this build (x0-x15 in rf_data, x16-x31 in the 35-bit rf_shared bank; we_a_dec, wshared_data, flop generates) | yes (live RV32I, never excluded; buckets B15 / F1 / F13) | none except Branch A.3 :113 and Condition A.4 :95, :113, :136-137 (next rows) | live coverage (F-RST-021/022/023, TP-RST-021..023) |
| 156 | rtl/ibex_register_file_ff.sv:113 | wshared_data = cheriot_enabled ? wcap_a_i : CapWidth'(wdata_a_i) | yes (live RV32I arm) | Branch A.3: wcap_a_i arm only (T022_RF_CAP0) | live coverage (every x16-x31 write) |
| 157 | rtl/ibex_register_file_ff.sv:136-137 | shared-flop enable: (cheriot_enabled && ...) OR (!cheriot_enabled && !RV32E && we_a_dec[i] && waddr_a_i[4]) | yes (live RV32I second term; A.8 item 8) | Condition A.4: first OR term only | live coverage (x17-x31 writes) |
| 158 | rtl/ibex_register_file_ff.sv:144-213 | g_dummy_r0 (:155-186; g_normal_r0 :188-212 NOT-ELAB): we_data_r0, rf_data_r0_q, we_shared_r0 (:160-161), rf_shared_r0_q (the x16 flop), rcap_r0 (:184, toggles: x16 data during dummies, F2) | yes (live RV32I, never excluded; buckets F1 / F2 / F13) | none: bucket F13 nets listed by name (A.8 item 8); the RF Condition vector 74 on the :160-161 `cheriot_enabled ? we_data_r0 : (...)` enable ternary was removed by the A.8 carve-back filter (select report; README section 5 item 7): live | live coverage (F-DIT-015, F-RST-022) |
| 159 | rtl/ibex_register_file_ff.sv:221-224 | rdata_a_o / rdata_b_o bank select (raddr_x_i[4] && !cheriot_enabled) | yes (live RV32I: reduces to raddr_x_i[4]) | Condition A.4 for the `!g_cheriot_rf.cheriot_enabled` sub-term only (:221, :223: constant 1 at its impossible value 0); the parent ternary vectors are not selected (row 175); no Block or Branch (A.8 item 8) | live coverage (every x16-x31 read) |
| 160 | rtl/ibex_register_file_ff.sv:227-230 | rcap_a_o / rcap_b_o = cheriot_enabled ? ... : CapWordZeroVal | yes (live constant arm) | none as Branch in 9ebf2d9 (the RF Branch group holds 1 vector for the (113) and (227-230) ranges together, `g_cheriot_rf.cheriot_enabled` true arm, Branch 0; the group annotation names both ranges, so at most one of the three ternaries carries the entry); the two RF Condition vectors 67 / 70 on these ternaries were removed by the A.8 carve-back filter (text matches the shared-net carve-backs; select report; README section 5 item 7): live | constant-value monitor rvfi_rs1_rcap / rvfi_rs2_rcap |
| 161 | rtl/ibex_register_file_ff.sv:237-239 | CheriotWaddrMSBClear / CheriotRaddrAMSBClear / CheriotRaddrBMSBClear | no (vacuous: antecedent cheriot_enabled constant 0; bucket F3) | Assert A.7 | not counted as checkers |
| 162 | rtl/ibex_register_file_ff.sv:241-327 | g_plain_rf | NOT-ELAB | none | none |
| 163 | rtl/ibex_cheriot_pkg.sv:1-965 | capability types, NULL_CAP, encode / decode functions (evaluated inline from shared modules) | n/a (types; functions inlined) | none (A.2: no coverage objects) | none |
| 164 | rtl/ibex_trvk.sv:9-420 | temporal revocation unit | not instantiated in ibex_core (ibex_top only) | none (A.2 / CC A3) | none (F-SEC-036: not a DUT feature) |
| 165 | rtl/ibex_pkg.sv:38,84-85,378-379,626-628,728,816-822 | BaseIsaRV32IorCHERIoT, OPCODE_CHERI / OPCODE_AUICGP, ExcCauseCheriFault (28), CSR_MSHWM / MSHWMB / CDBG_CTRL addresses, CSR_MARCHID_CHERIOT_VALUE, CTX_* / CRX_* enum values | n/a (constants); the CTX_* / CRX_* values are the FSM A.6 states | none beyond FSM A.6 | negative checks: mcause never 28; 0xBC1/2/4 trap; marchid = 22 |
| 166 | rtl/ibex_controller.sv:690-696 | `if (BranchPredictor)` body in DECODE (draft Part C row 12) | NOT-REACH: BranchPredictor = 0 is an elaboration constant of the opentitan configuration (gen_param_resolution.md; time-0 config banner) | Block, class P (build-parameter constant): 1 Block; EC-1 T022_CORE_BP0 PROVED, yosys constant instr_bp_taken_id = 0 (evidence 4.3), EC-2 expected URG Unreachable, EC-5 strict load. The :684 part of Part C row 12 (assign-ternary on the same parameter) has no object (folded, README section 5 item 1); in 9ebf2d9: 1 Block `nt_branch_mispredict_o = 1'b1;` (MODULE ibex_controller Block 67) | none (no branch predictor in the DUT; PC_BP mux arm never selected, F-RST-003) |
| 167 | rtl/ibex_decoder.sv:1342-1344,1348-1350 | BCOMPRESS / BDECOMPRESS multicycle bodies (draft Part C rows 42-43); the case items :1341 / :1347 stay live | NOT-REACH: RV32B = RV32BOTEarlGrey, so `RV32B == RV32BFull` is false (elaboration constant) | Block, class P: 2 Blocks; EC-1 configuration plus the legality case :641-642; EC-2 expected URG Unreachable; EC-5 strict load; in 9ebf2d9: 2 Blocks (ALU_BDECOMPRESS / ALU_BCOMPRESS, Blocks 414 / 417) | none (the encodings trap as illegal in this build: ISA / BIT area) |
| 168 | rtl/ibex_controller.sv:684; rtl/ibex_id_stage.sv:925-926,936-942 | Part C rows 12 (:684 part), 30 and 32: parameter-select assign-ternaries | live selected arm only | none: VCS folded the parameter select, no branch or condition object exists in the dump (README section 5 item 1; select report 0 vectors for :684 and :936-942) | none (EC-2 by construction) |
| 169 | rtl/ibex_controller.sv:990-993; rtl/ibex_load_store_unit.sv:605-607; rtl/ibex_multdiv_fast.sv:522-524 | Class D default arms with spare encodings: ctrl_fsm default -> RESET (ctrl_fsm_e 4-bit, 10 named values, 6 spare), ls_fsm default (ls_fsm_e 4-bit, 8 named, 8 spare), md_state default (md_fsm_e 3-bit, 7 named, 1 spare) (draft Part C rows 1, 23, 33) | no: unreachable without fault injection into the state flop; guarded by the RTL assertions IbexCtrlStateValid (rtl/ibex_controller.sv:1104-1106), IbexLsuStateValid (rtl/ibex_load_store_unit.sv:821-824), IbexMultDivStateValid (rtl/ibex_multdiv_fast.sv:532-533) | OUT of gen_exclusions.el at 9ebf2d9 (class D 2b): the three spare-encoding default arms are HELD OUT (file header line 5; README section 2 "0 (held out)"; select report "class-D spare-encoding group HELD OUT (EC-3 not filled)"); EC-1 k-induction T022_CTRL_NAMED / T022_LSU_NAMED / T022_MD_NAMED stands; the EC-3 fill (ATTEMPTS > 0, FAILURES == 0 for IbexCtrlStateValid / IbexLsuStateValid / IbexMultDivStateValid) is deferred to the first measured regression's evidence asserts.txt, read by gen_excl_select.py --ec3-asserts dv/auto_dv/evidence/gen_round_<n>/asserts.txt --ec3-round round_<n> (README section 7; Critic F-3); until then no entry and the three arms count in the denominator (legal-stimulus tiers only in the measured merge, B.7 rule 6; URG emits no separate case-default branch vector here, README section 5 item 5) | assertion coverage: the three state-valid assertions report attempts > 0 and zero failures in every measured run (TP-SEC-015 hosts IbexCtrlStateValid; the LSU / multdiv ones through gen_sva_multdiv MD-4 and the DMEM area); the first measured round's evidence asserts.txt is the EC-3 input (README section 7) |
| 170 | rtl/ibex_id_stage.sv:968-970; rtl/ibex_multdiv_fast.sv:238-240; rtl/ibex_icache.sv:1268 | Class D default arms with NO spare encoding: id_fsm default (1-bit enum, 2 named values), mult_fsm default (1-bit, 2 named), inval_state default (2-bit, 4 named) (draft Part C rows 31, 34, 35) | no: unreachable by construction of the enum | Block, class D (C.2, 2a arms): 3 Blocks in 9ebf2d9 (MODULE ibex_id_stage Block 83 `id_fsm_d = FIRST_CYCLE;`, ibex_multdiv_fast Block 11 `gen_mult_single_cycle.mult_state_d = MULL;`, ibex_icache Block 265, the empty default statement); EC-1 declaration cite; EC-5 strict load pass 13; no EC-3 assertion needed | none |
| 171 | rtl/ibex_compressed_decoder.sv (Zcmp expander) | Class R rows 37-40 of draft Part C: Zcmp mismatched-state default arms | reachability not yet proved (EC-4: the seven per-state covers must be hit on a full measured regression) | none: OUT of gen_exclusions.el until EC-4 passes (README section 2 last row, F-5); a later inclusion needs a recorded Critic ruling | live coverage until ruled (CMP area Zcmp items; TP-RVFI-025 / TP-RVFI-026 exercise every sequence position) |
| 172 | rtl/ibex_cheriot_ex.sv (always_comb defaults, statement headers of `case (cheriot_adder_*_sel_i)` / `if (cheriot_setaddr_sel_i == ...)`, the `if (!rst_ni)` reset arm and reset-value assignments, zero-value vectors of conditions on constant-0 internal selects) | objects of the module with no dead guard (the 38 A.1 objects the dca91fd sweep had selected and the strict load refuted belong here) | yes: the module's combinational logic runs with cheriot off; only the arm bodies and the impossible-value vectors are dead | none in 9ebf2d9: not selected by the guard analysis (README section 1 rule 3 selects dead arms only; statement headers execute with their scope, rule 2); the pass-13 run dropped 0 entries on the --attempts logs (README COUNTS block "entries refuted ... and dropped: 0"); the dca91fd sweep "everything except the live list" is gone (README section 4) | none (coverage-tool semantics, not RTL findings; the objects count in the denominator) |
| 173 | rtl/ibex_cs_registers.sv:2014-2224 reset arms (:2065 pcc_cap_q, :2114 mtvec_cap, :2128 mstack_epc_cap_q, :2136 mepc_cap, :2155 mtdc_cap, :2170 mscratchc_cap, :2185 depc_cap, :2203 dscratch0_cap, :2220 cheriot_fatal_err_q), the :2053 `cheriot_csr_rdata_o = 32'b0` default, the `case (cheriot_csr_addr_i)` header and the PMP-illegal `if (...)` header at :707 | in-range objects the predicate keeps live (select report: 21 in-range Blocks kept in coverage, no dead guard, plus 3 A.8 carve-backs) | yes: reset arms and defaults execute with cheriot off | none in 9ebf2d9: reset arms (`if (!rst_ni)`) and always_comb defaults have no dead guard, statement headers are never selected (README section 1 rule 2, section 5b; select report "live" Blocks 273, 275, 292, 302, 311, 316, 321, 328, 335 and carve-back Block 297); the corresponding UPDATE arms remain excluded (row 150) except :2130 / :2142 (row 151 carve-backs) | none |
| 174 | rtl/ibex_id_stage.sv:747; rtl/ibex_core.sv:1343-1344 | id_stage Condition 37 `(csr_access_o & instr_executing & (param & On ? first_cycle : id_done))` (a ternary used as an OPERAND has the value of an arm, not of its select); core Conditions 90/91 `instr_exec & !(On OR Off)` (URG encodes a top-level negation by the value of the negated sub-expression) | yes (live condition objects) | none for the parent vectors (the classifier binds a negation to one operand and treats ternaries only at the top level, README section 1 rule 4; row 175 lists id_stage :747); the sub-term vectors with the tie at its impossible value ARE in the file: :747 (two id_stage groups) and :1343 (row 11; the top-level negation is encoded by the inner value) | live coverage (CSR writes; the cheriot_enable_i MuBi negative check, TP-SEC-017) |
| 175 | rtl/ibex_controller.sv:268,271,837; rtl/ibex_core.sv:648,649,1405,1414,2289,2290; rtl/ibex_cs_registers.sv:377,739,845,2108,2121,2149,2164,2179,2194,2197; rtl/ibex_decoder.sv:238; rtl/ibex_id_stage.sv:747,1012,1095; rtl/ibex_register_file_ff.sv:221,223; rtl/ibex_wb_stage.sv:115,183,190,193,195 | Conditions that mention a CHERIoT name but were NOT selected by the classifier (select report "manual follow-up" list): mixed-operator parents whose constant sub-term is handled by URG's own sub-condition object, the `cheriot_csr_addr_i == CHERIOT_SCR_*` comparisons (constant ports compared with constants; their lines are already Block-excluded), the mtvec / misa ternaries on the BaseIsa parameter, and the fetch_enable_i / mcounteren_writable_i comparisons | yes (kept in coverage) | none: kept in coverage (README section 5 item 2); the first measured regression's holes decide whether any gets an explicit entry (Critic ruling per entry). The fetch_enable_i vectors (rtl/ibex_core.sv:648, :649, :1414) and mcounteren_writable_i (:845) are DRIVEN pins in the real TB (Q-007) and are never excluded (README section 5 item 3). Verified against the pass-13 select report list (the same 30 lines, 47 condition entries); several of these lines also carry selected sub-term vectors (:377, :739, :747, :1012, :1095, :115, :183, :190-195, :221, :223, :238, :268, :271, :837, :2108-2197): only the mixed-operator / ternary parents stay live | live coverage (fetch_enable_i encodings TP-SEC-016 / TP-RST-013; mcounteren_writable_i TP-SEC-019; misa / mtvec TP-RST-028 / TP-RST-003) |
| 176 | rtl/ibex_cheriot_ex.sv:970; rtl/ibex_cs_registers.sv:377,1020; rtl/ibex_core.sv:1343 | The four glitch-covered cheriot_enable_i tie conditions (Critic N-2 / F-4, LOG-007): covered only by -cm_glitch 1 artefacts | no (constant tie) | Condition vectors, A.4, class T: in the file and loaded strictly under the -cm_glitch 0 build only (R-002 recorded; README section 5 item 3 / F-4); all four present in 9ebf2d9 (cheriot_ex :970 two groups, cs_registers :377 and :1020, core :1343) | none (every measured build uses -cm_glitch 0, gen_tb_architecture.md 8.1 item 2) |

Note on rtl/ibex_cheriot_ex.sv:991-994: csr_mshwm_set_o is NOT gated by cheriot_enable_i
(lsu_req & lsu_we & mshwmb <= addr < mshwm). It is constant 0 only because mshwm/mshwmb reset to
0 and are writable only when On (rtl/ibex_cs_registers.sv:879-882,1302; carve-out F17). A negative
check that mshwm stays 0 is not possible (readable only when On, so unobservable); recorded as
accepted. csr_mshwm_new_o (:994) toggles and is never excluded (bucket D / F13).

Note on the exclusion mechanics: the "no" rows and the constant ports of the "yes (constant 0)"
rows are the objects of the single exclusion cheriot-out-of-scope in gen_exclusions.el at 9ebf2d9
(pass 13; README COUNTS block, generated): 1421 entry lines = 186 Block, 83 Branch vector, 667
Condition vector, 463 Toggle, 2 Fsm + 5 State + 12 Transition, 3 Assert, in 41 (module, metric)
scopes of 13 modules and 492 annotation groups (487 class T, 2 class P, 3 class D). By rule: A.1
(MODULE ibex_cheriot_ex, guard analysis) = 75 Blocks, 66 Branch vectors, 246 Condition vectors, 144
Toggle entries in 218 groups; A.3 = 105 Blocks and 17 true-arm Branch vectors in the shared modules
(Blocks / Branch vectors: core 1 / 7, id_stage 2 / 1, decoder 36 / 3, compressed_decoder 11 / 0,
controller 14 / 0, load_store_unit 24 / 3, cs_registers 17 / 0, wb_stage 0 / 2, register_file_ff 0
/ 1); A.4 = 421 vectors in 10 shared modules; A.5 = 463 port / struct-field entries (319 shared,
144 cheriot_ex); A.6 = ls_fsm_cs 3 states + 7 transitions, cap_rx_fsm_q 2 states + 5 transitions;
A.7 = 3; class P = 3 Blocks (controller :690-696, decoder :1342-1344 / :1348-1350); class D 2a = 3
Blocks (id_stage :968-970, multdiv_fast :238-240, icache :1268); class D 2b = 0 (held out, row
169); class R = 0 (row 171). Every entry carries the A.0 annotation (class, RTL location, dead
guard or constant term, tie chain or parameter, EC set, T022_* pointer into
dv/auto_dv/evidence/gen_t022_formal/). The RTL isolation assertions
(rtl/ibex_id_stage.sv:1297-1300, rtl/ibex_load_store_unit.sv:833-834,
rtl/ibex_cs_registers.sv:1996-1997) and the controller one-hot assertion
(rtl/ibex_controller.sv:377-383) stay enabled as the proof that CHERIoT logic is inert (EC-3); only
the three vacuous register-file Cheriot*MSBClear assertions are excluded (A.7; README section 5
item 4). Strict-load status: pass 13 loads against the round-0 re-baseline with 0 warnings and 0
errors (rtl-arch-007; gated rows identical to pass 12); the first measured regression re-runs the
generator against its own dump (F-1) and fills the class-D 2b EC-3 fields from its evidence
asserts.txt (F-3, README section 7). Cross-area requests of the earlier table revisions, restated
against 9ebf2d9: (1) row 151, mstack_epc_cap_q: CLOSED at 4125c36 (carve-back filter; no entry in
the file); (2) the CSR_MSECCFG / CSR_MSECCFGH illegal else-arms rtl/ibex_cs_registers.sv:510-512,
:519-521 are UNREACH in the carve-out but have no Block entry (row 129): still open, narrows
coverage if granted, a Critic ruling per entry at the first measured regression; (3) the constant
ports rtl/ibex_prefetch_buffer.sv:30 and rtl/ibex_fetch_fifo.sv:33 (cheriot_force_uc_i) and the
fetch_fifo :127 vector have no scope in the file (rows 24, 31): still open, same rule. Rows
re-aligned to 9ebf2d9 in this revision (84 rows, rewritten in place): 8, 10, 11, 13, 14, 17, 24,
31, 35, 37, 38, 39, 42, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 61, 65, 66, 67, 70, 71, 73,
74, 78, 80, 85, 86, 87, 88, 89, 91, 93, 95, 97, 99, 100, 106, 107, 115, 116, 117, 118, 120, 122,
126, 127, 128, 129, 130, 131, 133, 134, 135, 137, 142, 143, 146, 148, 150, 151, 155, 157, 158, 159,
160, 166, 167, 169, 170, 172, 173, 174, 175, 176. README consistency note for rtl-arch: section 4
opens with "10 entries of the current selection were covered by the NOP smoke and are dropped"
while the generated COUNTS block of the same file reports 0 entries refuted and dropped and the
select report lists no drop; this table follows the generated block.

---------------------------------------------------------------------------------------------------

