"""Flow probe for the cocotb-on-LSF path (T-027): proves that the cocotb VPI library, libpython
and this module load on the compute host and that Python sees the DUT. It is test equipment of
the flow, not a DUT test: no checking of Ibex behaviour, `measured: false` in the testlist.

MODULE=dv.auto_dv.flow.gen_cocotb_probe, TOPLEVEL=gen_smoke_tb_top (SIM_RECIPE Section 4). The
smoke top keeps driving clock, reset and NOPs; this test only observes a bounded number of cycles
and ends before the smoke's own $finish. ASCII-only logging (TB_CONTRACT Section 4).
"""

import os
import socket

import cocotb
from cocotb.triggers import RisingEdge

PROBE_CYCLES = 200
PASS_MARKER = "GEN_COCOTB_PROBE_PASS"


@cocotb.test()
async def gen_cocotb_probe(dut):
    log = dut._log
    log.info("GEN_COCOTB_PROBE alive host=%s pid=%d RANDOM_SEED=%s cocotb=%s",
             socket.gethostname(), os.getpid(), os.environ.get("RANDOM_SEED", "unset"), cocotb.__version__)
    log.info("GEN_COCOTB_PROBE toplevel=%s python_module=%s", dut._name, __file__)
    # Wait for reset release, then a bounded number of cycles; count retirements seen from Python.
    while dut.rst_n.value.binstr != "1":
        await RisingEdge(dut.clk)
    retired = 0
    for _ in range(PROBE_CYCLES):
        await RisingEdge(dut.clk)
        if dut.rvfi_valid.value.is_resolvable and int(dut.rvfi_valid.value) == 1:
            retired += 1
    log.info("GEN_COCOTB_PROBE cycles=%d rvfi_retired_seen=%d", PROBE_CYCLES, retired)
    assert retired > 0, "GEN_COCOTB_PROBE_FAIL: no RVFI retirement observed from Python"
    log.info(PASS_MARKER)
