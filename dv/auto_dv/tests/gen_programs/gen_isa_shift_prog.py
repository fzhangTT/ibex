#!/usr/bin/env python3
"""gen_isa_shift_prog: per-seed program generator of gen_test_isa_shift (plan group gen_isa_shift: TP-ISA-010
shift-immediate slli/srli/srai, TP-ISA-011 shift by 0 and 31 and sign propagation, TP-ISA-013 shift-register
sll/srl/sra, TP-ISA-014 rs2 upper bits ignored; dv/auto_dv/docs/gen_test_plan.md AREA ISA, covergroup CG-ISA-003).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:isa_shift"): one shuffled
stream of base shifts, every op followed by a store of its rd to GEN_MM_EOT_ADDR (one report word per op, the RAW
observation), made of the directed floors the items' fire-checks name plus weighted extras:
  - shamt floor: every op (6) x every shift amount 0..31 with an operand that keeps the result sensitive to the amount
    (TP-ISA-010 every shamt class per op, TP-ISA-013 every amount; register forms with rs2[31:5] = 0);
  - operand floor: every op x every CG-ISA-003 cp_operand class (zero, all_ones, msb_only, lsb_only, neg_rand, pos_rand);
  - rd = x0 floor: one op per op with rd = x0 (cr_op_rd_x0; vacuous for the shift result, counted apart);
  - TP-ISA-011 directed cases: the eight cr_sra_sign tuples, their sll/srl mirrors, and a shift by 0 of a random
    operand per op (result == rs1);
  - TP-ISA-014 floor: every register op x every nonzero cp_rs2_upper class (32, 33, 0xFFFFFFFF, 0x80000000,
    0xFFFFFFE0, random rs2[31:5] != 0), msb_only / lsb_only operands tried first in 20 percent of its iterations;
  - extras with the W1 / W3 / W4 freedom (imm or register form, rd = x0, x0 sources, rs1 == rs2, rs2 upper bits per W3).
Item attribution is by construction: immediate forms -> TP-ISA-010, register forms with rs2[31:5] = 0 -> TP-ISA-013,
with rs2[31:5] != 0 -> TP-ISA-014, the directed cases -> TP-ISA-011. Every op loads its own sources (li) before it
executes, so one op's report word depends on that op alone. The expected rd of every op is the 32-bit shift model
below, written from the RV32I text (tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc: the amount is imm[4:0] or
rs2[4:0]; slli zero-fills the low bits, srli zero-fills the high bits, srai copies the sign bit), never from the RTL.
W-tables (gen_test_plan.md "Layer-1 weight tables"): W1 operands, W3 amounts and rs2 upper bits, W4 register indices.

red=True makes the PROGRAM deviate on one op of one item while the expectations stay true: the op is emitted as another
op of its form (sign-fill or direction error) or with a shift amount differing in one bit (imm field or rs2 value),
chosen so that the emitted result differs from the expectation (self-checked on the model), so exactly that item's
fire-check fails. red_item names the item; None lets random.Random(f"{seed}:red") draw it.

CLI: python3 gen_isa_shift_prog.py --seed N --out <file.S> [--red [--red-item TP-ISA-010|TP-ISA-011|TP-ISA-013|TP-ISA-014]]
"""
import argparse
import random
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dv.auto_dv.tests.gen_programs.gen_prog_const import TOHOST_PASS  # noqa: E402

RNG_TAG = "program:isa_shift"
RED_TAG = "red"
MASK32 = 0xFFFFFFFF
MSB = 0x80000000
N_SHAMT = 32
EOT_REG = 28                                   # holds GEN_MM_EOT_ADDR for every report store
REG_POOL = tuple(r for r in range(1, 32) if r != EOT_REG)

