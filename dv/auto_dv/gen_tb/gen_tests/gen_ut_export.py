"""Record and event export test (T-080, addendum gen_rvfi_export_addendum.md): the boot flow of gen_ut_lockstep, then
EXPORT_FLUSH and a read of the export file bound to the flush sequence just issued. Two flushes are issued (one early, one after the end of test) and read(seq) is bound to the second; the first must be a prefix of it. Checks (Section 5.1): header
field list equals the rendered EXPORT_RECORD_FIELDS (plus the counter fields iff counters=1); the marker's records
equals its retired count and the parsed R-line count; order increments by one; the first record's pc_rdata is the
boot page + 0x80; every RVFI store to the tohost address carries 1 and their count does not exceed the memory model's end-of-test count; pc continuity between
consecutive R lines with no I line between them; the bridge's retired count read after the ack is >= the marker's.
Plusargs as gen_ut_lockstep plus +gen_export_file=<path> (relative to the run directory).
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_export, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb import gen_export
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, MEMORY_MAP, PLUSARGS, REGIME_WINDOWS

PASS_MARKER = "GEN_UT_EXPORT_PASS"
# a store's RVFI record retires after its bus response (the rendered rvalid window maximum) plus a pipeline margin; too short fails loud (tohost assert)
SETTLE_CYCLES = max(hi for lo, hi in REGIME_WINDOWS["rvalid_delay"].values()) + 8
FIRST_FETCH_OFFSET = MEMORY_MAP["boot_reset_offset"]   # the first fetch is {boot_addr[31:8], 8'h80} (rtl/ibex_if_stage.sv), one origin in the yaml
MRET_INSN, DRET_INSN = CONSTANTS["GEN_INSN_MRET"], CONSTANTS["GEN_INSN_DRET"]   # their pc_wdata is not the target (plan C-1)


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


def check_records(records, markers, img, eot_count, log):
    """The program-derived content checks of Section 5.1 (read() already enforced count, order and format)."""
    assert records, "GEN_UT_EXPORT: no records exported"
    boot_page = img.entry & MEMORY_MAP["boot_page_mask"]
    first_pc = records[0].pc_rdata
    assert first_pc == boot_page + FIRST_FETCH_OFFSET, f"GEN_UT_EXPORT: first record pc 0x{first_pc:08x} != boot page + boot_reset_offset (0x{boot_page + FIRST_FETCH_OFFSET:08x})"
    # the tohost stores as RVFI reports them against the memory model's independent count of the same stores
    # (the bridge's evt_eot_count, read after the flush ack, so it may exceed the flushed prefix but never trail it)
    tohost_stores = [r for r in records if r.mem_wmask != 0 and r.mem_addr == img.tohost]
    assert tohost_stores, f"GEN_UT_EXPORT: no store to tohost 0x{img.tohost:08x} in the export"
    assert all(r.mem_wdata == 1 for r in tohost_stores), "GEN_UT_EXPORT: a tohost store carries a value other than 1"
    assert len(tohost_stores) <= eot_count, f"GEN_UT_EXPORT: {len(tohost_stores)} tohost stores exported, the memory model saw {eot_count}"
    # pc continuity: pc_rdata[k+1] == pc_wdata[k] unless an I line (interrupt entry) lies between them, record k is a
    # debug entry, record k trapped (this RTL reports pc + 4 as pc_wdata of a trap record, not the handler address:
    # first green run, riscv-dv seed 7, order 466 ecall; F-RVFI-010), or record k is mret/dret (pc_wdata is the next
    # sequential address, plan C-1); Zcmp micro-op records (ext_exp_valid and not
    # ext_exp_last) are skipped pending the RVFI convention recorded at the first green run (addendum 5.1)
    marker_cycles = sorted(m.cycle for m in markers)
    breaks = 0
    for k in range(len(records) - 1):
        a, b = records[k], records[k + 1]
        if (a.ext_exp_valid and not a.ext_exp_last) or a.trap or a.insn in (MRET_INSN, DRET_INSN):
            continue
        if any(a.cycle < c <= b.cycle for c in marker_cycles) or a.ext_debug_mode != b.ext_debug_mode:
            continue
        if b.pc_rdata != a.pc_wdata:
            breaks += 1
            log.error("GEN_UT_EXPORT pc discontinuity: order %d pc_wdata 0x%08x, next pc_rdata 0x%08x", a.order, a.pc_wdata, b.pc_rdata)
    assert breaks == 0, f"GEN_UT_EXPORT: {breaks} pc discontinuities between consecutive records"


@cocotb.test()
async def gen_ut_export(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    retire_target = int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"]))
    export_path = plus("export_file")
    assert export_path, "GEN_UT_EXPORT: +gen_export_file is required"
    assert plus("fetch_en_at_reset") == "0", "GEN_UT_EXPORT: run with +gen_fetch_en_at_reset=0 (the read-back precedes execution)"
    await b.start()
    n_rb = int(plus("mem_readback_words", PLUSARGS["mem_readback_words"]["default"]))
    bad = 0
    for idx, word in img.sample(n_rb, seed):
        if await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) != word:
            bad += 1
    assert bad == 0, f"GEN_UT_EXPORT: {bad} read-back mismatches"
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(retire_target // 2, timeout_cycles=retire_target * 40 + 2000)   # so the early prefix has records
    seq_early = await b.export_flush()   # an early flush: read(seq) must bind to the flush it names, never to this one
    await b.wait_retired_until(retire_target, timeout_cycles=retire_target * 40 + 2000)
    if img.tohost is not None and int(h.b.evt_eot_count.value) == 0:
        try:
            await with_timeout(Edge(h.b.evt_eot_seen), 20000 * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
        except Exception as exc:
            raise AssertionError(f"GEN_UT_EXPORT: no tohost store ({type(exc).__name__})") from None
    await b.wait_cycles_until(int(h.b.cycle_count.value) + SETTLE_CYCLES)
    # checks first, then the finish handshake (TB_CONTRACT Section 2)
    seq = await b.export_flush()
    retired_now = int(h.b.evt_retired_count.value)
    counters = plus("export_counters", "0") == "1"
    assert seq == seq_early + 1, f"GEN_UT_EXPORT: flush sequence {seq} does not follow {seq_early}"
    data = gen_export.read(export_path, seq, counters=counters)
    early = gen_export.read(export_path, seq_early, counters=counters)
    log.info("GEN_UT_EXPORT flush seq %d: records %d retired %d markers %d events %d (bridge retired now %d; early flush seq %d had %d records)",
             seq, data.flush.records, data.flush.retired, data.flush.markers, data.flush.events, retired_now, seq_early, early.flush.records)
    assert retired_now >= data.flush.retired, f"GEN_UT_EXPORT: bridge retired {retired_now} < marker retired {data.flush.retired}"
    assert [r.order for r in early.records] == [r.order for r in data.records[:len(early.records)]], "GEN_UT_EXPORT: the early flush is not a prefix of the final one"
    check_records(data.records, data.markers, img, int(h.b.evt_eot_count.value), log)
    assert int(h.b.evt_eot_code.value) == 1, "GEN_UT_EXPORT: program did not report pass"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
