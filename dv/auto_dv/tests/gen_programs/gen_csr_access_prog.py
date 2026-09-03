#!/usr/bin/env python3
"""gen_csr_access_prog: per-seed program generator of gen_test_csr_access (plan group gen_csr_access,
items TP-CSR-001/002/003/004/005/012 of dv/auto_dv/docs/gen_test_plan.md Section 4.2).

plan(seed, red=False, hart_id=0) draws every operand from random.Random(f"{seed}:program:csr_access")
through the area's layer-1 W-tables (transcribed in TABLES) and computes, from the Zicsr semantics
(tools/specs/riscv-isa-manual/src/unpriv/zicsr.adoc "CSR Instructions") and the WARL rules of the
Implemented CSR map (gen_feature_list.md Section 4.2), the report words the program stores to
GEN_MM_EOT_ADDR: the rd value of every CSR instruction and the csrr read-back that follows it, the
handler's mcause/mtval of every deliberate illegal word, and the trap count. emit(plan) renders the
RV32IMC assembly (lowRISC gcc 10.2). red=True makes the PROGRAM deviate on one intent (the first
TP-CSR-001 sequence becomes a csrrw whose operand has one writable bit flipped in the program only)
while the test keeps evaluating against plan(seed) of the green program, so fire_tp_csr_001 must fail.

Register use: x4 holds GEN_MM_EOT_ADDR, x3 the tohost code, x30/x31 belong to the trap handler
(scratch, trap counter); every random rd/rs1/filler register comes from x1, x2, x5..x29.

Operand constraints beyond the plan's C-SWEEP/C-MPRV/C-DUM rules, all imposed by the ISA comparator
as built (dv/auto_dv/isa/gen_isa_shim.cc, dv/auto_dv/env/gen_rvfi_pkg.sv; each one is a TB finding
reported with the test, and each lifts when the comparator models the DUT fact):
- mcountinhibit.IR is never set (the shim derives a retirement from Spike's minstret delta) and
  mcountinhibit operands stay inside the implemented mask (Spike keeps bits 13..31, Ibex drops them);
- mstatus.MIE stays 0 (no interrupt entry in a program whose handler skips one 32-bit word) and
  mstatus operands carry XS = 0 (Spike keeps XS and derives SD once the shim's custom-CSR extension
  is registered; Ibex has no XS);
- mcause operands are read-back fixed points (Spike models mcause as fully writable);
- cpuctrlsts is not accessed (the shim masks bit 8, ic_scr_key_valid, which the DUT reads as 1);
- minstret(h), mhpmcounter3..12 and mcycle are left out of the TP-CSR-004 sweep; hpmcounter3..12
  low halves, marchid (Spike reads 5, Ibex 0x16) and cycle (the shim's mcycle does not follow the
  DUT) are read with rd = x0 only, so those reads prove legality (no trap), not the value;
- TP-CSR-005 words are emitted only with traps > 0 (F3_100_WORDS / --traps): every deliberate trap
  ends in an mret whose rvfi_pc_wdata is the next sequential address (plan C-1), which the
  comparator's isa_pc_next row does not exempt yet. Its report words (mcause 2, mtval = word,
  mscratch untouched) are ready and passed 82/82 in bring-up.
Excluded on purpose: dscratch0/1 (debug mode is not enterable from a program at HEAD) and the
U-mode half of TP-CSR-005 (needs the C-2 PMP prologue; this program stays in M-mode).
The trap handler stays installed in every program: an unplanned trap reports mcause/mtval and
bumps the trap count, whose final report word is checked against the planned trap number.

CLI: python3 gen_csr_access_prog.py --seed N --out <file.S> [--red] [--traps N] [--dump] [--check-log <spike_commits.log>]
"""
import argparse
import random
import re
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, MEMORY_MAP  # noqa: E402
from dv.auto_dv.tests.gen_test_lib import Weighted  # noqa: E402

GROUP = "csr_access"
ITEMS = ("TP-CSR-001", "TP-CSR-002", "TP-CSR-003", "TP-CSR-004", "TP-CSR-005", "TP-CSR-012")
MASK32 = 0xFFFFFFFF
REPORT_BASE = 4      # x4: GEN_MM_EOT_ADDR
TRAP_SCRATCH = 30    # x30: handler scratch, also the mtvec restore register
TRAP_COUNT = 31      # x31: number of traps taken
POOL = [1, 2] + list(range(5, 30))
POOL_LO = [r for r in POOL if r <= 15]
POOL_HI = [r for r in POOL if r >= 16]
HANDLER_LEN = 9      # instructions the trap handler retires per trap (emit())
F3_100_WORDS = 0     # TP-CSR-005 words per seed; the plan's 40 once the comparator exempts mret records (C-1)
OPS = ("csrrw", "csrrs", "csrrc", "csrrwi", "csrrsi", "csrrci")
DEMOTED = ("csrrs", "csrrc", "csrrsi", "csrrci")
ALU_I = ("addi", "xori", "ori", "andi", "slti", "sltiu")
ALU_SH = ("slli", "srli", "srai")
ALU_R = ("add", "sub", "xor", "or", "and", "sll", "srl", "sra", "slt", "sltu")

