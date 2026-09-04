"""An interrupt raised inside a long NMI handler (CM132-M-1): boot gen_nmi_long_directed.S (its NMI handler retires 41 records),
raise the NMI through the bridge, then raise the external line while the handler runs and hold it until taken. NMI mode masks
every interrupt, so the line's expectation outlives GEN_IRQ_ENTRY_BOUND_RECORDS inside the handler; the irq checker must keep it
and judge it after the handler's mret, when the DUT takes the line (green) or a TB mutant withholds it (MUT-NT3: the never-taken
line must fail). The test itself requires the NMI entry and zero ISA mismatches. Plusargs as gen_ut_lockstep.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_irq_nmi_long, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_IRQ_NMI_LONG_PASS"
HOLD_UNTIL_TAKEN = 2
MASK_NM = 1 << 18            # line mask bits: 0 software, 1 timer, 2 external, 3..17 fast, 18 nm (gen_ut_irq)
MASK_EXTERNAL = 1 << 2
HANDLER_RECORDS_BEFORE_RAISE = 6   # the ext line is raised this many records into the 41-record NMI handler


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


async def taken_within(h, cycles):
    try:
        await with_timeout(Edge(h.b.evt_irq_taken), cycles * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
        return True
    except Exception:
        return False


@cocotb.test()
async def gen_ut_irq_nmi_long(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    assert plus("fetch_en_at_reset") == "0", "GEN_UT_IRQ_NMI_LONG: run with +gen_fetch_en_at_reset=0"
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_IRQ_NMI_LONG: read-back mismatch"
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(200, timeout_cycles=20000)
    await b.cmd("IRQ_SET", (MASK_NM, HOLD_UNTIL_TAKEN, 0, 0))
    ok = await taken_within(h, 4000)
    assert ok, "GEN_UT_IRQ_NMI_LONG: the NMI was not taken within 4000 cycles"
    base = int(h.b.evt_retired_count.value)
    await b.wait_retired_until(base + HANDLER_RECORDS_BEFORE_RAISE, timeout_cycles=20000)
    await b.cmd("IRQ_SET", (MASK_EXTERNAL, HOLD_UNTIL_TAKEN, 0, 0))   # raised inside the NMI handler: masked until its mret
    log.info("GEN_UT_IRQ_NMI_LONG external raised at retired %d, %d records after the NMI entry", int(h.b.evt_retired_count.value), HANDLER_RECORDS_BEFORE_RAISE)
    await b.wait_retired_until(base + 200, timeout_cycles=40000)   # the handler's 41 records, its mret, and room for the judgement
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_IRQ_NMI_LONG retired %d mismatches %d", int(h.b.evt_retired_count.value), mism)
    assert mism == 0, f"GEN_UT_IRQ_NMI_LONG: {mism} ISA mismatches"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
