#!/usr/bin/env python3
"""gen_pmc_ctrl_prog: per-seed program generator of gen_test_pmc_ctrl (plan group gen_pmc_ctrl, items TP-PMC-022..033,
056, 057 of dv/auto_dv/docs/gen_test_plan.md, AREA PMC: mcountinhibit / mcounteren control of the counters).

plan(seed, red=False, red_item=None, pin="on") draws the scenario from random.Random(f"{seed}:program:pmc_ctrl") and returns
a Plan: the assembly lines, the ordered expected report words, k, min_retired and per-item metadata for the fire-checks.
`pin` is the value of the static TB knob knob_mcounteren_writable (on / off / invalid): it changes the EXPECTATIONS of the
mcounteren writes and of everything gated by mcounteren (applied when on, dropped when off or invalid), never the program
text, so one image serves every pin value.

Semantics modelled (privileged spec Zicntr / Zihpm counter and control CSRs; the plan's PMC parameter shorthands (HPM_LAST, HPM_CTRL_MASK) and its exact-counter separation rule;
rtl/ibex_cs_registers.sv read only as a cross-check):
  mcountinhibit / mcounteren: WARL, the writable bits are CY, IR and HPM_FIRST..HPM_LAST (HPM_CTRL_MASK); TM and the bits
  above HPM_LAST read 0; mcounteren resets to 0 and its write is dropped without a trap unless the pin is On.
  Counters: an instruction retires under the inhibit state produced by the CSR writes of every instruction up to and
  including itself (the write precedes the writeback, spec: the inhibit takes effect from the next cycle); an inhibited
  counter's delta is 0 while reads and writes keep working; a counter written while inhibited resumes from the written
  value. Exactness classes (plan TP-PMC-023): minstret, loads, stores, jumps, branches (every branch separated from a
  preceding load/store by an ALU instruction), taken branches and compressed retirements are exact per window;
  mcycle, the IF stall counter and the mul/div wait counters are bound class (lower bound from the window's
  instructions, taken transfers and stalling operations, upper bound the window's mcycle delta); the LSU stall counter
  is bound class without a floor. The speculative +1 of minstret /
  mhpmcounter10 reads is removed under the inhibit (all reads frozen equal); under IR=0 a read pair's difference equals
  the instructions retired between them, whatever the WB timing.
  Privilege: every M-mode counter CSR (mcountinhibit, mcounteren, mhpmevent*, mcycle(h), minstret(h), mhpmcounter*(h)) is
  illegal in U-mode; the U-mode aliases cycle/instret/hpmcounterN(h) are legal in U iff mcounteren[N]; the aliases
  above HPM_LAST are illegal in U (hardwired 0) and read 0 in M; every write op to the alias ranges is illegal in M and
  U (csrrs/csrrc with x0 / uimm 0 are reads); time/timeh are unimplemented (illegal everywhere); mcounteren.TM reads 0.

Report channel: csrr read-backs, counter deltas the program computes (sub after, before) and the handler's trap
records (mcause << 16 | MPP << 8 | instruction index from the armed base register s9) are stored to GEN_MM_EOT_ADDR in
program order; the test compares every word with the plan (kinds abs / range / bound). Raw counter values are never
expected (they are the comparator's consistency compares), so 024 and 033 report differences (xor / sub) of reads.

Program (M-mode unless stated, .option norvc except the compressed event windows; U episodes run in a 4 KiB PMP NAPOT
code region, mret in, ecall back through the returning handler; no trap inside a counter window):
  P0 mtvec, s0 = EOT, s1 = scratch, the U code PMP entry; P1 027 then 022 (WARL patterns), 032 (TM bit, time/timeh in
  M and U), 028 (mcounteren writes under the pin, U alias read), 026 (U access to the M-mode counter CSRs), 029 (>= 3
  masks incl. all-ones and all-zeros, U and M alias reads), 030 (unimplemented aliases in U and M), 031 (write ops to the
  alias ranges in M and U, control reads in M); P2 counters with mcounteren all-ones: 023 (each of the 12 inhibit bits
  and a random mask, 12-counter windows), 024 (IR=1 reads frozen: lw;csrr, add;csrr, csrr runs, c.lw;csrr mhpmcounter10;
  IR=0 control differences), 025 (mcycle / minstret / hpm written under the inhibit then resumed, hpm written without
  inhibit), 056 (inhibit set and cleared inside a window), 033 (inhibited but enabled alias read twice in U-mode); end.
  The item blocks of P1 and P2 are shuffled by the seed inside their phase.

Red fixtures (red=True): the PROGRAM deviates on one intent of one item, the plan keeps the green expectations, so exactly
that item's fire_tp method fails. The seed-drawn item comes from RED_ITEMS (the 13 built items; TP-PMC-057 is not built
and --red-item refuses it). Deviations: 022/027/028 one control-register write carries a flipped writable bit (restored
after the read-back); 023 one window's inhibit write leaves the bit clear; 024 the IR inhibit is cleared before the reads;
025 the counter is written with a different value; 026 one illegal U access is replaced by an ebreak (the record carries
cause 3 for the expected 2); 029/031/032 one trapping instruction and one non-trapping instruction of a block swap
places in the program (the record's index moves); 030 one M-mode read of an unimplemented
alias reads an implemented one (nonzero); 033 the inhibit bit is cleared before the U episode; 056 the mid-window inhibit
write carries no bit.

CLI: python3 gen_pmc_ctrl_prog.py --seed N --out <file.S> [--red [--red-item TP-PMC-0nn]] [--pin on|off|invalid] [--summary]
"""
import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dv.auto_dv.tests.gen_programs.gen_pmp_csr_warl_prog import (  # noqa: E402
    A_NAPOT, CAUSE_ECALL_U, CAUSE_ILLEGAL, MPP_MASK, Report, UIMM_FORMS, cfg_byte, record, wchoice)
from dv.auto_dv.tests.gen_programs.gen_prog_const import (  # noqa: E402
    CONFIG_NAME, CSR, TOHOST_FAIL, TOHOST_PASS, hpmcounter, mhpmcounter, mhpmevent)

RNG_TAG = "program:pmc_ctrl"
RED_RNG_TAG = "red"
RED_SITE_TAG = "red:site"
ITEMS = ("TP-PMC-022", "TP-PMC-023", "TP-PMC-024", "TP-PMC-025", "TP-PMC-026", "TP-PMC-027", "TP-PMC-028", "TP-PMC-029",
         "TP-PMC-030", "TP-PMC-031", "TP-PMC-032", "TP-PMC-033", "TP-PMC-056", "TP-PMC-057")
NOT_BUILT = ("TP-PMC-057",)
RED_ITEMS = tuple(i for i in ITEMS if i not in NOT_BUILT)
PINS = ("on", "off", "invalid")


def _hpm_num():
    """MHPMCounterNum from the one configuration source (ibex_configs.yaml, as util/ibex_config.py reads it)."""
    import yaml
    cfg = yaml.safe_load((ROOT / "ibex_configs.yaml").read_text())[CONFIG_NAME]
    return int(cfg["MHPMCounterNum"])


