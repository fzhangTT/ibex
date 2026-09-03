"""Probe of run()'s drain wait (cross-model R2-4 fix b): apply_phase holds the runner 40 cycles without a bridge
command and the schedule's last boundary is the end-of-test cycle (+gen_regime_sched=imem_gnt_delay:long@c0,
imem_gnt_delay:short@c1924 with the seed-1 boot image, EOT at cycle 1924), so the runner is mid-apply when the
program ends: run() must wait for it (GEN_TEST_DRAIN line) and fire_schedule_applied must PASS with both phases
applied. MODULE=gen_ut_drain_probe (PYTHONPATH: clone root and this directory), TOPLEVEL=gen_tb_top."""
import cocotb
from cocotb.triggers import Timer

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest


class DrainProbe(GenTest):
    name = "gen_ut_drain_probe"
    schedulable = ()

    async def apply_phase(self, p):
        await Timer(40 * self.period_ns, "ns")   # holds across the end of test; wait_cycles would abandon there
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
