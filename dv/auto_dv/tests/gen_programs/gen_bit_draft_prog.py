#!/usr/bin/env python3
"""gen_bit_draft_prog: per-seed program generator for gen_test_bit_draft (group gen_bit_draft).

Built item: TP-BIT-016 (generic grevi / gorci / grev / gorc over the 32 control values, brev8 = grevi 7, with the
ratified aliases rev8 = grevi 24 and orc.b = gorci 7). Blocked items, owner TB Infra (T-102 item 4: gen_isa_exec_reference
in dv/auto_dv/isa/gen_isa_shim.cc lacks pack/packh/packu, slo/sro(i), shfl/unshfl(i), xperm.n/.b/.h, cmov/cmix, fsl/fsr/fsri,
bfp, crc32*/crc32c*): TP-BIT-011 and TP-BIT-022..TP-BIT-033. No alternative exists until that shim extension lands (any
other draft op raises uvm_error isa_rd), so this program never emits those ops.

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:bit_draft"). The op stream
is the directed floor shuffled into weighted random extras: the floor holds one op per (base, control) pair (grevi and
gorci immediates 0..31, grev and gorc rs2[4:0] 0..31) plus the alias forms rev8 / orc.b / rev.b, every floor op
non-vacuous by construction (rd != x0, rs1 operand from W1 minus the control-insensitive classes zero and all_ones, so its
result constrains the control), one floor op per base with a single-bit operand and one register-form floor op per base
with nonzero rs2 upper bits. The N_RANDOM_OPS extras keep the full W1 / W3 / W4 / W9 freedom (rd = x0, x0 source,
rs1 == rs2, zero and all-ones operands, canonical control weights); the test counts those vacuous compares separately.
Register indices (W4), operand chaining and unrelated filler instructions are randomized throughout. The expected rd of
every op comes from the Python grev32/gorc32 below, written from the draft Bitmanip text
(tools/specs/riscv-bitmanip/texsrc/bext.tex "Generalized Reverse" and "Generalized OR-Combine"), never from the RTL.

Red fixtures deviate the PROGRAM on one intent while the expectations stay true: `--red [--red-item ID[:SEL]]`; without
--red-item the seed draws the item among BUILT_ITEMS. TP-BIT-016:imm (the default selector) emits one generic gorci op,
whose control another op also carries, with a different immediate so only the gorci compare fails. TP-BIT-016:ctrl emits
the sole carrier of one (base, control) pair with another control so that control is never exercised: the base compare and
the control-coverage check fail.

emit(plan) renders RV32IMC(B) assembly for the lowRISC gcc 10.2 (-march=rv32imcb): every op stores its rd into a result
buffer in .data as it goes; the program then replays the buffer to GEN_MM_EOT_ADDR (one report word per op, plan order)
and ends with the tohost pass code.

CLI: python3 gen_bit_draft_prog.py --seed N --out <file.S> [--red [--red-item TP-BIT-016[:imm|:ctrl]]]
"""
import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dv.auto_dv.tests.gen_programs.gen_prog_const import TOHOST_PASS  # noqa: E402

MASK32 = 0xFFFFFFFF
PROGRAM_TAG = "bit_draft"
BUILT_ITEMS = ("TP-BIT-016",)
RED_SELECTORS = {"TP-BIT-016": ("imm", "ctrl")}     # first entry = the default deviation of the item
CTRL_BITS = 5                      # log2(XLEN) control bits of grev/gorc on RV32
N_CTRL = 1 << CTRL_BITS
CANONICAL_CTRL = (7, 24, 31)       # brev8 / rev8 / rev (W9 weight 2)
RANDOM_KINDS = ("grevi", "gorci", "grev", "gorc")
# Ratified or named aliases pinned once per seed inside the stream (rev.b is the draft name of the brev8 encoding,
# grevi 7; the toolchain has no brev8 mnemonic).
ALIAS_KINDS = {"rev8": ("grevi", 24), "orc.b": ("gorci", 7), "rev.b": ("grevi", 7)}
IMM_KINDS = ("grevi", "gorci")
REG_KINDS = ("grev", "gorc")
N_RANDOM_OPS = (36, 44)            # random extras per seed (inclusive range)
CHAIN_PROB = 0.25                  # rs1 = the previous op's rd (forwarding path, no li)
CTRL_INSENSITIVE = ("zero", "all_ones")   # grev/gorc of these give the same rd for every control

