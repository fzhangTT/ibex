"""Debug-request path test (build step 2b): boot a riscv-dv program with a debug ROM (dret), request
debug entry through the bridge (DBG_REQ with the UNTIL_DEBUG_MODE hold policy), expect the entry
(evt_dbg_entered edge within the bound), the ROM to run and return, and zero ISA mismatches. Written
before the debug agent existed (TDD). Hold policies: 0 CYCLES(arg1), 1 UNTIL_DEBUG_MODE, 2 STICKY.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_dbg, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_DBG_PASS"
HOLD_UNTIL_DEBUG_MODE = 1


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_dbg(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_DBG: read-back mismatch"
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(300, timeout_cycles=20000)
    entries = 0
    for i in range(2):
        base = int(h.b.evt_retired_count.value)
        await b.cmd("DBG_REQ", (1, HOLD_UNTIL_DEBUG_MODE, 0, 0))
        try:
            await with_timeout(Edge(h.b.evt_dbg_entered), 4000 * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
        except Exception as exc:
            raise AssertionError(f"GEN_UT_DBG: debug entry {i} not seen within 4000 cycles ({type(exc).__name__})") from None
        entries += 1
        log.info("GEN_UT_DBG entry %d at cycle %d", i, int(h.b.cycle_count.value))
        await b.wait_retired_until(base + 80, timeout_cycles=40000)   # ROM runs and drets
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_DBG entries %d retired %d compared %d mismatches %d", entries, int(h.b.evt_retired_count.value),
             int(h.b.evt_isa_records.value), mism)
    assert mism == 0, f"GEN_UT_DBG: {mism} ISA mismatches across the debug entries"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
