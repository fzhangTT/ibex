"""Spanning-load integrity corruption: arm integrity corruptions on the program's buffer (MEM_ERR_ARM, kind
integrity) before the core is released, so the misaligned lw of gen_intg_span_directed.S takes a corrupted response on
its bus words: the DUT suppresses the destination write and raises the internal NMI, the scoreboard's suppressed-write gate must
consume BOTH announced words, and the later clean lw of the second word must find no announcement left (the TB mutant MUT-SUP3
asserts the suppress flag on that record: refused when both words were consumed, accepted on the leftover). The export shows one
record with rf_wr_suppress set. Lock-step compare as gen_ut_lockstep, plusargs as gen_ut_lockstep plus +gen_export_file.

+gen_ut_intg_span_arm_count (default 2) is the arming count; the armed address range always covers both of the load's
words, so the knob alone decides how many of the load's accesses are corrupted. At 1 only the first bus access is
corrupted and the DUT still writes rd, which is bug candidate B16: the assertions below then fail on purpose and the
carrying testlist entry is the expected-fail one. Nothing here accommodates that value.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_intg_span, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb import gen_export
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_INTG_SPAN_PASS"
ARM_INTG = CONSTANTS["GEN_MEM_ERR_ARM_KIND_INTG"]   # MEM_ERR_ARM arg3[7:0]
SPAN_WORDS = 2          # the misaligned lw touches two bus words; the arming count decides how many are corrupted
SETTLE_CYCLES = 4
QUIESCE_CYCLES = 20   # bound on the wait for the retired and consumed counters to hold equal across a cycle


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_intg_span(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    export_path = plus("export_file")
    assert export_path, "GEN_UT_INTG_SPAN: +gen_export_file is required (the suppressed record is read from the export)"
    assert plus("fetch_en_at_reset") == "0", "GEN_UT_INTG_SPAN: run with +gen_fetch_en_at_reset=0"
    retire_target = int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"]))
    arm_count = int(plus("ut_intg_span_arm_count", PLUSARGS["ut_intg_span_arm_count"]["default"]))
    assert 1 <= arm_count <= SPAN_WORDS, f"GEN_UT_INTG_SPAN: arm count {arm_count} is outside 1..{SPAN_WORDS}"
    buf = int(img.sidecar["symbols"]["gen_span_buf"], 16)
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_INTG_SPAN: read-back mismatch"
    # the range spans both of the load's words whatever the count, so the count alone selects first-access-only (dbus = 1; count in arg3[31:8])
    log.info("GEN_UT_INTG_SPAN arming %d integrity corruption(s) in [%08x, %08x]", arm_count, buf, buf + 4 * SPAN_WORDS - 1)
    await b.cmd("MEM_ERR_ARM", (1, buf, buf + 4 * SPAN_WORDS - 1, ARM_INTG | (arm_count << 8)))
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(retire_target, timeout_cycles=retire_target * 40 + 2000)
    if img.tohost is not None and int(h.b.evt_eot_count.value) == 0:
        try:
            await with_timeout(Edge(h.b.evt_eot_seen), 20000 * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
        except Exception as exc:
            raise AssertionError(f"GEN_UT_INTG_SPAN: no tohost store ({type(exc).__name__})") from None
    await b.wait_cycles_until(int(h.b.cycle_count.value) + SETTLE_CYCLES)
    seq = await b.export_flush()
    e = gen_export.read(export_path, seq)
    sup = [r for r in e.records if r.ext_rf_wr_suppress]
    log.info("GEN_UT_INTG_SPAN records %d suppressed %d (orders %s)", len(e.records), len(sup), [r.order for r in sup])
    assert sup, "GEN_UT_INTG_SPAN: no record with rf_wr_suppress (the spanning load's corrupted halves should suppress its write)"
    assert sup[0].mem_addr == buf + 2, f"GEN_UT_INTG_SPAN: the first suppressed record's address {sup[0].mem_addr:08x} is not the spanning load's {buf + 2:08x}"
    # any further suppressed record is judged by the scoreboard's gate (a lying flag is its isa_rd miss), not here
    # The pair's two writers, and why one instant is not enough: see gen_ut_intg_store.py.
    settled = 0
    for _ in range(QUIESCE_CYCLES):
        retired = int(h.b.evt_retired_count.value)
        consumed = int(h.b.evt_isa_records.value)
        if retired == consumed:
            settled += 1
            if settled == 2:
                break
        else:
            settled = 0
        await b.wait_cycles_until(int(h.b.cycle_count.value) + 1)
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_INTG_SPAN retired %d consumed %d mismatches %d tohost 0x%08x", retired, consumed, mism, int(h.b.evt_eot_code.value))
    assert settled == 2, f"GEN_UT_INTG_SPAN: comparator consumed {consumed} records, {retired} retired (must be equal and hold across a cycle; {QUIESCE_CYCLES} cycles waited)"
    assert mism == 0, f"GEN_UT_INTG_SPAN: {mism} ISA mismatches"
    assert int(h.b.evt_eot_code.value) == 1, "GEN_UT_INTG_SPAN: program did not report pass"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
