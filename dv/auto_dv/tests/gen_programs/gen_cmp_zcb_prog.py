#!/usr/bin/env python3
"""gen_cmp_zcb_prog: per-seed program generator of gen_test_cmp_zcb (plan group gen_cmp_zcb:
TP-CMP-034 Zcb loads/stores, TP-CMP-036 Zcb ALU forms, TP-CMP-038 c.mul; dv/auto_dv/docs/gen_test_plan.md).

plan(seed, red=False) draws the scenario from random.Random(f"{seed}:program:cmp_zcb"): a shuffled
sequence of Zcb operations over x8..x15 (store-then-load pairs of the same location at every base
alignment and uimm, the five ALU forms over the TP-CMP-036 operand mix, c.mul over every rsd'/rs2'
with W7 operands), unrelated filler instructions between them, and the expected value of every
report word the program stores to GEN_MM_EOT_ADDR (the RAW observation: rd' after an ALU form or a
load, the memory word(s) after a store), computed here from the Zc specification semantics
(tools/specs/riscv-isa-manual/src/unpriv/zcb.adoc). red=True makes the PROGRAM deviate on one intent
(one ALU form is emitted as a different form whose result differs) while the expectation stays true.
emit(plan) renders the RV32IMC assembly (Zcb through the gen_zc_insn.h macros; gcc knows no Zcb).

CLI: python3 gen_cmp_zcb_prog.py --seed N --out <file.S> [--red]
"""
import argparse
import random
from dataclasses import dataclass, field
from pathlib import Path

RNG_TAG = "program:cmp_zcb"
MASK32 = 0xFFFFFFFF
CREGS = tuple(range(8, 16))       # the 3-bit compressed register fields (x8..x15)
EOT_REG = 28                      # holds GEN_MM_EOT_ADDR for every report store
ADDR_REG, DATA_REG = 29, 30       # word read-back after a Zcb store
FILLER_REGS = (5, 6, 7)           # the unrelated instructions between Zcb ops work on these
SCRATCH = "gen_scratch"
SCRATCH_BYTES = 64
REGION_STRIDE, REGIONS = 8, 6     # a store/load pair works in one region: base = 8*k + align (max ea 8*5+3+3 = 46)

ITEM_LS, ITEM_ALU, ITEM_MUL = "TP-CMP-034", "TP-CMP-036", "TP-CMP-038"
STORES = ("c_sb", "c_sh")
LOADS = ("c_lbu", "c_lhu", "c_lh")
ALU_FORMS = ("c_zext_b", "c_sext_b", "c_zext_h", "c_sext_h", "c_not")
# TP-CMP-036 operand classes (CG-CMP-005.cp_alu_operand) that every ALU form meets at least once.
ALU_MUST_CLASSES = ("bit7_set", "bit7_clear", "bit15_set", "zero", "all_ones", "rand")

# Layer-1 tables (gen_test_plan.md "Layer-1 weight tables"): W1 register operands with the TP-CMP-036
# mix as the group-specific extremes, W7 multiply operands (CG-MUL-001 extremes), W2 unsigned
# immediates, W4 register relations for the compressed fields (same register 1 in 8).
W1_ALU = {"zero": 1, "all_ones": 1, "int_min": 1, "int_max": 1, "one": 1, "byte_msb": 1, "half_msb": 1,
          "alt_5": 1, "alt_a": 1, "bit7_set": 1, "bit7_clear": 1, "bit15_set": 1, "pos_rand": 4, "neg_rand": 4}
W7_MUL = {"zero": 1, "one": 1, "all_ones": 1, "int_min": 1, "int_max": 1, "p16": 1, "two": 1, "pos_rand": 4, "neg_rand": 4}
W2_UIMM = {"zero": 1, "max": 1, "rand": 6}
W4_SAME_REG = 8
FILLER_TEMPLATES = ("addi x5, x5, {imm12}", "xori x6, x6, {imm12}", "slli x7, x7, {sh}", "add x5, x6, x7",
                    "sub x7, x5, x6", "lui x6, {imm20}", "andi x5, x5, {imm12}", "or x6, x6, x7", "nop")


def weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def sext(v, bits):
    return (v | (MASK32 & ~((1 << bits) - 1))) if (v >> (bits - 1)) & 1 else v


