// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// gen_smoke_tb: minimal self-checking smoke TB for the cleanroom gate.
//
// Stimulus: a 3-instruction ROM (addi x1, x0, MAGIC_VAL; sw x1, MAGIC_ADDR(x0); self-loop).
// Check: an SVA property requires every store to MAGIC_ADDR to carry MAGIC_VAL; the run passes
// only when the store is observed with zero check failures, and fails loud on timeout. Pass/fail
// is decided from the collected fail counter scanned from the log, never from the exit code.

module gen_smoke_tb import ibex_pkg::*; #(
  // Parameters set by util/ibex_config.py <config> vcs_opts (-pvalue+...).
  parameter bit          RV32E            = 1'b0,
  parameter bit          BranchTargetALU  = 1'b1,
  parameter bit          WritebackStage   = 1'b1,
  parameter bit          ICache           = 1'b1,
  parameter bit          ICacheECC        = 1'b1,
  parameter bit          ICacheScramble   = 1'b1,
  parameter bit          BranchPredictor  = 1'b0,
  parameter bit          DbgTriggerEn     = 1'b1,
  parameter bit          SecureIbex       = 1'b1,
  parameter bit          PMPEnable        = 1'b1,
  parameter int unsigned PMPGranularity   = 0,
  parameter int unsigned PMPNumRegions    = 16,
  parameter int unsigned MHPMCounterNum   = 10,
  parameter int unsigned MHPMCounterWidth = 32
);

  localparam logic [31:0] BootAddr  = 32'h8000_0000;             // reset fetch at BootAddr + 0x80
  localparam logic [31:0] MagicAddr = 32'h0000_0040;
  localparam logic [31:0] MagicVal  = 32'h0000_05A5;

  // Program: encodings hand-assembled for this stimulus.
  localparam logic [31:0] InsnAddiX1Magic = 32'h5A50_0093;       // addi x1, x0, 0x5A5
  localparam logic [31:0] InsnSwX1Magic   = 32'h0410_2023;       // sw   x1, 0x40(x0)
  localparam logic [31:0] InsnSelfLoop    = 32'h0000_006F;       // jal  x0, 0

  // ICacheScramble shapes only the wrapper's stub equipment; consume it to absorb the -pvalue.
  logic unused_params;
  assign unused_params = &{1'b0, ICacheScramble, 1'b0};

  logic clk, rst_n;
  int unsigned seed;
  int unsigned fail_count = 0;
  int unsigned magic_store_seen = 0;

  // Clock / reset.
  initial begin
    clk = 1'b0;
    forever #5ns clk = ~clk;
  end

  initial begin
    rst_n = 1'b0;
    repeat (10) @(posedge clk);
    rst_n = 1'b1;
  end

  // One run seed drives every source of randomness; this TB has none, but the seed is recorded
  // per the reproducibility rule (SIM_RECIPE.md section 5).
  initial begin
    if (!$value$plusargs("ntb_random_seed=%d", seed)) seed = 0;
    $display("GEN_SMOKE: seed = %0d", seed);
  end

  // Fetch enable: off out of reset, on shortly after.
  ibex_mubi_t fetch_enable;
  initial begin
    fetch_enable = IbexMuBiOff;
    wait (rst_n);
    repeat (20) @(posedge clk);
    fetch_enable = IbexMuBiOn;
    $display("GEN_SMOKE: fetch enabled at %0t", $time);
  end

  // DUT wrapper hookup.
  logic        instr_req, instr_gnt, instr_rvalid;
  logic [31:0] instr_addr, instr_rdata;
  logic        data_req, data_gnt, data_rvalid, data_we;
  logic [3:0]  data_be;
  logic [31:0] data_addr, data_wdata, data_rdata;
  logic        alert_minor, alert_major_internal, alert_major_bus;
  ibex_mubi_t  core_busy;

  gen_dut_top #(
    .PMPEnable       (PMPEnable),
    .PMPGranularity  (PMPGranularity),
    .PMPNumRegions   (PMPNumRegions),
    .MHPMCounterNum  (MHPMCounterNum),
    .MHPMCounterWidth(MHPMCounterWidth),
    .RV32E           (RV32E),
    .BranchTargetALU (BranchTargetALU),
    .WritebackStage  (WritebackStage),
    .ICache          (ICache),
    .ICacheECC       (ICacheECC),
    .BranchPredictor (BranchPredictor),
    .DbgTriggerEn    (DbgTriggerEn),
    .SecureIbex      (SecureIbex)
  ) u_gen_dut (
    .clk_i (clk),
    .rst_ni(rst_n),

    .hart_id_i  (32'd0),
    .boot_addr_i(BootAddr),

    .instr_req_o   (instr_req),
    .instr_gnt_i   (instr_gnt),
    .instr_rvalid_i(instr_rvalid),
    .instr_addr_o  (instr_addr),
    .instr_rdata_i (instr_rdata),
    .instr_err_i   (1'b0),

    .data_req_o   (data_req),
    .data_gnt_i   (data_gnt),
    .data_rvalid_i(data_rvalid),
    .data_we_o    (data_we),
    .data_be_o    (data_be),
    .data_addr_o  (data_addr),
    .data_wdata_o (data_wdata),
    .data_rdata_i (data_rdata),
    .data_err_i   (1'b0),

    .irq_software_i(1'b0),
    .irq_timer_i   (1'b0),
    .irq_external_i(1'b0),
    .irq_fast_i    (15'b0),
    .irq_nm_i      (1'b0),
    .debug_req_i   (1'b0),

    .fetch_enable_i        (fetch_enable),
    .alert_minor_o         (alert_minor),
    .alert_major_internal_o(alert_major_internal),
    .alert_major_bus_o     (alert_major_bus),
    .core_busy_o           (core_busy)
  );

  // Instruction ROM: grant combinationally, data one cycle after grant.
  function automatic logic [31:0] gen_rom_word(input logic [31:0] addr);
    case (addr)
      BootAddr + 32'h80: return InsnAddiX1Magic;
      BootAddr + 32'h84: return InsnSwX1Magic;
      BootAddr + 32'h88: return InsnSelfLoop;
      default:           return InsnSelfLoop;   // stray fetch (e.g. a trap) parks in a loop
    endcase
  endfunction

  assign instr_gnt = instr_req;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      instr_rvalid <= 1'b0;
      instr_rdata  <= '0;
    end else begin
      instr_rvalid <= instr_req && instr_gnt;
      instr_rdata  <= gen_rom_word(instr_addr);
    end
  end

  // Data memory: grant combinationally, zero read data one cycle later; writes observed only.
  assign data_gnt = data_req;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      data_rvalid <= 1'b0;
    end else begin
      data_rvalid <= data_req && data_gnt;
    end
  end
  assign data_rdata = 32'h0;

  // THE CHECK: every accepted store to MagicAddr must carry MagicVal on a full-word strobe.
  property p_gen_magic_store_value;
    @(posedge clk) disable iff (!rst_n)
      (data_req && data_gnt && data_we && (data_addr == MagicAddr)) |->
        ((data_wdata == MagicVal) && (data_be == 4'hF));
  endproperty

  a_gen_magic_store_value : assert property (p_gen_magic_store_value) begin
    magic_store_seen++;
    $display("GEN_SMOKE: magic store observed with expected value 0x%08h at %0t",
             MagicVal, $time);
  end else begin
    fail_count++;
    // $sampled: action blocks otherwise report post-edge values, not the ones checked.
    $error("GEN_SMOKE_CHECK_FAIL: store to 0x%08h carried wdata=0x%08h be=0x%01h, expected wdata=0x%08h be=0xf",
           MagicAddr, $sampled(data_wdata), $sampled(data_be), MagicVal);
  end

  // Alerts must stay silent for this stimulus.
  always @(posedge clk) begin
    if (rst_n && (alert_minor || alert_major_internal || alert_major_bus)) begin
      fail_count++;
      $error("GEN_SMOKE_CHECK_FAIL: alert fired (minor=%0b major_internal=%0b major_bus=%0b) at %0t",
             alert_minor, alert_major_internal, alert_major_bus, $time);
    end
  end

  // End of test: verdict from the collected fail counter, on observation or on timeout.
  initial begin
    fork
      begin : observe
        wait (magic_store_seen > 0 || fail_count > 0);
        repeat (20) @(posedge clk);   // window for any late alert/assertion
      end
      begin : watchdog
        #100us;
        fail_count++;
        $error("GEN_SMOKE_CHECK_FAIL: timeout, magic store never observed");
      end
    join_any
    disable fork;
    $display("GEN_SMOKE: check evaluated %0d time(s), fail_count = %0d",
             magic_store_seen + fail_count, fail_count);
    if (fail_count == 0 && magic_store_seen > 0) $display("GEN_SMOKE: TEST PASSED");
    else                                         $display("GEN_SMOKE: TEST FAILED");
    $finish;
  end

endmodule
