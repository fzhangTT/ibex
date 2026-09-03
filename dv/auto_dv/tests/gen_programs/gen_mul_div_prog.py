#!/usr/bin/env python3
"""gen_mul_div_prog: per-seed program generator of gen_test_mul_div (plan group gen_mul_div, dv/auto_dv/docs/
gen_test_plan.md AREA MUL: TP-MUL-013 divu, 014 rem, 015 remu, 016 div/divu by zero, 017 rem/remu by zero, 018 signed
overflow INT_MIN / -1, 019 div/rem sign quadrants, 020 divu/remu with MSB-set operands, 021 divide corner values,
026 M-extension decode forms with rd = x0; the latency items TP-MUL-012 and 022 contribute no unit).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:mul_div"): per item a
directed floor, the exhaustive set its Fire-check says "every ..." about (the CG-MUL-003 dividend and divisor classes
for divu and remu, the four sign quadrants of div/rem pairs, the six dividend classes of each divide by zero, the
(INT_MIN, -1) row of every op, the four MSB-set rows, the seven divisor corners of every op, the eight funct3 with
rd = x0 and rd != x0), plus weighted extras (W7 operands, W4 register relations), every unit shuffled into one stream
with single-cycle ALU fillers between units, and the expected value of every report word the program stores to
GEN_MM_EOT_ADDR (the RAW observation: rd after each op, or x0 read back after an rd = x0 form), computed here from
the RV32M specification (tools/specs/riscv-isa-manual/src/unpriv/m-st-ext.adoc: division rounding toward zero, the
remainder sign of the dividend, the divide-by-zero and signed-overflow table).
red=True makes the PROGRAM deviate on one intent of one item while the expectation stays true: one of that item's ops
is emitted with another funct3 of its family or with one operand bit flipped, chosen so that the emitted result
differs from the expectation on that item's report words only (self-checked on the same model), so exactly that
item's fire-check fails. red_item names the item; None lets random.Random(f"{seed}:red") draw it.
emit(plan) renders the RV32IM assembly.

CLI: python3 gen_mul_div_prog.py --seed N --out <file.S> [--red [--red-item TP-MUL-0nn]]
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

RNG_TAG = "program:mul_div"
RED_TAG = "red"
MASK32 = 0xFFFFFFFF
INT_MIN = 0x80000000
INT_MAX = 0x7FFFFFFF
ALL_ONES = MASK32
MINUS_TWO = 0xFFFFFFFE
EOT_REG = 28                      # holds GEN_MM_EOT_ADDR for every report store
FILLER_REGS = (5, 6, 7)           # the unrelated instructions between units work on these
OP_REGS = tuple(r for r in range(1, 32) if r != EOT_REG)   # rd/rs1/rs2 draws; x0 only through the W4 rules

MUL_OPS = ("mul", "mulh", "mulhsu", "mulhu")     # funct3 000..011 under funct7 0000001
DIV_OPS = ("div", "divu", "rem", "remu")         # funct3 100..111
M_OPS = MUL_OPS + DIV_OPS
SIGNED = {"div": True, "rem": True, "divu": False, "remu": False}

I_DIVU, I_REM, I_REMU, I_DIV0, I_REM0 = "TP-MUL-013", "TP-MUL-014", "TP-MUL-015", "TP-MUL-016", "TP-MUL-017"
I_OVF, I_SIGN, I_MSB, I_CORNER, I_DECODE = "TP-MUL-018", "TP-MUL-019", "TP-MUL-020", "TP-MUL-021", "TP-MUL-026"
RED_ITEMS = (I_DIVU, I_REM, I_REMU, I_DIV0, I_REM0, I_OVF, I_SIGN, I_MSB, I_CORNER, I_DECODE)

# CG-MUL-003 operand classes (gen_fcov_plan.md): the named values first, then the relations, then the random signs.
DIVIDEND_NAMED = {"zero": 0, "one": 1, "all_ones": ALL_ONES, "int_min": INT_MIN, "int_max": INT_MAX, "two": 2, "seven": 7}
DIVIDEND_CLASSES = tuple(DIVIDEND_NAMED) + ("pos_rand", "neg_rand")
DIVISOR_NAMED = {"zero": 0, "one": 1, "all_ones": ALL_ONES, "int_min": INT_MIN, "two": 2, "minus_two": MINUS_TWO}
DIVISOR_CLASSES = tuple(DIVISOR_NAMED) + ("eq_dividend", "abs_gt_dividend", "pos_rand", "neg_rand")
DIV0_DIVIDEND_CLASSES = ("zero", "one", "all_ones", "int_min", "int_max", "rand")            # TP-MUL-016/017
CORNER_DIVISOR_CLASSES = ("one", "eq_dividend", "abs_gt_dividend", "all_ones", "two", "minus_two", "int_min")  # TP-MUL-021
SIGN_PAIRS = ("pp", "pn", "np", "nn")            # bit 31 of (dividend, divisor)
SIGN_PINNED = {"np": (-7, 2), "pn": (7, -2), "nn": (-7, -2), "pp": (7, 2)}                     # TP-MUL-019
MSB_ROWS = ((ALL_ONES, 2), (INT_MIN, ALL_ONES), (ALL_ONES, ALL_ONES), (INT_MIN, INT_MIN))    # TP-MUL-020
MSB_RESULTS = (INT_MAX, 0, INT_MIN, 1)

# Layer-1 tables (gen_test_plan.md "Layer-1 weight tables"): W7 divide operands (the CG-MUL-003 extremes 1 each,
# pos_rand 4, neg_rand 4, divisor zero 1: about 7 percent of the extras; the by-zero items pin it), W4 register
# relations per 16 draws (rd = x0 1, all same 1, rs1 == rs2 1, rs == rd 2, x0 as a zero source 1 in 2 where the
# operand is zero).
W7_DIVIDEND = {**{c: 1 for c in DIVIDEND_NAMED}, "pos_rand": 4, "neg_rand": 4}
W7_DIVISOR = {**{c: 1 for c in DIVISOR_NAMED}, "eq_dividend": 1, "abs_gt_dividend": 1, "pos_rand": 4, "neg_rand": 4}
W4_REL = {"rd_x0": 1, "all_same": 1, "rs1_eq_rs2": 1, "rs_eq_rd": 2, "distinct": 11}
X0_SOURCE_ONE_IN = 2
FILLER_TEMPLATES = ("addi x5, x5, {imm12}", "xori x6, x6, {imm12}", "slli x7, x7, {sh}", "add x5, x6, x7",
                    "sub x7, x5, x6", "lui x6, {imm20}", "andi x5, x5, {imm12}", "or x6, x6, x7", "nop")


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def to_signed(v):
    return v - (1 << 32) if v & INT_MIN else v


def to_unsigned(v):
    return v & MASK32


def sign_bit(v):
    return (v >> 31) & 1


def magnitude(v, signed):
    return abs(to_signed(v)) if signed else v


def m_result(op, a, b):
    """RV32M semantics (m-st-ext.adoc): truncating division, remainder with the dividend's sign, the divide-by-zero
    row (quotient all ones, remainder the dividend), the signed-overflow row (quotient INT_MIN, remainder 0), the
    four multiply high/low words."""
    sa, sb = to_signed(a), to_signed(b)
    if op == "div":
        if b == 0:
            return ALL_ONES
        if a == INT_MIN and b == ALL_ONES:
            return INT_MIN
        q = abs(sa) // abs(sb)
        return to_unsigned(-q if (sa < 0) != (sb < 0) else q)
    if op == "rem":
        if b == 0:
            return a
        if a == INT_MIN and b == ALL_ONES:
            return 0
        r = abs(sa) - (abs(sa) // abs(sb)) * abs(sb)
        return to_unsigned(-r if sa < 0 else r)
    if op == "divu":
        return ALL_ONES if b == 0 else a // b
    if op == "remu":
        return a if b == 0 else a % b
    if op == "mul":
        return (a * b) & MASK32
    if op == "mulh":
        return ((sa * sb) >> 32) & MASK32
    if op == "mulhsu":
        return ((sa * b) >> 32) & MASK32
    if op == "mulhu":
        return ((a * b) >> 32) & MASK32
    raise ValueError(f"unknown M op {op}")


def classify_dividend(a):
    for name, v in DIVIDEND_NAMED.items():
        if a == v:
            return name
    return "neg_rand" if sign_bit(a) else "pos_rand"


def classify_divisor(b, a, signed):
    """The CG-MUL-003 cp_divisor classes a divisor realizes (a set: a named value may also equal the dividend)."""
    named = [name for name, v in DIVISOR_NAMED.items() if b == v]
    cls = set(named)
    if b == a and a != 0:
        cls.add("eq_dividend")
    if not named:
        if magnitude(b, signed) > magnitude(a, signed):
            cls.add("abs_gt_dividend")
        cls.add("neg_rand" if sign_bit(b) else "pos_rand")
    return frozenset(cls)


def sign_pair(a, b):
    return ("p", "n")[sign_bit(a)] + ("p", "n")[sign_bit(b)]


def rand_unnamed(rng, negative, named):
    """A random 32-bit value of the given sign bit that is none of the named values."""
    while True:
        r = rng.getrandbits(32)
        r = (r | INT_MIN) if negative else (r & INT_MAX)
        if r not in named:
            return r


def dividend(rng, cls):
    if cls in DIVIDEND_NAMED:
        return DIVIDEND_NAMED[cls]
    if cls == "rand":
        return rng.getrandbits(32)
    return rand_unnamed(rng, cls == "neg_rand", set(DIVIDEND_NAMED.values()))


def divisor(rng, cls, a, signed):
    """A divisor of the named class; the relations (eq_dividend, abs_gt_dividend) fall back to a random sign class
    when the dividend makes them impossible."""
    if cls in DIVISOR_NAMED:
        return DIVISOR_NAMED[cls]
    named = set(DIVISOR_NAMED.values())
    if cls == "eq_dividend" and a != 0:
        return a
    if cls == "abs_gt_dividend":
        m = magnitude(a, signed)
        top = INT_MAX if signed else MASK32
        if m < top:
            for _ in range(64):
                b = rng.randint(m + 1, top)
                if signed and rng.getrandbits(1):
                    b = to_unsigned(-b)
                if b not in named and b != a:
                    return b
    return rand_unnamed(rng, cls == "neg_rand" or (cls not in ("pos_rand",) and rng.getrandbits(1)), named)


def small_dividend(rng, signed):
    """A dividend that leaves room for an unlisted divisor of larger magnitude."""
    m = rng.randint(1, 1 << 30)
    return to_unsigned(-m) if signed and rng.getrandbits(1) else m


def nontrivial(rng):
    """A random operand outside the values a decode fault could hide behind (0, 1, all ones)."""
    while True:
        r = rng.getrandbits(32)
        if r not in (0, 1, ALL_ONES):
            return r


@dataclass
class Report:
    idx: int
    item: str
    expect: int
    label: str


@dataclass
class Unit:
    kind: str                 # op | filler
    item: str = ""
    ops: tuple = ()           # intended mnemonics (one, or the div/rem pair of the same operands)
    a: int = 0                # dividend / rs1 operand
    b: int = 0                # divisor / rs2 operand
    rds: tuple = ()           # rd per op (0 = x0: the report word is x0 read back)
    rs1: int = 0
    rs2: int = 0
    tag: str = ""             # the directed-floor row this unit realizes ("" for a weighted extra)
    vacuous: bool = False     # an rd = x0 draw outside TP-MUL-026: reported (x0 reads 0) but counted apart
    emit_ops: list = field(default_factory=list)   # what the program emits; differs from ops only in a red fixture
    emit_a: int = 0
    emit_b: int = 0
    text: str = ""            # filler instruction
    idx: list = field(default_factory=list)        # report indices in store order


@dataclass
class Plan:
    seed: int
    red: bool
    units: list
    reports: list
    k: int
    min_retired: int
    items: dict               # item id -> report indices in store order
    filler_init: tuple
    summary: dict
    red_item: str
    red_note: str


def draw_regs(rng, u, allow_x0_rd, pair=False):
    """W4 register relations for one unit; rs1 == rs2 only when the operands are equal; x0 as a source only for a
    zero operand; a pair's quotient register never overlaps the operands (the rem still reads them)."""
    rel = weighted(rng, W4_REL)
    if rel == "rd_x0" and not allow_x0_rd:
        rel = "distinct"
    same_ok = u.a == u.b
    if rel in ("all_same", "rs1_eq_rs2") and (not same_ok or pair):
        rel = "distinct"
    rs1 = rng.choice(OP_REGS)
    if rel in ("all_same", "rs1_eq_rs2"):
        rs2 = rs1
    else:
        rs2 = rng.choice([r for r in OP_REGS if r != rs1])
    if u.a == 0 and rel not in ("all_same", "rs1_eq_rs2") and rng.randrange(X0_SOURCE_ONE_IN) == 0:
        rs1 = 0
    if u.b == 0 and rel not in ("all_same", "rs1_eq_rs2") and rng.randrange(X0_SOURCE_ONE_IN) == 0:
        rs2 = 0
    if rs1 == 0 and rs2 == 0:
        rs2 = rng.choice(OP_REGS) if rng.getrandbits(1) else 0
    if rel == "rd_x0":
        rd = 0
    elif rel == "all_same":
        rd = rs1
    elif rel == "rs_eq_rd" and not pair:
        rd = rng.choice([r for r in (rs1, rs2) if r != 0] or list(OP_REGS))
    else:
        rd = rng.choice([r for r in OP_REGS if r not in (rs1, rs2)])
    u.rs1, u.rs2 = rs1, rs2
    if pair:
        u.rds = (rd, rng.choice(OP_REGS))
    else:
        u.rds = (rd,)
    u.vacuous = rd == 0 and u.item != I_DECODE
    return u