def operand(rng, cls):
    """A 32-bit operand of the named W1/W7 class."""
    fixed = {"zero": 0, "one": 1, "two": 2, "all_ones": MASK32, "int_min": 0x80000000, "int_max": 0x7FFFFFFF,
             "p16": 0x10000, "byte_msb": 0x80, "half_msb": 0x8000, "alt_5": 0x55555555, "alt_a": 0xAAAAAAAA}
    if cls in fixed:
        return fixed[cls]
    r = rng.getrandbits(32)
    if cls == "bit7_set":
        return (r | 0x80) & ~0x8000 & MASK32
    if cls == "bit7_clear":
        return r & ~0x8080 & MASK32
    if cls == "bit15_set":
        return r | 0x8000
    if cls == "pos_rand":
        return r & 0x7FFFFFFF
    if cls == "neg_rand":
        return r | 0x80000000
    if cls == "rand":
        return r
    raise ValueError(f"unknown operand class {cls}")


def alu(form, x):
    """Zc semantics of the Zcb ALU forms (zcb.adoc Operation lines)."""
    if form == "c_zext_b":
        return x & 0xFF
    if form == "c_sext_b":
        return sext(x & 0xFF, 8)
    if form == "c_zext_h":
        return x & 0xFFFF
    if form == "c_sext_h":
        return sext(x & 0xFFFF, 16)
    if form == "c_not":
        return (~x) & MASK32
    raise ValueError(f"unknown ALU form {form}")


def access_size(form):
    return 1 if form in ("c_sb", "c_lbu") else 2


def legal_uimm(form):
    return (0, 1, 2, 3) if access_size(form) == 1 else (0, 2)


def draw_uimm(rng, form):
    """W2 unsigned-immediate draw over the form's legal field values."""
    legal = legal_uimm(form)
    cls = weighted(rng, W2_UIMM)
    return {"zero": legal[0], "max": legal[-1]}.get(cls, rng.choice(legal))


@dataclass
class Report:
    idx: int
    item: str
    expect: int
    label: str


@dataclass
class Op:
    kind: str                 # store | load | alu | mul | filler
    form: str = ""            # the Zcb form (the intent; expectations follow it)
    rd: int = 0               # rd' (loads, ALU), rsd' (c.mul), rs2' (stores)
    rs1: int = 0              # rs1' base (loads/stores), rs2' (c.mul)
    uimm: int = 0             # byte offset field
    base_off: int = 0         # rs1' = gen_scratch + base_off
    value: int = 0            # store data / ALU operand / c.mul rsd' operand
    value2: int = 0           # c.mul rs2' operand
    emit_form: str = ""       # what the program emits; differs from form only in the red fixture
    text: str = ""            # filler instruction
    words: list = field(default_factory=list)      # scratch word offsets read back after a store
    reports: list = field(default_factory=list)


@dataclass
class Plan:
    seed: int
    red: bool
    ops: list
    reports: list
    k: int
    min_retired: int
    items: dict               # item id -> report indices in store order
    scratch_init: bytes
    filler_init: tuple        # initial values of FILLER_REGS
    summary: dict
    red_note: str


def load_op(rng, form, base_off, uimm):
    rs1 = rng.choice(CREGS)
    rd = rs1 if rng.randrange(W4_SAME_REG) == 0 else rng.choice([r for r in CREGS if r != rs1])
    return Op("load", form, rd=rd, rs1=rs1, uimm=uimm, base_off=base_off)


def ls_group(rng, store_form, align, uimm_s):
    """One TP-CMP-034 unit: a store, then a load of the same location with its own base/uimm split,
    sometimes a further load somewhere in the scratch buffer. rs2' != rs1' keeps the stored data
    independent of the link address so the expectation is known before linking."""
    size = access_size(store_form)
    base_s = REGION_STRIDE * rng.randrange(REGIONS) + align
    ea = base_s + uimm_s
    msb_bit = 7 if size == 1 else 15
    data = rng.getrandbits(32)
    data = (data | (1 << msb_bit)) if rng.getrandbits(1) else (data & ~(1 << msb_bit) & MASK32)
    rs1 = rng.choice(CREGS)
    rs2 = rng.choice([r for r in CREGS if r != rs1])
    ops = [Op("store", store_form, rd=rs2, rs1=rs1, uimm=uimm_s, base_off=base_s, value=data)]
    load_form = "c_lbu" if size == 1 else rng.choice(["c_lhu", "c_lh"])
    uimm_l = rng.choice([u for u in legal_uimm(load_form) if u <= ea])
    ops.append(load_op(rng, load_form, ea - uimm_l, uimm_l))
    if rng.getrandbits(1):
        form = rng.choice(LOADS)
        u = draw_uimm(rng, form)
        ops.append(load_op(rng, form, rng.randrange(0, SCRATCH_BYTES - u - access_size(form) + 1), u))
    return ops


