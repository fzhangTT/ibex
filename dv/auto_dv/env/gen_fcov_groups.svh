// gen_fcov_groups.svh: the fcov plan's covergroups, rendered by dv/auto_dv/tb/gen_fcov_codegen.py from
// dv/auto_dv/docs/gen_trace_tp_bin.csv (every bin) and dv/auto_dv/docs/gen_fcov_plan.md (names, bin order, cross
// components); do not edit. Included by gen_fcov_pkg.sv; the samplers there fill the sample() arguments with the
// GEN_FC_* indices (-1 = not applicable, ignored).

  // CG-MUL-001 (gen_mul_ops_cg), 46 coverpoint bins, 390 cross bins
  localparam int GEN_FC_MUL_OPS_CP_OP_MUL = 0;
  localparam int GEN_FC_MUL_OPS_CP_OP_MULH = 1;
  localparam int GEN_FC_MUL_OPS_CP_OP_MULHSU = 2;
  localparam int GEN_FC_MUL_OPS_CP_OP_MULHU = 3;
  localparam int GEN_FC_MUL_OPS_CP_OP_C_MUL = 4;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_ZERO = 0;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_ONE = 1;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_ALL_ONES = 2;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_INT_MIN = 3;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_INT_MAX = 4;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_P16 = 5;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_TWO = 6;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_NEG_RAND = 7;
  localparam int GEN_FC_MUL_OPS_CP_RS1_CLASS_POS_RAND = 8;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_ZERO = 0;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_ONE = 1;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_ALL_ONES = 2;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_INT_MIN = 3;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_INT_MAX = 4;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_P16 = 5;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_TWO = 6;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_NEG_RAND = 7;
  localparam int GEN_FC_MUL_OPS_CP_RS2_CLASS_POS_RAND = 8;
  localparam int GEN_FC_MUL_OPS_CP_SIGN_PAIR_PP = 0;
  localparam int GEN_FC_MUL_OPS_CP_SIGN_PAIR_PN = 1;
  localparam int GEN_FC_MUL_OPS_CP_SIGN_PAIR_NP = 2;
  localparam int GEN_FC_MUL_OPS_CP_SIGN_PAIR_NN = 3;
  localparam int GEN_FC_MUL_OPS_CP_SAME_REGS_RS1_EQ_RS2 = 0;
  localparam int GEN_FC_MUL_OPS_CP_SAME_REGS_ALL_SAME = 1;
  localparam int GEN_FC_MUL_OPS_CP_SAME_REGS_RS_EQ_RD = 2;
  localparam int GEN_FC_MUL_OPS_CP_SAME_REGS_DISTINCT = 3;
  localparam int GEN_FC_MUL_OPS_CP_RD_X0_NO = 0;
  localparam int GEN_FC_MUL_OPS_CP_RD_X0_YES = 1;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_ZERO = 0;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_ONE = 1;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_ALL_ONES = 2;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_INT_MIN = 3;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_INT_MAX = 4;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_FFFFFFFE = 5;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_R3FFFFFFF = 6;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_R40000000 = 7;
  localparam int GEN_FC_MUL_OPS_CP_RESULT_CLASS_OTHER = 8;
  localparam int GEN_FC_MUL_OPS_CP_FUNCT3_F0 = 0;
  localparam int GEN_FC_MUL_OPS_CP_FUNCT3_F1 = 1;
  localparam int GEN_FC_MUL_OPS_CP_FUNCT3_F2 = 2;
  localparam int GEN_FC_MUL_OPS_CP_FUNCT3_F3 = 3;
  covergroup gen_mul_ops_cg with function sample(int v_cp_op, int v_cp_rs1_class, int v_cp_rs2_class, int v_cp_sign_pair, int v_cp_same_regs, int v_cp_rd_x0, int v_cp_result_class, int v_cp_funct3);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins mul= {0}; bins mulh= {1}; bins mulhsu= {2}; bins mulhu= {3}; bins c_mul= {4}; ignore_bins na = {-1}; }
    cp_rs1_class: coverpoint v_cp_rs1_class { bins zero= {0}; bins one= {1}; bins all_ones= {2}; bins int_min= {3}; bins int_max= {4}; bins p16= {5}; bins two= {6}; bins neg_rand= {7}; bins pos_rand= {8}; ignore_bins na = {-1}; }
    cp_rs2_class: coverpoint v_cp_rs2_class { bins zero= {0}; bins one= {1}; bins all_ones= {2}; bins int_min= {3}; bins int_max= {4}; bins p16= {5}; bins two= {6}; bins neg_rand= {7}; bins pos_rand= {8}; ignore_bins na = {-1}; }
    cp_sign_pair: coverpoint v_cp_sign_pair { bins pp= {0}; bins pn= {1}; bins np= {2}; bins nn= {3}; ignore_bins na = {-1}; }
    cp_same_regs: coverpoint v_cp_same_regs { bins rs1_eq_rs2= {0}; bins all_same= {1}; bins rs_eq_rd= {2}; bins distinct= {3}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_result_class: coverpoint v_cp_result_class { bins zero= {0}; bins one= {1}; bins all_ones= {2}; bins int_min= {3}; bins int_max= {4}; bins fffffffe= {5}; bins r3fffffff= {6}; bins r40000000= {7}; bins other= {8}; ignore_bins na = {-1}; }
    cp_funct3: coverpoint v_cp_funct3 { bins f0= {0}; bins f1= {1}; bins f2= {2}; bins f3= {3}; ignore_bins na = {-1}; }
    cr_op_rs1: cross cp_op, cp_rs1_class {
      bins c_mul_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs1_class.all_ones);
      bins c_mul_int_max= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_max);
      bins c_mul_int_min= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_min);
      bins c_mul_neg_rand= binsof(cp_op.c_mul) && binsof(cp_rs1_class.neg_rand);
      bins c_mul_one= binsof(cp_op.c_mul) && binsof(cp_rs1_class.one);
      bins c_mul_p16= binsof(cp_op.c_mul) && binsof(cp_rs1_class.p16);
      bins c_mul_pos_rand= binsof(cp_op.c_mul) && binsof(cp_rs1_class.pos_rand);
      bins c_mul_two= binsof(cp_op.c_mul) && binsof(cp_rs1_class.two);
      bins c_mul_zero= binsof(cp_op.c_mul) && binsof(cp_rs1_class.zero);
      bins mul_all_ones= binsof(cp_op.mul) && binsof(cp_rs1_class.all_ones);
      bins mul_int_max= binsof(cp_op.mul) && binsof(cp_rs1_class.int_max);
      bins mul_int_min= binsof(cp_op.mul) && binsof(cp_rs1_class.int_min);
      bins mul_neg_rand= binsof(cp_op.mul) && binsof(cp_rs1_class.neg_rand);
      bins mul_one= binsof(cp_op.mul) && binsof(cp_rs1_class.one);
      bins mul_p16= binsof(cp_op.mul) && binsof(cp_rs1_class.p16);
      bins mul_pos_rand= binsof(cp_op.mul) && binsof(cp_rs1_class.pos_rand);
      bins mul_two= binsof(cp_op.mul) && binsof(cp_rs1_class.two);
      bins mul_zero= binsof(cp_op.mul) && binsof(cp_rs1_class.zero);
      bins mulh_all_ones= binsof(cp_op.mulh) && binsof(cp_rs1_class.all_ones);
      bins mulh_int_max= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_max);
      bins mulh_int_min= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_min);
      bins mulh_neg_rand= binsof(cp_op.mulh) && binsof(cp_rs1_class.neg_rand);
      bins mulh_one= binsof(cp_op.mulh) && binsof(cp_rs1_class.one);
      bins mulh_p16= binsof(cp_op.mulh) && binsof(cp_rs1_class.p16);
      bins mulh_pos_rand= binsof(cp_op.mulh) && binsof(cp_rs1_class.pos_rand);
      bins mulh_two= binsof(cp_op.mulh) && binsof(cp_rs1_class.two);
      bins mulh_zero= binsof(cp_op.mulh) && binsof(cp_rs1_class.zero);
      bins mulhsu_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.all_ones);
      bins mulhsu_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_max);
      bins mulhsu_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_min);
      bins mulhsu_neg_rand= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.neg_rand);
      bins mulhsu_one= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.one);
      bins mulhsu_p16= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.p16);
      bins mulhsu_pos_rand= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.pos_rand);
      bins mulhsu_two= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.two);
      bins mulhsu_zero= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.zero);
      bins mulhu_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs1_class.all_ones);
      bins mulhu_int_max= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_max);
      bins mulhu_int_min= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_min);
      bins mulhu_neg_rand= binsof(cp_op.mulhu) && binsof(cp_rs1_class.neg_rand);
      bins mulhu_one= binsof(cp_op.mulhu) && binsof(cp_rs1_class.one);
      bins mulhu_p16= binsof(cp_op.mulhu) && binsof(cp_rs1_class.p16);
      bins mulhu_pos_rand= binsof(cp_op.mulhu) && binsof(cp_rs1_class.pos_rand);
      bins mulhu_two= binsof(cp_op.mulhu) && binsof(cp_rs1_class.two);
      bins mulhu_zero= binsof(cp_op.mulhu) && binsof(cp_rs1_class.zero);
    }
    cr_op_same: cross cp_op, cp_same_regs {
      bins c_mul_all_same= binsof(cp_op.c_mul) && binsof(cp_same_regs.all_same);
      bins c_mul_rs_eq_rd= binsof(cp_op.c_mul) && binsof(cp_same_regs.rs_eq_rd);
      bins mul_all_same= binsof(cp_op.mul) && binsof(cp_same_regs.all_same);
      bins mul_distinct= binsof(cp_op.mul) && binsof(cp_same_regs.distinct);
      bins mul_rs1_eq_rs2= binsof(cp_op.mul) && binsof(cp_same_regs.rs1_eq_rs2);
      bins mul_rs_eq_rd= binsof(cp_op.mul) && binsof(cp_same_regs.rs_eq_rd);
      bins mulh_all_same= binsof(cp_op.mulh) && binsof(cp_same_regs.all_same);
      bins mulh_distinct= binsof(cp_op.mulh) && binsof(cp_same_regs.distinct);
      bins mulh_rs1_eq_rs2= binsof(cp_op.mulh) && binsof(cp_same_regs.rs1_eq_rs2);
      bins mulh_rs_eq_rd= binsof(cp_op.mulh) && binsof(cp_same_regs.rs_eq_rd);
      bins mulhsu_all_same= binsof(cp_op.mulhsu) && binsof(cp_same_regs.all_same);
      bins mulhsu_distinct= binsof(cp_op.mulhsu) && binsof(cp_same_regs.distinct);
      bins mulhsu_rs1_eq_rs2= binsof(cp_op.mulhsu) && binsof(cp_same_regs.rs1_eq_rs2);
      bins mulhsu_rs_eq_rd= binsof(cp_op.mulhsu) && binsof(cp_same_regs.rs_eq_rd);
      bins mulhu_all_same= binsof(cp_op.mulhu) && binsof(cp_same_regs.all_same);
      bins mulhu_distinct= binsof(cp_op.mulhu) && binsof(cp_same_regs.distinct);
      bins mulhu_rs1_eq_rs2= binsof(cp_op.mulhu) && binsof(cp_same_regs.rs1_eq_rs2);
      bins mulhu_rs_eq_rd= binsof(cp_op.mulhu) && binsof(cp_same_regs.rs_eq_rd);
    }
    cr_op_rs2: cross cp_op, cp_rs2_class {
      bins mul_all_ones= binsof(cp_op.mul) && binsof(cp_rs2_class.all_ones);
      bins mul_int_max= binsof(cp_op.mul) && binsof(cp_rs2_class.int_max);
      bins mul_int_min= binsof(cp_op.mul) && binsof(cp_rs2_class.int_min);
      bins mul_neg_rand= binsof(cp_op.mul) && binsof(cp_rs2_class.neg_rand);
      bins mul_one= binsof(cp_op.mul) && binsof(cp_rs2_class.one);
      bins mul_p16= binsof(cp_op.mul) && binsof(cp_rs2_class.p16);
      bins mul_pos_rand= binsof(cp_op.mul) && binsof(cp_rs2_class.pos_rand);
      bins mul_two= binsof(cp_op.mul) && binsof(cp_rs2_class.two);
      bins mul_zero= binsof(cp_op.mul) && binsof(cp_rs2_class.zero);
      bins c_mul_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs2_class.all_ones);
      bins c_mul_int_max= binsof(cp_op.c_mul) && binsof(cp_rs2_class.int_max);
      bins c_mul_int_min= binsof(cp_op.c_mul) && binsof(cp_rs2_class.int_min);
      bins c_mul_neg_rand= binsof(cp_op.c_mul) && binsof(cp_rs2_class.neg_rand);
      bins c_mul_one= binsof(cp_op.c_mul) && binsof(cp_rs2_class.one);
      bins c_mul_p16= binsof(cp_op.c_mul) && binsof(cp_rs2_class.p16);
      bins c_mul_pos_rand= binsof(cp_op.c_mul) && binsof(cp_rs2_class.pos_rand);
      bins c_mul_two= binsof(cp_op.c_mul) && binsof(cp_rs2_class.two);
      bins c_mul_zero= binsof(cp_op.c_mul) && binsof(cp_rs2_class.zero);
      bins mulh_all_ones= binsof(cp_op.mulh) && binsof(cp_rs2_class.all_ones);
      bins mulh_int_max= binsof(cp_op.mulh) && binsof(cp_rs2_class.int_max);
      bins mulh_int_min= binsof(cp_op.mulh) && binsof(cp_rs2_class.int_min);
      bins mulh_neg_rand= binsof(cp_op.mulh) && binsof(cp_rs2_class.neg_rand);
      bins mulh_one= binsof(cp_op.mulh) && binsof(cp_rs2_class.one);
      bins mulh_p16= binsof(cp_op.mulh) && binsof(cp_rs2_class.p16);
      bins mulh_pos_rand= binsof(cp_op.mulh) && binsof(cp_rs2_class.pos_rand);
      bins mulh_two= binsof(cp_op.mulh) && binsof(cp_rs2_class.two);
      bins mulh_zero= binsof(cp_op.mulh) && binsof(cp_rs2_class.zero);
      bins mulhsu_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.all_ones);
      bins mulhsu_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.int_max);
      bins mulhsu_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.int_min);
      bins mulhsu_neg_rand= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.neg_rand);
      bins mulhsu_one= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.one);
      bins mulhsu_p16= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.p16);
      bins mulhsu_pos_rand= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.pos_rand);
      bins mulhsu_two= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.two);
      bins mulhsu_zero= binsof(cp_op.mulhsu) && binsof(cp_rs2_class.zero);
      bins mulhu_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs2_class.all_ones);
      bins mulhu_int_max= binsof(cp_op.mulhu) && binsof(cp_rs2_class.int_max);
      bins mulhu_int_min= binsof(cp_op.mulhu) && binsof(cp_rs2_class.int_min);
      bins mulhu_neg_rand= binsof(cp_op.mulhu) && binsof(cp_rs2_class.neg_rand);
      bins mulhu_one= binsof(cp_op.mulhu) && binsof(cp_rs2_class.one);
      bins mulhu_p16= binsof(cp_op.mulhu) && binsof(cp_rs2_class.p16);
      bins mulhu_pos_rand= binsof(cp_op.mulhu) && binsof(cp_rs2_class.pos_rand);
      bins mulhu_two= binsof(cp_op.mulhu) && binsof(cp_rs2_class.two);
      bins mulhu_zero= binsof(cp_op.mulhu) && binsof(cp_rs2_class.zero);
    }
    cr_op_sign: cross cp_op, cp_sign_pair {
      bins mul_nn= binsof(cp_op.mul) && binsof(cp_sign_pair.nn);
      bins mul_np= binsof(cp_op.mul) && binsof(cp_sign_pair.np);
      bins mul_pn= binsof(cp_op.mul) && binsof(cp_sign_pair.pn);
      bins mul_pp= binsof(cp_op.mul) && binsof(cp_sign_pair.pp);
      bins c_mul_nn= binsof(cp_op.c_mul) && binsof(cp_sign_pair.nn);
      bins c_mul_np= binsof(cp_op.c_mul) && binsof(cp_sign_pair.np);
      bins c_mul_pn= binsof(cp_op.c_mul) && binsof(cp_sign_pair.pn);
      bins c_mul_pp= binsof(cp_op.c_mul) && binsof(cp_sign_pair.pp);
      bins mulh_nn= binsof(cp_op.mulh) && binsof(cp_sign_pair.nn);
      bins mulh_np= binsof(cp_op.mulh) && binsof(cp_sign_pair.np);
      bins mulh_pn= binsof(cp_op.mulh) && binsof(cp_sign_pair.pn);
      bins mulh_pp= binsof(cp_op.mulh) && binsof(cp_sign_pair.pp);
      bins mulhsu_nn= binsof(cp_op.mulhsu) && binsof(cp_sign_pair.nn);
      bins mulhsu_np= binsof(cp_op.mulhsu) && binsof(cp_sign_pair.np);
      bins mulhsu_pn= binsof(cp_op.mulhsu) && binsof(cp_sign_pair.pn);
      bins mulhsu_pp= binsof(cp_op.mulhsu) && binsof(cp_sign_pair.pp);
      bins mulhu_nn= binsof(cp_op.mulhu) && binsof(cp_sign_pair.nn);
      bins mulhu_np= binsof(cp_op.mulhu) && binsof(cp_sign_pair.np);
      bins mulhu_pn= binsof(cp_op.mulhu) && binsof(cp_sign_pair.pn);
      bins mulhu_pp= binsof(cp_op.mulhu) && binsof(cp_sign_pair.pp);
    }
    cr_extremes: cross cp_op, cp_rs1_class, cp_rs2_class {
      bins c_mul_all_ones_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.all_ones);
      bins c_mul_all_ones_int_max= binsof(cp_op.c_mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_max);
      bins c_mul_all_ones_int_min= binsof(cp_op.c_mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_min);
      bins c_mul_all_ones_one= binsof(cp_op.c_mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.one);
      bins c_mul_all_ones_p16= binsof(cp_op.c_mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.p16);
      bins c_mul_all_ones_two= binsof(cp_op.c_mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.two);
      bins c_mul_all_ones_zero= binsof(cp_op.c_mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.zero);
      bins c_mul_int_max_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.all_ones);
      bins c_mul_int_max_int_max= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_max);
      bins c_mul_int_max_int_min= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_min);
      bins c_mul_int_max_one= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.one);
      bins c_mul_int_max_p16= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.p16);
      bins c_mul_int_max_two= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.two);
      bins c_mul_int_max_zero= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.zero);
      bins c_mul_int_min_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.all_ones);
      bins c_mul_int_min_int_max= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_max);
      bins c_mul_int_min_int_min= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_min);
      bins c_mul_int_min_one= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.one);
      bins c_mul_int_min_p16= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.p16);
      bins c_mul_int_min_two= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.two);
      bins c_mul_int_min_zero= binsof(cp_op.c_mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.zero);
      bins c_mul_one_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.all_ones);
      bins c_mul_one_int_max= binsof(cp_op.c_mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_max);
      bins c_mul_one_int_min= binsof(cp_op.c_mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_min);
      bins c_mul_one_one= binsof(cp_op.c_mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.one);
      bins c_mul_one_p16= binsof(cp_op.c_mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.p16);
      bins c_mul_one_two= binsof(cp_op.c_mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.two);
      bins c_mul_one_zero= binsof(cp_op.c_mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.zero);
      bins c_mul_p16_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.all_ones);
      bins c_mul_p16_int_max= binsof(cp_op.c_mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_max);
      bins c_mul_p16_int_min= binsof(cp_op.c_mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_min);
      bins c_mul_p16_one= binsof(cp_op.c_mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.one);
      bins c_mul_p16_p16= binsof(cp_op.c_mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.p16);
      bins c_mul_p16_two= binsof(cp_op.c_mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.two);
      bins c_mul_p16_zero= binsof(cp_op.c_mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.zero);
      bins c_mul_two_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.all_ones);
      bins c_mul_two_int_max= binsof(cp_op.c_mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_max);
      bins c_mul_two_int_min= binsof(cp_op.c_mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_min);
      bins c_mul_two_one= binsof(cp_op.c_mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.one);
      bins c_mul_two_p16= binsof(cp_op.c_mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.p16);
      bins c_mul_two_two= binsof(cp_op.c_mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.two);
      bins c_mul_two_zero= binsof(cp_op.c_mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.zero);
      bins c_mul_zero_all_ones= binsof(cp_op.c_mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.all_ones);
      bins c_mul_zero_int_max= binsof(cp_op.c_mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_max);
      bins c_mul_zero_int_min= binsof(cp_op.c_mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_min);
      bins c_mul_zero_one= binsof(cp_op.c_mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.one);
      bins c_mul_zero_p16= binsof(cp_op.c_mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.p16);
      bins c_mul_zero_two= binsof(cp_op.c_mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.two);
      bins c_mul_zero_zero= binsof(cp_op.c_mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.zero);
      bins mul_all_ones_all_ones= binsof(cp_op.mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.all_ones);
      bins mul_all_ones_int_max= binsof(cp_op.mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_max);
      bins mul_all_ones_int_min= binsof(cp_op.mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_min);
      bins mul_all_ones_one= binsof(cp_op.mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.one);
      bins mul_all_ones_p16= binsof(cp_op.mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.p16);
      bins mul_all_ones_two= binsof(cp_op.mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.two);
      bins mul_all_ones_zero= binsof(cp_op.mul) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.zero);
      bins mul_int_max_all_ones= binsof(cp_op.mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.all_ones);
      bins mul_int_max_int_max= binsof(cp_op.mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_max);
      bins mul_int_max_int_min= binsof(cp_op.mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_min);
      bins mul_int_max_one= binsof(cp_op.mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.one);
      bins mul_int_max_p16= binsof(cp_op.mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.p16);
      bins mul_int_max_two= binsof(cp_op.mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.two);
      bins mul_int_max_zero= binsof(cp_op.mul) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.zero);
      bins mul_int_min_all_ones= binsof(cp_op.mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.all_ones);
      bins mul_int_min_int_max= binsof(cp_op.mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_max);
      bins mul_int_min_int_min= binsof(cp_op.mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_min);
      bins mul_int_min_one= binsof(cp_op.mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.one);
      bins mul_int_min_p16= binsof(cp_op.mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.p16);
      bins mul_int_min_two= binsof(cp_op.mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.two);
      bins mul_int_min_zero= binsof(cp_op.mul) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.zero);
      bins mul_one_all_ones= binsof(cp_op.mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.all_ones);
      bins mul_one_int_max= binsof(cp_op.mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_max);
      bins mul_one_int_min= binsof(cp_op.mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_min);
      bins mul_one_one= binsof(cp_op.mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.one);
      bins mul_one_p16= binsof(cp_op.mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.p16);
      bins mul_one_two= binsof(cp_op.mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.two);
      bins mul_one_zero= binsof(cp_op.mul) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.zero);
      bins mul_p16_all_ones= binsof(cp_op.mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.all_ones);
      bins mul_p16_int_max= binsof(cp_op.mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_max);
      bins mul_p16_int_min= binsof(cp_op.mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_min);
      bins mul_p16_one= binsof(cp_op.mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.one);
      bins mul_p16_p16= binsof(cp_op.mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.p16);
      bins mul_p16_two= binsof(cp_op.mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.two);
      bins mul_p16_zero= binsof(cp_op.mul) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.zero);
      bins mul_two_all_ones= binsof(cp_op.mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.all_ones);
      bins mul_two_int_max= binsof(cp_op.mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_max);
      bins mul_two_int_min= binsof(cp_op.mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_min);
      bins mul_two_one= binsof(cp_op.mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.one);
      bins mul_two_p16= binsof(cp_op.mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.p16);
      bins mul_two_two= binsof(cp_op.mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.two);
      bins mul_two_zero= binsof(cp_op.mul) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.zero);
      bins mul_zero_all_ones= binsof(cp_op.mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.all_ones);
      bins mul_zero_int_max= binsof(cp_op.mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_max);
      bins mul_zero_int_min= binsof(cp_op.mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_min);
      bins mul_zero_one= binsof(cp_op.mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.one);
      bins mul_zero_p16= binsof(cp_op.mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.p16);
      bins mul_zero_two= binsof(cp_op.mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.two);
      bins mul_zero_zero= binsof(cp_op.mul) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.zero);
      bins mulh_all_ones_all_ones= binsof(cp_op.mulh) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.all_ones);
      bins mulh_all_ones_int_max= binsof(cp_op.mulh) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_max);
      bins mulh_all_ones_int_min= binsof(cp_op.mulh) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_min);
      bins mulh_all_ones_one= binsof(cp_op.mulh) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.one);
      bins mulh_all_ones_p16= binsof(cp_op.mulh) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.p16);
      bins mulh_all_ones_two= binsof(cp_op.mulh) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.two);
      bins mulh_all_ones_zero= binsof(cp_op.mulh) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.zero);
      bins mulh_int_max_all_ones= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.all_ones);
      bins mulh_int_max_int_max= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_max);
      bins mulh_int_max_int_min= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_min);
      bins mulh_int_max_one= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.one);
      bins mulh_int_max_p16= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.p16);
      bins mulh_int_max_two= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.two);
      bins mulh_int_max_zero= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.zero);
      bins mulh_int_min_all_ones= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.all_ones);
      bins mulh_int_min_int_max= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_max);
      bins mulh_int_min_int_min= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_min);
      bins mulh_int_min_one= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.one);
      bins mulh_int_min_p16= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.p16);
      bins mulh_int_min_two= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.two);
      bins mulh_int_min_zero= binsof(cp_op.mulh) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.zero);
      bins mulh_one_all_ones= binsof(cp_op.mulh) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.all_ones);
      bins mulh_one_int_max= binsof(cp_op.mulh) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_max);
      bins mulh_one_int_min= binsof(cp_op.mulh) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_min);
      bins mulh_one_one= binsof(cp_op.mulh) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.one);
      bins mulh_one_p16= binsof(cp_op.mulh) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.p16);
      bins mulh_one_two= binsof(cp_op.mulh) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.two);
      bins mulh_one_zero= binsof(cp_op.mulh) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.zero);
      bins mulh_p16_all_ones= binsof(cp_op.mulh) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.all_ones);
      bins mulh_p16_int_max= binsof(cp_op.mulh) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_max);
      bins mulh_p16_int_min= binsof(cp_op.mulh) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_min);
      bins mulh_p16_one= binsof(cp_op.mulh) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.one);
      bins mulh_p16_p16= binsof(cp_op.mulh) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.p16);
      bins mulh_p16_two= binsof(cp_op.mulh) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.two);
      bins mulh_p16_zero= binsof(cp_op.mulh) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.zero);
      bins mulh_two_all_ones= binsof(cp_op.mulh) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.all_ones);
      bins mulh_two_int_max= binsof(cp_op.mulh) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_max);
      bins mulh_two_int_min= binsof(cp_op.mulh) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_min);
      bins mulh_two_one= binsof(cp_op.mulh) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.one);
      bins mulh_two_p16= binsof(cp_op.mulh) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.p16);
      bins mulh_two_two= binsof(cp_op.mulh) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.two);
      bins mulh_two_zero= binsof(cp_op.mulh) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.zero);
      bins mulh_zero_all_ones= binsof(cp_op.mulh) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.all_ones);
      bins mulh_zero_int_max= binsof(cp_op.mulh) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_max);
      bins mulh_zero_int_min= binsof(cp_op.mulh) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_min);
      bins mulh_zero_one= binsof(cp_op.mulh) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.one);
      bins mulh_zero_p16= binsof(cp_op.mulh) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.p16);
      bins mulh_zero_two= binsof(cp_op.mulh) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.two);
      bins mulh_zero_zero= binsof(cp_op.mulh) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.zero);
      bins mulhsu_all_ones_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.all_ones);
      bins mulhsu_all_ones_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_max);
      bins mulhsu_all_ones_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_min);
      bins mulhsu_all_ones_one= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.one);
      bins mulhsu_all_ones_p16= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.p16);
      bins mulhsu_all_ones_two= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.two);
      bins mulhsu_all_ones_zero= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.zero);
      bins mulhsu_int_max_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.all_ones);
      bins mulhsu_int_max_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_max);
      bins mulhsu_int_max_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_min);
      bins mulhsu_int_max_one= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.one);
      bins mulhsu_int_max_p16= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.p16);
      bins mulhsu_int_max_two= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.two);
      bins mulhsu_int_max_zero= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.zero);
      bins mulhsu_int_min_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.all_ones);
      bins mulhsu_int_min_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_max);
      bins mulhsu_int_min_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_min);
      bins mulhsu_int_min_one= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.one);
      bins mulhsu_int_min_p16= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.p16);
      bins mulhsu_int_min_two= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.two);
      bins mulhsu_int_min_zero= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.zero);
      bins mulhsu_one_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.all_ones);
      bins mulhsu_one_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_max);
      bins mulhsu_one_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_min);
      bins mulhsu_one_one= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.one);
      bins mulhsu_one_p16= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.p16);
      bins mulhsu_one_two= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.two);
      bins mulhsu_one_zero= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.zero);
      bins mulhsu_p16_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.all_ones);
      bins mulhsu_p16_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_max);
      bins mulhsu_p16_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_min);
      bins mulhsu_p16_one= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.one);
      bins mulhsu_p16_p16= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.p16);
      bins mulhsu_p16_two= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.two);
      bins mulhsu_p16_zero= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.zero);
      bins mulhsu_two_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.all_ones);
      bins mulhsu_two_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_max);
      bins mulhsu_two_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_min);
      bins mulhsu_two_one= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.one);
      bins mulhsu_two_p16= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.p16);
      bins mulhsu_two_two= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.two);
      bins mulhsu_two_zero= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.zero);
      bins mulhsu_zero_all_ones= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.all_ones);
      bins mulhsu_zero_int_max= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_max);
      bins mulhsu_zero_int_min= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_min);
      bins mulhsu_zero_one= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.one);
      bins mulhsu_zero_p16= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.p16);
      bins mulhsu_zero_two= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.two);
      bins mulhsu_zero_zero= binsof(cp_op.mulhsu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.zero);
      bins mulhu_all_ones_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.all_ones);
      bins mulhu_all_ones_int_max= binsof(cp_op.mulhu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_max);
      bins mulhu_all_ones_int_min= binsof(cp_op.mulhu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_min);
      bins mulhu_all_ones_one= binsof(cp_op.mulhu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.one);
      bins mulhu_all_ones_p16= binsof(cp_op.mulhu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.p16);
      bins mulhu_all_ones_two= binsof(cp_op.mulhu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.two);
      bins mulhu_all_ones_zero= binsof(cp_op.mulhu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.zero);
      bins mulhu_int_max_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.all_ones);
      bins mulhu_int_max_int_max= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_max);
      bins mulhu_int_max_int_min= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_min);
      bins mulhu_int_max_one= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.one);
      bins mulhu_int_max_p16= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.p16);
      bins mulhu_int_max_two= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.two);
      bins mulhu_int_max_zero= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.zero);
      bins mulhu_int_min_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.all_ones);
      bins mulhu_int_min_int_max= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_max);
      bins mulhu_int_min_int_min= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_min);
      bins mulhu_int_min_one= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.one);
      bins mulhu_int_min_p16= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.p16);
      bins mulhu_int_min_two= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.two);
      bins mulhu_int_min_zero= binsof(cp_op.mulhu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.zero);
      bins mulhu_one_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.all_ones);
      bins mulhu_one_int_max= binsof(cp_op.mulhu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_max);
      bins mulhu_one_int_min= binsof(cp_op.mulhu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_min);
      bins mulhu_one_one= binsof(cp_op.mulhu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.one);
      bins mulhu_one_p16= binsof(cp_op.mulhu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.p16);
      bins mulhu_one_two= binsof(cp_op.mulhu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.two);
      bins mulhu_one_zero= binsof(cp_op.mulhu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.zero);
      bins mulhu_p16_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.all_ones);
      bins mulhu_p16_int_max= binsof(cp_op.mulhu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_max);
      bins mulhu_p16_int_min= binsof(cp_op.mulhu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.int_min);
      bins mulhu_p16_one= binsof(cp_op.mulhu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.one);
      bins mulhu_p16_p16= binsof(cp_op.mulhu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.p16);
      bins mulhu_p16_two= binsof(cp_op.mulhu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.two);
      bins mulhu_p16_zero= binsof(cp_op.mulhu) && binsof(cp_rs1_class.p16) && binsof(cp_rs2_class.zero);
      bins mulhu_two_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.all_ones);
      bins mulhu_two_int_max= binsof(cp_op.mulhu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_max);
      bins mulhu_two_int_min= binsof(cp_op.mulhu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.int_min);
      bins mulhu_two_one= binsof(cp_op.mulhu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.one);
      bins mulhu_two_p16= binsof(cp_op.mulhu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.p16);
      bins mulhu_two_two= binsof(cp_op.mulhu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.two);
      bins mulhu_two_zero= binsof(cp_op.mulhu) && binsof(cp_rs1_class.two) && binsof(cp_rs2_class.zero);
      bins mulhu_zero_all_ones= binsof(cp_op.mulhu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.all_ones);
      bins mulhu_zero_int_max= binsof(cp_op.mulhu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_max);
      bins mulhu_zero_int_min= binsof(cp_op.mulhu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_min);
      bins mulhu_zero_one= binsof(cp_op.mulhu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.one);
      bins mulhu_zero_p16= binsof(cp_op.mulhu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.p16);
      bins mulhu_zero_two= binsof(cp_op.mulhu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.two);
      bins mulhu_zero_zero= binsof(cp_op.mulhu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.zero);
    }
    cr_funct3_rd_x0: cross cp_funct3, cp_rd_x0 {
      bins f0_no= binsof(cp_funct3.f0) && binsof(cp_rd_x0.no);
      bins f0_yes= binsof(cp_funct3.f0) && binsof(cp_rd_x0.yes);
      bins f1_no= binsof(cp_funct3.f1) && binsof(cp_rd_x0.no);
      bins f1_yes= binsof(cp_funct3.f1) && binsof(cp_rd_x0.yes);
      bins f2_no= binsof(cp_funct3.f2) && binsof(cp_rd_x0.no);
      bins f2_yes= binsof(cp_funct3.f2) && binsof(cp_rd_x0.yes);
      bins f3_no= binsof(cp_funct3.f3) && binsof(cp_rd_x0.no);
      bins f3_yes= binsof(cp_funct3.f3) && binsof(cp_rd_x0.yes);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins c_mul_no= binsof(cp_op.c_mul) && binsof(cp_rd_x0.no);
      bins mul_no= binsof(cp_op.mul) && binsof(cp_rd_x0.no);
      bins mul_yes= binsof(cp_op.mul) && binsof(cp_rd_x0.yes);
      bins mulh_no= binsof(cp_op.mulh) && binsof(cp_rd_x0.no);
      bins mulh_yes= binsof(cp_op.mulh) && binsof(cp_rd_x0.yes);
      bins mulhsu_no= binsof(cp_op.mulhsu) && binsof(cp_rd_x0.no);
      bins mulhsu_yes= binsof(cp_op.mulhsu) && binsof(cp_rd_x0.yes);
      bins mulhu_no= binsof(cp_op.mulhu) && binsof(cp_rd_x0.no);
      bins mulhu_yes= binsof(cp_op.mulhu) && binsof(cp_rd_x0.yes);
    }
  endgroup

  // CG-MUL-003 (gen_div_ops_cg), 36 coverpoint bins, 140 cross bins
  localparam int GEN_FC_DIV_OPS_CP_OP_DIV = 0;
  localparam int GEN_FC_DIV_OPS_CP_OP_DIVU = 1;
  localparam int GEN_FC_DIV_OPS_CP_OP_REM = 2;
  localparam int GEN_FC_DIV_OPS_CP_OP_REMU = 3;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_ZERO = 0;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_ONE = 1;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_ALL_ONES = 2;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_INT_MIN = 3;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_INT_MAX = 4;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_TWO = 5;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_SEVEN = 6;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_NEG_RAND = 7;
  localparam int GEN_FC_DIV_OPS_CP_DIVIDEND_POS_RAND = 8;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_ZERO = 0;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_ONE = 1;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_ALL_ONES = 2;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_INT_MIN = 3;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_TWO = 4;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_MINUS_TWO = 5;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_EQ_DIVIDEND = 6;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_ABS_GT_DIVIDEND = 7;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_NEG_RAND = 8;
  localparam int GEN_FC_DIV_OPS_CP_DIVISOR_POS_RAND = 9;
  localparam int GEN_FC_DIV_OPS_CP_SIGN_PAIR_PP = 0;
  localparam int GEN_FC_DIV_OPS_CP_SIGN_PAIR_PN = 1;
  localparam int GEN_FC_DIV_OPS_CP_SIGN_PAIR_NP = 2;
  localparam int GEN_FC_DIV_OPS_CP_SIGN_PAIR_NN = 3;
  localparam int GEN_FC_DIV_OPS_CP_RD_X0_NO = 0;
  localparam int GEN_FC_DIV_OPS_CP_RD_X0_YES = 1;
  localparam int GEN_FC_DIV_OPS_CP_RESULT_CLASS_ZERO = 0;
  localparam int GEN_FC_DIV_OPS_CP_RESULT_CLASS_ONE = 1;
  localparam int GEN_FC_DIV_OPS_CP_RESULT_CLASS_ALL_ONES = 2;
  localparam int GEN_FC_DIV_OPS_CP_RESULT_CLASS_INT_MIN = 3;
  localparam int GEN_FC_DIV_OPS_CP_RESULT_CLASS_INT_MAX = 4;
  localparam int GEN_FC_DIV_OPS_CP_RESULT_CLASS_EQ_DIVIDEND = 5;
  localparam int GEN_FC_DIV_OPS_CP_RESULT_CLASS_OTHER = 6;
  covergroup gen_div_ops_cg with function sample(int v_cp_op, int v_cp_dividend, int v_cp_divisor, int v_cp_sign_pair, int v_cp_rd_x0, int v_cp_result_class);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins div= {0}; bins divu= {1}; bins rem= {2}; bins remu= {3}; ignore_bins na = {-1}; }
    cp_dividend: coverpoint v_cp_dividend { bins zero= {0}; bins one= {1}; bins all_ones= {2}; bins int_min= {3}; bins int_max= {4}; bins two= {5}; bins seven= {6}; bins neg_rand= {7}; bins pos_rand= {8}; ignore_bins na = {-1}; }
    cp_divisor: coverpoint v_cp_divisor { bins zero= {0}; bins one= {1}; bins all_ones= {2}; bins int_min= {3}; bins two= {4}; bins minus_two= {5}; bins eq_dividend= {6}; bins abs_gt_dividend= {7}; bins neg_rand= {8}; bins pos_rand= {9}; ignore_bins na = {-1}; }
    cp_sign_pair: coverpoint v_cp_sign_pair { bins pp= {0}; bins pn= {1}; bins np= {2}; bins nn= {3}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_result_class: coverpoint v_cp_result_class { bins zero= {0}; bins one= {1}; bins all_ones= {2}; bins int_min= {3}; bins int_max= {4}; bins eq_dividend= {5}; bins other= {6}; ignore_bins na = {-1}; }
    cr_op_dividend: cross cp_op, cp_dividend {
      bins div_all_ones= binsof(cp_op.div) && binsof(cp_dividend.all_ones);
      bins div_int_max= binsof(cp_op.div) && binsof(cp_dividend.int_max);
      bins div_int_min= binsof(cp_op.div) && binsof(cp_dividend.int_min);
      bins div_neg_rand= binsof(cp_op.div) && binsof(cp_dividend.neg_rand);
      bins div_one= binsof(cp_op.div) && binsof(cp_dividend.one);
      bins div_pos_rand= binsof(cp_op.div) && binsof(cp_dividend.pos_rand);
      bins div_seven= binsof(cp_op.div) && binsof(cp_dividend.seven);
      bins div_two= binsof(cp_op.div) && binsof(cp_dividend.two);
      bins div_zero= binsof(cp_op.div) && binsof(cp_dividend.zero);
      bins divu_all_ones= binsof(cp_op.divu) && binsof(cp_dividend.all_ones);
      bins divu_int_max= binsof(cp_op.divu) && binsof(cp_dividend.int_max);
      bins divu_int_min= binsof(cp_op.divu) && binsof(cp_dividend.int_min);
      bins divu_neg_rand= binsof(cp_op.divu) && binsof(cp_dividend.neg_rand);
      bins divu_one= binsof(cp_op.divu) && binsof(cp_dividend.one);
      bins divu_pos_rand= binsof(cp_op.divu) && binsof(cp_dividend.pos_rand);
      bins divu_seven= binsof(cp_op.divu) && binsof(cp_dividend.seven);
      bins divu_two= binsof(cp_op.divu) && binsof(cp_dividend.two);
      bins divu_zero= binsof(cp_op.divu) && binsof(cp_dividend.zero);
      bins rem_all_ones= binsof(cp_op.rem) && binsof(cp_dividend.all_ones);
      bins rem_int_max= binsof(cp_op.rem) && binsof(cp_dividend.int_max);
      bins rem_int_min= binsof(cp_op.rem) && binsof(cp_dividend.int_min);
      bins rem_neg_rand= binsof(cp_op.rem) && binsof(cp_dividend.neg_rand);
      bins rem_one= binsof(cp_op.rem) && binsof(cp_dividend.one);
      bins rem_pos_rand= binsof(cp_op.rem) && binsof(cp_dividend.pos_rand);
      bins rem_seven= binsof(cp_op.rem) && binsof(cp_dividend.seven);
      bins rem_two= binsof(cp_op.rem) && binsof(cp_dividend.two);
      bins rem_zero= binsof(cp_op.rem) && binsof(cp_dividend.zero);
      bins remu_all_ones= binsof(cp_op.remu) && binsof(cp_dividend.all_ones);
      bins remu_int_max= binsof(cp_op.remu) && binsof(cp_dividend.int_max);
      bins remu_int_min= binsof(cp_op.remu) && binsof(cp_dividend.int_min);
      bins remu_neg_rand= binsof(cp_op.remu) && binsof(cp_dividend.neg_rand);
      bins remu_one= binsof(cp_op.remu) && binsof(cp_dividend.one);
      bins remu_pos_rand= binsof(cp_op.remu) && binsof(cp_dividend.pos_rand);
      bins remu_seven= binsof(cp_op.remu) && binsof(cp_dividend.seven);
      bins remu_two= binsof(cp_op.remu) && binsof(cp_dividend.two);
      bins remu_zero= binsof(cp_op.remu) && binsof(cp_dividend.zero);
    }
    cr_op_sign: cross cp_op, cp_sign_pair {
      bins div_nn= binsof(cp_op.div) && binsof(cp_sign_pair.nn);
      bins div_np= binsof(cp_op.div) && binsof(cp_sign_pair.np);
      bins div_pn= binsof(cp_op.div) && binsof(cp_sign_pair.pn);
      bins div_pp= binsof(cp_op.div) && binsof(cp_sign_pair.pp);
      bins rem_nn= binsof(cp_op.rem) && binsof(cp_sign_pair.nn);
      bins rem_np= binsof(cp_op.rem) && binsof(cp_sign_pair.np);
      bins rem_pn= binsof(cp_op.rem) && binsof(cp_sign_pair.pn);
      bins rem_pp= binsof(cp_op.rem) && binsof(cp_sign_pair.pp);
      bins divu_nn= binsof(cp_op.divu) && binsof(cp_sign_pair.nn);
      bins divu_np= binsof(cp_op.divu) && binsof(cp_sign_pair.np);
      bins divu_pn= binsof(cp_op.divu) && binsof(cp_sign_pair.pn);
      bins divu_pp= binsof(cp_op.divu) && binsof(cp_sign_pair.pp);
      bins remu_nn= binsof(cp_op.remu) && binsof(cp_sign_pair.nn);
      bins remu_np= binsof(cp_op.remu) && binsof(cp_sign_pair.np);
      bins remu_pn= binsof(cp_op.remu) && binsof(cp_sign_pair.pn);
      bins remu_pp= binsof(cp_op.remu) && binsof(cp_sign_pair.pp);
    }
    cr_op_divisor: cross cp_op, cp_divisor {
      bins divu_abs_gt_dividend= binsof(cp_op.divu) && binsof(cp_divisor.abs_gt_dividend);
      bins divu_all_ones= binsof(cp_op.divu) && binsof(cp_divisor.all_ones);
      bins divu_eq_dividend= binsof(cp_op.divu) && binsof(cp_divisor.eq_dividend);
      bins divu_int_min= binsof(cp_op.divu) && binsof(cp_divisor.int_min);
      bins divu_minus_two= binsof(cp_op.divu) && binsof(cp_divisor.minus_two);
      bins divu_neg_rand= binsof(cp_op.divu) && binsof(cp_divisor.neg_rand);
      bins divu_one= binsof(cp_op.divu) && binsof(cp_divisor.one);
      bins divu_pos_rand= binsof(cp_op.divu) && binsof(cp_divisor.pos_rand);
      bins divu_two= binsof(cp_op.divu) && binsof(cp_divisor.two);
      bins divu_zero= binsof(cp_op.divu) && binsof(cp_divisor.zero);
      bins remu_abs_gt_dividend= binsof(cp_op.remu) && binsof(cp_divisor.abs_gt_dividend);
      bins remu_all_ones= binsof(cp_op.remu) && binsof(cp_divisor.all_ones);
      bins remu_eq_dividend= binsof(cp_op.remu) && binsof(cp_divisor.eq_dividend);
      bins remu_int_min= binsof(cp_op.remu) && binsof(cp_divisor.int_min);
      bins remu_minus_two= binsof(cp_op.remu) && binsof(cp_divisor.minus_two);
      bins remu_neg_rand= binsof(cp_op.remu) && binsof(cp_divisor.neg_rand);
      bins remu_one= binsof(cp_op.remu) && binsof(cp_divisor.one);
      bins remu_pos_rand= binsof(cp_op.remu) && binsof(cp_divisor.pos_rand);
      bins remu_two= binsof(cp_op.remu) && binsof(cp_divisor.two);
      bins remu_zero= binsof(cp_op.remu) && binsof(cp_divisor.zero);
      bins div_abs_gt_dividend= binsof(cp_op.div) && binsof(cp_divisor.abs_gt_dividend);
      bins div_all_ones= binsof(cp_op.div) && binsof(cp_divisor.all_ones);
      bins div_eq_dividend= binsof(cp_op.div) && binsof(cp_divisor.eq_dividend);
      bins div_int_min= binsof(cp_op.div) && binsof(cp_divisor.int_min);
      bins div_minus_two= binsof(cp_op.div) && binsof(cp_divisor.minus_two);
      bins div_neg_rand= binsof(cp_op.div) && binsof(cp_divisor.neg_rand);
      bins div_one= binsof(cp_op.div) && binsof(cp_divisor.one);
      bins div_pos_rand= binsof(cp_op.div) && binsof(cp_divisor.pos_rand);
      bins div_two= binsof(cp_op.div) && binsof(cp_divisor.two);
      bins div_zero= binsof(cp_op.div) && binsof(cp_divisor.zero);
      bins rem_abs_gt_dividend= binsof(cp_op.rem) && binsof(cp_divisor.abs_gt_dividend);
      bins rem_all_ones= binsof(cp_op.rem) && binsof(cp_divisor.all_ones);
      bins rem_eq_dividend= binsof(cp_op.rem) && binsof(cp_divisor.eq_dividend);
      bins rem_int_min= binsof(cp_op.rem) && binsof(cp_divisor.int_min);
      bins rem_minus_two= binsof(cp_op.rem) && binsof(cp_divisor.minus_two);
      bins rem_neg_rand= binsof(cp_op.rem) && binsof(cp_divisor.neg_rand);
      bins rem_one= binsof(cp_op.rem) && binsof(cp_divisor.one);
      bins rem_pos_rand= binsof(cp_op.rem) && binsof(cp_divisor.pos_rand);
      bins rem_two= binsof(cp_op.rem) && binsof(cp_divisor.two);
      bins rem_zero= binsof(cp_op.rem) && binsof(cp_divisor.zero);
    }
    cr_div0: cross cp_op, cp_divisor, cp_dividend {
      bins div_zero_all_ones= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.all_ones);
      bins div_zero_int_max= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.int_max);
      bins div_zero_int_min= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.int_min);
      bins div_zero_neg_rand= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.neg_rand);
      bins div_zero_one= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.one);
      bins div_zero_pos_rand= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.pos_rand);
      bins div_zero_seven= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.seven);
      bins div_zero_two= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.two);
      bins div_zero_zero= binsof(cp_op.div) && binsof(cp_divisor.zero) && binsof(cp_dividend.zero);
      bins divu_zero_all_ones= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.all_ones);
      bins divu_zero_int_max= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.int_max);
      bins divu_zero_int_min= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.int_min);
      bins divu_zero_neg_rand= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.neg_rand);
      bins divu_zero_one= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.one);
      bins divu_zero_pos_rand= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.pos_rand);
      bins divu_zero_seven= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.seven);
      bins divu_zero_two= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.two);
      bins divu_zero_zero= binsof(cp_op.divu) && binsof(cp_divisor.zero) && binsof(cp_dividend.zero);
      bins rem_zero_all_ones= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.all_ones);
      bins rem_zero_int_max= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.int_max);
      bins rem_zero_int_min= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.int_min);
      bins rem_zero_neg_rand= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.neg_rand);
      bins rem_zero_one= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.one);
      bins rem_zero_pos_rand= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.pos_rand);
      bins rem_zero_seven= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.seven);
      bins rem_zero_two= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.two);
      bins rem_zero_zero= binsof(cp_op.rem) && binsof(cp_divisor.zero) && binsof(cp_dividend.zero);
      bins remu_zero_all_ones= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.all_ones);
      bins remu_zero_int_max= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.int_max);
      bins remu_zero_int_min= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.int_min);
      bins remu_zero_neg_rand= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.neg_rand);
      bins remu_zero_one= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.one);
      bins remu_zero_pos_rand= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.pos_rand);
      bins remu_zero_seven= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.seven);
      bins remu_zero_two= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.two);
      bins remu_zero_zero= binsof(cp_op.remu) && binsof(cp_divisor.zero) && binsof(cp_dividend.zero);
    }
    cr_overflow: cross cp_op, cp_dividend, cp_divisor {
      bins div_intmin_m1= binsof(cp_op.div) && binsof(cp_dividend.int_min) && binsof(cp_divisor.all_ones);
      bins divu_intmin_m1= binsof(cp_op.divu) && binsof(cp_dividend.int_min) && binsof(cp_divisor.all_ones);
      bins rem_intmin_m1= binsof(cp_op.rem) && binsof(cp_dividend.int_min) && binsof(cp_divisor.all_ones);
      bins remu_intmin_m1= binsof(cp_op.remu) && binsof(cp_dividend.int_min) && binsof(cp_divisor.all_ones);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins div_no= binsof(cp_op.div) && binsof(cp_rd_x0.no);
      bins div_yes= binsof(cp_op.div) && binsof(cp_rd_x0.yes);
      bins divu_no= binsof(cp_op.divu) && binsof(cp_rd_x0.no);
      bins divu_yes= binsof(cp_op.divu) && binsof(cp_rd_x0.yes);
      bins rem_no= binsof(cp_op.rem) && binsof(cp_rd_x0.no);
      bins rem_yes= binsof(cp_op.rem) && binsof(cp_rd_x0.yes);
      bins remu_no= binsof(cp_op.remu) && binsof(cp_rd_x0.no);
      bins remu_yes= binsof(cp_op.remu) && binsof(cp_rd_x0.yes);
    }
  endgroup

  // CG-ISA-002 (gen_isa_alu_reg_cg), 46 coverpoint bins, 294 cross bins
  localparam int GEN_FC_ISA_ALU_REG_CP_OP_ADD = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_OP_SUB = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_OP_SLT = 2;
  localparam int GEN_FC_ISA_ALU_REG_CP_OP_SLTU = 3;
  localparam int GEN_FC_ISA_ALU_REG_CP_OP_XOR = 4;
  localparam int GEN_FC_ISA_ALU_REG_CP_OP_OR = 5;
  localparam int GEN_FC_ISA_ALU_REG_CP_OP_AND = 6;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ZERO = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_INT_MIN = 2;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_INT_MAX = 3;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ONE = 4;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_POS_RAND = 5;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_NEG_RAND = 6;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS2_CLASS_ZERO = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS2_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS2_CLASS_INT_MIN = 2;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS2_CLASS_INT_MAX = 3;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS2_CLASS_ONE = 4;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS2_CLASS_POS_RAND = 5;
  localparam int GEN_FC_ISA_ALU_REG_CP_RS2_CLASS_NEG_RAND = 6;
  localparam int GEN_FC_ISA_ALU_REG_CP_SIGN_PAIR_PP = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_SIGN_PAIR_PN = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_SIGN_PAIR_NP = 2;
  localparam int GEN_FC_ISA_ALU_REG_CP_SIGN_PAIR_NN = 3;
  localparam int GEN_FC_ISA_ALU_REG_CP_EQ_OPERANDS_NO = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_EQ_OPERANDS_YES = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS1_EQ_RS2 = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_SAME_REGS_ALL_SAME = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS1_EQ_RD = 2;
  localparam int GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS2_EQ_RD = 3;
  localparam int GEN_FC_ISA_ALU_REG_CP_SAME_REGS_DISTINCT = 4;
  localparam int GEN_FC_ISA_ALU_REG_CP_RD_X0_NO = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_RD_X0_YES = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ZERO = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_INT_MIN = 2;
  localparam int GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_INT_MAX = 3;
  localparam int GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ONE = 4;
  localparam int GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_OTHER = 5;
  localparam int GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_CARRY = 0;
  localparam int GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_POS_OVF = 1;
  localparam int GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_NEG_OVF = 2;
  localparam int GEN_FC_ISA_ALU_REG_CP_WRAP_SUB_BORROW = 3;
  localparam int GEN_FC_ISA_ALU_REG_CP_WRAP_SUB_OVF = 4;
  localparam int GEN_FC_ISA_ALU_REG_CP_WRAP_NONE = 5;
  covergroup gen_isa_alu_reg_cg with function sample(int v_cp_op, int v_cp_rs1_class, int v_cp_rs2_class, int v_cp_sign_pair, int v_cp_eq_operands, int v_cp_same_regs, int v_cp_rd_x0, int v_cp_result_class, int v_cp_wrap);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins add= {0}; bins sub= {1}; bins slt= {2}; bins sltu= {3}; bins \xor = {4}; bins \or = {5}; bins \and = {6}; ignore_bins na = {-1}; }
    cp_rs1_class: coverpoint v_cp_rs1_class { bins zero= {0}; bins all_ones= {1}; bins int_min= {2}; bins int_max= {3}; bins one= {4}; bins pos_rand= {5}; bins neg_rand= {6}; ignore_bins na = {-1}; }
    cp_rs2_class: coverpoint v_cp_rs2_class { bins zero= {0}; bins all_ones= {1}; bins int_min= {2}; bins int_max= {3}; bins one= {4}; bins pos_rand= {5}; bins neg_rand= {6}; ignore_bins na = {-1}; }
    cp_sign_pair: coverpoint v_cp_sign_pair { bins pp= {0}; bins pn= {1}; bins np= {2}; bins nn= {3}; ignore_bins na = {-1}; }
    cp_eq_operands: coverpoint v_cp_eq_operands { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_same_regs: coverpoint v_cp_same_regs { bins rs1_eq_rs2= {0}; bins all_same= {1}; bins rs1_eq_rd= {2}; bins rs2_eq_rd= {3}; bins distinct= {4}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_result_class: coverpoint v_cp_result_class { bins zero= {0}; bins all_ones= {1}; bins int_min= {2}; bins int_max= {3}; bins one= {4}; bins other= {5}; ignore_bins na = {-1}; }
    cp_wrap: coverpoint v_cp_wrap { bins add_carry= {0}; bins add_pos_ovf= {1}; bins add_neg_ovf= {2}; bins sub_borrow= {3}; bins sub_ovf= {4}; bins none= {5}; ignore_bins na = {-1}; }
    cr_op_eq: cross cp_op, cp_eq_operands {
      bins add_no= binsof(cp_op.add) && binsof(cp_eq_operands.no);
      bins and_no= binsof(cp_op.\and ) && binsof(cp_eq_operands.no);
      bins or_no= binsof(cp_op.\or ) && binsof(cp_eq_operands.no);
      bins slt_no= binsof(cp_op.slt) && binsof(cp_eq_operands.no);
      bins sltu_no= binsof(cp_op.sltu) && binsof(cp_eq_operands.no);
      bins sub_no= binsof(cp_op.sub) && binsof(cp_eq_operands.no);
      bins xor_no= binsof(cp_op.\xor ) && binsof(cp_eq_operands.no);
      bins add_yes= binsof(cp_op.add) && binsof(cp_eq_operands.yes);
      bins and_yes= binsof(cp_op.\and ) && binsof(cp_eq_operands.yes);
      bins or_yes= binsof(cp_op.\or ) && binsof(cp_eq_operands.yes);
      bins slt_yes= binsof(cp_op.slt) && binsof(cp_eq_operands.yes);
      bins sltu_yes= binsof(cp_op.sltu) && binsof(cp_eq_operands.yes);
      bins sub_yes= binsof(cp_op.sub) && binsof(cp_eq_operands.yes);
      bins xor_yes= binsof(cp_op.\xor ) && binsof(cp_eq_operands.yes);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins add_no= binsof(cp_op.add) && binsof(cp_rd_x0.no);
      bins add_yes= binsof(cp_op.add) && binsof(cp_rd_x0.yes);
      bins and_no= binsof(cp_op.\and ) && binsof(cp_rd_x0.no);
      bins and_yes= binsof(cp_op.\and ) && binsof(cp_rd_x0.yes);
      bins or_no= binsof(cp_op.\or ) && binsof(cp_rd_x0.no);
      bins or_yes= binsof(cp_op.\or ) && binsof(cp_rd_x0.yes);
      bins slt_no= binsof(cp_op.slt) && binsof(cp_rd_x0.no);
      bins slt_yes= binsof(cp_op.slt) && binsof(cp_rd_x0.yes);
      bins sltu_no= binsof(cp_op.sltu) && binsof(cp_rd_x0.no);
      bins sltu_yes= binsof(cp_op.sltu) && binsof(cp_rd_x0.yes);
      bins sub_no= binsof(cp_op.sub) && binsof(cp_rd_x0.no);
      bins sub_yes= binsof(cp_op.sub) && binsof(cp_rd_x0.yes);
      bins xor_no= binsof(cp_op.\xor ) && binsof(cp_rd_x0.no);
      bins xor_yes= binsof(cp_op.\xor ) && binsof(cp_rd_x0.yes);
    }
    cr_op_rs1: cross cp_op, cp_rs1_class {
      bins add_all_ones= binsof(cp_op.add) && binsof(cp_rs1_class.all_ones);
      bins add_int_max= binsof(cp_op.add) && binsof(cp_rs1_class.int_max);
      bins add_int_min= binsof(cp_op.add) && binsof(cp_rs1_class.int_min);
      bins add_neg_rand= binsof(cp_op.add) && binsof(cp_rs1_class.neg_rand);
      bins add_one= binsof(cp_op.add) && binsof(cp_rs1_class.one);
      bins add_pos_rand= binsof(cp_op.add) && binsof(cp_rs1_class.pos_rand);
      bins add_zero= binsof(cp_op.add) && binsof(cp_rs1_class.zero);
      bins and_all_ones= binsof(cp_op.\and ) && binsof(cp_rs1_class.all_ones);
      bins and_int_max= binsof(cp_op.\and ) && binsof(cp_rs1_class.int_max);
      bins and_int_min= binsof(cp_op.\and ) && binsof(cp_rs1_class.int_min);
      bins and_neg_rand= binsof(cp_op.\and ) && binsof(cp_rs1_class.neg_rand);
      bins and_one= binsof(cp_op.\and ) && binsof(cp_rs1_class.one);
      bins and_pos_rand= binsof(cp_op.\and ) && binsof(cp_rs1_class.pos_rand);
      bins and_zero= binsof(cp_op.\and ) && binsof(cp_rs1_class.zero);
      bins or_all_ones= binsof(cp_op.\or ) && binsof(cp_rs1_class.all_ones);
      bins or_int_max= binsof(cp_op.\or ) && binsof(cp_rs1_class.int_max);
      bins or_int_min= binsof(cp_op.\or ) && binsof(cp_rs1_class.int_min);
      bins or_neg_rand= binsof(cp_op.\or ) && binsof(cp_rs1_class.neg_rand);
      bins or_one= binsof(cp_op.\or ) && binsof(cp_rs1_class.one);
      bins or_pos_rand= binsof(cp_op.\or ) && binsof(cp_rs1_class.pos_rand);
      bins or_zero= binsof(cp_op.\or ) && binsof(cp_rs1_class.zero);
      bins slt_all_ones= binsof(cp_op.slt) && binsof(cp_rs1_class.all_ones);
      bins slt_int_max= binsof(cp_op.slt) && binsof(cp_rs1_class.int_max);
      bins slt_int_min= binsof(cp_op.slt) && binsof(cp_rs1_class.int_min);
      bins slt_neg_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.neg_rand);
      bins slt_one= binsof(cp_op.slt) && binsof(cp_rs1_class.one);
      bins slt_pos_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.pos_rand);
      bins slt_zero= binsof(cp_op.slt) && binsof(cp_rs1_class.zero);
      bins sltu_all_ones= binsof(cp_op.sltu) && binsof(cp_rs1_class.all_ones);
      bins sltu_int_max= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_max);
      bins sltu_int_min= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_min);
      bins sltu_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.neg_rand);
      bins sltu_one= binsof(cp_op.sltu) && binsof(cp_rs1_class.one);
      bins sltu_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.pos_rand);
      bins sltu_zero= binsof(cp_op.sltu) && binsof(cp_rs1_class.zero);
      bins sub_all_ones= binsof(cp_op.sub) && binsof(cp_rs1_class.all_ones);
      bins sub_int_max= binsof(cp_op.sub) && binsof(cp_rs1_class.int_max);
      bins sub_int_min= binsof(cp_op.sub) && binsof(cp_rs1_class.int_min);
      bins sub_neg_rand= binsof(cp_op.sub) && binsof(cp_rs1_class.neg_rand);
      bins sub_one= binsof(cp_op.sub) && binsof(cp_rs1_class.one);
      bins sub_pos_rand= binsof(cp_op.sub) && binsof(cp_rs1_class.pos_rand);
      bins sub_zero= binsof(cp_op.sub) && binsof(cp_rs1_class.zero);
      bins xor_all_ones= binsof(cp_op.\xor ) && binsof(cp_rs1_class.all_ones);
      bins xor_int_max= binsof(cp_op.\xor ) && binsof(cp_rs1_class.int_max);
      bins xor_int_min= binsof(cp_op.\xor ) && binsof(cp_rs1_class.int_min);
      bins xor_neg_rand= binsof(cp_op.\xor ) && binsof(cp_rs1_class.neg_rand);
      bins xor_one= binsof(cp_op.\xor ) && binsof(cp_rs1_class.one);
      bins xor_pos_rand= binsof(cp_op.\xor ) && binsof(cp_rs1_class.pos_rand);
      bins xor_zero= binsof(cp_op.\xor ) && binsof(cp_rs1_class.zero);
    }
    cr_op_rs2: cross cp_op, cp_rs2_class {
      bins add_all_ones= binsof(cp_op.add) && binsof(cp_rs2_class.all_ones);
      bins add_int_max= binsof(cp_op.add) && binsof(cp_rs2_class.int_max);
      bins add_int_min= binsof(cp_op.add) && binsof(cp_rs2_class.int_min);
      bins add_neg_rand= binsof(cp_op.add) && binsof(cp_rs2_class.neg_rand);
      bins add_one= binsof(cp_op.add) && binsof(cp_rs2_class.one);
      bins add_pos_rand= binsof(cp_op.add) && binsof(cp_rs2_class.pos_rand);
      bins add_zero= binsof(cp_op.add) && binsof(cp_rs2_class.zero);
      bins and_all_ones= binsof(cp_op.\and ) && binsof(cp_rs2_class.all_ones);
      bins and_int_max= binsof(cp_op.\and ) && binsof(cp_rs2_class.int_max);
      bins and_int_min= binsof(cp_op.\and ) && binsof(cp_rs2_class.int_min);
      bins and_neg_rand= binsof(cp_op.\and ) && binsof(cp_rs2_class.neg_rand);
      bins and_one= binsof(cp_op.\and ) && binsof(cp_rs2_class.one);
      bins and_pos_rand= binsof(cp_op.\and ) && binsof(cp_rs2_class.pos_rand);
      bins and_zero= binsof(cp_op.\and ) && binsof(cp_rs2_class.zero);
      bins or_all_ones= binsof(cp_op.\or ) && binsof(cp_rs2_class.all_ones);
      bins or_int_max= binsof(cp_op.\or ) && binsof(cp_rs2_class.int_max);
      bins or_int_min= binsof(cp_op.\or ) && binsof(cp_rs2_class.int_min);
      bins or_neg_rand= binsof(cp_op.\or ) && binsof(cp_rs2_class.neg_rand);
      bins or_one= binsof(cp_op.\or ) && binsof(cp_rs2_class.one);
      bins or_pos_rand= binsof(cp_op.\or ) && binsof(cp_rs2_class.pos_rand);
      bins or_zero= binsof(cp_op.\or ) && binsof(cp_rs2_class.zero);
      bins slt_all_ones= binsof(cp_op.slt) && binsof(cp_rs2_class.all_ones);
      bins slt_int_max= binsof(cp_op.slt) && binsof(cp_rs2_class.int_max);
      bins slt_int_min= binsof(cp_op.slt) && binsof(cp_rs2_class.int_min);
      bins slt_neg_rand= binsof(cp_op.slt) && binsof(cp_rs2_class.neg_rand);
      bins slt_one= binsof(cp_op.slt) && binsof(cp_rs2_class.one);
      bins slt_pos_rand= binsof(cp_op.slt) && binsof(cp_rs2_class.pos_rand);
      bins slt_zero= binsof(cp_op.slt) && binsof(cp_rs2_class.zero);
      bins sltu_all_ones= binsof(cp_op.sltu) && binsof(cp_rs2_class.all_ones);
      bins sltu_int_max= binsof(cp_op.sltu) && binsof(cp_rs2_class.int_max);
      bins sltu_int_min= binsof(cp_op.sltu) && binsof(cp_rs2_class.int_min);
      bins sltu_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs2_class.neg_rand);
      bins sltu_one= binsof(cp_op.sltu) && binsof(cp_rs2_class.one);
      bins sltu_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs2_class.pos_rand);
      bins sltu_zero= binsof(cp_op.sltu) && binsof(cp_rs2_class.zero);
      bins sub_all_ones= binsof(cp_op.sub) && binsof(cp_rs2_class.all_ones);
      bins sub_int_max= binsof(cp_op.sub) && binsof(cp_rs2_class.int_max);
      bins sub_int_min= binsof(cp_op.sub) && binsof(cp_rs2_class.int_min);
      bins sub_neg_rand= binsof(cp_op.sub) && binsof(cp_rs2_class.neg_rand);
      bins sub_one= binsof(cp_op.sub) && binsof(cp_rs2_class.one);
      bins sub_pos_rand= binsof(cp_op.sub) && binsof(cp_rs2_class.pos_rand);
      bins sub_zero= binsof(cp_op.sub) && binsof(cp_rs2_class.zero);
      bins xor_all_ones= binsof(cp_op.\xor ) && binsof(cp_rs2_class.all_ones);
      bins xor_int_max= binsof(cp_op.\xor ) && binsof(cp_rs2_class.int_max);
      bins xor_int_min= binsof(cp_op.\xor ) && binsof(cp_rs2_class.int_min);
      bins xor_neg_rand= binsof(cp_op.\xor ) && binsof(cp_rs2_class.neg_rand);
      bins xor_one= binsof(cp_op.\xor ) && binsof(cp_rs2_class.one);
      bins xor_pos_rand= binsof(cp_op.\xor ) && binsof(cp_rs2_class.pos_rand);
      bins xor_zero= binsof(cp_op.\xor ) && binsof(cp_rs2_class.zero);
    }
    cr_op_same: cross cp_op, cp_same_regs {
      bins add_all_same= binsof(cp_op.add) && binsof(cp_same_regs.all_same);
      bins add_distinct= binsof(cp_op.add) && binsof(cp_same_regs.distinct);
      bins add_rs1_eq_rd= binsof(cp_op.add) && binsof(cp_same_regs.rs1_eq_rd);
      bins add_rs1_eq_rs2= binsof(cp_op.add) && binsof(cp_same_regs.rs1_eq_rs2);
      bins add_rs2_eq_rd= binsof(cp_op.add) && binsof(cp_same_regs.rs2_eq_rd);
      bins and_all_same= binsof(cp_op.\and ) && binsof(cp_same_regs.all_same);
      bins and_distinct= binsof(cp_op.\and ) && binsof(cp_same_regs.distinct);
      bins and_rs1_eq_rd= binsof(cp_op.\and ) && binsof(cp_same_regs.rs1_eq_rd);
      bins and_rs1_eq_rs2= binsof(cp_op.\and ) && binsof(cp_same_regs.rs1_eq_rs2);
      bins and_rs2_eq_rd= binsof(cp_op.\and ) && binsof(cp_same_regs.rs2_eq_rd);
      bins or_all_same= binsof(cp_op.\or ) && binsof(cp_same_regs.all_same);
      bins or_distinct= binsof(cp_op.\or ) && binsof(cp_same_regs.distinct);
      bins or_rs1_eq_rd= binsof(cp_op.\or ) && binsof(cp_same_regs.rs1_eq_rd);
      bins or_rs1_eq_rs2= binsof(cp_op.\or ) && binsof(cp_same_regs.rs1_eq_rs2);
      bins or_rs2_eq_rd= binsof(cp_op.\or ) && binsof(cp_same_regs.rs2_eq_rd);
      bins slt_all_same= binsof(cp_op.slt) && binsof(cp_same_regs.all_same);
      bins slt_distinct= binsof(cp_op.slt) && binsof(cp_same_regs.distinct);
      bins slt_rs1_eq_rd= binsof(cp_op.slt) && binsof(cp_same_regs.rs1_eq_rd);
      bins slt_rs1_eq_rs2= binsof(cp_op.slt) && binsof(cp_same_regs.rs1_eq_rs2);
      bins slt_rs2_eq_rd= binsof(cp_op.slt) && binsof(cp_same_regs.rs2_eq_rd);
      bins sltu_all_same= binsof(cp_op.sltu) && binsof(cp_same_regs.all_same);
      bins sltu_distinct= binsof(cp_op.sltu) && binsof(cp_same_regs.distinct);
      bins sltu_rs1_eq_rd= binsof(cp_op.sltu) && binsof(cp_same_regs.rs1_eq_rd);
      bins sltu_rs1_eq_rs2= binsof(cp_op.sltu) && binsof(cp_same_regs.rs1_eq_rs2);
      bins sltu_rs2_eq_rd= binsof(cp_op.sltu) && binsof(cp_same_regs.rs2_eq_rd);
      bins sub_all_same= binsof(cp_op.sub) && binsof(cp_same_regs.all_same);
      bins sub_distinct= binsof(cp_op.sub) && binsof(cp_same_regs.distinct);
      bins sub_rs1_eq_rd= binsof(cp_op.sub) && binsof(cp_same_regs.rs1_eq_rd);
      bins sub_rs1_eq_rs2= binsof(cp_op.sub) && binsof(cp_same_regs.rs1_eq_rs2);
      bins sub_rs2_eq_rd= binsof(cp_op.sub) && binsof(cp_same_regs.rs2_eq_rd);
      bins xor_all_same= binsof(cp_op.\xor ) && binsof(cp_same_regs.all_same);
      bins xor_distinct= binsof(cp_op.\xor ) && binsof(cp_same_regs.distinct);
      bins xor_rs1_eq_rd= binsof(cp_op.\xor ) && binsof(cp_same_regs.rs1_eq_rd);
      bins xor_rs1_eq_rs2= binsof(cp_op.\xor ) && binsof(cp_same_regs.rs1_eq_rs2);
      bins xor_rs2_eq_rd= binsof(cp_op.\xor ) && binsof(cp_same_regs.rs2_eq_rd);
    }
    cr_op_sign: cross cp_op, cp_sign_pair {
      bins add_nn= binsof(cp_op.add) && binsof(cp_sign_pair.nn);
      bins add_np= binsof(cp_op.add) && binsof(cp_sign_pair.np);
      bins add_pn= binsof(cp_op.add) && binsof(cp_sign_pair.pn);
      bins add_pp= binsof(cp_op.add) && binsof(cp_sign_pair.pp);
      bins and_nn= binsof(cp_op.\and ) && binsof(cp_sign_pair.nn);
      bins and_np= binsof(cp_op.\and ) && binsof(cp_sign_pair.np);
      bins and_pn= binsof(cp_op.\and ) && binsof(cp_sign_pair.pn);
      bins and_pp= binsof(cp_op.\and ) && binsof(cp_sign_pair.pp);
      bins or_nn= binsof(cp_op.\or ) && binsof(cp_sign_pair.nn);
      bins or_np= binsof(cp_op.\or ) && binsof(cp_sign_pair.np);
      bins or_pn= binsof(cp_op.\or ) && binsof(cp_sign_pair.pn);
      bins or_pp= binsof(cp_op.\or ) && binsof(cp_sign_pair.pp);
      bins slt_nn= binsof(cp_op.slt) && binsof(cp_sign_pair.nn);
      bins slt_np= binsof(cp_op.slt) && binsof(cp_sign_pair.np);
      bins slt_pn= binsof(cp_op.slt) && binsof(cp_sign_pair.pn);
      bins slt_pp= binsof(cp_op.slt) && binsof(cp_sign_pair.pp);
      bins sltu_nn= binsof(cp_op.sltu) && binsof(cp_sign_pair.nn);
      bins sltu_np= binsof(cp_op.sltu) && binsof(cp_sign_pair.np);
      bins sltu_pn= binsof(cp_op.sltu) && binsof(cp_sign_pair.pn);
      bins sltu_pp= binsof(cp_op.sltu) && binsof(cp_sign_pair.pp);
      bins sub_nn= binsof(cp_op.sub) && binsof(cp_sign_pair.nn);
      bins sub_np= binsof(cp_op.sub) && binsof(cp_sign_pair.np);
      bins sub_pn= binsof(cp_op.sub) && binsof(cp_sign_pair.pn);
      bins sub_pp= binsof(cp_op.sub) && binsof(cp_sign_pair.pp);
      bins xor_nn= binsof(cp_op.\xor ) && binsof(cp_sign_pair.nn);
      bins xor_np= binsof(cp_op.\xor ) && binsof(cp_sign_pair.np);
      bins xor_pn= binsof(cp_op.\xor ) && binsof(cp_sign_pair.pn);
      bins xor_pp= binsof(cp_op.\xor ) && binsof(cp_sign_pair.pp);
    }
    cr_wrap: cross cp_op, cp_wrap {
      bins add_none= binsof(cp_op.add) && binsof(cp_wrap.none);
      bins sub_none= binsof(cp_op.sub) && binsof(cp_wrap.none);
      bins add_add_carry= binsof(cp_op.add) && binsof(cp_wrap.add_carry);
      bins add_add_neg_ovf= binsof(cp_op.add) && binsof(cp_wrap.add_neg_ovf);
      bins add_add_pos_ovf= binsof(cp_op.add) && binsof(cp_wrap.add_pos_ovf);
      bins sub_sub_borrow= binsof(cp_op.sub) && binsof(cp_wrap.sub_borrow);
      bins sub_sub_ovf= binsof(cp_op.sub) && binsof(cp_wrap.sub_ovf);
    }
    cr_slt_boundary: cross cp_op, cp_rs1_class, cp_rs2_class {
      bins slt_all_ones_all_ones= binsof(cp_op.slt) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.all_ones);
      bins slt_all_ones_int_max= binsof(cp_op.slt) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_max);
      bins slt_all_ones_int_min= binsof(cp_op.slt) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_min);
      bins slt_all_ones_neg_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.neg_rand);
      bins slt_all_ones_one= binsof(cp_op.slt) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.one);
      bins slt_all_ones_pos_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.pos_rand);
      bins slt_all_ones_zero= binsof(cp_op.slt) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.zero);
      bins slt_int_max_all_ones= binsof(cp_op.slt) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.all_ones);
      bins slt_int_max_int_max= binsof(cp_op.slt) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_max);
      bins slt_int_max_int_min= binsof(cp_op.slt) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_min);
      bins slt_int_max_neg_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.neg_rand);
      bins slt_int_max_one= binsof(cp_op.slt) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.one);
      bins slt_int_max_pos_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.pos_rand);
      bins slt_int_max_zero= binsof(cp_op.slt) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.zero);
      bins slt_int_min_all_ones= binsof(cp_op.slt) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.all_ones);
      bins slt_int_min_int_max= binsof(cp_op.slt) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_max);
      bins slt_int_min_int_min= binsof(cp_op.slt) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_min);
      bins slt_int_min_neg_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.neg_rand);
      bins slt_int_min_one= binsof(cp_op.slt) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.one);
      bins slt_int_min_pos_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.pos_rand);
      bins slt_int_min_zero= binsof(cp_op.slt) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.zero);
      bins slt_neg_rand_all_ones= binsof(cp_op.slt) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.all_ones);
      bins slt_neg_rand_int_max= binsof(cp_op.slt) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.int_max);
      bins slt_neg_rand_int_min= binsof(cp_op.slt) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.int_min);
      bins slt_neg_rand_neg_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.neg_rand);
      bins slt_neg_rand_one= binsof(cp_op.slt) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.one);
      bins slt_neg_rand_pos_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.pos_rand);
      bins slt_neg_rand_zero= binsof(cp_op.slt) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.zero);
      bins slt_one_all_ones= binsof(cp_op.slt) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.all_ones);
      bins slt_one_int_max= binsof(cp_op.slt) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_max);
      bins slt_one_int_min= binsof(cp_op.slt) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_min);
      bins slt_one_neg_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.neg_rand);
      bins slt_one_one= binsof(cp_op.slt) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.one);
      bins slt_one_pos_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.pos_rand);
      bins slt_one_zero= binsof(cp_op.slt) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.zero);
      bins slt_pos_rand_all_ones= binsof(cp_op.slt) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.all_ones);
      bins slt_pos_rand_int_max= binsof(cp_op.slt) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.int_max);
      bins slt_pos_rand_int_min= binsof(cp_op.slt) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.int_min);
      bins slt_pos_rand_neg_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.neg_rand);
      bins slt_pos_rand_one= binsof(cp_op.slt) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.one);
      bins slt_pos_rand_pos_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.pos_rand);
      bins slt_pos_rand_zero= binsof(cp_op.slt) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.zero);
      bins slt_zero_all_ones= binsof(cp_op.slt) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.all_ones);
      bins slt_zero_int_max= binsof(cp_op.slt) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_max);
      bins slt_zero_int_min= binsof(cp_op.slt) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_min);
      bins slt_zero_neg_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.neg_rand);
      bins slt_zero_one= binsof(cp_op.slt) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.one);
      bins slt_zero_pos_rand= binsof(cp_op.slt) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.pos_rand);
      bins slt_zero_zero= binsof(cp_op.slt) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.zero);
      bins sltu_all_ones_all_ones= binsof(cp_op.sltu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.all_ones);
      bins sltu_all_ones_int_max= binsof(cp_op.sltu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_max);
      bins sltu_all_ones_int_min= binsof(cp_op.sltu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.int_min);
      bins sltu_all_ones_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.neg_rand);
      bins sltu_all_ones_one= binsof(cp_op.sltu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.one);
      bins sltu_all_ones_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.pos_rand);
      bins sltu_all_ones_zero= binsof(cp_op.sltu) && binsof(cp_rs1_class.all_ones) && binsof(cp_rs2_class.zero);
      bins sltu_int_max_all_ones= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.all_ones);
      bins sltu_int_max_int_max= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_max);
      bins sltu_int_max_int_min= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.int_min);
      bins sltu_int_max_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.neg_rand);
      bins sltu_int_max_one= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.one);
      bins sltu_int_max_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.pos_rand);
      bins sltu_int_max_zero= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_max) && binsof(cp_rs2_class.zero);
      bins sltu_int_min_all_ones= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.all_ones);
      bins sltu_int_min_int_max= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_max);
      bins sltu_int_min_int_min= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.int_min);
      bins sltu_int_min_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.neg_rand);
      bins sltu_int_min_one= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.one);
      bins sltu_int_min_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.pos_rand);
      bins sltu_int_min_zero= binsof(cp_op.sltu) && binsof(cp_rs1_class.int_min) && binsof(cp_rs2_class.zero);
      bins sltu_neg_rand_all_ones= binsof(cp_op.sltu) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.all_ones);
      bins sltu_neg_rand_int_max= binsof(cp_op.sltu) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.int_max);
      bins sltu_neg_rand_int_min= binsof(cp_op.sltu) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.int_min);
      bins sltu_neg_rand_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.neg_rand);
      bins sltu_neg_rand_one= binsof(cp_op.sltu) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.one);
      bins sltu_neg_rand_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.pos_rand);
      bins sltu_neg_rand_zero= binsof(cp_op.sltu) && binsof(cp_rs1_class.neg_rand) && binsof(cp_rs2_class.zero);
      bins sltu_one_all_ones= binsof(cp_op.sltu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.all_ones);
      bins sltu_one_int_max= binsof(cp_op.sltu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_max);
      bins sltu_one_int_min= binsof(cp_op.sltu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.int_min);
      bins sltu_one_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.neg_rand);
      bins sltu_one_one= binsof(cp_op.sltu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.one);
      bins sltu_one_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.pos_rand);
      bins sltu_one_zero= binsof(cp_op.sltu) && binsof(cp_rs1_class.one) && binsof(cp_rs2_class.zero);
      bins sltu_pos_rand_all_ones= binsof(cp_op.sltu) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.all_ones);
      bins sltu_pos_rand_int_max= binsof(cp_op.sltu) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.int_max);
      bins sltu_pos_rand_int_min= binsof(cp_op.sltu) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.int_min);
      bins sltu_pos_rand_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.neg_rand);
      bins sltu_pos_rand_one= binsof(cp_op.sltu) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.one);
      bins sltu_pos_rand_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.pos_rand);
      bins sltu_pos_rand_zero= binsof(cp_op.sltu) && binsof(cp_rs1_class.pos_rand) && binsof(cp_rs2_class.zero);
      bins sltu_zero_all_ones= binsof(cp_op.sltu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.all_ones);
      bins sltu_zero_int_max= binsof(cp_op.sltu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_max);
      bins sltu_zero_int_min= binsof(cp_op.sltu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.int_min);
      bins sltu_zero_neg_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.neg_rand);
      bins sltu_zero_one= binsof(cp_op.sltu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.one);
      bins sltu_zero_pos_rand= binsof(cp_op.sltu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.pos_rand);
      bins sltu_zero_zero= binsof(cp_op.sltu) && binsof(cp_rs1_class.zero) && binsof(cp_rs2_class.zero);
    }
  endgroup

  // CG-BIT-001 (gen_bit_zba_zbb_ops_cg), 51 coverpoint bins, 373 cross bins
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH1ADD = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH2ADD = 1;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH3ADD = 2;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ANDN = 3;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ORN = 4;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_XNOR = 5;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MIN = 6;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MAX = 7;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MINU = 8;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MAXU = 9;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SEXT_B = 10;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SEXT_H = 11;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ZEXT_H = 12;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACK = 13;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACKU = 14;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACKH = 15;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ZERO = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_INT_MIN = 2;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_INT_MAX = 3;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ONE = 4;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_E0000000 = 5;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_BYTE_MSB = 6;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_HALF_MSB = 7;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_POS_RAND = 8;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_NEG_RAND = 9;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ZERO = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_INT_MIN = 2;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_INT_MAX = 3;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ONE = 4;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_POS_RAND = 5;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_NEG_RAND = 6;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_EQ_OPERANDS_NO = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_EQ_OPERANDS_YES = 1;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_RS1_EQ_RS2 = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_ALL_SAME = 1;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_DISTINCT = 2;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RD_X0_NO = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RD_X0_YES = 1;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_SIGN_PAIR_PP = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_SIGN_PAIR_PN = 1;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_SIGN_PAIR_NP = 2;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_SIGN_PAIR_NN = 3;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_ZERO = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_INT_MIN = 2;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_INT_MAX = 3;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_OTHER = 4;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_WRAP_NO = 0;
  localparam int GEN_FC_BIT_ZBA_ZBB_OPS_CP_WRAP_YES = 1;
  covergroup gen_bit_zba_zbb_ops_cg with function sample(int v_cp_op, int v_cp_rs1_class, int v_cp_rs2_class, int v_cp_eq_operands, int v_cp_same_regs, int v_cp_rd_x0, int v_cp_sign_pair, int v_cp_result_class, int v_cp_wrap);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins sh1add= {0}; bins sh2add= {1}; bins sh3add= {2}; bins andn= {3}; bins orn= {4}; bins \xnor = {5}; bins min= {6}; bins max= {7}; bins minu= {8}; bins maxu= {9}; bins sext_b= {10}; bins sext_h= {11}; bins zext_h= {12}; bins pack= {13}; bins packu= {14}; bins packh= {15}; ignore_bins na = {-1}; }
    cp_rs1_class: coverpoint v_cp_rs1_class { bins zero= {0}; bins all_ones= {1}; bins int_min= {2}; bins int_max= {3}; bins one= {4}; bins e0000000= {5}; bins byte_msb= {6}; bins half_msb= {7}; bins pos_rand= {8}; bins neg_rand= {9}; ignore_bins na = {-1}; }
    cp_rs2_class: coverpoint v_cp_rs2_class { bins zero= {0}; bins all_ones= {1}; bins int_min= {2}; bins int_max= {3}; bins one= {4}; bins pos_rand= {5}; bins neg_rand= {6}; ignore_bins na = {-1}; }
    cp_eq_operands: coverpoint v_cp_eq_operands { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_same_regs: coverpoint v_cp_same_regs { bins rs1_eq_rs2= {0}; bins all_same= {1}; bins distinct= {2}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_sign_pair: coverpoint v_cp_sign_pair { bins pp= {0}; bins pn= {1}; bins np= {2}; bins nn= {3}; ignore_bins na = {-1}; }
    cp_result_class: coverpoint v_cp_result_class { bins zero= {0}; bins all_ones= {1}; bins int_min= {2}; bins int_max= {3}; bins other= {4}; ignore_bins na = {-1}; }
    cp_wrap: coverpoint v_cp_wrap { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cr_op_rs1: cross cp_op, cp_rs1_class {
      bins sh1add_all_ones= binsof(cp_op.sh1add) && binsof(cp_rs1_class.all_ones);
      bins sh1add_byte_msb= binsof(cp_op.sh1add) && binsof(cp_rs1_class.byte_msb);
      bins sh1add_e0000000= binsof(cp_op.sh1add) && binsof(cp_rs1_class.e0000000);
      bins sh1add_half_msb= binsof(cp_op.sh1add) && binsof(cp_rs1_class.half_msb);
      bins sh1add_int_max= binsof(cp_op.sh1add) && binsof(cp_rs1_class.int_max);
      bins sh1add_int_min= binsof(cp_op.sh1add) && binsof(cp_rs1_class.int_min);
      bins sh1add_neg_rand= binsof(cp_op.sh1add) && binsof(cp_rs1_class.neg_rand);
      bins sh1add_one= binsof(cp_op.sh1add) && binsof(cp_rs1_class.one);
      bins sh1add_pos_rand= binsof(cp_op.sh1add) && binsof(cp_rs1_class.pos_rand);
      bins sh1add_zero= binsof(cp_op.sh1add) && binsof(cp_rs1_class.zero);
      bins sh2add_all_ones= binsof(cp_op.sh2add) && binsof(cp_rs1_class.all_ones);
      bins sh2add_byte_msb= binsof(cp_op.sh2add) && binsof(cp_rs1_class.byte_msb);
      bins sh2add_e0000000= binsof(cp_op.sh2add) && binsof(cp_rs1_class.e0000000);
      bins sh2add_half_msb= binsof(cp_op.sh2add) && binsof(cp_rs1_class.half_msb);
      bins sh2add_int_max= binsof(cp_op.sh2add) && binsof(cp_rs1_class.int_max);
      bins sh2add_int_min= binsof(cp_op.sh2add) && binsof(cp_rs1_class.int_min);
      bins sh2add_neg_rand= binsof(cp_op.sh2add) && binsof(cp_rs1_class.neg_rand);
      bins sh2add_one= binsof(cp_op.sh2add) && binsof(cp_rs1_class.one);
      bins sh2add_pos_rand= binsof(cp_op.sh2add) && binsof(cp_rs1_class.pos_rand);
      bins sh2add_zero= binsof(cp_op.sh2add) && binsof(cp_rs1_class.zero);
      bins sh3add_all_ones= binsof(cp_op.sh3add) && binsof(cp_rs1_class.all_ones);
      bins sh3add_byte_msb= binsof(cp_op.sh3add) && binsof(cp_rs1_class.byte_msb);
      bins sh3add_e0000000= binsof(cp_op.sh3add) && binsof(cp_rs1_class.e0000000);
      bins sh3add_half_msb= binsof(cp_op.sh3add) && binsof(cp_rs1_class.half_msb);
      bins sh3add_int_max= binsof(cp_op.sh3add) && binsof(cp_rs1_class.int_max);
      bins sh3add_int_min= binsof(cp_op.sh3add) && binsof(cp_rs1_class.int_min);
      bins sh3add_neg_rand= binsof(cp_op.sh3add) && binsof(cp_rs1_class.neg_rand);
      bins sh3add_one= binsof(cp_op.sh3add) && binsof(cp_rs1_class.one);
      bins sh3add_pos_rand= binsof(cp_op.sh3add) && binsof(cp_rs1_class.pos_rand);
      bins sh3add_zero= binsof(cp_op.sh3add) && binsof(cp_rs1_class.zero);
      bins andn_all_ones= binsof(cp_op.andn) && binsof(cp_rs1_class.all_ones);
      bins andn_byte_msb= binsof(cp_op.andn) && binsof(cp_rs1_class.byte_msb);
      bins andn_e0000000= binsof(cp_op.andn) && binsof(cp_rs1_class.e0000000);
      bins andn_half_msb= binsof(cp_op.andn) && binsof(cp_rs1_class.half_msb);
      bins andn_int_max= binsof(cp_op.andn) && binsof(cp_rs1_class.int_max);
      bins andn_int_min= binsof(cp_op.andn) && binsof(cp_rs1_class.int_min);
      bins andn_neg_rand= binsof(cp_op.andn) && binsof(cp_rs1_class.neg_rand);
      bins andn_one= binsof(cp_op.andn) && binsof(cp_rs1_class.one);
      bins andn_pos_rand= binsof(cp_op.andn) && binsof(cp_rs1_class.pos_rand);
      bins andn_zero= binsof(cp_op.andn) && binsof(cp_rs1_class.zero);
      bins orn_all_ones= binsof(cp_op.orn) && binsof(cp_rs1_class.all_ones);
      bins orn_byte_msb= binsof(cp_op.orn) && binsof(cp_rs1_class.byte_msb);
      bins orn_e0000000= binsof(cp_op.orn) && binsof(cp_rs1_class.e0000000);
      bins orn_half_msb= binsof(cp_op.orn) && binsof(cp_rs1_class.half_msb);
      bins orn_int_max= binsof(cp_op.orn) && binsof(cp_rs1_class.int_max);
      bins orn_int_min= binsof(cp_op.orn) && binsof(cp_rs1_class.int_min);
      bins orn_neg_rand= binsof(cp_op.orn) && binsof(cp_rs1_class.neg_rand);
      bins orn_one= binsof(cp_op.orn) && binsof(cp_rs1_class.one);
      bins orn_pos_rand= binsof(cp_op.orn) && binsof(cp_rs1_class.pos_rand);
      bins orn_zero= binsof(cp_op.orn) && binsof(cp_rs1_class.zero);
      bins xnor_all_ones= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.all_ones);
      bins xnor_byte_msb= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.byte_msb);
      bins xnor_e0000000= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.e0000000);
      bins xnor_half_msb= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.half_msb);
      bins xnor_int_max= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.int_max);
      bins xnor_int_min= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.int_min);
      bins xnor_neg_rand= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.neg_rand);
      bins xnor_one= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.one);
      bins xnor_pos_rand= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.pos_rand);
      bins xnor_zero= binsof(cp_op.\xnor ) && binsof(cp_rs1_class.zero);
      bins max_all_ones= binsof(cp_op.max) && binsof(cp_rs1_class.all_ones);
      bins max_byte_msb= binsof(cp_op.max) && binsof(cp_rs1_class.byte_msb);
      bins max_e0000000= binsof(cp_op.max) && binsof(cp_rs1_class.e0000000);
      bins max_half_msb= binsof(cp_op.max) && binsof(cp_rs1_class.half_msb);
      bins max_int_max= binsof(cp_op.max) && binsof(cp_rs1_class.int_max);
      bins max_int_min= binsof(cp_op.max) && binsof(cp_rs1_class.int_min);
      bins max_neg_rand= binsof(cp_op.max) && binsof(cp_rs1_class.neg_rand);
      bins max_one= binsof(cp_op.max) && binsof(cp_rs1_class.one);
      bins max_pos_rand= binsof(cp_op.max) && binsof(cp_rs1_class.pos_rand);
      bins max_zero= binsof(cp_op.max) && binsof(cp_rs1_class.zero);
      bins maxu_all_ones= binsof(cp_op.maxu) && binsof(cp_rs1_class.all_ones);
      bins maxu_byte_msb= binsof(cp_op.maxu) && binsof(cp_rs1_class.byte_msb);
      bins maxu_e0000000= binsof(cp_op.maxu) && binsof(cp_rs1_class.e0000000);
      bins maxu_half_msb= binsof(cp_op.maxu) && binsof(cp_rs1_class.half_msb);
      bins maxu_int_max= binsof(cp_op.maxu) && binsof(cp_rs1_class.int_max);
      bins maxu_int_min= binsof(cp_op.maxu) && binsof(cp_rs1_class.int_min);
      bins maxu_neg_rand= binsof(cp_op.maxu) && binsof(cp_rs1_class.neg_rand);
      bins maxu_one= binsof(cp_op.maxu) && binsof(cp_rs1_class.one);
      bins maxu_pos_rand= binsof(cp_op.maxu) && binsof(cp_rs1_class.pos_rand);
      bins maxu_zero= binsof(cp_op.maxu) && binsof(cp_rs1_class.zero);
      bins min_all_ones= binsof(cp_op.min) && binsof(cp_rs1_class.all_ones);
      bins min_byte_msb= binsof(cp_op.min) && binsof(cp_rs1_class.byte_msb);
      bins min_e0000000= binsof(cp_op.min) && binsof(cp_rs1_class.e0000000);
      bins min_half_msb= binsof(cp_op.min) && binsof(cp_rs1_class.half_msb);
      bins min_int_max= binsof(cp_op.min) && binsof(cp_rs1_class.int_max);
      bins min_int_min= binsof(cp_op.min) && binsof(cp_rs1_class.int_min);
      bins min_neg_rand= binsof(cp_op.min) && binsof(cp_rs1_class.neg_rand);
      bins min_one= binsof(cp_op.min) && binsof(cp_rs1_class.one);
      bins min_pos_rand= binsof(cp_op.min) && binsof(cp_rs1_class.pos_rand);
      bins min_zero= binsof(cp_op.min) && binsof(cp_rs1_class.zero);
      bins minu_all_ones= binsof(cp_op.minu) && binsof(cp_rs1_class.all_ones);
      bins minu_byte_msb= binsof(cp_op.minu) && binsof(cp_rs1_class.byte_msb);
      bins minu_e0000000= binsof(cp_op.minu) && binsof(cp_rs1_class.e0000000);
      bins minu_half_msb= binsof(cp_op.minu) && binsof(cp_rs1_class.half_msb);
      bins minu_int_max= binsof(cp_op.minu) && binsof(cp_rs1_class.int_max);
      bins minu_int_min= binsof(cp_op.minu) && binsof(cp_rs1_class.int_min);
      bins minu_neg_rand= binsof(cp_op.minu) && binsof(cp_rs1_class.neg_rand);
      bins minu_one= binsof(cp_op.minu) && binsof(cp_rs1_class.one);
      bins minu_pos_rand= binsof(cp_op.minu) && binsof(cp_rs1_class.pos_rand);
      bins minu_zero= binsof(cp_op.minu) && binsof(cp_rs1_class.zero);
      bins zext_h_all_ones= binsof(cp_op.zext_h) && binsof(cp_rs1_class.all_ones);
      bins zext_h_byte_msb= binsof(cp_op.zext_h) && binsof(cp_rs1_class.byte_msb);
      bins zext_h_e0000000= binsof(cp_op.zext_h) && binsof(cp_rs1_class.e0000000);
      bins zext_h_half_msb= binsof(cp_op.zext_h) && binsof(cp_rs1_class.half_msb);
      bins zext_h_int_max= binsof(cp_op.zext_h) && binsof(cp_rs1_class.int_max);
      bins zext_h_int_min= binsof(cp_op.zext_h) && binsof(cp_rs1_class.int_min);
      bins zext_h_neg_rand= binsof(cp_op.zext_h) && binsof(cp_rs1_class.neg_rand);
      bins zext_h_one= binsof(cp_op.zext_h) && binsof(cp_rs1_class.one);
      bins zext_h_pos_rand= binsof(cp_op.zext_h) && binsof(cp_rs1_class.pos_rand);
      bins zext_h_zero= binsof(cp_op.zext_h) && binsof(cp_rs1_class.zero);
      bins pack_all_ones= binsof(cp_op.pack) && binsof(cp_rs1_class.all_ones);
      bins pack_byte_msb= binsof(cp_op.pack) && binsof(cp_rs1_class.byte_msb);
      bins pack_e0000000= binsof(cp_op.pack) && binsof(cp_rs1_class.e0000000);
      bins pack_half_msb= binsof(cp_op.pack) && binsof(cp_rs1_class.half_msb);
      bins pack_int_max= binsof(cp_op.pack) && binsof(cp_rs1_class.int_max);
      bins pack_int_min= binsof(cp_op.pack) && binsof(cp_rs1_class.int_min);
      bins pack_neg_rand= binsof(cp_op.pack) && binsof(cp_rs1_class.neg_rand);
      bins pack_one= binsof(cp_op.pack) && binsof(cp_rs1_class.one);
      bins pack_pos_rand= binsof(cp_op.pack) && binsof(cp_rs1_class.pos_rand);
      bins pack_zero= binsof(cp_op.pack) && binsof(cp_rs1_class.zero);
      bins packh_all_ones= binsof(cp_op.packh) && binsof(cp_rs1_class.all_ones);
      bins packh_byte_msb= binsof(cp_op.packh) && binsof(cp_rs1_class.byte_msb);
      bins packh_e0000000= binsof(cp_op.packh) && binsof(cp_rs1_class.e0000000);
      bins packh_half_msb= binsof(cp_op.packh) && binsof(cp_rs1_class.half_msb);
      bins packh_int_max= binsof(cp_op.packh) && binsof(cp_rs1_class.int_max);
      bins packh_int_min= binsof(cp_op.packh) && binsof(cp_rs1_class.int_min);
      bins packh_neg_rand= binsof(cp_op.packh) && binsof(cp_rs1_class.neg_rand);
      bins packh_one= binsof(cp_op.packh) && binsof(cp_rs1_class.one);
      bins packh_pos_rand= binsof(cp_op.packh) && binsof(cp_rs1_class.pos_rand);
      bins packh_zero= binsof(cp_op.packh) && binsof(cp_rs1_class.zero);
      bins packu_all_ones= binsof(cp_op.packu) && binsof(cp_rs1_class.all_ones);
      bins packu_byte_msb= binsof(cp_op.packu) && binsof(cp_rs1_class.byte_msb);
      bins packu_e0000000= binsof(cp_op.packu) && binsof(cp_rs1_class.e0000000);
      bins packu_half_msb= binsof(cp_op.packu) && binsof(cp_rs1_class.half_msb);
      bins packu_int_max= binsof(cp_op.packu) && binsof(cp_rs1_class.int_max);
      bins packu_int_min= binsof(cp_op.packu) && binsof(cp_rs1_class.int_min);
      bins packu_neg_rand= binsof(cp_op.packu) && binsof(cp_rs1_class.neg_rand);
      bins packu_one= binsof(cp_op.packu) && binsof(cp_rs1_class.one);
      bins packu_pos_rand= binsof(cp_op.packu) && binsof(cp_rs1_class.pos_rand);
      bins packu_zero= binsof(cp_op.packu) && binsof(cp_rs1_class.zero);
      bins sext_b_all_ones= binsof(cp_op.sext_b) && binsof(cp_rs1_class.all_ones);
      bins sext_b_byte_msb= binsof(cp_op.sext_b) && binsof(cp_rs1_class.byte_msb);
      bins sext_b_e0000000= binsof(cp_op.sext_b) && binsof(cp_rs1_class.e0000000);
      bins sext_b_half_msb= binsof(cp_op.sext_b) && binsof(cp_rs1_class.half_msb);
      bins sext_b_int_max= binsof(cp_op.sext_b) && binsof(cp_rs1_class.int_max);
      bins sext_b_int_min= binsof(cp_op.sext_b) && binsof(cp_rs1_class.int_min);
      bins sext_b_neg_rand= binsof(cp_op.sext_b) && binsof(cp_rs1_class.neg_rand);
      bins sext_b_one= binsof(cp_op.sext_b) && binsof(cp_rs1_class.one);
      bins sext_b_pos_rand= binsof(cp_op.sext_b) && binsof(cp_rs1_class.pos_rand);
      bins sext_b_zero= binsof(cp_op.sext_b) && binsof(cp_rs1_class.zero);
      bins sext_h_all_ones= binsof(cp_op.sext_h) && binsof(cp_rs1_class.all_ones);
      bins sext_h_byte_msb= binsof(cp_op.sext_h) && binsof(cp_rs1_class.byte_msb);
      bins sext_h_e0000000= binsof(cp_op.sext_h) && binsof(cp_rs1_class.e0000000);
      bins sext_h_half_msb= binsof(cp_op.sext_h) && binsof(cp_rs1_class.half_msb);
      bins sext_h_int_max= binsof(cp_op.sext_h) && binsof(cp_rs1_class.int_max);
      bins sext_h_int_min= binsof(cp_op.sext_h) && binsof(cp_rs1_class.int_min);
      bins sext_h_neg_rand= binsof(cp_op.sext_h) && binsof(cp_rs1_class.neg_rand);
      bins sext_h_one= binsof(cp_op.sext_h) && binsof(cp_rs1_class.one);
      bins sext_h_pos_rand= binsof(cp_op.sext_h) && binsof(cp_rs1_class.pos_rand);
      bins sext_h_zero= binsof(cp_op.sext_h) && binsof(cp_rs1_class.zero);
    }
    cr_op_rs2: cross cp_op, cp_rs2_class {
      bins sh1add_all_ones= binsof(cp_op.sh1add) && binsof(cp_rs2_class.all_ones);
      bins sh1add_int_max= binsof(cp_op.sh1add) && binsof(cp_rs2_class.int_max);
      bins sh1add_int_min= binsof(cp_op.sh1add) && binsof(cp_rs2_class.int_min);
      bins sh1add_neg_rand= binsof(cp_op.sh1add) && binsof(cp_rs2_class.neg_rand);
      bins sh1add_one= binsof(cp_op.sh1add) && binsof(cp_rs2_class.one);
      bins sh1add_pos_rand= binsof(cp_op.sh1add) && binsof(cp_rs2_class.pos_rand);
      bins sh1add_zero= binsof(cp_op.sh1add) && binsof(cp_rs2_class.zero);
      bins sh2add_all_ones= binsof(cp_op.sh2add) && binsof(cp_rs2_class.all_ones);
      bins sh2add_int_max= binsof(cp_op.sh2add) && binsof(cp_rs2_class.int_max);
      bins sh2add_int_min= binsof(cp_op.sh2add) && binsof(cp_rs2_class.int_min);
      bins sh2add_neg_rand= binsof(cp_op.sh2add) && binsof(cp_rs2_class.neg_rand);
      bins sh2add_one= binsof(cp_op.sh2add) && binsof(cp_rs2_class.one);
      bins sh2add_pos_rand= binsof(cp_op.sh2add) && binsof(cp_rs2_class.pos_rand);
      bins sh2add_zero= binsof(cp_op.sh2add) && binsof(cp_rs2_class.zero);
      bins sh3add_all_ones= binsof(cp_op.sh3add) && binsof(cp_rs2_class.all_ones);
      bins sh3add_int_max= binsof(cp_op.sh3add) && binsof(cp_rs2_class.int_max);
      bins sh3add_int_min= binsof(cp_op.sh3add) && binsof(cp_rs2_class.int_min);
      bins sh3add_neg_rand= binsof(cp_op.sh3add) && binsof(cp_rs2_class.neg_rand);
      bins sh3add_one= binsof(cp_op.sh3add) && binsof(cp_rs2_class.one);
      bins sh3add_pos_rand= binsof(cp_op.sh3add) && binsof(cp_rs2_class.pos_rand);
      bins sh3add_zero= binsof(cp_op.sh3add) && binsof(cp_rs2_class.zero);
      bins andn_all_ones= binsof(cp_op.andn) && binsof(cp_rs2_class.all_ones);
      bins andn_int_max= binsof(cp_op.andn) && binsof(cp_rs2_class.int_max);
      bins andn_int_min= binsof(cp_op.andn) && binsof(cp_rs2_class.int_min);
      bins andn_neg_rand= binsof(cp_op.andn) && binsof(cp_rs2_class.neg_rand);
      bins andn_one= binsof(cp_op.andn) && binsof(cp_rs2_class.one);
      bins andn_pos_rand= binsof(cp_op.andn) && binsof(cp_rs2_class.pos_rand);
      bins andn_zero= binsof(cp_op.andn) && binsof(cp_rs2_class.zero);
      bins orn_all_ones= binsof(cp_op.orn) && binsof(cp_rs2_class.all_ones);
      bins orn_int_max= binsof(cp_op.orn) && binsof(cp_rs2_class.int_max);
      bins orn_int_min= binsof(cp_op.orn) && binsof(cp_rs2_class.int_min);
      bins orn_neg_rand= binsof(cp_op.orn) && binsof(cp_rs2_class.neg_rand);
      bins orn_one= binsof(cp_op.orn) && binsof(cp_rs2_class.one);
      bins orn_pos_rand= binsof(cp_op.orn) && binsof(cp_rs2_class.pos_rand);
      bins orn_zero= binsof(cp_op.orn) && binsof(cp_rs2_class.zero);
      bins xnor_all_ones= binsof(cp_op.\xnor ) && binsof(cp_rs2_class.all_ones);
      bins xnor_int_max= binsof(cp_op.\xnor ) && binsof(cp_rs2_class.int_max);
      bins xnor_int_min= binsof(cp_op.\xnor ) && binsof(cp_rs2_class.int_min);
      bins xnor_neg_rand= binsof(cp_op.\xnor ) && binsof(cp_rs2_class.neg_rand);
      bins xnor_one= binsof(cp_op.\xnor ) && binsof(cp_rs2_class.one);
      bins xnor_pos_rand= binsof(cp_op.\xnor ) && binsof(cp_rs2_class.pos_rand);
      bins xnor_zero= binsof(cp_op.\xnor ) && binsof(cp_rs2_class.zero);
      bins max_all_ones= binsof(cp_op.max) && binsof(cp_rs2_class.all_ones);
      bins max_int_max= binsof(cp_op.max) && binsof(cp_rs2_class.int_max);
      bins max_int_min= binsof(cp_op.max) && binsof(cp_rs2_class.int_min);
      bins max_neg_rand= binsof(cp_op.max) && binsof(cp_rs2_class.neg_rand);
      bins max_one= binsof(cp_op.max) && binsof(cp_rs2_class.one);
      bins max_pos_rand= binsof(cp_op.max) && binsof(cp_rs2_class.pos_rand);
      bins max_zero= binsof(cp_op.max) && binsof(cp_rs2_class.zero);
      bins maxu_all_ones= binsof(cp_op.maxu) && binsof(cp_rs2_class.all_ones);
      bins maxu_int_max= binsof(cp_op.maxu) && binsof(cp_rs2_class.int_max);
      bins maxu_int_min= binsof(cp_op.maxu) && binsof(cp_rs2_class.int_min);
      bins maxu_neg_rand= binsof(cp_op.maxu) && binsof(cp_rs2_class.neg_rand);
      bins maxu_one= binsof(cp_op.maxu) && binsof(cp_rs2_class.one);
      bins maxu_pos_rand= binsof(cp_op.maxu) && binsof(cp_rs2_class.pos_rand);
      bins maxu_zero= binsof(cp_op.maxu) && binsof(cp_rs2_class.zero);
      bins min_all_ones= binsof(cp_op.min) && binsof(cp_rs2_class.all_ones);
      bins min_int_max= binsof(cp_op.min) && binsof(cp_rs2_class.int_max);
      bins min_int_min= binsof(cp_op.min) && binsof(cp_rs2_class.int_min);
      bins min_neg_rand= binsof(cp_op.min) && binsof(cp_rs2_class.neg_rand);
      bins min_one= binsof(cp_op.min) && binsof(cp_rs2_class.one);
      bins min_pos_rand= binsof(cp_op.min) && binsof(cp_rs2_class.pos_rand);
      bins min_zero= binsof(cp_op.min) && binsof(cp_rs2_class.zero);
      bins minu_all_ones= binsof(cp_op.minu) && binsof(cp_rs2_class.all_ones);
      bins minu_int_max= binsof(cp_op.minu) && binsof(cp_rs2_class.int_max);
      bins minu_int_min= binsof(cp_op.minu) && binsof(cp_rs2_class.int_min);
      bins minu_neg_rand= binsof(cp_op.minu) && binsof(cp_rs2_class.neg_rand);
      bins minu_one= binsof(cp_op.minu) && binsof(cp_rs2_class.one);
      bins minu_pos_rand= binsof(cp_op.minu) && binsof(cp_rs2_class.pos_rand);
      bins minu_zero= binsof(cp_op.minu) && binsof(cp_rs2_class.zero);
      bins pack_all_ones= binsof(cp_op.pack) && binsof(cp_rs2_class.all_ones);
      bins pack_int_max= binsof(cp_op.pack) && binsof(cp_rs2_class.int_max);
      bins pack_int_min= binsof(cp_op.pack) && binsof(cp_rs2_class.int_min);
      bins pack_neg_rand= binsof(cp_op.pack) && binsof(cp_rs2_class.neg_rand);
      bins pack_one= binsof(cp_op.pack) && binsof(cp_rs2_class.one);
      bins pack_pos_rand= binsof(cp_op.pack) && binsof(cp_rs2_class.pos_rand);
      bins pack_zero= binsof(cp_op.pack) && binsof(cp_rs2_class.zero);
      bins packh_all_ones= binsof(cp_op.packh) && binsof(cp_rs2_class.all_ones);
      bins packh_int_max= binsof(cp_op.packh) && binsof(cp_rs2_class.int_max);
      bins packh_int_min= binsof(cp_op.packh) && binsof(cp_rs2_class.int_min);
      bins packh_neg_rand= binsof(cp_op.packh) && binsof(cp_rs2_class.neg_rand);
      bins packh_one= binsof(cp_op.packh) && binsof(cp_rs2_class.one);
      bins packh_pos_rand= binsof(cp_op.packh) && binsof(cp_rs2_class.pos_rand);
      bins packh_zero= binsof(cp_op.packh) && binsof(cp_rs2_class.zero);
      bins packu_all_ones= binsof(cp_op.packu) && binsof(cp_rs2_class.all_ones);
      bins packu_int_max= binsof(cp_op.packu) && binsof(cp_rs2_class.int_max);
      bins packu_int_min= binsof(cp_op.packu) && binsof(cp_rs2_class.int_min);
      bins packu_neg_rand= binsof(cp_op.packu) && binsof(cp_rs2_class.neg_rand);
      bins packu_one= binsof(cp_op.packu) && binsof(cp_rs2_class.one);
      bins packu_pos_rand= binsof(cp_op.packu) && binsof(cp_rs2_class.pos_rand);
      bins packu_zero= binsof(cp_op.packu) && binsof(cp_rs2_class.zero);
    }
    cr_op_eq: cross cp_op, cp_eq_operands {
      bins andn_no= binsof(cp_op.andn) && binsof(cp_eq_operands.no);
      bins andn_yes= binsof(cp_op.andn) && binsof(cp_eq_operands.yes);
      bins max_no= binsof(cp_op.max) && binsof(cp_eq_operands.no);
      bins max_yes= binsof(cp_op.max) && binsof(cp_eq_operands.yes);
      bins maxu_no= binsof(cp_op.maxu) && binsof(cp_eq_operands.no);
      bins maxu_yes= binsof(cp_op.maxu) && binsof(cp_eq_operands.yes);
      bins min_no= binsof(cp_op.min) && binsof(cp_eq_operands.no);
      bins min_yes= binsof(cp_op.min) && binsof(cp_eq_operands.yes);
      bins minu_no= binsof(cp_op.minu) && binsof(cp_eq_operands.no);
      bins minu_yes= binsof(cp_op.minu) && binsof(cp_eq_operands.yes);
      bins orn_no= binsof(cp_op.orn) && binsof(cp_eq_operands.no);
      bins orn_yes= binsof(cp_op.orn) && binsof(cp_eq_operands.yes);
      bins pack_no= binsof(cp_op.pack) && binsof(cp_eq_operands.no);
      bins pack_yes= binsof(cp_op.pack) && binsof(cp_eq_operands.yes);
      bins packh_no= binsof(cp_op.packh) && binsof(cp_eq_operands.no);
      bins packh_yes= binsof(cp_op.packh) && binsof(cp_eq_operands.yes);
      bins packu_no= binsof(cp_op.packu) && binsof(cp_eq_operands.no);
      bins packu_yes= binsof(cp_op.packu) && binsof(cp_eq_operands.yes);
      bins sh1add_no= binsof(cp_op.sh1add) && binsof(cp_eq_operands.no);
      bins sh1add_yes= binsof(cp_op.sh1add) && binsof(cp_eq_operands.yes);
      bins sh2add_no= binsof(cp_op.sh2add) && binsof(cp_eq_operands.no);
      bins sh2add_yes= binsof(cp_op.sh2add) && binsof(cp_eq_operands.yes);
      bins sh3add_no= binsof(cp_op.sh3add) && binsof(cp_eq_operands.no);
      bins sh3add_yes= binsof(cp_op.sh3add) && binsof(cp_eq_operands.yes);
      bins xnor_no= binsof(cp_op.\xnor ) && binsof(cp_eq_operands.no);
      bins xnor_yes= binsof(cp_op.\xnor ) && binsof(cp_eq_operands.yes);
    }
    cr_op_same: cross cp_op, cp_same_regs {
      bins andn_all_same= binsof(cp_op.andn) && binsof(cp_same_regs.all_same);
      bins andn_distinct= binsof(cp_op.andn) && binsof(cp_same_regs.distinct);
      bins andn_rs1_eq_rs2= binsof(cp_op.andn) && binsof(cp_same_regs.rs1_eq_rs2);
      bins max_all_same= binsof(cp_op.max) && binsof(cp_same_regs.all_same);
      bins max_distinct= binsof(cp_op.max) && binsof(cp_same_regs.distinct);
      bins max_rs1_eq_rs2= binsof(cp_op.max) && binsof(cp_same_regs.rs1_eq_rs2);
      bins maxu_all_same= binsof(cp_op.maxu) && binsof(cp_same_regs.all_same);
      bins maxu_distinct= binsof(cp_op.maxu) && binsof(cp_same_regs.distinct);
      bins maxu_rs1_eq_rs2= binsof(cp_op.maxu) && binsof(cp_same_regs.rs1_eq_rs2);
      bins min_all_same= binsof(cp_op.min) && binsof(cp_same_regs.all_same);
      bins min_distinct= binsof(cp_op.min) && binsof(cp_same_regs.distinct);
      bins min_rs1_eq_rs2= binsof(cp_op.min) && binsof(cp_same_regs.rs1_eq_rs2);
      bins minu_all_same= binsof(cp_op.minu) && binsof(cp_same_regs.all_same);
      bins minu_distinct= binsof(cp_op.minu) && binsof(cp_same_regs.distinct);
      bins minu_rs1_eq_rs2= binsof(cp_op.minu) && binsof(cp_same_regs.rs1_eq_rs2);
      bins orn_all_same= binsof(cp_op.orn) && binsof(cp_same_regs.all_same);
      bins orn_distinct= binsof(cp_op.orn) && binsof(cp_same_regs.distinct);
      bins orn_rs1_eq_rs2= binsof(cp_op.orn) && binsof(cp_same_regs.rs1_eq_rs2);
      bins pack_all_same= binsof(cp_op.pack) && binsof(cp_same_regs.all_same);
      bins pack_distinct= binsof(cp_op.pack) && binsof(cp_same_regs.distinct);
      bins pack_rs1_eq_rs2= binsof(cp_op.pack) && binsof(cp_same_regs.rs1_eq_rs2);
      bins packh_all_same= binsof(cp_op.packh) && binsof(cp_same_regs.all_same);
      bins packh_distinct= binsof(cp_op.packh) && binsof(cp_same_regs.distinct);
      bins packh_rs1_eq_rs2= binsof(cp_op.packh) && binsof(cp_same_regs.rs1_eq_rs2);
      bins packu_all_same= binsof(cp_op.packu) && binsof(cp_same_regs.all_same);
      bins packu_distinct= binsof(cp_op.packu) && binsof(cp_same_regs.distinct);
      bins packu_rs1_eq_rs2= binsof(cp_op.packu) && binsof(cp_same_regs.rs1_eq_rs2);
      bins sext_b_distinct= binsof(cp_op.sext_b) && binsof(cp_same_regs.distinct);
      bins sext_h_distinct= binsof(cp_op.sext_h) && binsof(cp_same_regs.distinct);
      bins sh1add_all_same= binsof(cp_op.sh1add) && binsof(cp_same_regs.all_same);
      bins sh1add_distinct= binsof(cp_op.sh1add) && binsof(cp_same_regs.distinct);
      bins sh1add_rs1_eq_rs2= binsof(cp_op.sh1add) && binsof(cp_same_regs.rs1_eq_rs2);
      bins sh2add_all_same= binsof(cp_op.sh2add) && binsof(cp_same_regs.all_same);
      bins sh2add_distinct= binsof(cp_op.sh2add) && binsof(cp_same_regs.distinct);
      bins sh2add_rs1_eq_rs2= binsof(cp_op.sh2add) && binsof(cp_same_regs.rs1_eq_rs2);
      bins sh3add_all_same= binsof(cp_op.sh3add) && binsof(cp_same_regs.all_same);
      bins sh3add_distinct= binsof(cp_op.sh3add) && binsof(cp_same_regs.distinct);
      bins sh3add_rs1_eq_rs2= binsof(cp_op.sh3add) && binsof(cp_same_regs.rs1_eq_rs2);
      bins xnor_all_same= binsof(cp_op.\xnor ) && binsof(cp_same_regs.all_same);
      bins xnor_distinct= binsof(cp_op.\xnor ) && binsof(cp_same_regs.distinct);
      bins xnor_rs1_eq_rs2= binsof(cp_op.\xnor ) && binsof(cp_same_regs.rs1_eq_rs2);
      bins zext_h_distinct= binsof(cp_op.zext_h) && binsof(cp_same_regs.distinct);
    }
    cr_shadd_wrap: cross cp_op, cp_wrap {
      bins sh1add_no= binsof(cp_op.sh1add) && binsof(cp_wrap.no);
      bins sh1add_yes= binsof(cp_op.sh1add) && binsof(cp_wrap.yes);
      bins sh2add_no= binsof(cp_op.sh2add) && binsof(cp_wrap.no);
      bins sh2add_yes= binsof(cp_op.sh2add) && binsof(cp_wrap.yes);
      bins sh3add_no= binsof(cp_op.sh3add) && binsof(cp_wrap.no);
      bins sh3add_yes= binsof(cp_op.sh3add) && binsof(cp_wrap.yes);
    }
    cr_minmax_sign: cross cp_op, cp_sign_pair {
      bins max_nn= binsof(cp_op.max) && binsof(cp_sign_pair.nn);
      bins max_np= binsof(cp_op.max) && binsof(cp_sign_pair.np);
      bins max_pn= binsof(cp_op.max) && binsof(cp_sign_pair.pn);
      bins max_pp= binsof(cp_op.max) && binsof(cp_sign_pair.pp);
      bins maxu_nn= binsof(cp_op.maxu) && binsof(cp_sign_pair.nn);
      bins maxu_np= binsof(cp_op.maxu) && binsof(cp_sign_pair.np);
      bins maxu_pn= binsof(cp_op.maxu) && binsof(cp_sign_pair.pn);
      bins maxu_pp= binsof(cp_op.maxu) && binsof(cp_sign_pair.pp);
      bins min_nn= binsof(cp_op.min) && binsof(cp_sign_pair.nn);
      bins min_np= binsof(cp_op.min) && binsof(cp_sign_pair.np);
      bins min_pn= binsof(cp_op.min) && binsof(cp_sign_pair.pn);
      bins min_pp= binsof(cp_op.min) && binsof(cp_sign_pair.pp);
      bins minu_nn= binsof(cp_op.minu) && binsof(cp_sign_pair.nn);
      bins minu_np= binsof(cp_op.minu) && binsof(cp_sign_pair.np);
      bins minu_pn= binsof(cp_op.minu) && binsof(cp_sign_pair.pn);
      bins minu_pp= binsof(cp_op.minu) && binsof(cp_sign_pair.pp);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins andn_no= binsof(cp_op.andn) && binsof(cp_rd_x0.no);
      bins andn_yes= binsof(cp_op.andn) && binsof(cp_rd_x0.yes);
      bins max_no= binsof(cp_op.max) && binsof(cp_rd_x0.no);
      bins max_yes= binsof(cp_op.max) && binsof(cp_rd_x0.yes);
      bins maxu_no= binsof(cp_op.maxu) && binsof(cp_rd_x0.no);
      bins maxu_yes= binsof(cp_op.maxu) && binsof(cp_rd_x0.yes);
      bins min_no= binsof(cp_op.min) && binsof(cp_rd_x0.no);
      bins min_yes= binsof(cp_op.min) && binsof(cp_rd_x0.yes);
      bins minu_no= binsof(cp_op.minu) && binsof(cp_rd_x0.no);
      bins minu_yes= binsof(cp_op.minu) && binsof(cp_rd_x0.yes);
      bins orn_no= binsof(cp_op.orn) && binsof(cp_rd_x0.no);
      bins orn_yes= binsof(cp_op.orn) && binsof(cp_rd_x0.yes);
      bins pack_no= binsof(cp_op.pack) && binsof(cp_rd_x0.no);
      bins pack_yes= binsof(cp_op.pack) && binsof(cp_rd_x0.yes);
      bins packh_no= binsof(cp_op.packh) && binsof(cp_rd_x0.no);
      bins packh_yes= binsof(cp_op.packh) && binsof(cp_rd_x0.yes);
      bins packu_no= binsof(cp_op.packu) && binsof(cp_rd_x0.no);
      bins packu_yes= binsof(cp_op.packu) && binsof(cp_rd_x0.yes);
      bins sext_b_no= binsof(cp_op.sext_b) && binsof(cp_rd_x0.no);
      bins sext_b_yes= binsof(cp_op.sext_b) && binsof(cp_rd_x0.yes);
      bins sext_h_no= binsof(cp_op.sext_h) && binsof(cp_rd_x0.no);
      bins sext_h_yes= binsof(cp_op.sext_h) && binsof(cp_rd_x0.yes);
      bins sh1add_no= binsof(cp_op.sh1add) && binsof(cp_rd_x0.no);
      bins sh1add_yes= binsof(cp_op.sh1add) && binsof(cp_rd_x0.yes);
      bins sh2add_no= binsof(cp_op.sh2add) && binsof(cp_rd_x0.no);
      bins sh2add_yes= binsof(cp_op.sh2add) && binsof(cp_rd_x0.yes);
      bins sh3add_no= binsof(cp_op.sh3add) && binsof(cp_rd_x0.no);
      bins sh3add_yes= binsof(cp_op.sh3add) && binsof(cp_rd_x0.yes);
      bins xnor_no= binsof(cp_op.\xnor ) && binsof(cp_rd_x0.no);
      bins xnor_yes= binsof(cp_op.\xnor ) && binsof(cp_rd_x0.yes);
      bins zext_h_no= binsof(cp_op.zext_h) && binsof(cp_rd_x0.no);
      bins zext_h_yes= binsof(cp_op.zext_h) && binsof(cp_rd_x0.yes);
    }
  endgroup

  // CG-ISA-001 (gen_isa_alu_imm_cg), 40 coverpoint bins, 105 cross bins
  localparam int GEN_FC_ISA_ALU_IMM_CP_OP_ADDI = 0;
  localparam int GEN_FC_ISA_ALU_IMM_CP_OP_SLTI = 1;
  localparam int GEN_FC_ISA_ALU_IMM_CP_OP_SLTIU = 2;
  localparam int GEN_FC_ISA_ALU_IMM_CP_OP_XORI = 3;
  localparam int GEN_FC_ISA_ALU_IMM_CP_OP_ORI = 4;
  localparam int GEN_FC_ISA_ALU_IMM_CP_OP_ANDI = 5;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ZERO = 0;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_INT_MIN = 2;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_INT_MAX = 3;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ONE = 4;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_POS_RAND = 5;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_NEG_RAND = 6;
  localparam int GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_ZERO = 0;
  localparam int GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_PLUS1 = 1;
  localparam int GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MINUS1 = 2;
  localparam int GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MAX_POS = 3;
  localparam int GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MIN_NEG = 4;
  localparam int GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_POS_RAND = 5;
  localparam int GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_NEG_RAND = 6;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RD_X0_NO = 0;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RD_X0_YES = 1;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_EQ_RD_NO = 0;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RS1_EQ_RD_YES = 1;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ZERO = 0;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_INT_MIN = 2;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_INT_MAX = 3;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ONE = 4;
  localparam int GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_OTHER = 5;
  localparam int GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_POS_WRAP = 0;
  localparam int GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_NEG_WRAP = 1;
  localparam int GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_NONE = 2;
  localparam int GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_EQ = 0;
  localparam int GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTI_INTMIN_0 = 1;
  localparam int GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTI_0_NEG = 2;
  localparam int GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_IMM_M1 = 3;
  localparam int GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_SEQZ = 4;
  localparam int GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_ONES_M1 = 5;
  localparam int GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_OTHER = 6;
  covergroup gen_isa_alu_imm_cg with function sample(int v_cp_op, int v_cp_rs1_class, int v_cp_imm_class, int v_cp_rd_x0, int v_cp_rs1_eq_rd, int v_cp_result_class, int v_cp_addi_wrap, int v_cp_slt_case);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins addi= {0}; bins slti= {1}; bins sltiu= {2}; bins xori= {3}; bins ori= {4}; bins andi= {5}; ignore_bins na = {-1}; }
    cp_rs1_class: coverpoint v_cp_rs1_class { bins zero= {0}; bins all_ones= {1}; bins int_min= {2}; bins int_max= {3}; bins one= {4}; bins pos_rand= {5}; bins neg_rand= {6}; ignore_bins na = {-1}; }
    cp_imm_class: coverpoint v_cp_imm_class { bins zero= {0}; bins plus1= {1}; bins minus1= {2}; bins max_pos= {3}; bins min_neg= {4}; bins pos_rand= {5}; bins neg_rand= {6}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_rs1_eq_rd: coverpoint v_cp_rs1_eq_rd { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_result_class: coverpoint v_cp_result_class { bins zero= {0}; bins all_ones= {1}; bins int_min= {2}; bins int_max= {3}; bins one= {4}; bins other= {5}; ignore_bins na = {-1}; }
    cp_addi_wrap: coverpoint v_cp_addi_wrap { bins pos_wrap= {0}; bins neg_wrap= {1}; bins none= {2}; ignore_bins na = {-1}; }
    cp_slt_case: coverpoint v_cp_slt_case { bins eq= {0}; bins slti_intmin_0= {1}; bins slti_0_neg= {2}; bins sltiu_imm_m1= {3}; bins sltiu_seqz= {4}; bins sltiu_ones_m1= {5}; bins other= {6}; ignore_bins na = {-1}; }
    cr_op_imm: cross cp_op, cp_imm_class {
      bins addi_max_pos= binsof(cp_op.addi) && binsof(cp_imm_class.max_pos);
      bins addi_min_neg= binsof(cp_op.addi) && binsof(cp_imm_class.min_neg);
      bins addi_minus1= binsof(cp_op.addi) && binsof(cp_imm_class.minus1);
      bins addi_neg_rand= binsof(cp_op.addi) && binsof(cp_imm_class.neg_rand);
      bins addi_plus1= binsof(cp_op.addi) && binsof(cp_imm_class.plus1);
      bins addi_pos_rand= binsof(cp_op.addi) && binsof(cp_imm_class.pos_rand);
      bins addi_zero= binsof(cp_op.addi) && binsof(cp_imm_class.zero);
      bins andi_max_pos= binsof(cp_op.andi) && binsof(cp_imm_class.max_pos);
      bins andi_min_neg= binsof(cp_op.andi) && binsof(cp_imm_class.min_neg);
      bins andi_minus1= binsof(cp_op.andi) && binsof(cp_imm_class.minus1);
      bins andi_neg_rand= binsof(cp_op.andi) && binsof(cp_imm_class.neg_rand);
      bins andi_plus1= binsof(cp_op.andi) && binsof(cp_imm_class.plus1);
      bins andi_pos_rand= binsof(cp_op.andi) && binsof(cp_imm_class.pos_rand);
      bins andi_zero= binsof(cp_op.andi) && binsof(cp_imm_class.zero);
      bins ori_max_pos= binsof(cp_op.ori) && binsof(cp_imm_class.max_pos);
      bins ori_min_neg= binsof(cp_op.ori) && binsof(cp_imm_class.min_neg);
      bins ori_minus1= binsof(cp_op.ori) && binsof(cp_imm_class.minus1);
      bins ori_neg_rand= binsof(cp_op.ori) && binsof(cp_imm_class.neg_rand);
      bins ori_plus1= binsof(cp_op.ori) && binsof(cp_imm_class.plus1);
      bins ori_pos_rand= binsof(cp_op.ori) && binsof(cp_imm_class.pos_rand);
      bins ori_zero= binsof(cp_op.ori) && binsof(cp_imm_class.zero);
      bins slti_max_pos= binsof(cp_op.slti) && binsof(cp_imm_class.max_pos);
      bins slti_min_neg= binsof(cp_op.slti) && binsof(cp_imm_class.min_neg);
      bins slti_minus1= binsof(cp_op.slti) && binsof(cp_imm_class.minus1);
      bins slti_neg_rand= binsof(cp_op.slti) && binsof(cp_imm_class.neg_rand);
      bins slti_plus1= binsof(cp_op.slti) && binsof(cp_imm_class.plus1);
      bins slti_pos_rand= binsof(cp_op.slti) && binsof(cp_imm_class.pos_rand);
      bins slti_zero= binsof(cp_op.slti) && binsof(cp_imm_class.zero);
      bins sltiu_max_pos= binsof(cp_op.sltiu) && binsof(cp_imm_class.max_pos);
      bins sltiu_min_neg= binsof(cp_op.sltiu) && binsof(cp_imm_class.min_neg);
      bins sltiu_minus1= binsof(cp_op.sltiu) && binsof(cp_imm_class.minus1);
      bins sltiu_neg_rand= binsof(cp_op.sltiu) && binsof(cp_imm_class.neg_rand);
      bins sltiu_plus1= binsof(cp_op.sltiu) && binsof(cp_imm_class.plus1);
      bins sltiu_pos_rand= binsof(cp_op.sltiu) && binsof(cp_imm_class.pos_rand);
      bins sltiu_zero= binsof(cp_op.sltiu) && binsof(cp_imm_class.zero);
      bins xori_max_pos= binsof(cp_op.xori) && binsof(cp_imm_class.max_pos);
      bins xori_min_neg= binsof(cp_op.xori) && binsof(cp_imm_class.min_neg);
      bins xori_minus1= binsof(cp_op.xori) && binsof(cp_imm_class.minus1);
      bins xori_neg_rand= binsof(cp_op.xori) && binsof(cp_imm_class.neg_rand);
      bins xori_plus1= binsof(cp_op.xori) && binsof(cp_imm_class.plus1);
      bins xori_pos_rand= binsof(cp_op.xori) && binsof(cp_imm_class.pos_rand);
      bins xori_zero= binsof(cp_op.xori) && binsof(cp_imm_class.zero);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins addi_no= binsof(cp_op.addi) && binsof(cp_rd_x0.no);
      bins addi_yes= binsof(cp_op.addi) && binsof(cp_rd_x0.yes);
      bins andi_no= binsof(cp_op.andi) && binsof(cp_rd_x0.no);
      bins andi_yes= binsof(cp_op.andi) && binsof(cp_rd_x0.yes);
      bins ori_no= binsof(cp_op.ori) && binsof(cp_rd_x0.no);
      bins ori_yes= binsof(cp_op.ori) && binsof(cp_rd_x0.yes);
      bins slti_no= binsof(cp_op.slti) && binsof(cp_rd_x0.no);
      bins slti_yes= binsof(cp_op.slti) && binsof(cp_rd_x0.yes);
      bins sltiu_no= binsof(cp_op.sltiu) && binsof(cp_rd_x0.no);
      bins sltiu_yes= binsof(cp_op.sltiu) && binsof(cp_rd_x0.yes);
      bins xori_no= binsof(cp_op.xori) && binsof(cp_rd_x0.no);
      bins xori_yes= binsof(cp_op.xori) && binsof(cp_rd_x0.yes);
    }
    cr_op_rs1: cross cp_op, cp_rs1_class {
      bins addi_all_ones= binsof(cp_op.addi) && binsof(cp_rs1_class.all_ones);
      bins addi_int_max= binsof(cp_op.addi) && binsof(cp_rs1_class.int_max);
      bins addi_int_min= binsof(cp_op.addi) && binsof(cp_rs1_class.int_min);
      bins addi_neg_rand= binsof(cp_op.addi) && binsof(cp_rs1_class.neg_rand);
      bins addi_one= binsof(cp_op.addi) && binsof(cp_rs1_class.one);
      bins addi_pos_rand= binsof(cp_op.addi) && binsof(cp_rs1_class.pos_rand);
      bins addi_zero= binsof(cp_op.addi) && binsof(cp_rs1_class.zero);
      bins andi_all_ones= binsof(cp_op.andi) && binsof(cp_rs1_class.all_ones);
      bins andi_int_max= binsof(cp_op.andi) && binsof(cp_rs1_class.int_max);
      bins andi_int_min= binsof(cp_op.andi) && binsof(cp_rs1_class.int_min);
      bins andi_neg_rand= binsof(cp_op.andi) && binsof(cp_rs1_class.neg_rand);
      bins andi_one= binsof(cp_op.andi) && binsof(cp_rs1_class.one);
      bins andi_pos_rand= binsof(cp_op.andi) && binsof(cp_rs1_class.pos_rand);
      bins andi_zero= binsof(cp_op.andi) && binsof(cp_rs1_class.zero);
      bins ori_all_ones= binsof(cp_op.ori) && binsof(cp_rs1_class.all_ones);
      bins ori_int_max= binsof(cp_op.ori) && binsof(cp_rs1_class.int_max);
      bins ori_int_min= binsof(cp_op.ori) && binsof(cp_rs1_class.int_min);
      bins ori_neg_rand= binsof(cp_op.ori) && binsof(cp_rs1_class.neg_rand);
      bins ori_one= binsof(cp_op.ori) && binsof(cp_rs1_class.one);
      bins ori_pos_rand= binsof(cp_op.ori) && binsof(cp_rs1_class.pos_rand);
      bins ori_zero= binsof(cp_op.ori) && binsof(cp_rs1_class.zero);
      bins slti_all_ones= binsof(cp_op.slti) && binsof(cp_rs1_class.all_ones);
      bins slti_int_max= binsof(cp_op.slti) && binsof(cp_rs1_class.int_max);
      bins slti_int_min= binsof(cp_op.slti) && binsof(cp_rs1_class.int_min);
      bins slti_neg_rand= binsof(cp_op.slti) && binsof(cp_rs1_class.neg_rand);
      bins slti_one= binsof(cp_op.slti) && binsof(cp_rs1_class.one);
      bins slti_pos_rand= binsof(cp_op.slti) && binsof(cp_rs1_class.pos_rand);
      bins slti_zero= binsof(cp_op.slti) && binsof(cp_rs1_class.zero);
      bins sltiu_all_ones= binsof(cp_op.sltiu) && binsof(cp_rs1_class.all_ones);
      bins sltiu_int_max= binsof(cp_op.sltiu) && binsof(cp_rs1_class.int_max);
      bins sltiu_int_min= binsof(cp_op.sltiu) && binsof(cp_rs1_class.int_min);
      bins sltiu_neg_rand= binsof(cp_op.sltiu) && binsof(cp_rs1_class.neg_rand);
      bins sltiu_one= binsof(cp_op.sltiu) && binsof(cp_rs1_class.one);
      bins sltiu_pos_rand= binsof(cp_op.sltiu) && binsof(cp_rs1_class.pos_rand);
      bins sltiu_zero= binsof(cp_op.sltiu) && binsof(cp_rs1_class.zero);
      bins xori_all_ones= binsof(cp_op.xori) && binsof(cp_rs1_class.all_ones);
      bins xori_int_max= binsof(cp_op.xori) && binsof(cp_rs1_class.int_max);
      bins xori_int_min= binsof(cp_op.xori) && binsof(cp_rs1_class.int_min);
      bins xori_neg_rand= binsof(cp_op.xori) && binsof(cp_rs1_class.neg_rand);
      bins xori_one= binsof(cp_op.xori) && binsof(cp_rs1_class.one);
      bins xori_pos_rand= binsof(cp_op.xori) && binsof(cp_rs1_class.pos_rand);
      bins xori_zero= binsof(cp_op.xori) && binsof(cp_rs1_class.zero);
    }
    cr_slt: cross cp_op, cp_slt_case {
      bins slti_other= binsof(cp_op.slti) && binsof(cp_slt_case.other);
      bins sltiu_other= binsof(cp_op.sltiu) && binsof(cp_slt_case.other);
      bins slti_eq= binsof(cp_op.slti) && binsof(cp_slt_case.eq);
      bins slti_slti_0_neg= binsof(cp_op.slti) && binsof(cp_slt_case.slti_0_neg);
      bins slti_slti_intmin_0= binsof(cp_op.slti) && binsof(cp_slt_case.slti_intmin_0);
      bins sltiu_eq= binsof(cp_op.sltiu) && binsof(cp_slt_case.eq);
      bins sltiu_sltiu_imm_m1= binsof(cp_op.sltiu) && binsof(cp_slt_case.sltiu_imm_m1);
      bins sltiu_sltiu_ones_m1= binsof(cp_op.sltiu) && binsof(cp_slt_case.sltiu_ones_m1);
      bins sltiu_sltiu_seqz= binsof(cp_op.sltiu) && binsof(cp_slt_case.sltiu_seqz);
    }
  endgroup

  // CG-ISA-003 (gen_isa_shift_cg), 31 coverpoint bins, 101 cross bins
  localparam int GEN_FC_ISA_SHIFT_CP_OP_SLLI = 0;
  localparam int GEN_FC_ISA_SHIFT_CP_OP_SRLI = 1;
  localparam int GEN_FC_ISA_SHIFT_CP_OP_SRAI = 2;
  localparam int GEN_FC_ISA_SHIFT_CP_OP_SLL = 3;
  localparam int GEN_FC_ISA_SHIFT_CP_OP_SRL = 4;
  localparam int GEN_FC_ISA_SHIFT_CP_OP_SRA = 5;
  localparam int GEN_FC_ISA_SHIFT_CP_SHAMT_S0 = 0;
  localparam int GEN_FC_ISA_SHIFT_CP_SHAMT_S1 = 1;
  localparam int GEN_FC_ISA_SHIFT_CP_SHAMT_MID = 2;
  localparam int GEN_FC_ISA_SHIFT_CP_SHAMT_S31 = 3;
  localparam int GEN_FC_ISA_SHIFT_CP_RS2_UPPER_ZERO = 0;
  localparam int GEN_FC_ISA_SHIFT_CP_RS2_UPPER_IS32 = 1;
  localparam int GEN_FC_ISA_SHIFT_CP_RS2_UPPER_IS33 = 2;
  localparam int GEN_FC_ISA_SHIFT_CP_RS2_UPPER_ALL_ONES = 3;
  localparam int GEN_FC_ISA_SHIFT_CP_RS2_UPPER_MSB_ONLY = 4;
  localparam int GEN_FC_ISA_SHIFT_CP_RS2_UPPER_FFFFFFE0 = 5;
  localparam int GEN_FC_ISA_SHIFT_CP_RS2_UPPER_OTHER_NONZERO = 6;
  localparam int GEN_FC_ISA_SHIFT_CP_OPERAND_ZERO = 0;
  localparam int GEN_FC_ISA_SHIFT_CP_OPERAND_ALL_ONES = 1;
  localparam int GEN_FC_ISA_SHIFT_CP_OPERAND_MSB_ONLY = 2;
  localparam int GEN_FC_ISA_SHIFT_CP_OPERAND_LSB_ONLY = 3;
  localparam int GEN_FC_ISA_SHIFT_CP_OPERAND_NEG_RAND = 4;
  localparam int GEN_FC_ISA_SHIFT_CP_OPERAND_POS_RAND = 5;
  localparam int GEN_FC_ISA_SHIFT_CP_RD_X0_NO = 0;
  localparam int GEN_FC_ISA_SHIFT_CP_RD_X0_YES = 1;
  localparam int GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ZERO = 0;
  localparam int GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ALL_ONES = 1;
  localparam int GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_MSB_ONLY = 2;
  localparam int GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ONE = 3;
  localparam int GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_C0000000 = 4;
  localparam int GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_OTHER = 5;
  covergroup gen_isa_shift_cg with function sample(int v_cp_op, int v_cp_shamt, int v_cp_rs2_upper, int v_cp_operand, int v_cp_rd_x0, int v_cp_result_class);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins slli= {0}; bins srli= {1}; bins srai= {2}; bins sll= {3}; bins srl= {4}; bins sra= {5}; ignore_bins na = {-1}; }
    cp_shamt: coverpoint v_cp_shamt { bins s0= {0}; bins s1= {1}; bins mid= {2}; bins s31= {3}; ignore_bins na = {-1}; }
    cp_rs2_upper: coverpoint v_cp_rs2_upper { bins zero= {0}; bins is32= {1}; bins is33= {2}; bins all_ones= {3}; bins msb_only= {4}; bins ffffffe0= {5}; bins other_nonzero= {6}; ignore_bins na = {-1}; }
    cp_operand: coverpoint v_cp_operand { bins zero= {0}; bins all_ones= {1}; bins msb_only= {2}; bins lsb_only= {3}; bins neg_rand= {4}; bins pos_rand= {5}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_result_class: coverpoint v_cp_result_class { bins zero= {0}; bins all_ones= {1}; bins msb_only= {2}; bins one= {3}; bins c0000000= {4}; bins other= {5}; ignore_bins na = {-1}; }
    cr_op_operand: cross cp_op, cp_operand {
      bins slli_all_ones= binsof(cp_op.slli) && binsof(cp_operand.all_ones);
      bins slli_lsb_only= binsof(cp_op.slli) && binsof(cp_operand.lsb_only);
      bins slli_msb_only= binsof(cp_op.slli) && binsof(cp_operand.msb_only);
      bins slli_neg_rand= binsof(cp_op.slli) && binsof(cp_operand.neg_rand);
      bins slli_pos_rand= binsof(cp_op.slli) && binsof(cp_operand.pos_rand);
      bins slli_zero= binsof(cp_op.slli) && binsof(cp_operand.zero);
      bins srai_all_ones= binsof(cp_op.srai) && binsof(cp_operand.all_ones);
      bins srai_lsb_only= binsof(cp_op.srai) && binsof(cp_operand.lsb_only);
      bins srai_msb_only= binsof(cp_op.srai) && binsof(cp_operand.msb_only);
      bins srai_neg_rand= binsof(cp_op.srai) && binsof(cp_operand.neg_rand);
      bins srai_pos_rand= binsof(cp_op.srai) && binsof(cp_operand.pos_rand);
      bins srai_zero= binsof(cp_op.srai) && binsof(cp_operand.zero);
      bins srli_all_ones= binsof(cp_op.srli) && binsof(cp_operand.all_ones);
      bins srli_lsb_only= binsof(cp_op.srli) && binsof(cp_operand.lsb_only);
      bins srli_msb_only= binsof(cp_op.srli) && binsof(cp_operand.msb_only);
      bins srli_neg_rand= binsof(cp_op.srli) && binsof(cp_operand.neg_rand);
      bins srli_pos_rand= binsof(cp_op.srli) && binsof(cp_operand.pos_rand);
      bins srli_zero= binsof(cp_op.srli) && binsof(cp_operand.zero);
      bins sll_all_ones= binsof(cp_op.sll) && binsof(cp_operand.all_ones);
      bins sll_lsb_only= binsof(cp_op.sll) && binsof(cp_operand.lsb_only);
      bins sll_msb_only= binsof(cp_op.sll) && binsof(cp_operand.msb_only);
      bins sll_neg_rand= binsof(cp_op.sll) && binsof(cp_operand.neg_rand);
      bins sll_pos_rand= binsof(cp_op.sll) && binsof(cp_operand.pos_rand);
      bins sll_zero= binsof(cp_op.sll) && binsof(cp_operand.zero);
      bins sra_all_ones= binsof(cp_op.sra) && binsof(cp_operand.all_ones);
      bins sra_lsb_only= binsof(cp_op.sra) && binsof(cp_operand.lsb_only);
      bins sra_msb_only= binsof(cp_op.sra) && binsof(cp_operand.msb_only);
      bins sra_neg_rand= binsof(cp_op.sra) && binsof(cp_operand.neg_rand);
      bins sra_pos_rand= binsof(cp_op.sra) && binsof(cp_operand.pos_rand);
      bins sra_zero= binsof(cp_op.sra) && binsof(cp_operand.zero);
      bins srl_all_ones= binsof(cp_op.srl) && binsof(cp_operand.all_ones);
      bins srl_lsb_only= binsof(cp_op.srl) && binsof(cp_operand.lsb_only);
      bins srl_msb_only= binsof(cp_op.srl) && binsof(cp_operand.msb_only);
      bins srl_neg_rand= binsof(cp_op.srl) && binsof(cp_operand.neg_rand);
      bins srl_pos_rand= binsof(cp_op.srl) && binsof(cp_operand.pos_rand);
      bins srl_zero= binsof(cp_op.srl) && binsof(cp_operand.zero);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins slli_no= binsof(cp_op.slli) && binsof(cp_rd_x0.no);
      bins slli_yes= binsof(cp_op.slli) && binsof(cp_rd_x0.yes);
      bins srai_no= binsof(cp_op.srai) && binsof(cp_rd_x0.no);
      bins srai_yes= binsof(cp_op.srai) && binsof(cp_rd_x0.yes);
      bins srli_no= binsof(cp_op.srli) && binsof(cp_rd_x0.no);
      bins srli_yes= binsof(cp_op.srli) && binsof(cp_rd_x0.yes);
      bins sll_no= binsof(cp_op.sll) && binsof(cp_rd_x0.no);
      bins sll_yes= binsof(cp_op.sll) && binsof(cp_rd_x0.yes);
      bins sra_no= binsof(cp_op.sra) && binsof(cp_rd_x0.no);
      bins sra_yes= binsof(cp_op.sra) && binsof(cp_rd_x0.yes);
      bins srl_no= binsof(cp_op.srl) && binsof(cp_rd_x0.no);
      bins srl_yes= binsof(cp_op.srl) && binsof(cp_rd_x0.yes);
    }
    cr_op_shamt: cross cp_op, cp_shamt {
      bins slli_mid= binsof(cp_op.slli) && binsof(cp_shamt.mid);
      bins slli_s0= binsof(cp_op.slli) && binsof(cp_shamt.s0);
      bins slli_s1= binsof(cp_op.slli) && binsof(cp_shamt.s1);
      bins slli_s31= binsof(cp_op.slli) && binsof(cp_shamt.s31);
      bins srai_mid= binsof(cp_op.srai) && binsof(cp_shamt.mid);
      bins srai_s0= binsof(cp_op.srai) && binsof(cp_shamt.s0);
      bins srai_s1= binsof(cp_op.srai) && binsof(cp_shamt.s1);
      bins srai_s31= binsof(cp_op.srai) && binsof(cp_shamt.s31);
      bins srli_mid= binsof(cp_op.srli) && binsof(cp_shamt.mid);
      bins srli_s0= binsof(cp_op.srli) && binsof(cp_shamt.s0);
      bins srli_s1= binsof(cp_op.srli) && binsof(cp_shamt.s1);
      bins srli_s31= binsof(cp_op.srli) && binsof(cp_shamt.s31);
      bins sll_mid= binsof(cp_op.sll) && binsof(cp_shamt.mid);
      bins sll_s0= binsof(cp_op.sll) && binsof(cp_shamt.s0);
      bins sll_s1= binsof(cp_op.sll) && binsof(cp_shamt.s1);
      bins sll_s31= binsof(cp_op.sll) && binsof(cp_shamt.s31);
      bins sra_mid= binsof(cp_op.sra) && binsof(cp_shamt.mid);
      bins sra_s0= binsof(cp_op.sra) && binsof(cp_shamt.s0);
      bins sra_s1= binsof(cp_op.sra) && binsof(cp_shamt.s1);
      bins sra_s31= binsof(cp_op.sra) && binsof(cp_shamt.s31);
      bins srl_mid= binsof(cp_op.srl) && binsof(cp_shamt.mid);
      bins srl_s0= binsof(cp_op.srl) && binsof(cp_shamt.s0);
      bins srl_s1= binsof(cp_op.srl) && binsof(cp_shamt.s1);
      bins srl_s31= binsof(cp_op.srl) && binsof(cp_shamt.s31);
    }
    cr_sra_sign: cross cp_op, cp_operand, cp_shamt {
      bins slli_lsb_31= binsof(cp_op.slli) && binsof(cp_operand.lsb_only) && binsof(cp_shamt.s31);
      bins sra_msb_1= binsof(cp_op.sra) && binsof(cp_operand.msb_only) && binsof(cp_shamt.s1);
      bins sra_neg_31= binsof(cp_op.sra) && binsof(cp_operand.neg_rand) && binsof(cp_shamt.s31);
      bins sra_pos_31= binsof(cp_op.sra) && binsof(cp_operand.pos_rand) && binsof(cp_shamt.s31);
      bins srai_msb_1= binsof(cp_op.srai) && binsof(cp_operand.msb_only) && binsof(cp_shamt.s1);
      bins srai_neg_31= binsof(cp_op.srai) && binsof(cp_operand.neg_rand) && binsof(cp_shamt.s31);
      bins srai_pos_31= binsof(cp_op.srai) && binsof(cp_operand.pos_rand) && binsof(cp_shamt.s31);
      bins srli_msb_31= binsof(cp_op.srli) && binsof(cp_operand.msb_only) && binsof(cp_shamt.s31);
    }
    cr_reg_upper: cross cp_op, cp_rs2_upper {
      bins sll_zero= binsof(cp_op.sll) && binsof(cp_rs2_upper.zero);
      bins sra_zero= binsof(cp_op.sra) && binsof(cp_rs2_upper.zero);
      bins srl_zero= binsof(cp_op.srl) && binsof(cp_rs2_upper.zero);
      bins sll_all_ones= binsof(cp_op.sll) && binsof(cp_rs2_upper.all_ones);
      bins sll_ffffffe0= binsof(cp_op.sll) && binsof(cp_rs2_upper.ffffffe0);
      bins sll_is32= binsof(cp_op.sll) && binsof(cp_rs2_upper.is32);
      bins sll_is33= binsof(cp_op.sll) && binsof(cp_rs2_upper.is33);
      bins sll_msb_only= binsof(cp_op.sll) && binsof(cp_rs2_upper.msb_only);
      bins sll_other_nonzero= binsof(cp_op.sll) && binsof(cp_rs2_upper.other_nonzero);
      bins sra_all_ones= binsof(cp_op.sra) && binsof(cp_rs2_upper.all_ones);
      bins sra_ffffffe0= binsof(cp_op.sra) && binsof(cp_rs2_upper.ffffffe0);
      bins sra_is32= binsof(cp_op.sra) && binsof(cp_rs2_upper.is32);
      bins sra_is33= binsof(cp_op.sra) && binsof(cp_rs2_upper.is33);
      bins sra_msb_only= binsof(cp_op.sra) && binsof(cp_rs2_upper.msb_only);
      bins sra_other_nonzero= binsof(cp_op.sra) && binsof(cp_rs2_upper.other_nonzero);
      bins srl_all_ones= binsof(cp_op.srl) && binsof(cp_rs2_upper.all_ones);
      bins srl_ffffffe0= binsof(cp_op.srl) && binsof(cp_rs2_upper.ffffffe0);
      bins srl_is32= binsof(cp_op.srl) && binsof(cp_rs2_upper.is32);
      bins srl_is33= binsof(cp_op.srl) && binsof(cp_rs2_upper.is33);
      bins srl_msb_only= binsof(cp_op.srl) && binsof(cp_rs2_upper.msb_only);
      bins srl_other_nonzero= binsof(cp_op.srl) && binsof(cp_rs2_upper.other_nonzero);
    }
  endgroup

  // CG-BIT-002 (gen_bit_count_cg), 52 coverpoint bins, 147 cross bins
  localparam int GEN_FC_BIT_COUNT_CP_OP_CLZ = 0;
  localparam int GEN_FC_BIT_COUNT_CP_OP_CTZ = 1;
  localparam int GEN_FC_BIT_COUNT_CP_OP_CPOP = 2;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_ZERO = 0;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_ALL_ONES = 1;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_MSB_ONLY = 2;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_LSB_ONLY = 3;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_SINGLE_OTHER = 4;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_ALT_5 = 5;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_ALT_A = 6;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_INT_MAX = 7;
  localparam int GEN_FC_BIT_COUNT_CP_OPERAND_RAND = 8;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P0 = 0;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P1 = 1;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P2 = 2;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P3 = 3;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P4 = 4;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P5 = 5;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P6 = 6;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P7 = 7;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P8 = 8;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P9 = 9;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P10 = 10;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P11 = 11;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P12 = 12;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P13 = 13;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P14 = 14;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P15 = 15;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P16 = 16;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P17 = 17;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P18 = 18;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P19 = 19;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P20 = 20;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P21 = 21;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P22 = 22;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P23 = 23;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P24 = 24;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P25 = 25;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P26 = 26;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P27 = 27;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P28 = 28;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P29 = 29;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P30 = 30;
  localparam int GEN_FC_BIT_COUNT_CP_SINGLE_POS_P31 = 31;
  localparam int GEN_FC_BIT_COUNT_CP_RESULT_R0 = 0;
  localparam int GEN_FC_BIT_COUNT_CP_RESULT_R1 = 1;
  localparam int GEN_FC_BIT_COUNT_CP_RESULT_R16 = 2;
  localparam int GEN_FC_BIT_COUNT_CP_RESULT_R31 = 3;
  localparam int GEN_FC_BIT_COUNT_CP_RESULT_R32 = 4;
  localparam int GEN_FC_BIT_COUNT_CP_RESULT_OTHER = 5;
  localparam int GEN_FC_BIT_COUNT_CP_RD_X0_NO = 0;
  localparam int GEN_FC_BIT_COUNT_CP_RD_X0_YES = 1;
  covergroup gen_bit_count_cg with function sample(int v_cp_op, int v_cp_operand, int v_cp_single_pos, int v_cp_result, int v_cp_rd_x0);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins clz= {0}; bins ctz= {1}; bins cpop= {2}; ignore_bins na = {-1}; }
    cp_operand: coverpoint v_cp_operand { bins zero= {0}; bins all_ones= {1}; bins msb_only= {2}; bins lsb_only= {3}; bins single_other= {4}; bins alt_5= {5}; bins alt_a= {6}; bins int_max= {7}; bins \rand = {8}; ignore_bins na = {-1}; }
    cp_single_pos: coverpoint v_cp_single_pos { bins p0= {0}; bins p1= {1}; bins p2= {2}; bins p3= {3}; bins p4= {4}; bins p5= {5}; bins p6= {6}; bins p7= {7}; bins p8= {8}; bins p9= {9}; bins p10= {10}; bins p11= {11}; bins p12= {12}; bins p13= {13}; bins p14= {14}; bins p15= {15}; bins p16= {16}; bins p17= {17}; bins p18= {18}; bins p19= {19}; bins p20= {20}; bins p21= {21}; bins p22= {22}; bins p23= {23}; bins p24= {24}; bins p25= {25}; bins p26= {26}; bins p27= {27}; bins p28= {28}; bins p29= {29}; bins p30= {30}; bins p31= {31}; ignore_bins na = {-1}; }
    cp_result: coverpoint v_cp_result { bins r0= {0}; bins r1= {1}; bins r16= {2}; bins r31= {3}; bins r32= {4}; bins other= {5}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cr_op_operand: cross cp_op, cp_operand {
      bins clz_all_ones= binsof(cp_op.clz) && binsof(cp_operand.all_ones);
      bins clz_alt_5= binsof(cp_op.clz) && binsof(cp_operand.alt_5);
      bins clz_alt_a= binsof(cp_op.clz) && binsof(cp_operand.alt_a);
      bins clz_int_max= binsof(cp_op.clz) && binsof(cp_operand.int_max);
      bins clz_lsb_only= binsof(cp_op.clz) && binsof(cp_operand.lsb_only);
      bins clz_msb_only= binsof(cp_op.clz) && binsof(cp_operand.msb_only);
      bins clz_rand= binsof(cp_op.clz) && binsof(cp_operand.\rand );
      bins clz_single_other= binsof(cp_op.clz) && binsof(cp_operand.single_other);
      bins clz_zero= binsof(cp_op.clz) && binsof(cp_operand.zero);
      bins cpop_all_ones= binsof(cp_op.cpop) && binsof(cp_operand.all_ones);
      bins cpop_alt_5= binsof(cp_op.cpop) && binsof(cp_operand.alt_5);
      bins cpop_alt_a= binsof(cp_op.cpop) && binsof(cp_operand.alt_a);
      bins cpop_int_max= binsof(cp_op.cpop) && binsof(cp_operand.int_max);
      bins cpop_lsb_only= binsof(cp_op.cpop) && binsof(cp_operand.lsb_only);
      bins cpop_msb_only= binsof(cp_op.cpop) && binsof(cp_operand.msb_only);
      bins cpop_rand= binsof(cp_op.cpop) && binsof(cp_operand.\rand );
      bins cpop_single_other= binsof(cp_op.cpop) && binsof(cp_operand.single_other);
      bins cpop_zero= binsof(cp_op.cpop) && binsof(cp_operand.zero);
      bins ctz_all_ones= binsof(cp_op.ctz) && binsof(cp_operand.all_ones);
      bins ctz_alt_5= binsof(cp_op.ctz) && binsof(cp_operand.alt_5);
      bins ctz_alt_a= binsof(cp_op.ctz) && binsof(cp_operand.alt_a);
      bins ctz_int_max= binsof(cp_op.ctz) && binsof(cp_operand.int_max);
      bins ctz_lsb_only= binsof(cp_op.ctz) && binsof(cp_operand.lsb_only);
      bins ctz_msb_only= binsof(cp_op.ctz) && binsof(cp_operand.msb_only);
      bins ctz_rand= binsof(cp_op.ctz) && binsof(cp_operand.\rand );
      bins ctz_single_other= binsof(cp_op.ctz) && binsof(cp_operand.single_other);
      bins ctz_zero= binsof(cp_op.ctz) && binsof(cp_operand.zero);
    }
    cr_op_result: cross cp_op, cp_result {
      bins clz_other= binsof(cp_op.clz) && binsof(cp_result.other);
      bins clz_r1= binsof(cp_op.clz) && binsof(cp_result.r1);
      bins clz_r16= binsof(cp_op.clz) && binsof(cp_result.r16);
      bins cpop_other= binsof(cp_op.cpop) && binsof(cp_result.other);
      bins cpop_r1= binsof(cp_op.cpop) && binsof(cp_result.r1);
      bins cpop_r16= binsof(cp_op.cpop) && binsof(cp_result.r16);
      bins ctz_other= binsof(cp_op.ctz) && binsof(cp_result.other);
      bins ctz_r1= binsof(cp_op.ctz) && binsof(cp_result.r1);
      bins ctz_r16= binsof(cp_op.ctz) && binsof(cp_result.r16);
      bins clz_r0= binsof(cp_op.clz) && binsof(cp_result.r0);
      bins clz_r31= binsof(cp_op.clz) && binsof(cp_result.r31);
      bins clz_r32= binsof(cp_op.clz) && binsof(cp_result.r32);
      bins cpop_r0= binsof(cp_op.cpop) && binsof(cp_result.r0);
      bins cpop_r31= binsof(cp_op.cpop) && binsof(cp_result.r31);
      bins cpop_r32= binsof(cp_op.cpop) && binsof(cp_result.r32);
      bins ctz_r0= binsof(cp_op.ctz) && binsof(cp_result.r0);
      bins ctz_r31= binsof(cp_op.ctz) && binsof(cp_result.r31);
      bins ctz_r32= binsof(cp_op.ctz) && binsof(cp_result.r32);
    }
    cr_op_single: cross cp_op, cp_single_pos {
      bins clz_p0= binsof(cp_op.clz) && binsof(cp_single_pos.p0);
      bins clz_p1= binsof(cp_op.clz) && binsof(cp_single_pos.p1);
      bins clz_p10= binsof(cp_op.clz) && binsof(cp_single_pos.p10);
      bins clz_p11= binsof(cp_op.clz) && binsof(cp_single_pos.p11);
      bins clz_p12= binsof(cp_op.clz) && binsof(cp_single_pos.p12);
      bins clz_p13= binsof(cp_op.clz) && binsof(cp_single_pos.p13);
      bins clz_p14= binsof(cp_op.clz) && binsof(cp_single_pos.p14);
      bins clz_p15= binsof(cp_op.clz) && binsof(cp_single_pos.p15);
      bins clz_p16= binsof(cp_op.clz) && binsof(cp_single_pos.p16);
      bins clz_p17= binsof(cp_op.clz) && binsof(cp_single_pos.p17);
      bins clz_p18= binsof(cp_op.clz) && binsof(cp_single_pos.p18);
      bins clz_p19= binsof(cp_op.clz) && binsof(cp_single_pos.p19);
      bins clz_p2= binsof(cp_op.clz) && binsof(cp_single_pos.p2);
      bins clz_p20= binsof(cp_op.clz) && binsof(cp_single_pos.p20);
      bins clz_p21= binsof(cp_op.clz) && binsof(cp_single_pos.p21);
      bins clz_p22= binsof(cp_op.clz) && binsof(cp_single_pos.p22);
      bins clz_p23= binsof(cp_op.clz) && binsof(cp_single_pos.p23);
      bins clz_p24= binsof(cp_op.clz) && binsof(cp_single_pos.p24);
      bins clz_p25= binsof(cp_op.clz) && binsof(cp_single_pos.p25);
      bins clz_p26= binsof(cp_op.clz) && binsof(cp_single_pos.p26);
      bins clz_p27= binsof(cp_op.clz) && binsof(cp_single_pos.p27);
      bins clz_p28= binsof(cp_op.clz) && binsof(cp_single_pos.p28);
      bins clz_p29= binsof(cp_op.clz) && binsof(cp_single_pos.p29);
      bins clz_p3= binsof(cp_op.clz) && binsof(cp_single_pos.p3);
      bins clz_p30= binsof(cp_op.clz) && binsof(cp_single_pos.p30);
      bins clz_p31= binsof(cp_op.clz) && binsof(cp_single_pos.p31);
      bins clz_p4= binsof(cp_op.clz) && binsof(cp_single_pos.p4);
      bins clz_p5= binsof(cp_op.clz) && binsof(cp_single_pos.p5);
      bins clz_p6= binsof(cp_op.clz) && binsof(cp_single_pos.p6);
      bins clz_p7= binsof(cp_op.clz) && binsof(cp_single_pos.p7);
      bins clz_p8= binsof(cp_op.clz) && binsof(cp_single_pos.p8);
      bins clz_p9= binsof(cp_op.clz) && binsof(cp_single_pos.p9);
      bins cpop_p0= binsof(cp_op.cpop) && binsof(cp_single_pos.p0);
      bins cpop_p1= binsof(cp_op.cpop) && binsof(cp_single_pos.p1);
      bins cpop_p10= binsof(cp_op.cpop) && binsof(cp_single_pos.p10);
      bins cpop_p11= binsof(cp_op.cpop) && binsof(cp_single_pos.p11);
      bins cpop_p12= binsof(cp_op.cpop) && binsof(cp_single_pos.p12);
      bins cpop_p13= binsof(cp_op.cpop) && binsof(cp_single_pos.p13);
      bins cpop_p14= binsof(cp_op.cpop) && binsof(cp_single_pos.p14);
      bins cpop_p15= binsof(cp_op.cpop) && binsof(cp_single_pos.p15);
      bins cpop_p16= binsof(cp_op.cpop) && binsof(cp_single_pos.p16);
      bins cpop_p17= binsof(cp_op.cpop) && binsof(cp_single_pos.p17);
      bins cpop_p18= binsof(cp_op.cpop) && binsof(cp_single_pos.p18);
      bins cpop_p19= binsof(cp_op.cpop) && binsof(cp_single_pos.p19);
      bins cpop_p2= binsof(cp_op.cpop) && binsof(cp_single_pos.p2);
      bins cpop_p20= binsof(cp_op.cpop) && binsof(cp_single_pos.p20);
      bins cpop_p21= binsof(cp_op.cpop) && binsof(cp_single_pos.p21);
      bins cpop_p22= binsof(cp_op.cpop) && binsof(cp_single_pos.p22);
      bins cpop_p23= binsof(cp_op.cpop) && binsof(cp_single_pos.p23);
      bins cpop_p24= binsof(cp_op.cpop) && binsof(cp_single_pos.p24);
      bins cpop_p25= binsof(cp_op.cpop) && binsof(cp_single_pos.p25);
      bins cpop_p26= binsof(cp_op.cpop) && binsof(cp_single_pos.p26);
      bins cpop_p27= binsof(cp_op.cpop) && binsof(cp_single_pos.p27);
      bins cpop_p28= binsof(cp_op.cpop) && binsof(cp_single_pos.p28);
      bins cpop_p29= binsof(cp_op.cpop) && binsof(cp_single_pos.p29);
      bins cpop_p3= binsof(cp_op.cpop) && binsof(cp_single_pos.p3);
      bins cpop_p30= binsof(cp_op.cpop) && binsof(cp_single_pos.p30);
      bins cpop_p31= binsof(cp_op.cpop) && binsof(cp_single_pos.p31);
      bins cpop_p4= binsof(cp_op.cpop) && binsof(cp_single_pos.p4);
      bins cpop_p5= binsof(cp_op.cpop) && binsof(cp_single_pos.p5);
      bins cpop_p6= binsof(cp_op.cpop) && binsof(cp_single_pos.p6);
      bins cpop_p7= binsof(cp_op.cpop) && binsof(cp_single_pos.p7);
      bins cpop_p8= binsof(cp_op.cpop) && binsof(cp_single_pos.p8);
      bins cpop_p9= binsof(cp_op.cpop) && binsof(cp_single_pos.p9);
      bins ctz_p0= binsof(cp_op.ctz) && binsof(cp_single_pos.p0);
      bins ctz_p1= binsof(cp_op.ctz) && binsof(cp_single_pos.p1);
      bins ctz_p10= binsof(cp_op.ctz) && binsof(cp_single_pos.p10);
      bins ctz_p11= binsof(cp_op.ctz) && binsof(cp_single_pos.p11);
      bins ctz_p12= binsof(cp_op.ctz) && binsof(cp_single_pos.p12);
      bins ctz_p13= binsof(cp_op.ctz) && binsof(cp_single_pos.p13);
      bins ctz_p14= binsof(cp_op.ctz) && binsof(cp_single_pos.p14);
      bins ctz_p15= binsof(cp_op.ctz) && binsof(cp_single_pos.p15);
      bins ctz_p16= binsof(cp_op.ctz) && binsof(cp_single_pos.p16);
      bins ctz_p17= binsof(cp_op.ctz) && binsof(cp_single_pos.p17);
      bins ctz_p18= binsof(cp_op.ctz) && binsof(cp_single_pos.p18);
      bins ctz_p19= binsof(cp_op.ctz) && binsof(cp_single_pos.p19);
      bins ctz_p2= binsof(cp_op.ctz) && binsof(cp_single_pos.p2);
      bins ctz_p20= binsof(cp_op.ctz) && binsof(cp_single_pos.p20);
      bins ctz_p21= binsof(cp_op.ctz) && binsof(cp_single_pos.p21);
      bins ctz_p22= binsof(cp_op.ctz) && binsof(cp_single_pos.p22);
      bins ctz_p23= binsof(cp_op.ctz) && binsof(cp_single_pos.p23);
      bins ctz_p24= binsof(cp_op.ctz) && binsof(cp_single_pos.p24);
      bins ctz_p25= binsof(cp_op.ctz) && binsof(cp_single_pos.p25);
      bins ctz_p26= binsof(cp_op.ctz) && binsof(cp_single_pos.p26);
      bins ctz_p27= binsof(cp_op.ctz) && binsof(cp_single_pos.p27);
      bins ctz_p28= binsof(cp_op.ctz) && binsof(cp_single_pos.p28);
      bins ctz_p29= binsof(cp_op.ctz) && binsof(cp_single_pos.p29);
      bins ctz_p3= binsof(cp_op.ctz) && binsof(cp_single_pos.p3);
      bins ctz_p30= binsof(cp_op.ctz) && binsof(cp_single_pos.p30);
      bins ctz_p31= binsof(cp_op.ctz) && binsof(cp_single_pos.p31);
      bins ctz_p4= binsof(cp_op.ctz) && binsof(cp_single_pos.p4);
      bins ctz_p5= binsof(cp_op.ctz) && binsof(cp_single_pos.p5);
      bins ctz_p6= binsof(cp_op.ctz) && binsof(cp_single_pos.p6);
      bins ctz_p7= binsof(cp_op.ctz) && binsof(cp_single_pos.p7);
      bins ctz_p8= binsof(cp_op.ctz) && binsof(cp_single_pos.p8);
      bins ctz_p9= binsof(cp_op.ctz) && binsof(cp_single_pos.p9);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins clz_no= binsof(cp_op.clz) && binsof(cp_rd_x0.no);
      bins clz_yes= binsof(cp_op.clz) && binsof(cp_rd_x0.yes);
      bins cpop_no= binsof(cp_op.cpop) && binsof(cp_rd_x0.no);
      bins cpop_yes= binsof(cp_op.cpop) && binsof(cp_rd_x0.yes);
      bins ctz_no= binsof(cp_op.ctz) && binsof(cp_rd_x0.no);
      bins ctz_yes= binsof(cp_op.ctz) && binsof(cp_rd_x0.yes);
    }
  endgroup

  // CG-CMP-001 (gen_cmp_zca_cg), 46 coverpoint bins, 250 cross bins
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_ADDI4SPN = 0;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_LW = 1;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_SW = 2;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_LWSP = 3;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_SWSP = 4;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_ADDI = 5;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_NOP = 6;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_JAL = 7;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_J = 8;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_LI = 9;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_LUI = 10;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_ADDI16SP = 11;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_SRLI = 12;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_SRAI = 13;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_ANDI = 14;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_SUB = 15;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_XOR = 16;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_OR = 17;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_AND = 18;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_BEQZ = 19;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_BNEZ = 20;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_SLLI = 21;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_MV = 22;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_JR = 23;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_ADD = 24;
  localparam int GEN_FC_CMP_ZCA_CP_INSN_C_JALR = 25;
  localparam int GEN_FC_CMP_ZCA_CP_PC_ALIGN_WORD = 0;
  localparam int GEN_FC_CMP_ZCA_CP_PC_ALIGN_HALF = 1;
  localparam int GEN_FC_CMP_ZCA_CP_NEXT_LEN_N16 = 0;
  localparam int GEN_FC_CMP_ZCA_CP_NEXT_LEN_N32 = 1;
  localparam int GEN_FC_CMP_ZCA_CP_PC_INC_TWO = 0;
  localparam int GEN_FC_CMP_ZCA_CP_INSN32_STRADDLE_NO = 0;
  localparam int GEN_FC_CMP_ZCA_CP_INSN32_STRADDLE_YES = 1;
  localparam int GEN_FC_CMP_ZCA_CP_REG3_R8 = 0;
  localparam int GEN_FC_CMP_ZCA_CP_REG3_R9 = 1;
  localparam int GEN_FC_CMP_ZCA_CP_REG3_R10 = 2;
  localparam int GEN_FC_CMP_ZCA_CP_REG3_R11 = 3;
  localparam int GEN_FC_CMP_ZCA_CP_REG3_R12 = 4;
  localparam int GEN_FC_CMP_ZCA_CP_REG3_R13 = 5;
  localparam int GEN_FC_CMP_ZCA_CP_REG3_R14 = 6;
  localparam int GEN_FC_CMP_ZCA_CP_REG3_R15 = 7;
  localparam int GEN_FC_CMP_ZCA_CP_RD_FULL_X1 = 0;
  localparam int GEN_FC_CMP_ZCA_CP_RD_FULL_X2 = 1;
  localparam int GEN_FC_CMP_ZCA_CP_RD_FULL_X8_15 = 2;
  localparam int GEN_FC_CMP_ZCA_CP_RD_FULL_X16_31 = 3;
  localparam int GEN_FC_CMP_ZCA_CP_RD_FULL_X3_7 = 4;
  covergroup gen_cmp_zca_cg with function sample(int v_cp_insn, int v_cp_pc_align, int v_cp_next_len, int v_cp_pc_inc, int v_cp_insn32_straddle, int v_cp_reg3, int v_cp_rd_full);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_insn: coverpoint v_cp_insn { bins c_addi4spn= {0}; bins c_lw= {1}; bins c_sw= {2}; bins c_lwsp= {3}; bins c_swsp= {4}; bins c_addi= {5}; bins c_nop= {6}; bins c_jal= {7}; bins c_j= {8}; bins c_li= {9}; bins c_lui= {10}; bins c_addi16sp= {11}; bins c_srli= {12}; bins c_srai= {13}; bins c_andi= {14}; bins c_sub= {15}; bins c_xor= {16}; bins c_or= {17}; bins c_and= {18}; bins c_beqz= {19}; bins c_bnez= {20}; bins c_slli= {21}; bins c_mv= {22}; bins c_jr= {23}; bins c_add= {24}; bins c_jalr= {25}; ignore_bins na = {-1}; }
    cp_pc_align: coverpoint v_cp_pc_align { bins word= {0}; bins half= {1}; ignore_bins na = {-1}; }
    cp_next_len: coverpoint v_cp_next_len { bins n16= {0}; bins n32= {1}; ignore_bins na = {-1}; }
    cp_pc_inc: coverpoint v_cp_pc_inc { bins two= {0}; ignore_bins na = {-1}; }
    cp_insn32_straddle: coverpoint v_cp_insn32_straddle { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_reg3: coverpoint v_cp_reg3 { bins r8= {0}; bins r9= {1}; bins r10= {2}; bins r11= {3}; bins r12= {4}; bins r13= {5}; bins r14= {6}; bins r15= {7}; ignore_bins na = {-1}; }
    cp_rd_full: coverpoint v_cp_rd_full { bins x1= {0}; bins x2= {1}; bins x8_15= {2}; bins x16_31= {3}; bins x3_7= {4}; ignore_bins na = {-1}; }
    cr_insn_align: cross cp_insn, cp_pc_align {
      bins c_add_half= binsof(cp_insn.c_add) && binsof(cp_pc_align.half);
      bins c_add_word= binsof(cp_insn.c_add) && binsof(cp_pc_align.word);
      bins c_addi16sp_half= binsof(cp_insn.c_addi16sp) && binsof(cp_pc_align.half);
      bins c_addi16sp_word= binsof(cp_insn.c_addi16sp) && binsof(cp_pc_align.word);
      bins c_addi4spn_half= binsof(cp_insn.c_addi4spn) && binsof(cp_pc_align.half);
      bins c_addi4spn_word= binsof(cp_insn.c_addi4spn) && binsof(cp_pc_align.word);
      bins c_addi_half= binsof(cp_insn.c_addi) && binsof(cp_pc_align.half);
      bins c_addi_word= binsof(cp_insn.c_addi) && binsof(cp_pc_align.word);
      bins c_and_half= binsof(cp_insn.c_and) && binsof(cp_pc_align.half);
      bins c_and_word= binsof(cp_insn.c_and) && binsof(cp_pc_align.word);
      bins c_andi_half= binsof(cp_insn.c_andi) && binsof(cp_pc_align.half);
      bins c_andi_word= binsof(cp_insn.c_andi) && binsof(cp_pc_align.word);
      bins c_beqz_half= binsof(cp_insn.c_beqz) && binsof(cp_pc_align.half);
      bins c_beqz_word= binsof(cp_insn.c_beqz) && binsof(cp_pc_align.word);
      bins c_bnez_half= binsof(cp_insn.c_bnez) && binsof(cp_pc_align.half);
      bins c_bnez_word= binsof(cp_insn.c_bnez) && binsof(cp_pc_align.word);
      bins c_j_half= binsof(cp_insn.c_j) && binsof(cp_pc_align.half);
      bins c_j_word= binsof(cp_insn.c_j) && binsof(cp_pc_align.word);
      bins c_jal_half= binsof(cp_insn.c_jal) && binsof(cp_pc_align.half);
      bins c_jal_word= binsof(cp_insn.c_jal) && binsof(cp_pc_align.word);
      bins c_jalr_half= binsof(cp_insn.c_jalr) && binsof(cp_pc_align.half);
      bins c_jalr_word= binsof(cp_insn.c_jalr) && binsof(cp_pc_align.word);
      bins c_jr_half= binsof(cp_insn.c_jr) && binsof(cp_pc_align.half);
      bins c_jr_word= binsof(cp_insn.c_jr) && binsof(cp_pc_align.word);
      bins c_li_half= binsof(cp_insn.c_li) && binsof(cp_pc_align.half);
      bins c_li_word= binsof(cp_insn.c_li) && binsof(cp_pc_align.word);
      bins c_lui_half= binsof(cp_insn.c_lui) && binsof(cp_pc_align.half);
      bins c_lui_word= binsof(cp_insn.c_lui) && binsof(cp_pc_align.word);
      bins c_lw_half= binsof(cp_insn.c_lw) && binsof(cp_pc_align.half);
      bins c_lw_word= binsof(cp_insn.c_lw) && binsof(cp_pc_align.word);
      bins c_lwsp_half= binsof(cp_insn.c_lwsp) && binsof(cp_pc_align.half);
      bins c_lwsp_word= binsof(cp_insn.c_lwsp) && binsof(cp_pc_align.word);
      bins c_mv_half= binsof(cp_insn.c_mv) && binsof(cp_pc_align.half);
      bins c_mv_word= binsof(cp_insn.c_mv) && binsof(cp_pc_align.word);
      bins c_nop_half= binsof(cp_insn.c_nop) && binsof(cp_pc_align.half);
      bins c_nop_word= binsof(cp_insn.c_nop) && binsof(cp_pc_align.word);
      bins c_or_half= binsof(cp_insn.c_or) && binsof(cp_pc_align.half);
      bins c_or_word= binsof(cp_insn.c_or) && binsof(cp_pc_align.word);
      bins c_slli_half= binsof(cp_insn.c_slli) && binsof(cp_pc_align.half);
      bins c_slli_word= binsof(cp_insn.c_slli) && binsof(cp_pc_align.word);
      bins c_srai_half= binsof(cp_insn.c_srai) && binsof(cp_pc_align.half);
      bins c_srai_word= binsof(cp_insn.c_srai) && binsof(cp_pc_align.word);
      bins c_srli_half= binsof(cp_insn.c_srli) && binsof(cp_pc_align.half);
      bins c_srli_word= binsof(cp_insn.c_srli) && binsof(cp_pc_align.word);
      bins c_sub_half= binsof(cp_insn.c_sub) && binsof(cp_pc_align.half);
      bins c_sub_word= binsof(cp_insn.c_sub) && binsof(cp_pc_align.word);
      bins c_sw_half= binsof(cp_insn.c_sw) && binsof(cp_pc_align.half);
      bins c_sw_word= binsof(cp_insn.c_sw) && binsof(cp_pc_align.word);
      bins c_swsp_half= binsof(cp_insn.c_swsp) && binsof(cp_pc_align.half);
      bins c_swsp_word= binsof(cp_insn.c_swsp) && binsof(cp_pc_align.word);
      bins c_xor_half= binsof(cp_insn.c_xor) && binsof(cp_pc_align.half);
      bins c_xor_word= binsof(cp_insn.c_xor) && binsof(cp_pc_align.word);
    }
    cr_insn_next: cross cp_insn, cp_next_len {
      bins c_add_n16= binsof(cp_insn.c_add) && binsof(cp_next_len.n16);
      bins c_add_n32= binsof(cp_insn.c_add) && binsof(cp_next_len.n32);
      bins c_addi16sp_n16= binsof(cp_insn.c_addi16sp) && binsof(cp_next_len.n16);
      bins c_addi16sp_n32= binsof(cp_insn.c_addi16sp) && binsof(cp_next_len.n32);
      bins c_addi4spn_n16= binsof(cp_insn.c_addi4spn) && binsof(cp_next_len.n16);
      bins c_addi4spn_n32= binsof(cp_insn.c_addi4spn) && binsof(cp_next_len.n32);
      bins c_addi_n16= binsof(cp_insn.c_addi) && binsof(cp_next_len.n16);
      bins c_addi_n32= binsof(cp_insn.c_addi) && binsof(cp_next_len.n32);
      bins c_and_n16= binsof(cp_insn.c_and) && binsof(cp_next_len.n16);
      bins c_and_n32= binsof(cp_insn.c_and) && binsof(cp_next_len.n32);
      bins c_andi_n16= binsof(cp_insn.c_andi) && binsof(cp_next_len.n16);
      bins c_andi_n32= binsof(cp_insn.c_andi) && binsof(cp_next_len.n32);
      bins c_beqz_n16= binsof(cp_insn.c_beqz) && binsof(cp_next_len.n16);
      bins c_beqz_n32= binsof(cp_insn.c_beqz) && binsof(cp_next_len.n32);
      bins c_bnez_n16= binsof(cp_insn.c_bnez) && binsof(cp_next_len.n16);
      bins c_bnez_n32= binsof(cp_insn.c_bnez) && binsof(cp_next_len.n32);
      bins c_j_n16= binsof(cp_insn.c_j) && binsof(cp_next_len.n16);
      bins c_j_n32= binsof(cp_insn.c_j) && binsof(cp_next_len.n32);
      bins c_jal_n16= binsof(cp_insn.c_jal) && binsof(cp_next_len.n16);
      bins c_jal_n32= binsof(cp_insn.c_jal) && binsof(cp_next_len.n32);
      bins c_jalr_n16= binsof(cp_insn.c_jalr) && binsof(cp_next_len.n16);
      bins c_jalr_n32= binsof(cp_insn.c_jalr) && binsof(cp_next_len.n32);
      bins c_jr_n16= binsof(cp_insn.c_jr) && binsof(cp_next_len.n16);
      bins c_jr_n32= binsof(cp_insn.c_jr) && binsof(cp_next_len.n32);
      bins c_li_n16= binsof(cp_insn.c_li) && binsof(cp_next_len.n16);
      bins c_li_n32= binsof(cp_insn.c_li) && binsof(cp_next_len.n32);
      bins c_lui_n16= binsof(cp_insn.c_lui) && binsof(cp_next_len.n16);
      bins c_lui_n32= binsof(cp_insn.c_lui) && binsof(cp_next_len.n32);
      bins c_lw_n16= binsof(cp_insn.c_lw) && binsof(cp_next_len.n16);
      bins c_lw_n32= binsof(cp_insn.c_lw) && binsof(cp_next_len.n32);
      bins c_lwsp_n16= binsof(cp_insn.c_lwsp) && binsof(cp_next_len.n16);
      bins c_lwsp_n32= binsof(cp_insn.c_lwsp) && binsof(cp_next_len.n32);
      bins c_mv_n16= binsof(cp_insn.c_mv) && binsof(cp_next_len.n16);
      bins c_mv_n32= binsof(cp_insn.c_mv) && binsof(cp_next_len.n32);
      bins c_nop_n16= binsof(cp_insn.c_nop) && binsof(cp_next_len.n16);
      bins c_nop_n32= binsof(cp_insn.c_nop) && binsof(cp_next_len.n32);
      bins c_or_n16= binsof(cp_insn.c_or) && binsof(cp_next_len.n16);
      bins c_or_n32= binsof(cp_insn.c_or) && binsof(cp_next_len.n32);
      bins c_slli_n16= binsof(cp_insn.c_slli) && binsof(cp_next_len.n16);
      bins c_slli_n32= binsof(cp_insn.c_slli) && binsof(cp_next_len.n32);
      bins c_srai_n16= binsof(cp_insn.c_srai) && binsof(cp_next_len.n16);
      bins c_srai_n32= binsof(cp_insn.c_srai) && binsof(cp_next_len.n32);
      bins c_srli_n16= binsof(cp_insn.c_srli) && binsof(cp_next_len.n16);
      bins c_srli_n32= binsof(cp_insn.c_srli) && binsof(cp_next_len.n32);
      bins c_sub_n16= binsof(cp_insn.c_sub) && binsof(cp_next_len.n16);
      bins c_sub_n32= binsof(cp_insn.c_sub) && binsof(cp_next_len.n32);
      bins c_sw_n16= binsof(cp_insn.c_sw) && binsof(cp_next_len.n16);
      bins c_sw_n32= binsof(cp_insn.c_sw) && binsof(cp_next_len.n32);
      bins c_swsp_n16= binsof(cp_insn.c_swsp) && binsof(cp_next_len.n16);
      bins c_swsp_n32= binsof(cp_insn.c_swsp) && binsof(cp_next_len.n32);
      bins c_xor_n16= binsof(cp_insn.c_xor) && binsof(cp_next_len.n16);
      bins c_xor_n32= binsof(cp_insn.c_xor) && binsof(cp_next_len.n32);
    }
    cr_insn_reg3: cross cp_insn, cp_reg3 {
      bins c_addi4spn_r10= binsof(cp_insn.c_addi4spn) && binsof(cp_reg3.r10);
      bins c_addi4spn_r11= binsof(cp_insn.c_addi4spn) && binsof(cp_reg3.r11);
      bins c_addi4spn_r12= binsof(cp_insn.c_addi4spn) && binsof(cp_reg3.r12);
      bins c_addi4spn_r13= binsof(cp_insn.c_addi4spn) && binsof(cp_reg3.r13);
      bins c_addi4spn_r14= binsof(cp_insn.c_addi4spn) && binsof(cp_reg3.r14);
      bins c_addi4spn_r15= binsof(cp_insn.c_addi4spn) && binsof(cp_reg3.r15);
      bins c_addi4spn_r8= binsof(cp_insn.c_addi4spn) && binsof(cp_reg3.r8);
      bins c_addi4spn_r9= binsof(cp_insn.c_addi4spn) && binsof(cp_reg3.r9);
      bins c_and_r10= binsof(cp_insn.c_and) && binsof(cp_reg3.r10);
      bins c_and_r11= binsof(cp_insn.c_and) && binsof(cp_reg3.r11);
      bins c_and_r12= binsof(cp_insn.c_and) && binsof(cp_reg3.r12);
      bins c_and_r13= binsof(cp_insn.c_and) && binsof(cp_reg3.r13);
      bins c_and_r14= binsof(cp_insn.c_and) && binsof(cp_reg3.r14);
      bins c_and_r15= binsof(cp_insn.c_and) && binsof(cp_reg3.r15);
      bins c_and_r8= binsof(cp_insn.c_and) && binsof(cp_reg3.r8);
      bins c_and_r9= binsof(cp_insn.c_and) && binsof(cp_reg3.r9);
      bins c_or_r10= binsof(cp_insn.c_or) && binsof(cp_reg3.r10);
      bins c_or_r11= binsof(cp_insn.c_or) && binsof(cp_reg3.r11);
      bins c_or_r12= binsof(cp_insn.c_or) && binsof(cp_reg3.r12);
      bins c_or_r13= binsof(cp_insn.c_or) && binsof(cp_reg3.r13);
      bins c_or_r14= binsof(cp_insn.c_or) && binsof(cp_reg3.r14);
      bins c_or_r15= binsof(cp_insn.c_or) && binsof(cp_reg3.r15);
      bins c_or_r8= binsof(cp_insn.c_or) && binsof(cp_reg3.r8);
      bins c_or_r9= binsof(cp_insn.c_or) && binsof(cp_reg3.r9);
      bins c_sub_r10= binsof(cp_insn.c_sub) && binsof(cp_reg3.r10);
      bins c_sub_r11= binsof(cp_insn.c_sub) && binsof(cp_reg3.r11);
      bins c_sub_r12= binsof(cp_insn.c_sub) && binsof(cp_reg3.r12);
      bins c_sub_r13= binsof(cp_insn.c_sub) && binsof(cp_reg3.r13);
      bins c_sub_r14= binsof(cp_insn.c_sub) && binsof(cp_reg3.r14);
      bins c_sub_r15= binsof(cp_insn.c_sub) && binsof(cp_reg3.r15);
      bins c_sub_r8= binsof(cp_insn.c_sub) && binsof(cp_reg3.r8);
      bins c_sub_r9= binsof(cp_insn.c_sub) && binsof(cp_reg3.r9);
      bins c_xor_r10= binsof(cp_insn.c_xor) && binsof(cp_reg3.r10);
      bins c_xor_r11= binsof(cp_insn.c_xor) && binsof(cp_reg3.r11);
      bins c_xor_r12= binsof(cp_insn.c_xor) && binsof(cp_reg3.r12);
      bins c_xor_r13= binsof(cp_insn.c_xor) && binsof(cp_reg3.r13);
      bins c_xor_r14= binsof(cp_insn.c_xor) && binsof(cp_reg3.r14);
      bins c_xor_r15= binsof(cp_insn.c_xor) && binsof(cp_reg3.r15);
      bins c_xor_r8= binsof(cp_insn.c_xor) && binsof(cp_reg3.r8);
      bins c_xor_r9= binsof(cp_insn.c_xor) && binsof(cp_reg3.r9);
      bins c_andi_r10= binsof(cp_insn.c_andi) && binsof(cp_reg3.r10);
      bins c_andi_r11= binsof(cp_insn.c_andi) && binsof(cp_reg3.r11);
      bins c_andi_r12= binsof(cp_insn.c_andi) && binsof(cp_reg3.r12);
      bins c_andi_r13= binsof(cp_insn.c_andi) && binsof(cp_reg3.r13);
      bins c_andi_r14= binsof(cp_insn.c_andi) && binsof(cp_reg3.r14);
      bins c_andi_r15= binsof(cp_insn.c_andi) && binsof(cp_reg3.r15);
      bins c_andi_r8= binsof(cp_insn.c_andi) && binsof(cp_reg3.r8);
      bins c_andi_r9= binsof(cp_insn.c_andi) && binsof(cp_reg3.r9);
      bins c_beqz_r10= binsof(cp_insn.c_beqz) && binsof(cp_reg3.r10);
      bins c_beqz_r11= binsof(cp_insn.c_beqz) && binsof(cp_reg3.r11);
      bins c_beqz_r12= binsof(cp_insn.c_beqz) && binsof(cp_reg3.r12);
      bins c_beqz_r13= binsof(cp_insn.c_beqz) && binsof(cp_reg3.r13);
      bins c_beqz_r14= binsof(cp_insn.c_beqz) && binsof(cp_reg3.r14);
      bins c_beqz_r15= binsof(cp_insn.c_beqz) && binsof(cp_reg3.r15);
      bins c_beqz_r8= binsof(cp_insn.c_beqz) && binsof(cp_reg3.r8);
      bins c_beqz_r9= binsof(cp_insn.c_beqz) && binsof(cp_reg3.r9);
      bins c_bnez_r10= binsof(cp_insn.c_bnez) && binsof(cp_reg3.r10);
      bins c_bnez_r11= binsof(cp_insn.c_bnez) && binsof(cp_reg3.r11);
      bins c_bnez_r12= binsof(cp_insn.c_bnez) && binsof(cp_reg3.r12);
      bins c_bnez_r13= binsof(cp_insn.c_bnez) && binsof(cp_reg3.r13);
      bins c_bnez_r14= binsof(cp_insn.c_bnez) && binsof(cp_reg3.r14);
      bins c_bnez_r15= binsof(cp_insn.c_bnez) && binsof(cp_reg3.r15);
      bins c_bnez_r8= binsof(cp_insn.c_bnez) && binsof(cp_reg3.r8);
      bins c_bnez_r9= binsof(cp_insn.c_bnez) && binsof(cp_reg3.r9);
      bins c_lw_r10= binsof(cp_insn.c_lw) && binsof(cp_reg3.r10);
      bins c_lw_r11= binsof(cp_insn.c_lw) && binsof(cp_reg3.r11);
      bins c_lw_r12= binsof(cp_insn.c_lw) && binsof(cp_reg3.r12);
      bins c_lw_r13= binsof(cp_insn.c_lw) && binsof(cp_reg3.r13);
      bins c_lw_r14= binsof(cp_insn.c_lw) && binsof(cp_reg3.r14);
      bins c_lw_r15= binsof(cp_insn.c_lw) && binsof(cp_reg3.r15);
      bins c_lw_r8= binsof(cp_insn.c_lw) && binsof(cp_reg3.r8);
      bins c_lw_r9= binsof(cp_insn.c_lw) && binsof(cp_reg3.r9);
      bins c_srai_r10= binsof(cp_insn.c_srai) && binsof(cp_reg3.r10);
      bins c_srai_r11= binsof(cp_insn.c_srai) && binsof(cp_reg3.r11);
      bins c_srai_r12= binsof(cp_insn.c_srai) && binsof(cp_reg3.r12);
      bins c_srai_r13= binsof(cp_insn.c_srai) && binsof(cp_reg3.r13);
      bins c_srai_r14= binsof(cp_insn.c_srai) && binsof(cp_reg3.r14);
      bins c_srai_r15= binsof(cp_insn.c_srai) && binsof(cp_reg3.r15);
      bins c_srai_r8= binsof(cp_insn.c_srai) && binsof(cp_reg3.r8);
      bins c_srai_r9= binsof(cp_insn.c_srai) && binsof(cp_reg3.r9);
      bins c_srli_r10= binsof(cp_insn.c_srli) && binsof(cp_reg3.r10);
      bins c_srli_r11= binsof(cp_insn.c_srli) && binsof(cp_reg3.r11);
      bins c_srli_r12= binsof(cp_insn.c_srli) && binsof(cp_reg3.r12);
      bins c_srli_r13= binsof(cp_insn.c_srli) && binsof(cp_reg3.r13);
      bins c_srli_r14= binsof(cp_insn.c_srli) && binsof(cp_reg3.r14);
      bins c_srli_r15= binsof(cp_insn.c_srli) && binsof(cp_reg3.r15);
      bins c_srli_r8= binsof(cp_insn.c_srli) && binsof(cp_reg3.r8);
      bins c_srli_r9= binsof(cp_insn.c_srli) && binsof(cp_reg3.r9);
      bins c_sw_r10= binsof(cp_insn.c_sw) && binsof(cp_reg3.r10);
      bins c_sw_r11= binsof(cp_insn.c_sw) && binsof(cp_reg3.r11);
      bins c_sw_r12= binsof(cp_insn.c_sw) && binsof(cp_reg3.r12);
      bins c_sw_r13= binsof(cp_insn.c_sw) && binsof(cp_reg3.r13);
      bins c_sw_r14= binsof(cp_insn.c_sw) && binsof(cp_reg3.r14);
      bins c_sw_r15= binsof(cp_insn.c_sw) && binsof(cp_reg3.r15);
      bins c_sw_r8= binsof(cp_insn.c_sw) && binsof(cp_reg3.r8);
      bins c_sw_r9= binsof(cp_insn.c_sw) && binsof(cp_reg3.r9);
    }
    cr_insn_rdfull: cross cp_insn, cp_rd_full {
      bins c_lwsp_x1= binsof(cp_insn.c_lwsp) && binsof(cp_rd_full.x1);
      bins c_lwsp_x16_31= binsof(cp_insn.c_lwsp) && binsof(cp_rd_full.x16_31);
      bins c_lwsp_x2= binsof(cp_insn.c_lwsp) && binsof(cp_rd_full.x2);
      bins c_lwsp_x3_7= binsof(cp_insn.c_lwsp) && binsof(cp_rd_full.x3_7);
      bins c_lwsp_x8_15= binsof(cp_insn.c_lwsp) && binsof(cp_rd_full.x8_15);
      bins c_swsp_x1= binsof(cp_insn.c_swsp) && binsof(cp_rd_full.x1);
      bins c_swsp_x16_31= binsof(cp_insn.c_swsp) && binsof(cp_rd_full.x16_31);
      bins c_swsp_x2= binsof(cp_insn.c_swsp) && binsof(cp_rd_full.x2);
      bins c_swsp_x3_7= binsof(cp_insn.c_swsp) && binsof(cp_rd_full.x3_7);
      bins c_swsp_x8_15= binsof(cp_insn.c_swsp) && binsof(cp_rd_full.x8_15);
      bins c_slli_x1= binsof(cp_insn.c_slli) && binsof(cp_rd_full.x1);
      bins c_slli_x16_31= binsof(cp_insn.c_slli) && binsof(cp_rd_full.x16_31);
      bins c_slli_x2= binsof(cp_insn.c_slli) && binsof(cp_rd_full.x2);
      bins c_slli_x3_7= binsof(cp_insn.c_slli) && binsof(cp_rd_full.x3_7);
      bins c_slli_x8_15= binsof(cp_insn.c_slli) && binsof(cp_rd_full.x8_15);
      bins c_mv_x1= binsof(cp_insn.c_mv) && binsof(cp_rd_full.x1);
      bins c_mv_x16_31= binsof(cp_insn.c_mv) && binsof(cp_rd_full.x16_31);
      bins c_mv_x2= binsof(cp_insn.c_mv) && binsof(cp_rd_full.x2);
      bins c_mv_x3_7= binsof(cp_insn.c_mv) && binsof(cp_rd_full.x3_7);
      bins c_mv_x8_15= binsof(cp_insn.c_mv) && binsof(cp_rd_full.x8_15);
      bins c_add_x1= binsof(cp_insn.c_add) && binsof(cp_rd_full.x1);
      bins c_add_x16_31= binsof(cp_insn.c_add) && binsof(cp_rd_full.x16_31);
      bins c_add_x2= binsof(cp_insn.c_add) && binsof(cp_rd_full.x2);
      bins c_add_x3_7= binsof(cp_insn.c_add) && binsof(cp_rd_full.x3_7);
      bins c_add_x8_15= binsof(cp_insn.c_add) && binsof(cp_rd_full.x8_15);
      bins c_addi16sp_x2= binsof(cp_insn.c_addi16sp) && binsof(cp_rd_full.x2);
      bins c_addi_x1= binsof(cp_insn.c_addi) && binsof(cp_rd_full.x1);
      bins c_addi_x16_31= binsof(cp_insn.c_addi) && binsof(cp_rd_full.x16_31);
      bins c_addi_x2= binsof(cp_insn.c_addi) && binsof(cp_rd_full.x2);
      bins c_addi_x3_7= binsof(cp_insn.c_addi) && binsof(cp_rd_full.x3_7);
      bins c_addi_x8_15= binsof(cp_insn.c_addi) && binsof(cp_rd_full.x8_15);
      bins c_jalr_x1= binsof(cp_insn.c_jalr) && binsof(cp_rd_full.x1);
      bins c_jalr_x16_31= binsof(cp_insn.c_jalr) && binsof(cp_rd_full.x16_31);
      bins c_jalr_x2= binsof(cp_insn.c_jalr) && binsof(cp_rd_full.x2);
      bins c_jalr_x3_7= binsof(cp_insn.c_jalr) && binsof(cp_rd_full.x3_7);
      bins c_jalr_x8_15= binsof(cp_insn.c_jalr) && binsof(cp_rd_full.x8_15);
      bins c_jr_x1= binsof(cp_insn.c_jr) && binsof(cp_rd_full.x1);
      bins c_jr_x16_31= binsof(cp_insn.c_jr) && binsof(cp_rd_full.x16_31);
      bins c_jr_x2= binsof(cp_insn.c_jr) && binsof(cp_rd_full.x2);
      bins c_jr_x3_7= binsof(cp_insn.c_jr) && binsof(cp_rd_full.x3_7);
      bins c_jr_x8_15= binsof(cp_insn.c_jr) && binsof(cp_rd_full.x8_15);
      bins c_li_x1= binsof(cp_insn.c_li) && binsof(cp_rd_full.x1);
      bins c_li_x16_31= binsof(cp_insn.c_li) && binsof(cp_rd_full.x16_31);
      bins c_li_x2= binsof(cp_insn.c_li) && binsof(cp_rd_full.x2);
      bins c_li_x3_7= binsof(cp_insn.c_li) && binsof(cp_rd_full.x3_7);
      bins c_li_x8_15= binsof(cp_insn.c_li) && binsof(cp_rd_full.x8_15);
      bins c_lui_x1= binsof(cp_insn.c_lui) && binsof(cp_rd_full.x1);
      bins c_lui_x16_31= binsof(cp_insn.c_lui) && binsof(cp_rd_full.x16_31);
      bins c_lui_x3_7= binsof(cp_insn.c_lui) && binsof(cp_rd_full.x3_7);
      bins c_lui_x8_15= binsof(cp_insn.c_lui) && binsof(cp_rd_full.x8_15);
    }
  endgroup

  // CG-CMP-006 (gen_cmp_zcmp_pushpop_cg), 47 coverpoint bins, 244 cross bins
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP = 1;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRET = 2;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRETZ = 3;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R4 = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R5 = 1;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R6 = 2;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R7 = 3;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R8 = 4;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R9 = 5;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R10 = 6;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R11 = 7;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R12 = 8;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R13 = 9;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R14 = 10;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R15 = 11;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SPIMM_S0 = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SPIMM_S1 = 1;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SPIMM_S2 = 2;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SPIMM_S3 = 3;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A16 = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A32 = 1;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A48 = 2;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A64 = 3;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A80 = 4;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A96 = 5;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A112 = 6;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_ALIGN_ALIGNED = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_ALIGN_MIS1 = 1;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_ALIGN_MIS2 = 2;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_ALIGN_MIS3 = 3;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_NONE = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_PUSH_BELOW_ZERO = 1;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_POP_ABOVE_MAX = 2;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_UOP_COUNT_OK_YES = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_ORDER_OK_YES = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RVFI_TAGS_OK_YES = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_MINSTRET_ONCE_YES = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_WORD = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_HALF = 1;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_ODD = 2;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_MIN1 = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_SHORT = 1;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_LONG = 2;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_MIXED = 3;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_DUMMY_EN_OFF = 0;
  localparam int GEN_FC_CMP_ZCMP_PUSHPOP_CP_DUMMY_EN_ON = 1;
  covergroup gen_cmp_zcmp_pushpop_cg with function sample(int v_cp_insn, int v_cp_rlist, int v_cp_spimm, int v_cp_stack_adj, int v_cp_sp_align, int v_cp_sp_wrap, int v_cp_uop_count_ok, int v_cp_order_ok, int v_cp_rvfi_tags_ok, int v_cp_minstret_once, int v_cp_ret_align, int v_cp_dmem_delay, int v_cp_dummy_en);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_insn: coverpoint v_cp_insn { bins cm_push= {0}; bins cm_pop= {1}; bins cm_popret= {2}; bins cm_popretz= {3}; ignore_bins na = {-1}; }
    cp_rlist: coverpoint v_cp_rlist { bins r4= {0}; bins r5= {1}; bins r6= {2}; bins r7= {3}; bins r8= {4}; bins r9= {5}; bins r10= {6}; bins r11= {7}; bins r12= {8}; bins r13= {9}; bins r14= {10}; bins r15= {11}; ignore_bins na = {-1}; }
    cp_spimm: coverpoint v_cp_spimm { bins s0= {0}; bins s1= {1}; bins s2= {2}; bins s3= {3}; ignore_bins na = {-1}; }
    cp_stack_adj: coverpoint v_cp_stack_adj { bins a16= {0}; bins a32= {1}; bins a48= {2}; bins a64= {3}; bins a80= {4}; bins a96= {5}; bins a112= {6}; ignore_bins na = {-1}; }
    cp_sp_align: coverpoint v_cp_sp_align { bins aligned= {0}; bins mis1= {1}; bins mis2= {2}; bins mis3= {3}; ignore_bins na = {-1}; }
    cp_sp_wrap: coverpoint v_cp_sp_wrap { bins none= {0}; bins push_below_zero= {1}; bins pop_above_max= {2}; ignore_bins na = {-1}; }
    cp_uop_count_ok: coverpoint v_cp_uop_count_ok { bins yes= {0}; ignore_bins na = {-1}; }
    cp_order_ok: coverpoint v_cp_order_ok { bins yes= {0}; ignore_bins na = {-1}; }
    cp_rvfi_tags_ok: coverpoint v_cp_rvfi_tags_ok { bins yes= {0}; ignore_bins na = {-1}; }
    cp_minstret_once: coverpoint v_cp_minstret_once { bins yes= {0}; ignore_bins na = {-1}; }
    cp_ret_align: coverpoint v_cp_ret_align { bins word= {0}; bins half= {1}; bins odd= {2}; ignore_bins na = {-1}; }
    cp_dmem_delay: coverpoint v_cp_dmem_delay { bins min1= {0}; bins short= {1}; bins long= {2}; bins mixed= {3}; ignore_bins na = {-1}; }
    cp_dummy_en: coverpoint v_cp_dummy_en { bins off= {0}; bins on= {1}; ignore_bins na = {-1}; }
    cr_insn_delay: cross cp_insn, cp_dmem_delay {
      bins cm_push_long= binsof(cp_insn.cm_push) && binsof(cp_dmem_delay.long);
      bins cm_push_min1= binsof(cp_insn.cm_push) && binsof(cp_dmem_delay.min1);
      bins cm_push_mixed= binsof(cp_insn.cm_push) && binsof(cp_dmem_delay.mixed);
      bins cm_push_short= binsof(cp_insn.cm_push) && binsof(cp_dmem_delay.short);
      bins cm_pop_long= binsof(cp_insn.cm_pop) && binsof(cp_dmem_delay.long);
      bins cm_pop_min1= binsof(cp_insn.cm_pop) && binsof(cp_dmem_delay.min1);
      bins cm_pop_mixed= binsof(cp_insn.cm_pop) && binsof(cp_dmem_delay.mixed);
      bins cm_pop_short= binsof(cp_insn.cm_pop) && binsof(cp_dmem_delay.short);
      bins cm_popret_long= binsof(cp_insn.cm_popret) && binsof(cp_dmem_delay.long);
      bins cm_popret_min1= binsof(cp_insn.cm_popret) && binsof(cp_dmem_delay.min1);
      bins cm_popret_mixed= binsof(cp_insn.cm_popret) && binsof(cp_dmem_delay.mixed);
      bins cm_popret_short= binsof(cp_insn.cm_popret) && binsof(cp_dmem_delay.short);
      bins cm_popretz_long= binsof(cp_insn.cm_popretz) && binsof(cp_dmem_delay.long);
      bins cm_popretz_min1= binsof(cp_insn.cm_popretz) && binsof(cp_dmem_delay.min1);
      bins cm_popretz_mixed= binsof(cp_insn.cm_popretz) && binsof(cp_dmem_delay.mixed);
      bins cm_popretz_short= binsof(cp_insn.cm_popretz) && binsof(cp_dmem_delay.short);
    }
    cr_insn_rlist_spimm: cross cp_insn, cp_rlist, cp_spimm {
      bins cm_push_r10_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r10) && binsof(cp_spimm.s0);
      bins cm_push_r10_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r10) && binsof(cp_spimm.s1);
      bins cm_push_r10_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r10) && binsof(cp_spimm.s2);
      bins cm_push_r10_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r10) && binsof(cp_spimm.s3);
      bins cm_push_r11_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r11) && binsof(cp_spimm.s0);
      bins cm_push_r11_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r11) && binsof(cp_spimm.s1);
      bins cm_push_r11_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r11) && binsof(cp_spimm.s2);
      bins cm_push_r11_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r11) && binsof(cp_spimm.s3);
      bins cm_push_r12_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r12) && binsof(cp_spimm.s0);
      bins cm_push_r12_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r12) && binsof(cp_spimm.s1);
      bins cm_push_r12_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r12) && binsof(cp_spimm.s2);
      bins cm_push_r12_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r12) && binsof(cp_spimm.s3);
      bins cm_push_r13_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r13) && binsof(cp_spimm.s0);
      bins cm_push_r13_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r13) && binsof(cp_spimm.s1);
      bins cm_push_r13_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r13) && binsof(cp_spimm.s2);
      bins cm_push_r13_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r13) && binsof(cp_spimm.s3);
      bins cm_push_r14_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r14) && binsof(cp_spimm.s0);
      bins cm_push_r14_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r14) && binsof(cp_spimm.s1);
      bins cm_push_r14_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r14) && binsof(cp_spimm.s2);
      bins cm_push_r14_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r14) && binsof(cp_spimm.s3);
      bins cm_push_r15_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r15) && binsof(cp_spimm.s0);
      bins cm_push_r15_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r15) && binsof(cp_spimm.s1);
      bins cm_push_r15_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r15) && binsof(cp_spimm.s2);
      bins cm_push_r15_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r15) && binsof(cp_spimm.s3);
      bins cm_push_r4_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r4) && binsof(cp_spimm.s0);
      bins cm_push_r4_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r4) && binsof(cp_spimm.s1);
      bins cm_push_r4_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r4) && binsof(cp_spimm.s2);
      bins cm_push_r4_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r4) && binsof(cp_spimm.s3);
      bins cm_push_r5_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r5) && binsof(cp_spimm.s0);
      bins cm_push_r5_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r5) && binsof(cp_spimm.s1);
      bins cm_push_r5_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r5) && binsof(cp_spimm.s2);
      bins cm_push_r5_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r5) && binsof(cp_spimm.s3);
      bins cm_push_r6_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r6) && binsof(cp_spimm.s0);
      bins cm_push_r6_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r6) && binsof(cp_spimm.s1);
      bins cm_push_r6_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r6) && binsof(cp_spimm.s2);
      bins cm_push_r6_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r6) && binsof(cp_spimm.s3);
      bins cm_push_r7_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r7) && binsof(cp_spimm.s0);
      bins cm_push_r7_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r7) && binsof(cp_spimm.s1);
      bins cm_push_r7_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r7) && binsof(cp_spimm.s2);
      bins cm_push_r7_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r7) && binsof(cp_spimm.s3);
      bins cm_push_r8_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r8) && binsof(cp_spimm.s0);
      bins cm_push_r8_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r8) && binsof(cp_spimm.s1);
      bins cm_push_r8_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r8) && binsof(cp_spimm.s2);
      bins cm_push_r8_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r8) && binsof(cp_spimm.s3);
      bins cm_push_r9_s0= binsof(cp_insn.cm_push) && binsof(cp_rlist.r9) && binsof(cp_spimm.s0);
      bins cm_push_r9_s1= binsof(cp_insn.cm_push) && binsof(cp_rlist.r9) && binsof(cp_spimm.s1);
      bins cm_push_r9_s2= binsof(cp_insn.cm_push) && binsof(cp_rlist.r9) && binsof(cp_spimm.s2);
      bins cm_push_r9_s3= binsof(cp_insn.cm_push) && binsof(cp_rlist.r9) && binsof(cp_spimm.s3);
      bins cm_pop_r10_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r10) && binsof(cp_spimm.s0);
      bins cm_pop_r10_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r10) && binsof(cp_spimm.s1);
      bins cm_pop_r10_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r10) && binsof(cp_spimm.s2);
      bins cm_pop_r10_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r10) && binsof(cp_spimm.s3);
      bins cm_pop_r11_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r11) && binsof(cp_spimm.s0);
      bins cm_pop_r11_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r11) && binsof(cp_spimm.s1);
      bins cm_pop_r11_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r11) && binsof(cp_spimm.s2);
      bins cm_pop_r11_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r11) && binsof(cp_spimm.s3);
      bins cm_pop_r12_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r12) && binsof(cp_spimm.s0);
      bins cm_pop_r12_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r12) && binsof(cp_spimm.s1);
      bins cm_pop_r12_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r12) && binsof(cp_spimm.s2);
      bins cm_pop_r12_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r12) && binsof(cp_spimm.s3);
      bins cm_pop_r13_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r13) && binsof(cp_spimm.s0);
      bins cm_pop_r13_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r13) && binsof(cp_spimm.s1);
      bins cm_pop_r13_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r13) && binsof(cp_spimm.s2);
      bins cm_pop_r13_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r13) && binsof(cp_spimm.s3);
      bins cm_pop_r14_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r14) && binsof(cp_spimm.s0);
      bins cm_pop_r14_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r14) && binsof(cp_spimm.s1);
      bins cm_pop_r14_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r14) && binsof(cp_spimm.s2);
      bins cm_pop_r14_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r14) && binsof(cp_spimm.s3);
      bins cm_pop_r15_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r15) && binsof(cp_spimm.s0);
      bins cm_pop_r15_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r15) && binsof(cp_spimm.s1);
      bins cm_pop_r15_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r15) && binsof(cp_spimm.s2);
      bins cm_pop_r15_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r15) && binsof(cp_spimm.s3);
      bins cm_pop_r4_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r4) && binsof(cp_spimm.s0);
      bins cm_pop_r4_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r4) && binsof(cp_spimm.s1);
      bins cm_pop_r4_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r4) && binsof(cp_spimm.s2);
      bins cm_pop_r4_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r4) && binsof(cp_spimm.s3);
      bins cm_pop_r5_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r5) && binsof(cp_spimm.s0);
      bins cm_pop_r5_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r5) && binsof(cp_spimm.s1);
      bins cm_pop_r5_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r5) && binsof(cp_spimm.s2);
      bins cm_pop_r5_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r5) && binsof(cp_spimm.s3);
      bins cm_pop_r6_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r6) && binsof(cp_spimm.s0);
      bins cm_pop_r6_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r6) && binsof(cp_spimm.s1);
      bins cm_pop_r6_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r6) && binsof(cp_spimm.s2);
      bins cm_pop_r6_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r6) && binsof(cp_spimm.s3);
      bins cm_pop_r7_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r7) && binsof(cp_spimm.s0);
      bins cm_pop_r7_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r7) && binsof(cp_spimm.s1);
      bins cm_pop_r7_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r7) && binsof(cp_spimm.s2);
      bins cm_pop_r7_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r7) && binsof(cp_spimm.s3);
      bins cm_pop_r8_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r8) && binsof(cp_spimm.s0);
      bins cm_pop_r8_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r8) && binsof(cp_spimm.s1);
      bins cm_pop_r8_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r8) && binsof(cp_spimm.s2);
      bins cm_pop_r8_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r8) && binsof(cp_spimm.s3);
      bins cm_pop_r9_s0= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r9) && binsof(cp_spimm.s0);
      bins cm_pop_r9_s1= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r9) && binsof(cp_spimm.s1);
      bins cm_pop_r9_s2= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r9) && binsof(cp_spimm.s2);
      bins cm_pop_r9_s3= binsof(cp_insn.cm_pop) && binsof(cp_rlist.r9) && binsof(cp_spimm.s3);
      bins cm_popret_r10_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r10) && binsof(cp_spimm.s0);
      bins cm_popret_r10_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r10) && binsof(cp_spimm.s1);
      bins cm_popret_r10_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r10) && binsof(cp_spimm.s2);
      bins cm_popret_r10_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r10) && binsof(cp_spimm.s3);
      bins cm_popret_r11_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r11) && binsof(cp_spimm.s0);
      bins cm_popret_r11_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r11) && binsof(cp_spimm.s1);
      bins cm_popret_r11_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r11) && binsof(cp_spimm.s2);
      bins cm_popret_r11_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r11) && binsof(cp_spimm.s3);
      bins cm_popret_r12_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r12) && binsof(cp_spimm.s0);
      bins cm_popret_r12_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r12) && binsof(cp_spimm.s1);
      bins cm_popret_r12_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r12) && binsof(cp_spimm.s2);
      bins cm_popret_r12_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r12) && binsof(cp_spimm.s3);
      bins cm_popret_r13_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r13) && binsof(cp_spimm.s0);
      bins cm_popret_r13_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r13) && binsof(cp_spimm.s1);
      bins cm_popret_r13_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r13) && binsof(cp_spimm.s2);
      bins cm_popret_r13_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r13) && binsof(cp_spimm.s3);
      bins cm_popret_r14_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r14) && binsof(cp_spimm.s0);
      bins cm_popret_r14_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r14) && binsof(cp_spimm.s1);
      bins cm_popret_r14_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r14) && binsof(cp_spimm.s2);
      bins cm_popret_r14_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r14) && binsof(cp_spimm.s3);
      bins cm_popret_r15_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r15) && binsof(cp_spimm.s0);
      bins cm_popret_r15_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r15) && binsof(cp_spimm.s1);
      bins cm_popret_r15_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r15) && binsof(cp_spimm.s2);
      bins cm_popret_r15_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r15) && binsof(cp_spimm.s3);
      bins cm_popret_r4_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r4) && binsof(cp_spimm.s0);
      bins cm_popret_r4_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r4) && binsof(cp_spimm.s1);
      bins cm_popret_r4_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r4) && binsof(cp_spimm.s2);
      bins cm_popret_r4_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r4) && binsof(cp_spimm.s3);
      bins cm_popret_r5_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r5) && binsof(cp_spimm.s0);
      bins cm_popret_r5_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r5) && binsof(cp_spimm.s1);
      bins cm_popret_r5_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r5) && binsof(cp_spimm.s2);
      bins cm_popret_r5_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r5) && binsof(cp_spimm.s3);
      bins cm_popret_r6_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r6) && binsof(cp_spimm.s0);
      bins cm_popret_r6_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r6) && binsof(cp_spimm.s1);
      bins cm_popret_r6_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r6) && binsof(cp_spimm.s2);
      bins cm_popret_r6_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r6) && binsof(cp_spimm.s3);
      bins cm_popret_r7_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r7) && binsof(cp_spimm.s0);
      bins cm_popret_r7_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r7) && binsof(cp_spimm.s1);
      bins cm_popret_r7_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r7) && binsof(cp_spimm.s2);
      bins cm_popret_r7_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r7) && binsof(cp_spimm.s3);
      bins cm_popret_r8_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r8) && binsof(cp_spimm.s0);
      bins cm_popret_r8_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r8) && binsof(cp_spimm.s1);
      bins cm_popret_r8_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r8) && binsof(cp_spimm.s2);
      bins cm_popret_r8_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r8) && binsof(cp_spimm.s3);
      bins cm_popret_r9_s0= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r9) && binsof(cp_spimm.s0);
      bins cm_popret_r9_s1= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r9) && binsof(cp_spimm.s1);
      bins cm_popret_r9_s2= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r9) && binsof(cp_spimm.s2);
      bins cm_popret_r9_s3= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r9) && binsof(cp_spimm.s3);
      bins cm_popretz_r10_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r10) && binsof(cp_spimm.s0);
      bins cm_popretz_r10_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r10) && binsof(cp_spimm.s1);
      bins cm_popretz_r10_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r10) && binsof(cp_spimm.s2);
      bins cm_popretz_r10_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r10) && binsof(cp_spimm.s3);
      bins cm_popretz_r11_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r11) && binsof(cp_spimm.s0);
      bins cm_popretz_r11_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r11) && binsof(cp_spimm.s1);
      bins cm_popretz_r11_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r11) && binsof(cp_spimm.s2);
      bins cm_popretz_r11_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r11) && binsof(cp_spimm.s3);
      bins cm_popretz_r12_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r12) && binsof(cp_spimm.s0);
      bins cm_popretz_r12_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r12) && binsof(cp_spimm.s1);
      bins cm_popretz_r12_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r12) && binsof(cp_spimm.s2);
      bins cm_popretz_r12_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r12) && binsof(cp_spimm.s3);
      bins cm_popretz_r13_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r13) && binsof(cp_spimm.s0);
      bins cm_popretz_r13_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r13) && binsof(cp_spimm.s1);
      bins cm_popretz_r13_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r13) && binsof(cp_spimm.s2);
      bins cm_popretz_r13_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r13) && binsof(cp_spimm.s3);
      bins cm_popretz_r14_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r14) && binsof(cp_spimm.s0);
      bins cm_popretz_r14_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r14) && binsof(cp_spimm.s1);
      bins cm_popretz_r14_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r14) && binsof(cp_spimm.s2);
      bins cm_popretz_r14_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r14) && binsof(cp_spimm.s3);
      bins cm_popretz_r15_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r15) && binsof(cp_spimm.s0);
      bins cm_popretz_r15_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r15) && binsof(cp_spimm.s1);
      bins cm_popretz_r15_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r15) && binsof(cp_spimm.s2);
      bins cm_popretz_r15_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r15) && binsof(cp_spimm.s3);
      bins cm_popretz_r4_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r4) && binsof(cp_spimm.s0);
      bins cm_popretz_r4_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r4) && binsof(cp_spimm.s1);
      bins cm_popretz_r4_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r4) && binsof(cp_spimm.s2);
      bins cm_popretz_r4_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r4) && binsof(cp_spimm.s3);
      bins cm_popretz_r5_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r5) && binsof(cp_spimm.s0);
      bins cm_popretz_r5_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r5) && binsof(cp_spimm.s1);
      bins cm_popretz_r5_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r5) && binsof(cp_spimm.s2);
      bins cm_popretz_r5_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r5) && binsof(cp_spimm.s3);
      bins cm_popretz_r6_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r6) && binsof(cp_spimm.s0);
      bins cm_popretz_r6_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r6) && binsof(cp_spimm.s1);
      bins cm_popretz_r6_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r6) && binsof(cp_spimm.s2);
      bins cm_popretz_r6_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r6) && binsof(cp_spimm.s3);
      bins cm_popretz_r7_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r7) && binsof(cp_spimm.s0);
      bins cm_popretz_r7_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r7) && binsof(cp_spimm.s1);
      bins cm_popretz_r7_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r7) && binsof(cp_spimm.s2);
      bins cm_popretz_r7_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r7) && binsof(cp_spimm.s3);
      bins cm_popretz_r8_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r8) && binsof(cp_spimm.s0);
      bins cm_popretz_r8_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r8) && binsof(cp_spimm.s1);
      bins cm_popretz_r8_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r8) && binsof(cp_spimm.s2);
      bins cm_popretz_r8_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r8) && binsof(cp_spimm.s3);
      bins cm_popretz_r9_s0= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r9) && binsof(cp_spimm.s0);
      bins cm_popretz_r9_s1= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r9) && binsof(cp_spimm.s1);
      bins cm_popretz_r9_s2= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r9) && binsof(cp_spimm.s2);
      bins cm_popretz_r9_s3= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r9) && binsof(cp_spimm.s3);
    }
    cr_ret_align: cross cp_insn, cp_ret_align {
      bins cm_popret_half= binsof(cp_insn.cm_popret) && binsof(cp_ret_align.half);
      bins cm_popret_odd= binsof(cp_insn.cm_popret) && binsof(cp_ret_align.odd);
      bins cm_popret_word= binsof(cp_insn.cm_popret) && binsof(cp_ret_align.word);
      bins cm_popretz_half= binsof(cp_insn.cm_popretz) && binsof(cp_ret_align.half);
      bins cm_popretz_odd= binsof(cp_insn.cm_popretz) && binsof(cp_ret_align.odd);
      bins cm_popretz_word= binsof(cp_insn.cm_popretz) && binsof(cp_ret_align.word);
    }
    cr_popret_r4: cross cp_insn, cp_rlist {
      bins popret_r4= binsof(cp_insn.cm_popret) && binsof(cp_rlist.r4);
      bins popretz_r4= binsof(cp_insn.cm_popretz) && binsof(cp_rlist.r4);
    }
    cr_insn_sp_align: cross cp_insn, cp_sp_align {
      bins cm_pop_mis1= binsof(cp_insn.cm_pop) && binsof(cp_sp_align.mis1);
      bins cm_pop_mis2= binsof(cp_insn.cm_pop) && binsof(cp_sp_align.mis2);
      bins cm_pop_mis3= binsof(cp_insn.cm_pop) && binsof(cp_sp_align.mis3);
      bins cm_popret_mis1= binsof(cp_insn.cm_popret) && binsof(cp_sp_align.mis1);
      bins cm_popret_mis2= binsof(cp_insn.cm_popret) && binsof(cp_sp_align.mis2);
      bins cm_popret_mis3= binsof(cp_insn.cm_popret) && binsof(cp_sp_align.mis3);
      bins cm_popretz_mis1= binsof(cp_insn.cm_popretz) && binsof(cp_sp_align.mis1);
      bins cm_popretz_mis2= binsof(cp_insn.cm_popretz) && binsof(cp_sp_align.mis2);
      bins cm_popretz_mis3= binsof(cp_insn.cm_popretz) && binsof(cp_sp_align.mis3);
      bins cm_push_mis1= binsof(cp_insn.cm_push) && binsof(cp_sp_align.mis1);
      bins cm_push_mis2= binsof(cp_insn.cm_push) && binsof(cp_sp_align.mis2);
      bins cm_push_mis3= binsof(cp_insn.cm_push) && binsof(cp_sp_align.mis3);
      bins cm_pop_aligned= binsof(cp_insn.cm_pop) && binsof(cp_sp_align.aligned);
      bins cm_popret_aligned= binsof(cp_insn.cm_popret) && binsof(cp_sp_align.aligned);
      bins cm_popretz_aligned= binsof(cp_insn.cm_popretz) && binsof(cp_sp_align.aligned);
      bins cm_push_aligned= binsof(cp_insn.cm_push) && binsof(cp_sp_align.aligned);
    }
    cr_insn_dummy: cross cp_insn, cp_dummy_en {
      bins cm_pop_on= binsof(cp_insn.cm_pop) && binsof(cp_dummy_en.on);
      bins cm_popret_on= binsof(cp_insn.cm_popret) && binsof(cp_dummy_en.on);
      bins cm_popretz_on= binsof(cp_insn.cm_popretz) && binsof(cp_dummy_en.on);
      bins cm_push_on= binsof(cp_insn.cm_push) && binsof(cp_dummy_en.on);
      bins cm_pop_off= binsof(cp_insn.cm_pop) && binsof(cp_dummy_en.off);
      bins cm_popret_off= binsof(cp_insn.cm_popret) && binsof(cp_dummy_en.off);
      bins cm_popretz_off= binsof(cp_insn.cm_popretz) && binsof(cp_dummy_en.off);
      bins cm_push_off= binsof(cp_insn.cm_push) && binsof(cp_dummy_en.off);
    }
    cr_insn_wrap: cross cp_insn, cp_sp_wrap {
      bins pop_above_max= binsof(cp_insn.cm_pop) && binsof(cp_sp_wrap.pop_above_max);
      bins popret_above_max= binsof(cp_insn.cm_popret) && binsof(cp_sp_wrap.pop_above_max);
      bins popretz_above_max= binsof(cp_insn.cm_popretz) && binsof(cp_sp_wrap.pop_above_max);
      bins push_below_zero= binsof(cp_insn.cm_push) && binsof(cp_sp_wrap.push_below_zero);
    }
  endgroup

  // CG-CMP-007 (gen_cmp_zcmp_mv_cg), 29 coverpoint bins, 134 cross bins
  localparam int GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01 = 0;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVA01S = 1;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R1S_S0 = 0;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R1S_S1 = 1;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R1S_S2 = 2;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R1S_S3 = 3;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R1S_S4 = 4;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R1S_S5 = 5;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R1S_S6 = 6;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R1S_S7 = 7;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R2S_S0 = 0;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R2S_S1 = 1;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R2S_S2 = 2;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R2S_S3 = 3;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R2S_S4 = 4;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R2S_S5 = 5;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R2S_S6 = 6;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_R2S_S7 = 7;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_EQUAL_NO = 0;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_EQUAL_YES = 1;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_SRC_VALUES_DISTINCT = 0;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_SRC_VALUES_SAME = 1;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_B2B_MVSA01_THEN_MVA01S = 0;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_B2B_MVA01S_THEN_MVSA01 = 1;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_B2B_NONE = 2;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_LOAD_PREV = 0;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_ALU_PREV = 1;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_NONE = 2;
  localparam int GEN_FC_CMP_ZCMP_MV_CP_UOP_COUNT_OK_YES = 0;
  covergroup gen_cmp_zcmp_mv_cg with function sample(int v_cp_insn, int v_cp_r1s, int v_cp_r2s, int v_cp_equal, int v_cp_src_values, int v_cp_b2b, int v_cp_hazard_src, int v_cp_uop_count_ok);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_insn: coverpoint v_cp_insn { bins cm_mvsa01= {0}; bins cm_mva01s= {1}; ignore_bins na = {-1}; }
    cp_r1s: coverpoint v_cp_r1s { bins s0= {0}; bins s1= {1}; bins s2= {2}; bins s3= {3}; bins s4= {4}; bins s5= {5}; bins s6= {6}; bins s7= {7}; ignore_bins na = {-1}; }
    cp_r2s: coverpoint v_cp_r2s { bins s0= {0}; bins s1= {1}; bins s2= {2}; bins s3= {3}; bins s4= {4}; bins s5= {5}; bins s6= {6}; bins s7= {7}; ignore_bins na = {-1}; }
    cp_equal: coverpoint v_cp_equal { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_src_values: coverpoint v_cp_src_values { bins distinct= {0}; bins same= {1}; ignore_bins na = {-1}; }
    cp_b2b: coverpoint v_cp_b2b { bins mvsa01_then_mva01s= {0}; bins mva01s_then_mvsa01= {1}; bins none= {2}; ignore_bins na = {-1}; }
    cp_hazard_src: coverpoint v_cp_hazard_src { bins load_prev= {0}; bins alu_prev= {1}; bins none= {2}; ignore_bins na = {-1}; }
    cp_uop_count_ok: coverpoint v_cp_uop_count_ok { bins yes= {0}; ignore_bins na = {-1}; }
    cr_insn_r1_r2: cross cp_insn, cp_r1s, cp_r2s {
      bins cm_mvsa01_s0_s1= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s0) && binsof(cp_r2s.s1);
      bins cm_mvsa01_s0_s2= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s0) && binsof(cp_r2s.s2);
      bins cm_mvsa01_s0_s3= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s0) && binsof(cp_r2s.s3);
      bins cm_mvsa01_s0_s4= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s0) && binsof(cp_r2s.s4);
      bins cm_mvsa01_s0_s5= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s0) && binsof(cp_r2s.s5);
      bins cm_mvsa01_s0_s6= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s0) && binsof(cp_r2s.s6);
      bins cm_mvsa01_s0_s7= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s0) && binsof(cp_r2s.s7);
      bins cm_mvsa01_s1_s0= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s1) && binsof(cp_r2s.s0);
      bins cm_mvsa01_s1_s2= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s1) && binsof(cp_r2s.s2);
      bins cm_mvsa01_s1_s3= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s1) && binsof(cp_r2s.s3);
      bins cm_mvsa01_s1_s4= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s1) && binsof(cp_r2s.s4);
      bins cm_mvsa01_s1_s5= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s1) && binsof(cp_r2s.s5);
      bins cm_mvsa01_s1_s6= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s1) && binsof(cp_r2s.s6);
      bins cm_mvsa01_s1_s7= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s1) && binsof(cp_r2s.s7);
      bins cm_mvsa01_s2_s0= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s2) && binsof(cp_r2s.s0);
      bins cm_mvsa01_s2_s1= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s2) && binsof(cp_r2s.s1);
      bins cm_mvsa01_s2_s3= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s2) && binsof(cp_r2s.s3);
      bins cm_mvsa01_s2_s4= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s2) && binsof(cp_r2s.s4);
      bins cm_mvsa01_s2_s5= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s2) && binsof(cp_r2s.s5);
      bins cm_mvsa01_s2_s6= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s2) && binsof(cp_r2s.s6);
      bins cm_mvsa01_s2_s7= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s2) && binsof(cp_r2s.s7);
      bins cm_mvsa01_s3_s0= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s3) && binsof(cp_r2s.s0);
      bins cm_mvsa01_s3_s1= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s3) && binsof(cp_r2s.s1);
      bins cm_mvsa01_s3_s2= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s3) && binsof(cp_r2s.s2);
      bins cm_mvsa01_s3_s4= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s3) && binsof(cp_r2s.s4);
      bins cm_mvsa01_s3_s5= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s3) && binsof(cp_r2s.s5);
      bins cm_mvsa01_s3_s6= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s3) && binsof(cp_r2s.s6);
      bins cm_mvsa01_s3_s7= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s3) && binsof(cp_r2s.s7);
      bins cm_mvsa01_s4_s0= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s4) && binsof(cp_r2s.s0);
      bins cm_mvsa01_s4_s1= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s4) && binsof(cp_r2s.s1);
      bins cm_mvsa01_s4_s2= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s4) && binsof(cp_r2s.s2);
      bins cm_mvsa01_s4_s3= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s4) && binsof(cp_r2s.s3);
      bins cm_mvsa01_s4_s5= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s4) && binsof(cp_r2s.s5);
      bins cm_mvsa01_s4_s6= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s4) && binsof(cp_r2s.s6);
      bins cm_mvsa01_s4_s7= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s4) && binsof(cp_r2s.s7);
      bins cm_mvsa01_s5_s0= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s5) && binsof(cp_r2s.s0);
      bins cm_mvsa01_s5_s1= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s5) && binsof(cp_r2s.s1);
      bins cm_mvsa01_s5_s2= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s5) && binsof(cp_r2s.s2);
      bins cm_mvsa01_s5_s3= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s5) && binsof(cp_r2s.s3);
      bins cm_mvsa01_s5_s4= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s5) && binsof(cp_r2s.s4);
      bins cm_mvsa01_s5_s6= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s5) && binsof(cp_r2s.s6);
      bins cm_mvsa01_s5_s7= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s5) && binsof(cp_r2s.s7);
      bins cm_mvsa01_s6_s0= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s6) && binsof(cp_r2s.s0);
      bins cm_mvsa01_s6_s1= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s6) && binsof(cp_r2s.s1);
      bins cm_mvsa01_s6_s2= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s6) && binsof(cp_r2s.s2);
      bins cm_mvsa01_s6_s3= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s6) && binsof(cp_r2s.s3);
      bins cm_mvsa01_s6_s4= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s6) && binsof(cp_r2s.s4);
      bins cm_mvsa01_s6_s5= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s6) && binsof(cp_r2s.s5);
      bins cm_mvsa01_s6_s7= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s6) && binsof(cp_r2s.s7);
      bins cm_mvsa01_s7_s0= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s7) && binsof(cp_r2s.s0);
      bins cm_mvsa01_s7_s1= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s7) && binsof(cp_r2s.s1);
      bins cm_mvsa01_s7_s2= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s7) && binsof(cp_r2s.s2);
      bins cm_mvsa01_s7_s3= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s7) && binsof(cp_r2s.s3);
      bins cm_mvsa01_s7_s4= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s7) && binsof(cp_r2s.s4);
      bins cm_mvsa01_s7_s5= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s7) && binsof(cp_r2s.s5);
      bins cm_mvsa01_s7_s6= binsof(cp_insn.cm_mvsa01) && binsof(cp_r1s.s7) && binsof(cp_r2s.s6);
      bins cm_mva01s_s0_s0= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s0) && binsof(cp_r2s.s0);
      bins cm_mva01s_s0_s1= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s0) && binsof(cp_r2s.s1);
      bins cm_mva01s_s0_s2= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s0) && binsof(cp_r2s.s2);
      bins cm_mva01s_s0_s3= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s0) && binsof(cp_r2s.s3);
      bins cm_mva01s_s0_s4= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s0) && binsof(cp_r2s.s4);
      bins cm_mva01s_s0_s5= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s0) && binsof(cp_r2s.s5);
      bins cm_mva01s_s0_s6= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s0) && binsof(cp_r2s.s6);
      bins cm_mva01s_s0_s7= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s0) && binsof(cp_r2s.s7);
      bins cm_mva01s_s1_s0= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s1) && binsof(cp_r2s.s0);
      bins cm_mva01s_s1_s1= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s1) && binsof(cp_r2s.s1);
      bins cm_mva01s_s1_s2= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s1) && binsof(cp_r2s.s2);
      bins cm_mva01s_s1_s3= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s1) && binsof(cp_r2s.s3);
      bins cm_mva01s_s1_s4= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s1) && binsof(cp_r2s.s4);
      bins cm_mva01s_s1_s5= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s1) && binsof(cp_r2s.s5);
      bins cm_mva01s_s1_s6= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s1) && binsof(cp_r2s.s6);
      bins cm_mva01s_s1_s7= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s1) && binsof(cp_r2s.s7);
      bins cm_mva01s_s2_s0= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s2) && binsof(cp_r2s.s0);
      bins cm_mva01s_s2_s1= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s2) && binsof(cp_r2s.s1);
      bins cm_mva01s_s2_s2= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s2) && binsof(cp_r2s.s2);
      bins cm_mva01s_s2_s3= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s2) && binsof(cp_r2s.s3);
      bins cm_mva01s_s2_s4= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s2) && binsof(cp_r2s.s4);
      bins cm_mva01s_s2_s5= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s2) && binsof(cp_r2s.s5);
      bins cm_mva01s_s2_s6= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s2) && binsof(cp_r2s.s6);
      bins cm_mva01s_s2_s7= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s2) && binsof(cp_r2s.s7);
      bins cm_mva01s_s3_s0= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s3) && binsof(cp_r2s.s0);
      bins cm_mva01s_s3_s1= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s3) && binsof(cp_r2s.s1);
      bins cm_mva01s_s3_s2= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s3) && binsof(cp_r2s.s2);
      bins cm_mva01s_s3_s3= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s3) && binsof(cp_r2s.s3);
      bins cm_mva01s_s3_s4= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s3) && binsof(cp_r2s.s4);
      bins cm_mva01s_s3_s5= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s3) && binsof(cp_r2s.s5);
      bins cm_mva01s_s3_s6= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s3) && binsof(cp_r2s.s6);
      bins cm_mva01s_s3_s7= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s3) && binsof(cp_r2s.s7);
      bins cm_mva01s_s4_s0= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s4) && binsof(cp_r2s.s0);
      bins cm_mva01s_s4_s1= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s4) && binsof(cp_r2s.s1);
      bins cm_mva01s_s4_s2= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s4) && binsof(cp_r2s.s2);
      bins cm_mva01s_s4_s3= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s4) && binsof(cp_r2s.s3);
      bins cm_mva01s_s4_s4= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s4) && binsof(cp_r2s.s4);
      bins cm_mva01s_s4_s5= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s4) && binsof(cp_r2s.s5);
      bins cm_mva01s_s4_s6= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s4) && binsof(cp_r2s.s6);
      bins cm_mva01s_s4_s7= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s4) && binsof(cp_r2s.s7);
      bins cm_mva01s_s5_s0= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s5) && binsof(cp_r2s.s0);
      bins cm_mva01s_s5_s1= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s5) && binsof(cp_r2s.s1);
      bins cm_mva01s_s5_s2= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s5) && binsof(cp_r2s.s2);
      bins cm_mva01s_s5_s3= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s5) && binsof(cp_r2s.s3);
      bins cm_mva01s_s5_s4= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s5) && binsof(cp_r2s.s4);
      bins cm_mva01s_s5_s5= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s5) && binsof(cp_r2s.s5);
      bins cm_mva01s_s5_s6= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s5) && binsof(cp_r2s.s6);
      bins cm_mva01s_s5_s7= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s5) && binsof(cp_r2s.s7);
      bins cm_mva01s_s6_s0= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s6) && binsof(cp_r2s.s0);
      bins cm_mva01s_s6_s1= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s6) && binsof(cp_r2s.s1);
      bins cm_mva01s_s6_s2= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s6) && binsof(cp_r2s.s2);
      bins cm_mva01s_s6_s3= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s6) && binsof(cp_r2s.s3);
      bins cm_mva01s_s6_s4= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s6) && binsof(cp_r2s.s4);
      bins cm_mva01s_s6_s5= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s6) && binsof(cp_r2s.s5);
      bins cm_mva01s_s6_s6= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s6) && binsof(cp_r2s.s6);
      bins cm_mva01s_s6_s7= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s6) && binsof(cp_r2s.s7);
      bins cm_mva01s_s7_s0= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s7) && binsof(cp_r2s.s0);
      bins cm_mva01s_s7_s1= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s7) && binsof(cp_r2s.s1);
      bins cm_mva01s_s7_s2= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s7) && binsof(cp_r2s.s2);
      bins cm_mva01s_s7_s3= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s7) && binsof(cp_r2s.s3);
      bins cm_mva01s_s7_s4= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s7) && binsof(cp_r2s.s4);
      bins cm_mva01s_s7_s5= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s7) && binsof(cp_r2s.s5);
      bins cm_mva01s_s7_s6= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s7) && binsof(cp_r2s.s6);
      bins cm_mva01s_s7_s7= binsof(cp_insn.cm_mva01s) && binsof(cp_r1s.s7) && binsof(cp_r2s.s7);
    }
    cr_insn_equal: cross cp_insn, cp_equal {
      bins cm_mvsa01_yes= binsof(cp_insn.cm_mvsa01) && binsof(cp_equal.yes);
      bins cm_mva01s_no= binsof(cp_insn.cm_mva01s) && binsof(cp_equal.no);
      bins cm_mva01s_yes= binsof(cp_insn.cm_mva01s) && binsof(cp_equal.yes);
      bins cm_mvsa01_no= binsof(cp_insn.cm_mvsa01) && binsof(cp_equal.no);
    }
    cr_insn_b2b: cross cp_insn, cp_b2b {
      bins cm_mva01s_mva01s_then_mvsa01= binsof(cp_insn.cm_mva01s) && binsof(cp_b2b.mva01s_then_mvsa01);
      bins cm_mva01s_mvsa01_then_mva01s= binsof(cp_insn.cm_mva01s) && binsof(cp_b2b.mvsa01_then_mva01s);
      bins cm_mvsa01_mva01s_then_mvsa01= binsof(cp_insn.cm_mvsa01) && binsof(cp_b2b.mva01s_then_mvsa01);
      bins cm_mvsa01_mvsa01_then_mva01s= binsof(cp_insn.cm_mvsa01) && binsof(cp_b2b.mvsa01_then_mva01s);
    }
    cr_insn_hazard: cross cp_insn, cp_hazard_src {
      bins cm_mva01s_alu_prev= binsof(cp_insn.cm_mva01s) && binsof(cp_hazard_src.alu_prev);
      bins cm_mva01s_load_prev= binsof(cp_insn.cm_mva01s) && binsof(cp_hazard_src.load_prev);
      bins cm_mva01s_none= binsof(cp_insn.cm_mva01s) && binsof(cp_hazard_src.none);
      bins cm_mvsa01_alu_prev= binsof(cp_insn.cm_mvsa01) && binsof(cp_hazard_src.alu_prev);
      bins cm_mvsa01_load_prev= binsof(cp_insn.cm_mvsa01) && binsof(cp_hazard_src.load_prev);
      bins cm_mvsa01_none= binsof(cp_insn.cm_mvsa01) && binsof(cp_hazard_src.none);
    }
  endgroup

  // CG-CSR-002 (gen_csr_trap_setup_warl_cg), 67 coverpoint bins, 141 cross bins
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MSTATUS = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MISA = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MIE = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MTVEC = 3;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MCOUNTEREN = 4;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MSTATUSH = 5;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MENVCFG = 6;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MENVCFGH = 7;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_OP_CSRRW = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_OP_CSRRS = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_OP_CSRRC = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_OP_CSRRWI = 3;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_OP_CSRRSI = 4;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_OP_CSRRCI = 5;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_RAND = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ALL1 = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ALL0 = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_LEGAL_ONLY = 3;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ILLEGAL_ONLY = 4;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_MSB_ONLY = 5;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_RD_X0 = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_RD_NONX0 = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MPP_W_U = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MPP_W_S = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MPP_W_H = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MPP_W_M = 3;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MST_MIE_W_B0 = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MST_MIE_W_B1 = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MST_MPIE_W_B0 = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MST_MPIE_W_B1 = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MST_MPRV_W_B0 = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MST_MPRV_W_B1 = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MST_TW_W_B0 = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MST_TW_W_B1 = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_MODE_W_D00 = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_MODE_W_V01 = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_MODE_W_R10 = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_MODE_W_R11 = 3;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_LO_W_ZERO = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_LO_W_NONZERO = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_LOW = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_BOOT_PAGE = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_HIGH = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_RAND = 3;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_STD_ONLY = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_FAST_ONLY = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_STD_FAST = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_RO_ONLY = 3;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_ALL_FAST = 4;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_ON = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_OFF = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_INVALID = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_CY = 0;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_IR = 1;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM3 = 2;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM4 = 3;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM5 = 4;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM6 = 5;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM7 = 6;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM8 = 7;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM9 = 8;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM10 = 9;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM11 = 10;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM12 = 11;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_TM_RO = 12;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HI_RO = 13;
  localparam int GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_ALL1 = 14;
  covergroup gen_csr_trap_setup_warl_cg with function sample(int v_cp_csr, int v_cp_op, int v_cp_wpat, int v_cp_rd, int v_cp_mpp_w, int v_cp_mst_mie_w, int v_cp_mst_mpie_w, int v_cp_mst_mprv_w, int v_cp_mst_tw_w, int v_cp_mtvec_mode_w, int v_cp_mtvec_lo_w, int v_cp_mtvec_base_w, int v_cp_mie_w, int v_cp_mcen_gate, int v_cp_mcen_w);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_csr: coverpoint v_cp_csr { bins mstatus= {0}; bins misa= {1}; bins mie= {2}; bins mtvec= {3}; bins mcounteren= {4}; bins mstatush= {5}; bins menvcfg= {6}; bins menvcfgh= {7}; ignore_bins na = {-1}; }
    cp_op: coverpoint v_cp_op { bins csrrw= {0}; bins csrrs= {1}; bins csrrc= {2}; bins csrrwi= {3}; bins csrrsi= {4}; bins csrrci= {5}; ignore_bins na = {-1}; }
    cp_wpat: coverpoint v_cp_wpat { bins \rand = {0}; bins all1= {1}; bins all0= {2}; bins legal_only= {3}; bins illegal_only= {4}; bins msb_only= {5}; ignore_bins na = {-1}; }
    cp_rd: coverpoint v_cp_rd { bins x0= {0}; bins nonx0= {1}; ignore_bins na = {-1}; }
    cp_mpp_w: coverpoint v_cp_mpp_w { bins u= {0}; bins s= {1}; bins h= {2}; bins m= {3}; ignore_bins na = {-1}; }
    cp_mst_mie_w: coverpoint v_cp_mst_mie_w { bins b0= {0}; bins b1= {1}; ignore_bins na = {-1}; }
    cp_mst_mpie_w: coverpoint v_cp_mst_mpie_w { bins b0= {0}; bins b1= {1}; ignore_bins na = {-1}; }
    cp_mst_mprv_w: coverpoint v_cp_mst_mprv_w { bins b0= {0}; bins b1= {1}; ignore_bins na = {-1}; }
    cp_mst_tw_w: coverpoint v_cp_mst_tw_w { bins b0= {0}; bins b1= {1}; ignore_bins na = {-1}; }
    cp_mtvec_mode_w: coverpoint v_cp_mtvec_mode_w { bins d00= {0}; bins v01= {1}; bins r10= {2}; bins r11= {3}; ignore_bins na = {-1}; }
    cp_mtvec_lo_w: coverpoint v_cp_mtvec_lo_w { bins zero= {0}; bins nonzero= {1}; ignore_bins na = {-1}; }
    cp_mtvec_base_w: coverpoint v_cp_mtvec_base_w { bins low= {0}; bins boot_page= {1}; bins high= {2}; bins \rand = {3}; ignore_bins na = {-1}; }
    cp_mie_w: coverpoint v_cp_mie_w { bins std_only= {0}; bins fast_only= {1}; bins std_fast= {2}; bins ro_only= {3}; bins all_fast= {4}; ignore_bins na = {-1}; }
    cp_mcen_gate: coverpoint v_cp_mcen_gate { bins on= {0}; bins off= {1}; bins invalid= {2}; ignore_bins na = {-1}; }
    cp_mcen_w: coverpoint v_cp_mcen_w { bins cy= {0}; bins ir= {1}; bins hpm3= {2}; bins hpm4= {3}; bins hpm5= {4}; bins hpm6= {5}; bins hpm7= {6}; bins hpm8= {7}; bins hpm9= {8}; bins hpm10= {9}; bins hpm11= {10}; bins hpm12= {11}; bins tm_ro= {12}; bins hi_ro= {13}; bins all1= {14}; ignore_bins na = {-1}; }
    cr_csr_wpat: cross cp_csr, cp_wpat {
      bins mie_all0= binsof(cp_csr.mie) && binsof(cp_wpat.all0);
      bins misa_msb= binsof(cp_csr.misa) && binsof(cp_wpat.msb_only);
      bins misa_rand= binsof(cp_csr.misa) && binsof(cp_wpat.\rand );
      bins misa_all0= binsof(cp_csr.misa) && binsof(cp_wpat.all0);
      bins misa_all1= binsof(cp_csr.misa) && binsof(cp_wpat.all1);
      bins mstatus_all0= binsof(cp_csr.mstatus) && binsof(cp_wpat.all0);
      bins mstatus_illegal= binsof(cp_csr.mstatus) && binsof(cp_wpat.illegal_only);
      bins mstatus_legal= binsof(cp_csr.mstatus) && binsof(cp_wpat.legal_only);
      bins mstatus_msb= binsof(cp_csr.mstatus) && binsof(cp_wpat.msb_only);
      bins mstatus_rand= binsof(cp_csr.mstatus) && binsof(cp_wpat.\rand );
      bins mstatus_all1= binsof(cp_csr.mstatus) && binsof(cp_wpat.all1);
      bins mstatush_all0= binsof(cp_csr.mstatush) && binsof(cp_wpat.all0);
      bins mstatush_all1= binsof(cp_csr.mstatush) && binsof(cp_wpat.all1);
      bins mstatush_msb= binsof(cp_csr.mstatush) && binsof(cp_wpat.msb_only);
      bins mstatush_rand= binsof(cp_csr.mstatush) && binsof(cp_wpat.\rand );
      bins menvcfg_all0= binsof(cp_csr.menvcfg) && binsof(cp_wpat.all0);
      bins menvcfg_all1= binsof(cp_csr.menvcfg) && binsof(cp_wpat.all1);
      bins menvcfg_msb= binsof(cp_csr.menvcfg) && binsof(cp_wpat.msb_only);
      bins menvcfg_rand= binsof(cp_csr.menvcfg) && binsof(cp_wpat.\rand );
      bins menvcfgh_all0= binsof(cp_csr.menvcfgh) && binsof(cp_wpat.all0);
      bins menvcfgh_all1= binsof(cp_csr.menvcfgh) && binsof(cp_wpat.all1);
      bins menvcfgh_msb= binsof(cp_csr.menvcfgh) && binsof(cp_wpat.msb_only);
      bins menvcfgh_rand= binsof(cp_csr.menvcfgh) && binsof(cp_wpat.\rand );
      bins mie_illegal= binsof(cp_csr.mie) && binsof(cp_wpat.illegal_only);
      bins mie_legal= binsof(cp_csr.mie) && binsof(cp_wpat.legal_only);
      bins mie_msb= binsof(cp_csr.mie) && binsof(cp_wpat.msb_only);
      bins mie_rand= binsof(cp_csr.mie) && binsof(cp_wpat.\rand );
      bins mie_all1= binsof(cp_csr.mie) && binsof(cp_wpat.all1);
      bins mtvec_legal= binsof(cp_csr.mtvec) && binsof(cp_wpat.legal_only);
      bins mtvec_rand= binsof(cp_csr.mtvec) && binsof(cp_wpat.\rand );
      bins mtvec_all0= binsof(cp_csr.mtvec) && binsof(cp_wpat.all0);
      bins mtvec_all1= binsof(cp_csr.mtvec) && binsof(cp_wpat.all1);
      bins mtvec_illegal= binsof(cp_csr.mtvec) && binsof(cp_wpat.illegal_only);
      bins mtvec_msb= binsof(cp_csr.mtvec) && binsof(cp_wpat.msb_only);
      bins mcounteren_all0= binsof(cp_csr.mcounteren) && binsof(cp_wpat.all0);
      bins mcounteren_illegal= binsof(cp_csr.mcounteren) && binsof(cp_wpat.illegal_only);
      bins mcounteren_legal= binsof(cp_csr.mcounteren) && binsof(cp_wpat.legal_only);
      bins mcounteren_msb= binsof(cp_csr.mcounteren) && binsof(cp_wpat.msb_only);
      bins mcounteren_rand= binsof(cp_csr.mcounteren) && binsof(cp_wpat.\rand );
      bins mcounteren_all1= binsof(cp_csr.mcounteren) && binsof(cp_wpat.all1);
    }
    cr_csr_op: cross cp_csr, cp_op {
      bins misa_csrrc= binsof(cp_csr.misa) && binsof(cp_op.csrrc);
      bins misa_csrrci= binsof(cp_csr.misa) && binsof(cp_op.csrrci);
      bins misa_csrrs= binsof(cp_csr.misa) && binsof(cp_op.csrrs);
      bins misa_csrrsi= binsof(cp_csr.misa) && binsof(cp_op.csrrsi);
      bins misa_csrrw= binsof(cp_csr.misa) && binsof(cp_op.csrrw);
      bins misa_csrrwi= binsof(cp_csr.misa) && binsof(cp_op.csrrwi);
      bins mstatus_csrrc= binsof(cp_csr.mstatus) && binsof(cp_op.csrrc);
      bins mstatus_csrrci= binsof(cp_csr.mstatus) && binsof(cp_op.csrrci);
      bins mstatus_csrrs= binsof(cp_csr.mstatus) && binsof(cp_op.csrrs);
      bins mstatus_csrrsi= binsof(cp_csr.mstatus) && binsof(cp_op.csrrsi);
      bins mstatus_csrrw= binsof(cp_csr.mstatus) && binsof(cp_op.csrrw);
      bins mstatus_csrrwi= binsof(cp_csr.mstatus) && binsof(cp_op.csrrwi);
      bins mstatush_csrrc= binsof(cp_csr.mstatush) && binsof(cp_op.csrrc);
      bins mstatush_csrrci= binsof(cp_csr.mstatush) && binsof(cp_op.csrrci);
      bins mstatush_csrrs= binsof(cp_csr.mstatush) && binsof(cp_op.csrrs);
      bins mstatush_csrrsi= binsof(cp_csr.mstatush) && binsof(cp_op.csrrsi);
      bins mstatush_csrrw= binsof(cp_csr.mstatush) && binsof(cp_op.csrrw);
      bins mstatush_csrrwi= binsof(cp_csr.mstatush) && binsof(cp_op.csrrwi);
      bins menvcfg_csrrc= binsof(cp_csr.menvcfg) && binsof(cp_op.csrrc);
      bins menvcfg_csrrci= binsof(cp_csr.menvcfg) && binsof(cp_op.csrrci);
      bins menvcfg_csrrs= binsof(cp_csr.menvcfg) && binsof(cp_op.csrrs);
      bins menvcfg_csrrsi= binsof(cp_csr.menvcfg) && binsof(cp_op.csrrsi);
      bins menvcfg_csrrw= binsof(cp_csr.menvcfg) && binsof(cp_op.csrrw);
      bins menvcfg_csrrwi= binsof(cp_csr.menvcfg) && binsof(cp_op.csrrwi);
      bins menvcfgh_csrrc= binsof(cp_csr.menvcfgh) && binsof(cp_op.csrrc);
      bins menvcfgh_csrrci= binsof(cp_csr.menvcfgh) && binsof(cp_op.csrrci);
      bins menvcfgh_csrrs= binsof(cp_csr.menvcfgh) && binsof(cp_op.csrrs);
      bins menvcfgh_csrrsi= binsof(cp_csr.menvcfgh) && binsof(cp_op.csrrsi);
      bins menvcfgh_csrrw= binsof(cp_csr.menvcfgh) && binsof(cp_op.csrrw);
      bins menvcfgh_csrrwi= binsof(cp_csr.menvcfgh) && binsof(cp_op.csrrwi);
      bins mie_csrrc= binsof(cp_csr.mie) && binsof(cp_op.csrrc);
      bins mie_csrrci= binsof(cp_csr.mie) && binsof(cp_op.csrrci);
      bins mie_csrrs= binsof(cp_csr.mie) && binsof(cp_op.csrrs);
      bins mie_csrrsi= binsof(cp_csr.mie) && binsof(cp_op.csrrsi);
      bins mie_csrrw= binsof(cp_csr.mie) && binsof(cp_op.csrrw);
      bins mie_csrrwi= binsof(cp_csr.mie) && binsof(cp_op.csrrwi);
      bins mtvec_csrrc= binsof(cp_csr.mtvec) && binsof(cp_op.csrrc);
      bins mtvec_csrrci= binsof(cp_csr.mtvec) && binsof(cp_op.csrrci);
      bins mtvec_csrrs= binsof(cp_csr.mtvec) && binsof(cp_op.csrrs);
      bins mtvec_csrrsi= binsof(cp_csr.mtvec) && binsof(cp_op.csrrsi);
      bins mtvec_csrrw= binsof(cp_csr.mtvec) && binsof(cp_op.csrrw);
      bins mtvec_csrrwi= binsof(cp_csr.mtvec) && binsof(cp_op.csrrwi);
      bins mcounteren_csrrc= binsof(cp_csr.mcounteren) && binsof(cp_op.csrrc);
      bins mcounteren_csrrci= binsof(cp_csr.mcounteren) && binsof(cp_op.csrrci);
      bins mcounteren_csrrs= binsof(cp_csr.mcounteren) && binsof(cp_op.csrrs);
      bins mcounteren_csrrsi= binsof(cp_csr.mcounteren) && binsof(cp_op.csrrsi);
      bins mcounteren_csrrw= binsof(cp_csr.mcounteren) && binsof(cp_op.csrrw);
      bins mcounteren_csrrwi= binsof(cp_csr.mcounteren) && binsof(cp_op.csrrwi);
    }
    cr_mst_fields: cross cp_mst_mie_w, cp_mst_mpie_w, cp_mst_mprv_w, cp_mst_tw_w {
      bins all0= binsof(cp_mst_mie_w.b0) && binsof(cp_mst_mpie_w.b0) && binsof(cp_mst_mprv_w.b0) && binsof(cp_mst_tw_w.b0);
      bins mie_mpie= binsof(cp_mst_mie_w.b1) && binsof(cp_mst_mpie_w.b1) && binsof(cp_mst_mprv_w.b0) && binsof(cp_mst_tw_w.b0);
      bins mie_only= binsof(cp_mst_mie_w.b1) && binsof(cp_mst_mpie_w.b0) && binsof(cp_mst_mprv_w.b0) && binsof(cp_mst_tw_w.b0);
      bins mpie_only= binsof(cp_mst_mie_w.b0) && binsof(cp_mst_mpie_w.b1) && binsof(cp_mst_mprv_w.b0) && binsof(cp_mst_tw_w.b0);
      bins mprv_only= binsof(cp_mst_mie_w.b0) && binsof(cp_mst_mpie_w.b0) && binsof(cp_mst_mprv_w.b1) && binsof(cp_mst_tw_w.b0);
      bins mprv_tw= binsof(cp_mst_mie_w.b0) && binsof(cp_mst_mpie_w.b0) && binsof(cp_mst_mprv_w.b1) && binsof(cp_mst_tw_w.b1);
      bins tw_only= binsof(cp_mst_mie_w.b0) && binsof(cp_mst_mpie_w.b0) && binsof(cp_mst_mprv_w.b0) && binsof(cp_mst_tw_w.b1);
      bins all1= binsof(cp_mst_mie_w.b1) && binsof(cp_mst_mpie_w.b1) && binsof(cp_mst_mprv_w.b1) && binsof(cp_mst_tw_w.b1);
    }
    cr_mpp_op: cross cp_mpp_w, cp_op {
      bins mpp_h_csrrs= binsof(cp_mpp_w.h) && binsof(cp_op.csrrs);
      bins mpp_h_csrrw= binsof(cp_mpp_w.h) && binsof(cp_op.csrrw);
      bins mpp_m_csrrs= binsof(cp_mpp_w.m) && binsof(cp_op.csrrs);
      bins mpp_m_csrrw= binsof(cp_mpp_w.m) && binsof(cp_op.csrrw);
      bins mpp_s_csrrs= binsof(cp_mpp_w.s) && binsof(cp_op.csrrs);
      bins mpp_s_csrrw= binsof(cp_mpp_w.s) && binsof(cp_op.csrrw);
      bins mpp_u_csrrc= binsof(cp_mpp_w.u) && binsof(cp_op.csrrc);
      bins mpp_u_csrrw= binsof(cp_mpp_w.u) && binsof(cp_op.csrrw);
    }
    cr_mie_w_op: cross cp_mie_w, cp_op {
      bins allfast_csrrw= binsof(cp_mie_w.all_fast) && binsof(cp_op.csrrw);
      bins both_csrrw= binsof(cp_mie_w.std_fast) && binsof(cp_op.csrrw);
      bins fast_csrrc= binsof(cp_mie_w.fast_only) && binsof(cp_op.csrrc);
      bins fast_csrrs= binsof(cp_mie_w.fast_only) && binsof(cp_op.csrrs);
      bins fast_csrrw= binsof(cp_mie_w.fast_only) && binsof(cp_op.csrrw);
      bins ro_csrrw= binsof(cp_mie_w.ro_only) && binsof(cp_op.csrrw);
      bins std_csrrc= binsof(cp_mie_w.std_only) && binsof(cp_op.csrrc);
      bins std_csrrci= binsof(cp_mie_w.std_only) && binsof(cp_op.csrrci);
      bins std_csrrs= binsof(cp_mie_w.std_only) && binsof(cp_op.csrrs);
      bins std_csrrsi= binsof(cp_mie_w.std_only) && binsof(cp_op.csrrsi);
      bins std_csrrw= binsof(cp_mie_w.std_only) && binsof(cp_op.csrrw);
    }
    cr_mtvec_base_op: cross cp_mtvec_base_w, cp_op {
      bins boot_csrrw= binsof(cp_mtvec_base_w.boot_page) && binsof(cp_op.csrrw);
      bins high_csrrs= binsof(cp_mtvec_base_w.high) && binsof(cp_op.csrrs);
      bins high_csrrw= binsof(cp_mtvec_base_w.high) && binsof(cp_op.csrrw);
      bins low_csrrw= binsof(cp_mtvec_base_w.low) && binsof(cp_op.csrrw);
      bins rand_csrrc= binsof(cp_mtvec_base_w.\rand ) && binsof(cp_op.csrrc);
      bins rand_csrrs= binsof(cp_mtvec_base_w.\rand ) && binsof(cp_op.csrrs);
      bins rand_csrrw= binsof(cp_mtvec_base_w.\rand ) && binsof(cp_op.csrrw);
    }
    cr_mtvec_mode_lo: cross cp_mtvec_mode_w, cp_mtvec_lo_w {
      bins d00_nz= binsof(cp_mtvec_mode_w.d00) && binsof(cp_mtvec_lo_w.nonzero);
      bins d00_zero= binsof(cp_mtvec_mode_w.d00) && binsof(cp_mtvec_lo_w.zero);
      bins r10_nz= binsof(cp_mtvec_mode_w.r10) && binsof(cp_mtvec_lo_w.nonzero);
      bins r10_zero= binsof(cp_mtvec_mode_w.r10) && binsof(cp_mtvec_lo_w.zero);
      bins r11_nz= binsof(cp_mtvec_mode_w.r11) && binsof(cp_mtvec_lo_w.nonzero);
      bins r11_zero= binsof(cp_mtvec_mode_w.r11) && binsof(cp_mtvec_lo_w.zero);
      bins v01_nz= binsof(cp_mtvec_mode_w.v01) && binsof(cp_mtvec_lo_w.nonzero);
      bins v01_zero= binsof(cp_mtvec_mode_w.v01) && binsof(cp_mtvec_lo_w.zero);
    }
    cr_mcen_gate_w: cross cp_mcen_gate, cp_mcen_w {
      bins on_cy= binsof(cp_mcen_gate.on) && binsof(cp_mcen_w.cy);
      bins on_hi_ro= binsof(cp_mcen_gate.on) && binsof(cp_mcen_w.hi_ro);
      bins on_hpm12= binsof(cp_mcen_gate.on) && binsof(cp_mcen_w.hpm12);
      bins on_hpm3= binsof(cp_mcen_gate.on) && binsof(cp_mcen_w.hpm3);
      bins on_ir= binsof(cp_mcen_gate.on) && binsof(cp_mcen_w.ir);
      bins on_tm_ro= binsof(cp_mcen_gate.on) && binsof(cp_mcen_w.tm_ro);
      bins invalid_all1= binsof(cp_mcen_gate.invalid) && binsof(cp_mcen_w.all1);
      bins invalid_ir= binsof(cp_mcen_gate.invalid) && binsof(cp_mcen_w.ir);
      bins off_all1= binsof(cp_mcen_gate.off) && binsof(cp_mcen_w.all1);
      bins off_cy= binsof(cp_mcen_gate.off) && binsof(cp_mcen_w.cy);
      bins on_all1= binsof(cp_mcen_gate.on) && binsof(cp_mcen_w.all1);
    }
  endgroup

  // CG-ISA-007 (gen_isa_branch_cg), 28 coverpoint bins, 180 cross bins
  localparam int GEN_FC_ISA_BRANCH_CP_OP_BEQ = 0;
  localparam int GEN_FC_ISA_BRANCH_CP_OP_BNE = 1;
  localparam int GEN_FC_ISA_BRANCH_CP_OP_BLT = 2;
  localparam int GEN_FC_ISA_BRANCH_CP_OP_BGE = 3;
  localparam int GEN_FC_ISA_BRANCH_CP_OP_BLTU = 4;
  localparam int GEN_FC_ISA_BRANCH_CP_OP_BGEU = 5;
  localparam int GEN_FC_ISA_BRANCH_CP_OP_C_BEQZ = 6;
  localparam int GEN_FC_ISA_BRANCH_CP_OP_C_BNEZ = 7;
  localparam int GEN_FC_ISA_BRANCH_CP_TAKEN_NO = 0;
  localparam int GEN_FC_ISA_BRANCH_CP_TAKEN_YES = 1;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_EQUAL = 0;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_INTMIN_ZERO = 1;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ZERO_INTMIN = 2;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ZERO_ONES = 3;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ONES_ZERO = 4;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_BOTH_MSB_EQ = 5;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_SLT_UGT = 6;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_SGT_ULT = 7;
  localparam int GEN_FC_ISA_BRANCH_CP_CMP_CLASS_RAND = 8;
  localparam int GEN_FC_ISA_BRANCH_CP_OFFSET_SELF = 0;
  localparam int GEN_FC_ISA_BRANCH_CP_OFFSET_MAX_FWD = 1;
  localparam int GEN_FC_ISA_BRANCH_CP_OFFSET_MAX_BWD = 2;
  localparam int GEN_FC_ISA_BRANCH_CP_OFFSET_POS_RAND = 3;
  localparam int GEN_FC_ISA_BRANCH_CP_OFFSET_NEG_RAND = 4;
  localparam int GEN_FC_ISA_BRANCH_CP_TARGET_ALIGN_WORD = 0;
  localparam int GEN_FC_ISA_BRANCH_CP_TARGET_ALIGN_HALF = 1;
  localparam int GEN_FC_ISA_BRANCH_CP_WRAP_NO = 0;
  localparam int GEN_FC_ISA_BRANCH_CP_WRAP_YES = 1;
  covergroup gen_isa_branch_cg with function sample(int v_cp_op, int v_cp_taken, int v_cp_cmp_class, int v_cp_offset, int v_cp_target_align, int v_cp_wrap);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins beq= {0}; bins bne= {1}; bins blt= {2}; bins bge= {3}; bins bltu= {4}; bins bgeu= {5}; bins c_beqz= {6}; bins c_bnez= {7}; ignore_bins na = {-1}; }
    cp_taken: coverpoint v_cp_taken { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_cmp_class: coverpoint v_cp_cmp_class { bins equal= {0}; bins intmin_zero= {1}; bins zero_intmin= {2}; bins zero_ones= {3}; bins ones_zero= {4}; bins both_msb_eq= {5}; bins slt_ugt= {6}; bins sgt_ult= {7}; bins \rand = {8}; ignore_bins na = {-1}; }
    cp_offset: coverpoint v_cp_offset { bins self= {0}; bins max_fwd= {1}; bins max_bwd= {2}; bins pos_rand= {3}; bins neg_rand= {4}; ignore_bins na = {-1}; }
    cp_target_align: coverpoint v_cp_target_align { bins word= {0}; bins half= {1}; ignore_bins na = {-1}; }
    cp_wrap: coverpoint v_cp_wrap { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cr_wrap: cross cp_op, cp_wrap {
      bins beq_yes= binsof(cp_op.beq) && binsof(cp_wrap.yes);
      bins bge_yes= binsof(cp_op.bge) && binsof(cp_wrap.yes);
      bins bgeu_yes= binsof(cp_op.bgeu) && binsof(cp_wrap.yes);
      bins blt_yes= binsof(cp_op.blt) && binsof(cp_wrap.yes);
      bins bltu_yes= binsof(cp_op.bltu) && binsof(cp_wrap.yes);
      bins bne_yes= binsof(cp_op.bne) && binsof(cp_wrap.yes);
      bins c_beqz_yes= binsof(cp_op.c_beqz) && binsof(cp_wrap.yes);
      bins c_bnez_yes= binsof(cp_op.c_bnez) && binsof(cp_wrap.yes);
      bins c_beqz_no= binsof(cp_op.c_beqz) && binsof(cp_wrap.no);
      bins c_bnez_no= binsof(cp_op.c_bnez) && binsof(cp_wrap.no);
      bins beq_no= binsof(cp_op.beq) && binsof(cp_wrap.no);
      bins bge_no= binsof(cp_op.bge) && binsof(cp_wrap.no);
      bins bgeu_no= binsof(cp_op.bgeu) && binsof(cp_wrap.no);
      bins blt_no= binsof(cp_op.blt) && binsof(cp_wrap.no);
      bins bltu_no= binsof(cp_op.bltu) && binsof(cp_wrap.no);
      bins bne_no= binsof(cp_op.bne) && binsof(cp_wrap.no);
    }
    cr_op_align: cross cp_op, cp_target_align {
      bins c_beqz_half= binsof(cp_op.c_beqz) && binsof(cp_target_align.half);
      bins c_beqz_word= binsof(cp_op.c_beqz) && binsof(cp_target_align.word);
      bins c_bnez_half= binsof(cp_op.c_bnez) && binsof(cp_target_align.half);
      bins c_bnez_word= binsof(cp_op.c_bnez) && binsof(cp_target_align.word);
      bins beq_half= binsof(cp_op.beq) && binsof(cp_target_align.half);
      bins beq_word= binsof(cp_op.beq) && binsof(cp_target_align.word);
      bins bge_half= binsof(cp_op.bge) && binsof(cp_target_align.half);
      bins bge_word= binsof(cp_op.bge) && binsof(cp_target_align.word);
      bins bgeu_half= binsof(cp_op.bgeu) && binsof(cp_target_align.half);
      bins bgeu_word= binsof(cp_op.bgeu) && binsof(cp_target_align.word);
      bins blt_half= binsof(cp_op.blt) && binsof(cp_target_align.half);
      bins blt_word= binsof(cp_op.blt) && binsof(cp_target_align.word);
      bins bltu_half= binsof(cp_op.bltu) && binsof(cp_target_align.half);
      bins bltu_word= binsof(cp_op.bltu) && binsof(cp_target_align.word);
      bins bne_half= binsof(cp_op.bne) && binsof(cp_target_align.half);
      bins bne_word= binsof(cp_op.bne) && binsof(cp_target_align.word);
    }
    cr_op_offset_taken: cross cp_op, cp_offset, cp_taken {
      bins c_beqz_neg_rand_no= binsof(cp_op.c_beqz) && binsof(cp_offset.neg_rand) && binsof(cp_taken.no);
      bins c_beqz_neg_rand_yes= binsof(cp_op.c_beqz) && binsof(cp_offset.neg_rand) && binsof(cp_taken.yes);
      bins c_beqz_pos_rand_no= binsof(cp_op.c_beqz) && binsof(cp_offset.pos_rand) && binsof(cp_taken.no);
      bins c_beqz_pos_rand_yes= binsof(cp_op.c_beqz) && binsof(cp_offset.pos_rand) && binsof(cp_taken.yes);
      bins c_bnez_neg_rand_no= binsof(cp_op.c_bnez) && binsof(cp_offset.neg_rand) && binsof(cp_taken.no);
      bins c_bnez_neg_rand_yes= binsof(cp_op.c_bnez) && binsof(cp_offset.neg_rand) && binsof(cp_taken.yes);
      bins c_bnez_pos_rand_no= binsof(cp_op.c_bnez) && binsof(cp_offset.pos_rand) && binsof(cp_taken.no);
      bins c_bnez_pos_rand_yes= binsof(cp_op.c_bnez) && binsof(cp_offset.pos_rand) && binsof(cp_taken.yes);
      bins beq_neg_rand_no= binsof(cp_op.beq) && binsof(cp_offset.neg_rand) && binsof(cp_taken.no);
      bins beq_neg_rand_yes= binsof(cp_op.beq) && binsof(cp_offset.neg_rand) && binsof(cp_taken.yes);
      bins beq_pos_rand_no= binsof(cp_op.beq) && binsof(cp_offset.pos_rand) && binsof(cp_taken.no);
      bins beq_pos_rand_yes= binsof(cp_op.beq) && binsof(cp_offset.pos_rand) && binsof(cp_taken.yes);
      bins bge_neg_rand_no= binsof(cp_op.bge) && binsof(cp_offset.neg_rand) && binsof(cp_taken.no);
      bins bge_neg_rand_yes= binsof(cp_op.bge) && binsof(cp_offset.neg_rand) && binsof(cp_taken.yes);
      bins bge_pos_rand_no= binsof(cp_op.bge) && binsof(cp_offset.pos_rand) && binsof(cp_taken.no);
      bins bge_pos_rand_yes= binsof(cp_op.bge) && binsof(cp_offset.pos_rand) && binsof(cp_taken.yes);
      bins bgeu_neg_rand_no= binsof(cp_op.bgeu) && binsof(cp_offset.neg_rand) && binsof(cp_taken.no);
      bins bgeu_neg_rand_yes= binsof(cp_op.bgeu) && binsof(cp_offset.neg_rand) && binsof(cp_taken.yes);
      bins bgeu_pos_rand_no= binsof(cp_op.bgeu) && binsof(cp_offset.pos_rand) && binsof(cp_taken.no);
      bins bgeu_pos_rand_yes= binsof(cp_op.bgeu) && binsof(cp_offset.pos_rand) && binsof(cp_taken.yes);
      bins blt_neg_rand_no= binsof(cp_op.blt) && binsof(cp_offset.neg_rand) && binsof(cp_taken.no);
      bins blt_neg_rand_yes= binsof(cp_op.blt) && binsof(cp_offset.neg_rand) && binsof(cp_taken.yes);
      bins blt_pos_rand_no= binsof(cp_op.blt) && binsof(cp_offset.pos_rand) && binsof(cp_taken.no);
      bins blt_pos_rand_yes= binsof(cp_op.blt) && binsof(cp_offset.pos_rand) && binsof(cp_taken.yes);
      bins bltu_neg_rand_no= binsof(cp_op.bltu) && binsof(cp_offset.neg_rand) && binsof(cp_taken.no);
      bins bltu_neg_rand_yes= binsof(cp_op.bltu) && binsof(cp_offset.neg_rand) && binsof(cp_taken.yes);
      bins bltu_pos_rand_no= binsof(cp_op.bltu) && binsof(cp_offset.pos_rand) && binsof(cp_taken.no);
      bins bltu_pos_rand_yes= binsof(cp_op.bltu) && binsof(cp_offset.pos_rand) && binsof(cp_taken.yes);
      bins bne_neg_rand_no= binsof(cp_op.bne) && binsof(cp_offset.neg_rand) && binsof(cp_taken.no);
      bins bne_neg_rand_yes= binsof(cp_op.bne) && binsof(cp_offset.neg_rand) && binsof(cp_taken.yes);
      bins bne_pos_rand_no= binsof(cp_op.bne) && binsof(cp_offset.pos_rand) && binsof(cp_taken.no);
      bins bne_pos_rand_yes= binsof(cp_op.bne) && binsof(cp_offset.pos_rand) && binsof(cp_taken.yes);
      bins beq_max_bwd_no= binsof(cp_op.beq) && binsof(cp_offset.max_bwd) && binsof(cp_taken.no);
      bins beq_max_bwd_yes= binsof(cp_op.beq) && binsof(cp_offset.max_bwd) && binsof(cp_taken.yes);
      bins beq_max_fwd_no= binsof(cp_op.beq) && binsof(cp_offset.max_fwd) && binsof(cp_taken.no);
      bins beq_max_fwd_yes= binsof(cp_op.beq) && binsof(cp_offset.max_fwd) && binsof(cp_taken.yes);
      bins beq_self_no= binsof(cp_op.beq) && binsof(cp_offset.self) && binsof(cp_taken.no);
      bins beq_self_yes= binsof(cp_op.beq) && binsof(cp_offset.self) && binsof(cp_taken.yes);
      bins bge_max_bwd_no= binsof(cp_op.bge) && binsof(cp_offset.max_bwd) && binsof(cp_taken.no);
      bins bge_max_bwd_yes= binsof(cp_op.bge) && binsof(cp_offset.max_bwd) && binsof(cp_taken.yes);
      bins bge_max_fwd_no= binsof(cp_op.bge) && binsof(cp_offset.max_fwd) && binsof(cp_taken.no);
      bins bge_max_fwd_yes= binsof(cp_op.bge) && binsof(cp_offset.max_fwd) && binsof(cp_taken.yes);
      bins bge_self_no= binsof(cp_op.bge) && binsof(cp_offset.self) && binsof(cp_taken.no);
      bins bge_self_yes= binsof(cp_op.bge) && binsof(cp_offset.self) && binsof(cp_taken.yes);
      bins bgeu_max_bwd_no= binsof(cp_op.bgeu) && binsof(cp_offset.max_bwd) && binsof(cp_taken.no);
      bins bgeu_max_bwd_yes= binsof(cp_op.bgeu) && binsof(cp_offset.max_bwd) && binsof(cp_taken.yes);
      bins bgeu_max_fwd_no= binsof(cp_op.bgeu) && binsof(cp_offset.max_fwd) && binsof(cp_taken.no);
      bins bgeu_max_fwd_yes= binsof(cp_op.bgeu) && binsof(cp_offset.max_fwd) && binsof(cp_taken.yes);
      bins bgeu_self_no= binsof(cp_op.bgeu) && binsof(cp_offset.self) && binsof(cp_taken.no);
      bins bgeu_self_yes= binsof(cp_op.bgeu) && binsof(cp_offset.self) && binsof(cp_taken.yes);
      bins blt_max_bwd_no= binsof(cp_op.blt) && binsof(cp_offset.max_bwd) && binsof(cp_taken.no);
      bins blt_max_bwd_yes= binsof(cp_op.blt) && binsof(cp_offset.max_bwd) && binsof(cp_taken.yes);
      bins blt_max_fwd_no= binsof(cp_op.blt) && binsof(cp_offset.max_fwd) && binsof(cp_taken.no);
      bins blt_max_fwd_yes= binsof(cp_op.blt) && binsof(cp_offset.max_fwd) && binsof(cp_taken.yes);
      bins blt_self_no= binsof(cp_op.blt) && binsof(cp_offset.self) && binsof(cp_taken.no);
      bins blt_self_yes= binsof(cp_op.blt) && binsof(cp_offset.self) && binsof(cp_taken.yes);
      bins bltu_max_bwd_no= binsof(cp_op.bltu) && binsof(cp_offset.max_bwd) && binsof(cp_taken.no);
      bins bltu_max_bwd_yes= binsof(cp_op.bltu) && binsof(cp_offset.max_bwd) && binsof(cp_taken.yes);
      bins bltu_max_fwd_no= binsof(cp_op.bltu) && binsof(cp_offset.max_fwd) && binsof(cp_taken.no);
      bins bltu_max_fwd_yes= binsof(cp_op.bltu) && binsof(cp_offset.max_fwd) && binsof(cp_taken.yes);
      bins bltu_self_no= binsof(cp_op.bltu) && binsof(cp_offset.self) && binsof(cp_taken.no);
      bins bltu_self_yes= binsof(cp_op.bltu) && binsof(cp_offset.self) && binsof(cp_taken.yes);
      bins bne_max_bwd_no= binsof(cp_op.bne) && binsof(cp_offset.max_bwd) && binsof(cp_taken.no);
      bins bne_max_bwd_yes= binsof(cp_op.bne) && binsof(cp_offset.max_bwd) && binsof(cp_taken.yes);
      bins bne_max_fwd_no= binsof(cp_op.bne) && binsof(cp_offset.max_fwd) && binsof(cp_taken.no);
      bins bne_max_fwd_yes= binsof(cp_op.bne) && binsof(cp_offset.max_fwd) && binsof(cp_taken.yes);
      bins bne_self_no= binsof(cp_op.bne) && binsof(cp_offset.self) && binsof(cp_taken.no);
      bins bne_self_yes= binsof(cp_op.bne) && binsof(cp_offset.self) && binsof(cp_taken.yes);
      bins c_beqz_max_bwd_no= binsof(cp_op.c_beqz) && binsof(cp_offset.max_bwd) && binsof(cp_taken.no);
      bins c_beqz_max_bwd_yes= binsof(cp_op.c_beqz) && binsof(cp_offset.max_bwd) && binsof(cp_taken.yes);
      bins c_beqz_max_fwd_no= binsof(cp_op.c_beqz) && binsof(cp_offset.max_fwd) && binsof(cp_taken.no);
      bins c_beqz_max_fwd_yes= binsof(cp_op.c_beqz) && binsof(cp_offset.max_fwd) && binsof(cp_taken.yes);
      bins c_beqz_self_no= binsof(cp_op.c_beqz) && binsof(cp_offset.self) && binsof(cp_taken.no);
      bins c_beqz_self_yes= binsof(cp_op.c_beqz) && binsof(cp_offset.self) && binsof(cp_taken.yes);
      bins c_bnez_max_bwd_no= binsof(cp_op.c_bnez) && binsof(cp_offset.max_bwd) && binsof(cp_taken.no);
      bins c_bnez_max_bwd_yes= binsof(cp_op.c_bnez) && binsof(cp_offset.max_bwd) && binsof(cp_taken.yes);
      bins c_bnez_max_fwd_no= binsof(cp_op.c_bnez) && binsof(cp_offset.max_fwd) && binsof(cp_taken.no);
      bins c_bnez_max_fwd_yes= binsof(cp_op.c_bnez) && binsof(cp_offset.max_fwd) && binsof(cp_taken.yes);
      bins c_bnez_self_no= binsof(cp_op.c_bnez) && binsof(cp_offset.self) && binsof(cp_taken.no);
      bins c_bnez_self_yes= binsof(cp_op.c_bnez) && binsof(cp_offset.self) && binsof(cp_taken.yes);
    }
    cr_op_taken_cmp: cross cp_op, cp_taken, cp_cmp_class {
      bins beq_no_intmin_zero= binsof(cp_op.beq) && binsof(cp_taken.no) && binsof(cp_cmp_class.intmin_zero);
      bins beq_no_ones_zero= binsof(cp_op.beq) && binsof(cp_taken.no) && binsof(cp_cmp_class.ones_zero);
      bins beq_no_rand= binsof(cp_op.beq) && binsof(cp_taken.no) && binsof(cp_cmp_class.\rand );
      bins beq_no_sgt_ult= binsof(cp_op.beq) && binsof(cp_taken.no) && binsof(cp_cmp_class.sgt_ult);
      bins beq_no_slt_ugt= binsof(cp_op.beq) && binsof(cp_taken.no) && binsof(cp_cmp_class.slt_ugt);
      bins beq_no_zero_intmin= binsof(cp_op.beq) && binsof(cp_taken.no) && binsof(cp_cmp_class.zero_intmin);
      bins beq_no_zero_ones= binsof(cp_op.beq) && binsof(cp_taken.no) && binsof(cp_cmp_class.zero_ones);
      bins beq_yes_both_msb_eq= binsof(cp_op.beq) && binsof(cp_taken.yes) && binsof(cp_cmp_class.both_msb_eq);
      bins beq_yes_equal= binsof(cp_op.beq) && binsof(cp_taken.yes) && binsof(cp_cmp_class.equal);
      bins bge_no_intmin_zero= binsof(cp_op.bge) && binsof(cp_taken.no) && binsof(cp_cmp_class.intmin_zero);
      bins bge_no_ones_zero= binsof(cp_op.bge) && binsof(cp_taken.no) && binsof(cp_cmp_class.ones_zero);
      bins bge_no_rand= binsof(cp_op.bge) && binsof(cp_taken.no) && binsof(cp_cmp_class.\rand );
      bins bge_no_slt_ugt= binsof(cp_op.bge) && binsof(cp_taken.no) && binsof(cp_cmp_class.slt_ugt);
      bins bge_yes_both_msb_eq= binsof(cp_op.bge) && binsof(cp_taken.yes) && binsof(cp_cmp_class.both_msb_eq);
      bins bge_yes_equal= binsof(cp_op.bge) && binsof(cp_taken.yes) && binsof(cp_cmp_class.equal);
      bins bge_yes_rand= binsof(cp_op.bge) && binsof(cp_taken.yes) && binsof(cp_cmp_class.\rand );
      bins bge_yes_sgt_ult= binsof(cp_op.bge) && binsof(cp_taken.yes) && binsof(cp_cmp_class.sgt_ult);
      bins bge_yes_zero_intmin= binsof(cp_op.bge) && binsof(cp_taken.yes) && binsof(cp_cmp_class.zero_intmin);
      bins bge_yes_zero_ones= binsof(cp_op.bge) && binsof(cp_taken.yes) && binsof(cp_cmp_class.zero_ones);
      bins bgeu_no_rand= binsof(cp_op.bgeu) && binsof(cp_taken.no) && binsof(cp_cmp_class.\rand );
      bins bgeu_no_sgt_ult= binsof(cp_op.bgeu) && binsof(cp_taken.no) && binsof(cp_cmp_class.sgt_ult);
      bins bgeu_no_zero_intmin= binsof(cp_op.bgeu) && binsof(cp_taken.no) && binsof(cp_cmp_class.zero_intmin);
      bins bgeu_no_zero_ones= binsof(cp_op.bgeu) && binsof(cp_taken.no) && binsof(cp_cmp_class.zero_ones);
      bins bgeu_yes_both_msb_eq= binsof(cp_op.bgeu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.both_msb_eq);
      bins bgeu_yes_equal= binsof(cp_op.bgeu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.equal);
      bins bgeu_yes_intmin_zero= binsof(cp_op.bgeu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.intmin_zero);
      bins bgeu_yes_ones_zero= binsof(cp_op.bgeu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.ones_zero);
      bins bgeu_yes_rand= binsof(cp_op.bgeu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.\rand );
      bins bgeu_yes_slt_ugt= binsof(cp_op.bgeu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.slt_ugt);
      bins blt_no_both_msb_eq= binsof(cp_op.blt) && binsof(cp_taken.no) && binsof(cp_cmp_class.both_msb_eq);
      bins blt_no_equal= binsof(cp_op.blt) && binsof(cp_taken.no) && binsof(cp_cmp_class.equal);
      bins blt_no_rand= binsof(cp_op.blt) && binsof(cp_taken.no) && binsof(cp_cmp_class.\rand );
      bins blt_no_sgt_ult= binsof(cp_op.blt) && binsof(cp_taken.no) && binsof(cp_cmp_class.sgt_ult);
      bins blt_no_zero_intmin= binsof(cp_op.blt) && binsof(cp_taken.no) && binsof(cp_cmp_class.zero_intmin);
      bins blt_no_zero_ones= binsof(cp_op.blt) && binsof(cp_taken.no) && binsof(cp_cmp_class.zero_ones);
      bins blt_yes_intmin_zero= binsof(cp_op.blt) && binsof(cp_taken.yes) && binsof(cp_cmp_class.intmin_zero);
      bins blt_yes_ones_zero= binsof(cp_op.blt) && binsof(cp_taken.yes) && binsof(cp_cmp_class.ones_zero);
      bins blt_yes_rand= binsof(cp_op.blt) && binsof(cp_taken.yes) && binsof(cp_cmp_class.\rand );
      bins blt_yes_slt_ugt= binsof(cp_op.blt) && binsof(cp_taken.yes) && binsof(cp_cmp_class.slt_ugt);
      bins bltu_no_both_msb_eq= binsof(cp_op.bltu) && binsof(cp_taken.no) && binsof(cp_cmp_class.both_msb_eq);
      bins bltu_no_equal= binsof(cp_op.bltu) && binsof(cp_taken.no) && binsof(cp_cmp_class.equal);
      bins bltu_no_intmin_zero= binsof(cp_op.bltu) && binsof(cp_taken.no) && binsof(cp_cmp_class.intmin_zero);
      bins bltu_no_ones_zero= binsof(cp_op.bltu) && binsof(cp_taken.no) && binsof(cp_cmp_class.ones_zero);
      bins bltu_no_rand= binsof(cp_op.bltu) && binsof(cp_taken.no) && binsof(cp_cmp_class.\rand );
      bins bltu_no_slt_ugt= binsof(cp_op.bltu) && binsof(cp_taken.no) && binsof(cp_cmp_class.slt_ugt);
      bins bltu_yes_rand= binsof(cp_op.bltu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.\rand );
      bins bltu_yes_sgt_ult= binsof(cp_op.bltu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.sgt_ult);
      bins bltu_yes_zero_intmin= binsof(cp_op.bltu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.zero_intmin);
      bins bltu_yes_zero_ones= binsof(cp_op.bltu) && binsof(cp_taken.yes) && binsof(cp_cmp_class.zero_ones);
      bins bne_no_both_msb_eq= binsof(cp_op.bne) && binsof(cp_taken.no) && binsof(cp_cmp_class.both_msb_eq);
      bins bne_no_equal= binsof(cp_op.bne) && binsof(cp_taken.no) && binsof(cp_cmp_class.equal);
      bins bne_yes_intmin_zero= binsof(cp_op.bne) && binsof(cp_taken.yes) && binsof(cp_cmp_class.intmin_zero);
      bins bne_yes_ones_zero= binsof(cp_op.bne) && binsof(cp_taken.yes) && binsof(cp_cmp_class.ones_zero);
      bins bne_yes_rand= binsof(cp_op.bne) && binsof(cp_taken.yes) && binsof(cp_cmp_class.\rand );
      bins bne_yes_sgt_ult= binsof(cp_op.bne) && binsof(cp_taken.yes) && binsof(cp_cmp_class.sgt_ult);
      bins bne_yes_slt_ugt= binsof(cp_op.bne) && binsof(cp_taken.yes) && binsof(cp_cmp_class.slt_ugt);
      bins bne_yes_zero_intmin= binsof(cp_op.bne) && binsof(cp_taken.yes) && binsof(cp_cmp_class.zero_intmin);
      bins bne_yes_zero_ones= binsof(cp_op.bne) && binsof(cp_taken.yes) && binsof(cp_cmp_class.zero_ones);
      bins c_beqz_no_intmin_zero= binsof(cp_op.c_beqz) && binsof(cp_taken.no) && binsof(cp_cmp_class.intmin_zero);
      bins c_beqz_no_ones_zero= binsof(cp_op.c_beqz) && binsof(cp_taken.no) && binsof(cp_cmp_class.ones_zero);
      bins c_beqz_no_slt_ugt= binsof(cp_op.c_beqz) && binsof(cp_taken.no) && binsof(cp_cmp_class.slt_ugt);
      bins c_beqz_yes_equal= binsof(cp_op.c_beqz) && binsof(cp_taken.yes) && binsof(cp_cmp_class.equal);
      bins c_bnez_no_equal= binsof(cp_op.c_bnez) && binsof(cp_taken.no) && binsof(cp_cmp_class.equal);
      bins c_bnez_yes_intmin_zero= binsof(cp_op.c_bnez) && binsof(cp_taken.yes) && binsof(cp_cmp_class.intmin_zero);
      bins c_bnez_yes_ones_zero= binsof(cp_op.c_bnez) && binsof(cp_taken.yes) && binsof(cp_cmp_class.ones_zero);
      bins c_bnez_yes_slt_ugt= binsof(cp_op.c_bnez) && binsof(cp_taken.yes) && binsof(cp_cmp_class.slt_ugt);
      bins c_beqz_no_rand= binsof(cp_op.c_beqz) && binsof(cp_taken.no) && binsof(cp_cmp_class.\rand );
      bins c_bnez_yes_rand= binsof(cp_op.c_bnez) && binsof(cp_taken.yes) && binsof(cp_cmp_class.\rand );
    }
  endgroup

  // CG-BIT-006 (gen_bit_sbit_cg), 22 coverpoint bins, 100 cross bins
  localparam int GEN_FC_BIT_SBIT_CP_OP_BCLR = 0;
  localparam int GEN_FC_BIT_SBIT_CP_OP_BSET = 1;
  localparam int GEN_FC_BIT_SBIT_CP_OP_BINV = 2;
  localparam int GEN_FC_BIT_SBIT_CP_OP_BEXT = 3;
  localparam int GEN_FC_BIT_SBIT_CP_OP_BCLRI = 4;
  localparam int GEN_FC_BIT_SBIT_CP_OP_BSETI = 5;
  localparam int GEN_FC_BIT_SBIT_CP_OP_BINVI = 6;
  localparam int GEN_FC_BIT_SBIT_CP_OP_BEXTI = 7;
  localparam int GEN_FC_BIT_SBIT_CP_INDEX_I0 = 0;
  localparam int GEN_FC_BIT_SBIT_CP_INDEX_MID = 1;
  localparam int GEN_FC_BIT_SBIT_CP_INDEX_I31 = 2;
  localparam int GEN_FC_BIT_SBIT_CP_RS2_UPPER_ZERO = 0;
  localparam int GEN_FC_BIT_SBIT_CP_RS2_UPPER_ALL_ONES = 1;
  localparam int GEN_FC_BIT_SBIT_CP_RS2_UPPER_OTHER_NONZERO = 2;
  localparam int GEN_FC_BIT_SBIT_CP_PRIOR_BIT_CLEAR = 0;
  localparam int GEN_FC_BIT_SBIT_CP_PRIOR_BIT_SET = 1;
  localparam int GEN_FC_BIT_SBIT_CP_OPERAND_ZERO = 0;
  localparam int GEN_FC_BIT_SBIT_CP_OPERAND_ALL_ONES = 1;
  localparam int GEN_FC_BIT_SBIT_CP_OPERAND_RAND = 2;
  localparam int GEN_FC_BIT_SBIT_CP_RD_X0_NO = 0;
  localparam int GEN_FC_BIT_SBIT_CP_RD_X0_YES = 1;
  localparam int GEN_FC_BIT_SBIT_CP_BINV_TWICE_YES = 0;
  covergroup gen_bit_sbit_cg with function sample(int v_cp_op, int v_cp_index, int v_cp_rs2_upper, int v_cp_prior_bit, int v_cp_operand, int v_cp_rd_x0, int v_cp_binv_twice);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins bclr= {0}; bins bset= {1}; bins binv= {2}; bins bext= {3}; bins bclri= {4}; bins bseti= {5}; bins binvi= {6}; bins bexti= {7}; ignore_bins na = {-1}; }
    cp_index: coverpoint v_cp_index { bins i0= {0}; bins mid= {1}; bins i31= {2}; ignore_bins na = {-1}; }
    cp_rs2_upper: coverpoint v_cp_rs2_upper { bins zero= {0}; bins all_ones= {1}; bins other_nonzero= {2}; ignore_bins na = {-1}; }
    cp_prior_bit: coverpoint v_cp_prior_bit { bins clear= {0}; bins set= {1}; ignore_bins na = {-1}; }
    cp_operand: coverpoint v_cp_operand { bins zero= {0}; bins all_ones= {1}; bins \rand = {2}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_binv_twice: coverpoint v_cp_binv_twice { bins yes= {0}; ignore_bins na = {-1}; }
    cr_op_index_prior: cross cp_op, cp_index, cp_prior_bit {
      bins bclr_i0_clear= binsof(cp_op.bclr) && binsof(cp_index.i0) && binsof(cp_prior_bit.clear);
      bins bclr_i0_set= binsof(cp_op.bclr) && binsof(cp_index.i0) && binsof(cp_prior_bit.set);
      bins bclr_i31_clear= binsof(cp_op.bclr) && binsof(cp_index.i31) && binsof(cp_prior_bit.clear);
      bins bclr_i31_set= binsof(cp_op.bclr) && binsof(cp_index.i31) && binsof(cp_prior_bit.set);
      bins bclr_mid_clear= binsof(cp_op.bclr) && binsof(cp_index.mid) && binsof(cp_prior_bit.clear);
      bins bclr_mid_set= binsof(cp_op.bclr) && binsof(cp_index.mid) && binsof(cp_prior_bit.set);
      bins bext_i0_clear= binsof(cp_op.bext) && binsof(cp_index.i0) && binsof(cp_prior_bit.clear);
      bins bext_i0_set= binsof(cp_op.bext) && binsof(cp_index.i0) && binsof(cp_prior_bit.set);
      bins bext_i31_clear= binsof(cp_op.bext) && binsof(cp_index.i31) && binsof(cp_prior_bit.clear);
      bins bext_i31_set= binsof(cp_op.bext) && binsof(cp_index.i31) && binsof(cp_prior_bit.set);
      bins bext_mid_clear= binsof(cp_op.bext) && binsof(cp_index.mid) && binsof(cp_prior_bit.clear);
      bins bext_mid_set= binsof(cp_op.bext) && binsof(cp_index.mid) && binsof(cp_prior_bit.set);
      bins binv_i0_clear= binsof(cp_op.binv) && binsof(cp_index.i0) && binsof(cp_prior_bit.clear);
      bins binv_i0_set= binsof(cp_op.binv) && binsof(cp_index.i0) && binsof(cp_prior_bit.set);
      bins binv_i31_clear= binsof(cp_op.binv) && binsof(cp_index.i31) && binsof(cp_prior_bit.clear);
      bins binv_i31_set= binsof(cp_op.binv) && binsof(cp_index.i31) && binsof(cp_prior_bit.set);
      bins binv_mid_clear= binsof(cp_op.binv) && binsof(cp_index.mid) && binsof(cp_prior_bit.clear);
      bins binv_mid_set= binsof(cp_op.binv) && binsof(cp_index.mid) && binsof(cp_prior_bit.set);
      bins bset_i0_clear= binsof(cp_op.bset) && binsof(cp_index.i0) && binsof(cp_prior_bit.clear);
      bins bset_i0_set= binsof(cp_op.bset) && binsof(cp_index.i0) && binsof(cp_prior_bit.set);
      bins bset_i31_clear= binsof(cp_op.bset) && binsof(cp_index.i31) && binsof(cp_prior_bit.clear);
      bins bset_i31_set= binsof(cp_op.bset) && binsof(cp_index.i31) && binsof(cp_prior_bit.set);
      bins bset_mid_clear= binsof(cp_op.bset) && binsof(cp_index.mid) && binsof(cp_prior_bit.clear);
      bins bset_mid_set= binsof(cp_op.bset) && binsof(cp_index.mid) && binsof(cp_prior_bit.set);
      bins bclri_i0_clear= binsof(cp_op.bclri) && binsof(cp_index.i0) && binsof(cp_prior_bit.clear);
      bins bclri_i0_set= binsof(cp_op.bclri) && binsof(cp_index.i0) && binsof(cp_prior_bit.set);
      bins bclri_i31_clear= binsof(cp_op.bclri) && binsof(cp_index.i31) && binsof(cp_prior_bit.clear);
      bins bclri_i31_set= binsof(cp_op.bclri) && binsof(cp_index.i31) && binsof(cp_prior_bit.set);
      bins bclri_mid_clear= binsof(cp_op.bclri) && binsof(cp_index.mid) && binsof(cp_prior_bit.clear);
      bins bclri_mid_set= binsof(cp_op.bclri) && binsof(cp_index.mid) && binsof(cp_prior_bit.set);
      bins bexti_i0_clear= binsof(cp_op.bexti) && binsof(cp_index.i0) && binsof(cp_prior_bit.clear);
      bins bexti_i0_set= binsof(cp_op.bexti) && binsof(cp_index.i0) && binsof(cp_prior_bit.set);
      bins bexti_i31_clear= binsof(cp_op.bexti) && binsof(cp_index.i31) && binsof(cp_prior_bit.clear);
      bins bexti_i31_set= binsof(cp_op.bexti) && binsof(cp_index.i31) && binsof(cp_prior_bit.set);
      bins bexti_mid_clear= binsof(cp_op.bexti) && binsof(cp_index.mid) && binsof(cp_prior_bit.clear);
      bins bexti_mid_set= binsof(cp_op.bexti) && binsof(cp_index.mid) && binsof(cp_prior_bit.set);
      bins binvi_i0_clear= binsof(cp_op.binvi) && binsof(cp_index.i0) && binsof(cp_prior_bit.clear);
      bins binvi_i0_set= binsof(cp_op.binvi) && binsof(cp_index.i0) && binsof(cp_prior_bit.set);
      bins binvi_i31_clear= binsof(cp_op.binvi) && binsof(cp_index.i31) && binsof(cp_prior_bit.clear);
      bins binvi_i31_set= binsof(cp_op.binvi) && binsof(cp_index.i31) && binsof(cp_prior_bit.set);
      bins binvi_mid_clear= binsof(cp_op.binvi) && binsof(cp_index.mid) && binsof(cp_prior_bit.clear);
      bins binvi_mid_set= binsof(cp_op.binvi) && binsof(cp_index.mid) && binsof(cp_prior_bit.set);
      bins bseti_i0_clear= binsof(cp_op.bseti) && binsof(cp_index.i0) && binsof(cp_prior_bit.clear);
      bins bseti_i0_set= binsof(cp_op.bseti) && binsof(cp_index.i0) && binsof(cp_prior_bit.set);
      bins bseti_i31_clear= binsof(cp_op.bseti) && binsof(cp_index.i31) && binsof(cp_prior_bit.clear);
      bins bseti_i31_set= binsof(cp_op.bseti) && binsof(cp_index.i31) && binsof(cp_prior_bit.set);
      bins bseti_mid_clear= binsof(cp_op.bseti) && binsof(cp_index.mid) && binsof(cp_prior_bit.clear);
      bins bseti_mid_set= binsof(cp_op.bseti) && binsof(cp_index.mid) && binsof(cp_prior_bit.set);
    }
    cr_op_operand: cross cp_op, cp_operand {
      bins bclri_all_ones= binsof(cp_op.bclri) && binsof(cp_operand.all_ones);
      bins bclri_rand= binsof(cp_op.bclri) && binsof(cp_operand.\rand );
      bins bclri_zero= binsof(cp_op.bclri) && binsof(cp_operand.zero);
      bins bexti_all_ones= binsof(cp_op.bexti) && binsof(cp_operand.all_ones);
      bins bexti_rand= binsof(cp_op.bexti) && binsof(cp_operand.\rand );
      bins bexti_zero= binsof(cp_op.bexti) && binsof(cp_operand.zero);
      bins binvi_all_ones= binsof(cp_op.binvi) && binsof(cp_operand.all_ones);
      bins binvi_rand= binsof(cp_op.binvi) && binsof(cp_operand.\rand );
      bins binvi_zero= binsof(cp_op.binvi) && binsof(cp_operand.zero);
      bins bseti_all_ones= binsof(cp_op.bseti) && binsof(cp_operand.all_ones);
      bins bseti_rand= binsof(cp_op.bseti) && binsof(cp_operand.\rand );
      bins bseti_zero= binsof(cp_op.bseti) && binsof(cp_operand.zero);
      bins bclr_all_ones= binsof(cp_op.bclr) && binsof(cp_operand.all_ones);
      bins bclr_rand= binsof(cp_op.bclr) && binsof(cp_operand.\rand );
      bins bclr_zero= binsof(cp_op.bclr) && binsof(cp_operand.zero);
      bins bext_all_ones= binsof(cp_op.bext) && binsof(cp_operand.all_ones);
      bins bext_rand= binsof(cp_op.bext) && binsof(cp_operand.\rand );
      bins bext_zero= binsof(cp_op.bext) && binsof(cp_operand.zero);
      bins binv_all_ones= binsof(cp_op.binv) && binsof(cp_operand.all_ones);
      bins binv_rand= binsof(cp_op.binv) && binsof(cp_operand.\rand );
      bins binv_zero= binsof(cp_op.binv) && binsof(cp_operand.zero);
      bins bset_all_ones= binsof(cp_op.bset) && binsof(cp_operand.all_ones);
      bins bset_rand= binsof(cp_op.bset) && binsof(cp_operand.\rand );
      bins bset_zero= binsof(cp_op.bset) && binsof(cp_operand.zero);
    }
    cr_reg_upper: cross cp_op, cp_rs2_upper {
      bins bclr_all_ones= binsof(cp_op.bclr) && binsof(cp_rs2_upper.all_ones);
      bins bext_all_ones= binsof(cp_op.bext) && binsof(cp_rs2_upper.all_ones);
      bins binv_all_ones= binsof(cp_op.binv) && binsof(cp_rs2_upper.all_ones);
      bins bset_all_ones= binsof(cp_op.bset) && binsof(cp_rs2_upper.all_ones);
      bins bclr_other_nonzero= binsof(cp_op.bclr) && binsof(cp_rs2_upper.other_nonzero);
      bins bclr_zero= binsof(cp_op.bclr) && binsof(cp_rs2_upper.zero);
      bins bext_other_nonzero= binsof(cp_op.bext) && binsof(cp_rs2_upper.other_nonzero);
      bins bext_zero= binsof(cp_op.bext) && binsof(cp_rs2_upper.zero);
      bins binv_other_nonzero= binsof(cp_op.binv) && binsof(cp_rs2_upper.other_nonzero);
      bins binv_zero= binsof(cp_op.binv) && binsof(cp_rs2_upper.zero);
      bins bset_other_nonzero= binsof(cp_op.bset) && binsof(cp_rs2_upper.other_nonzero);
      bins bset_zero= binsof(cp_op.bset) && binsof(cp_rs2_upper.zero);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins bclr_no= binsof(cp_op.bclr) && binsof(cp_rd_x0.no);
      bins bclr_yes= binsof(cp_op.bclr) && binsof(cp_rd_x0.yes);
      bins bclri_no= binsof(cp_op.bclri) && binsof(cp_rd_x0.no);
      bins bclri_yes= binsof(cp_op.bclri) && binsof(cp_rd_x0.yes);
      bins bext_no= binsof(cp_op.bext) && binsof(cp_rd_x0.no);
      bins bext_yes= binsof(cp_op.bext) && binsof(cp_rd_x0.yes);
      bins bexti_no= binsof(cp_op.bexti) && binsof(cp_rd_x0.no);
      bins bexti_yes= binsof(cp_op.bexti) && binsof(cp_rd_x0.yes);
      bins binv_no= binsof(cp_op.binv) && binsof(cp_rd_x0.no);
      bins binv_yes= binsof(cp_op.binv) && binsof(cp_rd_x0.yes);
      bins binvi_no= binsof(cp_op.binvi) && binsof(cp_rd_x0.no);
      bins binvi_yes= binsof(cp_op.binvi) && binsof(cp_rd_x0.yes);
      bins bset_no= binsof(cp_op.bset) && binsof(cp_rd_x0.no);
      bins bset_yes= binsof(cp_op.bset) && binsof(cp_rd_x0.yes);
      bins bseti_no= binsof(cp_op.bseti) && binsof(cp_rd_x0.no);
      bins bseti_yes= binsof(cp_op.bseti) && binsof(cp_rd_x0.yes);
    }
  endgroup

  // CG-CMP-005 (gen_cmp_zcb_cg), 30 coverpoint bins, 65 cross bins
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_LBU = 0;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_LHU = 1;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_LH = 2;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_SB = 3;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_SH = 4;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_ZEXT_B = 5;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_SEXT_B = 6;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_ZEXT_H = 7;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_SEXT_H = 8;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_NOT = 9;
  localparam int GEN_FC_CMP_ZCB_CP_INSN_C_MUL = 10;
  localparam int GEN_FC_CMP_ZCB_CP_UIMM_B_U0 = 0;
  localparam int GEN_FC_CMP_ZCB_CP_UIMM_B_U1 = 1;
  localparam int GEN_FC_CMP_ZCB_CP_UIMM_B_U2 = 2;
  localparam int GEN_FC_CMP_ZCB_CP_UIMM_B_U3 = 3;
  localparam int GEN_FC_CMP_ZCB_CP_UIMM_H_U0 = 0;
  localparam int GEN_FC_CMP_ZCB_CP_UIMM_H_U2 = 1;
  localparam int GEN_FC_CMP_ZCB_CP_DATA_SIGN_POS = 0;
  localparam int GEN_FC_CMP_ZCB_CP_DATA_SIGN_NEG = 1;
  localparam int GEN_FC_CMP_ZCB_CP_ALU_OPERAND_BIT7_SET = 0;
  localparam int GEN_FC_CMP_ZCB_CP_ALU_OPERAND_BIT7_CLEAR = 1;
  localparam int GEN_FC_CMP_ZCB_CP_ALU_OPERAND_BIT15_SET = 2;
  localparam int GEN_FC_CMP_ZCB_CP_ALU_OPERAND_ZERO = 3;
  localparam int GEN_FC_CMP_ZCB_CP_ALU_OPERAND_ALL_ONES = 4;
  localparam int GEN_FC_CMP_ZCB_CP_ALU_OPERAND_RAND = 5;
  localparam int GEN_FC_CMP_ZCB_CP_ADDR_ALIGN_ALIGNED = 0;
  localparam int GEN_FC_CMP_ZCB_CP_ADDR_ALIGN_MIS1 = 1;
  localparam int GEN_FC_CMP_ZCB_CP_ADDR_ALIGN_MIS3 = 2;
  localparam int GEN_FC_CMP_ZCB_CP_REGS_SAME = 0;
  localparam int GEN_FC_CMP_ZCB_CP_REGS_DISTINCT = 1;
  covergroup gen_cmp_zcb_cg with function sample(int v_cp_insn, int v_cp_uimm_b, int v_cp_uimm_h, int v_cp_data_sign, int v_cp_alu_operand, int v_cp_addr_align, int v_cp_regs);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_insn: coverpoint v_cp_insn { bins c_lbu= {0}; bins c_lhu= {1}; bins c_lh= {2}; bins c_sb= {3}; bins c_sh= {4}; bins c_zext_b= {5}; bins c_sext_b= {6}; bins c_zext_h= {7}; bins c_sext_h= {8}; bins c_not= {9}; bins c_mul= {10}; ignore_bins na = {-1}; }
    cp_uimm_b: coverpoint v_cp_uimm_b { bins u0= {0}; bins u1= {1}; bins u2= {2}; bins u3= {3}; ignore_bins na = {-1}; }
    cp_uimm_h: coverpoint v_cp_uimm_h { bins u0= {0}; bins u2= {1}; ignore_bins na = {-1}; }
    cp_data_sign: coverpoint v_cp_data_sign { bins pos= {0}; bins neg= {1}; ignore_bins na = {-1}; }
    cp_alu_operand: coverpoint v_cp_alu_operand { bins bit7_set= {0}; bins bit7_clear= {1}; bins bit15_set= {2}; bins zero= {3}; bins all_ones= {4}; bins \rand = {5}; ignore_bins na = {-1}; }
    cp_addr_align: coverpoint v_cp_addr_align { bins aligned= {0}; bins mis1= {1}; bins mis3= {2}; ignore_bins na = {-1}; }
    cp_regs: coverpoint v_cp_regs { bins same= {0}; bins distinct= {1}; ignore_bins na = {-1}; }
    cr_half_misaligned: cross cp_insn, cp_addr_align {
      bins c_lh_aligned= binsof(cp_insn.c_lh) && binsof(cp_addr_align.aligned);
      bins c_lh_mis1= binsof(cp_insn.c_lh) && binsof(cp_addr_align.mis1);
      bins c_lh_mis3= binsof(cp_insn.c_lh) && binsof(cp_addr_align.mis3);
      bins c_lhu_aligned= binsof(cp_insn.c_lhu) && binsof(cp_addr_align.aligned);
      bins c_lhu_mis1= binsof(cp_insn.c_lhu) && binsof(cp_addr_align.mis1);
      bins c_lhu_mis3= binsof(cp_insn.c_lhu) && binsof(cp_addr_align.mis3);
      bins c_sh_aligned= binsof(cp_insn.c_sh) && binsof(cp_addr_align.aligned);
      bins c_sh_mis1= binsof(cp_insn.c_sh) && binsof(cp_addr_align.mis1);
      bins c_sh_mis3= binsof(cp_insn.c_sh) && binsof(cp_addr_align.mis3);
    }
    cr_load_sign: cross cp_insn, cp_data_sign {
      bins c_lbu_neg= binsof(cp_insn.c_lbu) && binsof(cp_data_sign.neg);
      bins c_lbu_pos= binsof(cp_insn.c_lbu) && binsof(cp_data_sign.pos);
      bins c_lh_neg= binsof(cp_insn.c_lh) && binsof(cp_data_sign.neg);
      bins c_lh_pos= binsof(cp_insn.c_lh) && binsof(cp_data_sign.pos);
      bins c_lhu_neg= binsof(cp_insn.c_lhu) && binsof(cp_data_sign.neg);
      bins c_lhu_pos= binsof(cp_insn.c_lhu) && binsof(cp_data_sign.pos);
    }
    cr_ls_b: cross cp_insn, cp_uimm_b {
      bins c_lbu_u0= binsof(cp_insn.c_lbu) && binsof(cp_uimm_b.u0);
      bins c_lbu_u1= binsof(cp_insn.c_lbu) && binsof(cp_uimm_b.u1);
      bins c_lbu_u2= binsof(cp_insn.c_lbu) && binsof(cp_uimm_b.u2);
      bins c_lbu_u3= binsof(cp_insn.c_lbu) && binsof(cp_uimm_b.u3);
      bins c_sb_u0= binsof(cp_insn.c_sb) && binsof(cp_uimm_b.u0);
      bins c_sb_u1= binsof(cp_insn.c_sb) && binsof(cp_uimm_b.u1);
      bins c_sb_u2= binsof(cp_insn.c_sb) && binsof(cp_uimm_b.u2);
      bins c_sb_u3= binsof(cp_insn.c_sb) && binsof(cp_uimm_b.u3);
    }
    cr_ls_h: cross cp_insn, cp_uimm_h {
      bins c_lh_u0= binsof(cp_insn.c_lh) && binsof(cp_uimm_h.u0);
      bins c_lh_u2= binsof(cp_insn.c_lh) && binsof(cp_uimm_h.u2);
      bins c_lhu_u0= binsof(cp_insn.c_lhu) && binsof(cp_uimm_h.u0);
      bins c_lhu_u2= binsof(cp_insn.c_lhu) && binsof(cp_uimm_h.u2);
      bins c_sh_u0= binsof(cp_insn.c_sh) && binsof(cp_uimm_h.u0);
      bins c_sh_u2= binsof(cp_insn.c_sh) && binsof(cp_uimm_h.u2);
    }
    cr_alu_operand: cross cp_insn, cp_alu_operand {
      bins c_not_all_ones= binsof(cp_insn.c_not) && binsof(cp_alu_operand.all_ones);
      bins c_not_bit15_set= binsof(cp_insn.c_not) && binsof(cp_alu_operand.bit15_set);
      bins c_not_bit7_clear= binsof(cp_insn.c_not) && binsof(cp_alu_operand.bit7_clear);
      bins c_not_bit7_set= binsof(cp_insn.c_not) && binsof(cp_alu_operand.bit7_set);
      bins c_not_rand= binsof(cp_insn.c_not) && binsof(cp_alu_operand.\rand );
      bins c_not_zero= binsof(cp_insn.c_not) && binsof(cp_alu_operand.zero);
      bins c_sext_b_all_ones= binsof(cp_insn.c_sext_b) && binsof(cp_alu_operand.all_ones);
      bins c_sext_b_bit15_set= binsof(cp_insn.c_sext_b) && binsof(cp_alu_operand.bit15_set);
      bins c_sext_b_bit7_clear= binsof(cp_insn.c_sext_b) && binsof(cp_alu_operand.bit7_clear);
      bins c_sext_b_bit7_set= binsof(cp_insn.c_sext_b) && binsof(cp_alu_operand.bit7_set);
      bins c_sext_b_rand= binsof(cp_insn.c_sext_b) && binsof(cp_alu_operand.\rand );
      bins c_sext_b_zero= binsof(cp_insn.c_sext_b) && binsof(cp_alu_operand.zero);
      bins c_sext_h_all_ones= binsof(cp_insn.c_sext_h) && binsof(cp_alu_operand.all_ones);
      bins c_sext_h_bit15_set= binsof(cp_insn.c_sext_h) && binsof(cp_alu_operand.bit15_set);
      bins c_sext_h_bit7_clear= binsof(cp_insn.c_sext_h) && binsof(cp_alu_operand.bit7_clear);
      bins c_sext_h_bit7_set= binsof(cp_insn.c_sext_h) && binsof(cp_alu_operand.bit7_set);
      bins c_sext_h_rand= binsof(cp_insn.c_sext_h) && binsof(cp_alu_operand.\rand );
      bins c_sext_h_zero= binsof(cp_insn.c_sext_h) && binsof(cp_alu_operand.zero);
      bins c_zext_b_all_ones= binsof(cp_insn.c_zext_b) && binsof(cp_alu_operand.all_ones);
      bins c_zext_b_bit15_set= binsof(cp_insn.c_zext_b) && binsof(cp_alu_operand.bit15_set);
      bins c_zext_b_bit7_clear= binsof(cp_insn.c_zext_b) && binsof(cp_alu_operand.bit7_clear);
      bins c_zext_b_bit7_set= binsof(cp_insn.c_zext_b) && binsof(cp_alu_operand.bit7_set);
      bins c_zext_b_rand= binsof(cp_insn.c_zext_b) && binsof(cp_alu_operand.\rand );
      bins c_zext_b_zero= binsof(cp_insn.c_zext_b) && binsof(cp_alu_operand.zero);
      bins c_zext_h_all_ones= binsof(cp_insn.c_zext_h) && binsof(cp_alu_operand.all_ones);
      bins c_zext_h_bit15_set= binsof(cp_insn.c_zext_h) && binsof(cp_alu_operand.bit15_set);
      bins c_zext_h_bit7_clear= binsof(cp_insn.c_zext_h) && binsof(cp_alu_operand.bit7_clear);
      bins c_zext_h_bit7_set= binsof(cp_insn.c_zext_h) && binsof(cp_alu_operand.bit7_set);
      bins c_zext_h_rand= binsof(cp_insn.c_zext_h) && binsof(cp_alu_operand.\rand );
      bins c_zext_h_zero= binsof(cp_insn.c_zext_h) && binsof(cp_alu_operand.zero);
      bins c_mul_all_ones= binsof(cp_insn.c_mul) && binsof(cp_alu_operand.all_ones);
      bins c_mul_bit15_set= binsof(cp_insn.c_mul) && binsof(cp_alu_operand.bit15_set);
      bins c_mul_bit7_clear= binsof(cp_insn.c_mul) && binsof(cp_alu_operand.bit7_clear);
      bins c_mul_bit7_set= binsof(cp_insn.c_mul) && binsof(cp_alu_operand.bit7_set);
      bins c_mul_rand= binsof(cp_insn.c_mul) && binsof(cp_alu_operand.\rand );
      bins c_mul_zero= binsof(cp_insn.c_mul) && binsof(cp_alu_operand.zero);
    }
  endgroup

  // CG-MUL-002 (gen_mul_timing_cg), 24 coverpoint bins, 56 cross bins
  localparam int GEN_FC_MUL_TIMING_CP_OP_MUL = 0;
  localparam int GEN_FC_MUL_TIMING_CP_OP_MULH = 1;
  localparam int GEN_FC_MUL_TIMING_CP_OP_MULHSU = 2;
  localparam int GEN_FC_MUL_TIMING_CP_OP_MULHU = 3;
  localparam int GEN_FC_MUL_TIMING_CP_DELTA_D1 = 0;
  localparam int GEN_FC_MUL_TIMING_CP_DELTA_D2 = 1;
  localparam int GEN_FC_MUL_TIMING_CP_DELTA_D3PLUS = 2;
  localparam int GEN_FC_MUL_TIMING_CP_PREV_ALU = 0;
  localparam int GEN_FC_MUL_TIMING_CP_PREV_MUL = 1;
  localparam int GEN_FC_MUL_TIMING_CP_PREV_MULH_CLASS = 2;
  localparam int GEN_FC_MUL_TIMING_CP_PREV_LOAD = 3;
  localparam int GEN_FC_MUL_TIMING_CP_PREV_STORE = 4;
  localparam int GEN_FC_MUL_TIMING_CP_PREV_DIV = 5;
  localparam int GEN_FC_MUL_TIMING_CP_PREV_BRANCH = 6;
  localparam int GEN_FC_MUL_TIMING_CP_PREV_OTHER = 7;
  localparam int GEN_FC_MUL_TIMING_CP_NEXT_DEP_NO = 0;
  localparam int GEN_FC_MUL_TIMING_CP_NEXT_DEP_YES = 1;
  localparam int GEN_FC_MUL_TIMING_CP_WB_BUSY_NO = 0;
  localparam int GEN_FC_MUL_TIMING_CP_WB_BUSY_YES = 1;
  localparam int GEN_FC_MUL_TIMING_CP_FETCH_STALL_NO = 0;
  localparam int GEN_FC_MUL_TIMING_CP_FETCH_STALL_YES = 1;
  localparam int GEN_FC_MUL_TIMING_CP_DMEM_DELAY_MIN1 = 0;
  localparam int GEN_FC_MUL_TIMING_CP_DMEM_DELAY_SHORT = 1;
  localparam int GEN_FC_MUL_TIMING_CP_DMEM_DELAY_LONG = 2;
  covergroup gen_mul_timing_cg with function sample(int v_cp_op, int v_cp_delta, int v_cp_prev, int v_cp_next_dep, int v_cp_wb_busy, int v_cp_fetch_stall, int v_cp_dmem_delay);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins mul= {0}; bins mulh= {1}; bins mulhsu= {2}; bins mulhu= {3}; ignore_bins na = {-1}; }
    cp_delta: coverpoint v_cp_delta { bins d1= {0}; bins d2= {1}; bins d3plus= {2}; ignore_bins na = {-1}; }
    cp_prev: coverpoint v_cp_prev { bins alu= {0}; bins mul= {1}; bins mulh_class= {2}; bins load= {3}; bins store= {4}; bins div= {5}; bins branch= {6}; bins other= {7}; ignore_bins na = {-1}; }
    cp_next_dep: coverpoint v_cp_next_dep { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_wb_busy: coverpoint v_cp_wb_busy { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_fetch_stall: coverpoint v_cp_fetch_stall { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_dmem_delay: coverpoint v_cp_dmem_delay { bins min1= {0}; bins short= {1}; bins long= {2}; ignore_bins na = {-1}; }
    cr_op_delta_clean: cross cp_op, cp_delta, cp_fetch_stall, cp_wb_busy {
      bins mulh_d2= binsof(cp_op.mulh) && binsof(cp_delta.d2) && binsof(cp_fetch_stall.no) && binsof(cp_wb_busy.no);
      bins mulhu_d2= binsof(cp_op.mulhu) && binsof(cp_delta.d2) && binsof(cp_fetch_stall.no) && binsof(cp_wb_busy.no);
      bins mulhsu_d2= binsof(cp_op.mulhsu) && binsof(cp_delta.d2) && binsof(cp_fetch_stall.no) && binsof(cp_wb_busy.no);
      bins mul_d1= binsof(cp_op.mul) && binsof(cp_delta.d1) && binsof(cp_fetch_stall.no) && binsof(cp_wb_busy.no);
    }
    cr_op_next_dep: cross cp_op, cp_next_dep {
      bins mul_yes= binsof(cp_op.mul) && binsof(cp_next_dep.yes);
      bins mulh_yes= binsof(cp_op.mulh) && binsof(cp_next_dep.yes);
      bins mulhsu_yes= binsof(cp_op.mulhsu) && binsof(cp_next_dep.yes);
      bins mulhu_yes= binsof(cp_op.mulhu) && binsof(cp_next_dep.yes);
      bins mul_no= binsof(cp_op.mul) && binsof(cp_next_dep.no);
      bins mulh_no= binsof(cp_op.mulh) && binsof(cp_next_dep.no);
      bins mulhsu_no= binsof(cp_op.mulhsu) && binsof(cp_next_dep.no);
      bins mulhu_no= binsof(cp_op.mulhu) && binsof(cp_next_dep.no);
    }
    cr_seq: cross cp_prev, cp_op {
      bins alu_mul= binsof(cp_prev.alu) && binsof(cp_op.mul);
      bins alu_mulh= binsof(cp_prev.alu) && binsof(cp_op.mulh);
      bins alu_mulhsu= binsof(cp_prev.alu) && binsof(cp_op.mulhsu);
      bins alu_mulhu= binsof(cp_prev.alu) && binsof(cp_op.mulhu);
      bins branch_mul= binsof(cp_prev.branch) && binsof(cp_op.mul);
      bins branch_mulh= binsof(cp_prev.branch) && binsof(cp_op.mulh);
      bins branch_mulhsu= binsof(cp_prev.branch) && binsof(cp_op.mulhsu);
      bins branch_mulhu= binsof(cp_prev.branch) && binsof(cp_op.mulhu);
      bins div_mul= binsof(cp_prev.div) && binsof(cp_op.mul);
      bins div_mulh= binsof(cp_prev.div) && binsof(cp_op.mulh);
      bins div_mulhsu= binsof(cp_prev.div) && binsof(cp_op.mulhsu);
      bins div_mulhu= binsof(cp_prev.div) && binsof(cp_op.mulhu);
      bins load_mul= binsof(cp_prev.load) && binsof(cp_op.mul);
      bins load_mulh= binsof(cp_prev.load) && binsof(cp_op.mulh);
      bins load_mulhsu= binsof(cp_prev.load) && binsof(cp_op.mulhsu);
      bins load_mulhu= binsof(cp_prev.load) && binsof(cp_op.mulhu);
      bins mul_mul= binsof(cp_prev.mul) && binsof(cp_op.mul);
      bins mul_mulh= binsof(cp_prev.mul) && binsof(cp_op.mulh);
      bins mul_mulhsu= binsof(cp_prev.mul) && binsof(cp_op.mulhsu);
      bins mul_mulhu= binsof(cp_prev.mul) && binsof(cp_op.mulhu);
      bins mulh_class_mul= binsof(cp_prev.mulh_class) && binsof(cp_op.mul);
      bins mulh_class_mulh= binsof(cp_prev.mulh_class) && binsof(cp_op.mulh);
      bins mulh_class_mulhsu= binsof(cp_prev.mulh_class) && binsof(cp_op.mulhsu);
      bins mulh_class_mulhu= binsof(cp_prev.mulh_class) && binsof(cp_op.mulhu);
      bins other_mul= binsof(cp_prev.other) && binsof(cp_op.mul);
      bins other_mulh= binsof(cp_prev.other) && binsof(cp_op.mulh);
      bins other_mulhsu= binsof(cp_prev.other) && binsof(cp_op.mulhsu);
      bins other_mulhu= binsof(cp_prev.other) && binsof(cp_op.mulhu);
      bins store_mul= binsof(cp_prev.store) && binsof(cp_op.mul);
      bins store_mulh= binsof(cp_prev.store) && binsof(cp_op.mulh);
      bins store_mulhsu= binsof(cp_prev.store) && binsof(cp_op.mulhsu);
      bins store_mulhu= binsof(cp_prev.store) && binsof(cp_op.mulhu);
    }
    cr_wb_defer: cross cp_op, cp_wb_busy, cp_dmem_delay {
      bins mul_yes_long= binsof(cp_op.mul) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.long);
      bins mul_yes_min1= binsof(cp_op.mul) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.min1);
      bins mul_yes_short= binsof(cp_op.mul) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.short);
      bins mulh_yes_long= binsof(cp_op.mulh) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.long);
      bins mulh_yes_min1= binsof(cp_op.mulh) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.min1);
      bins mulh_yes_short= binsof(cp_op.mulh) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.short);
      bins mulhsu_yes_long= binsof(cp_op.mulhsu) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.long);
      bins mulhsu_yes_min1= binsof(cp_op.mulhsu) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.min1);
      bins mulhsu_yes_short= binsof(cp_op.mulhsu) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.short);
      bins mulhu_yes_long= binsof(cp_op.mulhu) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.long);
      bins mulhu_yes_min1= binsof(cp_op.mulhu) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.min1);
      bins mulhu_yes_short= binsof(cp_op.mulhu) && binsof(cp_wb_busy.yes) && binsof(cp_dmem_delay.short);
    }
  endgroup

  // CG-RST-001 (gen_rst_boot_cg), 26 coverpoint bins, 18 cross bins
  localparam int GEN_FC_RST_BOOT_CP_BOOT_ADDR_ZERO = 0;
  localparam int GEN_FC_RST_BOOT_CP_BOOT_ADDR_LOW = 1;
  localparam int GEN_FC_RST_BOOT_CP_BOOT_ADDR_MID = 2;
  localparam int GEN_FC_RST_BOOT_CP_BOOT_ADDR_HIGH = 3;
  localparam int GEN_FC_RST_BOOT_CP_BOOT_LOW_BYTE_ZERO = 0;
  localparam int GEN_FC_RST_BOOT_CP_FETCH_EN_AT_RELEASE_ON = 0;
  localparam int GEN_FC_RST_BOOT_CP_FETCH_EN_AT_RELEASE_OFF = 1;
  localparam int GEN_FC_RST_BOOT_CP_FETCH_EN_AT_RELEASE_INVALID = 2;
  localparam int GEN_FC_RST_BOOT_CP_PENDING_NONE = 0;
  localparam int GEN_FC_RST_BOOT_CP_PENDING_IRQ_ENABLED_LATER = 1;
  localparam int GEN_FC_RST_BOOT_CP_PENDING_NMI = 2;
  localparam int GEN_FC_RST_BOOT_CP_PENDING_DEBUG_REQ = 3;
  localparam int GEN_FC_RST_BOOT_CP_PENDING_NMI_AND_DEBUG = 4;
  localparam int GEN_FC_RST_BOOT_CP_PENDING_IRQ_AND_DEBUG = 5;
  localparam int GEN_FC_RST_BOOT_CP_FIRST_EVENT_FIRST_INSTR_RETIRE = 0;
  localparam int GEN_FC_RST_BOOT_CP_FIRST_EVENT_NMI_TAKEN = 1;
  localparam int GEN_FC_RST_BOOT_CP_FIRST_EVENT_DEBUG_ENTRY = 2;
  localparam int GEN_FC_RST_BOOT_CP_FIRST_EVENT_NONE_FETCH_DISABLED = 3;
  localparam int GEN_FC_RST_BOOT_CP_HART_ID_ZERO = 0;
  localparam int GEN_FC_RST_BOOT_CP_HART_ID_MAX = 1;
  localparam int GEN_FC_RST_BOOT_CP_HART_ID_RANDOM = 2;
  localparam int GEN_FC_RST_BOOT_CP_RESET_KIND_POWER_ON = 0;
  localparam int GEN_FC_RST_BOOT_CP_RESET_KIND_MID_RUN = 1;
  localparam int GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_TWO = 0;
  localparam int GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_THREE = 1;
  localparam int GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_MORE = 2;
  covergroup gen_rst_boot_cg with function sample(int v_cp_boot_addr, int v_cp_boot_low_byte, int v_cp_fetch_en_at_release, int v_cp_pending, int v_cp_first_event, int v_cp_hart_id, int v_cp_reset_kind, int v_cp_boot_to_req_cycles);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_boot_addr: coverpoint v_cp_boot_addr { bins zero= {0}; bins low= {1}; bins mid= {2}; bins high= {3}; ignore_bins na = {-1}; }
    cp_boot_low_byte: coverpoint v_cp_boot_low_byte { bins zero= {0}; ignore_bins na = {-1}; }
    cp_fetch_en_at_release: coverpoint v_cp_fetch_en_at_release { bins on= {0}; bins off= {1}; bins invalid= {2}; ignore_bins na = {-1}; }
    cp_pending: coverpoint v_cp_pending { bins none= {0}; bins irq_enabled_later= {1}; bins nmi= {2}; bins debug_req= {3}; bins nmi_and_debug= {4}; bins irq_and_debug= {5}; ignore_bins na = {-1}; }
    cp_first_event: coverpoint v_cp_first_event { bins first_instr_retire= {0}; bins nmi_taken= {1}; bins debug_entry= {2}; bins none_fetch_disabled= {3}; ignore_bins na = {-1}; }
    cp_hart_id: coverpoint v_cp_hart_id { bins zero= {0}; bins max= {1}; bins random= {2}; ignore_bins na = {-1}; }
    cp_reset_kind: coverpoint v_cp_reset_kind { bins power_on= {0}; bins mid_run= {1}; ignore_bins na = {-1}; }
    cp_boot_to_req_cycles: coverpoint v_cp_boot_to_req_cycles { bins two= {0}; bins three= {1}; bins more= {2}; ignore_bins na = {-1}; }
    cr_boot_kind: cross cp_boot_addr, cp_reset_kind {
      bins high_power_on= binsof(cp_boot_addr.high) && binsof(cp_reset_kind.power_on);
      bins low_power_on= binsof(cp_boot_addr.low) && binsof(cp_reset_kind.power_on);
      bins mid_power_on= binsof(cp_boot_addr.mid) && binsof(cp_reset_kind.power_on);
      bins zero_power_on= binsof(cp_boot_addr.zero) && binsof(cp_reset_kind.power_on);
      bins high_mid_run= binsof(cp_boot_addr.high) && binsof(cp_reset_kind.mid_run);
      bins low_mid_run= binsof(cp_boot_addr.low) && binsof(cp_reset_kind.mid_run);
      bins mid_mid_run= binsof(cp_boot_addr.mid) && binsof(cp_reset_kind.mid_run);
      bins zero_mid_run= binsof(cp_boot_addr.zero) && binsof(cp_reset_kind.mid_run);
    }
    cr_pending_first: cross cp_pending, cp_first_event {
      bins none_first_instr_retire= binsof(cp_pending.none) && binsof(cp_first_event.first_instr_retire);
      bins irq_enabled_later_first_instr_retire= binsof(cp_pending.irq_enabled_later) && binsof(cp_first_event.first_instr_retire);
      bins debug_req_debug_entry= binsof(cp_pending.debug_req) && binsof(cp_first_event.debug_entry);
      bins nmi_and_debug_debug_entry= binsof(cp_pending.nmi_and_debug) && binsof(cp_first_event.debug_entry);
      bins nmi_nmi_taken= binsof(cp_pending.nmi) && binsof(cp_first_event.nmi_taken);
      bins irq_and_debug_debug_entry= binsof(cp_pending.irq_and_debug) && binsof(cp_first_event.debug_entry);
    }
    cr_fetch_en_first: cross cp_fetch_en_at_release, cp_first_event {
      bins on_first_instr_retire= binsof(cp_fetch_en_at_release.on) && binsof(cp_first_event.first_instr_retire);
      bins invalid_none_fetch_disabled= binsof(cp_fetch_en_at_release.invalid) && binsof(cp_first_event.none_fetch_disabled);
      bins off_first_instr_retire= binsof(cp_fetch_en_at_release.off) && binsof(cp_first_event.first_instr_retire);
      bins off_none_fetch_disabled= binsof(cp_fetch_en_at_release.off) && binsof(cp_first_event.none_fetch_disabled);
    }
  endgroup

  // CG-SEC-005 (gen_sec_ctrl_inputs_cg), 35 coverpoint bins, 16 cross bins
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_CPUCTRL_READ = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_FETCH_EN_CHANGE = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_MCOUNTEREN_W_CHANGE = 2;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_KEY_REQ = 3;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_KEY_VALID_CHANGE = 4;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_MCOUNTEREN_WRITE = 5;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_BOOT_ADDR_CHANGE = 6;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BOOT_ADDR_CHANGE_CTX_RUNNING = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BOOT_ADDR_CHANGE_CTX_IN_HANDLER = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BOOT_ADDR_CHANGE_CTX_IN_WFI = 2;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BIT8_READBACK_ZERO = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BIT8_READBACK_ONE = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BITS67_READBACK_B6_0_B7_0 = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BITS67_READBACK_B6_1_B7_0 = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BITS67_READBACK_B6_0_B7_1 = 2;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_BITS67_READBACK_B6_1_B7_1 = 3;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_ICACHE_EN_READBACK_IN_DEBUG_ONE = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_ICACHE_EN_READBACK_IN_DEBUG_ZERO = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_ON = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_OFF = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_INVALID = 2;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_ON = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_OFF = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_INVALID = 2;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_WRITE_EFFECT_APPLIED = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_WRITE_EFFECT_DROPPED = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_KEY_DELAY_IMMEDIATE = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_KEY_DELAY_DELAYED = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_KEY_DELAY_WITHHELD_THEN_VALID = 2;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_KEY_REQ_CONTEXT_RESET_INVAL = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_KEY_REQ_CONTEXT_FENCE_I = 1;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_KEY_REQ_CONTEXT_DEBUG_MODE = 2;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_KEY_REQ_CONTEXT_ICACHE_DISABLED = 3;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_RVFI_EXT_KEY_VALID_ZERO = 0;
  localparam int GEN_FC_SEC_CTRL_INPUTS_CP_RVFI_EXT_KEY_VALID_ONE = 1;
  covergroup gen_sec_ctrl_inputs_cg with function sample(int v_cp_event, int v_cp_boot_addr_change_ctx, int v_cp_bit8_readback, int v_cp_bits67_readback, int v_cp_icache_en_readback_in_debug, int v_cp_fetch_en_val, int v_cp_mcounteren_w_val, int v_cp_mcounteren_write_effect, int v_cp_key_delay, int v_cp_key_req_context, int v_cp_rvfi_ext_key_valid);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_event: coverpoint v_cp_event { bins cpuctrl_read= {0}; bins fetch_en_change= {1}; bins mcounteren_w_change= {2}; bins key_req= {3}; bins key_valid_change= {4}; bins mcounteren_write= {5}; bins boot_addr_change= {6}; ignore_bins na = {-1}; }
    cp_boot_addr_change_ctx: coverpoint v_cp_boot_addr_change_ctx { bins running= {0}; bins in_handler= {1}; bins in_wfi= {2}; ignore_bins na = {-1}; }
    cp_bit8_readback: coverpoint v_cp_bit8_readback { bins zero= {0}; bins one= {1}; ignore_bins na = {-1}; }
    cp_bits67_readback: coverpoint v_cp_bits67_readback { bins b6_0_b7_0= {0}; bins b6_1_b7_0= {1}; bins b6_0_b7_1= {2}; bins b6_1_b7_1= {3}; ignore_bins na = {-1}; }
    cp_icache_en_readback_in_debug: coverpoint v_cp_icache_en_readback_in_debug { bins one= {0}; bins zero= {1}; ignore_bins na = {-1}; }
    cp_fetch_en_val: coverpoint v_cp_fetch_en_val { bins on= {0}; bins off= {1}; bins invalid= {2}; ignore_bins na = {-1}; }
    cp_mcounteren_w_val: coverpoint v_cp_mcounteren_w_val { bins on= {0}; bins off= {1}; bins invalid= {2}; ignore_bins na = {-1}; }
    cp_mcounteren_write_effect: coverpoint v_cp_mcounteren_write_effect { bins applied= {0}; bins dropped= {1}; ignore_bins na = {-1}; }
    cp_key_delay: coverpoint v_cp_key_delay { bins immediate= {0}; bins delayed= {1}; bins withheld_then_valid= {2}; ignore_bins na = {-1}; }
    cp_key_req_context: coverpoint v_cp_key_req_context { bins reset_inval= {0}; bins fence_i= {1}; bins debug_mode= {2}; bins icache_disabled= {3}; ignore_bins na = {-1}; }
    cp_rvfi_ext_key_valid: coverpoint v_cp_rvfi_ext_key_valid { bins zero= {0}; bins one= {1}; ignore_bins na = {-1}; }
    cr_mcounteren: cross cp_mcounteren_w_val, cp_mcounteren_write_effect {
      bins invalid_dropped= binsof(cp_mcounteren_w_val.invalid) && binsof(cp_mcounteren_write_effect.dropped);
      bins off_dropped= binsof(cp_mcounteren_w_val.off) && binsof(cp_mcounteren_write_effect.dropped);
      bins on_applied= binsof(cp_mcounteren_w_val.on) && binsof(cp_mcounteren_write_effect.applied);
    }
    cr_key: cross cp_key_delay, cp_bit8_readback {
      bins delayed_one= binsof(cp_key_delay.delayed) && binsof(cp_bit8_readback.one);
      bins delayed_zero= binsof(cp_key_delay.delayed) && binsof(cp_bit8_readback.zero);
      bins immediate_one= binsof(cp_key_delay.immediate) && binsof(cp_bit8_readback.one);
      bins withheld_then_valid_one= binsof(cp_key_delay.withheld_then_valid) && binsof(cp_bit8_readback.one);
      bins withheld_then_valid_zero= binsof(cp_key_delay.withheld_then_valid) && binsof(cp_bit8_readback.zero);
    }
    cr_key_ctx: cross cp_key_req_context, cp_key_delay {
      bins debug_mode_delayed= binsof(cp_key_req_context.debug_mode) && binsof(cp_key_delay.delayed);
      bins fence_i_delayed= binsof(cp_key_req_context.fence_i) && binsof(cp_key_delay.delayed);
      bins fence_i_immediate= binsof(cp_key_req_context.fence_i) && binsof(cp_key_delay.immediate);
      bins fence_i_withheld_then_valid= binsof(cp_key_req_context.fence_i) && binsof(cp_key_delay.withheld_then_valid);
      bins icache_disabled_immediate= binsof(cp_key_req_context.icache_disabled) && binsof(cp_key_delay.immediate);
      bins reset_inval_delayed= binsof(cp_key_req_context.reset_inval) && binsof(cp_key_delay.delayed);
      bins reset_inval_immediate= binsof(cp_key_req_context.reset_inval) && binsof(cp_key_delay.immediate);
      bins reset_inval_withheld_then_valid= binsof(cp_key_req_context.reset_inval) && binsof(cp_key_delay.withheld_then_valid);
    }
  endgroup

  // CG-RVFI-001 (gen_rvfi_record_cg), 38 coverpoint bins, 32 cross bins
  localparam int GEN_FC_RVFI_RECORD_CP_TRAP_NO = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_TRAP_YES = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_INTR_NO = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_INTR_YES = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_MODE_U = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_MODE_M = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_INSN_KIND_C16 = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_INSN_KIND_I32 = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_INSN_KIND_ZCMP_UOP = 2;
  localparam int GEN_FC_RVFI_RECORD_CP_RD_X0 = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_RD_NONZERO = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_RS1_X0 = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_RS1_NONZERO = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_RS2_X0 = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_RS2_NONZERO = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_RS3_ZERO = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_RS3_NONZERO = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_DELTA_PLUS2 = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_DELTA_PLUS4 = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_DELTA_JUMP_FWD = 2;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_DELTA_JUMP_BACK = 3;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_DELTA_REDIRECT_OTHER = 4;
  localparam int GEN_FC_RVFI_RECORD_CP_ORDER_STEP_FIRST = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_CONTINUOUS = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_INTR = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_AFTER_TRAP = 2;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_AFTER_FLUSH_REDIRECT = 3;
  localparam int GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_DEBUG = 4;
  localparam int GEN_FC_RVFI_RECORD_CP_VALID_GAP_G1 = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_VALID_GAP_G2 = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_VALID_GAP_G3_PLUS = 2;
  localparam int GEN_FC_RVFI_RECORD_CP_INTR_KIND_IRQ = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_INTR_KIND_NMI = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_INTR_KIND_NMI_INT = 2;
  localparam int GEN_FC_RVFI_RECORD_CP_INTR_KIND_NONE = 3;
  localparam int GEN_FC_RVFI_RECORD_CP_RD_SOURCE_ALU_WB = 0;
  localparam int GEN_FC_RVFI_RECORD_CP_RD_SOURCE_LOAD_LSU = 1;
  localparam int GEN_FC_RVFI_RECORD_CP_RD_SOURCE_NONE = 2;
  covergroup gen_rvfi_record_cg with function sample(int v_cp_trap, int v_cp_intr, int v_cp_mode, int v_cp_insn_kind, int v_cp_rd, int v_cp_rs1, int v_cp_rs2, int v_cp_rs3, int v_cp_pc_delta, int v_cp_order_step, int v_cp_pc_continuity, int v_cp_valid_gap, int v_cp_intr_kind, int v_cp_rd_source);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_trap: coverpoint v_cp_trap { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_intr: coverpoint v_cp_intr { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_mode: coverpoint v_cp_mode { bins u= {0}; bins m= {1}; ignore_bins na = {-1}; }
    cp_insn_kind: coverpoint v_cp_insn_kind { bins c16= {0}; bins i32= {1}; bins zcmp_uop= {2}; ignore_bins na = {-1}; }
    cp_rd: coverpoint v_cp_rd { bins x0= {0}; bins nonzero= {1}; ignore_bins na = {-1}; }
    cp_rs1: coverpoint v_cp_rs1 { bins x0= {0}; bins nonzero= {1}; ignore_bins na = {-1}; }
    cp_rs2: coverpoint v_cp_rs2 { bins x0= {0}; bins nonzero= {1}; ignore_bins na = {-1}; }
    cp_rs3: coverpoint v_cp_rs3 { bins zero= {0}; bins nonzero= {1}; ignore_bins na = {-1}; }
    cp_pc_delta: coverpoint v_cp_pc_delta { bins plus2= {0}; bins plus4= {1}; bins jump_fwd= {2}; bins jump_back= {3}; bins redirect_other= {4}; ignore_bins na = {-1}; }
    cp_order_step: coverpoint v_cp_order_step { bins first= {0}; ignore_bins na = {-1}; }
    cp_pc_continuity: coverpoint v_cp_pc_continuity { bins continuous= {0}; bins discontinuous_intr= {1}; bins discontinuous_after_trap= {2}; bins discontinuous_after_flush_redirect= {3}; bins discontinuous_debug= {4}; ignore_bins na = {-1}; }
    cp_valid_gap: coverpoint v_cp_valid_gap { bins g1= {0}; bins g2= {1}; bins g3_plus= {2}; ignore_bins na = {-1}; }
    cp_intr_kind: coverpoint v_cp_intr_kind { bins irq= {0}; bins nmi= {1}; bins nmi_int= {2}; bins none= {3}; ignore_bins na = {-1}; }
    cp_rd_source: coverpoint v_cp_rd_source { bins alu_wb= {0}; bins load_lsu= {1}; bins none= {2}; ignore_bins na = {-1}; }
    cr_kind_trap: cross cp_insn_kind, cp_trap {
      bins i32_yes= binsof(cp_insn_kind.i32) && binsof(cp_trap.yes);
      bins zcmp_uop_no= binsof(cp_insn_kind.zcmp_uop) && binsof(cp_trap.no);
      bins c16_no= binsof(cp_insn_kind.c16) && binsof(cp_trap.no);
      bins i32_no= binsof(cp_insn_kind.i32) && binsof(cp_trap.no);
      bins zcmp_uop_yes= binsof(cp_insn_kind.zcmp_uop) && binsof(cp_trap.yes);
      bins c16_yes= binsof(cp_insn_kind.c16) && binsof(cp_trap.yes);
    }
    cr_intr_cont: cross cp_intr, cp_pc_continuity {
      bins no_discontinuous_after_trap= binsof(cp_intr.no) && binsof(cp_pc_continuity.discontinuous_after_trap);
      bins no_discontinuous_debug= binsof(cp_intr.no) && binsof(cp_pc_continuity.discontinuous_debug);
      bins yes_discontinuous_intr= binsof(cp_intr.yes) && binsof(cp_pc_continuity.discontinuous_intr);
      bins no_continuous= binsof(cp_intr.no) && binsof(cp_pc_continuity.continuous);
      bins no_discontinuous_after_flush_redirect= binsof(cp_intr.no) && binsof(cp_pc_continuity.discontinuous_after_flush_redirect);
    }
    cr_mode_trap: cross cp_mode, cp_trap {
      bins m_no= binsof(cp_mode.m) && binsof(cp_trap.no);
      bins u_no= binsof(cp_mode.u) && binsof(cp_trap.no);
      bins m_yes= binsof(cp_mode.m) && binsof(cp_trap.yes);
      bins u_yes= binsof(cp_mode.u) && binsof(cp_trap.yes);
    }
    cr_rd_kind: cross cp_rd, cp_insn_kind, cp_trap {
      bins nonzero_c16_no= binsof(cp_rd.nonzero) && binsof(cp_insn_kind.c16) && binsof(cp_trap.no);
      bins nonzero_i32_no= binsof(cp_rd.nonzero) && binsof(cp_insn_kind.i32) && binsof(cp_trap.no);
      bins nonzero_zcmp_uop_no= binsof(cp_rd.nonzero) && binsof(cp_insn_kind.zcmp_uop) && binsof(cp_trap.no);
      bins x0_c16_no= binsof(cp_rd.x0) && binsof(cp_insn_kind.c16) && binsof(cp_trap.no);
      bins x0_c16_yes= binsof(cp_rd.x0) && binsof(cp_insn_kind.c16) && binsof(cp_trap.yes);
      bins x0_i32_no= binsof(cp_rd.x0) && binsof(cp_insn_kind.i32) && binsof(cp_trap.no);
      bins x0_i32_yes= binsof(cp_rd.x0) && binsof(cp_insn_kind.i32) && binsof(cp_trap.yes);
      bins x0_zcmp_uop_yes= binsof(cp_rd.x0) && binsof(cp_insn_kind.zcmp_uop) && binsof(cp_trap.yes);
    }
    cr_rd_source_kind: cross cp_rd_source, cp_insn_kind {
      bins alu_wb_c16= binsof(cp_rd_source.alu_wb) && binsof(cp_insn_kind.c16);
      bins alu_wb_i32= binsof(cp_rd_source.alu_wb) && binsof(cp_insn_kind.i32);
      bins alu_wb_zcmp_uop= binsof(cp_rd_source.alu_wb) && binsof(cp_insn_kind.zcmp_uop);
      bins load_lsu_c16= binsof(cp_rd_source.load_lsu) && binsof(cp_insn_kind.c16);
      bins load_lsu_i32= binsof(cp_rd_source.load_lsu) && binsof(cp_insn_kind.i32);
      bins load_lsu_zcmp_uop= binsof(cp_rd_source.load_lsu) && binsof(cp_insn_kind.zcmp_uop);
      bins none_c16= binsof(cp_rd_source.none) && binsof(cp_insn_kind.c16);
      bins none_i32= binsof(cp_rd_source.none) && binsof(cp_insn_kind.i32);
      bins none_zcmp_uop= binsof(cp_rd_source.none) && binsof(cp_insn_kind.zcmp_uop);
    }
  endgroup

  // CG-CMP-009 (gen_cmp_zcmp_hazard_cg), 28 coverpoint bins, 74 cross bins
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_STORE_SAME_SLOT_THEN_POP = 0;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_WRITE_PUSHED_REG_THEN_PUSH = 1;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_LOAD_PUSHED_REG_THEN_PUSH = 2;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_LOAD_THEN_MVA01S = 3;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRET_RA_DEFERRED = 4;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_PUSH_THEN_POP_B2B = 5;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POP_THEN_PUSH_B2B = 6;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRET_THEN_TARGET = 7;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRETZ_THEN_TARGET = 8;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_MVSA01_THEN_MVA01S = 9;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRET_FT_CM = 10;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRETZ_FT_CM = 11;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_PUSH = 0;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_POP = 1;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_POPRET = 2;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_POPRETZ = 3;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_MVSA01 = 4;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_MVA01S = 5;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_RET_ONCE_YES = 0;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_REDIRECT_ONCE_YES = 0;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R4 = 0;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R5_14 = 1;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R15 = 2;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_MIN1 = 0;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_SHORT = 1;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_LONG = 2;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_DELTA_UOP_ALL_ONE = 0;
  localparam int GEN_FC_CMP_ZCMP_HAZARD_CP_DELTA_UOP_SOME_STALL = 1;
  covergroup gen_cmp_zcmp_hazard_cg with function sample(int v_cp_hazard, int v_cp_ft_kind, int v_cp_ret_once, int v_cp_redirect_once, int v_cp_rlist_class, int v_cp_dmem_delay, int v_cp_delta_uop);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_hazard: coverpoint v_cp_hazard { bins store_same_slot_then_pop= {0}; bins write_pushed_reg_then_push= {1}; bins load_pushed_reg_then_push= {2}; bins load_then_mva01s= {3}; bins popret_ra_deferred= {4}; bins push_then_pop_b2b= {5}; bins pop_then_push_b2b= {6}; bins popret_then_target= {7}; bins popretz_then_target= {8}; bins mvsa01_then_mva01s= {9}; bins popret_ft_cm= {10}; bins popretz_ft_cm= {11}; ignore_bins na = {-1}; }
    cp_ft_kind: coverpoint v_cp_ft_kind { bins cm_push= {0}; bins cm_pop= {1}; bins cm_popret= {2}; bins cm_popretz= {3}; bins cm_mvsa01= {4}; bins cm_mva01s= {5}; ignore_bins na = {-1}; }
    cp_ret_once: coverpoint v_cp_ret_once { bins yes= {0}; ignore_bins na = {-1}; }
    cp_redirect_once: coverpoint v_cp_redirect_once { bins yes= {0}; ignore_bins na = {-1}; }
    cp_rlist_class: coverpoint v_cp_rlist_class { bins r4= {0}; bins r5_14= {1}; bins r15= {2}; ignore_bins na = {-1}; }
    cp_dmem_delay: coverpoint v_cp_dmem_delay { bins min1= {0}; bins short= {1}; bins long= {2}; ignore_bins na = {-1}; }
    cp_delta_uop: coverpoint v_cp_delta_uop { bins all_one= {0}; bins some_stall= {1}; ignore_bins na = {-1}; }
    cr_hazard_delay: cross cp_hazard, cp_dmem_delay {
      bins popret_ra_deferred_long= binsof(cp_hazard.popret_ra_deferred) && binsof(cp_dmem_delay.long);
      bins popret_ra_deferred_short= binsof(cp_hazard.popret_ra_deferred) && binsof(cp_dmem_delay.short);
      bins load_pushed_reg_then_push_long= binsof(cp_hazard.load_pushed_reg_then_push) && binsof(cp_dmem_delay.long);
      bins load_pushed_reg_then_push_min1= binsof(cp_hazard.load_pushed_reg_then_push) && binsof(cp_dmem_delay.min1);
      bins load_pushed_reg_then_push_short= binsof(cp_hazard.load_pushed_reg_then_push) && binsof(cp_dmem_delay.short);
      bins load_then_mva01s_long= binsof(cp_hazard.load_then_mva01s) && binsof(cp_dmem_delay.long);
      bins load_then_mva01s_min1= binsof(cp_hazard.load_then_mva01s) && binsof(cp_dmem_delay.min1);
      bins load_then_mva01s_short= binsof(cp_hazard.load_then_mva01s) && binsof(cp_dmem_delay.short);
      bins store_same_slot_then_pop_long= binsof(cp_hazard.store_same_slot_then_pop) && binsof(cp_dmem_delay.long);
      bins store_same_slot_then_pop_min1= binsof(cp_hazard.store_same_slot_then_pop) && binsof(cp_dmem_delay.min1);
      bins store_same_slot_then_pop_short= binsof(cp_hazard.store_same_slot_then_pop) && binsof(cp_dmem_delay.short);
      bins write_pushed_reg_then_push_long= binsof(cp_hazard.write_pushed_reg_then_push) && binsof(cp_dmem_delay.long);
      bins write_pushed_reg_then_push_min1= binsof(cp_hazard.write_pushed_reg_then_push) && binsof(cp_dmem_delay.min1);
      bins write_pushed_reg_then_push_short= binsof(cp_hazard.write_pushed_reg_then_push) && binsof(cp_dmem_delay.short);
      bins pop_then_push_b2b_long= binsof(cp_hazard.pop_then_push_b2b) && binsof(cp_dmem_delay.long);
      bins pop_then_push_b2b_min1= binsof(cp_hazard.pop_then_push_b2b) && binsof(cp_dmem_delay.min1);
      bins pop_then_push_b2b_short= binsof(cp_hazard.pop_then_push_b2b) && binsof(cp_dmem_delay.short);
      bins popret_ft_cm_long= binsof(cp_hazard.popret_ft_cm) && binsof(cp_dmem_delay.long);
      bins popret_ft_cm_min1= binsof(cp_hazard.popret_ft_cm) && binsof(cp_dmem_delay.min1);
      bins popret_ft_cm_short= binsof(cp_hazard.popret_ft_cm) && binsof(cp_dmem_delay.short);
      bins popret_then_target_long= binsof(cp_hazard.popret_then_target) && binsof(cp_dmem_delay.long);
      bins popret_then_target_min1= binsof(cp_hazard.popret_then_target) && binsof(cp_dmem_delay.min1);
      bins popret_then_target_short= binsof(cp_hazard.popret_then_target) && binsof(cp_dmem_delay.short);
      bins popretz_ft_cm_long= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_dmem_delay.long);
      bins popretz_ft_cm_min1= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_dmem_delay.min1);
      bins popretz_ft_cm_short= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_dmem_delay.short);
      bins popretz_then_target_long= binsof(cp_hazard.popretz_then_target) && binsof(cp_dmem_delay.long);
      bins popretz_then_target_min1= binsof(cp_hazard.popretz_then_target) && binsof(cp_dmem_delay.min1);
      bins popretz_then_target_short= binsof(cp_hazard.popretz_then_target) && binsof(cp_dmem_delay.short);
      bins push_then_pop_b2b_long= binsof(cp_hazard.push_then_pop_b2b) && binsof(cp_dmem_delay.long);
      bins push_then_pop_b2b_min1= binsof(cp_hazard.push_then_pop_b2b) && binsof(cp_dmem_delay.min1);
      bins push_then_pop_b2b_short= binsof(cp_hazard.push_then_pop_b2b) && binsof(cp_dmem_delay.short);
    }
    cr_hazard_rlist: cross cp_hazard, cp_rlist_class {
      bins load_pushed_reg_then_push_r15= binsof(cp_hazard.load_pushed_reg_then_push) && binsof(cp_rlist_class.r15);
      bins load_pushed_reg_then_push_r4= binsof(cp_hazard.load_pushed_reg_then_push) && binsof(cp_rlist_class.r4);
      bins load_pushed_reg_then_push_r5_14= binsof(cp_hazard.load_pushed_reg_then_push) && binsof(cp_rlist_class.r5_14);
      bins store_same_slot_then_pop_r15= binsof(cp_hazard.store_same_slot_then_pop) && binsof(cp_rlist_class.r15);
      bins store_same_slot_then_pop_r4= binsof(cp_hazard.store_same_slot_then_pop) && binsof(cp_rlist_class.r4);
      bins store_same_slot_then_pop_r5_14= binsof(cp_hazard.store_same_slot_then_pop) && binsof(cp_rlist_class.r5_14);
      bins write_pushed_reg_then_push_r15= binsof(cp_hazard.write_pushed_reg_then_push) && binsof(cp_rlist_class.r15);
      bins write_pushed_reg_then_push_r4= binsof(cp_hazard.write_pushed_reg_then_push) && binsof(cp_rlist_class.r4);
      bins write_pushed_reg_then_push_r5_14= binsof(cp_hazard.write_pushed_reg_then_push) && binsof(cp_rlist_class.r5_14);
      bins pop_then_push_b2b_r15= binsof(cp_hazard.pop_then_push_b2b) && binsof(cp_rlist_class.r15);
      bins pop_then_push_b2b_r4= binsof(cp_hazard.pop_then_push_b2b) && binsof(cp_rlist_class.r4);
      bins pop_then_push_b2b_r5_14= binsof(cp_hazard.pop_then_push_b2b) && binsof(cp_rlist_class.r5_14);
      bins popret_ft_cm_r15= binsof(cp_hazard.popret_ft_cm) && binsof(cp_rlist_class.r15);
      bins popret_ft_cm_r4= binsof(cp_hazard.popret_ft_cm) && binsof(cp_rlist_class.r4);
      bins popret_ft_cm_r5_14= binsof(cp_hazard.popret_ft_cm) && binsof(cp_rlist_class.r5_14);
      bins popret_ra_deferred_r15= binsof(cp_hazard.popret_ra_deferred) && binsof(cp_rlist_class.r15);
      bins popret_ra_deferred_r4= binsof(cp_hazard.popret_ra_deferred) && binsof(cp_rlist_class.r4);
      bins popret_ra_deferred_r5_14= binsof(cp_hazard.popret_ra_deferred) && binsof(cp_rlist_class.r5_14);
      bins popret_then_target_r15= binsof(cp_hazard.popret_then_target) && binsof(cp_rlist_class.r15);
      bins popret_then_target_r4= binsof(cp_hazard.popret_then_target) && binsof(cp_rlist_class.r4);
      bins popret_then_target_r5_14= binsof(cp_hazard.popret_then_target) && binsof(cp_rlist_class.r5_14);
      bins popretz_ft_cm_r15= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_rlist_class.r15);
      bins popretz_ft_cm_r4= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_rlist_class.r4);
      bins popretz_ft_cm_r5_14= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_rlist_class.r5_14);
      bins popretz_then_target_r15= binsof(cp_hazard.popretz_then_target) && binsof(cp_rlist_class.r15);
      bins popretz_then_target_r4= binsof(cp_hazard.popretz_then_target) && binsof(cp_rlist_class.r4);
      bins popretz_then_target_r5_14= binsof(cp_hazard.popretz_then_target) && binsof(cp_rlist_class.r5_14);
      bins push_then_pop_b2b_r15= binsof(cp_hazard.push_then_pop_b2b) && binsof(cp_rlist_class.r15);
      bins push_then_pop_b2b_r4= binsof(cp_hazard.push_then_pop_b2b) && binsof(cp_rlist_class.r4);
      bins push_then_pop_b2b_r5_14= binsof(cp_hazard.push_then_pop_b2b) && binsof(cp_rlist_class.r5_14);
    }
    cr_ft_kind: cross cp_hazard, cp_ft_kind {
      bins popret_ft_cm_cm_mva01s= binsof(cp_hazard.popret_ft_cm) && binsof(cp_ft_kind.cm_mva01s);
      bins popret_ft_cm_cm_mvsa01= binsof(cp_hazard.popret_ft_cm) && binsof(cp_ft_kind.cm_mvsa01);
      bins popret_ft_cm_cm_pop= binsof(cp_hazard.popret_ft_cm) && binsof(cp_ft_kind.cm_pop);
      bins popret_ft_cm_cm_popret= binsof(cp_hazard.popret_ft_cm) && binsof(cp_ft_kind.cm_popret);
      bins popret_ft_cm_cm_popretz= binsof(cp_hazard.popret_ft_cm) && binsof(cp_ft_kind.cm_popretz);
      bins popret_ft_cm_cm_push= binsof(cp_hazard.popret_ft_cm) && binsof(cp_ft_kind.cm_push);
      bins popretz_ft_cm_cm_mva01s= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_ft_kind.cm_mva01s);
      bins popretz_ft_cm_cm_mvsa01= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_ft_kind.cm_mvsa01);
      bins popretz_ft_cm_cm_pop= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_ft_kind.cm_pop);
      bins popretz_ft_cm_cm_popret= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_ft_kind.cm_popret);
      bins popretz_ft_cm_cm_popretz= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_ft_kind.cm_popretz);
      bins popretz_ft_cm_cm_push= binsof(cp_hazard.popretz_ft_cm) && binsof(cp_ft_kind.cm_push);
    }
  endgroup

  // CG-ISA-004 (gen_isa_lui_auipc_cg), 16 coverpoint bins, 18 cross bins
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_OP_LUI = 0;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_OP_AUIPC = 1;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_IMM20_ZERO = 0;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_IMM20_ALL_ONES = 1;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_IMM20_MSB = 2;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_IMM20_ONE = 3;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_IMM20_RAND = 4;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_PC_ALIGN_WORD = 0;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_PC_ALIGN_HALF = 1;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_PC_REGION_LOW = 0;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_PC_REGION_HIGH = 1;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_PC_REGION_MID = 2;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_WRAP_NO = 0;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_WRAP_YES = 1;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_RD_X0_NO = 0;
  localparam int GEN_FC_ISA_LUI_AUIPC_CP_RD_X0_YES = 1;
  covergroup gen_isa_lui_auipc_cg with function sample(int v_cp_op, int v_cp_imm20, int v_cp_pc_align, int v_cp_pc_region, int v_cp_wrap, int v_cp_rd_x0);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins lui= {0}; bins auipc= {1}; ignore_bins na = {-1}; }
    cp_imm20: coverpoint v_cp_imm20 { bins zero= {0}; bins all_ones= {1}; bins msb= {2}; bins one= {3}; bins \rand = {4}; ignore_bins na = {-1}; }
    cp_pc_align: coverpoint v_cp_pc_align { bins word= {0}; bins half= {1}; ignore_bins na = {-1}; }
    cp_pc_region: coverpoint v_cp_pc_region { bins low= {0}; bins high= {1}; bins mid= {2}; ignore_bins na = {-1}; }
    cp_wrap: coverpoint v_cp_wrap { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_rd_x0: coverpoint v_cp_rd_x0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cr_op_imm: cross cp_op, cp_imm20 {
      bins auipc_all_ones= binsof(cp_op.auipc) && binsof(cp_imm20.all_ones);
      bins auipc_msb= binsof(cp_op.auipc) && binsof(cp_imm20.msb);
      bins auipc_one= binsof(cp_op.auipc) && binsof(cp_imm20.one);
      bins auipc_rand= binsof(cp_op.auipc) && binsof(cp_imm20.\rand );
      bins auipc_zero= binsof(cp_op.auipc) && binsof(cp_imm20.zero);
      bins lui_all_ones= binsof(cp_op.lui) && binsof(cp_imm20.all_ones);
      bins lui_msb= binsof(cp_op.lui) && binsof(cp_imm20.msb);
      bins lui_one= binsof(cp_op.lui) && binsof(cp_imm20.one);
      bins lui_rand= binsof(cp_op.lui) && binsof(cp_imm20.\rand );
      bins lui_zero= binsof(cp_op.lui) && binsof(cp_imm20.zero);
    }
    cr_op_rd_x0: cross cp_op, cp_rd_x0 {
      bins auipc_no= binsof(cp_op.auipc) && binsof(cp_rd_x0.no);
      bins auipc_yes= binsof(cp_op.auipc) && binsof(cp_rd_x0.yes);
      bins lui_no= binsof(cp_op.lui) && binsof(cp_rd_x0.no);
      bins lui_yes= binsof(cp_op.lui) && binsof(cp_rd_x0.yes);
    }
    cr_auipc_pc: cross cp_op, cp_pc_align, cp_wrap {
      bins auipc_half_nowrap= binsof(cp_op.auipc) && binsof(cp_pc_align.half) && binsof(cp_wrap.no);
      bins auipc_half_wrap= binsof(cp_op.auipc) && binsof(cp_pc_align.half) && binsof(cp_wrap.yes);
      bins auipc_word_nowrap= binsof(cp_op.auipc) && binsof(cp_pc_align.word) && binsof(cp_wrap.no);
      bins auipc_word_wrap= binsof(cp_op.auipc) && binsof(cp_pc_align.word) && binsof(cp_wrap.yes);
    }
  endgroup

  // CG-ISA-005 (gen_isa_hint_x0_cg), 42 coverpoint bins, 42 cross bins
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_CANONICAL_NOP = 0;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ADDI_X0_NZIMM = 1;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ANDI_X0 = 2;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ORI_X0 = 3;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_XORI_X0 = 4;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLTI_X0 = 5;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLTIU_X0 = 6;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_LUI_X0 = 7;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_AUIPC_X0 = 8;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ADD_X0 = 9;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SUB_X0 = 10;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLL_X0 = 11;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRL_X0 = 12;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRA_X0 = 13;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLT_X0 = 14;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLTU_X0 = 15;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_XOR_X0 = 16;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_OR_X0 = 17;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_AND_X0 = 18;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLLI_X0_SEMIHOST = 19;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRAI_X0_SEMIHOST = 20;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLLI_X0_OTHER = 21;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRLI_X0 = 22;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRAI_X0_OTHER = 23;
  localparam int GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_OTHER = 24;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_ALU_IMM = 0;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_SHIFT = 1;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_ALU_REG = 2;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_LUI_AUIPC = 3;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_LOAD = 4;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_CSRR = 5;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_JAL = 6;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_JALR = 7;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_MUL = 8;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_MULH = 9;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_DIV_REM = 10;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_BIT_1CYC = 11;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_BIT_2CYC = 12;
  localparam int GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_CMP_HINT = 13;
  localparam int GEN_FC_ISA_HINT_X0_CP_X0_READ_RS1_ZERO = 0;
  localparam int GEN_FC_ISA_HINT_X0_CP_X0_READ_RS2_ZERO = 1;
  localparam int GEN_FC_ISA_HINT_X0_CP_X0_READ_NONE = 2;
  covergroup gen_isa_hint_x0_cg with function sample(int v_cp_hint_class, int v_cp_writer_class, int v_cp_x0_read);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_hint_class: coverpoint v_cp_hint_class { bins canonical_nop= {0}; bins addi_x0_nzimm= {1}; bins andi_x0= {2}; bins ori_x0= {3}; bins xori_x0= {4}; bins slti_x0= {5}; bins sltiu_x0= {6}; bins lui_x0= {7}; bins auipc_x0= {8}; bins add_x0= {9}; bins sub_x0= {10}; bins sll_x0= {11}; bins srl_x0= {12}; bins sra_x0= {13}; bins slt_x0= {14}; bins sltu_x0= {15}; bins xor_x0= {16}; bins or_x0= {17}; bins and_x0= {18}; bins slli_x0_semihost= {19}; bins srai_x0_semihost= {20}; bins slli_x0_other= {21}; bins srli_x0= {22}; bins srai_x0_other= {23}; bins other= {24}; ignore_bins na = {-1}; }
    cp_writer_class: coverpoint v_cp_writer_class { bins alu_imm= {0}; bins shift= {1}; bins alu_reg= {2}; bins lui_auipc= {3}; bins load= {4}; bins csrr= {5}; bins jal= {6}; bins jalr= {7}; bins mul= {8}; bins mulh= {9}; bins div_rem= {10}; bins bit_1cyc= {11}; bins bit_2cyc= {12}; bins cmp_hint= {13}; ignore_bins na = {-1}; }
    cp_x0_read: coverpoint v_cp_x0_read { bins rs1_zero= {0}; bins rs2_zero= {1}; bins none= {2}; ignore_bins na = {-1}; }
    cr_writer_read: cross cp_writer_class, cp_x0_read {
      bins alu_imm_none= binsof(cp_writer_class.alu_imm) && binsof(cp_x0_read.none);
      bins alu_imm_rs1_zero= binsof(cp_writer_class.alu_imm) && binsof(cp_x0_read.rs1_zero);
      bins alu_imm_rs2_zero= binsof(cp_writer_class.alu_imm) && binsof(cp_x0_read.rs2_zero);
      bins alu_reg_none= binsof(cp_writer_class.alu_reg) && binsof(cp_x0_read.none);
      bins alu_reg_rs1_zero= binsof(cp_writer_class.alu_reg) && binsof(cp_x0_read.rs1_zero);
      bins alu_reg_rs2_zero= binsof(cp_writer_class.alu_reg) && binsof(cp_x0_read.rs2_zero);
      bins bit_1cyc_none= binsof(cp_writer_class.bit_1cyc) && binsof(cp_x0_read.none);
      bins bit_1cyc_rs1_zero= binsof(cp_writer_class.bit_1cyc) && binsof(cp_x0_read.rs1_zero);
      bins bit_1cyc_rs2_zero= binsof(cp_writer_class.bit_1cyc) && binsof(cp_x0_read.rs2_zero);
      bins bit_2cyc_none= binsof(cp_writer_class.bit_2cyc) && binsof(cp_x0_read.none);
      bins bit_2cyc_rs1_zero= binsof(cp_writer_class.bit_2cyc) && binsof(cp_x0_read.rs1_zero);
      bins bit_2cyc_rs2_zero= binsof(cp_writer_class.bit_2cyc) && binsof(cp_x0_read.rs2_zero);
      bins cmp_hint_none= binsof(cp_writer_class.cmp_hint) && binsof(cp_x0_read.none);
      bins cmp_hint_rs1_zero= binsof(cp_writer_class.cmp_hint) && binsof(cp_x0_read.rs1_zero);
      bins cmp_hint_rs2_zero= binsof(cp_writer_class.cmp_hint) && binsof(cp_x0_read.rs2_zero);
      bins csrr_none= binsof(cp_writer_class.csrr) && binsof(cp_x0_read.none);
      bins csrr_rs1_zero= binsof(cp_writer_class.csrr) && binsof(cp_x0_read.rs1_zero);
      bins csrr_rs2_zero= binsof(cp_writer_class.csrr) && binsof(cp_x0_read.rs2_zero);
      bins div_rem_none= binsof(cp_writer_class.div_rem) && binsof(cp_x0_read.none);
      bins div_rem_rs1_zero= binsof(cp_writer_class.div_rem) && binsof(cp_x0_read.rs1_zero);
      bins div_rem_rs2_zero= binsof(cp_writer_class.div_rem) && binsof(cp_x0_read.rs2_zero);
      bins jal_none= binsof(cp_writer_class.jal) && binsof(cp_x0_read.none);
      bins jal_rs1_zero= binsof(cp_writer_class.jal) && binsof(cp_x0_read.rs1_zero);
      bins jal_rs2_zero= binsof(cp_writer_class.jal) && binsof(cp_x0_read.rs2_zero);
      bins jalr_none= binsof(cp_writer_class.jalr) && binsof(cp_x0_read.none);
      bins jalr_rs1_zero= binsof(cp_writer_class.jalr) && binsof(cp_x0_read.rs1_zero);
      bins jalr_rs2_zero= binsof(cp_writer_class.jalr) && binsof(cp_x0_read.rs2_zero);
      bins load_none= binsof(cp_writer_class.load) && binsof(cp_x0_read.none);
      bins load_rs1_zero= binsof(cp_writer_class.load) && binsof(cp_x0_read.rs1_zero);
      bins load_rs2_zero= binsof(cp_writer_class.load) && binsof(cp_x0_read.rs2_zero);
      bins lui_auipc_none= binsof(cp_writer_class.lui_auipc) && binsof(cp_x0_read.none);
      bins lui_auipc_rs1_zero= binsof(cp_writer_class.lui_auipc) && binsof(cp_x0_read.rs1_zero);
      bins lui_auipc_rs2_zero= binsof(cp_writer_class.lui_auipc) && binsof(cp_x0_read.rs2_zero);
      bins mul_none= binsof(cp_writer_class.mul) && binsof(cp_x0_read.none);
      bins mul_rs1_zero= binsof(cp_writer_class.mul) && binsof(cp_x0_read.rs1_zero);
      bins mul_rs2_zero= binsof(cp_writer_class.mul) && binsof(cp_x0_read.rs2_zero);
      bins mulh_none= binsof(cp_writer_class.mulh) && binsof(cp_x0_read.none);
      bins mulh_rs1_zero= binsof(cp_writer_class.mulh) && binsof(cp_x0_read.rs1_zero);
      bins mulh_rs2_zero= binsof(cp_writer_class.mulh) && binsof(cp_x0_read.rs2_zero);
      bins shift_none= binsof(cp_writer_class.shift) && binsof(cp_x0_read.none);
      bins shift_rs1_zero= binsof(cp_writer_class.shift) && binsof(cp_x0_read.rs1_zero);
      bins shift_rs2_zero= binsof(cp_writer_class.shift) && binsof(cp_x0_read.rs2_zero);
    }
  endgroup

  // CG-ISA-006 (gen_isa_jump_cg), 35 coverpoint bins, 68 cross bins
  localparam int GEN_FC_ISA_JUMP_CP_OP_JAL = 0;
  localparam int GEN_FC_ISA_JUMP_CP_OP_JALR = 1;
  localparam int GEN_FC_ISA_JUMP_CP_OP_C_J = 2;
  localparam int GEN_FC_ISA_JUMP_CP_OP_C_JAL = 3;
  localparam int GEN_FC_ISA_JUMP_CP_OP_C_JR = 4;
  localparam int GEN_FC_ISA_JUMP_CP_OP_C_JALR = 5;
  localparam int GEN_FC_ISA_JUMP_CP_RD_CLASS_X0 = 0;
  localparam int GEN_FC_ISA_JUMP_CP_RD_CLASS_X1 = 1;
  localparam int GEN_FC_ISA_JUMP_CP_RD_CLASS_X5 = 2;
  localparam int GEN_FC_ISA_JUMP_CP_RD_CLASS_OTHER = 3;
  localparam int GEN_FC_ISA_JUMP_CP_JAL_OFF_SELF = 0;
  localparam int GEN_FC_ISA_JUMP_CP_JAL_OFF_MAX_FWD = 1;
  localparam int GEN_FC_ISA_JUMP_CP_JAL_OFF_MAX_BWD = 2;
  localparam int GEN_FC_ISA_JUMP_CP_JAL_OFF_POS_RAND = 3;
  localparam int GEN_FC_ISA_JUMP_CP_JAL_OFF_NEG_RAND = 4;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_IMM_ZERO = 0;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_IMM_MAX_POS = 1;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_IMM_MIN_NEG = 2;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_IMM_ODD = 3;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_IMM_POS_RAND = 4;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_IMM_NEG_RAND = 5;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_RS1_X0 = 0;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_RS1_EQ_RD = 1;
  localparam int GEN_FC_ISA_JUMP_CP_JALR_RS1_OTHER = 2;
  localparam int GEN_FC_ISA_JUMP_CP_TARGET_ALIGN_WORD = 0;
  localparam int GEN_FC_ISA_JUMP_CP_TARGET_ALIGN_HALF = 1;
  localparam int GEN_FC_ISA_JUMP_CP_TARGET_ODD_NO = 0;
  localparam int GEN_FC_ISA_JUMP_CP_TARGET_ODD_YES = 1;
  localparam int GEN_FC_ISA_JUMP_CP_WRAP_NO = 0;
  localparam int GEN_FC_ISA_JUMP_CP_WRAP_YES = 1;
  localparam int GEN_FC_ISA_JUMP_CP_PC_REGION_ZERO_PAGE = 0;
  localparam int GEN_FC_ISA_JUMP_CP_PC_REGION_HIGH = 1;
  localparam int GEN_FC_ISA_JUMP_CP_PC_REGION_MID = 2;
  localparam int GEN_FC_ISA_JUMP_CP_LINK_LEN_PC4 = 0;
  localparam int GEN_FC_ISA_JUMP_CP_LINK_LEN_PC2 = 1;
  covergroup gen_isa_jump_cg with function sample(int v_cp_op, int v_cp_rd_class, int v_cp_jal_off, int v_cp_jalr_imm, int v_cp_jalr_rs1, int v_cp_target_align, int v_cp_target_odd, int v_cp_wrap, int v_cp_pc_region, int v_cp_link_len);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins jal= {0}; bins jalr= {1}; bins c_j= {2}; bins c_jal= {3}; bins c_jr= {4}; bins c_jalr= {5}; ignore_bins na = {-1}; }
    cp_rd_class: coverpoint v_cp_rd_class { bins x0= {0}; bins x1= {1}; bins x5= {2}; bins other= {3}; ignore_bins na = {-1}; }
    cp_jal_off: coverpoint v_cp_jal_off { bins self= {0}; bins max_fwd= {1}; bins max_bwd= {2}; bins pos_rand= {3}; bins neg_rand= {4}; ignore_bins na = {-1}; }
    cp_jalr_imm: coverpoint v_cp_jalr_imm { bins zero= {0}; bins max_pos= {1}; bins min_neg= {2}; bins odd= {3}; bins pos_rand= {4}; bins neg_rand= {5}; ignore_bins na = {-1}; }
    cp_jalr_rs1: coverpoint v_cp_jalr_rs1 { bins x0= {0}; bins eq_rd= {1}; bins other= {2}; ignore_bins na = {-1}; }
    cp_target_align: coverpoint v_cp_target_align { bins word= {0}; bins half= {1}; ignore_bins na = {-1}; }
    cp_target_odd: coverpoint v_cp_target_odd { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_wrap: coverpoint v_cp_wrap { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_pc_region: coverpoint v_cp_pc_region { bins zero_page= {0}; bins high= {1}; bins mid= {2}; ignore_bins na = {-1}; }
    cp_link_len: coverpoint v_cp_link_len { bins pc4= {0}; bins pc2= {1}; ignore_bins na = {-1}; }
    cr_link: cross cp_op, cp_link_len {
      bins jal_pc4= binsof(cp_op.jal) && binsof(cp_link_len.pc4);
      bins c_jal_pc2= binsof(cp_op.c_jal) && binsof(cp_link_len.pc2);
      bins c_jalr_pc2= binsof(cp_op.c_jalr) && binsof(cp_link_len.pc2);
      bins jalr_pc4= binsof(cp_op.jalr) && binsof(cp_link_len.pc4);
    }
    cr_op_align: cross cp_op, cp_target_align {
      bins jal_half= binsof(cp_op.jal) && binsof(cp_target_align.half);
      bins jal_word= binsof(cp_op.jal) && binsof(cp_target_align.word);
      bins c_jalr_half= binsof(cp_op.c_jalr) && binsof(cp_target_align.half);
      bins c_jalr_word= binsof(cp_op.c_jalr) && binsof(cp_target_align.word);
      bins c_jr_half= binsof(cp_op.c_jr) && binsof(cp_target_align.half);
      bins c_jr_word= binsof(cp_op.c_jr) && binsof(cp_target_align.word);
      bins jalr_half= binsof(cp_op.jalr) && binsof(cp_target_align.half);
      bins jalr_word= binsof(cp_op.jalr) && binsof(cp_target_align.word);
      bins c_j_half= binsof(cp_op.c_j) && binsof(cp_target_align.half);
      bins c_jal_half= binsof(cp_op.c_jal) && binsof(cp_target_align.half);
      bins c_j_word= binsof(cp_op.c_j) && binsof(cp_target_align.word);
      bins c_jal_word= binsof(cp_op.c_jal) && binsof(cp_target_align.word);
    }
    cr_op_wrap: cross cp_op, cp_wrap {
      bins c_j_yes= binsof(cp_op.c_j) && binsof(cp_wrap.yes);
      bins c_jal_yes= binsof(cp_op.c_jal) && binsof(cp_wrap.yes);
      bins jal_yes= binsof(cp_op.jal) && binsof(cp_wrap.yes);
      bins jalr_yes= binsof(cp_op.jalr) && binsof(cp_wrap.yes);
      bins c_j_no= binsof(cp_op.c_j) && binsof(cp_wrap.no);
      bins c_jal_no= binsof(cp_op.c_jal) && binsof(cp_wrap.no);
      bins c_jalr_no= binsof(cp_op.c_jalr) && binsof(cp_wrap.no);
      bins c_jr_no= binsof(cp_op.c_jr) && binsof(cp_wrap.no);
      bins jal_no= binsof(cp_op.jal) && binsof(cp_wrap.no);
      bins jalr_no= binsof(cp_op.jalr) && binsof(cp_wrap.no);
    }
    cr_jal_off_rd: cross cp_op, cp_jal_off, cp_rd_class {
      bins jal_neg_rand_other= binsof(cp_op.jal) && binsof(cp_jal_off.neg_rand) && binsof(cp_rd_class.other);
      bins jal_neg_rand_x0= binsof(cp_op.jal) && binsof(cp_jal_off.neg_rand) && binsof(cp_rd_class.x0);
      bins jal_neg_rand_x1= binsof(cp_op.jal) && binsof(cp_jal_off.neg_rand) && binsof(cp_rd_class.x1);
      bins jal_neg_rand_x5= binsof(cp_op.jal) && binsof(cp_jal_off.neg_rand) && binsof(cp_rd_class.x5);
      bins jal_pos_rand_other= binsof(cp_op.jal) && binsof(cp_jal_off.pos_rand) && binsof(cp_rd_class.other);
      bins jal_pos_rand_x0= binsof(cp_op.jal) && binsof(cp_jal_off.pos_rand) && binsof(cp_rd_class.x0);
      bins jal_pos_rand_x1= binsof(cp_op.jal) && binsof(cp_jal_off.pos_rand) && binsof(cp_rd_class.x1);
      bins jal_pos_rand_x5= binsof(cp_op.jal) && binsof(cp_jal_off.pos_rand) && binsof(cp_rd_class.x5);
      bins jal_max_bwd_other= binsof(cp_op.jal) && binsof(cp_jal_off.max_bwd) && binsof(cp_rd_class.other);
      bins jal_max_bwd_x0= binsof(cp_op.jal) && binsof(cp_jal_off.max_bwd) && binsof(cp_rd_class.x0);
      bins jal_max_bwd_x1= binsof(cp_op.jal) && binsof(cp_jal_off.max_bwd) && binsof(cp_rd_class.x1);
      bins jal_max_bwd_x5= binsof(cp_op.jal) && binsof(cp_jal_off.max_bwd) && binsof(cp_rd_class.x5);
      bins jal_max_fwd_other= binsof(cp_op.jal) && binsof(cp_jal_off.max_fwd) && binsof(cp_rd_class.other);
      bins jal_max_fwd_x0= binsof(cp_op.jal) && binsof(cp_jal_off.max_fwd) && binsof(cp_rd_class.x0);
      bins jal_max_fwd_x1= binsof(cp_op.jal) && binsof(cp_jal_off.max_fwd) && binsof(cp_rd_class.x1);
      bins jal_max_fwd_x5= binsof(cp_op.jal) && binsof(cp_jal_off.max_fwd) && binsof(cp_rd_class.x5);
      bins jal_self_other= binsof(cp_op.jal) && binsof(cp_jal_off.self) && binsof(cp_rd_class.other);
      bins jal_self_x0= binsof(cp_op.jal) && binsof(cp_jal_off.self) && binsof(cp_rd_class.x0);
      bins jal_self_x1= binsof(cp_op.jal) && binsof(cp_jal_off.self) && binsof(cp_rd_class.x1);
      bins jal_self_x5= binsof(cp_op.jal) && binsof(cp_jal_off.self) && binsof(cp_rd_class.x5);
    }
    cr_zero_page_bwd: cross cp_op, cp_pc_region, cp_jal_off {
      bins jal_zero_page_neg= binsof(cp_op.jal) && binsof(cp_pc_region.zero_page) && binsof(cp_jal_off.neg_rand);
    }
    cr_jalr_rs1_imm: cross cp_jalr_rs1, cp_jalr_imm {
      bins other_neg_rand= binsof(cp_jalr_rs1.other) && binsof(cp_jalr_imm.neg_rand);
      bins other_pos_rand= binsof(cp_jalr_rs1.other) && binsof(cp_jalr_imm.pos_rand);
      bins eq_rd_max_pos= binsof(cp_jalr_rs1.eq_rd) && binsof(cp_jalr_imm.max_pos);
      bins eq_rd_min_neg= binsof(cp_jalr_rs1.eq_rd) && binsof(cp_jalr_imm.min_neg);
      bins eq_rd_zero= binsof(cp_jalr_rs1.eq_rd) && binsof(cp_jalr_imm.zero);
      bins other_max_pos= binsof(cp_jalr_rs1.other) && binsof(cp_jalr_imm.max_pos);
      bins other_min_neg= binsof(cp_jalr_rs1.other) && binsof(cp_jalr_imm.min_neg);
      bins other_zero= binsof(cp_jalr_rs1.other) && binsof(cp_jalr_imm.zero);
      bins x0_max_pos= binsof(cp_jalr_rs1.x0) && binsof(cp_jalr_imm.max_pos);
      bins x0_min_neg= binsof(cp_jalr_rs1.x0) && binsof(cp_jalr_imm.min_neg);
      bins x0_zero= binsof(cp_jalr_rs1.x0) && binsof(cp_jalr_imm.zero);
      bins other_odd= binsof(cp_jalr_rs1.other) && binsof(cp_jalr_imm.odd);
      bins eq_rd_neg_rand= binsof(cp_jalr_rs1.eq_rd) && binsof(cp_jalr_imm.neg_rand);
      bins eq_rd_odd= binsof(cp_jalr_rs1.eq_rd) && binsof(cp_jalr_imm.odd);
      bins eq_rd_pos_rand= binsof(cp_jalr_rs1.eq_rd) && binsof(cp_jalr_imm.pos_rand);
      bins x0_neg_rand= binsof(cp_jalr_rs1.x0) && binsof(cp_jalr_imm.neg_rand);
      bins x0_odd= binsof(cp_jalr_rs1.x0) && binsof(cp_jalr_imm.odd);
      bins x0_pos_rand= binsof(cp_jalr_rs1.x0) && binsof(cp_jalr_imm.pos_rand);
    }
    cr_odd: cross cp_op, cp_target_odd {
      bins c_jalr_odd= binsof(cp_op.c_jalr) && binsof(cp_target_odd.yes);
      bins c_jr_odd= binsof(cp_op.c_jr) && binsof(cp_target_odd.yes);
      bins jalr_odd= binsof(cp_op.jalr) && binsof(cp_target_odd.yes);
    }
  endgroup

  // CG-MUL-004 (gen_div_timing_cg), 30 coverpoint bins, 92 cross bins
  localparam int GEN_FC_DIV_TIMING_CP_OP_DIV = 0;
  localparam int GEN_FC_DIV_TIMING_CP_OP_DIVU = 1;
  localparam int GEN_FC_DIV_TIMING_CP_OP_REM = 2;
  localparam int GEN_FC_DIV_TIMING_CP_OP_REMU = 3;
  localparam int GEN_FC_DIV_TIMING_CP_DIT_OFF = 0;
  localparam int GEN_FC_DIV_TIMING_CP_DIT_ON = 1;
  localparam int GEN_FC_DIV_TIMING_CP_DIV0_NO = 0;
  localparam int GEN_FC_DIV_TIMING_CP_DIV0_YES = 1;
  localparam int GEN_FC_DIV_TIMING_CP_DELTA_D2 = 0;
  localparam int GEN_FC_DIV_TIMING_CP_DELTA_D37 = 1;
  localparam int GEN_FC_DIV_TIMING_CP_DELTA_OTHER = 2;
  localparam int GEN_FC_DIV_TIMING_CP_EVENT_MID_NONE = 0;
  localparam int GEN_FC_DIV_TIMING_CP_EVENT_MID_IRQ = 1;
  localparam int GEN_FC_DIV_TIMING_CP_EVENT_MID_DEBUG_REQ = 2;
  localparam int GEN_FC_DIV_TIMING_CP_EVENT_MID_NMI = 3;
  localparam int GEN_FC_DIV_TIMING_CP_WB_DEFER_NO = 0;
  localparam int GEN_FC_DIV_TIMING_CP_WB_DEFER_YES = 1;
  localparam int GEN_FC_DIV_TIMING_CP_PREV_LOAD_DEP = 0;
  localparam int GEN_FC_DIV_TIMING_CP_PREV_MUL = 1;
  localparam int GEN_FC_DIV_TIMING_CP_PREV_DIV = 2;
  localparam int GEN_FC_DIV_TIMING_CP_PREV_ALU = 3;
  localparam int GEN_FC_DIV_TIMING_CP_PREV_OTHER = 4;
  localparam int GEN_FC_DIV_TIMING_CP_NEXT_DEP_ALU = 0;
  localparam int GEN_FC_DIV_TIMING_CP_NEXT_MUL = 1;
  localparam int GEN_FC_DIV_TIMING_CP_NEXT_DIV = 2;
  localparam int GEN_FC_DIV_TIMING_CP_NEXT_OTHER = 3;
  localparam int GEN_FC_DIV_TIMING_CP_FETCH_STALL_NO = 0;
  localparam int GEN_FC_DIV_TIMING_CP_FETCH_STALL_YES = 1;
  localparam int GEN_FC_DIV_TIMING_CP_IRQ_LATENCY_LE37 = 0;
  localparam int GEN_FC_DIV_TIMING_CP_IRQ_LATENCY_GT37 = 1;
  covergroup gen_div_timing_cg with function sample(int v_cp_op, int v_cp_dit, int v_cp_div0, int v_cp_delta, int v_cp_event_mid, int v_cp_wb_defer, int v_cp_prev, int v_cp_next, int v_cp_fetch_stall, int v_cp_irq_latency);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_op: coverpoint v_cp_op { bins div= {0}; bins divu= {1}; bins rem= {2}; bins remu= {3}; ignore_bins na = {-1}; }
    cp_dit: coverpoint v_cp_dit { bins off= {0}; bins on= {1}; ignore_bins na = {-1}; }
    cp_div0: coverpoint v_cp_div0 { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_delta: coverpoint v_cp_delta { bins d2= {0}; bins d37= {1}; bins other= {2}; ignore_bins na = {-1}; }
    cp_event_mid: coverpoint v_cp_event_mid { bins none= {0}; bins irq= {1}; bins debug_req= {2}; bins nmi= {3}; ignore_bins na = {-1}; }
    cp_wb_defer: coverpoint v_cp_wb_defer { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_prev: coverpoint v_cp_prev { bins load_dep= {0}; bins mul= {1}; bins div= {2}; bins alu= {3}; bins other= {4}; ignore_bins na = {-1}; }
    cp_next: coverpoint v_cp_next { bins dep_alu= {0}; bins mul= {1}; bins div= {2}; bins other= {3}; ignore_bins na = {-1}; }
    cp_fetch_stall: coverpoint v_cp_fetch_stall { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_irq_latency: coverpoint v_cp_irq_latency { bins le37= {0}; bins gt37= {1}; ignore_bins na = {-1}; }
    cr_dit_div0_delta: cross cp_dit, cp_div0, cp_delta, cp_fetch_stall, cp_wb_defer {
      bins dit0_nodiv0_d37= binsof(cp_dit.off) && binsof(cp_div0.no) && binsof(cp_delta.d37) && binsof(cp_fetch_stall.no) && binsof(cp_wb_defer.no);
      bins dit0_div0_d2= binsof(cp_dit.off) && binsof(cp_div0.yes) && binsof(cp_delta.d2) && binsof(cp_fetch_stall.no) && binsof(cp_wb_defer.no);
      bins dit1_div0_d37= binsof(cp_dit.on) && binsof(cp_div0.yes) && binsof(cp_delta.d37) && binsof(cp_fetch_stall.no) && binsof(cp_wb_defer.no);
      bins dit1_nodiv0_d37= binsof(cp_dit.on) && binsof(cp_div0.no) && binsof(cp_delta.d37) && binsof(cp_fetch_stall.no) && binsof(cp_wb_defer.no);
    }
    cr_op_div0: cross cp_op, cp_div0, cp_dit {
      bins div_no_off= binsof(cp_op.div) && binsof(cp_div0.no) && binsof(cp_dit.off);
      bins div_no_on= binsof(cp_op.div) && binsof(cp_div0.no) && binsof(cp_dit.on);
      bins div_yes_off= binsof(cp_op.div) && binsof(cp_div0.yes) && binsof(cp_dit.off);
      bins div_yes_on= binsof(cp_op.div) && binsof(cp_div0.yes) && binsof(cp_dit.on);
      bins divu_no_off= binsof(cp_op.divu) && binsof(cp_div0.no) && binsof(cp_dit.off);
      bins divu_no_on= binsof(cp_op.divu) && binsof(cp_div0.no) && binsof(cp_dit.on);
      bins divu_yes_off= binsof(cp_op.divu) && binsof(cp_div0.yes) && binsof(cp_dit.off);
      bins divu_yes_on= binsof(cp_op.divu) && binsof(cp_div0.yes) && binsof(cp_dit.on);
      bins rem_no_off= binsof(cp_op.rem) && binsof(cp_div0.no) && binsof(cp_dit.off);
      bins rem_no_on= binsof(cp_op.rem) && binsof(cp_div0.no) && binsof(cp_dit.on);
      bins rem_yes_off= binsof(cp_op.rem) && binsof(cp_div0.yes) && binsof(cp_dit.off);
      bins rem_yes_on= binsof(cp_op.rem) && binsof(cp_div0.yes) && binsof(cp_dit.on);
      bins remu_no_off= binsof(cp_op.remu) && binsof(cp_div0.no) && binsof(cp_dit.off);
      bins remu_no_on= binsof(cp_op.remu) && binsof(cp_div0.no) && binsof(cp_dit.on);
      bins remu_yes_off= binsof(cp_op.remu) && binsof(cp_div0.yes) && binsof(cp_dit.off);
      bins remu_yes_on= binsof(cp_op.remu) && binsof(cp_div0.yes) && binsof(cp_dit.on);
    }
    cr_event_div0_dit: cross cp_event_mid, cp_div0, cp_dit {
      bins debug_req_no_off= binsof(cp_event_mid.debug_req) && binsof(cp_div0.no) && binsof(cp_dit.off);
      bins debug_req_no_on= binsof(cp_event_mid.debug_req) && binsof(cp_div0.no) && binsof(cp_dit.on);
      bins debug_req_yes_off= binsof(cp_event_mid.debug_req) && binsof(cp_div0.yes) && binsof(cp_dit.off);
      bins debug_req_yes_on= binsof(cp_event_mid.debug_req) && binsof(cp_div0.yes) && binsof(cp_dit.on);
      bins irq_no_off= binsof(cp_event_mid.irq) && binsof(cp_div0.no) && binsof(cp_dit.off);
      bins irq_no_on= binsof(cp_event_mid.irq) && binsof(cp_div0.no) && binsof(cp_dit.on);
      bins irq_yes_off= binsof(cp_event_mid.irq) && binsof(cp_div0.yes) && binsof(cp_dit.off);
      bins irq_yes_on= binsof(cp_event_mid.irq) && binsof(cp_div0.yes) && binsof(cp_dit.on);
      bins nmi_no_off= binsof(cp_event_mid.nmi) && binsof(cp_div0.no) && binsof(cp_dit.off);
      bins nmi_no_on= binsof(cp_event_mid.nmi) && binsof(cp_div0.no) && binsof(cp_dit.on);
      bins nmi_yes_off= binsof(cp_event_mid.nmi) && binsof(cp_div0.yes) && binsof(cp_dit.off);
      bins nmi_yes_on= binsof(cp_event_mid.nmi) && binsof(cp_div0.yes) && binsof(cp_dit.on);
    }
    cr_op_event: cross cp_op, cp_event_mid {
      bins div_debug_req= binsof(cp_op.div) && binsof(cp_event_mid.debug_req);
      bins div_irq= binsof(cp_op.div) && binsof(cp_event_mid.irq);
      bins div_nmi= binsof(cp_op.div) && binsof(cp_event_mid.nmi);
      bins divu_debug_req= binsof(cp_op.divu) && binsof(cp_event_mid.debug_req);
      bins divu_irq= binsof(cp_op.divu) && binsof(cp_event_mid.irq);
      bins divu_nmi= binsof(cp_op.divu) && binsof(cp_event_mid.nmi);
      bins rem_debug_req= binsof(cp_op.rem) && binsof(cp_event_mid.debug_req);
      bins rem_irq= binsof(cp_op.rem) && binsof(cp_event_mid.irq);
      bins rem_nmi= binsof(cp_op.rem) && binsof(cp_event_mid.nmi);
      bins remu_debug_req= binsof(cp_op.remu) && binsof(cp_event_mid.debug_req);
      bins remu_irq= binsof(cp_op.remu) && binsof(cp_event_mid.irq);
      bins remu_nmi= binsof(cp_op.remu) && binsof(cp_event_mid.nmi);
      bins div_none= binsof(cp_op.div) && binsof(cp_event_mid.none);
      bins divu_none= binsof(cp_op.divu) && binsof(cp_event_mid.none);
      bins rem_none= binsof(cp_op.rem) && binsof(cp_event_mid.none);
      bins remu_none= binsof(cp_op.remu) && binsof(cp_event_mid.none);
    }
    cr_op_wb_defer: cross cp_op, cp_wb_defer {
      bins div_yes= binsof(cp_op.div) && binsof(cp_wb_defer.yes);
      bins divu_yes= binsof(cp_op.divu) && binsof(cp_wb_defer.yes);
      bins rem_yes= binsof(cp_op.rem) && binsof(cp_wb_defer.yes);
      bins remu_yes= binsof(cp_op.remu) && binsof(cp_wb_defer.yes);
      bins div_no= binsof(cp_op.div) && binsof(cp_wb_defer.no);
      bins divu_no= binsof(cp_op.divu) && binsof(cp_wb_defer.no);
      bins rem_no= binsof(cp_op.rem) && binsof(cp_wb_defer.no);
      bins remu_no= binsof(cp_op.remu) && binsof(cp_wb_defer.no);
    }
    cr_next_op: cross cp_next, cp_op {
      bins dep_alu_div= binsof(cp_next.dep_alu) && binsof(cp_op.div);
      bins dep_alu_divu= binsof(cp_next.dep_alu) && binsof(cp_op.divu);
      bins dep_alu_rem= binsof(cp_next.dep_alu) && binsof(cp_op.rem);
      bins dep_alu_remu= binsof(cp_next.dep_alu) && binsof(cp_op.remu);
      bins div_div= binsof(cp_next.div) && binsof(cp_op.div);
      bins div_divu= binsof(cp_next.div) && binsof(cp_op.divu);
      bins div_rem= binsof(cp_next.div) && binsof(cp_op.rem);
      bins div_remu= binsof(cp_next.div) && binsof(cp_op.remu);
      bins mul_div= binsof(cp_next.mul) && binsof(cp_op.div);
      bins mul_divu= binsof(cp_next.mul) && binsof(cp_op.divu);
      bins mul_rem= binsof(cp_next.mul) && binsof(cp_op.rem);
      bins mul_remu= binsof(cp_next.mul) && binsof(cp_op.remu);
      bins other_div= binsof(cp_next.other) && binsof(cp_op.div);
      bins other_divu= binsof(cp_next.other) && binsof(cp_op.divu);
      bins other_rem= binsof(cp_next.other) && binsof(cp_op.rem);
      bins other_remu= binsof(cp_next.other) && binsof(cp_op.remu);
    }
    cr_prev_op: cross cp_prev, cp_op {
      bins load_dep_div= binsof(cp_prev.load_dep) && binsof(cp_op.div);
      bins load_dep_divu= binsof(cp_prev.load_dep) && binsof(cp_op.divu);
      bins load_dep_rem= binsof(cp_prev.load_dep) && binsof(cp_op.rem);
      bins load_dep_remu= binsof(cp_prev.load_dep) && binsof(cp_op.remu);
      bins alu_div= binsof(cp_prev.alu) && binsof(cp_op.div);
      bins alu_divu= binsof(cp_prev.alu) && binsof(cp_op.divu);
      bins alu_rem= binsof(cp_prev.alu) && binsof(cp_op.rem);
      bins alu_remu= binsof(cp_prev.alu) && binsof(cp_op.remu);
      bins div_div= binsof(cp_prev.div) && binsof(cp_op.div);
      bins div_divu= binsof(cp_prev.div) && binsof(cp_op.divu);
      bins div_rem= binsof(cp_prev.div) && binsof(cp_op.rem);
      bins div_remu= binsof(cp_prev.div) && binsof(cp_op.remu);
      bins mul_div= binsof(cp_prev.mul) && binsof(cp_op.div);
      bins mul_divu= binsof(cp_prev.mul) && binsof(cp_op.divu);
      bins mul_rem= binsof(cp_prev.mul) && binsof(cp_op.rem);
      bins mul_remu= binsof(cp_prev.mul) && binsof(cp_op.remu);
      bins other_div= binsof(cp_prev.other) && binsof(cp_op.div);
      bins other_divu= binsof(cp_prev.other) && binsof(cp_op.divu);
      bins other_rem= binsof(cp_prev.other) && binsof(cp_op.rem);
      bins other_remu= binsof(cp_prev.other) && binsof(cp_op.remu);
    }
  endgroup

  // CG-CMP-002 (gen_cmp_imm_edges_cg), 47 coverpoint bins, 36 cross bins
  localparam int GEN_FC_CMP_IMM_EDGES_CP_ADDI4SPN_IMM_MIN = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_ADDI4SPN_IMM_MAX = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_ADDI4SPN_IMM_RAND = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LW_SW_UIMM_ZERO = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LW_SW_UIMM_MAX = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LW_SW_UIMM_RAND = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SP_UIMM_ZERO = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SP_UIMM_MAX = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SP_UIMM_RAND = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_OP_C_ADDI = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_OP_C_LI = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_OP_C_ANDI = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_MIN = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_MINUS1 = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_ZERO = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_ONE = 3;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_MAX = 4;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_RAND = 5;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_POS_MIN = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_POS_MAX = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_NEG_MIN = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_NEG_MAX = 3;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_RAND = 4;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_MIN = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_MAX = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_PLUS16 = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_MINUS16 = 3;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_RAND = 4;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SHIFT_OP_C_SRLI = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SHIFT_OP_C_SRAI = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SHIFT_OP_C_SLLI = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SHAMT_ONE = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SHAMT_MAX = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SHAMT_RAND = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_SELF = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_MAX_FWD = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_MAX_BWD = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_POS_RAND = 3;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_NEG_RAND = 4;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_SELF = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_MAX_FWD = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_MAX_BWD = 2;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_POS_RAND = 3;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_NEG_RAND = 4;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SP_WRAP_NO = 0;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_SP_WRAP_YES = 1;
  localparam int GEN_FC_CMP_IMM_EDGES_CP_LINK_PC2 = 0;
  covergroup gen_cmp_imm_edges_cg with function sample(int v_cp_addi4spn_imm, int v_cp_lw_sw_uimm, int v_cp_sp_uimm, int v_cp_ci_op, int v_cp_ci_imm6, int v_cp_lui_imm, int v_cp_addi16sp_imm, int v_cp_shift_op, int v_cp_shamt, int v_cp_cj_off, int v_cp_cb_off, int v_cp_sp_wrap, int v_cp_link);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_addi4spn_imm: coverpoint v_cp_addi4spn_imm { bins min= {0}; bins max= {1}; bins \rand = {2}; ignore_bins na = {-1}; }
    cp_lw_sw_uimm: coverpoint v_cp_lw_sw_uimm { bins zero= {0}; bins max= {1}; bins \rand = {2}; ignore_bins na = {-1}; }
    cp_sp_uimm: coverpoint v_cp_sp_uimm { bins zero= {0}; bins max= {1}; bins \rand = {2}; ignore_bins na = {-1}; }
    cp_ci_op: coverpoint v_cp_ci_op { bins c_addi= {0}; bins c_li= {1}; bins c_andi= {2}; ignore_bins na = {-1}; }
    cp_ci_imm6: coverpoint v_cp_ci_imm6 { bins min= {0}; bins minus1= {1}; bins zero= {2}; bins one= {3}; bins max= {4}; bins \rand = {5}; ignore_bins na = {-1}; }
    cp_lui_imm: coverpoint v_cp_lui_imm { bins pos_min= {0}; bins pos_max= {1}; bins neg_min= {2}; bins neg_max= {3}; bins \rand = {4}; ignore_bins na = {-1}; }
    cp_addi16sp_imm: coverpoint v_cp_addi16sp_imm { bins min= {0}; bins max= {1}; bins plus16= {2}; bins minus16= {3}; bins \rand = {4}; ignore_bins na = {-1}; }
    cp_shift_op: coverpoint v_cp_shift_op { bins c_srli= {0}; bins c_srai= {1}; bins c_slli= {2}; ignore_bins na = {-1}; }
    cp_shamt: coverpoint v_cp_shamt { bins one= {0}; bins max= {1}; bins \rand = {2}; ignore_bins na = {-1}; }
    cp_cj_off: coverpoint v_cp_cj_off { bins self= {0}; bins max_fwd= {1}; bins max_bwd= {2}; bins pos_rand= {3}; bins neg_rand= {4}; ignore_bins na = {-1}; }
    cp_cb_off: coverpoint v_cp_cb_off { bins self= {0}; bins max_fwd= {1}; bins max_bwd= {2}; bins pos_rand= {3}; bins neg_rand= {4}; ignore_bins na = {-1}; }
    cp_sp_wrap: coverpoint v_cp_sp_wrap { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_link: coverpoint v_cp_link { bins pc2= {0}; ignore_bins na = {-1}; }
    cr_ci: cross cp_ci_op, cp_ci_imm6 {
      bins c_addi_max= binsof(cp_ci_op.c_addi) && binsof(cp_ci_imm6.max);
      bins c_addi_min= binsof(cp_ci_op.c_addi) && binsof(cp_ci_imm6.min);
      bins c_andi_max= binsof(cp_ci_op.c_andi) && binsof(cp_ci_imm6.max);
      bins c_andi_min= binsof(cp_ci_op.c_andi) && binsof(cp_ci_imm6.min);
      bins c_li_max= binsof(cp_ci_op.c_li) && binsof(cp_ci_imm6.max);
      bins c_li_min= binsof(cp_ci_op.c_li) && binsof(cp_ci_imm6.min);
      bins c_andi_zero= binsof(cp_ci_op.c_andi) && binsof(cp_ci_imm6.zero);
      bins c_li_zero= binsof(cp_ci_op.c_li) && binsof(cp_ci_imm6.zero);
      bins c_addi_minus1= binsof(cp_ci_op.c_addi) && binsof(cp_ci_imm6.minus1);
      bins c_addi_one= binsof(cp_ci_op.c_addi) && binsof(cp_ci_imm6.one);
      bins c_andi_minus1= binsof(cp_ci_op.c_andi) && binsof(cp_ci_imm6.minus1);
      bins c_andi_one= binsof(cp_ci_op.c_andi) && binsof(cp_ci_imm6.one);
      bins c_li_minus1= binsof(cp_ci_op.c_li) && binsof(cp_ci_imm6.minus1);
      bins c_li_one= binsof(cp_ci_op.c_li) && binsof(cp_ci_imm6.one);
      bins c_addi_rand= binsof(cp_ci_op.c_addi) && binsof(cp_ci_imm6.\rand );
      bins c_andi_rand= binsof(cp_ci_op.c_andi) && binsof(cp_ci_imm6.\rand );
      bins c_li_rand= binsof(cp_ci_op.c_li) && binsof(cp_ci_imm6.\rand );
    }
    cr_sp_wrap: cross cp_addi16sp_imm, cp_sp_wrap {
      bins max_no= binsof(cp_addi16sp_imm.max) && binsof(cp_sp_wrap.no);
      bins min_no= binsof(cp_addi16sp_imm.min) && binsof(cp_sp_wrap.no);
      bins minus16_no= binsof(cp_addi16sp_imm.minus16) && binsof(cp_sp_wrap.no);
      bins plus16_no= binsof(cp_addi16sp_imm.plus16) && binsof(cp_sp_wrap.no);
      bins rand_no= binsof(cp_addi16sp_imm.\rand ) && binsof(cp_sp_wrap.no);
      bins max_yes= binsof(cp_addi16sp_imm.max) && binsof(cp_sp_wrap.yes);
      bins min_yes= binsof(cp_addi16sp_imm.min) && binsof(cp_sp_wrap.yes);
      bins minus16_yes= binsof(cp_addi16sp_imm.minus16) && binsof(cp_sp_wrap.yes);
      bins plus16_yes= binsof(cp_addi16sp_imm.plus16) && binsof(cp_sp_wrap.yes);
      bins rand_yes= binsof(cp_addi16sp_imm.\rand ) && binsof(cp_sp_wrap.yes);
    }
    cr_shift: cross cp_shift_op, cp_shamt {
      bins c_slli_max= binsof(cp_shift_op.c_slli) && binsof(cp_shamt.max);
      bins c_slli_one= binsof(cp_shift_op.c_slli) && binsof(cp_shamt.one);
      bins c_slli_rand= binsof(cp_shift_op.c_slli) && binsof(cp_shamt.\rand );
      bins c_srai_max= binsof(cp_shift_op.c_srai) && binsof(cp_shamt.max);
      bins c_srai_one= binsof(cp_shift_op.c_srai) && binsof(cp_shamt.one);
      bins c_srai_rand= binsof(cp_shift_op.c_srai) && binsof(cp_shamt.\rand );
      bins c_srli_max= binsof(cp_shift_op.c_srli) && binsof(cp_shamt.max);
      bins c_srli_one= binsof(cp_shift_op.c_srli) && binsof(cp_shamt.one);
      bins c_srli_rand= binsof(cp_shift_op.c_srli) && binsof(cp_shamt.\rand );
    }
  endgroup

  // CG-IC-006 (gen_ic_ecc_cg), 24 coverpoint bins, 16 cross bins
  localparam int GEN_FC_IC_ECC_CP_RAM_TAG = 0;
  localparam int GEN_FC_IC_ECC_CP_RAM_DATA = 1;
  localparam int GEN_FC_IC_ECC_CP_BITS_SINGLE = 0;
  localparam int GEN_FC_IC_ECC_CP_BITS_DOUBLE = 1;
  localparam int GEN_FC_IC_ECC_CP_WAY_WAY0 = 0;
  localparam int GEN_FC_IC_ECC_CP_WAY_WAY1 = 1;
  localparam int GEN_FC_IC_ECC_CP_BEAT_BEAT0 = 0;
  localparam int GEN_FC_IC_ECC_CP_BEAT_BEAT1 = 1;
  localparam int GEN_FC_IC_ECC_CP_ALERT_PULSES_ONE = 0;
  localparam int GEN_FC_IC_ECC_CP_INVAL_WAYS_ALL_WAYS = 0;
  localparam int GEN_FC_IC_ECC_CP_INVAL_WAYS_HIT_WAY_ONLY = 1;
  localparam int GEN_FC_IC_ECC_CP_REFETCH_YES = 0;
  localparam int GEN_FC_IC_ECC_CP_MAJOR_NMI_QUIET_YES = 0;
  localparam int GEN_FC_IC_ECC_CP_LOOKUPS_BLOCKED_NEXT_YES = 0;
  localparam int GEN_FC_IC_ECC_CP_NO_ALERT_CASE_UNUSED_WAY_DATA = 0;
  localparam int GEN_FC_IC_ECC_CP_NO_ALERT_CASE_DISABLED_CACHE = 1;
  localparam int GEN_FC_IC_ECC_CP_NO_ALERT_CASE_DURING_INVALIDATION = 2;
  localparam int GEN_FC_IC_ECC_CP_NO_ALERT_CASE_UNINITIALISED_DATA_RAM = 3;
  localparam int GEN_FC_IC_ECC_CP_NO_ALERT_CASE_MASKED_DUPLICATE_COPY = 4;
  localparam int GEN_FC_IC_ECC_CP_MULTIWAY_MISMATCH_ALERT_OR_WRONG = 0;
  localparam int GEN_FC_IC_ECC_CP_MULTIWAY_MISMATCH_MASKED = 1;
  localparam int GEN_FC_IC_ECC_CP_KNOB_NONE = 0;
  localparam int GEN_FC_IC_ECC_CP_KNOB_RARE = 1;
  localparam int GEN_FC_IC_ECC_CP_KNOB_FREQUENT = 2;
  covergroup gen_ic_ecc_cg with function sample(int v_cp_ram, int v_cp_bits, int v_cp_way, int v_cp_beat, int v_cp_alert_pulses, int v_cp_inval_ways, int v_cp_refetch, int v_cp_major_nmi_quiet, int v_cp_lookups_blocked_next, int v_cp_no_alert_case, int v_cp_multiway_mismatch, int v_cp_knob);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_ram: coverpoint v_cp_ram { bins tag= {0}; bins data= {1}; ignore_bins na = {-1}; }
    cp_bits: coverpoint v_cp_bits { bins single= {0}; bins double= {1}; ignore_bins na = {-1}; }
    cp_way: coverpoint v_cp_way { bins way0= {0}; bins way1= {1}; ignore_bins na = {-1}; }
    cp_beat: coverpoint v_cp_beat { bins beat0= {0}; bins beat1= {1}; ignore_bins na = {-1}; }
    cp_alert_pulses: coverpoint v_cp_alert_pulses { bins one= {0}; ignore_bins na = {-1}; }
    cp_inval_ways: coverpoint v_cp_inval_ways { bins all_ways= {0}; bins hit_way_only= {1}; ignore_bins na = {-1}; }
    cp_refetch: coverpoint v_cp_refetch { bins yes= {0}; ignore_bins na = {-1}; }
    cp_major_nmi_quiet: coverpoint v_cp_major_nmi_quiet { bins yes= {0}; ignore_bins na = {-1}; }
    cp_lookups_blocked_next: coverpoint v_cp_lookups_blocked_next { bins yes= {0}; ignore_bins na = {-1}; }
    cp_no_alert_case: coverpoint v_cp_no_alert_case { bins unused_way_data= {0}; bins disabled_cache= {1}; bins during_invalidation= {2}; bins uninitialised_data_ram= {3}; bins masked_duplicate_copy= {4}; ignore_bins na = {-1}; }
    cp_multiway_mismatch: coverpoint v_cp_multiway_mismatch { bins alert_or_wrong= {0}; bins masked= {1}; ignore_bins na = {-1}; }
    cp_knob: coverpoint v_cp_knob { bins none= {0}; bins rare= {1}; bins frequent= {2}; ignore_bins na = {-1}; }
    cr_ram_x_bits_x_way: cross cp_ram, cp_bits, cp_way {
      bins tag_double_way0= binsof(cp_ram.tag) && binsof(cp_bits.double) && binsof(cp_way.way0);
      bins tag_double_way1= binsof(cp_ram.tag) && binsof(cp_bits.double) && binsof(cp_way.way1);
      bins tag_single_way0= binsof(cp_ram.tag) && binsof(cp_bits.single) && binsof(cp_way.way0);
      bins tag_single_way1= binsof(cp_ram.tag) && binsof(cp_bits.single) && binsof(cp_way.way1);
      bins data_double_way0= binsof(cp_ram.data) && binsof(cp_bits.double) && binsof(cp_way.way0);
      bins data_double_way1= binsof(cp_ram.data) && binsof(cp_bits.double) && binsof(cp_way.way1);
      bins data_single_way0= binsof(cp_ram.data) && binsof(cp_bits.single) && binsof(cp_way.way0);
      bins data_single_way1= binsof(cp_ram.data) && binsof(cp_bits.single) && binsof(cp_way.way1);
    }
    cr_ram_x_inval: cross cp_ram, cp_inval_ways {
      bins tag_all= binsof(cp_ram.tag) && binsof(cp_inval_ways.all_ways);
      bins data_hit= binsof(cp_ram.data) && binsof(cp_inval_ways.hit_way_only);
    }
    cr_data_x_beat: cross cp_ram, cp_beat {
      bins data_beat0= binsof(cp_ram.data) && binsof(cp_beat.beat0);
      bins data_beat1= binsof(cp_ram.data) && binsof(cp_beat.beat1);
    }
    cr_bits_x_rate: cross cp_bits, cp_knob {
      bins double_frequent= binsof(cp_bits.double) && binsof(cp_knob.frequent);
      bins single_frequent= binsof(cp_bits.single) && binsof(cp_knob.frequent);
      bins double_rare= binsof(cp_bits.double) && binsof(cp_knob.rare);
      bins single_rare= binsof(cp_bits.single) && binsof(cp_knob.rare);
    }
  endgroup

  // CG-PMP-001 (gen_pmp_cfg_write_cg), 54 coverpoint bins, 100 cross bins
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E0 = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E1 = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E2 = 2;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E3 = 3;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E4 = 4;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E5 = 5;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E6 = 6;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E7 = 7;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E8 = 8;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E9 = 9;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E10 = 10;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E11 = 11;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E12 = 12;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E13 = 13;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E14 = 14;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E15 = 15;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_OP_CSRRW = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_OP_CSRRS = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_OP_CSRRC = 2;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_MODE_OFF = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_MODE_TOR = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_MODE_NA4 = 2;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_MODE_NAPOT = 3;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0000 = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0001 = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0010 = 2;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0011 = 3;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0100 = 4;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0101 = 5;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0110 = 6;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0111 = 7;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C1000 = 8;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C1001 = 9;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C1010 = 10;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C1011 = 11;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C1100 = 12;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C1101 = 13;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C1110 = 14;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C1111 = 15;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_RES_BITS_ZERO = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_RES_BITS_NONZERO = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_MML_MML0 = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_MML_MML1 = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_RLB_RLB0 = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_RLB_RLB1 = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_PRELOCK_UNLOCKED = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_PRELOCK_LOCKED = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_OUTCOME_WRITTEN = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_OUTCOME_W_DROPPED = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_OUTCOME_IGNORED_LOCK = 2;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_OUTCOME_IGNORED_MML_EXEC = 3;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WORD_LOCKMIX_NONE = 0;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WORD_LOCKMIX_SOME = 1;
  localparam int GEN_FC_PMP_CFG_WRITE_CP_WORD_LOCKMIX_ALL = 2;
  covergroup gen_pmp_cfg_write_cg with function sample(int v_cp_entry, int v_cp_op, int v_cp_wr_mode, int v_cp_wr_lrwx, int v_cp_res_bits, int v_cp_mml, int v_cp_rlb, int v_cp_prelock, int v_cp_outcome, int v_cp_word_lockmix);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_entry: coverpoint v_cp_entry { bins e0= {0}; bins e1= {1}; bins e2= {2}; bins e3= {3}; bins e4= {4}; bins e5= {5}; bins e6= {6}; bins e7= {7}; bins e8= {8}; bins e9= {9}; bins e10= {10}; bins e11= {11}; bins e12= {12}; bins e13= {13}; bins e14= {14}; bins e15= {15}; ignore_bins na = {-1}; }
    cp_op: coverpoint v_cp_op { bins csrrw= {0}; bins csrrs= {1}; bins csrrc= {2}; ignore_bins na = {-1}; }
    cp_wr_mode: coverpoint v_cp_wr_mode { bins off= {0}; bins tor= {1}; bins na4= {2}; bins napot= {3}; ignore_bins na = {-1}; }
    cp_wr_lrwx: coverpoint v_cp_wr_lrwx { bins c0000= {0}; bins c0001= {1}; bins c0010= {2}; bins c0011= {3}; bins c0100= {4}; bins c0101= {5}; bins c0110= {6}; bins c0111= {7}; bins c1000= {8}; bins c1001= {9}; bins c1010= {10}; bins c1011= {11}; bins c1100= {12}; bins c1101= {13}; bins c1110= {14}; bins c1111= {15}; ignore_bins na = {-1}; }
    cp_res_bits: coverpoint v_cp_res_bits { bins zero= {0}; bins nonzero= {1}; ignore_bins na = {-1}; }
    cp_mml: coverpoint v_cp_mml { bins mml0= {0}; bins mml1= {1}; ignore_bins na = {-1}; }
    cp_rlb: coverpoint v_cp_rlb { bins rlb0= {0}; bins rlb1= {1}; ignore_bins na = {-1}; }
    cp_prelock: coverpoint v_cp_prelock { bins unlocked= {0}; bins locked= {1}; ignore_bins na = {-1}; }
    cp_outcome: coverpoint v_cp_outcome { bins written= {0}; bins w_dropped= {1}; bins ignored_lock= {2}; bins ignored_mml_exec= {3}; ignore_bins na = {-1}; }
    cp_word_lockmix: coverpoint v_cp_word_lockmix { bins none= {0}; bins some= {1}; bins all= {2}; ignore_bins na = {-1}; }
    cr_mode_lrwx: cross cp_wr_mode, cp_wr_lrwx {
      bins na4_c0000= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c0000);
      bins na4_c0001= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c0001);
      bins na4_c0010= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c0010);
      bins na4_c0011= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c0011);
      bins na4_c0100= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c0100);
      bins na4_c0101= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c0101);
      bins na4_c0110= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c0110);
      bins na4_c0111= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c0111);
      bins na4_c1000= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c1000);
      bins na4_c1001= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c1001);
      bins na4_c1010= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c1010);
      bins na4_c1011= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c1011);
      bins na4_c1100= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c1100);
      bins na4_c1101= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c1101);
      bins na4_c1110= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c1110);
      bins na4_c1111= binsof(cp_wr_mode.na4) && binsof(cp_wr_lrwx.c1111);
      bins napot_c0000= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c0000);
      bins napot_c0001= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c0001);
      bins napot_c0010= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c0010);
      bins napot_c0011= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c0011);
      bins napot_c0100= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c0100);
      bins napot_c0101= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c0101);
      bins napot_c0110= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c0110);
      bins napot_c0111= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c0111);
      bins napot_c1000= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c1000);
      bins napot_c1001= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c1001);
      bins napot_c1010= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c1010);
      bins napot_c1011= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c1011);
      bins napot_c1100= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c1100);
      bins napot_c1101= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c1101);
      bins napot_c1110= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c1110);
      bins napot_c1111= binsof(cp_wr_mode.napot) && binsof(cp_wr_lrwx.c1111);
      bins off_c0000= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c0000);
      bins off_c0001= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c0001);
      bins off_c0010= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c0010);
      bins off_c0011= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c0011);
      bins off_c0100= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c0100);
      bins off_c0101= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c0101);
      bins off_c0110= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c0110);
      bins off_c0111= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c0111);
      bins off_c1000= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c1000);
      bins off_c1001= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c1001);
      bins off_c1010= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c1010);
      bins off_c1011= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c1011);
      bins off_c1100= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c1100);
      bins off_c1101= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c1101);
      bins off_c1110= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c1110);
      bins off_c1111= binsof(cp_wr_mode.off) && binsof(cp_wr_lrwx.c1111);
      bins tor_c0000= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c0000);
      bins tor_c0001= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c0001);
      bins tor_c0010= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c0010);
      bins tor_c0011= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c0011);
      bins tor_c0100= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c0100);
      bins tor_c0101= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c0101);
      bins tor_c0110= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c0110);
      bins tor_c0111= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c0111);
      bins tor_c1000= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c1000);
      bins tor_c1001= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c1001);
      bins tor_c1010= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c1010);
      bins tor_c1011= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c1011);
      bins tor_c1100= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c1100);
      bins tor_c1101= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c1101);
      bins tor_c1110= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c1110);
      bins tor_c1111= binsof(cp_wr_mode.tor) && binsof(cp_wr_lrwx.c1111);
    }
    cr_res_op: cross cp_res_bits, cp_op {
      bins nonzero_csrrc= binsof(cp_res_bits.nonzero) && binsof(cp_op.csrrc);
      bins nonzero_csrrs= binsof(cp_res_bits.nonzero) && binsof(cp_op.csrrs);
      bins nonzero_csrrw= binsof(cp_res_bits.nonzero) && binsof(cp_op.csrrw);
    }
    cr_rw01_mml: cross cp_wr_lrwx, cp_mml, cp_rlb, cp_outcome {
      bins rw01_mml0_wdrop= (binsof(cp_wr_lrwx.c0010) || binsof(cp_wr_lrwx.c0011) || binsof(cp_wr_lrwx.c1010) || binsof(cp_wr_lrwx.c1011)) && binsof(cp_mml.mml0) && binsof(cp_outcome.w_dropped);
      bins rw01_mml1_l1_rlb1_stored= (binsof(cp_wr_lrwx.c1010) || binsof(cp_wr_lrwx.c1011)) && binsof(cp_mml.mml1) && binsof(cp_rlb.rlb1) && binsof(cp_outcome.written);
      bins rw01_mml1_stored= (binsof(cp_wr_lrwx.c0010) || binsof(cp_wr_lrwx.c0011)) && binsof(cp_mml.mml1) && binsof(cp_outcome.written);
      bins rw01_mml1_l1_rlb0_suppressed= (binsof(cp_wr_lrwx.c1010) || binsof(cp_wr_lrwx.c1011)) && binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.ignored_mml_exec);
    }
    cr_lock_outcome: cross cp_prelock, cp_rlb, cp_outcome {
      bins locked_rlb0_ignored= binsof(cp_prelock.locked) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.ignored_lock);
      bins unlocked_rlb0_written= binsof(cp_prelock.unlocked) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.written);
      bins locked_rlb1_written= binsof(cp_prelock.locked) && binsof(cp_rlb.rlb1) && binsof(cp_outcome.written);
      bins unlocked_rlb1_written= binsof(cp_prelock.unlocked) && binsof(cp_rlb.rlb1) && binsof(cp_outcome.written);
    }
    cr_lockmix_op: cross cp_word_lockmix, cp_op {
      bins some_csrrc= binsof(cp_word_lockmix.some) && binsof(cp_op.csrrc);
      bins some_csrrs= binsof(cp_word_lockmix.some) && binsof(cp_op.csrrs);
      bins some_csrrw= binsof(cp_word_lockmix.some) && binsof(cp_op.csrrw);
    }
    cr_prelock_wrl: cross cp_prelock, cp_wr_lrwx, cp_outcome, cp_mml {
      bins setlock_c1000= binsof(cp_prelock.unlocked) && binsof(cp_wr_lrwx.c1000) && binsof(cp_outcome.written) && binsof(cp_mml.mml0);
      bins setlock_c1001= binsof(cp_prelock.unlocked) && binsof(cp_wr_lrwx.c1001) && binsof(cp_outcome.written) && binsof(cp_mml.mml0);
      bins setlock_c1100= binsof(cp_prelock.unlocked) && binsof(cp_wr_lrwx.c1100) && binsof(cp_outcome.written) && binsof(cp_mml.mml0);
      bins setlock_c1101= binsof(cp_prelock.unlocked) && binsof(cp_wr_lrwx.c1101) && binsof(cp_outcome.written) && binsof(cp_mml.mml0);
      bins setlock_c1110= binsof(cp_prelock.unlocked) && binsof(cp_wr_lrwx.c1110) && binsof(cp_outcome.written) && binsof(cp_mml.mml0);
      bins setlock_c1111= binsof(cp_prelock.unlocked) && binsof(cp_wr_lrwx.c1111) && binsof(cp_outcome.written) && binsof(cp_mml.mml0);
    }
    cr_mml_exec_suppress: cross cp_mml, cp_rlb, cp_wr_lrwx, cp_outcome {
      bins rlb0_c1001_suppressed= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_wr_lrwx.c1001) && binsof(cp_outcome.ignored_mml_exec);
      bins rlb0_c1010_suppressed= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_wr_lrwx.c1010) && binsof(cp_outcome.ignored_mml_exec);
      bins rlb0_c1011_suppressed= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_wr_lrwx.c1011) && binsof(cp_outcome.ignored_mml_exec);
      bins rlb0_c1101_suppressed= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_wr_lrwx.c1101) && binsof(cp_outcome.ignored_mml_exec);
      bins rlb1_c1001_written= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb1) && binsof(cp_wr_lrwx.c1001) && binsof(cp_outcome.written);
      bins rlb1_c1010_written= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb1) && binsof(cp_wr_lrwx.c1010) && binsof(cp_outcome.written);
      bins rlb1_c1011_written= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb1) && binsof(cp_wr_lrwx.c1011) && binsof(cp_outcome.written);
      bins rlb1_c1101_written= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb1) && binsof(cp_wr_lrwx.c1101) && binsof(cp_outcome.written);
    }
    cr_suppress_mode: cross cp_outcome, cp_wr_mode {
      bins na4= binsof(cp_outcome.ignored_mml_exec) && binsof(cp_wr_mode.na4);
      bins napot= binsof(cp_outcome.ignored_mml_exec) && binsof(cp_wr_mode.napot);
      bins tor= binsof(cp_outcome.ignored_mml_exec) && binsof(cp_wr_mode.tor);
      bins off= binsof(cp_outcome.ignored_mml_exec) && binsof(cp_wr_mode.off);
    }
    cr_mml_nonexec_accept: cross cp_mml, cp_rlb, cp_wr_lrwx, cp_outcome {
      bins c1000_written= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_wr_lrwx.c1000) && binsof(cp_outcome.written);
      bins c1100_written= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_wr_lrwx.c1100) && binsof(cp_outcome.written);
      bins c1110_written= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_wr_lrwx.c1110) && binsof(cp_outcome.written);
      bins c1111_written= binsof(cp_mml.mml1) && binsof(cp_rlb.rlb0) && binsof(cp_wr_lrwx.c1111) && binsof(cp_outcome.written);
    }
  endgroup

  // CG-PMP-002 (gen_pmp_addr_write_cg), 39 coverpoint bins, 70 cross bins
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A0 = 0;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A1 = 1;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A2 = 2;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A3 = 3;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A4 = 4;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A5 = 5;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A6 = 6;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A7 = 7;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A8 = 8;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A9 = 9;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A10 = 10;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A11 = 11;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A12 = 12;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A13 = 13;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A14 = 14;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_IDX_A15 = 15;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_OP_CSRRW = 0;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_OP_CSRRS = 1;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_OP_CSRRC = 2;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_SELF_LOCK_UNLOCKED = 0;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_SELF_LOCK_LOCKED = 1;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_NEXT_UNLOCKED_TOR = 0;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_NEXT_UNLOCKED_OTHER = 1;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_NEXT_LOCKED_TOR = 2;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_NEXT_LOCKED_OTHER = 3;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_TOP = 4;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_RLB_RLB0 = 0;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_RLB_RLB1 = 1;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_OUTCOME_WRITTEN = 0;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_OUTCOME_IGNORED_SELF_LOCK = 1;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_OUTCOME_IGNORED_TOR_LOCK = 2;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_HI_BITS_NONE = 0;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_HI_BITS_BIT30 = 1;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_HI_BITS_BIT31 = 2;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_HI_BITS_BOTH = 3;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_SELF_MODE_OFF = 0;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_SELF_MODE_TOR = 1;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_SELF_MODE_NA4 = 2;
  localparam int GEN_FC_PMP_ADDR_WRITE_CP_SELF_MODE_NAPOT = 3;
  covergroup gen_pmp_addr_write_cg with function sample(int v_cp_idx, int v_cp_op, int v_cp_self_lock, int v_cp_next_cfg, int v_cp_rlb, int v_cp_outcome, int v_cp_hi_bits, int v_cp_self_mode);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_idx: coverpoint v_cp_idx { bins a0= {0}; bins a1= {1}; bins a2= {2}; bins a3= {3}; bins a4= {4}; bins a5= {5}; bins a6= {6}; bins a7= {7}; bins a8= {8}; bins a9= {9}; bins a10= {10}; bins a11= {11}; bins a12= {12}; bins a13= {13}; bins a14= {14}; bins a15= {15}; ignore_bins na = {-1}; }
    cp_op: coverpoint v_cp_op { bins csrrw= {0}; bins csrrs= {1}; bins csrrc= {2}; ignore_bins na = {-1}; }
    cp_self_lock: coverpoint v_cp_self_lock { bins unlocked= {0}; bins locked= {1}; ignore_bins na = {-1}; }
    cp_next_cfg: coverpoint v_cp_next_cfg { bins next_unlocked_tor= {0}; bins next_unlocked_other= {1}; bins next_locked_tor= {2}; bins next_locked_other= {3}; bins top= {4}; ignore_bins na = {-1}; }
    cp_rlb: coverpoint v_cp_rlb { bins rlb0= {0}; bins rlb1= {1}; ignore_bins na = {-1}; }
    cp_outcome: coverpoint v_cp_outcome { bins written= {0}; bins ignored_self_lock= {1}; bins ignored_tor_lock= {2}; ignore_bins na = {-1}; }
    cp_hi_bits: coverpoint v_cp_hi_bits { bins none= {0}; bins bit30= {1}; bins bit31= {2}; bins both= {3}; ignore_bins na = {-1}; }
    cp_self_mode: coverpoint v_cp_self_mode { bins off= {0}; bins tor= {1}; bins na4= {2}; bins napot= {3}; ignore_bins na = {-1}; }
    cr_hi_mode: cross cp_hi_bits, cp_self_mode {
      bins bit30_na4= binsof(cp_hi_bits.bit30) && binsof(cp_self_mode.na4);
      bins bit30_napot= binsof(cp_hi_bits.bit30) && binsof(cp_self_mode.napot);
      bins bit30_off= binsof(cp_hi_bits.bit30) && binsof(cp_self_mode.off);
      bins bit30_tor= binsof(cp_hi_bits.bit30) && binsof(cp_self_mode.tor);
      bins bit31_na4= binsof(cp_hi_bits.bit31) && binsof(cp_self_mode.na4);
      bins bit31_napot= binsof(cp_hi_bits.bit31) && binsof(cp_self_mode.napot);
      bins bit31_off= binsof(cp_hi_bits.bit31) && binsof(cp_self_mode.off);
      bins bit31_tor= binsof(cp_hi_bits.bit31) && binsof(cp_self_mode.tor);
      bins both_na4= binsof(cp_hi_bits.both) && binsof(cp_self_mode.na4);
      bins both_napot= binsof(cp_hi_bits.both) && binsof(cp_self_mode.napot);
      bins both_off= binsof(cp_hi_bits.both) && binsof(cp_self_mode.off);
      bins both_tor= binsof(cp_hi_bits.both) && binsof(cp_self_mode.tor);
    }
    cr_self_lock: cross cp_self_lock, cp_rlb, cp_outcome {
      bins unlocked_rlb0_written= binsof(cp_self_lock.unlocked) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.written);
      bins locked_rlb0_ignored= binsof(cp_self_lock.locked) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.ignored_self_lock);
      bins locked_rlb1_written= binsof(cp_self_lock.locked) && binsof(cp_rlb.rlb1) && binsof(cp_outcome.written);
    }
    cr_idx_op: cross cp_idx, cp_op {
      bins a0_csrrc= binsof(cp_idx.a0) && binsof(cp_op.csrrc);
      bins a0_csrrs= binsof(cp_idx.a0) && binsof(cp_op.csrrs);
      bins a0_csrrw= binsof(cp_idx.a0) && binsof(cp_op.csrrw);
      bins a10_csrrc= binsof(cp_idx.a10) && binsof(cp_op.csrrc);
      bins a10_csrrs= binsof(cp_idx.a10) && binsof(cp_op.csrrs);
      bins a10_csrrw= binsof(cp_idx.a10) && binsof(cp_op.csrrw);
      bins a11_csrrc= binsof(cp_idx.a11) && binsof(cp_op.csrrc);
      bins a11_csrrs= binsof(cp_idx.a11) && binsof(cp_op.csrrs);
      bins a11_csrrw= binsof(cp_idx.a11) && binsof(cp_op.csrrw);
      bins a12_csrrc= binsof(cp_idx.a12) && binsof(cp_op.csrrc);
      bins a12_csrrs= binsof(cp_idx.a12) && binsof(cp_op.csrrs);
      bins a12_csrrw= binsof(cp_idx.a12) && binsof(cp_op.csrrw);
      bins a13_csrrc= binsof(cp_idx.a13) && binsof(cp_op.csrrc);
      bins a13_csrrs= binsof(cp_idx.a13) && binsof(cp_op.csrrs);
      bins a13_csrrw= binsof(cp_idx.a13) && binsof(cp_op.csrrw);
      bins a14_csrrc= binsof(cp_idx.a14) && binsof(cp_op.csrrc);
      bins a14_csrrs= binsof(cp_idx.a14) && binsof(cp_op.csrrs);
      bins a14_csrrw= binsof(cp_idx.a14) && binsof(cp_op.csrrw);
      bins a15_csrrc= binsof(cp_idx.a15) && binsof(cp_op.csrrc);
      bins a15_csrrs= binsof(cp_idx.a15) && binsof(cp_op.csrrs);
      bins a15_csrrw= binsof(cp_idx.a15) && binsof(cp_op.csrrw);
      bins a1_csrrc= binsof(cp_idx.a1) && binsof(cp_op.csrrc);
      bins a1_csrrs= binsof(cp_idx.a1) && binsof(cp_op.csrrs);
      bins a1_csrrw= binsof(cp_idx.a1) && binsof(cp_op.csrrw);
      bins a2_csrrc= binsof(cp_idx.a2) && binsof(cp_op.csrrc);
      bins a2_csrrs= binsof(cp_idx.a2) && binsof(cp_op.csrrs);
      bins a2_csrrw= binsof(cp_idx.a2) && binsof(cp_op.csrrw);
      bins a3_csrrc= binsof(cp_idx.a3) && binsof(cp_op.csrrc);
      bins a3_csrrs= binsof(cp_idx.a3) && binsof(cp_op.csrrs);
      bins a3_csrrw= binsof(cp_idx.a3) && binsof(cp_op.csrrw);
      bins a4_csrrc= binsof(cp_idx.a4) && binsof(cp_op.csrrc);
      bins a4_csrrs= binsof(cp_idx.a4) && binsof(cp_op.csrrs);
      bins a4_csrrw= binsof(cp_idx.a4) && binsof(cp_op.csrrw);
      bins a5_csrrc= binsof(cp_idx.a5) && binsof(cp_op.csrrc);
      bins a5_csrrs= binsof(cp_idx.a5) && binsof(cp_op.csrrs);
      bins a5_csrrw= binsof(cp_idx.a5) && binsof(cp_op.csrrw);
      bins a6_csrrc= binsof(cp_idx.a6) && binsof(cp_op.csrrc);
      bins a6_csrrs= binsof(cp_idx.a6) && binsof(cp_op.csrrs);
      bins a6_csrrw= binsof(cp_idx.a6) && binsof(cp_op.csrrw);
      bins a7_csrrc= binsof(cp_idx.a7) && binsof(cp_op.csrrc);
      bins a7_csrrs= binsof(cp_idx.a7) && binsof(cp_op.csrrs);
      bins a7_csrrw= binsof(cp_idx.a7) && binsof(cp_op.csrrw);
      bins a8_csrrc= binsof(cp_idx.a8) && binsof(cp_op.csrrc);
      bins a8_csrrs= binsof(cp_idx.a8) && binsof(cp_op.csrrs);
      bins a8_csrrw= binsof(cp_idx.a8) && binsof(cp_op.csrrw);
      bins a9_csrrc= binsof(cp_idx.a9) && binsof(cp_op.csrrc);
      bins a9_csrrs= binsof(cp_idx.a9) && binsof(cp_op.csrrs);
      bins a9_csrrw= binsof(cp_idx.a9) && binsof(cp_op.csrrw);
    }
    cr_tor_lock: cross cp_self_lock, cp_next_cfg, cp_rlb, cp_outcome {
      bins nl_tor_rlb0_ignored= binsof(cp_self_lock.unlocked) && binsof(cp_next_cfg.next_locked_tor) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.ignored_tor_lock);
      bins nl_other_rlb0_written= binsof(cp_self_lock.unlocked) && binsof(cp_next_cfg.next_locked_other) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.written);
      bins nu_tor_rlb0_written= binsof(cp_self_lock.unlocked) && binsof(cp_next_cfg.next_unlocked_tor) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.written);
      bins top_rlb0_written= binsof(cp_self_lock.unlocked) && binsof(cp_next_cfg.top) && binsof(cp_rlb.rlb0) && binsof(cp_outcome.written);
      bins nl_tor_rlb1_written= binsof(cp_self_lock.unlocked) && binsof(cp_next_cfg.next_locked_tor) && binsof(cp_rlb.rlb1) && binsof(cp_outcome.written);
    }
    cr_top_lock: cross cp_idx, cp_self_lock, cp_outcome {
      bins top_locked_ignored= binsof(cp_idx.a15) && binsof(cp_self_lock.locked) && binsof(cp_outcome.ignored_self_lock);
      bins top_unlocked_written= binsof(cp_idx.a15) && binsof(cp_self_lock.unlocked) && binsof(cp_outcome.written);
    }
  endgroup

  // CG-PMP-004 (gen_pmp_csr_access_cg), 20 coverpoint bins, 46 cross bins
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_CLASS_PMPCFG = 0;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_CLASS_PMPADDR = 1;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_CLASS_MSECCFG = 2;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_CLASS_MSECCFGH = 3;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_PRIV_M = 0;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_PRIV_U = 1;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_DBG_D0 = 0;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_DBG_D1 = 1;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRW = 0;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRS = 1;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRC = 2;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRWI = 3;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRSI = 4;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRCI = 5;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_RW_READ_ONLY = 0;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_RW_WRITE = 1;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_TRAP_NONE = 0;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_TRAP_ILLEGAL = 1;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_FIRST_AFTER_RESET_NO = 0;
  localparam int GEN_FC_PMP_CSR_ACCESS_CP_FIRST_AFTER_RESET_YES = 1;
  covergroup gen_pmp_csr_access_cg with function sample(int v_cp_class, int v_cp_priv, int v_cp_dbg, int v_cp_op, int v_cp_rw, int v_cp_trap, int v_cp_first_after_reset);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_class: coverpoint v_cp_class { bins pmpcfg= {0}; bins pmpaddr= {1}; bins mseccfg= {2}; bins mseccfgh= {3}; ignore_bins na = {-1}; }
    cp_priv: coverpoint v_cp_priv { bins m= {0}; bins u= {1}; ignore_bins na = {-1}; }
    cp_dbg: coverpoint v_cp_dbg { bins d0= {0}; bins d1= {1}; ignore_bins na = {-1}; }
    cp_op: coverpoint v_cp_op { bins csrrw= {0}; bins csrrs= {1}; bins csrrc= {2}; bins csrrwi= {3}; bins csrrsi= {4}; bins csrrci= {5}; ignore_bins na = {-1}; }
    cp_rw: coverpoint v_cp_rw { bins read_only= {0}; bins write= {1}; ignore_bins na = {-1}; }
    cp_trap: coverpoint v_cp_trap { bins none= {0}; bins illegal= {1}; ignore_bins na = {-1}; }
    cp_first_after_reset: coverpoint v_cp_first_after_reset { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cr_op_class: cross cp_op, cp_class {
      bins csrrw_pmpcfg= binsof(cp_op.csrrw) && binsof(cp_class.pmpcfg);
      bins csrrw_pmpaddr= binsof(cp_op.csrrw) && binsof(cp_class.pmpaddr);
      bins csrrc_mseccfg= binsof(cp_op.csrrc) && binsof(cp_class.mseccfg);
      bins csrrc_mseccfgh= binsof(cp_op.csrrc) && binsof(cp_class.mseccfgh);
      bins csrrc_pmpaddr= binsof(cp_op.csrrc) && binsof(cp_class.pmpaddr);
      bins csrrc_pmpcfg= binsof(cp_op.csrrc) && binsof(cp_class.pmpcfg);
      bins csrrci_mseccfg= binsof(cp_op.csrrci) && binsof(cp_class.mseccfg);
      bins csrrci_mseccfgh= binsof(cp_op.csrrci) && binsof(cp_class.mseccfgh);
      bins csrrci_pmpaddr= binsof(cp_op.csrrci) && binsof(cp_class.pmpaddr);
      bins csrrci_pmpcfg= binsof(cp_op.csrrci) && binsof(cp_class.pmpcfg);
      bins csrrs_mseccfg= binsof(cp_op.csrrs) && binsof(cp_class.mseccfg);
      bins csrrs_mseccfgh= binsof(cp_op.csrrs) && binsof(cp_class.mseccfgh);
      bins csrrs_pmpaddr= binsof(cp_op.csrrs) && binsof(cp_class.pmpaddr);
      bins csrrs_pmpcfg= binsof(cp_op.csrrs) && binsof(cp_class.pmpcfg);
      bins csrrsi_mseccfg= binsof(cp_op.csrrsi) && binsof(cp_class.mseccfg);
      bins csrrsi_mseccfgh= binsof(cp_op.csrrsi) && binsof(cp_class.mseccfgh);
      bins csrrsi_pmpaddr= binsof(cp_op.csrrsi) && binsof(cp_class.pmpaddr);
      bins csrrsi_pmpcfg= binsof(cp_op.csrrsi) && binsof(cp_class.pmpcfg);
      bins csrrw_mseccfg= binsof(cp_op.csrrw) && binsof(cp_class.mseccfg);
      bins csrrw_mseccfgh= binsof(cp_op.csrrw) && binsof(cp_class.mseccfgh);
      bins csrrwi_mseccfg= binsof(cp_op.csrrwi) && binsof(cp_class.mseccfg);
      bins csrrwi_mseccfgh= binsof(cp_op.csrrwi) && binsof(cp_class.mseccfgh);
      bins csrrwi_pmpaddr= binsof(cp_op.csrrwi) && binsof(cp_class.pmpaddr);
      bins csrrwi_pmpcfg= binsof(cp_op.csrrwi) && binsof(cp_class.pmpcfg);
    }
    cr_priv_trap: cross cp_priv, cp_trap {
      bins m_none= binsof(cp_priv.m) && binsof(cp_trap.none);
      bins u_illegal= binsof(cp_priv.u) && binsof(cp_trap.illegal);
    }
    cr_u_class: cross cp_priv, cp_class, cp_rw {
      bins u_mseccfg_read_only= binsof(cp_priv.u) && binsof(cp_class.mseccfg) && binsof(cp_rw.read_only);
      bins u_mseccfg_write= binsof(cp_priv.u) && binsof(cp_class.mseccfg) && binsof(cp_rw.write);
      bins u_mseccfgh_read_only= binsof(cp_priv.u) && binsof(cp_class.mseccfgh) && binsof(cp_rw.read_only);
      bins u_mseccfgh_write= binsof(cp_priv.u) && binsof(cp_class.mseccfgh) && binsof(cp_rw.write);
      bins u_pmpaddr_read_only= binsof(cp_priv.u) && binsof(cp_class.pmpaddr) && binsof(cp_rw.read_only);
      bins u_pmpaddr_write= binsof(cp_priv.u) && binsof(cp_class.pmpaddr) && binsof(cp_rw.write);
      bins u_pmpcfg_read_only= binsof(cp_priv.u) && binsof(cp_class.pmpcfg) && binsof(cp_rw.read_only);
      bins u_pmpcfg_write= binsof(cp_priv.u) && binsof(cp_class.pmpcfg) && binsof(cp_rw.write);
    }
    cr_dbg_class: cross cp_dbg, cp_class, cp_rw {
      bins d1_mseccfg_read_only= binsof(cp_dbg.d1) && binsof(cp_class.mseccfg) && binsof(cp_rw.read_only);
      bins d1_mseccfg_write= binsof(cp_dbg.d1) && binsof(cp_class.mseccfg) && binsof(cp_rw.write);
      bins d1_mseccfgh_read_only= binsof(cp_dbg.d1) && binsof(cp_class.mseccfgh) && binsof(cp_rw.read_only);
      bins d1_mseccfgh_write= binsof(cp_dbg.d1) && binsof(cp_class.mseccfgh) && binsof(cp_rw.write);
      bins d1_pmpaddr_read_only= binsof(cp_dbg.d1) && binsof(cp_class.pmpaddr) && binsof(cp_rw.read_only);
      bins d1_pmpaddr_write= binsof(cp_dbg.d1) && binsof(cp_class.pmpaddr) && binsof(cp_rw.write);
      bins d1_pmpcfg_read_only= binsof(cp_dbg.d1) && binsof(cp_class.pmpcfg) && binsof(cp_rw.read_only);
      bins d1_pmpcfg_write= binsof(cp_dbg.d1) && binsof(cp_class.pmpcfg) && binsof(cp_rw.write);
    }
    cr_reset_read: cross cp_first_after_reset, cp_class, cp_rw {
      bins rst_mseccfg= binsof(cp_first_after_reset.yes) && binsof(cp_class.mseccfg) && binsof(cp_rw.read_only);
      bins rst_mseccfgh= binsof(cp_first_after_reset.yes) && binsof(cp_class.mseccfgh) && binsof(cp_rw.read_only);
      bins rst_pmpaddr= binsof(cp_first_after_reset.yes) && binsof(cp_class.pmpaddr) && binsof(cp_rw.read_only);
      bins rst_pmpcfg= binsof(cp_first_after_reset.yes) && binsof(cp_class.pmpcfg) && binsof(cp_rw.read_only);
    }
  endgroup

  // CG-PMP-014 (gen_pmp_table_state_cg), 36 coverpoint bins, 42 cross bins
  localparam int GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N0 = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N1 = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N2_4 = 2;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N5_8 = 3;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N9_15 = 4;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N16 = 5;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_LOCKED_N0 = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_LOCKED_N1_4 = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_LOCKED_N5_15 = 2;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_LOCKED_N16 = 3;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MODES_NONE = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MODES_TOR_ONLY = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MODES_NA_ONLY = 2;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MODES_MIXED = 3;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_TOR_EMPTY_NONE = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_TOR_EMPTY_SOME = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_OVERLAP_NONE = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_OVERLAP_SOME = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_REGIME_OFF = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_REGIME_SPARSE = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_REGIME_DENSE = 2;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_REGIME_MML_ON = 3;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_ALL_OFF_U_NO = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_ALL_OFF_U_YES = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_E15_OFF = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_E15_ACTIVE = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_E0_TOR_NO = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_E0_TOR_YES = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S000 = 0;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S001 = 1;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S010 = 2;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S011 = 3;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S100 = 4;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S101 = 5;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S110 = 6;
  localparam int GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S111 = 7;
  covergroup gen_pmp_table_state_cg with function sample(int v_cp_active, int v_cp_locked, int v_cp_modes, int v_cp_tor_empty, int v_cp_overlap, int v_cp_regime, int v_cp_all_off_u, int v_cp_e15, int v_cp_e0_tor, int v_cp_mseccfg);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_active: coverpoint v_cp_active { bins n0= {0}; bins n1= {1}; bins n2_4= {2}; bins n5_8= {3}; bins n9_15= {4}; bins n16= {5}; ignore_bins na = {-1}; }
    cp_locked: coverpoint v_cp_locked { bins n0= {0}; bins n1_4= {1}; bins n5_15= {2}; bins n16= {3}; ignore_bins na = {-1}; }
    cp_modes: coverpoint v_cp_modes { bins none= {0}; bins tor_only= {1}; bins na_only= {2}; bins mixed= {3}; ignore_bins na = {-1}; }
    cp_tor_empty: coverpoint v_cp_tor_empty { bins none= {0}; bins some= {1}; ignore_bins na = {-1}; }
    cp_overlap: coverpoint v_cp_overlap { bins none= {0}; bins some= {1}; ignore_bins na = {-1}; }
    cp_regime: coverpoint v_cp_regime { bins off= {0}; bins sparse= {1}; bins dense= {2}; bins mml_on= {3}; ignore_bins na = {-1}; }
    cp_all_off_u: coverpoint v_cp_all_off_u { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_e15: coverpoint v_cp_e15 { bins off= {0}; bins active= {1}; ignore_bins na = {-1}; }
    cp_e0_tor: coverpoint v_cp_e0_tor { bins no= {0}; bins yes= {1}; ignore_bins na = {-1}; }
    cp_mseccfg: coverpoint v_cp_mseccfg { bins s000= {0}; bins s001= {1}; bins s010= {2}; bins s011= {3}; bins s100= {4}; bins s101= {5}; bins s110= {6}; bins s111= {7}; ignore_bins na = {-1}; }
    cr_overlap_modes: cross cp_overlap, cp_modes {
      bins overlap_mixed= binsof(cp_overlap.some) && binsof(cp_modes.mixed);
      bins overlap_na_only= binsof(cp_overlap.some) && binsof(cp_modes.na_only);
      bins overlap_tor_only= binsof(cp_overlap.some) && binsof(cp_modes.tor_only);
    }
    cr_e15_e0: cross cp_e15, cp_e0_tor {
      bins e15_active_e0tor_no= binsof(cp_e15.active) && binsof(cp_e0_tor.no);
      bins e15_active_e0tor_yes= binsof(cp_e15.active) && binsof(cp_e0_tor.yes);
    }
    cr_locked_regime: cross cp_locked, cp_regime {
      bins n0_dense= binsof(cp_locked.n0) && binsof(cp_regime.dense);
      bins n0_mml_on= binsof(cp_locked.n0) && binsof(cp_regime.mml_on);
      bins n0_sparse= binsof(cp_locked.n0) && binsof(cp_regime.sparse);
      bins n16_dense= binsof(cp_locked.n16) && binsof(cp_regime.dense);
      bins n16_mml_on= binsof(cp_locked.n16) && binsof(cp_regime.mml_on);
      bins n1_4_dense= binsof(cp_locked.n1_4) && binsof(cp_regime.dense);
      bins n1_4_mml_on= binsof(cp_locked.n1_4) && binsof(cp_regime.mml_on);
      bins n1_4_sparse= binsof(cp_locked.n1_4) && binsof(cp_regime.sparse);
      bins n5_15_dense= binsof(cp_locked.n5_15) && binsof(cp_regime.dense);
      bins n5_15_mml_on= binsof(cp_locked.n5_15) && binsof(cp_regime.mml_on);
    }
    cr_regime_active: cross cp_regime, cp_active {
      bins dense_n16= binsof(cp_regime.dense) && binsof(cp_active.n16);
      bins dense_n5_8= binsof(cp_regime.dense) && binsof(cp_active.n5_8);
      bins dense_n9_15= binsof(cp_regime.dense) && binsof(cp_active.n9_15);
      bins sparse_n1= binsof(cp_regime.sparse) && binsof(cp_active.n1);
      bins sparse_n2_4= binsof(cp_regime.sparse) && binsof(cp_active.n2_4);
      bins mml_on_n1= binsof(cp_regime.mml_on) && binsof(cp_active.n1);
      bins mml_on_n16= binsof(cp_regime.mml_on) && binsof(cp_active.n16);
      bins mml_on_n2_4= binsof(cp_regime.mml_on) && binsof(cp_active.n2_4);
      bins mml_on_n5_8= binsof(cp_regime.mml_on) && binsof(cp_active.n5_8);
      bins mml_on_n9_15= binsof(cp_regime.mml_on) && binsof(cp_active.n9_15);
      bins off_n0= binsof(cp_regime.off) && binsof(cp_active.n0);
    }
    cr_regime_mseccfg: cross cp_regime, cp_mseccfg {
      bins dense_s000= binsof(cp_regime.dense) && binsof(cp_mseccfg.s000);
      bins dense_s001= binsof(cp_regime.dense) && binsof(cp_mseccfg.s001);
      bins dense_s010= binsof(cp_regime.dense) && binsof(cp_mseccfg.s010);
      bins dense_s011= binsof(cp_regime.dense) && binsof(cp_mseccfg.s011);
      bins sparse_s000= binsof(cp_regime.sparse) && binsof(cp_mseccfg.s000);
      bins sparse_s001= binsof(cp_regime.sparse) && binsof(cp_mseccfg.s001);
      bins sparse_s010= binsof(cp_regime.sparse) && binsof(cp_mseccfg.s010);
      bins sparse_s011= binsof(cp_regime.sparse) && binsof(cp_mseccfg.s011);
      bins mml_on_s100= binsof(cp_regime.mml_on) && binsof(cp_mseccfg.s100);
      bins mml_on_s101= binsof(cp_regime.mml_on) && binsof(cp_mseccfg.s101);
      bins mml_on_s110= binsof(cp_regime.mml_on) && binsof(cp_mseccfg.s110);
      bins mml_on_s111= binsof(cp_regime.mml_on) && binsof(cp_mseccfg.s111);
      bins off_s000= binsof(cp_regime.off) && binsof(cp_mseccfg.s000);
      bins off_s001= binsof(cp_regime.off) && binsof(cp_mseccfg.s001);
      bins off_s010= binsof(cp_regime.off) && binsof(cp_mseccfg.s010);
      bins off_s011= binsof(cp_regime.off) && binsof(cp_mseccfg.s011);
    }
  endgroup

  // CG-IRQ-001 (gen_irq_entry_cg), 32 coverpoint bins, 54 cross bins
  localparam int GEN_FC_IRQ_ENTRY_CP_LINE_SOFTWARE = 0;
  localparam int GEN_FC_IRQ_ENTRY_CP_LINE_TIMER = 1;
  localparam int GEN_FC_IRQ_ENTRY_CP_LINE_EXTERNAL = 2;
  localparam int GEN_FC_IRQ_ENTRY_CP_LINE_FAST = 3;
  localparam int GEN_FC_IRQ_ENTRY_CP_LINE_NMI_EXT = 18;
  localparam int GEN_FC_IRQ_ENTRY_CP_LINE_NMI_INT = 19;
  localparam int GEN_FC_IRQ_ENTRY_CP_PRIV_PRE_M = 0;
  localparam int GEN_FC_IRQ_ENTRY_CP_PRIV_PRE_U = 1;
  localparam int GEN_FC_IRQ_ENTRY_CP_MIE_GLOBAL_MIE0 = 0;
  localparam int GEN_FC_IRQ_ENTRY_CP_MIE_GLOBAL_MIE1 = 1;
  localparam int GEN_FC_IRQ_ENTRY_CP_OTHERS_ONLY_THIS = 0;
  localparam int GEN_FC_IRQ_ENTRY_CP_OTHERS_OTHERS_ENABLED_IDLE = 1;
  localparam int GEN_FC_IRQ_ENTRY_CP_OTHERS_OTHERS_PENDING_LOWER = 2;
  localparam int GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_SEQUENTIAL = 0;
  localparam int GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_BRANCH_TARGET = 1;
  localparam int GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_JUMP_TARGET = 2;
  localparam int GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_MRET_TARGET = 3;
  localparam int GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_DRET_TARGET = 4;
  localparam int GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_WFI_NEXT = 5;
  localparam int GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_BOOT_PC = 6;
  localparam int GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_CM_PC = 7;
  localparam int GEN_FC_IRQ_ENTRY_CP_U_PATH_MRET_MPP_U = 0;
  localparam int GEN_FC_IRQ_ENTRY_CP_U_PATH_DRET_PRV_U = 1;
  localparam int GEN_FC_IRQ_ENTRY_CP_U_PENDING_AT_RETURN_ALREADY_PENDING = 0;
  localparam int GEN_FC_IRQ_ENTRY_CP_U_PENDING_AT_RETURN_ARRIVED_LATER = 1;
  localparam int GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_INTR_WITH_PRE_MIP = 0;
  localparam int GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_IRQ_VALID_LEVEL = 1;
  localparam int GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_IRQ_VALID_ABSENT = 2;
  localparam int GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_PRE_POST_MIP_EQUAL = 3;
  localparam int GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_PRE_POST_MIP_DIFFER = 4;
  localparam int GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_NMI_FLAG = 5;
  localparam int GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_NMI_INT_FLAG = 6;
  covergroup gen_irq_entry_cg with function sample(int v_cp_line, int v_cp_priv_pre, int v_cp_mie_global, int v_cp_others, int v_cp_mepc_src, int v_cp_u_path, int v_cp_u_pending_at_return, int v_cp_rvfi_marks);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_line: coverpoint v_cp_line { bins software= {0}; bins timer= {1}; bins external= {2}; bins fast[15]= {[3:17]}; bins nmi_ext= {18}; bins nmi_int= {19}; ignore_bins na = {-1}; }
    cp_priv_pre: coverpoint v_cp_priv_pre { bins m= {0}; bins u= {1}; ignore_bins na = {-1}; }
    cp_mie_global: coverpoint v_cp_mie_global { bins mie0= {0}; bins mie1= {1}; ignore_bins na = {-1}; }
    cp_others: coverpoint v_cp_others { bins only_this= {0}; bins others_enabled_idle= {1}; bins others_pending_lower= {2}; ignore_bins na = {-1}; }
    cp_mepc_src: coverpoint v_cp_mepc_src { bins sequential= {0}; bins branch_target= {1}; bins jump_target= {2}; bins mret_target= {3}; bins dret_target= {4}; bins wfi_next= {5}; bins boot_pc= {6}; bins cm_pc= {7}; ignore_bins na = {-1}; }
    cp_u_path: coverpoint v_cp_u_path { bins mret_mpp_u= {0}; bins dret_prv_u= {1}; ignore_bins na = {-1}; }
    cp_u_pending_at_return: coverpoint v_cp_u_pending_at_return { bins already_pending= {0}; bins arrived_later= {1}; ignore_bins na = {-1}; }
    cp_rvfi_marks: coverpoint v_cp_rvfi_marks { bins intr_with_pre_mip= {0}; bins irq_valid_level= {1}; bins irq_valid_absent= {2}; bins pre_post_mip_equal= {3}; bins pre_post_mip_differ= {4}; bins nmi_flag= {5}; bins nmi_int_flag= {6}; ignore_bins na = {-1}; }
    cr_line_marks: cross cp_line, cp_rvfi_marks {
      bins software_intr_with_pre_mip= binsof(cp_line.software) && binsof(cp_rvfi_marks.intr_with_pre_mip);
      bins fast_5_intr_with_pre_mip= binsof(cp_line.fast[5]) && binsof(cp_rvfi_marks.intr_with_pre_mip);
      bins nmi_ext_nmi_flag= binsof(cp_line.nmi_ext) && binsof(cp_rvfi_marks.nmi_flag);
      bins timer_pre_post_mip_differ= binsof(cp_line.timer) && binsof(cp_rvfi_marks.pre_post_mip_differ);
      bins nmi_int_nmi_int_flag= binsof(cp_line.nmi_int) && binsof(cp_rvfi_marks.nmi_int_flag);
      bins external_irq_valid_level= binsof(cp_line.external) && binsof(cp_rvfi_marks.irq_valid_level);
    }
    cr_line_mepc: cross cp_line, cp_mepc_src {
      bins software_sequential= binsof(cp_line.software) && binsof(cp_mepc_src.sequential);
      bins timer_branch_target= binsof(cp_line.timer) && binsof(cp_mepc_src.branch_target);
      bins external_jump_target= binsof(cp_line.external) && binsof(cp_mepc_src.jump_target);
      bins fast_14_sequential= binsof(cp_line.fast[14]) && binsof(cp_mepc_src.sequential);
      bins software_mret_target= binsof(cp_line.software) && binsof(cp_mepc_src.mret_target);
      bins nmi_ext_boot_pc= binsof(cp_line.nmi_ext) && binsof(cp_mepc_src.boot_pc);
      bins external_branch_target= binsof(cp_line.external) && binsof(cp_mepc_src.branch_target);
      bins fast_0_cm_pc= binsof(cp_line.fast[0]) && binsof(cp_mepc_src.cm_pc);
      bins fast_3_mret_target= binsof(cp_line.fast[3]) && binsof(cp_mepc_src.mret_target);
      bins fast_9_dret_target= binsof(cp_line.fast[9]) && binsof(cp_mepc_src.dret_target);
      bins timer_dret_target= binsof(cp_line.timer) && binsof(cp_mepc_src.dret_target);
      bins nmi_int_sequential= binsof(cp_line.nmi_int) && binsof(cp_mepc_src.sequential);
      bins external_wfi_next= binsof(cp_line.external) && binsof(cp_mepc_src.wfi_next);
      bins nmi_ext_wfi_next= binsof(cp_line.nmi_ext) && binsof(cp_mepc_src.wfi_next);
    }
    cr_line_others: cross cp_line, cp_others {
      bins software_only_this= binsof(cp_line.software) && binsof(cp_others.only_this);
      bins timer_only_this= binsof(cp_line.timer) && binsof(cp_others.only_this);
      bins external_others_enabled_idle= binsof(cp_line.external) && binsof(cp_others.others_enabled_idle);
      bins external_others_pending_lower= binsof(cp_line.external) && binsof(cp_others.others_pending_lower);
      bins fast_0_others_pending_lower= binsof(cp_line.fast[0]) && binsof(cp_others.others_pending_lower);
      bins fast_14_others_pending_lower= binsof(cp_line.fast[14]) && binsof(cp_others.others_pending_lower);
      bins software_others_pending_lower= binsof(cp_line.software) && binsof(cp_others.others_pending_lower);
    }
    cr_line_priv_mie: cross cp_line, cp_priv_pre, cp_mie_global {
      bins software_m_mie1= binsof(cp_line.software) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie1);
      bins software_u_mie0= binsof(cp_line.software) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie0);
      bins software_u_mie1= binsof(cp_line.software) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie1);
      bins timer_m_mie1= binsof(cp_line.timer) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie1);
      bins timer_u_mie0= binsof(cp_line.timer) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie0);
      bins timer_u_mie1= binsof(cp_line.timer) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie1);
      bins external_m_mie1= binsof(cp_line.external) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie1);
      bins external_u_mie0= binsof(cp_line.external) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie0);
      bins external_u_mie1= binsof(cp_line.external) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie1);
      bins fast_7_u_mie1= binsof(cp_line.fast[7]) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie1);
      bins fast_0_m_mie1= binsof(cp_line.fast[0]) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie1);
      bins fast_0_u_mie0= binsof(cp_line.fast[0]) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie0);
      bins fast_14_m_mie1= binsof(cp_line.fast[14]) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie1);
      bins fast_14_u_mie0= binsof(cp_line.fast[14]) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie0);
      bins nmi_ext_m_mie0= binsof(cp_line.nmi_ext) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie0);
      bins nmi_ext_m_mie1= binsof(cp_line.nmi_ext) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie1);
      bins nmi_ext_u_mie0= binsof(cp_line.nmi_ext) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie0);
      bins nmi_ext_u_mie1= binsof(cp_line.nmi_ext) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie1);
      bins nmi_int_m_mie0= binsof(cp_line.nmi_int) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie0);
      bins nmi_int_m_mie1= binsof(cp_line.nmi_int) && binsof(cp_priv_pre.m) && binsof(cp_mie_global.mie1);
      bins nmi_int_u_mie0= binsof(cp_line.nmi_int) && binsof(cp_priv_pre.u) && binsof(cp_mie_global.mie0);
    }
    cr_upath_pending: cross cp_u_path, cp_u_pending_at_return, cp_mie_global {
      bins mret_mpp_u_arrived_later_mie0= binsof(cp_u_path.mret_mpp_u) && binsof(cp_u_pending_at_return.arrived_later) && binsof(cp_mie_global.mie0);
      bins dret_prv_u_already_pending_mie0= binsof(cp_u_path.dret_prv_u) && binsof(cp_u_pending_at_return.already_pending) && binsof(cp_mie_global.mie0);
      bins dret_prv_u_arrived_later_mie1= binsof(cp_u_path.dret_prv_u) && binsof(cp_u_pending_at_return.arrived_later) && binsof(cp_mie_global.mie1);
      bins mret_mpp_u_already_pending_mie0= binsof(cp_u_path.mret_mpp_u) && binsof(cp_u_pending_at_return.already_pending) && binsof(cp_mie_global.mie0);
      bins mret_mpp_u_already_pending_mie1= binsof(cp_u_path.mret_mpp_u) && binsof(cp_u_pending_at_return.already_pending) && binsof(cp_mie_global.mie1);
      bins mret_mpp_u_arrived_later_mie1= binsof(cp_u_path.mret_mpp_u) && binsof(cp_u_pending_at_return.arrived_later) && binsof(cp_mie_global.mie1);
    }
  endgroup

  // CG-IRQ-003 (gen_irq_pending_model_cg), 37 coverpoint bins, 36 cross bins
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_RISE_ENABLED = 0;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_RISE_DISABLED = 1;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_RISE_ENABLED_OTHER_HIGH = 2;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_FALL_LAST = 3;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_FALL_NOT_LAST = 4;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_MIE_SET_PIN_HIGH = 5;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_MIE_CLEAR_PIN_HIGH = 6;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_NMI_ONLY_RISE = 7;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_STATE_MIE0_M = 0;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_STATE_MIE1_M = 1;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_STATE_U_MODE = 2;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_STATE_DEBUG_MODE = 3;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_STATE_NMI_MODE = 4;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_STATE_STEP = 5;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_STATE_SLEEP = 6;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_SOFTWARE = 0;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_TIMER = 1;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_EXTERNAL = 2;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_FAST_LOW = 3;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_FAST_MID = 4;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_FAST_HIGH = 5;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_READ_MIE0_PINS_HIGH = 0;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_READ_PARTIAL_MIE = 1;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_READ_ALL_LOW = 2;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_WRITE_CSRRW_IGNORED = 3;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_WRITE_CSRRS_IGNORED = 4;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_WRITE_CSRRC_IGNORED = 5;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_WRITE_ALL_ONES = 0;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_WRITE_ZERO = 1;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_WRITE_RANDOM_MASKED = 2;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_WRITE_FAST_ONLY = 3;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_SET_PENDING = 0;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_CLEAR_PENDING = 1;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_SET_IDLE = 2;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_CLEAR_IDLE = 3;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_MRET_MPIE1_PENDING = 4;
  localparam int GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_MRET_MPIE0_PENDING = 5;
  covergroup gen_irq_pending_model_cg with function sample(int v_cp_transition, int v_cp_state, int v_cp_line_kind, int v_cp_mip_access, int v_cp_mie_write, int v_cp_mie_global_edge);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_transition: coverpoint v_cp_transition { bins rise_enabled= {0}; bins rise_disabled= {1}; bins rise_enabled_other_high= {2}; bins fall_last= {3}; bins fall_not_last= {4}; bins mie_set_pin_high= {5}; bins mie_clear_pin_high= {6}; bins nmi_only_rise= {7}; ignore_bins na = {-1}; }
    cp_state: coverpoint v_cp_state { bins mie0_m= {0}; bins mie1_m= {1}; bins u_mode= {2}; bins debug_mode= {3}; bins nmi_mode= {4}; bins step= {5}; bins sleep= {6}; ignore_bins na = {-1}; }
    cp_line_kind: coverpoint v_cp_line_kind { bins software= {0}; bins timer= {1}; bins external= {2}; bins fast_low= {3}; bins fast_mid= {4}; bins fast_high= {5}; ignore_bins na = {-1}; }
    cp_mip_access: coverpoint v_cp_mip_access { bins read_mie0_pins_high= {0}; bins read_partial_mie= {1}; bins read_all_low= {2}; bins write_csrrw_ignored= {3}; bins write_csrrs_ignored= {4}; bins write_csrrc_ignored= {5}; ignore_bins na = {-1}; }
    cp_mie_write: coverpoint v_cp_mie_write { bins all_ones= {0}; bins zero= {1}; bins random_masked= {2}; bins fast_only= {3}; ignore_bins na = {-1}; }
    cp_mie_global_edge: coverpoint v_cp_mie_global_edge { bins set_pending= {0}; bins clear_pending= {1}; bins set_idle= {2}; bins clear_idle= {3}; bins mret_mpie1_pending= {4}; bins mret_mpie0_pending= {5}; ignore_bins na = {-1}; }
    cr_access_state: cross cp_mip_access, cp_state {
      bins read_all_low_mie1_m= binsof(cp_mip_access.read_all_low) && binsof(cp_state.mie1_m);
      bins read_mie0_pins_high_mie0_m= binsof(cp_mip_access.read_mie0_pins_high) && binsof(cp_state.mie0_m);
      bins read_partial_mie_mie1_m= binsof(cp_mip_access.read_partial_mie) && binsof(cp_state.mie1_m);
      bins write_csrrc_ignored_mie1_m= binsof(cp_mip_access.write_csrrc_ignored) && binsof(cp_state.mie1_m);
      bins write_csrrs_ignored_mie0_m= binsof(cp_mip_access.write_csrrs_ignored) && binsof(cp_state.mie0_m);
      bins write_csrrw_ignored_mie1_m= binsof(cp_mip_access.write_csrrw_ignored) && binsof(cp_state.mie1_m);
    }
    cr_transition_line: cross cp_transition, cp_line_kind {
      bins fall_last_external= binsof(cp_transition.fall_last) && binsof(cp_line_kind.external);
      bins fall_last_fast_high= binsof(cp_transition.fall_last) && binsof(cp_line_kind.fast_high);
      bins fall_last_fast_low= binsof(cp_transition.fall_last) && binsof(cp_line_kind.fast_low);
      bins fall_last_software= binsof(cp_transition.fall_last) && binsof(cp_line_kind.software);
      bins fall_last_timer= binsof(cp_transition.fall_last) && binsof(cp_line_kind.timer);
      bins mie_clear_pin_high_external= binsof(cp_transition.mie_clear_pin_high) && binsof(cp_line_kind.external);
      bins rise_disabled_fast_mid= binsof(cp_transition.rise_disabled) && binsof(cp_line_kind.fast_mid);
      bins rise_enabled_external= binsof(cp_transition.rise_enabled) && binsof(cp_line_kind.external);
      bins rise_enabled_fast_high= binsof(cp_transition.rise_enabled) && binsof(cp_line_kind.fast_high);
      bins rise_enabled_fast_low= binsof(cp_transition.rise_enabled) && binsof(cp_line_kind.fast_low);
      bins rise_enabled_fast_mid= binsof(cp_transition.rise_enabled) && binsof(cp_line_kind.fast_mid);
      bins rise_enabled_software= binsof(cp_transition.rise_enabled) && binsof(cp_line_kind.software);
      bins rise_enabled_timer= binsof(cp_transition.rise_enabled) && binsof(cp_line_kind.timer);
    }
    cr_transition_state: cross cp_transition, cp_state {
      bins fall_last_debug_mode= binsof(cp_transition.fall_last) && binsof(cp_state.debug_mode);
      bins fall_last_mie0_m= binsof(cp_transition.fall_last) && binsof(cp_state.mie0_m);
      bins fall_last_mie1_m= binsof(cp_transition.fall_last) && binsof(cp_state.mie1_m);
      bins mie_clear_pin_high_mie1_m= binsof(cp_transition.mie_clear_pin_high) && binsof(cp_state.mie1_m);
      bins mie_set_pin_high_mie0_m= binsof(cp_transition.mie_set_pin_high) && binsof(cp_state.mie0_m);
      bins mie_set_pin_high_mie1_m= binsof(cp_transition.mie_set_pin_high) && binsof(cp_state.mie1_m);
      bins nmi_only_rise_mie1_m= binsof(cp_transition.nmi_only_rise) && binsof(cp_state.mie1_m);
      bins nmi_only_rise_sleep= binsof(cp_transition.nmi_only_rise) && binsof(cp_state.sleep);
      bins rise_disabled_mie1_m= binsof(cp_transition.rise_disabled) && binsof(cp_state.mie1_m);
      bins rise_disabled_sleep= binsof(cp_transition.rise_disabled) && binsof(cp_state.sleep);
      bins rise_enabled_debug_mode= binsof(cp_transition.rise_enabled) && binsof(cp_state.debug_mode);
      bins rise_enabled_mie0_m= binsof(cp_transition.rise_enabled) && binsof(cp_state.mie0_m);
      bins rise_enabled_mie1_m= binsof(cp_transition.rise_enabled) && binsof(cp_state.mie1_m);
      bins rise_enabled_nmi_mode= binsof(cp_transition.rise_enabled) && binsof(cp_state.nmi_mode);
      bins rise_enabled_sleep= binsof(cp_transition.rise_enabled) && binsof(cp_state.sleep);
      bins rise_enabled_step= binsof(cp_transition.rise_enabled) && binsof(cp_state.step);
      bins rise_enabled_u_mode= binsof(cp_transition.rise_enabled) && binsof(cp_state.u_mode);
    }
  endgroup

  // CG-IRQ-010 (gen_irq_debug_interplay_cg), 17 coverpoint bins, 25 cross bins
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_IRQ = 0;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_NMI_EXT = 1;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_NMI_INT = 2;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_MODE_DEBUG_MODE = 0;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_MODE_STEP_OUTSIDE = 1;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_MODE_DEBUG_IN_NMI_HANDLER = 2;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_DURATION_HELD_THROUGH_EXIT = 0;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_DURATION_DROPPED_BEFORE_EXIT = 1;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_POST_EXIT_TAKEN_BEFORE_FIRST_INSN = 0;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_POST_EXIT_NOT_TAKEN = 1;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_POST_EXIT_TAKEN_AFTER_NMI_MRET = 2;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_DCSR_PRV_M = 0;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_DCSR_PRV_U = 1;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_NMIP_READ_READ_WITH_NMI_HIGH = 0;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_NMIP_READ_READ_WITH_NMI_LOW = 1;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_EXIT_KIND_DRET = 0;
  localparam int GEN_FC_IRQ_DEBUG_INTERPLAY_CP_EXIT_KIND_STEP_COMPLETE = 1;
  covergroup gen_irq_debug_interplay_cg with function sample(int v_cp_line, int v_cp_mode, int v_cp_duration, int v_cp_post_exit, int v_cp_dcsr_prv, int v_cp_nmip_read, int v_cp_exit_kind);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_line: coverpoint v_cp_line { bins irq= {0}; bins nmi_ext= {1}; bins nmi_int= {2}; ignore_bins na = {-1}; }
    cp_mode: coverpoint v_cp_mode { bins debug_mode= {0}; bins step_outside= {1}; bins debug_in_nmi_handler= {2}; ignore_bins na = {-1}; }
    cp_duration: coverpoint v_cp_duration { bins held_through_exit= {0}; bins dropped_before_exit= {1}; ignore_bins na = {-1}; }
    cp_post_exit: coverpoint v_cp_post_exit { bins taken_before_first_insn= {0}; bins not_taken= {1}; bins taken_after_nmi_mret= {2}; ignore_bins na = {-1}; }
    cp_dcsr_prv: coverpoint v_cp_dcsr_prv { bins m= {0}; bins u= {1}; ignore_bins na = {-1}; }
    cp_nmip_read: coverpoint v_cp_nmip_read { bins read_with_nmi_high= {0}; bins read_with_nmi_low= {1}; ignore_bins na = {-1}; }
    cp_exit_kind: coverpoint v_cp_exit_kind { bins dret= {0}; bins step_complete= {1}; ignore_bins na = {-1}; }
    cr_dur_post: cross cp_duration, cp_post_exit {
      bins held_through_exit_taken_before_first_insn= binsof(cp_duration.held_through_exit) && binsof(cp_post_exit.taken_before_first_insn);
      bins dropped_before_exit_not_taken= binsof(cp_duration.dropped_before_exit) && binsof(cp_post_exit.not_taken);
    }
    cr_line_exit: cross cp_line, cp_exit_kind {
      bins irq_dret= binsof(cp_line.irq) && binsof(cp_exit_kind.dret);
      bins nmi_ext_dret= binsof(cp_line.nmi_ext) && binsof(cp_exit_kind.dret);
      bins irq_step_complete= binsof(cp_line.irq) && binsof(cp_exit_kind.step_complete);
      bins nmi_ext_step_complete= binsof(cp_line.nmi_ext) && binsof(cp_exit_kind.step_complete);
    }
    cr_line_mode_post: cross cp_line, cp_mode, cp_post_exit {
      bins irq_debug_mode_not_taken= binsof(cp_line.irq) && binsof(cp_mode.debug_mode) && binsof(cp_post_exit.not_taken);
      bins irq_debug_mode_taken_before_first_insn= binsof(cp_line.irq) && binsof(cp_mode.debug_mode) && binsof(cp_post_exit.taken_before_first_insn);
      bins nmi_ext_debug_mode_not_taken= binsof(cp_line.nmi_ext) && binsof(cp_mode.debug_mode) && binsof(cp_post_exit.not_taken);
      bins nmi_ext_debug_mode_taken_before_first_insn= binsof(cp_line.nmi_ext) && binsof(cp_mode.debug_mode) && binsof(cp_post_exit.taken_before_first_insn);
      bins nmi_int_debug_mode_taken_before_first_insn= binsof(cp_line.nmi_int) && binsof(cp_mode.debug_mode) && binsof(cp_post_exit.taken_before_first_insn);
      bins irq_step_outside_not_taken= binsof(cp_line.irq) && binsof(cp_mode.step_outside) && binsof(cp_post_exit.not_taken);
      bins nmi_ext_step_outside_not_taken= binsof(cp_line.nmi_ext) && binsof(cp_mode.step_outside) && binsof(cp_post_exit.not_taken);
      bins irq_debug_in_nmi_handler_not_taken= binsof(cp_line.irq) && binsof(cp_mode.debug_in_nmi_handler) && binsof(cp_post_exit.not_taken);
      bins irq_debug_in_nmi_handler_taken_after_nmi_mret= binsof(cp_line.irq) && binsof(cp_mode.debug_in_nmi_handler) && binsof(cp_post_exit.taken_after_nmi_mret);
      bins nmi_ext_debug_in_nmi_handler_not_taken= binsof(cp_line.nmi_ext) && binsof(cp_mode.debug_in_nmi_handler) && binsof(cp_post_exit.not_taken);
      bins nmi_ext_debug_in_nmi_handler_taken_after_nmi_mret= binsof(cp_line.nmi_ext) && binsof(cp_mode.debug_in_nmi_handler) && binsof(cp_post_exit.taken_after_nmi_mret);
    }
    cr_line_prv: cross cp_line, cp_dcsr_prv {
      bins irq_m= binsof(cp_line.irq) && binsof(cp_dcsr_prv.m);
      bins irq_u= binsof(cp_line.irq) && binsof(cp_dcsr_prv.u);
      bins nmi_ext_m= binsof(cp_line.nmi_ext) && binsof(cp_dcsr_prv.m);
      bins nmi_ext_u= binsof(cp_line.nmi_ext) && binsof(cp_dcsr_prv.u);
    }
    cr_mode_exit: cross cp_mode, cp_exit_kind {
      bins debug_mode_dret= binsof(cp_mode.debug_mode) && binsof(cp_exit_kind.dret);
      bins step_outside_step_complete= binsof(cp_mode.step_outside) && binsof(cp_exit_kind.step_complete);
      bins debug_in_nmi_handler_dret= binsof(cp_mode.debug_in_nmi_handler) && binsof(cp_exit_kind.dret);
      bins debug_in_nmi_handler_step_complete= binsof(cp_mode.debug_in_nmi_handler) && binsof(cp_exit_kind.step_complete);
    }
  endgroup

  // CG-IRQ-011 (gen_irq_reset_fetch_en_cg), 20 coverpoint bins, 10 cross bins
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_NONE = 0;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_REGULAR_ONLY = 1;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_NMI_ONLY = 2;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_NMI_AND_REGULAR = 3;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_DEBUG_AND_NMI = 4;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_DEBUG_AND_REGULAR = 5;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FIRST_EVENT_BOOT_INSN = 0;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FIRST_EVENT_NMI_BEFORE_INSN = 1;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FIRST_EVENT_DEBUG_BEFORE_INSN = 2;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_RESET_READS_MSTATUS_0X80 = 0;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_RESET_READS_MIE_0 = 1;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_RESET_READS_MTVEC_BOOT_PAGE = 2;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_RESET_READS_MIP_REFLECTS_PINS = 3;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_BOOT_MRET_TO_U_MIE1 = 0;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_OFF_IRQ_PENDING_WHILE_OFF_CSR_UPDATED = 0;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_OFF_IRQ_ARRIVES_WHILE_OFF = 1;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_OFF_NMI_WHILE_OFF = 2;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_OFF_NONE_PENDING_WHILE_OFF = 3;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_ON_AFTER_HANDLER_FETCHED_AT_ON = 0;
  localparam int GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_ON_AFTER_RESUME_AT_ON = 1;
  covergroup gen_irq_reset_fetch_en_cg with function sample(int v_cp_lines_at_reset, int v_cp_first_event, int v_cp_reset_reads, int v_cp_boot_mret, int v_cp_fetch_off, int v_cp_fetch_on_after);
    option.per_instance = 0;
    option.cross_auto_bin_max = 0;   // a cross has exactly the CSV's named bins: no automatic bins for the plan's ignored tuples
    cp_lines_at_reset: coverpoint v_cp_lines_at_reset { bins none= {0}; bins regular_only= {1}; bins nmi_only= {2}; bins nmi_and_regular= {3}; bins debug_and_nmi= {4}; bins debug_and_regular= {5}; ignore_bins na = {-1}; }
    cp_first_event: coverpoint v_cp_first_event { bins boot_insn= {0}; bins nmi_before_insn= {1}; bins debug_before_insn= {2}; ignore_bins na = {-1}; }
    cp_reset_reads: coverpoint v_cp_reset_reads { bins mstatus_0x80= {0}; bins mie_0= {1}; bins mtvec_boot_page= {2}; bins mip_reflects_pins= {3}; ignore_bins na = {-1}; }
    cp_boot_mret: coverpoint v_cp_boot_mret { bins to_u_mie1= {0}; ignore_bins na = {-1}; }
    cp_fetch_off: coverpoint v_cp_fetch_off { bins irq_pending_while_off_csr_updated= {0}; bins irq_arrives_while_off= {1}; bins nmi_while_off= {2}; bins none_pending_while_off= {3}; ignore_bins na = {-1}; }
    cp_fetch_on_after: coverpoint v_cp_fetch_on_after { bins handler_fetched_at_on= {0}; bins resume_at_on= {1}; ignore_bins na = {-1}; }
    cr_lines_first: cross cp_lines_at_reset, cp_first_event {
      bins debug_and_nmi_debug_before_insn= binsof(cp_lines_at_reset.debug_and_nmi) && binsof(cp_first_event.debug_before_insn);
      bins debug_and_regular_debug_before_insn= binsof(cp_lines_at_reset.debug_and_regular) && binsof(cp_first_event.debug_before_insn);
      bins nmi_and_regular_nmi_before_insn= binsof(cp_lines_at_reset.nmi_and_regular) && binsof(cp_first_event.nmi_before_insn);
      bins nmi_only_nmi_before_insn= binsof(cp_lines_at_reset.nmi_only) && binsof(cp_first_event.nmi_before_insn);
      bins none_boot_insn= binsof(cp_lines_at_reset.none) && binsof(cp_first_event.boot_insn);
      bins regular_only_boot_insn= binsof(cp_lines_at_reset.regular_only) && binsof(cp_first_event.boot_insn);
    }
    cr_off_on: cross cp_fetch_off, cp_fetch_on_after {
      bins irq_arrives_while_off_handler_fetched_at_on= binsof(cp_fetch_off.irq_arrives_while_off) && binsof(cp_fetch_on_after.handler_fetched_at_on);
      bins irq_pending_while_off_csr_updated_handler_fetched_at_on= binsof(cp_fetch_off.irq_pending_while_off_csr_updated) && binsof(cp_fetch_on_after.handler_fetched_at_on);
      bins nmi_while_off_handler_fetched_at_on= binsof(cp_fetch_off.nmi_while_off) && binsof(cp_fetch_on_after.handler_fetched_at_on);
      bins none_pending_while_off_resume_at_on= binsof(cp_fetch_off.none_pending_while_off) && binsof(cp_fetch_on_after.resume_at_on);
    }
  endgroup