def unit(rng, item, ops, a, b, tag="", allow_x0_rd=False, rd=None):
    u = Unit("op", item, tuple(ops), a & MASK32, b & MASK32, tag=tag)
    draw_regs(rng, u, allow_x0_rd, pair=len(ops) == 2)
    if rd is not None:                       # TP-MUL-026 pins its rd class; x0 sources stay out (the operands matter)
        u.rs1 = u.rs1 or rng.choice(OP_REGS)
        u.rs2 = u.rs2 or rng.choice([r for r in OP_REGS if r != u.rs1])
        u.rds = (0 if rd == 0 else rng.choice([r for r in OP_REGS if r not in (u.rs1, u.rs2)]),)
        u.vacuous = False
    return u


def w7_divisor(rng, a, signed, zero=True):
    table = dict(W7_DIVISOR) if zero else {c: w for c, w in W7_DIVISOR.items() if c != "zero"}
    return divisor(rng, weighted(rng, table), a, signed)


def build_unsigned_units(rng, item, op):
    """TP-MUL-013 / 015: every dividend class (divisor non-zero, so the dividend shows) and every divisor class."""
    signed = SIGNED[op]
    U = []
    for c in DIVIDEND_CLASSES:
        a = dividend(rng, c)
        U.append(unit(rng, item, (op,), a, w7_divisor(rng, a, signed, zero=False), tag=f"dividend:{c}"))
    for c in DIVISOR_CLASSES:
        if c == "abs_gt_dividend":
            a = small_dividend(rng, signed)
        elif c == "eq_dividend":
            a = rand_unnamed(rng, rng.getrandbits(1), set(DIVIDEND_NAMED.values()))
        else:
            a = dividend(rng, weighted(rng, W7_DIVIDEND))
        U.append(unit(rng, item, (op,), a, divisor(rng, c, a, signed), tag=f"divisor:{c}"))
    for _ in range(rng.randint(4, 10)):
        a = dividend(rng, weighted(rng, W7_DIVIDEND))
        U.append(unit(rng, item, (op,), a, w7_divisor(rng, a, signed), allow_x0_rd=True))
    return U


