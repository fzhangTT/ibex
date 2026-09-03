#!/usr/bin/env python3
"""Unit test for the constants codegen (architecture C11): one YAML source, four rendered consumers
(the marked region of gen_tb_pkg.sv, gen_env_cfg_knobs.svh, dv/auto_dv/gen_tb/gen_knobs.py,
dv/auto_dv/isa/gen_isa_shim_map.h). Positive path on the real tree; negative paths through --src
(schema fixtures the loader must refuse) and --root (stale-target mutations --check must catch) on a
scratch copy under dv/auto_dv/work/tb-infra/ut_scratch (repo-local, never /tmp). TDD transcript:
dv/auto_dv/evidence/gen_tdd_knobs_codegen.md. Plain asserts, no pytest; exit 1 on any failure."""
import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TB = ROOT / "dv/auto_dv/tb"
YAML_SRC = TB / "gen_tb_knobs.yaml"
CODEGEN = TB / "gen_knobs_codegen.py"
PKG = TB / "gen_tb_pkg.sv"
CFG_SVH = TB / "gen_env_cfg_knobs.svh"
PY_OUT = ROOT / "dv/auto_dv/gen_tb/gen_knobs.py"
H_OUT = ROOT / "dv/auto_dv/isa/gen_isa_shim_map.h"
IBEX_PKG = ROOT / "rtl/ibex_pkg.sv"
TESTLIST = ROOT / "dv/auto_dv/flow/gen_testlist.yaml"
PROGRAM = ROOT / "dv/auto_dv/stim/gen_program.py"
SCRATCH = ROOT / "dv/auto_dv/work/tb-infra/ut_scratch/knobs_codegen"
TARGETS = ("dv/auto_dv/tb/gen_tb_pkg.sv", "dv/auto_dv/tb/gen_env_cfg_knobs.svh",
           "dv/auto_dv/gen_tb/gen_knobs.py", "dv/auto_dv/isa/gen_isa_shim_map.h")
# the 20 DV Lead regime knobs (gen_fcov_plan.md Section REG)
REG_KNOBS = ["imem_gnt_delay", "imem_rvalid_delay", "imem_err_rate", "imem_intg_err_rate", "imem_outstanding_cap",
             "dmem_gnt_delay", "dmem_rvalid_delay", "dmem_err_rate", "dmem_intg_err_rate", "irq_regime",
             "irq_line_mix", "irq_hold", "debug_req_regime", "scr_key_delay", "icache_ecc_err_rate",
             "fetch_enable_regime", "mcounteren_writable", "instr_mix", "priv_regime", "pmp_regime"]

fails = 0


def check(what, ok, detail=""):
    global fails
    print(f"{'OK  ' if ok else 'FAIL'} {what}" + (f" ({detail})" if detail and not ok else ""))
    if not ok:
        fails += 1


def codegen(*args):
    return subprocess.run([sys.executable, str(CODEGEN), *args], capture_output=True, text=True)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ibex_int_param(name):
    m = re.search(rf"parameter\s+int\s+unsigned\s+{name}\s*=\s*(\d+)\s*;", IBEX_PKG.read_text())
    return int(m.group(1)) if m else None


