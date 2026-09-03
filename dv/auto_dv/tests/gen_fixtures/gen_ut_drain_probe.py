"""Probe of run()'s drain wait (cross-model R2-4 fix b): apply_phase waits for the end-of-test edge and 40 more cycles
without a bridge command, so on any build the runner is mid-apply when the program ends; run() must wait for it
(GEN_TEST_DRAIN waited cycles=40) and fire_schedule_applied must PASS with the phase applied 40 cycles after EOT. Any
reached boundary works (+gen_regime_sched=imem_gnt_delay:short@c200 with the seed-1 boot image); the consumed set is
pinned in the fixture because the stub consumes the knob itself. MODULE=gen_ut_drain_probe (PYTHONPATH: clone root and
this directory)."""
import cocotb
from cocotb.triggers import Edge, Timer

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest

# the stub apply consumes the knob itself: the schedule must not be gated by the build's rendered consumed set
lib.CONSUMED_KNOBS = lib.SCHEDULABLE_KNOBS = ("knob_imem_gnt_delay",)


class DrainProbe(GenTest):
    name = "gen_ut_drain_probe"
    schedulable = ()

    async def apply_phase(self, p):
        if not self.eot_seen:                     # hold until the program ends, then 40 more cycles: mid-apply at EOT on any build
            await Edge(self.h.b.evt_eot_seen)
        await Timer(40 * self.period_ns, "ns")    # a Timer, because wait_cycles would abandon at the end of test
        p.applied_cycle = self.cycle()
        self.applied.append(p)
        self.log.info("GEN_TEST_PHASE idx=%d trigger=%s%d knob=%s value=%s cycle=%d (stub: 40-cycle apply, no bridge command)",
                      p.idx, p.kind, p.count, lib.short_knob(p.knob), p.value, p.applied_cycle)

    def fire_check(self):
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_eot_pass_code", code == 1, f"tohost code 0x{code:08x}")


@cocotb.test()
async def gen_ut_drain_probe(dut):
    await DrainProbe(dut).run()
