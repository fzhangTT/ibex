// gen_b8_probe.sv: the B8 assertion (T-225, rtl-arch's gen_b8_rtl_facts.md section 6): a dummy instruction must not enter the
// IF-ID register while the compressed decoder's Zcmp expansion FSM moves. A probe bind behind a knob (LOG-067): off by default,
// because the DUT fails it on every dummy insertion inside an expansion (the B8 defect); the reproducer runs turn it on.
module gen_b8_probe
  import uvm_pkg::*;
(
  input logic clk_i,
  input logic rst_ni,
  input logic pipe_we_i,     // ibex_if_stage if_id_pipe_reg_we
  input logic dummy_i,       // ibex_if_stage gen_dummy_instr.insert_dummy_instr
  input logic fsm_stable_i   // compressed_decoder_i: cm_state_d == cm_state_q, cm_rlist_d == cm_rlist_q, cm_sp_offset_d == cm_sp_offset_q
);
  bit en = 1'b0;
  initial begin
    int v;
    if ($value$plusargs({gen_tb_pkg::PLUSARG_CHK_SVA_B8, "=%d"}, v)) en = (v != 0);
    if ($value$plusargs({gen_tb_pkg::PLUSARG_CHK_ALL, "=%d"}, v) && v == 0) en = 1'b0;
  end
  sva_b8_dummy_in_expansion: assert property (@(posedge clk_i) disable iff (!rst_ni || !en) (pipe_we_i && dummy_i) |-> fsm_stable_i)
    else `uvm_error("sva_b8_dummy_in_expansion", $sformatf("GEN_PROTO sva_b8_dummy_in_expansion: a dummy instruction entered IF-ID while the Zcmp expansion FSM moved (time %0t)", $time))
endmodule
