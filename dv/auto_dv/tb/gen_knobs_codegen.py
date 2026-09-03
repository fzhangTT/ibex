#!/usr/bin/env python3
"""Render dv/auto_dv/tb/gen_tb_knobs.yaml (the single constants source, architecture C11) into:
  - the GEN_KNOBS_BEGIN/END region of dv/auto_dv/tb/gen_tb_pkg.sv (plusarg names, knob value
    sets, TB constants, memory map) -- the file Runtime's testlist loader and the smoke driver read;
  - dv/auto_dv/gen_tb/gen_knobs.py (the Python mirror for cocotb tests and gen_program.py);
  - dv/auto_dv/isa/gen_isa_shim_map.h (memory map, ISA string and constants for the Spike shim).
`--check` renders in memory and fails (exit 1) when any target differs. Output is deterministic
(no timestamps). Run from anywhere; paths are clone-root relative internally."""
import argparse
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent            # dv/auto_dv/tb
ROOT = HERE.parents[2]
SRC = HERE / "gen_tb_knobs.yaml"
PKG = HERE / "gen_tb_pkg.sv"
WRAPPER = HERE / "gen_dut_top.sv"
LD = ROOT / "dv/auto_dv/stim/gen_riscv_dv_target/gen_link.ld"
PY_OUT = ROOT / "dv/auto_dv/gen_tb/gen_knobs.py"
H_OUT = ROOT / "dv/auto_dv/isa/gen_isa_shim_map.h"
BEGIN = "  // GEN_KNOBS_BEGIN"
END = "  // GEN_KNOBS_END"
KINDS = {"string", "int", "hex", "bool", "enum"}


def die(msg):
    sys.exit(f"gen_knobs_codegen: {msg}")


def sv_param(path, name):
    m = re.search(rf"\b{name}\b\s*=\s*32'h([0-9a-fA-F_]+)", path.read_text())
    if not m:
        die(f"parameter {name} not found in {path}")
    return int(m.group(1).replace("_", ""), 16)


def ld_prog_length(path):
    m = re.search(r"^\s*PROG\s*\(\w+\)\s*:\s*ORIGIN\s*=\s*0x([0-9A-Fa-f]+)\s*,\s*LENGTH\s*=\s*0x([0-9A-Fa-f]+)",
                  path.read_text(), re.M)
    if not m:
        die(f"PROG region not found in {path}")
    return int(m.group(1), 16), int(m.group(2), 16)


def load():
    src = yaml.safe_load(SRC.read_text())
    if src.get("schema_version") != 1:
        die("unsupported schema_version")
    names = [p["name"] for p in src["plusargs"]]
    if len(names) != len(set(names)):
        die("duplicate plusarg names: " + ", ".join(sorted({n for n in names if names.count(n) > 1})))
    for p in src["plusargs"]:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", p["name"]):
            die(f"bad plusarg name {p['name']}")
        if p["kind"] not in KINDS:
            die(f"bad kind for {p['name']}")
        if p["kind"] == "enum":
            vals = [str(v) for v in p["values"]]
            if len(vals) < 2 or len(vals) != len(set(vals)):
                die(f"enum {p['name']} needs >= 2 distinct values")
            if str(p["default"]) not in vals:
                die(f"enum {p['name']} default not in values")
            p["values"] = vals
            p["default"] = str(p["default"])
    return src


def memory_map(src):
    mm = src["memory_map"]
    boot = int(mm["boot_addr_default"])
    prog_origin, prog_len = ld_prog_length(LD)
    boot_page = boot & 0xFFFFFF00
    if prog_origin != (boot_page | 0x80):
        die(f"gen_link.ld PROG origin 0x{prog_origin:08x} != first fetch 0x{boot_page | 0x80:08x}")
    dm_base = sv_param(WRAPPER, "DmBaseAddr")
    dm_mask = sv_param(WRAPPER, "DmAddrMask")
    dm_halt = sv_param(WRAPPER, "DmHaltAddr")
    dm_exc = sv_param(WRAPPER, "DmExceptionAddr")
    out = {"boot_addr_default": boot, "boot_page": boot_page, "prog_size": 0x80 + prog_len,
           "dm_base": dm_base, "dm_size": dm_mask + 1, "dm_halt": dm_halt, "dm_exception": dm_exc,
           "dm_budget": dm_base + dm_mask + 1 - dm_halt,
           "mmio_base": int(mm["mmio_base"]), "mmio_size": int(mm["mmio_size"])}
    for k, off in mm["registers"].items():
        if int(off) >= out["mmio_size"]:
            die(f"register {k} outside the MMIO page")
        out[k] = out["mmio_base"] + int(off)
    return out


def sv_default(p):
    d = p.get("default")
    if d is None:
        return "unset"
    if p["kind"] == "hex":
        return f"0x{int(d):x}"
    return str(d)


