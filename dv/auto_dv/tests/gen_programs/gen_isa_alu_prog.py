#!/usr/bin/env python3
"""gen_isa_alu_prog: per-seed program generator of gen_test_isa_alu (plan group gen_isa_alu: TP-ISA-001 I-type ALU,
002 addi wrap, 003 slti/sltiu boundaries, 004 HINTs with rd = x0, 005 lui/auipc, 006 lui/auipc extremes and PC wrap,
007 R-type ALU, 008 add/sub wrap, 009 slt/sltu boundaries, 052 writes to x0 discarded; dv/auto_dv/docs/gen_test_plan.md
AREA ISA, Version 2 of 2026-09-03 12:43 UTC).

plan(seed, red=False, red_item=None) draws the scenario from random.Random(f"{seed}:program:isa_alu"): one shuffled
stream of units over x1..x23 with unrelated filler instructions (x24..x26) between them and random 2-byte c.nop
insertions so the 32-bit instructions run at both PC alignments. Every unit stores the RAW observation (rd of the op,
rd of the x0 reader, the minstret delta of a hint block, the word read back after a store, the mcountinhibit read-back
of the TP-ISA-004 precondition) to GEN_MM_EOT_ADDR; the
expected value of every report word is computed here from the RV32I text (tools/specs/riscv-isa-manual/src/unpriv/
rv32.adoc "Integer Register-Immediate Instructions", "Integer Register-Register Instructions", "HINT Instructions";
zca.adoc for the compressed HINT code points; m-st-ext.adoc / zbb for the x0-writer classes of TP-ISA-052) or, for
auipc, by the test from the site's linked address (every lui/auipc site carries a global label gen_u<n>, so the test
reads the pc from the image sidecar and this generator models the layout to place both alignments).

Directed floors inside the random stream (the test asserts each per seed from the observed words):
TP-ISA-001 every op x every rs1 class and x every imm class (CG-ISA-001 classes, weights 1:1:1:1:1:4:4), rs1 == rd and
rd = x0 forms, every result class; TP-ISA-002 both wrap signs with the pinned pairs; TP-ISA-003 every cp_slt_case;
TP-ISA-004 every cp_hint_class in a hint/reader pair (reader rs1 = x0 and rs2 = x0 forms, distance 1..3) plus
HINT_BLOCK-hint blocks bracketed by minstret reads; TP-ISA-005 every imm20 class per op at both alignments; TP-ISA-006
lui 0xFFFFF / 0, auipc imm 0 at both alignments, auipc wrap and no-wrap at both alignments; TP-ISA-007 every op x rs1
class, x rs2 class, x sign pair, x register relation, equal operands, result classes; TP-ISA-008 every wrap-table row;
TP-ISA-009 equal, (INT_MIN, INT_MAX), (INT_MIN, 1), rs1 = x0 for both ops; TP-ISA-052 every cp_writer_class with an x0
reader of each form. Vacuous compares (rd = x0 forms) and degenerate operands (and/andi with 0, or/ori with all ones)
are counted apart from the observations.

The red fixture (red=True) deviates the PROGRAM on one intent of one item while the expectation keeps the true program,
so exactly that item's fire-check fails; every deviation is a one-field override of one instruction (mnemonic,
immediate or destination) so k, min_retired and the layout stay those of the green program. red_item names the item
(RED_ITEMS); None lets random.Random(f"{seed}:red") draw it.

CLI: python3 gen_isa_alu_prog.py --seed N --out <file.S> [--red [--red-item TP-ISA-nnn]]
"""
import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP  # noqa: E402  (placeholder pc base of the red self-check)
from dv.auto_dv.tests.gen_programs.gen_prog_const import TOHOST_PASS, csr_hex  # noqa: E402

RNG_TAG = "program:isa_alu"
RED_TAG = "red"
M = 0xFFFFFFFF
INT_MIN, INT_MAX = 0x80000000, 0x7FFFFFFF
EOT_REG = 28                      # holds GEN_MM_EOT_ADDR for every report store
BASE_REG = 27                     # holds the address of gen_scratch (TP-ISA-052 loads and stores)
CTR_A, CTR_B = 29, 30             # minstret reads of a hint block
SPARE = 31                        # jalr target register (TP-ISA-052)
FILLER_REGS = (24, 25, 26)        # the unrelated instructions between units work on these
POOL = tuple(range(1, 24))        # rd / rs1 / rs2 of the units
SCRATCH = "gen_scratch"
SCRATCH_WORDS = 128

I001, I002, I003, I004, I005 = "TP-ISA-001", "TP-ISA-002", "TP-ISA-003", "TP-ISA-004", "TP-ISA-005"
I006, I007, I008, I009, I052 = "TP-ISA-006", "TP-ISA-007", "TP-ISA-008", "TP-ISA-009", "TP-ISA-052"
RED_ITEMS = (I001, I002, I003, I004, I005, I006, I007, I008, I009, I052)

# Stimulus floors of the items (plan Stimulus lines): counts per seed.
N_IMM_MIN, N_REG_MIN, N_U_MIN = 2000, 3000, 500
HINT_BLOCK = 64
HINT_BLOCK_DELTA = HINT_BLOCK + 1   # the first csrr retires inside the window (plan TP-ISA-004, rtl-arch T-053)

IMM_OPS = ("addi", "slti", "sltiu", "xori", "ori", "andi")
REG_OPS = ("add", "sub", "slt", "sltu", "xor", "or", "and")
SHIFT_I = ("slli", "srli", "srai")
# CG-ISA-001/002 operand classes with the items' weights (TP-ISA-001: 1:1:1:1:1:4:4); W2 immediates (plan "Layer-1
# weight tables"); TP-ISA-005 imm20 mix (1:1:1:1:6).
RS_CLASSES = {"zero": 1, "all_ones": 1, "int_min": 1, "int_max": 1, "one": 1, "pos_rand": 4, "neg_rand": 4}
IMM_CLASSES = {"zero": 1, "plus1": 1, "minus1": 1, "max_pos": 1, "min_neg": 1, "pos_rand": 4, "neg_rand": 4}
IMM20_CLASSES = {"zero": 1, "all_ones": 1, "msb": 1, "one": 1, "rand": 6}
REL_CLASSES = ("rs1_eq_rs2", "all_same", "rs1_eq_rd", "rs2_eq_rd", "distinct")   # CG-ISA-002 cp_same_regs
SIGN_PAIRS = ("pp", "pn", "np", "nn")
RESULT_CLASSES = ("zero", "all_ones", "int_min", "int_max", "one", "other")
W4_RD_X0, W4_RS_EQ_RD, W4_EQ_OPERANDS = 16, 8, 8   # W4: rd = x0 1/16, rs == rd 1/8; TP-ISA-007 equal operands 1/8
# CG-ISA-005 cp_hint_class (rv32.adoc HINT table: computational instructions with rd = x0; the two semihosting markers).
HINT_CLASSES = ("canonical_nop", "addi_x0_nzimm", "andi_x0", "ori_x0", "xori_x0", "slti_x0", "sltiu_x0", "lui_x0",
                "auipc_x0", "add_x0", "sub_x0", "sll_x0", "srl_x0", "sra_x0", "slt_x0", "sltu_x0", "xor_x0", "or_x0",
                "and_x0", "slli_x0_semihost", "srai_x0_semihost", "slli_x0_other", "srli_x0", "srai_x0_other")
HINT_READERS = ("add_rs1z", "add_rs2z", "addi_rs1z", "or_rs1z", "xor_rs2z", "sub_rs2z", "sltu_rs1z", "sll_rs2z")
# CG-ISA-005 cp_writer_class (zcb_alu is an ignore bin: Zcb forms cannot name x0).
WRITER_CLASSES = ("alu_imm", "shift", "alu_reg", "lui_auipc", "load", "csrr", "jal", "jalr", "mul", "mulh",
                  "div_rem", "bit_1cyc", "bit_2cyc", "cmp_hint")
X0_READERS = ("add_x0_x0", "sw_x0", "beq_x0")
MUL_OPS = ("mul",)
MULH_OPS = ("mulh", "mulhu", "mulhsu")
DIV_OPS = ("div", "divu", "rem", "remu")
BIT1_R = ("andn", "orn", "xnor", "sh1add", "sh2add", "sh3add", "min", "max", "minu", "maxu")   # single-cycle Zba/Zbb
BIT2_R = ("rol", "ror")                                                                       # ibex_decoder alu_multicycle
CMP_HINTS = ("c.li", "c.lui", "c.slli", "c.mv", "c.add")
FILLER_TEMPLATES = ("addi x24, x24, {imm12}", "xori x25, x25, {imm12}", "slli x26, x26, {sh}", "add x24, x25, x26",
                    "sub x26, x24, x25", "lui x25, {imm20}", "andi x24, x24, {imm12}", "or x26, x26, x25")