def signed_pair(rng, sp, max_mag=INT_MAX):
    """(dividend, divisor) of the sign quadrant with random magnitudes; INT_MIN never appears, so no pair overflows."""
    a = rng.randint(1, max_mag)
    b = rng.randint(1, max_mag)
    return to_unsigned(-a if sp[0] == "n" else a), to_unsigned(-b if sp[1] == "n" else b)


def build_rem_units(rng):
    """TP-MUL-014: rem paired with the div of the same operands for every sign pair; the identity check is the test's."""
    U = [unit(rng, I_REM, ("div", "rem"), *signed_pair(rng, sp), tag=f"sign:{sp}") for sp in SIGN_PAIRS]
    for _ in range(rng.randint(2, 6)):
        a = dividend(rng, weighted(rng, W7_DIVIDEND))
        U.append(unit(rng, I_REM, ("div", "rem"), a, w7_divisor(rng, a, True)))
    return U


def build_sign_units(rng):
    """TP-MUL-019: the four pinned quadrant pairs, one random-magnitude pair per quadrant, extras."""
    U = [unit(rng, I_SIGN, ("div", "rem"), to_unsigned(a), to_unsigned(b), tag=f"pinned:{sp}") for sp, (a, b) in SIGN_PINNED.items()]
    U += [unit(rng, I_SIGN, ("div", "rem"), *signed_pair(rng, sp), tag=f"random:{sp}") for sp in SIGN_PAIRS]
    U += [unit(rng, I_SIGN, ("div", "rem"), *signed_pair(rng, rng.choice(SIGN_PAIRS))) for _ in range(rng.randint(0, 4))]
    return U


