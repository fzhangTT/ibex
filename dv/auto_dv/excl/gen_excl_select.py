#!/usr/bin/env python3
"""Generate dv/auto_dv/excl/gen_exclusions.el from a URG `-dump full_exclusions` module dump.

The selection below IS gen_exclusions_draft.md v2 (Parts A and C) in executable form: every entry
is taken verbatim (id, checksum, signature) from fullexclude_module.<metric> so -excl_strict can
verify it, and carries the A.0 annotation (class, RTL location, tie chain / parameter, evidence
class and pointer). Nothing outside Parts A/C and the six C.2 default arms is selected (Critic F-7);
the ten A.8 carve-backs and the four class-R arcs are never selected.

Usage: gen_excl_select.py --dump <dir with fullexclude_module.*> --out gen_exclusions.el --report <md>
"""
import argparse, re, subprocess, sys
from pathlib import Path

METRICS = ["line", "branch", "cond", "tgl", "fsm", "assert"]
RE_MOD = re.compile(r'^// ANNOTATION: "ModuleName: (\S+)"')
RE_MODULE = re.compile(r'^// MODULE: (\S+)')
RE_CHK = re.compile(r'^// CHECKSUM: "(.*)"')
RE_SRC = re.compile(r'^// ANNOTATION: "(?:[^"]*?)FileName: (\S+), LineNumber: (\d+)"')
RE_ENTRY = re.compile(r'^// (Block|Branch|Condition|Toggle|Fsm|State|Transition|Assert) ')
RE_VEC_BR = re.compile(r'" \((\d+)\) "')          # branch vector marker
RE_VEC_CO = re.compile(r'" \((\d+) "([01]+)"\)$')   # condition vector marker


class Entry:
    def __init__(self, mod, metric, chk, f, line, header):
        self.mod, self.metric, self.chk, self.file, self.line, self.header = mod, metric, chk, f, line, header
        self.vectors = []   # branch/cond vectors, fsm states+transitions

    def name(self):
        return self.header.split('"')[0].strip()


def parse(dump_dir):
    entries = []
    for metric in METRICS:
        p = Path(dump_dir) / f"fullexclude_module.{metric}"
        if not p.exists():
            continue
        mod = chk = f = None
        line = 0
        cur = None
        for raw in p.read_text().splitlines():
            m = RE_CHK.match(raw)
            if m:
                chk = m.group(1); cur = None; continue
            m = RE_MOD.match(raw) or RE_MODULE.match(raw)
            if m:
                mod = m.group(1); cur = None; f = None; line = -1; continue
            m = RE_SRC.match(raw)
            if m:
                f, line = m.group(1), int(m.group(2)); cur = None; continue
            m = RE_ENTRY.match(raw)
            if not m or mod is None:
                continue
            kind = m.group(1)
            text = raw[3:]
            if kind in ("Block", "Toggle", "Assert"):
                cur = Entry(mod, metric, chk, f, line, text); entries.append(cur)
            elif kind in ("Branch", "Condition"):
                is_vec = (kind == "Branch" and RE_VEC_BR.search(text)) or (kind == "Condition" and RE_VEC_CO.search(text))
                if is_vec and cur is not None and cur.header.split('"')[0:2] == text.split('"')[0:2]:
                    cur.vectors.append(text)
                else:
                    cur = Entry(mod, metric, chk, f, line, text); entries.append(cur)
            elif kind == "Fsm":
                cur = Entry(mod, metric, chk, f, line, text); entries.append(cur)
            elif kind in ("State", "Transition"):
                if cur is not None:
                    cur.vectors.append(text)
    return entries


RE_STMT_HDR = re.compile(r'^Block \d+ "\d+" "(if|else if|unique case|priority case|case|unique if|for) ?\(')


def in_ranges(line, ranges):
    return any(lo <= line <= hi for lo, hi in ranges)


# ---------------------------------------------------------------------------------------------
# Annotation texts (A.0 shape: class, location, tie chain or parameter, evidence class + pointer)
# ---------------------------------------------------------------------------------------------
A0 = ("cheriot-out-of-scope: owner ruling DV_prompt.txt Section 2 (2026-09-02); gen_dut_top ties "
      "ibex_core.cheriot_enable_i to ibex_pkg::IbexMuBiOff (dv/auto_dv/tb/gen_dut_top.sv:206). ")


def ann_T(where, evidence, extra=""):
    return (A0 + f"Class T (constant tie). {where}. Reachable only with cheriot_enable_i == IbexMuBiOn. "
            f"EC-1 k-induction PASS {evidence} (dv/auto_dv/evidence/gen_t022_formal/, "
            f"gen_unreachability_evidence.md 4.1/4.2); EC-2 constfile; EC-3 IbexCheriot*Disabled assertions; EC-5 strict load. {extra}").strip()


def ann_P(where, param, evidence):
    return (f"Class P (build-parameter constant, opentitan configuration, values verified against util/ibex_config.py at generation): {where}. {param} is an elaboration "
            f"constant (dv/auto_dv/evidence/gen_param_resolution.md; time-0 config banner). "
            f"EC-1 {evidence}; EC-2 expected URG Unreachable; EC-5 strict load. gen_exclusions_draft.md Part C.")


def ann_D2a(where, enum):
    return (f"Class D (enum default arm, no spare encoding): {where}. {enum}. The default arm is unreachable "
            f"by construction of the enum. EC-1 declaration cite; EC-5 strict load. gen_exclusions_draft.md C.2.")


def ann_D2b(where, statereg, spare, guard, proof):
    return (f"Class D (enum default arm, spare encodings): {where}. Unreachable without fault injection into "
            f"{statereg}; {spare} spare encodings; guarded by RTL assertion {guard} (EC-3: attempts N, failures 0 "
            f"in <first measured regression>, TO BE FILLED); measured merge contains legal-stimulus tiers only "
            f"(gen_exclusions_draft.md B.7 rule 6); EC-1 k-induction proof {proof} "
            f"(dv/auto_dv/evidence/gen_t022_formal/); EC-5 strict load.")


# ---------------------------------------------------------------------------------------------
# Selection spec = gen_exclusions_draft.md Parts A.3-A.7, C.2, C rows 12/30/32/42-43
# ---------------------------------------------------------------------------------------------
# A.8 carve-backs (draft v2 A.8 and its v1 list): objects that are LIVE in RV32I mode and must never be
# selected whatever range or predicate would pick them. Signature regexes are matched against the
# dump entry line; ranges are RTL lines. Applied as the last filter over every shared-module entry.
CARVE_BACK = {
    # mstack_epc_cap_q updates on every non-debug trap (mstack_en, :933); pcc_cap_d / tf_cap / tr_cap /
    # pcc_exc_cap are live NETS (no toggle object under portsonly) whose gated consumers stay excludable
    "ibex_cs_registers": {"sig": [r"mstack_epc_cap_q", r"_combi\b"], "lines": []},
    "ibex_controller": {"sig": [r"illegal_insn_d\s*="], "lines": [(827, 840), (909, 914), (923, 926)]},
    "ibex_id_stage": {"sig": [r"instr_kill", r"instr_is_rv32lsu_id"], "lines": [(1033, 1036)]},
    "ibex_core": {"sig": [r"rvfi_id_done\s*=", r"branch_target_ex\s*=", r"alert_major_internal_o\s*="], "lines": [(1851, 1853)]},
    "ibex_load_store_unit": {"sig": [r"resp_is_cap_q\s*<=", r"resp_lc_clrperm_q\s*<="], "lines": [(650, 653), (664, 667)]},
    "ibex_decoder": {"sig": [r"illegal_insn\s*=\s*1'b1;"], "lines": []},
    "ibex_register_file_ff": {"sig": [r"rf_shared\[", r"wshared_data", r"we_shared_r0", r"rf_shared_r0_q", r"rcap_r0", r"we_data_r0", r"rf_data_r0_q"], "lines": []},
    "ibex_cheriot_ex": {"sig": [r"csr_mshwm_new_o"], "lines": [(699, 737), (943, 960), (970, 973), (991, 994)]},
}


def carved_back(mod, line_text, rtl_line):
    cb = CARVE_BACK.get(mod)
    if not cb:
        return False
    if rtl_line is not None and in_ranges(rtl_line, cb["lines"]):
        return True
    return any(re.search(rx, line_text) for rx in cb["sig"])


MODULE_RTL = {"ibex_core": "rtl/ibex_core.sv", "ibex_id_stage": "rtl/ibex_id_stage.sv", "ibex_decoder": "rtl/ibex_decoder.sv",
              "ibex_compressed_decoder": "rtl/ibex_compressed_decoder.sv", "ibex_controller": "rtl/ibex_controller.sv",
              "ibex_load_store_unit": "rtl/ibex_load_store_unit.sv", "ibex_cs_registers": "rtl/ibex_cs_registers.sv",
              "ibex_if_stage": "rtl/ibex_if_stage.sv", "ibex_wb_stage": "rtl/ibex_wb_stage.sv", "ibex_multdiv_fast": "rtl/ibex_multdiv_fast.sv",
              "ibex_icache": "rtl/ibex_icache.sv", "ibex_register_file_ff": "rtl/ibex_register_file_ff.sv", "ibex_cheriot_ex": "rtl/ibex_cheriot_ex.sv"}
