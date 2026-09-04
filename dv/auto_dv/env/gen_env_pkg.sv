// gen_env_pkg: the UVM environment of the generated TB (architecture C2, C9): gen_bridge (cocotb
// command consumer, MEM_PEEK over the memory model), gen_env (memory model with the image load and
// digest check, MMIO windows and the tohost watch, the two bus agents, the scramble-key responder) and
// gen_base_test (plusarg parsing, banner, end-of-test handshake). Tests differ by Python, not by UVM
// test class (DV_prompt Section 9). Configuration and command item: gen_cfg_pkg; agents: gen_agents_pkg.
package gen_env_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  import gen_cfg_pkg::*;
  import gen_mem_pkg::*;
  import gen_agents_pkg::*;
  import gen_export_pkg::*;
  import gen_fcov_pkg::*;
  import gen_rvfi_pkg::*;
  import gen_checkers_pkg::*;
  `include "uvm_macros.svh"

  // ------------------------------------------------------------------------------------------
  // gen_bridge: arms the listener, consumes one command per cmd_valid edge, publishes it on cmd_ap
  // and toggles cmd_ack the next cycle; MEM_PEEK is answered from the memory model (peek_word, no
  // side effects); a peek without a model is a collected error, never a silent 0.
  class gen_bridge extends uvm_component;
    `uvm_component_utils(gen_bridge)
    virtual gen_bridge_if vif;
    gen_env_cfg   cfg;
    gen_mem_model mem;
    uvm_analysis_port #(gen_cmd_item) cmd_ap;
    int unsigned consumed = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      cmd_ap = new("cmd_ap", this);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", vif))
        `uvm_fatal("GEN_BRIDGE", "bridge_vif not in uvm_config_db")
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg))
        `uvm_fatal("GEN_BRIDGE", "cfg not in uvm_config_db")
    endfunction
    virtual function logic [31:0] peek_word(logic [31:0] addr);
      if (mem == null) begin
        `uvm_error("GEN_BRIDGE", $sformatf("MEM_PEEK 0x%08h without a memory model", addr))
        return 32'h0;
      end
      return mem.peek_word(addr);
    endfunction
    task run_phase(uvm_phase phase);
      gen_cmd_item item;
      @(posedge vif.clk);
      vif.listener_armed = 1'b1;
      forever begin
        @(vif.cmd_valid);            // Python toggles the level once per command
        item = gen_cmd_item::type_id::create($sformatf("cmd_%0d", consumed));
        item.kind   = vif.cmd_kind;
        item.arg[0] = vif.cmd_arg0; item.arg[1] = vif.cmd_arg1;
        item.arg[2] = vif.cmd_arg2; item.arg[3] = vif.cmd_arg3;
        item.seq    = vif.cmd_seq;
        if (item.kind == GEN_CMD_MEM_PEEK) vif.peek_data = peek_word(item.arg[0]);
        cmd_ap.write(item);
        consumed++;
        @(posedge vif.clk);
        vif.cmds_consumed = consumed[15:0];
        vif.cmd_ack_seq   = item.seq;
        vif.cmd_ack       = ~vif.cmd_ack;
        `uvm_info("GEN_BRIDGE", $sformatf("cmd %s seq=%0d args=%08h %08h %08h %08h", item.kind_name(),
                  item.seq, item.arg[0], item.arg[1], item.arg[2], item.arg[3]), UVM_HIGH)
      end
    endtask
  endclass

  // ------------------------------------------------------------------------------------------
  // Bridge command dispatcher: routes each gen_cmd_item to the component that acts on it. Kinds
  // without a consumer yet (ICACHE_ECC_ARM, COV_WITNESS) are collected errors so a test cannot believe it
  // stimulated something that nothing consumed.
  class gen_cmd_dispatch extends uvm_subscriber #(gen_cmd_item);
    `uvm_component_utils(gen_cmd_dispatch)
    gen_ctrl_driver   ctrl;
    gen_export_sink   sink;
    gen_wit_cov       wit;
    gen_isa_cov       isa_cov;   // FCOV_SELFTEST / FCOV_QUERY
    gen_irq_driver    irq;
    gen_dbg_driver    dbg;
    gen_scrkey_driver scrkey;
    gen_bus_agent     ibus, dbus;
    virtual gen_bridge_if bvif;
    int unsigned routed = 0, ignored = 0, phases = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction
    function void end_of_elaboration_phase(uvm_phase phase);
      super.end_of_elaboration_phase(phase);
      if (sink != null) sink.register_row("regime", "phase");
    endfunction
    // REGIME_SET: arg0 = knob id (GEN_KNOB_ID_*), arg1 = value index. The rendered predicate decides which knobs have a
    // run-time consumer (yaml regime_set_consumer); a knob without one is a collected error, never a silent no-op.
    function void apply_knob(int id, int idx);
      string name = gen_knob_name(id), value = gen_knob_value(id, idx);
      if (name == "" || value == "") `uvm_fatal("GEN_CMD_DISPATCH", $sformatf("REGIME_SET with bad knob %0d / value %0d", id, idx))
      if (!gen_knob_regime_set_consumed(id)) begin
        `uvm_error("GEN_CMD_DISPATCH", {"REGIME_SET: no run-time consumer for ", name, " (regime_set_consumer ", gen_knob_consumer(id), ")"})
        return;
      end
      case (id)
        GEN_KNOB_ID_IMEM_GNT_DELAY, GEN_KNOB_ID_IMEM_RVALID_DELAY, GEN_KNOB_ID_IMEM_ERR_RATE, GEN_KNOB_ID_IMEM_INTG_ERR_RATE,
        GEN_KNOB_ID_IMEM_OUTSTANDING_CAP:
          if (!ibus.cfg.apply_knob(id, value)) `uvm_fatal("GEN_CMD_DISPATCH", {"ibus refused ", name})
        GEN_KNOB_ID_DMEM_GNT_DELAY, GEN_KNOB_ID_DMEM_RVALID_DELAY, GEN_KNOB_ID_DMEM_ERR_RATE, GEN_KNOB_ID_DMEM_INTG_ERR_RATE:
          if (!dbus.cfg.apply_knob(id, value)) `uvm_fatal("GEN_CMD_DISPATCH", {"dbus refused ", name})
        GEN_KNOB_ID_IRQ_REGIME, GEN_KNOB_ID_IRQ_LINE_MIX, GEN_KNOB_ID_IRQ_HOLD: irq.set_regime(id, value);
        GEN_KNOB_ID_DEBUG_REQ_REGIME: dbg.set_regime(value);
        GEN_KNOB_ID_SCR_KEY_DELAY:    scrkey.set_regime(value);
        default: `uvm_fatal("GEN_CMD_DISPATCH", {"consumed knob without a dispatcher case: ", name})   // predicate and case must agree
      endcase
      phases++;
      if (sink != null && sink.source_on("regime")) sink.write_event(gen_export_line_regime_phase(sink.cycle(), id, idx, phases));
      `uvm_info("GEN_PHASE", $sformatf("phase %0d knob=%s value=%s cycle=%0d", phases, name, value, bvif.cycle_count), UVM_LOW)
    endfunction
    function void write(gen_cmd_item t);
      case (t.kind)
        GEN_CMD_FETCH_EN:     begin ctrl.queue_fetch_en(t.arg[0]); routed++; end
        GEN_CMD_EXPORT_FLUSH: begin bvif.peek_data = sink.flush_export(); routed++; end   // the seq rides back like a MEM_PEEK word
        GEN_CMD_COV_WITNESS:  begin bvif.peek_data = wit.witness(t.arg[0], t.arg[1]); routed++; end   // arg0 item index, arg1 the issuing test's group
        GEN_CMD_FCOV_SELFTEST: begin bvif.peek_data = isa_cov.self_test(); routed++; end   // the classifier vector table: failures
        GEN_CMD_FCOV_QUERY:   begin bvif.peek_data = isa_cov.query(t.arg[0]); routed++; end    // arg0 = a sampler counter index
        GEN_CMD_IRQ_SET:      begin irq.cmd_set(t.arg[0][18:0], gen_irq_hold_e'(t.arg[1]), t.arg[2], 1'b0); routed++; end
        GEN_CMD_IRQ_CLR:      begin irq.cmd_clr(t.arg[0][18:0]); routed++; end
        GEN_CMD_NMI_PULSE:    begin irq.cmd_set(19'h40000, GEN_IRQ_HOLD_CYCLES, t.arg[0] == 0 ? 1 : t.arg[0], 1'b0); routed++; end
        GEN_CMD_DBG_REQ:      begin dbg.cmd(t.arg[0][0], t.arg[1], t.arg[2]); routed++; end
        GEN_CMD_REGIME_SET:   begin apply_knob(t.arg[0], t.arg[1]); routed++; end
        GEN_CMD_KEY_MODE:     begin scrkey.set_regime(gen_knob_value(GEN_KNOB_ID_SCR_KEY_DELAY, t.arg[0])); routed++; end
        GEN_CMD_MEM_ERR_ARM: begin   // arg0 bus (0 ibus, 1 dbus), arg1 lo, arg2 hi, arg3 = kind (GEN_MEM_ERR_ARM_KIND_ERR / _INTG) | count << 8
          if (t.arg[0] == 0) ibus.driver.arm_err(t.arg[3][7:0], t.arg[1], t.arg[2], t.arg[3][31:8] == 0 ? 1 : t.arg[3][31:8]);
          else               dbus.driver.arm_err(t.arg[3][7:0], t.arg[1], t.arg[2], t.arg[3][31:8] == 0 ? 1 : t.arg[3][31:8]);
          routed++;
        end
        GEN_CMD_MEM_PEEK, GEN_CMD_MISC: routed++;   // answered by the bridge / no-op
        default: begin
          ignored++;
          `uvm_error("GEN_CMD_DISPATCH", $sformatf("command %s has no consumer yet", t.kind_name()))
        end
      endcase
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  class gen_env extends uvm_env;
    `uvm_component_utils(gen_env)
    gen_env_cfg       cfg;
    gen_bridge        bridge;
    gen_mem_model     mem;
    gen_bus_agent     ibus_agent;
    gen_bus_agent     dbus_agent;
    gen_scrkey_driver scrkey;
    gen_ctrl_driver   ctrl;
    gen_cmd_dispatch  dispatch;
    gen_rvfi_monitor  rvfi_mon;
    gen_scoreboard    sb;
    gen_export_sink   sink;
    gen_wit_cov       wit;
    gen_isa_cov       isa_cov;
    gen_irq_driver    irq;
    gen_dbg_driver    dbg;
    gen_irq_checker   irq_chk;
    gen_dbg_checker   dbg_chk;
    gen_misc_monitor  misc_mon;
    gen_eot_handler    eot_h;
    gen_record_handler sig_h, ack_h, phase_h;
    virtual gen_bridge_if bvif;
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg))
        `uvm_fatal("GEN_ENV", "cfg not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", bvif))
        `uvm_fatal("GEN_ENV", "bridge_vif not in uvm_config_db")
      // memory model and image (the only backdoor write; digest verified, C3.3)
      mem = new("mem");
      mem.unmapped_ok = cfg.mem_unmapped_ok;
      if (cfg.mem_image_set) begin
        int unsigned n = mem.load_vmem(cfg.mem_image);
        if (!cfg.mem_image_crc32_set || !cfg.mem_image_words_set)
          `uvm_fatal("MEM_LOAD", "+gen_mem_image needs +gen_mem_image_crc32 and +gen_mem_image_words (sidecar values)")
        if (!mem.verify_digest(cfg.mem_image_crc32, cfg.mem_image_words))
          `uvm_fatal("MEM_LOAD", $sformatf("image %s: %0d words loaded, crc32 0x%08h, sidecar says %0d words crc32 0x%08h",
                     cfg.mem_image, n, mem.crc32_index_word(), cfg.mem_image_words, cfg.mem_image_crc32))
        `uvm_info("MEM_LOAD", $sformatf("image %s: %0d words, crc32 0x%08h verified", cfg.mem_image, n, cfg.mem_image_crc32), UVM_LOW)
      end else begin
        `uvm_warning("MEM_LOAD", "no +gen_mem_image: the core fetches zeros from RAM (bring-up only)")
      end
      eot_h   = new(bvif);
      sig_h   = new("GEN_SIG");
      ack_h   = new("GEN_IRQ_ACK");
      phase_h = new("GEN_PHASE_MARK");
      mem.add_mmio(GEN_MM_SIG_ADDR, GEN_MM_SIG_SIZE, sig_h);
      mem.add_mmio(GEN_MM_IRQ_ACK_ADDR, GEN_MM_IRQ_ACK_SIZE, ack_h);
      mem.add_mmio(GEN_MM_EOT_ADDR, GEN_MM_EOT_SIZE, eot_h);
      mem.add_mmio(GEN_MM_PHASE_MARK_ADDR, GEN_MM_PHASE_MARK_SIZE, phase_h);
      if (cfg.tohost_addr_set) mem.add_watch(cfg.tohost_addr, eot_h);
      // agents
      ibus_agent = gen_bus_agent::type_id::create("ibus_agent", this);
      dbus_agent = gen_bus_agent::type_id::create("dbus_agent", this);
      ibus_agent.cfg = gen_bus_cfg::type_id::create("ibus_cfg"); ibus_agent.cfg.from_env(cfg, 1'b0);
      dbus_agent.cfg = gen_bus_cfg::type_id::create("dbus_cfg"); dbus_agent.cfg.from_env(cfg, 1'b1);
      scrkey = gen_scrkey_driver::type_id::create("scrkey", this);
      ctrl   = gen_ctrl_driver::type_id::create("ctrl", this);
      dispatch = gen_cmd_dispatch::type_id::create("dispatch", this);
      wit = gen_wit_cov::type_id::create("wit", this);
      isa_cov = gen_isa_cov::type_id::create("isa_cov", this);
      rvfi_mon = gen_rvfi_monitor::type_id::create("rvfi_mon", this);
      sb       = gen_scoreboard::type_id::create("sb", this);
      sink     = gen_export_sink::type_id::create("sink", this);
      irq      = gen_irq_driver::type_id::create("irq", this);
      dbg      = gen_dbg_driver::type_id::create("dbg", this);
      irq_chk  = gen_irq_checker::type_id::create("irq_chk", this);
      dbg_chk  = gen_dbg_checker::type_id::create("dbg_chk", this);
      misc_mon = gen_misc_monitor::type_id::create("misc_mon", this);
      bridge = gen_bridge::type_id::create("bridge", this);
      `uvm_info("GEN_ENV", {"ibus: ", ibus_agent.cfg.describe()}, UVM_LOW)
      `uvm_info("GEN_ENV", {"dbus: ", dbus_agent.cfg.describe()}, UVM_LOW)
    endfunction

    function void connect_phase(uvm_phase phase);
      super.connect_phase(phase);
      ibus_agent.driver.mem = mem;
      dbus_agent.driver.mem = mem;
      bridge.mem = mem;
      dispatch.ctrl = ctrl;
      dispatch.sink = sink;
      dispatch.wit = wit; dispatch.isa_cov = isa_cov;
      dispatch.bvif = bvif;
      dispatch.irq = irq; dispatch.dbg = dbg; dispatch.scrkey = scrkey;
      dispatch.ibus = ibus_agent; dispatch.dbus = dbus_agent;
      ack_h.irq = irq;
      rvfi_mon.sink = sink;
      // event writers get the sink handle; each registers the rows it emits in its end_of_elaboration_phase and the sink
      // checks the emitted set (yaml export_active_sources) against the registrations in every run (T-141)
      ibus_agent.driver.sink = sink; dbus_agent.driver.sink = sink; ctrl.sink = sink; scrkey.sink = sink;
      irq.sink = sink; dbg.sink = sink; misc_mon.sink = sink; irq_chk.sink = sink;
      bridge.cmd_ap.connect(dispatch.analysis_export);
      rvfi_mon.ap.connect(sb.analysis_export);
      rvfi_mon.ap.connect(isa_cov.analysis_export);
      dbus_agent.ap.connect(isa_cov.dbus_imp);   // completed data-bus transactions: the Zcmp collector's observed latency class
      ibus_agent.ap.connect(isa_cov.ibus_imp);   // fetches: the multiply's fetch-stall class and the boot-to-request distance
      scrkey.ap.connect(isa_cov.key_imp);        // scramble-key req / valid changes: the security-input events
      sb.ap_state.connect(irq_chk.imp_state);
      sb.ap_state.connect(dbg_chk.imp_state);
      sb.ap_state.connect(misc_mon.imp_state);
      irq.ap.connect(irq_chk.imp_evt);
      irq.ap.connect(sb.imp_irq);   // the NMI raises of the two-record window (external NMI classification, CM25-L-6)
      dbg.ap.connect(dbg_chk.imp_evt);
    endfunction

    function void report_phase(uvm_phase phase);
      // referees: every interrupt / debug entry the scoreboard stepped must have reached the entry checkers as a published
      // state (an entry whose handler's first record folds into a Zcmp sequence once escaped them)
      if (irq_chk.entries_seen != sb.irq_entries)
        `uvm_error("irq_entries_referee", $sformatf("scoreboard stepped %0d interrupt entries, the irq checker saw %0d", sb.irq_entries, irq_chk.entries_seen))
      if (dbg_chk.entries != sb.dbg_entries)
        `uvm_error("dbg_entries_referee", $sformatf("scoreboard stepped %0d debug entries, the debug checker saw %0d", sb.dbg_entries, dbg_chk.entries))
      `uvm_info("GEN_ENV", $sformatf("mem: %0d words, %0d mmio writes, %0d unmapped accesses; eot stores %0d (last code 0x%08h); sig writes %0d; key requests %0d; commands routed %0d ignored %0d",
                mem.word_count(), mem.mmio_writes, mem.unmapped_count, bvif.evt_eot_count, bvif.evt_eot_code, sig_h.writes, scrkey.requests, dispatch.routed, dispatch.ignored), UVM_LOW)
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // gen_base_test: builds the cfg from plusargs (names from gen_tb_pkg, unknown +gen_* is fatal,
  // A-23), prints the TB banner, holds the run-phase objection until Python raises finish_req and has
  // dropped stim_active, and toggles finish_ack after the UVM report. UVM never calls $finish: cocotb
  // owns the end of simulation (TB_CONTRACT Section 2).
  class gen_base_test extends uvm_test;
    `uvm_component_utils(gen_base_test)
    gen_env_cfg cfg;
    gen_env     env;
    virtual gen_bridge_if vif;
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction

    function void check_unknown_plusargs();
      uvm_cmdline_processor clp = uvm_cmdline_processor::get_inst();
      string args[$];
      clp.get_args(args);
      foreach (args[i]) begin
        string a = args[i];
        string nm;
        int eq;
        if (a.len() < 5 || a.substr(0, 4) != "+gen_") continue;
        eq = a.len();
        for (int k = 0; k < a.len(); k++) if (a[k] == "=") begin eq = k; break; end
        nm = a.substr(1, eq - 1);
        if (!gen_is_known_plusarg(nm))
          `uvm_fatal("GEN_UNKNOWN_PLUSARG", $sformatf("unknown plusarg %s (names live in gen_tb_knobs.yaml)", a))
        if (eq == a.len() && gen_is_bool_plusarg(nm))
          `uvm_fatal("GEN_BARE_PLUSARG", $sformatf("%s needs =0 or =1 (a bare bool plusarg would be a silent no-op)", a))
      end
    endfunction

    function void build_phase(uvm_phase phase);
      string msg;
      int unsigned s;
      super.build_phase(phase);
      cfg = gen_env_cfg::type_id::create("cfg");
`ifndef COCOTB_SIM
      `uvm_fatal("GEN_NO_COCOTB", "gen_tb_top tests are cocotb-driven; a pure-SV build of this top would pass vacuously (TB_CONTRACT Section 6)")
`endif
      check_unknown_plusargs();
      cfg.parse_plusargs();
      if (!cfg.validate(msg)) `uvm_fatal("GEN_BAD_KNOB", msg)
      if ($value$plusargs("ntb_random_seed=%d", s)) cfg.seed = s;
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", vif))
        `uvm_fatal("GEN_BASE_TEST", "bridge_vif not in uvm_config_db")
      uvm_config_db#(gen_env_cfg)::set(this, "*", "cfg", cfg);
      env = gen_env::type_id::create("env", this);
      banner();
    endfunction

    function void banner();
      $display("%s tb=gen_tb_top uvm_test=%s seed=%0d build_config=%s pinned_knobs=%0d regime_sched=%s",
               GEN_BANNER_TAG, get_type_name(), cfg.seed, cfg.build_config, cfg.pinned_count(),
               cfg.regime_sched_set ? cfg.regime_sched : "derived");
