#!/usr/bin/env python3
"""Render dv/auto_dv/tb/gen_tb_knobs.yaml (the single constants source, architecture C11) into:
  - the GEN_KNOBS_BEGIN/END region of dv/auto_dv/tb/gen_tb_pkg.sv (plusarg names, knob value
    sets, regime windows, TB constants, memory map, command codes and names);
  - dv/auto_dv/tb/gen_env_cfg_knobs.svh (the gen_env_cfg fields and plusarg parsing);
  - dv/auto_dv/gen_tb/gen_knobs.py (the Python mirror for cocotb tests and gen_program.py);
  - dv/auto_dv/isa/gen_isa_shim_map.h (memory map, ISA string and constants for the Spike shim).
load() refuses any key outside the schema, so a misspelled key fails loud instead of rendering a
wrong default. Derived constants take their Python/C literal from rtl/ibex_pkg.sv and render a
`<NAME>_PY` mirror the TB top checks against the SV expression at time 0. `--check` renders in
memory and fails (exit 1) naming every stale target. `--src` and `--root` point the renderer at
another source / target tree (unit-test fixtures and stale-target mutations). Output is
deterministic (no timestamps) and ASCII."""
import argparse
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent            # dv/auto_dv/tb
ROOT = HERE.parents[2]
SRC = HERE / "gen_tb_knobs.yaml"
WRAPPER = HERE / "gen_dut_top.sv"
IBEX_PKG = ROOT / "rtl/ibex_pkg.sv"
LD = ROOT / "dv/auto_dv/stim/gen_riscv_dv_target/gen_link.ld"
CS_REGS = ROOT / "rtl/ibex_cs_registers.sv"
CONFIGS = ROOT / "ibex_configs.yaml"
AGENTS_PKG = ROOT / "dv/auto_dv/env/gen_agents_pkg.sv"
# SV enums mirrored into the Python module. The declaring package is the authority for the names AND
# the ordinals; the yaml declares no copy, so the two cannot drift.
SV_ENUM_SOURCES = (("gen_irq_hold_e", AGENTS_PKG),)
# rendered targets, clone-root relative (relocated under --root)
REL_PKG = "dv/auto_dv/tb/gen_tb_pkg.sv"
REL_CFG = "dv/auto_dv/tb/gen_env_cfg_knobs.svh"
REL_PY = "dv/auto_dv/gen_tb/gen_knobs.py"
REL_H = "dv/auto_dv/isa/gen_isa_shim_map.h"
REL_RLINE = "dv/auto_dv/env/gen_export_record_line.svh"
REL_ELINE = "dv/auto_dv/env/gen_export_event_lines.svh"
REL_WIT = "dv/auto_dv/env/gen_wit_bins.svh"
BEGIN = "  // GEN_KNOBS_BEGIN"
END = "  // GEN_KNOBS_END"
KINDS = {"string", "int", "hex", "bool", "enum"}
SCHEMA = {
    "top": {"schema_version", "isa_string", "plusargs", "bridge_cmds", "regime_windows", "constants", "memory_map",
            "export_record_fields", "export_counter_fields", "export_events", "export_active_sources", "witness_csv"},
    "export_event": {"source", "event", "fields"},
    "plusarg": {"name", "kind", "default", "default_from", "values", "debug_only", "desc", "regime_set_consumer"},
    "constant": {"name", "value", "derive", "sv", "sv_type", "desc"},
    "memory_map": {"boot_addr_default", "boot_page_mask", "boot_reset_offset", "mmio_base", "mmio_size", "registers"},
    "register": {"offset", "size"},
    "regime_windows": {"gnt_delay", "rvalid_delay", "rate_per_mille", "outstanding_cap", "irq_event_mean", "dbg_event_mean"},
}
# regime window group -> the enum knobs whose value set must equal the group's keys
WINDOW_KNOBS = {
    "gnt_delay": ("knob_imem_gnt_delay", "knob_dmem_gnt_delay"),
    "rvalid_delay": ("knob_imem_rvalid_delay", "knob_dmem_rvalid_delay"),
    "rate_per_mille": ("knob_imem_err_rate", "knob_imem_intg_err_rate", "knob_dmem_err_rate", "knob_dmem_intg_err_rate"),
    "outstanding_cap": ("knob_imem_outstanding_cap",),
    "irq_event_mean": ("knob_irq_regime",),
    "dbg_event_mean": ("knob_debug_req_regime",),
}
RANGE_GROUPS = {"gnt_delay", "rvalid_delay"}      # [lo, hi] windows; the others are scalars
DERIVATIONS = {"ibus_max_outstanding", "irq_fast_w", "irq_fast_mask", "csr_marchid_value", "csr_addr_cpuctrlsts",
               "csr_addr_secureseed", "icram_lines_x_ways", "csr_meix_bit"}
# REGIME_SET consumers a knob may name; the first four are run-time consumers in the SV dispatcher
KNOB_CONSUMERS = {"bus", "irq", "dbg", "scrkey", "none", "program"}
RUNTIME_CONSUMERS = {"bus", "irq", "dbg", "scrkey"}


def die(msg):
    sys.exit(f"gen_knobs_codegen: {msg}")


def sv_param(path, name):
    m = re.search(rf"\b{name}\b\s*=\s*32'h([0-9a-fA-F_]+)", path.read_text())
    if not m:
        die(f"parameter {name} not found in {path}")
    return int(m.group(1).replace("_", ""), 16)


def sv_int_param(path, name):
    m = re.search(rf"parameter\s+int\s+unsigned\s+{name}\s*=\s*(\d+)\s*;", path.read_text())
    if not m:
        die(f"integer parameter {name} not found in {path}")
    return int(m.group(1))