# Layer-1 weight tables of the CSR area (gen_test_plan.md Section 4.2 "Layer-1 weight tables"); an
# item that states its own distribution overrides the table for that item only (noted per block).
TABLES = {
    "W-OP": {"csrrw": 25, "csrrs": 20, "csrrc": 20, "csrrwi": 15, "csrrsi": 10, "csrrci": 10},
    "W-PAT": {"rand": 30, "legal_only": 15, "illegal_only": 15, "all1": 10, "all0": 10, "msb_only": 5,
              "near_wrap": 5, "small": 5, "walking_one": 5},
    "W-REG-RD": {"x0": 10, "x1_x15": 45, "x16_x31": 45},
    "W-REG-RS1": {"x1_x15": 50, "x16_x31": 50},
    "W-REG-VAL": {"zero": 10, "all_ones": 10, "single_bit": 20, "uniform": 60},
    "W-UIMM": {"0": 15, "1": 15, "2_30": 55, "31": 15},
    # W-FILL without its load/store class: the data bus carries only the report stores of this program
    "W-FILL": {"none": 40, "one_alu": 25, "alu_branch_2_4": 25},
}

# CSR numbers (RISC-V privileged spec Table "Machine-level CSRs"; rtl/ibex_pkg.sv csr_num_e for the custom ones)
CSR_ADDR = {"mstatus": 0x300, "mie": 0x304, "mtvec": 0x305, "mcounteren": 0x306, "mcountinhibit": 0x320,
            "mscratch": 0x340, "mepc": 0x341, "mcause": 0x342, "mtval": 0x343,
            "cpuctrlsts": 0x7C0, "secureseed": 0x7C1,
            "mcycle": 0xB00, "minstret": 0xB02, "mcycleh": 0xB80, "minstreth": 0xB82,
            "cycle": 0xC00, "instret": 0xC02, "cycleh": 0xC80, "instreth": 0xC82,
            "mvendorid": 0xF11, "marchid": 0xF12, "mimpid": 0xF13, "mhartid": 0xF14, "mconfigptr": 0xF15}
PMPCFG0, PMPADDR0, MHPMCOUNTER3, HPMCOUNTER3, HPMCOUNTER3H = 0x3A0, 0x3B0, 0xB03, 0xC03, 0xC83
MARCHID_IBEX = 22          # RISC-V marchid registry entry of lowRISC Ibex (rtl/ibex_pkg.sv CSR_MARCHID_VALUE)
MCONFIGPTR_VALUE = 0       # rtl/ibex_pkg.sv CSR_MCONFIGPTR_VALUE
MIE_MASK = CONSTANTS["GEN_IRQ_FAST_MASK"] | (1 << 3) | (1 << 7) | (1 << 11)   # MSIE, MTIE, MEIE, fast lines
MSTATUS_BITS = (1 << 3) | (1 << 7) | (1 << 17) | (1 << 21)   # MIE, MPIE, MPRV, TW; MPP legalised apart
MSTATUS_RESTORE = 3 << 11  # MPP = M, MPRV = 0: the state every other block relies on (C-MPRV)
CPUCTRL_WMASK = 0xFF
CPUCTRL_CMP_MASK = MASK32 & ~(1 << 8)   # bit 8 (ic_scr_key_valid) is live TB state, excluded from the compare
MCAUSE_INT_FILL = 0x7FFFFFE0            # bits 30:5 read all-ones for an internal-NMI cause


@lru_cache(maxsize=None)
def build_params():
    """Integer parameters of the opentitan build configuration, read from ibex_configs.yaml (the file
    util/ibex_config.py renders the -pvalue+ options from; read directly because that tool resolves the
    yaml path against the cwd, which is the run directory inside a simulation)."""
    import yaml
    cfg = yaml.safe_load((ROOT / "ibex_configs.yaml").read_text())["opentitan"]
    params = {k: v for k, v in cfg.items() if isinstance(v, int)}
    for key in ("MHPMCounterNum", "PMPNumRegions", "PMPGranularity"):
        assert key in params, f"gen_csr_access_prog: {key} missing from the opentitan configuration"
    return params


@lru_cache(maxsize=None)
def tb_param(name):
    """Default of a 32-bit gen_dut_top.sv parameter the build configuration leaves alone (CsrMvendorId, CsrMimpId)."""
    text = (ROOT / "dv/auto_dv/tb/gen_dut_top.sv").read_text()
    m = re.search(r"parameter\s+logic\s*\[31:0\]\s+" + name + r"\s*=\s*\d+'([bdh])([0-9a-fA-F_]+)", text)
    assert m, f"gen_csr_access_prog: parameter {name} not found in gen_dut_top.sv"
    return int(m.group(2).replace("_", ""), {"b": 2, "d": 10, "h": 16}[m.group(1)])


def hpm_num():
    return build_params()["MHPMCounterNum"]


def ctr_mask():
    """Implemented bits of mcounteren / mcountinhibit: CY, IR, HPM3..(2+MHPMCounterNum); TM (bit 1) RO-zero."""
    return ((1 << (3 + hpm_num())) - 1) & ~2