ITEM_010, ITEM_011, ITEM_013, ITEM_014 = "TP-ISA-010", "TP-ISA-011", "TP-ISA-013", "TP-ISA-014"
RED_ITEMS = (ITEM_010, ITEM_011, ITEM_013, ITEM_014)
IMM_OPS = ("slli", "srli", "srai")
REG_OPS = ("sll", "srl", "sra")
OPS = IMM_OPS + REG_OPS
# CG-ISA-003 class names (gen_fcov_plan.md): cp_operand, cp_shamt, cp_rs2_upper, cp_result_class.
OPERAND_CLASSES = ("zero", "all_ones", "msb_only", "lsb_only", "neg_rand", "pos_rand")
SHAMT_CLASSES = ("s0", "s1", "mid", "s31")
UPPER_FIXED = {"is32": 32, "is33": 33, "all_ones": MASK32, "msb_only": MSB, "ffffffe0": 0xFFFFFFE0}
UPPER_NONZERO = tuple(UPPER_FIXED) + ("other_nonzero",)
# TP-ISA-011 directed cases: name -> (op, operand class, amount) and the result F-ISA-011 states for each.
SIGN_CASES = {"srai_neg_31": ("srai", "neg_rand", 31), "srai_pos_31": ("srai", "pos_rand", 31), "srai_msb_1": ("srai", "msb_only", 1),
              "sra_neg_31": ("sra", "neg_rand", 31), "sra_pos_31": ("sra", "pos_rand", 31), "sra_msb_1": ("sra", "msb_only", 1),
              "srli_msb_31": ("srli", "msb_only", 31), "slli_lsb_31": ("slli", "lsb_only", 31),
              "srl_msb_31": ("srl", "msb_only", 31), "sll_lsb_31": ("sll", "lsb_only", 31)}
SIGN_RESULTS = {"srai_neg_31": MASK32, "srai_pos_31": 0, "srai_msb_1": 0xC0000000, "sra_neg_31": MASK32, "sra_pos_31": 0,
                "sra_msb_1": 0xC0000000, "srli_msb_31": 1, "slli_lsb_31": MSB, "srl_msb_31": 1, "sll_lsb_31": MSB}
ZERO_CASES = tuple(f"{op}_by_0" for op in OPS)     # shift by 0 of a random operand: result == rs1
CASE_NAMES = tuple(SIGN_CASES) + ZERO_CASES

# Layer-1 tables (gen_test_plan.md "Layer-1 weight tables"): W1 register operands (int_max / alt_5 / alt_a are the
# group extremes), W3 amounts and rs2[31:5], W4 register-index fractions.
W1_OPERAND = {"zero": 1, "all_ones": 1, "msb_only": 1, "int_max": 1, "lsb_only": 1, "alt_5": 1, "alt_a": 1, "pos_rand": 4, "neg_rand": 4}
W3_AMOUNT = {"s0": 1, "s1": 1, "s31": 1, "mid": 4}
W3_UPPER = {"zero": 4, "is32": 1, "is33": 1, "ffffffe0": 1, "msb_only": 1, "all_ones": 1, "other_nonzero": 2}
W4_RD_X0, W4_SAME3, W4_SAME_SRC, W4_SRC_IS_RD, W4_X0_SRC = 1 / 16, 1 / 16, 1 / 16, 1 / 8, 1 / 16
SENSITIVE_CLASSES = ("msb_only", "lsb_only", "neg_rand", "pos_rand")   # operand classes tried for the shamt floors
PIN_FRACTION_014 = 0.2      # TP-ISA-014: msb_only / lsb_only operands tried first in this fraction of iterations
N_EXTRA = (60, 120)
NOP_FRACTION = 0.25         # a compressed nop before an op flips the PC alignment of the 32-bit shift
RETIRE_MARGIN = 4           # instructions still in flight at the end-of-test store


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def shift(op, x, amt):
    """RV32I shift semantics: the amount is the low five bits of the immediate or of rs2."""
    s = amt & (N_SHAMT - 1)
    if op in ("slli", "sll"):
        return (x << s) & MASK32
    if op in ("srli", "srl"):
        return x >> s
    if op in ("srai", "sra"):
        return ((x - (1 << 32)) >> s) & MASK32 if x & MSB else x >> s
    raise ValueError(f"unknown shift op {op}")


def sensitive(op, x, amt):
    """The result moves when the amount moves by one either way: the observation constrains the decoded amount."""
    s = amt & (N_SHAMT - 1)
    r = shift(op, x, s)
    return r != shift(op, x, (s + 1) % N_SHAMT) and r != shift(op, x, (s - 1) % N_SHAMT)


def operand_class(x):
    if x == 0:
        return "zero"
    if x == MASK32:
        return "all_ones"
    if x == MSB:
        return "msb_only"
    if x == 1:
        return "lsb_only"
    return "neg_rand" if x & MSB else "pos_rand"


def shamt_class(s):
    return {0: "s0", 1: "s1", 31: "s31"}.get(s, "mid")


