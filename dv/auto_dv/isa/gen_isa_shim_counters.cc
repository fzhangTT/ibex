// gen_isa_shim_counters.cc: see gen_isa_shim_counters.h (T-235, Runtime's part; rules from gen_counter_csr_anchors.md section 10).
#include "gen_isa_shim_counters.h"
#include <riscv/encoding.h>

gen_mcountinhibit_csr_t::gen_mcountinhibit_csr_t(processor_t* proc, reg_t addr) : csr_t(proc, addr) {}

void gen_install_counter_holders(processor_t* proc, state_t* s, std::shared_ptr<gen_mcountinhibit_csr_t>& out_inhibit) {
  out_inhibit = std::make_shared<gen_mcountinhibit_csr_t>(proc, CSR_MCOUNTINHIBIT);
  s->csrmap[CSR_MCOUNTINHIBIT] = out_inhibit;
  // Unimplemented counters 13..31: gen_zero_csr_t for the counter, its high half and its event register alike
  // (the mhpmevent13..31 holders duplicate legalize_after_reset's const-0 holders; either may stay, both read 0 and ignore writes).
  for (unsigned i = 13; i <= 31; i++) {
    const unsigned k = i - 3;
    s->csrmap[CSR_MHPMCOUNTER3 + k]  = std::make_shared<gen_zero_csr_t>(proc, CSR_MHPMCOUNTER3 + k);
    s->csrmap[CSR_MHPMCOUNTER3H + k] = std::make_shared<gen_zero_csr_t>(proc, CSR_MHPMCOUNTER3H + k);
    s->csrmap[CSR_MHPMEVENT3 + k]    = std::make_shared<gen_zero_csr_t>(proc, CSR_MHPMEVENT3 + k);
  }
}
