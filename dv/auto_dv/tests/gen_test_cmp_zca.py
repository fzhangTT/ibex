"""gen_test_cmp_zca: plan group gen_cmp_zca (dv/auto_dv/docs/gen_test_plan.md AREA CMP, plan version 2 of
2026-09-03 12:43 UTC, the committed plan and tree named by the batch-2 dispatch).

Items and canonical features (gen_feature_list.md Section 3), all 21 built: TP-CMP-001 expansion / PC increment /
32-bit instructions at 2-byte boundaries (F-CMP-001), 002 c.addi4spn (F-CMP-002), 004 c.lw/c.sw (F-CMP-004), 005
c.lwsp/c.swsp (F-CMP-005), 008 c.addi/c.nop (F-CMP-008), 010 c.jal/c.j (F-CMP-010), 011 c.jal link and target extremes
(F-CMP-011), 012 c.li (F-CMP-012), 014 c.lui (F-CMP-014), 016 c.addi16sp (F-CMP-016), 017 c.addi16sp illegal /
extremes / sp wrap (F-CMP-017), 018 c.srli/c.srai (F-CMP-018), 020 c.andi (F-CMP-020), 021 c.sub/c.xor/c.or/c.and
(F-CMP-021), 023 c.beqz/c.bnez (F-CMP-023), 024 c.slli (F-CMP-024), 026 c.mv (F-CMP-026), 028 c.jr (F-CMP-028), 030
c.add (F-CMP-030), 032 c.jalr (F-CMP-032), 033 c.ebreak (F-CMP-033 is an ALIAS of F-ISA-034, the canonical feature).
not_built = {} (every group item has a fire_tp method).

Program: the per-seed generator dv/auto_dv/tests/gen_programs/gen_cmp_zca_prog.py (testlist `program: {generator:
..., seed: run}`) draws every Zca form's operands, registers, immediates, layout and the filler instructions around
them from the run seed, computes every expected report word from the Zca specification semantics, and stores RAW
observations to GEN_MM_EOT_ADDR: the destination register after each compressed form and, beside it, the same
operation's 32-bit form on another register (the "versus its 32-bit form" evidence); the memory word after each
c.sw/c.swsp read back by the compressed load and by a 32-bit lw; a trace register that every reached block shifts a
mark into (control transfers, both target alignments, exact +2046/-2048 and +254/-256 offsets); mcause/mtval/mepc read
by the trap handler on c.ebreak and on the illegal c.addi16sp nzimm = 0 halfword. Facts that depend on the link
address (link registers, mepc, the sp value a c.swsp x2 stored) are checked as relations between two raw report words
(an auipc anchor report and the observed value: value == anchor + delta), never against a re-typed address.
Red fixtures: `--red [--red-item <item>]` makes the program deviate on one intent of that item (an immediate or operand
value, a swapped form or branch sense, a moved store immediate, a c.nop inserted between an anchor and its anchored
instruction, c.jr emitted as c.jalr) while the expectation keeps the true program, so exactly that item's fire-check
fails; without --red-item the seed draws the item.

Fire-checks, one per item over the report words the plan attributes to it (every word equal to its absolute or
anchor-relative expectation, and the item's directed floor present in the seed's plan): fire_tp_cmp_001 (PC delta of
4 + 2k over k compressed ops, 32-bit auipc/xori at pc[1] = 1, anchor alignment), 002 (every rd', nzuimm 4/1020/rand),
004 (every rs1' and rd', uimm 0/124/rand, c.lw and lw read the stored word), 005 (rs2 x0/x1/x2/low/high incl. the
stored sp and the stored zero, rd x1/x2/low/high, uimm 0/252/rand), 008 (every rd, imm -32/-1/1/31/rand), 010 (c.j
forward/backward, c.jal call and c.jr return, link = pc + 2, both target alignments), 011 (+2046 and -2048 taken by
c.jal and c.j, link = pc + 2), 012 (every rd, imm classes incl. 0), 014 (rd not x0/x2, nzimm 1/31/-32/-1/rand), 016
(nzimm -512/496/16/-16/rand without wrap, result used as a c.lwsp base), 017 (nzimm = 0 traps with mcause 2, mtval
0x6101, mepc = its pc; extremes; wrap for -512/-16/rand and 496/16/rand), 018 (both ops, shamt 1/31/rand, msb-set/
msb-clear/all-ones/zero operands, sign fill), 020 (every rd', imm classes), 021 (four ops over every rd' and rs2',
rd' == rs2', c.sub wrap), 023 (both ops taken and not taken, forward/backward, +254/-256 taken, offset 0 not taken,
every rs1'), 024 (every rd, both rd groups, shamt classes), 026 (every rd, rd == rs2), 028 (every rs1 in x1..x31,
both target alignments, no x1 write), 030 (every rd, wrap, rd == rs2), 032 (every rs1 incl. x1, link = pc + 2,
target from the old rs1), 033 (c.ebreak at both alignments: mcause 3, mtval 0, mepc = its pc, execution resumes at
pc + 2). fire_program_verdict (not a plan item, declares no bins) asserts tohost == lib.TOHOST_PASS, retirements at
the end-of-test store >= the program's gen_min_retired floor, report count == the plan's k.

Clauses NOT asserted here, with the missing channel named (they rest on the always-on checkers whose uvm_error the
flow collects: the ISA comparator rows isa_insn/isa_rd/isa_mem/isa_pc/isa_pc_next/isa_trap/isa_csr, rvfi_proto, the
bus protocol checkers ibus_proto/dbus_proto): TP-CMP-001 rvfi_insn[31:16] = 0 and rvfi_trap = 0 per record and the
>= 500 straddling-retirement count (RVFI record export, TB Infra ASK 5); 004/005 rvfi_mem_wmask and the per-record
address (record export); 008 c.nop rvfi_rd_addr = 0 (record export; c.nop's PC advance is asserted by the 001 probes);
011 the c.j-to-self loop broken by a timer interrupt (needs IRQ_SET bridge codes, not rendered; knob irq_regime is not
schedulable here); 017 and 033 rvfi_trap = 1 / rvfi_insn = 0x9002 per record (record export) and the U-mode variants
(M-mode group); 033 the debug case (dcsr.ebreakm/ebreaku = 1 -> debug entry, dpc = pc, dcsr.cause = 1) needs
debug-mode entry (DBG_REQ bridge codes not rendered, knob debug_req_regime not schedulable). The plan's stimulus size
is >= 3000 retired instructions per seed with the per-form floors governing (the seed-1 program retires about 3800), asserted by fire_program_verdict's retirement floor.
Dropped clause (program-shaped, owner named): TP-CMP-028 odd c.jr targets (bit 0 set) are not drawn, because the DUT's
rvfi_pc_wdata keeps bit 0 (bug candidate B13, gen_bug_log.md; the plan's 028 fire-check masks bit 0 for that reason);
the always-on isa_pc_next comparator row counts that bit as a documented exception and B13's xfail item owns the bug.
The handler's mtval read after c.ebreak is asserted as 0 (doc cs_registers.rst "for all other exceptions mtval is 0",
the plan's TP-CMP-033 value); the DUT and the model both report 0, so the isa_rd / isa_mem rows agree on it.
Knobs: schedulable = lib.TIMING_ONLY_KNOBS (the items' imem/dmem gnt and rvalid delays and imem_outstanding_cap);
nothing is pinned; declare_bins() is not overridden: the template declares the plan bins of the 21
items the fire_tp_cmp_* methods name (the manifest is rendered from this module). MODULE=dv.auto_dv.tests.gen_test_cmp_zca.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_cmp_zca_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest

MASK32 = prog.MASK32


def _plan(test):
    """The seed's program plan, built once per test instance: the generator is the single origin of the
    program's intent and of the expected report words."""
    if getattr(test, "_cmp_zca_plan", None) is None:
        test._cmp_zca_plan = prog.plan(test.seed)
    return test._cmp_zca_plan