def sv_enum_members(path, typename):
    """Members of a plain `typedef enum {A, B, C} typename;` in declaration order, name -> ordinal.
    Refuses an explicitly valued member rather than guessing what the ordinals became."""
    m = re.search(rf"typedef\s+enum\s*\{{([^}}]*)\}}\s*{typename}\s*;", path.read_text())
    if not m:
        die(f"enum {typename} not found in {path}")
    body = m.group(1)
    # strip comments before splitting: a // or /* */ inside the braces would otherwise become part of a
    # member name, and a wrong NAME renders a mirror that silently never matches what a caller asks for
    body = re.sub(r"/\*.*?\*/", " ", body, flags=re.S)
    body = re.sub(r"//[^\n]*", " ", body)
    out = {}
    for i, raw in enumerate(body.split(",")):
        name = raw.strip()
        if not name:
            die(f"enum {typename} in {path}: empty member")
        if "=" in name:
            die(f"enum {typename} in {path}: member {name!r} carries an explicit value; this mirror only "
                f"renders positional ordinals")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            die(f"enum {typename} in {path}: member {name!r} is not an identifier")
        out[name] = i
    return out


def sv_enum_hex12(path, name):
    """CSR address of an ibex_pkg csr_num_e member (`NAME = 12'hXXX`)."""
    m = re.search(rf"\b{name}\s*=\s*12'h([0-9a-fA-F_]+)", path.read_text())
    if not m:
        die(f"CSR address {name} not found in {path}")
    return int(m.group(1).replace("_", ""), 16)


def sv_marchid_value(path):
    """ibex_pkg CSR_MARCHID_VALUE = {1'b0, 31'dN}."""
    m = re.search(r"CSR_MARCHID_VALUE\s*=\s*\{1'b0,\s*31'd(\d+)\}", path.read_text())
    if not m:
        die(f"CSR_MARCHID_VALUE not found in {path}")
    return int(m.group(1))


def sv_tdata1_rdata(path):
    """Ibex's fixed tdata1 read value: the tmatch_control_rdata concatenation with the one variable (execute) at 0."""
    text = path.read_text()
    m = re.search(r"assign\s+tmatch_control_rdata\s*=\s*\{(.*?)\};", text, re.S)
    if not m:
        die(f"tmatch_control_rdata assign not found in {path}")
    body = re.sub(r"//[^\n]*", "", m.group(1))
    value, width, variables = 0, 0, 0
    for tok in [t.strip() for t in body.split(",") if t.strip()]:
        lit = re.fullmatch(r"(\d+)'([hbd])([0-9a-fA-F_]+)", tok)
        if lit:
            w = int(lit.group(1)); v = int(lit.group(3).replace("_", ""), {"h": 16, "b": 2, "d": 10}[lit.group(2)])
        elif re.fullmatch(r"[A-Za-z_]\w*", tok):
            w, v = 1, 0; variables += 1
        else:
            die(f"tmatch_control_rdata: unexpected token {tok!r}")
        value = (value << w) | v; width += w
    if width != 32 or variables != 1:
        die(f"tmatch_control_rdata: {width} bits and {variables} variables parsed, expected 32 and 1")
    return value


def cfg_int_param(path, config, name):
    """An integer parameter of one build configuration in ibex_configs.yaml, read from the block itself (no configuration
    uses `inherits:` today; a block that did would have to be resolved through util/ibex_config.py instead)."""
    import yaml as _yaml
    cfgs = _yaml.safe_load(path.read_text())
    if config not in cfgs or name not in cfgs[config]:
        die(f"{path}: no {name} in configuration {config}")
    return int(cfgs[config][name])


def sv_irq_fast_width(path):
    m = re.search(r"logic\s*\[\s*(\d+)\s*:\s*0\s*\]\s*irq_fast\s*;", path.read_text())
    if not m:
        die(f"irq_fast width not found in {path}")
    return int(m.group(1)) + 1


def ld_prog_length(path):
    m = re.search(r"^\s*PROG\s*\(\w+\)\s*:\s*ORIGIN\s*=\s*0x([0-9A-Fa-f]+)\s*,\s*LENGTH\s*=\s*0x([0-9A-Fa-f]+)",
                  path.read_text(), re.M)
    if not m:
        die(f"PROG region not found in {path}")
    return int(m.group(1), 16), int(m.group(2), 16)


def check_keys(mapping, allowed, where):
    if not isinstance(mapping, dict):
        die(f"{where}: expected a mapping")
    bad = sorted(k for k in mapping if k not in allowed)
    if bad:
        die(f"{where}: unknown key(s) {', '.join(str(b) for b in bad)} (allowed: {', '.join(sorted(allowed))})")


