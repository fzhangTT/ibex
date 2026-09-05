"""gen_test_isa_alu: plan group gen_isa_alu (dv/auto_dv/docs/gen_test_plan.md AREA ISA, Version 2 generated 2026-09-03
12:43 UTC, read at the batch-2 dispatch HEAD).

Items and canonical features (gen_feature_list.md Section 3; none of these ids is an alias or folded), all ten built on
the program report channel: TP-ISA-001 I-type ALU (F-ISA-001), TP-ISA-002 addi wrap (F-ISA-002), TP-ISA-003 slti/sltiu
boundaries (F-ISA-003), TP-ISA-004 HINTs with rd = x0 (F-ISA-004, F-ISA-051), TP-ISA-005 lui/auipc (F-ISA-005),
TP-ISA-006 lui/auipc extremes and PC wrap (F-ISA-006), TP-ISA-007 R-type ALU (F-ISA-007), TP-ISA-008 add/sub wrap
(F-ISA-008), TP-ISA-009 slt/sltu boundaries (F-ISA-009), TP-ISA-052 writes to x0 discarded (F-ISA-051).
Expected: pass for every item (no expected-fail or informational item in the group).

Program: the per-seed generator dv/auto_dv/tests/gen_programs/gen_isa_alu_prog.py (testlist `program: {generator: ...,
seed: run}`) draws the operations, operand classes, immediates, registers, order, fillers and PC alignments from the
run seed, computes every expected report word from the RV32I text (rv32.adoc; zca.adoc for the compressed HINT code
points) and stores the RAW observations to GEN_MM_EOT_ADDR: rd after every observable op, the rd of the x0 reader that
follows every HINT or x0 writer, the minstret delta over every block of 64 HINTs, the mcountinhibit read-back of the
TP-ISA-004 precondition. auipc words are checked against the site's linked address (global labels gen_u<n>, read
from the image sidecar), so no pc is re-typed; fire_program_layout proves the generator's byte-exact layout model
against the linked symbols. Red fixtures: `--red [--red-item <item>]` makes the program deviate on one intent of that
item (another mnemonic, a non-wrapping or flipped immediate, a HINT writing the reader's source register, a hint-block
delta emitted with add, an x0 reader emitted reading a live register or as a never-taken bne) while the expectation
keeps the true program, so exactly that item's fire-check fails; without --red-item the seed draws the item.

Fire-checks, one primary compare per item over the report words the plan attributes to it (named exactly
fire_tp_isa_<nnn>; a `_floor` sub-check asserts the per-seed coverage the item's "every ..." clauses demand, computed
from the observed and matched words): 001 six opcodes x seven rs1 classes and x seven imm classes, rs1 == rd both
ways, every result class, >= 2000 ops; 002 both wrap signs with the sign flip visible in the word and the pinned pairs;
003 every cp_slt_case; 004 every cp_hint_class in a HINT/reader pair (reader rs1 = x0 and rs2 = x0 forms, distance
1..3), minstret delta == 65 per 64-HINT block (64 HINTs plus the first csrr, plan TP-ISA-004 / rtl-arch T-053),
mcountinhibit written 0 and read back 0; 005 lui and auipc at both pc[1] values with every imm20
class and >= 500 each; 006 lui 0xFFFFF -> 0xFFFFF000 and lui 0 -> 0, auipc imm 0 == pc at both alignments, auipc
address-space wrap (the 33-bit sum pc + sext(imm << 12) past 2^32: imm20 0x7FFFF from pc >= 0x80001000), carry-out
(word < pc, a negative immediate) and no carry-out, each at both alignments; 007 seven ops x four sign pairs, x rs1/rs2
classes, x five register relations, equal operands, every result class, >= 3000 ops; 008 add carry, add positive and
negative signed overflow, sub borrow and sub signed overflow, each confirmed in the word; 009 slt and sltu each with
equal operands, (INT_MIN, INT_MAX), (INT_MIN, 1) and rs1 = x0 with rs2 zero and nonzero; 052 every cp_writer_class
(alu_imm, shift, alu_reg, lui_auipc, load, csrr, jal, jalr, mul, mulh, div_rem, bit_1cyc, bit_2cyc, cmp_hint) with an
x0 reader of each form (add rd,x0,x0; sw x0 read back; beq x0,x0) reporting 0 / the taken-branch value.
Vacuous compares (rd = x0 forms of 001/005/007) and degenerate operands (and/andi with 0, or/ori with all ones) are
counted apart in the details; they are not observations. fire_program_verdict (not a plan item, declares no bins):
tohost == lib.TOHOST_PASS, retirements at the end-of-test store >= gen_min_retired, report count == the plan's k.

Dropped clauses (listed per the batch-1 remediation), each resting on the always-on checkers whose uvm_error the flow
collects (the ISA comparator rows isa_insn, isa_rd, isa_pc, isa_trap, isa_csr; rvfi_proto; dbus_proto) until the
named channel lands: (a) the RVFI-record form of every fire-check (rvfi_trap = 0, rvfi_rd_addr = 0 / rvfi_rd_wdata = 0
of a HINT, rvfi_rs*_rdata = 0 of the reader, per-record class counting from rvfi_rs1_rdata) needs the RVFI record
export (plan Section 6 item 5, TB Infra ASK 5); this test observes the same facts through register state.
(b) TP-ISA-052 "the sw x0 stores 0 on the data bus" is a bus fact (bus record export, ASK 4); the test reads the stored
word back through memory instead. (c) TP-ISA-006 "auipc at pc >= 0xFFFFF000" and "lui/auipc from the low page
(pc < 0x1000)": the program window is MEMORY_MAP boot_page + prog_size (0x80000000 + 1 MiB, gen_link.ld PROG), so no
program text can run in the high or low page until the TB memory map offers those windows (WP-9, owner TB Infra / DV
Lead), and the CG-ISA-004 bins cp_pc_region.high / cp_pc_region.low stay declared not_hit; the address-space wrap that the
plan's cp_wrap means (the 33-bit sum pc + sext(imm << 12) outside [0, 2^32)) needs no such page: from any pc >= 0x80001000
an auipc with imm20 0x7FFFF leaves the space, so the program places one per alignment past the first 4 KiB and the fire
check confirms the wrap from the linked pc; the negative-immediate cases carry out of the 32-bit add (word < pc) without
leaving the space and are the plan's cp_wrap.no. (d) The "U vs M
mode 50/50 after an mret" randomization of TP-ISA-001/004/007: batch-2 programs stay in M-mode by design (the C-2 PMP
prologue and mret return belong to the batch-3 privilege groups). (e) TP-ISA-004 dummy_instr_en = 0 is the cpuctrlsts
reset value (doc/03_reference/cs_registers.rst) and is neither written nor read back: the flow's standalone Spike check
(gen_program.py --spike-check) has no cpuctrlsts and would trap on the read, so the precondition rests on reset.
Knobs (the items' Knobs lines: imem_rvalid_delay, imem_gnt_delay, dmem_rvalid_delay): schedulable = lib.TIMING_ONLY_KNOBS;
nothing is pinned.
declare_bins() is not overridden: the template declares the plan bins of the ten items the fire_tp_isa_* methods name
(the manifest dv/auto_dv/fcov_expectations/gen_test_isa_alu.fcov.yaml is rendered from this module).
MODULE=dv.auto_dv.tests.gen_test_isa_alu.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_isa_alu_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest

M = prog.M


def _plan(test):
    """The seed's program plan, built once per test instance: the generator is the single origin of the program's
    intent and of the expected report words."""
    if getattr(test, "_isa_alu_plan", None) is None:
        test._isa_alu_plan = prog.plan(test.seed)
    return test._isa_alu_plan


def _symbols(test):
    if getattr(test, "_isa_alu_syms", None) is None:
        test._isa_alu_syms = {k: int(v, 16) for k, v in test.image.sidecar["symbols"].items()}
    return test._isa_alu_syms


def _expect(test, r):
    """Expected word of a report (auipc words depend on the site's linked address)."""
    if r.kind == "auipc":
        return prog.u_value("auipc", r.imm, _symbols(test)[r.label])
    return r.expect


def _word_ok(test, r, got):
    return got == _expect(test, r)


def _got(test, i):
    return test.reports[i] if i < len(test.reports) else None


def _compare(test, item, detail):
    """(ok, detail) of one item: every report word the plan attributes to it matches its expectation."""
    p = _plan(test)
    idxs = p.items[item]
    bad = [i for i in idxs if _got(test, i) is None or not _word_ok(test, p.reports[i], _got(test, i))]
    text = f"{len(idxs)} report words ({detail})"
    if bad:
        i, r = bad[0], p.reports[bad[0]]
        g = _got(test, i)
        text += (f": {len(bad)} mismatch(es), first idx={i} {r.text} expected 0x{_expect(test, r):08x} got "
                 + (f"0x{g:08x}" if g is not None else "missing"))
    else:
        text += " all match"
    return bool(idxs) and not bad, text


def _matched(test, item):
    """Units of the item whose every report word matched (the floors are asserted over observations, never intent)."""
    p = _plan(test)
    out = []
    for o in p.ops:
        if o.item == item and o.ridx and all(_got(test, i) is not None and _word_ok(test, p.reports[i], _got(test, i)) for i in o.ridx):
            out.append(o)
    return out


def _missing(sets):
    """Text of the (name, wanted, got) floor triples that are incomplete."""
    return "; ".join(f"{n} missing {sorted(set(w) - set(g))}" for n, w, g in sets if not set(w) <= set(g))


def _pc(test, o):
    return _symbols(test)[o.label]


class IsaAlu(GenTest):
    name = "gen_test_isa_alu"
    schedulable = lib.TIMING_ONLY_KNOBS
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    # bins of built items this test cannot hit until WP-9 lands (code windows at address 0 and the top page)
    bins_not_hit = {
        "gen_isa_alu_reg_cg.cr_slt_boundary.slt_all_ones_int_max":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.slt_int_max_all_ones":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.slt_int_min_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_all_ones_int_max":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_all_ones_int_min":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_all_ones_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_int_max_one":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_int_min_all_ones":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_one_int_max":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_one_int_min":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_one_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_zero_int_max":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_alu_reg_cg.cr_slt_boundary.sltu_zero_int_min":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.bit_1cyc_rs1_zero":
            "stimulus: the program never places this writer class immediately before a retirement that reads x0 through the named operand (cp_x0_read samples the next retirement, so the pair must be adjacent)",
        "gen_isa_hint_x0_cg.cr_writer_read.bit_1cyc_rs2_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.bit_2cyc_none":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.bit_2cyc_rs1_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.bit_2cyc_rs2_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.cmp_hint_none":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.cmp_hint_rs1_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.cmp_hint_rs2_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.csrr_rs2_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.div_rem_none":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.div_rem_rs1_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.div_rem_rs2_zero":
            "stimulus: the program never places this writer class immediately before a retirement that reads x0 through the named operand (cp_x0_read samples the next retirement, so the pair must be adjacent)",
        "gen_isa_hint_x0_cg.cr_writer_read.jal_rs1_zero":
            "stimulus: the program never places this writer class immediately before a retirement that reads x0 through the named operand (cp_x0_read samples the next retirement, so the pair must be adjacent)",
        "gen_isa_hint_x0_cg.cr_writer_read.jal_rs2_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.jalr_none":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.jalr_rs1_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.jalr_rs2_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.load_none":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.load_rs1_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.load_rs2_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.mul_none":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.mul_rs1_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_hint_x0_cg.cr_writer_read.mul_rs2_zero":
            "stimulus: the program never places this writer class immediately before a retirement that reads x0 through the named operand (cp_x0_read samples the next retirement, so the pair must be adjacent)",
        "gen_isa_hint_x0_cg.cr_writer_read.mulh_rs1_zero":
            "stimulus: the program never places this writer class immediately before a retirement that reads x0 through the named operand (cp_x0_read samples the next retirement, so the pair must be adjacent)",
        "gen_isa_hint_x0_cg.cr_writer_read.mulh_rs2_zero":
            "stimulus: the program never places this writer class immediately before a retirement that reads x0 through the named operand (cp_x0_read samples the next retirement, so the pair must be adjacent)",
        "gen_isa_hint_x0_cg.cr_writer_read.shift_rs2_zero":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_isa_lui_auipc_cg.cp_pc_region.high":
            "needs WP-9: no executable code in the top page",
        "gen_isa_lui_auipc_cg.cp_pc_region.low":
            "needs WP-9: no executable code below 0x1000",
    }
    not_built = {}

    def report_count(self):
        return _plan(self).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_program_layout()
        self.fire_tp_isa_001()
        self.fire_tp_isa_002()
        self.fire_tp_isa_003()
        self.fire_tp_isa_004()
        self.fire_tp_isa_005()
        self.fire_tp_isa_006()
        self.fire_tp_isa_007()
        self.fire_tp_isa_008()
        self.fire_tp_isa_009()
        self.fire_tp_isa_052()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image, _plan(self).min_retired)
        got = self.eot_retired
        n, k = len(self.reports), _plan(self).k
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and n == k,
                   f"tohost code 0x{code:08x} (pass {lib.TOHOST_PASS}); retired at eot {got} (floor {floor}); reports {n} (k {k})")

    def fire_program_layout(self):
        """The generator's byte-exact layout model equals the linked image: _start word-aligned, every lui/auipc site at
        _start + its modeled offset (the alignment floors of 005/006 rest on this model)."""
        p, syms = _plan(self), _symbols(self)
        start = syms.get("_start")
        bad = [(l, off) for l, off in p.sites.items() if syms.get(l) != (start or 0) + off]
        self.check("fire_program_layout", start is not None and start % 4 == 0 and not bad,
                   f"_start 0x{start or 0:08x}, {len(p.sites)} labeled sites, {len(bad)} off-model" + (f", first {bad[0]}" if bad else ""))

    def fire_tp_isa_001(self):
        p = _plan(self)
        ok, detail = _compare(self, prog.I001, "I-type ALU ops, operand classes")
        self.check("fire_tp_isa_001", ok, detail)
        obs = [o for o in _matched(self, prog.I001) if o.rd]
        allv = [o for o in p.ops if o.item == prog.I001]
        sets = []
        for op in prog.IMM_OPS:
            r = [o for o in obs if o.op == op]
            sets += [(f"{op} rs1 class", prog.RS_CLASSES, {o.tags['rs1_cls'] for o in r}),
                     (f"{op} imm class", prog.IMM_CLASSES, {o.tags['imm_cls'] for o in r}),
                     (f"{op} rs1==rd", (True, False), {o.tags['rs1_eq_rd'] for o in r})]
        sets.append(("result class", prog.RESULT_CLASSES, {prog.result_class(prog.alu_i(o.op, o.a, o.imm)) for o in obs}))
        miss = _missing(sets)
        vac = sum(1 for o in allv if o.rd == 0)
        deg = sum(1 for o in obs if prog.degenerate(o))
        self.check("fire_tp_isa_001_floor", not miss and len(allv) >= prog.N_IMM_MIN,
                   f"{len(allv)} I-type ops (floor {prog.N_IMM_MIN} over every plan op), {len(obs)} observed; {vac} rd=x0 vacuous and {deg} degenerate ops are inside the floor but excluded from the value compare"
                   + (f"; {miss}" if miss else "; every op x rs1 class, op x imm class, rs1==rd and result class seen"))

    def fire_tp_isa_002(self):
        ok, detail = _compare(self, prog.I002, "addi wrap windows and pinned pairs")
        self.check("fire_tp_isa_002", ok, detail)
        obs = _matched(self, prog.I002)
        flips = {}
        for o in obs:
            got = _got(self, o.ridx[0])
            if o.tags["wrap"] != "none" and (prog.s32(o.a) < 0) != (prog.s32(got) < 0) and (prog.s32(o.a) < 0) == (o.imm < 0):
                flips[o.tags["wrap"]] = flips.get(o.tags["wrap"], 0) + 1
        pinned = {(o.a, o.imm) for o in obs} >= {(prog.INT_MAX, 1), (prog.INT_MIN, -1)}
        self.check("fire_tp_isa_002_floor", flips.get("pos", 0) > 0 and flips.get("neg", 0) > 0 and pinned,
                   f"sign-flipping addi observed: pos {flips.get('pos', 0)}, neg {flips.get('neg', 0)} of {len(obs)}; pinned pairs {pinned}")

    def fire_tp_isa_003(self):
        ok, detail = _compare(self, prog.I003, "slti/sltiu boundary table")
        self.check("fire_tp_isa_003", ok, detail)
        obs = _matched(self, prog.I003)
        want = ("eq", "slti_intmin_0", "slti_0_neg", "sltiu_imm_m1", "sltiu_seqz", "sltiu_ones_m1")
        miss = _missing([("slt case", want, {o.tags['case'] for o in obs}),
                         ("eq op", ("slti", "sltiu"), {o.op for o in obs if o.tags['case'] == 'eq'})])
        self.check("fire_tp_isa_003_floor", not miss, f"{len(obs)} compares observed" + (f"; {miss}" if miss else "; every cp_slt_case seen"))

    def fire_tp_isa_004(self):
        ok, detail = _compare(self, prog.I004, "HINT/reader pairs, hint-block minstret deltas, preconditions")
        self.check("fire_tp_isa_004", ok, detail)
        obs = _matched(self, prog.I004)
        pairs = [o for o in obs if o.kind == "hint_pair"]
        blocks = [o for o in obs if o.kind == "hint_block"]
        deltas = [_got(self, o.ridx[1]) for o in blocks]
        miss = _missing([("hint class", prog.HINT_CLASSES, {o.op for o in pairs}),
                         ("reader zero side", ("rs1", "rs2"), {o.reader['zero_side'] for o in pairs}),
                         ("reader distance", (1, 2, 3), {o.tags['dist'] for o in pairs})])
        pre = [o for o in obs if o.kind == "pre"]
        self.check("fire_tp_isa_004_floor", not miss and len(blocks) >= 2 and all(d == prog.HINT_BLOCK_DELTA for d in deltas) and len(pre) == 1,
                   f"{len(pairs)} HINT/reader pairs, {len(blocks)} blocks of {prog.HINT_BLOCK} with minstret deltas {deltas} (expected {prog.HINT_BLOCK_DELTA}), "
                   f"mcountinhibit read back {len(pre)}/1" + (f"; {miss}" if miss else "; every cp_hint_class seen"))

    def fire_tp_isa_005(self):
        p = _plan(self)
        ok, detail = _compare(self, prog.I005, "lui/auipc imm20 mix, both pc alignments (pc from the linked labels)")
        self.check("fire_tp_isa_005", ok, detail)
        obs = _matched(self, prog.I005)
        sets = []
        for op in ("lui", "auipc"):
            r = [o for o in obs if o.op == op]
            sets += [(f"{op} pc[1]", (0, 2), {_pc(self, o) & 2 for o in r}), (f"{op} imm20 class", prog.IMM20_CLASSES, {o.tags['imm20'] for o in r})]
        miss = _missing(sets)
        n = {op: sum(1 for o in p.ops if o.item == prog.I005 and o.op == op) for op in ("lui", "auipc")}
        vac = sum(1 for o in p.ops if o.item == prog.I005 and o.rd == 0)
        self.check("fire_tp_isa_005_floor", not miss and all(v >= prog.N_U_MIN for v in n.values()),
                   f"lui {n['lui']}, auipc {n['auipc']} (floor {prog.N_U_MIN} each over every plan op), {len(obs)} observed; {vac} rd=x0 vacuous ops are inside the floor but excluded from the value compare"
                   + (f"; {miss}" if miss else "; both alignments and every imm20 class per op seen"))

    def fire_tp_isa_006(self):
        ok, detail = _compare(self, prog.I006, "lui extremes, auipc imm 0, auipc address-space wrap, carry-out and no carry-out at both alignments")
        self.check("fire_tp_isa_006", ok, detail)
        obs = _matched(self, prog.I006)
        lui = {_got(self, o.ridx[0]) for o in obs if o.op == "lui"}
        au = [(o, _pc(self, o), _got(self, o.ridx[0])) for o in obs if o.op == "auipc"]
        eq_pc = {pc & 2 for o, pc, g in au if o.imm == 0 and g == pc}
        # the plan's cp_wrap: the 33-bit sum leaves the address space; from this window only the upward wrap (a positive immediate
        # past 2^32) is reachable, the downward one (a negative immediate from pc < |imm| << 12) joins this set when WP-9's low page
        # lands; the carry-out of the 32-bit add (word < pc) holds the negative-immediate cases, which stay in the space, plus the
        # space units, whose carry-out is the wrap
        space = {pc & 2 for o, pc, g in au if 0 < o.imm < 0x80000 and pc + (o.imm << 12) >= 1 << 32}
        carry = {pc & 2 for o, pc, g in au if o.imm and g < pc}
        nocarry = {pc & 2 for o, pc, g in au if o.imm and g >= pc}
        miss = _missing([("lui word", (0xFFFFF000, 0), lui), ("auipc imm0==pc at pc[1]", (0, 2), eq_pc),
                         ("auipc address-space wrap at pc[1]", (0, 2), space), ("auipc carry-out (word < pc) at pc[1]", (0, 2), carry),
                         ("auipc no carry-out at pc[1]", (0, 2), nocarry)])
        self.check("fire_tp_isa_006_floor", not miss, f"{len(obs)} observed; auipc pcs in 0x{min([pc for _, pc, _ in au] or [0]):08x}.."
                   + (f"; {miss}" if miss else "; lui 0xFFFFF000/0, auipc == pc, address-space wrap, carry-out and no carry-out at both alignments seen"))

    def fire_tp_isa_007(self):
        p = _plan(self)
        ok, detail = _compare(self, prog.I007, "R-type ALU ops, operand classes, sign pairs, register relations")
        self.check("fire_tp_isa_007", ok, detail)
        obs = [o for o in _matched(self, prog.I007) if o.rd]
        allv = [o for o in p.ops if o.item == prog.I007]
        sets = []
        for op in prog.REG_OPS:
            r = [o for o in obs if o.op == op]
            sets += [(f"{op} sign pair", prog.SIGN_PAIRS, {o.tags['sign'] for o in r}),
                     (f"{op} rs1 class", prog.RS_CLASSES, {o.tags['rs1_cls'] for o in r}),
                     (f"{op} rs2 class", prog.RS_CLASSES, {o.tags['rs2_cls'] for o in r}),
                     (f"{op} relation", prog.REL_CLASSES, {o.tags['rel'] for o in r}),
                     (f"{op} equal operands", (True, False), {o.tags['eq'] for o in r})]
        sets.append(("result class", prog.RESULT_CLASSES, {prog.result_class(prog.alu_r(o.op, o.a, o.b)) for o in obs}))
        miss = _missing(sets)
        vac = sum(1 for o in allv if o.rd == 0)
        deg = sum(1 for o in obs if prog.degenerate(o))
        self.check("fire_tp_isa_007_floor", not miss and len(allv) >= prog.N_REG_MIN,
                   f"{len(allv)} R-type ops (floor {prog.N_REG_MIN} over every plan op), {len(obs)} observed; {vac} rd=x0 vacuous and {deg} degenerate ops are inside the floor but excluded from the value compare"
                   + (f"; {miss}" if miss else "; every op x sign pair, x operand class, x relation, equal operands and result class seen"))

    def fire_tp_isa_008(self):
        ok, detail = _compare(self, prog.I008, "add/sub wrap table, windows and random pairs")
        self.check("fire_tp_isa_008", ok, detail)
        seen = set()
        for o in _matched(self, prog.I008):
            g = _got(self, o.ridx[0])
            k = o.tags["wrap"]
            if "add_carry" in k and g == o.a + o.b - (1 << 32):
                seen.add("add_carry")
            if "add_pos_ovf" in k and prog.s32(g) < 0:
                seen.add("add_pos_ovf")
            if "add_neg_ovf" in k and prog.s32(g) >= 0:
                seen.add("add_neg_ovf")
            if "sub_borrow" in k and g == o.a - o.b + (1 << 32):
                seen.add("sub_borrow")
            if "sub_ovf" in k and prog.s32(g) >= 0:
                seen.add("sub_ovf")
        want = ("add_carry", "add_pos_ovf", "add_neg_ovf", "sub_borrow", "sub_ovf")
        miss = _missing([("wrap fact", want, seen)])
        self.check("fire_tp_isa_008_floor", not miss, "wrap facts confirmed in the words: " + ", ".join(sorted(seen)) + (f"; {miss}" if miss else ""))

    def fire_tp_isa_009(self):
        ok, detail = _compare(self, prog.I009, "slt/sltu boundary table")
        self.check("fire_tp_isa_009", ok, detail)
        obs = _matched(self, prog.I009)
        sets = []
        for op in ("slt", "sltu"):
            r = [o for o in obs if o.op == op]
            sets += [(f"{op} case", ("eq", "intmin_intmax", "intmin_1", "rs1_x0"), {o.tags['case'] for o in r}),
                     (f"{op} rs1=x0 rs2 zero/nonzero", (True, False), {o.tags['b_zero'] for o in r if o.tags['case'] == 'rs1_x0'})]
        miss = _missing(sets)
        self.check("fire_tp_isa_009_floor", not miss, f"{len(obs)} compares observed" + (f"; {miss}" if miss else "; every boundary row per op seen"))

    def fire_tp_isa_052(self):
        ok, detail = _compare(self, prog.I052, "x0 writers of every class, x0 readers (value clause; the bus clause is dropped, see the docstring)")
        self.check("fire_tp_isa_052", ok, detail)
        obs = _matched(self, prog.I052)
        miss = _missing([("writer class", prog.WRITER_CLASSES, {o.tags['writer'] for o in obs}),
                         ("reader form", prog.X0_READERS, {o.tags['reader'] for o in obs})])
        self.check("fire_tp_isa_052_floor", not miss, f"{len(obs)} writer/reader units observed" + (f"; {miss}" if miss else "; every cp_writer_class and reader form seen"))


@cocotb.test()
async def gen_test_isa_alu(dut):
    await IsaAlu(dut).run()