# gen_test_plan.md "Layer-1 weight tables" W1: 32-bit register operand classes.
W1 = {"zero": 1, "all_ones": 1, "int_min": 1, "int_max": 1, "one": 1, "p16": 1, "two": 1, "e0000000": 1,
      "byte_msb": 1, "half_msb": 1, "single_bit": 1, "alt": 1, "bytes_01020304": 1, "distinct_lanes": 1,
      "pos_rand": 4, "neg_rand": 4}
W1_FLOOR = {k: v for k, v in W1.items() if k not in CTRL_INSENSITIVE}
# W3, register-form upper bits rs2[31:5]: zero 4, the named values 1 each, other_nonzero 2.
W3_UPPER = {"zero": 4, "v32": 1, "v33": 1, "vFFFFFFE0": 1, "v80000000": 1, "vFFFFFFFF": 1, "other_nonzero": 2}
# The literal W3 classes fix rs2[4:0] themselves; a floor op may draw one only when it names the op's control.
W3_FIXED_CTRL = {"v32": 0, "v33": 1, "vFFFFFFFF": N_CTRL - 1}
# W9, grev/gorc control words: uniform over 0..31, the canonical values weight 2.
W9_CTRL = {c: (2 if c in CANONICAL_CTRL else 1) for c in range(N_CTRL)}
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
    return v, v & (N_CTRL - 1)


def floor_upper_table(ctrl, nonzero):
    """W3 classes a floor register op with this control may draw (nonzero = the forced nonzero-upper slot)."""
    return {k: w for k, w in W3_UPPER.items()
            if W3_FIXED_CTRL.get(k, ctrl) == ctrl and not (nonzero and k == "zero")}


def sensitive(rd, rs1_val):
    """A compare that constrains the control: rd is written and grev/gorc of the operand depends on the control."""
    return rd != 0 and rs1_val not in (0, MASK32)


@dataclass
class Slot:
    kind: str                # grevi gorci grev gorc rev8 orc.b rev.b
    ctrl: int = -1           # pinned control (floor and alias slots); -1 = draw from W9
    floor: bool = False
    force_rs1: str = ""      # forced W1 class ("" = draw)
    force_upper: bool = False  # forced nonzero rs2 upper bits


@dataclass
class Op:
    idx: int
    kind: str                # grevi gorci grev gorc rev8 orc.b rev.b
    base: str                # the reference op: grevi gorci grev gorc
    floor: bool              # directed-floor member (non-vacuous by construction)
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

    @property
    def sensitive(self):
        return sensitive(self.rd, self.rs1_val)


@dataclass
class Plan:
    seed: int
    red: bool
    red_item: str            # "" when not red
    red_sel: str             # deviation selector ("" when not red)
    eot_reg: int
    buf_reg: int
    ops: list
    reports: list            # expected rd values, one per op, plan order
    k: int
    min_retired: int
    red_idx: int             # op whose control the red program deviates on (-1 when not red)
    red_ctrl: int
    items: dict              # per-item expectations the test asserts


def program_rng(seed):
    return random.Random(f"{int(seed)}:program:{PROGRAM_TAG}")


def red_rng(seed):
    """Separate stream for the red choices so the expectations are identical with and without --red."""
    return random.Random(f"{int(seed)}:red:{PROGRAM_TAG}")


FILLER_FORMS = ("addi", "xori", "andi", "ori", "add", "sub", "sll", "xor", "lui")


def _filler(rng, pool):
    form = rng.choice(FILLER_FORMS)
    rd, ra, rb = (rng.choice(pool) for _ in range(3))
    if form in ("addi", "xori", "andi", "ori"):
        return f"{form} x{rd}, x{ra}, {rng.randrange(-2048, 2048)}"
    if form == "lui":
        return f"lui x{rd}, 0x{rng.randrange(1 << 20):x}"
    return f"{form} x{rd}, x{ra}, x{rb}"


