#!/usr/bin/env python3
"""gen_bit_draft_prog: per-seed program generator for gen_test_bit_draft (group gen_bit_draft).

Built item: TP-BIT-016 (generic grevi / gorci / grev / gorc over the 32 control values, brev8 = grevi 7,
with the ratified aliases rev8 = grevi 24 and orc.b = gorci 7). The other items of the group name draft
ops (pack/packh/packu, slo/sro, shfl/unshfl, xperm, cmov/cmix, fsl/fsr/fsri, bfp, crc32*) that the TB's
ISA comparator cannot yet reference (dv/auto_dv/isa/gen_isa_shim.cc gen_isa_exec_reference serves only
grev/gorc), so this program never emits them.

plan(seed, red=False) draws the scenario from random.Random(f"{seed}:program:bit_draft"): the op mix,
register indices (W4), rs1 operand classes (W1), control words (W9), rs2 upper bits of the register forms
(W3), operand chaining and the unrelated filler instructions. The expected rd of every op comes from the
Python grev32/gorc32 below, written from the draft Bitmanip text (tools/specs/riscv-bitmanip/texsrc/
bext.tex "Generalized Reverse" and "Generalized OR-Combine"), never from the RTL. red=True makes emit()
deviate on exactly one intent (one grevi/gorci immediate differs from the plan) while the expectations
stay true, so the test's fire-check must fail.

emit(plan) renders RV32IMC(B) assembly for the lowRISC gcc 10.2 (-march=rv32imcb): every op stores its
rd into a result buffer in .data as it goes; the program then replays the buffer to GEN_MM_EOT_ADDR
(one report word per op, plan order) and ends with tohost 1.

CLI: python3 gen_bit_draft_prog.py --seed N --out <file.S> [--red]
"""
import argparse
import random
from dataclasses import dataclass, field

MASK32 = 0xFFFFFFFF
PROGRAM_TAG = "bit_draft"
CTRL_BITS = 5                      # log2(XLEN) control bits of grev/gorc on RV32
CANONICAL_CTRL = (7, 24, 31)       # brev8 / rev8 / rev (W9 weight 2)
RANDOM_KINDS = ("grevi", "gorci", "grev", "gorc")
# Ratified or named aliases pinned once per seed inside the random stream (rev.b is the draft name of
# the brev8 encoding, grevi 7; the toolchain has no brev8 mnemonic).
ALIAS_KINDS = {"rev8": ("grevi", 24), "orc.b": ("gorci", 7), "rev.b": ("grevi", 7)}
IMM_KINDS = ("grevi", "gorci")
N_RANDOM_OPS = (36, 44)            # random ops per seed (inclusive range)
CHAIN_PROB = 0.25                  # rs1 = the previous op's rd (forwarding path, no li)

# gen_test_plan.md "Layer-1 weight tables" W1: 32-bit register operand classes.
W1 = {"zero": 1, "all_ones": 1, "int_min": 1, "int_max": 1, "one": 1, "p16": 1, "two": 1, "e0000000": 1,
      "byte_msb": 1, "half_msb": 1, "single_bit": 1, "alt": 1, "bytes_01020304": 1, "distinct_lanes": 1,
      "pos_rand": 4, "neg_rand": 4}
# W3, register-form upper bits rs2[31:5]: zero 4, the named values 1 each, other_nonzero 2.
W3_UPPER = {"zero": 4, "v32": 1, "v33": 1, "vFFFFFFE0": 1, "v80000000": 1, "vFFFFFFFF": 1, "other_nonzero": 2}
# W9, grev/gorc control words: uniform over 0..31, the canonical values weight 2.
W9_CTRL = {c: (2 if c in CANONICAL_CTRL else 1) for c in range(1 << CTRL_BITS)}
# W4 register-index fractions used here (rd = x0, rs1 == rs2, rs2 == rd, x0 as a source).
W4_RD_X0 = 1 / 16
W4_RS_SAME = 1 / 16
W4_RS2_EQ_RD = 1 / 8
W4_X0_SRC = 1 / 16


