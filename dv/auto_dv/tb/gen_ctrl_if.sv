// gen_ctrl_if: slow control inputs of gen_dut_top driven by the TB (architecture C1/C3): fetch_enable_i
// (MuBi; bridge command FETCH_EN) and mcounteren_writable_i (knob_mcounteren_writable). Driven by
// gen_ctrl_driver; the checkers of C4 read them as boundary facts.
interface gen_ctrl_if (input logic clk, input logic rst_n);
  import ibex_pkg::*;
  ibex_mubi_t fetch_enable        = IbexMuBiOn;
  ibex_mubi_t mcounteren_writable = IbexMuBiOn;
endinterface