def _expected(test, r):
    """Expected value of one report word: absolute, or relative to another raw report word (an anchor)."""
    if isinstance(r.expect, prog.Rel):
        if r.expect.base >= len(test.reports):
            return None
        return (test.reports[r.expect.base] + r.expect.delta) & MASK32
    return r.expect


def _compare(test, item, detail):
    """(ok, detail) of one item: every report word the plan attributes to it equals its expectation; anchor words
    (expect None) are counted, not compared."""
    p = _plan(test)
    idxs = p.items[item]
    bad = []
    compared = 0
    for i in idxs:
        r = p.reports[i]
        if r.expect is None:
            continue
        compared += 1
        exp = _expected(test, r)
        if i >= len(test.reports) or exp is None or test.reports[i] != exp:
            bad.append((i, r, exp))
    text = f"{len(idxs)} report words, {compared} compared ({detail})"
    if bad:
        i, r, exp = bad[0]
        got = f"0x{test.reports[i]:08x}" if i < len(test.reports) else "missing"
        want = f"0x{exp:08x}" if exp is not None else "anchor missing"
        text += f": {len(bad)} mismatch(es), first idx={i} {r.label} expected {want} got {got}"
    else:
        text += " all match"
    return bool(idxs) and compared > 0 and not bad, text


class CmpZca(GenTest):
    name = "gen_test_cmp_zca"
    schedulable = lib.TIMING_ONLY_KNOBS
    # every item of the plan group has a fire_tp method (two-sided against the group by the structure check)
    # bins this test does not guarantee per run, with the reason and its class (gen_test_template.bins_not_hit)
    bins_not_hit = {
        "gen_cmp_imm_edges_cg.cp_cj_off.self":
            "stimulus: this program emits no c.j or c.jal with offset 0, so the bin is 0 of 40 in the wave at 4017573 (gen_wave_4017573/gen_wave_nothit.txt); entry-scoped, not exclusive with termination: a zero-offset compressed jump is the park-here idiom that other entries retire (398 merged hits in round 0, gen_round_0/gen_grpinfo.txt)",
        "gen_cmp_zca_cg.cr_insn_rdfull.c_lwsp_x3_7":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zca_cg.cr_insn_rdfull.c_lwsp_x8_15":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
    }
    not_built = {}

    def report_count(self):
        return _plan(self).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_tp_cmp_001()
        self.fire_tp_cmp_002()
        self.fire_tp_cmp_004()
        self.fire_tp_cmp_005()
        self.fire_tp_cmp_008()
        self.fire_tp_cmp_010()
        self.fire_tp_cmp_011()
        self.fire_tp_cmp_012()
        self.fire_tp_cmp_014()
        self.fire_tp_cmp_016()
        self.fire_tp_cmp_017()
        self.fire_tp_cmp_018()
        self.fire_tp_cmp_020()
        self.fire_tp_cmp_021()
        self.fire_tp_cmp_023()
        self.fire_tp_cmp_024()
        self.fire_tp_cmp_026()
        self.fire_tp_cmp_028()
        self.fire_tp_cmp_030()
        self.fire_tp_cmp_032()
        self.fire_tp_cmp_033()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image, _plan(self).min_retired)
        got = self.eot_retired
        n, k = len(self.reports), _plan(self).k
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and n == k,
                   f"tohost code 0x{code:08x} (pass {lib.TOHOST_PASS}); retired at eot {got} (floor {floor}); reports {n} (k {k})")

    def fire_item(self, item, detail):
        s = _plan(self).summary
        ok, text = _compare(self, item, f"{detail}; units {s['items'][item]} words")
        self.check("fire_tp_cmp_" + item[-3:], ok, text)

    def fire_tp_cmp_001(self):
        self.fire_item(prog.I001, "pc delta 4 + 2k per probe, 32-bit auipc/xori at pc[1] = 1, anchor aligned")

    def fire_tp_cmp_002(self):
        self.fire_item(prog.I002, "c.addi4spn every rd', nzuimm 4/1020/rand, 32-bit twins")

    def fire_tp_cmp_004(self):
        self.fire_item(prog.I004, "c.sw then c.lw and lw read-back, every rs1'/rd', uimm 0/124/rand")

    def fire_tp_cmp_005(self):
        self.fire_item(prog.I005, "c.swsp/c.lwsp rs2 x0/x1/x2/low/high, rd x1/x2/low/high, uimm 0/252/rand")

    def fire_tp_cmp_008(self):
        self.fire_item(prog.I008, "c.addi every rd, imm -32/-1/1/31/rand, c.nop between")

    def fire_tp_cmp_010(self):
        self.fire_item(prog.I010, "c.j fwd/bwd traces, c.jal link pc + 2 and c.jr return, both target alignments")

    def fire_tp_cmp_011(self):
        self.fire_item(prog.I011, "c.jal/c.j at +2046 and -2048 taken, link pc + 2")

    def fire_tp_cmp_012(self):
        self.fire_item(prog.I012, "c.li every rd, imm -32/-1/0/1/31/rand")

    def fire_tp_cmp_014(self):
        self.fire_item(prog.I014, "c.lui rd not x0/x2, nzimm 1/31/-32/-1/rand")

    def fire_tp_cmp_016(self):
        self.fire_item(prog.I016, "c.addi16sp nzimm -512/496/16/-16/rand no wrap, result used as c.lwsp base")

    def fire_tp_cmp_017(self):
        self.fire_item(prog.I017, "nzimm 0 illegal (mcause 2, mtval 0x6101, mepc), extremes, sp wrap both ways")

    def fire_tp_cmp_018(self):
        self.fire_item(prog.I018, "c.srli/c.srai every rd', shamt 1/31/rand, msb/all-ones/zero operands")

    def fire_tp_cmp_020(self):
        self.fire_item(prog.I020, "c.andi every rd', imm -32/-1/0/1/31/rand")

    def fire_tp_cmp_021(self):
        self.fire_item(prog.I021, "c.sub/c.xor/c.or/c.and every rd' and rs2', rd' == rs2', c.sub wrap")

    def fire_tp_cmp_023(self):
        self.fire_item(prog.I023, "c.beqz/c.bnez taken and not taken, fwd/bwd, +254/-256, self, every rs1'")

    def fire_tp_cmp_024(self):
        self.fire_item(prog.I024, "c.slli every rd (both groups), shamt 1/31/rand")

    def fire_tp_cmp_026(self):
        self.fire_item(prog.I026, "c.mv every rd (both groups), rd == rs2")

    def fire_tp_cmp_028(self):
        self.fire_item(prog.I028, "c.jr every rs1 in x1..x31, both alignments, x1 not written (odd targets not drawn: B13)")

    def fire_tp_cmp_030(self):
        self.fire_item(prog.I030, "c.add every rd (both groups), wrap, rd == rs2")

    def fire_tp_cmp_032(self):
        self.fire_item(prog.I032, "c.jalr every rs1 incl x1, link pc + 2, target from the old rs1, c.jr return")

    def fire_tp_cmp_033(self):
        self.fire_item(prog.I033, "c.ebreak at both alignments: mcause 3, mtval 0, mepc = pc, resume at pc + 2")


@cocotb.test()
async def gen_test_cmp_zca(dut):
    await CmpZca(dut).run()