# class-D 2a default arms: the guard analysis cannot see the enum width, the enum declaration is the cone
EXPLICIT_BLOCK_RANGES = {("ibex_id_stage", (968, 970)), ("ibex_multdiv_fast", (238, 240)), ("ibex_icache", (1268, 1268)),
                         ("ibex_controller", (990, 993)), ("ibex_load_store_unit", (605, 607)), ("ibex_multdiv_fast", (522, 524)),
                         # case items of states the k-induction proofs show are never held (T022_LSU_NO_CTX, T022_CRX_IDLE):
                         # the cone is the state register, not a guard term
                         ("ibex_load_store_unit", (565, 603)), ("ibex_load_store_unit", (618, 623))}

BLOCKS = [  # (module, [(lo,hi)...], annotation)
    ("ibex_core", [(2223, 2225)], ann_T("rtl/ibex_core.sv:2223-2225 RVFI cap-read arm (resp_is_cap_q)", "T022_LSU_CHERI0", "+define+RVFI builds only.")),
    ("ibex_id_stage", [(901, 908)], ann_T("rtl/ibex_id_stage.sv:901-908 cheriot_lsu_req_dec case item (Part C row 29)", "T022_ID_CHERI0, T022_DEC_CHERI0")),
    ("ibex_decoder", [(314, 323), (339, 352), (402, 407), (447, 453), (474, 482), (793, 876), (883, 891)],
     ann_T("rtl/ibex_decoder.sv CHERIoT arms of JAL/JALR/STORE/LOAD/AUIPC and the OPCODE_CHERI / OPCODE_AUICGP bodies (case items and their illegal arms stay live, A.8)", "T022_DEC_CHERI0")),
    ("ibex_compressed_decoder", [(230, 233), (249, 252), (329, 332), (359, 363), (391, 394), (411, 414), (557, 560), (575, 579), (615, 620), (854, 857)],
     ann_T("rtl/ibex_compressed_decoder.sv the ten (BaseIsa dual && cheriot_enable_i == On) arms (Part C row 36 for :615-620)", "wrapper tie (constant compare)")),
    ("ibex_controller", [(850, 858), (894, 897), (901, 908), (915, 922), (928, 948), (318, 319), (328, 331)],
     ann_T("rtl/ibex_controller.sv CHERIoT exception arms (Part C rows 2-3, 5-10)", "T022_CORE_CHERI0_B, T022_CTRL_CHERI0, T022_CTRL_PRIO0")),
    ("ibex_load_store_unit", [(139, 140), (211, 219), (437, 467), (565, 603), (616, 617), (618, 623), (669, 678)],
     ann_T("rtl/ibex_load_store_unit.sv cap arms, CTX_* and cap_rx items (Part C rows 14-22, 24-28)", "T022_LSU_CHERI0, T022_LSU_NO_CTX, T022_CRX_IDLE")),
    ("ibex_cs_registers", [(469, 475), (478, 484), (678, 698), (707, 715), (2014, 2056), (2063, 2067), (2108, 2209), (2218, 2224)],
     ann_T("rtl/ibex_cs_registers.sv CHERIoT CSR arms (mtvec/mepc illegal-under-On, MSHWM/MSHWMB/CDBG_CTRL reads, PMP-illegal block, SCR mux, pcc/cap updates, fatal_err set); the else/illegal arms stay live (A.8)", "T022_CSR_CHERI0, T022_CSR_MSHWM0")),
    # class P blocks
    ("ibex_controller", [(690, 696)], ann_P("rtl/ibex_controller.sv:690-696 if (BranchPredictor) body (Part C row 12)", "BranchPredictor = 0", "T022_CORE_BP0 PROVED; yosys constants instr_bp_taken_id = 0 (evidence 4.3)")),
    ("ibex_decoder", [(1342, 1344), (1348, 1350)], ann_P("rtl/ibex_decoder.sv:1342-1344, :1348-1350 BCOMPRESS/BDECOMPRESS multicycle bodies (Part C rows 42-43; the case items :1341/:1347 stay live)", "RV32B = RV32BOTEarlGrey (RV32B == RV32BFull is false)", "configuration + legality case :641-642")),
    # class D blocks (default-arm statements)
    ("ibex_controller", [(990, 993)], ann_D2b("rtl/ibex_controller.sv:990-993 ctrl_fsm default -> RESET (Part C row 1)", "ctrl_fsm_cs (ctrl_fsm_e 4-bit, 10 named values, rtl/ibex_pkg.sv:291-302)", "6", "IbexCtrlStateValid (rtl/ibex_controller.sv:1104-1106)", "T022_CTRL_NAMED")),
    ("ibex_load_store_unit", [(605, 607)], ann_D2b("rtl/ibex_load_store_unit.sv:605-607 ls_fsm default (Part C row 23)", "ls_fsm_cs (ls_fsm_e 4-bit, 8 named values, rtl/ibex_pkg.sv:816-820)", "8", "IbexLsuStateValid (rtl/ibex_load_store_unit.sv:821-824)", "T022_LSU_NAMED")),
    ("ibex_multdiv_fast", [(522, 524)], ann_D2b("rtl/ibex_multdiv_fast.sv:522-524 md_state default (Part C row 33)", "md_state_q (md_fsm_e 3-bit, 7 named values, :90-92)", "1", "IbexMultDivStateValid (rtl/ibex_multdiv_fast.sv:532-533)", "T022_MD_NAMED")),
    ("ibex_id_stage", [(968, 970)], ann_D2a("rtl/ibex_id_stage.sv:968-970 id_fsm default (Part C row 31)", "no spare encoding: 1-bit enum, 2 named values (rtl/ibex_id_stage.sv:861)")),
    ("ibex_multdiv_fast", [(238, 240)], ann_D2a("rtl/ibex_multdiv_fast.sv:238-240 mult_fsm default (Part C row 34)", "no spare encoding: 1-bit enum, 2 named values (rtl/ibex_multdiv_fast.sv:142-144)")),
    ("ibex_icache", [(1268, 1268)], ann_D2a("rtl/ibex_icache.sv:1268 inval_state default (Part C row 35)", "no spare encoding: 2-bit enum, 4 named values (rtl/ibex_icache.sv:193-198)")),
]

TRUE_ARM = r'\) 1"$|[a-zA-Z_\]\)] 1"$'   # ternary/if true arm vector: signature ends with " 1"
FALSE_ARM = r' 0"$'
BRANCHES = [  # (module, ranges, vector regex, annotation)
    ("ibex_core", [(1000, 1001)], TRUE_ARM, ann_T("rtl/ibex_core.sv:1000-1001 branch_target_ex mux, CHERIoT arm (instr_is_cheriot_id)", "T022_CORE_CHERI0")),
    ("ibex_core", [(1590, 1593), (1627, 1630)], TRUE_ARM, ann_T("rtl/ibex_core.sv:1590-1593, :1627-1630 g_pmp_*_gate ternaries, (cheriot_enable_i == On) true arms", "wrapper tie")),
    ("ibex_if_stage", [(222, 228)], TRUE_ARM, ann_T("rtl/ibex_if_stage.sv:222-228 exc_pc ternaries, CHERIoT arms", "T022_IF_CHERI0")),
    ("ibex_id_stage", [(578, 578), (746, 749)], TRUE_ARM, ann_T("rtl/ibex_id_stage.sv:578 ex_valid_all and :746-749 csr_op_en_o ternaries, CHERIoT arms (instr_is_cheriot_id_o)", "T022_ID_CHERI0")),
    ("ibex_decoder", [(202, 202)], TRUE_ARM, ann_T("rtl/ibex_decoder.sv:202 raddr_a CAUICGP ternary, CHERIoT arm", "T022_DEC_CHERI0")),
    ("ibex_decoder", [(212, 217)], TRUE_ARM, ann_T("rtl/ibex_decoder.sv:212-217 gen_16_regs ternaries, masked (CHERIoT) arms; pass-through arms live (A.8 item 8)", "T022_DEC_CHERI0 illegal_reg_16 == 0")),
    ("ibex_controller", [(866, 868)], TRUE_ARM, ann_T("rtl/ibex_controller.sv:866-868 illegal mtval ternary, CHERIoT arm only (Part C row 4; RV32I arm live, A.8 item 2)", "wrapper tie")),
    ("ibex_load_store_unit", [(131, 132), (702, 709)], TRUE_ARM, ann_T("rtl/ibex_load_store_unit.sv:131-132 data_offset and :702-709 gen_memcap_rd ternaries, CHERIoT arms (RV32I arms live)", "T022_LSU_CHERI0")),
    ("ibex_wb_stage", [(182, 183), (215, 215)], TRUE_ARM, ann_T("rtl/ibex_wb_stage.sv:182-183, :215 rf_wdata muxes, wb_is_cheriot_q arms", "T022_WB_CHERI0")),
    ("ibex_cs_registers", [(424, 426)], TRUE_ARM, ann_T("rtl/ibex_cs_registers.sv:424-426 CSR_MARCHID ternary, CHERIoT arm (32'hce1)", "wrapper tie")),
    ("ibex_register_file_ff", [(113, 113), (227, 230)], TRUE_ARM, ann_T("rtl/ibex_register_file_ff.sv:113 wshared_data and :227-230 rcap ternaries, cap arms", "T022_RF_CAP0")),
    # class P branches
    ("ibex_controller", [(684, 684)], TRUE_ARM, ann_P("rtl/ibex_controller.sv:684 pc_set_o = BranchPredictor ? ~instr_bp_taken_i : 1'b1, true arm only (Part C row 12)", "BranchPredictor = 0", "T022_CORE_BP0 PROVED")),
    ("ibex_id_stage", [(936, 942)], FALSE_ARM, ann_P("rtl/ibex_id_stage.sv:936-942 jump: BranchTargetALU ? FIRST_CYCLE : MULTI_CYCLE, MULTI_CYCLE (false) arm only (Part C row 30)", "BranchTargetALU = 1", "elaboration constant (config + banner)")),
    # class D default-arm branch vectors
]

