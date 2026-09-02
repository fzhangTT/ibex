// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// Handshake bits shared between the SV TB and the cocotb (Python) side. Entire body compiles
// away when COCOTB_SIM is undefined, so the stock flow is unaffected.
`ifdef COCOTB_SIM

interface core_ibex_cocotb_if ();

  // Set by Python once its process is alive and driving the handshake.
  bit cctb_alive = 1'b0;
  // Set by Python for the duration of active stimulus.
  bit cocotb_active = 1'b0;
  // Set by the UVM monitor's final_phase(); Python polls this before returning from finish().
  bit uvm_finished = 1'b0;
  // Set by the SV side once its cocotb-triggered event listener is armed; Python awaits it
  // before the first trigger so no event is lost (wired up starting with Milestone B).
  bit uvm_ready = 1'b0;

  // Counts IRQ_TAKEN controller-state entries (see core_ibex_tb_top.sv); the checker Python reads
  // at finish() to attribute handler entries to its own cocotb_irq_raise triggers. Driven solely
  // by tb_top's always_ff (no initializer here — VCS treats one as a second driver).
  int unsigned handler_entry_count;

  // Lets Python confirm this snapshot was actually compiled with COCOTB_SIM (quasar pattern),
  // rather than inferring it from whether this interface happens to exist in the hierarchy.
  bit COCOTB_SIM__DEFINED = 1'b1;

  // A dead/unresponsive cocotb process (e.g. a Python import error) must fail loud and fast
  // rather than hang a VCS license waiting for a $finish that will never come.
  initial begin
    #100ns;
    if (!cctb_alive) begin
      $fatal(1,
        "cocotb failed to start (cctb_alive still 0 at 100ns) — check python import errors in the sim log");
    end
  end

endinterface

`endif // COCOTB_SIM
