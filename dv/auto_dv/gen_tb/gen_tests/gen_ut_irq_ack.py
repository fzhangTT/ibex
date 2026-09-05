"""The UNTIL_ACK hold policy releases the line the handler acknowledged, and only that one.

Boot gen_irq_ack_directed.S (every cause vectors to one handler that reports its own mcause to the
report register, acknowledges that cause at the irq-ack register and mrets), then raise TWO lines at
once through the bridge under the UNTIL_ACK hold. The DUT takes the higher-priority line first and
its handler acknowledges that cause; the other line is still at level and owes a second entry. A
driver that treats one acknowledgement as a release of every UNTIL_ACK line leaves that second entry
missing, which is what the second wait here fails on.

Line mask bits: 0 software, 1 timer, 2 external, 3..17 fast[0..14], 18 nm. Hold policies: 0
CYCLES(arg2), 1 UNTIL_ACK, 2 UNTIL_TAKEN, 3 STICKY. Plusargs as gen_ut_lockstep.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_irq_ack, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_IRQ_ACK_PASS"
HOLD_UNTIL_ACK = 1
LINE_FAST3 = 3 + 3         # fast[3]
LINE_EXTERNAL = 2
# the mcause lower cause of a line is its mie/mip bit: 3 software, 7 timer, 11 external, 16 + id fast
CAUSE_FAST3 = 16 + 3
CAUSE_EXTERNAL = 11
BOTH_MASK = (1 << LINE_FAST3) | (1 << LINE_EXTERNAL)
ENTRY_BOUND_CYCLES = 4000  # an enabled line at level is taken far inside this
BOOT_RETIREMENTS = 300     # the program is well into its loop, with mtvec, mie and MIE set


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


async def entry_cause(h, cycles):
    """The cause of the next handler entry, from its report store, or None if none arrives in time."""
    try:
        await with_timeout(Edge(h.b.evt_eot_seen), cycles * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
    except Exception:   # cocotb SimTimeoutError: no entry, which is a verdict this test states itself
        return None
    return int(h.b.evt_eot_code.value)


@cocotb.test()
async def gen_ut_irq_ack(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_IRQ_ACK: read-back mismatch"
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(BOOT_RETIREMENTS, timeout_cycles=20000)
    early = int(h.b.evt_eot_count.value)
    assert early == 0, f"GEN_UT_IRQ_ACK: {early} report stores before any line was raised"

    await b.cmd("IRQ_SET", (BOTH_MASK, HOLD_UNTIL_ACK, 0, 0))
    log.info("GEN_UT_IRQ_ACK raised lines 0x%05x (fast3 and external) under UNTIL_ACK at cycle %d",
             BOTH_MASK, int(h.b.cycle_count.value))
    first = await entry_cause(h, ENTRY_BOUND_CYCLES)
    assert first is not None, (
        f"GEN_UT_IRQ_ACK: no entry within {ENTRY_BOUND_CYCLES} cycles of raising lines 0x{BOTH_MASK:05x}")
    log.info("GEN_UT_IRQ_ACK entry 1 through cause %d, acknowledged, at cycle %d", first, int(h.b.cycle_count.value))
    second = await entry_cause(h, ENTRY_BOUND_CYCLES)
    assert second is not None, (
        f"GEN_UT_IRQ_ACK: cause {first} was acknowledged and no second entry followed within "
        f"{ENTRY_BOUND_CYCLES} cycles: the other line of mask 0x{BOTH_MASK:05x} was released by an "
        f"acknowledgement that did not name it")
    log.info("GEN_UT_IRQ_ACK entry 2 through cause %d at cycle %d", second, int(h.b.cycle_count.value))
    assert {first, second} == {CAUSE_FAST3, CAUSE_EXTERNAL}, (
        f"GEN_UT_IRQ_ACK: entries came through causes {first} and {second}, expected "
        f"{CAUSE_FAST3} (fast3) and {CAUSE_EXTERNAL} (external), one each")
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_IRQ_ACK 2 entries, retired %d, compared %d, mismatches %d",
             int(h.b.evt_retired_count.value), int(h.b.evt_isa_records.value), mism)
    assert mism == 0, f"GEN_UT_IRQ_ACK: {mism} ISA mismatches across the interrupt entries"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
