// gen_ic_lookup_probe.sv: the icache lookup tag as a read-only probe (probe register P9, the C10 exception recorded as LOG-079):
// bound into ibex_icache, it publishes lookup_addr_ic1 (the tag bits the DUT compares in IC1, the cycle after the tag RAM read) to
// gen_icram_events every cycle while the knob probe_ic_lookup is on, so the misc monitor can derive the hit way for a data-RAM ECC
// injection from the TB's own tag RAM contents. It reads and never drives; off by default and debug-only (never on in a measured
// run); no checker verdict depends on it except the data-injection judgement it exists for.
module gen_ic_lookup_probe
  import gen_tb_pkg::*;
#(
  parameter int unsigned TagW = ibex_pkg::ADDR_W - ibex_pkg::IC_INDEX_HI - 1
) (
  input logic            clk_i,
  input logic            rst_ni,
  input logic [TagW-1:0] lookup_tag_i   // ibex_icache lookup_addr_ic1
);
  bit en = 1'b0;
  int unsigned cycle = 0;   // the same count as the RAM models' and gen_misc_if's (posedge clk from the reset release)

  initial begin
    int v;
    if ($value$plusargs({PLUSARG_PROBE_IC_LOOKUP, "=%d"}, v)) en = (v != 0);
  end

  always @(posedge clk_i or negedge rst_ni) if (!rst_ni) cycle <= 0; else cycle <= cycle + 1;
  always @(posedge clk_i) if (rst_ni && en) gen_icram_events::note_lookup(cycle, 32'(lookup_tag_i));
endmodule
