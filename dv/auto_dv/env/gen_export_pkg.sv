// gen_export_pkg: the record and event export (architecture Section 9, T-080). gen_export_sink is the ONE writer of the
// export file: header, R/I/E lines handed in by the RVFI monitor and the event writers, flush markers carrying the
// same-instant (records, retired, grant) counts, the end marker in extract_phase. Marker key=value pairs are decimal, every R/I/E value is hex.
// Format version 2 (T-080 step 2): the markers carry ibus_grants= dbus_grants= and the header's sources= and # events rows
// are the rows the writer instances registered (T-141), which the sink requires to cover the yaml's active list.
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
    string       rows_registered [$];    // "source/event" rows announced by writer instances
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
            if (!gen_export_source_active(name)) `uvm_warning("GEN_EXPORT", {"+", PLUSARG_EXPORT_SOURCES, " names ", name, ", a source without a writer in this build (export_active_sources); it gets no lines"})
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

    // A writer announces every (source, event) row it emits (its end_of_elaboration_phase). The header lists exactly the
    // registered rows of the knob-enabled active sources, so a deleted writer changes the header and fails Runtime's
    // emitted-set check; a row of an active source (yaml export_active_sources, the set Runtime records as emitted) with no
    // registered writer is a fatal at start of simulation in EVERY run, export on or off (T-141).
    function void register_row(string source, string ev);
      string key = {source, "/", ev};
      if (gen_export_row_header(source, ev) == "") `uvm_fatal("GEN_EXPORT", {"unknown export row ", key})
      if (!gen_export_source_active(source)) `uvm_fatal("GEN_EXPORT", {"writer registered row ", key, " but export_active_sources says ", source, " has no writer (yaml)"})
      foreach (rows_registered[i]) if (rows_registered[i] == key) return;
      rows_registered.push_back(key);
    endfunction
    function bit is_row_registered(string source, string ev);
      string key = {source, "/", ev};
      foreach (rows_registered[i]) if (rows_registered[i] == key) return 1'b1;
      return 1'b0;
    endfunction
    function bit is_registered(string s);   // the source has at least one registered row
      foreach (rows_registered[i]) if (rows_registered[i].substr(0, s.len()) == {s, "/"}) return 1'b1;
      return 1'b0;
    endfunction
    static function void split_csv(string s, ref string out [$]);
      int start = 0;
      out.delete();
      for (int i = 0; i <= s.len(); i++) if (i == s.len() || s[i] == ",") begin
        out.push_back(s.substr(start, i - 1));
        start = i + 1;
      end
    endfunction
    static function void split_row(string key, output string source, output string ev);
      for (int i = 0; i < key.len(); i++) if (key[i] == "/") begin
        source = key.substr(0, i - 1); ev = key.substr(i + 1, key.len() - 1); return;
      end
      source = key; ev = "";
    endfunction
    // the emitted set is a build property: checked before the enabled test so a build without +gen_export_file fatals too
    function void check_registered_rows();
      string rows [$], src, ev;
      split_csv(GEN_EXPORT_ROWS, rows);
      foreach (rows[i]) begin
        split_row(rows[i], src, ev);
        if (gen_export_source_active(src) && !is_row_registered(src, ev))
          `uvm_fatal("GEN_EXPORT", {"emitted row ", rows[i], " has no registered writer in this build (export_active_sources lists ", src, ")"})
      end
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
      string srcs = "", act [$], rows [$], src, ev;
      super.start_of_simulation_phase(phase);
      check_registered_rows();
      if (!enabled) return;
      fd = $fopen(cfg.export_file, "w");
      if (fd == 0) `uvm_fatal("GEN_EXPORT", {"cannot open export file ", cfg.export_file})
      // sources= : the active sources (yaml order) that registered a row and are knob-enabled; the # events rows are the
      // registered rows of those sources in the yaml's row order
      split_csv(GEN_EXPORT_ACTIVE_SOURCES, act);
      foreach (act[i]) if (is_registered(act[i]) && source_on(act[i])) begin srcs = {srcs, srcs == "" ? "" : ",", act[i]}; active_on.push_back(act[i]); end
      $fwrite(fd, "# gen_export v2 seed=%0d build_config=%s counters=%0d sources=%s fields=%s%s%s\n", cfg.seed, cfg.build_config,
              cfg.export_counters, srcs, GEN_EXPORT_RECORD_FIELDS, cfg.export_counters ? "," : "", cfg.export_counters ? GEN_EXPORT_COUNTER_FIELDS : "");
      $fwrite(fd, "# image %s\n", cfg.mem_image_set ? cfg.mem_image : "none");
      split_csv(GEN_EXPORT_ROWS, rows);
      foreach (rows[i]) begin
        split_row(rows[i], src, ev);
        if (is_row_registered(src, ev)) foreach (active_on[j]) if (active_on[j] == src) $fwrite(fd, "%s", gen_export_row_header(src, ev));
      end
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
