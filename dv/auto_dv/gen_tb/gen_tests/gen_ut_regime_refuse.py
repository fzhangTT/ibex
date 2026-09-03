"""REGIME_SET refusal: after boot, send REGIME_SET for a knob whose yaml regime_set_consumer is none and finish. The
run must FAIL through the dispatcher's collected GEN_CMD_DISPATCH uvm_error (there is no run-time consumer to apply it);
the marker below is printed so that a run passing on the marker alone would expose a missing refusal.
Plusargs as gen_ut_boot. MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_regime_refuse, TOPLEVEL=gen_tb_top."""
import cocotb

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_knobs import KNOB_CONSUMER, KNOB_IDS, PLUSARGS

PASS_MARKER = "GEN_UT_REGIME_REFUSE_PASS"


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_regime_refuse(dut):
    log = dut._log
    b = GenBridge(GenHandles(dut), log)
    unconsumed = sorted(k for k, c in KNOB_CONSUMER.items() if c == "none")
    assert unconsumed, "GEN_UT_REGIME_REFUSE: no knob with regime_set_consumer none in gen_tb_knobs.yaml"
    knob = unconsumed[0]
    await b.start()
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"])), timeout_cycles=60000)
    log.info("GEN_UT_REGIME_REFUSE: REGIME_SET %s (id %d) has no run-time consumer; the dispatcher must refuse it", knob, KNOB_IDS[knob])
    await b.cmd("REGIME_SET", (KNOB_IDS[knob], 0, 0, 0))
    await b.finish()
    log.info(PASS_MARKER)