def build_zero_units(rng, item, ops):
    """TP-MUL-016 / 017: each op of the pair by zero with a dividend from every class, extras by zero too."""
    U = [unit(rng, item, (op,), dividend(rng, c), 0, tag=f"{op}:{c}") for op in ops for c in DIV0_DIVIDEND_CLASSES]
    for _ in range(rng.randint(0, 4)):
        U.append(unit(rng, item, (rng.choice(ops),), dividend(rng, rng.choice(DIV0_DIVIDEND_CLASSES)), 0, allow_x0_rd=True))
    return U


def build_overflow_units(rng):
    """TP-MUL-018: (INT_MIN, -1) for every op; extras 40 percent that row, else (INT_MIN, random negative)."""
    U = [unit(rng, I_OVF, (op,), INT_MIN, ALL_ONES, tag=f"{op}:intmin_m1") for op in DIV_OPS]
    for _ in range(rng.randint(4, 8)):
        b = ALL_ONES if rng.random() < 0.4 else rand_unnamed(rng, True, {ALL_ONES})
        U.append(unit(rng, I_OVF, (rng.choice(DIV_OPS),), INT_MIN, b, allow_x0_rd=True))
    return U


def build_msb_units(rng):
    """TP-MUL-020: the four MSB-set rows for divu and remu, plus random MSB-set pairs."""
    U = [unit(rng, I_MSB, (op,), a, b, tag=f"{op}:{a:08x}/{b:08x}") for a, b in MSB_ROWS for op in ("divu", "remu")]
    for _ in range(rng.randint(2, 6)):
        which = rng.randrange(3)             # msb set on the dividend, the divisor, or both
        a = rng.getrandbits(32) | (INT_MIN if which != 1 else 0)
        b = rng.getrandbits(32) | (INT_MIN if which != 0 else 0)
        U.append(unit(rng, I_MSB, (rng.choice(("divu", "remu")),), a, b, allow_x0_rd=True))
    return U