def upper_class(v):
    """cp_rs2_upper of a register-form rs2 value."""
    if v >> 5 == 0:
        return "zero"
    for name, val in UPPER_FIXED.items():
        if v == val:
            return name
    return "other_nonzero"


def result_class(v):
    return {0: "zero", MASK32: "all_ones", MSB: "msb_only", 1: "one", 0xC0000000: "c0000000"}.get(v, "other")


def operand(rng, cls):
    """A 32-bit operand of the named class (pos_rand / neg_rand stay out of the listed values)."""
    fixed = {"zero": 0, "all_ones": MASK32, "msb_only": MSB, "lsb_only": 1, "int_max": 0x7FFFFFFF, "alt_5": 0x55555555, "alt_a": 0xAAAAAAAA}
    if cls in fixed:
        return fixed[cls]
    r = rng.getrandbits(32)
    if cls == "pos_rand":
        r &= 0x7FFFFFFF
        return r | 2 if r in (0, 1) else r
    if cls == "neg_rand":
        r |= MSB
        return r ^ 2 if r in (MASK32, MSB) else r
    raise ValueError(f"unknown operand class {cls}")


def amount(rng):
    """W3 shift amount by class."""
    return {"s0": 0, "s1": 1, "s31": 31}.get(weighted(rng, W3_AMOUNT), rng.randrange(2, 31))


def upper_value(rng, cls, shamt=None):
    """An rs2 value of the named cp_rs2_upper class; shamt pins the low five bits when given."""
    if cls in UPPER_FIXED:
        return UPPER_FIXED[cls]
    s = rng.randrange(N_SHAMT) if shamt is None else shamt
    if cls == "zero":
        return s
    while True:
        v = (rng.getrandbits(27) << 5) | s
        if upper_class(v) == "other_nonzero":
            return v


def sensitive_operand(rng, op, amt, classes=SENSITIVE_CLASSES, tries=16):
    """An operand of one of the classes that keeps the result sensitive to the amount; the canonical single-bit
    operand of the op's direction is the fallback (sensitive at every amount)."""
    for _ in range(tries):
        x = operand(rng, rng.choice(classes))
        if sensitive(op, x, amt):
            return x
    return 1 if op in ("slli", "sll") else MSB


@dataclass
class Op:
    item: str
    op: str                   # the intent (expectations follow it)
    x: int                    # rs1 operand
    amt: int                  # immediate shamt (0..31) or the rs2 value
    rd: int
    rs1: int
    rs2: int = -1             # -1 = immediate form
    kind: str = ""            # shamt_floor | operand_floor | rd_x0 | case:<name> | upper_floor | extra
    nop_before: bool = False
    emit_op: str = ""         # what the program emits; differs from op only in a red fixture
    emit_amt: int = 0         # differs from amt only in a red fixture
    idx: int = -1             # report index = position in program order

    @property
    def reg_form(self):
        return self.op in REG_OPS

    @property
    def shamt(self):
        return self.amt & (N_SHAMT - 1)

    @property
    def expect(self):
        return shift(self.op, self.x, self.amt) if self.rd else 0

    @property
    def emitted(self):
        return shift(self.emit_op, self.x, self.emit_amt) if self.rd else 0

    @property
    def vacuous(self):
        """rd = x0 or an amount-insensitive operand (0, all ones under sra, ...): not an observation of the amount."""
        return self.rd == 0 or not sensitive(self.op, self.x, self.amt)

    def label(self):
        src2 = f"x{self.rs2}" if self.reg_form else str(self.amt)
        return f"{self.op} x{self.rd},x{self.rs1},{src2} x=0x{self.x:08x} amt=0x{self.amt:08x} [{self.kind}]"


@dataclass
class Report:
    idx: int
    item: str
    expect: int
    label: str


@dataclass
class Plan:
    seed: int
    red: bool
    ops: list
    reports: list
    k: int
    min_retired: int
    items: dict               # item id -> report indices in store order
    cases: dict               # TP-ISA-011 case name -> report index
    summary: dict
    red_item: str             # the item the red fixture deviates on ("" when green)
    red_note: str


def item_of(op):
    return ITEM_010 if op in IMM_OPS else ITEM_013