def writable_mask(csr):
    """Bits a write can change (the W-PAT legal_only / illegal_only classes)."""
    if csr == "mstatus":
        return MSTATUS_BITS | (3 << 11)
    if csr == "mie":
        return MIE_MASK
    if csr == "mtvec":
        return 0xFFFFFF00
    if csr in ("mcounteren", "mcountinhibit"):
        return ctr_mask()
    if csr == "mepc":
        return MASK32 & ~1
    if csr.startswith("pmpcfg"):
        return 0x1F1F1F1F
    if csr == "cpuctrlsts":
        return CPUCTRL_WMASK & ~((1 << 2) | (1 << 6) | (1 << 7))
    return MASK32


def in_tb_window(byte_addr):
    windows = ((MEMORY_MAP["boot_page"], MEMORY_MAP["prog_size"]), (MEMORY_MAP["mmio_base"], MEMORY_MAP["mmio_size"]),
               (MEMORY_MAP["dm_base"], MEMORY_MAP["dm_size"]))
    return any(base <= byte_addr < base + size for base, size in windows)


def legal(csr, v):
    """Value that reads back after Ibex's WARL legalisation of a write of v (Implemented CSR map, gen_feature_list.md 4.2)."""
    v &= MASK32
    if csr == "mstatus":
        mpp = (v >> 11) & 3
        if mpp in (1, 2):
            mpp = 0
        return (v & MSTATUS_BITS) | (mpp << 11)
    if csr == "mie":
        return v & MIE_MASK
    if csr == "mtvec":
        return (v & 0xFFFFFF00) | 1
    if csr in ("mcounteren", "mcountinhibit"):
        return v & ctr_mask()
    if csr == "mepc":
        return v & ~1
    if csr == "mcause":
        sel, code = (v >> 30) & 3, v & 0x1F
        if sel == 3:
            return (1 << 31) | MCAUSE_INT_FILL | code
        return ((1 << 31) | code) if sel == 2 else code
    if csr.startswith("pmpcfg"):
        out = 0
        for b in range(4):
            byte = (v >> (8 * b)) & 0x9F                       # bits 6:5 reserved
            if ((byte >> 3) & 3) == 2 and build_params()["PMPGranularity"] > 0:
                byte &= ~(3 << 3)                             # NA4 unavailable with G > 0
            if (byte & 3) == 2:
                byte &= ~2                                    # W=1,R=0 reserved with MML=0: W forced 0
            out |= byte << (8 * b)
        return out
    if csr == "cpuctrlsts":
        return v & CPUCTRL_WMASK
    if csr == "secureseed":
        return 0
    return v   # mscratch, mtval, pmpaddr*, mcycle(h): every bit writable


def constrain(csr, v, rng):
    """Operand restrictions applied before a write (plan C-SWEEP / C-MPRV / C-DUM plus the shim limits in the module docstring)."""
    v &= MASK32
    if csr == "mstatus":
        v &= ~(1 << 3)
        v &= ~(3 << 15)   # XS: Spike keeps it (the shim's custom-CSR extension) and derives SD; Ibex has no XS
        if (v >> 17) & 1 and ((v >> 11) & 3) != 3:
            v &= ~(1 << 17)
    elif csr == "mcountinhibit":
        v &= ctr_mask() & ~(1 << 2)
    elif csr == "cpuctrlsts":
        v &= ~((1 << 2) | (1 << 6) | (1 << 7))
    elif csr == "mcause":
        v = legal("mcause", v)
    elif csr.startswith("pmpcfg"):
        out = 0
        for b in range(4):
            byte = (v >> (8 * b)) & 0x1F                       # L = 0, reserved bits 0
            if (byte & 3) == 2:
                byte |= 1                                     # no R=0,W=1
            out |= byte << (8 * b)
        v = out
    elif csr.startswith("pmpaddr"):
        while in_tb_window((v << 2) & MASK32):
            v = rng.getrandbits(32)
    return v


def apply_op(op, old, operand):
    """Zicsr read-modify-write: the value the CSR receives before legalisation."""
    if op in ("csrrw", "csrrwi"):
        return operand & MASK32
    if op in ("csrrs", "csrrsi"):
        return (old | operand) & MASK32
    return old & ~operand & MASK32


def li_len(v):
    """Instructions GNU as expands `li` into for a 32-bit value (1 for a 12-bit signed or lui-only value, else 2)."""
    v &= MASK32
    s = v - (1 << 32) if v & 0x80000000 else v
    return 1 if -2048 <= s < 2048 or (v & 0xFFF) == 0 else 2


@dataclass
class Expect:
    """One report word: what the test compares it with. kind eq: (got & mask) == (value & mask); same: equals report
    [ref] under mask; gt: 0 < got - report[ref] <= hi; window: lo <= got - value <= hi; base: reference word of a pair."""
    item: str
    label: str
    kind: str = "eq"
    value: int = 0
    mask: int = MASK32
    ref: int = -1
    lo: int = 0
    hi: int = 0


@dataclass
class Plan:
    seed: int
    red: bool
    hart_id: int
    tables: dict
    lines: list = field(default_factory=list)       # scenario body (assembly lines between the prologue and the epilogue)
    expected: list = field(default_factory=list)    # one Expect per report word, in store order
    min_retired: int = 0                            # main-path plus handler retirements (li counted by li_len)
    traps: int = 0                                  # deliberate illegal words
    counts: dict = field(default_factory=dict)      # sequences emitted per item
    red_note: str = ""

    @property
    def k(self):
        return len(self.expected)


