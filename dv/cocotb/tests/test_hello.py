"""Hello-world cocotb test: handshake and read a DUT signal."""

import cocotb
from dv.cocotb.common.handshake import start, finish


@cocotb.test()
async def test_hello(dut):
    """Signal alive, read hart_id_i, then signal finish."""
    await start(dut)

    hart_id = dut.hart_id_i.value
    cocotb.log.info(f"COCOTB-HELLO: read hart_id_i={hart_id}")

    await finish(dut)
