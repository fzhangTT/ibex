# DV Lead response to Critic verdict v1 on the feature list (T-007 part 1)

Artifact reviewed: dv/auto_dv/work/dv-lead/gen_feature_list_draft.md (v1). Remediated artifact:
dv/auto_dv/docs/gen_feature_list.md (v2, promoted; regenerated from the corrected area parts under
dv/auto_dv/work/dv-lead/parts/ by gen_build_docs.py). Date: 2026-09-03. No finding is disputed.

| Finding | Severity | Status | Where / how |
|---|---|---|---|
| C-01 | info | noted | sample result; citation re-verification done by every area author (sed/grep dump of all RTL cites) |
| C-02 | medium | fixed | F-EXC-009, F-CSR-017 (now ALIAS) and canonical F-DBG-050 state that only dcsr/dpc/dscratch0/1 trap outside debug mode; tselect/tdata1-3 legal from M-mode; doc defect D12 recorded; TP items expecting a trap corrected (TP-EXC-008 pass with negative fire-check) |
| C-03 | low | fixed | F-PMP-038: 29 trailing ones; observable named |
| C-04 | low | fixed | every listed citation corrected (F-DBG-042, F-TRG-028, F-PMC-046, F-DMEM-042 gen_memcap_rd, F-ISA-046, F-IMEM-028, F-IRQ-056, F-EXC-060 RTL-defined, F-PMC-007); authors found and fixed further off-by-one and non-elaborated-arm cites (e.g. F-ISA-024/F-BTALU-001 g_branch_set_direct, F-DMEM-033/F-FE-016/F-IC-036/F-IC-039) |
| C-05 | medium | fixed | F-ISA-012 (fsri legal), F-MUL-022 (rem mechanism), F-FE-017 (3 buffers; depth bins re-cut), F-IC-006 (doc defect D9), F-DIT-025 (SIMULATION dependency + observable), F-SEC-032 (bits 6/7 RW; checker expectation corrected) |
| C-06 | medium | fixed | F-DBG-044/059 one-cycle dip; F-RST-008 FIRST_FETCH one cycle; F-IRQ-051 likewise. Follow-up from rtl-arch's fact-check row 29: the dip is a ctrl_busy fact; core_busy_o dips only with no fetch beat outstanding, no invalidation, LSU idle: carried in gen_tb_architecture.md 8.2 item 1 and applied to the features in v3 |
| C-07 | medium | fixed | every ACTIVE Observable at names a DUT port or RVFI field using the Section 0 shorthand; F-DBG-067 corrected (now ALIAS of F-SEC-023) |
| C-08 | low | fixed | F-DIT-011 (P1 candidate), F-FE-012 (P3/boundary derivation), F-CSR-001 (rvfi_rd_wdata + read-back; internal net under P6 debug-only) |
| C-09 | medium | fixed | 8 new features: F-DBG-068 (H-C1 variants; dret not an arc per RTL), F-IRQ-066 (H-N1), F-CMP-069 (H-Z6; only fetch_err gates the expander, PMP error does not), F-BIT-041 (H-I1), F-MUL-028 (H-D3 assertion feature), F-CMP-070 (H-Z4), F-RVFI-034 (P10 one-hot RF write), F-DIT-030 (dummy DIV x interrupt); each with TP item and bin |
| C-10 | medium | fixed | 7 new features: F-IMEM-031/F-DMEM-048 (gnt without req rule), F-IMEM-032 (I-side unsolicited rvalid, informational test), F-DMEM-049 (no X on rdata), F-DMEM-050 (SECDED covers all lanes; valid on loads: RTL-defined observation, coverage only, per TB Infra C3.2), F-IC-048 (disable does not invalidate), F-DMEM-051 (EX-09 WB write timings); F-IC-022 states the 258-cycle minimum; F-DMEM-035 stands (load wdata architecturally don't-care) |
| C-11 | info | forwarded | rtl-arch corrected H-L4/CSR-23/H-I4/EX-04 in T-017 (gen_dvlead_reconciliation.md Section 5) |
| C-12 | medium | fixed | edge rule recorded in Section 0; all 579 edge entries reviewed by the area authors; 154 entries FOLDED into parent bins (Status field), 341 ACTIVE edges remain |
| C-13 | low | fixed | F-EXC-047 parent corrected (then ALIAS of F-SEC-023); all 27 depth-2 chains re-pointed to base features; validation shows 0 depth-2 chains |
| C-14 | medium | fixed | Status field ALIAS on 95 entries in 66 clusters, canonical per the DV Lead's decision list (parts/README_FIX_BRIEF.md); Section 3.1 generated from the Status fields; completeness counts ACTIVE only |
| C-15 | low | fixed | Section 3 is generated from explicit IDs; no prose references remain |
| C-16 | high | fixed | F-CHERI-001 table rebuilt row for row against gen_exclusions_draft.md (165 rows, exclusion kind per row); the six rows now cite the dead sub-arm or term only; live RV32I rows added for controller trap entry, fault arms, illegal mtval arm, illegal_insn_d, instr_kill, mstatus_en/_d_combi, LSU FSM flop, alert assign |
| C-17 | medium | fixed | live arm cited in yes rows, dead arm in no rows (decoder jump/auipc/illegal arms, compressed decoder else-arms); csr_mshwm_new toggling-but-dead; lsu_wcap_o constant; row 36/37 overlap removed; block-label exclusions replaced by sub-block cites; RegFileCapEccWidth note corrected (RegFileECC=0; 42 if 1) |
| C-18 | medium | fixed | rows added for cs_registers :707-715, depc/dscratch *_combi (F8), rvfi_id_done (F10), resp_is_cap_q, rvfi_rd_cap_d; every bucket-F item appears as live |
| C-19 | low | fixed | row count stated (165); rule sentence added (exclusion file authoritative; table records the DV consequence; constant nets need toggle exclusions) |
| C-20 | medium | fixed | B6 reclassified RTL-defined (Sdext.adoc:32, :51; agrees with rtl-arch T-017); TP-EXC-046 and TP-DBG-034 pass; bug log keeps the ID as not-a-bug |
| C-21 | medium | fixed | dcsr.ebreaks is B15 (spec violation, core_registers.xml:163-172; rtl-arch BUG-03 alias); items expected-fail with checker predicting 0 |
| C-22 | low | fixed | B5 cited against core_registers.xml:292-298; reading report Section 3 item 4 corrected (xml/ on disk) |
| C-23 | low | fixed | merged doc-defect list D1..D19 in gen_bug_log.md Section 3 (D5 retired); features cite the canonical D numbers |
| C-24 | info | forwarded | rtl-arch T-017 corrected the map/summary items |
| C-25 | info | noted | no change |
| C-26 | low | fixed | 22 prefixes; 165 rows; "spot-checked by the author; area authors re-dumped all RTL citations for v2" |

Residual items the DV Lead carries into v3 (not blocking promotion): core_busy_o port rule per
fact-check row 29 on F-DBG-044/059 and F-IRQ-051; F-DBG-017 observable (rvfi_trap is 0 on
ebreak-into-debug, Critic pre-review S-2); F-DMEM-050 wording per TB Infra C3.2; re-alignment of the
F-CHERI-001 table with rtl-arch's exclusion v2 when it lands (T-022 rows 37-40 pending).
