"""gen_test_isa_cti: plan group gen_isa_cti (dv/auto_dv/docs/gen_test_plan.md AREA ISA, control-transfer
instructions; plan version 2 generated 2026-09-03 12:43 UTC, the committed tree named by the batch-2 dispatch).

Items built (fire_tp_isa_<nnn>) and their canonical features (gen_feature_list.md Section 3): TP-ISA-015 jal
(F-ISA-015), TP-ISA-017 link value pc + length (F-ISA-017 is FOLDED into F-ISA-015, bin CG-ISA-006.cr_link.c_jal_pc2),
TP-ISA-018 jalr (F-ISA-018), TP-ISA-019 odd jalr target (F-ISA-019), TP-ISA-020 jalr rs1 == rd (F-ISA-020),
TP-ISA-023 conditional branches (F-ISA-023), TP-ISA-027 sign/unsigned boundaries (F-ISA-027), TP-ISA-053 no
instruction-address-misaligned exception (F-ISA-052).
Items NOT built (class attribute not_built, the missing component named): TP-ISA-016 (F-ISA-016) and TP-ISA-022
(F-ISA-022) need text the TB memory map does not provide (jal reach of +-1 MiB exceeds the 1 MiB PROG window of
gen_link.ld, no code page at 0, nothing below 0x1000 or in the top 2 KiB; TB Infra) and, for 016, the self-loop
exit by interrupt (IRQ_SET argument codes not rendered, gen_knobs codegen); TP-ISA-024 (F-ISA-024, ALIAS of
F-BTALU-001) is the group's marked timing item (bus records / RVFI cycle, event export); TP-ISA-026 (F-ISA-026)
needs the interrupt exit of its self-loop and text near address 0, and building its +4094/-4096 clause alone would
declare the self and wrap bins this test can never hit.
Program: the per-seed generator dv/auto_dv/tests/gen_programs/gen_isa_cti_prog.py (testlist `program: {generator:
..., seed: run}`) draws the units, registers, immediates, alignments, directions and the branch operand classes
from the run seed and stores RAW observations to GEN_MM_EOT_ADDR: the landing marker of every jump (a wrong target
skips or changes it), the link register after every jal/jalr/c.jal/c.jalr with rd != 0 (expected: the jump site's
sidecar address + the instruction length), the branch outcome vector (one bit per branch, a word per 32), misa,
and the trap handler's count and last mcause. Expected words come from the plan and the image sidecar symbols.
Red fixtures: `--red [--red-item <item>]`, one program-only deviation per built item (generator docstring); the
default red of seed 1 pins TP-ISA-017 (random.Random("1:red")).
Fire-checks: fire_tp_isa_015 (every 015 word matches; >= 500 jal, rd classes x0/x1/x5/other, both directions
near and far, both target alignments read from the image), fire_tp_isa_017 (links equal site + 4 for jal/jalr and
site + 2 for c.jal/c.jalr, every form at both site alignments), fire_tp_isa_018 (>= 500 jalr, imm classes zero/
max_pos/min_neg/pos_rand/neg_rand, rs1 from lui/addi and from a load, rd classes), fire_tp_isa_019 (at least prog.ODD_PLAN_MIN odd sums
over jalr/c.jr/c.jalr with both odd constructions landed on the even target, plus even-sum controls; a misaligned
trap would skip the landing block), fire_tp_isa_020 (jalr rd, rd, imm: old value selects the target, new value is
the link; write-to-use distances 0..3), fire_tp_isa_023 (>= 2400 branches, every outcome bit as predicted, per op
both outcomes with min(3, admissible) compare classes: beq taken and bne not-taken admit only the two equal-valued
classes), fire_tp_isa_027 (every (op, named class) observed with its outcome bit as predicted), fire_tp_isa_053
(misa.C set; >= 100 half-word-aligned targets and >= 20 odd jalr sums, alignment read from the image; branch, jal,
jalr, c.j, c.jal, c.jr, c.jalr, mret and fence.i kinds; the handler counted no trap and saw no mcause).
fire_program_verdict (no plan item, declares no bins): tohost == lib.TOHOST_PASS, retirements at the end-of-test
store >= gen_min_retired, report count == the plan's k, and the generator's byte-parity model agrees with the
linked image for every site and target label.
Clauses dropped, with the owner: the bus clauses of TP-ISA-015 (ibus request for an uncached target), TP-ISA-019
(instr_addr_o word-aligned) and TP-ISA-053 (ibus address bit 0) need the bus record export (TB Infra ASK 4); the
dret kind of TP-ISA-053 needs a debug entry (DBG_REQ codes not rendered); the M/U randomization of 015/018/023 is
out of scope (batch-2 programs stay in M-mode, C-2); TP-ISA-019's run-wide "no mcause 0" is TP-ISA-053's counter.
Always-on checkers relied on (their uvm_error fails the flow): the ISA comparator rows isa_pc, isa_pc_next,
isa_insn, isa_rd, isa_trap, isa_prv (mret and the returning handler allowed since T-102), rvfi_proto, and the bus
protocol checkers. Knobs (items' lines: imem gnt/rvalid, dmem_rvalid): schedulable = lib.TIMING_ONLY_KNOBS, nothing
pinned; declare_bins() is
not overridden: the template declares the plan bins of the eight built items (manifest rendered from this module).
MODULE=dv.auto_dv.tests.gen_test_isa_cti.

Substitution: TP-ISA-019's fire-check is written on RVFI (rvfi_pc_rdata of the next record == (rs1 + imm) & ~1); this test
proves the landing through program-visible markers on the even target instead (RVFI record export pending), so the item counts as
built on a substitute observable, listed here as such.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_isa_cti_prog as prog
from dv.auto_dv.tests.gen_programs.gen_prog_const import MISA_C_BIT
from dv.auto_dv.tests.gen_test_template import GenTest

TRANSFER_KINDS = {"branch", "jal", "jalr", "c_j", "c_jal", "c_jr", "c_jalr", "mret", "fencei"}


def _plan(test):
    """The seed's program plan, built once per test instance (the generator is the single origin of intent)."""
    if getattr(test, "_isa_cti_plan", None) is None:
        test._isa_cti_plan = prog.plan(test.seed)
    return test._isa_cti_plan


