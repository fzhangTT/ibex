"""Misaligned-store integrity corruption: arm ONE integrity corruption on the program's buffer (MEM_ERR_ARM, kind integrity,
count 1) before the core is released, so the misaligned sw of gen_intg_store_directed.S takes a corrupted response on its first
bus word: the DUT raises the internal NMI with mtval = the store's own (misaligned) address, and the scoreboard's model must
report the same address, not the announced word's (the handler reads mtval, so the lock-step compare judges it). The export
shows the NMI entry record. Lock-step compare as gen_ut_lockstep, plusargs as gen_ut_lockstep plus +gen_export_file.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_intg_store, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb import gen_export
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_INTG_STORE_PASS"
ARM_INTG = CONSTANTS["GEN_MEM_ERR_ARM_KIND_INTG"]   # MEM_ERR_ARM arg3[7:0]
SETTLE_CYCLES = 4


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


# cycles to wait for the retired and compared counts to agree before reading them: the skew is one record and a
# record retires every few cycles, so this is generous; non-convergence fails the equality rather than hiding
QUIESCE_CYCLES = 20


@cocotb.test()
async def gen_ut_intg_store(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    export_path = plus("export_file")
    assert export_path, "GEN_UT_INTG_STORE: +gen_export_file is required (the NMI entry is read from the export)"
    assert plus("fetch_en_at_reset") == "0", "GEN_UT_INTG_STORE: run with +gen_fetch_en_at_reset=0"
    retire_target = int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"]))
    buf = int(img.sidecar["symbols"]["gen_store_buf"], 16)
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_INTG_STORE: read-back mismatch"
    # one integrity corruption on the first data access inside the buffer's first word (dbus = 1; count in arg3[31:8])
    await b.cmd("MEM_ERR_ARM", (1, buf, buf + 3, ARM_INTG | (1 << 8)))
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(retire_target, timeout_cycles=retire_target * 40 + 2000)
    if img.tohost is not None and int(h.b.evt_eot_count.value) == 0:
        try:
            await with_timeout(Edge(h.b.evt_eot_seen), 20000 * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
        except Exception as exc:
            raise AssertionError(f"GEN_UT_INTG_STORE: no tohost store ({type(exc).__name__})") from None
    await b.wait_cycles_until(int(h.b.cycle_count.value) + SETTLE_CYCLES)
    seq = await b.export_flush()
    e = gen_export.read(export_path, seq)
    entries = [r for r in e.records if r.intr]
    log.info("GEN_UT_INTG_STORE records %d interrupt entries %d (orders %s)", len(e.records), len(entries), [r.order for r in entries])
    assert entries, "GEN_UT_INTG_STORE: no interrupt-entry record (the corrupted store response should raise the internal NMI)"
    # The two counts are written by different mechanisms: the comparator writes evt_isa_records while it processes a
    # record, the interface increments evt_retired_count on the clock edge, so the pair is offset by one whenever a
    # record is in flight. Read them only once nothing is in flight. The bound decides how long to wait, never
    # whether to report: a record the comparator never consumed never converges, so the assertion below still fails.
    for _ in range(QUIESCE_CYCLES):
        if int(h.b.evt_retired_count.value) == int(h.b.evt_isa_records.value):
            break
        await b.wait_cycles_until(int(h.b.cycle_count.value) + 1)
    retired = int(h.b.evt_retired_count.value)
    consumed = int(h.b.evt_isa_records.value)
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_INTG_STORE retired %d consumed %d mismatches %d tohost 0x%08x", retired, consumed, mism, int(h.b.evt_eot_code.value))
    assert consumed == retired, f"GEN_UT_INTG_STORE: comparator consumed {consumed} records, {retired} retired (must be equal)"
    assert mism == 0, f"GEN_UT_INTG_STORE: {mism} ISA mismatches"
    assert int(h.b.evt_eot_code.value) == 1, "GEN_UT_INTG_STORE: program did not report pass"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
