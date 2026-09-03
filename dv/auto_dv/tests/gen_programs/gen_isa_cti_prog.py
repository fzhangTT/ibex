#!/usr/bin/env python3
"""gen_isa_cti_prog: per-seed program generator of gen_test_isa_cti (plan group gen_isa_cti, AREA ISA:
control-transfer instructions; dv/auto_dv/docs/gen_test_plan.md TP-ISA-015..027, TP-ISA-053).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:isa_cti"): one
shuffled stream of control-transfer units and conditional branches, every outcome program-visible and stored RAW
to GEN_MM_EOT_ADDR:
  - a jump unit (jal, jalr, c.jal, c.jalr, c.jr, c.j, mret, fence.i) lands on its own block, which reports a
    per-unit random marker and jumps back to the return point; a unit with a link register then reports the
    link register itself (expected: the jump site's address gen_j<n> from the image sidecar plus the instruction
    length, so a link of pc + 4 where pc + 2 is due is a mismatch);
  - a conditional branch shifts its taken bit into an outcome register (acc = acc * 2 + taken), reported every
    32 branches and at the end (a lossless outcome vector; a wrong outcome or a wrong landing changes it);
  - the trap handler (mtvec base; the program takes no trap by design) counts every trap and keeps its mcause;
    the counter and the cause are the last two report words (TP-ISA-053: never a trap, never mcause 0);
  - misa is reported once (TP-ISA-053 precondition: the C bit).
Layout: `.option norvc` and `.option norelax` make every instruction 4 bytes except the explicit compressed
jumps and the 2-byte c.nop shims that place jump sites and landing blocks at both PC alignments (the shim
positions follow a byte-parity model of the emitted code that the test verifies against the sidecar).
Items and units: TP-ISA-015 jal (rd mix x0/x1/x5/other, forward/backward, near and far pools); TP-ISA-017
jal/jalr/c.jal/c.jalr links at both site alignments; TP-ISA-018 jalr (imm classes of W6, rs1 from lui/addi
or from a load, rd mix); TP-ISA-019 odd rs1 + imm sums (jalr with odd rs1 or odd imm, c.jr, c.jalr) with
even-sum controls; TP-ISA-020 jalr rd, rd, imm with 0..3 instructions between the write of rd and the jalr;
TP-ISA-023 branches over the W5 compare classes with taken/not-taken balanced by construction; TP-ISA-027 the
boundary classes, every (op, class) at least once; TP-ISA-053 the half-word-aligned targets of every kind plus
mret (mepc = target, MPP = M) and fence.i at a half-aligned pc, and the trap counter.
Red fixtures: `--red [--red-item <item>]` makes the PROGRAM deviate on one intent of one item while the
expectation keeps the true program and the byte layout stays (so exactly that item's fire-check fails):
015 one jal writes another register than the reported one; 017 one 32-bit jal x1 is emitted as c.jal plus a
c.nop pad (link pc + 2 where pc + 4 is due); 018 / 019 one target register points 4 bytes past the landing
block (the marker instruction is skipped); 020 one jalr rd, rd, 0 writes its link to another register (the
reported rd keeps the old value); 023 / 027 one branch is emitted as its complementary op (the outcome bit
flips); 053 the reserved nop slot is emitted as ecall (the handler counts one trap). red_item names the item;
None lets random.Random(f"{seed}:red") draw it.

CLI: python3 gen_isa_cti_prog.py --seed N --out <file.S> [--red [--red-item TP-ISA-0nn]]
"""
import argparse
import random
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dv.auto_dv.tests.gen_programs.gen_prog_const import CAUSE_ECALL_M, MISA_VALUE, MSTATUS_MPP_M, TOHOST_PASS, csr_hex  # noqa: E402

RNG_TAG = "program:isa_cti"
LAYOUT_TAG = "program:isa_cti:layout"
RED_TAG = "red"
MASK32 = 0xFFFFFFFF

I015, I017, I018, I019, I020, I023, I027, I053 = ("TP-ISA-015", "TP-ISA-017", "TP-ISA-018", "TP-ISA-019",
                                                  "TP-ISA-020", "TP-ISA-023", "TP-ISA-027", "TP-ISA-053")
BUILT_ITEMS = (I015, I017, I018, I019, I020, I023, I027, I053)
BRANCH_WORD = "BRANCH"           # outcome-window words: TP-ISA-023 and TP-ISA-027 read their own bits

# Registers: x28 EOT address, x29 branch outcome vector, x30 scratch address, x31 landing marker temp; the trap
# handler owns x24..x27 (scratch, last mcause, trap counter, scratch); x8..x15 hold the branch operand pool.
R_EOT, R_ACC, R_SCR, R_TMP = 28, 29, 30, 31
R_HS1, R_LASTC, R_TRAPS, R_HS0 = 24, 25, 26, 27
JREGS = (1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23)   # rd / rs1 of the jump units
P_ZERO, P_ONES, P_MIN, P_MAX = 8, 9, 10, 11                      # fixed pool values
P_NEG = (12, 13)                                                 # negative random pool values
P_POS = (14, 15)                                                 # positive random pool values
POOL_FIXED = {P_ZERO: 0, P_ONES: MASK32, P_MIN: 0x80000000, P_MAX: 0x7FFFFFFF}
LASTC_SENTINEL = 0x5A5A00FF      # never a legal mcause: the handler overwrites it on the first trap
FLOOR_MARGIN = 8                 # retirements still in flight at the end-of-test store
JAL_MIN, JAL_MAX = 500, 540      # TP-ISA-015 stimulus floor
JALR_MIN, JALR_MAX = 500, 540    # TP-ISA-018
N017_MIN, N017_MAX = 120, 140
ODD_PLAN_MIN = 50                # TP-ISA-019 asks >= 50 odd rs1 + imm sums
ODD_MIN, ODD_MAX = 60, 72        # drawn count, above the plan floor
CTRL_019 = 10                    # even-sum controls of TP-ISA-019
N020_MIN, N020_MAX = 40, 48
N053_MRET, N053_FENCEI, N053_CJ = 12, 12, 30
BR023_MIN, BR023_MAX = 2400, 2500
BR027_MIN, BR027_MAX = 700, 760
BR_WINDOW = 32                   # outcome bits per report word
HALF_TARGETS_MIN, ODD_SUMS_MIN = 100, 20   # TP-ISA-053 fire-check floors
FAR_JAL_FRACTION = 0.08          # jal units whose landing block sits in a far pool

