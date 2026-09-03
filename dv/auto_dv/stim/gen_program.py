#!/usr/bin/env python3
"""gen_program.py: the single driver from (test config, seed) to ELF + memory image + sidecar.

One run seed drives everything (DV_prompt.txt Section 6): the same --seed value goes to the
riscv-dv generator (+ntb_random_seed through run.py --seed) and is recorded in the sidecar so the
TB and the ISA shim see it. Steps (each skippable): riscv-dv generation (run.py --so, gen step
only), debug-ROM relocation (gen_relocate_debug_rom.py), assemble + link with the lowRISC
toolchain and dv/auto_dv/stim/gen_riscv_dv_target/gen_link.ld (-Wl,-N, boot and debug-ROM stubs),
ELF -> image (gen_elf2mem.py), optional standalone Spike sanity run (pinned tools/spike).

Directed programs: --directed <file.S> [<file.S> ...] skips the generator and assembles the given
sources (plus the stubs) instead.

Usage (from a login shell with ci/env.sh sourced, any cwd):
    gen_program.py --test gen_rand_smoke --seed 1 --out <dir>            # generated
    gen_program.py --directed my.S --seed 1 --out <dir> --spike-check     # directed
    gen_program.py --test gen_rand_smoke --seed 1 --out <dir> --gen-build <dir>   # reuse a generator build
Outputs in <out>: prog.S (final assembly), prog.elf, prog.dis, prog.nm, prog.vmem, prog.sym.json
(sidecar: seed, test, gen_opts, sources, tool versions, checksum, symbols, entry), and
spike_commits.log when --spike-check is given. Exit status is nonzero on any failed step.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # dv/auto_dv/stim
ROOT = HERE.parents[2]                             # clone root
TARGET_SRC = HERE / "gen_riscv_dv_target"          # committed, gen_-prefixed sources
# riscv-dv and its `.include` lines need fixed file names (riscv_core_setting.sv, testlist.yaml,
# user_define.h, user_init.s, user_extension.svh); the tree keeps only gen_-prefixed files (landing
# rule), so the fixed-name target directory is materialized out-of-tree at flow time.
TARGET_FIXED_NAMES = {"gen_riscv_core_setting.sv": "riscv_core_setting.sv",
                      "gen_testlist.yaml": "testlist.yaml",
                      "user_extension/gen_user_define.h": "user_extension/user_define.h",
                      "user_extension/gen_user_init.s": "user_extension/user_init.s",
                      "user_extension/gen_user_extension.svh": "user_extension/user_extension.svh"}
TARGET_STATIC = ["gen_link.ld", "gen_boot_stub.S", "gen_debug_rom_stub.S"]
SV_WRAPPER = ROOT / "dv/auto_dv/tb/gen_dut_top.sv"
SV_TB_PKG = ROOT / "dv/auto_dv/tb/gen_tb_pkg.sv"
RISCV_DV = ROOT / "vendor/google_riscv-dv"
# Spike binary: tools/spike from SIM_RECIPE Section 11, overridable for a differently placed build.
SPIKE = Path(os.environ.get("GEN_SPIKE_BIN", str(ROOT / "tools/spike/bin/spike")))
# The ISA string and the MMIO page come from the rendered constants mirror (one origin: gen_tb_knobs.yaml).
def _gen_knobs():
    """The rendered constants mirror (dv/auto_dv/gen_tb/gen_knobs.py): ISA string and MMIO page."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_knobs", ROOT / "dv/auto_dv/gen_tb/gen_knobs.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN_KNOBS = _gen_knobs()
SPIKE_ISA = GEN_KNOBS.ISA_STRING
# Memory windows are derived from the SV parameters and gen_link.ld at run time (spike_mem_opts()).
CONFIG_NAME = "opentitan"   # the build configuration (DV_prompt Section 2); stated in every report


def config_params() -> dict:
    """-pvalue+ parameters of the build configuration from util/ibex_config.py (the single source
    of the opentitan values; the wrapper's own defaults are not the build's values)."""
    out = subprocess.run([sys.executable, str(ROOT / "util" / "ibex_config.py"), CONFIG_NAME, "vcs_opts"],
                         check=True, capture_output=True, text=True).stdout
    return {m.group(1): int(m.group(2)) for m in re.finditer(r"-pvalue\+(\w+)=(\d+)", out)}


