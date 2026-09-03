// gen_tb_pkg: the single constants home of the generated TB (plusarg names, TB memory map,
// banner tag). Widths, encodings and enums come from ibex_pkg; nothing here re-types them.
package gen_tb_pkg;
  import ibex_pkg::*;

  // Plusarg names: declared once here, never as string literals at a call site.
  parameter string PLUSARG_BUILD_CONFIG = "gen_build_config";  // e.g. +gen_build_config=opentitan
  parameter string PLUSARG_SMOKE_CYCLES = "gen_smoke_cycles";  // bounded run length of the smoke

  // Every time-0 banner line starts with this tag so a log scanner can grep one token.
  parameter string GEN_BANNER_TAG = "GEN_CONFIG_BANNER";

  // TB memory map (test equipment). The first fetch is {boot_addr_i[31:8], 8'h80}
  // (rtl/ibex_if_stage.sv:243), so a program entry must sit at that offset of the boot page.
  parameter logic [31:0] GEN_BOOT_ADDR_DEFAULT = 32'h8000_0000;
  parameter logic [7:0]  GEN_BOOT_FETCH_OFFSET = 8'h80;

  // Bus integrity: the core wraps 32 data bits with 7 SECDED check bits when MemECC is set
  // (rtl/ibex_core.sv MemDataWidth = 32 + 7); the check bits sit above the data.
  parameter int unsigned GEN_DATA_W = 32;
  parameter int unsigned GEN_INTG_W = 7;

  // RV32I NOP = addi x0, x0, 0, composed from the ibex_pkg opcode so no encoding is re-typed.
  parameter logic [31:0] GEN_RV32_NOP = {12'd0, 5'd0, 3'b000, 5'd0, OPCODE_OP_IMM};

  // Cache RAM geometry the TB models must follow (ibex_pkg).
  parameter int unsigned GEN_IC_NUM_WAYS  = IC_NUM_WAYS;
  parameter int unsigned GEN_IC_NUM_LINES = IC_NUM_LINES;
  parameter int unsigned GEN_IC_INDEX_W   = IC_INDEX_W;

  function automatic string gen_mubi_str(ibex_mubi_t v);
    if (v == IbexMuBiOn)  return "On";
    if (v == IbexMuBiOff) return "Off";
    return $sformatf("INVALID(%0b)", v);
  endfunction

endpackage
