// gen_export_pkg: the record and event export (architecture Section 9, T-080). gen_export_sink is the ONE writer of the
// export file: header, R/I/E lines handed in by the RVFI monitor and the event writers, flush markers carrying the
// same-instant (records, retired, grant) counts, the end marker in extract_phase. Marker key=value pairs are decimal, every R/I/E value is hex.
// Format version 2 (T-080 step 2): the markers carry ibus_grants= dbus_grants= and the header's sources= is the yaml's active list.
// Line text comes from the rendered functions
// (gen_export_event_lines.svh here, gen_export_record_line.svh in gen_rvfi_pkg), so the column order is the yaml's.
package gen_export_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  import gen_cfg_pkg::*;
  `include "uvm_macros.svh"
  `include "gen_export_event_lines.svh"

  class gen_export_sink extends uvm_component;
    `uvm_component_utils(gen_export_sink)
    gen_env_cfg cfg;
    virtual gen_bridge_if bvif;
    int          fd = 0;
    bit          enabled = 0;
    int unsigned records = 0, markers = 0, events = 0, flushes = 0;
    bit          src_enabled [string];   // +gen_export_sources (all = every known source)
    string       registered [$];         // sources with a writer instance
    string       active_on [$];          // active sources enabled by the knob, header order
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_EXPORT", "cfg not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_bridge_if)::get(this, "", "bridge_vif", bvif)) `uvm_fatal("GEN_EXPORT", "bridge_vif not in uvm_config_db")
      enabled = cfg.export_file_set;
      if (cfg.export_sources == "all") begin
        foreach_source(1'b1);
      end else begin
        int start = 0;
        string s = cfg.export_sources;
        for (int i = 0; i <= s.len(); i++) begin
          if (i == s.len() || s[i] == ",") begin
            string name = s.substr(start, i - 1);
            if (!gen_export_source_known(name)) `uvm_fatal("GEN_EXPORT", {"+", PLUSARG_EXPORT_SOURCES, " names an unknown source ", name, " (known: ", GEN_EXPORT_SOURCES, ")"})
            src_enabled[name] = 1'b1;
            start = i + 1;
          end
        end
      end
    endfunction
    function void foreach_source(bit on);
      int start = 0;
      string s = GEN_EXPORT_SOURCES;
      for (int i = 0; i <= s.len(); i++) if (i == s.len() || s[i] == ",") begin
        src_enabled[s.substr(start, i - 1)] = on;
        start = i + 1;
      end
    endfunction

    // A writer announces its source once (connect time). The header's sources= is the yaml's active list (rendered
    // GEN_EXPORT_ACTIVE_SOURCES, the set Runtime records as emitted) intersected with +gen_export_sources; a writer for a
    // source the yaml calls inactive, or an active source without a writer, is a fatal at start of simulation.
    function void register_source(string s);
      if (!gen_export_source_known(s)) `uvm_fatal("GEN_EXPORT", {"unknown export source ", s})
      if (!gen_export_source_active(s)) `uvm_fatal("GEN_EXPORT", {"writer registered for ", s, " but export_active_sources says it has none (yaml)"})
      foreach (registered[i]) if (registered[i] == s) return;
      registered.push_back(s);
    endfunction
    function bit is_registered(string s);
      foreach (registered[i]) if (registered[i] == s) return 1'b1;
      return 1'b0;
    endfunction
    // the one cycle base of every E line (the bridge's posedge counter; a driver at the negedge stamps the cycle just passed)
    function int unsigned cycle();
      return bvif.cycle_count;
    endfunction
    // Writers ask before formatting a line (no cost when off).
    function bit source_on(string s);
      return enabled && src_enabled.exists(s) && src_enabled[s];
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
      string srcs = "";
      super.start_of_simulation_phase(phase);
      if (!enabled) return;
      fd = $fopen(cfg.export_file, "w");
      if (fd == 0) `uvm_fatal("GEN_EXPORT", {"cannot open export file ", cfg.export_file})
      begin   // sources= from the rendered active list, in its order; every active source must have registered a writer
        int start = 0;
        string a = GEN_EXPORT_ACTIVE_SOURCES;
        for (int i = 0; i <= a.len(); i++) if (i == a.len() || a[i] == ",") begin
          string s = a.substr(start, i - 1);
          start = i + 1;
          if (!is_registered(s)) `uvm_fatal("GEN_EXPORT", {"active source ", s, " has no registered writer in this build"})
          if (source_on(s)) begin srcs = {srcs, srcs == "" ? "" : ",", s}; active_on.push_back(s); end
        end
      end
      $fwrite(fd, "# gen_export v2 seed=%0d build_config=%s counters=%0d sources=%s fields=%s%s%s\n", cfg.seed, cfg.build_config,
              cfg.export_counters, srcs, GEN_EXPORT_RECORD_FIELDS, cfg.export_counters ? "," : "", cfg.export_counters ? GEN_EXPORT_COUNTER_FIELDS : "");
      $fwrite(fd, "# image %s\n", cfg.mem_image_set ? cfg.mem_image : "none");
      foreach (active_on[i]) $fwrite(fd, "%s", gen_export_event_header(active_on[i]));
      `uvm_info("GEN_EXPORT", {"export file ", cfg.export_file, " open; sources: ", srcs == "" ? "(none)" : srcs}, UVM_LOW)
    endfunction

    function void write_record(string line);
      if (!enabled) return;
      $fwrite(fd, "%s\n", line); records++;
      if (cfg.export_flush_every_set && cfg.export_flush_every > 0 && (records % cfg.export_flush_every) == 0) $fflush(fd);
    endfunction
    function void write_marker(string line);
      if (!enabled) return;
      $fwrite(fd, "%s\n", line); markers++;
    endfunction
    function void write_event(string line);
      if (!enabled) return;
      $fwrite(fd, "%s\n", line); events++;
    endfunction

    // EXPORT_FLUSH: the marker carries this sink's counts and the bridge's retired count read in the same call
    // (the dispatcher calls this from the bridge's cmd_valid wake, never from a clocked process); returns the seq.
    function int unsigned flush_export();
      string err;
      if (!enabled) `uvm_fatal("GEN_EXPORT", "EXPORT_FLUSH without +gen_export_file")
      flushes++;
      $fwrite(fd, "# flush seq=%0d records=%0d retired=%0d markers=%0d events=%0d ibus_grants=%0d dbus_grants=%0d cycle=%0d\n", flushes, records,
              bvif.evt_retired_count, markers, events, bvif.evt_ibus_grants, bvif.evt_dbus_grants, bvif.cycle_count);
      $fflush(fd);
      if ($ferror(fd, err) != 0) `uvm_error("GEN_EXPORT", {"write error after flush: ", err})
      return flushes;
    endfunction

    // End marker and close before the UVM report and before finish_ack (final_phase) can release Python.
    function void extract_phase(uvm_phase phase);
      string err;
      super.extract_phase(phase);
      if (!enabled) return;
      $fwrite(fd, "# end records=%0d retired=%0d markers=%0d events=%0d ibus_grants=%0d dbus_grants=%0d\n", records, bvif.evt_retired_count, markers, events,
              bvif.evt_ibus_grants, bvif.evt_dbus_grants);
      $fflush(fd);
      if ($ferror(fd, err) != 0) `uvm_error("GEN_EXPORT", {"write error at end: ", err})
      $fclose(fd); fd = 0;
    endfunction
    function void report_phase(uvm_phase phase);
      if (enabled) `uvm_info("GEN_EXPORT", $sformatf("export: records=%0d markers=%0d events=%0d flushes=%0d", records, markers, events, flushes), UVM_LOW)
    endfunction
  endclass
endpackage
