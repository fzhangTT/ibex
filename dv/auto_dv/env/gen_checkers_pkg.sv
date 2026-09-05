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
    int unsigned eor_open = 0;
    // model mie history: (effective DUT cycle, value); the compare of cycle c uses the last entry <= c
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
      gen_irq_view::clear(); gen_irq_view::push_mie(0, 32'h0);   // reset value
    endfunction
    function void end_of_elaboration_phase(uvm_phase phase);   // the sink requires every emitted row to be announced (T-141)
      super.end_of_elaboration_phase(phase);
      if (sink != null) sink.register_row("misc", "irq_entry");
    endfunction

    function logic [31:0] mie_at(int unsigned c);   // the published history, so the coverage class reads the same one
      return gen_irq_view::mie_at(c);
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
        gen_irq_view::push_mie(eff, st.mie);
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
      // entry bound: expectations older than GEN_IRQ_ENTRY_BOUND_RECORDS records. The bound measures the
      // INTERRUPT PATH, so a record on which the DUT was right to withhold must not spend it. That has to be
      // decided PER RECORD, before the expiry test: a mask that lifts before the bound expires (the global
      // enable does, exactly at the mret) would otherwise leave the whole masked window already charged, and a
      // restart tested only at expiry never sees it. Measured: every fire reports mstatus with MIE already
      // restored, so a restart at expiry cannot help.
      begin
        bit masked = nmi_mode || st.debug_mode ||
                     (!st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT] && st.prv == ibex_pkg::PRIV_LVL_M);
        if (masked) foreach (expects[i]) expects[i].order_at = st.order;
      end
      foreach (expects[i]) begin
        if (st.order - expects[i].order_at > GEN_IRQ_ENTRY_BOUND_RECORDS) begin
          // still enabled? (the line may have been released or masked meanwhile)
          bit still = 0;
          logic [17:0] pins = vif.lines();
          // NMI mode and debug mode mask every line: the expectation is neither judged nor forgotten, its bound restarts when the mask lifts
          if (nmi_mode || st.debug_mode) begin expects[i].order_at = st.order; continue; end
          for (int l = 0; l < 18; l++) if (expects[i].lines[l] && pins[l] && st.mie[gen_irq_mie_bit(l)]) still = 1;
          if (expects[i].nmi) still = vif.nm;
          if (still && (expects[i].nmi || st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT] || st.prv != ibex_pkg::PRIV_LVL_M)) begin
            expect_fail++;
            if (gen_chk_en(cfg, expects[i].nmi ? cfg.chk_nmi_entry : cfg.chk_irq_entry, expects[i].nmi ? cfg.chk_nmi_entry_set : cfg.chk_irq_entry_set))
              `uvm_error(expects[i].nmi ? "nmi_entry" : "irq_entry",
                         $sformatf("lines %05h (enable bits %08h) raised at cycle %0d (order %0d) not taken within %0d records (now order %0d, mie %08h mstatus %08h)",
                                   expects[i].lines, gen_irq_lines_to_mie_bits(expects[i].lines), expects[i].cycle, expects[i].order_at, GEN_IRQ_ENTRY_BOUND_RECORDS, st.order, st.mie, st.mstatus))
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
        gen_irq_view::push_sample(bvif.cycle_count, vif.lines(), vif.pending);   // the same sample, published
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
    // end of run: the drain gives the DUT its full entry allowance after the last stimulus, so the in-run bound is
    // the only judge and what survives here is reported open, not failed
    function void report_phase(uvm_phase phase);
      if (have_st) foreach (expects[i]) begin
        bit still = 0; logic [17:0] pins = vif.lines();
        for (int l = 0; l < 18; l++) if (expects[i].lines[l] && pins[l] && last_st.mie[gen_irq_mie_bit(l)]) still = 1;
        if (expects[i].nmi) still = vif.nm;
        if (still && (expects[i].nmi || last_st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT] || last_st.prv != ibex_pkg::PRIV_LVL_M) && !last_st.debug_mode && !nmi_mode) begin
          // The run is drained by GEN_IRQ_ENTRY_BOUND_RECORDS records after the last stimulus, so the in-run bound
          // above is the single judge: an expectation still pending here was raised inside a window the drain could
          // not close, and at the end of a run a withheld line and a not-yet-taken line are indistinguishable.
          eor_open++;
        end
      end
      `uvm_info("GEN_IRQ_CHK", $sformatf("irq_pending cycles checked=%0d mismatches=%0d; entries=%0d nmi=%0d (internal %0d, accepted on announced corruptions) cause checked=%0d mismatches=%0d priority undecidable=%0d bound failures=%0d expectations released=%0d open expectations=%0d nmi_internal bound failures=%0d open after the drain=%0d",
                checked_cycles, pending_mismatch, entries_seen, nmi_seen, nmi_internal_entries, cause_checked, cause_mismatch, priority_undecidable, expect_fail, expect_released, expects.size(), nmi_internal_fail, eor_open), UVM_LOW)
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
      // a request held through the dret re-enters debug first and that record is the debug ROM's, judged by the entry rule).
      // An interrupt enabled at the dret is taken before the instruction at dpc retires, so the record after the dret is
      // then the vector and its mode is M whatever dcsr.prv names; the resume point the entry displaced is in mepc, and a
      // wrong-target entry still fails through that.
      if (have_st && dret_q && !st.debug_mode) begin
        dret_checked++;
        if (st.is_intr) begin
          if (st.mepc != dpc_q) begin
            dret_fail++;
            if (gen_chk_en(cfg, cfg.chk_dbg_dret, cfg.chk_dbg_dret_set))
              `uvm_error("dbg_dret", $sformatf("interrupt entry at the dret target (order %0d): mepc %08h, dpc %08h", st.order, st.mepc, dpc_q))
          end
        end else if (st.pc_rdata != dpc_q || st.mode != dcsr_q[GEN_DCSR_PRV_BIT_HIGH:GEN_DCSR_PRV_BIT_LOW]) begin
          dret_fail++;
          if (gen_chk_en(cfg, cfg.chk_dbg_dret, cfg.chk_dbg_dret_set))
            `uvm_error("dbg_dret", $sformatf("record after dret (order %0d): pc %08h mode %0d, dpc %08h dcsr.prv %0d", st.order, st.pc_rdata, st.mode, dpc_q, dcsr_q[GEN_DCSR_PRV_BIT_HIGH:GEN_DCSR_PRV_BIT_LOW]))
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
    int unsigned alert_minor_injections = 0, alert_minor_qualified = 0, alert_minor_missing = 0;   // tag-RAM ECC injections judged
    int unsigned alert_minor_unobservable = 0;   // qualified tag injections whose alert window reached past the last observed cycle
    int unsigned data_injections = 0, data_hit_way = 0, data_other_way = 0, data_other_valid = 0, data_unjudged = 0, data_missing = 0, data_other_pulses = 0;   // data-RAM ECC injections judged; other_valid: a valid way that lost the compare to the other valid way
    int unsigned ab_both = 0, ab_agree = 0, ab_disagree = 0, b_lat_min = 0, b_lat_max = 0, data_ambiguous = 0, data_dup_visible = 0, data_dup_masked = 0;   // duplicate copies of the line in two ways: the injection visible (a bit rose) or masked by the OR   // form (a) against form (b) where both judged; (b)'s retirement latency; (b)'s ambiguous associations
    int unsigned held [$]; int unsigned held_pulses = 0;   // alert_minor pulses waiting for the verdicts of the data injections in their window
    int unsigned rt_cyc [$]; logic [31:0] rt_pc [$]; bit rt_disc [$]; bit rt_nmi [$];   // the retirements (cycle, pc, a control-flow discontinuity, the internal-NMI flag) form (b) reads the lookup tag from
    // cycles at which a signal was HIGH, for the window terms of CG-IC-006: a level is asked about per cycle, so a level that
    // predates the window and outlasts it counts as high inside it. Pruned to the longest window any term asks about.
    int unsigned minor_hi [$], major_hi [$];
    int unsigned uninit_sampled = 0, uninit_skipped_inject = 0, uninit_skipped_alert = 0;   // the never-written observation: sampled, and dropped because an injection or an alert shared the read's window
    gen_fcov_pkg::gen_isa_cov ic_cov;   // the CG-IC-006 sampler lives with the other covergroups; gen_env assigns this handle
    int unsigned alert_minor_lat [GEN_ICACHE_ECC_WINDOW + 1];   // pulses by (pulse cycle - injection cycle): the window as measured
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
    bit fe_off_valid = 0;   // a window opening at cycle 0 is a real window: the cycle alone cannot say so
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
      rt_cyc.push_back(st.cycle); rt_pc.push_back(st.pc_rdata);
      rt_disc.push_back(st.is_trap || st.is_intr || st.is_mret || st.is_dret || (st.pc_after != st.pc_rdata + (st.insn[1:0] == 2'b11 ? 32'd4 : 32'd2)));   // the sequential run of lines ends here
      rt_nmi.push_back(st.nmi_int_pend);   // a per-retirement RVFI flag, not a level: the quiet term reads it over the retirement window
      if (rt_cyc.size() > 512) begin void'(rt_cyc.pop_front()); void'(rt_pc.pop_front()); void'(rt_disc.pop_front()); void'(rt_nmi.pop_front()); end
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
      if (fe_off_valid) begin
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
        begin   // record the level histories declared above (their semantics are stated at the declaration)
          if (misc.alert_minor) minor_hi.push_back(misc.cycle);
          if (misc.alert_major_internal || misc.alert_major_bus) major_hi.push_back(misc.cycle);
          while (minor_hi.size() > 0 && misc.cycle > minor_hi[0] + GEN_ICACHE_RETIRE_WINDOW + GEN_ICACHE_ECC_WINDOW) void'(minor_hi.pop_front());
          while (major_hi.size() > 0 && misc.cycle > major_hi[0] + GEN_ICACHE_RETIRE_WINDOW + GEN_ICACHE_ECC_WINDOW) void'(major_hi.pop_front());
        end
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
        begin   // alert_minor: a pulse needs an ECC injection within GEN_ICACHE_ECC_WINDOW (one pulse per injection cycle: the ways read
                // together share one check), and a qualified injection owes a pulse (gen_icram_events, the grace rules). A tag injection
                // owes on any way; a data injection when its way was valid and the lookup hit it (the verdict comes with the P9 probe's tag
                // at once, or with the retirement of the fetched instruction later); one on an invalid way excuses nothing
          if (misc.alert_minor) begin
            alert_minor_hits++;
            // attributed at once when every data injection in its window has a verdict, else held until they have (the verdict arrives with
            // the retirement, after the pulse and possibly after the window)
            if (pending_in_window(misc.cycle)) begin held.push_back(misc.cycle); held_pulses++; end
            else attribute_pulse(misc.cycle);
          end
          foreach (gen_icram_events::q[i])
            if (gen_icram_events::q[i].kind == "inject_data" && !gen_icram_events::q[i].judged && misc.cycle > gen_icram_events::q[i].cycle + GEN_ICACHE_ECC_WINDOW)
              void'(judge_data(i));
          foreach (gen_icram_events::q[i])
            if (gen_icram_events::q[i].kind == "inject" && !gen_icram_events::q[i].judged && misc.cycle > gen_icram_events::q[i].cycle + GEN_ICACHE_ECC_WINDOW) begin
              gen_icram_events::q[i].judged = 1; gen_icram_events::q[i].verdict = gen_icram_events::q[i].qualified; alert_minor_injections++;
              if (gen_icram_events::q[i].qualified) alert_minor_qualified++;
            end
          resolve_held(0);
          close_owed(0);
          drain_uninit(0);
        end
        begin   // fetch_enable_i: remember the cycle it left On; back On clears the window
          bit fe_on = (misc.fetch_enable == ibex_pkg::IbexMuBiOn);
          if (fe_on_q && !fe_on) begin fe_off_cycle = misc.cycle; fe_off_valid = 1; end
          // the window's END, which the drain check never needed and a covergroup does: publish it on the
          // return to On, before the Off cycle is cleared
          if (!fe_on_q && fe_on && fe_off_valid) gen_fetch_en_windows::publish(fe_off_cycle, misc.cycle);
          if (fe_on) begin fe_off_cycle = 0; fe_off_valid = 0; end
          fe_on_q = fe_on;
        end
        if (misc.double_fault_seen) begin
          dfs_pulses++;
          dfs_cycles.push_back(misc.cycle);
          while (dfs_cycles.size() > 32) void'(dfs_cycles.pop_front());
        end
      end
    endtask
    // the hit way of a lookup at an index: the way whose stored {valid, tag} (at the read) equals {1, the lookup tag}; -1 for a miss
    function int hit_way_of(gen_icram_events::evt_t e, logic [31:0] tag);
      for (int w = 0; w < GEN_IC_NUM_WAYS; w++) if (e.valid_w[w] && e.tag_w[w] == tag) return w;
      return -1;
    endfunction
    function int hit_count_of(gen_icram_events::evt_t e, logic [31:0] tag);   // more than one: the line sits in several ways and the DUT ORs their data (rtl/ibex_icache.sv:507-513)
      int n = 0;
      for (int w = 0; w < GEN_IC_NUM_WAYS; w++) if (e.valid_w[w] && e.tag_w[w] == tag) n++;
      return n;
    endfunction
    // the verdict of a data injection on the injected way against the lookup tag: 1 owes a pulse, 0 owes none. One matching way: the
    // injected way must be it. Several (duplicate copies): the injected way must be one of them and a flipped bit must have risen, since a
    // bit cleared in one copy is restored by the OR of the others (the fetched word stays correct and no error is visible)
    function int data_verdict_of(gen_icram_events::evt_t e, logic [31:0] tag);
      int n = hit_count_of(e, tag);
      if (n == 0 || !(e.valid_w[e.way] && e.tag_w[e.way] == tag)) return 0;
      if (n == 1) return 1;
      return e.rose ? 1 : 0;
    endfunction
    function bit data_dup_of(gen_icram_events::evt_t e);   // the judged lookup found the line in more than one way (counted once, at the judgement)
      logic [31:0] tag; int unsigned lat; bit pending;
      if (gen_icram_events::probe_on && gen_icram_events::lookup_tag_at(e.cycle + 1, tag)) return hit_count_of(e, tag) > 1 && e.valid_w[e.way] && e.tag_w[e.way] == tag;
      if (tag_b(e, tag, lat, pending) == 1) return hit_count_of(e, tag) > 1 && e.valid_w[e.way] && e.tag_w[e.way] == tag;
      return 0;
    endfunction
    // form (b)'s lookup tag: the pc of the first retirement after the read whose line index is the injected index, provided it and every
    // retirement between are sequential flow: a jump, trap, interrupt entry or return retiring after the read may have been fetched before
    // it (the far program's loop-line jumps share the bodies' indices under another tag), and after one the lookup may have been squashed.
    // 1 = found (tag, latency), 0 = none yet (pending while inside GEN_ICACHE_RETIRE_WINDOW), -1 = ambiguous
    function int tag_b(gen_icram_events::evt_t e, output logic [31:0] tag, output int unsigned lat, output bit pending);
      pending = 0;
      foreach (rt_cyc[k]) begin
        if (rt_cyc[k] <= e.cycle) continue;
        if (rt_disc[k]) return -1;
        if (rt_pc[k][ibex_pkg::IC_INDEX_HI:ibex_pkg::IC_LINE_W] == e.index[ibex_pkg::IC_INDEX_W-1:0]) begin
          tag = 32'(rt_pc[k][31:ibex_pkg::IC_INDEX_HI+1]); lat = rt_cyc[k] - e.cycle;
          return 1;
        end
      end
      pending = (misc.cycle <= e.cycle + GEN_ICACHE_RETIRE_WINDOW);
      return 0;
    endfunction
    // form (a): the P9 probe's tag of the cycle after the read. 1 = the injected way is the hit way (owes a pulse), 0 = another way, a miss
    // or an invalid way (owes none), -1 = no tag recorded for that cycle, -2 = the probe is off
    function int verdict_a(gen_icram_events::evt_t e);
      logic [31:0] tag;
      if (!gen_icram_events::probe_on) return -2;
      if (!e.valid_w[e.way]) return 0;
      if (!gen_icram_events::lookup_tag_at(e.cycle + 1, tag)) return -1;
      gen_icram_events::q_set_hit(e.cycle, e.way, hit_way_of(e, tag));
      return data_verdict_of(e, tag);
    endfunction
    // form (b): the retirement tag_b finds judges the injection as the probe's tag would; -1 = unjudged (none yet: a squashed speculative
    // lookup, or the run ended), -3 = ambiguous (a discontinuity retired first)
    function int verdict_b(gen_icram_events::evt_t e, output bit pending);
      logic [31:0] tag; int unsigned lat; int r;
      pending = 0;
      if (!e.valid_w[e.way]) return 0;
      r = tag_b(e, tag, lat, pending);
      if (r < 0) return -3;
      if (r == 0) return -1;
      if (b_lat_min == 0 || lat < b_lat_min) b_lat_min = lat;
      if (lat > b_lat_max) b_lat_max = lat;
      if (!gen_icram_events::probe_on) gen_icram_events::q_set_hit(e.cycle, e.way, hit_way_of(e, tag));
      return data_verdict_of(e, tag);
    endfunction
    // the data injection's verdict once its window has passed: the probe's tag when the probe is on, else the retirement's; deferred (0)
    // while form (b) still waits for the revealing retirement, since the agreement statistics need both
    function bit judge_data(int i);
      bit pending, dup; int va = verdict_a(gen_icram_events::q[i]), vb = verdict_b(gen_icram_events::q[i], pending), v;
      if (vb == -1 && pending) return 0;
      if (vb == -3) data_ambiguous++;      // a discontinuity retired first: (b) does not attribute a tag
      v = (va >= 0) ? va : ((vb >= 0) ? vb : -1);   // the probe judges when it is on, the retirement otherwise; ambiguous or absent = unjudged
      if (va >= 0 && vb >= 0) begin ab_both++; if (va == vb) ab_agree++; else ab_disagree++; end
      gen_icram_events::q[i].judged = 1; gen_icram_events::q[i].verdict = v; gen_icram_events::q[i].verdict_b = vb; data_injections++;
      dup = (v >= 0) && data_dup_of(gen_icram_events::q[i]);
      if (dup) begin if (gen_icram_events::q[i].rose) data_dup_visible++; else data_dup_masked++; end
      `uvm_info("GEN_MISC_ECC", $sformatf("data injection cycle %0d way %0d index %0d beat %0d bits %0d: valid %0b/%0b tags %08h/%08h, hit way %0d, verdict a %0d b %0d -> %0d, pulse seen %0b, qualified %0b",
                                      gen_icram_events::q[i].cycle, gen_icram_events::q[i].way, gen_icram_events::q[i].index, gen_icram_events::q[i].beat, gen_icram_events::q[i].bits,
                                      gen_icram_events::q[i].valid_w[0], gen_icram_events::q[i].valid_w[1], gen_icram_events::q[i].tag_w[0], gen_icram_events::q[i].tag_w[1],
                                      gen_icram_events::q[i].hit_way, va, vb, v, gen_icram_events::q[i].seen, gen_icram_events::q[i].qualified), UVM_HIGH)
      if (v < 0) data_unjudged++;
      else if (v == 0) begin
        data_other_way++;
        if (!dup && gen_icram_events::q[i].valid_w[gen_icram_events::q[i].way] && gen_icram_events::q[i].hit_way >= 0 && gen_icram_events::q[i].hit_way != int'(gen_icram_events::q[i].way)) data_other_valid++;
      end else data_hit_way++;
      return 1;
    endfunction
    function int data_verdict_now(int i);   // a data injection's verdict as known now: the judged one, else the probe's (-2 off, -1 no tag)
      return gen_icram_events::q[i].judged ? gen_icram_events::q[i].verdict : verdict_a(gen_icram_events::q[i]);
    endfunction
    // the window of a pulse at p: the injections 1..GEN_ICACHE_ECC_WINDOW cycles before it (the read's own cycle is excluded: the ECC check is
    // in IC1, the cycle after the read, and a later injection at p must not take the credit)
    // a valid-way data injection inside the window ending at p whose verdict is not known yet
    function bit pending_in_window(int unsigned p);
      foreach (gen_icram_events::q[i])
        if (gen_icram_events::q[i].kind == "inject_data" && gen_icram_events::q[i].valid_w[gen_icram_events::q[i].way] && !gen_icram_events::q[i].judged &&
            p > gen_icram_events::q[i].cycle && p - gen_icram_events::q[i].cycle <= GEN_ICACHE_ECC_WINDOW && data_verdict_now(i) < 0) return 1;
      return 0;
    endfunction
    function bit held_in_window(int unsigned c);   // a held pulse inside the window of the injection at c
      foreach (held[k]) if (held[k] > c && held[k] - c <= GEN_ICACHE_ECC_WINDOW) return 1;
      return 0;
    endfunction
    // the pulse at p is credited to the nearest injection in its window that owes it and has none yet (a qualified tag injection, or a data
    // injection judged the hit way), else to the nearest one that excuses it (an unqualified tag injection: its lookup ran unchecked; a data
    // injection left unjudged); the injections of that cycle share the credit (the ways read together share one check). Nobody: a pulse without
    // an announced injection, or one every injection of the window was judged not to owe
    function void attribute_pulse(int unsigned p);
      int best = -1, best_unj = -1; int unsigned best_lat = GEN_ICACHE_ECC_WINDOW + 1, unj_lat = GEN_ICACHE_ECC_WINDOW + 1; bit announced = 0;
      foreach (gen_icram_events::q[i]) begin
        int unsigned lat;
        if (!(p > gen_icram_events::q[i].cycle && p - gen_icram_events::q[i].cycle <= GEN_ICACHE_ECC_WINDOW) || gen_icram_events::q[i].seen) continue;
        lat = p - gen_icram_events::q[i].cycle;
        if (gen_icram_events::q[i].kind == "inject") begin
          announced = 1;
          if (gen_icram_events::q[i].qualified) begin if (lat < best_lat) begin best_lat = lat; best = i; end end
          else if (lat < unj_lat) begin unj_lat = lat; best_unj = i; end
        end else if (gen_icram_events::q[i].kind == "inject_data" && gen_icram_events::q[i].valid_w[gen_icram_events::q[i].way]) begin
          announced = 1;
          if (data_verdict_now(i) == 1) begin if (lat < best_lat) begin best_lat = lat; best = i; end end
          else if (data_verdict_now(i) < 0 && lat < unj_lat) begin unj_lat = lat; best_unj = i; end
        end
      end
      if (best < 0) begin best = best_unj; best_lat = unj_lat; end
      if (best >= 0) begin
        alert_minor_lat[best_lat]++;
        foreach (gen_icram_events::q[i])
          if (gen_icram_events::q[i].cycle == gen_icram_events::q[best].cycle && !gen_icram_events::q[i].seen &&
              (gen_icram_events::q[i].kind == "inject" || (gen_icram_events::q[i].kind == "inject_data" && gen_icram_events::q[i].valid_w[gen_icram_events::q[i].way] && data_verdict_now(i) != 0)))
            begin gen_icram_events::q[i].seen = 1; gen_icram_events::q[i].pulse_cycle = p; end
      end else if (!announced) begin
        alert_minor_mismatch++;
        if (gen_chk_en(cfg, cfg.chk_alert_minor, cfg.chk_alert_minor_set))
          `uvm_error("alert_minor", $sformatf("alert_minor_o high at cycle %0d without an announced ECC injection", p))
      end else begin
        data_other_pulses++;
        if (gen_chk_en(cfg, cfg.chk_alert_minor, cfg.chk_alert_minor_set))
          `uvm_error("alert_minor", $sformatf("alert_minor_o high at cycle %0d: every ECC injection in its window was judged not to owe it (a data injection on another or an invalid way), so nothing announced this pulse", p))
      end
    endfunction
    // held pulses are attributed once no injection in their window still waits for a verdict (all of them when the run ends)
    function void resolve_held(bit final_pass);
      int unsigned keep [$];
      foreach (held[k]) if (final_pass || !pending_in_window(held[k])) attribute_pulse(held[k]); else keep.push_back(held[k]);
      held = keep;
    endfunction
    // the three queries share one arithmetic, gen_tb_pkg's gen_ic_in_window, whose boundary is pinned by unit-test cases; an
    // off-by-one there fails those cases in any run, which repeating the comparison three times here would not
    function bit minor_in_window(int unsigned c, int unsigned span);   // alert_minor_o high in c+1 .. c+span
      foreach (minor_hi[k]) if (gen_ic_in_window(minor_hi[k], c, span)) return 1;
      return 0;
    endfunction
    function bit major_in_window(int unsigned c, int unsigned span);   // either major alert output high in c+1 .. c+span
      foreach (major_hi[k]) if (gen_ic_in_window(major_hi[k], c, span)) return 1;
      return 0;
    endfunction
    // the internal-NMI flag is per RETIREMENT, so it is asked about over the retirement window; retirement_seen says whether the
    // window held any retirement at all, since a window with none cannot support a quiet claim
    function bit nmi_in_window(int unsigned c, int unsigned span, output bit retirement_seen);
      retirement_seen = 0;
      foreach (rt_cyc[k])
        if (gen_ic_in_window(rt_cyc[k], c, span)) begin
          retirement_seen = 1;
          if (rt_nmi[k]) return 1;
        end
      return 0;
    endfunction
    // CG-IC-006, one sample per closed injection: the announced event, the verdict the judge already reached and the window terms
    function void sample_injection(int i);
      gen_icram_events::evt_t e = gen_icram_events::q[i];
      bit is_data = (e.kind == "inject_data");
      bit owed = is_data ? (e.verdict == 1 && e.qualified) : e.qualified;
      bit dup_masked = is_data && e.verdict >= 0 && !e.rose && data_dup_of(e);
      bit ret_seen; bit nmi_hi = nmi_in_window(e.cycle, GEN_ICACHE_RETIRE_WINDOW, ret_seen);
      ic_cov.sample_ic_ecc_injection(is_data, e.bits, e.way, e.beat, owed && e.seen, e.en_ok, e.sweep_ok, e.verdict, dup_masked,
                                     major_in_window(e.cycle, GEN_ICACHE_ECC_WINDOW), nmi_hi, ret_seen);
    endfunction
    // the never-written data-line reads, drained from their own queue: an event is classified once its window has closed, since
    // the no-alert half is only known then, and the monitor is the only place that can see whether an injection shared the cycle
    function void drain_uninit(bit final_pass);
      gen_icram_events::uninit_t keep [$];
      foreach (gen_icram_events::uq[k]) begin
        gen_icram_events::uninit_t u = gen_icram_events::uq[k];
        bit shared_inject = 0;
        if (!final_pass && misc.cycle <= u.cycle + GEN_ICACHE_ECC_WINDOW) begin keep.push_back(u); continue; end
        foreach (gen_icram_events::q[j]) if (gen_icram_events::q[j].cycle == u.cycle) shared_inject = 1;
        if (shared_inject) uninit_skipped_inject++;                                  // that cycle's bin comes from the injection's own closure
        else if (minor_in_window(u.cycle, GEN_ICACHE_ECC_WINDOW)) uninit_skipped_alert++;   // an alert fired: not a no-alert case
        else begin
          uninit_sampled++;
          if (ic_cov != null) ic_cov.sample_ic_ecc_uninit();
        end
      end
      gen_icram_events::uq = keep;
    endfunction
    // an owed injection without a pulse is missing once no held pulse lies in its window (its pulse may be among them)
    function void close_owed(bit final_pass);
      foreach (gen_icram_events::q[i]) begin
        if (!gen_icram_events::q[i].judged || gen_icram_events::q[i].closed) continue;
        if (!final_pass && held_in_window(gen_icram_events::q[i].cycle)) continue;
        gen_icram_events::q[i].closed = 1;
        if (ic_cov != null && !gen_icram_events::q[i].sampled) begin gen_icram_events::q[i].sampled = 1; sample_injection(i); end
        // The DUT alerts one cycle after a valid lookup whose tag ECC fails, with no term for the fetch being
        // consumed or retired (rtl/ibex_icache.sv:585 gates the tag term on lookup_valid_ic1 alone). So the only
        // reason a qualified injection can lack a pulse without the DUT being at fault is that its window reached
        // past the last cycle anyone observed. In-run this is false by construction, since an injection is judged
        // only once misc.cycle has passed its window.
        if (gen_icram_events::q[i].kind == "inject" && gen_icram_events::q[i].qualified && !gen_icram_events::q[i].seen
            && (gen_icram_events::q[i].cycle + GEN_ICACHE_ECC_WINDOW > misc.cycle)) begin
          alert_minor_unobservable++;   // reported, never failed: the window outlived the last observed cycle
        end else if (gen_icram_events::q[i].kind == "inject" && gen_icram_events::q[i].qualified && !gen_icram_events::q[i].seen) begin
          alert_minor_missing++;
          if (gen_chk_en(cfg, cfg.chk_alert_minor, cfg.chk_alert_minor_set))
            `uvm_error("alert_minor", $sformatf("alert_minor_o missing within %0d cycles of the tag-RAM ECC injection at cycle %0d (way %0d index %0d)",
                                                GEN_ICACHE_ECC_WINDOW, gen_icram_events::q[i].cycle, gen_icram_events::q[i].way, gen_icram_events::q[i].index))
        end else if (gen_icram_events::q[i].kind == "inject_data" && gen_icram_events::q[i].verdict == 1 && gen_icram_events::q[i].qualified && !gen_icram_events::q[i].seen) begin
          data_missing++;
          if (gen_chk_en(cfg, cfg.chk_alert_minor, cfg.chk_alert_minor_set))
            `uvm_error("alert_minor", $sformatf("alert_minor_o missing within %0d cycles of the data-RAM ECC injection at cycle %0d (way %0d index %0d beat %0d, %0d bit(s)): the way the lookup hit",
                                                GEN_ICACHE_ECC_WINDOW, gen_icram_events::q[i].cycle, gen_icram_events::q[i].way, gen_icram_events::q[i].index, gen_icram_events::q[i].beat, gen_icram_events::q[i].bits))
        end
      end
    endfunction
    function void report_phase(uvm_phase phase);
      int unsigned data_pending = 0;   // valid-way data injections the run ended before their verdict: unjudged, reported, never failed
      foreach (gen_icram_events::q[i]) begin
        if (gen_icram_events::q[i].judged) continue;
        if (gen_icram_events::q[i].kind == "inject_data") begin
          if (gen_icram_events::q[i].valid_w[gen_icram_events::q[i].way]) begin data_pending++; data_unjudged++; end else data_other_way++;
          gen_icram_events::q[i].judged = 1; gen_icram_events::q[i].verdict = gen_icram_events::q[i].valid_w[gen_icram_events::q[i].way] ? -1 : 0; data_injections++;
        end else if (gen_icram_events::q[i].kind == "inject") begin
          gen_icram_events::q[i].judged = 1; gen_icram_events::q[i].verdict = gen_icram_events::q[i].qualified; alert_minor_injections++;
          if (gen_icram_events::q[i].qualified) alert_minor_qualified++;
        end
      end
      resolve_held(1);   // the run ends: the held pulses are attributed with the pending injections as unjudged, then the owed ones closed
      close_owed(1);
      drain_uninit(1);
      if (dfs_pulses > dfs_expected && gen_chk_en(cfg, cfg.chk_double_fault, cfg.chk_double_fault_set))
        `uvm_error("double_fault", $sformatf("%0d double_fault_seen_o pulses for %0d expected double faults", dfs_pulses, dfs_expected))
      `uvm_info("GEN_MISC", $sformatf("alert_bus hits=%0d mismatches=%0d; alert_minor hits=%0d mismatches=%0d (ecc injections judged=%0d qualified=%0d missing=%0d unobservable=%0d, pulse latencies %p; data injections judged=%0d hit_way=%0d other_or_invalid_way=%0d (other valid way %0d) unjudged=%0d (ambiguous %0d, pending at the end %0d) missing=%0d other_way_pulses=%0d held_pulses=%0d duplicate_copies visible=%0d masked=%0d; forms a/b both=%0d agree=%0d disagree=%0d, b latency %0d..%0d); alert_internal hits=%0d; data_tag hits=%0d; sync traps=%0d double faults expected=%0d pulses=%0d mismatches=%0d; crash_dump checked=%0d late=%0d early=%0d mismatches=%0d; fetch_en records after off=%0d late=%0d; uninitialised data reads reported=%0d sampled=%0d skipped(injection %0d, alert %0d) dropped=%0d",
                alert_bus_hits, alert_bus_mismatch, alert_minor_hits, alert_minor_mismatch, alert_minor_injections, alert_minor_qualified, alert_minor_missing, alert_minor_unobservable, alert_minor_lat, data_injections, data_hit_way, data_other_way, data_other_valid, data_unjudged, data_ambiguous, data_pending, data_missing, data_other_pulses, held_pulses, data_dup_visible, data_dup_masked, ab_both, ab_agree, ab_disagree, b_lat_min, b_lat_max, alert_internal_hits, data_tag_hits, sync_traps, dfs_expected, dfs_pulses, dfs_mismatch, cd_checked, cd_late, cd_early, cd_mismatch, fe_records_after_off, fe_late_records,
                gen_icram_events::uninit_reads, uninit_sampled, uninit_skipped_inject, uninit_skipped_alert, gen_icram_events::uninit_dropped), UVM_LOW)
    endfunction
  endclass
endpackage
