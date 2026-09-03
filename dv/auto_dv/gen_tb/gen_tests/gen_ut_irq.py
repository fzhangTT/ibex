"""Interrupt path: boot a program whose mtvec table handlers mret with interrupts enabled, raise lines through
the bridge (IRQ_SET, UNTIL_TAKEN hold) and require each to be taken (evt_irq_taken edge within the bound) with
zero ISA mismatches. Line mask bits: 0 software, 1 timer, 2 external, 3..17 fast[0..14], 18 nm. Hold policies:
0 CYCLES(arg2), 1 UNTIL_ACK, 2 UNTIL_TAKEN, 3 STICKY. Plusargs as gen_ut_lockstep.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_irq, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_IRQ_PASS"
HOLD_UNTIL_TAKEN = 2
LINES = [("fast3", 1 << (3 + 3)), ("external", 1 << 2), ("software", 1 << 0), ("timer", 1 << 1), ("fast14+fast0", (1 << (3 + 14)) | (1 << 3))]


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


async def taken_within(h, cycles):
    try:
        await with_timeout(Edge(h.b.evt_irq_taken), cycles * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
        return True
    except Exception:
        return False


@cocotb.test()
async def gen_ut_irq(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_IRQ: read-back mismatch"
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(300, timeout_cycles=20000)
    taken = 0
    for name, mask in LINES:
        base = int(h.b.evt_retired_count.value)
        await b.cmd("IRQ_SET", (mask, HOLD_UNTIL_TAKEN, 0, 0))
        ok = await taken_within(h, 4000)
        log.info("GEN_UT_IRQ line %s mask 0x%05x taken=%s at cycle %d", name, mask, ok, int(h.b.cycle_count.value))
        assert ok, f"GEN_UT_IRQ: interrupt on {name} not taken within 4000 cycles"
        taken += 1
        await b.wait_retired_until(base + 60, timeout_cycles=20000)   # let the handler run and mret
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_IRQ taken %d interrupts, retired %d, compared %d, mismatches %d", taken,
             int(h.b.evt_retired_count.value), int(h.b.evt_isa_records.value), mism)
    assert taken == len(LINES)
    assert mism == 0, f"GEN_UT_IRQ: {mism} ISA mismatches across the interrupt entries"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
