"""gen_test_csr_access: plan group gen_csr_access (dv/auto_dv/docs/gen_test_plan.md Section 4.2).

Items built and their canonical features (ALIAS/FOLDED resolved through gen_feature_list.md Section 3):
  TP-CSR-001 CSR op classes, single-cycle RMW on RW CSRs          -> F-CSR-001, F-CSR-100
  TP-CSR-002 csrrs/csrrc x0 and csrrsi/csrrci 0 are pure reads     -> F-CSR-002
  TP-CSR-003 csrrw x0 / csrrwi 0 is a real write of zero           -> F-CSR-003
  TP-CSR-004 csrrw/csrrwi rd = x0 still writes; reads no side effect -> F-CSR-004 FOLDED into F-CSR-001
  TP-CSR-012 demoted forms on a read-only CSR are legal reads      -> F-CSR-012 ALIAS of F-CSR-002
Item of the group NOT built: TP-CSR-005 (SYSTEM funct3 = 100 traps; F-CSR-005, alias F-ISA-046). Its
program block and report words (handler mcause 2, mtval = word, mscratch untouched, trap count) exist
in the generator behind F3_100_WORDS / --traps; it joins the test once its mret-ending traps are
re-proven against the lock-step comparator (its isa_pc_next convention).

Consistency compares (dv/auto_dv/docs/gen_component_api_isa_shim.md,
Counter CSRs): the comparator's mcycle, mhpmcounter3..(2+MHPMCounterNum) and cpuctrlsts bit 8 are
synchronised from the DUT record before each step, so the reads of cycle, the HPM counters and
cpuctrlsts bit 8 are checked for consistency; value verification pending ctr_* / scrkey_proto. The
program reads them like every other CSR (rd != x0) and reports them; the fire-check compares a pair of
adjacent counter reads (non-decreasing, strictly increasing for cycle with CY running, equal for the
event counters no adjacent CSR read can bump) and every read against the previous read of the same
counter, and compares cpuctrlsts under a mask that excludes bit 8 (bit 8 equal across the two reads
of a sweep block). Each fire_tp detail counts these words apart from the verified words (pending
ctr_*=n scrkey_proto=m); they are not counted as fully built. mcycle, minstret(h) and the
mhpmcounters are not written by the TP-CSR-004 sweep for the same reason (a written counter has no
independent check until ctr_*). marchid is a verified constant (22, gen_feature_list.md 4.2,
cross-checked against the rendered GEN_CSR_MARCHID_VALUE).
Further operand limits (mcountinhibit.IR, mstatus.MIE/XS, mcause fixed points) are in the generator
docstring. Not built on purpose: dscratch0/1 (debug mode is not enterable from a program); the
RVFI-level parts of the items' fire-checks (funct3 on rvfi_insn, rvfi_trap, retirement gaps for
gen_chk_csr_flush) need the RVFI export (ASK 5).

Program: dv/auto_dv/tests/gen_programs/gen_csr_access_prog.py, a per-seed generator (testlist
`program: {generator: ..., seed: run}`); its plan(seed) draws the operands from the area's W-tables
and computes every report word from the Zicsr semantics and the Implemented CSR map, and the
program stores the RAW rd values and read-backs to GEN_MM_EOT_ADDR (report channel). The test never
re-derives the intent: report_count() returns plan.k and each fire_tp_csr_<nnn> compares the item's
report words with the plan through gen_csr_access_prog.evaluate; fire_tp_csr_001 also asserts the
item's directed floor (every op class and every listed CSR at least once per seed). The mhartid
expectation follows the TB's +gen_hart_id plusarg. The program installs its own trap handler
(reports mcause/mtval, counts) and the final report word is the trap count, so any unplanned trap or
skipped store desynchronises the stream and fails the checks (TP-CSR-001: every op retires without
trap). Red fixtures: `--red --red-item TP-CSR-<nnn>` (or `--red` alone, the seed draws the item) makes
the program deviate on one intent of that item so exactly its fire_tp method fails.

Knobs: the built items name knob:instr_mix, knob:imem_gnt_delay and knob:imem_rvalid_delay; the two
fetch-latency knobs are declared in `schedulable`; instr_mix is a program-side region marker
(gen_tb_knobs.yaml: regime_set_consumer program) that the TB cannot schedule and this program does
not implement, so it is not declared.

Bins: declare_bins() is the template default, the plan bins of the five fire_tp items (manifest
dv/auto_dv/fcov_expectations/gen_test_csr_access.fcov.yaml rendered from this module); no covergroup
exists yet (CG-CSR-001/003/010/012 land with gen_fcov_pkg), so the flow entry carries
fcov_expectation_file: null. Always-on checkers relied on: the ISA comparator rows
isa_pc/insn/trap/rd/mem/prv/pc_next/csr (gen_isa_compare), rvfi_proto, the ibus/dbus protocol
checkers and the bridge accounting. MODULE=dv.auto_dv.tests.gen_test_csr_access, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_csr_access_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest


def plan_for(test):
    """The seed's plan; the mhartid expectation follows the hart_id_i plusarg (hex, gen_knobs)."""
    if getattr(test, "plan", None) is None:
        hart_id = int(str(lib.plus("hart_id", lib.knob_default("hart_id"))), 16)
        test.plan = prog.plan(test.seed, hart_id=hart_id)
    return test.plan


