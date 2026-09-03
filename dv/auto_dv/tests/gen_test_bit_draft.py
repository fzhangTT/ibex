"""gen_test_bit_draft: group gen_bit_draft (gen_test_plan.md Section 4.1 AREA BIT), the draft-0.93
bitmanip ops the pinned Spike lacks, checked through the shim's C reference (C5.5).

Items BUILT: TP-BIT-016 (feature F-BIT-016, ACTIVE, no alias): generic grevi / gorci / grev / gorc with
every W9 control word, W1 operands, W3 rs2 upper bits, plus the pinned aliases rev8 (grevi 24), orc.b
(gorci 7) and brev8 (draft rev.b = grevi 7). Items not built, blocker generator growth (the shim's C reference
gen_isa_exec_reference in dv/auto_dv/isa/gen_isa_shim.cc covers these op groups; this test's generator emits
grev/gorc forms only, so their programs, expected values and fire_tp methods are still to be written):
TP-BIT-011 (F-BIT-011: pack/packh/packu with rs2 != x0), TP-BIT-022 /
TP-BIT-023 (F-BIT-022 / F-BIT-023: slo/sro/sloi/sroi), TP-BIT-024 (F-BIT-024: shfl/unshfl/shfli/unshfli),
TP-BIT-025 / TP-BIT-026 (F-BIT-025 / F-BIT-026: xperm.n/.b/.h), TP-BIT-027 (F-BIT-027: cmov/cmix),
TP-BIT-028 / TP-BIT-029 (F-BIT-028 / F-BIT-029: fsl/fsr/fsri), TP-BIT-030 / TP-BIT-031 (F-BIT-030 /
F-BIT-031: bfp), TP-BIT-032 / TP-BIT-033 (F-BIT-032 / F-BIT-033: crc32.b/h/w, crc32c.b/h/w).

Program: dv/auto_dv/tests/gen_programs/gen_bit_draft_prog.py at the run seed (testlist `program:
{generator: ..., seed: run}`); plan(seed) is the single source of the op stream, the expected rd values
(Python grev32/gorc32 from the draft Bitmanip text) and the report count; the program replays every rd
to the EOT register in plan order. The stream carries a directed floor inside the random extras: one
control-sensitive op (rd != x0, operand neither 0 nor all-ones) per (base, control) pair over the 32
controls of each of the four bases, the three alias forms, a single-bit operand per base and nonzero
rs2 upper bits per register base; the extras keep rd = x0, x0 sources and zero operands, whose compares
are vacuous and counted apart. Knobs: knob:imem_rvalid_delay (the item's Knobs line), varied by the
template's layers 2/3 when the build consumes it. Fire-check per seed (fire_tp_bit_016): every report
word equals the plan's reference value per generic base and for the aliases; every (base, control)
pair has a control-sensitive op whose rd matched and the matched control-sensitive count reaches the
floor; each base has a matched single-bit op and each register base a matched op with nonzero rs2
upper bits; the report count is the plan's k; the program's retirement floor is reached; the
end-of-test code is the pass code. declare_bins() takes the template default (the plan's bins of
TP-BIT-016, checked against the rendered manifest in finish()). Always-on checkers relied on: the ISA
comparator (isa_rd through the shim's grev/gorc reference for the draft controls, Spike for rev8 /
orc.b), rvfi_proto, the bus protocol checkers. Red fixtures: the generator's --red --red-item
TP-BIT-016:imm (one gorci compare fails) and TP-BIT-016:ctrl (one base compare and the control-coverage
check fail). MODULE=dv.auto_dv.tests.gen_test_bit_draft, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_bit_draft_prog as prog

ITEM_KNOBS = ("knob_imem_rvalid_delay",)   # TP-BIT-016 Knobs line, literal so the regime-handler rule can read it
assert all(k in lib.REGIME_KNOBS for k in ITEM_KNOBS), f"unknown regime knob in {ITEM_KNOBS}"


class BitDraft(GenTest):
    name = "gen_test_bit_draft"
    schedulable = ITEM_KNOBS
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {
        "TP-BIT-011": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-022": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-023": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-024": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-025": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-026": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-027": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-028": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-029": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-030": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-031": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-032": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
        "TP-BIT-033": "the shim's draft-B references cover this op group since T-102, but this test's generator covers grev/gorc only (growth pending)",
    }

    def report_count(self):
        return prog.plan(self.seed).k

    def fire_check(self):
        self.fire_tp_bit_016()

    def fire_tp_bit_016(self):
        p = prog.plan(self.seed)
        got = self.reports
        exp = p.items["TP-BIT-016"]

        def matched(i):
            return i < len(got) and got[i] == p.reports[i]

        def compare(name, indices):
            bad = [i for i in indices if not matched(i)]
            detail = f"{len(indices)} ops, {len(bad)} mismatches"
            if bad:
                i = bad[0]
                op = p.ops[i]
                seen = f"0x{got[i]:08x}" if i < len(got) else "missing"
                detail += (f"; first op {i} {op.kind} ctrl={op.ctrl} rs1=0x{op.rs1_val:08x}"
                           + (f" rs2=0x{op.rs2_val:08x}" if not op.is_imm else "")
                           + f" expected 0x{op.expect:08x} got {seen}")
            self.check(name, len(indices) > 0 and not bad, detail)

        def per_base(name, groups):
            # every listed base needs at least one matched op; vacuous ops never enter these lists
            short = [b for b, idxs in groups.items() if not any(matched(i) for i in idxs)]
            self.check(name, len(groups) > 0 and not short,
                       f"matched per base {{{', '.join(f'{b}: {sum(matched(i) for i in idxs)}/{len(idxs)}' for b, idxs in groups.items())}}}"
                       + (f"; none matched for {short}" if short else ""))

        for base, indices in exp["ops_by_base"].items():
            compare(f"fire_tp_bit_016_{base}", indices)
        compare("fire_tp_bit_016_alias", exp["alias_ops"])
        # control floor: a (base, control) pair counts only through a control-sensitive op whose rd matched
        want = {(b, c) for b in prog.RANDOM_KINDS for c in range(prog.N_CTRL)}
        covered = {pair for pair, idxs in exp["controls"].items() if any(matched(i) for i in idxs)}
        missing = sorted(want - covered)
        n_sens = len(exp["sensitive_ops"])
        n_ok = sum(matched(i) for i in exp["sensitive_ops"])
        self.check("fire_tp_bit_016_controls", not missing and n_ok >= len(exp["floor_ops"]),
                   f"{len(covered)}/{len(want)} (base, control) pairs observed; {n_ok}/{n_sens} control-sensitive ops "
                   f"matched (floor {len(exp['floor_ops'])}, {len(p.ops) - n_sens} vacuous of {len(p.ops)})"
                   + (f"; missing {missing[:4]}" if missing else ""))
        per_base("fire_tp_bit_016_single_bit", exp["single_bit_ops"])
        per_base("fire_tp_bit_016_rs2_upper", exp["nonzero_upper_ops"])
        self.check("fire_tp_bit_016_reports", len(got) == p.k, f"{len(got)} report words (plan k={p.k})")
        floor = lib.program_min_retired(self.image)
        retired = self.retired()
        self.check("fire_tp_bit_016_retired", retired >= floor >= p.min_retired,
                   f"retired {retired} (program floor {floor}, plan {p.min_retired})")
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_tp_bit_016_eot", code == lib.TOHOST_PASS, f"tohost code 0x{code:08x} (pass = {lib.TOHOST_PASS})")


@cocotb.test()
async def gen_test_bit_draft(dut):
    await BitDraft(dut).run()
