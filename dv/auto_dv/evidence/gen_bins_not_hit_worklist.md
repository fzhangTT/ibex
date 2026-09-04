# bins_not_hit work list for the 13 measured entries (DV Lead, derived at the round's pinned commit)

Three classes, each with the reason its bins need. Class A and B reasons are ready to paste; class C
reasons are the Test Writer's triage and the shape is given. Adding a bin here removes it from BOTH the
rendered manifest and the test's declare_bins(), because both go through gen_fcov_manifest.plan_bins
(gen_test_lib.py:915-918), so no plan edit and no generator change is needed.

## Class A: the covergroup is not rendered

Reason to use, per bin, with the covergroup's own name and plan id substituted:

    "covergroup <cg> not rendered in gen_fcov_groups.svh: no bin of it can be hit until <CG-id> is built"

### gen_test_bit_draft (measured): 15 of 15 declared bins, 1 covergroups
    gen_bit_perm_cg (CG-BIT-004, gen_fcov_plan.md:888): 15 bins
    bins:
        gen_bit_perm_cg.cp_grev_ctrl.c0
        gen_bit_perm_cg.cp_grev_ctrl.c31
        gen_bit_perm_cg.cp_op.gorc
        gen_bit_perm_cg.cp_op.grev
        gen_bit_perm_cg.cp_operand.single_bit
        gen_bit_perm_cg.cp_rs2_upper.nonzero
        gen_bit_perm_cg.cp_rs2_upper.zero
        gen_bit_perm_cg.cr_grev_ctrl.gorc_c0
        gen_bit_perm_cg.cr_grev_ctrl.gorc_c31
        gen_bit_perm_cg.cr_grev_ctrl.grev_c0
        gen_bit_perm_cg.cr_grev_ctrl.grev_c31
        gen_bit_perm_cg.cr_reg_upper.gorc_nonzero
        gen_bit_perm_cg.cr_reg_upper.gorc_zero
        gen_bit_perm_cg.cr_reg_upper.grev_nonzero
        gen_bit_perm_cg.cr_reg_upper.grev_zero

### gen_test_bit_ratified (measured): 176 of 830 declared bins, 7 covergroups
    gen_bit_clmul_crc_cg (CG-BIT-007, gen_fcov_plan.md:942): 77 bins
    gen_bit_perm_cg (CG-BIT-004, gen_fcov_plan.md:888): 39 bins
    gen_bit_rotate_shiftones_cg (CG-BIT-003, gen_fcov_plan.md:870): 23 bins
    gen_bit_ternary_cg (CG-BIT-008, gen_fcov_plan.md:958): 17 bins
    gen_bit_xperm_cg (CG-BIT-005, gen_fcov_plan.md:908): 11 bins
    gen_bit_decode_cg (CG-BIT-011, gen_fcov_plan.md:1023): 8 bins
    gen_bit_bfp_cg (CG-BIT-009, gen_fcov_plan.md:979): 1 bins
    bins:
        gen_bit_bfp_cg.cp_rd_x0.yes
        gen_bit_clmul_crc_cg.cp_bit_sum.ge32
        gen_bit_clmul_crc_cg.cp_bit_sum.lt32
        gen_bit_clmul_crc_cg.cp_op.clmul
        gen_bit_clmul_crc_cg.cp_op.clmulh
        gen_bit_clmul_crc_cg.cp_op.clmulr
        gen_bit_clmul_crc_cg.cp_op.crc32_b
        gen_bit_clmul_crc_cg.cp_op.crc32_h
        gen_bit_clmul_crc_cg.cp_op.crc32_w
        gen_bit_clmul_crc_cg.cp_op.crc32c_b
        gen_bit_clmul_crc_cg.cp_op.crc32c_h
        gen_bit_clmul_crc_cg.cp_op.crc32c_w
        gen_bit_clmul_crc_cg.cp_rd_x0.no
        gen_bit_clmul_crc_cg.cp_rd_x0.yes
        gen_bit_clmul_crc_cg.cp_rs1_class.all_ones
        gen_bit_clmul_crc_cg.cp_rs1_class.one
        gen_bit_clmul_crc_cg.cp_rs1_class.rand
        gen_bit_clmul_crc_cg.cp_rs1_class.single_bit
        gen_bit_clmul_crc_cg.cp_rs1_class.zero
        gen_bit_clmul_crc_cg.cp_rs2_class.all_ones
        gen_bit_clmul_crc_cg.cp_rs2_class.one
        gen_bit_clmul_crc_cg.cp_rs2_class.rand
        gen_bit_clmul_crc_cg.cp_rs2_class.single_bit
        gen_bit_clmul_crc_cg.cp_rs2_class.zero
        gen_bit_clmul_crc_cg.cr_clmul_bitsum.clmul_ge32
        gen_bit_clmul_crc_cg.cr_clmul_bitsum.clmul_lt32
        gen_bit_clmul_crc_cg.cr_clmul_bitsum.clmulh_ge32
        gen_bit_clmul_crc_cg.cr_clmul_bitsum.clmulh_lt32
        gen_bit_clmul_crc_cg.cr_clmul_bitsum.clmulr_ge32
        gen_bit_clmul_crc_cg.cr_clmul_bitsum.clmulr_lt32
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmul_all_ones
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmul_one
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmul_rand
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmul_single_bit
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmul_zero
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulh_all_ones
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulh_one
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulh_rand
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulh_single_bit
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulh_zero
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulr_all_ones
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulr_one
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulr_rand
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulr_single_bit
        gen_bit_clmul_crc_cg.cr_clmul_rs2.clmulr_zero
        gen_bit_clmul_crc_cg.cr_op_rd_x0.clmul_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.clmul_yes
        gen_bit_clmul_crc_cg.cr_op_rd_x0.clmulh_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.clmulh_yes
        gen_bit_clmul_crc_cg.cr_op_rd_x0.clmulr_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.clmulr_yes
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32_b_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32_b_yes
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32_h_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32_h_yes
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32_w_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32_w_yes
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32c_b_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32c_b_yes
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32c_h_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32c_h_yes
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32c_w_no
        gen_bit_clmul_crc_cg.cr_op_rd_x0.crc32c_w_yes
        gen_bit_clmul_crc_cg.cr_op_rs1.clmul_all_ones
        gen_bit_clmul_crc_cg.cr_op_rs1.clmul_one
        gen_bit_clmul_crc_cg.cr_op_rs1.clmul_rand
        gen_bit_clmul_crc_cg.cr_op_rs1.clmul_single_bit
        gen_bit_clmul_crc_cg.cr_op_rs1.clmul_zero
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulh_all_ones
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulh_one
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulh_rand
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulh_single_bit
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulh_zero
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulr_all_ones
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulr_one
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulr_rand
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulr_single_bit
        gen_bit_clmul_crc_cg.cr_op_rs1.clmulr_zero
        gen_bit_decode_cg.cp_illegal_class.bclri_bit25
        gen_bit_decode_cg.cp_illegal_class.bexti_bit25
        gen_bit_decode_cg.cp_illegal_class.binvi_bit25
        gen_bit_decode_cg.cp_illegal_class.bseti_bit25
        gen_bit_decode_cg.cp_misa.b_clear
        gen_bit_decode_cg.cp_misa.c_set
        gen_bit_decode_cg.cp_misa.m_set
        gen_bit_decode_cg.cp_misa.x_set
        gen_bit_perm_cg.cp_bit25.b0
        gen_bit_perm_cg.cp_grev_ctrl.c24
        gen_bit_perm_cg.cp_grev_ctrl.c7
        gen_bit_perm_cg.cp_op.gorc
        gen_bit_perm_cg.cp_op.gorci
        gen_bit_perm_cg.cp_op.grev
        gen_bit_perm_cg.cp_op.grevi
        gen_bit_perm_cg.cp_op.shfl
        gen_bit_perm_cg.cp_op.shfli
        gen_bit_perm_cg.cp_op.unshfl
        gen_bit_perm_cg.cp_op.unshfli
        gen_bit_perm_cg.cp_operand.all_ones
        gen_bit_perm_cg.cp_operand.bytes_01020304
        gen_bit_perm_cg.cp_operand.rand
        gen_bit_perm_cg.cp_operand.single_bit
        gen_bit_perm_cg.cp_operand.zero
        gen_bit_perm_cg.cp_rd_x0.no
        gen_bit_perm_cg.cp_rd_x0.yes
        gen_bit_perm_cg.cr_op_operand.gorci_all_ones
        gen_bit_perm_cg.cr_op_operand.gorci_bytes_01020304
        gen_bit_perm_cg.cr_op_operand.gorci_rand
        gen_bit_perm_cg.cr_op_operand.gorci_single_bit
        gen_bit_perm_cg.cr_op_operand.gorci_zero
        gen_bit_perm_cg.cr_op_rd_x0.gorc_no
        gen_bit_perm_cg.cr_op_rd_x0.gorc_yes
        gen_bit_perm_cg.cr_op_rd_x0.gorci_no
        gen_bit_perm_cg.cr_op_rd_x0.gorci_yes
        gen_bit_perm_cg.cr_op_rd_x0.grev_no
        gen_bit_perm_cg.cr_op_rd_x0.grev_yes
        gen_bit_perm_cg.cr_op_rd_x0.grevi_no
        gen_bit_perm_cg.cr_op_rd_x0.grevi_yes
        gen_bit_perm_cg.cr_op_rd_x0.shfl_no
        gen_bit_perm_cg.cr_op_rd_x0.shfl_yes
        gen_bit_perm_cg.cr_op_rd_x0.shfli_no
        gen_bit_perm_cg.cr_op_rd_x0.shfli_yes
        gen_bit_perm_cg.cr_op_rd_x0.unshfl_no
        gen_bit_perm_cg.cr_op_rd_x0.unshfl_yes
        gen_bit_perm_cg.cr_op_rd_x0.unshfli_no
        gen_bit_perm_cg.cr_op_rd_x0.unshfli_yes
        gen_bit_rotate_shiftones_cg.cp_op.rol
        gen_bit_rotate_shiftones_cg.cp_op.ror
        gen_bit_rotate_shiftones_cg.cp_op.rori
        gen_bit_rotate_shiftones_cg.cp_op.slo
        gen_bit_rotate_shiftones_cg.cp_op.sloi
        gen_bit_rotate_shiftones_cg.cp_op.sro
        gen_bit_rotate_shiftones_cg.cp_op.sroi
        gen_bit_rotate_shiftones_cg.cp_rd_x0.no
        gen_bit_rotate_shiftones_cg.cp_rd_x0.yes
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.rol_no
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.rol_yes
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.ror_no
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.ror_yes
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.rori_no
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.rori_yes
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.slo_no
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.slo_yes
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.sloi_no
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.sloi_yes
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.sro_no
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.sro_yes
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.sroi_no
        gen_bit_rotate_shiftones_cg.cr_op_rd_x0.sroi_yes
        gen_bit_ternary_cg.cp_op.cmix
        gen_bit_ternary_cg.cp_op.cmov
        gen_bit_ternary_cg.cp_op.fsl
        gen_bit_ternary_cg.cp_op.fsr
        gen_bit_ternary_cg.cp_op.fsri
        gen_bit_ternary_cg.cp_rd_x0.no
        gen_bit_ternary_cg.cp_rd_x0.yes
        gen_bit_ternary_cg.cr_op_rd_x0.cmix_no
        gen_bit_ternary_cg.cr_op_rd_x0.cmix_yes
        gen_bit_ternary_cg.cr_op_rd_x0.cmov_no
        gen_bit_ternary_cg.cr_op_rd_x0.cmov_yes
        gen_bit_ternary_cg.cr_op_rd_x0.fsl_no
        gen_bit_ternary_cg.cr_op_rd_x0.fsl_yes
        gen_bit_ternary_cg.cr_op_rd_x0.fsr_no
        gen_bit_ternary_cg.cr_op_rd_x0.fsr_yes
        gen_bit_ternary_cg.cr_op_rd_x0.fsri_no
        gen_bit_ternary_cg.cr_op_rd_x0.fsri_yes
        gen_bit_xperm_cg.cp_op.xperm_b
        gen_bit_xperm_cg.cp_op.xperm_h
        gen_bit_xperm_cg.cp_op.xperm_n
        gen_bit_xperm_cg.cp_rd_x0.no
        gen_bit_xperm_cg.cp_rd_x0.yes
        gen_bit_xperm_cg.cr_op_rd_x0.xperm_b_no
        gen_bit_xperm_cg.cr_op_rd_x0.xperm_b_yes
        gen_bit_xperm_cg.cr_op_rd_x0.xperm_h_no
        gen_bit_xperm_cg.cr_op_rd_x0.xperm_h_yes
        gen_bit_xperm_cg.cr_op_rd_x0.xperm_n_no
        gen_bit_xperm_cg.cr_op_rd_x0.xperm_n_yes