def _addr(test, symbol):
    syms = test.image.sidecar["symbols"]
    assert symbol in syms, f"GEN_TEST: program image defines no symbol {symbol}"
    return int(syms[symbol], 16)


def _half(test, symbol):
    """Half-word alignment of a code label in the linked image (the observed alignment class)."""
    return _addr(test, symbol) % 4 == 2


def _expect(test, r):
    return _addr(test, r.expect.symbol) + r.expect.add if isinstance(r.expect, prog.Sym) else r.expect


def _mismatches(test, idxs):
    p = _plan(test)
    bad = []
    for i in idxs:
        exp = _expect(test, p.reports[i])
        got = test.reports[i] if i < len(test.reports) else None
        if got != exp:
            bad.append(f"[{i}] {p.reports[i].label}: expected 0x{exp:08x} got {'none' if got is None else f'0x{got:08x}'}")
    return bad


def _bit_mismatches(test, units):
    """Branch outcome bits of `units` read from the reported window words versus the plan's outcome."""
    bad = []
    for u in units:
        idx, pos = u.bit
        if idx >= len(test.reports):
            bad.append(f"branch {u.n} ({u.form} {u.cls}): word {idx} missing")
            continue
        got = (test.reports[idx] >> pos) & 1
        if got != int(u.outcome):
            bad.append(f"branch {u.n} ({u.form} {u.cls} 0x{u.a:08x},0x{u.b:08x}): expected taken={int(u.outcome)} got {got} (word {idx} bit {pos})")
    return bad


def _words(test, item, bad):
    n = len(_plan(test).items[item])
    return f"{n} report words" + (f": {len(bad)} mismatch(es), first {bad[0]}" if bad else " all match")