def _stream(rng):
    """The shuffled op stream: the directed floor (one slot per (base, control) pair, the alias forms) inside the
    random extras; per base one floor slot carries a single-bit operand, per register base one nonzero upper half."""
    slots = []
    for base in RANDOM_KINDS:
        group = [Slot(base, c, floor=True) for c in range(N_CTRL)]
        picks = rng.sample(group, 2)
        picks[0].force_rs1 = "single_bit"
        if base in REG_KINDS:
            picks[1].force_upper = True
        slots += group
    slots += [Slot(alias, ALIAS_KINDS[alias][1], floor=True) for alias in ALIAS_KINDS]
    slots += [Slot(rng.choice(RANDOM_KINDS)) for _ in range(rng.randint(*N_RANDOM_OPS))]
    rng.shuffle(slots)
    return slots


def _floor_op(rng, pool, slot, prev):
    """Operands of a floor slot: rd written, operand control-sensitive, the slot's control kept effective."""
    base, ctrl = ALIAS_KINDS.get(slot.kind, (slot.kind, slot.ctrl))
    rd = rng.choice(pool)
    chain_ok = prev is not None and sensitive(prev.rd, prev.expect) and not slot.force_rs1
    if chain_ok and rng.random() < CHAIN_PROB:
        rs1, rs1_val, rs1_class, chained = prev.rd, prev.expect, "chain_prev", True
    else:
        rs1 = rng.choice(pool)
        rs1_class = slot.force_rs1 or weighted(rng, W1_FLOOR)
        rs1_val, chained = operand_value(rng, rs1_class), False
    rs2, rs2_val, upper_class = 0, 0, ""
    if base in REG_KINDS:
        upper_class = weighted(rng, floor_upper_table(ctrl, slot.force_upper))
        rs2 = rd if (rng.random() < W4_RS2_EQ_RD and rd != rs1) else rng.choice([x for x in pool if x != rs1])
        rs2_val, eff = rs2_value(rng, upper_class, ctrl)
        assert eff == ctrl, f"floor control lost: {slot} -> {eff}"
    return base, rd, rs1, rs2, rs1_val, rs2_val, ctrl, rs1_class, upper_class, chained


def _extra_op(rng, pool, slot, prev):
    """Operands of a random extra: full W1 / W3 / W4 / W9 freedom, vacuous compares allowed."""
    base = slot.kind
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
    ctrl = weighted(rng, W9_CTRL)
    rs2, rs2_val, upper_class = 0, 0, ""
    if base in REG_KINDS:
        upper_class = weighted(rng, W3_UPPER)
        r = rng.random()
        if r < W4_RS_SAME and rs1 != 0:
            rs2, rs2_val, ctrl, upper_class = rs1, rs1_val, rs1_val & (N_CTRL - 1), "same_as_rs1"
        else:
            rs2 = rd if (r < W4_RS_SAME + W4_RS2_EQ_RD and rd != 0 and rd != rs1) else rng.choice([x for x in pool if x != rs1])
            rs2_val, ctrl = rs2_value(rng, upper_class, ctrl)
    return base, rd, rs1, rs2, rs1_val, rs2_val, ctrl, rs1_class, upper_class, chained


def _items(ops):
    carriers = {(b, c): [] for b in RANDOM_KINDS for c in range(N_CTRL)}
    for op in ops:
        if op.sensitive:
            carriers[(op.base, op.ctrl)].append(op.idx)
    return {"TP-BIT-016": {
        "ops_by_base": {b: [op.idx for op in ops if op.base == b and op.kind == b] for b in RANDOM_KINDS},
        "alias_ops": [op.idx for op in ops if op.kind in ALIAS_KINDS],
        "floor_ops": [op.idx for op in ops if op.floor],
        "sensitive_ops": [op.idx for op in ops if op.sensitive],
        # (base, control) -> control-sensitive carriers; the test needs a matching carrier for every pair
        "controls": carriers,
        "single_bit_ops": {b: [op.idx for op in ops if op.base == b and op.sensitive and op.rs1_class == "single_bit"]
                           for b in RANDOM_KINDS},
        "nonzero_upper_ops": {b: [op.idx for op in ops if op.base == b and op.sensitive and (op.rs2_val >> CTRL_BITS) != 0]
                              for b in REG_KINDS},
    }}


