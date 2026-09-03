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
      case (v)
        "same_cycle": begin gnt_min = 0;  gnt_max = 0;  end
        "short":      begin gnt_min = 1;  gnt_max = 3;  end
        "long":       begin gnt_min = 4;  gnt_max = 32; end
        "random":     begin gnt_min = 0;  gnt_max = 32; end
        default: `uvm_fatal("GEN_BUS_CFG", {"bad gnt regime ", v})
      endcase
    endfunction
    function void apply_rvalid_regime(string v);
      rvalid_regime = v;
      case (v)
        "min1":   begin rvalid_min = 1; rvalid_max = 1;  end
        "short":  begin rvalid_min = 1; rvalid_max = 3;  end
        "long":   begin rvalid_min = 4; rvalid_max = 32; end
        "random": begin rvalid_min = 1; rvalid_max = 32; end
        default: `uvm_fatal("GEN_BUS_CFG", {"bad rvalid regime ", v})
      endcase
    endfunction
    function int unsigned rate_of(string v);
      case (v)
        "none":     return 0;
        "rare":     return 2;     // about 1/512
        "frequent": return 50;    // about 1/20
        default: `uvm_fatal("GEN_BUS_CFG", {"bad rate regime ", v})
      endcase
      return 0;
    endfunction
    function void apply_cap_regime(string v);
      cap_regime = v;
      case (v)
        "cap1": max_outstanding = 1;
        "cap2": max_outstanding = 2;
        "cap4": max_outstanding = 4;
        "cap8": max_outstanding = 8;
        default: `uvm_fatal("GEN_BUS_CFG", {"bad cap regime ", v})
      endcase
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
    uvm_analysis_port #(gen_bus_txn) ap;   // completed transactions with the driver's injection facts
    gen_bus_pend_t pend [$];
    int unsigned cycle = 0;
    int unsigned grants = 0, responses = 0, injected_err = 0, injected_intg = 0;
    function new(string name, uvm_component parent);
      super.new(name, parent);
      ap = new("ap", this);
    endfunction

    function logic [38:0] encode(logic [31:0] w);
      return prim_secded_pkg::prim_secded_inv_39_32_enc(w);
    endfunction

    task run_phase(uvm_phase phase);
      int unsigned gnt_wait = 0;
      bit          gnt_armed = 0;
      int unsigned last_due = 0;
      vif.gnt = 1'b0; vif.rvalid = 1'b0; vif.err = 1'b0; vif.rdata = '0;
      forever begin
        @(negedge vif.clk);
        if (!vif.rst_n) begin
          vif.gnt = 1'b0; vif.rvalid = 1'b0; vif.err = 1'b0;
          pend.delete(); gnt_armed = 0; cycle = 0; last_due = 0;
          continue;
        end
        cycle++;
        // ---- response side: at most one per cycle, in order
        vif.rvalid = 1'b0; vif.err = 1'b0;
        if (pend.size() > 0 && pend[0].due <= cycle) begin
          gen_bus_pend_t p = pend.pop_front();
          gen_bus_txn t = gen_bus_txn::type_id::create("txn");
          vif.rvalid = 1'b1;
          vif.err    = p.err;
          vif.rdata  = {p.intg, p.word};
          responses++;
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
            gnt_wait = $urandom_range(cfg.gnt_max, cfg.gnt_min);
          end
          if (gnt_wait == 0 && pend.size() < cfg.max_outstanding) begin
            gen_bus_pend_t p;
            logic [38:0] enc;
            p.addr = vif.addr; p.we = cfg.is_data ? vif.we : 1'b0; p.be = cfg.is_data ? vif.be : 4'hF;
            p.wdata = cfg.is_data ? vif.wdata[31:0] : '0;
            p.gnt_delay = 0; p.cycle_req = cycle; p.cycle_gnt = cycle; p.outstanding_at_gnt = pend.size();
            p.err = 0; p.injected = 0;
            if (cfg.err_rate > 0 && cfg.in_err_window(p.addr) && ($urandom_range(999, 0) < cfg.err_rate)) begin
              p.err = 1; p.injected = 1; injected_err++;
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
            if (cfg.intg_err_rate > 0 && cfg.in_err_window(p.addr) && ($urandom_range(999, 0) < cfg.intg_err_rate)) begin
              int b1 = $urandom_range(38, 0);
              logic [38:0] flipped = {p.intg, p.word};
              flipped[b1] = ~flipped[b1];
              if (cfg.intg_bits > 1) begin
                int b2 = (b1 + 1 + $urandom_range(37, 0)) % 39;
                flipped[b2] = ~flipped[b2];
              end
              p.intg = flipped[38:32]; p.word = flipped[31:0];
              p.injected = 1; injected_intg++;
            end
            p.rvalid_delay = $urandom_range(cfg.rvalid_max, cfg.rvalid_min);
            p.due = cycle + p.rvalid_delay;
            if (p.due <= last_due) p.due = last_due + 1;   // in-order, one response per cycle
            last_due = p.due;
            pend.push_back(p);
            vif.gnt = 1'b1;
            grants++;
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
      super.build_phase(phase);
      driver = gen_bus_driver::type_id::create("driver", this);
      driver.cfg = cfg;
      if (!uvm_config_db#(virtual gen_bus_if)::get(this, "", "vif", driver.vif))
        `uvm_fatal("GEN_BUS_AGENT", {get_full_name(), ": vif not in uvm_config_db"})
      driver.vif.chk_rvalid_legal_en = 1'b1;
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
    function int unsigned delay_cycles();
      case (cfg.knob_scr_key_delay)
        "immediate":           return 1;
        "delayed":             return $urandom_range(cfg.key_delay_max, cfg.key_delay_min);
        "withheld_then_valid": return cfg.key_never_cycles + 1;
        default: `uvm_fatal("GEN_SCRKEY", {"bad knob_scr_key_delay ", cfg.knob_scr_key_delay})
      endcase
      return 1;
    endfunction
    task run_phase(uvm_phase phase);
      int unsigned wait_n = 0;
      bit req_q = 0;
      vif.valid = cfg.key_reset_valid;
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
        req_q = vif.req;
      end
    endtask
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
    function void set_fetch_en(logic [31:0] v);
      case (v)
        32'd0:   vif.fetch_enable = ibex_pkg::IbexMuBiOff;
        32'd1:   vif.fetch_enable = ibex_pkg::IbexMuBiOn;
        default: vif.fetch_enable = ibex_pkg::ibex_mubi_t'(0);   // invalid encoding acts as Off (CTRL-04)
      endcase
      fetch_en_changes++;
      `uvm_info("GEN_CTRL", $sformatf("fetch_enable_i <= %s (FETCH_EN arg %0d)", gen_mubi_str(vif.fetch_enable), v), UVM_LOW)
    endfunction
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
    function new(string t); tag = t; endfunction
    virtual function void on_write(logic [31:0] addr, logic [31:0] data, logic [3:0] be);
      writes++; last_data = data; last_addr = addr;
      uvm_report_info(tag, $sformatf("store 0x%08h at 0x%08h (be %b)", data, addr, be), UVM_HIGH);
    endfunction
  endclass
endpackage
