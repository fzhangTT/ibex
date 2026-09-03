// gen_isa_shim_counters.h: Ibex's counter CSR holders for the Spike-backed ISA shim (T-235, Runtime's part to tb-infra's
// spec dv/auto_dv/work/tb-infra/gen_t235_counters_spec.md). Authority for every rule: dv/auto_dv/evidence/gen_counter_csr_anchors.md
// section 10; the rtl/ibex_cs_registers.sv lines it cites are given per member. Pure C++ against tools/spike headers; no TB dependence.
#ifndef GEN_ISA_SHIM_COUNTERS_H
#define GEN_ISA_SHIM_COUNTERS_H
#include <riscv/csrs.h>
#include <riscv/processor.h>
#include <memory>
#include "gen_isa_shim_map.h"

// mcountinhibit as Ibex holds it: bits 0 and 2..(MHPMCounterNum + 2) writable, bit 1 and the bits above read 0, reset 0
// (rtl/ibex_cs_registers.sv:304 storage width, :1554-1561 write with bit 1 forced 0 and bits 31:13 dropped, :1714 read, :1723-1728 reset).
// Spike's own mcountinhibit is never touched (it stays 0 so Spike's minstret keeps counting); the proxy reads the two bits below (:1627, :1643).
class gen_mcountinhibit_csr_t : public csr_t {
 public:
  gen_mcountinhibit_csr_t(processor_t* proc, reg_t addr);
  static constexpr reg_t kMask = (reg_t)1 | ((((reg_t)1 << (GEN_MHPM_COUNTER_NUM + 1)) - 1) << 2);   // 0x1FFD for MHPMCounterNum 10
  reg_t read() const noexcept override { return val_; }
  bool ir_inhibited() const noexcept { return ((val_ >> 2) & 1) != 0; }   // bit 2: minstret increment masked
  bool cy_inhibited() const noexcept { return (val_ & 1) != 0; }          // bit 0: mcycle increment masked
 protected:
  bool unlogged_write(reg_t val) noexcept override { val_ = val & kMask; return true; }
 private:
  reg_t val_ = 0;
};

// A CSR Ibex implements as a constant zero that ignores writes without trapping in M: mhpmcounter13..31 and their high halves
// (:1699-1700 read 0, :1716-1717 write enables tied off) and mhpmevent13..31 (:1615-1618 read 0, no write arm in :845-872).
class gen_zero_csr_t : public csr_t {
 public:
  gen_zero_csr_t(processor_t* proc, reg_t addr) : csr_t(proc, addr) {}
  reg_t read() const noexcept override { return 0; }
 protected:
  bool unlogged_write(reg_t) noexcept override { return true; }
};

// Creates the holders and places them in s->csrmap (called after every reset() rebuilt csrmap; each call replaces the previous
// instances); hands the inhibit holder back so gen_isa_shim.cc can keep it for the minstret proxy.
void gen_install_counter_holders(processor_t* proc, state_t* s, std::shared_ptr<gen_mcountinhibit_csr_t>& out_inhibit);

#endif
