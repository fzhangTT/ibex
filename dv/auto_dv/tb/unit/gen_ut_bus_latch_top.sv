// gen_ut_bus_latch_top: unit test of the instant at which the reactive slave driver captures a request
// (architecture C3.2), pure SV with UVM report functions, no RTL and no core.
//
// The address a core presents is not a registered output: it settles through combinational logic during the
// cycle, and another TB driver writing a DUT input at the falling edge can move it. The bus contract fixes
// which value counts: the one the core holds at the ACCEPTING RISING EDGE, where req and gnt are both sampled
// high. A slave that reads the address at the falling edge where it decides the grant reads a mid-cycle
// settling value the core never presented at any clock edge, and answers the wrong address.
//
// This test presents one address, lets the grant happen, moves the address in the half cycle between the
// granting falling edge and the accepting rising edge, and requires the answered word to be the settled
// address's. The control does the same without moving the address, so a slave that simply answers late is
// not mistaken for a correct one.
module gen_ut_bus_latch_top;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  import gen_mem_pkg::*;
  import gen_agents_pkg::*;
  `include "uvm_macros.svh"

  // the two addresses of the order-548 wave, so the shape here is the shape that was observed
  localparam logic [31:0] ADDR_PRESENTED = 32'h8000_0348;
  localparam logic [31:0] ADDR_SETTLED   = 32'h8000_0340;
  localparam logic [31:0] WORD_PRESENTED = 32'hFEED_0348;
  localparam logic [31:0] WORD_SETTLED   = 32'hFEED_0340;

  logic clk = 1'b0, rst_n = 1'b0, rvfi_valid = 1'b0;
  always #5 clk = ~clk;

  gen_bus_if    u_ibus_if   (.clk(clk), .rst_n(rst_n));
  gen_bridge_if u_bridge_if (.clk(clk), .rst_n(rst_n), .rvfi_valid(rvfi_valid));

  int unsigned fails = 0;
  function automatic void check(string what, logic [31:0] got, logic [31:0] exp);
    bit ok = (got === exp);
    $display("%s %s got 0x%08h exp 0x%08h", ok ? "OK  " : "FAIL", what, got, exp);
    if (!ok) fails++;
  endfunction

  gen_bus_driver drv;
  gen_bus_cfg    cfg;
  gen_mem_model  m;

  // One fetch. The address is presented at a rising edge and moved to `settled` in the half cycle after the
  // granting falling edge, which is where a combinational DUT output moves when another driver writes an input
  // at that edge. Returns the word the slave answered with.
  task automatic one_fetch(logic [31:0] presented, logic [31:0] settled, output logic [31:0] word);
    @(posedge clk);
    u_ibus_if.addr = presented;
    u_ibus_if.req  = 1'b1;
    forever begin
      @(negedge clk); #1;                       // after the falling edge: the driver has decided and driven gnt
      if (u_ibus_if.gnt) begin
        u_ibus_if.addr = settled;               // the combinational address settles before the accepting edge
        break;
      end
    end
    @(posedge clk);                             // the accepting edge: req and gnt both high
    u_ibus_if.req = 1'b0;
    forever begin
      @(posedge clk);
      if (u_ibus_if.rvalid) begin
        word = u_ibus_if.rdata[31:0];
        break;
      end
    end
  endtask

  logic [31:0] w;

  initial begin
    u_ibus_if.req = 1'b0; u_ibus_if.addr = ADDR_PRESENTED; u_ibus_if.we = 1'b0; u_ibus_if.be = 4'hF;
    u_ibus_if.wdata = '0;
    m = new("ut_mem");
    m.write_masked(ADDR_PRESENTED, WORD_PRESENTED, 4'hF);
    m.write_masked(ADDR_SETTLED,   WORD_SETTLED,   4'hF);
    cfg = new("ut_cfg");
    cfg.is_data = 1'b0; cfg.rvalid_min = 1; cfg.rvalid_max = 1; cfg.max_outstanding = 4;
    cfg.err_rate = 0; cfg.intg_err_rate = 0;
    drv = new("ut_drv", null);
    drv.vif = u_ibus_if; drv.cfg = cfg; drv.mem = m; drv.bvif = u_bridge_if; drv.sink = null;
    fork drv.run_phase(null); join_none

    repeat (4) @(posedge clk);
    rst_n = 1'b1;
    repeat (2) @(posedge clk);

    // 1. SAME-CYCLE GRANT, the shape of the order-548 wave.
    cfg.gnt_min = 0; cfg.gnt_max = 0;
    one_fetch(ADDR_PRESENTED, ADDR_SETTLED, w);
    check("same-cycle grant: the word of the address held at the accepting edge", w, WORD_SETTLED);

    // 2. THE CONTROL: the same sequence with the address unmoved answers the presented address, so a slave
    //    that answered the wrong word for every request would not pass this test.
    one_fetch(ADDR_PRESENTED, ADDR_PRESENTED, w);
    check("same-cycle grant, address unmoved: the presented address's word", w, WORD_PRESENTED);

    // 3. A DELAYED GRANT: the capture instant is the accepting edge for every grant-delay shape, so the same
    //    move in the half cycle before it must give the same answer.
    cfg.gnt_min = 2; cfg.gnt_max = 2;
    one_fetch(ADDR_PRESENTED, ADDR_SETTLED, w);
    check("grant after two cycles: the word of the address held at the accepting edge", w, WORD_SETTLED);
    one_fetch(ADDR_PRESENTED, ADDR_PRESENTED, w);
    check("grant after two cycles, address unmoved: the presented address's word", w, WORD_PRESENTED);

    $display("gen_ut_bus_latch: %0d failures", fails);
    if (fails != 0) $display("GEN_UT_BUS_LATCH_FAIL");
    else            $display("GEN_UT_BUS_LATCH_PASS");
    $finish;
  end

  initial begin
    #20000;
    $display("FAIL gen_ut_bus_latch: timeout with %0d failures so far", fails);
    $display("GEN_UT_BUS_LATCH_FAIL");
    $finish;
  end
endmodule
