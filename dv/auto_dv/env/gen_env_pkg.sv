// gen_env_pkg: the UVM environment skeleton of the generated TB (architecture C2, C9): gen_env_cfg
// (knob fields rendered from gen_tb_knobs.yaml), gen_cmd_item, gen_bridge, gen_env, gen_base_test.
// Tests differ by Python, not by UVM test class (DV_prompt Section 9); the one UVM test is
// gen_base_test. Agents, monitors and the scoreboard join this package in build steps 1c and 2.
package gen_env_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  `include "uvm_macros.svh"

  // ------------------------------------------------------------------------------------------
  class gen_env_cfg extends uvm_object;
    `uvm_object_utils(gen_env_cfg)
    int unsigned seed = 0;   // +ntb_random_seed, echoed in the banner next to Python's RANDOM_SEED
    `include "gen_env_cfg_knobs.svh"
    function new(string name = "gen_env_cfg");
      super.new(name);
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // One bridge command as captured from gen_bridge_if; published to the agents' sequencers.
  class gen_cmd_item extends uvm_sequence_item;
    logic [7:0]  kind;
    logic [31:0] arg [4];
    logic [15:0] seq;
    `uvm_object_utils_begin(gen_cmd_item)
      `uvm_field_int(kind, UVM_ALL_ON)
      `uvm_field_sarray_int(arg, UVM_ALL_ON)
      `uvm_field_int(seq, UVM_ALL_ON)
    `uvm_object_utils_end
    function new(string name = "gen_cmd_item");
      super.new(name);
    endfunction
    function string kind_name();
      case (kind)
        GEN_CMD_IRQ_SET:        return "IRQ_SET";
        GEN_CMD_IRQ_CLR:        return "IRQ_CLR";
        GEN_CMD_NMI_PULSE:      return "NMI_PULSE";
        GEN_CMD_DBG_REQ:        return "DBG_REQ";
        GEN_CMD_REGIME_SET:     return "REGIME_SET";
        GEN_CMD_KEY_MODE:       return "KEY_MODE";
        GEN_CMD_MEM_ERR_ARM:    return "MEM_ERR_ARM";
        GEN_CMD_ICACHE_ECC_ARM: return "ICACHE_ECC_ARM";
        GEN_CMD_FETCH_EN:       return "FETCH_EN";
        GEN_CMD_MEM_PEEK:       return "MEM_PEEK";
        GEN_CMD_MISC:           return "MISC";
        default:                return $sformatf("UNKNOWN(%0d)", kind);
      endcase
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // gen_bridge: arms the listener, consumes one command per cmd_valid edge, publishes it on cmd_ap
  // and toggles cmd_ack the next cycle; MEM_PEEK is answered from a memory read callback that the
  // memory model registers (step 1c); until then a peek is a collected error, never a silent 0.
  class gen_bridge extends uvm_component;
    `uvm_component_utils(gen_bridge)
    virtual gen_bridge_if vif;
    gen_env_cfg cfg;
    uvm_analysis_port #(gen_cmd_item) cmd_ap;
    int unsigned consumed = 0;
    // Memory read hook for MEM_PEEK (set by the memory model in step 1c).
    typedef logic [31:0] peek_fn_t;
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
      `uvm_error("GEN_BRIDGE", $sformatf("MEM_PEEK 0x%08h without a memory model", addr))
      return 32'h0;
    endfunction
    task run_phase(uvm_phase phase);
      gen_cmd_item item;
      logic cmd_valid_q;
      @(posedge vif.clk);
      cmd_valid_q = vif.cmd_valid;
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
  class gen_env extends uvm_env;
    `uvm_component_utils(gen_env)
    gen_env_cfg cfg;
    gen_bridge  bridge;
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg))
        `uvm_fatal("GEN_ENV", "cfg not in uvm_config_db")
      bridge = gen_bridge::type_id::create("bridge", this);
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
      $display("%s alive_timeout=%0d finish_timeout=%0d mem_image=%s", GEN_BANNER_TAG,
               cfg.alive_timeout, cfg.finish_timeout, cfg.mem_image_set ? cfg.mem_image : "none");
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
      super.end_of_elaboration_phase(phase);
      uvm_root::get().finish_on_completion = 0;   // cocotb ends the simulation
    endfunction

    task run_phase(uvm_phase phase);
      phase.raise_objection(this, "gen_base_test: waiting for finish_req");
      @(posedge vif.finish_req);
      while (vif.stim_active) @(posedge vif.clk);   // Python's checks complete before we conclude
      `uvm_info("GEN_BASE_TEST", $sformatf("finish_req seen at cycle %0d, commands consumed %0d",
                vif.cycle_count, vif.cmds_consumed), UVM_LOW)
      phase.drop_objection(this, "gen_base_test: finish_req");
    endtask

    function void final_phase(uvm_phase phase);
      super.final_phase(phase);
      vif.finish_ack = ~vif.finish_ack;   // after the UVM report: Python awaits this edge
    endfunction
  endclass
endpackage
