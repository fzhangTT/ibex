// gen_scrkey_if: the scramble-key handshake pins of gen_dut_top (architecture C3.5): ic_scr_key_req_o
// (one-cycle pulse from the core) and ic_scr_key_valid_i (driven by gen_scrkey_driver).
interface gen_scrkey_if (input logic clk, input logic rst_n);
  logic req;
  logic valid;
endinterface
