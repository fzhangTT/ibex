"""Forced-red proof of the alive watchdog (TB_CONTRACT Section 3): this test never sets alive, so
gen_tb_top must $fatal with GEN_ALIVE_TIMEOUT after +gen_alive_timeout cycles. A run of this module
that reaches its own assert is a watchdog defect. Handles come from gen_handles.py; the wait is one
timer sized in cycles (no per-cycle polling)."""
import cocotb
from cocotb.triggers import Timer

from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS

BUDGET_CYCLES = 20000


@cocotb.test()
async def gen_ut_bridge_noalive(dut):
    h = GenHandles(dut)
    dut._log.info("GEN_UT_BRIDGE_NEG: not setting alive on %s; expecting GEN_ALIVE_TIMEOUT", h.b.alive._path)
    await Timer(BUDGET_CYCLES * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
    assert False, "GEN_UT_BRIDGE_NEG: the alive watchdog did not fire"
