// gen: riscv-dv core setting for the generated TB's DUT (ibex_core + register file, opentitan
// configuration). Values derive from rtl/ibex_pkg.sv and the RISC-V specifications, never from
// any Ibex DV collateral. Template shape: vendor/google_riscv-dv/target/rv32imc/riscv_core_setting.sv.
// Deliberate limits (recorded in dv/auto_dv/evidence/gen_t023_stimulus_toolchain.md):
//   - Zba/Zbb/Zbc/Zbs ratified groups only; the RTL's draft Zbp/Zbr/Zbt/Zbf ops (RV32B group)
//     are excluded from random generation (no ISA model and no assembler agreement for them).
//   - Zcb/Zcmp are not known to this riscv-dv version or to gcc 10.2: directed programs only.
//   - Fast interrupts (mie/mip bits 16..30) and the NMI are not riscv-dv interrupt causes: the
//     TB drives them; the generated vectored table covers ids 1..max_interrupt_vector_num-1.
//   - VECTORED only: ibex forces mtvec.MODE = 01 and 256-byte alignment (+tvec_alignment=8).
//   - support_debug_mode = 0 for now: riscv-dv emits its debug ROM inside .text, but ibex
//     enters debug at the fixed DmHaltAddr; a post-processing step or user-extension override
//     is needed before generated debug ROMs can be used (gen_link.ld already reserves .debug_rom).

parameter int XLEN = 32;

// No address translation in ibex (M and U modes only).
parameter satp_mode_t SATP_MODE = BARE;

privileged_mode_t supported_privileged_mode[] = {MACHINE_MODE, USER_MODE};

riscv_instr_name_t unsupported_instr[];

// RV32IMC plus the ratified bitmanip groups implemented by RV32BOTEarlGrey.
riscv_instr_group_t supported_isa[$] = {RV32I, RV32M, RV32C, RV32ZBA, RV32ZBB, RV32ZBC, RV32ZBS};

// ibex: mtvec.MODE is hard-wired to vectored.
mtvec_mode_t supported_interrupt_mode[$] = {VECTORED};

// Standard causes 3/7/11 only are generator-known; ibex vectors extend to id 30 (fast) and the
// NMI slot 31 (mtvec + 0x7C), so the jump table must cover 32 entries.
int max_interrupt_vector_num = 32;

// opentitan: PMPEnable = 1, PMPNumRegions = 16 (ibex_pkg::PMP_MAX_REGIONS), Smepmp present.
bit support_pmp = 1;

bit support_epmp = 1;

// See header: generated debug ROM placement is not yet solved.
bit support_debug_mode = 0;

// No N extension / user-mode trap delegation in ibex.
bit support_umode_trap = 0;

bit support_sfence = 0;

// ibex splits misaligned data accesses in hardware; no misaligned exception exists.
bit support_unaligned_load_store = 1'b1;

parameter int NUM_FLOAT_GPR = 32;
parameter int NUM_GPR = 32;
parameter int NUM_VEC_GPR = 32;

parameter int VECTOR_EXTENSION_ENABLE = 0;

parameter int VLEN = 512;

parameter int ELEN = 32;

parameter int SELEN = 8;

parameter int VELEN = int'($ln(ELEN)/$ln(2)) - 3;
parameter int MAX_LMUL = 8;

parameter int NUM_HARTS = 1;

// CSRs implemented by ibex (doc/03_reference/cs_registers.rst table; ibex_pkg csr_num_e).
// Used by riscv-dv for signature dumps and gen_all_csrs_by_default; cpuctrlsts/secureseed
// (0x7C0/0x7C1) are custom_csr candidates, left out until their write effects are wanted.
`ifdef DSIM
privileged_reg_t implemented_csr[] = {
`else
const privileged_reg_t implemented_csr[] = {
`endif
    MVENDORID, MARCHID, MIMPID, MHARTID, MCONFIGPTR,
    MSTATUS, MSTATUSH, MISA, MIE, MTVEC, MCOUNTEREN, MENVCFG, MENVCFGH,
    MSCRATCH, MEPC, MCAUSE, MTVAL, MIP,
    PMPCFG0, PMPCFG1, PMPCFG2, PMPCFG3,
    PMPADDR0, PMPADDR1, PMPADDR2, PMPADDR3, PMPADDR4, PMPADDR5, PMPADDR6, PMPADDR7,
    PMPADDR8, PMPADDR9, PMPADDR10, PMPADDR11, PMPADDR12, PMPADDR13, PMPADDR14, PMPADDR15,
    MSECCFG, MSECCFGH,
    TSELECT, TDATA1, TDATA2, TDATA3, TINFO, MCONTEXT, MSCONTEXT, SCONTEXT,
    DCSR, DPC, DSCRATCH0, DSCRATCH1,
    MCOUNTINHIBIT,
    MHPMEVENT3, MHPMEVENT4, MHPMEVENT5, MHPMEVENT6, MHPMEVENT7, MHPMEVENT8, MHPMEVENT9,
    MHPMEVENT10, MHPMEVENT11, MHPMEVENT12,
    MCYCLE, MINSTRET, MCYCLEH, MINSTRETH,
    MHPMCOUNTER3, MHPMCOUNTER4, MHPMCOUNTER5, MHPMCOUNTER6, MHPMCOUNTER7, MHPMCOUNTER8,
    MHPMCOUNTER9, MHPMCOUNTER10, MHPMCOUNTER11, MHPMCOUNTER12,
    MHPMCOUNTER3H, MHPMCOUNTER12H
};
bit [11:0] custom_csr[] = {
};

`ifdef DSIM
interrupt_cause_t implemented_interrupt[] = {
`else
const interrupt_cause_t implemented_interrupt[] = {
`endif
    M_SOFTWARE_INTR,
    M_TIMER_INTR,
    M_EXTERNAL_INTR
};

// ibex exception codes 1, 2, 3, 5, 7, 8, 11 (doc/03_reference/exception_interrupts.rst); no
// address-misaligned exceptions exist for RV32 data accesses or fetches (C always on).
`ifdef DSIM
exception_cause_t implemented_exception[] = {
`else
const exception_cause_t implemented_exception[] = {
`endif
    INSTRUCTION_ACCESS_FAULT,
    ILLEGAL_INSTRUCTION,
    BREAKPOINT,
    LOAD_ACCESS_FAULT,
    STORE_AMO_ACCESS_FAULT,
    ECALL_UMODE,
    ECALL_MMODE
};
