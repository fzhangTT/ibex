#!/usr/bin/env python3
"""gen_pmp_csr_warl_prog: per-seed program generator of gen_test_pmp_csr_warl (plan group
gen_pmp_csr_warl, items TP-PMP-001..008 of dv/auto_dv/docs/gen_test_plan.md Section 4.4).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:pmp_csr_warl"),
runs PmpModel (the PMP CSR WARL rules as the specification states them; sources in the class docstring)
and returns a Plan: the assembly lines, the ordered expected report words (the raw csrr read-back after
every write, the rd value of every RMW op, the trap records of the M-mode handler, the probe results), k,
min_retired and per-item metadata for the fire-checks. Layout-relative expectations (pmpaddr values built
from the probe pool, the U code area and the end of .text) resolve from the image's symbol table:
Plan.expected(idx, bases) with bases = bases_from_symbols(<prog.sym.json>["symbols"]); the program also
reports the three addresses so the test checks them against the same table.

Program phases (M-mode unless stated; PMP reset state: every entry OFF, mseccfg 0):
  P0 mtvec, report the three layout addresses, clear entry 0
  P1 MML=0, no lock: TP-PMP-001 (pmpcfg packing), TP-PMP-002 (32-bit pmpaddr), TP-PMP-003 (reserved
     bits), TP-PMP-004 (RW=01 legalised), TP-PMP-007 (RMW forms) in a shuffled order
  P2 U-mode episodes: TP-PMP-008 (PMP CSR access from U traps, no write), TP-PMP-006 (A modes
     written, read back and probed from U at a pool word and its neighbour)
  P3 lock step: mseccfg.RLB drawn, TP-PMP-004 L=1 rows, TP-PMP-007 ops on locked entries
  P4 MML=1: code rule (entry 0, L=1 R/X TOR over [0, end of .text)), then TP-PMP-005 (RW=01 stored),
     TP-PMP-003 and TP-PMP-007 under MML=1. Every LRWX row the draw produces is programmed, LRWX=1111
     under RLB=0 included: smepmp.adoc defines it as a locked shared read-only data region without
     execute privilege, so the write is stored (and locks the entry); a shim that legalises it
     differently shows up as a comparator row, never as a program change.
Safety rule: an entry that can deny M-mode (L=1 under MML=0, any entry under MML=1) only ever holds a
pmpaddr <= SAFE_MAX_WORD, so its region lies below the program window; MMWP is never set.
U-mode regions (plan C-2): only the U-executable code region is programmed. No U-RW data/stack region:
the U stubs use no stack and touch no data except the probe words whose per-mode verdict is the
subject of TP-PMP-006 (an R/W region over the pool would decide every load/store probe), and the
handler's report store runs in M-mode.

Red fixtures (red=True): the PROGRAM deviates on exactly one intent of one item while the plan stays
the green plan, so exactly that item's fire-check fails. Item and site come from
random.Random(f"{seed}:red") unless red_item names the item. TP-PMP-001..007: one CSR write of the
item carries a deviated operand (A[0] of the entry flipped for 001 and 006, one pmpaddr bit for 002,
the X bit for 003/004/005, the first stored bit that changes the outcome for 007); the read-back is
reported, then the planned value is restored without a report so no later expectation moves.
TP-PMP-008: one of the U-mode attempted writes is let through (an M-mode write of the same CSR class
right after the return to M), caught by the after-U read-back, then restored. The record words carry
cause, MPP and index only, so the identity of the CSR a U attempt named is not observable through the
report channel (RVFI export needed); the red targets the item's no-write clause.

CLI: python3 gen_pmp_csr_warl_prog.py --seed N --out <file.S> [--red [--red-item TP-PMP-00X]]
     python3 gen_pmp_csr_warl_prog.py --seed N --check-spike <spike_commits.log> --sym <prog.sym.json>
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
from dv.auto_dv.tests.gen_programs.gen_prog_const import (  # noqa: E402
    CONFIG_NAME, CSR, PMPADDR_BASE, PMPCFG_BASE, TOHOST_FAIL, TOHOST_PASS, pmpaddr, pmpcfg)

RNG_TAG = "program:pmp_csr_warl"
RED_RNG_TAG = "red"
RED_ITEMS = tuple(f"TP-PMP-00{i}" for i in range(1, 9))


def _config():
    """PMP build parameters from the one configuration source (ibex_configs.yaml, as util/ibex_config.py reads it)."""
    import yaml
    cfg = yaml.safe_load((ROOT / "ibex_configs.yaml").read_text())[CONFIG_NAME]
    assert cfg["PMPEnable"] == 1, "gen_pmp_csr_warl_prog: the configuration has no PMP"
    return int(cfg["PMPNumRegions"]), int(cfg["PMPGranularity"])


NUM_REGIONS, GRANULARITY = _config()
assert GRANULARITY == 0, "gen_pmp_csr_warl_prog: the plan's WARL expectations assume G = 0 (NA4 selectable, full pmpaddr)"
NUM_CFG_CSRS = NUM_REGIONS // 4
# gcc 10.2 knows no mseccfg name, so the program names these two CSRs by number.
CSR_MSECCFG, CSR_MSECCFGH = CSR["mseccfg"], CSR["mseccfgh"]
MSECCFG_MML, MSECCFG_MMWP, MSECCFG_RLB = 1, 2, 4
A_OFF, A_TOR, A_NA4, A_NAPOT = 0, 1, 2, 3
A_NAMES = {A_OFF: "OFF", A_TOR: "TOR", A_NA4: "NA4", A_NAPOT: "NAPOT"}
# Exception causes (priv spec mcause table) and the M-mode handler's record word layout.
CAUSE_IFETCH, CAUSE_ILLEGAL, CAUSE_LOAD, CAUSE_STORE, CAUSE_ECALL_U = 1, 2, 5, 7, 8
UIMM_FORMS = ("csrrwi", "csrrsi", "csrrci")


def record(cause, idx, mpp=0):
    """Handler record word: mcause << 16 | mstatus.MPP << 8 | instruction index (words from the stub base)."""
    return (cause << 16) | (mpp << 8) | (idx & 0xFF)


# Word-address window whose regions can never cover the program, the MMIO page or the boot page:
# [0x40000000, 0x80000000) in bytes. Every entry that can deny M-mode keeps its pmpaddr <= SAFE_MAX_WORD
# (a NAPOT value there spans at most [0, 0x80000000)); the debug module lies below the window.
WINDOW_LO_WORD = 0x10000000
SAFE_MAX_WORD = (MEMORY_MAP["boot_page"] >> 2) - 2
assert MEMORY_MAP["boot_page"] == 0x80000000 and MEMORY_MAP["mmio_base"] >= MEMORY_MAP["boot_page"], \
    "gen_pmp_csr_warl_prog: the safety window assumes the program and MMIO pages sit at or above 0x80000000"
assert MEMORY_MAP["dm_base"] + MEMORY_MAP["dm_size"] <= WINDOW_LO_WORD * 4, "gen_pmp_csr_warl_prog: DM window overlaps the safety window"

# Layout symbols (global labels of the program) whose addresses resolve the relative expectations; the
# placeholders keep the model's addresses distinct while generating, the symbol table gives the real ones.
BASE_SYMBOLS = {"pool": "gen_probe_pool", "ucode": "gen_u_code", "text_end": "gen_text_end"}
PH_UCODE = MEMORY_MAP["boot_page"] + 0x400
PH_POOL = MEMORY_MAP["boot_page"] + 0x3000
PH_TEXT_END = MEMORY_MAP["boot_page"] + 0x1000
UCODE_ALIGN_BITS = 9            # U code area: 512 bytes, one NAPOT with 6 trailing ones
UCODE_NAPOT_ONES = UCODE_ALIGN_BITS - 3
U_CODE_ENTRY = NUM_REGIONS - 1  # the U-executable region sits at the lowest-priority entry
POOL_ALIGN_BITS = 6
PROBE_CODE_WORD = 0x80820A85    # c.addi s5, 1 ; c.jr ra  (one NA4 word that counts and returns)
LOAD_SENT0, LOAD_SENT1, STORE_PAT, FETCH_SENT = 0x5E170000, 0x5E170001, 0x57A7E000, 0x0F000000
MPP_MASK = 0x1800               # mstatus.MPP field (bits 12:11)

# Layer-1 distributions transcribed from the items' Stimulus fields (gen_test_plan.md Section 4.4).
W_ADDR_VALUE = {"uniform": 50, "hi_bits": 25, "pattern": 25}                    # TP-PMP-002
W_PROBE_TYPE = {"load": 40, "store": 40, "fetch": 20}                            # TP-PMP-006 probe type
W_NAPOT_ONES = {0: 50, 1: 30, 2: 20}                                             # TP-PMP-006 NAPOT size 8/16/32 bytes
W_OP_FORM_RMW = {"csrrs": 30, "csrrc": 25, "csrrsi": 15, "csrrci": 15, "csrrwi": 15}   # TP-PMP-007
W_LOCK_A = {A_OFF: 40, A_NA4: 30, A_NAPOT: 30}                                   # TP-PMP-004 L=1 rows (TOR excluded: base ambiguity)

FILLER_REGS = ["a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "t4", "t5", "t6"]
ATTEMPT_REGS = ["a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7"]


def wchoice(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def cfg_byte(l, a, x, w, r, res=0):
    return ((l & 1) << 7) | ((res & 3) << 5) | ((a & 3) << 3) | ((x & 1) << 2) | ((w & 1) << 1) | (r & 1)


def byte_fields(b):
    """(L, A, X, W, R) of one pmpcfg byte."""
    return (b >> 7) & 1, (b >> 3) & 3, (b >> 2) & 1, (b >> 1) & 1, b & 1


def trailing_ones(v):
    n = 0
    while n < 32 and (v >> n) & 1:
        n += 1
    return n


def is_cfg(csr):
    return PMPCFG_BASE <= csr < PMPCFG_BASE + NUM_CFG_CSRS


def is_addr(csr):
    return PMPADDR_BASE <= csr < PMPADDR_BASE + NUM_REGIONS


def cfg_bits(lane, first):
    """Red candidate bits of a pmpcfg operand: the preferred (lane, field bit) first, then every stored
    non-lock field bit (R W X A0 A1 = bits 0..4 of each lane; 6:5 read zero and L = 7 are never flipped)."""
    pref = 8 * lane + first
    return [pref] + [8 * ln + b for ln in range(4) for b in (2, 3, 4, 0, 1) if 8 * ln + b != pref]


def addr_bits(first):
    return [first] + [b for b in range(32) if b != first]


class PmpModel:
    """PMP CSR state and the WARL write rules, each taken from the specification; the RTL
    (rtl/ibex_cs_registers.sv g_pmp_registers, rtl/ibex_pmp.sv) is a cross-check only:
      - pmpcfg bits 6:5 are reserved and read zero (machine.adoc pmpcfg format; cs_registers.rst pmpcfgx
        table "Reserved (Read as zero)");
      - RW=01 is reserved while MML=0 (machine.adoc norm pmp_rwx_warl and the mseccfg rule list); the
        documented Ibex WARL outcome is W=0 with R/X/A/L kept (cs_registers.rst pmpcfgx note); under MML=1
        every LRWX value is a defined encoding (smepmp.adoc norm mml_truth_table), so W is stored verbatim;
      - a locked entry (L=1, RLB=0) ignores pmpcfg and pmpaddr writes, and a locked TOR entry i also freezes
        pmpaddr(i-1) (machine.adoc norm pmp_l_bit_write_protection; norm mseccfg_rlb_op_warl for the bypass);
      - under MML=1 with RLB=0 a write producing an M-mode-only or locked shared-region rule with execute
        privilege (truth-table rows LRWX 1001, 1010, 1011, 1101) is ignored for that entry (machine.adoc norm
        mseccfg_mml_X_restrict); LRWX=1111 is the locked shared read-only data region and is stored (norm
        mseccfg_mml_shared_LRWX_1111_op);
      - MML and MMWP are sticky once set (smepmp.adoc norm mseccfg_locking); RLB stays 0 while any entry has
        L=1 with RLB=0 (machine.adoc norm mseccfg_rlb_op_warl);
      - pmpaddr stores all 32 bits at G=0 (machine.adoc norms pmp_tor_off_addr_read_mask and
        pmp_napot_addr_read_mask mask low bits only for G >= 1; PMPGranularity 0 in ibex_configs.yaml);
      - mseccfgh reads zero and ignores writes (cs_registers.rst mseccfg section);
      - csrrsi/csrrci with uimm = 0 read without writing (unprivileged spec, Zicsr CSR instruction table);
        the register forms always use rs1 = t0 here, so they always write;
      - U-mode access verdict at MML=0: lowest-numbered matching entry decides by its R/W/X, L does not
        matter below M, no match denies (machine.adoc norms pmp_entry_priority, pmp_no_entry_match)."""

    def __init__(self):
        self.cfg = [0] * NUM_REGIONS
        self.addr = [0] * NUM_REGIONS
        self.mml = self.mmwp = self.rlb = 0

    def copy(self):
        c = PmpModel.__new__(PmpModel)
        c.cfg, c.addr = list(self.cfg), list(self.addr)
        c.mml, c.mmwp, c.rlb = self.mml, self.mmwp, self.rlb
        return c

    # --- reads -----------------------------------------------------------------------------------
    def read_cfg(self, n):
        return sum(self.cfg[4 * n + i] << (8 * i) for i in range(4))

    def read(self, csr):
        if is_cfg(csr):
            return self.read_cfg(csr - PMPCFG_BASE)
        if is_addr(csr):
            return self.addr[csr - PMPADDR_BASE]
        if csr == CSR_MSECCFG:
            return (self.rlb << 2) | (self.mmwp << 1) | self.mml
        if csr == CSR_MSECCFGH:
            return 0
        raise AssertionError(f"model: unknown CSR 0x{csr:03x}")

    # --- write rules -------------------------------------------------------------------------------
    def locked(self, e):
        return bool((self.cfg[e] >> 7) & 1) and not self.rlb

    @staticmethod
    def is_mml_m_exec(b):
        """A locked row that grants M-mode execution under MML (truth-table rows LRWX 1001, 1010, 1011, 1101)."""
        l, _a, x, w, r = byte_fields(b)
        return l == 1 and (r, w, x) in ((0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 1))

    def legalise_byte(self, b):
        l, a, x, w, r = byte_fields(b)
        w_eff = w if self.mml else (w & r)
        return cfg_byte(l, a, x, w_eff, r)

    def write_cfg(self, n, value):
        for i in range(4):
            e = 4 * n + i
            b = self.legalise_byte((value >> (8 * i)) & 0xFF)
            suppress = self.mml and not self.rlb and self.is_mml_m_exec(b)
            if not self.locked(e) and not suppress:
                self.cfg[e] = b

    def addr_writable(self, e):
        tor_lock = e < NUM_REGIONS - 1 and self.locked(e + 1) and ((self.cfg[e + 1] >> 3) & 3) == A_TOR
        return not self.locked(e) and not tor_lock

    def write_addr(self, e, value):
        if self.addr_writable(e):
            self.addr[e] = value & 0xFFFFFFFF

    def write_mseccfg(self, value):
        any_locked = any(self.locked(e) for e in range(NUM_REGIONS))
        rlb_d = 0 if any_locked else (value >> 2) & 1
        self.mml |= value & 1
        self.mmwp |= (value >> 1) & 1
        self.rlb = rlb_d

    def write(self, csr, value):
        if is_cfg(csr):
            self.write_cfg(csr - PMPCFG_BASE, value)
        elif is_addr(csr):
            self.write_addr(csr - PMPADDR_BASE, value)
        elif csr == CSR_MSECCFG:
            self.write_mseccfg(value)
        elif csr == CSR_MSECCFGH:
            pass
        else:
            raise AssertionError(f"model: unknown CSR 0x{csr:03x}")

    def combined(self, form, csr, operand):
        """The value the CSR write path sees for one op form; None when no write happens."""
        old = self.read(csr)
        if form in ("csrrw", "csrrwi"):
            return operand
        if form in ("csrrs", "csrrsi"):
            return None if operand == 0 and form == "csrrsi" else (old | operand)
        if form in ("csrrc", "csrrci"):
            return None if operand == 0 and form == "csrrci" else (old & ~operand & 0xFFFFFFFF)
        raise AssertionError(form)

    def op(self, form, csr, operand):
        """Apply one CSR op; returns the old value (the op's rd)."""
        old = self.read(csr)
        wdata = self.combined(form, csr, operand)
        if wdata is not None:
            self.write(csr, wdata)
        return old

    # --- U-mode access verdict under MML=0 ------------------------------------------------------------
    def match(self, e, word):
        a = (self.cfg[e] >> 3) & 3
        if a == A_OFF:
            return False
        if a == A_NA4:
            return word == self.addr[e]
        if a == A_NAPOT:
            mask = (1 << (trailing_ones(self.addr[e]) + 1)) - 1   # NAPOT regions are 8 bytes at least (spec NAPOT table)
            return (word & ~mask) == (self.addr[e] & ~mask)
        base = 0 if e == 0 else self.addr[e - 1]
        return base <= word < self.addr[e]

    def u_allowed(self, byte_addr, access):
        """access: 'load' | 'store' | 'fetch'; an unmatched U-mode access is denied; L is ignored for U."""
        assert self.mml == 0, "the U verdict is modelled for MML=0 only"
        word = (byte_addr >> 2) & 0xFFFFFFFF
        for e in range(NUM_REGIONS):
            if self.match(e, word):
                _l, _a, x, w, r = byte_fields(self.cfg[e])
                return bool({"load": r, "store": w, "fetch": x}[access])
        return False


@dataclass
class Report:
    item: str
    label: str
    kind: str                   # 'abs' (value), 'rel' (base name, byte offset, or-mask), 'base' (base name)
    value: object = None
    idx: int = -1


@dataclass
class Plan:
    seed: int
    red: bool
    rlb: int
    reports: list = field(default_factory=list)
    items: dict = field(default_factory=dict)
    lines: list = field(default_factory=list)
    min_retired: int = 0
    red_item: str = ""
    red_note: str = ""
    red_sites: dict = field(default_factory=dict)

    @property
    def k(self):
        return len(self.reports)

    def expected(self, idx, bases):
        """Expected value of report idx; bases = {'pool'|'ucode'|'text_end': byte address} from the symbol table."""
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
    """The layout bases from a prog.sym.json symbol table ({name: '0x...'})."""
    missing = [s for s in BASE_SYMBOLS.values() if s not in symbols]
    assert not missing, f"gen_pmp_csr_warl_prog: the image defines no symbol {missing}"
    return {k: int(symbols[s], 16) for k, s in BASE_SYMBOLS.items()}


def csr_name(csr):
    if is_cfg(csr):
        return f"pmpcfg{csr - PMPCFG_BASE}"
    if is_addr(csr):
        return f"pmpaddr{csr - PMPADDR_BASE}"
    return f"0x{csr:03x}"


class Gen:
    def __init__(self, seed, red_target=None):
        self.rng = random.Random(f"{int(seed)}:{RNG_TAG}")
        self.m = PmpModel()
        self.plan = Plan(seed=seed, red=red_target is not None, rlb=self.rng.choice([0, 1]))
        self.plan.items = {tp: {} for tp in RED_ITEMS}
        self.plan.items["bases"] = {}
        self.main = []          # main-flow lines (executed once, in order)
        self.aux = []           # handler and U stubs
        self.pool = []          # (init word, kind) per pool word
        self.u_attempts = []    # (asm, form, cls, is_write)
        self.res_n = 0
        self.in_main = True
        self.probe_count = 0
        # pmpaddr entries holding a layout-relative value: ('pool'|'ucode'|'text_end', byte offset, or-mask);
        # their read-back expectation is resolved from the symbol table, and they are never RMW targets
        self.addr_rel = [None] * NUM_REGIONS
        # red fixture: (item, site serial) to deviate at; every eligible site is recorded per item
        self.red_target = red_target
        self.red_sites = {tp: [] for tp in RED_ITEMS}
        self.site_serial = 0

    # --- emission ---------------------------------------------------------------------------------
    def emit(self, line):
        (self.main if self.in_main else self.aux).append(line)
        text = line.strip()
        if self.in_main and text and not text.startswith((".", "#")) and not text.endswith(":"):
            self.plan.min_retired += 1

    def report_reg(self, reg, item, label, kind, value):
        self.emit(f"  sw   {reg}, 0(s0)")
        r = Report(item, label, kind, value, len(self.plan.reports))
        self.plan.reports.append(r)
        return r.idx

    def expect_record(self, item, label, value):
        """A report word the handler stores during a U episode (no main-flow instruction)."""
        r = Report(item, label, "abs", value, len(self.plan.reports))
        self.plan.reports.append(r)
        return r.idx

    def filler(self, n_max=3):
        for _ in range(self.rng.randint(0, n_max)):
            rd, rs = self.rng.choice(FILLER_REGS), self.rng.choice(FILLER_REGS)
            kind = self.rng.choice(["addi", "xori", "andi", "ori", "slli", "srli", "add", "sub", "xor", "or", "and"])
            if kind in ("addi", "xori", "andi", "ori"):
                self.emit(f"  {kind} {rd}, {rs}, {self.rng.randint(-2048, 2047)}")
            elif kind in ("slli", "srli"):
                self.emit(f"  {kind} {rd}, {rs}, {self.rng.randint(0, 31)}")
            else:
                self.emit(f"  {kind}  {rd}, {rs}, {self.rng.choice(FILLER_REGS)}")

    def li(self, reg, value):
        self.emit(f"  li   {reg}, 0x{value & 0xFFFFFFFF:08x}")

    # --- red fixture mechanics ----------------------------------------------------------------------
    def state_safe(self, m):
        """No enforced active entry above the code rule reaches the program window (M-mode stays runnable)."""
        for e in range(1, NUM_REGIONS):
            l, a, _x, _w, _r = byte_fields(m.cfg[e])
            if a != A_OFF and (m.mml or l) and m.addr[e] > SAFE_MAX_WORD:
                return False
        return True

    def red_deviation(self, form, csr, operand, before, bits):
        """A program operand differing from the plan by one candidate bit whose spec-modelled outcome differs
        from the planned read-back and keeps M-mode safe; None when no candidate qualifies."""
        planned = self.m.read(csr)
        for bit in bits:
            if form in UIMM_FORMS and bit > 4:
                continue
            cand = operand ^ (1 << bit)
            clone = before.copy()
            clone.op(form, csr, cand)
            if clone.read(csr) != planned and self.state_safe(clone):
                return cand
        return None

    def red_site(self, item, form, csr, operand, before, bits):
        """Record a deviation-eligible site; returns the deviated operand when this site is the red target."""
        if bits is None or (is_addr(csr) and self.addr_rel[csr - PMPADDR_BASE] is not None):
            return None
        dev = self.red_deviation(form, csr, operand, before, bits)
        serial, self.site_serial = self.site_serial, self.site_serial + 1
        if dev is None:
            return None
        self.red_sites[item].append(serial)
        if self.red_target == (item, serial):
            self.plan.red_item = item
            return dev
        return None

    def restore(self, csr):
        """Write the planned value back after a red deviation (no report): later expectations stay green."""
        self.li("t0", self.m.read(csr))
        self.emit(f"  csrw {csr_name(csr)}, t0")

    def csr_op(self, form, csr, operand, item, label, report_old=False, expect=None, red_bits=None):
        """One CSR op with the model update, optional rd report (old value) and the read-back report.
        red_bits: candidate bits of a red deviation at this site (None: the site is never deviated)."""
        e_addr = csr - PMPADDR_BASE if is_addr(csr) else None
        if e_addr is not None:
            assert form in ("csrrw", "csrrwi") or self.addr_rel[e_addr] is None, f"RMW on layout-relative pmpaddr{e_addr}"
            if self.m.addr_writable(e_addr) and form in ("csrrw", "csrrwi"):
                self.addr_rel[e_addr] = None
        before = self.m.copy()
        old = self.m.op(form, csr, operand)
        if e_addr is not None and expect is None and self.addr_rel[e_addr] is not None:
            expect = ("rel", self.addr_rel[e_addr])
        dev = self.red_site(item, form, csr, operand, before, red_bits)
        prog_val = operand if dev is None else dev
        name = csr_name(csr)
        if form in ("csrrw", "csrrs", "csrrc"):
            self.li("t0", prog_val)
            self.emit(f"  {form} t1, {name}, t0")
        else:
            assert 0 <= prog_val <= 31, "uimm form needs a 5-bit operand"
            self.emit(f"  {form} t1, {name}, {prog_val}")
        old_idx = self.report_reg("t1", item, f"{label} rd_old {form} {name}", "abs", old) if report_old else None
        self.emit(f"  csrr t1, {name}")
        rb = self.m.read(csr)
        if expect is None:
            idx = self.report_reg("t1", item, f"{label} readback {name}", "abs", rb)
        else:
            idx = self.report_reg("t1", item, f"{label} readback {name}", expect[0], expect[1])
        if dev is not None:
            self.plan.red_note = f"{item} {label}: program {form} {name} with 0x{dev:08x} for planned 0x{operand:08x}, read-back idx {idx}"
            self.restore(csr)
        return old_idx, idx

    def cfg_word_with(self, n, lane, b):
        """The current pmpcfgN read value with one entry byte replaced (entry-targeted writes)."""
        v = self.m.read_cfg(n)
        return (v & ~(0xFF << (8 * lane))) | (b << (8 * lane))

    def window_word(self):
        return self.rng.randint(WINDOW_LO_WORD, SAFE_MAX_WORD)

    def window_napot(self):
        """A NAPOT value whose region stays inside the window (at most 27 trailing ones)."""
        ones = self.rng.choice([0, 1, 2, 3, 5, 8, 12, 17, 22, 27])
        base = WINDOW_LO_WORD | (self.rng.randrange(0, 1 << (28 - ones)) << ones)
        v = base | ((1 << ones) - 1)
        return v if v <= SAFE_MAX_WORD else base

    # --- P0 -----------------------------------------------------------------------------------------
    def p0_setup(self):
        self.emit("  la   t0, gen_trap_vec")
        self.emit("  ori  t0, t0, 1")          # vectored mode bit: Ibex forces it, Spike stores it, both read back base|1
        self.emit("  csrw mtvec, t0")
        self.emit("  li   s0, GEN_MM_EOT_ADDR")
        self.emit("  la   s1, gen_probe_pool")
        self.plan.items["bases"]["pool"] = self.report_reg("s1", "bases", "probe pool base", "base", "pool")
        self.emit("  la   t4, gen_u_code")
        self.plan.items["bases"]["ucode"] = self.report_reg("t4", "bases", "U code area base", "base", "ucode")
        self.emit("  la   t4, gen_text_end")
        self.plan.items["bases"]["text_end"] = self.report_reg("t4", "bases", "end of .text", "base", "text_end")
        # Entry 0 explicitly cleared (csrw: no rd) so a PMP-unaware reference reset (Spike: pmpcfg0 NAPOT RWX,
        # pmpaddr0 all ones) cannot leak into the first read-modify-write; Ibex already resets both to 0.
        for name in ("pmpcfg0", "pmpaddr0"):
            self.emit(f"  csrw {name}, zero")
            self.emit(f"  csrr t1, {name}")
            self.report_reg("t1", "setup", f"entry 0 cleared: {name}", "abs", 0)

    # --- TP-PMP-001 ---------------------------------------------------------------------------------
    def p1_tp001(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-001"]
        meta["cfg_readbacks"] = []          # (report idx, N)
        order = list(range(NUM_CFG_CSRS))
        rng.shuffle(order)
        counts = {n: rng.randint(8, 32) for n in order}
        for n in order:
            for w in range(counts[n]):
                bytes_ = [cfg_byte(0, rng.randrange(4), rng.randrange(2), rng.randrange(2), rng.randrange(2), rng.randrange(4))
                          for _ in range(4)]
                value = sum(b << (8 * i) for i, b in enumerate(bytes_))
                _o, idx = self.csr_op("csrrw", pmpcfg(n), value, "TP-PMP-001", f"w{w}", red_bits=cfg_bits(0, 3))
                meta["cfg_readbacks"].append((idx, n))
                if rng.random() < 0.4:      # interleaved random pmpaddr writes (harmless with L=0 under MML=0)
                    e = rng.randrange(NUM_REGIONS)
                    self.csr_op("csrrw", pmpaddr(e), rng.getrandbits(32), "TP-PMP-001", f"w{w} addr{e}")
                self.filler()

    # --- TP-PMP-002 ---------------------------------------------------------------------------------
    def addr_value(self):
        cls = wchoice(self.rng, W_ADDR_VALUE)
        if cls == "uniform":
            return self.rng.getrandbits(32), cls
        if cls == "hi_bits":
            return self.rng.getrandbits(32) | self.rng.choice([1 << 31, 1 << 30, 3 << 30]), cls
        pat = self.rng.choice([0xFFFFFFFF, 0xAAAAAAAA, 0x55555555, 1 << self.rng.randrange(32), 0])
        return pat, cls

    def p1_tp002(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-002"]
        meta["addr_readbacks"] = []         # (report idx, N, value class)
        meta["mode_readbacks"] = []
        for rnd in range(rng.randint(2, 3)):
            for n in rng.sample(range(NUM_CFG_CSRS), NUM_CFG_CSRS):
                value = sum(cfg_byte(0, rng.randrange(4), rng.randrange(2), rng.randrange(2), rng.randrange(2)) << (8 * i) for i in range(4))
                _o, idx = self.csr_op("csrrw", pmpcfg(n), value, "TP-PMP-002", f"r{rnd} modes")
                meta["mode_readbacks"].append((idx, n))
            for e in rng.sample(range(NUM_REGIONS), NUM_REGIONS):
                v, cls = self.addr_value()
                _o, idx = self.csr_op("csrrw", pmpaddr(e), v, "TP-PMP-002", f"r{rnd} e{e} {cls}", red_bits=addr_bits(0))
                meta["addr_readbacks"].append((idx, e, cls))
                self.filler(2)
        # the item's fire-check wants bit 31 or 30 written at least once per N: top up the entries the draw missed
        hi = {e for idx, e, _c in meta["addr_readbacks"] if self.plan.reports[idx].value & (3 << 30)}
        for e in rng.sample([e for e in range(NUM_REGIONS) if e not in hi], NUM_REGIONS - len(hi)):
            v = rng.getrandbits(32) | rng.choice([1 << 31, 1 << 30, 3 << 30])
            _o, idx = self.csr_op("csrrw", pmpaddr(e), v, "TP-PMP-002", f"top-up e{e} hi_bits", red_bits=addr_bits(0))
            meta["addr_readbacks"].append((idx, e, "hi_bits"))

    # --- TP-PMP-003 ---------------------------------------------------------------------------------
    def tp003(self, phase):
        rng, meta = self.rng, self.plan.items["TP-PMP-003"]
        meta.setdefault("res_writes", [])   # (report idx, N, lanes with bits 6:5 set in the combined value, mml)
        meta.setdefault("ops", [])
        entries_ok = [e for e in range(NUM_REGIONS) if not self.m.locked(e) and (phase == "mml0" or e != 0)]
        for _ in range(rng.randint(4, 8)):
            n = rng.choice(sorted({e // 4 for e in entries_ok}))
            form = rng.choice(["csrrw", "csrrs", "csrrc"])
            lanes = rng.sample(range(4), rng.randint(1, 4))
            if phase == "mml1":
                lanes = [ln for ln in lanes if 4 * n + ln != 0] or [rng.choice([1, 2, 3])]
            value = 0
            for ln in range(4):
                e = 4 * n + ln
                if ln in lanes and not self.m.locked(e):
                    a = rng.randrange(4) if (phase == "mml0" or e != 0) else 0
                    b = cfg_byte(0, a, rng.randrange(2), rng.randrange(2), rng.randrange(2), 3)   # bits 6:5 set, L=0
                    if rng.random() < 0.3:
                        b = 0x7F                                                                   # all ones but L
                    value |= b << (8 * ln)
                elif form == "csrrw":
                    value |= self.m.cfg[e] << (8 * ln)                                            # keep the other entries
            if form != "csrrw":
                value &= 0x7F7F7F7F                                                                # never set L, never clear the code rule
                if phase == "mml1" and n == 0:
                    value &= 0xFFFFFF00
            comb = self.m.combined(form, pmpcfg(n), value)
            res_lanes = [ln for ln in range(4) if comb is not None and (comb >> (8 * ln)) & 0x60]
            _o, idx = self.csr_op(form, pmpcfg(n), value, "TP-PMP-003", f"{phase} {form}", red_bits=cfg_bits(lanes[0], 2))
            meta["ops"].append((idx, n, form, phase))
            if res_lanes:
                meta["res_writes"].append((idx, n, res_lanes, self.m.mml))
            self.filler(2)
        if not any(w[3] == (1 if phase == "mml1" else 0) for w in meta["res_writes"]):
            # Every draw above can be a clear-type write, which cannot present reserved bits at all:
            # they read zero, so csrrc combines to zero there. One directed set-type write keeps the
            # item's intent at such a seed; it draws only when the loop produced none, so every other
            # seed's program is unchanged.
            cands = [(e // 4, e % 4) for e in entries_ok]
            n = cands[0][0]
            lanes = [ln for nn, ln in cands if nn == n]
            value = sum(0x60 << (8 * ln) for ln in lanes)
            comb = self.m.combined("csrrs", pmpcfg(n), value)
            res_lanes = [ln for ln in range(4) if comb is not None and (comb >> (8 * ln)) & 0x60]
            _o, idx = self.csr_op("csrrs", pmpcfg(n), value, "TP-PMP-003",
                                  f"{phase} csrrs reserved-bit backstop", red_bits=cfg_bits(lanes[0], 2))
            meta["ops"].append((idx, n, "csrrs", phase))
            meta["res_writes"].append((idx, n, res_lanes, self.m.mml))
            self.filler(2)
        assert any(w[3] == (1 if phase == "mml1" else 0) for w in meta["res_writes"]), f"TP-PMP-003 {phase}: no reserved-bit write drawn"

    # --- TP-PMP-004 (MML=0) -------------------------------------------------------------------------
    def p1_tp004(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-004"]
        meta["rw01_bytes"] = []             # (report idx, N, lane, written byte)
        for e in rng.sample(range(NUM_REGIONS), NUM_REGIONS):
            n, ln = divmod(e, 4)
            b = cfg_byte(0, rng.randrange(4), rng.randrange(2), 1, 0)
            _o, idx = self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, ln, b), "TP-PMP-004", f"e{e} rw01", red_bits=cfg_bits(ln, 2))
            meta["rw01_bytes"].append((idx, n, ln, b))
            self.filler(2)
        # csrrs masks that would turn RW=00 into RW=01
        cands = [e for e in range(NUM_REGIONS) if (self.m.cfg[e] & 3) == 0]
        for e in rng.sample(cands, min(len(cands), rng.randint(2, 4))):
            n, ln = divmod(e, 4)
            b = self.m.cfg[e] | 0x02
            _o, idx = self.csr_op("csrrs", pmpcfg(n), 0x02 << (8 * ln), "TP-PMP-004", f"e{e} csrrs W", red_bits=cfg_bits(ln, 2))
            meta["rw01_bytes"].append((idx, n, ln, b))

    def p3_tp004_locked(self, lock_entries):
        rng, meta = self.rng, self.plan.items["TP-PMP-004"]
        meta["lock_bytes"] = []             # (report idx, N, lane, written byte)
        for e in lock_entries:
            n, ln = divmod(e, 4)
            a = wchoice(rng, W_LOCK_A)
            if a != A_OFF:
                v = self.window_napot() if a == A_NAPOT else self.window_word()
                self.csr_op("csrrw", pmpaddr(e), v, "TP-PMP-004", f"lock e{e} addr")
            b = cfg_byte(1, a, rng.randrange(2), 1, 0)
            _o, idx = self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, ln, b), "TP-PMP-004", f"lock e{e} rw01 L=1")
            meta["lock_bytes"].append((idx, n, ln, b))

    # --- TP-PMP-007 ---------------------------------------------------------------------------------
    def rmw_operand(self, form, csr, phase, entry_ok):
        """A mask/value for one RMW op that keeps the safety invariants of the phase; None to skip."""
        rng, m = self.rng, self.m
        for _ in range(64):
            if is_cfg(csr):
                n = csr - PMPCFG_BASE
                if form == "csrrwi":
                    if 4 * n == 0 and phase != "mml0":
                        return None
                    operand = rng.randrange(0, 32)
                else:
                    operand = 0
                    for ln in range(4):
                        if entry_ok(4 * n + ln) and rng.random() < 0.6:
                            operand |= rng.randrange(0, 256) << (8 * ln)
                    if form in ("csrrsi", "csrrci"):
                        operand = rng.randrange(0, 32) if entry_ok(4 * n) else 0
                    if phase == "mml0":
                        operand &= 0x7F7F7F7F if form in ("csrrs", "csrrsi") else 0xFFFFFFFF    # no lock before the lock step
                comb = m.combined(form, csr, operand)
                if comb is None:
                    continue
                bad = False
                for ln in range(4):
                    e, b = 4 * n + ln, (comb >> (8 * ln)) & 0xFF
                    l, a, _x, _w, _r = byte_fields(b)
                    if phase != "mml0" and e == 0 and b != m.cfg[0]:
                        bad = True                                     # the code rule byte is never touched
                    if l and a == A_TOR and (m.addr[e] > SAFE_MAX_WORD or (e > 0 and m.addr[e - 1] > SAFE_MAX_WORD)):
                        bad = True                                     # a denying TOR needs both bounds in the window
                    if l and a in (A_NA4, A_NAPOT) and m.addr[e] > SAFE_MAX_WORD:
                        bad = True
                    if phase == "mml1" and a != A_OFF and m.addr[e] > SAFE_MAX_WORD:
                        bad = True
                if bad:
                    continue
                return operand
            if is_addr(csr):
                if form == "csrrwi" and phase != "mml0":
                    return None
                operand = rng.randrange(0, 32) if form in UIMM_FORMS else rng.getrandbits(32)
                comb = m.combined(form, csr, operand)
                if comb is None:
                    continue
                if phase != "mml0" and comb > SAFE_MAX_WORD:
                    continue
                return operand
            # mseccfg: MMWP is never set; MML only once it is already set (sticky no-op); RLB may be set (a
            # WARL no-op when locked or already 1) and is never cleared after the lock step.
            if form in ("csrrs", "csrrsi", "csrrwi"):
                operand = rng.getrandbits(32) if form == "csrrs" else rng.randrange(0, 32)
                operand &= ~MSECCFG_MMWP & 0xFFFFFFFF
                if phase != "mml1":
                    operand &= ~MSECCFG_MML & 0xFFFFFFFF
                if form == "csrrwi" and phase != "mml0":
                    operand |= self.m.read(CSR_MSECCFG) & (MSECCFG_RLB | MSECCFG_MML)
                return operand
            operand = rng.getrandbits(32) if form == "csrrc" else rng.randrange(0, 32)
            if phase != "mml0":
                operand &= ~MSECCFG_RLB & 0xFFFFFFFF
            return operand
        return None

    def tp007(self, phase, n_ops, entry_ok, csr_classes=("pmpcfg", "pmpaddr", "mseccfg")):
        rng, meta = self.rng, self.plan.items["TP-PMP-007"]
        meta.setdefault("ops", [])          # (old idx, readback idx, form, class, phase)
        combos = [(f, c) for f in W_OP_FORM_RMW for c in csr_classes]
        rng.shuffle(combos)
        picks = combos + [(wchoice(rng, W_OP_FORM_RMW), rng.choice(csr_classes)) for _ in range(max(0, n_ops - len(combos)))]
        if phase != "mml0":
            picks = picks[:n_ops]
        for form, cls in picks:
            if cls == "pmpcfg":
                ns = sorted({e // 4 for e in range(NUM_REGIONS) if entry_ok(e)})
                csr, bits = pmpcfg(rng.choice(ns)), cfg_bits(0, 2)
            elif cls == "pmpaddr":
                csr, bits = pmpaddr(rng.choice([e for e in range(NUM_REGIONS) if entry_ok(e)])), addr_bits(0)
            else:
                csr, bits = CSR_MSECCFG, None      # sticky fields cannot be restored: never a red site
            operand = self.rmw_operand(form, csr, phase, entry_ok)
            if operand is None:
                continue
            old_idx, idx = self.csr_op(form, csr, operand, "TP-PMP-007", f"{phase} {form} {cls}", report_old=True, red_bits=bits)
            meta["ops"].append((old_idx, idx, form, cls, phase))
            self.filler(2)

    # --- table reset ---------------------------------------------------------------------------------
    def reset_cfgs(self, item, label):
        for n in self.rng.sample(range(NUM_CFG_CSRS), NUM_CFG_CSRS):
            self.csr_op("csrrw", pmpcfg(n), 0, item, f"{label} clear pmpcfg{n}")

    # --- P2: U-mode machinery -----------------------------------------------------------------------
    def set_u_code_region(self, item):
        """Entry U_CODE_ENTRY: NAPOT L=0 RWX=111 over the 512-byte U code area (M-mode ignores it under MML=0)."""
        e = U_CODE_ENTRY
        self.emit("  la   t0, gen_u_code")
        self.emit("  srli t0, t0, 2")
        self.emit(f"  ori  t0, t0, 0x{(1 << UCODE_NAPOT_ONES) - 1:x}")
        self.emit(f"  csrw pmpaddr{e}, t0")
        self.m.addr[e] = (PH_UCODE >> 2) | ((1 << UCODE_NAPOT_ONES) - 1)
        self.addr_rel[e] = ("ucode", 0, (1 << UCODE_NAPOT_ONES) - 1)
        self.emit(f"  csrr t1, pmpaddr{e}")
        self.report_reg("t1", item, f"U code region pmpaddr{e}", "rel", self.addr_rel[e])
        n, ln = divmod(e, 4)
        b = cfg_byte(0, A_NAPOT, 1, 1, 1)
        self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, ln, b), item, f"U code region pmpcfg{n}")

    def enter_u(self, stub_label, item, label):
        """M -> U through mret at the stub; the handler returns to gen_res_<n> on the stub's ecall."""
        self.res_n += 1
        res = f"gen_res_{self.res_n}"
        self.emit(f"  la   s9, {stub_label}")
        self.emit(f"  la   s8, {res}")
        self.emit("  csrw mepc, s9")
        self.li("t0", MPP_MASK)
        self.emit("  csrc mstatus, t0")
        self.emit("  mret")
        self.emit(f"{res}:")

    def p2_tp008(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-008"]
        classes = {"pmpcfg": lambda: pmpcfg(rng.randrange(NUM_CFG_CSRS)),
                   "pmpaddr": lambda: pmpaddr(rng.randrange(NUM_REGIONS)),
                   "mseccfg": lambda: CSR_MSECCFG, "mseccfgh": lambda: CSR_MSECCFGH}
        write_forms = ["csrrw", "csrrs", "csrrc", "csrrwi", "csrrsi", "csrrci", "csrw"]
        read_forms = ["csrr", "csrrsi0", "csrrci0"]
        picks = [(c, rng.choice(write_forms)) for c in classes] + [(c, rng.choice(read_forms)) for c in classes]
        picks += [(rng.choice(list(classes)), rng.choice(write_forms + read_forms)) for _ in range(rng.randint(0, 12))]
        rng.shuffle(picks)
        self.u_attempts = []
        for cls, form in picks:
            csr = classes[cls]()
            rd, rs = rng.choice(ATTEMPT_REGS + ["x0"]), rng.choice(ATTEMPT_REGS)
            uimm = rng.randrange(1, 32)
            name = csr_name(csr)
            asm = {"csrrw": f"csrrw {rd}, {name}, {rs}", "csrrs": f"csrrs {rd}, {name}, {rs}", "csrrc": f"csrrc {rd}, {name}, {rs}",
                   "csrrwi": f"csrrwi {rd}, {name}, {uimm}", "csrrsi": f"csrrsi {rd}, {name}, {uimm}",
                   "csrrci": f"csrrci {rd}, {name}, {uimm}", "csrw": f"csrw {name}, {rs}",
                   "csrr": f"csrr {rng.choice(ATTEMPT_REGS)}, {name}", "csrrsi0": f"csrrsi {rng.choice(ATTEMPT_REGS)}, {name}, 0",
                   "csrrci0": f"csrrci {rng.choice(ATTEMPT_REGS)}, {name}, 0"}[form]
            self.u_attempts.append((asm, form, cls, form in write_forms))
        meta["attempts"] = [(a[1], a[2], a[3]) for a in self.u_attempts]
        for reg in ATTEMPT_REGS:
            self.li(reg, rng.getrandbits(32))
        snapshot = [self.m.read(c) for c in self.all_csrs()]
        self.enter_u("gen_ustub_csr", "TP-PMP-008", "U CSR attempts")
        meta["records"] = [self.expect_record("TP-PMP-008", f"U attempt {i} {a[1]} {a[2]} -> illegal", record(CAUSE_ILLEGAL, i))
                           for i, a in enumerate(self.u_attempts)]
        meta["ecall_idx"] = self.expect_record("TP-PMP-008", "U ecall", record(CAUSE_ECALL_U, len(self.u_attempts)))
        meta["readbacks"] = []
        order = list(zip(self.all_csrs(), snapshot))
        rng.shuffle(order)
        for csr, val in order:
            assert self.m.read(csr) == val
            # red site (no-write clause): one attempted pmpcfg write lands after the return to M, then is restored
            leak = self.red_site("TP-PMP-008", "csrrw", csr, val, self.m, cfg_bits(0, 2) if is_cfg(csr) else None)
            if leak is not None:
                self.li("t0", leak)
                self.emit(f"  csrw {csr_name(csr)}, t0")
            self.emit(f"  csrr t1, {csr_name(csr)}")
            e = csr - PMPADDR_BASE
            if 0 <= e < NUM_REGIONS and self.addr_rel[e] is not None:
                idx = self.report_reg("t1", "TP-PMP-008", f"after U: {csr_name(csr)}", "rel", self.addr_rel[e])
            else:
                idx = self.report_reg("t1", "TP-PMP-008", f"after U: {csr_name(csr)}", "abs", val)
            meta["readbacks"].append((idx, csr))
            if leak is not None:
                self.plan.red_note = f"TP-PMP-008 after U: program writes {csr_name(csr)} 0x{leak:08x} (planned unchanged 0x{val:08x}), read-back idx {idx}"
                self.restore(csr)

    def all_csrs(self):
        return [pmpcfg(n) for n in range(NUM_CFG_CSRS)] + [pmpaddr(e) for e in range(NUM_REGIONS)] + [CSR_MSECCFG]

    def alloc_pair(self, code):
        """Two consecutive pool words (8-byte aligned); returns the byte offset of the first."""
        off = 4 * len(self.pool)
        assert off + 8 <= 2048, "probe pool exceeds the addi range"
        if code:
            self.pool += [(PROBE_CODE_WORD, "code"), (PROBE_CODE_WORD, "code")]
        else:
            i = len(self.pool)
            self.pool += [(0xA5000000 | (i << 8) | 0x11, "data"), (0xA5000000 | ((i + 1) << 8) | 0x22, "data")]
        return off

    def p2_tp006(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-006"]
        meta["a_readbacks"] = []            # (report idx, entry, A written)
        meta["episodes"] = []               # dicts: entry, A, ptype, expected verdicts, report idxs
        probe_entries = [e for e in range(NUM_REGIONS) if e != U_CODE_ENTRY]
        rng.shuffle(probe_entries)
        for e in probe_entries:
            n, ln = divmod(e, 4)
            modes = [A_OFF, A_TOR, A_NA4, A_NAPOT]
            rng.shuffle(modes)
            for a in modes:
                ptype = wchoice(rng, W_PROBE_TYPE)
                off = self.alloc_pair(code=(ptype == "fetch"))
                pool_word = (PH_POOL + off) >> 2
                r, w, x = rng.randrange(2), rng.randrange(2), rng.randrange(2)
                if e == 0 and a == A_TOR:
                    x = 1                                        # entry-0 TOR covers the U stub itself
                # pmpaddr programming per mode, expressed relative to the pool base
                if a == A_TOR:
                    span = rng.choice([1, 2])
                    if e > 0:
                        self.emit(f"  addi t0, s1, {off}")
                        self.emit("  srli t0, t0, 2")
                        self.emit(f"  csrw pmpaddr{e - 1}, t0")
                        self.m.write_addr(e - 1, pool_word)
                        self.addr_rel[e - 1] = ("pool", off, 0)
                        self.emit(f"  csrr t1, pmpaddr{e - 1}")
                        self.report_reg("t1", "TP-PMP-006", f"e{e} TOR base pmpaddr{e - 1}", "rel", self.addr_rel[e - 1])
                    self.emit(f"  addi t0, s1, {off + 4 * span}")
                    self.emit("  srli t0, t0, 2")
                    self.m.write_addr(e, pool_word + span)
                    rel = ("pool", off + 4 * span, 0)
                elif a == A_NAPOT:
                    ones = wchoice(rng, W_NAPOT_ONES)
                    low = (1 << (ones + 1)) - 1
                    aligned_off = off & ~(low << 2)
                    self.emit(f"  addi t0, s1, {aligned_off}")
                    self.emit("  srli t0, t0, 2")
                    if ones:
                        self.emit(f"  ori  t0, t0, 0x{(1 << ones) - 1:x}")
                    self.m.write_addr(e, ((PH_POOL + aligned_off) >> 2) | ((1 << ones) - 1))
                    rel = ("pool", aligned_off, (1 << ones) - 1)
                else:
                    self.emit(f"  addi t0, s1, {off}")
                    self.emit("  srli t0, t0, 2")
                    self.m.write_addr(e, pool_word)
                    rel = ("pool", off, 0)
                self.emit(f"  csrw pmpaddr{e}, t0")
                self.addr_rel[e] = rel
                self.emit(f"  csrr t1, pmpaddr{e}")
                self.report_reg("t1", "TP-PMP-006", f"e{e} {A_NAMES[a]} pmpaddr{e}", "rel", rel)
                b = cfg_byte(0, a, x, w, r)
                _o, idx = self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, ln, b), "TP-PMP-006", f"e{e} {A_NAMES[a]} cfg", red_bits=cfg_bits(ln, 3))
                meta["a_readbacks"].append((idx, e, a))
                # the U episode: probe the word and its neighbour
                ep = {"entry": e, "a": a, "ptype": ptype, "off": off, "rwx": (r, w, x), "records": [], "results": []}
                verdicts = [self.m.u_allowed(PH_POOL + off + 4 * p, ptype) for p in range(2)]
                ep["allowed"] = verdicts
                self.emit(f"  addi s2, s1, {off}")
                self.emit("  addi s3, s2, 4")
                if ptype == "load":
                    self.li("s5", LOAD_SENT0)
                    self.li("s7", LOAD_SENT1)
                elif ptype == "store":
                    self.li("s6", STORE_PAT)
                else:
                    self.li("s5", FETCH_SENT)
                self.enter_u(f"gen_ustub_{ptype}", "TP-PMP-006", f"e{e} {A_NAMES[a]} {ptype}")
                cause = {"load": CAUSE_LOAD, "store": CAUSE_STORE, "fetch": CAUSE_IFETCH}[ptype]
                for p in range(2):
                    if not verdicts[p]:
                        ep["records"].append(self.expect_record("TP-PMP-006", f"e{e} {A_NAMES[a]} {ptype} probe {p} denied", record(cause, p)))
                ep["ecall_idx"] = self.expect_record("TP-PMP-006", f"e{e} {A_NAMES[a]} ecall", record(CAUSE_ECALL_U, 2))
                w0, w1 = self.pool[off // 4][0], self.pool[off // 4 + 1][0]
                if ptype == "load":
                    ep["results"].append(self.report_reg("s5", "TP-PMP-006", f"e{e} {A_NAMES[a]} load word", "abs", w0 if verdicts[0] else LOAD_SENT0))
                    ep["results"].append(self.report_reg("s7", "TP-PMP-006", f"e{e} {A_NAMES[a]} load word+4", "abs", w1 if verdicts[1] else LOAD_SENT1))
                elif ptype == "store":
                    self.emit("  lw   t1, 0(s2)")
                    ep["results"].append(self.report_reg("t1", "TP-PMP-006", f"e{e} {A_NAMES[a]} stored word", "abs", STORE_PAT if verdicts[0] else w0))
                    self.emit("  lw   t1, 4(s2)")
                    ep["results"].append(self.report_reg("t1", "TP-PMP-006", f"e{e} {A_NAMES[a]} stored word+4", "abs", STORE_PAT if verdicts[1] else w1))
                else:
                    ep["results"].append(self.report_reg("s5", "TP-PMP-006", f"e{e} {A_NAMES[a]} fetched count", "abs", FETCH_SENT + sum(verdicts)))
                meta["episodes"].append(ep)
                self.probe_count += 1
            # leave the entry OFF so it never decides a later entry's probe
            self.csr_op("csrrw", pmpcfg(n), self.cfg_word_with(n, ln, 0), "TP-PMP-006", f"e{e} cleanup")

    # --- P3 -----------------------------------------------------------------------------------------
    def p3_lock_step(self):
        rng = self.rng
        # every pmpaddr concrete again before anything can lock (a locked entry keeps its value for good)
        for e in rng.sample(range(NUM_REGIONS), NUM_REGIONS):
            v, cls = self.addr_value()
            _o, idx = self.csr_op("csrrw", pmpaddr(e), v, "TP-PMP-002", f"pre-lock e{e} {cls}", red_bits=addr_bits(0))
            self.plan.items["TP-PMP-002"]["addr_readbacks"].append((idx, e, cls))
        assert all(r is None for r in self.addr_rel)
        self.csr_op("csrrw", CSR_MSECCFG, self.plan.rlb << 2, "TP-PMP-007", "lock step mseccfg RLB")
        assert self.m.rlb == self.plan.rlb
        lock_entries = rng.sample([e for e in range(1, NUM_REGIONS) if e != U_CODE_ENTRY], rng.randint(3, 6))
        self.plan.items["TP-PMP-004"]["lock_entries"] = lock_entries
        self.p3_tp004_locked(lock_entries)
        locked_ok = lambda e: e in lock_entries   # noqa: E731
        self.tp007("lock", rng.randint(6, 10), locked_ok)
        # RLB set attempt with locked entries (stays 0 when rlb=0, stays 1 when rlb=1)
        self.csr_op("csrrs", CSR_MSECCFG, MSECCFG_RLB, "TP-PMP-007", "lock step csrrs RLB", report_old=True)

    # --- P4 -----------------------------------------------------------------------------------------
    def p4_mml_phase(self):
        rng = self.rng
        self.reset_cfgs("TP-PMP-005", "pre-MML")
        for e in rng.sample(range(1, NUM_REGIONS), NUM_REGIONS - 1):
            self.csr_op("csrrw", pmpaddr(e), self.window_word(), "TP-PMP-005", f"pre-MML window pmpaddr{e}")
        # code rule: entry 0 TOR [0, end of .text), L=1 R/X (M-mode-only read/execute under MML)
        self.emit("  la   t0, gen_text_end")
        self.emit("  srli t0, t0, 2")
        self.emit("  csrw pmpaddr0, t0")
        self.m.write_addr(0, PH_TEXT_END >> 2)
        self.addr_rel[0] = ("text_end", 0, 0)
        self.emit("  csrr t1, pmpaddr0")
        self.report_reg("t1", "TP-PMP-005", "code rule pmpaddr0", "rel", self.addr_rel[0])
        code_byte = cfg_byte(1, A_TOR, 1, 0, 1)
        self.csr_op("csrrw", pmpcfg(0), self.cfg_word_with(0, 0, code_byte), "TP-PMP-005", "code rule pmpcfg0")
        assert self.m.cfg[0] == code_byte
        self.check_mml_safety()
        form = rng.choice(["csrrw", "csrrs", "csrrsi"])
        operand = MSECCFG_MML | (self.m.rlb << 2)
        _o, idx = self.csr_op(form, CSR_MSECCFG, operand, "TP-PMP-005", "set MML")
        self.plan.items["TP-PMP-005"]["mseccfg_idx"] = idx
        assert self.m.mml == 1 and self.m.mmwp == 0 and self.m.rlb == self.plan.rlb
        blocks = [self.p4_tp005, lambda: self.tp003("mml1"), self.p4_tp007]
        rng.shuffle(blocks)
        for blk in blocks:
            blk()
            self.check_mml_safety()

    def check_mml_safety(self):
        """Every active entry other than the code rule lies inside the safety window; the code rule is intact."""
        assert self.m.cfg[0] == cfg_byte(1, A_TOR, 1, 0, 1), "code rule byte changed"
        for e in range(1, NUM_REGIONS):
            a = (self.m.cfg[e] >> 3) & 3
            if a != A_OFF:
                assert self.m.addr[e] <= SAFE_MAX_WORD, f"entry {e} active outside the window under MML"

    def p4_tp005(self):
        rng, meta = self.rng, self.plan.items["TP-PMP-005"]
        meta["rw01_bytes"] = []             # (report idx, N, lane, written byte)
        cands = [e for e in range(1, NUM_REGIONS) if not self.m.locked(e)]
        for e in rng.sample(cands, min(len(cands), rng.randint(6, 12))):
            n, ln = divmod(e, 4)
            a = rng.choice([A_OFF, A_NA4, A_NAPOT] + ([A_TOR] if e >= 1 else []))
            if a == A_NAPOT:
                self.csr_op("csrrw", pmpaddr(e), self.window_napot(), "TP-PMP-005", f"e{e} napot addr")
            l = rng.randrange(2) if self.m.rlb else 0
            b = cfg_byte(l, a, rng.randrange(2), 1, 0)
            # csrrs only over a clear byte so the combined entry byte is exactly the RW=01 row under test
            form = rng.choice(["csrrw", "csrrs"]) if self.m.cfg[e] == 0 else "csrrw"
            operand = self.cfg_word_with(n, ln, b) if form == "csrrw" else (b << (8 * ln))
            comb = self.m.combined(form, pmpcfg(n), operand)
            written = (comb >> (8 * ln)) & 0xFF
            assert written == b
            _o, idx = self.csr_op(form, pmpcfg(n), operand, "TP-PMP-005", f"e{e} rw01 mml1 {form}", red_bits=cfg_bits(ln, 2))
            meta["rw01_bytes"].append((idx, n, ln, written))
            self.filler(2)

    def p4_tp007(self):
        ok = lambda e: e != 0   # noqa: E731
        self.tp007("mml1", self.rng.randint(10, 15), ok)

    # --- end, handler, stubs, data ------------------------------------------------------------------
    def p5_end(self):
        self.emit(f"  li   gp, {TOHOST_PASS}")
        self.emit("  la   t5, tohost")
        self.emit("  sw   gp, 0(t5)")
        self.emit("1:")
        self.emit("  j    1b")

    def handler_and_stubs(self):
        self.in_main = False
        a = self.aux
        a += ["", "# M-mode trap handler (mtvec base, 256-byte aligned): one record word per trap to the report",
              "# channel, then skip the U instruction (illegal / load / store fault), resume at ra (fetch fault at a",
              f"# probe word) or return to M at s8 (ecall). A trap taken in M-mode is a program failure (tohost {TOHOST_FAIL}).",
              ".align 8", "gen_trap_vec:",
              "  csrr t0, mcause", "  csrr t1, mepc", "  csrr t2, mstatus",
              "  srli t2, t2, 11", "  andi t2, t2, 3",
              "  li   t3, 3", "  beq  t2, t3, gen_trap_m_fail",
              "  slli t2, t2, 8",
              f"  li   t3, {CAUSE_IFETCH}", "  beq  t0, t3, 1f",
              "  sub  t3, t1, s9", "  j    2f",
              "1:", "  sub  t3, t1, s2",
              "2:", "  srli t3, t3, 2", "  andi t3, t3, 0xff",
              "  slli t0, t0, 16", "  or   t0, t0, t2", "  or   t0, t0, t3",
              "  li   t2, GEN_MM_EOT_ADDR", "  sw   t0, 0(t2)",
              "  csrr t0, mcause",
              f"  li   t3, {CAUSE_ECALL_U}", "  beq  t0, t3, 3f",
              f"  li   t3, {CAUSE_IFETCH}", "  beq  t0, t3, 4f",
              "  addi t1, t1, 4", "  csrw mepc, t1", "  mret",
              "4:", "  csrw mepc, ra", "  mret",
              "3:", "  csrw mepc, s8", f"  li   t0, 0x{MPP_MASK:x}", "  csrs mstatus, t0", "  mret",
              "gen_trap_m_fail:",
              "  slli t0, t0, 16", "  slli t2, t2, 8", "  or   t0, t0, t2",
              "  li   t2, GEN_MM_EOT_ADDR", "  sw   t0, 0(t2)",
              f"  li   gp, {TOHOST_FAIL}", "  la   t5, tohost", "  sw   gp, 0(t5)",
              "5:", "  j    5b",
              "", "# U-mode code area: one NAPOT region (L=0, RWX=111) covers it; fixed-size instructions so the",
              "# handler's record carries the index of the trapping instruction. The labels are global so the",
              "# image's symbol table (prog.sym.json) carries the layout the expectations resolve from.",
              f".align {UCODE_ALIGN_BITS}", ".globl gen_u_code", "gen_u_code:", ".option push", ".option norvc",
              "gen_ustub_load:", "  lw   s5, 0(s2)", "  lw   s7, 0(s3)", "  ecall",
              "gen_ustub_store:", "  sw   s6, 0(s2)", "  sw   s6, 0(s3)", "  ecall",
              "gen_ustub_fetch:", "  jalr ra, 0(s2)", "  jalr ra, 0(s3)", "  ecall",
              "gen_ustub_csr:"]
        a += [f"  {asm}" for asm, _f, _c, _w in self.u_attempts]
        # pad the U code block to its NAPOT size so .data (the probe pool) starts outside the region
        a += ["  ecall", ".option pop", f".align {UCODE_ALIGN_BITS}", ".globl gen_text_end", "gen_text_end:"]
        assert 12 * 3 + 4 * (len(self.u_attempts) + 1) <= (1 << UCODE_ALIGN_BITS), "U code area overflow"

    def data_section(self):
        d = ["", ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
             f".align {POOL_ALIGN_BITS}", "# probe pool: data pairs hold distinct patterns, code pairs hold c.addi s5,1 ; c.jr ra",
             ".globl gen_probe_pool", "gen_probe_pool:"]
        d += [f"  .word 0x{w:08x}" for w, _k in self.pool]
        d += [".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {self.plan.min_retired}"]
        return d

    def build(self):
        self.p0_setup()
        blocks = [self.p1_tp001, self.p1_tp002, lambda: self.tp003("mml0"), self.p1_tp004,
                  lambda: self.tp007("mml0", 20, lambda e: True)]
        self.rng.shuffle(blocks)
        for blk in blocks:
            blk()
        assert all(not ((c >> 7) & 1) for c in self.m.cfg) and self.m.read(CSR_MSECCFG) & 3 == 0, "P1 must leave no lock and no MML/MMWP"
        self.reset_cfgs("TP-PMP-008", "pre-U")
        self.set_u_code_region("TP-PMP-008")
        u_blocks = [self.p2_tp008, self.p2_tp006]
        self.rng.shuffle(u_blocks)
        for blk in u_blocks:
            blk()
        self.p3_lock_step()
        self.p4_mml_phase()
        self.p5_end()
        self.handler_and_stubs()
        assert self.red_target is None or self.plan.red_note, "red fixture: the deviation site was not emitted"
        self.plan.red_sites = self.red_sites
        header = ['# gen_pmp_csr_warl: generated per-seed program of gen_test_pmp_csr_warl (seed %d%s).' % (self.plan.seed, ", RED fixture " + self.plan.red_item if self.plan.red else ""),
                  "# Generator: dv/auto_dv/tests/gen_programs/gen_pmp_csr_warl_prog.py (do not edit; regenerate).",
                  '.include "gen_mmio_map.h"', ".section .text", ".globl _start", "_start:"]
        self.plan.lines = header + self.main + self.aux + self.data_section()
        return self.plan


def plan(seed, red=False, red_item=None):
    """The green plan of a seed, or the red fixture: the same expectations with one program deviation of
    one item (red_item, else drawn with the item's site from random.Random(f"{seed}:red"))."""
    green = Gen(seed).build()
    if not red:
        return green
    rng = random.Random(f"{int(seed)}:{RED_RNG_TAG}")
    item = red_item or rng.choice(RED_ITEMS)
    assert item in RED_ITEMS, f"red: unknown item {item}"
    sites = green.red_sites[item]
    assert sites, f"red: no deviation site for {item} at seed {seed}"
    p = Gen(seed, red_target=(item, rng.choice(sites))).build()
    assert p.signature() == green.signature() and p.rlb == green.rlb, "red: the expectations moved"
    return p


def emit(p):
    text = "\n".join(p.lines) + "\n"
    assert all(ord(ch) < 128 for ch in text), "generated program is not ASCII"
    return text


def check_spike_log(p, log_path, bases):
    """Host check of the model against a standalone Spike run (--log-commits): the sequence of words
    stored to the EOT MMIO register must equal the plan's expected reports (bases from the symbol table).
    Returns (stored words, [(idx, expected, got)] mismatches)."""
    import re
    eot = MEMORY_MAP["eot_addr"]
    pat = re.compile(r"mem 0x%08x 0x([0-9a-f]{8})" % eot)
    got = [int(m.group(1), 16) for m in pat.finditer(Path(log_path).read_text())]
    bad = []
    for i in range(p.k):
        exp = p.expected(i, bases)
        if i >= len(got):
            bad.append((i, exp, None))
        elif exp != got[i]:
            bad.append((i, exp, got[i]))
    return got, bad


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
        print(f"seed={p.seed} red={p.red} rlb={p.rlb} k={p.k} min_retired={p.min_retired} lines={len(p.lines)} per_item={per_item}"
              + f" red_sites={ {k: len(v) for k, v in p.red_sites.items()} }"
              + (f" red_item={p.red_item} red_note={p.red_note}" if p.red else ""))
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
