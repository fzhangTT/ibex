// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml; do not edit.
// Memory map, ISA string and TB constants for the Spike DPI shim (architecture C5.1, C11).
#ifndef GEN_ISA_SHIM_MAP_H
#define GEN_ISA_SHIM_MAP_H

#define GEN_ISA_STRING "rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zca_zcb_zcmp_zicntr_zihpm_zicclsm_smepmp"

#define GEN_MM_BOOT_ADDR_DEFAULT      0x80000000u
#define GEN_MM_BOOT_PAGE_MASK         0xffffff00u
#define GEN_MM_BOOT_RESET_OFFSET      0x00000080u
#define GEN_MM_BOOT_PAGE              0x80000000u
#define GEN_MM_PROG_SIZE              0x00100000u
#define GEN_MM_DM_BASE                0x1a110000u
#define GEN_MM_DM_SIZE                0x00001000u
#define GEN_MM_DM_HALT                0x1a110800u
#define GEN_MM_DM_EXCEPTION           0x1a110808u
#define GEN_MM_DM_BUDGET              0x00000800u
#define GEN_MM_MMIO_BASE              0x8ffff000u
#define GEN_MM_MMIO_SIZE              0x00001000u
#define GEN_MM_SIG_ADDR               0x8ffff000u
#define GEN_MM_SIG_SIZE               0x00000100u
#define GEN_MM_IRQ_ACK_ADDR           0x8ffff100u
#define GEN_MM_IRQ_ACK_SIZE           0x00000004u
#define GEN_MM_EOT_ADDR               0x8ffff104u
#define GEN_MM_EOT_SIZE               0x00000004u
#define GEN_MM_PHASE_MARK_ADDR        0x8ffff108u
#define GEN_MM_PHASE_MARK_SIZE        0x00000004u

#define GEN_ICACHE_NUM_FB                  4u
#define GEN_IBUS_MAX_OUTSTANDING           8u
#define GEN_DBUS_MAX_OUTSTANDING           2u
#define GEN_CSR_WRITE_TO_RVFI_OFFSET       2u
#define GEN_TRAP_TO_RVFI_OFFSET            1u
#define GEN_FETCH_EN_DRAIN_CYCLES          64u
#define GEN_LSU_TRAP_TO_RVFI_OFFSET        0u
#define GEN_IRQ_MARKER_TO_RVFI_OFFSET      2u
#define GEN_RVFI_ID_EXIT_OFFSET            2u
#define GEN_ICACHE_ECC_WINDOW              2u
#define GEN_IRQ_ENTRY_BOUND_RECORDS        17u
#define GEN_DBG_ENTRY_BOUND_RECORDS        17u
#define GEN_CLK_PERIOD_NS                  10u
#define GEN_MEM_READBACK_WORDS_DEFAULT     64u
#define GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT   100000u
#define GEN_FINISH_TIMEOUT_CYCLES_DEFAULT  20000u
#define GEN_IRQ_FAST_W                     15u
#define GEN_IRQ_FAST_MASK                  2147418112u
#define GEN_CSR_MARCHID_VALUE              22u
#define GEN_CSR_CPUCTRLSTS                 1984u
#define GEN_CSR_SECURESEED                 1985u
#define GEN_MHPM_COUNTER_NUM               10u
#define GEN_INSN_MRET                      807403635u
#define GEN_INSN_DRET                      2065694835u
#define GEN_TDATA1_IBEX_RDATA              671092808u
#define GEN_CPUCTRLSTS_SYNC_EXC_SEEN_BIT   6u
#define GEN_CPUCTRLSTS_DOUBLE_FAULT_SEEN_BIT 7u
#define GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT  2u
#define GEN_DCSR_PRV_BIT_LOW               0u
#define GEN_DCSR_PRV_BIT_HIGH              1u
#define GEN_CAUSE_NMI_EXTERNAL             2147483679u
#define GEN_CAUSE_NMI_INTERNAL             4294967264u
#define GEN_MEM_ERR_ARM_KIND_ERR           1u
#define GEN_BUS_ERR_LOG_DEPTH              256u
#define GEN_BUS_ERR_DRAIN_CYCLES           96u
#define GEN_NMI_INT_ENTRY_BOUND_RECORDS    4u
#define GEN_MEM_ERR_ARM_KIND_INTG          2u
#define GEN_ISA_FAULT_KIND_FETCH           0u
#define GEN_ISA_FAULT_KIND_LOAD            1u
#define GEN_ISA_FAULT_KIND_STORE           2u

#define GEN_CMD_IRQ_SET                      1u
#define GEN_CMD_IRQ_CLR                      2u
#define GEN_CMD_NMI_PULSE                    3u
#define GEN_CMD_DBG_REQ                      4u
#define GEN_CMD_REGIME_SET                   5u
#define GEN_CMD_KEY_MODE                     6u
#define GEN_CMD_MEM_ERR_ARM                  7u
#define GEN_CMD_ICACHE_ECC_ARM               8u
#define GEN_CMD_FETCH_EN                     9u
#define GEN_CMD_MEM_PEEK                     10u
#define GEN_CMD_MISC                         11u
#define GEN_CMD_EXPORT_FLUSH                 12u
#define GEN_CMD_COV_WITNESS                  13u
#define GEN_CMD_FCOV_SELFTEST                14u
#define GEN_CMD_FCOV_QUERY                   15u

#endif