### gen_test_cmp_zca (measured): 13 of 337 declared bins, 2 covergroups
    gen_isa_system_cg (CG-ISA-009, gen_fcov_plan.md:476): 12 bins
    gen_cmp_illegal_cg (CG-CMP-004, gen_fcov_plan.md:687): 1 bins
    bins:
        gen_cmp_illegal_cg.cp_class.addi16sp_imm0
        gen_isa_system_cg.cp_debug_mode.no
        gen_isa_system_cg.cp_ebreakm.clr
        gen_isa_system_cg.cp_ebreakm.set
        gen_isa_system_cg.cp_ebreaku.set
        gen_isa_system_cg.cp_op.c_ebreak
        gen_isa_system_cg.cp_outcome.debug_entry
        gen_isa_system_cg.cp_outcome.exception
        gen_isa_system_cg.cp_priv.m
        gen_isa_system_cg.cp_priv.u
        gen_isa_system_cg.cr_ebreak.c_m_dbg
        gen_isa_system_cg.cr_ebreak.c_m_exc
        gen_isa_system_cg.cr_ebreak.c_u_dbg

### gen_test_csr_access (measured): 76 of 80 declared bins, 4 covergroups
    gen_csr_access_class_cg (CG-CSR-001, gen_fcov_plan.md:1202): 41 bins
    gen_csr_trap_handling_warl_cg (CG-CSR-003, gen_fcov_plan.md:1255): 20 bins
    gen_csr_secureseed_cg (CG-CSR-010, gen_fcov_plan.md:1422): 10 bins
    gen_csr_write_effect_cg (CG-CSR-012, gen_fcov_plan.md:1465): 5 bins
    bins:
        gen_csr_access_class_cg.cp_aclass.alias_impl
        gen_csr_access_class_cg.cp_aclass.alias_unimpl
        gen_csr_access_class_cg.cp_aclass.info_ro
        gen_csr_access_class_cg.cp_aclass.pmp
        gen_csr_access_class_cg.cp_aclass.rw_m
        gen_csr_access_class_cg.cp_aclass.wi_m
        gen_csr_access_class_cg.cp_iclass.none
        gen_csr_access_class_cg.cp_op.csrrc
        gen_csr_access_class_cg.cp_op.csrrci
        gen_csr_access_class_cg.cp_op.csrrs
        gen_csr_access_class_cg.cp_op.csrrsi
        gen_csr_access_class_cg.cp_op.csrrw
        gen_csr_access_class_cg.cp_op.csrrwi
        gen_csr_access_class_cg.cp_priv.m
        gen_csr_access_class_cg.cp_rd.nonx0
        gen_csr_access_class_cg.cp_rd.x0
        gen_csr_access_class_cg.cp_rs1.zero
        gen_csr_access_class_cg.cp_trap.ok
        gen_csr_access_class_cg.cr_iclass_priv.none_m
        gen_csr_access_class_cg.cr_priv_aclass_trap.m_alias_impl_ok
        gen_csr_access_class_cg.cr_priv_aclass_trap.m_alias_unimpl_ok
        gen_csr_access_class_cg.cr_priv_aclass_trap.m_info_ro_ok
        gen_csr_access_class_cg.cr_priv_aclass_trap.m_pmp_ok
        gen_csr_access_class_cg.cr_priv_aclass_trap.m_rw_m_ok
        gen_csr_access_class_cg.cr_priv_aclass_trap.m_wi_m_ok
        gen_csr_access_class_cg.cr_rd_x0_write.csrrc_rdx0_rw_m
        gen_csr_access_class_cg.cr_rd_x0_write.csrrci_rdx0_rw_m
        gen_csr_access_class_cg.cr_rd_x0_write.csrrs_rdx0_rw_m
        gen_csr_access_class_cg.cr_rd_x0_write.csrrsi_rdx0_rw_m
        gen_csr_access_class_cg.cr_rd_x0_write.csrrw_rdnz_rw_m
        gen_csr_access_class_cg.cr_rd_x0_write.csrrw_rdx0_rw_m
        gen_csr_access_class_cg.cr_rd_x0_write.csrrw_rdx0_wi_m
        gen_csr_access_class_cg.cr_rd_x0_write.csrrwi_rdx0_rw_m
        gen_csr_access_class_cg.cr_rs1zero_ro.csrrc_x0_alias_ok
        gen_csr_access_class_cg.cr_rs1zero_ro.csrrc_x0_info_ok
        gen_csr_access_class_cg.cr_rs1zero_ro.csrrci_0_alias_ok
        gen_csr_access_class_cg.cr_rs1zero_ro.csrrci_0_info_ok
        gen_csr_access_class_cg.cr_rs1zero_ro.csrrs_x0_alias_ok
        gen_csr_access_class_cg.cr_rs1zero_ro.csrrs_x0_info_ok
        gen_csr_access_class_cg.cr_rs1zero_ro.csrrsi_0_alias_ok
        gen_csr_access_class_cg.cr_rs1zero_ro.csrrsi_0_info_ok
        gen_csr_secureseed_cg.cp_gap.g1
        gen_csr_secureseed_cg.cp_op.csrrc
        gen_csr_secureseed_cg.cp_op.csrrci
        gen_csr_secureseed_cg.cp_op.csrrs
        gen_csr_secureseed_cg.cp_op.csrrsi
        gen_csr_secureseed_cg.cp_rs1.zero
        gen_csr_secureseed_cg.cr_op_form_gap.csrrc_x0_g1
        gen_csr_secureseed_cg.cr_op_form_gap.csrrci_0_g1
        gen_csr_secureseed_cg.cr_op_form_gap.csrrs_x0_g1
        gen_csr_secureseed_cg.cr_op_form_gap.csrrsi_0_g1
        gen_csr_trap_handling_warl_cg.cp_csr.mscratch
        gen_csr_trap_handling_warl_cg.cp_csr.mtval
        gen_csr_trap_handling_warl_cg.cp_op.csrrc
        gen_csr_trap_handling_warl_cg.cp_op.csrrci
        gen_csr_trap_handling_warl_cg.cp_op.csrrs
        gen_csr_trap_handling_warl_cg.cp_op.csrrsi
        gen_csr_trap_handling_warl_cg.cp_op.csrrw
        gen_csr_trap_handling_warl_cg.cp_op.csrrwi
        gen_csr_trap_handling_warl_cg.cp_wpat.all0
        gen_csr_trap_handling_warl_cg.cr_csr_op.mscratch_csrrc
        gen_csr_trap_handling_warl_cg.cr_csr_op.mscratch_csrrci
        gen_csr_trap_handling_warl_cg.cr_csr_op.mscratch_csrrs
        gen_csr_trap_handling_warl_cg.cr_csr_op.mscratch_csrrsi
        gen_csr_trap_handling_warl_cg.cr_csr_op.mscratch_csrrw
        gen_csr_trap_handling_warl_cg.cr_csr_op.mscratch_csrrwi
        gen_csr_trap_handling_warl_cg.cr_csr_op.mtval_csrrc
        gen_csr_trap_handling_warl_cg.cr_csr_op.mtval_csrrs
        gen_csr_trap_handling_warl_cg.cr_csr_op.mtval_csrrw
        gen_csr_trap_handling_warl_cg.cr_csr_wpat.mscratch_all0
        gen_csr_trap_handling_warl_cg.cr_csr_wpat.mtval_all0
        gen_csr_write_effect_cg.cp_fam.other_flush
        gen_csr_write_effect_cg.cp_op.csrrw
        gen_csr_write_effect_cg.cp_op.csrrwi
        gen_csr_write_effect_cg.cr_fam_op.other_csrrw
        gen_csr_write_effect_cg.cr_fam_op.other_csrrwi