def make(rng, item, op, x, amt, kind):
    """A floor op: rd != x0, sources distinct; x0 as a source only where its value is the intended zero."""
    rd = rng.choice(REG_POOL)
    rs1 = 0 if x == 0 and rng.random() < 0.5 else rng.choice(REG_POOL)
    rs2 = -1
    if op in REG_OPS:
        rs2 = 0 if amt == 0 and rng.random() < 0.5 else rng.choice([r for r in REG_POOL if r != rs1])
    return Op(item, op, x, amt, rd, rs1, rs2, kind)


def build_floors(rng):
    ops = []
    for op in OPS:                       # every amount per op, amount-sensitive operand, rs2 upper bits zero
        for s in range(N_SHAMT):
            ops.append(make(rng, item_of(op), op, sensitive_operand(rng, op, s), s, "shamt_floor"))
    for op in OPS:                       # every cp_operand class per op
        for cls in OPERAND_CLASSES:
            ops.append(make(rng, item_of(op), op, operand(rng, cls), amount(rng), "operand_floor"))
    for op in OPS:                       # cr_op_rd_x0 yes: vacuous for the result, counted apart
        o = make(rng, item_of(op), op, operand(rng, weighted(rng, W1_OPERAND)), amount(rng), "rd_x0")
        o.rd = 0
        ops.append(o)
    for name, (op, cls, s) in SIGN_CASES.items():
        ops.append(make(rng, ITEM_011, op, operand(rng, cls), s, f"case:{name}"))
    for op in OPS:                       # shift by 0 of a random operand returns rs1
        ops.append(make(rng, ITEM_011, op, operand(rng, rng.choice(("pos_rand", "neg_rand"))), 0, f"case:{op}_by_0"))
    for op in REG_OPS:                   # every nonzero rs2 upper class per register op
        for cls in UPPER_NONZERO:
            amt = upper_value(rng, cls)
            classes = ("msb_only", "lsb_only") if rng.random() < PIN_FRACTION_014 else SENSITIVE_CLASSES
            x = sensitive_operand(rng, op, amt, classes, tries=2)
            if not sensitive(op, x, amt):
                x = sensitive_operand(rng, op, amt)
            ops.append(make(rng, ITEM_014, op, x, amt, "upper_floor"))
    return ops


def extra(rng):
    """A weighted random shift with the full W1 / W3 / W4 freedom (rd = x0, x0 sources, rs1 == rs2 allowed)."""
    reg_form = rng.random() < 0.5
    op = rng.choice(REG_OPS if reg_form else IMM_OPS)
    x = operand(rng, weighted(rng, W1_OPERAND))
    s = amount(rng)
    rd = 0 if rng.random() < W4_RD_X0 else rng.choice(REG_POOL)
    others = [r for r in REG_POOL if r != rd]
    r = rng.random()
    if not reg_form:
        if rd and r < W4_SRC_IS_RD:
            rs1 = rd
        elif r < W4_SRC_IS_RD + W4_X0_SRC:
            rs1, x = 0, 0
        else:
            rs1 = rng.choice(REG_POOL)
        return Op(ITEM_010, op, x, s, rd, rs1, kind="extra")
    amt = upper_value(rng, weighted(rng, W3_UPPER), s)
    if rd and r < W4_SAME3:
        rs1 = rs2 = rd
        amt = x
    elif r < W4_SAME3 + W4_SAME_SRC:
        rs1 = rs2 = rng.choice(others)
        amt = x
    elif rd and r < W4_SAME3 + W4_SAME_SRC + W4_SRC_IS_RD:
        rs1, rs2 = (rd, rng.choice(others)) if rng.random() < 0.5 else (rng.choice(others), rd)
    else:
        rs1 = 0 if rng.random() < W4_X0_SRC else rng.choice(REG_POOL)
        rs2 = 0 if rng.random() < W4_X0_SRC else rng.choice(REG_POOL)
        x = 0 if rs1 == 0 else x
        amt = 0 if rs2 == 0 else (x if rs1 == rs2 else amt)
    return Op(ITEM_013 if upper_class(amt) == "zero" else ITEM_014, op, x, amt, rd, rs1, rs2, "extra")


