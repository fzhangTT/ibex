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
SPIKE = ROOT / "tools/spike/bin/spike"
# Spike ISA string for this DUT (SN/architecture sections C5): ratified extensions the model has.
SPIKE_ISA = "rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs_zcb_zcmp_zicntr_zihpm_zicclsm"
SPIKE_OPTS = ["--priv=mu", "--pmpregions=16", "--pmpgranularity=4", "--triggers=1",
              "-m0x1a110000:0x1000,0x80000000:0x100000"]
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
    """Read a 32'h... default of a parameter from an SV file (single source of the memory map)."""
    m = re.search(rf"\b{name}\b\s*=\s*32'h([0-9a-fA-F_]+)", path.read_text())
    if not m:
        sys.exit(f"cannot find parameter {name} in {path}")
    return int(m.group(1).replace("_", ""), 16)


def check_link_constants(ld: Path) -> None:
    """gen_link.ld's MEMORY origins must equal the SV parameters they mirror; fail loud otherwise."""
    text = ld.read_text()
    origins = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^\s*(\w+)\s*\(\w+\)\s*:\s*ORIGIN\s*=\s*0x([0-9A-Fa-f]+)", text, re.M)}
    dm_halt = sv_param(SV_WRAPPER, "DmHaltAddr")
    boot = sv_param(SV_TB_PKG, "GEN_BOOT_ADDR_DEFAULT")
    first_fetch = (boot & 0xFFFFFF00) | 0x80   # {boot_addr_i[31:8], 8'h80}, rtl/ibex_if_stage.sv:243
    problems = []
    if origins.get("DM") != dm_halt:
        problems.append(f"DM origin 0x{origins.get('DM', 0):08x} != DmHaltAddr 0x{dm_halt:08x}")
    if origins.get("PROG") != first_fetch:
        problems.append(f"PROG origin 0x{origins.get('PROG', 0):08x} != first fetch 0x{first_fetch:08x}")
    if problems:
        sys.exit("gen_link.ld disagrees with the SV parameters: " + "; ".join(problems))


def build_generator(gen_build: Path, log: Path) -> None:
    target = materialize_target(gen_build / "target")
    cmd = [sys.executable, "run.py", "--co", "-si", "vcs", "-ct", str(target),
           "-ext", str(target / "user_extension"), "--isa", "rv32imc_zba_zbb_zbc_zbs",
           "--mabi", GCC_ABI, "-o", str(gen_build), "--cmp_opts=-licqueue"]
    if run(cmd, log, cwd=RISCV_DV):
        sys.exit("generator compile failed")


def generate(test: str, seed: int, gen_build: Path, sim_opts: str, log: Path) -> Path:
    target = materialize_target(gen_build / "target")
    cmd = [sys.executable, "run.py", "--so", "-si", "vcs", "-ct", str(target),
           "-ext", str(target / "user_extension"), "--isa", "rv32imc_zba_zbb_zbc_zbs",
           "--mabi", GCC_ABI, "-o", str(gen_build), "-tn", test, "--seed", str(seed),
           "-s", "gen", "--noclean"]
    if sim_opts:
        cmd.append(f"--sim_opts={sim_opts}")
    if run(cmd, log, cwd=RISCV_DV):
        sys.exit("generation failed")
    asms = sorted((gen_build / "asm_test").glob(f"{test}_*.S"), key=lambda p: p.stat().st_mtime)
    if not asms:
        sys.exit(f"no assembly produced for {test}")
    return asms[-1]


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
        asm = generate(args.test, args.seed, gen_build, args.sim_opts, out / "gen_run.log")
        shutil.copy(asm, prog_s)
        sidecar_extra["steps"].append("generate")
        sidecar_extra["generator_build"] = str(gen_build)
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
    check_link_constants(TARGET_SRC / "gen_link.ld")
    inc_dir = materialize_target(out / "target") / "user_extension"
    elf = out / "prog.elf"
    # A program that carries its own .debug_rom (relocated riscv-dv ROM or a directed one) must
    # not also link the default stub, or the two would both claim DmHaltAddr.
    has_debug_rom = any(".debug_rom" in p.read_text() for p in sources)
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
            sys.exit(f"{SPIKE} missing; build it per docs/dv/SIM_RECIPE.md Section 11")
        entry = meta["entry"]
        cmd = ["timeout", str(args.spike_timeout), str(SPIKE), f"--isa={args.spike_isa}", *SPIKE_OPTS,
               f"--pc={entry}", "--log-commits", f"--log={out / 'spike_commits.log'}", str(elf)]
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
