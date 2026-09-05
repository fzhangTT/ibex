"""gen_test_mul_mul: plan group gen_mul_mul (dv/auto_dv/docs/gen_test_plan.md version 2 of 2026-09-03 12:43 UTC, AREA
MUL; the plan at the clone HEAD of the batch-2 dispatch). Every item of the group is `Expected: pass`: a pass test.

Items built, with their canonical features (gen_feature_list.md Section 3): TP-MUL-001 mul (F-MUL-001), TP-MUL-002 mul
operand extremes and wrap (F-MUL-002), TP-MUL-004 mulh sign combinations and extremes (F-MUL-004), TP-MUL-005 mulhu
(F-MUL-005), TP-MUL-006 mulhu extremes (F-MUL-006), TP-MUL-007 mulhsu (F-MUL-007), TP-MUL-008 mulhsu asymmetry
(F-MUL-008), TP-MUL-027 c.mul reaches the multiplier (F-MUL-027 is an ALIAS of F-CMP-038, the canonical feature).
Item NOT built: TP-MUL-003 mulh and its two-cycle latency (F-MUL-003): its subject is the latency clause (retire delta 2
unstalled, gap_clean and wb_busy), a bus or RVFI cycle fact that needs the RVFI cycle / bus record export and the event
export (plan Section 6 item 5, TB Infra ASK 4/5); mulh values over every sign pair are checked under TP-MUL-004.
Program: the per-seed generator dv/auto_dv/tests/gen_programs/gen_mul_mul_prog.py (testlist `program: {generator: ...,
seed: run}`) draws every multiply form's directed floor inside the random stream (every extreme-by-extreme operand pair of
CG-MUL-001 cr_extremes, every rs1/rs2 operand class, every sign pair, every W4 register relation, the c.mul rsd'/rs2'
sweep, both orders of the TP-MUL-008 asymmetric pairs) plus W7-weighted extras, chains, rd = x0 and x0 sources, and
stores the RAW observation (rd after each multiply) to GEN_MM_EOT_ADDR; the expected words come from the RV32M product
model (m-st-ext.adoc "Multiplication Operations") walked over a register model of the program. The operand pool is
x1..x27 (x28 carries the report address, x29..x31 are the filler registers), c.mul uses x8..x15.
Fire-checks, one per built item over the report words the plan attributes to it, each also asserting the item's
directed floor for this seed from the plan (never "every bin over the regression"): fire_tp_mul_001 (every rs1 and rs2
class, every sign pair, every register relation, dependent chains), fire_tp_mul_002 (every extreme pair, x * 0 and
x * 1, result classes 1, 0, INT_MIN, 0xFFFFFFFE), fire_tp_mul_004 (every extreme pair and sign pair, results
0x3FFFFFFF, 0x40000000, 0, 0xFFFFFFFF), fire_tp_mul_005 (every rs1 and rs2 class), fire_tp_mul_006 (every extreme pair,
random msb-set pairs, results 0xFFFFFFFE, 1, 0x40000000, 0), fire_tp_mul_007 (all four sign pairs), fire_tp_mul_008
(both orders of every asymmetric pair with differing observed results where the model differs, results 0xFFFFFFFF,
INT_MIN, 0), fire_tp_mul_027 (correct low product in rsd' over every extreme pair, the rsd' and rs2' sweeps, rsd' ==
rs2' and distinct). Vacuous compares (rd = x0, a zero operand) are counted apart in every detail; they are not
observations. fire_program_verdict (not a plan item, so it declares no bins) asserts the program's own verdict:
tohost code == lib.TOHOST_PASS, retirements at the end-of-test store >= gen_min_retired, report count == the plan's k.
Clauses NOT asserted here, with the missing channel named (the always-on checkers carry them meanwhile): the stall and
latency clauses of TP-MUL-005 and TP-MUL-007 (">= 50 with retire delta 2 unstalled") and TP-MUL-027 ("retire delta 1
unstalled") need the RVFI cycle / bus record export; the RVFI-field clauses of TP-MUL-027 (rvfi_insn = the 16-bit c.mul
encoding, rvfi_rd_addr in x8..x15) and the "observed on RVFI" / "test decodes rs1/rs2 rdata" wording of TP-MUL-001..008
need the RVFI record export (ASK 5): until it lands the operand classes are the program's own operands (the plan) and the
observation is the stored rd. Always-on checkers relied on, whose uvm_error the flow collects: the ISA comparator rows
(isa_insn, isa_rd, isa_pc, isa_trap) and rvfi_proto. Red fixtures: `--red [--red-item <item>]` makes the program deviate
on one intent of that item (one multiply emitted as another RV32M form; for TP-MUL-027 one c.mul operand with its low
bit flipped) while the expectation keeps the true program, so exactly that item's fire-check fails; without --red-item
the seed draws the item.
Knobs (the items' Knobs lines: knob_imem_rvalid_delay, knob_imem_gnt_delay): schedulable = lib.TIMING_ONLY_KNOBS,
nothing pinned. declare_bins() is not overridden: the template declares the plan bins of the eight
items the fire_tp_mul_* methods name (the manifest is rendered from this module). MODULE=dv.auto_dv.tests.gen_test_mul_mul.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_mul_mul_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest


def _plan(test):
    """The seed's program plan, built once per test instance: the generator is the single origin of the
    program's intent, of the expected report words and of the per-seed directed floors."""
    if getattr(test, "_mul_mul_plan", None) is None:
        test._mul_mul_plan = prog.plan(test.seed)
    return test._mul_mul_plan


