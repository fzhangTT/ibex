// gen_tb_top: the VCS -top and cocotb TOPLEVEL of the generated TB (architecture C2). Declares the
// 19 configuration parameters the opentitan build sets with -pvalue+ and forwards them to gen_dut_top
// u_dut; instantiates clock/reset, the cocotb bridge (gen_bridge_if u_bridge_if) and, from build step
// 1c on, the interface agents and RAM models. Build step 1b: DUT inputs that agents will drive are
// tied to their idle values so the bridge, banner and end-of-test mechanics can be proven alone.
// Python owns the end of simulation (TB_CONTRACT Section 2): the alive watchdog here fatals when no
// Python side ever starts; UVM runs gen_base_test with finish_on_completion = 0.
module gen_tb_top import ibex_pkg::*; import gen_tb_pkg::*; #(
  parameter ibex_pkg::base_isa_e BaseIsa          = `BaseIsa,
  parameter bit                  PMPEnable        = 1'b0,
  parameter int unsigned         PMPGranularity   = 0,
  parameter int unsigned         PMPNumRegions    = 4,
  parameter int unsigned         MHPMCounterNum   = 0,
  parameter int unsigned         MHPMCounterWidth = 40,
  parameter bit                  RV32E            = 1'b0,
  parameter rv32m_e              RV32M            = `RV32M,
  parameter rv32b_e              RV32B            = `RV32B,
  parameter rv32zc_e             RV32ZC           = `RV32ZC,
  parameter regfile_e            RegFile          = `RegFile,
  parameter bit                  BranchTargetALU  = 1'b0,
  parameter bit                  WritebackStage   = 1'b0,
  parameter bit                  ICache           = 1'b0,
  parameter bit                  ICacheECC        = 1'b0,
  parameter bit                  ICacheScramble   = 1'b0,
  parameter bit                  BranchPredictor  = 1'b0,
  parameter bit                  DbgTriggerEn     = 1'b0,
  parameter bit                  SecureIbex       = 1'b0,
  parameter int unsigned         ClkHalfPeriodNs  = GEN_CLK_PERIOD_NS / 2,
  parameter int unsigned         ResetCycles      = 5
);
  import uvm_pkg::*;
  import gen_env_pkg::*;

  // Widths mirrored from gen_dut_top's derivation so the port declarations below match.
  localparam bit          MemECC       = SecureIbex;
  localparam int unsigned MemDataWidth = MemECC ? 32 + 7 : 32;
  localparam int unsigned BusSizeECC   = ICacheECC ? (BUS_SIZE + IC_DATA_ECC_SIZE) : BUS_SIZE;
  localparam int unsigned LineSizeECC  = BusSizeECC * IC_LINE_BEATS;
  localparam int unsigned TagSizeECC   = ICacheECC ? (IC_TAG_SIZE + IC_TAG_ECC_SIZE) : IC_TAG_SIZE;

`ifndef RVFI
  initial $fatal(1, "gen_tb_top requires +define+RVFI (the RVFI monitor and the retirement count would be vacuous)");
