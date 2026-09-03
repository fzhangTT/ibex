// gen_isa_shim.cc: the Spike-backed ISA model behind the DPI (architecture C5.1-C5.5). One processor_t
// over gen_simif_t, a sparse word memory loaded from the same .vmem as the TB and served byte-wise through
// mmio_fetch/load/store (addr_to_mem is NULL: every access is MMIO to Spike); an armed bus fault fails the
// access it covers. Per-word PMP splitting of misaligned accesses and the mtval override are NOT implemented.
// Ibex legalization on reset and after each step (C5.3a), fast interrupt bits through gen_mie_csr_t,
// cpuctrlsts/secureseed through the genibex extension, time(h) trapping, misa fixed to Ibex's value.
// Failures never abort: functions return < 0 and gen_isa_last_error() explains (the SV side raises the
// collected report). Build: dv/auto_dv/isa/gen_isa_shim_build.sh. ASCII only.
#include "gen_isa_shim.h"
#include "gen_isa_shim_map.h"

#include <riscv/cfg.h>
#include <riscv/simif.h>
#include <riscv/processor.h>
#include <riscv/mmu.h>
#include <riscv/csrs.h>
#include <riscv/encoding.h>
#include <riscv/extension.h>
#include <riscv/trap.h>
#include <riscv/debug_rom_defines.h>

#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

