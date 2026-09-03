// gen_dut_top: the DUT by owner ruling (DV_prompt.txt Section 2): ibex_core plus
// ibex_register_file_ff, wired as rtl/ibex_top.sv does, every remaining ibex_core port exposed.
// No clock gate, lockstep, TRVK, cache RAM or scramble logic: those are ibex_top equipment.
//
// Wrapper decisions, each a single parameter or define so an owner answer is a one-line change
// (owner questions: dv/auto_dv/docs/gen_intervention_log.md Q-002 (revised) covers RegFileECC,
// ResetAll and RVFI; LOG-004 records the integrity-port representation choice):
//   RegFileECC = 0          ibex_top's main-core value (rtl/ibex_top.sv:215); RF ECC lives only in
//                           the out-of-scope lockstep core. Q-002.
//   ResetAll = SecureIbex   ibex_top passes Lockstep = SecureIbex (rtl/ibex_top.sv:212-213). Q-002.
//   +define+RVFI            retirement trace exposed (set by the compile command). Q-002.
//   GEN_DUT_SPLIT_INTG      undefined: bus ports exactly as ibex_core declares them (integrity in
//                           bits [MemDataWidth-1:32]); defined: ibex_top-style data/intg split,
//                           pure bit-slicing. LOG-004.
//   PMPRstCfg/PMPRstAddr/PMPRstMsecCfg stay at ibex_core's ibex_pkg defaults (all regions OFF),
//                           the values ibex_top passes; named in the banner.
//   cheriot_enable_i        tied to IbexMuBiOff internally (Section 2 ruling); test_en_i of the
//                           register file tied 0 (unused by the FF implementation).
// The five enum parameters take their defaults from the config script's +define+ values because
// VCS cannot override enum parameters from the command line (doc/02_user/integration.rst:264-269).

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

module gen_dut_top import ibex_pkg::*; import ibex_cheriot_pkg::*; #(
  parameter ibex_pkg::base_isa_e    BaseIsa                      = `BaseIsa,
  parameter bit                     PMPEnable                    = 1'b0,
  parameter int unsigned            PMPGranularity               = 0,
  parameter int unsigned            PMPNumRegions                = 4,
  parameter int unsigned            MHPMCounterNum               = 0,
  parameter int unsigned            MHPMCounterWidth             = 40,
  parameter bit                     RV32E                        = 1'b0,
  parameter rv32m_e                 RV32M                        = `RV32M,
  parameter rv32b_e                 RV32B                        = `RV32B,
  parameter rv32zc_e                RV32ZC                       = `RV32ZC,
  parameter regfile_e               RegFile                      = `RegFile,
  parameter bit                     BranchTargetALU              = 1'b0,
  parameter bit                     WritebackStage               = 1'b0,
  parameter bit                     ICache                       = 1'b0,
  parameter bit                     ICacheECC                    = 1'b0,
  // Config knob with no ibex_core consumer (selects ibex_top's RAM primitive); accepted so the
  // unchanged config command applies, forwarded nowhere.
  parameter bit                     ICacheScramble               = 1'b0,
  parameter bit                     BranchPredictor              = 1'b0,
  parameter bit                     DbgTriggerEn                 = 1'b0,
  parameter int unsigned            DbgHwBreakNum                = 1,
  parameter bit                     SecureIbex                   = 1'b0,
  parameter bit                     RegFileECC                   = 1'b0,
  parameter bit                     ResetAll                     = SecureIbex,
  parameter lfsr_seed_t             RndCnstLfsrSeed              = RndCnstLfsrSeedDefault,
  parameter lfsr_perm_t             RndCnstLfsrPerm              = RndCnstLfsrPermDefault,
  parameter int unsigned            DmBaseAddr                   = 32'h1A110000,
  parameter int unsigned            DmAddrMask                   = 32'h00000FFF,
  parameter int unsigned            DmHaltAddr                   = 32'h1A110800,
  parameter int unsigned            DmExceptionAddr              = 32'h1A110808,
  parameter logic [31:0]            CsrMvendorId                 = 32'b0,
  parameter logic [31:0]            CsrMimpId                    = 32'b0,
  // Derived exactly as rtl/ibex_top.sv:41-45, 212-227 derives them (ibex_core's own defaults
  // are the non-ECC widths and would mis-size the RAM and bus ports).
  localparam bit                    DummyInstructions            = SecureIbex,
  localparam bit                    MemECC                       = SecureIbex,
  localparam int unsigned           MemDataWidth                 = MemECC ? 32 + 7 : 32,
  localparam bit                    ICacheTweakInfection         = SecureIbex,
  localparam int unsigned           RegFileDataWidth             = RegFileECC ? 32 + 7 : 32,
  localparam int unsigned           RegFileCapEccWidth           = RegFileECC ? REGCAP_W + 7 : REGCAP_W,
  localparam int unsigned           BusSizeECC                   = ICacheECC ? (BUS_SIZE + IC_DATA_ECC_SIZE) : BUS_SIZE,
  localparam int unsigned           LineSizeECC                  = BusSizeECC * IC_LINE_BEATS,
  localparam int unsigned           TagSizeECC                   = ICacheECC ? (IC_TAG_SIZE + IC_TAG_ECC_SIZE) : IC_TAG_SIZE
) (
  input  logic                         clk_i,
  input  logic                         rst_ni,

  input  logic [31:0]                  hart_id_i,
  input  logic [31:0]                  boot_addr_i,

  // Instruction memory interface
  output logic                         instr_req_o,
  input  logic                         instr_gnt_i,
  input  logic                         instr_rvalid_i,
  output logic [31:0]                  instr_addr_o,
`ifdef GEN_DUT_SPLIT_INTG
  input  logic [31:0]                  instr_rdata_i,
  input  logic [MemDataWidth-33:0]     instr_rdata_intg_i,
