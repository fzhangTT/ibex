"""Local proof of the template's program report channel (committed fixture, never a testlist entry): the fixture
program gen_report_channel.S stores three words to the EOT register, then tohost 1. The test expects
the three words and asserts their architectural values. MODULE=gen_ut_report_channel (PYTHONPATH must
hold the clone root and this directory), TOPLEVEL=gen_tb_top."""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest

EXPECTED = [0x600D + 0x0BAD, 0x600D << 4, 0xC0DE0003]   # the fixture's own arithmetic


class ReportChannel(GenTest):
    name = "gen_ut_report_channel"
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
async def gen_ut_report_channel(dut):
    await ReportChannel(dut).run()
