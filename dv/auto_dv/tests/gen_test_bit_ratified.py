"""gen_test_bit_ratified: group gen_bit_ratified (gen_test_plan.md Section 4.1 AREA BIT, plan HEAD of the batch-2
dispatch, dv/auto_dv/work/test-writer/batch2/README.md), the ratified Zba / Zbb / Zbs / Zbc ops of RV32BOTEarlGrey
checked through Python references written from the ratified Bitmanip chapter (tools/specs/riscv-isa-manual).

Items BUILT (canonical feature IDs; F-BIT-040 resolves to F-CSR-021 through gen_feature_list.md Section 3.1):
TP-BIT-002 (F-BIT-002) sh1add / sh2add / sh3add over every CG-BIT-001 rs1 x rs2 class, the result consumed as a load
address; TP-BIT-003 (F-BIT-003) shift-out (rs1 = 0xE0000000, all-ones), wrap (carry out of rs2 + (rs1 << n)), same
register and equal operands per op; TP-BIT-004 (F-BIT-004) andn / orn / xnor over every class, zero and all-ones
results per op; TP-BIT-005 (F-BIT-005) clz / ctz / cpop over every CG-BIT-002 operand class, results 1 and 16;
TP-BIT-006 (F-BIT-006) every (op, single-bit position), results 32 / 0 / 31; TP-BIT-007 (F-BIT-007) min / max / minu /
maxu over every sign pair and class; TP-BIT-008 (F-BIT-008) equal operands (same register, equal values), (-1, 1) and
(INT_MIN, INT_MAX) for all four ops; TP-BIT-009 (F-BIT-009) sext.b / sext.h and c.sext.b / c.sext.h over the bit 7 /
bit 15 classes with 0x80 -> 0xFFFFFF80, 0x7F -> 0x7F, 0x8000 -> 0xFFFF8000; TP-BIT-010 (F-BIT-010) zext.h and c.zext.h
over every rs1 class; TP-BIT-014 (F-BIT-014) orc.b over the 16 byte-zero patterns; TP-BIT-015 (F-BIT-015) rev8 with
0x01020304 -> 0x04030201, single bits, random; TP-BIT-017 (F-BIT-017) bclr / bset / binv / bext over every index class
x prior bit; TP-BIT-018 (F-BIT-018) the immediate forms over index class x prior bit and operand class; TP-BIT-019
(F-BIT-019) index 0 and 31 for all eight ops, bset on a set bit, bclr on a clear bit, binv twice restoring the operand,
every register form with every nonzero W3 upper class acting at rs2[4:0], each instr[25] = 1 immediate form trapping with
mcause 2 and mtval = word (handler read-back, returning handler); TP-BIT-020 (F-BIT-020) clmul / clmulh / clmulr over
every CG-BIT-007 rs1 / rs2 class; TP-BIT-021 (F-BIT-021) clmul(x, 0), clmul(x, 1), (all-ones, all-ones) = 0x55555555 for
clmul and clmulh, single-bit pairs with i + j < 32 and >= 32 per op, the program-computed identity clmulr ==
(clmulh << 1) | clmul[31]; TP-BIT-038 (F-BIT-038) VALUE clause: every legal Zb* mnemonic (ratified set, rotates, the
draft set the shim serves) with rd = x0 followed by an x0 reader that reports 0; TP-BIT-040 (F-CSR-021 via F-BIT-040)
csrr misa at random points and right after a csrw attempt: bit 23 = 1, bit 1 = 0, bit 12 = 1, bit 2 = 1, value
MISA_VALUE.

Items NOT BUILT (blocked, owner TB Infra unless noted): TP-BIT-001 (F-BIT-001): "every cp_legal_insn bin observed on
RVFI with rvfi_trap = 0" is a per-retirement RVFI record fact (record export, not in batch 2) and its U-mode leg (C-2)
leaves M-mode; the ratified rows' decode is exercised by TP-BIT-002..021 here, the draft rows by gen_test_bit_draft.
Dropped clause of TP-BIT-038: "two-cycle ops still show delta 2 unstalled" (gen_chk_timing_isa, bus records / RVFI
cycle facts; icache and regime pins) - the value clause is built, the stall clause waits for the record export.

Program: dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py at the run seed (testlist `program: {generator: ...,
seed: run}`); plan(seed) is the single source of the op stream, the expected report words and the report count k; every
op stores its report word(s) straight to the EOT register in plan order. Directed floors sit inside the random stream:
one non-vacuous op (rd != x0) per class, case, position or pair an item's fire-check names (prog.wanted()), plus weighted
random extras with rd = x0 and x0 sources, whose compares are vacuous and counted apart. Knobs: imem gnt / rvalid
delays (the items' Knobs lines) through lib.TIMING_ONLY_KNOBS, varied by the template's layers 2/3 when the build
consumes them. layers_required = False: the TB has no REGIME_SET consumer at HEAD (step 2b parked), so the layers are
logged not_applied (staged entry measured: false); flips to the default when step 2b lands. Pinned knobs: none.

Fire-checks per seed: every non-vacuous op of an item reports its reference value (fire_tp_bit_<nnn>_ops); every
exhaustive set the item names has a carrier whose report matched (fire_tp_bit_<nnn>_<set>); TP-BIT-021 adds the
0x55555555 results and the identity word; TP-BIT-040 checks the misa bits on the actual report words;
fire_program_verdict: tohost pass code, retirement floor reached, report count k. declare_bins() takes the template
default (the plan's bins of the built items, checked against the rendered manifest in finish()). Always-on checkers
relied on: the ISA comparator rows (isa_rd for every op through Spike's Zba / Zbb / Zbs / Zbc, isa_trap / isa_csr for
the illegal words and the misa reads; the draft rd = x0 ops through the shim's C reference), rvfi_proto, the bus
protocol checkers. Red fixtures: the generator's --red --red-item <TP-ID> (one program deviation per built item that
trips exactly that item's fire_tp method; the default red draws the item from the seed). Retirement floor: the program's
gen_min_retired word. MODULE=dv.auto_dv.tests.gen_test_bit_ratified, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_bit_ratified_prog as prog
from dv.auto_dv.tests.gen_programs.gen_prog_const import MISA_VALUE

MISA_BITS = {"x_set": (23, 1), "b_clear": (1, 0), "m_set": (12, 1), "c_set": (2, 1)}   # CG-BIT-011 cp_misa bins


class BitRatified(GenTest):
    name = "gen_test_bit_ratified"
    schedulable = lib.TIMING_ONLY_KNOBS
    # Bring-up state (tier check, measured false): the build has no REGIME_SET consumer, so the layers
    # are logged not_applied; returns to the default (required) when TB Infra's step 2b lands.
    layers_required = False
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {
        "TP-BIT-001": "per-retirement rvfi_trap = 0 over the ENC table is an RVFI record fact (record export, TB Infra) and the U-mode leg leaves M-mode",
    }

    def report_count(self):
        return prog.plan(self.seed).k

    def fire_check(self):
        self._p = prog.plan(self.seed)
        got = self.reports
        # an op matched when every one of its report words equals the plan's
        self._ok = {op.idx for op in self._p.ops
                    if op.rep + len(op.expects) <= len(got) and got[op.rep:op.rep + len(op.expects)] == op.expects}
        self._want = prog.wanted()
        self.fire_tp_bit_002()
        self.fire_tp_bit_003()
        self.fire_tp_bit_004()
        self.fire_tp_bit_005()
        self.fire_tp_bit_006()
        self.fire_tp_bit_007()
        self.fire_tp_bit_008()
        self.fire_tp_bit_009()
        self.fire_tp_bit_010()
        self.fire_tp_bit_014()
        self.fire_tp_bit_015()
        self.fire_tp_bit_017()
        self.fire_tp_bit_018()
        self.fire_tp_bit_019()
        self.fire_tp_bit_020()
        self.fire_tp_bit_021()
        self.fire_tp_bit_038()
        self.fire_tp_bit_040()
        self.fire_program_verdict()

    # ---- shared per-item checks (the `what` prefix names the calling item) ----------------------------------------
    def fire_ops(self, pre, item):
        """Every non-vacuous op of the item reports its reference value; vacuous compares are counted apart."""
        exp = self._p.items[item]
        idxs = exp["ops"]
        bad = [i for i in idxs if i not in self._ok]
        detail = (f"{len(idxs)} ops ({len(exp['floor'])} floor, {len(exp['vacuous'])} vacuous rd = x0 counted apart), "
                  f"{len(bad)} mismatches")
        if bad:
            op = self._p.ops[bad[0]]
            got = self.reports[op.rep:op.rep + len(op.expects)]
            detail += (f"; first op {op.idx} {op.kind} rs1=0x{op.rs1_val:08x}" + (f" rs2=0x{op.rs2_val:08x}" if op.rs2 else "")
                       + (f" imm={op.imm}" if op.imm >= 0 else "")
                       + f" expected {' '.join(f'0x{w:08x}' for w in op.expects)} got {' '.join(f'0x{w:08x}' for w in got) or 'missing'}")
        self.check(f"{pre}_ops", len(idxs) > 0 and not bad, detail)

    def fire_floor(self, pre, item, key):
        """Every key of the item's exhaustive set has at least one carrier whose report matched."""
        want = self._want[item][key]
        groups = self._p.items[item].get(key, {})
        missing = sorted((k for k in want if not any(i in self._ok for i in groups.get(k, []))), key=str)
        self.check(f"{pre}_{key}", len(want) > 0 and not missing,
                   f"{len(want) - len(missing)}/{len(want)} {key} keys observed with a matched rd"
                   + (f"; missing {missing[:4]}" if missing else ""))

    # ---- items ---------------------------------------------------------------------------------------------------
    def fire_tp_bit_002(self):
        self.fire_ops("fire_tp_bit_002", "TP-BIT-002")
        for key in ("op_rs1", "op_rs2", "addr"):
            self.fire_floor("fire_tp_bit_002", "TP-BIT-002", key)

    def fire_tp_bit_003(self):
        self.fire_ops("fire_tp_bit_003", "TP-BIT-003")
        self.fire_floor("fire_tp_bit_003", "TP-BIT-003", "cases")

    def fire_tp_bit_004(self):
        self.fire_ops("fire_tp_bit_004", "TP-BIT-004")
        for key in ("op_rs1", "op_rs2", "result"):
            self.fire_floor("fire_tp_bit_004", "TP-BIT-004", key)

    def fire_tp_bit_005(self):
        self.fire_ops("fire_tp_bit_005", "TP-BIT-005")
        for key in ("op_operand", "result"):
            self.fire_floor("fire_tp_bit_005", "TP-BIT-005", key)

    def fire_tp_bit_006(self):
        self.fire_ops("fire_tp_bit_006", "TP-BIT-006")
        for key in ("op_single", "result"):
            self.fire_floor("fire_tp_bit_006", "TP-BIT-006", key)

    def fire_tp_bit_007(self):
        self.fire_ops("fire_tp_bit_007", "TP-BIT-007")
        for key in ("op_sign", "op_rs1", "op_rs2"):
            self.fire_floor("fire_tp_bit_007", "TP-BIT-007", key)

    def fire_tp_bit_008(self):
        self.fire_ops("fire_tp_bit_008", "TP-BIT-008")
        for key in ("op_sign", "cases"):
            self.fire_floor("fire_tp_bit_008", "TP-BIT-008", key)

    def fire_tp_bit_009(self):
        self.fire_ops("fire_tp_bit_009", "TP-BIT-009")
        for key in ("form_class", "exact"):
            self.fire_floor("fire_tp_bit_009", "TP-BIT-009", key)

    def fire_tp_bit_010(self):
        self.fire_ops("fire_tp_bit_010", "TP-BIT-010")
        self.fire_floor("fire_tp_bit_010", "TP-BIT-010", "form_class")

    def fire_tp_bit_014(self):
        self.fire_ops("fire_tp_bit_014", "TP-BIT-014")
        self.fire_floor("fire_tp_bit_014", "TP-BIT-014", "pattern")

    def fire_tp_bit_015(self):
        self.fire_ops("fire_tp_bit_015", "TP-BIT-015")
        self.fire_floor("fire_tp_bit_015", "TP-BIT-015", "cases")

    def fire_tp_bit_017(self):
        self.fire_ops("fire_tp_bit_017", "TP-BIT-017")
        self.fire_floor("fire_tp_bit_017", "TP-BIT-017", "op_index_prior")

    def fire_tp_bit_018(self):
        self.fire_ops("fire_tp_bit_018", "TP-BIT-018")
        for key in ("op_index_prior", "op_operand"):
            self.fire_floor("fire_tp_bit_018", "TP-BIT-018", key)

    def fire_tp_bit_019(self):
        self.fire_ops("fire_tp_bit_019", "TP-BIT-019")
        for key in ("op_index", "cases", "twice", "upper", "illegal"):
            self.fire_floor("fire_tp_bit_019", "TP-BIT-019", key)
        # the trap clause on the actual words: mcause 2 then mtval = the illegal word, for each of the four forms
        ill = [self._p.ops[i] for idxs in self._p.items["TP-BIT-019"].get("illegal", {}).values() for i in idxs]
        bad = [op for op in ill if self.reports[op.rep:op.rep + 2] != op.expects]
        self.check("fire_tp_bit_019_trap", len(ill) == len(prog.SBIT_IMM) and not bad,
                   f"{len(ill) - len(bad)}/{len(ill)} instr[25] = 1 words trapped with mcause {prog.CAUSE_ILLEGAL} and mtval = word"
                   + (f"; wrong {[(op.kind[8:], [f'0x{x:08x}' for x in self.reports[op.rep:op.rep + 2]]) for op in bad[:2]]}" if bad else ""))

    def fire_tp_bit_020(self):
        self.fire_ops("fire_tp_bit_020", "TP-BIT-020")
        for key in ("op_rs1", "op_rs2"):
            self.fire_floor("fire_tp_bit_020", "TP-BIT-020", key)

    def fire_tp_bit_021(self):
        self.fire_ops("fire_tp_bit_021", "TP-BIT-021")
        for key in ("cases", "ident"):
            self.fire_floor("fire_tp_bit_021", "TP-BIT-021", key)
        cases = self._p.items["TP-BIT-021"].get("cases", {})
        ones = {k: [self._p.ops[i] for i in cases.get((k, "ones"), [])] for k in ("clmul", "clmulh")}
        good = all(any(op.idx in self._ok and op.expects == [0x55555555] for op in ops) for ops in ones.values())
        self.check("fire_tp_bit_021_ones", good,
                   "clmul and clmulh of (all-ones, all-ones) observed with result 0x55555555: "
                   + ", ".join(f"{k}={'ok' if any(op.idx in self._ok and op.expects == [0x55555555] for op in ops) else 'no'}" for k, ops in ones.items()))

    def fire_tp_bit_038(self):
        self.fire_ops("fire_tp_bit_038", "TP-BIT-038")
        self.fire_floor("fire_tp_bit_038", "TP-BIT-038", "mnemonic")

    def fire_tp_bit_040(self):
        self.fire_ops("fire_tp_bit_040", "TP-BIT-040")
        self.fire_floor("fire_tp_bit_040", "TP-BIT-040", "when")
        reads = [self._p.ops[i] for i in self._p.items["TP-BIT-040"]["ops"]]
        vals = [self.reports[op.rep] for op in reads if op.rep < len(self.reports)]
        bad_bits = sorted({name for v in vals for name, (bit, val) in MISA_BITS.items() if (v >> bit) & 1 != val})
        self.check("fire_tp_bit_040_bits", len(vals) == len(reads) > 0 and not bad_bits and all(v == MISA_VALUE for v in vals),
                   f"{len(vals)} misa reads {[f'0x{v:08x}' for v in vals[:4]]} (expected 0x{MISA_VALUE:08x}: X set, B clear, M set, C set)"
                   + (f"; wrong bits {bad_bits}" if bad_bits else ""))

    def fire_program_verdict(self):
        p = self._p
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_program_verdict_eot", code == lib.TOHOST_PASS, f"tohost code 0x{code:08x} (pass = {lib.TOHOST_PASS})")
        floor = lib.program_min_retired(self.image)
        retired = self.retired()
        self.check("fire_program_verdict_retired", retired >= floor >= p.min_retired,
                   f"retired {retired} (program floor {floor}, plan {p.min_retired})")
        self.check("fire_program_verdict_reports", len(self.reports) == p.k, f"{len(self.reports)} report words (plan k={p.k})")


@cocotb.test()
async def gen_test_bit_ratified(dut):
    await BitRatified(dut).run()