def body_lines(ops):
    """The .text lines after _start: every op loads its sources, executes, and stores rd to the EOT register."""
    L = [f"  li   x{EOT_REG}, GEN_MM_EOT_ADDR"]
    for o in ops:
        if o.nop_before:
            L.append("  nop")
        if o.rs1:
            L.append(f"  li   x{o.rs1}, 0x{o.x:08x}")
        if o.reg_form:
            if o.rs2 and o.rs2 != o.rs1:
                L.append(f"  li   x{o.rs2}, 0x{o.emit_amt:08x}")
            L.append(f"  {o.emit_op} x{o.rd}, x{o.rs1}, x{o.rs2}")
        else:
            L.append(f"  {o.emit_op} x{o.rd}, x{o.rs1}, {o.emit_amt}")
        L.append(f"  sw   x{o.rd}, 0(x{EOT_REG})")
    return L


def retire_floor(lines):
    """Honest lower bound of retirements at the end-of-test store: one per line (li is 1 or 2 instructions), less
    the instructions still in the pipeline at the store."""
    return max(len(lines) - RETIRE_MARGIN, 1)


def red_candidates(rng, ops, item):
    """(op, attribute, deviated value) of every encodable deviation of the item's non-vacuous ops, seed-drawn order.
    An amount deviation needs its own li: not for an immediate-free rs2 = x0 nor for rs1 == rs2."""
    cands = []
    for o in ops:
        if o.item != item or o.vacuous:
            continue
        cands += [(o, "emit_op", alt) for alt in (REG_OPS if o.reg_form else IMM_OPS) if alt != o.op]
        if not o.reg_form or (o.rs2 != 0 and o.rs2 != o.rs1):
            cands += [(o, "emit_amt", o.amt ^ 1), (o, "emit_amt", o.amt ^ 16)]
    rng.shuffle(cands)
    return cands


def apply_red(rng, ops, item):
    """The red fixture: the first deviation whose emitted result differs from the expectation of that op; every op
    loads its own sources, so only that op's report word (the item's) changes."""
    for o, attr, dev in red_candidates(rng, ops, item):
        keep = getattr(o, attr)
        setattr(o, attr, dev)
        if o.emitted != o.expect:
            return f"{item}: {o.label()} {attr} {keep} -> {dev}; report idx {o.idx} deviates (0x{o.expect:08x} -> 0x{o.emitted:08x})"
        setattr(o, attr, keep)
    raise AssertionError(f"no deviation of {item} changes one of its report words for this seed")


def check_coverage(p):
    """The plan carries what the items ask for; a generator drift fails here, not silently in a run."""
    for op in OPS:
        mine = [o for o in p.ops if o.op == op]
        amounts = {o.shamt for o in mine if not o.vacuous and (not o.reg_form or upper_class(o.amt) == "zero")}
        assert amounts == set(range(N_SHAMT)), f"{op}: amounts missing with a sensitive operand: {sorted(set(range(N_SHAMT)) - amounts)}"
        classes = {operand_class(o.x) for o in mine if o.rd}
        assert classes >= set(OPERAND_CLASSES), f"{op}: operand classes missing: {sorted(set(OPERAND_CLASSES) - classes)}"
        assert any(o.rd == 0 for o in mine), f"{op}: no rd = x0 form"
    for name in CASE_NAMES:
        o = p.ops[p.cases[name]]
        assert o.rd and o.item == ITEM_011, f"case {name} vacuous or misattributed"
        if name in SIGN_CASES:
            op, cls, s = SIGN_CASES[name]
            assert (o.op, operand_class(o.x), o.shamt) == (op, cls, s), f"case {name} tuple drift: {o.label()}"
            assert o.expect == SIGN_RESULTS[name], f"case {name}: model 0x{o.expect:08x} != F-ISA-011 0x{SIGN_RESULTS[name]:08x}"
        else:
            assert o.shamt == 0 and o.x not in (0, MASK32) and o.expect == o.x, f"case {name}: shift by 0 must return rs1: {o.label()}"
    for op in REG_OPS:
        uppers = {upper_class(o.amt) for o in p.ops if o.op == op and o.item == ITEM_014 and not o.vacuous}
        assert uppers >= set(UPPER_NONZERO), f"{op}: rs2 upper classes missing: {sorted(set(UPPER_NONZERO) - uppers)}"
    for o in p.ops:
        want = ITEM_011 if o.kind.startswith("case:") else ITEM_010 if not o.reg_form else ITEM_013 if upper_class(o.amt) == "zero" else ITEM_014
        assert o.item == want, f"attribution drift: {o.label()} is {o.item}, form says {want}"
        assert (o.rs1 != 0 or o.x == 0) and (o.rs2 != 0 or o.amt == 0), f"x0 source with a nonzero value: {o.label()}"
        assert not (o.reg_form and o.rs1 == o.rs2 and o.rs1 != 0) or o.amt == o.x, f"rs1 == rs2 with two values: {o.label()}"
        assert o.reg_form or 0 <= o.amt < N_SHAMT, f"immediate out of range: {o.label()}"
        assert o.rd != EOT_REG and o.rs1 != EOT_REG and o.rs2 != EOT_REG, f"EOT register used: {o.label()}"
    assert p.k == len(p.ops) == len(p.reports) and sum(len(v) for v in p.items.values()) == p.k
    assert all(0 <= ord(c) < 128 for c in emit(p)), "non-ASCII in the emitted program"


