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

  // gen_irq_mie_bit / gen_irq_line_of_cause / gen_irq_rank live in gen_agents_pkg (the driver's release rule uses them too)

  // ------------------------------------------------------------------------------------------
  class gen_irq_checker extends uvm_component;
    `uvm_component_utils(gen_irq_checker)
    virtual gen_irq_if    vif;
    virtual gen_bridge_if bvif;
    gen_env_cfg cfg;
    uvm_analysis_imp_state #(gen_model_state, gen_irq_checker) imp_state;
    uvm_analysis_imp_evt   #(gen_irq_evt, gen_irq_checker)     imp_evt;
    gen_export_sink sink;   // E misc irq_entry lines: per-entry priority decidability for the fire checks (CM25-L-3)
    int unsigned never_taken = 0;
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
    int unsigned cause_checked = 0, cause_mismatch = 0;
    // lines the driver raised / released since the last record, and during the record before it: a line raised after the
    // previous record's post_mip sample but before that record retired is in neither mip sample, so two records of driver
    // events feed the decision window
    logic [17:0] raised_since = '0, released_since = '0, raised_prev = '0, released_prev = '0;
    bit nmi_raised_since = 0, nmi_released_since = 0, nmi_raised_prev = 0, nmi_released_prev = 0;
    int unsigned priority_undecidable = 0, expect_released = 0, nmi_internal_entries = 0;
    // the DUT's internal-NMI pending bit (rtl/ibex_controller.sv:391-430): set by any data-response integrity error, cleared
    // by an NMI entry taken without an external NMI, not taken while in NMI mode; so an NMI-vector entry without a pin NMI
    // is legitimate when a corruption was announced since the last such entry consumed the bit. Announcements up to the
    // previous record are consumed by the entry (a corruption between that record and the entry may justify the next one).
    int unsigned intg_at_last = 0, intg_consumed = 0;
    // nmi_internal: an announced corruption must produce the internal NMI entry within GEN_NMI_INT_ENTRY_BOUND_RECORDS
    // records spent outside NMI mode (the DUT takes no NMI inside NMI mode); NMI mode runs from the NMI-vector entry to
    // the mret that closes it, nested traps inside it counted by depth
    bit nmi_mode = 0, intg_wait = 0;
    int nmi_depth = 0;
    int unsigned intg_wait_records = 0, nmi_internal_fail = 0;
    logic [63:0] intg_wait_order = 0;
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
    function void end_of_elaboration_phase(uvm_phase phase);   // the sink requires every emitted row to be announced (T-141)
      super.end_of_elaboration_phase(phase);
      if (sink != null) sink.register_row("misc", "irq_entry");
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
        // the taken cause is the one the DUT's vector names (the model's mcause is stale when the model did not take the
        // entry, e.g. an NMI it does not emulate); vector 31 is the NMI (external pin or internal, from an integrity error)
        bit is_nmi = (st.entry_cause == ibex_pkg::ExcCauseIrqNm.lower_cause);
        int line = (is_nmi || st.entry_cause < 0) ? -1 : gen_irq_line_of_cause(st.entry_cause);
        expect_t keep [$];
        entries_seen++;
        if (is_nmi) nmi_seen++;
        if (have_st) check_entry_cause(st, is_nmi, line);
        // the entry clears the expectations that named the taken line (or the NMI); the others stay, and their bound
        // restarts here: a lower-priority line legitimately waits while higher ones keep being taken (the priority rule
        // above judges each entry), so the bound measures the quiet time after the last entry
        // per line: the entry satisfies the taken line (or the NMI) of an expectation and leaves its other lines pending with a
        // restarted bound, so a line raised together with a taken one is still owed its own entry (CR8-M-5)
        foreach (expects[i]) begin
          if (is_nmi) expects[i].nmi = 0;
          if (line >= 0) expects[i].lines[line] = 1'b0;
          if (expects[i].lines[17:0] != 0 || expects[i].nmi) begin expects[i].order_at = st.order; keep.push_back(expects[i]); end
        end
        expects = keep;
        // irq_masked: an entry while M-mode with MIE clear and not an NMI (the state BEFORE the entry)
        if (have_st && !is_nmi && last_st.prv == ibex_pkg::PRIV_LVL_M && !last_st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT] && !last_st.debug_mode &&
            gen_chk_en(cfg, cfg.chk_irq_masked, cfg.chk_irq_masked_set))
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
          if (still && (expects[i].nmi || st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT] || st.prv != ibex_pkg::PRIV_LVL_M) && !st.debug_mode) begin
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
      // NMI mode and the internal-NMI latency bound
      if (st.is_intr && st.entry_cause == ibex_pkg::ExcCauseIrqNm.lower_cause) begin nmi_mode = 1; nmi_depth = 0; end
      else if (nmi_mode && (st.is_trap || st.is_intr)) nmi_depth++;
      else if (nmi_mode && st.is_mret && !st.is_trap) begin if (nmi_depth > 0) nmi_depth--; else nmi_mode = 0; end
      if (!intg_wait && gen_bus_err_log::intg_announced > intg_at_last) begin intg_wait = 1; intg_wait_order = st.order; intg_wait_records = 0; end
      else if (intg_wait && !nmi_mode && !st.debug_mode) begin   // handle_irq is closed in debug mode (rtl/ibex_controller.sv:498): not counted
        intg_wait_records++;
        if (intg_wait_records > GEN_NMI_INT_ENTRY_BOUND_RECORDS) begin
          nmi_internal_fail++; intg_wait = 0;
          if (gen_chk_en(cfg, cfg.chk_nmi_internal, cfg.chk_nmi_internal_set))
            `uvm_error("nmi_internal", $sformatf("no internal NMI entry within %0d records outside NMI mode of the integrity corruption announced at order %0d (now order %0d)",
                                                  GEN_NMI_INT_ENTRY_BOUND_RECORDS, intg_wait_order, st.order))
        end
      end
      last_st = st; have_st = 1; last_rec_cycle = st.cycle;
      raised_prev = raised_since; released_prev = released_since; nmi_raised_prev = nmi_raised_since; nmi_released_prev = nmi_released_since;
      intg_at_last = gen_bus_err_log::intg_announced;
      raised_since = '0; released_since = '0; nmi_raised_since = 0; nmi_released_since = 0;
    endfunction

    // T-136: the taken cause must be the highest-priority interrupt that was pending and enabled at the decision. The
    // decision lies between the previous record's post_mip and the entry record's pre_mip: a line in both samples was
    // surely pending; a line in either sample, or raised by the driver in the window, may have been.
    function void check_entry_cause(gen_model_state st, bit is_nmi, int line);
      logic [31:0] raised = '0, changed = '0;
      logic [31:0] either, both;
      logic [17:0] r_win = raised_since | raised_prev, c_win = raised_since | raised_prev | released_since | released_prev;
      bit nmi_r_win = nmi_raised_since || nmi_raised_prev, nmi_c_win = nmi_r_win || nmi_released_since || nmi_released_prev;
      bit nmi_either, nmi_both;
      string why = "";
      for (int l = 0; l < 18; l++) begin
        if (r_win[l]) raised[gen_irq_mie_bit(l)] = 1'b1;
        if (c_win[l]) changed[gen_irq_mie_bit(l)] = 1'b1;
      end
      either = (last_st.post_mip | st.pre_mip | raised) & last_st.mie;
      // a line the driver moved inside the window (released after the previous record, raised again before this one) has
      // no known level at the decision: it makes no priority claim and is counted instead
      both = last_st.post_mip & st.pre_mip & last_st.mie & ~changed;
      if ((last_st.post_mip & st.pre_mip & last_st.mie & changed) != 0) priority_undecidable++;
      if (sink != null && sink.source_on("misc") && st.is_intr && st.entry_cause >= 0)   // per-entry decidability, for a priority item's fire check
        sink.write_event(gen_export_line_misc_irq_entry(sink.cycle(), st.order[31:0], st.entry_cause[4:0], ((last_st.post_mip & st.pre_mip & last_st.mie & changed) == 0)));
      // the NMI pin in either record sample or a driver raise (the record's own internal-NMI level is the DUT's
      // self-report and counts for nothing; the injected corruption is the evidence for an internal NMI)
      nmi_either = last_st.nmi_pend || st.nmi_pend || nmi_r_win;
      nmi_both = last_st.nmi_pend && st.nmi_pend && !nmi_c_win;
      cause_checked++;
      if (is_nmi) begin
        // an NMI-vector entry with no pin NMI in the window is the internal NMI of a TB-injected data-side integrity error
        // (accepted and counted; its latency is the nmi_internal rule in write_state); otherwise a phantom NMI
        if (!nmi_either && gen_bus_err_log::intg_announced > intg_consumed) begin
          nmi_internal_entries++; intg_consumed = intg_at_last; intg_wait = 0;
        end else if (!nmi_either) why = "NMI entry without a pending NMI pin or an injected integrity error since the last NMI entry";
      end else if (line < 0) begin
        why = "cause is not an interrupt line";
      end else if (!either[gen_irq_mie_bit(line)]) begin
        why = "taken line was not pending-and-enabled";
      end else if (nmi_both) begin
        why = "an NMI pending throughout outranks it";
      end else begin
        for (int l = 0; l < 18; l++)
          if (both[gen_irq_mie_bit(l)] && gen_irq_rank(l) < gen_irq_rank(line)) why = $sformatf("line %0d pending throughout outranks it", l);
      end
      if (why != "") begin
        cause_mismatch++;
        if (gen_chk_en(cfg, is_nmi ? cfg.chk_nmi_entry : cfg.chk_irq_entry, is_nmi ? cfg.chk_nmi_entry_set : cfg.chk_irq_entry_set))
          `uvm_error(is_nmi ? "nmi_entry" : "irq_entry",
                     $sformatf("entry mcause %08h at order %0d: %s (pending-and-enabled either %08h both %08h, nmi either %0b both %0b)",
                               st.mcause, st.order, why, either, both, nmi_either, nmi_both))
      end
    endfunction

    function void write_evt(gen_irq_evt e);
      if (e.level) begin
        raised_since |= e.changed[17:0]; if (e.changed[18]) nmi_raised_since = 1;
      end else begin
        // a line the driver takes back before the DUT took it owes no entry: open expectations drop that line
        expect_t keep [$];
        released_since |= e.changed[17:0]; if (e.changed[18]) nmi_released_since = 1;
        foreach (expects[i]) begin
          expects[i].lines &= ~{1'b0, e.changed[17:0]};
          if (e.changed[18]) expects[i].nmi = 0;
          if (expects[i].lines[17:0] != 0 || expects[i].nmi) keep.push_back(expects[i]); else expect_released++;
        end
        expects = keep;
      end
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
    // end of run (CR8-M-5): a line raised, still held and enabled at the end, never taken, is an error; the per-entry bound above restarts at
    // every entry, so under a storm a starved line would otherwise never be flagged
    function void report_phase(uvm_phase phase);
      if (have_st) foreach (expects[i]) begin
        bit still = 0; logic [17:0] pins = vif.lines();
        for (int l = 0; l < 18; l++) if (expects[i].lines[l] && pins[l] && last_st.mie[gen_irq_mie_bit(l)]) still = 1;
        if (expects[i].nmi) still = vif.nm;
        if (still && (expects[i].nmi || last_st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT] || last_st.prv != ibex_pkg::PRIV_LVL_M) && !last_st.debug_mode) begin
          never_taken++;
          if (gen_chk_en(cfg, expects[i].nmi ? cfg.chk_nmi_entry : cfg.chk_irq_entry, expects[i].nmi ? cfg.chk_nmi_entry_set : cfg.chk_irq_entry_set))
            `uvm_error(expects[i].nmi ? "nmi_entry" : "irq_entry", $sformatf("lines %05h raised at cycle %0d (order %0d) still held and enabled at the end of the run, never taken (last order %0d)", expects[i].lines, expects[i].cycle, expects[i].order_at, last_st.order))
        end
      end
      `uvm_info("GEN_IRQ_CHK", $sformatf("irq_pending cycles checked=%0d mismatches=%0d; entries=%0d nmi=%0d (internal %0d, accepted on announced corruptions) cause checked=%0d mismatches=%0d priority undecidable=%0d bound failures=%0d expectations released=%0d open expectations=%0d nmi_internal bound failures=%0d",
                checked_cycles, pending_mismatch, entries_seen, nmi_seen, nmi_internal_entries, cause_checked, cause_mismatch, priority_undecidable, expect_fail, expect_released, expects.size(), nmi_internal_fail), UVM_LOW)
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
    int unsigned entries = 0, bound_fail = 0, masked_fail = 0, dret_checked = 0, dret_fail = 0;
    logic [31:0] dpc_q, dcsr_q;
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
      if (e.level && have_st && !dbg_q && !req_open) begin req_open = 1; req_order = last_order; req_cycle = e.cycle; end   // the first open request keeps the bound
    endfunction
    function void write_state(gen_model_state st);
      // dbg_dret: the record after a dret is fetched from the model's dpc in the mode dcsr.prv named (rtl/ibex_if_stage.sv:247;
      // a request held through the dret re-enters debug first and that record is the debug ROM's, judged by the entry rule)
      if (have_st && dret_q && !st.debug_mode) begin
        dret_checked++;
        if (st.pc_rdata != dpc_q || st.mode != dcsr_q[GEN_DCSR_PRV_BIT_HIGH:GEN_DCSR_PRV_BIT_LOW]) begin
          dret_fail++;
          if (gen_chk_en(cfg, cfg.chk_dbg_dret, cfg.chk_dbg_dret_set))
            `uvm_error("dbg_dret", $sformatf("record after dret (order %0d): pc %08h mode %0d, dpc %08h dcsr.prv %0d", st.order, st.pc_rdata, st.mode, dpc_q, dcsr_q[1:0]))
        end
      end
      dpc_q = st.dpc; dcsr_q = st.dcsr;
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
      `uvm_info("GEN_DBG_CHK", $sformatf("debug entries=%0d bound failures=%0d masked failures=%0d dret checked=%0d failures=%0d", entries, bound_fail, masked_fail, dret_checked, dret_fail), UVM_LOW)
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // Observed outputs: alert_internal (always 0 with RegFileECC = 0), data_tag_quiet, alert_bus (exact:
  // high in the rvalid cycle of a corrupted response and never otherwise), double_fault (a pulse exactly
  // GEN_TRAP_TO_RVFI_OFFSET cycles before a synchronous trap record that follows an earlier synchronous
  // trap with no mret between them; no other pulses; an exception taken in debug mode sets nothing,
  // rtl/ibex_cs_registers.sv:918).
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
    // crash_dump mirror: the mismatch seen at a record and the models of record on both sides of it
    bit cd_pending = 0; logic [31:0] cd_epc_seen, cd_addr_seen, cd_epc_exp, cd_addr_exp, cd_epc_prev, cd_addr_prev; logic [63:0] cd_order;
    int unsigned cd_checked = 0, cd_late = 0, cd_early = 0, cd_mismatch = 0;
    // fetch_enable: the cycle it left On (0 = never / back On) and the records seen after the drain window
    int unsigned fe_off_cycle = 0, fe_records_after_off = 0, fe_late_records = 0; bit fe_on_q = 1;
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
    function void end_of_elaboration_phase(uvm_phase phase);
      super.end_of_elaboration_phase(phase);
      if (sink == null) return;
      sink.register_row("alert", "alert_minor"); sink.register_row("alert", "alert_major_bus");
      sink.register_row("alert", "alert_major_internal"); sink.register_row("alert", "double_fault_seen");
      sink.register_row("misc", "irq_pending"); sink.register_row("misc", "core_busy");
      sink.register_row("misc", "crash_dump_current_pc"); sink.register_row("misc", "crash_dump_next_pc");
      sink.register_row("misc", "crash_dump_last_data_addr"); sink.register_row("misc", "crash_dump_exception_pc");
      sink.register_row("misc", "crash_dump_exception_addr");
    endfunction
    function void write_state(gen_model_state st);
      // crash_dump_o.exception_pc / exception_addr mirror mepc / mtval (rtl/ibex_core.sv:1329-1330). At a record's posedge the
      // mirror shows the CSR before that edge: a trap saving at the record's own edge (load/store faults) is one record LATE, the
      // next record's CSR write (GEN_CSR_WRITE_TO_RVFI_OFFSET edges ahead of its record) can show one record EARLY; both are
      // accepted by name, anything else is a crash_dump failure judged when the next state arrives
      if (cd_pending) begin
        if (cd_epc_seen == st.mepc && cd_addr_seen == st.mtval) cd_early++;
        else begin
          cd_mismatch++;
          if (gen_chk_en(cfg, cfg.chk_crash_dump, cfg.chk_crash_dump_set))
            `uvm_error("crash_dump", $sformatf("crash_dump exception_pc/exception_addr %08h/%08h at order %0d: model mepc/mtval %08h/%08h, previous %08h/%08h, next %08h/%08h",
                                               cd_epc_seen, cd_addr_seen, cd_order, cd_epc_exp, cd_addr_exp, cd_epc_prev, cd_addr_prev, st.mepc, st.mtval))
        end
        cd_pending = 0;
      end
      cd_checked++;
      if (misc.crash_dump.exception_pc != st.mepc || misc.crash_dump.exception_addr != st.mtval) begin
        if (cd_checked > 1 && misc.crash_dump.exception_pc == cd_epc_prev && misc.crash_dump.exception_addr == cd_addr_prev) cd_late++;
        else begin
          cd_pending = 1; cd_epc_seen = misc.crash_dump.exception_pc; cd_addr_seen = misc.crash_dump.exception_addr;
          cd_epc_exp = st.mepc; cd_addr_exp = st.mtval; cd_order = st.order;
        end
      end
      cd_epc_prev = st.mepc; cd_addr_prev = st.mtval;
      // fetch_en: after fetch_enable_i leaves On only the in-flight instructions retire, within GEN_FETCH_EN_DRAIN_CYCLES
      if (fe_off_cycle != 0) begin
        fe_records_after_off++;
        if (st.cycle > fe_off_cycle + GEN_FETCH_EN_DRAIN_CYCLES) begin
          fe_late_records++;
          if (gen_chk_en(cfg, cfg.chk_fetch_en, cfg.chk_fetch_en_set))
            `uvm_error("fetch_en", $sformatf("record at order %0d, cycle %0d, %0d cycles after fetch_enable_i left On at cycle %0d (drain window %0d)", st.order, st.cycle, st.cycle - fe_off_cycle, fe_off_cycle, GEN_FETCH_EN_DRAIN_CYCLES))
        end
      end
      if (st.is_mret && !st.is_trap) sync_seen = 0;
      if (st.is_trap && !st.is_intr && !st.debug_mode) begin
        bit is_store; int unsigned bytes;
        int unsigned want = st.cycle - (gen_insn_mem_access(st.insn, is_store, bytes) ? GEN_LSU_TRAP_TO_RVFI_OFFSET : GEN_TRAP_TO_RVFI_OFFSET);
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
        begin   // fetch_enable_i: remember the cycle it left On; back On clears the window
          bit fe_on = (misc.fetch_enable == ibex_pkg::IbexMuBiOn);
          if (fe_on_q && !fe_on) fe_off_cycle = misc.cycle;
          if (fe_on) fe_off_cycle = 0;
          fe_on_q = fe_on;
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
      `uvm_info("GEN_MISC", $sformatf("alert_bus hits=%0d mismatches=%0d; alert_minor hits=%0d mismatches=%0d; alert_internal hits=%0d; data_tag hits=%0d; sync traps=%0d double faults expected=%0d pulses=%0d mismatches=%0d; crash_dump checked=%0d late=%0d early=%0d mismatches=%0d; fetch_en records after off=%0d late=%0d",
                alert_bus_hits, alert_bus_mismatch, alert_minor_hits, alert_minor_mismatch, alert_internal_hits, data_tag_hits, sync_traps, dfs_expected, dfs_pulses, dfs_mismatch, cd_checked, cd_late, cd_early, cd_mismatch, fe_records_after_off, fe_late_records), UVM_LOW)
    endfunction
  endclass
endpackage