namespace {

std::string g_err;
void set_err(const std::string& s) { g_err = s; }

// ---- Ibex constants the shim legalizes to (RTL-defined rows of C5.3a) --------------------------
constexpr uint32_t kFastMask       = GEN_IRQ_FAST_MASK;                    // mie/mip bits 16..30
constexpr uint32_t kIbexMieMask    = MIP_MSIP | MIP_MTIP | MIP_MEIP | kFastMask;
constexpr uint32_t kMipInjectMask  = kIbexMieMask;
// misa: C(2) I(8) M(12) U(20) X(23: MisaXBit = RV32BExtra | BaseIsa == RV32IorCHERIoT) MXL=1
constexpr uint32_t kIbexMisa       = (1u << 2) | (1u << 8) | (1u << 12) | (1u << 20) | (1u << 23) | (1u << 30);
constexpr uint32_t kMcounterenMask = 0x1FFDu;                               // 13 bits, bit 1 (TM) forced 0
constexpr uint32_t kCpuctrlWmask   = 0x0FFu;                                // cpuctrlsts writable fields (icache_enable .. double_fault_seen)
constexpr uint32_t kMstatusReset   = 0x80u;                                 // MPIE 1, MPP U
constexpr uint32_t kResetMtvecMode = 1u;

// ---- memory ------------------------------------------------------------------------------------
std::unordered_map<uint32_t, uint32_t> g_mem;   // word index -> word
struct armed_fault_t { int kind; uint32_t addr; uint32_t size; bool armed; };
armed_fault_t g_fault{0, 0, 0, false};

bool mapped(uint32_t a) {
  return (a >= GEN_MM_BOOT_PAGE && a - GEN_MM_BOOT_PAGE < GEN_MM_PROG_SIZE) ||
         (a >= GEN_MM_DM_BASE && a - GEN_MM_DM_BASE < GEN_MM_DM_SIZE) ||
         (a >= GEN_MM_MMIO_BASE && a - GEN_MM_MMIO_BASE < GEN_MM_MMIO_SIZE);
}
uint8_t mem_rd8(uint32_t a) {
  auto it = g_mem.find(a >> 2);
  uint32_t w = (it == g_mem.end()) ? 0u : it->second;
  return (uint8_t)(w >> (8 * (a & 3)));
}
void mem_wr8(uint32_t a, uint8_t b) {
  uint32_t& w = g_mem[a >> 2];
  uint32_t sh = 8 * (a & 3);
  w = (w & ~(0xFFu << sh)) | ((uint32_t)b << sh);
}
bool fault_hits(int kind, uint32_t a, size_t len) {
  if (!g_fault.armed || g_fault.kind != kind) return false;
  uint32_t lo = g_fault.addr, hi = g_fault.addr + (g_fault.size ? g_fault.size : 4);
  return (a < hi) && (a + len > lo);
}

class gen_simif_t : public simif_t {
 public:
  explicit gen_simif_t(const cfg_t& cfg) : cfg_(cfg) { debug_mmu = nullptr; }
  char* addr_to_mem(reg_t) override { return nullptr; }          // everything is MMIO (C5.4)
  bool mmio_fetch(reg_t paddr, size_t len, uint8_t* bytes) override {
    if (!mapped((uint32_t)paddr) || fault_hits(0, (uint32_t)paddr, len)) return false;
    for (size_t i = 0; i < len; i++) bytes[i] = mem_rd8((uint32_t)paddr + i);
    return true;
  }
  bool mmio_load(reg_t paddr, size_t len, uint8_t* bytes) override {
    if (!mapped((uint32_t)paddr) || fault_hits(1, (uint32_t)paddr, len)) return false;
    for (size_t i = 0; i < len; i++) bytes[i] = mem_rd8((uint32_t)paddr + i);
    return true;
  }
  bool mmio_store(reg_t paddr, size_t len, const uint8_t* bytes) override {
    if (!mapped((uint32_t)paddr) || fault_hits(2, (uint32_t)paddr, len)) return false;
    for (size_t i = 0; i < len; i++) mem_wr8((uint32_t)paddr + i, bytes[i]);
    return true;
  }
  void proc_reset(unsigned) override {}
  const cfg_t& get_cfg() const override { return cfg_; }
  const std::map<size_t, processor_t*>& get_harts() const override { return harts_; }
  const char* get_symbol(uint64_t) override { return nullptr; }
  void add_hart(processor_t* p) { harts_[0] = p; }
 private:
  const cfg_t& cfg_;
  std::map<size_t, processor_t*> harts_;
};

// ---- CSR classes (link test 2) ----------------------------------------------------------------
class gen_mie_csr_t : public mie_csr_t {   // Ibex's writable mie set (unlogged_write is final: override the mask)
 public:
  using mie_csr_t::mie_csr_t;
 private:
  reg_t write_mask() const noexcept override { return kIbexMieMask; }
};
class gen_masked_csr_t : public csr_t {    // cpuctrlsts (masked) and secureseed (reads 0)
 public:
  gen_masked_csr_t(processor_t* proc, reg_t addr, reg_t mask) : csr_t(proc, addr), mask_(mask) {}
  reg_t read() const noexcept override { return val_; }
 protected:
  bool unlogged_write(reg_t val) noexcept override { val_ = val & mask_; return true; }
 private:
  reg_t mask_;
  reg_t val_ = 0;
};
class gen_const_csr_t : public csr_t {     // misa as Ibex reports it; writes ignored (read-only)
 public:
  gen_const_csr_t(processor_t* proc, reg_t addr, reg_t v) : csr_t(proc, addr), v_(v) {}
  reg_t read() const noexcept override { return v_; }
 protected:
  bool unlogged_write(reg_t) noexcept override { return false; }
 private:
  reg_t v_;
};
class gen_trap_csr_t : public csr_t {      // time / timeh: Ibex has no such CSR (illegal instruction)
 public:
  gen_trap_csr_t(processor_t* proc, reg_t addr) : csr_t(proc, addr) {}
  void verify_permissions(insn_t insn, bool) const override { throw trap_illegal_instruction(insn.bits()); }
  reg_t read() const noexcept override { return 0; }
 protected:
  bool unlogged_write(reg_t) noexcept override { return false; }
};
class gen_ibex_ext_t : public extension_t {
 public:
  std::vector<insn_desc_t> get_instructions(const processor_t&) override { return {}; }
  std::vector<disasm_insn_t*> get_disasms(const processor_t* = nullptr) override { return {}; }
  std::vector<csr_t_p> get_csrs(processor_t& p) const override {
    return {std::make_shared<gen_masked_csr_t>(&p, 0x7C0, kCpuctrlWmask),
            std::make_shared<gen_masked_csr_t>(&p, 0x7C1, 0)};
  }
  const char* name() const override { return "genibex"; }   // no underscore: the ISA parser splits on it
};
REGISTER_EXTENSION(genibex, []() { return new gen_ibex_ext_t; })

// ---- model instance ---------------------------------------------------------------------------
cfg_t g_cfg;
std::string g_isa;
std::unique_ptr<gen_simif_t> g_sim;
std::unique_ptr<processor_t> g_proc;
FILE* g_logf = nullptr;
std::vector<std::pair<uint32_t, uint32_t>> g_csr_writes;
std::vector<std::pair<uint32_t, uint32_t>> g_reg_writes;   // (idx, value) of the last step, x0 excluded, ascending register index (commit_log_reg_t is a std::map)
struct mem_access_t { uint32_t addr, data, size; };
std::vector<mem_access_t> g_mem_writes, g_mem_reads;       // data accesses of the last step, log order
uint32_t g_boot = 0;
uint32_t g_mcounteren_writable = 1;
uint32_t g_mcounteren_prev = 0;
bool g_pending_debug = false;

state_t* st() { return g_proc->get_state(); }
uint32_t csr(int which) { return (uint32_t)g_proc->get_csr(which); }

uint32_t fetch_word(uint32_t pc) {
  uint32_t lo = mem_rd8(pc) | (mem_rd8(pc + 1) << 8);
  if ((lo & 3) != 3) return lo;                       // compressed: 16-bit encoding zero-extended
  return lo | (mem_rd8(pc + 2) << 16) | (mem_rd8(pc + 3) << 24);
}

void legalize_after_reset() {
  state_t* s = st();
  // mie with Ibex's bits, installed after reset() rebuilt csrmap
  auto mie = std::make_shared<gen_mie_csr_t>(g_proc.get(), CSR_MIE);
  s->mie = mie;
  s->csrmap[CSR_MIE] = mie;
  s->csrmap[CSR_MISA] = std::make_shared<gen_const_csr_t>(g_proc.get(), CSR_MISA, kIbexMisa);
  s->csrmap[CSR_TIME]  = std::make_shared<gen_trap_csr_t>(g_proc.get(), CSR_TIME);
  s->csrmap[CSR_TIMEH] = std::make_shared<gen_trap_csr_t>(g_proc.get(), CSR_TIMEH);
  // reset values (C5.3a Reset row)
  uint32_t page = g_boot & GEN_MM_BOOT_PAGE_MASK;
  s->pc = page | 0x80u;
  g_proc->put_csr(CSR_MTVEC, page | kResetMtvecMode);
  g_proc->put_csr(CSR_MSTATUS, kMstatusReset);
  for (int i = 0; i < 4; i++) g_proc->put_csr(CSR_PMPCFG0 + i, 0);
  for (int i = 0; i < 16; i++) g_proc->put_csr(CSR_PMPADDR0 + i, 0);
  g_proc->put_csr(CSR_MIE, 0);
  g_proc->put_csr(CSR_MCAUSE, 0);
  g_proc->put_csr(CSR_MEPC, 0);
  g_proc->put_csr(CSR_MTVAL, 0);
  g_proc->put_csr(CSR_MSCRATCH, 0);
  g_mcounteren_prev = csr(CSR_MCOUNTEREN);
  g_proc->halt_request = processor_t::HR_NONE;
  g_pending_debug = false;
}

// CSR write legalization after a step (C5.3a rows); returns the value that now stands.
uint32_t legalize_csr_write(uint32_t addr) {
  uint32_t v = csr(addr);
  switch (addr) {
    case CSR_MTVEC: {
      uint32_t leg = (v & 0xFFFFFF00u) | 1u;             // BASE[7:2] = 0, MODE vectored
      if (leg != v) g_proc->put_csr(CSR_MTVEC, leg);
      return leg;
    }
    case CSR_MCOUNTEREN: {
      uint32_t leg = g_mcounteren_writable ? (v & kMcounterenMask) : g_mcounteren_prev;
      if (leg != v) g_proc->put_csr(CSR_MCOUNTEREN, leg);
      g_mcounteren_prev = leg;
      return leg;
    }
    default:
      return v;
  }
}

// ---- draft-B reference (C5.5): grev/gorc with any immediate; the rest arrive with directed tests
uint32_t grev32(uint32_t x, uint32_t k) {
  if (k & 1)  x = ((x & 0x55555555u) << 1)  | ((x & 0xAAAAAAAAu) >> 1);
  if (k & 2)  x = ((x & 0x33333333u) << 2)  | ((x & 0xCCCCCCCCu) >> 2);
  if (k & 4)  x = ((x & 0x0F0F0F0Fu) << 4)  | ((x & 0xF0F0F0F0u) >> 4);
  if (k & 8)  x = ((x & 0x00FF00FFu) << 8)  | ((x & 0xFF00FF00u) >> 8);
  if (k & 16) x = ((x & 0x0000FFFFu) << 16) | ((x & 0xFFFF0000u) >> 16);
  return x;
}
uint32_t gorc32(uint32_t x, uint32_t k) {
  if (k & 1)  x |= ((x & 0x55555555u) << 1)  | ((x & 0xAAAAAAAAu) >> 1);
  if (k & 2)  x |= ((x & 0x33333333u) << 2)  | ((x & 0xCCCCCCCCu) >> 2);
  if (k & 4)  x |= ((x & 0x0F0F0F0Fu) << 4)  | ((x & 0xF0F0F0F0u) >> 4);
  if (k & 8)  x |= ((x & 0x00FF00FFu) << 8)  | ((x & 0xFF00FF00u) >> 8);
  if (k & 16) x |= ((x & 0x0000FFFFu) << 16) | ((x & 0xFFFF0000u) >> 16);
  return x;
}

}  // namespace

