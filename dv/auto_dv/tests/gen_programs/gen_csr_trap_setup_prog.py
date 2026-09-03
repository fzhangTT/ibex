#!/usr/bin/env python3
"""gen_csr_trap_setup_prog: per-seed program generator of gen_test_csr_trap_setup (test-plan group
gen_csr_trap_setup; built items TP-CSR-023, 024, 025, 027, 028, 029, 030, 035, 036).

plan(seed, red=False) -> Plan: the randomized CSR operations of one seed, drawn from
random.Random(f"{seed}:program:csr_trap_setup") with the layer-1 weight tables of gen_test_plan.md
Section 4.2 (transcribed in TABLES), the expected report words in program order (the RAW read-back
values the program stores to GEN_MM_EOT_ADDR, predicted from the WARL rules Ibex implements), k (the
report count), min_retired (a lower bound of the instructions the straight-line program retires) and
per-item stimulus facts (which MPP values, TW/MPRV, fast bits, handler copies a seed exercised).
red=True makes the PROGRAM write one TP-CSR-036 mtvec operand with bit 8 flipped while the expectation
keeps the intended operand (TDD red fixture: exactly one fire-check must fail). emit(plan) -> the
RV32IMC assembly text (lowRISC gcc 10.2, -march=rv32imcb; CSRs by number, binutils 2.35 has no
menvcfg mnemonic).

WARL rules (doc/03_reference/cs_registers.rst; rtl/ibex_cs_registers.sv write logic): mstatus stores
bits 3 MIE, 7 MPIE, 12:11 MPP, 17 MPRV, 21 TW, an MPP of 01/10 becomes 00 (doc mismatch D2, the RTL
is followed); mie stores MIE_MASK = fast bits | 0x888; mtvec keeps BASE[31:8], forces [7:2] = 0 and
MODE = 01; mstatush, menvcfg, menvcfgh read 0 and take writes without a trap.

Program rules: no interrupt agent exists in the build, so irq pins stay low; the mstatus items run with
mie = 0 and the mie items with mstatus.MIE = 0 (their stated preconditions, which also keep the standalone
Spike run free of its CLINT timer interrupt, pending from reset with mtimecmp = 0); C-MPRV (plan Section 4.2): a data access never runs with MPRV = 1 and MPP != 11 (a csrrc of MPRV is
emitted before a store when the model says so); four 256-byte-aligned trap handler copies
(gen_tvec_h0..3) store a per-copy marker and mcause for the ecall rounds and count every other trap
(the final report words are that count and the last unexpected mcause); the mtvec value that stands
when a trap follows keeps bits 7:2 = 0 because the standalone Spike run vectors exceptions to
mtvec & ~1 (the TB's shim legalizes mtvec, the sanity run does not); random bits 7:2 are read back
in TP-CSR-036, where no trap follows. Expected words that are link addresses are Sym objects the test
resolves from the image sidecar (the one source of link addresses).

CLI: python3 gen_csr_trap_setup_prog.py --seed N --out <file.S> [--red]
"""
import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, MEMORY_MAP  # noqa: E402

GROUP = "csr_trap_setup"
MASK32 = 0xFFFFFFFF

# CSR numbers (RISC-V privileged specification, tools/specs)
CSR_MSTATUS, CSR_MIE, CSR_MTVEC = 0x300, 0x304, 0x305
CSR_MSTATUSH, CSR_MENVCFG, CSR_MENVCFGH = 0x310, 0x30A, 0x31A
CSR_MEPC, CSR_MCAUSE = 0x341, 0x342
CSR_PMPCFG0, CSR_PMPADDR0 = 0x3A0, 0x3B0
CSR_NAME = {CSR_MSTATUS: "mstatus", CSR_MIE: "mie", CSR_MTVEC: "mtvec", CSR_MSTATUSH: "mstatush",
            CSR_MENVCFG: "menvcfg", CSR_MENVCFGH: "menvcfgh"}

# mstatus fields Ibex implements (cs_registers.rst "Machine Status")
MST_MIE, MST_MPIE, MST_MPP_LO, MST_MPRV, MST_TW = 3, 7, 11, 17, 21
MST_LEGAL_BITS = (MST_MIE, MST_MPIE, MST_MPP_LO, MST_MPP_LO + 1, MST_MPRV, MST_TW)
MST_MASK = sum(1 << b for b in MST_LEGAL_BITS)            # 0x0022_1888
MST_RESET = 1 << MST_MPIE                                  # 0x80
PRIV_M, PRIV_U = 3, 0
# mie: standard enables MSIE/MTIE/MEIE plus the fast lines (ibex_pkg irqs_t; width from the rendered constants)
MIE_STD_BITS = (3, 7, 11)
MIE_STD_MASK = sum(1 << b for b in MIE_STD_BITS)          # 0x888
MIE_FAST_LO = 16
MIE_FAST_W = CONSTANTS["GEN_IRQ_FAST_W"]
MIE_FAST_MASK = CONSTANTS["GEN_IRQ_FAST_MASK"]
MIE_MASK = MIE_FAST_MASK | MIE_STD_MASK                    # 0x7FFF_0888
assert MIE_FAST_MASK == ((1 << MIE_FAST_W) - 1) << MIE_FAST_LO, "rendered fast-irq constants disagree"
MTVEC_BASE_MASK = 0xFFFFFF00
MTVEC_MODE_VECTORED = 1
CAUSE_ECALL_U, CAUSE_ECALL_M = 8, 11
# menvcfg field positions the item names (privileged spec 1.12: FIOM 0, CBIE 5:4, CBCFE 6, CBZE 7; menvcfgh PBMTE 30, STCE 31)
MENVCFG_FIELD_BITS = (0, 4, 5, 6, 7)
MENVCFGH_FIELD_BITS = (30, 31)

