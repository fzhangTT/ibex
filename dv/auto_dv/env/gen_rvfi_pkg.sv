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
  import gen_isa_dpi_pkg::*;
  `include "uvm_macros.svh"

  class gen_rvfi_txn extends uvm_sequence_item;
    logic [63:0] order;
    logic [31:0] insn;
    bit          trap, halt, intr;
    logic [1:0]  mode, ixl;
    logic [4:0]  rs1_addr, rs2_addr, rd_addr;
    logic [31:0] rs1_rdata, rs2_rdata, rd_wdata;
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

  // ------------------------------------------------------------------------------------------
  class gen_rvfi_monitor extends uvm_component;
    `uvm_component_utils(gen_rvfi_monitor)
    virtual gen_rvfi_if   vif;
    virtual gen_bridge_if bvif;
    gen_env_cfg cfg;
    uvm_analysis_port #(gen_rvfi_txn) ap;
    uvm_analysis_port #(gen_rvfi_txn) ap_irq;
    int unsigned records = 0, irq_markers = 0;
    logic [63:0] last_order;
    bit          have_order = 0, dbg_mode_q = 0;
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
      t.rs1_addr = vif.rs1_addr; t.rs2_addr = vif.rs2_addr; t.rd_addr = vif.rd_addr;
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
          if (cfg.rvfi_trace) `uvm_info("GEN_RVFI", t.brief(), UVM_LOW)
        end else if (vif.ext_irq_valid) begin
          gen_rvfi_txn t = sample();   // interrupt marker without a retirement
          irq_markers++;
          ap_irq.write(t);
        end
      end
    endtask
    function void report_phase(uvm_phase phase);
      `uvm_info("GEN_RVFI_MON", $sformatf("records=%0d irq_markers=%0d", records, irq_markers), UVM_LOW)
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  class gen_scoreboard extends uvm_subscriber #(gen_rvfi_txn);
    `uvm_component_utils(gen_scoreboard)
    gen_env_cfg cfg;
    virtual gen_bridge_if bvif;
    int unsigned compared = 0, mismatches = 0, folded = 0, draft_b = 0, irq_entries = 0, dbg_entries = 0, traps = 0;
    int unsigned rmask_nonload = 0;   // RVFI observation: rmask asserted on records the model did not read for
    bit          model_ready = 0;
    bit          in_seq = 0;
    gen_rvfi_txn seq_first;
    bit          dbg_q = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
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
    // The model is built once the configuration is final: reset values, then the same image as the TB.
    function void start_of_simulation_phase(uvm_phase phase);
      int rc, n;
      super.start_of_simulation_phase(phase);
      if (!isa_on()) begin
        `uvm_info("GEN_SB", "ISA compare disabled by knob", UVM_LOW)
        return;
      end
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
                      output int unsigned mem_size, output int unsigned prv, output int csr_n, output int reg_n);
      int rc = gen_isa_step_dpi(pc_b, pc_a, insn, retired, trap, cause, tval, rd_we, rd_addr, rd_wdata,
                                mem_r, mem_w, mem_addr, mem_wdata, mem_rdata, mem_size, prv, csr_n, reg_n);
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
      if (t.rd_addr != 0 && !t.ext_rf_wr_suppress) seq_rd[t.rd_addr] = t.rd_wdata;
      if (t.mem_wmask != 0) begin seq_st_addr.push_back(t.mem_addr); seq_st_data.push_back(t.mem_wdata); end
      if (t.insn[6:0] == ibex_pkg::OPCODE_LOAD) seq_ld_addr.push_back(t.mem_addr);
    endfunction
    function void seq_reset(gen_rvfi_txn t);
      in_seq = 1; seq_first = t; seq_rd.delete(); seq_st_addr.delete(); seq_st_data.delete(); seq_ld_addr.delete();
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
      int unsigned pc_b, pc_a, insn, cause, tval, rd_addr, rd_wdata, mem_addr, mem_wdata, mem_rdata, mem_size, prv;
      int retired, trap, rd_we, mem_r, mem_w, csr_n, reg_n;
      int unsigned pc_expect, insn_expect;
      bit is_seq = 0;
      if (!model_ready) return;
      // ---- Zcmp: micro-op records fold to the last one (C5.1/C5.2); the unions are compared on that record
      if (t.ext_exp_valid && !t.ext_exp_last) begin
        if (!in_seq) seq_reset(t);
        seq_note(t);
        folded++;
        bvif.evt_isa_records = compared + folded;
        return;
      end
      pc_expect = t.pc_rdata; insn_expect = t.insn;
      if (t.ext_exp_valid && t.ext_exp_last) begin
        // the micro-op records carry the expanded 32-bit instruction in rvfi_insn; the Zcmp encoding the
        // model executes as ONE instruction is rvfi_ext_expanded_insn (16 bits) of the sequence
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
        int unsigned ref_rd, model_pc, model_insn, rs1_v, rs2_v;
        logic [4:0] rs1_i, rs2_i, rd_i;
        bit r_type;
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
        if (t.rs1_rdata != rs1_v || (r_type && t.rs2_rdata != rs2_v))
          miss("isa_rd", $sformatf("draft-B operands model rs1=%08h rs2=%08h dut rs1=%08h rs2=%08h", rs1_v, rs2_v, t.rs1_rdata, t.rs2_rdata), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
        void'(gen_isa_exec_reference(model_insn, rs1_v, rs2_v, 32'h0, ref_rd));
        if (rd_i != t.rd_addr || (rd_i != 0 && ref_rd != t.rd_wdata))
          miss("isa_rd", $sformatf("draft-B rd model=x%0d/%08h dut=x%0d/%08h", rd_i, ref_rd, t.rd_addr, t.rd_wdata), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
        if (model_pc + 4 != t.pc_wdata)
          miss("isa_pc_next", $sformatf("draft-B pc_next model=%08h dut=%08h", model_pc + 4, t.pc_wdata), t, fld(cfg.chk_isa_pc_next, cfg.chk_isa_pc_next_set));
        if (rd_i != 0) gen_isa_write_gpr(rd_i, ref_rd);
        gen_isa_set_pc(model_pc + 4);
        return;
      end
      // ---- asynchronous entries before this record (C5.2): interrupt marker / debug request
      if (t.intr) begin
        gen_isa_arm_async(t.ext_pre_mip, 32'h0, t.ext_nmi, t.ext_nmi_int, 1'b0, 1'b1);
        if (!step(pc_b, pc_a, insn, retired, trap, cause, tval, rd_we, rd_addr, rd_wdata, mem_r, mem_w, mem_addr, mem_wdata, mem_rdata, mem_size, prv, csr_n, reg_n)) return;
        irq_entries++;
        if (retired != 0 || !cause[31])
          miss("isa_trap", $sformatf("interrupt entry expected, model retired %0d cause %08h", retired, cause), t, fld(cfg.chk_isa_trap, cfg.chk_isa_trap_set));
        if (pc_a != t.pc_rdata)
          miss("isa_pc", $sformatf("interrupt vector model=%08h dut=%08h", pc_a, t.pc_rdata), t, fld(cfg.chk_isa_pc, cfg.chk_isa_pc_set));
      end else if (t.ext_debug_mode && !dbg_q && t.pc_rdata == GEN_MM_DM_HALT) begin
        gen_isa_arm_async(t.ext_pre_mip, 32'h0, 1'b0, 1'b0, 1'b1, 1'b0);
        if (!step(pc_b, pc_a, insn, retired, trap, cause, tval, rd_we, rd_addr, rd_wdata, mem_r, mem_w, mem_addr, mem_wdata, mem_rdata, mem_size, prv, csr_n, reg_n)) return;
        dbg_entries++;
        if (retired != 0 || pc_a != GEN_MM_DM_HALT)
          miss("isa_pc", $sformatf("debug entry expected at DmHaltAddr, model retired %0d pc=%08h", retired, pc_a), t, fld(cfg.chk_isa_pc, cfg.chk_isa_pc_set));
      end else begin
        gen_isa_arm_async(t.ext_pre_mip, 32'h0, 1'b0, 1'b0, 1'b0, 1'b0);
      end
      dbg_q = t.ext_debug_mode;
      // ---- the record itself
      if (!step(pc_b, pc_a, insn, retired, trap, cause, tval, rd_we, rd_addr, rd_wdata, mem_r, mem_w, mem_addr, mem_wdata, mem_rdata, mem_size, prv, csr_n, reg_n)) return;
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
      end else begin
        if (retired != 1 || trap)
          miss("isa_trap", $sformatf("dut retired, model retired %0d trap=%0d cause=%08h tval=%08h", retired, trap, cause, tval), t, fld(cfg.chk_isa_trap, cfg.chk_isa_trap_set));
        if (is_seq) begin
          compare_seq_union(t, reg_n, mem_w, mem_r);
        end else begin
          if (rd_we) begin
            if (rd_addr != t.rd_addr || rd_wdata != t.rd_wdata)
              miss("isa_rd", $sformatf("rd model=x%0d/%08h dut=x%0d/%08h", rd_addr, rd_wdata, t.rd_addr, t.rd_wdata), t, fld(cfg.chk_isa_rd, cfg.chk_isa_rd_set));
          end else if (t.rd_addr != 0 && !t.ext_rf_wr_suppress) begin
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
        if (pc_a != t.pc_wdata)
          miss("isa_pc_next", $sformatf("pc_next model=%08h dut=%08h", pc_a, t.pc_wdata), t, fld(cfg.chk_isa_pc_next, cfg.chk_isa_pc_next_set));
      end
      // both sides carry the RISC-V privilege encoding (rvfi_mode is ibex_pkg::priv_lvl_e; Spike prv PRV_M/PRV_U)
      if (prv[1:0] != t.mode)
        miss("isa_prv", $sformatf("priv model=%0d dut mode=%0d", prv, t.mode), t, fld(cfg.chk_isa_prv, cfg.chk_isa_prv_set));
      if (cfg.sb_trace) `uvm_info("GEN_SB", $sformatf("%s | model pc=%08h->%08h retired=%0d trap=%0d", t.brief(), pc_b, pc_a, retired, trap), UVM_LOW)
    endfunction

    function void report_phase(uvm_phase phase);
      `uvm_info("GEN_SB", $sformatf("ISA compare: records=%0d mismatches=%0d folded=%0d draft_b=%0d traps=%0d irq_entries=%0d dbg_entries=%0d rvfi_rmask_on_nonload=%0d",
                compared, mismatches, folded, draft_b, traps, irq_entries, dbg_entries, rmask_nonload), UVM_LOW)
    endfunction
  endclass
endpackage
