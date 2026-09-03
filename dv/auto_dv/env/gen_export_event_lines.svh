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
function automatic string gen_export_line_pin_irq_software(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h pin irq_software %0h", cycle, value);
endfunction
function automatic string gen_export_line_pin_irq_timer(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h pin irq_timer %0h", cycle, value);
endfunction
function automatic string gen_export_line_pin_irq_external(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h pin irq_external %0h", cycle, value);
endfunction
function automatic string gen_export_line_pin_irq_fast(int unsigned cycle, int unsigned idx, int unsigned value);
  return $sformatf("E %0h pin irq_fast %0h %0h", cycle, idx, value);
endfunction
function automatic string gen_export_line_pin_irq_nm(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h pin irq_nm %0h", cycle, value);
endfunction
function automatic string gen_export_line_pin_debug_req(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h pin debug_req %0h", cycle, value);
endfunction
function automatic string gen_export_line_pin_fetch_enable(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h pin fetch_enable %0h", cycle, value);
endfunction
function automatic string gen_export_line_pin_mcounteren_writable(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h pin mcounteren_writable %0h", cycle, value);
endfunction
function automatic string gen_export_line_alert_alert_minor(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h alert alert_minor %0h", cycle, value);
endfunction
function automatic string gen_export_line_alert_alert_major_bus(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h alert alert_major_bus %0h", cycle, value);
endfunction
function automatic string gen_export_line_alert_alert_major_internal(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h alert alert_major_internal %0h", cycle, value);
endfunction
function automatic string gen_export_line_alert_double_fault_seen(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h alert double_fault_seen %0h", cycle, value);
endfunction
function automatic string gen_export_line_misc_irq_pending(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h misc irq_pending %0h", cycle, value);
endfunction
function automatic string gen_export_line_misc_irq_entry(int unsigned cycle, int unsigned order, int unsigned cause, int unsigned decidable);
  return $sformatf("E %0h misc irq_entry %0h %0h %0h", cycle, order, cause, decidable);
endfunction
function automatic string gen_export_line_misc_core_busy(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h misc core_busy %0h", cycle, value);
endfunction
function automatic string gen_export_line_misc_crash_dump_current_pc(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h misc crash_dump_current_pc %0h", cycle, value);
endfunction
function automatic string gen_export_line_misc_crash_dump_next_pc(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h misc crash_dump_next_pc %0h", cycle, value);
endfunction
function automatic string gen_export_line_misc_crash_dump_last_data_addr(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h misc crash_dump_last_data_addr %0h", cycle, value);
endfunction
function automatic string gen_export_line_misc_crash_dump_exception_pc(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h misc crash_dump_exception_pc %0h", cycle, value);
endfunction
function automatic string gen_export_line_misc_crash_dump_exception_addr(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h misc crash_dump_exception_addr %0h", cycle, value);
endfunction
function automatic string gen_export_line_icram_inject(int unsigned cycle, int unsigned way, int unsigned index);
  return $sformatf("E %0h icram inject %0h %0h", cycle, way, index);
endfunction
function automatic string gen_export_line_icram_lookup(int unsigned cycle, int unsigned index);
  return $sformatf("E %0h icram lookup %0h", cycle, index);
endfunction
function automatic string gen_export_line_icram_tag_write(int unsigned cycle, int unsigned way, int unsigned index, int unsigned valid);
  return $sformatf("E %0h icram tag_write %0h %0h %0h", cycle, way, index, valid);
endfunction
function automatic string gen_export_line_icram_fill_write(int unsigned cycle, int unsigned way, int unsigned index);
  return $sformatf("E %0h icram fill_write %0h %0h", cycle, way, index);
endfunction
function automatic string gen_export_line_scrkey_req(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h scrkey req %0h", cycle, value);
endfunction
function automatic string gen_export_line_scrkey_valid(int unsigned cycle, int unsigned value);
  return $sformatf("E %0h scrkey valid %0h", cycle, value);
endfunction
function automatic string gen_export_line_regime_phase(int unsigned cycle, int unsigned knob_id, int unsigned value_idx, int unsigned phase_idx);
  return $sformatf("E %0h regime phase %0h %0h %0h", cycle, knob_id, value_idx, phase_idx);
endfunction
