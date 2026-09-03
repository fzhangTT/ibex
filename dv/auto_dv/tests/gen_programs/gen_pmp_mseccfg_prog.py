#!/usr/bin/env python3
"""gen_pmp_mseccfg_prog: per-seed program generator of gen_test_pmp_mseccfg (plan group gen_pmp_mseccfg,
items TP-PMP-011, 012, 022..031 and 108 of dv/auto_dv/docs/gen_test_plan.md, AREA PMP).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:pmp_mseccfg"), runs
gen_pmp_csr_warl_prog.PmpModel (the mseccfg and pmpcfg WARL rules as the specification states them) and returns a
Plan: the assembly lines, the ordered expected report words (every csrr read-back, the handler's trap records, the
probe results), k, min_retired, the mseccfg walk (one entry per mseccfg write: pre state, written value, post
state) and per-item metadata for the fire-checks. Layout-relative expectations resolve from the image's symbol
table through bases_from_symbols(<prog.sym.json>["symbols"]) (pool, U code area, end of .text, .data base).

The program is one power-on walk through the {MML, MMWP, RLB} state machine (no reset exists on the bridge):
  s00x  TP-PMP-011 (hi bits read zero), 012 (mseccfgh), 024 (RLB free while no lock), 108 toggles
  path mmwp_first: 023 sets MMWP from s00x, then s01x toggles (108, 023 clear attempts, 011)
  lock step (RLB = 1, 026 "set RLB"): the M-mode table that survives MML = 1 and MMWP = 1 is written under RLB = 1
        (entry 0 TOR [0, U code area) L=1 R/X, entry 2 NA4 L=1 RW over pool word A, entry 4 NAPOT L=1 RW over the
        MMIO page, entry 5 NAPOT L=1 RW over .data) plus mixed rows (031); entry 1 (U code NAPOT L=0 RWX), entry 3
        (NA4 L=0 RWX over pool word B) and the catch-all entry 15 (NAPOT L=0 RWX over everything, M-mode cover
        while MMWP = 1 under MML = 0) are written before any lock
  031 before: csrr of every pmpcfg/pmpaddr, M-mode load of pool word B (allowed), U-mode load of pool word A (allowed)
  022 sets MML with RLB = 1 (from s001 or s011 only: an M-mode program needs the locked code rule before MML = 1, so
        the pre state has RLB = 1 or RLB is dead); 031 after: identical csrr set, both loads now denied (mcause 5)
  s1x1  030 (exec rows stored under RLB = 1); path mml_first_*: 023 sets MMWP here (or after the clear)
  026 clears RLB (locks exist: permanent); s1x0: 022/023 clear attempts, 030 suppressed repeat, 027 (per-entry
        suppression, all four words, csrrw and csrrs), 028 (A = OFF), 029 (non-exec locked rows stored), 025 and 026
        and 108 RLB set attempts (blocked), tohost 1
The state set one seed visits is the path's: mmwp_first {s000 s001 s010 s011 s111 s110}, mml_first_rlb
{s000 s001 s101 s111 s110}, mml_first_late {s000 s001 s101 s100 s110};
TP-PMP-108's per-seed visit floor is the path's set, never 8 (the plan's wrapper reset does not exist).

Red fixtures (red=True): the PROGRAM deviates on one intent of one item while the plan keeps the green
expectations, so exactly that item's fire-check fails. Item and site come from random.Random(f"{seed}:red")
unless red_item names the item. 011/024/108: one lock-free mseccfg write carries the RLB bit flipped, the planned
state is restored after the reported read-back. 012: one mseccfgh write lands on mseccfg (flipping RLB), restored.
022/023: the MML (MMWP) set write is emitted after the first clear attempt instead of before it (the attempt's
read-back then shows the bit still 0). 025: the program reports the written operand in place of the read-back
(the observation a leaky RLB would produce; an ignored write on a locked sticky field has no behavioural
deviation). 026: the RLB clear is skipped at its site and performed after the read-back. 027/028: one offending
byte is written with L = 0 (stored instead of suppressed), the planned word is written back. 029: the row is
written as an exec row (suppressed instead of stored), the planned row is written back. 030: one accepted row
write is skipped, then written back. 031: the after-MML M-mode probe targets pool word A (allowed) instead of
pool word B, or one free pmpaddr is changed between the two csrr passes and restored.

CLI: python3 gen_pmp_mseccfg_prog.py --seed N --out <file.S> [--red [--red-item TP-PMP-0nn]] [--summary]
"""
import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP  # noqa: E402
from dv.auto_dv.tests.gen_programs import gen_pmp_csr_warl_prog as warl  # noqa: E402
from dv.auto_dv.tests.gen_programs.gen_pmp_csr_warl_prog import (  # noqa: E402
    A_NA4, A_NAPOT, A_OFF, A_TOR, CAUSE_ECALL_U, CAUSE_LOAD, CSR_MSECCFG, CSR_MSECCFGH, MPP_MASK, MSECCFG_MML,
    MSECCFG_MMWP, MSECCFG_RLB, NUM_CFG_CSRS, NUM_REGIONS, PmpModel, UCODE_ALIGN_BITS, UCODE_NAPOT_ONES, UIMM_FORMS,
    byte_fields, cfg_byte, pmpaddr, pmpcfg, record, wchoice)
from dv.auto_dv.tests.gen_programs.gen_prog_const import TOHOST_FAIL  # noqa: E402

RNG_TAG = "program:pmp_mseccfg"
RED_RNG_TAG = "red"
RED_SITE_TAG = "red:site"                 # red-only choices draw here so the green and red plans share every draw
ITEMS = ("TP-PMP-011", "TP-PMP-012", "TP-PMP-022", "TP-PMP-023", "TP-PMP-024", "TP-PMP-025", "TP-PMP-026",
         "TP-PMP-027", "TP-PMP-028", "TP-PMP-029", "TP-PMP-030", "TP-PMP-031", "TP-PMP-108")
RED_ITEMS = tuple(i for i in ITEMS if i != "TP-PMP-108")   # the seed-drawn red targets a built item; an explicit --red-item TP-PMP-108 is caught by fire_program_verdict
REG_FORMS = ("csrrw", "csrrs", "csrrc")
ALL_FORMS = REG_FORMS + UIMM_FORMS
MSEC_MASK = MSECCFG_MML | MSECCFG_MMWP | MSECCFG_RLB
HI_MASK = ~MSEC_MASK & 0xFFFFFFFF          # mseccfg bits 31:3 (read zero)
MPP_M = 3                                 # privilege level encoding of M-mode (mstatus.MPP)
CAUSE_LOAD_M_RECORD = record(CAUSE_LOAD, 0, MPP_M)   # handler record of a denied M-mode probe load
NOTRAP_MARK = 0x4E0007A9                  # register marker left in place when the M-mode probe took no trap
LOAD_SENT = 0x5E170A00                    # sentinel the probe register keeps when the load is denied
MMIO_NAPOT_ONES = (MEMORY_MAP["mmio_size"].bit_length() - 1) - 3
DATA_ALIGN_BITS = 10                      # .data lives in one 1 KiB NAPOT (asserted against the emitted size)
PH_DATA = warl.PH_POOL - 0x400            # .data placeholder base until the symbol table resolves it (distinct from the warl placeholders)
DATA_NAPOT_ONES = DATA_ALIGN_BITS - 3
assert MEMORY_MAP["mmio_size"] == 1 << (MMIO_NAPOT_ONES + 3) and MEMORY_MAP["mmio_base"] % MEMORY_MAP["mmio_size"] == 0

