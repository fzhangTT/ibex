"""gen_test_cmp_zcb: plan group gen_cmp_zcb (dv/auto_dv/docs/gen_test_plan.md Section 4.1, AREA CMP).

Items and canonical features (gen_feature_list.md Section 3), all three built: TP-CMP-034 Zcb loads and
stores (F-CMP-034), TP-CMP-036 Zcb ALU forms (F-CMP-036), TP-CMP-038 c.mul (F-CMP-038; F-MUL-027 is its
ALIAS). Program: the per-seed generator dv/auto_dv/tests/gen_programs/gen_cmp_zcb_prog.py (testlist
`program: {generator: ..., seed: run}`) draws the Zcb operations, their operands, registers, order and the
unrelated instructions around them from the run seed, computes every expected report word from the Zc
specification semantics, and stores the RAW observations to GEN_MM_EOT_ADDR: the memory word(s) after each
c.sb/c.sh, rd' after each c.lbu/c.lhu/c.lh and each ALU form, rsd' after each c.mul. Red fixtures: `--red
[--red-item <item>]` makes the program deviate on one intent of that item (a load or store emitted as
another form, an ALU form emitted as another form, a c.mul rsd' operand differing in its low bit) while the
expectation keeps the true program, so exactly that item's fire-check fails; without --red-item the seed
draws the item.
Fire-checks, one per item over the report words the plan attributes to it: fire_tp_cmp_034 (stored bytes/
halves land at base + uimm for every alignment and uimm, loads zero/sign-extend per form), fire_tp_cmp_036
(results of the five forms over the operand mix), fire_tp_cmp_038 (low products over every rsd'/rs2' class).
fire_program_verdict (not a plan item, so it declares no bins) asserts the program's own verdict: tohost
code == lib.TOHOST_PASS, retirements at the end-of-test store >= the program's gen_min_retired floor, report
count == the plan's k.
Blocked in this test, with the missing channel named: the RVFI clauses of TP-CMP-034/036 (rvfi_mem_rmask/
wmask by access size, the zero/sign extension in rvfi_rd_wdata per record, rvfi_insn = the 16-bit encoding)
need the RVFI record export (plan Section 6 item 5, TB Infra ASK 5); the TP-CMP-034 split clause (a
halfword at addr[1:0] = 3 is two bus accesses, a halfword at addr[1:0] = 1 one access with be 0110) needs
the bus record export (ASK 4). Until those land the clauses rest on the always-on checkers whose uvm_error
the flow collects: the ISA comparator (isa_insn, isa_rd, isa_mem, isa_pc, isa_trap), rvfi_proto and the bus
protocol checkers (dbus_proto, dbus_split, ibus_proto).
Knobs (the items' Knobs lines): knob_dmem_rvalid_delay, knob_dmem_gnt_delay (TP-CMP-034),
knob_imem_rvalid_delay (TP-CMP-036/038); nothing is pinned.
declare_bins() is not overridden: the template declares the plan bins of the three items the fire_tp_cmp_*
methods name (the manifest is rendered from this module). MODULE=dv.auto_dv.tests.gen_test_cmp_zcb.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_cmp_zcb_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest


def _plan(test):
    """The seed's program plan, built once per test instance: the generator is the single origin of
    the program's intent and of the expected report words."""
    if getattr(test, "_cmp_zcb_plan", None) is None:
        test._cmp_zcb_plan = prog.plan(test.seed)
    return test._cmp_zcb_plan


def _compare(test, item, detail):
    """(ok, detail) of one item: every report word the plan attributes to it equals its expectation."""
    p = _plan(test)
    idxs = p.items[item]
    bad = [(i, p.reports[i]) for i in idxs if i >= len(test.reports) or test.reports[i] != p.reports[i].expect]
    text = f"{len(idxs)} report words ({detail})"
    if bad:
        i, r = bad[0]
        got = f"0x{test.reports[i]:08x}" if i < len(test.reports) else "missing"
        text += f": {len(bad)} mismatch(es), first idx={i} {r.label} expected 0x{r.expect:08x} got {got}"
    else:
        text += " all match"
    return bool(idxs) and not bad, text


