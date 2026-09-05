#!/usr/bin/env python3
"""gen_cmp_zca_prog: per-seed program generator of gen_test_cmp_zca (plan group gen_cmp_zca, the 21 Phase-1 Zca
items TP-CMP-001 002 004 005 008 010 011 012 014 016 017 018 020 021 023 024 026 028 030 032 033;
dv/auto_dv/docs/gen_test_plan.md AREA CMP).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:cmp_zca"): one unit per
Zca operation (the directed floors of every item as an exhaustive set plus weighted extras, W-tables W1/W2/W3/W4/W6/W8
of the plan's layer-1 table), shuffled, with unrelated filler instructions between them, and computes every report
word the program stores to GEN_MM_EOT_ADDR from the Zca specification semantics (tools/specs, zca.adoc). Every Zca
form is emitted as its explicit `c.*` mnemonic under `.option rvc`; the harness and the 32-bit twin forms (the same
operation as its 32-bit instruction on another register, reported beside the compressed result) stay under
`.option norvc`, so 32-bit instructions start at both halfword alignments throughout. Report words are RAW
observations: a register after a Zca form, a memory word read back after a Zca store, mcause/mtval/mepc read by the
trap handler. Facts that depend on the link address (a link register, mepc, the sp value a c.swsp x2 stored) are
reported raw beside an `auipc` anchor report and the test checks the relation (value == anchor + delta): the plan
lays every anchored region out from a `.balign 4` with fixed-size instructions only, so the deltas are exact.
Control transfers are visible through a trace register that every reached block shifts a mark into (skipped
shadow blocks carry marks too), so taken/not-taken, forward/backward, and both target alignments are asserted.
Traps: one handler (gen_trap_vec, 256-byte aligned, installed in mtvec at _start) reports mcause, mtval and mepc,
adds 2 to mepc and returns with mret: the c.ebreak exception case (TP-CMP-033, dcsr.ebreakm = 0 at reset) and the
illegal c.addi16sp nzimm = 0 halfword 0x6101 (TP-CMP-017).

red=True makes the PROGRAM deviate on one intent of one item while the expectation keeps the true program (exactly
that item's fire-check fails): an immediate or operand value changed (002 008 012 014 016 017 018 020 024 026 030),
a form swapped (018 shift kind, 021 CA op, 023 branch sense on a branch whose flip executes more instructions), a
store immediate moved (004 005), a c.nop inserted between an anchor and the anchored instruction (001 probe, 010/011
c.jal, 032 c.jalr, 033 c.ebreak), c.jr emitted as c.jalr (028). apply_red takes the first seed-ordered candidate whose
emitted program changes report words of that item only (proved by rendering both programs against the same model);
red_item names the item, None lets random.Random(f"{seed}:red") draw it. k, min_retired and every expectation are
identical to the green plan (asserted in main()).

Dropped clause (program-shaped, owner named): TP-CMP-028 odd c.jr targets (bit 0 set) are not drawn because the DUT's
rvfi_pc_wdata keeps bit 0 (bug candidate B13, gen_bug_log.md) and the always-on isa_pc_next comparator row would fail
every run of this pass-expected test; B13's xfail item owns it. Kept although the comparator flags it: the handler's
mtval read after c.ebreak (Ibex 0 as documented; the Spike-based model reports the pc) - a shim/comparator
legalization gap reported to TB Infra, never masked here.

CLI: python3 gen_cmp_zca_prog.py --seed N --out <file.S> [--red [--red-item TP-CMP-0nn]]
"""
import argparse
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP  # noqa: E402  (the EOT address a c.swsp x28 stores)
from dv.auto_dv.tests.gen_programs.gen_prog_const import TOHOST_PASS, csr_hex  # noqa: E402

RNG_TAG = "program:cmp_zca"
RED_TAG = "red"
MASK32 = 0xFFFFFFFF
CREGS = tuple(range(8, 16))            # 3-bit compressed register fields
ALLREGS = tuple(range(1, 32))
EOT_REG = 28                           # GEN_MM_EOT_ADDR for every report store (restored when an op writes it)
TMP, ANC, TRACE = 29, 30, 31           # handler scratch / anchor / trace register (re-chosen when an op needs them)
FILLER_REGS = (5, 6, 7)
SCR_LW, SCR_LW_BYTES = "gen_scr_lw", 256      # c.lw / c.sw region: base 0..128 step 4, uimm 0..124
SCR_SP, SCR_SP_BYTES = "gen_scr_sp", 512      # c.lwsp / c.swsp region: base 0..128 step 4, uimm 0..252
TRAP_VEC = "gen_trap_vec"
TRAP_RETIRE = 9                        # handler instructions retired per trap
ILLEGAL_ADDI16SP = 0x6101              # c.addi16sp sp, 0 (nzimm = 0): illegal
EXC_ILLEGAL, EXC_BREAKPOINT = 2, 3
EOT_ADDR = MEMORY_MAP["eot_addr"]

ITEMS = tuple(f"TP-CMP-{n:03d}" for n in (1, 2, 4, 5, 8, 10, 11, 12, 14, 16, 17, 18, 20, 21, 23, 24, 26, 28, 30, 32, 33))
I001, I002, I004, I005, I008, I010, I011, I012, I014, I016, I017, I018, I020, I021, I023, I024, I026, I028, I030, I032, I033 = ITEMS
RED_ITEMS = ITEMS

# Layer-1 tables (gen_test_plan.md "Layer-1 weight tables"): W1 register operands, W2 immediates (6-bit signed and
# unsigned Zc fields), W3 shift amounts, W6 control-transfer offsets, W8 Zc immediates; W4 register relations.
W1 = {"zero": 1, "all_ones": 1, "int_min": 1, "int_max": 1, "one": 1, "byte_msb": 1, "half_msb": 1, "alt_5": 1, "alt_a": 1,
      "pos_rand": 4, "neg_rand": 4}
W2_IMM6 = {"zero": 1, "plus1": 1, "minus1": 1, "max": 1, "min": 1, "pos_rand": 4, "neg_rand": 4}
W2_UIMM = {"zero": 1, "max": 1, "rand": 6}
W3_SHAMT = {"one": 1, "max": 1, "rand": 4}
W6_OFF = {"pos_rand": 4, "neg_rand": 4}
W8_ADDI16SP = {"min": 1, "max": 1, "plus16": 1, "minus16": 1, "rand": 4}
W4_SAME_REG = 8
FILLER_TEMPLATES = ("addi x5, x5, {imm12}", "xori x6, x6, {imm12}", "slli x7, x7, {sh}", "add x5, x6, x7",
                    "sub x7, x5, x6", "lui x6, {imm20}", "andi x5, x5, {imm12}", "or x6, x6, x7", "nop")
CA_OPS = ("c.sub", "c.xor", "c.or", "c.and")
# Compressed forms the directed alignment block emits at both alignments: no memory operand and no
# live register, since the destinations are the n16_ct unit's own two scratch registers.
ALIGN_FORMS = ("c.nop", "c.li x{r}, 0", "c.mv x{r}, x{c}", "c.add x{r}, x{c}", "c.sub x{c}, x{c}",
               "c.xor x{c}, x{c}", "c.or x{c}, x{c}", "c.and x{c}, x{c}", "c.andi x{c}, 1",
               "c.srli x{c}, 1", "c.srai x{c}, 1", "c.slli x{r}, 1", "c.lui x{r}, 1",
               "c.addi x{r}, 1")
SHIFT_OPS = ("c.srli", "c.srai")
BR_OPS = ("c.beqz", "c.bnez")
BR_VALUE_CLASSES = ("zero", "nonzero", "int_min")
SHIFT_OPERAND_CLASSES = ("msb_set", "msb_clear", "all_ones", "zero")
CJ_MAX_FWD, CJ_MAX_BWD = 2046, -2048
CB_MAX_FWD, CB_MAX_BWD = 254, -256
PROBE_FORMS = ("c.nop", "c.addi", "c.li", "c.slli")


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def sext(v, bits):
    v &= (1 << bits) - 1
    return (v | (MASK32 & ~((1 << bits) - 1))) if (v >> (bits - 1)) & 1 else v


def to_signed(v):
    return v - (1 << 32) if v & 0x80000000 else v


def operand(rng, cls):
    fixed = {"zero": 0, "one": 1, "all_ones": MASK32, "int_min": 0x80000000, "int_max": 0x7FFFFFFF,
             "byte_msb": 0x80, "half_msb": 0x8000, "alt_5": 0x55555555, "alt_a": 0xAAAAAAAA}
    if cls in fixed:
        return fixed[cls]
    r = rng.getrandbits(32)
    if cls == "pos_rand":
        return r & 0x7FFFFFFF
    if cls == "neg_rand":
        return r | 0x80000000
    if cls == "msb_set":
        return r | 0x80000000
    if cls == "msb_clear":
        return r & 0x7FFFFFFF
    if cls == "nonzero":
        return (r & 0x7FFFFFFF) or 1
    if cls == "rand":
        return r
    raise ValueError(f"unknown operand class {cls}")


def imm6(rng, cls):
    """Signed 6-bit immediate of the class (c.addi/c.li/c.andi: -32..31; c.lui: nonzero)."""
    fixed = {"zero": 0, "plus1": 1, "minus1": -1, "max": 31, "min": -32}
    if cls in fixed:
        return fixed[cls]
    return rng.randint(1, 31) if cls == "pos_rand" else rng.randint(-32, -1)


def shamt(rng, cls):
    return {"one": 1, "max": 31}.get(cls, rng.randint(1, 31))


def ci_result(form, val, imm):
    """Zca CI/CB-format ALU semantics on a 32-bit value (zca.adoc)."""
    if form == "c.addi":
        return (val + imm) & MASK32
    if form == "c.andi":
        return val & sext(imm, 6)
    if form == "c.slli":
        return (val << imm) & MASK32
    if form == "c.srli":
        return val >> imm
    if form == "c.srai":
        return (to_signed(val) >> imm) & MASK32
    raise ValueError(f"unknown CI form {form}")


