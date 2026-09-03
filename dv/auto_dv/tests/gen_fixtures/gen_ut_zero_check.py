"""Red fixture for the zero-fire-check guard (committed fixture, never a testlist entry): fire_check() records nothing. A template
that only inspects failures PASSes this test; the guarded template must FAIL it before the handshake.
MODULE=gen_ut_zero_check, TOPLEVEL=gen_tb_top."""
import cocotb

from dv.auto_dv.tests.gen_test_template import GenTest


class ZeroCheck(GenTest):
    name = "gen_ut_zero_check"
    schedulable = ()

    def fire_check(self):
        return None   # records no check on purpose


@cocotb.test()
async def gen_ut_zero_check(dut):
    await ZeroCheck(dut).run()
