#!/usr/bin/env python3
"""Program step of a run: build the test's memory image with dv/auto_dv/stim/gen_program.py
(riscv-dv generated or directed) into <run dir>/program/, then hand the image and its checksum to
the simulation through the plusargs TB Infra's memory model declares in gen_tb_pkg.sv
(PLUSARG_MEM_IMAGE, PLUSARG_MEM_IMAGE_CRC32). One seed: `program.seed: run` uses the run seed;
an integer pins the program while the run seed still drives the TB (bring-up milestones).

Testlist block:
    program:
      riscv_dv_test: gen_rand_smoke     # entry of dv/auto_dv/stim/gen_riscv_dv_target/gen_testlist.yaml
      # directed: [dv/auto_dv/stim/gen_directed/boot.S]   # instead of riscv_dv_test
      seed: run                          # or a fixed integer
      extra_args: []                     # passed to gen_program.py verbatim
      spike_check: false                 # --spike-check

Usage (standalone, e.g. to pre-generate):
    gen_stim.py --riscv-dv-test gen_rand_smoke --seed 1 --out DIR [--gen-build DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U


def generator_env() -> dict[str, str]:
    """Environment of the program stages (generator, gen_program.py): the caller's minus JOB_ENV_UNSET (no PYTHONPATH,
    so a generator resolves its own repository root), PYTHONHASHSEED pinned, the build-configuration name."""
    env = {k: v for k, v in os.environ.items() if k not in C.JOB_ENV_UNSET}
    env.update(PYTHONHASHSEED="0", **{C.ENV_BUILD_CONFIG: C.BUILD_CONFIG})
    return env


def build_program(prog: dict[str, Any], run_seed: int, out: Path, log: Path, timeout_s: int = 1800) -> dict[str, Any]:
    """Run gen_program.py; return the record for result.yaml (paths, digests, seed used)."""
    if not C.PROGRAM_TOOL.is_file():
        U.die(f"{C.PROGRAM_TOOL} missing")
    seed = run_seed if prog.get("seed", C.PROGRAM_SEED_RUN) == C.PROGRAM_SEED_RUN else int(prog["seed"])
    # A fresh program directory every time: nothing stale (a previous source or image) can pass for this run's.
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    # Pinned hash seed: set iteration and string hashing in a generator or in gen_program.py must not vary the
    # program for one seed. The build-configuration name has one home (gen_flow_const.BUILD_CONFIG).
    env = generator_env()
    generated: dict[str, Any] = {}
    if prog.get("generator"):
        # A per-seed program generator (Test Writer): everything it emits derives from --seed, so the
        # source it writes is the one directed input of the program tool; the seed binding is by construction.
        src = out / C.PROGRAM_GENERATOR_SOURCE
        gen_log = out / "generator.log"
        gen_argv = [sys.executable, str(C.SOURCE_ROOT / prog["generator"]), "--seed", str(seed), "--out", str(src),
                    *[str(x) for x in (prog.get("generator_args") or [])]]
        grc, gwall, gto = U.run_bounded(gen_argv, cwd=C.SOURCE_ROOT, log_path=gen_log, timeout_s=timeout_s, env=env)
        # The program directory was emptied just before this invocation, so a present, non-empty source was
        # written by it (no clock comparison across filesystems).
        fresh = src.is_file() and src.stat().st_size > 0
        if grc != 0 or gto or not fresh:
            U.die(f"program generator failed (rc={grc}, timed_out={gto}, source written by this invocation={fresh}); see {gen_log}")
        generated = {"generator": prog["generator"], "generator_args": list(prog.get("generator_args") or []),
                     "generator_command": " ".join(gen_argv), "generator_source": str(src),
                     "generator_source_sha256": U.sha256_file(src), "generator_wall_s": round(gwall, 1),
                     "generator_log": str(gen_log)}
        sources = [str(src)]
    argv = [sys.executable, str(C.PROGRAM_TOOL), "--seed", str(seed), "--out", str(out)]
    if prog.get("riscv_dv_test"):
        argv += ["--test", str(prog["riscv_dv_test"])]
    elif prog.get("generator"):
        argv += ["--directed", *sources]
    else:
        argv += ["--directed", *[str(C.SOURCE_ROOT / d) for d in prog["directed"]]]
    gen_build = C.site_value("riscv_dv_gen_build")
    if gen_build and prog.get("riscv_dv_test"):
        argv += ["--gen-build", gen_build]
    if prog.get("spike_check"):
        argv.append("--spike-check")
    argv += [str(x) for x in (prog.get("extra_args") or [])]
    rc, wall, timed_out = U.run_bounded(argv, cwd=C.SOURCE_ROOT, log_path=log, timeout_s=timeout_s, env=env)
    vmem = out / C.PROGRAM_VMEM
    sidecar = out / C.PROGRAM_SIDECAR
    if rc != 0 or timed_out or not vmem.is_file() or not sidecar.is_file():
        U.die(f"gen_program.py failed (rc={rc}, timed_out={timed_out}); see {log}")
    side = json.loads(sidecar.read_text(encoding="utf-8"))
    crc = (side.get("checksum") or {}).get("crc32")
    if crc is None:
        U.die(f"{sidecar}: no checksum.crc32")
    return {"tool": str(C.PROGRAM_TOOL), "command": " ".join(argv), "seed": seed, "seed_source":
            "run" if prog.get("seed", C.PROGRAM_SEED_RUN) == C.PROGRAM_SEED_RUN else "fixed",
            "riscv_dv_test": prog.get("riscv_dv_test"), "directed": prog.get("directed"), "gen_build": gen_build,
            **generated,
            "vmem": str(vmem), "vmem_sha256": U.sha256_file(vmem), "sidecar": str(sidecar), "crc32": crc,
            "word_count": (side.get("checksum") or {}).get("count"), "entry": side.get("entry"),
            "wall_s": round(wall, 1), "log": str(log)}


def image_plusargs(rec: dict[str, Any]) -> list[str]:
    """The image plusarg set the TB expects, produced by TB Infra's own helper
    dv/auto_dv/gen_tb/gen_image.py (GenImage(<vmem>).plusargs(): image, crc32, word count, boot address,
    tohost address; names from gen_tb_knobs.yaml) so the keys are never re-typed here. No fallback: the
    TB rejects any other composition, so a missing helper fails here by name; a missing dependency
    inside the helper propagates unchanged."""
    import importlib
    if str(C.SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(C.SOURCE_ROOT))
    try:
        mod = importlib.import_module(C.IMAGE_HELPER_MODULE)
    except ModuleNotFoundError as e:
        if e.name and (C.IMAGE_HELPER_MODULE == e.name or C.IMAGE_HELPER_MODULE.startswith(e.name + ".")):
            U.die(f"{C.IMAGE_HELPER_MODULE} is not importable ({e}); TB Infra's image helper must be present")
        raise
    U.require_under_source_root(mod, C.IMAGE_HELPER_MODULE)
    args = list(mod.GenImage(rec["vmem"]).plusargs())
    rec["image_plusargs_source"] = f"{C.IMAGE_HELPER_MODULE} GenImage.plusargs()"
    return args


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--riscv-dv-test")
    ap.add_argument("--directed", nargs="*")
    ap.add_argument("--generator", help="clone-relative per-seed program generator (writes --out <file.S>)")
    ap.add_argument("--generator-arg", action="append", default=[], help="extra generator argument (repeatable)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--spike-check", action="store_true")
    ap.add_argument("--print-plusargs", action="store_true", help="also print the image plusargs (needs the SV names)")
    a = ap.parse_args()
    if sum(bool(x) for x in (a.riscv_dv_test, a.directed, a.generator)) != 1:
        ap.error("exactly one of --riscv-dv-test / --directed / --generator is required")
    if a.generator and U.clone_relative_file(a.generator) is None:
        ap.error(f"--generator {a.generator!r} must be a clone-relative path (no .., no symlink out of the clone) to an existing script")
    prog = {"riscv_dv_test": a.riscv_dv_test, "directed": a.directed, "generator": a.generator,
            "generator_args": a.generator_arg, "seed": a.seed, "spike_check": a.spike_check}
    rec = build_program(prog, a.seed, a.out.resolve(), a.out.resolve() / "gen_program_driver.log")
    for k, v in rec.items():
        print(f"{k}: {v}")
    if a.print_plusargs:
        print("plusargs:", " ".join(image_plusargs(rec)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