def build_ls_units(rng):
    units = [ls_group(rng, f, a, u) for f in STORES for a in range(4) for u in legal_uimm(f)]
    for _ in range(rng.randint(2, 8)):
        f = rng.choice(STORES)
        units.append(ls_group(rng, f, rng.randrange(4), draw_uimm(rng, f)))
    halves = [u for u in units if u[0].form == "c_sh"]
    if len({(u[0].value >> 15) & 1 for u in halves}) < 2:     # both halfword msb states (2^-8 fix-up)
        halves[-1][0].value ^= 1 << 15
    if len({u[1].form for u in halves}) < 2:                  # both c.lhu and c.lh read a stored half back
        halves[-1][1].form = "c_lh" if halves[-1][1].form == "c_lhu" else "c_lhu"
    return units


def build_alu_units(rng):
    ops = [Op("alu", f, value=operand(rng, c)) for f in ALU_FORMS for c in ALU_MUST_CLASSES]
    ops += [Op("alu", rng.choice(ALU_FORMS), value=operand(rng, weighted(rng, W1_ALU))) for _ in range(rng.randint(0, 6))]
    rng.shuffle(ops)
    regs = list(CREGS)
    rng.shuffle(regs)
    for i, op in enumerate(ops):                              # every rd' at least once, the rest uniform
        op.rd = regs[i] if i < len(regs) else rng.choice(CREGS)
    return [[op] for op in ops]


def build_mul_units(rng):
    def mul(rd, rs2):
        a = operand(rng, weighted(rng, W7_MUL))
        b = a if rs2 == rd else operand(rng, weighted(rng, W7_MUL))
        return Op("mul", "c_mul", rd=rd, rs1=rs2, value=a, value2=b)
    ops = [mul(r, rng.choice([x for x in CREGS if x != r])) for r in CREGS]        # rsd' sweep
    ops += [mul(rng.choice([x for x in CREGS if x != r]), r) for r in CREGS]       # rs2' sweep
    ops += [mul(r, r) for r in rng.sample(CREGS, 2)]                               # rsd' == rs2'
    for _ in range(rng.randint(2, 8)):
        rd = rng.choice(CREGS)
        ops.append(mul(rd, rd if rng.randrange(W4_SAME_REG) == 0 else rng.choice([x for x in CREGS if x != rd])))
    return [[op] for op in ops]


def filler(rng):
    t = rng.choice(FILLER_TEMPLATES)
    return Op("filler", text=t.format(imm12=rng.randint(-2048, 2047), sh=rng.randint(0, 31), imm20=rng.randint(0, 0xFFFFF)))


def apply_red(rng, ops):
    """The red fixture: the first ALU op is emitted as another form whose result differs for its operand."""
    op = next(o for o in ops if o.kind == "alu")
    alts = [f for f in ALU_FORMS if f != op.form and alu(f, op.value) != alu(op.form, op.value)]
    op.emit_form = rng.choice(alts)
    return f"{op.form} x{op.rd} (operand 0x{op.value:08x}) emitted as {op.emit_form}"