class IsaCti(GenTest):
    name = "gen_test_isa_cti"
    schedulable = lib.TIMING_ONLY_KNOBS
    # Items of the plan group this test does not check, with the missing component (two-sided against the group).
    # bins this test does not guarantee per run, with the reason and its class: seed-dependent bins
    # are credited from the merged report, stimulus bins need a program change, declaration bins cannot
    # be a per-run guarantee at all
    bins_not_hit = {
        "gen_isa_branch_cg.cp_op.c_beqz":
            "stimulus: the program emits no compressed branch: gen_isa_cti_prog.py generates the 32-bit forms only",
        "gen_isa_branch_cg.cp_op.c_bnez":
            "stimulus: the program emits no compressed branch: gen_isa_cti_prog.py generates the 32-bit forms only",
        "gen_isa_branch_cg.cr_op_align.c_beqz_half":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_align.c_bnez_half":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_taken_cmp.c_beqz_no_intmin_zero":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_taken_cmp.c_beqz_no_ones_zero":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_taken_cmp.c_beqz_no_slt_ugt":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_taken_cmp.c_beqz_yes_equal":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_taken_cmp.c_bnez_no_equal":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_taken_cmp.c_bnez_yes_intmin_zero":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_taken_cmp.c_bnez_yes_ones_zero":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_branch_cg.cr_op_taken_cmp.c_bnez_yes_slt_ugt":
            "stimulus: depends on a compressed branch, which the program does not emit",
        "gen_isa_jump_cg.cp_jalr_rs1.x0":
            "stimulus: the program emits no jalr with rs1 = x0",
        "gen_isa_jump_cg.cr_jalr_rs1_imm.x0_max_pos":
            "stimulus: depends on jalr with rs1 = x0, which the program does not emit",
        "gen_isa_jump_cg.cr_jalr_rs1_imm.x0_min_neg":
            "stimulus: depends on jalr with rs1 = x0, which the program does not emit",
        "gen_isa_jump_cg.cr_jalr_rs1_imm.x0_zero":
            "stimulus: depends on jalr with rs1 = x0, which the program does not emit",
    }
    not_built = {
        "TP-ISA-016": "needs WP-9: executable code windows at address 0 and the top page for the jal wrap and extremes, and an irq-agent command to break the self-loop",
        "TP-ISA-022": "needs WP-9: executable code windows at address 0 and the top page for the jalr wrap and rs1 = x0 targets",
        "TP-ISA-024": "timing clause: bus records / RVFI cycle, event export",
        "TP-ISA-026": "needs WP-9: text near address 0 for the branch wrap and an irq-agent command to break the self-loop; the offset-extreme clause alone would declare bins the test cannot hit",
    }

    def report_count(self):
        return _plan(self).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_tp_isa_015()
        self.fire_tp_isa_017()
        self.fire_tp_isa_018()
        self.fire_tp_isa_019()
        self.fire_tp_isa_020()
        self.fire_tp_isa_023()
        self.fire_tp_isa_027()
        self.fire_tp_isa_053()

    def fire_program_verdict(self):
        p = _plan(self)
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image)
        got = self.eot_retired
        n, k = len(self.reports), p.k
        drift = [u.n for u in p.units if u.kind == "jump" and (_half(self, f"gen_j{u.n}") != u.site_half or _half(self, f"gen_t{u.n}") != u.target_half)]
        drift += [u.n for u in p.units if u.kind == "branch" and _half(self, f"gen_t{u.n}") != u.target_half]
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and n == k and not drift,
                   f"tohost code 0x{code:08x} (pass {lib.TOHOST_PASS}); retired at eot {got} (floor {floor}); reports {n} (k {k}); "
                   f"alignment model drifts from the image on {len(drift)} unit(s){' ' + str(drift[:4]) if drift else ''}")

    def fire_tp_isa_015(self):
        p = _plan(self)
        U = [u for u in p.units if u.item == prog.I015]
        bad = _mismatches(self, p.items[prog.I015])
        rd = {u.rd_class for u in U}
        dirs = {(u.fwd, u.far) for u in U}
        align = {_half(self, f"gen_t{u.n}") for u in U}
        ok = not bad and len(U) >= prog.JAL_MIN and rd == set(prog.W4_RD_JAL) and len(dirs) == 4 and align == {True, False}
        self.check("fire_tp_isa_015", ok, f"{len(U)} jal (>= {prog.JAL_MIN}), rd classes {sorted(rd)}, (fwd, far) {sorted(dirs)}, "
                   f"target half-aligned {sorted(align)}; {_words(self, prog.I015, bad)}")

    def fire_tp_isa_017(self):
        p = _plan(self)
        U = [u for u in p.units if u.item == prog.I017]
        bad = _mismatches(self, p.items[prog.I017])
        seen = {(u.form, _half(self, f"gen_j{u.n}")) for u in U}
        want = {(f, h) for f in prog.JUMP_FORMS_017 for h in (True, False)}
        ok = not bad and seen == want and all(u.rd != 0 for u in U)
        self.check("fire_tp_isa_017", ok, f"{len(U)} links (site + 4 for jal/jalr, site + 2 for c.jal/c.jalr), form x site alignment "
                   f"{len(seen)}/{len(want)}; {_words(self, prog.I017, bad)}")

    def fire_tp_isa_018(self):
        p = _plan(self)
        U = [u for u in p.units if u.item == prog.I018]
        bad = _mismatches(self, p.items[prog.I018])
        imm = {u.imm_class for u in U}
        rd = {u.rd_class for u in U}
        load = {u.from_load for u in U}
        ok = not bad and len(U) >= prog.JALR_MIN and imm == set(prog.W6_JALR_IMM) and rd == set(prog.W4_RD_JALR) and load == {True, False}
        self.check("fire_tp_isa_018", ok, f"{len(U)} jalr (>= {prog.JALR_MIN}), imm classes {sorted(imm)}, rd classes {sorted(rd)}, "
                   f"rs1 from load {sorted(load)}; {_words(self, prog.I018, bad)}")

    def fire_tp_isa_019(self):
        p = _plan(self)
        U = [u for u in p.units if u.item == prog.I019]
        odd = [u for u in U if not u.control]
        bad = _mismatches(self, p.items[prog.I019])
        forms = {u.form for u in odd}
        cons = {prog.odd_construction(u) for u in odd if u.form == "jalr"}
        ok = not bad and len(odd) >= prog.ODD_PLAN_MIN and forms == {"jalr", "c_jr", "c_jalr"} and cons == {"odd_rs1", "odd_imm"} and len(U) > len(odd)
        self.check("fire_tp_isa_019", ok, f"{len(odd)} odd sums (>= {prog.ODD_PLAN_MIN}) over {sorted(forms)}, constructions {sorted(cons)}, "
                   f"{len(U) - len(odd)} even-sum controls, every landing on the even target; {_words(self, prog.I019, bad)}")

    def fire_tp_isa_020(self):
        p = _plan(self)
        U = [u for u in p.units if u.item == prog.I020]
        bad = _mismatches(self, p.items[prog.I020])
        gaps = {u.gap for u in U}
        ok = not bad and len(U) >= prog.N020_MIN and gaps == {0, 1, 2, 3} and all(u.rd == u.rs1 != 0 for u in U)
        self.check("fire_tp_isa_020", ok, f"{len(U)} jalr rd, rd, imm (>= {prog.N020_MIN}), write-to-use gaps {sorted(gaps)}; "
                   f"{_words(self, prog.I020, bad)}")

    def fire_tp_isa_023(self):
        p = _plan(self)
        B = [u for u in p.units if u.item == prog.I023]
        bad = _bit_mismatches(self, B)
        short = []
        for op in prog.BR_OPS:
            for taken in (True, False):
                got = {u.cls for u in B if u.form == op and u.outcome == taken}
                need = min(3, len(prog.admissible_classes(op, taken)))
                if len(got) < need:
                    short.append(f"{op}/taken={int(taken)}:{len(got)}<{need}")
        ok = not bad and len(B) >= prog.BR023_MIN and not short
        self.check("fire_tp_isa_023", ok, f"{len(B)} branches (>= {prog.BR023_MIN}), {sum(u.outcome for u in B)} taken; per op and outcome "
                   f"min(3, admissible) classes{' short ' + str(short) if short else ' met'}; outcome bits"
                   + (f": {len(bad)} mismatch(es), first {bad[0]}" if bad else " all as predicted"))

    def fire_tp_isa_027(self):
        p = _plan(self)
        B = [u for u in p.units if u.item == prog.I027]
        bad = _bit_mismatches(self, B)
        seen = {(u.form, u.cls) for u in B if u.cls != "rand"}
        want = {(op, c) for op in prog.BR_OPS for c in prog.NAMED_CLASSES}
        ok = not bad and seen >= want
        self.check("fire_tp_isa_027", ok, f"{len(B)} boundary-table branches, (op, class) {len(seen & want)}/{len(want)} with the outcome "
                   f"recorded; outcome bits" + (f": {len(bad)} mismatch(es), first {bad[0]}" if bad else " all as predicted"))

    def fire_tp_isa_053(self):
        p = _plan(self)
        bad = _mismatches(self, p.items[prog.I053])
        misa_idx = p.items[prog.I053][0]
        misa = self.reports[misa_idx] if misa_idx < len(self.reports) else 0
        half = sum(1 for u in p.units if u.kind == "jump" and _half(self, f"gen_t{u.n}"))
        half += sum(1 for u in p.units if u.kind == "branch" and u.outcome and _half(self, f"gen_t{u.n}"))
        kinds = {u.form for u in p.units if u.kind == "jump"} | ({"branch"} if any(u.kind == "branch" for u in p.units) else set())
        ok = (not bad and (misa >> MISA_C_BIT) & 1 and half >= prog.HALF_TARGETS_MIN and p.n_odd_sums >= prog.ODD_SUMS_MIN
              and kinds == TRANSFER_KINDS)
        self.check("fire_tp_isa_053", ok, f"misa 0x{misa:08x} (C bit {(misa >> MISA_C_BIT) & 1}); {half} half-word-aligned targets "
                   f"(>= {prog.HALF_TARGETS_MIN}) and {p.n_odd_sums} odd jalr sums (>= {prog.ODD_SUMS_MIN}) over {sorted(kinds)}; "
                   f"handler count and last mcause; {_words(self, prog.I053, bad)}")


@cocotb.test()
async def gen_test_isa_cti(dut):
    await IsaCti(dut).run()
