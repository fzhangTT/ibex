"""Forced-red proof of the alive watchdog (TB_CONTRACT Section 3): this test never sets alive, so
gen_tb_top must $fatal with GEN_ALIVE_TIMEOUT after +gen_alive_timeout cycles. A run of this module
that reaches its own assert is a watchdog defect."""
import cocotb
from cocotb.triggers import ClockCycles


@cocotb.test()
async def gen_ut_bridge_noalive(dut):
    dut._log.info("GEN_UT_BRIDGE_NEG: not setting alive; expecting GEN_ALIVE_TIMEOUT")
    await ClockCycles(dut.clk, 20000)
    assert False, "GEN_UT_BRIDGE_NEG: the alive watchdog did not fire"
