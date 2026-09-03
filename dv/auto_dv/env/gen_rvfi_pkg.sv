// gen_rvfi_pkg: the RVFI monitor (architecture C4.1) and the scoreboard with the ISA-model comparator
// (C4.7, C5.2): one record in, one model step out, field-by-field compare with a checker id per field
// (isa_pc, isa_insn, isa_trap, isa_rd, isa_mem, isa_prv, isa_pc_next) and a knob per id; Zcmp micro-op
// records folded to their last record with the union of GPR writes and the ordered store/load lists
// compared against the model's logged accesses; draft-B ops checked against the model's pc, fetched
// instruction and operands with the shim's reference result (C5.5); interrupt and debug entries stepped
// per the C5.2 record classes. Counters and PMP models, the CSR compare and the misc checkers are later landings.
package gen_rvfi_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  import gen_cfg_pkg::*;
  import gen_export_pkg::*;
  import gen_isa_dpi_pkg::*;
  import gen_agents_pkg::*;
  `include "uvm_macros.svh"

  class gen_rvfi_txn extends uvm_sequence_item;
    logic [63:0] order;
    logic [31:0] insn;
    bit          trap, halt, intr;
    logic [1:0]  mode, ixl;
    logic [4:0]  rs1_addr, rs2_addr, rs3_addr, rd_addr;
    logic [31:0] rs1_rdata, rs2_rdata, rs3_rdata, rd_wdata;
    logic [31:0] pc_rdata, pc_wdata;
    logic [31:0] mem_addr, mem_rdata, mem_wdata;
    logic [3:0]  mem_rmask, mem_wmask;
    logic [31:0] ext_pre_mip, ext_post_mip;
    bit          ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode, ext_rf_wr_suppress;
    logic [63:0] ext_mcycle;
    bit          ext_ic_scr_key_valid, ext_irq_valid;
    bit          ext_exp_valid, ext_exp_last;
    logic [15:0] ext_exp_insn;
    int unsigned cycle;
    logic [31:0] ext_mhpmcounters [10], ext_mhpmcountersh [10];   // every record: the comparator syncs the model from them; exported under the counters knob
    `uvm_object_utils_begin(gen_rvfi_txn)
      `uvm_field_int(order, UVM_ALL_ON)
      `uvm_field_int(insn, UVM_ALL_ON)
      `uvm_field_int(trap, UVM_ALL_ON)
      `uvm_field_int(intr, UVM_ALL_ON)
      `uvm_field_int(pc_rdata, UVM_ALL_ON)
      `uvm_field_int(pc_wdata, UVM_ALL_ON)
      `uvm_field_int(rd_addr, UVM_ALL_ON)
      `uvm_field_int(rd_wdata, UVM_ALL_ON)
      `uvm_field_int(cycle, UVM_ALL_ON)
    `uvm_object_utils_end
    function new(string name = "gen_rvfi_txn");
      super.new(name);
    endfunction
    function string brief();
      return $sformatf("order=%0d pc=%08h insn=%08h trap=%0b intr=%0b rd=x%0d/%08h mem=%08h w%b r%b mode=%0d cyc=%0d",
                       order, pc_rdata, insn, trap, intr, rd_addr, rd_wdata, mem_addr, mem_wmask, mem_rmask, mode, cycle);
    endfunction
  endclass

  `include "gen_export_record_line.svh"

  // ------------------------------------------------------------------------------------------
  // The model of record after one RVFI record was processed (published by gen_scoreboard on ap_state);
  // the irq/debug/misc checkers consume this, never the shim directly.
  class gen_model_state extends uvm_sequence_item;
    logic [63:0] order;
    int unsigned cycle;          // cycle of the record
    logic [31:0] pc_after, insn;
    logic [31:0] mie, mstatus, mcause, mepc, mtval, dcsr, dpc;
    logic [1:0]  prv;            // privilege after the record
    logic [31:0] pc_rdata;       // the DUT record's pc
    logic [1:0]  mode;           // the DUT record's privilege
    logic [31:0] pre_mip, post_mip;   // the record's rvfi_ext mip samples
    bit          nmi_pend, nmi_int_pend;
    int          entry_cause;         // interrupt entry: the cause the DUT's vector names (31 = NMI); -1 otherwise
    bit          is_trap, is_intr, is_mret, is_dret, debug_mode, wrote_mie, wrote_mstatus;
    `uvm_object_utils_begin(gen_model_state)
      `uvm_field_int(order, UVM_ALL_ON)
      `uvm_field_int(cycle, UVM_ALL_ON)
      `uvm_field_int(pc_after, UVM_ALL_ON)
      `uvm_field_int(mie, UVM_ALL_ON)
      `uvm_field_int(mstatus, UVM_ALL_ON)
      `uvm_field_int(mcause, UVM_ALL_ON)
      `uvm_field_int(prv, UVM_ALL_ON)
    `uvm_object_utils_end
    function new(string name = "gen_model_state");
      super.new(name);
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  class gen_rvfi_monitor extends uvm_component;
    `uvm_component_utils(gen_rvfi_monitor)
    virtual gen_rvfi_if   vif;
    virtual gen_bridge_if bvif;
    gen_env_cfg cfg;
    uvm_analysis_port #(gen_rvfi_txn) ap;
    uvm_analysis_port #(gen_rvfi_txn) ap_irq;
    gen_export_sink sink;   // set by gen_env; null = no export
    int unsigned records = 0, irq_markers = 0;
    logic [63:0] last_order;
    bit          have_order = 0, dbg_mode_q = 0, irq_valid_q = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      ap = new("ap", this);
      ap_irq = new("ap_irq", this);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_rvfi_if)::get(this, "", "vif", vif)) `uvm_fatal("GEN_RVFI_MON", "vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", bvif)) `uvm_fatal("GEN_RVFI_MON", "bridge_vif not in uvm_config_db")
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_RVFI_MON", "cfg not in uvm_config_db")
    endfunction
    function bit chk_on(bit val, bit set);
      return cfg.chk_all ? val : (set && val);
    endfunction
    function gen_rvfi_txn sample();
      gen_rvfi_txn t = gen_rvfi_txn::type_id::create($sformatf("rvfi_%0d", records));
      t.order = vif.order; t.insn = vif.insn; t.trap = vif.trap; t.halt = vif.halt; t.intr = vif.intr;
      t.mode = vif.mode; t.ixl = vif.ixl;
      t.rs1_addr = vif.rs1_addr; t.rs2_addr = vif.rs2_addr; t.rs3_addr = vif.rs3_addr; t.rd_addr = vif.rd_addr;
      t.rs3_rdata = vif.rs3_rdata;
      t.rs1_rdata = vif.rs1_rdata; t.rs2_rdata = vif.rs2_rdata; t.rd_wdata = vif.rd_wdata;
      t.pc_rdata = vif.pc_rdata; t.pc_wdata = vif.pc_wdata;
      t.mem_addr = vif.mem_addr; t.mem_rdata = vif.mem_rdata; t.mem_wdata = vif.mem_wdata;
      t.mem_rmask = vif.mem_rmask; t.mem_wmask = vif.mem_wmask;
      t.ext_pre_mip = vif.ext_pre_mip; t.ext_post_mip = vif.ext_post_mip;
      t.ext_nmi = vif.ext_nmi; t.ext_nmi_int = vif.ext_nmi_int; t.ext_debug_req = vif.ext_debug_req;
      t.ext_debug_mode = vif.ext_debug_mode; t.ext_rf_wr_suppress = vif.ext_rf_wr_suppress;
      t.ext_mcycle = vif.ext_mcycle; t.ext_ic_scr_key_valid = vif.ext_ic_scr_key_valid;
      t.ext_irq_valid = vif.ext_irq_valid;
      t.ext_exp_valid = vif.ext_expanded_insn_valid; t.ext_exp_last = vif.ext_expanded_insn_last;
      t.ext_exp_insn = vif.ext_expanded_insn;
      t.cycle = vif.cycle;
      t.ext_mhpmcounters = vif.ext_mhpmcounters;
      t.ext_mhpmcountersh = vif.ext_mhpmcountersh;
      return t;
    endfunction
    task run_phase(uvm_phase phase);
      forever begin
        @(posedge vif.clk);
        if (!vif.rst_n) continue;
        if (vif.valid) begin
          gen_rvfi_txn t = sample();
          records++;
          // rvfi_order: +1 per record, never repeats; rvfi_halt never set (C4.1 row rvfi_order)
          if (have_order && chk_on(cfg.chk_rvfi_proto, cfg.chk_rvfi_proto_set) && t.order != last_order + 64'd1)
            `uvm_error("rvfi_order", $sformatf("order %0d after %0d (%s)", t.order, last_order, t.brief()))
          if (t.halt && chk_on(cfg.chk_rvfi_proto, cfg.chk_rvfi_proto_set))
            `uvm_error("rvfi_order", $sformatf("rvfi_halt set (%s)", t.brief()))
          last_order = t.order; have_order = 1;
          if (t.ext_debug_mode && !dbg_mode_q) bvif.evt_dbg_entered = ~bvif.evt_dbg_entered;
          dbg_mode_q = t.ext_debug_mode;
          if (t.intr) bvif.evt_irq_taken = ~bvif.evt_irq_taken;
          ap.write(t);
          if (sink != null && sink.enabled) sink.write_record(gen_export_record_line(t, cfg.export_counters));
          if (cfg.rvfi_trace) `uvm_info("GEN_RVFI", t.brief(), UVM_LOW)
        end
        // rvfi_ext_irq_valid is a LEVEL (X-16 / C-13): one marker per rising edge, at the rise cycle
        if (vif.ext_irq_valid && !irq_valid_q) begin
          gen_rvfi_txn m = sample();
          irq_markers++;
          ap_irq.write(m);
          if (sink != null && sink.enabled) sink.write_marker($sformatf("I %0h %0h %0h %0h %0h %0h %0h", m.cycle, m.ext_pre_mip, m.ext_post_mip,
                                                  m.ext_nmi, m.ext_nmi_int, m.ext_debug_req, m.ext_debug_mode));
        end
        irq_valid_q = vif.ext_irq_valid;
      end
    endtask
    function void report_phase(uvm_phase phase);
      `uvm_info("GEN_RVFI_MON", $sformatf("records=%0d irq_markers=%0d", records, irq_markers), UVM_LOW)
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  `uvm_analysis_imp_decl(_irq)
  class gen_scoreboard extends uvm_subscriber #(gen_rvfi_txn);
    // the irq driver's NMI raises since the previous record and during the one before it: the external-NMI classification of an
    // NMI-vector entry uses the same two-record window as the irq checker, not the record's single pin sample (CM25-L-6)
    uvm_analysis_imp_irq #(gen_irq_evt, gen_scoreboard) imp_irq;
    bit nm_raised_since = 0, nm_raised_prev = 0;
    function void write_irq(gen_irq_evt e); if (e.level && e.changed[18]) nm_raised_since = 1; endfunction
    `uvm_component_utils(gen_scoreboard)
    gen_env_cfg cfg;
    virtual gen_bridge_if bvif;
    int unsigned compared = 0, mismatches = 0, folded = 0, draft_b = 0, irq_entries = 0, dbg_entries = 0, traps = 0;
    int unsigned rmask_nonload = 0;   // RVFI observation: rmask asserted on records the model did not read for
    bit          model_ready = 0;
    bit          in_seq = 0;
    gen_rvfi_txn seq_first;
    int unsigned seq_len = 0, seq_splits = 0, faults_armed = 0, faults_unannounced = 0, breakpoints = 0, b13_odd_jalr = 0, rf_wr_suppressed = 0;
    int          entry_cause = -1;   // the current record's vector-derived interrupt cause, published with the model state
    bit          after_nmi_entry = 0;   // the previous record was an NMI entry: a vector-address record without intr is a pre-empted entry
    int unsigned nmi_preempted = 0;
    bit          dbg_q = 0, dret_q = 0;
    uvm_analysis_port #(gen_model_state) ap_state;
    function new(string name, uvm_component parent);
      super.new(name, parent); imp_irq = new("imp_irq", this);
      ap_state = new("ap_state", this);
    endfunction
    // the model of record after this record, for the boundary checkers (mie/mstatus/mcause/prv/debug and the CSR writes)
    function void publish_state(gen_rvfi_txn t, int unsigned pc_a, int unsigned prv, int csr_n, bit intr);
      gen_model_state st = gen_model_state::type_id::create("st");
      int unsigned a, v;
      st.order = t.order; st.cycle = t.cycle; st.pc_after = pc_a; st.insn = t.insn; st.prv = prv[1:0];
      st.mie = gen_isa_read_csr(ibex_pkg::CSR_MIE); st.mstatus = gen_isa_read_csr(ibex_pkg::CSR_MSTATUS);
      st.mcause = gen_isa_read_csr(ibex_pkg::CSR_MCAUSE); st.mepc = gen_isa_read_csr(ibex_pkg::CSR_MEPC);
      st.mtval = gen_isa_read_csr(ibex_pkg::CSR_MTVAL); st.dcsr = gen_isa_read_csr(ibex_pkg::CSR_DCSR); st.dpc = gen_isa_read_csr(ibex_pkg::CSR_DPC);
      st.pc_rdata = t.pc_rdata; st.mode = t.mode[1:0];
      st.is_trap = t.trap; st.is_intr = intr; st.debug_mode = t.ext_debug_mode;
      st.pre_mip = t.ext_pre_mip; st.post_mip = t.ext_post_mip; st.nmi_pend = t.ext_nmi; st.nmi_int_pend = t.ext_nmi_int;
      st.entry_cause = entry_cause; entry_cause = -1;
      st.is_mret = (t.insn == GEN_INSN_MRET); st.is_dret = (t.insn == GEN_INSN_DRET);
      for (int i = 0; i < csr_n; i++) if (gen_isa_csr_write(i, a, v) == 0) begin
        if (a == ibex_pkg::CSR_MIE) st.wrote_mie = 1;
        if (a == ibex_pkg::CSR_MSTATUS) st.wrote_mstatus = 1;
      end
      ap_state.write(st);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_SB", "cfg not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", bvif)) `uvm_fatal("GEN_SB", "bridge_vif not in uvm_config_db")
    endfunction
    function bit isa_on();
      return cfg.chk_all ? cfg.chk_isa : (cfg.chk_isa_set && cfg.chk_isa);
    endfunction
    function bit fld(bit val, bit set);
      return isa_on() && (cfg.chk_all ? val : (set && val));
    endfunction
    // RVFI reports a compressed instruction in its 16-bit form (zero-extended), so bits [1:0] give the length
    function int unsigned insn_len(logic [31:0] insn);
      return (insn[1:0] == 2'b11) ? 4 : 2;
    endfunction
    // jalr in either encoding (c.jr / c.jalr are reported in their 16-bit form: funct4 100x, rs1 != 0, rs2 = 0)
    function bit is_jalr(logic [31:0] insn);
      if (insn[1:0] == 2'b11) return insn[6:0] == ibex_pkg::OPCODE_JALR;
      return insn[1:0] == 2'b10 && insn[15:13] == 3'b100 && insn[6:2] == 5'd0 && insn[11:7] != 5'd0;
    endfunction
    // The model is built once the configuration is final: reset values, then the same image as the TB.
    function void start_of_simulation_phase(uvm_phase phase);
      int rc, n;
      super.start_of_simulation_phase(phase);
      // the model steps in every run: the irq/debug/misc checkers consume its published state; the knobs silence only
      // the isa_* rows (fld), so an isolation run of a boundary checker still has the model of record
      if (!isa_on()) `uvm_info("GEN_SB", "ISA compare rows silenced by knob; the model still steps for the boundary checkers", UVM_LOW)
      rc = gen_isa_reset_dpi(cfg.boot_addr, 0, cfg.isa_string_set ? cfg.isa_string : "",
                             cfg.isa_log_set ? cfg.isa_log : "", cfg.knob_mcounteren_writable == "on");
      if (rc != 0) `uvm_fatal("ISA_INIT", {"gen_isa_reset failed: ", gen_isa_last_error()})
      if (cfg.mem_image_set) begin
        n = gen_isa_load_vmem(cfg.mem_image);
        if (n < 0) `uvm_fatal("ISA_INIT", {"model image load failed: ", gen_isa_last_error()})
        if (n != cfg.mem_image_words) `uvm_fatal("ISA_INIT", $sformatf("model loaded %0d words, sidecar says %0d", n, cfg.mem_image_words))
      end
      model_ready = 1;
      `uvm_info("GEN_SB", $sformatf("ISA model ready: pc=%08h mtvec=%08h", gen_isa_get_pc(), gen_isa_read_csr(ibex_pkg::CSR_MTVEC)), UVM_LOW)
    endfunction

    function void miss(string id, string msg, gen_rvfi_txn t, bit en);
      if (!en) return;
      mismatches++;
      bvif.evt_isa_mismatch = mismatches[15:0];
      `uvm_error(id, {msg, " (", t.brief(), ")"})
    endfunction

    // one model step; returns 0 on shim failure (reported)
    function bit step(output int unsigned pc_b, output int unsigned pc_a, output int unsigned insn, output int retired,
                      output int trap, output int unsigned cause, output int unsigned tval, output int rd_we,
                      output int unsigned rd_addr, output int unsigned rd_wdata, output int mem_r, output int mem_w,
                      output int unsigned mem_addr, output int unsigned mem_wdata, output int unsigned mem_rdata,
                      output int unsigned mem_size, output int unsigned prv, output int unsigned prv_b, output int csr_n, output int reg_n);
      int rc = gen_isa_step_dpi(pc_b, pc_a, insn, retired, trap, cause, tval, rd_we, rd_addr, rd_wdata,
                                mem_r, mem_w, mem_addr, mem_wdata, mem_rdata, mem_size, prv, prv_b, csr_n, reg_n);
      if (rc != 0) begin
        `uvm_error("isa_step", {"model step failed: ", gen_isa_last_error()})
        return 0;
      end
      return 1;
    endfunction

    // Zcmp sequence bookkeeping: the union of the micro-op records' GPR writes, the ordered store list
    // and the ordered load addresses, compared with the model's logged writes/accesses on the last record.
    logic [31:0] seq_rd [int unsigned];
    logic [31:0] seq_st_addr [$], seq_st_data [$], seq_ld_addr [$];
    function void seq_note(gen_rvfi_txn t);
      seq_len++;
      if (t.rd_addr != 0 && !t.ext_rf_wr_suppress) seq_rd[t.rd_addr] = t.rd_wdata;
      if (t.mem_wmask != 0) begin seq_st_addr.push_back(t.mem_addr); seq_st_data.push_back(t.mem_wdata); end
      if (t.insn[6:0] == ibex_pkg::OPCODE_LOAD) seq_ld_addr.push_back(t.mem_addr);
    endfunction
    function void seq_reset(gen_rvfi_txn t);
      in_seq = 1; seq_first = t; seq_len = 0; seq_rd.delete(); seq_st_addr.delete(); seq_st_data.delete(); seq_ld_addr.delete();
    endfunction
    // C5.2 union compare after the model stepped the whole cm.* instruction (ids isa_rd, isa_mem)
    function void compare_seq_union(gen_rvfi_txn t, int reg_writes, int mem_w, int mem_r);
      int unsigned idx, val, addr, data, size;
      logic [31:0] model_rd [int unsigned];
      for (int i = 0; i < reg_writes; i++) if (gen_isa_reg_write(i, idx, val) == 0) model_rd[idx] = val;
      if (model_rd.size() != seq_rd.size())
        miss("isa_rd", $sformatf("Zcmp union: model wrote %0d registers, dut %0d", model_rd.size(), seq_rd.size()), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
      foreach (model_rd[r]) begin
        if (!seq_rd.exists(r))
          miss("isa_rd", $sformatf("Zcmp union: model wrote x%0d/%08h, dut did not", r, model_rd[r]), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
        else if (seq_rd[r] != model_rd[r])
          miss("isa_rd", $sformatf("Zcmp union: x%0d model=%08h dut=%08h", r, model_rd[r], seq_rd[r]), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
      end
      foreach (seq_rd[r]) if (!model_rd.exists(r))
        miss("isa_rd", $sformatf("Zcmp union: dut wrote x%0d/%08h, model did not", r, seq_rd[r]), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
      if (mem_w != seq_st_addr.size())
        miss("isa_mem", $sformatf("Zcmp stores: model %0d, dut %0d", mem_w, seq_st_addr.size()), t, fld(cfg.chk_isa_mem, cfg.chk_isa_mem_set));
      else for (int i = 0; i < mem_w; i++) if (gen_isa_mem_write(i, addr, data, size) == 0) begin
        if (addr != seq_st_addr[i] || data != seq_st_data[i] || size != 4)
          miss("isa_mem", $sformatf("Zcmp store %0d: model %08h<=%08h (%0d bytes) dut %08h<=%08h", i, addr, data, size, seq_st_addr[i], seq_st_data[i]), t, fld(cfg.chk_isa_mem, cfg.chk_isa_mem_set));
      end
      if (mem_r != seq_ld_addr.size())
        miss("isa_mem", $sformatf("Zcmp loads: model %0d, dut %0d", mem_r, seq_ld_addr.size()), t, fld(cfg.chk_isa_mem, cfg.chk_isa_mem_set));
      else for (int i = 0; i < mem_r; i++) if (gen_isa_mem_read(i, addr, data, size) == 0) begin
        if (addr != seq_ld_addr[i])
          miss("isa_mem", $sformatf("Zcmp load %0d: model addr %08h dut %08h", i, addr, seq_ld_addr[i]), t, fld(cfg.chk_isa_mem, cfg.chk_isa_mem_set));
      end
    endfunction

    function void write(gen_rvfi_txn t);
      int unsigned pc_b, pc_a, insn, cause, tval, rd_addr, rd_wdata, mem_addr, mem_wdata, mem_rdata, mem_size, prv, prv_b;
      int retired, trap, rd_we, mem_r, mem_w, csr_n, reg_n;
      int unsigned pc_expect, insn_expect, bytes;
      logic [31:0] gpr_before [32];   // snapshot for a suppressed register write (any encoding of the load)
      bit is_seq = 0, dbg_entry = 0, is_store, intr_now = 0, sup_ok = 0;
      if (!model_ready) return;
      // ---- asynchronous entries before this record (C5.2) come before the Zcmp fold: the handler's first record can
      //      itself be a micro-op, and an entry inside a sequence drops its partial micro-ops (the sequence restarts, R9)
      dbg_entry = t.ext_debug_mode && (!dbg_q || dret_q) && t.pc_rdata == GEN_MM_DM_HALT;   // a request held through dret re-enters at once
      dbg_q = t.ext_debug_mode; dret_q = (t.insn == GEN_INSN_DRET);
      // an interrupt entry the NMI pre-empted before the handler retired anything has no record of its own: the NMI's mepc
      // points into the handler, and the record after the NMI entry sits at a vector address without rvfi_intr (the flag
      // went to the NMI record). The model, back from the NMI's mret in the pre-entry state, takes that interrupt now.
      intr_now = t.intr;   // the entry flag the model acts on; the monitor's transaction stays the DUT's (CM25-M-1)
      if (after_nmi_entry && !t.intr && !t.trap) begin
        logic [31:0] base_v = gen_isa_read_csr(ibex_pkg::CSR_MTVEC) & ~32'hFF;
        if (t.pc_rdata >= base_v && t.pc_rdata < base_v + 32'd4 * ibex_pkg::ExcCauseIrqNm.lower_cause && gen_isa_get_pc() != t.pc_rdata) begin
          intr_now = 1'b1; nmi_preempted++;
          `uvm_info("GEN_SB", $sformatf("interrupt entry to %08h pre-empted by the NMI (no rvfi_intr of its own): entering it at order %0d", t.pc_rdata, t.order), UVM_LOW)
        end
      end
      after_nmi_entry = 0;
      if (in_seq && (intr_now || dbg_entry)) begin
        seq_splits++; in_seq = 0;
        `uvm_info("GEN_SB", $sformatf("Zcmp sequence at pc %08h split by %s entry (order %0d): %0d folded micro-ops dropped",
                                      seq_first.pc_rdata, intr_now ? "interrupt" : "debug", t.order, seq_len), UVM_LOW)
      end
      if (intr_now) begin
        // The DUT's vector names the interrupt it took (vectored mtvec: handler pc = base + 4 * cause) and the model is
        // offered exactly that bit: the record's pre_mip is sampled when the handler's first instruction is in ID,
        // after the decision, and a line released or raised in between (UNTIL_TAKEN releases the taken line at its
        // entry) makes pre_mip an unreliable record of the decision-time set. Spike still refuses an entry that is
        // not enabled (isa_trap); that the taken line was pending at the decision, and the priority among pending
        // lines, are the irq checker's rules (T-136), not the model's choice. Cause 31 (NMI) keeps pre_mip.
        logic [31:0] base = gen_isa_read_csr(ibex_pkg::CSR_MTVEC) & ~32'hFF;   // mtvec[7:0] read as 8'h01 (rtl/ibex_cs_registers.sv)
        logic [31:0] inj = t.ext_pre_mip;
        int unsigned cause = (t.pc_rdata - base) >> 2;
        bit nmi_vec = (t.pc_rdata >= base && cause == ibex_pkg::ExcCauseIrqNm.lower_cause);
        // an NMI-vector entry: the external pin (the record's nmi sample) outranks the internal cause, whose mtval is the
        // address of the corruption that set the DUT's pending bit (announced by the driver); the model emulates the entry
        bit nmi_pin = t.ext_nmi || nm_raised_since || nm_raised_prev;   // the pin in the record or raised inside the two-record window
        bit nmi_ext = nmi_vec && nmi_pin, nmi_int = nmi_vec && !nmi_pin;
        logic [31:0] nmi_mtval = nmi_int ? gen_bus_err_log::take_intg() : 32'h0;
        if (t.pc_rdata >= base && cause < ibex_pkg::ExcCauseIrqNm.lower_cause) inj = 32'h1 << cause;
        entry_cause = (t.pc_rdata >= base && cause <= ibex_pkg::ExcCauseIrqNm.lower_cause) ? int'(cause) : -1;
        bvif.evt_irq_taken_cause = entry_cause < 0 ? 5'd0 : entry_cause[4:0];
        after_nmi_entry = nmi_vec;
        gen_isa_arm_async(inj, nmi_mtval, nmi_ext, nmi_int, 1'b0, 1'b1);
        if (!step(pc_b, pc_a, insn, retired, trap, cause, tval, rd_we, rd_addr, rd_wdata, mem_r, mem_w, mem_addr, mem_wdata, mem_rdata, mem_size, prv, prv_b, csr_n, reg_n)) return;
        irq_entries++;
        if (retired != 0 || !cause[31])
          miss("isa_trap", $sformatf("interrupt entry expected, model retired %0d cause %08h", retired, cause), t, fld(cfg.chk_isa_trap, cfg.chk_isa_trap_set));
        if (pc_a != t.pc_rdata)
          miss("isa_pc", $sformatf("interrupt vector model=%08h dut=%08h", pc_a, t.pc_rdata), t, fld(cfg.chk_isa_pc, cfg.chk_isa_pc_set));
      end else if (dbg_entry) begin
        gen_isa_arm_async(t.ext_pre_mip, 32'h0, 1'b0, 1'b0, 1'b1, 1'b0);
        if (!step(pc_b, pc_a, insn, retired, trap, cause, tval, rd_we, rd_addr, rd_wdata, mem_r, mem_w, mem_addr, mem_wdata, mem_rdata, mem_size, prv, prv_b, csr_n, reg_n)) return;
        dbg_entries++;
        if (retired != 0 || pc_a != GEN_MM_DM_HALT)
          miss("isa_pc", $sformatf("debug entry expected at DmHaltAddr, model retired %0d pc=%08h", retired, pc_a), t, fld(cfg.chk_isa_pc, cfg.chk_isa_pc_set));
      end
      // ---- Zcmp: micro-op records fold to the last one (C5.1/C5.2); the unions are compared on that record
      if (t.ext_exp_valid && !t.ext_exp_last && !t.trap) begin   // a trapping micro-op ends the sequence and is compared below
        if (!in_seq) seq_reset(t);
        seq_note(t);
        folded++;
        bvif.evt_isa_records = compared + folded;
        if (intr_now || dbg_entry) publish_state(t, pc_a, prv, csr_n, intr_now);   // the entry stepped above must reach the checkers
        return;
      end
      pc_expect = t.pc_rdata; insn_expect = t.insn;
      if (t.ext_exp_valid && (t.ext_exp_last || t.trap)) begin
        // the micro-op records carry the expanded 32-bit instruction in rvfi_insn; the Zcmp encoding the
        // model executes as ONE instruction is rvfi_ext_expanded_insn (16 bits) of the sequence; a trapping
        // micro-op ends the sequence early and the model steps the whole instruction with the fault armed
        if (!in_seq) seq_reset(t);
        seq_note(t);
        pc_expect = seq_first.pc_rdata;
        insn_expect = {16'h0, t.ext_exp_insn};
        in_seq = 0;   // the last micro-op record is the compared one; only the earlier ones count as folded
        is_seq = 1;
      end
      // ---- draft-B op the model cannot execute (C5.5): every expectation comes from the MODEL (pc, fetched
      //      instruction, operands); the reference result and pc + 4 are written back into the model
      if (!t.trap && gen_isa_is_draft_b(t.insn)) begin
        int unsigned ref_rd, model_pc, model_insn, rs1_v, rs2_v, rs3_v;
        logic [4:0] rs1_i, rs2_i, rs3_i, rd_i;
        bit r_type, uses_rs3;
        model_pc = gen_isa_get_pc();
        model_insn = gen_isa_fetch_insn(model_pc);
        draft_b++; compared++;
        bvif.evt_isa_records = compared + folded;
        if (model_pc != t.pc_rdata)
          miss("isa_pc", $sformatf("draft-B pc model=%08h dut=%08h", model_pc, t.pc_rdata), t, fld(cfg.chk_isa_pc, cfg.chk_isa_pc_set));
        if (model_insn != t.insn) begin
          // the model did not fetch this instruction: no reference result, no write-back, no pc advance
          miss("isa_insn", $sformatf("draft-B insn model=%08h dut=%08h", model_insn, t.insn), t, fld(cfg.chk_isa_insn, cfg.chk_isa_insn_set));
          return;
        end
        // every operand of the reference comes from the model's own instruction word and registers
        rs1_i = model_insn[19:15]; rs2_i = model_insn[24:20]; rd_i = model_insn[11:7];
        r_type = (model_insn[6:0] == ibex_pkg::OPCODE_OP);
        rs1_v = gen_isa_read_gpr(rs1_i); rs2_v = r_type ? gen_isa_read_gpr(rs2_i) : 32'h0;
        // R4 forms (cmov/cmix/fsl/fsr and fsri) read rs3 = insn[31:27]
        uses_rs3 = model_insn[26] && (r_type || (model_insn[6:0] == ibex_pkg::OPCODE_OP_IMM && model_insn[14:12] == 3'b101));
        rs3_i = model_insn[31:27]; rs3_v = uses_rs3 ? gen_isa_read_gpr(rs3_i) : 32'h0;
        if (t.rs1_rdata != rs1_v || (r_type && t.rs2_rdata != rs2_v))
          miss("isa_rd", $sformatf("draft-B operands model rs1=%08h rs2=%08h dut rs1=%08h rs2=%08h", rs1_v, rs2_v, t.rs1_rdata, t.rs2_rdata), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
        if (uses_rs3 && (t.rs3_addr != rs3_i || t.rs3_rdata != rs3_v))
          miss("isa_rd", $sformatf("draft-B rs3 model=x%0d/%08h dut=x%0d/%08h", rs3_i, rs3_v, t.rs3_addr, t.rs3_rdata), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
        void'(gen_isa_exec_reference(model_insn, rs1_v, rs2_v, rs3_v, ref_rd));
        if (rd_i != t.rd_addr || (rd_i != 0 && ref_rd != t.rd_wdata))
          miss("isa_rd", $sformatf("draft-B rd model=x%0d/%08h dut=x%0d/%08h", rd_i, ref_rd, t.rd_addr, t.rd_wdata), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
        if (model_pc + 4 != t.pc_wdata)
          miss("isa_pc_next", $sformatf("draft-B pc_next model=%08h dut=%08h", model_pc + 4, t.pc_wdata), t, fld(cfg.chk_isa_pc_next, cfg.chk_isa_pc_next_set));
        if (rd_i != 0) gen_isa_write_gpr(rd_i, ref_rd);
        gen_isa_set_pc(model_pc + 4);
        return;
      end
      if (!intr_now && !dbg_entry) begin
        // an ordinary record: pending bits the DUT saw and still retired past are withheld from the model when they are
        // enabled (M-mode with MIE, or U-mode), since Spike would take them before this instruction; the entry itself
        // comes with the next record's intr and its own pre_mip
        logic [31:0] mie_m = gen_isa_read_csr(ibex_pkg::CSR_MIE);
        logic [31:0] mst_m = gen_isa_read_csr(ibex_pkg::CSR_MSTATUS);
        bit ien = (gen_isa_get_prv() != ibex_pkg::PRIV_LVL_M) || mst_m[ibex_pkg::CSR_MSTATUS_MIE_BIT];
        gen_isa_arm_async(ien ? (t.ext_pre_mip & ~mie_m) : t.ext_pre_mip, 32'h0, 1'b0, 1'b0, 1'b0, 1'b0);
      end
      // ---- the record itself: the model's counters and status follow the record's sampled values (ID-exit sample point,
      //      the cycle a CSR read sees). A csrr of cycle, mhpmcounterN or cpuctrlsts bit 8 under isa_rd is therefore a
      //      CONSISTENCY compare (record value == read value), not an independent check (Critic T-102 M-1): the counters
      //      belong to the counter checkers (ctr_mcycle, ctr_minstret, ctr_hpm_exact, ctr_hpm_bound; step 2d) and bit 8
      //      to the scramble-key responder's scrkey_proto status row
      gen_isa_set_time(t.ext_mcycle);
      for (int k = 0; k < GEN_MHPM_COUNTER_NUM; k++) gen_isa_set_hpm(k, t.ext_mhpmcounters[k], t.ext_mhpmcountersh[k]);
      gen_isa_set_status(t.ext_ic_scr_key_valid);
      // a trapping memory access: only a bus error the data-bus driver announced for that word becomes the model's fault on
      // the same bytes for this one step (size from funct3); otherwise the model decides alone, so a PMP denial faults on
      // both sides and a DUT fault on an access nobody corrupted is an isa_trap miss (T-137)
      if (t.trap && gen_insn_mem_access(t.insn, is_store, bytes)) begin
        logic [1:0] hit = gen_bus_err_log::take(t.mem_addr, bytes);
        if (hit != 2'b00) begin
          // Ibex's mtval is the address of the FAILING bus transaction: the effective address when the first transaction
          // of the access errors (the LSU keeps addr_last on an error, rtl/ibex_load_store_unit.sv:258, :540), the second
          // word when only the second transaction of a spanning access errors; the model takes it with the fault
          logic [31:0] tval = hit[0] ? t.mem_addr : {t.mem_addr[31:2], 2'b00} + 32'd4;
          faults_armed++;
          gen_isa_arm_fault(is_store ? GEN_ISA_FAULT_KIND_STORE : GEN_ISA_FAULT_KIND_LOAD, t.mem_addr, bytes, tval);
        end else begin
          faults_unannounced++;
          `uvm_info("GEN_SB", $sformatf("%s trap at %08h (order %0d) without a TB-injected error: the model decides",
                                        is_store ? "store" : "load", t.mem_addr, t.order), UVM_LOW)
        end
      end
      // a suppressed register write (a load whose response carried an integrity error, rtl/ibex_core.sv rvfi_ext_rf_wr_suppress):
      // the DUT keeps the destination's old value and raises the internal NMI; the model saw the clean word, so its write is
      // undone after the step and the rd compare is skipped for this record
      // (T-183 gate) accepted only when the data-bus driver announced a corruption for that load's word and the record's rd fields report
      // no write (rtl/ibex_core.sv:2379-2385 clears them with rf_we); a flag without either is an isa_rd miss, never an undo
      sup_ok = 0;
      if (t.ext_rf_wr_suppress && !is_seq) begin
        bit announced = gen_bus_err_log::take_intg_word(t.mem_addr);
        sup_ok = announced && (t.rd_addr == 0);
        if (!announced) miss("isa_rd", $sformatf("rf_wr_suppress asserted without an announced integrity corruption for %08h", t.mem_addr), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
        else if (t.rd_addr != 0) miss("isa_rd", $sformatf("rf_wr_suppress asserted but the record reports a write to x%0d", t.rd_addr), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
        if (sup_ok) for (int i = 1; i < 32; i++) gpr_before[i] = gen_isa_read_gpr(i);
      end
      if (!step(pc_b, pc_a, insn, retired, trap, cause, tval, rd_we, rd_addr, rd_wdata, mem_r, mem_w, mem_addr, mem_wdata, mem_rdata, mem_size, prv, prv_b, csr_n, reg_n)) return;
      if (sup_ok && rd_we && rd_addr != 0) begin
        gen_isa_write_gpr(rd_addr, gpr_before[rd_addr]); rf_wr_suppressed++; rd_we = 0;
      end
      compared++;
      bvif.evt_isa_records = compared + folded;   // records consumed: compared once each, Zcmp micro-ops through their fold
      if (pc_b != pc_expect)
        miss("isa_pc", $sformatf("pc model=%08h dut=%08h", pc_b, pc_expect), t, fld(cfg.chk_isa_pc, cfg.chk_isa_pc_set));
      if (insn != insn_expect)
        miss("isa_insn", $sformatf("insn model=%08h dut=%08h", insn, insn_expect), t, fld(cfg.chk_isa_insn, cfg.chk_isa_insn_set));
      if (t.trap) begin
        traps++;
        if (!(trap && retired == 0))
          miss("isa_trap", $sformatf("dut trapped, model retired %0d trap=%0d cause=%08h", retired, trap, cause), t, fld(cfg.chk_isa_trap, cfg.chk_isa_trap_set));
        // trap record: pc_wdata is pc_if = pc + length (F-RVFI-010, C-1); a fetch fault (cause 1) has no fetched length;
        // an aborted Zcmp sequence restarts from its own pc, so its offset is 0 (plan C-12, rtl-arch R9)
        if (trap && cause != 1 && t.pc_wdata != t.pc_rdata + (t.ext_exp_valid ? 0 : insn_len(t.insn)))
          miss("isa_pc_next", $sformatf("trap record pc_wdata=%08h != pc + %0d (C-1%s)", t.pc_wdata, t.ext_exp_valid ? 0 : insn_len(t.insn), t.ext_exp_valid ? ", aborted Zcmp restarts" : ""), t, fld(cfg.chk_isa_pc_next, cfg.chk_isa_pc_next_set));
        // a trapping Zcmp sequence: the accesses and register writes completed before the fault are compared as the union
        // (both sides store the highest register of rlist first: rtl/ibex_compressed_decoder.sv:626-660, Spike cm_push.h)
        if (is_seq) compare_seq_union(t, reg_n, mem_w, mem_r);
        // breakpoint exception: mepc is the [c.]ebreak's own pc and mtval is 0 (rtl-arch R10; the shim mirrors Ibex's 0)
        if (trap && cause == ibex_pkg::ExcCauseBreakpoint.lower_cause) begin
          breakpoints++;
          if (gen_isa_read_csr(ibex_pkg::CSR_MEPC) != t.pc_rdata)
            miss("isa_trap", $sformatf("breakpoint mepc model=%08h != pc %08h (R10)", gen_isa_read_csr(ibex_pkg::CSR_MEPC), t.pc_rdata), t, fld(cfg.chk_isa_trap, cfg.chk_isa_trap_set));
          if (tval != 0)
            miss("isa_trap", $sformatf("breakpoint mtval model=%08h != 0 (R10)", tval), t, fld(cfg.chk_isa_trap, cfg.chk_isa_trap_set));
        end
      end else begin
        if (retired != 1 || trap)
          miss("isa_trap", $sformatf("dut retired, model retired %0d trap=%0d cause=%08h tval=%08h", retired, trap, cause, tval), t, fld(cfg.chk_isa_trap, cfg.chk_isa_trap_set));
        if (is_seq) begin
          compare_seq_union(t, reg_n, mem_w, mem_r);
        end else begin
          if (rd_we) begin
            if (rd_addr != t.rd_addr || rd_wdata != t.rd_wdata)
              miss("isa_rd", $sformatf("rd model=x%0d/%08h dut=x%0d/%08h", rd_addr, rd_wdata, t.rd_addr, t.rd_wdata), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
          end else if (t.rd_addr != 0 && !sup_ok) begin
            miss("isa_rd", $sformatf("dut wrote x%0d/%08h, model wrote nothing", t.rd_addr, t.rd_wdata), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
          end
          begin
            // rvfi_mem_rmask is NOT gated by a load in this RTL (rvfi_mem_mask_int follows the data type on
            // every instruction, rtl/ibex_core.sv), so a DUT read is inferred from the model's access;
            // rvfi_mem_wmask is gated (data_we) and is compared directly. Counted as an RVFI observation.
            bit dut_wr  = (t.mem_wmask != 0);
            bit mdl_mem = (mem_r + mem_w) > 0;
            bit dut_mem = dut_wr || (mdl_mem && mem_w == 0);
            if (t.mem_rmask != 0 && !mdl_mem) rmask_nonload++;
            if (dut_wr != (mem_w > 0))
              miss("isa_mem", $sformatf("store model=%0d dut wmask=%b", mem_w > 0, t.mem_wmask), t, fld(cfg.chk_isa_mem, cfg.chk_isa_mem_set));
            else if (dut_mem && mem_addr != t.mem_addr)
              miss("isa_mem", $sformatf("mem addr model=%08h dut=%08h", mem_addr, t.mem_addr), t, fld(cfg.chk_isa_mem, cfg.chk_isa_mem_set));
            else if (dut_mem && t.mem_wmask == 4'hF && mem_w > 0 && mem_size == 4 && mem_wdata != t.mem_wdata)
              miss("isa_mem", $sformatf("store data model=%08h dut=%08h", mem_wdata, t.mem_wdata), t, fld(cfg.chk_isa_mem, cfg.chk_isa_mem_set));
          end
        end
        // mret/dret records: rvfi_pc_wdata is the next sequential address, never the target (plan C-1, rtl-arch R1), so the
        // convention itself is checked here and the redirect target on the NEXT record's isa_pc (model pc vs pc_rdata)
        if (t.insn == GEN_INSN_MRET || t.insn == GEN_INSN_DRET) begin
          if (t.pc_wdata != t.pc_rdata + insn_len(t.insn))
            miss("isa_pc_next", $sformatf("mret/dret record pc_wdata=%08h != pc + %0d (C-1)", t.pc_wdata, insn_len(t.insn)), t, fld(cfg.chk_isa_pc_next, cfg.chk_isa_pc_next_set));
        end else if (is_jalr(t.insn) && t.pc_wdata[0] && cfg.isa_pc_next_mask_b13) begin
          // B13 (rtl-arch R11): rvfi_pc_wdata carries the raw rs1 + imm of a jalr while the core fetches the even address
          // (rtl/ibex_core.sv:2084); bit 0 is masked and the record counted until the RTL fix (+gen_isa_pc_next_mask_b13=0
          // runs the raw rule for the expected-fail test)
          b13_odd_jalr++;
          if (pc_a != {t.pc_wdata[31:1], 1'b0})
            miss("isa_pc_next", $sformatf("pc_next model=%08h dut=%08h (bit 0 masked, B13)", pc_a, t.pc_wdata), t, fld(cfg.chk_isa_pc_next, cfg.chk_isa_pc_next_set));
        end else if (pc_a != t.pc_wdata)
          miss("isa_pc_next", $sformatf("pc_next model=%08h dut=%08h", pc_a, t.pc_wdata), t, fld(cfg.chk_isa_pc_next, cfg.chk_isa_pc_next_set));
      end
      // rvfi_mode is the privilege the instruction executed in, so the model's pre-step privilege is compared (both RISC-V encoded)
      if (prv_b[1:0] != t.mode)
        miss("isa_prv", $sformatf("priv model=%0d (before the step) dut mode=%0d", prv_b, t.mode), t, fld(cfg.chk_isa_prv, cfg.chk_isa_prv_set));
      publish_state(t, pc_a, prv, csr_n, intr_now);
      nm_raised_prev = nm_raised_since; nm_raised_since = 0;
      if (cfg.sb_trace) `uvm_info("GEN_SB", $sformatf("%s | model pc=%08h->%08h retired=%0d trap=%0d", t.brief(), pc_b, pc_a, retired, trap), UVM_LOW)
    endfunction

    function void report_phase(uvm_phase phase);
      // referee: every announced data-bus error must have been consumed by a trap record (a leftover is an injected error
      // the DUT never trapped on, or a stale announcement that could legitimise a later trap); announcements younger than the
      // drain window are still in flight at the end of the run
      if (gen_bus_err_log::leftover(bvif.cycle_count) != 0)
        `uvm_error("bus_err_leftover", $sformatf("%0d announced data-bus errors never consumed by a trap record (announced %0d, taken %0d, drain window %0d cycles)",
                                                gen_bus_err_log::leftover(bvif.cycle_count), gen_bus_err_log::announced, gen_bus_err_log::taken, GEN_BUS_ERR_DRAIN_CYCLES))
      `uvm_info("GEN_SB", $sformatf("ISA compare: records=%0d mismatches=%0d folded=%0d draft_b=%0d traps=%0d breakpoints=%0d irq_entries=%0d dbg_entries=%0d zcmp_splits=%0d faults_armed=%0d faults_unannounced=%0d bus_err_announced=%0d b13_odd_jalr=%0d rf_wr_suppressed=%0d nmi_preempted=%0d rvfi_rmask_on_nonload=%0d",
                compared, mismatches, folded, draft_b, traps, breakpoints, irq_entries, dbg_entries, seq_splits, faults_armed, faults_unannounced, gen_bus_err_log::announced, b13_odd_jalr, rf_wr_suppressed, nmi_preempted, rmask_nonload), UVM_LOW)
    endfunction
  endclass
endpackage