def refused_fixtures(text):
    """(label, mutated yaml text, expected fragment of the refusal message)."""
    yield ("unknown plusarg key", text.replace("{name: hart_id, kind: hex, default: 0,",
                                              "{name: hart_id, kind: hex, defualt: 0,", 1), "unknown key(s) defualt")
    yield ("unquoted comma in desc", text.replace('desc: "hart_id_i (architecture C1)"',
                                                 "desc: hart_id_i, architecture C1", 1), "unknown key(s)")
    yield ("unknown constant key", text.replace("{name: GEN_DBUS_MAX_OUTSTANDING, value: 2,",
                                                "{name: GEN_DBUS_MAX_OUTSTANDING, valeu: 2,", 1), "unknown key(s) valeu")
    yield ("unknown memory_map key", text.replace("  mmio_size: 0x1000\n", "  mmio_size: 0x1000\n  mmio_sise: 0x1000\n", 1),
           "memory_map: unknown key(s) mmio_sise")
    yield ("unknown register key", text.replace("eot_addr: {offset: 0x104, size: 0x4}",
                                                "eot_addr: {offset: 0x104, sise: 0x4}", 1), "unknown key(s) sise")
    yield ("unknown top-level key", text + "\nregime_windowz: {}\n", "top level: unknown key(s) regime_windowz")
    yield ("regime window value outside the enum set", text.replace("rate_per_mille: {none: 0, rare: 2, frequent: 50}",
                                                                   "rate_per_mille: {none: 0, rare: 2, often: 50}", 1),
           "regime_windows.rate_per_mille")
    yield ("unknown derivation", text.replace("derive: irq_fast_w,", "derive: irq_fast_width,", 1), "unknown derivation")
    yield ("default and default_from together", text.replace("{name: hart_id, kind: hex, default: 0,",
                                                             "{name: hart_id, kind: hex, default: 0, default_from: GEN_CLK_PERIOD_NS,", 1),
           "exactly one of default / default_from")


