"""Green counterpart of gen_ut_sched_vacuous: the normal schedule runner with the stubbed apply_phase
applies every reached boundary, so the schedule check must PASS."""
import cocotb

from gen_ut_sched_vacuous import SchedSound


@cocotb.test()
async def gen_ut_sched_sound(dut):
    await SchedSound(dut).run()