def spike_cfg_opts() -> list:
    """Spike options derived from the build configuration and the wrapper defaults it does not name:
    PMP region count, PMP granularity (Ibex G -> 2^(G+2) bytes), trigger count (DbgHwBreakNum when
    DbgTriggerEn)."""
    cfg = config_params()
    regions = cfg.get("PMPNumRegions", sv_param(SV_WRAPPER, "PMPNumRegions"))
    gran = cfg.get("PMPGranularity", sv_param(SV_WRAPPER, "PMPGranularity"))
    trig_en = cfg.get("DbgTriggerEn", sv_param(SV_WRAPPER, "DbgTriggerEn"))
    triggers = sv_param(SV_WRAPPER, "DbgHwBreakNum") if trig_en else 0
    return ["--priv=mu", f"--pmpregions={regions}", f"--pmpgranularity={4 << gran}", f"--triggers={triggers}"]
GCC_ISA = "rv32imcb"   # lowRISC gcc 10.2: draft-B march, accepts the ratified Zb* mnemonics
GCC_ABI = "ilp32"


def run(cmd, log: Path | None = None, cwd: Path | None = None, env=None) -> int:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if log is not None:
        log.write_text("$ " + " ".join(map(str, cmd)) + "\n" + r.stdout + r.stderr)
    if r.returncode != 0:
        print(f"FAILED ({r.returncode}): {' '.join(map(str, cmd))}", file=sys.stderr)
        print((r.stdout + r.stderr)[-3000:], file=sys.stderr)
    return r.returncode


def tool(name_suffix: str) -> str:
    gcc = os.environ.get("RISCV_GCC")
    if not gcc:
        sys.exit("RISCV_GCC not set; source ci/env.sh")
    d, b = os.path.dirname(gcc), os.path.basename(gcc)
    return os.path.join(d, b.replace("-gcc", "-" + name_suffix))


def tool_version(cmd) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()[0]
    except Exception:  # noqa: BLE001 - version strings are informational only
        return "unknown"


def materialize_target(dest: Path) -> Path:
    """Copy the committed target sources into <dest> under the fixed names riscv-dv expects."""
    for src, fixed in TARGET_FIXED_NAMES.items():
        d = dest / fixed
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(TARGET_SRC / src, d)
    for name in TARGET_STATIC:
        shutil.copy(TARGET_SRC / name, dest / name)
    return dest


def sv_param(path: Path, name: str) -> int:
    """Read a parameter default (32'h..., 1'b., or decimal) from an SV file."""
    text = path.read_text()
    m = re.search(rf"\b{name}\b\s*=\s*32'h([0-9a-fA-F_]+)", text)
    if m:
        return int(m.group(1).replace("_", ""), 16)
    m = re.search(rf"\b{name}\b\s*=\s*(?:1'b)?(\d+)\s*[,)]", text)
    if not m:
        sys.exit(f"cannot find parameter {name} in {path}")
    return int(m.group(1))


def ld_regions(ld: Path) -> dict:
    """MEMORY regions of gen_link.ld: name -> (origin, length)."""
    text = ld.read_text()
    regs = {}
    for m in re.finditer(r"^\s*(\w+)\s*\(\w+\)\s*:\s*ORIGIN\s*=\s*0x([0-9A-Fa-f]+)\s*,\s*LENGTH\s*=\s*0x([0-9A-Fa-f]+)", text, re.M):
        regs[m.group(1)] = (int(m.group(2), 16), int(m.group(3), 16))
    return regs