### gen_test_csr_reset (measured): 68 of 68 declared bins, 6 covergroups
    gen_csr_reset_read_cg (CG-CSR-016, gen_fcov_plan.md:1534): 56 bins
    gen_csr_trigger_csr_cg (CG-CSR-008, gen_fcov_plan.md:1363): 4 bins
    gen_prv_trap_vector_cg (CG-PRV-008, gen_fcov_plan.md:1712): 3 bins
    gen_csr_cpuctrlsts_cg (CG-CSR-009, gen_fcov_plan.md:1387): 2 bins
    gen_csr_pmp_warl_cg (CG-CSR-011, gen_fcov_plan.md:1445): 2 bins
    gen_csr_secureseed_cg (CG-CSR-010, gen_fcov_plan.md:1422): 1 bins
    bins:
        gen_csr_cpuctrlsts_cg.cp_key_pin.hi
        gen_csr_cpuctrlsts_cg.cp_key_pin.lo
        gen_csr_pmp_warl_cg.cp_fam.addr
        gen_csr_pmp_warl_cg.cp_fam.cfg
        gen_csr_reset_read_cg.cp_boot_lo.nonzero
        gen_csr_reset_read_cg.cp_boot_lo.zero
        gen_csr_reset_read_cg.cp_csr.cpuctrlsts
        gen_csr_reset_read_cg.cp_csr.cycle_alias
        gen_csr_reset_read_cg.cp_csr.hpm
        gen_csr_reset_read_cg.cp_csr.hpm_alias
        gen_csr_reset_read_cg.cp_csr.hpm_unimpl
        gen_csr_reset_read_cg.cp_csr.hpmh
        gen_csr_reset_read_cg.cp_csr.instret_alias
        gen_csr_reset_read_cg.cp_csr.marchid
        gen_csr_reset_read_cg.cp_csr.mcause
        gen_csr_reset_read_cg.cp_csr.mconfigptr
        gen_csr_reset_read_cg.cp_csr.mcounteren
        gen_csr_reset_read_cg.cp_csr.mcountinhibit
        gen_csr_reset_read_cg.cp_csr.mcycle
        gen_csr_reset_read_cg.cp_csr.mcycleh
        gen_csr_reset_read_cg.cp_csr.menvcfg
        gen_csr_reset_read_cg.cp_csr.menvcfgh
        gen_csr_reset_read_cg.cp_csr.mepc
        gen_csr_reset_read_cg.cp_csr.mhartid
        gen_csr_reset_read_cg.cp_csr.mhpmevent
        gen_csr_reset_read_cg.cp_csr.mhpmevent_unimpl
        gen_csr_reset_read_cg.cp_csr.mie
        gen_csr_reset_read_cg.cp_csr.mimpid
        gen_csr_reset_read_cg.cp_csr.minstret
        gen_csr_reset_read_cg.cp_csr.minstreth
        gen_csr_reset_read_cg.cp_csr.mip
        gen_csr_reset_read_cg.cp_csr.misa
        gen_csr_reset_read_cg.cp_csr.mscratch
        gen_csr_reset_read_cg.cp_csr.mseccfg
        gen_csr_reset_read_cg.cp_csr.mseccfgh
        gen_csr_reset_read_cg.cp_csr.mstatus
        gen_csr_reset_read_cg.cp_csr.mstatush
        gen_csr_reset_read_cg.cp_csr.mtval
        gen_csr_reset_read_cg.cp_csr.mtvec
        gen_csr_reset_read_cg.cp_csr.mvendorid
        gen_csr_reset_read_cg.cp_csr.pmpaddr
        gen_csr_reset_read_cg.cp_csr.pmpcfg
        gen_csr_reset_read_cg.cp_csr.secureseed
        gen_csr_reset_read_cg.cp_csr.tdata1
        gen_csr_reset_read_cg.cp_csr.tdata2
        gen_csr_reset_read_cg.cp_csr.tselect
        gen_csr_reset_read_cg.cp_dbg.nondbg
        gen_csr_reset_read_cg.cp_when.early
        gen_csr_reset_read_cg.cp_when.first_insn
        gen_csr_reset_read_cg.cp_when.later
        gen_csr_reset_read_cg.cr_first_csr.cpuctrlsts_first
        gen_csr_reset_read_cg.cr_first_csr.mcycle_first
        gen_csr_reset_read_cg.cr_first_csr.mie_first
        gen_csr_reset_read_cg.cr_first_csr.minstret_first
        gen_csr_reset_read_cg.cr_first_csr.misa_first
        gen_csr_reset_read_cg.cr_first_csr.mstatus_first
        gen_csr_reset_read_cg.cr_mtvec_first.mtvec_early_nonzero
        gen_csr_reset_read_cg.cr_mtvec_first.mtvec_early_zero
        gen_csr_reset_read_cg.cr_mtvec_first.mtvec_first_nonzero
        gen_csr_reset_read_cg.cr_mtvec_first.mtvec_first_zero
        gen_csr_secureseed_cg.cr_form_priv_trap.rd_m_ok
        gen_csr_trigger_csr_cg.cp_csr.tdata1
        gen_csr_trigger_csr_cg.cp_dbg.nondbg
        gen_csr_trigger_csr_cg.cp_form.rd_only
        gen_csr_trigger_csr_cg.cr_csr_dbg_form.tdata1_nondbg_rd
        gen_prv_trap_vector_cg.cp_base.boot_page
        gen_prv_trap_vector_cg.cp_cause.exc
        gen_prv_trap_vector_cg.cr_base_cause.boot_exc

