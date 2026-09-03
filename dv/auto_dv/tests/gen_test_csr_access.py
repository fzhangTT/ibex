"""gen_test_csr_access: plan group gen_csr_access (dv/auto_dv/docs/gen_test_plan.md Section 4.2).

Items built and their canonical features (ALIAS/FOLDED resolved through gen_feature_list.md Section 3):
  TP-CSR-001 CSR op classes, single-cycle RMW on RW CSRs          -> F-CSR-001, F-CSR-100
  TP-CSR-002 csrrs/csrrc x0 and csrrsi/csrrci 0 are pure reads     -> F-CSR-002
  TP-CSR-003 csrrw x0 / csrrwi 0 is a real write of zero           -> F-CSR-003
  TP-CSR-004 csrrw/csrrwi rd = x0 still writes; reads no side effect -> F-CSR-004 FOLDED into F-CSR-001
  TP-CSR-012 demoted forms on a read-only CSR are legal reads      -> F-CSR-012 ALIAS of F-CSR-002
Item of the group NOT built: TP-CSR-005 (SYSTEM funct3 = 100 traps; F-CSR-005, alias F-ISA-046).
Its program block and report words (handler mcause 2, mtval = word, mscratch untouched, trap count)
are implemented in the generator behind F3_100_WORDS / --traps and passed 82/82 in bring-up, but
every deliberate trap ends in an mret whose rvfi_pc_wdata is the next sequential address (plan
C-1) and the ISA comparator's isa_pc_next row does not exempt mret records yet (40 UVM_ERROR per
seed); it joins the test when that comparator row follows C-1.

Program: dv/auto_dv/tests/gen_programs/gen_csr_access_prog.py, a per-seed generator (testlist
`program: {generator: ..., seed: run}`); its plan(seed) draws the operands from the area's W-tables
and computes every report word from the Zicsr semantics and the Implemented CSR map, and the
program stores the RAW rd values and read-backs to GEN_MM_EOT_ADDR (report channel). The test never
re-derives the intent: report_count() returns plan.k and each fire_tp_csr_<nnn> compares the item's
report words with the plan through gen_csr_access_prog.evaluate. The mhartid expectation follows the
TB's +gen_hart_id plusarg. The program installs its own trap handler (reports mcause/mtval, counts)
and the final report word is the trap count, so any unplanned trap or skipped store desynchronises
the stream and fails the checks (TP-CSR-001: every op retires without trap).

Knobs: the built items name knob:instr_mix, knob:imem_gnt_delay and knob:imem_rvalid_delay; they
are declared in `schedulable` (instr_mix is a program-side region marker this program does not
consume). layers_required = False: the TB has no REGIME_SET consumer at HEAD (step 2b parked), so
the layers are logged not_applied; the flag returns to the default when step 2b lands and the entry
takes its plan tier.

Not covered here (details in the generator docstring, each a TB finding reported with the test):
cpuctrlsts in TP-CSR-002/003/004 (the shim masks bit 8 ic_scr_key_valid, the DUT reads 1),
mcountinhibit bits 13..31 (Spike keeps them), mcycle in TP-CSR-004 and the cycle value in
TP-CSR-012 (the shim's mcycle does not follow the DUT), the marchid value 0x16 (Spike reads 5),
minstret(h) and mhpmcounter3..12 writes and the hpmcounter3..12 low-half values (Spike's retirement
detection and constant-0 hpm counters); dscratch0/1 (debug mode); the RVFI-level parts of the
items' fire-checks (funct3 on rvfi_insn, rvfi_trap, retirement gaps for gen_chk_csr_flush) need the
RVFI export (ASK 5). Bins: none declared, no covergroup exists yet (CG-CSR-001/003/010/012 land
with gen_fcov_pkg). Always-on checkers relied on: the ISA comparator rows isa_pc/insn/trap/rd/mem/
prv/pc_next/csr (gen_isa_compare), rvfi_proto, the ibus/dbus protocol checkers and the bridge
accounting. MODULE=dv.auto_dv.tests.gen_test_csr_access, TOPLEVEL=gen_tb_top.
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


class CsrAccess(GenTest):
    name = "gen_test_csr_access"
    schedulable = ("knob_instr_mix", "knob_imem_gnt_delay", "knob_imem_rvalid_delay")
    # Bring-up flag (tier check, measured false): no REGIME_SET consumer at HEAD; back to the default with step 2b.
    layers_required = False

    def report_count(self):
        return plan_for(self).k

    def fire_check(self):
        self.fire_tp_csr_001()
        self.fire_tp_csr_002()
        self.fire_tp_csr_003()
        self.fire_tp_csr_004()
        self.fire_tp_csr_012()

    def fire_tp_csr_001(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-001")
        self.check("fire_tp_csr_001", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over {plan_for(self).counts['TP-CSR-001']} RMW sequences "
                   f"(rd = pre-op value, read-back = legalised op result, trap count {plan_for(self).traps})"
                   + (f"; first mismatch {bad[0]}" if bad else ""))

    def fire_tp_csr_002(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-002")
        self.check("fire_tp_csr_002", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over {plan_for(self).counts['TP-CSR-002']} demoted reads "
                   f"(rd = CSR value, CSR unchanged; minstret exact)" + (f"; first mismatch {bad[0]}" if bad else ""))

    def fire_tp_csr_003(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-003")
        self.check("fire_tp_csr_003", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over {plan_for(self).counts['TP-CSR-003']} zero writes "
                   f"(rd = pre-write value, read-back 0)" + (f"; first mismatch {bad[0]}" if bad else ""))

    def fire_tp_csr_004(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-004")
        self.check("fire_tp_csr_004", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over the {plan_for(self).counts['TP-CSR-004']}-CSR rd=x0 sweep "
                   f"(read-back = legalised operand, two reads agree)" + (f"; first mismatch {bad[0]}" if bad else ""))

    def fire_tp_csr_012(self):
        n, bad = prog.evaluate(plan_for(self), self.reports, "TP-CSR-012")
        self.check("fire_tp_csr_012", n > 0 and not bad,
                   f"{n - len(bad)}/{n} report words as planned over {plan_for(self).counts['TP-CSR-012']} demoted read-only reads "
                   f"(id constants, counter pairs, RO-zero addresses)" + (f"; first mismatch {bad[0]}" if bad else ""))


@cocotb.test()
async def gen_test_csr_access(dut):
    await CsrAccess(dut).run()
