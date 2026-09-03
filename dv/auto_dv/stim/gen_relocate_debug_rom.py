#!/usr/bin/env python3
"""Move a riscv-dv generated debug ROM into the .debug_rom section that gen_link.ld places at
DmHaltAddr, with the debug-exception entry at DmHaltAddr + 8.

riscv-dv (support_debug_mode = 1) emits the debug ROM inside .text as a self-contained block:
    debug_rom:        ...          (entry code, optional debug sub-programs, single-step logic)
    debug_end:        ...  dret
    debug_exception:  ...  dret
    instr_end:        nop
Ibex enters debug at the fixed parameter DmHaltAddr and takes debug-mode exceptions at
DmExceptionAddr = DmHaltAddr + 8 (dv/auto_dv/docs/gen_component_api_dut_top.md), so the block must
live in .debug_rom. This script inserts, before `debug_rom:`, a section switch plus an 8-byte
uncompressed header (`j debug_rom`; `nop`; `j debug_exception`) and, before `instr_end:`, a switch
back to .text. Everything the block references (its own labels, `la` to .text symbols) keeps
working because the block moves as a unit and riscv-dv calls its sub-programs with `la` + `jalr`.
The header symbols match gen_debug_rom_stub.S so sidecars and the TB see the same names; a program
processed here must be linked WITHOUT gen_debug_rom_stub.S (gen_program.py does that).

Usage: gen_relocate_debug_rom.py <prog.S> [--in-place | -o <out.S>]
Exit 0: relocated, or no debug ROM present (nothing to do, reported). Exit 1: malformed block.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADER = """.section .debug_rom, "ax", @progbits
.option push
.option norvc
.globl gen_debug_rom_entry
gen_debug_rom_entry:
                  j debug_rom
                  nop
.globl gen_debug_exception_entry
gen_debug_exception_entry:
                  j debug_exception
.option pop
"""
FOOTER = ".section .text\n"
LABEL = re.compile(r"^\s*([A-Za-z_][A-Za-z_0-9]*):")


def relocate(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    idx = {}
    for i, l in enumerate(lines):
        m = LABEL.match(l)
        if m and m.group(1) in ("debug_rom", "debug_end", "debug_exception", "instr_end"):
            idx.setdefault(m.group(1), i)
    if "debug_rom" not in idx:
        return text, "no debug_rom label: nothing to relocate"
    for need in ("debug_exception", "instr_end"):
        if need not in idx:
            raise ValueError(f"debug_rom present but {need} label missing")
    r, e, x = idx["debug_rom"], idx["debug_exception"], idx["instr_end"]
    if not (r < e < x):
        raise ValueError(f"unexpected label order debug_rom={r} debug_exception={e} instr_end={x}")
    # Reject a block that already carries a section directive (already processed or foreign).
    for l in lines[r:x]:
        if l.strip().startswith(".section"):
            raise ValueError("section directive inside the debug block; already relocated?")
    out = lines[:r] + [HEADER] + lines[r:x] + [FOOTER] + lines[x:]
    return "".join(out), f"relocated lines {r + 1}-{x} ({x - r} lines) into .debug_rom"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--in-place", action="store_true")
    g.add_argument("-o", "--out", type=Path)
    args = ap.parse_args()
    try:
        new, note = relocate(args.src.read_text())
    except ValueError as err:
        print(f"ERROR: {args.src}: {err}", file=sys.stderr)
        return 1
    dst = args.src if args.in_place else args.out
    dst.write_text(new)
    print(f"{args.src}: {note} -> {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