def ca_result(form, a, b):
    return {"c.sub": (a - b) & MASK32, "c.xor": a ^ b, "c.or": a | b, "c.and": a & b}[form]


def enc_cj(off, form):
    """c.j / c.jal encoding for a byte offset (zca.adoc CJ format: imm[11|4|9:8|10|6|7|3:1|5])."""
    assert -2048 <= off <= 2046 and off % 2 == 0, f"{form} offset {off} not encodable"
    b = lambda i: (off >> i) & 1  # noqa: E731
    return ((0b001 if form == "c.jal" else 0b101) << 13) | b(11) << 12 | b(4) << 11 | ((off >> 8) & 3) << 9 | b(10) << 8 \
        | b(6) << 7 | b(7) << 6 | ((off >> 1) & 7) << 3 | b(5) << 2 | 0b01


def enc_cb(off, rs1, form):
    """c.beqz / c.bnez encoding for a byte offset (zca.adoc CB format: offset[8|4:3] rs1' offset[7:6|2:1|5])."""
    assert -256 <= off <= 254 and off % 2 == 0, f"{form} offset {off} not encodable"
    assert rs1 in CREGS, rs1
    b = lambda i: (off >> i) & 1  # noqa: E731
    return ((0b111 if form == "c.bnez" else 0b110) << 13) | b(8) << 12 | ((off >> 3) & 3) << 10 | ((rs1 - 8) & 7) << 7 \
        | ((off >> 6) & 3) << 5 | ((off >> 1) & 3) << 3 | b(5) << 2 | 0b01


def li_size(val):
    """Bytes GAS emits for `li rd, val` under .option norvc: addi, lui, or lui + addi."""
    s = to_signed(val & MASK32)
    if -2048 <= s <= 2047:
        return 4
    lo = (((val & 0xFFF) + 0x800) & 0xFFF) - 0x800      # GAS load_const: lui when the sign-extended low part is 0
    return 4 if lo == 0 else 8


def line_size(text):
    """Bytes of one emitted line (fixed-size instruction set: no relaxable instruction inside an anchored region)."""
    t = text.strip()
    if not t or t.endswith(":") or t.startswith((".option", ".balign", ".globl", ".section", "#")):
        return 0
    if t.startswith(".2byte"):
        return 2
    m = re.match(r"\.fill\s+(\d+),\s*2,", t)
    if m:
        return 2 * int(m.group(1))
    op = t.split()[0]
    if op.startswith("c."):
        return 2
    if op == "li":
        arg = t.split(",", 1)[1].strip()
        return 8 if arg == "GEN_MM_EOT_ADDR" else li_size(int(arg, 0) & MASK32)
    if op == "la":
        return 8
    return 4


@dataclass
class Rel:
    """Expectation relative to another raw report word: value == reports[base] + delta (mod 2^32)."""
    base: int
    delta: int


@dataclass
class Report:
    idx: int
    item: str
    expect: object          # int (absolute), Rel, or None (an anchor: reported, never compared)
    label: str


@dataclass
class Op:
    item: str
    kind: str
    p: dict = field(default_factory=dict)      # the intent
    dev: dict = field(default_factory=dict)    # the red fixture's deviation (applied to the emitted program only)


@dataclass
class Plan:
    seed: int
    red: bool
    ops: list
    reports: list
    k: int
    min_retired: int
    items: dict
    summary: dict
    red_item: str
    red_note: str
    text: str