### gen_test_csr_trap_setup (measured): 17 of 168 declared bins, 3 covergroups
    gen_prv_transition_cg (CG-PRV-001, gen_fcov_plan.md:1571): 9 bins
    gen_prv_trap_vector_cg (CG-PRV-008, gen_fcov_plan.md:1712): 5 bins
    gen_csr_reset_read_cg (CG-CSR-016, gen_fcov_plan.md:1534): 3 bins
    bins:
        gen_csr_reset_read_cg.cp_csr.menvcfg
        gen_csr_reset_read_cg.cp_csr.menvcfgh
        gen_csr_reset_read_cg.cp_csr.mstatush
        gen_prv_transition_cg.cp_from.m
        gen_prv_transition_cg.cp_from.u
        gen_prv_transition_cg.cp_to.m
        gen_prv_transition_cg.cp_to.u
        gen_prv_transition_cg.cp_via.ecall
        gen_prv_transition_cg.cp_via.mret
        gen_prv_transition_cg.cr_trans.m_m_mret
        gen_prv_transition_cg.cr_trans.m_u_mret
        gen_prv_transition_cg.cr_trans.u_m_ecall
        gen_prv_trap_vector_cg.cp_base.sw_high
        gen_prv_trap_vector_cg.cp_base.sw_low
        gen_prv_trap_vector_cg.cp_cause.exc
        gen_prv_trap_vector_cg.cr_base_cause.high_exc
        gen_prv_trap_vector_cg.cr_base_cause.low_exc