def load(src_path=SRC):
    src = yaml.safe_load(src_path.read_text())
    check_keys(src, SCHEMA["top"], "top level")
    if src.get("schema_version") != 1:
        die("unsupported schema_version")
    for section in ("isa_string", "plusargs", "bridge_cmds", "regime_windows", "constants", "memory_map",
                    "export_record_fields", "export_counter_fields", "export_events"):
        if section not in src:
            die(f"missing section {section}")
    names = [p.get("name") for p in src["plusargs"]]
    if len(names) != len(set(names)):
        die("duplicate plusarg names: " + ", ".join(sorted({str(n) for n in names if names.count(n) > 1})))
    cmds = src["bridge_cmds"]
    if not isinstance(cmds, list) or len(cmds) < 1 or len(cmds) != len(set(cmds)) \
            or any(not re.fullmatch(r"[A-Z][A-Z0-9_]*", str(k)) for k in cmds):
        die("bridge_cmds must be a non-empty list of unique UPPER_CASE names")
    for p in src["plusargs"]:
        where = f"plusarg {p.get('name', '?')}"
        check_keys(p, SCHEMA["plusarg"], where)
        for req in ("name", "kind", "desc"):
            if req not in p:
                die(f"{where}: missing {req}")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", p["name"]):
            die(f"bad plusarg name {p['name']}")
        if p["kind"] not in KINDS:
            die(f"bad kind for {p['name']}")
        if not isinstance(p["desc"], str):
            die(f"{where}: desc must be a string")
        if ("default" in p) == ("default_from" in p):
            die(f"{where}: exactly one of default / default_from is required")
        if p["kind"] == "enum":
            if "values" not in p:
                die(f"{where}: enum needs values")
            vals = [str(v) for v in p["values"]]
            if len(vals) < 2 or len(vals) != len(set(vals)):
                die(f"enum {p['name']} needs >= 2 distinct values")
            if str(p.get("default")) not in vals:
                die(f"enum {p['name']} default not in values")
            p["values"] = vals
            p["default"] = str(p["default"])
        elif "values" in p:
            die(f"{where}: values only on enum knobs")
    for p in src["plusargs"]:
        if p["kind"] == "enum" and p["name"].startswith("knob_"):
            if p.get("regime_set_consumer") not in KNOB_CONSUMERS:
                die(f"plusarg {p['name']}: regime_set_consumer must be one of {sorted(KNOB_CONSUMERS)}")
        elif "regime_set_consumer" in p:
            die(f"plusarg {p['name']}: regime_set_consumer is for enum knob_* entries only")
    # literals that mirror the RTL or the build configuration are verified at every render (guards, not derivations)
    lits = {c["name"]: c for c in src["constants"] if "value" in c}
    if "GEN_TDATA1_IBEX_RDATA" in lits and int(lits["GEN_TDATA1_IBEX_RDATA"]["value"]) != sv_tdata1_rdata(CS_REGS):
        die(f"GEN_TDATA1_IBEX_RDATA {int(lits['GEN_TDATA1_IBEX_RDATA']['value']):#x} differs from rtl/ibex_cs_registers.sv tmatch_control_rdata {sv_tdata1_rdata(CS_REGS):#x}")
    if "GEN_MHPM_COUNTER_NUM" in lits:
        cfg_name = next((p["default"] for p in src["plusargs"] if p["name"] == "build_config"), None)
        if int(lits["GEN_MHPM_COUNTER_NUM"]["value"]) != cfg_int_param(CONFIGS, cfg_name, "MHPMCounterNum"):
            die(f"GEN_MHPM_COUNTER_NUM {lits['GEN_MHPM_COUNTER_NUM']['value']} differs from ibex_configs.yaml {cfg_name} MHPMCounterNum")
    for c in src["constants"]:
        where = f"constant {c.get('name', '?')}"
        check_keys(c, SCHEMA["constant"], where)
        for req in ("name", "sv_type", "desc"):
            if req not in c:
                die(f"{where}: missing {req}")
        if ("value" in c) == ("derive" in c):
            die(f"{where}: exactly one of value / derive is required")
        if "derive" in c and c["derive"] not in DERIVATIONS:
            die(f"{where}: unknown derivation {c['derive']} (known: {', '.join(sorted(DERIVATIONS))})")
        if "derive" in c and "sv" not in c:
            die(f"{where}: a derived constant needs its sv expression")
    mm = src["memory_map"]
    check_keys(mm, SCHEMA["memory_map"], "memory_map")
    for req in SCHEMA["memory_map"]:
        if req not in mm:
            die(f"memory_map: missing {req}")
    for k, r in mm["registers"].items():
        check_keys(r, SCHEMA["register"], f"memory_map.registers.{k}")
        if "offset" not in r or "size" not in r or not str(k).endswith("_addr"):
            die(f"memory_map.registers.{k}: needs offset and size; the key ends in _addr")
    rw = src["regime_windows"]
    check_keys(rw, SCHEMA["regime_windows"], "regime_windows")
    enums = {p["name"]: p for p in src["plusargs"] if p["kind"] == "enum"}
    for group, knobs in WINDOW_KNOBS.items():
        if group not in rw:
            die(f"regime_windows: missing group {group}")
        keys = [str(k) for k in rw[group]]
        for kn in knobs:
            if kn not in enums:
                die(f"regime_windows.{group}: knob {kn} is not an enum plusarg")
            if sorted(keys) != sorted(enums[kn]["values"]):
                die(f"regime_windows.{group}: keys {keys} differ from the values of {kn} {enums[kn]['values']}")
        for k, v in rw[group].items():
            if group in RANGE_GROUPS:
                if not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, int) for x in v) and 0 <= v[0] <= v[1]):
                    die(f"regime_windows.{group}.{k}: expected [lo, hi] with 0 <= lo <= hi")
            elif not isinstance(v, int) or v < 0:
                die(f"regime_windows.{group}.{k}: expected a non-negative integer")
    for key in ("export_record_fields", "export_counter_fields"):
        names = src[key]
        if not isinstance(names, list) or not names or len(names) != len(set(names)) \
                or any(not re.fullmatch(r"[a-z][a-z0-9_]*", str(n)) for n in names):
            die(f"{key}: expected a non-empty list of unique lower_case names")
    seen = set()
    for row in src["export_events"]:
        check_keys(row, SCHEMA["export_event"], f"export_events row {row.get('source', '?')}/{row.get('event', '?')}")
        for req in ("source", "event", "fields"):
            if req not in row:
                die(f"export_events row: missing {req}")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", row["source"]):
            die(f"export_events: bad source {row['source']}")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", row["event"]):
            die(f"export_events: bad event {row['event']} (one exact lower_case event name per row; no wildcard rows)")
        if (row["source"], row["event"]) in seen:
            die(f"export_events: duplicate row {row['source']}/{row['event']}")
        seen.add((row["source"], row["event"]))
        if not isinstance(row["fields"], list) or not row["fields"] or any(not re.fullmatch(r"[a-z][a-z0-9_]*", str(f)) for f in row["fields"]):
            die(f"export_events {row['source']}/{row['event']}: fields must be a non-empty list of lower_case names")
    if "export_active_sources" not in src:
        die("missing export_active_sources (the sources whose writers are instanced in this build)")
    act = src["export_active_sources"]
    if not isinstance(act, list) or len(set(act)) != len(act) or any(a not in export_sources(src) for a in act):
        die(f"export_active_sources must list distinct sources of export_events, got {act}")
    return src