def simulate(ops, scratch_init):
    """Walk the program order once: memory model of the scratch buffer, one Report per stored word."""
    mem = bytearray(scratch_init)
    reports = []
    items = {ITEM_LS: [], ITEM_ALU: [], ITEM_MUL: []}

    def report(item, expect, label):
        r = Report(len(reports), item, expect & MASK32, label)
        reports.append(r)
        items[item].append(r.idx)
        return r

    for op in ops:
        op.reports = []
        if op.kind == "store":
            size = access_size(op.form)
            ea = op.base_off + op.uimm
            for i in range(size):
                mem[ea + i] = (op.value >> (8 * i)) & 0xFF
            w0 = ea & ~3
            op.words = [w0] + ([w0 + 4] if ea + size - 1 >= w0 + 4 else [])
            for w in op.words:
                op.reports.append(report(ITEM_LS, int.from_bytes(mem[w:w + 4], "little"),
                                         f"{op.form} x{op.rd},{op.uimm}(x{op.rs1}) ea={ea} word={w}"))
        elif op.kind == "load":
            size = access_size(op.form)
            ea = op.base_off + op.uimm
            raw = int.from_bytes(mem[ea:ea + size], "little")
            v = sext(raw, 16) if op.form == "c_lh" else raw
            op.reports.append(report(ITEM_LS, v, f"{op.form} x{op.rd},{op.uimm}(x{op.rs1}) ea={ea}"))
        elif op.kind == "alu":
            op.reports.append(report(ITEM_ALU, alu(op.form, op.value), f"{op.form} x{op.rd} operand=0x{op.value:08x}"))
        elif op.kind == "mul":
            op.reports.append(report(ITEM_MUL, (op.value * op.value2) & MASK32,
                                     f"c_mul x{op.rd},x{op.rs1} 0x{op.value:08x}*0x{op.value2:08x}"))
    return reports, items


def body_lines(ops, filler_init):
    """The .text lines after _start (the scenario and its report stores)."""
    L = [f"  li   x{EOT_REG}, GEN_MM_EOT_ADDR"]
    L += [f"  li   x{r}, 0x{v:08x}" for r, v in zip(FILLER_REGS, filler_init)]
    for op in ops:
        if op.kind == "filler":
            L.append(f"  {op.text}")
            continue
        if op.kind in ("store", "load"):
            L.append(f"  la   x{op.rs1}, {SCRATCH}")
            if op.base_off:
                L.append(f"  addi x{op.rs1}, x{op.rs1}, {op.base_off}")
        if op.kind == "store":
            L.append(f"  li   x{op.rd}, 0x{op.value:08x}")
            L.append(f"  {op.emit_form} {op.rd}, {op.uimm}, {op.rs1}")
            L.append(f"  la   x{ADDR_REG}, {SCRATCH}")
            for w in op.words:
                L.append(f"  lw   x{DATA_REG}, {w}(x{ADDR_REG})")
                L.append(f"  sw   x{DATA_REG}, 0(x{EOT_REG})")
        elif op.kind == "load":
            L.append(f"  {op.emit_form} {op.rd}, {op.uimm}, {op.rs1}")
            L.append(f"  sw   x{op.rd}, 0(x{EOT_REG})")
        elif op.kind == "alu":
            L.append(f"  li   x{op.rd}, 0x{op.value:08x}")
            L.append(f"  {op.emit_form} {op.rd}")
            L.append(f"  sw   x{op.rd}, 0(x{EOT_REG})")
        elif op.kind == "mul":
            L.append(f"  li   x{op.rd}, 0x{op.value:08x}")
            if op.rs1 != op.rd:
                L.append(f"  li   x{op.rs1}, 0x{op.value2:08x}")
            L.append(f"  {op.emit_form} {op.rd}, {op.rs1}")
            L.append(f"  sw   x{op.rd}, 0(x{EOT_REG})")
    return L


def retire_floor(lines):
    """Honest lower bound of retirements at the end-of-test store: one per straight-line instruction
    (la = 2, li counted as 1), less a margin for the instructions still in the pipeline at the store."""
    n = sum(2 if ln.split()[0] == "la" else 1 for ln in lines)
    return max(n - 4, 1)