BR_OPS = ("beq", "bne", "blt", "bge", "bltu", "bgeu")
COMPLEMENT = {"beq": "bne", "bne": "beq", "blt": "bge", "bge": "blt", "bltu": "bgeu", "bgeu": "bltu"}
NAMED_CLASSES = ("equal", "intmin_zero", "zero_intmin", "zero_ones", "ones_zero", "both_msb_eq", "slt_ugt", "sgt_ult")
JUMP_FORMS_017 = ("jal", "jalr", "c_jal", "c_jalr")
# Layer-1 tables (gen_test_plan.md "Layer-1 weight tables"): W5 compare classes, W6 jalr immediates, W4 rd classes
# with the item's named rd mix (x0, x1, x5, other) as the group-specific extremes.
W5 = {**{c: 1 for c in NAMED_CLASSES}, "rand": 6}
W6_JALR_IMM = {"zero": 1, "max_pos": 1, "min_neg": 1, "pos_rand": 3, "neg_rand": 3}
W4_RD_JAL = {"x0": 3, "x1": 3, "x5": 3, "other": 7}
W4_RD_JALR = {"x0": 1, "eq_rd": 2, "other": 13}
W_FILL_JUMP = {"none": 10, "small": 7, "large": 3}
W_FILL_BR = {"none": 6, "small": 3, "large": 1}
FILL_RANGES = {"none": (0, 0), "small": (1, 16), "large": (17, 120)}


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def s32(v):
    v &= MASK32
    return v - (1 << 32) if v & 0x80000000 else v


def li_len(v):
    """Instructions gas emits for li (32-bit): addi, lui, or lui + addi."""
    if -2048 <= s32(v) <= 2047:
        return 1
    return 1 if (v & 0xFFF) == 0 else 2


def branch_taken(op, a, b):
    a &= MASK32
    b &= MASK32
    return {"beq": a == b, "bne": a != b, "blt": s32(a) < s32(b), "bge": s32(a) >= s32(b), "bltu": a < b, "bgeu": a >= b}[op]


def cmp_class(a, b):
    """CG-ISA-007.cp_cmp_class of an operand pair (the covergroup's value rule)."""
    a &= MASK32
    b &= MASK32
    if a == b == 0x80000000:
        return "both_msb_eq"
    if a == b:
        return "equal"
    if a == 0x80000000 and b == 0:
        return "intmin_zero"
    if a == 0 and b == 0x80000000:
        return "zero_intmin"
    if a == 0 and b == MASK32:
        return "zero_ones"
    if a == MASK32 and b == 0:
        return "ones_zero"
    if s32(a) < s32(b) and a > b:
        return "slt_ugt"
    if s32(a) > s32(b) and a < b:
        return "sgt_ult"
    return "rand"


CLASS_REPS = {"equal": (7, 7), "intmin_zero": (0x80000000, 0), "zero_intmin": (0, 0x80000000), "zero_ones": (0, MASK32),
              "ones_zero": (MASK32, 0), "both_msb_eq": (0x80000000, 0x80000000), "slt_ugt": (0xFFFFFFF0, 0x10), "sgt_ult": (0x10, 0xFFFFFFF0)}


def admissible_classes(op, taken):
    """Classes that can give `op` the outcome `taken`: the named classes decide it by value; rand (unequal operands
    of one sign) is admissible except for beq taken and bne not taken, which need equal operands."""
    out = [c for c, (a, b) in CLASS_REPS.items() if branch_taken(op, a, b) == taken]
    if not ((op == "beq" and taken) or (op == "bne" and not taken)):
        out.append("rand")
    return out


@dataclass
class Sym:
    """Expected word = sidecar address of `symbol` + add (the test resolves it from the image)."""
    symbol: str
    add: int = 0


@dataclass
class Report:
    idx: int
    item: str
    expect: object          # int or Sym
    label: str


@dataclass
class Unit:
    kind: str               # jump | branch | slot
    item: str = ""
    n: int = 0              # unit number (labels gen_j<n>, gen_t<n>, gen_r<n>, gen_c<n>, gen_b<n>)
    form: str = ""          # jal jalr c_jal c_jalr c_jr c_j mret fencei | branch op
    rd: int = 0
    rs1: int = 0
    rs2: int = 0
    imm: int = 0            # jalr immediate
    odd: int = 0            # 1: rs1 + imm is odd (target = sum & ~1)
    control: bool = False   # TP-ISA-019 even-sum control (rs1 odd and imm odd)
    imm_class: str = ""
    rd_class: str = ""
    cmp_cls: str = ""       # branch compare class requested (rand may fall back to a named class when bound)
    taken: bool = False     # branch outcome requested (TP-ISA-023 balances by construction)
    cls: str = ""           # bound compare class (the value rule of CG-ISA-007)
    outcome: bool = False   # bound outcome
    fwd: bool = True        # landing block after (True) or before (False) the site
    far: bool = False       # landing block in a far pool (jal only)
    site_half: bool = False
    target_half: bool = False
    from_load: bool = False
    gap: int = 0            # TP-ISA-020: instructions between the write of rd and the jalr
    fill: int = 0           # nop words between site and landing block (never executed)
    marker: int = 0
    a: int = 0              # branch operand values at the branch
    b: int = 0
    emit_form: str = ""
    emit_rd: int = 0
    emit_adjust: int = 0    # extra bytes added to the la of the target register (red fixture)
    emit_slot: str = "nop"  # the reserved slot instruction (ecall in the TP-ISA-053 red)
    refresh: tuple = ()     # (pool register, new value) loaded before a branch
    bit: tuple = ()         # (report index, bit position) of a branch outcome


