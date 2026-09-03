#!/usr/bin/env python3
"""gen_pmp_lock_prog: per-seed program generator of gen_test_pmp_lock (plan group gen_pmp_lock, items
TP-PMP-013..021 and TP-PMP-112 of dv/auto_dv/docs/gen_test_plan.md Section 4.4).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:pmp_lock"), runs
the shared PmpModel of gen_pmp_csr_warl_prog (the lock, TOR-lock, RLB and mseccfg rules as the privileged
specification states them; the RTL is a cross-check only) and returns a Plan: the assembly lines, the ordered
expected report words (the raw csrr read-back after every PMP CSR write, one probe load), k, min_retired and
per-item metadata for the fire-checks. Two expectations are layout-relative (pmpaddr0 = end of .text,
TP-PMP-019's pmpaddr = a probe-pool word) and resolve from the image's symbol table through bases_from_symbols.

One run has no wrapper reset, so the lock state only ever grows: a lock taken under RLB=0 is permanent, RLB
can be set only while no enforced lock exists, MML is sticky. The phase order follows from that:
  P0 mtvec, entry 0 cleared, pmpaddr0 = end of .text (never written again)
  P1 TP-PMP-021: mseccfg.RLB set first; 3..4 entries locked (one TOR above an unlocked entry); locked
     pmpcfg / pmpaddr and the pmpaddr below the locked TOR rewritten and read back changed under RLB=1;
     then every locked entry is rewritten to L=1/A=OFF (kept) or L=0 (released) so that TP-PMP-019 later
     sees only A=OFF locks
  P2 TP-PMP-112: the one RLB clear (csrw/csrrc/csrrci) with locks present, followed at gap 0 by a write to a
     locked pmpcfg (variant A) or pmpaddr (variant B), both read back unchanged; more locked writes after
     1..3 fillers; TP-PMP-021's repeated write after the clear is ignored
  P3 TP-PMP-013 none-mix write to pmpcfg0 (no lock in the word)
  P4 TP-PMP-019: L=1/A=OFF lock on a fresh entry whose pmpaddr names a probe-pool word; rewrites ignored;
     csrrs mseccfg RLB stays 0 while every locked entry is A=OFF; an M-mode load probe of that word
  P5 TP-PMP-020: 3..4 episodes, each a lock-setting write immediately (gap 0, or 1..3 / >= 4 fillers on the
     extra episode) followed by csrw pmpaddr(i) / csrw pmpcfg of the same word / csrw mseccfg RLB=1
  P6 TP-PMP-015, 016, 017, 018 in a shuffled order (018 owns entry PMPNumRegions-1)
  P7 TP-PMP-014: its own lock, then pmpaddr writes to locked entries of every A mode
  P8 TP-PMP-013: lock mixes per word (one word all locked, the others 1..3), csrrw/csrrs/csrrc writes;
     TP-PMP-112's later RLB set attempt while non-OFF locks exist
  P9 (half of the seeds) MML=1 tail: unlocked entries cleared, the code rule (entry 0, L=1 R/X TOR over
     [0, end of .text)), MML set, locked writes still ignored, RLB still 0
Dropped clauses (owner: plan; one run, no wrapper reset): TP-PMP-112 variant C (a locked TOR at the clear
would break TP-PMP-019's all-locks-OFF condition later in the same run) and its repeated RLB clears; MML is 0
at the clear (the MML=0 items follow it); MMWP is never set (M-mode default-deny needs a full rule set).
Safety rule: an entry that is L=1 with A != OFF always holds pmpaddr <= SAFE_MAX_WORD (region below the
program window); under MML=1 every unlocked entry is OFF and entry 0 is the code rule.

Red fixtures (--red [--red-item TP-PMP-0nn]): the PROGRAM deviates on one intent of one item while the plan
stays the green plan. At the drawn site a write is replaced by a read of the same CSR (same instruction
count) and the planned state is restored without a report afterwards: 013 a lock-mix word write (whole-word
suppression); 014, 015, 018 (second half), 019, 020 the lock-setting write, so the follow-up write lands;
016, 017, 018 (first half), 021 a write that should land; 112 the RLB clear, so the adjacent locked write
lands. The red program's retirement floor is the green one.

CLI: python3 gen_pmp_lock_prog.py --seed N --out <file.S> [--red [--red-item TP-PMP-0nn]] [--summary]
     python3 gen_pmp_lock_prog.py --seed N --check-spike <spike_commits.log> --sym <prog.sym.json>
"""
import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP  # noqa: E402
from dv.auto_dv.tests.gen_programs.gen_prog_const import (  # noqa: E402
    CSR, PMPADDR_BASE, PMPCFG_BASE, TOHOST_FAIL, TOHOST_PASS, pmpaddr, pmpcfg)
from dv.auto_dv.tests.gen_programs.gen_pmp_csr_warl_prog import (  # noqa: E402
    A_NA4, A_NAMES, A_NAPOT, A_OFF, A_TOR, CSR_MSECCFG, FILLER_REGS, MSECCFG_MML, MSECCFG_RLB, NUM_CFG_CSRS,
    NUM_REGIONS, PH_POOL, PH_TEXT_END, SAFE_MAX_WORD, UIMM_FORMS, WINDOW_LO_WORD, Plan, PmpModel, Report,
    bases_from_symbols, byte_fields, cfg_byte, check_spike_log, csr_name, is_addr, is_cfg, wchoice)

RNG_TAG = "program:pmp_lock"
RED_RNG_TAG = "red"
ITEMS = ("TP-PMP-013", "TP-PMP-014", "TP-PMP-015", "TP-PMP-016", "TP-PMP-017", "TP-PMP-018", "TP-PMP-019",
         "TP-PMP-020", "TP-PMP-021", "TP-PMP-112")
RED_ITEMS = ITEMS
CODE_ENTRY = 0                    # the MML=1 code rule; pmpaddr0 holds the end of .text from P0 on
TOP_ENTRY = NUM_REGIONS - 1       # TP-PMP-018's entry
# The six L=1 rows storable under MML=0 as (R, W, X): RW=01 rows legalise to W=0 (TP-PMP-004) and are not drawn.
LOCK_ROWS = ((0, 0, 0), (0, 0, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1))
A_MODES = (A_OFF, A_TOR, A_NA4, A_NAPOT)
BB_KINDS = ("addr", "cfg", "rlb")             # TP-PMP-020 second-write kinds
CLR_VARIANTS = ("cfg", "addr")                # TP-PMP-112 adjacent-write variants (C dropped, docstring)
# Layer-1 distributions from the area's W-PMP-4 table (gen_test_plan.md Section 4.4): op class of a PMP CSR write.
W_OP = {"csrrw": 50, "csrrs": 25, "csrrc": 25}
W_MSECCFG_SET = {"csrrw": 40, "csrrs": 40, "csrrsi": 20}
W_MSECCFG_CLR = {"csrrw": 40, "csrrc": 40, "csrrci": 20}
POOL_WORDS = 8
POOL_PATTERN = 0x5A130000         # probe-pool words: pattern | index, distinct and non-degenerate
MSECCFG_STATE_MASK = MSECCFG_MML | MSECCFG_RLB | 2

assert NUM_REGIONS >= 8 and NUM_CFG_CSRS == NUM_REGIONS // 4, "gen_pmp_lock_prog: the entry roles need at least 8 regions"


