// gen_checkers_pkg: boundary checkers that consume the scoreboard's model of record (gen_model_state),
// the agents' events and the observed-output interface (architecture C4.2, C4.4, C4.5). Every row has
// a checker id, a `+gen_chk_<id>` knob (isolation via the rendered `_set` flags) and reports through
// `uvm_error <id>`. Timing classes follow C4.8 (v3): irq_pending windowed by GEN_CSR_WRITE_TO_RVFI_OFFSET,
// entry bounds in records, alert_bus exact, double_fault exact with GEN_TRAP_TO_RVFI_OFFSET.
package gen_checkers_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  import gen_cfg_pkg::*;
  import gen_agents_pkg::*;
  import gen_rvfi_pkg::*;
  import gen_export_pkg::*;
  `include "uvm_macros.svh"

  `uvm_analysis_imp_decl(_state)
  `uvm_analysis_imp_decl(_evt)

  function automatic bit gen_chk_en(gen_env_cfg cfg, bit val, bit set);
    return cfg.chk_all ? val : (set && val);
  endfunction

  // Interrupt-line bit i (0 sw, 1 timer, 2 ext, 3..17 fast, 18 nm) -> mie/mip bit position
  function automatic int gen_irq_mie_bit(int line);
    if (line == 0) return 3;
    if (line == 1) return 7;
    if (line == 2) return 11;
    if (line <= 17) return 16 + (line - 3);
    return -1;
  endfunction

  // ------------------------------------------------------------------------------------------
  class gen_irq_checker extends uvm_component;
    `uvm_component_utils(gen_irq_checker)
    virtual gen_irq_if    vif;
    virtual gen_bridge_if bvif;
    gen_env_cfg cfg;
    uvm_analysis_imp_state #(gen_model_state, gen_irq_checker) imp_state;
    uvm_analysis_imp_evt   #(gen_irq_evt, gen_irq_checker)     imp_evt;
    // model mie history: (effective DUT cycle, value); the compare of cycle c uses the last entry <= c
    typedef struct { int unsigned eff_cycle; logic [31:0] mie; } mie_upd_t;
    mie_upd_t mie_hist [$];
    typedef struct { int unsigned cycle; logic [17:0] pins; bit pending; } sample_t;
    sample_t pend_q [$];
    int unsigned last_rec_cycle = 0;
    // entry expectations
    typedef struct { logic [63:0] order_at; int unsigned cycle; logic [18:0] lines; bit nmi; } expect_t;
    expect_t expects [$];
    gen_model_state last_st;
    bit have_st = 0;
    int unsigned checked_cycles = 0, entries_seen = 0, expect_fail = 0, pending_mismatch = 0, nmi_seen = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      imp_state = new("imp_state", this);
      imp_evt   = new("imp_evt", this);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_irq_if)::get(this, "", "vif", vif)) `uvm_fatal("GEN_IRQ_CHK", "vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", bvif)) `uvm_fatal("GEN_IRQ_CHK", "bridge_vif not in uvm_config_db")
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_IRQ_CHK", "cfg not in uvm_config_db")
      mie_hist.push_back('{0, 32'h0});   // reset value
    endfunction

    function logic [31:0] mie_at(int unsigned c);
      logic [31:0] v = 32'h0;
      foreach (mie_hist[i]) if (mie_hist[i].eff_cycle <= c) v = mie_hist[i].mie;
      return v;
    endfunction
    function bit expected_pending(logic [17:0] pins, logic [31:0] mie);
      for (int i = 0; i < 18; i++) if (pins[i] && mie[gen_irq_mie_bit(i)]) return 1'b1;
      return 1'b0;
    endfunction

    // model state after a record: mie history (effective from commit = record cycle - offset + 1),
    // entry bookkeeping
    function void write_state(gen_model_state st);
      if (st.wrote_mie || !have_st) begin
        int unsigned eff = (st.cycle >= GEN_CSR_WRITE_TO_RVFI_OFFSET) ? st.cycle - GEN_CSR_WRITE_TO_RVFI_OFFSET + 1 : 0;
        mie_hist.push_back('{eff, st.mie});
        while (mie_hist.size() > 64) void'(mie_hist.pop_front());
      end
      if (st.is_intr) begin
        entries_seen++;
        // an entry satisfies every open expectation whose line is in the taken set (any line: the model compared the cause)
        expects.delete();
        // irq_masked: an entry while M-mode with MIE clear and not an NMI (the state BEFORE the entry)
        if (have_st && !st.mcause[30] && st.mcause[31] && last_st.prv == 2'b11 && !last_st.mstatus[3] && !last_st.debug_mode &&
            gen_chk_en(cfg, cfg.chk_irq_masked, cfg.chk_irq_masked_set) && (st.mcause & 32'h7fffffff) != 31)
          `uvm_error("irq_masked", $sformatf("interrupt entry (mcause %08h) while MIE=0 in M-mode at order %0d", st.mcause, st.order))
      end
      // entry bound: expectations older than GEN_IRQ_ENTRY_BOUND_RECORDS records
      foreach (expects[i]) begin
        if (st.order - expects[i].order_at > GEN_IRQ_ENTRY_BOUND_RECORDS) begin
          // still enabled? (the line may have been released or masked meanwhile)
          bit still = 0;
          logic [17:0] pins = vif.lines();
          for (int l = 0; l < 18; l++) if (expects[i].lines[l] && pins[l] && st.mie[gen_irq_mie_bit(l)]) still = 1;
          if (expects[i].nmi) still = vif.nm;
          if (still && (expects[i].nmi || st.mstatus[3] || st.prv != 2'b11) && !st.debug_mode) begin
            expect_fail++;
            if (gen_chk_en(cfg, expects[i].nmi ? cfg.chk_nmi_entry : cfg.chk_irq_entry, expects[i].nmi ? cfg.chk_nmi_entry_set : cfg.chk_irq_entry_set))
              `uvm_error(expects[i].nmi ? "nmi_entry" : "irq_entry",
                         $sformatf("lines %05h raised at cycle %0d (order %0d) not taken within %0d records (now order %0d, mie %08h mstatus %08h)",
                                   expects[i].lines, expects[i].cycle, expects[i].order_at, GEN_IRQ_ENTRY_BOUND_RECORDS, st.order, st.mie, st.mstatus))
          end
          expects.delete(i);
          break;
        end
      end
      last_st = st; have_st = 1; last_rec_cycle = st.cycle;
      if (st.is_intr && st.mcause == 32'h8000001f) nmi_seen++;
    endfunction

    function void write_evt(gen_irq_evt e);
      if (e.level && have_st) begin
        expect_t x;
        x.order_at = last_st.order; x.cycle = e.cycle; x.lines = e.changed; x.nmi = e.changed[18];
        expects.push_back(x);
      end
    endfunction

    // irq_pending: sampled every cycle, evaluated GEN_CSR_WRITE_TO_RVFI_OFFSET + 1 cycles later
    task run_phase(uvm_phase phase);
      forever begin
        @(posedge vif.clk);
        if (!vif.rst_n) begin pend_q.delete(); continue; end
        pend_q.push_back('{bvif.cycle_count, vif.lines()[17:0], vif.pending});
        while (pend_q.size() > 0 && pend_q[0].cycle + GEN_CSR_WRITE_TO_RVFI_OFFSET + 1 <= bvif.cycle_count) begin
          sample_t smp = pend_q.pop_front();
          bit exp = expected_pending(smp.pins, mie_at(smp.cycle));
          checked_cycles++;
          if (exp != smp.pending) begin
            pending_mismatch++;
            if (gen_chk_en(cfg, cfg.chk_irq_pending, cfg.chk_irq_pending_set))
              `uvm_error("irq_pending", $sformatf("cycle %0d: irq_pending_o=%0b expected %0b (pins %05h mie %08h)", smp.cycle, smp.pending, exp, smp.pins, mie_at(smp.cycle)))
          end
        end
      end
    endtask
    function void report_phase(uvm_phase phase);
      `uvm_info("GEN_IRQ_CHK", $sformatf("irq_pending cycles checked=%0d mismatches=%0d; entries=%0d nmi=%0d bound failures=%0d open expectations=%0d",
                checked_cycles, pending_mismatch, entries_seen, nmi_seen, expect_fail, expects.size()), UVM_LOW)
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  class gen_dbg_checker extends uvm_component;
    `uvm_component_utils(gen_dbg_checker)
    gen_env_cfg cfg;
    uvm_analysis_imp_state #(gen_model_state, gen_dbg_checker) imp_state;
    uvm_analysis_imp_evt   #(gen_irq_evt, gen_dbg_checker)     imp_evt;
    logic [63:0] req_order; int unsigned req_cycle; bit req_open = 0;
    bit dbg_q = 0, dret_q = 0, have_st = 0;
    logic [63:0] last_order;
    int unsigned entries = 0, bound_fail = 0, masked_fail = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      imp_state = new("imp_state", this);
      imp_evt   = new("imp_evt", this);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_DBG_CHK", "cfg not in uvm_config_db")
    endfunction
    function void write_evt(gen_irq_evt e);
      if (e.level && have_st && !dbg_q) begin req_open = 1; req_order = last_order; req_cycle = e.cycle; end
    endfunction
    function void write_state(gen_model_state st);
      if (st.debug_mode && (!dbg_q || dret_q)) begin   // a request held through dret re-enters at once
        entries++;
        req_open = 0;
      end
      if (req_open && st.order - req_order > GEN_DBG_ENTRY_BOUND_RECORDS) begin
        bound_fail++; req_open = 0;
        if (gen_chk_en(cfg, cfg.chk_dbg_entry, cfg.chk_dbg_entry_set))
          `uvm_error("dbg_entry", $sformatf("debug_req_i at cycle %0d (order %0d) without debug entry within %0d records (now order %0d)", req_cycle, req_order, GEN_DBG_ENTRY_BOUND_RECORDS, st.order))
      end
      if (st.is_intr && dbg_q && st.debug_mode) begin
        masked_fail++;
        if (gen_chk_en(cfg, cfg.chk_dbg_masked, cfg.chk_dbg_masked_set))
          `uvm_error("dbg_masked", $sformatf("interrupt entry (mcause %08h) while in debug mode at order %0d", st.mcause, st.order))
      end
      dbg_q = st.debug_mode; dret_q = st.is_dret; last_order = st.order; have_st = 1;
    endfunction
    function void report_phase(uvm_phase phase);
      `uvm_info("GEN_DBG_CHK", $sformatf("debug entries=%0d bound failures=%0d masked failures=%0d", entries, bound_fail, masked_fail), UVM_LOW)
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // Observed outputs: alert_internal (always 0 with RegFileECC = 0), data_tag_quiet, alert_bus (exact:
  // high in the rvalid cycle of a corrupted response and never otherwise), double_fault (a pulse exactly
  // GEN_TRAP_TO_RVFI_OFFSET cycles before a synchronous trap record that follows an earlier synchronous
  // trap with no mret between them; no other pulses).
  class gen_misc_monitor extends uvm_component;
    `uvm_component_utils(gen_misc_monitor)
    virtual gen_misc_if misc;
    virtual gen_bus_if  ibus, dbus;
    gen_env_cfg cfg;
    uvm_analysis_imp_state #(gen_model_state, gen_misc_monitor) imp_state;
    int unsigned alert_bus_hits = 0, alert_bus_mismatch = 0, alert_internal_hits = 0, data_tag_hits = 0;
    int unsigned alert_minor_hits = 0, alert_minor_mismatch = 0;
    gen_export_sink sink;   // E alert / misc lines: the levels at reset release, then every change
    bit ev_init = 0;
    logic a_minor_q, a_bus_q, a_int_q, dfs_q, irq_pend_q;
    int unsigned busy_q, cd_cur_q, cd_next_q, cd_lda_q, cd_epc_q, cd_eaddr_q;
    function void write_changes();
      int unsigned c;
      if (sink == null || !(sink.source_on("alert") || sink.source_on("misc"))) return;
      c = sink.cycle();
      if (sink.source_on("alert")) begin
        if (!ev_init || misc.alert_minor != a_minor_q) sink.write_event(gen_export_line_alert_alert_minor(c, misc.alert_minor));
        if (!ev_init || misc.alert_major_bus != a_bus_q) sink.write_event(gen_export_line_alert_alert_major_bus(c, misc.alert_major_bus));
        if (!ev_init || misc.alert_major_internal != a_int_q) sink.write_event(gen_export_line_alert_alert_major_internal(c, misc.alert_major_internal));
        if (!ev_init || misc.double_fault_seen != dfs_q) sink.write_event(gen_export_line_alert_double_fault_seen(c, misc.double_fault_seen));
      end
      if (sink.source_on("misc")) begin
        if (!ev_init || misc.irq_pending != irq_pend_q) sink.write_event(gen_export_line_misc_irq_pending(c, misc.irq_pending));
        if (!ev_init || int'(misc.core_busy) != busy_q) sink.write_event(gen_export_line_misc_core_busy(c, int'(misc.core_busy)));
        if (!ev_init || misc.crash_dump.current_pc != cd_cur_q) sink.write_event(gen_export_line_misc_crash_dump_current_pc(c, misc.crash_dump.current_pc));
        if (!ev_init || misc.crash_dump.next_pc != cd_next_q) sink.write_event(gen_export_line_misc_crash_dump_next_pc(c, misc.crash_dump.next_pc));
        if (!ev_init || misc.crash_dump.last_data_addr != cd_lda_q) sink.write_event(gen_export_line_misc_crash_dump_last_data_addr(c, misc.crash_dump.last_data_addr));
        if (!ev_init || misc.crash_dump.exception_pc != cd_epc_q) sink.write_event(gen_export_line_misc_crash_dump_exception_pc(c, misc.crash_dump.exception_pc));
        if (!ev_init || misc.crash_dump.exception_addr != cd_eaddr_q) sink.write_event(gen_export_line_misc_crash_dump_exception_addr(c, misc.crash_dump.exception_addr));
      end
      ev_init = 1;
      a_minor_q = misc.alert_minor; a_bus_q = misc.alert_major_bus; a_int_q = misc.alert_major_internal; dfs_q = misc.double_fault_seen;
      irq_pend_q = misc.irq_pending; busy_q = int'(misc.core_busy);
      cd_cur_q = misc.crash_dump.current_pc; cd_next_q = misc.crash_dump.next_pc; cd_lda_q = misc.crash_dump.last_data_addr;
      cd_epc_q = misc.crash_dump.exception_pc; cd_eaddr_q = misc.crash_dump.exception_addr;
    endfunction
    int unsigned dfs_pulses = 0, dfs_expected = 0, dfs_mismatch = 0, sync_traps = 0;
    int unsigned dfs_cycles [$];
    bit sync_seen = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      imp_state = new("imp_state", this);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_misc_if)::get(this, "", "vif", misc)) `uvm_fatal("GEN_MISC", "vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bus_if)::get(this, "", "ibus_vif", ibus)) `uvm_fatal("GEN_MISC", "ibus_vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bus_if)::get(this, "", "dbus_vif", dbus)) `uvm_fatal("GEN_MISC", "dbus_vif not in uvm_config_db")
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_MISC", "cfg not in uvm_config_db")
    endfunction
    function void write_state(gen_model_state st);
      if (st.is_mret) sync_seen = 0;
      if (st.is_trap && !st.is_intr) begin
        int unsigned want = st.cycle - GEN_TRAP_TO_RVFI_OFFSET;
        bit found = 0;
        sync_traps++;
        foreach (dfs_cycles[i]) if (dfs_cycles[i] == want) found = 1;
        if (sync_seen) begin
          dfs_expected++;
          if (!found) begin
            dfs_mismatch++;
            if (gen_chk_en(cfg, cfg.chk_double_fault, cfg.chk_double_fault_set))
              `uvm_error("double_fault", $sformatf("second synchronous trap (order %0d, cycle %0d) without a double_fault_seen_o pulse at cycle %0d", st.order, st.cycle, want))
          end
        end else if (found) begin
          dfs_mismatch++;
          if (gen_chk_en(cfg, cfg.chk_double_fault, cfg.chk_double_fault_set))
            `uvm_error("double_fault", $sformatf("double_fault_seen_o pulse at cycle %0d for a first synchronous trap (order %0d)", want, st.order))
        end
        sync_seen = 1;
      end
    endfunction
    task run_phase(uvm_phase phase);
      forever begin
        @(posedge misc.clk);
        if (!misc.rst_n) continue;
        write_changes();
        if (misc.alert_major_internal) begin
          alert_internal_hits++;
          if (gen_chk_en(cfg, cfg.chk_alert_internal, cfg.chk_alert_internal_set))
            `uvm_error("alert_internal", $sformatf("alert_major_internal_o high at cycle %0d", misc.cycle))
        end
        if (misc.data_tag_o) begin
          data_tag_hits++;
          if (gen_chk_en(cfg, cfg.chk_data_tag_quiet, cfg.chk_data_tag_quiet_set))
            `uvm_error("data_tag_quiet", $sformatf("data_tag_o high at cycle %0d", misc.cycle))
        end
        begin
          bit exp = (ibus.rvalid && ibus.intg_corrupt) || (dbus.rvalid && dbus.intg_corrupt);
          if (misc.alert_major_bus) alert_bus_hits++;
          if (misc.alert_major_bus != exp) begin
            alert_bus_mismatch++;
            if (gen_chk_en(cfg, cfg.chk_alert_bus, cfg.chk_alert_bus_set))
              `uvm_error("alert_bus", $sformatf("cycle %0d: alert_major_bus_o=%0b expected %0b (ibus rvalid %0b corrupt %0b, dbus rvalid %0b corrupt %0b)",
                         misc.cycle, misc.alert_major_bus, exp, ibus.rvalid, ibus.intg_corrupt, dbus.rvalid, dbus.intg_corrupt))
          end
        end
        begin   // alert_minor: only within GEN_ICACHE_ECC_WINDOW of an ECC injection the RAM models announced (none exist yet, so never)
          bit exp_minor = 0;
          foreach (gen_icram_events::q[i])
            if (gen_icram_events::q[i].kind == "inject" && misc.cycle >= gen_icram_events::q[i].cycle &&
                misc.cycle - gen_icram_events::q[i].cycle <= GEN_ICACHE_ECC_WINDOW) exp_minor = 1;
          if (misc.alert_minor) alert_minor_hits++;
          if (misc.alert_minor && !exp_minor) begin
            alert_minor_mismatch++;
            if (gen_chk_en(cfg, cfg.chk_alert_minor, cfg.chk_alert_minor_set))
              `uvm_error("alert_minor", $sformatf("alert_minor_o high at cycle %0d without an announced ECC injection", misc.cycle))
          end
        end
        if (misc.double_fault_seen) begin
          dfs_pulses++;
          dfs_cycles.push_back(misc.cycle);
          while (dfs_cycles.size() > 32) void'(dfs_cycles.pop_front());
        end
      end
    endtask
    function void report_phase(uvm_phase phase);
      if (dfs_pulses > dfs_expected && gen_chk_en(cfg, cfg.chk_double_fault, cfg.chk_double_fault_set))
        `uvm_error("double_fault", $sformatf("%0d double_fault_seen_o pulses for %0d expected double faults", dfs_pulses, dfs_expected))
      `uvm_info("GEN_MISC", $sformatf("alert_bus hits=%0d mismatches=%0d; alert_minor hits=%0d mismatches=%0d; alert_internal hits=%0d; data_tag hits=%0d; sync traps=%0d double faults expected=%0d pulses=%0d mismatches=%0d",
                alert_bus_hits, alert_bus_mismatch, alert_minor_hits, alert_minor_mismatch, alert_internal_hits, data_tag_hits, sync_traps, dfs_expected, dfs_pulses, dfs_mismatch), UVM_LOW)
    endfunction
  endclass
endpackage
