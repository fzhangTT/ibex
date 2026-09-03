"""gen_test_bit_draft: group gen_bit_draft (gen_test_plan.md Section 4.1 AREA BIT), the draft-0.93
bitmanip ops the pinned Spike lacks, checked through the shim's C reference (C5.5).

Items BUILT: TP-BIT-016 (feature F-BIT-016, ACTIVE, no alias): generic grevi / gorci / grev / gorc with
W9 control words, W1 operands, W3 rs2 upper bits, plus the pinned aliases rev8 (grevi 24), orc.b
(gorci 7) and brev8 (draft rev.b = grevi 7). Items BLOCKED on TB Infra's C5.5 reference for their op
(gen_isa_shim.cc gen_isa_exec_reference serves only grev/grevi/gorc/gorci; any other draft op raises
uvm_error isa_rd, so the program never emits one): TP-BIT-011 (F-BIT-011: pack/packh/packu with rs2 !=
x0), TP-BIT-022 / TP-BIT-023 (F-BIT-022 / F-BIT-023: slo/sro/sloi/sroi), TP-BIT-024 (F-BIT-024:
shfl/unshfl/shfli/unshfli), TP-BIT-025 / TP-BIT-026 (F-BIT-025 / F-BIT-026: xperm.n/.b/.h), TP-BIT-027
(F-BIT-027: cmov/cmix), TP-BIT-028 / TP-BIT-029 (F-BIT-028 / F-BIT-029: fsl/fsr/fsri), TP-BIT-030 /
TP-BIT-031 (F-BIT-030 / F-BIT-031: bfp), TP-BIT-032 / TP-BIT-033 (F-BIT-032 / F-BIT-033: crc32.b/h/w,
crc32c.b/h/w).

Program: dv/auto_dv/tests/gen_programs/gen_bit_draft_prog.py at the run seed (testlist `program:
{generator: ..., seed: run}`); plan(seed) is the single source of the op list, the expected rd values
(Python grev32/gorc32 from the draft Bitmanip text) and the report count; the program replays every rd
to the EOT register in plan order. Knobs: knob:imem_rvalid_delay (the item's Knobs line), varied by
the template's layers 2/3 when the build consumes it. layers_required = False: the TB has no REGIME_SET
consumer at HEAD (step 2b parked), so the layers are logged not_applied; flips to the default when step
2b lands. Fire-check per seed (fire_tp_bit_016): every report word equals the plan's reference value,
per op class (grevi, gorci, grev, gorc, the aliases), the retirement floor of the program is reached and
the end-of-test code is the pass code. declare_bins() takes the template default (the plan's bins for the group, checked against the
rendered manifest in finish(); the entry stays unwired until gen_fcov_pkg lands). Always-on checkers relied on: the ISA comparator (isa_rd through the
shim's grev/gorc reference for the draft controls, Spike for rev8 / orc.b), rvfi_proto, the bus protocol
checkers. MODULE=dv.auto_dv.tests.gen_test_bit_draft, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_bit_draft_prog as prog

ITEM_KNOBS = tuple(lib.long_knob(k) for k in ("imem_rvalid_delay",))   # TP-BIT-016 Knobs line
assert all(k in lib.REGIME_KNOBS for k in ITEM_KNOBS), f"unknown regime knob in {ITEM_KNOBS}"


class BitDraft(GenTest):
    name = "gen_test_bit_draft"
    schedulable = ITEM_KNOBS
    # Bring-up state (tier check, measured false): the build has no REGIME_SET consumer, so the layers
    # are logged not_applied; returns to the default (required) when TB Infra's step 2b lands.
    layers_required = False

    def report_count(self):
        return prog.plan(self.seed).k

    def fire_check(self):
        self.fire_tp_bit_016()

    def fire_tp_bit_016(self):
        p = prog.plan(self.seed)
        got = self.reports
        exp = p.items["TP-BIT-016"]

        def compare(name, indices):
            bad = [i for i in indices if i >= len(got) or got[i] != p.reports[i]]
            detail = f"{len(indices)} ops, {len(bad)} mismatches"
            if bad:
                i = bad[0]
                op = p.ops[i]
                seen = f"0x{got[i]:08x}" if i < len(got) else "missing"
                detail += (f"; first op {i} {op.kind} ctrl={op.ctrl} rs1=0x{op.rs1_val:08x}"
                           + (f" rs2=0x{op.rs2_val:08x}" if not op.is_imm else "")
                           + f" expected 0x{op.expect:08x} got {seen}")
            self.check(name, len(indices) > 0 and not bad, detail)

        for base, indices in exp["ops_by_base"].items():
            compare(f"fire_tp_bit_016_{base}", indices)
        compare("fire_tp_bit_016_alias", exp["alias_ops"])
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
