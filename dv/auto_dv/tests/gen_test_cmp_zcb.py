"""gen_test_cmp_zcb: plan group gen_cmp_zcb (dv/auto_dv/docs/gen_test_plan.md Section 4.1, AREA CMP).

Items and canonical features (gen_feature_list.md Section 3): TP-CMP-034 Zcb loads and stores
(F-CMP-034), TP-CMP-036 Zcb ALU forms (F-CMP-036), TP-CMP-038 c.mul (F-CMP-038; F-MUL-027 is its
ALIAS). Program: the per-seed generator dv/auto_dv/tests/gen_programs/gen_cmp_zcb_prog.py (testlist
`program: {generator: ..., seed: run}`), which draws the Zcb operations, their operands, registers,
order and the unrelated instructions around them from the run seed, computes every expected report
word from the Zc specification semantics, and stores the RAW observations to GEN_MM_EOT_ADDR: the
memory word(s) after each c.sb/c.sh, rd' after each c.lbu/c.lhu/c.lh, rd' after each ALU form, rsd'
after each c.mul; `--red` emits one ALU form as a different form while the expectation stays true.
Fire-checks (one per item, each over that item's report words): fire_tp_cmp_034 (stored bytes/
halves land at base + uimm for every alignment and uimm, loads zero/sign-extend per form),
fire_tp_cmp_036 (results of the five forms over the operand mix), fire_tp_cmp_038 (low products
over every rsd'/rs2' class). The items' RVFI- and bus-level clauses (rvfi_mem_rmask/wmask, the
split of a halfword at addr[1:0] = 3 versus one access with be 0110 at addr[1:0] = 1, rvfi_insn =
the 16-bit encoding) are not observable from Python at HEAD; they rest on the always-on checkers
relied on here: the ISA comparator (isa_insn, isa_rd, isa_mem, isa_pc, isa_trap), rvfi_proto and the
bus protocol checkers (dbus_proto, dbus_split, ibus_proto), whose uvm_error the flow collects.
Knobs (the items' Knobs lines): knob_dmem_rvalid_delay, knob_dmem_gnt_delay (TP-CMP-034),
knob_imem_rvalid_delay (TP-CMP-036/038); nothing is pinned. layers_required = False: the TB has no
REGIME_SET consumer at HEAD (step 2b parked), so the layers are logged not_applied; it flips to the
default when step 2b lands. declare_bins() returns []: no covergroup exists yet (CG-CMP-005 and
CG-MUL-001 bins are wired when gen_fcov_pkg lands). MODULE=dv.auto_dv.tests.gen_test_cmp_zcb.
"""
import cocotb

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
    # Bring-up flag: no REGIME_SET consumer at HEAD (step 2b parked); back to the default when it lands.
    layers_required = False

    def report_count(self):
        return _plan(self).k

    def fire_check(self):
        self.fire_tp_cmp_034()
        self.fire_tp_cmp_036()
        self.fire_tp_cmp_038()

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