CNOP = ".2byte 0x0001"            # c.nop: flips the PC alignment of the 32-bit instructions that follow


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def s32(v):
    v &= M
    return v - (1 << 32) if v & 0x80000000 else v


def sext(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v


def operand(rng, cls):
    fixed = {"zero": 0, "all_ones": M, "int_min": INT_MIN, "int_max": INT_MAX, "one": 1}
    if cls in fixed:
        return fixed[cls]
    if cls == "pos_rand":
        return rng.randint(2, INT_MAX - 1)
    if cls == "neg_rand":
        return rng.randint(INT_MIN + 1, M - 1)
    raise ValueError(f"unknown operand class {cls}")


def rs_class(v):
    return {0: "zero", M: "all_ones", INT_MIN: "int_min", INT_MAX: "int_max", 1: "one"}.get(v, "pos_rand" if v < INT_MIN else "neg_rand")


def imm12(rng, cls):
    fixed = {"zero": 0, "plus1": 1, "minus1": -1, "max_pos": 2047, "min_neg": -2048}
    if cls in fixed:
        return fixed[cls]
    if cls == "pos_rand":
        return rng.randint(2, 2046)
    if cls == "neg_rand":
        return rng.randint(-2047, -2)
    raise ValueError(f"unknown immediate class {cls}")


def imm_class(i):
    return {0: "zero", 1: "plus1", -1: "minus1", 2047: "max_pos", -2048: "min_neg"}.get(i, "pos_rand" if i > 0 else "neg_rand")


def imm20(rng, cls):
    fixed = {"zero": 0, "all_ones": 0xFFFFF, "msb": 0x80000, "one": 1}
    return fixed[cls] if cls in fixed else rng.randint(2, 0xFFFFE)


def imm20_class(i):
    return {0: "zero", 0xFFFFF: "all_ones", 0x80000: "msb", 1: "one"}.get(i, "rand")


def result_class(v):
    return {0: "zero", M: "all_ones", INT_MIN: "int_min", INT_MAX: "int_max", 1: "one"}.get(v, "other")


# ---- RV32I / M / Zb models (the expectations; rv32.adoc, m-st-ext.adoc, zbb.adoc) -----------------------------------
def alu_i(op, a, imm):
    i = imm & M
    if op == "addi":
        return (a + i) & M
    if op == "slti":
        return int(s32(a) < imm)
    if op == "sltiu":
        return int(a < i)
    if op == "xori":
        return a ^ i
    if op == "ori":
        return a | i
    if op == "andi":
        return a & i
    raise ValueError(op)


def alu_r(op, a, b):
    if op == "add":
        return (a + b) & M
    if op == "sub":
        return (a - b) & M
    if op == "slt":
        return int(s32(a) < s32(b))
    if op == "sltu":
        return int(a < b)
    if op == "xor":
        return a ^ b
    if op == "or":
        return a | b
    if op == "and":
        return a & b
    raise ValueError(op)


def shift(op, a, sh):
    sh &= 31
    if op in ("slli", "sll"):
        return (a << sh) & M
    if op in ("srli", "srl"):
        return a >> sh
    if op in ("srai", "sra"):
        return (s32(a) >> sh) & M
    raise ValueError(op)


def mul_op(op, a, b):
    if op == "mul":
        return (a * b) & M
    if op == "mulh":
        return ((s32(a) * s32(b)) >> 32) & M
    if op == "mulhu":
        return (a * b) >> 32
    if op == "mulhsu":
        return ((s32(a) * b) >> 32) & M
    raise ValueError(op)


def div_op(op, a, b):
    sa, sb = s32(a), s32(b)
    if op == "div":
        if b == 0:
            return M
        if sa == -(1 << 31) and sb == -1:
            return INT_MIN
        q = abs(sa) // abs(sb)
        return (-q if (sa < 0) != (sb < 0) else q) & M
    if op == "divu":
        return M if b == 0 else a // b
    if op == "rem":
        if b == 0:
            return a
        if sa == -(1 << 31) and sb == -1:
            return 0
        q = abs(sa) // abs(sb)
        q = -q if (sa < 0) != (sb < 0) else q
        return (sa - q * sb) & M
    if op == "remu":
        return a if b == 0 else a % b
    raise ValueError(op)


def bit_op(op, a, b):
    if op == "andn":
        return a & ~b & M
    if op == "orn":
        return (a | ~b) & M
    if op == "xnor":
        return ~(a ^ b) & M
    if op in ("sh1add", "sh2add", "sh3add"):
        return (b + (a << int(op[2]))) & M
    if op == "min":
        return a if s32(a) < s32(b) else b
    if op == "max":
        return a if s32(a) > s32(b) else b
    if op == "minu":
        return min(a, b)
    if op == "maxu":
        return max(a, b)
    if op in ("rol", "ror", "rori"):
        sh = b & 31
        if sh == 0:
            return a
        return ((a << sh) | (a >> (32 - sh))) & M if op == "rol" else ((a >> sh) | (a << (32 - sh))) & M
    raise ValueError(op)


def u_value(op, imm, pc):
    """lui / auipc result (rv32.adoc norm:lui_op, norm:auipc_op); pc is the address of the instruction."""
    return (imm << 12) & M if op == "lui" else (pc + (imm << 12)) & M


def li_len(v):
    """Bytes of `li rd, v` under .option norvc (gas: addi, lui, or lui + addi)."""
    v &= M
    if -2048 <= s32(v) <= 2047 or v & 0xFFF == 0:
        return 4
    return 8


@dataclass
class Report:
    idx: int
    item: str
    expect: int          # None when the value depends on the linked pc (kind auipc)
    text: str
    kind: str = "value"  # value | auipc
    label: str = ""      # gen_u<n> site label of an auipc report
    imm: int = 0         # imm20 of an auipc report
    op_idx: int = -1     # index of the unit in Plan.ops


@dataclass
class Op:
    kind: str                 # imm | slt_i | hint_pair | hint_block | u | reg | slt_r | x0w | pre | filler | cnop
    item: str = ""
    op: str = ""              # mnemonic of the observed instruction
    rd: int = 0
    rs1: int = 0
    rs2: int = 0
    a: int = 0                # rs1 value (loaded with li)
    b: int = 0                # rs2 value
    imm: int = 0              # imm12 (signed) / imm20 / shamt / imm6
    tags: dict = field(default_factory=dict)      # coverage classes of the unit
    label: str = ""           # gen_u<n> site label (lui / auipc)
    align: int = -1           # wanted pc[1] of the site (-1: free)
    reader: dict = None       # hint_pair / x0w reader
    hints: list = None        # hint_block: the HINT_BLOCK hints as (text, hint class)
    mid: list = None          # filler texts between the hint / writer and its reader
    red: dict = field(default_factory=dict)       # one-field override of the emitted instruction (red fixture)
    text: str = ""            # filler text / pre-unit text
    words: tuple = ()         # gen_scratch word offsets (x0w load / store reader)
    ridx: list = field(default_factory=list)      # report indices of the unit
    off: int = -1             # modeled byte offset of the observed instruction from _start


@dataclass
class Plan:
    seed: int
    red: bool
    ops: list
    reports: list
    k: int
    min_retired: int
    items: dict
    scratch_init: list
    filler_init: tuple
    summary: dict
    red_item: str
    red_note: str
    body: list                # rendered .text lines after _start
    sites: dict               # gen_u<n> label -> modeled byte offset from _start


def pick(rng, exclude=()):
    return rng.choice([r for r in POOL if r not in exclude])


# ---- unit builders --------------------------------------------------------------------------------------------------
def imm_unit(rng, op, rs1_cls=None, imm_cls=None, rd=None, rs1_eq_rd=None, a=None, imm=None):
    rs1_cls = rs1_cls or weighted(rng, RS_CLASSES)
    imm_cls = imm_cls or weighted(rng, IMM_CLASSES)
    a = operand(rng, rs1_cls) if a is None else a
    imm = imm12(rng, imm_cls) if imm is None else imm
    if rd is None:
        rd = 0 if rng.randrange(W4_RD_X0) == 0 else pick(rng)
    if rs1_eq_rd is None:
        rs1_eq_rd = rd != 0 and rng.randrange(W4_RS_EQ_RD) == 0
    rs1 = rd if rs1_eq_rd and rd else pick(rng, (rd,))
    return Op("imm", I001, op, rd, rs1, 0, a, 0, imm,
              tags={"rs1_cls": rs_class(a), "imm_cls": imm_class(imm), "rs1_eq_rd": rs1 == rd != 0})


def build_imm_units(rng):
    ops = []
    for op in IMM_OPS:
        ops += [imm_unit(rng, op, rs1_cls=c, rd=pick(rng)) for c in RS_CLASSES]
        ops += [imm_unit(rng, op, imm_cls=c, rd=pick(rng)) for c in IMM_CLASSES]
        ops.append(imm_unit(rng, op, rd=0))
        ops.append(imm_unit(rng, op, rd=pick(rng), rs1_eq_rd=True))
        ops.append(imm_unit(rng, op, rd=pick(rng), rs1_eq_rd=False))
    # result classes (CG-ISA-001 cp_result_class): one recipe each
    ops.append(imm_unit(rng, "andi", rd=pick(rng), imm=0))                                   # zero
    ops.append(imm_unit(rng, "ori", rd=pick(rng), imm=-1))                                   # all_ones
    ops.append(imm_unit(rng, "addi", rd=pick(rng), a=INT_MIN, imm=0))                        # int_min
    ops.append(imm_unit(rng, "addi", rd=pick(rng), a=INT_MAX, imm=0))                        # int_max
    ops.append(imm_unit(rng, "addi", rd=pick(rng), a=0, imm=1))                              # one
    while len(ops) < N_IMM_MIN + rng.randint(0, 200):
        ops.append(imm_unit(rng, rng.choice(IMM_OPS)))
    return ops


def wrap_addi_unit(rng, kind, a=None, imm=None):
    """TP-ISA-002: addi whose signed result flips sign (pos: rs1 near INT_MAX, imm > INT_MAX - rs1; neg: mirrored)."""
    if kind == "pos":
        a = rng.randint(INT_MAX - 2046, INT_MAX) if a is None else a
        imm = rng.randint(INT_MAX - a + 1, 2047) if imm is None else imm
    elif kind == "neg":
        a = rng.randint(INT_MIN, INT_MIN + 0x7FF) if a is None else a
        hi = -(1 << 31) - s32(a) - 1          # imm < INT_MIN - rs1 (signed)
        imm = rng.randint(-2048, hi) if imm is None else imm
    else:
        a, imm = operand(rng, weighted(rng, RS_CLASSES)), imm12(rng, weighted(rng, IMM_CLASSES))
    rd = pick(rng)
    return Op("imm", I002, "addi", rd, pick(rng, (rd,)), 0, a, 0, imm, tags={"wrap": addi_wrap_kind(a, imm)})


def addi_wrap_kind(a, imm):
    r = alu_i("addi", a, imm)
    if s32(a) >= 0 and imm > 0 and s32(r) < 0:
        return "pos"
    if s32(a) < 0 and imm < 0 and s32(r) >= 0:
        return "neg"
    return "none"


def build_addi_wrap_units(rng):
    ops = [wrap_addi_unit(rng, "pos", a=INT_MAX, imm=1), wrap_addi_unit(rng, "neg", a=INT_MIN, imm=-1)]
    for _ in range(rng.randint(40, 80)):
        ops.append(wrap_addi_unit(rng, weighted(rng, {"pos": 30, "neg": 30, "rand": 40})))
    return ops


def slt_case(op, a, imm):
    """CG-ISA-001 cp_slt_case of a slti/sltiu operand pair."""
    if op == "slti" and a == INT_MIN and imm == 0:
        return "slti_intmin_0"
    if op == "slti" and a == 0 and imm < 0:
        return "slti_0_neg"
    if op == "sltiu" and a == M and imm == -1:
        return "sltiu_ones_m1"
    if a == (imm & M):
        return "eq"
    if op == "sltiu" and imm == -1:
        return "sltiu_imm_m1"
    if op == "sltiu" and imm == 1:
        return "sltiu_seqz"
    return "other"


def slt_i_unit(rng, op, a, imm):
    rd = pick(rng)
    return Op("slt_i", I003, op, rd, pick(rng, (rd,)), 0, a, 0, imm, tags={"case": slt_case(op, a, imm)})


def build_slt_i_units(rng):
    def rnd_imm():
        return imm12(rng, weighted(rng, IMM_CLASSES))
    table = []
    for op in ("slti", "sltiu"):
        i = rnd_imm()
        table.append(slt_i_unit(rng, op, i & M, i))                                    # eq
    table.append(slt_i_unit(rng, "slti", INT_MIN, 0))                                  # slti_intmin_0
    table.append(slt_i_unit(rng, "slti", 0, -2048))                                    # slti_0_neg (min imm)
    table.append(slt_i_unit(rng, "slti", 0, rng.randint(-2047, -1)))
    table.append(slt_i_unit(rng, "sltiu", operand(rng, "pos_rand"), -1))               # sltiu_imm_m1
    for a in (0, 1, rng.getrandbits(32) | 2):
        table.append(slt_i_unit(rng, "sltiu", a, 1))                                   # sltiu_seqz
    table.append(slt_i_unit(rng, "sltiu", M, -1))                                      # sltiu_ones_m1
    n = rng.randint(40, 80)
    for _ in range(n // 2):
        row = rng.choice(table)
        a = row.a if row.tags["case"] not in ("sltiu_imm_m1",) else operand(rng, weighted(rng, RS_CLASSES))
        table.append(slt_i_unit(rng, row.op, a, row.imm))
    for _ in range(n - n // 2):
        table.append(slt_i_unit(rng, rng.choice(("slti", "sltiu")), operand(rng, weighted(rng, RS_CLASSES)), rnd_imm()))
    return table


def hint_text(cls, rs1, rs2, imm):
    """Assembly of one HINT (rd = x0) of the class."""
    if cls == "canonical_nop":
        return "addi x0, x0, 0"
    if cls == "addi_x0_nzimm":
        return f"addi x0, x{rs1}, {imm}"
    if cls in ("andi_x0", "ori_x0", "xori_x0", "slti_x0", "sltiu_x0"):
        return f"{cls[:-3]} x0, x{rs1}, {imm}"
    if cls in ("lui_x0", "auipc_x0"):
        return f"{cls[:-3]} x0, 0x{imm:x}"
    if cls in ("add_x0", "sub_x0", "sll_x0", "srl_x0", "sra_x0", "slt_x0", "sltu_x0", "xor_x0", "or_x0", "and_x0"):
        return f"{cls[:-3]} x0, x{rs1}, x{rs2}"
    if cls == "slli_x0_semihost":
        return "slli x0, x0, 0x1f"
    if cls == "srai_x0_semihost":
        return "srai x0, x0, 7"
    if cls in ("slli_x0_other", "srli_x0", "srai_x0_other"):
        return f"{cls.split('_')[0]} x0, x{rs1}, {imm}"
    raise ValueError(cls)


def hint_would_be(cls, a, b, imm):
    """Value the HINT would write if x0 were writable (None for auipc: pc-dependent)."""
    if cls == "canonical_nop":
        return 0
    if cls == "addi_x0_nzimm":
        return alu_i("addi", a, imm)
    if cls in ("andi_x0", "ori_x0", "xori_x0", "slti_x0", "sltiu_x0"):
        return alu_i(cls[:-3], a, imm)
    if cls == "lui_x0":
        return u_value("lui", imm, 0)
    if cls == "auipc_x0":
        return None
    if cls in ("sll_x0", "srl_x0", "sra_x0"):
        return shift(cls[:-3], a, b)
    if cls.endswith("_x0") and cls[:-3] in REG_OPS:
        return alu_r(cls[:-3], a, b)
    if cls in ("slli_x0_semihost", "srai_x0_semihost"):
        return 0
    return shift(cls.split("_")[0], a, imm)


def hint_draw(rng, cls, regs):
    """(rs1, rs2, imm, a, b) of a HINT of the class over registers in `regs`, would-be result nonzero where the class allows."""
    for _ in range(64):
        rs1 = rng.choice(regs)
        rs2 = rng.choice([r for r in regs if r != rs1])
        a, b = operand(rng, weighted(rng, RS_CLASSES)), operand(rng, weighted(rng, RS_CLASSES))
        imm = 0
        if cls == "addi_x0_nzimm":
            imm = rng.choice([i for i in range(-2048, 2048) if i != 0])
        elif cls in ("andi_x0", "ori_x0", "xori_x0", "slti_x0", "sltiu_x0"):
            imm = imm12(rng, weighted(rng, IMM_CLASSES))
        elif cls in ("lui_x0", "auipc_x0"):
            imm = rng.randint(1, 0xFFFFF)
        elif cls == "slli_x0_other":
            imm = rng.randint(0, 30)
        elif cls == "srli_x0":
            imm = rng.randint(0, 31)
        elif cls == "srai_x0_other":
            imm = rng.choice([s for s in range(32) if s != 7])
        elif cls in ("sll_x0", "srl_x0", "sra_x0"):
            b = rng.randint(0, 31) if rng.getrandbits(1) else b
        w = hint_would_be(cls, a, b, imm)
        if cls in ("canonical_nop", "slli_x0_semihost", "srai_x0_semihost") or w is None or w != 0:
            return rs1, rs2, imm, a, b
    raise AssertionError(f"no nonzero would-be result for hint class {cls}")


def hint_reader(rng, form, exclude):
    """Reader of x0 whose result depends on x0 being zero: (rd, s, S/imm, expected)."""
    rd = pick(rng, exclude)
    s = pick(rng, exclude + (rd,))
    if form == "addi_rs1z":
        imm = rng.choice([i for i in range(-2048, 2048) if i != 0])
        return {"form": form, "rd": rd, "s": 0, "val": imm, "expect": imm & M, "zero_side": "rs1"}
    val = rng.getrandbits(32) or 1
    if form == "sltu_rs1z":
        return {"form": form, "rd": rd, "s": s, "val": val, "expect": 1, "zero_side": "rs1"}
    side = "rs1" if form in ("add_rs1z", "or_rs1z") else "rs2"
    return {"form": form, "rd": rd, "s": s, "val": val, "expect": val, "zero_side": side}


def reader_text(r):
    f, rd, s = r["form"], r["rd"], r["s"]
    return {"add_rs1z": f"add x{rd}, x0, x{s}", "add_rs2z": f"add x{rd}, x{s}, x0", "addi_rs1z": f"addi x{rd}, x0, {r['val']}",
            "or_rs1z": f"or x{rd}, x0, x{s}", "xor_rs2z": f"xor x{rd}, x{s}, x0", "sub_rs2z": f"sub x{rd}, x{s}, x0",
            "sltu_rs1z": f"sltu x{rd}, x0, x{s}", "sll_rs2z": f"sll x{rd}, x{s}, x0"}[f]


def hint_pair_unit(rng, cls):
    rs1, rs2, imm, a, b = hint_draw(rng, cls, POOL)
    r = hint_reader(rng, rng.choice(HINT_READERS), (rs1, rs2))
    mid = [filler(rng).text for _ in range(rng.choice((0, 1, 2)))]
    return Op("hint_pair", I004, cls, 0, rs1, rs2, a, b, imm, tags={"hint": cls, "reader": r["form"], "dist": len(mid) + 1},
              reader=r, mid=mid)


def hint_block_unit(rng):
    hints = []
    for _ in range(HINT_BLOCK):
        cls = rng.choice(HINT_CLASSES)
        rs1, rs2, imm, _a, _b = hint_draw(rng, cls, POOL)
        hints.append((hint_text(cls, rs1, rs2, imm), cls))
    r = hint_reader(rng, rng.choice([f for f in HINT_READERS if f != "addi_rs1z"]), ())
    return Op("hint_block", I004, "block", tags={"reader": r["form"], "dist": 3, "last_hint": hints[-1][1]}, reader=r, hints=hints)


def build_hint_units(rng):
    ops = [hint_pair_unit(rng, c) for c in HINT_CLASSES]
    ops += [hint_pair_unit(rng, rng.choice(HINT_CLASSES)) for _ in range(rng.randint(4, 16))]
    ops += [hint_block_unit(rng) for _ in range(rng.randint(2, 3))]
    return ops


def u_unit(rng, item, op, imm, rd=None, align=-1):
    if rd is None:
        rd = 0 if rng.randrange(W4_RD_X0) == 0 else pick(rng)
    return Op("u", item, op, rd, 0, 0, 0, 0, imm, tags={"imm20": imm20_class(imm)}, align=align)


def build_u_units(rng):
    ops = []
    for op in ("lui", "auipc"):
        ops += [u_unit(rng, I005, op, imm20(rng, c), rd=pick(rng)) for c in IMM20_CLASSES]
        ops.append(u_unit(rng, I005, op, imm20(rng, "rand"), rd=0))
        for al in (0, 2):                    # one site per alignment pinned; the c.nop stream randomizes the rest
            ops.append(u_unit(rng, I005, op, imm20(rng, weighted(rng, IMM20_CLASSES)), rd=pick(rng), align=al))
        while sum(1 for o in ops if o.op == op) < N_U_MIN + rng.randint(0, 60):
            ops.append(u_unit(rng, I005, op, imm20(rng, weighted(rng, IMM20_CLASSES))))
    return ops


def build_u_ext_units(rng):
    """TP-ISA-006: lui extremes, auipc imm 0 (rd == pc), auipc carry-out wrap and no-wrap, each at both alignments."""
    ops = []
    for _ in range(rng.randint(1, 3)):
        ops.append(u_unit(rng, I006, "lui", 0xFFFFF, rd=pick(rng)))
        ops.append(u_unit(rng, I006, "lui", 0, rd=pick(rng)))
    for al in (0, 2):
        ops.append(u_unit(rng, I006, "auipc", 0, rd=pick(rng), align=al))
        ops.append(u_unit(rng, I006, "auipc", 0x80000 if al == 0 else rng.randint(0x80000, 0xFFFFF), rd=pick(rng), align=al))
        ops.append(u_unit(rng, I006, "auipc", rng.randint(1, 0x7FFFF), rd=pick(rng), align=al))
    for _ in range(rng.randint(2, 8)):
        ops.append(u_unit(rng, I006, "auipc", rng.choice((0, rng.randint(0x80000, 0xFFFFF), rng.randint(1, 0x7FFFF))), rd=pick(rng)))
    for o in ops:
        if o.op == "auipc":
            o.tags["wrap"] = o.imm >= 0x80000     # pc >= 0x80000000 in the program window: carry out iff imm20 bit 19
    return ops


def sign_pair(a, b):
    return ("n" if a & INT_MIN else "p") + ("n" if b & INT_MIN else "p")


def reg_unit(rng, op, rs1_cls=None, rs2_cls=None, rel=None, rd=None, a=None, b=None, equal=None):
    a = operand(rng, rs1_cls or weighted(rng, RS_CLASSES)) if a is None else a
    if equal is None:
        equal = rng.randrange(W4_EQ_OPERANDS) == 0
    b = a if equal else (operand(rng, rs2_cls or weighted(rng, RS_CLASSES)) if b is None else b)
    if rel is None:
        r = rng.randrange(16)
        rel = "all_same" if r == 0 else "rs1_eq_rs2" if r == 1 else "rs1_eq_rd" if r == 2 else "rs2_eq_rd" if r == 3 else "distinct"
    if rd is None:
        rd = 0 if rel in ("rs1_eq_rs2", "distinct") and rng.randrange(W4_RD_X0) == 0 else pick(rng)
    if rel in ("rs1_eq_rs2", "all_same"):
        b = a
    if rel == "all_same":
        rs1 = rs2 = rd
    elif rel == "rs1_eq_rs2":
        rs1 = rs2 = pick(rng, (rd,))
    elif rel == "rs1_eq_rd":
        rs1, rs2 = rd, pick(rng, (rd,))
    elif rel == "rs2_eq_rd":
        rs2, rs1 = rd, pick(rng, (rd,))
    else:
        rs1 = pick(rng, (rd,))
        rs2 = pick(rng, (rd, rs1))
    return Op("reg", I007, op, rd, rs1, rs2, a, b, 0,
              tags={"rs1_cls": rs_class(a), "rs2_cls": rs_class(b), "sign": sign_pair(a, b), "rel": rel, "eq": a == b})


def build_reg_units(rng):
    ops = []
    for op in REG_OPS:
        ops += [reg_unit(rng, op, rs1_cls=c, rel="distinct", rd=pick(rng), equal=False) for c in RS_CLASSES]
        ops += [reg_unit(rng, op, rs2_cls=c, rel="distinct", rd=pick(rng), equal=False) for c in RS_CLASSES]
        for sp in SIGN_PAIRS:
            ops.append(reg_unit(rng, op, rs1_cls="pos_rand" if sp[0] == "p" else "neg_rand",
                                rs2_cls="pos_rand" if sp[1] == "p" else "neg_rand", rel="distinct", rd=pick(rng), equal=False))
        ops += [reg_unit(rng, op, rel=r, rd=pick(rng)) for r in REL_CLASSES]
        ops.append(reg_unit(rng, op, rel="distinct", rd=pick(rng), equal=True))
        ops.append(reg_unit(rng, op, rel="distinct", rd=0))
    # result classes (CG-ISA-002 cp_result_class): one recipe each
    ops.append(reg_unit(rng, "and", rel="distinct", rd=pick(rng), a=0, equal=False))                 # zero
    ops.append(reg_unit(rng, "or", rel="distinct", rd=pick(rng), a=M, equal=False))                  # all_ones
    ops.append(reg_unit(rng, "add", rel="distinct", rd=pick(rng), a=INT_MIN, b=0, equal=False))      # int_min
    ops.append(reg_unit(rng, "add", rel="distinct", rd=pick(rng), a=INT_MAX, b=0, equal=False))      # int_max
    ops.append(reg_unit(rng, "sltu", rel="distinct", rd=pick(rng), a=0, b=1, equal=False))           # one
    while len(ops) < N_REG_MIN + rng.randint(0, 300):
        ops.append(reg_unit(rng, rng.choice(REG_OPS)))
    return ops


def wrap_kinds(op, a, b):
    """CG-ISA-002 cp_wrap facts of an add/sub operand pair (two negatives always carry out, so a set)."""
    k = set()
    if op == "add":
        r = (a + b) & M
        if a + b > M:
            k.add("add_carry")
        if s32(a) >= 0 and s32(b) >= 0 and s32(r) < 0:
            k.add("add_pos_ovf")
        if s32(a) < 0 and s32(b) < 0 and s32(r) >= 0:
            k.add("add_neg_ovf")
    else:
        if a < b:
            k.add("sub_borrow")
        if a == INT_MIN and s32(b) > 0:
            k.add("sub_ovf")
    return frozenset(k) or frozenset({"none"})


def wrap_unit(rng, op, a, b):
    rd = pick(rng)
    rs1 = pick(rng, (rd,))
    return Op("reg", I008, op, rd, rs1, pick(rng, (rd, rs1)), a, b, 0, tags={"wrap": wrap_kinds(op, a, b), "sign": sign_pair(a, b)})


def build_wrap_units(rng):
    table = (("add", M, 1), ("add", INT_MAX, INT_MAX), ("add", INT_MIN, INT_MIN), ("sub", 0, 1), ("sub", INT_MIN, 1),
             ("sub", INT_MIN, INT_MAX))
    ops = [wrap_unit(rng, *row) for row in table]
    for _ in range(rng.randint(40, 80)):
        cls = weighted(rng, {"table": 40, "window": 30, "rand": 30})
        if cls == "table":
            ops.append(wrap_unit(rng, *rng.choice(table)))
        elif cls == "window":
            w = rng.choice(("carry", "pos", "neg", "borrow", "sub_ovf"))
            if w == "carry":
                ops.append(wrap_unit(rng, "add", rng.randint(M - 0x7FF, M), rng.randint(0x800, 0xFFFF)))
            elif w == "pos":
                ops.append(wrap_unit(rng, "add", rng.randint(INT_MAX - 0x7FF, INT_MAX), rng.randint(0x800, 0xFFFF)))
            elif w == "neg":
                ops.append(wrap_unit(rng, "add", rng.randint(INT_MIN, INT_MIN + 0x7FF), rng.randint(INT_MIN, INT_MIN + 0x7FF)))
            elif w == "borrow":
                ops.append(wrap_unit(rng, "sub", rng.randint(0, 0x7FF), rng.randint(0x800, 0xFFFF)))
            else:
                ops.append(wrap_unit(rng, "sub", INT_MIN, rng.randint(1, 0x7FF)))
        else:
            ops.append(wrap_unit(rng, rng.choice(("add", "sub")), operand(rng, weighted(rng, RS_CLASSES)), operand(rng, weighted(rng, RS_CLASSES))))
    return ops


def slt_r_unit(rng, op, a, b, rs1_x0=False):
    rd = pick(rng)
    rs1 = 0 if rs1_x0 else pick(rng, (rd,))
    rs2 = pick(rng, (rd, rs1))
    a = 0 if rs1_x0 else a
    case = "rs1_x0" if rs1_x0 else "eq" if a == b else "intmin_intmax" if (a, b) == (INT_MIN, INT_MAX) else "intmin_1" if (a, b) == (INT_MIN, 1) else "other"
    return Op("slt_r", I009, op, rd, rs1, rs2, a, b, 0, tags={"case": case, "b_zero": b == 0, "sign": sign_pair(a, b)})


def build_slt_r_units(rng):
    ops = []
    for op in ("slt", "sltu"):
        v = operand(rng, weighted(rng, RS_CLASSES))
        ops += [slt_r_unit(rng, op, v, v), slt_r_unit(rng, op, M, M), slt_r_unit(rng, op, INT_MIN, INT_MAX),
                slt_r_unit(rng, op, INT_MIN, 1), slt_r_unit(rng, op, 0, 0, rs1_x0=True),
                slt_r_unit(rng, op, 0, rng.getrandbits(32) | 1, rs1_x0=True)]
    n = rng.randint(40, 80)
    for _ in range(n):
        op = rng.choice(("slt", "sltu"))
        if rng.getrandbits(1):
            row = rng.choice(("eq", "intmin_intmax", "intmin_1", "x0", "ones"))
            if row == "eq":
                v = operand(rng, weighted(rng, RS_CLASSES))
                ops.append(slt_r_unit(rng, op, v, v))
            elif row == "intmin_intmax":
                ops.append(slt_r_unit(rng, op, INT_MIN, INT_MAX))
            elif row == "intmin_1":
                ops.append(slt_r_unit(rng, op, INT_MIN, 1))
            elif row == "x0":
                ops.append(slt_r_unit(rng, op, 0, rng.choice((0, rng.getrandbits(32) | 1)), rs1_x0=True))
            else:
                ops.append(slt_r_unit(rng, op, M, M))
        else:
            ops.append(slt_r_unit(rng, op, operand(rng, weighted(rng, RS_CLASSES)), operand(rng, weighted(rng, RS_CLASSES))))
    return ops


def writer_would_be(op, cls, a, b, imm):
    """Value an x0 writer of TP-ISA-052 would write (None when pc- or CSR-dependent)."""
    if cls == "alu_imm":
        return alu_i(op, a, imm)
    if cls == "shift":
        return shift(op, a, imm)
    if cls == "alu_reg":
        return alu_r(op, a, b)
    if cls == "lui_auipc":
        return u_value("lui", imm, 0) if op == "lui" else None
    if cls in ("mul", "mulh"):
        return mul_op(op, a, b)
    if cls == "div_rem":
        return div_op(op, a, b)
    if cls == "bit_1cyc":
        return bit_op(op, a, b)
    if cls == "bit_2cyc":
        return bit_op(op, a, imm if op == "rori" else b)
    if cls == "cmp_hint":
        return {"c.li": sext(imm, 6) & M, "c.lui": (sext(imm, 6) << 12) & M, "c.slli": 0, "c.mv": b, "c.add": b}[op]
    return None


def x0w_unit(rng, cls, scratch_next):
    """One TP-ISA-052 unit: an x0 writer of the class (nonzero would-be result), 0..2 fillers, an x0 reader."""
    rs1, rs2 = pick(rng), 0
    rs2 = pick(rng, (rs1,))
    for _ in range(64):
        a, b, imm, op = operand(rng, weighted(rng, RS_CLASSES)), operand(rng, weighted(rng, RS_CLASSES)), 0, ""
        if cls == "alu_imm":
            op, imm = rng.choice(IMM_OPS), imm12(rng, weighted(rng, IMM_CLASSES))
        elif cls == "shift":
            op, imm = rng.choice(SHIFT_I), rng.randint(0, 31)
        elif cls == "alu_reg":
            op = rng.choice(REG_OPS)
        elif cls == "lui_auipc":
            op, imm = rng.choice(("lui", "auipc")), rng.randint(1, 0xFFFFF)
        elif cls == "load":
            op = "lw"
        elif cls == "csrr":
            op = rng.choice(("misa", "mscratch"))
            a = a or 1                                         # mscratch is written with a first
        elif cls in ("jal", "jalr"):
            op = cls
        elif cls == "mul":
            op = "mul"
        elif cls == "mulh":
            op = rng.choice(MULH_OPS)
        elif cls == "div_rem":
            op, b = rng.choice(DIV_OPS), b or 3
        elif cls == "bit_1cyc":
            op = rng.choice(BIT1_R)
        elif cls == "bit_2cyc":
            op = rng.choice(BIT2_R + ("rori",))
            imm = rng.randint(1, 31)
            b = rng.randint(1, 31) if rng.getrandbits(1) else b
        elif cls == "cmp_hint":
            op = rng.choice(CMP_HINTS)
            imm = rng.choice([i for i in range(64) if i not in (0, 32)]) if op == "c.li" else rng.randint(1, 31)
            b = b or 1
        w = writer_would_be(op, cls, a, b, imm)
        if w is None or w != 0 or op == "c.slli":
            break
    else:
        raise AssertionError(f"no nonzero would-be result for writer class {cls}")
    form = rng.choice(X0_READERS)
    rd = pick(rng, (rs1, rs2))
    good = rng.choice([v for v in range(-2048, 2048) if v != 0])
    bad = rng.choice([v for v in range(-2048, 2048) if v not in (0, good)])
    words = ()
    if cls == "load":
        words += (next(scratch_next),)
    if form == "sw_x0":
        words += (next(scratch_next),)
    reader = {"form": form, "rd": rd, "good": good, "bad": bad, "expect": 0 if form != "beq_x0" else good & M}
    mid = [filler(rng).text for _ in range(rng.choice((0, 1)) if form == "beq_x0" else rng.choice((0, 1, 2)))]
    return Op("x0w", I052, op, 0, rs1, rs2, a, b, imm, tags={"writer": cls, "reader": form, "dist": len(mid) + (2 if form == "beq_x0" else 1)},
              reader=reader, mid=mid, words=words)


def build_x0w_units(rng, scratch_next):
    ops = [x0w_unit(rng, c, scratch_next) for c in WRITER_CLASSES]
    ops += [x0w_unit(rng, rng.choice(WRITER_CLASSES), scratch_next) for _ in range(rng.randint(4, 12))]
    return ops


def filler(rng):
    t = rng.choice(FILLER_TEMPLATES)
    return Op("filler", text=t.format(imm12=rng.randint(-2048, 2047), sh=rng.randint(0, 31), imm20=rng.randint(0, 0xFFFFF)))


# ---- values, reports, red fixture ------------------------------------------------------------------------------------
def unit_value(o, dev=None, pc=0):
    """Report value(s) of one unit from its intent fields, or under the red override `dev` (the self-check; pc is a
    placeholder for auipc, whose deviations are pc-independent). Returns a list (hint blocks report two words)."""
    d = dev or {}
    op = d.get("op", o.op)
    imm = d.get("imm", o.imm)
    if o.kind in ("imm", "slt_i"):
        return [alu_i(op, o.a, imm)] if o.rd else []
    if o.kind in ("reg", "slt_r"):
        return [alu_r(op, o.a, o.b)] if o.rd else []
    if o.kind == "u":
        return [u_value(op, imm, pc)] if o.rd else []
    if o.kind == "hint_pair":
        if "hint_rd" in d:                               # the hint wrote the reader's source register
            w = hint_would_be(o.op, o.a, o.b, o.imm)
            return [int(w != 0) if o.reader["form"] == "sltu_rs1z" else w]
        return [o.reader["expect"]]
    if o.kind == "hint_block":
        return [o.reader["expect"], None if "delta_op" in d else HINT_BLOCK_DELTA]
    if o.kind == "x0w":
        if "reader_dev" in d:
            return [o.reader["bad"] & M if o.reader["form"] == "beq_x0" else o.a]
        return [o.reader["expect"]]
    if o.kind == "pre":
        return [o.a]
    return []


def red_candidates(rng, ops, item):
    """(unit, override) of every one-field deviation of the item, seed-shuffled; each changes only that unit's words."""
    c = []
    for o in ops:
        if o.item != item or not o.rd and o.kind in ("imm", "slt_i", "reg", "slt_r", "u"):
            continue
        if item == I001:
            c += [(o, {"op": alt}) for alt in IMM_OPS if alt != o.op]
        elif item == I002:
            if o.tags["wrap"] != "none":
                c.append((o, {"imm": 0}))
        elif item == I003:
            c.append((o, {"op": "sltiu" if o.op == "slti" else "slti"}))
        elif item == I004:
            if o.kind == "hint_pair" and o.op != "auipc_x0" and o.reader["s"]:
                c.append((o, {"hint_rd": o.reader["s"]}))
            elif o.kind == "hint_block":
                c.append((o, {"delta_op": "add"}))
        elif item == I005:
            c += [(o, {"imm": o.imm ^ 1}), (o, {"op": "auipc" if o.op == "lui" else "lui"})]
        elif item == I006:
            if o.op == "lui":
                c.append((o, {"imm": o.imm ^ 0x80000}))
            else:
                c.append((o, {"imm": (o.imm ^ 0x80000) if o.imm else 1}))
        elif item == I007:
            c += [(o, {"op": alt}) for alt in REG_OPS if alt != o.op]
        elif item == I008:
            c.append((o, {"op": "sub" if o.op == "add" else "add"}))
        elif item == I009:
            c.append((o, {"op": "sltu" if o.op == "slt" else "slt"}))
        elif item == I052:
            c.append((o, {"reader_dev": True}))
    rng.shuffle(c)
    return c


def apply_red(rng, ops, item, pc_of):
    """The first candidate whose emitted words differ from the expectation on that unit (proved on the models)."""
    for o, dev in red_candidates(rng, ops, item):
        pc = pc_of(o)
        if unit_value(o, dev, pc) != unit_value(o, None, pc):
            o.red = dev
            what = o.op if o.kind != "hint_pair" else o.tags["hint"]
            return f"{item}: {o.kind} {what} at report idx {o.ridx} emitted with {dev}"
    raise AssertionError(f"no deviation of {item} changes one of its report words for this seed")


def make_reports(ops):
    reports, items = [], {i: [] for i in RED_ITEMS}

    def add(o, item, expect, text, kind="value"):
        r = Report(len(reports), item, expect, text, kind, o.label, o.imm, n)
        reports.append(r)
        items[item].append(r.idx)
        o.ridx.append(r.idx)

    for n, o in enumerate(ops):
        if o.kind in ("imm", "slt_i") and o.rd:
            add(o, o.item, alu_i(o.op, o.a, o.imm), f"{o.op} x{o.rd}, x{o.rs1}, {o.imm} rs1=0x{o.a:08x}")
        elif o.kind in ("reg", "slt_r") and o.rd:
            add(o, o.item, alu_r(o.op, o.a, o.b), f"{o.op} x{o.rd}, x{o.rs1}, x{o.rs2} 0x{o.a:08x}, 0x{o.b:08x}")
        elif o.kind == "u" and o.rd:
            if o.op == "lui":
                add(o, o.item, u_value("lui", o.imm, 0), f"lui x{o.rd}, 0x{o.imm:05x} at {o.label}")
            else:
                add(o, o.item, None, f"auipc x{o.rd}, 0x{o.imm:05x} at {o.label}", "auipc")
        elif o.kind == "hint_pair":
            add(o, I004, o.reader["expect"], f"hint {o.op} then {o.reader['form']} reader x{o.reader['rd']} at distance {o.tags['dist']}")
        elif o.kind == "hint_block":
            add(o, I004, o.reader["expect"], f"block tail {o.reader['form']} reader x{o.reader['rd']} after {o.tags['last_hint']}")
            add(o, I004, HINT_BLOCK_DELTA, f"minstret delta over {HINT_BLOCK} hints")
        elif o.kind == "x0w":
            add(o, I052, o.reader["expect"], f"{o.tags['writer']} {o.op} x0 then {o.reader['form']} reader x{o.reader['rd']}")
        elif o.kind == "pre":
            add(o, I004, o.a, o.text)
    return reports, items


# ---- rendering (with the byte-exact layout model of .option norvc) ----------------------------------------------------
class Body:
    def __init__(self):
        self.lines, self.off, self.insns = [], 0, 0

    def add(self, text, nbytes=4, ninsn=1):
        self.lines.append(text)
        self.off += nbytes
        self.insns += ninsn

    def li(self, rd, v, retired=True):
        """retired=False: the li sits behind a taken beq and never retires (bytes count, retirements do not)."""
        n = li_len(v)
        self.add(f"li x{rd}, 0x{v & M:08x}", n, n // 4 if retired else 0)

    def la(self, rd, sym):
        self.add(f"la x{rd}, {sym}", 8, 2)

    def cnop(self):
        self.add(CNOP, 2, 1)

    def label(self, name, public=False):
        if public:
            self.lines.append(f".globl {name}")
        self.lines.append(f"{name}:")

    def report(self, rd):
        self.add(f"sw x{rd}, 0(x{EOT_REG})")


def render(ops, filler_init):
    """The .text lines after _start with every unit's modeled offset and the count of instructions that retire; the red
    override of a unit changes one field."""
    B = Body()
    n = li_len(MEMORY_MAP["eot_addr"])                    # the symbol is the rendered address (gen_mmio_map.h)
    B.add(f"li x{EOT_REG}, GEN_MM_EOT_ADDR", n, n // 4)
    B.la(BASE_REG, SCRATCH)
    for r, v in zip(FILLER_REGS, filler_init):
        B.li(r, v)
    B.add(f"csrw {csr_hex('mcountinhibit')}, x0")        # TP-ISA-004 precondition: minstret counts
    sites, jn = {}, 0
    for o in ops:
        d = o.red
        if o.kind == "filler":
            B.add(o.text)
        elif o.kind == "cnop":
            B.cnop()
        elif o.kind == "pre":
            B.add(f"csrr x{o.rd}, {csr_hex(o.op)}")
            B.report(o.rd)
        elif o.kind in ("imm", "slt_i"):
            B.li(o.rs1, o.a)
            B.add(f"{d.get('op', o.op)} x{o.rd}, x{o.rs1}, {d.get('imm', o.imm)}")
            if o.rd:
                B.report(o.rd)
        elif o.kind in ("reg", "slt_r"):
            if o.rs1:
                B.li(o.rs1, o.a)
            if o.rs2 != o.rs1:
                B.li(o.rs2, o.b)
            B.add(f"{d.get('op', o.op)} x{o.rd}, x{o.rs1}, x{o.rs2}")
            if o.rd:
                B.report(o.rd)
        elif o.kind == "u":
            if o.align >= 0 and (B.off & 2) != o.align:
                B.cnop()
            o.off = B.off
            sites[o.label] = B.off
            B.label(o.label, public=True)
            B.add(f"{d.get('op', o.op)} x{o.rd}, 0x{d.get('imm', o.imm):x}")
            if o.rd:
                B.report(o.rd)
        elif o.kind == "hint_pair":
            B.li(o.rs1, o.a)
            if o.rs2 != o.rs1:
                B.li(o.rs2, o.b)
            r = o.reader
            if r["s"]:
                B.li(r["s"], r["val"])
            t = hint_text(o.op, o.rs1, o.rs2, o.imm)
            if "hint_rd" in d:
                t = t.replace(" x0,", f" x{d['hint_rd']},", 1)
            B.add(t)
            for f in o.mid:
                B.add(f)
            B.add(reader_text(r))
            B.report(r["rd"])
        elif o.kind == "hint_block":
            r = o.reader
            B.li(r["s"], r["val"])
            B.add(f"csrr x{CTR_A}, {csr_hex('minstret')}")
            for t, _cls in o.hints:
                B.add(t)
            B.add(f"csrr x{CTR_B}, {csr_hex('minstret')}")
            B.add(f"{d.get('delta_op', 'sub')} x{CTR_B}, x{CTR_B}, x{CTR_A}")
            B.add(reader_text(r))
            B.report(r["rd"])
            B.report(CTR_B)
        elif o.kind == "x0w":
            B.li(o.rs1, o.a)
            cls, r = o.tags["writer"], o.reader
            if cls in ("alu_reg", "mul", "mulh", "div_rem", "bit_1cyc", "bit_2cyc", "cmp_hint"):
                B.li(o.rs2, o.b)
            if cls == "alu_imm" or cls == "shift":
                B.add(f"{o.op} x0, x{o.rs1}, {o.imm}")
            elif cls in ("alu_reg", "mul", "mulh", "div_rem", "bit_1cyc"):
                B.add(f"{o.op} x0, x{o.rs1}, x{o.rs2}")
            elif cls == "bit_2cyc":
                B.add(f"rori x0, x{o.rs1}, {o.imm}" if o.op == "rori" else f"{o.op} x0, x{o.rs1}, x{o.rs2}")
            elif cls == "lui_auipc":
                B.add(f"{o.op} x0, 0x{o.imm:x}")
            elif cls == "load":
                B.add(f"lw x0, {o.words[0]}(x{BASE_REG})")
            elif cls == "csrr":
                if o.op == "mscratch":
                    B.add(f"csrw {csr_hex('mscratch')}, x{o.rs1}")
                B.add(f"csrr x0, {csr_hex(o.op)}")
            elif cls == "jal":
                jn += 1
                B.add(f"jal x0, gen_j{jn}")
                B.label(f"gen_j{jn}")
            elif cls == "jalr":
                jn += 1
                B.la(SPARE, f"gen_j{jn}")
                B.add(f"jalr x0, 0(x{SPARE})")
                B.label(f"gen_j{jn}")
            elif cls == "cmp_hint":
                B.lines.append(".option push")
                B.lines.append(".option rvc")
                arg = f"x{o.rs2}" if o.op in ("c.mv", "c.add") else str(sext(o.imm, 6)) if o.op in ("c.li", "c.lui") else str(o.imm)
                B.add(f"{o.op} x0, {arg}", 2, 1)
                B.lines.append(".option pop")
            for f in o.mid:
                B.add(f)
            src = f"x{o.rs1}" if "reader_dev" in d else "x0"
            if r["form"] == "add_x0_x0":
                B.add(f"add x{r['rd']}, x0, {src}")
            elif r["form"] == "sw_x0":
                w = o.words[-1]
                B.add(f"sw {src}, {w}(x{BASE_REG})")
                B.add(f"lw x{r['rd']}, {w}(x{BASE_REG})")
            else:
                jn += 1
                B.li(r["rd"], r["good"])
                B.add(f"{'bne' if 'reader_dev' in d else 'beq'} x0, x0, gen_j{jn}")
                B.li(r["rd"], r["bad"], retired=False)
                B.label(f"gen_j{jn}")
            B.report(r["rd"])
    return B.lines, sites, B.insns


def check_coverage(p):
    """The plan carries what the items ask for; a generator drift fails here, not silently in a run."""
    ops = p.ops
    obs = [o for o in ops if o.ridx]
    imm = [o for o in ops if o.item == I001]
    assert len(imm) >= N_IMM_MIN, f"TP-ISA-001: {len(imm)} I-type ops < {N_IMM_MIN}"
    for op in IMM_OPS:
        got = {o.tags["rs1_cls"] for o in imm if o.op == op and o.rd}
        assert got == set(RS_CLASSES), f"TP-ISA-001 {op}: rs1 classes missing {set(RS_CLASSES) - got}"
        got = {o.tags["imm_cls"] for o in imm if o.op == op and o.rd}
        assert got == set(IMM_CLASSES), f"TP-ISA-001 {op}: imm classes missing {set(IMM_CLASSES) - got}"
        assert any(o.rd == 0 for o in imm if o.op == op) and {o.tags["rs1_eq_rd"] for o in imm if o.op == op and o.rd} == {True, False}
    assert {result_class(alu_i(o.op, o.a, o.imm)) for o in imm if o.rd} >= set(RESULT_CLASSES), "TP-ISA-001 result classes"
    wr = [o for o in ops if o.item == I002]
    assert {o.tags["wrap"] for o in wr} >= {"pos", "neg"} and any((o.a, o.imm) == (INT_MAX, 1) for o in wr) and any((o.a, o.imm) == (INT_MIN, -1) for o in wr)
    cases = {o.tags["case"] for o in ops if o.item == I003}
    assert cases >= {"eq", "slti_intmin_0", "slti_0_neg", "sltiu_imm_m1", "sltiu_seqz", "sltiu_ones_m1"}, f"TP-ISA-003 cases {cases}"
    assert {o.op for o in ops if o.item == I003 and o.tags["case"] == "eq"} == {"slti", "sltiu"}
    pairs = [o for o in ops if o.kind == "hint_pair"]
    assert {o.op for o in pairs} == set(HINT_CLASSES), "TP-ISA-004 hint classes"
    assert {o.reader["zero_side"] for o in pairs} == {"rs1", "rs2"} and {o.tags["dist"] for o in pairs} == {1, 2, 3}
    assert sum(1 for o in ops if o.kind == "hint_block") >= 2 and all(len(o.hints) == HINT_BLOCK for o in ops if o.kind == "hint_block")
    for op in ("lui", "auipc"):
        us = [o for o in ops if o.item == I005 and o.op == op]
        assert len(us) >= N_U_MIN and {o.tags["imm20"] for o in us if o.rd} == set(IMM20_CLASSES) and any(o.rd == 0 for o in us)
        assert {o.off & 2 for o in us if o.rd} == {0, 2}, f"TP-ISA-005 {op}: one pc alignment only"
    ext = [o for o in ops if o.item == I006]
    assert {o.imm for o in ext if o.op == "lui"} >= {0xFFFFF, 0}
    combos = {(o.off & 2, o.tags["wrap"]) for o in ext if o.op == "auipc" and o.imm}
    assert combos == {(0, True), (2, True), (0, False), (2, False)}, f"TP-ISA-006 auipc alignment x wrap {combos}"
    assert {o.off & 2 for o in ext if o.op == "auipc" and o.imm == 0} == {0, 2}
    reg = [o for o in ops if o.item == I007]
    assert len(reg) >= N_REG_MIN
    for op in REG_OPS:
        r = [o for o in reg if o.op == op and o.rd]
        assert {o.tags["rs1_cls"] for o in r} == set(RS_CLASSES) and {o.tags["rs2_cls"] for o in r} == set(RS_CLASSES), f"TP-ISA-007 {op} classes"
        assert {o.tags["sign"] for o in r} == set(SIGN_PAIRS) and {o.tags["rel"] for o in r} == set(REL_CLASSES), f"TP-ISA-007 {op} sign/rel"
        assert {o.tags["eq"] for o in r} == {True, False} and any(o.rd == 0 for o in reg if o.op == op)
    assert {result_class(alu_r(o.op, o.a, o.b)) for o in reg if o.rd} >= set(RESULT_CLASSES), "TP-ISA-007 result classes"
    kinds = set().union(*(o.tags["wrap"] for o in ops if o.item == I008))
    assert kinds >= {"add_carry", "add_pos_ovf", "add_neg_ovf", "sub_borrow", "sub_ovf"}, f"TP-ISA-008 {kinds}"
    for op in ("slt", "sltu"):
        cs = {o.tags["case"] for o in ops if o.item == I009 and o.op == op}
        assert cs >= {"eq", "intmin_intmax", "intmin_1", "rs1_x0"}, f"TP-ISA-009 {op} {cs}"
        assert {o.tags["b_zero"] for o in ops if o.item == I009 and o.op == op and o.tags["case"] == "rs1_x0"} == {True, False}
    x0w = [o for o in ops if o.kind == "x0w"]
    assert {o.tags["writer"] for o in x0w} == set(WRITER_CLASSES) and {o.tags["reader"] for o in x0w} == set(X0_READERS)
    assert all(1 <= o.tags["dist"] <= 3 for o in x0w) and len({w for o in x0w for w in o.words}) == sum(len(o.words) for o in x0w)
    assert all(0 <= w < 4 * SCRATCH_WORDS for o in x0w for w in o.words) and all(p.scratch_init[w // 4] for o in x0w for w in o.words)
    assert p.k == len(p.reports) == sum(len(v) for v in p.items.values()) == sum(len(o.ridx) for o in obs)
    assert all(0 <= ord(c) < 128 for c in emit(p)), "non-ASCII in the emitted program"


def red_item_of(seed, red_item):
    if red_item is None:
        return random.Random(f"{int(seed)}:{RED_TAG}").choice(RED_ITEMS)
    if red_item not in RED_ITEMS:
        raise ValueError(f"unknown red item {red_item}; one of {RED_ITEMS}")
    return red_item


def plan(seed, red=False, red_item=None):
    rng = random.Random(f"{int(seed)}:{RNG_TAG}")
    scratch_init = [rng.getrandbits(32) | 1 for _ in range(SCRATCH_WORDS)]
    filler_init = tuple(rng.getrandbits(32) for _ in FILLER_REGS)
    word_order = list(range(0, 4 * SCRATCH_WORDS, 4))
    rng.shuffle(word_order)
    scratch_next = iter(word_order)
    # TP-ISA-004 precondition: mcountinhibit written 0 and read back (dummy_instr_en = 0 is the cpuctrlsts reset value; the
    # standalone Spike check has no cpuctrlsts, so it is not read here)
    pre = [Op("pre", I004, "mcountinhibit", pick(rng), a=0, text="mcountinhibit read-back (written 0)")]
    units = ([[o] for o in build_imm_units(rng)] + [[o] for o in build_addi_wrap_units(rng)] + [[o] for o in build_slt_i_units(rng)]
             + [[o] for o in build_hint_units(rng)] + [[o] for o in build_u_units(rng)] + [[o] for o in build_u_ext_units(rng)]
             + [[o] for o in build_reg_units(rng)] + [[o] for o in build_wrap_units(rng)] + [[o] for o in build_slt_r_units(rng)]
             + [[o] for o in build_x0w_units(rng, scratch_next)])
    rng.shuffle(units)
    ops = list(pre)
    for unit in units:
        ops.extend(filler(rng) for _ in range(rng.choice((0, 0, 1, 1, 2))))
        if rng.randrange(6) == 0:
            ops.append(Op("cnop"))
        ops.extend(unit)
    n = 0
    for o in ops:
        if o.kind == "u":
            o.label = f"gen_u{n}"
            n += 1
    _lines, sites, _insns = render(ops, filler_init)             # layout: site offsets, alignments
    reports, items = make_reports(ops)
    red_item = red_item_of(seed, red_item) if red else ""
    base = MEMORY_MAP["boot_page"]
    red_note = apply_red(rng, ops, red_item, lambda o: base + o.off) if red else ""
    body, sites, insns = render(ops, filler_init)
    kinds = [o.kind for o in ops]
    summary = {"imm": kinds.count("imm"), "slt_i": kinds.count("slt_i"), "hint_pairs": kinds.count("hint_pair"),
               "hint_blocks": kinds.count("hint_block"), "u": kinds.count("u"), "reg": kinds.count("reg"),
               "slt_r": kinds.count("slt_r"), "x0w": kinds.count("x0w"), "fillers": kinds.count("filler"), "cnops": kinds.count("cnop"),
               "rd_x0_vacuous": sum(1 for o in ops if o.kind in ("imm", "slt_i", "reg", "slt_r", "u") and o.rd == 0),
               "degenerate": sum(1 for o in ops if degenerate(o)), "insns": insns}
    # Retirement floor at the end-of-test store: every instruction before the epilogue (in-order core, the store issues after
    # its elders retired); the boot stub and the epilogue's own li/la are the margin.
    p = Plan(int(seed), bool(red), ops, reports, len(reports), insns, items, scratch_init, filler_init, summary,
             red_item, red_note, body, sites)
    check_coverage(p)
    return p


def degenerate(o):
    """Operand pairs whose result cannot discriminate (and with 0, or with all ones); counted apart, still compared."""
    if o.kind in ("imm", "reg") and o.rd:
        if o.op in ("andi", "and"):
            return o.a == 0 or (o.imm == 0 if o.kind == "imm" else o.b == 0)
        if o.op in ("ori", "or"):
            return o.a == M or (o.imm == -1 if o.kind == "imm" else o.b == M)
    return False


def emit(p):
    L = [f"# gen_isa_alu_prog.py --seed {p.seed}{' --red --red-item ' + p.red_item if p.red else ''}: RV32I ALU program of gen_test_isa_alu",
         f"# k={p.k} report words (" + ", ".join(f"{i} {len(p.items[i])}" for i in RED_ITEMS) + f"), gen_min_retired={p.min_retired}"]
    if p.red:
        L.append(f"# RED FIXTURE {p.red_note}; the expectation keeps the true program, so the {p.red_item} fire-check must fail")
    L += [".option norvc", ".option norelax", '.include "gen_mmio_map.h"', "", ".section .text", ".globl _start", ".balign 4", "_start:"]
    L += ["  " + ln if not ln.endswith(":") and not ln.startswith(".globl") else ln for ln in p.body]
    L += [f"  li   gp, {TOHOST_PASS}", "  la   t5, tohost", "  sw   gp, 0(t5)", "1:", "  j    1b", "",
          ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
          ".align 4", f"{SCRATCH}:"]
    for i in range(0, SCRATCH_WORDS, 8):
        L.append("  .word " + ", ".join(f"0x{w:08x}" for w in p.scratch_init[i:i + 8]))
    L += [".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}", ""]
    return "\n".join(L)


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
        assert [r.expect for r in p.reports] == [r.expect for r in g.reports] and p.k == g.k and p.min_retired == g.min_retired \
            and p.sites == g.sites, "the red plan's expectations, k, min_retired or layout differ from the green plan"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(emit(p))
    print(f"OK seed={a.seed} red={red} out={a.out} k={p.k} min_retired={p.min_retired} {p.summary}"
          + (f" red_item={p.red_item} red_note={p.red_note!r}" if red else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
