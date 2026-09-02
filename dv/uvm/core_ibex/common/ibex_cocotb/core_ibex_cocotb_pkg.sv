// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// Packages core_ibex_cocotb_monitor for import into core_ibex_test_pkg, mirroring how the other
// common/ agents (e.g. irq_agent_pkg) package their classes.
package core_ibex_cocotb_pkg;

  import uvm_pkg::*;

  `include "uvm_macros.svh"
  `include "core_ibex_cocotb_monitor.sv"

endpackage