extern "C" {

const char* gen_isa_last_error(void) { return g_err.c_str(); }

int gen_isa_reset(const gen_isa_cfg_t* cfg) {
  try {
    g_proc.reset();
    g_sim.reset();
    if (g_logf && g_logf != stderr) { std::fclose(g_logf); g_logf = nullptr; }
    g_isa = (cfg->isa_override && cfg->isa_override[0]) ? std::string(cfg->isa_override) : std::string(GEN_ISA_STRING);
    if (g_isa.find("xgenibex") == std::string::npos) g_isa += "_xgenibex";
    g_cfg = cfg_t();
    g_cfg.isa = g_isa.c_str();
    g_cfg.priv = "mu";
    g_cfg.pmpregions = 16;
    g_cfg.pmpgranularity = 4;
    g_cfg.trigger_count = 1;
    g_boot = cfg->boot_addr;
    g_mcounteren_writable = cfg->mcounteren_writable;
    g_sim = std::make_unique<gen_simif_t>(g_cfg);
    bool logging = cfg->log_path && cfg->log_path[0];
    g_logf = logging ? std::fopen(cfg->log_path, "w") : std::fopen("/dev/null", "w");
    if (!g_logf) { set_err(std::string("cannot open log ") + cfg->log_path); return -1; }
    g_proc = std::make_unique<processor_t>(g_cfg.isa, g_cfg.priv, &g_cfg, g_sim.get(), cfg->hart_id, false, g_logf, std::cerr);
    g_sim->add_hart(g_proc.get());
    g_proc->reset();                       // the constructor's reset ran before genibex was registered
    g_proc->enable_log_commits();          // the step bookkeeping needs the commit log even when not written out
    legalize_after_reset();
    g_fault.armed = false;
    g_csr_writes.clear();
    g_reg_writes.clear();
    g_mem_writes.clear();
    g_mem_reads.clear();
    return 0;
  } catch (std::exception& e) {
    set_err(std::string("gen_isa_reset: ") + e.what());
    return -1;
  } catch (...) {
    set_err("gen_isa_reset: unknown failure (bad ISA string?)");
    return -1;
  }
}

int gen_isa_load_vmem(const char* path) {
  std::ifstream f(path);
  if (!f) { set_err(std::string("cannot open image ") + path); return -1; }
  std::string line;
  uint32_t idx = 0;
  int n = 0;
  while (std::getline(f, line)) {
    while (!line.empty() && (line.back() == '\r' || line.back() == ' ')) line.pop_back();
    if (line.empty()) continue;
    if (line[0] == '@') { idx = (uint32_t)std::stoul(line.substr(1), nullptr, 16); continue; }
    g_mem[idx++] = (uint32_t)std::stoul(line, nullptr, 16);
    n++;
  }
  return n;
}

void gen_isa_write_word(uint32_t addr, uint32_t word) { g_mem[addr >> 2] = word; }
uint32_t gen_isa_read_word(uint32_t addr) {
  auto it = g_mem.find(addr >> 2);
  return it == g_mem.end() ? 0u : it->second;
}

int gen_isa_step(gen_isa_step_t* out) {
  if (!g_proc) { set_err("gen_isa_step before gen_isa_reset"); return -1; }
  std::memset(out, 0, sizeof(*out));
  g_csr_writes.clear();
  g_reg_writes.clear();
  g_mem_writes.clear();
  g_mem_reads.clear();
  state_t* s = st();
  uint64_t minstret0 = g_proc->get_csr(CSR_MINSTRET) | ((uint64_t)g_proc->get_csr(CSR_MINSTRETH) << 32);
  out->pc_before = (uint32_t)s->pc;
  out->insn = mapped(out->pc_before) ? fetch_word(out->pc_before) : 0u;
  s->log_reg_write.clear();
  s->log_mem_read.clear();
  s->log_mem_write.clear();
  bool was_debug = s->debug_mode;
  try {
    g_proc->step(1);
  } catch (std::exception& e) {
    set_err(std::string("gen_isa_step: ") + e.what());
    return -1;
  }
  uint64_t minstret1 = g_proc->get_csr(CSR_MINSTRET) | ((uint64_t)g_proc->get_csr(CSR_MINSTRETH) << 32);
  out->retired = (int32_t)(minstret1 - minstret0);
  // debug entry: Spike parks pc in its own ROM (0x800/0x808); Ibex enters at DmHaltAddr (C5.2)
  if (!was_debug && s->debug_mode) {
    s->pc = GEN_MM_DM_HALT;
    g_proc->halt_request = processor_t::HR_NONE;
  }
  out->pc_after = (uint32_t)s->pc;
  out->prv = (uint32_t)s->prv;
  if (out->retired == 0) {
    out->trap = 1;
    out->trap_cause = csr(CSR_MCAUSE);
    out->trap_tval = csr(CSR_MTVAL);
  }
  for (auto& kv : s->log_reg_write) {
    reg_t key = kv.first;
    int type = key & 0xF;
    reg_t idx = key >> 4;
    if (type == 0) {                                   // integer register
      if (idx != 0) {
        out->rd_we = 1; out->rd_addr = (uint32_t)idx; out->rd_wdata = (uint32_t)kv.second.v[0];
        g_reg_writes.emplace_back((uint32_t)idx, (uint32_t)kv.second.v[0]);
      }
    } else if (type == 4) {                            // CSR
      uint32_t a = (uint32_t)idx;
      try {
        g_csr_writes.emplace_back(a, legalize_csr_write(a));
      } catch (trap_t& t) {
        // a logged CSR write whose address get_csr rejects (not in csrmap): record it unlegalized
        char buf[96];
        std::snprintf(buf, sizeof(buf), "csr 0x%03x logged but not readable (cause %llu)", a, (unsigned long long)t.cause());
        set_err(buf);
        g_csr_writes.emplace_back(a, (uint32_t)kv.second.v[0]);
      }
    }
  }
  out->csr_writes = (int32_t)g_csr_writes.size();
  out->reg_writes = (int32_t)g_reg_writes.size();
  for (auto& m : s->log_mem_write) g_mem_writes.push_back({(uint32_t)std::get<0>(m), (uint32_t)std::get<1>(m), std::get<2>(m)});
  for (auto& m : s->log_mem_read)  g_mem_reads.push_back({(uint32_t)std::get<0>(m), (uint32_t)std::get<1>(m), std::get<2>(m)});
  out->mem_reads = (int32_t)s->log_mem_read.size();
  out->mem_writes = (int32_t)s->log_mem_write.size();
  if (!s->log_mem_write.empty()) {
    out->mem_addr = (uint32_t)std::get<0>(s->log_mem_write[0]);
    out->mem_wdata = (uint32_t)std::get<1>(s->log_mem_write[0]);
    out->mem_size = std::get<2>(s->log_mem_write[0]);
  } else if (!s->log_mem_read.empty()) {
    out->mem_addr = (uint32_t)std::get<0>(s->log_mem_read[0]);
    out->mem_rdata = (uint32_t)std::get<1>(s->log_mem_read[0]);
    out->mem_size = std::get<2>(s->log_mem_read[0]);
  }
  return 0;
}

int gen_isa_csr_write(int32_t i, uint32_t* addr, uint32_t* val) {
  if (i < 0 || (size_t)i >= g_csr_writes.size()) return -1;
  *addr = g_csr_writes[i].first;
  *val = g_csr_writes[i].second;
  return 0;
}
int gen_isa_reg_write(int32_t i, uint32_t* idx, uint32_t* val) {
  if (i < 0 || (size_t)i >= g_reg_writes.size()) return -1;
  *idx = g_reg_writes[i].first;
  *val = g_reg_writes[i].second;
  return 0;
}
int gen_isa_mem_write(int32_t i, uint32_t* addr, uint32_t* data, uint32_t* size) {
  if (i < 0 || (size_t)i >= g_mem_writes.size()) return -1;
  *addr = g_mem_writes[i].addr; *data = g_mem_writes[i].data; *size = g_mem_writes[i].size;
  return 0;
}
int gen_isa_mem_read(int32_t i, uint32_t* addr, uint32_t* data, uint32_t* size) {
  if (i < 0 || (size_t)i >= g_mem_reads.size()) return -1;
  *addr = g_mem_reads[i].addr; *data = g_mem_reads[i].data; *size = g_mem_reads[i].size;
  return 0;
}
uint32_t gen_isa_fetch_insn(uint32_t pc) { return mapped(pc) ? fetch_word(pc) : 0u; }

uint32_t gen_isa_read_csr(uint32_t addr) {
  try { return (uint32_t)g_proc->get_csr((int)addr); } catch (...) { return 0xFFFFFFFFu; }
}
int gen_isa_write_csr(uint32_t addr, uint32_t val) {
  try { g_proc->put_csr((int)addr, val); return 0; } catch (...) { set_err("gen_isa_write_csr failed"); return -1; }
}
uint32_t gen_isa_read_gpr(int32_t idx) { return (uint32_t)st()->XPR[idx]; }
void gen_isa_write_gpr(int32_t idx, uint32_t val) { if (idx != 0) st()->XPR.write(idx, (sreg_t)(int32_t)val); }
uint32_t gen_isa_get_pc(void) { return (uint32_t)st()->pc; }
void gen_isa_set_pc(uint32_t pc) { st()->pc = (sreg_t)(int32_t)pc; }
uint32_t gen_isa_get_prv(void) { return (uint32_t)st()->prv; }

int gen_isa_exec_reference(uint32_t insn, uint32_t rs1, uint32_t rs2, uint32_t rs3, uint32_t* rd) {
  uint32_t opcode = insn & 0x7F, f3 = (insn >> 12) & 7, f7 = (insn >> 25) & 0x7F, hi5 = (insn >> 27) & 0x1F;
  uint32_t shamt = (insn >> 20) & 0x1F;
  if (opcode == 0x13 && f3 == 5 && ((insn >> 26) & 1) == 0) {
    if (hi5 == 0x0D) { *rd = grev32(rs1, shamt); return 0; }       // grevi (rev8 = 24)
    if (hi5 == 0x05) { *rd = gorc32(rs1, shamt); return 0; }       // gorci (orc.b = 7)
  }
  if (opcode == 0x33 && f3 == 5) {
    if (f7 == 0x34) { *rd = grev32(rs1, rs2 & 31); return 0; }     // grev
    if (f7 == 0x14) { *rd = gorc32(rs1, rs2 & 31); return 0; }     // gorc
  }
  (void)rs3;
  return 1;
}

void gen_isa_arm_async(uint32_t pre_mip, uint32_t, int32_t, int32_t, int32_t debug_req, int32_t) {
  if (!g_proc) return;
  st()->mip->backdoor_write_with_mask(kMipInjectMask, pre_mip);
  if (debug_req) g_proc->halt_request = processor_t::HR_REGULAR;
}
void gen_isa_arm_fault(int32_t kind, uint32_t addr, uint32_t size) { g_fault = {kind, addr, size, true}; }
void gen_isa_set_time(uint64_t mcycle) {
  if (!g_proc) return;
  g_proc->put_csr(CSR_MCYCLE, (uint32_t)mcycle);
  g_proc->put_csr(CSR_MCYCLEH, (uint32_t)(mcycle >> 32));
}
void gen_isa_note_memory_write(uint32_t addr, uint32_t data, uint8_t be) {
  for (int k = 0; k < 4; k++) if (be & (1 << k)) mem_wr8(addr + k, (uint8_t)(data >> (8 * k)));
}

}  // extern "C"