class Gen:
    def __init__(self, seed, red_target=None, floor=None):
        self.rng = random.Random(f"{int(seed)}:{RNG_TAG}")
        self.m = PmpModel()
        self.plan = Plan(seed=seed, red=red_target is not None, rlb=1)
        self.plan.items = {tp: {} for tp in ITEMS}
        self.plan.items["setup"] = {}
        self.plan.items["tail"] = {"drawn": False}
        self.main = []
        self.aux = []
        self.in_main = True
        # pmpaddr entries holding a layout-relative value ('pool'|'text_end', byte offset, or-mask)
        self.addr_rel = [None] * NUM_REGIONS
        self.red_target = red_target
        self.red_sites = {tp: 0 for tp in ITEMS}    # deviation-eligible sites seen per item
        self.floor = floor
        self.locks = []                              # (report idx, entry, legalised byte) of every lock-setting write
        self.row_pool = []

    # --- emission -----------------------------------------------------------------------------------------------
    def emit(self, line):
        (self.main if self.in_main else self.aux).append(line)
        text = line.strip()
        if self.in_main and text and not text.startswith((".", "#")) and not text.endswith(":"):
            self.plan.min_retired += 1

    def li(self, reg, value):
        self.emit(f"  li   {reg}, 0x{value & 0xFFFFFFFF:08x}")

    def report_reg(self, reg, item, label, kind, value):
        self.emit(f"  sw   {reg}, 0(s0)")
        r = Report(item, label, kind, value, len(self.plan.reports))
        self.plan.reports.append(r)
        return r.idx

    def filler(self, n):
        for _ in range(n):
            rd, rs = self.rng.choice(FILLER_REGS), self.rng.choice(FILLER_REGS)
            kind = self.rng.choice(["addi", "xori", "andi", "ori", "slli", "srli", "add", "sub", "xor", "or", "and"])
            if kind in ("addi", "xori", "andi", "ori"):
                self.emit(f"  {kind} {rd}, {rs}, {self.rng.randint(-2048, 2047)}")
            elif kind in ("slli", "srli"):
                self.emit(f"  {kind} {rd}, {rs}, {self.rng.randint(0, 31)}")
            else:
                self.emit(f"  {kind}  {rd}, {rs}, {self.rng.choice(FILLER_REGS)}")

    def rand_filler(self, n_max=3):
        self.filler(self.rng.randint(0, n_max))

    # --- red fixture mechanics ----------------------------------------------------------------------------------
    def site(self, item):
        """Count one deviation-eligible site of an item; True when this site is the red target."""
        serial, self.red_sites[item] = self.red_sites[item], self.red_sites[item] + 1
        return self.red_target == (item, serial)

    def restore(self, csr):
        """Write the planned value back after a red deviation (no report): later expectations stay green."""
        e = csr - PMPADDR_BASE if is_addr(csr) else None
        if e is not None and self.addr_rel[e] is not None:
            self.load_rel("t0", self.addr_rel[e])
        else:
            self.li("t0", self.m.read(csr))
        self.emit(f"  csrw {csr_name(csr)}, t0")

    def load_rel(self, reg, rel):
        base, off, mask = rel
        self.emit(f"  la   {reg}, {'gen_probe_pool' if base == 'pool' else 'gen_text_end'}")
        if off:
            self.emit(f"  addi {reg}, {reg}, {off}")
        self.emit(f"  srli {reg}, {reg}, 2")
        if mask:
            self.emit(f"  ori  {reg}, {reg}, 0x{mask:x}")

    # --- one CSR op ---------------------------------------------------------------------------------------------
    def csr_op(self, form, csr, operand, item, label, skip=False):
        """One CSR op (model update, program op, csrr read-back reported); returns (report idx, pre-write value).
        skip=True is the red deviation: the write is replaced by a read of the same CSR, the count is unchanged."""
        e = csr - PMPADDR_BASE if is_addr(csr) else None
        if e is not None and self.m.addr_writable(e):
            assert form == "csrrw" or self.addr_rel[e] is None, f"RMW on layout-relative pmpaddr{e}"
            if form == "csrrw":
                self.addr_rel[e] = None
        pre = self.m.read(csr)
        self.m.op(form, csr, operand)
        name = csr_name(csr)
        if form in UIMM_FORMS:
            assert 0 <= operand <= 31, "uimm form needs a 5-bit operand"
            self.emit(f"  csrr t1, {name}" if skip else f"  {form} t1, {name}, {operand}")
        else:
            self.li("t0", operand)
            self.emit(f"  csrr t1, {name}" if skip else f"  {form} t1, {name}, t0")
        self.emit(f"  csrr t1, {name}")
        if e is not None and self.addr_rel[e] is not None:
            idx = self.report_reg("t1", item, f"{label} readback {name}", "rel", self.addr_rel[e])
        else:
            idx = self.report_reg("t1", item, f"{label} readback {name}", "abs", self.m.read(csr))
        return idx, pre

    def cfg_word_with(self, n, lane, b):
        v = self.m.read_cfg(n)
        return (v & ~(0xFF << (8 * lane))) | (b << (8 * lane))

    def window_word(self):
        return self.rng.randint(WINDOW_LO_WORD, SAFE_MAX_WORD)

    def window_napot(self):
        ones = self.rng.choice([0, 1, 2, 3, 5, 8, 12, 17, 22, 27])
        base = WINDOW_LO_WORD | (self.rng.randrange(0, 1 << (28 - ones)) << ones)
        v = base | ((1 << ones) - 1)
        return v if v <= SAFE_MAX_WORD else base

    def in_window(self, e):
        return self.addr_rel[e] is None and self.m.addr[e] <= SAFE_MAX_WORD

    def locked(self, e):
        return bool((self.m.cfg[e] >> 7) & 1)

    def mode(self, e):
        return (self.m.cfg[e] >> 3) & 3

    def next_row(self):
        """(R, W, X) of the next lock-setting write: the six storable rows first (shuffled), then random."""
        if not self.row_pool:
            self.row_pool = list(LOCK_ROWS)
            self.rng.shuffle(self.row_pool)
        return self.row_pool.pop()

    def rmw_addr_operand(self, form, e):
        """An operand that changes pmpaddr(e) through the given form (for a write the plan says lands)."""
        old = self.m.addr[e]
        if form == "csrrw":
            v = self.rng.getrandbits(32)
            return v if v != old else v ^ 1
        if form == "csrrs":
            clear = [b for b in range(32) if not (old >> b) & 1] or [0]
            return (self.rng.getrandbits(32) & ~old & 0xFFFFFFFF) | (1 << self.rng.choice(clear))
        setb = [b for b in range(32) if (old >> b) & 1] or [0]
        return (self.rng.getrandbits(32) & old) | (1 << self.rng.choice(setb))

    def addr_write(self, form, e, item, label, must_change=False, skip=False):
        """One pmpaddr(e) write of the given op class; must_change makes the operand change the value (csrrw when the RMW
        form cannot, e.g. csrrc on zero). Returns (report idx, pre-write value, form used)."""
        operand = self.rmw_addr_operand(form, e)
        if must_change and self.m.combined(form, pmpaddr(e), operand) == self.m.addr[e]:
            form, operand = "csrrw", self.rng.getrandbits(32)
            if operand == self.m.addr[e]:
                operand ^= 1
        idx, pre = self.csr_op(form, pmpaddr(e), operand, item, f"{label} {form}", skip=skip)
        return idx, pre, form

    # --- lock-setting writes -------------------------------------------------------------------------------------
    def lock_entry(self, e, a, item, label, form=None, skip=False):
        """Lock entry e (L=1, A=a, an RWX row from the six-row pool) with the safety rule: an active locked region
        lies below the program window, else the mode falls back to OFF. Returns (report idx, pre-write word, byte)."""
        assert not self.locked(e) or self.m.rlb, f"entry {e} is already locked"
        if a != A_OFF and not self.in_window(e):
            if self.m.addr_writable(e):
                v = self.window_napot() if a == A_NAPOT else self.window_word()
                self.csr_op("csrrw", pmpaddr(e), v, item, f"{label} pre-lock pmpaddr{e}")
            else:
                a = A_OFF
        r, w, x = self.next_row()
        b = cfg_byte(1, a, x, w, r)
        n, lane = divmod(e, 4)
        form = form or ("csrrs" if self.m.cfg[e] == 0 and self.rng.random() < 0.4 else "csrrw")
        operand = self.cfg_word_with(n, lane, b) if form == "csrrw" else (b << (8 * lane))
        idx, pre = self.csr_op(form, pmpcfg(n), operand, item, f"{label} lock e{e} {A_NAMES[a]} {form}", skip=skip)
        if not skip:
            assert self.m.cfg[e] == b, f"lock of entry {e} did not take in the model"
        self.locks.append((idx, e, b))
        return idx, pre, b

    def rewrite_locked_cfg(self, e, item, label, form=None, skip=False):
        """Write the word of a locked entry with a different byte for e (L cleared or A/RWX changed), unlocked lanes kept."""
        n, lane = divmod(e, 4)
        cur = self.m.cfg[e]
        while True:
            l = self.rng.randrange(2)
            a = self.rng.choice(A_MODES) if (l == 0 or self.in_window(e)) else A_OFF
            r, w, x = self.rng.choice(LOCK_ROWS) if l else (self.rng.randrange(2), self.rng.randrange(2), self.rng.randrange(2))
            b = cfg_byte(l, a, x, w, r)
            if self.m.legalise_byte(b) != cur:
                break
        form = form or wchoice(self.rng, W_OP)
        if form == "csrrw":
            operand = self.cfg_word_with(n, lane, b)
        elif form == "csrrs":
            operand = (b & ~cur & 0xFF) << (8 * lane)
            if operand == 0:
                form, operand = "csrrw", self.cfg_word_with(n, lane, b)
        else:
            operand = (cur & ~b & 0xFF) << (8 * lane)
            if operand == 0:
                form, operand = "csrrw", self.cfg_word_with(n, lane, b)
        return self.csr_op(form, pmpcfg(n), operand, item, f"{label} {form}", skip=skip) + (form,)

    # --- P0 -------------------------------------------------------------------------------------------------------
    def p0_setup(self):
        self.emit("  la   t0, gen_trap_vec")
        self.emit("  csrw mtvec, t0")
        self.emit("  li   s0, GEN_MM_EOT_ADDR")
        self.emit("  la   s1, gen_probe_pool")
        self.plan.items["setup"]["pool"] = self.report_reg("s1", "setup", "probe pool base", "base", "pool")
        self.emit("  la   t4, gen_text_end")
        self.plan.items["setup"]["text_end"] = self.report_reg("t4", "setup", "end of .text", "base", "text_end")
        # Entry 0 cleared first (csrw, no rd) so a PMP-unaware reference reset (Spike: pmpcfg0 NAPOT RWX) cannot leak.
        self.emit("  csrw pmpcfg0, zero")
        self.emit("  csrr t1, pmpcfg0")
        self.report_reg("t1", "setup", "entry 0 cleared: pmpcfg0", "abs", 0)
        self.load_rel("t0", ("text_end", 0, 0))
        self.emit("  csrw pmpaddr0, t0")
        self.m.write_addr(CODE_ENTRY, PH_TEXT_END >> 2)
        self.addr_rel[CODE_ENTRY] = ("text_end", 0, 0)
        self.emit("  csrr t1, pmpaddr0")
        self.report_reg("t1", "setup", "pmpaddr0 = end of .text", "rel", self.addr_rel[CODE_ENTRY])
        self.emit("  csrr t1, 0x%03x" % CSR_MSECCFG)
        self.report_reg("t1", "setup", "mseccfg reset", "abs", 0)

    # --- P1: TP-PMP-021 (RLB = 1) -----------------------------------------------------------------------------------
    def p1_rlb_phase(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-021"]
        meta.update({"rlb_idx": [], "lock_writes": [], "rewrites": [], "tor_below": [], "post_clear": []})
        form = wchoice(rng, W_MSECCFG_SET)
        idx, _pre = self.csr_op(form, CSR_MSECCFG, MSECCFG_RLB, "TP-PMP-021", f"set RLB {form}")
        meta["rlb_idx"].append(idx)
        assert self.m.rlb == 1
        s_entries = list(self.roles["rlb_set"])
        tor = self.roles["rlb_tor"]
        j = tor - 1
        for e in s_entries:
            a = A_TOR if e == tor else rng.choice(A_MODES)
            idx, pre, _b = self.lock_entry(e, a, "TP-PMP-021", "rlb1")
            meta["lock_writes"].append((idx, e, pre))
            self.rand_filler(2)
        assert self.mode(tor) == A_TOR and not self.locked(j)
        self.tor_below_write(j, tor, meta)
        # rewrites of locked state under RLB=1: every one lands
        rounds = rng.randint(1, 2)
        for _ in range(rounds):
            for e in rng.sample(s_entries, len(s_entries)):
                if self.locked(e) and rng.random() < 0.7:
                    skip = self.site("TP-PMP-021")
                    idx, pre, _f = self.rewrite_locked_cfg(e, "TP-PMP-021", "rlb1 rewrite cfg", skip=skip)
                    if skip:
                        self.plan.red_note = f"TP-PMP-021: the pmpcfg{e // 4} rewrite of locked entry {e} under RLB=1 is replaced by a read (idx {idx})"
                        self.restore(pmpcfg(e // 4))
                    meta["rewrites"].append((idx, e, "cfg", pre))
                    self.rand_filler(2)
                if self.locked(e):
                    skip = self.site("TP-PMP-021")
                    if self.mode(e) == A_OFF:
                        idx, pre, _f = self.addr_write(wchoice(rng, W_OP), e, "TP-PMP-021", "rlb1 rewrite addr", must_change=True, skip=skip)
                    else:
                        v = self.window_napot() if self.mode(e) == A_NAPOT else self.window_word()
                        if v == self.m.addr[e]:
                            v ^= 1
                        idx, pre = self.csr_op("csrrw", pmpaddr(e), v, "TP-PMP-021", "rlb1 rewrite addr csrrw", skip=skip)
                    if skip:
                        self.plan.red_note = f"TP-PMP-021: the pmpaddr{e} write of locked entry {e} under RLB=1 is replaced by a read (idx {idx})"
                        self.restore(pmpaddr(e))
                    meta["rewrites"].append((idx, e, "addr", pre))
            if self.locked(tor) and self.mode(tor) == A_TOR:
                self.tor_below_write(j, tor, meta)
            idx, _pre = self.csr_op("csrrsi", CSR_MSECCFG, 0, "TP-PMP-021", "mseccfg read (csrrsi 0)")
            meta["rlb_idx"].append(idx)
        # normalise for the clear: the kept locks become A=OFF, the others are released (L cleared)
        for e in rng.sample(s_entries, len(s_entries)):
            n, lane = divmod(e, 4)
            if e in self.roles["clear"]:
                r, w, x = rng.choice(LOCK_ROWS)
                b = cfg_byte(1, A_OFF, x, w, r)
            else:
                b = cfg_byte(0, rng.choice(A_MODES), rng.randrange(2), rng.randrange(2), rng.randrange(2))
            while self.m.legalise_byte(b) == self.m.cfg[e]:
                b ^= 1 << rng.choice([0, 2])
            idx, pre = self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, lane, b), "TP-PMP-021", f"rlb1 normalise e{e} {'keep OFF' if e in self.roles['clear'] else 'release'}")
            meta["rewrites"].append((idx, e, "cfg", pre))
        assert all(self.locked(e) and self.mode(e) == A_OFF for e in self.roles["clear"])
        assert all(not self.locked(e) for e in range(NUM_REGIONS) if e not in self.roles["clear"])

    def tor_below_write(self, j, tor, meta):
        """pmpaddr(j) below the locked TOR entry under RLB=1: the write lands (a TP-PMP-021 red site)."""
        skip = self.site("TP-PMP-021")
        idx, pre, _f = self.addr_write(wchoice(self.rng, W_OP), j, "TP-PMP-021", f"rlb1 pmpaddr{j} below locked TOR", must_change=True, skip=skip)
        if skip:
            self.plan.red_note = f"TP-PMP-021: the pmpaddr{j} write below the locked TOR entry {tor} under RLB=1 is replaced by a read (idx {idx})"
            self.restore(pmpaddr(j))
        meta["tor_below"].append((idx, j, pre))

    # --- P2: TP-PMP-112 (the one RLB clear) ----------------------------------------------------------------------
    def p2_rlb_clear(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-112"]
        variant = rng.choice(CLR_VARIANTS)
        e = rng.choice(self.roles["clear"])
        n, lane = divmod(e, 4)
        form = wchoice(rng, W_MSECCFG_CLR)
        operand = {"csrrw": self.m.read(CSR_MSECCFG) & ~MSECCFG_RLB & 0xFFFFFFFF, "csrrc": MSECCFG_RLB | (rng.getrandbits(32) & ~MSECCFG_STATE_MASK & 0xFFFFFFFF),
                   "csrrci": MSECCFG_RLB}[form]
        skip = self.site("TP-PMP-112")
        # the clear and the adjacent write: no read-back in between (adjacent rvfi_order)
        pre_ms = self.m.read(CSR_MSECCFG)
        self.m.op(form, CSR_MSECCFG, operand)
        ms_name = csr_name(CSR_MSECCFG)
        if form in UIMM_FORMS:
            self.emit(f"  csrr t2, {ms_name}" if skip else f"  {form} t2, {ms_name}, {operand}")
        else:
            self.li("t3", operand)
            self.emit(f"  csrr t2, {ms_name}" if skip else f"  {form} t2, {ms_name}, t3")
        assert self.m.rlb == 0 and pre_ms & MSECCFG_RLB
        if variant == "cfg":
            cur = self.m.cfg[e]
            b = cfg_byte(0, rng.choice(A_MODES), rng.randrange(2), rng.randrange(2), rng.randrange(2))
            if self.m.legalise_byte(b) == cur:
                b ^= 4
            csr, wdata, pre = pmpcfg(n), self.cfg_word_with(n, lane, b), self.m.read_cfg(n)
        else:
            csr, wdata, pre = pmpaddr(e), self.rng.getrandbits(32), self.m.addr[e]
            if wdata == pre:
                wdata ^= 1
        self.li("t0", wdata)
        self.emit(f"  csrw {csr_name(csr)}, t0")
        self.m.write(csr, wdata)
        self.emit(f"  csrr t2, {ms_name}")
        meta["clear_idx"] = self.report_reg("t2", "TP-PMP-112", f"mseccfg after RLB clear {form}", "abs", self.m.read(CSR_MSECCFG))
        self.emit(f"  csrr t1, {csr_name(csr)}")
        meta["adj_idx"] = self.report_reg("t1", "TP-PMP-112", f"adjacent {variant} write to locked e{e} (gap 0)", "abs", self.m.read(csr))
        if skip:
            self.plan.red_note = f"TP-PMP-112: the RLB clear is replaced by a read, so the adjacent {variant} write to locked entry {e} lands (idx {meta['adj_idx']})"
            self.restore(csr)
            self.li("t0", 0)
            self.emit(f"  csrw {ms_name}, t0")
        meta.update({"variant": variant, "entry": e, "gap": 0, "adj_pre": pre, "clear_form": form, "late": [], "rlb_attempt_idx": None})
        # locked writes after 1..3 fillers: still ignored
        for g in rng.sample([1, 2, 3], rng.randint(1, 3)):
            self.filler(g)
            e2 = rng.choice(self.roles["clear"])
            n2, lane2 = divmod(e2, 4)
            if rng.random() < 0.5:
                b = cfg_byte(rng.randrange(2), rng.choice(A_MODES), rng.randrange(2), rng.randrange(2), rng.randrange(2))
                idx, pre2 = self.csr_op("csrrw", pmpcfg(n2), self.cfg_word_with(n2, lane2, b), "TP-PMP-112", f"gap {g} cfg write to locked e{e2}")
                meta["late"].append((idx, pmpcfg(n2), pre2, g))
            else:
                idx, pre2, _f = self.addr_write(wchoice(rng, W_OP), e2, "TP-PMP-112", f"gap {g} addr write to locked e{e2}")
                meta["late"].append((idx, pmpaddr(e2), pre2, g))
        # TP-PMP-021: a repeated write after the clear is ignored
        m21 = self.plan.items["TP-PMP-021"]
        e3 = rng.choice(self.roles["clear"])
        n3, lane3 = divmod(e3, 4)
        b = cfg_byte(0, rng.choice(A_MODES), 1, 1, 1)
        idx, pre3 = self.csr_op("csrrw", pmpcfg(n3), self.cfg_word_with(n3, lane3, b), "TP-PMP-021", f"after RLB clear: repeated write to locked e{e3}")
        m21["post_clear"].append((idx, pmpcfg(n3), pre3))
        idx, _p = self.csr_op("csrrsi", CSR_MSECCFG, 0, "TP-PMP-021", "mseccfg after clear (csrrsi 0)")
        m21["rlb_idx"].append(idx)

    # --- P3 / P8: TP-PMP-013 ----------------------------------------------------------------------------------------
    def lockmix_write(self, n, form, label):
        """One csrrw/csrrs/csrrc to pmpcfgN: locked lanes get an attempt to clear L or change A/RWX, unlocked lanes
        random L=0 data; the read-back keeps the locked lanes and updates the unlocked ones."""
        meta = self.plan.items["TP-PMP-013"]
        lanes = [4 * n + i for i in range(4)]
        locked = [e for e in lanes if self.locked(e)]
        pre = self.m.read_cfg(n)
        operand = 0
        for i, e in enumerate(lanes):
            cur = self.m.cfg[e]
            if form == "csrrw":
                b = cfg_byte(0, self.rng.choice(A_MODES), self.rng.randrange(2), self.rng.randrange(2), self.rng.randrange(2))
                if e in locked and self.rng.random() < 0.5:
                    b |= 0x80                                  # keep L but change A/RWX
                if self.m.legalise_byte(b) == cur:
                    b ^= 4
                operand |= b << (8 * i)
            elif form == "csrrs":
                clear_bits = [bit for bit in (0, 1, 2, 3, 4) if not (cur >> bit) & 1]
                mask = 0
                for bit in clear_bits:
                    if self.rng.random() < 0.5:
                        mask |= 1 << bit
                if not mask and clear_bits:
                    mask = 1 << self.rng.choice(clear_bits)
                operand |= mask << (8 * i)
            else:
                set_bits = [bit for bit in (0, 1, 2, 3, 4, 7) if (cur >> bit) & 1]
                mask = 0
                for bit in set_bits:
                    if self.rng.random() < 0.5:
                        mask |= 1 << bit
                if not mask and set_bits:
                    mask = 1 << self.rng.choice(set_bits)
                operand |= mask << (8 * i)
        comb = self.m.combined(form, pmpcfg(n), operand)
        changed = [e for e in lanes if e not in locked and self.m.legalise_byte((comb >> (8 * (e % 4))) & 0xFF) != self.m.cfg[e]]
        if not changed and len(locked) < 4:
            e = self.rng.choice([e for e in lanes if e not in locked])
            i = e % 4
            if form == "csrrw":
                operand = (operand & ~(0xFF << (8 * i))) | (((self.m.cfg[e] ^ 4) & 0x7F) << (8 * i))
            elif form == "csrrs":
                clear_bits = [bit for bit in (0, 1, 2, 3, 4) if not (self.m.cfg[e] >> bit) & 1]
                operand |= (1 << self.rng.choice(clear_bits)) << (8 * i) if clear_bits else 0
            else:
                set_bits = [bit for bit in (0, 1, 2, 3, 4) if (self.m.cfg[e] >> bit) & 1]
                operand |= (1 << self.rng.choice(set_bits)) << (8 * i) if set_bits else 0
        mix = "all" if len(locked) == 4 else ("none" if not locked else "some")
        skip = self.site("TP-PMP-013")
        idx, pre = self.csr_op(form, pmpcfg(n), operand, "TP-PMP-013", f"{label} {mix} {form}", skip=skip)
        if skip:
            self.plan.red_note = f"TP-PMP-013: the {form} to pmpcfg{n} ({mix} lock mix) is replaced by a read (idx {idx})"
            self.restore(pmpcfg(n))
        meta.setdefault("writes", []).append((idx, n, form, mix, [e % 4 for e in locked], pre))
        return idx

    def p3_none_write(self):
        form = wchoice(self.rng, W_OP)
        assert not any(self.locked(e) for e in range(4))
        self.lockmix_write(0, form, "P3 word 0")

    # --- P4: TP-PMP-019 -----------------------------------------------------------------------------------------------
    def p4_off_lock(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-019"]
        e = self.roles["off_lock"]
        n, lane = divmod(e, 4)
        assert all(self.mode(x) == A_OFF for x in range(NUM_REGIONS) if self.locked(x)), "TP-PMP-019 needs only A=OFF locks"
        word = rng.randrange(POOL_WORDS)
        off = 4 * word
        self.load_rel("t0", ("pool", off, 0))
        self.emit(f"  csrw pmpaddr{e}, t0")
        self.m.write_addr(e, (PH_POOL + off) >> 2)
        self.addr_rel[e] = ("pool", off, 0)
        self.emit(f"  csrr t1, pmpaddr{e}")
        meta["addr_setup_idx"] = self.report_reg("t1", "TP-PMP-019", f"pmpaddr{e} = pool word {word}", "rel", self.addr_rel[e])
        skip = self.site("TP-PMP-019")
        idx, pre, b = self.lock_entry(e, A_OFF, "TP-PMP-019", "L=1 A=OFF", skip=skip)
        meta.update({"entry": e, "lock_idx": idx, "lock_pre": pre, "lock_byte": b, "pool_word": word, "rewrites": []})
        if skip:
            self.plan.red_note = f"TP-PMP-019: the L=1/A=OFF lock write of entry {e} is replaced by a read (idx {idx}); the rewrites land"
        self.rand_filler(2)
        # rewrite attempts (L=0 data: an attempt to unlock or change A/RWX) and a pmpaddr write: both ignored
        for kind in rng.sample(["cfg", "addr", "cfg", "addr"], rng.randint(2, 4)):
            if kind == "cfg":
                bb = cfg_byte(0, rng.choice(A_MODES), rng.randrange(2), rng.randrange(2), rng.randrange(2))
                form = wchoice(rng, W_OP)
                if form == "csrrw":
                    operand = self.cfg_word_with(n, lane, bb)
                elif form == "csrrs":
                    operand = ((bb & ~self.m.cfg[e]) & 0x7F or 0x40) << (8 * lane)
                else:
                    operand = ((self.m.cfg[e] & 0x9F) or 0x80) << (8 * lane)
                idx2, pre2 = self.csr_op(form, pmpcfg(n), operand, "TP-PMP-019", f"rewrite locked-OFF cfg {form}")
                meta["rewrites"].append((idx2, pmpcfg(n), pre2))
            else:
                idx2, pre2, _f = self.addr_write(wchoice(rng, W_OP), e, "TP-PMP-019", "write locked-OFF pmpaddr")
                meta["rewrites"].append((idx2, pmpaddr(e), pre2))
            self.rand_filler(1)
        if skip:
            self.restore(pmpaddr(e))
            self.restore(pmpcfg(n))
        form = rng.choice(["csrrs", "csrrsi"])
        idx3, _p = self.csr_op(form, CSR_MSECCFG, MSECCFG_RLB, "TP-PMP-019", f"RLB set attempt with A=OFF locks only {form}")
        meta["mseccfg_idx"] = idx3
        assert self.m.rlb == 0
        # M-mode load probe of the locked OFF entry's word: an OFF entry decides nothing, the load lands
        self.emit(f"  lw   t1, {off}(s1)")
        meta["probe_idx"] = self.report_reg("t1", "TP-PMP-019", f"M-mode load of pool word {word}", "abs", POOL_PATTERN | word)

    # --- P5: TP-PMP-020 -----------------------------------------------------------------------------------------------
    def p5_back_to_back(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-020"]
        meta["episodes"] = []
        entries = sorted(self.roles["bb"])            # increasing: a TOR lock never freezes a later episode's pmpaddr
        kinds = list(BB_KINDS)
        rng.shuffle(kinds)
        modes = [A_NA4, A_NAPOT, rng.choice(A_MODES)]
        rng.shuffle(modes)
        while len(kinds) < len(entries):
            kinds.append(rng.choice(BB_KINDS))
            modes.append(rng.choice(A_MODES))
        gaps = [0, 0, 0] + [rng.choice([rng.randint(1, 3), rng.randint(4, 8)]) for _ in entries[3:]]
        for e, kind, a, gap in zip(entries, kinds, modes, gaps):
            n, lane = divmod(e, 4)
            if a != A_OFF and not self.in_window(e):
                self.csr_op("csrrw", pmpaddr(e), self.window_napot() if a == A_NAPOT else self.window_word(), "TP-PMP-020", f"e{e} pre-lock pmpaddr")
            skip = self.site("TP-PMP-020")
            # the lock-setting write and the second write are adjacent (gap 0) or separated by fillers only
            r, w, x = self.next_row()
            b = cfg_byte(1, a, x, w, r)
            word = self.cfg_word_with(n, lane, b)
            pre_word = self.m.read_cfg(n)
            self.m.write_cfg(n, word)
            assert self.m.cfg[e] == b
            self.li("t0", word)
            self.emit(f"  csrr t1, pmpcfg{n}" if skip else f"  csrw pmpcfg{n}, t0")
            self.filler(gap)
            if kind == "addr":
                csr, wdata = pmpaddr(e), rng.getrandbits(32)
                if wdata == self.m.addr[e]:
                    wdata ^= 1
            elif kind == "cfg":
                b2 = cfg_byte(0, rng.choice(A_MODES), rng.randrange(2), rng.randrange(2), rng.randrange(2))
                if self.m.legalise_byte(b2) == b:
                    b2 ^= 4
                csr, wdata = pmpcfg(n), self.cfg_word_with(n, lane, b2)
            else:
                csr, wdata = CSR_MSECCFG, MSECCFG_RLB
            pre2 = self.m.read(csr)
            self.m.write(csr, wdata)
            self.li("t0", wdata)
            self.emit(f"  csrw {csr_name(csr)}, t0")
            self.emit(f"  csrr t1, pmpcfg{n}")
            lock_idx = self.report_reg("t1", "TP-PMP-020", f"e{e} lock write {A_NAMES[a]} row {r}{w}{x} readback pmpcfg{n}", "abs", self.m.read_cfg(n))
            self.locks.append((lock_idx, e, b))
            self.emit(f"  csrr t1, {csr_name(csr)}")
            second_idx = self.report_reg("t1", "TP-PMP-020", f"e{e} second write {kind} gap {gap} readback {csr_name(csr)}", "abs", self.m.read(csr))
            if skip:
                self.plan.red_note = f"TP-PMP-020: the lock-setting write of entry {e} ({kind} episode) is replaced by a read (idx {lock_idx}); the second write lands"
                if kind == "addr":
                    self.restore(pmpaddr(e))
                self.restore(pmpcfg(n))
            meta["episodes"].append({"entry": e, "kind": kind, "gap": gap, "lock_idx": lock_idx, "second_idx": second_idx,
                                     "pre_word": pre_word, "pre_second": pre2, "row": (r, w, x), "lane": lane})
            self.rand_filler(2)

    # --- P6: TP-PMP-015 / 016 / 017 / 018 -------------------------------------------------------------------------------
    def p6_tor_lock(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-015"]
        t = self.roles["tor_lock"]
        i = t - 1
        assert not self.locked(i) and not self.locked(t) and self.m.addr_writable(i)
        skip = self.site("TP-PMP-015")
        idx, pre, b = self.lock_entry(t, A_TOR, "TP-PMP-015", f"lock TOR e{t}", skip=skip)
        meta.update({"pair": (i, t), "lock_idx": idx, "lock_byte": b, "addr_writes": [], "cfg_i": None})
        if skip:
            self.plan.red_note = f"TP-PMP-015: the TOR lock write of entry {t} is replaced by a read (idx {idx}); the pmpaddr{i} writes land"
        forms = ["csrrw", "csrrs", "csrrc"]
        rng.shuffle(forms)
        for form in forms + [wchoice(rng, W_OP) for _ in range(rng.randint(0, 2))]:
            idx2, pre2, _f = self.addr_write(form, i, "TP-PMP-015", f"pmpaddr{i} below locked TOR")
            meta["addr_writes"].append((idx2, form, pre2))
            self.rand_filler(1)
        if skip:
            self.restore(pmpaddr(i))
            self.restore(pmpcfg(t // 4))
        n, lane = divmod(i, 4)
        b2 = cfg_byte(0, rng.choice(A_MODES), rng.randrange(2), rng.randrange(2), rng.randrange(2))
        if self.m.legalise_byte(b2) == self.m.cfg[i]:
            b2 ^= 4
        idx3, pre3 = self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, lane, b2), "TP-PMP-015", f"pmpcfg{n} entry {i} stays writable")
        meta["cfg_i"] = (idx3, lane, (pre3 >> (8 * lane)) & 0xFF)

    def p6_nontor_neighbour(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-016"]
        meta["pairs"] = []
        cands = [e for e in range(2, NUM_REGIONS) if self.locked(e) and self.mode(e) != A_TOR and not self.locked(e - 1) and self.m.addr_writable(e - 1)]
        assert self.roles["ntor"] in cands, "TP-PMP-016: the reserved locked non-TOR neighbour is not available"
        picks = [self.roles["ntor"]] + rng.sample([e for e in cands if e != self.roles["ntor"]], min(len(cands) - 1, rng.randint(0, 2)))
        for e in picks:
            i = e - 1
            n_e, lane_e = divmod(e, 4)
            self.emit(f"  csrr t1, pmpcfg{n_e}")
            cfg_idx = self.report_reg("t1", "TP-PMP-016", f"pmpcfg{n_e} shows e{e} locked {A_NAMES[self.mode(e)]}", "abs", self.m.read_cfg(n_e))
            for form in rng.sample(["csrrw", "csrrs", "csrrc"], rng.randint(1, 3)):
                skip = self.site("TP-PMP-016")
                idx, pre, form = self.addr_write(form, i, "TP-PMP-016", f"pmpaddr{i} under locked non-TOR e{e}", must_change=True, skip=skip)
                if skip:
                    self.plan.red_note = f"TP-PMP-016: the pmpaddr{i} write (entry {e} locked {A_NAMES[self.mode(e)]}) is replaced by a read (idx {idx})"
                    self.restore(pmpaddr(i))
                meta["pairs"].append((idx, i, e, self.mode(e), lane_e, cfg_idx, pre))
            self.rand_filler(1)

    def p6_unlocked_tor(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-017"]
        meta["pairs"] = []
        cands = [e for e in range(2, NUM_REGIONS - 1) if not self.locked(e) and not self.locked(e - 1) and self.m.addr_writable(e - 1)
                 and e - 1 != CODE_ENTRY and e != self.roles["utor"]]
        assert not self.locked(self.roles["utor"]) and not self.locked(self.roles["utor"] - 1), "TP-PMP-017: the reserved pair is locked"
        for e in [self.roles["utor"]] + rng.sample(cands, min(len(cands), rng.randint(0, 1))):
            i = e - 1
            n_e, lane_e = divmod(e, 4)
            b = cfg_byte(0, A_TOR, rng.randrange(2), rng.randrange(2), rng.randrange(2))
            cfg_idx, _p = self.csr_op("csrrw", pmpcfg(n_e), self.cfg_word_with(n_e, lane_e, b), "TP-PMP-017", f"e{e} unlocked TOR")
            for form in rng.sample(["csrrw", "csrrs", "csrrc"], rng.randint(1, 3)):
                skip = self.site("TP-PMP-017")
                idx, pre, form = self.addr_write(form, i, "TP-PMP-017", f"pmpaddr{i} under unlocked TOR e{e}", must_change=True, skip=skip)
                if skip:
                    self.plan.red_note = f"TP-PMP-017: the pmpaddr{i} write (entry {e} unlocked TOR) is replaced by a read (idx {idx})"
                    self.restore(pmpaddr(i))
                meta["pairs"].append((idx, i, e, lane_e, cfg_idx, pre))
            self.rand_filler(1)

    def p6_top_entry(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-018"]
        e = TOP_ENTRY
        assert not self.locked(e)
        meta.update({"entry": e, "first": [], "second": []})
        for form in rng.sample(["csrrw", "csrrs", "csrrc"], rng.randint(1, 3)):
            skip = self.site("TP-PMP-018")
            idx, pre, form = self.addr_write(form, e, "TP-PMP-018", f"unlocked pmpaddr{e}", must_change=True, skip=skip)
            if skip:
                self.plan.red_note = f"TP-PMP-018: the unlocked pmpaddr{e} write is replaced by a read (idx {idx})"
                self.restore(pmpaddr(e))
            meta["first"].append((idx, form, pre))
            self.rand_filler(1)
        skip = self.site("TP-PMP-018")
        a = rng.choice(A_MODES)
        idx, pre, b = self.lock_entry(e, a, "TP-PMP-018", "lock top entry", skip=skip)
        meta.update({"lock_idx": idx, "lock_byte": b})
        if skip:
            self.plan.red_note = f"TP-PMP-018: the lock write of entry {e} is replaced by a read (idx {idx}); the second-half writes land"
        for form in rng.sample(["csrrw", "csrrs", "csrrc"], rng.randint(1, 3)):
            idx2, pre2, _f = self.addr_write(form, e, "TP-PMP-018", f"locked pmpaddr{e}")
            meta["second"].append((idx2, form, pre2))
        if skip:
            self.restore(pmpaddr(e))
            self.restore(pmpcfg(e // 4))

    # --- P7: TP-PMP-014 -----------------------------------------------------------------------------------------------
    def p7_locked_addr(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-014"]
        e = self.roles["own_lock"]
        skip = self.site("TP-PMP-014")
        idx, pre, b = self.lock_entry(e, rng.choice(A_MODES), "TP-PMP-014", "own lock", skip=skip)
        meta.update({"own": e, "lock_idx": idx, "writes": []})
        if skip:
            self.plan.red_note = f"TP-PMP-014: the lock write of entry {e} is replaced by a read (idx {idx}); the pmpaddr{e} write lands"
        idx2, pre2, form = self.addr_write(wchoice(rng, W_OP), e, "TP-PMP-014", f"locked pmpaddr{e} {A_NAMES[self.mode(e)]}")
        meta["writes"].append((idx2, e, form, self.mode(e), pre2))
        if skip:
            self.restore(pmpaddr(e))
            self.restore(pmpcfg(e // 4))
        locked = [x for x in range(NUM_REGIONS) if self.locked(x)]
        by_mode = {a: [x for x in locked if self.mode(x) == a] for a in A_MODES}
        assert all(by_mode[a] for a in A_MODES), f"TP-PMP-014 needs a locked entry of every A mode, have {by_mode}"
        picks = [rng.choice(by_mode[a]) for a in A_MODES] + rng.sample(locked, rng.randint(1, 4))
        rng.shuffle(picks)
        for x in picks:
            idx3, pre3, form = self.addr_write(wchoice(rng, W_OP), x, "TP-PMP-014", f"locked pmpaddr{x} {A_NAMES[self.mode(x)]}")
            meta["writes"].append((idx3, x, form, self.mode(x), pre3))
            self.rand_filler(1)

    # --- P8: TP-PMP-013 lock mixes; TP-PMP-112's later RLB attempt ------------------------------------------------------
    def p8_lock_mixes(self):
        rng = self.rng
        w_all = self.roles["all_word"]
        # fill the lock mixes: the chosen word fully locked, every other word with at least one lock (word 0 at most 3)
        for e in [4 * w_all + i for i in range(4)]:
            if not self.locked(e):
                self.lock_entry(e, rng.choice(A_MODES), "TP-PMP-013", f"fill word {w_all}")
        for n in range(NUM_CFG_CSRS):
            lanes = [4 * n + i for i in range(4)]
            if not any(self.locked(e) for e in lanes):
                e = rng.choice([e for e in lanes if e != CODE_ENTRY])
                self.lock_entry(e, rng.choice(A_MODES), "TP-PMP-013", f"fill word {n}")
        assert all(self.locked(e) for e in range(4 * w_all, 4 * w_all + 4)) and not self.locked(CODE_ENTRY)
        some_words = [n for n in range(NUM_CFG_CSRS) if 1 <= sum(self.locked(e) for e in range(4 * n, 4 * n + 4)) <= 3]
        assert 0 in some_words
        forms = ["csrrw", "csrrs", "csrrc"]
        rng.shuffle(forms)
        for form in forms:                                    # every op class on a partially locked word
            self.lockmix_write(rng.choice(some_words), form, "some")
            self.rand_filler(2)
        for form in [wchoice(rng, W_OP) for _ in range(rng.randint(2, 4))]:
            self.lockmix_write(w_all, form, "all")
            self.rand_filler(1)
        for _ in range(rng.randint(2, 6)):
            self.lockmix_write(rng.randrange(NUM_CFG_CSRS), wchoice(rng, W_OP), "mixed")
            self.rand_filler(1)
        # TP-PMP-112: the later RLB set attempt while locked (non-OFF) entries exist reads back 0
        assert any(self.locked(e) and self.mode(e) != A_OFF for e in range(NUM_REGIONS))
        form = rng.choice(["csrrs", "csrrsi", "csrrw"])
        idx, _p = self.csr_op(form, CSR_MSECCFG, MSECCFG_RLB, "TP-PMP-112", f"later RLB set attempt {form}")
        self.plan.items["TP-PMP-112"]["rlb_attempt_idx"] = idx
        assert self.m.rlb == 0

    # --- P9: MML = 1 tail (half of the seeds) -------------------------------------------------------------------------------
    def p9_mml_tail(self):
        rng, meta = self.rng, self.plan.items["tail"]
        meta.update({"drawn": True, "ignored": [], "landed": [], "mml_idx": None, "rlb_idx": None})
        for e in rng.sample(range(NUM_REGIONS), NUM_REGIONS):   # every unlocked entry OFF: an L=0 rule denies M-mode under MML
            if not self.locked(e) and self.m.cfg[e] != 0:
                n, lane = divmod(e, 4)
                self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, lane, 0), "tail", f"clear unlocked e{e}")
        assert self.addr_rel[CODE_ENTRY] == ("text_end", 0, 0) and not self.locked(CODE_ENTRY)
        code_byte = cfg_byte(1, A_TOR, 1, 0, 1)
        idx, _p = self.csr_op("csrrw", pmpcfg(0), self.cfg_word_with(0, 0, code_byte), "tail", "code rule pmpcfg0 L=1 R/X TOR")
        self.locks.append((idx, CODE_ENTRY, code_byte))
        assert self.m.cfg[0] == code_byte
        for e in range(1, NUM_REGIONS):
            assert self.mode(e) == A_OFF or self.in_window(e), f"entry {e} active outside the window before MML"
        form = wchoice(rng, W_MSECCFG_SET)
        meta["mml_idx"], _p = self.csr_op(form, CSR_MSECCFG, MSECCFG_MML, "tail", f"set MML {form}")
        assert self.m.mml == 1 and self.m.rlb == 0
        locked = [e for e in range(NUM_REGIONS) if self.locked(e)]
        for e in rng.sample(locked, min(len(locked), rng.randint(3, 6))):
            n, lane = divmod(e, 4)
            if rng.random() < 0.5:
                b = cfg_byte(rng.randrange(2), rng.choice(A_MODES), rng.randrange(2), rng.randrange(2), rng.randrange(2))
                if self.m.legalise_byte(b) == self.m.cfg[e]:
                    b ^= 1
                idx, pre = self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, lane, b), "tail", f"mml1 write to locked e{e} cfg")
                meta["ignored"].append((idx, pmpcfg(n), pre))
            else:
                idx, pre, _f = self.addr_write(wchoice(rng, W_OP), e, "tail", f"mml1 write to locked pmpaddr{e}")
                meta["ignored"].append((idx, pmpaddr(e), pre))
        # TP-PMP-014 under MML=1: the code rule's pmpaddr0 is locked too
        idx, pre, form = self.addr_write(wchoice(rng, W_OP), 0, "TP-PMP-014", "locked pmpaddr0 under MML=1")
        self.plan.items["TP-PMP-014"]["writes"].append((idx, 0, form, A_TOR, pre))
        # an unlocked entry still takes a non-executable row (in the window)
        free = [e for e in range(1, NUM_REGIONS) if not self.locked(e) and self.m.addr_writable(e)]
        if free:
            e = rng.choice(free)
            n, lane = divmod(e, 4)
            self.csr_op("csrrw", pmpaddr(e), self.window_word(), "tail", f"mml1 unlocked pmpaddr{e}")
            b = cfg_byte(0, rng.choice([A_NA4, A_TOR]), 0, rng.randrange(2), 1)
            idx, pre = self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, lane, b), "tail", f"mml1 unlocked e{e} cfg lands")
            meta["landed"].append((idx, e, lane, b))
            assert self.m.cfg[e] == b
        form = rng.choice(["csrrs", "csrrsi"])
        meta["rlb_idx"], _p = self.csr_op(form, CSR_MSECCFG, MSECCFG_RLB, "tail", f"mml1 RLB attempt {form}")
        assert self.m.rlb == 0 and self.m.mml == 1

    # --- end, handler, data -----------------------------------------------------------------------------------------------
    def p_end(self):
        self.emit(f"  li   gp, {TOHOST_PASS}")
        self.emit("  la   t5, tohost")
        self.emit("  sw   gp, 0(t5)")
        self.emit("1:")
        self.emit("  j    1b")

    def handler(self):
        self.in_main = False
        self.aux += ["", "# M-mode trap handler (mtvec base, 256-byte aligned): the program takes no trap by design, so any trap",
                     f"# stores its mcause / mepc record to the report channel and ends the program with tohost {TOHOST_FAIL}.",
                     ".align 8", "gen_trap_vec:",
                     "  csrr t0, mcause", "  csrr t1, mepc", "  slli t0, t0, 16", "  andi t1, t1, 0x7ff", "  or   t0, t0, t1",
                     "  li   t2, GEN_MM_EOT_ADDR", "  sw   t0, 0(t2)",
                     f"  li   gp, {TOHOST_FAIL}", "  la   t5, tohost", "  sw   gp, 0(t5)", "5:", "  j    5b",
                     "", "# no U-mode code in this group; the label keeps the shared layout symbol set complete",
                     ".align 2", ".globl gen_u_code", "gen_u_code:", ".globl gen_text_end", "gen_text_end:"]

    def data_section(self):
        d = ["", ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
             ".align 6", "# probe pool: distinct patterns; TP-PMP-019's locked OFF entry names one of these words", ".globl gen_probe_pool", "gen_probe_pool:"]
        d += [f"  .word 0x{POOL_PATTERN | i:08x}" for i in range(POOL_WORDS)]
        d += [".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {self.plan.min_retired}"]
        return d

    # --- entry roles ---------------------------------------------------------------------------------------------------------
    def assign_roles(self):
        """Entries 1..PMPNumRegions-2 take the lock roles; entry 0 is the code rule, the top entry is TP-PMP-018's.
        The unlocked lower neighbours the TOR items need are reserved (never given a lock role before P8)."""
        rng = self.rng
        pool = list(range(1, TOP_ENTRY))
        rng.shuffle(pool)
        roles = {}
        tor = next(e for e in pool if e >= 4)                     # RLB-phase locks avoid word 0 (the none-mix write)
        pool.remove(tor)
        j = tor - 1                                                # stays unlocked while the RLB TOR is in force
        others = [e for e in pool if e != j and e >= 4][:rng.randint(2, 3)]
        for e in others:
            pool.remove(e)
        roles["rlb_tor"] = tor
        roles["rlb_set"] = rng.sample([tor] + others, len(others) + 1)
        roles["clear"] = rng.sample(roles["rlb_set"], 2)
        pool += [e for e in roles["rlb_set"] if e not in roles["clear"]]   # released entries are free again
        rng.shuffle(pool)

        def protect(e):
            if e in pool:
                pool.remove(e)

        roles["ntor"] = rng.choice(roles["clear"])                 # TP-PMP-016: a locked OFF entry above an unlocked one
        protect(roles["ntor"] - 1)
        cands = [e for e in pool if e >= 2 and (e - 1) in pool]
        roles["utor"] = rng.choice(cands)                          # TP-PMP-017: both entries unlocked
        protect(roles["utor"])
        protect(roles["utor"] - 1)
        unlocked = {roles["ntor"] - 1, roles["utor"], roles["utor"] - 1}
        cands = [e for e in pool if e >= 2 and ((e - 1) in pool or (e - 1) in unlocked)]
        roles["tor_lock"] = rng.choice(cands)                      # TP-PMP-015: locked TOR above an unlocked entry
        protect(roles["tor_lock"])
        protect(roles["tor_lock"] - 1)
        roles["off_lock"] = pool.pop()
        roles["own_lock"] = pool.pop()
        roles["bb"] = [pool.pop() for _ in range(3 + (1 if len(pool) >= 2 and rng.random() < 0.5 else 0))]
        roles["spare"] = pool
        roles["all_word"] = rng.randrange(1, NUM_CFG_CSRS)
        self.roles = roles

    def build(self):
        self.assign_roles()
        self.p0_setup()
        self.p1_rlb_phase()
        self.p2_rlb_clear()
        self.p3_none_write()
        self.p4_off_lock()
        self.p5_back_to_back()
        blocks = [self.p6_tor_lock, self.p6_unlocked_tor, self.p6_top_entry]
        self.rng.shuffle(blocks)
        for blk in blocks:
            blk()
        self.p6_nontor_neighbour()
        self.p7_locked_addr()
        self.p8_lock_mixes()
        if self.rng.random() < 0.5:
            self.p9_mml_tail()
        self.p_end()
        self.handler()
        self.check_coverage()
        assert self.red_target is None or self.plan.red_note, "red fixture: the deviation site was not emitted"
        self.plan.items["TP-PMP-020"]["lock_events"] = list(self.locks)
        self.plan.red_sites = dict(self.red_sites)
        if self.floor is not None:
            assert self.plan.min_retired >= self.floor, "red program retires fewer instructions than the green one"
            self.plan.min_retired = self.floor
        header = ['# gen_pmp_lock: generated per-seed program of gen_test_pmp_lock (seed %d%s).' % (self.plan.seed, ", RED fixture " + self.plan.red_item if self.plan.red else ""),
                  "# Generator: dv/auto_dv/tests/gen_programs/gen_pmp_lock_prog.py (do not edit; regenerate).",
                  '.include "gen_mmio_map.h"', ".section .text", ".globl _start", "_start:"]
        self.plan.lines = header + self.main + self.aux + self.data_section()
        return self.plan

    def check_coverage(self):
        """The per-seed floors the fire-checks assert: the six L=1 rows among the MML=0 lock writes, every A mode among
        TP-PMP-014's locked targets, every lock mix and op class in TP-PMP-013, every second-write kind at gap 0 in TP-PMP-020."""
        rows = {(r, w, x) for (_l, _a, x, w, r) in (byte_fields(b) for _i, _e, b in self.locks)}
        assert set(LOCK_ROWS) <= rows, f"lock rows drawn {sorted(rows)} miss {set(LOCK_ROWS) - rows}"
        assert {a for _i, _e, _f, a, _p in self.plan.items["TP-PMP-014"]["writes"]} == set(A_MODES)
        w13 = self.plan.items["TP-PMP-013"]["writes"]
        assert {m for _i, _n, _f, m, _l, _p in w13} == {"none", "some", "all"}
        assert {f for _i, _n, f, m, _l, _p in w13 if m == "some"} == {"csrrw", "csrrs", "csrrc"}
        eps = self.plan.items["TP-PMP-020"]["episodes"]
        assert {ep["kind"] for ep in eps if ep["gap"] == 0} == set(BB_KINDS)


def plan(seed, red=False, red_item=None):
    """The green plan of a seed, or the red fixture: the same expectations with one program deviation of one item
    (red_item, else drawn with the item's site from random.Random(f"{seed}:red")); the red floor is the green one."""
    green = Gen(seed).build()
    if not red:
        return green
    rng = random.Random(f"{int(seed)}:{RED_RNG_TAG}")
    item = red_item or rng.choice(RED_ITEMS)
    assert item in RED_ITEMS, f"red: unknown item {item}"
    sites = green.red_sites[item]
    assert sites, f"red: no deviation site for {item} at seed {seed}"
    p = Gen(seed, red_target=(item, rng.randrange(sites)), floor=green.min_retired).build()
    p.red_item = item
    assert p.signature() == green.signature() and p.k == green.k and p.min_retired == green.min_retired, "red: the expectations moved"
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
    ap.add_argument("--red-item", choices=RED_ITEMS, help="the item the red fixture targets (default: drawn from the seed)")
    ap.add_argument("--check-spike", type=Path, help="compare the plan with a Spike commit log's EOT stores")
    ap.add_argument("--sym", type=Path, help="prog.sym.json of the built program (layout bases for --check-spike)")
    ap.add_argument("--summary", action="store_true", help="print k, min_retired and the per-item report counts")
    args = ap.parse_args(argv)
    p = plan(args.seed, args.red, args.red_item)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(emit(p))
    if args.summary or not (args.out or args.check_spike):
        per_item = {}
        for r in p.reports:
            per_item[r.item] = per_item.get(r.item, 0) + 1
        print(f"seed={p.seed} red={p.red} k={p.k} min_retired={p.min_retired} lines={len(p.lines)} tail={p.items['tail']['drawn']} per_item={per_item}"
              + f" red_sites={p.red_sites}" + (f" red_item={p.red_item} red_note={p.red_note}" if p.red else ""))
    if args.check_spike:
        import json
        assert args.sym, "--check-spike needs --sym <prog.sym.json>"
        bases = bases_from_symbols(json.loads(args.sym.read_text())["symbols"])
        got, bad = check_spike_log(p, args.check_spike, bases)
        print(f"spike EOT stores: {len(got)} (plan k={p.k}); mismatches: {len(bad)}")
        for i, exp, g in bad[:20]:
            r = p.reports[i]
            print(f"  idx {i} [{r.item} {r.label}] expected 0x{exp:08x} got {g if g is None else '0x%08x' % g}")
        return 1 if bad or len(got) != p.k else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
