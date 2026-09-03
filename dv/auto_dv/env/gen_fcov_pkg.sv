// gen_fcov_pkg: functional coverage sampled from TB-side facts: the RVFI record (gen_isa_cov, the plan's covergroups rendered
// in gen_fcov_groups.svh) and the witness command. CG-WIT-001 (gen_wit_cycle_clause_cg): one bin per marked
// test-plan item, sampled by the COV_WITNESS bridge command a test's epilogue issues for a fire-check whose cycle clause held
// (dv/auto_dv/docs/gen_fcov_plan.md, WIT). The dispatcher refuses an index outside the list and an item of another test's
// group (arg1); the peek word returns the distinct bins hit as the covergroup itself counts them.
package gen_fcov_pkg;
  import uvm_pkg::*;
  `include "uvm_macros.svh"
  import gen_tb_pkg::*;
  import gen_cfg_pkg::*;
  import gen_rvfi_pkg::*;
  import gen_isa_dpi_pkg::*;
  `include "gen_wit_bins.svh"
  `include "gen_fcov_groups.svh"

  // type-based: urg reports gen_wit_cycle_clause_cg.cp_clause.<bin>, the names the fcov manifests carry
  covergroup gen_wit_cycle_clause_cg with function sample(int unsigned idx);
    option.per_instance = 0;
    cp_clause: coverpoint idx { `GEN_WIT_BINS }
  endgroup

  // the n-th token of a comma-separated list ("" past the end)
  function automatic string gen_csv_nth(string csv, int unsigned n);
    int unsigned k = 0, start = 0;
    for (int i = 0; i <= csv.len(); i++) begin
      if (i == csv.len() || csv[i] == ",") begin
        if (k == n) return csv.substr(start, i - 1);
        k++; start = i + 1;
      end
    end
    return "";
  endfunction

  class gen_wit_cov extends uvm_component;
    `uvm_component_utils(gen_wit_cov)
    gen_env_cfg cfg;
    gen_wit_cycle_clause_cg cg;
    int unsigned witnessed = 0, foreign = 0, out_of_range = 0;
    bit hit [GEN_WITNESS_COUNT];
    function new(string name, uvm_component parent);
      super.new(name, parent);
      foreach (hit[i]) hit[i] = 1'b0;
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_WIT", "cfg not in uvm_config_db")
      if (cfg.fcov_en) cg = new();
    endfunction
    // distinct bins hit: the covergroup's own count when it exists (so a dropped sample shows), the bookkeeping otherwise
    function int unsigned distinct();
      int unsigned n = 0;
      if (cg != null) return int'(cg.cp_clause.get_coverage() * GEN_WITNESS_COUNT / 100.0);   // the int cast rounds to nearest
      foreach (hit[i]) if (hit[i]) n++;
      return n;
    endfunction
    function int unsigned witness(int unsigned idx, int unsigned owner);
      if (idx >= GEN_WITNESS_COUNT) begin
        out_of_range++;
        `uvm_error("GEN_CMD_DISPATCH", $sformatf("COV_WITNESS index %0d is outside the witness list (%0d rows)", idx, GEN_WITNESS_COUNT))
        return distinct();
      end
      if (GEN_WITNESS_GROUP_OF[idx] != owner) begin
        foreign++;
        `uvm_error("GEN_WITNESS_FOREIGN", $sformatf("COV_WITNESS %s (index %0d) belongs to %s, issued by %s", gen_csv_nth(GEN_WITNESS_TP_NAMES, idx), idx,
                   gen_csv_nth(GEN_WITNESS_GROUP_NAMES, GEN_WITNESS_GROUP_OF[idx]), owner < GEN_WITNESS_GROUP_COUNT ? gen_csv_nth(GEN_WITNESS_GROUP_NAMES, owner) : "an unknown group"))
        return distinct();
      end
      witnessed++; hit[idx] = 1'b1;
      if (cg != null) cg.sample(idx);
      return distinct();
    endfunction
    function void report_phase(uvm_phase phase);
      int unsigned n = 0;
      foreach (hit[i]) if (hit[i]) n++;
      `uvm_info("GEN_WIT", $sformatf("witnesses=%0d distinct=%0d covergroup=%0d foreign=%0d out_of_range=%0d", witnessed, n, cg != null ? distinct() : 0, foreign, out_of_range), UVM_LOW)
      if (cg != null && distinct() != n)
        `uvm_error("wit_referee", $sformatf("the covergroup counts %0d distinct bins, the dispatcher accepted %0d distinct witnesses", distinct(), n))
    endfunction
  endclass

  // The RVFI sampler of the plan's instruction covergroups (T-205). Every classifier is a partition of a record field the plan
  // names; the sample condition is the plan's (decoded encoding, rvfi_trap == 0). RVFI reports a compressed instruction in its
  // 16-bit form, so c.mul is decoded from it (rtl/ibex_core.sv:2263-2267); rd_wdata is forced to 0 on an rd = x0 record.
  class gen_isa_cov extends uvm_subscriber #(gen_rvfi_txn);
    `uvm_component_utils(gen_isa_cov)
    gen_env_cfg cfg;
    gen_mul_ops_cg     mul_cg;
    gen_div_ops_cg     div_cg;
    gen_isa_alu_reg_cg alu_cg;
    gen_bit_zba_zbb_ops_cg bit_cg;
    gen_isa_alu_imm_cg imm_cg;
    gen_isa_shift_cg   sh_cg;
    gen_bit_count_cg   cnt_cg;
    gen_cmp_zca_cg     zca_cg;
    gen_cmp_zcmp_pushpop_cg zcmp_cg;
    gen_cmp_zcmp_mv_cg mv_cg;
    gen_csr_trap_setup_warl_cg csr_cg;
    gen_isa_branch_cg  br_cg;
    // CG-CMP-007 move pair: form, register fields, the two source values, the neighbour facts; sampled once the next record is known
    int zp_mv = -1, mv_r1, mv_r2, mv_hz, mv_prev; logic [31:0] mv_src1, mv_src2; bit mv_ok, mv_pend = 0; int mv_v [8];
    // the registers written and the load fact of the instruction in progress and of the one before it (an expansion is one instruction)
    logic [31:0] cur_wr = '0, prev_wr = '0; bit cur_ld = 0, prev_ld = 0; int cur_mv = -1, prev_mv = -1;
    // CG-CSR-002 pairs per tracked CSR: the open write (op, operand, rd, effective value) and the standing value of the last read-back
    bit csr_pend [8], csr_eff_ok [8], csr_shadow_ok [8]; int csr_op [8], csr_rd [8]; logic [31:0] csr_wval [8], csr_eff [8], csr_shadow [8];
    int unsigned n_br = 0, n_mv = 0, n_csr_pairs = 0, n_csr_wr = 0, n_csr_replaced = 0;
    // CG-CMP-006 sequence collector: one cm.push / cm.pop / cm.popret / cm.popretz from its first micro-op record to its last
    bit zp_in = 0, zp_sp_valid, zp_order_ok, zp_tags_ok; int zp_kind, zp_rlist, zp_spimm, zp_n, zp_adj, zp_count, zp_mem_k, zp_ret_align;
    logic [31:0] zp_pc, zp_sp, zp_mhpm10_before, prev_mhpm10 = 0; logic [4:0] zp_prev_reg; int unsigned n_zcmp = 0, n_zcmp_abandoned = 0;
    int unsigned n_mul = 0, n_div = 0, n_alu = 0, n_bit = 0, n_imm = 0, n_sh = 0, n_cnt = 0, n_zca = 0, n_zca32 = 0;
    // the pending 16-bit record of CG-CMP-001: sampled when the next record tells the next instruction's length
    bit zca_pend = 0; int zca_v [7];
    function new(string name, uvm_component parent); super.new(name, parent); endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_FCOV", "cfg not in uvm_config_db")
      if (cfg.fcov_en) begin mul_cg = new(); div_cg = new(); alu_cg = new(); bit_cg = new(); imm_cg = new(); sh_cg = new(); cnt_cg = new(); zca_cg = new(); zcmp_cg = new(); mv_cg = new(); csr_cg = new(); br_cg = new(); end
    endfunction
    // ---- classifiers (plan bin order = the rendered GEN_FC_* indices)
    function int mul_rs_cls(logic [31:0] v);   // CG-MUL-001 cp_rs1_class / cp_rs2_class (same bin list)
      case (v)
        32'h0000_0000: return GEN_FC_MUL_OPS_CP_RS1_CLASS_ZERO;
        32'h0000_0001: return GEN_FC_MUL_OPS_CP_RS1_CLASS_ONE;
        32'hFFFF_FFFF: return GEN_FC_MUL_OPS_CP_RS1_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_MUL_OPS_CP_RS1_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_MUL_OPS_CP_RS1_CLASS_INT_MAX;
        32'h0001_0000: return GEN_FC_MUL_OPS_CP_RS1_CLASS_P16;
        32'h0000_0002: return GEN_FC_MUL_OPS_CP_RS1_CLASS_TWO;
        default:       return v[31] ? GEN_FC_MUL_OPS_CP_RS1_CLASS_NEG_RAND : GEN_FC_MUL_OPS_CP_RS1_CLASS_POS_RAND;
      endcase
    endfunction
    function int mul_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_ZERO;
        32'h0000_0001: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_ONE;
        32'hFFFF_FFFF: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_INT_MAX;
        32'hFFFF_FFFE: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_FFFFFFFE;
        32'h3FFF_FFFF: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_R3FFFFFFF;
        32'h4000_0000: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_R40000000;
        default:       return GEN_FC_MUL_OPS_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    // sign pair: bins pp, pn, np, nn in that order = {rs1[31], rs2[31]}
    function int sign_pair(logic [31:0] a, logic [31:0] b); return int'({a[31], b[31]}); endfunction
    function int mul_same(logic [4:0] rs1, logic [4:0] rs2, logic [4:0] rd);
      if (rs1 == rs2 && rs2 == rd && rd != 0) return GEN_FC_MUL_OPS_CP_SAME_REGS_ALL_SAME;
      if (rs1 == rs2 && rs1 != rd) return GEN_FC_MUL_OPS_CP_SAME_REGS_RS1_EQ_RS2;
      if ((rs1 == rd || rs2 == rd) && rs1 != rs2) return GEN_FC_MUL_OPS_CP_SAME_REGS_RS_EQ_RD;
      return GEN_FC_MUL_OPS_CP_SAME_REGS_DISTINCT;
    endfunction
    function int div_dividend_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_DIV_OPS_CP_DIVIDEND_ZERO;
        32'h0000_0001: return GEN_FC_DIV_OPS_CP_DIVIDEND_ONE;
        32'hFFFF_FFFF: return GEN_FC_DIV_OPS_CP_DIVIDEND_ALL_ONES;
        32'h8000_0000: return GEN_FC_DIV_OPS_CP_DIVIDEND_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_DIV_OPS_CP_DIVIDEND_INT_MAX;
        32'h0000_0002: return GEN_FC_DIV_OPS_CP_DIVIDEND_TWO;
        32'h0000_0007: return GEN_FC_DIV_OPS_CP_DIVIDEND_SEVEN;
        default:       return v[31] ? GEN_FC_DIV_OPS_CP_DIVIDEND_NEG_RAND : GEN_FC_DIV_OPS_CP_DIVIDEND_POS_RAND;
      endcase
    endfunction
    // the listed values first, then the relations to the dividend, then the sign classes (plan order)
    function int div_divisor_cls(logic [31:0] rs2, logic [31:0] rs1);
      logic [32:0] abs1 = rs1[31] ? (33'd0 - {1'b0, rs1}) : {1'b0, rs1};
      logic [32:0] abs2 = rs2[31] ? (33'd0 - {1'b0, rs2}) : {1'b0, rs2};
      case (rs2)
        32'h0000_0000: return GEN_FC_DIV_OPS_CP_DIVISOR_ZERO;
        32'h0000_0001: return GEN_FC_DIV_OPS_CP_DIVISOR_ONE;
        32'hFFFF_FFFF: return GEN_FC_DIV_OPS_CP_DIVISOR_ALL_ONES;
        32'h8000_0000: return GEN_FC_DIV_OPS_CP_DIVISOR_INT_MIN;
        32'h0000_0002: return GEN_FC_DIV_OPS_CP_DIVISOR_TWO;
        32'hFFFF_FFFE: return GEN_FC_DIV_OPS_CP_DIVISOR_MINUS_TWO;
        default: begin
          if (rs2 == rs1) return GEN_FC_DIV_OPS_CP_DIVISOR_EQ_DIVIDEND;
          if (abs2 > abs1) return GEN_FC_DIV_OPS_CP_DIVISOR_ABS_GT_DIVIDEND;
          return rs2[31] ? GEN_FC_DIV_OPS_CP_DIVISOR_NEG_RAND : GEN_FC_DIV_OPS_CP_DIVISOR_POS_RAND;
        end
      endcase
    endfunction
    function int div_res_cls(logic [31:0] v, logic [31:0] rs1);
      case (v)
        32'h0000_0000: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_ZERO;
        32'h0000_0001: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_ONE;
        32'hFFFF_FFFF: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_INT_MAX;
        default:       return (v == rs1) ? GEN_FC_DIV_OPS_CP_RESULT_CLASS_EQ_DIVIDEND : GEN_FC_DIV_OPS_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int alu_rs_cls(logic [31:0] v);   // CG-ISA-002 cp_rs1_class / cp_rs2_class
      case (v)
        32'h0000_0000: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ONE;
        default:       return v[31] ? GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_NEG_RAND : GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_POS_RAND;
      endcase
    endfunction
    function int alu_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ONE;
        default:       return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int alu_same(logic [4:0] rs1, logic [4:0] rs2, logic [4:0] rd);
      if (rs1 == rs2 && rs2 == rd && rd != 0) return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_ALL_SAME;
      if (rs1 == rs2 && rs1 != rd) return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS1_EQ_RS2;
      if (rs1 == rd && rs1 != rs2) return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS1_EQ_RD;
      if (rs2 == rd && rs1 != rs2) return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS2_EQ_RD;
      return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_DISTINCT;
    endfunction
    // add / sub only; the overflow cases take precedence over the carry / borrow they imply (one bin per sample)
    function int alu_wrap(int op, logic [31:0] a, logic [31:0] b);
      logic [32:0] sum = {1'b0, a} + {1'b0, b};
      if (op == GEN_FC_ISA_ALU_REG_CP_OP_ADD) begin
        if (!a[31] && !b[31] && sum[31]) return GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_POS_OVF;
        if (a[31] && b[31] && !sum[31]) return GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_NEG_OVF;
        if (sum[32]) return GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_CARRY;
        return GEN_FC_ISA_ALU_REG_CP_WRAP_NONE;
      end
      if (op == GEN_FC_ISA_ALU_REG_CP_OP_SUB) begin
        if (a == 32'h8000_0000 && !b[31] && b != 0) return GEN_FC_ISA_ALU_REG_CP_WRAP_SUB_OVF;
        if (a < b) return GEN_FC_ISA_ALU_REG_CP_WRAP_SUB_BORROW;
        return GEN_FC_ISA_ALU_REG_CP_WRAP_NONE;
      end
      return -1;
    endfunction

    // ---- CG-BIT-001 (Zba / Zbb / pack): the listed values, then the byte / half-word sign classes, then the sign
    function int bit_rs1_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ONE;
        32'hE000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_E0000000;
        default: begin
          if (v[7] && !v[15]) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_BYTE_MSB;
          if (v[15] && !v[7]) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_HALF_MSB;
          return v[31] ? GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_NEG_RAND : GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_POS_RAND;
        end
      endcase
    endfunction
    function int bit_rs2_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ONE;
        default:       return v[31] ? GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_NEG_RAND : GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_POS_RAND;
      endcase
    endfunction
    function int bit_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_INT_MAX;
        default:       return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int bit_same(logic [4:0] rs1, logic [4:0] rs2, logic [4:0] rd);
      if (rs1 == rs2 && rs2 == rd && rd != 0) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_ALL_SAME;
      if (rs1 == rs2 && rs1 != rd) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_RS1_EQ_RS2;
      return GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_DISTINCT;
    endfunction
    // the Zba / Zbb / pack op of an OP or OP-IMM encoding, -1 when none (decoder arms rtl/ibex_decoder.sv:609-624, :1106-1107)
    function int bit_op(logic [31:0] insn);
      logic [6:0] f7 = insn[31:25]; logic [2:0] f3 = insn[14:12]; logic [4:0] r2 = insn[24:20];
      if (insn[6:0] == ibex_pkg::OPCODE_OP_IMM && f3 == 3'b001 && f7 == 7'b0110000) begin
        if (r2 == 5'b00100) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SEXT_B;
        if (r2 == 5'b00101) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SEXT_H;
        return -1;
      end
      if (insn[6:0] != ibex_pkg::OPCODE_OP) return -1;
      case ({f7, f3})
        {7'b0010000, 3'b010}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH1ADD;
        {7'b0010000, 3'b100}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH2ADD;
        {7'b0010000, 3'b110}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH3ADD;
        {7'b0100000, 3'b111}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ANDN;
        {7'b0100000, 3'b110}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ORN;
        {7'b0100000, 3'b100}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_XNOR;
        {7'b0000101, 3'b100}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MIN;
        {7'b0000101, 3'b110}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MAX;
        {7'b0000101, 3'b101}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MINU;
        {7'b0000101, 3'b111}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MAXU;
        {7'b0000100, 3'b100}: return (r2 == 5'd0) ? GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ZEXT_H : GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACK;
        {7'b0100100, 3'b100}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACKU;
        {7'b0000100, 3'b111}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACKH;
        default: return -1;
      endcase
    endfunction
    // carry out of rs2 + ((rs1 << n) mod 2^32) for shNadd (the truncated shifted operand feeds the adder, rtl/ibex_alu.sv:87-89)
    function int bit_wrap(int op, logic [31:0] rs1, logic [31:0] rs2);
      int n = (op == GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH1ADD) ? 1 : (op == GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH2ADD) ? 2 : (op == GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH3ADD) ? 3 : 0;
      logic [32:0] sum;
      if (n == 0) return -1;
      sum = {1'b0, rs2} + {1'b0, rs1 << n};
      return sum[32] ? GEN_FC_BIT_ZBA_ZBB_OPS_CP_WRAP_YES : GEN_FC_BIT_ZBA_ZBB_OPS_CP_WRAP_NO;
    endfunction
    // ---- CG-ISA-001 (OP-IMM ALU)
    function int imm_rs1_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ONE;
        default:       return v[31] ? GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_NEG_RAND : GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_POS_RAND;
      endcase
    endfunction
    function int imm_cls(int imm);
      case (imm)
        0:     return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_ZERO;
        1:     return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_PLUS1;
        -1:    return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MINUS1;
        2047:  return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MAX_POS;
        -2048: return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MIN_NEG;
        default: return imm > 0 ? GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_POS_RAND : GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_NEG_RAND;
      endcase
    endfunction
    function int imm_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ONE;
        default:       return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int addi_wrap(int op, logic [31:0] rs1, int imm, logic [31:0] res);
      if (op != GEN_FC_ISA_ALU_IMM_CP_OP_ADDI) return -1;
      if (!rs1[31] && imm > 0 && res[31]) return GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_POS_WRAP;
      if (rs1[31] && imm < 0 && !res[31]) return GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_NEG_WRAP;
      return GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_NONE;
    endfunction
    // the named boundary cases first (they imply eq in two places), then eq, then other
    function int slt_case(int op, logic [31:0] rs1, int imm);
      bit slti = (op == GEN_FC_ISA_ALU_IMM_CP_OP_SLTI), sltiu = (op == GEN_FC_ISA_ALU_IMM_CP_OP_SLTIU);
      if (!slti && !sltiu) return -1;
      if (slti && rs1 == 32'h8000_0000 && imm == 0) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTI_INTMIN_0;
      if (slti && rs1 == 32'h0 && imm < 0) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTI_0_NEG;
      if (sltiu && rs1 == 32'hFFFF_FFFF && imm == -1) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_ONES_M1;
      if (sltiu && imm == -1) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_IMM_M1;
      if (sltiu && imm == 1) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_SEQZ;
      if (rs1 == 32'(imm)) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_EQ;   // sext(imm) as a 32-bit word
      return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_OTHER;
    endfunction
    // ---- CG-ISA-003 (base shifts)
    function int sh_operand_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_SHIFT_CP_OPERAND_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_SHIFT_CP_OPERAND_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_SHIFT_CP_OPERAND_MSB_ONLY;
        32'h0000_0001: return GEN_FC_ISA_SHIFT_CP_OPERAND_LSB_ONLY;
        default:       return v[31] ? GEN_FC_ISA_SHIFT_CP_OPERAND_NEG_RAND : GEN_FC_ISA_SHIFT_CP_OPERAND_POS_RAND;
      endcase
    endfunction
    function int sh_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_MSB_ONLY;
        32'h0000_0001: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ONE;
        32'hC000_0000: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_C0000000;
        default:       return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int sh_amt_cls(logic [4:0] a);
      if (a == 0) return GEN_FC_ISA_SHIFT_CP_SHAMT_S0;
      if (a == 1) return GEN_FC_ISA_SHIFT_CP_SHAMT_S1;
      if (a == 31) return GEN_FC_ISA_SHIFT_CP_SHAMT_S31;
      return GEN_FC_ISA_SHIFT_CP_SHAMT_MID;
    endfunction
    // register forms only: the exact values first, then the upper-bits-clear class, else other_nonzero
    function int sh_rs2_upper(logic [31:0] v);
      case (v)
        32'd32:        return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_IS32;
        32'd33:        return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_IS33;
        32'hFFFF_FFFF: return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_MSB_ONLY;
        32'hFFFF_FFE0: return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_FFFFFFE0;
        default:       return (v[31:5] == 0) ? GEN_FC_ISA_SHIFT_CP_RS2_UPPER_ZERO : GEN_FC_ISA_SHIFT_CP_RS2_UPPER_OTHER_NONZERO;
      endcase
    endfunction

    // ---- CG-BIT-002 (clz / ctz / cpop)
    function int cnt_operand_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_BIT_COUNT_CP_OPERAND_ZERO;
        32'hFFFF_FFFF: return GEN_FC_BIT_COUNT_CP_OPERAND_ALL_ONES;
        32'h8000_0000: return GEN_FC_BIT_COUNT_CP_OPERAND_MSB_ONLY;
        32'h0000_0001: return GEN_FC_BIT_COUNT_CP_OPERAND_LSB_ONLY;
        32'h5555_5555: return GEN_FC_BIT_COUNT_CP_OPERAND_ALT_5;
        32'hAAAA_AAAA: return GEN_FC_BIT_COUNT_CP_OPERAND_ALT_A;
        32'h7FFF_FFFF: return GEN_FC_BIT_COUNT_CP_OPERAND_INT_MAX;
        default:       return ($countones(v) == 1) ? GEN_FC_BIT_COUNT_CP_OPERAND_SINGLE_OTHER : GEN_FC_BIT_COUNT_CP_OPERAND_RAND;
      endcase
    endfunction
    function int cnt_single_pos(logic [31:0] v);   // p0..p31 are consecutive indices from GEN_FC_BIT_COUNT_CP_SINGLE_POS_P0
      if ($countones(v) != 1) return -1;
      for (int i = 0; i < 32; i++) if (v[i]) return GEN_FC_BIT_COUNT_CP_SINGLE_POS_P0 + i;
      return -1;
    endfunction
    function int cnt_result_cls(logic [31:0] v);
      case (v)
        32'd0:  return GEN_FC_BIT_COUNT_CP_RESULT_R0;
        32'd1:  return GEN_FC_BIT_COUNT_CP_RESULT_R1;
        32'd16: return GEN_FC_BIT_COUNT_CP_RESULT_R16;
        32'd31: return GEN_FC_BIT_COUNT_CP_RESULT_R31;
        32'd32: return GEN_FC_BIT_COUNT_CP_RESULT_R32;
        default: return GEN_FC_BIT_COUNT_CP_RESULT_OTHER;
      endcase
    endfunction
    // ---- CG-CMP-001 (Zca): the 16-bit form as RVFI reports it (rvfi_insn[1:0] != 11); -1 for an encoding outside the plan's list
    function int zca_insn(logic [15:0] i);
      logic [2:0] f3 = i[15:13]; logic [4:0] rd = i[11:7], rs2 = i[6:2];
      case (i[1:0])
        2'b00: case (f3)
          3'b000: return (i != 16'h0) ? GEN_FC_CMP_ZCA_CP_INSN_C_ADDI4SPN : -1;
          3'b010: return GEN_FC_CMP_ZCA_CP_INSN_C_LW;
          3'b110: return GEN_FC_CMP_ZCA_CP_INSN_C_SW;
          default: return -1;
        endcase
        2'b01: case (f3)
          3'b000: return (rd == 0) ? GEN_FC_CMP_ZCA_CP_INSN_C_NOP : GEN_FC_CMP_ZCA_CP_INSN_C_ADDI;
          3'b001: return GEN_FC_CMP_ZCA_CP_INSN_C_JAL;
          3'b010: return GEN_FC_CMP_ZCA_CP_INSN_C_LI;
          3'b011: return (rd == 5'd2) ? GEN_FC_CMP_ZCA_CP_INSN_C_ADDI16SP : GEN_FC_CMP_ZCA_CP_INSN_C_LUI;
          3'b100: case (i[11:10])
            2'b00: return GEN_FC_CMP_ZCA_CP_INSN_C_SRLI;
            2'b01: return GEN_FC_CMP_ZCA_CP_INSN_C_SRAI;
            2'b10: return GEN_FC_CMP_ZCA_CP_INSN_C_ANDI;
            default: begin
              if (i[12]) return -1;   // c.subw / c.addw (RV64) and the Zcb arithmetic forms
              case (i[6:5])
                2'b00: return GEN_FC_CMP_ZCA_CP_INSN_C_SUB; 2'b01: return GEN_FC_CMP_ZCA_CP_INSN_C_XOR;
                2'b10: return GEN_FC_CMP_ZCA_CP_INSN_C_OR;  default: return GEN_FC_CMP_ZCA_CP_INSN_C_AND;
              endcase
            end
          endcase
          3'b101: return GEN_FC_CMP_ZCA_CP_INSN_C_J;
          3'b110: return GEN_FC_CMP_ZCA_CP_INSN_C_BEQZ;
          default: return GEN_FC_CMP_ZCA_CP_INSN_C_BNEZ;
        endcase
        2'b10: case (f3)
          3'b000: return GEN_FC_CMP_ZCA_CP_INSN_C_SLLI;
          3'b010: return GEN_FC_CMP_ZCA_CP_INSN_C_LWSP;
          3'b100: begin
            if (!i[12]) return (rs2 == 0) ? ((rd != 0) ? GEN_FC_CMP_ZCA_CP_INSN_C_JR : -1) : GEN_FC_CMP_ZCA_CP_INSN_C_MV;
            if (rs2 == 0) return (rd != 0) ? GEN_FC_CMP_ZCA_CP_INSN_C_JALR : -1;   // rd = 0 is c.ebreak, a trap record
            return GEN_FC_CMP_ZCA_CP_INSN_C_ADD;
          end
          3'b110: return GEN_FC_CMP_ZCA_CP_INSN_C_SWSP;
          default: return -1;
        endcase
        default: return -1;
      endcase
    endfunction
    function bit zca_is_cti(int op);
      return op inside {GEN_FC_CMP_ZCA_CP_INSN_C_JAL, GEN_FC_CMP_ZCA_CP_INSN_C_J, GEN_FC_CMP_ZCA_CP_INSN_C_JR, GEN_FC_CMP_ZCA_CP_INSN_C_JALR, GEN_FC_CMP_ZCA_CP_INSN_C_BEQZ, GEN_FC_CMP_ZCA_CP_INSN_C_BNEZ};
    endfunction
    // the 3-bit register field of the CIW / CL / CS / CA / CB formats (rd' of c.addi4spn, rs1' otherwise); -1 for the other formats
    function int zca_reg3(int op, logic [15:0] i);
      if (op == GEN_FC_CMP_ZCA_CP_INSN_C_ADDI4SPN) return GEN_FC_CMP_ZCA_CP_REG3_R8 + int'(i[4:2]);
      if (op inside {GEN_FC_CMP_ZCA_CP_INSN_C_LW, GEN_FC_CMP_ZCA_CP_INSN_C_SW, GEN_FC_CMP_ZCA_CP_INSN_C_SRLI, GEN_FC_CMP_ZCA_CP_INSN_C_SRAI, GEN_FC_CMP_ZCA_CP_INSN_C_ANDI,
                     GEN_FC_CMP_ZCA_CP_INSN_C_SUB, GEN_FC_CMP_ZCA_CP_INSN_C_XOR, GEN_FC_CMP_ZCA_CP_INSN_C_OR, GEN_FC_CMP_ZCA_CP_INSN_C_AND, GEN_FC_CMP_ZCA_CP_INSN_C_BEQZ, GEN_FC_CMP_ZCA_CP_INSN_C_BNEZ})
        return GEN_FC_CMP_ZCA_CP_REG3_R8 + int'(i[9:7]);
      return -1;
    endfunction
    // the 5-bit register field of the CI / CR formats (rd, insn[11:7]) and of c.swsp (rs2, insn[6:2]); x0 has no bin
    function int zca_rd_full(int op, logic [15:0] i);
      logic [4:0] r;
      if (op inside {GEN_FC_CMP_ZCA_CP_INSN_C_ADDI, GEN_FC_CMP_ZCA_CP_INSN_C_LI, GEN_FC_CMP_ZCA_CP_INSN_C_LUI, GEN_FC_CMP_ZCA_CP_INSN_C_ADDI16SP, GEN_FC_CMP_ZCA_CP_INSN_C_SLLI,
                     GEN_FC_CMP_ZCA_CP_INSN_C_LWSP, GEN_FC_CMP_ZCA_CP_INSN_C_MV, GEN_FC_CMP_ZCA_CP_INSN_C_ADD, GEN_FC_CMP_ZCA_CP_INSN_C_JR, GEN_FC_CMP_ZCA_CP_INSN_C_JALR}) r = i[11:7];
      else if (op == GEN_FC_CMP_ZCA_CP_INSN_C_SWSP) r = i[6:2];
      else return -1;
      if (r == 1) return GEN_FC_CMP_ZCA_CP_RD_FULL_X1;
      if (r == 2) return GEN_FC_CMP_ZCA_CP_RD_FULL_X2;
      if (r >= 8 && r <= 15) return GEN_FC_CMP_ZCA_CP_RD_FULL_X8_15;
      if (r >= 16) return GEN_FC_CMP_ZCA_CP_RD_FULL_X16_31;
      if (r >= 3) return GEN_FC_CMP_ZCA_CP_RD_FULL_X3_7;
      return -1;
    endfunction
    // the pending 16-bit record samples once the following record's length is known (a Zcmp micro-op record is a 16-bit instruction)
    function void zca_flush(gen_rvfi_txn nxt);
      if (!zca_pend) return;
      zca_v[2] = (nxt == null) ? -1 : ((nxt.insn[1:0] != 2'b11 || nxt.ext_exp_valid) ? GEN_FC_CMP_ZCA_CP_NEXT_LEN_N16 : GEN_FC_CMP_ZCA_CP_NEXT_LEN_N32);
      zca_cg.sample(zca_v[0], zca_v[1], zca_v[2], zca_v[3], zca_v[4], zca_v[5], zca_v[6]);
      zca_pend = 0;
    endfunction

    // ---- CG-CMP-006: the 16-bit source word of a Zcmp stack instruction (rvfi_ext_expanded_insn): kind, rlist, spimm, N, stack_adj
    function void zp_start(gen_rvfi_txn t);
      logic [15:0] w = t.ext_exp_insn;
      zp_in = 1; zp_pc = t.pc_rdata; zp_count = 0; zp_mem_k = 0; zp_sp_valid = 0; zp_order_ok = 1; zp_tags_ok = 1; zp_ret_align = -1; zp_prev_reg = 5'd31;
      zp_mhpm10_before = prev_mhpm10;
      zp_kind = -1;
      if (w[15:13] == 3'b101 && w[1:0] == 2'b10) case (w[12:8])
        5'b11000: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH;
        5'b11010: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP;
        5'b11100: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRETZ;
        5'b11110: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRET;
        default:  zp_kind = -1;
      endcase
      zp_rlist = int'(w[7:4]); zp_spimm = int'(w[3:2]);
      zp_mv = mv_form(w);
      if (zp_mv >= 0) begin   // the sources: a0 / a1 for cm.mvsa01, r1s' / r2s' for cm.mva01s; the neighbour facts come from the instruction before
        logic [31:0] srcs;
        mv_r1 = int'(w[9:7]); mv_r2 = int'(w[4:2]); mv_ok = 1;
        srcs = (zp_mv == GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01) ? (32'h1 << 10) | (32'h1 << 11) : (32'h1 << (8 + mv_r1)) | (32'h1 << (8 + mv_r2));
        mv_hz = ((prev_wr & srcs) == 0) ? GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_NONE : prev_ld ? GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_LOAD_PREV : GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_ALU_PREV;
        mv_prev = prev_mv;
      end
      zp_n = (zp_rlist == 15) ? 13 : zp_rlist - 3;                                       // rlist 15 saves x27..x18, x9, x8, x1
      zp_adj = ((zp_rlist <= 7) ? 16 : (zp_rlist <= 11) ? 32 : (zp_rlist <= 14) ? 48 : 64) + zp_spimm * 16;   // zcmp.adoc stack_adj (RV32)
    endfunction
    function int zp_delay_cls();
      case (cfg.knob_dmem_rvalid_delay)
        "min1":  return GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_MIN1;
        "short": return GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_SHORT;
        "long":  return GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_LONG;
        default: return GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_MIXED;
      endcase
    endfunction
    // one micro-op record of an open sequence; samples the group on the last micro-op of a sequence that never trapped
    function void zp_step(gen_rvfi_txn t);
      bit is_st; int unsigned bytes; logic [4:0] r; logic [31:0] want;
      zp_count++;
      if (!t.ext_exp_last && t.pc_wdata != t.pc_rdata) zp_tags_ok = 0;   // intermediate micro-ops report their own pc (R9)
      if (t.insn[1:0] != 2'b11) zp_tags_ok = 0;                            // every micro-op word is the synthesized 32-bit one
      if (zp_mv >= 0) begin   // a move micro-op: `addi dst, src, 0` with the register pair of its position
        logic [4:0] want_rd, want_rs1; logic [4:0] sreg = 5'(8 + (zp_count == 1 ? mv_r1 : mv_r2)); logic [4:0] areg = (zp_count == 1) ? 5'd10 : 5'd11;
        if (zp_mv == GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01) begin want_rd = sreg; want_rs1 = areg; end else begin want_rd = areg; want_rs1 = sreg; end
        if (t.insn[6:0] != ibex_pkg::OPCODE_OP_IMM || t.insn[14:12] != 3'b000 || t.insn[31:20] != 12'h0 || t.insn[11:7] != want_rd || t.insn[19:15] != want_rs1 || zp_count > 2) mv_ok = 0;
        if (zp_count == 1) mv_src1 = t.rs1_rdata; else mv_src2 = t.rs1_rdata;
        if (t.ext_exp_last) begin
          mv_v[0] = zp_mv; mv_v[1] = mv_r1; mv_v[2] = mv_r2;
          mv_v[3] = (mv_r1 == mv_r2) ? GEN_FC_CMP_ZCMP_MV_CP_EQUAL_YES : GEN_FC_CMP_ZCMP_MV_CP_EQUAL_NO;
          mv_v[4] = (mv_src1 == mv_src2) ? GEN_FC_CMP_ZCMP_MV_CP_SRC_VALUES_SAME : GEN_FC_CMP_ZCMP_MV_CP_SRC_VALUES_DISTINCT;
          mv_v[5] = (mv_prev >= 0 && mv_prev != zp_mv) ? mv_b2b(mv_prev, zp_mv) : GEN_FC_CMP_ZCMP_MV_CP_B2B_NONE;   // the neighbour after is checked at the flush
          mv_v[6] = mv_hz;
          mv_v[7] = (zp_count == 2 && mv_ok && zp_tags_ok) ? GEN_FC_CMP_ZCMP_MV_CP_UOP_COUNT_OK_YES : -1;
          mv_pend = 1; cur_mv = zp_mv; n_mv++;
        end
      end
      if (gen_insn_mem_access(t.insn, is_st, bytes) && t.insn[19:15] == 5'd2) begin   // sp-based store (push) / load (pop*)
        if (!zp_sp_valid) begin zp_sp = t.rs1_rdata; zp_sp_valid = 1; end
        r = is_st ? t.insn[24:20] : t.insn[11:7];
        zp_mem_k++;
        want = is_st ? zp_sp - 32'(4 * zp_mem_k) : zp_sp + 32'(zp_adj) - 32'(4 * zp_mem_k);
        if (t.mem_addr != want || (zp_mem_k > 1 && r >= zp_prev_reg)) zp_order_ok = 0;   // descending registers, addresses as predicted
        zp_prev_reg = r;
      end
      if (t.insn[6:0] == 7'b1100111)   // the jalr x0, 0(ra) of popret / popretz: the loaded ra
        zp_ret_align = t.rs1_rdata[0] ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_ODD : t.rs1_rdata[1] ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_HALF : GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_WORD;
      if (t.ext_exp_last) begin
        if (zp_kind >= 0 && zp_sp_valid) begin
          int want_n = zp_n + ((zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH || zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP) ? 1 : (zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRET) ? 2 : 3);
          bit is_push = (zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH);
          int wrap = is_push ? ((zp_sp < 32'(4 * zp_n)) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_PUSH_BELOW_ZERO : GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_NONE)
                             : (({1'b0, zp_sp} + 33'(zp_adj) >= 33'h1_0000_0000) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_POP_ABOVE_MAX : GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_NONE);
          n_zcmp++;
          zcmp_cg.sample(zp_kind, GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R4 + (zp_rlist - 4), GEN_FC_CMP_ZCMP_PUSHPOP_CP_SPIMM_S0 + zp_spimm,
                         GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A16 + (zp_adj / 16 - 1), GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_ALIGN_ALIGNED + int'(zp_sp[1:0]), wrap,
                         (zp_count == want_n) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_UOP_COUNT_OK_YES : -1, (zp_order_ok && zp_mem_k == zp_n) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_ORDER_OK_YES : -1,
                         zp_tags_ok ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_RVFI_TAGS_OK_YES : -1, (t.ext_mhpmcounters[7] - zp_mhpm10_before == 32'd1) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_MINSTRET_ONCE_YES : -1,
                         is_push || zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP ? -1 : zp_ret_align, zp_delay_cls(),
                         gen_isa_read_csr(GEN_CSR_CPUCTRLSTS)[2] ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_DUMMY_EN_ON : GEN_FC_CMP_ZCMP_PUSHPOP_CP_DUMMY_EN_OFF);
        end
        zp_in = 0;
      end
    endfunction
    // ---- CG-CMP-007 helpers: the move form of a Zcmp source word (-1 for the stack forms), the b2b bin of an ordered pair
    function int mv_form(logic [15:0] w);
      if (w[15:13] != 3'b101 || w[12:10] != 3'b011 || w[1:0] != 2'b10) return -1;
      return (w[6:5] == 2'b01) ? GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01 : (w[6:5] == 2'b11) ? GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVA01S : -1;
    endfunction
    function int mv_b2b(int first, int second);
      return (first == GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01) ? GEN_FC_CMP_ZCMP_MV_CP_B2B_MVSA01_THEN_MVA01S : GEN_FC_CMP_ZCMP_MV_CP_B2B_MVA01S_THEN_MVSA01;
    endfunction
    // the pending move pair samples once the following record is known: the other move form opening there is the b2b neighbour after
    function void mv_flush(gen_rvfi_txn nxt);
      if (!mv_pend) return;
      if (nxt != null && mv_v[5] == GEN_FC_CMP_ZCMP_MV_CP_B2B_NONE && nxt.ext_exp_valid && !zp_in) begin
        int k = mv_form(nxt.ext_exp_insn);
        if (k >= 0 && k != mv_v[0]) mv_v[5] = mv_b2b(mv_v[0], k);
      end
      mv_cg.sample(mv_v[0], mv_v[1], mv_v[2], mv_v[3], mv_v[4], mv_v[5], mv_v[6], mv_v[7]);
      mv_pend = 0;
    endfunction

    // ---- CG-ISA-007: the compare classes in plan precedence (the named operand pairs before equal and the sign-order classes)
    function int br_cmp_cls(logic [31:0] a, logic [31:0] b);
      if (a == 32'h8000_0000 && b == 32'h8000_0000) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_BOTH_MSB_EQ;
      if (a == 32'h8000_0000 && b == 32'h0) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_INTMIN_ZERO;
      if (a == 32'h0 && b == 32'h8000_0000) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ZERO_INTMIN;
      if (a == 32'h0 && b == 32'hffff_ffff) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ZERO_ONES;
      if (a == 32'hffff_ffff && b == 32'h0) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ONES_ZERO;
      if (a == b) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_EQUAL;
      if ($signed(a) < $signed(b) && a > b) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_SLT_UGT;
      if ($signed(a) > $signed(b) && a < b) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_SGT_ULT;
      return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_RAND;
    endfunction
    function int br_off_cls(int imm, bit c16);
      if (imm == 0) return GEN_FC_ISA_BRANCH_CP_OFFSET_SELF;
      if (imm == (c16 ? 254 : 4094)) return GEN_FC_ISA_BRANCH_CP_OFFSET_MAX_FWD;
      if (imm == (c16 ? -256 : -4096)) return GEN_FC_ISA_BRANCH_CP_OFFSET_MAX_BWD;
      return (imm > 0) ? GEN_FC_ISA_BRANCH_CP_OFFSET_POS_RAND : GEN_FC_ISA_BRANCH_CP_OFFSET_NEG_RAND;
    endfunction
    // a BRANCH record (funct3 000 / 001 / 1xx) or c.beqz / c.bnez in its 16-bit form; taken = the next pc is not the sequential one
    function bit br_sample(gen_rvfi_txn t);
      int op, imm; bit c16, taken; logic [31:0] rs2, target; logic [32:0] sum;
      if (t.insn[1:0] == 2'b11) begin
        if (t.insn[6:0] != 7'b1100011 || t.insn[14:13] == 2'b01) return 0;
        case (t.insn[14:12])
          3'b000: op = GEN_FC_ISA_BRANCH_CP_OP_BEQ; 3'b001: op = GEN_FC_ISA_BRANCH_CP_OP_BNE;  3'b100: op = GEN_FC_ISA_BRANCH_CP_OP_BLT;
          3'b101: op = GEN_FC_ISA_BRANCH_CP_OP_BGE; 3'b110: op = GEN_FC_ISA_BRANCH_CP_OP_BLTU; default: op = GEN_FC_ISA_BRANCH_CP_OP_BGEU;
        endcase
        imm = signed'({t.insn[31], t.insn[7], t.insn[30:25], t.insn[11:8], 1'b0});   // imm_b, 13 bits
        c16 = 0; rs2 = t.rs2_rdata;
      end else begin
        if (t.insn[1:0] != 2'b01 || t.insn[15:14] != 2'b11) return 0;   // c.beqz 110, c.bnez 111
        op = t.insn[13] ? GEN_FC_ISA_BRANCH_CP_OP_C_BNEZ : GEN_FC_ISA_BRANCH_CP_OP_C_BEQZ;
        imm = signed'({t.insn[12], t.insn[6:5], t.insn[2], t.insn[11:10], t.insn[4:3], 1'b0});   // CB offset, 9 bits
        c16 = 1; rs2 = 32'h0;   // the compare is against x0
      end
      taken = (t.pc_wdata != t.pc_rdata + (c16 ? 32'd2 : 32'd4));
      target = t.pc_rdata + 32'(imm);
      sum = {1'b0, t.pc_rdata} + {1'b0, 32'(imm)};   // the carry the target adder discards
      n_br++;
      br_cg.sample(op, taken ? GEN_FC_ISA_BRANCH_CP_TAKEN_YES : GEN_FC_ISA_BRANCH_CP_TAKEN_NO, br_cmp_cls(t.rs1_rdata, rs2), br_off_cls(imm, c16),
                   target[1] ? GEN_FC_ISA_BRANCH_CP_TARGET_ALIGN_HALF : GEN_FC_ISA_BRANCH_CP_TARGET_ALIGN_WORD,
                   taken ? (sum[32] ? GEN_FC_ISA_BRANCH_CP_WRAP_YES : GEN_FC_ISA_BRANCH_CP_WRAP_NO) : -1);
      return 1;
    endfunction

    // ---- CG-CSR-002: the tracked CSRs in plan order and the bits Ibex lets a write change (mcounteren: bit 0 and 2..MHPMCounterNum+2)
    function int csr_idx(logic [11:0] a);
      case (a) 12'h300: return 0; 12'h301: return 1; 12'h304: return 2; 12'h305: return 3; 12'h306: return 4; 12'h310: return 5; 12'h30A: return 6; 12'h31A: return 7; default: return -1; endcase
    endfunction
    function logic [31:0] csr_wmask(int i);
      case (i)
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MSTATUS:    return 32'h0022_1888;   // MIE, MPIE, MPP, MPRV, TW
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MIE:        return 32'h7FFF_0888;   // software, timer, external, fast 16..30
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MTVEC:      return 32'hFFFF_FF00;
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MCOUNTEREN: return 32'h1 | (((32'h1 << (GEN_MHPM_COUNTER_NUM + 3)) - 1) & ~32'h3);
        default:                                      return 32'h0;
      endcase
    endfunction
    function int mie_w_cls(logic [31:0] v);
      logic [31:0] std = v & 32'h0000_0888, fast = v & 32'h7FFF_0000;
      if (fast == 32'h7FFF_0000) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_ALL_FAST;
      if (std != 0 && fast != 0) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_STD_FAST;
      if (std != 0) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_STD_ONLY;
      if (fast != 0) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_FAST_ONLY;
      return (v != 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_RO_ONLY : -1;
    endfunction
    function int mcen_w_cls(logic [31:0] v);
      logic [31:0] low = v & ((32'h1 << (GEN_MHPM_COUNTER_NUM + 3)) - 1);
      if (v == 32'hffff_ffff) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_ALL1;
      if (low != 0 && (low & (low - 1)) == 0 && low == v) begin   // exactly one bit, in the counter field
        if (low == 32'h1) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_CY;
        if (low == 32'h2) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_TM_RO;
        if (low == 32'h4) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_IR;
        return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM3 + ($clog2(low) - 3);
      end
      return (v != 0 && low == 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HI_RO : -1;   // only bits above the counter field
    endfunction
    // the pair closes on the read-back: the write operand classifies cp_wpat, the effective written value the field coverpoints
    function void csr_pair_sample(int i);
      int wpat, mpp = -1, mie_b = -1, mpie_b = -1, mprv_b = -1, tw_b = -1, tmode = -1, tlo = -1, tbase = -1, miew = -1, gate = -1, mcw = -1;
      logic [31:0] v = csr_eff[i], w = csr_wval[i], mask = csr_wmask(i);
      wpat = (w == 32'h0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ALL0 : (w == 32'hffff_ffff) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ALL1 :
             (w == 32'h8000_0000) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_MSB_ONLY : ((w & ~mask) == 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_LEGAL_ONLY :
             ((w & mask) == 0 && mask != 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ILLEGAL_ONLY : GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_RAND;   // a CSR without writable bits has no illegal-only class: mixed patterns are rand
      if (csr_eff_ok[i]) case (i)
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MSTATUS: begin mpp = int'(v[12:11]); mie_b = int'(v[3]); mpie_b = int'(v[7]); mprv_b = int'(v[17]); tw_b = int'(v[21]); end
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MTVEC: begin
          tmode = int'(v[1:0]); tlo = (v[7:2] != 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_LO_W_NONZERO : GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_LO_W_ZERO;
          tbase = (v[31:8] == cfg.boot_addr[31:8]) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_BOOT_PAGE : (v < 32'h1000) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_LOW :
                  v[31] ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_HIGH : GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_RAND;
        end
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MIE: miew = mie_w_cls(v);
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MCOUNTEREN: mcw = mcen_w_cls(v);
        default: ;
      endcase
      if (i == GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MCOUNTEREN)
        gate = (cfg.knob_mcounteren_writable == "on") ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_ON : (cfg.knob_mcounteren_writable == "off") ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_OFF : GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_INVALID;
      n_csr_pairs++;
      csr_cg.sample(i, csr_op[i], wpat, (csr_rd[i] == 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_RD_X0 : GEN_FC_CSR_TRAP_SETUP_WARL_CP_RD_NONX0,
                    mpp, mie_b, mpie_b, mprv_b, tw_b, tmode, tlo, tbase, miew, gate, mcw);
      csr_pend[i] = 0;
    endfunction
    // a CSR-op record on a tracked CSR: rd != x0 returns the standing value (closes an open pair, refreshes the shadow); a write opens a pair
    function bit csr_track(gen_rvfi_txn t);
      int i; logic [2:0] f3 = t.insn[14:12]; logic [31:0] src, old; bit old_ok, is_write;
      if (t.insn[6:0] != 7'b1110011 || f3 == 3'b000 || f3 == 3'b100) return 0;
      i = csr_idx(t.insn[31:20]);
      if (i < 0) return 0;
      src = f3[2] ? 32'(t.insn[19:15]) : t.rs1_rdata;
      is_write = (f3[1:0] == 2'b01) || (t.insn[19:15] != 5'd0);   // csrrs / csrrc with rs1 = x0 (uimm 0) are reads (the decoder demotes them)
      if (t.rd_addr != 0) begin
        if (csr_pend[i]) csr_pair_sample(i);
        csr_shadow[i] = t.rd_wdata; csr_shadow_ok[i] = 1;
      end
      if (is_write) begin
        if (csr_pend[i]) n_csr_replaced++;   // a second write with rd = x0 before any read-back: the first pair never closes
        old = (t.rd_addr != 0) ? t.rd_wdata : csr_shadow[i]; old_ok = (t.rd_addr != 0) || csr_shadow_ok[i];
        csr_pend[i] = 1; csr_op[i] = int'(f3[1:0]) - 1 + (f3[2] ? 3 : 0); csr_rd[i] = int'(t.rd_addr); csr_wval[i] = src;
        case (f3[1:0])
          2'b01:   begin csr_eff[i] = src;        csr_eff_ok[i] = 1; end
          2'b10:   begin csr_eff[i] = old | src;  csr_eff_ok[i] = old_ok; end
          default: begin csr_eff[i] = old & ~src; csr_eff_ok[i] = old_ok; end
        endcase
        csr_shadow_ok[i] = 0;   // the standing value is now the legalised write, known only from the next read-back
        n_csr_wr++;
      end
      return 1;
    endfunction
    function void write(gen_rvfi_txn t);
      logic [6:0] f7 = t.insn[31:25]; logic [2:0] f3 = t.insn[14:12];
      bit is_op = (t.insn[6:0] == ibex_pkg::OPCODE_OP), is_opimm = (t.insn[6:0] == ibex_pkg::OPCODE_OP_IMM);
      bit is_cmul = (t.insn[1:0] == 2'b01 && t.insn[15:10] == 6'b100111 && t.insn[6:5] == 2'b10);   // c.mul (Zcb)
      if (mul_cg == null) return;
      mv_flush(t);
      zca_flush(t);
      // an instruction boundary (a plain record, or the first micro-op of an expansion) closes the write set of the instruction before
      if (!t.ext_exp_valid || !zp_in || t.pc_rdata != zp_pc) begin prev_wr = cur_wr; prev_ld = cur_ld; prev_mv = cur_mv; cur_wr = '0; cur_ld = 0; cur_mv = -1; end
      if (!t.trap && t.rd_addr != 0) cur_wr[t.rd_addr] = 1'b1;
      begin bit st; int unsigned nb; if (gen_insn_mem_access(t.insn, st, nb) && !st) cur_ld = 1; end   // decoded: Ibex reports rvfi_mem_rmask for non-memory records too
      if (t.ext_exp_valid) begin   // a Zcmp micro-op record: the sequence collector owns it
        if (zp_in && t.pc_rdata != zp_pc) n_zcmp_abandoned++;   // a sequence replaced by another one's first micro-op (an entry split it)
        if (!zp_in || t.pc_rdata != zp_pc) zp_start(t);
        if (t.trap) begin zp_in = 0; n_zcmp_abandoned++; end else zp_step(t);
      end else if (zp_in) begin zp_in = 0; n_zcmp_abandoned++; end   // an entry split the sequence (its restart begins again)
      prev_mhpm10 = t.ext_mhpmcounters[7];
      if (t.trap) return;
      if (!t.ext_exp_valid && t.insn[1:0] != 2'b11) begin   // a Zca retirement: pending until the next record's length is known
        int op = zca_insn(t.insn[15:0]);
        if (op >= 0) begin
          n_zca++;
          zca_v[0] = op; zca_v[1] = t.pc_rdata[1] ? GEN_FC_CMP_ZCA_CP_PC_ALIGN_HALF : GEN_FC_CMP_ZCA_CP_PC_ALIGN_WORD;
          zca_v[3] = (!zca_is_cti(op) && t.pc_wdata - t.pc_rdata == 32'd2) ? GEN_FC_CMP_ZCA_CP_PC_INC_TWO : -1;
          zca_v[4] = -1; zca_v[5] = zca_reg3(op, t.insn[15:0]); zca_v[6] = zca_rd_full(op, t.insn[15:0]);
          zca_pend = 1;
        end
      end else if (!t.ext_exp_valid && t.insn[1:0] == 2'b11) begin   // a 32-bit retirement: only the straddle coverpoint
        n_zca32++;
        zca_cg.sample(-1, -1, -1, -1, t.pc_rdata[1] ? GEN_FC_CMP_ZCA_CP_INSN32_STRADDLE_YES : GEN_FC_CMP_ZCA_CP_INSN32_STRADDLE_NO, -1, -1);
      end
      if (!t.ext_exp_valid && (br_sample(t) || csr_track(t))) return;
      if (is_opimm && f3 == 3'b001 && t.insn[31:20] inside {12'h600, 12'h601, 12'h602}) begin
        int op = (t.insn[31:20] == 12'h600) ? GEN_FC_BIT_COUNT_CP_OP_CLZ : (t.insn[31:20] == 12'h601) ? GEN_FC_BIT_COUNT_CP_OP_CTZ : GEN_FC_BIT_COUNT_CP_OP_CPOP;
        n_cnt++;
        cnt_cg.sample(op, cnt_operand_cls(t.rs1_rdata), cnt_single_pos(t.rs1_rdata), cnt_result_cls(t.rd_wdata), t.rd_addr == 0);
        return;
      end
      if ((is_op && f7 == 7'b0000001 && !f3[2]) || is_cmul) begin
        int op = is_cmul ? GEN_FC_MUL_OPS_CP_OP_C_MUL : int'(f3[1:0]);   // mul, mulh, mulhsu, mulhu in funct3 order
        n_mul++;
        mul_cg.sample(op, mul_rs_cls(t.rs1_rdata), mul_rs_cls(t.rs2_rdata), sign_pair(t.rs1_rdata, t.rs2_rdata),
                      mul_same(t.rs1_addr, t.rs2_addr, t.rd_addr), t.rd_addr == 0, mul_res_cls(t.rd_wdata), is_cmul ? -1 : int'(f3));
      end else if (is_op && f7 == 7'b0000001) begin
        n_div++;
        div_cg.sample(int'(f3[1:0]), div_dividend_cls(t.rs1_rdata), div_divisor_cls(t.rs2_rdata, t.rs1_rdata), sign_pair(t.rs1_rdata, t.rs2_rdata),
                      t.rd_addr == 0, div_res_cls(t.rd_wdata, t.rs1_rdata));
      end else if (bit_op(t.insn) >= 0) begin
        int op = bit_op(t.insn);
        n_bit++;
        bit_cg.sample(op, bit_rs1_cls(t.rs1_rdata), bit_rs2_cls(t.rs2_rdata), t.rs1_rdata == t.rs2_rdata, bit_same(t.rs1_addr, t.rs2_addr, t.rd_addr),
                      t.rd_addr == 0, sign_pair(t.rs1_rdata, t.rs2_rdata), bit_res_cls(t.rd_wdata), bit_wrap(op, t.rs1_rdata, t.rs2_rdata));
      end else if (is_opimm && f3 != 3'b001 && f3 != 3'b101) begin
        int op, imm = signed'(t.insn[31:20]);   // sign-extended imm12
        case (f3)
          3'b000: op = GEN_FC_ISA_ALU_IMM_CP_OP_ADDI; 3'b010: op = GEN_FC_ISA_ALU_IMM_CP_OP_SLTI; 3'b011: op = GEN_FC_ISA_ALU_IMM_CP_OP_SLTIU;
          3'b100: op = GEN_FC_ISA_ALU_IMM_CP_OP_XORI; 3'b110: op = GEN_FC_ISA_ALU_IMM_CP_OP_ORI;  default: op = GEN_FC_ISA_ALU_IMM_CP_OP_ANDI;
        endcase
        n_imm++;
        imm_cg.sample(op, imm_rs1_cls(t.rs1_rdata), imm_cls(imm), t.rd_addr == 0, (t.rs1_addr == t.rd_addr && t.rd_addr != 0), imm_res_cls(t.rd_wdata),
                      addi_wrap(op, t.rs1_rdata, imm, t.rd_wdata), slt_case(op, t.rs1_rdata, imm));
      end else if ((is_opimm || is_op) && (f3 == 3'b001 || f3 == 3'b101) && (f7 == 7'b0000000 || f7 == 7'b0100000) && !(f3 == 3'b001 && f7 == 7'b0100000)) begin
        int op;
        if (is_opimm) op = (f3 == 3'b001) ? GEN_FC_ISA_SHIFT_CP_OP_SLLI : (f7 == 7'b0100000) ? GEN_FC_ISA_SHIFT_CP_OP_SRAI : GEN_FC_ISA_SHIFT_CP_OP_SRLI;
        else          op = (f3 == 3'b001) ? GEN_FC_ISA_SHIFT_CP_OP_SLL  : (f7 == 7'b0100000) ? GEN_FC_ISA_SHIFT_CP_OP_SRA  : GEN_FC_ISA_SHIFT_CP_OP_SRL;
        n_sh++;
        sh_cg.sample(op, sh_amt_cls(is_opimm ? t.insn[24:20] : t.rs2_rdata[4:0]), is_opimm ? -1 : sh_rs2_upper(t.rs2_rdata), sh_operand_cls(t.rs1_rdata),
                     t.rd_addr == 0, sh_res_cls(t.rd_wdata));
      end else if (is_op && (f7 == 7'b0000000 || f7 == 7'b0100000) && f3 != 3'b001 && f3 != 3'b101 && !(f7 == 7'b0100000 && f3 != 3'b000)) begin
        int op;
        case (f3)
          3'b000: op = (f7 == 7'b0100000) ? GEN_FC_ISA_ALU_REG_CP_OP_SUB : GEN_FC_ISA_ALU_REG_CP_OP_ADD;
          3'b010: op = GEN_FC_ISA_ALU_REG_CP_OP_SLT;  3'b011: op = GEN_FC_ISA_ALU_REG_CP_OP_SLTU;
          3'b100: op = GEN_FC_ISA_ALU_REG_CP_OP_XOR;  3'b110: op = GEN_FC_ISA_ALU_REG_CP_OP_OR;
          default: op = GEN_FC_ISA_ALU_REG_CP_OP_AND;
        endcase
        n_alu++;
        alu_cg.sample(op, alu_rs_cls(t.rs1_rdata), alu_rs_cls(t.rs2_rdata), sign_pair(t.rs1_rdata, t.rs2_rdata), t.rs1_rdata == t.rs2_rdata,
                      alu_same(t.rs1_addr, t.rs2_addr, t.rd_addr), t.rd_addr == 0, alu_res_cls(t.rd_wdata), alu_wrap(op, t.rs1_rdata, t.rs2_rdata));
      end
    endfunction
    function void report_phase(uvm_phase phase);
      zca_flush(null);   // the last 16-bit record has no successor: its next_len is not applicable
      mv_flush(null);    // a move pair at the very end has no neighbour after
      `uvm_info("GEN_FCOV", $sformatf("isa samples: mul=%0d div=%0d alu_reg=%0d zba_zbb=%0d alu_imm=%0d shift=%0d bit_count=%0d zca=%0d zca32=%0d zcmp=%0d (abandoned %0d) zcmp_mv=%0d branch=%0d csr_pairs=%0d (writes %0d, replaced %0d)%s", n_mul, n_div, n_alu, n_bit, n_imm, n_sh, n_cnt, n_zca, n_zca32, n_zcmp, n_zcmp_abandoned, n_mv, n_br, n_csr_pairs, n_csr_wr, n_csr_replaced, mul_cg == null ? " (covergroups off)" : ""), UVM_LOW)
    endfunction
  endclass
endpackage
