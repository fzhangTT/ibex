#!/usr/bin/env python3
"""gen_cmp_zcmp_basic_prog: per-seed program generator of gen_test_cmp_zcmp_basic (plan group
gen_cmp_zcmp_basic: TP-CMP-039..043, 045..050, 052, 053, 055, 066, 069, 073).

plan(seed, red=False) draws the scenario list from random.Random(f"{seed}:program:gen_cmp_zcmp_basic")
and runs a Python model of the Zcmp semantics (tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc,
RV32I column: register list ra, s0-s11 = x1, x8, x9, x18..x27; stack_adj = stack_adj_base(rlist) +
16 * spimm with base 16/32/48/64 for rlist 4-7/8-11/12-14/15; cm.push stores the list top at sp - 4
and ra at sp - 4N then sp -= stack_adj; cm.pop loads register k from sp + stack_adj - 4k then
sp += stack_adj; cm.popret returns to the loaded ra; cm.popretz also writes a0 = 0; cm.mvsa01 moves
a0/a1 into two sreg' registers and cm.mva01s moves two sreg' registers into a0/a1, sreg' 0..7 = x8,
x9, x18..x23) beside the emitted assembly, so every report word has an expectation derived from
intent. The stack layout was cross-checked on Spike (dv/auto_dv/evidence/gen_t025_stim_tooling.md
Section 2: list top at sp_old - 4, ra at sp_old - stack_adj_base).

emit(plan) renders RV32IMC assembly for the lowRISC gcc 10.2 toolchain: the Zcmp halfwords come from
gen_zc_insn.h (the assembler knows no Zc), the program keeps its observations in a result buffer
(tp = write pointer, never touched by Zcmp) and stores them as RAW words to GEN_MM_EOT_ADDR in plan
order at the end, then tohost 1. Report words: sp before and after every frame instruction, the whole
frame read back after a cm.push (list slots and the poison the program wrote to the other slots), all
13 rlist-capable registers after a pop, the marker the return target stores (a decoy block is reached
only through the stale ra), a0 after cm.popretz, the eight sreg' after cm.mvsa01, a0/a1 after
cm.mva01s, minstret before and after one cm.* of each kind.

red=True deviates the PROGRAM on one intent (one plain cm.push is emitted with the other spimm bit) while
the plan keeps the true expectation, so the test's fire-check must fail (TDD red fixture).

CLI: python3 gen_cmp_zcmp_basic_prog.py --seed N --out <file.S> [--red]
"""
import argparse
import random
from dataclasses import dataclass, field
from pathlib import Path

MASK = 0xFFFFFFFF
TAG = "program:gen_cmp_zcmp_basic"

# ---- Zcmp semantics (zcmp.adoc, RV32I column) --------------------------------------------------
RLIST_ORDER = (1, 8, 9, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27)   # ra, s0-s11 in list order
SREGS = (8, 9, 18, 19, 20, 21, 22, 23)                             # sreg' 0..7
RLISTS = tuple(range(4, 16))
SPIMMS = (0, 1, 2, 3)
ALL_COMBOS = frozenset((r, s) for r in RLISTS for s in SPIMMS)
FRAME_KINDS = ("push", "pop", "popret", "popretz")
RET_KINDS = ("popret", "popretz")
MOVE_KINDS = ("mvsa01", "mva01s")
CM_KINDS = FRAME_KINDS + MOVE_KINDS
B2B_KINDS = ("b2b_push_pop", "b2b_pop_push", "b2b_mvsa01_mva01s", "b2b_mva01s_mvsa01")
HAZ_VARIANTS = ("haz_store_slot", "haz_alu_reg", "haz_load_reg", "haz_load_mv")
STACK_BYTES = 2048      # gen_stack area; a frame (<= 112 bytes) keeps >= 128 bytes to both ends
FRAME_MAX = 112