def corner_operands(rng, op, c):
    signed = SIGNED[op]
    if c == "one":
        return dividend(rng, weighted(rng, W7_DIVIDEND)), 1
    if c == "eq_dividend":
        a = rand_unnamed(rng, rng.getrandbits(1), set(DIVIDEND_NAMED.values()))
        return a, a
    if c == "abs_gt_dividend":
        a = small_dividend(rng, signed)
        return a, divisor(rng, c, a, signed)
    if c == "all_ones":
        return dividend(rng, weighted(rng, {k: w for k, w in W7_DIVIDEND.items() if k != "int_min"})), ALL_ONES
    if c in ("two", "minus_two", "int_min"):
        return INT_MIN, DIVISOR_NAMED[c]
    if c == "dividend_zero":
        return 0, w7_divisor(rng, 0, signed, zero=False)
    raise ValueError(c)


def build_corner_units(rng):
    """TP-MUL-021: every corner divisor class and the zero dividend for each of the four ops, extras from the same set."""
    cases = CORNER_DIVISOR_CLASSES + ("dividend_zero",)
    U = [unit(rng, I_CORNER, (op,), *corner_operands(rng, op, c), tag=f"{op}:{c}") for op in DIV_OPS for c in cases]
    for _ in range(rng.randint(0, 6)):
        op = rng.choice(DIV_OPS)
        U.append(unit(rng, I_CORNER, (op,), *corner_operands(rng, op, rng.choice(cases)), allow_x0_rd=True))
    return U


def build_decode_units(rng):
    """TP-MUL-026: all eight funct3 with rd = x0 (x0 read back) and rd != x0, non-trivial operands."""
    U = []
    for op in M_OPS:
        for x0 in (True, False):
            U.append(unit(rng, I_DECODE, (op,), nontrivial(rng), nontrivial(rng), tag=f"{op}:{'rd_x0' if x0 else 'rd'}", rd=0 if x0 else -1))
    for _ in range(rng.randint(0, 4)):
        U.append(unit(rng, I_DECODE, (rng.choice(M_OPS),), nontrivial(rng), nontrivial(rng), rd=0 if rng.getrandbits(1) else -1))
    return U


