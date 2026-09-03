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
intent.

Scenario list per seed: the 48 (rlist, spimm) cm.push combinations PUSH_REPEATS times (TP-CMP-039
Stimulus: each combination >= 3 times) and the 48 cm.pop combinations once, the hazard producers, the
ret kinds at both target alignments (rlist RET_PINNED_RLIST pinned, one multi-register draw so every
seed restores registers through a popret and a popretz), all sreg' pairs of both moves, one
minstret-wrapped cm.* per kind, the four back-to-back patterns and one fall-through cm.* per kind,
shuffled. The back-to-back push;pop pops a LONGER list at the same stack_adj (longer_same_adj), so the
pop loads a register the push never stored and a pop that loads nothing is visible in the register
records; a same-rlist pop would restore every register to its own value.

emit(plan) renders RV32IMC assembly for the lowRISC gcc 10.2 toolchain: the Zcmp halfwords come from
gen_zc_insn.h (the assembler knows no Zc), the program keeps its observations in a result buffer
(tp = write pointer, never touched by Zcmp) and stores them as RAW words to GEN_MM_EOT_ADDR in plan
order at the end, then tohost TOHOST_PASS. Report words: sp before and after every frame instruction,
the whole frame read back after a cm.push (list slots and the poison the program wrote to the other
slots), all 13 rlist-capable registers after a pop, the marker the return target stores (a decoy block
is reached only through the stale ra), a0 after cm.popretz, the eight sreg' after cm.mvsa01, a0/a1
after cm.mva01s, minstret before and after one cm.* of each kind. CSR addresses, the tohost code and
the configuration name come from gen_prog_const.

Red fixtures (TDD): red=True deviates the PROGRAM on one intent while the plan keeps the true
expectation, so the named fire-check must fail. RED_ITEMS maps every built item to its deviation and
names the related checks that read the same words and trip with it; red_item selects the item, and
without one random.Random(f"{seed}:red") draws it. The red draws (item, target scenario, slot) come
from that separate stream, so the green plan and every red program share the main program stream.
After the deviated scenario the red program re-loads every tracked register with the model's value
(resync), so the deviation is visible in that scenario's records alone.