# Layer-1 tables of gen_test_plan.md "Layer-1 weight tables" this group uses (transcribed once):
# W4 register indices: Zcmp rlist uniform over 4..15, spimm uniform over 0..3 (the push/pop enumerations
#     are a shuffled full set, the other draws uniform); sreg' fields uniform.
# W8 Zc immediates and stack geometry: sp[1:0] aligned only (the misaligned-sp items are elsewhere), frame
#     contents random with a checkable pattern: the value classes below, every word distinct, no 0/all-ones.
# W6 control-transfer targets: return-target alignment word/half 1:1 (odd ra excluded: B13 owns it).
W8_VALUE_CLASSES = {"pos_rand": 4, "neg_rand": 4, "lane_pattern": 1, "single_bit": 1}
W6_RET_ALIGN = {0: 1, 2: 1}
FILLER = ("addi a2, a3, {imm}", "xori a3, a2, {imm}", "slli a4, a5, {sh}", "srli a5, a4, {sh}",
          "add a2, a2, a4", "sub a3, a5, a2", "andi a4, a3, {imm}", "or a5, a2, a3")


def weighted(rng, table):
    """Layer-1 weighted class draw (gen_test_lib.Weighted semantics, local so the CLI needs no TB import)."""
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def rlist_regs(rlist):
    """Registers of an rlist in list order (ra first); rlist 15 adds s10 and s11 together."""
    return RLIST_ORDER[:13 if rlist == 15 else rlist - 3]


def stack_adj_base(rlist):
    return 16 if rlist <= 7 else 32 if rlist <= 11 else 48 if rlist <= 14 else 64


def stack_adj(rlist, spimm):
    return stack_adj_base(rlist) + 16 * spimm


STACK_ADJ_VALUES = frozenset(stack_adj(r, s) for r, s in ALL_COMBOS)   # 16, 32, ..., 112


def push_slots(rlist):
    """(offset from sp_old, register) of each cm.push store: list top at -4, ra at -4N."""
    regs = rlist_regs(rlist)
    return [(-4 * k, r) for k, r in enumerate(reversed(regs), 1)]


def pop_slots(rlist, spimm):
    """(offset from sp_old, register) of each cm.pop load: list top at stack_adj - 4, ra at stack_adj - 4N."""
    adj = stack_adj(rlist, spimm)
    regs = rlist_regs(rlist)
    return [(adj - 4 * k, r) for k, r in enumerate(reversed(regs), 1)]


# ---- plan data ------------------------------------------------------------------------------
@dataclass
class Report:
    idx: int
    sc: int              # scenario index the word belongs to
    kind: str            # data (exact word) | sp (offset from gen_stack) | sym (label) | ctr0/ctr1 (minstret pair)
    expect: object       # int, int offset, label name, or the expected minstret delta (ctr1)
    tag: str


@dataclass
class Scenario:
    idx: int
    kind: str
    variant: str = "plain"      # plain | haz_* | minstret | ft (fall-through cm.* after a ret) | ft_inner
    rlist: int = 0
    spimm: int = 0
    r1s: int = 0
    r2s: int = 0
    align: int = 0              # return-target address modulo 4 (ret kinds, ft resume label)
    sp: int = 0                 # sp before the cm.*, as an offset from gen_stack
    inner: object = None        # ft: the cm.* at the ret's fall-through halfword
    aux: dict = field(default_factory=dict)
    reports: list = field(default_factory=list)
    target: str = ""
    decoy: str = ""
    good: int = 0
    bad: int = 0
    decoy_mark: int = 0


@dataclass
class Plan:
    seed: int
    red: bool
    scenarios: list
    reports: list
    k: int
    min_retired: int
    lines: list
    red_note: str


def describe(sc):
    if sc.kind in FRAME_KINDS or sc.kind in ("b2b_push_pop", "b2b_pop_push"):
        return f"{sc.kind}#{sc.idx} rlist={sc.rlist} spimm={sc.spimm} {sc.variant}"
    return f"{sc.kind}#{sc.idx} r1s={sc.r1s} r2s={sc.r2s} {sc.variant}"


