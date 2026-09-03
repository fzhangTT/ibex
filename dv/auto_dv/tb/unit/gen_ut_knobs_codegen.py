#!/usr/bin/env python3
"""Unit test for the constants codegen (architecture C11): one YAML source, three generated
consumers (the marked region of gen_tb_pkg.sv, dv/auto_dv/gen_tb/gen_knobs.py, dv/auto_dv/isa/
gen_isa_shim_map.h). Written BEFORE gen_knobs_codegen.py existed (TDD red run recorded in
dv/auto_dv/evidence/gen_tdd_knobs_codegen.md). Plain asserts, no pytest; exit 1 on the first
failure, 0 when every check passes."""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TB = ROOT / "dv/auto_dv/tb"
YAML_SRC = TB / "gen_tb_knobs.yaml"
CODEGEN = TB / "gen_knobs_codegen.py"
PKG = TB / "gen_tb_pkg.sv"
PY_OUT = ROOT / "dv/auto_dv/gen_tb/gen_knobs.py"
H_OUT = ROOT / "dv/auto_dv/isa/gen_isa_shim_map.h"
TESTLIST = ROOT / "dv/auto_dv/flow/gen_testlist.yaml"
PROGRAM = ROOT / "dv/auto_dv/stim/gen_program.py"

fails = 0
def check(what, ok, detail=""):
    global fails
    print(f"{'OK  ' if ok else 'FAIL'} {what}" + (f" ({detail})" if detail and not ok else ""))
    if not ok:
        fails += 1

def main():
    import yaml
    check("yaml source exists", YAML_SRC.is_file(), str(YAML_SRC))
    check("codegen exists", CODEGEN.is_file(), str(CODEGEN))
    if fails:
        return finish()
    src = yaml.safe_load(YAML_SRC.read_text())
    # --check must pass on a freshly generated tree
    r = subprocess.run([sys.executable, str(CODEGEN), "--check"], capture_output=True, text=True)
    check("codegen --check passes", r.returncode == 0, (r.stdout + r.stderr)[-400:])
    pkg = PKG.read_text()
    names = [p["name"] for p in src["plusargs"]]
    check("plusarg names unique", len(names) == len(set(names)))
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
    dbg_only = [p["name"] for p in src["plusargs"] if p.get("debug_only")]
    check("dbg_csr_probe is debug_only", "dbg_csr_probe" in dbg_only)
    tl = yaml.safe_load(TESTLIST.read_text())
    for n in dbg_only:
        check(f"Runtime debug_only_plusargs lists gen_{n}", f"gen_{n}" in tl.get("debug_only_plusargs", []))
    # the 19 DV Lead regime knobs (gen_fcov_plan.md Section REG) exist as enum knobs
    reg = ["imem_gnt_delay", "imem_rvalid_delay", "imem_err_rate", "imem_intg_err_rate", "imem_outstanding_cap",
           "dmem_gnt_delay", "dmem_rvalid_delay", "dmem_err_rate", "dmem_intg_err_rate", "irq_regime",
           "irq_line_mix", "irq_hold", "debug_req_regime", "scr_key_delay", "icache_ecc_err_rate",
           "fetch_enable_regime", "mcounteren_writable", "instr_mix", "priv_regime", "pmp_regime"]
    enums = {p["name"]: p for p in src["plusargs"] if p["kind"] == "enum"}
    for k in reg:
        check(f"regime knob knob_{k} present as enum", f"knob_{k}" in enums)
    # generated python module
    check("gen_knobs.py exists", PY_OUT.is_file())
    if PY_OUT.is_file():
        spec = importlib.util.spec_from_file_location("gen_knobs", PY_OUT)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        check("python PLUSARGS has every name", set(m.PLUSARGS) == set(names))
        check("python ISA_STRING equals yaml", m.ISA_STRING == src["isa_string"])
        check("python knob values match yaml", all(m.PLUSARGS[k]["values"] == enums[k]["values"] for k in enums))
        hdr = H_OUT.read_text() if H_OUT.is_file() else ""
        check("header exists", H_OUT.is_file())
        check("header ISA string equals yaml", f'#define GEN_ISA_STRING "{src["isa_string"]}"' in hdr)
        for k, v in m.MEMORY_MAP.items():
            check(f"header carries {k}", re.search(rf"#define GEN_MM_{k.upper()}\s+0x{v:08x}", hdr) is not None, f"0x{v:08x}")
        # memory map agrees with gen_program.py's own derivation
        spec2 = importlib.util.spec_from_file_location("gen_program", PROGRAM)
        gp = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(gp)
        mm = gp.check_link_constants(gp.TARGET_SRC / "gen_link.ld")
        for k in ("dm_base", "dm_size", "dm_halt", "boot_page", "prog_size"):
            check(f"memory map {k} agrees with gen_program", m.MEMORY_MAP[k] == mm[k], f"{m.MEMORY_MAP.get(k)} vs {mm[k]}")
        check("gen_program ISA string equals yaml", gp.SPIKE_ISA == src["isa_string"])
        # MMIO page lies outside RAM and DM
        mmio = m.MEMORY_MAP["mmio_base"]; msz = m.MEMORY_MAP["mmio_size"]
        outside = (mmio + msz <= mm["boot_page"] or mmio >= mm["boot_page"] + mm["prog_size"]) and \
                  (mmio + msz <= mm["dm_base"] or mmio >= mm["dm_base"] + mm["dm_size"])
        check("MMIO page outside program and DM windows", outside)
        for c in src["constants"]:
            check(f"pkg declares constant {c['name']}", re.search(rf"\b{c['name']}\b\s*=", pkg) is not None)
            if "value" in c:
                check(f"python CONSTANTS[{c['name']}]", m.CONSTANTS.get(c["name"]) == c["value"])
    # step 1b additions (written before the renderer produced them): bridge command codes and the
    # rendered env-cfg include with one field and one parse line per plusarg, plus the known-name check
    CFG_SVH = TB / "gen_env_cfg_knobs.svh"
    check("yaml has bridge_cmds", isinstance(src.get("bridge_cmds"), list) and len(src["bridge_cmds"]) >= 10)
    for i, k in enumerate(src.get("bridge_cmds", []), start=1):
        check(f"pkg declares GEN_CMD_{k} = {i}", re.search(rf"GEN_CMD_{k}\s*=\s*8'd{i}\b", pkg) is not None)
    if PY_OUT.is_file():
        check("python CMD codes match", all(m.CMD.get(k) == i for i, k in enumerate(src.get("bridge_cmds", []), start=1)))
    check("env cfg include exists", CFG_SVH.is_file(), str(CFG_SVH))
    if CFG_SVH.is_file():
        svh = CFG_SVH.read_text()
        for pa in src["plusargs"]:
            check(f"cfg field for {pa['name']}", re.search(rf"\b{pa['name']}\b\s*(=|;)", svh) is not None)
            check(f"cfg parses PLUSARG_{pa['name'].upper()}", f"PLUSARG_{pa['name'].upper()}" in svh)
        check("cfg has parse_plusargs", "function void parse_plusargs" in svh)
        check("cfg validates enum values", "GEN_ENUM_" in svh and "_VALUES" in svh)
    check("pkg has gen_is_known_plusarg", "function automatic bit gen_is_known_plusarg" in pkg)
    check("known-plusarg list covers every name", all(f'"gen_{n}"' in pkg[pkg.find("gen_is_known_plusarg"):] for n in names))
    return finish()

def finish():
    print(f"GEN_UT_KNOBS_CODEGEN {'FAIL' if fails else 'PASS'} ({fails} failures)")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
