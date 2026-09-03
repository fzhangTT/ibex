"""COV_WITNESS refusal (CG-WIT-001 rule C-2): one item witnessed with ANOTHER test's group index. The run must FAIL through
the collected GEN_WITNESS_FOREIGN uvm_error; the marker below is printed so that a run passing on the marker alone would
expose a missing refusal. Plusargs as gen_ut_boot. MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_witness_foreign, TOPLEVEL=gen_tb_top."""
import cocotb
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_knobs import PLUSARGS, WITNESS_GROUP_OF, WITNESS_GROUPS
PASS_MARKER = "GEN_UT_WITNESS_FOREIGN_PASS"


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_witness_foreign(dut):
    log = dut._log
    b = GenBridge(GenHandles(dut), log)
    tp, own = sorted(WITNESS_GROUP_OF.items())[0]
    other = next(g for g in WITNESS_GROUPS if g != own)
    await b.start()
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"])), timeout_cycles=60000)
    log.info("GEN_UT_WITNESS_FOREIGN: %s belongs to %s; issuing it as %s, the dispatcher must refuse it", tp, own, other)
    await b.cov_witness(tp, other)
    await b.finish()
    log.info(PASS_MARKER)