// ---- DPI-C wrappers (scalar arguments; structs do not cross the DPI boundary) --------------------
extern "C" {
int gen_isa_reset_dpi(uint32_t boot_addr, uint32_t hart_id, const char* isa_override, const char* log_path,
                      int32_t mcounteren_writable) {
  gen_isa_cfg_t c{};
  c.boot_addr = boot_addr; c.hart_id = hart_id; c.isa_override = isa_override; c.log_path = log_path;
  c.mcounteren_writable = (uint32_t)mcounteren_writable;
  return gen_isa_reset(&c);
}
int gen_isa_step_dpi(uint32_t* pc_before, uint32_t* pc_after, uint32_t* insn, int32_t* retired, int32_t* trap,
                     uint32_t* trap_cause, uint32_t* trap_tval, int32_t* rd_we, uint32_t* rd_addr, uint32_t* rd_wdata,
                     int32_t* mem_reads, int32_t* mem_writes, uint32_t* mem_addr, uint32_t* mem_wdata,
                     uint32_t* mem_rdata, uint32_t* mem_size, uint32_t* prv, int32_t* csr_writes,
                     int32_t* reg_writes) {
  gen_isa_step_t o;
  int rc = gen_isa_step(&o);
  *pc_before = o.pc_before; *pc_after = o.pc_after; *insn = o.insn; *retired = o.retired; *trap = o.trap;
  *trap_cause = o.trap_cause; *trap_tval = o.trap_tval; *rd_we = o.rd_we; *rd_addr = o.rd_addr; *rd_wdata = o.rd_wdata;
  *mem_reads = o.mem_reads; *mem_writes = o.mem_writes; *mem_addr = o.mem_addr; *mem_wdata = o.mem_wdata;
  *mem_rdata = o.mem_rdata; *mem_size = o.mem_size; *prv = o.prv; *csr_writes = o.csr_writes;
  *reg_writes = o.reg_writes;
  return rc;
}
// 1 when the instruction is a draft-B op the model cannot execute (served by gen_isa_exec_reference)
int gen_isa_is_draft_b(uint32_t insn) {
  uint32_t rd = 0;
  uint32_t opcode = insn & 0x7F, f3 = (insn >> 12) & 7, hi5 = (insn >> 27) & 0x1F, shamt = (insn >> 20) & 0x1F;
  if (opcode == 0x13 && f3 == 5 && ((insn >> 26) & 1) == 0) {
    if (hi5 == 0x0D && shamt == 24) return 0;   // rev8: ratified alias, the model executes it
    if (hi5 == 0x05 && shamt == 7)  return 0;   // orc.b
  }
  return gen_isa_exec_reference(insn, 0, 0, 0, &rd) == 0 ? 1 : 0;
}
}