class Builder:
    """Renders the ops into assembly lines and report expectations; emitted=True applies the deviations."""

    def __init__(self, init_lw, init_sp, filler_init, emitted):
        self.emitted = emitted
        self.lines = []
        self.reports = []
        self.items = {i: [] for i in ITEMS}
        self.retire = 0
        self.off = None            # byte offset inside an anchored region (None outside)
        self.last_report = False
        self.eot_live = True
        self.mem_lw = bytearray(init_lw)
        self.mem_sp = dict(init_sp)      # word offset -> int or ("sp", anchor report idx)
        self.filler_init = filler_init
        self.uid = 0
        self.twins = 0
        self.label_off = {}
        self.fixups = {}

    def v(self, op, key):
        if self.emitted and key in op.dev:
            return op.dev[key]
        return op.p[key]

    def ln(self, text, exe=True):
        size = line_size(text)
        self.lines.append(text)
        if self.off is not None:
            self.off += size
        if exe and size:
            op = text.strip().split()[0]
            self.retire += 2 if (op == "la" or (op == "li" and size == 8)) else 1
        if size:
            self.last_report = False

    def c(self, text, exe=True):
        self.ln(".option rvc")
        self.ln(text, exe)
        self.ln(".option norvc")

    def li(self, reg, val):
        self.ln(f"  li x{reg}, 0x{val & MASK32:08x}")
        if reg == EOT_REG:
            self.eot_live = False

    def la(self, reg, sym):
        self.ln(f"  la x{reg}, {sym}")
        if reg == EOT_REG:
            self.eot_live = False

    def wrote(self, reg):
        if reg == EOT_REG:
            self.eot_live = False

    def restore_eot(self):
        self.ln(f"  li x{EOT_REG}, GEN_MM_EOT_ADDR")
        self.eot_live = True

    def label(self, base):
        self.uid += 1
        name = f"gen_{base}_{self.uid}"
        return name

    def put_label(self, name):
        self.ln(f"{name}:")
        if self.off is not None:
            self.label_off[name] = self.off
            for idx, pos, form, rs1 in self.fixups.pop(name, []):
                self.lines[idx] = self.raw_ct(form, rs1, self.off - pos, name)

    @staticmethod
    def raw_ct(form, rs1, off, label):
        enc = enc_cb(off, rs1, form) if form in BR_OPS else enc_cj(off, form)
        return f"  .2byte 0x{enc:04x}   # {form} {'x%d, ' % rs1 if rs1 else ''}{label} ({off:+d})"

    def ct(self, form, label, rs1=None, exe=True):
        """A tested c.j / c.jal / c.beqz / c.bnez to a label of the same anchored region, as its raw 16-bit
        encoding (patched in when a forward label is placed): GAS 2.35 widens compressed forward jumps and
        branches far below their encodable range, which would move the target and change link values."""
        assert self.off is not None, "compressed control transfers are emitted inside an anchored region"
        pos = self.off
        if label in self.label_off:
            self.ln(self.raw_ct(form, rs1, self.label_off[label] - pos, label), exe)
        else:
            self.ln(f"  .2byte 0x0000   # {form} {label} (patched)", exe)
            self.fixups.setdefault(label, []).append((len(self.lines) - 1, pos, form, rs1))

    def region(self):
        """Start of an anchored region: 4-byte aligned (the .balign must see .option rvc to pad with a c.nop)."""
        self.ln(".option rvc")
        self.ln("  .balign 4")
        self.ln(".option norvc")
        self.off = 0

    def end_region(self):
        assert not self.fixups, f"unresolved jump labels {sorted(self.fixups)}"
        self.label_off = {}
        self.off = None

    def pad_to(self, target):
        n = target - self.off
        assert n >= 0 and n % 2 == 0, f"pad {n} bytes to reach offset {target} from {self.off}"
        if n:
            self.ln(f"  .fill {n // 2}, 2, 0x0001", exe=False)

    def mark(self, reg, k, exe):
        self.ln(f"  slli x{reg}, x{reg}, 4", exe)
        self.ln(f"  ori x{reg}, x{reg}, {k}", exe)

    @staticmethod
    def trace_of(marks):
        t = 0
        for k in marks:
            t = ((t << 4) | k) & MASK32
        return t

    def rep(self, reg, item, expect, label):
        """One report store; back-to-back stores get a nop between them (one bridge edge per store)."""
        if self.last_report:
            self.ln("  nop")
        if self.eot_live:
            self.ln(f"  sw x{reg}, 0(x{EOT_REG})")
        else:
            t = 30 if reg == 29 else 29
            self.ln(f"  li x{t}, GEN_MM_EOT_ADDR")
            self.ln(f"  sw x{reg}, 0(x{t})")
            self.ln(f"  li x{EOT_REG}, GEN_MM_EOT_ADDR")
            self.eot_live = True
        r = Report(len(self.reports), item, expect if (expect is None or isinstance(expect, Rel)) else expect & MASK32, label)
        self.reports.append(r)
        self.items[item].append(r.idx)
        self.last_report = True
        return r.idx

    def trap(self, item, cause, tval, anchor_idx, delta, label):
        """The handler's three report stores (mcause, mtval, mepc) at a trap the program takes on purpose."""
        self.rep_handler(item, cause, f"{label} mcause")
        self.rep_handler(item, tval, f"{label} mtval")
        self.rep_handler(item, Rel(anchor_idx, delta), f"{label} mepc")
        self.retire += TRAP_RETIRE

    def rep_handler(self, item, expect, label):
        r = Report(len(self.reports), item, expect if isinstance(expect, Rel) else expect & MASK32, label)
        self.reports.append(r)
        self.items[item].append(r.idx)

    def twin_reg(self, *avoid):
        return next(t for t in (29, 30, 31, 27) if t not in avoid)

    def twin(self, tmpl, rd_val, xt, item, expect, label):
        """The 32-bit form of the operation on register xt (`li xt, rd_val` first when the form reads xt)."""
        if rd_val is not None:
            self.li(xt, rd_val)
        self.ln("  " + tmpl.format(t=xt))
        self.twins += 1
        self.rep(xt, item, expect, label + " (32-bit twin)")

    # ---- item renderers --------------------------------------------------------------------------------------
    def r_probe(self, op):
        """TP-CMP-001: auipc anchor, k compressed ops, auipc at pc + 4 + 2k (pc[1] = k & 1), a 32-bit xori at the odd
        alignment when k is odd; reports the PC delta, the anchor's alignment and the compressed ops' result."""
        k = self.v(op, "k")
        forms = self.v(op, "forms")
        self.region()
        self.ln(f"  auipc x{ANC}, 0")
        val = 0
        for form, imm in forms:
            if form == "c.nop":
                self.c("  c.nop")
            elif form == "c.li":
                self.c(f"  c.li x{TRACE}, {imm}")
                val = sext(imm, 6)
            elif form == "c.addi":
                self.c(f"  c.addi x{TRACE}, {imm}")
                val = (val + imm) & MASK32
            else:
                self.c(f"  c.slli x{TRACE}, {imm}")
                val = (val << imm) & MASK32
        self.ln(f"  auipc x{TMP}, 0")
        if k % 2:
            self.ln(f"  xori x{TRACE}, x{TRACE}, {op.p['xor']}")
            val ^= op.p["xor"] & MASK32
        self.ln(f"  sub x{TMP}, x{TMP}, x{ANC}")
        self.rep(TMP, I001, 4 + 2 * k, f"probe pc delta over {k} compressed ops")
        self.ln(f"  andi x{ANC}, x{ANC}, 3")
        self.rep(ANC, I001, 0, "probe anchor alignment (balign 4)")
        self.rep(TRACE, I001, val, f"probe compressed result {[f for f, _ in forms]}")
        self.end_region()

    def r_addi4spn(self, op):
        rd, spv, imm = op.p["rd"], op.p["sp"], self.v(op, "imm")
        self.li(2, spv)
        self.c(f"  c.addi4spn x{rd}, sp, {imm}")
        self.next16(op)
        self.rep(rd, I002, spv + imm, f"c.addi4spn x{rd} sp=0x{spv:08x} nzuimm={imm}")
        if op.p["twin"]:
            self.twin(f"addi x{{t}}, x2, {op.p['imm']}", None, self.twin_reg(rd), I002, spv + op.p["imm"], f"addi x2 + {op.p['imm']}")

    def r_lw_sw(self, op):
        rs1, rs2, base_s, uimm_s, data = op.p["rs1"], op.p["rs2"], op.p["base_s"], self.v(op, "uimm_s"), op.p["data"]
        rd, rs1b, base_l, uimm_l = op.p["rd"], op.p["rs1b"], op.p["base_l"], op.p["uimm_l"]
        self.la(rs1, SCR_LW)
        if base_s:
            self.ln(f"  addi x{rs1}, x{rs1}, {base_s}")
        self.li(rs2, data)
        self.c(f"  c.sw x{rs2}, {uimm_s}(x{rs1})")
        self.next16(op)   # the store's own successor, not the readback's
        ea = base_s + uimm_s
        self.mem_lw[ea:ea + 4] = (data & MASK32).to_bytes(4, "little")
        ea_i = op.p["base_s"] + op.p["uimm_s"]
        self.la(rs1b, SCR_LW)
        if base_l:
            self.ln(f"  addi x{rs1b}, x{rs1b}, {base_l}")
        self.c(f"  c.lw x{rd}, {uimm_l}(x{rs1b})")
        word = int.from_bytes(self.mem_lw[ea_i:ea_i + 4], "little")
        self.next16(op)
        self.rep(rd, I004, word, f"c.sw x{rs2},{op.p['uimm_s']}(x{rs1}) ea={ea_i} then c.lw x{rd},{uimm_l}(x{rs1b})")
        self.la(TMP, SCR_LW)
        self.ln(f"  lw x{ANC}, {ea_i}(x{TMP})")
        self.rep(ANC, I004, word, f"lw readback of ea={ea_i} after c.sw")

    def r_sp_ls(self, op):
        base = op.p["base"]
        self.la(2, SCR_SP)
        if base:
            self.ln(f"  addi x2, x2, {base}")
        sp_idx = None
        for j, sub in enumerate(op.p["subs"]):
            kind, reg, uimm = sub["kind"], sub["reg"], sub["uimm"]
            if self.emitted and op.dev.get("sub") == j:
                uimm = op.dev["uimm"]
            w = base + sub["uimm"]
            if kind == "swsp":
                if reg == 2:
                    if sp_idx is None:
                        sp_idx = self.rep(2, I005, None, "sp anchor (c.swsp x2 stores it)")
                    val = ("sp", sp_idx)
                elif reg == 0:
                    val = 0
                elif reg == EOT_REG:
                    val = EOT_ADDR
                else:
                    val = sub["data"]
                    self.li(reg, val)
                self.c(f"  c.swsp x{reg}, {uimm}(sp)")
                self.next16(op)   # the store's own successor, not the readback's
                self.mem_sp[base + uimm] = val
                self.ln(f"  lw x{ANC}, {sub['uimm']}(sp)")
                self.rep(ANC, I005, self.word_sp(w), f"lw readback after c.swsp x{reg},{sub['uimm']}(sp) ea={w}")
            else:
                self.c(f"  c.lwsp x{reg}, {uimm}(sp)")
                self.wrote(reg)
                self.next16(op)
                self.rep(reg, I005, self.word_sp(w), f"c.lwsp x{reg},{sub['uimm']}(sp) ea={w}")

    def word_sp(self, w):
        val = self.mem_sp[w]
        return Rel(val[1], 0) if isinstance(val, tuple) else val

    def r_ci(self, op):
        """c.addi (008), c.li (012), c.lui (014), c.andi (020), c.slli (024), c.srli/c.srai (018)."""
        form, rd, imm = op.p["form"], op.p["rd"], self.v(op, "imm")
        f = self.v(op, "form")
        val = op.p.get("val")
        item = op.item
        i0 = op.p["imm"]
        if form == "c.li":
            self.c(f"  c.li x{rd}, {imm}")
            exp, exp_t = sext(imm, 6), sext(i0, 6)
            tw = f"addi x{{t}}, x0, {i0}"
            tv = None
        elif form == "c.lui":
            self.c(f"  c.lui x{rd}, 0x{imm & 0xFFFFF:x}")
            exp, exp_t = (sext(imm, 6) << 12) & MASK32, (sext(i0, 6) << 12) & MASK32
            tw = f"lui x{{t}}, 0x{i0 & 0xFFFFF:x}"
            tv = None
        else:
            self.li(rd, val)
            if op.p.get("nop_before"):
                self.c("  c.nop")
            self.c(f"  {f} x{rd}, {imm}")
            exp, exp_t = ci_result(f, val, imm), ci_result(form, val, i0)
            tw = f"{form[2:]} x{{t}}, x{{t}}, {i0}"
            tv = val
        self.wrote(rd)
        self.next16(op)
        self.rep(rd, item, exp, f"{form} x{rd} imm={i0}" + (f" val=0x{val:08x}" if val is not None else ""))
        if op.p["twin"]:
            self.twin(tw, tv, self.twin_reg(rd), item, exp_t, f"{form} x{rd} 32-bit form")

    def next16(self, op):
        """Put a compressed instruction between a compressed op and its report store.

        cp_next_len is the length of the NEXT RETIRED instruction. Every renderer here reports
        straight after its compressed op, and rep() emits a 32-bit `sw`, which is why the n32 legs
        of cr_insn_next are all hit and the n16 legs are not. This is opt-in per unit: making it
        global would take the n32 legs away.
        """
        if op.p.get("next16"):
            self.c("  c.nop")

    def r_ca(self, op):
        rd, rs2, a, b = op.p["rd"], op.p["rs2"], op.p["a"], op.p["b"]
        f = self.v(op, "form")
        self.li(rd, a)
        if rs2 != rd:
            self.li(rs2, b)
        bb = a if rs2 == rd else b
        if op.p["twin"]:
            self.twin(f"{op.p['form'][2:]} x{{t}}, x{{t}}, x{rs2}", a, self.twin_reg(rd, rs2), I021, ca_result(op.p["form"], a, bb), f"{op.p['form']} 32-bit form")
        self.c(f"  {f} x{rd}, x{rs2}")
        self.next16(op)
        self.rep(rd, I021, ca_result(f, a, bb), f"{op.p['form']} x{rd},x{rs2} 0x{a:08x},0x{bb:08x}")

    def r_mv_add(self, op):
        rd, rs2, a, b = op.p["rd"], op.p["rs2"], op.p["a"], self.v(op, "b")
        form = op.p["form"]
        item = I026 if form == "c.mv" else I030
        if rs2 != rd:
            self.li(rd, a)
            self.li(rs2, b)
        else:
            self.li(rd, b)
        bb = b
        if form == "c.mv":
            exp = bb
            tw = f"addi x{{t}}, x{rs2}, 0"
            tv = None
        else:
            exp = ((bb + bb) if rs2 == rd else (a + bb)) & MASK32
            tw = f"add x{{t}}, x{{t}}, x{rs2}"
            tv = bb if rs2 == rd else a
        xt = self.twin_reg(rd, rs2, *((29, 30) if EOT_REG in (rd, rs2) else ()))
        if op.p["twin"]:
            if tv is not None:
                self.li(xt, tv)
            self.ln("  " + tw.format(t=xt))
            self.twins += 1
        self.c(f"  {form} x{rd}, x{rs2}")
        self.wrote(rd)
        self.next16(op)
        self.rep(rd, item, exp, f"{form} x{rd},x{rs2} 0x{a:08x},0x{bb:08x}")
        if op.p["twin"]:
            self.rep(xt, item, exp, f"{form} 32-bit form")

    def r_addi16sp(self, op):
        """c.addi16sp on a random sp (016 no wrap, 017 wrap windows) with its 32-bit twin."""
        spv, imm = op.p["sp"], self.v(op, "imm")
        self.li(2, spv)
        self.c(f"  c.addi16sp sp, {imm}")
        self.rep(2, op.item, spv + imm, f"c.addi16sp sp=0x{spv:08x} nzimm={op.p['imm']} wrap={op.p['wrap']}")
        if op.p["twin"]:
            self.twin(f"addi x{{t}}, x{{t}}, {op.p['imm']}", spv, self.twin_reg(2), op.item, spv + op.p["imm"], "addi 32-bit form")

    def r_addi16sp_base(self, op):
        """TP-CMP-016: the result is the base of a following c.lwsp (sp = scratch + off after the add)."""
        off, imm, uimm = op.p["off"], self.v(op, "imm"), op.p["uimm"]
        rd = op.p["rd"]
        self.la(2, SCR_SP)
        self.ln(f"  addi x2, x2, {off - op.p['imm']}")
        self.c(f"  c.addi16sp sp, {imm}")
        self.c(f"  c.lwsp x{rd}, {uimm}(sp)")
        self.wrote(rd)
        w = off + uimm + (imm - op.p["imm"])
        self.rep(rd, I016, self.word_sp(w), f"c.lwsp x{rd},{uimm}(sp) after c.addi16sp nzimm={op.p['imm']} (base ea={w})")

    def r_illegal16sp(self, op):
        spv = op.p["sp"]
        self.li(2, spv)
        self.region()
        self.ln(f"  auipc x{ANC}, 0")
        a = self.rep(ANC, I017, None, "anchor before the illegal c.addi16sp")
        if op.p["odd"]:
            self.c("  c.nop")
        at = self.off
        self.ln(f"  .2byte 0x{ILLEGAL_ADDI16SP:04x}")
        self.trap(I017, EXC_ILLEGAL, ILLEGAL_ADDI16SP, a, at, f"illegal c.addi16sp nzimm=0 at pc[1]={int(op.p['odd'])}")
        self.rep(2, I017, spv, "sp unchanged after the illegal c.addi16sp")
        self.end_region()

    def r_ebreak(self, op):
        self.region()
        self.ln(f"  auipc x{ANC}, 0")
        a = self.rep(ANC, I033, None, "anchor before c.ebreak")
        for _ in range(int(op.p["odd"]) + (op.dev.get("nops", 0) if self.emitted else 0)):
            self.c("  c.nop")
        at = self.off
        self.c("  c.ebreak")
        self.trap(I033, EXC_BREAKPOINT, 0, a, at, f"c.ebreak at pc[1]={int(op.p['odd'])}")
        self.li(TMP, op.p["cont"])
        self.rep(TMP, I033, op.p["cont"], "execution resumed after the c.ebreak (mret to mepc + 2)")
        self.end_region()

    def r_cj(self, op):
        """TP-CMP-010: c.j forward over a shadow block, c.j backward through two blocks, c.jal call/return."""
        var, pad = op.p["var"], op.p["pad"]
        self.li(TRACE, 0)
        self.region()
        if var == "fwd":
            lf = self.label("cj_f")
            j = self.off
            self.ct("c.j", lf)
            self.mark(TRACE, op.p["m_shadow"], False)
            self.pad_to(j + 2 + 8 + pad)
            self.put_label(lf)
            self.mark(TRACE, op.p["m_t"], True)
            self.rep(TRACE, I010, self.trace_of([op.p["m_t"]]), f"c.j forward +{2 + 8 + pad} target pc[1]={((j + 10 + pad) >> 1) & 1}")
        elif var == "bwd":
            le, lb, lx = self.label("cj_e"), self.label("cj_b"), self.label("cj_x")
            if pad % 4:
                self.c("  c.nop")
            self.ct("c.j", le)
            self.put_label(lb)
            b_at = self.off
            self.mark(TRACE, op.p["m_b"], True)
            self.ct("c.j", lx)
            self.pad_to(self.off + pad)
            self.put_label(le)
            self.mark(TRACE, op.p["m_a"], True)
            back = self.off
            self.ct("c.j", lb)
            self.put_label(lx)
            self.rep(TRACE, I010, self.trace_of([op.p["m_a"], op.p["m_b"]]), f"c.j backward {b_at - back} target pc[1]={(b_at >> 1) & 1}")
        else:
            ls, lx = self.label("cjal_s"), self.label("cjal_x")
            self.ln(f"  auipc x{ANC}, 0")
            a = self.rep(ANC, I010, None, "anchor before c.jal")
            if self.emitted and op.dev.get("nops"):
                self.c("  c.nop")
            j = self.off
            self.ct("c.jal", ls)
            self.mark(TRACE, op.p["m_r"], True)
            self.ct("c.j", lx)
            self.pad_to(self.off + pad)
            self.put_label(ls)
            s_at = self.off
            self.mark(TRACE, op.p["m_s"], True)
            self.c("  c.jr x1")
            self.put_label(lx)
            self.rep(1, I010, Rel(a, j + 2), f"c.jal link (pc + 2), target +{s_at - j} pc[1]={(s_at >> 1) & 1}")
            self.rep(TRACE, I010, self.trace_of([op.p["m_s"], op.p["m_r"]]), "c.jal call and c.jr return path")
        self.end_region()

    def r_cj_extreme(self, op):
        """TP-CMP-011: offsets exactly +2046 and -2048 (c.jal forward / c.j backward, or c.j forward / c.jal backward)."""
        self.li(TRACE, 0)
        self.region()
        self.ln(f"  auipc x{ANC}, 0")
        a = self.rep(ANC, I011, None, "anchor before the extreme jump")
        if self.emitted and op.dev.get("nops"):
            self.c("  c.nop")
        lfar, lback, lx = self.label("far"), self.label("back"), self.label("x")
        j = self.off
        if op.p["var"] == "jal_fwd":
            self.ct("c.jal", lfar)
            self.mark(TRACE, op.p["m_shadow"], False)
            self.ln(f"  j {lx}", False)
            self.put_label(lback)
            b_at = self.off
            self.mark(TRACE, op.p["m_b"], True)
            self.ln(f"  j {lx}")
            self.pad_to(j + CJ_MAX_FWD)
            self.put_label(lfar)
            self.mark(TRACE, op.p["m_s"], True)
            self.rep(1, I011, Rel(a, j + 2), f"c.jal +{CJ_MAX_FWD} link pc + 2")
            self.pad_to(b_at - CJ_MAX_BWD)
            self.ct("c.j", lback)
            self.put_label(lx)
            self.rep(TRACE, I011, self.trace_of([op.p["m_s"], op.p["m_b"]]), f"c.jal +{CJ_MAX_FWD} then c.j {CJ_MAX_BWD} taken")
        else:
            self.ct("c.j", lfar)
            self.mark(TRACE, op.p["m_shadow"], False)
            self.ln(f"  j {lx}", False)
            self.put_label(lback)
            b_at = self.off
            self.mark(TRACE, op.p["m_b"], True)
            self.rep(1, I011, Rel(a, b_at - CJ_MAX_BWD + 2), f"c.jal {CJ_MAX_BWD} link pc + 2")
            self.ln(f"  j {lx}")
            self.pad_to(j + CJ_MAX_FWD)
            self.put_label(lfar)
            self.mark(TRACE, op.p["m_s"], True)
            self.pad_to(b_at - CJ_MAX_BWD)
            self.ct("c.jal", lback)
            self.put_label(lx)
            self.rep(TRACE, I011, self.trace_of([op.p["m_s"], op.p["m_b"]]), f"c.j +{CJ_MAX_FWD} then c.jal {CJ_MAX_BWD} taken")
        self.end_region()

    def r_cb(self, op):
        form, rs1, val, var, pad = self.v(op, "form"), op.p["rs1"], op.p["val"], op.p["var"], op.p["pad"]
        taken = (val == 0) == (form == "c.beqz")
        self.li(rs1, val)
        self.li(TRACE, 0)
        self.region()
        if var == "fwd":
            lt = self.label("cb_t")
            j = self.off
            self.ct(form, lt, rs1)
            self.mark(TRACE, op.p["m_f"], not taken)
            self.pad_to(j + 2 + 8 + pad)
            self.put_label(lt)
            self.mark(TRACE, op.p["m_t"], True)
            marks = [op.p["m_t"]] if taken else [op.p["m_f"], op.p["m_t"]]
            desc = f"forward +{10 + pad}"
        elif var == "bwd":
            le, lt, lx = self.label("cb_e"), self.label("cb_t"), self.label("cb_x")
            self.ct("c.j", le)
            self.put_label(lt)
            t_at = self.off
            self.mark(TRACE, op.p["m_t"], taken)
            self.ct("c.j", lx, exe=taken)
            self.pad_to(t_at + 10 + pad)
            self.put_label(le)
            self.ct(form, lt, rs1)
            self.mark(TRACE, op.p["m_f"], not taken)
            self.put_label(lx)
            marks = [op.p["m_t"]] if taken else [op.p["m_f"]]
            desc = f"backward {t_at - (t_at + 10 + pad)}"
        else:
            ls = self.label("cb_self")
            self.put_label(ls)
            self.ct(form, ls, rs1)
            self.mark(TRACE, op.p["m_f"], True)
            marks = [op.p["m_f"]]
            desc = "offset 0 (self)"
        self.rep(TRACE, I023, self.trace_of(marks), f"{op.p['form']} x{rs1}=0x{val:08x} {desc} {'taken' if (val == 0) == (op.p['form'] == 'c.beqz') else 'not taken'}")
        self.end_region()

    def r_cjr(self, op):
        rs1, odd, pad, link_c = op.p["rs1"], op.p["odd"], op.p["pad"], op.p["link"]
        tr = TRACE if rs1 != TRACE else 26
        an = ANC if rs1 != ANC else 27
        form = self.v(op, "form")
        lt = self.label("cjr_t")
        self.la(rs1, lt)
        if odd:
            self.ln(f"  addi x{rs1}, x{rs1}, 1")
        if rs1 != 1:
            self.li(1, link_c)
        self.li(tr, 0)
        self.region()
        self.ln(f"  auipc x{an}, 0")
        jpos = self.off
        self.c(f"  {form} x{rs1}")
        self.mark(tr, op.p["m_shadow"], False)
        self.pad_to(self.off + pad)
        self.put_label(lt)
        t_at = self.off
        if rs1 == EOT_REG:
            self.restore_eot()
        self.mark(tr, op.p["m_t"], True)
        a = self.rep(an, I028, None, "anchor before c.jr")
        exp1 = Rel(a, jpos + 2) if form == "c.jalr" else (Rel(a, t_at + odd) if rs1 == 1 else link_c)
        self.rep(1, I028, exp1, f"x1 after c.jr x{rs1} (no rd write; {'x1 holds the target' if rs1 == 1 else 'x1 untouched'})")
        self.rep(tr, I028, self.trace_of([op.p["m_t"]]), f"c.jr x{rs1} target +{t_at} pc[1]={(t_at >> 1) & 1}")
        self.end_region()

    def r_cjalr(self, op):
        rs1, pad = op.p["rs1"], op.p["pad"]
        tr = TRACE if rs1 != TRACE else 26
        an = ANC if rs1 != ANC else 27
        ls, lx = self.label("cjalr_s"), self.label("cjalr_x")
        self.la(rs1, ls)
        self.li(tr, 0)
        self.region()
        self.ln(f"  auipc x{an}, 0")
        if self.emitted and op.dev.get("nops"):
            self.c("  c.nop")
        j = self.off
        self.c(f"  c.jalr x{rs1}")
        self.mark(tr, op.p["m_r"], True)
        self.ct("c.j", lx)
        self.pad_to(self.off + pad)
        self.put_label(ls)
        s_at = self.off
        if rs1 == EOT_REG:
            self.restore_eot()
        self.mark(tr, op.p["m_s"], True)
        self.c("  c.jr x1")
        self.put_label(lx)
        a = self.rep(an, I032, None, "anchor before c.jalr")
        self.rep(1, I032, Rel(a, j + 2), f"c.jalr x{rs1} link pc + 2 (target from the old rs1), target +{s_at} pc[1]={(s_at >> 1) & 1}")
        self.rep(tr, I032, self.trace_of([op.p["m_s"], op.p["m_r"]]), f"c.jalr x{rs1} call and c.jr x1 return path")
        self.end_region()

    def r_n16_ct(self, op):
        """The cr_insn_next n16 legs of the control transfers (CG-CMP gen_cmp_zca_cg).

        Their retired successor is the TARGET when taken and the fall-through when not, so the
        filler that serves the ordinary forms does nothing for them. Self-contained on purpose:
        it owns its region and its labels, emits no report, and touches no other unit's offsets,
        so the branch and link expectations elsewhere are untouched. Each branch is arranged NOT
        taken, which puts its compressed fall-through in the retired stream; each jump falls into
        a target whose first instruction is compressed.
        """
        cr, jr = op.p["creg"], op.p["jreg"]
        self.region()
        b1, b2 = self.label("n16b"), self.label("n16b")
        l1, l2, l3, l4 = (self.label("n16j"), self.label("n16j"), self.label("n16j"),
                          self.label("n16j"))
        self.li(cr, 1)                 # non-zero, so c.beqz is not taken
        self.ct("c.beqz", b1, cr)
        self.c("  c.nop")              # the 16-bit successor of c.beqz
        self.put_label(b1)
        self.li(cr, 0)                 # zero, so c.bnez is not taken
        self.ct("c.bnez", b2, cr)
        self.c("  c.nop")              # the 16-bit successor of c.bnez
        self.put_label(b2)
        self.la(jr, l1)
        self.c(f"  c.jr x{jr}")
        self.put_label(l1)
        self.c("  c.nop")              # the 16-bit successor of c.jr
        self.la(jr, l2)
        if self.off % 4 == 0:
            self.c("  c.nop")          # the c.jalr retires half-word aligned (cr_insn_align)
        self.c(f"  c.jalr x{jr}")
        self.put_label(l2)
        self.c("  c.nop")              # the 16-bit successor of c.jalr
        self.ct("c.jal", l3)
        self.put_label(l3)
        self.c("  c.nop")              # the 16-bit successor of c.jal
        self.ct("c.j", l4)
        self.put_label(l4)
        self.c("  c.nop")              # the 16-bit successor of c.j
        # one instance of each safe form at BOTH alignments: the alignment legs are declared bins,
        # and an instance whose address is left to the surrounding stream is a coincidence that
        # holds at most seeds and fails at the rest
        for form in ALIGN_FORMS:
            for want in (0, 2):
                if self.off % 4 != want:
                    self.c("  c.nop")
                self.c("  " + form.format(c=cr, r=jr))
        self.end_region()

    def r_filler(self, op):
        if op.p["rvc"]:
            self.ln(".option rvc")
            self.ln("  " + op.p["text"])
            self.ln(".option norvc")
        else:
            self.ln("  " + op.p["text"])

    RENDER = {"probe": "r_probe", "addi4spn": "r_addi4spn", "lw_sw": "r_lw_sw", "sp_ls": "r_sp_ls", "ci": "r_ci",
              "ca": "r_ca", "mv_add": "r_mv_add", "addi16sp": "r_addi16sp", "addi16sp_base": "r_addi16sp_base",
              "illegal16sp": "r_illegal16sp", "ebreak": "r_ebreak", "cj": "r_cj", "cj_ext": "r_cj_extreme", "cb": "r_cb",
              "cjr": "r_cjr", "cjalr": "r_cjalr", "filler": "r_filler",
              "n16_ct": "r_n16_ct"}

    def render(self, ops):
        self.ln(f"  la x{TMP}, {TRAP_VEC}")
        self.ln(f"  csrw {csr_hex('mtvec')}, x{TMP}")
        self.ln(f"  li x{EOT_REG}, GEN_MM_EOT_ADDR")
        for r, v in zip(FILLER_REGS, self.filler_init):
            self.li(r, v)
        for op in ops:
            getattr(self, self.RENDER[op.kind])(op)
        return self.lines, self.reports


