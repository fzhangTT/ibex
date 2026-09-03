"""Lock-step ISA compare test (build step 2a): the boot flow of gen_ut_boot plus the requirement that the
scoreboard compared (almost) every retired record against the Spike model with zero mismatches. Written
before the RVFI monitor and the scoreboard existed (TDD): on the step-1c top the compared count stays 0.
Forced red of the compare path: run with +gen_isa_string=rv32imc_zicsr_zifencei (no Zc/Zb in the model) and
expect ISA mismatches. Plusargs as gen_ut_boot plus +gen_ut_lockstep_min_ratio_pct.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_lockstep, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_LOCKSTEP_PASS"


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
    min_ratio = int(plus("ut_lockstep_min_ratio_pct", PLUSARGS["ut_lockstep_min_ratio_pct"]["default"]))
    await b.start()
    n_rb = int(plus("mem_readback_words", CONSTANTS["GEN_MEM_READBACK_WORDS_DEFAULT"]))
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
    retired = int(h.b.evt_retired_count.value)
    compared = int(h.b.evt_isa_records.value)
    mism = int(h.b.evt_isa_mismatch.value)
    log.info("GEN_UT_LOCKSTEP retired %d compared %d mismatches %d tohost 0x%08x", retired, compared, mism,
             int(h.b.evt_eot_code.value))
    assert retired > 0, "GEN_UT_LOCKSTEP: nothing retired"
    assert compared * 100 >= retired * min_ratio, f"GEN_UT_LOCKSTEP: compared {compared} of {retired} retired records (< {min_ratio}%)"
    assert mism == 0, f"GEN_UT_LOCKSTEP: {mism} ISA mismatches"
    assert int(h.b.evt_eot_code.value) == 1, "GEN_UT_LOCKSTEP: program did not report pass"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
