// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// DPI export letting Python trigger a named global uvm_event synchronously. `` `include ``d
// directly into core_ibex_tb_top's module body (not a separate compile unit) so the exported
// task's DPI scope is exactly "core_ibex_tb_top" — the scope name uvm_bridge.py targets via
// svSetScope(svGetScopeFromName(...)) before calling in. Entire body compiles away when
// COCOTB_SIM is undefined, since only the cocotb overlay ever calls this.
`ifdef COCOTB_SIM

task automatic cocotb_trigger_uvm_event(input string ev_name);
  uvm_pkg::uvm_event ev;
  ev = uvm_pkg::uvm_event_pool::get_global(ev_name);
  ev.trigger();
endtask

export "DPI-C" task cocotb_trigger_uvm_event;

`endif // COCOTB_SIM
