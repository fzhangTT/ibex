"""Red fixture for wait_eot's runaway cap (committed fixture, never a testlist entry): the report-channel program stores
three words and then loops on itself after tohost, so the core keeps retiring while the fourth store the fixture expects
never comes; the template must FAIL after progress_rounds_max budgets with "although the core keeps retiring (runaway
program)", after logging one GEN_TEST_SLOW line per budget. MODULE=gen_ut_eot_runaway, TOPLEVEL=gen_tb_top; budget and
cap lowered to keep the run short."""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS
from gen_ut_report_channel import ReportChannel


class EotRunaway(ReportChannel):
    name = "gen_ut_eot_runaway"
    expected_reports = 4
    program_budget_cycles = CONSTANTS["GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT"] // 20
    progress_rounds_max = 3


@cocotb.test()
async def gen_ut_eot_runaway(dut):
    await EotRunaway(dut).run()
