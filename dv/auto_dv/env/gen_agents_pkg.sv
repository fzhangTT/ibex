// gen_agents_pkg: the interface agents and test-equipment drivers of build step 1c (architecture
// C3.1, C3.2, C3.5): the memory-bus agent (reactive slave over gen_mem_model with the regime knobs of
// gen_fcov_plan.md Section REG mapped to latency windows and injection rates, one instance per bus),
// the scramble-key responder, and the MMIO/watch handlers that turn program stores into bridge events.
// Checker rows (ibus_proto, dbus_*, scrkey_proto) follow in step 2; this package only drives and
// observes. Stimulus legality is asserted in gen_bus_if (sva_rvalid_legal).
package gen_agents_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  import gen_cfg_pkg::*;
  import gen_export_pkg::*;
  import gen_mem_pkg::*;
  `include "uvm_macros.svh"

  typedef enum {GEN_BUS_FETCH, GEN_BUS_LOAD, GEN_BUS_STORE} gen_bus_kind_e;

  // ------------------------------------------------------------------------------------------
  // One bus transaction as observed at the boundary (published by the monitor).
  class gen_bus_txn extends uvm_sequence_item;
    gen_bus_kind_e kind;
    logic [31:0]   addr;
    logic [31:0]   data;            // rdata word (fetch/load) or wdata word (store)
    logic [6:0]    intg;            // integrity bits as driven / observed
    logic [3:0]    be;
    bit            err;
    bit            injected;        // the agent injected err or corrupted integrity on purpose
    int unsigned   gnt_delay;
    int unsigned   rvalid_delay;
    int unsigned   cycle_req;
    int unsigned   cycle_gnt;
    int unsigned   cycle_rvalid;
    int unsigned   outstanding_at_gnt;
    `uvm_object_utils_begin(gen_bus_txn)
      `uvm_field_enum(gen_bus_kind_e, kind, UVM_ALL_ON)
      `uvm_field_int(addr, UVM_ALL_ON)
      `uvm_field_int(data, UVM_ALL_ON)
      `uvm_field_int(intg, UVM_ALL_ON)
      `uvm_field_int(be, UVM_ALL_ON)
      `uvm_field_int(err, UVM_ALL_ON)
      `uvm_field_int(injected, UVM_ALL_ON)
      `uvm_field_int(gnt_delay, UVM_ALL_ON)
      `uvm_field_int(rvalid_delay, UVM_ALL_ON)
      `uvm_field_int(cycle_req, UVM_ALL_ON)
      `uvm_field_int(cycle_gnt, UVM_ALL_ON)
      `uvm_field_int(cycle_rvalid, UVM_ALL_ON)
      `uvm_field_int(outstanding_at_gnt, UVM_ALL_ON)
    `uvm_object_utils_end
    function new(string name = "gen_bus_txn");
      super.new(name);
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // Per-agent configuration: latency windows, caps and injection rates. Enum regime knobs (DV Lead
  // value sets) map to windows here; numeric plusarg overrides win when supplied.
  class gen_bus_cfg extends uvm_object;
    `uvm_object_utils(gen_bus_cfg)
    bit          is_data = 0;
    int unsigned gnt_min = 1, gnt_max = 3;
    int unsigned rvalid_min = 1, rvalid_max = 3;
    int unsigned max_outstanding = GEN_IBUS_MAX_OUTSTANDING;
    int unsigned err_rate = 0;          // per mille per response
    int unsigned intg_err_rate = 0;     // per mille per response
    int unsigned intg_bits = 1;
    logic [31:0] err_win_lo = '0, err_win_hi = '0;   // lo == hi == 0: any address
    string       err_half = "any";
    bit          err_store_perform = 1;
    // applied enum values, for the phase log / coverage
    string gnt_regime = "short", rvalid_regime = "short", err_regime = "none", intg_regime = "none", cap_regime = "cap8";
    function new(string name = "gen_bus_cfg");
      super.new(name);
    endfunction

    function void apply_gnt_regime(string v);
      gnt_regime = v;
      if (!gen_regime_window("gnt_delay", v, gnt_min, gnt_max)) `uvm_fatal("GEN_BUS_CFG", {"bad gnt regime ", v})
    endfunction
    function void apply_rvalid_regime(string v);
      rvalid_regime = v;
      if (!gen_regime_window("rvalid_delay", v, rvalid_min, rvalid_max)) `uvm_fatal("GEN_BUS_CFG", {"bad rvalid regime ", v})
    endfunction
    function int unsigned rate_of(string v);
      int unsigned r;
      if (!gen_regime_scalar("rate_per_mille", v, r)) `uvm_fatal("GEN_BUS_CFG", {"bad rate regime ", v})
      return r;
    endfunction
    function void apply_cap_regime(string v);
      cap_regime = v;
      if (!gen_regime_scalar("outstanding_cap", v, max_outstanding)) `uvm_fatal("GEN_BUS_CFG", {"bad cap regime ", v})
      if (!is_data && max_outstanding > GEN_IBUS_MAX_OUTSTANDING) max_outstanding = GEN_IBUS_MAX_OUTSTANDING;
      if (is_data  && max_outstanding > GEN_DBUS_MAX_OUTSTANDING) max_outstanding = GEN_DBUS_MAX_OUTSTANDING;
    endfunction

    // Build from the environment configuration: enum knobs first, numeric overrides after.
    function void from_env(gen_env_cfg c, bit data);
      is_data = data;
      if (!data) begin
        apply_gnt_regime(c.knob_imem_gnt_delay);
        apply_rvalid_regime(c.knob_imem_rvalid_delay);
        err_regime = c.knob_imem_err_rate;   err_rate = rate_of(err_regime);
        intg_regime = c.knob_imem_intg_err_rate; intg_err_rate = rate_of(intg_regime);
        apply_cap_regime(c.knob_imem_outstanding_cap);
        if (c.ibus_gnt_min_set) gnt_min = c.ibus_gnt_min;
        if (c.ibus_gnt_max_set) gnt_max = c.ibus_gnt_max;
        if (c.ibus_rvalid_min_set) rvalid_min = c.ibus_rvalid_min;
        if (c.ibus_rvalid_max_set) rvalid_max = c.ibus_rvalid_max;
        if (c.ibus_max_outstanding_set) max_outstanding = c.ibus_max_outstanding;
        if (c.ibus_err_rate_set) err_rate = c.ibus_err_rate;
        if (c.ibus_intg_err_rate_set) intg_err_rate = c.ibus_intg_err_rate;
        intg_bits = c.ibus_intg_bits;
        if (c.ibus_err_window_set) parse_window(c.ibus_err_window);
      end else begin
        apply_gnt_regime(c.knob_dmem_gnt_delay);
        apply_rvalid_regime(c.knob_dmem_rvalid_delay);
        err_regime = c.knob_dmem_err_rate;   err_rate = rate_of(err_regime);
        intg_regime = c.knob_dmem_intg_err_rate; intg_err_rate = rate_of(intg_regime);
        max_outstanding = GEN_DBUS_MAX_OUTSTANDING; cap_regime = "cap2";
        if (c.dbus_gnt_min_set) gnt_min = c.dbus_gnt_min;
        if (c.dbus_gnt_max_set) gnt_max = c.dbus_gnt_max;
        if (c.dbus_rvalid_min_set) rvalid_min = c.dbus_rvalid_min;
        if (c.dbus_rvalid_max_set) rvalid_max = c.dbus_rvalid_max;
        if (c.dbus_max_outstanding_set) max_outstanding = c.dbus_max_outstanding;
        if (c.dbus_err_rate_set) err_rate = c.dbus_err_rate;
        if (c.dbus_intg_err_rate_set) intg_err_rate = c.dbus_intg_err_rate;
        intg_bits = c.dbus_intg_bits;
        if (c.dbus_err_window_set) parse_window(c.dbus_err_window);
        err_half = c.dbus_err_half;
        err_store_perform = c.dbus_err_store_perform;
      end
      if (rvalid_min < 1) rvalid_min = 1;   // hard floor: a same-cycle response is illegal
      if (rvalid_max < rvalid_min) rvalid_max = rvalid_min;
      if (gnt_max < gnt_min) gnt_max = gnt_min;
      if (max_outstanding < 1) max_outstanding = 1;
    endfunction
    function void parse_window(string s);
      int sep = -1;
      for (int i = 0; i < s.len(); i++) if (s[i] == ":") begin sep = i; break; end
      if (sep < 0) `uvm_fatal("GEN_BUS_CFG", {"bad error window ", s, " (lo:hi)"})
      err_win_lo = s.substr(0, sep - 1).atohex();
      err_win_hi = s.substr(sep + 1, s.len() - 1).atohex();
    endfunction
    function bit in_err_window(logic [31:0] a);
      if (err_win_lo == 0 && err_win_hi == 0) return 1'b1;
      return (a >= err_win_lo) && (a <= err_win_hi);
    endfunction
    // REGIME_SET at run time (gen_cmd_dispatch): the knob id selects the regime this configuration owns
    function bit apply_knob(int id, string value);
      case (id)
        GEN_KNOB_ID_IMEM_GNT_DELAY, GEN_KNOB_ID_DMEM_GNT_DELAY:         apply_gnt_regime(value);
        GEN_KNOB_ID_IMEM_RVALID_DELAY, GEN_KNOB_ID_DMEM_RVALID_DELAY:   apply_rvalid_regime(value);
        GEN_KNOB_ID_IMEM_ERR_RATE, GEN_KNOB_ID_DMEM_ERR_RATE:           begin err_regime = value; err_rate = rate_of(value); end
        GEN_KNOB_ID_IMEM_INTG_ERR_RATE, GEN_KNOB_ID_DMEM_INTG_ERR_RATE: begin intg_regime = value; intg_err_rate = rate_of(value); end
        GEN_KNOB_ID_IMEM_OUTSTANDING_CAP:                               apply_cap_regime(value);
        default: return 0;
      endcase
      if (rvalid_min < 1) rvalid_min = 1;
      if (rvalid_max < rvalid_min) rvalid_max = rvalid_min;
      if (gnt_max < gnt_min) gnt_max = gnt_min;
      return 1;
    endfunction
    function string describe();
      return $sformatf("%s gnt=%0d..%0d(%s) rvalid=%0d..%0d(%s) cap=%0d(%s) err=%0d/1000(%s) intg=%0d/1000(%s)x%0d",
                       is_data ? "dbus" : "ibus", gnt_min, gnt_max, gnt_regime, rvalid_min, rvalid_max, rvalid_regime,
                       max_outstanding, cap_regime, err_rate, err_regime, intg_err_rate, intg_regime, intg_bits);
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // A granted request waiting for its response (driver-side queue, in order).
  typedef struct {
    logic [31:0] addr;
    bit          we;
    logic [3:0]  be;
    logic [31:0] wdata;
    logic [31:0] word;      // response word (fetch/load) or the stored word (store)
    logic [6:0]  intg;      // driven integrity
    bit          err;
    bit          injected;
    bit          intg_bad;  // the driven integrity is corrupted (alert_bus must fire in the rvalid cycle)
    int unsigned gnt_delay;
    int unsigned rvalid_delay;
    int unsigned cycle_req;
    int unsigned cycle_gnt;
    int unsigned due;       // response cycle
    int unsigned outstanding_at_gnt;
  } gen_bus_pend_t;

  // ------------------------------------------------------------------------------------------
  // Reactive slave driver: acts at the falling edge (the core's posedge outputs are stable), grants
  // after the drawn delay while the outstanding cap allows, performs the memory operation at grant,
  // and drives the response for exactly one cycle after the drawn latency, in grant order.
  class gen_bus_driver extends uvm_component;
    `uvm_component_utils(gen_bus_driver)
    virtual gen_bus_if vif;
    gen_bus_cfg   cfg;
    gen_mem_model mem;
    gen_export_sink sink;                  // E req / gnt / rvalid lines when the source is on (set by gen_env)
    virtual gen_bridge_if bvif;            // grant counters evt_ibus_grants / evt_dbus_grants
    uvm_analysis_port #(gen_bus_txn) ap;   // completed transactions with the driver's injection facts
    gen_bus_pend_t pend [$];
    int unsigned cycle = 0;
    int unsigned grants = 0, responses = 0, injected_err = 0, injected_intg = 0;
    // one-shot arming (bridge MEM_ERR_ARM): kind 1 = bus error, 2 = integrity corruption; count accesses in [lo, hi]
    int unsigned arm_kind = 0, arm_count = 0;
    logic [31:0] arm_lo = '0, arm_hi = '0;
    function void arm_err(int unsigned kind, logic [31:0] lo, logic [31:0] hi, int unsigned count);
      arm_kind = kind; arm_lo = lo; arm_hi = hi; arm_count = count;
      `uvm_info("GEN_BUS_ARM", $sformatf("%s: armed kind %0d for %0d accesses in [%08h, %08h]", cfg.is_data ? "dbus" : "ibus", kind, count, lo, hi), UVM_LOW)
    endfunction
    function bit armed_hit(int unsigned kind, logic [31:0] a);
      if (arm_count == 0 || arm_kind != kind) return 0;
      if (a < arm_lo || a > arm_hi) return 0;
      arm_count--;
      return 1;
    endfunction
    function new(string name, uvm_component parent);
      super.new(name, parent);
      ap = new("ap", this);
    endfunction

    function logic [38:0] encode(logic [31:0] w);
      return prim_secded_pkg::prim_secded_inv_39_32_enc(w);
    endfunction

    // The SECDED encoder above is the 39/32 inv code; a bus of another width would truncate {intg, word}
    // silently, so the mismatch is a build-time fatal instead.
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_bus_if)::get(this, "", "vif", vif))
        `uvm_fatal("GEN_BUS_DRIVER", {get_full_name(), ": vif not in uvm_config_db"})
      if ($bits(vif.rdata) != $bits(logic [38:0]))
        `uvm_fatal("GEN_BUS_DRIVER", $sformatf("%s: bus data width %0d, the driver encodes %0d bits", get_full_name(), $bits(vif.rdata), $bits(logic [38:0])))
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", bvif))
        `uvm_fatal("GEN_BUS_DRIVER", {get_full_name(), ": bridge_vif not in uvm_config_db"})
    endfunction
    function bit ev_on();
      return sink != null && sink.source_on(cfg.is_data ? "dbus" : "ibus");
    endfunction
    function void end_of_elaboration_phase(uvm_phase phase);
      string s = cfg.is_data ? "dbus" : "ibus";
      super.end_of_elaboration_phase(phase);
      if (sink == null) return;
      sink.register_row(s, "req"); sink.register_row(s, "gnt"); sink.register_row(s, "rvalid");
    endfunction
    // the instruction side has no write enable or byte strobes: a fetch is a full-word read
    function bit req_we(); return cfg.is_data ? vif.we : 1'b0; endfunction
    function logic [3:0] req_be(); return cfg.is_data ? vif.be : 4'hF; endfunction

    task run_phase(uvm_phase phase);
      int unsigned gnt_wait = 0;
      bit          gnt_armed = 0;
      int unsigned req_cycle = 0;     // first cycle the pending request was seen (driver counter, for the txn)
      int unsigned req_stamp = 0;     // the same instant on the export's cycle base (E req / gnt lines)
      int unsigned last_due = 0;
      int unsigned data_w = $bits(vif.rdata);
      vif.gnt = 1'b0; vif.rvalid = 1'b0; vif.err = 1'b0; vif.rdata = '0; vif.intg_corrupt = 1'b0;
      forever begin
        @(negedge vif.clk);
        if (!vif.rst_n) begin
          vif.gnt = 1'b0; vif.rvalid = 1'b0; vif.err = 1'b0;
          pend.delete(); gnt_armed = 0; cycle = 0; last_due = 0;
          continue;
        end
        cycle++;
        // ---- response side: at most one per cycle, in order
        vif.rvalid = 1'b0; vif.err = 1'b0; vif.intg_corrupt = 1'b0;
        if (pend.size() > 0 && pend[0].due <= cycle) begin
          gen_bus_pend_t p = pend.pop_front();
          gen_bus_txn t = gen_bus_txn::type_id::create("txn");
          vif.rvalid = 1'b1;
          vif.err    = p.err;
          vif.rdata  = {p.intg, p.word};
          vif.intg_corrupt = p.intg_bad;
          responses++;
          if (ev_on()) sink.write_event(cfg.is_data ? gen_export_line_dbus_rvalid(sink.cycle(), p.addr, p.we, p.err, p.intg_bad, pend.size())
                                                    : gen_export_line_ibus_rvalid(sink.cycle(), p.addr, p.we, p.err, p.intg_bad, pend.size()));
          t.kind = cfg.is_data ? (p.we ? GEN_BUS_STORE : GEN_BUS_LOAD) : GEN_BUS_FETCH;
          t.addr = p.addr; t.data = p.we ? p.wdata : p.word; t.intg = p.intg; t.be = p.be;
          t.err = p.err; t.injected = p.injected; t.gnt_delay = p.gnt_delay; t.rvalid_delay = p.rvalid_delay;
          t.cycle_req = p.cycle_req; t.cycle_gnt = p.cycle_gnt; t.cycle_rvalid = cycle;
          t.outstanding_at_gnt = p.outstanding_at_gnt;
          ap.write(t);
        end
        // ---- request side
        vif.gnt = 1'b0;
        if (vif.req) begin
          if (!gnt_armed) begin
            gnt_armed = 1;
            req_cycle = cycle;
            gnt_wait = $urandom_range(cfg.gnt_max, cfg.gnt_min);
            if (ev_on()) begin
              req_stamp = sink.cycle();
              sink.write_event(cfg.is_data ? gen_export_line_dbus_req(req_stamp, vif.addr, req_we(), req_be())
                                           : gen_export_line_ibus_req(req_stamp, vif.addr, req_we(), req_be()));
            end
          end
          if (gnt_wait == 0 && pend.size() < cfg.max_outstanding) begin
            gen_bus_pend_t p;
            logic [38:0] enc;
            p.addr = vif.addr; p.we = req_we(); p.be = req_be();
            p.wdata = cfg.is_data ? vif.wdata[31:0] : '0;
            p.gnt_delay = cycle - req_cycle; p.cycle_req = req_cycle; p.cycle_gnt = cycle; p.outstanding_at_gnt = pend.size();
            p.err = 0; p.injected = 0; p.intg_bad = 0;
            if (armed_hit(GEN_MEM_ERR_ARM_KIND_ERR, p.addr) || (cfg.err_rate > 0 && cfg.in_err_window(p.addr) && ($urandom_range(999, 0) < cfg.err_rate))) begin
              p.err = 1; p.injected = 1; injected_err++;
              if (cfg.is_data) gen_bus_err_log::note(p.addr, bvif.cycle_count);   // the scoreboard arms the model's fault only for announced errors
            end
            if (p.we) begin
              if (!p.err || cfg.err_store_perform) mem.write_masked(p.addr, p.wdata, p.be);
              p.word = p.wdata;
            end else begin
              p.word = mem.read32(p.addr);
            end
            enc = encode(p.we ? 32'h0 : p.word);   // store responses carry a valid encoding of zero
            if (p.we) p.word = 32'h0;
            p.intg = enc[38:32];
            if (armed_hit(GEN_MEM_ERR_ARM_KIND_INTG, p.addr) || (cfg.intg_err_rate > 0 && cfg.in_err_window(p.addr) && ($urandom_range(999, 0) < cfg.intg_err_rate))) begin
              int b1 = $urandom_range(data_w - 1, 0);
              logic [38:0] flipped = {p.intg, p.word};
              flipped[b1] = ~flipped[b1];
              if (cfg.is_data) gen_bus_err_log::note_intg(p.addr);
              if (cfg.intg_bits > 1) begin
                int b2 = (b1 + 1 + $urandom_range(data_w - 2, 0)) % data_w;
                flipped[b2] = ~flipped[b2];
              end
              p.intg = flipped[38:32]; p.word = flipped[31:0];
              p.injected = 1; p.intg_bad = 1; injected_intg++;
            end
            p.rvalid_delay = $urandom_range(cfg.rvalid_max, cfg.rvalid_min);
            p.due = cycle + p.rvalid_delay;
            if (p.due <= last_due) p.due = last_due + 1;   // in-order, one response per cycle
            last_due = p.due;
            pend.push_back(p);
            vif.gnt = 1'b1;
            grants++;
            if (cfg.is_data) bvif.evt_dbus_grants <= bvif.evt_dbus_grants + 32'd1; else bvif.evt_ibus_grants <= bvif.evt_ibus_grants + 32'd1;
            if (ev_on()) sink.write_event(cfg.is_data ? gen_export_line_dbus_gnt(sink.cycle(), p.addr, p.we, p.be, req_stamp, pend.size())
                                                      : gen_export_line_ibus_gnt(sink.cycle(), p.addr, p.we, p.be, req_stamp, pend.size()));
            gnt_armed = 0;
          end else if (gnt_wait > 0) begin
            gnt_wait--;
          end
        end else begin
          gnt_armed = 0;
        end
      end
    endtask
  endclass

  class gen_bus_agent extends uvm_agent;
    `uvm_component_utils(gen_bus_agent)
    gen_bus_cfg    cfg;
    gen_bus_driver driver;
    uvm_analysis_port #(gen_bus_txn) ap;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      ap = new("ap", this);
    endfunction
    function void build_phase(uvm_phase phase);
      gen_env_cfg ecfg;
      super.build_phase(phase);
      driver = gen_bus_driver::type_id::create("driver", this);
      driver.cfg = cfg;
      if (!uvm_config_db#(virtual gen_bus_if)::get(this, "", "vif", driver.vif))
        `uvm_fatal("GEN_BUS_AGENT", {get_full_name(), ": vif not in uvm_config_db"})
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", ecfg))
        `uvm_fatal("GEN_BUS_AGENT", {get_full_name(), ": cfg not in uvm_config_db"})
      driver.vif.chk_rvalid_legal_en = ecfg.chk_all ? ecfg.chk_sva_rvalid_legal
                                                    : (ecfg.chk_sva_rvalid_legal_set && ecfg.chk_sva_rvalid_legal);
      if (driver.vif.chk_rvalid_legal_en) `uvm_info(get_type_name(), {get_full_name(), ": sva_rvalid_legal armed"}, UVM_LOW)
      else `uvm_info(get_type_name(), {get_full_name(), ": sva_rvalid_legal disabled by knob"}, UVM_LOW)
    endfunction
    function void connect_phase(uvm_phase phase);
      super.connect_phase(phase);
      driver.ap.connect(ap);
    endfunction
    function void report_phase(uvm_phase phase);
      `uvm_info(get_type_name(), $sformatf("%s: grants=%0d responses=%0d injected_err=%0d injected_intg=%0d",
                cfg.describe(), driver.grants, driver.responses, driver.injected_err, driver.injected_intg), UVM_LOW)
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // Scramble-key responder (C3.5): answers each ic_scr_key_req_o pulse by dropping valid, holding it
  // low for the regime's delay, then raising it until the next pulse.
  class gen_scrkey_driver extends uvm_component;
    `uvm_component_utils(gen_scrkey_driver)
    virtual gen_scrkey_if vif;
    gen_env_cfg cfg;
    int unsigned requests = 0;
    gen_export_sink sink;   // E scrkey req / valid lines on every change
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_scrkey_if)::get(this, "", "vif", vif))
        `uvm_fatal("GEN_SCRKEY", "vif not in uvm_config_db")
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg))
        `uvm_fatal("GEN_SCRKEY", "cfg not in uvm_config_db")
    endfunction
    function void end_of_elaboration_phase(uvm_phase phase);
      super.end_of_elaboration_phase(phase);
      if (sink == null) return;
      sink.register_row("scrkey", "req"); sink.register_row("scrkey", "valid");
    endfunction
    string regime;   // current knob_scr_key_delay value (REGIME_SET / KEY_MODE change it)
    function void set_regime(string v);
      regime = v;
      `uvm_info("GEN_SCRKEY", {"key regime <= ", v}, UVM_LOW)
    endfunction
    function int unsigned delay_cycles();
      case (regime)
        "immediate":           return 1;
        "delayed":             return $urandom_range(cfg.key_delay_max, cfg.key_delay_min);
        "withheld_then_valid": return cfg.key_never_cycles + 1;
        default: `uvm_fatal("GEN_SCRKEY", {"bad knob_scr_key_delay ", regime})
      endcase
      return 1;
    endfunction
    task run_phase(uvm_phase phase);
      int unsigned wait_n = 0;
      bit req_q = 0, valid_q;
      regime = cfg.knob_scr_key_delay;
      vif.valid = cfg.key_reset_valid;
      valid_q = vif.valid;
      forever begin
        @(negedge vif.clk);
        if (!vif.rst_n) begin vif.valid = cfg.key_reset_valid; wait_n = 0; continue; end
        if (vif.req && !req_q) begin
          requests++;
          vif.valid = 1'b0;
          wait_n = delay_cycles();
        end else if (wait_n > 0) begin
          wait_n--;
          if (wait_n == 0) vif.valid = 1'b1;
        end
        if (sink != null && sink.source_on("scrkey")) begin
          if (vif.req != req_q) sink.write_event(gen_export_line_scrkey_req(sink.cycle(), vif.req));
          if (vif.valid != valid_q) sink.write_event(gen_export_line_scrkey_valid(sink.cycle(), vif.valid));
        end
        valid_q = vif.valid;
        req_q = vif.req;
      end
    endtask
  endclass

  // ------------------------------------------------------------------------------------------
  // Interrupt line event, published by gen_irq_driver (and gen_dbg_driver for debug_req) for the checkers.
  typedef enum {GEN_IRQ_HOLD_CYCLES, GEN_IRQ_HOLD_UNTIL_ACK, GEN_IRQ_HOLD_UNTIL_TAKEN, GEN_IRQ_HOLD_STICKY} gen_irq_hold_e;
  class gen_irq_evt extends uvm_sequence_item;
    logic [18:0]   lines_after;   // level of every line after this event (0 sw, 1 timer, 2 ext, 3..17 fast, 18 nm)
    logic [18:0]   changed;       // lines that changed in this event
    bit            level;         // 1 = asserted, 0 = released
    gen_irq_hold_e hold;
    int unsigned   cycle;
    bit            from_regime;   // 1 = the autonomous regime engine, 0 = a bridge command
    `uvm_object_utils_begin(gen_irq_evt)
      `uvm_field_int(lines_after, UVM_ALL_ON)
      `uvm_field_int(changed, UVM_ALL_ON)
      `uvm_field_int(level, UVM_ALL_ON)
      `uvm_field_enum(gen_irq_hold_e, hold, UVM_ALL_ON)
      `uvm_field_int(cycle, UVM_ALL_ON)
      `uvm_field_int(from_regime, UVM_ALL_ON)
    `uvm_object_utils_end
    function new(string name = "gen_irq_evt");
      super.new(name);
    endfunction
  endclass

  // gen_irq_driver (C3.6): levels on the interrupt pins from bridge commands (IRQ_SET mask, hold policy,
  // hold cycles; IRQ_CLR mask; NMI_PULSE cycles) and from the regime engine (knob_irq_regime quiet /
  // sparse / storm, knob_irq_line_mix, knob_irq_hold). Hold policies: CYCLES(n) releases after n cycles,
  // UNTIL_TAKEN releases the line the DUT took on its own entry (evt_irq_taken and the entry's vector cause), STICKY
  // never releases, UNTIL_ACK releases on the handler's store to the irq-ack register (memory-model hook).
  // Acts at the falling edge like every driver; every change is published on ap with its cycle.
  // Interrupt-line bit i (0 sw, 1 timer, 2 ext, 3..17 fast, 18 nm) -> mie/mip bit position
  function automatic int gen_irq_mie_bit(int line);
    if (line == 0) return ibex_pkg::CSR_MSIX_BIT;
    if (line == 1) return ibex_pkg::CSR_MTIX_BIT;
    if (line == 2) return ibex_pkg::CSR_MEIX_BIT;
    if (line <= 17) return ibex_pkg::CSR_MFIX_BIT_LOW + (line - 3);
    return -1;
  endfunction
  // mcause lower_cause of an interrupt entry -> line bit (-1: not a line, e.g. NMI)
  function automatic int gen_irq_line_of_cause(int unsigned lower_cause);
    for (int l = 0; l < 18; l++) if (gen_irq_mie_bit(l) == lower_cause) return l;
    return -1;
  endfunction
  // controller priority (rtl/ibex_controller.sv exc_cause_o chain and gen_mfip_id): lowest fast id, then external,
  // software, timer; NMI outranks all and is handled apart. Smaller rank wins.
  function automatic int gen_irq_rank(int line);
    if (line >= 3) return line - 3;
    if (line == 2) return 15;
    if (line == 0) return 16;
    return 17;
  endfunction
  class gen_irq_driver extends uvm_component;
    `uvm_component_utils(gen_irq_driver)
    virtual gen_irq_if    vif;
    virtual gen_bridge_if bvif;
    gen_env_cfg cfg;
    uvm_analysis_port #(gen_irq_evt) ap;
    string regime, line_mix, hold_knob;
    int unsigned event_mean = 0;   // regime_windows.irq_event_mean of the current regime (0 = no autonomous events)
    function void set_mean();
      if (!gen_regime_scalar("irq_event_mean", regime, event_mean)) `uvm_fatal("GEN_IRQ", {"no irq_event_mean for regime ", regime})
    endfunction
    gen_export_sink sink;                  // E pin lines per changed line
    logic [18:0]   applied_q = '0;         // the levels last driven (the E line set is the difference)
    logic [18:0]   level = '0;
    gen_irq_hold_e hold_of [19];
    int unsigned   hold_left [19];
    int unsigned   events = 0, releases = 0, regime_events = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      ap = new("ap", this);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_irq_if)::get(this, "", "vif", vif)) `uvm_fatal("GEN_IRQ", "vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", bvif)) `uvm_fatal("GEN_IRQ", "bridge_vif not in uvm_config_db")
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_IRQ", "cfg not in uvm_config_db")
      regime = cfg.knob_irq_regime; line_mix = cfg.knob_irq_line_mix; hold_knob = cfg.knob_irq_hold; set_mean();
      foreach (hold_of[i]) begin hold_of[i] = GEN_IRQ_HOLD_CYCLES; hold_left[i] = 0; end
    endfunction
    function void end_of_elaboration_phase(uvm_phase phase);
      super.end_of_elaboration_phase(phase);
      if (sink == null) return;
      sink.register_row("pin", "irq_software"); sink.register_row("pin", "irq_timer"); sink.register_row("pin", "irq_external");
      sink.register_row("pin", "irq_fast"); sink.register_row("pin", "irq_nm");
    endfunction
    function void set_regime(int id, string value);
      case (id)
        GEN_KNOB_ID_IRQ_REGIME:   begin regime = value; set_mean(); end
        GEN_KNOB_ID_IRQ_LINE_MIX: line_mix = value;
        GEN_KNOB_ID_IRQ_HOLD:     hold_knob = value;
        default: `uvm_fatal("GEN_IRQ", {"not an irq knob: ", gen_knob_name(id)})
      endcase
      `uvm_info("GEN_IRQ", $sformatf("%s <= %s", gen_knob_name(id), value), UVM_LOW)
    endfunction
    function void publish(logic [18:0] changed, bit lvl, gen_irq_hold_e h, bit from_regime);
      gen_irq_evt e = gen_irq_evt::type_id::create($sformatf("irq_%0d", events));
      e.lines_after = level; e.changed = changed; e.level = lvl; e.hold = h; e.cycle = bvif.cycle_count; e.from_regime = from_regime;
      events++;
      ap.write(e);
    endfunction
    function void apply_levels();
      vif.sw = level[0]; vif.timer = level[1]; vif.ext = level[2]; vif.fast = level[17:3]; vif.nm = level[18];
      if (sink != null && sink.source_on("pin")) begin
        int unsigned c = sink.cycle();
        for (int i = 0; i < 19; i++) if (level[i] != applied_q[i]) begin
          case (i)
            0:  sink.write_event(gen_export_line_pin_irq_software(c, level[i]));
            1:  sink.write_event(gen_export_line_pin_irq_timer(c, level[i]));
            2:  sink.write_event(gen_export_line_pin_irq_external(c, level[i]));
            18: sink.write_event(gen_export_line_pin_irq_nm(c, level[i]));
            default: sink.write_event(gen_export_line_pin_irq_fast(c, i - 3, level[i]));
          endcase
        end
      end
      applied_q = level;
    endfunction
    function void cmd_set(logic [18:0] mask, gen_irq_hold_e h, int unsigned cycles, bit from_regime);
      for (int i = 0; i < 19; i++) if (mask[i]) begin hold_of[i] = h; hold_left[i] = (h == GEN_IRQ_HOLD_CYCLES) ? (cycles == 0 ? 1 : cycles) : 0; end
      level |= mask;
      apply_levels();
      publish(mask, 1'b1, h, from_regime);
    endfunction
    function void cmd_clr(logic [18:0] mask);
      level &= ~mask;
      apply_levels();
      releases++;
      publish(mask, 1'b0, GEN_IRQ_HOLD_CYCLES, 1'b0);
    endfunction
    function void ack_seen();   // from the irq-ack MMIO handler
      logic [18:0] m = '0;
      for (int i = 0; i < 19; i++) if (level[i] && hold_of[i] == GEN_IRQ_HOLD_UNTIL_ACK) m[i] = 1'b1;
      if (m != 0) cmd_clr(m);
    endfunction
    function logic [18:0] regime_lines();
      logic [18:0] m = '0;
      int n;
      case (line_mix)
        "single":    m[$urandom_range(17, 0)] = 1'b1;
        "multi":     begin n = $urandom_range(4, 2); repeat (n) m[$urandom_range(17, 0)] = 1'b1; end
        "fast_only": m[$urandom_range(17, 3)] = 1'b1;
        "with_nmi":  begin m[$urandom_range(17, 0)] = 1'b1; if ($urandom_range(3, 0) == 0) m[18] = 1'b1; end
        default: `uvm_fatal("GEN_IRQ", {"bad knob_irq_line_mix ", line_mix})
      endcase
      return m;
    endfunction
    task run_phase(uvm_phase phase);
      bit taken_q;
      apply_levels();
      taken_q = bvif.evt_irq_taken;
      forever begin
        @(negedge vif.clk);
        if (!vif.rst_n) continue;
        begin   // releases: CYCLES countdown, UNTIL_TAKEN on an entry
          logic [18:0] rel = '0;
          for (int i = 0; i < 19; i++) if (level[i] && hold_of[i] == GEN_IRQ_HOLD_CYCLES) begin
            if (hold_left[i] > 0) hold_left[i]--;
            if (hold_left[i] == 0) rel[i] = 1'b1;
          end
          if (bvif.evt_irq_taken != taken_q) begin
            // only the line the DUT took is released: the entry's vector cause (31 = the nm line) names it, so the other
            // held lines stay pending for their own entries, as a real source would
            int taken_line = (bvif.evt_irq_taken_cause == ibex_pkg::ExcCauseIrqNm.lower_cause) ? 18 : gen_irq_line_of_cause(bvif.evt_irq_taken_cause);
            taken_q = bvif.evt_irq_taken;
            if (taken_line >= 0 && level[taken_line] && hold_of[taken_line] == GEN_IRQ_HOLD_UNTIL_TAKEN) rel[taken_line] = 1'b1;
          end
          if (rel != 0) cmd_clr(rel);
        end
        if (event_mean != 0) begin   // regime engine: geometric inter-arrival with the regime's mean
          if ($urandom_range(event_mean - 1, 0) == 0) begin
            gen_irq_hold_e h = (hold_knob == "pulse") ? GEN_IRQ_HOLD_CYCLES :
                               (hold_knob == "through_handler") ? GEN_IRQ_HOLD_UNTIL_ACK : GEN_IRQ_HOLD_UNTIL_TAKEN;
            logic [18:0] m = regime_lines();
            if (m[18]) begin m[18] = 1'b0; cmd_set(19'h40000, GEN_IRQ_HOLD_CYCLES, 1, 1'b1); end
            if (m != 0) cmd_set(m, h, (hold_knob == "pulse") ? 1 : $urandom_range(cfg.irq_hold_max, cfg.irq_hold_min), 1'b1);
            regime_events++;
          end
        end
      end
    endtask
    function void report_phase(uvm_phase phase);
      `uvm_info("GEN_IRQ", $sformatf("events=%0d releases=%0d regime_events=%0d final_levels=%05h", events, releases, regime_events, level), UVM_LOW)
    endfunction
  endclass

  // gen_dbg_driver (C3.7): debug_req_i level from DBG_REQ (arg0 1/0, arg1 hold policy 0 CYCLES(arg2) /
  // 1 UNTIL_DEBUG_MODE / 2 STICKY) and from knob_debug_req_regime (none / sparse / storm).
  class gen_dbg_driver extends uvm_component;
    `uvm_component_utils(gen_dbg_driver)
    virtual gen_dbg_if    vif;
    virtual gen_bridge_if bvif;
    gen_env_cfg cfg;
    uvm_analysis_port #(gen_irq_evt) ap;   // reuses the event item: changed[0] = req, level, cycle
    gen_export_sink sink;                  // E pin debug_req line per change
    string regime;
    int unsigned event_mean = 0;   // regime_windows.dbg_event_mean of the current regime (0 = no autonomous requests)
    function void set_mean();
      if (!gen_regime_scalar("dbg_event_mean", regime, event_mean)) `uvm_fatal("GEN_DBG", {"no dbg_event_mean for regime ", regime})
    endfunction
    int unsigned hold_policy = 0, hold_left = 0, requests = 0, releases = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      ap = new("ap", this);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_dbg_if)::get(this, "", "vif", vif)) `uvm_fatal("GEN_DBG", "vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", bvif)) `uvm_fatal("GEN_DBG", "bridge_vif not in uvm_config_db")
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_DBG", "cfg not in uvm_config_db")
      regime = cfg.knob_debug_req_regime; set_mean();
    endfunction
    function void end_of_elaboration_phase(uvm_phase phase);
      super.end_of_elaboration_phase(phase);
      if (sink != null) sink.register_row("pin", "debug_req");
    endfunction
    function void publish(bit lvl);
      gen_irq_evt e = gen_irq_evt::type_id::create($sformatf("dbg_%0d", requests + releases));
      e.lines_after = {18'h0, vif.req}; e.changed = 19'h1; e.level = lvl; e.cycle = bvif.cycle_count;
      ap.write(e);
    endfunction
    function void cmd(bit assert_req, int unsigned policy, int unsigned cycles);
      if (assert_req) begin
        vif.req = 1'b1; hold_policy = policy; hold_left = (policy == 0) ? (cycles == 0 ? 1 : cycles) : 0;
        requests++; publish(1'b1);
      end else begin
        vif.req = 1'b0; releases++; publish(1'b0);
      end
      if (sink != null && sink.source_on("pin")) sink.write_event(gen_export_line_pin_debug_req(sink.cycle(), vif.req));
    endfunction
    function void set_regime(string value);
      regime = value; set_mean();
      `uvm_info("GEN_DBG", {"knob_debug_req_regime <= ", value}, UVM_LOW)
    endfunction
    task run_phase(uvm_phase phase);
      bit entered_q = bvif.evt_dbg_entered;
      forever begin
        @(negedge vif.clk);
        if (!vif.rst_n) continue;
        if (vif.req) begin
          if (hold_policy == 0) begin if (hold_left > 0) hold_left--; if (hold_left == 0) cmd(1'b0, 0, 0); end
          else if (hold_policy == 1 && bvif.evt_dbg_entered != entered_q) cmd(1'b0, 0, 0);
        end
        entered_q = bvif.evt_dbg_entered;
        if (event_mean != 0 && !vif.req) begin
          if ($urandom_range(event_mean - 1, 0) == 0) cmd(1'b1, 1, 0);
        end
      end
    endtask
    function void report_phase(uvm_phase phase);
      `uvm_info("GEN_DBG", $sformatf("requests=%0d releases=%0d", requests, releases), UVM_LOW)
    endfunction
  endclass

  // ------------------------------------------------------------------------------------------
  // Slow control driver: fetch_enable_i (reset value from +gen_fetch_en_at_reset, then FETCH_EN
  // commands: 0 = Off, 1 = On, 2 = an invalid MuBi encoding) and mcounteren_writable_i from
  // knob_mcounteren_writable (on / off / invalid).
  class gen_ctrl_driver extends uvm_component;
    `uvm_component_utils(gen_ctrl_driver)
    virtual gen_ctrl_if vif;
    gen_env_cfg cfg;
    int unsigned fetch_en_changes = 0;
    gen_export_sink sink;          // E pin fetch_enable / mcounteren_writable lines (initial level, then every change)
    logic [31:0] fetch_en_q [$];   // FETCH_EN arguments waiting for the next falling edge
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual gen_ctrl_if)::get(this, "", "vif", vif))
        `uvm_fatal("GEN_CTRL", "vif not in uvm_config_db")
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg))
        `uvm_fatal("GEN_CTRL", "cfg not in uvm_config_db")
      vif.fetch_enable = cfg.fetch_en_at_reset ? ibex_pkg::IbexMuBiOn : ibex_pkg::IbexMuBiOff;
      case (cfg.knob_mcounteren_writable)
        "on":      vif.mcounteren_writable = ibex_pkg::IbexMuBiOn;
        "off":     vif.mcounteren_writable = ibex_pkg::IbexMuBiOff;
        "invalid": vif.mcounteren_writable = ibex_pkg::ibex_mubi_t'(0);
        default: `uvm_fatal("GEN_CTRL", {"bad knob_mcounteren_writable ", cfg.knob_mcounteren_writable})
      endcase
    endfunction
    function void end_of_elaboration_phase(uvm_phase phase);
      super.end_of_elaboration_phase(phase);
      if (sink == null) return;
      sink.register_row("pin", "fetch_enable"); sink.register_row("pin", "mcounteren_writable");
    endfunction
    function void queue_fetch_en(logic [31:0] v);
      fetch_en_q.push_back(v);
    endfunction
    function void set_fetch_en(logic [31:0] v);
      case (v)
        32'd0:   vif.fetch_enable = ibex_pkg::IbexMuBiOff;
        32'd1:   vif.fetch_enable = ibex_pkg::IbexMuBiOn;
        default: vif.fetch_enable = ibex_pkg::ibex_mubi_t'(0);   // invalid encoding acts as Off (CTRL-04)
      endcase
      fetch_en_changes++;
      if (sink != null && sink.source_on("pin")) sink.write_event(gen_export_line_pin_fetch_enable(sink.cycle(), int'(vif.fetch_enable)));
      `uvm_info("GEN_CTRL", $sformatf("fetch_enable_i <= %s (FETCH_EN arg %0d)", gen_mubi_str(vif.fetch_enable), v), UVM_LOW)
    endfunction
    task run_phase(uvm_phase phase);
      bit init_done = 0;
      forever begin
        @(negedge vif.clk);
        if (vif.rst_n && !init_done) begin   // the levels at reset release, so a consumer knows the starting value
          init_done = 1;
          if (sink != null && sink.source_on("pin")) begin
            sink.write_event(gen_export_line_pin_fetch_enable(sink.cycle(), int'(vif.fetch_enable)));
            sink.write_event(gen_export_line_pin_mcounteren_writable(sink.cycle(), int'(vif.mcounteren_writable)));
          end
        end
        if (vif.rst_n && fetch_en_q.size() > 0) set_fetch_en(fetch_en_q.pop_front());
      end
    endtask
  endclass

  // ------------------------------------------------------------------------------------------
  // Program-visible registers: end of test (tohost watch and the EOT register), signature, irq ack,
  // phase marker. Each turns a store into a bridge event; the irq-ack and phase hooks grow in step 2.
  class gen_eot_handler extends gen_mmio_handler;
    virtual gen_bridge_if vif;
    function new(virtual gen_bridge_if v); vif = v; endfunction
    virtual function void on_write(logic [31:0] addr, logic [31:0] data, logic [3:0] be);
      vif.evt_eot_code  = data;
      vif.evt_eot_count = vif.evt_eot_count + 16'd1;
      vif.evt_eot_seen  = ~vif.evt_eot_seen;
      // riscv-dv programs spin on the tohost store: report the first at LOW, the rest at HIGH
      uvm_report_info("GEN_EOT", $sformatf("end-of-test store 0x%08h at 0x%08h (store %0d)", data, addr, vif.evt_eot_count),
                      vif.evt_eot_count == 1 ? UVM_LOW : UVM_HIGH);
    endfunction
  endclass

  class gen_record_handler extends gen_mmio_handler;
    string       tag;
    int unsigned writes = 0;
    logic [31:0] last_data = '0, last_addr = '0;
    gen_irq_driver irq;   // set on the irq-ack window: a store releases the UNTIL_ACK lines
    function new(string t); tag = t; endfunction
    virtual function void on_write(logic [31:0] addr, logic [31:0] data, logic [3:0] be);
      writes++; last_data = data; last_addr = addr;
      uvm_report_info(tag, $sformatf("store 0x%08h at 0x%08h (be %b)", data, addr, be), UVM_HIGH);
      if (irq != null) irq.ack_seen();
    endfunction
  endclass
endpackage