BOOT_PAGE = MEMORY_MAP["boot_page"]
PROG_END = MEMORY_MAP["boot_page"] + MEMORY_MAP["prog_size"]
PMP_TOR_RWX = 0x0F                 # pmpcfg byte: A = TOR, X W R set, L clear (C-2 U-mode prologue)
NUM_HANDLER_COPIES = 4
HANDLER_SYMBOL = "gen_tvec_h{}"
HANDLER_ECALL_INSNS = 12           # instructions of the handler's ecall path (M-mode entry; the U entry runs 14)
PROGRAM_ITEM = "PROGRAM"           # report words about the program itself (unexpected-trap count, last cause)

# Registers: x27 EOT address, x26/x23 handler scratch, x25 unexpected-trap counter, x24 its last mcause
R_EOT, R_HS0, R_HS1, R_TRAPS, R_LASTC = 27, 26, 23, 25, 24
RESERVED = {R_EOT, R_HS0, R_HS1, R_TRAPS, R_LASTC}
LOW_REGS = tuple(n for n in range(1, 16) if n not in RESERVED)
HIGH_REGS = tuple(n for n in range(16, 32) if n not in RESERVED)

# Layer-1 weight tables, transcribed from gen_test_plan.md Section 4.2 "Layer-1 weight tables" and the
# items' Stimulus lines; classes a CSR or an op form cannot take are dropped and the rest renormalised.
TABLES = {
    "W-OP": {"csrrw": 25, "csrrs": 20, "csrrc": 20, "csrrwi": 15, "csrrsi": 10, "csrrci": 10},
    "W-REG rd": {"x0": 10, "low": 45, "high": 45},
    "W-REG rs1": {"low": 50, "high": 50},
    "W-REG rs1 value": {"zero": 10, "all1": 10, "single": 20, "uniform": 60},
    "W-UIMM": {"0": 15, "1": 15, "mid": 55, "31": 15},
    "W-GAP": {"0": 40, "1": 30, "2_4": 20, "5_16": 10},
    "TP-CSR-023 class": {"rand": 40, "legal_only": 20, "illegal_only": 15, "all1": 10, "all0": 10, "msb_only": 5},
    "TP-CSR-027 pattern": {"rand": 25, "all1": 25, "all0": 25, "msb": 25},
    "TP-CSR-028 pattern": {"rand": 20, "all1": 20, "all0": 20, "msb": 20, "fields": 20},
    "TP-CSR-029 class": {"std_only": 15, "fast_only": 15, "std_fast": 20, "ro_only": 15, "all_fast": 10, "rand": 25},
}
PAIRS_023, ROUNDS_024, ROUNDS_025, PAIRS_027, PAIRS_028_PER_CSR = 200, 30, 10, 30, 30
PAIRS_029, ROUNDS_030, ROUNDS_035, PAIRS_036 = 150, 10, 40, 40
ITEMS_BUILT = ("TP-CSR-023", "TP-CSR-024", "TP-CSR-025", "TP-CSR-027", "TP-CSR-028", "TP-CSR-029",
               "TP-CSR-030", "TP-CSR-035", "TP-CSR-036")


@dataclass(frozen=True)
class Sym:
    """Expected word = link address of `symbol` (a 256-byte-aligned handler copy) | or_mask."""
    symbol: str
    or_mask: int = 0


@dataclass
class Plan:
    seed: int
    red: bool
    k: int
    expected: list
    labels: list
    items: dict
    min_retired: int
    facts: dict
    markers: dict
    block_order: list
    lines: list = field(repr=False)
    handler_lines: list = field(repr=False)
    tables: dict = field(default_factory=lambda: TABLES, repr=False)


def csr_op(op, old, operand):
    """Value a CSR write instruction presents to the register (csr_wdata_int)."""
    if op in ("csrrw", "csrrwi"):
        return operand & MASK32
    if op in ("csrrs", "csrrsi"):
        return (old | operand) & MASK32
    return old & ~operand & MASK32


def legal_mstatus(v):
    v &= MST_MASK
    if (v >> MST_MPP_LO) & 3 in (1, 2):
        v &= ~(3 << MST_MPP_LO)
    return v


def legal_mie(v):
    return v & MIE_MASK


def legal_mtvec(v):
    return (v & MTVEC_BASE_MASK) | MTVEC_MODE_VECTORED


def resolve(expected, symbols):
    """Concrete expected word: an int as is, a Sym through the image sidecar's symbol table."""
    if isinstance(expected, Sym):
        assert expected.symbol in symbols, f"GEN_TEST: program image defines no symbol {expected.symbol}"
        addr = int(symbols[expected.symbol], 16)
        assert addr & ~MTVEC_BASE_MASK == 0, f"GEN_TEST: {expected.symbol} at 0x{addr:08x} is not 256-byte aligned"
        return addr | expected.or_mask
    return expected