def render_sv_region(src, mm):
    L = [BEGIN + " (rendered by dv/auto_dv/tb/gen_knobs_codegen.py from gen_tb_knobs.yaml; edit the yaml, not this block)",
         "  // Plusarg names: +gen_<name>=<value>; declared once here, never as string literals elsewhere."]
    for p in src["plusargs"]:
        up = p["name"].upper()
        tag = " [debug-only]" if p.get("debug_only") else ""
        L.append(f'  parameter string PLUSARG_{up} = "gen_{p["name"]}";  // {p["kind"]}, default {sv_default(p)}{tag}: {p["desc"]}')
    L.append("  // Enumerated knob value sets and defaults (DV Lead regime knobs and TB enums).")
    for p in src["plusargs"]:
        if p["kind"] == "enum":
            up = p["name"].upper()
            L.append(f'  parameter string GEN_KNOB_{up}_VALUES = "{",".join(p["values"])}";')
            L.append(f'  parameter string GEN_KNOB_{up}_DEFAULT = "{p["default"]}";')
    L.append("  // TB constants (values predicted by rtl-arch T-051 where noted; bring-up confirms).")
    for c in src["constants"]:
        rhs = c["sv"] if "sv" in c else str(c["value"])
        L.append(f'  parameter {c["sv_type"]} {c["name"]} = {rhs};  // {c["desc"]}')
    L.append("  // TB memory map: DM windows from gen_dut_top.sv, program window from gen_link.ld, MMIO page from the yaml.")
    for k, v in mm.items():
        L.append(f"  parameter logic [31:0] GEN_MM_{k.upper()} = 32'h{v >> 16:04x}_{v & 0xFFFF:04x};")
    b = mm["boot_addr_default"]
    L.append(f"  parameter logic [31:0] GEN_BOOT_ADDR_DEFAULT = 32'h{b >> 16:04x}_{b & 0xFFFF:04x};  // literal twin of GEN_MM_BOOT_ADDR_DEFAULT (regex readers: gen_program.py, gen_smoke_run.sh)")
    L.append(END)
    return "\n".join(L) + "\n"


def render_pkg(src, mm):
    text = PKG.read_text()
    i = text.find(BEGIN); j = text.find(END)
    if i < 0 or j < 0:
        die("gen_tb_pkg.sv lacks the GEN_KNOBS_BEGIN/END markers")
    j = text.index("\n", j) + 1
    return text[:i] + render_sv_region(src, mm) + text[j:]


def render_py(src, mm):
    L = ['"""Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml; do not edit.',
         'Python mirror of gen_tb_pkg.sv: plusarg names and defaults, regime knob value sets, TB constants,',
         'the memory map and the ISA string (one origin, architecture C11)."""', "",
         f'ISA_STRING = "{src["isa_string"]}"', "", "PLUSARGS = {"]
    for p in src["plusargs"]:
        d = p.get("default")
        dflt = "None" if d is None else (repr(d) if p["kind"] in ("string", "enum") else str(int(d)))
        vals = repr(p["values"]) if p["kind"] == "enum" else "None"
        L.append(f'    "{p["name"]}": {{"plusarg": "gen_{p["name"]}", "kind": "{p["kind"]}", "default": {dflt}, '
                 f'"values": {vals}, "debug_only": {bool(p.get("debug_only"))}, "desc": {repr(p["desc"])}}},')
    L.append("}"); L.append("")
    L.append("CONSTANTS = {")
    for c in src["constants"]:
        L.append(f'    "{c["name"]}": {int(c["value"])},')
    L.append("}"); L.append("")
    L.append("MEMORY_MAP = {")
    for k, v in mm.items():
        L.append(f'    "{k}": 0x{v:08x},')
    L.append("}"); L.append("")
    L.append("DEBUG_ONLY = [p[\"plusarg\"] for p in PLUSARGS.values() if p[\"debug_only\"]]")
    L.append("CHECKERS = [n[4:] for n in PLUSARGS if n.startswith(\"chk_\") and n != \"chk_all\"]")
    L.append("")
    L.append("def plusarg(name, value=None):")
    L.append('    """+gen_<name>[=value] as passed on the simv command line."""')
    L.append("    p = PLUSARGS[name]")
    L.append("    return f\"+{p['plusarg']}\" if value is None else f\"+{p['plusarg']}={value}\"")
    return "\n".join(L) + "\n"


def render_h(src, mm):
    L = ["// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml; do not edit.",
         "// Memory map, ISA string and TB constants for the Spike DPI shim (architecture C5.1, C11).",
         "#ifndef GEN_ISA_SHIM_MAP_H", "#define GEN_ISA_SHIM_MAP_H", "",
         f'#define GEN_ISA_STRING "{src["isa_string"]}"', ""]
    for k, v in mm.items():
        L.append(f"#define GEN_MM_{k.upper():<22} 0x{v:08x}u")
    L.append("")
    for c in src["constants"]:
        L.append(f"#define {c['name']:<34} {int(c['value'])}u")
    L += ["", "#endif"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail when any rendered file is stale")
    args = ap.parse_args()
    src = load()
    mm = memory_map(src)
    targets = {PKG: render_pkg(src, mm), PY_OUT: render_py(src, mm), H_OUT: render_h(src, mm)}
    for path, text in targets.items():
        if any(ord(ch) > 127 for ch in text):
            die(f"non-ASCII output for {path}")
    stale = [str(p.relative_to(ROOT)) for p, t in targets.items() if not p.is_file() or p.read_text() != t]
    if args.check:
        if stale:
            print("gen_knobs_codegen --check: STALE " + " ".join(stale))
            return 1
        print("gen_knobs_codegen --check: up to date")
        return 0
    for p, t in targets.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t)
    print("gen_knobs_codegen: rendered " + " ".join(str(p.relative_to(ROOT)) for p in targets)
          + f" ({len(src['plusargs'])} plusargs, {len(src['constants'])} constants, {len(mm)} map entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