def filler(rng):
    t = rng.choice(FILLER_TEMPLATES)
    return Unit("filler", text=t.format(imm12=rng.randint(-2048, 2047), sh=rng.randint(0, 31), imm20=rng.randint(0, 0xFFFFF)))


def operands(u, emitted):
    """(rs1 value, rs2 value) the op sees: the intent, or what the program loads (one li serves a shared register)."""
    if not emitted:
        return u.a, u.b
    return u.emit_a, (u.emit_a if u.rs1 == u.rs2 else u.emit_b)


def simulate(units, emitted=False):
    """Walk the program order once: one Report per stored word, from the intended ops and operands (the expectation)
    or, with emitted=True, from what the program emits (the red fixture's self-check). An rd = x0 form reports x0."""
    reports = []
    items = {i: [] for i in RED_ITEMS}
    for u in units:
        if u.kind != "op":
            continue
        a, b = operands(u, emitted)
        ops = u.emit_ops if emitted else u.ops
        u.idx = []
        for op, rd in zip(ops, u.rds):
            value = 0 if rd == 0 else m_result(op, a, b)
            r = Report(len(reports), u.item, value, f"{op} x{rd},x{u.rs1},x{u.rs2} 0x{u.a:08x}/0x{u.b:08x}" + (" [x0 readback]" if rd == 0 else ""))
            reports.append(r)
            items[u.item].append(r.idx)
            u.idx.append(r.idx)
    return reports, items


def red_candidates(rng, units, item):
    """(unit, attribute, deviated value) of every encodable deviation of the item, in a seed-drawn order: another
    funct3 of the op's family, or one operand bit flipped (only through a register the program loads)."""
    cands = []
    for u in units:
        if u.kind != "op" or u.item != item:
            continue
        for i, op in enumerate(u.ops):
            family = M_OPS if item == I_DECODE else DIV_OPS
            cands += [(u, f"op{i}", alt) for alt in family if alt != op]
        if u.rs1 != 0:
            cands += [(u, "emit_a", u.a ^ 1), (u, "emit_a", u.a ^ INT_MIN)]
        if u.rs2 != 0 and u.rs2 != u.rs1:
            cands += [(u, "emit_b", u.b ^ 1), (u, "emit_b", u.b ^ INT_MIN)]
    rng.shuffle(cands)
    return cands


def set_dev(u, attr, value):
    if attr.startswith("op"):
        u.emit_ops[int(attr[2:])] = value
    else:
        setattr(u, attr, value)


def get_dev(u, attr):
    return u.emit_ops[int(attr[2:])] if attr.startswith("op") else getattr(u, attr)


def apply_red(rng, units, item, expected):
    """The red fixture: the first candidate deviation whose emitted program changes report words of the item and of
    no other item (proved on the model); the expectation keeps the true program."""
    exp = [r.expect for r in expected]
    for u, attr, dev in red_candidates(rng, units, item):
        keep = get_dev(u, attr)
        set_dev(u, attr, dev)
        actual = [r.expect for r in simulate(units, emitted=True)[0]]
        diff = [i for i, (x, e) in enumerate(zip(actual, exp)) if x != e]
        if diff and all(expected[i].item == item for i in diff):
            was = f"{keep} -> {dev}" if attr.startswith("op") else f"0x{keep:08x} -> 0x{dev:08x}"
            return f"{item}: {'/'.join(u.ops)} rd x{u.rds[0]} {attr} {was}; report idx {diff} deviate"
        set_dev(u, attr, keep)
    raise AssertionError(f"no deviation of {item} changes one of its report words for this seed")


def li(reg, value):
    return f"  li   x{reg}, 0x{value:08x}"


def body_lines(units, filler_init):
    """The .text lines after _start (the scenario and its report stores)."""
    L = [f"  li   x{EOT_REG}, GEN_MM_EOT_ADDR"]
    L += [li(r, v) for r, v in zip(FILLER_REGS, filler_init)]
    for u in units:
        if u.kind == "filler":
            L.append(f"  {u.text}")
            continue
        a, b = operands(u, emitted=True)
        if u.rs1:
            L.append(li(u.rs1, a))
        if u.rs2 and u.rs2 != u.rs1:
            L.append(li(u.rs2, b))
        for op, rd in zip(u.emit_ops, u.rds):
            L.append(f"  {op} x{rd}, x{u.rs1}, x{u.rs2}")
            L.append(f"  sw   x{rd}, 0(x{EOT_REG})")
    return L


