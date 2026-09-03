// gen_tb_pkg: the single constants home of the generated TB (plusarg names, TB memory map,
// banner tag). Widths, encodings and enums come from ibex_pkg; nothing here re-types them.
package gen_tb_pkg;
  import ibex_pkg::*;

  // Plusarg names: declared once here, never as string literals at a call site.
  parameter string PLUSARG_BUILD_CONFIG = "gen_build_config";  // e.g. +gen_build_config=opentitan
  parameter string PLUSARG_SMOKE_CYCLES = "gen_smoke_cycles";  // bounded run length of the smoke
  // Smoke red-run knob: flip this bit of the TB-side SECDED-encoded NOP word so the core sees an
  // integrity error (proves the smoke's alert check fires). Absent = no corruption.
  parameter string PLUSARG_SMOKE_INTG_FLIP = "gen_smoke_intg_flip";

  // Every time-0 banner line starts with this tag so a log scanner can grep one token.
  parameter string GEN_BANNER_TAG = "GEN_CONFIG_BANNER";

  // TB memory map (test equipment). The first fetch is {boot_addr_i[31:8], 8'h80}
  // (rtl/ibex_if_stage.sv:243); gen_link.ld places the program entry there (checked against this
  // value by dv/auto_dv/stim/gen_program.py).
  parameter logic [31:0] GEN_BOOT_ADDR_DEFAULT = 32'h8000_0000;

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
