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
  // without a consumer yet (irq/debug agents, regimes, injection arms: step 2) are collected errors so
  // a test cannot believe it stimulated something that nothing consumed.
  class gen_cmd_dispatch extends uvm_subscriber #(gen_cmd_item);
    `uvm_component_utils(gen_cmd_dispatch)
    gen_ctrl_driver ctrl;
    int unsigned routed = 0, ignored = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction
    function void write(gen_cmd_item t);
      case (t.kind)
        GEN_CMD_FETCH_EN: begin ctrl.set_fetch_en(t.arg[0]); routed++; end
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
      mem.add_mmio(GEN_MM_SIG_ADDR, 32'h100, sig_h);
      mem.add_mmio(GEN_MM_IRQ_ACK_ADDR, 32'h4, ack_h);
      mem.add_mmio(GEN_MM_EOT_ADDR, 32'h4, eot_h);
      mem.add_mmio(GEN_MM_PHASE_MARK_ADDR, 32'h4, phase_h);
      if (cfg.tohost_addr_set) mem.add_watch(cfg.tohost_addr, eot_h);
      // agents
      ibus_agent = gen_bus_agent::type_id::create("ibus_agent", this);
      dbus_agent = gen_bus_agent::type_id::create("dbus_agent", this);
      ibus_agent.cfg = gen_bus_cfg::type_id::create("ibus_cfg"); ibus_agent.cfg.from_env(cfg, 1'b0);
      dbus_agent.cfg = gen_bus_cfg::type_id::create("dbus_cfg"); dbus_agent.cfg.from_env(cfg, 1'b1);
      scrkey = gen_scrkey_driver::type_id::create("scrkey", this);
      ctrl   = gen_ctrl_driver::type_id::create("ctrl", this);
      dispatch = gen_cmd_dispatch::type_id::create("dispatch", this);
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
      bridge.cmd_ap.connect(dispatch.analysis_export);
    endfunction

    function void report_phase(uvm_phase phase);
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
      end
    endfunction

    function void build_phase(uvm_phase phase);
      string msg;
      int unsigned s;
      super.build_phase(phase);
      cfg = gen_env_cfg::type_id::create("cfg");
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
      $display("%s alive_timeout=%0d finish_timeout=%0d mem_image=%s tohost=%s", GEN_BANNER_TAG,
               cfg.alive_timeout, cfg.finish_timeout, cfg.mem_image_set ? cfg.mem_image : "none",
               cfg.tohost_addr_set ? $sformatf("0x%08h", cfg.tohost_addr) : "none");
      $display("%s knobs imem gnt=%s rvalid=%s err=%s intg=%s cap=%s dmem gnt=%s rvalid=%s err=%s intg=%s key=%s icram_init=%s",
               GEN_BANNER_TAG, cfg.knob_imem_gnt_delay, cfg.knob_imem_rvalid_delay, cfg.knob_imem_err_rate,
               cfg.knob_imem_intg_err_rate, cfg.knob_imem_outstanding_cap, cfg.knob_dmem_gnt_delay,
               cfg.knob_dmem_rvalid_delay, cfg.knob_dmem_err_rate, cfg.knob_dmem_intg_err_rate,
               cfg.knob_scr_key_delay, cfg.icram_init);
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
