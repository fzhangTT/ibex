"""Red fixture for the forked-coroutine failure path (Critic L-1): stimulus() raises an AssertionError
inside the background task; cocotb must abort the test and the flow must report FAIL.
MODULE=gen_ut_stim_raises, TOPLEVEL=gen_tb_top."""
import cocotb

from dv.auto_dv.tests.gen_test_template import GenTest


class StimRaises(GenTest):
    name = "gen_ut_stim_raises"
    schedulable = ()

    async def stimulus(self):
        await self.wait_cycles(self.cycle() + 100)
        raise AssertionError("GEN_TEST_FAIL gen_ut_stim_raises: deliberate failure inside the forked stimulus()")

    def fire_check(self):
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_eot_pass_code", code == 1, f"tohost code 0x{code:08x}")


@cocotb.test()
async def gen_ut_stim_raises(dut):
    await StimRaises(dut).run()
