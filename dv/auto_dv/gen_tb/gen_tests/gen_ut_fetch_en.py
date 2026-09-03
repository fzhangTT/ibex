"""fetch_enable_i Off and back On (misc rule fetch_en): boot, FETCH_EN 0, wait past the drain window plus a margin, FETCH_EN 1, then
the program runs on to its tohost store. The judgement is the monitor's: a record later than GEN_FETCH_EN_DRAIN_CYCLES after the
Off edge is a fetch_en failure; the test only drives the scenario and logs the record counts. Plusargs as gen_ut_boot.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_fetch_en, TOPLEVEL=gen_tb_top."""
import cocotb
from cocotb.triggers import ClockCycles
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS
PASS_MARKER = "GEN_UT_FETCH_EN_PASS"


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_fetch_en(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    await b.start()
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"])), timeout_cycles=60000)
    await b.cmd("FETCH_EN", (0, 0, 0, 0))
    drain = CONSTANTS["GEN_FETCH_EN_DRAIN_CYCLES"]
    await ClockCycles(h.clk, drain)
    n_drained = int(h.b.evt_retired_count.value)
    await ClockCycles(h.clk, 4 * drain)
    n_idle = int(h.b.evt_retired_count.value)
    log.info("GEN_UT_FETCH_EN: %d records retired by the end of the drain window, %d after %d more idle cycles", n_drained, n_idle, 4 * drain)
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(n_idle + 20, timeout_cycles=60000)
    await b.finish()
    log.info(PASS_MARKER)
