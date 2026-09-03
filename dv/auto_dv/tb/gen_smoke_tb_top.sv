// gen_smoke_tb_top: compile + elaborate + run smoke for gen_dut_top. Pure SV: no cocotb, no UVM
// environment (UVM is only linked by the compile command). It drives legal idle values, answers
// instruction fetches with NOPs through a same-cycle-grant memory, models the icache RAMs as
// plain synchronous arrays, counts RVFI retirements and alerts, and finishes after a bounded
// number of cycles. It is not the TB top; the real TB top replaces it.
//
// Every parameter of the config command is declared here so -pvalue+ reaches it and is
// forwarded to gen_dut_top unchanged.

`ifndef BaseIsa
  `define BaseIsa ibex_pkg::BaseIsaRV32I
`endif
`ifndef RV32M
  `define RV32M ibex_pkg::RV32MFast
`endif
`ifndef RV32B
  `define RV32B ibex_pkg::RV32BNone
`endif
`ifndef RV32ZC
  `define RV32ZC ibex_pkg::RV32ZcaZcbZcmp
`endif
`ifndef RegFile
  `define RegFile ibex_pkg::RegFileFF
`endif

module gen_smoke_tb_top import ibex_pkg::*; import gen_tb_pkg::*; #(
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
  // Smoke-only knobs
  parameter int unsigned         ClkHalfPeriodNs  = 5,
  parameter int unsigned         ResetCycles      = 5,
  parameter int unsigned         DefaultCycles    = 3000
);

  // Widths mirrored from gen_dut_top's derivation so the port declarations below match.
  localparam bit          MemECC       = SecureIbex;
  localparam int unsigned MemDataWidth = MemECC ? 32 + 7 : 32;
  localparam int unsigned BusSizeECC   = ICacheECC ? (BUS_SIZE + IC_DATA_ECC_SIZE) : BUS_SIZE;
  localparam int unsigned LineSizeECC  = BusSizeECC * IC_LINE_BEATS;
  localparam int unsigned TagSizeECC   = ICacheECC ? (IC_TAG_SIZE + IC_TAG_ECC_SIZE) : IC_TAG_SIZE;

  logic clk;
  logic rst_n;

  // DUT ports
  logic                      instr_req;
  logic                      instr_gnt;
  logic                      instr_rvalid;
  logic [31:0]               instr_addr;
  logic [MemDataWidth-1:0]   instr_rdata;
  logic                      data_req;
  logic                      data_gnt;
  logic                      data_rvalid;
  logic                      data_we;
  logic [3:0]                data_be;
  logic [31:0]               data_addr;
  logic [MemDataWidth-1:0]   data_wdata;
  logic [MemDataWidth-1:0]   data_rdata;
  logic                      data_tag_o;
  logic [IC_NUM_WAYS-1:0]    ic_tag_req;
  logic                      ic_tag_write;
  logic [IC_INDEX_W-1:0]     ic_tag_addr;
  logic [TagSizeECC-1:0]     ic_tag_wdata;
  logic [TagSizeECC-1:0]     ic_tag_rdata [IC_NUM_WAYS];
  logic [IC_NUM_WAYS-1:0]    ic_data_req;
  logic                      ic_data_write;
  logic [IC_INDEX_W-1:0]     ic_data_addr;
  logic [LineSizeECC-1:0]    ic_data_wdata;
  logic [LineSizeECC-1:0]    ic_data_rdata [IC_NUM_WAYS];
  logic                      ic_scr_key_req;
  logic                      irq_pending;
  crash_dump_t               crash_dump;
  logic                      double_fault_seen;
  logic                      alert_minor;
  logic                      alert_major_internal;
  logic                      alert_major_bus;
  ibex_mubi_t                core_busy;

`ifdef RVFI
  logic                      rvfi_valid;
  logic [63:0]               rvfi_order;
  logic [31:0]               rvfi_insn;
  logic                      rvfi_trap;
  logic                      rvfi_halt;
  logic                      rvfi_intr;
  logic [1:0]                rvfi_mode;
  logic [1:0]                rvfi_ixl;
  logic [4:0]                rvfi_rs1_addr;
  logic [4:0]                rvfi_rs2_addr;
  logic [4:0]                rvfi_rs3_addr;
  logic [31:0]               rvfi_rs1_rdata;
  ibex_cheriot_pkg::cap_t    rvfi_rs1_rcap;
  logic [31:0]               rvfi_rs2_rdata;
  ibex_cheriot_pkg::cap_t    rvfi_rs2_rcap;
  logic [31:0]               rvfi_rs3_rdata;
  logic [4:0]                rvfi_rd_addr;
  logic [31:0]               rvfi_rd_wdata;
  ibex_cheriot_pkg::cap_t    rvfi_rd_wcap;
  logic [31:0]               rvfi_pc_rdata;
  logic [31:0]               rvfi_pc_wdata;
  logic                      rvfi_mem_is_cap;
  logic [31:0]               rvfi_mem_addr;
  logic [3:0]                rvfi_mem_rmask;
  logic [3:0]                rvfi_mem_wmask;
  logic [31:0]               rvfi_mem_rdata;
  ibex_cheriot_pkg::cap_t    rvfi_mem_rcap;
  logic [31:0]               rvfi_mem_wdata;
  ibex_cheriot_pkg::cap_t    rvfi_mem_wcap;
  logic [31:0]               rvfi_ext_pre_mip;
  logic [31:0]               rvfi_ext_post_mip;
  logic                      rvfi_ext_nmi;
  logic                      rvfi_ext_nmi_int;
  logic                      rvfi_ext_debug_req;
  logic                      rvfi_ext_debug_mode;
  logic                      rvfi_ext_rf_wr_suppress;
  logic [63:0]               rvfi_ext_mcycle;
  logic [31:0]               rvfi_ext_mhpmcounters [10];
  logic [31:0]               rvfi_ext_mhpmcountersh [10];
  logic                      rvfi_ext_ic_scr_key_valid;
  logic                      rvfi_ext_irq_valid;
  logic                      rvfi_ext_expanded_insn_valid;
  logic [15:0]               rvfi_ext_expanded_insn;
  logic                      rvfi_ext_expanded_insn_last;