def red_item_of(seed, red_item):
    """The item a red fixture deviates on: the named one, else the seed's own draw."""
    if red_item is None:
        return random.Random(f"{int(seed)}:{RED_TAG}").choice(RED_ITEMS)
    if red_item not in RED_ITEMS:
        raise ValueError(f"unknown red item {red_item}; one of {RED_ITEMS}")
    return red_item


def plan(seed, red=False, red_item=None):
    rng = random.Random(f"{int(seed)}:{RNG_TAG}")
    ops = build_floors(rng) + [extra(rng) for _ in range(rng.randint(*N_EXTRA))]
    rng.shuffle(ops)
    for i, o in enumerate(ops):
        o.idx, o.emit_op, o.emit_amt = i, o.op, o.amt
        o.nop_before = rng.random() < NOP_FRACTION
    reports = [Report(o.idx, o.item, o.expect, o.label()) for o in ops]
    items = {it: [o.idx for o in ops if o.item == it] for it in RED_ITEMS}
    cases = {o.kind[5:]: o.idx for o in ops if o.kind.startswith("case:")}
    red_item = red_item_of(seed, red_item) if red else ""
    red_note = apply_red(rng, ops, red_item) if red else ""
    summary = {op: sum(1 for o in ops if o.op == op) for op in OPS}
    summary.update({"extras": sum(1 for o in ops if o.kind == "extra"), "nops": sum(1 for o in ops if o.nop_before),
                    "rd_x0": sum(1 for o in ops if o.rd == 0), "insensitive": sum(1 for o in ops if o.rd and o.vacuous),
                    "upper_nonzero": len(items[ITEM_014]), "cases": len(cases)})
    p = Plan(int(seed), bool(red), ops, reports, len(reports), retire_floor(body_lines(ops)), items, cases, summary, red_item, red_note)
    check_coverage(p)
    return p


def emit(p):
    L = [f"# gen_isa_shift_prog.py --seed {p.seed}{' --red --red-item ' + p.red_item if p.red else ''}: shift program of gen_test_isa_shift",
         f"# k={p.k} report words (" + ", ".join(f"{it} {len(p.items[it])}" for it in RED_ITEMS) + f"), gen_min_retired={p.min_retired}"]
    if p.red:
        L.append(f"# RED FIXTURE {p.red_note}; the expectation keeps the true program, so the {p.red_item} fire-check must fail")
    L += ['.include "gen_mmio_map.h"', "", ".section .text", ".globl _start", "_start:"]
    L += body_lines(p.ops)
    L += [f"  li   gp, {TOHOST_PASS}", "  la   t5, tohost", "  sw   gp, 0(t5)", "1:", "  j    1b", "",
          ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
          ".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--red", action="store_true", help="emit the TDD red fixture (one item's program deviates)")
    ap.add_argument("--red-item", choices=RED_ITEMS, help="the item the red fixture deviates on (default: the seed draws it); implies --red")
    a = ap.parse_args()
    red = a.red or a.red_item is not None
    p = plan(a.seed, red, a.red_item)
    if red:
        g = plan(a.seed)
        assert [r.expect for r in p.reports] == [r.expect for r in g.reports] and (p.k, p.min_retired) == (g.k, g.min_retired), \
            "red plan changed the expectations, k or min_retired"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(emit(p))
    print(f"OK seed={a.seed} red={red} out={a.out} k={p.k} min_retired={p.min_retired} {p.summary}"
          + (f" red_item={p.red_item} red_note={p.red_note!r}" if red else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