`else
  input  logic [MemDataWidth-1:0]      instr_rdata_i,
`endif
  input  logic                         instr_err_i,

  // Data memory interface
  output logic                         data_req_o,
  input  logic                         data_gnt_i,
  input  logic                         data_rvalid_i,
  output logic                         data_we_o,
  output logic [3:0]                   data_be_o,
  output logic [31:0]                  data_addr_o,
`ifdef GEN_DUT_SPLIT_INTG
  output logic [31:0]                  data_wdata_o,
  output logic [MemDataWidth-33:0]     data_wdata_intg_o,
  input  logic [31:0]                  data_rdata_i,
  input  logic [MemDataWidth-33:0]     data_rdata_intg_i,
`else
  output logic [MemDataWidth-1:0]      data_wdata_o,
  input  logic [MemDataWidth-1:0]      data_rdata_i,
`endif
  output logic                         data_tag_o,
  input  logic                         data_tag_i,
  input  logic                         data_err_i,

  // Instruction cache RAM interface (TB test equipment answers it)
  output logic [IC_NUM_WAYS-1:0]       ic_tag_req_o,
  output logic                         ic_tag_write_o,
  output logic [IC_INDEX_W-1:0]        ic_tag_addr_o,
  output logic [TagSizeECC-1:0]        ic_tag_wdata_o,
  input  logic [TagSizeECC-1:0]        ic_tag_rdata_i [IC_NUM_WAYS],
  output logic [IC_NUM_WAYS-1:0]       ic_data_req_o,
  output logic                         ic_data_write_o,
  output logic [IC_INDEX_W-1:0]        ic_data_addr_o,
  output logic [LineSizeECC-1:0]       ic_data_wdata_o,
  input  logic [LineSizeECC-1:0]       ic_data_rdata_i [IC_NUM_WAYS],
  input  logic                         ic_scr_key_valid_i,
  output logic                         ic_scr_key_req_o,

  // Interrupt inputs
  input  logic                         irq_software_i,
  input  logic                         irq_timer_i,
  input  logic                         irq_external_i,
  input  logic [14:0]                  irq_fast_i,
  input  logic                         irq_nm_i,
  output logic                         irq_pending_o,

  // Debug interface
  input  logic                         debug_req_i,
  output crash_dump_t                  crash_dump_o,
  output logic                         double_fault_seen_o,

`ifdef RVFI
  output logic                         rvfi_valid,
  output logic [63:0]                  rvfi_order,
  output logic [31:0]                  rvfi_insn,
  output logic                         rvfi_trap,
  output logic                         rvfi_halt,
  output logic                         rvfi_intr,
  output logic [ 1:0]                  rvfi_mode,
  output logic [ 1:0]                  rvfi_ixl,
  output logic [ 4:0]                  rvfi_rs1_addr,
  output logic [ 4:0]                  rvfi_rs2_addr,
  output logic [ 4:0]                  rvfi_rs3_addr,
  output logic [31:0]                  rvfi_rs1_rdata,
  output cap_t                         rvfi_rs1_rcap,
  output logic [31:0]                  rvfi_rs2_rdata,
  output cap_t                         rvfi_rs2_rcap,
  output logic [31:0]                  rvfi_rs3_rdata,
  output logic [ 4:0]                  rvfi_rd_addr,
  output logic [31:0]                  rvfi_rd_wdata,
  output cap_t                         rvfi_rd_wcap,
  output logic [31:0]                  rvfi_pc_rdata,
  output logic [31:0]                  rvfi_pc_wdata,
  output logic                         rvfi_mem_is_cap,
  output logic [31:0]                  rvfi_mem_addr,
  output logic [ 3:0]                  rvfi_mem_rmask,
  output logic [ 3:0]                  rvfi_mem_wmask,
  output logic [31:0]                  rvfi_mem_rdata,
  output cap_t                         rvfi_mem_rcap,
  output logic [31:0]                  rvfi_mem_wdata,
  output cap_t                         rvfi_mem_wcap,
  output logic [31:0]                  rvfi_ext_pre_mip,
  output logic [31:0]                  rvfi_ext_post_mip,
  output logic                         rvfi_ext_nmi,
  output logic                         rvfi_ext_nmi_int,
  output logic                         rvfi_ext_debug_req,
  output logic                         rvfi_ext_debug_mode,
  output logic                         rvfi_ext_rf_wr_suppress,
  output logic [63:0]                  rvfi_ext_mcycle,
  output logic [31:0]                  rvfi_ext_mhpmcounters [10],
  output logic [31:0]                  rvfi_ext_mhpmcountersh [10],
  output logic                         rvfi_ext_ic_scr_key_valid,
  output logic                         rvfi_ext_irq_valid,
  output logic                         rvfi_ext_expanded_insn_valid,
  output logic [15:0]                  rvfi_ext_expanded_insn,
  output logic                         rvfi_ext_expanded_insn_last,
