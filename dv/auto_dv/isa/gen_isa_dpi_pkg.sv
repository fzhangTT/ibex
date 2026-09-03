// gen_isa_dpi_pkg: SystemVerilog imports of the ISA shim (dv/auto_dv/isa/gen_isa_shim.cc, built as
// libgen_isa_shim.so and linked with -LDFLAGS). Scalar arguments only; the scoreboard (gen_scoreboard)
// is the sole caller (architecture C5.1).
package gen_isa_dpi_pkg;
  import "DPI-C" context function int gen_isa_reset_dpi(input int unsigned boot_addr, input int unsigned hart_id,
                                                        input string isa_override, input string log_path,
                                                        input int mcounteren_writable);
  import "DPI-C" context function string gen_isa_last_error();
  import "DPI-C" context function int gen_isa_load_vmem(input string path);
  import "DPI-C" context function void gen_isa_write_word(input int unsigned addr, input int unsigned word);
  import "DPI-C" context function int unsigned gen_isa_read_word(input int unsigned addr);
  import "DPI-C" context function int gen_isa_step_dpi(output int unsigned pc_before, output int unsigned pc_after,
                                                       output int unsigned insn, output int retired, output int trap,
                                                       output int unsigned trap_cause, output int unsigned trap_tval,
                                                       output int rd_we, output int unsigned rd_addr,
                                                       output int unsigned rd_wdata, output int mem_reads,
                                                       output int mem_writes, output int unsigned mem_addr,
                                                       output int unsigned mem_wdata, output int unsigned mem_rdata,
                                                       output int unsigned mem_size, output int unsigned prv,
                                                       output int csr_writes, output int reg_writes);
  import "DPI-C" context function int gen_isa_csr_write(input int i, output int unsigned addr, output int unsigned val);
  import "DPI-C" context function int gen_isa_reg_write(input int i, output int unsigned idx, output int unsigned val);
  import "DPI-C" context function int gen_isa_mem_write(input int i, output int unsigned addr, output int unsigned data,
                                                        output int unsigned size);
  import "DPI-C" context function int gen_isa_mem_read(input int i, output int unsigned addr, output int unsigned data,
                                                       output int unsigned size);
  import "DPI-C" context function int unsigned gen_isa_fetch_insn(input int unsigned pc);
  import "DPI-C" context function int unsigned gen_isa_read_csr(input int unsigned addr);
  import "DPI-C" context function int gen_isa_write_csr(input int unsigned addr, input int unsigned val);
  import "DPI-C" context function int unsigned gen_isa_read_gpr(input int idx);
  import "DPI-C" context function void gen_isa_write_gpr(input int idx, input int unsigned val);
  import "DPI-C" context function int unsigned gen_isa_get_pc();
  import "DPI-C" context function void gen_isa_set_pc(input int unsigned pc);
  import "DPI-C" context function int unsigned gen_isa_get_prv();
  import "DPI-C" context function int gen_isa_exec_reference(input int unsigned insn, input int unsigned rs1,
                                                             input int unsigned rs2, input int unsigned rs3,
                                                             output int unsigned rd);
  import "DPI-C" context function int gen_isa_is_draft_b(input int unsigned insn);
  import "DPI-C" context function void gen_isa_arm_async(input int unsigned pre_mip, input int unsigned taken_cause,
                                                         input int nmi, input int nmi_int, input int debug_req,
                                                         input int irq_valid);
  import "DPI-C" context function void gen_isa_arm_fault(input int kind, input int unsigned addr, input int unsigned size);
  import "DPI-C" context function void gen_isa_set_time(input longint unsigned mcycle);
  import "DPI-C" context function void gen_isa_note_memory_write(input int unsigned addr, input int unsigned data,
                                                                 input byte unsigned be);
endpackage