@dataclass
class Plan:
    seed: int
    red: bool
    units: list
    reports: list
    k: int
    min_retired: int
    items: dict             # item -> report indices (the item's own words)
    counts: dict
    red_item: str
    red_note: str
    pool_init: dict
    n_half_targets: int     # jump units and taken branches whose target is half-word aligned
    n_odd_sums: int
    text: list


def link_len(form):
    return 2 if form in ("c_jal", "c_jalr") else 4


def has_link(u):
    return u.form in JUMP_FORMS_017 and u.rd != 0


def odd_construction(u):
    """TP-ISA-019: rs1 = gen_t + odd - imm and gen_t is even, so rs1 is odd exactly when imm is even."""
    return "odd_rs1" if u.imm % 2 == 0 else "odd_imm"


# ---- unit builders -----------------------------------------------------------------------------------------------
def marker(rng):
    """A 32-bit marker that li always renders as lui + addi (low 12 bits non-zero, high part non-trivial)."""
    while True:
        v = rng.getrandbits(32)
        if (v & 0xFFF) not in (0, 0xFFF) and li_len(v) == 2 and v not in (LASTC_SENTINEL, MISA_VALUE):
            return v


def draw_fill(rng, table):
    lo, hi = FILL_RANGES[weighted(rng, table)]
    return rng.randint(lo, hi) if hi else 0


def jal_unit(rng, item, rd_class=None, far=None):
    rd_class = rd_class or weighted(rng, W4_RD_JAL)
    rd = {"x0": 0, "x1": 1, "x5": 5}.get(rd_class)
    if rd is None:
        rd = rng.choice([r for r in JREGS if r not in (1, 5)])
    far = (rng.random() < FAR_JAL_FRACTION) if far is None else far
    return Unit("jump", item, form="jal", rd=rd, rd_class=rd_class, fwd=bool(rng.getrandbits(1)), far=far,
                site_half=bool(rng.getrandbits(1)), target_half=bool(rng.getrandbits(1)),
                fill=0 if far else draw_fill(rng, W_FILL_JUMP), marker=marker(rng))


def jalr_imm(rng, cls):
    if cls == "zero":
        return 0
    if cls == "max_pos":
        return 2047
    if cls == "min_neg":
        return -2048
    if cls == "pos_rand":
        return rng.randrange(2, 2047, 2)
    if cls == "neg_rand":
        return -rng.randrange(2, 2047, 2)
    if cls == "odd":
        return rng.randrange(-2047, 2048, 2)
    raise ValueError(cls)


def jalr_unit(rng, item, imm_class=None, rd_class=None, from_load=None, odd=0, control=False):
    imm_class = imm_class or weighted(rng, W6_JALR_IMM)
    rd_class = rd_class or weighted(rng, W4_RD_JALR)
    rs1 = rng.choice(JREGS)
    rd = 0 if rd_class == "x0" else rs1 if rd_class == "eq_rd" else rng.choice([r for r in JREGS if r != rs1])
    from_load = (rng.random() < 0.25) if from_load is None else from_load
    return Unit("jump", item, form="jalr", rd=rd, rs1=rs1, imm=jalr_imm(rng, imm_class), odd=odd, control=control,
                imm_class=imm_class, rd_class=rd_class, fwd=bool(rng.getrandbits(1)), site_half=bool(rng.getrandbits(1)),
                target_half=bool(rng.getrandbits(1)), from_load=from_load, fill=draw_fill(rng, W_FILL_JUMP), marker=marker(rng))


def compressed_unit(rng, item, form, odd=0, target_half=None):
    rs1 = rng.choice(JREGS) if form in ("c_jr", "c_jalr") else 0
    rd = 1 if form in ("c_jal", "c_jalr") else 0
    th = bool(rng.getrandbits(1)) if target_half is None else target_half
    return Unit("jump", item, form=form, rd=rd, rs1=rs1, odd=odd, fwd=bool(rng.getrandbits(1)),
                site_half=bool(rng.getrandbits(1)), target_half=th, fill=rng.randint(0, 24), marker=marker(rng))


def build_015(rng):
    units = [jal_unit(rng, I015, rd_class=c) for c in W4_RD_JAL for _ in range(2)]
    units += [jal_unit(rng, I015) for _ in range(rng.randint(JAL_MIN, JAL_MAX) - len(units))]
    for u, fwd in ((units[-1], True), (units[-2], False)):   # both far pools are used whatever the draws
        u.far, u.fwd, u.fill = True, fwd, 0
    return units


def unit_017(rng, form, rd=None):
    if form == "jal":
        u = jal_unit(rng, I017, rd_class="x1" if rd == 1 else rng.choice(("x1", "x5", "other")), far=False)
    elif form == "jalr":
        u = jalr_unit(rng, I017, imm_class=rng.choice(("pos_rand", "neg_rand")), rd_class="other")
    else:
        u = compressed_unit(rng, I017, form)
    return u


def build_017(rng):
    units = []
    for form in JUMP_FORMS_017:
        for site_half in (False, True):
            units.append(unit_017(rng, form))
            units[-1].site_half = site_half
    units.append(unit_017(rng, "jal", rd=1))                  # the 32-bit jal x1 the red fixture compresses
    units += [unit_017(rng, rng.choice(JUMP_FORMS_017)) for _ in range(rng.randint(N017_MIN, N017_MAX) - len(units))]
    return units


