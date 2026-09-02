// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// Entire body compiles away when COCOTB_SIM is undefined (core_ibex_cocotb_if doesn't exist
// otherwise).
`ifdef COCOTB_SIM

// Holds a run_phase objection open while cocotb owns stimulus, so UVM doesn't tear down
// component threads out from under Python before it is done. See core_ibex_cocotb_if for the
// handshake bits.
class core_ibex_cocotb_monitor extends uvm_component;

  `uvm_component_utils(core_ibex_cocotb_monitor)

  virtual core_ibex_cocotb_if cocotb_vif;

  function new(string name = "core_ibex_cocotb_monitor", uvm_component parent = null);
    super.new(name, parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if (!uvm_config_db#(virtual core_ibex_cocotb_if)::get(null, "", "cocotb_if", cocotb_vif)) begin
      `uvm_fatal(`gfn, "Cannot get cocotb_if")
    end
  endfunction

  // Race-free handshake: cctb_alive (activation) is awaited before cocotb_active is ever
  // sampled, so a slow-starting Python process can't be mistaken for "never going active" at
  // time zero.
  virtual task run_phase(uvm_phase phase);
    phase.raise_objection(this);
    wait (cocotb_vif.cctb_alive == 1'b1);
    wait (cocotb_vif.cocotb_active == 1'b1);
    wait (cocotb_vif.cocotb_active == 1'b0);
    phase.drop_objection(this);
  endtask

  virtual function void final_phase(uvm_phase phase);
    cocotb_vif.uvm_finished = 1'b1;
  endfunction

endclass

`endif // COCOTB_SIM