def _pair_mask(width):
    """Bits of the lower group of every adjacent pair of `width`-bit groups."""
    m = 0
    for b in range(0, 32, 2 * width):
        m |= ((1 << width) - 1) << b
    return m


def grev32(x, k):
    """bext.tex Generalized Reverse: for each control bit i set, swap each adjacent pair of 2^i-bit groups."""
    for i in range(CTRL_BITS):
        if (k >> i) & 1:
            w = 1 << i
            lo = _pair_mask(w)
            hi = ~lo & MASK32
            x = (((x & lo) << w) | ((x & hi) >> w)) & MASK32
    return x


def gorc32(x, k):
    """bext.tex Generalized OR-Combine: as grev, but OR the pair together and write it into both positions."""
    for i in range(CTRL_BITS):
        if (k >> i) & 1:
            w = 1 << i
            lo = _pair_mask(w)
            hi = ~lo & MASK32
            x = (x | ((x & lo) << w) | ((x & hi) >> w)) & MASK32
    return x


REFERENCE = {"grevi": grev32, "gorci": gorc32, "grev": grev32, "gorc": gorc32}


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def operand_value(rng, cls):
    if cls == "zero":
        return 0
    if cls == "all_ones":
        return MASK32
    if cls == "int_min":
        return 0x80000000
    if cls == "int_max":
        return 0x7FFFFFFF
    if cls == "one":
        return 1
    if cls == "p16":
        return 1 << 16
    if cls == "two":
        return 2
    if cls == "e0000000":
        return 0xE0000000
    if cls == "byte_msb":
        return 0x80808080
    if cls == "half_msb":
        return 0x80008000
    if cls == "single_bit":
        return 1 << rng.randrange(32)
    if cls == "alt":
        return rng.choice((0x55555555, 0xAAAAAAAA))
    if cls == "bytes_01020304":
        return 0x01020304
    if cls == "distinct_lanes":
        v = 0
        for nib in rng.sample(range(16), 8):
            v = (v << 4) | nib
        return v
    if cls == "pos_rand":
        return rng.randrange(1, 0x80000000)
    if cls == "neg_rand":
        return rng.randrange(0x80000000, 1 << 32)
    raise ValueError(cls)


def rs2_value(rng, cls, ctrl):
    """Full rs2 of a register form: the W3 upper-bit class around the drawn control (the literal classes
    32, 33 and all-ones fix rs2[4:0] themselves); returns (rs2, effective control)."""
    if cls == "zero":
        v = ctrl
    elif cls == "v32":
        v = 32
    elif cls == "v33":
        v = 33
    elif cls == "vFFFFFFE0":
        v = 0xFFFFFFE0 | ctrl
    elif cls == "v80000000":
        v = 0x80000000 | ctrl
    elif cls == "vFFFFFFFF":
        v = MASK32
    elif cls == "other_nonzero":
        v = (rng.randrange(1, 1 << 27) << 5) | ctrl
    else:
        raise ValueError(cls)
    return v, v & ((1 << CTRL_BITS) - 1)


@dataclass
class Op:
    idx: int
    kind: str                # grevi gorci grev gorc rev8 orc.b rev.b
    base: str                # the reference op: grevi gorci grev gorc
    rd: int
    rs1: int
    rs2: int                 # register forms only (0 otherwise)
    rs1_val: int
    rs2_val: int             # register forms only
    ctrl: int                # effective control word 0..31
    rs1_class: str
    upper_class: str         # register forms only
    chained: bool            # rs1 carries the previous op's rd (no li)
    expect: int
    fillers: list = field(default_factory=list)

    @property
    def is_imm(self):
        return self.base in IMM_KINDS


@dataclass
class Plan:
    seed: int
    red: bool
    eot_reg: int
    buf_reg: int
    ops: list
    reports: list            # expected rd values, one per op, plan order
    k: int
    min_retired: int
    red_idx: int             # op whose immediate the red program deviates on (-1 when not red)
    red_ctrl: int
    items: dict              # per-item expectations the test asserts