# entry roles: the table an M-mode program needs to survive MML = 1 and MMWP = 1 (lowest-numbered match decides)
E_CODE, E_UCODE, E_POOL_A, E_POOL_B, E_MMIO, E_DATA = 0, 1, 2, 3, 4, 5
E_CATCHALL = NUM_REGIONS - 1
E_MIXED = (8, 9, 12, 13)                  # TP-PMP-031 mixed rows (at most one L=1 among them)
E_030 = 10                                # TP-PMP-030 rows (rewritten under RLB=1; ends locked)
E_FREE_FIRST = 6                          # entries 6..14 hold item rows; never anything the program touches
BASE_SYMBOLS = dict(warl.BASE_SYMBOLS, data="gen_data_base")

# Layer-1 distributions transcribed from the items' Stimulus fields
W_PATH = {"mmwp_first": 60, "mml_first_rlb": 25, "mml_first_late": 15}
W_HI = {"nonzero": 80, "zero": 20}                                   # TP-PMP-011 bits 31:3
W_FORM_011 = {"csrrw": 60, "csrrs": 20, "csrrc": 20}
W_SET_FORM = {"csrrw": 50, "csrrs": 50}                              # TP-PMP-022/023 set op
W_A_ANY = {A_OFF: 25, A_TOR: 25, A_NA4: 25, A_NAPOT: 25}
EXEC_ROWS = ((0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 1))            # RWX of the M-exec locked rows (LRWX 1001 1010 1011 1101)
NONEXEC_ROWS = ((0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1))         # LRWX 1000 1100 1110 1111
SUPPRESS_MODES = (A_TOR, A_NA4, A_NAPOT)


def sname(st):
    return "s%d%d%d" % st


@dataclass
class Plan:
    seed: int
    red: bool
    path: str
    reports: list = field(default_factory=list)
    items: dict = field(default_factory=dict)
    lines: list = field(default_factory=list)
    min_retired: int = 0
    red_item: str = ""
    red_note: str = ""
    red_sites: dict = field(default_factory=dict)
    walk: list = field(default_factory=list)      # dicts: idx item form pre wdata post locked (every mseccfg write)
    states: list = field(default_factory=list)    # every state the walk touches, in first-visit order

    @property
    def k(self):
        return len(self.reports)

    def expected(self, idx, bases):
        """Expected value of report idx (kinds as gen_pmp_csr_warl_prog.Plan: abs, rel, base)."""
        r = self.reports[idx]
        if r.kind == "abs":
            return r.value
        if r.kind == "base":
            return bases[r.value]
        base_name, off, mask = r.value
        return (((bases[base_name] + off) >> 2) | mask) & 0xFFFFFFFF

    def item_indices(self, item):
        return [r.idx for r in self.reports if r.item == item]

    def signature(self):
        return [(r.item, r.kind, r.value) for r in self.reports]


def bases_from_symbols(symbols):
    missing = [s for s in BASE_SYMBOLS.values() if s not in symbols]
    assert not missing, f"gen_pmp_mseccfg_prog: the image defines no symbol {missing}"
    return {k: int(symbols[s], 16) for k, s in BASE_SYMBOLS.items()}


