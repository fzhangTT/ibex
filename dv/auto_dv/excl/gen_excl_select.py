#!/usr/bin/env python3
"""Generate dv/auto_dv/excl/gen_exclusions.el from a URG `-dump full_exclusions` module dump.

The selection below IS gen_exclusions_draft.md v2 (Parts A and C) in executable form: every entry
is taken verbatim (id, checksum, signature) from fullexclude_module.<metric> so -excl_strict can
verify it, and carries the A.0 annotation (class, RTL location, tie chain / parameter, evidence
class and pointer). Nothing outside Parts A/C and the six C.2 default arms is selected (Critic F-7);
the ten A.8 carve-backs and the four class-R arcs are never selected.

Usage: gen_excl_select.py --dump <dir with fullexclude_module.*> --out gen_exclusions.el --report <md>
"""
import argparse, re, sys
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
    return (f"Class P (build-parameter constant, opentitan configuration): {where}. {param} is an elaboration "
            f"constant (dv/auto_dv/work/rtl-arch/gen_param_resolution.md; time-0 config banner). "
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
BLOCKS = [  # (module, [(lo,hi)...], annotation)
    ("ibex_core", [(2223, 2225)], ann_T("rtl/ibex_core.sv:2223-2225 RVFI cap-read arm (resp_is_cap_q)", "T022_LSU_CHERI0", "+define+RVFI builds only.")),
    ("ibex_id_stage", [(901, 908)], ann_T("rtl/ibex_id_stage.sv:901-908 cheriot_lsu_req_dec case item (Part C row 29)", "T022_ID_CHERI0, T022_DEC_CHERI0")),
    ("ibex_decoder", [(314, 323), (339, 352), (402, 407), (447, 453), (474, 482), (793, 876), (883, 891)],
     ann_T("rtl/ibex_decoder.sv CHERIoT arms of JAL/JALR/STORE/LOAD/AUIPC and the OPCODE_CHERI / OPCODE_AUICGP bodies (case items and their illegal arms stay live, A.8)", "T022_DEC_CHERI0")),
    ("ibex_compressed_decoder", [(230, 233), (249, 252), (329, 332), (359, 363), (391, 394), (411, 414), (557, 560), (575, 579), (615, 620), (854, 857)],
     ann_T("rtl/ibex_compressed_decoder.sv the ten (BaseIsa dual && cheriot_enable_i == On) arms (Part C row 36 for :615-620)", "wrapper tie (constant compare)")),
    ("ibex_controller", [(850, 858), (894, 897), (901, 908), (915, 922), (928, 948), (318, 319), (328, 331)],
     ann_T("rtl/ibex_controller.sv CHERIoT exception arms (Part C rows 2-3, 5-10)", "T022_CORE_CHERI0_B, T022_CTRL_CHERI0, T022_CTRL_PRIO0")),
    ("ibex_load_store_unit", [(139, 140), (211, 219), (437, 467), (565, 603), (616, 623), (669, 678)],
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


def const_value(operand, _depth=0):
    """Return the impossible value (0/1) of a constant-tie operand, or None."""
    o = strip_outer(operand)
    if _depth > 3:
        return None
    sel = split_ternary(o)
    if sel is not None:
        # URG encodes a ternary CONDITION by its select; a ternary used as an operand has the value
        # of an arm, which is not the select: only classify at the top level.
        return const_value(sel, _depth + 1) if _depth == 0 else None
    mneg = re.match(r'^[~!]\s*(.+)$', o)
    if mneg:
        inner = const_value(mneg.group(1), _depth + 1)
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
    """A.4 / A.1: vectors in which a constant-tie operand takes its impossible value."""
    out = []
    unclassified = []
    for e in entries:
        if e.metric != "cond":
            continue
        sig = e.header.split('"')[3] if e.header.count('"') >= 4 else ""
        expr = sig.rsplit(" ", 2)[0] if sig else ""
        if e.mod == "ibex_cheriot_ex" and not in_ranges(e.line, live_lines_cheriot_ex):
            out.append((e, list(e.vectors), "A1"))  # every vector; refuted (covered) ones are dropped by --attempts
            continue
        ops = split_top(strip_outer(expr))
        vals = [const_value(expr, 0)] if len(ops) == 1 else [const_value(o, 1) for o in ops]
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
     ann_T("A.7 rtl/ibex_register_file_ff.sv:237-239 ASSERT_IF with antecedent cheriot_enabled == constant 0: vacuous, never covered", "T022_RF_CAP0")),
]

# A.1 ibex_cheriot_ex: everything except the live objects
CHERIOT_EX_LIVE_LINES = [(200, 233), (943, 960), (970, 973), (991, 994)]
CHERIOT_EX_LIVE_PORTS = {"lsu_req_o", "lsu_we_o", "lsu_addr_o", "lsu_wdata_o", "lsu_type_o", "lsu_sign_ext_o", "rv32_addr_incr_req_o", "rv32_addr_last_o",
                         "rv32_lsu_req_i", "rv32_lsu_we_i", "rv32_lsu_type_i", "rv32_lsu_wdata_i", "rv32_lsu_sign_ext_i", "rv32_lsu_addr_i", "rv32_lsu_err",
                         "addr_incr_req_i", "addr_last_i", "csr_rdata_i", "csr_mstatus_mie_i", "csr_mshwm_new_o", "fwd_wdata_i", "fwd_we_i", "fwd_waddr_i",
                         "rf_rdata_a_i", "rf_rdata_b_i", "rf_raddr_a_i", "rf_raddr_b_i", "pc_id_i", "debug_mode_i", "instr_valid_i", "instr_first_cycle_i",
                         "instr_is_compressed_i", "instr_is_rv32lsu_i", "clk_i", "rst_ni", "lsu_req_done_i", "lsu_resp_valid_i", "lsu_load_err_i",
                         "lsu_store_err_i", "rv32_lsu_err_i"}
CHERIOT_EX_ANN = ann_T("A.1 object-list exclusion inside u_ibex_cheriot_ex (gen_cheriot_carveout.md A1, buckets C/D): every object not on the live list (RV32I LSU mux arms :943-960, :970-973, :991-994, fwd merger :200-233 and the live ports stay in coverage)",
                       "T022_DEC_CHERI0 (instr_is_cheriot_o == 0), T022_ID_CHERI0 (cheriot_exec_id_o == 0)")
CHERIOT_EX_ARM_ANN = ann_T("A.1 step 3: CHERIoT arms of the live ternaries :943-960 and :234-235 (instr_is_cheriot_i true arms)", "T022_DEC_CHERI0")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--attempts", action="append", default=[], help="URG attempts.log of a strict load; listed objects are refuted and dropped")
    a = ap.parse_args()
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

    # Blocks
    for mod, ranges, ann in BLOCKS:
        hits = [e for e in entries if e.metric == "line" and e.mod == mod and in_ranges(e.line, ranges) and not RE_STMT_HDR.match(e.header)]
        report.append(f"BLOCK {mod} {ranges}: {len(hits)} blocks")
        for e in hits:
            add(e, ann, [e.header])
    # Branch vectors
    for mod, ranges, vec_re, ann in BRANCHES:
        n = 0
        for e in entries:
            if e.metric == "branch" and e.mod == mod and in_ranges(e.line, ranges):
                sel = [v for v in e.vectors if re.search(vec_re, v)]
                if sel:
                    add(e, ann, sel); n += len(sel)   # vectors only: a bare header would exclude every arm
        report.append(f"BRANCH {mod} {ranges} /{vec_re}/: {n} vectors")
    # ibex_cheriot_ex object list: blocks and branches (conditions handled below)
    n_b = n_v = 0
    for e in entries:
        if e.mod != "ibex_cheriot_ex":
            continue
        if e.metric == "line" and not in_ranges(e.line, CHERIOT_EX_LIVE_LINES) and not RE_STMT_HDR.match(e.header) \
                and not re.match(r'^Block \d+ "\d+" "(;|else)', e.header):
            add(e, CHERIOT_EX_ANN, [e.header]); n_b += 1
        elif e.metric == "branch":
            if not in_ranges(e.line, CHERIOT_EX_LIVE_LINES) and "rst_ni" not in e.header:
                add(e, CHERIOT_EX_ANN, list(e.vectors)); n_v += len(e.vectors)   # every arm; refuted ones dropped by --attempts
            elif in_ranges(e.line, [(943, 960), (234, 235)]) and "instr_is_cheriot_i" in e.header:
                sel = [v for v in e.vectors if re.search(r'instr_is_cheriot_i\)? 1"$', v)]
                if sel:
                    add(e, CHERIOT_EX_ARM_ANN, sel); n_v += len(sel)
    report.append(f"CHERIOT_EX blocks {n_b}, branch vectors {n_v}")
    # Conditions (A.4 generic + A.1)
    for e, sel, tag in select_conditions(entries, CHERIOT_EX_LIVE_LINES, report):
        ann = CHERIOT_EX_ANN if tag == "A1" else ann_T(f"A.4 condition vectors with a constant-tie operand at its impossible value ({Path(e.file).name if e.file else '?'}:{e.line})", "T022_* (gen_unreachability_evidence.md 4.1 table)")
        add(e, ann, [e.header] if sel is None else sel)
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
            add(e, TGL_ANN if mod != "ibex_cheriot_ex" else CHERIOT_EX_ANN, [e.header])
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
             "// Load: urg ... -elfile gen_exclusions.el -excl_strict (a rejected entry is a finding, never a reason to drop the flag).", ""]
    total = 0
    dropped = []
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
            keep = [l for l in ls if not is_refuted(l)]
            dropped.extend(f"{mod}: {l}" for l in ls if is_refuted(l))
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
    Path(a.report).write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
