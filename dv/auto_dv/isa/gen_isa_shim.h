// gen_isa_shim.h: C ABI of the Spike-backed ISA model shim (architecture C5). One processor_t over the
// shim's own simif_t (memory served from a sparse word map loaded from the same .vmem as the TB), Ibex
// legalization applied on reset and after each step, Ibex's fast interrupt bits through gen_mie_csr_t,
// custom CSRs through the genibex extension (evidence: gen_t019_spike_build.md, gen_t046_spike_linktest2.md).
// The SV side imports these through gen_isa_dpi_pkg.sv (scalar-argument wrappers); C++ unit tests use
// the structs directly. All functions return 0 on success unless documented; gen_isa_last_error() holds
// the last failure text (ASCII).
#ifndef GEN_ISA_SHIM_H
#define GEN_ISA_SHIM_H
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  uint32_t    boot_addr;      // boot_addr_i; pc = {boot[31:8], GEN_MM_BOOT_RESET_OFFSET}, mtvec = {boot[31:8], 0x01}
  uint32_t    hart_id;
  const char* isa_override;   // NULL: GEN_ISA_STRING from gen_isa_shim_map.h
  const char* log_path;       // NULL or "": no commit log
  uint32_t    mcounteren_writable;   // mcounteren_writable_i == On: writes to mcounteren take effect
} gen_isa_cfg_t;

typedef struct {
  uint32_t pc_before;
  uint32_t pc_after;
  uint32_t insn;              // instruction word fetched for this step (0 when the step took a trap before fetch)
  int32_t  retired;           // instructions retired by this step (minstret delta): 0 for traps/interrupts
  int32_t  trap;              // 1 when the step ended in a trap or interrupt entry
  uint32_t trap_cause;        // mcause after the step when trap == 1
  uint32_t trap_tval;         // mtval after the step when trap == 1
  int32_t  rd_we;             // an integer register other than x0 was written
  uint32_t rd_addr;
  uint32_t rd_wdata;
  int32_t  mem_reads;         // number of data reads logged
  int32_t  mem_writes;        // number of data writes logged
  uint32_t mem_addr;          // first logged access address (word aligned by the caller if needed)
  uint32_t mem_wdata;
  uint32_t mem_rdata;
  uint32_t mem_size;          // bytes of the first logged access
  uint32_t prv;               // privilege after the step (3 = M, 0 = U)
  uint32_t prv_before;        // privilege the instruction executed in (what rvfi_mode reports)
  int32_t  csr_writes;        // CSR writes logged (after legalization); read with gen_isa_csr_write()
  int32_t  reg_writes;        // integer register writes logged (x0 excluded); read with gen_isa_reg_write()
} gen_isa_step_t;

const char* gen_isa_last_error(void);
int      gen_isa_reset(const gen_isa_cfg_t* cfg);
int      gen_isa_load_vmem(const char* path);                     // >= 0: words loaded
void     gen_isa_write_word(uint32_t addr, uint32_t word);        // backdoor into the shim memory
uint32_t gen_isa_read_word(uint32_t addr);
int      gen_isa_step(gen_isa_step_t* out);
int      gen_isa_csr_write(int32_t i, uint32_t* addr, uint32_t* val);   // i-th CSR write of the last step
// Per-step accessors (log order, -1 when i is out of range): x-register writes, data writes, data reads
// (size in bytes; read data is what Spike logged, which is 0).
int      gen_isa_reg_write(int32_t i, uint32_t* idx, uint32_t* val);
int      gen_isa_mem_write(int32_t i, uint32_t* addr, uint32_t* data, uint32_t* size);
int      gen_isa_mem_read(int32_t i, uint32_t* addr, uint32_t* data, uint32_t* size);
uint32_t gen_isa_fetch_insn(uint32_t pc);   // word at pc from the shim memory: 16-bit encodings zero-extended, 0 when unmapped
uint32_t gen_isa_read_csr(uint32_t addr);
int      gen_isa_write_csr(uint32_t addr, uint32_t val);
uint32_t gen_isa_read_gpr(int32_t idx);
void     gen_isa_write_gpr(int32_t idx, uint32_t val);
uint32_t gen_isa_get_pc(void);
void     gen_isa_set_pc(uint32_t pc);
uint32_t gen_isa_get_prv(void);
int      gen_isa_is_draft_b(uint32_t insn);   // 1 when the model cannot execute the op and gen_isa_exec_reference serves it
// Draft-B (Zbp/Zbr/Zbt/Zbf) reference execution (C5.5): 0 = handled and *rd written, 1 = not a draft-B op.
int      gen_isa_exec_reference(uint32_t insn, uint32_t rs1, uint32_t rs2, uint32_t rs3, uint32_t* rd);
void     gen_isa_arm_async(uint32_t pre_mip, uint32_t nmi_mtval, int32_t nmi, int32_t nmi_int,
                           int32_t debug_req, int32_t irq_valid);   // nmi / nmi_int: the next step is the NMI entry (mtval = nmi_mtval when internal)
void     gen_isa_arm_fault(int32_t kind, uint32_t addr, uint32_t size, uint32_t tval);   // tval: the mtval the DUT reports for it
void     gen_isa_set_time(uint64_t mcycle);                          // mcycle from the record's rvfi_ext_mcycle, before its step
void     gen_isa_set_hpm(int32_t idx, uint32_t lo, uint32_t hi);      // mhpmcounter(3+idx) from the record's counter words, before its step
void     gen_isa_set_status(int32_t ic_scr_key_valid);               // cpuctrlsts bit 8 from the record's rvfi_ext_ic_scr_key_valid
void     gen_isa_set_retire_gap(int32_t gap);                         // cycles from the previous record's retirement to this one's (the minstret write corners)
void     gen_isa_count_retire(int32_t n);                             // retirements the model did not step (a draft-B op executed by the scoreboard): counted in minstret unless IR inhibits
void     gen_isa_note_memory_write(uint32_t addr, uint32_t data, uint8_t be);

#ifdef __cplusplus
}
#endif
#endif