### gen_test_pmp_csr_warl (measured): 266 of 266 declared bins, 5 covergroups
    gen_pmp_cfg_write_cg (CG-PMP-001, gen_fcov_plan.md:2420): 117 bins
    gen_pmp_addr_write_cg (CG-PMP-002, gen_fcov_plan.md:2446): 92 bins
    gen_pmp_csr_access_cg (CG-PMP-004, gen_fcov_plan.md:2493): 51 bins
    gen_pmp_access_verdict_cg (CG-PMP-005, gen_fcov_plan.md:2512): 3 bins
    gen_pmp_mseccfg_cg (CG-PMP-003, gen_fcov_plan.md:2466): 3 bins
    bins:
        gen_pmp_access_verdict_cg.cp_mode.na4
        gen_pmp_access_verdict_cg.cp_mode.napot
        gen_pmp_access_verdict_cg.cp_mode.tor
        gen_pmp_addr_write_cg.cp_hi_bits.bit30
        gen_pmp_addr_write_cg.cp_hi_bits.bit31
        gen_pmp_addr_write_cg.cp_hi_bits.both
        gen_pmp_addr_write_cg.cp_hi_bits.none
        gen_pmp_addr_write_cg.cp_idx.a0
        gen_pmp_addr_write_cg.cp_idx.a1
        gen_pmp_addr_write_cg.cp_idx.a10
        gen_pmp_addr_write_cg.cp_idx.a11
        gen_pmp_addr_write_cg.cp_idx.a12
        gen_pmp_addr_write_cg.cp_idx.a13
        gen_pmp_addr_write_cg.cp_idx.a14
        gen_pmp_addr_write_cg.cp_idx.a15
        gen_pmp_addr_write_cg.cp_idx.a2
        gen_pmp_addr_write_cg.cp_idx.a3
        gen_pmp_addr_write_cg.cp_idx.a4
        gen_pmp_addr_write_cg.cp_idx.a5
        gen_pmp_addr_write_cg.cp_idx.a6
        gen_pmp_addr_write_cg.cp_idx.a7
        gen_pmp_addr_write_cg.cp_idx.a8
        gen_pmp_addr_write_cg.cp_idx.a9
        gen_pmp_addr_write_cg.cp_next_cfg.next_unlocked_other
        gen_pmp_addr_write_cg.cp_op.csrrc
        gen_pmp_addr_write_cg.cp_op.csrrs
        gen_pmp_addr_write_cg.cp_op.csrrw
        gen_pmp_addr_write_cg.cp_outcome.written
        gen_pmp_addr_write_cg.cp_rlb.rlb0
        gen_pmp_addr_write_cg.cp_self_lock.unlocked
        gen_pmp_addr_write_cg.cp_self_mode.na4
        gen_pmp_addr_write_cg.cp_self_mode.napot
        gen_pmp_addr_write_cg.cp_self_mode.off
        gen_pmp_addr_write_cg.cp_self_mode.tor
        gen_pmp_addr_write_cg.cr_hi_mode.bit30_na4
        gen_pmp_addr_write_cg.cr_hi_mode.bit30_napot
        gen_pmp_addr_write_cg.cr_hi_mode.bit30_off
        gen_pmp_addr_write_cg.cr_hi_mode.bit30_tor
        gen_pmp_addr_write_cg.cr_hi_mode.bit31_na4
        gen_pmp_addr_write_cg.cr_hi_mode.bit31_napot
        gen_pmp_addr_write_cg.cr_hi_mode.bit31_off
        gen_pmp_addr_write_cg.cr_hi_mode.bit31_tor
        gen_pmp_addr_write_cg.cr_hi_mode.both_na4
        gen_pmp_addr_write_cg.cr_hi_mode.both_napot
        gen_pmp_addr_write_cg.cr_hi_mode.both_off
        gen_pmp_addr_write_cg.cr_hi_mode.both_tor
        gen_pmp_addr_write_cg.cr_idx_op.a0_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a0_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a0_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a10_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a10_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a10_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a11_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a11_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a11_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a12_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a12_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a12_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a13_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a13_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a13_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a14_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a14_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a14_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a15_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a15_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a15_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a1_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a1_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a1_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a2_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a2_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a2_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a3_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a3_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a3_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a4_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a4_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a4_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a5_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a5_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a5_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a6_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a6_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a6_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a7_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a7_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a7_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a8_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a8_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a8_csrrw
        gen_pmp_addr_write_cg.cr_idx_op.a9_csrrc
        gen_pmp_addr_write_cg.cr_idx_op.a9_csrrs
        gen_pmp_addr_write_cg.cr_idx_op.a9_csrrw
        gen_pmp_addr_write_cg.cr_self_lock.unlocked_rlb0_written
        gen_pmp_cfg_write_cg.cp_entry.e0
        gen_pmp_cfg_write_cg.cp_entry.e1
        gen_pmp_cfg_write_cg.cp_entry.e10
        gen_pmp_cfg_write_cg.cp_entry.e11
        gen_pmp_cfg_write_cg.cp_entry.e12
        gen_pmp_cfg_write_cg.cp_entry.e13
        gen_pmp_cfg_write_cg.cp_entry.e14
        gen_pmp_cfg_write_cg.cp_entry.e15
        gen_pmp_cfg_write_cg.cp_entry.e2
        gen_pmp_cfg_write_cg.cp_entry.e3
        gen_pmp_cfg_write_cg.cp_entry.e4
        gen_pmp_cfg_write_cg.cp_entry.e5
        gen_pmp_cfg_write_cg.cp_entry.e6
        gen_pmp_cfg_write_cg.cp_entry.e7
        gen_pmp_cfg_write_cg.cp_entry.e8
        gen_pmp_cfg_write_cg.cp_entry.e9
        gen_pmp_cfg_write_cg.cp_mml.mml0
        gen_pmp_cfg_write_cg.cp_mml.mml1
        gen_pmp_cfg_write_cg.cp_op.csrrc
        gen_pmp_cfg_write_cg.cp_op.csrrs
        gen_pmp_cfg_write_cg.cp_op.csrrw
        gen_pmp_cfg_write_cg.cp_outcome.w_dropped
        gen_pmp_cfg_write_cg.cp_outcome.written
        gen_pmp_cfg_write_cg.cp_prelock.unlocked
        gen_pmp_cfg_write_cg.cp_res_bits.nonzero
        gen_pmp_cfg_write_cg.cp_res_bits.zero
        gen_pmp_cfg_write_cg.cp_rlb.rlb0
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c0000
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c0001
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c0010
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c0011
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c0100
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c0101
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c0110
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c0111
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c1000
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c1001
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c1010
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c1011
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c1100
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c1101
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c1110
        gen_pmp_cfg_write_cg.cp_wr_lrwx.c1111
        gen_pmp_cfg_write_cg.cp_wr_mode.na4
        gen_pmp_cfg_write_cg.cp_wr_mode.napot
        gen_pmp_cfg_write_cg.cp_wr_mode.off
        gen_pmp_cfg_write_cg.cp_wr_mode.tor
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c0000
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c0001
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c0010
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c0011
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c0100
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c0101
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c0110
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c0111
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c1000
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c1001
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c1010
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c1011
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c1100
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c1101
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c1110
        gen_pmp_cfg_write_cg.cr_mode_lrwx.na4_c1111
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c0000
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c0001
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c0010
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c0011
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c0100
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c0101
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c0110
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c0111
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c1000
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c1001
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c1010
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c1011
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c1100
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c1101
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c1110
        gen_pmp_cfg_write_cg.cr_mode_lrwx.napot_c1111
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c0000
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c0001
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c0010
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c0011
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c0100
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c0101
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c0110
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c0111
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c1000
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c1001
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c1010
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c1011
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c1100
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c1101
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c1110
        gen_pmp_cfg_write_cg.cr_mode_lrwx.off_c1111
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c0000
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c0001
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c0010
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c0011
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c0100
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c0101
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c0110
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c0111
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c1000
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c1001
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c1010
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c1011
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c1100
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c1101
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c1110
        gen_pmp_cfg_write_cg.cr_mode_lrwx.tor_c1111
        gen_pmp_cfg_write_cg.cr_res_op.nonzero_csrrc
        gen_pmp_cfg_write_cg.cr_res_op.nonzero_csrrs
        gen_pmp_cfg_write_cg.cr_res_op.nonzero_csrrw
        gen_pmp_cfg_write_cg.cr_rw01_mml.rw01_mml0_wdrop
        gen_pmp_cfg_write_cg.cr_rw01_mml.rw01_mml1_l1_rlb1_stored
        gen_pmp_cfg_write_cg.cr_rw01_mml.rw01_mml1_stored
        gen_pmp_csr_access_cg.cp_class.mseccfg
        gen_pmp_csr_access_cg.cp_class.mseccfgh
        gen_pmp_csr_access_cg.cp_class.pmpaddr
        gen_pmp_csr_access_cg.cp_class.pmpcfg
        gen_pmp_csr_access_cg.cp_dbg.d0
        gen_pmp_csr_access_cg.cp_op.csrrc
        gen_pmp_csr_access_cg.cp_op.csrrci
        gen_pmp_csr_access_cg.cp_op.csrrs
        gen_pmp_csr_access_cg.cp_op.csrrsi
        gen_pmp_csr_access_cg.cp_op.csrrw
        gen_pmp_csr_access_cg.cp_op.csrrwi
        gen_pmp_csr_access_cg.cp_priv.m
        gen_pmp_csr_access_cg.cp_priv.u
        gen_pmp_csr_access_cg.cp_rw.read_only
        gen_pmp_csr_access_cg.cp_rw.write
        gen_pmp_csr_access_cg.cp_trap.illegal
        gen_pmp_csr_access_cg.cp_trap.none
        gen_pmp_csr_access_cg.cr_op_class.csrrc_mseccfg
        gen_pmp_csr_access_cg.cr_op_class.csrrc_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrc_pmpaddr
        gen_pmp_csr_access_cg.cr_op_class.csrrc_pmpcfg
        gen_pmp_csr_access_cg.cr_op_class.csrrci_mseccfg
        gen_pmp_csr_access_cg.cr_op_class.csrrci_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrci_pmpaddr
        gen_pmp_csr_access_cg.cr_op_class.csrrci_pmpcfg
        gen_pmp_csr_access_cg.cr_op_class.csrrs_mseccfg
        gen_pmp_csr_access_cg.cr_op_class.csrrs_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrs_pmpaddr
        gen_pmp_csr_access_cg.cr_op_class.csrrs_pmpcfg
        gen_pmp_csr_access_cg.cr_op_class.csrrsi_mseccfg
        gen_pmp_csr_access_cg.cr_op_class.csrrsi_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrsi_pmpaddr
        gen_pmp_csr_access_cg.cr_op_class.csrrsi_pmpcfg
        gen_pmp_csr_access_cg.cr_op_class.csrrw_mseccfg
        gen_pmp_csr_access_cg.cr_op_class.csrrw_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrw_pmpaddr
        gen_pmp_csr_access_cg.cr_op_class.csrrw_pmpcfg
        gen_pmp_csr_access_cg.cr_op_class.csrrwi_mseccfg
        gen_pmp_csr_access_cg.cr_op_class.csrrwi_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrwi_pmpaddr
        gen_pmp_csr_access_cg.cr_op_class.csrrwi_pmpcfg
        gen_pmp_csr_access_cg.cr_priv_trap.m_none
        gen_pmp_csr_access_cg.cr_priv_trap.u_illegal
        gen_pmp_csr_access_cg.cr_u_class.u_mseccfg_read_only
        gen_pmp_csr_access_cg.cr_u_class.u_mseccfg_write
        gen_pmp_csr_access_cg.cr_u_class.u_mseccfgh_read_only
        gen_pmp_csr_access_cg.cr_u_class.u_mseccfgh_write
        gen_pmp_csr_access_cg.cr_u_class.u_pmpaddr_read_only
        gen_pmp_csr_access_cg.cr_u_class.u_pmpaddr_write
        gen_pmp_csr_access_cg.cr_u_class.u_pmpcfg_read_only
        gen_pmp_csr_access_cg.cr_u_class.u_pmpcfg_write
        gen_pmp_mseccfg_cg.cp_op.csrrc
        gen_pmp_mseccfg_cg.cp_op.csrrs
        gen_pmp_mseccfg_cg.cp_op.csrrw