CLI: python3 gen_cmp_zcmp_basic_prog.py --seed N --out <file.S> [--red [--red-item TP-CMP-nnn]]
"""
import argparse
import random
from dataclasses import dataclass, field
from pathlib import Path

from dv.auto_dv.tests.gen_programs.gen_prog_const import CONFIG_NAME, TOHOST_PASS, csr_hex
from dv.auto_dv.tests.gen_test_lib import Weighted

MASK = 0xFFFFFFFF
TAG = "program:gen_cmp_zcmp_basic"
RED_TAG = "red"

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

# Plan pins (gen_test_plan.md AREA CMP): TP-CMP-039 Stimulus "each combination >= 3 times"; TP-CMP-046 Stimulus
# "cm.pop {ra, s0-s3}, 48 (rlist 8, spimm 1) and cm.pop {ra, s0-s11}, 112 (rlist 15, spimm 3) pinned";
# TP-CMP-049 Stimulus / TP-CMP-047 "rlist 4" for the ret kinds.
PUSH_REPEATS = 3
POP_PINNED_COMBOS = ((8, 1), (15, 3))
RET_PINNED_RLIST = 4

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
    """Layer-1 weighted class draw from the program stream."""
    return Weighted(table).draw(rng)


def rlist_regs(rlist):
    """Registers of an rlist in list order (ra first); rlist 15 adds s10 and s11 together."""
    return RLIST_ORDER[:13 if rlist == 15 else rlist - 3]


def stack_adj_base(rlist):
    return 16 if rlist <= 7 else 32 if rlist <= 11 else 48 if rlist <= 14 else 64


def stack_adj(rlist, spimm):
    return stack_adj_base(rlist) + 16 * spimm


STACK_ADJ_VALUES = frozenset(stack_adj(r, s) for r, s in ALL_COMBOS)   # 16, 32, ..., 112


def same_group_rlist(rlist):
    """The neighbouring rlist with the same stack_adj_base (None for 15, alone in the base-64 group)."""
    if rlist == 15:
        return None
    return rlist + 1 if stack_adj_base(rlist + 1) == stack_adj_base(rlist) else rlist - 1


def longer_same_adj(rlist, spimm):
    """(rlist, spimm) pairs with the same stack_adj and a longer register list: a pop of one of them after a
    push of (rlist, spimm) loads a register the push never stored, so a pop that loads nothing is visible."""
    adj = stack_adj(rlist, spimm)
    return [(r, s) for r, s in sorted(ALL_COMBOS) if r > rlist and stack_adj(r, s) == adj]


B2B_PUSH_COMBOS = tuple(c for c in sorted(ALL_COMBOS) if longer_same_adj(*c))   # 41 of 48 have a longer partner

# Red fixtures: item -> (scenario filter, one-line deviation note naming the related checks that also trip).
RED_ITEMS = {
    "TP-CMP-039": (lambda sc: sc.kind == "push" and sc.variant == "plain",
                   "a plain cm.push emitted with the other spimm bit: sp_new off by 16 (also trips TP-CMP-043 and the "
                   "rlist's item 040/041/042)"),
    "TP-CMP-040": (lambda sc: sc.kind == "push" and sc.variant == "plain" and sc.rlist == 4,
                   "the rlist 4 cm.push emitted as rlist 5: x8 lands in the poison slot sp-8 (also trips TP-CMP-039)"),
    "TP-CMP-041": (lambda sc: sc.kind == "push" and sc.variant == "plain" and sc.rlist == 15 and sc.spimm < 3,
                   "a rlist 15 cm.push emitted as rlist 14 with spimm+1: same stack_adj, frame shifted by one register "
                   "(also trips TP-CMP-039)"),
    "TP-CMP-042": (lambda sc: sc.kind == "push" and sc.variant == "plain" and 5 <= sc.rlist <= 14,
                   "a rlist 5..14 cm.push emitted with the neighbouring rlist of its stack_adj group: frame shifted "
                   "(also trips TP-CMP-039)"),
    "TP-CMP-043": (lambda sc: sc.kind == "pop" and sc.variant == "plain" and (sc.rlist, sc.spimm) not in POP_PINNED_COMBOS,
                   "a plain cm.pop emitted with the other spimm bit: sp delta off by 16 (also trips TP-CMP-045)"),
    "TP-CMP-045": (lambda sc: sc.kind == "pop" and sc.variant == "plain" and (sc.rlist, sc.spimm) not in POP_PINNED_COMBOS
                   and sc.rlist != 15,
                   "a plain cm.pop emitted with the neighbouring rlist of its stack_adj group: registers loaded from "
                   "shifted slots"),
    "TP-CMP-046": (lambda sc: sc.kind == "pop" and sc.variant == "plain" and (sc.rlist, sc.spimm) in POP_PINNED_COMBOS
                   and same_group_rlist(sc.rlist) is not None,
                   "the pinned (8, 1) cm.pop emitted as (9, 1): s4 loaded, the list shifted (also trips TP-CMP-045)"),
    "TP-CMP-047": (lambda sc: sc.kind == "popret" and sc.variant == "plain" and sc.rlist > 4,
                   "one non-ra frame slot of a multi-register cm.popret overwritten after the fill: that register "
                   "restores the wrong word"),
    "TP-CMP-048": (lambda sc: sc.kind == "popretz" and sc.variant == "plain",
                   "a cm.popretz emitted as cm.popret: a0 keeps its nonzero value"),
    "TP-CMP-049": (lambda sc: sc.kind == "popret" and sc.variant == "plain",
                   "a cm.popret emitted as cm.pop then jr through the stale x1: control reaches the decoy block "
                   "(also trips TP-CMP-047)"),
    "TP-CMP-050": (lambda sc: sc.kind == "mvsa01" and sc.variant == "plain",
                   "a cm.mvsa01 emitted with r1s' and r2s' swapped"),
    "TP-CMP-052": (lambda sc: sc.kind == "mva01s" and sc.variant == "plain" and sc.r1s != sc.r2s,
                   "a cm.mva01s emitted with r1s' and r2s' swapped"),
    "TP-CMP-053": (lambda sc: sc.kind == "mva01s" and sc.variant == "plain" and sc.r1s == sc.r2s,
                   "an equal-pair cm.mva01s emitted with another r2s': a1 != a0"),
    "TP-CMP-055": (lambda sc: sc.variant == "minstret" and sc.kind in MOVE_KINDS,
                   "the minstret-wrapped cm.mvsa01 or cm.mva01s emitted twice: same registers, minstret delta 3"),
    "TP-CMP-066": (lambda sc: sc.kind == "b2b_push_pop",
                   "the back-to-back pop emitted with the push's own (rlist, spimm): the longer list's extra register is "
                   "never loaded"),
    "TP-CMP-069": (lambda sc: sc.variant == "haz_load_mv",
                   "the load producer emitted after the cm.mva01s: the move reads the old register value (also trips "
                   "TP-CMP-052)"),
    "TP-CMP-073": (lambda sc: sc.variant == "ft",
                   "the later jump lands 2 bytes past the fall-through cm.*: its effect never happens (also trips the "
                   "outer ret kind's item 047/048, whose audit reads the same scenario's words)"),
}


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
    red_item: str
    red_note: str


def describe(sc):
    if sc.kind in FRAME_KINDS or sc.kind in ("b2b_push_pop", "b2b_pop_push"):
        return f"{sc.kind}#{sc.idx} rlist={sc.rlist} spimm={sc.spimm} {sc.variant}"
    return f"{sc.kind}#{sc.idx} r1s={sc.r1s} r2s={sc.r2s} {sc.variant}"


# ---- emitter: assembly text and the intent model advance together in execution order ---------
class _Emitter:
    def __init__(self, rng, red, red_item, red_rng):
        self.rng = rng
        self.red = red
        self.red_item = red_item if red else None
        self.red_rng = red_rng
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
        self.deferred = []        # producer lines the TP-CMP-069 red emits after the consumer

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
    def cm_text(self, sc, kind=None, rlist=None, spimm=None, r1s=None, r2s=None):
        """Assembly of the scenario's cm.*; an explicit operand replaces the planned one (red fixtures)."""
        kind = kind or sc.kind
        if kind in FRAME_KINDS:
            return f"cm_{kind} {sc.rlist if rlist is None else rlist}, {sc.spimm if spimm is None else spimm}"
        return f"cm_{kind} {sc.r1s if r1s is None else r1s}, {sc.r2s if r2s is None else r2s}"

    def dev(self, sc):
        """The red item this scenario carries the deviation of (None on the green path)."""
        return self.red_item if self.red and sc.idx == self.red_target else None

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
            if self.dev(sc) == "TP-CMP-047":
                off, r = self.red_rng.choice([(o, r) for o, r in pop_slots(sc.rlist, sc.spimm) if r != 1])
                self.ins(f"li t3, 0x{~self.mem[self.base + off] & MASK:08x}")   # the model keeps the fill word
                self.ins(f"sw t3, {off}(t0)")
                self.red_note = f"scenario {sc.idx} {describe(sc)}: frame slot sp_old{off:+d} (x{r}) overwritten after the fill"
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
            producer = [f"li t3, 0x{w:08x}", "sw t3, 0(t4)", f"lw x{r}, 0(t4)"]
            if self.dev(sc) == "TP-CMP-069":
                self.deferred = producer                                 # emitted after the consumer instead
                self.red_note = f"scenario {sc.idx} {describe(sc)}: lw x{r} producer emitted after the cm.mva01s"
            else:
                for t in producer:
                    self.ins(t)
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
            self.ins(f"csrr t5, {csr_hex('minstret')}")
        self.cm_emit(sc)
        self.cm_model(kind, sc)
        for t in self.deferred:
            self.ins(t)
        self.deferred = []
        if kind in RET_KINDS:
            self.ret_tail(sc)
        if sc.variant == "minstret":
            self.ins(f"csrr t6, {csr_hex('minstret')}")
        (self.post_frame if frame else self.post_move)(sc, kind)
        if sc.variant == "minstret":
            self._rec(30, "ctr0", 0, "minstret_before")
            self._rec(31, "ctr1", 2, "minstret_after")
        self.flush()

    def cm_emit(self, sc):
        """The scenario's cm.* on the executed path; the red target of an item emits that item's deviation."""
        d = self.dev(sc)
        text = self.cm_text(sc)
        note = ""
        if d in ("TP-CMP-039", "TP-CMP-043"):
            text, note = self.cm_text(sc, spimm=sc.spimm ^ 1), f"emitted spimm {sc.spimm ^ 1} (sp off by 16)"
        elif d == "TP-CMP-040":
            text, note = self.cm_text(sc, rlist=5), "emitted rlist 5 (x8 stored into the poison slot sp-8)"
        elif d == "TP-CMP-041":
            text, note = self.cm_text(sc, rlist=14, spimm=sc.spimm + 1), f"emitted rlist 14 spimm {sc.spimm + 1} (same stack_adj)"
        elif d in ("TP-CMP-042", "TP-CMP-045", "TP-CMP-046"):
            r = same_group_rlist(sc.rlist)
            text, note = self.cm_text(sc, rlist=r), f"emitted rlist {r} (same stack_adj)"
        elif d == "TP-CMP-048":
            text, note = self.cm_text(sc, kind="popret"), "emitted cm.popret (a0 not zeroed)"
        elif d == "TP-CMP-049":
            self.ins("mv t3, x1")                                        # the stale ra, as a wrong ret would use it
            text, note = self.cm_text(sc, kind="pop"), "emitted cm.pop then jr through the stale x1 (decoy reached)"
        elif d in ("TP-CMP-050", "TP-CMP-052"):
            text, note = self.cm_text(sc, r1s=sc.r2s, r2s=sc.r1s), "emitted with r1s' and r2s' swapped"
        elif d == "TP-CMP-053":
            r2 = self.red_rng.choice([r for r in SREGS if r != sc.r1s])
            text, note = self.cm_text(sc, r2s=r2), f"emitted r2s' x{r2} (a1 != a0)"
        self.ins(text)
        if d == "TP-CMP-049":
            self.ins("jr t3")
        elif d == "TP-CMP-055":
            self.ins(text)
            note = "emitted twice inside the minstret window (delta 3)"
        if note:
            self.red_note = f"scenario {sc.idx} {describe(sc)}: {note}"

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
        if self.dev(sc) == "TP-CMP-073":
            self.ins(f"j {ft} + 2")                       # lands past the fall-through halfword: its effect never happens
            self.retired -= 1                             # the skipped cm.* was counted when its text was placed
            self.red_note = f"scenario {sc.idx} {describe(sc)}: the later jump skips the fall-through cm.{inner.kind}"
        else:
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
            r2, s2 = sc.aux["rlist2"], sc.aux["spimm2"]      # longer list, same stack_adj: the pop's loads are visible
            if self.dev(sc) == "TP-CMP-066":
                self.ins(self.cm_text(sc, "pop"))
                self.red_note = f"scenario {sc.idx} {describe(sc)}: pop emitted with the push's own rlist instead of {r2}"
            else:
                self.ins(f"cm_pop {r2}, {s2}")
            self.model_pop(r2, s2)
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

        def combo(min_rlist=RLISTS[0]):
            return {"rlist": rng.choice([r for r in RLISTS if r >= min_rlist]), "spimm": rng.choice(SPIMMS)}

        def spair(distinct):
            while True:
                a, b = rng.choice(SREGS), rng.choice(SREGS)
                if a != b or not distinct:
                    return {"r1s": a, "r2s": b}

        for _ in range(PUSH_REPEATS):                           # TP-CMP-039: every (rlist, spimm) >= 3 times
            for r, s in sorted(ALL_COMBOS):
                add("push", rlist=r, spimm=s)
        for r, s in sorted(ALL_COMBOS):                         # TP-CMP-043/045/046: every (rlist, spimm) once
            add("pop", rlist=r, spimm=s)
        add("push", "haz_alu_reg", **combo())                   # TP-CMP-069 patterns
        add("push", "haz_load_reg", **combo())
        add("pop", "haz_store_slot", **combo())
        for kind, aligns in (("popret", (0, 2)), ("popretz", (2, 0))):
            add(kind, rlist=RET_PINNED_RLIST, spimm=rng.choice(SPIMMS), align=aligns[0])   # TP-CMP-049 pin
            add(kind, align=aligns[1], **combo(min_rlist=5))    # one multi-register ret per kind and seed
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
        r1, s1 = rng.choice(B2B_PUSH_COMBOS)                      # TP-CMP-066 patterns
        r2, s2 = rng.choice(longer_same_adj(r1, s1))
        add("b2b_push_pop", rlist=r1, spimm=s1, aux={"rlist2": r2, "spimm2": s2})
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
        self.pick_red(scs)
        return scs

    def pick_red(self, scs):
        """Red fixture: the item (drawn when not given) and its target scenario, from the red stream only."""
        if not self.red:
            return
        if self.red_item is None:
            self.red_item = self.red_rng.choice(sorted(RED_ITEMS))
        pick = RED_ITEMS[self.red_item][0]
        cands = [sc.idx for sc in scs if pick(sc)]
        assert cands, f"no scenario carries the red fixture of {self.red_item}"
        self.red_target = self.red_rng.choice(cands)

    def prologue(self):
        self.cur = Scenario(idx=-1, kind="init", variant="init")
        self.ins(f"csrwi {csr_hex('mcountinhibit')}, 0")   # counters run (TP-CMP-055 precondition, set explicitly)
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
        self.ins(f"li gp, {TOHOST_PASS}")
        self.ins("la t5, tohost")
        self.ins("sw gp, 0(t5)")
        self.raw("1:")
        self.raw("  j 1b")
        self.retired += 1                       # gen_boot_stub.S: j _start

    def resync(self):
        """Red fixture: re-load every tracked register with the model's value after the deviated scenario, so the
        deviation shows in that scenario's records alone (later records of untouched registers stay green)."""
        for r in RLIST_ORDER + (10, 11):
            v = self.regs[r]
            self.ins(f"la x{r}, {v}" if isinstance(v, str) else f"li x{r}, 0x{v:08x}")

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
            if self.dev(sc):
                self.resync()
        assert self.pending == 0, "records left unflushed"
        self.epilogue()


