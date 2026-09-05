"""The four reset read-backs of CG-IRQ-011 cp_reset_reads, judged with a line already at level.

Raise one line while fetch_enable is still Off, then let the core run gen_irq_reset_reads_directed.S,
whose first four instructions read mstatus, mie, mtvec and mip before anything writes them. The line
stays pending rather than being taken, because mie is 0 and MIE is clear out of reset.

The asserted line is what makes the mip read discriminating. mip is bit-positioned (3 software, 7
timer, 11 external, 16 + id fast) while the driver's mask is line-indexed (0 software, 1 timer, 2
external, 3..17 fast), so with every pin low the two agree and a comparison that confuses them still
matches. This test fails on exactly that confusion.

Line mask bits: 0 software, 1 timer, 2 external, 3..17 fast[0..14], 18 nm. Hold policies: 0
CYCLES(arg2), 1 UNTIL_ACK, 2 UNTIL_TAKEN, 3 STICKY. Plusargs as gen_ut_lockstep.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_irq_reset_reads, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_IRQ_RESET_READS_PASS"
HOLD_STICKY = 3
LINE_EXTERNAL = 2          # driver mask bit
MIP_EXTERNAL_BIT = 11      # the same line's mip/mie bit, which is not the same number
MSTATUS_RESET = 0x80       # MPIE set, MIE clear, MPP = U (rtl/ibex_cs_registers.sv:1052-1056)
REPORT_BOUND_CYCLES = 4000
REPORT_NAMES = ("mstatus", "mie", "mtvec", "mip")


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


async def next_report(h, cycles):
    """The next value the program stored to the report register, or None if none arrives in time."""
    try:
        await with_timeout(Edge(h.b.evt_eot_seen), cycles * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
    except Exception:   # cocotb SimTimeoutError: the verdict this test states itself
        return None
    return int(h.b.evt_eot_code.value)


@cocotb.test()
async def gen_ut_irq_reset_reads(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    boot_addr = int(plus("boot_addr", "80000000"), 16)
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_IRQ_RESET_READS: read-back mismatch"

    # the line goes up while fetch is still Off, so it is at level for the very first record
    await b.cmd("IRQ_SET", (1 << LINE_EXTERNAL, HOLD_STICKY, 0, 0))
    log.info("GEN_UT_IRQ_RESET_READS raised line %d (external) before fetch_enable", LINE_EXTERNAL)
    await b.cmd("FETCH_EN", (1, 0, 0, 0))

    vals = []
    for name in REPORT_NAMES:
        v = await next_report(h, REPORT_BOUND_CYCLES)
        assert v is not None, (
            f"GEN_UT_IRQ_RESET_READS: no {name} report within {REPORT_BOUND_CYCLES} cycles "
            f"(reports so far {[hex(x) for x in vals]})")
        vals.append(v)
        log.info("GEN_UT_IRQ_RESET_READS %s reads %08x", name, v)
    mstatus, mie, mtvec, mip = vals

    assert mstatus == MSTATUS_RESET, f"GEN_UT_IRQ_RESET_READS: mstatus reads {mstatus:08x}, expected {MSTATUS_RESET:08x}"
    assert mie == 0, f"GEN_UT_IRQ_RESET_READS: mie reads {mie:08x} out of reset, expected every line masked"
    assert (mtvec >> 8) == (boot_addr >> 8), (
        f"GEN_UT_IRQ_RESET_READS: mtvec reads {mtvec:08x}, whose page is not the boot page {boot_addr:08x}")
    assert mip & (1 << MIP_EXTERNAL_BIT), (
        f"GEN_UT_IRQ_RESET_READS: mip reads {mip:08x} with line {LINE_EXTERNAL} (external) at level; "
        f"bit {MIP_EXTERNAL_BIT} is the one that line sets, and bit {LINE_EXTERNAL} is not")
    assert not (mip & (1 << LINE_EXTERNAL)), (
        f"GEN_UT_IRQ_RESET_READS: mip reads {mip:08x}, which has the line INDEX set as a bit; mip is "
        f"bit-positioned, so a value carrying bit {LINE_EXTERNAL} means the two numberings were confused")
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_IRQ_RESET_READS retired %d, compared %d, mismatches %d",
             int(h.b.evt_retired_count.value), int(h.b.evt_isa_records.value), mism)
    assert mism == 0, f"GEN_UT_IRQ_RESET_READS: {mism} ISA mismatches"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
