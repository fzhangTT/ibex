// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// gen_dut_top: DUT wrapper for the cleanroom smoke gate (opentitan build configuration).
//
// Instantiates ibex_core + ibex_register_file_ff, mirroring the ibex_top wiring for this
// configuration. Bench equipment (out of DUT coverage scope): the ICache tag/data RAM ports are
// stubbed, the scramble-key handshake is answered with a fixed one-cycle turnaround, and the
// MemECC integrity bits on both read channels are encoded here so the TB drives plain 32-bit
// data. CHERIoT is tied off (cheriot_enable_i = IbexMuBiOff); the CHERI-touching files are in
// the compile but out of coverage scope.

`include "prim_assert.sv"

module gen_dut_top import ibex_pkg::*; import ibex_cheriot_pkg::*; #(
  parameter bit          PMPEnable        = 1'b1,
  parameter int unsigned PMPGranularity   = 0,
  parameter int unsigned PMPNumRegions    = 16,
  parameter int unsigned MHPMCounterNum   = 10,
  parameter int unsigned MHPMCounterWidth = 32,
  parameter bit          RV32E            = 1'b0,
  parameter bit          BranchTargetALU  = 1'b1,
  parameter bit          WritebackStage   = 1'b1,
  parameter bit          ICache           = 1'b1,
  parameter bit          ICacheECC        = 1'b1,
  parameter bit          BranchPredictor  = 1'b0,
  parameter bit          DbgTriggerEn     = 1'b1,
  parameter bit          SecureIbex       = 1'b1
) (
  input  logic        clk_i,
  input  logic        rst_ni,

  input  logic [31:0] hart_id_i,
  input  logic [31:0] boot_addr_i,

  // Instruction memory interface (32-bit data; integrity encoded internally)
  output logic        instr_req_o,
  input  logic        instr_gnt_i,
  input  logic        instr_rvalid_i,
  output logic [31:0] instr_addr_o,
  input  logic [31:0] instr_rdata_i,
  input  logic        instr_err_i,

  // Data memory interface (32-bit data; integrity encoded internally)
  output logic        data_req_o,
  input  logic        data_gnt_i,
  input  logic        data_rvalid_i,
  output logic        data_we_o,
  output logic [3:0]  data_be_o,
  output logic [31:0] data_addr_o,
  output logic [31:0] data_wdata_o,
  input  logic [31:0] data_rdata_i,
  input  logic        data_err_i,

  // Interrupts / debug
  input  logic        irq_software_i,
  input  logic        irq_timer_i,
  input  logic        irq_external_i,
  input  logic [14:0] irq_fast_i,
  input  logic        irq_nm_i,
  input  logic        debug_req_i,

  // Control / status
  input  ibex_mubi_t  fetch_enable_i,
  output logic        alert_minor_o,
  output logic        alert_major_internal_o,
  output logic        alert_major_bus_o,
  output ibex_mubi_t  core_busy_o
);

  // Derived localparams, same expressions as ibex_top for this configuration.
  localparam bit          Lockstep           = 1'b0;             // lockstep shadow core not wrapped
  localparam bit          DummyInstructions  = SecureIbex;
  localparam bit          RegFileECC         = 1'b0;
  localparam int unsigned RegFileDataWidth   = 32;
  localparam bit          MemECC             = SecureIbex;
  localparam int unsigned MemDataWidth       = MemECC ? 32 + 7 : 32;
  localparam int unsigned BusSizeECC         = ICacheECC ? (BUS_SIZE + IC_DATA_ECC_SIZE) : BUS_SIZE;
  localparam int unsigned LineSizeECC        = BusSizeECC * IC_LINE_BEATS;
  localparam int unsigned TagSizeECC         = ICacheECC ? (IC_TAG_SIZE + IC_TAG_ECC_SIZE) : IC_TAG_SIZE;

  // Build-configuration macros emitted by util/ibex_config.py (vlogdefines).
`ifdef BaseIsa
  localparam base_isa_e BaseIsaP = `BaseIsa;
`else
  localparam base_isa_e BaseIsaP = BaseIsaRV32IorCHERIoT;
`endif
`ifdef RV32M
  localparam rv32m_e RV32MP = `RV32M;
`else
  localparam rv32m_e RV32MP = RV32MSingleCycle;
`endif
`ifdef RV32B
  localparam rv32b_e RV32BP = `RV32B;
`else
  localparam rv32b_e RV32BP = RV32BOTEarlGrey;
`endif
`ifdef RV32ZC
  localparam rv32zc_e RV32ZCP = `RV32ZC;
`else
  localparam rv32zc_e RV32ZCP = RV32ZcaZcbZcmp;