class Gen(warl.Gen):
    """The csr_warl generator's emission, model and report mechanics with this group's phases, handler and reds."""

    def __init__(self, seed, red_target=None):
        self.rng = random.Random(f"{int(seed)}:{RNG_TAG}")
        self.red_rng = random.Random(f"{int(seed)}:{RED_SITE_TAG}")
        self.m = PmpModel()
        self.plan = Plan(seed=seed, red=red_target is not None, path=wchoice(self.rng, W_PATH))
        self.plan.items = {tp: {} for tp in ITEMS}
        self.plan.items["bases"] = {}
        self.main, self.aux, self.pool = [], [], []
        self.u_attempts = []
        self.res_n = 0
        self.in_main = True
        self.probe_count = 0
        self.addr_rel = [None] * NUM_REGIONS
        self.red_target = red_target
        self.red_sites = {tp: [] for tp in ITEMS}
        self.site_serial = 0
        self.mprobe_n = 0

    # --- state helpers --------------------------------------------------------------------------------
    def state(self):
        return (self.m.mml, self.m.mmwp, self.m.rlb)

    def any_l(self):
        return any((c >> 7) & 1 for c in self.m.cfg)

    def locked_entries(self):
        return [e for e in range(NUM_REGIONS) if self.m.locked(e)]

    def unlocked_free(self, word=None):
        """Item-row entries (6..14) that are writable now, optionally of one pmpcfg word."""
        return [e for e in range(E_FREE_FIRST, NUM_REGIONS - 1) if not self.m.locked(e) and (word is None or e // 4 == word)]

    def msec_name(self):
        return warl.csr_name(CSR_MSECCFG)

    def hi_bits(self, cls=None):
        cls = cls or wchoice(self.rng, W_HI)
        return (self.rng.getrandbits(32) & HI_MASK) or (1 << self.rng.randint(3, 31)) if cls == "nonzero" else 0

    # --- red mechanics ----------------------------------------------------------------------------------
    def red_here(self, item):
        """Record a deviation-eligible site of item; True when it is the red target."""
        serial, self.site_serial = self.site_serial, self.site_serial + 1
        self.red_sites[item].append(serial)
        if self.red_target == (item, serial):
            self.plan.red_item = item
            return True
        return False

    def msec_flip_dev(self, form, operand):
        """The operand with RLB flipped when that changes the modelled read-back and RLB is restorable (no L bit)."""
        if form not in REG_FORMS or self.any_l():
            return None
        dev = operand ^ MSECCFG_RLB
        planned, clone = self.m.copy(), self.m.copy()
        planned.op(form, CSR_MSECCFG, operand)
        clone.op(form, CSR_MSECCFG, dev)
        if clone.read(CSR_MSECCFG) == planned.read(CSR_MSECCFG) or (clone.mml, clone.mmwp) != (planned.mml, planned.mmwp):
            return None
        return dev

    def restore_msec(self):
        self.li("t0", self.m.read(CSR_MSECCFG))
        self.emit(f"  csrw {self.msec_name()}, t0")

    # --- mseccfg write with walk bookkeeping -----------------------------------------------------------------
    def msec(self, form, operand, item, label, report_old=False, red=True):
        """One mseccfg op with read-back report and walk entry; red: the RLB-flip deviation site of item."""
        pre, locked = self.state(), bool(self.locked_entries())
        wdata = self.m.combined(form, CSR_MSECCFG, operand)
        dev = self.msec_flip_dev(form, operand) if red else None
        if dev is not None and self.red_here(item):
            self.li("t0", dev)
            self.emit(f"  {form} t1, {self.msec_name()}, t0")
            self.m.op(form, CSR_MSECCFG, operand)
            self.emit(f"  csrr t1, {self.msec_name()}")
            idx = self.report_reg("t1", item, f"{label} readback mseccfg", "abs", self.m.read(CSR_MSECCFG))
            self.plan.red_note = f"{item} {label}: program {form} mseccfg with 0x{dev:08x} for planned 0x{operand:08x}, read-back idx {idx}"
            self.restore_msec()
        else:
            _o, idx = self.csr_op(form, CSR_MSECCFG, operand, item, label, report_old=report_old)
        post = self.state()
        self.plan.walk.append({"idx": idx, "item": item, "form": form, "pre": pre, "wdata": wdata, "post": post, "locked": locked})
        for st in (pre, post):
            if st not in self.plan.states:
                self.plan.states.append(st)
        self.plan.items[item].setdefault("msec", []).append(idx)
        return idx

    def msec_value(self, rlb, hi=None):
        """A csrrw operand keeping the sticky bits at their current value with the RLB bit and hi bits given."""
        hi = self.hi_bits() if hi is None else hi
        return hi | (self.m.mml * MSECCFG_MML) | (self.m.mmwp * MSECCFG_MMWP) | (rlb * MSECCFG_RLB)

    def rlb_op(self, target, item, label, red=True):
        """One write whose RLB bit is target (0/1), form drawn; sticky bits kept, hi bits random."""
        cur = self.m.rlb
        form = self.rng.choice(REG_FORMS)
        if form == "csrrw":
            operand = self.msec_value(target)
        elif form == "csrrs":
            operand = self.hi_bits() | (MSECCFG_RLB if target else 0)
            if not target and cur:
                form, operand = "csrrc", self.hi_bits() | MSECCFG_RLB
        else:
            operand = self.hi_bits() | (0 if target else MSECCFG_RLB)
            if target and not cur:
                form, operand = "csrrs", self.hi_bits() | MSECCFG_RLB
        return self.msec(form, operand, item, label, red=red), form

    # --- P0 --------------------------------------------------------------------------------------------------
    def p0(self):
        self.p0_setup()
        self.emit("  la   t4, gen_data_base")
        self.plan.items["bases"]["data"] = self.report_reg("t4", "bases", ".data base", "base", "data")
        self.li("s10", 0)
        self.li("s11", NOTRAP_MARK)

    def set_rel_addr(self, e, base_sym, off, mask, item, label):
        """pmpaddr(e) = (<symbol> + off) >> 2 | mask from the symbol at run time; reported relative."""
        self.emit(f"  la   t0, {BASE_SYMBOLS[base_sym]}")
        if off:
            self.emit(f"  addi t0, t0, {off}")
        self.emit("  srli t0, t0, 2")
        if mask:
            self.emit(f"  ori  t0, t0, 0x{mask:x}")
        self.emit(f"  csrw pmpaddr{e}, t0")
        ph = {"pool": warl.PH_POOL, "ucode": warl.PH_UCODE, "text_end": warl.PH_TEXT_END, "data": PH_DATA}[base_sym]
        self.m.write_addr(e, ((ph + off) >> 2) | mask)
        self.addr_rel[e] = (base_sym, off, mask)
        self.emit(f"  csrr t1, pmpaddr{e}")
        self.report_reg("t1", item, f"{label} pmpaddr{e}", "rel", self.addr_rel[e])

    def set_cfg(self, e, b, item, label, form="csrrw"):
        n, ln = divmod(e, 4)
        return self.csr_op(form, pmpcfg(n), self.cfg_word_with(n, ln, b), item, f"{label} pmpcfg{n}")[1]

    def p_table_init(self):
        """The L=0 part of the survival table, before any lock or MMWP."""
        item = "setup"
        self.csr_op("csrrw", pmpaddr(E_CATCHALL), 0xFFFFFFFF, item, "catch-all")
        self.set_cfg(E_CATCHALL, cfg_byte(0, A_NAPOT, 1, 1, 1), item, "catch-all")
        self.set_rel_addr(E_UCODE, "ucode", 0, (1 << UCODE_NAPOT_ONES) - 1, item, "U code")
        self.set_cfg(E_UCODE, cfg_byte(0, A_NAPOT, 1, 1, 1), item, "U code")
        self.alloc_pair(code=False)
        self.set_rel_addr(E_POOL_B, "pool", 4, 0, item, "pool B")
        self.set_cfg(E_POOL_B, cfg_byte(0, A_NA4, 1, 1, 1), item, "pool B")

    # --- TP-PMP-011 ---------------------------------------------------------------------------------------------
    def tp011(self, n):
        meta = self.plan.items["TP-PMP-011"]
        meta.setdefault("writes", [])       # (idx, form, hi class, pre rlb, written rlb)
        picks = [(wchoice(self.rng, W_FORM_011), wchoice(self.rng, W_HI), self.rng.randrange(2)) for _ in range(n)]
        picks += [("csrrw", "zero", 1 - self.m.rlb), ("csrrw", "nonzero", self.m.rlb)]   # both hi classes, both RLB values
        for i, (form, cls, rlb) in enumerate(picks):
            hi = self.hi_bits(cls)
            if form == "csrrw":
                operand = self.msec_value(rlb, hi)
            elif form == "csrrs":
                operand = hi | (MSECCFG_RLB if rlb else 0)
            else:
                operand = hi | (0 if rlb else MSECCFG_RLB)
            pre_rlb = self.m.rlb
            wd = self.m.combined(form, CSR_MSECCFG, operand)
            idx = self.msec(form, operand, "TP-PMP-011", f"w{i} {cls}")
            meta["writes"].append((idx, form, cls, pre_rlb, (wd >> 2) & 1))
            self.filler(2)

    # --- TP-PMP-012 ---------------------------------------------------------------------------------------------
    def tp012(self):
        meta = self.plan.items["TP-PMP-012"]
        meta.setdefault("writes", [])       # (mseccfgh readback idx, mseccfg readback idx, form)
        forms = list(ALL_FORMS)
        self.rng.shuffle(forms)
        forms += [self.rng.choice(ALL_FORMS) for _ in range(self.rng.randint(0, 3))]
        for i, form in enumerate(forms):
            operand = self.rng.randint(1, 31) if form in UIMM_FORMS else (self.rng.getrandbits(32) or 1)
            dev = None
            if not self.any_l():
                cur = self.m.rlb
                if form in ("csrrw", "csrrwi"):
                    dev = (self.m.read(CSR_MSECCFG) ^ MSECCFG_RLB)
                elif form in ("csrrs", "csrrsi") and not cur:
                    dev = MSECCFG_RLB
                elif form in ("csrrc", "csrrci") and cur:
                    dev = MSECCFG_RLB
            red = dev is not None and self.red_here("TP-PMP-012")
            if red:
                if form in UIMM_FORMS:
                    self.emit(f"  {form} t1, {self.msec_name()}, {dev}")
                else:
                    self.li("t0", dev)
                    self.emit(f"  {form} t1, {self.msec_name()}, t0")
                self.emit(f"  csrr t1, {warl.csr_name(CSR_MSECCFGH)}")
                idx = self.report_reg("t1", "TP-PMP-012", f"w{i} readback mseccfgh", "abs", 0)
                self.plan.red_note = f"TP-PMP-012 w{i}: program {form} lands on mseccfg with 0x{dev:08x} instead of mseccfgh, read-back idx {idx + 1}"
            else:
                _o, idx = self.csr_op(form, CSR_MSECCFGH, operand, "TP-PMP-012", f"w{i}")
            self.emit(f"  csrr t1, {self.msec_name()}")
            idx2 = self.report_reg("t1", "TP-PMP-012", f"w{i} mseccfg unchanged", "abs", self.m.read(CSR_MSECCFG))
            if red:
                self.restore_msec()
            meta["writes"].append((idx, idx2, form))
            self.filler(2)

    # --- TP-PMP-024 ---------------------------------------------------------------------------------------------
    def tp024(self):
        meta = self.plan.items["TP-PMP-024"]
        meta["writes"] = []                 # (idx, pre rlb, written rlb, form)
        while True:
            seq = [self.rng.randrange(2) for _ in range(self.rng.randint(8, 14))]
            pre = self.m.rlb
            combos = set()
            for w in seq:
                combos.add((pre, w))
                pre = w
            if combos == {(0, 0), (0, 1), (1, 0), (1, 1)}:
                break
        for i, w in enumerate(seq):
            pre = self.m.rlb
            idx, form = self.rlb_op(w, "TP-PMP-024", f"w{i} rlb {pre}->{w}")
            meta["writes"].append((idx, pre, w, form))
            self.filler(1)

    # --- TP-PMP-108 toggles -----------------------------------------------------------------------------------------
    def tp108_toggles(self, n_change, n_hold):
        meta = self.plan.items["TP-PMP-108"]
        meta.setdefault("steps", [])        # idx per 108 write (walk entries carry the rest)
        kinds = ["change"] * n_change + ["hold"] * n_hold
        self.rng.shuffle(kinds)
        for i, kind in enumerate(kinds):
            target = (1 - self.m.rlb) if kind == "change" else self.m.rlb
            idx, _f = self.rlb_op(target, "TP-PMP-108", f"walk {sname(self.state())} {kind}")
            meta["steps"].append(idx)
            self.filler(1)

    def tp108_hold(self, label):
        meta = self.plan.items["TP-PMP-108"]
        form = self.rng.choice(("csrrw", "csrrs"))
        operand = self.msec_value(self.m.rlb) if form == "csrrw" else (self.hi_bits() | (MSECCFG_RLB * self.m.rlb))
        idx = self.msec(form, operand, "TP-PMP-108", f"walk {sname(self.state())} hold {label}", red=False)
        meta.setdefault("steps", []).append(idx)

    def tp108_final(self):
        """RLB set attempts at (1,x,0) with locks present: blocked, bit stays 0."""
        meta = self.plan.items["TP-PMP-108"]
        meta["blocked"] = []
        for form in self.rng.sample(("csrrw", "csrrs"), 2):
            operand = self.msec_value(1) if form == "csrrw" else (self.hi_bits() | MSECCFG_RLB)
            idx = self.msec(form, operand, "TP-PMP-108", f"walk {sname(self.state())} rlb set attempt", red=False)
            meta["steps"].append(idx)
            meta["blocked"].append(idx)

    # --- TP-PMP-022 / 023: sticky set and clear attempts ---------------------------------------------------------------
    def sticky_set(self, item, bit, rlb_after):
        """The set write of MML (022) or MMWP (023) with the first clear attempt adjacent; the item's red swaps them."""
        meta = self.plan.items[item]
        meta.setdefault("attempts", [])     # (idx, form)
        form = wchoice(self.rng, W_SET_FORM)
        operand = self.msec_value(rlb_after) | bit if form == "csrrw" else (self.hi_bits() | bit | (MSECCFG_RLB * rlb_after))
        if form == "csrrs" and rlb_after != self.m.rlb:
            form, operand = "csrrw", self.msec_value(rlb_after) | bit
        att_form = self.rng.choice(("csrrw", "csrrc"))
        att_operand = (self.msec_value(rlb_after) & ~bit & 0xFFFFFFFF) if att_form == "csrrw" else (self.hi_bits() | bit)
        pre, locked = self.state(), bool(self.locked_entries())
        wd_set = self.m.combined(form, CSR_MSECCFG, operand)
        if self.red_here(item):
            # program order: attempt first, then the set; the model keeps the planned order
            self.li("t0", att_operand)
            self.emit(f"  {att_form} t1, {self.msec_name()}, t0")
            self.m.op(form, CSR_MSECCFG, operand)
            mid = self.state()
            self.emit(f"  csrr t1, {self.msec_name()}")
            set_idx = self.report_reg("t1", item, f"set {form}", "abs", self.m.read(CSR_MSECCFG))
            self.li("t0", operand)
            self.emit(f"  {form} t1, {self.msec_name()}, t0")
            wd_att = self.m.combined(att_form, CSR_MSECCFG, att_operand)
            self.m.op(att_form, CSR_MSECCFG, att_operand)
            self.emit(f"  csrr t1, {self.msec_name()}")
            att_idx = self.report_reg("t1", item, f"attempt 0 {att_form}", "abs", self.m.read(CSR_MSECCFG))
            self.plan.red_note = f"{item}: the set write ({form}) is emitted after the first clear attempt ({att_form}); read-back idx {set_idx}"
            self.plan.walk.append({"idx": set_idx, "item": item, "form": form, "pre": pre, "wdata": wd_set, "post": mid, "locked": locked})
            self.plan.walk.append({"idx": att_idx, "item": item, "form": att_form, "pre": mid, "wdata": wd_att, "post": self.state(), "locked": locked})
            for st in (pre, mid, self.state()):
                if st not in self.plan.states:
                    self.plan.states.append(st)
            meta.setdefault("msec", []).extend([set_idx, att_idx])
        else:
            set_idx = self.msec(form, operand, item, f"set {form}", red=False)
            att_idx = self.msec(att_form, att_operand, item, f"attempt 0 {att_form}", red=False)
        meta["set_idx"] = set_idx
        meta["attempts"].append((att_idx, att_form))
        assert (self.m.read(CSR_MSECCFG) & bit) and self.m.rlb == rlb_after

    def sticky_attempts(self, item, bit, n):
        """Clear attempts of a sticky bit: csrrw 0, csrrc bit, csrrw random with the bit 0; also the 1->1 write."""
        meta = self.plan.items[item]
        meta.setdefault("attempts", [])
        forms = ["csrrw", "csrrc"] + [self.rng.choice(("csrrw", "csrrc", "csrrs")) for _ in range(n)]
        self.rng.shuffle(forms)
        for form in forms:
            if form == "csrrw":
                operand = self.msec_value(self.rng.randrange(2)) & ~bit & 0xFFFFFFFF
                if self.rng.random() < 0.3:
                    operand = 0
            elif form == "csrrc":
                operand = bit | self.hi_bits()
            else:
                operand = bit | self.hi_bits() | (MSECCFG_RLB * self.m.rlb)
            idx = self.msec(form, operand, item, f"attempt {len(meta['attempts'])} {form}", red=False)
            meta["attempts"].append((idx, form))
            self.filler(1)

    # --- lock step and TP-PMP-031 table --------------------------------------------------------------------------------
    def rlb_set_026(self):
        meta = self.plan.items["TP-PMP-026"]
        if self.m.rlb:
            self.rlb_op(0, "TP-PMP-108", "walk pre-lock rlb clear", red=False)
        idx, form = self.rlb_op(1, "TP-PMP-026", "set RLB before the locks", red=False)
        meta["set_idx"] = idx
        assert self.m.rlb == 1 and not self.any_l()

    def lock_table(self):
        """The L=1 survival rules and the 031 mixed rows, all under RLB = 1 and MML = 0."""
        item = "TP-PMP-031"
        meta = self.plan.items[item]
        self.set_rel_addr(E_CODE, "ucode", 0, 0, item, "code rule TOR top")
        self.set_cfg(E_CODE, cfg_byte(1, A_TOR, 1, 0, 1), item, "code rule L=1 R/X")
        self.set_rel_addr(E_POOL_A, "pool", 0, 0, item, "pool A")
        self.set_cfg(E_POOL_A, cfg_byte(1, A_NA4, 0, 1, 1), item, "pool A L=1 RW")
        self.csr_op("csrrw", pmpaddr(E_MMIO), (MEMORY_MAP["mmio_base"] >> 2) | ((1 << MMIO_NAPOT_ONES) - 1), item, "MMIO page")
        self.set_cfg(E_MMIO, cfg_byte(1, A_NAPOT, 0, 1, 1), item, "MMIO L=1 RW")
        self.set_rel_addr(E_DATA, "data", 0, (1 << DATA_NAPOT_ONES) - 1, item, ".data")
        self.set_cfg(E_DATA, cfg_byte(1, A_NAPOT, 0, 1, 1), item, ".data L=1 RW")
        # mixed rows: random L/RWX/A, at least one RW=01 row (legalised to W=0 under MML=0), at most one L=1
        mixed = list(E_MIXED)
        self.rng.shuffle(mixed)
        l_slot = self.rng.choice(mixed + [None])
        rw01_slot = self.rng.choice(mixed)
        meta["mixed"] = []
        for e in mixed:
            l = 1 if e == l_slot else 0
            if e == rw01_slot:
                r, w, x = 0, 1, self.rng.randrange(2)
            else:
                r, w, x = self.rng.randrange(2), self.rng.randrange(2), self.rng.randrange(2)
            a = wchoice(self.rng, W_A_ANY)
            self.csr_op("csrrw", pmpaddr(e), self.rng.getrandbits(32), item, f"mixed e{e} addr")
            idx = self.set_cfg(e, cfg_byte(l, a, x, w, r), item, f"mixed e{e} LRWX {l}{r}{w}{x}")
            meta["mixed"].append((idx, e, l, r, w, x))
        meta["locks"] = [e for e in range(NUM_REGIONS) if (self.m.cfg[e] >> 7) & 1]
        self.plan.items["TP-PMP-026"]["locks"] = list(meta["locks"])

    def all_csrs(self):
        return [pmpcfg(n) for n in range(NUM_CFG_CSRS)] + [pmpaddr(e) for e in range(NUM_REGIONS)]

    def read_all(self, item, label):
        idxs = []
        for csr in self.all_csrs():
            self.emit(f"  csrr t1, {warl.csr_name(csr)}")
            e = csr - warl.PMPADDR_BASE
            if warl.is_addr(csr) and self.addr_rel[e] is not None:
                idxs.append(self.report_reg("t1", item, f"{label} {warl.csr_name(csr)}", "rel", self.addr_rel[e]))
            else:
                idxs.append(self.report_reg("t1", item, f"{label} {warl.csr_name(csr)}", "abs", self.m.read(csr)))
        return idxs

    def m_probe(self, word_off, allowed, item, label):
        """M-mode load of a pool word with the handler armed (s10 = probe pc); reports the trap marker and the value."""
        self.mprobe_n += 1
        lab = f"gen_mprobe_{self.mprobe_n}"
        self.li("s11", NOTRAP_MARK)
        self.li("s5", LOAD_SENT)
        self.emit(f"  addi s2, s1, {word_off}")
        self.emit(f"  la   s10, {lab}")
        self.emit(".option push")
        self.emit(".option norvc")
        self.emit(f"{lab}:")
        self.emit("  lw   s5, 0(s2)")
        self.emit(".option pop")
        self.li("s10", 0)
        marker = self.report_reg("s11", item, f"{label} M probe marker", "abs", NOTRAP_MARK if allowed else CAUSE_LOAD_M_RECORD)
        value = self.report_reg("s5", item, f"{label} M probe value", "abs", self.pool[word_off // 4][0] if allowed else LOAD_SENT)
        return marker, value

    def u_probe(self, word_off, allowed, item, label):
        """U-mode load of a pool word through the U stub; the handler records a denied load, then the ecall."""
        self.li("s5", LOAD_SENT)
        self.emit(f"  addi s2, s1, {word_off}")
        self.enter_u("gen_ustub_load", item, label)
        recs = []
        if not allowed:
            recs.append(self.expect_record(item, f"{label} U probe denied", record(CAUSE_LOAD, 0)))
        recs.append(self.expect_record(item, f"{label} U ecall", record(CAUSE_ECALL_U, 1)))
        value = self.report_reg("s5", item, f"{label} U probe value", "abs", self.pool[word_off // 4][0] if allowed else LOAD_SENT)
        return recs, value

    def tp031_pass(self, when):
        meta = self.plan.items["TP-PMP-031"]
        mml = self.m.mml
        assert mml == (1 if when == "after" else 0)
        # the model's own view of the two probe regions (the survival table decides both verdicts)
        assert byte_fields(self.m.cfg[E_POOL_B]) == (0, A_NA4, 1, 1, 1) and byte_fields(self.m.cfg[E_POOL_A]) == (1, A_NA4, 0, 1, 1)
        meta[f"csr_{when}"] = self.read_all("TP-PMP-031", f"{when} MML")
        if when == "after" and self.red_here("TP-PMP-031"):
            # red (b): one free pmpaddr changed before the after pass is read back, restored after it
            e = self.red_rng.choice(self.unlocked_free())
            dev = self.m.read(pmpaddr(e)) ^ (1 << self.red_rng.randrange(32))
            self.plan.red_note = f"TP-PMP-031: pmpaddr{e} changed to 0x{dev:08x} between the two csrr passes, read-back idx {meta['csr_after'][NUM_CFG_CSRS + e]}"
            body = self.main
            ins = len(body) - 2 * len(self.all_csrs())
            body[ins:ins] = [f"  li   t0, 0x{dev:08x}", f"  csrw pmpaddr{e}, t0"]
            self.restore(pmpaddr(e))
        probes = ["m", "u"]
        self.rng.shuffle(probes)
        allowed = when == "before"
        for p in probes:
            if p == "m":
                off = 4
                if when == "after" and self.red_here("TP-PMP-031"):
                    off = 0     # red (a): the M probe targets pool word A (L=1 RW: M-mode allowed under MML=1)
                    self.plan.red_note = "TP-PMP-031: the after-MML M-mode probe loads pool word A (allowed) instead of pool word B"
                meta[f"m_{when}"] = self.m_probe(off, allowed, "TP-PMP-031", f"{when} MML")
            else:
                meta[f"u_{when}"] = self.u_probe(0, allowed, "TP-PMP-031", f"{when} MML")

    # --- TP-PMP-030 ------------------------------------------------------------------------------------------------
    def tp030(self):
        meta = self.plan.items["TP-PMP-030"]
        assert self.m.mml == 1 and self.m.rlb == 1
        self.emit(f"  csrr t1, {self.msec_name()}")
        meta["msec_before"] = self.report_reg("t1", "TP-PMP-030", "mseccfg under RLB=1", "abs", self.m.read(CSR_MSECCFG))
        rows = list(EXEC_ROWS)
        self.rng.shuffle(rows)
        meta["rows"] = []                   # (idx, e, written byte)
        for i, (r, w, x) in enumerate(rows):
            e = E_030
            n, ln = divmod(e, 4)
            b = cfg_byte(1, wchoice(self.rng, W_A_ANY), x, w, r)
            if self.red_here("TP-PMP-030"):
                self.emit(f"  csrr t1, pmpcfg{n}")
                self.m.write_cfg(n, self.cfg_word_with(n, ln, b))
                idx = self.report_reg("t1", "TP-PMP-030", f"row {i} readback pmpcfg{n}", "abs", self.m.read_cfg(n))
                self.plan.red_note = f"TP-PMP-030 row {i}: the accepted write of LRWX 1{r}{w}{x} to entry {e} is skipped, read-back idx {idx}"
                self.restore(pmpcfg(n))
            else:
                idx = self.set_cfg(e, b, "TP-PMP-030", f"row {i} LRWX 1{r}{w}{x}")
            assert self.m.cfg[e] == b
            meta["rows"].append((idx, e, b))
            self.filler(1)

    def tp030_repeat(self):
        """After the RLB clear: one exec row on a free entry is suppressed again."""
        meta = self.plan.items["TP-PMP-030"]
        assert self.m.mml == 1 and self.m.rlb == 0
        self.emit(f"  csrr t1, {self.msec_name()}")
        meta["msec_after"] = self.report_reg("t1", "TP-PMP-030", "mseccfg under RLB=0", "abs", self.m.read(CSR_MSECCFG))
        e = self.rng.choice(self.unlocked_free())
        r, w, x = self.rng.choice(EXEC_ROWS)
        pre = self.m.cfg[e]
        idx = self.set_cfg(e, cfg_byte(1, wchoice(self.rng, W_A_ANY), x, w, r), "TP-PMP-030", f"repeat LRWX 1{r}{w}{x} suppressed")
        assert self.m.cfg[e] == pre
        meta["repeat"] = (idx, e, pre)

    # --- TP-PMP-027 / 028 / 029 ------------------------------------------------------------------------------------
    def word_write(self, item, label, n, offend, ordinary, form):
        """One pmpcfg word write: offend = {lane: LRWX byte} (suppressed rows), ordinary = {lane: byte} (stored);
        the red of 027/028 writes one offending byte with L = 0 (stored), 029's writes its row as an exec row."""
        pre_word = self.m.read_cfg(n)
        value = 0
        for ln in range(4):
            b = offend.get(ln, ordinary.get(ln))
            if b is None:
                b = self.m.cfg[4 * n + ln] if form == "csrrw" else 0
            value |= b << (8 * ln)
        red_lane = None
        if self.red_here(item):
            red_lane = self.red_rng.choice(sorted(offend))
            b = offend[red_lane]
            if item == "TP-PMP-029":
                dev = cfg_byte(1, (b >> 3) & 3, 1, 0, 0)          # LRWX 1001: suppressed instead of stored
            else:
                dev = b & 0x7F                                     # L = 0: stored instead of suppressed
            dev_value = (value & ~(0xFF << (8 * red_lane))) | (dev << (8 * red_lane))
            self.li("t0", dev_value)
            self.emit(f"  {form} t1, pmpcfg{n}, t0")
            self.m.op(form, pmpcfg(n), value)
            self.emit(f"  csrr t1, pmpcfg{n}")
            idx = self.report_reg("t1", item, f"{label} readback pmpcfg{n}", "abs", self.m.read_cfg(n))
            self.plan.red_note = f"{item} {label}: lane {red_lane} of pmpcfg{n} written 0x{dev:02x} for planned 0x{b:02x}, read-back idx {idx}"
            self.restore(pmpcfg(n))
        else:
            _o, idx = self.csr_op(form, pmpcfg(n), value, item, label)
        return idx, pre_word, value

    def tp027(self):
        meta = self.plan.items["TP-PMP-027"]
        meta["writes"] = []                 # dicts: idx n form pre value offend(lanes->byte) ordinary(lanes->byte) modes rows
        pairs = [(n, f) for n in range(NUM_CFG_CSRS) for f in ("csrrw", "csrrs")]
        self.rng.shuffle(pairs)
        rows = list(EXEC_ROWS) * 2
        modes = list(SUPPRESS_MODES) * 3
        self.rng.shuffle(rows)
        self.rng.shuffle(modes)
        for i, (n, form) in enumerate(pairs):
            free = [e % 4 for e in self.unlocked_free(n)]
            free += [e for e in (E_UCODE, E_POOL_B) if n == 0]
            assert len(free) >= 2, f"TP-PMP-027 word {n}: fewer than two unlocked entries"
            self.rng.shuffle(free)
            n_off = self.rng.randint(1, min(3, len(free) - 1))
            off_lanes, ord_lanes = free[:n_off], free[n_off:]
            offend, ordinary = {}, {}
            if form == "csrrs":
                # csrrs ORs into the current bytes: the target lanes are cleared first so the combined byte is the row itself
                prep = self.m.read_cfg(n)
                for ln in off_lanes + ord_lanes:
                    prep &= ~(0xFF << (8 * ln)) & 0xFFFFFFFF
                self.csr_op("csrrw", pmpcfg(n), prep, "TP-PMP-027", f"w{i} prep pmpcfg{n}")
            for ln in off_lanes:
                r, w, x = rows[i]
                a = modes[i]
                offend[ln] = cfg_byte(1, a, x, w, r)
            for ln in ord_lanes:
                cur = self.m.cfg[4 * n + ln]
                while True:
                    b = cfg_byte(0, self.rng.randrange(4), self.rng.randrange(2), self.rng.randrange(2), self.rng.randrange(2))
                    b = self.m.legalise_byte(b)
                    if b != cur and b != 0:
                        break
                ordinary[ln] = b
            idx, pre, value = self.word_write("TP-PMP-027", f"w{i} pmpcfg{n} {form}", n, offend, ordinary, form)
            comb = self.m.combined(form, pmpcfg(n), value) if form == "csrrs" else value
            meta["writes"].append({"idx": idx, "n": n, "form": form, "pre": pre, "value": comb,
                                   "offend": sorted(offend), "ordinary": sorted(ordinary),
                                   "modes": [(offend[ln] >> 3) & 3 for ln in sorted(offend)],
                                   "rows": [byte_fields(offend[ln])[2:][::-1] for ln in sorted(offend)]})
            self.filler(1)

    def tp028(self):
        meta = self.plan.items["TP-PMP-028"]
        meta["writes"] = []
        rows = [(r, w, x) for (r, w, x) in EXEC_ROWS if x]
        self.rng.shuffle(rows)
        for i, (r, w, x) in enumerate(rows):
            e = self.rng.choice(self.unlocked_free())
            n, ln = divmod(e, 4)
            pre_byte = self.m.cfg[e]
            idx, pre, value = self.word_write("TP-PMP-028", f"w{i} pmpcfg{n} A=OFF", n, {ln: cfg_byte(1, A_OFF, x, w, r)}, {}, "csrrw")
            assert self.m.cfg[e] == pre_byte
            meta["writes"].append((idx, n, ln, pre, cfg_byte(1, A_OFF, x, w, r)))

    def tp029(self):
        meta = self.plan.items["TP-PMP-029"]
        meta["writes"] = []                 # (idx, n, lane, written byte)
        rows = list(NONEXEC_ROWS)
        self.rng.shuffle(rows)
        entries = self.rng.sample(self.unlocked_free(), len(rows))
        for i, ((r, w, x), e) in enumerate(zip(rows, entries)):
            n, ln = divmod(e, 4)
            b = cfg_byte(1, wchoice(self.rng, W_A_ANY), x, w, r)
            idx, _pre, _v = self.word_write("TP-PMP-029", f"w{i} pmpcfg{n} LRWX 1{r}{w}{x}", n, {ln: b}, {}, "csrrw")
            assert self.m.cfg[e] == b
            meta["writes"].append((idx, n, ln, b))

    # --- TP-PMP-025 / 026 attempts -----------------------------------------------------------------------------------
    def tp025(self):
        meta = self.plan.items["TP-PMP-025"]
        meta["attempts"] = []               # (idx, form, written rlb)
        meta["locks"] = [(e, (self.m.cfg[e] >> 3) & 3) for e in self.locked_entries()]
        assert self.m.rlb == 0 and meta["locks"]
        forms = ["csrrw", "csrrs", self.rng.choice(("csrrw", "csrrs"))]
        targets = [1, 1, 0] + [self.rng.randrange(2) for _ in range(self.rng.randint(0, 3))]
        forms += [self.rng.choice(("csrrw", "csrrs")) for _ in range(len(targets) - len(forms))]
        order = list(zip(forms, targets))
        self.rng.shuffle(order)
        for i, (form, t) in enumerate(order):
            if form == "csrrw":
                operand = self.hi_bits() | (self.rng.randrange(4)) | (MSECCFG_RLB * t)
            else:
                operand = self.hi_bits() | (MSECCFG_RLB * t) | self.rng.randrange(4)
            if t and self.red_here("TP-PMP-025"):
                self.li("t0", operand)
                self.emit(f"  {form} t1, {self.msec_name()}, t0")
                self.m.op(form, CSR_MSECCFG, operand)
                self.emit(f"  csrr t1, {self.msec_name()}")
                idx = self.report_reg("t0", "TP-PMP-025", f"attempt {i} {form} readback mseccfg", "abs", self.m.read(CSR_MSECCFG))
                self.plan.red_note = f"TP-PMP-025 attempt {i}: the program reports the written operand 0x{operand:08x} in place of the read-back, idx {idx}"
                self.plan.walk.append({"idx": idx, "item": "TP-PMP-025", "form": form, "pre": self.state(), "wdata": operand,
                                       "post": self.state(), "locked": True})
                self.plan.items["TP-PMP-025"].setdefault("msec", []).append(idx)
            else:
                idx = self.msec(form, operand, "TP-PMP-025", f"attempt {i} {form}", red=False)
            meta["attempts"].append((idx, form, t))
            self.filler(1)

    def rlb_clear_026(self):
        meta = self.plan.items["TP-PMP-026"]
        assert self.m.rlb == 1 and self.locked_entries() == [] and self.any_l()
        form = self.rng.choice(("csrrw", "csrrc"))
        operand = self.msec_value(0) if form == "csrrw" else (MSECCFG_RLB | self.hi_bits())
        pre, wd = self.state(), self.m.combined(form, CSR_MSECCFG, operand)
        if self.red_here("TP-PMP-026"):
            self.m.op(form, CSR_MSECCFG, operand)
            self.emit(f"  csrr t1, {self.msec_name()}")
            idx = self.report_reg("t1", "TP-PMP-026", f"clear RLB {form}", "abs", self.m.read(CSR_MSECCFG))
            self.plan.red_note = f"TP-PMP-026: the RLB clear ({form}) is skipped at its site and performed after the read-back idx {idx}"
            self.li("t0", operand)
            self.emit(f"  {form} t1, {self.msec_name()}, t0")
            self.plan.walk.append({"idx": idx, "item": "TP-PMP-026", "form": form, "pre": pre, "wdata": wd, "post": self.state(), "locked": False})
            if self.state() not in self.plan.states:
                self.plan.states.append(self.state())
            meta.setdefault("msec", []).append(idx)
        else:
            idx = self.msec(form, operand, "TP-PMP-026", f"clear RLB {form}", red=False)
        assert self.m.rlb == 0 and self.locked_entries()
        meta["clear_idx"] = idx

    def rlb_attempt_026(self):
        meta = self.plan.items["TP-PMP-026"]
        form = self.rng.choice(("csrrw", "csrrs"))
        operand = self.msec_value(1) if form == "csrrw" else (MSECCFG_RLB | self.hi_bits())
        meta["attempt_idx"] = self.msec(form, operand, "TP-PMP-026", f"set RLB again {form}", red=False)
        meta["locks_at_attempt"] = self.locked_entries()

    # --- program body -------------------------------------------------------------------------------------------------
    def low_phase(self):
        n_change = self.rng.randint(9, 11) if self.plan.path == "mmwp_first" else self.rng.randint(17, 19)
        blocks = [lambda: self.tp011(self.rng.randint(4, 7)), self.tp012, self.tp024,
                  lambda: self.tp108_toggles(n_change, self.rng.randint(2, 4))]
        self.rng.shuffle(blocks)
        for blk in blocks:
            blk()
        assert not self.any_l() and self.m.mml == 0 and self.m.mmwp == 0

    def s01x_phase(self):
        blocks = [lambda: self.tp011(self.rng.randint(1, 3)), lambda: self.sticky_attempts("TP-PMP-023", MSECCFG_MMWP, self.rng.randint(0, 2)),
                  lambda: self.tp108_toggles(self.rng.randint(8, 10), self.rng.randint(1, 3))]
        self.rng.shuffle(blocks)
        for blk in blocks:
            blk()

    def high_phase(self):
        """s1x0 with MMWP = 1: hold attempts, the suppression items, then the blocked RLB attempts."""
        assert self.state() == (1, 1, 0)
        blocks = [lambda: self.sticky_attempts("TP-PMP-022", MSECCFG_MML, self.rng.randint(1, 3)),
                  lambda: self.sticky_attempts("TP-PMP-023", MSECCFG_MMWP, self.rng.randint(0, 2)), self.tp030_repeat]
        self.rng.shuffle(blocks)
        for blk in blocks:
            blk()
        blocks = [self.tp027, self.tp028]
        self.rng.shuffle(blocks)
        for blk in blocks:
            blk()
        self.tp029()
        blocks = [self.tp025, self.rlb_attempt_026, self.tp108_final]
        self.rng.shuffle(blocks)
        for blk in blocks:
            blk()

    def build(self):
        path = self.plan.path
        self.p0()
        self.p_table_init()
        self.low_phase()
        if path == "mmwp_first":
            self.sticky_set("TP-PMP-023", MSECCFG_MMWP, self.rng.randrange(2))
            self.s01x_phase()
        self.rlb_set_026()
        self.lock_table()
        self.tp031_pass("before")
        self.sticky_set("TP-PMP-022", MSECCFG_MML, 1)
        self.tp108_hold("under MML")
        self.tp031_pass("after")
        self.tp030()
        if path == "mml_first_rlb":
            self.sticky_set("TP-PMP-023", MSECCFG_MMWP, 1)
            self.tp108_hold("MMWP under RLB=1")
            self.rlb_clear_026()
        elif path == "mml_first_late":
            self.rlb_clear_026()
            self.tp108_hold("s100")
            self.sticky_set("TP-PMP-023", MSECCFG_MMWP, 0)
        else:
            self.rlb_clear_026()
        self.high_phase()
        self.p5_end()
        self.handler_and_stubs()
        assert self.red_target is None or self.plan.red_note, "red fixture: the deviation site was not emitted"
        self.plan.red_sites = self.red_sites
        self.check_coverage()
        header = ["# gen_pmp_mseccfg: generated per-seed program of gen_test_pmp_mseccfg (seed %d, path %s%s)." % (
                      self.plan.seed, path, ", RED fixture " + self.plan.red_item if self.plan.red else ""),
                  "# Generator: dv/auto_dv/tests/gen_programs/gen_pmp_mseccfg_prog.py (do not edit; regenerate).",
                  '.include "gen_mmio_map.h"', ".section .text", ".globl _start", "_start:"]
        self.plan.lines = header + self.main + self.aux + self.data_section()
        return self.plan

    def check_coverage(self):
        """The plan's own floors: what every item says 'every ...' about is present in this seed."""
        p, it = self.plan, self.plan.items
        w108 = [w for w in p.walk if w["item"] == "TP-PMP-108"]
        changed = sum(1 for w in w108 if w["pre"] != w["post"])
        assert changed >= 16, f"TP-PMP-108: only {changed} state-changing walk writes"
        assert any(w["pre"][2] == 0 and w["post"][2] == 1 and not w["locked"] for w in w108), "TP-PMP-108: no free RLB 0->1"
        assert any(w["pre"] == (1, 1, 0) and (w["wdata"] >> 2) & 1 and w["post"] == (1, 1, 0) for w in w108), "TP-PMP-108: no blocked (1,x,0)->(1,x,1)"
        expect_states = {"mmwp_first": {(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)},
                         "mml_first_rlb": {(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (1, 1, 0)},
                         "mml_first_late": {(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0), (1, 1, 0)}}[p.path]
        seen108 = {st for w in w108 for st in (w["pre"], w["post"])}
        assert seen108 == expect_states, f"TP-PMP-108: walk states {sorted(seen108)} != path set {sorted(expect_states)}"
        it["TP-PMP-108"]["states"] = sorted(expect_states)
        w011 = it["TP-PMP-011"]["writes"]
        assert {c for _i, _f, c, _p, _w in w011} == {"nonzero", "zero"} and {w for *_r, w in w011} == {0, 1} and {p_ for _i, _f, _c, p_, _w in w011} == {0, 1} \
            and any(f == "csrrw" for _i, f, _c, _p, _w in w011), "TP-PMP-011: hi-bit classes, RLB pre/written values or csrrw missing"
        assert {f for _a, _b, f in it["TP-PMP-012"]["writes"]} == set(ALL_FORMS), "TP-PMP-012: an op form is missing"
        assert {(pre, w) for _i, pre, w, _f in it["TP-PMP-024"]["writes"]} == {(0, 0), (0, 1), (1, 0), (1, 1)}
        for item in ("TP-PMP-022", "TP-PMP-023"):
            forms = {f for _i, f in it[item]["attempts"]}
            assert {"csrrw", "csrrc"} <= forms, f"{item}: attempt forms {forms}"
        w027 = it["TP-PMP-027"]["writes"]
        assert {w["n"] for w in w027} == set(range(NUM_CFG_CSRS)) and {w["form"] for w in w027} == {"csrrw", "csrrs"}
        assert {m for w in w027 for m in w["modes"]} == set(SUPPRESS_MODES), "TP-PMP-027: a suppression mode is missing"
        assert {tuple(r) for w in w027 for r in w["rows"]} == set(EXEC_ROWS), "TP-PMP-027: an exec row is missing"
        assert len(it["TP-PMP-029"]["writes"]) == 4 and len(it["TP-PMP-030"]["rows"]) == 4
        assert {t for _i, _f, t in it["TP-PMP-025"]["attempts"]} == {0, 1}
        assert len(self.pool) == 2

    # --- handler, U stub, data ---------------------------------------------------------------------------------------------
    def handler_and_stubs(self):
        self.in_main = False
        a = self.aux
        a += ["", "# M-mode trap handler (mtvec base): a trap from U stores one record word (mcause << 16 | MPP << 8 | index",
              "# of the instruction in the stub) to the report channel, skips the U instruction or returns to M at s8 on ecall;",
              "# a trap from M is expected only at the armed probe (mepc == s10): the record goes to s11 and the load is skipped;",
              f"# any other M-mode trap ends the program with tohost {TOHOST_FAIL}.",
              ".align 8", "gen_trap_vec:",
              "  csrr t0, mcause", "  csrr t1, mepc", "  csrr t2, mstatus",
              "  srli t2, t2, 11", "  andi t2, t2, 3",
              f"  li   t3, {MPP_M}", "  bne  t2, t3, 1f",
              "  beq  t1, s10, 6f", "  j    gen_trap_m_fail",
              "6:", "  slli t0, t0, 16", f"  li   t3, 0x{MPP_M << 8:x}", "  or   s11, t0, t3",
              "  addi t1, t1, 4", "  csrw mepc, t1", "  li   s10, 0", "  mret",
              "1:", "  slli t2, t2, 8", "  sub  t3, t1, s9", "  srli t3, t3, 2", "  andi t3, t3, 0xff",
              "  slli t0, t0, 16", "  or   t0, t0, t2", "  or   t0, t0, t3",
              "  li   t2, GEN_MM_EOT_ADDR", "  sw   t0, 0(t2)",
              "  csrr t0, mcause", f"  li   t3, {CAUSE_ECALL_U}", "  beq  t0, t3, 3f",
              "  addi t1, t1, 4", "  csrw mepc, t1", "  mret",
              "3:", "  csrw mepc, s8", f"  li   t0, 0x{MPP_MASK:x}", "  csrs mstatus, t0", "  mret",
              "gen_trap_m_fail:",
              "  slli t0, t0, 16", "  slli t2, t2, 8", "  or   t0, t0, t2",
              "  li   t2, GEN_MM_EOT_ADDR", "  sw   t0, 0(t2)",
              f"  li   gp, {TOHOST_FAIL}", "  la   t5, tohost", "  sw   gp, 0(t5)",
              "5:", "  j    5b",
              "", "# U-mode code area: one NAPOT region (entry 1, L=0 RWX) covers it; fixed-size instructions so the",
              "# handler's record carries the index of the trapping instruction; global labels for the symbol table.",
              f".align {UCODE_ALIGN_BITS}", ".globl gen_u_code", "gen_u_code:", ".option push", ".option norvc",
              "gen_ustub_load:", "  lw   s5, 0(s2)", "  ecall",
              ".option pop", f".align {UCODE_ALIGN_BITS}", ".globl gen_text_end", "gen_text_end:"]

    def data_section(self):
        d = ["", ".section .data", f".align {DATA_ALIGN_BITS}", ".globl gen_data_base", "gen_data_base:",
             ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
             f".align {warl.POOL_ALIGN_BITS}", "# probe pool: word A (L=1 RW region, entry 2) and word B (L=0 RWX region, entry 3)",
             ".globl gen_probe_pool", "gen_probe_pool:"]
        d += [f"  .word 0x{w:08x}" for w, _k in self.pool]
        d += [".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {self.plan.min_retired}"]
        size = 16 + (1 << warl.POOL_ALIGN_BITS) + 4 * len(self.pool) + 4
        assert size <= (1 << DATA_ALIGN_BITS), ".data exceeds its NAPOT"
        return d


def plan(seed, red=False, red_item=None):
    """The green plan of a seed, or the red fixture: the same expectations with one program deviation of one
    item (red_item, else drawn with the item's site from random.Random(f"{seed}:red"))."""
    green = Gen(seed).build()
    if not red:
        return green
    rng = random.Random(f"{int(seed)}:{RED_RNG_TAG}")
    item = red_item or rng.choice(RED_ITEMS)
    assert item in ITEMS, f"red: unknown item {item}"
    sites = green.red_sites[item]
    assert sites, f"red: no deviation site for {item} at seed {seed}"
    p = Gen(seed, red_target=(item, rng.choice(sites))).build()
    assert p.signature() == green.signature() and p.path == green.path and p.min_retired <= green.min_retired + 8, "red: the expectations moved"
    assert p.red_item == item
    return p


def emit(p):
    text = "\n".join(p.lines) + "\n"
    assert all(ord(ch) < 128 for ch in text), "generated program is not ASCII"
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, help="assembly output file")
    ap.add_argument("--red", action="store_true", help="red fixture: the program deviates on one intent of one item")
    ap.add_argument("--red-item", choices=ITEMS, help="the item the red fixture targets (default: drawn from the seed)")
    ap.add_argument("--summary", action="store_true", help="print k, min_retired, the path and the per-item report counts")
    args = ap.parse_args(argv)
    p = plan(args.seed, args.red, args.red_item)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(emit(p))
    if args.summary or not args.out:
        per_item = {}
        for r in p.reports:
            per_item[r.item] = per_item.get(r.item, 0) + 1
        print(f"seed={p.seed} red={p.red} path={p.path} k={p.k} min_retired={p.min_retired} lines={len(p.lines)} "
              f"states={[sname(s) for s in p.states]} walk={len(p.walk)} per_item={per_item}"
              + f" red_sites={ {k: len(v) for k, v in p.red_sites.items()} }"
              + (f" red_item={p.red_item} red_note={p.red_note}" if p.red else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
