// gen_tb_top: the VCS -top and cocotb TOPLEVEL of the generated TB (architecture C2). Declares the
// 19 configuration parameters the opentitan build sets with -pvalue+ and forwards them to gen_dut_top
// u_dut; instantiates clock/reset, the cocotb bridge (gen_bridge_if u_bridge_if) and, from build step
// 1c on, the bus interfaces with their agents, the icache RAM models and the scramble-key responder;
// the interrupt/debug pins stay tied idle until their agents land in step 2.
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
    forever #(ClkHalfPeriodNs * 1ns) clk = ~clk;   // explicit unit: Python converts cycles with GEN_CLK_PERIOD_NS
  end
  initial begin
    rst_n = 1'b0;
    repeat (ResetCycles) @(posedge clk);
    rst_n = 1'b1;
  end

  // boot_addr_i and hart_id_i from their plusargs (names from gen_tb_pkg); defaults from the rendered map.
  logic [31:0] boot_addr = GEN_BOOT_ADDR_DEFAULT;
  logic [31:0] hart_id = '0;
  initial begin
    logic [31:0] h;
    if ($value$plusargs({PLUSARG_BOOT_ADDR, "=%h"}, h)) boot_addr = h;
    if ($value$plusargs({PLUSARG_HART_ID, "=%h"}, h)) hart_id = h;
  end

  // Time-0 guards: the mirrored MemDataWidth equals the DUT port width, and every derived constant's
  // Python/C literal (_PY, rendered from rtl/ibex_pkg.sv) equals its SV expression.
  initial begin
    if (MemDataWidth != $bits(u_dut.instr_rdata_i))
      $fatal(1, "GEN_WIDTH_GUARD: MemDataWidth %0d != DUT instr_rdata_i width %0d", MemDataWidth, $bits(u_dut.instr_rdata_i));
    if (GEN_IBUS_MAX_OUTSTANDING != GEN_IBUS_MAX_OUTSTANDING_PY)
      $fatal(1, "GEN_WIDTH_GUARD: GEN_IBUS_MAX_OUTSTANDING sv %0d != rendered %0d", GEN_IBUS_MAX_OUTSTANDING, GEN_IBUS_MAX_OUTSTANDING_PY);
    if (GEN_CSR_MARCHID_VALUE != GEN_CSR_MARCHID_VALUE_PY || GEN_CSR_CPUCTRLSTS != GEN_CSR_CPUCTRLSTS_PY ||
        GEN_CSR_SECURESEED != GEN_CSR_SECURESEED_PY)
      $fatal(1, "GEN_WIDTH_GUARD: CSR constants sv %08h/%03h/%03h != rendered %08h/%03h/%03h", GEN_CSR_MARCHID_VALUE,
             GEN_CSR_CPUCTRLSTS, GEN_CSR_SECURESEED, GEN_CSR_MARCHID_VALUE_PY, GEN_CSR_CPUCTRLSTS_PY, GEN_CSR_SECURESEED_PY);
    if (GEN_MHPM_COUNTER_NUM != u_dut.MHPMCounterNum)
      $fatal(1, "GEN_WIDTH_GUARD: GEN_MHPM_COUNTER_NUM %0d != DUT MHPMCounterNum %0d", GEN_MHPM_COUNTER_NUM, u_dut.MHPMCounterNum);
    if (GEN_IRQ_FAST_W != GEN_IRQ_FAST_W_PY || GEN_IRQ_FAST_MASK != GEN_IRQ_FAST_MASK_PY)
      $fatal(1, "GEN_WIDTH_GUARD: GEN_IRQ_FAST_W/MASK sv %0d/%08h != rendered %0d/%08h", GEN_IRQ_FAST_W, GEN_IRQ_FAST_MASK, GEN_IRQ_FAST_W_PY, GEN_IRQ_FAST_MASK_PY);
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
  logic [GEN_IRQ_FAST_W-1:0]  irq_fast;
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

  // ---- bus agents (step 1c): the interfaces carry the DUT ports; drivers in gen_agents_pkg ----
  gen_bus_if #(.DataW(MemDataWidth), .Name("ibus")) u_ibus_if (.clk(clk), .rst_n(rst_n));
  gen_bus_if #(.DataW(MemDataWidth), .Name("dbus")) u_dbus_if (.clk(clk), .rst_n(rst_n));
  assign u_ibus_if.req  = instr_req;
  assign u_ibus_if.addr = instr_addr;
  assign u_ibus_if.we   = 1'b0;
  assign u_ibus_if.be   = 4'hF;
  assign u_ibus_if.wdata = '0;
  assign instr_gnt    = u_ibus_if.gnt;
  assign instr_rvalid = u_ibus_if.rvalid;
  assign instr_rdata  = u_ibus_if.rdata;
  assign instr_err    = u_ibus_if.err;
  assign u_dbus_if.req   = data_req;
  assign u_dbus_if.addr  = data_addr;
  assign u_dbus_if.we    = data_we;
  assign u_dbus_if.be    = data_be;
  assign u_dbus_if.wdata = data_wdata;
  assign data_gnt     = u_dbus_if.gnt;
  assign data_rvalid  = u_dbus_if.rvalid;
  assign data_rdata   = u_dbus_if.rdata;
  assign data_err     = u_dbus_if.err;
  assign data_tag_i   = 1'b0;

  // ---- icache RAM models, one per way for tags and data (step 1c) -------------------------------
  for (genvar w = 0; w < IC_NUM_WAYS; w++) begin : g_icram
    gen_icache_ram #(.Width(TagSizeECC), .Depth(IC_NUM_LINES), .Name($sformatf("tag%0d", w)), .Ways(IC_NUM_WAYS), .Way(w), .IsTag(1'b1)) u_tag (
      .clk(clk), .rst_n(rst_n), .req(ic_tag_req[w]), .write(ic_tag_write), .addr(ic_tag_addr),
      .wdata(ic_tag_wdata), .rdata(ic_tag_rdata[w]));
    gen_icache_ram #(.Width(LineSizeECC), .Depth(IC_NUM_LINES), .Name($sformatf("data%0d", w)), .Ways(IC_NUM_WAYS), .Way(w)) u_data (
      .clk(clk), .rst_n(rst_n), .req(ic_data_req[w]), .write(ic_data_write), .addr(ic_data_addr),
      .wdata(ic_data_wdata), .rdata(ic_data_rdata[w]));
  end

  // ---- scramble-key responder (step 1c) -------------------------------------------------------
  gen_scrkey_if u_scrkey_if (.clk(clk), .rst_n(rst_n));
  assign u_scrkey_if.req  = ic_scr_key_req;
  assign ic_scr_key_valid = u_scrkey_if.valid;

  // ---- interrupt and debug drivers, observed outputs (step 2b) --------------------------------
  gen_irq_if u_irq_if (.clk(clk), .rst_n(rst_n));
  assign irq_software = u_irq_if.sw;
  assign irq_timer    = u_irq_if.timer;
  assign irq_external = u_irq_if.ext;
  assign irq_fast     = u_irq_if.fast;
  assign irq_nm       = u_irq_if.nm;
  assign u_irq_if.pending = irq_pending;
  gen_dbg_if u_dbg_if (.clk(clk), .rst_n(rst_n));
  assign debug_req = u_dbg_if.req;
  gen_misc_if u_misc_if (.clk(clk), .rst_n(rst_n));
  assign u_misc_if.alert_minor          = alert_minor;
  assign u_misc_if.alert_major_internal = alert_major_internal;
  assign u_misc_if.alert_major_bus      = alert_major_bus;
  assign u_misc_if.double_fault_seen    = double_fault_seen;
  assign u_misc_if.data_tag_o           = data_tag_o;
  assign u_misc_if.irq_pending          = irq_pending;
  assign u_misc_if.core_busy            = core_busy;
  assign u_misc_if.fetch_enable         = fetch_enable;
  assign u_misc_if.crash_dump           = crash_dump;
  gen_ctrl_if u_ctrl_if (.clk(clk), .rst_n(rst_n));
  assign fetch_enable        = u_ctrl_if.fetch_enable;
  assign mcounteren_writable = u_ctrl_if.mcounteren_writable;

  gen_dut_top #(
    .BaseIsa(BaseIsa), .PMPEnable(PMPEnable), .PMPGranularity(PMPGranularity),
    .PMPNumRegions(PMPNumRegions), .MHPMCounterNum(MHPMCounterNum), .MHPMCounterWidth(MHPMCounterWidth),
    .RV32E(RV32E), .RV32M(RV32M), .RV32B(RV32B), .RV32ZC(RV32ZC), .RegFile(RegFile),
    .BranchTargetALU(BranchTargetALU), .WritebackStage(WritebackStage), .ICache(ICache),
    .ICacheECC(ICacheECC), .ICacheScramble(ICacheScramble), .BranchPredictor(BranchPredictor),
    .DbgTriggerEn(DbgTriggerEn), .SecureIbex(SecureIbex)
  ) u_dut (
    .clk_i(clk), .rst_ni(rst_n), .hart_id_i(hart_id), .boot_addr_i(boot_addr),
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

  // ---- RVFI bundle for the monitor (step 2a) ----------------------------------------------------
  gen_rvfi_if u_rvfi_if (.clk(clk), .rst_n(rst_n));
  assign u_rvfi_if.valid = rvfi_valid;         assign u_rvfi_if.order = rvfi_order;
  assign u_rvfi_if.insn = rvfi_insn;           assign u_rvfi_if.trap = rvfi_trap;
  assign u_rvfi_if.halt = rvfi_halt;           assign u_rvfi_if.intr = rvfi_intr;
  assign u_rvfi_if.mode = rvfi_mode;           assign u_rvfi_if.ixl = rvfi_ixl;
  assign u_rvfi_if.rs1_addr = rvfi_rs1_addr;   assign u_rvfi_if.rs2_addr = rvfi_rs2_addr;
  assign u_rvfi_if.rs3_addr = rvfi_rs3_addr;   assign u_rvfi_if.rd_addr = rvfi_rd_addr;
  assign u_rvfi_if.rs1_rdata = rvfi_rs1_rdata; assign u_rvfi_if.rs2_rdata = rvfi_rs2_rdata;
  assign u_rvfi_if.rs3_rdata = rvfi_rs3_rdata; assign u_rvfi_if.rd_wdata = rvfi_rd_wdata;
  assign u_rvfi_if.pc_rdata = rvfi_pc_rdata;   assign u_rvfi_if.pc_wdata = rvfi_pc_wdata;
  assign u_rvfi_if.mem_addr = rvfi_mem_addr;   assign u_rvfi_if.mem_rdata = rvfi_mem_rdata;
  assign u_rvfi_if.mem_wdata = rvfi_mem_wdata; assign u_rvfi_if.mem_rmask = rvfi_mem_rmask;
  assign u_rvfi_if.mem_wmask = rvfi_mem_wmask; assign u_rvfi_if.mem_is_cap = rvfi_mem_is_cap;
  assign u_rvfi_if.ext_pre_mip = rvfi_ext_pre_mip;   assign u_rvfi_if.ext_post_mip = rvfi_ext_post_mip;
  assign u_rvfi_if.ext_nmi = rvfi_ext_nmi;           assign u_rvfi_if.ext_nmi_int = rvfi_ext_nmi_int;
  assign u_rvfi_if.ext_debug_req = rvfi_ext_debug_req; assign u_rvfi_if.ext_debug_mode = rvfi_ext_debug_mode;
  assign u_rvfi_if.ext_rf_wr_suppress = rvfi_ext_rf_wr_suppress;
  assign u_rvfi_if.ext_mcycle = rvfi_ext_mcycle;
  assign u_rvfi_if.ext_mhpmcounters = rvfi_ext_mhpmcounters;
  assign u_rvfi_if.ext_mhpmcountersh = rvfi_ext_mhpmcountersh;
  assign u_rvfi_if.ext_ic_scr_key_valid = rvfi_ext_ic_scr_key_valid;
  assign u_rvfi_if.ext_irq_valid = rvfi_ext_irq_valid;
  assign u_rvfi_if.ext_expanded_insn_valid = rvfi_ext_expanded_insn_valid;
  assign u_rvfi_if.ext_expanded_insn = rvfi_ext_expanded_insn;
  assign u_rvfi_if.ext_expanded_insn_last = rvfi_ext_expanded_insn_last;

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
    uvm_config_db#(virtual gen_bus_if)::set(null, "uvm_test_top.env.ibus_agent*", "vif", u_ibus_if);
    uvm_config_db#(virtual gen_bus_if)::set(null, "uvm_test_top.env.dbus_agent*", "vif", u_dbus_if);
    uvm_config_db#(virtual gen_scrkey_if)::set(null, "uvm_test_top.env.scrkey*", "vif", u_scrkey_if);
    uvm_config_db#(virtual gen_ctrl_if)::set(null, "uvm_test_top.env.ctrl*", "vif", u_ctrl_if);
    uvm_config_db#(virtual gen_ctrl_if)::set(null, "uvm_test_top.env.isa_cov", "vif", u_ctrl_if);   // cp_mcen_gate reads the pin at the write
    uvm_config_db#(virtual gen_irq_if)::set(null, "uvm_test_top.env.isa_cov", "irq_vif", u_irq_if);   // the pins pending at the reset release (gen_rst_boot_cg)
    uvm_config_db#(virtual gen_dbg_if)::set(null, "uvm_test_top.env.isa_cov", "dbg_vif", u_dbg_if);
    uvm_config_db#(virtual gen_rvfi_if)::set(null, "uvm_test_top.env.rvfi_mon*", "vif", u_rvfi_if);
    uvm_config_db#(virtual gen_irq_if)::set(null, "uvm_test_top.env.irq*", "vif", u_irq_if);
    uvm_config_db#(virtual gen_dbg_if)::set(null, "uvm_test_top.env.dbg*", "vif", u_dbg_if);
    uvm_config_db#(virtual gen_misc_if)::set(null, "uvm_test_top.env.misc_mon*", "vif", u_misc_if);
    uvm_config_db#(virtual gen_bus_if)::set(null, "uvm_test_top.env.misc_mon*", "ibus_vif", u_ibus_if);
    uvm_config_db#(virtual gen_bus_if)::set(null, "uvm_test_top.env.misc_mon*", "dbus_vif", u_dbus_if);
    run_test();
  end
endmodule