# ---- plan: the units of every item ---------------------------------------------------------------------------
def marks(rng, n):
    return rng.sample(range(1, 16), n)


def n16_clones(rng, U):
    """One directed clone per unit family with next16 set (cr_insn_next n16 legs).

    A clone of a real unit rather than a hand-built parameter dict: the parameters are valid by
    construction, so a directed instance cannot differ from a working one in some field nobody
    checked. Additive only -- every original keeps its 32-bit report store as its retired
    successor, which is what keeps the n32 legs hit.
    """
    import copy
    out = []
    for kind, form_key in (("addi4spn", None), ("lw_sw", None), ("ci", "form"), ("mv_add", "form")):
        seen = set()
        for o in U:
            if o.kind != kind:
                continue
            key = o.p.get(form_key) if form_key else kind
            if key in seen:
                continue
            seen.add(key)
            c = copy.deepcopy(o)
            c.p["next16"] = True
            out.append(c)
    # sp_ls emits one compressed op per SUB, so cloning the kind does not guarantee both forms:
    # a unit whose subs happen to be all swsp leaves c.lwsp short at that seed. Select by sub kind.
    for want in ("swsp", "lwsp"):
        o = next((o for o in U if o.kind == "sp_ls" and any(s["kind"] == want for s in o.p["subs"])), None)
        if o is not None:
            c = copy.deepcopy(o)
            c.p["next16"] = True
            out.append(c)
    return out


