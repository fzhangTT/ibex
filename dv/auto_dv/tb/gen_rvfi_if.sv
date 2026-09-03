// gen_rvfi_if: the RVFI record of gen_dut_top as one bundle (architecture C4.1; RVFI is a define-gated
// DUT interface at the boundary, probe register ruling). The top assigns every field from the wrapper
// ports; gen_rvfi_monitor samples at the posedge where valid is 1.
interface gen_rvfi_if (input logic clk, input logic rst_n);
  logic        valid;
  logic [63:0] order;
  logic [31:0] insn;
  logic        trap, halt, intr;
  logic [1:0]  mode, ixl;
  logic [4:0]  rs1_addr, rs2_addr, rs3_addr, rd_addr;
  logic [31:0] rs1_rdata, rs2_rdata, rs3_rdata, rd_wdata;
  logic [31:0] pc_rdata, pc_wdata;
  logic [31:0] mem_addr, mem_rdata, mem_wdata;
  logic [3:0]  mem_rmask, mem_wmask;
  logic        mem_is_cap;
  logic [31:0] ext_pre_mip, ext_post_mip;
  logic        ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode, ext_rf_wr_suppress;
  logic [63:0] ext_mcycle;
  logic [31:0] ext_mhpmcounters [10];
  logic [31:0] ext_mhpmcountersh [10];
  logic        ext_ic_scr_key_valid, ext_irq_valid;
  logic        ext_expanded_insn_valid, ext_expanded_insn_last;
  logic [15:0] ext_expanded_insn;
  int unsigned cycle = 0;
  always @(posedge clk or negedge rst_n) if (!rst_n) cycle <= 0; else cycle <= cycle + 1;
endinterface
