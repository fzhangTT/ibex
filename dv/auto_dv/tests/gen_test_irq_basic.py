"""gen_test_irq_basic: plain interrupt entry and return on all four line classes.

Items (gen_test_plan.md): TP-IRQ-001 software, TP-IRQ-002 timer, TP-IRQ-003 external, TP-IRQ-004
the fast sweep. This test drives every line itself, one at a time, so each is taken alone under the
quiet regime, which is the precondition those items state.

The entry is schedulable across the regime and hold knobs as well as the timing ones. Under sparse
or storm the driver adds autonomous entries, and the program absorbs them: only the FIRST entry
through a vector reports, so the report count is exactly the same under every regime and a repeat
entry is acknowledged and returned from silently. That is what lets one entry cover the knob shapes
without the report channel, which needs an exact count, becoming unpredictable.

knob_irq_line_mix is NOT schedulable and is pinned by the entry away from with_nmi. The NMI is
non-maskable, so mie having no bit for it is not protection: an NMI would arrive at a cause outside
this program's 31-slot vector table. No debug-request and no NMI shape belongs to this entry.

The program (gen_irq_basic_prog) stores an armed marker, then five raw words per entry (the vector
index it was entered through, mcause, mepc, mtval, mstatus), then the run's unexpected-trap count.
The checking here is intent-derived: the vector a handler was entered through determines the
mcause it must carry, so a wrong-line entry fails its own tuple rather than being averaged away.
"""

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.tests.gen_programs import gen_irq_basic_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest

HOLD_UNTIL_ACK = 1        # gen_irq_hold_e: {CYCLES, UNTIL_ACK, UNTIL_TAKEN, STICKY}
NMI_DRIVER_BIT = 18       # never driven here: this entry owns no NMI shape
MSTATUS_MIE = 1 << 3
MSTATUS_MPIE = 1 << 7
# a phase group applies one command per cycle from its trigger, at most k of them (lib.Schedule
# k_range), so this covers the whole group plus the bridge command round trip
PHASE_SETTLE_CYCLES = 64


def entries_of(reports):
    """The report stream as (vector_index, mcause, mepc, mtval, mstatus) tuples."""
    w = prog.WORDS_PER_ENTRY
    body = list(reports[1:-1])
    return [tuple(body[i:i + w]) for i in range(0, len(body), w)]


def by_vector(reports):
    return {t[0]: t for t in entries_of(reports)}


def line_facts(reports, cause, label):
    """The facts one line-class entry must satisfy, as (ok, detail) pairs for the caller to record.

    Kept pure so the fire methods do every self.check themselves: the collected mechanism is the
    only thing that decides a verdict.
    """
    got = by_vector(reports)
    if cause not in got:
        return [(False, f"{label}: no entry through vector {cause} in {sorted(got)}")]
    idx, mcause, mepc, mtval, mstatus = got[cause]
    want = prog.MCAUSE_INTERRUPT | cause
    return [
        (mcause == want, f"{label}: vector {idx} carried mcause 0x{mcause:08x}, expected 0x{want:08x}"),
        ((mstatus & MSTATUS_MIE) == 0,
         f"{label}: mstatus.MIE is {(mstatus >> 3) & 1} in the handler, hardware entry clears it"),
        ((mstatus & MSTATUS_MPIE) != 0,
         f"{label}: mstatus.MPIE is 0 in the handler, entry from MIE=1 sets it"),
        (mtval == 0, f"{label}: mtval is 0x{mtval:08x}, an interrupt writes no trap value"),
    ]


async def await_reports(test, n):
    """Wait until the program has stored at least n report words, so the next line is driven only
    after the previous entry has completed and released its line.

    Driven by the report edge rather than by a poll on the bridge cycle slot: that slot is shared
    with the schedule runner and every arm suppresses one cycle's compare, so a poll that re-arms
    it every few cycles can cost the runner a boundary. Lateness is judged by retirement, the way
    the report collector judges it, because a bus regime stretches a program many times over and a
    fixed cycle budget fails a healthy run at some seeds and not others.
    """
    b = test.h.b
    final = test.report_count() + 1        # the last store is the end of test, not a report word
    rounds, last_retired = 0, test.retired()
    while test.eot_count() < n:
        if test.eot_count() >= final:
            return   # the program reached end of test; wait_eot owns the verdict from here
        try:
            await with_timeout(Edge(b.evt_eot_seen), test.program_budget_cycles * test.period_ns, "ns")
        except Exception as exc:   # cocotb SimTimeoutError
            now_retired = test.retired()
            assert now_retired > last_retired, (
                f"GEN_TEST_IRQ: {test.eot_count()} report words at cycle {test.cycle()}, expected {n}, "
                f"and no retirement for {test.program_budget_cycles} cycles ({type(exc).__name__})")
            rounds += 1
            assert rounds < test.progress_rounds_max, (
                f"GEN_TEST_IRQ: {test.eot_count()} report words at cycle {test.cycle()}, expected {n}, "
                f"after {rounds} x {test.program_budget_cycles} cycles although the core keeps retiring")
            last_retired = now_retired


