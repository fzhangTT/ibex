#!/usr/bin/env python3
"""gen_mul_mul_prog: per-seed program generator of gen_test_mul_mul (plan group gen_mul_mul: TP-MUL-001/002 mul,
TP-MUL-004 mulh, TP-MUL-005/006 mulhu, TP-MUL-007/008 mulhsu, TP-MUL-027 c.mul; dv/auto_dv/docs/gen_test_plan.md
AREA MUL. TP-MUL-003, the two-cycle mulh latency item, is not built).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:mul_mul"): for every
multiply form a shuffled directed floor inside the random stream (every extreme-by-extreme operand pair of
CG-MUL-001 cr_extremes, every rs1/rs2 operand class, every sign pair, every W4 register relation, the rsd'/rs2'
sweep of c.mul, both orders of the TP-MUL-008 asymmetric pairs) plus W7-weighted random extras (extreme x random,
random x random, dependent back-to-back chains, rd = x0 at 1/16, x0 as a zero source at 1/16); every multiply is
followed by a store of rd to GEN_MM_EOT_ADDR (the RAW observation). Expected words come from the RV32M product
model here (tools/specs/riscv-isa-manual/src/unpriv/m-st-ext.adoc "Multiplication Operations": mul = low word of
rs1 * rs2; mulh / mulhu / mulhsu = high word of the signed / unsigned / signed-by-unsigned 64-bit product; c.mul =
mul rsd', rsd', rs2' per zcb.adoc) walked over a 32-register model of the program, so register reuse and chains
are modelled, never assumed. red=True makes the PROGRAM deviate on one intent of one item while the expectation
stays true: one multiply of that item emitted as another RV32M form (TP-MUL-001..008) or one c.mul operand loaded
with its low bit flipped (TP-MUL-027); the deviation is chosen so that only that item's report words change
(proved on the same register model). red_item names the item; None lets random.Random(f"{seed}:red") draw it.

CLI: python3 gen_mul_mul_prog.py --seed N --out <file.S> [--red [--red-item TP-MUL-<nnn>]]
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

RNG_TAG = "program:mul_mul"
RED_TAG = "red"
MASK32 = 0xFFFFFFFF
EOT_REG = 28                       # holds GEN_MM_EOT_ADDR for every report store
FILLER_REGS = (29, 30, 31)         # the unrelated instructions between units write these only
OPERAND_REGS = tuple(range(1, 28))  # the W4 pool: x1..x31 less the report and filler registers
CREGS = tuple(range(8, 16))        # the 3-bit compressed register fields (x8..x15)

ITEM_MUL, ITEM_MUL_EXT, ITEM_MULH, ITEM_MULHU = "TP-MUL-001", "TP-MUL-002", "TP-MUL-004", "TP-MUL-005"
ITEM_MULHU_EXT, ITEM_MULHSU, ITEM_MULHSU_ASYM, ITEM_CMUL = "TP-MUL-006", "TP-MUL-007", "TP-MUL-008", "TP-MUL-027"
ITEMS = (ITEM_MUL, ITEM_MUL_EXT, ITEM_MULH, ITEM_MULHU, ITEM_MULHU_EXT, ITEM_MULHSU, ITEM_MULHSU_ASYM, ITEM_CMUL)
RED_ITEMS = ITEMS
RV32M_FORMS = ("mul", "mulh", "mulhsu", "mulhu")
MUL_KINDS = RV32M_FORMS + ("c_mul",)
FORM_OF = {ITEM_MUL: "mul", ITEM_MUL_EXT: "mul", ITEM_MULH: "mulh", ITEM_MULHU: "mulhu", ITEM_MULHU_EXT: "mulhu",
           ITEM_MULHSU: "mulhsu", ITEM_MULHSU_ASYM: "mulhsu", ITEM_CMUL: "c_mul"}
EXTREME_ITEMS = (ITEM_MUL_EXT, ITEM_MULH, ITEM_MULHU_EXT, ITEM_MULHSU_ASYM, ITEM_CMUL)

# Layer-1 table W7 (gen_test_plan.md "Layer-1 weight tables"): CG-MUL-001 operand classes, extremes 1 each,
# pos_rand 4, neg_rand 4; TP-MUL-005 weights the msb-set classes up; W4 register relations (rd = x0 1/16,
# rs1 == rs2 == rd 1/16, rs1 == rs2 != rd 1/16, rs1 == rd or rs2 == rd 1/8, otherwise distinct).
EXTREMES = {"zero": 0, "one": 1, "all_ones": MASK32, "int_min": 0x80000000, "int_max": 0x7FFFFFFF, "p16": 0x10000, "two": 2}
W7 = {**{c: 1 for c in EXTREMES}, "pos_rand": 4, "neg_rand": 4}
W7_MSB_UP = {**W7, "all_ones": 2, "int_min": 2, "neg_rand": 8}
CLASSES = tuple(W7)
NEG_CLASSES = ("all_ones", "int_min", "neg_rand")
POS_CLASSES = tuple(c for c in CLASSES if c not in NEG_CLASSES)
SIGN_PAIRS = ("pp", "pn", "np", "nn")
RELATIONS = ("rs1_eq_rs2", "all_same", "rs_eq_rd", "distinct")
W4_RELATIONS = {"rd_x0": 1, "all_same": 1, "rs1_eq_rs2": 1, "rs_eq_rd": 2, "distinct": 11}
RESULT_CLASSES = {"zero": 0, "one": 1, "all_ones": MASK32, "int_min": 0x80000000, "int_max": 0x7FFFFFFF,
                  "fffffffe": 0xFFFFFFFE, "r3fffffff": 0x3FFFFFFF, "r40000000": 0x40000000}
# result classes each extreme item's Fire-check names
RESULT_FLOOR = {ITEM_MUL_EXT: ("one", "zero", "int_min", "fffffffe"), ITEM_MULH: ("r3fffffff", "r40000000", "zero", "all_ones"),
                ITEM_MULHU_EXT: ("fffffffe", "one", "r40000000", "zero"), ITEM_MULHSU_ASYM: ("all_ones", "int_min", "zero")}
# TP-MUL-008 asymmetric pairs (rs1 class, rs2 class) whose swapped order the program also retires
ASYM_PAIRS = (("all_ones", "all_ones"), ("int_min", "all_ones"), ("one", "all_ones"), ("all_ones", "one"))
FILLER_TEMPLATES = ("addi x29, x29, {imm12}", "xori x30, x30, {imm12}", "slli x31, x31, {sh}", "add x29, x30, x31",
                    "lui x30, {imm20}", "nop", "c.nop")


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def s32(v):
    return v - (1 << 32) if v & 0x80000000 else v


def product(form, a, b):
    """RV32M semantics (m-st-ext.adoc): the low word of the product, or the high word of the 64-bit product
    for the signed (mulh), unsigned (mulhu) and signed rs1 by unsigned rs2 (mulhsu) interpretation."""
    if form in ("mul", "c_mul"):
        return (a * b) & MASK32
    if form == "mulh":
        return ((s32(a) * s32(b)) >> 32) & MASK32
    if form == "mulhsu":
        return ((s32(a) * b) >> 32) & MASK32
    if form == "mulhu":
        return ((a * b) >> 32) & MASK32
    raise ValueError(f"unknown multiply form {form}")


def classify(v):
    """CG-MUL-001 operand class of a 32-bit value."""
    for name, val in EXTREMES.items():
        if v == val:
            return name
    return "neg_rand" if v & 0x80000000 else "pos_rand"


def sign_pair(a, b):
    return ("n" if a >> 31 else "p") + ("n" if b >> 31 else "p")


def result_class(v):
    return next((n for n, x in RESULT_CLASSES.items() if v == x), "other")


def relation(rd, rs1, rs2):
    """CG-MUL-001 cp_same_regs of an index triple."""
    if rs1 == rs2:
        if rs1 == rd:
            return "all_same" if rd else "distinct"
        return "rs1_eq_rs2"
    return "rs_eq_rd" if rd in (rs1, rs2) else "distinct"


def operand(rng, cls):
    """A 32-bit operand of the named class (a random draw never lands on a named extreme)."""
    if cls in EXTREMES:
        return EXTREMES[cls]
    while True:
        r = rng.getrandbits(32)
        r = (r | 0x80000000) if cls == "neg_rand" else (r & 0x7FFFFFFF)
        if classify(r) == cls:
            return r


def signed_operand(rng, neg, table=W7):
    """A W7 draw restricted to one sign (bit 31)."""
    sub = {c: w for c, w in table.items() if (c in NEG_CLASSES) == neg}
    return operand(rng, weighted(rng, sub))


@dataclass
class Insn:
    kind: str                 # li | mul | mulh | mulhsu | mulhu | c_mul | report | filler
    item: str = ""            # the plan item the instruction serves ("" for fillers)
    rd: int = 0
    rs1: int = 0              # c_mul: rs1 == rd (rsd'); report: the register stored
    rs2: int = 0
    value: int = 0            # li immediate
    text: str = ""            # filler instruction
    tag: str = ""             # unit tag for labels and the summary
    emit_kind: str = ""       # what the program emits; differs from kind only in a red fixture
    emit_value: int = 0       # what a li loads; differs from value only in a red fixture


@dataclass
class Obs:
    form: str
    rd: int
    rs1: int
    rs2: int
    a: int
    b: int
    result: int
    tag: str
    idx: int                  # report index of this multiply


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
    obs: dict                 # item id -> Obs list (the intended program's multiplies)
    missing: dict             # item id -> directed-floor entries the plan lacks (empty when complete)
    summary: dict             # item id -> counts
    asym: list                # (idx_ab, idx_ba, model results differ) of TP-MUL-008 swapped pairs
    red_item: str             # the item the red fixture deviates on ("" when green)
    red_note: str


def draw_relation(rng, same_value, observable):
    rel = weighted(rng, W4_RELATIONS)
    if observable and rel == "rd_x0":
        rel = "distinct"
    if not same_value and rel in ("all_same", "rs1_eq_rs2"):
        rel = "distinct"
    return rel


def pick_regs(rng, a, b, rel):
    """(rd, rs1, rs2) of an RV32M multiply realizing the W4 relation; a zero operand rides on x0 at 1/16."""
    r1, r2, r3 = rng.sample(OPERAND_REGS, 3)
    if rel == "all_same":
        return r1, r1, r1
    if rel == "rs1_eq_rs2":
        return r2, r1, r1
    if rel == "rs_eq_rd":
        return (r1, r1, r2) if rng.getrandbits(1) else (r2, r1, r2)
    rd = 0 if rel == "rd_x0" else r1
    rs1 = 0 if a == 0 and rng.randrange(16) == 0 else r2
    rs2 = 0 if b == 0 and rng.randrange(16) == 0 else r3
    return rd, rs1, rs2


def mul_unit(rng, item, a, b, rel=None, observable=True, tag=""):
    """One observed multiply: operand loads (shuffled), the multiply, the report store of rd."""
    form = FORM_OF[item]
    if form == "c_mul":
        rd = rng.choice(CREGS)
        same = a == b and (rel == "all_same" or (rel is None and rng.randrange(8) == 0))
        rs1, rs2 = rd, (rd if same else rng.choice([r for r in CREGS if r != rd]))
    else:
        rd, rs1, rs2 = pick_regs(rng, a, b, rel or draw_relation(rng, a == b, observable))
    loads = [Insn("li", item, rd=rs1, value=a)] if rs1 else []
    if rs2 and rs2 != rs1:
        loads.append(Insn("li", item, rd=rs2, value=b))
    rng.shuffle(loads)
    m = Insn(form, item, rd=rd, rs1=rs1, rs2=rs2, tag=tag)
    return loads + [m, Insn("report", item, rs1=rd)]


def chain_unit(rng, item, n):
    """n back-to-back mul with each product feeding the next (TP-MUL-001 dependent chains), reported at the end."""
    regs = rng.sample(OPERAND_REGS, n + 2)
    vals = [operand(rng, weighted(rng, W7)) for _ in range(n + 1)]
    ops = [Insn("li", item, rd=r, value=v) for r, v in zip(regs[:n + 1], vals)]
    prev = regs[0]
    dsts = []
    for i in range(n):
        rd = regs[n + 1] if i == 0 else regs[i]          # later products overwrite consumed operand registers
        ops.append(Insn("mul", item, rd=rd, rs1=prev, rs2=regs[i + 1], tag="chain"))
        dsts.append(rd)
        prev = rd
    return ops + [Insn("report", item, rs1=r) for r in dsts]


def swap_unit(rng, item, a, b):
    """mulhsu rs1, rs2 then the same registers swapped (TP-MUL-008: both orders retire)."""
    rd1, rd2, rs1, rs2 = rng.sample(OPERAND_REGS, 4)
    return [Insn("li", item, rd=rs1, value=a), Insn("li", item, rd=rs2, value=b),
            Insn("mulhsu", item, rd=rd1, rs1=rs1, rs2=rs2, tag="swap_ab"), Insn("report", item, rs1=rd1),
            Insn("mulhsu", item, rd=rd2, rs1=rs2, rs2=rs1, tag="swap_ba"), Insn("report", item, rs1=rd2)]


def extreme_units(rng, item):
    """Every extreme-by-extreme operand pair once (CG-MUL-001 cr_extremes, the items' extreme tables)."""
    return [mul_unit(rng, item, EXTREMES[c1], EXTREMES[c2], tag="extreme") for c1 in EXTREMES for c2 in EXTREMES]


def build_units(rng):
    U = []
    # TP-MUL-001: rs1 and rs2 class sweeps, every sign pair, every register relation, W4 extras, chains
    U += [mul_unit(rng, ITEM_MUL, operand(rng, c), operand(rng, weighted(rng, W7)), tag="rs1_sweep") for c in CLASSES]
    U += [mul_unit(rng, ITEM_MUL, operand(rng, weighted(rng, W7)), operand(rng, c), tag="rs2_sweep") for c in CLASSES]
    U += [mul_unit(rng, ITEM_MUL, signed_operand(rng, sp[0] == "n"), signed_operand(rng, sp[1] == "n"), tag="sign") for sp in SIGN_PAIRS]
    for rel in RELATIONS:
        a = operand(rng, weighted(rng, W7))
        b = a if rel in ("rs1_eq_rs2", "all_same") else operand(rng, weighted(rng, W7))
        U.append(mul_unit(rng, ITEM_MUL, a, b, rel=rel, tag="relation"))
    U += [mul_unit(rng, ITEM_MUL, operand(rng, weighted(rng, W7)), operand(rng, weighted(rng, W7)), observable=False, tag="rand")
          for _ in range(rng.randint(6, 14))]
    U += [chain_unit(rng, ITEM_MUL, rng.randint(2, 3)) for _ in range(rng.randint(2, 4))]
    # TP-MUL-002: the extreme table, x * 0 and x * 1 with a random x, extreme x random and random extras
    U += extreme_units(rng, ITEM_MUL_EXT)
    U += [mul_unit(rng, ITEM_MUL_EXT, operand(rng, weighted(rng, W7)), EXTREMES[c], tag="table") for c in ("zero", "one")]
    for _ in range(rng.randint(4, 10)):
        r = rng.random()
        if r < 0.5:
            a, b = EXTREMES[rng.choice(list(EXTREMES))], EXTREMES[rng.choice(list(EXTREMES))]
        elif r < 0.8:
            a, b = EXTREMES[rng.choice(list(EXTREMES))], operand(rng, rng.choice(("pos_rand", "neg_rand")))
            if rng.getrandbits(1):
                a, b = b, a
        else:
            a, b = operand(rng, rng.choice(("pos_rand", "neg_rand"))), operand(rng, rng.choice(("pos_rand", "neg_rand")))
        U.append(mul_unit(rng, ITEM_MUL_EXT, a, b, tag="extra"))
    # TP-MUL-004: the extreme pairs, (x, 0), a random pair per sign quadrant, extras
    U += extreme_units(rng, ITEM_MULH)
    U.append(mul_unit(rng, ITEM_MULH, operand(rng, rng.choice(("pos_rand", "neg_rand"))), 0, tag="x_zero"))
    U += [mul_unit(rng, ITEM_MULH, operand(rng, "neg_rand" if sp[0] == "n" else "pos_rand"),
                   operand(rng, "neg_rand" if sp[1] == "n" else "pos_rand"), tag="quadrant") for sp in SIGN_PAIRS]
    U += [mul_unit(rng, ITEM_MULH, operand(rng, weighted(rng, W7)), operand(rng, weighted(rng, W7)), tag="rand") for _ in range(rng.randint(2, 8))]
    # TP-MUL-005: rs1 and rs2 class sweeps with the msb-set classes weighted up, extras
    U += [mul_unit(rng, ITEM_MULHU, operand(rng, c), operand(rng, weighted(rng, W7_MSB_UP)), tag="rs1_sweep") for c in CLASSES]
    U += [mul_unit(rng, ITEM_MULHU, operand(rng, weighted(rng, W7_MSB_UP)), operand(rng, c), tag="rs2_sweep") for c in CLASSES]
    U += [mul_unit(rng, ITEM_MULHU, operand(rng, weighted(rng, W7_MSB_UP)), operand(rng, weighted(rng, W7_MSB_UP)), tag="rand")
          for _ in range(rng.randint(4, 10))]
    # TP-MUL-006: the extreme pairs and random msb-set pairs
    U += extreme_units(rng, ITEM_MULHU_EXT)
    U += [mul_unit(rng, ITEM_MULHU_EXT, operand(rng, "neg_rand"), operand(rng, "neg_rand"), tag="msb_pair") for _ in range(rng.randint(2, 5))]
    # TP-MUL-007: rs1 sign balanced and rs2 msb balanced
    for sp in SIGN_PAIRS:
        U += [mul_unit(rng, ITEM_MULHSU, signed_operand(rng, sp[0] == "n"), signed_operand(rng, sp[1] == "n"), tag="sign")
              for _ in range(rng.randint(2, 5))]
    # TP-MUL-008: every ordered extreme pair (both orders of each asymmetric pair) and random swapped pairs
    U += extreme_units(rng, ITEM_MULHSU_ASYM)
    for _ in range(rng.randint(2, 4)):
        a = operand(rng, weighted(rng, W7))
        b = operand(rng, weighted(rng, W7))
        while b == a:
            b = operand(rng, weighted(rng, W7))
        U.append(swap_unit(rng, ITEM_MULHSU_ASYM, a, b))
    # TP-MUL-027: the extreme pairs, the rsd' and rs2' sweeps, rsd' == rs2' twice, extras
    U += extreme_units(rng, ITEM_CMUL)
    for r in CREGS:
        u = mul_unit(rng, ITEM_CMUL, operand(rng, weighted(rng, W7)), operand(rng, weighted(rng, W7)), rel="distinct", tag="rsd_sweep")
        retarget_cmul(u, rd=r)
        U.append(u)
        u = mul_unit(rng, ITEM_CMUL, operand(rng, weighted(rng, W7)), operand(rng, weighted(rng, W7)), rel="distinct", tag="rs2_sweep")
        retarget_cmul(u, rs2=r)
        U.append(u)
    for _ in range(2):
        a = operand(rng, weighted(rng, W7))
        U.append(mul_unit(rng, ITEM_CMUL, a, a, rel="all_same", tag="same"))
    U += [mul_unit(rng, ITEM_CMUL, operand(rng, weighted(rng, W7)), operand(rng, weighted(rng, W7)), tag="rand") for _ in range(rng.randint(2, 6))]
    return U


def retarget_cmul(unit, rd=None, rs2=None):
    """Move a distinct-register c.mul unit onto the swept register (the other register stays distinct)."""
    m = next(o for o in unit if o.kind == "c_mul")
    old_rd, old_rs2 = m.rd, m.rs2
    new_rd = rd if rd is not None else (old_rd if old_rd != rs2 else old_rs2)
    new_rs2 = rs2 if rs2 is not None else (old_rs2 if old_rs2 != rd else old_rd)
    remap = {old_rd: new_rd, old_rs2: new_rs2}
    for o in unit:
        if o.kind == "li":
            o.rd = remap[o.rd]
        elif o.kind == "c_mul":
            o.rd, o.rs1, o.rs2 = new_rd, new_rd, new_rs2
        elif o.kind == "report":
            o.rs1 = new_rd


def filler(rng):
    t = rng.choice(FILLER_TEMPLATES)
    return Insn("filler", text=t.format(imm12=rng.randint(-2048, 2047), sh=rng.randint(0, 31), imm20=rng.randint(0, 0xFFFFF)))


def simulate(ops, emitted=False):
    """Walk the program once over a 32-register model: one Report per report store, from the intended forms
    and operands (the expectation) or, with emitted=True, from what the program emits (the red self-check)."""
    regs = [0] * 32
    reports, items, obs = [], {i: [] for i in ITEMS}, {i: [] for i in ITEMS}
    last = {}
    for op in ops:
        kind = op.emit_kind if emitted else op.kind
        if kind == "li":
            regs[op.rd] = (op.emit_value if emitted else op.value) & MASK32
        elif kind in MUL_KINDS:
            a, b = regs[op.rs1], regs[op.rs2]
            res = product(kind, a, b)
            if op.rd:
                regs[op.rd] = res
            last[op.rd] = Obs(op.kind, op.rd, op.rs1, op.rs2, a, b, res, op.tag, -1)
        elif kind == "report":
            o = last.pop(op.rs1, None)
            label = (f"{o.form} x{o.rd},x{o.rs1},x{o.rs2} 0x{o.a:08x}*0x{o.b:08x} [{classify(o.a)} x {classify(o.b)}]"
                     if o else f"x{op.rs1}")
            r = Report(len(reports), op.item, regs[op.rs1], label)
            reports.append(r)
            items[op.item].append(r.idx)
            if o and not emitted:
                o.idx = r.idx
                obs[op.item].append(o)
    return reports, items, obs


def floors(item, obs):
    """Directed-floor entries of the item the observable multiplies (rd != x0) miss; empty when complete."""
    vis = [o for o in obs if o.rd]
    pairs = {(classify(o.a), classify(o.b)) for o in vis}
    rs1c, rs2c = {classify(o.a) for o in vis}, {classify(o.b) for o in vis}
    signs = {sign_pair(o.a, o.b) for o in vis}
    rels = {relation(o.rd, o.rs1, o.rs2) for o in vis}
    results = {result_class(o.result) for o in vis}
    miss = []
    if item in (ITEM_MUL, ITEM_MULHU):
        miss += [f"rs1 class {c}" for c in CLASSES if c not in rs1c] + [f"rs2 class {c}" for c in CLASSES if c not in rs2c]
    if item in (ITEM_MUL, ITEM_MULH, ITEM_MULHSU):
        miss += [f"sign pair {s}" for s in SIGN_PAIRS if s not in signs]
    if item == ITEM_MUL:
        miss += [f"relation {r}" for r in RELATIONS if r not in rels]
        miss += [] if any(o.tag == "chain" for o in vis) else ["dependent chain"]
    if item in EXTREME_ITEMS:
        miss += [f"extreme pair {c1} x {c2}" for c1 in EXTREMES for c2 in EXTREMES if (c1, c2) not in pairs]
    miss += [f"result class {c}" for c in RESULT_FLOOR.get(item, ()) if c not in results]
    if item == ITEM_MULHU_EXT and not any(classify(o.a) == classify(o.b) == "neg_rand" for o in vis):
        miss.append("random msb-set pair")
    if item == ITEM_MULHSU_ASYM and sum(1 for o in vis if o.tag == "swap_ab") < 2:
        miss.append("random swapped pairs")
    if item == ITEM_CMUL:
        miss += [f"rsd' x{r}" for r in CREGS if r not in {o.rd for o in vis}] + [f"rs2' x{r}" for r in CREGS if r not in {o.rs2 for o in vis}]
        miss += [] if any(o.rd == o.rs2 for o in vis) else ["rsd' == rs2'"]
        miss += [] if any(o.rd != o.rs2 for o in vis) else ["rsd' != rs2'"]
    return miss


def asym_pairs(obs):
    """(idx of (a, b), idx of (b, a), model results differ) for the listed asymmetric pairs and the swapped units."""
    out = []
    for c1, c2 in ASYM_PAIRS:
        ab = next((o for o in obs if o.rd and (classify(o.a), classify(o.b)) == (c1, c2)), None)
        ba = next((o for o in obs if o.rd and (classify(o.a), classify(o.b)) == (c2, c1)), None)
        if ab and ba:
            out.append((ab.idx, ba.idx, ab.result != ba.result))
    swaps = [o for o in obs if o.tag in ("swap_ab", "swap_ba")]
    for ab, ba in zip(swaps[0::2], swaps[1::2]):
        out.append((ab.idx, ba.idx, ab.result != ba.result))
    return out


def summarize(item, obs):
    vis = [o for o in obs if o.rd]
    return {"reports": len(obs), "observable": len(vis), "rd_x0": len(obs) - len(vis),
            "vacuous": sum(1 for o in vis if o.a == 0 or o.b == 0),
            "extreme_pairs": len({(classify(o.a), classify(o.b)) for o in vis if classify(o.a) in EXTREMES and classify(o.b) in EXTREMES}),
            "sign_pairs": len({sign_pair(o.a, o.b) for o in vis}), "chains": sum(1 for o in vis if o.tag == "chain"),
            "same_regs": sum(1 for o in vis if o.rs1 == o.rs2), "swaps": sum(1 for o in vis if o.tag == "swap_ab")}


def red_candidates(rng, ops, item):
    """(op, attribute, deviated value) of every deviation of the item, in a seed-drawn order."""
    if item not in RED_ITEMS:
        raise ValueError(f"unknown red item {item}; one of {RED_ITEMS}")
    if item == ITEM_CMUL:
        cands = [(op, "emit_value", op.value ^ 1) for op in ops if op.kind == "li" and op.item == item]
    else:
        cands = [(op, "emit_kind", alt) for op in ops if op.kind in RV32M_FORMS and op.item == item for alt in RV32M_FORMS if alt != op.kind]
    rng.shuffle(cands)
    return cands


def apply_red(rng, ops, item, expected):
    """The red fixture: the first candidate deviation whose emitted program changes report words of the item
    and of no other item (proved on the register model); the expectation keeps the true program."""
    exp = [r.expect for r in expected]
    for op, attr, dev in red_candidates(rng, ops, item):
        keep = getattr(op, attr)
        setattr(op, attr, dev)
        actual = [r.expect for r in simulate(ops, emitted=True)[0]]
        diff = [i for i, (a, e) in enumerate(zip(actual, exp)) if a != e]
        if diff and all(expected[i].item == item for i in diff):
            was = f"0x{keep:08x} -> 0x{dev:08x}" if attr == "emit_value" else f"{keep} -> {dev}"
            return f"{item}: {op.kind} x{op.rd} {attr} {was}; report idx {diff} deviate"
        setattr(op, attr, keep)
    raise AssertionError(f"no deviation of {item} changes one of its report words for this seed")


def body_lines(ops):
    """The .text lines after _start (the scenario and its report stores)."""
    L = [f"  li   x{EOT_REG}, GEN_MM_EOT_ADDR"]
    for op in ops:
        k = op.emit_kind
        if k == "li":
            L.append(f"  li   x{op.rd}, 0x{op.emit_value:08x}")
        elif k in RV32M_FORMS:
            L.append(f"  {k} x{op.rd}, x{op.rs1}, x{op.rs2}")
        elif k == "c_mul":
            L.append(f"  c_mul {op.rd}, {op.rs2}")
        elif k == "report":
            L.append(f"  sw   x{op.rs1}, 0(x{EOT_REG})")
        elif k == "filler":
            L.append(f"  {op.text}")
        else:
            raise ValueError(f"unknown instruction kind {k}")
    return L


def retire_floor(lines):
    """Honest lower bound of retirements at the end-of-test store: one per line (li counted as 1), less a
    margin for the instructions still in the pipeline at the store."""
    return max(len(lines) - 4, 1)


def check_coverage(p):
    """The plan carries what the items ask for; a generator drift fails here, not silently in a run."""
    for item in ITEMS:
        assert not p.missing[item], f"{item} directed floor incomplete: {p.missing[item][:5]}"
        assert p.items[item], f"{item} has no report word"
    for o in sum(p.obs.values(), []):
        assert o.form != "c_mul" or (o.rd in CREGS and o.rs2 in CREGS and o.rs1 == o.rd), f"c.mul register outside x8..x15: {o}"
        assert EOT_REG not in (o.rd, o.rs1, o.rs2) and not ({o.rd, o.rs1, o.rs2} & set(FILLER_REGS)), f"reserved register in a multiply: {o}"
    assert sum(1 for i, j, d in p.asym if d) >= 3, "TP-MUL-008: fewer than three swapped pairs with differing model results"
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
    units = build_units(rng)
    rng.shuffle(units)
    ops = []
    for unit in units:
        ops.extend(filler(rng) for _ in range(rng.choice((0, 0, 1, 1, 2))))
        ops.extend(unit)
    for op in ops:
        op.emit_kind, op.emit_value = op.kind, op.value
    reports, items, obs = simulate(ops)
    red_item = red_item_of(seed, red_item) if red else ""
    red_note = apply_red(rng, ops, red_item, reports) if red else ""
    p = Plan(int(seed), bool(red), ops, reports, len(reports), retire_floor(body_lines(ops)), items, obs,
             {i: floors(i, obs[i]) for i in ITEMS}, {i: summarize(i, obs[i]) for i in ITEMS}, asym_pairs(obs[ITEM_MULHSU_ASYM]),
             red_item, red_note)
    check_coverage(p)
    return p


def emit(p):
    L = [f"# gen_mul_mul_prog.py --seed {p.seed}{' --red --red-item ' + p.red_item if p.red else ''}: RV32M program of gen_test_mul_mul",
         "# k=" + str(p.k) + " report words (" + ", ".join(f"{i} {len(p.items[i])}" for i in ITEMS) + f"), gen_min_retired={p.min_retired}"]
    if p.red:
        L.append(f"# RED FIXTURE {p.red_note}; the expectation keeps the true program, so the {p.red_item} fire-check must fail")
    L += ['.include "gen_zc_insn.h"', '.include "gen_mmio_map.h"', "", ".section .text", ".globl _start", "_start:"]
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
    if red:   # the red fixture deviates in the program only: the expectation, k and the floor are the green plan's
        g = plan(a.seed)
        assert [r.expect for r in p.reports] == [r.expect for r in g.reports] and p.k == g.k and p.min_retired == g.min_retired, \
            "red plan expectations differ from the green plan"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(emit(p))
    counts = " ".join(f"{i}={s['reports']}/{s['observable']}" for i, s in p.summary.items())
    print(f"OK seed={a.seed} red={red} out={a.out} k={p.k} min_retired={p.min_retired} reports/observable per item: {counts}"
          + (f" red_item={p.red_item} red_note={p.red_note!r}" if red else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