CONST0 = {"instr_is_cheriot_id", "instr_is_cheriot_i", "instr_is_cheriot_o", "instr_is_cheriot_id_o", "cheriot_exec_id", "cheriot_exec_id_i",
          "cheriot_exec_id_o", "lsu_is_cap", "lsu_is_cap_i", "cheriot_wb_err_q", "cheriot_ex_err_q", "cheriot_asr_err_q", "resp_is_cap_q",
          "lsu_err_is_cheriot_q", "lsu_err_is_cheriot_i", "lsu_err_is_cheriot", "wb_is_cheriot_q", "wb_cheriot_load_q", "wb_cheriot_store_q",
          "cheriot_enabled", "cheriot_fatal_err", "cheriot_fatal_err_q", "cheriot_enable_mubi_err", "cheriot_err_q", "cheriot_lsu_req_dec",
          "cheriot_branch_req", "cheriot_branch_req_i", "cheriot_branch_req_spec", "cheriot_data_req_o", "lsu_cheriot_err", "lsu_cheriot_err_i",
          "cheriot_wb_err", "cheriot_ex_err", "cheriot_wb_err_i", "cheriot_ex_err_i", "instr_is_cheriot", "cheriot_csr_op_en", "cheriot_csr_op_en_i",
          "cheriot_csr_set_mie", "cheriot_csr_clr_mie", "cheriot_csr_set_mie_i", "cheriot_csr_clr_mie_i", "csr_mshwm_set", "csr_mshwm_set_i",
          "cheriot_lsu_req", "cpu_req_erred", "lsu_go_goodcap", "instr_is_legal_cheriot", "illegal_reg_16", "cheriot_load_id", "cheriot_store_id",
          "cheriot_rf_we", "cheriot_rf_we_q", "cheriot_rf_we_i", "csr_dbg_tclr_fault", "instr_fetch_cheriot_acc_vio", "instr_fetch_cheriot_bound_vio",
          "instr_fetch_cheriot_acc_vio_i", "instr_fetch_cheriot_bound_vio_i", "cheriot_acc_vio", "cheriot_bound_vio", "cheriot_force_uc",
          "cheriot_load_i", "cheriot_store_i", "cpu_lsu_is_cap", "cheriot_lsu_is_cap", "mshwm_en", "mshwmb_en", "cdbg_ctrl_en", "cheriot_fatal_err_o",
          "lsu_cheriot_err_o", "cheriot_csr_access_i", "cheriot_csr_access", "mshwm_en_combi", "csr_mepcc_clrtag"}
RE_ON = re.compile(r'^\(?\s*cheriot_enable_i\s*==\s*(ibex_pkg::)?IbexMuBiOn\s*\)?$')
RE_ISOFF = re.compile(r'^\(?\s*cheriot_enable_i\s*==\s*(ibex_pkg::)?IbexMuBiOff\s*\)?$')
RE_OFF = re.compile(r'^\(?\s*cheriot_enable_i\s*!=\s*(ibex_pkg::)?IbexMuBiOn\s*\)?$')
RE_NEG = re.compile(r'^\(?\s*[~!]\s*\(?\s*([A-Za-z_][\w.]*)\s*\)?\s*\)?$')
RE_NAME = re.compile(r'^\(?\s*([A-Za-z_][\w.]*)\s*\)?$')
RE_ONAND = re.compile(r'cheriot_enable_i\s*==\s*(ibex_pkg::)?IbexMuBiOn')


def split_neg(o):
    """If `o` is a unary negation of ONE operand (`~x`, `!x`, `~(...)` with the group covering the rest),
    return that operand; `~a && b` is a binary expression and returns None."""
    m = re.match(r"^[~!]\s*(.+)$", o.strip())
    if not m:
        return None
    rest = m.group(1).strip()
    if re.match(r"^[\w.\[\]':]+$", rest):
        return rest
    if rest.startswith("("):
        depth = 0
        for i, c in enumerate(rest):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return rest if i == len(rest) - 1 else None
    return None


def strip_outer(s):
    s = s.strip()
    while s.startswith("(") and s.endswith(")"):
        depth = 0; ok = True
        for i, c in enumerate(s):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0 and i != len(s) - 1:
                    ok = False; break
        if not ok:
            break
        s = s[1:-1].strip()
    return s


def split_top_ops(expr):
    """Split at top-level binary operators; return (operands, operators) in URG's operand order."""
    ops, kinds, depth, cur, i = [], [], 0, "", 0
    while i < len(expr):
        c = expr[i]
        two = expr[i:i + 2]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if depth == 0 and two in ("||", "&&", "==", "!="):
            if two in ("==", "!="):
                cur += two; i += 2; continue
            ops.append(cur); kinds.append(two); cur = ""; i += 2; continue
        if depth == 0 and c in "|&^":
            ops.append(cur); kinds.append(c); cur = ""; i += 1; continue
        cur += c; i += 1
    ops.append(cur)
    return [o.strip() for o in ops], kinds


def split_top(expr):
    return split_top_ops(expr)[0]


def last_name(n):
    return n.split(".")[-1]


def split_ternary(expr):
    """Return the select expression of a top-level `sel ? a : b`, or None."""
    depth = 0
    for i, c in enumerate(expr):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "?" and depth == 0:
            return expr[:i].strip()
    return None


EX_MODE = False


def const_value(operand, _depth=0):
    """Return the impossible value (0/1) of a constant-tie operand, or None."""
    o = strip_outer(operand)
    if _depth > 3:
        return None
    if EX_MODE:
        # ternary condition / top-level negation keep URG's encoding rules below; plain terms use the
        # module constant table
        if split_ternary(o) is None and split_neg(o) is None:
            cv = ex_const(o)
            if cv is not None:
                return 1 - cv
    sel = split_ternary(o)
    if sel is not None:
        # URG encodes a ternary CONDITION by its select; a ternary used as an operand has the value
        # of an arm, which is not the select: only classify at the top level.
        return const_value(sel, _depth + 1) if _depth == 0 else None
    neg = split_neg(o)
    if neg is not None:
        inner = const_value(neg, _depth + 1)
        if inner is None:
            return None
        # top-level negation: URG's vector bit is the value of the negated sub-expression itself
        return inner if _depth == 0 else 1 - inner
    if RE_ON.match(o):
        return 1
    if RE_OFF.match(o) or RE_ISOFF.match(o):
        return 0
    m = RE_NAME.match(o)
    if m and (last_name(m.group(1)) in CONST0 or re.search(r'_en_cheriot$|cheriot_asr_err', last_name(m.group(1)))
              or "cheriot_operator_o." in m.group(1)):
        return 1
    parts, kinds = split_top_ops(o)
    if len(parts) > 1 and kinds:
        vals = [const_value(p, _depth + 1) for p in parts]
        if all(k in ("&", "&&") for k in kinds) and any(v == 1 for v in vals):
            return 1   # AND with a constant-0 factor is constant 0: value 1 impossible
        if all(k in ("|", "||") for k in kinds) and any(v == 0 for v in vals):
            return 0   # OR with a constant-1 term is constant 1: value 0 impossible
        if all(k in ("|", "||") for k in kinds) and all(v == 1 for v in vals):
            return 1   # OR of constant-0 terms is constant 0: value 1 impossible
        if all(k in ("&", "&&") for k in kinds) and all(v == 0 for v in vals):
            return 0   # AND of constant-1 terms is constant 1: value 0 impossible
    return None


def select_conditions(entries, live_lines_cheriot_ex, report):
    global EX_MODE
    """A.4 / A.1: vectors in which a constant-tie operand takes its impossible value."""
    out = []
    unclassified = []
    for e in entries:
        if e.metric != "cond":
            continue
        sig = e.header.split('"')[3] if e.header.count('"') >= 4 else ""
        expr = sig.rsplit(" ", 2)[0] if sig else ""
        if e.mod == "ibex_cheriot_ex" and e.line in live_lines_cheriot_ex:   # here: the DEAD line map
            out.append((e, list(e.vectors), "A1"))
            continue
        global EX_MOD
        EX_MODE = (e.mod == "ibex_cheriot_ex")
        EX_MOD = e.mod
        ops = split_top(strip_outer(expr))
        vals = [const_value(expr, 0)] if len(ops) == 1 else [const_value(o, 1) for o in ops]
        EX_MODE = False
        if all(v is None for v in vals):
            if re.search(r'cheriot|is_cap|IbexMuBiOn', re.sub(r'g_cheriot_(rf|ex)\.', '', expr)) and e.mod != "ibex_cheriot_ex":
                unclassified.append(f"{e.mod} {Path(e.file).name if e.file else '?'}:{e.line} {expr}")
            continue
        sel = []
        for v in e.vectors:
            m = RE_VEC_CO.search(v)
            if not m:
                continue
            bits = m.group(2)
            if len(bits) != len(ops):
                unclassified.append(f"{e.mod} {Path(e.file).name if e.file else '?'}:{e.line} width mismatch {len(bits)} vs {len(ops)}: {expr}")
                sel = []; break
            if any(val is not None and bits[i] == str(val) for i, val in enumerate(vals)):
                sel.append(v)
        if sel:
            terms = "; ".join(f"`{strip_outer(o)[:60]}` constant {1 - val} (vector bit {val} impossible)"
                              for o, val in zip(ops, vals) if val is not None)
            e.terms = terms
            out.append((e, sel, "A4"))
    report.append(f"Conditions: {sum(1 for _ in out)} condition objects, {sum(len(s) for _, s, _ in out)} vectors selected ({sum(len(s) for _, s, t in out if t == 'A1')} A.1 all-vector, {sum(len(s) for _, s, t in out if t == 'A4')} A.4 impossible-value).")
    if unclassified:
        report.append("Conditions mentioning a CHERIoT name but NOT selected (manual follow-up; kept in coverage):")
        report.extend("  - " + u for u in sorted(set(unclassified)))
    return out


