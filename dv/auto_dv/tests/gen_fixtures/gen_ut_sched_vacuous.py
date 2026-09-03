"""Red fixture for the template's schedule check (committed fixture, never a testlist entry): the schedule runner is broken on
purpose (run_schedule returns at once, so no phase after c0 is ever applied) and apply_phase records
the phase without a bridge command (no REGIME_SET consumer exists at HEAD). With
+gen_regime_sched=imem_gnt_delay:long@c0,imem_gnt_delay:short@c200 the c200 boundary passes before the
program ends, so a sound fire_schedule_applied must FAIL; a vacuous one PASSes.
MODULE=gen_ut_sched_vacuous (PYTHONPATH: clone root and this directory), TOPLEVEL=gen_tb_top."""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest

# the stub apply consumes the knob itself: the schedule must not be gated by the build's rendered consumed set
lib.CONSUMED_KNOBS = lib.SCHEDULABLE_KNOBS = ("knob_imem_gnt_delay",)


class StubApply:
    async def apply_phase(self, p):
        p.applied_cycle = self.cycle()
        self.applied.append(p)
        self.log.info("GEN_TEST_PHASE idx=%d trigger=%s%d knob=%s value=%s cycle=%d (stub, no bridge command)",
                      p.idx, p.kind, p.count, lib.short_knob(p.knob), p.value, p.applied_cycle)


class SchedVacuous(StubApply, GenTest):
    name = "gen_ut_sched_vacuous"
    schedulable = ()

    async def run_schedule(self):
        return None   # the broken runner: later boundaries pass unapplied

    def fire_check(self):
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_eot_pass_code", code == 1, f"tohost code 0x{code:08x}")


class SchedSound(StubApply, GenTest):
    name = "gen_ut_sched_sound"
    schedulable = ()

    def fire_check(self):
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_eot_pass_code", code == 1, f"tohost code 0x{code:08x}")


@cocotb.test()
async def gen_ut_sched_vacuous(dut):
    await SchedVacuous(dut).run()
