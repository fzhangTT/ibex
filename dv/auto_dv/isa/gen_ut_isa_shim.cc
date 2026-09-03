// gen_ut_isa_shim: unit test of the ISA shim (architecture C5; shim unit test 1 of the build order).
// Checks: Ibex reset legalization, the real Zc image run through the model to its tohost store (with the
// per-step register/memory accessors on its cm.push/cm.pop steps), grevi/gorci decode (ratified aliases
// execute, other immediates trap and are served by gen_isa_exec_reference), mtvec/mie/custom-CSR
// legalization, step bookkeeping.
//   gen_ut_isa_shim <path/to/prog.vmem>
#include "gen_isa_shim.h"
#include "gen_isa_shim_map.h"
#include <riscv/encoding.h>
#include <cstdio>
#include <cstring>

static int fails = 0;
static void check(const char* what, unsigned long long got, unsigned long long exp) {
  bool ok = got == exp;
  std::printf("%-44s got 0x%llx exp 0x%llx %s\n", what, got, exp, ok ? "OK" : "FAIL");
  std::fflush(stdout);
  if (!ok) fails++;
}

// Instruction encoders for the reference checks (RTL encodings: rtl/ibex_decoder.sv OPCODE_OP / OPCODE_OP_IMM tables).
static uint32_t enc_r(uint32_t f7, uint32_t f3, uint32_t rs1, uint32_t rs2, uint32_t rd) {
  return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0x33u;
}
static uint32_t enc_r4(uint32_t rs3, uint32_t f2, uint32_t f3, uint32_t rs1, uint32_t rs2, uint32_t rd) {
  return (rs3 << 27) | (f2 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0x33u;
}
static uint32_t enc_i(uint32_t imm12, uint32_t f3, uint32_t rs1, uint32_t rd) {
  return (imm12 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0x13u;
}
static bool ref(uint32_t insn, uint32_t rs1, uint32_t rs2, uint32_t rs3, uint32_t exp) {
  uint32_t rd = 0;
  return gen_isa_exec_reference(insn, rs1, rs2, rs3, &rd) == 0 && rd == exp;
}

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: gen_ut_isa_shim <prog.vmem>\n"); return 2; }
  gen_isa_cfg_t cfg{};
  cfg.boot_addr = GEN_MM_BOOT_ADDR_DEFAULT;
  cfg.hart_id = 0;
  cfg.isa_override = nullptr;
  cfg.log_path = nullptr;
  cfg.mcounteren_writable = 1;

  std::puts("-- 1. reset legalization (C5.3a Reset row)");
  check("gen_isa_reset", gen_isa_reset(&cfg) == 0, 1);
  check("pc = boot page + boot_reset_offset", gen_isa_get_pc(), GEN_MM_BOOT_PAGE + GEN_MM_BOOT_RESET_OFFSET);
  check("mtvec = boot page | 1", gen_isa_read_csr(CSR_MTVEC), GEN_MM_BOOT_PAGE | 1u);
  check("mstatus = 0x80 (MPIE, MPP U)", gen_isa_read_csr(CSR_MSTATUS), 0x80u);
  check("prv M", gen_isa_get_prv(), 3);
  check("misa RV32IMCU + X (MisaXBit = 1 for BaseIsaRV32IorCHERIoT)", gen_isa_read_csr(CSR_MISA), 0x40901104u);
  check("pmpcfg0 all OFF", gen_isa_read_csr(CSR_PMPCFG0), 0);
  check("pmpaddr0 zero", gen_isa_read_csr(CSR_PMPADDR0), 0);
  check("mie zero", gen_isa_read_csr(CSR_MIE), 0);
  check("mcause zero", gen_isa_read_csr(CSR_MCAUSE), 0);

  std::puts("-- 2. the Zc image runs to its tohost store");
  int words = gen_isa_load_vmem(argv[1]);
  check("image words", words > 0, 1);
  check("entry word j _start", gen_isa_read_word(GEN_MM_BOOT_PAGE + GEN_MM_BOOT_RESET_OFFSET), 0x0040006fu);
  gen_isa_step_t st{};
  check("step 1 ok", gen_isa_step(&st) == 0, 1);
  check("step 1 pc_before", st.pc_before, GEN_MM_BOOT_PAGE + GEN_MM_BOOT_RESET_OFFSET);
  check("step 1 insn", st.insn, 0x0040006fu);
  check("step 1 retired", st.retired, 1);
  check("step 1 pc_after = _start (jal +4)", st.pc_after, GEN_MM_BOOT_PAGE + 0x84u);
  check("step 1 no trap", st.trap, 0);
  check("step 1 fetch_insn(pc_before) = insn", gen_isa_fetch_insn(st.pc_before), st.insn);
  check("step 1 (j) logs no x-register write", st.reg_writes, 0);
  { uint32_t i = 0, v = 0; check("step 1 reg_write(0) -> -1", gen_isa_reg_write(0, &i, &v) == -1, 1); }
  int steps = 1, tohost_seen = 0; unsigned tohost_val = 0;
  int fetch_mismatch = 0, rd_we_mismatch = 0, push_seen = 0, pop_seen = 0;
  for (; steps < 2000 && !tohost_seen; steps++) {
    if (gen_isa_step(&st) != 0) { std::printf("step error: %s\n", gen_isa_last_error()); fails++; break; }
    if (gen_isa_fetch_insn(st.pc_before) != st.insn) fetch_mismatch++;
    if ((st.reg_writes > 0) != (st.rd_we != 0)) rd_we_mismatch++;
    if (!push_seen && st.mem_writes >= 2) {   // cm.push: one store per listed register, top register first at sp-4
      push_seen = 1;
      std::printf("   (multi-store step: pc 0x%x insn 0x%x, %d writes)\n", st.pc_before, st.insn, st.mem_writes);
      int bad_rc = 0, bad_align = 0, bad_size = 0, bad_stride = 0;
      uint32_t a = 0, d = 0, sz = 0, prev = 0;
      for (int i = 0; i < st.mem_writes; i++) {
        if (gen_isa_mem_write(i, &a, &d, &sz) != 0) { bad_rc++; continue; }
        if (a & 3) bad_align++;
        if (sz != 4) bad_size++;
        if (i > 0 && a != prev - 4) bad_stride++;
        if (i == 0) { check("cm.push mem_write(0) addr = mem_addr", a, st.mem_addr); check("cm.push mem_write(0) data = mem_wdata", d, st.mem_wdata); }
        prev = a;
      }
      check("cm.push mem_write(i) rc 0 for every i", bad_rc, 0);
      check("cm.push store addresses 4-byte aligned", bad_align, 0);
      check("cm.push store sizes 4", bad_size, 0);
      check("cm.push consecutive stores descend by 4", bad_stride, 0);
      check("cm.push mem_write(mem_writes) -> -1", gen_isa_mem_write(st.mem_writes, &a, &d, &sz) == -1, 1);
      check("cm.push logs no loads", st.mem_reads, 0);
      check("cm.push mem_read(0) -> -1", gen_isa_mem_read(0, &a, &d, &sz) == -1, 1);
    }
    if (!pop_seen && st.reg_writes >= 2) {    // cm.pop: one load and one register write per listed register, plus sp
      pop_seen = 1;
      std::printf("   (multi-register-write step: pc 0x%x insn 0x%x, %d writes, %d reads)\n", st.pc_before, st.insn, st.reg_writes, st.mem_reads);
      int bad_rc = 0, bad_x0 = 0, bad_order = 0;
      uint32_t idx = 0, val = 0, prev_idx = 0;
      for (int i = 0; i < st.reg_writes; i++) {
        if (gen_isa_reg_write(i, &idx, &val) != 0) { bad_rc++; continue; }
        if (idx == 0) bad_x0++;
        if (i > 0 && idx <= prev_idx) bad_order++;
        prev_idx = idx;
      }
      check("cm.pop reg_write(i) rc 0 for every i", bad_rc, 0);
      check("cm.pop reg_write never reports x0", bad_x0, 0);
      check("cm.pop register indices strictly ascending (Spike log order)", bad_order, 0);
      check("cm.pop reg_write(reg_writes) -> -1", gen_isa_reg_write(st.reg_writes, &idx, &val) == -1, 1);
      check("cm.pop logs >= 2 loads", st.mem_reads >= 2, 1);
      int rbad_rc = 0, rbad_align = 0, rbad_size = 0;
      uint32_t a = 0, d = 0, sz = 0;
      for (int i = 0; i < st.mem_reads; i++) {
        if (gen_isa_mem_read(i, &a, &d, &sz) != 0) { rbad_rc++; continue; }
        if (a & 3) rbad_align++;
        if (sz != 4) rbad_size++;
      }
      check("cm.pop mem_read(i) rc 0 for every i", rbad_rc, 0);
      check("cm.pop load addresses 4-byte aligned", rbad_align, 0);
      check("cm.pop load sizes 4", rbad_size, 0);
      check("cm.pop mem_read(mem_reads) -> -1", gen_isa_mem_read(st.mem_reads, &a, &d, &sz) == -1, 1);
      check("cm.pop logs no stores", st.mem_writes, 0);
    }
    if (st.mem_writes > 0 && st.mem_addr == 0x80000280u) { tohost_seen = 1; tohost_val = st.mem_wdata; }
    if (st.trap) { std::printf("unexpected trap cause 0x%x at pc 0x%x\n", st.trap_cause, st.pc_before); fails++; break; }
  }
  check("tohost store reached", tohost_seen, 1);
  check("tohost value 1 (pass)", tohost_val, 1);
  check("steps to tohost within 400", steps < 400, 1);
  std::printf("   (%d steps)\n", steps);
  check("fetch_insn(pc_before) = insn on every step", fetch_mismatch, 0);
  check("rd_we agrees with reg_writes on every step", rd_we_mismatch, 0);
  check("a multi-store step (cm.push) was found", push_seen, 1);
  check("a multi-register-write step (cm.pop) was found", pop_seen, 1);
  check("fetch_insn(unmapped) = 0", gen_isa_fetch_insn(0x00000000u), 0);

  std::puts("-- 3. grevi/gorci decode: aliases execute, other immediates trap, reference serves them");
  check("re-reset", gen_isa_reset(&cfg) == 0, 1);
  const uint32_t scratch = GEN_MM_BOOT_PAGE + GEN_MM_BOOT_RESET_OFFSET;
  const uint32_t prog[] = {0x12345137u, 0x67810113u,   // lui x2,0x12345 ; addi x2,x2,0x678
                           0x69815093u,                  // grevi x1,x2,24  (rev8, Zbb alias)
                           0x28715193u,                  // gorci x3,x2,7   (orc.b, Zbb alias)
                           0x68115213u,                  // grevi x4,x2,1   (Zbp only)
                           0x28115293u,                  // gorci x5,x2,1   (Zbp only)
                           0x00000013u};
  for (unsigned i = 0; i < sizeof(prog) / 4; i++) gen_isa_write_word(scratch + 4 * i, prog[i]);
  gen_isa_write_word(GEN_MM_BOOT_PAGE, 0x00000013u);   // trap vector: nop
  gen_isa_step(&st); gen_isa_step(&st);
  check("x2 = 0x12345678", gen_isa_read_gpr(2), 0x12345678u);
  gen_isa_step(&st);
  check("rev8 retires", st.retired, 1);
  check("rev8 rd", st.rd_addr, 1);
  check("rev8 value", st.rd_wdata, 0x78563412u);
  check("rev8 reg_writes = 1", st.reg_writes, 1);
  { uint32_t i = 0, v = 0;
    check("rev8 reg_write(0) rc", gen_isa_reg_write(0, &i, &v), 0);
    check("rev8 reg_write(0) idx = rd_addr", i, st.rd_addr);
    check("rev8 reg_write(0) val = rd_wdata", v, st.rd_wdata);
    check("rev8 reg_write(1) -> -1", gen_isa_reg_write(1, &i, &v) == -1, 1); }
  gen_isa_step(&st);
  check("orc.b retires", st.retired, 1);
  check("orc.b value", st.rd_wdata, 0xffffffffu);
  gen_isa_step(&st);
  std::printf("   (last shim note: %s)\n", gen_isa_last_error());
  check("grevi imm 1 traps", st.trap, 1);
  check("grevi imm 1 cause illegal (2)", st.trap_cause, 2);
  check("grevi imm 1 mtval = insn", st.trap_tval, 0x68115213u);
  check("grevi imm 1 retires 0", st.retired, 0);
  check("grevi imm 1 fetch_insn(pc_before) = insn", gen_isa_fetch_insn(st.pc_before), st.insn);
  check("grevi imm 1 logs no x-register write", st.reg_writes, 0);
  check("trap pc = mtvec base", st.pc_after, GEN_MM_BOOT_PAGE);
  uint32_t rd = 0;
  check("reference handles grevi imm 1", gen_isa_exec_reference(0x68115213u, 0x12345678u, 0, 0, &rd), 0);
  check("grev(x,1)", rd, 0x2138a9b4u);
  check("reference handles gorci imm 1", gen_isa_exec_reference(0x28115293u, 0x12345678u, 0, 0, &rd), 0);
  check("gorc(x,1)", rd, 0x333cfffcu);
  check("reference grev 31 (rev)", gen_isa_exec_reference(0x69f15213u, 0x12345678u, 0, 0, &rd) == 0 && rd == 0x1e6a2c48u, 1);
  check("reference gorc 16", gen_isa_exec_reference(0x29015293u, 0x00010002u, 0, 0, &rd) == 0 && rd == 0x30003u, 1);
  check("reference rejects a plain addi", gen_isa_exec_reference(0x00000013u, 0, 0, 0, &rd), 1);

  std::puts("-- 4. CSR legalization after retired writes");
  check("re-reset", gen_isa_reset(&cfg) == 0, 1);
  const uint32_t prog2[] = {0x80001337u, 0x23430313u,   // lui x6,0x80001 ; addi x6,x6,0x234  -> 0x80001234
                            0x30531073u,                 // csrw mtvec, x6
                            0x00010337u,                 // lui x6, 0x10 -> 0x10000
                            0x30431073u,                 // csrw mie, x6
                            0x0ff00313u,                 // addi x6, x0, 0xff
                            0x7c031073u,                 // csrw cpuctrlsts(0x7c0), x6
                            0x00000013u};
  for (unsigned i = 0; i < sizeof(prog2) / 4; i++) gen_isa_write_word(scratch + 4 * i, prog2[i]);
  gen_isa_step(&st); gen_isa_step(&st); gen_isa_step(&st);
  check("csrw mtvec retires", st.retired, 1);
  check("mtvec legalized: BASE[7:2] = 0, MODE 1", gen_isa_read_csr(CSR_MTVEC), 0x80001201u);   // 0x80001234 -> BASE 0x80001200
  check("csr write list has mtvec", st.csr_writes >= 1, 1);
  { uint32_t a = 0, v = 0; gen_isa_csr_write(0, &a, &v); check("csr write 0 is mtvec", a, CSR_MTVEC); check("csr write 0 value legalized", v, 0x80001201u); }
  gen_isa_step(&st); gen_isa_step(&st);
  check("mie fast bit 16 sticks", gen_isa_read_csr(CSR_MIE), 0x10000u);
  gen_isa_step(&st); gen_isa_step(&st);
  check("csrw cpuctrlsts retires (no trap)", st.retired, 1);
  check("cpuctrlsts: 8 writable bits (icache_enable .. double_fault_seen), key_valid RO", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS), 0xffu);
  check("gpr write/read", (gen_isa_write_gpr(10, 0xdeadbeefu), gen_isa_read_gpr(10)), 0xdeadbeefu);
  check("set_pc/get_pc", (gen_isa_set_pc(0x80000100u), gen_isa_get_pc()), 0x80000100u);

  std::puts("-- 5. T-102: Ibex conventions the model must show (reset values, WARL, counters, draft-B references)");
  check("re-reset", gen_isa_reset(&cfg) == 0, 1);
  check("marchid = ibex_pkg CSR_MARCHID_VALUE", gen_isa_read_csr(CSR_MARCHID), GEN_CSR_MARCHID_VALUE);
  check("mhpmevent3 = 1 (event bit i-3)", gen_isa_read_csr(CSR_MHPMEVENT3), 1);
  check("mhpmevent(3+N-1) = 1 << (N-1)", gen_isa_read_csr(CSR_MHPMEVENT3 + GEN_MHPM_COUNTER_NUM - 1), 1u << (GEN_MHPM_COUNTER_NUM - 1));
  check("mhpmevent(3+N) = 0 beyond MHPMCounterNum", gen_isa_read_csr(CSR_MHPMEVENT3 + GEN_MHPM_COUNTER_NUM), 0);
  check("mhpmevent31 = 0", gen_isa_read_csr(CSR_MHPMEVENT31), 0);
  check("tdata1 = Ibex mcontrol view", gen_isa_read_csr(CSR_TDATA1), GEN_TDATA1_IBEX_RDATA);
  gen_isa_write_csr(CSR_TDATA1, 0xffffffffu);
  check("tdata1 write outside debug mode ignored", gen_isa_read_csr(CSR_TDATA1), GEN_TDATA1_IBEX_RDATA);
  gen_isa_write_csr(CSR_TDATA2, 0x80000004u);
  check("tdata2 write outside debug mode ignored", gen_isa_read_csr(CSR_TDATA2), 0);
  gen_isa_write_csr(CSR_MSTATUS, 0xffffffffu);
  check("mstatus all-ones write: XS and SD stay 0", gen_isa_read_csr(CSR_MSTATUS) & 0x80018000u, 0);
  check("pack",  ref(enc_r(0x04, 4, 1, 2, 3), 0x12345678u, 0x9abcdef0u, 0, 0xdef05678u), 1);
  check("packu", ref(enc_r(0x24, 4, 1, 2, 3), 0x12345678u, 0x9abcdef0u, 0, 0x9abc1234u), 1);
  check("packh", ref(enc_r(0x04, 7, 1, 2, 3), 0x12345678u, 0x9abcdef0u, 0, 0x0000f078u), 1);
  check("slo 4",  ref(enc_r(0x10, 1, 1, 2, 3), 0x0000000fu, 4, 0, 0xffu), 1);
  check("slo rs2 = 32 acts as 0", ref(enc_r(0x10, 1, 1, 2, 3), 0x12345678u, 32, 0, 0x12345678u), 1);
  check("sloi 31 of 0 = 0x7fffffff", ref(enc_i(0x200u | 31, 1, 1, 3), 0, 0, 0, 0x7fffffffu), 1);
  check("sro 4",  ref(enc_r(0x10, 5, 1, 2, 3), 0xf0000000u, 4, 0, 0xff000000u), 1);
  check("sro 1 of 0 = 0x80000000", ref(enc_r(0x10, 5, 1, 2, 3), 0, 1, 0, 0x80000000u), 1);
  check("sroi 31 of 0 = 0xfffffffe", ref(enc_i(0x200u | 31, 5, 1, 3), 0, 0, 0, 0xfffffffeu), 1);
  check("shfl 15 (zip)", ref(enc_r(0x04, 1, 1, 2, 3), 0x0000ffffu, 15, 0, 0x55555555u), 1);
  check("unshfl 15 (unzip)", ref(enc_r(0x04, 5, 1, 2, 3), 0x55555555u, 15, 0, 0x0000ffffu), 1);
  check("shfli 15", ref(enc_i(0x080u | 15, 1, 1, 3), 0x0000ffffu, 0, 0, 0x55555555u), 1);
  check("unshfli 15", ref(enc_i(0x080u | 15, 5, 1, 3), 0x55555555u, 0, 0, 0x0000ffffu), 1);
  check("xperm.n", ref(enc_r(0x14, 2, 1, 2, 3), 0x76543210u, 0x01234567u, 0, 0x01234567u), 1);
  check("xperm.b", ref(enc_r(0x14, 4, 1, 2, 3), 0x44332211u, 0x00010203u, 0, 0x11223344u), 1);
  check("xperm.b out-of-range lanes read 0", ref(enc_r(0x14, 4, 1, 2, 3), 0x44332211u, 0x04040404u, 0, 0), 1);
  check("xperm.h", ref(enc_r(0x14, 6, 1, 2, 3), 0xbbbbaaaau, 0x00000001u, 0, 0xaaaabbbbu), 1);
  check("cmov rs2 = 0 selects rs3", ref(enc_r4(4, 3, 5, 1, 2, 3), 0x11111111u, 0, 0x33333333u, 0x33333333u), 1);
  check("cmov rs2 != 0 selects rs1", ref(enc_r4(4, 3, 5, 1, 2, 3), 0x11111111u, 5, 0x33333333u, 0x11111111u), 1);
  check("cmix", ref(enc_r4(4, 3, 1, 1, 2, 3), 0xff00ff00u, 0x0000ffffu, 0x12345678u, 0x1234ff00u), 1);
  check("fsl 1",  ref(enc_r4(4, 2, 1, 1, 2, 3), 1, 1, 0x80000000u, 3), 1);
  check("fsl 31", ref(enc_r4(4, 2, 1, 1, 2, 3), 1, 31, 0x80000000u, 0xc0000000u), 1);
  check("fsl 32 = rs3", ref(enc_r4(4, 2, 1, 1, 2, 3), 1, 32, 0x80000000u, 0x80000000u), 1);
  check("fsl 64 acts as 0 = rs1", ref(enc_r4(4, 2, 1, 1, 2, 3), 1, 64, 0x80000000u, 1), 1);
  check("fsr 1",  ref(enc_r4(4, 2, 5, 1, 2, 3), 0x80000000u, 1, 1, 0xc0000000u), 1);
  check("fsri 1", ref((4u << 27) | (1u << 26) | (1u << 20) | (1u << 15) | (5u << 12) | (3u << 7) | 0x13u, 0x80000000u, 0, 1, 0xc0000000u), 1);
  check("bfp len 8 off 8", ref(enc_r(0x24, 7, 1, 2, 3), 0, (8u << 24) | (8u << 16) | 0xabu, 0, 0x0000ab00u), 1);
  check("bfp len 0 places 16 bits", ref(enc_r(0x24, 7, 1, 2, 3), 0xffffffffu, 0x1234u, 0, 0xffff1234u), 1);
  check("crc32.b(1)", ref(enc_i(0x610, 1, 1, 3), 1, 0, 0, 0x77073096u), 1);
  check("crc32.b(2)", ref(enc_i(0x610, 1, 1, 3), 2, 0, 0, 0xee0e612cu), 1);
  check("crc32c.b(1)", ref(enc_i(0x618, 1, 1, 3), 1, 0, 0, 0xf26b8303u), 1);
  check("crc32.w(0) = 0", ref(enc_i(0x612, 1, 1, 3), 0, 0, 0, 0), 1);
  check("crc32c.w(0) = 0", ref(enc_i(0x61a, 1, 1, 3), 0, 0, 0, 0), 1);
  { uint32_t h = 0, b1 = 0, b2 = 0;
    gen_isa_exec_reference(enc_i(0x611, 1, 1, 3), 0x12345678u, 0, 0, &h);
    gen_isa_exec_reference(enc_i(0x610, 1, 1, 3), 0x12345678u, 0, 0, &b1);
    gen_isa_exec_reference(enc_i(0x610, 1, 1, 3), b1, 0, 0, &b2);
    check("crc32.h = crc32.b applied twice", h, b2); }
  check("reference rejects rori (ratified)", gen_isa_exec_reference(enc_i(0x601, 5, 1, 3), 0, 0, 0, &rd), 1);
  check("reference rejects clz (ratified)", gen_isa_exec_reference(enc_i(0x600, 1, 1, 3), 0, 0, 0, &rd), 1);
  check("is_draft_b(pack) = 1", gen_isa_is_draft_b(enc_r(0x04, 4, 1, 2, 3)), 1);
  check("is_draft_b(rori) = 0", gen_isa_is_draft_b(enc_i(0x601, 5, 1, 3)), 0);
  gen_isa_set_time(1000);
  check("cycle CSR follows set_time", gen_isa_read_csr(CSR_CYCLE), 1000);
  check("mcycle follows set_time", gen_isa_read_csr(CSR_MCYCLE), 1000);
  gen_isa_set_hpm(2, 0x1234u, 1u);
  check("mhpmcounter5 follows set_hpm (lo)", gen_isa_read_csr(CSR_MHPMCOUNTER5), 0x1234u);
  check("mhpmcounter5h follows set_hpm (hi)", gen_isa_read_csr(CSR_MHPMCOUNTER5H), 1u);
  check("hpmcounter5 alias follows", gen_isa_read_csr(CSR_HPMCOUNTER5), 0x1234u);
  gen_isa_set_status(1);
  check("cpuctrlsts bit 8 follows ic_scr_key_valid", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS), 0x100u);
  gen_isa_write_csr(GEN_CSR_CPUCTRLSTS, 0x1ffu);
  check("cpuctrlsts write: control bits taken, bit 8 is status", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS), 0x1ffu);
  gen_isa_set_status(0);
  check("cpuctrlsts bit 8 cleared by status", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS), 0xffu);

  std::puts("-- 6. T-102: prv_before is the privilege the instruction executed in (rvfi_mode's meaning)");
  check("re-reset", gen_isa_reset(&cfg) == 0, 1);
  { const uint32_t prog3[] = {GEN_INSN_MRET, 0x00000013u, 0x00000013u, 0x00000013u, 0x00000073u};   // mret ; nops ; ecall in U
    for (unsigned i = 0; i < sizeof(prog3) / 4; i++) gen_isa_write_word(scratch + 4 * i, prog3[i]);
    gen_isa_write_csr(CSR_MEPC, scratch + 16u);   // mepc -> the ecall; mstatus.MPP is U after reset
    gen_isa_write_csr(CSR_PMPADDR0, 0xffffffffu); gen_isa_write_csr(CSR_PMPCFG0, 0x0fu);   // pmp0 TOR RWX over everything: U-mode fetch and ecall, not an access fault (plan C-2)
    gen_isa_step(&st);
    check("mret retires", st.retired, 1);
    check("mret prv_before = M", st.prv_before, 3);
    check("mret prv (after) = U", st.prv, 0);
    check("mret pc_after = mepc", st.pc_after, scratch + 16u);
    gen_isa_step(&st);
    check("ecall from U traps", st.trap, 1);
    check("ecall cause 8 (U)", st.trap_cause, 8);
    check("ecall prv_before = U", st.prv_before, 0);
    check("ecall prv (after) = M", st.prv, 3); }

  std::puts("-- 7. T-102: cpuctrlsts sync_exc_seen / double_fault_seen follow the model's traps (rtl/ibex_cs_registers.sv:935-943, :964-965)");
  check("re-reset", gen_isa_reset(&cfg) == 0, 1);
  gen_isa_write_word(scratch, 0x00000073u);                 // ecall in M at the reset pc
  gen_isa_write_word(GEN_MM_BOOT_PAGE, 0x00000073u);         // trap vector (mtvec base = boot page): a second ecall
  gen_isa_write_word(GEN_MM_BOOT_PAGE + 4u, GEN_INSN_MRET);  // mret, entered by set_pc
  const uint32_t kSync = 1u << GEN_CPUCTRLSTS_SYNC_EXC_SEEN_BIT, kDouble = 1u << GEN_CPUCTRLSTS_DOUBLE_FAULT_SEEN_BIT, kFlags = kSync | kDouble;
  check("flags clear after reset", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS) & kFlags, 0);
  gen_isa_step(&st);
  check("first ecall traps", st.trap, 1);
  check("sync_exc_seen set (bit 6)", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS) & kFlags, kSync);
  gen_isa_step(&st);
  check("second ecall traps", st.trap, 1);
  check("double_fault_seen set (bit 7)", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS) & kFlags, kFlags);
  gen_isa_set_pc(GEN_MM_BOOT_PAGE + 4u);
  gen_isa_step(&st);
  check("mret retires", st.retired, 1);
  check("mret clears sync_exc_seen, double_fault_seen sticky", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS) & kFlags, kDouble);
  gen_isa_write_csr(GEN_CSR_CPUCTRLSTS, 0);
  check("software clears the status bits", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS) & kFlags, 0);

  std::puts("-- 8. R10: a breakpoint exception writes mepc = the [c.]ebreak pc and mtval = 0 (rtl/ibex_controller.sv:550, :882-899)");
  check("re-reset", gen_isa_reset(&cfg) == 0, 1);
  gen_isa_write_word(scratch, 0x00100073u);                  // ebreak
  gen_isa_write_word(scratch + 4u, 0x00019002u);             // c.ebreak ; c.nop
  gen_isa_write_word(GEN_MM_BOOT_PAGE, 0x00000013u);          // trap vector: nop
  gen_isa_step(&st);
  check("ebreak traps", st.trap, 1);
  check("ebreak cause 3 (breakpoint)", st.trap_cause, 3);
  check("ebreak mtval = 0 (Ibex, spec-legal)", st.trap_tval, 0);
  check("ebreak mtval CSR = 0", gen_isa_read_csr(CSR_MTVAL), 0);
  check("ebreak mepc = its own pc", gen_isa_read_csr(CSR_MEPC), scratch);
  gen_isa_set_pc(scratch + 4u);
  gen_isa_step(&st);
  check("c.ebreak traps", st.trap, 1);
  check("c.ebreak cause 3", st.trap_cause, 3);
  check("c.ebreak mtval = 0", st.trap_tval, 0);
  check("c.ebreak mepc = its own pc (2-byte aligned)", gen_isa_read_csr(CSR_MEPC), scratch + 4u);

  std::puts("-- 9. CR6-L-4: an exception taken in debug mode sets neither sync_exc_seen nor double_fault_seen (rtl/ibex_cs_registers.sv:918)");
  check("re-reset", gen_isa_reset(&cfg) == 0, 1);
  gen_isa_write_word(scratch, 0x00000013u);                  // nop at the reset pc; the debug request pre-empts it
  gen_isa_write_word(GEN_MM_DM_HALT, 0x00000073u);            // the debug ROM's first instruction: an ecall inside debug mode
  gen_isa_arm_async(0, 0, 0, 0, 1, 0);                       // debug_req
  gen_isa_step(&st);
  check("debug entry retires nothing", st.retired, 0);
  check("debug entry parks the pc at DmHaltAddr", st.pc_after, GEN_MM_DM_HALT);
  check("flags clear after the entry", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS) & kFlags, 0);
  gen_isa_step(&st);
  check("ecall in debug mode retires nothing", st.retired, 0);
  check("ecall in debug mode leaves sync_exc_seen clear", gen_isa_read_csr(GEN_CSR_CPUCTRLSTS) & kFlags, 0);

  std::printf("GEN_UT_ISA_SHIM %s (%d failures)\n", fails ? "FAIL" : "PASS", fails);
  return fails ? 1 : 0;
}