`ifdef SIMULATION
      $display("%s define SIMULATION=1 (prim_lfsr default-seed randomisation active, F-DIT-025)", GEN_BANNER_TAG);
`else
      $display("%s define SIMULATION=0 (F-DIT-025)", GEN_BANNER_TAG);
`endif
`ifdef COCOTB_SIM
      $display("%s define COCOTB_SIM=1 (cocotb-master run)", GEN_BANNER_TAG);
`else
      $display("%s define COCOTB_SIM=0 (pure-SV run: the alive watchdog will fatal unless a test sets alive)", GEN_BANNER_TAG);
`endif
      $display("%s boot_addr=0x%08h hart_id=0x%08h alive_timeout=%0d finish_timeout=%0d mem_image=%s tohost=%s", GEN_BANNER_TAG,
               cfg.boot_addr, cfg.hart_id, cfg.alive_timeout, cfg.finish_timeout, cfg.mem_image_set ? cfg.mem_image : "none",
               cfg.tohost_addr_set ? $sformatf("0x%08h", cfg.tohost_addr) : "none");
      $display("%s knobs imem gnt=%s rvalid=%s err=%s intg=%s cap=%s dmem gnt=%s rvalid=%s err=%s intg=%s key=%s icram_init=%s",
               GEN_BANNER_TAG, cfg.knob_imem_gnt_delay, cfg.knob_imem_rvalid_delay, cfg.knob_imem_err_rate,
               cfg.knob_imem_intg_err_rate, cfg.knob_imem_outstanding_cap, cfg.knob_dmem_gnt_delay,
               cfg.knob_dmem_rvalid_delay, cfg.knob_dmem_err_rate, cfg.knob_dmem_intg_err_rate,
               cfg.knob_scr_key_delay, cfg.icram_init);
      // the tag RAM models read the injection rate from gen_icram_events (they hold no cfg handle)
      if (!gen_regime_scalar("rate_per_mille", cfg.knob_icache_ecc_err_rate, gen_icram_events::inject_rate))
        `uvm_fatal("GEN_ENV", {"bad icache ECC rate regime ", cfg.knob_icache_ecc_err_rate})
      $display("%s knobs irq regime=%s line_mix=%s hold=%s debug_req=%s fetch_enable=%s icache_ecc=%s", GEN_BANNER_TAG,
               cfg.knob_irq_regime, cfg.knob_irq_line_mix, cfg.knob_irq_hold, cfg.knob_debug_req_regime,
               cfg.knob_fetch_enable_regime, cfg.knob_icache_ecc_err_rate);
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
      super.end_of_elaboration_phase(phase);
      uvm_root::get().finish_on_completion = 0;   // cocotb ends the simulation
    endfunction

    task run_phase(uvm_phase phase);
      phase.raise_objection(this, "gen_base_test: waiting for finish_req");
      @(posedge vif.finish_req);
      while (vif.stim_active) @(posedge vif.clk);   // Python's checks complete before we conclude
      `uvm_info("GEN_BASE_TEST", $sformatf("finish_req seen at cycle %0d, commands consumed %0d, retired %0d",
                vif.cycle_count, vif.cmds_consumed, vif.evt_retired_count), UVM_LOW)
      phase.drop_objection(this, "gen_base_test: finish_req");
    endtask

    function void final_phase(uvm_phase phase);
      super.final_phase(phase);
      vif.finish_ack = ~vif.finish_ack;   // after the UVM report: Python awaits this edge
    endfunction
  endclass
endpackage