TOGGLES = {
    "ibex_core": ["cheriot_enable_i", "data_tag_o", "data_tag_i", "rf_wcap_ecc_wb_o", "rf_rcap_a_ecc_i", "rf_rcap_b_ecc_i",
                  "rvfi_rs1_rcap", "rvfi_rs2_rcap", "rvfi_rd_wcap", "rvfi_mem_is_cap", "rvfi_mem_rcap", "rvfi_mem_wcap"],
    "ibex_if_stage": ["cheriot_enable_i", "instr_fetch_cheriot_acc_vio_o", "instr_fetch_cheriot_bound_vio_o", "pcc_cap_i"],
    "ibex_id_stage": ["cheriot_enable_i", "cheriot_exec_id_o", "instr_is_cheriot_id_o", "cheriot_imm12_o", "cheriot_imm20_o", "cheriot_imm21_o",
                      "cheriot_operator_o", "cheriot_cs2_dec_o", "cheriot_cap_field_sel_o", "cheriot_adder_a_sel_o", "cheriot_adder_b_sel_o",
                      "cheriot_setaddr_sel_o", "cheriot_setbounds_sel_o", "cheriot_load_o", "cheriot_store_o", "cheriot_ex_valid_i", "cheriot_ex_err_i",
                      "cheriot_ex_err_info_i", "cheriot_wb_err_i", "cheriot_wb_err_info_i", "cheriot_branch_req_i", "cheriot_branch_target_i",
                      "lsu_err_is_cheriot_i", "csr_pcc_perm_sr_i", "csr_mepcc_clrtag_o", "instr_fetch_cheriot_acc_vio_i", "instr_fetch_cheriot_bound_vio_i"],
    "ibex_decoder": None,      # every cheriot_* / csr_pcc_perm_sr_i / csr_mepcc_clrtag_o / instr_fetch_cheriot_*_i / instr_is_cheriot_* / lsu_err_is_cheriot* port
    "ibex_controller": None,
    "ibex_load_store_unit": ["cheriot_enable_i", "lsu_is_cap_i", "lsu_cheriot_err_i", "lsu_wcap_i", "lsu_lc_clrperm_i", "lsu_rcap_o", "data_tag_o", "data_tag_i", "lsu_err_is_cheriot_o"],
    "ibex_wb_stage": ["instr_is_cheriot_i", "cheriot_load_i", "cheriot_store_i", "cheriot_rf_we_i", "cheriot_rf_wdata_i", "cheriot_rf_wcap_i", "rf_wcap_lsu_i", "rf_wcap_fwd_wb_o", "rf_wcap_wb_o"],
    "ibex_cs_registers": ["cheriot_enable_i", "cheriot_csr_access_i", "cheriot_csr_addr_i", "cheriot_csr_wdata_i", "cheriot_csr_wcap_i", "cheriot_csr_op_i",
                          "cheriot_csr_op_en_i", "cheriot_csr_set_mie_i", "cheriot_csr_clr_mie_i", "cheriot_csr_rdata_o", "cheriot_csr_rcap_o", "csr_mshwm_o",
                          "csr_mshwmb_o", "csr_mshwm_set_i", "cheriot_branch_req_i", "cheriot_branch_target_i", "pcc_cap_i", "pcc_cap_o", "csr_dbg_tclr_fault_o", "cheriot_fatal_err_o"],
    "ibex_compressed_decoder": ["cheriot_enable_i"],
    "ibex_register_file_ff": ["cheriot_enable_i", "rcap_a_o", "rcap_b_o", "wcap_a_i"],
    "ibex_cheriot_ex": ["fwd_wcap_i", "rf_rcap_a_i", "rf_rcap_b_i", "pcc_cap_i", "pcc_cap_o", "csr_mshwm_i", "csr_mshwmb_i", "csr_mshwm_set_o", "csr_rcap_i",
                        "csr_wcap_o", "lsu_wcap_o", "lsu_is_cap_o", "lsu_lc_clrperm_o", "lsu_cheriot_err_o"],  # plus every cheriot_* port (A.1)
}
RE_TGL_GENERIC = re.compile(r'^(cheriot_\w*|csr_pcc_perm_sr_i|csr_mepcc_clrtag_o|instr_fetch_cheriot_\w*_i|instr_is_cheriot\w*|lsu_err_is_cheriot\w*)$')
TGL_ANN = ann_T("A.5 constant CHERIoT-only port (gen_cheriot_carveout.md bucket D port-level view); both edges excluded",
                "tie chain G1-G8 (T022_CORE_CHERI0/_B, T022_RF_CAP0)", "-cm_tgl portsonly: ports are the only toggle objects.")

FSMS = [
    ("ibex_load_store_unit", "ls_fsm_cs", ["CTX_WAIT_GNT1", "CTX_WAIT_GNT2", "CTX_WAIT_RESP"], r'CTX_',
     ann_T("A.6 rtl/ibex_load_store_unit.sv ls_fsm_cs CTX_* states and every transition touching them (Part C rows 14-22; gen_hierarchy_map.md FSM-2)", "T022_LSU_NO_CTX")),
    ("ibex_load_store_unit", "cap_rx_fsm_q", ["CRX_WAIT_RESP1", "CRX_WAIT_RESP2"], r'CRX_',
     ann_T("A.6 rtl/ibex_load_store_unit.sv cap_rx_fsm_q frozen in CRX_IDLE: both wait states and every transition (Part C rows 24-28; FSM-3)", "T022_CRX_IDLE")),
]

ASSERTS = [
    ("ibex_register_file_ff", ["CheriotWaddrMSBClear", "CheriotRaddrAMSBClear", "CheriotRaddrBMSBClear"],
     ann_T("A.7 rtl/ibex_register_file_ff.sv:237-239 `ASSERT(name, cheriot_enabled |-> ...)` with antecedent cheriot_enabled == constant 0: vacuous, never covered", "T022_RF_CAP0")),
]

# A.5 for ibex_cheriot_ex: the constant CHERIoT-only ports (toggle objects); live RV32I ports never selected
CHERIOT_EX_LIVE_PORTS = {"lsu_req_o", "lsu_we_o", "lsu_addr_o", "lsu_wdata_o", "lsu_type_o", "lsu_sign_ext_o", "rv32_addr_incr_req_o", "rv32_addr_last_o",
                         "rv32_lsu_req_i", "rv32_lsu_we_i", "rv32_lsu_type_i", "rv32_lsu_wdata_i", "rv32_lsu_sign_ext_i", "rv32_lsu_addr_i", "rv32_lsu_err",
                         "addr_incr_req_i", "addr_last_i", "csr_rdata_i", "csr_mstatus_mie_i", "csr_mshwm_new_o", "fwd_wdata_i", "fwd_we_i", "fwd_waddr_i",
                         "rf_rdata_a_i", "rf_rdata_b_i", "rf_raddr_a_i", "rf_raddr_b_i", "pc_id_i", "debug_mode_i", "instr_valid_i", "instr_first_cycle_i",
                         "instr_is_compressed_i", "instr_is_rv32lsu_i", "clk_i", "rst_ni", "lsu_req_done_i", "lsu_resp_valid_i", "lsu_load_err_i",
                         "lsu_store_err_i", "rv32_lsu_err_i"}


def ann_ex(reason, line):
    return (A0 + f"Class T (dead arm inside u_ibex_cheriot_ex, A.1 revised): rtl/ibex_cheriot_ex.sv:{line}: {reason}. "
            f"Term(s) {CHERIOT_EX_EVIDENCE}. Reachable-but-masked logic of this module is NOT excluded. "
            f"EC-1 constant propagation + k-induction; EC-5 strict load.")




# ---------------------------------------------------------------------------------------------
# A.1: ibex_cheriot_ex objects are excluded only when an enclosing guard is provably dead under the
# cheriot_enable_i tie (a "dead arm"); reachable-but-masked logic counts. The constants below are the
# machine-checked ones.
# ---------------------------------------------------------------------------------------------
# 1-bit nets of u_ibex_cheriot_ex that yosys `opt -full` ties to 1'0 with the wrapper tie
# (dv/auto_dv/work/rtl-arch/t022/model/t022_flat.il `connect` lines, regenerable by
# dv/auto_dv/evidence/gen_t022_formal/gen_t022_regen.sh step 3; EC-1 by constant propagation).
CHERIOT_EX_CONST0_1BIT = {
    "branch_req_o", "branch_req_raw", "branch_req_spec_o", "branch_req_spec_raw", "cheriot_exec_id_i",
    "cheriot_ex_err_o", "cheriot_ex_err_raw", "cheriot_ex_valid_o", "cheriot_lsu_err", "cheriot_lsu_is_cap",
    "cheriot_lsu_req", "cheriot_lsu_we", "cheriot_rf_we_o", "cheriot_wb_err_d", "cheriot_wb_err_o",
    "cheriot_wb_err_q", "chk_cs2_bad_type", "cpu_lsu_cheriot_err", "csr_access_o", "csr_clr_mie_o",
    "csr_clr_mie_raw", "csr_op_en_o", "csr_op_en_raw", "csr_set_mie_o", "csr_set_mie_raw",
    "illegal_scr_addr", "instr_is_cheriot_i", "is_cap", "is_load_cap", "is_store_cap", "lsu_cheriot_err_o",
    "perm_vio_slc", "req_exact", "rv32_lsu_err", "scr_legalization"}
