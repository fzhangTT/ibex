// gen_irq_if: the interrupt pins of gen_dut_top (architecture C3.6), driven by gen_irq_driver as levels;
// irq_pending_o observed for the irq_pending checker. Line numbering used by the bridge and the checkers:
// 0 software, 1 timer, 2 external, 3..17 fast[0..14], 18 nm.
interface gen_irq_if (input logic clk, input logic rst_n);
  logic        sw      = 1'b0;
  logic        timer   = 1'b0;
  logic        ext     = 1'b0;
  logic [14:0] fast    = '0;
  logic        nm      = 1'b0;
  logic        pending;          // irq_pending_o
  function automatic logic [18:0] lines();
    return {nm, fast, ext, timer, sw};
  endfunction
endinterface
