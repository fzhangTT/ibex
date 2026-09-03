"""Red fixture for wait_eot's progress rule (committed fixture, never a testlist entry): the report-channel program stores
three words, the fixture expects a fourth that never comes, and the observer's retirement count is frozen, so the template
must FAIL within one budget with "no retirement" (a slow program keeps retiring and is waited for; a dead one is not).
MODULE=gen_ut_eot_stall, TOPLEVEL=gen_tb_top; program gen_report_channel.S; budget lowered to keep the run short."""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS
from gen_ut_report_channel import ReportChannel


class EotStall(ReportChannel):
    name = "gen_ut_eot_stall"
    expected_reports = 4
    program_budget_cycles = CONSTANTS["GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT"] // 20

    def retired(self):
        return 0   # frozen observer: no retirement progress is ever seen


@cocotb.test()
async def gen_ut_eot_stall(dut):
    await EotStall(dut).run()
