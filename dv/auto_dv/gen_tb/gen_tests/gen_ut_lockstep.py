"""Lock-step ISA compare test (build step 2a): the boot flow of gen_ut_boot plus the requirement that the
scoreboard consumed EVERY retired record (compared, or folded into its Zcmp sequence) with zero mismatches.
Forced red of the compare path: run with +gen_isa_string=rv32imc_zicsr_zifencei (no Zc/Zb in the model) and
expect ISA mismatches. Plusargs as gen_ut_boot. TDD transcript: dv/auto_dv/evidence/gen_tdd_lockstep.md.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_lockstep, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_LOCKSTEP_PASS"
QUIESCE_CYCLES = 20   # bound on the wait for the retired and consumed counters to hold equal across a cycle


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_lockstep(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    retire_target = int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"]))
    assert plus("fetch_en_at_reset") == "0", "GEN_UT_LOCKSTEP: run with +gen_fetch_en_at_reset=0 (the read-back precedes execution)"
    await b.start()
    n_rb = int(plus("mem_readback_words", PLUSARGS["mem_readback_words"]["default"]))
    bad = 0
    for idx, word in img.sample(n_rb, seed):
        if await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) != word:
            bad += 1
    assert bad == 0, f"GEN_UT_LOCKSTEP: {bad} read-back mismatches"
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(retire_target, timeout_cycles=retire_target * 40 + 2000)
    if img.tohost is not None and int(h.b.evt_eot_count.value) == 0:
        try:
            await with_timeout(Edge(h.b.evt_eot_seen), 20000 * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
        except Exception as exc:
            raise AssertionError(f"GEN_UT_LOCKSTEP: no tohost store ({type(exc).__name__})") from None
    # Two writers, one pair: the comparator writes evt_isa_records mid-record, the interface increments
    # evt_retired_count on the edge, so equality at a single instant can be a skipped record cancelling one in
    # flight; require it across a whole cycle. The bound waits, it never decides: an unconsumed record never converges.
    settled = 0
    for _ in range(QUIESCE_CYCLES):
        if int(h.b.evt_retired_count.value) == int(h.b.evt_isa_records.value):
            settled += 1
            if settled == 2:
                break
        else:
            settled = 0
        await b.wait_cycles_until(int(h.b.cycle_count.value) + 1)
    retired = int(h.b.evt_retired_count.value)
    consumed = int(h.b.evt_isa_records.value)
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_LOCKSTEP retired %d consumed %d mismatches %d tohost 0x%08x", retired, consumed, mism,
             int(h.b.evt_eot_code.value))
    assert retired > 0, "GEN_UT_LOCKSTEP: nothing retired"
    assert consumed == retired, f"GEN_UT_LOCKSTEP: comparator consumed {consumed} records, {retired} retired (must be equal)"
    assert mism == 0, f"GEN_UT_LOCKSTEP: {mism} ISA mismatches"
    assert int(h.b.evt_eot_code.value) == 1, "GEN_UT_LOCKSTEP: program did not report pass"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