class CmpZcb(GenTest):
    name = "gen_test_cmp_zcb"
    schedulable = ("knob_dmem_rvalid_delay", "knob_dmem_gnt_delay", "knob_imem_rvalid_delay")
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    # bins this test does not guarantee per run, with the reason and its class (gen_test_template.bins_not_hit)
    bins_not_hit = {
        "gen_cmp_zcb_cg.cp_alu_operand.rand":
            "declaration: default catch-all bin: the program drives only named operand classes, so the `rand` default never fires; a default bin cannot be a per-run guarantee",
        "gen_cmp_zcb_cg.cr_alu_operand.c_not_rand":
            "declaration: component bin cp_alu_operand.rand is a default that never fires, so this cross cannot be hit; the cross follows its component",
        "gen_cmp_zcb_cg.cr_alu_operand.c_sext_b_rand":
            "declaration: component bin cp_alu_operand.rand is a default that never fires, so this cross cannot be hit; the cross follows its component",
        "gen_cmp_zcb_cg.cr_alu_operand.c_sext_h_rand":
            "declaration: component bin cp_alu_operand.rand is a default that never fires, so this cross cannot be hit; the cross follows its component",
        "gen_cmp_zcb_cg.cr_alu_operand.c_zext_b_rand":
            "declaration: component bin cp_alu_operand.rand is a default that never fires, so this cross cannot be hit; the cross follows its component",
        "gen_cmp_zcb_cg.cr_alu_operand.c_zext_h_rand":
            "declaration: component bin cp_alu_operand.rand is a default that never fires, so this cross cannot be hit; the cross follows its component",
        "gen_mul_ops_cg.cp_rs1_class.all_ones":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_mul_ops_cg.cp_rs1_class.int_max":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_mul_ops_cg.cp_rs1_class.int_min":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_mul_ops_cg.cp_rs1_class.zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_mul_ops_cg.cr_op_rs1.c_mul_all_ones":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_mul_ops_cg.cr_op_rs1.c_mul_int_max":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_mul_ops_cg.cr_op_rs1.c_mul_int_min":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_mul_ops_cg.cr_op_rs1.c_mul_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
    }
    not_built = {}

    def report_count(self):
        return _plan(self).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_tp_cmp_034()
        self.fire_tp_cmp_036()
        self.fire_tp_cmp_038()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image, _plan(self).min_retired)
        got = self.eot_retired
        n, k = len(self.reports), _plan(self).k
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and n == k,
                   f"tohost code 0x{code:08x} (pass {lib.TOHOST_PASS}); retired at eot {got} (floor {floor}); reports {n} (k {k})")

    def fire_tp_cmp_034(self):
        s = _plan(self).summary
        ok, detail = _compare(self, prog.ITEM_LS, f"c_sb {s['c_sb']} c_sh {s['c_sh']} (split {s['sh_split']}) "
                              f"c_lbu {s['c_lbu']} c_lhu {s['c_lhu']} c_lh {s['c_lh']}, every alignment and uimm")
        self.check("fire_tp_cmp_034", ok, detail)

    def fire_tp_cmp_036(self):
        s = _plan(self).summary
        ok, detail = _compare(self, prog.ITEM_ALU, " ".join(f"{f} {s[f]}" for f in prog.ALU_FORMS) + ", operand mix")
        self.check("fire_tp_cmp_036", ok, detail)

    def fire_tp_cmp_038(self):
        s = _plan(self).summary
        ok, detail = _compare(self, prog.ITEM_MUL, f"c_mul {s['mul']} (rsd' == rs2' {s['c_mul_same']}), rsd'/rs2' sweep")
        self.check("fire_tp_cmp_038", ok, detail)


@cocotb.test()
async def gen_test_cmp_zcb(dut):
    await CmpZcb(dut).run()