def check_link_constants(ld: Path) -> dict:
    """gen_link.ld's MEMORY regions must match the SV parameters they mirror; fail loud otherwise.
    Returns the derived memory map (boot page base, program window size, DM base/size, DM budget)."""
    regs = ld_regions(ld)
    dm_halt = sv_param(SV_WRAPPER, "DmHaltAddr")
    dm_base = sv_param(SV_WRAPPER, "DmBaseAddr")
    dm_mask = sv_param(SV_WRAPPER, "DmAddrMask")
    boot = sv_param(SV_TB_PKG, "GEN_BOOT_ADDR_DEFAULT")
    boot_page = boot & 0xFFFFFF00
    first_fetch = boot_page | GEN_KNOBS.MEMORY_MAP["boot_reset_offset"]   # {boot_addr_i[31:8], 8'h80}, rtl/ibex_if_stage.sv:243, one origin in the yaml
    dm_budget = dm_base + dm_mask + 1 - dm_halt   # bytes from DmHaltAddr to the end of the DM window
    problems = []
    if "DM" not in regs or "PROG" not in regs:
        problems.append("MEMORY regions DM and PROG not both found")
    else:
        if regs["DM"][0] != dm_halt:
            problems.append(f"DM origin 0x{regs['DM'][0]:08x} != DmHaltAddr 0x{dm_halt:08x}")
        if regs["DM"][1] != dm_budget:
            problems.append(f"DM LENGTH 0x{regs['DM'][1]:x} != DmBaseAddr+DmAddrMask+1-DmHaltAddr 0x{dm_budget:x}")
        if regs["PROG"][0] != first_fetch:
            problems.append(f"PROG origin 0x{regs['PROG'][0]:08x} != first fetch 0x{first_fetch:08x}")
    if problems:
        sys.exit("gen_link.ld disagrees with the SV parameters: " + "; ".join(problems))
    return {"boot_page": boot_page, "prog_size": GEN_KNOBS.MEMORY_MAP["boot_reset_offset"] + regs["PROG"][1], "dm_base": dm_base,
            "dm_size": dm_mask + 1, "dm_halt": dm_halt, "dm_budget": dm_budget}


def spike_mem_opts(mm: dict) -> str:
    """-m windows for Spike: DM, program and the TB MMIO page (so signature and marker stores succeed
    standalone); all 4 KiB aligned by construction of the sources."""
    mmio = GEN_KNOBS.MEMORY_MAP
    return (f"-m0x{mm['dm_base']:x}:0x{mm['dm_size']:x},0x{mm['boot_page']:x}:0x{mm['prog_size']:x},"
            f"0x{mmio['mmio_base']:x}:0x{mmio['mmio_size']:x}")


def check_debug_rom_budget(elf: Path, mm: dict) -> int:
    """The linked .debug_rom must fit the DM budget (the linker also refuses overflow; this gives the
    Test Writer a clear message and records the size). Returns the ROM size in bytes."""
    sys.path.insert(0, str(HERE))
    import gen_elf2mem  # noqa: E402
    _entry, segs, _syms = gen_elf2mem.parse_elf32(elf.read_bytes())
    rom = [len(body) for vaddr, body in segs if vaddr == mm["dm_halt"]]
    size = rom[0] if rom else 0
    if size > mm["dm_budget"]:
        sys.exit(f"debug ROM 0x{size:x} bytes exceeds the DM budget 0x{mm['dm_budget']:x}")
    return size


def build_generator(gen_build: Path, log: Path) -> None:
    target = materialize_target(gen_build / "target")
    cmd = [sys.executable, "run.py", "--co", "-si", "vcs", "-ct", str(target),
           "-ext", str(target / "user_extension"), "--isa", "rv32imc_zba_zbb_zbc_zbs",
           "--mabi", GCC_ABI, "-o", str(gen_build), "--cmp_opts=-licqueue"]
    if run(cmd, log, cwd=RISCV_DV):
        sys.exit("generator compile failed")