`endif

  logic clk;
  logic rst_n;
  initial begin
    clk = 1'b0;
    forever #(ClkHalfPeriodNs) clk = ~clk;
  end
  initial begin
    rst_n = 1'b0;
    repeat (ResetCycles) @(posedge clk);
    rst_n = 1'b1;
  end

  // boot_addr_i from +gen_boot_addr (name from gen_tb_pkg); default GEN_BOOT_ADDR_DEFAULT.
  logic [31:0] boot_addr = GEN_BOOT_ADDR_DEFAULT;
  initial begin
    logic [31:0] h;
    if ($value$plusargs({PLUSARG_BOOT_ADDR, "=%h"}, h)) boot_addr = h;
  end

  // ---- DUT boundary signals (agents drive the *_i side from step 1c; tied idle here) ----------
  logic                       instr_req, instr_gnt, instr_rvalid, instr_err;
  logic [31:0]                instr_addr;
  logic [MemDataWidth-1:0]    instr_rdata;
  logic                       data_req, data_gnt, data_rvalid, data_we, data_err, data_tag_o, data_tag_i;
  logic [3:0]                 data_be;
  logic [31:0]                data_addr;
  logic [MemDataWidth-1:0]    data_wdata, data_rdata;
  logic [IC_NUM_WAYS-1:0]     ic_tag_req, ic_data_req;
  logic                       ic_tag_write, ic_data_write;
  logic [IC_INDEX_W-1:0]      ic_tag_addr, ic_data_addr;
  logic [TagSizeECC-1:0]      ic_tag_wdata;
  logic [TagSizeECC-1:0]      ic_tag_rdata [IC_NUM_WAYS];
  logic [LineSizeECC-1:0]     ic_data_wdata;
  logic [LineSizeECC-1:0]     ic_data_rdata [IC_NUM_WAYS];
  logic                       ic_scr_key_valid, ic_scr_key_req;
  logic                       irq_software, irq_timer, irq_external, irq_nm, irq_pending;
  logic [14:0]                irq_fast;
  logic                       debug_req;
  crash_dump_t                crash_dump;
  logic                       double_fault_seen;
  ibex_mubi_t                 fetch_enable, mcounteren_writable, core_busy;
  logic                       alert_minor, alert_major_internal, alert_major_bus;

  // RVFI (bundled into gen_rvfi_if in step 2; the bridge counts rvfi_valid from here)
  logic        rvfi_valid;
  logic [63:0] rvfi_order;
  logic [31:0] rvfi_insn;
  logic        rvfi_trap, rvfi_halt, rvfi_intr;
  logic [1:0]  rvfi_mode, rvfi_ixl;
  logic [4:0]  rvfi_rs1_addr, rvfi_rs2_addr, rvfi_rs3_addr, rvfi_rd_addr;
  logic [31:0] rvfi_rs1_rdata, rvfi_rs2_rdata, rvfi_rs3_rdata, rvfi_rd_wdata;
  logic [31:0] rvfi_pc_rdata, rvfi_pc_wdata, rvfi_mem_addr, rvfi_mem_rdata, rvfi_mem_wdata;
  logic [3:0]  rvfi_mem_rmask, rvfi_mem_wmask;
  logic        rvfi_mem_is_cap;
  ibex_cheriot_pkg::cap_t rvfi_rs1_rcap, rvfi_rs2_rcap, rvfi_rd_wcap, rvfi_mem_rcap, rvfi_mem_wcap;
  logic [31:0] rvfi_ext_pre_mip, rvfi_ext_post_mip;
  logic        rvfi_ext_nmi, rvfi_ext_nmi_int, rvfi_ext_debug_req, rvfi_ext_debug_mode, rvfi_ext_rf_wr_suppress;
  logic [63:0] rvfi_ext_mcycle;
  logic [31:0] rvfi_ext_mhpmcounters [10];
  logic [31:0] rvfi_ext_mhpmcountersh [10];
  logic        rvfi_ext_ic_scr_key_valid, rvfi_ext_irq_valid;
  logic        rvfi_ext_expanded_insn_valid, rvfi_ext_expanded_insn_last;
  logic [15:0] rvfi_ext_expanded_insn;

  // Step 1b tie-offs (replaced by agents in step 1c: no grant, no response, valid key, no events).
  assign instr_gnt        = 1'b0;
  assign instr_rvalid     = 1'b0;
  assign instr_rdata      = '0;
  assign instr_err        = 1'b0;
  assign data_gnt         = 1'b0;
  assign data_rvalid      = 1'b0;
  assign data_rdata       = '0;
  assign data_err         = 1'b0;
  assign data_tag_i       = 1'b0;
  for (genvar w = 0; w < IC_NUM_WAYS; w++) begin : g_icram_tie
    assign ic_tag_rdata[w]  = '0;
    assign ic_data_rdata[w] = '0;
  end
  assign ic_scr_key_valid = 1'b1;
  assign irq_software     = 1'b0;
  assign irq_timer        = 1'b0;
  assign irq_external     = 1'b0;
  assign irq_fast         = '0;
  assign irq_nm           = 1'b0;
  assign debug_req        = 1'b0;
  assign fetch_enable        = IbexMuBiOn;
  assign mcounteren_writable = IbexMuBiOn;

  gen_dut_top #(
    .BaseIsa(BaseIsa), .PMPEnable(PMPEnable), .PMPGranularity(PMPGranularity),
    .PMPNumRegions(PMPNumRegions), .MHPMCounterNum(MHPMCounterNum), .MHPMCounterWidth(MHPMCounterWidth),
    .RV32E(RV32E), .RV32M(RV32M), .RV32B(RV32B), .RV32ZC(RV32ZC), .RegFile(RegFile),
    .BranchTargetALU(BranchTargetALU), .WritebackStage(WritebackStage), .ICache(ICache),
    .ICacheECC(ICacheECC), .ICacheScramble(ICacheScramble), .BranchPredictor(BranchPredictor),
    .DbgTriggerEn(DbgTriggerEn), .SecureIbex(SecureIbex)
  ) u_dut (
    .clk_i(clk), .rst_ni(rst_n), .hart_id_i(32'd0), .boot_addr_i(boot_addr),
    .instr_req_o(instr_req), .instr_gnt_i(instr_gnt), .instr_rvalid_i(instr_rvalid),
    .instr_addr_o(instr_addr), .instr_rdata_i(instr_rdata), .instr_err_i(instr_err),
    .data_req_o(data_req), .data_gnt_i(data_gnt), .data_rvalid_i(data_rvalid), .data_we_o(data_we),
    .data_be_o(data_be), .data_addr_o(data_addr), .data_wdata_o(data_wdata), .data_rdata_i(data_rdata),
    .data_tag_o(data_tag_o), .data_tag_i(data_tag_i), .data_err_i(data_err),
    .ic_tag_req_o(ic_tag_req), .ic_tag_write_o(ic_tag_write), .ic_tag_addr_o(ic_tag_addr),
    .ic_tag_wdata_o(ic_tag_wdata), .ic_tag_rdata_i(ic_tag_rdata),
    .ic_data_req_o(ic_data_req), .ic_data_write_o(ic_data_write), .ic_data_addr_o(ic_data_addr),
    .ic_data_wdata_o(ic_data_wdata), .ic_data_rdata_i(ic_data_rdata),
    .ic_scr_key_valid_i(ic_scr_key_valid), .ic_scr_key_req_o(ic_scr_key_req),
    .irq_software_i(irq_software), .irq_timer_i(irq_timer), .irq_external_i(irq_external),
    .irq_fast_i(irq_fast), .irq_nm_i(irq_nm), .irq_pending_o(irq_pending),
    .debug_req_i(debug_req), .crash_dump_o(crash_dump), .double_fault_seen_o(double_fault_seen),
    .rvfi_valid(rvfi_valid), .rvfi_order(rvfi_order), .rvfi_insn(rvfi_insn), .rvfi_trap(rvfi_trap),
    .rvfi_halt(rvfi_halt), .rvfi_intr(rvfi_intr), .rvfi_mode(rvfi_mode), .rvfi_ixl(rvfi_ixl),
    .rvfi_rs1_addr(rvfi_rs1_addr), .rvfi_rs2_addr(rvfi_rs2_addr), .rvfi_rs3_addr(rvfi_rs3_addr),
    .rvfi_rs1_rdata(rvfi_rs1_rdata), .rvfi_rs2_rdata(rvfi_rs2_rdata), .rvfi_rs3_rdata(rvfi_rs3_rdata),
    .rvfi_rs1_rcap(rvfi_rs1_rcap), .rvfi_rs2_rcap(rvfi_rs2_rcap),
    .rvfi_rd_addr(rvfi_rd_addr), .rvfi_rd_wdata(rvfi_rd_wdata), .rvfi_rd_wcap(rvfi_rd_wcap),
    .rvfi_pc_rdata(rvfi_pc_rdata), .rvfi_pc_wdata(rvfi_pc_wdata), .rvfi_mem_is_cap(rvfi_mem_is_cap),
    .rvfi_mem_addr(rvfi_mem_addr), .rvfi_mem_rmask(rvfi_mem_rmask), .rvfi_mem_wmask(rvfi_mem_wmask),
    .rvfi_mem_rdata(rvfi_mem_rdata), .rvfi_mem_rcap(rvfi_mem_rcap), .rvfi_mem_wdata(rvfi_mem_wdata),
    .rvfi_mem_wcap(rvfi_mem_wcap), .rvfi_ext_pre_mip(rvfi_ext_pre_mip), .rvfi_ext_post_mip(rvfi_ext_post_mip),
    .rvfi_ext_nmi(rvfi_ext_nmi), .rvfi_ext_nmi_int(rvfi_ext_nmi_int), .rvfi_ext_debug_req(rvfi_ext_debug_req),
    .rvfi_ext_debug_mode(rvfi_ext_debug_mode), .rvfi_ext_rf_wr_suppress(rvfi_ext_rf_wr_suppress),
    .rvfi_ext_mcycle(rvfi_ext_mcycle), .rvfi_ext_mhpmcounters(rvfi_ext_mhpmcounters),
    .rvfi_ext_mhpmcountersh(rvfi_ext_mhpmcountersh), .rvfi_ext_ic_scr_key_valid(rvfi_ext_ic_scr_key_valid),
    .rvfi_ext_irq_valid(rvfi_ext_irq_valid), .rvfi_ext_expanded_insn_valid(rvfi_ext_expanded_insn_valid),
    .rvfi_ext_expanded_insn(rvfi_ext_expanded_insn), .rvfi_ext_expanded_insn_last(rvfi_ext_expanded_insn_last),
    .fetch_enable_i(fetch_enable), .mcounteren_writable_i(mcounteren_writable),
    .alert_minor_o(alert_minor), .alert_major_internal_o(alert_major_internal),
    .alert_major_bus_o(alert_major_bus), .core_busy_o(core_busy)
  );

  // ---- cocotb bridge ---------------------------------------------------------------------------
  gen_bridge_if u_bridge_if (.clk(clk), .rst_n(rst_n), .rvfi_valid(rvfi_valid));

  // Alive watchdog (TB_CONTRACT Section 2 item 1): fails loud in hardware when no Python side starts.
  initial begin
    int unsigned budget = GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT;
    int unsigned u;
    if ($value$plusargs({PLUSARG_ALIVE_TIMEOUT, "=%d"}, u)) budget = u;
    repeat (budget) @(posedge clk);
    if (!u_bridge_if.alive)
      $fatal(1, "GEN_ALIVE_TIMEOUT: Python never set the alive bit within %0d cycles", budget);
  end

  initial begin
    uvm_config_db#(virtual gen_bridge_if)::set(null, "*", "bridge_vif", u_bridge_if);
    run_test();
  end
endmodule
