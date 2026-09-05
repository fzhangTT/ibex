#!/usr/bin/env python3
"""gen_bit_ratified_prog: per-seed program generator for gen_test_bit_ratified (group gen_bit_ratified).

Built items (gen_test_plan.md Section 4.1 AREA BIT): TP-BIT-002 / 003 (Zba sh1add / sh2add / sh3add over the CG-BIT-001
rs1 x rs2 classes, the result consumed as a load address, shift-out and wrap corners), TP-BIT-004 (andn / orn / xnor,
zero and all-ones results), TP-BIT-005 / 006 (clz / ctz / cpop over the CG-BIT-002 operand classes, every single-bit
position, results 0 / 1 / 16 / 31 / 32), TP-BIT-007 / 008 (min / max / minu / maxu over the sign pairs, equal operands,
the signed-versus-unsigned corner pairs), TP-BIT-009 / 010 (sext.b / sext.h / zext.h and their Zcb forms), TP-BIT-014
(orc.b over the 16 byte-zero patterns), TP-BIT-015 (rev8), TP-BIT-017 / 018 / 019 (Zbs register and immediate forms over
index class x prior bit, rs2 upper bits, binv twice, the instr[25] = 1 immediate forms trapping with mcause 2 and
mtval = word through a returning handler), TP-BIT-020 / 021 (Zbc clmul / clmulh / clmulr classes, corner values, the
program-computed identity clmulr == (clmulh << 1) | clmul[31]), TP-BIT-038 (every legal Zb* mnemonic with rd = x0
followed by an x0 reader; value clause only) and TP-BIT-040 (csrr misa at random points and after a csrw attempt).
Not built: TP-BIT-001 (per-retirement rvfi_trap = 0 over the 58-row ENC table is an RVFI record fact, and its U-mode
leg leaves M-mode); the stall / delta-2 clause of TP-BIT-038 needs bus records.

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:bit_ratified"). The op
stream is the directed floor of every built item (one op per class, case, position or pair the item's fire-check names,
each op non-vacuous by construction: rd != x0) shuffled as units (chains stay adjacent) into N_EXTRAS weighted random
extras with the full W1 / W3 / W4 freedom (rd = x0, x0 sources); the test counts vacuous compares (rd = x0) apart. The
expected rd of every op comes from the Python references below, written from the ratified Bitmanip chapter
(tools/specs/riscv-isa-manual/src/unpriv/zb.adoc, Operation blocks of sh1add..sh3add, andn, orn, xnor, clz, ctz, cpop,
min, max, minu, maxu, sext.b, sext.h, pack (zext.h), orc.b, rev8, bclr..bexti, clmul, clmulh, clmulr, rol, ror), never
from the RTL or the shim. Every op stores its report word(s) straight to GEN_MM_EOT_ADDR: its rd, the loaded word for an
address-consuming shNadd, mcause then mtval for an illegal word, 0 for the x0 reader, the misa value for a CSR read.

Red fixtures deviate the PROGRAM on one intent while the expectations stay true: `--red [--red-item ID[:SEL]]`; without
--red-item the seed draws the item among BUILT_ITEMS (random.Random(f"{seed}:red:bit_ratified")). Selector src (items
002..021): one floor op loads one source register with a value whose reference result differs. Selector x0 (TP-BIT-038):
one x0 reader stores the op's nonzero source instead of x0. Selector csr (TP-BIT-040): one misa read reads mhartid instead.
main() asserts that the red plan's report words, k and min_retired equal the green plan's.

emit(plan) renders RV32IMC(B) assembly for the lowRISC gcc 10.2 (-march=rv32imcb accepts the ratified Zba / Zbb / Zbs / Zbc
mnemonics; the Zcb forms come from dv/auto_dv/stim/gen_zc_insn.h): mtvec at the handler, the op stream with its stores,
the tohost pass code. The handler reports mcause and mtval and returns to mepc + 4.

CLI: python3 gen_bit_ratified_prog.py --seed N --out <file.S> [--red [--red-item TP-BIT-<nnn>[:SEL]]]
"""
import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dv.auto_dv.tests.gen_programs.gen_prog_const import MISA_VALUE, TOHOST_PASS, csr_hex  # noqa: E402

MASK32 = 0xFFFFFFFF
PROGRAM_TAG = "bit_ratified"
BUILT_ITEMS = ("TP-BIT-002", "TP-BIT-003", "TP-BIT-004", "TP-BIT-005", "TP-BIT-006", "TP-BIT-007", "TP-BIT-008",
               "TP-BIT-009", "TP-BIT-010", "TP-BIT-014", "TP-BIT-015", "TP-BIT-017", "TP-BIT-018", "TP-BIT-019",
               "TP-BIT-020", "TP-BIT-021", "TP-BIT-038", "TP-BIT-040")
ITEM_X0 = "TP-BIT-038"
ITEM_MISA = "TP-BIT-040"
RED_SELECTORS = {i: ("x0",) if i == ITEM_X0 else ("csr",) if i == ITEM_MISA else ("src",) for i in BUILT_ITEMS}
CAUSE_ILLEGAL = 2
N_EXTRAS = (48, 64)                # random extras per seed (inclusive range)
N_TABLE_WORDS = 64                 # load table for the address-consuming shNadd ops
ADDR_FRACTION = 0.3                # TP-BIT-002: fraction of shNadd iterations consumed as a load address
FILLER_FORMS = ("addi", "xori", "andi", "ori", "add", "sub", "sll", "xor", "lui")
W4_RD_X0 = 1 / 16
W4_X0_SRC = 1 / 16
W4_RS_SAME = 1 / 16

# Instruction forms: r (rd, rs1, rs2), i (rd, rs1, imm), u (rd, rs1), c (Zcb: rd' in x8..x15 in place).
FORMS = {"sh1add": "r", "sh2add": "r", "sh3add": "r", "andn": "r", "orn": "r", "xnor": "r", "clz": "u", "ctz": "u",
         "cpop": "u", "min": "r", "max": "r", "minu": "r", "maxu": "r", "sext.b": "u", "sext.h": "u", "zext.h": "u",
         "orc.b": "u", "rev8": "u", "bclr": "r", "bset": "r", "binv": "r", "bext": "r", "bclri": "i", "bseti": "i",
         "binvi": "i", "bexti": "i", "clmul": "r", "clmulh": "r", "clmulr": "r", "rol": "r", "ror": "r", "rori": "i",
         "c_sext_b": "c", "c_sext_h": "c", "c_zext_h": "c",
         "pack": "r", "packh": "r", "packu": "r"}
C_BASE = {"c_sext_b": "sext.b", "c_sext_h": "sext.h", "c_zext_h": "zext.h"}
IMM_BITS = {"bclri": 5, "bseti": 5, "binvi": 5, "bexti": 5, "rori": 5}
# Smoke items own the mnemonics the extras draw from.
ITEM_OPS = {"TP-BIT-002": ("sh1add", "sh2add", "sh3add"), "TP-BIT-004": ("andn", "orn", "xnor"),
            "TP-BIT-005": ("clz", "ctz", "cpop"), "TP-BIT-007": ("min", "max", "minu", "maxu"),
            "TP-BIT-009": ("sext.b", "sext.h", "c_sext_b", "c_sext_h"), "TP-BIT-010": ("zext.h", "c_zext_h", "pack", "packh", "packu"),
            "TP-BIT-014": ("orc.b",), "TP-BIT-015": ("rev8",), "TP-BIT-017": ("bclr", "bset", "binv", "bext"),
            "TP-BIT-018": ("bclri", "bseti", "binvi", "bexti"), "TP-BIT-020": ("clmul", "clmulh", "clmulr")}
SHADD_N = {"sh1add": 1, "sh2add": 2, "sh3add": 3}
SBIT_REG = ("bclr", "bset", "binv", "bext")
SBIT_IMM = ("bclri", "bseti", "binvi", "bexti")
# funct7 of the immediate single-bit forms with instr[25] set (shamt[5], reserved on RV32): illegal (TP-BIT-019).
ILLEGAL_F7_F3 = {"bclri": (0b0100101, 1), "bseti": (0b0010101, 1), "binvi": (0b0110101, 1), "bexti": (0b0100101, 5)}
OPCODE_OP_IMM = 0x13

# gen_test_plan.md "Layer-1 weight tables" W1: 32-bit register operand classes (values per CG-BIT-001 cp_rs1_class).
W1 = {"zero": 1, "all_ones": 1, "int_min": 1, "int_max": 1, "one": 1, "p16": 1, "two": 1, "e0000000": 1,
      "byte_msb": 1, "half_msb": 1, "single_bit": 1, "alt": 1, "bytes_01020304": 1, "distinct_lanes": 1,
      "pos_rand": 4, "neg_rand": 4}
