#!/usr/bin/env python3
"""Render the SystemVerilog covergroups of the fcov plan (T-205): dv/auto_dv/env/gen_fcov_groups.svh.

One origin for the bins: dv/auto_dv/docs/gen_trace_tp_bin.csv (tp_item, covergroup, coverpoint, bin, adopted) lists every bin
a plan covergroup declares, cross bins included and already reduced by the plan's ignore rules; dv/auto_dv/docs/gen_fcov_plan.md
gives the SV name (header `### CG-X-nnn: gen_cg_<name>` -> `gen_<name>_cg`), the bin ORDER of each coverpoint (its `bins a{..}, b{..}`
list) and the component coverpoints of each cross (`cr_x = cp_a x cp_b [x cp_c]`). Each covergroup renders as
`covergroup gen_<name>_cg with function sample(int v_<cp>, ...)`: a coverpoint per plan coverpoint whose bins are the plan's names
on consecutive indices (a `localparam int GEN_FC_<NAME>_<CP>_<BIN>` per bin is rendered for the sampler; -1 = not applicable,
ignored), and a cross per plan cross whose bins are the CSV's cross-bin names, each split into its component bins
(underscore-joined, longest match with backtracking) and rendered as `binsof(...) && binsof(...)`. Only the covergroups in
IMPLEMENTED render (their samplers exist in gen_fcov_pkg.sv); `--check` fails when the rendered file is stale. Refusals: a
coverpoint whose plan bins and CSV bins differ, a cross bin that does not split into its components, a cross without a plan line,
a group without a plan header."""
import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL_CSV = "dv/auto_dv/docs/gen_trace_tp_bin.csv"
REL_PLAN = "dv/auto_dv/docs/gen_fcov_plan.md"
REL_OUT = "dv/auto_dv/env/gen_fcov_groups.svh"
# the covergroups whose samplers exist (gen_fcov_pkg.sv); plan order of implementation (evidence/gen_round0_covergroup_set.md)
IMPLEMENTED = ("CG-MUL-001", "CG-MUL-003", "CG-ISA-002", "CG-BIT-001", "CG-ISA-001", "CG-ISA-003", "CG-BIT-002", "CG-CMP-001", "CG-CMP-006")


def die(msg):
    print("gen_fcov_codegen: " + msg)
    sys.exit(2)