# ---- emitter: assembly text and the intent model advance together in execution order ---------
class _Emitter:
    def __init__(self, rng, red):
        self.rng = rng
        self.red = red
        self.lines = []
        self.reports = []
        self.scenarios = []
        self.retired = 0          # retirement floor: one per emitted instruction on the executed path
        self.regs = {}            # x -> int value or label name
        self.mem = {}             # gen_stack offset -> int value or label name
        self.sp = None            # sp as an offset from gen_stack
        self.base = None          # the offset t0 holds (sp before the cm.*)
        self.used = set()         # every drawn value: all data words of the program are distinct
        self.pending = 0
        self.nlabel = 0
        self.nmark = 0
        self.cur = None
        self.pfx = ""
        self.red_target = None
        self.red_note = ""

    # -- text
    def ins(self, text, retired=True):
        self.lines.append("  " + text)
        if retired:
            self.retired += 1

    def raw(self, text):
        self.lines.append(text)

    def glabel(self, stem):
        self.nlabel += 1
        return f"gen_{stem}_{self.nlabel}"

    def place(self, name):
        self.raw(f".globl {name}")
        self.raw(f"{name}:")

    def align_target(self, align):
        self.raw(".balign 4")
        if align == 2:
            self.raw("  c.nop")

    def parity(self):
        """Perturb the address parity of the following cm.* halfword (fall-through alignment varies)."""
        if self.rng.random() < 0.5:
            self.ins("c.nop")

    def filler(self):
        """Unrelated instructions on a2..a5 around the scenario (never a tracked register)."""
        for _ in range(self.rng.choice((0, 0, 1, 1, 2, 3))):
            self.ins(self.rng.choice(FILLER).format(imm=self.rng.randrange(-2048, 2048), sh=self.rng.randrange(32)))

    # -- records (RAW observations into the result buffer; the expectation is the model's)
    def _rec(self, xreg, kind, expect, tag):
        self.ins(f"sw x{xreg}, {4 * self.pending}(tp)")
        rep = Report(len(self.reports), self.cur.idx, kind, expect, self.pfx + tag)
        self.reports.append(rep)
        self.cur.reports.append(rep.idx)
        self.pending += 1

    def rec(self, xreg, value, tag):
        self._rec(xreg, "sym" if isinstance(value, str) else "data", value, tag)

    def rec_sp(self, tag):
        self._rec(2, "sp", self.sp, tag)

    def flush(self):
        if self.pending:
            self.ins(f"addi tp, tp, {4 * self.pending}")
            self.pending = 0

    # -- values and state
    def value(self):
        while True:
            cls = weighted(self.rng, W8_VALUE_CLASSES)
            if cls == "pos_rand":
                v = self.rng.randrange(1, 1 << 31)
            elif cls == "neg_rand":
                v = self.rng.randrange(1 << 31, MASK)
            elif cls == "lane_pattern":
                b = self.rng.sample(range(1, 256), 4)
                v = b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)
            else:
                v = 1 << self.rng.randrange(32)
            if v not in self.used and v not in (0, MASK):
                self.used.add(v)
                return v

    def marker(self):
        self.nmark += 1
        return self.nmark

    def set_reg(self, r, v):
        self.ins(f"li x{r}, 0x{v:08x}")
        self.regs[r] = v

    def pick_sp(self):
        return self.rng.randrange(FRAME_MAX + 16, STACK_BYTES - FRAME_MAX - 16 + 1, 4)

    def set_sp(self, off):
        self.ins("la sp, gen_stack")
        self.ins(f"addi sp, sp, {off}")
        self.ins("mv t0, sp")          # t0 = sp before the cm.*: base of every frame fill and read-back
        self.sp = off
        self.base = off

    def fill(self, offs):
        """Write a distinct arithmetic word pattern to the slots at t0 + off (W8: checkable frame contents)."""
        while True:
            start = self.value()
            step = self.rng.randrange(0x101, 0x7F1, 2)
            words = [(start + k * step) & MASK for k in range(len(offs))]
            rest = set(words[1:])
            if len(rest) == len(offs) - 1 and not (rest & self.used) and 0 not in rest and MASK not in rest:
                break
        self.used.update(words)
        self.ins(f"li t2, 0x{words[0]:08x}")
        for i, off in enumerate(offs):
            if i:
                self.ins(f"addi t2, t2, {step}")
            self.ins(f"sw t2, {off}(t0)")
            self.mem[self.base + off] = words[i]

    def readback(self, offs):
        for off in offs:
            self.ins(f"lw t1, {off}(t0)")
            self.rec(6, self.mem.get(self.base + off, 0), f"frame[sp_old{off:+d}]")

    # -- the cm.* instruction: text and model kept apart (the ft layout emits before it executes)
    def cm_text(self, sc, kind=None, deviate=False):
        kind = kind or sc.kind
        if kind in FRAME_KINDS:
            return f"cm_{kind} {sc.rlist}, {sc.spimm ^ 1 if deviate else sc.spimm}"
        return f"cm_{kind} {sc.r1s}, {sc.r2s}"

    def model_push(self, rlist, spimm):
        for off, r in push_slots(rlist):
            self.mem[self.sp + off] = self.regs[r]
        self.sp -= stack_adj(rlist, spimm)

    def model_pop(self, rlist, spimm):
        for off, r in pop_slots(rlist, spimm):
            self.regs[r] = self.mem.get(self.sp + off, 0)
        self.sp += stack_adj(rlist, spimm)

    def cm_model(self, kind, sc):
        if kind == "push":
            self.model_push(sc.rlist, sc.spimm)
        elif kind in ("pop", "popret"):
            self.model_pop(sc.rlist, sc.spimm)
        elif kind == "popretz":
            self.model_pop(sc.rlist, sc.spimm)
            self.regs[10] = 0
        elif kind == "mvsa01":
            a0, a1 = self.regs[10], self.regs[11]
            self.regs[sc.r1s] = a0
            self.regs[sc.r2s] = a1
        else:
            self.regs[10] = self.regs[sc.r1s]
            self.regs[11] = self.regs[sc.r2s]

    # -- scenario pieces
    def prep_ret(self, sc, target=None):
        n = self.marker()
        sc.target = target or self.glabel("ret_target")
        sc.decoy = self.glabel("ret_decoy")
        sc.good, sc.bad, sc.decoy_mark = 0x600D0000 | n, 0x0BAD0000 | n, 0xDEC00000 | n

    def pre_frame(self, sc, kind):
        sc.sp = self.pick_sp()
        self.set_sp(sc.sp)
        adj = stack_adj(sc.rlist, sc.spimm)
        nwords = adj // 4
        if kind == "push":
            self.fill([-4 * k for k in range(1, nwords + 1)])           # poison: an extra or misplaced store is visible
            for r in rlist_regs(sc.rlist):
                self.set_reg(r, self.value())                            # distinct fresh list registers
        else:
            self.fill([adj - 4 * k for k in range(1, nwords + 1)])      # the frame the pop reads
            if kind in RET_KINDS:
                ra_off = adj - 4 * len(rlist_regs(sc.rlist))
                self.ins(f"la t3, {sc.target}")
                self.ins(f"sw t3, {ra_off}(t0)")
                self.mem[self.base + ra_off] = sc.target
                self.ins(f"la x1, {sc.decoy}")                           # stale ra: the decoy marker would show it was used
                self.regs[1] = sc.decoy
                self.ins(f"li t1, 0x{sc.good:08x}")
                if kind == "popretz":
                    self.set_reg(10, self.value())                       # a0 nonzero before cm.popretz
        self.filler()
        self.rec_sp("sp_old")

    def post_frame(self, sc, kind):
        if kind in RET_KINDS:
            self.rec(6, sc.good, "ret_marker")
            if kind == "popretz":
                self.rec(10, 0, "a0")
        self.rec_sp("sp_new")
        if kind == "push":
            self.readback([-4 * k for k in range(1, stack_adj(sc.rlist, sc.spimm) // 4 + 1)])
        else:
            for r in RLIST_ORDER:
                self.rec(r, self.regs[r], f"x{r}")

    def pre_move(self, sc, kind):
        if kind == "mvsa01":
            self.set_reg(10, self.value())
            self.set_reg(11, self.value())
        else:
            for r in sorted({sc.r1s, sc.r2s}):
                self.set_reg(r, self.value())
        self.filler()

    def post_move(self, sc, kind):
        if kind == "mvsa01":
            for r in SREGS:
                self.rec(r, self.regs[r], f"x{r}")
        else:
            self.rec(10, self.regs[10], "a0")
            self.rec(11, self.regs[11], "a1")

    def post_moves_all(self):
        self.rec(10, self.regs[10], "a0")
        self.rec(11, self.regs[11], "a1")
        for r in SREGS:
            self.rec(r, self.regs[r], f"x{r}")

    def ret_tail(self, sc, place_target=True):
        """After a cm.popret/popretz halfword: the never-executed fall-through and decoy blocks, then the target."""
        self.ins(f"li t1, 0x{sc.bad:08x}", retired=False)
        self.ins(f"j {sc.target}", retired=False)
        self.place(sc.decoy)
        self.ins(f"li t1, 0x{sc.decoy_mark:08x}", retired=False)
        self.ins(f"j {sc.target}", retired=False)
        if place_target:
            self.align_target(sc.align)
            self.place(sc.target)

    def hazard(self, sc):
        """TP-CMP-069 producers immediately before the cm.*: the value must reach the micro-op."""
        v = sc.variant
        if v == "haz_store_slot":
            off, r = self.rng.choice(pop_slots(sc.rlist, sc.spimm))
            w = self.value()
            self.ins(f"li t3, 0x{w:08x}")
            self.ins(f"sw t3, {off}(t0)")
            self.mem[self.base + off] = w
            sc.aux["haz"] = f"sw slot sp_old{off:+d} (x{r}) then cm.pop"
        elif v == "haz_alu_reg":
            r = self.rng.choice(rlist_regs(sc.rlist))
            imm = self.rng.choice([i for i in range(-2048, 2048) if i])
            self.ins(f"xori x{r}, x{r}, {imm}")
            self.regs[r] = self.regs[r] ^ (imm & MASK)
            sc.aux["haz"] = f"xori x{r} then cm.push"
        elif v == "haz_load_reg":
            r = self.rng.choice(rlist_regs(sc.rlist))
            w = self.value()
            self.ins(f"li t3, 0x{w:08x}")
            self.ins("sw t3, 0(t4)")
            self.ins(f"lw x{r}, 0(t4)")
            self.regs[r] = w
            sc.aux["haz"] = f"lw x{r} then cm.push"
        elif v == "haz_load_mv":
            r = sc.aux["load_reg"]
            w = self.value()
            self.ins(f"li t3, 0x{w:08x}")
            self.ins("sw t3, 0(t4)")
            self.ins(f"lw x{r}, 0(t4)")
            self.regs[r] = w
            sc.aux["haz"] = f"lw x{r} then cm.mva01s"

    # -- scenario emitters
    def emit_simple(self, sc):
        self.cur = sc
        kind = sc.kind
        frame = kind in FRAME_KINDS
        if kind in RET_KINDS:
            self.prep_ret(sc)
        (self.pre_frame if frame else self.pre_move)(sc, kind)
        if kind in RET_KINDS:
            self.parity()
        self.hazard(sc)
        if sc.variant == "minstret":
            self.ins("csrr t5, minstret")
        deviate = self.red and sc.idx == self.red_target
        if deviate:
            self.red_note = (f"scenario {sc.idx} cm.push rlist {sc.rlist}: planned spimm {sc.spimm}, emitted spimm "
                             f"{sc.spimm ^ 1} (sp_new off by 16; the plan keeps the true expectation)")
        self.ins(self.cm_text(sc, deviate=deviate))
        self.cm_model(kind, sc)
        if kind in RET_KINDS:
            self.ret_tail(sc)
        if sc.variant == "minstret":
            self.ins("csrr t6, minstret")
        (self.post_frame if frame else self.post_move)(sc, kind)
        if sc.variant == "minstret":
            self._rec(30, "ctr0", 0, "minstret_before")
            self._rec(31, "ctr1", 2, "minstret_after")
        self.flush()

    def emit_ft(self, sc):
        """TP-CMP-073: the halfword at the ret's PC + 2 is another cm.*, executed later through a jump."""
        self.cur = sc
        inner = sc.inner
        self.prep_ret(sc)
        self.pre_frame(sc, sc.kind)
        self.parity()
        self.ins(self.cm_text(sc))
        self.cm_model(sc.kind, sc)
        ft, resume = self.glabel("ft"), self.glabel("ft_resume")
        self.place(ft)
        self.ins(self.cm_text(inner))                 # the fall-through cm.*; retires only when reached via j ft
        if inner.kind in RET_KINDS:
            self.prep_ret(inner, target=resume)
            self.ret_tail(inner, place_target=False)
        else:
            self.ins(f"j {resume}")
        self.ret_tail(sc)
        self.post_frame(sc, sc.kind)
        self.flush()
        self.pfx = "ft_inner:"
        (self.pre_frame if inner.kind in FRAME_KINDS else self.pre_move)(inner, inner.kind)
        self.ins(f"j {ft}")
        self.cm_model(inner.kind, inner)
        self.align_target(inner.align)
        self.place(resume)
        (self.post_frame if inner.kind in FRAME_KINDS else self.post_move)(inner, inner.kind)
        self.flush()
        self.pfx = ""

    def emit_b2b(self, sc):
        """TP-CMP-066 back-to-back patterns: nothing between the two cm.* instructions."""
        self.cur = sc
        if sc.kind == "b2b_push_pop":
            self.pre_frame(sc, "push")
            self.ins(self.cm_text(sc, "push"))
            self.cm_model("push", sc)
            self.ins(self.cm_text(sc, "pop"))
            self.cm_model("pop", sc)
            self.rec_sp("sp_new")
            for r in RLIST_ORDER:
                self.rec(r, self.regs[r], f"x{r}")
            self.readback([-4 * k for k in range(1, stack_adj(sc.rlist, sc.spimm) // 4 + 1)])
        elif sc.kind == "b2b_pop_push":
            self.pre_frame(sc, "pop")
            self.ins(self.cm_text(sc, "pop"))
            self.cm_model("pop", sc)
            r2, s2 = sc.aux["rlist2"], sc.aux["spimm2"]
            self.ins(f"cm_push {r2}, {s2}")
            self.model_push(r2, s2)
            self.rec_sp("sp_new")
            for r in RLIST_ORDER:
                self.rec(r, self.regs[r], f"x{r}")
            adj1 = stack_adj(sc.rlist, sc.spimm)
            self.readback([adj1 - 4 * k for k in range(1, stack_adj(r2, s2) // 4 + 1)])
        elif sc.kind == "b2b_mvsa01_mva01s":
            self.pre_move(sc, "mvsa01")
            self.ins(self.cm_text(sc, "mvsa01"))
            self.cm_model("mvsa01", sc)
            r1, r2 = sc.aux["r1s2"], sc.aux["r2s2"]
            self.ins(f"cm_mva01s {r1}, {r2}")
            self.regs[10], self.regs[11] = self.regs[r1], self.regs[r2]
            self.post_moves_all()
        else:
            self.pre_move(sc, "mva01s")
            self.ins(self.cm_text(sc, "mva01s"))
            self.cm_model("mva01s", sc)
            r1, r2 = sc.aux["r1s2"], sc.aux["r2s2"]
            self.ins(f"cm_mvsa01 {r1}, {r2}")
            a0, a1 = self.regs[10], self.regs[11]
            self.regs[r1] = a0
            self.regs[r2] = a1
            self.post_moves_all()
        self.flush()

    # -- the scenario list of one seed
    def draw_scenarios(self):
        rng = self.rng
        scs = []

        def add(kind, variant="plain", **kw):
            sc = Scenario(idx=len(scs), kind=kind, variant=variant, **kw)
            scs.append(sc)
            return sc

        def combo():
            return {"rlist": rng.choice(RLISTS), "spimm": rng.choice(SPIMMS)}

        def spair(distinct):
            while True:
                a, b = rng.choice(SREGS), rng.choice(SREGS)
                if a != b or not distinct:
                    return {"r1s": a, "r2s": b}

        for r, s in sorted(ALL_COMBOS):                         # TP-CMP-039/043/045: every (rlist, spimm)
            add("push", rlist=r, spimm=s)
            add("pop", rlist=r, spimm=s)
        add("push", "haz_alu_reg", **combo())                   # TP-CMP-069 patterns
        add("push", "haz_load_reg", **combo())
        add("pop", "haz_store_slot", **combo())
        for kind, aligns in (("popret", (0, 2)), ("popretz", (2, 0))):
            add(kind, rlist=4, spimm=rng.choice(SPIMMS), align=aligns[0])   # rlist 4 pinned (TP-CMP-049)
            add(kind, align=aligns[1], **combo())
            add(kind, align=weighted(rng, W6_RET_ALIGN), **combo())
        for a in SREGS:
            for b in SREGS:
                if a != b:                                        # r1s' == r2s' is reserved: B4, its own _xfail group
                    add("mvsa01", r1s=a, r2s=b)
                add("mva01s", r1s=a, r2s=b)                       # equal pairs included (TP-CMP-053)
        p = spair(True)
        add("mva01s", "haz_load_mv", aux={"load_reg": rng.choice((p["r1s"], p["r2s"]))}, **p)
        for kind in CM_KINDS:                                     # TP-CMP-055: minstret around one cm.* per kind
            kw = combo() if kind in FRAME_KINDS else spair(kind == "mvsa01")
            add(kind, "minstret", align=weighted(rng, W6_RET_ALIGN), **kw)
        add("b2b_push_pop", **combo())                            # TP-CMP-066 patterns
        c2 = combo()
        add("b2b_pop_push", aux={"rlist2": c2["rlist"], "spimm2": c2["spimm"]}, **combo())
        p, q = spair(True), spair(False)
        add("b2b_mvsa01_mva01s", aux={"r1s2": q["r1s"], "r2s2": q["r2s"]}, **p)
        p, q = spair(False), spair(True)
        add("b2b_mva01s_mvsa01", aux={"r1s2": q["r1s"], "r2s2": q["r2s"]}, **p)
        for k in CM_KINDS:                                        # TP-CMP-073: each cm.* kind once at a ret's fall-through
            kw = combo() if k in FRAME_KINDS else spair(k == "mvsa01")
            inner = Scenario(idx=-1, kind=k, variant="ft_inner", align=weighted(rng, W6_RET_ALIGN), **kw)
            add(rng.choice(RET_KINDS), "ft", align=weighted(rng, W6_RET_ALIGN), inner=inner, **combo())
        rng.shuffle(scs)
        for i, sc in enumerate(scs):
            sc.idx = i
        self.red_target = rng.choice([sc.idx for sc in scs if sc.kind == "push" and sc.variant == "plain"])
        return scs

    def prologue(self):
        self.cur = Scenario(idx=-1, kind="init", variant="init")
        self.ins("csrwi 0x320, 0")              # mcountinhibit = 0: counters run (TP-CMP-055 precondition, set explicitly)
        self.ins("la tp, gen_results")          # tp: result-buffer write pointer (no Zcmp instruction touches x4)
        self.ins("la t4, gen_scratch")          # t4: scratch word of the load producers (TP-CMP-069)
        for r in RLIST_ORDER + (10, 11):        # every tracked register starts at a known distinct value
            self.set_reg(r, self.value())

    def epilogue(self):
        k = len(self.reports)
        self.raw("  # report channel: K RAW words in plan order, one EOT-register store each, then tohost 1")
        self.ins("la tp, gen_results")
        self.ins("li t6, GEN_MM_EOT_ADDR")
        self.ins(f"li t5, {k}")
        self.raw("gen_report_loop:")
        for t in ("lw t0, 0(tp)", "sw t0, 0(t6)", "addi tp, tp, 4", "addi t5, t5, -1", "bnez t5, gen_report_loop"):
            self.raw("  " + t)
        self.retired += 5 * k
        self.ins("li gp, 1")
        self.ins("la t5, tohost")
        self.ins("sw gp, 0(t5)")
        self.raw("1:")
        self.raw("  j 1b")
        self.retired += 1                       # gen_boot_stub.S: j _start

    def build(self):
        self.prologue()
        for sc in self.draw_scenarios():
            self.scenarios.append(sc)
            if sc.variant == "ft":
                self.emit_ft(sc)
            elif sc.kind in B2B_KINDS:
                self.emit_b2b(sc)
            else:
                self.emit_simple(sc)
        assert self.pending == 0, "records left unflushed"
        self.epilogue()


def plan(seed, red=False):
    em = _Emitter(random.Random(f"{int(seed)}:{TAG}"), bool(red))
    em.build()
    return Plan(seed=int(seed), red=bool(red), scenarios=em.scenarios, reports=em.reports, k=len(em.reports),
                min_retired=em.retired, lines=em.lines, red_note=em.red_note)


def emit(p):
    head = [f"# gen_cmp_zcmp_basic program, seed {p.seed}{' RED FIXTURE' if p.red else ''}: {len(p.scenarios)} scenarios, "
            f"{p.k} report words, retirement floor {p.min_retired}.",
            "# Generated by dv/auto_dv/tests/gen_programs/gen_cmp_zcmp_basic_prog.py; do not edit.",
            f"# red deviation: {p.red_note}" if p.red else "# green program: no deviation from the plan",
            '.include "gen_zc_insn.h"', '.include "gen_mmio_map.h"', ".section .text", ".globl _start", "_start:"]
    data = [".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
            ".align 2", ".globl gen_scratch", "gen_scratch: .word 0",
            ".align 4", ".globl gen_results", f"gen_results: .fill {p.k}, 4, 0",
            ".align 4", ".globl gen_stack", f"gen_stack: .fill {STACK_BYTES}, 1, 0", ".globl gen_stack_top", "gen_stack_top:",
            ".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}"]
    return "\n".join(head + p.lines + data) + "\n"


# ---- expectation helpers for the test's fire-checks ------------------------------------------
def resolve(rep, syms):
    """Expected RAW word: data as planned, sp relative to the linked gen_stack, labels through the image's
    global symbols (name -> int address); None when a symbol is missing from the image."""
    if rep.kind == "sp":
        base = syms.get("gen_stack")
        return None if base is None else (base + rep.expect) & MASK
    if rep.kind == "sym":
        v = syms.get(rep.expect)
        return None if v is None else v & MASK
    return rep.expect


def audit(p, got, syms, pick):
    """Compare the collected report words of the scenarios pick() selects with the plan (minstret pairs
    excluded, see minstret_deltas). Returns (scenarios, words, mismatch strings)."""
    scs = [sc for sc in p.scenarios if pick(sc)]
    words, bad = 0, []
    for sc in scs:
        for i in sc.reports:
            rep = p.reports[i]
            if rep.kind.startswith("ctr"):
                continue
            words += 1
            exp = resolve(rep, syms)
            have = got[i] if i < len(got) else None
            if exp is None or have != exp:
                bad.append(f"report {i} ({describe(sc)} {rep.tag}): expected "
                           f"{'unresolved ' + str(rep.expect) if exp is None else f'0x{exp:08x}'} got "
                           f"{'none' if have is None else f'0x{have:08x}'}")
    return scs, words, bad


def sp_adjust(p, got, sc):
    """Observed |stack_adj| of a frame scenario from its sp_old/sp_new words (None when a word is missing)."""
    old = [i for i in sc.reports if p.reports[i].tag == "sp_old"]
    new = [i for i in sc.reports if p.reports[i].tag == "sp_new"]
    if not old or not new or max(old[0], new[0]) >= len(got):
        return None
    delta = (got[new[0]] - got[old[0]]) & MASK
    return (-delta) & MASK if sc.kind == "push" else delta


def minstret_deltas(p, got):
    """(scenario, minstret delta) of every minstret-wrapped cm.* (report pair ctr0/ctr1); None when missing."""
    out = []
    for sc in p.scenarios:
        if sc.variant != "minstret":
            continue
        pair = [i for i in sc.reports if p.reports[i].kind in ("ctr0", "ctr1")]
        ok = len(pair) == 2 and pair[1] < len(got)
        out.append((sc, (got[pair[1]] - got[pair[0]]) & MASK if ok else None))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="per-seed program generator of gen_test_cmp_zcmp_basic")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--red", action="store_true", help="TDD red fixture: one cm.push deviates from the plan")
    a = ap.parse_args(argv)
    p = plan(a.seed, a.red)
    text = emit(p)
    assert text.isascii(), "generated program is not ASCII"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text)
    print(f"gen_cmp_zcmp_basic_prog: seed {p.seed} red {p.red} scenarios {len(p.scenarios)} reports {p.k} "
          f"min_retired {p.min_retired} -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