W1_NONZERO = {k: v for k, v in W1.items() if k != "zero"}
# CG-BIT-001 cp_rs1_class / cp_rs2_class bins (the "10 x 7 classes" of TP-BIT-002).
RS1_CLASSES = ("zero", "all_ones", "int_min", "int_max", "one", "e0000000", "byte_msb", "half_msb", "pos_rand", "neg_rand")
RS2_CLASSES = ("zero", "all_ones", "int_min", "int_max", "one", "pos_rand", "neg_rand")
POS_CLASSES = ("zero", "int_max", "one", "p16", "two", "bytes_01020304", "pos_rand")
NEG_CLASSES = ("all_ones", "int_min", "e0000000", "byte_msb", "half_msb", "neg_rand")
# CG-BIT-002 cp_operand bins.
COUNT_CLASSES = ("zero", "all_ones", "msb_only", "lsb_only", "single_other", "alt_5", "alt_a", "int_max", "rand")
# CG-BIT-006 cp_index / cp_operand / cp_rs2_upper bins; W3 upper-bit classes of the register forms.
INDEX_CLASSES = ("i0", "mid", "i31")
SBIT_OPERANDS = ("zero", "all_ones", "rand")
UPPER_NONZERO = ("v32", "v33", "vFFFFFFE0", "v80000000", "vFFFFFFFF", "other_nonzero")
# CG-BIT-007 cp_rs1_class / cp_rs2_class bins of the clmul family.
CLMUL_CLASSES = ("zero", "one", "all_ones", "single_bit", "rand")
# TP-BIT-009 operand classes (bit 7 / bit 15 set or clear, zero, all-ones, random) and the named exact values.
SEXT_CLASSES = ("bit7_set", "bit7_clear", "bit15_set", "bit15_clear", "zero", "all_ones", "rand")
SEXT_EXACT = {"sext.b": (0x80, 0x7F), "sext.h": (0x8000,)}
# TP-BIT-038: every legal Zb* mnemonic (ratified set of this test, the rotates, the draft set the shim serves).
X0_DRAFT = {"grev": "r", "gorc": "r", "grevi": "i5", "gorci": "i5", "shfl": "r", "unshfl": "r", "shfli": "i4",
            "unshfli": "i4", "xperm.n": "r", "xperm.b": "r", "xperm.h": "r", "pack": "r", "packh": "r", "packu": "r",
            "slo": "r", "sro": "r", "sloi": "i5", "sroi": "i5", "fsl": "r4", "fsr": "r4", "fsri": "r4i", "bfp": "r",
            "cmov": "r4", "cmix": "r4", "crc32.b": "u", "crc32.h": "u", "crc32.w": "u", "crc32c.b": "u",
            "crc32c.h": "u", "crc32c.w": "u"}
# A mnemonic the draft set already probes is not probed twice: pack, packh and packu are draft
# encodings this test also emits normally, and two probes of one mnemonic is not a second shape.
X0_RATIFIED = tuple(k for k in FORMS if FORMS[k] != "c" and k not in X0_DRAFT)


# ---- references (zb.adoc Operation blocks) -----------------------------------------------------------------------------
def signed(x):
    return x - (1 << 32) if x & 0x80000000 else x


def sext(v, bits):
    return (v - (1 << bits)) & MASK32 if v & (1 << (bits - 1)) else v


def clz32(x):
    return 32 - x.bit_length()


def ctz32(x):
    return 32 if x == 0 else (x & -x).bit_length() - 1


def cpop32(x):
    return bin(x).count("1")


def orc_b32(x):
    return sum(0xFF << s for s in range(0, 32, 8) if (x >> s) & 0xFF)


def rev8_32(x):
    return int.from_bytes(x.to_bytes(4, "little"), "big")


def clmul32(a, b):
    out = 0
    for i in range(32):
        if (b >> i) & 1:
            out ^= a << i
    return out & MASK32


def clmulh32(a, b):
    out = 0
    for i in range(1, 32):
        if (b >> i) & 1:
            out ^= a >> (32 - i)
    return out & MASK32


def clmulr32(a, b):
    out = 0
    for i in range(32):
        if (b >> i) & 1:
            out ^= a >> (31 - i)
    return out & MASK32


def rol32(a, sh):
    sh &= 31
    return ((a << sh) | (a >> (32 - sh))) & MASK32 if sh else a


def ror32(a, sh):
    sh &= 31
    return ((a >> sh) | (a << (32 - sh))) & MASK32 if sh else a


def reference(kind, rs1, rs2=0, imm=0):
    """Expected rd of one ratified op; rs2 carries the register operand, imm the immediate (index forms use bits 4:0)."""
    if kind in PACK_REF:
        return PACK_REF[kind](rs1, rs2)
    kind = C_BASE.get(kind, kind)
    k = imm if FORMS[kind] == "i" else rs2
    if kind in SHADD_N:
        return (rs2 + (rs1 << SHADD_N[kind])) & MASK32
    if kind == "andn":
        return rs1 & ~rs2 & MASK32
    if kind == "orn":
        return (rs1 | (~rs2 & MASK32)) & MASK32
    if kind == "xnor":
        return ~(rs1 ^ rs2) & MASK32
    if kind == "clz":
        return clz32(rs1)
    if kind == "ctz":
        return ctz32(rs1)
    if kind == "cpop":
        return cpop32(rs1)
    if kind == "min":
        return rs1 if signed(rs1) < signed(rs2) else rs2
    if kind == "max":
        return rs1 if signed(rs1) > signed(rs2) else rs2
    if kind == "minu":
        return min(rs1, rs2)
    if kind == "maxu":
        return max(rs1, rs2)
    if kind == "sext.b":
        return sext(rs1 & 0xFF, 8)
    if kind == "sext.h":
        return sext(rs1 & 0xFFFF, 16)
    if kind == "zext.h":
        return rs1 & 0xFFFF
    if kind == "orc.b":
        return orc_b32(rs1)
    if kind == "rev8":
        return rev8_32(rs1)
    if kind in ("bclr", "bclri"):
        return rs1 & ~(1 << (k & 31)) & MASK32
    if kind in ("bset", "bseti"):
        return rs1 | (1 << (k & 31))
    if kind in ("binv", "binvi"):
        return rs1 ^ (1 << (k & 31))
    if kind in ("bext", "bexti"):
        return (rs1 >> (k & 31)) & 1
    if kind == "clmul":
        return clmul32(rs1, rs2)
    if kind == "clmulh":
        return clmulh32(rs1, rs2)
    if kind == "clmulr":
        return clmulr32(rs1, rs2)
    if kind == "rol":
        return rol32(rs1, rs2)
    if kind in ("ror", "rori"):
        return ror32(rs1, k)
    raise ValueError(kind)


PACK_REF = {
    # rtl/ibex_alu.sv:565-567: packu {b[31:16], a[31:16]}, packh {16'h0, b[7:0], a[7:0]},
    # pack (the default arm) {b[15:0], a[15:0]}. zext.h is this same encoding with rs2 = x0.
    "pack":  lambda a, b: (((b & 0xFFFF) << 16) | (a & 0xFFFF)) & MASK32,
    "packu": lambda a, b: ((b & 0xFFFF0000) | ((a >> 16) & 0xFFFF)) & MASK32,
    "packh": lambda a, b: (((b & 0xFF) << 8) | (a & 0xFF)) & MASK32,
}


def shadd_wrap(kind, rs1, rs2):
    """CG-BIT-001 cp_wrap: carry out of rs2 + (rs1 << n) on 32 bits."""
    return ((rs1 << SHADD_N[kind]) & MASK32) + rs2 > MASK32


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


# The coverage classifies an operand by VALUE (gen_fcov_pkg.sv bit_rs1_cls): six exact values are
# their own classes, and any other value whose bit 7 and bit 15 differ is byte_msb or half_msb. A
# draw that ignores that is classified as some other class, so the op's pos_rand or neg_rand leg goes
# unhit at the seeds where every draw for that op happened to land elsewhere.
_NAMED_EXACT = (0x00000000, 0xFFFFFFFF, 0x80000000, 0x7FFFFFFF, 0x00000001, 0xE0000000)


def _plain_rand(rng, lo, hi):
    """A value the coverage will classify as pos_rand / neg_rand rather than as a named class."""
    for _ in range(64):
        v = rng.randrange(lo, hi)
        if v not in _NAMED_EXACT and ((v >> 7) & 1) == ((v >> 15) & 1):
            return v
    raise AssertionError("no plain random value in 64 draws")