# nets of OTHER modules that carry the same constants (cheriot_ex outputs seen at the consumer's ports)
MODULE_CONST_ZERO_MULTI = {
    "ibex_cs_registers": {"cheriot_csr_addr_i", "cheriot_csr_op_i", "cheriot_csr_wdata_i", "cheriot_csr_wcap_i", "cheriot_branch_target_i"},
}
# multi-bit inputs/nets of u_ibex_cheriot_ex that the same netlist ties to all-zero (value 0): the
# decoder assigns them only inside (cheriot_enable_i == On) arms and defaults them to the zero
# literal (rtl/ibex_decoder.sv:297-303), which the netlist confirms.
CHERIOT_EX_CONST_ZERO_MULTI = {
    "cheriot_adder_a_sel_i", "cheriot_adder_b_sel_i", "cheriot_cap_field_sel_i", "cheriot_cs2_dec_i",
    "cheriot_imm12_i", "cheriot_imm20_i", "cheriot_imm21_i", "cheriot_operator_i", "cheriot_setaddr_sel_i",
    "cheriot_setbounds_sel_i", "csr_addr_o", "csr_op_o", "cheriot_lsu_wcap", "csc_wcap", "csr_wcap_o",
    "lsu_wcap_o", "result_cap_o", "rf_rcap_a_i", "rf_rcap_b_i", "ztop_rcap_i"}
CHERIOT_EX_EVIDENCE = ("constant under the cheriot_enable_i tie: yosys constant propagation, "
                       "t022_flat.il connect list (gen_t022_regen.sh step 3) and the decoder defaults "
                       "rtl/ibex_decoder.sv:297-303 with CHERIoT-only assignments; T022_DEC_CHERI0, T022_ID_CHERI0")


def self_test():
    """Classifier self-test: negation precedence, ternary and negation vector encodings, scoping."""
    global EX_MOD
    EX_MOD = "ibex_cheriot_ex"
    cases = [
        (ex_const("~is_cap && debug_mode_i"), None, "unary negation binds to is_cap only: ~0 && x is not constant"),
        (ex_const("~(is_cap && debug_mode_i)"), 1, "negated group of a constant-0 AND is constant 1"),
        (ex_const("~is_cap"), 1, "negated constant-0 term"),
        (ex_const("is_cap | cheriot_operator_i.CJALR"), 0, "OR of constant-0 terms"),
        (ex_const("(cheriot_enable_i != ibex_pkg::IbexMuBiOn) | instr_is_rv32lsu_i"), 1, "OR with the constant-1 tie compare"),
        (ex_const("cheriot_setaddr_sel_i == SETADDR_PCC_PCNXT"), 0, "all-zero select compared with a non-zero literal"),
        (ex_const("debug_mode_i"), None, "a driven pin is not constant"),
        (const_value("~instr_is_cheriot_i | x", 1), 0, "operand-level: ~0 | x is constant 1, so bit 0 is impossible (the old regex read it as ~(0 | x) and found nothing)"),
        (const_value("~instr_is_cheriot_i & x", 1), None, "operand-level: ~0 & x is x, not constant (the old regex read it as ~(0 & x) = constant 1 and could kill a live arm)"),
        (const_value("~instr_is_cheriot_i", 1), 0, "nested negated constant-0 operand: value 0 impossible"),
        (const_value("( ! ((cheriot_enable_i == ibex_pkg::IbexMuBiOn) || (cheriot_enable_i == ibex_pkg::IbexMuBiOff)) )", 0), 0,
         "top-level negation is encoded by the inner value: inner constant 1, bit 0 impossible"),
    ]
    EX_MOD = "ibex_id_stage"
    cases += [
        (ex_const("csr_access_o"), None, "scoping: csr_access_o is constant only inside ibex_cheriot_ex, live in ibex_id_stage"),
        (ex_const("PMPEnable"), None, "scoping: PMPEnable is not a parameter of ibex_id_stage"),
    ]
    EX_MOD = "ibex_cs_registers"
    cases += [
        (ex_const("!PMPEnable || ((BaseIsa == BaseIsaRV32IorCHERIoT) && (cheriot_enable_i == IbexMuBiOn))"), 0,
         "rtl/ibex_cs_registers.sv:707: !1 || (1 && 0) = 0 with the unary negation bound to PMPEnable only"),
        (ex_const("cheriot_csr_addr_i == CHERIOT_SCR_MTCC"), 0, "cs_registers input tied to cheriot_ex's constant csr_addr_o"),
    ]
    EX_MOD = None
    bad = [f"{why}: got {got!r}, want {want!r}" for got, want, why in cases if got != want]
    if bad:
        sys.exit("gen_excl_select self-test FAILED:\n  " + "\n  ".join(bad))


def load_enum_values(pkg_paths):
    """NAME -> integer value for every `typedef enum` literal in the given packages."""
    vals = {}
    for pth in pkg_paths:
        txt = Path(pth).read_text()
        for m in re.finditer(r"typedef\s+enum[^{]*\{(.*?)\}\s*(\w+)\s*;", txt, re.S):
            body = re.sub(r"//[^\n]*", "", m.group(1))
            nxt = 0
            for item in body.split(","):
                item = item.strip()
                if not item:
                    continue
                mm = re.match(r"(\w+)\s*(?:=\s*(\S+))?$", item)
                if not mm:
                    continue
                if mm.group(2):
                    lit = mm.group(2)
                    ml = re.match(r"^(\d+)?'([bhd])([0-9a-fA-F_]+)$", lit)
                    v = int(ml.group(3).replace("_", ""), {"b": 2, "h": 16, "d": 10}[ml.group(2)]) if ml else int(lit)
                else:
                    v = nxt
                vals[mm.group(1)] = v
                nxt = v + 1
    # package parameters / localparams with a literal value (e.g. `parameter logic [4:0] CHERIOT_SCR_MTCC = 5'h1c;`)
    for pth in pkg_paths:
        txt = re.sub(r"//[^\n]*", "", Path(pth).read_text())
        for m in re.finditer(r"^\s*(?:localparam|parameter)\b[^=;]*?\b(\w+)\s*=\s*([0-9]+'[bhd][0-9a-fA-F_]+|\d+)\s*;", txt, re.M):
            lit = m.group(2)
            ml = re.match(r"^(\d+)?'([bhd])([0-9a-fA-F_]+)$", lit)
            vals.setdefault(m.group(1), int(ml.group(3).replace("_", ""), {"b": 2, "h": 16, "d": 10}[ml.group(2)]) if ml else int(lit))
    return vals


ENUMS = load_enum_values(["rtl/ibex_cheriot_pkg.sv", "rtl/ibex_pkg.sv"])
EX_MOD = None   # module whose expression is being classified (set by the callers); scopes the constant tables


def load_module_params(rtl_paths):
    """Module name -> set of its `parameter` names (a bare parameter name is a constant only in its module)."""
    out = {}
    for mod, pth in rtl_paths.items():
        txt = Path(pth).read_text()
        out[mod] = set(re.findall(r"^\s*parameter\s+[^=;\n]*?\b(\w+)\s*=", txt, re.M))
    return out


MODULE_PARAMS = load_module_params(MODULE_RTL)


def load_config():
    """opentitan -pvalue+ integers and +define+ enum names from util/ibex_config.py (never re-typed)."""
    cfg = subprocess.run([sys.executable, "util/ibex_config.py", "opentitan", "vcs_opts"], check=True,
                         capture_output=True, text=True).stdout
    pvals = {m.group(1): int(m.group(2)) for m in re.finditer(r"-pvalue\+(\w+)=(\d+)", cfg)}
    defs = {m.group(1): m.group(2).split("::")[-1] for m in re.finditer(r"\+define\+(\w+)=(\S+)", cfg)}
    return pvals, defs


PVALS, DEFS = load_config()
RE_EQ = re.compile(r"^\(?\s*([\w.]+)\s*(==|!=)\s*([\w:']+)\s*\)?$")


def lit_value(tok):
    tok = tok.split("::")[-1]
    ml = re.match(r"^(\d+)?'([bhd])([0-9a-fA-F_]+)$", tok)
    if ml:
        return int(ml.group(3).replace("_", ""), {"b": 2, "h": 16, "d": 10}[ml.group(2)])
    if tok.isdigit():
        return int(tok)
    return ENUMS.get(tok)