def main():
    import yaml
    check("yaml source exists", YAML_SRC.is_file(), str(YAML_SRC))
    check("codegen exists", CODEGEN.is_file(), str(CODEGEN))
    if fails:
        return finish()
    src = yaml.safe_load(YAML_SRC.read_text())
    # ---- positive path: the real tree is up to date
    r = codegen("--check")
    check("codegen --check passes", r.returncode == 0, (r.stdout + r.stderr)[-400:])
    pkg = PKG.read_text()
    names = [p["name"] for p in src["plusargs"]]
    check("plusarg names unique", len(names) == len(set(names)))
    allowed = {"name", "kind", "default", "default_from", "values", "debug_only", "desc"}
    check("yaml parses with no spurious plusarg keys (every desc quoted)",
          all(set(p) <= allowed for p in src["plusargs"]),
          str([(p["name"], sorted(set(p) - allowed)) for p in src["plusargs"] if not set(p) <= allowed]))
    for p in src["plusargs"]:
        up = p["name"].upper()
        decl = f'parameter string PLUSARG_{up} = "gen_{p["name"]}";'
        check(f"pkg declares PLUSARG_{up} once", pkg.count(decl) == 1, decl)
        if p["kind"] == "enum":
            check(f"enum {p['name']} has >= 2 values", len(p["values"]) >= 2)
            check(f"enum {p['name']} default is a value", p["default"] in p["values"], str(p.get("default")))
            vals = ",".join(p["values"])
            check(f"pkg carries values of {p['name']}", f'GEN_ENUM_{up}_VALUES = "{vals}"' in pkg)
    check("no PLUSARG_ outside the generated region", pkg.count("parameter string PLUSARG_") == len(names))
    check("hart_id knob present (C1)", "hart_id" in names)
    check("ut_lockstep_min_ratio_pct removed (exact consumed-records check)", "ut_lockstep_min_ratio_pct" not in names)
    dbg_only = [p["name"] for p in src["plusargs"] if p.get("debug_only")]
    for n in ("dbg_csr_probe", "rvfi_trace", "isa_string", "isa_log", "sb_trace"):
        check(f"{n} is debug_only", n in dbg_only)
    tl = yaml.safe_load(TESTLIST.read_text())
    for n in dbg_only:
        check(f"Runtime debug_only_plusargs lists gen_{n}", f"gen_{n}" in tl.get("debug_only_plusargs", []))
    enums = {p["name"]: p for p in src["plusargs"] if p["kind"] == "enum"}
    for k in REG_KNOBS:
        check(f"regime knob knob_{k} present as enum", f"knob_{k}" in enums)
    # ---- regime windows: one origin for the numeric meaning of the regimes
    rw = src["regime_windows"]
    for group, knobs in (("gnt_delay", ("knob_imem_gnt_delay", "knob_dmem_gnt_delay")),
                         ("rvalid_delay", ("knob_imem_rvalid_delay", "knob_dmem_rvalid_delay")),
                         ("rate_per_mille", ("knob_imem_err_rate", "knob_dmem_err_rate")),
                         ("outstanding_cap", ("knob_imem_outstanding_cap",))):
        for kn in knobs:
            check(f"regime_windows.{group} keys equal values of {kn}", sorted(rw[group]) == sorted(enums[kn]["values"]))
    check("rvalid classes align with the fcov plan (min1 1, short 2..4, long 5..)",
          rw["rvalid_delay"]["min1"] == [1, 1] and rw["rvalid_delay"]["short"] == [2, 4] and rw["rvalid_delay"]["long"][0] == 5)
    check("pkg has gen_regime_window()", "function automatic bit gen_regime_window(string group, string value, output int unsigned lo, output int unsigned hi)" in pkg)
    check("pkg has gen_regime_scalar()", "function automatic bit gen_regime_scalar(string group, string value, output int unsigned v)" in pkg)
    for k, v in rw["rvalid_delay"].items():
        check(f"pkg renders rvalid window {k}", f'if (group == "rvalid_delay" && value == "{k}") begin lo = {v[0]}; hi = {v[1]}; return 1\'b1; end' in pkg)
    # ---- generated python module
    check("gen_knobs.py exists", PY_OUT.is_file())
    if PY_OUT.is_file():
        m = load_module("gen_knobs", PY_OUT)
        check("python PLUSARGS has every name", set(m.PLUSARGS) == set(names))
        check("python ISA_STRING equals yaml", m.ISA_STRING == src["isa_string"])
        check("python knob values match yaml", all(m.PLUSARGS[k]["values"] == enums[k]["values"] for k in enums))
        check("python REGIME_WINDOWS equals yaml", m.REGIME_WINDOWS == rw)
        check("python DEBUG_ONLY equals yaml", sorted(m.DEBUG_ONLY) == sorted(f"gen_{n}" for n in dbg_only))
        hdr = H_OUT.read_text() if H_OUT.is_file() else ""
        check("header exists", H_OUT.is_file())
        check("header ISA string equals yaml", f'#define GEN_ISA_STRING "{src["isa_string"]}"' in hdr)
        for k, v in m.MEMORY_MAP.items():
            check(f"header carries {k}", re.search(rf"#define GEN_MM_{k.upper()}\s+0x{v:08x}", hdr) is not None, f"0x{v:08x}")
            check(f"pkg carries GEN_MM_{k.upper()}", f"GEN_MM_{k.upper()} = 32'h{v >> 16:04x}_{v & 0xFFFF:04x}" in pkg)
        for reg in src["memory_map"]["registers"]:
            base = reg[:-len("_addr")]
            check(f"memory map renders {base}_size", f"{base}_size" in m.MEMORY_MAP and m.MEMORY_MAP[f"{base}_size"] == src["memory_map"]["registers"][reg]["size"])
        check("memory map carries boot_page_mask", m.MEMORY_MAP.get("boot_page_mask") == src["memory_map"]["boot_page_mask"])
        # memory map agrees with gen_program.py's own derivation
        gp = load_module("gen_program", PROGRAM)
        mm = gp.check_link_constants(gp.TARGET_SRC / "gen_link.ld")
        for k in ("dm_base", "dm_size", "dm_halt", "boot_page", "prog_size"):
            check(f"memory map {k} agrees with gen_program", m.MEMORY_MAP[k] == mm[k], f"{m.MEMORY_MAP.get(k)} vs {mm[k]}")
        check("gen_program ISA string equals yaml", gp.SPIKE_ISA == src["isa_string"])
        mmio = m.MEMORY_MAP["mmio_base"]; msz = m.MEMORY_MAP["mmio_size"]
        outside = (mmio + msz <= mm["boot_page"] or mmio >= mm["boot_page"] + mm["prog_size"]) and \
                  (mmio + msz <= mm["dm_base"] or mmio >= mm["dm_base"] + mm["dm_size"])
        check("MMIO page outside program and DM windows", outside)
        # constants: literal ones mirror the yaml; derived ones mirror an independent parse of ibex_pkg
        for c in src["constants"]:
            check(f"pkg declares constant {c['name']}", re.search(rf"\b{c['name']}\b\s*=", pkg) is not None)
            check(f"header carries {c['name']}", re.search(rf"#define {c['name']}\s+{m.CONSTANTS[c['name']]}u", hdr) is not None)
            if "value" in c:
                check(f"python CONSTANTS[{c['name']}] equals yaml", m.CONSTANTS.get(c["name"]) == c["value"])
            else:
                check(f"pkg renders {c['name']}_PY mirror", f"{c['name']}_PY = {m.CONSTANTS[c['name']]};" in pkg)
        bus_bytes = ibex_int_param("BUS_SIZE") // 8
        line_bytes = ibex_int_param("IC_LINE_SIZE") // 8
        beats = line_bytes // bus_bytes
        fast_m = re.search(r"logic\s*\[\s*(\d+)\s*:\s*0\s*\]\s*irq_fast\s*;", IBEX_PKG.read_text())
        fast_w = int(fast_m.group(1)) + 1 if fast_m else None
        check("derived GEN_IBUS_MAX_OUTSTANDING == GEN_ICACHE_NUM_FB * IC_LINE_BEATS (ibex_pkg parse)",
              m.CONSTANTS["GEN_IBUS_MAX_OUTSTANDING"] == m.CONSTANTS["GEN_ICACHE_NUM_FB"] * beats, f"{beats} beats")
        check("derived GEN_IRQ_FAST_W == irq_fast width (ibex_pkg parse)", m.CONSTANTS["GEN_IRQ_FAST_W"] == fast_w, str(fast_w))
        check("derived GEN_IRQ_FAST_MASK == ((1 << w) - 1) << 16", m.CONSTANTS["GEN_IRQ_FAST_MASK"] == ((1 << fast_w) - 1) << 16)
        # default_from: one origin for defaults that were duplicated inside the source
        check("boot_addr default from memory_map.boot_addr_default", m.PLUSARGS["boot_addr"]["default"] == m.MEMORY_MAP["boot_addr_default"])
        for knob, const in (("mem_readback_words", "GEN_MEM_READBACK_WORDS_DEFAULT"), ("alive_timeout", "GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT"),
                            ("finish_timeout", "GEN_FINISH_TIMEOUT_CYCLES_DEFAULT")):
            check(f"{knob} default from {const}", m.PLUSARGS[knob]["default"] == m.CONSTANTS[const])
        # bridge commands
        check("yaml has bridge_cmds", isinstance(src.get("bridge_cmds"), list) and len(src["bridge_cmds"]) >= 10)
        for i, k in enumerate(src["bridge_cmds"], start=1):
            check(f"pkg declares GEN_CMD_{k} = {i}", re.search(rf"GEN_CMD_{k}\s*=\s*8'd{i}\b", pkg) is not None)
            check(f"pkg gen_cmd_name maps {i} to {k}", f'8\'d{i}: return "{k}";' in pkg)
        check("python CMD codes match", all(m.CMD.get(k) == i for i, k in enumerate(src["bridge_cmds"], start=1)))
        knob_names = [p["name"] for p in src["plusargs"] if p["kind"] == "enum" and p["name"].startswith("knob_")]
        for i, k in enumerate(knob_names):
            check(f"pkg declares GEN_KNOB_ID_{k[5:].upper()} = {i}", re.search(rf"GEN_KNOB_ID_{k[5:].upper()}\s*=\s*{i}\b", pkg) is not None)
        check("python KNOB_IDS matches", list(m.KNOB_IDS) == knob_names and all(m.KNOB_IDS[k] == i for i, k in enumerate(knob_names)))
    check("pkg has gen_knob_value()", "function automatic string gen_knob_value(int id, int idx)" in pkg)
    check("pkg has gen_knob_name()", "function automatic string gen_knob_name(int id)" in pkg)
    check("pkg has gen_is_known_plusarg", "function automatic bit gen_is_known_plusarg" in pkg)
    check("known-plusarg list covers every name", all(f'"gen_{n}"' in pkg[pkg.find("gen_is_known_plusarg"):] for n in names))
    check("pkg has gen_is_bool_plusarg", "function automatic bit gen_is_bool_plusarg" in pkg)
    bools = [p["name"] for p in src["plusargs"] if p["kind"] == "bool"]
    check("bool-plusarg list covers every bool knob", all(f'"gen_{n}"' in pkg[pkg.find("gen_is_bool_plusarg"):] for n in bools))
    # ---- rendered env-cfg include
    check("env cfg include exists", CFG_SVH.is_file(), str(CFG_SVH))
    if CFG_SVH.is_file():
        svh = CFG_SVH.read_text()
        for pa in src["plusargs"]:
            check(f"cfg field for {pa['name']}", re.search(rf"\b{pa['name']}\b\s*(=|;)", svh) is not None)
            check(f"cfg parses PLUSARG_{pa['name'].upper()}", f"PLUSARG_{pa['name'].upper()}" in svh)
        check("cfg has parse_plusargs", "function void parse_plusargs" in svh)
        check("cfg validates enum values", "GEN_ENUM_" in svh and "_VALUES" in svh)
        check("cfg boot_addr default resolved to the memory-map literal", "logic [31:0] boot_addr = 32'h80000000;" in svh)
    # ---- negative paths: schema fixtures the loader refuses
    SCRATCH.mkdir(parents=True, exist_ok=True)
    text = YAML_SRC.read_text()
    for label, mutated, fragment in refused_fixtures(text):
        check(f"fixture differs from the source ({label})", mutated != text)
        fx = SCRATCH / f"fixture_{label.replace(' ', '_')}.yaml"
        fx.write_text(mutated)
        r = codegen("--check", "--src", str(fx))
        check(f"loader refuses: {label}", r.returncode != 0 and fragment in (r.stdout + r.stderr), (r.stdout + r.stderr)[-300:])
    # ---- negative paths: --check catches a stale target (mutation of each rendered file in turn)
    root = SCRATCH / "tree"
    if root.exists():
        shutil.rmtree(root)
    for rel in TARGETS:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dst)
    r = codegen("--check", "--root", str(root))
    check("--check passes on the fresh scratch copy", r.returncode == 0, (r.stdout + r.stderr)[-300:])
    for rel in TARGETS:
        dst = root / rel
        orig = dst.read_text()
        lines = orig.splitlines(keepends=True)
        # the pkg keeps hand-written text outside its markers; the mutation must land inside the rendered region
        first = next((i for i, ln in enumerate(lines) if "GEN_KNOBS_BEGIN" in ln), -1) + 1
        idx = next(i for i, ln in enumerate(lines) if i >= first and re.search(r"\d", ln)
                   and not ln.lstrip().startswith(("//", "# ", '"""')))   # narrative lines; #define lines count
        lines[idx] = re.sub(r"\d", lambda mo: "1" if mo.group() == "0" else "0", lines[idx], count=1)   # one digit changes
        dst.write_text("".join(lines))
        r = codegen("--check", "--root", str(root))
        check(f"--check fails on a mutated {rel}", r.returncode == 1 and f"STALE {rel}" in r.stdout, (r.stdout + r.stderr)[-300:])
        dst.write_text(orig)
        r = codegen("--check", "--root", str(root))
        check(f"--check passes again after restoring {rel}", r.returncode == 0)
    r = codegen("--check", "--root", str(root))
    check("--check passes on the restored scratch copy", r.returncode == 0)
    return finish()


def finish():
    print(f"GEN_UT_KNOBS_CODEGEN {'FAIL' if fails else 'PASS'} ({fails} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