def operand_value(rng, cls):
    if cls == "zero":
        return 0
    if cls == "all_ones":
        return MASK32
    if cls in ("int_min", "msb_only"):
        return 0x80000000
    if cls == "int_max":
        return 0x7FFFFFFF
    if cls in ("one", "lsb_only"):
        return 1
    if cls == "p16":
        return 1 << 16
    if cls == "two":
        return 2
    if cls == "e0000000":
        return 0xE0000000
    if cls == "byte_msb":
        return (rng.randrange(1 << 32) | 0x80) & ~0x8000 & MASK32
    if cls == "half_msb":
        return (rng.randrange(1 << 32) | 0x8000) & ~0x80 & MASK32
    if cls == "single_bit":
        return 1 << rng.randrange(32)
    if cls == "single_other":
        return 1 << rng.randrange(1, 31)
    if cls == "alt":
        return rng.choice((0x55555555, 0xAAAAAAAA))
    if cls == "alt_5":
        return 0x55555555
    if cls == "alt_a":
        return 0xAAAAAAAA
    if cls == "bytes_01020304":
        return 0x01020304
    if cls == "distinct_lanes":
        v = 0
        for nib in rng.sample(range(16), 8):
            v = (v << 4) | nib
        return v
    if cls == "pos_rand":
        return _plain_rand(rng, 1, 0x80000000)
    if cls == "neg_rand":
        return _plain_rand(rng, 0x80000000, 1 << 32)
    if cls == "rand":
        return rng.randrange(1 << 32)
    if cls == "bit7_set":
        return rng.randrange(1 << 32) | 0x80
    if cls == "bit7_clear":
        return rng.randrange(1 << 32) & ~0x80 & MASK32
    if cls == "bit15_set":
        return rng.randrange(1 << 32) | 0x8000
    if cls == "bit15_clear":
        return rng.randrange(1 << 32) & ~0x8000 & MASK32
    raise ValueError(cls)


def index_value(rng, cls):
    return {"i0": 0, "i31": 31}.get(cls) if cls != "mid" else rng.randrange(1, 31)


def upper_value(rng, cls, idx):
    """Full rs2 of a register single-bit form: W3 upper-bit class around the index; (rs2, effective index)."""
    if cls == "zero":
        v = idx
    elif cls == "v32":
        v = 32
    elif cls == "v33":
        v = 33
    elif cls == "vFFFFFFE0":
        v = 0xFFFFFFE0 | idx
    elif cls == "v80000000":
        v = 0x80000000 | idx
    elif cls == "vFFFFFFFF":
        v = MASK32
    elif cls == "other_nonzero":
        v = (rng.randrange(1, 1 << 27) << 5) | idx
    else:
        raise ValueError(cls)
    return v, v & 31


def with_bit(x, idx, prior):
    return (x | (1 << idx)) if prior else (x & ~(1 << idx) & MASK32)


