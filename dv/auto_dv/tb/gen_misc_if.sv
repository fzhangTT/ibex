// gen_misc_if: the observed-only outputs of gen_dut_top (architecture C4.2): alerts, crash dump,
// double fault, core busy, data tag, plus the fetch_enable the TB drives, sampled by gen_misc_monitor.
interface gen_misc_if (input logic clk, input logic rst_n);
  import ibex_pkg::*;
  logic        alert_minor, alert_major_internal, alert_major_bus;
  logic        double_fault_seen;
  logic        data_tag_o;
  logic        irq_pending;
  ibex_mubi_t  core_busy;
  ibex_mubi_t  fetch_enable;
  crash_dump_t crash_dump;
  int unsigned cycle = 0;
  always @(posedge clk or negedge rst_n) if (!rst_n) cycle <= 0; else cycle <= cycle + 1;
endinterface
