// gen_ut_isa_shim: unit test of the ISA shim (architecture C5; shim unit test 1 of the build order).
// Checks: Ibex reset legalization, the real Zc image run through the model to its tohost store (with the
// per-step register/memory accessors on its cm.push/cm.pop steps), grevi/gorci decode (ratified aliases
// execute, other immediates trap and are served by gen_isa_exec_reference), mtvec/mie/custom-CSR
// legalization, step bookkeeping.
//   gen_ut_isa_shim <path/to/prog.vmem>
#include "gen_isa_shim.h"
#include "gen_isa_shim_map.h"
#include <cstdio>
#include <cstring>

static int fails = 0;
static void check(const char* what, unsigned long long got, unsigned long long exp) {
  bool ok = got == exp;
  std::printf("%-44s got 0x%llx exp 0x%llx %s\n", what, got, exp, ok ? "OK" : "FAIL");
  if (!ok) fails++;
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
  check("pc = boot page + 0x80", gen_isa_get_pc(), GEN_MM_BOOT_PAGE + 0x80u);
  check("mtvec = boot page | 1", gen_isa_read_csr(0x305), GEN_MM_BOOT_PAGE | 1u);
  check("mstatus = 0x80 (MPIE, MPP U)", gen_isa_read_csr(0x300), 0x80u);
  check("prv M", gen_isa_get_prv(), 3);
  check("misa RV32IMCU + X (MisaXBit = 1 for BaseIsaRV32IorCHERIoT)", gen_isa_read_csr(0x301), 0x40901104u);
  check("pmpcfg0 all OFF", gen_isa_read_csr(0x3A0), 0);
  check("pmpaddr0 zero", gen_isa_read_csr(0x3B0), 0);
  check("mie zero", gen_isa_read_csr(0x304), 0);
  check("mcause zero", gen_isa_read_csr(0x342), 0);

  std::puts("-- 2. the Zc image runs to its tohost store");
  int words = gen_isa_load_vmem(argv[1]);
  check("image words", words > 0, 1);
  check("entry word j _start", gen_isa_read_word(GEN_MM_BOOT_PAGE + 0x80u), 0x0040006fu);
  gen_isa_step_t st{};
  check("step 1 ok", gen_isa_step(&st) == 0, 1);
  check("step 1 pc_before", st.pc_before, GEN_MM_BOOT_PAGE + 0x80u);
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
  const uint32_t scratch = GEN_MM_BOOT_PAGE + 0x80u;
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
  check("mtvec legalized: BASE[7:2] = 0, MODE 1", gen_isa_read_csr(0x305), 0x80001201u);   // 0x80001234 -> BASE 0x80001200
  check("csr write list has mtvec", st.csr_writes >= 1, 1);
  { uint32_t a = 0, v = 0; gen_isa_csr_write(0, &a, &v); check("csr write 0 is mtvec", a, 0x305); check("csr write 0 value legalized", v, 0x80001201u); }
  gen_isa_step(&st); gen_isa_step(&st);
  check("mie fast bit 16 sticks", gen_isa_read_csr(0x304), 0x10000u);
  gen_isa_step(&st); gen_isa_step(&st);
  check("csrw cpuctrlsts retires (no trap)", st.retired, 1);
  check("cpuctrlsts: 8 writable bits (icache_enable .. double_fault_seen), key_valid RO", gen_isa_read_csr(0x7c0), 0xffu);
  check("gpr write/read", (gen_isa_write_gpr(10, 0xdeadbeefu), gen_isa_read_gpr(10)), 0xdeadbeefu);
  check("set_pc/get_pc", (gen_isa_set_pc(0x80000100u), gen_isa_get_pc()), 0x80000100u);

  std::printf("GEN_UT_ISA_SHIM %s (%d failures)\n", fails ? "FAIL" : "PASS", fails);
  return fails ? 1 : 0;
}
