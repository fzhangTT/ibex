"""'Boots and retires' with fetch enabled at the reset release: the core starts on its own, so there is no read-back before execution
(the C3.3 backdoor rule is gen_ut_boot's, run with +gen_fetch_en_at_reset=0); this test is the fetch_enable-On boot of gen_rst_boot_cg
(boot_to_req two) and requires only the retirement threshold and the program's tohost store. Plusargs as gen_ut_boot with
+gen_fetch_en_at_reset=1 (one value: the TB's $value$plusargs takes the first match, cocotb the last, so a run must never carry both).
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_boot_fe1, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_BOOT_FE1_PASS"


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_boot_fe1(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    image_path = plus("mem_image")
    assert image_path, "GEN_UT_BOOT_FE1: +gen_mem_image is required"
    img = GenImage(image_path)
    retire_target = int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"]))
    assert plus("fetch_en_at_reset") == "1", "GEN_UT_BOOT_FE1: run with +gen_fetch_en_at_reset=1 (the core is released at reset; gen_ut_boot is the held form)"
    await b.start()
    await b.wait_retired_until(retire_target, timeout_cycles=retire_target * 40 + 2000)
    retired = int(h.b.evt_retired_count.value)
    log.info("GEN_UT_BOOT_FE1 retired %d (target %d) at cycle %d", retired, retire_target, int(h.b.cycle_count.value))
    if img.tohost is not None:
        if not (h.b.evt_eot_seen.value.is_resolvable and int(h.b.evt_eot_count.value) > 0):
            try:
                await with_timeout(Edge(h.b.evt_eot_seen), 20000 * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
            except Exception as exc:
                raise AssertionError(f"GEN_UT_BOOT_FE1: no tohost store within 20000 cycles ({type(exc).__name__})") from None
        code = int(h.b.evt_eot_code.value)
        log.info("GEN_UT_BOOT_FE1 tohost code 0x%08x", code)
        assert code == 1, f"GEN_UT_BOOT_FE1: program reported failure code 0x{code:08x} (1 = pass)"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
