"""Counter-model unit test: run a program that reads a performance counter at both ends of a window, then read
back the program's OWN measured differences from memory and require them to be what the RTL is known to
produce. That is this module's fire-check: it proves the program met the counter behaviour under test, so a
green counter checker in the same run means the checker judged that behaviour rather than nothing at all. The
counter rules themselves (ctr_hpm_exact, ctr_hpm_bound) fail through their own uvm_error, which the flow
collects; this module does not repeat their judgement.
+gen_ut_ctr_delta_sym names the program symbol holding the differences and +gen_ut_ctr_delta_expect the words
expected there, comma separated, each a value or lo:hi where the RTL's own count depends on the bus latency.
+gen_ut_ctr_nmi_after pulses one NMI after that many retirements, which lands an NMI entry inside an open
counter read window: the counter rules leave such a window unjudged, and that run is how the rule's
unjudged-entry row is exercised rather than asserted. An NMI needs no interrupt enable, and the programs'
vector tables answer it with an mret, so no program change is needed. Plusargs as gen_ut_lockstep plus those.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_counters, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_COUNTERS_PASS"
QUIESCE_CYCLES = 20   # bound on the wait for the retired and consumed counters to hold equal across a cycle
NMI_PULSE_CYCLES = 4  # hold on the non-maskable line, as gen_ut_export_rows drives it


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


def parse_expect(spec):
    """One (lo, hi) bound per word; a bare value is the closed range [v, v]."""
    out = []
    for field in spec.split(","):
        field = field.strip()
        if ":" in field:
            lo, hi = field.split(":", 1)
            out.append((int(lo, 0), int(hi, 0)))
        else:
            v = int(field, 0)
            out.append((v, v))
    return out


@cocotb.test()
async def gen_ut_counters(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    retire_target = int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"]))
    sym = plus("ut_ctr_delta_sym")
    spec = plus("ut_ctr_delta_expect")
    nmi_after = int(plus("ut_ctr_nmi_after", PLUSARGS["ut_ctr_nmi_after"]["default"]))
    assert sym, "GEN_UT_COUNTERS: +gen_ut_ctr_delta_sym is required (the fire-check reads the program's own differences)"
    assert spec, "GEN_UT_COUNTERS: +gen_ut_ctr_delta_expect is required"
    assert plus("fetch_en_at_reset") == "0", "GEN_UT_COUNTERS: run with +gen_fetch_en_at_reset=0 (the read-back precedes execution)"
    expect = parse_expect(spec)
    assert sym in img.sidecar["symbols"], f"GEN_UT_COUNTERS: the image has no symbol {sym}"
    delta_addr = int(img.sidecar["symbols"][sym], 16)
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_COUNTERS: read-back mismatch"
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    if nmi_after:
        # the pulse must land while a counter window is open, so it is timed off the retirement count the
        # caller picked from the program's own window layout rather than off a cycle
        await b.wait_retired_until(nmi_after, timeout_cycles=nmi_after * 40 + 2000)
        await b.cmd("NMI_PULSE", (NMI_PULSE_CYCLES, 0, 0, 0))
        log.info("GEN_UT_COUNTERS pulsed one NMI after %d retirements", nmi_after)
    await b.wait_retired_until(retire_target, timeout_cycles=retire_target * 40 + 2000)
    if img.tohost is not None and int(h.b.evt_eot_count.value) == 0:
        try:
            await with_timeout(Edge(h.b.evt_eot_seen), 20000 * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
        except Exception as exc:
            raise AssertionError(f"GEN_UT_COUNTERS: no tohost store ({type(exc).__name__})") from None
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
    got = [await b.cmd("MEM_PEEK", (delta_addr + 4 * i, 0, 0, 0)) for i in range(len(expect))]
    log.info("GEN_UT_COUNTERS %s at 0x%08x: %s (expected %s)", sym, delta_addr,
             [f"{w}" for w in got], [f"{lo}..{hi}" for lo, hi in expect])
    bad = [(i, got[i], expect[i]) for i in range(len(expect)) if not expect[i][0] <= got[i] <= expect[i][1]]
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_COUNTERS retired %d consumed %d mismatches %d tohost 0x%08x", retired, consumed, mism,
             int(h.b.evt_eot_code.value))
    assert not bad, "GEN_UT_COUNTERS: " + "; ".join(
        f"word {i} of {sym} is {v}, outside {e[0]}..{e[1]}" for i, v, e in bad)
    assert settled == 2, f"GEN_UT_COUNTERS: comparator consumed {consumed} records, {retired} retired (must be equal and hold across a cycle; {QUIESCE_CYCLES} cycles waited)"
    assert mism == 0, f"GEN_UT_COUNTERS: {mism} ISA mismatches"
    # The end-of-test CODE is the program's own verdict against the documentation, so a bug reproducer stores
    # a failing one by design and the entry that owns the program judges it. This module requires only that
    # the program reached its store, so a run that died in its trap vector cannot pass here.
    assert int(h.b.evt_eot_count.value) > 0, "GEN_UT_COUNTERS: the program never reached its end-of-test store"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
