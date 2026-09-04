#!/usr/bin/env python3
"""Unit test for the covergroup renderer (T-205): the rendered include is up to date on the tree, the renderer refuses a
coverpoint whose plan bins and CSV bins differ, a cross bin that does not split into its components, and a cross without a plan
line; --check catches a stale include. Scratch copies live under dv/auto_dv/work/tb-infra/ut_scratch (repo-local). Plain asserts."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CODEGEN = ROOT / "dv/auto_dv/tb/gen_fcov_codegen.py"
CSV = "dv/auto_dv/docs/gen_trace_tp_bin.csv"
PLAN = "dv/auto_dv/docs/gen_fcov_plan.md"
OUT = "dv/auto_dv/env/gen_fcov_groups.svh"
SCRATCH = ROOT / "dv/auto_dv/work/tb-infra/ut_scratch/fcov_codegen"
fails = 0


def check(what, ok, detail=""):
    global fails
    print(f"{'OK  ' if ok else 'FAIL'} {what}" + (f" ({detail})" if detail and not ok else ""))
    if not ok:
        fails += 1


def codegen(*args):
    return subprocess.run([sys.executable, str(CODEGEN), *args], capture_output=True, text=True)


def scratch_tree(name):
    root = SCRATCH / name
    if root.exists():
        shutil.rmtree(root)
    for rel in (CSV, PLAN, OUT):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, root / rel)
    return root


def main():
    r = codegen("--check")
    check("--check passes on the tree", r.returncode == 0, (r.stdout + r.stderr)[-300:])
    text = (ROOT / OUT).read_text()
    check("every rendered covergroup is type-based", text.count("covergroup ") == text.count("option.per_instance = 0;"))
    check("every rendered covergroup drops the automatic cross bins (option.cross_auto_bin_max = 0)", text.count("covergroup ") == text.count("option.cross_auto_bin_max = 0;"))
    check("keyword bin names are escaped identifiers", "bins \\xor = {" in text and "binsof(cp_op.\\xor )" in text)
    check("no auto cross bins: every cross bin is named from the CSV", "bins auto" not in text)
    check("a tuple naming 1-bit values renders the b<v> bins", "bins all0= binsof(cp_mst_mie_w.b0) && binsof(cp_mst_mpie_w.b0) && binsof(cp_mst_mprv_w.b0) && binsof(cp_mst_tw_w.b0);" in text)
    check("a space-separated tuple renders its components", "bins mstatus_csrrw= binsof(cp_csr.mstatus) && binsof(cp_op.csrrw);" in text)
    named = sum(len(re.findall(r"(?<![a-z_])bins \\?\w+ ?=", l)) for l in text.splitlines() if ": coverpoint " in l)
    ignored = sum(l.count("ignore_bins na") for l in text.splitlines() if ": coverpoint " in l)
    check("the rendered coverpoint lines carry one ignore_bins na each and the named bins are counted apart", ignored == text.count(": coverpoint ") and named > ignored)
    root = scratch_tree("nested_brace_value")
    p = root / PLAN; s = p.read_text()
    s2 = s.replace("bins f0{000}, f1{001}", "bins f0{{1'b0, 2'b00}}, f1{001}", 1)
    check("fixture differs (nested-brace value)", s2 != s); p.write_text(s2)
    r = codegen("--check", "--root", str(root))
    check("a coverpoint value with an inner brace pair still parses (the bins are unchanged, the include is up to date)", r.returncode == 0, r.stdout[-300:])
    root = scratch_tree("operand_only_unmarked")
    p = root / PLAN; s = p.read_text()
    s2 = re.sub(r"(- cp_reg3 = [^\n]*?)\s*\[operand-only:[^\]]*\]", r"\1", s, count=1)
    check("fixture differs (operand-only marker removed)", s2 != s); p.write_text(s2)
    r = codegen("--check", "--root", str(root))
    check("refuses a plan coverpoint without CSV rows unless marked operand-only", r.returncode != 0 and "no [operand-only:] marker" in r.stdout, r.stdout[-300:])
    # ---- the plan grammar forms of the round-0 groups (Slice A): each renders the same include
    def same_render(name, before, after, what):
        root = scratch_tree(name)
        p = root / PLAN; s = p.read_text(); s2 = s.replace(before, after, 1)
        check(f"fixture differs ({name})", s2 != s); p.write_text(s2)
        r = codegen("--check", "--root", str(root))
        check(what, r.returncode == 0, r.stdout[-300:])
    same_render("wrapped_bins_line", "cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f3{011}",
                "cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001},\n    f2{010}, f3{011}", "a bins list wrapped over an indented continuation line parses as one bullet")
    same_render("expressionless_coverpoint", "  - cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f3{011}",
                "  - cp_funct3: bins f0{000}, f1{001}, f2{010}, f3{011}", "a coverpoint line without `= <expression>` parses")
    same_render("iff_clause_before_expression", "  - cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f3{011}",
                "  - cp_funct3 iff OP funct7 0000001 = instr[14:12]: bins f0{000}, f1{001}, f2{010}, f3{011}", "a coverpoint line with an `iff` clause before the expression parses")
    same_render("ignore_bins_clause", "cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f3{011}",
                "cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f3{011}; ignore_bins f4{100}: never encoded", "an `; ignore_bins x{..}: reason` clause is not a bin")
    same_render("names_only_cross", "  - cr_funct3_rd_x0 = cp_funct3 x cp_rd_x0: bins auto{all combinations}\n",
                "  - cr_funct3_rd_x0 = cp_funct3 x cp_rd_x0: f0_no, f0_yes, f1_no, f1_yes, f2_no, f2_yes, f3_no, f3_yes\n", "a cross line listing bin names without tuples declares no tuple and renders from the CSV")
    # ---- refusals on scratch copies
    root = scratch_tree("plan_bins_differ")
    p = root / PLAN; s = p.read_text()
    s2 = s.replace("cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f3{011}", "cp_funct3 = instr[14:12], iff OP funct7 0000001: bins f0{000}, f1{001}, f2{010}, f9{011}", 1)
    check("fixture differs (plan bins)", s2 != s); p.write_text(s2)
    r = codegen("--check", "--root", str(root))
    check("refuses a coverpoint whose plan bins differ from the CSV", r.returncode != 0 and "differ from CSV bins" in r.stdout, r.stdout[-300:])
    root = scratch_tree("cross_bin_unsplittable")
    p = root / CSV; s = p.read_text()
    s2 = s.replace("CG-MUL-001,cr_op_rd_x0,mul_no,", "CG-MUL-001,cr_op_rd_x0,mul_maybe,", 1)
    check("fixture differs (cross bin)", s2 != s); p.write_text(s2)
    r = codegen("--check", "--root", str(root))
    check("refuses a cross bin that does not split into its components", r.returncode != 0 and "does not split" in r.stdout, r.stdout[-300:])
    root = scratch_tree("cross_without_plan_line")
    p = root / PLAN; s = p.read_text()
    s2 = s.replace("  - cr_funct3_rd_x0 = cp_funct3 x cp_rd_x0: bins auto{all combinations}\n", "", 1)
    check("fixture differs (cross line)", s2 != s); p.write_text(s2)
    r = codegen("--check", "--root", str(root))
    check("refuses a cross without a plan line", r.returncode != 0 and "no plan cross line" in r.stdout, r.stdout[-300:])
    root = scratch_tree("stale_include")
    p = root / OUT; lines = p.read_text().splitlines(keepends=True)
    idx = next(i for i, ln in enumerate(lines) if re.search(r"bins \S+ = \{\d+\};", ln))
    lines[idx] = re.sub(r"= \{(\d+)\}", lambda m: "= {" + str(int(m.group(1)) + 1) + "}", lines[idx], count=1)
    p.write_text("".join(lines))
    r = codegen("--check", "--root", str(root))
    check("--check catches a stale include", r.returncode == 1 and "STALE" in r.stdout, r.stdout[-300:])
    print(f"GEN_UT_FCOV_CODEGEN {'FAIL' if fails else 'PASS'} ({fails} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