def plan(seed, red=False, red_item=None):
    assert red_item is None or red_item in RED_ITEMS, f"unknown red item {red_item}"
    em = _Emitter(random.Random(f"{int(seed)}:{TAG}"), bool(red), red_item, random.Random(f"{int(seed)}:{RED_TAG}"))
    em.build()
    assert not red or em.red_note, "red fixture selected but no deviation was emitted"
    return Plan(seed=int(seed), red=bool(red), scenarios=em.scenarios, reports=em.reports, k=len(em.reports),
                min_retired=em.retired, lines=em.lines, red_item=em.red_item or "", red_note=em.red_note)


def emit(p):
    head = [f"# gen_cmp_zcmp_basic program, seed {p.seed}, configuration {CONFIG_NAME}{' RED FIXTURE' if p.red else ''}: "
            f"{len(p.scenarios)} scenarios, {p.k} report words, retirement floor {p.min_retired}.",
            "# Generated by dv/auto_dv/tests/gen_programs/gen_cmp_zcmp_basic_prog.py; do not edit.",
            f"# red fixture {p.red_item}: {RED_ITEMS[p.red_item][1]}; {p.red_note}" if p.red
            else "# green program: no deviation from the plan",
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


def audit(p, got, syms, pick, tags=None):
    """Compare the collected report words of the scenarios pick() selects with the plan (minstret pairs
    excluded, see minstret_deltas; `tags` restricts the words to those report tags). Returns (scenarios,
    words, mismatch strings)."""
    scs = [sc for sc in p.scenarios if pick(sc)]
    words, bad = 0, []
    for sc in scs:
        for i in sc.reports:
            rep = p.reports[i]
            if rep.kind.startswith("ctr") or (tags is not None and rep.tag not in tags):
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
    ap.add_argument("--red", action="store_true", help="TDD red fixture: the program deviates on one item's intent")
    ap.add_argument("--red-item", choices=sorted(RED_ITEMS), default=None,
                    help="the item whose fire-check the red fixture trips (default: drawn from the seed)")
    a = ap.parse_args(argv)
    if a.red_item and not a.red:
        ap.error("--red-item needs --red")
    p = plan(a.seed, a.red, a.red_item)
    text = emit(p)
    assert text.isascii(), "generated program is not ASCII"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text)
    print(f"gen_cmp_zcmp_basic_prog: seed {p.seed} red {p.red} scenarios {len(p.scenarios)} reports {p.k} "
          f"min_retired {p.min_retired} -> {a.out}" + (f" red_item {p.red_item}: {p.red_note}" if p.red else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