`endif

  // CPU control signals
  input  ibex_mubi_t                   fetch_enable_i,
  input  ibex_mubi_t                   mcounteren_writable_i,
  output logic                         alert_minor_o,
  output logic                         alert_major_internal_o,
  output logic                         alert_major_bus_o,
  output ibex_mubi_t                   core_busy_o
);

  // Owner ruling: CHERIoT mode is never entered; the enable is not a DUT input.
  localparam ibex_mubi_t CheriotEnable = IbexMuBiOff;
  // Unused by ibex_register_file_ff (rtl/ibex_register_file_ff.sv:232-233).
  localparam logic       RfTestEn      = 1'b0;

  // Core <-> register file seam (rtl/ibex_top.sv:437-448, 540-559)
  logic                          dummy_instr_id;
  logic                          dummy_instr_wb;
  logic [4:0]                    rf_raddr_a;
  logic [4:0]                    rf_raddr_b;
  logic [4:0]                    rf_waddr_wb;
  logic                          rf_we_wb;
  logic [RegFileDataWidth-1:0]   rf_wdata_wb;
  logic [RegFileDataWidth-1:0]   rf_rdata_a;
  logic [RegFileDataWidth-1:0]   rf_rdata_b;
  logic [RegFileCapEccWidth-1:0] rf_wcap_wb;
  logic [RegFileCapEccWidth-1:0] rf_rcap_a;
  logic [RegFileCapEccWidth-1:0] rf_rcap_b;

  // Bus ports as ibex_core sees them (integrity above the data, rtl/ibex_top.sv:355-366)
  logic [MemDataWidth-1:0]       instr_rdata_core;
  logic [MemDataWidth-1:0]       data_rdata_core;
  logic [MemDataWidth-1:0]       data_wdata_core;

`ifdef GEN_DUT_SPLIT_INTG
  assign instr_rdata_core  = {instr_rdata_intg_i, instr_rdata_i};
  assign data_rdata_core   = {data_rdata_intg_i, data_rdata_i};
  assign data_wdata_o      = data_wdata_core[31:0];
  assign data_wdata_intg_o = data_wdata_core[MemDataWidth-1:32];
