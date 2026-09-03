"""Unit test of the cocotb-to-UVM bridge (build step 1b): start handshake, commands with sequence
acks, the two threshold edge bits, accounting and the finish handshake. Runs on gen_tb_top with the
DUT inputs tied idle. MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_bridge, TOPLEVEL=gen_tb_top."""
import cocotb

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles

PASS_MARKER = "GEN_UT_BRIDGE_PASS"


@cocotb.test()
async def gen_ut_bridge(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    await b.start()
    for i in range(5):
        await b.cmd("MISC", (i, 0xA5A5_0000 | i, 0, 0))
    await b.cmd("MISC", (1, 2, 3, 4))   # a second kind with a consumer; REGIME_SET gets one in step 2
    c0 = int(h.b.cycle_count.value)
    await b.wait_cycles_until(c0 + 50)
    c1 = int(h.b.cycle_count.value)
    assert c0 + 50 <= c1 <= c0 + 56, f"cycle threshold hit at {c1}, armed for {c0 + 50}"
    await b.wait_cycles_until(c1 + 20)
    c2 = int(h.b.cycle_count.value)
    assert c1 + 20 <= c2 <= c1 + 26, f"second cycle threshold hit at {c2}, armed for {c1 + 20}"
    consumed = int(h.b.cmds_consumed.value)
    assert consumed == 6, f"cmds_consumed {consumed} != 6"
    log.info("GEN_UT_BRIDGE cycles %d -> %d -> %d, consumed %d", c0, c1, c2, consumed)
    await b.finish()   # budget from +gen_finish_timeout (or its rendered default): the plusarg path runs here
    log.info(PASS_MARKER)
