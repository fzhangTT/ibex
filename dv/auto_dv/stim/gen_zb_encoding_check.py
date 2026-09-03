#!/usr/bin/env python3
"""Which bitmanip mnemonics the lowRISC gcc 10.2 assembler accepts under -march=rv32imcb, and whether
the emitted encodings match the RTL decoder table (dv/auto_dv/docs/gen_rv32b_otearlgrey_encodings.md,
ENC; the expected fields below are transcribed from its rows 1-3). Evidence:
dv/auto_dv/evidence/gen_t023_stimulus_toolchain.md. Usage (ci/env.sh sourced):
    python3 dv/auto_dv/stim/gen_zb_encoding_check.py <workdir>
Exit 1 on any accepted-but-mismatching encoding.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

GCC = os.environ["RISCV_GCC"]
OBJDUMP = os.path.join(os.path.dirname(GCC), os.path.basename(GCC).replace("-gcc", "-objdump"))
MARCH = "rv32imcb"

# mnemonic -> (operands, expected fields per ENC). OP rows: f7, f3. OP-IMM rows: hi5, f3 (+ note).
OP_ROWS = {
    "sh1add": ("x1,x2,x3", "0010000", "010"), "sh2add": ("x1,x2,x3", "0010000", "100"),
    "sh3add": ("x1,x2,x3", "0010000", "110"),
    "andn": ("x1,x2,x3", "0100000", "111"), "orn": ("x1,x2,x3", "0100000", "110"),
    "xnor": ("x1,x2,x3", "0100000", "100"),
    "rol": ("x1,x2,x3", "0110000", "001"), "ror": ("x1,x2,x3", "0110000", "101"),
    "min": ("x1,x2,x3", "0000101", "100"), "max": ("x1,x2,x3", "0000101", "110"),
    "minu": ("x1,x2,x3", "0000101", "101"), "maxu": ("x1,x2,x3", "0000101", "111"),
    "pack": ("x1,x2,x3", "0000100", "100"), "packu": ("x1,x2,x3", "0100100", "100"),
    "packh": ("x1,x2,x3", "0000100", "111"),
    "bclr": ("x1,x2,x3", "0100100", "001"), "bset": ("x1,x2,x3", "0010100", "001"),
    "binv": ("x1,x2,x3", "0110100", "001"), "bext": ("x1,x2,x3", "0100100", "101"),
    "bfp": ("x1,x2,x3", "0100100", "111"),
    "grev": ("x1,x2,x3", "0110100", "101"), "gorc": ("x1,x2,x3", "0010100", "101"),
    "shfl": ("x1,x2,x3", "0000100", "001"), "unshfl": ("x1,x2,x3", "0000100", "101"),
    "xperm.n": ("x1,x2,x3", "0010100", "010"), "xperm.b": ("x1,x2,x3", "0010100", "100"),
    "xperm.h": ("x1,x2,x3", "0010100", "110"),
    "slo": ("x1,x2,x3", "0010000", "001"), "sro": ("x1,x2,x3", "0010000", "101"),
    "clmul": ("x1,x2,x3", "0000101", "001"), "clmulr": ("x1,x2,x3", "0000101", "010"),
    "clmulh": ("x1,x2,x3", "0000101", "011"),
    "zext.h": ("x1,x2", "0000100", "100"),  # = pack x1,x2,x0
}
# Zbt ternaries: instr[26:25] and f3; rs3 in [31:27].
TERNARY_ROWS = {
    "cmix": ("x1,x2,x3,x4", "11", "001"), "cmov": ("x1,x2,x3,x4", "11", "101"),
    "fsl": ("x1,x2,x3,x4", "10", "001"), "fsr": ("x1,x2,x3,x4", "10", "101"),
}
OPIMM_ROWS = {  # mnemonic -> (operands, hi5, f3, imm field constraint or None)
    "sloi": ("x1,x2,3", "00100", "001", None), "sroi": ("x1,x2,3", "00100", "101", None),
    "bclri": ("x1,x2,3", "01001", "001", None), "bseti": ("x1,x2,3", "00101", "001", None),
    "binvi": ("x1,x2,3", "01101", "001", None), "bexti": ("x1,x2,3", "01001", "101", None),
    "shfli": ("x1,x2,3", "00001", "001", None), "unshfli": ("x1,x2,3", "00001", "101", None),
    "clz": ("x1,x2", "01100", "001", "0000000"), "ctz": ("x1,x2", "01100", "001", "0000001"),
    "cpop": ("x1,x2", "01100", "001", "0000010"),
    "sext.b": ("x1,x2", "01100", "001", "0000100"), "sext.h": ("x1,x2", "01100", "001", "0000101"),
    "crc32.b": ("x1,x2", "01100", "001", "0010000"), "crc32.h": ("x1,x2", "01100", "001", "0010001"),
    "crc32.w": ("x1,x2", "01100", "001", "0010010"),
    "crc32c.b": ("x1,x2", "01100", "001", "0011000"), "crc32c.h": ("x1,x2", "01100", "001", "0011001"),
    "crc32c.w": ("x1,x2", "01100", "001", "0011010"),
    "rori": ("x1,x2,3", "01100", "101", None),
    "grevi": ("x1,x2,3", "01101", "101", None), "gorci": ("x1,x2,3", "00101", "101", None),
    "rev8": ("x1,x2", "01101", "101", "0011000"),   # grevi imm 24 -> instr[26:20] = 0011000
    "orc.b": ("x1,x2", "00101", "101", "0000111"),  # gorci imm 7
    "fsri": ("x1,x2,x3,3", None, "101", None),      # instr[26] = 1
}


def assemble(mn: str, ops: str, work: Path):
    src = work / f"zb_{mn.replace('.', '_')}.S"
    obj = src.with_suffix(".o")
    src.write_text(f".text\n{mn} {ops}\n")
    r = subprocess.run([GCC, "-c", f"-march={MARCH}", "-mabi=ilp32", str(src), "-o", str(obj)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "assembler error"
    d = subprocess.run([OBJDUMP, "-d", str(obj)], capture_output=True, text=True).stdout
    m = re.search(r"^\s*0:\s+([0-9a-f]{8})\s", d, re.M)
    return (int(m.group(1), 16) if m else None), None


def bits(v: int, hi: int, lo: int) -> str:
    return format((v >> lo) & ((1 << (hi - lo + 1)) - 1), f"0{hi - lo + 1}b")


def main() -> int:
    work = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    work.mkdir(parents=True, exist_ok=True)
    rows = []
    n_ok = n_mis = n_rej = 0
    for mn, (ops, f7, f3) in OP_ROWS.items():
        enc, err = assemble(mn, ops, work)
        if enc is None:
            rows.append((mn, "REJECTED", err)); n_rej += 1; continue
        got = (bits(enc, 31, 25), bits(enc, 14, 12), bits(enc, 6, 0))
        ok = got == (f7, f3, "0110011") and (mn != "zext.h" or bits(enc, 24, 20) == "00000")
        rows.append((mn, f"0x{enc:08x}", f"f7 {got[0]} f3 {got[1]} opc {got[2]} {'MATCH' if ok else 'MISMATCH vs ENC ' + f7 + '/' + f3}"))
        n_ok += ok; n_mis += (not ok)
    for mn, (ops, b2625, f3) in TERNARY_ROWS.items():
        enc, err = assemble(mn, ops, work)
        if enc is None:
            rows.append((mn, "REJECTED", err)); n_rej += 1; continue
        got = (bits(enc, 26, 25), bits(enc, 14, 12), bits(enc, 6, 0))
        ok = got == (b2625, f3, "0110011")
        rows.append((mn, f"0x{enc:08x}", f"[26:25] {got[0]} f3 {got[1]} opc {got[2]} {'MATCH' if ok else 'MISMATCH vs ENC ' + b2625 + '/' + f3}"))
        n_ok += ok; n_mis += (not ok)
    for mn, (ops, hi5, f3, immc) in OPIMM_ROWS.items():
        enc, err = assemble(mn, ops, work)
        if enc is None:
            rows.append((mn, "REJECTED", err)); n_rej += 1; continue
        got_hi5, got_f3, got_opc = bits(enc, 31, 27), bits(enc, 14, 12), bits(enc, 6, 0)
        if mn == "fsri":
            ok = bits(enc, 26, 26) == "1" and got_f3 == f3 and got_opc == "0010011"
        else:
            ok = got_hi5 == hi5 and got_f3 == f3 and got_opc == "0010011"
            if immc is not None:
                ok = ok and bits(enc, 26, 20) == immc
        rows.append((mn, f"0x{enc:08x}", f"hi5 {got_hi5} [26:20] {bits(enc, 26, 20)} f3 {got_f3} opc {got_opc} {'MATCH' if ok else 'MISMATCH vs ENC'}"))
        n_ok += ok; n_mis += (not ok)
    print(f"# march={MARCH} gcc={GCC}")
    print(f"# accepted+match {n_ok}, accepted+mismatch {n_mis}, rejected {n_rej}")
    for mn, enc, note in rows:
        print(f"{mn:10s} {enc:12s} {note}")
    return 1 if n_mis else 0


if __name__ == "__main__":
    sys.exit(main())