def illegal_word(kind, rd, rs1, shamt):
    f7, f3 = ILLEGAL_F7_F3[kind]
    return (f7 << 25) | ((shamt & 31) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | OPCODE_OP_IMM


@dataclass
class Spec:
    """One op before register allocation: values fixed, registers drawn later."""
    item: str
    kind: str                  # mnemonic key; special kinds: addr_<shNadd>, ident, illegal_<kind>, x0_<mnemonic>, misa_read, misa_write
    rs1_val: int = 0
    rs2_val: int = 0
    imm: int = -1
    rs1_class: str = "given"
    rs2_class: str = "given"
    tags: dict = field(default_factory=dict)
    floor: bool = True
    chain: bool = False        # rs1 = the previous op's rd (value = prev.expect)
    follow: bool = False       # same unit as the previous op (adjacent, no value chain)
    same_rs: bool = False      # rs2 is the rs1 register
    same_all: bool = False     # rd, rs1 and rs2 are one register (cp_same_regs.all_same)
    same_rd: bool = False      # rd is the previous op's rd (with chain: the same rd AND index)
    rd_x0: bool = False


@dataclass
class Op:
    idx: int
    item: str
    kind: str
    rd: int
    rs1: int
    rs2: int
    rs1_val: int
    rs2_val: int
    imm: int
    expects: list              # report words this op stores, in order
    floor: bool
    rs1_class: str
    rs2_class: str
    tags: dict
    chained: bool = False
    rep: int = 0               # index of the first report word
    keep: tuple = ()           # registers live across this op's fillers (unit-local values)
    fillers: list = field(default_factory=list)
    aux: dict = field(default_factory=dict)   # extra registers of the special kinds

    @property
    def form(self):
        return FORMS.get(self.kind, "")

    @property
    def vacuous(self):
        """rd = x0 outside TP-BIT-038 (whose ops are the x0 readers by design)."""
        return self.rd == 0 and self.item != ITEM_X0


@dataclass
class Plan:
    seed: int
    red: bool
    red_item: str
    red_sel: str
    eot_reg: int
    trap_tmp: int
    ops: list
    reports: list
    k: int
    min_retired: int
    red_idx: int
    red_field: str
    red_val: int
    items: dict
    table: list


def program_rng(seed):
    return random.Random(f"{int(seed)}:program:{PROGRAM_TAG}")


def red_rng(seed):
    return random.Random(f"{int(seed)}:red:{PROGRAM_TAG}")


# ---- item floors -------------------------------------------------------------------------------------------------------
def _rs_pair(rng, item, kind, c1, c2, tags=None, floor=True):
    return Spec(item, kind, operand_value(rng, c1), operand_value(rng, c2), rs1_class=c1, rs2_class=c2,
                tags=dict(tags or {}), floor=floor)


def _spec_002(rng):
    specs = []
    shift = rng.randrange(len(RS2_CLASSES))
    for kind in ITEM_OPS["TP-BIT-002"]:
        for i, c1 in enumerate(RS1_CLASSES):
            specs.append(_rs_pair(rng, "TP-BIT-002", kind, c1, RS2_CLASSES[(i + shift) % len(RS2_CLASSES)]))
    n_addr = round(ADDR_FRACTION * len(specs) / (1 - ADDR_FRACTION))
    for i in range(n_addr):
        kind = ITEM_OPS["TP-BIT-002"][i % 3]
        n = SHADD_N[kind]
        word = rng.randrange(N_TABLE_WORDS)
        # index << n must be a word offset inside the table: idx = word * 4 >> n with word even for sh3add
        if n == 3:
            word &= ~1
        idx = (word * 4) >> n
        specs.append(Spec("TP-BIT-002", f"addr_{kind}", idx, 0, rs1_class="index", rs2_class="table", tags={"word": word}))
    return specs


def _spec_003(rng):
    specs = []
    for kind in ITEM_OPS["TP-BIT-002"]:
        n = SHADD_N[kind]
        for cls in ("e0000000", "all_ones"):
            specs.append(_rs_pair(rng, "TP-BIT-003", kind, cls, weighted(rng, W1), tags={"case": cls}))
        shifted = 0
        while not shifted:
            rs1 = operand_value(rng, "neg_rand")
            shifted = (rs1 << n) & MASK32
        rs2 = rng.randrange(MASK32 - shifted + 1, 1 << 32)   # the sum crosses 2^32
        assert shadd_wrap(kind, rs1, rs2)
        specs.append(Spec("TP-BIT-003", kind, rs1, rs2, rs1_class="neg_rand", rs2_class="wrap", tags={"case": "wrap"}))
        c, v = _nonzero(rng)
        specs.append(Spec("TP-BIT-003", kind, v, v, rs1_class=c, rs2_class=c, tags={"case": "same"}, same_rs=True))
        c, v = _nonzero(rng)
        specs.append(Spec("TP-BIT-003", kind, v, v, rs1_class=c, rs2_class=c, tags={"case": "eq"}))
    return specs


def _nonzero(rng):
    c = weighted(rng, W1_NONZERO)
    return c, operand_value(rng, c)


def _spec_004(rng):
    specs = []
    shift = rng.randrange(len(RS2_CLASSES))
    for kind in ITEM_OPS["TP-BIT-004"]:
        for i, c1 in enumerate(RS1_CLASSES):
            specs.append(_rs_pair(rng, "TP-BIT-004", kind, c1, RS2_CLASSES[(i + shift) % len(RS2_CLASSES)]))
        c, x = _nonzero(rng)
        # result classes: andn x,x = 0 and all_ones & ~0 = all ones; orn 0,all_ones = 0 and x,x = all ones;
        # xnor x,~x = 0 and x,x = all ones
        pairs = {"andn": ((x, x, 0), (MASK32, 0, MASK32)), "orn": ((0, MASK32, 0), (x, x, MASK32)),
                 "xnor": ((x, ~x & MASK32, 0), (x, x, MASK32))}[kind]
        for a, b, want in pairs:
            assert reference(kind, a, b) == want
            specs.append(Spec("TP-BIT-004", kind, a, b, rs1_class=c, rs2_class=c,
                              tags={"result": "zero" if want == 0 else "all_ones"}))
    return specs


def _spec_005(rng):
    specs = []
    for kind in ITEM_OPS["TP-BIT-005"]:
        for cls in COUNT_CLASSES:
            specs.append(Spec("TP-BIT-005", kind, operand_value(rng, cls), rs1_class=cls, tags={"cls": cls}))
        # results 1 and 16 (CG-BIT-002 cp_result r1 / r16)
        for want in (1, 16):
            if kind == "clz":
                x = (1 << (31 - want)) | rng.randrange(1 << (31 - want))
            elif kind == "ctz":
                x = (rng.randrange(1 << (31 - want)) << (want + 1)) | (1 << want)
            else:
                x = 0
                for b in rng.sample(range(32), want):
                    x |= 1 << b
            assert reference(kind, x) == want, (kind, want, hex(x))
            specs.append(Spec("TP-BIT-005", kind, x, rs1_class="result", tags={"result": f"r{want}"}))
    # cp_result.other for cpop: the operand classes above weigh 0, 1, 16, 31 or 32 bits and the two
    # directed results are 1 and 16, so the remaining result bin rested on whatever a random operand
    # happened to weigh. Five bits is in no other bin.
    x = 0
    for b in rng.sample(range(32), 5):
        x |= 1 << b
    assert reference("cpop", x) == 5, hex(x)
    specs.append(Spec("TP-BIT-005", "cpop", x, rs1_class="rand", tags={"cls": "rand", "result": "other"}))
    return specs


def _spec_006(rng):
    specs = []
    for kind in ITEM_OPS["TP-BIT-005"]:
        for pos in range(32):
            specs.append(Spec("TP-BIT-006", kind, 1 << pos, rs1_class="single_bit",
                              tags={"pos": pos, "result": f"r{reference(kind, 1 << pos)}"}))
        for cls in ("zero", "all_ones", "int_max"):
            x = operand_value(rng, cls)
            specs.append(Spec("TP-BIT-006", kind, x, rs1_class=cls, tags={"cls": cls, "result": f"r{reference(kind, x)}"}))
    return specs


def _sign_pair(rng, kind, item, pair):
    c1 = rng.choice(POS_CLASSES if pair[0] == "p" else NEG_CLASSES)
    c2 = rng.choice(POS_CLASSES if pair[1] == "p" else NEG_CLASSES)
    return _rs_pair(rng, item, kind, c1, c2, tags={"sign": pair})


def _spec_007(rng):
    specs = []
    shift = rng.randrange(len(RS2_CLASSES))
    for kind in ITEM_OPS["TP-BIT-007"]:
        for i, c1 in enumerate(RS1_CLASSES):
            specs.append(_rs_pair(rng, "TP-BIT-007", kind, c1, RS2_CLASSES[(i + shift) % len(RS2_CLASSES)]))
        for pair in ("pp", "pn", "np", "nn"):
            specs.append(_sign_pair(rng, kind, "TP-BIT-007", pair))
    return specs


def _spec_008(rng):
    specs = []
    for kind in ITEM_OPS["TP-BIT-007"]:
        c, v = _nonzero(rng)
        specs.append(Spec("TP-BIT-008", kind, v, v, rs1_class=c, rs2_class=c, tags={"case": "same"}, same_rs=True))
        c, v = _nonzero(rng)
        specs.append(Spec("TP-BIT-008", kind, v, v, rs1_class=c, rs2_class=c, tags={"case": "eq"}))
        # the signed-versus-unsigned corners the item names, applied to all four ops
        for case, a, b in (("m1_p1", MASK32, 1), ("min_max", 0x80000000, 0x7FFFFFFF)):
            specs.append(Spec("TP-BIT-008", kind, a, b, rs1_class="all_ones" if a == MASK32 else "int_min",
                              rs2_class="one" if b == 1 else "int_max", tags={"case": case}))
        for pair in ("pp", "pn", "np", "nn"):
            specs.append(_sign_pair(rng, kind, "TP-BIT-008", pair))
    return specs


def _spec_009(rng):
    specs = []
    for kind in ITEM_OPS["TP-BIT-009"]:
        for cls in SEXT_CLASSES:
            specs.append(Spec("TP-BIT-009", kind, operand_value(rng, cls), rs1_class=cls, tags={"cls": cls}))
        for x in SEXT_EXACT[C_BASE.get(kind, kind)]:
            specs.append(Spec("TP-BIT-009", kind, x, rs1_class="exact", tags={"exact": x}))
    return specs


def _spec_010(rng):
    return [Spec("TP-BIT-010", kind, operand_value(rng, cls), rs1_class=cls, tags={"cls": cls})
            for kind in ITEM_OPS["TP-BIT-010"] for cls in RS1_CLASSES]


def _spec_014(rng):
    specs = []
    for mask in range(16):
        x = 0
        for b in range(4):
            if (mask >> b) & 1:
                x |= rng.randrange(1, 256) << (8 * b)
        specs.append(Spec("TP-BIT-014", "orc.b", x, rs1_class="pattern", tags={"pattern": mask}))
    for _ in range(4):
        c, v = _nonzero(rng)
        specs.append(Spec("TP-BIT-014", "orc.b", v, rs1_class=c, tags={"cls": c}))
    return specs


def _spec_015(rng):
    specs = [Spec("TP-BIT-015", "rev8", 0x01020304, rs1_class="bytes_01020304", tags={"case": "bytes_01020304"})]
    for byte in range(4):
        pos = 8 * byte + rng.randrange(8)
        specs.append(Spec("TP-BIT-015", "rev8", 1 << pos, rs1_class="single_bit", tags={"case": "single_bit", "pos": pos}))
    for _ in range(4):
        c, v = _nonzero(rng)
        specs.append(Spec("TP-BIT-015", "rev8", v, rs1_class=c, tags={"case": "rand"}))
    return specs


def _spec_017(rng):
    specs = []
    for kind in SBIT_REG:
        for icls in INDEX_CLASSES:
            for prior in (0, 1):
                idx = index_value(rng, icls)
                x = with_bit(rng.randrange(1 << 32), idx, prior)
                specs.append(Spec("TP-BIT-017", kind, x, idx, rs1_class="rand", rs2_class="zero",
                                  tags={"icls": icls, "prior": prior}))
    return specs


def _spec_018(rng):
    specs = []
    for kind in SBIT_IMM:
        for icls in INDEX_CLASSES:
            for prior in (0, 1):
                idx = index_value(rng, icls)
                x = with_bit(rng.randrange(1 << 32), idx, prior)
                specs.append(Spec("TP-BIT-018", kind, x, imm=idx, rs1_class="rand", tags={"icls": icls, "prior": prior}))
        for ocls in SBIT_OPERANDS:
            idx = rng.randrange(32)
            x = operand_value(rng, ocls)
            specs.append(Spec("TP-BIT-018", kind, x, imm=idx, rs1_class=ocls,
                              tags={"ocls": ocls, "icls": "i0" if idx == 0 else "i31" if idx == 31 else "mid",
                                    "prior": (x >> idx) & 1}))
    return specs


def _spec_019(rng):
    specs = []
    for kind in SBIT_REG + SBIT_IMM:
        for idx in (0, 31):
            x = rng.randrange(1 << 32)
            spec = Spec("TP-BIT-019", kind, x, rs1_class="rand", tags={"index": idx})
            if FORMS[kind] == "i":
                spec.imm = idx
            else:
                spec.rs2_val, spec.rs2_class = idx, "zero"
            specs.append(spec)
    for kind, prior, tag in (("bset", 1, "set_on_set"), ("bclr", 0, "clr_on_clr"), ("bseti", 1, "set_on_set"), ("bclri", 0, "clr_on_clr")):
        idx = rng.randrange(32)
        x = with_bit(rng.randrange(1 << 32), idx, prior)
        spec = Spec("TP-BIT-019", kind, x, rs1_class="rand", tags={"case": tag})
        if FORMS[kind] == "i":
            spec.imm = idx
        else:
            spec.rs2_val, spec.rs2_class = idx, "zero"
        assert reference(kind, x, spec.rs2_val, spec.imm) == x
        specs.append(spec)
    for kind in ("binv", "binvi"):   # binv twice on the same bit restores the operand (a chained pair)
        idx = rng.randrange(32)
        c, x = _nonzero(rng)
        first = Spec("TP-BIT-019", kind, x, rs1_class=c, tags={"twice": "first", "index": idx})
        second = Spec("TP-BIT-019", kind, rs1_class="chain_prev", tags={"twice": "second", "index": idx, "restore": x}, chain=True)
        for spec in (first, second):
            if FORMS[kind] == "i":
                spec.imm = idx
            else:
                spec.rs2_val, spec.rs2_class = idx, "zero"
        specs += [first, second]
    for kind in SBIT_REG:
        for ucls in UPPER_NONZERO:
            idx = rng.randrange(32)
            rs2, eff = upper_value(rng, ucls, idx)
            specs.append(Spec("TP-BIT-019", kind, rng.randrange(1 << 32), rs2, rs1_class="rand", rs2_class=ucls,
                              tags={"upper": ucls, "eff": eff}))
    for kind in SBIT_IMM:
        specs.append(Spec("TP-BIT-019", f"illegal_{kind}", rng.randrange(1 << 32), imm=rng.randrange(32),
                          rs1_class="rand", tags={"illegal": kind}))
    return specs


def _spec_020(rng):
    specs = []
    shift = rng.randrange(1, len(CLMUL_CLASSES))
    for kind in ITEM_OPS["TP-BIT-020"]:
        for i, c1 in enumerate(CLMUL_CLASSES):
            specs.append(_rs_pair(rng, "TP-BIT-020", kind, c1, CLMUL_CLASSES[(i + shift) % len(CLMUL_CLASSES)]))
    return specs


def _spec_021(rng):
    specs = []
    for kind in ITEM_OPS["TP-BIT-020"]:
        for case, c2 in (("x_0", "zero"), ("x_1", "one")):
            c1, x = _nonzero(rng)
            specs.append(Spec("TP-BIT-021", kind, x, operand_value(rng, c2), rs1_class=c1, rs2_class=c2, tags={"case": case}))
        specs.append(Spec("TP-BIT-021", kind, MASK32, MASK32, rs1_class="all_ones", rs2_class="all_ones", tags={"case": "ones"}))
        for case in ("lt32", "ge32"):
            if case == "lt32":
                i = rng.randrange(32)
                j = rng.randrange(32 - i)
            else:
                i = rng.randrange(1, 32)
                j = rng.randrange(32 - i, 32)
            assert (i + j < 32) == (case == "lt32")
            specs.append(Spec("TP-BIT-021", kind, 1 << i, 1 << j, rs1_class="single_bit", rs2_class="single_bit",
                              tags={"case": case, "i": i, "j": j}))
    assert reference("clmul", MASK32, MASK32) == 0x55555555 and reference("clmulh", MASK32, MASK32) == 0x55555555
    for _ in range(2):   # the program-computed identity over one operand pair (a chained unit of four)
        c1, a = _nonzero(rng)
        c2, b = _nonzero(rng)
        for kind in ITEM_OPS["TP-BIT-020"]:
            specs.append(Spec("TP-BIT-021", kind, a, b, rs1_class=c1, rs2_class=c2, tags={"ident": kind}, follow=kind != "clmul"))
        specs.append(Spec("TP-BIT-021", "ident", tags={"ident": "check"}, follow=True))
    return specs


def _spec_038(rng):
    specs = []
    for kind in X0_RATIFIED:
        c1, v1 = _nonzero(rng)
        spec = Spec(ITEM_X0, f"x0_{kind}", v1, rs1_class=c1, rd_x0=True, tags={"mnemonic": kind})
        if FORMS[kind] == "r":
            spec.rs2_class, spec.rs2_val = _nonzero(rng)
        elif FORMS[kind] == "i":
            spec.imm = rng.randrange(1 << IMM_BITS[kind])
        specs.append(spec)
    for kind, form in X0_DRAFT.items():
        c1, v1 = _nonzero(rng)
        spec = Spec(ITEM_X0, f"x0_{kind}", v1, rs1_class=c1, rd_x0=True, tags={"mnemonic": kind, "form": form})
        if form in ("r", "r4"):
            spec.rs2_class, spec.rs2_val = _nonzero(rng)
        if form in ("i5", "i4", "r4i"):
            spec.imm = rng.randrange(32 if form != "i4" else 16)
        specs.append(spec)
    return specs


def _spec_040(rng):
    specs = [Spec(ITEM_MISA, "misa_read", tags={"when": "plain"}) for _ in range(2)]
    specs.append(Spec(ITEM_MISA, "misa_write", rng.randrange(1 << 32), rs1_class="rand", tags={"when": "write"}))
    specs.append(Spec(ITEM_MISA, "misa_read", tags={"when": "after_write"}, follow=True))
    return specs


ITEM_FLOORS = {"TP-BIT-002": _spec_002, "TP-BIT-003": _spec_003, "TP-BIT-004": _spec_004, "TP-BIT-005": _spec_005,
               "TP-BIT-006": _spec_006, "TP-BIT-007": _spec_007, "TP-BIT-008": _spec_008, "TP-BIT-009": _spec_009,
               "TP-BIT-010": _spec_010, "TP-BIT-014": _spec_014, "TP-BIT-015": _spec_015, "TP-BIT-017": _spec_017,
               "TP-BIT-018": _spec_018, "TP-BIT-019": _spec_019, "TP-BIT-020": _spec_020, "TP-BIT-021": _spec_021,
               ITEM_X0: _spec_038, ITEM_MISA: _spec_040}


def _extra(rng):
    """A random extra over the ratified mnemonics: W1 operands, W3 amounts, W4 register freedom (rd = x0, x0 source)."""
    item = rng.choice(list(ITEM_OPS))
    kind = rng.choice(ITEM_OPS[item])
    x0_src = FORMS[kind] != "c" and rng.random() < W4_X0_SRC
    c1, v1 = ("x0_src", 0) if x0_src else (weighted(rng, W1), None)
    spec = Spec(item, kind, 0 if x0_src else operand_value(rng, c1), rs1_class=c1, floor=False,
                rd_x0=FORMS[kind] != "c" and rng.random() < W4_RD_X0, tags={"extra": True})
    if FORMS[kind] == "r":
        if rng.random() < W4_RS_SAME and not x0_src:
            spec.rs2_val, spec.rs2_class, spec.same_rs = spec.rs1_val, c1, True
        else:
            spec.rs2_class = weighted(rng, W1)
            spec.rs2_val = operand_value(rng, spec.rs2_class)
            if kind in SBIT_REG:
                ucls = weighted(rng, {"zero": 4, "v32": 1, "v33": 1, "vFFFFFFE0": 1, "v80000000": 1, "vFFFFFFFF": 1, "other_nonzero": 2})
                spec.rs2_val, _ = upper_value(rng, ucls, rng.randrange(32))
                spec.rs2_class = ucls
    elif FORMS[kind] == "i":
        spec.imm = weighted(rng, {0: 1, 1: 1, 31: 1, "mid": 4})
        spec.imm = rng.randrange(2, 31) if spec.imm == "mid" else spec.imm
    return spec


def _filler(rng, regs):
    form = rng.choice(FILLER_FORMS)
    rd, ra, rb = (rng.choice(regs) for _ in range(3))
    if form in ("addi", "xori", "andi", "ori"):
        return f"{form} x{rd}, x{ra}, {rng.randrange(-2048, 2048)}"
    if form == "lui":
        return f"lui x{rd}, 0x{rng.randrange(1 << 20):x}"
    return f"{form} x{rd}, x{ra}, x{rb}"


def _place(rng, pool, cpool, idx, spec, prev, table, keep):
    """Registers and expected report words of one Spec."""
    kind = spec.kind
    tags = dict(spec.tags)
    aux = {}
    rs2 = 0
    rs2_val = spec.rs2_val
    imm = spec.imm
    free = [r for r in pool if r not in keep]
    if spec.chain:
        assert prev is not None and prev.rd != 0, f"chain without a source at op {idx}"
        rs1, rs1_val, chained = prev.rd, prev.expects[0], True
    else:
        rs1, rs1_val, chained = (0 if spec.rs1_class == "x0_src" else rng.choice(free)), spec.rs1_val, False
    if spec.same_rd:
        assert prev is not None and prev.rd != 0, f"same_rd without a previous rd at op {idx}"
    if kind.startswith("addr_"):
        base = kind[5:]
        rd = rng.choice([r for r in free if r != rs1])
        rs2 = rng.choice([r for r in free if r not in (rs1, rd)])
        expects = [table[tags["word"]]]
        return Op(idx, spec.item, kind, rd, rs1, rs2, rs1_val, 0, -1, expects, spec.floor, spec.rs1_class, spec.rs2_class, tags)
    if kind == "ident":
        a, b, c = prev.aux["ident"]
        t, u = rng.sample([r for r in free if r not in (a, b, c)], 2)
        return Op(idx, spec.item, kind, t, u, 0, 0, 0, -1, [0], spec.floor, "ident", "", tags, aux={"abc": (a, b, c)})
    if kind.startswith("illegal_"):
        base = kind[8:]
        rd = rng.choice(free)
        word = illegal_word(base, rd, rs1, imm)
        return Op(idx, spec.item, kind, rd, rs1, 0, rs1_val, 0, imm, [CAUSE_ILLEGAL, word], spec.floor, spec.rs1_class, "", tags, aux={"word": word})
    if kind == "misa_read":
        rd = rng.choice(free)
        return Op(idx, spec.item, kind, rd, 0, 0, 0, 0, -1, [MISA_VALUE], spec.floor, "", "", tags, chained)
    if kind == "misa_write":
        rd = rng.choice([r for r in free if r != rs1])
        return Op(idx, spec.item, kind, rd, rs1, 0, rs1_val, 0, -1, [MISA_VALUE], spec.floor, spec.rs1_class, "", tags)
    if kind.startswith("x0_"):
        base = kind[3:]
        form = X0_DRAFT.get(base, FORMS.get(base))
        rd = 0
        if form in ("r", "r4"):
            rs2 = rng.choice([r for r in free if r != rs1])
        if form in ("r4", "r4i"):
            aux["rs3"] = rng.choice([r for r in free if r not in (rs1, rs2)])
            aux["rs3_val"] = operand_value(rng, "pos_rand")
        return Op(idx, spec.item, kind, rd, rs1, rs2, rs1_val, rs2_val, imm, [0], spec.floor, spec.rs1_class, spec.rs2_class, tags, aux=aux)
    form = FORMS[kind]
    if form == "c":
        rd = rs1 = rng.choice([r for r in cpool if r not in keep])
    else:
        # same_rs means the rs1_eq_rs2 shape, which needs rd != rs1: an rd draw that happened to
        # pick rs1 turned the op into all_same instead, at a few seeds per op
        rd_pool = [r for r in free if r != rs1] if spec.same_rs else free
        rd = prev.rd if spec.same_rd else (rs1 if spec.same_all else (0 if spec.rd_x0 else rng.choice(rd_pool)))
    if form == "r":
        rs2 = rs1 if (spec.same_rs or spec.same_all) else rng.choice([r for r in free if r != rs1])
        if spec.same_rs or spec.same_all:
            rs2_val = rs1_val
    expect = reference(kind, rs1_val, rs2_val, imm) if rd != 0 else 0
    return Op(idx, spec.item, kind, rd, rs1, rs2, rs1_val, rs2_val, imm, [expect], spec.floor, spec.rs1_class, spec.rs2_class, tags, chained)


def _items(ops):
    """Per-item expectations the test asserts: op index lists per class, case, position or pair."""
    def grp():
        return {}

    def add(d, key, op):
        d.setdefault(key, []).append(op.idx)

    items = {i: {"ops": [], "vacuous": [], "floor": []} for i in BUILT_ITEMS}
    f = {i: {} for i in BUILT_ITEMS}
    for op in ops:
        it = items[op.item]
        (it["vacuous"] if op.vacuous else it["ops"]).append(op.idx)
        if op.floor and not op.vacuous:
            it["floor"].append(op.idx)
        if op.vacuous:
            continue
        t = op.tags
        d = f[op.item]
        if op.item == "TP-BIT-002":
            if op.kind.startswith("addr_"):
                add(d.setdefault("addr", grp()), op.kind[5:], op)
            elif op.rs1_class in RS1_CLASSES and op.rs2_class in RS2_CLASSES:
                add(d.setdefault("op_rs1", grp()), (op.kind, op.rs1_class), op)
                add(d.setdefault("op_rs2", grp()), (op.kind, op.rs2_class), op)
        elif op.item == "TP-BIT-003" and "case" in t:
            add(d.setdefault("cases", grp()), (op.kind, t["case"]), op)
        elif op.item == "TP-BIT-004":
            if "result" in t:
                add(d.setdefault("result", grp()), (op.kind, t["result"]), op)
            elif op.rs1_class in RS1_CLASSES and op.rs2_class in RS2_CLASSES:
                add(d.setdefault("op_rs1", grp()), (op.kind, op.rs1_class), op)
                add(d.setdefault("op_rs2", grp()), (op.kind, op.rs2_class), op)
        elif op.item == "TP-BIT-005":
            if "cls" in t:
                add(d.setdefault("op_operand", grp()), (op.kind, t["cls"]), op)
            if "result" in t:
                add(d.setdefault("result", grp()), (op.kind, t["result"]), op)
        elif op.item == "TP-BIT-006":
            if "pos" in t:
                add(d.setdefault("op_single", grp()), (op.kind, t["pos"]), op)
            if "result" in t:
                add(d.setdefault("result", grp()), (op.kind, t["result"]), op)
        elif op.item in ("TP-BIT-007", "TP-BIT-008"):
            if "sign" in t:
                add(d.setdefault("op_sign", grp()), (op.kind, t["sign"]), op)
            if "case" in t:
                add(d.setdefault("cases", grp()), (op.kind, t["case"]), op)
            if op.item == "TP-BIT-007" and op.rs1_class in RS1_CLASSES and op.rs2_class in RS2_CLASSES:
                add(d.setdefault("op_rs1", grp()), (op.kind, op.rs1_class), op)
                add(d.setdefault("op_rs2", grp()), (op.kind, op.rs2_class), op)
        elif op.item == "TP-BIT-009":
            if "cls" in t:
                add(d.setdefault("form_class", grp()), (op.kind, t["cls"]), op)
            if "exact" in t:
                add(d.setdefault("exact", grp()), (op.kind, t["exact"]), op)
        elif op.item == "TP-BIT-010" and "cls" in t:
            add(d.setdefault("form_class", grp()), (op.kind, t["cls"]), op)
        elif op.item == "TP-BIT-014" and "pattern" in t:
            add(d.setdefault("pattern", grp()), t["pattern"], op)
        elif op.item == "TP-BIT-015" and "case" in t:
            add(d.setdefault("cases", grp()), t["case"], op)
        elif op.item in ("TP-BIT-017", "TP-BIT-018"):
            if "icls" in t:
                add(d.setdefault("op_index_prior", grp()), (op.kind, t["icls"], t["prior"]), op)
            if "ocls" in t:
                add(d.setdefault("op_operand", grp()), (op.kind, t["ocls"]), op)
        elif op.item == "TP-BIT-019":
            if "index" in t and "twice" not in t:
                add(d.setdefault("op_index", grp()), (op.kind, t["index"]), op)
            if "case" in t:
                add(d.setdefault("cases", grp()), (op.kind, t["case"]), op)
            if t.get("twice") == "second":
                add(d.setdefault("twice", grp()), op.kind, op)
            if "upper" in t:
                add(d.setdefault("upper", grp()), (op.kind, t["upper"]), op)
            if "illegal" in t:
                add(d.setdefault("illegal", grp()), t["illegal"], op)
        elif op.item == "TP-BIT-020" and op.rs1_class in CLMUL_CLASSES:
            add(d.setdefault("op_rs1", grp()), (op.kind, op.rs1_class), op)
            add(d.setdefault("op_rs2", grp()), (op.kind, op.rs2_class), op)
        elif op.item == "TP-BIT-021":
            if "case" in t:
                add(d.setdefault("cases", grp()), (op.kind, t["case"]), op)
            if t.get("ident") == "check":
                add(d.setdefault("ident", grp()), "check", op)
        elif op.item == ITEM_X0:
            add(d.setdefault("mnemonic", grp()), t["mnemonic"], op)
        elif op.item == ITEM_MISA:
            add(d.setdefault("when", grp()), t["when"], op)
    for i in BUILT_ITEMS:
        items[i].update(f[i])
    return items


def wanted():
    """Every exhaustive set an item's fire-check names: item -> key -> the keys a plan must carry (the test asserts a
    matched carrier per key, the generator refuses a plan that misses one)."""
    return {
        "TP-BIT-002": {"op_rs1": {(k, c) for k in ITEM_OPS["TP-BIT-002"] for c in RS1_CLASSES},
                       "op_rs2": {(k, c) for k in ITEM_OPS["TP-BIT-002"] for c in RS2_CLASSES},
                       "addr": set(ITEM_OPS["TP-BIT-002"])},
        "TP-BIT-003": {"cases": {(k, c) for k in ITEM_OPS["TP-BIT-002"] for c in ("e0000000", "all_ones", "wrap", "same", "eq")}},
        "TP-BIT-004": {"op_rs1": {(k, c) for k in ITEM_OPS["TP-BIT-004"] for c in RS1_CLASSES},
                       "op_rs2": {(k, c) for k in ITEM_OPS["TP-BIT-004"] for c in RS2_CLASSES},
                       "result": {(k, c) for k in ITEM_OPS["TP-BIT-004"] for c in ("zero", "all_ones")}},
        "TP-BIT-005": {"op_operand": {(k, c) for k in ITEM_OPS["TP-BIT-005"] for c in COUNT_CLASSES},
                       "result": {(k, r) for k in ITEM_OPS["TP-BIT-005"] for r in ("r1", "r16")}},
        "TP-BIT-006": {"op_single": {(k, p) for k in ITEM_OPS["TP-BIT-005"] for p in range(32)},
                       "result": {("clz", "r32"), ("ctz", "r32"), ("cpop", "r32"), ("clz", "r0"), ("ctz", "r0"), ("cpop", "r0"),
                                  ("clz", "r31"), ("ctz", "r31"), ("cpop", "r31")}},
        "TP-BIT-007": {"op_sign": {(k, s) for k in ITEM_OPS["TP-BIT-007"] for s in ("pp", "pn", "np", "nn")},
                       "op_rs1": {(k, c) for k in ITEM_OPS["TP-BIT-007"] for c in RS1_CLASSES},
                       "op_rs2": {(k, c) for k in ITEM_OPS["TP-BIT-007"] for c in RS2_CLASSES}},
        "TP-BIT-008": {"op_sign": {(k, s) for k in ITEM_OPS["TP-BIT-007"] for s in ("pp", "pn", "np", "nn")},
                       "cases": {(k, c) for k in ITEM_OPS["TP-BIT-007"] for c in ("same", "eq", "m1_p1", "min_max")}},
        "TP-BIT-009": {"form_class": {(k, c) for k in ITEM_OPS["TP-BIT-009"] for c in SEXT_CLASSES},
                       "exact": {(k, x) for k in ITEM_OPS["TP-BIT-009"] for x in SEXT_EXACT[C_BASE.get(k, k)]}},
        "TP-BIT-010": {"form_class": {(k, c) for k in ITEM_OPS["TP-BIT-010"] for c in RS1_CLASSES}},
        "TP-BIT-014": {"pattern": set(range(16))},
        "TP-BIT-015": {"cases": {"bytes_01020304", "single_bit", "rand"}},
        "TP-BIT-017": {"op_index_prior": {(k, i, p) for k in SBIT_REG for i in INDEX_CLASSES for p in (0, 1)}},
        "TP-BIT-018": {"op_index_prior": {(k, i, p) for k in SBIT_IMM for i in INDEX_CLASSES for p in (0, 1)},
                       "op_operand": {(k, o) for k in SBIT_IMM for o in SBIT_OPERANDS}},
        "TP-BIT-019": {"op_index": {(k, i) for k in SBIT_REG + SBIT_IMM for i in (0, 31)},
                       "cases": {("bset", "set_on_set"), ("bclr", "clr_on_clr"), ("bseti", "set_on_set"), ("bclri", "clr_on_clr")},
                       "twice": {"binv", "binvi"}, "upper": {(k, u) for k in SBIT_REG for u in UPPER_NONZERO},
                       "illegal": set(SBIT_IMM)},
        "TP-BIT-020": {"op_rs1": {(k, c) for k in ITEM_OPS["TP-BIT-020"] for c in CLMUL_CLASSES},
                       "op_rs2": {(k, c) for k in ITEM_OPS["TP-BIT-020"] for c in CLMUL_CLASSES}},
        "TP-BIT-021": {"cases": {(k, c) for k in ITEM_OPS["TP-BIT-020"] for c in ("x_0", "x_1", "ones", "lt32", "ge32")},
                       "ident": {"check"}},
        ITEM_X0: {"mnemonic": set(X0_RATIFIED) | set(X0_DRAFT)},
        ITEM_MISA: {"when": {"plain", "write", "after_write"}},
    }


def check_coverage(items):
    want = wanted()
    for item, sets in want.items():
        for key, keys in sets.items():
            missing = keys - set(items[item].get(key, {}))
            assert not missing, f"{item} {key}: plan misses {sorted(missing, key=str)[:4]}"
    return want


def _red_choice(seed, red, red_item):
    if not red:
        return "", ""
    item, _, sel = (red_item or "").partition(":")
    item = item or red_rng(seed).choice(BUILT_ITEMS)
    assert item in BUILT_ITEMS, f"--red-item {item}: not a built item ({', '.join(BUILT_ITEMS)})"
    sel = sel or RED_SELECTORS[item][0]
    assert sel in RED_SELECTORS[item], f"--red-item {item}:{sel}: selectors are {', '.join(RED_SELECTORS[item])}"
    return item, sel


def _red_target(seed, ops, item, sel):
    """(op index, deviated field, value): the deviation changes the op's true result while the expectation stays."""
    rng = red_rng(seed)
    lone = [op for op in ops if op.item == item and op.floor and not op.chained
            and not (op.idx + 1 < len(ops) and ops[op.idx + 1].chained)]
    if sel == "x0":
        cands = [op for op in lone if op.rs1 != 0 and op.rs1_val != 0]
        assert cands, f"red {item}:{sel}: no eligible op at seed {seed}"
        return rng.choice(cands).idx, "reader", 0
    if sel == "csr":
        cands = [op for op in ops if op.kind == "misa_read"]
        return rng.choice(cands).idx, "csr", 0
    cands = [op for op in lone if op.kind in FORMS and op.rd != 0 and op.rs2 != op.rs1]
    assert cands, f"red {item}:{sel}: no eligible op at seed {seed}"
    rng.shuffle(cands)
    for op in cands:   # first op whose result moves under a one-bit flip or a fresh value of one source
        fields = ["rs1"] + (["rs2"] if op.form == "r" else [])
        for fld in rng.sample(fields, len(fields)):
            cur = getattr(op, f"{fld}_val")
            trials = [cur ^ (1 << bit) for bit in rng.sample(range(32), 32)] + [rng.randrange(1 << 32) for _ in range(8)]
            for new in trials:
                vals = {"rs1": op.rs1_val, "rs2": op.rs2_val}
                vals[fld] = new
                if reference(op.kind, vals["rs1"], vals["rs2"], op.imm) != op.expects[0]:
                    return op.idx, fld, new
    raise AssertionError(f"red {item}:{sel}: no op of {item} depends on its sources at seed {seed}")


def _insn_count(lines):
    return sum(1 for ln in lines if ln.startswith("  ") and not ln.lstrip().startswith("#"))


# every r-form op in the cross's own cp_op bin set, not just the ones that happened to fail: the
# sweep is scoped to the coverpoint, so a bin that is merely rare today cannot slip out of it
SWEEP_OPS = ("andn", "max", "maxu", "min", "minu", "orn", "pack", "packh", "packu",
             "sh1add", "sh2add", "sh3add", "xnor")
SWEEP_ITEM = {op: item for item, ops in ITEM_OPS.items() for op in ops if op in SWEEP_OPS}


def _binv_twice_pair(rng):
    """binv/binvi applied twice to the SAME rd and index (CG-BIT gen_bit_sbit_cg.cp_binv_twice).

    The second op restores the bit, which is why nothing else in the program produces this shape:
    every other single-bit sequence moves on to a different index or a different destination. The
    pair is chained and shares rd, so the two ops are adjacent and operate on one register.
    """
    idx = rng.randrange(32)
    c, v = _nonzero(rng)
    first = Spec("TP-BIT-018", "binvi", v, imm=idx, rs1_class=c, tags={"case": "binv_twice_first"})
    second = Spec("TP-BIT-018", "binvi", v, imm=idx, rs1_class=c,
                  tags={"case": "binv_twice_second"}, chain=True, same_rd=True)
    return [first, second]


def _relationship_sweep(rng):
    """Directed sweep of the op x register-relationship product (CG-BIT-001 cr_op_same).

    The allocator draws rd and rs2 independently of the op, so an op and a register relationship
    each appear across a run while their combination is left to coincidence: the all_same shapes
    that did turn up varied with any change to the draw stream. These specs pair each op with each
    relationship directly, which is what makes the cross a per-run fact rather than a lucky draw.
    """
    specs = []
    for op in SWEEP_OPS:
        item = SWEEP_ITEM[op]
        c, v = _nonzero(rng)
        specs.append(Spec(item, op, v, v, rs1_class=c, rs2_class=c,
                          tags={"case": "all_same", "sweep": True}, same_all=True))
        c, v = _nonzero(rng)
        specs.append(Spec(item, op, v, v, rs1_class=c, rs2_class=c,
                          tags={"case": "same", "sweep": True}, same_rs=True))
    return specs


def plan(seed, red=False, red_item=None):
    rng = program_rng(seed)
    eot_reg = rng.randrange(5, 32)
    pool = [r for r in range(1, 32) if r != eot_reg]
    cpool = [r for r in range(8, 16) if r != eot_reg]
    trap_tmp = rng.choice(pool)
    table = [rng.randrange(1 << 32) for _ in range(N_TABLE_WORDS)]
    units = []
    for make in ITEM_FLOORS.values():
        unit = []
        for spec in make(rng):
            if spec.chain or spec.follow:
                unit.append(spec)
            else:
                if unit:
                    units.append(unit)
                unit = [spec]
        units.append(unit)
    units += [[s] for s in _relationship_sweep(rng)]
    units.append(_binv_twice_pair(rng))
    units += [[_extra(rng)] for _ in range(rng.randint(*N_EXTRAS))]
    rng.shuffle(units)
    ops = []
    rep = 0
    for unit in units:
        prev = None
        keep = ()
        ident_regs = []
        for spec in unit:
            op = _place(rng, pool, cpool, len(ops), spec, prev, table, keep)
            if op.tags.get("ident") in ITEM_OPS["TP-BIT-020"]:
                ident_regs.append(op.rd)
                op.aux["ident"] = tuple(ident_regs)
            keep = tuple(sorted(set(keep) | {op.rd} - {0}))
            op.keep = keep
            live = set(keep) | ({prev.rd} if op.chained else set())
            op.fillers = [_filler(rng, [r for r in pool if r not in live]) for _ in range(rng.randrange(3))]
            op.rep = rep
            rep += len(op.expects)
            ops.append(op)
            prev = op
    for op in ops:
        if op.chained:
            assert ops[op.idx - 1].rd == op.rs1 != 0, f"broken chain at op {op.idx}"
    reports = [w for op in ops for w in op.expects]
    items = _items(ops)
    check_coverage(items)
    red_item, red_sel = _red_choice(seed, red, red_item)
    red_idx, red_field, red_val = _red_target(seed, ops, red_item, red_sel) if red else (-1, "", -1)
    p = Plan(seed, red, red_item, red_sel, eot_reg, trap_tmp, ops, reports, len(reports), 0, red_idx, red_field, red_val, items, table)
    p.min_retired = _insn_count(_body(p)) + _insn_count(_handler(p))
    return p


# ---- emission --------------------------------------------------------------------------------------------------------
def _emitted(p, op, fld):
    if p.red and op.idx == p.red_idx and p.red_field == fld:
        return p.red_val
    return getattr(op, f"{fld}_val")


def _op_lines(p, op):
    """The op and its report store(s); the red deviation applies to the one target op."""
    e = p.eot_reg
    red_here = p.red and op.idx == p.red_idx
    k = op.kind
    if k.startswith("addr_"):
        base = k[5:]
        return [f"  la   x{op.rs2}, gen_bit_table", f"  li   x{op.rs1}, {op.rs1_val}", f"  {base} x{op.rd}, x{op.rs1}, x{op.rs2}",
                f"  lw   x{op.rd}, 0(x{op.rd})", f"  sw   x{op.rd}, 0(x{e})"]
    if k == "ident":
        a, b, c = op.aux["abc"]
        t, u = op.rd, op.rs1
        return [f"  slli x{t}, x{b}, 1", f"  srli x{u}, x{a}, 31", f"  or   x{t}, x{t}, x{u}", f"  xor  x{t}, x{t}, x{c}",
                f"  sw   x{t}, 0(x{e})"]
    if k.startswith("illegal_"):
        return [f"  li   x{op.rs1}, 0x{op.rs1_val:08x}",
                f"  .word 0x{op.aux['word']:08x}   # {k[8:]} x{op.rd}, x{op.rs1}, {op.imm} with instr[25] = 1: illegal, handler reports mcause and mtval"]
    if k == "misa_read":
        csr = "mhartid" if red_here else "misa"
        return [f"  csrr x{op.rd}, {csr_hex(csr)}", f"  sw   x{op.rd}, 0(x{e})"]
    if k == "misa_write":
        return [f"  li   x{op.rs1}, 0x{op.rs1_val:08x}", f"  csrrw x{op.rd}, {csr_hex('misa')}, x{op.rs1}", f"  sw   x{op.rd}, 0(x{e})"]
    if k.startswith("x0_"):
        base = k[3:]
        form = X0_DRAFT.get(base, FORMS.get(base))
        out = [f"  li   x{op.rs1}, 0x{op.rs1_val:08x}"]
        if form in ("r", "r4"):
            out.append(f"  li   x{op.rs2}, 0x{op.rs2_val:08x}")
        if form in ("r4", "r4i"):
            out.append(f"  li   x{op.aux['rs3']}, 0x{op.aux['rs3_val']:08x}")
        if form == "u":
            out.append(f"  {base} x0, x{op.rs1}")
        elif form == "r":
            out.append(f"  {base} x0, x{op.rs1}, x{op.rs2}")
        elif form in ("i", "i5", "i4"):
            out.append(f"  {base} x0, x{op.rs1}, {op.imm}")
        elif form == "r4":
            out.append(f"  {base} x0, x{op.rs1}, x{op.aux['rs3']}, x{op.rs2}")
        else:
            out.append(f"  {base} x0, x{op.rs1}, x{op.aux['rs3']}, {op.imm}")
        out.append(f"  sw   x{op.rs1 if red_here else 0}, 0(x{e})   # x0 reader")
        return out
    form = op.form
    out = []
    if not op.chained and op.rs1 != 0:
        out.append(f"  li   x{op.rs1}, 0x{_emitted(p, op, 'rs1'):08x}")
    if form == "r" and op.rs2 != op.rs1 and op.rs2 != 0:
        out.append(f"  li   x{op.rs2}, 0x{_emitted(p, op, 'rs2'):08x}")
    if form == "c":
        out.append(f"  {k} {op.rd}")
    elif form == "u":
        out.append(f"  {k} x{op.rd}, x{op.rs1}")
    elif form == "r":
        out.append(f"  {k} x{op.rd}, x{op.rs1}, x{op.rs2}")
    else:
        out.append(f"  {k} x{op.rd}, x{op.rs1}, {op.imm}")
    out.append(f"  sw   x{op.rd}, 0(x{e})")
    return out


def _body(p):
    out = ["  la   x5, gen_bit_trap", f"  csrw {csr_hex('mtvec')}, x5", f"  li   x{p.eot_reg}, GEN_MM_EOT_ADDR"]
    for op in p.ops:
        red_mark = "  RED: deviates" if (p.red and op.idx == p.red_idx) else ""
        srcs = f"rs1={op.rs1_class} 0x{op.rs1_val:08x}" + (f" rs2={op.rs2_class} 0x{op.rs2_val:08x}" if op.rs2 else "")
        out.append(f"  # op {op.idx}: {op.item} {op.kind}{' imm=' + str(op.imm) if op.imm >= 0 else ''} "
                   f"{'floor' if op.floor else 'extra'} {srcs} -> {' '.join(f'0x{w:08x}' for w in op.expects)}{red_mark}")
        out += [f"  {f}" for f in op.fillers]
        out += _op_lines(p, op)
    return out


def _handler(p):
    t = p.trap_tmp
    return [f"  csrr x{t}, {csr_hex('mcause')}", f"  sw   x{t}, 0(x{p.eot_reg})", f"  csrr x{t}, {csr_hex('mtval')}",
            f"  sw   x{t}, 0(x{p.eot_reg})", f"  csrr x{t}, {csr_hex('mepc')}", f"  addi x{t}, x{t}, 4",
            f"  csrw {csr_hex('mepc')}, x{t}", "  mret"]


def emit(plan_):
    p = plan_
    out = [f"# gen_bit_ratified_prog.py seed={p.seed} red={int(p.red)}: generated, do not edit (k={p.k} reports, min_retired={p.min_retired})"]
    if p.red:
        out.append(f"# RED FIXTURE {p.red_item}:{p.red_sel}: op {p.red_idx} {p.red_field} deviates"
                   f"{f' to 0x{p.red_val:x}' if p.red_field in ('rs1', 'rs2') else ''}; the expectation keeps the true value")
    out += ['.include "gen_zc_insn.h"', '.include "gen_mmio_map.h"', ".section .text", ".globl _start", "_start:"]
    out += _body(p)
    out += [f"  li   gp, {TOHOST_PASS}", "  la   t5, tohost", "  sw   gp, 0(t5)", "1:", "  j    1b",
            "  .balign 256", ".globl gen_bit_trap", "gen_bit_trap:"]
    out += _handler(p)
    out += ["", ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
            ".align 4", "gen_bit_table:"]
    out += [f"  .word 0x{w:08x}" for w in p.table]
    out += [".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--red", action="store_true", help="emit a TDD red fixture (one op deviates)")
    ap.add_argument("--red-item", default=None, metavar="ID[:SEL]",
                    help="the item (and selector) the red fixture targets; built: " + ", ".join(BUILT_ITEMS))
    a = ap.parse_args()
    if a.red_item and not a.red:
        ap.error("--red-item needs --red")
    p = plan(a.seed, a.red, a.red_item)
    if a.red:
        g = plan(a.seed)
        assert (g.reports, g.k, g.min_retired) == (p.reports, p.k, p.min_retired), "red plan changed the expectations"
    text = emit(p)
    assert all(ord(ch) < 128 for ch in text), "non-ASCII in the generated program"
    with open(a.out, "w") as f:
        f.write(text)
    floor = sum(1 for op in p.ops if op.floor)
    print(f"gen_bit_ratified_prog seed={p.seed} red={int(p.red)} red_item={p.red_item}:{p.red_sel} k={p.k} ops={len(p.ops)} "
          f"floor={floor} min_retired={p.min_retired} red_idx={p.red_idx} red_field={p.red_field} -> {a.out}")


if __name__ == "__main__":
    main()