### gen_test_pmp_lock (unmeasured targeted): 50 of 50 declared bins, 4 covergroups
    gen_pmp_addr_write_cg (CG-PMP-002, gen_fcov_plan.md:2446): 21 bins
    gen_pmp_cfg_write_cg (CG-PMP-001, gen_fcov_plan.md:2420): 20 bins
    gen_pmp_mseccfg_cg (CG-PMP-003, gen_fcov_plan.md:2466): 5 bins
    gen_pmp_recfg_cg (CG-PMP-011, gen_fcov_plan.md:2654): 4 bins
    bins:
        gen_pmp_addr_write_cg.cp_next_cfg.next_locked_other
        gen_pmp_addr_write_cg.cp_next_cfg.next_locked_tor
        gen_pmp_addr_write_cg.cp_next_cfg.next_unlocked_tor
        gen_pmp_addr_write_cg.cp_next_cfg.top
        gen_pmp_addr_write_cg.cp_outcome.ignored_self_lock
        gen_pmp_addr_write_cg.cp_outcome.ignored_tor_lock
        gen_pmp_addr_write_cg.cp_rlb.rlb1
        gen_pmp_addr_write_cg.cp_self_lock.locked
        gen_pmp_addr_write_cg.cp_self_mode.na4
        gen_pmp_addr_write_cg.cp_self_mode.napot
        gen_pmp_addr_write_cg.cp_self_mode.off
        gen_pmp_addr_write_cg.cp_self_mode.tor
        gen_pmp_addr_write_cg.cr_self_lock.locked_rlb0_ignored
        gen_pmp_addr_write_cg.cr_self_lock.locked_rlb1_written
        gen_pmp_addr_write_cg.cr_top_lock.top_locked_ignored
        gen_pmp_addr_write_cg.cr_top_lock.top_unlocked_written
        gen_pmp_addr_write_cg.cr_tor_lock.nl_other_rlb0_written
        gen_pmp_addr_write_cg.cr_tor_lock.nl_tor_rlb0_ignored
        gen_pmp_addr_write_cg.cr_tor_lock.nl_tor_rlb1_written
        gen_pmp_addr_write_cg.cr_tor_lock.nu_tor_rlb0_written
        gen_pmp_addr_write_cg.cr_tor_lock.top_rlb0_written
        gen_pmp_cfg_write_cg.cp_outcome.ignored_lock
        gen_pmp_cfg_write_cg.cp_prelock.locked
        gen_pmp_cfg_write_cg.cp_rlb.rlb1
        gen_pmp_cfg_write_cg.cp_word_lockmix.all
        gen_pmp_cfg_write_cg.cp_word_lockmix.none
        gen_pmp_cfg_write_cg.cp_word_lockmix.some
        gen_pmp_cfg_write_cg.cp_wr_mode.off
        gen_pmp_cfg_write_cg.cr_lock_outcome.locked_rlb0_ignored
        gen_pmp_cfg_write_cg.cr_lock_outcome.locked_rlb1_written
        gen_pmp_cfg_write_cg.cr_lock_outcome.unlocked_rlb0_written
        gen_pmp_cfg_write_cg.cr_lock_outcome.unlocked_rlb1_written
        gen_pmp_cfg_write_cg.cr_lockmix_op.some_csrrc
        gen_pmp_cfg_write_cg.cr_lockmix_op.some_csrrs
        gen_pmp_cfg_write_cg.cr_lockmix_op.some_csrrw
        gen_pmp_cfg_write_cg.cr_prelock_wrl.setlock_c1000
        gen_pmp_cfg_write_cg.cr_prelock_wrl.setlock_c1001
        gen_pmp_cfg_write_cg.cr_prelock_wrl.setlock_c1100
        gen_pmp_cfg_write_cg.cr_prelock_wrl.setlock_c1101
        gen_pmp_cfg_write_cg.cr_prelock_wrl.setlock_c1110
        gen_pmp_cfg_write_cg.cr_prelock_wrl.setlock_c1111
        gen_pmp_mseccfg_cg.cp_locked_off_only.yes
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_0_w1_locked_blocked
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_0_w1_lockedoff_blocked
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_1_w0_clear
        gen_pmp_mseccfg_cg.cr_state_trans.s001_to_s000
        gen_pmp_recfg_cg.cp_bb.lock_then_addr
        gen_pmp_recfg_cg.cp_bb.lock_then_cfg
        gen_pmp_recfg_cg.cp_bb.lock_then_rlb
        gen_pmp_recfg_cg.cp_bb.rlbclr_then_cfg

### gen_test_pmp_mseccfg (unmeasured targeted): 77 of 77 declared bins, 5 covergroups
    gen_pmp_mseccfg_cg (CG-PMP-003, gen_fcov_plan.md:2466): 46 bins
    gen_pmp_cfg_write_cg (CG-PMP-001, gen_fcov_plan.md:2420): 19 bins
    gen_pmp_csr_access_cg (CG-PMP-004, gen_fcov_plan.md:2493): 7 bins
    gen_pmp_access_verdict_cg (CG-PMP-005, gen_fcov_plan.md:2512): 4 bins
    gen_pmp_recfg_cg (CG-PMP-011, gen_fcov_plan.md:2654): 1 bins
    bins:
        gen_pmp_access_verdict_cg.cr_truth_mml0.c0111_m_load
        gen_pmp_access_verdict_cg.cr_truth_mml0.c1110_u_load
        gen_pmp_access_verdict_cg.cr_truth_mml1.c0111_m_load
        gen_pmp_access_verdict_cg.cr_truth_mml1.c1110_u_load
        gen_pmp_cfg_write_cg.cp_outcome.ignored_mml_exec
        gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb0_c1001_suppressed
        gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb0_c1010_suppressed
        gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb0_c1011_suppressed
        gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb0_c1101_suppressed
        gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb1_c1001_written
        gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb1_c1010_written
        gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb1_c1011_written
        gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb1_c1101_written
        gen_pmp_cfg_write_cg.cr_mml_nonexec_accept.c1000_written
        gen_pmp_cfg_write_cg.cr_mml_nonexec_accept.c1100_written
        gen_pmp_cfg_write_cg.cr_mml_nonexec_accept.c1110_written
        gen_pmp_cfg_write_cg.cr_mml_nonexec_accept.c1111_written
        gen_pmp_cfg_write_cg.cr_rw01_mml.rw01_mml1_l1_rlb0_suppressed
        gen_pmp_cfg_write_cg.cr_rw01_mml.rw01_mml1_l1_rlb1_stored
        gen_pmp_cfg_write_cg.cr_suppress_mode.na4
        gen_pmp_cfg_write_cg.cr_suppress_mode.napot
        gen_pmp_cfg_write_cg.cr_suppress_mode.off
        gen_pmp_cfg_write_cg.cr_suppress_mode.tor
        gen_pmp_csr_access_cg.cr_op_class.csrrc_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrci_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrs_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrsi_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrw_mseccfg
        gen_pmp_csr_access_cg.cr_op_class.csrrw_mseccfgh
        gen_pmp_csr_access_cg.cr_op_class.csrrwi_mseccfgh
        gen_pmp_mseccfg_cg.cp_any_locked.none
        gen_pmp_mseccfg_cg.cp_any_locked.some
        gen_pmp_mseccfg_cg.cp_csr.mseccfg
        gen_pmp_mseccfg_cg.cp_csr.mseccfgh
        gen_pmp_mseccfg_cg.cp_hi_bits.nonzero
        gen_pmp_mseccfg_cg.cp_hi_bits.zero
        gen_pmp_mseccfg_cg.cp_locked_off_only.no
        gen_pmp_mseccfg_cg.cp_post.s000
        gen_pmp_mseccfg_cg.cp_post.s001
        gen_pmp_mseccfg_cg.cp_pre_mml.p0
        gen_pmp_mseccfg_cg.cp_pre_mml.p1
        gen_pmp_mseccfg_cg.cp_pre_mmwp.p0
        gen_pmp_mseccfg_cg.cp_pre_mmwp.p1
        gen_pmp_mseccfg_cg.cp_pre_rlb.p0
        gen_pmp_mseccfg_cg.cp_pre_rlb.p1
        gen_pmp_mseccfg_cg.cp_wr_mml.w0
        gen_pmp_mseccfg_cg.cp_wr_mml.w1
        gen_pmp_mseccfg_cg.cp_wr_mmwp.w0
        gen_pmp_mseccfg_cg.cp_wr_mmwp.w1
        gen_pmp_mseccfg_cg.cp_wr_rlb.w0
        gen_pmp_mseccfg_cg.cp_wr_rlb.w1
        gen_pmp_mseccfg_cg.cr_hi_bits.mseccfg_hi_nonzero
        gen_pmp_mseccfg_cg.cr_mml_trans.mml_0_w0_stay0
        gen_pmp_mseccfg_cg.cr_mml_trans.mml_0_w1_set
        gen_pmp_mseccfg_cg.cr_mml_trans.mml_1_w0_hold
        gen_pmp_mseccfg_cg.cr_mml_trans.mml_1_w1_hold
        gen_pmp_mseccfg_cg.cr_mmwp_trans.mmwp_0_w0_stay0
        gen_pmp_mseccfg_cg.cr_mmwp_trans.mmwp_0_w1_set
        gen_pmp_mseccfg_cg.cr_mmwp_trans.mmwp_1_w0_hold
        gen_pmp_mseccfg_cg.cr_mmwp_trans.mmwp_1_w1_hold
        gen_pmp_mseccfg_cg.cr_mseccfgh.mseccfgh_nonzero_csrrc
        gen_pmp_mseccfg_cg.cr_mseccfgh.mseccfgh_nonzero_csrrs
        gen_pmp_mseccfg_cg.cr_mseccfgh.mseccfgh_nonzero_csrrw
        gen_pmp_mseccfg_cg.cr_op_trans.csrrc_mml_hold
        gen_pmp_mseccfg_cg.cr_op_trans.csrrc_mmwp_hold
        gen_pmp_mseccfg_cg.cr_op_trans.csrrw_mml_hold
        gen_pmp_mseccfg_cg.cr_op_trans.csrrw_mmwp_hold
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_0_w0_locked_stay
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_0_w0_nolock_stay
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_0_w1_locked_blocked
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_0_w1_nolock_set
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_1_w0_clear
        gen_pmp_mseccfg_cg.cr_rlb_trans.rlb_1_w1_hold
        gen_pmp_mseccfg_cg.cr_state_trans.s000_to_s000
        gen_pmp_mseccfg_cg.cr_state_trans.s000_to_s001
        gen_pmp_mseccfg_cg.cr_state_trans.s001_to_s000
        gen_pmp_recfg_cg.cr_csr_data.mseccfg_mml_now_denied