class _Builder:
    def __init__(self, rng, red):
        self.rng, self.red = rng, red
        self.lines, self.expected = [], []
        self.retired = 0
        self.nlabel = 0
        self.counts = {i: 0 for i in ITEMS}
        self.red_note = ""
        self._last_report = False
        self.mcycleh = 0             # architectural mcycleh in program order (reset 0, then the sweep's writes)
        self.mcycle_may_carry = False   # a low-half write near the wrap may carry into mcycleh at an unknown point

    # ---- emission primitives ----------------------------------------------------------------------
    def ins(self, text, retire=1):
        self.lines.append("  " + text)
        self.retired += retire
        self._last_report = False

    def li(self, reg, value):
        self.ins(f"li x{reg}, 0x{value & MASK32:08x}", li_len(value))

    def csr_op(self, op, rd, csr, src):
        addr = _csr_addr(csr) if isinstance(csr, str) else csr
        self.ins(f"{op} x{rd}, 0x{addr:03x}, {src if op.endswith('i') else 'x' + str(src)}")

    def csr_read(self, rd, csr):
        self.csr_op("csrrs", rd, csr, 0)

    def csr_write(self, csr, reg):
        self.csr_op("csrrw", 0, csr, reg)

    def report(self, reg, exp):
        """Store x<reg> to the EOT register; one filler separates back-to-back report stores (one bridge edge per store)."""
        if self._last_report:
            self.filler_alu(set([reg]))
        self.ins(f"sw x{reg}, 0(x{REPORT_BASE})")
        self._last_report = True
        self.expected.append(exp)
        return len(self.expected) - 1

    def pick(self, exclude=()):
        return self.rng.choice([r for r in POOL if r not in exclude])

    # ---- layer-1 draws -----------------------------------------------------------------------------
    def draw_rd(self, allow_x0=True):
        table = dict(TABLES["W-REG-RD"])
        if not allow_x0:
            table.pop("x0")
        cls = Weighted(table).draw(self.rng)
        return 0 if cls == "x0" else self.rng.choice(POOL_LO if cls == "x1_x15" else POOL_HI)

    def draw_rs1(self):
        return self.rng.choice(POOL_LO if Weighted(TABLES["W-REG-RS1"]).draw(self.rng) == "x1_x15" else POOL_HI)

    def draw_reg_value(self):
        cls = Weighted(TABLES["W-REG-VAL"]).draw(self.rng)
        if cls == "zero":
            return 0
        if cls == "all_ones":
            return MASK32
        if cls == "single_bit":
            return 1 << self.rng.randrange(32)
        return self.rng.getrandbits(32)

    def draw_pattern(self, mask, classes=None):
        table = {k: v for k, v in TABLES["W-PAT"].items() if classes is None or k in classes}
        if mask == MASK32:
            table.pop("illegal_only", None)
        cls = Weighted(table).draw(self.rng)
        r = self.rng
        if cls == "rand":
            return r.getrandbits(32)
        if cls == "legal_only":
            return r.getrandbits(32) & mask
        if cls == "illegal_only":
            return r.getrandbits(32) & ~mask & MASK32
        if cls == "all1":
            return MASK32
        if cls == "all0":
            return 0
        if cls == "msb_only":
            return 1 << 31
        if cls == "near_wrap":
            return r.choice([MASK32 - r.randrange(16), 0x7FFFFFFF - r.randrange(16), 0x80000000 + r.randrange(16)])
        if cls == "small":
            return r.randrange(256)
        return 1 << r.randrange(32)   # walking_one

    def draw_uimm(self):
        cls = Weighted(TABLES["W-UIMM"]).draw(self.rng)
        return self.rng.randint(2, 30) if cls == "2_30" else int(cls)

    # ---- fillers (W-FILL): ALU and forward branches on registers that are not live -----------------
    def filler_alu(self, live):
        rd = self.pick(live)
        rs1, rs2 = self.rng.choice(POOL), self.rng.choice(POOL)
        kind = self.rng.choice(ALU_I + ALU_SH + ALU_R + ("lui",))
        if kind in ALU_I:
            self.ins(f"{kind} x{rd}, x{rs1}, {self.rng.randrange(-2048, 2048)}")
        elif kind in ALU_SH:
            self.ins(f"{kind} x{rd}, x{rs1}, {self.rng.randrange(32)}")
        elif kind == "lui":
            self.ins(f"lui x{rd}, 0x{self.rng.randrange(1 << 20):x}")
        else:
            self.ins(f"{kind} x{rd}, x{rs1}, x{rs2}")

    def filler_branch(self, live):
        """Forward branch over one ALU filler: beq r,r is taken (the ALU op does not retire), bne r,r is not."""
        r = self.rng.choice(POOL)
        taken = self.rng.random() < 0.5
        label = f".Lgf{self.nlabel}"
        self.nlabel += 1
        self.ins(f"{'beq' if taken else 'bne'} x{r}, x{r}, {label}")
        self.filler_alu(live)
        if taken:
            self.retired -= 1
        self.lines.append(f"{label}:")

    def fill(self, live):
        cls = Weighted(TABLES["W-FILL"]).draw(self.rng)
        n = {"none": 0, "one_alu": 1}.get(cls, self.rng.randint(2, 4))
        for _ in range(n):
            if cls == "alu_branch_2_4" and self.rng.random() < 0.25:
                self.filler_branch(live)
            else:
                self.filler_alu(live)

    def preload(self, csr, nonzero=False, classes=None):
        """csrrw x0 of a W-PAT value into csr; returns the legalised value now standing."""
        mask = writable_mask(csr)
        while True:
            v = constrain(csr, self.draw_pattern(mask, classes), self.rng)
            if not nonzero or legal(csr, v) != 0:
                break
        rp = self.pick()
        self.li(rp, v)
        self.csr_write(csr, rp)
        return legal(csr, v)

    # ---- blocks ------------------------------------------------------------------------------------
    def block_001(self, idx):
        """TP-CSR-001: <op> rd, csr, src then csrr; op/rd/src uniform per the item (overrides W-OP/W-REG for rd, rs1)."""
        item = "TP-CSR-001"
        csr = self.rng.choice(["mscratch", "mtval", "mepc", "mie", "mcountinhibit", "mcounteren", "pmpaddr"])
        if csr == "pmpaddr":
            csr = f"pmpaddr{self.rng.randrange(build_params()['PMPNumRegions'])}"
        op = self.rng.choice(OPS)
        rd = self.rng.choice(POOL)
        pre = self.preload(csr)
        if self.red and idx == 0:
            op = "csrrw"   # the red deviation needs a write whose operand decides the read-back
        if op.endswith("i"):
            while True:
                uimm = constrain(csr, self.rng.randrange(32), self.rng)
                if op == "csrrwi" or uimm != 0:
                    break
            self.csr_op(op, rd, csr, uimm)
            operand = uimm
        else:
            src = self.pick([rd])
            operand = constrain(csr, self.draw_reg_value(), self.rng)
            emitted = operand
            if self.red and idx == 0:
                flip = writable_mask(csr) & -writable_mask(csr)
                emitted = operand ^ flip
                self.red_note = f"{item} sequence 0 forced to csrrw {csr} with operand bit {flip.bit_length() - 1} flipped in the program only"
            self.li(src, emitted)
            self.csr_op(op, rd, csr, src)
        new = legal(csr, apply_op(op, pre, operand))
        self.fill({rd})
        self.report(rd, Expect(item, f"seq{idx} {op} {csr}: rd = pre-op value", "eq", pre))
        rd2 = self.pick()
        self.csr_read(rd2, csr)
        self.report(rd2, Expect(item, f"seq{idx} {csr} read-back after {op}", "eq", new))
        self.counts[item] += 1

    def block_002(self, idx):
        """TP-CSR-002: a demoted form (rs1 = x0 / uimm = 0) reads and leaves the CSR unchanged; forms uniform per the item."""
        item = "TP-CSR-002"
        csr = self.rng.choice(["mscratch", "mie", "mcountinhibit", "secureseed", "minstret"])
        form = self.rng.choice(DEMOTED)
        rd = self.draw_rd(allow_x0=csr != "minstret")
        cmp_mask = CPUCTRL_CMP_MASK if csr == "cpuctrlsts" else MASK32
        value = self.preload(csr) if csr != "minstret" else None
        self.fill({rd})
        self.csr_op(form, rd, csr, 0)
        if csr == "minstret":
            first = self.retired - 1          # instructions retired before the demoted read itself
        self.ins(f"xori x{self.pick([rd])}, x{rd}, {self.rng.randrange(-2048, 2048)}")   # dependent ALU
        rd2 = self.pick()
        if csr == "minstret":
            self.report(rd, Expect(item, f"seq{idx} {form} x0 minstret = instructions retired so far", "eq", first))
            self.csr_read(rd2, csr)
            self.report(rd2, Expect(item, f"seq{idx} minstret csrr after the demoted read", "eq", self.retired - 1))
        else:
            self.report(rd, Expect(item, f"seq{idx} {form} x0 {csr}: rd = CSR value", "eq", value if rd else 0, cmp_mask))
            self.csr_read(rd2, csr)
            self.report(rd2, Expect(item, f"seq{idx} {csr} unchanged after demoted {form}", "eq", value, cmp_mask))
        self.counts[item] += 1

    def block_003(self, idx):
        """TP-CSR-003: csrrw rd, csr, x0 / csrrwi rd, csr, 0 is a real write of zero; rd uniform over x0 and the pool."""
        item = "TP-CSR-003"
        csr = self.rng.choice(["mscratch", "mie", "mtval", "mcountinhibit", "mepc"])
        cmp_mask = CPUCTRL_CMP_MASK if csr == "cpuctrlsts" else MASK32
        value = self.preload(csr, nonzero=True)
        form = self.rng.choice(["csrrw", "csrrwi"])
        rd = self.rng.choice([0] + POOL)
        flanked = self.rng.random() < 0.5   # between two interrupt-enable manipulations (MIE stays 0)
        self.fill({rd})
        if flanked:
            self.csr_op("csrrci", 0, "mstatus", 8)
        self.csr_op(form, rd, csr, 0)
        if flanked:
            self.csr_op("csrrci", 0, "mstatus", 8)
        self.report(rd, Expect(item, f"seq{idx} {form} x0-source {csr}: rd = pre-write value", "eq", value if rd else 0, cmp_mask))
        rd2 = self.pick()
        self.csr_read(rd2, csr)
        self.report(rd2, Expect(item, f"seq{idx} {csr} reads 0 after the write of zero", "eq", 0, cmp_mask))
        self.counts[item] += 1

    def block_004(self, csr):
        """TP-CSR-004: csrrw/csrrwi x0 (W-OP restricted) writes csr, csrr reads it back, two more reads agree."""
        item = "TP-CSR-004"
        op = Weighted({k: TABLES["W-OP"][k] for k in ("csrrw", "csrrwi")}).draw(self.rng)
        if csr == "mcycleh":
            self.csr_write("mcycle", 0)                    # no carry into the high half during the read-back gap
        if csr == "mcycle":
            self.csr_op("csrrci", 0, "mcountinhibit", 1)   # CY runs, so the read-back moves
        if op == "csrrw":
            v = constrain(csr, self.draw_pattern(writable_mask(csr), ("rand", "legal_only", "all1")), self.rng)
            rs = self.pick()
            self.li(rs, v)
            self.csr_op(op, 0, csr, rs)
        else:
            v = constrain(csr, self.draw_uimm(), self.rng) & 31
            self.csr_op(op, 0, csr, v)
        exp = legal(csr, v)
        cmp_mask = CPUCTRL_CMP_MASK if csr == "cpuctrlsts" else MASK32
        if csr == "mcycleh":
            self.mcycleh, self.mcycle_may_carry = exp, False
        if csr == "mcycle":
            self.mcycle_may_carry = self.mcycle_may_carry or v >= (1 << 32) - (1 << 20)
        self.fill(set())
        rd2 = self.pick()
        self.csr_read(rd2, csr)
        if csr == "mcycle":
            self.report(rd2, Expect(item, f"{csr} read-back after {op} x0 (cycles advance)", "window", exp, lo=1, hi=256))
        else:
            self.report(rd2, Expect(item, f"{csr} read-back after {op} x0", "eq", exp, cmp_mask))
        ra = self.pick()
        rb = self.pick([ra])
        self.csr_read(ra, csr)
        self.csr_read(rb, csr)
        if csr == "mcycle":
            ia = self.report(ra, Expect(item, f"{csr} first of two reads", "base"))
            self.report(rb, Expect(item, f"{csr} second read moved by a few cycles", "gt", ref=ia, hi=64))
        else:
            ia = self.report(ra, Expect(item, f"{csr} first of two reads", "eq", exp, cmp_mask))
            self.report(rb, Expect(item, f"{csr} second read equals the first (no read side effect)", "same", ref=ia, mask=cmp_mask))
        if csr == "mstatus":
            rr = self.pick()
            self.li(rr, MSTATUS_RESTORE)
            self.csr_write("mstatus", rr)
        if csr == "mtvec":
            self.ins("la x30, gen_trap_handler", 2)
            self.csr_write("mtvec", TRAP_SCRATCH)
        self.counts[item] += 1

    def block_005(self, n_words):
        """TP-CSR-005: SYSTEM words with funct3 = 100 trap (handler reports mcause 2 and mtval = word); mscratch stays."""
        item = "TP-CSR-005"
        rp = self.pick()
        value = self.rng.getrandbits(32)
        self.li(rp, value)
        self.csr_write("mscratch", rp)
        implemented = list(CSR_ADDR.values()) + [PMPCFG0 + i for i in range(4)] + \
            [PMPADDR0 + i for i in range(build_params()["PMPNumRegions"])] + [MHPMCOUNTER3 + i for i in range(hpm_num())]
        for j in range(n_words):
            self.fill(set())
            imm = self.rng.choice(implemented) if self.rng.random() < 0.5 else self.rng.randrange(4096)
            word = (imm << 20) | (self.rng.randrange(32) << 15) | (4 << 12) | (self.rng.randrange(32) << 7) | 0x73
            self.lines.append(f"  .word 0x{word:08x}")
            self.retired += HANDLER_LEN
            self._last_report = False
            self.expected.append(Expect(item, f"word{j} 0x{word:08x}: handler mcause", "eq", 2))
            self.expected.append(Expect(item, f"word{j} 0x{word:08x}: handler mtval = the word", "eq", word))
            self.counts[item] += 1
        rq = self.pick()
        self.csr_read(rq, "mscratch")
        self.report(rq, Expect(item, "mscratch unchanged by the funct3=100 words", "eq", value))
        return n_words

    def block_012(self, name, addr, expect):
        """TP-CSR-012: a demoted form (W-OP demoted subset) reads a read-only address; expect = constant, 'pair' or 'zero_rd'."""
        item = "TP-CSR-012"
        form = Weighted({k: TABLES["W-OP"][k] for k in DEMOTED}).draw(self.rng)
        self.fill(set())
        if expect == "pair":
            if name == "cycle":
                self.csr_op("csrrci", 0, "mcountinhibit", 1)
            r1 = self.draw_rd(allow_x0=False)
            r2 = self.pick([r1])
            form2 = Weighted({k: TABLES["W-OP"][k] for k in DEMOTED}).draw(self.rng)
            self.csr_op(form, r1, addr, 0)
            first = self.retired - 1
            self.csr_op(form2, r2, addr, 0)
            if name == "cycle":
                i1 = self.report(r1, Expect(item, f"{name} via {form} x0", "base"))
                self.report(r2, Expect(item, f"{name} again via {form2} x0: later by a few cycles", "gt", ref=i1, hi=64))
            else:
                self.report(r1, Expect(item, f"{name} via {form} x0 = instructions retired so far", "eq", first))
                self.report(r2, Expect(item, f"{name} again via {form2} x0 = one more retirement", "eq", first + 1))
        elif expect == "zero_rd":
            self.csr_op(form, 0, addr, 0)   # legal read, value not comparable against the shim (hpm counters constant 0 there)
        elif expect == "mcycleh":
            rd = self.draw_rd(allow_x0=False)
            self.csr_op(form, rd, addr, 0)
            self.report(rd, Expect(item, f"{name} via {form} x0 = last mcycleh write" + (" (+carry)" if self.mcycle_may_carry else ""),
                                   "window", self.mcycleh, lo=0, hi=1 if self.mcycle_may_carry else 0))
        else:
            rd = self.draw_rd()
            self.csr_op(form, rd, addr, 0)
            self.report(rd, Expect(item, f"{name} via {form} x0" + (" (rd = x0)" if rd == 0 else ""), "eq", expect if rd else 0))
        self.counts[item] += 1


