"""Red counterpart of gen_ut_report_channel (committed fixture, never a testlist entry): the same program and channel,
but the expected value of report word 1 is deliberately wrong, so fire_report_1 must FAIL (the fixture proves the report
words are compared, not merely counted). MODULE=gen_ut_report_channel_red, TOPLEVEL=gen_tb_top."""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest

EXPECTED = [0x600D + 0x0BAD, 0x600D << 5, 0xC0DE0003]   # report 1 deliberately wrong: the red proof   # the fixture's own arithmetic


class ReportChannel(GenTest):
    name = "gen_ut_report_channel_red"
    schedulable = ()
    expected_reports = len(EXPECTED)

    def fire_check(self):
        self.check("fire_report_count", len(self.reports) == len(EXPECTED), f"reports {len(self.reports)} (expected {len(EXPECTED)})")
        for i, (got, exp) in enumerate(zip(self.reports, EXPECTED)):
            self.check(f"fire_report_{i}", got == exp, f"report {i} 0x{got:08x} (expected 0x{exp:08x})")
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_eot_pass_code", code == 1, f"tohost code 0x{code:08x}")
        floor = lib.program_min_retired(self.image)
        self.check("fire_retired_floor", self.retired() >= floor, f"retired {self.retired()} (floor {floor})")


@cocotb.test()
async def gen_ut_report_channel_red(dut):
    await ReportChannel(dut).run()