def _red_choice(seed, red, red_item):
    if not red:
        return "", ""
    item, _, sel = (red_item or "").partition(":")
    item = item or red_rng(seed).choice(BUILT_ITEMS)
    assert item in BUILT_ITEMS, f"--red-item {item}: not a built item ({', '.join(BUILT_ITEMS)})"
    sel = sel or RED_SELECTORS[item][0]
    assert sel in RED_SELECTORS[item], f"--red-item {item}:{sel}: selectors are {', '.join(RED_SELECTORS[item])}"
    return item, sel


def _red_target(seed, ops, items, sel):
    """(op index, deviated control) for the selector; the deviated control changes the op's true result."""
    carriers = items["TP-BIT-016"]["controls"]
    # a chain source's wrong rd would propagate to the chained ops: keep the deviation to one op's compare
    lone = [op for op in ops if not (op.idx + 1 < len(ops) and ops[op.idx + 1].chained)]
    if sel == "imm":
        cands = [op for op in lone if op.kind == "gorci" and op.sensitive and len(carriers[(op.base, op.ctrl)]) >= 2]
    else:
        cands = [op for op in lone if op.floor and op.kind in RANDOM_KINDS and len(carriers[(op.base, op.ctrl)]) == 1]
    assert cands, f"red {sel}: no eligible op at seed {seed}"
    op = red_rng(seed).choice(cands)
    for c in [op.ctrl ^ 1] + [c for c in range(N_CTRL) if c not in (op.ctrl, op.ctrl ^ 1)]:
        if REFERENCE[op.base](op.rs1_val, c) != op.expect:
            return op.idx, c
    raise AssertionError(f"red {sel}: op {op.idx} result does not depend on its control")


def plan(seed, red=False, red_item=None):
    rng = program_rng(seed)
    eot_reg, buf_reg = rng.sample(range(5, 32), 2)        # x5..x31: gp/t5 stay free for the tohost tail
    pool = [r for r in range(1, 32) if r not in (eot_reg, buf_reg)]
    ops = []
    prev = None
    for idx, slot in enumerate(_stream(rng)):
        draw = _floor_op if slot.floor else _extra_op
        base, rd, rs1, rs2, rs1_val, rs2_val, ctrl, rs1_class, upper_class, chained = draw(rng, pool, slot, prev)
        fill_pool = [x for x in pool if not (chained and x == prev.rd)]
        fillers = [_filler(rng, fill_pool) for _ in range(rng.randrange(3))]
        expect = REFERENCE[base](rs1_val, ctrl) if rd != 0 else 0
        op = Op(idx, slot.kind, base, slot.floor, rd, rs1, rs2, rs1_val, rs2_val, ctrl, rs1_class, upper_class,
                chained, expect, fillers)
        assert not slot.floor or op.sensitive, f"vacuous floor op {op}"
        ops.append(op)
        prev = op
    reports = [op.expect for op in ops]
    # retirement floor: every emitted straight-line instruction counted once (li/la expand to >= 1)
    n_insn = 2 + sum(len(op.fillers) + (0 if op.chained or op.rs1 == 0 else 1)
                     + (0 if op.is_imm or op.rs2 == op.rs1 else 1) + 2 for op in ops) + 2 * len(ops) + 3
    items = _items(ops)
    red_item, red_sel = _red_choice(seed, red, red_item)
    red_idx, red_ctrl = _red_target(seed, ops, items, red_sel) if red else (-1, -1)
    return Plan(seed, red, red_item, red_sel, eot_reg, buf_reg, ops, reports, len(reports), n_insn, red_idx, red_ctrl,
                items)


def _emitted_ctrl(plan_, op):
    return plan_.red_ctrl if (plan_.red and op.idx == plan_.red_idx) else op.ctrl