`endif

  // CHERIoT tied off: RV32I mode, CHERI datapath in compile but inert.
  ibex_mubi_t cheriot_enable;
  assign cheriot_enable = IbexMuBiOff;

  // Register file <-> core wiring.
  logic                        dummy_instr_id, dummy_instr_wb;
  logic [4:0]                  rf_raddr_a, rf_raddr_b, rf_waddr_wb;
  logic                        rf_we_wb;
  logic [RegFileDataWidth-1:0] rf_wdata_wb, rf_rdata_a, rf_rdata_b;
  logic [REGCAP_W-1:0]         rf_wcap, rf_rcap_a, rf_rcap_b;

  // ICache RAM interface (stubbed below).
  logic [IC_NUM_WAYS-1:0] ic_tag_req, ic_data_req;
  logic                   ic_tag_write, ic_data_write;
  logic [IC_INDEX_W-1:0]  ic_tag_addr, ic_data_addr;
  logic [TagSizeECC-1:0]  ic_tag_wdata;
  logic [TagSizeECC-1:0]  ic_tag_rdata [IC_NUM_WAYS];
  logic [LineSizeECC-1:0] ic_data_wdata;
  logic [LineSizeECC-1:0] ic_data_rdata [IC_NUM_WAYS];
  logic                   ic_scr_key_req;
  logic                   scr_key_valid_q;

  // Memory read channels with bench-encoded integrity bits.
  logic [MemDataWidth-1:0] instr_rdata_core, data_rdata_core, data_wdata_core;

  if (MemECC) begin : gen_mem_rdata_ecc
    prim_secded_inv_39_32_enc u_gen_instr_intg_enc (
      .data_i(instr_rdata_i),
      .data_o(instr_rdata_core)
    );
    prim_secded_inv_39_32_enc u_gen_data_intg_enc (
      .data_i(data_rdata_i),
      .data_o(data_rdata_core)
    );
  end else begin : gen_no_mem_rdata_ecc
    assign instr_rdata_core = instr_rdata_i;
    assign data_rdata_core  = data_rdata_i;
  end

  assign data_wdata_o = data_wdata_core[31:0];

  // Bench equipment: ICache tag/data RAM stub (reads return zero; the smoke test never enables
  // the ICache, so these ports carry no traffic that reaches checking).
  for (genvar way = 0; way < IC_NUM_WAYS; way++) begin : gen_ic_stub
    assign ic_tag_rdata[way]  = '0;
    assign ic_data_rdata[way] = '0;
  end

  // Bench equipment: scramble-key request answered with a one-cycle turnaround, valid at reset.
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      scr_key_valid_q <= 1'b1;
    end else if (ic_scr_key_req) begin
      scr_key_valid_q <= 1'b0;
    end else begin
      scr_key_valid_q <= 1'b1;
    end
  end

  logic unused_tag_signals;
  logic data_tag_out;
  assign unused_tag_signals = &{1'b0, data_tag_out, ic_tag_write, ic_data_write,
                                ic_tag_addr, ic_data_addr, ic_tag_wdata, ic_data_wdata,
                                ic_tag_req, ic_data_req, 1'b0};

  logic        irq_pending, double_fault_seen;
  crash_dump_t crash_dump;
  logic        unused_status;
  assign unused_status = &{1'b0, irq_pending, double_fault_seen, crash_dump, 1'b0};

  ibex_core #(
    .PMPEnable        (PMPEnable),
    .PMPGranularity   (PMPGranularity),
    .PMPNumRegions    (PMPNumRegions),
    .MHPMCounterNum   (MHPMCounterNum),
    .MHPMCounterWidth (MHPMCounterWidth),
    .RV32E            (RV32E),
    .RV32M            (RV32MP),
    .RV32B            (RV32BP),
    .RV32ZC           (RV32ZCP),
    .BranchTargetALU  (BranchTargetALU),
    .ICache           (ICache),
    .ICacheECC        (ICacheECC),
    .BusSizeECC       (BusSizeECC),
    .TagSizeECC       (TagSizeECC),
    .LineSizeECC      (LineSizeECC),
    .BranchPredictor  (BranchPredictor),
    .DbgTriggerEn     (DbgTriggerEn),
    .WritebackStage   (WritebackStage),
    .ResetAll         (SecureIbex),
    .SecureIbex       (SecureIbex),
    .DummyInstructions(DummyInstructions),
    .RegFileECC       (RegFileECC),
    .RegFileDataWidth (RegFileDataWidth),
    .RegFileCapEccWidth(REGCAP_W),
    .MemECC           (MemECC),
    .MemDataWidth     (MemDataWidth),
    .BaseIsa          (BaseIsaP)
  ) u_ibex_core (
    .clk_i (clk_i),
    .rst_ni(rst_ni),

    .hart_id_i       (hart_id_i),
    .boot_addr_i     (boot_addr_i),
    .cheriot_enable_i(cheriot_enable),

    .instr_req_o   (instr_req_o),
    .instr_gnt_i   (instr_gnt_i),
    .instr_rvalid_i(instr_rvalid_i),
    .instr_addr_o  (instr_addr_o),
    .instr_rdata_i (instr_rdata_core),
    .instr_err_i   (instr_err_i),

    .data_req_o   (data_req_o),
    .data_gnt_i   (data_gnt_i),
    .data_rvalid_i(data_rvalid_i),
    .data_we_o    (data_we_o),
    .data_be_o    (data_be_o),
    .data_addr_o  (data_addr_o),
    .data_wdata_o (data_wdata_core),
    .data_tag_o   (data_tag_out),
    .data_rdata_i (data_rdata_core),
    .data_tag_i   (1'b0),
    .data_err_i   (data_err_i),

    .dummy_instr_id_o (dummy_instr_id),
    .dummy_instr_wb_o (dummy_instr_wb),
    .rf_raddr_a_o     (rf_raddr_a),
    .rf_raddr_b_o     (rf_raddr_b),
    .rf_waddr_wb_o    (rf_waddr_wb),
    .rf_we_wb_o       (rf_we_wb),
    .rf_wdata_wb_ecc_o(rf_wdata_wb),
    .rf_rdata_a_ecc_i (rf_rdata_a),
    .rf_rdata_b_ecc_i (rf_rdata_b),
    .rf_wcap_ecc_wb_o (rf_wcap),
    .rf_rcap_a_ecc_i  (rf_rcap_a),
    .rf_rcap_b_ecc_i  (rf_rcap_b),

    .ic_tag_req_o      (ic_tag_req),
    .ic_tag_write_o    (ic_tag_write),
    .ic_tag_addr_o     (ic_tag_addr),
    .ic_tag_wdata_o    (ic_tag_wdata),
    .ic_tag_rdata_i    (ic_tag_rdata),
    .ic_data_req_o     (ic_data_req),
    .ic_data_write_o   (ic_data_write),
    .ic_data_addr_o    (ic_data_addr),
    .ic_data_wdata_o   (ic_data_wdata),
    .ic_data_rdata_i   (ic_data_rdata),
    .ic_scr_key_valid_i(scr_key_valid_q),
    .ic_scr_key_req_o  (ic_scr_key_req),

    .irq_software_i(irq_software_i),
    .irq_timer_i   (irq_timer_i),
    .irq_external_i(irq_external_i),
    .irq_fast_i    (irq_fast_i),
    .irq_nm_i      (irq_nm_i),
    .irq_pending_o (irq_pending),

    .debug_req_i        (debug_req_i),
    .crash_dump_o       (crash_dump),
    .double_fault_seen_o(double_fault_seen),

    .fetch_enable_i        (fetch_enable_i),
    .mcounteren_writable_i (IbexMuBiOff),
    .alert_minor_o         (alert_minor_o),
    .alert_major_internal_o(alert_major_internal_o),
    .alert_major_bus_o     (alert_major_bus_o),
    .core_busy_o           (core_busy_o)
  );

  ibex_register_file_ff #(
    .BaseIsa          (BaseIsaP),
    .RV32E            (RV32E),
    .DataWidth        (RegFileDataWidth),
    .DummyInstructions(DummyInstructions),
    .WordZeroVal      (RegFileDataWidth'(prim_secded_pkg::SecdedInv3932ZeroWord))
  ) u_register_file (
    .clk_i (clk_i),
    .rst_ni(rst_ni),

    .test_en_i       (1'b0),
    .dummy_instr_id_i(dummy_instr_id),
    .dummy_instr_wb_i(dummy_instr_wb),
    .cheriot_enable_i(cheriot_enable),

    .raddr_a_i(rf_raddr_a),
    .rdata_a_o(rf_rdata_a),
    .rcap_a_o (rf_rcap_a),
    .raddr_b_i(rf_raddr_b),
    .rdata_b_o(rf_rdata_b),
    .rcap_b_o (rf_rcap_b),
    .waddr_a_i(rf_waddr_wb),
    .wdata_a_i(rf_wdata_wb),
    .wcap_a_i (rf_wcap),
    .we_a_i   (rf_we_wb)
  );

endmodule
