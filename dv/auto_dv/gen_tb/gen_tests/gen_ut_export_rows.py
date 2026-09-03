"""Export rows with no retained observation before (regime phase, pin debug_req, pin irq_nm): boot the program, issue two
REGIME_SET commands on a consumed bus knob and, per +gen_ut_rows_set, one DBG_REQ assert-and-release (regime_dbg, needs
a debug ROM) or one NMI_PULSE (regime_nmi, needs a vector-31 handler), flush the export and require: one E regime phase
line per REGIME_SET with the knob id, value index and phase index issued, in order; a pin debug_req (or irq_nm) line pair
carrying 1 then 0 with non-decreasing stamps; zero ISA mismatches. The first lines are logged for the hand check.
Plusargs as gen_ut_export plus +gen_ut_rows_set. MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_export_rows, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb import gen_export
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, KNOB_IDS, PLUSARGS

PASS_MARKER = "GEN_UT_EXPORT_ROWS_PASS"
KNOB = "knob_imem_gnt_delay"                       # a bus knob with a run-time consumer: REGIME_SET is applied, never refused
PHASES = ("short", "long")                         # value names issued in this order
HOLD_CYCLES_POLICY = 0                             # DBG_REQ arg1: the request drops after arg2 cycles
DBG_HOLD_CYCLES = 60
NMI_PULSE_CYCLES = 4
SETTLE_CYCLES = 200


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


async def edge_within(sig, cycles, what):
    try:
        await with_timeout(Edge(sig), cycles * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
    except Exception:
        raise AssertionError(f"GEN_UT_EXPORT_ROWS: no {what} within {cycles} cycles") from None


def check_pair(lines, name, log):
    """A pin row driven high then low: at least two lines, 1 then 0, stamps non-decreasing."""
    assert len(lines) >= 2, f"GEN_UT_EXPORT_ROWS: {len(lines)} E pin {name} lines, expected the assert and the release"
    assert lines[0].fields == (1,) and lines[1].fields == (0,), f"GEN_UT_EXPORT_ROWS: pin {name} values {[l.fields for l in lines[:2]]}, expected (1,) then (0,)"
    assert lines[0].cycle <= lines[1].cycle, f"GEN_UT_EXPORT_ROWS: pin {name} release stamped before the assert"
    for l in lines[:2]:
        log.info("GEN_UT_EXPORT_ROWS first lines: E %x pin %s %s", l.cycle, name, " ".join(f"{f:x}" for f in l.fields))


@cocotb.test()
async def gen_ut_export_rows(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    rows_set = plus("ut_rows_set", PLUSARGS["ut_rows_set"]["default"])
    export_path = plus("export_file")
    assert export_path, "GEN_UT_EXPORT_ROWS: +gen_export_file is required"
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_EXPORT_ROWS: read-back mismatch"
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(200, timeout_cycles=20000)
    issued = []
    for i, value in enumerate(PHASES):
        idx = PLUSARGS[KNOB]["values"].index(value)
        await b.cmd("REGIME_SET", (KNOB_IDS[KNOB], idx, 0, 0))
        issued.append((KNOB_IDS[KNOB], idx, i + 1))
        if i == 0:
            if rows_set == "regime_dbg":
                await b.cmd("DBG_REQ", (1, HOLD_CYCLES_POLICY, DBG_HOLD_CYCLES, 0))
                await edge_within(h.b.evt_dbg_entered, 4000, "debug entry")
            else:
                await b.cmd("NMI_PULSE", (NMI_PULSE_CYCLES, 0, 0, 0))
                await edge_within(h.b.evt_irq_taken, 4000, "NMI entry")
            base = int(h.b.evt_retired_count.value)
            await b.wait_retired_until(base + 100, timeout_cycles=20000)
    await b.wait_cycles_until(int(h.b.cycle_count.value) + SETTLE_CYCLES)
    seq = await b.export_flush()
    data = gen_export.read(export_path, seq, counters=plus("export_counters", "0") == "1", sources=plus("export_sources", PLUSARGS["export_sources"]["default"]))
    phases = [e for e in data.events if e.source == "regime" and e.event == "phase"]
    assert [p.fields for p in phases] == issued, f"GEN_UT_EXPORT_ROWS: regime phase lines {[p.fields for p in phases]}, issued {issued}"
    for p in phases:
        log.info("GEN_UT_EXPORT_ROWS first lines: E %x regime phase %s", p.cycle, " ".join(f"{f:x}" for f in p.fields))
    if rows_set == "regime_dbg":
        check_pair([e for e in data.events if e.source == "pin" and e.event == "debug_req"], "debug_req", log)
    else:
        check_pair([e for e in data.events if e.source == "pin" and e.event == "irq_nm"], "irq_nm", log)
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_EXPORT_ROWS set=%s phases=%d records=%d events=%d mismatches=%d", rows_set, len(phases), data.flush.records, data.flush.events, mism)
    assert mism == 0, f"GEN_UT_EXPORT_ROWS: {mism} ISA mismatches"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