HPM_NUM = _hpm_num()
CY, TM, IR, HPM_FIRST = 0, 1, 2, 3          # counter indices of the spec (cycle, time, instret, hpmcounter3)
HPM_LAST = HPM_FIRST + HPM_NUM - 1
HPM_CTRL_MASK = ((1 << (HPM_FIRST + HPM_NUM)) - 1) & ~(1 << TM) & 0xFFFFFFFF
# implemented counters by index (the plan's classes): 0 mcycle, 2 minstret, 3 LSU stall, 4 IF stall, 5 loads, 6 stores,
# 7 jumps, 8 branches, 9 taken branches, 10 compressed, 11 mul wait, 12 div wait
COUNTERS = (CY, IR) + tuple(range(HPM_FIRST, HPM_LAST + 1))
CTR_NAMES = {0: "mcycle", 2: "minstret", 3: "lsu", 4: "if", 5: "ld", 6: "st", 7: "jmp", 8: "br", 9: "tk", 10: "rc", 11: "mul", 12: "div"}
EXACT = (2, 5, 6, 7, 8, 9, 10)               # exact class under the separation rule: no branch, mulh or div directly follows a load or store
BOUND = (0, 3, 4, 11, 12)                    # bound class: lo <= delta <= the window's mcycle delta
ALIAS_MAX = 31                               # hpmcounter31: last alias of the read-only range
UNIMPL_KS = tuple(range(HPM_NUM, ALIAS_MAX - HPM_FIRST + 1))   # k with hpmcounter(3 + k) unimplemented
CSR_MCOUNTEREN, CSR_MCOUNTINHIBIT = CSR["mcounteren"], CSR["mcountinhibit"]
CSR_TIME, CSR_TIMEH = hpmcounter(TM), hpmcounter(TM, high=True)
REG_FORMS = ("csrrw", "csrrs", "csrrc")
ALL_FORMS = REG_FORMS + UIMM_FORMS
OP_CLASS = {"csrrw": "wr", "csrrwi": "wr", "csrrs": "set", "csrrsi": "set", "csrrc": "clr", "csrrci": "clr"}
UCODE_ALIGN_BITS = 12                        # U code area: one 4 KiB NAPOT
UCODE_NAPOT_ONES = UCODE_ALIGN_BITS - 3
U_ENTRY = 0
SCRATCH_WORDS = 16                           # window load/store area (s1 + 0..60)
SAVE_OFF = 4 * SCRATCH_WORDS                 # before-read save area (12 words)
MARK_029 = 0x02900A11
SENT_A, SENT_B = 0x5A5A0001, 0x5A5A0002      # 033 sentinels (kept when the U reads trap)
MPP_M = 3
CTR_REGS = ["a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "t2", "t3", "t4", "t5"]
FILLER_REGS = ["s2", "s3", "s4", "s5", "s6", "s7"]

# Layer-1 distributions transcribed from the items (W1 register operands, W2 immediates, W10 window lengths, W13 ops)
W_PATTERN_VALUE = {"masked": 40, "full": 40, "hi_only": 20}      # random-pattern operand shape
W_WALK_OP = {"wr": 4, "set": 3, "clr": 3}
W_EVENTS = {5: 30, 6: 25, 7: 20, 8: 15, 9: 10}                     # events per class in a window (W10 counter window)
W_CTR_025 = {5: 3, 6: 3, 7: 2, 8: 2, 9: 2, 10: 2}
W_056_N = {5: 1, 6: 1, 8: 1, 10: 1}
W_033_N = {0: 2, 2: 2, 7: 2, 8: 2, 9: 2, 11: 1, 12: 1}             # memory-free classes (U-mode has no data region)


def csr_hex(csr):
    return f"0x{csr:03x}"


def alias(idx, high=False):
    """U-mode alias CSR of counter idx (cycle 0xC00 + idx, high half 0xC80 + idx)."""
    return hpmcounter(idx, high)


def mcsr(idx, high=False):
    """M-mode counter CSR of counter idx."""
    return mhpmcounter(idx, high)


@dataclass
class Plan:
    seed: int
    red: bool
    pin: str
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

    def applied(self):
        return self.pin == "on"

    def expected(self, idx):
        """abs: the value; range: (lo, hi); bound: (lo, ref_idx) with hi = the expected word at ref_idx (None: no upper)."""
        return self.reports[idx].value

    def matches(self, idx, word, reports):
        r = self.reports[idx]
        if r.kind == "abs":
            return word == r.value
        if r.kind == "range":
            lo, hi = r.value
            return lo <= word <= hi
        lo, ref = r.value
        hi = None if ref is None else (reports[ref] if ref < len(reports) else None)
        return word >= lo and (hi is None or word <= hi)

    def describe(self, idx):
        r = self.reports[idx]
        if r.kind == "abs":
            return f"0x{r.value:08x}"
        if r.kind == "range":
            return f"[0x{r.value[0]:x}..0x{r.value[1]:x}]"
        return f">= {r.value[0]}" + (f" and <= word {r.value[1]}" if r.value[1] is not None else "")

    def item_indices(self, item):
        return [r.idx for r in self.reports if r.item == item]

    def signature(self):
        return [(r.item, r.kind, r.value) for r in self.reports]


class Model:
    """mcountinhibit / mcounteren state and the WARL rules; the pin gates mcounteren writes."""

    def __init__(self, pin):
        self.inh = 0
        self.en = 0
        self.pin = pin

    def read(self, csr):
        return self.inh if csr == CSR_MCOUNTINHIBIT else self.en

    @staticmethod
    def post_op(form, old, operand):
        if form in ("csrrw", "csrrwi"):
            return operand & 0xFFFFFFFF
        if form in ("csrrs", "csrrsi"):
            return old | operand
        return old & ~operand & 0xFFFFFFFF

    def op(self, form, csr, operand):
        old = self.read(csr)
        post = self.post_op(form, old, operand) & HPM_CTRL_MASK
        if csr == CSR_MCOUNTINHIBIT:
            self.inh = post
        elif self.pin == "on":
            self.en = post
        return old

    def u_alias_legal(self, idx):
        return bool((self.en >> idx) & 1) if idx <= HPM_LAST and idx != TM else False


class Gen:
    def __init__(self, seed, pin="on", red_target=None):
        assert pin in PINS, f"pin {pin} not in {PINS}"
        self.rng = random.Random(f"{int(seed)}:{RNG_TAG}")
        self.red_rng = random.Random(f"{int(seed)}:{RED_SITE_TAG}")
        self.m = Model(pin)
        self.plan = Plan(seed=seed, red=red_target is not None, pin=pin)
        self.plan.items = {tp: {} for tp in ITEMS}
        self.main, self.aux = [], []
        self.in_main = True
        self.stream = []             # (inh state after the instruction, {counter idx: increment}) per main-flow instruction
        self.u_len = 0               # U code words emitted (4 bytes each)
        self.u_n = 0
        self.arm_n = 0
        self.red_target = red_target
        self.red_sites = {tp: [] for tp in RED_ITEMS}
        self.site_serial = 0
        self.compressed_ok = False   # inside a .option rvc window

    # --- emission and the instruction stream --------------------------------------------------------------------
    def emit(self, line, events=None):
        """One assembly line; a main-flow instruction enters the stream with its counter events (minstret and the
        per-instruction cycle floor implied) under the inhibit state after its own CSR write."""
        (self.main if self.in_main else self.aux).append(line)
        text = line.strip()
        if text and not text.startswith((".", "#")) and not text.endswith(":"):
            if self.in_main:
                self.plan.min_retired += 1
                ev = {2: 1, 0: 1}
                ev.update(events or {})
                self.stream.append((self.m.inh, ev))
            else:
                self.u_len += 1

    def li(self, reg, value):
        v = value & 0xFFFFFFFF
        self.emit(f"  li   {reg}, 0x{v:08x}")
        signed = v - (1 << 32) if v & 0x80000000 else v
        if not (-2048 <= signed <= 2047) and v & 0xFFF:
            self.stream.append((self.m.inh, {2: 1, 0: 1}))   # li expands to lui + addi (lui alone when the low 12 bits are 0)
            self.plan.min_retired += 1

    def report_reg(self, reg, item, label, kind="abs", value=0):
        self.emit(f"  sw   {reg}, 0(s0)", {6: 1})
        r = Report(item, label, kind, value, len(self.plan.reports))
        self.plan.reports.append(r)
        return r.idx

    def expect_record(self, item, label, value):
        r = Report(item, label, "abs", value, len(self.plan.reports))
        self.plan.reports.append(r)
        return r.idx

    def filler(self, n_max=2, n_min=0):
        for _ in range(self.rng.randint(n_min, n_max)):
            rd, rs = self.rng.choice(FILLER_REGS), self.rng.choice(FILLER_REGS)
            kind = self.rng.choice(["addi", "xori", "andi", "ori", "slli", "srli", "add", "sub", "xor", "or", "and"])
            if kind in ("addi", "xori", "andi", "ori"):
                self.emit(f"  {kind} {rd}, {rs}, {self.rng.randint(-2048, 2047)}")
            elif kind in ("slli", "srli"):
                self.emit(f"  {kind} {rd}, {rs}, {self.rng.randint(0, 31)}")
            else:
                self.emit(f"  {kind}  {rd}, {rs}, {self.rng.choice(FILLER_REGS)}")

    def alu(self):
        self.filler(1, 1)

    def red_here(self, item):
        serial, self.site_serial = self.site_serial, self.site_serial + 1
        self.red_sites[item].append(serial)
        if self.red_target == (item, serial):
            self.plan.red_item = item
            return True
        return False

    # --- control-register ops ---------------------------------------------------------------------------------------
    def ctrl_op(self, form, csr, operand, item, label, dev=None):
        """One op on mcountinhibit / mcounteren with the read-back report; dev: the program operand of a red."""
        prog_val = operand if dev is None else dev
        if form in REG_FORMS:
            self.li("t0", prog_val)
        old = self.m.op(form, csr, operand)        # the op retires under the state its own write produces
        if form in REG_FORMS:
            self.emit(f"  {form} t1, {csr_hex(csr)}, t0")
        else:
            self.emit(f"  {form} t1, {csr_hex(csr)}, {prog_val}")
        self.emit(f"  csrr t1, {csr_hex(csr)}")
        idx = self.report_reg("t1", item, f"{label} readback {csr_hex(csr)}", "abs", self.m.read(csr))
        if dev is not None:
            self.plan.red_note = f"{item} {label}: program {form} {csr_hex(csr)} with 0x{dev:08x} for planned 0x{operand:08x}, read-back idx {idx}"
            self.li("t0", self.m.read(csr))
            self.emit(f"  csrw {csr_hex(csr)}, t0")
        return old, idx

    def set_inhibit(self, value, item, label):
        return self.ctrl_op("csrrw", CSR_MCOUNTINHIBIT, value, item, label)[1]

    def set_enable(self, value, item, label):
        return self.ctrl_op("csrrw", CSR_MCOUNTEREN, value, item, label)[1]

    def flip_dev(self, form, csr, operand):
        """The operand with one writable bit flipped when that changes the modelled read-back (None otherwise)."""
        if csr == CSR_MCOUNTEREN and self.m.pin != "on":
            return None
        bits = [b for b in COUNTERS]
        self.red_rng.shuffle(bits)
        old = self.m.read(csr)
        for b in bits:
            if form in UIMM_FORMS and b > 4:
                continue
            dev = operand ^ (1 << b)
            if Model.post_op(form, old, dev) & HPM_CTRL_MASK != Model.post_op(form, old, operand) & HPM_CTRL_MASK:
                return dev
        return None

    # --- P0 -------------------------------------------------------------------------------------------------------
    def p0(self):
        self.emit("  la   t0, gen_trap_vec")
        self.emit("  ori  t0, t0, 1")          # vectored mode bit: Ibex forces it, Spike stores it, both read back base|1
        self.emit("  csrw mtvec, t0")
        self.emit("  li   s0, GEN_MM_EOT_ADDR")
        self.emit("  la   s1, gen_scratch")
        self.emit("  li   s9, 0")
        # U code region: NAPOT L=0 RWX over the 4 KiB U code area (M-mode ignores it: MML=0)
        self.emit("  la   t0, gen_u_code")
        self.emit("  srli t0, t0, 2")
        self.emit(f"  ori  t0, t0, 0x{(1 << UCODE_NAPOT_ONES) - 1:x}")
        self.emit(f"  csrw pmpaddr{U_ENTRY}, t0")
        self.li("t0", cfg_byte(0, A_NAPOT, 1, 1, 1) << (8 * (U_ENTRY % 4)))
        self.emit(f"  csrw pmpcfg{U_ENTRY // 4}, t0")
        for i, r in enumerate(FILLER_REGS):
            self.li(r, 0x100 * (i + 1) + 1)   # nonzero, distinct: division and multiply operands of the windows
        self.li("s10", 1)                       # s10 < s11: the taken-branch compare pair (never touched by fillers)
        self.li("s11", 2)
        for w in range(SCRATCH_WORDS):
            self.emit(f"  sw   s2, {4 * w}(s1)", {6: 1})

    # --- U-mode episodes and armed M-mode blocks -------------------------------------------------------------------
    def u_episode(self, body, item, label, prog_body=None):
        """Run `body` (list of (asm, expected record value or None)) in U-mode; the handler records every trap with the
        instruction index from the stub base; the closing ecall returns to M. Returns the record indices. prog_body: the
        text a red fixture emits in place of body (same length; the expectations stay body's)."""
        self.u_n += 1
        stub, res = f"gen_ustub_{self.u_n}", f"gen_res_{self.u_n}"
        self.emit(f"  la   s9, {stub}")
        self.emit(f"  la   s8, {res}")
        self.emit("  csrw mepc, s9")
        self.li("t0", MPP_MASK)
        self.emit("  csrc mstatus, t0")
        self.emit("  mret")
        self.in_main = False
        self.aux.append(f"{stub}:")
        idxs = []
        i = 0                                    # instruction index from the stub base (labels do not count)
        for k, (asm, rec) in enumerate(body):
            self.emit(f"  {(prog_body or body)[k][0]}")
            if asm.strip().endswith(":"):
                continue
            if rec is not None:
                idxs.append(self.expect_record(item, f"{label} U idx {i}: {asm.strip()}", record(rec, i)))
            i += 1
        self.emit("  ecall")
        idxs.append(self.expect_record(item, f"{label} U ecall", record(CAUSE_ECALL_U, i)))
        self.in_main = True
        self.emit(f"{res}:")
        self.emit("  li   s9, 0")
        return idxs

    def m_block(self, body, item, label, prog_body=None):
        """Armed M-mode block (norvc, s9 = base): every trapping instruction is recorded with its index and skipped;
        prog_body: a red fixture's text in place of body (same length; the expectations stay body's)."""
        self.arm_n += 1
        base = f"gen_marm_{self.arm_n}"
        self.emit(f"  la   s9, {base}")
        self.emit(f"{base}:")
        idxs = []
        for i, (asm, rec) in enumerate(body):
            self.emit(f"  {(prog_body or body)[i][0]}")
            if rec is not None:
                idxs.append(self.expect_record(item, f"{label} M idx {i}: {asm.strip()}", record(rec, i, MPP_M)))
        self.emit("  li   s9, 0")
        return idxs

    @staticmethod
    def swap_dev(body, i, j):
        body = list(body)
        body[i], body[j] = body[j], body[i]
        return body

    def red_swap(self, item, body, label):
        """Red of the record-index kind: the PROGRAM has one trapping and one non-trapping entry of the block swapped
        (the expectations stay the plan's); returns the program body or None."""
        traps = [i for i, (_a, r) in enumerate(body) if r is not None]
        frees = [i for i, (_a, r) in enumerate(body) if r is None]
        if traps and frees and self.red_here(item):
            i, j = self.red_rng.choice(traps), self.red_rng.choice(frees)
            self.plan.red_note = f"{item} {label}: instructions {i} (trapping) and {j} (legal) swap places, the record index moves"
            return self.swap_dev(body, i, j)
        return None

    # --- TP-PMC-027 / 022: WARL patterns -------------------------------------------------------------------------
    def warl_patterns(self, csr, item):
        meta = self.plan.items[item]
        meta["writes"] = []          # (idx, form, pattern class, pre, post & mask, operand)
        name = csr_hex(csr)
        self.emit(f"  csrr t1, {name}")
        meta["read_idx"] = self.report_reg("t1", item, f"plain read {name}", "abs", self.m.read(csr))
        ops = [("zeros", "csrrw"), ("ones", "csrrw"), ("ones", "csrrs"), ("ones", "csrrc"),
               ("random", "csrrw"), ("random", "csrrs"), ("random", "csrrc"), ("zeros", "csrrwi")]
        ops += [("random", self.rng.choice(ALL_FORMS)) for _ in range(self.rng.randint(1, 4))]
        walk_ops = {"wr": 0, "set": 0, "clr": 0}
        walk = []
        for b in self.rng.sample(range(32), 32):
            cls = wchoice(self.rng, W_WALK_OP)
            form = {"wr": "csrrw", "set": "csrrs", "clr": "csrrc"}[cls]
            if b < 5 and self.rng.random() < 0.4:
                form += "i"
            walk_ops[cls] += 1
            walk.append(("walking", form, b))
        for cls in walk_ops:
            if walk_ops[cls] == 0:
                walk.append(("walking", {"wr": "csrrw", "set": "csrrs", "clr": "csrrc"}[cls], self.rng.randrange(32)))
        seq = [(p, f, None) for p, f in ops] + walk
        self.rng.shuffle(seq)
        for i, (pattern, form, bit) in enumerate(seq):
            if pattern == "zeros":
                operand = 0
            elif pattern == "ones":
                operand = 0xFFFFFFFF
            elif pattern == "walking":
                operand = 1 << bit
            else:
                shape = wchoice(self.rng, W_PATTERN_VALUE)
                operand = self.rng.getrandbits(32)
                if shape == "masked":
                    operand &= HPM_CTRL_MASK
                elif shape == "hi_only":
                    operand &= ~HPM_CTRL_MASK & 0xFFFFFFFF
                if form in UIMM_FORMS:
                    operand = self.rng.randint(1, 31)
            if form in UIMM_FORMS and operand > 31:
                operand &= 31
            pre = self.m.read(csr)
            cand = self.flip_dev(form, csr, operand)
            dev = cand if cand is not None and self.red_here(item) else None
            _old, idx = self.ctrl_op(form, csr, operand, item, f"{pattern} {form}", dev=dev)
            meta["writes"].append((idx, form, pattern, pre, Model.post_op(form, pre, operand) & HPM_CTRL_MASK, operand))
            self.filler(1)
        meta["final_idx"] = self.set_inhibit(0, item, "restore 0") if csr == CSR_MCOUNTINHIBIT else self.set_enable(0, item, "restore 0")

    def tp027(self):
        self.warl_patterns(CSR_MCOUNTEREN, "TP-PMC-027")

    def tp022(self):
        self.warl_patterns(CSR_MCOUNTINHIBIT, "TP-PMC-022")

    # --- TP-PMC-032: time/timeh, TM bit ------------------------------------------------------------------------------
    def tp032(self):
        item, meta = "TP-PMC-032", self.plan.items["TP-PMC-032"]
        pre = self.m.read(CSR_MCOUNTEREN)
        _o, meta["tm_idx"] = self.ctrl_op("csrrs", CSR_MCOUNTEREN, 1 << TM, item, "TM set attempt")
        body = []
        for csr in self.rng.sample((CSR_TIME, CSR_TIMEH), 2):
            body.append((f"csrr t1, {csr_hex(csr)}", CAUSE_ILLEGAL))
            form = self.rng.choice(ALL_FORMS)
            src = f"{self.rng.randint(1, 31)}" if form in UIMM_FORMS else "t4"
            body.append((f"{form} t1, {csr_hex(csr)}, {src}", CAUSE_ILLEGAL))
        body.append(("addi t6, t6, 1", None))
        self.rng.shuffle(body)
        meta["m_body"] = list(body)
        self.li("t4", self.rng.getrandbits(32))
        meta["m_idx"] = self.m_block(body, item, "time", prog_body=self.red_swap(item, body, "M block"))
        ubody = [(f"csrr t1, {csr_hex(c)}", CAUSE_ILLEGAL) for c in self.rng.sample((CSR_TIME, CSR_TIMEH), 2)]
        ubody.append((f"csrrwi t1, {csr_hex(self.rng.choice((CSR_TIME, CSR_TIMEH)))}, {self.rng.randint(1, 31)}", CAUSE_ILLEGAL))
        meta["u_body"] = list(ubody)
        meta["u_idx"] = self.u_episode(ubody, item, "time")
        meta["pre"] = pre

    # --- TP-PMC-028: the pin -----------------------------------------------------------------------------------------
    def tp028(self):
        item, meta = "TP-PMC-028", self.plan.items["TP-PMC-028"]
        meta["writes"] = []          # (idx, form, pre, post if applied, operand)
        meta["u_reads"] = []         # (record idxs, [(alias idx, legal)])
        preset = self.rng.getrandbits(32) & HPM_CTRL_MASK
        n = self.rng.randint(3, 5)
        forms = list(REG_FORMS) + [self.rng.choice(ALL_FORMS) for _ in range(n - 3)]
        self.rng.shuffle(forms)
        _o, meta["preset_idx"] = self.ctrl_op("csrrw", CSR_MCOUNTEREN, preset, item, "preset")
        for i, form in enumerate(forms):
            operand = self.rng.randint(1, 31) if form in UIMM_FORMS else (self.rng.getrandbits(32) | (1 << self.rng.choice(COUNTERS)))
            pre = self.m.read(CSR_MCOUNTEREN)
            cand = self.flip_dev(form, CSR_MCOUNTEREN, operand)
            dev = cand if cand is not None and self.red_here(item) else None
            _o, idx = self.ctrl_op(form, CSR_MCOUNTEREN, operand, item, f"w{i} {form}", dev=dev)
            meta["writes"].append((idx, form, pre, Model.post_op(form, pre, operand) & HPM_CTRL_MASK, operand))
            picks = self.rng.sample((CY, IR, HPM_FIRST, HPM_LAST), 2)
            body = [(f"csrr t1, {csr_hex(alias(a))}", None if self.m.u_alias_legal(a) else CAUSE_ILLEGAL) for a in picks]
            recs = self.u_episode(body, item, f"w{i} alias read")
            meta["u_reads"].append((recs, [(a, self.m.u_alias_legal(a)) for a in picks]))

    # --- TP-PMC-026: U access to the M-mode counter CSRs ----------------------------------------------------------------
    def tp026(self):
        item, meta = "TP-PMC-026", self.plan.items["TP-PMC-026"]
        self.set_enable(0xFFFFFFFF, item, "mcounteren all-ones")
        k = self.rng.randrange(HPM_NUM)
        classes = {"en": CSR_MCOUNTEREN, "inh": CSR_MCOUNTINHIBIT, "event": mhpmevent(HPM_FIRST + self.rng.randrange(29)),
                   "mcycle": mcsr(CY), "minstret": mcsr(IR), "hpm": mcsr(HPM_FIRST + k), "mcycleh": mcsr(CY, True),
                   "minstreth": mcsr(IR, True), "hpmh": mcsr(HPM_FIRST + self.rng.randrange(29), True)}
        acc = [(c, w) for c in classes for w in (False, True)]
        acc += [(self.rng.choice(list(classes)), self.rng.random() < 0.5) for _ in range(self.rng.randint(0, 4))]
        self.rng.shuffle(acc)
        body, meta["accesses"] = [], []
        for cls, write in acc:
            csr = classes[cls]
            if write:
                form = self.rng.choice(ALL_FORMS)
                src = f"{self.rng.randint(1, 31)}" if form in UIMM_FORMS else self.rng.choice(("t4", "t5"))
                asm = f"{form} t1, {csr_hex(csr)}, {src}"
            else:
                form, asm = "csrr", f"csrr t1, {csr_hex(csr)}"
            body.append((asm, CAUSE_ILLEGAL))
            meta["accesses"].append((cls, write, form))
        prog_body = None
        if self.red_here(item):
            i = self.red_rng.randrange(len(body))
            prog_body = list(body)
            prog_body[i] = ("ebreak", CAUSE_ILLEGAL)      # the program traps with cause 3 where the plan expects the illegal-instruction record
            self.plan.red_note = f"{item}: U access {i} ({body[i][0]}) replaced by ebreak (record cause 3 for the expected 2)"
        self.li("t4", self.rng.getrandbits(32))
        self.li("t5", self.rng.getrandbits(32))
        inh_pre, en_pre = self.m.inh, self.m.en
        meta["rec_idx"] = self.u_episode(body, item, "M-mode CSR from U", prog_body=prog_body)
        for csr, lbl in ((CSR_MCOUNTINHIBIT, "inh"), (CSR_MCOUNTEREN, "en")):
            self.emit(f"  csrr t1, {csr_hex(csr)}")
            meta[f"{lbl}_after"] = self.report_reg("t1", item, f"{lbl} unchanged after the U episode", "abs", self.m.read(csr))
        assert (self.m.inh, self.m.en) == (inh_pre, en_pre)

    # --- TP-PMC-029: per-bit gating of the aliases -------------------------------------------------------------------
    def tp029(self):
        item, meta = "TP-PMC-029", self.plan.items["TP-PMC-029"]
        meta["masks"] = []
        masks = [0xFFFFFFFF, 0] + [self.rng.getrandbits(32) & HPM_CTRL_MASK for _ in range(self.rng.randint(1, 3))]
        self.rng.shuffle(masks)
        for mi, mask in enumerate(masks):
            _o, idx = self.ctrl_op("csrrw", CSR_MCOUNTEREN, mask, item, f"mask {mi}")
            reads = [(a, h) for a in COUNTERS for h in (False, True)]
            self.rng.shuffle(reads)
            body = [(f"csrr t1, {csr_hex(alias(a, h))}", None if self.m.u_alias_legal(a) else CAUSE_ILLEGAL) for a, h in reads]
            recs = self.u_episode(body, item, f"mask {mi}", prog_body=self.red_swap(item, body, f"mask {mi}"))
            m_reads = list(reads)
            self.rng.shuffle(m_reads)
            for a, h in m_reads:
                self.emit(f"  csrr t1, {csr_hex(alias(a, h))}")
            self.li("t1", MARK_029)
            mark = self.report_reg("t1", item, f"mask {mi} M reads done", "abs", MARK_029)
            meta["masks"].append({"mask": self.m.en, "mask_idx": idx, "recs": recs, "reads": reads, "mark_idx": mark})

    # --- TP-PMC-030: aliases above HPM_LAST ------------------------------------------------------------------------------
    def tp030(self):
        item, meta = "TP-PMC-030", self.plan.items["TP-PMC-030"]
        self.set_enable(0xFFFFFFFF, item, "mcounteren all-ones")
        ks = self.rng.sample(UNIMPL_KS, self.rng.randint(6, 9))
        body = [(f"csrr t1, {csr_hex(alias(HPM_FIRST + k, h))}", CAUSE_ILLEGAL) for k in ks for h in (False, True)]
        self.rng.shuffle(body)
        meta["u_n"] = len(body)
        meta["u_idx"] = self.u_episode(body, item, "unimplemented alias")
        meta["m_reads"] = []         # (idx, k, high)
        m_ks = self.rng.sample(UNIMPL_KS, self.rng.randint(6, 9))
        reads = [(k, h) for k in m_ks for h in (False, True)]
        self.rng.shuffle(reads)
        red_i = self.red_rng.randrange(len(reads)) if self.red_here(item) else None
        for i, (k, h) in enumerate(reads):
            csr = alias(HPM_FIRST + k, h)
            if i == red_i:
                csr = alias(CY)              # implemented alias: nonzero read
                self.plan.red_note = f"{item}: M read {i} of hpmcounter{HPM_FIRST + k}{'h' if h else ''} reads cycle instead"
            self.emit(f"  csrr t1, {csr_hex(csr)}")
            meta["m_reads"].append((self.report_reg("t1", item, f"M read hpmcounter{HPM_FIRST + k}{'h' if h else ''}", "abs", 0), k, h))

    # --- TP-PMC-031: write ops to the alias ranges ----------------------------------------------------------------------
    def tp031(self):
        item, meta = "TP-PMC-031", self.plan.items["TP-PMC-031"]
        mask = self.rng.getrandbits(32) & HPM_CTRL_MASK
        _o, meta["mask_idx"] = self.ctrl_op("csrrw", CSR_MCOUNTEREN, mask, item, "random mcounteren")
        ku = self.rng.choice(UNIMPL_KS)
        floor_m = [(CY, False, "csrrw"), (IR, False, "csrrs"), (HPM_FIRST, False, "csrrc"), (CY, True, "csrrw"), (HPM_FIRST + ku, True, "csrrw")]
        floor_u = [(CY, False, "csrrw"), (HPM_FIRST + ku, False, "csrrw")]
        extra = lambda: (self.rng.randrange(ALIAS_MAX + 1), self.rng.random() < 0.5, self.rng.choice(ALL_FORMS))
        m_ops = floor_m + [extra() for _ in range(self.rng.randint(3, 6))]
        u_ops = floor_u + [extra() for _ in range(self.rng.randint(2, 5))]
        for f in ALL_FORMS:                                   # every op class in each privilege
            if f not in {o[2] for o in m_ops}:
                m_ops.append((self.rng.randrange(ALIAS_MAX + 1), False, f))
            if f not in {o[2] for o in u_ops}:
                u_ops.append((self.rng.randrange(ALIAS_MAX + 1), False, f))
        self.rng.shuffle(m_ops)
        self.rng.shuffle(u_ops)

        def op_asm(a, h, form):
            src = f"{self.rng.randint(1, 31)}" if form in UIMM_FORMS else self.rng.choice(("t4", "t5"))
            return f"{form} t1, {csr_hex(alias(a, h))}, {src}"

        body = [(op_asm(a, h, f), CAUSE_ILLEGAL) for a, h, f in m_ops]
        n_ctrl = self.rng.randint(1, 3)
        ctrl = []
        for _ in range(n_ctrl):
            a, h = self.rng.choice(COUNTERS), self.rng.random() < 0.5
            f = self.rng.choice(("csrrs", "csrrc", "csrrsi", "csrrci"))
            ctrl.append((f"{f} t1, {csr_hex(alias(a, h))}, {'0' if f in UIMM_FORMS else 'x0'}", None))
        body += ctrl
        self.rng.shuffle(body)
        meta["m_ops"], meta["u_ops"], meta["n_ctrl"] = m_ops, u_ops, n_ctrl
        self.li("t4", self.rng.getrandbits(32) | 1)
        self.li("t5", self.rng.getrandbits(32) | 2)
        meta["m_idx"] = self.m_block(body, item, "alias write", prog_body=self.red_swap(item, body, "M block"))
        ubody = [(op_asm(a, h, f), CAUSE_ILLEGAL) for a, h, f in u_ops]
        meta["u_idx"] = self.u_episode(ubody, item, "alias write")

    # --- counter windows ---------------------------------------------------------------------------------------------------
    def window(self, spec, start_alu=True):
        """Straight-line event window: spec = {counter idx: events}; 5 loads, 6 stores, 7 jumps, 8 branches (taken and
        not), 9 taken branches (beyond the branch set), 10 compressed, 11 mulh, 12 div; a branch, mulh or div never
        follows a load/store directly."""
        ops = []
        for c, n in spec.items():
            ops += [c] * n
        self.rng.shuffle(ops)
        if start_alu:
            self.alu()
        last_mem = False
        for c in ops:
            if c in (8, 9, 11, 12) and last_mem:
                self.alu()
            last_mem = False
            if c == 5:
                self.emit(f"  lw   {self.rng.choice(FILLER_REGS)}, {4 * self.rng.randrange(SCRATCH_WORDS)}(s1)", {5: 1})
                last_mem = True
            elif c == 6:
                self.emit(f"  sw   {self.rng.choice(FILLER_REGS)}, {4 * self.rng.randrange(SCRATCH_WORDS)}(s1)", {6: 1})
                last_mem = True
            elif c == 7:
                self.emit("  jal  x0, 1f", {7: 1})
                self.emit("1:")
            elif c == 8:
                if self.rng.random() < 0.5:
                    self.emit("  beq  x0, x0, 1f", {8: 1, 9: 1})
                else:
                    self.emit("  bne  x0, x0, 1f", {8: 1})
                self.emit("1:")
            elif c == 9:
                self.emit("  blt  s10, s11, 1f", {8: 1, 9: 1})      # s10 < s11 (P0, never touched): taken
                self.emit("1:")
            elif c == 10:
                self.emit(".option push")
                self.emit(".option rvc")
                n = self.rng.choice((2, 4))                            # even count keeps the 4-byte alignment
                for _ in range(n):
                    self.emit(f"  c.addi {self.rng.choice(FILLER_REGS)}, {self.rng.randint(1, 15)}", {10: 1})
                self.emit(".option pop")
            elif c == 11:
                self.emit(f"  mulh {self.rng.choice(FILLER_REGS)}, {self.rng.choice(FILLER_REGS)}, {self.rng.choice(FILLER_REGS)}", {11: 1})
            elif c == 12:
                self.emit(f"  div  {self.rng.choice(FILLER_REGS)}, {self.rng.choice(FILLER_REGS)}, {self.rng.choice(FILLER_REGS)}", {12: 1})
            if self.rng.random() < 0.3:
                self.alu()
                last_mem = False

    def full_spec(self):
        spec = {c: self.rng.randint(5, 9) for c in (5, 6, 7, 8, 9, 11, 12)}
        spec[10] = self.rng.randint(3, 5)     # compressed pairs: 6..20 instructions
        return spec

    def delta(self, c, i0, i1, raw=False):
        """Expected increment of counter c over stream[i0:i1] (each entry under its own inhibit state; raw: ignore it)."""
        return sum(ev.get(c, 0) for st, ev in self.stream[i0:i1] if raw or not (st >> c) & 1)

    def inhibited(self, c, i0, i1):
        return all((st >> c) & 1 for st, _ev in self.stream[i0:i1])

    def bound_lo(self, c, i0, i1):
        """Lower bound of a bound-class counter over an interval: mcycle one cycle per instruction, the mul/div wait
        counters one stall cycle per mulh / div, the IF stall counter 1 when the interval has a taken control transfer
        (the fetch bubble), the LSU stall counter none (a fast grant/response regime can leave a memory op without a
        stall cycle)."""
        if c in (0, 11, 12):
            return self.delta(c, i0, i1)
        if c == 3:
            return 0          # a fast grant/response regime showed 0 stall cycles over 10+ memory ops: no floor
        return 1 if self.delta(7, i0, i1, raw=True) + self.delta(9, i0, i1, raw=True) else 0

    def read_all_before(self, order):
        """csrr of every counter (mcycle first) saved to the scratch area; returns {c: stream index of its read}."""
        pos = {}
        for i, c in enumerate([CY] + order):
            pos[c] = len(self.stream)
            self.emit(f"  csrr t0, {csr_hex(mcsr(c))}")
            self.emit(f"  sw   t0, {SAVE_OFF + 4 * i}(s1)", {6: 1})
        return pos

    def read_all_after(self, order, pos, item, label):
        """csrr of every counter (mcycle last) into registers, then the deltas reported: exact class abs, an inhibited
        counter abs 0, bound class lo <= delta <= the window's mcycle delta; returns {c: report idx}."""
        after = {}
        for c in order + [CY]:
            after[c] = len(self.stream)
            self.emit(f"  csrr {CTR_REGS[COUNTERS.index(c)]}, {csr_hex(mcsr(c))}")
        idxs = {}
        cy_inh = self.inhibited(CY, pos[CY], after[CY])
        self.emit(f"  lw   t0, {SAVE_OFF}(s1)", {5: 1})
        self.emit(f"  sub  t0, {CTR_REGS[0]}, t0")
        if cy_inh:
            idxs[CY] = self.report_reg("t0", item, f"{label} delta mcycle (inhibited)", "abs", 0)
        else:
            idxs[CY] = self.report_reg("t0", item, f"{label} delta mcycle", "bound", (self.bound_lo(CY, pos[CY], after[CY]), None))
        for i, c in enumerate(order, start=1):
            self.emit(f"  lw   t0, {SAVE_OFF + 4 * i}(s1)", {5: 1})
            self.emit(f"  sub  t0, {CTR_REGS[COUNTERS.index(c)]}, t0")
            if self.inhibited(c, pos[c], after[c]):
                idxs[c] = self.report_reg("t0", item, f"{label} delta {CTR_NAMES[c]} (inhibited)", "abs", 0)
            elif c in EXACT:
                idxs[c] = self.report_reg("t0", item, f"{label} delta {CTR_NAMES[c]}", "abs", self.delta(c, pos[c], after[c]))
            else:
                lo = self.bound_lo(c, pos[c], after[c])
                idxs[c] = self.report_reg("t0", item, f"{label} delta {CTR_NAMES[c]}", "bound", (lo, None if cy_inh else idxs[CY]))
        return idxs

    def measured_window(self, spec, item, label):
        order = [c for c in COUNTERS if c != CY]
        self.rng.shuffle(order)
        pos = self.read_all_before(order)
        w0 = len(self.stream)
        self.window(spec)
        w1 = len(self.stream)
        idxs = self.read_all_after(order, pos, item, label)
        events = {c: sum(ev.get(c, 0) for _s, ev in self.stream[w0:w1]) for c in COUNTERS}
        return idxs, events

    # --- TP-PMC-023 ----------------------------------------------------------------------------------------------------------
    def tp023(self):
        item, meta = "TP-PMC-023", self.plan.items["TP-PMC-023"]
        meta["windows"] = []          # dicts: mask, bits, inh_idx, deltas {c: idx}, events {c: n}
        masks = [1 << b for b in COUNTERS]
        self.rng.shuffle(masks)
        multi = 0
        while bin(multi).count("1") < 2:
            multi = self.rng.getrandbits(32) & HPM_CTRL_MASK
        masks.append(multi)
        for wi, mask in enumerate(masks):
            dev = None
            if self.red_here(item):
                b = self.red_rng.choice([c for c in COUNTERS if (mask >> c) & 1])
                dev = mask & ~(1 << b)
                self.plan.red_note = f"{item} window {wi}: the inhibit write leaves bit {b} clear (0x{dev:08x} for 0x{mask:08x})"
            _o, inh_idx = self.ctrl_op("csrrw", CSR_MCOUNTINHIBIT, mask, item, f"w{wi} inhibit 0x{mask:x}", dev=dev)
            idxs, events = self.measured_window(self.full_spec(), item, f"w{wi} inh 0x{mask:x}")
            meta["windows"].append({"mask": mask, "bits": [c for c in COUNTERS if (mask >> c) & 1], "inh_idx": inh_idx,
                                    "deltas": idxs, "events": events})
        meta["clear_idx"] = self.set_inhibit(0, item, "clear")

    # --- TP-PMC-024 ----------------------------------------------------------------------------------------------------------
    def tp024(self):
        item, meta = "TP-PMC-024", self.plan.items["TP-PMC-024"]
        meta["frozen"] = []           # (idx, form)
        meta["control"] = []          # (idx, form, expected difference)
        meta["hpm10"] = []
        for variant in ("ir", "hpm10"):
            bit = IR if variant == "ir" else 10
            mask = (1 << bit) | (self.rng.getrandbits(32) & HPM_CTRL_MASK & ~(1 << bit) if self.rng.random() < 0.3 else (1 << bit))
            dev = mask & ~(1 << bit) if self.red_here(item) else None
            if dev is not None:
                self.plan.red_note = f"{item} {variant}: the inhibit write leaves bit {bit} clear (0x{dev:08x} for 0x{mask:08x})"
            _o, idx = self.ctrl_op("csrrw", CSR_MCOUNTINHIBIT, mask, item, f"{variant} inhibit", dev=dev)
            meta[f"{variant}_inh_idx"] = idx
            csr = csr_hex(mcsr(bit))
            self.emit(f"  csrr s2, {csr}")                       # the frozen reference
            forms = ["lw_csrr", "run", "add_csrr"] if variant == "ir" else ["clw_csrr", "clw_csrr"]
            forms += [self.rng.choice(forms) for _ in range(self.rng.randint(1, 3))]
            self.rng.shuffle(forms)
            for rep in range(2):                                     # second pass: warm icache
                for form in forms:
                    if form == "lw_csrr":
                        self.emit(f"  lw   s3, {4 * self.rng.randrange(SCRATCH_WORDS)}(s1)", {5: 1})
                        self.emit(f"  csrr s4, {csr}")
                    elif form == "clw_csrr":
                        self.emit(".option push")
                        self.emit(".option rvc")
                        self.emit(f"  c.lw a0, {4 * self.rng.randrange(8)}(s1)", {5: 1, 10: 1})   # rd in x8..x15
                        self.emit("  c.nop", {10: 1})
                        self.emit(".option pop")
                        self.emit(f"  csrr s4, {csr}")
                    elif form == "add_csrr":
                        self.emit("  add  s3, s3, s5")
                        self.emit(f"  csrr s4, {csr}")
                    else:
                        for _ in range(self.rng.randint(3, 6)):
                            self.emit(f"  csrr s4, {csr}")
                    self.emit("  xor  t1, s4, s2")
                    ridx = self.report_reg("t1", item, f"{variant} {form} pass {rep} read minus frozen", "abs", 0)
                    (meta["frozen"] if variant == "ir" else meta["hpm10"]).append((ridx, form))
            self.set_inhibit(0, item, f"{variant} clear")
            if variant == "ir":
                for form in ("lw_csrr", "add_csrr", "run"):
                    i0 = len(self.stream)
                    self.emit(f"  csrr s2, {csr}")
                    if form == "lw_csrr":
                        self.emit(f"  lw   s3, {4 * self.rng.randrange(SCRATCH_WORDS)}(s1)", {5: 1})
                    elif form == "add_csrr":
                        self.emit("  add  s3, s3, s5")
                    else:
                        for _ in range(self.rng.randint(1, 3)):
                            self.emit("  addi s3, s3, 1")
                    i1 = len(self.stream)
                    self.emit(f"  csrr s4, {csr}")
                    self.emit("  sub  t1, s4, s2")
                    d = self.delta(IR, i0, i1)
                    meta["control"].append((self.report_reg("t1", item, f"IR=0 {form} difference", "abs", d), form, d))

    # --- TP-PMC-025 ----------------------------------------------------------------------------------------------------------
    def tp025(self):
        item, meta = "TP-PMC-025", self.plan.items["TP-PMC-025"]
        meta["episodes"] = []
        hpm_a = wchoice(self.rng, W_CTR_025)
        hpm_b = 5 if hpm_a != 5 else wchoice(self.rng, W_CTR_025)
        eps = [("mcycle_inh_resume", CY), ("minstret_inh_resume", IR), ("hpm_inh_resume", hpm_a), ("hpm_noinh", hpm_b)]
        self.rng.shuffle(eps)
        for kind, c in eps:
            x = self.rng.getrandbits(31) & ~0xF
            inh = kind != "hpm_noinh"
            mask = (1 << c) | (self.rng.getrandbits(32) & HPM_CTRL_MASK if self.rng.random() < 0.3 else 0) if inh else 0
            inh_idx = self.set_inhibit(mask, item, f"{kind} inhibit 0x{mask:x}")
            dev = x ^ (1 << self.red_rng.randrange(4, 28)) if self.red_here(item) else None
            if dev is not None:
                self.plan.red_note = f"{item} {kind}: counter {CTR_NAMES[c]} written 0x{dev:08x} for planned 0x{x:08x}"
            self.li("t0", x if dev is None else dev)
            self.emit(f"  csrw {csr_hex(mcsr(c))}, t0")
            w_idx = len(self.stream) - 1
            spec = {k: self.rng.randint(2, 6) for k in self.rng.sample((5, 6, 7, 8, 9, 10), 3)}
            spec[c] = self.rng.randint(5, 9) if c in (5, 6, 7, 8, 9, 10) else 0
            if c not in spec or spec[c] == 0:
                spec.pop(c, None)
            frozen_idx = None
            if inh:
                self.window(spec)
                self.emit(f"  csrr t1, {csr_hex(mcsr(c))}")
                frozen_idx = self.report_reg("t1", item, f"{kind} frozen read", "abs", x)
                clear_idx = self.set_inhibit(0, item, f"{kind} clear")
            self.window(spec)                     # the known window after the un-inhibit (or right after the write)
            r_idx = len(self.stream)
            self.emit(f"  csrr t1, {csr_hex(mcsr(c))}")
            inc = self.delta(c, w_idx + 1, r_idx)
            if c == CY:
                final_idx = self.report_reg("t1", item, f"{kind} final read", "range", (x + inc, 0xFFFFFFFF))
            else:
                final_idx = self.report_reg("t1", item, f"{kind} final read", "abs", (x + inc) & 0xFFFFFFFF)
            meta["episodes"].append({"kind": kind, "ctr": c, "x": x, "inh_idx": inh_idx, "frozen_idx": frozen_idx,
                                     "final_idx": final_idx, "inc": inc, "events": spec.get(c, 0)})
            if not inh:
                clear_idx = None
            meta["episodes"][-1]["clear_idx"] = clear_idx

    # --- TP-PMC-056 ----------------------------------------------------------------------------------------------------------
    def tp056(self):
        item, meta = "TP-PMC-056", self.plan.items["TP-PMC-056"]
        meta["windows"] = []
        shapes = [(5, False, False), (6, False, False), (8, True, False), (10, False, False)]
        shapes += [(wchoice(self.rng, W_056_N), self.rng.random() < 0.6, self.rng.random() < 0.3) for _ in range(self.rng.randint(1, 3))]
        shapes.append((wchoice(self.rng, W_056_N), self.rng.random() < 0.6, True))   # the CY variant at least once
        self.rng.shuffle(shapes)
        for wi, (n, clear, cy) in enumerate(shapes):
            e1, e2, e3 = (self.rng.randint(2, 7) for _ in range(3))
            bit = (1 << n) | ((1 << CY) if cy else 0)
            form = self.rng.choice(("csrrs", "csrrw"))
            p0 = len(self.stream)
            self.emit(f"  csrr t5, {csr_hex(mcsr(CY))}")       # t5 / t6: window-start values, never touched by fillers
            self.emit(f"  csrr t6, {csr_hex(mcsr(n))}")
            self.window({n: e1}, start_alu=True)
            dev = 0 if self.red_here(item) else None
            if dev is not None:
                self.plan.red_note = f"{item} window {wi}: the mid-window {form} of mcountinhibit carries no bit (0 for 0x{bit:x})"
            self.li("t0", bit if dev is None else dev)
            self.emit(f"  {form} x0, {csr_hex(CSR_MCOUNTINHIBIT)}, t0")
            self.m.inh = self.m.post_op(form, self.m.inh, bit) & HPM_CTRL_MASK
            self.stream[-1] = (self.m.inh, self.stream[-1][1])
            self.window({n: e2})
            if clear:
                self.li("t0", bit)
                self.emit(f"  csrrc x0, {csr_hex(CSR_MCOUNTINHIBIT)}, t0")
                self.m.inh &= ~bit & 0xFFFFFFFF
                self.stream[-1] = (self.m.inh, self.stream[-1][1])
                self.window({n: e3})
            p1 = len(self.stream)
            self.emit(f"  csrr t1, {csr_hex(mcsr(n))}")
            self.emit("  sub  t1, t1, t6")
            d = self.delta(n, p0 + 1, p1)
            d_idx = self.report_reg("t1", item, f"w{wi} delta {CTR_NAMES[n]} (E1 {e1}, E2 {e2}, E3 {e3 if clear else 0})", "abs", d)
            self.emit(f"  csrr t1, {csr_hex(mcsr(CY))}")
            self.emit("  sub  t1, t1, t5")
            cy_idx = self.report_reg("t1", item, f"w{wi} delta mcycle", "bound", (self.delta(CY, p0, p1 + 2), None))
            self.emit(f"  csrr t1, {csr_hex(CSR_MCOUNTINHIBIT)}")
            inh_idx = self.report_reg("t1", item, f"w{wi} mcountinhibit after", "abs", self.m.inh)
            meta["windows"].append({"n": n, "e1": e1, "e2": e2, "e3": e3 if clear else 0, "cleared": clear, "cy": cy, "form": form,
                                    "delta_idx": d_idx, "cy_idx": cy_idx, "inh_idx": inh_idx, "expected": d,
                                    "total": self.delta(n, p0 + 1, p1, raw=True)})
            self.set_inhibit(0, item, f"w{wi} restore 0")

    # --- TP-PMC-033 ----------------------------------------------------------------------------------------------------------
    def tp033(self):
        item, meta = "TP-PMC-033", self.plan.items["TP-PMC-033"]
        meta["episodes"] = []
        n = wchoice(self.rng, W_033_N)
        later_clear = self.rng.random() < 0.5
        en = (1 << n) | (self.rng.getrandbits(32) & HPM_CTRL_MASK if self.rng.random() < 0.5 else 0)
        en_idx = self.set_enable(en, item, f"mcounteren bit {n}")
        for kind in ("inh", "noinh"):
            mask = (1 << n) if kind == "inh" else 0
            dev = 0 if kind == "inh" and self.red_here(item) else None
            if dev is not None:
                self.plan.red_note = f"{item}: the inhibit of counter {CTR_NAMES[n]} is not set before the U episode"
            _o, inh_idx = self.ctrl_op("csrrw", CSR_MCOUNTINHIBIT, mask, item, f"{kind} inhibit 0x{mask:x}", dev=dev)
            self.li("s5", SENT_A)
            self.li("s6", SENT_B)
            legal = self.m.u_alias_legal(n)
            body = [(f"csrr s5, {csr_hex(alias(n))}", None if legal else CAUSE_ILLEGAL)]
            ev = self.rng.randint(5, 9)
            for _ in range(ev):
                body.append(("addi s4, s4, 1", None))
                if n == 7:
                    body += [("jal x0, 1f", None), ("1:", None)]
                elif n == 8:
                    body += [("bne x0, x0, 1f", None), ("1:", None)]
                elif n == 9:
                    body += [("beq x0, x0, 1f", None), ("1:", None)]
                elif n == 11:
                    body.append(("mulh s7, s3, s2", None))
                elif n == 12:
                    body.append(("div s7, s3, s2", None))
                else:
                    body.append(("xori s7, s7, 3", None))
            body.append((f"csrr s6, {csr_hex(alias(n))}", None if legal else CAUSE_ILLEGAL))
            recs = self.u_episode(body, item, f"{kind} episode")
            if kind == "inh":
                self.emit("  xor  t1, s5, s6")
                obs = self.report_reg("t1", item, f"{kind} second read xor first", "abs", 0 if legal else SENT_A ^ SENT_B)
            else:
                self.emit("  sltu t1, s5, s6")     # both reads legal: the second is above the first; trapped: the sentinels compare
                obs = self.report_reg("t1", item, f"{kind} second read above first", "abs", 1 if legal else int(SENT_A < SENT_B))
            meta["episodes"].append({"kind": kind, "n": n, "events": ev, "inh_idx": inh_idx, "recs": recs, "obs_idx": obs, "legal": legal})
        meta["en_idx"], meta["n"], meta["later_clear"] = en_idx, n, later_clear
        if later_clear:
            self.set_enable(en & ~(1 << n) & 0xFFFFFFFF, item, "mcounteren bit cleared")
            recs = self.u_episode([(f"csrr s5, {csr_hex(alias(n))}", None if self.m.u_alias_legal(n) else CAUSE_ILLEGAL)], item, "cleared read")
            meta["clear_recs"] = recs

    # --- body --------------------------------------------------------------------------------------------------------------
    def p_end(self):
        self.emit(f"  li   gp, {TOHOST_PASS}")
        self.emit("  la   t5, tohost")
        self.emit("  sw   gp, 0(t5)", {6: 1, 3: 1})
        self.emit("1:")
        self.emit("  j    1b")

    def handler_and_stubs(self):
        self.in_main = False
        a = self.aux
        a[:0] = ["", "# M-mode trap handler (mtvec base): with an armed base in s9 the trap is recorded to the report channel as",
                 "# mcause << 16 | MPP << 8 | (mepc - s9) / 4 and the instruction is skipped (ecall from U returns to M at s8);",
                 f"# a trap with s9 == 0 is a program failure (tohost {TOHOST_FAIL}).",
                 ".align 8", "gen_trap_vec:",
                 "  csrr t0, mcause", "  csrr t1, mepc", "  csrr t2, mstatus",
                 "  srli t2, t2, 11", "  andi t2, t2, 3",
                 "  beqz s9, gen_trap_fail",
                 "  sub  t3, t1, s9", "  srli t3, t3, 2", "  andi t3, t3, 0xff",
                 "  slli t2, t2, 8", "  slli t0, t0, 16", "  or   t0, t0, t2", "  or   t0, t0, t3",
                 "  sw   t0, 0(s0)",
                 "  csrr t0, mcause", f"  li   t3, {CAUSE_ECALL_U}", "  beq  t0, t3, 3f",
                 "  addi t1, t1, 4", "  csrw mepc, t1", "  mret",
                 "3:", "  csrw mepc, s8", f"  li   t0, 0x{MPP_MASK:x}", "  csrs mstatus, t0", "  mret",
                 "gen_trap_fail:",
                 "  slli t0, t0, 16", "  slli t2, t2, 8", "  or   t0, t0, t2", "  sw   t0, 0(s0)",
                 f"  li   gp, {TOHOST_FAIL}", "  la   t5, tohost", "  sw   gp, 0(t5)",
                 "5:", "  j    5b",
                 "", "# U-mode code area: one 4 KiB NAPOT region (entry 0, L=0 RWX); fixed-size instructions so the handler's",
                 "# record carries the index of the trapping instruction.",
                 f".align {UCODE_ALIGN_BITS}", ".globl gen_u_code", "gen_u_code:"]
        a += [f".align {UCODE_ALIGN_BITS}", ".globl gen_text_end", "gen_text_end:"]
        assert 4 * self.u_len <= (1 << UCODE_ALIGN_BITS), f"U code area overflow: {self.u_len} words"

    def data_section(self):
        return ["", ".section .data", ".align 6", ".globl gen_scratch", "gen_scratch:", f"  .space {4 * SCRATCH_WORDS + 4 * len(COUNTERS)}",
                ".align 3", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
                ".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {self.plan.min_retired}"]

    def build(self):
        self.p0()
        self.tp027()
        p1 = [self.tp022, self.tp032, self.tp028, self.tp026, self.tp029, self.tp030, self.tp031]
        self.rng.shuffle(p1)
        for blk in p1:
            blk()
        self.set_enable(0xFFFFFFFF, "setup", "mcounteren all-ones for the counter phase")
        self.set_inhibit(0, "setup", "mcountinhibit 0 for the counter phase")
        p2 = [self.tp023, self.tp024, self.tp025, self.tp056, self.tp033]
        self.rng.shuffle(p2)
        for blk in p2:
            blk()
        self.p_end()
        self.handler_and_stubs()
        assert self.red_target is None or self.plan.red_note, "red fixture: the deviation site was not emitted"
        self.plan.red_sites = self.red_sites
        self.check_coverage()
        header = ["# gen_pmc_ctrl: generated per-seed program of gen_test_pmc_ctrl (seed %d%s)." % (
                      self.plan.seed, ", RED fixture " + self.plan.red_item if self.plan.red else ""),
                  "# Generator: dv/auto_dv/tests/gen_programs/gen_pmc_ctrl_prog.py (do not edit; regenerate).",
                  '.include "gen_mmio_map.h"', ".section .text", ".globl _start", ".option norvc", "_start:"]
        self.plan.lines = header + self.main + self.aux + self.data_section()
        return self.plan

    def check_coverage(self):
        """The plan's own floors per seed (what the items say 'every ...' about)."""
        it = self.plan.items
        for item in ("TP-PMC-022", "TP-PMC-027"):
            w = it[item]["writes"]
            classes = {(p, OP_CLASS[f]) for _i, f, p, _pre, _post, _op in w}
            need = {("zeros", "wr"), ("ones", "wr"), ("ones", "set"), ("ones", "clr"), ("walking", "wr"), ("walking", "set"),
                    ("walking", "clr"), ("random", "wr"), ("random", "set"), ("random", "clr")}
            assert need <= classes, f"{item}: pattern x op classes missing {need - classes}"
            bits = {op.bit_length() - 1 for _i, _f, p, _pre, _post, op in w if p == "walking"}
            assert bits == set(range(32)), f"{item}: walking one misses bits {set(range(32)) - bits}"
        acc = it["TP-PMC-026"]["accesses"]
        assert len(acc) >= 12 and {c for c, _w, _f in acc} == {"en", "inh", "event", "mcycle", "minstret", "hpm", "mcycleh", "minstreth", "hpmh"}
        masks = {m["mask"] for m in it["TP-PMC-029"]["masks"]}
        assert {HPM_CTRL_MASK, 0} <= masks and len(masks) >= 3 or self.m.pin != "on", "TP-PMC-029: masks"
        assert it["TP-PMC-030"]["u_n"] >= 12 and len(it["TP-PMC-030"]["m_reads"]) >= 12
        m_ops, u_ops = it["TP-PMC-031"]["m_ops"], it["TP-PMC-031"]["u_ops"]
        assert {f for _a, _h, f in m_ops} == set(ALL_FORMS) and {f for _a, _h, f in u_ops} == set(ALL_FORMS)
        assert {tuple(w["bits"]) for w in it["TP-PMC-023"]["windows"] if len(w["bits"]) == 1} == {(c,) for c in COUNTERS}
        for w in it["TP-PMC-023"]["windows"]:
            assert all(w["events"][c] >= 5 for c in (5, 6, 7, 8, 9, 10, 11, 12)), f"TP-PMC-023 window events {w['events']}"
        assert {e["kind"] for e in it["TP-PMC-025"]["episodes"]} == {"mcycle_inh_resume", "minstret_inh_resume", "hpm_inh_resume", "hpm_noinh"}
        assert any(e["ctr"] == 5 for e in it["TP-PMC-025"]["episodes"])
        w56 = it["TP-PMC-056"]["windows"]
        assert {(w["n"], w["cleared"]) for w in w56} >= {(5, False), (6, False), (8, True), (10, False)} and any(w["cy"] for w in w56)
        assert all(w["e1"] >= 2 and w["e2"] >= 2 and (not w["cleared"] or w["e3"] >= 2) for w in w56)
        assert {e["kind"] for e in it["TP-PMC-033"]["episodes"]} == {"inh", "noinh"}
        assert {f for _i, f in it["TP-PMC-024"]["frozen"]} == {"lw_csrr", "run", "add_csrr"} and it["TP-PMC-024"]["hpm10"]


def plan(seed, red=False, red_item=None, pin="on"):
    """The green plan of a seed, or the red fixture: the same expectations with one program deviation of one built item
    (red_item, else drawn from RED_ITEMS with the site from random.Random(f"{seed}:red")); pin = the TB knob value."""
    green = Gen(seed, pin).build()
    if not red:
        return green
    rng = random.Random(f"{int(seed)}:{RED_RNG_TAG}")
    item = red_item or rng.choice(RED_ITEMS)
    assert item in RED_ITEMS, f"red: {item} is not a built item (refused: {NOT_BUILT} have no fire_tp method)"
    sites = green.red_sites[item]
    assert sites, f"red: no deviation site for {item} at seed {seed}"
    p = Gen(seed, pin, red_target=(item, rng.choice(sites))).build()
    assert p.signature() == green.signature() and p.k == green.k and p.min_retired <= green.min_retired + 8, "red: the expectations moved"
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
    ap.add_argument("--red", action="store_true", help="red fixture: the program deviates on one intent of one built item")
    ap.add_argument("--red-item", choices=RED_ITEMS, help="the built item the red fixture targets (default: drawn from the seed)")
    ap.add_argument("--pin", choices=PINS, default="on", help="knob_mcounteren_writable value the expectations assume (the text is the same)")
    ap.add_argument("--summary", action="store_true", help="print k, min_retired and the per-item report counts")
    args = ap.parse_args(argv)
    p = plan(args.seed, args.red, args.red_item, args.pin)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(emit(p))
    if args.summary or not args.out:
        per_item = {}
        for r in p.reports:
            per_item[r.item] = per_item.get(r.item, 0) + 1
        print(f"seed={p.seed} red={p.red} pin={p.pin} k={p.k} min_retired={p.min_retired} lines={len(p.lines)} per_item={per_item}"
              + f" red_sites={ {k: len(v) for k, v in p.red_sites.items()} }"
              + (f" red_item={p.red_item} red_note={p.red_note}" if p.red else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