def build_018(rng):
    units = [jalr_unit(rng, I018, imm_class=c, rd_class=r) for c in W6_JALR_IMM for r in W4_RD_JALR]
    units += [jalr_unit(rng, I018, from_load=True), jalr_unit(rng, I018, from_load=False)]
    units += [jalr_unit(rng, I018) for _ in range(rng.randint(JALR_MIN, JALR_MAX) - len(units))]
    return units


def build_019(rng):
    kinds = ("jalr_odd_rs1", "jalr_odd_imm", "c_jr", "c_jalr")
    units = []
    for i in range(rng.randint(ODD_MIN, ODD_MAX)):
        kind = kinds[i % 4] if i < 8 else rng.choice(kinds)
        if kind == "jalr_odd_rs1":
            units.append(jalr_unit(rng, I019, imm_class=rng.choice(("zero", "pos_rand", "neg_rand", "min_neg")), odd=1))
        elif kind == "jalr_odd_imm":
            u = jalr_unit(rng, I019, imm_class="pos_rand", odd=1)
            u.imm, u.imm_class = jalr_imm(rng, "odd"), "odd"
            units.append(u)
        else:
            units.append(compressed_unit(rng, I019, kind, odd=1))
    for _ in range(CTRL_019):                                  # both odd: rs1 odd and imm odd, an even sum (control)
        u = jalr_unit(rng, I019, imm_class="pos_rand", control=True)
        u.imm, u.imm_class = jalr_imm(rng, "odd"), "odd"
        units.append(u)
    return units


def build_020(rng):
    units = []
    for i in range(rng.randint(N020_MIN, N020_MAX)):
        u = jalr_unit(rng, I020, imm_class="zero" if i == 0 else None, rd_class="eq_rd", from_load=False)
        u.gap = i % 4 if i < 4 else rng.choice((0, 0, 1, 2, 3))
        units.append(u)
    return units


def build_053(rng):
    units = []
    for _ in range(N053_MRET):
        units.append(Unit("jump", I053, form="mret", fwd=bool(rng.getrandbits(1)), site_half=bool(rng.getrandbits(1)),
                          target_half=rng.random() < 0.7, fill=draw_fill(rng, W_FILL_JUMP), marker=marker(rng)))
    for _ in range(N053_FENCEI):
        h = bool(rng.getrandbits(1))
        units.append(Unit("jump", I053, form="fencei", site_half=h, target_half=h, marker=marker(rng)))
    for _ in range(N053_CJ):
        units.append(compressed_unit(rng, I053, "c_j", target_half=rng.random() < 0.7))
    return units


def branch_unit(rng, item, op, cls, taken=False):
    """A branch request; operands are bound to the pool when the stream is laid out (pool values evolve)."""
    return Unit("branch", item, form=op, cmp_cls=cls, taken=taken, fwd=bool(rng.getrandbits(1)),
                site_half=bool(rng.getrandbits(1)), target_half=bool(rng.getrandbits(1)), fill=draw_fill(rng, W_FILL_BR))


def build_023(rng):
    units = []
    for op in BR_OPS:                                          # floor: per op and outcome, min(3, admissible) classes
        for taken in (True, False):
            adm = admissible_classes(op, taken)
            units += [branch_unit(rng, I023, op, cls, taken) for cls in rng.sample(adm, min(3, len(adm)))]
    n = rng.randint(BR023_MIN, BR023_MAX)
    while len(units) < n:
        op = rng.choice(BR_OPS)
        taken = bool(rng.getrandbits(1))                       # balanced by construction
        adm = admissible_classes(op, taken)
        units.append(branch_unit(rng, I023, op, weighted(rng, {c: W5[c] for c in adm}), taken))
    return units


def build_027(rng):
    units = [branch_unit(rng, I027, op, cls) for op in BR_OPS for cls in NAMED_CLASSES]
    n = rng.randint(BR027_MIN, BR027_MAX)
    while len(units) < n:
        cls = rng.choice(NAMED_CLASSES) if rng.random() < 0.6 else "rand"
        units.append(branch_unit(rng, I027, rng.choice(BR_OPS), cls))
    return units


# ---- the operand pool of the branches ----------------------------------------------------------------------------
class Pool:
    def __init__(self, rng):
        self.rng = rng
        self.val = dict(POOL_FIXED)
        for r in P_NEG:
            self.val[r] = self.fresh(True)
        for r in P_POS:
            self.val[r] = self.fresh(False)
        self.init = dict(self.val)

    def fresh(self, negative):
        while True:
            v = self.rng.getrandbits(32)
            v = (v | 0x80000000) if negative else (v & 0x7FFFFFFF)
            if (v & 0xFFF) != 0 and li_len(v) == 2 and v not in self.val.values():
                return v

    def refresh(self):
        r = self.rng.choice(P_NEG + P_POS)
        self.val[r] = self.fresh(r in P_NEG)
        return (r, self.val[r])

    def zero_reg(self):
        return self.rng.choice((0, P_ZERO))

    def operands(self, cls, op, taken):
        """(rs1, rs2) of the class; for rand the one-sign pair whose values give `taken` (None if none does)."""
        rng = self.rng
        if cls == "equal":
            if rng.getrandbits(2) == 0:
                z = self.zero_reg()
                return (z, P_ZERO if z == 0 else 0)
            r = rng.choice((P_ONES, P_MAX) + P_NEG + P_POS)
            return (r, r)
        if cls == "both_msb_eq":
            return (P_MIN, P_MIN)
        if cls == "intmin_zero":
            return (P_MIN, self.zero_reg())
        if cls == "zero_intmin":
            return (self.zero_reg(), P_MIN)
        if cls == "zero_ones":
            return (self.zero_reg(), P_ONES)
        if cls == "ones_zero":
            return (P_ONES, self.zero_reg())
        if cls == "slt_ugt":
            return (rng.choice(P_NEG), rng.choice(P_POS))
        if cls == "sgt_ult":
            return (rng.choice(P_POS), rng.choice(P_NEG))
        pairs = [(P_NEG[0], P_NEG[1]), (P_NEG[1], P_NEG[0]), (P_POS[0], P_POS[1]), (P_POS[1], P_POS[0])]
        rng.shuffle(pairs)
        for a, b in pairs:
            if branch_taken(op, self.val[a], self.val[b]) == taken and cmp_class(self.val[a], self.val[b]) == "rand":
                return (a, b)
        return None

    def value(self, r):
        return 0 if r == 0 else self.val[r]