`else
  assign instr_rdata_core  = instr_rdata_i;
  assign data_rdata_core   = data_rdata_i;
  assign data_wdata_o      = data_wdata_core;
`endif

  ibex_core #(
    .PMPEnable            (PMPEnable),
    .PMPGranularity       (PMPGranularity),
    .PMPNumRegions        (PMPNumRegions),
    .MHPMCounterNum       (MHPMCounterNum),
    .MHPMCounterWidth     (MHPMCounterWidth),
    .RV32E                (RV32E),
    .RV32M                (RV32M),
    .RV32B                (RV32B),
    .RV32ZC               (RV32ZC),
    .BranchTargetALU      (BranchTargetALU),
    .ICache               (ICache),
    .ICacheECC            (ICacheECC),
    .ICacheTweakInfection (ICacheTweakInfection),
    .BusSizeECC           (BusSizeECC),
    .TagSizeECC           (TagSizeECC),
    .LineSizeECC          (LineSizeECC),
    .BranchPredictor      (BranchPredictor),
    .DbgTriggerEn         (DbgTriggerEn),
    .DbgHwBreakNum        (DbgHwBreakNum),
    .WritebackStage       (WritebackStage),
    .ResetAll             (ResetAll),
    .RndCnstLfsrSeed      (RndCnstLfsrSeed),
    .RndCnstLfsrPerm      (RndCnstLfsrPerm),
    .SecureIbex           (SecureIbex),
    .DummyInstructions    (DummyInstructions),
    .RegFileECC           (RegFileECC),
    .RegFileDataWidth     (RegFileDataWidth),
    .RegFileCapEccWidth   (RegFileCapEccWidth),
    .MemECC               (MemECC),
    .MemDataWidth         (MemDataWidth),
    .DmBaseAddr           (DmBaseAddr),
    .DmAddrMask           (DmAddrMask),
    .DmHaltAddr           (DmHaltAddr),
    .DmExceptionAddr      (DmExceptionAddr),
    .CsrMvendorId         (CsrMvendorId),
    .CsrMimpId            (CsrMimpId),
    .BaseIsa              (BaseIsa)
  ) u_ibex_core (
    .clk_i,
    .rst_ni,

    .hart_id_i,
    .boot_addr_i,
    .cheriot_enable_i (CheriotEnable),

    .instr_req_o,
    .instr_gnt_i,
    .instr_rvalid_i,
    .instr_addr_o,
    .instr_rdata_i    (instr_rdata_core),
    .instr_err_i,

    .data_req_o,
    .data_gnt_i,
    .data_rvalid_i,
    .data_we_o,
    .data_be_o,
    .data_addr_o,
    .data_wdata_o     (data_wdata_core),
    .data_tag_o,
    .data_rdata_i     (data_rdata_core),
    .data_tag_i,
    .data_err_i,

    .dummy_instr_id_o (dummy_instr_id),
    .dummy_instr_wb_o (dummy_instr_wb),
    .rf_raddr_a_o     (rf_raddr_a),
    .rf_raddr_b_o     (rf_raddr_b),
    .rf_waddr_wb_o    (rf_waddr_wb),
    .rf_we_wb_o       (rf_we_wb),
    .rf_wdata_wb_ecc_o(rf_wdata_wb),
    .rf_rdata_a_ecc_i (rf_rdata_a),
    .rf_rdata_b_ecc_i (rf_rdata_b),
    .rf_wcap_ecc_wb_o (rf_wcap_wb),
    .rf_rcap_a_ecc_i  (rf_rcap_a),
    .rf_rcap_b_ecc_i  (rf_rcap_b),

    .ic_tag_req_o,
    .ic_tag_write_o,
    .ic_tag_addr_o,
    .ic_tag_wdata_o,
    .ic_tag_rdata_i,
    .ic_data_req_o,
    .ic_data_write_o,
    .ic_data_addr_o,
    .ic_data_wdata_o,
    .ic_data_rdata_i,
    .ic_scr_key_valid_i,
    .ic_scr_key_req_o,

    .irq_software_i,
    .irq_timer_i,
    .irq_external_i,
    .irq_fast_i,
    .irq_nm_i,
    .irq_pending_o,

    .debug_req_i,
    .crash_dump_o,
    .double_fault_seen_o,

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

    .fetch_enable_i,
    .mcounteren_writable_i,
    .alert_minor_o,
    .alert_major_internal_o,
    .alert_major_bus_o,
    .core_busy_o
  );

  // Only the flip-flop register file is in scope (rtl/ibex_top.sv:532-559 wiring). With
  // RegFileECC = 1 the cap zero word would also need its 64/57 SECDED encoding; not derived
  // here because the default keeps RegFileECC = 0 (Q-A).
  ibex_register_file_ff #(
    .BaseIsa          (BaseIsa),
    .RV32E            (RV32E),
    .DataWidth        (RegFileDataWidth),
    .DummyInstructions(DummyInstructions),
    .WordZeroVal      (RegFileDataWidth'(prim_secded_pkg::SecdedInv3932ZeroWord)),
    .CapWidth         (RegFileCapEccWidth)
  ) u_register_file (
    .clk_i,
    .rst_ni,

    .test_en_i        (RfTestEn),
    .dummy_instr_id_i (dummy_instr_id),
    .dummy_instr_wb_i (dummy_instr_wb),
    .cheriot_enable_i (CheriotEnable),

    .raddr_a_i        (rf_raddr_a),
    .rdata_a_o        (rf_rdata_a),
    .rcap_a_o         (rf_rcap_a),
    .raddr_b_i        (rf_raddr_b),
    .rdata_b_o        (rf_rdata_b),
    .rcap_b_o         (rf_rcap_b),
    .waddr_a_i        (rf_waddr_wb),
    .wdata_a_i        (rf_wdata_wb),
    .wcap_a_i         (rf_wcap_wb),
    .we_a_i           (rf_we_wb)
  );

  // Time-0 configuration banner: every log proves which configuration elaborated
  // (docs/dv/dv_principles.md Section 1). One line per value, one tag per line.
  initial begin : g_config_banner
    string cfg_name;
    if (!$value$plusargs({gen_tb_pkg::PLUSARG_BUILD_CONFIG, "=%s"}, cfg_name)) cfg_name = "UNSPECIFIED";
    $display("%s build_config=%s", gen_tb_pkg::GEN_BANNER_TAG, cfg_name);
    $display("%s BaseIsa=%s RV32M=%s RV32B=%s RV32ZC=%s RegFile=%s", gen_tb_pkg::GEN_BANNER_TAG,
             BaseIsa.name(), RV32M.name(), RV32B.name(), RV32ZC.name(), RegFile.name());
    $display("%s RV32E=%0d BranchTargetALU=%0d WritebackStage=%0d ICache=%0d ICacheECC=%0d ICacheScramble=%0d",
             gen_tb_pkg::GEN_BANNER_TAG, RV32E, BranchTargetALU, WritebackStage, ICache, ICacheECC,
             ICacheScramble);
    $display("%s BranchPredictor=%0d DbgTriggerEn=%0d DbgHwBreakNum=%0d SecureIbex=%0d",
             gen_tb_pkg::GEN_BANNER_TAG, BranchPredictor, DbgTriggerEn, DbgHwBreakNum, SecureIbex);
    $display("%s PMPEnable=%0d PMPGranularity=%0d PMPNumRegions=%0d MHPMCounterNum=%0d MHPMCounterWidth=%0d",
             gen_tb_pkg::GEN_BANNER_TAG, PMPEnable, PMPGranularity, PMPNumRegions, MHPMCounterNum,
             MHPMCounterWidth);
    $display("%s RegFileECC=%0d ResetAll=%0d DummyInstructions=%0d MemECC=%0d ICacheTweakInfection=%0d",
             gen_tb_pkg::GEN_BANNER_TAG, RegFileECC, ResetAll, DummyInstructions, MemECC,
             ICacheTweakInfection);
    $display("%s MemDataWidth=%0d RegFileDataWidth=%0d RegFileCapEccWidth=%0d BusSizeECC=%0d TagSizeECC=%0d LineSizeECC=%0d",
             gen_tb_pkg::GEN_BANNER_TAG, MemDataWidth, RegFileDataWidth, RegFileCapEccWidth,
             BusSizeECC, TagSizeECC, LineSizeECC);
    $display("%s DmBaseAddr=0x%08x DmAddrMask=0x%08x DmHaltAddr=0x%08x DmExceptionAddr=0x%08x",
             gen_tb_pkg::GEN_BANNER_TAG, DmBaseAddr, DmAddrMask, DmHaltAddr, DmExceptionAddr);
    $display("%s CsrMvendorId=0x%08x CsrMimpId=0x%08x cheriot_enable=%s rf_test_en=%0d",
             gen_tb_pkg::GEN_BANNER_TAG, CsrMvendorId, CsrMimpId,
             gen_tb_pkg::gen_mubi_str(CheriotEnable), RfTestEn);
    $display("%s RndCnstLfsrSeed=0x%08x RndCnstLfsrPerm=0x%040x", gen_tb_pkg::GEN_BANNER_TAG,
             RndCnstLfsrSeed, RndCnstLfsrPerm);
    $display("%s PMPRstCfg/PMPRstAddr/PMPRstMsecCfg=ibex_pkg::PmpCfgRst/PmpAddrRst/PmpMseccfgRst (ibex_core defaults, all regions OFF)",
             gen_tb_pkg::GEN_BANNER_TAG);
`ifdef RVFI
    $display("%s RVFI=1", gen_tb_pkg::GEN_BANNER_TAG);
`else
    $display("%s RVFI=0", gen_tb_pkg::GEN_BANNER_TAG);
`endif
`ifdef GEN_DUT_SPLIT_INTG
    $display("%s GEN_DUT_SPLIT_INTG=1", gen_tb_pkg::GEN_BANNER_TAG);
`else
    $display("%s GEN_DUT_SPLIT_INTG=0", gen_tb_pkg::GEN_BANNER_TAG);
`endif
  end

  // Elaboration guard (generate-scope elaboration system task, IEEE 1800-2017 20.11): the ruling
  // names ibex_register_file_ff; other RegFile values are not built.
  if (RegFile != RegFileFF) begin : g_regfile_guard
    $fatal(1, "gen_dut_top: only RegFileFF is the DUT; RegFile parameter is not RegFileFF");
  end

endmodule