`endif

  gen_dut_top #(
    .BaseIsa         (BaseIsa),
    .PMPEnable       (PMPEnable),
    .PMPGranularity  (PMPGranularity),
    .PMPNumRegions   (PMPNumRegions),
    .MHPMCounterNum  (MHPMCounterNum),
    .MHPMCounterWidth(MHPMCounterWidth),
    .RV32E           (RV32E),
    .RV32M           (RV32M),
    .RV32B           (RV32B),
    .RV32ZC          (RV32ZC),
    .RegFile         (RegFile),
    .BranchTargetALU (BranchTargetALU),
    .WritebackStage  (WritebackStage),
    .ICache          (ICache),
    .ICacheECC       (ICacheECC),
    .ICacheScramble  (ICacheScramble),
    .BranchPredictor (BranchPredictor),
    .DbgTriggerEn    (DbgTriggerEn),
    .SecureIbex      (SecureIbex)
  ) u_dut (
    .clk_i                 (clk),
    .rst_ni                (rst_n),
    .hart_id_i             (32'd0),
    .boot_addr_i           (GEN_BOOT_ADDR_DEFAULT),

    .instr_req_o           (instr_req),
    .instr_gnt_i           (instr_gnt),
    .instr_rvalid_i        (instr_rvalid),
    .instr_addr_o          (instr_addr),
    .instr_rdata_i         (instr_rdata),
    .instr_err_i           (1'b0),

    .data_req_o            (data_req),
    .data_gnt_i            (data_gnt),
    .data_rvalid_i         (data_rvalid),
    .data_we_o             (data_we),
    .data_be_o             (data_be),
    .data_addr_o           (data_addr),
    .data_wdata_o          (data_wdata),
    .data_tag_o            (data_tag_o),
    .data_rdata_i          (data_rdata),
    .data_tag_i            (1'b0),
    .data_err_i            (1'b0),

    .ic_tag_req_o          (ic_tag_req),
    .ic_tag_write_o        (ic_tag_write),
    .ic_tag_addr_o         (ic_tag_addr),
    .ic_tag_wdata_o        (ic_tag_wdata),
    .ic_tag_rdata_i        (ic_tag_rdata),
    .ic_data_req_o         (ic_data_req),
    .ic_data_write_o       (ic_data_write),
    .ic_data_addr_o        (ic_data_addr),
    .ic_data_wdata_o       (ic_data_wdata),
    .ic_data_rdata_i       (ic_data_rdata),
    .ic_scr_key_valid_i    (1'b1),
    .ic_scr_key_req_o      (ic_scr_key_req),

    .irq_software_i        (1'b0),
    .irq_timer_i           (1'b0),
    .irq_external_i        (1'b0),
    .irq_fast_i            ('0),
    .irq_nm_i              (1'b0),
    .irq_pending_o         (irq_pending),

    .debug_req_i           (1'b0),
    .crash_dump_o          (crash_dump),
    .double_fault_seen_o   (double_fault_seen),

`ifdef RVFI
    .rvfi_valid,
    .rvfi_order,
    .rvfi_insn,
    .rvfi_trap,
    .rvfi_halt,
    .rvfi_intr,
    .rvfi_mode,
    .rvfi_ixl,
    .rvfi_rs1_addr,
    .rvfi_rs2_addr,
    .rvfi_rs3_addr,
    .rvfi_rs1_rdata,
    .rvfi_rs1_rcap,
    .rvfi_rs2_rdata,
    .rvfi_rs2_rcap,
    .rvfi_rs3_rdata,
    .rvfi_rd_addr,
    .rvfi_rd_wdata,
    .rvfi_rd_wcap,
    .rvfi_pc_rdata,
    .rvfi_pc_wdata,
    .rvfi_mem_is_cap,
    .rvfi_mem_addr,
    .rvfi_mem_rmask,
    .rvfi_mem_wmask,
    .rvfi_mem_rdata,
    .rvfi_mem_rcap,
    .rvfi_mem_wdata,
    .rvfi_mem_wcap,
    .rvfi_ext_pre_mip,
    .rvfi_ext_post_mip,
    .rvfi_ext_nmi,
    .rvfi_ext_nmi_int,
    .rvfi_ext_debug_req,
    .rvfi_ext_debug_mode,
    .rvfi_ext_rf_wr_suppress,
    .rvfi_ext_mcycle,
    .rvfi_ext_mhpmcounters,
    .rvfi_ext_mhpmcountersh,
    .rvfi_ext_ic_scr_key_valid,
    .rvfi_ext_irq_valid,
    .rvfi_ext_expanded_insn_valid,
    .rvfi_ext_expanded_insn,
    .rvfi_ext_expanded_insn_last,