## Class B: built, hit at some round-1 seeds and not others

Reason to use, per bin:

    "not guaranteed per run: hit at some round-1 seeds and not others; credited from the merged report"

## Class C: built, hit at NO round-1 seed - triage owed, not a granularity question

Reason shape, per bin: state WHICH of the two it is, in these words plus the specifics:

    "stimulus gap: <what the program never emits>"   or   "declaration defect: <why the bin cannot apply>"

### gen_test_cmp_zcb: class B 8, class C 6 (union 14)
    class B bins:
        gen_mul_ops_cg.cp_rs1_class.all_ones
        gen_mul_ops_cg.cp_rs1_class.int_max
        gen_mul_ops_cg.cp_rs1_class.int_min
        gen_mul_ops_cg.cp_rs1_class.zero
        gen_mul_ops_cg.cr_op_rs1.c_mul_all_ones
        gen_mul_ops_cg.cr_op_rs1.c_mul_int_max
        gen_mul_ops_cg.cr_op_rs1.c_mul_int_min
        gen_mul_ops_cg.cr_op_rs1.c_mul_zero
    class C bins:
        gen_cmp_zcb_cg.cp_alu_operand.rand
        gen_cmp_zcb_cg.cr_alu_operand.c_not_rand
        gen_cmp_zcb_cg.cr_alu_operand.c_sext_b_rand
        gen_cmp_zcb_cg.cr_alu_operand.c_sext_h_rand
        gen_cmp_zcb_cg.cr_alu_operand.c_zext_b_rand
        gen_cmp_zcb_cg.cr_alu_operand.c_zext_h_rand

### gen_test_cmp_zcmp_basic: class B 73, class C 74 (union 147)
    class B bins:
        gen_cmp_zcmp_hazard_cg.cp_hazard.popret_ra_deferred
        gen_cmp_zcmp_hazard_cg.cp_rlist_class.r15
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_mva01s
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_mvsa01
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_popret
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_popretz
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_mva01s
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_mvsa01
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_popret
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_popretz
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_pushed_reg_then_push_long
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_pushed_reg_then_push_min1
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_then_mva01s_min1
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_then_mva01s_short
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.popret_ra_deferred_long
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.popret_ra_deferred_short
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.store_same_slot_then_pop_min1
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.store_same_slot_then_pop_short
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.write_pushed_reg_then_push_long
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.write_pushed_reg_then_push_min1
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_pop_long
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_pop_min1
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_pop_mixed
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_pop_short
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popret_long
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popret_min1
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popret_mixed
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popret_short
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popretz_long
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popretz_min1
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popretz_mixed
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_push_long
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_push_min1
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_push_mixed
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_push_short
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r10_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r10_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r10_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r12_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r12_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r13_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r13_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r14_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r15_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r4_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r4_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r5_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r6_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r6_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r7_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r7_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r7_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r8_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r9_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r11_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r11_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r11_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r12_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r13_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r13_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r14_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r14_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r15_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r4_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r4_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r4_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r5_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r5_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r6_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r8_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r8_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r8_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r9_s0
    class C bins:
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_pop
        gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_push
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_pushed_reg_then_push_short
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_then_mva01s_long
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.store_same_slot_then_pop_long
        gen_cmp_zcmp_hazard_cg.cr_hazard_delay.write_pushed_reg_then_push_short
        gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.load_pushed_reg_then_push_r15
        gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.load_pushed_reg_then_push_r4
        gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.store_same_slot_then_pop_r15
        gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.store_same_slot_then_pop_r4
        gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.write_pushed_reg_then_push_r15
        gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.write_pushed_reg_then_push_r4
        gen_cmp_zcmp_mv_cg.cr_insn_hazard.cm_mvsa01_load_prev
        gen_cmp_zcmp_pushpop_cg.cp_ret_align.odd
        gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popretz_short
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r10_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r11_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r11_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r11_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r11_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r12_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r12_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r13_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r13_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r14_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r14_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r14_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r15_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r15_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r15_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r4_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r5_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r5_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r5_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r6_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r6_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r7_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r8_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r8_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r8_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r9_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r9_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r9_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r10_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r10_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r10_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r10_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r11_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r12_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r12_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r12_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r13_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r13_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r14_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r14_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r15_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r15_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r15_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r4_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r5_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r5_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r6_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r6_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r6_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r7_s0
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r7_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r7_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r7_s3
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r8_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r9_s1
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r9_s2
        gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r9_s3
        gen_cmp_zcmp_pushpop_cg.cr_ret_align.cm_popret_odd
        gen_cmp_zcmp_pushpop_cg.cr_ret_align.cm_popretz_odd

### gen_test_isa_alu: class B 33, class C 6 (union 39)
    class B bins:
        gen_isa_alu_reg_cg.cr_slt_boundary.slt_all_ones_int_max
        gen_isa_alu_reg_cg.cr_slt_boundary.slt_int_max_all_ones
        gen_isa_alu_reg_cg.cr_slt_boundary.slt_int_min_zero
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_all_ones_int_max
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_all_ones_int_min
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_all_ones_zero
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_int_max_one
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_int_min_all_ones
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_one_int_max
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_one_int_min
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_one_zero
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_zero_int_max
        gen_isa_alu_reg_cg.cr_slt_boundary.sltu_zero_int_min
        gen_isa_hint_x0_cg.cr_writer_read.bit_1cyc_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.bit_2cyc_none
        gen_isa_hint_x0_cg.cr_writer_read.bit_2cyc_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.bit_2cyc_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.cmp_hint_none
        gen_isa_hint_x0_cg.cr_writer_read.cmp_hint_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.cmp_hint_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.csrr_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.div_rem_none
        gen_isa_hint_x0_cg.cr_writer_read.div_rem_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.jal_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.jalr_none
        gen_isa_hint_x0_cg.cr_writer_read.jalr_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.jalr_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.load_none
        gen_isa_hint_x0_cg.cr_writer_read.load_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.load_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.mul_none
        gen_isa_hint_x0_cg.cr_writer_read.mul_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.shift_rs2_zero
    class C bins:
        gen_isa_hint_x0_cg.cr_writer_read.bit_1cyc_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.div_rem_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.jal_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.mul_rs2_zero
        gen_isa_hint_x0_cg.cr_writer_read.mulh_rs1_zero
        gen_isa_hint_x0_cg.cr_writer_read.mulh_rs2_zero