def mismatches(plan, item, reports, symbols):
    """Report words of `item` that differ from the plan ('[idx] label: expected .. got ..'), and the count checked."""
    idxs = plan.items.get(item, [])
    bad = []
    for i in idxs:
        exp = resolve(plan.expected[i], symbols)
        got = reports[i] if i < len(reports) else None
        if got != exp:
            got_s = "none" if got is None else f"0x{got:08x}"
            bad.append(f"[{i}] {plan.labels[i]}: expected 0x{exp:08x} got {got_s}")
    return bad, len(idxs)


class _Builder:
    def __init__(self, seed, red):
        self.seed, self.red = seed, red
        self.rng = random.Random(f"{seed}:program:{GROUP}")
        self.red_pending = red
        self.lines, self.expected, self.labels, self.items = [], [], [], {}
        self.n_insn, self.n_ecall, self.n_label = 0, 0, 0
        self.mstatus, self.mie = MST_RESET, 0
        self.mtvec = BOOT_PAGE | MTVEC_MODE_VECTORED   # int, or ("sym", copy) once a handler copy is installed
        self.facts = {}
        used = set()
        self.markers = {}
        for k in range(NUM_HANDLER_COPIES):
            while True:
                m = self.rng.getrandbits(32) | 0x80000001
                if m not in used and m != MASK32:
                    break
            used.add(m)
            self.markers[k] = m

    # ---- draws -------------------------------------------------------------------------------
    def draw(self, table):
        names = list(table)
        return self.rng.choices(names, weights=[table[n] for n in names], k=1)[0]

    def pick_reg(self, table="W-REG rs1", exclude=()):
        pool = LOW_REGS if self.draw(TABLES[table]) == "low" else HIGH_REGS
        pool = [r for r in pool if r not in exclude]
        return self.rng.choice(pool)

    def pick_rd(self):
        cls = self.draw(TABLES["W-REG rd"])
        if cls == "x0":
            return 0
        return self.rng.choice(LOW_REGS if cls == "low" else HIGH_REGS)

    def rs1_value(self):
        cls = self.draw(TABLES["W-REG rs1 value"])
        if cls == "zero":
            return 0
        if cls == "all1":
            return MASK32
        if cls == "single":
            return 1 << self.rng.randrange(32)
        return self.rng.getrandbits(32)

    def uimm(self):
        cls = self.draw(TABLES["W-UIMM"])
        return {"0": 0, "1": 1, "31": 31}.get(cls, self.rng.randint(2, 30))

    def subset(self, bits, nonempty=True):
        while True:
            v = sum(1 << b for b in bits if self.rng.random() < 0.5)
            if v or not nonempty:
                return v

    # ---- emission ----------------------------------------------------------------------------
    def emit(self, text, retire=1):
        self.lines.append("  " + text)
        self.n_insn += retire

    def li(self, reg, value):
        self.emit(f"li x{reg}, 0x{value & MASK32:08x}")   # lui+addi pairs count once: min_retired stays a floor

    def new_label(self, stem):
        self.n_label += 1
        return f"gen_{stem}_{self.n_label}"

    def filler(self):
        rd, ra, rb = self.rng.choice(LOW_REGS + HIGH_REGS), self.rng.choice(LOW_REGS + HIGH_REGS), self.rng.choice(LOW_REGS + HIGH_REGS)
        kind = self.rng.randrange(4)
        if kind == 0:
            self.emit(f"{self.rng.choice(['add', 'sub', 'xor', 'or', 'and', 'sll', 'srl', 'sra', 'slt', 'sltu'])} x{rd}, x{ra}, x{rb}")
        elif kind == 1:
            self.emit(f"{self.rng.choice(['addi', 'xori', 'ori', 'andi'])} x{rd}, x{ra}, {self.rng.randint(-2048, 2047)}")
        elif kind == 2:
            self.emit(f"{self.rng.choice(['slli', 'srli', 'srai'])} x{rd}, x{ra}, {self.rng.randrange(32)}")
        else:
            self.emit(f"lui x{rd}, 0x{self.rng.getrandbits(20):05x}")

    def gap(self):
        """W-GAP: unrelated ALU instructions between a CSR write and its dependent read-back."""
        cls = self.draw(TABLES["W-GAP"])
        n = {"0": 0, "1": 1}.get(cls, self.rng.randint(2, 4) if cls == "2_4" else self.rng.randint(5, 16))
        for _ in range(n):
            self.filler()

    def csr_write(self, op, csr, operand, rd=None, rs1=None, prog_operand=None):
        """One CSR write; operand is the rs1 value (register forms) or the 5-bit uimm. prog_operand
        overrides what the PROGRAM writes (red fixture) while the caller models `operand`."""
        rd = self.pick_rd() if rd is None else rd
        value = operand if prog_operand is None else prog_operand
        if op.endswith("i"):
            self.emit(f"{op} x{rd}, 0x{csr:x}, {value & 31}")
        else:
            rs1 = self.pick_reg(exclude=()) if rs1 is None else rs1
            self.li(rs1, value)
            self.emit(f"{op} x{rd}, 0x{csr:x}, x{rs1}")

    def mprv_guard(self, exclude=()):
        """C-MPRV: clear MPRV before a data access when MPP != M (the LSU would run U-privileged)."""
        if (self.mstatus >> MST_MPRV) & 1 and (self.mstatus >> MST_MPP_LO) & 3 != PRIV_M:
            r = self.pick_reg(exclude=exclude)
            self.li(r, 1 << MST_MPRV)
            self.emit(f"csrrc x0, 0x{CSR_MSTATUS:x}, x{r}")
            self.mstatus &= ~(1 << MST_MPRV)

    def report_reg(self, reg, expected, item, label):
        self.mprv_guard(exclude=(reg,))
        self.emit(f"sw x{reg}, 0(x{R_EOT})")
        self.expected.append(expected)
        self.labels.append(label)
        self.items.setdefault(item, []).append(len(self.expected) - 1)

    def readback(self, csr, expected, item, label, exclude=()):
        """csrr of `csr` into a fresh register, then its report store (the guard runs after the read)."""
        rd = self.pick_reg(exclude=exclude)
        self.emit(f"csrrs x{rd}, 0x{csr:x}, x0")
        self.report_reg(rd, expected, item, label)

    def snapshot_traps(self, item, label):
        self.report_reg(R_TRAPS, 0, item, label)

    # ---- privilege model ---------------------------------------------------------------------
    def trap_enter(self, priv):
        mie = (self.mstatus >> MST_MIE) & 1
        self.mstatus &= ~((1 << MST_MIE) | (1 << MST_MPIE) | (3 << MST_MPP_LO))
        self.mstatus |= (mie << MST_MPIE) | (priv << MST_MPP_LO)

    def mret(self):
        """mret: MIE = MPIE, MPIE = 1, MPP = U, MPRV cleared when MPP was not M (rtl/ibex_cs_registers.sv:954-978)."""
        mpp = (self.mstatus >> MST_MPP_LO) & 3
        mpie = (self.mstatus >> MST_MPIE) & 1
        self.mstatus &= ~((1 << MST_MIE) | (3 << MST_MPP_LO))
        self.mstatus |= (mpie << MST_MIE) | (1 << MST_MPIE) | (PRIV_U << MST_MPP_LO)
        if mpp != PRIV_M:
            self.mstatus &= ~(1 << MST_MPRV)
        return PRIV_M if mpp == PRIV_M else PRIV_U

    def handler_round_trip(self, priv, item, label):
        """An ecall in privilege `priv` reaches the installed handler copy: it reports its marker and
        mcause, sets MPP = M and returns to the instruction after the ecall."""
        assert isinstance(self.mtvec, tuple), "an ecall with mtvec on no handler copy would lock the core"
        copy = self.mtvec[1]
        self.n_ecall += 1
        self.trap_enter(priv)
        cause = CAUSE_ECALL_M if priv == PRIV_M else CAUSE_ECALL_U
        self.expected.append(self.markers[copy])
        self.labels.append(f"{label}: handler copy marker (gen_tvec_h{copy})")
        self.items.setdefault(item, []).append(len(self.expected) - 1)
        self.expected.append(cause)
        self.labels.append(f"{label}: mcause ({'ecall from M' if priv == PRIV_M else 'ecall from U'})")
        self.items.setdefault(item, []).append(len(self.expected) - 1)
        self.mstatus |= PRIV_M << MST_MPP_LO
        self.mret()

    def mtvec_expected(self):
        if isinstance(self.mtvec, tuple):
            return Sym(HANDLER_SYMBOL.format(self.mtvec[1]), MTVEC_MODE_VECTORED)
        return self.mtvec

    def install_mtvec(self, copy, mode, rs1=None):
        """csrrw mtvec with the address of handler copy `copy` | mode (mode in bits 1:0 only)."""
        rs1 = self.pick_reg() if rs1 is None else rs1
        self.emit(f"la x{rs1}, {HANDLER_SYMBOL.format(copy)}", retire=2)
        if mode:
            self.emit(f"ori x{rs1}, x{rs1}, {mode}")
        self.emit(f"csrrw x{self.pick_rd()}, 0x{CSR_MTVEC:x}, x{rs1}")
        self.mtvec = ("sym", copy)

    # ---- program sections ---------------------------------------------------------------------
    def prologue(self):
        self.emit(f"li x{R_EOT}, GEN_MM_EOT_ADDR")
        self.readback(CSR_MSTATUSH, 0, "TP-CSR-027", "mstatush read at boot")
        self.install_mtvec(0, 0)
        self.readback(CSR_MTVEC, self.mtvec_expected(), "TP-CSR-035", "mtvec after installing handler copy 0")
        self.li(R_TRAPS, 0)
        self.li(R_LASTC, 0)
        r = self.pick_reg()
        self.li(r, PROG_END >> 2)
        self.emit(f"csrrw x0, 0x{CSR_PMPADDR0:x}, x{r}")
        self.li(r, PMP_TOR_RWX)
        self.emit(f"csrrw x0, 0x{CSR_PMPCFG0:x}, x{r}")

    def no_enabled_irq(self):
        """Precondition of the mstatus items: no enabled interrupt, so MIE writes have no side effect
        (the standalone Spike run has a pending timer interrupt from its CLINT; the TB's irq pins are low)."""
        self.emit(f"csrrw x0, 0x{CSR_MIE:x}, x0")
        self.mie = 0

    def mstatus_mie_off(self):
        """Precondition of the mie items: mstatus.MIE = 0 while mie bits are written at random."""
        self.emit(f"csrrci x0, 0x{CSR_MSTATUS:x}, {1 << MST_MIE}")
        self.mstatus &= ~(1 << MST_MIE)

    def mstatus_operand(self, cls, imm, mpp_uniform):
        if imm:
            if cls == "rand":
                return self.uimm()
            if cls == "illegal_only":
                return self.subset((0, 1, 2, 4))
            return {"legal_only": 1 << MST_MIE, "all1": 31, "all0": 0, "msb_only": 16}[cls]
        if cls == "rand":
            v = self.rs1_value()
        elif cls == "legal_only":
            v = self.subset(MST_LEGAL_BITS)
        elif cls == "illegal_only":
            v = self.subset([b for b in range(32) if b not in MST_LEGAL_BITS])
        elif cls == "all1":
            v = MASK32
        elif cls == "all0":
            v = 0
        else:
            v = 1 << 31
        if cls in ("rand", "legal_only"):
            v = (v & ~(3 << MST_MPP_LO)) | (mpp_uniform << MST_MPP_LO)
        return v & MASK32

    def mstatus_pair(self, op, cls, operand, item, label):
        new = csr_op(op, self.mstatus, operand)
        f = self.facts[item]
        if not op.endswith("i"):
            f["mpp_written"].add((new >> MST_MPP_LO) & 3)
        f["tw_written"] |= bool((new >> MST_TW) & 1)
        f["mprv_written"] |= bool((new >> MST_MPRV) & 1)
        f["ops"].add(op)
        f["classes"].add(cls)
        self.csr_write(op, CSR_MSTATUS, operand)
        self.mstatus = legal_mstatus(new)
        self.gap()
        self.readback(CSR_MSTATUS, self.mstatus, item, label)

    def block_023(self):
        item = "TP-CSR-023"
        self.facts[item] = {"mpp_written": set(), "tw_written": False, "mprv_written": False, "ops": set(), "classes": set(), "pairs": 0}
        self.no_enabled_irq()
        for i in range(PAIRS_023):
            op, cls = self.draw(TABLES["W-OP"]), self.draw(TABLES["TP-CSR-023 class"])
            operand = self.mstatus_operand(cls, op.endswith("i"), self.rng.randrange(4))
            self.mstatus_pair(op, cls, operand, item, f"mstatus pair {i} {op} {cls} operand 0x{operand:08x}")
        f = self.facts[item]
        for mpp in sorted({0, 1, 2, 3} - f["mpp_written"]):   # directed pins for corners the random stream missed
            operand = self.subset([MST_MIE, MST_MPIE, MST_TW], nonempty=False) | (mpp << MST_MPP_LO)
            self.mstatus_pair("csrrw", "legal_only", operand, item, f"mstatus directed csrrw MPP {mpp:02b} operand 0x{operand:08x}")
        for bit, name in ((MST_TW, "TW"), (MST_MPRV, "MPRV")):
            if not f[{"TW": "tw_written", "MPRV": "mprv_written"}[name]]:
                operand = (1 << bit) | (PRIV_M << MST_MPP_LO)
                self.mstatus_pair("csrrs", "legal_only", operand, item, f"mstatus directed csrrs {name} operand 0x{operand:08x}")
        f["pairs"] = len(self.items[item])

    def block_024(self):
        item = "TP-CSR-024"
        self.facts[item] = {"mpp_written": set(), "rounds": 0, "u_rounds": 0}
        self.no_enabled_irq()
        plan = [self.rng.randrange(4) for _ in range(ROUNDS_024)]
        plan += sorted({0, 1, 2, 3} - set(plan))
        for i, mpp in enumerate(plan):
            op = self.rng.choice(["csrrw", "csrrs"])
            fields = self.subset([MST_MIE, MST_MPIE, MST_TW, MST_MPRV], nonempty=False)
            if op == "csrrw":
                operand = fields | (mpp << MST_MPP_LO)
                self.csr_write("csrrw", CSR_MSTATUS, operand)
                new = csr_op("csrrw", self.mstatus, operand)
            else:
                self.csr_write("csrrw", CSR_MSTATUS, fields)
                self.mstatus = legal_mstatus(fields)
                operand = (mpp << MST_MPP_LO) | self.subset([MST_MIE, MST_MPIE, MST_TW], nonempty=False)
                self.csr_write("csrrs", CSR_MSTATUS, operand)
                new = csr_op("csrrs", self.mstatus, operand)
            self.facts[item]["mpp_written"].add((new >> MST_MPP_LO) & 3)
            self.mstatus = legal_mstatus(new)
            legal = self.mstatus
            self.gap()
            rb = self.pick_reg()
            self.emit(f"csrrs x{rb}, 0x{CSR_MSTATUS:x}, x0")
            t = self.pick_reg(exclude=(rb,))
            label = self.new_label("u")
            self.emit(f"la x{t}, {label}", retire=2)
            self.emit(f"csrrw x0, 0x{CSR_MEPC:x}, x{t}")
            self.emit("mret")
            priv = self.mret()
            self.lines.append(f"{label}:")
            self.emit("ecall", retire=0)
            self.handler_round_trip(priv, item, f"round {i} {op} MPP {mpp:02b} written")
            self.facts[item]["rounds"] += 1
            self.facts[item]["u_rounds"] += int(priv == PRIV_U)
            self.report_reg(rb, legal, item, f"round {i} mstatus read-back ({op} MPP {mpp:02b} written, legal MPP {(legal >> MST_MPP_LO) & 3:02b})")

    def block_025(self):
        item = "TP-CSR-025"
        self.facts[item] = {"rounds": ROUNDS_025}
        self.no_enabled_irq()
        for i in range(ROUNDS_025):
            ops = ["csrrw", "csrrs", "csrrc"]
            self.rng.shuffle(ops)
            for op in ops:
                self.csr_write(op, CSR_MSTATUS, MASK32)
                self.mstatus = legal_mstatus(csr_op(op, self.mstatus, MASK32))
                self.gap()
                self.readback(CSR_MSTATUS, self.mstatus, item, f"round {i} {op} mstatus, -1")

    def zero_csr_pairs(self, csrs, table, item):
        """Write/read-back pairs on CSRs that read 0 and ignore writes (mstatush, menvcfg, menvcfgh)."""
        for i, csr in enumerate(csrs):
            field_bits = {CSR_MENVCFG: MENVCFG_FIELD_BITS, CSR_MENVCFGH: MENVCFGH_FIELD_BITS}.get(csr, ())
            op, pat = self.draw(TABLES["W-OP"]), self.draw(TABLES[table])
            imm = op.endswith("i")
            if pat == "rand":
                operand = self.uimm() if imm else self.rs1_value()
            elif pat == "all1":
                operand = 31 if imm else MASK32
            elif pat == "all0":
                operand = 0
            elif pat == "msb":
                operand = 16 if imm else 1 << 31
            else:
                low = [b for b in field_bits if b < 5]
                operand = (self.subset(low) if low else self.uimm()) if imm else self.subset(field_bits)
            self.csr_write(op, csr, operand)
            self.gap()
            self.readback(csr, 0, item, f"{CSR_NAME[csr]} pair {i} {op} {pat} operand 0x{operand:08x}")

    def block_027(self):
        item = "TP-CSR-027"
        self.facts[item] = {"pairs": PAIRS_027}
        self.zero_csr_pairs([CSR_MSTATUSH] * PAIRS_027, "TP-CSR-027 pattern", item)
        self.snapshot_traps(item, "unexpected-trap count after the mstatush pairs")

    def block_028(self):
        item = "TP-CSR-028"
        self.facts[item] = {"pairs": 2 * PAIRS_028_PER_CSR}
        order = [CSR_MENVCFG] * PAIRS_028_PER_CSR + [CSR_MENVCFGH] * PAIRS_028_PER_CSR
        self.rng.shuffle(order)
        self.zero_csr_pairs(order, "TP-CSR-028 pattern", item)
        self.snapshot_traps(item, "unexpected-trap count after the menvcfg/menvcfgh pairs")

    def mie_operand(self, cls, imm):
        fast_bits = range(MIE_FAST_LO, MIE_FAST_LO + MIE_FAST_W)
        ro_bits = [b for b in range(32) if not (MIE_MASK >> b) & 1]
        if imm:
            if cls == "ro_only":
                return self.subset([b for b in ro_bits if b < 5])
            return 1 << 3 if cls == "std_only" else self.uimm()
        if cls == "std_only":
            return self.subset(MIE_STD_BITS)
        if cls == "fast_only":
            return self.subset(fast_bits)
        if cls == "std_fast":
            return self.subset(MIE_STD_BITS) | self.subset(fast_bits)
        if cls == "ro_only":
            return self.subset(ro_bits)
        if cls == "all_fast":
            return MIE_FAST_MASK
        return self.rs1_value()

    def mie_pair(self, op, cls, operand, item, label):
        f = self.facts[item]
        if cls == "fast_only":
            f["fast_bits"] |= {b for b in range(MIE_FAST_W) if (operand >> (MIE_FAST_LO + b)) & 1}
        f["op_class"].add((op, cls))
        self.csr_write(op, CSR_MIE, operand)
        self.mie = legal_mie(csr_op(op, self.mie, operand))
        self.gap()
        self.readback(CSR_MIE, self.mie, item, label)

    def block_029(self):
        item = "TP-CSR-029"
        self.facts[item] = {"fast_bits": set(), "op_class": set(), "pairs": 0}
        self.mstatus_mie_off()
        imm_table = {k: v for k, v in TABLES["TP-CSR-029 class"].items() if k in ("std_only", "ro_only", "rand")}
        for i in range(PAIRS_029):
            op = self.draw(TABLES["W-OP"])
            cls = self.draw(imm_table if op.endswith("i") else TABLES["TP-CSR-029 class"])
            operand = self.mie_operand(cls, op.endswith("i"))
            self.mie_pair(op, cls, operand, item, f"mie pair {i} {op} {cls} operand 0x{operand:08x}")
        for b in sorted(set(range(MIE_FAST_W)) - self.facts[item]["fast_bits"]):   # every fast bit at least once per seed
            operand = 1 << (MIE_FAST_LO + b)
            self.mie_pair("csrrs", "fast_only", operand, item, f"mie directed csrrs fast bit {b} operand 0x{operand:08x}")
        self.facts[item]["pairs"] = len(self.items[item])

    def block_030(self):
        item = "TP-CSR-030"
        self.facts[item] = {"rounds": ROUNDS_030}
        self.mstatus_mie_off()
        for i in range(ROUNDS_030):
            ops = [("csrrw", MASK32), ("csrrs", MASK32), ("csrrc", MASK32), ("csrrw", 0)]
            self.rng.shuffle(ops)
            for op, operand in ops:
                if operand == 0:
                    self.emit(f"csrrw x{self.pick_rd()}, 0x{CSR_MIE:x}, x0")
                else:
                    self.csr_write(op, CSR_MIE, operand)
                self.mie = legal_mie(csr_op(op, self.mie, operand))
                self.gap()
                self.readback(CSR_MIE, self.mie, item, f"round {i} {op} mie, {'x0' if operand == 0 else '-1'}")

    def block_035(self):
        item = "TP-CSR-035"
        self.facts[item] = {"copies": set(), "ops": set(), "rounds": ROUNDS_035}
        for i in range(ROUNDS_035):
            op = self.draw(TABLES["W-OP"])
            self.facts[item]["ops"].add(op)
            cur = self.mtvec[1]
            if op == "csrrw":
                copy, mode = self.rng.randrange(NUM_HANDLER_COPIES), self.rng.randrange(4)
                self.install_mtvec(copy, mode)
                desc = f"csrrw handler copy {copy} | MODE {mode:02b}"
            elif op == "csrrs":
                mode = self.rng.randrange(4)
                rs1 = self.pick_reg()
                self.emit(f"la x{rs1}, {HANDLER_SYMBOL.format(cur)}", retire=2)
                if mode:
                    self.emit(f"ori x{rs1}, x{rs1}, {mode}")
                self.emit(f"csrrs x{self.pick_rd()}, 0x{CSR_MTVEC:x}, x{rs1}")
                desc = f"csrrs current base | MODE {mode:02b}"
            elif op == "csrrc":
                low = self.rng.randrange(256)
                self.csr_write("csrrc", CSR_MTVEC, low)
                desc = f"csrrc low byte 0x{low:02x}"
            elif op == "csrrwi":
                u = self.uimm()
                self.csr_write("csrrwi", CSR_MTVEC, u)
                self.mtvec = legal_mtvec(u)
                self.gap()
                self.readback(CSR_MTVEC, self.mtvec, item, f"round {i} csrrwi mtvec, {u} (BASE 0, no trap)")
                copy, mode = self.rng.randrange(NUM_HANDLER_COPIES), self.rng.randrange(4)
                self.install_mtvec(copy, mode)
                desc = f"csrrwi {u} then csrrw handler copy {copy} | MODE {mode:02b}"
            elif op == "csrrsi":
                u = self.rng.randrange(4)   # bits 1:0 only: the standalone Spike run vectors to mtvec & ~1
                self.csr_write("csrrsi", CSR_MTVEC, u)
                desc = f"csrrsi mtvec, {u}"
            else:
                u = self.uimm()
                self.csr_write("csrrci", CSR_MTVEC, u)
                desc = f"csrrci mtvec, {u}"
            self.facts[item]["copies"].add(self.mtvec[1])
            self.gap()
            self.readback(CSR_MTVEC, self.mtvec_expected(), item, f"round {i} {desc}: mtvec read-back")
            self.emit("ecall", retire=0)
            self.handler_round_trip(PRIV_M, item, f"round {i} {desc}: ecall")

    def block_036(self):
        item = "TP-CSR-036"
        self.facts[item] = {"pairs": 0}
        fixed = [("csrrw", v) for v in (0x123456FF, 0x80000000, 0x00000000, 0xFFFFFFFF)]
        combos = []
        for mode in range(4):
            for nz in (False, True):
                low = (self.rng.randrange(1, 64) << 2 if nz else 0) | mode
                combos.append(("csrrw", (self.rng.getrandbits(24) << 8) | low))
        directed = [("csrrc", 1), ("csrrci", 3), ("csrrsi", 2)]
        rest = []
        while len(fixed) + len(combos) + len(directed) + len(rest) < PAIRS_036:
            op = self.draw(TABLES["W-OP"])
            rest.append((op, self.uimm() if op.endswith("i") else self.rs1_value()))
        first = fixed.pop(self.rng.randrange(len(fixed)))   # an int csrrw first: the model leaves the symbolic base
        pairs = fixed + combos + directed + rest
        self.rng.shuffle(pairs)
        pairs.insert(0, first)
        for i, (op, operand) in enumerate(pairs):
            prog_operand = None
            if self.red_pending and op == "csrrw":
                prog_operand = operand ^ (1 << 8)   # red fixture: the program writes a different BASE
                self.red_pending = False
            self.csr_write(op, CSR_MTVEC, operand, prog_operand=prog_operand)
            self.mtvec = legal_mtvec(csr_op(op, self.mtvec, operand))
            self.gap()
            self.readback(CSR_MTVEC, self.mtvec, item, f"pair {i} {op} mtvec operand 0x{operand:08x}")
        copy, mode = self.rng.randrange(NUM_HANDLER_COPIES), self.rng.randrange(4)
        self.install_mtvec(copy, mode)
        self.readback(CSR_MTVEC, self.mtvec_expected(), item, f"restore csrrw handler copy {copy} | MODE {mode:02b}")
        self.facts[item]["pairs"] = len(self.items[item])

    def epilogue(self):
        self.snapshot_traps(PROGRAM_ITEM, "unexpected-trap count at the end of the program")
        self.filler()
        self.report_reg(R_LASTC, 0, PROGRAM_ITEM, "mcause of the last unexpected trap (0 = none)")
        self.emit("li x3, 1")
        self.emit("la x30, tohost", retire=2)
        self.emit("sw x3, 0(x30)")
        self.lines.append("1:")
        self.lines.append("  j 1b")

    def handlers(self):
        out = []
        for k in range(NUM_HANDLER_COPIES):
            sym = HANDLER_SYMBOL.format(k)
            out += [
                "", ".balign 256", f".globl {sym}", f"{sym}:",
                f"  csrrs x{R_HS0}, 0x{CSR_MCAUSE:x}, x0",
                f"  addi x{R_HS1}, x{R_HS0}, -{CAUSE_ECALL_M}",
                f"  beqz x{R_HS1}, 1f",
                f"  addi x{R_HS1}, x{R_HS0}, -{CAUSE_ECALL_U}",
                f"  beqz x{R_HS1}, 1f",
                f"  addi x{R_TRAPS}, x{R_TRAPS}, 1",            # unexpected trap: count it, keep its cause, skip the instruction
                f"  mv x{R_LASTC}, x{R_HS0}",
                f"  csrrs x{R_HS0}, 0x{CSR_MEPC:x}, x0",
                f"  lhu x{R_HS1}, 0(x{R_HS0})",
                f"  andi x{R_HS1}, x{R_HS1}, 3",
                f"  addi x{R_HS1}, x{R_HS1}, -3",
                f"  addi x{R_HS0}, x{R_HS0}, 2",
                f"  bnez x{R_HS1}, 2f",
                f"  addi x{R_HS0}, x{R_HS0}, 2",
                "2:",
                f"  csrrw x0, 0x{CSR_MEPC:x}, x{R_HS0}",
                f"  li x{R_HS1}, 0x{PRIV_M << MST_MPP_LO:x}",
                f"  csrrs x0, 0x{CSR_MSTATUS:x}, x{R_HS1}",     # MPP = M: mret returns to M-mode code
                "  mret",
                "1:",
                f"  li x{R_HS1}, 0x{self.markers[k]:08x}",
                f"  sw x{R_HS1}, 0(x{R_EOT})",                   # report: which handler copy ran
                f"  csrrs x{R_HS1}, 0x{CSR_MEPC:x}, x0",
                f"  sw x{R_HS0}, 0(x{R_EOT})",                   # report: mcause
                f"  addi x{R_HS1}, x{R_HS1}, 4",
                f"  csrrw x0, 0x{CSR_MEPC:x}, x{R_HS1}",
                f"  li x{R_HS0}, 0x{PRIV_M << MST_MPP_LO:x}",
                f"  csrrs x0, 0x{CSR_MSTATUS:x}, x{R_HS0}",
                "  mret",
            ]
        return out

    def build(self):
        self.prologue()
        blocks = {"023": self.block_023, "024": self.block_024, "025": self.block_025, "027": self.block_027,
                  "028": self.block_028, "029": self.block_029, "030": self.block_030, "035": self.block_035,
                  "036": self.block_036}
        order = list(blocks)
        self.rng.shuffle(order)
        for b in order:
            self.lines.append(f"  # ---- TP-CSR-{b}")
            blocks[b]()
        self.epilogue()
        assert not self.red_pending, "red fixture found no csrrw pair to deviate on"
        min_retired = self.n_insn + HANDLER_ECALL_INSNS * self.n_ecall
        return Plan(seed=self.seed, red=self.red, k=len(self.expected), expected=list(self.expected),
                    labels=list(self.labels), items=dict(self.items), min_retired=min_retired, facts=self.facts,
                    markers=dict(self.markers), block_order=order, lines=list(self.lines), handler_lines=self.handlers())