def generate(test: str, seed: int, gen_build: Path, gen_run: Path, sim_opts: str, log: Path) -> tuple[Path, int]:
    """Run the compiled generator into a PRIVATE per-run directory so concurrent seeds never share
    an asm_test/ or seed.yaml; return the .S and the seed riscv-dv recorded for it."""
    if gen_run.exists():
        shutil.rmtree(gen_run)
    gen_run.mkdir(parents=True)
    for name in ("vcs_simv", "vcs_simv.daidir"):
        (gen_run / name).symlink_to(gen_build / name)
    target = materialize_target(gen_run / "target")
    cmd = [sys.executable, "run.py", "--so", "-si", "vcs", "-ct", str(target),
           "-ext", str(target / "user_extension"), "--isa", "rv32imc_zba_zbb_zbc_zbs",
           "--mabi", GCC_ABI, "-o", str(gen_run), "-tn", test, "--seed", str(seed),
           "-s", "gen", "--noclean"]
    if sim_opts:
        cmd.append(f"--sim_opts={sim_opts}")
    if run(cmd, log, cwd=RISCV_DV):
        sys.exit("generation failed")
    asms = sorted((gen_run / "asm_test").glob(f"{test}_*.S"))
    if len(asms) != 1:
        sys.exit(f"expected exactly one {test}_*.S in {gen_run / 'asm_test'}, found {len(asms)}")
    # Seed binding: riscv-dv records the seed it used per test in <out>/seed.yaml; it must be ours.
    seed_yaml = gen_run / "seed.yaml"
    if not seed_yaml.is_file():
        sys.exit(f"{seed_yaml} missing: cannot prove which seed generated {asms[0].name}")
    m = re.search(rf"^{re.escape(asms[0].stem)}:\s*'?(\d+)'?\s*$", seed_yaml.read_text(), re.M)
    if not m:
        sys.exit(f"{seed_yaml} has no entry for {asms[0].stem}")
    used = int(m.group(1))
    if used != seed:
        sys.exit(f"seed mismatch: requested {seed}, riscv-dv used {used} for {asms[0].name}")
    return asms[0], used


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--test", help="riscv-dv testlist entry (dv/auto_dv/stim/gen_riscv_dv_target/gen_testlist.yaml)")
    ap.add_argument("--directed", nargs="+", type=Path, help="directed assembly source(s) instead of the generator")
    ap.add_argument("--seed", type=int, required=True, help="the one run seed")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--gen-build", type=Path, default=None,
                    help="compiled generator dir (default <out>/../gen_build; built if missing)")
    ap.add_argument("--sim-opts", default="", help="extra plusargs for the generator run (e.g. +gen_debug_section=1)")
    ap.add_argument("--no-debug-rom-reloc", action="store_true", help="skip gen_relocate_debug_rom.py")
    ap.add_argument("--no-stubs", action="store_true", help="do not link gen_boot_stub.S / gen_debug_rom_stub.S")
    ap.add_argument("--gcc-opts", default="", help="extra gcc options (space separated)")
    ap.add_argument("--spike-check", action="store_true", help="run the ELF on tools/spike with --log-commits")
    ap.add_argument("--spike-isa", default=SPIKE_ISA)
    ap.add_argument("--spike-timeout", type=int, default=120)
    args = ap.parse_args()
    if bool(args.test) == bool(args.directed):
        sys.exit("give exactly one of --test or --directed")

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    gcc = os.environ.get("RISCV_GCC") or sys.exit("RISCV_GCC not set; source ci/env.sh")
    sidecar_extra = {"seed": args.seed, "test": args.test, "directed": [str(p) for p in (args.directed or [])],
                     "sim_opts": args.sim_opts, "steps": []}

    # Step 1: program source
    prog_s = out / "prog.S"
    if args.test:
        gen_build = (args.gen_build or (out.parent / "gen_build")).resolve()
        if not (gen_build / "vcs_simv").exists():
            build_generator(gen_build, out / "gen_compile.log")
            sidecar_extra["steps"].append("generator_compile")
        asm, seed_used = generate(args.test, args.seed, gen_build, out / "gen_run", args.sim_opts,
                                  out / "gen_run.log")
        shutil.copy(asm, prog_s)
        sidecar_extra["steps"].append("generate")
        sidecar_extra["generator_build"] = str(gen_build)
        sidecar_extra["seed_used"] = seed_used   # cross-checked against --seed by generate()
        if not args.no_debug_rom_reloc:
            if run([sys.executable, str(HERE / "gen_relocate_debug_rom.py"), str(prog_s), "--in-place"],
                   out / "reloc.log"):
                sys.exit("debug ROM relocation failed")
            sidecar_extra["steps"].append("debug_rom_relocate")
        sources = [prog_s]
    else:
        sources = [p.resolve() for p in args.directed]
        for p in sources:
            if not p.is_file():
                sys.exit(f"missing directed source {p}")
        shutil.copy(sources[0], prog_s)
        sidecar_extra["steps"].append("directed")

    # Step 2: assemble + link (after checking the linker script against the SV memory map)
    mm = check_link_constants(TARGET_SRC / "gen_link.ld")
    sidecar_extra["memory_map"] = {k: f"0x{v:x}" for k, v in mm.items()}
    sidecar_extra["spike_opts"] = spike_cfg_opts()
    inc_dir = materialize_target(out / "target") / "user_extension"
    elf = out / "prog.elf"
    # A program that carries its own .debug_rom (relocated riscv-dv ROM or a directed one) must
    # not also link the default stub, or the two would both claim DmHaltAddr.
    has_debug_rom = any(re.search(r"^\s*\.section\s+\.debug_rom\b", p.read_text(), re.M) for p in sources)
    stubs = [] if args.no_stubs else [TARGET_SRC / "gen_boot_stub.S"] + (
        [] if has_debug_rom else [TARGET_SRC / "gen_debug_rom_stub.S"])
    sidecar_extra["debug_rom"] = "program" if has_debug_rom else ("none" if args.no_stubs else "stub")
    cmd = [gcc, "-static", "-mcmodel=medany", "-fvisibility=hidden", "-nostdlib", "-nostartfiles",
           f"-march={GCC_ISA}", f"-mabi={GCC_ABI}", "-Wl,-N", "-T", str(TARGET_SRC / "gen_link.ld"),
           "-I", str(inc_dir), "-I", str(HERE)]
    cmd += args.gcc_opts.split()
    cmd += [str(s) for s in sources] + [str(s) for s in stubs] + ["-o", str(elf)]
    if run(cmd, out / "gcc.log"):
        sys.exit("assemble/link failed")
    sidecar_extra["steps"].append("link")
    sidecar_extra["debug_rom_bytes"] = check_debug_rom_budget(elf, mm)
    with open(out / "prog.dis", "w") as f:
        subprocess.run([tool("objdump"), "-d", str(elf)], stdout=f, check=False)
    with open(out / "prog.nm", "w") as f:
        subprocess.run([tool("nm"), "-n", str(elf)], stdout=f, check=False)

    # Step 3: image + sidecar
    if run([sys.executable, str(HERE / "gen_elf2mem.py"), str(elf), "--out-base", str(out / "prog")],
           out / "elf2mem.log"):
        sys.exit("elf2mem failed")
    side = out / "prog.sym.json"
    meta = json.loads(side.read_text())
    meta.update(sidecar_extra)
    meta["tools"] = {"gcc": tool_version([gcc, "--version"]),
                     "spike": tool_version([str(SPIKE), "--help"]) if SPIKE.exists() else "absent",
                     "gcc_march": GCC_ISA, "spike_isa": args.spike_isa}
    sidecar_extra["steps"].append("image")

    # Step 4: optional Spike sanity run
    if args.spike_check:
        if not SPIKE.exists():
            sys.exit(f"{SPIKE} missing; build it per docs/dv/SIM_RECIPE.md Section 11 or set GEN_SPIKE_BIN")
        entry = meta["entry"]
        cmd = ["timeout", str(args.spike_timeout), str(SPIKE), f"--isa={args.spike_isa}", *spike_cfg_opts(),
               spike_mem_opts(mm), f"--pc={entry}", "--log-commits",
               f"--log={out / 'spike_commits.log'}", str(elf)]
        rc = run(cmd, out / "spike_stdout.log")
        meta["spike_check"] = {"exit": rc, "commit_lines": sum(1 for _ in open(out / "spike_commits.log"))
                               if (out / "spike_commits.log").exists() else 0}
        sidecar_extra["steps"].append("spike_check")
        if rc != 0:
            side.write_text(json.dumps(meta, indent=2) + "\n")
            sys.exit(f"spike check failed (exit {rc})")
    side.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"OK seed={args.seed} steps={sidecar_extra['steps']} elf={elf} image={out / 'prog.vmem'} "
          f"entry={meta['entry']} words={meta['checksum']['count']} crc32={meta['checksum']['crc32']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