### gen_test_isa_cti: class B 0, class C 16 (union 16)
    class B bins:
        (none)
    class C bins:
        gen_isa_branch_cg.cp_op.c_beqz
        gen_isa_branch_cg.cp_op.c_bnez
        gen_isa_branch_cg.cr_op_align.c_beqz_half
        gen_isa_branch_cg.cr_op_align.c_bnez_half
        gen_isa_branch_cg.cr_op_taken_cmp.c_beqz_no_intmin_zero
        gen_isa_branch_cg.cr_op_taken_cmp.c_beqz_no_ones_zero
        gen_isa_branch_cg.cr_op_taken_cmp.c_beqz_no_slt_ugt
        gen_isa_branch_cg.cr_op_taken_cmp.c_beqz_yes_equal
        gen_isa_branch_cg.cr_op_taken_cmp.c_bnez_no_equal
        gen_isa_branch_cg.cr_op_taken_cmp.c_bnez_yes_intmin_zero
        gen_isa_branch_cg.cr_op_taken_cmp.c_bnez_yes_ones_zero
        gen_isa_branch_cg.cr_op_taken_cmp.c_bnez_yes_slt_ugt
        gen_isa_jump_cg.cp_jalr_rs1.x0
        gen_isa_jump_cg.cr_jalr_rs1_imm.x0_max_pos
        gen_isa_jump_cg.cr_jalr_rs1_imm.x0_min_neg
        gen_isa_jump_cg.cr_jalr_rs1_imm.x0_zero

### gen_test_mul_div: class B 9, class C 19 (union 28)
    class B bins:
        gen_div_ops_cg.cr_div0.div_zero_neg_rand
        gen_div_ops_cg.cr_div0.div_zero_pos_rand
        gen_div_ops_cg.cr_div0.divu_zero_neg_rand
        gen_div_ops_cg.cr_div0.divu_zero_pos_rand
        gen_div_ops_cg.cr_div0.rem_zero_neg_rand
        gen_div_ops_cg.cr_div0.rem_zero_pos_rand
        gen_div_ops_cg.cr_div0.remu_zero_neg_rand
        gen_div_ops_cg.cr_div0.remu_zero_pos_rand
        gen_div_ops_cg.cr_op_dividend.rem_two
    class C bins:
        gen_div_ops_cg.cr_div0.div_zero_seven
        gen_div_ops_cg.cr_div0.div_zero_two
        gen_div_ops_cg.cr_div0.divu_zero_seven
        gen_div_ops_cg.cr_div0.divu_zero_two
        gen_div_ops_cg.cr_div0.rem_zero_seven
        gen_div_ops_cg.cr_div0.rem_zero_two
        gen_div_ops_cg.cr_div0.remu_zero_seven
        gen_div_ops_cg.cr_div0.remu_zero_two
        gen_div_timing_cg.cp_dit.on
        gen_div_timing_cg.cr_op_div0.div_no_on
        gen_div_timing_cg.cr_op_div0.div_yes_on
        gen_div_timing_cg.cr_op_div0.divu_no_on
        gen_div_timing_cg.cr_op_div0.divu_yes_on
        gen_div_timing_cg.cr_op_div0.rem_no_on
        gen_div_timing_cg.cr_op_div0.rem_yes_on
        gen_div_timing_cg.cr_op_div0.remu_no_on
        gen_div_timing_cg.cr_op_div0.remu_yes_on
        gen_mul_ops_cg.cp_op.c_mul
        gen_mul_ops_cg.cr_op_rd_x0.c_mul_no

### gen_test_rst_boot: class B 0, class C 2 (union 2)
    class B bins:
        (none)
    class C bins:
        gen_rst_boot_cg.cp_boot_addr.zero
        gen_sec_ctrl_inputs_cg.cp_bit8_readback.zero

## Totals

    class A  758 bins over 7 measured and 2 unmeasured targeted entries
    class B  123 bins over 6 entries
    class C  123 bins over 6 entries
    class B + C = 246

A measured entry must keep a non-empty guaranteed set: the checker treats a manifest that declares no
bins as a cause and returns unverifiable rather than PASS (gen_fcov.py:330). Per-entry remainders:

    gen_test_bit_draft         declared   15 - excluded   15 =    0 guaranteed  <-- EMPTY, must not be measured
    gen_test_bit_ratified      declared  830 - excluded  176 =  654 guaranteed
    gen_test_cmp_zca           declared  337 - excluded   13 =  324 guaranteed
    gen_test_csr_access        declared   80 - excluded   76 =    4 guaranteed
    gen_test_csr_reset         declared   68 - excluded   68 =    0 guaranteed  <-- EMPTY, must not be measured
    gen_test_csr_trap_setup    declared  168 - excluded   17 =  151 guaranteed
    gen_test_pmp_csr_warl      declared  266 - excluded  266 =    0 guaranteed  <-- EMPTY, must not be measured
    gen_test_cmp_zcb           declared  110 - excluded   14 =   96 guaranteed
    gen_test_cmp_zcmp_basic    declared  472 - excluded  147 =  325 guaranteed
    gen_test_isa_alu           declared  602 - excluded   39 =  563 guaranteed
    gen_test_isa_cti           declared  200 - excluded   16 =  184 guaranteed
    gen_test_mul_div           declared  224 - excluded   28 =  196 guaranteed
    gen_test_rst_boot          declared    8 - excluded    2 =    6 guaranteed

## Addendum after the plan marks landed (v4w): what the marks change on the test side

Derived by running the manifest generator on an archive with the marks applied, not predicted.

### Stale bins_not_hit entries that MUST be deleted (13)

The marks take these bins out of the item-owned set, and gen_fcov_manifest.py:235 asserts that bins_not_hit
names only bins the items own, so the render fails until they go.

    gen_test_csr_reset.py
        gen_csr_reset_read_cg.cp_csr.dcsr
        gen_csr_reset_read_cg.cp_csr.dpc
        gen_csr_reset_read_cg.cp_csr.dscratch0
        gen_csr_reset_read_cg.cp_csr.dscratch1
        gen_csr_reset_read_cg.cp_dbg.dbg
    gen_test_csr_trap_setup.py
        gen_prv_trap_vector_cg.cp_cause.irq_fast
        gen_prv_trap_vector_cg.cp_cause.irq_sw
        gen_prv_trap_vector_cg.cr_base_cause.high_irq_fast
        gen_prv_trap_vector_cg.cr_base_cause.low_irq_sw
    gen_test_pmp_lock.py
        gen_pmp_mseccfg_cg.cr_state_trans.s011_to_s010
        gen_pmp_mseccfg_cg.cr_state_trans.s101_to_s100
        gen_pmp_mseccfg_cg.cr_state_trans.s111_to_s110
        gen_pmp_recfg_cg.cp_bb.rlbclr_then_addr

### Five entries whose manifest cannot be rendered at all

The generator refuses with "no manifest bins left": every bin their items own sits on an unbuilt covergroup.
Their manifest FILES have to go, or gen_test_lib.check_manifest_matches fails comparing a stale file against a
now-empty declare_bins(). Proven both ways in the archive.

    gen_test_bit_draft        0 owned bins   measured today -> measured false
    gen_test_csr_reset        8 owned, all excluded by its own bins_not_hit -> measured false
    gen_test_pmp_csr_warl     0 owned bins   measured today -> measured false
    gen_test_pmp_lock         0 owned bins   already unmeasured
    gen_test_pmp_mseccfg      0 owned bins   already unmeasured

### The ten entries to re-render, with the declared set each gets

    gen_test_bit_ratified     830 -> 654        gen_test_cmp_zcmp_basic   472 (unchanged)
    gen_test_cmp_zca          337 -> 324        gen_test_isa_alu          602 (unchanged)
    gen_test_csr_access        80 ->   4        gen_test_isa_cti          200 (unchanged)
    gen_test_csr_trap_setup   168 -> 151        gen_test_mul_div          224 (unchanged)
    gen_test_cmp_zcb          110 (unchanged)   gen_test_rst_boot           8 (unchanged)

The six of class B and C keep their declared sets from the marks' point of view; their reduction is the
bins_not_hit work above, not the marks.