def ex_const(expr, _depth=0):
    """Constant VALUE (0/1) of an ibex_cheriot_ex boolean expression under the tie, or None."""
    o = strip_outer(expr)
    if _depth > 6 or not o:
        return None
    if o in ("1'b1", "1"):
        return 1
    if o in ("1'b0", "0"):
        return 0
    neg = split_neg(o)
    if neg is not None:
        v = ex_const(neg, _depth + 1)
        return None if v is None else 1 - v
    if RE_ON.match(o):
        return 0
    if RE_OFF.match(o) or RE_ISOFF.match(o):
        return 1
    in_ex = (EX_MOD == "ibex_cheriot_ex")
    zero_multi = (CHERIOT_EX_CONST_ZERO_MULTI if in_ex else set()) | MODULE_CONST_ZERO_MULTI.get(EX_MOD, set())
    m = RE_NAME.match(o)
    if m:
        nm = m.group(1)
        base = nm.split(".")[-1]
        if (in_ex and nm in CHERIOT_EX_CONST0_1BIT) or base in CONST0 or nm.startswith(("cheriot_operator_i.", "cheriot_operator_o.")) \
                or re.search(r"_en_cheriot$|cheriot_asr_err", base):
            return 0
        if nm.split(".")[0] in zero_multi and "." in nm:
            return 0      # a field of an all-zero struct
        if nm in PVALS and PVALS[nm] in (0, 1) and nm in MODULE_PARAMS.get(EX_MOD, set()):
            return PVALS[nm]          # elaboration parameter declared by THIS module
        return None
    m = RE_EQ.match(o)
    if m and m.group(1) in DEFS:      # e.g. RV32B == RV32BFull with RV32B = RV32BOTEarlGrey
        eq = 1 if DEFS[m.group(1)] == m.group(3).split("::")[-1] else 0
        return eq if m.group(2) == "==" else 1 - eq
    if m and m.group(1) in PVALS and m.group(1) in MODULE_PARAMS.get(EX_MOD, set()):
        lv = lit_value(m.group(3))
        if lv is not None:
            eq = 1 if PVALS[m.group(1)] == lv else 0
            return eq if m.group(2) == "==" else 1 - eq
    if m and m.group(1).split(".")[0] in zero_multi:
        lv = lit_value(m.group(3))
        if lv is None:
            return None
        eq = 1 if lv == 0 else 0
        return eq if m.group(2) == "==" else 1 - eq
    parts, kinds = split_top_ops(o)
    if len(parts) > 1 and kinds:
        vals = [ex_const(pp, _depth + 1) for pp in parts]
        if all(k in ("&", "&&") for k in kinds):
            if any(v == 0 for v in vals):
                return 0
            if all(v == 1 for v in vals):
                return 1
        if all(k in ("|", "||") for k in kinds):
            if any(v == 1 for v in vals):
                return 1
            if all(v == 0 for v in vals):
                return 0
    return None


RE_HDR_IF = re.compile(r"^\s*(?:end\s+)?(else\s+if|if)\s*\((.*)$")
RE_HDR_ELSE = re.compile(r"^\s*(?:end\s+)?else\s*(begin)?\s*(//.*)?$")
RE_HDR_CASE = re.compile(r"^\s*(?:unique\s+|priority\s+)?case\s*\((.*)\)\s*$")
RE_CASE_ITEM = re.compile(r"^\s*(default|[\w.]+|\([^:]*\))\s*:\s*(begin)?\s*(.*)$")


def strip_comment(l):
    return re.sub(r"//.*$", "", l).rstrip()


def guard_analysis(rtl_path, mod=None):
    global EX_MOD
    EX_MOD = mod
    """Per RTL line: (dead, reason) from the enclosing if/else/case arms, using the file's indentation
    as the nesting (lowRISC style: bodies indented deeper than their header; chains at equal indent).
    Also returns per header line the ordered chain conditions and per case line the item labels."""
    raw = Path(rtl_path).read_text().split("\n")
    n = len(raw)
    lines = [strip_comment(l) for l in raw]
    # join multi-line headers (an `if (` whose parentheses close on a later line)
    hdr_text = {}
    hdr_end = {}
    i = 0
    while i < n:
        l = lines[i]
        if RE_HDR_IF.match(l) or RE_HDR_CASE.match(l) or re.match(r"^\s*(?:unique\s+)?case\s*\(", l):
            txt = l
            j = i
            while txt.count("(") > txt.count(")") and j + 1 < n:
                j += 1
                txt += " " + lines[j].strip()
            hdr_text[i] = txt
            hdr_end[i] = j
        i += 1

    def indent(l):
        return len(l) - len(l.lstrip(" "))

    dead = {}           # line index -> reason
    chains = {}         # header line index -> list of (cond, header_line_index)
    case_items = {}     # case header line index -> list of (label, item_line_index)
    stack = []          # frames: dict(indent, kind, cond, dead, reason, chain(list), case_sel, case_hdr)
    # `stack` holds only frames whose body is still open (by indentation)
    for idx in range(n):
        l = lines[idx]
        if not l.strip():
            continue
        ind = indent(l)
        is_hdr = idx in hdr_text
        txt = hdr_text.get(idx, l)
        m_if = RE_HDR_IF.match(txt) if is_hdr else None
        m_else = RE_HDR_ELSE.match(l)
        m_case = RE_HDR_CASE.match(txt) if is_hdr else None
        # close frames whose body ended: any line at indent <= frame indent closes it, except a
        # continuation of the same chain (else / else if at the same indent) handled below
        while stack and ind <= stack[-1]["indent"] and not (
                (m_if and m_if.group(1) == "else if" or m_else) and ind == stack[-1]["indent"] and stack[-1]["kind"] in ("if", "elseif")):
            stack.pop()
        # case items: a line at case-indent + 2 matching `label:` while a case frame is open
        top = stack[-1] if stack else None
        if top and top["kind"] == "case" and ind == top["indent"] + 2 and not m_if and not m_else and RE_CASE_ITEM.match(l) \
                and not l.strip().startswith("end"):
            mi = RE_CASE_ITEM.match(l)
            label = mi.group(1).strip()
            sel = top["case_sel"]
            if sel in ("1'b1", "1"):
                cval = ex_const(label)
                item_dead = (cval == 0)
                reason = f"case (1'b1) item `{label}` is constant 0" if item_dead else ""
                if label == "default":
                    item_dead = False
            else:
                sel_name = strip_outer(sel).split(".")[0]
                if sel_name in CHERIOT_EX_CONST_ZERO_MULTI:
                    if label == "default":
                        labels_here = [lab for lab, _ in case_items.get(top["hdr"], [])]
                        item_dead = any(lit_value(lab) == 0 for lab in labels_here)
                        reason = f"case ({sel}) selector is constant 0 and a listed item matches 0" if item_dead else ""
                    else:
                        lv = lit_value(label)
                        item_dead = (lv is not None and lv != 0)
                        reason = f"case ({sel}) selector is constant 0, item `{label}` = {lv}" if item_dead else ""
                else:
                    item_dead = False
                    reason = ""
            case_items.setdefault(top["hdr"], []).append((label, idx))
            inherited = top["dead"]
            frame = {"indent": ind, "kind": "caseitem", "cond": label, "dead": inherited or item_dead,
                     "reason": top["reason"] if inherited else reason, "chain": [], "case_sel": None, "hdr": idx}
            stack.append(frame)
            if frame["dead"]:
                dead[idx] = frame["reason"]
            continue
        if m_if or m_else:
            kind = "if" if (m_if and m_if.group(1) == "if") else ("elseif" if m_if else "else")
            cond = m_if.group(2).rsplit(")", 1)[0] if m_if else None
            if m_if:
                # drop the trailing `begin`/`)` remnants: keep the text inside the outermost parens
                inner = txt[txt.index("(") :]
                depth = 0
                for k, ch in enumerate(inner):
                    if ch == "(":
                        depth += 1
                    elif ch == ")":
                        depth -= 1
                        if depth == 0:
                            cond = inner[1:k]
                            break
            prev_chain = []
            if kind in ("elseif", "else") and stack and stack[-1]["indent"] == ind and stack[-1]["kind"] in ("if", "elseif"):
                prev_chain = list(stack[-1]["chain"])
                enclosing_dead, enclosing_reason = stack[-1]["enc_dead"], stack[-1]["enc_reason"]
                stack.pop()
            else:
                enclosing_dead = bool(stack and stack[-1]["dead"])
                enclosing_reason = stack[-1]["reason"] if stack else ""
            chain = prev_chain + ([(cond, idx)] if cond is not None else [])
            # arm dead-ness: own condition constant 0, or an earlier chain condition constant 1
            own_dead = False
            reason = ""
            for c, _hl in prev_chain:
                if ex_const(c) == 1:
                    own_dead = True
                    reason = f"earlier arm `if ({c})` is constant 1"
                    break
            if not own_dead and cond is not None and ex_const(cond) == 0:
                own_dead = True
                reason = f"arm `if ({cond})` requires a constant-0 term"
            frame = {"indent": ind, "kind": kind, "cond": cond, "dead": enclosing_dead or own_dead,
                     "reason": enclosing_reason if enclosing_dead else reason, "chain": chain,
                     "case_sel": None, "hdr": idx, "enc_dead": enclosing_dead, "enc_reason": enclosing_reason}
            stack.append(frame)
            first = chain[0][1] if chain else idx
            chains[first] = chain
            if enclosing_dead:
                for k in range(idx, hdr_end.get(idx, idx) + 1):
                    dead[k] = enclosing_reason
            continue
        if m_case:
            sel = m_case.group(1)
            enclosing_dead = bool(stack and stack[-1]["dead"])
            frame = {"indent": ind, "kind": "case", "cond": sel, "dead": enclosing_dead,
                     "reason": stack[-1]["reason"] if enclosing_dead else "", "chain": [], "case_sel": sel, "hdr": idx}
            stack.append(frame)
            case_items.setdefault(idx, [])
            if frame["dead"]:
                dead[idx] = frame["reason"]
            continue
        # ordinary line: dead if any open frame is dead
        if stack and stack[-1]["dead"]:
            dead[idx] = stack[-1]["reason"]
    # dead is 0-based; return 1-based line numbers
    return ({k + 1: v for k, v in dead.items()},
            {k + 1: [(c, h + 1) for c, h in v] for k, v in chains.items()},
            {k + 1: [(lab, i + 1) for lab, i in v] for k, v in case_items.items()})


