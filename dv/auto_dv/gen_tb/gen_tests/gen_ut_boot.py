"""'Boots and retires' test (build step 1c milestone): a program image from gen_program.py runs on
gen_tb_top through the bus agents and RAM models with no checking beyond the TB's own mechanics:
image digest, MEM_PEEK read-back of seeded words against the .vmem parsed here (C3.3 backdoor rule),
a retirement threshold, and the end-of-test store to tohost (evt_eot_seen edge, code 1 = pass).
Plusargs (from GenImage.plusargs): +gen_mem_image, +gen_mem_image_crc32, +gen_mem_image_words,
+gen_boot_addr, +gen_tohost_addr, +gen_fetch_en_at_reset=0 (the core is released by FETCH_EN after the
read-back); optional +gen_ut_boot_retire=<n> (yaml default 200).
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_boot, TOPLEVEL=gen_tb_top."""
import os

import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_BOOT_PASS"


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_boot(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    image_path = plus("mem_image")
    assert image_path, "GEN_UT_BOOT: +gen_mem_image is required"
    img = GenImage(image_path)
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    retire_target = int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"]))
    await b.start()
    # 1. read-back of seeded words through MEM_PEEK (Python compares against its own parse of the .vmem)
    n_rb = int(plus("mem_readback_words", CONSTANTS["GEN_MEM_READBACK_WORDS_DEFAULT"]))
    mismatches = 0
    for idx, word in img.sample(n_rb, seed):
        got = await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0))
        if got != word:
            mismatches += 1
            log.error("GEN_UT_BOOT read-back mismatch at word 0x%08x: sv 0x%08x vmem 0x%08x", idx * 4, got, word)
    assert mismatches == 0, f"GEN_UT_BOOT: {mismatches} read-back mismatches of {n_rb} words"
    log.info("GEN_UT_BOOT read-back ok: %d words", n_rb)
    # 1b. release the core: the test runs with +gen_fetch_en_at_reset=0 so the read-back above saw the
    #     image, not the program's own stores (C3.3 backdoor rule)
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    # 2. the core boots and retires
    await b.wait_retired_until(retire_target, timeout_cycles=retire_target * 40 + 2000)
    retired = int(h.b.evt_retired_count.value)
    log.info("GEN_UT_BOOT retired %d (target %d) at cycle %d", retired, retire_target, int(h.b.cycle_count.value))
    # 3. end of test: the program's tohost store (already seen, or awaited)
    if img.tohost is not None:
        if not (h.b.evt_eot_seen.value.is_resolvable and int(h.b.evt_eot_count.value) > 0):
            try:
                await with_timeout(Edge(h.b.evt_eot_seen), 20000 * CONSTANTS["GEN_CLK_PERIOD_NS"], "ns")
            except Exception as exc:
                raise AssertionError(f"GEN_UT_BOOT: no tohost store within 20000 cycles ({type(exc).__name__})") from None
        code = int(h.b.evt_eot_code.value)
        log.info("GEN_UT_BOOT tohost code 0x%08x", code)
        assert code == 1, f"GEN_UT_BOOT: program reported failure code 0x{code:08x} (1 = pass)"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
