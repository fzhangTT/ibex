"""Forced-red proof of the alive watchdog (TB_CONTRACT Section 3): this test never sets alive, so
gen_tb_top must $fatal with GEN_ALIVE_TIMEOUT after +gen_alive_timeout cycles. A run of this module
that reaches its own assert is a watchdog defect. Handles come from gen_handles.py; the wait is one
timer sized in cycles (no per-cycle polling)."""
import cocotb
from cocotb.triggers import Timer

from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

BUDGET_MULTIPLE = 2   # the wait must outlast the alive timeout in force, so the watchdog decides, not this test


@cocotb.test()
async def gen_ut_bridge_noalive(dut):
    h = GenHandles(dut)
    p = PLUSARGS["alive_timeout"]
    alive_cycles = int(cocotb.plusargs.get(p["plusarg"], p["default"]))
    dut._log.info("GEN_UT_BRIDGE_NEG: not setting alive on %s; expecting GEN_ALIVE_TIMEOUT within %d cycles", h.b.alive._path, alive_cycles)
    await Timer(BUDGET_MULTIPLE * alive_cycles * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
    assert False, "GEN_UT_BRIDGE_NEG: the alive watchdog did not fire"