`endif

    .fetch_enable_i        (IbexMuBiOn),
    .mcounteren_writable_i (IbexMuBiOn),
    .alert_minor_o         (alert_minor),
    .alert_major_internal_o(alert_major_internal),
    .alert_major_bus_o     (alert_major_bus),
    .core_busy_o           (core_busy)
  );

  // Clock and asynchronous active-low reset
  initial begin
    clk = 1'b0;
    forever #(ClkHalfPeriodNs) clk = ~clk;
  end

  initial begin
    rst_n = 1'b0;
    repeat (ResetCycles) @(posedge clk);
    rst_n = 1'b1;
  end

  // The smoke's retirement check needs the RVFI trace: refuse to run without it rather than pass
  // on the alert check alone (TB_CONTRACT Section 6 vacuous-pass guard).
`ifndef RVFI
  initial $fatal(1, "gen_smoke_tb_top requires +define+RVFI (retirement check would be vacuous)");
`endif

  // Instruction memory: every word is a NOP; same-cycle grant; response one cycle after grant
  // (rvalid never in the grant cycle). One request per cycle keeps the in-order rule trivially.
  // +gen_smoke_intg_flip=<bit> corrupts one bit of the encoded word (red run of the alert check).
  logic [MemDataWidth-1:0] nop_word;
  logic [MemDataWidth-1:0] nop_word_drv;
  int unsigned             intg_flip_bit;
  logic                    intg_flip_en;
  if (MemECC) begin : g_nop_intg
    prim_secded_inv_39_32_enc u_nop_enc (
      .data_i (GEN_RV32_NOP),
      .data_o (nop_word)
    );
  end else begin : g_nop_plain
    assign nop_word = GEN_RV32_NOP;
  end
  initial begin
    intg_flip_en = $value$plusargs({PLUSARG_SMOKE_INTG_FLIP, "=%d"}, intg_flip_bit);
    if (intg_flip_en) $display("GEN_SMOKE: corrupting NOP word bit %0d (expect alert_major_bus_o)", intg_flip_bit);
  end
  assign nop_word_drv = intg_flip_en ? (nop_word ^ (MemDataWidth'(1) << intg_flip_bit)) : nop_word;

  assign instr_gnt   = instr_req;
  assign instr_rdata = nop_word_drv;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) instr_rvalid <= 1'b0;
    else        instr_rvalid <= instr_req & instr_gnt;
  end

  // Data memory: same protocol, returns an integrity-valid zero word (the NOP program never
  // issues data accesses; the responder exists so any access stays protocol-legal).
  logic [MemDataWidth-1:0] zero_word;
  if (MemECC) begin : g_zero_intg
    prim_secded_inv_39_32_enc u_zero_enc (
      .data_i (32'd0),
      .data_o (zero_word)
    );
  end else begin : g_zero_plain
    assign zero_word = 32'd0;
  end

  assign data_gnt   = data_req;
  assign data_rdata = zero_word;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) data_rvalid <= 1'b0;
    else        data_rvalid <= data_req & data_gnt;
  end

  // Icache tag and data RAMs: synchronous single-port arrays with 1-cycle read latency, as the
  // core expects (rtl/ibex_icache.sv:466-472). Zero-initialised for the smoke only.
  for (genvar way = 0; way < IC_NUM_WAYS; way++) begin : g_ic_ram
    logic [TagSizeECC-1:0]  tag_mem  [IC_NUM_LINES];
    logic [LineSizeECC-1:0] data_mem [IC_NUM_LINES];

    initial begin
      for (int i = 0; i < IC_NUM_LINES; i++) begin
        tag_mem[i]  = '0;
        data_mem[i] = '0;
      end
    end

    // always (not always_ff): the arrays are also written by the initial block above, as in
    // vendor prim_ram_1p.sv.
    always @(posedge clk) begin
      if (ic_tag_req[way]) begin
        if (ic_tag_write) tag_mem[ic_tag_addr] <= ic_tag_wdata;
        else              ic_tag_rdata[way]    <= tag_mem[ic_tag_addr];
      end
      if (ic_data_req[way]) begin
        if (ic_data_write) data_mem[ic_data_addr] <= ic_data_wdata;
        else               ic_data_rdata[way]     <= data_mem[ic_data_addr];
      end
    end
  end

  // Smoke bookkeeping: retirements, alerts, bounded finish.
  int unsigned retired_cnt;
  int unsigned alert_cnt;
  int unsigned cycles;
  int unsigned max_cycles;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      retired_cnt <= 0;
      alert_cnt   <= 0;
    end else begin
`ifdef RVFI
      if (rvfi_valid) retired_cnt <= retired_cnt + 1;
`endif
      if (alert_minor | alert_major_internal | alert_major_bus) alert_cnt <= alert_cnt + 1;
    end
  end

  initial begin
    if (!$value$plusargs({PLUSARG_SMOKE_CYCLES, "=%d"}, max_cycles)) max_cycles = DefaultCycles;
    $display("GEN_SMOKE: max_cycles=%0d boot_addr=0x%08x", max_cycles, GEN_BOOT_ADDR_DEFAULT);
    cycles = 0;
    @(posedge rst_n);
    repeat (max_cycles) @(posedge clk);
    $display("GEN_SMOKE: retired=%0d alerts=%0d core_busy=%s irq_pending=%0d data_tag_o=%0d",
             retired_cnt, alert_cnt, gen_mubi_str(core_busy), irq_pending, data_tag_o);
`ifdef RVFI
    if (retired_cnt == 0) $fatal(1, "GEN_SMOKE_FAIL: no RVFI retirement observed");
`endif
    if (alert_cnt != 0)   $fatal(1, "GEN_SMOKE_FAIL: %0d alert cycles observed", alert_cnt);
    $display("GEN_SMOKE_PASS");
    $finish;
  end

endmodule