def program_rng(seed):
    return random.Random(f"{int(seed)}:program:{PROGRAM_TAG}")


FILLER_FORMS = ("addi", "xori", "andi", "ori", "add", "sub", "sll", "xor", "lui")


def _filler(rng, pool):
    form = rng.choice(FILLER_FORMS)
    rd, ra, rb = (rng.choice(pool) for _ in range(3))
    if form in ("addi", "xori", "andi", "ori"):
        return f"{form} x{rd}, x{ra}, {rng.randrange(-2048, 2048)}"
    if form == "lui":
        return f"lui x{rd}, 0x{rng.randrange(1 << 20):x}"
    return f"{form} x{rd}, x{ra}, x{rb}"


def plan(seed, red=False):
    rng = program_rng(seed)
    eot_reg, buf_reg = rng.sample(range(5, 32), 2)        # x5..x31: gp/t5 stay free for the tohost tail
    pool = [r for r in range(1, 32) if r not in (eot_reg, buf_reg)]
    kinds = [rng.choice(RANDOM_KINDS) for _ in range(rng.randint(*N_RANDOM_OPS))]
    for alias in ALIAS_KINDS:
        kinds.insert(rng.randrange(len(kinds) + 1), alias)
    ops = []
    prev = None
    for idx, kind in enumerate(kinds):
        base, fixed_ctrl = ALIAS_KINDS.get(kind, (kind, None))
        is_imm = base in IMM_KINDS
        chained = prev is not None and prev.rd != 0 and rng.random() < CHAIN_PROB
        rd = 0 if rng.random() < W4_RD_X0 else rng.choice(pool)
        if chained:
            rs1, rs1_val, rs1_class = prev.rd, prev.expect, "chain_prev"
        elif rng.random() < W4_X0_SRC:
            rs1, rs1_val, rs1_class = 0, 0, "x0_src"
        else:
            rs1 = rng.choice(pool)
            rs1_class = weighted(rng, W1)
            rs1_val = operand_value(rng, rs1_class)
        ctrl = fixed_ctrl if fixed_ctrl is not None else weighted(rng, W9_CTRL)
        rs2, rs2_val, upper_class = 0, 0, ""
        if not is_imm:
            upper_class = weighted(rng, W3_UPPER)
            r = rng.random()
            if r < W4_RS_SAME and rs1 != 0:
                rs2, rs2_val, ctrl, upper_class = rs1, rs1_val, rs1_val & 31, "same_as_rs1"
            else:
                rs2 = rd if (r < W4_RS_SAME + W4_RS2_EQ_RD and rd != 0 and rd != rs1) else rng.choice([x for x in pool if x != rs1])
                rs2_val, ctrl = rs2_value(rng, upper_class, ctrl)
        protect = {prev.rd} if chained else set()
        fill_pool = [x for x in pool if x not in protect]
        fillers = [_filler(rng, fill_pool) for _ in range(rng.randrange(3))]
        expect = REFERENCE[base](rs1_val, ctrl) if rd != 0 else 0
        op = Op(idx, kind, base, rd, rs1, rs2, rs1_val, rs2_val, ctrl, rs1_class, upper_class, chained, expect, fillers)
        ops.append(op)
        prev = op
    reports = [op.expect for op in ops]
    # retirement floor: every emitted straight-line instruction counted once (li/la expand to >= 1)
    n_insn = 2 + sum(len(op.fillers) + (0 if op.chained or op.rs1 == 0 else 1)
                     + (0 if op.is_imm or op.rs2 == op.rs1 else 1) + 2 for op in ops) + 2 * len(ops) + 3
    red_idx, red_ctrl = -1, -1
    if red:
        for op in ops:
            if op.is_imm and op.rd != 0:
                for c in [op.ctrl ^ 1] + [c for c in range(32) if c != op.ctrl]:
                    if REFERENCE[op.base](op.rs1_val, c) != op.expect:
                        red_idx, red_ctrl = op.idx, c
                        break
            if red_idx >= 0:
                break
        assert red_idx >= 0, "red: no immediate-form op whose result depends on its control"
    items = {"TP-BIT-016": {
        "ops_by_base": {b: [op.idx for op in ops if op.base == b] for b in RANDOM_KINDS},
        "alias_ops": [op.idx for op in ops if op.kind in ALIAS_KINDS],
        "controls": sorted({(op.base, op.ctrl) for op in ops}),
        "single_bit_ops": [op.idx for op in ops if op.rs1_class == "single_bit"],
        "nonzero_upper_ops": [op.idx for op in ops if not op.is_imm and (op.rs2_val >> CTRL_BITS) != 0],
        "chained_ops": [op.idx for op in ops if op.chained],
    }}
    return Plan(seed, red, eot_reg, buf_reg, ops, reports, len(reports), n_insn, red_idx, red_ctrl, items)