def check_coverage(p):
    """The plan carries what the items ask for; a generator drift fails here, not silently in a run."""
    stores = [o for o in p.ops if o.kind == "store"]
    loads = [o for o in p.ops if o.kind == "load"]
    combos = {(o.form, o.base_off & 3, o.uimm) for o in stores}
    want = {(f, a, u) for f in STORES for a in range(4) for u in legal_uimm(f)}
    assert want <= combos, f"store form x alignment x uimm not covered: {sorted(want - combos)}"
    assert {(o.form, o.uimm) for o in loads} >= {(f, u) for f in LOADS for u in legal_uimm(f)}, "load form x uimm not covered"
    for f in STORES:
        bit = 7 if f == "c_sb" else 15
        assert len({(o.value >> bit) & 1 for o in stores if o.form == f}) == 2, f"{f}: one msb state only"
    alus = [o for o in p.ops if o.kind == "alu"]
    assert {o.form for o in alus} == set(ALU_FORMS) and {o.rd for o in alus} == set(CREGS), "ALU forms / rd' sweep"
    muls = [o for o in p.ops if o.kind == "mul"]
    assert {o.rd for o in muls} == set(CREGS) and {o.rs1 for o in muls} == set(CREGS), "c.mul rsd'/rs2' sweep"
    assert sum(1 for o in muls if o.rd == o.rs1) >= 2, "c.mul same-register class"
    for o in stores + loads:
        assert 0 <= o.base_off + o.uimm + access_size(o.form) <= SCRATCH_BYTES, f"access outside the scratch buffer: {o}"
    assert p.k == len(p.reports) and sum(len(v) for v in p.items.values()) == p.k
    assert all(0 <= ord(c) < 128 for c in emit(p)), "non-ASCII in the emitted program"


def plan(seed, red=False):
    rng = random.Random(f"{int(seed)}:{RNG_TAG}")
    scratch_init = bytes(rng.getrandbits(8) for _ in range(SCRATCH_BYTES))
    filler_init = tuple(rng.getrandbits(32) for _ in FILLER_REGS)
    units = build_ls_units(rng) + build_alu_units(rng) + build_mul_units(rng)
    rng.shuffle(units)
    ops = []
    for unit in units:
        for op in unit:
            ops.extend(filler(rng) for _ in range(rng.choice((0, 0, 1, 1, 2))))
            ops.append(op)
    for op in ops:
        op.emit_form = op.form
    red_note = apply_red(rng, ops) if red else ""
    reports, items = simulate(ops, scratch_init)
    kinds = [o.kind for o in ops]
    summary = {"ls_groups": len([u for u in units if u[0].kind == "store"]), "stores": kinds.count("store"),
               "loads": kinds.count("load"), "alu": kinds.count("alu"), "mul": kinds.count("mul"),
               "fillers": kinds.count("filler")}
    for f in STORES + LOADS + ALU_FORMS:
        summary[f] = sum(1 for o in ops if o.form == f)
    summary["c_mul_same"] = sum(1 for o in ops if o.kind == "mul" and o.rd == o.rs1)
    summary["sh_split"] = sum(1 for o in ops if o.form == "c_sh" and len(o.words) == 2)
    p = Plan(int(seed), bool(red), ops, reports, len(reports), retire_floor(body_lines(ops, filler_init)), items,
             scratch_init, filler_init, summary, red_note)
    check_coverage(p)
    return p


def emit(p):
    L = [f"# gen_cmp_zcb_prog.py --seed {p.seed}{' --red' if p.red else ''}: Zcb program of gen_test_cmp_zcb",
         f"# k={p.k} report words (TP-CMP-034 {len(p.items[ITEM_LS])}, TP-CMP-036 {len(p.items[ITEM_ALU])}, "
         f"TP-CMP-038 {len(p.items[ITEM_MUL])}), gen_min_retired={p.min_retired}"]
    if p.red:
        L.append(f"# RED FIXTURE: {p.red_note}; the expectation keeps the true form, so the fire-check must fail")
    L += ['.include "gen_zc_insn.h"', '.include "gen_mmio_map.h"', "", ".section .text", ".globl _start", "_start:"]
    L += body_lines(p.ops, p.filler_init)
    L += ["  li   gp, 1", "  la   t5, tohost", "  sw   gp, 0(t5)", "1:", "  j    1b", "",
          ".section .data", ".align 6", ".globl tohost", "tohost:   .dword 0", ".globl fromhost", "fromhost: .dword 0",
          ".align 4", f"{SCRATCH}:"]
    for i in range(0, SCRATCH_BYTES, 16):
        L.append("  .byte " + ", ".join(f"0x{b:02x}" for b in p.scratch_init[i:i + 16]))
    L += [".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--red", action="store_true", help="emit the TDD red fixture (one ALU form deviates)")
    a = ap.parse_args()
    p = plan(a.seed, a.red)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(emit(p))
    print(f"OK seed={a.seed} red={a.red} out={a.out} k={p.k} min_retired={p.min_retired} {p.summary}"
          + (f" red_note={p.red_note!r}" if a.red else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
