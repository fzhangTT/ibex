"""COV_WITNESS (CG-WIT-001): after boot, two items of one test group are witnessed with their own group, the first one twice;
the peek word must count the distinct bins the covergroup itself holds: 1, 1, 2. Plusargs as gen_ut_boot.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_witness, TOPLEVEL=gen_tb_top."""
import cocotb
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_knobs import PLUSARGS, WITNESS_GROUP_OF
PASS_MARKER = "GEN_UT_WITNESS_PASS"


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


def first_group_with_two_items():
    by_group = {}
    for tp, g in WITNESS_GROUP_OF.items():
        by_group.setdefault(g, []).append(tp)
    return next((g, sorted(v)) for g, v in sorted(by_group.items()) if len(v) >= 2)


@cocotb.test()
async def gen_ut_witness(dut):
    log = dut._log
    b = GenBridge(GenHandles(dut), log)
    group, items = first_group_with_two_items()
    await b.start()
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"])), timeout_cycles=60000)
    n = await b.cov_witness(items[0], group)
    assert n == 1, f"GEN_UT_WITNESS: the first witness ({items[0]}) counts {n} distinct bins, expected 1"
    n = await b.cov_witness(items[0], group)
    assert n == 1, f"GEN_UT_WITNESS: the repeated witness counts {n} distinct bins, expected 1 (one bin, hit twice)"
    n = await b.cov_witness(items[1], group)
    assert n == 2, f"GEN_UT_WITNESS: the second item ({items[1]}) counts {n} distinct bins, expected 2"
    log.info("GEN_UT_WITNESS: %s witnessed %s twice and %s once: 2 distinct bins as the covergroup counts them", group, items[0], items[1])
    await b.finish()
    log.info(PASS_MARKER)