# ---- the layout walk: labels, expectations in execution order, byte parity, retirement count ---------------------
class Program:
    def __init__(self, seed, units):
        self.rng = random.Random(f"{int(seed)}:{LAYOUT_TAG}")   # the red re-walk draws the same values
        self.units = units
        self.pool = Pool(self.rng)
        self.L = []                  # .text lines from _start to the far pool after the end of test
        self.reports = []
        self.items = {i: [] for i in BUILT_ITEMS}
        self.n_exec = 0              # instructions on the executed path (the retirement floor)
        self.pos = 0                 # byte offset mod 4 of the next .text byte (the shim model)
        self.acc, self.n_br = 0, 0
        self.window = []             # branches of the open outcome window

    def report(self, item, expect, label):
        r = Report(len(self.reports), item, expect, label)
        self.reports.append(r)
        if item in self.items:
            self.items[item].append(r.idx)
        return r

    def ins(self, text, execd=True, nbytes=4):
        self.L.append("  " + text)
        self.n_exec += int(execd)
        self.pos = (self.pos + nbytes) % 4

    def li(self, reg, v, execd=True):
        self.n_exec += li_len(v) * int(execd)
        self.L.append(f"  li   x{reg}, 0x{v & MASK32:08x}")

    def la(self, reg, sym, execd=True):
        self.ins(f"la   x{reg}, {sym}", execd, 4)
        self.n_exec += int(execd)

    def addi_chain(self, reg, k):
        while k:
            step = max(-2048, min(2047, k))
            self.ins(f"addi x{reg}, x{reg}, {step}")
            k -= step

    def shim(self, want_half, execd=False):
        """One c.nop when the next byte does not have the wanted parity."""
        if (self.pos == 2) != want_half:
            self.ins(".2byte 0x0001", execd, 2)

    def fill(self, n):
        if n:
            self.L.append(f"  .fill {n}, 4, 0x00000013")

    def label(self, name, glob=True):
        if glob:
            self.L.append(f".globl {name}")
        self.L.append(f"{name}:")

    def compressed(self, text):
        self.L += ["  .option push", "  .option rvc"]
        self.ins(text, True, 2)
        self.L.append("  .option pop")

    def landing(self, u, record=True):
        """The landing block: marker report, then back to the return point (fence.i's target is the inline continuation).
        A far block is emitted in a pool and its report recorded at the jump site (execution order)."""
        self.shim(u.target_half)
        self.label(f"gen_t{u.n}")
        self.li(R_TMP, u.marker)
        self.ins(f"sw   x{R_TMP}, 0(x{R_EOT})")
        if record:
            self.marker_report(u)
        if u.form != "fencei":
            self.ins(f"j    gen_r{u.n}")

    def marker_report(self, u):
        self.report(u.item, u.marker, f"{u.form} unit {u.n} landing marker")

    def jump_setup(self, u):
        """Target register and privileged state before the site (jalr forms, c.jr/c.jalr, mret)."""
        if u.form in ("jalr", "c_jr", "c_jalr"):
            k = u.odd - (u.imm if u.form == "jalr" else 0)
            self.la(u.rs1, f"gen_t{u.n}" + (f"+{u.emit_adjust}" if u.emit_adjust else ""))
            self.addi_chain(u.rs1, k)
            if u.from_load:
                self.ins(f"sw   x{u.rs1}, 0(x{R_SCR})")
                self.ins(f"lw   x{u.rs1}, 0(x{R_SCR})")
            for g in range(u.gap):
                self.ins(("addi x{t}, x{t}, 1", "xori x{t}, x{t}, 5", "nop")[g % 3].format(t=R_TMP))
        elif u.form == "mret":
            self.la(R_HS0, f"gen_t{u.n}")
            self.ins(f"csrrw x0, {csr_hex('mepc')}, x{R_HS0}")
            self.li(R_HS1, MSTATUS_MPP_M)
            self.ins(f"csrrs x0, {csr_hex('mstatus')}, x{R_HS1}")

    def jump_site(self, u):
        self.shim(u.site_half, execd=u.fwd or u.far)
        self.label(f"gen_j{u.n}")
        f, rd = u.emit_form, u.emit_rd
        if f == "jal":
            self.ins(f"jal  x{rd}, gen_t{u.n}")
        elif f == "jalr":
            self.ins(f"jalr x{rd}, {u.imm}(x{u.rs1})")
        elif f == "c_jal":
            self.compressed(f"c.jal gen_t{u.n}")
        elif f == "c_jalr":
            self.compressed(f"c.jalr x{u.rs1}")
        elif f == "c_jr":
            self.compressed(f"c.jr x{u.rs1}")
        elif f == "c_j":
            self.compressed(f"c.j  gen_t{u.n}")
        elif f == "mret":
            self.ins("mret")
        elif f == "fencei":
            self.ins("fence.i")
        else:
            raise ValueError(f)
        self.label(f"gen_r{u.n}", glob=False)
        if link_len(f) < link_len(u.form):            # the red's compressed form keeps the byte layout with a pad
            self.ins(".2byte 0x0001", True, 2)
        if has_link(u):
            self.ins(f"sw   x{u.rd}, 0(x{R_EOT})")

    def link_report(self, u):
        if has_link(u):
            self.report(u.item, Sym(f"gen_j{u.n}", link_len(u.form)), f"{u.form} unit {u.n} link x{u.rd} = site + {link_len(u.form)}")

    def jump(self, u):
        """Text in layout order; reports in EXECUTION order: the landing marker runs before the return point's link store."""
        self.jump_setup(u)
        if u.form == "fencei":
            self.jump_site(u)
            self.landing(u)
            return
        if u.far:
            self.jump_site(u)
        elif u.fwd:
            self.jump_site(u)
            self.ins(f"j    gen_c{u.n}")
            self.fill(u.fill)
            self.landing(u, record=False)
            self.label(f"gen_c{u.n}", glob=False)
        else:
            self.ins(f"j    gen_b{u.n}")
            self.fill(u.fill)
            self.landing(u, record=False)
            self.fill(u.fill // 2)
            self.label(f"gen_b{u.n}", glob=False)
            self.jump_site(u)
        self.marker_report(u)
        self.link_report(u)

    def bind_operands(self, u):
        if self.rng.random() < 0.25:
            u.refresh = self.pool.refresh()
            self.li(u.refresh[0], u.refresh[1])
        want = bool(self.rng.getrandbits(1)) if (u.item == I027 and u.cmp_cls == "rand") else u.taken
        cls = u.cmp_cls
        ops = self.pool.operands(cls, u.form, want)
        if ops is None:                                        # no one-sign pair gives this outcome: a named class does
            cls = self.rng.choice([c for c in admissible_classes(u.form, want) if c != "rand"])
            ops = self.pool.operands(cls, u.form, want)
        u.rs1, u.rs2 = ops
        u.a, u.b = self.pool.value(u.rs1), self.pool.value(u.rs2)
        u.cls, u.outcome = cls, branch_taken(u.form, u.a, u.b)
        assert cmp_class(u.a, u.b) == u.cls, (u.cls, cmp_class(u.a, u.b), u.rs1, u.rs2)

    def branch(self, u):
        self.bind_operands(u)
        t = f"gen_t{u.n}"
        if u.fwd:
            self.shim(u.site_half, execd=True)
            self.label(f"gen_j{u.n}", glob=False)
            self.ins(f"{u.emit_form} x{u.rs1}, x{u.rs2}, {t}")
            self.ins(f"slli x{R_ACC}, x{R_ACC}, 1", execd=not u.outcome)
            self.ins(f"j    gen_c{u.n}", execd=not u.outcome)
            self.fill(u.fill)
            self.shim(u.target_half)
            self.label(t)
            self.ins(f"slli x{R_ACC}, x{R_ACC}, 1", execd=u.outcome)
            self.ins(f"ori  x{R_ACC}, x{R_ACC}, 1", execd=u.outcome)
            self.label(f"gen_c{u.n}", glob=False)
        else:
            self.ins(f"j    gen_b{u.n}")
            self.fill(u.fill)
            self.shim(u.target_half)
            self.label(t)
            self.ins(f"slli x{R_ACC}, x{R_ACC}, 1", execd=u.outcome)
            self.ins(f"ori  x{R_ACC}, x{R_ACC}, 1", execd=u.outcome)
            self.ins(f"j    gen_c{u.n}", execd=u.outcome)
            self.fill(u.fill // 2)
            self.shim(u.site_half)
            self.label(f"gen_b{u.n}", glob=False)
            self.label(f"gen_j{u.n}", glob=False)
            self.ins(f"{u.emit_form} x{u.rs1}, x{u.rs2}, {t}")
            self.ins(f"slli x{R_ACC}, x{R_ACC}, 1", execd=not u.outcome)
            self.label(f"gen_c{u.n}", glob=False)
        self.acc = ((self.acc << 1) | int(u.outcome)) & MASK32
        self.n_br += 1
        self.window.append(u)
        if len(self.window) == BR_WINDOW:
            self.acc_report()

    def acc_report(self):
        if not self.window:
            return
        self.ins(f"sw   x{R_ACC}, 0(x{R_EOT})")
        r = self.report(BRANCH_WORD, self.acc, f"branch outcome window ending at branch {self.n_br} ({len(self.window)} new bits)")
        n = len(self.window)
        for i, u in enumerate(self.window):
            u.bit = (r.idx, n - 1 - i)
        self.window = []

    def prologue(self):
        self.label("_start")
        self.ins(f"lui  x{R_EOT}, %hi(GEN_MM_EOT_ADDR)")
        self.ins(f"addi x{R_EOT}, x{R_EOT}, %lo(GEN_MM_EOT_ADDR)")
        for r, v in self.pool.init.items():
            self.li(r, v)
        for r, v in ((R_ACC, 0), (R_TRAPS, 0), (R_LASTC, LASTC_SENTINEL), (R_TMP, 0)):
            self.li(r, v)
        self.la(R_SCR, "gen_scratch")
        self.la(R_HS0, "gen_trap_handler")
        self.ins(f"ori  x{R_HS0}, x{R_HS0}, 1")
        self.ins(f"csrrw x0, {csr_hex('mtvec')}, x{R_HS0}")
        self.ins(f"csrrw x0, {csr_hex('mie')}, x0")
        self.ins(f"csrrs x{R_HS1}, {csr_hex('misa')}, x0")
        self.ins(f"sw   x{R_HS1}, 0(x{R_EOT})")
        self.report(I053, MISA_VALUE, "misa (C bit = 1)")
        self.ins("j    gen_main")

    def epilogue(self):
        self.acc_report()
        self.ins("nop")
        self.ins(f"sw   x{R_TRAPS}, 0(x{R_EOT})")
        self.report(I053, 0, "trap count (handler entries)")
        self.ins("nop")
        self.ins(f"sw   x{R_LASTC}, 0(x{R_EOT})")
        self.report(I053, LASTC_SENTINEL, "last mcause seen by the handler (sentinel: none)")
        self.ins(f"li   gp, {TOHOST_PASS}")
        self.la(5, "tohost")
        self.ins("sw   gp, 0(x5)")
        self.label("gen_end", glob=False)
        self.ins("j    gen_end", execd=False)

    def build(self):
        far_bwd = [u for u in self.units if u.kind == "jump" and u.far and not u.fwd]
        far_fwd = [u for u in self.units if u.kind == "jump" and u.far and u.fwd]
        self.prologue()
        self.label("gen_pool_before", glob=False)
        for u in far_bwd:
            self.landing(u, record=False)
        self.label("gen_main", glob=False)
        for u in self.units:
            if u.kind == "jump":
                self.jump(u)
            elif u.kind == "branch":
                self.branch(u)
            else:
                self.ins(u.emit_slot)
        self.epilogue()
        self.label("gen_pool_after", glob=False)
        for u in far_fwd:
            self.landing(u, record=False)
        return self


def check_coverage(p):
    """The plan carries what the items ask for; a generator drift fails here, not silently in a run."""
    U = [u for u in p.units if u.kind == "jump"]
    j015 = [u for u in U if u.item == I015]
    assert len(j015) >= JAL_MIN and {u.rd_class for u in j015} == set(W4_RD_JAL), "TP-ISA-015 rd classes / count"
    assert {(u.fwd, u.far) for u in j015} == {(True, False), (False, False), (True, True), (False, True)}, "TP-ISA-015 directions"
    assert {u.target_half for u in j015} == {True, False} and {u.site_half for u in j015} == {True, False}
    j017 = [u for u in U if u.item == I017]
    assert {(u.form, u.site_half) for u in j017} == {(f, h) for f in JUMP_FORMS_017 for h in (True, False)}, "TP-ISA-017 form x alignment"
    assert all(u.rd != 0 for u in j017) and any(u.form == "jal" and u.rd == 1 for u in j017)
    j018 = [u for u in U if u.item == I018]
    assert len(j018) >= JALR_MIN and {(u.imm_class, u.rd_class) for u in j018} >= {(c, r) for c in W6_JALR_IMM for r in W4_RD_JALR}
    assert {u.from_load for u in j018} == {True, False}
    j019 = [u for u in U if u.item == I019 and not u.control]
    assert len(j019) >= ODD_PLAN_MIN and all(u.odd == 1 for u in j019) and {u.form for u in j019} == {"jalr", "c_jr", "c_jalr"}
    assert {odd_construction(u) for u in j019 if u.form == "jalr"} == {"odd_rs1", "odd_imm"}, "TP-ISA-019 both odd-sum constructions"
    ctrl = [u for u in U if u.item == I019 and u.control]
    assert len(ctrl) == CTRL_019 and all(u.odd == 0 and u.imm % 2 == 1 for u in ctrl)
    j020 = [u for u in U if u.item == I020]
    assert len(j020) >= N020_MIN and all(u.rd == u.rs1 != 0 for u in j020) and {u.gap for u in j020} == {0, 1, 2, 3}
    assert any(u.imm == 0 for u in j020)
    assert {u.form for u in U if u.item == I053} == {"mret", "fencei", "c_j"}
    B = [u for u in p.units if u.kind == "branch"]
    b023 = [u for u in B if u.item == I023]
    assert len(b023) >= BR023_MIN, len(b023)
    for op in BR_OPS:
        for taken in (True, False):
            got = {u.cls for u in b023 if u.form == op and u.outcome == taken}
            assert len(got) >= min(3, len(admissible_classes(op, taken))), f"TP-ISA-023 {op} taken={taken}: classes {got}"
    b027 = [u for u in B if u.item == I027]
    assert {(u.form, u.cls) for u in b027} >= {(op, c) for op in BR_OPS for c in NAMED_CLASSES}, "TP-ISA-027 op x class"
    assert all(u.bit for u in B) and all(u.emit_form for u in U + B), "every branch has an outcome bit"
    assert p.n_half_targets >= HALF_TARGETS_MIN and p.n_odd_sums >= ODD_SUMS_MIN
    assert len(p.reports) == p.k and [r.idx for r in p.reports] == list(range(p.k))
    assert sum(1 for u in p.units if u.kind == "slot") == 1
    assert all(0 <= ord(c) < 128 for c in emit(p)), "non-ASCII in the emitted program"


def red_item_of(seed, red_item):
    if red_item is None:
        return random.Random(f"{int(seed)}:{RED_TAG}").choice(BUILT_ITEMS)
    if red_item not in BUILT_ITEMS:
        raise ValueError(f"unknown red item {red_item}; one of {BUILT_ITEMS}")
    return red_item


def apply_red(rng, units, item):
    """One program-only deviation of `item` that keeps every other observation and the byte layout."""
    U = [u for u in units if u.item == item]
    if item == I015:
        u = rng.choice([u for u in U if u.rd != 0])
        u.emit_rd = rng.choice([r for r in JREGS if r != u.rd])
        return f"{item}: jal unit {u.n} emitted with rd x{u.emit_rd} instead of x{u.rd}; its link word reports stale x{u.rd}"
    if item == I017:
        u = rng.choice([u for u in U if u.form == "jal" and u.rd == 1])
        u.emit_form = "c_jal"
        return f"{item}: jal x1 unit {u.n} emitted as c.jal + c.nop; its link is site + 2 where site + 4 is due"
    if item in (I018, I019):
        u = rng.choice([u for u in U if not u.control])
        u.emit_adjust = 4
        return f"{item}: unit {u.n} ({u.form}) target register points 4 bytes past gen_t{u.n}; its marker word deviates"
    if item == I020:
        u = rng.choice([u for u in U if u.imm == 0])
        u.emit_rd = rng.choice([r for r in JREGS if r != u.rd])
        return f"{item}: jalr rd, rd, 0 unit {u.n} emitted with link into x{u.emit_rd}; the reported x{u.rd} keeps the old value"
    if item in (I023, I027):
        u = rng.choice(U)
        u.emit_form = COMPLEMENT[u.form]
        return f"{item}: branch unit {u.n} emitted as {u.emit_form} instead of {u.form}; outcome bit {u.bit} flips"
    if item == I053:
        s = next(u for u in units if u.kind == "slot")
        s.emit_slot = "ecall"
        return f"{item}: the reserved slot is emitted as ecall; the handler counts one trap (mcause {CAUSE_ECALL_M})"
    raise ValueError(item)


def plan(seed, red=False, red_item=None):
    rng = random.Random(f"{int(seed)}:{RNG_TAG}")
    units = build_015(rng) + build_017(rng) + build_018(rng) + build_019(rng) + build_020(rng) + build_053(rng) + build_023(rng) + build_027(rng)
    units.append(Unit("slot"))
    rng.shuffle(units)
    for n, u in enumerate(units):
        u.n, u.emit_form, u.emit_rd = n, u.form, u.rd
    prog = Program(seed, units).build()
    reports = [Report(r.idx, r.item, r.expect, r.label) for r in prog.reports]
    n_half = sum(1 for u in units if u.kind == "jump" and u.target_half) + sum(1 for u in units if u.kind == "branch" and u.outcome and u.target_half)
    n_odd = sum(1 for u in units if u.kind == "jump" and u.odd == 1)
    counts = {"jump_units": sum(1 for u in units if u.kind == "jump"), "branches": prog.n_br, "n_exec": prog.n_exec,
              "half_targets": n_half, "odd_sums": n_odd}
    counts.update({i: sum(1 for u in units if u.item == i) for i in BUILT_ITEMS})
    p = Plan(int(seed), bool(red), units, reports, len(reports), max(prog.n_exec - FLOOR_MARGIN, 1), prog.items, counts,
             "", "", prog.pool.init, n_half, n_odd, prog.L)
    if red:
        p.red_item = red_item_of(seed, red_item)
        p.red_note = apply_red(rng, units, p.red_item)
        again = Program(seed, units).build()                   # the deviated text; the expectation stays the green walk's
        assert [(r.item, r.expect, r.label) for r in again.reports] == [(r.item, r.expect, r.label) for r in reports], "red walk changed the expectation"
        p.text = again.L
    check_coverage(p)
    return p


def handler_lines():
    """mtvec base: count the trap, keep mcause, step mepc over the trapping instruction (2 or 4 bytes), return to M-mode."""
    return [".globl gen_trap_handler", "gen_trap_handler:",
            f"  csrrs x{R_HS0}, {csr_hex('mcause')}, x0",
            f"  addi x{R_TRAPS}, x{R_TRAPS}, 1",
            f"  mv   x{R_LASTC}, x{R_HS0}",
            f"  csrrs x{R_HS0}, {csr_hex('mepc')}, x0",
            f"  lhu  x{R_HS1}, 0(x{R_HS0})",
            f"  andi x{R_HS1}, x{R_HS1}, 3",
            f"  addi x{R_HS1}, x{R_HS1}, -3",
            f"  addi x{R_HS0}, x{R_HS0}, 2",
            f"  bnez x{R_HS1}, gen_h_step",
            f"  addi x{R_HS0}, x{R_HS0}, 2",
            "gen_h_step:",
            f"  csrrw x0, {csr_hex('mepc')}, x{R_HS0}",
            f"  li   x{R_HS1}, 0x{MSTATUS_MPP_M:x}",
            f"  csrrs x0, {csr_hex('mstatus')}, x{R_HS1}",
            "  mret"]


def emit(p):
    L = [f"# gen_isa_cti_prog.py --seed {p.seed}{' --red --red-item ' + p.red_item if p.red else ''}: control-transfer program of gen_test_isa_cti",
         f"# k={p.k} report words, {p.counts['jump_units']} jump units, {p.counts['branches']} branches, gen_min_retired={p.min_retired}"]
    if p.red:
        L.append(f"# RED FIXTURE {p.red_note}; the expectation keeps the true program, so the {p.red_item} fire-check must fail")
    L += ['.include "gen_mmio_map.h"', ".option norvc", ".option norelax", "", ".section .text", ".p2align 8"]
    L += handler_lines()
    L += p.text
    L += ["", ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
          ".align 2", ".globl gen_scratch", "gen_scratch: .word 0", ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--red", action="store_true", help="emit the TDD red fixture (one item's program deviates)")
    ap.add_argument("--red-item", choices=BUILT_ITEMS, help="the item the red fixture deviates on (default: the seed draws it); implies --red")
    a = ap.parse_args()
    red = a.red or a.red_item is not None
    p = plan(a.seed, red, a.red_item)
    if red:
        g = plan(a.seed)
        assert [(r.item, r.expect, r.label) for r in p.reports] == [(r.item, r.expect, r.label) for r in g.reports], "red plan expectations differ"
        assert p.k == g.k and p.min_retired == g.min_retired and p.items == g.items, "red plan k / min_retired / items differ"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(emit(p))
    print(f"OK seed={a.seed} red={red} out={a.out} k={p.k} min_retired={p.min_retired} {p.counts}"
          + (f" red_item={p.red_item} red_note={p.red_note!r}" if red else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