def plan(seed, red=False):
    return _Builder(int(seed), bool(red)).build()


def emit(p):
    head = [
        f"# gen_csr_trap_setup program, seed {p.seed}{' RED FIXTURE' if p.red else ''}: rendered by",
        "# dv/auto_dv/tests/gen_programs/gen_csr_trap_setup_prog.py (plan group gen_csr_trap_setup).",
        f"# {p.k} report words to GEN_MM_EOT_ADDR, then tohost 1; block order TP-CSR-{', '.join(p.block_order)}.",
        '.include "gen_mmio_map.h"',
        ".section .text",
        ".globl _start",
        "_start:",
    ]
    tail = [
        "",
        ".section .data",
        ".align 6",
        ".globl tohost",
        "tohost:   .dword 0",
        ".globl fromhost",
        "fromhost: .dword 0",
        ".align 2",
        ".globl gen_min_retired",
        f"gen_min_retired: .word {p.min_retired}",
        "",
    ]
    return "\n".join(head + p.lines + p.handler_lines + tail)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--red", action="store_true", help="TDD red fixture: one mtvec write deviates from the plan")
    args = ap.parse_args(argv)
    p = plan(args.seed, args.red)
    text = emit(p)
    assert all(ord(c) < 128 for c in text), "non-ASCII byte in the rendered program"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"gen_csr_trap_setup_prog: seed {args.seed} red {args.red} -> {args.out} (k={p.k} reports, "
          f"min_retired={p.min_retired}, blocks {'-'.join(p.block_order)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