async def hold_for_last_phase(test):
    """Hold the final entry until every scheduled phase has been applied; False if the program ended.

    The program spins until every armed vector has been entered, so this costs simulation time and
    not an entry. Without it a whole schedule can be applied after the last entry was taken, and
    the knob values the schedule sets would never be in force while an interrupt is taken.
    """
    phases = test.schedule.phases
    last = max((ph.count for ph in phases), default=0)
    if last == 0:
        return True
    kind = phases[0].kind                  # lib.Schedule allows one trigger kind per schedule
    if kind == "c":
        reached = await test.wait_cycles(last, timeout_cycles=test.program_budget_cycles)
    else:
        reached = await test.wait_retired(last, timeout_cycles=test.program_budget_cycles)
    if not reached:
        return False
    return await test.wait_cycles(test.cycle() + PHASE_SETTLE_CYCLES,
                                  timeout_cycles=test.program_budget_cycles)


class IrqBasic(GenTest):
    name = "gen_test_irq_basic"
    # the regime and hold knobs are safe here (a repeat entry reports nothing); line_mix is pinned
    # by the entry because its with_nmi value would drive a cause this vector table has no slot for
    schedulable = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay", "knob_imem_outstanding_cap",
                   "knob_dmem_gnt_delay", "knob_dmem_rvalid_delay", "knob_scr_key_delay",
                   "knob_irq_regime", "knob_irq_hold")
    program_handlers = ("irq",)           # a returning interrupt handler, no debug ROM and no exception path
    # every item of the plan group has a fire_tp method (two-sided against the group by the structure check)
    # bins this test does not guarantee per run, with the reason and its class (gen_test_template.bins_not_hit)
    bins_not_hit = {}
    not_built = {}

    def report_count(self):
        return prog.plan(self.seed).k

    async def stimulus(self):
        """Drive each armed line alone, in this test's own order, after the program says it is armed.

        The armed marker is stored before mstatus.MIE is set, so no interrupt can be taken until it
        is out: the report stream always opens with it and every reported entry is taken from the
        program's one-instruction spin loop, whatever the regime adds on top.
        """
        p = prog.plan(self.seed)
        await await_reports(self, 1)         # the armed marker
        order = list(p.entries)
        self.rng.shuffle(order)              # the drive order is this test's, not the program's
        for i, e in enumerate(order):
            assert e.driver_bit != NMI_DRIVER_BIT, "gen_test_irq_basic drives no NMI"
            if i == len(order) - 1 and not await hold_for_last_phase(self):
                return                   # the program ended first; wait_eot owns the verdict
            await self.cmd("IRQ_SET", (1 << e.driver_bit, HOLD_UNTIL_ACK, 0, 0))
            self.log.info("GEN_TEST_IRQ drove %s (driver bit %d, cause %d), entry %d of %d",
                          e.line, e.driver_bit, e.cause, i + 1, len(order))
            await await_reports(self, 1 + (i + 1) * prog.WORDS_PER_ENTRY)

    def fire_check(self):
        self.fire_tp_irq_001()
        self.fire_tp_irq_002()
        self.fire_tp_irq_003()
        self.fire_tp_irq_004()

    def fire_tp_irq_001(self):
        """Software entry, and the armed marker without which no entry is deterministic."""
        armed = self.reports[0] if self.reports else None
        self.check("fire_tp_irq_001", armed == prog.ARMED_MARK,
                   f"armed marker is 0x{armed:08x}" if armed is not None else "no report words at all")
        for ok, detail in line_facts(self.reports, prog.CAUSE_SOFTWARE, "software interrupt entry"):
            self.check("fire_tp_irq_001", ok, detail)

    def fire_tp_irq_002(self):
        """Timer entry, and the pc every entry must have been taken from."""
        for ok, detail in line_facts(self.reports, prog.CAUSE_TIMER, "timer interrupt entry"):
            self.check("fire_tp_irq_002", ok, detail)
        pcs = {t[2] for t in entries_of(self.reports)}
        self.check("fire_tp_irq_002", len(pcs) <= 1,
                   f"entries were taken from {len(pcs)} different pcs {sorted(hex(x) for x in pcs)}, "
                   "the program spins on one instruction so every mepc must be that address")

    def fire_tp_irq_003(self):
        """External entry, and the run's own count of traps this test never armed."""
        for ok, detail in line_facts(self.reports, prog.CAUSE_EXTERNAL, "external interrupt entry"):
            self.check("fire_tp_irq_003", ok, detail)
        unexpected = self.reports[-1] if self.reports else None
        self.check("fire_tp_irq_003", unexpected == 0,
                   f"the run took {unexpected} unexpected trap(s) (an exception, or a vector this test never armed)")

    def fire_tp_irq_004(self):
        """Every fast id taken alone through its own vector; the sweep is the item, not one id."""
        got = by_vector(self.reports)
        missing = [c for c in prog.FAST_CAUSES if c not in got]
        self.check("fire_tp_irq_004", not missing,
                   f"fast sweep: no entry through vector(s) {missing}" if missing else "fast sweep: all ids entered")
        for c in prog.FAST_CAUSES:
            if c in got:
                for ok, detail in line_facts(self.reports, c, f"fast id {c - prog.FAST_CAUSE_LO} entry"):
                    self.check("fire_tp_irq_004", ok, detail)
        seen = sorted(t[0] for t in entries_of(self.reports))
        want = sorted(e.cause for e in prog.plan(self.seed).entries)
        self.check("fire_tp_irq_004", seen == want, f"vector indices {seen} != armed set {want}")


@cocotb.test()
async def gen_test_irq_basic(dut):
    await IrqBasic(dut).run()
