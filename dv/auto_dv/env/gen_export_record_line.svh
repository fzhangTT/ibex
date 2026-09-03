// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml (export_record_fields); do not edit.
// Included inside gen_rvfi_pkg after class gen_rvfi_txn: the export's R line in the header's field order (all hex).
function automatic string gen_export_record_line(gen_rvfi_txn t, bit counters);
  string s;
  s = $sformatf("R %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h", t.order, t.pc_rdata, t.pc_wdata, t.insn, t.trap, t.halt, t.intr, t.mode, t.ixl, t.rs1_addr, t.rs1_rdata, t.rs2_addr, t.rs2_rdata, t.rs3_addr, t.rs3_rdata, t.rd_addr, t.rd_wdata, t.mem_addr, t.mem_rmask, t.mem_wmask, t.mem_rdata, t.mem_wdata, t.ext_pre_mip, t.ext_post_mip, t.ext_nmi, t.ext_nmi_int, t.ext_debug_req, t.ext_debug_mode, t.ext_rf_wr_suppress, t.ext_ic_scr_key_valid, t.ext_irq_valid, t.ext_exp_valid, t.ext_exp_insn, t.ext_exp_last, t.ext_mcycle, t.cycle);
  if (counters)
    s = {s, $sformatf(" %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h %0h", t.ext_mhpmcounters[0], t.ext_mhpmcounters[1], t.ext_mhpmcounters[2], t.ext_mhpmcounters[3], t.ext_mhpmcounters[4], t.ext_mhpmcounters[5], t.ext_mhpmcounters[6], t.ext_mhpmcounters[7], t.ext_mhpmcounters[8], t.ext_mhpmcounters[9], t.ext_mhpmcountersh[0], t.ext_mhpmcountersh[1], t.ext_mhpmcountersh[2], t.ext_mhpmcountersh[3], t.ext_mhpmcountersh[4], t.ext_mhpmcountersh[5], t.ext_mhpmcountersh[6], t.ext_mhpmcountersh[7], t.ext_mhpmcountersh[8], t.ext_mhpmcountersh[9])};
  return s;
endfunction