def _op_line(plan_, op):
    ctrl = op.ctrl
    if plan_.red and op.idx == plan_.red_idx:
        ctrl = plan_.red_ctrl
    if op.kind in ALIAS_KINDS and ctrl == op.ctrl:
        return f"{op.kind} x{op.rd}, x{op.rs1}"
    if op.is_imm:
        return f"{op.base} x{op.rd}, x{op.rs1}, {ctrl}"
    return f"{op.base} x{op.rd}, x{op.rs1}, x{op.rs2}"


def emit(plan_):
    p = plan_
    out = [f"# gen_bit_draft_prog.py seed={p.seed} red={int(p.red)}: generated, do not edit "
           f"(k={p.k} reports, min_retired={p.min_retired})",
           '.include "gen_mmio_map.h"', ".section .text", ".globl _start", "_start:",
           f"  li   x{p.eot_reg}, GEN_MM_EOT_ADDR", f"  la   x{p.buf_reg}, gen_bit_results"]
    for op in p.ops:
        red_mark = "  RED: immediate deviates" if (p.red and op.idx == p.red_idx) else ""
        out.append(f"  # op {op.idx}: {op.kind} ctrl={op.ctrl} rs1={op.rs1_class} 0x{op.rs1_val:08x}"
                   + (f" rs2={op.upper_class} 0x{op.rs2_val:08x}" if not op.is_imm else "")
                   + f" -> 0x{op.expect:08x}{red_mark}")
        out += [f"  {f}" for f in op.fillers]
        if not op.chained and op.rs1 != 0:
            out.append(f"  li   x{op.rs1}, 0x{op.rs1_val:08x}")
        if not op.is_imm and op.rs2 != op.rs1:
            out.append(f"  li   x{op.rs2}, 0x{op.rs2_val:08x}")
        out.append(f"  {_op_line(p, op)}")
        out.append(f"  sw   x{op.rd}, {4 * op.idx}(x{p.buf_reg})")
    out.append("  # report replay: one EOT-register store per op, plan order")
    tmp = [r for r in range(5, 32) if r not in (p.eot_reg, p.buf_reg)][:2]
    for op in p.ops:
        t = tmp[op.idx % 2]
        out.append(f"  lw   x{t}, {4 * op.idx}(x{p.buf_reg})")
        out.append(f"  sw   x{t}, 0(x{p.eot_reg})")
    out += ["  li   gp, 1", "  la   t5, tohost", "  sw   gp, 0(t5)", "1:", "  j    1b", "",
            ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost",
            "fromhost: .dword 0", ".align 4", f"gen_bit_results: .fill {p.k}, 4, 0", ".align 2",
            ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--red", action="store_true")
    a = ap.parse_args()
    p = plan(a.seed, a.red)
    text = emit(p)
    assert all(ord(ch) < 128 for ch in text), "non-ASCII in the generated program"
    with open(a.out, "w") as f:
        f.write(text)
    print(f"gen_bit_draft_prog seed={p.seed} red={int(p.red)} k={p.k} min_retired={p.min_retired} "
          f"red_idx={p.red_idx} -> {a.out}")


if __name__ == "__main__":
    main()