def load_csv(root):
    with open(root / REL_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or set(rows[0].keys()) != {"tp_item", "covergroup", "coverpoint", "bin", "adopted"}:
        die(f"{REL_CSV}: columns must be tp_item,covergroup,coverpoint,bin,adopted")
    bins = {}   # cg id -> cp -> ordered unique bins (CSV order)
    for r in rows:
        cps = bins.setdefault(r["covergroup"], {})
        lst = cps.setdefault(r["coverpoint"], [])
        if r["bin"] not in lst:
            lst.append(r["bin"])
    return bins


def load_plan(root):
    """cg id -> {"sv": name, "cps": {cp: [bins in plan order]}, "crosses": {cr: [component cps]}}."""
    text = (root / REL_PLAN).read_text()
    groups = {}
    cur = None
    for line in text.splitlines():
        h = re.match(r"^### (CG-[A-Z]+-\d{3}): gen_cg_([a-z0-9_]+)\s*$", line)
        if h:
            cur = groups.setdefault(h.group(1), {"sv": f"gen_{h.group(2)}_cg", "cps": {}, "crosses": {}})
            continue
        if line.startswith("### ") or line.startswith("## "):
            cur = None
            continue
        if cur is None:
            continue
        m = re.match(r"^\s+- (cp_[a-z0-9_]+) = .*?: bins (.*)$", line)
        if m:
            names = re.findall(r"([a-z0-9_]+)\{", m.group(2))
            if names:
                cur["cps"][m.group(1)] = names
            continue
        m = re.match(r"^\s+- (cr_[a-z0-9_]+) = ((?:cp_[a-z0-9_]+\s*x\s*)+cp_[a-z0-9_]+)\s*:\s*bins (.*)$", line)
        if m:
            comps = [c.strip() for c in re.split(r"\s+x\s+", m.group(2))]
            # explicit cross bins name the component tuple in braces: `div_intmin_m1{div, int_min, all_ones}`; `auto{...}` names none
            explicit = {}
            for name, inside in re.findall(r"([a-z0-9_]+)\{([^}]*)\}", m.group(3)):
                parts = [x.strip() for x in inside.split(",")]
                if name != "auto" and len(parts) == len(comps) and all(re.fullmatch(r"[a-z0-9_]+", x) for x in parts):
                    explicit[name] = parts
            cur["crosses"][m.group(1)] = {"comps": comps, "explicit": explicit}
    return groups


def split_cross_bin(name, comp_bins):
    """Split an underscore-joined cross-bin name into one bin per component coverpoint (longest match, backtracking)."""
    def rec(rest, k):
        if k == len(comp_bins):
            return [] if rest == "" else None
        for b in sorted(comp_bins[k], key=len, reverse=True):
            if rest == b and k == len(comp_bins) - 1:
                return [b]
            if rest.startswith(b + "_"):
                tail = rec(rest[len(b) + 1:], k + 1)
                if tail is not None:
                    return [b] + tail
        return None
    return rec(name, 0)


# bin names that are SystemVerilog keywords (xor, or, and, ...) render as escaped identifiers: `\\xor ` (the trailing space ends it)
SV_KEYWORDS = frozenset(['accept_on', 'always', 'always_comb', 'always_ff', 'always_latch', 'and', 'assert', 'assign', 'assume', 'automatic', 'before', 'begin', 'bins', 'bit', 'break', 'buf', 'bufif0', 'bufif1', 'byte', 'case', 'casex', 'casez', 'cell', 'chandle', 'checker', 'class', 'clocking', 'cmos', 'config', 'const', 'constraint', 'context', 'continue', 'cover', 'covergroup', 'coverpoint', 'cross', 'deassign', 'default', 'defparam', 'design', 'disable', 'dist', 'do', 'edge', 'else', 'end', 'endcase', 'enum', 'event', 'eventually', 'expect', 'export', 'extends', 'final', 'first_match', 'for', 'force', 'forever', 'fork', 'function', 'generate', 'genvar', 'global', 'highz0', 'highz1', 'if', 'iff', 'ignore_bins', 'illegal_bins', 'implements', 'implies', 'import', 'incdir', 'include', 'initial', 'inout', 'input', 'inside', 'instance', 'int', 'integer', 'interconnect', 'interface', 'intersect', 'join', 'join_any', 'join_none', 'large', 'let', 'liblist', 'library', 'local', 'localparam', 'logic', 'longint', 'matches', 'medium', 'modport', 'module', 'nand', 'negedge', 'nettype', 'new', 'nexttime', 'nmos', 'nor', 'not', 'notif0', 'notif1', 'null', 'option', 'or', 'output', 'package', 'parameter', 'pmos', 'posedge', 'primitive', 'priority', 'program', 'property', 'protected', 'pull0', 'pull1', 'pulldown', 'pullup', 'pure', 'rand', 'randc', 'randomize', 'rcmos', 'real', 'realtime', 'ref', 'reg', 'reject_on', 'release', 'repeat', 'restrict', 'return', 'rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1', 's_always', 's_eventually', 's_nexttime', 's_until', 'scalared', 'sequence', 'shortint', 'shortreal', 'signed', 'small', 'soft', 'solve', 'specify', 'static', 'string', 'strong0', 'strong1', 'struct', 'super', 'supply0', 'supply1', 'sync_accept_on', 'sync_reject_on', 'table', 'tagged', 'task', 'this', 'throughout', 'time', 'tran', 'tranif0', 'tranif1', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'type', 'typedef', 'union', 'unique', 'unsigned', 'until', 'untyped', 'use', 'uwire', 'var', 'vectored', 'virtual', 'void', 'wait', 'wand', 'weak0', 'weak1', 'while', 'wire', 'with', 'within', 'wor', 'xnor', 'xor'])


def sv_bin(name):
    return ("\\" + name + " ") if name in SV_KEYWORDS else name


def sv_ident(s):
    return re.sub(r"[^A-Za-z0-9_]", "_", s)


def render(root):
    csv_bins = load_csv(root)
    plan = load_plan(root)
    L = ["// gen_fcov_groups.svh: the fcov plan's covergroups, rendered by dv/auto_dv/tb/gen_fcov_codegen.py from",
         "// dv/auto_dv/docs/gen_trace_tp_bin.csv (every bin) and dv/auto_dv/docs/gen_fcov_plan.md (names, bin order, cross",
         "// components); do not edit. Included by gen_fcov_pkg.sv; the samplers there fill the sample() arguments with the",
         "// GEN_FC_* indices (-1 = not applicable, ignored)."]
    for cg in IMPLEMENTED:
        if cg not in plan:
            die(f"{cg}: no plan header `### {cg}: gen_cg_<name>` in {REL_PLAN}")
        if cg not in csv_bins:
            die(f"{cg}: no bins in {REL_CSV}")
        g, cb = plan[cg], csv_bins[cg]
        sv = g["sv"]; up = sv[4:-3].upper()   # gen_mul_ops_cg -> MUL_OPS
        # every plan coverpoint renders, in the plan's order (the sample() argument order); an operand-only coverpoint (counted in an
        # adopted group, no CSV rows of its own) takes its bins from the plan line, a cross may still reference it
        cps = list(g["cps"])
        extra = {cp for cp in cb if cp.startswith("cp_")} - set(cps)
        if extra:
            die(f"{cg}: CSV coverpoints without a plan bins line: {sorted(extra)}")
        crs = [cr for cr in cb if cr.startswith("cr_")]
        other = [x for x in cb if not (x.startswith("cp_") or x.startswith("cr_"))]
        if other:
            die(f"{cg}: coverpoint names outside cp_/cr_: {other}")
        order = {}
        for cp in cps:
            if cp in cb and set(g["cps"][cp]) != set(cb[cp]):
                die(f"{cg}.{cp}: plan bins {sorted(set(g['cps'][cp]))} differ from CSV bins {sorted(set(cb[cp]))}")
            order[cp] = g["cps"][cp]
        L.append("")
        L.append(f"  // {cg} ({sv}), {sum(len(order[x]) for x in cps)} coverpoint bins, {sum(len(cb[x]) for x in crs)} cross bins")
        for cp in cps:
            for i, b in enumerate(order[cp]):
                L.append(f"  localparam int GEN_FC_{up}_{cp.upper()}_{sv_ident(b).upper()} = {i};")
        args = ", ".join(f"int v_{cp}" for cp in cps)
        L.append(f"  covergroup {sv} with function sample({args});")
        L.append("    option.per_instance = 0;")
        for cp in cps:
            body = " ".join(f"bins {sv_bin(b)}= {{{i}}};" for i, b in enumerate(order[cp]))
            L.append(f"    {cp}: coverpoint v_{cp} {{ {body} ignore_bins na = {{-1}}; }}")
        for cr in crs:
            if cr not in g["crosses"]:
                die(f"{cg}.{cr}: no plan cross line `- {cr} = cp_a x cp_b`")
            comps = g["crosses"][cr]["comps"]; explicit = g["crosses"][cr]["explicit"]
            for c in comps:
                if c not in order:
                    die(f"{cg}.{cr}: component {c} is not a coverpoint of the group")
            L.append(f"    {cr}: cross {', '.join(comps)} {{")
            for b in cb[cr]:
                parts = explicit.get(b) or split_cross_bin(b, [order[c] for c in comps])
                if parts is None or any(p not in order[c] for c, p in zip(comps, parts)):
                    die(f"{cg}.{cr}.{b}: does not split into bins of {comps}")
                L.append(f"      bins {sv_bin(b)}= " + " && ".join(f"binsof({c}.{sv_bin(p)})" for c, p in zip(comps, parts)) + ";")
            L.append("    }")
        L.append("  endgroup")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail when the rendered include is stale")
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args()
    root = a.root.resolve()
    text = render(root)
    if any(ord(ch) > 127 for ch in text):
        die("non-ASCII output")
    out = root / REL_OUT
    if a.check:
        if not out.is_file() or out.read_text() != text:
            print(f"gen_fcov_codegen --check: STALE {REL_OUT}")
            return 1
        print("gen_fcov_codegen --check: up to date")
        return 0
    out.write_text(text)
    n_cp = sum(len(re.findall(r"bins \\?\w+ ?=", l)) for l in text.splitlines() if ": coverpoint " in l)
    n_cr = sum(1 for l in text.splitlines() if l.strip().startswith("bins "))
    print(f"gen_fcov_codegen: rendered {REL_OUT} ({len(IMPLEMENTED)} covergroups, {n_cp} coverpoint bins, {n_cr} cross bins)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