def sweep_csrs():
    """TP-CSR-004 write sweep (Implemented CSR map minus mseccfg per C-SWEEP and the shim-excluded counters)."""
    names = ["mstatus", "mie", "mtvec", "mcounteren", "mcountinhibit", "mscratch", "mepc", "mcause", "mtval",
             "mcycleh", "secureseed"]
    names += [f"pmpcfg{i}" for i in range(build_params()["PMPNumRegions"] // 4)]
    names += [f"pmpaddr{i}" for i in range(build_params()["PMPNumRegions"])]
    return names


def readonly_set(hart_id):
    """TP-CSR-012 address set: (name, address, expectation) with the constants of the Implemented CSR map."""
    n = hpm_num()
    rows = [("mvendorid", CSR_ADDR["mvendorid"], tb_param("CsrMvendorId")), ("marchid", CSR_ADDR["marchid"], "zero_rd"),
            ("mimpid", CSR_ADDR["mimpid"], tb_param("CsrMimpId")), ("mhartid", CSR_ADDR["mhartid"], hart_id),
            ("mconfigptr", CSR_ADDR["mconfigptr"], MCONFIGPTR_VALUE),
            ("cycle", CSR_ADDR["cycle"], "zero_rd"), ("cycleh", CSR_ADDR["cycleh"], "mcycleh"),
            ("instret", CSR_ADDR["instret"], "pair"), ("instreth", CSR_ADDR["instreth"], 0)]
    rows += [(f"hpmcounter{i}", HPMCOUNTER3 + i - 3, "zero_rd") for i in range(3, 3 + n)]
    rows += [(f"hpmcounter{i}h", HPMCOUNTER3H + i - 3, 0) for i in range(3, 3 + n)]          # 32-bit counters: high half 0
    rows += [(f"hpmcounter{i}", HPMCOUNTER3 + i - 3, 0) for i in range(3 + n, 32)]            # unimplemented: RO-zero in M
    rows += [(f"hpmcounter{i}h", HPMCOUNTER3H + i - 3, 0) for i in range(3 + n, 32)]
    return rows


def _csr_addr(name):
    if name.startswith("pmpcfg"):
        return PMPCFG0 + int(name[6:])
    if name.startswith("pmpaddr"):
        return PMPADDR0 + int(name[7:])
    return CSR_ADDR[name]


def plan(seed, red=False, hart_id=0, traps=F3_100_WORDS):
    rng = random.Random(f"{seed}:program:{GROUP}")
    b = _Builder(rng, red)
    # the boot stub's jump and the prologue (emit()) retire before the first block
    b.retired = 1 + li_len(MEMORY_MAP["eot_addr"]) + li_len(0) + 2 + 1
    blocks = [("001", i) for i in range(200)] + [("002", i) for i in range(100)] + [("003", i) for i in range(60)]
    blocks += [("004", csr) for csr in sweep_csrs()] + ([("005", traps)] if traps else [])
    blocks += [("012", row) for _ in range(2) for row in readonly_set(hart_id)]
    rng.shuffle(blocks)
    traps = 0
    for kind, arg in blocks:
        if kind == "001":
            b.block_001(arg)
        elif kind == "002":
            b.block_002(arg)
        elif kind == "003":
            b.block_003(arg)
        elif kind == "004":
            b.block_004(arg)
        elif kind == "005":
            traps += b.block_005(arg)
        else:
            b.block_012(*arg)
    # TP-CSR-001 asks that every op retire without trap: the handler's count must equal the planned traps
    b.report(TRAP_COUNT, Expect("TP-CSR-001", f"trap count: {traps} planned traps, no CSR op trapped", "eq", traps))
    return Plan(seed=seed, red=red, hart_id=hart_id, tables=TABLES, lines=b.lines, expected=b.expected,
                min_retired=b.retired, traps=traps, counts=b.counts, red_note=b.red_note)


def emit(plan):
    head = [
        f"# gen_csr_access_prog seed={plan.seed} red={int(plan.red)} reports={plan.k} traps={plan.traps}"
        + (f" ({plan.red_note})" if plan.red_note else ""),
        '.include "gen_mmio_map.h"',
        ".section .text",
        ".globl _start",
        "_start:",
        f"  li x{REPORT_BASE}, GEN_MM_EOT_ADDR",
        f"  li x{TRAP_COUNT}, 0",
        f"  la x{TRAP_SCRATCH}, gen_trap_handler",
        f"  csrrw x0, 0x{CSR_ADDR['mtvec']:03x}, x{TRAP_SCRATCH}",
    ]
    tail = [
        "  li gp, 1",
        "  la t5, tohost",
        "  sw gp, 0(t5)",
        "1:",
        "  j 1b",
        "",
        "# trap handler (mtvec base, 256-byte aligned): report mcause and mtval, skip the 32-bit word, count",
        ".p2align 8",
        "gen_trap_handler:",
        f"  csrrs x{TRAP_SCRATCH}, 0x{CSR_ADDR['mcause']:03x}, x0",
        f"  sw x{TRAP_SCRATCH}, 0(x{REPORT_BASE})",
        f"  csrrs x{TRAP_SCRATCH}, 0x{CSR_ADDR['mtval']:03x}, x0",
        f"  sw x{TRAP_SCRATCH}, 0(x{REPORT_BASE})",
        f"  csrrs x{TRAP_SCRATCH}, 0x{CSR_ADDR['mepc']:03x}, x0",
        f"  addi x{TRAP_SCRATCH}, x{TRAP_SCRATCH}, 4",
        f"  csrrw x0, 0x{CSR_ADDR['mepc']:03x}, x{TRAP_SCRATCH}",
        f"  addi x{TRAP_COUNT}, x{TRAP_COUNT}, 1",
        "  mret",
        "",
        ".section .data",
        ".align 6",
        ".globl tohost",
        "tohost:   .dword 0",
        ".globl fromhost",
        "fromhost: .dword 0",
        ".align 2",
        ".globl gen_min_retired",
        f"gen_min_retired: .word {plan.min_retired}",
        "",
    ]
    return "\n".join(head + plan.lines + tail)


def evaluate(plan, reports, item):
    """Compare the item's report words with the plan: (checked, failures), failures as 'idx label: expected .. got ..'."""
    checked, bad = 0, []
    for i, e in enumerate(plan.expected):
        if e.item != item or e.kind == "base":
            continue
        checked += 1
        if i >= len(reports) or (e.ref >= 0 and e.ref >= len(reports)):
            bad.append(f"[{i}] {e.label}: report missing")
            continue
        got = reports[i]
        if e.kind == "eq":
            ok, want = (got & e.mask) == (e.value & e.mask), f"0x{e.value & e.mask:08x}" + ("" if e.mask == MASK32 else f" under mask 0x{e.mask:08x}")
        elif e.kind == "same":
            ok, want = (got & e.mask) == (reports[e.ref] & e.mask), f"report[{e.ref}] 0x{reports[e.ref]:08x}"
        elif e.kind == "gt":
            d = (got - reports[e.ref]) & MASK32
            ok, want = 1 <= d <= e.hi, f"report[{e.ref}] 0x{reports[e.ref]:08x} + 1..{e.hi}"
        elif e.kind == "window":
            d = (got - e.value) & MASK32
            ok, want = e.lo <= d <= e.hi, f"0x{e.value:08x} + {e.lo}..{e.hi}"
        else:
            raise AssertionError(f"gen_csr_access_prog: unknown expectation kind {e.kind}")
        if not ok:
            bad.append(f"[{i}] {e.label}: expected {want}, got 0x{got:08x}")
    return checked, bad


def reports_from_spike_log(path):
    """Report stores of a standalone Spike --log-commits run (host cross-check; diverges after the first custom CSR)."""
    pat = re.compile(r"mem 0x%08x 0x([0-9a-f]{8})" % MEMORY_MAP["eot_addr"])
    return [int(m.group(1), 16) for m in pat.finditer(Path(path).read_text())]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, help="assembly file to write")
    ap.add_argument("--red", action="store_true", help="red fixture: the program deviates on one intent")
    ap.add_argument("--hart-id", type=lambda s: int(s, 0), default=0, help="hart_id_i the TB drives (mhartid expectation)")
    ap.add_argument("--traps", type=int, default=F3_100_WORDS, help="TP-CSR-005 funct3=100 words per seed")
    ap.add_argument("--dump", action="store_true", help="print the expected report words")
    ap.add_argument("--check-log", type=Path, help="compare a Spike commit log's report stores with the plan")
    a = ap.parse_args()
    p = plan(a.seed, a.red, a.hart_id, a.traps)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(emit(p))
    if a.dump:
        for i, e in enumerate(p.expected):
            print(f"[{i}] {e.item} {e.kind} 0x{e.value:08x} mask=0x{e.mask:08x} ref={e.ref} {e.label}")
    if a.check_log:
        got = reports_from_spike_log(a.check_log)
        print(f"spike report stores: {len(got)} (plan k={p.k})")
        for item in ITEMS:
            n, bad = evaluate(p, got, item)
            print(f"{item}: {n - len(bad)}/{n} ok" + (f"; first {bad[0]}" if bad else ""))
    print(f"OK seed={a.seed} red={int(a.red)} k={p.k} min_retired={p.min_retired} traps={p.traps} counts={p.counts}"
          + (f" red_note={p.red_note!r}" if p.red_note else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
