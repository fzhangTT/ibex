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
import sys
from pathlib import Path
from typing import Any

import gen_flow_const as C
import gen_flow_util as U


def image_plusarg_names() -> tuple[str, str]:
    """The two image plusarg strings, read from the SV constants home; fail loud if not declared."""
    by_ident = {ident: name for name, ident in C.sv_plusarg_names().items()}
    missing = [i for i in (C.SV_PLUSARG_MEM_IMAGE, C.SV_PLUSARG_MEM_IMAGE_CRC32) if i not in by_ident]
    if missing:
        U.die(f"{C.TB_PKG_SV.name} does not declare {missing}; the memory model's image plusargs must land before a "
              "program-driven test can run")
    return by_ident[C.SV_PLUSARG_MEM_IMAGE], by_ident[C.SV_PLUSARG_MEM_IMAGE_CRC32]


def build_program(prog: dict[str, Any], run_seed: int, out: Path, log: Path, timeout_s: int = 1800) -> dict[str, Any]:
    """Run gen_program.py; return the record for result.yaml (paths, digests, seed used)."""
    if not C.PROGRAM_TOOL.is_file():
        U.die(f"{C.PROGRAM_TOOL} missing")
    seed = run_seed if prog.get("seed", C.PROGRAM_SEED_RUN) == C.PROGRAM_SEED_RUN else int(prog["seed"])
    argv = [sys.executable, str(C.PROGRAM_TOOL), "--seed", str(seed), "--out", str(out)]
    if prog.get("riscv_dv_test"):
        argv += ["--test", str(prog["riscv_dv_test"])]
    else:
        argv += ["--directed", *[str(C.REPO_ROOT / d) for d in prog["directed"]]]
    gen_build = C.site_value("riscv_dv_gen_build")
    if gen_build and prog.get("riscv_dv_test"):
        argv += ["--gen-build", gen_build]
    if prog.get("spike_check"):
        argv.append("--spike-check")
    argv += [str(x) for x in (prog.get("extra_args") or [])]
    out.mkdir(parents=True, exist_ok=True)
    # The build-configuration name has one home (gen_flow_const.BUILD_CONFIG); it is exported so the
    # stimulus tool can read it instead of carrying its own constant (owner of gen_program.py decides).
    env = dict(os.environ, **{C.ENV_BUILD_CONFIG: C.BUILD_CONFIG})
    rc, wall, timed_out = U.run_bounded(argv, cwd=C.REPO_ROOT, log_path=log, timeout_s=timeout_s, env=env)
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
            "vmem": str(vmem), "vmem_sha256": U.sha256_file(vmem), "sidecar": str(sidecar), "crc32": crc,
            "word_count": (side.get("checksum") or {}).get("count"), "entry": side.get("entry"),
            "wall_s": round(wall, 1), "log": str(log)}


def image_plusargs(rec: dict[str, Any]) -> list[str]:
    img, crc = image_plusarg_names()
    crc_val = rec["crc32"]
    crc_txt = crc_val if isinstance(crc_val, str) else f"0x{int(crc_val):08x}"
    return [f"+{img}={rec['vmem']}", f"+{crc}={crc_txt}"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--riscv-dv-test")
    ap.add_argument("--directed", nargs="*")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--spike-check", action="store_true")
    ap.add_argument("--print-plusargs", action="store_true", help="also print the image plusargs (needs the SV names)")
    a = ap.parse_args()
    if bool(a.riscv_dv_test) == bool(a.directed):
        ap.error("exactly one of --riscv-dv-test / --directed is required")
    prog = {"riscv_dv_test": a.riscv_dv_test, "directed": a.directed, "seed": a.seed, "spike_check": a.spike_check}
    rec = build_program(prog, a.seed, a.out.resolve(), a.out.resolve() / "gen_program_driver.log")
    for k, v in rec.items():
        print(f"{k}: {v}")
    if a.print_plusargs:
        print("plusargs:", " ".join(image_plusargs(rec)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