def _compare(test, item, detail):
    """(ok, detail) of one item: every report word the plan attributes to it equals its expectation and the
    plan carries the item's directed floor for this seed."""
    p = _plan(test)
    idxs = p.items[item]
    s = p.summary[item]
    bad = [(i, p.reports[i]) for i in idxs if i >= len(test.reports) or test.reports[i] != p.reports[i].expect]
    text = f"{len(idxs)} report words ({detail}; observable {s['observable']}, rd=x0 {s['rd_x0']}, vacuous zero-operand {s['vacuous']})"
    if bad:
        i, r = bad[0]
        got = f"0x{test.reports[i]:08x}" if i < len(test.reports) else "missing"
        text += f": {len(bad)} mismatch(es), first idx={i} {r.label} expected 0x{r.expect:08x} got {got}"
    else:
        text += " all match"
    missing = p.missing[item]
    text += f"; floor missing {missing[:3]}" if missing else "; floor complete"
    return bool(idxs) and not bad and not missing, text


class MulMul(GenTest):
    name = "gen_test_mul_mul"
    schedulable = lib.TIMING_ONLY_KNOBS
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {"TP-MUL-003": "latency clause: RVFI cycle / bus records, event export"}
    # bins this test does not guarantee per run, with the reason and its class (gen_test_template.bins_not_hit)
    bins_not_hit = {
        "gen_mul_timing_cg.cr_op_delta_clean.mulhsu_d2":
            "seed-dependent by measurement, cause undiagnosed: hit at 38 of 40 seeds in the wave at 4017573 (gen_wave_4017573/gen_wave_census.txt); one of the four delta-2 timing bins (mul_div cp_delta.d2 and cr_dit_div0_delta.dit0_div0_d2, mul_mul cr_op_delta_clean.mulhsu_d2 and mulhu_d2) that get one diagnosis together; PLANNED in traceability, credited from the merged report",
        "gen_mul_timing_cg.cr_op_delta_clean.mulhu_d2":
            "seed-dependent by measurement, cause undiagnosed: hit at 38 of 40 seeds in the wave at 4017573 (gen_wave_4017573/gen_wave_census.txt); one of the four delta-2 timing bins (mul_div cp_delta.d2 and cr_dit_div0_delta.dit0_div0_d2, mul_mul cr_op_delta_clean.mulhsu_d2 and mulhu_d2) that get one diagnosis together; PLANNED in traceability, credited from the merged report",
    }

    def report_count(self):
        return _plan(self).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_tp_mul_001()
        self.fire_tp_mul_002()
        self.fire_tp_mul_004()
        self.fire_tp_mul_005()
        self.fire_tp_mul_006()
        self.fire_tp_mul_007()
        self.fire_tp_mul_008()
        self.fire_tp_mul_027()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image, _plan(self).min_retired)
        got = self.eot_retired
        n, k = len(self.reports), _plan(self).k
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and n == k,
                   f"tohost code 0x{code:08x} (pass {lib.TOHOST_PASS}); retired at eot {got} (floor {floor}); reports {n} (k {k})")

    def fire_tp_mul_001(self):
        s = _plan(self).summary[prog.ITEM_MUL]
        ok, detail = _compare(self, prog.ITEM_MUL, f"mul mix: every rs1/rs2 class, {s['sign_pairs']} sign pairs, every register "
                              f"relation (same-register {s['same_regs']}), {s['chains']} chained products")
        self.check("fire_tp_mul_001", ok, detail)

    def fire_tp_mul_002(self):
        s = _plan(self).summary[prog.ITEM_MUL_EXT]
        ok, detail = _compare(self, prog.ITEM_MUL_EXT, f"mul extremes: {s['extreme_pairs']} extreme pairs, x*0, x*1, results 1/0/INT_MIN/0xFFFFFFFE")
        self.check("fire_tp_mul_002", ok, detail)

    def fire_tp_mul_004(self):
        s = _plan(self).summary[prog.ITEM_MULH]
        ok, detail = _compare(self, prog.ITEM_MULH, f"mulh: {s['extreme_pairs']} extreme pairs, {s['sign_pairs']} sign pairs, "
                              "results 0x3FFFFFFF/0x40000000/0/0xFFFFFFFF")
        self.check("fire_tp_mul_004", ok, detail)

    def fire_tp_mul_005(self):
        ok, detail = _compare(self, prog.ITEM_MULHU, "mulhu mix: every rs1 and rs2 class, msb-set classes weighted up")
        self.check("fire_tp_mul_005", ok, detail)

    def fire_tp_mul_006(self):
        s = _plan(self).summary[prog.ITEM_MULHU_EXT]
        ok, detail = _compare(self, prog.ITEM_MULHU_EXT, f"mulhu extremes: {s['extreme_pairs']} extreme pairs, random msb-set pairs, "
                              "results 0xFFFFFFFE/1/0x40000000/0")
        self.check("fire_tp_mul_006", ok, detail)

    def fire_tp_mul_007(self):
        s = _plan(self).summary[prog.ITEM_MULHSU]
        ok, detail = _compare(self, prog.ITEM_MULHSU, f"mulhsu mix: {s['sign_pairs']} sign pairs (rs1 sign x rs2 msb)")
        self.check("fire_tp_mul_007", ok, detail)

    def fire_tp_mul_008(self):
        p = _plan(self)
        s = p.summary[prog.ITEM_MULHSU_ASYM]
        ok, detail = _compare(self, prog.ITEM_MULHSU_ASYM, f"mulhsu asymmetry: {s['extreme_pairs']} ordered extreme pairs, "
                              f"{s['swaps']} random swapped pairs, results 0xFFFFFFFF/INT_MIN/0")
        differ = [(i, j) for i, j, d in p.asym if d]
        equal = [(i, j) for i, j in differ if i >= len(self.reports) or j >= len(self.reports) or self.reports[i] == self.reports[j]]
        detail += f"; {len(p.asym)} swapped-order pairs, {len(differ)} with differing model results, {len(equal)} observed equal or missing"
        self.check("fire_tp_mul_008", ok and bool(differ) and not equal, detail)

    def fire_tp_mul_027(self):
        s = _plan(self).summary[prog.ITEM_CMUL]
        ok, detail = _compare(self, prog.ITEM_CMUL, f"c.mul low product in rsd': {s['extreme_pairs']} extreme pairs, rsd'/rs2' sweep over "
                              f"x8..x15, rsd' == rs2' {s['same_regs']}")
        self.check("fire_tp_mul_027", ok, detail)


@cocotb.test()
async def gen_test_mul_mul(dut):
    await MulMul(dut).run()