def build_units(rng):
    U = []

    # TP-CMP-001: probes with odd and even k (both alignments of the second auipc), every probe form over the seed
    ks = [1, 2, 3, 4] + [rng.randint(1, 7) for _ in range(rng.randint(2, 6))]
    for k in ks:
        forms = [("c.li", imm6(rng, weighted(rng, W2_IMM6)))]
        for _ in range(k - 1):
            f = rng.choice(PROBE_FORMS)
            forms.append((f, {"c.nop": 0, "c.li": imm6(rng, weighted(rng, W2_IMM6)), "c.addi": imm6(rng, "pos_rand") if rng.getrandbits(1) else imm6(rng, "neg_rand"),
                              "c.slli": shamt(rng, weighted(rng, W3_SHAMT))}[f]))
        U.append(Op(I001, "probe", {"k": k, "forms": forms, "xor": rng.randint(-2048, 2047)}))
    U.append(Op(I001, "probe", {"k": 3, "forms": [("c.li", 5), ("c.nop", 0), ("c.nop", 0)], "xor": rng.randint(-2048, 2047)}))

    # TP-CMP-002: every rd', nzuimm classes min/max/rand
    imms = [4, 1020] + [4 * rng.randint(1, 255) for _ in range(6)]
    rng.shuffle(imms)
    for i, rd in enumerate(CREGS):
        U.append(Op(I002, "addi4spn", {"rd": rd, "sp": rng.getrandbits(32), "imm": imms[i], "twin": rng.getrandbits(1) == 1}))
    for _ in range(rng.randint(0, 4)):
        U.append(Op(I002, "addi4spn", {"rd": rng.choice(CREGS), "sp": rng.getrandbits(32), "imm": {"zero": 4, "max": 1020}.get(weighted(rng, W2_UIMM), 4 * rng.randint(1, 255)), "twin": rng.getrandbits(1) == 1}))

    # TP-CMP-004: every rs1', every rd'/rs2', uimm classes for c.sw and c.lw
    def lw_sw(rs1, rd, uimm_s, uimm_l):
        rs2 = rng.choice([r for r in CREGS if r != rs1])
        base_s = 4 * rng.randint(max(0, (uimm_l - uimm_s + 3) // 4), 32)
        ea = base_s + uimm_s
        rs1b = rng.choice(CREGS) if rng.randrange(W4_SAME_REG) else rs1
        return Op(I004, "lw_sw", {"rs1": rs1, "rs2": rs2, "base_s": base_s, "uimm_s": uimm_s, "data": operand(rng, weighted(rng, W1)) or rng.getrandbits(32),
                                  "rd": rd, "rs1b": rs1b, "base_l": ea - uimm_l, "uimm_l": uimm_l})
    us = [0, 124] + [4 * rng.randint(0, 31) for _ in range(6)]
    ul = [0, 124] + [4 * rng.randint(0, 31) for _ in range(6)]
    rng.shuffle(us)
    rng.shuffle(ul)
    rds = list(CREGS)
    rng.shuffle(rds)
    for i, rs1 in enumerate(CREGS):
        U.append(lw_sw(rs1, rds[i], us[i], ul[i]))
    for _ in range(rng.randint(2, 6)):
        U.append(lw_sw(rng.choice(CREGS), rng.choice(CREGS), {"zero": 0, "max": 124}.get(weighted(rng, W2_UIMM), 4 * rng.randint(0, 31)),
                       {"zero": 0, "max": 124}.get(weighted(rng, W2_UIMM), 4 * rng.randint(0, 31))))

    # TP-CMP-005: rs2 classes x0/x1/x2/low/high, rd classes x1/low/high/x2, uimm classes zero/max/rand for both
    def uimm_sp(cls=None):
        cls = cls or weighted(rng, W2_UIMM)
        return {"zero": 0, "max": 252}.get(cls, 4 * rng.randint(0, 63))
    stores = [(0, uimm_sp("zero")), (1, uimm_sp("max")), (2, uimm_sp()), (rng.randint(3, 15), uimm_sp()), (rng.randint(16, 31), uimm_sp()), (EOT_REG, uimm_sp())]
    loads = [(1, uimm_sp("zero")), (rng.randint(3, 15), uimm_sp("max")), (rng.randint(16, 31), uimm_sp()), (2, uimm_sp())]
    for _ in range(rng.randint(2, 5)):
        stores.append((rng.choice([r for r in range(0, 32)]), uimm_sp()))
        loads.append((rng.choice([r for r in range(1, 32) if r != 2]), uimm_sp()))
    rng.shuffle(stores)
    rng.shuffle(loads)
    while stores or loads:
        subs = []
        for _ in range(rng.randint(2, 4)):
            if stores and (not loads or rng.getrandbits(1)):
                reg, u = stores.pop()
                subs.append({"kind": "swsp", "reg": reg, "uimm": u, "data": operand(rng, weighted(rng, W1))})
            elif loads:
                reg, u = loads.pop()
                subs.append({"kind": "lwsp", "reg": reg, "uimm": u})
                if reg == 2:
                    break      # c.lwsp x2 replaces sp: last sub-op of its unit
        if subs:
            U.append(Op(I005, "sp_ls", {"base": 4 * rng.randint(0, 32), "subs": subs}))
    # cr_insn_rdfull: one c.swsp source register in each register range that the draw above leaves to
    # chance. The stores are sampled, so a range can go unused at a seed; a declared bin cannot rest
    # on that. x1 and x2 are left to the draw on purpose: the renderer gives them the anchor and
    # sp-value paths, and a directed instance would duplicate that bookkeeping rather than a shape.
    _uimms = [4 * u for u in rng.sample(range(64), 3)]
    U.append(Op(I005, "sp_ls", {"base": 4 * rng.randint(0, 32), "subs": [
        {"kind": "swsp", "reg": rng.randrange(3, 5), "uimm": _uimms[0], "data": operand(rng, weighted(rng, W1))},
        {"kind": "swsp", "reg": rng.choice(CREGS), "uimm": _uimms[1], "data": operand(rng, weighted(rng, W1))},
        {"kind": "swsp", "reg": rng.randrange(16, 28), "uimm": _uimms[2], "data": operand(rng, weighted(rng, W1))},
    ]}))

    # TP-CMP-008 c.addi (every rd, imm classes), TP-CMP-012 c.li (every rd, imm classes incl 0),
    # TP-CMP-014 c.lui (rd not x0/x2, nzimm classes), TP-CMP-024 c.slli (every rd, shamt classes)
    def ci_set(item, form, regs, imms, vals=None):
        regs = list(regs)
        rng.shuffle(regs)
        for i, rd in enumerate(regs):
            imm = imms[i] if i < len(imms) else imms[rng.randrange(len(imms))]
            p = {"form": form, "rd": rd, "imm": imm, "twin": rng.getrandbits(1) == 1}
            if vals is not None:
                p["val"] = vals()
            if form == "c.addi":
                p["nop_before"] = rng.randrange(4) == 0
            U.append(Op(item, "ci", p))
    ci_set(I008, "c.addi", ALLREGS, [-32, -1, 1, 31] + [imm6(rng, rng.choice(("pos_rand", "neg_rand"))) for _ in range(27)], lambda: operand(rng, weighted(rng, W1)))
    ci_set(I012, "c.li", ALLREGS, [-32, -1, 0, 1, 31] + [imm6(rng, weighted(rng, W2_IMM6)) for _ in range(26)])
    ci_set(I014, "c.lui", [r for r in ALLREGS if r != 2], [1, 31, -32, -1] + [imm6(rng, rng.choice(("pos_rand", "neg_rand"))) for _ in range(26)])
    ci_set(I024, "c.slli", ALLREGS, [1, 31] + [shamt(rng, weighted(rng, W3_SHAMT)) for _ in range(29)], lambda: operand(rng, weighted(rng, W1)))
    # TP-CMP-018 c.srli/c.srai: every rd', shamt classes and operand classes per op
    for form in SHIFT_OPS:
        combos = [(s, c) for s in (1, 31, None) for c in SHIFT_OPERAND_CLASSES]
        rng.shuffle(combos)
        regs = list(CREGS)
        rng.shuffle(regs)
        for i, (s, c) in enumerate(combos):
            U.append(Op(I018, "ci", {"form": form, "rd": regs[i % 8], "imm": s if s else shamt(rng, "rand"), "val": operand(rng, c), "twin": rng.getrandbits(1) == 1}))
    # TP-CMP-020 c.andi: every rd', imm classes, operand mix
    imms = [-32, -1, 0, 1, 31] + [imm6(rng, weighted(rng, W2_IMM6)) for _ in range(5)]
    rng.shuffle(imms)
    regs = list(CREGS) + [rng.choice(CREGS), rng.choice(CREGS)]
    for i, rd in enumerate(regs):
        U.append(Op(I020, "ci", {"form": "c.andi", "rd": rd, "imm": imms[i], "val": operand(rng, weighted(rng, W1)), "twin": rng.getrandbits(1) == 1}))
    # TP-CMP-021 CA ops: every op over every rd' and every rs2', rd' == rs2' cases, c.sub wrap
    for form in CA_OPS:
        rs2s = list(CREGS)
        rng.shuffle(rs2s)
        for i, rd in enumerate(CREGS):
            a = operand(rng, weighted(rng, W1))
            b = operand(rng, weighted(rng, W1))
            if form == "c.sub" and rng.getrandbits(1):
                a, b = rng.randint(0, 0xFFFF), rng.randint(0x10000, MASK32)     # a - b wraps
            U.append(Op(I021, "ca", {"form": form, "rd": rd, "rs2": rs2s[i], "a": a, "b": b, "twin": rng.getrandbits(1) == 1}))
        r = rng.choice(CREGS)      # rd' == rs2'
        U.append(Op(I021, "ca", {"form": form, "rd": r, "rs2": r, "a": operand(rng, weighted(rng, W1)), "b": 0, "twin": rng.getrandbits(1) == 1}))
    U.append(Op(I021, "ca", {"form": "c.sub", "rd": rng.choice(CREGS), "rs2": rng.choice(CREGS), "a": 0, "b": 1, "twin": True}))
    # cr_insn_next n16 legs: one directed instance per form whose retired successor is 16-bit.
    # Additive on purpose -- every instance above keeps its 32-bit report store as the successor,
    # so the n32 legs stay hit; a global change would trade one set of bins for the other.
    for form in CA_OPS:
        rd = rng.choice(CREGS)
        U.append(Op(I021, "ca", {"form": form, "rd": rd, "rs2": rng.choice([r for r in CREGS if r != rd]),
                                 "a": operand(rng, weighted(rng, W1)) or rng.getrandbits(32),
                                 "b": operand(rng, weighted(rng, W1)) or rng.getrandbits(32),
                                 "twin": False, "next16": True}))
    # TP-CMP-026 c.mv, TP-CMP-030 c.add: every rd, both rd groups, rd == rs2, wrap pairs
    for form, item in (("c.mv", I026), ("c.add", I030)):
        rs2s = list(ALLREGS)
        rng.shuffle(rs2s)
        for i, rd in enumerate(ALLREGS):
            rs2 = rd if rng.randrange(W4_SAME_REG) == 0 else rs2s[i]
            a, b = operand(rng, weighted(rng, W1)), operand(rng, weighted(rng, W1))
            if form == "c.add" and rng.getrandbits(1):
                a, b = rng.randint(0x80000000, MASK32), rng.randint(0x80000000, MASK32)     # wrap
            U.append(Op(item, "mv_add", {"form": form, "rd": rd, "rs2": rs2, "a": a, "b": b, "twin": rng.getrandbits(1) == 1}))
        U.append(Op(item, "mv_add", {"form": form, "rd": rng.choice(ALLREGS), "rs2": None, "a": 0, "b": operand(rng, "neg_rand"), "twin": True}))
        U[-1].p["rs2"] = U[-1].p["rd"]
    # TP-CMP-016: nzimm classes without wrap, plus the c.lwsp-base variant; TP-CMP-017: wrap windows, extremes, illegal
    def imm16(cls):
        return {"min": -512, "max": 496, "plus16": 16, "minus16": -16}.get(cls, 16 * rng.choice([i for i in range(-32, 32) if i]))
    for cls in ("min", "max", "plus16", "minus16", "rand", "rand"):
        imm = imm16(cls)
        U.append(Op(I016, "addi16sp", {"sp": rng.randrange(0x400, 0xFFFFF000), "imm": imm, "wrap": False, "twin": rng.getrandbits(1) == 1}))
    for _ in range(rng.randint(1, 3)):
        imm = imm16(weighted(rng, W8_ADDI16SP))
        U.append(Op(I016, "addi16sp_base", {"off": 4 * rng.randint(0, 32), "imm": imm, "uimm": 4 * rng.randint(0, 63), "rd": rng.choice([r for r in ALLREGS if r != 2])}))
    for cls in ("min", "minus16", "rand_neg", "max", "plus16", "rand_pos"):
        imm = imm16(cls) if not cls.startswith("rand") else 16 * rng.randint(1, 31) * (-1 if cls == "rand_neg" else 1)
        spv = rng.randrange(0, -imm) if imm < 0 else rng.randrange((1 << 32) - imm, 1 << 32)
        U.append(Op(I017, "addi16sp", {"sp": spv, "imm": imm, "wrap": True, "twin": rng.getrandbits(1) == 1}))
    for odd in (False, True):
        U.append(Op(I017, "illegal16sp", {"sp": rng.getrandbits(32), "odd": odd}))
    # TP-CMP-033 c.ebreak exception case at both alignments
    for odd in (False, True) + tuple(bool(rng.getrandbits(1)) for _ in range(rng.randint(0, 2))):
        U.append(Op(I033, "ebreak", {"odd": odd, "cont": rng.getrandbits(32)}))
    # TP-CMP-010 c.j forward/backward, c.jal call/return at both target alignments; TP-CMP-011 extremes
    def cj(var, pad):
        m = marks(rng, 3)
        return Op(I010, "cj", {"var": var, "pad": pad, "m_shadow": m[0], "m_t": m[1], "m_b": m[1], "m_a": m[2], "m_r": m[1], "m_s": m[2]})
    for var in ("fwd", "bwd", "jal", "jal"):
        for parity in (0, 2):
            U.append(cj(var, 4 * rng.randint(0, 200) + parity))
    for _ in range(rng.randint(0, 3)):
        U.append(cj(rng.choice(("fwd", "bwd", "jal")), 2 * rng.randint(0, 400)))
    for var in ("jal_fwd", "j_fwd"):
        m = marks(rng, 3)
        U.append(Op(I011, "cj_ext", {"var": var, "m_shadow": m[0], "m_b": m[1], "m_s": m[2]}))
    # TP-CMP-023: both ops x {fwd, bwd} x value classes, extremes taken, self not taken, every rs1'
    def cb(form, var, vcls, pad):
        m = marks(rng, 2)
        return Op(I023, "cb", {"form": form, "rs1": rng.choice(CREGS), "val": operand(rng, vcls), "var": var, "pad": pad, "m_f": m[0], "m_t": m[1]})
    for form in BR_OPS:
        for var in ("fwd", "bwd"):
            for vcls in BR_VALUE_CLASSES:
                U.append(cb(form, var, vcls, 2 * rng.randint(0, 60)))
        U.append(cb(form, "fwd", "zero" if form == "c.beqz" else "nonzero", CB_MAX_FWD - 10))
        U.append(cb(form, "bwd", "zero" if form == "c.beqz" else "nonzero", -CB_MAX_BWD - 10))
        U.append(cb(form, "self", "nonzero" if form == "c.beqz" else "zero", 0))
    regs = list(CREGS)
    rng.shuffle(regs)
    for i, rs1 in enumerate(regs):
        u = cb(rng.choice(BR_OPS), rng.choice(("fwd", "bwd")), rng.choice(BR_VALUE_CLASSES), 2 * rng.randint(0, 60))
        u.p["rs1"] = rs1
        U.append(u)
    # TP-CMP-028 c.jr over every rs1 (odd targets, both alignments); TP-CMP-032 c.jalr over every rs1 incl x1
    for rs1 in ALLREGS:
        m = marks(rng, 2)
        # odd targets (bit 0 set) are NOT drawn: the DUT's rvfi_pc_wdata keeps bit 0 (bug candidate B13) and the
        # always-on isa_pc_next comparator row fails the run; the clause belongs to B13's xfail item
        U.append(Op(I028, "cjr", {"form": "c.jr", "rs1": rs1, "odd": False, "pad": 2 * rng.randint(0, 20), "link": rng.getrandbits(32) | 1, "m_shadow": m[0], "m_t": m[1]}))
        m = marks(rng, 2)
        U.append(Op(I032, "cjalr", {"rs1": rs1, "pad": 2 * rng.randint(0, 20), "m_r": m[0], "m_s": m[1]}))
    U += n16_clones(rng, U)
    U.append(Op(I010, "n16_ct", {"creg": rng.choice(CREGS),
                                "jreg": rng.choice([r for r in ALLREGS if r not in (EOT_REG, 1, 2) and r not in FILLER_REGS])}))
    return U


def filler(rng):
    t = rng.choice(FILLER_TEMPLATES)
    return Op("", "filler", {"text": t.format(imm12=rng.randint(-2048, 2047), sh=rng.randint(0, 31), imm20=rng.randint(0, 0xFFFFF)), "rvc": rng.getrandbits(1) == 1})


def red_candidates(rng, ops, item):
    """(op, deviation) candidates of the item, seed-ordered; every deviation keeps the report count."""
    cands = []
    for op in ops:
        if op.item != item:
            continue
        k, p = op.kind, op.p
        if k == "probe":
            cands.append((op, {"k": p["k"] + 1, "forms": p["forms"] + [("c.nop", 0)]}))
        elif k == "addi4spn":
            cands.append((op, {"imm": 1020 if p["imm"] != 1020 else 4}))
        elif k == "lw_sw":
            cands += [(op, {"uimm_s": u}) for u in (0, 124, 4 * rng.randint(1, 30)) if u != p["uimm_s"]]
        elif k == "sp_ls":
            cands += [(op, {"sub": j, "uimm": u}) for j, s in enumerate(p["subs"]) if s["kind"] == "swsp"
                      for u in (0, 252, 4 * rng.randint(1, 62)) if u != s["uimm"]]
        elif k == "ci":
            if p["form"] in SHIFT_OPS:
                cands.append((op, {"form": "c.srai" if p["form"] == "c.srli" else "c.srli"}))
                cands.append((op, {"imm": 31 if p["imm"] != 31 else 1}))
            elif p["form"] in ("c.slli",):
                cands.append((op, {"imm": 31 if p["imm"] != 31 else 1}))
            elif p["form"] == "c.lui":
                cands.append((op, {"imm": 1 if p["imm"] != 1 else -1}))
            else:
                cands.append((op, {"imm": rng.choice([i for i in range(-32, 32) if i != p["imm"] and (i or p["form"] != "c.addi")])}))
        elif k == "ca":
            cands += [(op, {"form": f}) for f in CA_OPS if f != p["form"]]
        elif k == "mv_add":
            cands.append((op, {"b": (p["b"] ^ 0x10001) & MASK32}))
        elif k == "addi16sp":
            cands.append((op, {"imm": 496 if p["imm"] != 496 else -512}))
        elif k == "addi16sp_base":
            for d in (16, -16, 32, -32):
                i2 = p["imm"] + d
                if i2 and -512 <= i2 <= 496 and 0 <= p["off"] + p["uimm"] + d <= SCR_SP_BYTES - 4:
                    cands.append((op, {"imm": i2}))
                    break
        elif k in ("ebreak", "cjalr", "cj_ext"):
            cands.append((op, {"nops": 1}))
        elif k == "cj" and p["var"] == "jal":
            cands.append((op, {"nops": 1}))
        elif k == "cb" and p["var"] != "self":
            taken = (p["val"] == 0) == (p["form"] == "c.beqz")
            if (p["var"] == "fwd") == taken:      # the flipped sense executes more instructions (floor stays valid)
                cands.append((op, {"form": "c.bnez" if p["form"] == "c.beqz" else "c.beqz"}))
        elif k == "cjr":
            cands.append((op, {"form": "c.jalr"}))
    rng.shuffle(cands)
    return cands


def same_expect(a, b):
    if isinstance(a, Rel) or isinstance(b, Rel):
        return isinstance(a, Rel) and isinstance(b, Rel) and (a.base, a.delta) == (b.base, b.delta)
    return a == b


def render(ops, init_lw, init_sp, filler_init, emitted):
    b = Builder(init_lw, init_sp, filler_init, emitted)
    lines, reports = b.render(ops)
    return b, lines, reports


def apply_red(rng, ops, init_lw, init_sp, filler_init, item, expected):
    for op, dev in red_candidates(rng, ops, item):
        op.dev = dev
        _, _, actual = render(ops, init_lw, init_sp, filler_init, emitted=True)
        if len(actual) == len(expected):
            diff = [i for i, (a, e) in enumerate(zip(actual, expected)) if not same_expect(a.expect, e.expect)]
            if diff and all(expected[i].item == item for i in diff):
                return f"{item}: {op.kind} {op.p.get('form', '')} dev {dev}; report idx {diff} deviate"
        op.dev = {}
    raise AssertionError(f"no deviation of {item} changes one of its report words for this seed")


def check_coverage(p):
    """The plan carries every directed floor the items ask for; a generator drift fails here, not in a run."""
    ops = [o for o in p.ops if o.kind != "filler"]
    by = lambda kind: [o for o in ops if o.kind == kind]  # noqa: E731
    probes = by("probe")
    assert {o.p["k"] % 2 for o in probes} == {0, 1} and any(f == "c.nop" for o in probes for f, _ in o.p["forms"]), "001 probes"
    assert {o.p["rd"] for o in by("addi4spn")} == set(CREGS) and {4, 1020} <= {o.p["imm"] for o in by("addi4spn")}, "002 floors"
    ls = by("lw_sw")
    assert {o.p["rs1"] for o in ls} == set(CREGS) and {o.p["rd"] for o in ls} == set(CREGS), "004 register floors"
    assert {0, 124} <= {o.p["uimm_s"] for o in ls} and {0, 124} <= {o.p["uimm_l"] for o in ls}, "004 uimm classes"
    subs = [s for o in by("sp_ls") for s in o.p["subs"]]
    st, ld = [s for s in subs if s["kind"] == "swsp"], [s for s in subs if s["kind"] == "lwsp"]
    assert {0, 1, 2, EOT_REG} <= {s["reg"] for s in st} and any(3 <= s["reg"] <= 15 for s in st) and any(s["reg"] >= 16 for s in st), "005 rs2 classes"
    assert {1, 2} <= {s["reg"] for s in ld} and any(3 <= s["reg"] <= 15 for s in ld) and any(s["reg"] >= 16 for s in ld), "005 rd classes"
    assert {0, 252} <= {s["uimm"] for s in st} and {0, 252} <= {s["uimm"] for s in ld}, "005 uimm classes"
    ci = by("ci")
    for form, regs, need in (("c.addi", ALLREGS, {-32, -1, 1, 31}), ("c.li", ALLREGS, {-32, -1, 0, 1, 31}), ("c.lui", [r for r in ALLREGS if r != 2], {1, 31, -32, -1}),
                             ("c.slli", ALLREGS, {1, 31}), ("c.andi", CREGS, {-32, -1, 0, 1, 31})):
        os_ = [o for o in ci if o.p["form"] == form]
        assert {o.p["rd"] for o in os_} == set(regs) and need <= {o.p["imm"] for o in os_}, f"{form} floors"
    for form in SHIFT_OPS:
        os_ = [o for o in ci if o.p["form"] == form]
        assert {o.p["rd"] for o in os_} == set(CREGS) and {1, 31} <= {o.p["imm"] for o in os_}, f"{form} floors"
        assert any(o.p["val"] & 0x80000000 for o in os_) and any(o.p["val"] == 0 for o in os_) and any(o.p["val"] == MASK32 for o in os_), f"{form} operands"
    ca = by("ca")
    for form in CA_OPS:
        os_ = [o for o in ca if o.p["form"] == form]
        assert {o.p["rd"] for o in os_} == set(CREGS) and {o.p["rs2"] for o in os_} == set(CREGS), f"{form} register floors"
    assert any(o.p["rd"] == o.p["rs2"] for o in ca), "021 rd' == rs2'"
    for form in ("c.mv", "c.add"):
        os_ = [o for o in by("mv_add") if o.p["form"] == form]
        assert {o.p["rd"] for o in os_} == set(ALLREGS) and any(o.p["rd"] == o.p["rs2"] for o in os_), f"{form} floors"
    a16 = by("addi16sp")
    assert {o.p["imm"] for o in a16 if not o.p["wrap"]} >= {-512, 496, 16, -16} and {o.p["imm"] for o in a16 if o.p["wrap"]} >= {-512, 496, 16, -16}, "016/017 nzimm classes"
    assert by("addi16sp_base") and {o.p["odd"] for o in by("illegal16sp")} == {False, True}, "016 base use / 017 illegal alignments"
    assert {o.p["odd"] for o in by("ebreak")} == {False, True}, "033 alignments"
    cj = by("cj")
    assert {(o.p["var"], o.p["pad"] % 4) for o in cj} >= {("fwd", 0), ("fwd", 2), ("bwd", 0), ("bwd", 2), ("jal", 0), ("jal", 2)}, "010 variants and alignments"
    assert {o.p["var"] for o in by("cj_ext")} == {"jal_fwd", "j_fwd"}, "011 extremes"
    cb = by("cb")
    for form in BR_OPS:
        os_ = [o for o in cb if o.p["form"] == form]
        taken = {(o.p["val"] == 0) == (form == "c.beqz") for o in os_}
        assert taken == {True, False} and {o.p["var"] for o in os_} == {"fwd", "bwd", "self"}, f"{form} outcomes"
        assert any(o.p["var"] == "fwd" and o.p["pad"] == CB_MAX_FWD - 10 for o in os_) and any(o.p["var"] == "bwd" and o.p["pad"] == -CB_MAX_BWD - 10 for o in os_), f"{form} extremes"
    assert {o.p["rs1"] for o in cb} == set(CREGS), "023 rs1' floors"
    assert {o.p["rs1"] for o in by("cjr")} == set(ALLREGS) and not any(o.p["odd"] for o in by("cjr")), "028 floors (odd targets dropped: B13)"
    assert {o.p["rs1"] for o in by("cjalr")} == set(ALLREGS), "032 floors"
    assert p.k == len(p.reports) and sum(len(v) for v in p.items.values()) == p.k and all(p.items[i] for i in ITEMS)
    assert all(0 <= ord(c) < 128 for c in p.text), "non-ASCII in the emitted program"


def red_item_of(seed, red_item):
    if red_item is None:
        return random.Random(f"{int(seed)}:{RED_TAG}").choice(RED_ITEMS)
    if red_item not in RED_ITEMS:
        raise ValueError(f"unknown red item {red_item}; one of {RED_ITEMS}")
    return red_item


def emit_text(lines, init_lw, init_sp, min_retired, header):
    L = header + ['.include "gen_mmio_map.h"', ".option norvc", "", ".section .text", ".globl _start", "_start:"]
    L += lines
    L += [f"  li   gp, {TOHOST_PASS}", "  la   t5, tohost", "  sw   gp, 0(t5)", "1:", "  j    1b", "",
          "# trap handler: report mcause, mtval, mepc; skip the 2-byte trapping instruction; return",
          ".option rvc", "  .balign 256", ".option norvc", f".globl {TRAP_VEC}", f"{TRAP_VEC}:",
          f"  csrr x{TMP}, {csr_hex('mcause')}", f"  sw x{TMP}, 0(x{EOT_REG})",
          f"  csrr x{TMP}, {csr_hex('mtval')}", f"  sw x{TMP}, 0(x{EOT_REG})",
          f"  csrr x{TMP}, {csr_hex('mepc')}", f"  sw x{TMP}, 0(x{EOT_REG})",
          f"  addi x{TMP}, x{TMP}, 2", f"  csrw {csr_hex('mepc')}, x{TMP}", "  mret", "",
          ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
          ".align 4", f"{SCR_LW}:"]
    for i in range(0, SCR_LW_BYTES, 16):
        L.append("  .byte " + ", ".join(f"0x{b:02x}" for b in init_lw[i:i + 16]))
    L += [".align 4", f"{SCR_SP}:"]
    words = [init_sp[w] for w in range(0, SCR_SP_BYTES, 4)]
    for i in range(0, len(words), 8):
        L.append("  .word " + ", ".join(f"0x{w:08x}" for w in words[i:i + 8]))
    L += [".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {min_retired}", ""]
    return "\n".join(L)


def plan(seed, red=False, red_item=None):
    rng = random.Random(f"{int(seed)}:{RNG_TAG}")
    init_lw = bytes(rng.getrandbits(8) for _ in range(SCR_LW_BYTES))
    init_sp = {w: rng.getrandbits(32) for w in range(0, SCR_SP_BYTES, 4)}
    filler_init = tuple(rng.getrandbits(32) for _ in FILLER_REGS)
    units = build_units(rng)
    rng.shuffle(units)
    ops = []
    for u in units:
        ops.extend(filler(rng) for _ in range(rng.choice((0, 0, 1, 1, 2))))
        ops.append(u)
    b, _, reports = render(ops, init_lw, init_sp, filler_init, emitted=False)
    red_item = red_item_of(seed, red_item) if red else ""
    red_note = apply_red(rng, ops, init_lw, init_sp, filler_init, red_item, reports) if red else ""
    be, lines, _ = render(ops, init_lw, init_sp, filler_init, emitted=True)
    min_retired = max(b.retire - 4, 1)
    kinds = [o.kind for o in ops if o.kind != "filler"]
    summary = {k: kinds.count(k) for k in sorted(set(kinds))}
    summary["fillers"] = sum(1 for o in ops if o.kind == "filler")
    summary["twins"] = b.twins
    summary["items"] = {i: len(b.items[i]) for i in ITEMS}
    header = [f"# gen_cmp_zca_prog.py --seed {seed}{' --red --red-item ' + red_item if red else ''}: Zca program of gen_test_cmp_zca",
              f"# k={len(reports)} report words, gen_min_retired={min_retired}, units={len(units)}, 32-bit twins={b.twins}"]
    if red:
        header.append(f"# RED FIXTURE {red_note}; the expectation keeps the true program, so the {red_item} fire-check must fail")
    text = emit_text(lines, init_lw, init_sp, min_retired, header)
    p = Plan(int(seed), bool(red), ops, reports, len(reports), min_retired, b.items, summary, red_item, red_note, text)
    check_coverage(p)
    return p


def emit(p):
    return p.text


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
        assert (g.k, g.min_retired) == (p.k, p.min_retired) and all(same_expect(x.expect, y.expect) for x, y in zip(g.reports, p.reports)), \
            "red plan expectations differ from the green plan"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(emit(p))
    print(f"OK seed={a.seed} red={red} out={a.out} k={p.k} min_retired={p.min_retired} {p.summary}"
          + (f" red_item={p.red_item} red_note={p.red_note!r}" if red else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