def retire_floor(lines):
    """Honest lower bound of retirements at the end-of-test store: one per straight-line instruction (li counted as
    1 whatever the assembler expands), less a margin for the instructions still in the pipeline at the store."""
    return max(len(lines) - 4, 1)


def op_units(p, item, op=None, observed=True):
    """Units of an item (optionally of one op) whose result is an observation (rd != x0)."""
    return [u for u in p.units if u.kind == "op" and u.item == item and (op is None or op in u.ops) and (not observed or not u.vacuous)]


def check_coverage(p):
    """The plan carries what the items ask for; a generator drift fails here, not silently in a run."""
    for item, op in ((I_DIVU, "divu"), (I_REMU, "remu")):
        us = op_units(p, item, op)
        assert {classify_dividend(u.a) for u in us if u.b != 0} == set(DIVIDEND_CLASSES), f"{item}: dividend classes"
        seen = set().union(*(classify_divisor(u.b, u.a, SIGNED[op]) for u in us))
        assert seen >= set(DIVISOR_CLASSES), f"{item}: divisor classes missing {set(DIVISOR_CLASSES) - seen}"
    assert {sign_pair(u.a, u.b) for u in op_units(p, I_REM)} == set(SIGN_PAIRS), "TP-MUL-014: sign pairs"
    assert all(u.ops == ("div", "rem") and u.rds[0] not in (u.rs1, u.rs2) for u in op_units(p, I_REM) + op_units(p, I_SIGN)), "pair form"
    for item, ops in ((I_DIV0, ("div", "divu")), (I_REM0, ("rem", "remu"))):
        assert all(u.b == 0 for u in op_units(p, item, observed=False)), f"{item}: a non-zero divisor"
        for op in ops:
            got = {c for c in DIV0_DIVIDEND_CLASSES[:-1] for u in op_units(p, item, op) if u.a == DIVIDEND_NAMED[c]}
            got |= {"rand" for u in op_units(p, item, op) if u.a not in DIVIDEND_NAMED.values()}
            assert got == set(DIV0_DIVIDEND_CLASSES), f"{item} {op}: dividend classes {sorted(got)}"
    for op in DIV_OPS:
        assert any(u.a == INT_MIN and u.b == ALL_ONES for u in op_units(p, I_OVF, op)), f"TP-MUL-018 {op}: (INT_MIN, -1) missing"
    assert all(u.a == INT_MIN and sign_bit(u.b) for u in op_units(p, I_OVF, observed=False)), "TP-MUL-018: operand rows"
    sign_units = op_units(p, I_SIGN)
    pinned = {(to_signed(u.a), to_signed(u.b)) for u in sign_units}
    assert pinned >= set(SIGN_PINNED.values()), "TP-MUL-019: pinned quadrant pairs"
    assert {sign_pair(u.a, u.b) for u in sign_units} == set(SIGN_PAIRS), "TP-MUL-019: quadrants"
    assert all(u.b != 0 and not (u.a == INT_MIN and u.b == ALL_ONES) for u in sign_units), "TP-MUL-019: a by-zero or overflow pair"
    for op in ("divu", "remu"):
        assert {(u.a, u.b) for u in op_units(p, I_MSB, op)} >= set(MSB_ROWS), f"TP-MUL-020 {op}: rows"
    assert {m_result(u.ops[0], u.a, u.b) for u in op_units(p, I_MSB)} >= set(MSB_RESULTS), "TP-MUL-020: result classes"
    for op in DIV_OPS:
        us = op_units(p, I_CORNER, op)
        seen = set().union(*(classify_divisor(u.b, u.a, SIGNED[op]) for u in us))
        assert seen >= set(CORNER_DIVISOR_CLASSES), f"TP-MUL-021 {op}: divisor corners missing {set(CORNER_DIVISOR_CLASSES) - seen}"
        assert any(u.a == 0 for u in us), f"TP-MUL-021 {op}: zero dividend"
        assert any(u.b == ALL_ONES and u.a != INT_MIN for u in us), f"TP-MUL-021 {op}: divisor -1 with a non-INT_MIN dividend"
    dec = op_units(p, I_DECODE, observed=False)
    assert {(u.ops[0], u.rds[0] == 0) for u in dec} >= {(op, x0) for op in M_OPS for x0 in (True, False)}, "TP-MUL-026: funct3 x rd class"
    assert all(u.a not in (0, 1, ALL_ONES) and u.b not in (0, 1, ALL_ONES) for u in dec), "TP-MUL-026: trivial operand"
    for u in p.units:
        if u.kind != "op":
            continue
        assert u.rs1 != u.rs2 or u.a == u.b, f"shared source register with different operands: {u}"
        assert (u.rs1 or u.a == 0) and (u.rs2 or u.b == 0), f"x0 as the source of a non-zero operand: {u}"
        assert EOT_REG not in (u.rs1, u.rs2) + u.rds and all(0 <= r < 32 for r in (u.rs1, u.rs2) + u.rds), f"register out of range: {u}"
        assert len(u.idx) == len(u.ops) == len(u.rds) == len(u.emit_ops)
    lines = body_lines(p.units, p.filler_init)
    stores = [i for i, ln in enumerate(lines) if ln.split()[0] == "sw"]
    assert all(b - a >= 2 for a, b in zip(stores, stores[1:])), "two report stores back to back (one edge per store)"
    assert p.k == len(p.reports) and sum(len(v) for v in p.items.values()) == p.k
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
    filler_init = tuple(rng.getrandbits(32) for _ in FILLER_REGS)
    units = (build_unsigned_units(rng, I_DIVU, "divu") + build_rem_units(rng) + build_unsigned_units(rng, I_REMU, "remu")
             + build_zero_units(rng, I_DIV0, ("div", "divu")) + build_zero_units(rng, I_REM0, ("rem", "remu"))
             + build_overflow_units(rng) + build_sign_units(rng) + build_msb_units(rng) + build_corner_units(rng)
             + build_decode_units(rng))
    rng.shuffle(units)
    stream = []
    for u in units:
        stream.extend(filler(rng) for _ in range(rng.choice((0, 0, 1, 1, 2))))
        stream.append(u)
    for u in stream:
        if u.kind == "op":
            u.emit_ops, u.emit_a, u.emit_b = list(u.ops), u.a, u.b
    reports, items = simulate(stream)
    red_item = red_item_of(seed, red_item) if red else ""
    red_note = apply_red(rng, stream, red_item, reports) if red else ""
    simulate(stream)                                  # restore the intended report indices on every unit
    ops = [u for u in stream if u.kind == "op"]
    summary = {"units": len(ops), "pairs": sum(1 for u in ops if len(u.ops) == 2), "fillers": sum(1 for u in stream if u.kind == "filler"),
               "vacuous_rd_x0": sum(1 for u in ops if u.vacuous), "x0_forms_026": sum(1 for u in ops if u.item == I_DECODE and u.rds[0] == 0),
               "by_zero": sum(1 for u in ops if u.b == 0), "x0_sources": sum(1 for u in ops if u.rs1 == 0 or u.rs2 == 0)}
    for op in M_OPS:
        summary[op] = sum(u.ops.count(op) for u in ops)
    for item in RED_ITEMS:
        summary[item] = len(items[item])
    p = Plan(int(seed), bool(red), stream, reports, len(reports), retire_floor(body_lines(stream, filler_init)), items,
             filler_init, summary, red_item, red_note)
    check_coverage(p)
    return p


def emit(p):
    L = [f"# gen_mul_div_prog.py --seed {p.seed}{' --red --red-item ' + p.red_item if p.red else ''}: RV32M divide program of gen_test_mul_div",
         f"# k={p.k} report words (" + ", ".join(f"{i} {len(p.items[i])}" for i in RED_ITEMS) + f"), gen_min_retired={p.min_retired}"]
    if p.red:
        L.append(f"# RED FIXTURE {p.red_note}; the expectation keeps the true program, so the {p.red_item} fire-check must fail")
    L += ['.include "gen_mmio_map.h"', "", ".section .text", ".globl _start", "_start:"]
    L += body_lines(p.units, p.filler_init)
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
    if red:                                           # the red deviates the program only, never the expectation
        g = plan(a.seed)
        assert [r.expect for r in p.reports] == [r.expect for r in g.reports] and p.k == g.k and p.min_retired == g.min_retired, \
            "red plan differs from the green plan in its expectations, k or retirement floor"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(emit(p))
    print(f"OK seed={a.seed} red={red} out={a.out} k={p.k} min_retired={p.min_retired} {p.summary}"
          + (f" red_item={p.red_item} red_note={p.red_note!r}" if red else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