def _op_line(plan_, op):
    ctrl = _emitted_ctrl(plan_, op)
    if op.kind in ALIAS_KINDS and ctrl == op.ctrl:
        return f"{op.kind} x{op.rd}, x{op.rs1}"
    if op.is_imm:
        return f"{op.base} x{op.rd}, x{op.rs1}, {ctrl}"
    return f"{op.base} x{op.rd}, x{op.rs1}, x{op.rs2}"


def emit(plan_):
    p = plan_
    out = [f"# gen_bit_draft_prog.py seed={p.seed} red={int(p.red)}: generated, do not edit "
           f"(k={p.k} reports, min_retired={p.min_retired})"]
    if p.red:
        out.append(f"# RED FIXTURE {p.red_item}:{p.red_sel}: op {p.red_idx} is emitted with control {p.red_ctrl}; "
                   "the expectation keeps the true control, so the fire-check must fail")
    out += ['.include "gen_mmio_map.h"', ".section .text", ".globl _start", "_start:",
            f"  li   x{p.eot_reg}, GEN_MM_EOT_ADDR", f"  la   x{p.buf_reg}, gen_bit_results"]
    for op in p.ops:
        ctrl = _emitted_ctrl(p, op)
        red_mark = f"  RED: control deviates to {ctrl}" if ctrl != op.ctrl else ""
        out.append(f"  # op {op.idx}: {op.kind} ctrl={op.ctrl} {'floor' if op.floor else 'extra'} rs1={op.rs1_class} "
                   f"0x{op.rs1_val:08x}"
                   + (f" rs2={op.upper_class} 0x{op.rs2_val:08x}" if not op.is_imm else "")
                   + f" -> 0x{op.expect:08x}{red_mark}")
        out += [f"  {f}" for f in op.fillers]
        if not op.chained and op.rs1 != 0:
            out.append(f"  li   x{op.rs1}, 0x{op.rs1_val:08x}")
        if not op.is_imm and op.rs2 != op.rs1:
            rs2_val = (op.rs2_val & ~(N_CTRL - 1)) | ctrl
            out.append(f"  li   x{op.rs2}, 0x{rs2_val:08x}")
        out.append(f"  {_op_line(p, op)}")
        out.append(f"  sw   x{op.rd}, {4 * op.idx}(x{p.buf_reg})")
    out.append("  # report replay: one EOT-register store per op, plan order")
    tmp = [r for r in range(5, 32) if r not in (p.eot_reg, p.buf_reg)][:2]
    for op in p.ops:
        t = tmp[op.idx % 2]
        out.append(f"  lw   x{t}, {4 * op.idx}(x{p.buf_reg})")
        out.append(f"  sw   x{t}, 0(x{p.eot_reg})")
    out += [f"  li   gp, {TOHOST_PASS}", "  la   t5, tohost", "  sw   gp, 0(t5)", "1:", "  j    1b", "",
            ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost",
            "fromhost: .dword 0", ".align 4", f"gen_bit_results: .fill {p.k}, 4, 0", ".align 2",
            ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--red", action="store_true", help="emit a TDD red fixture (one op's control deviates)")
    ap.add_argument("--red-item", default=None, metavar="ID[:SEL]",
                    help="the item (and deviation selector) the red fixture targets; built: "
                         + ", ".join(i + ":" + "|".join(RED_SELECTORS[i]) for i in BUILT_ITEMS))
    a = ap.parse_args()
    if a.red_item and not a.red:
        ap.error("--red-item needs --red")
    p = plan(a.seed, a.red, a.red_item)
    text = emit(p)
    assert all(ord(ch) < 128 for ch in text), "non-ASCII in the generated program"
    with open(a.out, "w") as f:
        f.write(text)
    floor = len(p.items["TP-BIT-016"]["floor_ops"])
    print(f"gen_bit_draft_prog seed={p.seed} red={int(p.red)} red_item={p.red_item}:{p.red_sel} k={p.k} floor={floor} "
          f"sensitive={len(p.items['TP-BIT-016']['sensitive_ops'])} min_retired={p.min_retired} red_idx={p.red_idx} "
          f"red_ctrl={p.red_ctrl} -> {a.out}")


if __name__ == "__main__":
    main()
