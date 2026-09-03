// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml (export_events); do not edit.
// Included inside gen_export_pkg: the E line of one boundary event, `E <cycle> <source> <event> <fields...>` (all hex).
function automatic string gen_export_line_ibus_req(int unsigned cycle, int unsigned addr, int unsigned we, int unsigned be);
  return $sformatf("E %0h ibus req %0h %0h %0h", cycle, addr, we, be);
endfunction
function automatic string gen_export_line_ibus_gnt(int unsigned cycle, int unsigned addr, int unsigned we, int unsigned be, int unsigned req_cycle, int unsigned outstanding_after);
  return $sformatf("E %0h ibus gnt %0h %0h %0h %0h %0h", cycle, addr, we, be, req_cycle, outstanding_after);
endfunction
function automatic string gen_export_line_ibus_rvalid(int unsigned cycle, int unsigned addr, int unsigned we, int unsigned err, int unsigned intg_injected, int unsigned outstanding_after);
  return $sformatf("E %0h ibus rvalid %0h %0h %0h %0h %0h", cycle, addr, we, err, intg_injected, outstanding_after);
endfunction
function automatic string gen_export_line_dbus_req(int unsigned cycle, int unsigned addr, int unsigned we, int unsigned be);
  return $sformatf("E %0h dbus req %0h %0h %0h", cycle, addr, we, be);
endfunction
function automatic string gen_export_line_dbus_gnt(int unsigned cycle, int unsigned addr, int unsigned we, int unsigned be, int unsigned req_cycle, int unsigned outstanding_after);
  return $sformatf("E %0h dbus gnt %0h %0h %0h %0h %0h", cycle, addr, we, be, req_cycle, outstanding_after);
endfunction
function automatic string gen_export_line_dbus_rvalid(int unsigned cycle, int unsigned addr, int unsigned we, int unsigned err, int unsigned intg_injected, int unsigned outstanding_after);
  return $sformatf("E %0h dbus rvalid %0h %0h %0h %0h %0h", cycle, addr, we, err, intg_injected, outstanding_after);
endfunction
function automatic string gen_export_line_pin_any(int unsigned cycle, string name, int unsigned value);
  return $sformatf("E %0h pin %s %0h", cycle, name, value);
endfunction
function automatic string gen_export_line_alert_any(int unsigned cycle, string name, int unsigned value);
  return $sformatf("E %0h alert %s %0h", cycle, name, value);
endfunction
function automatic string gen_export_line_misc_any(int unsigned cycle, string name, int unsigned value);
  return $sformatf("E %0h misc %s %0h", cycle, name, value);
endfunction
function automatic string gen_export_line_icram_inject(int unsigned cycle, int unsigned way, int unsigned index);
  return $sformatf("E %0h icram inject %0h %0h", cycle, way, index);
endfunction
function automatic string gen_export_line_scrkey_any(int unsigned cycle, string name, int unsigned value);
  return $sformatf("E %0h scrkey %s %0h", cycle, name, value);
endfunction
function automatic string gen_export_line_regime_phase(int unsigned cycle, int unsigned knob_id, int unsigned value_idx, int unsigned phase_idx);
  return $sformatf("E %0h regime phase %0h %0h %0h", cycle, knob_id, value_idx, phase_idx);
endfunction