def pending_detail(test, item):
    """Words checked for consistency only, by the checker that owns their value (state the comparator synchronises from the DUT record)."""
    pend = prog.pending_words(plan_for(test), item)
    return "; consistency only, value verification pending " + " ".join(f"{k}={v}" for k, v in sorted(pend.items())) if pend else ""


class CsrAccess(GenTest):
    name = "gen_test_csr_access"
    # knob_instr_mix is a program-side region marker (regime_set_consumer: program), not a TB regime: not declared here
    schedulable = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay")
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {
        "TP-CSR-005": "mret/ecall privilege sequence deferred to the trap batch (comparator convention fixed by T-102)",
    }

    def report_count(self):
        return plan_for(self).k

    def fire_check(self):
        # the image carries the number this generator computed and the plan recomputes it, so a
        # difference means the program and the Python checking it are different versions
        lib.program_min_retired(self.image, self.plan.min_retired)
        self.fire_tp_csr_001()
        self.fire_tp_csr_002()
        self.fire_tp_csr_003()
        self.fire_tp_csr_004()
        self.fire_tp_csr_012()

    def fire_tp_csr_001(self):
        p = plan_for(self)
        n, bad = prog.evaluate(p, self.reports, "TP-CSR-001")
        # the directed floor of the item: a class never emitted cannot have retired
        missing = [op for op in prog.OPS if not p.op_counts.get(op)] + [c for c in prog.CSRS_001 if not p.csr_counts.get(c)]
        self.check("fire_tp_csr_001", n > 0 and not bad and not missing,
                   f"{n - len(bad)}/{n} report words as planned over {p.counts['TP-CSR-001']} RMW sequences "
                   f"(rd = pre-op value, read-back = legalised op result, trap count {p.traps}); op classes "
                   + " ".join(f"{op}={p.op_counts[op]}" for op in prog.OPS)
                   + (f"; classes never emitted {missing}" if missing else "") + (f"; first mismatch {bad[0]}" if bad else ""))

    def fire_tp_csr_002(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-002")
        self.check("fire_tp_csr_002", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over {plan_for(self).counts['TP-CSR-002']} demoted reads "
                   f"(rd = CSR value, CSR unchanged; minstret exact)" + pending_detail(self, "TP-CSR-002")
                   + (f"; first mismatch {bad[0]}" if bad else ""))

    def fire_tp_csr_003(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-003")
        self.check("fire_tp_csr_003", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over {plan_for(self).counts['TP-CSR-003']} zero writes "
                   f"(rd = pre-write value, read-back 0)" + pending_detail(self, "TP-CSR-003")
                   + (f"; first mismatch {bad[0]}" if bad else ""))

    def fire_tp_csr_004(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-004")
        self.check("fire_tp_csr_004", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over the {plan_for(self).counts['TP-CSR-004']}-CSR rd=x0 sweep "
                   f"(read-back = legalised operand, two reads agree)" + pending_detail(self, "TP-CSR-004")
                   + (f"; first mismatch {bad[0]}" if bad else ""))

    def fire_tp_csr_012(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-012")
        self.check("fire_tp_csr_012", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over {plan_for(self).counts['TP-CSR-012']} demoted read-only reads "
                   f"(id constants, cycleh, instret pairs, RO-zero addresses, counter pairs)" + pending_detail(self, "TP-CSR-012")
                   + (f"; first mismatch {bad[0]}" if bad else ""))


@cocotb.test()
async def gen_test_csr_access(dut):
    await CsrAccess(dut).run()
