"""gen_test_isa_shift: plan group gen_isa_shift (dv/auto_dv/docs/gen_test_plan.md AREA ISA, plan version 2 of
2026-09-03 12:43 UTC at the batch-2 dispatch HEAD, dv/auto_dv/work/test-writer/batch2/README.md).

Items and canonical features (gen_feature_list.md Section 3 lists no ALIAS or FOLDED id for them), all four built:
TP-ISA-010 shift-immediate slli/srli/srai over the shamt and operand classes (F-ISA-010), TP-ISA-011 shift by 0 and 31
and sign propagation (F-ISA-011), TP-ISA-013 shift-register sll/srl/sra with rs2[31:5] = 0 (F-ISA-013), TP-ISA-014
shift-register ignores the rs2 upper bits (F-ISA-014). not_built = {} (no item of the group is left out).
Program: the per-seed generator dv/auto_dv/tests/gen_programs/gen_isa_shift_prog.py (testlist `program: {generator: ...,
seed: run}`) draws one shuffled stream of base shifts (the directed floors: every op x every amount 0..31 with an
amount-sensitive operand, every op x every cp_operand class, one rd = x0 form per op, the TP-ISA-011 directed cases,
every register op x every nonzero cp_rs2_upper class; plus W1/W3/W4 weighted extras with rd = x0, x0 sources and
rs1 == rs2 allowed), randomizes registers, order and PC alignment (a compressed nop before a fraction of the shifts),
and stores the RAW rd of every shift to GEN_MM_EOT_ADDR (one report word per op). Every expected word comes from the
generator's 32-bit shift model written from the RV32I text (tools/specs rv32.adoc), never from the RTL.
Fire-checks, one per item over the report words the plan attributes to it, asserted per seed:
fire_tp_isa_010: every attributed word matches, and per immediate op every shamt class (s0, s1, mid, s31) and every
cp_operand class was observed (shamt classes only through amount-sensitive, rd != x0 compares);
fire_tp_isa_011: every directed case matches with the result F-ISA-011 states (the eight cr_sra_sign tuples and their
sll/srl mirrors) and the shift by 0 of a random operand returned rs1 for each of the six ops;
fire_tp_isa_013: every attributed word matches, and per register op with rs2[31:5] = 0 every shift amount 0..31 and every
cp_operand class was observed (amounts only through amount-sensitive, rd != x0 compares);
fire_tp_isa_014: every attributed word matches, and every register op was observed with every nonzero cp_rs2_upper
class (32, 33, all ones, msb only, 0xFFFFFFE0, other nonzero) through amount-sensitive compares.
Vacuous compares (rd = x0; amount-insensitive operands such as 0, or all ones under an arithmetic right shift) are
counted apart in the detail and never satisfy a coverage clause; they are still emitted and compared (no dodges).
fire_program_verdict (not a plan item, so it declares no bins): tohost code == lib.TOHOST_PASS, retirements at the
end-of-test store >= the program's gen_min_retired floor, report count == the plan's k.
Red fixtures: `--red [--red-item <item>]` makes the program emit one non-vacuous op of that item as another op of its
form or with a shift amount differing in one bit while the expectation keeps the true program, so exactly that item's
fire-check fails; without --red-item the seed draws the item (seed 1 draws TP-ISA-010).
Clauses not checked here, with the missing channel named: the RVFI-record form of every fire-check (the retirement's
rvfi_rs1_rdata / rvfi_rs2_rdata / rvfi_rd_wdata fields, TP-ISA-011's rvfi_rd_wdata == rvfi_rs1_rdata per record) needs
the RVFI record export (plan Section 6 item 5, TB Infra ASK 5); the value clause is checked on the architectural rd
through the report channel and the record itself rests on the always-on ISA comparator (isa_insn, isa_rd, isa_pc,
isa_trap rows) and rvfi_proto, whose uvm_error the flow collects. The U-mode iterations of TP-ISA-010/013 ("U per C-2")
are not taken: batch-2 programs stay in M-mode by design (M-mode group rule of the batch-2 brief).
Knobs (the items' Knobs lines): knob:imem_rvalid_delay (all four items), knob:imem_gnt_delay (TP-ISA-011/014);
schedulable = lib.TIMING_ONLY_KNOBS (the program needs no handler); nothing is pinned.
declare_bins() is not overridden: the template declares the plan bins of the four items the fire_tp_isa_* methods name
(the manifest dv/auto_dv/fcov_expectations/gen_test_isa_shift.fcov.yaml is rendered from this module).
MODULE=dv.auto_dv.tests.gen_test_isa_shift.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_isa_shift_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest


def _plan(test):
    """The seed's program plan, built once per test instance: the generator is the single origin of the program's
    intent and of the expected report words."""
    if getattr(test, "_isa_shift_plan", None) is None:
        test._isa_shift_plan = prog.plan(test.seed)
    return test._isa_shift_plan


def _matched(test, ops):
    """The plan ops whose report word arrived and equals the expectation."""
    return [o for o in ops if o.idx < len(test.reports) and test.reports[o.idx] == o.expect]


def _compare(test, item):
    """(ok, matched ops, detail) of one item: every report word the plan attributes to it equals its expectation."""
    ops = [o for o in _plan(test).ops if o.item == item]
    good = _matched(test, ops)
    bad = [o for o in ops if o.idx not in {g.idx for g in good}]
    text = (f"{len(ops)} report words ({sum(1 for o in ops if o.rd == 0)} rd_x0 and "
            f"{sum(1 for o in ops if o.rd and o.vacuous)} amount-insensitive counted apart)")
    if bad:
        o = bad[0]
        got = f"0x{test.reports[o.idx]:08x}" if o.idx < len(test.reports) else "missing"
        text += f": {len(bad)} mismatch(es), first idx={o.idx} {o.label()} expected 0x{o.expect:08x} got {got}"
    else:
        text += " all match"
    return bool(ops) and not bad, good, text


def _missing(good, ops, key, want, sensitive_only):
    """Per op: the wanted classes no matched (and, when asked, amount-sensitive) compare with rd != x0 reached."""
    out = []
    for op in ops:
        seen = {key(o) for o in good if o.op == op and o.rd and not (sensitive_only and o.vacuous)}
        gap = sorted(set(want) - seen)
        if gap:
            out.append(f"{op}:{','.join(str(g) for g in gap)}")
    return out


class IsaShift(GenTest):
    name = "gen_test_isa_shift"
    schedulable = lib.TIMING_ONLY_KNOBS
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {}

    def report_count(self):
        return _plan(self).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_tp_isa_010()
        self.fire_tp_isa_011()
        self.fire_tp_isa_013()
        self.fire_tp_isa_014()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image, _plan(self).min_retired)
        got = self.eot_retired
        n, k = len(self.reports), _plan(self).k
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and n == k,
                   f"tohost code 0x{code:08x} (pass {lib.TOHOST_PASS}); retired at eot {got} (floor {floor}); reports {n} (k {k})")

    def fire_tp_isa_010(self):
        ok, good, detail = _compare(self, prog.ITEM_010)
        gaps = _missing(good, prog.IMM_OPS, lambda o: prog.shamt_class(o.shamt), prog.SHAMT_CLASSES, True)
        gaps += _missing(good, prog.IMM_OPS, lambda o: prog.operand_class(o.x), prog.OPERAND_CLASSES, False)
        s = _plan(self).summary
        self.check("fire_tp_isa_010", ok and not gaps,
                   f"slli {s['slli']} srli {s['srli']} srai {s['srai']}: {detail}; shamt and operand classes per op "
                   + ("all observed" if not gaps else f"missing {gaps}"))

    def fire_tp_isa_011(self):
        p = _plan(self)
        ok, good, detail = _compare(self, prog.ITEM_011)
        hit = {o.kind[5:] for o in good}
        bad = [n for n in prog.CASE_NAMES if n not in hit]
        # the matched word equals the model; the model is pinned to the F-ISA-011 results and to result == rs1 here
        bad += [n for n, want in prog.SIGN_RESULTS.items() if n not in bad and p.ops[p.cases[n]].expect != want]
        bad += [n for n in prog.ZERO_CASES if n not in bad and p.ops[p.cases[n]].expect != p.ops[p.cases[n]].x]
        self.check("fire_tp_isa_011", ok and not bad,
                   f"{len(prog.CASE_NAMES)} directed cases ({len(prog.SIGN_CASES)} sign/extreme, {len(prog.ZERO_CASES)} shift by 0): "
                   f"{detail}; " + ("every case observed with the F-ISA-011 result" if not bad else f"cases failed {bad}"))

    def fire_tp_isa_013(self):
        ok, good, detail = _compare(self, prog.ITEM_013)
        gaps = _missing(good, prog.REG_OPS, lambda o: o.shamt, range(prog.N_SHAMT), True)
        gaps += _missing(good, prog.REG_OPS, lambda o: prog.operand_class(o.x), prog.OPERAND_CLASSES, False)
        s = _plan(self).summary
        self.check("fire_tp_isa_013", ok and not gaps,
                   f"sll {s['sll']} srl {s['srl']} sra {s['sra']} (rs2[31:5] = 0 on this item): {detail}; every amount 0..31 and "
                   "operand class per op " + ("all observed" if not gaps else f"missing {gaps}"))

    def fire_tp_isa_014(self):
        ok, good, detail = _compare(self, prog.ITEM_014)
        gaps = _missing(good, prog.REG_OPS, lambda o: prog.upper_class(o.amt), prog.UPPER_NONZERO, True)
        self.check("fire_tp_isa_014", ok and not gaps,
                   f"{_plan(self).summary['upper_nonzero']} register shifts with rs2[31:5] != 0: {detail}; nonzero rs2 upper classes per op "
                   + ("all observed" if not gaps else f"missing {gaps}"))


@cocotb.test()
async def gen_test_isa_shift(dut):
    await IsaShift(dut).run()