def export_sources(src):
    out = []
    for row in src["export_events"]:
        if row["source"] not in out:
            out.append(row["source"])
    return out


def event_fn_name(row):
    return f"gen_export_line_{row['source']}_{row['event']}"


def render_record_line(src):
    """Include for gen_rvfi_pkg (after class gen_rvfi_txn): the R line of one record in the rendered field order."""
    fields = src["export_record_fields"]
    L = ["// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml (export_record_fields); do not edit.",
         "// Included inside gen_rvfi_pkg after class gen_rvfi_txn: the export's R line in the header's field order (all hex).",
         "function automatic string gen_export_record_line(gen_rvfi_txn t, bit counters);",
         "  string s;",
         '  s = $sformatf("R ' + " ".join("%0h" for _ in fields) + '", ' + ", ".join(f"t.{f}" for f in fields) + ");"]
    n = len(src["export_counter_fields"]) // 2
    L.append("  if (counters)")
    L.append('    s = {s, $sformatf(" ' + " ".join("%0h" for _ in range(2 * n)) + '", '
             + ", ".join(f"t.ext_mhpmcounters[{i}]" for i in range(n)) + ", "
             + ", ".join(f"t.ext_mhpmcountersh[{i}]" for i in range(n)) + ")};")
    L += ["  return s;", "endfunction", ""]
    return "\n".join(L)


def render_event_lines(src):
    """Include for gen_export_pkg: one line-formatting function per event row; argument names are the field names."""
    L = ["// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml (export_events); do not edit.",
         "// Included inside gen_export_pkg: the E line of one boundary event, `E <cycle> <source> <event> <fields...>` (all hex)."]
    for row in src["export_events"]:
        args = ["int unsigned cycle"] + [f"int unsigned {f}" for f in row["fields"]]
        ev = row["event"]
        vals = ["cycle"] + list(row["fields"])
        L.append(f"function automatic string {event_fn_name(row)}({', '.join(args)});")
        L.append(f'  return $sformatf("E %0h {row["source"]} {ev} ' + " ".join("%0h" for _ in row["fields"]) + '", ' + ", ".join(vals) + ");")
        L.append("endfunction")
    L.append("")
    return "\n".join(L)