def cheriot_ex_branch_dead_vectors(e, dead, chains, case_items):
    """Vectors of a Branch object of ibex_cheriot_ex whose arm is dead: (vector line, reason)."""
    out = []
    if e.line in dead:
        return [(v, dead[e.line]) for v in e.vectors]
    sig = e.header.split('"')[3] if e.header.count('"') >= 4 else ""
    for v in e.vectors:
        m = re.search(r'\((\d+)\) "(.*)"$', v)
        if not m:
            continue
        vs = m.group(2)
        rest = vs[len(sig):].strip() if vs.startswith(sig) else vs.split(" ", 1)[-1]
        toks = [t.strip() for t in rest.split(",")]
        if e.line in case_items and case_items[e.line]:
            label = toks[0]
            if label.startswith("CASEITEM-"):
                label = label.split(":", 1)[1].strip()
            hit = [(lab, il) for lab, il in case_items[e.line] if strip_outer(lab) == strip_outer(label) or lab == label]
            if hit and hit[0][1] in dead:
                out.append((v, dead[hit[0][1]]))
            continue
        chain = chains.get(e.line)
        if chain:
            if all(t in ("0", "-") for t in toks):          # else arm
                body = None
                for k in range(chain[-1][1] + 1, chain[-1][1] + 40):
                    pass
                for c, _h in chain:
                    if ex_const(c) == 1:
                        out.append((v, f"else arm of a chain whose `if ({c})` is constant 1"))
                        break
                continue
            arm = next((i for i, t in enumerate(toks) if t == "1"), None)
            if arm is not None and arm < len(chain):
                c = chain[arm][0]
                if ex_const(c) == 0:
                    out.append((v, f"arm `if ({c})` requires a constant-0 term ({CHERIOT_EX_EVIDENCE})"))
                elif any(ex_const(cc) == 1 for cc, _ in chain[:arm]):
                    out.append((v, "arm behind a constant-1 earlier condition"))
    return out



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--attempts", action="append", default=[], help="URG attempts.log of a strict load; listed objects are refuted and dropped")
    ap.add_argument("--allow-unfilled-ec3", action="store_true",
                    help="emit the three class-D spare-encoding default arms although their EC-3 attempts/failures are not filled (F-3 open)")
    ap.add_argument("--ec3-asserts", help="URG asserts.txt of a MEASURED regression (<outdir>/cov/report/asserts.txt): fills the "
                    "EC-3 fields of the class-D spare-encoding groups from its ATTEMPTS / FAILURES columns and emits them (F-3)")
    ap.add_argument("--ec3-round", default="<round>", help="round tag written into the filled EC-3 fields (e.g. round_1)")
    ap.add_argument("--readme", help="README whose COUNTS block (between <!-- COUNTS-BEGIN --> and <!-- COUNTS-END -->) is rewritten from this run")
    a = ap.parse_args()
    self_test()
    # EC-3 fill (F-3): the guarding assertion of each class-D spare-encoding arm must show attempts > 0 and
    # failures == 0 in the measured regression; read from URG's asserts.txt detail rows
    # (columns: ASSERTIONS CATEGORY SEVERITY ATTEMPTS REAL SUCCESSES FAILURES INCOMPLETE).
    EC3_GUARDS = ("IbexCtrlStateValid", "IbexLsuStateValid", "IbexMultDivStateValid")
    ec3 = {}
    ec3_rel = None
    if a.ec3_asserts:
        ap_ = Path(a.ec3_asserts).resolve()
        root = Path.cwd().resolve()
        try:
            ec3_rel = str(ap_.relative_to(root))
        except ValueError:
            sys.exit(f"gen_excl_select: EC-3 fill refused: {a.ec3_asserts} is outside the clone")
        if not re.match(r"^dv/auto_dv/evidence/gen_round_[^/]+/asserts\.txt$", ec3_rel):
            sys.exit(f"gen_excl_select: EC-3 fill refused: {ec3_rel} is not dv/auto_dv/evidence/gen_round_<n>/asserts.txt")
        man = ap_.parent / "regress_manifest.yaml"
        try:
            import yaml
            cov = (yaml.safe_load(man.read_text()) or {}).get("coverage") or {}
        except Exception as exc:
            sys.exit(f"gen_excl_select: EC-3 fill refused: cannot read {man}: {exc}")
        if not cov.get("dashboard_txt"):
            sys.exit(f"gen_excl_select: EC-3 fill refused: {man} has no measured merge (coverage.dashboard_txt empty)")
        for raw in ap_.read_text(errors="replace").splitlines():
            m = re.match(r"^(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", raw)
            if m and m.group(1).split(".")[-1] in EC3_GUARDS:
                ec3[m.group(1).split(".")[-1]] = {"attempts": int(m.group(4)), "successes": int(m.group(5)), "failures": int(m.group(6))}
        missing = [g for g in EC3_GUARDS if g not in ec3]
        bad = [g for g, v in ec3.items() if v["attempts"] == 0 or v["failures"] != 0]
        if missing or bad:
            sys.exit(f"gen_excl_select: EC-3 fill refused: missing {missing}; attempts 0 or failures != 0 for {bad} (from {a.ec3_asserts})")
        a.allow_unfilled_ec3 = True   # the fields are filled below; the groups may be emitted
    refuted = set()          # (module, exact entry line)
    refuted_heads = set()    # (module, "Kind id") for bare-header (whole object) attempts
    for att in a.attempts:
        amod = None
        for raw in Path(att).read_text().splitlines():
            if raw.startswith("MODULE:"):
                amod = raw.split()[1]; continue
            if not raw or raw.startswith("//") or amod is None:
                continue
            t = raw.strip()
            refuted.add((amod, t))
            q = t.split('"')
            if len(q) == 5 and " (" not in q[4]:          # header only: Kind id "checksum" "signature"
                refuted_heads.add((amod, " ".join(q[0].split()[:2])))
    entries = parse(a.dump)
    report = [f"# gen_excl_select report", f"dump: {a.dump}", f"parsed entries: {len(entries)}", ""]
    groups = {}   # (mod, metric) -> [(ann, [lines])]
    chks = {}

    def add(e, ann, lines):
        key = (e.mod, e.metric)
        chks[key] = e.chk
        groups.setdefault(key, []).append((ann, lines))

    # class P values come from the configuration, never re-typed
    pvals, defs = PVALS, DEFS
    cfg_ok = pvals.get("BranchPredictor") == 0 and pvals.get("BranchTargetALU") == 1 and defs.get("RV32B", "") == "RV32BOTEarlGrey"
    if not cfg_ok:
        sys.exit(f"gen_excl_select: opentitan configuration differs from the class-P assumptions: {pvals.get('BranchPredictor')=} {pvals.get('BranchTargetALU')=} RV32B={defs.get('RV32B')}")
    report.append(f"config check: BranchPredictor={pvals['BranchPredictor']} BranchTargetALU={pvals['BranchTargetALU']} RV32B={defs['RV32B']} (util/ibex_config.py opentitan vcs_opts)")
    # Guard analysis of every shared module that has Block ranges: a Block is selected only when it is
    # inside an approved range AND under a dead guard (or the range is an explicit enum-default entry).
    dead_by_mod = {}
    for mod, rtl in MODULE_RTL.items():
        d, _c, _ci = guard_analysis(rtl, mod)
        dead_by_mod[mod] = d
        report.append(f"guard analysis {mod}: {len(d)} dead RTL lines")
    # Blocks
    for mod, ranges, ann in BLOCKS:
        if "TO BE FILLED" in ann and not a.allow_unfilled_ec3:
            report.append(f"BLOCK {mod} {ranges}: class-D spare-encoding group HELD OUT (EC-3 not filled; --allow-unfilled-ec3 to emit)")
            continue
        explicit_ranges = [r for r in ranges if (mod, tuple(r)) in EXPLICIT_BLOCK_RANGES]
        explicit = bool(explicit_ranges)
        cand = [e for e in entries if e.metric == "line" and e.mod == mod and in_ranges(e.line, ranges) and not RE_STMT_HDR.match(e.header)]
        hits, live, carved = [], [], []
        for e in cand:
            if carved_back(mod, e.header, e.line):
                carved.append(e); continue
            if in_ranges(e.line, explicit_ranges) or e.line in dead_by_mod.get(mod, {}):
                hits.append(e)
            else:
                live.append(e)
        report.append(f"BLOCK {mod} {ranges}: {len(hits)} blocks selected" + (" (explicit enum-default entry)" if explicit else " (dead guard)")
                      + f"; {len(live)} in-range blocks kept in coverage (no dead guard); {len(carved)} A.8 carve-backs kept in coverage"
                      + ("".join(f"\n    live: :{e.line} {e.header[:80]}" for e in live) if live else "")
                      + ("".join(f"\n    carve-back: :{e.line} {e.header[:80]}" for e in carved) if carved else ""))
        if "TO BE FILLED" in ann and ec3:
            g = next(g for g in ("IbexCtrlStateValid", "IbexLsuStateValid", "IbexMultDivStateValid") if g in ann)
            ann = ann.replace("attempts N, failures 0 in <first measured regression>, TO BE FILLED",
                              f"attempts {ec3[g]['attempts']}, failures {ec3[g]['failures']} in {a.ec3_round} ({ec3_rel})")
        for e in hits:
            add(e, ann, [e.header])
    # Branch vectors
    for mod, ranges, vec_re, ann in BRANCHES:
        n = 0
        if "TO BE FILLED" in ann and not a.allow_unfilled_ec3:
            report.append(f"BRANCH {mod} {ranges}: class-D spare-encoding group HELD OUT (EC-3 not filled)")
            continue
        for e in entries:
            if e.metric == "branch" and e.mod == mod and in_ranges(e.line, ranges):
                cond = e.header.split('"')[3] if e.header.count('"') >= 4 else ""
                global EX_MOD
                EX_MOD = mod
                cv = ex_const(cond)
                want = 0 if vec_re == TRUE_ARM else (1 if vec_re == FALSE_ARM else None)
                if want is not None and cv != want:
                    report.append(f"BRANCH {mod} :{e.line} skipped: select `{cond[:70]}` is not constant {want} by the guard predicate (value {cv})")
                    continue
                sel = [v for v in e.vectors if re.search(vec_re, v) and not carved_back(mod, v, e.line)]
                if sel:
                    add(e, ann, sel); n += len(sel)   # vectors only: a bare header would exclude every arm
        report.append(f"BRANCH {mod} {ranges} /{vec_re}/: {n} vectors")
    # ibex_cheriot_ex (A.1, revised): dead arms only. Blocks and branch vectors under a provably dead
    # guard; conditions: on dead lines every vector, elsewhere the impossible-value vectors (A.4 rule
    # with the module's constant table). Reachable-but-masked logic stays in coverage.
    global EX_MODE
    dead, chains, case_items = guard_analysis("rtl/ibex_cheriot_ex.sv", "ibex_cheriot_ex")
    report.append(f"CHERIOT_EX guard analysis: {len(dead)} dead RTL lines in rtl/ibex_cheriot_ex.sv (reasons in the per-group annotations)")
    n_b = n_v = 0
    EX_MOD = "ibex_cheriot_ex"
    for e in entries:
        if e.mod != "ibex_cheriot_ex":
            continue
        if e.metric == "line" and e.line in dead:
            add(e, ann_ex(dead[e.line], e.line), [e.header]); n_b += 1
        elif e.metric == "branch":
            for v, why in cheriot_ex_branch_dead_vectors(e, dead, chains, case_items):
                add(e, ann_ex(why, e.line), [v]); n_v += 1
    report.append(f"CHERIOT_EX dead-arm blocks {n_b}, dead-arm branch vectors {n_v}")
    # Conditions (A.4 generic + A.1)
    for e, sel, tag in select_conditions(entries, dead, report):
        terms = getattr(e, "terms", "")
        if tag == "A1":
            ann = ann_ex(dead[e.line], e.line)
        elif e.mod == "ibex_cheriot_ex":
            ann = ann_ex(f"condition vector with a constant operand at its impossible value: {terms}", e.line)
        else:
            ann = ann_T(f"A.4 condition vectors with a constant-tie operand at its impossible value ({Path(e.file).name if e.file else '?'}:{e.line}): {terms}", "T022_* (gen_unreachability_evidence.md 4.1 table)")
        add(e, ann, sel)
    # Toggles
    for mod, names in TOGGLES.items():
        hits = []
        for e in entries:
            if e.metric != "tgl" or e.mod != mod:
                continue
            nm = e.header.split()[1].split(".")[0]
            if mod == "ibex_cheriot_ex":
                if nm in CHERIOT_EX_LIVE_PORTS:
                    continue
                if nm in names or RE_TGL_GENERIC.match(nm):
                    hits.append(e)
            elif names is None:
                if RE_TGL_GENERIC.match(nm):
                    hits.append(e)
            elif nm in names:
                hits.append(e)
        report.append(f"TOGGLE {mod}: {len(hits)} ports" + ("" if names is None or mod == "ibex_cheriot_ex" else f" (spec {len(names)}; missing: {sorted(set(names) - {h.header.split()[1].split('.')[0] for h in hits})})"))
        for e in hits:
            add(e, TGL_ANN, [e.header])
    # FSMs
    for mod, fsm, states, tr_re, ann in FSMS:
        for e in entries:
            if e.metric == "fsm" and e.mod == mod and e.header.split()[1] == fsm:
                sel = [v for v in e.vectors if (v.startswith("State ") and v.split()[1] in states) or (v.startswith("Transition ") and re.search(tr_re, v.split()[1]))]
                add(e, ann, [e.header] + sel)
                report.append(f"FSM {mod}.{fsm}: {len(sel)} states+transitions")
    # Asserts
    for mod, names, ann in ASSERTS:
        hits = [e for e in entries if e.metric == "assert" and e.mod == mod and e.header.split()[1].split(".")[-1] in names]
        report.append(f"ASSERT {mod}: {len(hits)} of {len(names)} found: {[h.header.split()[1] for h in hits]}")
        for e in hits:
            add(e, ann, [e.header])

    # Emit
    order = {m: i for i, m in enumerate(METRICS)}
    lines = ["// gen_exclusions.el -- URG exclusion file for the ibex auto-DV DUT (gen_dut_top: u_dut.u_ibex_core + u_dut.u_register_file).",
             "// GENERATED by dv/auto_dv/excl/gen_excl_select.py from a `urg -dump full_exclusions` module dump; do not edit by hand.",
             "// Content = gen_exclusions_draft.md v2 (Parts A, C, C.2); README: dv/auto_dv/excl/gen_exclusions_README.md.",
             "// Load: urg ... -elfile gen_exclusions.el -excl_strict (a rejected entry is a finding, never a reason to drop the flag).",
             (f"// Class-D spare-encoding default arms (ctrl_fsm, ls_fsm, md_state): INCLUDED, EC-3 fields filled from {ec3_rel} ({a.ec3_round})."
              if a.ec3_asserts else
              "// Class-D spare-encoding default arms (ctrl_fsm, ls_fsm, md_state): INCLUDED with unfilled EC-3 fields (--allow-unfilled-ec3)."
              if a.allow_unfilled_ec3 else
              "// Class-D spare-encoding default arms (ctrl_fsm, ls_fsm, md_state): HELD OUT until the first measured regression fills their EC-3 fields (Critic F-3)."), ""]
    total = 0
    dropped = []
    carve_hits = []
    for (mod, metric) in sorted(groups, key=lambda k: (k[0], order[k[1]])):
        scope = [f'CHECKSUM: "{chks[(mod, metric)]}"', f"MODULE: {mod}"]
        byann = {}
        for ann, ls in groups[(mod, metric)]:
            byann.setdefault(ann, []).extend(ls)
        for ann, ls in byann.items():
            def is_refuted(l):
                t = l.strip()
                if (mod, t) in refuted:
                    return True
                head = " ".join(t.split('"')[0].split()[:2])   # e.g. `Branch 33` / `Condition 40`
                return (mod, head) in refuted_heads
            keep = [l for l in ls if not is_refuted(l) and not carved_back(mod, l, None)]
            dropped.extend(f"{mod}: {l}" for l in ls if is_refuted(l))
            carve_hits.extend(f"{mod}: {l}" for l in ls if carved_back(mod, l, None) and not is_refuted(l))
            if not keep:
                continue
            scope.append(f'ANNOTATION_BEGIN: "{ann}"')
            scope.extend(keep)
            scope.append("ANNOTATION_END")
            total += len(keep)
        if len(scope) > 2:          # never emit an empty scope
            lines.extend(scope + [""])
    Path(a.out).write_text("\n".join(lines) + "\n")
    report.append("")
    report.append(f"Emitted {total} entry lines in {len(groups)} (module, metric) scopes to {a.out}")
    if dropped:
        report.append(f"Dropped {len(dropped)} entries refuted by a strict load (covered in the reference vdb; kept in coverage):")
        report.extend("  - " + d[:200] for d in dropped)
    report.append(f"A.8 carve-back filter removed {len(carve_hits)} emitted lines" + (":" if carve_hits else " (none reached the emit stage)"))
    report.extend("  - " + d[:200] for d in carve_hits)
    Path(a.report).write_text("\n".join(report) + "\n")
    if a.readme:
        import hashlib
        kinds = {}
        for l in lines:
            k = l.split(" ")[0]
            if k in ("Block", "Branch", "Condition", "Toggle", "Fsm", "State", "Transition", "Assert"):
                kinds[k] = kinds.get(k, 0) + 1
        n_live = sum(r.count("\n    live:") for r in report)
        n_carve = sum(r.count("\n    carve-back:") for r in report)
        md5 = hashlib.md5(Path(a.out).read_bytes()).hexdigest()
        block = ["<!-- COUNTS-BEGIN -->",
                 f"Generated by gen_excl_select.py from the run that produced this file (md5 {md5}); do not edit by hand.",
                 "", "| Quantity | Value |", "|---|---|",
                 f"| entry lines | {total} ({', '.join(f'{v} {k}' for k, v in sorted(kinds.items()))}) |",
                 f"| (module, metric) scopes / annotation groups | {len(groups)} / {sum(1 for l in lines if l.startswith('ANNOTATION_BEGIN'))} |",
                 f"| in-range shared-module blocks kept in coverage (no dead guard) | {n_live} |",
                 f"| in-range blocks kept in coverage by the A.8 carve-back table | {n_carve} |",
                 f"| entries refuted by the strict-load attempts logs and dropped | {len(dropped)} |",
                 f"| emitted lines removed by the carve-back filter | {len(carve_hits)} |",
                 "<!-- COUNTS-END -->"]
        rd = Path(a.readme).read_text()
        rd = re.sub(r"<!-- COUNTS-BEGIN -->.*?<!-- COUNTS-END -->", "\n".join(block), rd, flags=re.S)
        Path(a.readme).write_text(rd)
        report.append(f"README counts block rewritten in {a.readme}")
    print("\n".join(report))


if __name__ == "__main__":
    main()