def derive_values(src):
    """Python/C literals of the derived constants, from rtl/ibex_pkg.sv and the literal constants."""
    lits = {c["name"]: int(c["value"]) for c in src["constants"] if "value" in c}
    bus_bytes = sv_int_param(IBEX_PKG, "BUS_SIZE") // 8
    line_bytes = sv_int_param(IBEX_PKG, "IC_LINE_SIZE") // 8
    beats = line_bytes // bus_bytes
    fast_w = sv_irq_fast_width(IBEX_PKG)
    out = {}
    for c in src["constants"]:
        if "derive" not in c:
            continue
        d = c["derive"]
        if d == "ibus_max_outstanding":
            if "GEN_ICACHE_NUM_FB" not in lits:
                die("ibus_max_outstanding needs the literal GEN_ICACHE_NUM_FB")
            out[c["name"]] = lits["GEN_ICACHE_NUM_FB"] * beats
        elif d == "icram_lines_x_ways":
            ways = sv_int_param(IBEX_PKG, "IC_NUM_WAYS")
            out[c["name"]] = (sv_int_param(IBEX_PKG, "IC_SIZE_BYTES") // ways // line_bytes) * ways
        elif d == "irq_fast_w":
            out[c["name"]] = fast_w
        elif d == "irq_fast_mask":
            out[c["name"]] = ((1 << fast_w) - 1) << 16
        elif d == "csr_meix_bit":
            out[c["name"]] = sv_int_param(IBEX_PKG, "CSR_MEIX_BIT")
        elif d == "csr_marchid_value":
            out[c["name"]] = sv_marchid_value(IBEX_PKG)
        elif d == "csr_addr_cpuctrlsts":
            out[c["name"]] = sv_enum_hex12(IBEX_PKG, "CSR_CPUCTRLSTS")
        elif d == "csr_addr_secureseed":
            out[c["name"]] = sv_enum_hex12(IBEX_PKG, "CSR_SECURESEED")
    return out


def const_values(src):
    vals = derive_values(src)
    for c in src["constants"]:
        if "value" in c:
            vals[c["name"]] = int(c["value"])
    return vals


def memory_map(src):
    mm = src["memory_map"]
    boot = int(mm["boot_addr_default"])
    mask = int(mm["boot_page_mask"])
    prog_origin, prog_len = ld_prog_length(LD)
    boot_page = boot & mask
    off = int(mm["boot_reset_offset"])
    if prog_origin != (boot_page | off):
        die(f"gen_link.ld PROG origin 0x{prog_origin:08x} != first fetch 0x{boot_page | off:08x}")
    dm_base = sv_param(WRAPPER, "DmBaseAddr")
    dm_mask = sv_param(WRAPPER, "DmAddrMask")
    dm_halt = sv_param(WRAPPER, "DmHaltAddr")
    dm_exc = sv_param(WRAPPER, "DmExceptionAddr")
    out = {"boot_addr_default": boot, "boot_page_mask": mask, "boot_reset_offset": off, "boot_page": boot_page, "prog_size": off + prog_len,
           "dm_base": dm_base, "dm_size": dm_mask + 1, "dm_halt": dm_halt, "dm_exception": dm_exc,
           "dm_budget": dm_base + dm_mask + 1 - dm_halt,
           "mmio_base": int(mm["mmio_base"]), "mmio_size": int(mm["mmio_size"])}
    for k, r in mm["registers"].items():
        off, size = int(r["offset"]), int(r["size"])
        if off + size > out["mmio_size"]:
            die(f"register {k} outside the MMIO page")
        out[k] = out["mmio_base"] + off
        out[k[:-len("_addr")] + "_size"] = size
    return out


def resolve_defaults(src, mm, cvals):
    """Fill `default` of every default_from plusarg from a constant or a memory-map key."""
    for p in src["plusargs"]:
        if "default_from" not in p:
            continue
        ref = p["default_from"]
        if ref.startswith("memory_map."):
            key = ref[len("memory_map."):]
            if key not in mm:
                die(f"plusarg {p['name']}: default_from {ref} is not a memory-map key")
            p["default"] = mm[key]
        elif ref in cvals:
            p["default"] = cvals[ref]
        else:
            die(f"plusarg {p['name']}: default_from {ref} names no constant or memory-map key")
        if p["kind"] not in ("int", "hex"):
            die(f"plusarg {p['name']}: default_from is for int/hex knobs")


def sv_default(p):
    d = p.get("default")
    if d is None:
        return "unset"
    if p["kind"] == "hex":
        return f"0x{int(d):x}"
    return str(d)


def render_sv_region(src, mm, cvals):
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
            L.append(f'  parameter string GEN_ENUM_{up}_VALUES = "{",".join(p["values"])}";')
            L.append(f'  parameter string GEN_ENUM_{up}_DEFAULT = "{p["default"]}";')
    L.append("  // Numeric meaning of the latency/rate/cap regimes (yaml regime_windows); 0 = unknown group or value.")
    L.append("  function automatic bit gen_regime_window(string group, string value, output int unsigned lo, output int unsigned hi);")
    L.append("    lo = 0; hi = 0;")
    for group in sorted(RANGE_GROUPS):
        for k, v in src["regime_windows"][group].items():
            L.append(f'    if (group == "{group}" && value == "{k}") begin lo = {v[0]}; hi = {v[1]}; return 1\'b1; end')
    L.append("    return 1'b0;")
    L.append("  endfunction")
    L.append("  function automatic bit gen_regime_scalar(string group, string value, output int unsigned v);")
    L.append("    v = 0;")
    for group in sorted(SCHEMA["regime_windows"] - RANGE_GROUPS):
        for k, val in src["regime_windows"][group].items():
            L.append(f'    if (group == "{group}" && value == "{k}") begin v = {val}; return 1\'b1; end')
    L.append("    return 1'b0;")
    L.append("  endfunction")
    L.append("  // TB constants (values predicted by rtl-arch T-051 where noted; bring-up confirms). A derived constant")
    L.append("  // keeps its SV expression; its _PY twin is the literal Python and C use (gen_tb_top fatals when they differ).")
    for c in src["constants"]:
        rhs = c["sv"] if "sv" in c else str(c["value"])
        L.append(f'  parameter {c["sv_type"]} {c["name"]} = {rhs};  // {c["desc"]}')
        if "derive" in c:
            L.append(f'  parameter {c["sv_type"]} {c["name"]}_PY = {cvals[c["name"]]};  // rendered from rtl/ibex_pkg.sv ({c["derive"]})')
    L.append("  // TB memory map: DM windows from gen_dut_top.sv, program window from gen_link.ld, MMIO page from the yaml.")
    for k, v in mm.items():
        L.append(f"  parameter logic [31:0] GEN_MM_{k.upper()} = 32'h{v >> 16:04x}_{v & 0xFFFF:04x};")
    L.append("  // Bridge command kinds (C2); 0 is NONE.")
    L.append("  parameter logic [7:0] GEN_CMD_NONE = 8'd0;")
    for i, k in enumerate(src["bridge_cmds"], start=1):
        L.append(f"  parameter logic [7:0] GEN_CMD_{k} = 8'd{i};")
    L.append("  function automatic string gen_cmd_name(logic [7:0] kind);")
    L.append("    case (kind)")
    for i, k in enumerate(src["bridge_cmds"], start=1):
        L.append(f'      8\'d{i}: return "{k}";')
    L.append('      default: return $sformatf("UNKNOWN(%0d)", kind);')
    L.append("    endcase")
    L.append("  endfunction")
    knobs = [p for p in src["plusargs"] if p["kind"] == "enum" and p["name"].startswith("knob_")]
    L.append("  // Regime knob ids and value lookup (bridge command REGIME_SET: arg0 = knob id, arg1 = value index).")
    for i, p in enumerate(knobs):
        L.append(f"  parameter int GEN_KNOB_ID_{p['name'][5:].upper()} = {i};")
    L.append("  function automatic string gen_knob_name(int id);")
    L.append("    case (id)")
    for i, p in enumerate(knobs):
        L.append(f'      {i}: return "{p["name"]}";')
    L.append('      default: return "";')
    L.append("    endcase")
    L.append("  endfunction")
    L.append("  // REGIME_SET consumer per knob (yaml regime_set_consumer): the dispatcher refuses a knob without a run-time consumer.")
    L.append("  function automatic string gen_knob_consumer(int id);")
    L.append("    case (id)")
    for i, p in enumerate(knobs):
        L.append(f'      {i}: return "{p["regime_set_consumer"]}";')
    L.append('      default: return "";')
    L.append("    endcase")
    L.append("  endfunction")
    L.append("  function automatic bit gen_knob_regime_set_consumed(int id);")
    L.append("    case (id)")
    consumed = [i for i, p in enumerate(knobs) if p["regime_set_consumer"] in RUNTIME_CONSUMERS]
    L.append("      " + ", ".join(str(i) for i in consumed) + ": return 1'b1;")
    L.append("      default: return 1'b0;")
    L.append("    endcase")
    L.append("  endfunction")
    L.append("  function automatic string gen_knob_value(int id, int idx);")
    L.append("    case (id)")
    for i, p in enumerate(knobs):
        L.append(f"      {i}: case (idx) " + " ".join(f'{j}: return "{v}";' for j, v in enumerate(p["values"])) + ' default: return ""; endcase')
    L.append('      default: return "";')
    L.append("    endcase")
    L.append("  endfunction")
    L.append("  // Record and event export (architecture Section 9): the header's field lists, the event sources and rows.")
    L.append(f'  parameter string GEN_EXPORT_RECORD_FIELDS = "{",".join(src["export_record_fields"])}";')
    L.append(f'  parameter string GEN_EXPORT_COUNTER_FIELDS = "{",".join(src["export_counter_fields"])}";')
    L.append(f'  parameter string GEN_EXPORT_SOURCES = "{",".join(export_sources(src))}";')
    L.append(f'  parameter string GEN_EXPORT_ACTIVE_SOURCES = "{",".join(src["export_active_sources"])}";  // sources with a writer in this build (yaml export_active_sources)')
    L.append("  function automatic bit gen_export_source_active(string s);")
    L.append("    case (s)")
    L.append("      " + ", ".join(f'"{x}"' for x in src["export_active_sources"]) + ": return 1'b1;")
    L.append("      default: return 1'b0;")
    L.append("    endcase")
    L.append("  endfunction")
    L.append("  function automatic bit gen_export_source_known(string s);")
    L.append("    case (s)")
    L.append("      " + ", ".join(f'"{x}"' for x in export_sources(src)) + ": return 1'b1;")
    L.append("      default: return 1'b0;")
    L.append("    endcase")
    L.append("  endfunction")
    L.append("  // The `# events <source> <event> <fields>` header rows of one source, newline-terminated.")
    L.append("  function automatic string gen_export_event_header(string source);")
    L.append("    case (source)")
    for srcname in export_sources(src):
        rows = "".join(f'# events {r["source"]} {r["event"]} {",".join(r["fields"])}\\n' for r in src["export_events"] if r["source"] == srcname)
        L.append(f'      "{srcname}": return "{rows}";')
    L.append('      default: return "";')
    L.append("    endcase")
    L.append("  endfunction")
    rows_csv = ",".join(r["source"] + "/" + r["event"] for r in src["export_events"])
    L.append('  parameter string GEN_EXPORT_ROWS = "' + rows_csv + '";  // every (source, event) row, yaml order')
    L.append("  // The `# events <source> <event> <fields>` header row of ONE (source, event), newline-terminated; empty when unknown.")
    L.append("  function automatic string gen_export_row_header(string source, string ev);")
    L.append('    case ({source, "/", ev})')
    for r in src["export_events"]:
        key = r["source"] + "/" + r["event"]
        hdr = "# events " + r["source"] + " " + r["event"] + " " + ",".join(r["fields"]) + "\\n"
        L.append('      "' + key + '": return "' + hdr + '";')
    L.append('      default: return "";')
    L.append("    endcase")
    L.append("  endfunction")
    L.append("  // Every legal +gen_* plusarg name; gen_base_test fatals on any other +gen_* argument (A-23).")
    L.append("  function automatic bit gen_is_known_plusarg(string name);")
    L.append("    case (name)")
    L.append("      " + ", ".join(f'"gen_{p["name"]}"' for p in src["plusargs"]) + ": return 1'b1;")
    L.append("      default: return 1'b0;")
    L.append("    endcase")
    L.append("  endfunction")
    L.append("  // A bool knob needs an explicit =0/=1 (a bare +gen_<bool> would otherwise be a silent no-op).")
    L.append("  function automatic bit gen_is_bool_plusarg(string name);")
    L.append("    case (name)")
    L.append("      " + ", ".join(f'"gen_{p["name"]}"' for p in src["plusargs"] if p["kind"] == "bool") + ": return 1'b1;")
    L.append("      default: return 1'b0;")
    L.append("    endcase")
    L.append("  endfunction")
    b = mm["boot_addr_default"]
    L.append(f"  parameter logic [31:0] GEN_BOOT_ADDR_DEFAULT = 32'h{b >> 16:04x}_{b & 0xFFFF:04x};  // literal twin of GEN_MM_BOOT_ADDR_DEFAULT (regex readers: gen_program.py, gen_smoke_run.sh)")
    L.append(END)
    return "\n".join(L) + "\n"


def render_pkg(src, mm, cvals, pkg_path):
    text = pkg_path.read_text()
    i = text.find(BEGIN); j = text.find(END)
    if i < 0 or j < 0:
        die(f"{pkg_path} lacks the GEN_KNOBS_BEGIN/END markers")
    j = text.index("\n", j) + 1
    return text[:i] + render_sv_region(src, mm, cvals) + text[j:]


def render_py(src, mm, cvals):
    L = ['"""Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml; do not edit.',
         'Python mirror of gen_tb_pkg.sv: plusarg names and defaults, regime knob value sets and windows, TB',
         'constants, the memory map and the ISA string (one origin, architecture C11)."""', "",
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
        L.append(f'    "{c["name"]}": {cvals[c["name"]]},')
    L.append("}"); L.append("")
    L.append("REGIME_WINDOWS = {  # group -> value -> [lo, hi] (latencies) or scalar (rates per mille, caps)")
    for group in sorted(SCHEMA["regime_windows"]):
        L.append(f'    "{group}": {{' + ", ".join(f'"{k}": {v!r}' for k, v in src["regime_windows"][group].items()) + "},")
    L.append("}"); L.append("")
    L.append("KNOB_IDS = {  # regime knob -> REGIME_SET arg0; value index = position in PLUSARGS[name]['values']")
    for i, p in enumerate([q for q in src["plusargs"] if q["kind"] == "enum" and q["name"].startswith("knob_")]):
        L.append(f'    "{p["name"]}": {i},')
    L.append("}"); L.append("")
    rk = [q for q in src["plusargs"] if q["kind"] == "enum" and q["name"].startswith("knob_")]
    L.append("KNOB_CONSUMER = {  # regime knob -> yaml regime_set_consumer (bus, irq, dbg, scrkey, none, program)")
    for p in rk:
        L.append(f'    "{p["name"]}": "{p["regime_set_consumer"]}",')
    L.append("}"); L.append("")
    L.append("# knobs the SV dispatcher consumes at run time (REGIME_SET); the test library's CONSUMED_KNOBS reads this")
    L.append("REGIME_SET_CONSUMED = (" + ", ".join(f'"{p["name"]}"' for p in rk if p["regime_set_consumer"] in RUNTIME_CONSUMERS) + ",)")
    L.append("")
    L.append("SV_ENUMS = {  # mirrored from the declaring SV package, which is the authority for names and ordinals")
    for tname, path in SV_ENUM_SOURCES:
        members = sv_enum_members(path, tname)
        L.append(f'    "{tname}": {{' + ", ".join(f'"{k}": {v}' for k, v in members.items()) + "},")
    L.append("}"); L.append("")
    L.append("CMD = {  # bridge command kinds (cmd_kind codes)")
    for i, k in enumerate(src["bridge_cmds"], start=1):
        L.append(f'    "{k}": {i},')
    L.append("}"); L.append("")
    L.append(f"EXPORT_RECORD_FIELDS = {tuple(src['export_record_fields'])!r}")
    L.append(f"EXPORT_COUNTER_FIELDS = {tuple(src['export_counter_fields'])!r}")
    L.append(f"EXPORT_SOURCES = {tuple(export_sources(src))!r}")
    L.append(f"EXPORT_ACTIVE_SOURCES = {tuple(src['export_active_sources'])!r}  # sources whose writers are instanced in this build (yaml export_active_sources)")
    L.append("EXPORT_EVENTS = (  # (source, event, fields); one exact event per row")
    for row in src["export_events"]:
        L.append(f"    ({row['source']!r}, {row['event']!r}, {tuple(row['fields'])!r}),")
    L.append(")"); L.append("")
    rows = src.get("_witness_rows") or []
    groups = witness_groups(rows)
    L.append("# CG-WIT-001 witness protocol (COV_WITNESS arg0 = WITNESS_IDS[tp], arg1 = WITNESS_GROUPS[the issuing test's group])")
    L.append("WITNESS_IDS = {" + ", ".join(f"{r['tp_item']!r}: {i}" for i, r in enumerate(rows)) + "}")
    L.append("WITNESS_BINS = {" + ", ".join(f"{r['tp_item']!r}: {r['bin']!r}" for r in rows) + "}")
    L.append("WITNESS_GROUP_OF = {" + ", ".join(f"{r['tp_item']!r}: {r['test_group']!r}" for r in rows) + "}")
    L.append("WITNESS_GROUPS = {" + ", ".join(f"{g!r}: {k}" for g, k in groups.items()) + "}")
    L.append(f"WITNESS_COUNT = {len(rows)}"); L.append("")
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


def render_h(src, mm, cvals):
    L = ["// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml; do not edit.",
         "// Memory map, ISA string and TB constants for the Spike DPI shim (architecture C5.1, C11).",
         "#ifndef GEN_ISA_SHIM_MAP_H", "#define GEN_ISA_SHIM_MAP_H", "",
         f'#define GEN_ISA_STRING "{src["isa_string"]}"', ""]
    for k, v in mm.items():
        L.append(f"#define GEN_MM_{k.upper():<22} 0x{v:08x}u")
    L.append("")
    for c in src["constants"]:
        L.append(f"#define {c['name']:<34} {cvals[c['name']]}u")
    L.append("")
    for i, k in enumerate(src["bridge_cmds"], start=1):
        L.append(f"#define GEN_CMD_{k:<28} {i}u")
    L += ["", "#endif"]
    return "\n".join(L) + "\n"


def sv_literal(p):
    d = p.get("default")
    if p["kind"] in ("string", "enum"):
        return f'"{d if d is not None else ""}"'
    if p["kind"] == "hex":
        return f"32'h{int(d):08x}" if d is not None else "32'h0"
    if p["kind"] == "bool":
        return "1'b1" if d else "1'b0"
    return str(int(d)) if d is not None else "0"


def render_cfg(src):
    """Include for class gen_env_cfg: one field per plusarg (plus a `_set` flag), parse_plusargs(),
    validate() for enum values and pinned_count() for the banner."""
    L = ["// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml; do not edit.",
         "// Included inside class gen_env_cfg (dv/auto_dv/env/gen_env_pkg.sv): fields, parse_plusargs(),",
         "// validate(), pinned_count(). Types: string/enum -> string, int -> int unsigned, hex -> logic [31:0],",
         "// bool -> bit. `<name>_set` records that the plusarg was supplied (pinning, optional knobs, checker isolation).", ""]
    for p in src["plusargs"]:
        k = p["kind"]; n = p["name"]
        typ = {"string": "string", "enum": "string", "int": "int unsigned", "hex": "logic [31:0]", "bool": "bit"}[k]
        L.append(f"  {typ} {n} = {sv_literal(p)};")
        L.append(f"  bit {n}_set = 1'b0;")
    L += ["", "  function void parse_plusargs();", "    string s; int unsigned u; logic [31:0] h;"]
    for p in src["plusargs"]:
        k = p["kind"]; n = p["name"]; P = f"PLUSARG_{n.upper()}"
        if k in ("string", "enum"):
            L.append(f'    if ($value$plusargs({{{P}, "=%s"}}, s)) begin {n} = s; {n}_set = 1\'b1; end')
        elif k == "int":
            L.append(f'    if ($value$plusargs({{{P}, "=%d"}}, u)) begin {n} = u; {n}_set = 1\'b1; end')
        elif k == "hex":
            L.append(f'    if ($value$plusargs({{{P}, "=%h"}}, h)) begin {n} = h; {n}_set = 1\'b1; end')
        else:
            L.append(f'    if ($value$plusargs({{{P}, "=%d"}}, u)) begin {n} = (u != 0); {n}_set = 1\'b1; end')
    L += ["  endfunction", "",
          "  // Enumerated knobs must hold one of their yaml values; msg names the first offender.",
          "  function bit validate(output string msg);"]
    for p in src["plusargs"]:
        if p["kind"] == "enum":
            n = p["name"]; U = n.upper()
            L.append(f'    if (!gen_str_in_csv({n}, GEN_ENUM_{U}_VALUES)) begin msg = {{"+", PLUSARG_{U}, "=", {n}, " not in ", GEN_ENUM_{U}_VALUES}}; return 1\'b0; end')
    L += ["    msg = \"\";", "    return 1'b1;", "  endfunction", "",
          "  // Regime knobs supplied on the command line (pinned), for the banner and CG-REG cp_pinned_count.",
          "  function int unsigned pinned_count();", "    int unsigned c = 0;"]
    for p in src["plusargs"]:
        if p["kind"] == "enum" and p["name"].startswith("knob_"):
            L.append(f"    if ({p['name']}_set) c++;")
    L += ["    return c;", "  endfunction", ""]
    return "\n".join(L) + "\n"


def load_witness(src, root):
    """The CG-WIT-001 rows of the witness CSV (witness_csv): index = row order, unique bins w_tp_<area>_<nnn>, non-empty groups."""
    import csv
    rel = src.get("witness_csv")
    if not isinstance(rel, str) or not rel:
        die("witness_csv must name the CG-WIT-001 CSV")
    path = Path(rel) if Path(rel).is_absolute() else root / rel
    if not path.is_file():
        die(f"witness_csv {rel} not found")
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or set(rows[0].keys()) != {"index", "tp_item", "bin", "test_group", "marked"}:
        die(f"witness_csv {rel}: columns must be index,tp_item,bin,test_group,marked")
    seen_bin, seen_tp = set(), set()
    for i, r in enumerate(rows):
        if r["index"] != str(i):
            die(f"witness_csv {rel}: row {i} carries index {r['index']}")
        if not re.fullmatch(r"TP-[A-Z]+-[0-9]{3}", r["tp_item"]) or r["tp_item"] in seen_tp:
            die(f"witness_csv {rel}: bad or repeated tp_item {r['tp_item']} at row {i}")
        if not re.fullmatch(r"w_tp_[a-z0-9]+_[0-9]{3}", r["bin"]) or r["bin"] in seen_bin:
            die(f"witness_csv {rel}: bad or repeated bin {r['bin']} at row {i}")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", r["test_group"]):
            die(f"witness_csv {rel}: bad test_group {r['test_group']!r} at row {i}")
        if r["marked"] not in ("0", "1"):
            die(f"witness_csv {rel}: marked must be 0 or 1 at row {i}")
        seen_bin.add(r["bin"]); seen_tp.add(r["tp_item"])
    return rows


def witness_groups(rows):
    """test group -> group index, in first-appearance order."""
    groups = {}
    for r in rows:
        groups.setdefault(r["test_group"], len(groups))
    return groups


def render_wit(rows):
    groups = witness_groups(rows)
    L = ["// gen_wit_bins.svh: CG-WIT-001 witness bins, rendered by dv/auto_dv/tb/gen_knobs_codegen.py from the yaml's witness_csv",
         "// (dv/auto_dv/docs/gen_trace_witness_ids.csv); do not edit. Included by gen_fcov_pkg.sv.",
         f"localparam int unsigned GEN_WITNESS_COUNT = {len(rows)};",
         f"localparam int unsigned GEN_WITNESS_GROUP_COUNT = {len(groups)};",
         'localparam string GEN_WITNESS_TP_NAMES = "' + ",".join(r["tp_item"] for r in rows) + '";  // index order',
         'localparam string GEN_WITNESS_GROUP_NAMES = "' + ",".join(groups) + '";  // group index order',
         "// the owning test's group index per row (COV_WITNESS arg1 must equal it)",
         "localparam int unsigned GEN_WITNESS_GROUP_OF [GEN_WITNESS_COUNT] = '{" + ", ".join(str(groups[r["test_group"]]) for r in rows) + "};",
         "`define GEN_WIT_BINS \\"]
    for i, r in enumerate(rows):
        tail = " \\" if i + 1 < len(rows) else ""
        L.append(f"  bins {r['bin']} = {{{i}}};{tail}")
    return "\n".join(L) + "\n"


def render_all(src_path, root):
    src = load(src_path)
    src["_witness_rows"] = load_witness(src, root)
    cvals = const_values(src)
    mm = memory_map(src)
    resolve_defaults(src, mm, cvals)
    pkg = root / REL_PKG
    return {pkg: render_pkg(src, mm, cvals, pkg), root / REL_PY: render_py(src, mm, cvals),
            root / REL_H: render_h(src, mm, cvals), root / REL_CFG: render_cfg(src),
            root / REL_RLINE: render_record_line(src), root / REL_ELINE: render_event_lines(src),
            root / REL_WIT: render_wit(src["_witness_rows"])}, src, mm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail when any rendered file is stale")
    ap.add_argument("--src", type=Path, default=SRC, help="yaml source (default: the one source)")
    ap.add_argument("--root", type=Path, default=ROOT, help="tree that holds the rendered targets (default: the clone)")
    args = ap.parse_args()
    root = args.root.resolve()
    targets, src, mm = render_all(args.src.resolve(), root)
    for path, text in targets.items():
        if any(ord(ch) > 127 for ch in text):
            die(f"non-ASCII output for {path}")
    stale = [str(p.relative_to(root)) for p, t in targets.items() if not p.is_file() or p.read_text() != t]
    if args.check:
        if stale:
            print("gen_knobs_codegen --check: STALE " + " ".join(stale))
            return 1
        print("gen_knobs_codegen --check: up to date")
        return 0
    for p, t in targets.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t)
    print("gen_knobs_codegen: rendered " + " ".join(str(p.relative_to(root)) for p in targets)
          + f" ({len(src['plusargs'])} plusargs, {len(src['constants'])} constants, {len(mm)} map entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
